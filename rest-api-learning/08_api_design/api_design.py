# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   REST API 학습 08단계: API 설계 고급 패턴
#   ─ OpenAPI/Swagger, 멱등성, PATCH vs PUT, 벌크 작업, Webhook ─
#
#   좋은 API를 만들려면 설계 원칙과 고급 패턴을 알아야 합니다.
#   이 파일에서 실전에서 자주 쓰이는 패턴들을 배워 봅시다.
#
#   ■ 실행: python api_design.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import json
import copy


# ─────────────────────────────────────────────────────────────────────
# ■ 샘플 데이터
# ─────────────────────────────────────────────────────────────────────
STUDENTS_DB = {
    1: {"id": 1, "name": "민수", "grade": 3, "score": 92, "club": "축구부"},
    2: {"id": 2, "name": "지우", "grade": 2, "score": 88, "club": "미술부"},
    3: {"id": 3, "name": "서연", "grade": 3, "score": 95, "club": "과학부"},
}


def lesson1_openapi_swagger():
    # =========================================================================
    #   레슨 1 — OpenAPI / Swagger 개념
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 1 : OpenAPI / Swagger 개념             │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ OpenAPI = API의 "설명서 작성 규격"
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     가구 조립 설명서를 상상해 보세요.
    #     어떤 부품이 있고, 어떻게 조립하고, 어떤 결과물이 나오는지
    #     표준 양식으로 적어 놓은 것이 OpenAPI 명세서입니다.
    #
    #   Swagger는 OpenAPI 명세서를 예쁘게 보여 주는 도구입니다.
    #   웹 브라우저에서 API를 테스트할 수도 있습니다!
    #

    # OpenAPI 명세서 예시 (YAML/JSON 형식)
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "학교 학생 관리 API",
            "version": "1.0.0",
            "description": "학생 정보를 관리하는 REST API",
        },
        "paths": {
            "/students": {
                "get": {
                    "summary": "학생 목록 조회",
                    "parameters": [
                        {"name": "grade", "in": "query", "type": "integer"},
                    ],
                    "responses": {
                        "200": {"description": "성공"},
                    },
                },
                "post": {
                    "summary": "학생 등록",
                    "requestBody": {"content": "application/json"},
                    "responses": {
                        "201": {"description": "생성 성공"},
                        "400": {"description": "잘못된 요청"},
                    },
                },
            },
        },
    }

    print("  OpenAPI 명세서 예시:")
    print(json.dumps(openapi_spec, indent=4, ensure_ascii=False))
    print()
    print("  이 명세서를 작성하면:")
    print("    1. Swagger UI에서 API 문서를 자동 생성")
    print("    2. 프론트엔드 개발자가 API를 바로 이해 가능")
    print("    3. 클라이언트 코드 자동 생성 가능 (codegen)")
    print("    4. API 테스트 자동화 가능")
    print()


def lesson2_idempotency():
    # =========================================================================
    #   레슨 2 — 멱등성 (Idempotency)
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 2 : 멱등성 (Idempotency)              │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 멱등성 = "같은 요청을 여러 번 보내도 결과가 같은 성질"
    # ─────────────────────────────────────────────────────────────────────
    #
    #   읽는 법: "멱등성" (べき等性)
    #
    #   비유:
    #     엘리베이터 버튼을 한 번 누르나 열 번 누르나 결과는 같습니다.
    #     → 이것이 멱등(idempotent)입니다!
    #
    #     반면, 장바구니 "추가" 버튼을 누를 때마다
    #     상품이 하나씩 더 들어갑니다.
    #     → 이것은 멱등하지 않습니다!
    #
    #   HTTP 메서드별 멱등성:
    #     GET    → 멱등 [O] (여러 번 조회해도 결과 같음)
    #     PUT    → 멱등 [O] (같은 값으로 덮어쓰면 결과 같음)
    #     DELETE → 멱등 [O] (이미 삭제된 걸 다시 삭제해도 결과 같음)
    #     POST   → 멱등 [X] (게시글 작성 → 매번 새 글이 생김!)
    #     PATCH  → 보통 멱등 [X] (구현에 따라 다름)
    #

    db = copy.deepcopy(STUDENTS_DB)

    print("  [PUT은 멱등] PUT /students/1  {name: '민수', score: 100}")
    for i in range(3):
        db[1] = {"id": 1, "name": "민수", "grade": 3, "score": 100, "club": "축구부"}
        print(f"    {i + 1}번째 PUT → 점수: {db[1]['score']}  (항상 같음)")
    print()

    print("  [POST는 비멱등] POST /students  {name: '새학생'}")
    next_id = max(db.keys()) + 1
    for i in range(3):
        db[next_id] = {"id": next_id, "name": "새학생"}
        print(f"    {i + 1}번째 POST → 학생 id={next_id} 생성됨  (매번 새로 생김!)")
        next_id += 1
    print()

    # 멱등성 키
    print("  [해결책] Idempotency Key")
    print("    POST 요청에 고유 키를 붙여서 중복 실행을 방지!")
    print("    예: POST /payments")
    print("        Idempotency-Key: pay-20260321-001")
    print("    → 같은 키로 다시 요청하면 이전 결과를 그대로 반환")
    print("    → 결제가 중복 실행되지 않음!")
    print()


