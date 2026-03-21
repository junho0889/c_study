# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   파이썬 학습 09단계: 데코레이터와 람다
#   ─ 일급 함수, 클로저, 데코레이터, 람다, 내장 데코레이터 ─
#
#   데코레이터는 "함수에 기능을 덧입히는 포장지"이고,
#   람다는 "이름 없는 한 줄짜리 즉석 함수"입니다.
#   함수를 자유자재로 다루는 고급 기술을 배웁니다!
#
#   ■ 실행 방법: python 09_decorators_lambda.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 일급 함수(First-class Function) - 함수를 변수에, 인자로, 반환값으로
#   2. 클로저(Closure) - 외부 변수 기억, nonlocal, 팩토리
#   3. 데코레이터 기초 - @decorator, 래퍼 함수, functools.wraps
#   4. 실용 데코레이터들 - 실행시간, 로깅, 재시도, 캐싱
#   5. 인자가 있는 데코레이터 - 3중 중첩, @decorator(args)
#   6. 클래스 데코레이터 - __call__, 상태를 가진 데코레이터
#   7. 데코레이터 쌓기 - 여러 데코레이터 순서, 실행 흐름
#   8. 내장 데코레이터 - @property, @classmethod, @staticmethod 등
#   9. 람다(Lambda) 완전정복 - 문법, sorted, map/filter
#  10. 실전: 웹 프레임워크 스타일 라우터
#
# ─────────────────────────────────────────────────────────────────────────

import time
import functools


def lesson1_first_class_functions():
    # =========================================================================
    #
    #   레슨 1 — 일급 함수(First-class Function)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 일급 함수                  │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 일급 함수(First-class Function)란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   파이썬에서 함수는 "일급 객체(First-class Object)"입니다.
    #
    #   "일급"이라는 말 = "다른 값(숫자, 문자열)처럼 자유롭게 다룰 수 있다"
    #
    #   할 수 있는 것:
    #     1. 변수에 저장할 수 있다
    #     2. 함수의 인자로 전달할 수 있다
    #     3. 함수의 반환값으로 사용할 수 있다
    #     4. 리스트/딕셔너리에 저장할 수 있다
    #
    #   비유: 함수도 "물건"처럼 상자에 넣고, 선물로 주고, 가게에 진열 가능!
    #

    # ── 1. 함수를 변수에 저장 ──
    def greet(name):
        return f"안녕, {name}!"

    say_hello = greet     # 함수를 변수에 저장! (괄호 없이!)
    print(f"  [변수에 저장] say_hello('민수') = {say_hello('민수')}")
    print(f"    greet와 say_hello는 같은 함수? {greet is say_hello}")

    # ── 2. 함수를 인자로 전달 ──
    def apply_operation(func, a, b):
        """함수를 받아서 실행하는 함수"""
        return func(a, b)

    def add(x, y): return x + y
    def multiply(x, y): return x * y

    print(f"\n  [인자로 전달] apply(add, 3, 4) = {apply_operation(add, 3, 4)}")
    print(f"  [인자로 전달] apply(mul, 3, 4) = {apply_operation(multiply, 3, 4)}")

    # ── 3. 함수를 반환값으로 사용 ──
    def choose_operation(op_name):
        """문자열에 따라 함수를 골라서 반환"""
        def add(x, y): return x + y
        def sub(x, y): return x - y
        def mul(x, y): return x * y

        ops = {"더하기": add, "빼기": sub, "곱하기": mul}
        return ops.get(op_name, add)

    op = choose_operation("곱하기")
    print(f"\n  [반환값으로] choose('곱하기')(5, 3) = {op(5, 3)}")

    # ── 4. 리스트/딕셔너리에 저장 ──
    operations = [add, multiply, lambda x, y: x - y]
    print(f"\n  [리스트에 저장] 함수 3개를 리스트에:")
    for func in operations:
        print(f"    {func.__name__}(10, 3) = {func(10, 3)}")

    # ── 함수도 속성을 가진 객체! ──
    print(f"\n  [함수의 속성]")
    print(f"    greet.__name__ = {greet.__name__}")
    print(f"    greet.__doc__  = {greet.__doc__}")
    print(f"    type(greet)    = {type(greet)}")
    print()


