-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- SQL 학습 08단계: 트리거와 제약 조건 (Trigger & Constraint)
-- 실행 방법: MySQL   →  mysql -u root -p < lesson.sql
--            SQLite  →  sqlite3 < lesson.sql (일부 문법 차이 있음)
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- 트리거란?
-- 테이블에 INSERT/UPDATE/DELETE가 일어나면 "자동으로" 실행되는 코드입니다.
-- 비유: 편의점 재고 관리에서 물건이 나가면 자동으로 재고를 줄이고,
--       재고가 5개 이하면 "주문 필요!" 알림을 남기는 것.
--
-- 제약 조건이란?
-- 테이블에 넣을 수 있는 값의 규칙을 정하는 것입니다.
-- 비유: "가격은 0원 이상이어야 한다", "상품 코드는 겹치면 안 된다"
--       같은 규칙을 DB가 스스로 지키게 합니다.
-- ============================================================================

-- ┌─────────────────────────────────────────────┐
-- │  준비: 편의점 재고 관리 시스템                │
-- └─────────────────────────────────────────────┘

DROP TABLE IF EXISTS inventory_log;
DROP TABLE IF EXISTS sale_records;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS suppliers;

-- 공급업체
CREATE TABLE suppliers (
    id    INTEGER PRIMARY KEY,
    name  TEXT NOT NULL
);

INSERT INTO suppliers VALUES (1, '맛있는식품'), (2, '신선유통');

-- 상품 테이블 (제약 조건 포함!)
CREATE TABLE products (
    id          INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    barcode     TEXT    NOT NULL UNIQUE,     -- UNIQUE: 바코드 겹치면 안 됨!
    price       INTEGER NOT NULL CHECK(price > 0),         -- CHECK: 가격은 양수만
    stock       INTEGER NOT NULL CHECK(stock >= 0),        -- CHECK: 재고는 0 이상
    min_stock   INTEGER NOT NULL DEFAULT 5,                -- 최소 재고 (이하면 주문)
    supplier_id INTEGER NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)     -- FOREIGN KEY: 존재하는 공급업체만
);

INSERT INTO products (id, name, barcode, price, stock, min_stock, supplier_id) VALUES
    (1, '삼각김밥',   'BAR-001', 1200, 20, 5, 1),
    (2, '초코우유',   'BAR-002', 1500, 8,  5, 2),
    (3, '컵라면',     'BAR-003', 1800, 3,  5, 1),
    (4, '바나나우유', 'BAR-004', 1300, 15, 5, 2);

