-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- SQL 학습 07단계: 저장 프로시저 (Stored Procedure)
-- 실행 방법: MySQL   →  mysql -u root -p < lesson.sql
--            (SQLite는 저장 프로시저를 지원하지 않으므로 MySQL/MariaDB 권장)
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- 저장 프로시저란?
-- 여러 SQL 문장을 하나의 "레시피 묶음"으로 저장하고,
-- 이름만 불러서 실행할 수 있게 하는 것입니다.
--
-- 비유: 학교 출석 관리에서
--   매일 "출석부 열기 → 이름 확인 → 결석자 표시 → 결석자 수 세기"를
--   선생님이 일일이 타이핑하는 대신,
--   "출석 체크 시작!"이라고 한 마디만 하면 다 되는 것!
-- ============================================================================

-- ┌─────────────────────────────────────────────┐
-- │  준비: 학교 출석 시스템 테이블                │
-- └─────────────────────────────────────────────┘

DROP TABLE IF EXISTS attendance_log;
DROP TABLE IF EXISTS students;

CREATE TABLE students (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(50)  NOT NULL,
    class_name  VARCHAR(20)  NOT NULL,
    status      VARCHAR(20)  DEFAULT '재학'    -- '재학', '휴학', '전학'
);

CREATE TABLE attendance_log (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    student_id  INT NOT NULL,
    attend_date DATE NOT NULL,
    attend_type VARCHAR(10) NOT NULL,  -- '출석', '지각', '결석', '조퇴'
    memo        VARCHAR(200),
    FOREIGN KEY (student_id) REFERENCES students(id)
);

INSERT INTO students (name, class_name) VALUES
    ('민수', '1반'), ('지우', '1반'), ('서연', '1반'),
    ('하준', '2반'), ('유나', '2반'), ('도윤', '2반');


-- ┌─────────────────────────────────────────────┐
-- │  레슨 1: 기본 프로시저 — 매개변수 없는 버전   │
-- └─────────────────────────────────────────────┘
-- DELIMITER를 바꾸는 이유:
-- 프로시저 안에 ;이 여러 개 있는데, MySQL이 중간에 끊지 않게
-- "프로시저가 끝나는 표시"를 // 로 바꿔 주는 것입니다.
-- ═══════════════════════════════════════════════

DELIMITER //

CREATE PROCEDURE sp_show_all_students()
BEGIN
    -- 재학 중인 학생만 반별로 보여 줍니다.
    SELECT id, name, class_name
    FROM students
    WHERE status = '재학'
    ORDER BY class_name, name;
END //

DELIMITER ;

-- 실행 방법: 이름만 부르면 됩니다!
CALL sp_show_all_students();


-- ┌─────────────────────────────────────────────┐
-- │  레슨 2: IN 매개변수 — 값을 받아서 사용       │
-- └─────────────────────────────────────────────┘
-- IN 매개변수는 "바깥에서 프로시저 안으로 값을 넣어 주는 것"입니다.
-- 비유: 선생님이 "1반 출석 체크!"라고 할 때 "1반"이 매개변수예요.
-- ═══════════════════════════════════════════════

DELIMITER //

CREATE PROCEDURE sp_record_attendance(
    IN p_student_id  INT,          -- 학생 번호
    IN p_date        DATE,         -- 날짜
    IN p_type        VARCHAR(10),  -- '출석', '지각', '결석', '조퇴'
    IN p_memo        VARCHAR(200)  -- 메모 (선택)
)
BEGIN
    INSERT INTO attendance_log (student_id, attend_date, attend_type, memo)
    VALUES (p_student_id, p_date, p_type, p_memo);

    -- 기록 후 확인 메시지 출력
    SELECT CONCAT(p_student_id, '번 학생의 ', p_date, ' 출석이 [',
                  p_type, '](으)로 기록되었습니다.') AS result_message;
END //

DELIMITER ;

-- 민수(1번) 출석 기록
CALL sp_record_attendance(1, '2024-03-15', '출석', NULL);
CALL sp_record_attendance(2, '2024-03-15', '지각', '버스 늦음');
CALL sp_record_attendance(3, '2024-03-15', '결석', '감기');
CALL sp_record_attendance(1, '2024-03-16', '출석', NULL);
CALL sp_record_attendance(2, '2024-03-16', '출석', NULL);
CALL sp_record_attendance(3, '2024-03-16', '출석', NULL);


