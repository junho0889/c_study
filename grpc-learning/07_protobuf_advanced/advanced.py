# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   gRPC 학습 07단계: Protocol Buffers 심화 (파이썬 시뮬레이션)
#   ─ oneof, map, repeated, nested, enum, well-known types 개념 실습 ─
#
#   advanced.proto 파일의 개념을 파이썬으로 직접 만들어 봅니다.
#   실제 protobuf 라이브러리 없이 개념만 이해하는 연습입니다.
#
#   ■ 실행: python advanced.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import IntEnum


# ─────────────────────────────────────────────────────────────────────
# ■ Enum 정의 (proto의 enum을 파이썬으로)
# ─────────────────────────────────────────────────────────────────────

class Grade(IntEnum):
    UNSPECIFIED = 0
    FIRST = 1
    SECOND = 2
    THIRD = 3


class Club(IntEnum):
    UNSPECIFIED = 0
    SOCCER = 1
    ART = 2
    SCIENCE = 3
    MUSIC = 4


GRADE_NAMES = {Grade.FIRST: "1학년", Grade.SECOND: "2학년", Grade.THIRD: "3학년"}
CLUB_NAMES = {Club.SOCCER: "축구부", Club.ART: "미술부",
              Club.SCIENCE: "과학부", Club.MUSIC: "음악부"}


def lesson1_enum():
    # =========================================================================
    #   레슨 1 — Enum (열거형)
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 1 : Enum (열거형)                      │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ enum = 정해진 값들 중에서만 고를 수 있는 타입
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     자판기에서 버튼 1, 2, 3번만 있는 것처럼
    #     학년도 1, 2, 3만 있습니다. "7학년"은 없어요!
    #
    #   proto3 규칙:
    #     - 0번 값이 반드시 있어야 함 (기본값 = UNSPECIFIED)
    #     - 필드에 값을 안 넣으면 자동으로 0 (UNSPECIFIED)
    #

    print("  학년 enum:")
    for grade in Grade:
        name = GRADE_NAMES.get(grade, "미지정")
        print(f"    {grade.name} = {grade.value} → {name}")
    print()

    print("  동아리 enum:")
    for club in Club:
        name = CLUB_NAMES.get(club, "미지정")
        print(f"    {club.name} = {club.value} → {name}")
    print()

    # 기본값 데모
    print("  proto3 기본값:")
    default_grade = Grade(0)
    print(f"    값을 안 넣으면 → {default_grade.name} ({default_grade.value})")
    print("    → 클라이언트가 학년을 안 보내면 UNSPECIFIED로 처리됩니다!")
    print()


def lesson2_repeated():
    # =========================================================================
    #   레슨 2 — Repeated (배열/리스트)
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 2 : Repeated (배열/리스트)             │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ repeated = 같은 타입의 값을 여러 개 담을 수 있는 필드
    # ─────────────────────────────────────────────────────────────────────
    #
    #   proto:
    #     repeated string hobbies = 4;
    #     repeated int32 scores = 5;
    #
    #   비유:
    #     한 학생이 취미가 여러 개일 수 있잖아요?
    #     "축구, 그림, 게임" → 리스트로 담아야 합니다!
    #

    @dataclass
    class Student:
        id: int
        name: str
        grade: Grade
        hobbies: List[str] = field(default_factory=list)     # repeated string
        scores: List[int] = field(default_factory=list)       # repeated int32

    student = Student(
        id=1,
        name="민수",
        grade=Grade.THIRD,
        hobbies=["축구", "게임", "독서"],
        scores=[92, 88, 95, 78],
    )

    print(f"  학생: {student.name} ({GRADE_NAMES[student.grade]})")
    print(f"  취미 (repeated string): {student.hobbies}")
    print(f"  점수 (repeated int32):  {student.scores}")
    print()

    # 빈 repeated 필드
    student2 = Student(id=2, name="지우", grade=Grade.SECOND)
    print(f"  학생: {student2.name}")
    print(f"  취미: {student2.hobbies}  ← 비어 있어도 OK (기본값 = 빈 리스트)")
    print()

    print("  repeated 필드 규칙:")
    print("    - 0개 이상 가능 (비어 있어도 됨)")
    print("    - 순서가 유지됨")
    print("    - 같은 타입만 가능 (string이면 전부 string)")
    print()


