# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   파이썬 학습 08단계: 이터레이터와 제너레이터
#   ─ 이터러블, 이터레이터, 제너레이터, yield, itertools ─
#
#   이터레이터는 "다음 것을 하나씩 꺼내주는 자판기"이고,
#   제너레이터는 "필요할 때만 만들어주는 똑똑한 공장"입니다.
#   대용량 데이터를 메모리 걱정 없이 처리하는 핵심 기술!
#
#   ■ 실행 방법: python 08_iterators_generators.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 이터러블 vs 이터레이터 - __iter__와 __next__, StopIteration
#   2. for문의 비밀 - for문이 내부적으로 어떻게 동작하는지
#   3. 커스텀 이터레이터 만들기 - 카운트다운, 피보나치
#   4. 제너레이터 함수 - yield의 마법, 실행 흐름 추적
#   5. 제너레이터 표현식 - () vs [], 메모리 비교
#   6. yield from - 서브 제너레이터 위임
#   7. 무한 시퀀스 - 끝없는 데이터 스트림
#   8. itertools 완전정복 - chain, product, combinations 등
#   9. 제너레이터로 파이프라인 만들기
#  10. 실전: 대용량 로그 파일 분석기
#
# ─────────────────────────────────────────────────────────────────────────

import sys
import itertools
import tempfile
import os
from collections import Counter


def lesson1_iterable_vs_iterator():
    # =========================================================================
    #
    #   레슨 1 — 이터러블 vs 이터레이터
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 이터러블 vs 이터레이터     │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 이터러블(Iterable)이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   이터러블 = "하나씩 꺼낼 수 있는 것"
    #
    #   비유: "줄 서 있는 사람들" — 한 명씩 차례로 나올 수 있음
    #
    #   이터러블인 것들:
    #     - 리스트 [1, 2, 3]
    #     - 튜플 (1, 2, 3)
    #     - 문자열 "hello"
    #     - 딕셔너리 {"a": 1}
    #     - 셋 {1, 2, 3}
    #     - range(10)
    #     - 파일 객체
    #
    #   이터러블이 아닌 것들:
    #     - 숫자 42
    #     - None
    #     - bool True/False
    #

    # ─────────────────────────────────────────────────────────────────────
    # ■ 이터레이터(Iterator)란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   이터레이터 = "현재 위치를 기억하면서 다음 값을 꺼내주는 기계"
    #
    #   비유: 자판기!
    #     - 버튼을 누르면(next()) 음료가 하나 나옴
    #     - 다 떨어지면 StopIteration 에러!
    #     - 한번 꺼낸 음료는 다시 넣을 수 없음 (되돌릴 수 없음!)
    #
    #   핵심 메서드:
    #     __iter__() → 자기 자신을 반환
    #     __next__() → 다음 값을 반환, 없으면 StopIteration 발생
    #

    # ── 이터러블 → 이터레이터 변환: iter() ──
    fruits = ["사과", "바나나", "포도"]       # 이터러블 (리스트)
    fruit_iter = iter(fruits)                   # 이터레이터로 변환!

    print("  이터러블 (리스트):")
    print(f"    type(fruits) = {type(fruits)}")
    print(f"    type(fruit_iter) = {type(fruit_iter)}")

    # ── next()로 하나씩 꺼내기 ──
    print(f"\n  next() 호출:")
    print(f"    1번째: {next(fruit_iter)}")     # 사과
    print(f"    2번째: {next(fruit_iter)}")     # 바나나
    print(f"    3번째: {next(fruit_iter)}")     # 포도

    # 더 이상 꺼낼 게 없으면?
    try:
        next(fruit_iter)
    except StopIteration:
        print("    4번째: StopIteration! 더 이상 없음!")

    # ── next()에 기본값 주기 ──
    #
    # next(iterator, default) → StopIteration 대신 default 반환
    #
    empty_iter = iter([])
    result = next(empty_iter, "비어있음!")
    print(f"\n  next(빈 이터레이터, 기본값): '{result}'")

    # ── 이터러블인지 확인하는 방법 ──
    from collections.abc import Iterable, Iterator
    print(f"\n  리스트는 이터러블? {isinstance([], Iterable)}")          # True
    print(f"  리스트는 이터레이터? {isinstance([], Iterator)}")          # False!
    print(f"  iter(리스트)는 이터레이터? {isinstance(iter([]), Iterator)}")  # True
    print(f"  숫자는 이터러블? {isinstance(42, Iterable)}")              # False

    # ── ★ 핵심 차이점 ──
    #
    #   이터러블: __iter__() 있음 → for문에 넣을 수 있음
    #   이터레이터: __iter__() + __next__() 있음 → 값을 하나씩 꺼낼 수 있음
    #
    #   이터러블 ────iter()───→ 이터레이터 ────next()───→ 값, 값, ... StopIteration
    #
    print()


