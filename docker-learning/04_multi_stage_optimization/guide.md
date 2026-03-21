# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# ■ 파일명: guide.md
# ■ 목적: 멀티스테이지 빌드와 이미지 최적화 가이드
# ■ 설명: 빌드 전략, .dockerignore, 레이어 캐싱
# ■ 날짜: 2026-03-21
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# 멀티스테이지 빌드와 이미지 최적화 가이드

## 1. 멀티스테이지 빌드란?

```
Dockerfile 하나에 여러 개의 FROM을 쓰는 기법이야

┌─────────────────────────────────────────────┐
│  스테이지 1: 빌더 (Builder)                   │
│  ┌─────────────────────────────────────┐     │
│  │ 기본 이미지 (큰 것)                    │     │
│  │ + 빌드 도구 (gcc, npm, javac)         │     │
│  │ + 소스코드                            │     │
│  │ + 의존성                              │     │
│  │ = 빌드 결과물 (바이너리, 정적 파일)      │     │
│  └──────────────────┬──────────────────┘     │
│                     │ 필요한 것만 복사          │
│  스테이지 2: 프로덕션 ▼                        │
│  ┌─────────────────────────────────────┐     │
│  │ 기본 이미지 (작은 것)                   │     │
│  │ + 빌드 결과물만!                       │     │
│  │ = 최종 이미지 (작고 안전)               │     │
│  └─────────────────────────────────────┘     │
└─────────────────────────────────────────────┘
```

## 2. 언어별 이미지 크기 비교

| 언어 | 일반 빌드 | 멀티스테이지 | 감소율 |
|------|----------|------------|--------|
| Python | ~900MB | ~150MB | 83% |
| Node.js | ~1GB | ~30MB | 97% |
| Go | ~800MB | ~10MB | 99% |
| Java | ~600MB | ~200MB | 67% |
| Rust | ~1.5GB | ~10MB | 99% |

## 3. 기본 이미지 선택 가이드

```
이미지 크기 비교 (Python 기준):

python:3.12         ~900MB  ← 풀 이미지 (빌드 도구 포함)
python:3.12-slim    ~150MB  ← 슬림 (필수만 포함, 추천!)
python:3.12-alpine   ~50MB  ← 초소형 (호환성 문제 가능)

정리:
┌────────────┬─────────┬──────────┬──────────────┐
│ 이미지 태그  │ 크기     │ 패키지    │ 사용 사례      │
├────────────┼─────────┼──────────┼──────────────┤
│ :latest    │ 가장 큼  │ 풀 패키지  │ 빌드 스테이지   │
│ :slim      │ 중간     │ 최소 필수  │ 프로덕션 (추천) │
│ :alpine    │ 가장 작음 │ musl libc │ 초경량 필요 시  │
│ scratch    │ 0 바이트  │ 없음      │ Go, Rust     │
│ distroless │ 매우 작음 │ 없음      │ 보안 최우선    │
└────────────┴─────────┴──────────┴──────────────┘

Alpine 주의사항:
- musl libc 사용 (glibc가 아님) → 일부 패키지 호환 안 됨
- Python wheels가 없어서 소스 컴파일 필요 → 빌드 시간 증가
```

## 4. .dockerignore 파일

```
.dockerignore = Docker 빌드 시 무시할 파일/폴더 목록
.gitignore와 비슷한 역할이야!

없으면: COPY . . 할 때 node_modules, .git 등 불필요한 파일까지 복사
있으면: 필요한 파일만 복사 → 빌드 빠르고 이미지 작아!
```

### .dockerignore 예시

```dockerignore
# Git 관련
.git
.gitignore

# 의존성 (컨테이너에서 다시 설치)
node_modules
__pycache__
*.pyc
.venv
vendor

# IDE 설정
.idea
.vscode
*.swp

# Docker 관련
Dockerfile*
docker-compose*
.dockerignore

# 문서 (실행에 불필요)
README.md
docs/
*.md

# 테스트
tests/
test/
coverage/

# 환경 파일 (보안!)
.env
.env.local
*.pem
*.key

# OS 관련
.DS_Store
Thumbs.db

# 로그
*.log
logs/
```

## 5. 레이어 캐싱 최적화

### 나쁜 예 (캐싱 비효율)
```dockerfile
# 소스코드가 바뀌면 pip install도 다시 실행됨!
COPY . .
RUN pip install -r requirements.txt
```

### 좋은 예 (캐싱 최적화)
```dockerfile
# 1. 의존성 파일만 먼저 복사
COPY requirements.txt .
# 2. 패키지 설치 (requirements.txt가 안 바뀌면 캐시 사용!)
RUN pip install -r requirements.txt
# 3. 소스코드는 나중에 복사 (자주 바뀌는 것은 마지막에!)
COPY . .
```

### 캐싱 동작 원리
```
레이어 1: FROM python:3.12     → 캐시 ✅ (바뀔 일 없음)
레이어 2: COPY requirements.txt → 캐시 ✅ (파일 안 바뀜)
레이어 3: RUN pip install       → 캐시 ✅ (위가 안 바뀌니까)
레이어 4: COPY . .              → 변경됨 ❌ (소스 수정)
레이어 5: CMD ["python", ...]   → 다시 빌드 (위가 바뀌어서)

결과: pip install은 캐시에서! 빌드 시간 대폭 단축!
```

## 6. 추가 최적화 팁

### RUN 명령어 합치기
```dockerfile
# 나쁜 예: 레이어 3개 생성
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# 좋은 예: 레이어 1개 생성
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*
```

### 캐시 삭제
```dockerfile
# pip 캐시 삭제
RUN pip install --no-cache-dir -r requirements.txt

# apt 캐시 삭제
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# npm 캐시 삭제
RUN npm ci --omit=dev && npm cache clean --force
```

## 7. 이미지 크기 확인 명령어

```bash
# 이미지 크기 보기
docker images

# 이미지 레이어별 크기 보기
docker history myimage:latest

# 이미지 상세 분석 (dive 도구 추천!)
# dive = 레이어별 파일 변경사항을 시각적으로 보여주는 도구
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  wagoodman/dive:latest myimage:latest
```

## 8. 빌드 및 비교 실습

```bash
# 각 Dockerfile 빌드
docker build -f Dockerfile.python -t python-opt .
docker build -f Dockerfile.node -t node-opt .
docker build -f Dockerfile.go -t go-opt .
docker build -f Dockerfile.java -t java-opt .

# 크기 비교
docker images | grep opt

# 레이어 분석
docker history python-opt
docker history go-opt
```
