# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# ■ 파일명: guide.md
# ■ 목적: 개발 vs 프로덕션 설정 차이와 배포 전략
# ■ 설명: 환경별 설정, 롤링 업데이트, Blue-Green, 트러블슈팅
# ■ 날짜: 2026-03-21
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# 프로덕션 패턴 가이드

## 1. 개발 vs 프로덕션 설정 차이

| 항목 | 개발 (dev) | 프로덕션 (prod) |
|------|-----------|----------------|
| **소스코드** | 바인드 마운트 (실시간 반영) | 이미지에 포함 (고정) |
| **핫 리로드** | 활성화 | 비활성화 |
| **디버그 포트** | 열어둠 (5678) | 닫아둠 |
| **로그 레벨** | DEBUG (모든 것) | INFO/WARNING |
| **DB 포트** | 외부 공개 (직접 접근) | 내부만 (보안) |
| **비밀번호** | 간단 (devpassword) | 복잡 + 시크릿 관리 |
| **리소스 제한** | 없음 | CPU/메모리 제한 |
| **재시작 정책** | no (직접 확인) | always/on-failure |
| **이미지 태그** | latest | 특정 버전 (v1.2.3) |
| **관리 도구** | Adminer, Redis Commander | 없음 (보안!) |
| **파일시스템** | 읽기+쓰기 | read_only |
| **보안 옵션** | 기본 | no-new-privileges |
| **헬스체크** | 선택사항 | 필수 |
| **로그 용량** | 무제한 | 제한 (max-size) |
| **네트워크** | 하나로 통합 | 분리 (frontend/backend) |

## 2. 환경별 실행 방법

```bash
# ── 개발 환경 실행 ──
docker-compose -f docker-compose.dev.yml up -d

# ── 프로덕션 환경 실행 ──
docker-compose -f docker-compose.prod.yml up -d

# ── 두 파일 합쳐서 실행 (오버라이드) ──
# base 파일 + override 파일
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
# 뒤의 파일이 앞의 파일 설정을 덮어써!
```

## 3. 배포 전략

### 3.1 롤링 업데이트 (Rolling Update)

```
하나씩 순차적으로 업데이트하는 방식

시간 →
서버1: [v1] [v1] [v2 설치중] [v2] [v2] [v2]
서버2: [v1] [v1] [v1]       [v1] [v2 설치중] [v2]
서버3: [v1] [v1] [v1]       [v1] [v1]       [v2]

장점: 무중단 배포, 리소스 적게 필요
단점: v1과 v2가 동시에 실행되는 시간이 있어

Docker Compose에서:
docker-compose up -d --no-deps --build web
# --no-deps = 의존 서비스 재시작 안 함
# web만 새 버전으로 업데이트
```

### 3.2 Blue-Green 배포

```
두 개의 환경을 준비하고 한 번에 전환

┌──────────────┐        ┌──────────────┐
│  Blue (v1)   │  현재   │  Green (v2)  │  대기
│  ● 운영 중    │←──────│  ● 준비 완료   │
└──────────────┘  전환!  └──────────────┘
                  │
                  ▼
┌──────────────┐        ┌──────────────┐
│  Blue (v1)   │  대기   │  Green (v2)  │  현재
│  ● 정지       │──────→│  ● 운영 중    │
└──────────────┘        └──────────────┘

장점: 즉시 전환, 문제 시 즉시 롤백
단점: 리소스 2배 필요
```

```bash
# Blue-Green 실행 예시:
# 1. Blue 실행 중 (현재 운영)
docker-compose -f docker-compose.blue.yml up -d

# 2. Green 준비 (새 버전)
docker-compose -f docker-compose.green.yml up -d

# 3. 테스트 후 Nginx 설정 변경 (Green으로 전환)
# nginx.conf의 upstream을 green으로 변경

# 4. 문제 있으면 다시 Blue로 전환 (즉시 롤백!)
```

### 3.3 Canary 배포

