"""
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  RabbitMQ 04단계: Routing과 Topic Exchange                      ■
■  Direct Exchange, Topic Exchange (와일드카드), Headers Exchange   ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
"""

import re
from collections import defaultdict


# ============================================================
#  토이 Exchange 구현
#  비유: 우체국 분류실 - 편지의 주소(routing key)를 보고
#       어느 배달부(큐)에게 줄지 결정합니다.
# ============================================================
class DirectExchange:
    """
    Direct Exchange: routing key가 정확히 일치하는 큐에만 전달.
    비유: 우편번호가 정확히 맞는 우체통에만 넣기.
    """

    def __init__(self, name):
        self.name = name
        self.bindings = defaultdict(list)  # {routing_key: [queue1, queue2, ...]}

    def bind(self, queue, routing_key):
        self.bindings[routing_key].append(queue)

    def publish(self, routing_key, message):
        delivered = []
        for queue in self.bindings.get(routing_key, []):
            queue.append({"routing_key": routing_key, "body": message})
            delivered.append(queue)
        return len(delivered)


class TopicExchange:
    """
    Topic Exchange: 와일드카드 패턴으로 routing key를 매칭.
    비유: 우편물 분류에서 '서울시.*.아파트'처럼 패턴으로 묶어 배달.

    와일드카드:
      * (별표) = 단어 하나와 매칭 (예: log.*.error -> log.app.error)
      # (샵)  = 0개 이상의 단어와 매칭 (예: log.# -> log.app.error, log.db)
    """

    def __init__(self, name):
        self.name = name
        self.bindings = []  # [(pattern, queue), ...]

    def bind(self, queue, pattern):
        self.bindings.append((pattern, queue))

    def _matches(self, pattern, routing_key):
        """패턴이 routing_key와 매칭되는지 확인"""
        pattern_parts = pattern.split(".")
        key_parts = routing_key.split(".")

        return self._match_parts(pattern_parts, key_parts)

    def _match_parts(self, pattern_parts, key_parts):
        if not pattern_parts and not key_parts:
            return True
        if not pattern_parts:
            return False
        if pattern_parts[0] == "#":
            if len(pattern_parts) == 1:
                return True  # # 뒤에 아무것도 없으면 모든 것 매칭
            # #은 0개 이상이므로 여러 경우를 시도
            for i in range(len(key_parts) + 1):
                if self._match_parts(pattern_parts[1:], key_parts[i:]):
                    return True
            return False
        if not key_parts:
            return False
        if pattern_parts[0] == "*" or pattern_parts[0] == key_parts[0]:
            return self._match_parts(pattern_parts[1:], key_parts[1:])
        return False

    def publish(self, routing_key, message):
        delivered = []
        for pattern, queue in self.bindings:
            if self._matches(pattern, routing_key):
                queue.append({"routing_key": routing_key, "body": message})
                delivered.append(pattern)
        return delivered


