# ■■■ TimescaleDB 가이드 ■■■

## ■■■ 1. TimescaleDB 핵심 개념 ■■■

### 하이퍼테이블 (Hypertable)

```
일반 PostgreSQL 테이블:
┌─────────────────────────────────────────┐
│           하나의 큰 테이블                │
│  (모든 데이터가 하나의 파일에 저장)        │
└─────────────────────────────────────────┘

TimescaleDB 하이퍼테이블:
┌─────────────────────────────────────────┐
│           하이퍼테이블 (가상)             │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐       │
│  │청크1│ │청크2│ │청크3│ │청크4│  ...   │
│  │3/1- │ │3/2- │ │3/3- │ │3/4- │       │
│  │3/1  │ │3/2  │ │3/3  │ │3/4  │       │
│  └─────┘ └─────┘ └─────┘ └─────┘       │
└─────────────────────────────────────────┘
```

- **하이퍼테이블**: 사용자에게 보이는 가상 테이블 (일반 테이블처럼 사용)
- **청크 (Chunk)**: 실제 데이터가 저장되는 물리적 파티션 (시간 간격별)
- **자동 파티셔닝**: 데이터 삽입 시 자동으로 적절한 청크에 배치
- **투명한 접근**: SELECT/INSERT/UPDATE/DELETE 모두 일반 테이블과 동일

### 청크 (Chunk)

```
chunk_time_interval = '1 day' 설정 시:

시간 →
├──── 3월 18일 ────┤──── 3월 19일 ────┤──── 3월 20일 ────┤
│    chunk_001     │    chunk_002     │    chunk_003     │
│   50,000 rows    │   48,000 rows    │   52,000 rows    │
│    (압축됨)       │    (압축됨)       │   (미압축)        │
└──────────────────┴──────────────────┴──────────────────┘

장점:
- 특정 시간 범위 쿼리 시 해당 청크만 스캔 (chunk exclusion)
- 오래된 청크 삭제가 매우 빠름 (DROP vs DELETE)
- 청크별 압축 적용 가능
- 청크별 인덱스 자동 생성
```

## ■■■ 2. IoT/모니터링 사용 사례 ■■■

### IoT 센서 모니터링

```
센서 네트워크:
  [온도 센서] → ┐
  [습도 센서] → ├→ [데이터 수집기] → [TimescaleDB] → [Grafana 대시보드]
  [기압 센서] → ┘

데이터 흐름:
  1. 센서가 10초마다 데이터 전송
  2. 수집기가 배치로 INSERT (batch insert)
  3. TimescaleDB가 자동으로 청크에 분배
  4. 연속 집계가 1시간/1일 단위로 자동 집계
  5. Grafana가 연속 집계를 조회하여 대시보드 표시
```

### 서버 모니터링

```sql
-- 실시간 서버 상태 대시보드
-- P95 응답 시간이 1초를 넘는 서비스 알림
SELECT
    time_bucket('5 minutes', time) AS interval,
    host,
    service,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time) AS p95_ms,
    SUM(error_count) AS errors
FROM server_metrics
WHERE time > NOW() - INTERVAL '1 hour'
GROUP BY interval, host, service
HAVING PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time) > 1000
ORDER BY interval DESC;
```

### 금융 데이터

```sql
-- OHLCV 캔들스틱 차트 데이터
SELECT
    time_bucket('1 day', time) AS day,
    symbol,
    first(price, time) AS open,
    MAX(price) AS high,
    MIN(price) AS low,
    last(price, time) AS close,
    SUM(volume) AS volume
FROM stock_prices
GROUP BY day, symbol
ORDER BY day DESC;
```

## ■■■ 3. 성능 최적화 ■■■

### 청크 크기 설정 가이드

| 데이터 삽입 빈도 | 권장 chunk_time_interval | 이유 |
|-----------------|------------------------|------|
| 초당 1,000+ 행 | 1시간 ~ 6시간 | 작은 청크로 빠른 압축/삭제 |
| 초당 100~1,000 행 | 6시간 ~ 1일 | 균형 |
| 초당 100 미만 | 1일 ~ 7일 | 큰 청크로 오버헤드 최소화 |

```sql
-- 청크 크기 변경
SELECT set_chunk_time_interval('sensor_data', INTERVAL '6 hours');
```

