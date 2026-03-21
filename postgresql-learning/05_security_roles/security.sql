-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ PostgreSQL 보안 & 역할 관리                     ■■■
-- ■■■ ROLE, GRANT/REVOKE, Row Level Security (RLS)    ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 1. 역할(ROLE) 생성 및 관리                     ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- PostgreSQL에서는 USER와 ROLE이 같은 개념
-- CREATE USER = CREATE ROLE + LOGIN 권한
-- ROLE은 그룹 역할(그룹)과 로그인 역할(사용자) 두 가지로 사용

-- ■■■ 그룹 역할 생성 (로그인 불가, 권한 그룹) ■■■
-- NOLOGIN: 직접 로그인 불가 (권한 그룹으로만 사용)

-- 읽기 전용 그룹
CREATE ROLE readonly_group NOLOGIN;
-- 읽기/쓰기 그룹
CREATE ROLE readwrite_group NOLOGIN;
-- 관리자 그룹
CREATE ROLE admin_group NOLOGIN;
-- 애플리케이션 그룹
CREATE ROLE app_group NOLOGIN;

-- ■■■ 로그인 역할(사용자) 생성 ■■■
-- LOGIN: 로그인 가능
-- PASSWORD: 비밀번호 설정
-- VALID UNTIL: 비밀번호 만료일
-- CONNECTION LIMIT: 최대 동시 연결 수

-- 읽기 전용 사용자 (분석/리포팅용)
CREATE ROLE analyst LOGIN
    PASSWORD 'analyst_secure_pw_2025!'     -- 강력한 비밀번호 (프로덕션에서는 더 복잡하게)
    VALID UNTIL '2027-12-31'               -- 비밀번호 유효기간
    CONNECTION LIMIT 5                      -- 최대 5개 동시 연결
    IN ROLE readonly_group;                -- readonly_group에 소속

-- 개발자 사용자
CREATE ROLE developer LOGIN
    PASSWORD 'developer_secure_pw_2025!'
    CONNECTION LIMIT 10
    IN ROLE readwrite_group;

-- DBA 사용자
CREATE ROLE dba_user LOGIN
    PASSWORD 'dba_super_secure_2025!'
    CREATEDB                                -- 데이터베이스 생성 권한
    CREATEROLE                              -- 역할 생성 권한
    IN ROLE admin_group;

-- 앱 서비스 계정
CREATE ROLE app_service LOGIN
    PASSWORD 'app_service_pw_2025!'
    CONNECTION LIMIT 50                     -- 앱은 많은 연결 필요
    IN ROLE app_group;

-- ■■■ 역할 속성 변경 ■■■
-- ALTER ROLE: 기존 역할의 속성 변경
-- ALTER ROLE analyst PASSWORD 'new_password';       -- 비밀번호 변경
-- ALTER ROLE analyst VALID UNTIL '2028-12-31';     -- 유효기간 연장
-- ALTER ROLE analyst CONNECTION LIMIT 10;           -- 연결 제한 변경

-- ■■■ 역할 확인 ■■■
-- SELECT rolname, rolsuper, rolcreatedb, rolcreaterole, rolcanlogin
-- FROM pg_roles
-- WHERE rolname NOT LIKE 'pg_%'
-- ORDER BY rolname;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 2. 권한 부여 (GRANT)                           ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ 데이터베이스 레벨 권한 ■■■
-- CONNECT: 데이터베이스에 연결 권한
GRANT CONNECT ON DATABASE study_db TO readonly_group;
GRANT CONNECT ON DATABASE study_db TO readwrite_group;
GRANT CONNECT ON DATABASE study_db TO admin_group;
GRANT CONNECT ON DATABASE study_db TO app_group;

-- ■■■ 스키마 레벨 권한 ■■■
-- USAGE: 스키마 내 객체에 접근할 권한
-- CREATE: 스키마 내 새 객체 생성 권한
GRANT USAGE ON SCHEMA public TO readonly_group;
GRANT USAGE, CREATE ON SCHEMA public TO readwrite_group;
GRANT ALL ON SCHEMA public TO admin_group;
GRANT USAGE ON SCHEMA public TO app_group;