def lesson2_closures():
    # =========================================================================
    #
    #   레슨 2 — 클로저(Closure)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : 클로저(Closure)            │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 클로저(Closure)란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   클로저 = "바깥 함수의 변수를 기억하는 안쪽 함수"
    #
    #   비유: 도시락 싸주기!
    #     엄마(바깥 함수)가 반찬(변수)을 도시락(안쪽 함수)에 넣어줌
    #     학교에 간 아이(안쪽 함수)는 도시락을 열면 반찬(변수)이 있음!
    #     엄마가 집에 없어도(바깥 함수 끝나도) 반찬은 남아있음!
    #
    #   조건 3가지:
    #     1. 함수 안에 함수가 있어야 함 (중첩 함수)
    #     2. 안쪽 함수가 바깥 함수의 변수를 사용해야 함
    #     3. 바깥 함수가 안쪽 함수를 반환해야 함
    #

    # ── 기본 클로저 ──
    def make_greeter(greeting):
        """인사말을 기억하는 함수를 만들어 반환"""
        def greeter(name):
            return f"{greeting}, {name}!"    # greeting은 바깥 변수!
        return greeter

    hello = make_greeter("안녕하세요")
    bye = make_greeter("안녕히 가세요")

    print(f"  [클로저] hello('민수') = {hello('민수')}")
    print(f"  [클로저] bye('민수')   = {bye('민수')}")

    # make_greeter는 이미 끝났지만, hello/bye는 greeting을 기억!
    # 이것이 클로저의 핵심!

    # ── 클로저가 기억하는 변수 확인 ──
    print(f"\n  [클로저 내부 들여다보기]")
    print(f"    hello의 자유 변수: {hello.__code__.co_freevars}")
    print(f"    hello의 클로저: {hello.__closure__[0].cell_contents}")

    # ── nonlocal 키워드 ──
    #
    # 클로저에서 바깥 변수를 "읽기"만 하면 nonlocal 불필요
    # 바깥 변수를 "수정"하려면 nonlocal 선언 필요!
    #
    def make_counter(initial=0):
        count = initial

        def increment():
            nonlocal count   # "바깥의 count를 수정하겠다!"
            count += 1
            return count

        def get_count():
            return count     # 읽기만 하므로 nonlocal 불필요

        return increment, get_count

    inc, get = make_counter(10)
    print(f"\n  [nonlocal - 카운터]")
    print(f"    inc() = {inc()}")     # 11
    print(f"    inc() = {inc()}")     # 12
    print(f"    inc() = {inc()}")     # 13
    print(f"    get() = {get()}")     # 13

    # ── 팩토리 패턴 (실전에서 많이 씀!) ──
    #
    # 비유: "붕어빵 틀" — 틀(팩토리)을 한번 만들면 붕어빵(함수)을 여러 개 찍어낼 수 있음
    #
    def make_multiplier(factor):
        """곱하기 함수를 만드는 팩토리"""
        def multiplier(x):
            return x * factor
        return multiplier

    double = make_multiplier(2)
    triple = make_multiplier(3)
    print(f"\n  [팩토리 패턴]")
    print(f"    double(5) = {double(5)}")    # 10
    print(f"    triple(5) = {triple(5)}")    # 15

    # ── 자주 하는 실수: 루프 변수와 클로저 ──
    #
    # ★ 주의! 클로저는 변수의 "값"이 아니라 "변수 자체"를 기억!
    #
    print(f"\n  [★ 주의: 루프 변수 함정]")

    # 잘못된 예: 모두 4를 출력! (i의 마지막 값)
    funcs_bad = []
    for i in range(5):
        funcs_bad.append(lambda: i)    # i를 "참조"함 (값이 아님!)
    print(f"    잘못: {[f() for f in funcs_bad]}")     # [4, 4, 4, 4, 4]!

    # 올바른 예: 기본값으로 값을 "캡처"!
    funcs_good = []
    for i in range(5):
        funcs_good.append(lambda x=i: x)    # x=i로 값을 즉시 캡처!
    print(f"    올바름: {[f() for f in funcs_good]}")   # [0, 1, 2, 3, 4]
    print()


