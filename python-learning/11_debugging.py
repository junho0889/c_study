# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   파이썬 학습 11단계: 디버깅
#   ─ 버그 종류, print 디버깅, assert, breakpoint, 흔한 버그, 로깅, 프로파일링 ─
#   ■ 실행 방법: python 11_debugging.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 디버깅이란? — 버그의 종류, 디버깅 마인드셋
#   2. print 디버깅 — f-string 활용, pprint, __repr__, 조건부 출력
#   3. assert 활용 — assert문 패턴, 언제 쓰는지, -O 옵션
#   4. 중단점(breakpoint) — breakpoint(), pdb 사용법
#   5. 흔한 버그 패턴 — 가변 기본인자, 루프에서 수정, 얕은복사, is vs ==
#   6. 로깅(logging) — print 대신 logging, 레벨, 포맷, 파일 출력
#   7. traceback 읽기 — 에러 메시지 해석법, stack trace 따라가기
#   8. 프로파일링 기초 — time.perf_counter, cProfile, 병목 찾기
#   9. 실전: 버그 있는 코드 10개 수정 챌린지
#
# ─────────────────────────────────────────────────────────────────────────

import copy
import logging
import time
import traceback
from pprint import pformat


# =========================================================================
#
#   레슨 1 — 디버깅이란?
#
# =========================================================================

