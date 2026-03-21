##############################################################################
# ■■■ RabbitMQ Producer 실습 코드 ■■■
#
# 이 스크립트는 RabbitMQ에 메시지를 발행(Publish)하는 방법을 보여줍니다.
# Direct, Topic, Fanout Exchange를 모두 실습합니다.
#
# 사전 준비:
#   pip install pika
#
# 실행 방법:
#   python producer.py
#
# 주요 학습 내용:
#   1. RabbitMQ 연결 및 채널 생성
#   2. Exchange 선언 (Direct, Topic, Fanout)
#   3. 메시지 속성 설정 (영속성, 우선순위, TTL)
#   4. 각 Exchange 타입별 메시지 발행
#   5. 발행 확인 (Publisher Confirm)
##############################################################################

import pika
import json
import sys
import time
from datetime import datetime


# ■■■ 연결 설정 ■■■
RABBITMQ_HOST = "localhost"         # RabbitMQ 서버 주소
RABBITMQ_PORT = 5672                # AMQP 포트
RABBITMQ_USER = "admin"             # 사용자 이름
RABBITMQ_PASS = "admin1234"         # 비밀번호
RABBITMQ_VHOST = "/"                # 가상 호스트

# ■■■ Exchange 이름 (definitions.json에서 미리 정의) ■■■
DIRECT_EXCHANGE = "direct.exchange"   # Direct Exchange
TOPIC_EXCHANGE = "topic.exchange"     # Topic Exchange
FANOUT_EXCHANGE = "fanout.exchange"   # Fanout Exchange


def create_connection():
    """
    ■■■ RabbitMQ 연결 생성 ■■■

    pika 라이브러리를 사용하여 RabbitMQ 서버에 연결합니다.

    연결 과정:
    1. 인증 정보(credentials) 설정
    2. 연결 파라미터 설정 (호스트, 포트, 하트비트 등)
    3. BlockingConnection으로 동기 연결 생성

    Returns:
        pika.BlockingConnection: RabbitMQ 연결 객체
    """
    # 인증 정보 설정
    credentials = pika.PlainCredentials(
        username=RABBITMQ_USER,
        password=RABBITMQ_PASS,
    )

    # 연결 파라미터 설정
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=credentials,
        # 하트비트 간격 (초): 연결 활성 상태 확인
        heartbeat=600,
        # 블로킹 연결 타임아웃 (초)
        blocked_connection_timeout=300,
        # 연결 타임아웃 (초)
        connection_attempts=3,    # 최대 재시도 횟수
        retry_delay=5,            # 재시도 간격 (초)
    )

    try:
        connection = pika.BlockingConnection(parameters)
        print(f"[연결] RabbitMQ 서버 연결 성공 ({RABBITMQ_HOST}:{RABBITMQ_PORT})")
        return connection
    except pika.exceptions.AMQPConnectionError as e:
        print(f"[오류] RabbitMQ 연결 실패: {e}")
        print("  → docker-compose up -d 로 RabbitMQ를 먼저 시작하세요.")
        sys.exit(1)


def setup_channel(connection):
    """
    ■■■ 채널 생성 및 설정 ■■■

    채널(Channel)은 연결(Connection) 내의 가상 연결입니다.
    하나의 TCP 연결에서 여러 채널을 사용하여 동시 작업이 가능합니다.

    Publisher Confirm 모드:
    - 메시지가 브로커에 도달했는지 확인하는 메커니즘
    - 메시지 손실 방지에 필수

    Args:
        connection: RabbitMQ 연결 객체

    Returns:
        pika.channel.Channel: 채널 객체
    """
    channel = connection.channel()

    # Publisher Confirm 모드 활성화
    # 이 모드에서는 브로커가 메시지 수신을 확인(ACK)해줌
    # basic_publish()가 성공하면 메시지가 브로커에 도달한 것이 보장됨
    channel.confirm_delivery()

    print("[채널] 채널 생성 및 Publisher Confirm 활성화 완료")
    return channel