def lesson3_put_vs_patch():
    # =========================================================================
    #   레슨 3 — PUT vs PATCH
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 3 : PUT vs PATCH                      │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ PUT = "전체 교체",  PATCH = "부분 수정"
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     PUT  = 낡은 타이어 4개를 전부 새것으로 교체
    #     PATCH = 펑크 난 타이어 1개만 수리
    #
    #   PUT 주의사항:
    #     보내지 않은 필드는 null/빈값으로 덮어씌워질 수 있음!
    #

    original = {"id": 1, "name": "민수", "grade": 3, "score": 92, "club": "축구부"}
    print(f"  원본 데이터: {json.dumps(original, ensure_ascii=False)}")
    print()

    # PUT: 전체 교체
    print("  [PUT] PUT /students/1  {name: '민수', grade: 3, score: 100, club: '축구부'}")
    put_data = {"id": 1, "name": "민수", "grade": 3, "score": 100, "club": "축구부"}
    result_put = put_data  # 전체 교체
    print(f"  결과: {json.dumps(result_put, ensure_ascii=False)}")
    print("  → 모든 필드를 다 보내야 합니다!")
    print()

    # PUT에서 필드를 빠뜨리면?
    print("  [PUT 실수] PUT /students/1  {name: '민수', score: 100}")
    print("  → club과 grade가 빠졌으므로 null이 될 수 있음! 위험!")
    print()

    # PATCH: 부분 수정
    print("  [PATCH] PATCH /students/1  {score: 100}")
    patched = copy.copy(original)
    patched["score"] = 100  # score만 수정
    print(f"  결과: {json.dumps(patched, ensure_ascii=False)}")
    print("  → score만 보냈는데 나머지 필드는 그대로 유지!")
    print()

    print("  정리:")
    print("    PUT   → 리소스 전체를 대체 (빠진 필드 = 삭제될 수 있음)")
    print("    PATCH → 보낸 필드만 수정 (안 보낸 필드 = 그대로 유지)")
    print("    실무에서는 PATCH를 더 자주 사용합니다!")
    print()


def lesson4_bulk_operations():
    # =========================================================================
    #   레슨 4 — 벌크 작업 (Bulk Operations)
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 4 : 벌크 작업 (Bulk Operations)       │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 벌크 작업 = "여러 건을 한 번에 처리"
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     택배를 1개씩 보내면 배송비가 10번 듭니다.
    #     하지만 10개를 하나의 큰 상자에 넣어 보내면 배송비 1번!
    #     → 네트워크 비용을 줄이고 속도를 높입니다.
    #
    #   설계 방법:
    #     POST /students/bulk
    #     Body: [학생1, 학생2, 학생3, ...]
    #

    def bulk_create(students_data):
        """여러 학생을 한 번에 등록"""
        results = []
        next_id = max(STUDENTS_DB.keys()) + 1

        for i, data in enumerate(students_data):
            if "name" not in data:
                results.append({
                    "index": i,
                    "status": "error",
                    "message": "이름이 누락되었습니다",
                })
            else:
                results.append({
                    "index": i,
                    "status": "created",
                    "id": next_id,
                    "name": data["name"],
                })
                next_id += 1

        success_count = sum(1 for r in results if r["status"] == "created")
        error_count = sum(1 for r in results if r["status"] == "error")

        return {
            "total": len(students_data),
            "success": success_count,
            "errors": error_count,
            "results": results,
        }

    batch = [
        {"name": "하준", "grade": 1},
        {"name": "예린", "grade": 2},
        {"grade": 1},  # 이름 누락!
        {"name": "도윤", "grade": 3},
    ]

    print("  POST /students/bulk")
    print(f"  요청: {json.dumps(batch, ensure_ascii=False)}")
    print()

    result = bulk_create(batch)
    print("  응답:")
    print(json.dumps(result, indent=4, ensure_ascii=False))
    print()

    print("  핵심: 일부가 실패해도 나머지는 성공할 수 있으므로")
    print("       각 항목별 결과를 따로 알려 줘야 합니다!")
    print()


