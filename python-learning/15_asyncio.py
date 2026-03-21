# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   파이썬 학습 15단계: asyncio (비동기 프로그래밍)
#   ─ 코루틴, 이벤트 루프, 동시 실행, 큐, 타임아웃 ─
#   ■ 실행 방법: python 15_asyncio.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 동기 vs 비동기 — 카페 주문 비유, 블로킹/논블로킹
#   2. 코루틴(Coroutine) 기초 — async def, await, 코루틴 객체 vs 함수
#   3. asyncio.run과 이벤트 루프 — 이벤트 루프가 뭔지, run()
#   4. 동시 실행 — asyncio.gather(), asyncio.create_task()
#   5. asyncio.wait와 as_completed — 먼저 끝나는 것부터 처리
#   6. 비동기 이터레이터/제너레이터 — async for, __aiter__/__anext__
#   7. asyncio.Queue — 생산자-소비자 패턴
#   8. 동기 코드와 혼합 — run_in_executor, 쓰레드풀
#   9. 에러 처리와 타임아웃 — asyncio.wait_for(), 예외 전파, 취소
#  10. 실전: 비동기 웹 크롤러 시뮬레이션
#
# ─────────────────────────────────────────────────────────────────────────

import asyncio
import time
import random
from concurrent.futures import ThreadPoolExecutor


# ─────────────────────────────────────────────────────────────────────────
# ■ 공통 헬퍼 함수
# ─────────────────────────────────────────────────────────────────────────

def print_lesson(title: str) -> None:
    """레슨 제목을 눈에 띄게 출력한다."""
    print()
    print("┌──────────────────────────────────────┐")
    print(f"│  {title:<36s} │")
    print("└──────────────────────────────────────┘")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨에서 사용할 비동기 유틸 함수들
# ─────────────────────────────────────────────────────────────────────────

async def make_coffee(name: str, seconds: float) -> str:
    """커피를 내리는 작업을 시뮬레이션한다. (비동기)"""
    await asyncio.sleep(seconds)
    return f"{name} 커피 완성 ({seconds}초 소요)"


def heavy_cpu_work(n: int) -> int:
    """CPU를 점유하는 동기 작업을 시뮬레이션한다."""
    # time.sleep은 실제로 쓰레드를 블로킹한다
    time.sleep(0.05)
    return sum(range(n))


# =========================================================================
#
#   레슨 1 — 동기 vs 비동기: 카페 주문 비유
#
# =========================================================================

async def lesson1_sync_vs_async():
    print_lesson("레슨 1 : 동기 vs 비동기")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 동기(Synchronous)란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   한 가지 일이 끝나야 다음 일을 시작하는 방식
    #
    #   비유: 카페에서 커피를 한 잔 주문하고,
    #         그 커피가 나올 때까지 카운터 앞에서 서서 기다린 다음,
    #         커피를 받고 나서야 다음 주문을 할 수 있는 것
    #
    #   [주문1] ──▶ [대기] ──▶ [완료] ──▶ [주문2] ──▶ [대기] ──▶ [완료]
    #   총 시간: 주문1 시간 + 주문2 시간  (합산)
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 동기 방식: 순서대로 하나씩 기다리기")
    print("  ─────────────────────────────────────")

    start = time.perf_counter()

    # await를 하나씩 호출 → 순차 실행 (동기처럼 동작)
    result1 = await make_coffee("아메리카노", 0.1)
    result2 = await make_coffee("카페라떼",   0.1)
    result3 = await make_coffee("에스프레소", 0.1)

    elapsed = time.perf_counter() - start
    print(f"  결과: {result1}")
    print(f"  결과: {result2}")
    print(f"  결과: {result3}")
    print(f"  → 순차 실행 시간: {elapsed:.3f}초 (약 0.3초 - 합산)")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 비동기(Asynchronous)란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   기다리는 동안 다른 일을 먼저 처리하는 방식
    #
    #   비유: 카페에서 커피 3잔을 한꺼번에 주문하고,
    #         바리스타가 동시에 3잔을 내리는 동안 자리에 앉아 기다리는 것
    #
    #   [주문1] ──▶ ┐
    #   [주문2] ──▶ ├──▶ [동시 대기] ──▶ [모두 완료]
    #   [주문3] ──▶ ┘
    #   총 시간: 가장 오래 걸리는 주문 1개 시간
    #
    # ─────────────────────────────────────────────────────────────────────

    print()
    print("  ■ 비동기 방식: 동시에 기다리기")
    print("  ─────────────────────────────────────")

    start = time.perf_counter()

    # gather로 동시 실행 → 비동기
    results = await asyncio.gather(
        make_coffee("아메리카노", 0.1),
        make_coffee("카페라떼",   0.1),
        make_coffee("에스프레소", 0.1),
    )

    elapsed = time.perf_counter() - start
    for r in results:
        print(f"  결과: {r}")
    print(f"  → 동시 실행 시간: {elapsed:.3f}초 (약 0.1초 - 가장 긴 것 하나)")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 블로킹 vs 논블로킹
    # ─────────────────────────────────────────────────────────────────────
    #
    #   블로킹(Blocking):
    #     코드가 어떤 작업이 끝날 때까지 멈추는 것
    #     예) time.sleep(3) → 3초 동안 아무것도 못 함
    #     예) input()       → 사용자가 입력할 때까지 멈춤
    #
    #   논블로킹(Non-blocking):
    #     작업을 요청하고 바로 다음 코드로 넘어가는 것
    #     예) await asyncio.sleep(3) → 3초 기다리는 동안 다른 코루틴 실행
    #
    #   ★ 핵심: asyncio에서 time.sleep()을 쓰면 안 되는 이유!
    #     time.sleep()은 이벤트 루프 자체를 멈춰버린다.
    #     asyncio.sleep()은 이벤트 루프에게 "나 잠깐 쉴게, 다른 거 해"라고 한다.
    #
    # ─────────────────────────────────────────────────────────────────────

    print()
    print("  ■ 왜 비동기가 필요한가?")
    print("  ─────────────────────────────────────")
    print("  - 네트워크 요청 (웹 API 호출, DB 쿼리)")
    print("  - 파일 I/O (대용량 파일 읽기/쓰기)")
    print("  - 여러 사용자 동시 처리 (웹 서버)")
    print("  → 기다리는 시간이 긴 작업에 비동기가 유리!")
    print()