def lesson3_decorator_basics():
    # =========================================================================
    #
    #   레슨 3 — 데코레이터 기초
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : 데코레이터 기초            │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 데코레이터(Decorator)란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   데코레이터 = "함수를 감싸서 기능을 추가하는 함수"
    #
    #   비유: 스마트폰 케이스!
    #     - 원래 폰(함수)은 그대로
    #     - 케이스(데코레이터)를 씌우면 추가 기능 (보호, 카드 넣기 등)
    #     - 케이스를 바꿔도 폰은 변하지 않음
    #
    #   @decorator     ← 이 한 줄이 데코레이터 적용!
    #   def function():
    #       ...
    #
    #   이것은 사실 이것과 같음:
    #   function = decorator(function)
    #

    # ── 데코레이터 없이 함수 감싸기 (옛날 방식) ──
    def my_decorator(func):
        def wrapper(*args, **kwargs):
            print("    [before] 함수 실행 전")
            result = func(*args, **kwargs)
            print("    [after] 함수 실행 후")
            return result
        return wrapper

    def say_hello():
        print("    Hello!")

    # 수동으로 감싸기
    print("  [수동 감싸기]")
    wrapped_hello = my_decorator(say_hello)
    wrapped_hello()

    # ── @decorator 문법 (파이썬스러운 방식) ──
    @my_decorator
    def say_goodbye():
        print("    Goodbye!")

    print("\n  [@decorator 문법]")
    say_goodbye()

    # ── functools.wraps의 중요성 ──
    #
    # ★ 문제: 데코레이터를 쓰면 원래 함수의 이름, 독스트링이 사라짐!
    #
    print(f"\n  [functools.wraps 없이]")
    print(f"    say_goodbye.__name__ = {say_goodbye.__name__}")  # "wrapper"!

    # ★ 해결: functools.wraps를 사용!
    def better_decorator(func):
        @functools.wraps(func)    # ← 이것이 핵심! 원래 함수 정보 보존!
        def wrapper(*args, **kwargs):
            print("    [before]")
            result = func(*args, **kwargs)
            print("    [after]")
            return result
        return wrapper

    @better_decorator
    def greet(name):
        """인사하는 함수"""
        print(f"    안녕, {name}!")

    print(f"\n  [functools.wraps 사용]")
    greet("민수")
    print(f"    greet.__name__ = {greet.__name__}")    # "greet"!
    print(f"    greet.__doc__  = {greet.__doc__}")      # "인사하는 함수"

    # ── 데코레이터 기본 템플릿 ──
    #
    #   def my_decorator(func):
    #       @functools.wraps(func)
    #       def wrapper(*args, **kwargs):
    #           # --- 함수 실행 전 처리 ---
    #           result = func(*args, **kwargs)
    #           # --- 함수 실행 후 처리 ---
    #           return result
    #       return wrapper
    #
    #   ★ *args, **kwargs → 어떤 함수에든 적용 가능!
    #   ★ functools.wraps(func) → 원래 함수 정보 보존!
    #   ★ return result → 원래 함수의 반환값 전달!
    #
    print()


