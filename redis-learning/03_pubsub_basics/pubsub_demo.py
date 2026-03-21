class PubSubBus:
    def __init__(self):
        self.channels = {}

    def subscribe(self, channel, listener):
        self.channels.setdefault(channel, []).append(listener)

    def publish(self, channel, message):
        for listener in self.channels.get(channel, []):
            listener(message)


def lesson1_multiple_subscribers_hear_the_same_message():
    print("[레슨 1] 같은 채널을 듣는 여러 구독자가 동시에 메시지를 받기")
    print()

    bus = PubSubBus()
    bus.subscribe("school-bell", lambda message: print("  1반 수신:", message))
    bus.subscribe("school-bell", lambda message: print("  2반 수신:", message))
    bus.subscribe("school-bell", lambda message: print("  방송실 기록:", message))

    bus.publish("school-bell", "쉬는 시간이 끝났습니다. 자리에 앉아 주세요.")
    print()


def lesson2_no_history_for_late_subscriber():
    print("[레슨 2] 늦게 구독한 사람은 예전 방송을 자동으로 받지 못함")
    print()

    bus = PubSubBus()
    bus.subscribe("notice", lambda message: print("  먼저 듣고 있던 화면:", message))

    bus.publish("notice", "첫 번째 공지")

    # 여기서 새 구독자는 첫 번째 공지를 못 듣습니다.
    # Redis Pub/Sub은 기본적으로 메시지 보관함이 아니라 "실시간 방송"에 가깝기 때문입니다.
    bus.subscribe("notice", lambda message: print("  늦게 들어온 화면:", message))
    bus.publish("notice", "두 번째 공지")
    print()


def lesson3_where_pubsub_fits():
    print("[레슨 3] 어떤 문제에 잘 맞는가")
    print()
    print("  - 채팅 알림")
    print("  - 실시간 대시보드 갱신")
    print("  - 게임 방 안의 상태 전파")
    print("  반대로 '나중에라도 꼭 다시 받아야 하는 일'은 큐나 스트림이 더 어울립니다.")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("Redis 03단계: Pub/Sub 기초")
    print("=" * 72)
    print()

    lesson1_multiple_subscribers_hear_the_same_message()
    lesson2_no_history_for_late_subscriber()
    lesson3_where_pubsub_fits()
