# ■■■ PostgreSQL 프로덕션 배포 가이드 ■■■

## ■■■ 1. 프로덕션 배포 체크리스트 ■■■

```
■ 서버 설정
[ ] shared_buffers = RAM의 25%
[ ] effective_cache_size = RAM의 50~75%
[ ] work_mem = RAM / (max_connections × 4)
[ ] maintenance_work_mem = RAM의 5~10%
[ ] random_page_cost = 1.1 (SSD)
[ ] effective_io_concurrency = 200 (SSD)

■ WAL 설정
[ ] wal_level = replica
[ ] max_wal_size = 2~4GB
[ ] checkpoint_completion_target = 0.9
[ ] archive_mode = on (PITR 필요 시)

■ VACUUM 설정
[ ] autovacuum = on (절대 끄지 마세요!)
[ ] autovacuum_vacuum_scale_factor = 0.05
[ ] autovacuum_analyze_scale_factor = 0.05

■ 보안
[ ] pg_hba.conf: scram-sha-256 인증
[ ] SSL 인증서 설정
[ ] 불필요한 public 권한 제거
[ ] 강력한 비밀번호 정책
[ ] 정기 비밀번호 변경

■ 모니터링
[ ] pg_stat_statements 확장 설치
[ ] Prometheus postgres_exporter 설정
[ ] 느린 쿼리 로깅 (log_min_duration_statement)
[ ] 연결 수 모니터링
[ ] 디스크 공간 모니터링

■ 백업
[ ] 일일 pg_dump 자동화
[ ] WAL 아카이빙 설정
[ ] 스트리밍 복제 (Standby)
[ ] 백업 복원 테스트 (월 1회)

■ 커넥션 풀링
[ ] PgBouncer 설치 및 설정
[ ] transaction 풀링 모드
[ ] 적절한 pool_size 설정
```

## ■■■ 2. 커넥션 풀링 (PgBouncer) ■■■

### 왜 필요한가?

```
PgBouncer 없이:
  App 인스턴스 1 (100 연결) ──┐
  App 인스턴스 2 (100 연결) ──┼──→ PostgreSQL (300 연결)
  App 인스턴스 3 (100 연결) ──┘    → 각 연결 ~10MB 메모리 = 3GB!

PgBouncer 사용:
  App 인스턴스 1 (100 연결) ──┐
  App 인스턴스 2 (100 연결) ──┼──→ PgBouncer ──→ PostgreSQL (25 연결)
  App 인스턴스 3 (100 연결) ──┘    (300→25)       → 250MB만 사용!
```

### 풀링 모드 비교

| 모드 | 설명 | 장점 | 단점 |
|------|------|------|------|
| session | 세션 종료까지 연결 유지 | 완벽한 호환성 | 풀링 효과 낮음 |
| **transaction** | 트랜잭션 종료 시 반환 | **최적의 효율 (권장)** | SET, PREPARE 주의 |
| statement | 각 SQL 문마다 반환 | 최대 효율 | 다중 문 트랜잭션 불가 |

### PgBouncer 접속 및 관리

```bash
# PgBouncer를 통한 접속
psql -h localhost -p 6432 -U postgres -d study_db

# PgBouncer 관리 콘솔 (pgbouncer 가상 DB)
psql -h localhost -p 6432 -U postgres -d pgbouncer

# 관리 콘솔 명령어
SHOW POOLS;          # 풀 상태 확인
SHOW STATS;          # 통계 확인
SHOW CLIENTS;        # 클라이언트 연결 목록
SHOW SERVERS;        # 서버 연결 목록
SHOW CONFIG;         # 현재 설정 확인
RELOAD;              # 설정 다시 로드
PAUSE study_db;      # 데이터베이스 일시 중지 (유지보수)
RESUME study_db;     # 데이터베이스 재개
```

## ■■■ 3. 모니터링 ■■■

### 핵심 모니터링 쿼리

