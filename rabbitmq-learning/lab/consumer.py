##############################################################################
# ■■■ RabbitMQ Consumer 실습 코드 ■■■
#
# 이 스크립트는 RabbitMQ 큐에서 메시지를 소비(Consume)하는 방법을 보여줍니다.
#
# 사전 준비:
#   pip install pika
#
# 실행 방법:
#   python consumer.py                # 기본 (order.queue 소비)
#   python consumer.py order          # 주문 큐 소비
#   python consumer.py log-error      # 에러 로그 큐 소비
#   python consumer.py log-all        # 전체 로그 큐 소비
#   python consumer.py notification   # 알림 큐 소비
#
# 주요 학습 내용:
#   1. 메시지 소비 (basic_consume)
#   2. 메시지 확인 (ACK/NACK/Reject)
#   3. Prefetch (QoS) 설정
#   4. 에러 핸들링 및 재처리
#   5. 그레이스풀 셧다운
##############################################################################

import pika
import json
import sys
import time
import signal
from datetime import datetime


# ■■■ 연결 설정 ■■■
RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
RABBITMQ_USER = "admin"
RABBITMQ_PASS = "admin1234"
RABBITMQ_VHOST = "/"

# ■■■ 큐 이름 매핑 ■■■
QUEUE_MAP = {
    "order":        "order.queue",              # Direct Exchange에서 주문 메시지
    "log-error":    "log.error.queue",           # Topic Exchange에서 에러 로그
    "log-all":      "log.all.queue",             # Topic Exchange에서 전체 로그
    "notification": "notification.a.queue",      # Fanout Exchange에서 알림
}

# ■■■ 그레이스풀 셧다운 플래그 ■■■
shutdown_requested = False


def signal_handler(signum, frame):
    """
    ■■■ 시그널 핸들러 ■■■

    Ctrl+C (SIGINT) 수신 시 안전하게 종료합니다.
    현재 처리 중인 메시지를 완료한 후 종료합니다.
    """
    global shutdown_requested
    print("\n[시그널] 종료 요청 수신. 현재 메시지 처리 완료 후 종료합니다...")
    shutdown_requested = True


# 시그널 핸들러 등록
signal.signal(signal.SIGINT, signal_handler)


def create_connection():
    """
    ■■■ RabbitMQ 연결 생성 ■■■

    Returns:
        pika.BlockingConnection: RabbitMQ 연결 객체
    """
    credentials = pika.PlainCredentials(
        username=RABBITMQ_USER,
        password=RABBITMQ_PASS,
    )

    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300,
        connection_attempts=3,
        retry_delay=5,
    )

    try:
        connection = pika.BlockingConnection(parameters)
        print(f"[연결] RabbitMQ 서버 연결 성공 ({RABBITMQ_HOST}:{RABBITMQ_PORT})")
        return connection
    except pika.exceptions.AMQPConnectionError as e:
        print(f"[오류] RabbitMQ 연결 실패: {e}")
        print("  → docker-compose up -d 로 RabbitMQ를 먼저 시작하세요.")
        sys.exit(1)


def process_order(body):
    """
    ■■■ 주문 메시지 처리 함수 ■■■

    실제 서비스에서는 여기에 비즈니스 로직을 구현합니다.
    - 데이터베이스에 주문 저장
    - 결제 처리 요청
    - 재고 차감
    - 확인 이메일 발송

    Args:
        body: 메시지 본문 (dict)

    Raises:
        Exception: 처리 실패 시
    """
    print(f"    처리: 주문 {body.get('order_id')} - "
          f"{body.get('product')} x {body.get('quantity')} = "
          f"{body.get('price')}원")
    # 실제 처리 시뮬레이션 (0.5초 소요)
    time.sleep(0.5)


def process_log(body):
    """
    ■■■ 로그 메시지 처리 함수 ■■■

    로그 수준에 따라 다른 처리를 수행합니다.
    - error: 알림 발송, 온콜 담당자 호출
    - warning: 모니터링 대시보드에 표시
    - info: 로그 저장소에 기록

    Args:
        body: 메시지 본문 (dict)
    """
    level = body.get("level", "unknown").upper()
    message = body.get("message", "")
    print(f"    로그: [{level:7s}] {message}")


def process_notification(body):
    """
    ■■■ 알림 메시지 처리 함수 ■■■

    알림을 사용자에게 전달합니다.
    - 이메일 발송
    - 푸시 알림
    - SMS 발송

    Args:
        body: 메시지 본문 (dict)
    """
    content = body.get("content", "")
    priority = body.get("priority", "normal")
    print(f"    알림: [{priority}] {content}")