def lesson2_for_loop_secret():
    # =========================================================================
    #
    #   레슨 2 — for문의 비밀: 내부 동작 원리
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : for문의 비밀               │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ for문은 사실 iter() + next()의 반복!
    # ─────────────────────────────────────────────────────────────────────
    #
    #   for item in [1, 2, 3]:
    #       print(item)
    #
    #   이 코드는 내부적으로 이렇게 동작합니다:
    #
    #   _iter = iter([1, 2, 3])      # 1단계: 이터레이터 생성
    #   while True:                    # 2단계: 무한 반복
    #       try:
    #           item = next(_iter)     # 3단계: 다음 값 꺼내기
    #       except StopIteration:      # 4단계: 끝나면 종료
    #           break
    #       print(item)                # 5단계: 본문 실행
    #

    colors = ["빨강", "파랑", "초록"]

    # ── 방법 1: 일반 for문 ──
    print("  [일반 for문]")
    for color in colors:
        print(f"    {color}")

    # ── 방법 2: for문이 실제로 하는 일 (직접 구현) ──
    print("\n  [for문의 실제 동작 - 직접 구현]")
    _iterator = iter(colors)
    while True:
        try:
            color = next(_iterator)
        except StopIteration:
            break
        print(f"    {color}")

    # ── 문자열도 이터러블! ──
    print("\n  [문자열도 이터러블]")
    word_iter = iter("파이썬")
    print(f"    {next(word_iter)}")    # 파
    print(f"    {next(word_iter)}")    # 이
    print(f"    {next(word_iter)}")    # 썬

    # ── 딕셔너리의 이터레이션 ──
    print("\n  [딕셔너리 이터레이션]")
    scores = {"민수": 95, "지유": 88}
    # for key in dict → 키만 나옴!
    d_iter = iter(scores)
    print(f"    첫 번째 키: {next(d_iter)}")
    print(f"    두 번째 키: {next(d_iter)}")

    # ── ★ 이터레이터는 1회용! ──
    #
    # 한번 다 꺼내면 끝! 다시 처음부터 꺼내려면 새 이터레이터 필요!
    #
    print("\n  [이터레이터는 1회용!]")
    nums = [1, 2, 3]
    nums_iter = iter(nums)
    print(f"    1회차: {list(nums_iter)}")     # [1, 2, 3]
    print(f"    2회차: {list(nums_iter)}")     # [] ← 비어있음!
    # 다시 하려면: nums_iter = iter(nums)
    print()


def lesson3_custom_iterator():
    # =========================================================================
    #
    #   레슨 3 — 커스텀 이터레이터 만들기
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : 커스텀 이터레이터          │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 이터레이터 직접 만들기
    # ─────────────────────────────────────────────────────────────────────
    #
    #   __iter__() → self 반환
    #   __next__() → 다음 값 반환, 끝나면 raise StopIteration
    #

    # ── 카운트다운 이터레이터 ──
    class Countdown:
        """N부터 1까지 카운트다운하는 이터레이터

        비유: 로켓 발사 전 카운트다운!
              "5... 4... 3... 2... 1... 발사!"
        """
        def __init__(self, start):
            self.current = start

        def __iter__(self):
            return self     # 이터레이터는 자기 자신을 반환!

        def __next__(self):
            if self.current <= 0:
                raise StopIteration    # 끝!
            value = self.current
            self.current -= 1
            return value

    print("  [카운트다운 이터레이터]")
    for num in Countdown(5):
        print(f"    {num}...")
    print("    발사!")

    # ── 피보나치 이터레이터 ──
    class Fibonacci:
        """피보나치 수열을 max_count개까지 생성하는 이터레이터

        비유: 토끼 번식!
              이번 달 토끼 수 = 지난달 + 지지난달
              1, 1, 2, 3, 5, 8, 13, 21, ...
        """
        def __init__(self, max_count):
            self.max_count = max_count
            self.count = 0
            self.a, self.b = 0, 1

        def __iter__(self):
            return self

        def __next__(self):
            if self.count >= self.max_count:
                raise StopIteration
            self.count += 1
            result = self.a
            self.a, self.b = self.b, self.a + self.b
            return result

    print("\n  [피보나치 이터레이터 - 처음 10개]")
    fib_list = list(Fibonacci(10))
    print(f"    {fib_list}")

    # ── 범위 이터레이터 (range 직접 구현) ──
    class MyRange:
        """range()를 직접 구현한 이터레이터"""
        def __init__(self, start, stop=None, step=1):
            if stop is None:
                self.start, self.stop = 0, start
            else:
                self.start, self.stop = start, stop
            self.step = step
            self.current = self.start

        def __iter__(self):
            # ★ 중요: 매번 새 이터레이터를 반환하면 재사용 가능!
            self.current = self.start
            return self

        def __next__(self):
            if (self.step > 0 and self.current >= self.stop) or \
               (self.step < 0 and self.current <= self.stop):
                raise StopIteration
            value = self.current
            self.current += self.step
            return value

    print("\n  [MyRange - range() 직접 구현]")
    print(f"    MyRange(5): {list(MyRange(5))}")
    print(f"    MyRange(2, 8): {list(MyRange(2, 8))}")
    print(f"    MyRange(10, 0, -2): {list(MyRange(10, 0, -2))}")
    print()


