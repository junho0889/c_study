-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
-- SQL 학습 10단계: 실무에서 자주 쓰는 패턴들 (Practical Patterns)
-- 실행 방법: SQLite  →  sqlite3 < lesson.sql
--            MySQL   →  mysql -u root -p < lesson.sql
-- ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
--
-- 이 파일은 실제 서비스를 만들 때 거의 반드시 쓰게 되는
-- 검증된 SQL 패턴들을 모았습니다.
-- "이론은 알겠는데 실전에서 어떻게 쓰지?"에 대한 답입니다.
-- ============================================================================

-- ┌─────────────────────────────────────────────┐
-- │  준비: 게시판 시스템 테이블                   │
-- └─────────────────────────────────────────────┘

DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id         INTEGER PRIMARY KEY,
    username   TEXT    NOT NULL UNIQUE,
    email      TEXT    NOT NULL,
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    is_deleted INTEGER NOT NULL DEFAULT 0    -- Soft Delete용
);

CREATE TABLE posts (
    id         INTEGER PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    title      TEXT    NOT NULL,
    body       TEXT    NOT NULL,
    view_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT,
    is_deleted INTEGER NOT NULL DEFAULT 0,   -- Soft Delete용
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE comments (
    id         INTEGER PRIMARY KEY,
    post_id    INTEGER NOT NULL,
    user_id    INTEGER NOT NULL,
    content    TEXT    NOT NULL,
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    is_deleted INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 감사 로그 (누가 무엇을 했는지 기록)
CREATE TABLE audit_log (
    id          INTEGER PRIMARY KEY,
    table_name  TEXT NOT NULL,
    record_id   INTEGER NOT NULL,
    action      TEXT NOT NULL,      -- 'INSERT', 'UPDATE', 'DELETE'
    old_value   TEXT,
    new_value   TEXT,
    changed_by  INTEGER,
    changed_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 샘플 데이터 넣기
INSERT INTO users (id, username, email) VALUES
    (1, 'minsu',  'minsu@test.com'),
    (2, 'jiwoo',  'jiwoo@test.com'),
    (3, 'seoyeon','seoyeon@test.com'),
    (4, 'hajun',  'hajun@test.com'),
    (5, 'yuna',   'yuna@test.com');

INSERT INTO posts (id, user_id, title, body, view_count, created_at) VALUES
    (1, 1, '첫 번째 글',  '안녕하세요! 첫 글입니다.',       150, '2024-03-01 09:00:00'),
    (2, 1, '두 번째 글',  'SQL 공부를 시작했습니다.',        230, '2024-03-02 10:30:00'),
    (3, 2, '지우의 일기',  '오늘 날씨가 좋았습니다.',         45, '2024-03-03 14:00:00'),
    (4, 3, '코딩 팁',     'SELECT를 잘 쓰는 방법.',         890, '2024-03-04 16:20:00'),
    (5, 2, '맛집 추천',   '학교 앞 떡볶이 맛집!',           340, '2024-03-05 11:00:00'),
    (6, 4, '게임 리뷰',   '새로 나온 게임을 해봤습니다.',    120, '2024-03-06 18:00:00'),
    (7, 5, '공부 계획',   '이번 주 공부 계획을 세웠습니다.',   67, '2024-03-07 08:00:00'),
    (8, 1, '질문있어요',  'JOIN이 뭔가요?',                 410, '2024-03-08 09:30:00'),
    (9, 3, '프로젝트 소개','학교 프로젝트를 소개합니다.',     200, '2024-03-09 13:00:00'),
    (10,4, '주말 이야기', '주말에 산에 다녀왔습니다.',         88, '2024-03-10 20:00:00');

INSERT INTO comments (id, post_id, user_id, content, created_at) VALUES
    (1, 1, 2, '환영해요!',          '2024-03-01 10:00:00'),
    (2, 1, 3, '반갑습니다!',        '2024-03-01 11:00:00'),
    (3, 4, 1, '좋은 팁이네요!',     '2024-03-04 17:00:00'),
    (4, 4, 5, '저도 배우고 싶어요', '2024-03-04 18:00:00'),
    (5, 5, 3, '거기 저도 가봤어요', '2024-03-05 12:00:00');


-- ┌─────────────────────────────────────────────┐
-- │  패턴 1: 페이지네이션 (Pagination)            │
-- └─────────────────────────────────────────────┘
-- 게시판에 글이 1000개 있을 때 한 번에 다 보여주면 느리죠.
-- 10개씩 끊어서 "1페이지, 2페이지, …"로 보여줍니다.
--
-- 비유: 책의 목차처럼 한 페이지에 10줄씩 보여주는 것.
-- LIMIT = 한 페이지에 몇 개
-- OFFSET = 앞에서 몇 개를 건너뛸지
-- ═══════════════════════════════════════════════

-- 1페이지 (처음 3개)
SELECT '📄 1페이지' AS page;
SELECT id, title, view_count, created_at
FROM posts
WHERE is_deleted = 0
ORDER BY created_at DESC
LIMIT 3 OFFSET 0;

-- 2페이지 (4~6번째)
SELECT '📄 2페이지' AS page;
SELECT id, title, view_count, created_at
FROM posts
WHERE is_deleted = 0
ORDER BY created_at DESC
LIMIT 3 OFFSET 3;

-- 3페이지 (7~9번째)
SELECT '📄 3페이지' AS page;
SELECT id, title, view_count, created_at
FROM posts
WHERE is_deleted = 0
ORDER BY created_at DESC
LIMIT 3 OFFSET 6;

-- 전체 페이지 수 계산
SELECT
    COUNT(*) AS total_posts,
    (COUNT(*) + 3 - 1) / 3 AS total_pages  -- 올림 나눗셈
FROM posts
WHERE is_deleted = 0;


-- ┌─────────────────────────────────────────────┐
-- │  패턴 2: Soft Delete (논리 삭제)              │
-- └─────────────────────────────────────────────┘
-- 실제로 DELETE 하면 복구할 수 없습니다.
-- 대신 is_deleted = 1로 "삭제된 것처럼" 표시만 합니다.
--
-- 비유: 연필로 쓴 글을 지우개로 지우는 게 아니라,
--       줄을 긋고 "삭제됨"이라고 표시하는 것.
--       나중에 "아, 틀렸다 복구해야지" 할 수 있어요.
-- ═══════════════════════════════════════════════

-- 글 삭제 (실제로는 표시만)
UPDATE posts SET is_deleted = 1, updated_at = datetime('now')
WHERE id = 6;

-- 삭제 안 된 글만 보기 (일반 조회)
SELECT '✅ Soft Delete 후 — 삭제 안 된 글만' AS status;
SELECT id, title FROM posts WHERE is_deleted = 0;

-- 관리자: 삭제된 글도 볼 수 있음
SELECT '🗑 삭제된 글 포함' AS status;
SELECT id, title, CASE is_deleted WHEN 1 THEN '삭제됨' ELSE '정상' END AS state
FROM posts;

-- 복구도 쉬움!
UPDATE posts SET is_deleted = 0, updated_at = datetime('now')
WHERE id = 6;


-- ┌─────────────────────────────────────────────┐
-- │  패턴 3: Audit Log (감사 로그)                │
-- └─────────────────────────────────────────────┘
-- "누가, 언제, 무엇을 바꿨는지" 기록하는 패턴입니다.
-- 보안, 디버깅, 법적 요구사항 때문에 거의 모든 서비스에서 씁니다.
--
-- 비유: CCTV 녹화처럼 모든 변경 사항을 기록해 두는 것.
-- ═══════════════════════════════════════════════

-- 트리거로 자동 기록 (글 수정 시)
CREATE TRIGGER trg_audit_post_update
AFTER UPDATE ON posts
WHEN OLD.title != NEW.title OR OLD.body != NEW.body
BEGIN
    INSERT INTO audit_log (table_name, record_id, action, old_value, new_value, changed_by)
    VALUES (
        'posts',
        NEW.id,
        'UPDATE',
        '제목: ' || OLD.title || ' / 내용: ' || OLD.body,
        '제목: ' || NEW.title || ' / 내용: ' || NEW.body,
        NEW.user_id
    );
END;

-- 글 수정 테스트
UPDATE posts
SET title = '코딩 팁 (수정됨)', body = 'SELECT를 잘 쓰는 방법 + GROUP BY 추가!',
    updated_at = datetime('now')
WHERE id = 4;

SELECT '📋 감사 로그 기록' AS status;
SELECT action, old_value, new_value, changed_at FROM audit_log;


-- ┌─────────────────────────────────────────────┐
-- │  패턴 4: Pivot Table (행↔열 변환)             │
-- └─────────────────────────────────────────────┘
-- 세로로 나열된 데이터를 가로 표로 바꾸는 패턴입니다.
-- 비유: 출석부에서 학생별로 "월/화/수/…" 출석 여부를 가로로 보여주는 것.
-- ═══════════════════════════════════════════════

-- 사용자별 글 수와 댓글 수를 가로로
SELECT
    u.username,
    COUNT(DISTINCT p.id) AS post_count,
    COUNT(DISTINCT c.id) AS comment_count,
    COALESCE(SUM(p.view_count), 0) AS total_views
FROM users u
LEFT JOIN posts p ON u.id = p.user_id AND p.is_deleted = 0
LEFT JOIN comments c ON u.id = c.user_id AND c.is_deleted = 0
GROUP BY u.id, u.username
ORDER BY post_count DESC;

-- 월별 글 수 피벗 (CASE WHEN으로 구현)
DROP TABLE IF EXISTS monthly_sales;
CREATE TABLE monthly_sales (
    month_name TEXT,
    category   TEXT,
    amount     INTEGER
);

INSERT INTO monthly_sales VALUES
    ('1월', '음식', 50000), ('1월', '옷', 30000), ('1월', '전자', 80000),
    ('2월', '음식', 45000), ('2월', '옷', 35000), ('2월', '전자', 70000),
    ('3월', '음식', 60000), ('3월', '옷', 25000), ('3월', '전자', 90000);

SELECT '📊 Pivot Table — 카테고리별 월간 매출' AS status;
SELECT
    category,
    SUM(CASE WHEN month_name = '1월' THEN amount ELSE 0 END) AS "1월",
    SUM(CASE WHEN month_name = '2월' THEN amount ELSE 0 END) AS "2월",
    SUM(CASE WHEN month_name = '3월' THEN amount ELSE 0 END) AS "3월",
    SUM(amount) AS 합계
FROM monthly_sales
GROUP BY category;


-- ┌─────────────────────────────────────────────┐
-- │  패턴 5: Full-Text Search (전문 검색)         │
-- └─────────────────────────────────────────────┘
-- LIKE '%검색어%'는 느립니다 (인덱스를 못 씀).
-- SQLite의 FTS5, MySQL의 FULLTEXT INDEX를 쓰면 빠릅니다.
--
-- 비유: 책에서 단어를 찾을 때
--   LIKE = 1페이지부터 끝까지 한 글자씩 비교 (느림)
--   FTS  = 맨 뒤의 "찾아보기(색인)"를 이용 (빠름)
-- ═══════════════════════════════════════════════

-- 기본 검색 (느린 방법 — 데이터 적을 때는 OK)
SELECT '🔍 LIKE 검색' AS status;
SELECT id, title, body
FROM posts
WHERE (title LIKE '%SQL%' OR body LIKE '%SELECT%')
  AND is_deleted = 0;

-- SQLite FTS5 전문 검색 (빠른 방법)
DROP TABLE IF EXISTS posts_fts;
CREATE VIRTUAL TABLE posts_fts USING fts5(title, body);

INSERT INTO posts_fts (rowid, title, body)
SELECT id, title, body FROM posts WHERE is_deleted = 0;

SELECT '🔍 FTS5 전문 검색' AS status;
SELECT rowid, title, body FROM posts_fts WHERE posts_fts MATCH 'SQL OR 공부';
-- FTS는 데이터가 수십만 건일 때 LIKE보다 수백 배 빠를 수 있습니다!


-- ┌─────────────────────────────────────────────┐
-- │  패턴 6: Upsert (있으면 수정, 없으면 삽입)    │
-- └─────────────────────────────────────────────┘
-- 비유: 출석부에 이름이 있으면 출석 표시를 업데이트,
--       이름이 없으면 새로 추가.
-- ═══════════════════════════════════════════════

DROP TABLE IF EXISTS user_settings;
CREATE TABLE user_settings (
    user_id INTEGER PRIMARY KEY,
    theme   TEXT NOT NULL DEFAULT 'light',
    lang    TEXT NOT NULL DEFAULT 'ko'
);

-- 처음: 없으므로 INSERT
INSERT INTO user_settings (user_id, theme, lang) VALUES (1, 'dark', 'ko')
    ON CONFLICT(user_id) DO UPDATE SET theme = excluded.theme, lang = excluded.lang;

-- 다시: 이미 있으므로 UPDATE
INSERT INTO user_settings (user_id, theme, lang) VALUES (1, 'blue', 'en')
    ON CONFLICT(user_id) DO UPDATE SET theme = excluded.theme, lang = excluded.lang;

SELECT '✅ Upsert 결과' AS status;
SELECT * FROM user_settings;
-- theme이 'dark'가 아니라 'blue'로 바뀌어 있습니다!


-- ┌─────────────────────────────────────────────┐
-- │  패턴 7: 통계 대시보드 쿼리                   │
-- └─────────────────────────────────────────────┘
-- 관리자 화면에서 자주 쓰는 "한 방 쿼리" 모음
-- ═══════════════════════════════════════════════

SELECT '📊 대시보드 통계' AS status;

-- 전체 요약
SELECT
    (SELECT COUNT(*) FROM users WHERE is_deleted = 0) AS total_users,
    (SELECT COUNT(*) FROM posts WHERE is_deleted = 0) AS total_posts,
    (SELECT COUNT(*) FROM comments WHERE is_deleted = 0) AS total_comments,
    (SELECT SUM(view_count) FROM posts WHERE is_deleted = 0) AS total_views;

-- 인기글 TOP 3
SELECT '🏆 인기글 TOP 3' AS ranking;
SELECT p.title, u.username AS author, p.view_count
FROM posts p
JOIN users u ON p.user_id = u.id
WHERE p.is_deleted = 0
ORDER BY p.view_count DESC
LIMIT 3;

-- 활동 많은 사용자 TOP 3
SELECT '👑 활동왕 TOP 3' AS ranking;
SELECT
    u.username,
    COUNT(DISTINCT p.id) AS posts,
    COUNT(DISTINCT c.id) AS comments,
    COUNT(DISTINCT p.id) + COUNT(DISTINCT c.id) AS total_activity
FROM users u
LEFT JOIN posts p ON u.id = p.user_id AND p.is_deleted = 0
LEFT JOIN comments c ON u.id = c.user_id AND c.is_deleted = 0
WHERE u.is_deleted = 0
GROUP BY u.id
ORDER BY total_activity DESC
LIMIT 3;


-- ═══════════════════════════════════════════════
-- 정리 노트 — 실무 패턴 요약
-- ═══════════════════════════════════════════════
-- Pagination    : LIMIT + OFFSET으로 페이지 나누기
-- Soft Delete   : is_deleted 칸으로 논리 삭제 (복구 가능)
-- Audit Log     : 트리거로 변경 이력 자동 기록
-- Pivot Table   : CASE WHEN으로 행↔열 변환
-- Full-Text     : FTS5/FULLTEXT INDEX로 빠른 텍스트 검색
-- Upsert        : ON CONFLICT로 있으면 수정, 없으면 삽입
-- Dashboard     : 서브쿼리 + JOIN으로 통계 한 방 쿼리
-- ═══════════════════════════════════════════════
