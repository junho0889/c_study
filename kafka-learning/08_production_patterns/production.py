"""
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  Kafka 08단계: 프로덕션 패턴                                    ■
■  Dead Letter Queue, Retry Topic, Event Sourcing, CQRS,         ■
■  Consumer Lag 모니터링, 파티션 전략                              ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
"""

import time
import hashlib
import random


# ============================================================
#  토이 Kafka 인프라
# ============================================================
class ToyTopic:
    def __init__(self, name, partitions=1):
        self.name = name
        self.partitions = [[] for _ in range(partitions)]

    def produce(self, key, value, partition=None):
        if partition is None:
            # 키 해시로 파티션 결정
            p = int(hashlib.md5(str(key).encode()).hexdigest(), 16) % len(self.partitions)
        else:
            p = partition
        offset = len(self.partitions[p])
        record = {"offset": offset, "key": key, "value": value, "timestamp": time.time()}
        self.partitions[p].append(record)
        return p, offset

    def total_records(self):
        return sum(len(p) for p in self.partitions)


class ToyConsumer:
    def __init__(self, name, topic):
        self.name = name
        self.topic = topic
        self.offsets = {i: 0 for i in range(len(topic.partitions))}

    def poll(self, partition):
        offset = self.offsets[partition]
        if offset < len(self.topic.partitions[partition]):
            record = self.topic.partitions[partition][offset]
            self.offsets[partition] = offset + 1
            return record
        return None

    def lag(self):
        """Consumer Lag: 아직 처리하지 못한 메시지 수"""
        total_lag = 0
        for p in range(len(self.topic.partitions)):
            latest = len(self.topic.partitions[p])
            current = self.offsets[p]
            total_lag += latest - current
        return total_lag


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 1: Dead Letter Queue (DLQ) - 처리 실패 메시지 격리     │
# │  비유: 배달 불가 우편물을 따로 모아두는 반송 우편함            │
# └─────────────────────────────────────────────────────────────┘
def lesson1_dead_letter_queue():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 1: Dead Letter Queue - 실패 메시지 격리       │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 처리할 수 없는 메시지(잘못된 형식, 비즈니스 규칙 위반 등)를
    # 메인 토픽에서 빼고 별도의 DLQ 토픽에 넣습니다.
    # 배달 불가 우편물을 반송 우편함에 따로 모아두는 것과 같아요!
    # 나중에 DLQ를 확인해서 원인을 분석하고 재처리할 수 있습니다.

    main_topic = ToyTopic("orders")
    dlq_topic = ToyTopic("orders.DLQ")

    messages = [
        {"order_id": 1001, "amount": 50000},
        {"order_id": 1002, "amount": -100},        # 금액 오류!
        {"order_id": 1003, "amount": 35000},
        {"order_id": None, "amount": 20000},        # ID 누락!
        {"order_id": 1005, "amount": 12000},
    ]

    processed = 0
    failed = 0

    print("  메시지 처리:")
    for msg in messages:
        # 유효성 검사
        if msg["order_id"] is None:
            dlq_topic.produce(str(msg), f"DLQ: ID 누락 - {msg}")
            print(f"    [DLQ] {msg} -> ID가 없습니다!")
            failed += 1
        elif msg["amount"] <= 0:
            dlq_topic.produce(str(msg), f"DLQ: 금액 오류 - {msg}")
            print(f"    [DLQ] {msg} -> 금액이 잘못되었습니다!")
            failed += 1
        else:
            main_topic.produce(str(msg["order_id"]), str(msg))
            print(f"    [OK]  {msg} -> 처리 완료")
            processed += 1

    print(f"\n  결과: 성공 {processed}건, DLQ {failed}건")
    print("  -> DLQ에 있는 메시지는 나중에 원인 분석 후 재처리합니다.")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 2: Retry Topic - 실패 시 재시도                       │