def lesson4_generator_functions():
    # =========================================================================
    #
    #   레슨 4 — 제너레이터 함수: yield의 마법
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : 제너레이터 함수            │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 제너레이터(Generator)란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   제너레이터 = yield를 사용하는 함수
    #
    #   일반 함수: return → 값을 반환하고 함수 끝!
    #   제너레이터: yield → 값을 반환하지만 함수는 일시 정지!
    #                        다음 next() 호출 때 이어서 실행!
    #
    #   비유: 일반 함수 = 라면 끓여서 한꺼번에 배달
    #         제너레이터 = 초밥 카운터에서 하나씩 만들어 줌
    #                      "하나 만들어 → 손님한테 → 기다림 → 또 만들어 → ..."
    #
    #   ★ yield가 있는 함수를 호출하면?
    #     → 함수가 실행되는 게 아니라, 제너레이터 객체가 반환됨!
    #     → next()를 호출해야 비로소 실행이 시작됨!
    #

    # ── 가장 간단한 제너레이터 ──
    def simple_gen():
        print("      [gen] 첫 번째 yield 전")
        yield "첫 번째"
        print("      [gen] 두 번째 yield 전")
        yield "두 번째"
        print("      [gen] 세 번째 yield 전")
        yield "세 번째"
        print("      [gen] 함수 끝")

    print("  [제너레이터 실행 흐름 추적]")
    gen = simple_gen()
    print(f"    type(gen) = {type(gen)}")     # <class 'generator'>

    # next()를 호출해야 실행됨!
    print(f"\n    next(gen) = {next(gen)}")    # "첫 번째" - 여기서 멈춤!
    print(f"    next(gen) = {next(gen)}")      # "두 번째" - 여기서 멈춤!
    print(f"    next(gen) = {next(gen)}")      # "세 번째" - 여기서 멈춤!

    # ── return vs yield 비교 ──
    def with_return():
        """return은 값을 반환하고 함수 종료"""
        return [1, 2, 3]    # 리스트를 통째로 만들어서 반환

    def with_yield():
        """yield는 하나씩 반환하고 일시 정지"""
        yield 1    # 여기서 멈춤
        yield 2    # next() 호출하면 여기서 멈춤
        yield 3    # next() 호출하면 여기서 멈춤

    print(f"\n  return 결과: {with_return()}")           # [1, 2, 3]
    print(f"  yield 결과: {list(with_yield())}")         # [1, 2, 3] (같은 결과!)

    # ── 제너레이터 카운트다운 (클래스 없이!) ──
    #
    # 아까 레슨 3에서 클래스로 만든 카운트다운을 제너레이터로 만들면?
    # → 훨씬 간결함! __iter__, __next__, StopIteration 다 자동!
    #
    def countdown(n):
        while n > 0:
            yield n
            n -= 1

    print(f"\n  [제너레이터 카운트다운] {list(countdown(5))}")

    # ── 제너레이터 피보나치 ──
    def fibonacci(max_count):
        a, b = 0, 1
        for _ in range(max_count):
            yield a
            a, b = b, a + b

    print(f"  [제너레이터 피보나치] {list(fibonacci(10))}")

    # ── 제너레이터에 return 값 ──
    #
    # 제너레이터 안에서 return을 쓰면 StopIteration의 value가 됨
    # (잘 안 쓰이지만 알아두면 좋음)
    #
    def gen_with_return():
        yield 1
        yield 2
        return "끝!"    # StopIteration에 "끝!" 값이 담김

    g = gen_with_return()
    next(g)   # 1
    next(g)   # 2
    try:
        next(g)
    except StopIteration as e:
        print(f"\n  [return 값] StopIteration.value = '{e.value}'")
    print()


