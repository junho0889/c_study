def choose_status_code(action, target_exists=True, payload_is_valid=True):
    if not payload_is_valid:
        return 400

    if action == "create":
        return 201

    if action == "read" and not target_exists:
        return 404

    return 200


def lesson1_status_examples():
    print("[레슨 1] 상태 코드는 서버의 결과를 짧은 숫자로 알려 준다")
    print()

    cases = {
        200: "조회 성공",
        201: "생성 성공",
        400: "요청 형식 오류",
        404: "대상 없음",
        500: "서버 내부 오류",
    }

    for code, meaning in cases.items():
        print(f"  {code}: {meaning}")
    print()


def lesson2_same_api_different_result():
    print("[레슨 2] 같은 API라도 상황에 따라 다른 코드가 나온다")
    print()

    print("  GET /students/7    ->", choose_status_code("read", target_exists=True))
    print("  GET /students/999  ->", choose_status_code("read", target_exists=False))
    print("  POST /students     ->", choose_status_code("create", payload_is_valid=True))
    print("  잘못된 JSON 전송    ->", choose_status_code("create", payload_is_valid=False))
    print()


def lesson3_how_to_think_about_codes():
    print("[레슨 3] 상태 코드를 고르는 간단한 생각법")
    print()
    print("  1. 요청 자체가 이상한가? -> 400 쪽 먼저 생각")
    print("  2. 찾는 대상이 없는가? -> 404")
    print("  3. 새로 만들어졌는가? -> 201")
    print("  4. 그 외 정상 처리인가? -> 200")
    print("  상태 코드는 서버의 짧은 표정이라고 생각하면 기억하기 쉽습니다.")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("REST API 03단계: 상태 코드")
    print("=" * 72)
    print()

    lesson1_status_examples()
    lesson2_same_api_different_result()
    lesson3_how_to_think_about_codes()
