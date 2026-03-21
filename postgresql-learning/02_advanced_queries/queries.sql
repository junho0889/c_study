-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ PostgreSQL 고급 쿼리 학습                       ■■■
-- ■■■ Window Functions, CTE, LATERAL, JSON 등         ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- 사전 조건: 01_basics/init.sql이 실행된 상태에서 사용
-- 접속: docker-compose exec postgres psql -U postgres -d study_db

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 1. Window Functions (윈도우 함수)              ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- 윈도우 함수: GROUP BY 없이 집계 + 원본 행 유지
-- 구문: 함수() OVER (PARTITION BY ... ORDER BY ... FRAME ...)
-- GROUP BY와의 차이: GROUP BY는 행을 그룹으로 축소하지만,
--                    윈도우 함수는 모든 행을 유지하면서 집계 가능

-- ■■■ ROW_NUMBER(): 행 번호 부여 (1, 2, 3, ...) ■■■
-- 부서별로 급여 높은 순서대로 번호 매기기
SELECT
    first_name,
    last_name,
    d.name AS department,
    salary,
    -- PARTITION BY: 부서별로 그룹 나누기
    -- ORDER BY: 급여 내림차순으로 번호 부여
    ROW_NUMBER() OVER (
        PARTITION BY e.department_id    -- 부서별로 번호 초기화
        ORDER BY e.salary DESC          -- 급여 높은 순
    ) AS rank_in_dept
FROM employees e
JOIN departments d ON e.department_id = d.id;

-- ■■■ RANK() vs DENSE_RANK(): 순위 부여 ■■■
-- RANK(): 동일 값이면 같은 순위, 다음 순위 건너뜀 (1, 2, 2, 4)
-- DENSE_RANK(): 동일 값이면 같은 순위, 다음 순위 연속 (1, 2, 2, 3)
SELECT
    first_name, last_name, salary,
    RANK() OVER (ORDER BY salary DESC) AS rank,              -- 1, 2, 2, 4
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank,  -- 1, 2, 2, 3
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num      -- 1, 2, 3, 4
FROM employees;

-- ■■■ LAG() / LEAD(): 이전/다음 행 참조 ■■■
-- LAG(컬럼, N): N개 이전 행의 값 (기본 N=1)
-- LEAD(컬럼, N): N개 다음 행의 값
SELECT
    first_name, last_name, salary,
    -- 이전 직원의 급여 (급여 순 정렬 기준)
    LAG(salary, 1) OVER (ORDER BY salary DESC) AS prev_salary,
    -- 다음 직원의 급여
    LEAD(salary, 1) OVER (ORDER BY salary DESC) AS next_salary,
    -- 이전 직원과의 급여 차이
    salary - LAG(salary, 1) OVER (ORDER BY salary DESC) AS salary_diff
FROM employees;

