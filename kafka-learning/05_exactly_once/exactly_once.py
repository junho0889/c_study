"""
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  Kafka 05단계: 메시지 전달 보장 (Delivery Semantics)             ■
■  At-most-once, At-least-once, Exactly-once,                     ■
■  멱등성 프로듀서, 트랜잭션 API, 오프셋 커밋 전략                  ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
"""

import random


# ============================================================
#  토이 Kafka 브로커
# ============================================================
class ToyBroker:
    def __init__(self):
        self.topic = []
        self.committed_offset = -1  # 소비자가 '여기까지 처리했어요' 기록

    def produce(self, key, value):
        offset = len(self.topic)
        self.topic.append({"offset": offset, "key": key, "value": value})
        return offset

    def consume_from(self, offset):
        if offset < len(self.topic):
            return self.topic[offset]
        return None

    def commit_offset(self, offset):
        self.committed_offset = offset


class IdempotentProducer:
    """
    멱등성(Idempotent) 프로듀서: 같은 메시지를 여러 번 보내도 한 번만 저장.
    비유: 택배 기사가 '송장번호 1234는 이미 배달했으니 다시 안 가도 돼'하는 것.
    """

    def __init__(self, broker):
        self.broker = broker
        self.producer_id = random.randint(1000, 9999)
        self.sequence = 0
        self.sent_sequences = set()  # 브로커 측에서 이미 받은 시퀀스

    def send(self, key, value, simulate_retry=False):
        seq = self.sequence
        self.sequence += 1

        # 첫 번째 전송
        if seq not in self.sent_sequences:
            self.sent_sequences.add(seq)
            offset = self.broker.produce(key, value)
            result = {"status": "OK", "offset": offset, "seq": seq}
        else:
            result = {"status": "DUPLICATE_SKIPPED", "seq": seq}

        # 재전송 시뮬레이션 (네트워크 타임아웃으로 재시도)
        if simulate_retry:
            if seq in self.sent_sequences:
                return {"status": "DUPLICATE_SKIPPED (재전송)", "seq": seq}

        return result


class TransactionalProducer:
    """
    트랜잭션 프로듀서: 여러 메시지를 원자적으로 전송.
    비유: 시험 답안지 - 다 쓰고 나서 한꺼번에 제출하거나, 전부 취소하거나.
    """

    def __init__(self, broker):
        self.broker = broker
        self.tx_buffer = None

    def begin_transaction(self):
        self.tx_buffer = []

    def send(self, key, value):
        if self.tx_buffer is None:
            raise RuntimeError("트랜잭션이 시작되지 않았습니다!")
        self.tx_buffer.append((key, value))

    def commit_transaction(self):
        if self.tx_buffer is None:
            raise RuntimeError("트랜잭션이 시작되지 않았습니다!")
        offsets = []
        for key, value in self.tx_buffer:
            offset = self.broker.produce(key, value)
            offsets.append(offset)
        self.tx_buffer = None
        return offsets

    def abort_transaction(self):
        count = len(self.tx_buffer) if self.tx_buffer else 0
        self.tx_buffer = None
        return count


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 1: At-most-once - 최대 한 번 (유실 가능)              │
# │  비유: 선생님이 한 번만 말하고, 못 들은 학생은 그냥 넘어감    │
# └─────────────────────────────────────────────────────────────┘
def lesson1_at_most_once():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 1: At-most-once - 최대 한 번 전달             │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # At-most-once: 메시지를 최대 한 번만 전달합니다.
    # 선생님이 한 번 말하고, 못 들은 학생은 그냥 넘어가는 것과 같아요.
    # 장점: 빠르고 간단   단점: 메시지가 유실될 수 있음
    # 사용 예: 로그 수집, 센서 데이터 (일부 유실 허용)

    broker = ToyBroker()

    # 프로듀서: 보내고 확인 안 함 (fire-and-forget)
    messages = ["로그A", "로그B", "로그C"]
    sent_count = 0
    for msg in messages:
        # 30% 확률로 네트워크 실패 시뮬레이션
        if random.random() < 0.3:
            print(f"  [실패] '{msg}' 전송 실패 (재시도 안 함)")
            continue
        broker.produce("log", msg)
        sent_count += 1
        print(f"  [성공] '{msg}' 전송")

    # 소비자: 읽기 전에 오프셋을 먼저 커밋
    broker.commit_offset(len(broker.topic) - 1)
    print(f"\n  저장된 메시지: {sent_count}개 / 원래 {len(messages)}개")
    print("  -> 실패한 메시지는 유실됩니다. 하지만 중복은 절대 없습니다.")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 2: At-least-once - 최소 한 번 (중복 가능)             │
