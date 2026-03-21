# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   REST API 학습 05단계: 페이지네이션과 필터링
#   ─ Offset, Cursor, 필터링, 정렬, 필드 선택, HATEOAS 링크 ─
#
#   데이터가 1만 건이면 한 번에 다 보내면 안 됩니다!
#   "한 페이지씩 나눠서" 보내는 것이 페이지네이션입니다.
#
#   ■ 실행: python pagination.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import json

# ─────────────────────────────────────────────────────────────────────
# ■ 샘플 데이터: 학생 20명
# ─────────────────────────────────────────────────────────────────────
ALL_STUDENTS = [
    {"id": i, "name": name, "grade": grade, "score": score, "club": club}
    for i, (name, grade, score, club) in enumerate([
        ("민수", 3, 92, "축구부"), ("지우", 2, 88, "미술부"),
        ("서연", 3, 95, "과학부"), ("하준", 1, 76, "축구부"),
        ("예린", 2, 91, "미술부"), ("도윤", 3, 84, "과학부"),
        ("수아", 1, 97, "미술부"), ("시우", 2, 72, "축구부"),
        ("하은", 3, 89, "과학부"), ("지호", 1, 81, "축구부"),
        ("윤서", 2, 93, "미술부"), ("건우", 3, 78, "과학부"),
        ("소율", 1, 86, "미술부"), ("은우", 2, 90, "축구부"),
        ("채원", 3, 94, "과학부"), ("태윤", 1, 73, "축구부"),
        ("주아", 2, 87, "미술부"), ("현우", 3, 82, "과학부"),
        ("다은", 1, 96, "미술부"), ("준서", 2, 79, "축구부"),
    ], start=1)
]


def lesson1_offset_pagination():
    # =========================================================================
    #   레슨 1 — Offset 페이지네이션
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 1 : Offset 페이지네이션                │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Offset 방식 = "몇 번째부터 몇 개 보여줘"
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     책의 목차에서 "37페이지부터 5줄 보여줘"와 같은 방식
    #
    #   URL 예시:
    #     GET /students?page=2&size=5
    #     → 2페이지, 한 페이지에 5명
    #     → offset = (2-1) * 5 = 5번째부터 5개
    #

    def get_page(page, size):
        """Offset 방식 페이지네이션"""
        offset = (page - 1) * size
        items = ALL_STUDENTS[offset:offset + size]
        total = len(ALL_STUDENTS)
        total_pages = (total + size - 1) // size  # 올림 나눗셈

        return {
            "data": items,
            "page": page,
            "size": size,
            "total": total,
            "total_pages": total_pages,
        }

    # 1페이지 조회
    result = get_page(page=1, size=5)
    print(f"  GET /students?page=1&size=5")
    print(f"  총 {result['total']}명 중 {result['page']}페이지 (전체 {result['total_pages']}페이지)")
    for s in result["data"]:
        print(f"    id={s['id']} {s['name']} ({s['grade']}학년, {s['score']}점)")
    print()

    # 3페이지 조회
    result = get_page(page=3, size=5)
    print(f"  GET /students?page=3&size=5")
    print(f"  {result['page']}페이지:")
    for s in result["data"]:
        print(f"    id={s['id']} {s['name']} ({s['grade']}학년, {s['score']}점)")
    print()

    print("  장점: 구현이 간단하고 '3페이지로 점프' 가능")
    print("  단점: 중간에 데이터가 추가/삭제되면 항목이 빠지거나 중복될 수 있음")
    print()


