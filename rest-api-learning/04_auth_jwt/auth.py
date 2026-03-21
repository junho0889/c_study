# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   REST API 학습 04단계: 인증과 JWT
#   ─ Authentication vs Authorization, API Key, Bearer Token, JWT 구조 ─
#
#   인증(Authentication)은 "너 누구야?" 라고 확인하는 것이고,
#   인가(Authorization)는 "너 이거 해도 돼?" 라고 허락하는 것입니다.
#
#   ■ 실행: python auth.py
#   ■ 외부 라이브러리 없이 base64만 사용합니다.
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import base64
import json
import hashlib
import time


# ─────────────────────────────────────────────────────────────────────
# ■ 사용자 데이터베이스 (실제로는 DB에 저장)
# ─────────────────────────────────────────────────────────────────────
USERS = {
    "minsu": {"password": "1234", "role": "student"},
    "teacher_kim": {"password": "abcd", "role": "teacher"},
}

API_KEYS = {
    "key-abc-123": "minsu",
    "key-xyz-789": "teacher_kim",
}

SECRET_KEY = "my-super-secret-key"


def lesson1_auth_vs_authz():
    # =========================================================================
    #   레슨 1 — 인증(Authentication) vs 인가(Authorization)
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 1 : 인증 vs 인가                       │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 인증(Authentication) = "누구인지 확인"
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     학교 정문에서 학생증을 보여 주는 것
    #     "나는 3학년 2반 민수입니다" → 학생증 사진과 얼굴이 같으면 통과!
    #
    # ■ 인가(Authorization) = "권한이 있는지 확인"
    #
    #   비유:
    #     교무실에 들어갈 수 있는지 확인하는 것
    #     학생증이 있어도 "학생"은 교무실 출입 불가 → 권한 없음!
    #     "선생님"이면 교무실 출입 가능 → 권한 있음!
    #

    print("  [인증] 민수가 로그인합니다...")
    username = "minsu"
    password = "1234"

    if USERS.get(username) and USERS[username]["password"] == password:
        print(f"  [O] 인증 성공! {username}님 확인되었습니다.")
        role = USERS[username]["role"]
        print(f"  역할: {role}")
    print()

    print("  [인가] 민수가 성적 수정을 요청합니다...")
    if role == "teacher":
        print("  [O] 성적 수정 권한이 있습니다.")
    else:
        print("  [X] 학생은 성적을 수정할 수 없습니다! (403 Forbidden)")
    print()

    print("  [인가] 선생님이 성적 수정을 요청합니다...")
    teacher_role = USERS["teacher_kim"]["role"]
    if teacher_role == "teacher":
        print("  [O] 선생님은 성적 수정 권한이 있습니다!")
    print()


def lesson2_api_key():
    # =========================================================================
    #   레슨 2 — API Key 인증
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 2 : API Key 인증                       │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ API Key = 서버가 미리 발급한 비밀 열쇠
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     놀이공원 연간 이용권 번호
    #     매번 신분증을 보여 줄 필요 없이 번호만 보여 주면 통과!
    #     단, 번호를 남에게 주면 그 사람도 들어갈 수 있으니 비밀로 간직!
    #
    #   사용법:
    #     요청 헤더에 넣기:  X-API-Key: key-abc-123
    #     또는 쿼리에 넣기:  /students?api_key=key-abc-123
    #

    def authenticate_with_api_key(api_key):
        """API Key로 사용자를 확인하는 함수"""
        if api_key in API_KEYS:
            username = API_KEYS[api_key]
            return {"authenticated": True, "username": username}
        return {"authenticated": False, "username": None}

    # 올바른 키
    result = authenticate_with_api_key("key-abc-123")
    print(f"  키 'key-abc-123' → {result}")

    # 잘못된 키
    result = authenticate_with_api_key("wrong-key")
    print(f"  키 'wrong-key'   → {result}")

    print()
    print("  장점: 구현이 간단하고, 서버 간 통신에 자주 사용")
    print("  단점: 키가 유출되면 누구나 접근 가능, 만료 기능이 없음")
    print()


