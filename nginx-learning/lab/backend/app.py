# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# ■■■ Flask 백엔드 테스트 서버                          ■■■
# ■■■ Nginx 로드밸런싱, 프록시 테스트용 간단한 API      ■■■
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import os                   # 환경 변수 읽기
import time                 # 타임스탬프 생성
import socket               # 호스트 이름 가져오기
import json                 # JSON 직렬화
from datetime import datetime  # 날짜/시간 처리
from flask import Flask, request, jsonify  # Flask 웹 프레임워크

# ■■■ Flask 앱 초기화 ■■■
app = Flask(__name__)

# ■■■ 환경 변수에서 앱 설정 읽기 ■■■
APP_NAME = os.environ.get('APP_NAME', 'unknown')     # 앱 식별자 (app1, app2 등)
APP_PORT = int(os.environ.get('APP_PORT', 5000))     # 서버 포트
HOSTNAME = socket.gethostname()                       # 컨테이너 호스트 이름

# ■■■ 요청 카운터 (로드밸런싱 테스트용) ■■■
request_count = 0


@app.route('/')
def index():
    """루트 경로 - 서버 정보 반환"""
    global request_count
    request_count += 1  # 요청 횟수 증가
    return jsonify({
        'server': APP_NAME,           # 어떤 서버가 응답했는지 확인
        'hostname': HOSTNAME,         # 컨테이너 호스트 이름
        'request_count': request_count,  # 이 서버의 총 요청 횟수
        'timestamp': datetime.now().isoformat(),  # 응답 시간
        'message': f'Hello from {APP_NAME}!'
    })


@app.route('/api/health')
def health():
    """헬스체크 엔드포인트 - 로드밸런서/모니터링에서 사용"""
    return jsonify({
        'server': APP_NAME,
        'status': 'healthy',          # 서버 상태
        'uptime': time.process_time()  # 프로세스 실행 시간 (초)
    })


@app.route('/api/data')
def data():
    """데이터 API - 로드밸런싱 테스트용"""
    global request_count
    request_count += 1
    return jsonify({
        'server': APP_NAME,
        'data': f'Response from {APP_NAME}',
        'request_number': request_count,
        'headers': {
            'X-Real-IP': request.headers.get('X-Real-IP', 'N/A'),
            'X-Forwarded-For': request.headers.get('X-Forwarded-For', 'N/A'),
            'X-Forwarded-Proto': request.headers.get('X-Forwarded-Proto', 'N/A'),
            'Host': request.headers.get('Host', 'N/A'),
        },
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/slow')
def slow():
    """느린 응답 엔드포인트 - 타임아웃 테스트용"""
    delay = int(request.args.get('delay', 3))  # 기본 3초 지연
    time.sleep(delay)
    return jsonify({
        'server': APP_NAME,
        'message': f'Slow response after {delay}s delay'
    })


@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    """로그인 엔드포인트 - Rate Limiting 테스트용"""
    return jsonify({
        'server': APP_NAME,
        'message': 'Login endpoint (rate limited)',
        'client_ip': request.headers.get('X-Real-IP', request.remote_addr)
    })


# ■■■ 서버 시작 ■■■
if __name__ == '__main__':
    print(f'■■■ {APP_NAME} 서버 시작 (포트: {APP_PORT}) ■■■')
    # host='0.0.0.0': 모든 네트워크 인터페이스에서 수신 (Docker 컨테이너에서 필수)
    # debug=False: 프로덕션 모드 (자동 리로드 비활성화)
    app.run(host='0.0.0.0', port=APP_PORT, debug=False)
