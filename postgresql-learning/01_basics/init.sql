-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ PostgreSQL 기초 학습 - 초기화 SQL                ■■■
-- ■■■ 테이블 생성, 데이터 타입, INSERT, SELECT 등      ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ PostgreSQL 데이터 타입 총정리 (주석 레퍼런스)  ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- ┌──────────────────┬──────────────────┬──────────────────────────────────┐
-- │ 카테고리          │ 타입              │ 설명                              │
-- ├──────────────────┼──────────────────┼──────────────────────────────────┤
-- │ 정수형            │ SMALLINT (INT2)   │ 2바이트, -32768 ~ 32767           │
-- │                  │ INTEGER (INT4)    │ 4바이트, -2^31 ~ 2^31-1          │
-- │                  │ BIGINT (INT8)     │ 8바이트, -2^63 ~ 2^63-1          │
-- │                  │ SERIAL            │ 자동 증가 INTEGER (시퀀스 생성)    │
-- │                  │ BIGSERIAL         │ 자동 증가 BIGINT                  │
-- ├──────────────────┼──────────────────┼──────────────────────────────────┤
-- │ 실수형            │ REAL (FLOAT4)     │ 4바이트, 6자리 정밀도              │
-- │                  │ DOUBLE PRECISION  │ 8바이트, 15자리 정밀도             │
-- │                  │ NUMERIC(p,s)      │ 정확한 소수, p: 전체자릿수, s: 소수 │
-- │                  │ MONEY             │ 통화 타입 (로케일 의존)             │
-- ├──────────────────┼──────────────────┼──────────────────────────────────┤
-- │ 문자형            │ CHAR(n)           │ 고정 길이 문자열 (n자, 공백 패딩)   │
-- │                  │ VARCHAR(n)        │ 가변 길이 문자열 (최대 n자)         │
-- │                  │ TEXT              │ 무제한 길이 문자열                  │
-- ├──────────────────┼──────────────────┼──────────────────────────────────┤
-- │ 날짜/시간         │ DATE              │ 날짜만 (2026-03-21)               │
-- │                  │ TIME              │ 시간만 (14:30:00)                 │
-- │                  │ TIMESTAMP         │ 날짜+시간 (타임존 없음)            │
-- │                  │ TIMESTAMPTZ       │ 날짜+시간+타임존 (권장!)           │
-- │                  │ INTERVAL          │ 시간 간격 (1 year 2 months)       │
-- ├──────────────────┼──────────────────┼──────────────────────────────────┤
-- │ 불리언            │ BOOLEAN           │ TRUE / FALSE / NULL               │
-- ├──────────────────┼──────────────────┼──────────────────────────────────┤
-- │ 바이너리          │ BYTEA             │ 바이너리 데이터 (이미지, 파일 등)   │
-- ├──────────────────┼──────────────────┼──────────────────────────────────┤
-- │ UUID             │ UUID              │ 범용 고유 식별자 (128비트)          │
-- ├──────────────────┼──────────────────┼──────────────────────────────────┤
-- │ JSON             │ JSON              │ JSON 텍스트 (매번 파싱)            │
-- │                  │ JSONB             │ JSON 바이너리 (인덱싱 가능, 권장!) │
-- ├──────────────────┼──────────────────┼──────────────────────────────────┤
-- │ 배열              │ 타입[]            │ 1차원/다차원 배열 (INTEGER[] 등)   │
-- ├──────────────────┼──────────────────┼──────────────────────────────────┤
-- │ 네트워크          │ INET              │ IPv4/IPv6 주소                    │
-- │                  │ CIDR              │ IPv4/IPv6 네트워크                │
-- │                  │ MACADDR           │ MAC 주소                         │
-- ├──────────────────┼──────────────────┼──────────────────────────────────┤
-- │ 기하학            │ POINT             │ 2D 좌표 (x, y)                   │
-- │                  │ LINE              │ 무한 직선                         │
-- │                  │ BOX               │ 직사각형                          │
-- │                  │ CIRCLE            │ 원                               │
-- ├──────────────────┼──────────────────┼──────────────────────────────────┤
-- │ 전문 검색          │ TSVECTOR          │ 검색용 토큰화된 텍스트             │
-- │                  │ TSQUERY           │ 검색 쿼리                         │
-- ├──────────────────┼──────────────────┼──────────────────────────────────┤
-- │ 범위형            │ INT4RANGE         │ INTEGER 범위 ([1, 10))           │
-- │                  │ TSRANGE           │ TIMESTAMP 범위                    │
-- │                  │ DATERANGE         │ DATE 범위                         │
-- └──────────────────┴──────────────────┴──────────────────────────────────┘

