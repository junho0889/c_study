# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [데이터 연계] 학습 09단계: REST API 기초
#   ─ HTTP · 상태코드 · REST 원칙 · 버전 관리 ─
#   ■ 실행 방법: python 09_rest_api_basics.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. HTTP 한 줄 복습 (요청/응답/헤더/바디)
#   2. REST 의 6 가지 제약
#   3. 자원(Resource) 지향 URL 설계
#   4. 메서드 / 상태코드 매핑
#   5. 페이지네이션 / 필터링 / 정렬
#   6. 버전 관리 (URL / 헤더 / 컨텐츠 협상)
#   7. 실전: 미니 라우터를 dict 로 구현
#
# ─────────────────────────────────────────────────────────────────────────


def lesson1_http():
    # =========================================================================
    #   레슨 1 — HTTP 복습
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : HTTP                       │")
    print("└──────────────────────────────────────┘")
    # ■ 요청:
    #     GET /orders/42 HTTP/1.1
    #     Host: api.example.com
    #     Authorization: Bearer <token>
    #     Accept: application/json
    #
    # ■ 응답:
    #     HTTP/1.1 200 OK
    #     Content-Type: application/json
    #     ETag: "xyz"
    #
    #     {"id":42,"amount":100}
    #
    # ■ 핵심 개념:
    #   - 무상태(stateless): 매 요청 자체로 충분
    #   - 헤더(metadata) ↔ 바디(payload) 의 분리
    print(" REST 는 ‘HTTP 를 잘 쓰자’의 약자에 가깝다.  HTTP 를 이해하면 절반 끝.")
    print()


def lesson2_rest_constraints():
    # =========================================================================
    #   레슨 2 — REST 6 제약
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : REST 6 제약                │")
    print("└──────────────────────────────────────┘")
    # ■ 1) 클라이언트-서버 분리
    # ■ 2) 무상태(stateless)
    # ■ 3) 캐시 가능(cacheable)
    # ■ 4) 균일 인터페이스(uniform interface) — 자원/표현/HATEOAS
    # ■ 5) 계층화 시스템(layered system)
    # ■ 6) (선택) 코드 온 디맨드
    #
    # ■ 가장 자주 “REST 가 맞나?” 라고 의심받는 항목:
    #   - HATEOAS — 실무 99% 미적용. ‘참고’ 정도.
    print(" 실무 REST 는 ‘uniform interface + cacheable + stateless’ 가 핵심.")
    print()


def lesson3_resource_url():
    # =========================================================================
    #   레슨 3 — 자원 지향 URL
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : Resource URL               │")
    print("└──────────────────────────────────────┘")
    # ■ 좋은 URL: 명사 + 계층 + 식별자
    #   - GET    /v1/orders
    #   - POST   /v1/orders
    #   - GET    /v1/orders/{id}
    #   - PATCH  /v1/orders/{id}
    #   - DELETE /v1/orders/{id}
    #   - GET    /v1/users/{uid}/orders     ← 관계 표현
    #
    # ■ 안티패턴:
    #   - /v1/getOrders, /v1/order/delete   (동사 포함)
    #   - /v1/orders?action=delete         (동사)
    print(" URL 은 ‘명사 + 계층’. 동사는 HTTP 메서드가 표현.")
    print()


def lesson4_methods_status():
    # =========================================================================
    #   레슨 4 — 메서드 / 상태코드
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : 메서드 / 상태코드          │")
    print("└──────────────────────────────────────┘")
    # ■ 메서드 의미:
    #   - GET    : 조회, safe, idempotent
    #   - POST   : 생성, 부작용 OK, idempotent X
    #   - PUT    : 전체 교체, idempotent
    #   - PATCH  : 부분 수정, 보통 idempotent
    #   - DELETE : 삭제, idempotent
    #
    # ■ 상태코드:
    #   - 2xx 성공:     200 OK / 201 Created / 204 No Content
    #   - 3xx 리다이렉트: 301 / 302 / 304 Not Modified
    #   - 4xx 클라이언트 잘못: 400 / 401 / 403 / 404 / 409 / 422 / 429
    #   - 5xx 서버 잘못: 500 / 502 / 503 / 504
    #
    # ■ 자주 헷갈리는 것:
    #   - 401 (인증 X) vs 403 (인증 O, 권한 X)
    #   - 422 (유효성 실패) vs 400 (요청 형식 자체가 깨짐)
    print(" 메서드/상태코드는 ‘프로토콜의 어휘’.  엇갈리게 쓰면 외부 통합 시 사고 빈발.")
    print()


