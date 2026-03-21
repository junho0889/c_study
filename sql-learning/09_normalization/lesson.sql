-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- SQL 학습 09단계: 정규화 (Normalization)
-- 실행 방법: SQLite  →  sqlite3 < lesson.sql
--            MySQL   →  mysql -u root -p < lesson.sql
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- 정규화란?
-- 테이블을 "깔끔하게 쪼개는 규칙"입니다.
-- 같은 정보를 여러 곳에 적어 두면, 하나만 고치고 다른 건 안 고쳐서
-- 데이터가 엉망이 됩니다. 이걸 막으려고 테이블을 나눕니다.
--
-- 비유: 반 친구 연락처를 종이 한 장에 몽땅 적으면
--       주소가 바뀔 때 모든 곳을 찾아 고쳐야 합니다.
--       하지만 "연락처 카드"를 따로 만들어 놓으면
--       카드 하나만 고치면 끝!
-- ============================================================================

-- ┌─────────────────────────────────────────────┐
-- │  레슨 1: 정규화 전 — 엉망진창 테이블          │
-- └─────────────────────────────────────────────┘
-- 하나의 테이블에 모든 걸 다 넣은 "나쁜 예"부터 봅시다.
-- ═══════════════════════════════════════════════

DROP TABLE IF EXISTS bad_orders;

CREATE TABLE bad_orders (
    order_id       INTEGER,
    order_date     TEXT,
    customer_name  TEXT,
    customer_phone TEXT,
    customer_addr  TEXT,
    item1_name     TEXT,    -- 상품1 이름
    item1_price    INTEGER, -- 상품1 가격
    item1_qty      INTEGER, -- 상품1 수량
    item2_name     TEXT,    -- 상품2 이름 (없으면 NULL)
    item2_price    INTEGER,
    item2_qty      INTEGER,
    item3_name     TEXT,    -- 상품3 이름 (없으면 NULL)
    item3_price    INTEGER,
    item3_qty      INTEGER
);

INSERT INTO bad_orders VALUES
    (1, '2024-03-15', '민수', '010-1111-2222', '서울시 강남구',
     '삼각김밥', 1200, 2,   '우유', 1500, 1,    NULL, NULL, NULL),
    (2, '2024-03-15', '민수', '010-1111-2222', '서울시 강남구',
     '컵라면', 1800, 1,     NULL, NULL, NULL,   NULL, NULL, NULL),
    (3, '2024-03-16', '지우', '010-3333-4444', '서울시 서초구',
     '삼각김밥', 1200, 3,   '초코우유', 1300, 2, '과자', 2000, 1);

-- 이 테이블의 문제점들:
--
-- 문제 1: 반복 (Redundancy)
--   민수의 전화번호와 주소가 주문마다 반복됩니다.
--   → 민수가 이사하면 모든 줄을 다 찾아서 고쳐야 해요!
--
-- 문제 2: 고정된 상품 칸 (item1, item2, item3)
--   상품이 4개면? 5개면? 칸이 모자랍니다!
--   상품이 1개면? 나머지 칸이 NULL로 낭비됩니다.
--
-- 문제 3: 상품 정보 중복
--   삼각김밥(1200원)이 여러 주문에 나옵니다.
--   → 가격이 바뀌면 모든 주문을 찾아 고쳐야 해요!

SELECT '❌ 나쁜 테이블 — 모든 게 한 덩어리' AS status;
SELECT * FROM bad_orders;


-- ┌─────────────────────────────────────────────┐
-- │  레슨 2: 제1정규형 (1NF) — 칸 하나에 값 하나  │
-- └─────────────────────────────────────────────┘
-- 1NF 규칙:
--   1) 모든 칸에 하나의 값만 (쉼표로 여러 개 넣지 말 것)
--   2) 반복되는 칸 그룹(item1, item2, item3)을 없앨 것
--   3) 각 행을 구분할 수 있는 기본키가 있을 것
--
-- 비유: "좋아하는 과일: 사과, 바나나, 딸기"를 한 칸에 넣지 말고
--       사과 한 줄, 바나나 한 줄, 딸기 한 줄로 나누는 것.
-- ═══════════════════════════════════════════════