### 인덱스 전략

```sql
-- 1. 시간 + 디바이스 복합 인덱스 (가장 일반적)
CREATE INDEX ON sensor_data (sensor_id, time DESC);

-- 2. 시간만 (시간 범위 쿼리 최적화, 기본 자동 생성)
-- CREATE INDEX ON sensor_data (time DESC);

-- 3. BRIN 인덱스 (시계열에 적합, 매우 작은 크기)
-- 시간 순서대로 삽입되는 데이터에 효과적
```

### 배치 삽입

```sql
-- 단일 INSERT보다 배치 INSERT가 10~100배 빠름
-- 1,000~10,000건 단위로 배치 삽입 권장

-- COPY 명령 (가장 빠름)
-- COPY sensor_data FROM '/data/sensors.csv' WITH (FORMAT csv, HEADER true);

-- 다중 값 INSERT
INSERT INTO sensor_data (time, sensor_id, location, temperature, humidity, pressure)
VALUES
    (NOW(), 1, '서울', 25.3, 60.1, 1013.2),
    (NOW(), 2, '부산', 27.1, 55.3, 1012.8),
    (NOW(), 3, '대전', 24.8, 62.5, 1013.5);
```

## ■■■ 4. Grafana 대시보드 설정 ■■■

```
1. Grafana 접속: http://localhost:3000
   - 계정: admin / admin123

2. 데이터 소스 추가:
   - Configuration → Data Sources → Add → PostgreSQL
   - Host: timescaledb:5432 (Docker 네트워크)
   - Database: timescale_db
   - User: postgres / postgres123
   - TLS/SSL Mode: disable
   - TimescaleDB: Enable 체크!

3. 대시보드 생성:
   - + → Dashboard → Add panel
   - 쿼리 예시 (Time series):
     SELECT
       $__timeGroupAlias(time, '1h'),
       sensor_id::text AS metric,
       AVG(temperature) AS temperature
     FROM sensor_data
     WHERE $__timeFilter(time)
     GROUP BY 1, 2
     ORDER BY 1
```

## ■■■ 5. 운영 명령어 ■■■

```bash
# 환경 시작
docker-compose up -d

# TimescaleDB 접속
docker exec -it timescaledb-study psql -U postgres -d timescale_db

# 하이퍼테이블 크기 확인
docker exec -it timescaledb-study psql -U postgres -d timescale_db -c "
    SELECT hypertable_name,
           pg_size_pretty(hypertable_size(format('%I.%I', hypertable_schema, hypertable_name)::regclass))
    FROM timescaledb_information.hypertables;
"

# 청크 목록 확인
docker exec -it timescaledb-study psql -U postgres -d timescale_db -c "
    SELECT hypertable_name, chunk_name, range_start, range_end, is_compressed
    FROM timescaledb_information.chunks
    ORDER BY range_start DESC LIMIT 20;
"

# 수동 압축 실행
docker exec -it timescaledb-study psql -U postgres -d timescale_db -c "
    SELECT compress_chunk(c.chunk_name::regclass)
    FROM timescaledb_information.chunks c
    WHERE c.hypertable_name = 'sensor_data'
      AND NOT c.is_compressed
      AND c.range_end < NOW() - INTERVAL '7 days';
"

# 연속 집계 리프레시
docker exec -it timescaledb-study psql -U postgres -d timescale_db -c "
    CALL refresh_continuous_aggregate('sensor_hourly', NULL, NOW());
"
```

## ■■■ 6. TimescaleDB vs 일반 PostgreSQL ■■■

| 기능 | PostgreSQL | TimescaleDB |
|------|-----------|-------------|
| 시간 파티셔닝 | 수동 (PARTITION BY RANGE) | 자동 (create_hypertable) |
| 오래된 데이터 삭제 | DELETE (느림) | drop_chunks (매우 빠름) |
| 데이터 압축 | 없음 | 네이티브 (90%+ 절감) |
| 시간 집계 | date_trunc (제한적) | time_bucket (유연) |
| 연속 집계 | MATERIALIZED VIEW (수동 리프레시) | 연속 집계 (자동 증분 업데이트) |
| 보존 정책 | 수동 (cron + DELETE) | 자동 (add_retention_policy) |
| first/last 함수 | 없음 | 내장 |
