# =============================================================================
#   REST API 학습 01단계: HTTP CRUD
# =============================================================================

students = [
    {"id": 1, "name": "민수"},
    {"id": 2, "name": "지우"},
]


def lesson1_get():
    # GET = 보기
    print("[레슨 1] GET /students")
    print(students)
    print()


def lesson2_post():
    # POST = 만들기
    print("[레슨 2] POST /students")
    new_student = {"id": 3, "name": "서연"}
    students.append(new_student)
    print("추가 후 목록:", students)
    print()


def lesson3_patch():
    # PATCH = 일부 수정하기
    print("[레슨 3] PATCH /students/2")
    students[1]["name"] = "지우(수정)"
    print("수정 후 목록:", students)
    print()


def lesson4_delete():
    # DELETE = 지우기
    print("[레슨 4] DELETE /students/1")
    removed = students.pop(0)
    print("삭제한 학생:", removed)
    print("남은 목록:", students)
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("  REST API 01단계 : HTTP CRUD")
    print("=" * 60)
    print()

    lesson1_get()
    lesson2_post()
    lesson3_patch()
    lesson4_delete()
