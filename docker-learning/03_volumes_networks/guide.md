# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# ■ 파일명: guide.md
# ■ 목적: Docker 볼륨과 네트워크 완벽 가이드
# ■ 설명: 볼륨 종류 비교, 네트워크 종류 비교, 백업/복원 방법
# ■ 날짜: 2026-03-21
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# Docker 볼륨과 네트워크 완벽 가이드

## 1. 볼륨이 왜 필요해?

```
컨테이너는 일회용이야!
컨테이너를 삭제하면 안에 있던 데이터도 다 사라져!

볼륨 없이:
  컨테이너 시작 → 데이터 저장 → 컨테이너 삭제 → 데이터 사라짐 😱

볼륨 있으면:
  컨테이너 시작 → 데이터 저장 (볼륨에) → 컨테이너 삭제 → 데이터 남아있음 ✅
```

## 2. 볼륨 종류별 비교표

| 구분 | Named Volume | Bind Mount | tmpfs |
|------|-------------|------------|-------|
| **저장 위치** | Docker가 관리하는 영역 | 호스트의 특정 경로 | 메모리(RAM) |
| **영속성** | 컨테이너 삭제해도 유지 | 호스트에 남아있음 | 컨테이너 종료 시 삭제 |
| **성능** | 좋음 | OS에 따라 다름 | 매우 빠름 (RAM이니까) |
| **이식성** | 높음 (경로 무관) | 낮음 (호스트 경로 의존) | 높음 |
| **관리** | Docker CLI로 관리 | 호스트에서 직접 관리 | 관리 불필요 |
| **사용 사례** | DB 데이터, 설정 | 소스코드, 설정 파일 | 비밀번호, 임시 파일 |
| **문법** | `volume:/path` | `./host:/path` | `tmpfs: /path` |
| **백업** | docker volume 명령 | cp/rsync 등 | 불가 (메모리니까) |

### 각 볼륨 사용 예시

```yaml
services:
  myapp:
    image: myapp:latest
    volumes:
      # Named Volume: DB 데이터처럼 중요한 데이터에 사용
      - app-data:/var/lib/data

      # Bind Mount: 개발 시 소스코드 실시간 반영
      - ./src:/app/src

      # Bind Mount (읽기 전용): 설정 파일
      - ./config.yml:/app/config.yml:ro

    # tmpfs: 민감한 임시 데이터
    tmpfs:
      - /tmp:size=100m
      - /app/secrets:size=10m

volumes:
  app-data:
    driver: local
```

## 3. 볼륨 관리 명령어

```bash
# ── 볼륨 생성 ──
docker volume create my-volume                    # 볼륨 만들기

# ── 볼륨 목록 ──
docker volume ls                                  # 모든 볼륨 보기

# ── 볼륨 상세 정보 ──
docker volume inspect my-volume                   # 볼륨 세부 정보

# ── 볼륨 삭제 ──
docker volume rm my-volume                        # 특정 볼륨 삭제
docker volume prune                               # 사용 안 하는 볼륨 전부 삭제

# ── 볼륨 사용 확인 ──
docker ps -a --filter volume=my-volume            # 이 볼륨을 사용하는 컨테이너
```

## 4. 데이터 백업과 복원

### 방법 1: 별도 컨테이너로 백업

```bash
# ── PostgreSQL 볼륨 백업 ──
# 임시 컨테이너를 만들어서 볼륨 데이터를 tar로 압축해
docker run --rm \
  -v vol-db-data:/source:ro \
  -v $(pwd)/backup:/backup \
  alpine \
  tar czf /backup/db-backup-$(date +%Y%m%d).tar.gz -C /source .

# 설명:
# --rm: 작업 끝나면 컨테이너 자동 삭제
# -v vol-db-data:/source:ro: 백업할 볼륨을 읽기 전용으로 마운트
# -v $(pwd)/backup:/backup: 백업 파일을 호스트에 저장
# tar czf: 압축해서 저장
```

### 방법 2: 백업에서 복원

```bash
# ── 볼륨 복원 ──
docker run --rm \
  -v vol-db-data:/target \
  -v $(pwd)/backup:/backup:ro \
  alpine \
  sh -c "cd /target && tar xzf /backup/db-backup-20260321.tar.gz"

# 설명:
# -v vol-db-data:/target: 복원할 대상 볼륨
# tar xzf: 압축 풀기
```

### 방법 3: DB 전용 백업 (pg_dump)

```bash
# PostgreSQL 데이터베이스 백업 (추천!)
docker-compose exec db pg_dump -U admin volumetest > backup.sql

# 복원
docker-compose exec -T db psql -U admin volumetest < backup.sql
```

## 5. 네트워크 종류별 비교표

