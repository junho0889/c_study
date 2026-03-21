-- 초기화 SQL: 컨테이너 첫 실행 시 자동 실행
CREATE TABLE IF NOT EXISTS visits (
    id SERIAL PRIMARY KEY,
    visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45)
);
