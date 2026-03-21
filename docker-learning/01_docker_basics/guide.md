# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# ■ 파일명: guide.md
# ■ 목적: Docker 기초 완벽 가이드 (한국어)
# ■ 설명: 설치부터 기본 명령어까지 모든 것
# ■ 날짜: 2026-03-21
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# Docker 기초 완벽 가이드

## 1. Docker가 뭐야?

Docker는 **앱을 상자(컨테이너)에 넣어서 어디서든 똑같이 실행**할 수 있게 해주는 도구야.

생각해봐:
- 내 컴퓨터에서는 되는데 다른 컴퓨터에서는 안 되는 경우 있지?
- Python 버전이 달라서 에러가 나는 경우도 있고
- 이런 문제를 Docker가 해결해줘!

**컨테이너 = 앱 + 필요한 모든 것(라이브러리, 설정, OS)을 하나의 상자에 담은 것**

## 2. Docker 설치

### Windows
```bash
# 1. Docker Desktop 다운로드
# https://www.docker.com/products/docker-desktop/

# 2. WSL2 백엔드 활성화 (설치 시 자동으로 됨)

# 3. 설치 확인
docker --version          # Docker 버전 확인
docker-compose --version  # Docker Compose 버전 확인
```

### macOS
```bash
# 1. Docker Desktop 다운로드
# https://www.docker.com/products/docker-desktop/

# 2. 또는 Homebrew로 설치
brew install --cask docker

# 3. 설치 확인
docker --version
```

### Linux (Ubuntu)
```bash
# 1. 이전 버전 제거
sudo apt-get remove docker docker-engine docker.io containerd runc

# 2. 필요한 패키지 설치
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg lsb-release

# 3. Docker 공식 GPG 키 추가
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 4. Docker 저장소 추가
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. Docker 설치
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 6. sudo 없이 사용하기
sudo usermod -aG docker $USER
# (로그아웃 후 다시 로그인)

# 7. 설치 확인
docker run hello-world
```

## 3. 이미지 vs 컨테이너 (가장 중요한 개념!)

```
이미지 (Image)                  컨테이너 (Container)
━━━━━━━━━━━━━━━━━━━━          ━━━━━━━━━━━━━━━━━━━━━━
- 설계도 / 레시피               - 설계도로 만든 실제 건물
- 읽기 전용 (변경 불가)          - 읽기 + 쓰기 가능
- docker images 로 확인         - docker ps 로 확인
- 여러 컨테이너를 만들 수 있음    - 하나의 실행 인스턴스
- Docker Hub에서 다운로드         - 이미지로부터 생성

비유:
  이미지 = 붕어빵 틀
  컨테이너 = 붕어빵 틀로 만든 붕어빵 (여러 개 만들 수 있어!)
```

## 4. 레이어 개념

```
Docker 이미지는 여러 개의 레이어(층)으로 이루어져 있어:

┌─────────────────────┐
│ CMD ["python",      │  ← 레이어 5: 실행 명령어
│      "app.py"]      │
├─────────────────────┤
│ COPY app.py .       │  ← 레이어 4: 소스코드 복사
├─────────────────────┤
│ RUN pip install     │  ← 레이어 3: 패키지 설치
│     flask           │
├─────────────────────┤
│ COPY requirements   │  ← 레이어 2: 요구사항 파일
│      .txt .         │
├─────────────────────┤
│ FROM python:3.12    │  ← 레이어 1: 기본 이미지
└─────────────────────┘

왜 레이어가 중요할까?
→ 변경된 레이어부터 다시 빌드해 (캐싱!)
→ requirements.txt가 안 바뀌면 pip install을 다시 안 해도 돼
→ 그래서 자주 바뀌는 파일(소스코드)은 아래쪽(나중)에 COPY 해야 해!
```

## 5. 기본 명령어 총정리

### 이미지 관련 명령어

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `docker pull` | 이미지 다운로드 | `docker pull python:3.12` |
| `docker images` | 이미지 목록 보기 | `docker images` |
| `docker build` | 이미지 만들기 | `docker build -t myapp .` |
| `docker rmi` | 이미지 삭제 | `docker rmi myapp` |
| `docker tag` | 이미지에 태그 붙이기 | `docker tag myapp myapp:v2` |
| `docker push` | 이미지 업로드 | `docker push myuser/myapp` |
| `docker history` | 이미지 레이어 보기 | `docker history myapp` |
| `docker inspect` | 이미지 상세 정보 | `docker inspect myapp` |

