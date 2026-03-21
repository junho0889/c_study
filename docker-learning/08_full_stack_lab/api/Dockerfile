# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# ■ 파일명: Dockerfile
# ■ 목적: Python API 서버 이미지 빌드
# ■ 설명: Flask 기반 REST API + Prometheus 메트릭
# ■ 날짜: 2026-03-21
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ── 빌더 스테이지 ──
FROM python:3.12-slim AS builder

# 빌드 도구 설치 (psycopg2 빌드에 필요)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# 가상환경 생성 + 의존성 설치
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── 프로덕션 스테이지 ──
FROM python:3.12-slim

# 런타임 라이브러리만 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

# 비루트 사용자 생성
RUN groupadd -r api && useradd -r -g api -d /app api

# 가상환경 복사
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 소스코드 복사
WORKDIR /app
COPY --chown=api:api . .

# 환경변수
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --retries=3 --start-period=10s \
    CMD curl -f http://localhost:8000/health || exit 1

USER api
CMD ["python", "app.py"]
