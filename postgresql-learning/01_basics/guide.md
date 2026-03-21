# ■■■ PostgreSQL 기초 가이드 ■■■

## ■■■ 1. 환경 시작 ■■■

```bash
# Docker Compose로 PostgreSQL + pgAdmin 시작
cd postgresql-learning/01_basics
docker-compose up -d

# 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f postgres
```

## ■■■ 2. psql 접속 방법 ■■■

### 방법 1: Docker exec으로 직접 접속

```bash
# 컨테이너 내부의 psql 사용
docker-compose exec postgres psql -U postgres -d study_db

# 또는 컨테이너 이름으로 접속
docker exec -it pg-study psql -U postgres -d study_db
```

### 방법 2: 호스트에서 psql로 접속

```bash
# 호스트에 psql이 설치되어 있는 경우
psql -h localhost -p 5432 -U postgres -d study_db
# 비밀번호: postgres123 (.env 파일에서 설정)
```

### 방법 3: 연결 문자열 (Connection String)

```bash
psql "postgresql://postgres:postgres123@localhost:5432/study_db"
```

## ■■■ 3. psql 필수 명령어 ■■■

| 명령어 | 설명 |
|--------|------|
| `\l` | 데이터베이스 목록 |
| `\c dbname` | 데이터베이스 전환 |
| `\dt` | 테이블 목록 |
| `\dt+` | 테이블 목록 (크기 포함) |
| `\d tablename` | 테이블 구조 상세 |
| `\d+ tablename` | 테이블 구조 + 설명 |
| `\di` | 인덱스 목록 |
| `\dn` | 스키마 목록 |
| `\du` | 사용자/역할 목록 |
| `\df` | 함수 목록 |
| `\dv` | 뷰 목록 |
| `\x` | 확장 출력 모드 토글 (세로 표시) |
| `\timing` | 쿼리 실행 시간 표시 토글 |
| `\i filename.sql` | SQL 파일 실행 |
| `\o filename` | 출력을 파일로 저장 |
| `\e` | 외부 편집기로 쿼리 편집 |
| `\q` | psql 종료 |
| `\?` | psql 명령어 도움말 |
| `\h SELECT` | SQL 명령어 도움말 |

### 유용한 psql 팁

```sql
-- 쿼리 실행 시간 표시
\timing on

-- 확장 출력 (컬럼이 많을 때 세로로 표시)
\x auto

-- 현재 연결 정보 확인
\conninfo

-- NULL 값 표시 문자 변경
\pset null '(NULL)'

-- 쿼리 결과를 CSV로 출력
\copy (SELECT * FROM employees) TO '/tmp/employees.csv' WITH CSV HEADER
```

## ■■■ 4. pgAdmin 4 사용법 ■■■

### 접속

1. 브라우저에서 `http://localhost:5050` 접속
2. 로그인: `admin@admin.com` / `admin123`

### 서버 등록

1. 좌측 패널 → **Servers** 우클릭 → **Register** → **Server**
2. **General** 탭:
   - Name: `Study DB` (표시 이름)
3. **Connection** 탭:
   - Host: `postgres` (Docker 네트워크 내 컨테이너 이름)
   - Port: `5432`
   - Maintenance database: `study_db`
   - Username: `postgres`
   - Password: `postgres123`
   - Save password: 체크

### pgAdmin 주요 기능

| 기능 | 경로 | 설명 |
|------|------|------|
| Query Tool | 서버 → DB → Tools → Query Tool | SQL 쿼리 실행 |
| Dashboard | 서버 선택 시 자동 표시 | 서버 상태 모니터링 |
| ERD | Tools → ERD For Database | ER 다이어그램 생성 |
| Backup | DB 우클릭 → Backup | 데이터베이스 백업 |
| Restore | DB 우클릭 → Restore | 백업 복원 |

## ■■■ 5. 데이터베이스 관리 기본 ■■■

```sql
-- 데이터베이스 생성
CREATE DATABASE mydb
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TEMPLATE = template0;

-- 데이터베이스 삭제
DROP DATABASE IF EXISTS mydb;

-- 스키마 생성 (네임스페이스, 테이블 그룹화)
CREATE SCHEMA IF NOT EXISTS app;

-- 스키마 내 테이블 생성
CREATE TABLE app.users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

-- 검색 경로 설정 (스키마를 명시하지 않아도 찾을 수 있게)
SET search_path TO app, public;
```

## ■■■ 6. 환경 종료 ■■■

```bash
# 컨테이너 중지 (데이터 유지)
docker-compose stop

# 컨테이너 삭제 + 볼륨 삭제 (데이터 초기화)
docker-compose down -v

# 컨테이너 삭제 (볼륨 유지 → 데이터 보존)
docker-compose down
```
