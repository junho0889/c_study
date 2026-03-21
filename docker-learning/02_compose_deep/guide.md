# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# ■ 파일명: guide.md
# ■ 목적: Docker Compose 심화 가이드
# ■ 설명: Compose 명령어 총정리, 서비스 간 통신, DNS 해석
# ■ 날짜: 2026-03-21
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# Docker Compose 심화 가이드

## 1. Docker Compose란?

여러 개의 컨테이너를 **한 번에** 관리하는 도구야.

하나의 `docker-compose.yml` 파일에 모든 서비스를 정의하고,
`docker-compose up` 한 방이면 전부 실행돼!

```
docker run 여러 번 실행      vs     docker-compose up 한 번
━━━━━━━━━━━━━━━━━━━━━━━━          ━━━━━━━━━━━━━━━━━━━━━━━
docker run redis                   docker-compose up -d
docker run postgres                (끝!)
docker run myapp
docker network create ...
docker volume create ...
(너무 복잡해!)
```

## 2. docker-compose 명령어 총정리

### 기본 명령어

| 명령어 | 설명 | 자주 쓰는 옵션 |
|--------|------|----------------|
| `up` | 서비스 시작 | `-d` (백그라운드), `--build` (빌드 후 시작) |
| `down` | 서비스 종료 | `-v` (볼륨도 삭제), `--rmi all` (이미지도 삭제) |
| `ps` | 서비스 상태 보기 | |
| `logs` | 로그 보기 | `-f` (실시간), `--tail 100` (마지막 100줄) |
| `exec` | 서비스에서 명령 실행 | `-it` (인터랙티브) |
| `build` | 이미지 빌드 | `--no-cache` (캐시 무시) |
| `pull` | 이미지 다운로드 | |
| `restart` | 서비스 재시작 | |
| `stop` | 서비스 정지 | |
| `start` | 정지된 서비스 시작 | |
| `config` | 설정 파일 검증 | `--services` (서비스 목록만) |
| `top` | 프로세스 목록 | |

### 실전 명령어 예시

```bash
# ── 시작과 종료 ──
docker-compose up -d                    # 모든 서비스 백그라운드 시작
docker-compose up -d --build            # 이미지 다시 빌드 후 시작
docker-compose up -d web                # web 서비스만 시작
docker-compose down                     # 모든 서비스 종료
docker-compose down -v                  # 종료 + 볼륨까지 삭제
docker-compose down --rmi all -v        # 종료 + 이미지 + 볼륨 전부 삭제

# ── 상태 확인 ──
docker-compose ps                       # 서비스 상태 보기
docker-compose ps -a                    # 정지된 서비스 포함
docker-compose top                      # 각 서비스의 프로세스 목록

# ── 로그 ──
docker-compose logs                     # 전체 로그
docker-compose logs -f                  # 실시간 로그 (Ctrl+C로 종료)
docker-compose logs -f web              # web 서비스 로그만
docker-compose logs --tail 50 db        # db 서비스 마지막 50줄

# ── 실행 중인 서비스에 접속 ──
docker-compose exec web bash            # web 서비스 셸 접속
docker-compose exec db psql -U postgres # PostgreSQL 클라이언트 접속
docker-compose exec redis redis-cli     # Redis 클라이언트 접속

# ── 빌드 ──
docker-compose build                    # 모든 서비스 빌드
docker-compose build --no-cache web     # 캐시 없이 web만 빌드
docker-compose build --parallel         # 병렬 빌드

# ── 설정 검증 ──
docker-compose config                   # 설정 파일 문법 검증 + 최종 결과 출력
docker-compose config --services        # 서비스 이름만 출력
```

## 3. 서비스 간 통신 (DNS 이름 해석)

Docker Compose가 자동으로 해주는 마법 같은 기능이야!