def lesson5_generator_expressions():
    # =========================================================================
    #
    #   레슨 5 — 제너레이터 표현식
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 제너레이터 표현식          │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 리스트 컴프리헨션 vs 제너레이터 표현식
    # ─────────────────────────────────────────────────────────────────────
    #
    #   리스트 컴프리헨션:  [x**2 for x in range(10)]   ← 대괄호 []
    #   제너레이터 표현식:  (x**2 for x in range(10))   ← 소괄호 ()
    #
    #   차이:
    #     리스트 컴프리헨션 → 모든 값을 한꺼번에 메모리에 생성
    #     제너레이터 표현식 → 필요할 때 하나씩 생성 (게으름!)
    #
    #   비유:
    #     리스트 = 냉장고에 반찬 100가지를 미리 다 만들어 놓기
    #     제너레이터 = 반찬이 필요할 때마다 하나씩 만들기
    #

    # ── 기본 비교 ──
    list_comp = [x**2 for x in range(10)]     # 리스트 (즉시 생성)
    gen_expr = (x**2 for x in range(10))      # 제너레이터 (게으른 생성)

    print(f"  리스트 컴프리헨션: {list_comp}")
    print(f"  제너레이터 표현식: {gen_expr}")     # <generator object ...>
    print(f"  제너레이터 → 리스트: {list(gen_expr)}")

    # ── 메모리 비교 ──
    #
    # ★ 핵심: 대용량 데이터에서 메모리 차이가 어마어마함!
    #
    list_size = sys.getsizeof([x for x in range(10000)])
    gen_size = sys.getsizeof(x for x in range(10000))
    print(f"\n  [메모리 비교 - 10,000개]")
    print(f"    리스트: {list_size:,} bytes")
    print(f"    제너레이터: {gen_size:,} bytes")    # 훨씬 작음!
    print(f"    차이: {list_size - gen_size:,} bytes 절약!")

    # ── 제너레이터 표현식을 함수 인자로 바로 사용 ──
    #
    # sum(), min(), max(), any(), all() 등에 바로 넣기 가능!
    # 이때 소괄호를 하나 생략 가능
    #
    print(f"\n  [함수 인자로 바로 사용]")
    total = sum(x**2 for x in range(1, 11))   # 소괄호 하나로 OK!
    print(f"    1~10 제곱의 합: {total}")

    max_val = max(len(word) for word in ["파이썬", "자바", "C"])
    print(f"    가장 긴 단어 길이: {max_val}")

    has_negative = any(x < 0 for x in [1, -2, 3, 4])
    print(f"    음수가 있는가? {has_negative}")

    all_positive = all(x > 0 for x in [1, 2, 3, 4])
    print(f"    모두 양수인가? {all_positive}")

    # ── 중첩 제너레이터 표현식 ──
    matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    flat = list(x for row in matrix for x in row)    # 행렬 평탄화
    print(f"\n  [행렬 평탄화] {matrix} → {flat}")

    # ── 조건부 제너레이터 표현식 ──
    even_squares = list(x**2 for x in range(20) if x % 2 == 0)
    print(f"  [조건부] 0~19 짝수의 제곱: {even_squares}")
    print()