-- ■■■ SUM() OVER: 누적 합계 (Running Total) ■■■
SELECT
    first_name, last_name, salary,
    -- 입사일 순서로 급여 누적 합계
    SUM(salary) OVER (
        ORDER BY hire_date
        -- ROWS BETWEEN: 윈도우 프레임 정의
        -- UNBOUNDED PRECEDING: 파티션의 첫 행부터
        -- CURRENT ROW: 현재 행까지
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total,
    -- 부서별 급여 합계 (파티션 내 전체)
    SUM(salary) OVER (PARTITION BY department_id) AS dept_total,
    -- 전체 급여 대비 비율
    ROUND(salary / SUM(salary) OVER () * 100, 2) AS salary_pct
FROM employees
ORDER BY hire_date;

-- ■■■ NTILE(): N개 그룹으로 균등 분할 ■■■
-- 급여 기준으로 4개 분위(사분위수)로 나누기
SELECT
    first_name, last_name, salary,
    NTILE(4) OVER (ORDER BY salary) AS quartile  -- 1~4 사분위
FROM employees;

-- ■■■ FIRST_VALUE() / LAST_VALUE(): 첫/마지막 값 ■■■
SELECT
    first_name, last_name, salary, d.name AS department,
    -- 부서 내 최고 급여자 이름
    FIRST_VALUE(first_name || ' ' || last_name) OVER (
        PARTITION BY e.department_id
        ORDER BY salary DESC
    ) AS highest_paid_in_dept,
    -- 부서 내 최고 급여
    FIRST_VALUE(salary) OVER (
        PARTITION BY e.department_id
        ORDER BY salary DESC
    ) AS max_dept_salary
FROM employees e
JOIN departments d ON e.department_id = d.id;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 2. CTE (Common Table Expression)              ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- WITH 절로 임시 결과 집합을 정의 (서브쿼리의 가독성 좋은 대안)
-- 같은 쿼리 내에서 여러 번 참조 가능

-- ■■■ 기본 CTE: 부서별 통계 → 평균 이상 부서 필터 ■■■
WITH dept_stats AS (
    -- CTE 정의: 부서별 직원 수, 평균 급여 계산
    SELECT
        d.name AS department,
        COUNT(*) AS emp_count,
        ROUND(AVG(e.salary), 2) AS avg_salary,
        SUM(e.salary) AS total_salary
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    GROUP BY d.name
)
-- CTE 결과를 메인 쿼리에서 사용
SELECT *
FROM dept_stats
WHERE avg_salary > (SELECT AVG(avg_salary) FROM dept_stats)  -- 전체 평균보다 높은 부서
ORDER BY avg_salary DESC;

-- ■■■ 다중 CTE: 여러 CTE를 순차적으로 정의 ■■■
WITH
    -- CTE 1: 활성 프로젝트 목록
    active_projects AS (
        SELECT id, name, budget
        FROM projects
        WHERE status = 'active'
    ),
    -- CTE 2: 프로젝트별 참여 직원 수
    project_members AS (
        SELECT
            project_id,
            COUNT(*) AS member_count
        FROM employee_projects
        GROUP BY project_id
    )
-- 두 CTE를 조인하여 결과 생성
SELECT
    ap.name AS project,
    ap.budget,
    COALESCE(pm.member_count, 0) AS members  -- NULL이면 0
FROM active_projects ap
LEFT JOIN project_members pm ON ap.id = pm.project_id;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 3. Recursive CTE (재귀 CTE)                   ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- 자기 참조 데이터 (트리, 계층 구조) 처리에 사용

-- ■■■ 재귀 CTE용 테이블 생성: 조직도 (자기 참조) ■■■
CREATE TABLE IF NOT EXISTS org_chart (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    title VARCHAR(100),
    manager_id INTEGER REFERENCES org_chart(id)  -- 자기 참조 외래 키
);

-- 데이터 삽입 (계층 구조)
INSERT INTO org_chart (id, name, title, manager_id) VALUES
    (1, '김대표', 'CEO', NULL),        -- 최상위 (관리자 없음)
    (2, '이부장', 'VP Engineering', 1),
    (3, '박부장', 'VP Marketing', 1),
    (4, '최팀장', 'Team Lead', 2),
    (5, '정개발', 'Senior Dev', 4),
    (6, '한주임', 'Junior Dev', 4),
    (7, '윤매니저', 'Marketing Manager', 3)
ON CONFLICT (id) DO NOTHING;  -- 중복 시 무시

-- ■■■ 재귀 CTE: 조직도 트리 탐색 ■■■
WITH RECURSIVE org_tree AS (
    -- ■ 비재귀 항 (Anchor): 시작점 (CEO, manager_id IS NULL)
    SELECT
        id, name, title, manager_id,
        1 AS level,                          -- 계층 깊이
        name::TEXT AS path                   -- 경로 (루트부터)
    FROM org_chart
    WHERE manager_id IS NULL

    UNION ALL

    -- ■ 재귀 항 (Recursive): 이전 결과의 하위 직원 찾기
    SELECT
        oc.id, oc.name, oc.title, oc.manager_id,
        ot.level + 1,                        -- 깊이 +1
        ot.path || ' → ' || oc.name          -- 경로에 현재 이름 추가
    FROM org_chart oc
    INNER JOIN org_tree ot ON oc.manager_id = ot.id  -- 부모-자식 연결
)
SELECT
    -- REPEAT: 들여쓰기로 계층 시각화
    REPEAT('  ', level - 1) || name AS org_hierarchy,
    title,
    level,
    path
FROM org_tree
ORDER BY path;  -- 경로 기준 정렬 → 트리 순서 출력

-- ■■■ 재귀 CTE: 숫자 시퀀스 생성 (1~10) ■■■
WITH RECURSIVE numbers AS (
    SELECT 1 AS n              -- 시작: 1
    UNION ALL
    SELECT n + 1 FROM numbers  -- 재귀: n+1
    WHERE n < 10               -- 종료 조건: 10까지
)
SELECT n FROM numbers;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 4. LATERAL JOIN                                ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- LATERAL: 서브쿼리가 바깥 쿼리의 각 행을 참조할 수 있게 함
-- 일반 서브쿼리와 달리, 왼쪽 테이블의 컬럼을 서브쿼리 내에서 사용 가능

-- ■■■ 부서별 급여 상위 2명 조회 (LATERAL 사용) ■■■
SELECT
    d.name AS department,
    top_emp.first_name,
    top_emp.last_name,
    top_emp.salary
FROM departments d
-- LATERAL: 각 부서(d)마다 서브쿼리 실행
CROSS JOIN LATERAL (
    SELECT first_name, last_name, salary
    FROM employees e
    WHERE e.department_id = d.id    -- 바깥 쿼리의 d.id 참조!
    ORDER BY salary DESC
    LIMIT 2                          -- 상위 2명만
) AS top_emp
ORDER BY d.name, top_emp.salary DESC;

-- ■■■ LATERAL + generate_series: 날짜 범위 확장 ■■■
-- 프로젝트 기간의 각 월을 행으로 확장
SELECT
    p.name AS project,
    month_series.month
FROM projects p
CROSS JOIN LATERAL (
    SELECT generate_series(
        DATE_TRUNC('month', p.start_date),   -- 시작 월
        COALESCE(p.end_date, CURRENT_DATE),  -- 종료 월 (없으면 현재)
        '1 month'::INTERVAL                   -- 1개월 간격
    )::DATE AS month
) AS month_series
WHERE p.start_date IS NOT NULL
ORDER BY p.name, month_series.month;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 5. ARRAY 타입 고급 연산                        ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ unnest(): 배열을 행으로 변환 ■■■
SELECT
    first_name, last_name,
    unnest(skills) AS skill     -- 배열의 각 요소를 별도 행으로
FROM employees;

-- ■■■ 배열 집계: array_agg() ■■■
-- 부서별 직원 이름을 배열로 집계
SELECT
    d.name AS department,
    array_agg(e.first_name || ' ' || e.last_name ORDER BY e.salary DESC) AS employees
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.name;

-- ■■■ 배열 연산자 ■■■
SELECT
    first_name, skills,
    -- 배열 길이
    array_length(skills, 1) AS skill_count,
    -- 배열에 특정 요소 포함 여부
    'Python' = ANY(skills) AS knows_python,
    -- 배열 요소 위치
    array_position(skills, 'Python') AS python_position
FROM employees;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 6. JSON/JSONB 고급 연산                        ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ JSONB 접근 연산자 ■■■
SELECT
    first_name,
    metadata,
    -- ->  : JSON 객체/배열 요소 (JSON 타입 반환)
    metadata -> 'level' AS level_json,
    -- ->> : 텍스트 값 추출 (TEXT 타입 반환)
    metadata ->> 'level' AS level_text,
    -- #>  : 경로로 접근 (JSON 타입 반환)
    metadata #> '{team}' AS team_json,
    -- #>> : 경로로 접근 (TEXT 타입 반환)
    metadata #>> '{team}' AS team_text
FROM employees;

-- ■■■ jsonb_each(): JSONB 키-값 쌍을 행으로 변환 ■■■
SELECT
    first_name,
    kv.key,           -- JSON 키
    kv.value          -- JSON 값 (JSONB 타입)
FROM employees,
     jsonb_each(metadata) AS kv;  -- 각 키-값 쌍이 별도 행

-- ■■■ jsonb_array_elements(): JSON 배열을 행으로 변환 ■■■
SELECT
    order_no,
    item ->> 'product' AS product,   -- 상품명 추출
    (item ->> 'qty')::INT AS qty,    -- 수량 추출 (INT 캐스팅)
    (item ->> 'price')::NUMERIC AS price  -- 가격 추출
FROM orders,
     jsonb_array_elements(items) AS item;  -- JSON 배열의 각 요소를 행으로

-- ■■■ jsonb_set(): JSONB 값 수정 ■■■
-- metadata에 'department' 키 추가 (원본 수정 안 함, SELECT만)
SELECT
    first_name,
    jsonb_set(
        metadata,                      -- 원본 JSONB
        '{department}',                -- 경로 (키 이름)
        '"Engineering"'::jsonb,        -- 새 값
        true                           -- true: 키가 없으면 생성
    ) AS updated_metadata
FROM employees
WHERE employee_no = 'EMP001';

-- ■■■ JSONB 집계: jsonb_agg(), jsonb_object_agg() ■■■
-- 부서별 직원 정보를 JSON 배열로 집계
SELECT
    d.name AS department,
    jsonb_agg(
        jsonb_build_object(        -- JSON 객체 생성
            'name', e.first_name || ' ' || e.last_name,
            'salary', e.salary,
            'level', e.metadata ->> 'level'
        )
        ORDER BY e.salary DESC
    ) AS employees_json
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.name;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 7. Full-Text Search (전문 검색)                ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- LIKE '%keyword%': 인덱스 사용 불가, 느림
-- 전문 검색: tsvector + tsquery → GIN 인덱스 사용, 빠름

-- ■■■ 전문 검색용 테이블 ■■■
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    content TEXT NOT NULL,
    -- tsvector: 검색용 토큰화된 텍스트 (자동 업데이트)
    search_vector TSVECTOR,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ■■■ 샘플 데이터 ■■■
INSERT INTO articles (title, content) VALUES
    ('PostgreSQL 성능 최적화', 'PostgreSQL 데이터베이스의 쿼리 성능을 최적화하는 방법을 알아봅니다. 인덱스, 실행 계획, 통계 분석 등을 다룹니다.'),
    ('Docker 컨테이너 가이드', 'Docker 컨테이너를 사용하여 애플리케이션을 패키징하고 배포하는 방법. Dockerfile, docker-compose, 네트워크 설정.'),
    ('Kubernetes 클러스터 구축', 'Kubernetes를 사용한 컨테이너 오케스트레이션. Pod, Service, Deployment, Ingress 설정 방법.')
ON CONFLICT DO NOTHING;

-- ■■■ tsvector 업데이트 (영문 검색) ■■■
UPDATE articles
SET search_vector = to_tsvector('english', title || ' ' || content);

-- ■■■ GIN 인덱스 생성 (전문 검색 성능 향상) ■■■
CREATE INDEX IF NOT EXISTS idx_articles_search ON articles USING GIN(search_vector);

-- ■■■ 전문 검색 실행 ■■■
-- to_tsquery: 검색 쿼리 생성
-- @@: tsvector와 tsquery 매칭 연산자
SELECT
    title,
    -- ts_rank: 검색 결과 관련성 점수
    ts_rank(search_vector, to_tsquery('english', 'PostgreSQL & performance')) AS rank,
    -- ts_headline: 검색어 하이라이팅
    ts_headline('english', content,
        to_tsquery('english', 'PostgreSQL & performance'),
        'StartSel=<<, StopSel=>>'  -- 하이라이트 태그
    ) AS highlighted
FROM articles
WHERE search_vector @@ to_tsquery('english', 'PostgreSQL | Docker')
ORDER BY rank DESC;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 8. 서브쿼리 유형                               ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ 스칼라 서브쿼리: 단일 값 반환 ■■■
-- 평균 급여보다 높은 직원 조회
SELECT first_name, last_name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);