class HeadersExchange:
    """
    Headers Exchange: 메시지 헤더의 키-값으로 매칭.
    비유: 편지 봉투의 '빠른등기', '등기', '일반' 스탬프를 보고 분류.
    """

    def __init__(self, name):
        self.name = name
        self.bindings = []  # [(headers_match, match_type, queue), ...]

    def bind(self, queue, headers, match_type="all"):
        """
        match_type:
          "all" = 모든 헤더가 일치 (AND)
          "any" = 하나라도 일치 (OR)
        """
        self.bindings.append((headers, match_type, queue))

    def publish(self, headers, message):
        delivered = []
        for bind_headers, match_type, queue in self.bindings:
            if match_type == "all":
                if all(headers.get(k) == v for k, v in bind_headers.items()):
                    queue.append({"headers": headers, "body": message})
                    delivered.append("all-match")
            elif match_type == "any":
                if any(headers.get(k) == v for k, v in bind_headers.items()):
                    queue.append({"headers": headers, "body": message})
                    delivered.append("any-match")
        return delivered


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 1: Direct Exchange - 정확한 주소로 배달                │
# │  비유: 우편번호가 정확히 맞는 우체통에만 넣기                 │
# └─────────────────────────────────────────────────────────────┘
def lesson1_direct_exchange():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 1: Direct Exchange - 정확한 주소로 배달        │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Direct Exchange는 routing key가 정확히 일치하는 큐에만 메시지를 전달합니다.
    # 우편번호가 정확히 맞는 우체통에만 편지를 넣는 것과 같아요!
    # 로그 레벨별 분류에 자주 사용됩니다.

    exchange = DirectExchange("log_exchange")

    error_queue = []
    warning_queue = []
    info_queue = []

    exchange.bind(error_queue, "error")
    exchange.bind(warning_queue, "warning")
    exchange.bind(info_queue, "info")

    # 메시지 발행
    messages = [
        ("error", "DB 연결 실패!"),
        ("info", "서버 시작됨"),
        ("warning", "메모리 80% 사용"),
        ("error", "파일을 찾을 수 없음"),
        ("info", "요청 처리 완료"),
    ]

    for routing_key, msg in messages:
        count = exchange.publish(routing_key, msg)
        print(f"  [{routing_key:8s}] '{msg}' -> {count}개 큐에 전달")

    print(f"\n  error 큐: {len(error_queue)}개 - {[m['body'] for m in error_queue]}")
    print(f"  warning 큐: {len(warning_queue)}개 - {[m['body'] for m in warning_queue]}")
    print(f"  info 큐: {len(info_queue)}개 - {[m['body'] for m in info_queue]}")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 2: Topic Exchange - 패턴으로 분류                      │
# │  비유: '서울시.*.아파트' 같은 패턴으로 편지를 분류             │
# └─────────────────────────────────────────────────────────────┘
def lesson2_topic_exchange():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 2: Topic Exchange - 패턴으로 분류              │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Topic Exchange는 와일드카드 패턴을 사용합니다.
    # *: 단어 하나와 매칭 (예: log.*.error)
    # #: 0개 이상의 단어와 매칭 (예: log.#)
    # 비유: 우편물 분류에서 '서울시.*.아파트'는 서울시 어느 구든 아파트면 OK!

    exchange = TopicExchange("event_exchange")

    all_logs = []      # 모든 로그를 받는 큐
    app_errors = []    # 앱 에러만 받는 큐
    db_all = []        # DB 관련 모든 로그를 받는 큐

    exchange.bind(all_logs, "log.#")         # 모든 로그
    exchange.bind(app_errors, "log.app.error")  # 앱 에러만
    exchange.bind(db_all, "log.db.*")        # DB 로그 전부

    messages = [
        ("log.app.error", "앱 크래시 발생"),
        ("log.app.info", "사용자 로그인"),
        ("log.db.error", "쿼리 타임아웃"),
        ("log.db.warning", "슬로우 쿼리 감지"),
        ("log.system.info", "시스템 정상"),
    ]

    print("  메시지 라우팅:")
    for routing_key, msg in messages:
        matched = exchange.publish(routing_key, msg)
        print(f"    {routing_key:20s} -> 매칭 패턴: {matched}")

    print(f"\n  all_logs (log.#): {len(all_logs)}개")
    for m in all_logs:
        print(f"    {m['routing_key']}: {m['body']}")
    print(f"  app_errors (log.app.error): {len(app_errors)}개")
    print(f"  db_all (log.db.*): {len(db_all)}개")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 3: Headers Exchange - 봉투 스탬프로 분류               │
