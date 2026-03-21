def assign_partitions(consumers, partitions):
    assignments = {consumer: [] for consumer in consumers}

    for index, partition in enumerate(partitions):
        consumer = consumers[index % len(consumers)]
        assignments[consumer].append(partition)

    return assignments


def lesson1_group_shares_partitions():
    print("[레슨 1] consumer group은 파티션을 나눠 맡는다")
    print()

    assignments = assign_partitions(["A", "B"], [0, 1, 2, 3])
    for consumer, partitions in assignments.items():
        print(f"  consumer {consumer}: {partitions}")
    print()


def lesson2_more_consumers_than_partitions():
    print("[레슨 2] 소비자가 너무 많으면 일부는 놀게 된다")
    print()

    assignments = assign_partitions(["A", "B", "C", "D"], [0, 1])
    for consumer, partitions in assignments.items():
        print(f"  consumer {consumer}: {partitions}")

    print("  설명: 파티션이 2개면 동시에 일을 맡을 수 있는 소비자도 최대 2명입니다.")
    print()


def lesson3_rebalance_when_member_changes():
    print("[레슨 3] 그룹 구성원이 바뀌면 재배치(rebalance)가 일어난다")
    print()

    before = assign_partitions(["A", "B"], [0, 1, 2, 3])
    after = assign_partitions(["A", "B", "C"], [0, 1, 2, 3])

    print("  C가 들어오기 전:", before)
    print("  C가 들어온 뒤:", after)
    print("  실사용 주의: rebalance 동안 잠깐 처리 흐름이 흔들릴 수 있어 로그를 잘 봐야 합니다.")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("Kafka 03단계: Consumer Group")
    print("=" * 72)
    print()

    lesson1_group_shares_partitions()
    lesson2_more_consumers_than_partitions()
    lesson3_rebalance_when_member_changes()