| 드라이버 | 설명 | 사용 사례 | 격리 수준 |
|---------|------|----------|----------|
| **bridge** | 같은 호스트의 컨테이너끼리 통신 | 대부분의 경우 (기본) | 중간 |
| **host** | 호스트 네트워크 직접 사용 | 최대 성능 필요할 때 | 없음 |
| **overlay** | 여러 호스트 간 통신 | Docker Swarm 클러스터 | 높음 |
| **macvlan** | 컨테이너에 MAC 주소 부여 | 물리 네트워크 연결 필요 시 | 높음 |
| **none** | 네트워크 없음 | 완전 격리 필요 시 | 완전 격리 |

### 각 네트워크 드라이버 설명

```
1. bridge (다리)
   ┌─────────────────────────────┐
   │     Docker Bridge Network    │
   │                              │
   │  컨테이너A ←──→ 컨테이너B    │
   │      │                       │
   │      └───→ 외부 인터넷       │
   └─────────────────────────────┘
   → 기본값. 같은 네트워크의 컨테이너끼리 통신 가능

2. host (호스트)
   ┌─────────────────────────────┐
   │         호스트 네트워크        │
   │                              │
   │  호스트 ←──→ 컨테이너         │
   │  (같은 네트워크를 공유)        │
   └─────────────────────────────┘
   → 포트 매핑 필요 없음 (성능 최대)
   → 보안은 약해짐

3. overlay (오버레이)
   ┌──────────┐    ┌──────────┐
   │  호스트1   │    │  호스트2   │
   │ 컨테이너A  │←──→│ 컨테이너B  │
   └──────────┘    └──────────┘
   → 서로 다른 서버의 컨테이너끼리 통신
   → Docker Swarm에서 사용
```

## 6. 네트워크 관리 명령어

```bash
# ── 네트워크 생성 ──
docker network create my-network                   # 기본 bridge 네트워크
docker network create --driver overlay my-overlay   # overlay 네트워크
docker network create --subnet 172.30.0.0/16 my-net # IP 대역 지정

# ── 네트워크 목록 ──
docker network ls                                   # 모든 네트워크 보기

# ── 네트워크 상세 정보 ──
docker network inspect my-network                   # 연결된 컨테이너, IP 등

# ── 컨테이너를 네트워크에 연결/분리 ──
docker network connect my-network my-container      # 연결
docker network disconnect my-network my-container   # 분리

# ── 네트워크 삭제 ──
docker network rm my-network                        # 특정 네트워크 삭제
docker network prune                                # 사용 안 하는 네트워크 전부 삭제
```

## 7. Docker DNS (이름으로 통신하기)

```
Docker는 내장 DNS 서버를 제공해 (127.0.0.11)

같은 네트워크에 있는 컨테이너끼리는
서비스 이름 또는 컨테이너 이름으로 서로 찾을 수 있어!

예시:
  web 컨테이너에서 "db"로 접속하면
  Docker DNS가 db 컨테이너의 IP를 알려줘

  ping db          → db 컨테이너의 IP로 변환
  ping redis       → redis 컨테이너의 IP로 변환

주의:
  기본 bridge 네트워크(docker0)에서는 DNS가 안 돼!
  반드시 사용자 정의 네트워크를 만들어야 DNS가 작동해!
```

## 8. 이 프로젝트 실습

```bash
# 1. 시작
cd 03_volumes_networks/
docker-compose up -d

# 2. 볼륨 확인
docker volume ls                              # 생성된 볼륨 목록
docker volume inspect vol-db-data             # 볼륨 상세 정보

# 3. 네트워크 확인
docker network ls                             # 생성된 네트워크 목록
docker network inspect vol-net-backend        # 연결된 컨테이너 확인

# 4. DNS 테스트 결과 확인
docker logs dns-tester                        # DNS 조회 결과 보기

# 5. 데이터 영속성 테스트
docker-compose exec db psql -U admin volumetest -c "SELECT 1;"
docker-compose down                           # 종료 (볼륨은 남아있음!)
docker-compose up -d                          # 다시 시작 → 데이터 그대로!

# 6. 완전 정리 (볼륨까지 삭제)
docker-compose down -v
```

## 9. 자주 하는 실수

| 실수 | 문제 | 해결 |
|------|------|------|
| `docker-compose down -v` 실수 | 볼륨 데이터 날아감 | 백업 먼저! `-v` 조심 |
| Bind mount 경로 오타 | 빈 폴더가 마운트됨 | 절대 경로 사용 확인 |
| 기본 bridge에서 DNS 사용 | 이름으로 통신 안 됨 | 사용자 정의 네트워크 사용 |
| 볼륨 권한 문제 | Permission denied | USER 설정 또는 chown 필요 |
| Windows에서 bind mount | 성능 저하 | WSL2 백엔드 사용 |