-- ■■■ 테이블 레벨 권한 ■■■

-- 읽기 전용: SELECT만 허용
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_group;

-- 읽기/쓰기: SELECT + INSERT + UPDATE + DELETE
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO readwrite_group;

-- 관리자: 모든 권한
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin_group;

-- 앱 서비스: SELECT, INSERT, UPDATE만 (DELETE 불가)
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_group;

-- ■■■ 시퀀스 권한 (SERIAL/BIGSERIAL 사용 시 필요) ■■■
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO readwrite_group;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_group;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO admin_group;

-- ■■■ 기본 권한 설정 (향후 생성될 테이블에 자동 적용) ■■■
-- ALTER DEFAULT PRIVILEGES: 앞으로 생성되는 객체에 자동으로 권한 부여
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO readonly_group;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO readwrite_group;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE ON SEQUENCES TO readwrite_group;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE ON TABLES TO app_group;

-- ■■■ 특정 컬럼 권한 (세밀한 제어) ■■■
-- 급여 컬럼은 분석가에게 숨기기
-- REVOKE SELECT ON employees FROM readonly_group;
-- GRANT SELECT (id, employee_no, first_name, last_name, email, department_id, hire_date, is_active)
--     ON employees TO readonly_group;
-- → salary, metadata 등은 조회 불가

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 3. 권한 회수 (REVOKE)                          ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ 특정 권한 회수 ■■■
-- app_group에서 DELETE 권한 명시적 회수
REVOKE DELETE ON ALL TABLES IN SCHEMA public FROM app_group;

-- ■■■ 특정 테이블의 권한 회수 ■■■
-- audit_log 테이블에 대한 수정 권한 회수 (로그는 읽기만)
REVOKE INSERT, UPDATE, DELETE ON audit_log FROM readwrite_group;
REVOKE INSERT, UPDATE, DELETE ON audit_log FROM app_group;

-- ■■■ public 역할의 기본 권한 제거 (보안 강화) ■■■
-- PostgreSQL은 기본적으로 public 역할에 많은 권한 부여
-- 프로덕션에서는 반드시 제거해야 함
REVOKE ALL ON SCHEMA public FROM PUBLIC;            -- 스키마 접근 제거
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC;  -- 테이블 접근 제거
-- 이후 명시적으로 필요한 역할에만 GRANT

-- public 스키마 사용 권한 재부여 (위에서 제거했으므로)
GRANT USAGE ON SCHEMA public TO readonly_group, readwrite_group, admin_group, app_group;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 4. Row Level Security (RLS)                    ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- RLS: 행 단위 접근 제어
-- 사용자마다 볼 수 있는 행을 제한
-- 멀티테넌트 애플리케이션에서 필수!

