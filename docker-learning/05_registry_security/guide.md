# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# ■ 파일명: guide.md
# ■ 목적: Docker 레지스트리와 보안 가이드
# ■ 설명: Docker Hub, 프라이빗 레지스트리, 태깅 전략, 보안
# ■ 날짜: 2026-03-21
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# Docker 레지스트리와 보안 가이드

## 1. Docker Registry란?

```
레지스트리 = Docker 이미지를 저장하는 창고

GitHub가 코드를 저장하듯이,
Docker Registry는 Docker 이미지를 저장해

┌──────────────┐     push     ┌──────────────┐
│ 내 컴퓨터      │ ──────────→ │  Registry     │
│ (이미지 빌드)  │             │  (이미지 저장) │
│              │ ←────────── │              │
└──────────────┘     pull     └──────────────┘
```

## 2. 레지스트리 종류

| 종류 | 설명 | URL | 가격 |
|------|------|-----|------|
| **Docker Hub** | 가장 큰 공개 레지스트리 | hub.docker.com | 무료/유료 |
| **GitHub GHCR** | GitHub 연동 레지스트리 | ghcr.io | 무료/유료 |
| **AWS ECR** | AWS 클라우드 레지스트리 | *.dkr.ecr.*.amazonaws.com | 유료 |
| **GCP GCR** | Google 클라우드 레지스트리 | gcr.io | 유료 |
| **Azure ACR** | Azure 클라우드 레지스트리 | *.azurecr.io | 유료 |
| **Self-hosted** | 직접 운영 (registry:2) | localhost:5000 | 무료 |

## 3. Docker Hub 사용법

```bash
# ── 로그인 ──
docker login
# Username: myuser
# Password: ****

# ── 이미지 태깅 ──
# Docker Hub에 올리려면 "사용자명/이미지명:태그" 형식이 필요해
docker tag myapp:latest myuser/myapp:1.0.0
docker tag myapp:latest myuser/myapp:latest

# ── 이미지 업로드 (Push) ──
docker push myuser/myapp:1.0.0
docker push myuser/myapp:latest

# ── 이미지 다운로드 (Pull) ──
docker pull myuser/myapp:1.0.0

# ── 로그아웃 ──
docker logout
```

## 4. 프라이빗 레지스트리 사용법

```bash
# ── 1. 레지스트리 시작 ──
cd 05_registry_security/
docker-compose up -d

# ── 2. 이미지 태깅 (localhost:5000/ 접두사 필요!) ──
docker tag myapp:latest localhost:5000/myapp:1.0.0

# ── 3. 이미지 Push ──
docker push localhost:5000/myapp:1.0.0

# ── 4. 이미지 Pull ──
docker pull localhost:5000/myapp:1.0.0

# ── 5. 레지스트리에 있는 이미지 목록 보기 ──
curl http://localhost:5000/v2/_catalog
# 결과: {"repositories":["myapp"]}

# ── 6. 특정 이미지의 태그 목록 ──
curl http://localhost:5000/v2/myapp/tags/list
# 결과: {"name":"myapp","tags":["1.0.0"]}

# ── 7. 웹 UI로 확인 ──
# 브라우저에서 http://localhost:8080 접속!
```

## 5. 이미지 태깅 전략 (Semantic Versioning)

```
Semantic Versioning (SemVer): MAJOR.MINOR.PATCH

  v1.2.3
  │ │ └─ PATCH: 버그 수정 (하위 호환)
  │ └─── MINOR: 기능 추가 (하위 호환)
  └───── MAJOR: 큰 변경 (하위 호환 깨짐)

태깅 전략:
┌──────────────────────────────────────────────┐
│  하나의 빌드에 여러 태그를 붙여!               │
│                                              │
│  docker tag myapp:latest myapp:1.2.3         │
│  docker tag myapp:latest myapp:1.2           │
│  docker tag myapp:latest myapp:1             │
│  docker tag myapp:latest myapp:latest        │
│                                              │
│  → myapp:1.2.3 = 정확한 버전 (프로덕션 추천)  │
│  → myapp:1.2   = 1.2.x 중 최신              │
│  → myapp:1     = 1.x.x 중 최신              │
│  → myapp:latest = 가장 최신 (개발용)          │
└──────────────────────────────────────────────┘
```

### 태그 사용 규칙