def lesson3_nested_message():
    # =========================================================================
    #   레슨 3 — Nested Message (중첩 메시지)
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 3 : Nested Message (중첩 메시지)       │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 중첩 = 메시지 안에 다른 메시지를 넣기
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     러시아 인형(마트료시카)처럼 인형 안에 인형이 들어 있는 것!
    #     ClassRoom 안에 Teacher가 있고, Teacher 안에 Address가 있음!
    #

    @dataclass
    class Address:
        city: str
        district: str
        detail: str

    @dataclass
    class Teacher:
        id: int
        name: str
        home_address: Optional[Address] = None
        school_address: Optional[Address] = None

    @dataclass
    class ClassRoom:
        room_number: int
        teacher: Optional[Teacher] = None
        student_names: List[str] = field(default_factory=list)

    classroom = ClassRoom(
        room_number=302,
        teacher=Teacher(
            id=1,
            name="김선생님",
            home_address=Address("서울시", "강남구", "테헤란로 123"),
            school_address=Address("서울시", "서초구", "학교로 456"),
        ),
        student_names=["민수", "지우", "서연"],
    )

    print(f"  교실: {classroom.room_number}호")
    print(f"  담임: {classroom.teacher.name}")
    print(f"    자택: {classroom.teacher.home_address.city} "
          f"{classroom.teacher.home_address.district}")
    print(f"    학교: {classroom.teacher.school_address.city} "
          f"{classroom.teacher.school_address.district}")
    print(f"  학생: {classroom.student_names}")
    print()

    # JSON 직렬화로 구조 확인
    def to_dict(obj):
        if hasattr(obj, '__dataclass_fields__'):
            return {k: to_dict(v) for k, v in obj.__dict__.items()}
        if isinstance(obj, list):
            return [to_dict(i) for i in obj]
        return obj

    print("  JSON으로 보면:")
    print(json.dumps(to_dict(classroom), indent=4, ensure_ascii=False))
    print()


