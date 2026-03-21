from collections import deque


def lesson1_enqueue_messages(queue):
    print("[레슨 1] 생산자가 큐 뒤쪽에 차례대로 메시지 넣기")
    print()

    # 큐는 놀이공원 줄과 비슷합니다.
    # 먼저 줄 선 사람이 먼저 들어가므로 append로 뒤에 붙이고,
    # 나중에 popleft로 앞에서 꺼내면 FIFO(먼저 들어온 것이 먼저 나감)가 됩니다.
    queue.append({"student": "민수", "task": "수학 숙제 사진 업로드"})
    queue.append({"student": "지우", "task": "영어 단어 시험 결과 전송"})
    queue.append({"student": "서연", "task": "과학 실험 보고서 제출"})

    for order, message in enumerate(queue, start=1):
        print(f"  줄 번호 {order}: {message['student']} -> {message['task']}")
    print()


def lesson2_consume_messages_in_order(queue):
    print("[레슨 2] 소비자가 앞에서 하나씩 꺼내 처리하기")
    print()

    # RabbitMQ의 가장 기본 그림은 "넣는 사람 1명, 꺼내는 사람 1명"입니다.
    # 상자 창고에서 맨 앞 상자부터 꺼내는 것처럼 앞에서부터 처리합니다.
    while queue:
        message = queue.popleft()
        print(f"  처리 중: {message['student']} / {message['task']}")
    print("  남은 메시지 수:", len(queue))
    print()


def lesson3_real_life_example():
    print("[레슨 3] 왜 큐가 필요한지 실제 상황으로 보기")
    print()

    lunch_queue = deque()

    # 급식실에서 주문이 한꺼번에 몰려도,
    # 큐에 넣어 두면 조리 담당이 자기 속도대로 차근차근 처리할 수 있습니다.
    for menu in ["김밥 1줄", "떡볶이 1인분", "우유 1개"]:
        lunch_queue.append(menu)

    first_order = lunch_queue.popleft()
    print("  먼저 들어온 주문:", first_order)
    print("  아직 기다리는 주문들:", list(lunch_queue))
    print("  실사용 비유: 웹 서버는 주문을 바로 다 못 처리할 때 큐에 넣고 천천히 꺼냅니다.")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("RabbitMQ 01단계: 큐의 가장 기본 흐름")
    print("=" * 72)
    print()

    homework_queue = deque()
    lesson1_enqueue_messages(homework_queue)
    lesson2_consume_messages_in_order(homework_queue)
    lesson3_real_life_example()