# =========================================================================
#
#   레슨 2 — 코루틴(Coroutine) 기초
#
# =========================================================================

async def lesson2_coroutine_basics():
    print_lesson("레슨 2 : 코루틴 기초")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 코루틴이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   코루틴 = "중간에 멈출 수 있는 함수"
    #
    #   일반 함수:  호출 → 처음부터 끝까지 실행 → 반환
    #   코루틴:     호출 → 실행 → await에서 멈춤 → 다시 실행 → 반환
    #
    #   비유: 일반 함수는 "처음부터 끝까지 읽어야 하는 책"
    #         코루틴은 "북마크를 끼워두고 나중에 이어 읽을 수 있는 책"
    #
    #   async def 로 정의하면 코루틴 함수가 된다.
    #   await 로 코루틴 안에서 다른 비동기 작업을 기다릴 수 있다.
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ async def 로 코루틴 함수 정의
    async def greet(name: str) -> str:
        await asyncio.sleep(0.01)  # 비동기로 잠깐 대기
        return f"안녕하세요, {name}님!"

    # ■ 코루틴 함수를 호출하면? → 코루틴 "객체"가 나온다! (바로 실행 X)
    coro_object = greet("민수")
    print(f"  코루틴 객체: {coro_object}")
    print(f"  타입: {type(coro_object)}")

    # ■ await를 써야 실제로 실행된다
    result = await coro_object
    print(f"  await 결과: {result}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 코루틴 객체 vs 코루틴 함수
    # ─────────────────────────────────────────────────────────────────────
    #
    #   async def greet():  ← 이것은 "코루틴 함수" (설계도)
    #       ...
    #
    #   greet()             ← 이것은 "코루틴 객체" (설계도로 만든 제품)
    #                         await 하지 않으면 실행되지 않음!
    #
    #   await greet()       ← 이것이 실제 실행!
    #
    #   ★ 흔한 실수: await를 빠뜨리면 코루틴이 실행되지 않고 경고 발생
    #     result = greet("민수")     ← 실행 안 됨! 코루틴 객체만 생성
    #     result = await greet("민수") ← 올바른 사용법
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ 여러 await를 순서대로 사용하기
    async def cook_meal():
        print("  1. 재료 손질 중...")
        await asyncio.sleep(0.01)
        print("  2. 끓이는 중...")
        await asyncio.sleep(0.01)
        print("  3. 완성!")
        return "된장찌개"

    meal = await cook_meal()
    print(f"  결과: {meal}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 코루틴 체이닝 (코루틴이 다른 코루틴을 호출)
    # ─────────────────────────────────────────────────────────────────────

    async def boil_water():
        await asyncio.sleep(0.01)
        return "뜨거운 물"

    async def brew_tea():
        water = await boil_water()       # 다른 코루틴을 await
        return f"{water}로 차 우리기 완료"

    tea = await brew_tea()
    print(f"  코루틴 체이닝 결과: {tea}")
    print()


# =========================================================================
#
#   레슨 3 — asyncio.run과 이벤트 루프
#
# =========================================================================

async def lesson3_event_loop():
    print_lesson("레슨 3 : 이벤트 루프")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 이벤트 루프(Event Loop)란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   이벤트 루프 = "코루틴들의 교통 정리사"
    #
    #   비유: 놀이공원의 운영 관리자
    #     - 여러 놀이기구(코루틴)가 동시에 돌아가고 있다
    #     - 관리자(이벤트 루프)가 어떤 기구가 멈췄고,
    #       어떤 기구가 다시 돌아야 하는지 관리한다
    #     - 기구가 "잠깐 멈춤"(await)이라고 하면
    #       관리자는 다른 기구를 먼저 돌린다
    #
    #   동작 방식:
    #     1. 실행할 코루틴들을 큐에 넣는다
    #     2. 하나를 꺼내서 실행한다
    #     3. await를 만나면 → 해당 코루틴을 대기 상태로 바꾸고
    #        → 다른 코루틴을 실행한다
    #     4. 대기 중인 작업이 완료되면 → 다시 큐에 넣는다
    #     5. 모든 코루틴이 끝날 때까지 반복
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ 현재 실행 중인 이벤트 루프 확인
    loop = asyncio.get_running_loop()
    print(f"  현재 이벤트 루프: {loop}")
    print(f"  루프 실행 중: {loop.is_running()}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ asyncio.run() 이해하기
    # ─────────────────────────────────────────────────────────────────────
    #
    #   asyncio.run(코루틴)의 역할:
    #     1. 새 이벤트 루프를 만든다
    #     2. 코루틴을 실행한다
    #     3. 모든 비동기 작업이 끝나면 루프를 닫는다
    #
    #   사용법:
    #     async def main():
    #         await do_something()
    #
    #     asyncio.run(main())   # ← 프로그램 진입점
    #
    #   ★ 주의: asyncio.run()은 프로그램에서 보통 한 번만 호출!
    #     이미 이벤트 루프가 돌고 있으면 asyncio.run()을 또 호출하면 에러!
    #
    #   ★ asyncio.run() vs get_event_loop()
    #     Python 3.10+ : asyncio.run()을 쓰는 것이 권장
    #     get_event_loop()는 레거시 방식 (하위 호환용)
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ asyncio.run()의 동작 순서")
    print("  ─────────────────────────────────────")
    print("  1. 새 이벤트 루프 생성")
    print("  2. 전달받은 코루틴 실행")
    print("  3. 모든 작업 완료 후 루프 종료")
    print()

    # ■ 이벤트 루프가 코루틴을 어떻게 관리하는지 시각화
    async def task_a():
        print("  [A] 시작")
        await asyncio.sleep(0.02)
        print("  [A] 완료")

    async def task_b():
        print("  [B] 시작")
        await asyncio.sleep(0.01)
        print("  [B] 완료")

    print("  ■ 이벤트 루프의 코루틴 전환 예시")
    print("  ─────────────────────────────────────")
    await asyncio.gather(task_a(), task_b())
    print("  → A와 B가 시작된 후, B가 먼저 끝남 (대기 시간이 짧으니까)")
    print()


# =========================================================================
#
#   레슨 4 — 동시 실행: gather와 create_task
#
# =========================================================================

async def lesson4_concurrent_execution():
    print_lesson("레슨 4 : 동시 실행")

    # ─────────────────────────────────────────────────────────────────────
    # ■ asyncio.gather() — 여러 코루틴을 한꺼번에 실행
    # ─────────────────────────────────────────────────────────────────────
    #
    #   gather(*코루틴들)
    #   - 모든 코루틴을 동시에 시작하고, 모두 끝나면 결과를 리스트로 반환
    #   - 결과 순서 = 인자 순서 (먼저 끝나도 순서 보장!)
    #
    #   비유: 식당에서 3가지 메뉴를 한꺼번에 주문 →
    #         주방에서 동시에 조리 → 모두 완성되면 한꺼번에 서빙
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ asyncio.gather() - 모두 완료 후 결과 수집")
    print("  ─────────────────────────────────────")

    async def download(name: str, seconds: float) -> str:
        print(f"    [{name}] 다운로드 시작")
        await asyncio.sleep(seconds)
        print(f"    [{name}] 다운로드 완료")
        return f"{name}: {seconds}초"

    start = time.perf_counter()
    results = await asyncio.gather(
        download("파일A", 0.03),
        download("파일B", 0.01),
        download("파일C", 0.02),
    )
    elapsed = time.perf_counter() - start

    print(f"  결과(순서 보장됨): {results}")
    print(f"  총 시간: {elapsed:.3f}초 (가장 긴 0.03초에 맞춰짐)")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ asyncio.create_task() — 태스크를 만들고 나중에 결과를 수집
    # ─────────────────────────────────────────────────────────────────────
    #
    #   create_task(코루틴) → Task 객체 반환
    #   - 호출 즉시 이벤트 루프에 등록 (바로 실행 시작!)
    #   - await task 로 결과를 나중에 받을 수 있다
    #   - gather보다 세밀한 제어가 가능
    #
    #   비유: gather는 "여기 3개 요리 부탁해요" (일괄 주문)
    #         create_task는 "이거 하나 먼저 부탁, 그 사이 나는 다른 것 준비"
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ asyncio.create_task() - 즉시 실행 등록")
    print("  ─────────────────────────────────────")

    async def process(name: str, delay: float) -> str:
        await asyncio.sleep(delay)
        return f"{name} 처리됨"

    task1 = asyncio.create_task(process("작업1", 0.02))
    task2 = asyncio.create_task(process("작업2", 0.01))

    # create_task를 호출한 순간 이미 실행이 시작됨!
    print("  태스크 생성 직후:")
    print(f"    task1 완료 여부: {task1.done()}")
    print(f"    task2 완료 여부: {task2.done()}")

    r1 = await task1
    r2 = await task2
    print(f"  결과: {r1}, {r2}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ gather vs create_task 비교
    # ─────────────────────────────────────────────────────────────────────
    #
    #   gather:
    #     - 간편하게 여러 코루틴을 한꺼번에 실행할 때
    #     - 결과 순서가 보장됨
    #     - return_exceptions=True 로 에러 수집 가능
    #
    #   create_task:
    #     - 실행 중간에 태스크를 추가하거나 취소할 때
    #     - task.cancel() 같은 세밀한 제어가 필요할 때
    #     - 특정 태스크의 상태(done, cancelled)를 확인할 때
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ gather의 return_exceptions 옵션
    async def might_fail(n: int) -> str:
        if n == 2:
            raise ValueError(f"작업 {n}에서 에러 발생!")
        await asyncio.sleep(0.01)
        return f"작업 {n} 성공"

    print("  ■ gather의 return_exceptions=True")
    print("  ─────────────────────────────────────")
    results = await asyncio.gather(
        might_fail(1), might_fail(2), might_fail(3),
        return_exceptions=True
    )
    for i, r in enumerate(results, 1):
        if isinstance(r, Exception):
            print(f"    작업{i}: 에러 - {r}")
        else:
            print(f"    작업{i}: {r}")
    print()


# =========================================================================
#
#   레슨 5 — asyncio.wait와 as_completed
#
# =========================================================================

async def lesson5_wait_and_as_completed():
    print_lesson("레슨 5 : wait와 as_completed")

    # ─────────────────────────────────────────────────────────────────────
    # ■ asyncio.wait() — 완료/미완료를 구분하여 반환
    # ─────────────────────────────────────────────────────────────────────
    #
    #   wait(태스크들, return_when=FIRST_COMPLETED|ALL_COMPLETED)
    #   - done(완료), pending(미완료) 두 집합을 반환
    #   - FIRST_COMPLETED: 하나라도 끝나면 즉시 반환
    #   - ALL_COMPLETED: 모두 끝나면 반환
    #
    #   비유: 경마장에서 말 여러 마리가 달리고 있을 때
    #     FIRST_COMPLETED = "1등 말이 들어오면 결과 발표"
    #     ALL_COMPLETED   = "모든 말이 들어오면 결과 발표"
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ asyncio.wait() - FIRST_COMPLETED")
    print("  ─────────────────────────────────────")

    async def runner(name: str, seconds: float) -> str:
        await asyncio.sleep(seconds)
        return f"{name} ({seconds}초)"

    tasks = [
        asyncio.create_task(runner("토끼", 0.01)),
        asyncio.create_task(runner("거북이", 0.03)),
        asyncio.create_task(runner("치타", 0.005)),
    ]

    # 하나라도 끝나면 바로 반환
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    print(f"  완료된 태스크 수: {len(done)}")
    for t in done:
        print(f"    완료: {t.result()}")
    print(f"  아직 진행 중: {len(pending)}개")

    # 남은 것도 기다리기
    if pending:
        done2, _ = await asyncio.wait(pending)
        for t in done2:
            print(f"    뒤늦게 완료: {t.result()}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ asyncio.as_completed() — 끝나는 순서대로 처리
    # ─────────────────────────────────────────────────────────────────────
    #
    #   먼저 끝나는 코루틴부터 결과를 하나씩 받을 수 있다
    #   이터레이터처럼 for 루프에서 사용
    #
    #   비유: 택배가 도착하는 순서대로 개봉하기
    #         (주문 순서와 도착 순서는 다를 수 있음)
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ asyncio.as_completed() - 완료 순서대로 처리")
    print("  ─────────────────────────────────────")

    coroutines = [
        runner("느린 택배", 0.03),
        runner("빠른 택배", 0.01),
        runner("보통 택배", 0.02),
    ]

    order = 1
    for coro in asyncio.as_completed(coroutines):
        result = await coro
        print(f"    {order}번째 도착: {result}")
        order += 1
    print()

    # ■ as_completed에 timeout 적용
    print("  ■ as_completed에 timeout 적용")
    print("  ─────────────────────────────────────")

    slow_coroutines = [
        runner("빠른 작업", 0.01),
        runner("느린 작업", 0.5),
    ]

    for coro in asyncio.as_completed(slow_coroutines, timeout=0.05):
        try:
            result = await coro
            print(f"    완료: {result}")
        except asyncio.TimeoutError:
            print("    타임아웃! 시간 초과된 작업이 있습니다.")
            break
    print()


# =========================================================================
#
#   레슨 6 — 비동기 이터레이터/제너레이터
#
# =========================================================================

async def lesson6_async_iterators():
    print_lesson("레슨 6 : 비동기 이터레이터")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 비동기 이터레이터란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   일반 이터레이터: for item in 리스트
    #   비동기 이터레이터: async for item in 비동기_소스
    #
    #   비유: 일반 이터레이터 = 도서관에서 책을 한 권씩 꺼내기 (즉시 가능)
    #         비동기 이터레이터 = 인터넷에서 파일을 한 개씩 다운로드 (대기 필요)
    #
    #   __aiter__() 와 __anext__() 를 구현하면 비동기 이터레이터!
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ 비동기 제너레이터 (async def + yield)
    async def countdown(n: int):
        """비동기 제너레이터: 카운트다운을 비동기로 수행"""
        while n > 0:
            await asyncio.sleep(0.01)
            yield n
            n -= 1

    print("  ■ 비동기 제너레이터 (async for)")
    print("  ─────────────────────────────────────")

    values = []
    async for number in countdown(5):
        values.append(number)
    print(f"  카운트다운: {values}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ __aiter__와 __anext__로 직접 구현
    # ─────────────────────────────────────────────────────────────────────

    class AsyncRange:
        """비동기 이터레이터를 직접 구현한 클래스"""
        def __init__(self, start: int, stop: int):
            self.current = start
            self.stop = stop

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self.current >= self.stop:
                raise StopAsyncIteration     # 비동기 반복 종료 신호
            value = self.current
            self.current += 1
            await asyncio.sleep(0.005)       # 비동기 작업 시뮬레이션
            return value

    print("  ■ 커스텀 비동기 이터레이터 (AsyncRange)")
    print("  ─────────────────────────────────────")

    result = []
    async for num in AsyncRange(1, 6):
        result.append(num)
    print(f"  AsyncRange(1, 6): {result}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ async with (비동기 컨텍스트 매니저)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   __aenter__와 __aexit__를 구현하면 async with를 쓸 수 있다.
    #   파일 열기, DB 연결, HTTP 세션 등에 활용
    #
    # ─────────────────────────────────────────────────────────────────────

    class AsyncConnection:
        """비동기 컨텍스트 매니저 예시 (DB 연결 시뮬레이션)"""
        def __init__(self, name: str):
            self.name = name

        async def __aenter__(self):
            await asyncio.sleep(0.01)
            print(f"    [{self.name}] 연결 열기")
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await asyncio.sleep(0.01)
            print(f"    [{self.name}] 연결 닫기")
            return False    # 예외를 전파

        async def query(self, sql: str) -> str:
            await asyncio.sleep(0.01)
            return f"'{sql}' 실행 결과: OK"

    print("  ■ async with (비동기 컨텍스트 매니저)")
    print("  ─────────────────────────────────────")

    async with AsyncConnection("TestDB") as conn:
        result = await conn.query("SELECT * FROM users")
        print(f"    쿼리 결과: {result}")
    print("  → 자동으로 연결이 열리고 닫힘")
    print()


# =========================================================================
#
#   레슨 7 — asyncio.Queue (생산자-소비자 패턴)
#
# =========================================================================

async def lesson7_async_queue():
    print_lesson("레슨 7 : asyncio.Queue")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 생산자-소비자 패턴이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   생산자(Producer): 데이터를 만들어서 큐에 넣는 쪽
    #   소비자(Consumer): 큐에서 데이터를 꺼내 처리하는 쪽
    #
    #   비유: 빵집
    #     - 제빵사(생산자)가 빵을 구워서 진열대(큐)에 놓는다
    #     - 점원(소비자)이 진열대에서 빵을 꺼내 손님에게 판다
    #     - 진열대가 꽉 차면 → 제빵사는 잠깐 쉰다 (큐 가득)
    #     - 진열대가 비면 → 점원은 빵이 올 때까지 기다린다 (큐 비어있음)
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ 기본 생산자-소비자
    print("  ■ 기본 생산자-소비자 패턴")
    print("  ─────────────────────────────────────")

    queue: asyncio.Queue = asyncio.Queue(maxsize=3)  # 최대 3개까지

    async def producer(name: str, items: list):
        for item in items:
            await queue.put(item)
            print(f"    [생산] {name} → {item} (큐 크기: {queue.qsize()})")
            await asyncio.sleep(0.01)

    async def consumer(name: str):
        while True:
            item = await queue.get()
            if item is None:   # 종료 신호
                queue.task_done()
                break
            print(f"    [소비] {name} ← {item}")
            await asyncio.sleep(0.02)   # 처리 시간
            queue.task_done()

    # 생산자가 데이터를 넣고 종료 신호(None)를 보냄
    items = ["주문1", "주문2", "주문3", "주문4"]

    await asyncio.gather(
        producer("주방", items + [None]),
        consumer("점원"),
    )
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 여러 소비자로 병렬 처리
    # ─────────────────────────────────────────────────────────────────────
    #
    #   소비자를 여러 개 두면 처리 속도가 빨라진다!
    #   비유: 점원 1명 → 3명으로 늘리면 주문 처리가 빨라지는 것
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 다중 소비자 패턴")
    print("  ─────────────────────────────────────")

    work_queue: asyncio.Queue = asyncio.Queue()
    results_collected = []

    async def worker(worker_id: int):
        while True:
            item = await work_queue.get()
            if item is None:
                work_queue.task_done()
                break
            await asyncio.sleep(0.01)
            result = f"워커{worker_id}가 '{item}' 처리"
            results_collected.append(result)
            work_queue.task_done()

    # 작업 투입
    for task_name in ["분석A", "분석B", "분석C", "분석D", "분석E", "분석F"]:
        await work_queue.put(task_name)

    # 종료 신호 (워커 수만큼)
    num_workers = 3
    for _ in range(num_workers):
        await work_queue.put(None)

    # 3개 워커 동시 실행
    workers = [asyncio.create_task(worker(i)) for i in range(num_workers)]
    await asyncio.gather(*workers)

    for r in results_collected:
        print(f"    {r}")
    print(f"  → {num_workers}개 워커로 {len(results_collected)}개 작업 처리 완료")
    print()


# =========================================================================
#
#   레슨 8 — 동기 코드와 혼합 (run_in_executor)
#
# =========================================================================

async def lesson8_sync_async_mixing():
    print_lesson("레슨 8 : 동기 코드와 혼합")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 왜 혼합이 필요한가?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   현실에서는 모든 라이브러리가 비동기를 지원하지 않는다!
    #   - requests 라이브러리 → 동기 방식
    #   - 파일 읽기/쓰기 → 기본적으로 동기
    #   - CPU 집약적 계산 → 동기
    #
    #   이런 동기 함수를 asyncio 안에서 바로 호출하면?
    #   → 이벤트 루프가 블로킹되어 다른 코루틴이 멈춤!
    #
    #   해결책: run_in_executor() 또는 asyncio.to_thread()
    #   - 동기 함수를 별도 쓰레드에서 실행
    #   - 이벤트 루프는 블로킹되지 않음
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ 문제 상황: 동기 함수가 이벤트 루프를 막는 경우
    print("  ■ asyncio.to_thread() - 동기 함수를 쓰레드로 분리")
    print("  ─────────────────────────────────────")

    def slow_io_operation(name: str) -> str:
        """동기 I/O 작업 시뮬레이션 (블로킹)"""
        time.sleep(0.05)
        return f"{name}: I/O 완료"

    start = time.perf_counter()

    # to_thread로 동기 함수를 별도 쓰레드에서 실행
    results = await asyncio.gather(
        asyncio.to_thread(slow_io_operation, "파일읽기"),
        asyncio.to_thread(slow_io_operation, "DB쿼리"),
        asyncio.to_thread(slow_io_operation, "API호출"),
    )

    elapsed = time.perf_counter() - start
    for r in results:
        print(f"    {r}")
    print(f"  총 시간: {elapsed:.3f}초 (3개를 동시에 → 약 0.05초)")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ run_in_executor — 더 세밀한 제어
    # ─────────────────────────────────────────────────────────────────────
    #
    #   loop.run_in_executor(executor, 함수, *인자)
    #   - executor=None → 기본 ThreadPoolExecutor
    #   - ThreadPoolExecutor → I/O 바운드 작업
    #   - ProcessPoolExecutor → CPU 바운드 작업
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ run_in_executor + ThreadPoolExecutor")
    print("  ─────────────────────────────────────")

    loop = asyncio.get_running_loop()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = await asyncio.gather(
            loop.run_in_executor(pool, heavy_cpu_work, 10000),
            loop.run_in_executor(pool, heavy_cpu_work, 20000),
        )

    print(f"  결과1: sum(0..9999) = {results[0]}")
    print(f"  결과2: sum(0..19999) = {results[1]}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 비동기 + 동기 혼합 패턴 정리
    # ─────────────────────────────────────────────────────────────────────
    #
    #   ┌──────────────────────┬──────────────────────────┐
    #   │ 상황                 │ 해결 방법                │
    #   ├──────────────────────┼──────────────────────────┤
    #   │ I/O 바운드 동기 함수 │ asyncio.to_thread()      │
    #   │ CPU 바운드 동기 함수 │ ProcessPoolExecutor      │
    #   │ async 코루틴 호출    │ await                    │
    #   │ 동기 코드에서 async  │ asyncio.run()            │
    #   └──────────────────────┴──────────────────────────┘
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 혼합 패턴 요약")
    print("  ─────────────────────────────────────")
    print("  I/O 바운드 동기 → asyncio.to_thread()")
    print("  CPU 바운드 동기 → ProcessPoolExecutor")
    print("  코루틴 호출     → await")
    print("  동기에서 비동기 → asyncio.run()")
    print()


# =========================================================================
#
#   레슨 9 — 에러 처리와 타임아웃
#
# =========================================================================

async def lesson9_error_handling_and_timeout():
    print_lesson("레슨 9 : 에러 처리와 타임아웃")

    # ─────────────────────────────────────────────────────────────────────
    # ■ asyncio.wait_for() — 타임아웃 설정
    # ─────────────────────────────────────────────────────────────────────
    #
    #   await asyncio.wait_for(코루틴, timeout=초)
    #   - 지정 시간 내에 완료되지 않으면 TimeoutError 발생
    #   - 코루틴은 자동으로 취소(cancel)됨
    #
    #   비유: 음식 배달 앱에서 "30분 이내 도착 보장"
    #         30분 넘기면 → 주문 취소!
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ asyncio.wait_for() - 타임아웃")
    print("  ─────────────────────────────────────")

    async def slow_api_call() -> str:
        await asyncio.sleep(0.5)   # 매우 느린 API
        return "API 응답"

    # 타임아웃 성공 케이스
    async def fast_api_call() -> str:
        await asyncio.sleep(0.01)
        return "빠른 API 응답"

    try:
        result = await asyncio.wait_for(fast_api_call(), timeout=0.1)
        print(f"  성공: {result}")
    except asyncio.TimeoutError:
        print("  시간 초과!")

    # 타임아웃 실패 케이스
    try:
        result = await asyncio.wait_for(slow_api_call(), timeout=0.05)
        print(f"  성공: {result}")
    except asyncio.TimeoutError:
        print("  시간 초과! → 느린 API 호출이 취소됨")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 태스크 취소 (task.cancel())
    # ─────────────────────────────────────────────────────────────────────
    #
    #   task.cancel() → CancelledError 발생
    #   - 취소된 태스크를 await하면 CancelledError
    #   - try/except CancelledError로 정리(cleanup) 가능
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 태스크 취소 (task.cancel())")
    print("  ─────────────────────────────────────")

    async def long_running_task():
        try:
            print("    장기 작업 시작...")
            await asyncio.sleep(10)
            return "완료"
        except asyncio.CancelledError:
            print("    장기 작업이 취소됨! 정리(cleanup) 수행...")
            raise   # 반드시 다시 raise 해야 정상 취소 처리

    task = asyncio.create_task(long_running_task())
    await asyncio.sleep(0.01)   # 잠깐 실행되게 두고
    task.cancel()               # 취소!

    try:
        await task
    except asyncio.CancelledError:
        print("    태스크가 정상적으로 취소되었습니다.")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 예외 전파 — gather에서의 에러 처리
    # ─────────────────────────────────────────────────────────────────────
    #
    #   gather(return_exceptions=False) → 첫 에러에서 즉시 전파 (기본값)
    #   gather(return_exceptions=True)  → 에러를 결과 리스트에 포함
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ gather에서의 예외 처리 전략")
    print("  ─────────────────────────────────────")

    async def risky_task(task_id: int) -> str:
        await asyncio.sleep(0.01)
        if task_id == 3:
            raise RuntimeError(f"태스크 {task_id}: 치명적 오류!")
        return f"태스크 {task_id}: 성공"

    # return_exceptions=True → 에러도 결과에 포함
    results = await asyncio.gather(
        risky_task(1), risky_task(2), risky_task(3), risky_task(4),
        return_exceptions=True
    )

    for i, r in enumerate(results, 1):
        if isinstance(r, Exception):
            print(f"    태스크{i}: 에러 → {type(r).__name__}: {r}")
        else:
            print(f"    태스크{i}: {r}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ asyncio.TaskGroup (Python 3.11+) — 구조적 동시성
    # ─────────────────────────────────────────────────────────────────────
    #
    #   TaskGroup은 gather의 개선 버전
    #   - 하나의 태스크가 실패하면 나머지 태스크 자동 취소
    #   - ExceptionGroup으로 여러 에러를 한번에 처리
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ asyncio.TaskGroup (Python 3.11+)")
    print("  ─────────────────────────────────────")

    async def safe_task(n: int) -> str:
        await asyncio.sleep(0.01)
        return f"작업{n} 완료"

    try:
        async with asyncio.TaskGroup() as tg:
            task1 = tg.create_task(safe_task(1))
            task2 = tg.create_task(safe_task(2))
            task3 = tg.create_task(safe_task(3))

        print(f"    결과: {task1.result()}, {task2.result()}, {task3.result()}")
    except* Exception as eg:
        for e in eg.exceptions:
            print(f"    에러: {e}")
    print()


# =========================================================================
#
#   레슨 10 — 실전: 비동기 웹 크롤러 시뮬레이션
#
# =========================================================================

async def lesson10_web_crawler_simulation():
    print_lesson("레슨 10 : 웹 크롤러 시뮬레이션")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 시나리오: 여러 웹 페이지를 동시에 크롤링하는 시뮬레이션
    # ─────────────────────────────────────────────────────────────────────
    #
    #   실제 HTTP 요청 대신 asyncio.sleep으로 네트워크 지연을 시뮬레이션
    #   핵심 구조:
    #     - URL 큐에 크롤링할 주소를 넣는다
    #     - 여러 워커가 동시에 URL을 꺼내서 크롤링한다
    #     - 결과를 수집하고 통계를 출력한다
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ 가짜 웹 페이지 데이터
    fake_pages = {
        "https://example.com":          {"title": "홈페이지", "links": 5, "delay": 0.02},
        "https://example.com/about":    {"title": "소개 페이지", "links": 3, "delay": 0.01},
        "https://example.com/products": {"title": "상품 목록", "links": 12, "delay": 0.03},
        "https://example.com/blog":     {"title": "블로그", "links": 8, "delay": 0.015},
        "https://example.com/contact":  {"title": "연락처", "links": 2, "delay": 0.005},
        "https://example.com/faq":      {"title": "자주 묻는 질문", "links": 6, "delay": 0.025},
        "https://example.com/login":    {"title": "로그인", "links": 1, "delay": 0.01},
        "https://example.com/error":    {"title": None, "links": 0, "delay": 0.01},  # 에러 페이지
    }

    # ■ 비동기 페이지 가져오기 함수
    async def fetch_page(url: str) -> dict:
        """URL을 '크롤링'하는 비동기 함수 (시뮬레이션)"""
        if url not in fake_pages:
            raise ValueError(f"404 Not Found: {url}")

        page = fake_pages[url]
        await asyncio.sleep(page["delay"])  # 네트워크 지연 시뮬레이션

        if page["title"] is None:
            raise ConnectionError(f"500 Server Error: {url}")

        return {
            "url": url,
            "title": page["title"],
            "links_found": page["links"],
        }

    # ■ 크롤러 워커
    crawl_results = []
    crawl_errors = []

    async def crawler_worker(worker_id: int, url_queue: asyncio.Queue):
        """큐에서 URL을 꺼내 크롤링하는 워커"""
        while True:
            url = await url_queue.get()
            if url is None:
                url_queue.task_done()
                break
            try:
                result = await asyncio.wait_for(fetch_page(url), timeout=0.05)
                crawl_results.append(result)
                print(f"    [워커{worker_id}] OK {result['title']} ({url})")
            except asyncio.TimeoutError:
                crawl_errors.append({"url": url, "error": "타임아웃"})
                print(f"    [워커{worker_id}] FAIL 타임아웃 ({url})")
            except Exception as e:
                crawl_errors.append({"url": url, "error": str(e)})
                print(f"    [워커{worker_id}] FAIL 에러: {e}")
            finally:
                url_queue.task_done()

    # ■ 크롤링 실행
    print("  ■ 비동기 크롤러 시작 (워커 3개)")
    print("  ─────────────────────────────────────")

    url_queue: asyncio.Queue = asyncio.Queue()

    # URL 투입
    for url in fake_pages.keys():
        await url_queue.put(url)

    # 종료 신호
    num_workers = 3
    for _ in range(num_workers):
        await url_queue.put(None)

    start = time.perf_counter()
    workers = [asyncio.create_task(crawler_worker(i, url_queue)) for i in range(num_workers)]
    await asyncio.gather(*workers)
    elapsed = time.perf_counter() - start

    # ■ 결과 통계
    print()
    print("  ■ 크롤링 결과 통계")
    print("  ─────────────────────────────────────")
    print(f"  총 URL 수: {len(fake_pages)}")
    print(f"  성공: {len(crawl_results)}개")
    print(f"  실패: {len(crawl_errors)}개")
    print(f"  총 소요 시간: {elapsed:.3f}초")

    if crawl_results:
        total_links = sum(r["links_found"] for r in crawl_results)
        print(f"  발견된 링크 수 합계: {total_links}개")

    if crawl_errors:
        print(f"  에러 목록:")
        for err in crawl_errors:
            print(f"    - {err['url']}: {err['error']}")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인 실행 함수
# ─────────────────────────────────────────────────────────────────────────

async def async_main() -> None:
    """모든 레슨을 순서대로 실행"""
    print("=" * 72)
    print("  파이썬 학습 15단계: asyncio (비동기 프로그래밍)")
    print("=" * 72)

    await lesson1_sync_vs_async()
    await lesson2_coroutine_basics()
    await lesson3_event_loop()
    await lesson4_concurrent_execution()
    await lesson5_wait_and_as_completed()
    await lesson6_async_iterators()
    await lesson7_async_queue()
    await lesson8_sync_async_mixing()
    await lesson9_error_handling_and_timeout()
    await lesson10_web_crawler_simulation()

    print()
    print("=" * 72)
    print("  모든 레슨 완료!")
    print("=" * 72)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
