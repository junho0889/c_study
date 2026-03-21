# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# ■ 파일명: app.py
# ■ 목적: Docker 기초 학습용 간단한 Flask 웹 앱
# ■ 날짜: 2026-03-21
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import os
import redis
from flask import Flask, jsonify

app = Flask(__name__)

# Redis 연결 (docker-compose에서 서비스 이름으로 접근)
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)

@app.route("/")
def hello():
    count = r.incr("visit_count")  # 방문할 때마다 숫자 증가
    return jsonify({
        "message": "Docker 학습에 오신 걸 환영합니다!",
        "visit_count": count,
        "version": os.getenv("APP_VERSION", "1.0.0")
    })

@app.route("/health")
def health():
    try:
        r.ping()
        return jsonify({"status": "healthy"}), 200
    except Exception:
        return jsonify({"status": "unhealthy"}), 500

if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", 8000))
    app.run(host="0.0.0.0", port=port)