# └─────────────────────────────────────────────────────────────┘
def lesson3_headers_exchange():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 3: Headers Exchange - 헤더 기반 라우팅         │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Headers Exchange는 routing key 대신 메시지의 헤더(메타데이터)로 라우팅합니다.
    # 편지 봉투에 '빠른등기', '국제우편' 스탬프를 찍으면
    # 스탬프 조합에 따라 분류하는 것과 같아요!

    exchange = HeadersExchange("notification_exchange")

    email_queue = []
    sms_queue = []
    urgent_queue = []

    # email AND type=alert인 메시지만
    exchange.bind(email_queue, {"channel": "email", "type": "alert"}, "all")
    # sms 채널이면 어떤 타입이든
    exchange.bind(sms_queue, {"channel": "sms"}, "any")
    # urgent이면 어떤 채널이든
    exchange.bind(urgent_queue, {"priority": "urgent"}, "any")

    messages = [
        ({"channel": "email", "type": "alert"}, "서버 다운 알림"),
        ({"channel": "sms", "type": "promo"}, "할인 쿠폰"),
        ({"channel": "email", "type": "info", "priority": "urgent"}, "긴급 공지"),
        ({"channel": "push", "type": "alert"}, "앱 푸시 알림"),
    ]

    print("  메시지 발행:")
    for headers, msg in messages:
        matched = exchange.publish(headers, msg)
        print(f"    {msg:15s} headers={headers}")
        print(f"      -> 매칭: {matched if matched else '없음'}")

    print(f"\n  email 큐: {len(email_queue)}개")
    print(f"  sms 큐: {len(sms_queue)}개")
    print(f"  urgent 큐: {len(urgent_queue)}개")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 4: 실전 예시 - 우편물 분류 시스템                      │
# └─────────────────────────────────────────────────────────────┘
def lesson4_mail_sorting():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 4: 실전 예시 - 우편물 분류 시스템              │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 실전: 이커머스의 주문 이벤트를 여러 서비스로 라우팅

    exchange = TopicExchange("order_exchange")

    # 각 서비스의 큐
    payment_queue = []
    inventory_queue = []
    shipping_queue = []
    analytics_queue = []

    exchange.bind(payment_queue, "order.*.payment")
    exchange.bind(inventory_queue, "order.*.inventory")
    exchange.bind(shipping_queue, "order.created.shipping")
    exchange.bind(analytics_queue, "order.#")  # 모든 주문 이벤트

    events = [
        ("order.created.payment", "주문1001: 결제 요청"),
        ("order.created.inventory", "주문1001: 재고 확인"),
        ("order.created.shipping", "주문1001: 배송 준비"),
        ("order.cancelled.payment", "주문1002: 환불 처리"),
        ("order.cancelled.inventory", "주문1002: 재고 복구"),
    ]

    print("  주문 이벤트 라우팅:")
    for routing_key, msg in events:
        matched = exchange.publish(routing_key, msg)
        print(f"    {routing_key:30s} -> {len(matched)}개 매칭")

    print(f"\n  결제 서비스: {len(payment_queue)}건")
    print(f"  재고 서비스: {len(inventory_queue)}건")
    print(f"  배송 서비스: {len(shipping_queue)}건 (생성 주문만)")
    print(f"  분석 서비스: {len(analytics_queue)}건 (모든 이벤트)")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 5: Exchange 비교 정리                                  │
# └─────────────────────────────────────────────────────────────┘
def lesson5_summary():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 5: Exchange 비교 정리                          │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    print("  ┌──────────────┬──────────────┬──────────────────────────────┐")
    print("  │ Exchange      │ 매칭 방식     │ 사용 예                       │")
    print("  ├──────────────┼──────────────┼──────────────────────────────┤")
    print("  │ Direct       │ 정확히 일치   │ 로그 레벨별 분류              │")
    print("  │ Topic        │ 와일드카드    │ 이벤트 계층별 라우팅          │")
    print("  │ Fanout       │ 모든 큐에 전달 │ 브로드캐스트 (03단계에서 학습) │")
    print("  │ Headers      │ 헤더 키-값    │ 복잡한 조건 분류              │")
    print("  └──────────────┴──────────────┴──────────────────────────────┘")
    print()


def main():
    print("=" * 72)
    print("  RabbitMQ 04단계: Routing과 Topic Exchange")
    print("=" * 72)
    print()

    lesson1_direct_exchange()
    lesson2_topic_exchange()
    lesson3_headers_exchange()
    lesson4_mail_sorting()
    lesson5_summary()


if __name__ == "__main__":
    main()
