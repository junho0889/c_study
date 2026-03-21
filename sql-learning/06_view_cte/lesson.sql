-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- SQL 학습 06단계: VIEW와 CTE (Common Table Expression)
-- 실행 방법: SQLite  →  sqlite3 < lesson.sql
--            MySQL   →  mysql -u root -p < lesson.sql
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- VIEW란?
-- 자주 쓰는 SELECT 질문을 "별명"으로 저장해 두는 것입니다.
-- 비유: 매번 "수학 90점 이상인 1반 학생 명단"을 타이핑하는 대신,
--       "우등생 목록"이라는 이름만 부르면 바로 나오게 하는 것!
--
-- CTE란?
-- 복잡한 쿼리를 쪼개서 "먼저 이걸 구하고 → 그 결과로 저걸 구하자"
-- 라고 단계적으로 쓸 수 있게 해 주는 임시 이름표입니다.
-- 비유: 수학 문제에서 "x = 3+2 라고 하자. 그러면 y = x × 4 이다" 처럼
--       중간 결과에 이름을 붙이는 것.
-- ============================================================================

-- ┌─────────────────────────────────────────────┐
-- │  준비: 가족·학생 테이블 만들기                │
-- └─────────────────────────────────────────────┘

DROP TABLE IF EXISTS student_scores;
DROP TABLE IF EXISTS family_tree;

CREATE TABLE student_scores (
    id         INTEGER PRIMARY KEY,
    name       TEXT    NOT NULL,
    class_name TEXT    NOT NULL,
    math       INTEGER NOT NULL,
    english    INTEGER NOT NULL,
    science    INTEGER NOT NULL
);

INSERT INTO student_scores (id, name, class_name, math, english, science) VALUES
    (1, '민수', '1반', 92, 88, 75),
    (2, '지우', '1반', 85, 95, 90),
    (3, '서연', '1반', 97, 90, 88),
    (4, '하준', '2반', 78, 82, 91),
    (5, '유나', '2반', 90, 82, 85),
    (6, '도윤', '2반', 65, 70, 72);


-- ┌─────────────────────────────────────────────┐
-- │  레슨 1: CREATE VIEW — 자주 쓰는 질문 저장   │
-- └─────────────────────────────────────────────┘
-- VIEW는 실제 데이터를 복사하지 않습니다.
-- "이 SELECT를 실행하라"는 레시피만 저장합니다.
-- 비유: 요리 레시피를 써 둔 것이지, 요리를 미리 해 둔 게 아닙니다.
-- ═══════════════════════════════════════════════

DROP VIEW IF EXISTS v_student_summary;

CREATE VIEW v_student_summary AS
SELECT
    name,
    class_name,
    math,
    english,
    science,
    (math + english + science)     AS total,
    ROUND((math + english + science) / 3.0, 1) AS average
FROM student_scores;

-- 이제 이름만 불러서 바로 쓸 수 있습니다!
SELECT * FROM v_student_summary ORDER BY average DESC;
-- VIEW를 마치 테이블처럼 사용할 수 있어요.


-- ┌─────────────────────────────────────────────┐
-- │  레슨 2: VIEW에 조건 걸기                    │
-- └─────────────────────────────────────────────┘
-- VIEW도 WHERE, ORDER BY를 붙일 수 있습니다.
-- ═══════════════════════════════════════════════

-- 평균 85점 이상인 우등생만 보기
SELECT name, class_name, average
FROM v_student_summary
WHERE average >= 85
ORDER BY average DESC;

-- 반별 평균도 VIEW 위에서 GROUP BY 가능!
SELECT class_name, ROUND(AVG(average), 1) AS class_average
FROM v_student_summary
GROUP BY class_name;


-- ┌─────────────────────────────────────────────┐
-- │  레슨 3: VIEW의 장점과 주의점                 │
-- └─────────────────────────────────────────────┘
-- 장점:
--   1) 복잡한 쿼리를 간단한 이름으로 부를 수 있음
--   2) 같은 쿼리를 여러 곳에서 재사용
--   3) 민감한 칸(비밀번호 등)을 숨기고 필요한 칸만 보여줄 수 있음
--
-- 주의점:
--   1) VIEW는 레시피일 뿐, 매번 실행됩니다 (느려질 수 있음)
--   2) 대부분의 VIEW에 INSERT/UPDATE는 불가능
-- ═══════════════════════════════════════════════

