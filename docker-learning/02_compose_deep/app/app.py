# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# ■ 파일명: app.py
# ■ 목적: Compose 심화 학습용 Flask 앱
# ■ 날짜: 2026-03-21
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import os
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def hello():
    return jsonify({"message": "Compose Deep Dive!", "env": os.getenv("APP_ENV")})

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("APP_PORT", 8000)))
