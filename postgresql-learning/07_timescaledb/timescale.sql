-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ TimescaleDB 학습 SQL                            ■■■
-- ■■■ 하이퍼테이블, time_bucket, 연속 집계, 압축      ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ TimescaleDB 확장 설치 ■■■
-- TimescaleDB는 PostgreSQL 확장(extension)으로 설치
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 설치 확인
SELECT extname, extversion FROM pg_extension WHERE extname = 'timescaledb';

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 1. 하이퍼테이블 (Hypertable) 생성               ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- 하이퍼테이블: 시간 기반으로 자동 파티셔닝되는 테이블
-- 일반 테이블처럼 사용하지만, 내부적으로 "청크(chunk)"로 분할
-- 각 청크는 특정 시간 범위의 데이터를 저장

-- ■■■ IoT 센서 데이터 테이블 ■■■
-- 먼저 일반 테이블로 생성
CREATE TABLE IF NOT EXISTS sensor_data (
    time        TIMESTAMPTZ NOT NULL,    -- 측정 시각 (타임존 포함, 필수!)
    sensor_id   INTEGER NOT NULL,        -- 센서 ID
    location    VARCHAR(50),             -- 센서 위치
    temperature DOUBLE PRECISION,        -- 온도 (℃)
    humidity    DOUBLE PRECISION,        -- 습도 (%)
    pressure    DOUBLE PRECISION,        -- 기압 (hPa)
    battery     DOUBLE PRECISION         -- 배터리 잔량 (%)
);

-- ■■■ 일반 테이블 → 하이퍼테이블 변환 ■■■
-- create_hypertable(): TimescaleDB의 핵심 함수
--   첫 번째 인자: 테이블 이름
--   두 번째 인자: 시간 컬럼 이름
--   chunk_time_interval: 청크 시간 간격 (기본: 7일)
--     → 1일 간격 = 하루치 데이터가 하나의 청크에 저장
SELECT create_hypertable(
    'sensor_data',                     -- 테이블 이름
    'time',                            -- 시간 컬럼
    chunk_time_interval => INTERVAL '1 day',  -- 1일 단위 청크
    if_not_exists => TRUE              -- 이미 있으면 무시
);

-- ■■■ 서버 메트릭 테이블 (모니터링용) ■■■
CREATE TABLE IF NOT EXISTS server_metrics (
    time          TIMESTAMPTZ NOT NULL,
    host          VARCHAR(100) NOT NULL,   -- 서버 호스트명
    service       VARCHAR(100),            -- 서비스 이름
    cpu_usage     DOUBLE PRECISION,        -- CPU 사용률 (%)
    memory_usage  DOUBLE PRECISION,        -- 메모리 사용률 (%)
    disk_usage    DOUBLE PRECISION,        -- 디스크 사용률 (%)
    network_in    BIGINT,                  -- 네트워크 수신 (bytes)
    network_out   BIGINT,                  -- 네트워크 송신 (bytes)
    request_count INTEGER,                 -- 요청 수
    error_count   INTEGER,                 -- 에러 수
    response_time DOUBLE PRECISION         -- 응답 시간 (ms)
);

SELECT create_hypertable(
    'server_metrics', 'time',
    chunk_time_interval => INTERVAL '6 hours',  -- 6시간 단위 청크
    if_not_exists => TRUE
);

-- ■■■ 주식 시세 테이블 (금융 데이터) ■■■
CREATE TABLE IF NOT EXISTS stock_prices (
    time      TIMESTAMPTZ NOT NULL,
    symbol    VARCHAR(10) NOT NULL,      -- 종목 코드 (예: AAPL, TSLA)
    price     NUMERIC(12, 4) NOT NULL,   -- 현재가
    volume    BIGINT,                    -- 거래량
    open_p    NUMERIC(12, 4),            -- 시가
    high_p    NUMERIC(12, 4),            -- 고가
    low_p     NUMERIC(12, 4),            -- 저가
    close_p   NUMERIC(12, 4)             -- 종가
);