def lesson2_cursor_pagination():
    # =========================================================================
    #   레슨 2 — Cursor 페이지네이션
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 2 : Cursor 페이지네이션                │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Cursor 방식 = "이 항목 다음부터 몇 개 보여줘"
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     책갈피를 꽂아 두고 "여기서부터 5줄 더 읽어줘"
    #     → 중간에 새 내용이 끼어들어도 내 책갈피 위치는 변하지 않음!
    #
    #   URL 예시:
    #     GET /students?cursor=5&limit=5
    #     → id가 5인 학생 다음부터 5명
    #

    def get_after_cursor(cursor_id, limit):
        """Cursor 방식 페이지네이션"""
        # cursor_id 이후의 항목들만 가져오기
        remaining = [s for s in ALL_STUDENTS if s["id"] > cursor_id]
        items = remaining[:limit]
        next_cursor = items[-1]["id"] if items else None

        return {
            "data": items,
            "next_cursor": next_cursor,
            "has_more": len(remaining) > limit,
        }

    # 처음부터
    print("  GET /students?cursor=0&limit=5  (처음부터)")
    result = get_after_cursor(cursor_id=0, limit=5)
    for s in result["data"]:
        print(f"    id={s['id']} {s['name']}")
    print(f"  다음 커서: {result['next_cursor']}, 더 있나: {result['has_more']}")
    print()

    # 이어서 다음 페이지
    print(f"  GET /students?cursor={result['next_cursor']}&limit=5  (이어서)")
    result2 = get_after_cursor(cursor_id=result["next_cursor"], limit=5)
    for s in result2["data"]:
        print(f"    id={s['id']} {s['name']}")
    print(f"  다음 커서: {result2['next_cursor']}, 더 있나: {result2['has_more']}")
    print()

    print("  장점: 데이터 추가/삭제에도 빠짐·중복 없음 (SNS 피드에 적합)")
    print("  단점: '5페이지로 점프'가 불가능, 항상 순서대로만 이동")
    print()


def lesson3_filtering():
    # =========================================================================
    #   레슨 3 — 필터링 (Query Parameters)
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 3 : 필터링                             │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 필터링 = "조건에 맞는 것만 골라줘"
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     도서관에서 "3학년 책만 보여주세요" 하는 것
    #
    #   URL 예시:
    #     GET /students?grade=3
    #     GET /students?grade=3&club=과학부
    #     GET /students?score_min=90
    #

    def filter_students(grade=None, club=None, score_min=None, score_max=None):
        """조건에 맞는 학생만 필터링"""
        result = ALL_STUDENTS[:]

        if grade is not None:
            result = [s for s in result if s["grade"] == grade]
        if club is not None:
            result = [s for s in result if s["club"] == club]
        if score_min is not None:
            result = [s for s in result if s["score"] >= score_min]
        if score_max is not None:
            result = [s for s in result if s["score"] <= score_max]

        return result

    # 3학년만
    print("  GET /students?grade=3")
    for s in filter_students(grade=3):
        print(f"    {s['name']} ({s['score']}점, {s['club']})")
    print()

    # 과학부이면서 90점 이상
    print("  GET /students?club=과학부&score_min=90")
    for s in filter_students(club="과학부", score_min=90):
        print(f"    {s['name']} ({s['score']}점)")
    print()


def lesson4_sorting():
    # =========================================================================
    #   레슨 4 — 정렬
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 4 : 정렬                               │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 정렬 = "어떤 기준으로 줄 세워줘"
    # ─────────────────────────────────────────────────────────────────────
    #
    #   URL 예시:
    #     GET /students?sort=score       → 점수 오름차순
    #     GET /students?sort=-score      → 점수 내림차순 (- 붙이기)
    #     GET /students?sort=grade,-score → 학년 오름차순 후 점수 내림차순
    #

    def sort_students(sort_fields):
        """정렬 필드 문자열을 파싱하여 정렬"""
        result = ALL_STUDENTS[:]
        fields = sort_fields.split(",")

        # 뒤에서부터 정렬해야 다중 정렬이 올바르게 동작
        for field in reversed(fields):
            if field.startswith("-"):
                key = field[1:]
                result.sort(key=lambda s: s[key], reverse=True)
            else:
                result.sort(key=lambda s: s[field])
        return result

    # 점수 내림차순 (상위 5명)
    print("  GET /students?sort=-score  (점수 높은 순)")
    for s in sort_students("-score")[:5]:
        print(f"    {s['name']} {s['score']}점 ({s['grade']}학년)")
    print()

    # 학년 오름차순 → 점수 내림차순
    print("  GET /students?sort=grade,-score  (학년별, 점수 높은 순)")
    for s in sort_students("grade,-score")[:8]:
        print(f"    {s['grade']}학년 {s['name']} {s['score']}점")
    print()


