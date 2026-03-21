-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- ■ 파일명: init.sql
-- ■ 목적: PostgreSQL 초기화 SQL
-- ■ 설명: 컨테이너 첫 실행 시 자동 실행돼서 테이블을 만들어
-- ■ 날짜: 2026-03-21
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

-- 아이템 테이블 생성
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 샘플 데이터 삽입
INSERT INTO items (name, description) VALUES
    ('Docker 입문', 'Docker의 기본 개념을 배웁니다'),
    ('Compose 실습', 'docker-compose로 멀티 서비스 관리'),
    ('볼륨 학습', '데이터 영속성과 볼륨 종류'),
    ('네트워크 이해', '컨테이너 간 통신 방법'),
    ('프로덕션 배포', '운영 환경 최적화 전략');