SELECT create_hypertable(
    'stock_prices', 'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 2. 시계열 데이터 삽입                           ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ 센서 데이터 대량 생성 (30일간, 10초 간격, 5개 센서) ■■■
INSERT INTO sensor_data (time, sensor_id, location, temperature, humidity, pressure, battery)
SELECT
    -- generate_series: 시작~끝까지 지정 간격으로 시간 생성
    ts AS time,
    sensor_id,
    -- 센서별 위치
    CASE sensor_id
        WHEN 1 THEN '서울-강남'
        WHEN 2 THEN '서울-종로'
        WHEN 3 THEN '부산-해운대'
        WHEN 4 THEN '대전-유성'
        WHEN 5 THEN '제주-서귀포'
    END AS location,
    -- 온도: 기본 20도 + 센서 편차 + 일별 변동 + 랜덤 노이즈
    20 + (sensor_id * 2) +
        5 * sin(EXTRACT(HOUR FROM ts) * PI() / 12) +  -- 낮에 높고 밤에 낮음
        (random() * 3 - 1.5) AS temperature,
    -- 습도: 50-80% 범위
    50 + 15 * cos(EXTRACT(HOUR FROM ts) * PI() / 12) +
        (random() * 10) AS humidity,
    -- 기압: 1013 hPa 기준
    1013 + (random() * 10 - 5) AS pressure,
    -- 배터리: 시간이 지나면서 감소
    100 - (EXTRACT(EPOCH FROM (ts - NOW() + INTERVAL '30 days')) / 86400) * 0.5 +
        (random() * 2) AS battery
FROM
    generate_series(
        NOW() - INTERVAL '30 days',     -- 30일 전부터
        NOW(),                            -- 현재까지
        INTERVAL '1 minute'               -- 1분 간격
    ) AS ts
CROSS JOIN
    generate_series(1, 5) AS sensor_id;  -- 5개 센서

-- ■■■ 서버 메트릭 데이터 생성 (7일간) ■■■
INSERT INTO server_metrics (time, host, service, cpu_usage, memory_usage, disk_usage,
                            network_in, network_out, request_count, error_count, response_time)
SELECT
    ts,
    host,
    CASE (ROW_NUMBER() OVER ()) % 3
        WHEN 0 THEN 'api-gateway'
        WHEN 1 THEN 'user-service'
        WHEN 2 THEN 'order-service'
    END AS service,
    -- CPU: 피크 시간대(10-18시)에 높음
    CASE
        WHEN EXTRACT(HOUR FROM ts) BETWEEN 10 AND 18
        THEN 40 + random() * 50         -- 40-90%
        ELSE 10 + random() * 30         -- 10-40%
    END AS cpu_usage,
    50 + random() * 30 AS memory_usage,
    60 + random() * 20 AS disk_usage,
    (random() * 1000000)::BIGINT AS network_in,
    (random() * 500000)::BIGINT AS network_out,
    (random() * 1000)::INTEGER AS request_count,
    (random() * 10)::INTEGER AS error_count,
    50 + random() * 200 AS response_time
FROM
    generate_series(
        NOW() - INTERVAL '7 days',
        NOW(),
        INTERVAL '30 seconds'
    ) AS ts
CROSS JOIN
    (VALUES ('web-01'), ('web-02'), ('api-01')) AS hosts(host);

-- ■■■ 주식 시세 데이터 생성 ■■■
INSERT INTO stock_prices (time, symbol, price, volume, open_p, high_p, low_p, close_p)
SELECT
    ts,
    symbol,
    base_price + (random() * 20 - 10) AS price,
    (random() * 100000)::BIGINT AS volume,
    base_price + (random() * 5) AS open_p,
    base_price + (random() * 15) AS high_p,
    base_price - (random() * 10) AS low_p,
    base_price + (random() * 10 - 5) AS close_p
FROM
    generate_series(
        NOW() - INTERVAL '90 days',
        NOW(),
        INTERVAL '5 minutes'
    ) AS ts
CROSS JOIN (
    VALUES ('AAPL', 180.0), ('TSLA', 250.0), ('GOOG', 140.0), ('MSFT', 420.0)
) AS symbols(symbol, base_price);

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 3. time_bucket() 시간 집계                     ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- time_bucket(): TimescaleDB의 핵심 함수
-- 시간을 지정한 간격으로 버킷화(그룹화)
-- SQL의 date_trunc()과 유사하지만 더 유연함

-- ■■■ 1시간 단위 평균 온도 ■■■
SELECT
    -- time_bucket('1 hour', time): 1시간 단위로 시간 그룹화
    time_bucket('1 hour', time) AS hour,
    sensor_id,
    location,
    ROUND(AVG(temperature)::NUMERIC, 2) AS avg_temp,    -- 평균 온도
    ROUND(MIN(temperature)::NUMERIC, 2) AS min_temp,    -- 최저 온도
    ROUND(MAX(temperature)::NUMERIC, 2) AS max_temp,    -- 최고 온도
    COUNT(*) AS readings                                 -- 측정 횟수
FROM sensor_data
WHERE time > NOW() - INTERVAL '1 day'                    -- 최근 24시간
GROUP BY hour, sensor_id, location
ORDER BY hour DESC, sensor_id
LIMIT 20;

-- ■■■ 5분 단위 서버 메트릭 집계 ■■■
SELECT
    time_bucket('5 minutes', time) AS five_min,
    host,
    ROUND(AVG(cpu_usage)::NUMERIC, 1) AS avg_cpu,
    ROUND(MAX(cpu_usage)::NUMERIC, 1) AS max_cpu,
    ROUND(AVG(memory_usage)::NUMERIC, 1) AS avg_memory,
    SUM(request_count) AS total_requests,
    SUM(error_count) AS total_errors,
    -- 에러율 계산
    CASE
        WHEN SUM(request_count) > 0
        THEN ROUND(SUM(error_count)::NUMERIC / SUM(request_count) * 100, 2)
        ELSE 0
    END AS error_rate_pct,
    ROUND(AVG(response_time)::NUMERIC, 1) AS avg_response_ms
FROM server_metrics
WHERE time > NOW() - INTERVAL '1 hour'
GROUP BY five_min, host
ORDER BY five_min DESC, host
LIMIT 20;

-- ■■■ 일별 주식 OHLCV 캔들스틱 데이터 ■■■
SELECT
    time_bucket('1 day', time) AS day,
    symbol,
    -- first(): 시간순 첫 번째 값 (시가)
    first(price, time) AS open_price,
    -- last(): 시간순 마지막 값 (종가)
    last(price, time) AS close_price,
    MAX(price) AS high_price,
    MIN(price) AS low_price,
    SUM(volume) AS total_volume,
    -- 일일 변동률
    ROUND(((last(price, time) - first(price, time)) / first(price, time) * 100)::NUMERIC, 2) AS change_pct
FROM stock_prices
WHERE time > NOW() - INTERVAL '30 days'
GROUP BY day, symbol
ORDER BY day DESC, symbol
LIMIT 20;

-- ■■■ 다양한 time_bucket 간격 ■■■
-- 15초, 1분, 5분, 15분, 1시간, 6시간, 1일, 1주, 1달 등 자유롭게 설정 가능
-- time_bucket('15 seconds', time)
-- time_bucket('5 minutes', time)
-- time_bucket('1 hour', time)
-- time_bucket('1 day', time)
-- time_bucket('1 week', time)
-- time_bucket('1 month', time)

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 4. 연속 집계 (Continuous Aggregates)            ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- 연속 집계: 실시간으로 자동 업데이트되는 물질화된 뷰
-- 매번 전체 데이터를 집계하는 대신, 변경된 부분만 증분 업데이트
-- 대시보드, 리포트 쿼리 성능을 수백~수천 배 향상

-- ■■■ 1시간 단위 센서 연속 집계 ■■■
CREATE MATERIALIZED VIEW IF NOT EXISTS sensor_hourly
WITH (timescaledb.continuous) AS    -- timescaledb.continuous: 연속 집계 활성화
SELECT
    time_bucket('1 hour', time) AS bucket,     -- 1시간 단위 버킷
    sensor_id,
    location,
    AVG(temperature) AS avg_temp,
    MIN(temperature) AS min_temp,
    MAX(temperature) AS max_temp,
    AVG(humidity) AS avg_humidity,
    AVG(pressure) AS avg_pressure,
    AVG(battery) AS avg_battery,
    COUNT(*) AS sample_count
FROM sensor_data
GROUP BY bucket, sensor_id, location
WITH NO DATA;                       -- 초기 데이터 없이 생성 (나중에 리프레시)

-- ■■■ 연속 집계 정책 설정: 자동 리프레시 ■■■
-- add_continuous_aggregate_policy: 자동 리프레시 스케줄 설정
SELECT add_continuous_aggregate_policy('sensor_hourly',
    start_offset => INTERVAL '3 days',    -- 3일 전 데이터부터 리프레시
    end_offset => INTERVAL '1 hour',      -- 최근 1시간은 제외 (아직 데이터 유입 중)
    schedule_interval => INTERVAL '1 hour', -- 1시간마다 리프레시 실행
    if_not_exists => TRUE
);

-- ■■■ 수동 리프레시 (즉시 실행) ■■■
CALL refresh_continuous_aggregate('sensor_hourly', NULL, NOW());

-- ■■■ 1일 단위 서버 메트릭 연속 집계 ■■■
CREATE MATERIALIZED VIEW IF NOT EXISTS metrics_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS bucket,
    host,
    service,
    AVG(cpu_usage) AS avg_cpu,
    MAX(cpu_usage) AS max_cpu,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY cpu_usage) AS p95_cpu,  -- 95번째 백분위
    AVG(memory_usage) AS avg_memory,
    SUM(request_count) AS total_requests,
    SUM(error_count) AS total_errors,
    AVG(response_time) AS avg_response_time,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_time) AS p99_response  -- P99 응답시간
