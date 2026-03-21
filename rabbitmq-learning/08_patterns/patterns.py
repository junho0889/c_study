"""
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  RabbitMQ 08단계: 고급 메시징 패턴                               ■
■  Priority Queue, Delayed Message, Saga Pattern,                ■
■  Competing Consumers, Message Deduplication                    ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
"""

import heapq
import time
import hashlib
from collections import deque


# ============================================================
#  토이 구현: 우선순위 큐, 지연 메시지, 중복 제거
# ============================================================
class PriorityQueue:
    """
    우선순위 큐: 높은 우선순위 메시지가 먼저 나옴.
    비유: 응급실 - 환자 상태가 심각할수록 먼저 진료합니다.
    """

    def __init__(self, name):
        self.name = name
        self.heap = []  # (priority, counter, message) - priority 낮을수록 먼저
        self.counter = 0

    def publish(self, body, priority=0):
        """priority가 높을수록(숫자가 클수록) 먼저 처리.
        내부적으로는 음수로 변환해 min-heap에서 높은 우선순위가 먼저 나오게 함."""
        heapq.heappush(self.heap, (-priority, self.counter, body))
        self.counter += 1

    def consume(self):
        if self.heap:
            neg_priority, _, body = heapq.heappop(self.heap)
            return {"body": body, "priority": -neg_priority}
        return None

    def size(self):
        return len(self.heap)


class DelayedQueue:
    """
    지연 메시지 큐: 정해진 시간 후에 메시지가 소비 가능해짐.
    비유: 예약 알람 - 지금 울리지 않고 정해진 시각에 울림.
    """

    def __init__(self, name):
        self.name = name
        self.messages = []  # (available_at, counter, message)
        self.counter = 0

    def publish(self, body, delay_seconds=0):
        available_at = time.time() + delay_seconds
        heapq.heappush(self.messages, (available_at, self.counter, body))
        self.counter += 1

    def consume(self, current_time=None):
        current_time = current_time or time.time()
        if self.messages and self.messages[0][0] <= current_time:
            _, _, body = heapq.heappop(self.messages)
            return body
        return None

    def pending_count(self):
        return len(self.messages)


class DeduplicationFilter:
    """
    메시지 중복 제거 필터.
    비유: 출석 체크에서 같은 학생이 두 번 출석하면 한 번만 인정.
    """

    def __init__(self, window_size=1000):
        self.seen_ids = set()
        self.window_size = window_size

    def is_duplicate(self, message_id):
        if message_id in self.seen_ids:
            return True
        self.seen_ids.add(message_id)
        # 윈도우 초과 시 오래된 것 제거 (간단 구현)
        if len(self.seen_ids) > self.window_size:
            self.seen_ids.clear()
        return False

    def compute_id(self, body):
        """메시지 본문으로 고유 ID 생성"""
        return hashlib.md5(str(body).encode()).hexdigest()[:12]


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 1: Priority Queue - 응급실처럼 긴급한 것 먼저         │
# │  비유: 응급실 - 심각한 환자부터 먼저 진료                     │
# └─────────────────────────────────────────────────────────────┘
def lesson1_priority_queue():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 1: Priority Queue - 긴급한 것 먼저            │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 우선순위 큐는 priority가 높은 메시지가 먼저 처리됩니다.
    # 응급실에서 환자 상태가 심각할수록 먼저 진료하는 것과 같아요!
    # RabbitMQ에서는 x-max-priority 설정으로 사용합니다.

    pq = PriorityQueue("support_tickets")

    # 고객 문의를 우선순위별로 등록
    tickets = [
        ("서버 다운! 전체 서비스 중단", 10),    # 최고 긴급
        ("로그인 버튼이 안 눌려요", 5),          # 중간
        ("다크 모드 추가해 주세요", 1),           # 낮음
        ("결제가 안 돼요", 8),                   # 높음
        ("글씨 크기 변경 요청", 2),              # 낮음
    ]

    print("  [접수] 고객 문의:")
    for body, priority in tickets:
        pq.publish(body, priority=priority)
        print(f"    우선순위 {priority:2d}: {body}")

    print(f"\n  [처리] 우선순위 높은 순서대로:")
    while pq.size() > 0:
        msg = pq.consume()
        print(f"    우선순위 {msg['priority']:2d}: {msg['body']}")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 2: Delayed Message - 예약 알람처럼 나중에 전달         │
