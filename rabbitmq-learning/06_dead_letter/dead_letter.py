"""
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  RabbitMQ 06단계: Dead Letter Exchange (DLX)                    ■
■  DLX, 메시지 TTL, max-length 큐, 지연 재시도, 독약 메시지 처리   ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
"""

import time
from collections import deque


# ============================================================
#  토이 RabbitMQ: DLX 기능 포함
# ============================================================
class ToyQueue:
    """큐 하나를 나타내는 클래스"""

    def __init__(self, name, max_length=None, message_ttl=None, dlx=None):
        self.name = name
        self.messages = deque()
        self.max_length = max_length        # 큐 최대 길이
        self.message_ttl = message_ttl      # 메시지 유효 시간(초)
        self.dlx = dlx                      # Dead Letter Exchange

    def publish(self, message, timestamp=None):
        msg = {
            "body": message,
            "timestamp": timestamp or time.time(),
            "retry_count": 0,
        }
        self.messages.append(msg)

        # max_length 초과 시 오래된 메시지를 DLX로 이동
        while self.max_length and len(self.messages) > self.max_length:
            expired = self.messages.popleft()
            if self.dlx:
                expired["reason"] = "max-length 초과"
                self.dlx.receive(expired)

    def consume(self, current_time=None):
        current_time = current_time or time.time()

        while self.messages:
            msg = self.messages[0]
            # TTL 확인
            if self.message_ttl:
                age = current_time - msg["timestamp"]
                if age > self.message_ttl:
                    expired = self.messages.popleft()
                    if self.dlx:
                        expired["reason"] = f"TTL 만료 ({age:.0f}초 > {self.message_ttl}초)"
                        self.dlx.receive(expired)
                    continue
            return self.messages.popleft()
        return None

    def nack(self, message):
        """메시지 처리 거부 -> DLX로 이동"""
        if self.dlx:
            message["reason"] = "NACK (처리 거부)"
            self.dlx.receive(message)


class DeadLetterExchange:
    """
    Dead Letter Exchange: 처리할 수 없는 메시지를 모아두는 곳.
    비유: 학교 분실물 보관함 - 주인을 찾지 못한 물건을 모아둡니다.
    """

    def __init__(self, name):
        self.name = name
        self.dead_letters = []

    def receive(self, message):
        self.dead_letters.append(message)

    def get_all(self):
        return list(self.dead_letters)


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 1: Dead Letter Exchange (DLX) 기본 개념               │
# │  비유: 분실물 보관함 - 처리 못한 메시지를 따로 모아두기       │
# └─────────────────────────────────────────────────────────────┘
def lesson1_dlx_basics():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 1: DLX 기본 개념                              │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # DLX는 '처리할 수 없는 메시지'가 가는 특별한 교환기입니다.
    # 학교 분실물 보관함처럼, 주인(처리자)을 찾지 못한 메시지를 모아둡니다.
    # 메시지가 DLX로 가는 3가지 경우:
    # 1. 소비자가 NACK(거부)한 경우
    # 2. 메시지 TTL이 만료된 경우
    # 3. 큐 길이 제한을 초과한 경우

    dlx = DeadLetterExchange("my_dlx")
    queue = ToyQueue("work_queue", dlx=dlx)

    # 메시지 발행
    queue.publish("정상 메시지 1")
    queue.publish("독약 메시지 (파싱 불가)")
    queue.publish("정상 메시지 2")

    # 소비자가 메시지 처리
    print("  메시지 처리:")
    for _ in range(3):
        msg = queue.consume()
        if msg:
            if "독약" in msg["body"]:
                print(f"    [NACK] '{msg['body']}' -> 처리 실패! DLX로 이동")
                queue.nack(msg)
            else:
                print(f"    [ACK]  '{msg['body']}' -> 처리 성공")

    print(f"\n  DLX에 모인 메시지: {len(dlx.get_all())}개")
    for dl in dlx.get_all():
        print(f"    사유: {dl['reason']}, 내용: {dl['body']}")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 2: 메시지 TTL - 유통기한이 지난 메시지 자동 제거       │
# │  비유: 편의점 도시락처럼 유통기한이 지나면 폐기               │
# └─────────────────────────────────────────────────────────────┘
def lesson2_message_ttl():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 2: 메시지 TTL - 유통기한 관리                 │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 메시지 TTL은 메시지의 유통기한입니다.
    # 편의점 도시락처럼 유통기한이 지나면 자동으로 폐기(DLX 이동)됩니다.
    # 오래된 주문, 만료된 인증 코드 등에 유용합니다.

    dlx = DeadLetterExchange("ttl_dlx")
    queue = ToyQueue("ttl_queue", message_ttl=5, dlx=dlx)  # 5초 TTL

    base_time = time.time()

    # 시간대별 메시지 추가
    queue.publish("인증코드: 1234", timestamp=base_time - 10)  # 10초 전 (만료)
    queue.publish("인증코드: 5678", timestamp=base_time - 3)   # 3초 전 (유효)
    queue.publish("인증코드: 9012", timestamp=base_time - 7)   # 7초 전 (만료)

    print("  메시지 소비 시도:")
    while True:
        msg = queue.consume(current_time=base_time)
        if msg is None:
            break
        print(f"    [유효] {msg['body']}")

    print(f"\n  TTL 만료로 DLX에 간 메시지:")
    for dl in dlx.get_all():
        print(f"    {dl['body']} - {dl['reason']}")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 3: max-length 큐 - 큐 크기 제한                       │