FROM server_metrics
GROUP BY bucket, host, service
WITH NO DATA;

SELECT add_continuous_aggregate_policy('metrics_daily',
    start_offset => INTERVAL '7 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

CALL refresh_continuous_aggregate('metrics_daily', NULL, NOW());

-- ■■■ 연속 집계 사용: 일반 뷰처럼 조회 ■■■
-- SELECT * FROM sensor_hourly
-- WHERE bucket > NOW() - INTERVAL '7 days'
-- ORDER BY bucket DESC;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 5. 압축 정책 (Compression)                     ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- TimescaleDB 네이티브 압축:
--   - 최대 90%+ 저장 공간 절약
--   - 압축된 데이터도 쿼리 가능 (투명한 압축 해제)
--   - 컬럼 기반 압축 (분석 쿼리에 유리)

-- ■■■ 센서 데이터 압축 설정 ■■■
ALTER TABLE sensor_data SET (
    timescaledb.compress,                               -- 압축 활성화
    timescaledb.compress_segmentby = 'sensor_id',       -- 세그먼트 기준 (같은 센서끼리 그룹)
    timescaledb.compress_orderby = 'time DESC'          -- 정렬 기준 (시간 내림차순)
);

-- ■■■ 자동 압축 정책 설정 ■■■
-- 7일 이전 데이터를 자동으로 압축
SELECT add_compression_policy('sensor_data',
    compress_after => INTERVAL '7 days',    -- 7일 지난 청크 자동 압축
    if_not_exists => TRUE
);

-- ■■■ 서버 메트릭 압축 설정 ■■■
ALTER TABLE server_metrics SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'host, service',   -- 호스트+서비스별 세그먼트
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('server_metrics',
    compress_after => INTERVAL '3 days',
    if_not_exists => TRUE
);

-- ■■■ 수동 압축 실행 ■■■
-- SELECT compress_chunk(c.chunk_name)
-- FROM timescaledb_information.chunks c
-- WHERE c.hypertable_name = 'sensor_data'
--   AND c.range_end < NOW() - INTERVAL '7 days'
--   AND NOT c.is_compressed;

-- ■■■ 압축 상태 확인 ■■■
SELECT
    hypertable_name,
    chunk_name,
    range_start,
    range_end,
    is_compressed,
    pg_size_pretty(before_compression_total_bytes) AS before_size,
    pg_size_pretty(after_compression_total_bytes) AS after_size,
    ROUND((1 - after_compression_total_bytes::NUMERIC /
           NULLIF(before_compression_total_bytes, 0)) * 100, 1) AS compression_ratio
FROM timescaledb_information.chunks
WHERE hypertable_name = 'sensor_data'
ORDER BY range_start DESC
LIMIT 10;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 6. 보존 정책 (Retention)                       ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- 오래된 데이터를 자동으로 삭제하여 디스크 공간 관리
-- DROP CHUNK: 청크 단위로 빠르게 삭제 (DELETE보다 수천 배 빠름)

-- ■■■ 자동 보존 정책 설정 ■■■
-- 90일 이전 센서 데이터 자동 삭제
SELECT add_retention_policy('sensor_data',
    drop_after => INTERVAL '90 days',       -- 90일 이전 청크 삭제
    if_not_exists => TRUE
);

-- 30일 이전 서버 메트릭 삭제
SELECT add_retention_policy('server_metrics',
    drop_after => INTERVAL '30 days',
    if_not_exists => TRUE
);

-- ■■■ 수동 청크 삭제 ■■■
-- SELECT drop_chunks('sensor_data', older_than => INTERVAL '60 days');

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 7. 실시간 대시보드 쿼리                        ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ 대시보드 쿼리 1: 실시간 센서 상태 ■■■
-- 각 센서의 최신 측정값
SELECT DISTINCT ON (sensor_id)
    sensor_id,
    location,
    time AS last_reading,
    ROUND(temperature::NUMERIC, 1) AS temperature,
    ROUND(humidity::NUMERIC, 1) AS humidity,
    ROUND(battery::NUMERIC, 1) AS battery,
    -- 온도 이상 감지
    CASE
        WHEN temperature > 35 THEN '과열 경고!'
        WHEN temperature < 5 THEN '저온 경고!'
        ELSE '정상'
    END AS status
FROM sensor_data
ORDER BY sensor_id, time DESC;

-- ■■■ 대시보드 쿼리 2: 시간대별 트래픽 히트맵 ■■■
SELECT
    EXTRACT(DOW FROM time) AS day_of_week,      -- 요일 (0=일, 6=토)
    EXTRACT(HOUR FROM time) AS hour_of_day,     -- 시간대 (0-23)
    ROUND(AVG(cpu_usage)::NUMERIC, 1) AS avg_cpu,
    SUM(request_count) AS total_requests
FROM server_metrics
WHERE time > NOW() - INTERVAL '7 days'
GROUP BY day_of_week, hour_of_day
ORDER BY day_of_week, hour_of_day;

-- ■■■ 대시보드 쿼리 3: 이동 평균 (Moving Average) ■■■
SELECT
    time_bucket('1 hour', time) AS hour,
    symbol,
    AVG(price) AS avg_price,
    -- 24시간 이동 평균 (Simple Moving Average)
    AVG(AVG(price)) OVER (
        PARTITION BY symbol
        ORDER BY time_bucket('1 hour', time)
        ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
    ) AS sma_24h
FROM stock_prices
WHERE time > NOW() - INTERVAL '7 days'
GROUP BY hour, symbol
ORDER BY hour DESC, symbol
LIMIT 20;

-- ■■■ 대시보드 쿼리 4: 이상 감지 (Anomaly Detection) ■■■
-- 3-시그마 규칙: 평균에서 표준편차 3배 이상 벗어난 값
WITH stats AS (
    SELECT
        sensor_id,
        AVG(temperature) AS mean_temp,
        STDDEV(temperature) AS stddev_temp
    FROM sensor_data
    WHERE time > NOW() - INTERVAL '7 days'
    GROUP BY sensor_id
)
SELECT
    sd.time,
    sd.sensor_id,
    sd.location,
    ROUND(sd.temperature::NUMERIC, 2) AS temperature,
    ROUND(s.mean_temp::NUMERIC, 2) AS mean_temp,
    ROUND(s.stddev_temp::NUMERIC, 2) AS stddev_temp,
    -- Z-Score: 표준 점수 (평균에서 몇 표준편차 떨어져 있는지)
    ROUND(((sd.temperature - s.mean_temp) / NULLIF(s.stddev_temp, 0))::NUMERIC, 2) AS z_score
FROM sensor_data sd
JOIN stats s ON sd.sensor_id = s.sensor_id
WHERE sd.time > NOW() - INTERVAL '1 day'
  AND ABS(sd.temperature - s.mean_temp) > 3 * s.stddev_temp  -- 3-시그마 이상
ORDER BY sd.time DESC
LIMIT 20;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 8. 하이퍼테이블 정보 조회                       ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ 하이퍼테이블 목록 ■■■
SELECT
    hypertable_name,
    num_dimensions,           -- 차원 수 (보통 1: 시간)
    num_chunks,               -- 청크 수
    pg_size_pretty(hypertable_size(format('%I.%I', hypertable_schema, hypertable_name)::regclass)) AS total_size
FROM timescaledb_information.hypertables;

-- ■■■ 청크 상세 정보 ■■■
SELECT
    hypertable_name,
    chunk_name,
    range_start,
    range_end,
    is_compressed,
    pg_size_pretty(pg_total_relation_size(format('%I.%I', chunk_schema, chunk_name)::regclass)) AS chunk_size
FROM timescaledb_information.chunks
WHERE hypertable_name = 'sensor_data'
ORDER BY range_start DESC
LIMIT 10;

-- ■■■ 정책 확인 ■■■
-- 압축 정책
SELECT * FROM timescaledb_information.compression_settings;

-- 모든 자동화 작업 (정책)
SELECT * FROM timescaledb_information.jobs
ORDER BY job_id;

-- ■■■ 데이터 삽입 완료 메시지 ■■■
SELECT '■■■ TimescaleDB 초기화 완료! ■■■' AS message;
SELECT
    'sensor_data: ' || COUNT(*) || '건' AS info
FROM sensor_data
UNION ALL
SELECT 'server_metrics: ' || COUNT(*) || '건' FROM server_metrics
UNION ALL
SELECT 'stock_prices: ' || COUNT(*) || '건' FROM stock_prices;
