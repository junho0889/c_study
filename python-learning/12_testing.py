# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   파이썬 학습 12단계: 테스트
#   ─ 자동 테스트, unittest, pytest, 모킹, TDD, 커버리지, 통합 테스트 ─
#   ■ 실행 방법: python 12_testing.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 왜 테스트를 하는가? — 수동 vs 자동, 테스트 피라미드
#   2. unittest 기초 — TestCase, setUp/tearDown, 실행 방법
#   3. assert 메서드 총정리
#   4. pytest 기초 — assert문, 픽스처, 파라미터화
#   5. 모킹 (Mock) — unittest.mock, patch, MagicMock
#   6. TDD 실습 — Red → Green → Refactor
#   7. 테스트 커버리지 — 무엇을 테스트할지, 경계값, 엣지케이스
#   8. 통합 테스트 vs 단위 테스트
#   9. 실전: 쇼핑몰 할인 시스템 TDD로 구현
#
# ─────────────────────────────────────────────────────────────────────────

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, date


# =========================================================================
#
#   레슨 1 — 왜 테스트를 하는가?
#
# =========================================================================

def lesson1_why_testing():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 왜 테스트를 하는가?          │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 테스트가 없으면 생기는 일
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유: 다리를 지었는데 차가 지나가도 되는지 확인 안 한 것!
    #
    #   - 코드를 수정할 때마다 "이거 고치면 다른 데 안 망가지겠지?" 불안
    #   - 새 기능 추가할 때마다 전체를 일일이 손으로 확인
    #   - 실수를 눈으로 확인해야 하므로 놓치기 쉬움
    #   - "어제까지 잘 됐는데?!" → 회귀 버그
    #

    print("  ■ 수동 테스트 vs 자동 테스트:")
    print()

    # ─── 수동 테스트 (지금까지 해온 방식) ───

    def add(a, b):
        return a + b

    print("  [수동 테스트]")
    print(f"    add(2, 3) = {add(2, 3)}  ← 눈으로 확인: 5 맞나?")
    print(f"    add(-1, 1) = {add(-1, 1)}  ← 눈으로 확인: 0 맞나?")
    print("    → 매번 눈으로 봐야 함. 100개면? 1000개면?")
    print()

    # ─── 자동 테스트 (컴퓨터가 확인!) ───

    print("  [자동 테스트]")
    tests_passed = 0
    tests_total = 0

    def auto_test(description, actual, expected):
        nonlocal tests_passed, tests_total
        tests_total += 1
        if actual == expected:
            tests_passed += 1
            print(f"    ✓ {description}")
        else:
            print(f"    ✗ {description}: 기대={expected}, 실제={actual}")

    auto_test("양수 더하기", add(2, 3), 5)
    auto_test("음수 더하기", add(-1, 1), 0)
    auto_test("0 더하기", add(0, 0), 0)
    auto_test("큰 수 더하기", add(999999, 1), 1000000)

    print(f"    결과: {tests_passed}/{tests_total} 통과!")
    print("    → 버튼 하나로 수천 개 테스트를 1초 만에!")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 테스트 피라미드
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 테스트 피라미드:")
    print()
    print("         /\\")
    print("        /  \\       E2E 테스트 (적게)")
    print("       /    \\      → 전체 시스템 테스트")
    print("      /──────\\")
    print("     /        \\    통합 테스트 (보통)")
    print("    /          \\   → 모듈 간 연동 테스트")
    print("   /────────────\\")
    print("  /              \\  단위 테스트 (많이!)")
    print(" /                \\ → 함수/클래스 하나하나 테스트")
    print(" ──────────────────")
    print()
    print("  → 단위 테스트를 가장 많이 작성하는 것이 이상적!")
    print()


# =========================================================================
#
#   레슨 2 — unittest 기초
#
# =========================================================================

# ─── 테스트 대상 코드 ───

def calculate_grade(score: int) -> str:
    """점수를 등급으로 변환합니다."""
    if not isinstance(score, (int, float)):
        raise TypeError("점수는 숫자여야 합니다")
    if score < 0 or score > 100:
        raise ValueError("점수는 0~100 사이여야 합니다")
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