# 큐별 처리 함수 매핑
PROCESSOR_MAP = {
    "order.queue": process_order,
    "log.error.queue": process_log,
    "log.all.queue": process_log,
    "notification.a.queue": process_notification,
    "notification.b.queue": process_notification,
}


def on_message_callback(channel, method, properties, body):
    """
    ■■■ 메시지 수신 콜백 함수 ■■■

    큐에서 메시지가 도착할 때마다 호출되는 콜백입니다.

    매개변수 설명:
    - channel: 메시지를 수신한 채널 객체
    - method: 전달 메타데이터 (delivery_tag, routing_key, exchange 등)
    - properties: 메시지 속성 (content_type, headers, message_id 등)
    - body: 메시지 본문 (바이트)

    ACK/NACK/Reject 설명:
    - basic_ack: 메시지 처리 성공 → 큐에서 삭제
    - basic_nack: 메시지 처리 실패 → requeue=True면 큐에 재입력
    - basic_reject: 단일 메시지 거부 → requeue=True면 재입력
    """
    global shutdown_requested

    # delivery_tag: 메시지의 고유 식별자 (채널 내에서 유일)
    # ACK/NACK 시 이 태그를 사용하여 어떤 메시지인지 지정
    delivery_tag = method.delivery_tag
    routing_key = method.routing_key
    queue_name = method.routing_key  # 기본 Exchange 사용 시 큐 이름 = 라우팅 키

    try:
        # 메시지 본문 디코딩
        message_body = json.loads(body.decode("utf-8"))

        print(f"\n  [수신] delivery_tag={delivery_tag}, "
              f"exchange='{method.exchange}', "
              f"routing_key='{routing_key}'")

        # 메시지 속성 출력 (디버깅용)
        if properties.message_id:
            print(f"    message_id: {properties.message_id}")
        if properties.headers:
            print(f"    headers: {properties.headers}")

        # 큐에 맞는 처리 함수 호출
        # consumer가 직접 큐를 subscribe하므로, 실제 큐 이름으로 처리 함수를 찾음
        # 여기서는 콜백 내에서 큐 이름을 알 수 없으므로 범용 처리
        if "order_id" in message_body:
            process_order(message_body)
        elif "level" in message_body:
            process_log(message_body)
        elif "notification_id" in message_body:
            process_notification(message_body)
        else:
            print(f"    범용 처리: {message_body}")

        # ■■■ ACK (Acknowledgement) ■■■
        # 메시지 처리 성공을 브로커에 알림
        # → 브로커가 큐에서 메시지를 삭제
        # ACK를 보내지 않으면 메시지는 큐에 남아있음 (unacked 상태)
        channel.basic_ack(delivery_tag=delivery_tag)
        print(f"    [ACK] 메시지 처리 완료 (delivery_tag={delivery_tag})")

    except json.JSONDecodeError as e:
        # JSON 파싱 실패: 메시지 형식 오류 → 재처리해도 실패하므로 거부
        print(f"    [에러] JSON 파싱 실패: {e}")
        # basic_reject: 단일 메시지 거부
        # requeue=False: 재입력하지 않음 (Dead Letter Queue로 이동, 설정 시)
        channel.basic_reject(delivery_tag=delivery_tag, requeue=False)
        print(f"    [REJECT] 메시지 거부 (재처리 불가, delivery_tag={delivery_tag})")

    except Exception as e:
        # 처리 중 예외 발생: 일시적 오류일 수 있으므로 재시도
        print(f"    [에러] 메시지 처리 실패: {e}")

        # basic_nack: 메시지 처리 실패 알림
        # requeue=True: 큐의 맨 앞에 다시 넣음 (재시도)
        # requeue=False: 큐에서 제거 (또는 DLQ로 이동)
        # 주의: requeue=True로 무한 재시도되면 장애 발생!
        #       실무에서는 재시도 횟수를 제한하거나 DLQ를 사용
        channel.basic_nack(delivery_tag=delivery_tag, requeue=True)
        print(f"    [NACK] 메시지를 큐에 재입력 (delivery_tag={delivery_tag})")

    # 종료 요청이 있으면 소비 중단
    if shutdown_requested:
        channel.stop_consuming()


