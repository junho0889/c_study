-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ PostgreSQL 함수 & 트리거                        ■■■
-- ■■■ PL/pgSQL, RETURNS TABLE, 감사 로그(Audit Log)   ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 1. 기본 함수 (SQL Functions)                   ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ 단순 SQL 함수: 급여 등급 계산 ■■■
-- SQL 함수: 순수 SQL 문으로 구성, 가장 간단한 형태
CREATE OR REPLACE FUNCTION get_salary_grade(salary_amount NUMERIC)
RETURNS TEXT                          -- 반환 타입: TEXT
LANGUAGE sql                          -- 언어: SQL
IMMUTABLE                             -- 불변: 같은 입력 → 항상 같은 출력 (캐시 가능)
AS $$
    -- CASE 표현식으로 급여 등급 분류
    SELECT CASE
        WHEN salary_amount >= 100000 THEN 'S등급 (임원급)'
        WHEN salary_amount >= 80000 THEN 'A등급 (시니어)'
        WHEN salary_amount >= 60000 THEN 'B등급 (미드)'
        WHEN salary_amount >= 40000 THEN 'C등급 (주니어)'
        ELSE 'D등급 (인턴)'
    END;
$$;

-- 함수 사용 예시
-- SELECT first_name, salary, get_salary_grade(salary) FROM employees;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 2. PL/pgSQL 함수 (절차적 함수)                 ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ 변수, 조건문, 반복문 사용 가능한 절차적 함수 ■■■
CREATE OR REPLACE FUNCTION calculate_bonus(
    emp_id UUID,             -- 직원 ID
    bonus_rate NUMERIC DEFAULT 0.10  -- 보너스 비율 (기본 10%)
)
RETURNS NUMERIC              -- 반환: 보너스 금액
LANGUAGE plpgsql              -- 언어: PL/pgSQL (절차적 확장)
STABLE                        -- 안정: 같은 트랜잭션 내에서 같은 결과
AS $$
DECLARE
    -- 변수 선언 블록
    emp_salary NUMERIC;       -- 직원 급여
    emp_level TEXT;            -- 직원 레벨
    final_bonus NUMERIC;      -- 최종 보너스
    years_worked INTEGER;     -- 근속 연수
BEGIN
    -- ■■■ SELECT INTO: 쿼리 결과를 변수에 저장 ■■■
    SELECT
        e.salary,
        e.metadata ->> 'level',
        EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.hire_date))
    INTO emp_salary, emp_level, years_worked
    FROM employees e
    WHERE e.id = emp_id;

    -- ■■■ 직원이 없는 경우 예외 처리 ■■■
    IF NOT FOUND THEN
        RAISE EXCEPTION '직원 ID %를 찾을 수 없습니다', emp_id;
    END IF;

    -- ■■■ 레벨별 보너스 비율 조정 ■■■
    IF emp_level = 'principal' THEN
        bonus_rate := bonus_rate * 2.0;       -- 프린시펄: 2배
    ELSIF emp_level = 'lead' THEN
        bonus_rate := bonus_rate * 1.5;       -- 리드: 1.5배
    ELSIF emp_level = 'senior' THEN
        bonus_rate := bonus_rate * 1.2;       -- 시니어: 1.2배
    END IF;

    -- ■■■ 근속 연수 보너스 추가 ■■■
    -- GREATEST: 둘 중 큰 값 (최소 0)
    bonus_rate := bonus_rate + GREATEST(years_worked * 0.01, 0);

    -- 최종 보너스 계산
    final_bonus := ROUND(emp_salary * bonus_rate, 2);

    -- ■■■ 디버깅용 로그 출력 ■■■
    RAISE NOTICE '직원 레벨: %, 근속: %년, 보너스율: %, 보너스: %',
        emp_level, years_worked, bonus_rate, final_bonus;

    RETURN final_bonus;          -- 결과 반환