-- ■■■ 확장 설치 ■■■
-- uuid-ossp: UUID 생성 함수 제공
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- pgcrypto: 암호화 함수 제공 (gen_random_uuid 포함)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 테이블 생성 (CREATE TABLE)                     ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ 부서 테이블 ■■■
CREATE TABLE departments (
    -- SERIAL: 자동 증가 정수 (INSERT 시 값 지정 불필요)
    id SERIAL PRIMARY KEY,
    -- VARCHAR(100): 최대 100자 가변 문자열
    name VARCHAR(100) NOT NULL UNIQUE,     -- 부서명 (중복 불가)
    -- TEXT: 길이 제한 없는 문자열
    description TEXT,                       -- 부서 설명
    -- TIMESTAMPTZ: 타임존 포함 날짜/시간 (NOW()는 현재 시간)
    created_at TIMESTAMPTZ DEFAULT NOW(),  -- 생성 시각 (기본값: 현재)
    updated_at TIMESTAMPTZ DEFAULT NOW()   -- 수정 시각
);

-- ■■■ 직원 테이블 ■■■
CREATE TABLE employees (
    -- UUID: 범용 고유 식별자 (분산 시스템에서 유용)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- 직원 번호 (문자열, 고유)
    employee_no VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,        -- 이름
    last_name VARCHAR(50) NOT NULL,         -- 성
    email VARCHAR(255) NOT NULL UNIQUE,     -- 이메일 (고유 제약)
    -- NUMERIC(10,2): 전체 10자리, 소수 2자리 (정확한 금액 저장)
    salary NUMERIC(10, 2) CHECK (salary > 0),  -- 급여 (양수만 허용)
    -- REFERENCES: 외래 키 제약 (departments 테이블의 id 참조)
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    -- DATE: 날짜만 저장
    hire_date DATE NOT NULL DEFAULT CURRENT_DATE,  -- 입사일
    -- BOOLEAN: 참/거짓 값
    is_active BOOLEAN DEFAULT TRUE,         -- 재직 여부
    -- JSONB: JSON 바이너리 (인덱싱 가능, 유연한 데이터 저장)
    metadata JSONB DEFAULT '{}',            -- 추가 정보 (유연한 스키마)
    -- TEXT[]: 문자열 배열 (PostgreSQL 고유 기능)
    skills TEXT[] DEFAULT '{}',             -- 보유 기술 (배열)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ■■■ 프로젝트 테이블 ■■■
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    -- 상태를 CHECK 제약으로 제한 (유효한 값만 허용)
    status VARCHAR(20) DEFAULT 'planning'
        CHECK (status IN ('planning', 'active', 'completed', 'cancelled')),
    -- NUMERIC(12,2): 예산 (최대 9999999999.99)
    budget NUMERIC(12, 2),
    start_date DATE,
    end_date DATE,
    -- end_date는 start_date 이후여야 함 (테이블 레벨 CHECK)
    CONSTRAINT valid_dates CHECK (end_date IS NULL OR end_date >= start_date),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ■■■ 직원-프로젝트 다대다 관계 테이블 ■■■
-- 한 직원이 여러 프로젝트에, 한 프로젝트에 여러 직원이 참여 가능
CREATE TABLE employee_projects (
    employee_id UUID REFERENCES employees(id) ON DELETE CASCADE,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    -- 역할
    role VARCHAR(50) DEFAULT 'member',
    joined_at DATE DEFAULT CURRENT_DATE,
    -- 복합 기본 키: (employee_id, project_id) 조합이 유일해야 함
    PRIMARY KEY (employee_id, project_id)
);

-- ■■■ 주문 테이블 (다양한 데이터 타입 예시) ■■■
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,               -- BIGSERIAL: 큰 자동 증가 정수
    order_no VARCHAR(30) NOT NULL UNIQUE,
    customer_name VARCHAR(100) NOT NULL,
    -- INET: IP 주소 저장
    customer_ip INET,                        -- 고객 IP 주소
    -- MONEY: 통화 타입 (로케일에 따라 포맷 달라짐)
    total_amount NUMERIC(12, 2) NOT NULL,
    -- JSONB: 주문 항목을 JSON 배열로 저장
    items JSONB NOT NULL DEFAULT '[]',
    -- INT4RANGE: 정수 범위 (배송 예상 일수)
    delivery_days INT4RANGE,
    notes TEXT,
    ordered_at TIMESTAMPTZ DEFAULT NOW()
);