class GradeTests(unittest.TestCase):
    """등급 계산 테스트 — unittest.TestCase를 상속합니다."""

    # ─── setUp: 각 테스트 전에 실행 ───
    def setUp(self):
        """각 테스트 시작 전에 호출됩니다. 공통 준비 작업."""
        self.test_scores = [95, 85, 75, 65, 55]

    # ─── tearDown: 각 테스트 후에 실행 ───
    def tearDown(self):
        """각 테스트 끝난 후에 호출됩니다. 정리 작업."""
        pass  # 여기서는 정리할 것이 없음

    def test_A_grade(self):
        self.assertEqual(calculate_grade(95), "A")
        self.assertEqual(calculate_grade(90), "A")
        self.assertEqual(calculate_grade(100), "A")

    def test_B_grade(self):
        self.assertEqual(calculate_grade(85), "B")
        self.assertEqual(calculate_grade(80), "B")

    def test_C_grade(self):
        self.assertEqual(calculate_grade(75), "C")
        self.assertEqual(calculate_grade(70), "C")

    def test_D_grade(self):
        self.assertEqual(calculate_grade(65), "D")
        self.assertEqual(calculate_grade(60), "D")

    def test_F_grade(self):
        self.assertEqual(calculate_grade(55), "F")
        self.assertEqual(calculate_grade(0), "F")

    def test_invalid_score_raises_error(self):
        with self.assertRaises(ValueError):
            calculate_grade(-1)
        with self.assertRaises(ValueError):
            calculate_grade(101)

    def test_invalid_type_raises_error(self):
        with self.assertRaises(TypeError):
            calculate_grade("A")