# │  비유: 전화 안 받으면 나중에 다시 전화하기                    │
# └─────────────────────────────────────────────────────────────┘
def lesson2_retry_topic():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 2: Retry Topic - 실패 시 재시도               │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 일시적 오류(네트워크 타임아웃 등)로 실패한 메시지는
    # retry 토픽에 넣어 나중에 다시 시도합니다.
    # 전화를 안 받으면 5분 후 다시 걸어보는 것과 같아요!
    # 보통 retry-1, retry-2, retry-3으로 단계를 두고,
    # 최종 실패 시 DLQ로 보냅니다.

    main_topic = ToyTopic("payments")
    retry_topics = [ToyTopic(f"payments.retry-{i}") for i in range(1, 4)]
    dlq_topic = ToyTopic("payments.DLQ")

    random.seed(42)

    def process_with_retry(message, max_retries=3):
        for attempt in range(max_retries + 1):
            # 시뮬레이션: 70% 확률로 성공
            success = random.random() > 0.3

            if attempt == 0:
                source = "main"
            else:
                source = f"retry-{attempt}"

            if success:
                print(f"    [{source}] '{message}' -> 성공!")
                return True
            else:
                if attempt < max_retries:
                    retry_topics[attempt].produce("key", message)
                    print(f"    [{source}] '{message}' -> 실패, retry-{attempt + 1}로 이동")
                else:
                    dlq_topic.produce("key", message)
                    print(f"    [{source}] '{message}' -> 최종 실패! DLQ로 이동")
                    return False

    print("  결제 처리 (최대 3회 재시도):")
    for msg in ["결제_A", "결제_B", "결제_C"]:
        process_with_retry(msg)
        print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 3: Event Sourcing - 모든 변경을 이벤트로 기록          │
# │  비유: 은행 통장에 입출금 내역을 모두 적어두기                │
# └─────────────────────────────────────────────────────────────┘
def lesson3_event_sourcing():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 3: Event Sourcing - 이벤트 기록               │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Event Sourcing은 현재 상태를 저장하는 대신,
    # '무엇이 일어났는지'를 이벤트로 차곡차곡 기록합니다.
    # 은행 통장에 입출금 내역을 모두 적어두면,
    # 처음부터 다시 계산해서 현재 잔액을 알 수 있는 것과 같아요!

    event_store = ToyTopic("account-events")

    # 이벤트 기록
    events = [
        {"type": "계좌개설", "amount": 0},
        {"type": "입금", "amount": 100000},
        {"type": "입금", "amount": 50000},
        {"type": "출금", "amount": -30000},
        {"type": "입금", "amount": 20000},
        {"type": "출금", "amount": -15000},
    ]

    print("  [이벤트 기록]")
    for event in events:
        event_store.produce("account:1001", str(event))
        print(f"    {event['type']:8s} {event['amount']:+,}원")

    # 현재 상태 재구성: 이벤트를 처음부터 다시 재생
    balance = 0
    print("\n  [상태 재구성] 이벤트를 처음부터 재생:")
    for record in event_store.partitions[0]:
        event = eval(record["value"])
        balance += event["amount"]
        print(f"    {event['type']:8s} -> 잔액: {balance:,}원")

    print(f"\n  최종 잔액: {balance:,}원")
    print("  -> 모든 변경 이력이 남아있어 '왜 이 잔액이 되었는지' 추적 가능!")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 4: CQRS - 읽기와 쓰기를 분리                          │
# │  비유: 도서관에서 등록(쓰기)과 검색(읽기) 창구를 분리          │
# └─────────────────────────────────────────────────────────────┘
def lesson4_cqrs():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 4: CQRS - 읽기와 쓰기를 분리                  │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # CQRS = Command Query Responsibility Segregation
    # 쓰기(Command)와 읽기(Query)를 분리하는 패턴입니다.
    # 도서관에서 등록 창구(쓰기)와 검색 창구(읽기)를 나누는 것과 같아요!

    # Command (쓰기) -> Kafka 이벤트
    command_topic = ToyTopic("product-commands")

    # Query (읽기) -> 읽기 전용 DB (물화된 뷰)
    read_db = {}  # 읽기 최적화된 저장소

    # 1. Command 처리 (쓰기)
    commands = [
        {"cmd": "CREATE", "id": "P001", "name": "노트북", "price": 1200000},
        {"cmd": "CREATE", "id": "P002", "name": "마우스", "price": 25000},
        {"cmd": "UPDATE_PRICE", "id": "P001", "price": 1100000},
    ]

    print("  [Command 쓰기]")
    for cmd in commands:
        command_topic.produce(cmd["id"], str(cmd))
        print(f"    {cmd['cmd']} -> {cmd}")

    # 2. 이벤트를 소비해서 읽기 DB 업데이트
    print("\n  [이벤트 소비 -> 읽기 DB 업데이트]")
    for partition in command_topic.partitions:
        for record in partition:
            cmd = eval(record["value"])
            if cmd["cmd"] == "CREATE":
                read_db[cmd["id"]] = {"name": cmd["name"], "price": cmd["price"]}
            elif cmd["cmd"] == "UPDATE_PRICE":
                if cmd["id"] in read_db:
                    read_db[cmd["id"]]["price"] = cmd["price"]
            print(f"    적용: {cmd['cmd']} {cmd['id']}")

    # 3. Query (읽기) - 빠르게 조회
    print("\n  [Query 읽기] 읽기 DB에서 즉시 조회:")
    for pid, info in read_db.items():
        print(f"    {pid}: {info['name']} - {info['price']:,}원")
    print("  -> 쓰기는 이벤트 기록, 읽기는 최적화된 DB에서!")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 5: Consumer Lag 모니터링                               │