def lesson6_yield_from():
    # =========================================================================
    #
    #   레슨 6 — yield from: 서브 제너레이터 위임
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : yield from                 │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ yield from이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   yield from 이터러블
    #   = "이 이터러블의 값들을 하나씩 yield 해줘!"
    #
    #   비유: 학교 반장이 선생님에게 보고하는 것
    #         반장: "1반 학생 이름 불러주세요" → yield from 1반
    #               "2반 학생 이름 불러주세요" → yield from 2반
    #

    # ── yield from 없이 (노가다 방식) ──
    def chain_manual(*iterables):
        for iterable in iterables:
            for item in iterable:     # 이중 for문 필요!
                yield item

    # ── yield from 사용 (깔끔!) ──
    def chain_elegant(*iterables):
        for iterable in iterables:
            yield from iterable       # 한 줄로 끝!

    list1 = [1, 2, 3]
    list2 = ["a", "b"]
    list3 = [True, False]

    print("  [yield from 없이]")
    print(f"    {list(chain_manual(list1, list2, list3))}")

    print("  [yield from 사용]")
    print(f"    {list(chain_elegant(list1, list2, list3))}")

    # ── 중첩 구조 평탄화 ──
    def flatten(nested):
        """다중 중첩 리스트를 1차원으로 평탄화"""
        for item in nested:
            if isinstance(item, (list, tuple)):
                yield from flatten(item)    # 재귀적으로 위임!
            else:
                yield item

    nested = [1, [2, 3, [4, 5]], [6, [7, [8, 9]]]]
    print(f"\n  [중첩 평탄화]")
    print(f"    원본: {nested}")
    print(f"    결과: {list(flatten(nested))}")

    # ── 트리 순회 예제 ──
    def tree_values(tree):
        """트리(딕셔너리) 구조에서 모든 값 추출"""
        if isinstance(tree, dict):
            for value in tree.values():
                yield from tree_values(value)
        elif isinstance(tree, (list, tuple)):
            for item in tree:
                yield from tree_values(item)
        else:
            yield tree

    org_chart = {
        "CEO": {
            "CTO": {"개발팀": ["민수", "지유"], "QA팀": ["서연"]},
            "CFO": {"재무팀": ["하준", "예린"]},
        }
    }
    print(f"\n  [트리 순회 - 조직도의 모든 사람]")
    print(f"    {list(tree_values(org_chart))}")
    print()


def lesson7_infinite_sequences():
    # =========================================================================
    #
    #   레슨 7 — 무한 시퀀스: 끝없는 데이터 스트림
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 무한 시퀀스               │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 무한 시퀀스란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   제너레이터는 끝없이 값을 생성할 수 있음!
    #   (필요한 만큼만 꺼내면 됨)
    #
    #   비유: 수도꼭지 — 물이 끝없이 나옴, 필요한 만큼만 받으면 됨
    #
    #   ★ 주의: 무한 제너레이터를 list()로 감싸면? → 메모리 폭발!
    #           반드시 islice, takewhile 등으로 제한해서 사용!
    #

    # ── 직접 만드는 무한 시퀀스들 ──
    def naturals(start=1):
        """자연수 무한 생성"""
        n = start
        while True:
            yield n
            n += 1

    def cycle_gen(items):
        """항목들을 무한 반복"""
        while True:
            yield from items

    def repeat_gen(value, times=None):
        """같은 값을 무한(또는 n번) 반복"""
        if times is None:
            while True:
                yield value
        else:
            for _ in range(times):
                yield value

    # ── 무한 시퀀스 사용하기 (islice로 제한!) ──
    print("  [자연수 - 처음 10개]")
    first_10 = list(itertools.islice(naturals(), 10))
    print(f"    {first_10}")

    print("\n  [무한 순환 - 계절]")
    seasons = list(itertools.islice(cycle_gen(["봄", "여름", "가을", "겨울"]), 8))
    print(f"    {seasons}")

    print("\n  [무한 반복 - 'hello' 5번]")
    hellos = list(itertools.islice(repeat_gen("hello"), 5))
    print(f"    {hellos}")

    # ── itertools의 무한 시퀀스 도구들 ──
    print("\n  [itertools 무한 시퀀스]")

    # count(start, step) — 무한 카운터
    counter = list(itertools.islice(itertools.count(10, 3), 5))
    print(f"    count(10, 3): {counter}")       # [10, 13, 16, 19, 22]

    # cycle(iterable) — 무한 반복
    abc = list(itertools.islice(itertools.cycle("ABC"), 7))
    print(f"    cycle('ABC'): {abc}")           # [A,B,C,A,B,C,A]

    # repeat(value, times) — 반복
    print(f"    repeat(0, 5): {list(itertools.repeat(0, 5))}")

    # ── 무한 시퀀스 실전 예: ID 생성기 ──
    def id_generator(prefix="ID"):
        """고유 ID 무한 생성"""
        for n in itertools.count(1):
            yield f"{prefix}-{n:04d}"

    print("\n  [ID 생성기]")
    ids = list(itertools.islice(id_generator("STU"), 5))
    print(f"    {ids}")
    print()