def lesson4_map_field():
    # =========================================================================
    #   레슨 4 — Map (딕셔너리)
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 4 : Map (딕셔너리)                     │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ map = 키-값 쌍으로 데이터 저장
    # ─────────────────────────────────────────────────────────────────────
    #
    #   proto:
    #     map<string, int32> subject_scores = 1;
    #
    #   비유:
    #     사물함: 번호(키) → 물건(값)
    #     성적표: 과목(키) → 점수(값)
    #

    # map<string, int32>
    subject_scores: Dict[str, int] = {
        "수학": 95,
        "영어": 88,
        "과학": 92,
        "국어": 87,
    }

    print("  성적표 (map<string, int32>):")
    for subject, score in subject_scores.items():
        bar = "#" * (score // 5)
        print(f"    {subject}: {score}점 {bar}")
    print()

    # map<int32, Student> 도 가능
    student_map: Dict[int, dict] = {
        1: {"name": "민수", "grade": 3},
        2: {"name": "지우", "grade": 2},
        3: {"name": "서연", "grade": 3},
    }

    print("  학생 맵 (map<int32, Student>):")
    for student_id, info in student_map.items():
        print(f"    ID {student_id} → {info['name']} ({info['grade']}학년)")
    print()

    print("  map 필드 제약:")
    print("    - 키: int32, int64, string 등 (float, bytes, message 불가!)")
    print("    - 값: 모든 타입 가능 (message 포함)")
    print("    - 순서가 보장되지 않음!")
    print("    - repeated와 함께 쓸 수 없음 (repeated map 불가)")
    print()


def lesson5_oneof():
    # =========================================================================
    #   레슨 5 — Oneof (택 1)
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 5 : Oneof (택 1)                      │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ oneof = 여러 필드 중 하나만 값이 있을 수 있음
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     점심 메뉴: "밥 OR 빵 OR 면" 중 하나만 선택!
    #     밥을 선택하면 빵과 면은 자동으로 비워짐!
    #
    #   proto:
    #     oneof content {
    #       string text_message = 2;
    #       bytes image_data = 3;
    #       ScoreAlert score_alert = 4;
    #     }
    #

    @dataclass
    class Notification:
        title: str
        # oneof content: 이 중 하나만 값이 있음
        text_message: Optional[str] = None
        image_data: Optional[bytes] = None
        score_alert: Optional[dict] = None

        @property
        def content_type(self):
            if self.text_message is not None:
                return "text_message"
            if self.image_data is not None:
                return "image_data"
            if self.score_alert is not None:
                return "score_alert"
            return "none"

    # 텍스트 알림
    notif1 = Notification(title="공지", text_message="내일 체육대회입니다!")
    print(f"  알림 1: [{notif1.content_type}]")
    print(f"    제목: {notif1.title}")
    print(f"    내용: {notif1.text_message}")
    print()

    # 점수 알림
    notif2 = Notification(
        title="성적 변경",
        score_alert={"student": "민수", "subject": "수학",
                     "old": 88, "new": 95},
    )
    print(f"  알림 2: [{notif2.content_type}]")
    print(f"    제목: {notif2.title}")
    print(f"    내용: {notif2.score_alert}")
    print()

    print("  oneof 규칙:")
    print("    - 한 번에 하나만 값이 있을 수 있음")
    print("    - 새 값을 설정하면 이전 값은 자동 삭제")
    print("    - 어떤 필드에 값이 있는지 확인하는 which_oneof() 사용")
    print("    - repeated 필드는 oneof 안에 넣을 수 없음")
    print()


def lesson6_well_known_types():
    # =========================================================================
    #   레슨 6 — Well-Known Types
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 6 : Well-Known Types                  │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Well-Known Types = 구글이 미리 만들어 둔 공통 타입
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     학교에서 쓰는 공통 서식 (출석부, 성적표 양식)처럼
    #     구글이 미리 만들어 둔 "자주 쓰는 데이터 양식"입니다.
    #

    # Timestamp (날짜/시간)
    print("  [Timestamp] 특정 시각을 표현")
    now = datetime.now()
    timestamp = {
        "seconds": int(now.timestamp()),
        "nanos": now.microsecond * 1000,
    }
    print(f"    현재 시각: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"    Timestamp: seconds={timestamp['seconds']}, nanos={timestamp['nanos']}")
    print()

    # Duration (시간 간격)
    print("  [Duration] 시간 간격을 표현")
    exam_duration = timedelta(hours=1, minutes=30)
    duration = {
        "seconds": int(exam_duration.total_seconds()),
        "nanos": 0,
    }
    print(f"    시험 시간: {exam_duration}")
    print(f"    Duration: seconds={duration['seconds']}")
    print()

    # Wrappers (nullable 값)
    print("  [Wrappers] null 가능한 기본 타입")
    print("    proto3에서 string의 기본값은 '' (빈 문자열)")
    print("    그래서 '값이 없음'과 '빈 문자열'을 구분할 수 없습니다!")
    print()
    print("    StringValue 사용 전:")
    print("      memo = ''    → 빈 메모인지? 메모를 안 쓴 건지?")
    print()
    print("    StringValue 사용 후:")
    print("      memo = null          → 메모를 안 쓴 것")
    print("      memo = {value: ''}   → 빈 메모를 쓴 것")
    print()

    # Any (아무 타입)
    print("  [Any] 어떤 메시지든 담을 수 있는 만능 상자")
    any_value = {
        "type_url": "type.googleapis.com/lesson.advanced.ScoreAlert",
        "value": {"student": "민수", "subject": "수학"},
    }
    print(f"    type_url로 어떤 타입인지 표시: {any_value['type_url']}")
    print(f"    value에 실제 데이터: {any_value['value']}")
    print("    → 받는 쪽에서 type_url을 보고 올바른 타입으로 해석합니다.")
    print()


def lesson7_proto3_vs_proto2():
    # =========================================================================
    #   레슨 7 — proto3 vs proto2
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 7 : proto3 vs proto2                   │")
    print("└──────────────────────────────────────────────┘")
    print()

    comparisons = [
        ("기본 키워드",    "required/optional 명시",     "모든 필드가 optional"),
        ("기본값",         "직접 지정 가능",             "타입별 자동 (0, '', false)"),
        ("enum 0번",      "선택사항",                    "필수 (UNSPECIFIED 권장)"),
        ("unknown 필드",  "무시 또는 에러",              "보존됨 (forward compat)"),
        ("map 지원",      "없음 (직접 구현)",            "기본 지원"),
        ("JSON 매핑",     "비공식",                      "공식 지원"),
        ("사용 권장",      "레거시 프로젝트",             "새 프로젝트"),
    ]

    print(f"  {'항목':<16s} {'proto2':<24s} {'proto3':<24s}")
    print(f"  {'─' * 16} {'─' * 24} {'─' * 24}")
    for item, p2, p3 in comparisons:
        print(f"  {item:<16s} {p2:<24s} {p3:<24s}")
    print()

    print("  결론: 새 프로젝트는 proto3를 사용하세요!")
    print("  proto2는 오래된 프로젝트에서만 볼 수 있습니다.")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("  gRPC 07단계 : Protocol Buffers 심화")
    print("=" * 72)
    print()

    lesson1_enum()
    lesson2_repeated()
    lesson3_nested_message()
    lesson4_map_field()
    lesson5_oneof()
    lesson6_well_known_types()
    lesson7_proto3_vs_proto2()
