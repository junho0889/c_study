"""
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  RabbitMQ 07단계: 신뢰성 (Reliability)                          ■
■  Publisher Confirms, Consumer ACK/NACK, 영속성(Durable/Persistent),■
■  Prefetch Count, QoS                                           ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
"""

import random
import time
from collections import deque


# ============================================================
#  토이 RabbitMQ: 신뢰성 기능 포함
# ============================================================
class ReliableQueue:
    """신뢰성 기능을 갖춘 큐"""

    def __init__(self, name, durable=False, max_unacked=None):
        self.name = name
        self.durable = durable          # 영속성 (서버 재시작 후 복구)
        self.messages = deque()
        self.unacked = {}               # {delivery_tag: message} ACK 대기 중
        self.next_tag = 1
        self.max_unacked = max_unacked  # prefetch count
        self.disk_log = []              # 영속 큐의 디스크 저장 시뮬레이션

    def publish(self, body, persistent=False):
        msg = {
            "body": body,
            "persistent": persistent,    # 메시지 영속성
            "timestamp": time.time(),
        }
        self.messages.append(msg)
        if self.durable and persistent:
            self.disk_log.append(msg)
        return True

    def consume(self):
        """메시지를 가져오되 ACK 전까지 unacked에 보관"""
        if self.max_unacked and len(self.unacked) >= self.max_unacked:
            return None  # prefetch 제한 초과

        if not self.messages:
            return None

        msg = self.messages.popleft()
        tag = self.next_tag
        self.next_tag += 1
        self.unacked[tag] = msg
        return tag, msg

    def ack(self, delivery_tag):
        """처리 완료 확인 - 메시지를 최종 삭제"""
        if delivery_tag in self.unacked:
            del self.unacked[delivery_tag]
            return True
        return False

    def nack(self, delivery_tag, requeue=True):
        """처리 거부"""
        if delivery_tag in self.unacked:
            msg = self.unacked.pop(delivery_tag)
            if requeue:
                self.messages.appendleft(msg)  # 큐 앞에 다시 넣기
            return True
        return False

    def recover_from_disk(self):
        """서버 재시작 후 디스크에서 복구"""
        self.messages = deque(self.disk_log)
        self.unacked = {}
        return len(self.messages)


class ReliablePublisher:
    """Publisher Confirms를 지원하는 발행자"""

    def __init__(self, queue):
        self.queue = queue
        self.confirmed = []
        self.failed = []

    def publish_with_confirm(self, body, persistent=False, fail_rate=0.0):
        """발행 후 브로커의 확인(confirm)을 받는다."""
        # 네트워크 실패 시뮬레이션
        if random.random() < fail_rate:
            self.failed.append(body)
            return False

        success = self.queue.publish(body, persistent=persistent)
        if success:
            self.confirmed.append(body)
        else:
            self.failed.append(body)
        return success


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 1: Publisher Confirms - 메시지가 잘 도착했는지 확인    │
# │  비유: 등기우편 - 받는 사람 서명을 받아야 배달 완료            │
# └─────────────────────────────────────────────────────────────┘
def lesson1_publisher_confirms():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 1: Publisher Confirms                         │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Publisher Confirms: 메시지가 브로커에 잘 저장되었는지 확인합니다.
    # 등기우편처럼 '받았습니다' 서명을 받아야 배달 완료로 처리합니다.
    # 확인을 못 받으면 재전송합니다.

    random.seed(42)
    queue = ReliableQueue("order_queue")
    publisher = ReliablePublisher(queue)

    messages = ["주문1001", "주문1002", "주문1003", "주문1004", "주문1005"]

    print("  [Publisher Confirms] 메시지 발행 (20% 실패율 시뮬레이션):")
    for msg in messages:
        success = publisher.publish_with_confirm(msg, fail_rate=0.2)
        print(f"    {msg}: {'확인(ACK)' if success else '실패(NACK) -> 재전송 필요'}")

    # 실패한 메시지 재전송
    if publisher.failed:
        print(f"\n  [재전송] 실패 메시지 {len(publisher.failed)}개:")
        for msg in publisher.failed:
            success = publisher.publish_with_confirm(msg, fail_rate=0)
            print(f"    {msg}: {'재전송 성공' if success else '재전송 실패'}")

    print(f"\n  최종 확인: {len(publisher.confirmed)}개, 큐 크기: {len(queue.messages)}")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 2: Consumer ACK/NACK - 처리 완료 보고                 │
