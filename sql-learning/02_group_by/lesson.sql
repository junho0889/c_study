-- ============================================================================
-- SQL 학습 02단계: GROUP BY
-- 같은 종류끼리 묶어서 개수, 합계, 평균을 구하는 연습입니다.
-- 장난감을 색깔별로 한 상자씩 나눠 담은 뒤 상자마다 몇 개 있는지 세는 느낌입니다.
-- ============================================================================

DROP TABLE IF EXISTS snack_sales;

CREATE TABLE snack_sales (
    day_name TEXT,
    item_name TEXT,
    amount INTEGER
);

INSERT INTO snack_sales (day_name, item_name, amount) VALUES
    ('월요일', '우유', 1200),
    ('월요일', '우유', 1200),
    ('월요일', '빵', 1800),
    ('화요일', '우유', 1200),
    ('화요일', '사과', 900),
    ('수요일', '빵', 1800);

-- 레슨 1: 간식 종류별 판매 횟수와 총액
SELECT item_name, COUNT(*) AS sale_count, SUM(amount) AS total_amount
FROM snack_sales
GROUP BY item_name
ORDER BY total_amount DESC;

-- 레슨 2: 요일별 평균 금액
SELECT day_name, AVG(amount) AS average_amount
FROM snack_sales
GROUP BY day_name
ORDER BY day_name;

-- 레슨 3: 합계가 2500원 이상인 간식만 보기
-- HAVING은 GROUP BY로 묶인 "상자 결과"를 다시 거르는 역할입니다.
SELECT item_name, SUM(amount) AS total_amount
FROM snack_sales
GROUP BY item_name
HAVING SUM(amount) >= 2500
ORDER BY total_amount DESC;