def lesson1_what_is_debugging():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 디버깅이란?                 │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 버그(Bug)의 유래
    # ─────────────────────────────────────────────────────────────────────
    #
    #   1947년, 하버드 대학의 Mark II 컴퓨터에서 진짜 나방(bug)이
    #   회로에 끼어서 오작동을 일으켰습니다.
    #   그때부터 프로그램 오류를 "버그"라고 부르게 되었습니다!
    #
    #   디버깅(Debugging) = 버그를 찾아서 제거하는 과정
    #
    #   비유: 의사의 진료 과정
    #     1. 증상 확인 → "어디가 아프세요?"
    #     2. 검사 → 혈액 검사, X-ray
    #     3. 진단 → "원인은 이것입니다"
    #     4. 치료 → 약 처방, 수술
    #     5. 확인 → "나았나요?"
    #

    # ─────────────────────────────────────────────────────────────────────
    # ■ 버그의 3가지 종류
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 버그의 3가지 종류:")
    print()

    # 1. 문법 에러 (Syntax Error) — 가장 찾기 쉬움!
    print("  1. 문법 에러 (SyntaxError)")
    print("     → 파이썬이 코드를 읽지도 못함")
    print("     → 예: print('hello'  ← 괄호 안 닫음")
    print("     → 해결: 에러 메시지가 정확히 위치를 알려줌!")
    print()

    # 2. 런타임 에러 (Runtime Error) — 실행 중 터짐!
    print("  2. 런타임 에러 (RuntimeError)")
    print("     → 실행하다가 갑자기 멈춤")
    print("     → 예: 0으로 나누기, 없는 인덱스 접근")

    try:
        result = 10 / 0
    except ZeroDivisionError as e:
        print(f"     → 발생: {type(e).__name__}: {e}")
    print()

    # 3. 논리 에러 (Logic Error) — 가장 찾기 어려움!
    print("  3. 논리 에러 (Logic Error)")
    print("     → 에러 없이 실행되지만 결과가 틀림")

    def buggy_average(scores):
        """버그: len - 1로 나누고 있음!"""
        return sum(scores) / (len(scores) - 1)

    scores = [80, 90, 100]
    wrong = buggy_average(scores)
    correct = sum(scores) / len(scores)
    print(f"     → 버그 평균: {wrong} (틀림!)")
    print(f"     → 정확한 평균: {correct}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 디버깅 마인드셋
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 디버깅 5단계 마인드셋:")
    print("    1단계: 증상 정확히 파악 — '뭐가 잘못됐지?'")
    print("    2단계: 재현 — '언제, 어떤 입력에서 발생하지?'")
    print("    3단계: 범위 좁히기 — '어디쯤에서 잘못됐지?'")
    print("    4단계: 원인 찾기 — '왜 잘못됐지?'")
    print("    5단계: 수정 + 검증 — '고쳤고, 다시 안 생기겠지?'")
    print()


# =========================================================================
#
#   레슨 2 — print 디버깅
#
# =========================================================================

def lesson2_print_debugging():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : print 디버깅                │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ print 디버깅이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   가장 원시적이지만 가장 자주 쓰이는 디버깅 방법입니다.
    #   코드 중간중간에 print()를 넣어서 값을 확인합니다.
    #
    #   비유: 요리 중간에 맛보기
    #     → "소금 넣었는데 짜지 않나?" → 한 숟갈 먹어봄!
    #

    # ─── f-string 디버깅 (= 기호) ───
    #
    #   파이썬 3.8+ 에서 가장 편리한 디버깅 트릭!
    #   f"{변수=}" 하면 변수 이름과 값이 함께 출력됩니다.
    #

    x = 42
    name = "민수"
    items = [1, 2, 3, 4, 5]

    print("  ─── f-string 디버깅 모드 ───")
    print(f"  {x=}")
    print(f"  {name=}")
    print(f"  {len(items)=}")
    print(f"  {sum(items)=}")
    print(f"  {items[2:]=}")
    print()

    # ─── 중간값 추적 ───

    print("  ─── 중간값 추적 예시 ───")

    def process_grades(grades: dict[str, list[int]]) -> dict[str, float]:
        """학생별 평균 계산 — print로 중간 과정 추적."""
        result = {}
        for name, scores in grades.items():
            print(f"    [DEBUG] {name}: 점수={scores}")
            total = sum(scores)
            count = len(scores)
            avg = total / count if count > 0 else 0
            print(f"    [DEBUG] {name}: 합={total}, 개수={count}, 평균={avg:.1f}")
            result[name] = avg
        return result

    grades = {
        "민수": [90, 85, 92],
        "지유": [100, 95, 88],
    }
    result = process_grades(grades)
    print(f"  결과: {result}")
    print()

    # ─── pprint (Pretty Print) ───
    #
    #   복잡한 데이터 구조를 보기 좋게 출력합니다.
    #   딕셔너리가 중첩되어 있을 때 특히 유용합니다.
    #

    print("  ─── pprint 활용 ───")
    complex_data = {
        "학교": "파이썬 초등학교",
        "학년": {
            "3학년": {"반": ["1반", "2반"], "학생수": 60},
            "4학년": {"반": ["1반", "2반", "3반"], "학생수": 90},
        },
        "교사수": 15,
    }
    print(f"  일반 print: {complex_data}")
    print(f"  pformat:\n{pformat(complex_data, indent=4, width=50)}")
    print()

    # ─── __repr__ 활용 ───

    print("  ─── repr()로 숨은 문자 찾기 ───")
    text1 = "hello"
    text2 = "hello\n"        # 숨은 줄바꿈!
    text3 = "hello\t world"  # 숨은 탭!

    print(f"  text1: '{text1}' → repr: {repr(text1)}")
    print(f"  text2: '{text2.strip()}' → repr: {repr(text2)}")
    print(f"  text3: '{text3}' → repr: {repr(text3)}")
    print()

    # ─── 조건부 디버그 출력 ───

    print("  ─── 조건부 디버그 출력 ───")

    DEBUG = True  # False로 바꾸면 디버그 메시지 꺼짐

    def debug_print(*args, **kwargs):
        if DEBUG:
            print("    [DEBUG]", *args, **kwargs)

    debug_print("이 메시지는 DEBUG=True일 때만 보입니다")
    debug_print(f"현재 items = {items}")
    print()


# =========================================================================
#
#   레슨 3 — assert 활용
#
# =========================================================================

def lesson3_assert():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : assert 활용                 │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ assert란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   assert 조건, "메시지"
    #   → 조건이 False이면 AssertionError를 발생시킵니다.
    #
    #   비유: 다리 건설 중 "이 기둥이 100톤을 버틸 수 있어야 한다" 체크
    #     → 통과하면 다음 공정으로 진행
    #     → 실패하면 즉시 공사 중단!
    #
    #   ★ 중요: assert는 개발/테스트용입니다!
    #     python -O 파일.py 로 실행하면 assert가 모두 무시됩니다.
    #     사용자 입력 검증에는 if + raise를 쓰세요!
    #

    # ─── 기본 사용법 ───

    print("  ─── 기본 assert ───")

    def calculate_average(scores: list[int]) -> float:
        assert len(scores) > 0, "점수 목록이 비어있습니다!"
        assert all(0 <= s <= 100 for s in scores), "점수는 0~100 사이여야 합니다!"
        return sum(scores) / len(scores)

    result = calculate_average([90, 85, 78])
    print(f"  평균: {result}")

    try:
        calculate_average([])
    except AssertionError as e:
        print(f"  빈 리스트 → AssertionError: {e}")
    except Exception as e:
        print(f"  빈 리스트 → {type(e).__name__}: {e}")

    try:
        calculate_average([90, 150, 80])
    except AssertionError as e:
        print(f"  범위 초과 → AssertionError: {e}")
    except Exception as e:
        print(f"  범위 초과 → {type(e).__name__}: {e}")
    print()

    # ─── 함수 전후 조건 검사 (계약 프로그래밍) ───

    print("  ─── 전후 조건 검사 ───")

    def withdraw(balance: int, amount: int) -> int:
        """출금 함수 — assert로 전/후 조건을 검사합니다."""
        # 전제 조건 (precondition)
        assert balance >= 0, f"잔액이 음수: {balance}"
        assert amount > 0, f"출금액은 양수여야 합니다: {amount}"
        assert amount <= balance, f"잔액 부족: {balance} < {amount}"

        new_balance = balance - amount

        # 사후 조건 (postcondition)
        assert new_balance >= 0, f"출금 후 잔액이 음수: {new_balance}"
        assert new_balance == balance - amount, "계산 오류!"

        return new_balance

    balance = withdraw(10000, 3000)
    print(f"  10000에서 3000 출금 → 잔액: {balance}")
    print()

    # ─── assert vs if + raise ───

    print("  ─── assert vs if + raise 비교 ───")
    print("  assert: 개발자의 가정을 검증 (개발 중 사용)")
    print("    → python -O 로 실행하면 무시됨!")
    print("    → 예: assert len(items) > 0")
    print()
    print("  if + raise: 사용자 입력 검증 (항상 필요)")
    print("    → 프로덕션에서도 동작!")
    print("    → 예: if age < 0: raise ValueError(...)")
    print()


# =========================================================================
#
#   레슨 4 — 중단점 (breakpoint)
#
# =========================================================================

def lesson4_breakpoint():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : 중단점 (breakpoint)          │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ breakpoint()란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   breakpoint()는 파이썬 3.7에 추가된 내장 함수입니다.
    #   코드 실행 중에 멈추고, 변수 값을 살펴볼 수 있습니다.
    #
    #   비유: 비디오 일시정지 버튼
    #     → 영화 보다가 "잠깐, 지금 뭐라고 했어?" 하고 멈추는 것
    #     → 멈춘 상태에서 이것저것 살펴보기
    #
    #   ★ 이 레슨에서는 실제로 breakpoint()를 호출하지 않습니다.
    #     (호출하면 대화형 모드에 들어가서 스크립트가 멈추기 때문!)
    #     실제 사용법을 설명으로 보여드립니다.
    #

    print("  ■ breakpoint() 사용법:")
    print()
    print("    def find_bug(data):")
    print("        for i, item in enumerate(data):")
    print("            breakpoint()    # ← 여기서 멈춤!")
    print("            process(item)")
    print()
    print("  ■ pdb 주요 명령어:")
    print("    n (next)     → 다음 줄 실행")
    print("    s (step)     → 함수 안으로 들어가기")
    print("    c (continue) → 다음 breakpoint까지 실행")
    print("    p 변수       → 변수 값 출력 (예: p data)")
    print("    pp 변수      → 예쁘게 출력 (pprint)")
    print("    l (list)     → 현재 위치 주변 코드 보기")
    print("    w (where)    → 호출 스택 보기")
    print("    q (quit)     → 디버거 종료")
    print()

    # ─── PYTHONBREAKPOINT 환경변수 ───

    print("  ■ 환경변수로 제어하기:")
    print("    PYTHONBREAKPOINT=0 python script.py")
    print("    → breakpoint()를 모두 무시! (프로덕션에서 유용)")
    print()
    print("    PYTHONBREAKPOINT=ipdb.set_trace python script.py")
    print("    → ipdb (향상된 디버거) 사용")
    print()

    # ─── 실전 예시 ───

    print("  ■ 실전 디버깅 시나리오:")
    print()

    def find_duplicates(items: list) -> list:
        """중복 항목을 찾는 함수 — breakpoint로 디버깅하는 예시."""
        seen = set()
        duplicates = []
        for item in items:
            # 실제 디버깅 시: breakpoint()  ← 여기에 넣기
            if item in seen:
                duplicates.append(item)
            seen.add(item)
        return duplicates

    test_data = ["사과", "바나나", "사과", "체리", "바나나", "바나나"]
    result = find_duplicates(test_data)
    print(f"    입력: {test_data}")
    print(f"    중복: {result}")
    print()
    print("    → breakpoint()를 for 루프 안에 넣으면:")
    print("      매 반복마다 seen, duplicates, item 값을 확인 가능!")
    print()


# =========================================================================
#
#   레슨 5 — 흔한 버그 패턴
#
# =========================================================================

def lesson5_common_bug_patterns():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 흔한 버그 패턴              │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 버그 패턴 1: 가변 기본 인자 (Mutable Default Argument)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   함수의 기본 인자로 리스트/딕셔너리를 쓰면 큰일!
    #   기본값 객체는 함수 정의 시 딱 한 번만 만들어지기 때문입니다.
    #

    print("  ■ 버그 1: 가변 기본 인자")

    def buggy_add_item(item, items=[]):  # ← 위험!
        items.append(item)
        return items

    result1 = buggy_add_item("사과")
    result2 = buggy_add_item("바나나")    # 여전히 같은 리스트!
    print(f"    버그: result1={result1}, result2={result2}")
    print(f"    → 같은 리스트를 공유! result1 is result2: {result1 is result2}")

    def fixed_add_item(item, items=None):  # ← 올바른 방법!
        if items is None:
            items = []
        items.append(item)
        return items

    result3 = fixed_add_item("사과")
    result4 = fixed_add_item("바나나")
    print(f"    수정: result3={result3}, result4={result4}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 버그 패턴 2: 루프에서 리스트 수정
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 버그 2: 루프에서 리스트 수정")

    numbers = [1, 2, 3, 4, 5, 6]
    numbers_copy = numbers.copy()

    # 버그: 순회 중에 삭제하면 인덱스가 꼬임!
    for n in numbers_copy:
        if n % 2 == 0:
            numbers_copy.remove(n)  # ← 위험!
    print(f"    버그 결과: {numbers_copy}  (4가 남아있음!)")

    # 올바른 방법: 컴프리헨션으로 새 리스트
    numbers = [1, 2, 3, 4, 5, 6]
    odds = [n for n in numbers if n % 2 != 0]
    print(f"    수정 결과: {odds}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 버그 패턴 3: 얕은 복사 (Shallow Copy)
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 버그 3: 얕은 복사 vs 깊은 복사")

    original = [[1, 2], [3, 4]]
    shallow = original.copy()           # 얕은 복사
    deep = copy.deepcopy(original)      # 깊은 복사

    shallow[0].append(99)               # 원본도 바뀜!
    deep[1].append(88)                  # 원본 안 바뀜!

    print(f"    original: {original}  ← shallow 때문에 99 추가됨!")
    print(f"    shallow : {shallow}")
    print(f"    deep    : {deep}  ← 독립적!")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 버그 패턴 4: is vs ==
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 버그 4: is vs == 혼동")

    a = [1, 2, 3]
    b = [1, 2, 3]
    c = a

    print(f"    a == b: {a == b}  (값이 같음)")
    print(f"    a is b: {a is b}  (같은 객체가 아님!)")
    print(f"    a is c: {a is c}  (같은 객체!)")
    print()

    # ★ is를 써야 하는 경우: None 비교
    value = None
    print(f"    value is None: {value is None}  ← 올바른 방법!")
    print(f"    value == None: {value == None}  ← 동작하지만 권장하지 않음!")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 버그 패턴 5: 스코프 함정 (클로저)
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 버그 5: 루프 변수 클로저")

    # 버그: 모든 함수가 마지막 i 값을 참조!
    buggy_funcs = []
    for i in range(3):
        buggy_funcs.append(lambda: i)

    print(f"    버그: {[f() for f in buggy_funcs]}  ← 모두 2!")

    # 수정: 기본 인자로 현재 값을 캡처
    fixed_funcs = []
    for i in range(3):
        fixed_funcs.append(lambda i=i: i)

    print(f"    수정: {[f() for f in fixed_funcs]}  ← 0, 1, 2!")
    print()


# =========================================================================
#
#   레슨 6 — 로깅 (logging)
#
# =========================================================================

def lesson6_logging():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 로깅 (logging)              │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 왜 print 대신 logging?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   print 디버깅의 한계:
    #   - 배포할 때 일일이 삭제해야 함
    #   - 중요도를 구분할 수 없음 (심각한 에러 vs 정보 vs 디버그)
    #   - 파일에 저장하기 어려움
    #   - 시간/위치 정보가 없음
    #
    #   logging은 이 모든 문제를 해결합니다!
    #
    #   비유: print = 그냥 소리 지르기
    #         logging = 체계적인 사내 방송 시스템
    #         → 긴급 방송, 일반 공지, 부서별 안내를 구분할 수 있음
    #

    # ─── 로깅 레벨 (낮은 순서) ───
    #
    #   DEBUG    (10) → 개발 중 상세 정보
    #   INFO     (20) → 정상 동작 확인
    #   WARNING  (30) → 주의 필요 (기본 레벨!)
    #   ERROR    (40) → 에러 발생 (기능 실패)
    #   CRITICAL (50) → 심각한 에러 (시스템 중단)
    #

    print("  ■ 로깅 레벨:")
    print("    DEBUG    (10) — 상세한 개발 정보")
    print("    INFO     (20) — 정상 동작 확인 메시지")
    print("    WARNING  (30) — 잠재적 문제 경고")
    print("    ERROR    (40) — 에러, 기능 실패")
    print("    CRITICAL (50) — 심각한 시스템 에러")
    print()

    # ─── 기본 사용법 (직접 출력으로 시뮬레이션) ───
    #
    #   ★ 주의: logging.basicConfig()는 프로세스당 한 번만 설정 가능합니다.
    #     여기서는 개념 설명을 위해 수동으로 포맷을 만들어 보여줍니다.
    #

    print("  ■ 로깅 포맷 예시:")

    import datetime

    def fake_log(level: str, message: str):
        """logging 모듈의 출력 형태를 시뮬레이션합니다."""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"    {now} [{level:>8}] {message}")

    fake_log("DEBUG", "데이터베이스 연결 시작")
    fake_log("INFO", "사용자 '민수' 로그인 성공")
    fake_log("WARNING", "디스크 사용량 85% 초과")
    fake_log("ERROR", "파일 'data.csv'를 찾을 수 없습니다")
    fake_log("CRITICAL", "데이터베이스 연결 끊김!")
    print()

    # ─── 실전 코드 예시 ───

    print("  ■ 실전 logging 코드 예시:")
    print()
    print("    import logging")
    print()
    print("    # 로거 설정")
    print("    logging.basicConfig(")
    print("        level=logging.DEBUG,")
    print("        format='%(asctime)s [%(levelname)s] %(message)s',")
    print("        filename='app.log',  # 파일에 저장")
    print("    )")
    print()
    print("    logger = logging.getLogger(__name__)")
    print()
    print("    # 사용")
    print("    logger.debug('상세 디버그 정보')")
    print("    logger.info('정상 처리 완료')")
    print("    logger.warning('주의!')")
    print("    logger.error('에러 발생!')")
    print()

    # ─── logging vs print 비교표 ───

    print("  ■ print vs logging 비교:")
    print(f"    {'기능':^12} {'print':^10} {'logging':^10}")
    print(f"    {'─' * 12} {'─' * 10} {'─' * 10}")
    print(f"    {'레벨 구분':^12} {'X':^10} {'O':^10}")
    print(f"    {'시간 기록':^12} {'수동':^10} {'자동':^10}")
    print(f"    {'파일 저장':^12} {'수동':^10} {'자동':^10}")
    print(f"    {'끄기/켜기':^12} {'어려움':^10} {'쉬움':^10}")
    print(f"    {'포맷 설정':^12} {'수동':^10} {'자동':^10}")
    print()


# =========================================================================
#
#   레슨 7 — traceback 읽기
#
# =========================================================================

def lesson7_traceback():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : traceback 읽기              │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ traceback이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   에러가 발생하면 파이썬이 보여주는 "에러 추적 보고서"입니다.
    #
    #   비유: 범인을 찾는 CCTV 기록
    #     → "이 함수가 저 함수를 호출했고, 거기서 또 저 함수를 호출했는데..."
    #     → 마지막 줄이 범인(에러 원인)!
    #
    #   ★ 핵심: traceback은 아래에서 위로 읽으면 됩니다!
    #     → 맨 아래: 무슨 에러인지
    #     → 그 위: 어디서 발생했는지
    #     → 더 위: 누가 호출했는지
    #

    # ─── traceback 읽기 실습 ───

    def function_c(name):
        """이 함수에서 에러가 발생합니다."""
        return name.upper()  # None이면 AttributeError!

    def function_b(data):
        """function_c를 호출합니다."""
        return function_c(data.get("name"))

    def function_a():
        """function_b를 호출합니다."""
        return function_b({"grade": 3})  # name 키가 없음!

    print("  ─── traceback 읽기 실습 ───")
    try:
        function_a()
    except AttributeError:
        # traceback 문자열로 캡처
        tb = traceback.format_exc()
        print("  발생한 traceback:")
        for line in tb.strip().split("\n"):
            print(f"    {line}")
    print()

    print("  ─── traceback 읽는 순서 ───")
    print("    1. 맨 아래 줄: 에러 종류와 메시지")
    print("       → AttributeError: 'NoneType' has no attribute 'upper'")
    print("    2. 바로 위: 에러가 발생한 코드 줄")
    print("       → return name.upper()")
    print("    3. 더 위: 호출 경로 (function_a → function_b → function_c)")
    print()

    # ─── 흔한 에러 종류 ───

    print("  ─── 자주 보는 에러 종류 ───")

    errors = [
        ("TypeError", "잘못된 타입 사용", "len(42)"),
        ("ValueError", "잘못된 값", "int('abc')"),
        ("KeyError", "없는 딕셔너리 키", "d['없는키']"),
        ("IndexError", "범위 밖 인덱스", "lst[100]"),
        ("AttributeError", "없는 속성/메서드", "None.upper()"),
        ("NameError", "정의 안 된 변수", "print(없는변수)"),
        ("FileNotFoundError", "파일 없음", "open('없는파일')"),
        ("ZeroDivisionError", "0으로 나눔", "1 / 0"),
    ]

    print(f"    {'에러 종류':<25} {'원인':^15} {'예시':>20}")
    print(f"    {'─' * 25} {'─' * 15} {'─' * 20}")
    for err_name, cause, example in errors:
        print(f"    {err_name:<25} {cause:^15} {example:>20}")
    print()


# =========================================================================
#
#   레슨 8 — 프로파일링 기초
#
# =========================================================================

def lesson8_profiling():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 8 : 프로파일링 기초              │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 프로파일링이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   "이 코드가 느린데, 어디서 시간을 많이 잡아먹지?"를 찾는 과정입니다.
    #
    #   비유: 요리 시간 분석
    #     → "파스타가 30분 걸렸는데, 면 삶기 10분, 소스 만들기 15분, 플레이팅 5분"
    #     → "소스 만들기가 병목이니 미리 만들어 놓자!"
    #
    #   ★ 최적화의 첫 번째 규칙: "측정하지 않으면 최적화하지 마라!"
    #

    # ─── time.perf_counter()로 시간 측정 ───

    print("  ─── time.perf_counter() ───")

    def slow_sum(n: int) -> int:
        """의도적으로 느린 합계 (하나씩 더하기)."""
        total = 0
        for i in range(n):
            total += i
        return total

    def fast_sum(n: int) -> int:
        """빠른 합계 (수학 공식)."""
        return n * (n - 1) // 2

    n = 100_000

    start = time.perf_counter()
    result1 = slow_sum(n)
    slow_time = time.perf_counter() - start

    start = time.perf_counter()
    result2 = fast_sum(n)
    fast_time = time.perf_counter() - start

    print(f"    slow_sum({n:,}) = {result1:,}  소요: {slow_time:.6f}초")
    print(f"    fast_sum({n:,}) = {result2:,}  소요: {fast_time:.6f}초")
    if fast_time > 0:
        print(f"    속도 차이: {slow_time / fast_time:.0f}배!")
    print()

    # ─── 컨텍스트 매니저로 시간 측정 ───

    print("  ─── 시간 측정 도우미 ───")

    class Timer:
        """with문으로 코드 블록의 실행 시간을 측정합니다."""
        def __init__(self, label: str = ""):
            self.label = label
            self.elapsed = 0.0

        def __enter__(self):
            self.start = time.perf_counter()
            return self

        def __exit__(self, *args):
            self.elapsed = time.perf_counter() - self.start
            print(f"    [{self.label}] {self.elapsed:.6f}초")

    with Timer("리스트 컴프리헨션"):
        squares = [x ** 2 for x in range(100_000)]

    with Timer("map + list"):
        squares = list(map(lambda x: x ** 2, range(100_000)))
    print()

    # ─── cProfile 사용법 ───

    print("  ─── cProfile 사용법 ───")
    print()
    print("    터미널에서:")
    print("    $ python -m cProfile -s cumulative my_script.py")
    print()
    print("    코드에서:")
    print("    import cProfile")
    print("    cProfile.run('my_function()')")
    print()
    print("    결과 컬럼 설명:")
    print("    ncalls    — 호출 횟수")
    print("    tottime   — 함수 자체 소요 시간 (하위 함수 제외)")
    print("    cumtime   — 누적 시간 (하위 함수 포함)")
    print("    percall   — 호출당 시간")
    print()

    # ─── 병목 찾기 실전 ───

    print("  ─── 병목 찾기 실전 예시 ───")

    def step1_load_data():
        time.sleep(0.01)
        return list(range(10000))

    def step2_process(data):
        return [x ** 2 for x in data]

    def step3_save(data):
        time.sleep(0.02)
        return len(data)

    steps = [
        ("데이터 로딩", step1_load_data, None),
        ("데이터 처리", step2_process, None),
        ("결과 저장", step3_save, None),
    ]

    data = None
    for name, func, _ in steps:
        start = time.perf_counter()
        if data is None:
            data = func()
        else:
            data = func(data)
        elapsed = time.perf_counter() - start
        bar = "█" * int(elapsed * 500)
        print(f"    {name:<12} {elapsed:.4f}초 {bar}")

    print()
    print("    → 가장 긴 막대가 병목입니다!")
    print()


# =========================================================================
#
#   레슨 9 — 실전: 버그 있는 코드 10개 수정 챌린지
#
# =========================================================================

def lesson9_bug_challenge():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 9 : 버그 수정 챌린지 (10문제)    │")
    print("└──────────────────────────────────────┘")
    print()

    passed = 0
    total = 10

    # ─── 버그 1: Off-by-one (하나 차이 오류) ───
    print("  버그 1: 1~N 합계")
    def buggy_sum_1_to_n(n):
        return sum(range(n))  # range(n)은 0~n-1!
    def fixed_sum_1_to_n(n):
        return sum(range(1, n + 1))

    assert fixed_sum_1_to_n(5) == 15  # 1+2+3+4+5
    print(f"    버그: sum_1_to_5 = {buggy_sum_1_to_n(5)} (틀림!)")
    print(f"    수정: sum_1_to_5 = {fixed_sum_1_to_n(5)} (정답!)")
    passed += 1

    # ─── 버그 2: 정수 나눗셈 ───
    print("  버그 2: 평균 계산")
    def buggy_avg(a, b):
        return a + b / 2  # 연산자 우선순위!
    def fixed_avg(a, b):
        return (a + b) / 2

    assert fixed_avg(3, 7) == 5.0
    print(f"    버그: avg(3,7) = {buggy_avg(3, 7)} (틀림!)")
    print(f"    수정: avg(3,7) = {fixed_avg(3, 7)} (정답!)")
    passed += 1

    # ─── 버그 3: 문자열 비교 ───
    print("  버그 3: 대소문자 비교")
    def buggy_check(answer):
        return answer == "yes"
    def fixed_check(answer):
        return answer.strip().lower() == "yes"

    assert fixed_check("  YES  ")
    print(f"    버그: check('  YES  ') = {buggy_check('  YES  ')}")
    print(f"    수정: check('  YES  ') = {fixed_check('  YES  ')}")
    passed += 1

    # ─── 버그 4: 딕셔너리 키 접근 ───
    print("  버그 4: 안전한 딕셔너리 접근")
    def buggy_get_name(d):
        return d["name"]  # 키가 없으면 KeyError!
    def fixed_get_name(d):
        return d.get("name", "이름 없음")

    assert fixed_get_name({}) == "이름 없음"
    print(f"    버그: 빈 딕셔너리에서 KeyError 발생!")
    print(f"    수정: get_name({{}}) = '{fixed_get_name({})}'")
    passed += 1

    # ─── 버그 5: 빈 리스트 확인 ───
    print("  버그 5: 최대값 찾기")
    def buggy_max(lst):
        return max(lst)  # 빈 리스트면 ValueError!
    def fixed_max(lst):
        return max(lst) if lst else None

    assert fixed_max([]) is None
    assert fixed_max([3, 1, 2]) == 3
    print(f"    버그: max([])에서 ValueError 발생!")
    print(f"    수정: fixed_max([]) = {fixed_max([])}")
    passed += 1

    # ─── 버그 6: 부동소수점 비교 ───
    print("  버그 6: 실수 비교")
    def buggy_equal(a, b):
        return a == b
    def fixed_equal(a, b, epsilon=1e-9):
        return abs(a - b) < epsilon

    assert not buggy_equal(0.1 + 0.2, 0.3)  # 부동소수점 함정!
    assert fixed_equal(0.1 + 0.2, 0.3)
    print(f"    버그: 0.1+0.2 == 0.3 → {buggy_equal(0.1 + 0.2, 0.3)}")
    print(f"    수정: fixed_equal(0.1+0.2, 0.3) → {fixed_equal(0.1 + 0.2, 0.3)}")
    passed += 1

    # ─── 버그 7: 변수 스코프 ───
    print("  버그 7: 카운터 함수")
    # 버그: 함수 안에서 외부 변수를 수정하려면 nonlocal!
    counter = [0]  # 리스트를 쓰면 nonlocal 없이도 가능
    def increment():
        counter[0] += 1
    increment()
    increment()
    assert counter[0] == 2
    print(f"    리스트 트릭으로 카운터: {counter[0]}")
    passed += 1

    # ─── 버그 8: 슬라이싱 실수 ───
    print("  버그 8: 문자열 뒤집기")
    def buggy_reverse(s):
        return s[1:][::-1]  # 첫 글자 빠짐!
    def fixed_reverse(s):
        return s[::-1]

    assert fixed_reverse("hello") == "olleh"
    print(f"    버그: reverse('hello') = '{buggy_reverse('hello')}'")
    print(f"    수정: reverse('hello') = '{fixed_reverse('hello')}'")
    passed += 1

    # ─── 버그 9: 타입 혼동 ───
    print("  버그 9: 숫자 합계")
    def buggy_total(items):
        return sum(items)  # 문자열이 섞여있으면 에러!
    def fixed_total(items):
        return sum(int(x) for x in items)

    assert fixed_total(["10", "20", "30"]) == 60
    print(f"    버그: sum(['10','20','30']) → TypeError!")
    print(f"    수정: fixed_total(['10','20','30']) = {fixed_total(['10', '20', '30'])}")
    passed += 1

    # ─── 버그 10: 논리 연산 실수 ───
    print("  버그 10: 범위 검사")
    def buggy_in_range(x, lo, hi):
        return lo < x and x > hi  # 논리 오류!
    def fixed_in_range(x, lo, hi):
        return lo <= x <= hi

    assert fixed_in_range(5, 1, 10)
    assert not fixed_in_range(15, 1, 10)
    print(f"    버그: in_range(5, 1, 10) = {buggy_in_range(5, 1, 10)}")
    print(f"    수정: in_range(5, 1, 10) = {fixed_in_range(5, 1, 10)}")
    passed += 1

    print()
    print(f"  ★ 챌린지 결과: {passed}/{total} 통과!")
    print(f"    모든 버그를 찾고 수정했습니다!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인 실행
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
    print("  파이썬 학습 11단계: 디버깅")
    print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
    print()

    lesson1_what_is_debugging()
    lesson2_print_debugging()
    lesson3_assert()
    lesson4_breakpoint()
    lesson5_common_bug_patterns()
    lesson6_logging()
    lesson7_traceback()
    lesson8_profiling()
    lesson9_bug_challenge()

    print("=" * 60)
    print("  11단계 완료! 디버깅의 핵심 기법을 모두 배웠습니다.")
    print("=" * 60)


if __name__ == "__main__":
    main()
