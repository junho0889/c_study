-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- SQL 학습 04단계: 윈도우 함수 (Window Functions)
-- 실행 방법: SQLite  →  sqlite3 < lesson.sql
--            MySQL   →  mysql -u root -p < lesson.sql
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- 윈도우 함수란?
-- GROUP BY는 여러 줄을 "하나로 뭉개서" 결과를 줍니다.
-- 윈도우 함수는 원래 줄을 그대로 두면서, 옆에 순위·합계 같은 값을 붙여 줍니다.
-- 비유: 시험지를 걷어서 평균만 알려 주는 게 GROUP BY,
--       시험지를 돌려주면서 "너는 반에서 3등이야"라고 옆에 적어 주는 게 윈도우 함수.
-- ============================================================================

-- ┌─────────────────────────────────────────────┐
-- │  준비: 학생 성적 테이블 만들기               │
-- └─────────────────────────────────────────────┘

DROP TABLE IF EXISTS exam_scores;

CREATE TABLE exam_scores (
    id          INTEGER PRIMARY KEY,
    class_name  TEXT    NOT NULL,   -- 반 이름 (예: '1반', '2반')
    student     TEXT    NOT NULL,   -- 학생 이름
    subject     TEXT    NOT NULL,   -- 과목
    score       INTEGER NOT NULL    -- 점수
);

INSERT INTO exam_scores (id, class_name, student, subject, score) VALUES
    (1,  '1반', '민수', '수학', 92),
    (2,  '1반', '지우', '수학', 85),
    (3,  '1반', '서연', '수학', 97),
    (4,  '1반', '하준', '수학', 85),
    (5,  '2반', '유나', '수학', 90),
    (6,  '2반', '도윤', '수학', 78),
    (7,  '2반', '소율', '수학', 95),
    (8,  '2반', '시우', '수학', 88),
    (9,  '1반', '민수', '영어', 88),
    (10, '1반', '지우', '영어', 95),
    (11, '1반', '서연', '영어', 90),
    (12, '2반', '유나', '영어', 82),
    (13, '2반', '도윤', '영어', 91),
    (14, '2반', '소율', '영어', 87);


-- ┌─────────────────────────────────────────────┐
-- │  레슨 1: ROW_NUMBER — 줄 번호 매기기         │
-- └─────────────────────────────────────────────┘
-- ROW_NUMBER()는 정렬 순서대로 1, 2, 3, … 번호를 붙입니다.
-- 같은 점수여도 반드시 다른 번호를 줍니다. (출석부 번호처럼)
-- ═══════════════════════════════════════════════

SELECT
    class_name,
    student,
    score,
    ROW_NUMBER() OVER (
        PARTITION BY class_name       -- 반별로 따로 번호를 매겨요
        ORDER BY score DESC           -- 점수 높은 순
    ) AS row_num
FROM exam_scores
WHERE subject = '수학';
-- 결과: 1반에서 서연(97)=1, 민수(92)=2, 지우(85)=3, 하준(85)=4
--       2반에서 소율(95)=1, 유나(90)=2, ...
-- 지우와 하준은 같은 85점이지만 번호가 다릅니다!


-- ┌─────────────────────────────────────────────┐
-- │  레슨 2: RANK vs DENSE_RANK — 공동 순위      │
-- └─────────────────────────────────────────────┘
-- RANK()   : 공동 2등이면 다음은 4등 (3등을 건너뜀)
-- DENSE_RANK(): 공동 2등이어도 다음은 3등 (빈틈 없이)
--
-- 비유: 달리기 대회에서 두 명이 동시에 들어오면
--   RANK  → "2등, 2등, 4등" (3등이 사라짐)
--   DENSE → "2등, 2등, 3등" (차곡차곡)
-- ═══════════════════════════════════════════════

SELECT
    class_name,
    student,
    score,
    RANK()       OVER (PARTITION BY class_name ORDER BY score DESC) AS rank_num,
    DENSE_RANK() OVER (PARTITION BY class_name ORDER BY score DESC) AS dense_rank_num
FROM exam_scores
WHERE subject = '수학';
-- 1반: 서연 97→1/1, 민수 92→2/2, 지우 85→3/3, 하준 85→3/3
-- 지우와 하준이 공동 3등일 때:
--   RANK 다음 → 5등 (만약 더 있다면)
--   DENSE_RANK 다음 → 4등


-- ┌─────────────────────────────────────────────┐
-- │  레슨 3: NTILE — N등분 나누기                │
-- └─────────────────────────────────────────────┘
-- NTILE(4)는 학생들을 점수 순서로 4그룹으로 나눕니다.
-- 비유: 체육 시간에 "키 순서대로 4팀으로 나눠라!" 하는 것과 같아요.
-- ═══════════════════════════════════════════════

