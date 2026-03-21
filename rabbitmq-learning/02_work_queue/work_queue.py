from collections import deque


def lesson1_round_robin_distribution():
    print("[레슨 1] 여러 작업자를 번갈아 쓰는 Round Robin")
    print()

    workers = ["worker-1", "worker-2"]
    tasks = [
        "색종이 자르기",
        "이름표 붙이기",
        "완성품 상자 담기",
        "배송 스티커 붙이기",
    ]

    # index % 작업자 수를 쓰면
    # 0, 1, 0, 1 ... 순서로 반복되어 공평하게 번갈아 배정됩니다.
    for index, task in enumerate(tasks):
        worker = workers[index % len(workers)]
        print(f"  {task} -> {worker}")
    print()


def lesson2_ack_and_requeue():
    print("[레슨 2] ACK가 없으면 일이 사라질 수 있고, ACK가 있으면 다시 맡길 수 있음")
    print()

    workers = ["worker-1", "worker-2"]
    tasks = deque(
        [
            {"name": "박스 접기", "should_fail_once": False},
            {"name": "스티커 붙이기", "should_fail_once": True},
            {"name": "포장 끈 묶기", "should_fail_once": False},
        ]
    )

    turn = 0
    while tasks:
        task = tasks.popleft()
        worker = workers[turn % len(workers)]
        print(f"  {worker} 가 '{task['name']}' 작업을 받았습니다.")

        if task["should_fail_once"]:
            print("    처리 중 실수 발생 -> ACK를 보내지 못했습니다.")
            print("    브로커는 '끝난 게 아니구나'라고 생각하고 일을 다시 줄 수 있습니다.")
            task["should_fail_once"] = False
            tasks.append(task)
        else:
            print("    처리 완료 -> ACK 전송")

        turn += 1

    print()


def lesson3_common_mistake():
    print("[레슨 3] 초보자가 자주 하는 오해")
    print()
    print("  1. 작업이 큐에 들어갔다고 바로 끝난 것이 아닙니다.")
    print("     소비자가 꺼내고, 실제 일을 끝내고, ACK까지 보내야 안전합니다.")
    print("  2. 작업자 수를 무작정 늘린다고 항상 빨라지지 않습니다.")
    print("     각 작업이 CPU를 많이 쓰는지, 네트워크를 기다리는지에 따라 적정 개수가 다릅니다.")
    print("  3. 오래 걸리는 작업과 짧은 작업을 한 큐에 섞으면 한쪽이 밀릴 수 있습니다.")
    print("     그래서 실무에서는 큐를 역할별로 나누기도 합니다.")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("RabbitMQ 02단계: Work Queue와 ACK")
    print("=" * 72)
    print()

    lesson1_round_robin_distribution()
    lesson2_ack_and_requeue()
    lesson3_common_mistake()