END;
$$;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 3. RETURNS TABLE (테이블 반환 함수)            ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ 부서별 통계를 테이블로 반환하는 함수 ■■■
CREATE OR REPLACE FUNCTION get_department_stats(
    min_employees INTEGER DEFAULT 1    -- 최소 직원 수 필터
)
RETURNS TABLE (                        -- 반환 타입: 테이블 (여러 행, 여러 컬럼)
    department_name VARCHAR,
    employee_count BIGINT,
    avg_salary NUMERIC,
    min_salary NUMERIC,
    max_salary NUMERIC,
    total_salary NUMERIC
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    -- RETURN QUERY: 쿼리 결과를 테이블로 반환
    RETURN QUERY
    SELECT
        d.name,
        COUNT(*)::BIGINT,
        ROUND(AVG(e.salary), 2),
        MIN(e.salary),
        MAX(e.salary),
        SUM(e.salary)
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    WHERE e.is_active = TRUE
    GROUP BY d.name
    HAVING COUNT(*) >= min_employees
    ORDER BY AVG(e.salary) DESC;

    -- 결과가 없을 경우 로그 출력
    IF NOT FOUND THEN
        RAISE NOTICE '조건에 맞는 부서가 없습니다 (최소 직원 수: %)', min_employees;
    END IF;
END;
$$;

-- 사용 예시: 일반 테이블처럼 FROM 절에서 호출
-- SELECT * FROM get_department_stats(2);

-- ■■■ RETURNS SETOF: 기존 테이블 타입의 여러 행 반환 ■■■
CREATE OR REPLACE FUNCTION search_employees(
    search_term TEXT,                  -- 검색어
    dept_filter VARCHAR DEFAULT NULL   -- 부서 필터 (선택)
)
RETURNS SETOF employees                -- employees 테이블의 행 타입 반환
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    SELECT e.*
    FROM employees e
    LEFT JOIN departments d ON e.department_id = d.id
    WHERE
        -- ILIKE: 대소문자 무시 LIKE
        (e.first_name ILIKE '%' || search_term || '%'
         OR e.last_name ILIKE '%' || search_term || '%'
         OR e.email ILIKE '%' || search_term || '%')
        -- 부서 필터 (NULL이면 무시)
        AND (dept_filter IS NULL OR d.name = dept_filter)
    ORDER BY e.last_name;
END;
$$;

-- 사용: SELECT * FROM search_employees('김', 'Engineering');

-- ■■■ OUT 매개변수를 사용한 다중 값 반환 ■■■
CREATE OR REPLACE FUNCTION get_salary_statistics(
    dept_id INTEGER,
    OUT avg_sal NUMERIC,          -- OUT: 출력 매개변수
    OUT min_sal NUMERIC,
    OUT max_sal NUMERIC,
    OUT emp_count INTEGER
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    SELECT
        ROUND(AVG(salary), 2),
        MIN(salary),
        MAX(salary),
        COUNT(*)::INTEGER
    INTO avg_sal, min_sal, max_sal, emp_count
    FROM employees
    WHERE department_id = dept_id AND is_active = TRUE;
END;
$$;

-- 사용: SELECT * FROM get_salary_statistics(1);

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 4. 예외 처리 (Exception Handling)              ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

CREATE OR REPLACE FUNCTION safe_divide(
    numerator NUMERIC,
    denominator NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    -- ■■■ 사전 검증 ■■■
    IF denominator = 0 THEN
        RAISE WARNING '0으로 나눌 수 없습니다. NULL을 반환합니다.';
        RETURN NULL;
    END IF;

    RETURN ROUND(numerator / denominator, 4);

EXCEPTION
    -- ■■■ 예외 포착 ■■■
    WHEN numeric_value_out_of_range THEN
        RAISE WARNING '숫자 범위 초과: % / %', numerator, denominator;
        RETURN NULL;
    WHEN OTHERS THEN
        -- SQLSTATE: PostgreSQL 에러 코드
        -- SQLERRM: 에러 메시지
        RAISE WARNING '예상치 못한 오류 [%]: %', SQLSTATE, SQLERRM;
        RETURN NULL;
END;
$$;

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 5. 트리거 (Triggers)                           ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- 트리거: INSERT, UPDATE, DELETE 이벤트 발생 시 자동 실행되는 함수
-- BEFORE: 데이터 변경 전에 실행 (데이터 검증/수정)
-- AFTER: 데이터 변경 후에 실행 (로깅, 알림)
-- INSTEAD OF: 뷰에서 사용 (실제 테이블에 대한 동작 정의)

-- ■■■ updated_at 자동 갱신 트리거 함수 ■■■
-- 레코드가 UPDATE될 때마다 updated_at을 현재 시각으로 갱신
CREATE OR REPLACE FUNCTION update_modified_timestamp()
RETURNS TRIGGER                        -- 트리거 함수는 반드시 TRIGGER 반환
LANGUAGE plpgsql
AS $$
BEGIN
    -- NEW: UPDATE 후의 새 행 데이터
    -- OLD: UPDATE 전의 기존 행 데이터 (INSERT에서는 NULL)
    NEW.updated_at = NOW();            -- 수정 시각을 현재로 변경
    RETURN NEW;                        -- 수정된 행 반환 (BEFORE 트리거)
    -- RETURN NULL이면 해당 작업 취소
END;
$$;

-- ■■■ 트리거 등록 (employees 테이블) ■■■
-- DROP TRIGGER IF EXISTS: 기존 트리거 삭제 (재생성용)
DROP TRIGGER IF EXISTS trg_employees_updated ON employees;
CREATE TRIGGER trg_employees_updated
    BEFORE UPDATE                      -- UPDATE 전에 실행
    ON employees                       -- employees 테이블에 대해
    FOR EACH ROW                       -- 각 행마다 실행 (행 레벨 트리거)
    EXECUTE FUNCTION update_modified_timestamp();  -- 실행할 함수

-- departments 테이블에도 동일 트리거 적용
DROP TRIGGER IF EXISTS trg_departments_updated ON departments;
CREATE TRIGGER trg_departments_updated
    BEFORE UPDATE ON departments
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_timestamp();

-- ■■■ 데이터 검증 트리거 (BEFORE INSERT/UPDATE) ■■■
CREATE OR REPLACE FUNCTION validate_employee()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- ■■■ 이메일 형식 검증 ■■■
    IF NEW.email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' THEN
        RAISE EXCEPTION '유효하지 않은 이메일 형식: %', NEW.email;
    END IF;

    -- ■■■ 급여 범위 검증 ■■■
    IF NEW.salary IS NOT NULL AND (NEW.salary < 0 OR NEW.salary > 1000000) THEN
        RAISE EXCEPTION '급여는 0~1,000,000 범위여야 합니다: %', NEW.salary;
    END IF;

    -- ■■■ 이름 공백 제거 및 정규화 ■■■
    NEW.first_name = TRIM(NEW.first_name);
    NEW.last_name = TRIM(NEW.last_name);

    -- ■■■ employee_no 자동 생성 (INSERT 시만) ■■■
    IF TG_OP = 'INSERT' AND NEW.employee_no IS NULL THEN
        NEW.employee_no = 'EMP' || LPAD(
            nextval('employees_employee_no_seq')::TEXT,  -- 시퀀스 다음 값
            6,                                           -- 6자리
            '0'                                          -- 앞을 0으로 채움
        );
    END IF;

    RETURN NEW;
END;
$$;

-- ■■■ 검증 트리거 등록 ■■■
DROP TRIGGER IF EXISTS trg_validate_employee ON employees;
CREATE TRIGGER trg_validate_employee
    BEFORE INSERT OR UPDATE            -- INSERT, UPDATE 모두에서 실행
    ON employees
    FOR EACH ROW
    EXECUTE FUNCTION validate_employee();

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 6. 감사 로그 (Audit Log) 구현                  ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- 모든 데이터 변경사항을 기록하는 감사 로그 시스템

-- ■■■ 감사 로그 테이블 ■■■
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,     -- 변경된 테이블 이름
    operation VARCHAR(10) NOT NULL,       -- 작업 종류 (INSERT, UPDATE, DELETE)
    record_id TEXT,                        -- 변경된 레코드 ID
    old_data JSONB,                        -- 변경 전 데이터 (UPDATE, DELETE)
    new_data JSONB,                        -- 변경 후 데이터 (INSERT, UPDATE)
    changed_fields TEXT[],                 -- 변경된 필드 목록 (UPDATE만)
    performed_by TEXT DEFAULT current_user, -- 변경한 사용자
    performed_at TIMESTAMPTZ DEFAULT NOW(),-- 변경 시각
    client_ip INET DEFAULT inet_client_addr(), -- 클라이언트 IP
    application_name TEXT DEFAULT current_setting('application_name')  -- 앱 이름
);

-- ■■■ 감사 로그 인덱스 ■■■
CREATE INDEX IF NOT EXISTS idx_audit_table_time
    ON audit_log (table_name, performed_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_record
    ON audit_log (table_name, record_id);

-- ■■■ 범용 감사 트리거 함수 ■■■
-- 어떤 테이블에든 적용 가능한 범용 감사 로그 함수
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER                       -- 함수 소유자 권한으로 실행 (보안)
AS $$
DECLARE
    old_json JSONB;                    -- 이전 데이터 JSON
    new_json JSONB;                    -- 새 데이터 JSON
    record_id_val TEXT;                -- 레코드 ID 값
    changed TEXT[];                    -- 변경된 필드 목록
    key_name TEXT;                     -- JSON 키 이름
BEGIN
    -- ■■■ 작업별 데이터 변환 ■■■
    IF TG_OP = 'DELETE' THEN
        -- DELETE: OLD만 있음
        old_json := to_jsonb(OLD);
        record_id_val := OLD.id::TEXT;
    ELSIF TG_OP = 'INSERT' THEN
        -- INSERT: NEW만 있음
        new_json := to_jsonb(NEW);
        record_id_val := NEW.id::TEXT;
    ELSIF TG_OP = 'UPDATE' THEN
        -- UPDATE: OLD, NEW 모두 있음
        old_json := to_jsonb(OLD);
        new_json := to_jsonb(NEW);
        record_id_val := NEW.id::TEXT;

        -- ■■■ 변경된 필드 감지 ■■■
        -- old_json과 new_json을 비교하여 변경된 키 찾기
        FOR key_name IN SELECT jsonb_object_keys(new_json)
        LOOP
            IF old_json -> key_name IS DISTINCT FROM new_json -> key_name THEN
                changed := array_append(changed, key_name);
            END IF;
        END LOOP;
    END IF;

    -- ■■■ 감사 로그 삽입 ■■■
    INSERT INTO audit_log (table_name, operation, record_id, old_data, new_data, changed_fields)
    VALUES (
        TG_TABLE_NAME,          -- 트리거가 걸린 테이블 이름 (자동)
        TG_OP,                  -- 작업 종류 (INSERT/UPDATE/DELETE, 자동)
        record_id_val,
        old_json,
        new_json,
        changed
    );

    -- ■■■ 반환 값 ■■■
    -- AFTER 트리거에서는 반환값이 무시되지만, 명시적으로 반환
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$;

-- ■■■ 감사 트리거 등록 (employees 테이블) ■■■
DROP TRIGGER IF EXISTS trg_audit_employees ON employees;
CREATE TRIGGER trg_audit_employees
    AFTER INSERT OR UPDATE OR DELETE   -- 변경 후에 실행
    ON employees
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

-- ■■■ 감사 트리거 등록 (departments 테이블) ■■■
DROP TRIGGER IF EXISTS trg_audit_departments ON departments;
CREATE TRIGGER trg_audit_departments
    AFTER INSERT OR UPDATE OR DELETE
    ON departments
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 7. 감사 로그 조회 함수                          ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ 특정 레코드의 변경 이력 조회 ■■■
CREATE OR REPLACE FUNCTION get_audit_history(
    p_table_name VARCHAR,              -- 테이블 이름
    p_record_id TEXT,                  -- 레코드 ID
    p_limit INTEGER DEFAULT 50        -- 최대 조회 건수
)
RETURNS TABLE (
    operation VARCHAR,
    changed_fields TEXT[],
    old_data JSONB,
    new_data JSONB,
    performed_by TEXT,
    performed_at TIMESTAMPTZ
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    SELECT
        al.operation,
        al.changed_fields,
        al.old_data,
        al.new_data,
        al.performed_by,
        al.performed_at
    FROM audit_log al
    WHERE al.table_name = p_table_name
      AND al.record_id = p_record_id
    ORDER BY al.performed_at DESC
    LIMIT p_limit;
END;
$$;

-- ■■■ 감사 로그 통계 함수 ■■■
CREATE OR REPLACE FUNCTION get_audit_summary(
    p_since TIMESTAMPTZ DEFAULT NOW() - INTERVAL '7 days'
)
RETURNS TABLE (
    table_name VARCHAR,
    inserts BIGINT,
    updates BIGINT,
    deletes BIGINT,
    total BIGINT
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    SELECT
        al.table_name,
        COUNT(*) FILTER (WHERE al.operation = 'INSERT'),
        COUNT(*) FILTER (WHERE al.operation = 'UPDATE'),
        COUNT(*) FILTER (WHERE al.operation = 'DELETE'),
        COUNT(*)
    FROM audit_log al
    WHERE al.performed_at >= p_since
    GROUP BY al.table_name
    ORDER BY COUNT(*) DESC;
END;
$$;

-- 사용: SELECT * FROM get_audit_summary(NOW() - INTERVAL '30 days');

-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■■■ 8. 유틸리티 함수                                ■■■
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- ■■■ 한국식 이름 포맷 (성 + 이름) ■■■
CREATE OR REPLACE FUNCTION format_korean_name(
    last_name TEXT,
    first_name TEXT
)
RETURNS TEXT
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT last_name || first_name;    -- 한국어: 성 + 이름 (공백 없음)
$$;

-- ■■■ 날짜 차이를 한국어로 표현 ■■■
CREATE OR REPLACE FUNCTION date_diff_korean(
    start_date DATE,
    end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TEXT
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    diff INTERVAL;
    years INT;
    months INT;
    days INT;
BEGIN
    diff := AGE(end_date, start_date);
    years := EXTRACT(YEAR FROM diff);
    months := EXTRACT(MONTH FROM diff);
    days := EXTRACT(DAY FROM diff);

    RETURN CONCAT_WS(' ',
        CASE WHEN years > 0 THEN years || '년' END,
        CASE WHEN months > 0 THEN months || '개월' END,
        CASE WHEN days > 0 THEN days || '일' END
    );
END;
$$;

-- 사용:
-- SELECT
--     format_korean_name(last_name, first_name) AS full_name,
--     hire_date,
--     date_diff_korean(hire_date) AS 근속기간
-- FROM employees;
