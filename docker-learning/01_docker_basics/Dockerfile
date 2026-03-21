# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# ■ 파일명: Dockerfile
# ■ 목적: Docker의 모든 명령어를 배우는 종합 Dockerfile
# ■ 설명: FROM부터 HEALTHCHECK까지, 멀티스테이지 빌드 포함
# ■ 날짜: 2026-03-21
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ============================================================
# 🔷 스테이지 1: 빌더 (Builder Stage)
# ============================================================
# 멀티스테이지 빌드란?
# → 이미지를 만드는 과정을 여러 단계로 나누는 것이야
# → 첫 번째 단계에서 만들고, 두 번째 단계에서 필요한 것만 가져가
# → 그러면 최종 이미지가 아주 작아져! (불필요한 것 제거)

# ── FROM: 기본 이미지를 정하는 명령어 ──
# 모든 Dockerfile은 반드시 FROM으로 시작해야 해
# "python:3.12-slim" = Python 3.12가 설치된 가벼운 리눅스
# "AS builder" = 이 단계에 "builder"라는 이름을 붙여줘
#   → 나중에 이 단계에서 만든 파일을 가져올 수 있어
FROM python:3.12-slim AS builder

# ── LABEL: 이미지에 정보 태그 붙이기 ──
# 이미지를 만든 사람, 버전, 설명 등을 적어두는 거야
# 실행에는 영향 없지만, 이미지를 관리할 때 아주 유용해
# docker inspect 명령어로 이 정보를 볼 수 있어
LABEL maintainer="student@example.com"
LABEL version="1.0.0"
LABEL description="Docker 학습용 Python 웹 애플리케이션"
LABEL org.opencontainers.image.source="https://github.com/example/docker-learning"

# ── ARG: 빌드할 때만 사용하는 변수 ──
# ARG는 이미지를 "만들 때"만 쓰이는 변수야
# 컨테이너가 실행될 때는 이 변수를 사용할 수 없어
# docker build --build-arg APP_VERSION=2.0.0 . 이렇게 값을 바꿀 수 있어
ARG APP_VERSION=1.0.0
ARG PIP_INDEX_URL=https://pypi.org/simple

# ── ENV: 실행할 때도 사용하는 환경변수 ──
# ENV는 이미지를 만들 때도, 컨테이너가 실행될 때도 쓰여
# ARG와의 차이:
#   ARG = 빌드할 때만 (요리 레시피에 적힌 메모)
#   ENV = 항상 사용 (냉장고에 붙여놓은 메모)
# PYTHONDONTWRITEBYTECODE=1 → .pyc 파일 안 만들어 (컨테이너에서는 필요 없으니까)
# PYTHONUNBUFFERED=1 → print() 출력이 바로바로 보여 (로그 확인할 때 중요!)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_VERSION=${APP_VERSION}

# ── WORKDIR: 작업 디렉토리 설정 ──
# "cd /app" 같은 거야. 이 뒤의 명령어는 모두 /app 안에서 실행돼
# 디렉토리가 없으면 자동으로 만들어줘
# 여러 번 사용하면 cd처럼 디렉토리를 이동할 수 있어
WORKDIR /build

# ── COPY vs ADD 차이 설명 ──
# COPY: 파일을 단순히 복사 (가장 많이 사용, 추천!)
# ADD: 복사 + 압축 해제 + URL 다운로드 (특별한 경우에만 사용)
#
# 왜 requirements.txt를 먼저 복사할까?
# → Docker는 "레이어 캐싱"이라는 걸 해
# → 파일이 바뀌지 않으면 그 단계를 다시 실행하지 않아
# → requirements.txt가 바뀌지 않으면 pip install을 다시 안 해도 돼!
# → 소스코드는 자주 바뀌니까 나중에 복사해
COPY requirements.txt .

# ── RUN: 명령어 실행 ──
# 이미지를 만드는 중에 명령어를 실행하는 거야
# && 로 여러 명령어를 한 줄에 쓰면 레이어가 하나만 생겨 → 이미지가 작아져!
# --no-cache-dir → pip 캐시를 저장하지 않아 (이미지 크기 줄이기)
# --prefix=/install → /install 디렉토리에 설치 (나중에 복사하기 쉽게)
RUN pip install \
    --no-cache-dir \
    --prefix=/install \
    -r requirements.txt

