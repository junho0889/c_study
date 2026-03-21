def build_student_routes(student_id):
    return [
        f"GET /students/{student_id}",
        f"PATCH /students/{student_id}",
        f"DELETE /students/{student_id}",
        f"GET /students/{student_id}/scores",
    ]


def lesson1_resource_first_route_design():
    print("[레슨 1] 경로는 동사보다 자원을 중심으로 읽히게 만들기")
    print()

    routes = [
        "GET /students",
        "POST /students",
        "GET /students/7",
        "PATCH /students/7",
    ]

    for route in routes:
        print(" ", route)

    print("  설명: URL은 '무엇을 다루는지'를 보여 주고, 행동은 GET/POST/PATCH가 말해 줍니다.")
    print()


def lesson2_path_parameter_vs_query_string():
    print("[레슨 2] 한 학생 자체를 가리킬 때는 path parameter가 더 또렷함")
    print()

    print("  덜 좋은 예: GET /getStudent?id=7")
    print("  더 읽기 좋은 예: GET /students/7")
    print()
    print("  비유: '학생 서랍장 7번 칸'이라고 말하는 것이")
    print("       '학생을 가져오는데 번호는 7이야'라고 길게 설명하는 것보다 더 바로 이해됩니다.")
    print()


def lesson3_nested_resource_example():
    print("[레슨 3] 자원 안에 또 다른 자원이 있을 때")
    print()

    for route in build_student_routes(7):
        print(" ", route)

    print()
    print("  /students/7/scores 는 '7번 학생의 점수 목록'이라는 뜻입니다.")
    print("  실수 주의: /students/getScores/7 처럼 동사를 URL 한가운데 넣으면")
    print("  API 개수가 늘수록 이름 규칙이 뒤죽박죽 되기 쉽습니다.")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("REST API 02단계: 읽기 좋은 라우트 설계")
    print("=" * 72)
    print()

    lesson1_resource_first_route_design()
    lesson2_path_parameter_vs_query_string()
    lesson3_nested_resource_example()