def publish_direct(channel):
    """
    ■■■ Direct Exchange로 메시지 발행 ■■■

    Direct Exchange는 라우팅 키가 정확히 일치하는 큐에 메시지를 전달합니다.

    동작 방식:
    - Producer → Exchange(routing_key="order") → Queue(binding_key="order")
    - 라우팅 키와 바인딩 키가 정확히 일치해야 전달

    사용 사례:
    - 작업 분배 (특정 작업 유형별 큐)
    - RPC 패턴
    - 특정 서비스로의 명시적 라우팅
    """
    print(f"\n{'='*60}")
    print("■■■ Direct Exchange 메시지 발행 ■■■")
    print(f"{'='*60}")

    # 주문 메시지 5건 발행
    for i in range(5):
        # 메시지 본문 (JSON 형식)
        message = {
            "order_id": f"ORD-{i+1:04d}",
            "product": f"상품{i+1}",
            "quantity": (i + 1) * 2,
            "price": (i + 1) * 10000,
            "timestamp": datetime.now().isoformat(),
        }

        # 메시지 속성 설정
        properties = pika.BasicProperties(
            # delivery_mode=2: 메시지를 디스크에 저장 (persistent)
            # RabbitMQ 재시작 후에도 메시지 유지
            # delivery_mode=1: 메모리에만 저장 (transient, 빠르지만 손실 가능)
            delivery_mode=2,

            # content_type: 메시지 본문의 MIME 타입
            content_type="application/json",

            # message_id: 메시지 고유 ID (중복 감지에 활용)
            message_id=f"msg-{i+1}",

            # timestamp: 메시지 생성 시각 (Unix timestamp)
            timestamp=int(time.time()),

            # headers: 커스텀 헤더 (메타데이터 전달용)
            headers={
                "source": "producer.py",
                "version": "1.0",
            },

            # expiration: 메시지 TTL (밀리초 문자열)
            # 이 시간이 지나면 메시지 자동 삭제
            # expiration="60000",  # 60초
        )

        try:
            # basic_publish: 메시지 발행
            channel.basic_publish(
                exchange=DIRECT_EXCHANGE,      # 대상 Exchange 이름
                routing_key="order",           # 라우팅 키 (바인딩 키와 매칭)
                body=json.dumps(message, ensure_ascii=False),  # 메시지 본문
                properties=properties,          # 메시지 속성
            )
            print(f"  [발행] 주문 #{message['order_id']} → {DIRECT_EXCHANGE} (routing_key='order')")

        except pika.exceptions.UnroutableError:
            # mandatory=True 사용 시, 라우팅할 큐가 없으면 이 예외 발생
            print(f"  [실패] 메시지를 라우팅할 큐가 없습니다.")

    print(f"[완료] Direct Exchange로 5건 발행 완료")


def publish_topic(channel):
    """
    ■■■ Topic Exchange로 메시지 발행 ■■■

    Topic Exchange는 라우팅 키의 패턴 매칭으로 큐를 선택합니다.

    패턴 매칭 규칙:
    - * (별표): 정확히 1개의 단어와 매칭
    - # (해시): 0개 이상의 단어와 매칭

    예시:
    - 라우팅 키: "log.error"
    - 바인딩 키: "log.error" → 매칭 O
    - 바인딩 키: "log.*"    → 매칭 O
    - 바인딩 키: "log.#"    → 매칭 O
    - 바인딩 키: "*.error"  → 매칭 O
    - 바인딩 키: "#"        → 매칭 O (모든 메시지)

    사용 사례:
    - 로그 레벨별 라우팅 (log.info, log.error, log.warn)
    - 이벤트 카테고리별 분류
    """
    print(f"\n{'='*60}")
    print("■■■ Topic Exchange 메시지 발행 ■■■")
    print(f"{'='*60}")

    # 다양한 로그 레벨의 메시지 발행
    log_messages = [
        {"level": "info",    "routing_key": "log.info",    "message": "사용자 로그인 성공"},
        {"level": "warning", "routing_key": "log.warning", "message": "디스크 사용량 80% 초과"},
        {"level": "error",   "routing_key": "log.error",   "message": "데이터베이스 연결 실패"},
        {"level": "info",    "routing_key": "log.info",    "message": "주문 처리 완료"},
        {"level": "error",   "routing_key": "log.error",   "message": "결제 시스템 타임아웃"},
        {"level": "debug",   "routing_key": "log.debug",   "message": "캐시 히트율: 95.3%"},
    ]

    for log_entry in log_messages:
        message = {
            "level": log_entry["level"],
            "message": log_entry["message"],
            "service": "order-service",
            "timestamp": datetime.now().isoformat(),
        }

        properties = pika.BasicProperties(
            delivery_mode=2,
            content_type="application/json",
        )

        channel.basic_publish(
            exchange=TOPIC_EXCHANGE,
            # 라우팅 키: "log.info", "log.error" 등
            # log.error.queue는 "log.error" 바인딩 → error만 수신
            # log.all.queue는 "log.#" 바인딩 → 모든 로그 수신
            routing_key=log_entry["routing_key"],
            body=json.dumps(message, ensure_ascii=False),
            properties=properties,
        )
        print(
            f"  [발행] [{log_entry['level'].upper():7s}] "
            f"{log_entry['message']} → routing_key='{log_entry['routing_key']}'"
        )

    print(f"[완료] Topic Exchange로 {len(log_messages)}건 발행 완료")
    print(f"  → log.error.queue: error 로그만 수신 (2건)")
    print(f"  → log.all.queue: 모든 로그 수신 ({len(log_messages)}건)")