def lesson4_practical_decorators():
    # =========================================================================
    #
    #   레슨 4 — 실용 데코레이터들
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : 실용 데코레이터들          │")
    print("└──────────────────────────────────────┘")
    print()

    # ── 1. 실행시간 측정 데코레이터 ──
    def timer(func):
        """함수 실행 시간을 측정하는 데코레이터"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            print(f"    {func.__name__} 실행 시간: {elapsed:.6f}초")
            return result
        return wrapper

    @timer
    def slow_sum(n):
        return sum(range(n))

    print("  [실행시간 측정]")
    result = slow_sum(1_000_000)
    print(f"    결과: {result:,}")

    # ── 2. 로깅 데코레이터 ──
    def logger(func):
        """함수 호출을 로깅하는 데코레이터"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args_str = ", ".join(repr(a) for a in args)
            kwargs_str = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
            all_args = ", ".join(filter(None, [args_str, kwargs_str]))
            print(f"    [LOG] {func.__name__}({all_args}) 호출")
            result = func(*args, **kwargs)
            print(f"    [LOG] {func.__name__} → {result!r}")
            return result
        return wrapper

    @logger
    def add(a, b):
        return a + b

    print("\n  [로깅]")
    add(3, 5)
    add(a=10, b=20)

    # ── 3. 재시도(Retry) 데코레이터 ──
    import random

    def retry(max_attempts=3):
        """실패 시 재시도하는 데코레이터 (인자 있는 데코레이터!)"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_error = None
                for attempt in range(1, max_attempts + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_error = e
                        print(f"    시도 {attempt}/{max_attempts}: 실패 ({e})")
                raise last_error
            return wrapper
        return decorator

    @retry(max_attempts=5)
    def flaky_api_call():
        """60% 확률로 실패하는 API"""
        if random.random() < 0.6:
            raise ConnectionError("서버 응답 없음")
        return {"status": "ok", "data": 42}

    print("\n  [재시도]")
    try:
        result = flaky_api_call()
        print(f"    성공: {result}")
    except ConnectionError:
        print("    최종 실패!")

    # ── 4. 간단한 캐싱 데코레이터 ──
    def memoize(func):
        """결과를 캐싱하는 데코레이터 (같은 인자 → 같은 결과 재활용)"""
        cache = {}

        @functools.wraps(func)
        def wrapper(*args):
            if args not in cache:
                cache[args] = func(*args)
                print(f"    [캐시 MISS] {func.__name__}{args} = {cache[args]}")
            else:
                print(f"    [캐시 HIT]  {func.__name__}{args} = {cache[args]}")
            return cache[args]
        return wrapper

    @memoize
    def fibonacci(n):
        if n < 2:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)

    print("\n  [캐싱 - 피보나치]")
    print(f"    fibonacci(6) = {fibonacci(6)}")
    print(f"    fibonacci(6) = {fibonacci(6)}")   # 캐시 히트!
    print()


def lesson5_decorator_with_args():
    # =========================================================================
    #
    #   레슨 5 — 인자가 있는 데코레이터
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 인자가 있는 데코레이터     │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ @decorator(인자)가 필요한 이유
    # ─────────────────────────────────────────────────────────────────────
    #
    #   기본 데코레이터: @timer → 동작이 고정됨
    #   인자 데코레이터: @repeat(3) → 동작을 커스터마이즈!
    #
    #   구조가 3중 중첩이 됨:
    #
    #   def decorator_factory(인자들):    # 1층: 인자 받기
    #       def decorator(func):           # 2층: 함수 받기
    #           @functools.wraps(func)
    #           def wrapper(*args, **kwargs):  # 3층: 실제 실행
    #               ...
    #           return wrapper
    #       return decorator
    #
    #   비유: 3중 포장!
    #     1층: "어떤 포장지를 쓸까?" (인자)
    #     2층: "무슨 선물을 포장할까?" (함수)
    #     3층: "실제로 포장 실행!" (래퍼)
    #

    # ── repeat 데코레이터 ──
    def repeat(times):
        """함수를 N번 반복 실행하는 데코레이터"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                results = []
                for i in range(times):
                    result = func(*args, **kwargs)
                    results.append(result)
                return results
            return wrapper
        return decorator

    @repeat(3)
    def say_hi(name):
        msg = f"안녕, {name}!"
        print(f"    {msg}")
        return msg

    print("  [@repeat(3)]")
    say_hi("민수")

    # ── 접근 제어 데코레이터 ──
    def require_role(role):
        """특정 역할만 실행 허용하는 데코레이터"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(user, *args, **kwargs):
                if user.get("role") != role:
                    print(f"    X 접근 거부: {user['name']}은 {role} 권한 없음!")
                    return None
                print(f"    O 접근 허용: {user['name']} ({role})")
                return func(user, *args, **kwargs)
            return wrapper
        return decorator

    @require_role("admin")
    def delete_user(user, target):
        return f"{target} 삭제 완료"

    print("\n  [@require_role('admin')]")
    admin_user = {"name": "관리자", "role": "admin"}
    normal_user = {"name": "민수", "role": "user"}
    delete_user(admin_user, "테스트계정")
    delete_user(normal_user, "테스트계정")

    # ── 범위 검증 데코레이터 ──
    def validate_range(min_val, max_val, param_name="value"):
        """인자 값의 범위를 검증하는 데코레이터"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                for arg in args:
                    if isinstance(arg, (int, float)):
                        if not (min_val <= arg <= max_val):
                            raise ValueError(
                                f"{param_name}({arg})이 범위 밖: {min_val}~{max_val}"
                            )
                return func(*args, **kwargs)
            return wrapper
        return decorator

    @validate_range(0, 100, "점수")
    def set_score(score):
        return f"점수 {score} 설정!"

    print("\n  [@validate_range(0, 100)]")
    print(f"    {set_score(85)}")
    try:
        set_score(150)
    except ValueError as e:
        print(f"    에러: {e}")
    print()


