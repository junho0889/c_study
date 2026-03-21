-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ PostgreSQL 인덱싱 & 성능 최적화                 ■■■
-- ■■■ B-tree, Hash, GiST, GIN, EXPLAIN ANALYZE        ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 인덱스 타입 총정리                              ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- ┌────────────┬──────────────────────────────────────────────────┐
-- │ 인덱스 타입 │ 설명 및 사용 사례                                │
-- ├────────────┼──────────────────────────────────────────────────┤
-- │ B-tree     │ 기본 인덱스. =, <, >, <=, >=, BETWEEN, IN,     │
-- │            │ IS NULL, LIKE 'abc%' (접두사만) 연산에 사용       │
-- │            │ 대부분의 경우 이것을 사용                          │
-- ├────────────┼──────────────────────────────────────────────────┤
-- │ Hash       │ 등호(=) 비교만 지원. B-tree보다 약간 빠를 수 있음 │
-- │            │ WAL 지원 (PG 10+), 거의 사용할 일 없음            │
-- ├────────────┼──────────────────────────────────────────────────┤
-- │ GiST       │ Generalized Search Tree. 기하학(geometry),       │
-- │            │ 범위(range), 전문검색(tsvector) 등 복잡한 데이터  │
-- │            │ PostGIS 공간 인덱스에 주로 사용                    │
-- ├────────────┼──────────────────────────────────────────────────┤
-- │ GIN        │ Generalized Inverted Index. 역색인.              │
-- │            │ 배열, JSONB, 전문검색(tsvector), hstore에 최적    │
-- │            │ 포함 여부(@>, ?, ?|, ?&) 검색에 강력               │
-- ├────────────┼──────────────────────────────────────────────────┤
-- │ BRIN       │ Block Range Index. 물리적으로 정렬된 큰 테이블    │
-- │            │ 타임스탬프 같은 자연 정렬 데이터에 적합             │
-- │            │ 매우 작은 크기, 시계열 데이터에 권장                │
-- ├────────────┼──────────────────────────────────────────────────┤
-- │ SP-GiST    │ Space-partitioned GiST. 비균형 트리 구조          │
-- │            │ IP 주소(inet), 전화번호 등 분할 가능 데이터         │
-- └────────────┴──────────────────────────────────────────────────┘

