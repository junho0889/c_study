# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [데이터 연계] 학습 13단계: 인증 / 인가
#   ─ JWT · OAuth2 · API Key · mTLS · RBAC / ABAC ─
#   ■ 실행 방법: python 13_auth.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 인증(authn) 과 인가(authz) 의 차이
#   2. JWT 의 구조와 위험
#   3. OAuth2 / OIDC — 위임 인증의 표준
#   4. API Key — 단순함의 미덕과 함정
#   5. mTLS — 서비스-서비스 강한 신뢰
#   6. RBAC / ABAC — 권한 모델
#   7. 실전: HMAC-SHA256 으로 단순 토큰 검증 (의사코드)
#
# ─────────────────────────────────────────────────────────────────────────

import hashlib
import hmac
import base64
import json
import time


def lesson1_authn_authz():
    # =========================================================================
    #   레슨 1 — Authn vs Authz
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : Authn vs Authz             │")
    print("└──────────────────────────────────────┘")
    # ■ Authentication(인증): “너는 누구냐?”
    #   - 로그인 / 토큰 검증
    # ■ Authorization(인가): “이 사람이 이 동작을 할 수 있냐?”
    #   - RBAC / ABAC / 정책 평가
    # ■ 두 단계는 분리 — 인증은 통과해도 권한이 없으면 403.
    print(" 401 = 누구냐?  403 = 권한 없음.  둘이 헷갈리면 운영 사고 자주 발생.")
    print()


def lesson2_jwt():
    # =========================================================================
    #   레슨 2 — JWT
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : JWT                        │")
    print("└──────────────────────────────────────┘")
    # ■ 구조: header.payload.signature   (각 base64url)
    #
    #   {alg:"HS256", typ:"JWT"}.{sub:"u1", exp: 17xxxx}.{서명}
    #
    # ■ 알고리즘:
    #   - HS256 (대칭, 공유 키)
    #   - RS256 / ES256 (비대칭, public key 만 배포)
    #   - 외부 발급자가 있다면 거의 항상 RS/ES.
    #
    # ■ 위험:
    #   - alg='none' 공격 (검증 비활성)
    #   - 키 교체(rotation) 미준비
    #   - JWT 무효화(invalidate) 어려움 → blacklist 또는 짧은 TTL + refresh token
    #
    # ■ 짧은 TTL + Refresh Token:
    #   - access token 15min, refresh token 7day (보안 저장)
    print(" JWT 는 ‘stateless 인증’ 의 표준.  대신 ‘무효화 어려움’ 을 항상 설계로 보완.")
    print()


def lesson3_oauth2():
    # =========================================================================
    #   레슨 3 — OAuth2 / OIDC
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : OAuth2 / OIDC              │")
    print("└──────────────────────────────────────┘")
    # ■ OAuth2 = ‘권한 위임’ 의 표준 (예: 구글 로그인)
    # ■ OIDC  = OAuth2 위에 ‘신원 정보’ 표준 (ID Token = JWT)
    #
    # ■ 4 가지 grant:
    #   - Authorization Code (+ PKCE) ← 대부분의 웹/모바일
    #   - Client Credentials          ← 머신 to 머신
    #   - Resource Owner Password     ← 권장 X
    #   - Implicit                    ← 폐기 권고
    #
    # ■ PKCE: 모바일/SPA 에서 ‘인증 코드 가로채기 공격’ 방어
    print(" 외부 통합 인증 = 거의 항상 OIDC.  자체 비번 관리 X 가 안전.")
    print()


def lesson4_api_key():
    # =========================================================================
    #   레슨 4 — API Key
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : API Key                    │")
    print("└──────────────────────────────────────┘")
    # ■ 장점:
    #   - 단순 (Authorization: Bearer <key>)
    #   - 서버-서버 통합/사내 도구에 적합
    #
    # ■ 함정:
    #   - 만료/회전이 잘 안 됨 → ‘잊혀진 키’ 가 사고의 시작
    #   - 권한 범위(scope) 가 보통 너무 큼
    #   - 키 노출 시 즉시 폐기 절차 필요
    #
    # ■ 운영 권장:
    #   - 키마다 scope + IP allowlist + 마지막 사용 시각 기록
    #   - 90일 회전 정책 + 알림
    print(" API Key 는 단순하지만 ‘회전/스코프/로그’ 가 빠지면 가장 흔한 보안 사고원.")
    print()