def lesson3_jwt_structure():
    # =========================================================================
    #   레슨 3 — JWT (JSON Web Token) 구조
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 3 : JWT 구조                           │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ JWT = 세 덩어리로 된 토큰
    # ─────────────────────────────────────────────────────────────────────
    #
    #   JWT는 점(.)으로 구분된 세 부분으로 이루어져 있습니다:
    #
    #   ┌──────────┐   ┌──────────┐   ┌──────────┐
    #   │  Header  │ . │ Payload  │ . │Signature │
    #   │ (머리)   │   │ (몸통)   │   │ (도장)   │
    #   └──────────┘   └──────────┘   └──────────┘
    #
    #   비유:
    #     택배 상자에 비유하면:
    #     Header    = 택배 종류 (일반택배/냉장택배) → 어떤 방식으로 암호화했는지
    #     Payload   = 택배 안에 든 물건 → 사용자 정보(이름, 권한, 만료시간)
    #     Signature = 택배 봉인 스티커 → 누가 뜯었는지 알 수 있는 도장
    #

    # Header: 토큰 타입과 암호화 알고리즘
    header = {"alg": "HS256", "typ": "JWT"}

    # Payload: 실제 담고 싶은 정보 (= Claims)
    payload = {
        "sub": "minsu",           # subject: 누구의 토큰인지
        "role": "student",        # 커스텀 클레임: 역할
        "iat": int(time.time()),  # issued at: 발급 시간
        "exp": int(time.time()) + 3600,  # expiration: 1시간 후 만료
    }

    print("  [Header]")
    print(f"    {json.dumps(header, indent=4)}")
    print()
    print("  [Payload]")
    print(f"    {json.dumps(payload, indent=4)}")
    print()

    # Base64로 인코딩 (실제 JWT에서 사용하는 방식)
    header_b64 = base64.urlsafe_b64encode(
        json.dumps(header).encode()
    ).rstrip(b"=").decode()

    payload_b64 = base64.urlsafe_b64encode(
        json.dumps(payload).encode()
    ).rstrip(b"=").decode()

    print(f"  Header (Base64):  {header_b64}")
    print(f"  Payload (Base64): {payload_b64}")
    print()

    # Signature: Header + Payload + Secret을 합쳐서 해시
    signature_input = f"{header_b64}.{payload_b64}.{SECRET_KEY}"
    signature = hashlib.sha256(signature_input.encode()).hexdigest()[:32]

    token = f"{header_b64}.{payload_b64}.{signature}"
    print(f"  완성된 JWT:")
    print(f"    {token}")
    print()
    print("  핵심: JWT는 서버가 DB를 조회하지 않아도")
    print("       토큰 자체에서 사용자 정보를 꺼낼 수 있습니다!")
    print()


def create_token(username, role, expires_in=3600):
    """간단한 JWT 생성 함수 (학습용)"""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": username,
        "role": role,
        "iat": int(time.time()),
        "exp": int(time.time()) + expires_in,
    }

    header_b64 = base64.urlsafe_b64encode(
        json.dumps(header).encode()
    ).rstrip(b"=").decode()

    payload_b64 = base64.urlsafe_b64encode(
        json.dumps(payload).encode()
    ).rstrip(b"=").decode()

    sig_input = f"{header_b64}.{payload_b64}.{SECRET_KEY}"
    signature = hashlib.sha256(sig_input.encode()).hexdigest()[:32]

    return f"{header_b64}.{payload_b64}.{signature}"


def verify_token(token):
    """간단한 JWT 검증 함수 (학습용)"""
    parts = token.split(".")
    if len(parts) != 3:
        return {"valid": False, "error": "토큰 형식이 잘못됨"}

    header_b64, payload_b64, received_sig = parts

    # 서명 재계산
    sig_input = f"{header_b64}.{payload_b64}.{SECRET_KEY}"
    expected_sig = hashlib.sha256(sig_input.encode()).hexdigest()[:32]

    if received_sig != expected_sig:
        return {"valid": False, "error": "서명이 일치하지 않음 (위조된 토큰!)"}

    # 페이로드 복원
    padding = 4 - len(payload_b64) % 4
    payload_b64_padded = payload_b64 + "=" * padding
    payload = json.loads(base64.urlsafe_b64decode(payload_b64_padded))

    # 만료 확인
    if payload.get("exp", 0) < time.time():
        return {"valid": False, "error": "토큰이 만료됨"}

    return {"valid": True, "payload": payload}