# 소스코드 복사 (requirements.txt가 바뀌지 않으면 위의 pip install은 캐시 사용!)
COPY . .

# ============================================================
# 🔷 스테이지 2: 프로덕션 (Production Stage)
# ============================================================
# 새로운 FROM으로 완전히 새로운 이미지에서 시작해
# builder 단계에서 설치한 파이썬 패키지만 가져오면 돼
# → 빌드 도구, 캐시 등이 없어서 이미지가 훨씬 작아!
FROM python:3.12-slim AS production

# 프로덕션 이미지에도 라벨을 달아줘
LABEL stage="production"

# 환경변수 다시 설정 (새로운 FROM이니까 이전 단계의 ENV는 없어져)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    APP_PORT=8000

# ── USER: 실행할 사용자 변경 ──
# 기본적으로 Docker 컨테이너는 root(관리자)로 실행돼
# 이건 보안상 위험해! 해커가 컨테이너에 침입하면 관리자 권한을 가지게 되니까
# 그래서 일반 사용자를 만들어서 그 사용자로 실행하는 거야
# groupadd = 그룹 만들기
# useradd = 사용자 만들기
#   -r = 시스템 사용자 (로그인 불필요)
#   -g = 이 그룹에 소속
#   -d = 홈 디렉토리
#   -s /sbin/nologin = 로그인 금지
RUN groupadd -r appgroup && \
    useradd -r -g appgroup -d /app -s /sbin/nologin appuser

# 작업 디렉토리 설정
WORKDIR /app

# ── COPY --from: 다른 스테이지에서 파일 가져오기 ──
# builder 스테이지에서 설치한 파이썬 패키지를 가져와
# --chown=appuser:appgroup → 파일 주인을 appuser로 설정
COPY --from=builder /install /usr/local
COPY --from=builder --chown=appuser:appgroup /build /app

# ── EXPOSE: 포트 알려주기 ──
# 실제로 포트를 열지는 않아! 문서화 용도야
# "이 컨테이너는 8000번 포트를 사용할 거야"라고 알려주는 것
# 실제 포트 연결은 docker run -p 8000:8000 으로 해야 해
EXPOSE ${APP_PORT}

# ── VOLUME: 데이터 저장소 ──
# 컨테이너가 삭제되면 안의 데이터도 다 사라져
# VOLUME으로 지정하면 데이터가 호스트에 저장돼서 안전해
# 로그 파일처럼 보존해야 하는 데이터에 사용해
VOLUME ["/app/data", "/app/logs"]

# ── HEALTHCHECK: 건강 확인 ──
# Docker가 주기적으로 컨테이너가 잘 동작하는지 확인하는 거야
# --interval=30s   → 30초마다 확인해
# --timeout=10s    → 10초 안에 응답 없으면 실패
# --start-period=5s → 시작 후 5초는 기다려줘 (앱이 준비되는 시간)
# --retries=3      → 3번 연속 실패하면 "unhealthy" (아픈 상태)
# curl로 /health 엔드포인트를 호출해서 확인해
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${APP_PORT}/health || exit 1

# 이제부터는 appuser로 실행 (보안!)
USER appuser

# ── ENTRYPOINT vs CMD 차이 ──
# ENTRYPOINT = 항상 실행되는 명령어 (변경 불가, 고정)
# CMD = 기본 인자값 (변경 가능)
#
# 예시:
#   ENTRYPOINT ["python"] + CMD ["app.py"]
#   → docker run myimage         → python app.py 실행
#   → docker run myimage test.py → python test.py 실행 (CMD만 바뀜)
#
# ENTRYPOINT만 쓰면:
#   → 항상 같은 명령어 실행 (인자만 추가 가능)
# CMD만 쓰면:
#   → docker run 뒤에 다른 명령어를 쓰면 완전히 대체됨
#
# 두 개 같이 쓰면:
#   → ENTRYPOINT는 고정, CMD는 기본값 (가장 유연한 방법!)

# exec form (권장): ["실행파일", "인자1", "인자2"]
# shell form (비권장): 단순 문자열 → sh -c로 실행됨
ENTRYPOINT ["python"]
CMD ["app.py"]