-- ┌─────────────────────────────────────────────┐
-- │  레슨 3: OUT 매개변수 — 결과를 밖으로 보내기  │
-- └─────────────────────────────────────────────┘
-- OUT 매개변수는 "프로시저가 계산한 결과를 바깥으로 돌려주는 것"입니다.
-- 비유: 선생님이 "오늘 결석자 몇 명이야?"라고 물으면
--       반장이 세어서 "3명이요!"라고 대답하는 것.
-- ═══════════════════════════════════════════════

DELIMITER //

CREATE PROCEDURE sp_count_absent(
    IN  p_date      DATE,
    IN  p_class     VARCHAR(20),
    OUT p_count     INT
)
BEGIN
    SELECT COUNT(*) INTO p_count
    FROM attendance_log al
    JOIN students s ON al.student_id = s.id
    WHERE al.attend_date = p_date
      AND al.attend_type = '결석'
      AND s.class_name = p_class;
END //

DELIMITER ;

-- 사용법: @변수에 결과를 받습니다
CALL sp_count_absent('2024-03-15', '1반', @absent_count);
SELECT @absent_count AS '1반_결석자_수';


-- ┌─────────────────────────────────────────────┐
-- │  레슨 4: IF / ELSE — 조건에 따라 다르게       │
-- └─────────────────────────────────────────────┘
-- 프로시저 안에서 조건 분기를 할 수 있습니다.
-- 비유: "결석이 3번 이상이면 경고, 5번 이상이면 학부모 연락"
-- ═══════════════════════════════════════════════

DELIMITER //

CREATE PROCEDURE sp_check_student_alert(
    IN p_student_id INT
)
BEGIN
    DECLARE v_absent_count INT DEFAULT 0;
    DECLARE v_name VARCHAR(50);

    -- 학생 이름 가져오기
    SELECT name INTO v_name FROM students WHERE id = p_student_id;

    -- 총 결석 횟수 세기
    SELECT COUNT(*) INTO v_absent_count
    FROM attendance_log
    WHERE student_id = p_student_id AND attend_type = '결석';

    -- 조건에 따라 다른 메시지
    IF v_absent_count >= 5 THEN
        SELECT CONCAT(v_name, ' 학생: 결석 ', v_absent_count,
                      '회 → ⚠ 학부모 연락 필요!') AS alert;
    ELSEIF v_absent_count >= 3 THEN
        SELECT CONCAT(v_name, ' 학생: 결석 ', v_absent_count,
                      '회 → 주의 경고') AS alert;
    ELSE
        SELECT CONCAT(v_name, ' 학생: 결석 ', v_absent_count,
                      '회 → 정상') AS alert;
    END IF;
END //

DELIMITER ;

CALL sp_check_student_alert(3);  -- 서연: 결석 1회 → 정상


-- ┌─────────────────────────────────────────────┐
-- │  레슨 5: WHILE 루프 — 반복 처리               │
-- └─────────────────────────────────────────────┘
-- 같은 작업을 여러 번 반복해야 할 때 WHILE을 씁니다.
-- 비유: "1번부터 6번까지 전부 출석으로 기록해"
-- ═══════════════════════════════════════════════

DELIMITER //

CREATE PROCEDURE sp_bulk_attendance(
    IN p_date  DATE,
    IN p_type  VARCHAR(10)
)
BEGIN
    DECLARE v_id INT DEFAULT 1;
    DECLARE v_max INT;

    -- 재학 중인 학생 수
    SELECT MAX(id) INTO v_max FROM students WHERE status = '재학';

    -- 루프: 1번부터 마지막 학생까지 반복
    WHILE v_id <= v_max DO
        -- 이미 기록이 없을 때만 추가 (중복 방지)
        IF NOT EXISTS (
            SELECT 1 FROM attendance_log
            WHERE student_id = v_id AND attend_date = p_date
        ) THEN
            INSERT INTO attendance_log (student_id, attend_date, attend_type, memo)
            VALUES (v_id, p_date, p_type, '일괄 등록');
        END IF;

        SET v_id = v_id + 1;
    END WHILE;

    SELECT CONCAT(p_date, ' 전체 학생 ', p_type, ' 일괄 기록 완료') AS result;
END //

DELIMITER ;

CALL sp_bulk_attendance('2024-03-17', '출석');
SELECT * FROM attendance_log WHERE attend_date = '2024-03-17';