```sql
-- ■■■ 활성 세션 확인 ■■■
SELECT
    pid, usename, datname, state,
    wait_event_type, wait_event,
    NOW() - query_start AS duration,
    LEFT(query, 100) AS query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;

-- ■■■ 연결 수 확인 ■■■
SELECT
    datname,
    COUNT(*) AS connections,
    COUNT(*) FILTER (WHERE state = 'active') AS active,
    COUNT(*) FILTER (WHERE state = 'idle') AS idle,
    COUNT(*) FILTER (WHERE state = 'idle in transaction') AS idle_in_txn
FROM pg_stat_activity
GROUP BY datname;

-- ■■■ 잠금 대기 확인 ■■■
SELECT
    blocked.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    LEFT(blocked_activity.query, 80) AS blocked_query,
    LEFT(blocking_activity.query, 80) AS blocking_query
FROM pg_catalog.pg_locks blocked
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked.pid
JOIN pg_catalog.pg_locks blocking ON blocking.locktype = blocked.locktype
    AND blocking.database IS NOT DISTINCT FROM blocked.database
    AND blocking.relation IS NOT DISTINCT FROM blocked.relation
    AND blocking.page IS NOT DISTINCT FROM blocked.page
    AND blocking.tuple IS NOT DISTINCT FROM blocked.tuple
    AND blocking.virtualxid IS NOT DISTINCT FROM blocked.virtualxid
    AND blocking.transactionid IS NOT DISTINCT FROM blocked.transactionid
    AND blocking.classid IS NOT DISTINCT FROM blocked.classid
    AND blocking.objid IS NOT DISTINCT FROM blocked.objid
    AND blocking.objsubid IS NOT DISTINCT FROM blocked.objsubid
    AND blocking.pid != blocked.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking.pid
WHERE NOT blocked.granted;

-- ■■■ 데이터베이스 크기 ■■■
SELECT
    datname,
    pg_size_pretty(pg_database_size(datname)) AS size
FROM pg_database
ORDER BY pg_database_size(datname) DESC;

-- ■■■ 테이블 크기 TOP 10 ■■■
SELECT
    schemaname || '.' || relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
    pg_size_pretty(pg_relation_size(relid)) AS table_size,
    pg_size_pretty(pg_indexes_size(relid)) AS index_size,
    n_live_tup AS live_rows,
    n_dead_tup AS dead_rows
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 10;

-- ■■■ 느린 쿼리 TOP 10 (pg_stat_statements 필요) ■■■
SELECT
    LEFT(query, 100) AS query,
    calls,
    ROUND(mean_exec_time::NUMERIC, 2) AS avg_time_ms,
    ROUND(total_exec_time::NUMERIC, 2) AS total_time_ms,
    rows AS total_rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- ■■■ 캐시 적중률 (99% 이상이어야 정상) ■■■
SELECT
    datname,
    ROUND(
        blks_hit::NUMERIC / NULLIF(blks_hit + blks_read, 0) * 100, 2
    ) AS cache_hit_ratio
FROM pg_stat_database
WHERE datname NOT LIKE 'template%';

-- ■■■ 인덱스 적중률 ■■■
SELECT
    relname AS table_name,
    ROUND(
        idx_scan::NUMERIC / NULLIF(idx_scan + seq_scan, 0) * 100, 2
    ) AS index_usage_pct,
    seq_scan,
    idx_scan
FROM pg_stat_user_tables
WHERE (seq_scan + idx_scan) > 0
ORDER BY index_usage_pct ASC
LIMIT 10;
```

### Prometheus 메트릭 확인

```bash
# postgres_exporter 메트릭 확인
curl http://localhost:9187/metrics

# 주요 메트릭:
# pg_stat_database_numbackends       - 현재 연결 수
# pg_stat_database_xact_commit       - 커밋 트랜잭션 수
# pg_stat_database_xact_rollback     - 롤백 트랜잭션 수
# pg_stat_database_blks_hit          - 캐시 히트 수
# pg_stat_database_blks_read         - 디스크 읽기 수
# pg_stat_database_tup_inserted      - 삽입된 행 수
# pg_stat_database_tup_updated       - 업데이트된 행 수
# pg_stat_database_tup_deleted       - 삭제된 행 수
# pg_stat_database_deadlocks         - 데드락 수
# pg_stat_database_temp_files        - 임시 파일 수
# pg_stat_database_temp_bytes        - 임시 파일 크기
```

## ■■■ 4. 트러블슈팅 ■■■

### 연결 부족 (too many clients)

```
증상: FATAL: sorry, too many clients already

원인:
  - max_connections 초과
  - 연결 누수 (close 안 함)
  - idle in transaction 연결 방치

해결:
  1. 현재 연결 상태 확인
     SELECT state, COUNT(*) FROM pg_stat_activity GROUP BY state;

  2. 오래된 idle 연결 종료
     SELECT pg_terminate_backend(pid) FROM pg_stat_activity
     WHERE state = 'idle' AND query_start < NOW() - INTERVAL '1 hour';

  3. PgBouncer 도입 (근본 해결)

  4. idle_in_transaction_session_timeout 설정
     SET idle_in_transaction_session_timeout = '5min';
```