def lesson6_class_decorators():
    # =========================================================================
    #
    #   레슨 6 — 클래스 데코레이터
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 클래스 데코레이터          │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 클래스를 데코레이터로 사용하기
    # ─────────────────────────────────────────────────────────────────────
    #
    #   클래스에 __call__ 메서드가 있으면 인스턴스를 함수처럼 호출 가능!
    #   → 상태(state)를 가지는 데코레이터를 만들 수 있음!
    #
    #   비유: 함수 데코레이터 = 일회용 포장지
    #         클래스 데코레이터 = 재사용 가능한 포장 기계
    #         (호출 횟수, 로그 등을 기억할 수 있음!)
    #

    # ── 호출 횟수를 세는 데코레이터 ──
    class CountCalls:
        """함수가 몇 번 호출됐는지 추적하는 데코레이터"""
        def __init__(self, func):
            functools.update_wrapper(self, func)
            self.func = func
            self.count = 0

        def __call__(self, *args, **kwargs):
            self.count += 1
            print(f"    [{self.func.__name__}] 호출 횟수: {self.count}")
            return self.func(*args, **kwargs)

    @CountCalls
    def say_hello(name):
        return f"안녕, {name}!"

    print("  [호출 횟수 추적]")
    say_hello("민수")
    say_hello("지유")
    say_hello("서연")
    print(f"    총 호출 횟수: {say_hello.count}")

    # ── 실행 이력을 저장하는 데코레이터 ──
    class HistoryTracker:
        """함수의 모든 호출 이력을 저장"""
        def __init__(self, func):
            functools.update_wrapper(self, func)
            self.func = func
            self.history = []

        def __call__(self, *args, **kwargs):
            result = self.func(*args, **kwargs)
            self.history.append({
                "args": args, "kwargs": kwargs, "result": result
            })
            return result

        def show_history(self):
            for i, h in enumerate(self.history, 1):
                print(f"    #{i}: args={h['args']}, result={h['result']}")

    @HistoryTracker
    def multiply(a, b):
        return a * b

    print(f"\n  [실행 이력 추적]")
    multiply(3, 4)
    multiply(5, 6)
    multiply(7, 8)
    multiply.show_history()

    # ── 클래스에 데코레이터 적용하기 ──
    #
    # 함수뿐 아니라 클래스 자체에도 데코레이터를 적용할 수 있음!
    #
    def add_repr(cls):
        """클래스에 자동 __repr__ 추가"""
        def __repr__(self):
            attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
            return f"{cls.__name__}({attrs})"
        cls.__repr__ = __repr__
        return cls

    @add_repr
    class Student:
        def __init__(self, name, score):
            self.name = name
            self.score = score

    print(f"\n  [클래스에 데코레이터 적용]")
    s = Student("민수", 95)
    print(f"    repr(s) = {s!r}")
    print()