def lesson5_mtls():
    # =========================================================================
    #   레슨 5 — mTLS
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : mTLS                       │")
    print("└──────────────────────────────────────┘")
    # ■ mTLS:
    #   - 서버 ↔ 클라이언트 ‘둘 다’ 인증서 제시
    #   - 사내 마이크로서비스 / 금융권 / IoT
    #
    # ■ 인증서 관리:
    #   - 자체 PKI 또는 Cert Manager + Vault
    #   - 만료 알림 → 무엇이든 자동화 (Let’s Encrypt 같은 짧은 만료 + 자동 갱신)
    #
    # ■ Zero Trust 와 함께:
    #   - 모든 호출이 mTLS + 토큰 + 정책 평가 (네트워크 위치 신뢰 X)
    print(" mTLS = ‘서비스 신원’ 의 가장 강한 형태. Zero Trust 아키텍처의 기본.")
    print()


def lesson6_rbac_abac():
    # =========================================================================
    #   레슨 6 — RBAC / ABAC
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : RBAC / ABAC                │")
    print("└──────────────────────────────────────┘")
    # ■ RBAC: role → permissions.  예: ‘admin’ → orders:read, orders:write
    # ■ ABAC: 속성(attribute) 조합으로 결정.
    #   - 예: user.region == record.region AND record.confidential != true
    # ■ ReBAC (관계 기반): Google Zanzibar 영감.  ‘이 user 가 이 doc 의 viewer?’
    # ■ 도구:
    #   - Open Policy Agent(OPA) + Rego
    #   - SpiceDB(Zanzibar 오픈소스)
    #   - 사내 정책 엔진 자체 구축
    print(" RBAC 로 시작 → 도메인 복잡해지면 ABAC/ReBAC 로 진화.  코드에 분기 X, 정책 엔진 O.")
    print()


def lesson7_practice_hmac_token():
    # =========================================================================
    #   레슨 7 — HMAC 기반 단순 토큰
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : HMAC 토큰                  │")
    print("└──────────────────────────────────────┘")
    SECRET = b"super-secret-key-do-not-share"

    def b64url(b):
        return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

    def sign(payload: dict, ttl=3600):
        body = json.dumps({**payload, "exp": int(time.time()) + ttl}, separators=(",", ":")).encode()
        sig = hmac.new(SECRET, body, hashlib.sha256).digest()
        return f"{b64url(body)}.{b64url(sig)}"

    def verify(token: str):
        try:
            body_b64, sig_b64 = token.split(".")
        except ValueError:
            return None
        body = base64.urlsafe_b64decode(body_b64 + "==")
        sig = base64.urlsafe_b64decode(sig_b64 + "==")
        expected = hmac.new(SECRET, body, hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected):
            return None
        data = json.loads(body)
        if data["exp"] < time.time():
            return None
        return data

    token = sign({"sub": "user-1", "role": "admin"}, ttl=60)
    print(" token   :", token[:30], "...")
    print(" verified:", verify(token))
    print(" tampered:", verify(token[:-2] + "AA"))
    print()
    # → 실 서비스에서는 JWT 라이브러리(JWS + JWE) 사용. 이 코드는 ‘원리 이해’ 용.


# ─────────────────────────────────────────────────────────────────────────
# ■ 연습문제
# ─────────────────────────────────────────────────────────────────────────
#  Q1. JWT 의 ‘alg=none’ 취약점 회피 방법을 두 가지 적어라.
#  Q2. OAuth2 의 client_credentials 흐름과 mTLS 의 차이를 ‘machine-to-machine’ 관점에서 비교하라.
#  Q3. API Key 의 ‘마지막 사용 시각 로그’ 가 보안 사고 분석에서 어떤 가치를 갖는가?
#  Q4. RBAC 의 한계가 드러나는 시나리오 두 가지를 적고 ABAC 의 해결책을 적어라.
#  Q5. 위 HMAC 토큰의 약점을 5 가지 적고, 운영 JWT 가 그것을 어떻게 해결하는지 비교하라.


if __name__ == "__main__":
    lesson1_authn_authz()
    lesson2_jwt()
    lesson3_oauth2()
    lesson4_api_key()
    lesson5_mtls()
    lesson6_rbac_abac()
    lesson7_practice_hmac_token()