-- ■■■ 인덱스 생성 ■■■
-- B-tree 인덱스 (기본, 범위 검색에 효율적)
CREATE INDEX idx_employees_department ON employees(department_id);
-- 이메일 검색용 인덱스
CREATE INDEX idx_employees_email ON employees(email);
-- JSONB 인덱스 (GIN: Generalized Inverted Index)
CREATE INDEX idx_employees_metadata ON employees USING GIN(metadata);
-- 배열 인덱스 (GIN)
CREATE INDEX idx_employees_skills ON employees USING GIN(skills);
-- 부분 인덱스 (조건부 인덱스): 재직 중인 직원만 인덱싱
CREATE INDEX idx_active_employees ON employees(last_name, first_name)
    WHERE is_active = TRUE;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 데이터 삽입 (INSERT)                           ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ 부서 데이터 삽입 ■■■
INSERT INTO departments (name, description) VALUES
    ('Engineering', '소프트웨어 개발팀'),       -- id=1 (SERIAL 자동 생성)
    ('Marketing', '마케팅 및 홍보팀'),          -- id=2
    ('Sales', '영업 및 판매팀'),                -- id=3
    ('HR', '인사 관리팀'),                      -- id=4
    ('Finance', '재무 및 회계팀');              -- id=5

-- ■■■ 직원 데이터 삽입 ■■■
-- skills는 ARRAY 리터럴 사용, metadata는 JSONB
INSERT INTO employees (employee_no, first_name, last_name, email, salary, department_id, hire_date, skills, metadata) VALUES
    ('EMP001', '민수', '김', 'minsu.kim@company.com', 85000.00, 1, '2020-03-15',
     ARRAY['Python', 'PostgreSQL', 'Docker'],                  -- TEXT[] 배열 리터럴
     '{"level": "senior", "team": "backend"}'::jsonb),         -- JSONB 캐스팅
    ('EMP002', '지은', '이', 'jieun.lee@company.com', 72000.00, 1, '2021-07-01',
     ARRAY['JavaScript', 'React', 'Node.js'],
     '{"level": "mid", "team": "frontend"}'::jsonb),
    ('EMP003', '현우', '박', 'hyunwoo.park@company.com', 95000.00, 1, '2019-01-10',
     ARRAY['Python', 'Kubernetes', 'AWS'],
     '{"level": "lead", "team": "devops"}'::jsonb),
    ('EMP004', '수진', '최', 'sujin.choi@company.com', 68000.00, 2, '2022-02-20',
     ARRAY['SEO', 'Google Analytics', 'Content Marketing'],
     '{"level": "mid", "team": "digital"}'::jsonb),
    ('EMP005', '동현', '정', 'donghyun.jung@company.com', 78000.00, 3, '2020-11-05',
     ARRAY['Salesforce', 'HubSpot', 'Negotiation'],
     '{"level": "senior", "team": "enterprise"}'::jsonb),
    ('EMP006', '은지', '한', 'eunji.han@company.com', 62000.00, 4, '2023-01-15',
     ARRAY['Recruiting', 'HR Analytics'],
     '{"level": "junior", "team": "talent"}'::jsonb),
    ('EMP007', '재현', '윤', 'jaehyun.yoon@company.com', 110000.00, 1, '2018-06-01',
     ARRAY['System Design', 'Python', 'Go', 'PostgreSQL'],
     '{"level": "principal", "team": "architecture"}'::jsonb),
    ('EMP008', '하영', '송', 'hayoung.song@company.com', 55000.00, 5, '2023-09-01',
     ARRAY['Excel', 'SAP', 'Financial Analysis'],
     '{"level": "junior", "team": "accounting"}'::jsonb);

-- ■■■ 프로젝트 데이터 삽입 ■■■
INSERT INTO projects (name, description, status, budget, start_date, end_date) VALUES
    ('웹 리뉴얼', '회사 홈페이지 리뉴얼 프로젝트', 'active', 500000.00, '2025-01-01', '2025-06-30'),
    ('모바일 앱', '모바일 앱 개발 프로젝트', 'planning', 800000.00, '2025-04-01', NULL),
    ('데이터 파이프라인', '실시간 데이터 처리 파이프라인 구축', 'active', 300000.00, '2025-02-01', '2025-12-31'),
    ('CRM 시스템', '고객 관계 관리 시스템 도입', 'completed', 200000.00, '2024-01-01', '2024-12-31');