# │  비유: 30분 후에 울리는 타이머 - 지금이 아니라 나중에         │
# └─────────────────────────────────────────────────────────────┘
def lesson2_delayed_message():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 2: Delayed Message - 나중에 전달              │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 지연 메시지는 '지금 보내지만, N초 후에 소비 가능'한 메시지입니다.
    # 30분 후에 울리는 알람과 같아요!
    # 활용: 주문 후 30분 미결제 시 자동 취소, 이메일 예약 발송

    dq = DelayedQueue("scheduled_tasks")
    base_time = time.time()

    # 지연 메시지 등록
    tasks = [
        ("미결제 주문 #1001 자동 취소", 30),    # 30초 후
        ("회원가입 환영 이메일 발송", 5),        # 5초 후
        ("리뷰 작성 독촉 알림", 60),            # 60초 후
        ("장바구니 리마인더 푸시", 10),          # 10초 후
    ]

    print("  [등록] 지연 메시지:")
    for body, delay in tasks:
        dq.publish(body, delay_seconds=delay)
        print(f"    {delay:3d}초 후: {body}")

    # 시간 경과 시뮬레이션
    print(f"\n  [시간 경과 시뮬레이션]")
    for elapsed in [0, 5, 10, 30, 60]:
        check_time = base_time + elapsed
        msg = dq.consume(current_time=check_time)
        if msg:
            print(f"    t={elapsed:2d}초: 소비 가능 -> '{msg}'")
        else:
            print(f"    t={elapsed:2d}초: 아직 소비 가능한 메시지 없음")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 3: Saga Pattern - 분산 트랜잭션                       │
# │  비유: 수학여행 예약 - 버스, 숙소, 식당 중 하나 실패하면      │
# │        나머지도 취소해야 함                                   │
# └─────────────────────────────────────────────────────────────┘
def lesson3_saga_pattern():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 3: Saga Pattern - 분산 트랜잭션               │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Saga는 여러 서비스에 걸친 트랜잭션을 관리하는 패턴입니다.
    # 수학여행 예약에서 버스, 숙소, 식당을 예약하는데
    # 식당 예약이 실패하면 버스와 숙소도 취소해야 합니다!
    # 각 단계가 성공하면 다음으로, 실패하면 이전 단계를 보상(취소)합니다.

    class SagaOrchestrator:
        def __init__(self):
            self.completed_steps = []
            self.compensations = []

        def execute_step(self, name, action, compensation):
            print(f"    [{name}] 실행 중...", end=" ")
            success = action()
            if success:
                print("성공!")
                self.completed_steps.append(name)
                self.compensations.append((name, compensation))
                return True
            else:
                print("실패!")
                self.rollback()
                return False

        def rollback(self):
            print("    [ROLLBACK] 이전 단계들을 보상(취소)합니다:")
            for name, compensation in reversed(self.compensations):
                print(f"      -> {name} 취소 중...", end=" ")
                compensation()
                print("완료")
            self.compensations.clear()
            self.completed_steps.clear()

    # 시나리오 1: 모두 성공
    print("  [시나리오 1] 주문 처리 - 모두 성공:")
    saga1 = SagaOrchestrator()
    saga1.execute_step("재고 차감", lambda: True, lambda: None)
    saga1.execute_step("결제 처리", lambda: True, lambda: None)
    saga1.execute_step("배송 요청", lambda: True, lambda: None)
    print(f"    완료된 단계: {saga1.completed_steps}")

    # 시나리오 2: 중간에 실패 -> 보상
    print(f"\n  [시나리오 2] 주문 처리 - 배송 단계에서 실패:")
    saga2 = SagaOrchestrator()
    saga2.execute_step("재고 차감", lambda: True, lambda: print("재고 복구"))
    saga2.execute_step("결제 처리", lambda: True, lambda: print("환불 처리"))
    saga2.execute_step("배송 요청", lambda: False, lambda: None)  # 실패!
    print(f"    완료된 단계: {saga2.completed_steps}")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 4: Competing Consumers - 일꾼 여럿이 나눠 처리        │