```
소수의 사용자에게만 새 버전을 노출

트래픽:  90%        10%
         ▼          ▼
┌──────────┐   ┌──────────┐
│  v1 (기존) │   │  v2 (새)  │
│  9대 서버  │   │  1대 서버  │
└──────────┘   └──────────┘

문제 없으면 점진적으로 v2 비율 증가:
80% v1 + 20% v2 → 50% + 50% → 100% v2
```

## 4. 트러블슈팅 가이드

### 4.1 컨테이너가 시작 안 될 때

```bash
# 1. 로그 확인 (가장 먼저!)
docker-compose logs 서비스명

# 2. 종료 코드 확인
docker inspect --format='{{.State.ExitCode}}' 컨테이너명
# 0 = 정상 종료, 1 = 에러, 137 = OOM (메모리 부족), 143 = SIGTERM

# 3. 이벤트 확인
docker events --since 10m

# 4. 컨테이너 안에서 직접 확인
docker run -it --entrypoint sh myimage
# 이미지를 셸로 시작해서 문제를 찾아
```

### 4.2 메모리 부족 (OOM Kill)

```bash
# 증상: 컨테이너가 갑자기 종료, exit code 137

# 확인:
docker inspect --format='{{.State.OOMKilled}}' 컨테이너명
# true면 메모리 부족으로 죽은 거야

# 해결:
# 1. deploy.resources.limits.memory 값 늘리기
# 2. 앱의 메모리 누수 확인
# 3. docker stats로 실시간 메모리 사용량 모니터링
docker stats
```

### 4.3 네트워크 연결 문제

```bash
# 1. 컨테이너 IP 확인
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 컨테이너명

# 2. DNS 해석 확인
docker exec 컨테이너명 nslookup 서비스명

# 3. 연결 테스트
docker exec 컨테이너명 ping -c 3 서비스명
docker exec 컨테이너명 curl http://서비스명:포트/

# 4. 네트워크 확인
docker network inspect 네트워크명
```

### 4.4 볼륨/권한 문제

```bash
# 1. 볼륨 확인
docker volume inspect 볼륨명

# 2. 파일 권한 확인
docker exec 컨테이너명 ls -la /path/to/dir

# 3. 소유자 변경
docker exec 컨테이너명 chown -R app:app /path/to/dir

# 4. Dockerfile에서 미리 설정
COPY --chown=app:app . /app
```

### 4.5 이미지 빌드 문제

```bash
# 1. 캐시 없이 빌드
docker-compose build --no-cache

# 2. 특정 스테이지까지만 빌드
docker build --target builder -t myapp:builder .

# 3. 빌드 로그 자세히 보기
docker build --progress=plain -t myapp .

# 4. .dockerignore 확인
# 필요한 파일이 ignore되고 있진 않은지 확인
```

## 5. 프로덕션 체크리스트

```
배포 전 확인사항:

□ 이미지 태그가 특정 버전인가? (latest 사용 금지)
□ 환경변수에 비밀번호가 하드코딩 되어있진 않은가?
□ 모든 서비스에 healthcheck가 설정되어 있는가?
□ 리소스 제한 (CPU, Memory)이 설정되어 있는가?
□ 로그 용량 제한이 설정되어 있는가?
□ 재시작 정책이 설정되어 있는가?
□ DB 포트가 외부에 노출되어 있진 않은가?
□ non-root 사용자로 실행하는가?
□ 불필요한 관리 도구 (Adminer 등)는 제거했는가?
□ 볼륨 백업 계획이 있는가?
□ 모니터링/알림이 설정되어 있는가?
□ 롤백 계획이 있는가?
```

## 6. 유용한 Docker 명령어

```bash
# ── 리소스 사용량 실시간 모니터링 ──
docker stats

# ── 디스크 사용량 확인 ──
docker system df
docker system df -v              # 상세 정보

# ── 전체 정리 ──
docker system prune -a --volumes  # 모든 불필요한 것 삭제 (주의!)

# ── 이미지 취약점 스캔 ──
docker scout cves myapp:1.0.0

# ── 컨테이너 내부 프로세스 확인 ──
docker top 컨테이너명

# ── 컨테이너 변경사항 확인 ──
docker diff 컨테이너명            # 이미지 대비 변경된 파일 목록
```