def lesson8_itertools_mastery():
    # =========================================================================
    #
    #   레슨 8 — itertools 완전정복
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 8 : itertools 완전정복         │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ itertools = 이터레이터의 보물 상자
    # ─────────────────────────────────────────────────────────────────────
    #
    #   파이썬 표준 라이브러리에서 제공하는 강력한 이터레이터 도구 모음!
    #   메모리 효율적이고, C로 구현되어 빠름!
    #

    # ── chain: 여러 이터러블을 하나로 연결 ──
    print("  [chain - 이터러블 연결]")
    result = list(itertools.chain([1, 2], [3, 4], [5]))
    print(f"    chain([1,2], [3,4], [5]) = {result}")

    # chain.from_iterable: 이터러블의 이터러블을 평탄화
    nested = [[1, 2], [3, 4], [5, 6]]
    flat = list(itertools.chain.from_iterable(nested))
    print(f"    chain.from_iterable({nested}) = {flat}")

    # ── islice: 이터레이터에서 슬라이싱 ──
    print(f"\n  [islice - 이터레이터 슬라이싱]")
    # islice(iterable, stop) 또는 islice(iterable, start, stop, step)
    print(f"    islice(range(100), 5) = {list(itertools.islice(range(100), 5))}")
    print(f"    islice(range(100), 2, 8, 2) = {list(itertools.islice(range(100), 2, 8, 2))}")

    # ── takewhile / dropwhile ──
    print(f"\n  [takewhile - 조건이 참인 동안만]")
    data = [1, 3, 5, 7, 2, 4, 6]
    taken = list(itertools.takewhile(lambda x: x < 6, data))
    print(f"    takewhile(x<6, {data}) = {taken}")     # [1, 3, 5]

    dropped = list(itertools.dropwhile(lambda x: x < 6, data))
    print(f"    dropwhile(x<6, {data}) = {dropped}")   # [7, 2, 4, 6]

    # ── product: 데카르트 곱 (모든 조합) ──
    print(f"\n  [product - 데카르트 곱]")
    colors = ["빨", "파"]
    sizes = ["S", "M"]
    combos = list(itertools.product(colors, sizes))
    print(f"    product({colors}, {sizes}) = {combos}")

    # 주사위 두 개 던지기
    dice = list(itertools.product(range(1, 7), repeat=2))
    print(f"    주사위 2개 조합 수: {len(dice)}가지")

    # ── combinations: 조합 (순서 무관) ──
    print(f"\n  [combinations - 조합]")
    students = ["민수", "지유", "서연", "하준"]
    pairs = list(itertools.combinations(students, 2))
    print(f"    4명 중 2명 조합: {pairs}")
    print(f"    조합 수: {len(pairs)}가지")

    # ── permutations: 순열 (순서 유관) ──
    print(f"\n  [permutations - 순열]")
    perms = list(itertools.permutations(["A", "B", "C"], 2))
    print(f"    ABC 중 2개 순열: {perms}")
    print(f"    순열 수: {len(perms)}가지")

    # ── groupby: 연속 그룹핑 ──
    #
    # ★ 주의: groupby는 정렬된 데이터에서만 제대로 동작!
    #         연속으로 같은 키를 가진 것들만 그룹핑!
    #
    print(f"\n  [groupby - 연속 그룹핑]")
    scores = [("A", 90), ("A", 85), ("B", 70), ("B", 75), ("A", 95)]
    # 먼저 정렬!
    scores_sorted = sorted(scores, key=lambda x: x[0])
    for grade, group in itertools.groupby(scores_sorted, key=lambda x: x[0]):
        items = list(group)
        print(f"    {grade}등급: {items}")

    # ── accumulate: 누적 연산 ──
    print(f"\n  [accumulate - 누적 합]")
    nums = [1, 2, 3, 4, 5]
    cumsum = list(itertools.accumulate(nums))
    print(f"    누적합: {nums} → {cumsum}")

    import operator
    cumprod = list(itertools.accumulate(nums, operator.mul))
    print(f"    누적곱: {nums} → {cumprod}")

    # ── starmap: 튜플 인자 풀어서 함수 적용 ──
    print(f"\n  [starmap - 튜플 인자 풀기]")
    pairs_data = [(2, 3), (4, 5), (6, 7)]
    products = list(itertools.starmap(lambda a, b: a * b, pairs_data))
    print(f"    starmap(곱, {pairs_data}) = {products}")

    # ── zip_longest: 길이 다른 이터러블 묶기 ──
    print(f"\n  [zip_longest - 길이 맞추기]")
    names = ["민수", "지유", "서연"]
    scores_list = [95, 88]
    result = list(itertools.zip_longest(names, scores_list, fillvalue=0))
    print(f"    zip_longest({names}, {scores_list}) = {result}")
    print()