-- ■■■ 성능 테스트용 대량 데이터 생성 ■■■
CREATE TABLE IF NOT EXISTS perf_test (
    id SERIAL PRIMARY KEY,
    user_name VARCHAR(100),
    email VARCHAR(255),
    department VARCHAR(50),
    salary NUMERIC(10, 2),
    hire_date DATE,
    status VARCHAR(20),
    tags TEXT[],
    metadata JSONB,
    location POINT,           -- 기하학 타입 (x, y 좌표)
    ip_address INET,          -- IP 주소 타입
    search_text TSVECTOR,     -- 전문 검색 벡터
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ■■■ 100,000건 테스트 데이터 삽입 ■■■
-- generate_series: 1부터 100000까지 숫자 생성
INSERT INTO perf_test (user_name, email, department, salary, hire_date, status, tags, metadata, location, ip_address)
SELECT
    -- || : 문자열 연결 연산자
    'user_' || i AS user_name,
    'user_' || i || '@company.com' AS email,
    -- CASE: 부서를 5개로 순환 배정
    CASE (i % 5)
        WHEN 0 THEN 'Engineering'
        WHEN 1 THEN 'Marketing'
        WHEN 2 THEN 'Sales'
        WHEN 3 THEN 'HR'
        WHEN 4 THEN 'Finance'
    END AS department,
    -- random(): 0~1 사이 난수, 40000~140000 범위 급여
    ROUND((random() * 100000 + 40000)::NUMERIC, 2) AS salary,
    -- 2015~2025년 사이 랜덤 입사일
    '2015-01-01'::DATE + (random() * 3650)::INTEGER AS hire_date,
    -- 상태를 3가지로 순환
    CASE (i % 3)
        WHEN 0 THEN 'active'
        WHEN 1 THEN 'inactive'
        WHEN 2 THEN 'pending'
    END AS status,
    -- 배열 데이터 생성
    ARRAY['tag_' || (i % 10), 'tag_' || (i % 20)] AS tags,
    -- JSONB 데이터 생성
    jsonb_build_object(
        'level', CASE (i % 4) WHEN 0 THEN 'junior' WHEN 1 THEN 'mid' WHEN 2 THEN 'senior' ELSE 'lead' END,
        'score', (random() * 100)::INT
    ) AS metadata,
    -- 좌표 데이터 (위도, 경도 시뮬레이션)
    POINT(random() * 360 - 180, random() * 180 - 90) AS location,
    -- IP 주소 생성
    ('192.168.' || (i % 256) || '.' || (i % 256))::INET AS ip_address
FROM generate_series(1, 100000) AS i
ON CONFLICT DO NOTHING;

-- 전문 검색 벡터 업데이트
UPDATE perf_test
SET search_text = to_tsvector('english', user_name || ' ' || department);

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 1. B-tree 인덱스 (기본)                        ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ 인덱스 없이 쿼리 (풀 테이블 스캔) ■■■
-- EXPLAIN ANALYZE: 실행 계획 + 실제 실행 시간 표시
EXPLAIN ANALYZE
SELECT * FROM perf_test WHERE email = 'user_50000@company.com';
-- 결과: Seq Scan (순차 스캔) → 전체 테이블을 처음부터 끝까지 읽음

-- ■■■ B-tree 인덱스 생성 ■■■
-- CONCURRENTLY: 테이블 잠금 없이 인덱스 생성 (프로덕션에서 권장)
-- 단, 트랜잭션 블록 안에서는 사용 불가
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_perf_email
    ON perf_test (email);

-- ■■■ 인덱스 생성 후 동일 쿼리 ■■■
EXPLAIN ANALYZE
SELECT * FROM perf_test WHERE email = 'user_50000@company.com';
-- 결과: Index Scan → 인덱스를 통해 직접 해당 행으로 접근 (수천 배 빠름)

-- ■■■ 복합 인덱스 (Multi-column Index) ■■■
-- 여러 컬럼을 조합한 인덱스 (컬럼 순서가 중요!)
-- (department, salary)는 department 단독 쿼리도 지원하지만,
-- salary 단독 쿼리는 지원하지 않음 (왼쪽 접두사 규칙)
CREATE INDEX IF NOT EXISTS idx_perf_dept_salary
    ON perf_test (department, salary DESC);

-- 복합 인덱스 활용 쿼리
EXPLAIN ANALYZE
SELECT * FROM perf_test
WHERE department = 'Engineering'
ORDER BY salary DESC
LIMIT 10;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 2. Hash 인덱스                                 ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- Hash 인덱스: 등호(=) 비교에만 사용 가능
-- B-tree보다 약간 작고, = 비교에서 약간 빠를 수 있음
-- 범위 검색(<, >, BETWEEN)에는 사용 불가
CREATE INDEX IF NOT EXISTS idx_perf_status_hash
    ON perf_test USING HASH (status);

EXPLAIN ANALYZE
SELECT COUNT(*) FROM perf_test WHERE status = 'active';

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 3. GiST 인덱스                                 ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- GiST: 기하학 데이터, 범위 데이터에 사용
-- POINT, BOX, CIRCLE 등의 근접 검색에 적합
CREATE INDEX IF NOT EXISTS idx_perf_location_gist
    ON perf_test USING GIST (location);

-- 특정 좌표 근처의 데이터 검색 (거리 기반)
-- <-> : 거리 연산자 (GiST 인덱스 사용)
EXPLAIN ANALYZE
SELECT user_name, location,
       location <-> POINT(0, 0) AS distance  -- 원점과의 거리
FROM perf_test
ORDER BY location <-> POINT(0, 0)            -- 거리 순 정렬
LIMIT 10;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 4. GIN 인덱스                                   ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- GIN: 역색인. 배열, JSONB, 전문 검색에 최적
-- "이 값을 포함하는 행은?" 질문에 빠르게 답변

-- ■■■ 배열 인덱스 (GIN) ■■■
CREATE INDEX IF NOT EXISTS idx_perf_tags_gin
    ON perf_test USING GIN (tags);

-- 배열 포함 검색 (@>: 왼쪽이 오른쪽을 포함하는지)
EXPLAIN ANALYZE
SELECT COUNT(*) FROM perf_test
WHERE tags @> ARRAY['tag_5'];       -- tag_5를 포함하는 행

-- ■■■ JSONB 인덱스 (GIN) ■■■
-- jsonb_path_ops: JSONB용 최적화된 GIN 연산자 클래스
-- 기본 GIN보다 작고, @> 연산에 최적화
CREATE INDEX IF NOT EXISTS idx_perf_metadata_gin
    ON perf_test USING GIN (metadata jsonb_path_ops);

-- JSONB 포함 검색
EXPLAIN ANALYZE
SELECT COUNT(*) FROM perf_test
WHERE metadata @> '{"level": "senior"}';

-- ■■■ 전문 검색 인덱스 (GIN) ■■■
CREATE INDEX IF NOT EXISTS idx_perf_search_gin
    ON perf_test USING GIN (search_text);

EXPLAIN ANALYZE
SELECT user_name, department
FROM perf_test
WHERE search_text @@ to_tsquery('english', 'Engineering');

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 5. Partial Index (부분 인덱스)                  ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- 부분 인덱스: WHERE 조건을 만족하는 행에만 인덱스 생성
-- 인덱스 크기 감소 → 성능 향상, 저장 공간 절약
CREATE INDEX IF NOT EXISTS idx_perf_active_salary
    ON perf_test (salary DESC)
    WHERE status = 'active';       -- active 상태인 행만 인덱싱

-- 부분 인덱스 활용 (WHERE 조건이 일치해야 인덱스 사용)
EXPLAIN ANALYZE
SELECT user_name, salary
FROM perf_test
WHERE status = 'active'
ORDER BY salary DESC
LIMIT 10;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 6. Expression Index (표현식 인덱스)             ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- 표현식 인덱스: 함수나 연산 결과에 인덱스 생성
-- 쿼리에서 같은 표현식을 사용해야 인덱스 활용 가능

-- LOWER(): 대소문자 무시 검색용 인덱스
CREATE INDEX IF NOT EXISTS idx_perf_email_lower
    ON perf_test (LOWER(email));

EXPLAIN ANALYZE
SELECT * FROM perf_test
WHERE LOWER(email) = 'user_12345@company.com';

-- 날짜 추출 인덱스: 연도별 조회 최적화
CREATE INDEX IF NOT EXISTS idx_perf_hire_year
    ON perf_test (EXTRACT(YEAR FROM hire_date));

EXPLAIN ANALYZE
SELECT COUNT(*) FROM perf_test
WHERE EXTRACT(YEAR FROM hire_date) = 2020;

-- JSONB 필드 인덱스: 특정 JSON 키에 대한 인덱스
CREATE INDEX IF NOT EXISTS idx_perf_metadata_level
    ON perf_test ((metadata ->> 'level'));

EXPLAIN ANALYZE
SELECT COUNT(*) FROM perf_test
WHERE metadata ->> 'level' = 'senior';

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 7. Covering Index (커버링 인덱스, INCLUDE)      ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- INCLUDE: 인덱스에 추가 컬럼 포함 (검색 키로는 사용 안 함)
-- Index-Only Scan 가능: 테이블 접근 없이 인덱스만으로 결과 반환
CREATE INDEX IF NOT EXISTS idx_perf_dept_covering
    ON perf_test (department)
    INCLUDE (user_name, salary);    -- user_name, salary는 인덱스에 포함되지만 검색 키는 아님

-- Index-Only Scan: 테이블 힙에 접근하지 않고 인덱스만 읽음 (빠름!)
EXPLAIN ANALYZE
SELECT department, user_name, salary
FROM perf_test
WHERE department = 'Engineering';

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 8. EXPLAIN ANALYZE 실행 계획 읽기              ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- EXPLAIN: 실행 계획만 표시 (쿼리 실행 안 함)
-- EXPLAIN ANALYZE: 실행 계획 + 실제 실행 (실제 시간, 행 수)
-- EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT): 버퍼 사용량 포함