-- 판매 기록
CREATE TABLE sale_records (
    id          INTEGER PRIMARY KEY,
    product_id  INTEGER NOT NULL,
    quantity    INTEGER NOT NULL CHECK(quantity > 0),
    sale_date   TEXT    NOT NULL DEFAULT (date('now')),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- 재고 변동 로그 (트리거가 자동으로 기록)
CREATE TABLE inventory_log (
    id          INTEGER PRIMARY KEY,
    product_id  INTEGER NOT NULL,
    change_type TEXT    NOT NULL,   -- 'SALE', 'RESTOCK', 'ALERT'
    old_stock   INTEGER,
    new_stock   INTEGER,
    message     TEXT,
    log_time    TEXT    NOT NULL DEFAULT (datetime('now'))
);


-- ┌─────────────────────────────────────────────┐
-- │  레슨 1: CHECK 제약 조건 — 잘못된 값 막기    │
-- └─────────────────────────────────────────────┘
-- CHECK는 "이 조건을 만족하는 값만 넣을 수 있다"는 규칙입니다.
-- 비유: 키가 120cm 이상이어야 놀이기구를 탈 수 있는 것처럼,
--       조건을 충족하지 못하면 DB가 거부합니다.
-- ═══════════════════════════════════════════════

-- 아래 두 줄은 CHECK에 걸려서 오류가 납니다:
-- INSERT INTO products VALUES (99, '공짜아이템', 'BAR-099', 0, 10, 5, 1);
--   → CHECK constraint failed: price > 0 (가격이 0이라서!)

-- INSERT INTO products VALUES (99, '귀신재고', 'BAR-099', 100, -5, 5, 1);
--   → CHECK constraint failed: stock >= 0 (재고가 음수라서!)

-- 정상적인 값은 잘 들어갑니다:
SELECT '✅ CHECK 제약 조건 테스트' AS test;
SELECT name, price, stock FROM products;


-- ┌─────────────────────────────────────────────┐
-- │  레슨 2: UNIQUE 제약 조건 — 중복 막기         │
-- └─────────────────────────────────────────────┘
-- UNIQUE는 "이 칸에 같은 값이 두 번 들어오면 안 된다"는 규칙입니다.
-- 비유: 학교에서 학번이 겹치면 안 되는 것처럼.
-- ═══════════════════════════════════════════════

-- 이미 있는 바코드를 다시 넣으면 오류:
-- INSERT INTO products VALUES (99, '가짜김밥', 'BAR-001', 1200, 10, 5, 1);
--   → UNIQUE constraint failed: products.barcode (BAR-001이 이미 있어서!)

SELECT '✅ UNIQUE 제약 조건 테스트' AS test;
SELECT name, barcode FROM products;


-- ┌─────────────────────────────────────────────┐
-- │  레슨 3: FOREIGN KEY — 존재하는 것만 참조     │
-- └─────────────────────────────────────────────┘
-- FOREIGN KEY는 "다른 테이블에 실제로 있는 값만 넣을 수 있다"는 규칙입니다.
-- 비유: 주소를 적을 때 실제로 존재하는 도시 이름만 쓸 수 있는 것.
-- ═══════════════════════════════════════════════

-- SQLite에서는 FOREIGN KEY 검사를 켜야 합니다:
PRAGMA foreign_keys = ON;

-- 존재하지 않는 공급업체(id=99)를 넣으면 오류:
-- INSERT INTO products VALUES (99, '유령상품', 'BAR-099', 1000, 10, 5, 99);
--   → FOREIGN KEY constraint failed (99번 공급업체가 없어서!)

SELECT '✅ FOREIGN KEY 제약 조건 테스트' AS test;
SELECT p.name, s.name AS supplier
FROM products p
JOIN suppliers s ON p.supplier_id = s.id;


-- ┌─────────────────────────────────────────────┐
-- │  레슨 4: BEFORE 트리거 — 실행 전에 가로채기   │
-- └─────────────────────────────────────────────┘
-- BEFORE 트리거는 INSERT/UPDATE가 "실행되기 전에" 먼저 동작합니다.
-- 비유: 편의점에서 물건을 팔기 전에 "재고가 충분한지" 먼저 확인하는 것.
--
-- 참고: SQLite에서는 BEFORE INSERT/UPDATE/DELETE 트리거를 지원합니다.
--       RAISE(ABORT, ...) 로 에러를 발생시킬 수 있습니다.
-- ═══════════════════════════════════════════════

-- 판매 시 재고가 부족하면 막는 트리거
CREATE TRIGGER trg_check_stock_before_sale
BEFORE INSERT ON sale_records
BEGIN
    SELECT CASE
        WHEN (SELECT stock FROM products WHERE id = NEW.product_id) < NEW.quantity
        THEN RAISE(ABORT, '재고 부족! 판매할 수 없습니다.')
    END;
END;

-- 재고 3개인 컵라면을 10개 팔려고 하면?
-- INSERT INTO sale_records (id, product_id, quantity) VALUES (99, 3, 10);
--   → 오류: "재고 부족! 판매할 수 없습니다."

-- 재고 20개인 삼각김밥 2개는 OK
INSERT INTO sale_records (id, product_id, quantity) VALUES (1, 1, 2);
SELECT '✅ BEFORE 트리거 통과: 삼각김밥 2개 판매 성공' AS test;


-- ┌─────────────────────────────────────────────┐
-- │  레슨 5: AFTER 트리거 — 실행 후 자동 처리     │
-- └─────────────────────────────────────────────┘
-- AFTER 트리거는 INSERT/UPDATE가 "성공한 뒤에" 동작합니다.
-- 비유: 물건이 팔린 뒤, 자동으로 재고를 줄이고 기록을 남기는 것.
-- ═══════════════════════════════════════════════

-- 판매 후 → 재고 감소 + 로그 기록
CREATE TRIGGER trg_after_sale
AFTER INSERT ON sale_records
BEGIN
    -- 1) 재고 감소
    UPDATE products
    SET stock = stock - NEW.quantity
    WHERE id = NEW.product_id;

    -- 2) 로그 기록
    INSERT INTO inventory_log (product_id, change_type, old_stock, new_stock, message)
    VALUES (
        NEW.product_id,
        'SALE',
        (SELECT stock + NEW.quantity FROM products WHERE id = NEW.product_id),
        (SELECT stock FROM products WHERE id = NEW.product_id),
        NEW.quantity || '개 판매됨'
    );

    -- 3) 최소 재고 이하면 경고 로그
    INSERT INTO inventory_log (product_id, change_type, old_stock, new_stock, message)
    SELECT
        NEW.product_id, 'ALERT', NULL,
        (SELECT stock FROM products WHERE id = NEW.product_id),
        '⚠ 재고 부족! 주문이 필요합니다.'
    WHERE (SELECT stock FROM products WHERE id = NEW.product_id)
          <= (SELECT min_stock FROM products WHERE id = NEW.product_id);