-- ■■■ EXISTS 서브쿼리: 존재 여부 확인 ■■■
-- 프로젝트에 참여 중인 직원만 조회
SELECT first_name, last_name
FROM employees e
WHERE EXISTS (
    SELECT 1
    FROM employee_projects ep
    WHERE ep.employee_id = e.id  -- 상관 서브쿼리 (외부 테이블 참조)
);

-- ■■■ NOT EXISTS: 존재하지 않는 경우 ■■■
-- 프로젝트에 참여하지 않는 직원 조회
SELECT first_name, last_name
FROM employees e
WHERE NOT EXISTS (
    SELECT 1
    FROM employee_projects ep
    WHERE ep.employee_id = e.id
);

-- ■■■ IN 서브쿼리: 목록 포함 여부 ■■■
-- 활성 프로젝트에 참여 중인 직원
SELECT first_name, last_name
FROM employees
WHERE id IN (
    SELECT ep.employee_id
    FROM employee_projects ep
    JOIN projects p ON ep.project_id = p.id
    WHERE p.status = 'active'
);

-- ■■■ FROM 절 서브쿼리 (인라인 뷰) ■■■
SELECT
    department,
    avg_salary,
    CASE
        WHEN avg_salary >= 90000 THEN '높음'
        WHEN avg_salary >= 70000 THEN '보통'
        ELSE '낮음'
    END AS salary_level