SELECT
    student,
    score,
    NTILE(2) OVER (ORDER BY score DESC) AS team_of_2,
    NTILE(4) OVER (ORDER BY score DESC) AS team_of_4
FROM exam_scores
WHERE subject = '수학';
-- 8명을 2팀으로 나누면: 상위 4명 = 1팀, 하위 4명 = 2팀
-- 8명을 4팀으로 나누면: 상위 2명 = 1팀, 다음 2명 = 2팀 …


-- ┌─────────────────────────────────────────────┐
-- │  레슨 4: LAG / LEAD — 이전·다음 행 엿보기    │
-- └─────────────────────────────────────────────┘
-- LAG(값, 1)  = 바로 윗줄의 값 (이전 학생의 점수)
-- LEAD(값, 1) = 바로 아랫줄의 값 (다음 학생의 점수)
--
-- 비유: 시험 결과를 점수 순서로 늘어놓고,
--       "바로 앞 사람과 몇 점 차이 나?"를 보는 느낌입니다.
-- ═══════════════════════════════════════════════

SELECT
    student,
    score,
    LAG(score, 1)  OVER (ORDER BY score DESC) AS prev_score,
    LEAD(score, 1) OVER (ORDER BY score DESC) AS next_score,
    score - LAG(score, 1) OVER (ORDER BY score DESC) AS diff_from_prev
FROM exam_scores
WHERE subject = '수학';
-- 1등(97점)의 prev_score는 NULL (앞에 아무도 없으니까)
-- 2등(95점)의 prev_score는 97, diff_from_prev = 95-97 = -2


-- ┌─────────────────────────────────────────────┐
-- │  레슨 5: 윈도우 프레임 (ROWS BETWEEN)        │
-- └─────────────────────────────────────────────┘
-- OVER() 안에서 "어디서부터 어디까지 볼 건지" 범위를 정합니다.
-- ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
--   → 현재 행 + 바로 위 1줄 + 바로 아래 1줄 = 3줄 범위
--
-- 비유: 롤러코스터 줄에서 "내 앞 1명, 나, 내 뒤 1명"만 보는 느낌.
-- ═══════════════════════════════════════════════

SELECT
    student,
    score,
    -- 현재 행까지의 누적 합계 (처음부터 여기까지)
    SUM(score) OVER (
        ORDER BY score DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total,

    -- 앞뒤 1명을 포함한 이동 평균 (3명 평균)
    ROUND(AVG(score * 1.0) OVER (
        ORDER BY score DESC
        ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
    ), 1) AS moving_avg_3
FROM exam_scores
WHERE subject = '수학';


-- ┌─────────────────────────────────────────────┐
-- │  레슨 6: 반별 과목 평균과 본인 점수 비교      │
-- └─────────────────────────────────────────────┘
-- GROUP BY 없이도 반 평균을 옆에 붙일 수 있습니다!
-- ═══════════════════════════════════════════════

SELECT
    class_name,
    student,
    subject,
    score,
    ROUND(AVG(score * 1.0) OVER (PARTITION BY class_name, subject), 1) AS class_avg,
    score - ROUND(AVG(score * 1.0) OVER (PARTITION BY class_name, subject), 1) AS diff_from_avg
FROM exam_scores
ORDER BY class_name, subject, score DESC;
-- 민수 수학 92점, 1반 수학 평균 89.8 → 차이 +2.2
-- 이렇게 하면 "나는 반 평균보다 몇 점 높은지"를 한 눈에 볼 수 있어요.


-- ┌─────────────────────────────────────────────┐
-- │  레슨 7: 종합 응용 — 과목별 1등 뽑기          │
-- └─────────────────────────────────────────────┘
-- 윈도우 함수를 서브쿼리와 합치면 "각 과목 1등만 보기" 같은 걸 쉽게 합니다.
-- ═══════════════════════════════════════════════

SELECT *
FROM (
    SELECT
        subject,
        student,
        score,
        RANK() OVER (PARTITION BY subject ORDER BY score DESC) AS subject_rank
    FROM exam_scores
) ranked
WHERE subject_rank = 1;
-- 수학 1등: 서연(97), 영어 1등: 지우(95)


-- ═══════════════════════════════════════════════
-- 정리 노트
-- ═══════════════════════════════════════════════
-- ROW_NUMBER : 겹치지 않는 일련번호
-- RANK       : 공동 순위 있음, 다음 번호 건너뜀
-- DENSE_RANK : 공동 순위 있음, 다음 번호 안 건너뜀
-- NTILE(n)   : n개 그룹으로 균등 분배
-- LAG / LEAD : 이전 / 다음 행 값 가져오기
-- ROWS BETWEEN : 윈도우 프레임 범위 지정
-- PARTITION BY : GROUP BY처럼 그룹을 나누되 행을 합치지 않음
-- ═══════════════════════════════════════════════
