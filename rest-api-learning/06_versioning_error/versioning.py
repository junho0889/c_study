# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   REST API 학습 06단계: 버전 관리와 에러 응답
#   ─ URL 버전, 헤더 버전, RFC 7807 에러, 커스텀 에러 코드, 유효성 검증 ─
#
#   API가 변하면 기존 사용자가 깨질 수 있습니다.
#   버전을 매기면 옛날 사용자와 새 사용자가 함께 공존할 수 있습니다.
#
#   ■ 실행: python versioning.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import json


def lesson1_url_versioning():
    # =========================================================================
    #   레슨 1 — URL 버전 관리 (/v1/, /v2/)
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 1 : URL 버전 관리                      │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ URL 버전 = URL 경로에 버전 번호를 넣는 방식
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     교과서 개정판과 같습니다.
    #     수학 교과서 1판을 쓰는 학교가 있고,
    #     수학 교과서 2판을 쓰는 학교가 있을 때
    #     서점에는 두 판이 다 있어야 합니다!
    #
    #   예시:
    #     GET /v1/students → 옛날 버전 (이름만 반환)
    #     GET /v2/students → 새 버전 (이름 + 점수 + 학년)
    #

    def get_students_v1():
        """v1: 이름만 반환하는 초기 버전"""
        return [
            {"id": 1, "name": "민수"},
            {"id": 2, "name": "지우"},
        ]

    def get_students_v2():
        """v2: 더 많은 정보를 포함하는 새 버전"""
        return [
            {"id": 1, "name": "민수", "grade": 3, "score": 92, "email": "minsu@school.kr"},
            {"id": 2, "name": "지우", "grade": 2, "score": 88, "email": "jiwoo@school.kr"},
        ]

    print("  GET /v1/students  (이전 버전)")
    print(f"    {json.dumps(get_students_v1(), ensure_ascii=False)}")
    print()
    print("  GET /v2/students  (새 버전)")
    print(f"    {json.dumps(get_students_v2(), ensure_ascii=False, indent=4)}")
    print()
    print("  장점: URL만 보면 어떤 버전인지 바로 알 수 있음")
    print("  단점: URL이 바뀌므로 클라이언트 코드 수정 필요")
    print()


def lesson2_header_versioning():
    # =========================================================================
    #   레슨 2 — 헤더 버전 관리
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 2 : 헤더 버전 관리                     │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 헤더 버전 = 같은 URL인데 헤더로 버전을 구분
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     같은 식당인데 "한국어 메뉴판"과 "영어 메뉴판"을 요청하는 것
    #     같은 음식(URL)이지만 어떤 언어(버전)로 보여줄지가 다름!
    #
    #   방법 1: Accept 헤더
    #     Accept: application/vnd.school.v2+json
    #
    #   방법 2: 커스텀 헤더
    #     X-API-Version: 2
    #

    def handle_request(url, headers):
        """헤더 버전에 따라 다른 응답"""
        version = headers.get("X-API-Version", "1")

        if version == "1":
            return {"version": 1, "data": [{"name": "민수"}, {"name": "지우"}]}
        elif version == "2":
            return {
                "version": 2,
                "data": [
                    {"name": "민수", "grade": 3, "score": 92},
                    {"name": "지우", "grade": 2, "score": 88},
                ],
            }
        else:
            return {"error": f"지원하지 않는 버전: {version}"}

    # 버전 1 요청
    print("  GET /students")
    print("  X-API-Version: 1")
    r1 = handle_request("/students", {"X-API-Version": "1"})
    print(f"  응답: {json.dumps(r1, ensure_ascii=False)}")
    print()

    # 버전 2 요청
    print("  GET /students")
    print("  X-API-Version: 2")
    r2 = handle_request("/students", {"X-API-Version": "2"})
    print(f"  응답: {json.dumps(r2, ensure_ascii=False)}")
    print()

    print("  장점: URL이 깔끔하게 유지됨")
    print("  단점: 브라우저에서 테스트하기 어려움 (헤더를 직접 넣어야 하니까)")
    print()


def lesson3_error_format_rfc7807():
    # =========================================================================
    #   레슨 3 — 에러 응답 형식 (RFC 7807)
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 3 : RFC 7807 에러 형식                 │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ RFC 7807 = 에러를 표준적으로 표현하는 약속
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     병원 진단서 양식이 전국 어디서나 같은 것처럼,
    #     에러 응답도 정해진 양식대로 보내면 모든 클라이언트가 이해할 수 있습니다.
    #
    #   RFC 7807 필수 필드:
    #     type     → 에러 종류를 설명하는 URL
    #     title    → 사람이 읽을 수 있는 짧은 제목
    #     status   → HTTP 상태 코드
    #     detail   → 이번 에러의 구체적 설명
    #     instance → 이번 요청의 고유 경로
    #

    def create_error_response(error_type, title, status, detail, instance):
        """RFC 7807 형식의 에러 응답 생성"""
        return {
            "type": f"https://api.school.kr/errors/{error_type}",
            "title": title,
            "status": status,
            "detail": detail,
            "instance": instance,
        }

    # 404 에러
    error_404 = create_error_response(
        error_type="student-not-found",
        title="학생을 찾을 수 없습니다",
        status=404,
        detail="ID가 999인 학생이 존재하지 않습니다.",
        instance="/v1/students/999",
    )
    print("  GET /v1/students/999 → 404")
    print(json.dumps(error_404, indent=4, ensure_ascii=False))
    print()

    # 400 에러
    error_400 = create_error_response(
        error_type="invalid-request",
        title="잘못된 요청입니다",
        status=400,
        detail="'score' 필드는 0 이상 100 이하여야 합니다. 전달된 값: 150",
        instance="/v1/students/1",
    )
    print("  PATCH /v1/students/1  {score: 150} → 400")
    print(json.dumps(error_400, indent=4, ensure_ascii=False))
    print()