| 태그 | 사용 시점 | 안정성 |
|------|----------|--------|
| `myapp:1.2.3` | 프로덕션 배포 | 가장 안정 (고정 버전) |
| `myapp:1.2` | 스테이징 환경 | 패치 업데이트 자동 |
| `myapp:latest` | 개발/테스트 | 불안정 (뭐가 올지 모름) |
| `myapp:dev` | 개발 전용 | 가장 불안정 |
| `myapp:sha-abc123` | CI/CD | 정확한 커밋 추적 |

## 6. Docker 보안 가이드

### 6.1 Rootless (비루트 실행)

```dockerfile
# 나쁜 예: root로 실행 (기본값)
FROM python:3.12
COPY . /app
CMD ["python", "app.py"]
# → 해커가 침입하면 root 권한을 가짐!

# 좋은 예: 일반 사용자로 실행
FROM python:3.12
RUN groupadd -r app && useradd -r -g app app
COPY --chown=app:app . /app
USER app
CMD ["python", "app.py"]
# → 해커가 침입해도 제한된 권한만 가짐
```

### 6.2 Read-only 파일시스템

```yaml
# docker-compose.yml에서:
services:
  web:
    image: myapp
    read_only: true            # 파일시스템을 읽기 전용으로!
    tmpfs:
      - /tmp                   # 쓰기가 필요한 곳만 tmpfs로 허용
      - /var/run
```

### 6.3 시크릿 관리

```yaml
# 나쁜 예: 환경변수에 비밀번호 직접 기재
environment:
  - DB_PASSWORD=mysecretpassword    # 코드에 비밀번호가 남아!

# 좋은 예 1: .env 파일 사용 (.gitignore에 추가!)
env_file:
  - .env                           # .env 파일에서 읽기

# 좋은 예 2: Docker Secrets 사용 (Swarm 모드)
secrets:
  db_password:
    file: ./secrets/db_password.txt  # 파일에서 읽기

# 좋은 예 3: 외부 시크릿 관리 도구
# - HashiCorp Vault
# - AWS Secrets Manager
# - Azure Key Vault
```

### 6.4 이미지 보안 스캔

```bash
# Docker Scout로 취약점 스캔
docker scout cves myapp:latest

# Trivy로 스캔 (추천!)
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image myapp:latest
```

### 6.5 보안 체크리스트

```
□ USER 명령어로 non-root 사용자 지정
□ 최신 기본 이미지 사용 (보안 패치 포함)
□ 불필요한 패키지 설치하지 않기
□ 멀티스테이지 빌드로 빌드 도구 제거
□ .dockerignore로 민감한 파일 제외
□ 이미지 취약점 스캔 실행
□ COPY 사용 (ADD 대신 - URL 다운로드 방지)
□ 환경변수에 비밀번호 하드코딩 하지 않기
□ read_only 파일시스템 사용 검토
□ 리소스 제한 설정 (memory, cpu)
□ 헬스체크 설정
□ 로그에 민감한 정보 남기지 않기
```

## 7. Dockerfile 보안 모범 사례

```dockerfile
# ── 좋은 Dockerfile 예시 ──

# 1. 특정 버전 사용 (latest 지양)
FROM python:3.12.1-slim

# 2. 라벨로 정보 기록
LABEL maintainer="team@company.com"

# 3. 불필요한 권한 제거
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/* && \
    # 4. 불필요한 사용자 제거
    deluser --remove-home daemon

# 5. 비루트 사용자 생성
RUN groupadd -r app && useradd -r -g app -d /app app

# 6. 소유권 설정
COPY --chown=app:app . /app
WORKDIR /app

# 7. 패키지 캐시 없이 설치
RUN pip install --no-cache-dir -r requirements.txt

# 8. 헬스체크 설정
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1

# 9. 비루트 사용자로 전환
USER app

# 10. exec form 사용 (shell form 지양)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

## 8. 실습

```bash
# 1. 프라이빗 레지스트리 시작
cd 05_registry_security/
docker-compose up -d

# 2. 테스트 이미지 만들기
docker pull nginx:alpine
docker tag nginx:alpine localhost:5000/my-nginx:1.0

# 3. Push
docker push localhost:5000/my-nginx:1.0

# 4. 레지스트리 확인
curl http://localhost:5000/v2/_catalog

# 5. 웹 UI 확인
# 브라우저: http://localhost:8080

# 6. 종료
docker-compose down -v
```
