# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   파이썬 학습 10단계: 모던 파이썬
#   ─ 타입 힌트, dataclass, match-case, walrus, f-string 고급, Enum, typing ─
#   ■ 실행 방법: python 10_modern_python.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 타입 힌트 완전정복
#   2. dataclass 완전정복
#   3. match-case (패턴 매칭)
#   4. Walrus 연산자 (:=)
#   5. f-string 고급
#   6. 딕셔너리 병합 (|, |=), 구조적 서브패턴
#   7. Enum 완전정복
#   8. typing 고급 — Protocol, TypedDict, Literal, Final, Annotated
#   9. 실전: 모던 파이썬으로 학생관리 시스템 리팩토링
#
# ─────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto, Flag
from typing import (
    Optional, Union, Callable, TypeVar, Protocol,
    TypedDict, Literal, Final, Annotated, runtime_checkable,
)


# =========================================================================
#
#   레슨 1 — 타입 힌트 완전정복
#
# =========================================================================

def lesson1_type_hints():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 타입 힌트 완전정복          │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 타입 힌트란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   파이썬은 동적 타입 언어라서 변수에 아무 값이나 넣을 수 있습니다.
    #   타입 힌트는 "이 변수에는 이런 타입이 들어올 거야"라고 표시하는 안내판입니다.
    #
    #   비유: 주차장의 "장애인 전용", "소형차 전용" 표지판
    #         → 표지판을 무시해도 주차는 되지만, 지키면 질서가 잡힘!
    #
    #   타입 힌트는 실행에 영향을 주지 않습니다 (힌트일 뿐!).
    #   하지만 mypy, pyright 같은 도구로 미리 버그를 잡을 수 있습니다.
    #

    # ─────────────────────────────────────────────────────────────────────
    # ■ 기본 타입 힌트
    # ─────────────────────────────────────────────────────────────────────

    name: str = "홍길동"              # 문자열
    age: int = 25                     # 정수
    height: float = 175.5             # 실수
    is_student: bool = True           # 불리언

    print(f"  이름: {name} (타입: {type(name).__name__})")
    print(f"  나이: {age} (타입: {type(age).__name__})")
    print(f"  키: {height} (타입: {type(height).__name__})")
    print(f"  학생 여부: {is_student} (타입: {type(is_student).__name__})")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 컬렉션 타입 힌트 — list, dict, tuple, set
    # ─────────────────────────────────────────────────────────────────────
    #
    #   파이썬 3.9+ 부터는 list[int] 형태로 바로 쓸 수 있습니다.
    #   그 이전에는 from typing import List, Dict 를 써야 했습니다.
    #

    scores: list[int] = [90, 85, 78]
    student_ages: dict[str, int] = {"민수": 15, "지유": 16}
    coordinate: tuple[float, float] = (37.5, 127.0)
    unique_tags: set[str] = {"python", "modern", "typing"}

    print(f"  점수 목록: {scores}")
    print(f"  학생 나이: {student_ages}")
    print(f"  좌표: {coordinate}")
    print(f"  태그: {unique_tags}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Optional과 Union
    # ─────────────────────────────────────────────────────────────────────
    #
    #   Optional[str] = str | None  (값이 있을 수도, 없을 수도 있음)
    #   Union[int, str] = int | str  (둘 중 하나)
    #
    #   파이썬 3.10+ 부터는 | 연산자로 간단히 쓸 수 있습니다.
    #

    def find_student(name: str) -> Optional[dict]:
        """학생을 찾아 반환. 없으면 None."""
        students = {"민수": {"grade": 3}, "지유": {"grade": 4}}
        return students.get(name)

    def process_id(id_value: Union[int, str]) -> str:
        """ID를 문자열로 변환."""
        return str(id_value)

    result = find_student("민수")
    print(f"  민수 검색: {result}")
    print(f"  없는학생 검색: {find_student('없는학생')}")
    print(f"  ID 처리: {process_id(42)}, {process_id('ABC')}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Callable — 함수를 인자로 받을 때
    # ─────────────────────────────────────────────────────────────────────
    #
    #   Callable[[인자타입들], 반환타입]
    #
    #   비유: "이 슬롯에는 동전 넣기 기계만 꽂을 수 있어요"처럼
    #         어떤 모양의 함수가 들어와야 하는지 명시하는 것
    #

    def apply_operation(x: int, y: int, op: Callable[[int, int], int]) -> int:
        return op(x, y)

    add: Callable[[int, int], int] = lambda a, b: a + b
    multiply: Callable[[int, int], int] = lambda a, b: a * b

    print(f"  apply_operation(3, 4, add) = {apply_operation(3, 4, add)}")
    print(f"  apply_operation(3, 4, multiply) = {apply_operation(3, 4, multiply)}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ TypeVar — 제네릭 타입
    # ─────────────────────────────────────────────────────────────────────
    #
    #   TypeVar는 "어떤 타입이든 같은 타입"을 나타냅니다.
    #   C++의 template<typename T>와 비슷합니다.
    #

    T = TypeVar("T")

    def first_element(items: list[T]) -> T:
        """리스트의 첫 번째 요소를 반환합니다."""
        return items[0]

    print(f"  first_element([10, 20, 30]) = {first_element([10, 20, 30])}")
    print(f"  first_element(['a', 'b']) = {first_element(['a', 'b'])}")
    print()


# =========================================================================
#
#   레슨 2 — dataclass 완전정복
#
# =========================================================================

def lesson2_dataclass():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : dataclass 완전정복          │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ dataclass란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   @dataclass는 데이터를 담는 클래스를 자동으로 만들어주는 마법 도장입니다.
    #
    #   비유: 학교에서 학생 카드 양식을 미리 인쇄해 놓는 것
    #         양식에 이름, 학년, 반 칸이 있으면 → 이름만 채우면 카드 완성!
    #
    #   자동으로 만들어주는 것:
    #   - __init__() : 생성자 (값 넣기)
    #   - __repr__() : 출력 형태
    #   - __eq__()   : 동등 비교 (==)
    #

    # ─── 기본 사용법 ───

    @dataclass
    class Student:
        name: str
        grade: int
        score: float = 0.0  # 기본값이 있는 필드는 뒤에!

    s1 = Student("민수", 3, 95.5)
    s2 = Student("지유", 4)       # score는 기본값 0.0

    print(f"  s1 = {s1}")
    print(f"  s2 = {s2}")
    print(f"  s1 == s2: {s1 == s2}")
    print(f"  s1 == Student('민수', 3, 95.5): {s1 == Student('민수', 3, 95.5)}")
    print()

    # ─── field()와 default_factory ───
    #
    # ★ 주의: 가변 기본값 (list, dict 등)은 반드시 field(default_factory=...)를 써야!
    #   그렇지 않으면 모든 인스턴스가 같은 리스트를 공유하는 무서운 버그 발생!
    #

    @dataclass
    class Classroom:
        room_number: int
        students: list[str] = field(default_factory=list)
        metadata: dict[str, str] = field(default_factory=dict)

    c1 = Classroom(101)
    c1.students.append("민수")
    c2 = Classroom(102)

    print(f"  c1.students = {c1.students}")
    print(f"  c2.students = {c2.students}  ← c1과 독립적!")
    print()

    # ─── __post_init__으로 생성 후 추가 처리 ───

    @dataclass
    class Product:
        name: str
        price: int
        quantity: int
        total: int = field(init=False)  # init=False: 생성자에서 받지 않음

        def __post_init__(self):
            """생성 직후 자동으로 호출됩니다."""
            self.total = self.price * self.quantity
            if self.price < 0:
                raise ValueError(f"가격은 음수가 될 수 없습니다: {self.price}")

    p = Product("연필", 500, 10)
    print(f"  Product('연필', 500, 10).total = {p.total}")
    print()

    # ─── frozen=True : 변경 불가 (불변) 객체 ───

    @dataclass(frozen=True)
    class Coordinate:
        x: float
        y: float

    point = Coordinate(37.5, 127.0)
    print(f"  불변 좌표: {point}")
    try:
        point.x = 0  # type: ignore
    except Exception as e:
        print(f"  변경 시도 → 에러: {e}")
    print()

    # ─── order=True : 비교/정렬 가능 ───

    @dataclass(order=True)
    class RankedStudent:
        score: float       # 첫 번째 필드 기준으로 비교
        name: str

    students = [
        RankedStudent(85.0, "민수"),
        RankedStudent(92.0, "지유"),
        RankedStudent(78.0, "서연"),
    ]
    students.sort()
    print("  정렬된 학생:")
    for s in students:
        print(f"    {s.name}: {s.score}점")
    print()


# =========================================================================
#
#   레슨 3 — match-case (패턴 매칭)
#
# =========================================================================

def lesson3_match_case():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : match-case (패턴 매칭)      │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ match-case란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   파이썬 3.10에 추가된 구조적 패턴 매칭입니다.
    #   C/C++의 switch-case보다 훨씬 강력합니다!
    #
    #   비유: 택배 분류 시스템
    #     → 상자의 라벨, 크기, 내용물을 보고 자동으로 분류하는 컨베이어 벨트
    #     → match가 상자를 올려놓고, case가 각 분류 조건
    #

    # ─── 값 패턴 (가장 기본) ───

    def get_day_type(day: str) -> str:
        match day:
            case "월" | "화" | "수" | "목" | "금":   # OR 패턴
                return "평일"
            case "토" | "일":
                return "주말"
            case _:                                   # 와일드카드 (default)
                return "알 수 없는 요일"

    for d in ["월", "토", "공휴일"]:
        print(f"  {d} → {get_day_type(d)}")
    print()

    # ─── 구조 패턴 (딕셔너리/리스트 분해) ───

    def process_event(event: dict) -> str:
        match event:
            case {"type": "login", "user": user}:
                return f"{user}님이 로그인했습니다"
            case {"type": "purchase", "user": user, "item": item}:
                return f"{user}님이 {item}을 구매했습니다"
            case {"type": "logout", "user": user}:
                return f"{user}님이 로그아웃했습니다"
            case _:
                return "알 수 없는 이벤트"

    events = [
        {"type": "login", "user": "민수"},
        {"type": "purchase", "user": "지유", "item": "노트북"},
        {"type": "logout", "user": "서연"},
        {"type": "unknown"},
    ]
    for ev in events:
        print(f"  {ev} → {process_event(ev)}")
    print()

    # ─── 가드 (if 조건 추가) ───

    def classify_score(score: int) -> str:
        match score:
            case s if s >= 90:
                return "A등급"
            case s if s >= 80:
                return "B등급"
            case s if s >= 70:
                return "C등급"
            case _:
                return "D등급"

    for sc in [95, 83, 72, 55]:
        print(f"  {sc}점 → {classify_score(sc)}")
    print()

    # ─── 캡처 패턴 (시퀀스 분해) ───

    def describe_list(items: list) -> str:
        match items:
            case []:
                return "빈 리스트"
            case [only]:
                return f"원소 1개: {only}"
            case [first, second]:
                return f"원소 2개: {first}, {second}"
            case [first, *rest]:
                return f"첫 번째: {first}, 나머지 {len(rest)}개"

    test_lists = [[], [42], [1, 2], [1, 2, 3, 4, 5]]
    for lst in test_lists:
        print(f"  {lst} → {describe_list(lst)}")
    print()


# =========================================================================
#
#   레슨 4 — Walrus 연산자 (:=)
#
# =========================================================================

def lesson4_walrus_operator():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : Walrus 연산자 (:=)          │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Walrus 연산자란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   := (바다코끼리 연산자)는 "대입과 동시에 사용"하는 연산자입니다.
    #   파이썬 3.8에 추가되었습니다.
    #
    #   이름 유래: := 를 90도 돌리면 바다코끼리(walrus) 얼굴처럼 보여서!
    #
    #   비유: 카페에서 "아메리카노 한 잔 주세요, 그리고 그걸로 마실게요"
    #         → 주문(대입)과 사용을 한 문장에!
    #
    #   ★ 없었을 때의 불편함:
    #     result = expensive_function()
    #     if result > 10:
    #         print(result)
    #
    #   ★ walrus로 개선:
    #     if (result := expensive_function()) > 10:
    #         print(result)
    #

    # ─── if 문에서 활용 ───

    data = ["hello", "", "world", "", "python"]

    print("  비어있지 않은 문자열:")
    for item in data:
        if (n := len(item)) > 0:
            print(f"    '{item}' (길이: {n})")
    print()

    # ─── while 문에서 활용 (가장 유용한 패턴!) ───
    #
    #   파일 읽기, 사용자 입력 등에서 매우 유용합니다.
    #   시뮬레이션으로 보여드리겠습니다.
    #

    import io
    fake_file = io.StringIO("첫 줄\n둘째 줄\n셋째 줄\n")

    print("  while + walrus로 파일 읽기:")
    while (line := fake_file.readline()):
        print(f"    읽은 줄: {line.strip()}")
    print()

    # ─── 리스트 컴프리헨션에서 활용 ───
    #
    #   계산 결과를 재활용할 때 유용합니다.
    #   계산을 두 번 하지 않아도 됩니다!
    #

    numbers = [4, 8, 15, 16, 23, 42]
    # 제곱이 100 이상인 것만, 제곱값과 함께 저장
    results = [(x, y) for x in numbers if (y := x ** 2) >= 100]
    print(f"  제곱이 100 이상: {results}")
    print()

    # ─── 주의사항 ───
    #
    #   ★ 남용하지 마세요!
    #   가독성이 떨어지면 그냥 두 줄로 쓰는 게 낫습니다.
    #
    #   나쁜 예: result = [(y := f(x), x / y) for x in data if y > 0]
    #   → 읽기 어려움! 두 줄로 나누세요.
    #

    print("  ★ Walrus 사용 규칙:")
    print("    1. if/while에서 대입+검사를 합칠 때 유용")
    print("    2. 컴프리헨션에서 중복 계산을 없앨 때 유용")
    print("    3. 한 줄이 복잡해지면 그냥 두 줄로 나누세요!")
    print()


# =========================================================================
#
#   레슨 5 — f-string 고급
#
# =========================================================================

def lesson5_fstring_advanced():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : f-string 고급               │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 포맷 스펙 — 정렬, 채우기, 소수점
    # ─────────────────────────────────────────────────────────────────────
    #
    #   {값:포맷스펙} 형태로 출력 형식을 지정합니다.
    #
    #   주요 포맷:
    #   {:>10}  → 오른쪽 정렬, 10칸
    #   {:<10}  → 왼쪽 정렬, 10칸
    #   {:^10}  → 가운데 정렬, 10칸
    #   {:0>5}  → 0으로 채우기, 5칸
    #   {:.2f}  → 소수점 2자리
    #   {:,}    → 천 단위 쉼표
    #

    name = "민수"
    score = 95.678
    price = 1234567

    print("  ─── 정렬 ───")
    print(f"  오른쪽 정렬: [{name:>10}]")
    print(f"  왼쪽 정렬 : [{name:<10}]")
    print(f"  가운데 정렬: [{name:^10}]")
    print(f"  별표 채우기: [{name:*^10}]")
    print()

    print("  ─── 숫자 포맷 ───")
    print(f"  소수점 2자리: {score:.2f}")
    print(f"  소수점 없이 : {score:.0f}")
    print(f"  천 단위 쉼표: {price:,}원")
    print(f"  0 채우기    : {42:05d}")
    print(f"  퍼센트      : {0.8567:.1%}")
    print()

    # ─── 디버깅 모드 (= 기호, 파이썬 3.8+) ───
    #
    #   f"{변수=}" 을 쓰면 변수 이름과 값이 함께 출력됩니다.
    #   디버깅할 때 매우 편리합니다!
    #

    x = 42
    y = "hello"
    items = [1, 2, 3]

    print("  ─── 디버깅 모드 (=) ───")
    print(f"  {x=}")
    print(f"  {y=}")
    print(f"  {len(items)=}")
    print(f"  {x * 2 + 1=}")
    print()

    # ─── 날짜 포맷 ───

    from datetime import datetime
    now = datetime(2025, 7, 15, 14, 30, 0)

    print("  ─── 날짜 포맷 ───")
    print(f"  기본       : {now}")
    print(f"  한국식 날짜: {now:%Y년 %m월 %d일}")
    print(f"  시간       : {now:%H시 %M분}")
    print(f"  요일       : {now:%A}")
    print()

    # ─── 표 만들기 실전 ───

    print("  ─── 성적표 (표 만들기) ───")
    students = [
        ("민수", 95, 88, 92),
        ("지유", 100, 95, 97),
        ("서연", 78, 82, 90),
    ]

    print(f"  {'이름':^6} {'국어':>5} {'수학':>5} {'영어':>5} {'평균':>7}")
    print(f"  {'─' * 6} {'─' * 5} {'─' * 5} {'─' * 5} {'─' * 7}")
    for name, kor, math_s, eng in students:
        avg = (kor + math_s + eng) / 3
        print(f"  {name:^6} {kor:>5} {math_s:>5} {eng:>5} {avg:>7.1f}")
    print()


# =========================================================================
#
#   레슨 6 — 딕셔너리 병합과 구조적 서브패턴
#
# =========================================================================

def lesson6_dict_merge():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 딕셔너리 병합 & 서브패턴    │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 딕셔너리 병합 연산자 (|, |=) — 파이썬 3.9+
    # ─────────────────────────────────────────────────────────────────────
    #
    #   | (파이프)는 두 딕셔너리를 합쳐서 새 딕셔너리를 만듭니다.
    #   |= 는 왼쪽 딕셔너리에 오른쪽을 합쳐 넣습니다 (in-place).
    #
    #   비유: 서류철 두 개를 합치기
    #     | → 새 서류철에 복사해서 합침
    #     |= → 왼쪽 서류철에 오른쪽 내용을 끼워 넣음
    #
    #   ★ 이전 방식과 비교:
    #   - 옛날: {**dict1, **dict2}
    #   - 모던: dict1 | dict2
    #

    defaults = {"theme": "light", "language": "ko", "font_size": 14}
    user_prefs = {"theme": "dark", "font_size": 16}

    # | 연산자: 새 딕셔너리 생성 (겹치면 오른쪽이 이김)
    merged = defaults | user_prefs
    print(f"  기본 설정: {defaults}")
    print(f"  사용자 설정: {user_prefs}")
    print(f"  병합 결과: {merged}")
    print()

    # |= 연산자: 기존 딕셔너리에 합치기
    config = {"debug": False, "log_level": "INFO"}
    config |= {"debug": True, "verbose": True}
    print(f"  |= 결과: {config}")
    print()

    # ─── 실전: 설정 계층 병합 ───

    system_config = {"max_users": 100, "timeout": 30}
    env_config = {"timeout": 60, "debug": True}
    cli_config = {"debug": False}

    # 우선순위: CLI > 환경변수 > 시스템 (오른쪽이 이김)
    final = system_config | env_config | cli_config
    print(f"  계층 병합 (system | env | cli): {final}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 구조적 서브패턴 — match-case의 중첩 패턴
    # ─────────────────────────────────────────────────────────────────────

    def process_order(order: dict) -> str:
        match order:
            case {"status": "delivered", "rating": int(r)} if r >= 4:
                return f"우수 배송 (별점 {r})"
            case {"status": "delivered", "rating": int(r)}:
                return f"배송 완료 (별점 {r})"
            case {"status": "shipped", "tracking": str(code)}:
                return f"배송중 (송장 {code})"
            case {"status": "pending"}:
                return "주문 접수됨"
            case _:
                return "알 수 없는 상태"

    orders = [
        {"status": "delivered", "rating": 5},
        {"status": "delivered", "rating": 2},
        {"status": "shipped", "tracking": "KR12345"},
        {"status": "pending"},
        {"status": "cancelled"},
    ]

    for order in orders:
        print(f"  {order} → {process_order(order)}")
    print()


# =========================================================================
#
#   레슨 7 — Enum 완전정복
#
# =========================================================================

def lesson7_enum():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : Enum 완전정복               │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Enum이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   Enum(열거형)은 관련된 상수들을 하나의 그룹으로 묶는 것입니다.
    #
    #   비유: 신호등의 빨강/노랑/초록
    #     → 신호등 상태는 이 3개 중 하나만 가능!
    #     → 문자열 "빨강"으로 쓰면 오타 위험 ("빨강" vs "발강")
    #     → Enum으로 만들면 오타가 즉시 에러로 잡힘!
    #

    # ─── 기본 Enum ───

    class Color(Enum):
        RED = "빨강"
        GREEN = "초록"
        BLUE = "파랑"

    print(f"  Color.RED = {Color.RED}")
    print(f"  Color.RED.name = {Color.RED.name}")
    print(f"  Color.RED.value = {Color.RED.value}")
    print(f"  Color('빨강') = {Color('빨강')}")  # 값으로 접근
    print()

    # ─── IntEnum (정수 비교 가능) ───

    class Priority(IntEnum):
        LOW = 1
        MEDIUM = 2
        HIGH = 3
        CRITICAL = 4

    task_priority = Priority.HIGH
    print(f"  task_priority = {task_priority}")
    print(f"  HIGH > MEDIUM: {Priority.HIGH > Priority.MEDIUM}")
    print(f"  HIGH == 3: {Priority.HIGH == 3}")  # IntEnum은 정수와 비교 가능!
    print()

    # ─── auto()로 자동 번호 매기기 ───

    class Direction(Enum):
        NORTH = auto()
        SOUTH = auto()
        EAST = auto()
        WEST = auto()

    print("  auto() 결과:")
    for d in Direction:
        print(f"    {d.name} = {d.value}")
    print()

    # ─── Flag : 비트 조합 (여러 개 선택 가능) ───

    class Permission(Flag):
        READ = auto()
        WRITE = auto()
        EXECUTE = auto()

    # 권한 조합
    admin = Permission.READ | Permission.WRITE | Permission.EXECUTE
    viewer = Permission.READ

    print(f"  admin 권한: {admin}")
    print(f"  viewer 권한: {viewer}")
    print(f"  admin에 WRITE 있나: {Permission.WRITE in admin}")
    print(f"  viewer에 WRITE 있나: {Permission.WRITE in viewer}")
    print()

    # ─── 실전: 상태 관리 ───

    class OrderStatus(Enum):
        PENDING = "pending"
        CONFIRMED = "confirmed"
        SHIPPED = "shipped"
        DELIVERED = "delivered"
        CANCELLED = "cancelled"

        def next_status(self) -> "OrderStatus":
            transitions = {
                OrderStatus.PENDING: OrderStatus.CONFIRMED,
                OrderStatus.CONFIRMED: OrderStatus.SHIPPED,
                OrderStatus.SHIPPED: OrderStatus.DELIVERED,
            }
            if self in transitions:
                return transitions[self]
            raise ValueError(f"{self.value}에서는 다음 단계로 진행할 수 없습니다")

    status = OrderStatus.PENDING
    print(f"  현재 상태: {status.value}")
    status = status.next_status()
    print(f"  다음 상태: {status.value}")
    status = status.next_status()
    print(f"  다음 상태: {status.value}")
    print()


# =========================================================================
#
#   레슨 8 — typing 고급
#
# =========================================================================

def lesson8_typing_advanced():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 8 : typing 고급                 │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Protocol — 덕 타이핑의 공식화
    # ─────────────────────────────────────────────────────────────────────
    #
    #   "오리처럼 걷고 오리처럼 꽥꽥대면, 그건 오리다"
    #   → 특정 메서드만 있으면 같은 타입으로 취급!
    #
    #   Protocol은 이 덕 타이핑을 타입 힌트로 명시합니다.
    #   Java의 interface와 비슷하지만 상속이 필요 없습니다!
    #

    @runtime_checkable
    class Drawable(Protocol):
        def draw(self) -> str: ...

    class Circle:
        def draw(self) -> str:
            return "●"

    class Square:
        def draw(self) -> str:
            return "■"

    class Text:
        def draw(self) -> str:
            return "Hello"

    def render(shape: Drawable) -> None:
        print(f"    렌더링: {shape.draw()}")

    print("  Protocol 예시:")
    render(Circle())
    render(Square())
    render(Text())
    print(f"  Circle은 Drawable? {isinstance(Circle(), Drawable)}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ TypedDict — 딕셔너리에 구조를 부여
    # ─────────────────────────────────────────────────────────────────────
    #
    #   일반 dict는 어떤 키가 있는지 알 수 없습니다.
    #   TypedDict로 "이 딕셔너리에는 이런 키들이 있어야 해"를 명시합니다.
    #

    class StudentInfo(TypedDict):
        name: str
        grade: int
        score: float

    student: StudentInfo = {"name": "민수", "grade": 3, "score": 95.5}
    print(f"  TypedDict: {student}")
    print(f"  학생 이름: {student['name']}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Literal — 허용되는 값을 제한
    # ─────────────────────────────────────────────────────────────────────

    def set_alignment(align: Literal["left", "center", "right"]) -> str:
        return f"정렬: {align}"

    print(f"  {set_alignment('left')}")
    print(f"  {set_alignment('center')}")
    # set_alignment("top")  # ← mypy가 에러를 잡아줌!
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Final — 재대입 금지
    # ─────────────────────────────────────────────────────────────────────

    MAX_RETRIES: Final = 3
    PI: Final[float] = 3.14159

    print(f"  MAX_RETRIES = {MAX_RETRIES}")
    print(f"  PI = {PI}")
    # MAX_RETRIES = 5  # ← mypy가 에러를 잡아줌!
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Annotated — 타입에 메타데이터 추가
    # ─────────────────────────────────────────────────────────────────────
    #
    #   Annotated[타입, 메타데이터] 형태로 추가 정보를 붙입니다.
    #   pydantic, FastAPI 등에서 검증 규칙을 붙일 때 활용됩니다.
    #

    Age = Annotated[int, "0~150 사이의 정수"]
    Score = Annotated[float, "0.0~100.0 사이의 실수"]

    def create_student(name: str, age: Age, score: Score) -> dict:
        return {"name": name, "age": age, "score": score}

    result = create_student("민수", 15, 95.5)
    print(f"  Annotated 활용: {result}")
    print()


# =========================================================================
#
#   레슨 9 — 실전: 모던 파이썬으로 학생관리 시스템 리팩토링
#
# =========================================================================

def lesson9_student_management_system():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 9 : 학생관리 시스템 리팩토링     │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 목표: 앞에서 배운 모던 파이썬 기능을 총동원하여
    #   학생 관리 시스템을 "현대적"으로 작성합니다.
    # ─────────────────────────────────────────────────────────────────────

    # ─── Enum으로 학년 상태 정의 ───

    class Grade(IntEnum):
        FIRST = 1
        SECOND = 2
        THIRD = 3
        FOURTH = 4
        FIFTH = 5
        SIXTH = 6

    # ─── dataclass로 학생 모델 정의 ───

    @dataclass(order=True)
    class Student:
        score: float                # 정렬 기준 (order=True이므로)
        name: str
        grade: Grade
        subjects: dict[str, int] = field(default_factory=dict)

        def __post_init__(self):
            if self.subjects:
                self.score = sum(self.subjects.values()) / len(self.subjects)

        @property
        def level(self) -> str:
            """학생의 성적 수준을 반환합니다."""
            match self.score:
                case s if s >= 90:
                    return "우수"
                case s if s >= 80:
                    return "양호"
                case s if s >= 70:
                    return "보통"
                case _:
                    return "노력필요"

    # ─── 학생 데이터 생성 ───

    students = [
        Student(0, "민수", Grade.THIRD, {"국어": 95, "수학": 88, "영어": 92}),
        Student(0, "지유", Grade.FOURTH, {"국어": 100, "수학": 95, "영어": 97}),
        Student(0, "서연", Grade.THIRD, {"국어": 78, "수학": 65, "영어": 80}),
        Student(0, "하준", Grade.FIFTH, {"국어": 85, "수학": 90, "영어": 88}),
        Student(0, "도윤", Grade.FOURTH, {"국어": 60, "수학": 55, "영어": 70}),
    ]

    # ─── 전체 학생 현황 출력 (f-string 고급 활용) ───

    print("  ╔══════════════════════════════════════════════════╗")
    print("  ║          학생 관리 시스템 v2.0 (모던 파이썬)       ║")
    print("  ╚══════════════════════════════════════════════════╝")
    print()
    print(f"  {'이름':^6} {'학년':>4} {'평균':>7} {'수준':^8}")
    print(f"  {'─' * 6} {'─' * 4} {'─' * 7} {'─' * 8}")
    for s in sorted(students, reverse=True):  # 성적 순 정렬
        print(f"  {s.name:^6} {s.grade.value:>4} {s.score:>7.1f} {s.level:^8}")
    print()

    # ─── match-case로 명령 처리 시뮬레이션 ───

    commands = [
        {"action": "search", "name": "민수"},
        {"action": "filter", "min_score": 80},
        {"action": "stats"},
        {"action": "unknown"},
    ]

    print("  ─── 명령 처리 ───")
    for cmd in commands:
        match cmd:
            case {"action": "search", "name": str(name)}:
                found = [s for s in students if s.name == name]
                if found:
                    s = found[0]
                    print(f"  검색 결과: {s.name} ({s.grade.value}학년, {s.score:.1f}점)")
                else:
                    print(f"  '{name}' 학생을 찾을 수 없습니다")

            case {"action": "filter", "min_score": int(min_s)}:
                filtered = [s for s in students if s.score >= min_s]
                names = ", ".join(s.name for s in filtered)
                print(f"  {min_s}점 이상: {names} ({len(filtered)}명)")

            case {"action": "stats"}:
                avg = sum(s.score for s in students) / len(students)
                top = max(students)
                print(f"  전체 평균: {avg:.1f}, 최고 성적: {top.name} ({top.score:.1f}점)")

            case _:
                print(f"  알 수 없는 명령: {cmd}")
    print()

    # ─── Walrus 연산자로 요약 통계 ───

    if (n := len(students)) > 0:
        total = sum(s.score for s in students)
        print(f"  총 {n}명, 전체 평균: {total / n:.1f}점")

    # 우수 학생이 있으면 출력
    if (excellent := [s for s in students if s.level == "우수"]):
        print(f"  우수 학생: {', '.join(s.name for s in excellent)}")

    print()
    print("  ★ 이 시스템에서 사용된 모던 파이썬 기능:")
    print("    - dataclass (order=True, field, __post_init__)")
    print("    - IntEnum (Grade)")
    print("    - match-case (명령 처리)")
    print("    - f-string 포맷 스펙 (표 만들기)")
    print("    - walrus 연산자 (조건부 출력)")
    print("    - 타입 힌트 (전체)")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인 실행
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
    print("  파이썬 학습 10단계: 모던 파이썬")
    print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
    print()

    lesson1_type_hints()
    lesson2_dataclass()
    lesson3_match_case()
    lesson4_walrus_operator()
    lesson5_fstring_advanced()
    lesson6_dict_merge()
    lesson7_enum()
    lesson8_typing_advanced()
    lesson9_student_management_system()

    print("=" * 60)
    print("  10단계 완료! 모던 파이썬의 핵심 기능을 모두 배웠습니다.")
    print("=" * 60)


if __name__ == "__main__":
    main()