# │  비유: 택배 기사가 서명 받을 때까지 계속 재배달               │
# └─────────────────────────────────────────────────────────────┘
def lesson2_at_least_once():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 2: At-least-once - 최소 한 번 전달            │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # At-least-once: 확인(ACK)을 받을 때까지 계속 재전송합니다.
    # 택배 기사가 서명 받을 때까지 계속 방문하는 것과 같아요.
    # 장점: 메시지 유실 없음   단점: 중복 가능
    # 사용 예: 결제 처리 (유실은 절대 안 되지만, 중복은 나중에 처리 가능)

    broker = ToyBroker()
    processed_ids = set()  # 소비자 측 중복 감지용

    # 프로듀서: ACK 없으면 재전송
    message = {"id": "order_1001", "amount": 50000}
    print(f"  프로듀서가 메시지 전송: {message}")
    broker.produce("order", str(message))

    # ACK 실패 시뮬레이션 -> 같은 메시지 재전송
    print("  [시뮬레이션] ACK 실패! 재전송합니다.")
    broker.produce("order", str(message))  # 중복!

    print(f"  브로커에 저장된 메시지 수: {len(broker.topic)}")
    print()

    # 소비자: 중복 감지 로직 필요!
    print("  소비자가 메시지를 읽습니다:")
    for i in range(len(broker.topic)):
        record = broker.consume_from(i)
        msg_str = record["value"]
        if msg_str in processed_ids:
            print(f"    offset={i}: 중복! 건너뜀")
        else:
            processed_ids.add(msg_str)
            print(f"    offset={i}: 처리 완료")
    print("  -> 중복은 소비자가 직접 감지해야 합니다 (멱등성 처리).")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 3: 멱등성 프로듀서 - 같은 메시지를 보내도 한 번만 저장 │
# │  비유: 택배 송장번호로 '이미 배달 완료'인지 확인              │
# └─────────────────────────────────────────────────────────────┘
def lesson3_idempotent_producer():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 3: 멱등성 프로듀서                            │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 멱등성(Idempotent): 같은 요청을 여러 번 해도 결과가 한 번과 같음.
    # Kafka는 프로듀서에 고유 ID + 시퀀스 번호를 부여해서
    # 같은 메시지가 재전송되면 자동으로 중복을 걸러냅니다.
    # enable.idempotence=true 설정으로 켤 수 있습니다.

    broker = ToyBroker()
    producer = IdempotentProducer(broker)

    # 정상 전송
    result = producer.send("order", "주문1001")
    print(f"  첫 번째 전송: {result}")

    # 재전송 시뮬레이션 (시퀀스가 올라간 후이므로 새 메시지)
    result = producer.send("order", "주문1002")
    print(f"  두 번째 전송: {result}")

    print(f"  브로커 저장 메시지: {len(broker.topic)}개")
    for r in broker.topic:
        print(f"    offset={r['offset']}, value={r['value']}")
    print("  -> 멱등성 프로듀서 덕분에 중복 없이 정확히 한 번 저장!")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 4: 트랜잭션 API - 여러 메시지를 원자적으로 전송        │