-- ■■■ 실행 계획 읽기 가이드 ■■■
/*
  주요 노드 타입:
  ┌──────────────────────┬────────────────────────────────────────┐
  │ 노드                  │ 설명                                  │
  ├──────────────────────┼────────────────────────────────────────┤
  │ Seq Scan             │ 순차 스캔 (전체 테이블 읽기) → 느림     │
  │ Index Scan           │ 인덱스로 행 찾고 테이블에서 데이터 읽기  │
  │ Index Only Scan      │ 인덱스만으로 결과 반환 (가장 빠름)      │
  │ Bitmap Index Scan    │ 인덱스로 비트맵 생성                    │
  │ Bitmap Heap Scan     │ 비트맵으로 테이블 블록 읽기              │
  │ Nested Loop          │ 중첩 루프 조인 (작은 테이블 간)          │
  │ Hash Join            │ 해시 조인 (중간 크기 테이블)             │
  │ Merge Join           │ 정렬 병합 조인 (큰 정렬된 테이블)        │
  │ Sort                 │ 정렬 (ORDER BY)                        │
  │ Aggregate            │ 집계 (COUNT, SUM 등)                   │
  │ HashAggregate        │ 해시 기반 그룹화                        │
  └──────────────────────┴────────────────────────────────────────┘

  주요 메트릭:
  - cost: 예상 비용 (시작..전체)
  - rows: 예상 반환 행 수
  - actual time: 실제 실행 시간 (ms)
  - actual rows: 실제 반환 행 수
  - Buffers: shared hit(캐시 히트) / read(디스크 읽기)
  - Planning Time: 쿼리 계획 수립 시간
  - Execution Time: 쿼리 실행 시간
*/