def lesson2_unittest_basics():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : unittest 기초               │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ unittest란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   파이썬 표준 라이브러리에 포함된 테스트 프레임워크입니다.
    #   Java의 JUnit에서 영감을 받았습니다.
    #
    #   비유: 공장의 품질 검사 라인
    #     → 제품이 컨베이어 벨트를 타고 지나가면서
    #     → 각 검사 스테이션에서 규격 확인!
    #     → 하나라도 불합격이면 즉시 알림!
    #
    #   구조:
    #   - TestCase: 테스트 클래스 (검사 스테이션)
    #   - test_xxx: 테스트 메서드 (개별 검사 항목)
    #   - setUp/tearDown: 준비/정리 작업
    #

    print("  ─── unittest 실행 ───")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(GradeTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print()

    print("  ─── 실행 방법 ───")
    print("    터미널에서:")
    print("    $ python -m unittest 파일명.py")
    print("    $ python -m unittest 파일명.TestClass.test_method")
    print("    $ python -m unittest discover  # 자동 탐색")
    print()


# =========================================================================
#
#   레슨 3 — assert 메서드 총정리
#
# =========================================================================

def lesson3_assert_methods():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : assert 메서드 총정리         │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ unittest의 assert 메서드들
    # ─────────────────────────────────────────────────────────────────────
    #
    #   unittest.TestCase는 다양한 비교 메서드를 제공합니다.
    #   일반 assert보다 실패 시 더 자세한 정보를 보여줍니다!
    #

    # ─── 직접 구현한 미니 테스트 프레임워크로 보여드리기 ───

    passed = 0
    total = 0

    def check(name, condition, detail=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"    ✓ {name}")
        else:
            print(f"    ✗ {name} — {detail}")

    # assertEqual — 같은지 비교
    print("  ■ assertEqual(a, b) — 두 값이 같은가?")
    check("1 + 1 == 2", 1 + 1 == 2)
    check("'hello' == 'hello'", "hello" == "hello")
    print()

    # assertNotEqual
    print("  ■ assertNotEqual(a, b) — 두 값이 다른가?")
    check("1 != 2", 1 != 2)
    print()

    # assertTrue / assertFalse
    print("  ■ assertTrue(x) / assertFalse(x)")
    check("True is truthy", bool(True))
    check("[1,2,3] is truthy", bool([1, 2, 3]))
    check("[] is falsy", not bool([]))
    check("0 is falsy", not bool(0))
    print()

    # assertIs / assertIsNone
    print("  ■ assertIs(a, b) / assertIsNone(x)")
    a = [1, 2]
    b = a
    c = [1, 2]
    check("a is b (같은 객체)", a is b)
    check("a is not c (다른 객체)", a is not c)
    check("None is None", None is None)
    print()

    # assertIn
    print("  ■ assertIn(a, b) — a가 b에 포함되어 있는가?")
    check("3 in [1, 2, 3]", 3 in [1, 2, 3])
    check("'py' in 'python'", "py" in "python")
    print()

    # assertAlmostEqual — 부동소수점 비교!
    print("  ■ assertAlmostEqual(a, b) — 거의 같은가? (소수점)")
    check("0.1+0.2 ≈ 0.3", abs((0.1 + 0.2) - 0.3) < 1e-7)
    print("    → 부동소수점 비교에 필수!")
    print()

    # assertRaises — 예외 발생 확인
    print("  ■ assertRaises(Error) — 예외가 발생하는가?")
    try:
        int("abc")
        check("int('abc') raises ValueError", False)
    except ValueError:
        check("int('abc') raises ValueError", True)
    print()

    # assertIsInstance
    print("  ■ assertIsInstance(obj, class)")
    check("42 is int", isinstance(42, int))
    check("'hello' is str", isinstance("hello", str))
    check("[1,2] is list", isinstance([1, 2], list))
    print()

    print(f"  결과: {passed}/{total} 통과!")
    print()


# =========================================================================
#
#   레슨 4 — pytest 기초
#
# =========================================================================

def lesson4_pytest_basics():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : pytest 기초                 │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ pytest란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   pytest는 파이썬에서 가장 인기 있는 서드파티 테스트 프레임워크입니다.
    #   unittest보다 간결하고 강력합니다!
    #
    #   비유: unittest가 수동 기어 자동차라면
    #         pytest는 자동 기어 자동차!
    #     → 더 편하고, 더 많은 기능이 자동으로!
    #
    #   설치: pip install pytest
    #   실행: pytest 파일명.py
    #

    print("  ■ unittest vs pytest 비교:")
    print()
    print("  [unittest 스타일]")
    print("    class TestAdd(unittest.TestCase):")
    print("        def test_add(self):")
    print("            self.assertEqual(add(2, 3), 5)")
    print()
    print("  [pytest 스타일]")
    print("    def test_add():       # 클래스 불필요!")
    print("        assert add(2, 3) == 5  # 그냥 assert!")
    print()

    # ─── pytest 스타일로 테스트 작성 (시뮬레이션) ───

    print("  ─── pytest 스타일 테스트 시뮬레이션 ───")

    def multiply(a, b):
        return a * b

    # pytest는 그냥 함수에 assert만 쓰면 됩니다
    def test_multiply_positive():
        assert multiply(3, 4) == 12

    def test_multiply_zero():
        assert multiply(5, 0) == 0

    def test_multiply_negative():
        assert multiply(-2, 3) == -6

    tests = [test_multiply_positive, test_multiply_zero, test_multiply_negative]
    for t in tests:
        try:
            t()
            print(f"    ✓ {t.__name__}")
        except (AssertionError, Exception) as e:
            print(f"    ✗ {t.__name__}: {e}")
    print()

    # ─── 픽스처 (@pytest.fixture) 개념 ───

    print("  ■ 픽스처 (Fixture) 개념:")
    print("    → 테스트에 필요한 데이터/환경을 미리 준비하는 것")
    print()
    print("    @pytest.fixture")
    print("    def sample_students():")
    print("        return [")
    print('        {"name": "민수", "score": 95},')
    print('        {"name": "지유", "score": 88},')
    print("    ]")
    print()
    print("    def test_top_student(sample_students):")
    print("        top = max(sample_students, key=lambda s: s['score'])")
    print("        assert top['name'] == '민수'")
    print()

    # ─── 파라미터화 (@pytest.mark.parametrize) 개념 ───

    print("  ■ 파라미터화 (Parametrize) 개념:")
    print("    → 같은 테스트를 여러 입력값으로 반복!")
    print()
    print("    @pytest.mark.parametrize('score,expected', [")
    print("        (95, 'A'),")
    print("        (85, 'B'),")
    print("        (75, 'C'),")
    print("        (55, 'F'),")
    print("    ])")
    print("    def test_grade(score, expected):")
    print("        assert calculate_grade(score) == expected")
    print()

    # 실제로 파라미터화를 시뮬레이션
    print("  ─── 파라미터화 시뮬레이션 ───")
    params = [(95, "A"), (85, "B"), (75, "C"), (65, "D"), (55, "F")]
    for score, expected in params:
        result = calculate_grade(score)
        status = "✓" if result == expected else "✗"
        print(f"    {status} grade({score}) == '{expected}'")
    print()


# =========================================================================
#
#   레슨 5 — 모킹 (Mock)
#
# =========================================================================

def lesson5_mocking():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 모킹 (Mock)                │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 모킹이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   "가짜 객체"를 만들어서 테스트하는 기법입니다.
    #
    #   비유: 영화 촬영에서 스턴트맨
    #     → 실제 배우 대신 스턴트맨이 위험한 장면을 담당
    #     → 테스트에서 실제 DB/API 대신 Mock이 담당!
    #
    #   왜 필요한가?
    #   - 데이터베이스에 연결 안 해도 테스트 가능
    #   - 외부 API 호출 없이 테스트 가능
    #   - 네트워크 문제와 무관하게 테스트 가능
    #   - 테스트가 빠르고 안정적!
    #

    # ─── MagicMock 기본 사용법 ───

    print("  ─── MagicMock 기본 ───")

    # 가짜 데이터베이스 만들기
    mock_db = MagicMock()
    mock_db.get_user.return_value = {"name": "민수", "age": 15}

    # 가짜 DB를 사용하는 함수
    def get_user_name(db, user_id):
        user = db.get_user(user_id)
        return user["name"]

    result = get_user_name(mock_db, 42)
    print(f"    Mock DB에서 가져온 이름: {result}")
    print(f"    get_user가 호출되었나?: {mock_db.get_user.called}")
    print(f"    호출된 인자: {mock_db.get_user.call_args}")
    print()

    # ─── side_effect 활용 ───

    print("  ─── side_effect (부작용 설정) ───")

    mock_api = MagicMock()

    # 첫 호출은 성공, 두 번째는 에러!
    mock_api.fetch.side_effect = [
        {"status": "ok", "data": [1, 2, 3]},
        ConnectionError("서버 연결 실패!"),
    ]

    # 첫 번째 호출
    result1 = mock_api.fetch()
    print(f"    첫 번째 호출: {result1}")

    # 두 번째 호출 — 에러!
    try:
        result2 = mock_api.fetch()
    except ConnectionError as e:
        print(f"    두 번째 호출: {e}")
    print()

    # ─── 실전: 이메일 발송 테스트 ───

    print("  ─── 실전: 이메일 발송 테스트 ───")

    class EmailService:
        def send(self, to: str, subject: str, body: str) -> bool:
            """실제로는 이메일을 보내지만, 테스트에서는 Mock!"""
            raise NotImplementedError("실제 서비스 구현 필요")

    class OrderProcessor:
        def __init__(self, email_service: EmailService):
            self.email_service = email_service

        def process_order(self, user_email: str, item: str) -> str:
            # 주문 처리 로직...
            self.email_service.send(
                to=user_email,
                subject=f"주문 확인: {item}",
                body=f"{item} 주문이 완료되었습니다.",
            )
            return f"{item} 주문 처리 완료"

    # Mock 이메일 서비스로 테스트!
    mock_email = MagicMock(spec=EmailService)
    mock_email.send.return_value = True

    processor = OrderProcessor(mock_email)
    result = processor.process_order("test@example.com", "파이썬 책")

    print(f"    결과: {result}")
    print(f"    이메일 발송 호출됨: {mock_email.send.called}")
    print(f"    발송 대상: {mock_email.send.call_args}")
    print()


# =========================================================================
#
#   레슨 6 — TDD 실습
#
# =========================================================================

def lesson6_tdd():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : TDD 실습                   │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ TDD (Test-Driven Development)란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   "테스트를 먼저 쓰고, 그 다음에 코드를 쓴다!"
    #
    #   비유: 시험 문제를 먼저 보고 공부하는 것!
    #     → 문제를 보면 뭘 공부해야 할지 명확해지죠?
    #
    #   TDD 3단계 (Red-Green-Refactor):
    #   1. RED    — 실패하는 테스트를 먼저 작성
    #   2. GREEN  — 테스트를 통과하는 최소한의 코드 작성
    #   3. REFACTOR — 코드를 깔끔하게 정리 (테스트는 계속 통과해야!)
    #

    print("  ■ TDD로 계산기 만들기 (Red → Green → Refactor)")
    print()

    # ─── 단계 1: RED — 테스트 먼저 작성! ───

    print("  [1단계: RED — 테스트 먼저 작성]")
    print("    → 아직 Calculator 클래스가 없으니 테스트는 실패!")
    print()
    print("    def test_add():")
    print("        calc = Calculator()")
    print("        assert calc.add(2, 3) == 5")
    print("    # → NameError: Calculator가 없음!")
    print()

    # ─── 단계 2: GREEN — 최소한의 구현 ───

    print("  [2단계: GREEN — 최소한의 구현]")

    class Calculator:
        def add(self, a, b):
            return a + b

        def subtract(self, a, b):
            return a - b

        def multiply(self, a, b):
            return a * b

        def divide(self, a, b):
            if b == 0:
                raise ValueError("0으로 나눌 수 없습니다")
            return a / b

    calc = Calculator()
    print(f"    calc.add(2, 3) = {calc.add(2, 3)} ✓")
    print(f"    calc.subtract(10, 4) = {calc.subtract(10, 4)} ✓")
    print(f"    calc.multiply(3, 5) = {calc.multiply(3, 5)} ✓")
    print(f"    calc.divide(10, 3) = {calc.divide(10, 3):.2f} ✓")
    print()

    # ─── 단계 3: REFACTOR + 추가 테스트 ───

    print("  [3단계: REFACTOR — 엣지케이스 추가]")

    tests = [
        ("add(0, 0)", calc.add(0, 0), 0),
        ("add(-1, -1)", calc.add(-1, -1), -2),
        ("subtract(0, 5)", calc.subtract(0, 5), -5),
        ("multiply(0, 100)", calc.multiply(0, 100), 0),
        ("multiply(-2, -3)", calc.multiply(-2, -3), 6),
    ]

    for name, actual, expected in tests:
        status = "✓" if actual == expected else "✗"
        print(f"    {status} {name} = {actual}")

    # 0으로 나누기 테스트
    try:
        calc.divide(10, 0)
        print("    ✗ divide(10, 0) should raise ValueError!")
    except ValueError:
        print("    ✓ divide(10, 0) raises ValueError")
    print()

    print("  ■ TDD의 장점:")
    print("    1. 설계가 명확해짐 (테스트가 명세 역할)")
    print("    2. 과도한 구현 방지 (필요한 것만 만듦)")
    print("    3. 자동 회귀 테스트 확보")
    print("    4. 코드 수정에 대한 자신감!")
    print()


# =========================================================================
#
#   레슨 7 — 테스트 커버리지
#
# =========================================================================

def lesson7_coverage():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 테스트 커버리지              │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 테스트 커버리지란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   "내 테스트가 코드의 몇 %를 실행하는가?"
    #
    #   비유: 건물 소방 점검
    #     → 1층만 점검하고 끝내면? 2층에 불나면?
    #     → 모든 층을 점검해야 안전!
    #     → 커버리지 = 점검한 층 / 전체 층 수
    #

    print("  ■ 커버리지 측정 방법:")
    print("    $ pip install coverage")
    print("    $ coverage run -m pytest")
    print("    $ coverage report")
    print("    $ coverage html  # HTML 리포트 생성")
    print()

    # ─── 무엇을 테스트해야 하는가? ───

    print("  ■ 무엇을 테스트할지 결정하는 기준:")
    print()

    # 예시 함수
    def calculate_discount(price: int, quantity: int, is_vip: bool) -> int:
        """할인 계산 — 다양한 분기가 있습니다."""
        if price < 0 or quantity < 0:
            raise ValueError("음수 불가")

        total = price * quantity

        # 대량 구매 할인
        if quantity >= 100:
            total = int(total * 0.8)   # 20% 할인
        elif quantity >= 50:
            total = int(total * 0.9)   # 10% 할인
        elif quantity >= 10:
            total = int(total * 0.95)  # 5% 할인

        # VIP 추가 할인
        if is_vip:
            total = int(total * 0.95)  # 추가 5%

        return total

    # ─── 경계값 테스트 ───

    print("  ─── 경계값 테스트 ───")
    boundary_tests = [
        ("quantity=9 (할인 없음)", 1000, 9, False, 9000),
        ("quantity=10 (5% 할인 시작)", 1000, 10, False, 9500),
        ("quantity=49 (5% 할인)", 1000, 49, False, 46550),
        ("quantity=50 (10% 할인 시작)", 1000, 50, False, 45000),
        ("quantity=99 (10% 할인)", 1000, 99, False, 89100),
        ("quantity=100 (20% 할인 시작)", 1000, 100, False, 80000),
    ]

    for desc, price, qty, vip, expected in boundary_tests:
        actual = calculate_discount(price, qty, vip)
        status = "✓" if actual == expected else "✗"
        print(f"    {status} {desc}: {actual}")
    print()

    # ─── 엣지케이스 테스트 ───

    print("  ─── 엣지케이스 테스트 ───")

    edge_tests = [
        ("가격 0", 0, 10, False, 0),
        ("수량 0", 1000, 0, False, 0),
        ("VIP 할인", 1000, 10, True, 9025),
    ]

    for desc, price, qty, vip, expected in edge_tests:
        actual = calculate_discount(price, qty, vip)
        status = "✓" if actual == expected else "✗"
        print(f"    {status} {desc}: {actual}")

    # 에러 케이스
    for desc, price, qty in [("음수 가격", -100, 10), ("음수 수량", 100, -1)]:
        try:
            calculate_discount(price, qty, False)
            print(f"    ✗ {desc}: ValueError 미발생!")
        except ValueError:
            print(f"    ✓ {desc}: ValueError 발생!")
    print()


# =========================================================================
#
#   레슨 8 — 통합 테스트 vs 단위 테스트
#
# =========================================================================

def lesson8_unit_vs_integration():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 8 : 통합 테스트 vs 단위 테스트   │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 단위 테스트 (Unit Test)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   하나의 함수/메서드만 독립적으로 테스트합니다.
    #
    #   비유: 자동차 부품 개별 검사
    #     → 브레이크 패드 따로, 엔진 오일 따로, 타이어 따로
    #

    print("  ■ 단위 테스트 예시:")

    class UserValidator:
        @staticmethod
        def validate_email(email: str) -> bool:
            return "@" in email and "." in email.split("@")[-1]

        @staticmethod
        def validate_age(age: int) -> bool:
            return 0 < age < 150

        @staticmethod
        def validate_name(name: str) -> bool:
            return len(name.strip()) >= 2

    # 각 함수를 개별 테스트 (단위 테스트)
    unit_tests = [
        ("이메일 유효", UserValidator.validate_email("test@gmail.com"), True),
        ("이메일 무효(@없음)", UserValidator.validate_email("testgmail"), False),
        ("나이 유효", UserValidator.validate_age(25), True),
        ("나이 무효(음수)", UserValidator.validate_age(-1), False),
        ("이름 유효", UserValidator.validate_name("민수"), True),
        ("이름 무효(1글자)", UserValidator.validate_name("A"), False),
    ]

    for desc, actual, expected in unit_tests:
        status = "✓" if actual == expected else "✗"
        print(f"    {status} {desc}: {actual}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 통합 테스트 (Integration Test)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   여러 컴포넌트를 함께 테스트합니다.
    #
    #   비유: 자동차 부품을 조립한 후 시운전
    #     → 개별 부품은 OK인데 조립하면 안 맞을 수도!
    #

    print("  ■ 통합 테스트 예시:")

    class UserService:
        def __init__(self):
            self.users = {}
            self.validator = UserValidator()

        def register(self, name: str, email: str, age: int) -> dict:
            """여러 검증기를 통합하여 사용자를 등록합니다."""
            errors = []
            if not self.validator.validate_name(name):
                errors.append("이름이 너무 짧습니다")
            if not self.validator.validate_email(email):
                errors.append("이메일 형식이 잘못되었습니다")
            if not self.validator.validate_age(age):
                errors.append("나이가 유효하지 않습니다")

            if errors:
                return {"success": False, "errors": errors}

            user_id = len(self.users) + 1
            self.users[user_id] = {"name": name, "email": email, "age": age}
            return {"success": True, "user_id": user_id}

    service = UserService()

    # 통합 테스트: 전체 흐름 테스트
    result1 = service.register("민수", "minsu@gmail.com", 15)
    result2 = service.register("", "bad-email", -1)

    print(f"    정상 등록: {result1}")
    print(f"    잘못된 입력: {result2}")
    print()

    # ─── 비교표 ───

    print("  ■ 단위 테스트 vs 통합 테스트 비교:")
    print(f"    {'항목':^12} {'단위 테스트':^14} {'통합 테스트':^14}")
    print(f"    {'─' * 12} {'─' * 14} {'─' * 14}")
    print(f"    {'범위':^12} {'함수 하나':^14} {'모듈 여러 개':^14}")
    print(f"    {'속도':^12} {'빠름':^14} {'느림':^14}")
    print(f"    {'격리':^12} {'독립적':^14} {'의존적':^14}")
    print(f"    {'버그 위치':^12} {'정확':^14} {'대략적':^14}")
    print(f"    {'비중':^12} {'많이':^14} {'적당히':^14}")
    print()


# =========================================================================
#
#   레슨 9 — 실전: 쇼핑몰 할인 시스템 TDD로 구현
#
# =========================================================================

def lesson9_shopping_tdd():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 9 : 쇼핑몰 할인 시스템 (TDD)    │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 요구사항
    # ─────────────────────────────────────────────────────────────────────
    #
    #   쇼핑몰 할인 규칙:
    #   1. 기본가: 상품가격 × 수량
    #   2. 쿠폰 할인: 고정 금액 또는 비율 할인
    #   3. 등급 할인: BRONZE 3%, SILVER 5%, GOLD 10%, VIP 15%
    #   4. 최소 결제액: 할인 후 최소 1000원
    #   5. 무료배송: 50000원 이상 구매 시
    #

    print("  ─── TDD 1단계: 테스트를 먼저 정의 ───")
    print()

    # ─── 구현 ───

    from enum import Enum

    class MemberGrade(Enum):
        BRONZE = "bronze"
        SILVER = "silver"
        GOLD = "gold"
        VIP = "vip"

    class Coupon:
        def __init__(self, coupon_type: str, value: int):
            """
            coupon_type: 'fixed' (고정 금액) 또는 'percent' (비율)
            value: 할인 금액 또는 할인 퍼센트(0~100)
            """
            self.coupon_type = coupon_type
            self.value = value

        def apply(self, price: int) -> int:
            if self.coupon_type == "fixed":
                return max(price - self.value, 0)
            elif self.coupon_type == "percent":
                return int(price * (100 - self.value) / 100)
            return price

    class ShoppingCart:
        GRADE_DISCOUNTS = {
            MemberGrade.BRONZE: 0.03,
            MemberGrade.SILVER: 0.05,
            MemberGrade.GOLD: 0.10,
            MemberGrade.VIP: 0.15,
        }
        FREE_SHIPPING_THRESHOLD = 50_000
        SHIPPING_FEE = 3_000
        MIN_PAYMENT = 1_000

        def __init__(self, grade: MemberGrade = MemberGrade.BRONZE):
            self.items: list[dict] = []
            self.grade = grade
            self.coupon: Coupon | None = None

        def add_item(self, name: str, price: int, quantity: int = 1):
            if price < 0 or quantity < 0:
                raise ValueError("가격과 수량은 0 이상이어야 합니다")
            self.items.append({"name": name, "price": price, "quantity": quantity})

        def apply_coupon(self, coupon: Coupon):
            self.coupon = coupon

        def subtotal(self) -> int:
            return sum(item["price"] * item["quantity"] for item in self.items)

        def calculate_total(self) -> dict:
            sub = self.subtotal()

            # 쿠폰 할인
            after_coupon = self.coupon.apply(sub) if self.coupon else sub

            # 등급 할인
            grade_discount = int(after_coupon * self.GRADE_DISCOUNTS[self.grade])
            after_grade = after_coupon - grade_discount

            # 최소 결제액 보장
            final = max(after_grade, self.MIN_PAYMENT) if sub > 0 else 0

            # 배송비
            shipping = 0 if final >= self.FREE_SHIPPING_THRESHOLD else self.SHIPPING_FEE
            if final == 0:
                shipping = 0

            return {
                "subtotal": sub,
                "coupon_discount": sub - after_coupon,
                "grade_discount": grade_discount,
                "final_price": final,
                "shipping_fee": shipping,
                "total": final + shipping,
            }

    # ─── TDD 테스트 실행 ───

    print("  ─── TDD 2단계: 테스트 실행 ───")
    print()
    passed = 0
    total = 0

    def assert_test(desc, condition):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"    ✓ {desc}")
        else:
            print(f"    ✗ {desc}")

    # 테스트 1: 기본 가격 계산
    cart = ShoppingCart()
    cart.add_item("연필", 500, 3)
    cart.add_item("공책", 1500, 2)
    assert_test("기본가 계산 (500*3 + 1500*2 = 4500)",
                cart.subtotal() == 4500)

    # 테스트 2: 고정 쿠폰 할인
    cart2 = ShoppingCart()
    cart2.add_item("가방", 30000, 1)
    cart2.apply_coupon(Coupon("fixed", 5000))
    result2 = cart2.calculate_total()
    assert_test("고정 쿠폰 5000원 할인",
                result2["coupon_discount"] == 5000)

    # 테스트 3: 비율 쿠폰 할인
    cart3 = ShoppingCart()
    cart3.add_item("신발", 50000, 1)
    cart3.apply_coupon(Coupon("percent", 10))
    result3 = cart3.calculate_total()
    assert_test("비율 쿠폰 10% 할인 (50000 → 45000)",
                result3["subtotal"] - result3["coupon_discount"] == 45000)

    # 테스트 4: 등급 할인 (GOLD 10%)
    cart4 = ShoppingCart(MemberGrade.GOLD)
    cart4.add_item("노트북", 100000, 1)
    result4 = cart4.calculate_total()
    assert_test("GOLD 등급 10% 할인",
                result4["grade_discount"] == 10000)

    # 테스트 5: 무료배송 (50000원 이상)
    cart5 = ShoppingCart()
    cart5.add_item("책", 60000, 1)
    result5 = cart5.calculate_total()
    assert_test("50000원 이상 무료배송",
                result5["shipping_fee"] == 0)

    # 테스트 6: 유료배송 (50000원 미만)
    cart6 = ShoppingCart()
    cart6.add_item("볼펜", 1000, 1)
    result6 = cart6.calculate_total()
    assert_test("50000원 미만 배송비 3000원",
                result6["shipping_fee"] == 3000)

    # 테스트 7: 최소 결제액
    cart7 = ShoppingCart(MemberGrade.VIP)
    cart7.add_item("샘플", 1200, 1)
    cart7.apply_coupon(Coupon("fixed", 1000))
    result7 = cart7.calculate_total()
    assert_test("최소 결제액 1000원 보장",
                result7["final_price"] >= 1000)

    # 테스트 8: 빈 장바구니
    cart8 = ShoppingCart()
    result8 = cart8.calculate_total()
    assert_test("빈 장바구니 = 0원",
                result8["total"] == 0)

    # 테스트 9: 음수 가격 에러
    cart9 = ShoppingCart()
    try:
        cart9.add_item("에러상품", -100, 1)
        assert_test("음수 가격 → ValueError", False)
    except ValueError:
        assert_test("음수 가격 → ValueError", True)

    print()
    print(f"  ★ TDD 결과: {passed}/{total} 테스트 통과!")
    print()

    # ─── 결과 상세 출력 ───

    print("  ─── 주문 상세 예시 (GOLD 회원, 10% 쿠폰) ───")
    demo_cart = ShoppingCart(MemberGrade.GOLD)
    demo_cart.add_item("파이썬 책", 35000, 1)
    demo_cart.add_item("노트", 3000, 5)
    demo_cart.apply_coupon(Coupon("percent", 10))
    demo_result = demo_cart.calculate_total()

    print(f"    소계:       {demo_result['subtotal']:>8,}원")
    print(f"    쿠폰 할인:  -{demo_result['coupon_discount']:>7,}원")
    print(f"    등급 할인:  -{demo_result['grade_discount']:>7,}원")
    print(f"    상품 금액:   {demo_result['final_price']:>8,}원")
    print(f"    배송비:      {demo_result['shipping_fee']:>8,}원")
    print(f"    ────────────────────────")
    print(f"    결제 금액:   {demo_result['total']:>8,}원")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인 실행
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
    print("  파이썬 학습 12단계: 테스트")
    print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
    print()

    lesson1_why_testing()
    lesson2_unittest_basics()
    lesson3_assert_methods()
    lesson4_pytest_basics()
    lesson5_mocking()
    lesson6_tdd()
    lesson7_coverage()
    lesson8_unit_vs_integration()
    lesson9_shopping_tdd()

    print("=" * 60)
    print("  12단계 완료! 테스트의 핵심 개념을 모두 배웠습니다.")
    print("=" * 60)


if __name__ == "__main__":
    main()