def lesson9_generator_pipeline():
    # =========================================================================
    #
    #   레슨 9 — 제너레이터로 파이프라인 만들기
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 9 : 제너레이터 파이프라인      │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 파이프라인이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   파이프라인 = 데이터를 단계별로 처리하는 연결 구조
    #
    #   비유: 공장 컨베이어 벨트!
    #     원재료 → [세척] → [절단] → [가열] → [포장] → 완제품
    #
    #   제너레이터 파이프라인:
    #     데이터 → gen1() → gen2() → gen3() → 결과
    #
    #   ★ 장점:
    #     - 메모리 효율적: 한 번에 하나씩만 처리 (대용량 OK!)
    #     - 모듈화: 각 단계를 독립적으로 교체 가능
    #     - 게으른 평가: 필요할 때만 계산
    #

    # ── 파이프라인 구성 요소들 ──

    def read_lines(text):
        """텍스트를 줄 단위로 생성"""
        for line in text.strip().split("\n"):
            yield line

    def filter_comments(lines):
        """주석(#)과 빈 줄 제거"""
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                yield stripped

    def parse_records(lines):
        """'이름,점수' 형태를 파싱"""
        for line in lines:
            try:
                name, score = line.split(",")
                yield {"이름": name.strip(), "점수": int(score.strip())}
            except (ValueError, IndexError):
                pass    # 파싱 실패한 줄은 건너뜀

    def filter_passing(records, threshold=60):
        """합격 점수 이상만 필터링"""
        for record in records:
            if record["점수"] >= threshold:
                yield record

    def add_grade(records):
        """등급 추가"""
        for record in records:
            score = record["점수"]
            if score >= 90:
                record["등급"] = "A"
            elif score >= 80:
                record["등급"] = "B"
            elif score >= 70:
                record["등급"] = "C"
            else:
                record["등급"] = "D"
            yield record

    # ── 파이프라인 실행! ──
    raw_data = """
    # 학생 성적표
    # 이름, 점수
    민수, 95
    지유, 88
    서연, 45
    하준, 72
    잘못된데이터
    예린, 100
    # 여기까지
    """

    print("  [파이프라인 실행]")
    print("  데이터 → 줄분리 → 주석제거 → 파싱 → 합격필터 → 등급추가")
    print()

    # 파이프라인 연결! (중간에 아무것도 저장하지 않음!)
    pipeline = add_grade(
        filter_passing(
            parse_records(
                filter_comments(
                    read_lines(raw_data)
                )
            ),
            threshold=60
        )
    )

    # 결과 소비
    for student in pipeline:
        print(f"    {student['이름']}: {student['점수']}점 ({student['등급']})")

    # ── 파이프라인의 메모리 효율성 ──
    #
    # 리스트 방식:
    #   lines = text.split("\n")        # 전체를 메모리에
    #   filtered = [l for l in lines]   # 또 전체를 메모리에
    #   parsed = [parse(l) for l in filtered]  # 또 전체를 메모리에
    #   → 3배의 메모리 사용!
    #
    # 제너레이터 방식:
    #   각 단계에서 한 줄만 메모리에 있음!
    #   1GB 파일이든 100GB 파일이든 메모리 사용량 거의 동일!
    #
    print(f"\n  ★ 핵심: 제너레이터 파이프라인은 데이터 크기에 상관없이")
    print(f"          메모리를 거의 사용하지 않습니다!")
    print()