def lesson7_stacking_decorators():
    # =========================================================================
    #
    #   레슨 7 — 데코레이터 쌓기
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 데코레이터 쌓기            │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 데코레이터 쌓기 (Stacking)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   @decorator1
    #   @decorator2
    #   @decorator3
    #   def func():
    #       ...
    #
    #   이것은 이것과 같음:
    #   func = decorator1(decorator2(decorator3(func)))
    #
    #   ★ 순서가 중요!
    #     아래에서 위로 적용! (func → decorator3 → decorator2 → decorator1)
    #     실행 시에는 위에서 아래로! (decorator1 → decorator2 → decorator3 → func)
    #
    #   비유: 양파 껍질!
    #     가장 안쪽 = func
    #     그 다음 = decorator3
    #     그 다음 = decorator2
    #     가장 바깥 = decorator1
    #

    def bold(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return f"<b>{func(*args, **kwargs)}</b>"
        return wrapper

    def italic(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return f"<i>{func(*args, **kwargs)}</i>"
        return wrapper

    def underline(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return f"<u>{func(*args, **kwargs)}</u>"
        return wrapper

    # ── 순서 테스트 ──
    @bold
    @italic
    @underline
    def greet(name):
        return f"Hello, {name}"

    print("  [데코레이터 쌓기 순서]")
    result = greet("민수")
    print(f"    @bold → @italic → @underline → func")
    print(f"    결과: {result}")
    # <b><i><u>Hello, 민수</u></i></b>
    # bold가 가장 바깥, underline이 가장 안쪽!

    # ── 순서를 바꾸면? ──
    @underline
    @bold
    @italic
    def greet2(name):
        return f"Hello, {name}"

    result2 = greet2("민수")
    print(f"\n    @underline → @bold → @italic → func")
    print(f"    결과: {result2}")

    # ── 실전: 로깅 + 시간 측정 쌓기 ──
    def log_call(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f"    [LOG] {func.__name__} 호출")
            return func(*args, **kwargs)
        return wrapper

    def time_it(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            print(f"    [TIME] {func.__name__}: {elapsed:.6f}초")
            return result
        return wrapper

    @log_call       # 2. 로그 출력
    @time_it        # 1. 시간 측정
    def compute(n):
        return sum(i * i for i in range(n))

    print(f"\n  [@log_call + @time_it]")
    compute(100_000)
    print()


def lesson8_builtin_decorators():
    # =========================================================================
    #
    #   레슨 8 — 내장 데코레이터
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 8 : 내장 데코레이터            │")
    print("└──────────────────────────────────────┘")
    print()

    # ── @property — 속성처럼 접근하는 메서드 ──
    #
    # getter/setter를 깔끔하게 만드는 데코레이터
    # 비유: 은행 잔고 → 직접 바꾸면 안 되고, 입금/출금만 가능
    #
    class Circle:
        def __init__(self, radius):
            self._radius = radius

        @property
        def radius(self):
            """반지름 getter"""
            return self._radius

        @radius.setter
        def radius(self, value):
            """반지름 setter - 유효성 검사 포함!"""
            if value < 0:
                raise ValueError("반지름은 음수일 수 없습니다!")
            self._radius = value

        @property
        def area(self):
            """넓이 - 읽기 전용 속성!"""
            import math
            return math.pi * self._radius ** 2

    print("  [@property]")
    c = Circle(5)
    print(f"    c.radius = {c.radius}")       # getter
    print(f"    c.area   = {c.area:.2f}")      # 읽기 전용
    c.radius = 10                              # setter
    print(f"    c.radius = {c.radius} (변경 후)")
    try:
        c.radius = -1
    except ValueError as e:
        print(f"    c.radius = -1 → {e}")

    # ── @classmethod / @staticmethod ──
    #
    # @classmethod: 클래스 자체를 첫 인자(cls)로 받음
    #               → 팩토리 메서드, 대안 생성자에 사용
    #
    # @staticmethod: self도 cls도 안 받음
    #                → 클래스와 관련은 있지만 인스턴스/클래스 접근 불필요할 때
    #
    class Student:
        count = 0

        def __init__(self, name, score):
            self.name = name
            self.score = score
            Student.count += 1

        @classmethod
        def from_string(cls, data_string):
            """문자열에서 학생 생성 (대안 생성자)"""
            name, score = data_string.split(",")
            return cls(name.strip(), int(score.strip()))

        @classmethod
        def get_count(cls):
            """생성된 학생 수 반환"""
            return cls.count

        @staticmethod
        def is_passing(score):
            """합격 여부 판단 (인스턴스/클래스 접근 불필요)"""
            return score >= 60

    print(f"\n  [@classmethod / @staticmethod]")
    s1 = Student("민수", 95)
    s2 = Student.from_string("지유, 88")    # classmethod로 생성!
    print(f"    s2.name = {s2.name}, s2.score = {s2.score}")
    print(f"    학생 수: {Student.get_count()}")
    print(f"    85점 합격? {Student.is_passing(85)}")

    # ── @functools.lru_cache — 자동 캐싱 ──
    #
    # LRU = Least Recently Used (가장 안 쓴 것부터 삭제)
    # 같은 인자로 호출하면 캐시에서 즉시 반환!
    #
    @functools.lru_cache(maxsize=128)
    def fibonacci(n):
        if n < 2:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)

    print(f"\n  [@functools.lru_cache - 피보나치]")
    print(f"    fibonacci(30) = {fibonacci(30)}")
    print(f"    캐시 정보: {fibonacci.cache_info()}")

    # ── @dataclass (파이썬 3.7+) ──
    #
    # __init__, __repr__, __eq__ 등을 자동 생성!
    #
    from dataclasses import dataclass, field

    @dataclass
    class Point:
        x: float
        y: float

        def distance_to(self, other):
            return ((self.x - other.x)**2 + (self.y - other.y)**2) ** 0.5

    @dataclass
    class StudentRecord:
        name: str
        scores: list = field(default_factory=list)

        @property
        def average(self):
            return sum(self.scores) / len(self.scores) if self.scores else 0

    print(f"\n  [@dataclass]")
    p1, p2 = Point(0, 0), Point(3, 4)
    print(f"    p1 = {p1}")
    print(f"    p1 == Point(0,0)? {p1 == Point(0, 0)}")   # __eq__ 자동!
    print(f"    거리: {p1.distance_to(p2)}")

    sr = StudentRecord("민수", [95, 88, 92])
    print(f"    {sr}")
    print(f"    평균: {sr.average}")
    print()


def lesson9_lambda():
    # =========================================================================
    #
    #   레슨 9 — 람다(Lambda) 완전정복
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 9 : 람다(Lambda) 완전정복      │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 람다(Lambda)란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   람다 = 이름 없는 한 줄짜리 함수
    #
    #   문법: lambda 인자들: 표현식
    #
    #   비유: 일반 함수 = 요리 레시피 (이름 있고, 여러 단계)
    #         람다 = 즉석 소스 ("이거 섞으면 끝!" 한 줄짜리)
    #
    #   제약사항:
    #     - 표현식 하나만 가능 (if/for/while 등 문장 불가)
    #     - 여러 줄 불가
    #     - 반드시 값을 반환 (return 키워드 없이 자동 반환)
    #

    # ── 기본 문법 ──
    # lambda는 사실 def와 같은 것!
    #
    #   def add(a, b):     ←→   add = lambda a, b: a + b
    #       return a + b
    #
    square = lambda x: x ** 2
    add = lambda a, b: a + b
    print(f"  [기본] square(5) = {square(5)}")
    print(f"  [기본] add(3, 4) = {add(3, 4)}")

    # ── sorted()와 함께 (가장 많이 쓰이는 패턴!) ──
    students = [
        {"이름": "민수", "점수": 88},
        {"이름": "지유", "점수": 95},
        {"이름": "서연", "점수": 72},
        {"이름": "하준", "점수": 91},
    ]

    print(f"\n  [sorted + lambda]")
    by_score = sorted(students, key=lambda s: s["점수"])
    print(f"    점수 오름차순: {[s['이름'] for s in by_score]}")

    by_score_desc = sorted(students, key=lambda s: s["점수"], reverse=True)
    print(f"    점수 내림차순: {[s['이름'] for s in by_score_desc]}")

    by_name = sorted(students, key=lambda s: s["이름"])
    print(f"    이름 순: {[s['이름'] for s in by_name]}")

    # 다중 기준 정렬
    data = [("민수", 88), ("지유", 88), ("서연", 95), ("하준", 88)]
    by_multi = sorted(data, key=lambda x: (-x[1], x[0]))
    print(f"    다중 기준 (점수↓, 이름↑): {by_multi}")

    # ── map()과 함께 ──
    #
    # map(func, iterable) → 각 요소에 func 적용
    #
    print(f"\n  [map + lambda]")
    numbers = [1, 2, 3, 4, 5]
    squares = list(map(lambda x: x**2, numbers))
    print(f"    제곱: {squares}")

    # 비교: 리스트 컴프리헨션이 더 파이썬스러움!
    squares2 = [x**2 for x in numbers]
    print(f"    (컴프리헨션): {squares2}")    # 같은 결과, 더 읽기 쉬움!

    # ── filter()와 함께 ──
    #
    # filter(func, iterable) → func이 True인 요소만
    #
    print(f"\n  [filter + lambda]")
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    evens = list(filter(lambda x: x % 2 == 0, numbers))
    print(f"    짝수만: {evens}")

    # 비교: 컴프리헨션이 더 좋음!
    evens2 = [x for x in numbers if x % 2 == 0]
    print(f"    (컴프리헨션): {evens2}")

    # ── 언제 람다를 쓰고, 언제 안 쓰는지 ──
    #
    # ★ 쓰면 좋은 경우:
    #   - sorted(key=lambda x: x[1])   → 짧은 정렬 키
    #   - max(data, key=lambda x: x.score) → 짧은 비교 키
    #   - 콜백 함수가 한 줄일 때
    #
    # ★ 쓰면 안 되는 경우:
    #   - 복잡한 로직 → def 함수 사용!
    #   - 변수에 저장할 때 → def 함수 사용! (PEP 8 권장)
    #   - 디버깅이 필요할 때 → 람다는 이름이 없어서 디버깅 어려움
    #
    print(f"\n  [★ 람다 사용 가이드]")
    print(f"    ○ sorted(key=lambda ...) → 좋음!")
    print(f"    ○ max(data, key=lambda ...) → 좋음!")
    print(f"    X my_func = lambda x: ... → def 사용 권장!")
    print(f"    X 복잡한 로직 → def 사용!")

    # ── 조건부 표현식과 함께 ──
    grade = lambda score: "A" if score >= 90 else ("B" if score >= 80 else "C")
    print(f"\n  [조건부 람다]")
    print(f"    95점 → {grade(95)}")
    print(f"    85점 → {grade(85)}")
    print(f"    70점 → {grade(70)}")
    print()


def lesson10_web_router():
    # =========================================================================
    #
    #   레슨 10 — 실전: 웹 프레임워크 스타일 라우터
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 10 : 웹 스타일 라우터          │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 프로젝트: Flask/FastAPI 스타일 URL 라우터 만들기
    # ─────────────────────────────────────────────────────────────────────
    #
    #   실제 웹 프레임워크에서 이런 코드를 봤을 겁니다:
    #
    #     @app.route("/hello")
    #     def hello():
    #         return "Hello!"
    #
    #   이 @app.route가 바로 데코레이터입니다!
    #   직접 구현해봅시다!
    #

    class MiniRouter:
        """초소형 URL 라우터 - 데코레이터로 URL을 함수에 매핑"""

        def __init__(self):
            self.routes = {}      # {"/path": handler_func}
            self.middleware = []   # 미들웨어 리스트

        def route(self, path, methods=None):
            """URL 경로를 함수에 매핑하는 데코레이터"""
            if methods is None:
                methods = ["GET"]

            def decorator(func):
                self.routes[path] = {
                    "handler": func,
                    "methods": methods,
                }
                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    return func(*args, **kwargs)
                return wrapper
            return decorator

        def use(self, middleware_func):
            """미들웨어 추가"""
            self.middleware.append(middleware_func)

        def handle_request(self, method, path, **kwargs):
            """요청 처리 - 실제 웹 서버가 하는 일!"""
            # 미들웨어 실행
            request = {"method": method, "path": path, "params": kwargs}
            for mw in self.middleware:
                request = mw(request)
                if request is None:
                    return "미들웨어에서 차단됨"

            # 라우트 찾기
            if path not in self.routes:
                return f"404 Not Found: {path}"

            route_info = self.routes[path]

            # 메서드 확인
            if method not in route_info["methods"]:
                return f"405 Method Not Allowed: {method} {path}"

            # 핸들러 실행
            try:
                return route_info["handler"](**kwargs)
            except Exception as e:
                return f"500 Internal Server Error: {e}"

        def show_routes(self):
            """등록된 모든 라우트 출력"""
            print("    등록된 라우트:")
            for path, info in self.routes.items():
                methods = ", ".join(info["methods"])
                print(f"      [{methods}] {path} → {info['handler'].__name__}()")

    # ── 라우터 사용! ──
    app = MiniRouter()

    # 미들웨어: 로깅
    def logging_middleware(request):
        print(f"    [MW] {request['method']} {request['path']}")
        return request

    app.use(logging_middleware)

    # 라우트 등록 — 데코레이터 사용!
    @app.route("/")
    def index():
        return "환영합니다! 메인 페이지입니다."

    @app.route("/hello")
    def hello(name="세계"):
        return f"안녕하세요, {name}님!"

    @app.route("/add")
    def add(a=0, b=0):
        return f"{a} + {b} = {a + b}"

    @app.route("/users", methods=["GET", "POST"])
    def users(action="list"):
        if action == "list":
            return "사용자 목록: [민수, 지유, 서연]"
        return f"사용자 액션: {action}"

    @app.route("/secret", methods=["POST"])
    def secret():
        return "비밀 데이터입니다!"

    # ── 라우트 정보 출력 ──
    print("  [라우터 설정]")
    app.show_routes()

    # ── 요청 시뮬레이션 ──
    print(f"\n  [요청 시뮬레이션]")

    test_requests = [
        ("GET", "/", {}),
        ("GET", "/hello", {"name": "민수"}),
        ("GET", "/add", {"a": 10, "b": 20}),
        ("GET", "/users", {}),
        ("POST", "/users", {"action": "create"}),
        ("GET", "/secret", {}),          # 405! GET 안 됨
        ("GET", "/not-exist", {}),       # 404!
    ]

    for method, path, params in test_requests:
        response = app.handle_request(method, path, **params)
        print(f"    응답: {response}")
        print()

    print("  ★ 핵심: @app.route()는 인자가 있는 데코레이터입니다!")
    print("    Flask, FastAPI 등 실제 웹 프레임워크도 이 패턴을 사용합니다!")
    print()


def main():
    print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
    print("  파이썬 학습 09단계: 데코레이터와 람다")
    print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")

    lesson1_first_class_functions()
    lesson2_closures()
    lesson3_decorator_basics()
    lesson4_practical_decorators()
    lesson5_decorator_with_args()
    lesson6_class_decorators()
    lesson7_stacking_decorators()
    lesson8_builtin_decorators()
    lesson9_lambda()
    lesson10_web_router()

    print("\n  ★ 09단계 학습 완료!")
    print("  → 다음 단계: 10_modules_packages.py")


if __name__ == "__main__":
    main()