def lesson5_webhook():
    # =========================================================================
    #   레슨 5 — Webhook 패턴
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 5 : Webhook 패턴                      │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Webhook = "이벤트가 발생하면 서버가 클라이언트에게 알려 주는 것"
    # ─────────────────────────────────────────────────────────────────────
    #
    #   보통 API:
    #     클라이언트 → 서버: "새 주문 있어?" (매번 물어봄 = 폴링)
    #     클라이언트 → 서버: "새 주문 있어?" (또 물어봄)
    #     클라이언트 → 서버: "새 주문 있어?" (또... 낭비!)
    #
    #   Webhook:
    #     서버 → 클라이언트: "새 주문이 들어왔어!" (이벤트 발생 시만!)
    #
    #   비유:
    #     폴링 = 매일 우체통을 확인하러 나가기
    #     Webhook = 택배 기사가 문 앞에 도착하면 초인종을 누르기
    #
    #   등록 흐름:
    #     1. 클라이언트가 "이 URL로 알려줘" 등록
    #        POST /webhooks  {url: "https://my-app.com/on-new-student", event: "student.created"}
    #     2. 이벤트 발생 시 서버가 해당 URL로 POST 요청
    #

    webhook_registry = []

    def register_webhook(url, event):
        """웹훅 등록"""
        webhook = {"id": len(webhook_registry) + 1, "url": url, "event": event}
        webhook_registry.append(webhook)
        return webhook

    def trigger_event(event, data):
        """이벤트 발생 시 등록된 웹훅으로 알림"""
        notifications = []
        for hook in webhook_registry:
            if hook["event"] == event:
                notification = {
                    "webhook_id": hook["id"],
                    "url": hook["url"],
                    "payload": {
                        "event": event,
                        "data": data,
                        "timestamp": "2026-03-21T10:30:00Z",
                    },
                }
                notifications.append(notification)
        return notifications

    # 웹훅 등록
    print("  [1단계] 웹훅 등록")
    hook1 = register_webhook("https://my-app.com/on-new-student", "student.created")
    hook2 = register_webhook("https://admin.com/notify", "student.created")
    hook3 = register_webhook("https://my-app.com/on-score-change", "score.updated")
    print(f"    등록된 웹훅:")
    for h in webhook_registry:
        print(f"      #{h['id']} {h['event']} → {h['url']}")
    print()

    # 이벤트 발생
    print("  [2단계] 학생 등록 이벤트 발생!")
    notifications = trigger_event("student.created", {"id": 4, "name": "하준"})
    for n in notifications:
        print(f"    → POST {n['url']}")
        print(f"      Body: {json.dumps(n['payload'], ensure_ascii=False)}")
    print()

    print("  [3단계] 점수 변경 이벤트 발생!")
    notifications = trigger_event("score.updated", {"id": 1, "name": "민수", "score": 95})
    for n in notifications:
        print(f"    → POST {n['url']}")
        print(f"      Body: {json.dumps(n['payload'], ensure_ascii=False)}")
    print()

    print("  Webhook 설계 시 주의사항:")
    print("    1. 재시도 로직: 상대방 서버가 응답 안 하면 3번까지 재시도")
    print("    2. 서명 검증: 요청이 진짜 우리 서버에서 온 건지 확인")
    print("    3. 타임아웃: 상대방이 너무 오래 걸리면 끊기")
    print("    4. 이벤트 로그: 어떤 알림을 보냈는지 기록")
    print()


def lesson6_api_documentation():
    # =========================================================================
    #   레슨 6 — API 문서화 모범 사례
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 6 : API 문서화 모범 사례               │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 좋은 API 문서에 꼭 들어가야 할 것들
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     레고 설명서가 그림만 있고 글이 없으면 조립할 수 있을까요?
    #     API 문서도 마찬가지로, 사용법을 명확하게 적어야 합니다!
    #

    doc_example = {
        "endpoint": "POST /v1/students",
        "description": "새 학생을 등록합니다",
        "authentication": "Bearer Token 필요",
        "request": {
            "headers": {"Content-Type": "application/json"},
            "body": {
                "name": "(필수) 학생 이름, 1~50자",
                "grade": "(필수) 학년, 1/2/3",
                "score": "(선택) 점수, 0~100, 기본값: 0",
                "club": "(선택) 동아리명",
            },
        },
        "responses": {
            "201": {"body": {"id": 4, "name": "하준", "grade": 1}},
            "400": {"body": {"error_code": "ERR_2001", "message": "필수 필드 누락"}},
            "401": {"body": {"error_code": "ERR_4001", "message": "인증 필요"}},
        },
        "example_curl": 'curl -X POST /v1/students -H "Authorization: Bearer ..." -d \'{"name":"하준","grade":1}\'',
    }

    print("  좋은 API 문서 예시:")
    print(json.dumps(doc_example, indent=4, ensure_ascii=False))
    print()

    print("  문서에 꼭 포함할 것:")
    print("    1. 엔드포인트 URL과 HTTP 메서드")
    print("    2. 필수/선택 파라미터와 타입")
    print("    3. 성공/실패 응답 예시")
    print("    4. 인증 방법")
    print("    5. 실행 가능한 curl 예시")
    print("    6. 에러 코드 목록")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("  REST API 08단계 : API 설계 고급 패턴")
    print("=" * 72)
    print()

    lesson1_openapi_swagger()
    lesson2_idempotency()
    lesson3_put_vs_patch()
    lesson4_bulk_operations()
    lesson5_webhook()
    lesson6_api_documentation()