def lesson10_log_analyzer():
    # =========================================================================
    #
    #   레슨 10 — 실전: 대용량 로그 파일 분석기
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 10 : 로그 파일 분석기          │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 프로젝트: 웹 서버 로그를 제너레이터로 분석
    # ─────────────────────────────────────────────────────────────────────
    #
    #   실제 서버 로그는 수 GB ~ 수 TB!
    #   전부 메모리에 올릴 수 없으므로 제너레이터가 필수!
    #

    # ── 테스트용 로그 파일 생성 ──
    with tempfile.TemporaryDirectory() as tmp:
        log_path = os.path.join(tmp, "access.log")

        sample_logs = [
            '2024-03-01 10:00:01 INFO GET /index.html 200 1234',
            '2024-03-01 10:00:02 INFO GET /about.html 200 5678',
            '2024-03-01 10:00:03 ERROR GET /missing.html 404 0',
            '2024-03-01 10:00:04 INFO POST /login 200 890',
            '2024-03-01 10:00:05 WARNING GET /slow-page.html 200 15000',
            '2024-03-01 10:00:06 ERROR POST /api/data 500 0',
            '2024-03-01 10:00:07 INFO GET /index.html 200 2345',
            '2024-03-01 10:00:08 INFO GET /products.html 200 6789',
            '2024-03-01 10:00:09 ERROR GET /secret.html 403 0',
            '2024-03-01 10:00:10 INFO GET /index.html 200 3456',
            '2024-03-01 10:00:11 INFO GET /about.html 200 4567',
            '2024-03-01 10:00:12 ERROR GET /broken.html 404 0',
            '2024-03-01 10:00:13 INFO POST /api/submit 201 1000',
            '2024-03-01 10:00:14 WARNING GET /heavy-page.html 200 20000',
            '2024-03-01 10:00:15 INFO GET /contact.html 200 3000',
        ]

        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(sample_logs))

        # ── 제너레이터 파이프라인 구성 ──

        def read_log_lines(filepath):
            """파일에서 한 줄씩 읽기 (메모리 절약!)"""
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    yield line.strip()

        def parse_log(lines):
            """로그 줄을 구조화된 딕셔너리로 파싱"""
            for line in lines:
                parts = line.split()
                if len(parts) >= 6:
                    yield {
                        "날짜": parts[0],
                        "시간": parts[1],
                        "레벨": parts[2],
                        "메서드": parts[3],
                        "경로": parts[4],
                        "상태코드": int(parts[5]),
                        "크기": int(parts[6]) if len(parts) > 6 else 0,
                    }

        def filter_by_level(entries, level):
            """특정 로그 레벨만 필터링"""
            for entry in entries:
                if entry["레벨"] == level:
                    yield entry

        def filter_by_status(entries, status_code):
            """특정 상태 코드만 필터링"""
            for entry in entries:
                if entry["상태코드"] == status_code:
                    yield entry

        # ── 분석 1: 에러 로그 찾기 ──
        print("  [1] 에러 로그:")
        error_pipeline = filter_by_level(
            parse_log(read_log_lines(log_path)),
            "ERROR"
        )
        for entry in error_pipeline:
            print(f"    {entry['시간']} {entry['메서드']} {entry['경로']} → {entry['상태코드']}")

        # ── 분석 2: 404 에러 찾기 ──
        print("\n  [2] 404 Not Found 에러:")
        not_found = filter_by_status(
            parse_log(read_log_lines(log_path)),
            404
        )
        for entry in not_found:
            print(f"    {entry['경로']} (404)")

        # ── 분석 3: 가장 많이 방문한 페이지 ──
        print("\n  [3] 페이지별 방문 횟수:")
        page_counts = Counter(
            entry["경로"]
            for entry in parse_log(read_log_lines(log_path))
        )
        for page, count in page_counts.most_common(5):
            bar = "#" * count
            print(f"    {page:25s} {count}회 {bar}")

        # ── 분석 4: 로그 레벨별 통계 ──
        print("\n  [4] 로그 레벨별 통계:")
        level_counts = Counter(
            entry["레벨"]
            for entry in parse_log(read_log_lines(log_path))
        )
        for level, count in level_counts.most_common():
            print(f"    {level:10s} {count}건")

        # ── 분석 5: 전체 요약 ──
        print("\n  [5] 전체 요약:")
        entries = list(parse_log(read_log_lines(log_path)))
        total = len(entries)
        errors = sum(1 for e in entries if e["레벨"] == "ERROR")
        total_size = sum(e["크기"] for e in entries)
        print(f"    총 요청 수: {total}건")
        print(f"    에러 수: {errors}건 ({errors/total*100:.1f}%)")
        print(f"    총 전송량: {total_size:,} bytes")

    print(f"\n  ★ 핵심: 이 분석기는 수 GB 로그 파일도 처리 가능!")
    print(f"    → 제너레이터가 한 줄씩 처리하므로 메모리 걱정 없음!")
    print()


def main():
    print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
    print("  파이썬 학습 08단계: 이터레이터와 제너레이터")
    print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")

    lesson1_iterable_vs_iterator()
    lesson2_for_loop_secret()
    lesson3_custom_iterator()
    lesson4_generator_functions()
    lesson5_generator_expressions()
    lesson6_yield_from()
    lesson7_infinite_sequences()
    lesson8_itertools_mastery()
    lesson9_generator_pipeline()
    lesson10_log_analyzer()

    print("\n  ★ 08단계 학습 완료!")
    print("  → 다음 단계: 09_decorators_lambda.py")


if __name__ == "__main__":
    main()