DROP TABLE IF EXISTS orders_1nf;

-- item1/item2/item3을 없애고, 한 줄에 상품 하나씩!
CREATE TABLE orders_1nf (
    order_id       INTEGER,
    order_date     TEXT,
    customer_name  TEXT,
    customer_phone TEXT,
    customer_addr  TEXT,
    item_name      TEXT,
    item_price     INTEGER,
    item_qty       INTEGER,
    PRIMARY KEY (order_id, item_name)  -- 주문+상품으로 구분
);

INSERT INTO orders_1nf VALUES
    (1, '2024-03-15', '민수', '010-1111-2222', '서울시 강남구', '삼각김밥', 1200, 2),
    (1, '2024-03-15', '민수', '010-1111-2222', '서울시 강남구', '우유',     1500, 1),
    (2, '2024-03-15', '민수', '010-1111-2222', '서울시 강남구', '컵라면',   1800, 1),
    (3, '2024-03-16', '지우', '010-3333-4444', '서울시 서초구', '삼각김밥', 1200, 3),
    (3, '2024-03-16', '지우', '010-3333-4444', '서울시 서초구', '초코우유', 1300, 2),
    (3, '2024-03-16', '지우', '010-3333-4444', '서울시 서초구', '과자',     2000, 1);

SELECT '✅ 1NF 완료 — 한 칸에 한 값, 반복 칸 제거' AS status;
SELECT * FROM orders_1nf;

-- 개선된 점: item4, item5를 추가할 필요 없이 줄만 늘리면 됩니다!
-- 아직 남은 문제: 민수의 전화번호·주소가 여전히 반복!


-- ┌─────────────────────────────────────────────┐
-- │  레슨 3: 제2정규형 (2NF) — 부분 종속 제거     │
-- └─────────────────────────────────────────────┘
-- 2NF 규칙:
--   1NF를 만족하고,
--   기본키의 "일부분"에만 의존하는 칸을 다른 테이블로 분리합니다.
--
-- 현재 기본키 = (order_id, item_name)
-- customer_name, customer_phone은 order_id만으로 알 수 있음
--   → order_id "부분"에만 의존 → 분리해야 함!
--
-- 비유: 시험에서 (학번, 과목)이 기본키인데
--       "학생 이름"은 학번만 알면 알 수 있죠?
--       과목까지 알 필요 없으니 따로 빼는 거예요.
-- ═══════════════════════════════════════════════

DROP TABLE IF EXISTS orders_2nf;
DROP TABLE IF EXISTS order_items_2nf;

-- 주문 테이블 (고객 정보는 주문에)
CREATE TABLE orders_2nf (
    order_id       INTEGER PRIMARY KEY,
    order_date     TEXT,
    customer_name  TEXT,
    customer_phone TEXT,
    customer_addr  TEXT
);

-- 주문 상품 테이블 (상품 정보만)
CREATE TABLE order_items_2nf (
    order_id   INTEGER,
    item_name  TEXT,
    item_price INTEGER,
    item_qty   INTEGER,
    PRIMARY KEY (order_id, item_name),
    FOREIGN KEY (order_id) REFERENCES orders_2nf(order_id)
);

INSERT INTO orders_2nf VALUES
    (1, '2024-03-15', '민수', '010-1111-2222', '서울시 강남구'),
    (2, '2024-03-15', '민수', '010-1111-2222', '서울시 강남구'),
    (3, '2024-03-16', '지우', '010-3333-4444', '서울시 서초구');

INSERT INTO order_items_2nf VALUES
    (1, '삼각김밥', 1200, 2),
    (1, '우유',     1500, 1),
    (2, '컵라면',   1800, 1),
    (3, '삼각김밥', 1200, 3),
    (3, '초코우유', 1300, 2),
    (3, '과자',     2000, 1);