def lesson5_pagination():
    # =========================================================================
    #   레슨 5 — Pagination / Filter / Sort
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 페이지네이션               │")
    print("└──────────────────────────────────────┘")
    # ■ Offset 방식:
    #     GET /orders?offset=200&limit=50
    #     - 단점: deep page 가 비쌈, 결과 시프트 이슈
    #
    # ■ Keyset / Cursor 방식 (권장):
    #     GET /orders?after=2026-05-13T10:00:00Z&limit=50
    #     - 안정적, 무한 스크롤에 강함
    #
    # ■ 필터 / 정렬:
    #     GET /orders?status=PAID&sort=-created_at
    #     GET /orders?amount[gte]=100&amount[lt]=1000
    print(" 대용량 API 는 keyset/cursor 페이지네이션이 표준.")
    print()


def lesson6_versioning():
    # =========================================================================
    #   레슨 6 — 버전 관리
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 버전 관리                  │")
    print("└──────────────────────────────────────┘")
    # ■ URL 버전:        /v1/orders, /v2/orders  ← 가장 단순/명확
    # ■ 헤더 버전:        X-API-Version: 1.2
    # ■ 컨텐츠 협상:      Accept: application/vnd.example.v2+json
    #
    # ■ 권장:
    #   - 외부 공개 API → URL 버전 (가장 디버깅 쉬움)
    #   - 변경 정책 명시: deprecation 알림 + Sunset 헤더
    print(" 가장 안전한 호환성 정책: 새 버전 추가, 옛 버전 ‘Sunset 시각 + 알림’.")
    print()


def lesson7_practice_router():
    # =========================================================================
    #   레슨 7 — 미니 라우터
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 미니 라우터                │")
    print("└──────────────────────────────────────┘")
    routes = {
        ("GET",    "/v1/orders"):       lambda body: ([{"id": 1, "amount": 100}], 200),
        ("GET",    "/v1/orders/{id}"): lambda body: ({"id": body["id"], "amount": 100}, 200),
        ("POST",   "/v1/orders"):       lambda body: ({"id": 99, **body}, 201),
        ("DELETE", "/v1/orders/{id}"): lambda body: (None, 204),
    }

    def route(method, path, body):
        # 매우 단순한 path match
        for (m, pat), fn in routes.items():
            if m != method:
                continue
            pat_parts = pat.split("/")
            path_parts = path.split("/")
            if len(pat_parts) != len(path_parts):
                continue
            params = {}
            ok = True
            for p, x in zip(pat_parts, path_parts):
                if p.startswith("{") and p.endswith("}"):
                    params[p[1:-1]] = x
                elif p != x:
                    ok = False
                    break
            if ok:
                return fn({**(body or {}), **params})
        return ({"error": "not found"}, 404)

    samples = [
        ("GET",    "/v1/orders", None),
        ("GET",    "/v1/orders/42", None),
        ("POST",   "/v1/orders", {"amount": 250}),
        ("DELETE", "/v1/orders/42", None),
        ("PUT",    "/v1/orders/42", {"amount": 1}),    # 미매핑 → 404 (실무에선 405)
    ]
    for m, p, b in samples:
        resp, status = route(m, p, b)
        print(f"  {m:>6} {p:<25}  →  {status}  {resp}")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 연습문제
# ─────────────────────────────────────────────────────────────────────────
#  Q1. PUT 과 PATCH 의 멱등성 차이를 한 줄로 적어라.
#  Q2. 401 / 403 / 404 의 ‘공개 정보 노출’ 관점 차이는?
#  Q3. offset 페이지네이션의 ‘결과 시프트’ 가 실제로 어떻게 사고를 만드나?
#  Q4. URL 버전과 헤더 버전의 운영/디버깅 측면 trade-off 3 가지?
#  Q5. 위 미니 라우터에서 PUT 이 404 대신 405(Method Not Allowed) 를 반환하도록 바꾸려면?


if __name__ == "__main__":
    lesson1_http()
    lesson2_rest_constraints()
    lesson3_resource_url()
    lesson4_methods_status()
    lesson5_pagination()
    lesson6_versioning()
    lesson7_practice_router()