END;

-- 초코우유 3개 판매 (재고 8 → 5)
INSERT INTO sale_records (id, product_id, quantity) VALUES (2, 2, 3);

-- 초코우유 3개 더 판매 (재고 5 → 2, 최소재고 5 이하이므로 경고!)
INSERT INTO sale_records (id, product_id, quantity) VALUES (3, 2, 3);

SELECT '✅ AFTER 트리거 결과 확인' AS test;
SELECT name, stock, min_stock FROM products ORDER BY id;

SELECT '📋 자동 생성된 재고 로그:' AS log_title;
SELECT product_id, change_type, old_stock, new_stock, message
FROM inventory_log
ORDER BY id;


-- ┌─────────────────────────────────────────────┐
-- │  레슨 6: UPDATE 트리거 — 가격 변경 감시       │
-- └─────────────────────────────────────────────┘
-- 가격이 바뀔 때마다 자동으로 기록을 남깁니다.
-- 비유: CCTV처럼 "누가 가격을 바꿨는지" 기록하는 것.
-- ═══════════════════════════════════════════════

DROP TABLE IF EXISTS price_change_log;
CREATE TABLE price_change_log (
    id          INTEGER PRIMARY KEY,
    product_id  INTEGER NOT NULL,
    old_price   INTEGER NOT NULL,
    new_price   INTEGER NOT NULL,
    changed_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TRIGGER trg_price_change
AFTER UPDATE OF price ON products
WHEN OLD.price != NEW.price
BEGIN
    INSERT INTO price_change_log (product_id, old_price, new_price)
    VALUES (OLD.id, OLD.price, NEW.price);
END;

-- 삼각김밥 가격 인상: 1200 → 1500
UPDATE products SET price = 1500 WHERE id = 1;

SELECT '✅ 가격 변경 로그' AS test;
SELECT p.name, pcl.old_price, pcl.new_price, pcl.changed_at
FROM price_change_log pcl
JOIN products p ON pcl.product_id = p.id;


-- ┌─────────────────────────────────────────────┐
-- │  레슨 7: DELETE 트리거 — 삭제 전 백업         │
-- └─────────────────────────────────────────────┘
-- 실수로 상품을 지웠을 때 복구할 수 있도록 백업합니다.
-- ═══════════════════════════════════════════════

DROP TABLE IF EXISTS products_backup;
CREATE TABLE products_backup (
    id          INTEGER,
    name        TEXT,
    barcode     TEXT,
    price       INTEGER,
    stock       INTEGER,
    deleted_at  TEXT DEFAULT (datetime('now'))
);

CREATE TRIGGER trg_backup_before_delete
BEFORE DELETE ON products
BEGIN
    INSERT INTO products_backup (id, name, barcode, price, stock)
    VALUES (OLD.id, OLD.name, OLD.barcode, OLD.price, OLD.stock);
END;

-- 바나나우유 삭제
DELETE FROM products WHERE id = 4;

SELECT '✅ 삭제된 상품이 백업에 저장됨' AS test;
SELECT * FROM products_backup;


-- ┌─────────────────────────────────────────────┐
-- │  레슨 8: 트리거 관리                         │
-- └─────────────────────────────────────────────┘
-- ═══════════════════════════════════════════════

-- SQLite: 트리거 목록 보기
SELECT name, tbl_name FROM sqlite_master WHERE type = 'trigger';

-- 트리거 삭제
-- DROP TRIGGER IF EXISTS trg_after_sale;


-- ═══════════════════════════════════════════════
-- 정리 노트
-- ═══════════════════════════════════════════════
-- CHECK         : 값의 조건 강제 (price > 0)
-- UNIQUE        : 중복 불가 (바코드 겹침 방지)
-- FOREIGN KEY   : 다른 테이블에 있는 값만 허용
-- NOT NULL      : 비어 있으면 안 됨
-- DEFAULT       : 안 넣으면 기본값 사용
-- BEFORE 트리거 : 실행 전에 가로채기 (검증, 차단)
-- AFTER 트리거  : 실행 후 자동 처리 (로그, 재고 감소)
-- WHEN 조건     : 트리거 실행 조건 추가
-- OLD / NEW     : 변경 전/후 값 참조
-- ═══════════════════════════════════════════════