def lesson4_custom_error_codes():
    # =========================================================================
    #   레슨 4 — 커스텀 에러 코드
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 4 : 커스텀 에러 코드                    │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 커스텀 에러 코드 = HTTP 상태 코드만으로는 부족할 때
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     병원에서 "아픕니다"(400)만으로는 부족하니
    #     "감기입니다"(ERR_1001), "독감입니다"(ERR_1002) 처럼
    #     더 구체적인 진단명을 붙이는 것!
    #
    #   HTTP 상태 코드 400 하나에도 여러 이유가 있을 수 있습니다:
    #     ERR_2001 = 필수 필드 누락
    #     ERR_2002 = 값 범위 초과
    #     ERR_2003 = 형식 오류 (숫자여야 하는데 문자 입력)
    #

    ERROR_CATALOG = {
        "ERR_1001": {"status": 404, "message": "학생을 찾을 수 없습니다"},
        "ERR_1002": {"status": 404, "message": "과목을 찾을 수 없습니다"},
        "ERR_2001": {"status": 400, "message": "필수 필드가 누락되었습니다"},
        "ERR_2002": {"status": 400, "message": "값이 허용 범위를 벗어났습니다"},
        "ERR_2003": {"status": 400, "message": "데이터 형식이 올바르지 않습니다"},
        "ERR_3001": {"status": 403, "message": "이 작업을 수행할 권한이 없습니다"},
        "ERR_5001": {"status": 500, "message": "서버 내부 오류가 발생했습니다"},
    }

    def make_error(code, detail):
        info = ERROR_CATALOG.get(code, {"status": 500, "message": "알 수 없는 오류"})
        return {
            "error_code": code,
            "status": info["status"],
            "message": info["message"],
            "detail": detail,
        }

    print("  에러 코드 카탈로그:")
    for code, info in ERROR_CATALOG.items():
        print(f"    {code} → {info['status']} {info['message']}")
    print()

    # 사용 예시
    err = make_error("ERR_2002", "score 필드: 입력값 150, 허용 범위 0~100")
    print("  사용 예시:")
    print(f"    {json.dumps(err, ensure_ascii=False, indent=4)}")
    print()

    print("  핵심: 클라이언트는 error_code를 보고 정확한 문제를 파악할 수 있습니다.")
    print("       프론트엔드에서 에러 코드별로 다른 메시지를 보여 줄 수 있습니다!")
    print()


def lesson5_validation_errors():
    # =========================================================================
    #   레슨 5 — 유효성 검증 에러
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 5 : 유효성 검증 에러                    │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 유효성 검증 = 데이터가 규칙에 맞는지 확인
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     시험 답안지 제출 전 검사:
    #     "이름 칸이 비어 있네요!" (필수 필드 누락)
    #     "학번은 숫자로 써야 해요!" (타입 오류)
    #     "점수는 0~100 사이로 쓰세요!" (범위 오류)
    #
    #   여러 필드에 동시에 오류가 있을 수 있으므로
    #   에러 목록을 배열로 반환하는 것이 좋습니다.
    #

    def validate_student(data):
        """학생 데이터 유효성 검증"""
        errors = []

        if "name" not in data or not data["name"].strip():
            errors.append({
                "field": "name",
                "code": "REQUIRED",
                "message": "이름은 필수 입력 항목입니다",
            })

        if "score" in data:
            if not isinstance(data["score"], (int, float)):
                errors.append({
                    "field": "score",
                    "code": "INVALID_TYPE",
                    "message": "점수는 숫자여야 합니다",
                })
            elif data["score"] < 0 or data["score"] > 100:
                errors.append({
                    "field": "score",
                    "code": "OUT_OF_RANGE",
                    "message": "점수는 0~100 사이여야 합니다",
                })

        if "grade" in data:
            if data["grade"] not in [1, 2, 3]:
                errors.append({
                    "field": "grade",
                    "code": "INVALID_VALUE",
                    "message": "학년은 1, 2, 3 중 하나여야 합니다",
                })

        if "email" in data:
            if "@" not in data.get("email", ""):
                errors.append({
                    "field": "email",
                    "code": "INVALID_FORMAT",
                    "message": "이메일 형식이 올바르지 않습니다 (@ 필요)",
                })

        return errors

    # 정상 데이터
    print("  [테스트 1] 정상 데이터")
    valid_data = {"name": "민수", "score": 92, "grade": 3, "email": "minsu@school.kr"}
    errs = validate_student(valid_data)
    print(f"    입력: {valid_data}")
    print(f"    오류: 없음 [O]") if not errs else None
    print()

    # 오류 가득한 데이터
    print("  [테스트 2] 여러 오류가 있는 데이터")
    bad_data = {"name": "", "score": 150, "grade": 5, "email": "no-at-sign"}
    errs = validate_student(bad_data)
    print(f"    입력: {bad_data}")
    print("    오류 목록:")
    response = {
        "status": 400,
        "message": "유효성 검증 실패",
        "errors": errs,
    }
    print(json.dumps(response, indent=4, ensure_ascii=False))
    print()

    print("  핵심: 오류 하나만 알려 주지 말고, 가능한 모든 오류를 한꺼번에 알려 주세요!")
    print("       사용자가 한 번에 고칠 수 있도록 배려하는 것입니다.")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("  REST API 06단계 : 버전 관리와 에러 응답")
    print("=" * 72)
    print()

    lesson1_url_versioning()
    lesson2_header_versioning()
    lesson3_error_format_rfc7807()
    lesson4_custom_error_codes()
    lesson5_validation_errors()