def consume_queue(queue_name):
    """
    ■■■ 큐 소비 시작 ■■■

    지정된 큐에서 메시지를 소비합니다.

    QoS (Quality of Service) / Prefetch:
    - prefetch_count: 한 번에 가져올 미확인(unacked) 메시지 수
    - 값이 1이면: 하나씩 처리 (처리 완료 후 다음 메시지)
    - 값이 높으면: 미리 가져와서 빠르게 처리 (처리량 향상)
    - 너무 높으면: 메모리 부족, 다른 컨슈머에 분배 안 됨

    Args:
        queue_name: 소비할 큐 이름
    """
    print(f"\n{'='*60}")
    print(f"■■■ 큐 소비 시작: {queue_name} ■■■")
    print(f"{'='*60}")
    print("Ctrl+C를 눌러 종료할 수 있습니다.\n")

    connection = create_connection()

    try:
        channel = connection.channel()

        # ■■■ QoS (Prefetch) 설정 ■■■
        # prefetch_count=1: 한 번에 1개의 메시지만 가져옴
        # 이전 메시지를 ACK해야 다음 메시지를 받음
        # 작업 시간이 오래 걸리는 경우 적합 (공정한 작업 분배)
        channel.basic_qos(prefetch_count=1)
        print(f"[QoS] prefetch_count=1 설정 (메시지 하나씩 처리)")

        # ■■■ 큐 선언 확인 ■■■
        # passive=True: 큐가 존재하는지만 확인 (없으면 예외)
        # definitions.json에서 미리 생성했으므로 존재해야 함
        try:
            channel.queue_declare(queue=queue_name, passive=True)
            print(f"[큐 확인] '{queue_name}' 큐가 존재합니다.")
        except pika.exceptions.ChannelClosedByBroker:
            print(f"[오류] '{queue_name}' 큐가 존재하지 않습니다!")
            print("  → producer.py를 먼저 실행하거나, definitions.json을 확인하세요.")
            return

        # ■■■ 메시지 소비 시작 ■■■
        # basic_consume: 큐에서 메시지를 비동기로 소비
        # on_message_callback: 메시지 도착 시 호출될 콜백 함수
        # auto_ack=False: 수동 ACK 모드 (메시지 처리 후 직접 ACK)
        #   - True로 설정하면 메시지 수신 즉시 자동 ACK (처리 실패 시 손실)
        consumer_tag = channel.basic_consume(
            queue=queue_name,
            on_message_callback=on_message_callback,
            auto_ack=False,  # 수동 ACK 모드 (프로덕션 권장)
        )
        print(f"[소비] consumer_tag='{consumer_tag}' 로 소비 시작")
        print(f"[대기] 메시지를 기다리고 있습니다...\n")

        # start_consuming(): 메시지를 무한 대기하며 콜백 호출
        # Ctrl+C 또는 channel.stop_consuming()으로 중단
        channel.start_consuming()

    except pika.exceptions.ConnectionClosedByBroker as e:
        print(f"[오류] 브로커에 의해 연결이 종료됨: {e}")
    except pika.exceptions.AMQPChannelError as e:
        print(f"[오류] 채널 에러: {e}")
    except pika.exceptions.AMQPConnectionError as e:
        print(f"[오류] 연결 에러: {e}")
    except Exception as e:
        print(f"[오류] 예상치 못한 오류: {e}")
    finally:
        # 연결 정리
        if connection and connection.is_open:
            connection.close()
        print(f"\n[종료] 컨슈머가 정상적으로 종료되었습니다.")


def main():
    """
    ■■■ 메인 실행 함수 ■■■

    커맨드라인 인자로 소비할 큐를 선택합니다.

    사용법:
        python consumer.py [큐타입]

    큐 타입:
        order        - 주문 처리 큐 (Direct Exchange)
        log-error    - 에러 로그 큐 (Topic Exchange)
        log-all      - 전체 로그 큐 (Topic Exchange)
        notification - 알림 큐 (Fanout Exchange)
    """
    print("=" * 60)
    print("■■■ RabbitMQ Consumer 실습 ■■■")
    print("=" * 60)

    # 커맨드라인 인자 처리
    queue_type = sys.argv[1] if len(sys.argv) > 1 else "order"

    if queue_type not in QUEUE_MAP:
        print(f"[오류] 알 수 없는 큐 타입: '{queue_type}'")
        print(f"[사용법] python consumer.py [{' | '.join(QUEUE_MAP.keys())}]")
        print(f"\n사용 가능한 큐:")
        for key, queue in QUEUE_MAP.items():
            print(f"  {key:15s} → {queue}")
        sys.exit(1)

    queue_name = QUEUE_MAP[queue_type]
    print(f"[설정] 큐 타입: {queue_type} → 큐 이름: {queue_name}")

    # 큐 소비 시작
    consume_queue(queue_name)


if __name__ == "__main__":
    main()