-- ┌─────────────────────────────────────────────┐
-- │  레슨 6: CURSOR — 한 줄씩 꺼내서 처리        │
-- └─────────────────────────────────────────────┘
-- CURSOR는 결과를 한 줄씩 꺼내서 하나하나 처리하는 방법입니다.
-- 비유: 출석부에서 이름을 한 줄 읽고 → 확인하고 → 다음 줄 읽고 …
--       마치 손가락으로 한 줄씩 짚어가며 읽는 것.
-- ═══════════════════════════════════════════════

DELIMITER //

CREATE PROCEDURE sp_daily_report(
    IN p_date DATE
)
BEGIN
    DECLARE v_done      INT DEFAULT 0;
    DECLARE v_name      VARCHAR(50);
    DECLARE v_type      VARCHAR(10);

    -- 커서 선언: 해당 날짜의 출석 기록을 한 줄씩 읽을 준비
    DECLARE cur_attendance CURSOR FOR
        SELECT s.name, al.attend_type
        FROM attendance_log al
        JOIN students s ON al.student_id = s.id
        WHERE al.attend_date = p_date
        ORDER BY s.name;

    -- 더 읽을 줄이 없으면 v_done을 1로 바꿔서 루프 종료
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    -- 임시 테이블에 보고서 저장
    DROP TEMPORARY TABLE IF EXISTS tmp_report;
    CREATE TEMPORARY TABLE tmp_report (
        student_name VARCHAR(50),
        status       VARCHAR(10)
    );

    OPEN cur_attendance;

    read_loop: LOOP
        FETCH cur_attendance INTO v_name, v_type;
        IF v_done = 1 THEN
            LEAVE read_loop;
        END IF;

        INSERT INTO tmp_report VALUES (v_name, v_type);
    END LOOP;

    CLOSE cur_attendance;

    -- 보고서 출력
    SELECT * FROM tmp_report;
    DROP TEMPORARY TABLE tmp_report;
END //

DELIMITER ;

CALL sp_daily_report('2024-03-15');


-- ┌─────────────────────────────────────────────┐
-- │  레슨 7: 에러 처리 — 실패해도 안전하게        │
-- └─────────────────────────────────────────────┘
-- DECLARE HANDLER로 에러가 나도 프로시저가 멈추지 않게 합니다.
-- 비유: 선생님이 "틀려도 괜찮아, 다음 문제로 넘어가자" 하는 것.
-- ═══════════════════════════════════════════════

DELIMITER //

CREATE PROCEDURE sp_safe_transfer(
    IN p_from_id  INT,
    IN p_to_id    INT,
    IN p_date     DATE
)
BEGIN
    -- 에러가 나면 ROLLBACK
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT '오류 발생! 변경 사항을 되돌렸습니다.' AS error_message;
    END;

    START TRANSACTION;

    -- 전학 처리: 원래 반에서 기록 삭제, 새 반에 추가
    -- 존재하지 않는 학생이면 외래키 에러 발생 → HANDLER가 잡음
    UPDATE students SET status = '전학' WHERE id = p_from_id;

    INSERT INTO attendance_log (student_id, attend_date, attend_type, memo)
    VALUES (p_from_id, p_date, '조퇴', '전학으로 인한 조퇴 처리');

    COMMIT;
    SELECT CONCAT(p_from_id, '번 학생 전학 처리 완료') AS result;
END //

DELIMITER ;

-- 정상 실행
-- CALL sp_safe_transfer(6, 1, '2024-03-18');


-- ┌─────────────────────────────────────────────┐
-- │  레슨 8: 프로시저 관리 명령어                 │
-- └─────────────────────────────────────────────┘
-- ═══════════════════════════════════════════════

-- 프로시저 목록 보기
SHOW PROCEDURE STATUS WHERE Db = DATABASE();

-- 프로시저 내용 보기
-- SHOW CREATE PROCEDURE sp_show_all_students;

-- 프로시저 삭제
-- DROP PROCEDURE IF EXISTS sp_show_all_students;


-- ═══════════════════════════════════════════════
-- 정리 노트
-- ═══════════════════════════════════════════════
-- CREATE PROCEDURE : SQL 묶음을 이름 붙여 저장
-- IN 매개변수      : 바깥 → 안으로 값 전달
-- OUT 매개변수     : 안 → 바깥으로 결과 전달
-- DECLARE 변수     : 프로시저 안에서 쓸 임시 변수
-- IF / ELSEIF / ELSE : 조건 분기
-- WHILE / LOOP     : 반복 실행
-- CURSOR           : 결과를 한 줄씩 꺼내서 처리
-- HANDLER          : 에러 발생 시 안전하게 처리
-- ═══════════════════════════════════════════════