# │  비유: 숙제 제출 - '다 했어요(ACK)' 또는 '못 했어요(NACK)'   │
# └─────────────────────────────────────────────────────────────┘
def lesson2_consumer_ack_nack():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 2: Consumer ACK/NACK                          │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # ACK: '이 메시지 잘 처리했어요!' -> 큐에서 영구 삭제
    # NACK: '이 메시지 처리 못 했어요!' -> 다시 큐에 넣거나 버리기
    # 비유: 숙제를 '다 했어요(ACK)' 또는 '못 했어요(NACK)'라고 보고하는 것!

    queue = ReliableQueue("task_queue")
    queue.publish("이메일 발송")
    queue.publish("결제 처리")
    queue.publish("파일 변환 (에러)")
    queue.publish("알림 전송")

    print("  메시지 처리:")
    processed = 0
    requeued = 0

    for _ in range(5):
        result = queue.consume()
        if result is None:
            break
        tag, msg = result

        # 에러가 포함된 메시지는 NACK
        if "에러" in msg["body"]:
            queue.nack(tag, requeue=True)
            print(f"    tag={tag}: '{msg['body']}' -> NACK (큐에 다시 넣기)")
            requeued += 1
        else:
            queue.ack(tag)
            print(f"    tag={tag}: '{msg['body']}' -> ACK (처리 완료)")
            processed += 1

    print(f"\n  처리 완료: {processed}개, 재큐잉: {requeued}개")
    print(f"  큐 남은 메시지: {len(queue.messages)}개")
    print(f"  ACK 대기(unacked): {len(queue.unacked)}개")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 3: 메시지 영속성 - 서버가 꺼져도 메시지 보존           │
# │  비유: 중요한 서류는 서랍이 아니라 금고에 보관               │
# └─────────────────────────────────────────────────────────────┘
def lesson3_persistence():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 3: 메시지 영속성 (Persistence)                │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 영속성은 서버가 재시작되어도 메시지가 사라지지 않게 하는 것입니다.
    # 두 가지를 모두 설정해야 합니다:
    # 1. durable=true: 큐 자체를 디스크에 기록 (금고 만들기)
    # 2. persistent=true: 메시지를 디스크에 기록 (금고에 넣기)

    # 비영속 큐
    temp_queue = ReliableQueue("temp_queue", durable=False)
    temp_queue.publish("임시 메시지 1")
    temp_queue.publish("임시 메시지 2")

    # 영속 큐
    durable_queue = ReliableQueue("durable_queue", durable=True)
    durable_queue.publish("영속 메시지 1", persistent=True)
    durable_queue.publish("영속 메시지 2", persistent=True)
    durable_queue.publish("비영속 메시지 3", persistent=False)  # 영속 큐지만 메시지는 비영속

    print("  서버 재시작 전:")
    print(f"    비영속 큐: {len(temp_queue.messages)}개")
    print(f"    영속 큐: {len(durable_queue.messages)}개")

    # 서버 재시작 시뮬레이션
    temp_queue.messages.clear()  # 비영속 큐는 날아감
    recovered = durable_queue.recover_from_disk()  # 영속 큐는 디스크에서 복구

    print(f"\n  서버 재시작 후:")
    print(f"    비영속 큐: {len(temp_queue.messages)}개 (전부 사라짐!)")
    print(f"    영속 큐: {recovered}개 (디스크에서 복구)")
    for msg in durable_queue.messages:
        print(f"      - {msg['body']}")

    print()
    print("  ┌──────────────┬────────────────┬─────────────────────┐")
    print("  │ 설정          │ 큐 재시작 후    │ 비유                 │")
    print("  ├──────────────┼────────────────┼─────────────────────┤")
    print("  │ 둘 다 False  │ 큐+메시지 사라짐│ 칠판 (지우면 끝)     │")
    print("  │ durable만    │ 큐는 남지만     │ 빈 금고 (내용물 없음) │")
    print("  │   True       │ 메시지 사라짐   │                     │")
    print("  │ 둘 다 True   │ 큐+메시지 모두  │ 금고에 서류 보관     │")
    print("  │              │ 복구           │                     │")
    print("  └──────────────┴────────────────┴─────────────────────┘")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 4: Prefetch Count (QoS) - 한 번에 가져갈 수 있는 양   │