FROM (
    SELECT
        d.name AS department,
        ROUND(AVG(e.salary), 2) AS avg_salary
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    GROUP BY d.name
) AS dept_avg;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 9. UPSERT (INSERT ON CONFLICT)                ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- UPSERT = INSERT + UPDATE
-- 레코드가 이미 존재하면 UPDATE, 없으면 INSERT

-- ■■■ ON CONFLICT DO UPDATE: 충돌 시 업데이트 ■■■
INSERT INTO departments (name, description)
VALUES ('Engineering', '소프트웨어 엔지니어링팀 (업데이트됨)')
-- ON CONFLICT: name 컬럼에서 충돌 발생 시
ON CONFLICT (name)
DO UPDATE SET
    description = EXCLUDED.description,    -- EXCLUDED: INSERT 하려던 값
    updated_at = NOW()                     -- 수정 시각 업데이트
RETURNING *;  -- 결과 행 반환 (INSERT 또는 UPDATE된 행)

-- ■■■ ON CONFLICT DO NOTHING: 충돌 시 무시 ■■■
INSERT INTO departments (name, description)
VALUES ('Engineering', '무시될 값')
ON CONFLICT (name) DO NOTHING;  -- 이미 있으면 아무것도 안 함

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 10. RETURNING 절                              ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- INSERT, UPDATE, DELETE 결과를 즉시 반환
-- 별도의 SELECT 없이 변경된 데이터 확인 가능

