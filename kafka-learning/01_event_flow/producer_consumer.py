def produce_event(topic, order_id, status):
    event = {
        "offset": len(topic),
        "order_id": order_id,
        "status": status,
    }
    topic.append(event)
    return event


def lesson1_producer_appends_to_topic(topic):
    print("[레슨 1] Producer는 topic 끝에 이벤트를 차곡차곡 붙인다")
    print()

    for status in ["created", "paid", "shipped"]:
        event = produce_event(topic, order_id=101, status=status)
        print("  저장된 이벤트:", event)
    print()


def lesson2_consumer_reads_by_offset(topic):
    print("[레슨 2] Consumer는 앞에서 지우지 않고 offset으로 읽는다")
    print()

    consumer_offset = 0

    while consumer_offset < len(topic):
        event = topic[consumer_offset]
        print(f"  offset {consumer_offset} 읽기 -> {event}")
        consumer_offset += 1

    print("  설명: Kafka는 큐처럼 꺼내며 지우기보다, 로그를 읽고 '어디까지 읽었는지'를 기억합니다.")
    print()


def lesson3_another_consumer_can_read_again(topic):
    print("[레슨 3] 다른 소비자는 처음부터 다시 읽을 수도 있다")
    print()

    second_consumer_offset = 0
    print("  두 번째 소비자가 처음부터 다시 읽습니다.")
    while second_consumer_offset < len(topic):
        event = topic[second_consumer_offset]
        print(f"  second consumer -> {event['status']}")
        second_consumer_offset += 1
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("Kafka 01단계: Producer와 Consumer의 이벤트 흐름")
    print("=" * 72)
    print()

    message_topic = []
    lesson1_producer_appends_to_topic(message_topic)
    lesson2_consumer_reads_by_offset(message_topic)
    lesson3_another_consumer_can_read_again(message_topic)
