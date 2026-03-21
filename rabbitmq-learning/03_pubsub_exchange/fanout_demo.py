from collections import deque


def publish_fanout(message, subscribers):
    # fanout exchange는 "누가 받을지 고르지 않고 모두에게 복사"하는 역할입니다.
    # 학교 방송이 복도 스피커, 교실 스피커, 방송실 녹음기에 동시에 퍼지는 모습과 비슷합니다.
    for queue in subscribers.values():
        queue.append(message)


def lesson1_broadcast_to_everyone():
    print("[레슨 1] fanout exchange는 같은 메시지를 모두에게 복사함")
    print()

    subscribers = {
        "notice-board": deque(),
        "mobile-app": deque(),
        "teacher-screen": deque(),
    }

    publish_fanout("운동회 일정이 금요일로 변경되었습니다.", subscribers)

    for name, queue in subscribers.items():
        print(f"  {name}: {list(queue)}")
    print()


def lesson2_each_queue_moves_at_its_own_speed():
    print("[레슨 2] 각 구독자는 자기 속도로 읽어도 됨")
    print()

    subscribers = {
        "notice-board": deque(),
        "mobile-app": deque(),
        "teacher-screen": deque(),
    }

    publish_fanout("1교시 시작 10분 전입니다.", subscribers)
    publish_fanout("체육복 검사를 준비하세요.", subscribers)

    # 공지판은 느리게 읽고, 모바일 앱은 바로 두 개 다 읽는다고 가정합니다.
    mobile_first = subscribers["mobile-app"].popleft()
    mobile_second = subscribers["mobile-app"].popleft()
    print("  mobile-app 처리:", mobile_first)
    print("  mobile-app 처리:", mobile_second)
    print("  notice-board에 아직 남은 메시지:", list(subscribers["notice-board"]))
    print("  핵심: 같은 방송을 받아도 각 큐의 처리 속도는 서로 독립적입니다.")
    print()


def lesson3_real_use_case():
    print("[레슨 3] 실무에서는 언제 쓰는가")
    print()
    print("  - 주문이 생기면 알림 서비스, 통계 서비스, 로그 저장 서비스가 모두 알아야 할 때")
    print("  - 회원 가입이 되면 이메일 발송, 쿠폰 지급, 관리자 대시보드 갱신이 모두 필요할 때")
    print("  fanout은 '한 번 말하면 여러 팀이 동시에 듣는 방송'에 어울립니다.")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("RabbitMQ 03단계: Fanout Exchange")
    print("=" * 72)
    print()

    lesson1_broadcast_to_everyone()
    lesson2_each_queue_moves_at_its_own_speed()
    lesson3_real_use_case()