-- ■■■ 직원-프로젝트 매핑 ■■■
INSERT INTO employee_projects (employee_id, project_id, role) VALUES
    ((SELECT id FROM employees WHERE employee_no = 'EMP001'), 1, 'developer'),
    ((SELECT id FROM employees WHERE employee_no = 'EMP002'), 1, 'developer'),
    ((SELECT id FROM employees WHERE employee_no = 'EMP003'), 3, 'lead'),
    ((SELECT id FROM employees WHERE employee_no = 'EMP001'), 3, 'developer'),
    ((SELECT id FROM employees WHERE employee_no = 'EMP005'), 4, 'manager'),
    ((SELECT id FROM employees WHERE employee_no = 'EMP007'), 2, 'architect');

-- ■■■ 주문 데이터 삽입 ■■■
INSERT INTO orders (order_no, customer_name, customer_ip, total_amount, items, delivery_days) VALUES
    ('ORD-2025-001', '김철수', '192.168.1.100', 150000.00,
     '[{"product": "노트북 거치대", "qty": 1, "price": 50000}, {"product": "무선 마우스", "qty": 2, "price": 50000}]'::jsonb,
     '[3, 7)'::int4range),  -- 배송 3~6일 (7 미포함)
    ('ORD-2025-002', '이영희', '10.0.0.50', 89000.00,
     '[{"product": "기계식 키보드", "qty": 1, "price": 89000}]'::jsonb,
     '[1, 3)'::int4range);  -- 배송 1~2일

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 기본 SELECT 쿼리 예제                          ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ SELECT: 기본 조회 ■■■
-- 모든 직원 조회 (* 는 모든 컬럼)
-- SELECT * FROM employees;

-- ■■■ WHERE: 조건 필터링 ■■■
-- 급여가 70000 이상인 직원 조회
-- SELECT first_name, last_name, salary
-- FROM employees
-- WHERE salary >= 70000;

-- ■■■ AND / OR: 복합 조건 ■■■
-- Engineering 부서이면서 급여 80000 이상인 직원
-- SELECT e.first_name, e.last_name, e.salary, d.name AS department
-- FROM employees e
-- JOIN departments d ON e.department_id = d.id
-- WHERE d.name = 'Engineering' AND e.salary >= 80000;

-- ■■■ ORDER BY: 정렬 ■■■
-- 급여 내림차순 정렬 (DESC: 높은 순, ASC: 낮은 순)
-- SELECT first_name, last_name, salary
-- FROM employees
-- ORDER BY salary DESC;

-- ■■■ LIMIT / OFFSET: 페이지네이션 ■■■
-- 급여 상위 3명 조회
-- SELECT first_name, last_name, salary
-- FROM employees
-- ORDER BY salary DESC
-- LIMIT 3 OFFSET 0;  -- 첫 페이지 (0부터 3개)

-- ■■■ LIKE: 패턴 매칭 ■■■
-- %: 0개 이상의 문자, _: 정확히 1개 문자
-- 이메일에 'kim'이 포함된 직원
-- SELECT * FROM employees WHERE email LIKE '%kim%';

-- ■■■ IN: 목록 포함 여부 ■■■
-- Engineering 또는 Marketing 부서 직원
-- SELECT e.*, d.name AS dept_name
-- FROM employees e
-- JOIN departments d ON e.department_id = d.id
-- WHERE d.name IN ('Engineering', 'Marketing');

-- ■■■ BETWEEN: 범위 조건 ■■■
-- 급여가 60000~80000 사이인 직원
-- SELECT * FROM employees WHERE salary BETWEEN 60000 AND 80000;

-- ■■■ IS NULL / IS NOT NULL: NULL 체크 ■■■
-- department_id가 NULL이 아닌 직원
-- SELECT * FROM employees WHERE department_id IS NOT NULL;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ JOIN 예제                                      ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ INNER JOIN: 양쪽 테이블에 모두 일치하는 행만 ■■■
-- SELECT e.first_name, e.last_name, d.name AS department
-- FROM employees e
-- INNER JOIN departments d ON e.department_id = d.id;