```
같은 네트워크 안에 있는 컨테이너끼리는
"서비스 이름"으로 서로 찾을 수 있어!

┌──────────────────────────────────────────┐
│         Docker 네트워크 (backend)         │
│                                          │
│  web 컨테이너에서:                        │
│    redis://redis:6379    ← "redis" = 서비스 이름│
│    postgres://db:5432    ← "db" = 서비스 이름  │
│                                          │
│  ┌─────┐    ┌───────┐    ┌────────────┐  │
│  │ web │────│ redis │    │ PostgreSQL │  │
│  │     │────│       │    │   (db)     │  │
│  └─────┘    └───────┘    └────────────┘  │
└──────────────────────────────────────────┘
```

### 왜 서비스 이름으로 통신할까?

```
IP 주소 사용 ❌ (나쁜 방법):
  - 컨테이너 IP는 매번 바뀔 수 있어
  - redis = 172.18.0.3 (이번에), 172.18.0.5 (다음에)

서비스 이름 사용 ✅ (좋은 방법):
  - "redis"라고 쓰면 Docker가 알아서 IP를 찾아줘
  - Docker 내장 DNS 서버가 이름 → IP 변환을 해줘
```

### 네트워크 분리의 중요성

```
이 프로젝트의 네트워크 구성:

  frontend 네트워크          backend 네트워크
  ┌──────────────────┐     ┌──────────────────┐
  │  nginx ←→ web    │     │  web ←→ db       │
  │                  │     │  web ←→ redis     │
  └──────────────────┘     └──────────────────┘

  nginx는 backend 네트워크에 없으니까
  db나 redis에 직접 접근할 수 없어! (보안!)
```

## 4. 환경변수 우선순위

Docker Compose에서 환경변수를 설정하는 방법은 여러 가지야.
우선순위가 높은 것이 이겨:

```
우선순위 (높은 순서):
1. docker-compose exec -e로 전달한 변수
2. docker-compose.yml의 environment 섹션
3. .env 파일 (docker-compose.yml과 같은 디렉토리)
4. Dockerfile의 ENV 명령어
5. 이미지에 포함된 환경변수
```

### .env 파일 사용법

```bash
# .env 파일은 docker-compose.yml과 같은 디렉토리에 있어야 해

# docker-compose.yml에서:
environment:
  - DB_PASSWORD=${DB_PASSWORD:-default}
  # ${변수명:-기본값} 형태
  # .env에 DB_PASSWORD가 있으면 그 값, 없으면 "default"

# 다른 .env 파일 사용하기:
docker-compose --env-file .env.production up -d
```

## 5. depends_on 심화

```yaml
# 단순 의존성 (시작 순서만 보장)
depends_on:
  - db
  - redis

# 조건부 의존성 (상태까지 확인) ← 추천!
depends_on:
  db:
    condition: service_healthy    # healthcheck 통과할 때까지 대기
  redis:
    condition: service_started    # 시작만 하면 OK
```

## 6. 이 프로젝트 실행하기

```bash
# 1. 디렉토리 이동
cd 02_compose_deep/

# 2. 설정 검증
docker-compose config

# 3. 시작
docker-compose up -d

# 4. 상태 확인
docker-compose ps

# 5. 각 서비스 접속 테스트
curl http://localhost:80              # Nginx → Web
docker-compose exec db psql -U postgres -d myapp  # DB 접속
docker-compose exec redis redis-cli   # Redis 접속

# 6. 로그 확인
docker-compose logs -f

# 7. 종료
docker-compose down -v
```

## 7. 트러블슈팅

| 문제 | 원인 | 해결 |
|------|------|------|
| 서비스가 시작 안 됨 | depends_on 조건 미충족 | `docker-compose logs 서비스명`으로 확인 |
| 연결 거부 (Connection refused) | 서비스가 아직 준비 안 됨 | healthcheck + depends_on condition 사용 |
| 환경변수가 안 먹힘 | .env 파일 위치 오류 | `docker-compose config`로 최종 값 확인 |
| 볼륨 데이터가 안 보임 | 볼륨 경로 오타 | `docker volume ls`로 볼륨 확인 |
| 포트 충돌 | 다른 프로세스가 사용 중 | `.env`에서 포트 번호 변경 |