-- ■■■ RLS 테스트용 테이블 생성 ■■■
CREATE TABLE IF NOT EXISTS customer_data (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    -- owner: 데이터 소유자 (역할 이름)
    owner_role VARCHAR(100) NOT NULL DEFAULT current_user,
    -- department: 부서 접근 제어용
    department VARCHAR(50),
    sensitive_data TEXT,          -- 민감 정보 (제한적 접근)
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 테스트 데이터 삽입
INSERT INTO customer_data (customer_name, email, owner_role, department, sensitive_data) VALUES
    ('고객A', 'a@test.com', 'developer', 'Engineering', '민감정보A'),
    ('고객B', 'b@test.com', 'developer', 'Engineering', '민감정보B'),
    ('고객C', 'c@test.com', 'analyst', 'Marketing', '민감정보C'),
    ('고객D', 'd@test.com', 'app_service', 'Sales', '민감정보D'),
    ('고객E', 'e@test.com', 'app_service', 'Sales', '민감정보E')
ON CONFLICT DO NOTHING;

-- ■■■ RLS 활성화 ■■■
-- ALTER TABLE ... ENABLE ROW LEVEL SECURITY
ALTER TABLE customer_data ENABLE ROW LEVEL SECURITY;

-- ■■■ RLS 강제 적용 (테이블 소유자에게도) ■■■
-- FORCE: 테이블 소유자(보통 superuser)에게도 RLS 적용
-- 기본적으로 테이블 소유자는 RLS를 우회함
ALTER TABLE customer_data FORCE ROW LEVEL SECURITY;

-- ■■■ RLS 정책 생성 ■■■

-- 정책 1: 자신의 데이터만 조회 가능
CREATE POLICY owner_select_policy ON customer_data
    FOR SELECT                          -- SELECT 쿼리에 적용
    TO readwrite_group, app_group       -- 적용 대상 역할
    USING (owner_role = current_user);  -- 조건: owner_role이 현재 사용자와 일치

-- 정책 2: 관리자는 모든 데이터 조회 가능
CREATE POLICY admin_all_policy ON customer_data
    FOR ALL                             -- 모든 작업 (SELECT, INSERT, UPDATE, DELETE)
    TO admin_group                      -- 관리자 그룹에게
    USING (true)                        -- 조건: 항상 참 (모든 행 접근)
    WITH CHECK (true);                  -- INSERT/UPDATE 시에도 제한 없음

-- 정책 3: 분석가는 민감 정보 제외 조회 (뷰 활용)
CREATE POLICY analyst_select_policy ON customer_data
    FOR SELECT
    TO readonly_group
    USING (true);                       -- 모든 행 접근 가능 (단, 컬럼 권한으로 민감 정보 제한)

-- 정책 4: 앱 서비스는 자신이 생성한 데이터만 수정 가능
CREATE POLICY app_update_policy ON customer_data
    FOR UPDATE
    TO app_group
    USING (owner_role = current_user)   -- 자신의 데이터만 수정
    WITH CHECK (owner_role = current_user);  -- 수정 후에도 owner_role 유지

-- 정책 5: 앱 서비스의 INSERT 정책
CREATE POLICY app_insert_policy ON customer_data
    FOR INSERT
    TO app_group
    WITH CHECK (owner_role = current_user);  -- 자신의 이름으로만 삽입 가능

-- ■■■ RLS 정책 확인 ■■■
-- SELECT * FROM pg_policies WHERE tablename = 'customer_data';

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 5. pg_hba.conf 설정 가이드                     ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- pg_hba.conf: Host-Based Authentication (호스트 기반 인증)
-- 클라이언트 연결 시 인증 방법을 결정하는 파일
-- 파일 위치: /var/lib/postgresql/data/pgdata/pg_hba.conf
--
-- 형식:
-- TYPE  DATABASE  USER  ADDRESS      METHOD
--
-- ┌──────────┬────────────────────────────────────────────────┐
-- │ TYPE     │ 연결 유형                                      │
-- ├──────────┼────────────────────────────────────────────────┤
-- │ local    │ Unix 소켓 연결 (같은 서버)                      │
-- │ host     │ TCP/IP 연결 (SSL 여부 무관)                     │
-- │ hostssl  │ SSL 필수 TCP/IP 연결                            │
-- │ hostnossl│ SSL 없는 TCP/IP 연결만                          │
-- └──────────┴────────────────────────────────────────────────┘
--
-- ┌──────────────┬────────────────────────────────────────────┐
-- │ METHOD       │ 인증 방법                                  │
-- ├──────────────┼────────────────────────────────────────────┤
-- │ trust        │ 무조건 허용 (비밀번호 불필요, 개발용)         │
-- │ reject       │ 무조건 거부                                 │
-- │ scram-sha-256│ SCRAM-SHA-256 비밀번호 인증 (권장!)          │
-- │ md5          │ MD5 비밀번호 인증 (레거시, 보안 취약)         │
-- │ password     │ 평문 비밀번호 (절대 사용 금지!)               │
-- │ peer         │ OS 사용자 이름으로 인증 (local 전용)          │
-- │ cert         │ SSL 클라이언트 인증서로 인증                  │
-- │ ldap         │ LDAP 서버로 인증                             │
-- └──────────────┴────────────────────────────────────────────┘
--
-- 예시 pg_hba.conf 설정:
-- # TYPE  DATABASE    USER          ADDRESS         METHOD
-- local   all         all                           peer
-- host    all         all           127.0.0.1/32    scram-sha-256
-- host    all         all           ::1/128         scram-sha-256
-- host    study_db    app_service   172.16.0.0/12   scram-sha-256
-- hostssl all         dba_user      0.0.0.0/0       scram-sha-256
-- host    all         all           0.0.0.0/0       reject

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 6. SSL 접속 설정                                ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- PostgreSQL에서 SSL 활성화:
-- 1. postgresql.conf에서 ssl = on 설정
-- 2. 서버 인증서와 키 파일 배치:
--    - ssl_cert_file = 'server.crt'     (서버 인증서)
--    - ssl_key_file = 'server.key'      (개인 키)
--    - ssl_ca_file = 'root.crt'         (CA 인증서, 클라이언트 인증 시)
-- 3. pg_hba.conf에서 hostssl 사용

-- ■■■ SSL 상태 확인 쿼리 ■■■
-- 현재 연결의 SSL 상태 확인
-- SELECT
--     ssl,                  -- SSL 사용 여부
--     version,              -- TLS 버전 (TLSv1.2, TLSv1.3)
--     cipher,               -- 암호화 알고리즘
--     bits,                 -- 키 길이
--     client_dn             -- 클라이언트 인증서 DN
-- FROM pg_stat_ssl
-- JOIN pg_stat_activity ON pg_stat_ssl.pid = pg_stat_activity.pid
-- WHERE pg_stat_activity.pid = pg_backend_pid();

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 7. 보안 모범 사례                               ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ 권한 확인 쿼리 ■■■
-- 특정 테이블의 권한 확인
SELECT
    grantee,                           -- 권한 부여 대상
    table_name,                        -- 테이블 이름
    privilege_type,                    -- 권한 종류
    is_grantable                       -- GRANT OPTION 여부 (다른 사람에게 권한 위임 가능)
FROM information_schema.table_privileges
WHERE table_schema = 'public'
  AND table_name = 'employees'
ORDER BY grantee, privilege_type;

-- ■■■ 역할 멤버십 확인 ■■■
SELECT
    r.rolname AS role,                  -- 역할 이름
    m.rolname AS member,               -- 소속 멤버
    a.admin_option                     -- 관리자 옵션 여부
FROM pg_auth_members am
JOIN pg_roles r ON am.roleid = r.oid
JOIN pg_roles m ON am.member = m.oid
LEFT JOIN LATERAL (SELECT am.admin_option) a ON true
ORDER BY r.rolname, m.rolname;

-- ■■■ 현재 활성 세션 확인 ■■■
SELECT
    pid,                               -- 프로세스 ID
    usename,                           -- 사용자 이름
    client_addr,                       -- 클라이언트 IP
    application_name,                  -- 앱 이름
    state,                             -- 상태 (active, idle, idle in transaction)
    query_start,                       -- 쿼리 시작 시각
    LEFT(query, 80) AS current_query   -- 현재 쿼리 (80자까지)
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;

-- ■■■ 비밀번호 만료 확인 ■■■
SELECT
    rolname,
    rolvaliduntil AS password_expires,
    CASE
        WHEN rolvaliduntil IS NULL THEN '만료일 없음'
        WHEN rolvaliduntil < NOW() THEN '만료됨!'
        WHEN rolvaliduntil < NOW() + INTERVAL '30 days' THEN '곧 만료'
        ELSE '정상'
    END AS status
FROM pg_roles
WHERE rolcanlogin = true
ORDER BY rolvaliduntil NULLS LAST;
