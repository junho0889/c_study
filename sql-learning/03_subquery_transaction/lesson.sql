-- ============================================================================
-- SQL 학습 03단계: 서브쿼리와 트랜잭션
-- 작은 질문을 먼저 안쪽에서 계산한 뒤 바깥 질문에 넣는 법,
-- 그리고 여러 UPDATE를 한 묶음으로 안전하게 처리하는 법을 같이 익힙니다.
-- ============================================================================

DROP TABLE IF EXISTS accounts;

CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    owner_name TEXT,
    balance INTEGER
);

INSERT INTO accounts (id, owner_name, balance) VALUES
    (1, '민수', 10000),
    (2, '지우', 8000),
    (3, '서연', 12000);

-- 레슨 1: 평균 잔액보다 많은 계좌 찾기
SELECT owner_name, balance
FROM accounts
WHERE balance > (
    SELECT AVG(balance)
    FROM accounts
);

-- 레슨 2: 송금은 두 UPDATE를 한 묶음으로 처리해야 함
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 2000 WHERE id = 1;
UPDATE accounts SET balance = balance + 2000 WHERE id = 2;
COMMIT;

SELECT * FROM accounts ORDER BY id;

-- 레슨 3: 중간에 마음이 바뀌면 ROLLBACK으로 취소 가능
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 500 WHERE id = 2;
UPDATE accounts SET balance = balance + 500 WHERE id = 3;
ROLLBACK;

SELECT * FROM accounts ORDER BY id;