# │  비유: 사물함이 3칸뿐이면 새 물건이 오면 오래된 것부터 빼기   │
# └─────────────────────────────────────────────────────────────┘
def lesson3_max_length():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 3: max-length 큐 - 크기 제한                  │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # max-length는 큐에 들어갈 수 있는 최대 메시지 수입니다.
    # 사물함이 3칸뿐이면, 4번째 물건이 오면 가장 오래된 물건을 빼야 합니다.
    # 빠진 물건은 DLX로 갑니다.

    dlx = DeadLetterExchange("overflow_dlx")
    queue = ToyQueue("limited_queue", max_length=3, dlx=dlx)

    print("  큐 최대 길이: 3")
    for i in range(1, 6):
        queue.publish(f"메시지_{i}")
        overflow_count = len(dlx.get_all())
        print(f"  메시지_{i} 추가 -> 큐 크기: {len(queue.messages)}, DLX: {overflow_count}개")

    print(f"\n  큐에 남은 메시지: {[m['body'] for m in queue.messages]}")
    print(f"  DLX로 밀려난 메시지: {[m['body'] for m in dlx.get_all()]}")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 4: 지연 재시도 - DLX + TTL로 나중에 다시 처리          │
# │  비유: 실패한 택배를 2시간 후에 다시 배달하기                 │
# └─────────────────────────────────────────────────────────────┘
def lesson4_delayed_retry():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 4: 지연 재시도 - DLX + TTL 활용               │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 지연 재시도는 실패한 메시지를 일정 시간 후에 다시 처리하는 패턴입니다.
    # 택배 배달 실패 시 '2시간 후 재배달'하는 것과 같아요!
    # 구현: 실패 -> 대기 큐(TTL 설정) -> TTL 만료 -> DLX를 통해 원래 큐로 복귀

    print("  지연 재시도 흐름:")
    print("    1. 메시지 처리 실패")
    print("    2. retry 큐로 이동 (TTL=30초)")
    print("    3. 30초 후 TTL 만료")
    print("    4. DLX를 통해 원래 큐로 복귀")
    print("    5. 다시 처리 시도")
    print()

    # 시뮬레이션
    retry_attempts = {}  # 메시지별 재시도 횟수
    max_retries = 3
    processed = []
    dead_letters = []

    messages = ["주문_A (정상)", "주문_B (일시 오류)", "주문_C (영구 오류)"]

    for msg in messages:
        retry_attempts[msg] = 0

        while retry_attempts[msg] <= max_retries:
            attempt = retry_attempts[msg] + 1

            if "정상" in msg:
                processed.append(msg)
                print(f"  [{msg}] 시도 #{attempt}: 성공!")
                break
            elif "일시 오류" in msg and attempt >= 3:
                processed.append(msg)
                print(f"  [{msg}] 시도 #{attempt}: 성공! (3번째에 복구)")
                break
            elif "영구 오류" in msg and attempt > max_retries:
                dead_letters.append(msg)
                print(f"  [{msg}] 시도 #{attempt}: 최종 실패 -> DLQ로 이동")
                break
            else:
                delay = 2 ** retry_attempts[msg]  # 지수 백오프
                print(f"  [{msg}] 시도 #{attempt}: 실패! {delay}초 후 재시도")
                retry_attempts[msg] += 1

    print(f"\n  처리 성공: {processed}")
    print(f"  최종 실패(DLQ): {dead_letters}")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 5: 독약(Poison) 메시지 처리                           │
# │  비유: 절대 풀 수 없는 문제 - 계속 틀리면 그냥 넘기기        │
# └─────────────────────────────────────────────────────────────┘
def lesson5_poison_message():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 5: 독약(Poison) 메시지 처리                   │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 독약 메시지: 어떻게 해도 처리할 수 없는 메시지.
    # 잘못된 형식, 깨진 데이터 등이 원인입니다.
    # 계속 재시도하면 큐가 막히므로, 일정 횟수 실패 후 DLQ로 보내야 합니다.
    # 절대 풀 수 없는 수학 문제를 계속 시도하면 시간만 낭비하니 넘기는 것과 같아요!

    dlx = DeadLetterExchange("poison_dlx")
    queue = ToyQueue("work_queue", dlx=dlx)

    messages = [
        {"body": '{"order_id": 1001, "amount": 50000}', "retry_count": 0},
        {"body": '깨진 JSON 데이터 @#$%', "retry_count": 0},     # 독약!
        {"body": '{"order_id": 1003, "amount": 30000}', "retry_count": 0},
    ]

    print("  메시지 처리 (최대 3회 재시도):")
    for msg in messages:
        success = False
        for attempt in range(1, 4):
            try:
                # JSON 파싱 시도
                if "@#$%" in msg["body"]:
                    raise ValueError("JSON 파싱 실패")
                print(f"    [{msg['body'][:30]}...] 시도 #{attempt}: 성공!")
                success = True
                break
            except ValueError as e:
                print(f"    [{msg['body'][:30]}...] 시도 #{attempt}: {e}")
                msg["retry_count"] += 1

        if not success:
            msg["reason"] = f"독약 메시지 - {msg['retry_count']}회 실패"
            dlx.receive(msg)
            print(f"    -> DLQ로 이동!")

    print(f"\n  DLQ 내용:")
    for dl in dlx.get_all():
        print(f"    {dl['body'][:30]}... - {dl['reason']}")
    print()


def main():
    print("=" * 72)
    print("  RabbitMQ 06단계: Dead Letter Exchange (DLX)")
    print("=" * 72)
    print()

    lesson1_dlx_basics()
    lesson2_message_ttl()
    lesson3_max_length()
    lesson4_delayed_retry()
    lesson5_poison_message()


if __name__ == "__main__":
    main()
