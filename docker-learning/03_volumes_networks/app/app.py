# 볼륨/네트워크 데모용 간단 앱
import os
from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/")
def hello():
    return jsonify({"message": "Volume & Network Demo!", "hostname": os.uname().nodename})

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