### 느린 쿼리

```
진단 절차:
  1. 느린 쿼리 로그 확인
     log_min_duration_statement = 1000  # 1초 이상

  2. pg_stat_statements로 TOP N 조회
     SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC;

  3. EXPLAIN ANALYZE로 실행 계획 분석
     EXPLAIN (ANALYZE, BUFFERS) SELECT ...;

  4. 인덱스 확인 및 추가
     - Seq Scan → 인덱스 필요
     - 큰 Sort → 인덱스로 정렬 대체

  5. 통계 갱신
     ANALYZE table_name;
```

### 디스크 공간 부족

```
확인:
  1. 데이터베이스 크기
     SELECT pg_size_pretty(pg_database_size('study_db'));

  2. 큰 테이블 찾기
     SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
     FROM pg_stat_user_tables ORDER BY pg_total_relation_size(relid) DESC;

  3. 블로트 확인
     SELECT relname, n_dead_tup FROM pg_stat_user_tables
     WHERE n_dead_tup > 10000 ORDER BY n_dead_tup DESC;

해결:
  1. VACUUM FULL (테이블 잠금 주의!)
  2. 오래된 데이터 삭제
  3. 사용 안 하는 인덱스 삭제
  4. WAL 파일 정리 확인
```

### 데드락

```
확인:
  SELECT * FROM pg_locks WHERE NOT granted;

예방:
  1. 트랜잭션을 짧게 유지
  2. 동일한 순서로 테이블/행 접근
  3. 적절한 isolation level 사용
  4. deadlock_timeout 모니터링

로그 확인:
  log_lock_waits = on
  deadlock_timeout = 1s
```

## ■■■ 5. 성능 튜닝 공식 ■■■

```
서버 RAM 기준 설정 계산:

┌────────────────────────────┬──────────────────────────┐
│ 설정                        │ 공식                      │
├────────────────────────────┼──────────────────────────┤
│ shared_buffers             │ RAM × 0.25               │
│ effective_cache_size       │ RAM × 0.625              │
│ work_mem                   │ RAM / (max_conn × 4)     │
│ maintenance_work_mem       │ RAM × 0.0625 (최대 2GB)  │
│ max_wal_size               │ RAM × 0.25 ~ 0.5        │
│ wal_buffers                │ shared_buffers / 32      │
└────────────────────────────┴──────────────────────────┘

예시 (8GB RAM, max_connections=100):
  shared_buffers      = 2GB
  effective_cache_size = 5GB
  work_mem            = 20MB
  maintenance_work_mem = 512MB
  max_wal_size        = 2GB

예시 (32GB RAM, max_connections=200):
  shared_buffers      = 8GB
  effective_cache_size = 20GB
  work_mem            = 40MB
  maintenance_work_mem = 2GB
  max_wal_size        = 8GB
```

## ■■■ 6. 일상 운영 명령어 ■■■

```bash
# ■■■ 환경 관리 ■■■
docker-compose up -d           # 시작
docker-compose down            # 중지
docker-compose logs -f postgres  # 로그 확인

# ■■■ PgBouncer를 통한 접속 ■■■
psql -h localhost -p 6432 -U postgres -d study_db

# ■■■ 직접 접속 (관리용) ■■■
psql -h localhost -p 5432 -U postgres -d study_db

# ■■■ 백업 ■■■
pg_dump -h localhost -p 5432 -U postgres -Fc study_db > backup_$(date +%Y%m%d).dump

# ■■■ 메트릭 확인 ■■■
curl -s http://localhost:9187/metrics | grep pg_stat_database_numbackends

# ■■■ pgAdmin ■■■
# http://localhost:5050 (admin@admin.com / admin123)

# ■■■ 설정 리로드 (재시작 없이) ■■■
docker exec pg-production psql -U postgres -c "SELECT pg_reload_conf();"

# ■■■ 현재 설정 확인 ■■■
docker exec pg-production psql -U postgres -c "SHOW shared_buffers;"
docker exec pg-production psql -U postgres -c "SHOW work_mem;"
docker exec pg-production psql -U postgres -c "SHOW max_connections;"
```
