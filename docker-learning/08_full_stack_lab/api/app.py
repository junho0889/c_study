# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# ■ 파일명: app.py
# ■ 목적: 풀스택 실습용 Python REST API
# ■ 설명: Flask + PostgreSQL + Redis + Prometheus 메트릭
# ■ 날짜: 2026-03-21
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import os
import time
import json
import psycopg2
import redis
from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# ── Flask 앱 초기화 ──
app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY", "dev-secret")

# ── Prometheus 메트릭 정의 ──
# Counter: 계속 증가하는 숫자 (요청 수, 에러 수)
REQUEST_COUNT = Counter(
    'api_requests_total',                    # 메트릭 이름
    'Total API requests',                    # 설명
    ['method', 'endpoint', 'status']         # 라벨 (분류용)
)
# Histogram: 분포를 보는 메트릭 (응답 시간)
REQUEST_LATENCY = Histogram(
    'api_request_latency_seconds',
    'API request latency',
    ['endpoint']
)
# Gauge: 올라갔다 내려갔다 하는 숫자 (활성 연결 수)
ACTIVE_CONNECTIONS = Gauge(
    'api_active_connections',
    'Number of active connections'
)

# ── 데이터베이스 연결 ──
def get_db():
    """PostgreSQL 연결을 가져오는 함수"""
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        return conn
    except Exception as e:
        app.logger.error(f"DB 연결 실패: {e}")
        return None

# ── Redis 연결 ──
def get_redis():
    """Redis 연결을 가져오는 함수"""
    try:
        r = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))
        r.ping()
        return r
    except Exception as e:
        app.logger.error(f"Redis 연결 실패: {e}")
        return None

# ══════════════════════════════════════════════════
# API 엔드포인트
# ══════════════════════════════════════════════════

@app.route("/")
def index():
    """메인 페이지 - API 정보 반환"""
    start = time.time()
    ACTIVE_CONNECTIONS.inc()

    # Redis에서 방문 수 카운트
    r = get_redis()
    visit_count = 0
    if r:
        visit_count = r.incr("api:visit_count")

    result = jsonify({
        "service": "Full Stack Lab API",
        "version": "1.0.0",
        "environment": os.getenv("APP_ENV", "unknown"),
        "visit_count": visit_count,
        "endpoints": {
            "/": "이 페이지 (API 정보)",
            "/health": "헬스체크",
            "/api/items": "아이템 목록 (GET) / 생성 (POST)",
            "/api/stats": "통계 정보",
            "/metrics": "Prometheus 메트릭"
        }
    })

    REQUEST_COUNT.labels(method='GET', endpoint='/', status='200').inc()
    REQUEST_LATENCY.labels(endpoint='/').observe(time.time() - start)
    ACTIVE_CONNECTIONS.dec()
    return result

@app.route("/health")
def health():
    """헬스체크 엔드포인트"""
    status = {"api": "healthy"}
    http_status = 200

    # DB 상태 확인
    conn = get_db()
    if conn:
        status["database"] = "healthy"
        conn.close()
    else:
        status["database"] = "unhealthy"
        http_status = 500

    # Redis 상태 확인
    r = get_redis()
    if r:
        status["redis"] = "healthy"
    else:
        status["redis"] = "unhealthy"
        http_status = 500

    status["overall"] = "healthy" if http_status == 200 else "degraded"
    return jsonify(status), http_status

@app.route("/api/items", methods=["GET"])
def get_items():
    """아이템 목록 조회 (캐시 활용)"""
    start = time.time()

    # 먼저 Redis 캐시 확인
    r = get_redis()
    if r:
        cached = r.get("cache:items")
        if cached:
            REQUEST_COUNT.labels(method='GET', endpoint='/api/items', status='200').inc()
            REQUEST_LATENCY.labels(endpoint='/api/items').observe(time.time() - start)
            return jsonify({"source": "cache", "items": json.loads(cached)})

    # 캐시에 없으면 DB에서 조회
    conn = get_db()
    if not conn:
        REQUEST_COUNT.labels(method='GET', endpoint='/api/items', status='500').inc()
        return jsonify({"error": "DB 연결 실패"}), 500

    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, description, created_at FROM items ORDER BY id DESC LIMIT 50")
        rows = cur.fetchall()
        items = [{"id": r[0], "name": r[1], "description": r[2], "created_at": str(r[3])} for r in rows]

        # 결과를 Redis에 캐시 (60초)
        if r:
            r.setex("cache:items", 60, json.dumps(items))

        REQUEST_COUNT.labels(method='GET', endpoint='/api/items', status='200').inc()
        REQUEST_LATENCY.labels(endpoint='/api/items').observe(time.time() - start)
        return jsonify({"source": "database", "items": items})
    except Exception as e:
        REQUEST_COUNT.labels(method='GET', endpoint='/api/items', status='500').inc()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/items", methods=["POST"])
def create_item():
    """아이템 생성"""
    start = time.time()
    data = request.get_json()

    if not data or "name" not in data:
        REQUEST_COUNT.labels(method='POST', endpoint='/api/items', status='400').inc()
        return jsonify({"error": "name 필드가 필요합니다"}), 400

    conn = get_db()
    if not conn:
        return jsonify({"error": "DB 연결 실패"}), 500

    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO items (name, description) VALUES (%s, %s) RETURNING id, created_at",
            (data["name"], data.get("description", ""))
        )
        result = cur.fetchone()
        conn.commit()

        # 캐시 무효화 (새 데이터가 추가됐으니까)
        r = get_redis()
        if r:
            r.delete("cache:items")

        REQUEST_COUNT.labels(method='POST', endpoint='/api/items', status='201').inc()
        REQUEST_LATENCY.labels(endpoint='/api/items').observe(time.time() - start)
        return jsonify({
            "id": result[0],
            "name": data["name"],
            "description": data.get("description", ""),
            "created_at": str(result[1])
        }), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/stats")
def stats():
    """통계 정보"""
    result = {"timestamp": time.time()}

    # DB 통계
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM items")
            result["total_items"] = cur.fetchone()[0]
        except:
            result["total_items"] = "error"
        finally:
            conn.close()

    # Redis 통계
    r = get_redis()
    if r:
        result["visit_count"] = int(r.get("api:visit_count") or 0)
        result["redis_keys"] = r.dbsize()

    return jsonify(result)

@app.route("/metrics")
def metrics():
    """Prometheus 메트릭 엔드포인트"""
    return generate_latest(), 200, {'Content-Type': 'text/plain; charset=utf-8'}

# ── 앱 시작 ──
if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", 8000))
    debug = os.getenv("APP_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