# │  비유: 뷔페에서 접시 하나만 들고 가서 먹고, 다시 가져오기     │
# └─────────────────────────────────────────────────────────────┘
def lesson4_prefetch():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 4: Prefetch Count (QoS)                       │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Prefetch Count는 소비자가 한 번에 가져갈 수 있는 ACK 안 된 메시지 수입니다.
    # 뷔페에서 접시 하나씩만 가져가는 규칙과 같아요.
    # 한꺼번에 많이 가져가면 다른 소비자가 일을 못 하니까요!
    # basic_qos(prefetch_count=1)로 설정합니다.

    queue = ReliableQueue("work_queue", max_unacked=2)  # prefetch=2

    for i in range(6):
        queue.publish(f"작업_{i + 1}")

    print(f"  큐 메시지: {len(queue.messages)}개, prefetch_count=2")
    print()

    # 소비자가 prefetch 제한 안에서 가져감
    tags = []
    for i in range(4):
        result = queue.consume()
        if result:
            tag, msg = result
            tags.append(tag)
            print(f"  consume #{i + 1}: tag={tag}, '{msg['body']}' (unacked={len(queue.unacked)})")
        else:
            print(f"  consume #{i + 1}: 가져올 수 없음! (unacked={len(queue.unacked)}, 제한={queue.max_unacked})")

    # ACK하면 새 메시지를 가져올 수 있음
    print()
    queue.ack(tags[0])
    print(f"  tag={tags[0]} ACK 후:")
    result = queue.consume()
    if result:
        tag, msg = result
        print(f"  consume 성공: tag={tag}, '{msg['body']}' (unacked={len(queue.unacked)})")
    print()
    print("  prefetch_count 가이드:")
    print("    1: 공평한 분배 (느린 소비자에게 몰리지 않음)")
    print("    10~50: 적당한 처리량과 공평성 균형")
    print("    0(무제한): 최대 처리량 (but 불공평할 수 있음)")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 5: 신뢰성 체크리스트                                   │
# └─────────────────────────────────────────────────────────────┘
def lesson5_checklist():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 5: 신뢰성 체크리스트                          │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    print("  메시지를 절대 잃어버리지 않으려면:")
    print()
    print("  [발행자 측]")
    print("    1. Publisher Confirms 사용 (confirm 못 받으면 재전송)")
    print("    2. persistent=True로 메시지 전송")
    print()
    print("  [브로커 측]")
    print("    3. durable=True로 큐 선언")
    print("    4. 클러스터 미러링으로 큐 복제")
    print()
    print("  [소비자 측]")
    print("    5. auto_ack=False (수동 ACK)")
    print("    6. 처리 완료 후에만 ACK")
    print("    7. prefetch_count 적절히 설정")
    print()
    print("  ┌─────────────────────────────────────────────┐")
    print("  │  Publisher  ──confirm──>  Broker             │")
    print("  │             <──ack/nack──                   │")
    print("  │                           │                 │")
    print("  │                     durable queue           │")
    print("  │                     persistent msg          │")
    print("  │                           │                 │")
    print("  │                      Consumer               │")
    print("  │                    prefetch + ACK            │")
    print("  └─────────────────────────────────────────────┘")
    print()


def main():
    print("=" * 72)
    print("  RabbitMQ 07단계: 신뢰성 (Reliability)")
    print("=" * 72)
    print()

    random.seed(42)
    lesson1_publisher_confirms()
    lesson2_consumer_ack_nack()
    lesson3_persistence()
    lesson4_prefetch()
    lesson5_checklist()


if __name__ == "__main__":
    main()