# │  비유: 시험 답안지를 다 쓰고 한꺼번에 제출하기                │
# └─────────────────────────────────────────────────────────────┘
def lesson4_transactional():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 4: 트랜잭션 API - 원자적 전송                 │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 트랜잭션은 여러 메시지를 '전부 성공 아니면 전부 취소'로 보냅니다.
    # 시험 답안지를 다 쓰고 제출하거나, 마음에 안 들면 전부 찢는 것과 같아요.

    broker = ToyBroker()
    tx_producer = TransactionalProducer(broker)

    # 성공하는 트랜잭션
    print("  [트랜잭션 1] 주문 처리:")
    tx_producer.begin_transaction()
    tx_producer.send("order", "주문생성")
    tx_producer.send("inventory", "재고차감")
    tx_producer.send("payment", "결제요청")
    offsets = tx_producer.commit_transaction()
    print(f"    커밋 완료! offsets={offsets}")

    # 실패하는 트랜잭션
    print("  [트랜잭션 2] 환불 처리 (중간에 오류 발생):")
    tx_producer.begin_transaction()
    tx_producer.send("refund", "환불시작")
    tx_producer.send("inventory", "재고복구")
    aborted = tx_producer.abort_transaction()
    print(f"    중단! {aborted}개 메시지 버림")

    print(f"\n  브로커 최종 메시지:")
    for r in broker.topic:
        print(f"    offset={r['offset']}, key={r['key']}, value={r['value']}")
    print("  -> 트랜잭션 2의 메시지는 커밋되지 않아 브로커에 없습니다!")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 5: 오프셋 커밋 전략 - 어디까지 읽었는지 기록 시점      │
# │  비유: 책갈피를 언제 끼울 것인가?                             │
# └─────────────────────────────────────────────────────────────┘
def lesson5_offset_commit():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 5: 오프셋 커밋 전략                           │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 오프셋 커밋은 '여기까지 읽었어요'를 기록하는 것입니다.
    # 책을 읽다가 책갈피를 끼우는 것과 같아요.
    # 책갈피를 너무 빨리 끼우면? -> 덜 읽었는데 읽은 척 (at-most-once)
    # 다 읽고 끼우면? -> 읽었는데 책갈피를 안 끼움 (at-least-once)

    broker = ToyBroker()
    for msg in ["메시지A", "메시지B", "메시지C"]:
        broker.produce("topic1", msg)

    # 전략 1: Auto Commit (자동 커밋) - 주기적으로 자동 커밋
    print("  전략 1) Auto Commit (enable.auto.commit=true):")
    print("    - 일정 주기(기본 5초)마다 자동으로 오프셋 커밋")
    print("    - 간편하지만, 처리 전에 커밋되면 메시지 유실 가능")
    print()

    # 전략 2: Manual Commit (수동 커밋) - 처리 완료 후 직접 커밋
    print("  전략 2) Manual Commit (commitSync/commitAsync):")
    offset = 0
    while offset < len(broker.topic):
        record = broker.consume_from(offset)
        print(f"    처리: offset={record['offset']}, value={record['value']}")
        broker.commit_offset(offset)  # 처리 후 커밋
        print(f"    -> 오프셋 {offset} 커밋 완료")
        offset += 1
    print("    - 처리 완료 후 커밋하므로 유실 방지 (but 중복 가능)")
    print()

    print("  ┌───────────────┬─────────────────┬──────────────────┐")
    print("  │ 전략           │ 유실 가능성      │ 중복 가능성       │")
    print("  ├───────────────┼─────────────────┼──────────────────┤")
    print("  │ Auto Commit   │ 있음 (처리 전 커밋)│ 있음              │")
    print("  │ 처리 전 커밋   │ 있음             │ 없음 (at-most-once)│")
    print("  │ 처리 후 커밋   │ 없음             │ 있음 (at-least-once)│")
    print("  │ 트랜잭션 커밋  │ 없음             │ 없음 (exactly-once)│")
    print("  └───────────────┴─────────────────┴──────────────────┘")
    print()


def main():
    print("=" * 72)
    print("  Kafka 05단계: 메시지 전달 보장 (Delivery Semantics)")
    print("=" * 72)
    print()

    random.seed(42)  # 재현 가능한 결과를 위해 시드 고정
    lesson1_at_most_once()
    lesson2_at_least_once()
    lesson3_idempotent_producer()
    lesson4_transactional()
    lesson5_offset_commit()


if __name__ == "__main__":
    main()