def publish_fanout(channel):
    """
    ■■■ Fanout Exchange로 메시지 발행 ■■■

    Fanout Exchange는 바인딩된 모든 큐에 메시지를 브로드캐스트합니다.
    라우팅 키를 무시하고, 바인딩된 모든 큐에 복사본을 전달합니다.

    동작 방식:
    - Producer → Fanout Exchange → Queue A (복사본)
                                  → Queue B (복사본)
                                  → Queue C (복사본)

    사용 사례:
    - 알림 브로드캐스트 (모든 서비스에 동일 알림)
    - 이벤트 발행 (여러 소비자가 독립적으로 처리)
    - 실시간 데이터 스트리밍
    """
    print(f"\n{'='*60}")
    print("■■■ Fanout Exchange 메시지 발행 ■■■")
    print(f"{'='*60}")

    # 알림 메시지 발행
    notifications = [
        "서버 점검 예정: 2024-12-20 02:00 ~ 04:00",
        "새로운 기능이 배포되었습니다: v2.5.0",
        "보안 업데이트가 적용되었습니다.",
    ]

    for i, notification in enumerate(notifications):
        message = {
            "notification_id": i + 1,
            "content": notification,
            "priority": "high" if i == 2 else "normal",
            "timestamp": datetime.now().isoformat(),
        }

        properties = pika.BasicProperties(
            delivery_mode=2,
            content_type="application/json",
            # priority: 메시지 우선순위 (0-9, 높을수록 우선)
            # 큐에 x-max-priority 설정이 있어야 동작
            priority=5 if message["priority"] == "high" else 1,
        )

        channel.basic_publish(
            exchange=FANOUT_EXCHANGE,
            # Fanout Exchange는 라우팅 키를 무시하므로 빈 문자열
            routing_key="",
            body=json.dumps(message, ensure_ascii=False),
            properties=properties,
        )
        print(
            f"  [브로드캐스트] 알림 #{i+1}: {notification[:30]}..."
        )

    print(f"[완료] Fanout Exchange로 {len(notifications)}건 브로드캐스트 완료")
    print(f"  → notification.a.queue: {len(notifications)}건 수신")
    print(f"  → notification.b.queue: {len(notifications)}건 수신")


def publish_to_default_exchange(channel):
    """
    ■■■ Default Exchange (기본 Exchange) 사용 ■■■

    RabbitMQ에는 이름이 빈 문자열("")인 기본 Exchange가 있습니다.
    기본 Exchange는 Direct 타입이며, 모든 큐가 자동으로 바인딩됩니다.
    라우팅 키를 큐 이름과 동일하게 설정하면 해당 큐에 직접 전달됩니다.

    사용 사례:
    - 간단한 작업 큐 패턴 (Work Queue)
    - 큐에 직접 메시지 전송 (Exchange 설정 불필요)
    """
    print(f"\n{'='*60}")
    print("■■■ Default Exchange (직접 큐 전송) ■■■")
    print(f"{'='*60}")

    # 임시 큐 선언 (실습용)
    queue_name = "simple.task.queue"
    channel.queue_declare(
        queue=queue_name,
        durable=True,      # 브로커 재시작 후에도 큐 유지
    )

    for i in range(3):
        message = {
            "task_id": i + 1,
            "task_name": f"간단한 작업 #{i+1}",
            "timestamp": datetime.now().isoformat(),
        }

        properties = pika.BasicProperties(
            delivery_mode=2,
            content_type="application/json",
        )

        # exchange="": 기본 Exchange 사용
        # routing_key=큐이름: 해당 큐에 직접 전달
        channel.basic_publish(
            exchange="",                    # 기본 Exchange
            routing_key=queue_name,         # 큐 이름 = 라우팅 키
            body=json.dumps(message, ensure_ascii=False),
            properties=properties,
        )
        print(f"  [직접 전송] 작업 #{i+1} → {queue_name}")

    print(f"[완료] Default Exchange로 3건 직접 전송 완료")


def main():
    """
    ■■■ 메인 실행 함수 ■■■

    실행 순서:
    1. RabbitMQ 연결
    2. 채널 생성
    3. Direct Exchange 메시지 발행
    4. Topic Exchange 메시지 발행
    5. Fanout Exchange 메시지 발행
    6. Default Exchange 직접 전송
    7. 연결 종료
    """
    print("=" * 60)
    print("■■■ RabbitMQ Producer 실습 시작 ■■■")
    print("=" * 60)

    # 1. 연결 생성
    connection = create_connection()

    try:
        # 2. 채널 생성
        channel = setup_channel(connection)

        # 3. Direct Exchange로 주문 메시지 발행
        publish_direct(channel)

        # 4. Topic Exchange로 로그 메시지 발행
        publish_topic(channel)

        # 5. Fanout Exchange로 알림 브로드캐스트
        publish_fanout(channel)

        # 6. Default Exchange로 직접 전송
        publish_to_default_exchange(channel)

        print(f"\n{'='*60}")
        print("■■■ 모든 메시지 발행 완료 ■■■")
        print(f"{'='*60}")
        print("\n[확인] Management UI에서 큐별 메시지를 확인하세요:")
        print("  → http://localhost:15672 (admin / admin1234)")

    except Exception as e:
        print(f"\n[오류] 메시지 발행 중 오류 발생: {e}")
    finally:
        # 7. 연결 종료 (채널도 자동 종료)
        if connection and connection.is_open:
            connection.close()
            print("\n[종료] RabbitMQ 연결이 정상적으로 종료되었습니다.")


if __name__ == "__main__":
    main()