def lesson5_field_selection():
    # =========================================================================
    #   레슨 5 — 필드 선택 (Sparse Fieldsets)
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 5 : 필드 선택 (Sparse Fieldsets)       │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 필드 선택 = "필요한 정보만 골라서 보내줘"
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     식당 메뉴판에서 전체를 다 읽지 않고
    #     "이름이랑 가격만 알려주세요" 하는 것
    #     → 데이터 양이 줄어서 네트워크 비용 절약!
    #
    #   URL 예시:
    #     GET /students?fields=name,score
    #

    def select_fields(students, fields):
        """지정한 필드만 골라서 반환"""
        return [{key: s[key] for key in fields if key in s} for s in students]

    print("  GET /students?fields=name,score  (이름과 점수만)")
    slim = select_fields(ALL_STUDENTS[:5], ["name", "score"])
    for s in slim:
        print(f"    {s}")
    print()

    print("  GET /students?fields=id,name  (ID와 이름만)")
    slim = select_fields(ALL_STUDENTS[:5], ["id", "name"])
    for s in slim:
        print(f"    {s}")
    print()

    print("  효과: 불필요한 데이터를 줄여서 응답 크기를 줄이고")
    print("       모바일처럼 대역폭이 제한된 환경에서 특히 유용합니다.")
    print()


def lesson6_hateoas_links():
    # =========================================================================
    #   레슨 6 — HATEOAS 링크
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 6 : HATEOAS 링크                      │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ HATEOAS = 응답에 "다음에 할 수 있는 동작"의 링크를 함께 보내는 것
    # ─────────────────────────────────────────────────────────────────────
    #
    #   읽는 법: "헤이티오스" 또는 "에이치에이티이오에이에스"
    #   풀네임: Hypermedia As The Engine Of Application State
    #
    #   비유:
    #     네비게이션이 "지금 위치에서 갈 수 있는 곳"을 알려 주는 것처럼
    #     API 응답이 "지금 이 데이터에서 할 수 있는 일"을 링크로 알려 줍니다.
    #
    #   장점:
    #     클라이언트가 URL을 하드코딩하지 않아도 됨
    #     서버가 URL을 바꿔도 클라이언트가 깨지지 않음
    #

    def get_students_with_links(page, size):
        """HATEOAS 스타일 응답"""
        offset = (page - 1) * size
        items = ALL_STUDENTS[offset:offset + size]
        total_pages = (len(ALL_STUDENTS) + size - 1) // size

        response = {
            "data": [{"id": s["id"], "name": s["name"]} for s in items],
            "_links": {
                "self": f"/students?page={page}&size={size}",
            }
        }

        if page > 1:
            response["_links"]["prev"] = f"/students?page={page - 1}&size={size}"
            response["_links"]["first"] = f"/students?page=1&size={size}"

        if page < total_pages:
            response["_links"]["next"] = f"/students?page={page + 1}&size={size}"
            response["_links"]["last"] = f"/students?page={total_pages}&size={size}"

        return response

    result = get_students_with_links(page=2, size=5)
    print("  GET /students?page=2&size=5 (HATEOAS 응답)")
    print()
    print(json.dumps(result, indent=4, ensure_ascii=False))
    print()
    print("  핵심: _links 안에 prev, next, first, last가 있으니")
    print("       클라이언트는 이 링크만 따라가면 됩니다.")
    print("       마치 웹페이지에서 '다음' 버튼을 누르는 것처럼!")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("  REST API 05단계 : 페이지네이션과 필터링")
    print("=" * 72)
    print()

    lesson1_offset_pagination()
    lesson2_cursor_pagination()
    lesson3_filtering()
    lesson4_sorting()
    lesson5_field_selection()
    lesson6_hateoas_links()