-- 비밀번호를 숨기는 VIEW 예시
DROP TABLE IF EXISTS user_accounts;
CREATE TABLE user_accounts (
    id       INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,  -- 이 칸은 숨기고 싶다!
    email    TEXT NOT NULL
);

INSERT INTO user_accounts VALUES (1, '민수', 'secret123', 'minsu@test.com');
INSERT INTO user_accounts VALUES (2, '지우', 'pass456',   'jiwoo@test.com');

DROP VIEW IF EXISTS v_user_public;
CREATE VIEW v_user_public AS
SELECT id, username, email FROM user_accounts;
-- 비밀번호 칸이 없으니 안전하게 보여줄 수 있습니다.

SELECT * FROM v_user_public;


-- ┌─────────────────────────────────────────────┐
-- │  레슨 4: WITH (CTE) — 중간 결과에 이름 붙이기│
-- └─────────────────────────────────────────────┘
-- CTE는 "이 쿼리 안에서만 쓰는 임시 이름표"입니다.
-- VIEW와 다르게 저장되지 않고, 이 쿼리가 끝나면 사라집니다.
--
-- 비유: VIEW = 교실 벽에 붙여둔 공식 포스터 (계속 있음)
--       CTE  = 칠판에 잠깐 쓴 풀이 과정 (수업 끝나면 지움)
-- ═══════════════════════════════════════════════

-- "반별 평균 → 평균이 80 이상인 반만 보기"를 단계적으로
WITH class_averages AS (
    SELECT
        class_name,
        ROUND(AVG(math), 1)    AS avg_math,
        ROUND(AVG(english), 1) AS avg_eng,
        ROUND(AVG(science), 1) AS avg_sci
    FROM student_scores
    GROUP BY class_name
)
SELECT *
FROM class_averages
WHERE avg_math >= 80;


-- ┌─────────────────────────────────────────────┐
-- │  레슨 5: 여러 CTE 연결하기                   │
-- └─────────────────────────────────────────────┘
-- CTE를 쉼표로 이어서 여러 개 만들 수 있습니다.
-- 마치 수학 풀이를 "x = ..., y = ..., z = x + y" 처럼 쓰는 것.
-- ═══════════════════════════════════════════════

WITH
totals AS (
    SELECT
        name,
        class_name,
        (math + english + science) AS total_score
    FROM student_scores
),
class_max AS (
    SELECT
        class_name,
        MAX(total_score) AS best_score
    FROM totals
    GROUP BY class_name
)
SELECT t.name, t.class_name, t.total_score, cm.best_score,
       CASE WHEN t.total_score = cm.best_score THEN '★ 반 1등!'
            ELSE '' END AS badge
FROM totals t
JOIN class_max cm ON t.class_name = cm.class_name
ORDER BY t.class_name, t.total_score DESC;


-- ┌─────────────────────────────────────────────┐
-- │  레슨 6: 재귀 CTE — 가족 계보 따라가기       │
-- └─────────────────────────────────────────────┘
-- 재귀 CTE는 "자기 자신을 다시 부르는" CTE입니다.
-- 가족 나무(family tree)처럼 "부모 → 자식 → 손자"를
-- 끝까지 따라가야 할 때 아주 유용합니다.
--
-- 비유: 족보를 펼쳐 놓고 할아버지부터 시작해서
--       아버지, 나, 내 아이 순서로 줄줄이 따라가는 것.
-- ═══════════════════════════════════════════════

CREATE TABLE family_tree (
    id        INTEGER PRIMARY KEY,
    name      TEXT    NOT NULL,
    parent_id INTEGER,              -- 부모의 id (최상위 조상은 NULL)
    FOREIGN KEY (parent_id) REFERENCES family_tree(id)
);

INSERT INTO family_tree (id, name, parent_id) VALUES
    (1, '할아버지 영수', NULL),     -- 최상위 (부모 없음)
    (2, '아버지 철수',   1),        -- 영수의 아들
    (3, '삼촌 영호',     1),        -- 영수의 아들
    (4, '나 민수',       2),        -- 철수의 아들
    (5, '동생 지우',     2),        -- 철수의 아들
    (6, '사촌 하준',     3),        -- 영호의 아들
    (7, '내 아이 서연',  4);        -- 민수의 아이

