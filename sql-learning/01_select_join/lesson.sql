-- ============================================================================
-- SQL 학습 01단계: SELECT, WHERE, ORDER BY, JOIN
-- 실제로 바로 실행해 볼 수 있도록 테이블 생성부터 조회까지 한 파일에 넣었습니다.
-- ============================================================================

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    class_name TEXT NOT NULL
);

CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    score INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

INSERT INTO classes (id, class_name) VALUES
    (1, '파랑반'),
    (2, '초록반');

INSERT INTO students (id, name, score, class_id) VALUES
    (1, '민수', 92, 1),
    (2, '지우', 85, 1),
    (3, '서연', 100, 2);

SELECT name, score
FROM students;

SELECT name, score
FROM students
WHERE score >= 90
ORDER BY score DESC;

SELECT s.name, s.score, c.class_name
FROM students s
JOIN classes c ON s.class_id = c.id
ORDER BY s.score DESC;