SELECT '✅ 2NF 완료 — 주문과 주문상품 분리' AS status;
SELECT * FROM orders_2nf;
SELECT * FROM order_items_2nf;

-- 개선된 점: 주문 상품 줄에서 고객 정보 반복이 사라졌습니다!
-- 아직 남은 문제: 민수의 정보가 주문 1, 2에 아직 반복!


-- ┌─────────────────────────────────────────────┐
-- │  레슨 4: 제3정규형 (3NF) — 이행 종속 제거     │
-- └─────────────────────────────────────────────┘
-- 3NF 규칙:
--   2NF를 만족하고,
--   기본키가 아닌 칸이 다른 기본키가 아닌 칸에 의존하면 분리합니다.
--
-- 현재: order_id → customer_name → customer_phone, customer_addr
--   customer_phone은 customer_name에 의존하지, order_id에 직접 의존하지 않음!
--   → 고객 테이블을 따로 만들어야 합니다.
--
-- 비유: 주문서에 "고객명: 민수, 전화: 010-…, 주소: 서울…"을 매번 적는 대신
--       "고객번호: 1"만 적고, 고객 정보는 고객 카드에서 보는 것.
-- ═══════════════════════════════════════════════

DROP TABLE IF EXISTS order_items_3nf;
DROP TABLE IF EXISTS orders_3nf;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS items;

-- 고객 테이블
CREATE TABLE customers (
    id    INTEGER PRIMARY KEY,
    name  TEXT NOT NULL,
    phone TEXT NOT NULL,
    addr  TEXT NOT NULL
);

-- 상품 마스터 테이블
CREATE TABLE items (
    id    INTEGER PRIMARY KEY,
    name  TEXT    NOT NULL,
    price INTEGER NOT NULL
);