-- ■■■ EXPLAIN 상세 옵션 ■■■
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT e.first_name, e.last_name, d.name
FROM employees e
JOIN departments d ON e.department_id = d.id
WHERE e.salary > 70000
ORDER BY e.salary DESC;

-- ■■■ EXPLAIN FORMAT JSON: JSON 형식 출력 ■■■
-- 프로그래밍 언어에서 파싱하기 쉬움
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT * FROM perf_test WHERE department = 'Engineering' LIMIT 10;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 9. 인덱스 관리 및 모니터링                      ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ 테이블의 모든 인덱스 확인 ■■■
SELECT
    indexname AS index_name,       -- 인덱스 이름
    indexdef AS index_definition   -- 인덱스 정의 (CREATE INDEX 문)
FROM pg_indexes
WHERE tablename = 'perf_test'
ORDER BY indexname;

-- ■■■ 인덱스 크기 확인 ■■■
SELECT
    indexrelname AS index_name,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_scan AS times_used,                -- 인덱스 스캔 횟수
    idx_tup_read AS tuples_read,           -- 인덱스에서 읽은 행 수
    idx_tup_fetch AS tuples_fetched        -- 테이블에서 가져온 행 수
FROM pg_stat_user_indexes
WHERE relname = 'perf_test'
ORDER BY pg_relation_size(indexrelid) DESC;

-- ■■■ 사용되지 않는 인덱스 찾기 ■■■
-- idx_scan = 0인 인덱스는 삭제 후보 (공간 낭비 + INSERT/UPDATE 성능 저하)
SELECT
    schemaname || '.' || relname AS table_name,
    indexrelname AS index_name,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_scan AS times_used
FROM pg_stat_user_indexes
WHERE idx_scan = 0                          -- 한 번도 사용되지 않은 인덱스
  AND indexrelname NOT LIKE '%_pkey'        -- 기본 키 인덱스 제외
ORDER BY pg_relation_size(indexrelid) DESC;

-- ■■■ 테이블 + 인덱스 전체 크기 ■■■
SELECT
    pg_size_pretty(pg_total_relation_size('perf_test')) AS total_size,     -- 테이블+인덱스 전체
    pg_size_pretty(pg_relation_size('perf_test')) AS table_size,           -- 테이블만
    pg_size_pretty(pg_indexes_size('perf_test')) AS all_indexes_size       -- 인덱스 전체
;

-- ■■■ 인덱스 REINDEX: 인덱스 재구축 (블로트 해소) ■■■
-- 많은 UPDATE/DELETE 후 인덱스가 비대해질 수 있음
-- REINDEX CONCURRENTLY: 테이블 잠금 없이 재구축 (PG 12+)
-- REINDEX INDEX CONCURRENTLY idx_perf_email;

-- ■■■ 인덱스 삭제 ■■■
-- DROP INDEX CONCURRENTLY IF EXISTS idx_perf_status_hash;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 10. 쿼리 최적화 팁                             ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ 통계 업데이트: ANALYZE ■■■
-- 쿼리 플래너가 최적의 실행 계획을 세우려면 정확한 통계가 필요
ANALYZE perf_test;     -- 특정 테이블 통계 갱신
-- ANALYZE;            -- 전체 데이터베이스 통계 갱신

-- ■■■ pg_stat_statements: 느린 쿼리 찾기 ■■■
-- 확장 설치 필요: CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
-- SELECT
--     query,
--     calls,                            -- 호출 횟수
--     mean_exec_time,                   -- 평균 실행 시간 (ms)
--     total_exec_time,                  -- 총 실행 시간 (ms)
--     rows                              -- 반환 행 수
-- FROM pg_stat_statements
-- ORDER BY mean_exec_time DESC
-- LIMIT 10;

-- ■■■ 테이블 블로트 확인 ■■■
-- dead tuple이 많으면 VACUUM 필요
SELECT
    relname AS table_name,
    n_live_tup AS live_rows,              -- 살아있는 행 수
    n_dead_tup AS dead_rows,              -- 죽은 행 수 (삭제/업데이트 후 미회수)
    n_mod_since_analyze AS mods_since_analyze,  -- ANALYZE 이후 변경 수
    last_vacuum,                           -- 마지막 VACUUM 시각
    last_autovacuum,                       -- 마지막 auto VACUUM 시각
    last_analyze                           -- 마지막 ANALYZE 시각
FROM pg_stat_user_tables
WHERE relname = 'perf_test';

-- ■■■ VACUUM: 죽은 행 회수 ■■■
-- VACUUM: 죽은 행 표시만 정리 (디스크 공간 반환 안 함)
-- VACUUM FULL: 테이블 재작성 (디스크 공간 반환, 테이블 잠금!)
-- VACUUM (VERBOSE) perf_test;