-- ■■■ LEFT JOIN: 왼쪽 테이블의 모든 행 + 오른쪽 일치 행 ■■■
-- 부서가 없는 직원도 포함 (department는 NULL)
-- SELECT e.first_name, e.last_name, d.name AS department
-- FROM employees e
-- LEFT JOIN departments d ON e.department_id = d.id;

-- ■■■ RIGHT JOIN: 오른쪽 테이블의 모든 행 + 왼쪽 일치 행 ■■■
-- 직원이 없는 부서도 포함
-- SELECT d.name AS department, e.first_name, e.last_name
-- FROM employees e
-- RIGHT JOIN departments d ON e.department_id = d.id;

-- ■■■ FULL OUTER JOIN: 양쪽 테이블의 모든 행 ■■■
-- SELECT d.name AS department, e.first_name, e.last_name
-- FROM employees e
-- FULL OUTER JOIN departments d ON e.department_id = d.id;

-- ■■■ 다중 JOIN: 3개 이상 테이블 조인 ■■■
-- 직원, 부서, 프로젝트 정보를 함께 조회
-- SELECT
--     e.first_name || ' ' || e.last_name AS full_name,
--     d.name AS department,
--     p.name AS project,
--     ep.role
-- FROM employees e
-- JOIN departments d ON e.department_id = d.id
-- JOIN employee_projects ep ON e.id = ep.employee_id
-- JOIN projects p ON ep.project_id = p.id
-- ORDER BY e.last_name;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 집계 함수 (Aggregate Functions)                ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ COUNT, SUM, AVG, MIN, MAX ■■■
-- SELECT
--     COUNT(*) AS total_employees,          -- 총 직원 수
--     ROUND(AVG(salary), 2) AS avg_salary,  -- 평균 급여 (소수점 2자리)
--     MIN(salary) AS min_salary,             -- 최저 급여
--     MAX(salary) AS max_salary,             -- 최고 급여
--     SUM(salary) AS total_salary            -- 급여 합계
-- FROM employees
-- WHERE is_active = TRUE;

-- ■■■ GROUP BY + HAVING: 그룹별 집계 ■■■
-- 부서별 직원 수와 평균 급여 (직원 2명 이상인 부서만)
-- SELECT
--     d.name AS department,
--     COUNT(*) AS employee_count,
--     ROUND(AVG(e.salary), 2) AS avg_salary
-- FROM employees e
-- JOIN departments d ON e.department_id = d.id
-- GROUP BY d.name
-- HAVING COUNT(*) >= 2
-- ORDER BY avg_salary DESC;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ PostgreSQL 배열/JSON 연산자 예제               ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ 배열 연산자 ■■■
-- @>: 왼쪽 배열이 오른쪽 배열을 포함하는지 (contains)
-- Python 기술을 가진 직원
-- SELECT first_name, last_name, skills
-- FROM employees
-- WHERE skills @> ARRAY['Python'];

-- &&: 배열 간 교집합이 있는지 (overlaps)
-- Python 또는 JavaScript 기술을 가진 직원
-- SELECT first_name, last_name, skills
-- FROM employees
-- WHERE skills && ARRAY['Python', 'JavaScript'];

-- array_length: 배열 길이
-- SELECT first_name, array_length(skills, 1) AS skill_count
-- FROM employees
-- ORDER BY skill_count DESC;

-- ■■■ JSONB 연산자 ■■■
-- ->: JSON 키로 접근 (JSON 타입 반환)
-- ->>: JSON 키로 접근 (TEXT 타입 반환)
-- SELECT first_name, metadata->>'level' AS level, metadata->>'team' AS team
-- FROM employees;

-- @>: JSONB 포함 여부 확인
-- senior 레벨 직원 조회
-- SELECT first_name, last_name, metadata
-- FROM employees
-- WHERE metadata @> '{"level": "senior"}'::jsonb;

-- ■■■ 최종 확인 쿼리 ■■■
-- 초기화 데이터가 잘 들어갔는지 확인
SELECT '■■■ 초기화 완료! ■■■' AS message;
SELECT 'departments: ' || COUNT(*) || '건' AS result FROM departments
UNION ALL
SELECT 'employees: ' || COUNT(*) || '건' FROM employees
UNION ALL
SELECT 'projects: ' || COUNT(*) || '건' FROM projects
UNION ALL
SELECT 'employee_projects: ' || COUNT(*) || '건' FROM employee_projects
UNION ALL
SELECT 'orders: ' || COUNT(*) || '건' FROM orders;