-- 할아버지부터 시작해서 모든 후손을 세대별로 출력
WITH RECURSIVE descendants AS (
    -- 시작점 (anchor): 할아버지
    SELECT id, name, parent_id, 1 AS generation
    FROM family_tree
    WHERE parent_id IS NULL

    UNION ALL

    -- 반복 (recursive): 이전 세대의 자식을 찾기
    SELECT ft.id, ft.name, ft.parent_id, d.generation + 1
    FROM family_tree ft
    JOIN descendants d ON ft.parent_id = d.id
)
SELECT
    generation AS 세대,
    name AS 이름,
    CASE generation
        WHEN 1 THEN '──── (시작)'
        WHEN 2 THEN '  └── 2세대'
        WHEN 3 THEN '    └── 3세대'
        WHEN 4 THEN '      └── 4세대'
    END AS 트리
FROM descendants
ORDER BY generation, id;
-- 결과:
-- 1 할아버지 영수  ──── (시작)
-- 2 아버지 철수      └── 2세대
-- 2 삼촌 영호        └── 2세대
-- 3 나 민수            └── 3세대
-- 3 동생 지우          └── 3세대
-- 3 사촌 하준          └── 3세대
-- 4 내 아이 서연         └── 4세대


-- ┌─────────────────────────────────────────────┐
-- │  레슨 7: 재귀 CTE — 숫자 연속 생성           │
-- └─────────────────────────────────────────────┘
-- 재귀 CTE로 1부터 10까지 숫자를 만들 수도 있습니다.
-- 테스트 데이터를 만들 때 자주 쓰는 기법이에요.
-- ═══════════════════════════════════════════════

WITH RECURSIVE numbers AS (
    SELECT 1 AS n           -- 시작: 1
    UNION ALL
    SELECT n + 1 FROM numbers WHERE n < 10  -- 10까지 반복
)
SELECT n AS 숫자 FROM numbers;


-- ┌─────────────────────────────────────────────┐
-- │  레슨 8: Materialized View 개념              │
-- └─────────────────────────────────────────────┘
-- 일반 VIEW는 매번 쿼리를 실행합니다 (느릴 수 있음).
-- Materialized View는 결과를 실제 테이블처럼 "저장"해 둡니다.
--
-- 비유: 일반 VIEW = 주문할 때마다 요리하는 식당
--       Materialized View = 미리 만들어 놓은 도시락
--       (빠르지만, 메뉴가 바뀌면 다시 만들어야 함)
--
-- 주의: SQLite에는 Materialized View가 없습니다.
--       PostgreSQL에서는 이렇게 씁니다:
--
--   CREATE MATERIALIZED VIEW mv_summary AS
--   SELECT class_name, AVG(math) as avg_math
--   FROM student_scores GROUP BY class_name;
--
--   REFRESH MATERIALIZED VIEW mv_summary;
--
-- SQLite에서 비슷하게 흉내내려면 결과를 테이블에 저장합니다:
-- ═══════════════════════════════════════════════

DROP TABLE IF EXISTS cached_summary;

CREATE TABLE cached_summary AS
SELECT
    class_name,
    ROUND(AVG(math), 1)    AS avg_math,
    ROUND(AVG(english), 1) AS avg_eng,
    ROUND(AVG(science), 1) AS avg_sci
FROM student_scores
GROUP BY class_name;

SELECT * FROM cached_summary;
-- 빠르지만, student_scores가 바뀌면 이 테이블을 다시 만들어야 합니다.


-- ═══════════════════════════════════════════════
-- 정리 노트
-- ═══════════════════════════════════════════════
-- VIEW              : 자주 쓰는 SELECT에 이름 붙이기 (저장됨, 매번 실행)
-- CTE (WITH)        : 쿼리 안에서만 쓰는 임시 이름표 (안 저장됨)
-- 재귀 CTE          : 자기 자신을 반복 호출 (족보, 조직도, 숫자 생성)
-- Materialized View : 결과를 미리 저장 (빠르지만, 갱신 필요)
-- ═══════════════════════════════════════════════