# │  비유: 마트 계산대 - 여러 계산대가 고객을 나눠 처리           │
# └─────────────────────────────────────────────────────────────┘
def lesson4_competing_consumers():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 4: Competing Consumers                        │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Competing Consumers: 여러 소비자가 하나의 큐에서 경쟁하며 메시지를 가져갑니다.
    # 마트에서 계산대 3개가 줄 선 고객을 나눠 처리하는 것과 같아요!
    # 메시지는 한 소비자에게만 전달됩니다 (중복 처리 없음).

    task_queue = deque()

    # 작업 10개 등록
    for i in range(1, 11):
        task_queue.append(f"작업_{i}")

    # 소비자 3명이 경쟁하며 처리
    consumers = {"소비자A": [], "소비자B": [], "소비자C": []}
    consumer_names = list(consumers.keys())
    idx = 0

    print("  [작업 분배] (라운드로빈 방식):")
    while task_queue:
        task = task_queue.popleft()
        consumer = consumer_names[idx % len(consumer_names)]
        consumers[consumer].append(task)
        idx += 1

    for name, tasks in consumers.items():
        print(f"    {name}: {tasks}")

    print(f"\n  각 소비자 처리량: {', '.join(f'{n}={len(t)}개' for n, t in consumers.items())}")
    print("  -> 작업이 고르게 분배되어 처리 속도가 빨라집니다!")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 5: Message Deduplication - 같은 메시지 중복 방지       │
# │  비유: 출석 체크에서 같은 학생이 두 번 오면 한 번만 인정      │
# └─────────────────────────────────────────────────────────────┘
def lesson5_deduplication():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 5: Message Deduplication - 중복 제거           │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 네트워크 재전송 등으로 같은 메시지가 여러 번 올 수 있습니다.
    # 출석 체크에서 같은 학생이 두 번 와도 한 번만 인정하는 것과 같아요!
    # 메시지 ID(또는 본문 해시)로 이미 처리한 것인지 확인합니다.

    dedup = DeduplicationFilter()

    messages = [
        {"id": "msg_001", "body": "주문 1001 결제"},
        {"id": "msg_002", "body": "주문 1002 결제"},
        {"id": "msg_001", "body": "주문 1001 결제"},    # 중복!
        {"id": "msg_003", "body": "주문 1003 결제"},
        {"id": "msg_002", "body": "주문 1002 결제"},    # 중복!
    ]

    processed = 0
    skipped = 0

    print("  메시지 처리:")
    for msg in messages:
        if dedup.is_duplicate(msg["id"]):
            print(f"    [{msg['id']}] '{msg['body']}' -> 중복! 건너뜀")
            skipped += 1
        else:
            print(f"    [{msg['id']}] '{msg['body']}' -> 처리")
            processed += 1

    print(f"\n  결과: 처리 {processed}건, 중복 건너뜀 {skipped}건")
    print()

    # 본문 기반 중복 제거
    print("  [본문 해시 기반 중복 제거]")
    dedup2 = DeduplicationFilter()
    bodies = ["결제 50000원", "결제 30000원", "결제 50000원"]
    for body in bodies:
        msg_id = dedup2.compute_id(body)
        dup = dedup2.is_duplicate(msg_id)
        print(f"    '{body}' (hash={msg_id}) -> {'중복!' if dup else '신규'}")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 6: 패턴 정리                                          │
# └─────────────────────────────────────────────────────────────┘
def lesson6_summary():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 6: 패턴 정리                                  │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    print("  ┌────────────────────┬─────────────────────────────────────┐")
    print("  │ 패턴                │ 핵심 아이디어                        │")
    print("  ├────────────────────┼─────────────────────────────────────┤")
    print("  │ Priority Queue     │ 긴급한 것을 먼저 (응급실)            │")
    print("  │ Delayed Message    │ 나중에 전달 (예약 알람)              │")
    print("  │ Saga Pattern       │ 실패 시 되돌리기 (수학여행 예약)     │")
    print("  │ Competing Consumer │ 여럿이 나눠서 처리 (마트 계산대)     │")
    print("  │ Deduplication      │ 같은 것 두 번 안 함 (출석 체크)      │")
    print("  └────────────────────┴─────────────────────────────────────┘")
    print()


def main():
    print("=" * 72)
    print("  RabbitMQ 08단계: 고급 메시징 패턴")
    print("=" * 72)
    print()

    lesson1_priority_queue()
    lesson2_delayed_message()
    lesson3_saga_pattern()
    lesson4_competing_consumers()
    lesson5_deduplication()
    lesson6_summary()


if __name__ == "__main__":
    main()