# │  비유: 급식 대기줄 길이 - 줄이 길어지면 조리 인원 추가!       │
# └─────────────────────────────────────────────────────────────┘
def lesson5_consumer_lag():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 5: Consumer Lag 모니터링                      │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Consumer Lag = 프로듀서가 보낸 메시지 수 - 컨슈머가 처리한 메시지 수
    # 급식 대기줄 길이와 같아요. 줄이 계속 길어지면 조리 인원을 추가해야 합니다!
    # Lag이 계속 증가하면 컨슈머를 늘리거나 처리 속도를 개선해야 합니다.

    topic = ToyTopic("user-events", partitions=3)
    consumer = ToyConsumer("analytics-consumer", topic)

    # 프로듀서가 15개 메시지 생성
    for i in range(15):
        topic.produce(f"user_{i % 5}", f"event_{i}")

    print(f"  토픽 전체 메시지: {topic.total_records()}개")
    print(f"  초기 Lag: {consumer.lag()}개")

    # 컨슈머가 일부만 처리
    processed = 0
    for p in range(3):
        for _ in range(2):
            record = consumer.poll(p)
            if record:
                processed += 1

    print(f"  처리 후: {processed}개 처리, Lag: {consumer.lag()}개")
    print()

    # Lag 모니터링 대시보드
    print("  [모니터링 대시보드]")
    for p in range(3):
        latest = len(topic.partitions[p])
        current = consumer.offsets[p]
        lag = latest - current
        bar = "#" * lag + "." * current
        print(f"    파티션 {p}: [{bar}] lag={lag}, offset={current}/{latest}")

    print("\n  경고 기준:")
    print("    Lag < 100 -> 정상")
    print("    Lag 100~1000 -> 주의 (처리 속도 확인)")
    print("    Lag > 1000 -> 위험 (컨슈머 추가 필요!)")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 6: 파티션 전략                                        │
# └─────────────────────────────────────────────────────────────┘
def lesson6_partition_strategy():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 6: 파티션 전략                                │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 파티션을 어떻게 나누느냐에 따라 순서 보장과 처리량이 달라집니다!

    topic = ToyTopic("orders", partitions=4)

    # 키 기반 파티셔닝: 같은 키는 항상 같은 파티션
    orders = [
        ("user_A", "주문1"), ("user_B", "주문2"),
        ("user_A", "주문3"), ("user_C", "주문4"),
        ("user_B", "주문5"), ("user_A", "주문6"),
    ]

    print("  [키 기반 파티셔닝] 같은 사용자 -> 같은 파티션:")
    for key, value in orders:
        p, offset = topic.produce(key, value)
        print(f"    key={key}, value={value} -> 파티션 {p}")

    print("\n  파티션별 데이터 분포:")
    for i, partition in enumerate(topic.partitions):
        if partition:
            keys = [r["key"] for r in partition]
            print(f"    파티션 {i}: {keys}")
        else:
            print(f"    파티션 {i}: (비어있음)")

    print()
    print("  ┌──────────────┬──────────────────────────────────────┐")
    print("  │ 전략          │ 설명                                 │")
    print("  ├──────────────┼──────────────────────────────────────┤")
    print("  │ 키 기반       │ 같은 키 -> 같은 파티션 (순서 보장)    │")
    print("  │ 라운드로빈    │ 순서대로 돌아가며 배분 (균등 분산)    │")
    print("  │ 커스텀        │ 비즈니스 로직으로 파티션 결정         │")
    print("  └──────────────┴──────────────────────────────────────┘")
    print()


def main():
    print("=" * 72)
    print("  Kafka 08단계: 프로덕션 패턴")
    print("=" * 72)
    print()

    lesson1_dead_letter_queue()
    lesson2_retry_topic()
    lesson3_event_sourcing()
    lesson4_cqrs()
    lesson5_consumer_lag()
    lesson6_partition_strategy()


if __name__ == "__main__":
    main()
