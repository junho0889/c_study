def choose_partition(key, partition_count):
    return sum(ord(ch) for ch in key) % partition_count


def append_to_partition(partitions, key, event_name):
    partition_index = choose_partition(key, len(partitions))
    partitions[partition_index].append({"key": key, "event": event_name})
    return partition_index


def lesson1_same_key_goes_to_same_partition():
    print("[레슨 1] 같은 key는 같은 파티션으로 가기 쉽다")
    print()

    for order_key in ["user-1", "user-2", "user-1", "user-3"]:
        partition = choose_partition(order_key, 3)
        print(f"  {order_key} -> partition {partition}")
    print()


def lesson2_order_is_kept_inside_one_partition():
    print("[레슨 2] 순서는 파티션 안에서 지켜진다")
    print()

    partitions = {0: [], 1: [], 2: []}
    append_to_partition(partitions, "user-1", "created")
    append_to_partition(partitions, "user-1", "paid")
    append_to_partition(partitions, "user-1", "shipped")

    user_partition = choose_partition("user-1", 3)
    print(f"  user-1 이 들어간 partition: {user_partition}")
    for index, event in enumerate(partitions[user_partition], start=1):
        print(f"  {index}. {event['key']} -> {event['event']}")
    print()


def lesson3_different_keys_can_be_parallel():
    print("[레슨 3] 다른 key는 다른 파티션으로 흩어져 병렬 처리가 쉬워진다")
    print()

    partitions = {0: [], 1: [], 2: []}

    for key, event_name in [
        ("user-1", "created"),
        ("user-2", "created"),
        ("user-3", "created"),
        ("user-2", "paid"),
    ]:
        partition = append_to_partition(partitions, key, event_name)
        print(f"  {key} / {event_name} -> partition {partition}")

    print("  설명: 같은 사용자의 순서는 지키되, 다른 사용자는 나눠서 처리하기 좋습니다.")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("Kafka 02단계: 파티션과 순서")
    print("=" * 72)
    print()

    lesson1_same_key_goes_to_same_partition()
    lesson2_order_is_kept_inside_one_partition()
    lesson3_different_keys_can_be_parallel()
