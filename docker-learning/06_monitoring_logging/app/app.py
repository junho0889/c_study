# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# ■ 파일명: app.py
# ■ 목적: Prometheus 메트릭을 제공하는 Flask 앱
# ■ 날짜: 2026-03-21
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import time
import random
from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, Gauge, generate_latest

app = Flask(__name__)

# Prometheus 메트릭 정의
REQUEST_COUNT = Counter('app_requests_total', 'Total request count', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('app_request_latency_seconds', 'Request latency', ['endpoint'])
ACTIVE_REQUESTS = Gauge('app_active_requests', 'Number of active requests')

@app.route("/")
def hello():
    start = time.time()
    ACTIVE_REQUESTS.inc()
    time.sleep(random.uniform(0.01, 0.1))  # 시뮬레이션
    REQUEST_COUNT.labels(method='GET', endpoint='/', status='200').inc()
    REQUEST_LATENCY.labels(endpoint='/').observe(time.time() - start)
    ACTIVE_REQUESTS.dec()
    return jsonify({"message": "Monitoring Demo!", "timestamp": time.time()})

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