-- ■■■ INSERT + RETURNING ■■■
INSERT INTO departments (name, description)
VALUES ('Research', 'R&D 연구개발팀')
ON CONFLICT (name) DO NOTHING
RETURNING id, name, created_at;   -- 삽입된 행의 id, name, created_at 반환

-- ■■■ UPDATE + RETURNING ■■■
-- 급여 10% 인상 후 변경된 결과 반환
-- (예시로 SELECT만 표시, 실제 실행 시 주석 해제)
-- UPDATE employees
-- SET salary = salary * 1.10,
--     updated_at = NOW()
-- WHERE department_id = 1
-- RETURNING first_name, last_name, salary AS new_salary;

-- ■■■ DELETE + RETURNING ■■■
-- 삭제된 행 정보 반환 (예시)
-- DELETE FROM employee_projects
-- WHERE joined_at < '2024-01-01'
-- RETURNING employee_id, project_id;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 11. 고급 집계 및 GROUPING SETS                 ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ GROUPING SETS: 여러 그룹 기준을 한 번에 ■■■
SELECT
    d.name AS department,
    e.metadata ->> 'level' AS level,
    COUNT(*) AS emp_count,
    ROUND(AVG(e.salary), 2) AS avg_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
-- GROUPING SETS: 여러 GROUP BY를 UNION ALL 하는 것과 같음
GROUP BY GROUPING SETS (
    (d.name, e.metadata ->> 'level'),   -- 부서+레벨별
    (d.name),                            -- 부서별 소계
    (e.metadata ->> 'level'),            -- 레벨별 소계
    ()                                    -- 전체 합계
)
ORDER BY department NULLS LAST, level NULLS LAST;

-- ■■■ ROLLUP: 계층적 소계 (상위 그룹부터) ■■■
-- ROLLUP(a, b) = GROUPING SETS ((a,b), (a), ())
SELECT
    d.name AS department,
    e.metadata ->> 'level' AS level,
    COUNT(*) AS emp_count,
    SUM(e.salary) AS total_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY ROLLUP (d.name, e.metadata ->> 'level')
ORDER BY department NULLS LAST;

-- ■■■ CUBE: 모든 조합의 소계 ■■■
-- CUBE(a, b) = GROUPING SETS ((a,b), (a), (b), ())
-- SELECT
--     d.name AS department,
--     e.is_active,
--     COUNT(*) AS emp_count
-- FROM employees e
-- JOIN departments d ON e.department_id = d.id
-- GROUP BY CUBE (d.name, e.is_active);

-- ■■■ FILTER: 조건부 집계 ■■■
SELECT
    d.name AS department,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE e.salary >= 80000) AS high_salary_count,
    COUNT(*) FILTER (WHERE e.salary < 80000) AS low_salary_count,
    ROUND(AVG(e.salary) FILTER (WHERE e.metadata ->> 'level' = 'senior'), 2) AS avg_senior_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.name;
