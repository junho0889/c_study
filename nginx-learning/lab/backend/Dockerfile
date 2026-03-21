# ■■■ Python Flask 백엔드 서버 Dockerfile ■■■
FROM python:3.12-slim
# 파이썬 출력 버퍼링 비활성화 (로그 즉시 출력)
ENV PYTHONUNBUFFERED=1
WORKDIR /app
# Flask 설치
RUN pip install --no-cache-dir flask gunicorn
# 앱 파일 복사
COPY app.py .
# Gunicorn으로 Flask 앱 실행 (프로덕션용 WSGI 서버)
# -w 2: 워커 프로세스 2개
# -b 0.0.0.0:5000: 모든 인터페이스의 5000번 포트에서 수신
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