### 컨테이너 관련 명령어

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `docker run` | 컨테이너 생성+실행 | `docker run -d -p 8000:8000 myapp` |
| `docker ps` | 실행 중인 컨테이너 보기 | `docker ps` |
| `docker ps -a` | 모든 컨테이너 보기 | `docker ps -a` |
| `docker stop` | 컨테이너 정지 | `docker stop mycontainer` |
| `docker start` | 정지된 컨테이너 시작 | `docker start mycontainer` |
| `docker restart` | 컨테이너 재시작 | `docker restart mycontainer` |
| `docker rm` | 컨테이너 삭제 | `docker rm mycontainer` |
| `docker logs` | 로그 보기 | `docker logs -f mycontainer` |
| `docker exec` | 컨테이너 안에서 명령 실행 | `docker exec -it mycontainer bash` |
| `docker cp` | 파일 복사 | `docker cp file.txt container:/path` |
| `docker stats` | 리소스 사용량 보기 | `docker stats` |

### docker run 옵션 상세

```bash
docker run \
  -d                          # 백그라운드 실행 (detached mode)
  --name myapp                # 컨테이너 이름 지정
  -p 8000:8000                # 포트 연결 (호스트:컨테이너)
  -v /host/path:/container    # 볼륨 마운트
  -e MY_VAR=hello             # 환경변수 설정
  --network mynetwork         # 네트워크 연결
  --restart unless-stopped    # 재시작 정책
  --memory 512m               # 메모리 제한
  --cpus 1.5                  # CPU 제한
  myimage:latest              # 사용할 이미지
```

### 정리(cleanup) 명령어

```bash
# 사용하지 않는 것들 한 번에 정리
docker system prune           # 멈춘 컨테이너, 안 쓰는 네트워크, 댕글링 이미지 삭제
docker system prune -a        # 위 + 사용하지 않는 모든 이미지 삭제
docker volume prune           # 사용하지 않는 볼륨 삭제

# 개별 정리
docker container prune        # 멈춘 컨테이너만 삭제
docker image prune            # 댕글링 이미지만 삭제
docker network prune          # 사용하지 않는 네트워크만 삭제
```

## 6. 실습: 이 프로젝트 실행하기

### 방법 1: docker-compose 사용 (추천!)
```bash
# 1. 이 디렉토리로 이동
cd 01_docker_basics/

# 2. 이미지 빌드 + 컨테이너 시작
docker-compose up -d --build

# 3. 브라우저에서 확인
# http://localhost:8000

# 4. 로그 확인
docker-compose logs -f

# 5. 컨테이너 안에 들어가기
docker-compose exec web bash

# 6. 종료
docker-compose down

# 7. 볼륨까지 삭제하며 종료
docker-compose down -v
```

### 방법 2: docker 명령어만 사용
```bash
# 1. 네트워크 만들기
docker network create app-network

# 2. Redis 실행
docker run -d \
  --name learning-redis \
  --network app-network \
  redis:7-alpine

# 3. 이미지 빌드
docker build -t docker-learning-web .

# 4. 웹 앱 실행
docker run -d \
  --name learning-web \
  --network app-network \
  -p 8000:8000 \
  -e REDIS_HOST=learning-redis \
  docker-learning-web

# 5. 확인
docker ps
docker logs learning-web

# 6. 정리
docker stop learning-web learning-redis
docker rm learning-web learning-redis
docker network rm app-network
```

## 7. 자주 쓰는 명령어 치트시트

```bash
# ──── 이미지 ────
docker build -t 이름:태그 .              # 이미지 빌드
docker pull 이미지:태그                   # 이미지 다운로드
docker images                            # 이미지 목록
docker rmi 이미지                        # 이미지 삭제

# ──── 컨테이너 ────
docker run -d -p 8080:80 nginx           # Nginx 실행
docker ps                                # 실행 중인 것 보기
docker ps -a                             # 전부 보기
docker stop $(docker ps -q)              # 모든 컨테이너 정지
docker rm $(docker ps -aq)               # 모든 컨테이너 삭제

# ──── 디버깅 ────
docker logs -f --tail 100 컨테이너       # 마지막 100줄 로그 + 실시간
docker exec -it 컨테이너 sh              # 컨테이너 안에 접속
docker inspect 컨테이너                  # 상세 정보 확인
docker stats                             # 실시간 리소스 모니터링

# ──── Docker Compose ────
docker-compose up -d                     # 시작 (백그라운드)
docker-compose up -d --build             # 빌드 후 시작
docker-compose down                      # 종료
docker-compose down -v                   # 종료 + 볼륨 삭제
docker-compose logs -f 서비스            # 특정 서비스 로그
docker-compose exec 서비스 명령어        # 서비스에서 명령 실행
docker-compose ps                        # 서비스 상태 확인
```

## 8. 흔한 실수와 해결법

| 실수 | 해결법 |
|------|--------|
| `port is already allocated` | 해당 포트를 사용 중인 프로세스 종료 또는 다른 포트 사용 |
| `image not found` | `docker pull`로 이미지 먼저 다운로드 |
| `permission denied` | Linux에서 `sudo` 사용 또는 docker 그룹에 추가 |
| `no space left on device` | `docker system prune -a`로 정리 |
| `container already exists` | `docker rm 컨테이너이름`으로 기존 것 삭제 |
| 컨테이너가 바로 종료됨 | `docker logs`로 에러 확인, 포그라운드 프로세스 필요 |