-- 주문 테이블 (고객 번호만 참조)
CREATE TABLE orders_3nf (
    id          INTEGER PRIMARY KEY,
    order_date  TEXT    NOT NULL,
    customer_id INTEGER NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- 주문 상품 테이블 (상품 번호만 참조)
CREATE TABLE order_items_3nf (
    order_id INTEGER,
    item_id  INTEGER,
    qty      INTEGER NOT NULL,
    PRIMARY KEY (order_id, item_id),
    FOREIGN KEY (order_id) REFERENCES orders_3nf(id),
    FOREIGN KEY (item_id)  REFERENCES items(id)
);

INSERT INTO customers VALUES
    (1, '민수', '010-1111-2222', '서울시 강남구'),
    (2, '지우', '010-3333-4444', '서울시 서초구');

INSERT INTO items VALUES
    (1, '삼각김밥', 1200),
    (2, '우유',     1500),
    (3, '컵라면',   1800),
    (4, '초코우유', 1300),
    (5, '과자',     2000);

INSERT INTO orders_3nf VALUES
    (1, '2024-03-15', 1),   -- 민수의 주문
    (2, '2024-03-15', 1),   -- 민수의 주문
    (3, '2024-03-16', 2);   -- 지우의 주문

INSERT INTO order_items_3nf VALUES
    (1, 1, 2), (1, 2, 1),   -- 주문1: 삼각김밥2, 우유1
    (2, 3, 1),               -- 주문2: 컵라면1
    (3, 1, 3), (3, 4, 2), (3, 5, 1);  -- 주문3: 삼각김밥3, 초코우유2, 과자1

SELECT '✅ 3NF 완료 — 고객, 상품, 주문, 주문상품 분리' AS status;

-- 깔끔하게 JOIN으로 원래 정보를 볼 수 있습니다:
SELECT
    o.id AS 주문번호,
    o.order_date AS 날짜,
    c.name AS 고객명,
    i.name AS 상품명,
    i.price AS 단가,
    oi.qty AS 수량,
    i.price * oi.qty AS 소계
FROM orders_3nf o
JOIN customers c ON o.customer_id = c.id
JOIN order_items_3nf oi ON o.id = oi.order_id
JOIN items i ON oi.item_id = i.id
ORDER BY o.id, i.name;


-- ┌─────────────────────────────────────────────┐
-- │  레슨 5: 변환 전후 비교 — 민수가 이사했을 때  │
-- └─────────────────────────────────────────────┘
-- ═══════════════════════════════════════════════

-- ❌ 나쁜 테이블 (정규화 전): 주소가 3번 반복
--    → 3줄 모두 고쳐야 합니다. 하나라도 빼먹으면 엉망!
-- UPDATE bad_orders SET customer_addr = '서울시 송파구' WHERE customer_name = '민수';

-- ✅ 좋은 테이블 (3NF): 고객 테이블 1줄만 수정!
UPDATE customers SET addr = '서울시 송파구' WHERE name = '민수';

SELECT '✅ 민수 이사 후 — 1줄만 수정!' AS status;
SELECT * FROM customers;


-- ┌─────────────────────────────────────────────┐
-- │  레슨 6: 역정규화 (Denormalization)           │
-- └─────────────────────────────────────────────┘
-- 정규화를 "너무 많이" 하면, JOIN이 많아져서 느려질 수 있습니다.
-- 그래서 일부러 "정보를 합치는" 역정규화를 하기도 합니다.
--
-- 비유: 서류를 부서별로 깔끔히 나눠 놓으면 찾기 어려울 때,
--       자주 보는 서류는 내 책상에 복사본을 놔두는 것.
--
-- 언제 역정규화할까?
--   - 읽기(SELECT)가 매우 많고 쓰기(INSERT/UPDATE)가 적을 때
--   - JOIN이 5개 이상이어서 성능이 느릴 때
--   - 대시보드/리포트처럼 빠른 조회가 중요할 때
-- ═══════════════════════════════════════════════

-- 예: 주문 요약 테이블 (역정규화)
-- 매번 JOIN하지 않고 바로 볼 수 있는 요약 테이블
DROP TABLE IF EXISTS order_summary;

CREATE TABLE order_summary AS
SELECT
    o.id AS order_id,
    o.order_date,
    c.name AS customer_name,
    c.phone AS customer_phone,
    COUNT(oi.item_id) AS item_count,
    SUM(i.price * oi.qty) AS total_amount
FROM orders_3nf o
JOIN customers c ON o.customer_id = c.id
JOIN order_items_3nf oi ON o.id = oi.order_id
JOIN items i ON oi.item_id = i.id
GROUP BY o.id;

SELECT '📊 역정규화된 주문 요약 (빠른 조회용)' AS status;
SELECT * FROM order_summary;
-- JOIN 없이 바로 볼 수 있지만,
-- 원본이 바뀌면 이 테이블도 다시 만들어야 합니다!


-- ═══════════════════════════════════════════════
-- 정리 노트 — 정규화 단계
-- ═══════════════════════════════════════════════
--
-- ┌────────┬──────────────────────────────────────────┐
-- │  단계  │  규칙                                     │
-- ├────────┼──────────────────────────────────────────┤
-- │  1NF   │  칸 하나에 값 하나, 반복 칸 그룹 제거       │
-- │  2NF   │  기본키의 일부에만 의존하는 칸 분리          │
-- │  3NF   │  기본키 아닌 칸끼리 의존하는 관계 분리       │
-- │  역정규화│ 성능을 위해 일부러 합침 (읽기 위주 시스템) │
-- └────────┴──────────────────────────────────────────┘
--
-- 핵심 기억법:
--   1NF = "한 칸에 한 값"
--   2NF = "기본키 전체에 의존해야 함"
--   3NF = "기본키에만 의존해야 함 (다른 칸을 거치면 안 됨)"
-- ═══════════════════════════════════════════════