def lesson4_token_create_and_verify():
    # =========================================================================
    #   레슨 4 — 토큰 생성과 검증
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 4 : 토큰 생성과 검증                    │")
    print("└──────────────────────────────────────────────┘")
    print()

    # 토큰 생성
    token = create_token("minsu", "student")
    print(f"  발급된 토큰: {token[:50]}...")
    print()

    # 정상 토큰 검증
    result = verify_token(token)
    print(f"  검증 결과: {result}")
    print()

    # 위조된 토큰 검증
    fake_token = token[:-5] + "XXXXX"
    result = verify_token(fake_token)
    print(f"  위조 토큰 검증: {result}")
    print()

    # 만료된 토큰 검증
    expired_token = create_token("minsu", "student", expires_in=-1)
    result = verify_token(expired_token)
    print(f"  만료 토큰 검증: {result}")
    print()


def lesson5_bearer_token():
    # =========================================================================
    #   레슨 5 — Bearer Token과 요청 흐름
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 5 : Bearer Token 사용법                │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Bearer Token = "이 토큰을 가진 사람" 이라는 뜻
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     영화 티켓과 같습니다.
    #     "이 티켓을 가진 사람(Bearer)은 영화를 볼 수 있다"
    #     누가 가져왔는지보다 티켓 자체가 유효한지가 중요!
    #
    #   HTTP 요청 예시:
    #     GET /students/me
    #     Authorization: Bearer eyJhbGci...
    #

    token = create_token("minsu", "student")

    # 요청 시뮬레이션
    request_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    print("  [클라이언트 → 서버] 요청 헤더:")
    for key, value in request_headers.items():
        display_value = value[:60] + "..." if len(value) > 60 else value
        print(f"    {key}: {display_value}")
    print()

    # 서버에서 토큰 추출 및 검증
    auth_header = request_headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        extracted_token = auth_header[7:]  # "Bearer " 이후 부분
        result = verify_token(extracted_token)
        if result["valid"]:
            user = result["payload"]["sub"]
            print(f"  [서버] 토큰 검증 성공! 사용자: {user}")
            print(f"  [서버] 200 OK — 민수의 정보를 응답합니다.")
        else:
            print(f"  [서버] 401 Unauthorized — {result['error']}")
    print()


def lesson6_refresh_token():
    # =========================================================================
    #   레슨 6 — Refresh Token 개념
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 6 : Refresh Token                     │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 왜 Refresh Token이 필요한가?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     Access Token  = 1일 입장권 (짧은 유효기간, 15분~1시간)
    #     Refresh Token = 연간 회원증 (긴 유효기간, 7일~30일)
    #
    #     1일 입장권(Access Token)이 만료되면,
    #     연간 회원증(Refresh Token)을 보여 주고 새 입장권을 받습니다.
    #     → 매번 로그인(아이디/비밀번호 입력)할 필요 없음!
    #
    #   흐름:
    #     1. 로그인 → Access Token + Refresh Token 두 개 발급
    #     2. API 요청할 때는 Access Token 사용
    #     3. Access Token 만료 → Refresh Token으로 새 Access Token 발급
    #     4. Refresh Token도 만료 → 다시 로그인 필요
    #

    print("  [1단계] 로그인하여 토큰 쌍 발급")
    access_token = create_token("minsu", "student", expires_in=900)     # 15분
    refresh_token = create_token("minsu", "refresh", expires_in=604800)  # 7일

    print(f"    Access Token  (15분): {access_token[:40]}...")
    print(f"    Refresh Token (7일):  {refresh_token[:40]}...")
    print()

    print("  [2단계] Access Token으로 API 호출")
    result = verify_token(access_token)
    print(f"    검증: {result['valid']} → 정상 접근 가능")
    print()

    print("  [3단계] Access Token 만료 후 갱신 시뮬레이션")
    print("    Access Token 만료됨!")
    print("    Refresh Token으로 새 Access Token 발급...")
    refresh_result = verify_token(refresh_token)
    if refresh_result["valid"]:
        new_access = create_token("minsu", "student", expires_in=900)
        print(f"    새 Access Token: {new_access[:40]}...")
        print("    → 사용자는 다시 로그인할 필요 없이 계속 사용 가능!")
    print()

    print("  요약:")
    print("    Access Token  → 짧은 수명, API 요청용")
    print("    Refresh Token → 긴 수명, Access Token 갱신용")
    print("    둘 다 만료     → 다시 로그인 필요")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("  REST API 04단계 : 인증과 JWT")
    print("=" * 72)
    print()

    lesson1_auth_vs_authz()
    lesson2_api_key()
    lesson3_jwt_structure()
    lesson4_token_create_and_verify()
    lesson5_bearer_token()
    lesson6_refresh_token()
