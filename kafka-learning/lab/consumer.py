##############################################################################
# ■■■ Kafka Consumer 실습 코드 ■■■
#
# 이 스크립트는 Kafka 토픽에서 메시지를 소비(Consume)하는 방법을 보여줍니다.
#
# 사전 준비:
#   pip install kafka-python
#
# 실행 방법:
#   python consumer.py
#
# 주요 학습 내용:
#   1. KafkaConsumer 생성 및 설정
#   2. Consumer Group을 통한 메시지 분산 처리
#   3. 오프셋 관리 (자동/수동 커밋)
#   4. 파티션 할당 및 리밸런싱
#   5. 에러 핸들링 및 그레이스풀 셧다운
##############################################################################

import json
import signal
import sys
import time
from datetime import datetime

from kafka import KafkaConsumer, TopicPartition
from kafka.errors import (
    KafkaError,
    NoBrokersAvailable,
    CommitFailedError,
)


# ■■■ 설정 상수 ■■■
# Kafka 브로커 접속 주소 (docker-compose 외부 포트)
BOOTSTRAP_SERVERS = ["localhost:9092", "localhost:9093", "localhost:9094"]
# 구독할 토픽 이름 (producer.py에서 생성한 토픽)
TOPIC_NAME = "test-topic"
# 컨슈머 그룹 ID
# 같은 그룹의 컨슈머들은 파티션을 분배받아 병렬 처리
# 다른 그룹은 동일한 메시지를 독립적으로 소비 가능
CONSUMER_GROUP = "test-consumer-group"


# ■■■ 그레이스풀 셧다운을 위한 플래그 ■■■
# Ctrl+C (SIGINT) 시 안전하게 종료하기 위한 전역 변수
running = True


def signal_handler(signum, frame):
    """
    ■■■ 시그널 핸들러 ■■■

    Ctrl+C (SIGINT) 를 받으면 컨슈머를 안전하게 종료합니다.
    즉시 종료하면 처리 중인 메시지가 손실될 수 있으므로,
    running 플래그를 False로 변경하여 폴링 루프를 종료합니다.

    그레이스풀 셧다운의 중요성:
    - 처리 중인 메시지의 오프셋 커밋 보장
    - 컨슈머 그룹에서의 정상적인 탈퇴 (리밸런싱 트리거)
    - 리소스 (네트워크 연결, 파일 핸들) 정리
    """
    global running
    print("\n[시그널] 종료 시그널을 받았습니다. 안전하게 종료 중...")
    running = False


# SIGINT (Ctrl+C) 시그널에 핸들러 등록
signal.signal(signal.SIGINT, signal_handler)


def create_auto_commit_consumer():
    """
    ■■■ 자동 오프셋 커밋 컨슈머 생성 ■■■

    enable_auto_commit=True 로 설정하면 일정 간격으로 자동으로 오프셋을 커밋합니다.

    장점: 구현이 간단
    단점: 메시지 처리 전에 오프셋이 커밋될 수 있음 (at-most-once 의미론)
         또는 중복 처리 가능 (at-least-once 의미론)

    Returns:
        KafkaConsumer: 자동 커밋이 설정된 컨슈머 인스턴스
    """
    consumer = KafkaConsumer(
        # 구독할 토픽 이름 (여러 토픽을 동시에 구독 가능)
        TOPIC_NAME,

        # 브로커 접속 주소 목록
        bootstrap_servers=BOOTSTRAP_SERVERS,

        # ── 컨슈머 그룹 설정 ──
        # 같은 group_id를 가진 컨슈머들은 파티션을 나누어 소비
        # 각 파티션은 그룹 내 하나의 컨슈머에게만 할당됨
        group_id=CONSUMER_GROUP,

        # ── 역직렬화 설정 ──
        # value_deserializer: 바이트 → Python 객체 변환
        # producer에서 JSON으로 직렬화했으므로 JSON으로 역직렬화
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        # key_deserializer: 키 바이트 → 문자열 변환
        key_deserializer=lambda k: k.decode("utf-8") if k else None,

        # ── 오프셋 설정 ──
        # auto_offset_reset: 저장된 오프셋이 없을 때 어디서부터 읽을지 결정
        #   'earliest': 가장 처음부터 (모든 메시지 읽기)
        #   'latest': 가장 최근부터 (새 메시지만 읽기)
        #   'none': 저장된 오프셋이 없으면 예외 발생
        auto_offset_reset="earliest",

        # ── 자동 커밋 설정 ──
        # enable_auto_commit=True: 오프셋을 자동으로 커밋
        enable_auto_commit=True,
        # auto_commit_interval_ms: 자동 커밋 간격 (밀리초)
        # 5000ms = 5초마다 현재까지 읽은 오프셋을 커밋
        auto_commit_interval_ms=5000,

        # ── 세션 관리 설정 ──
        # session_timeout_ms: 하트비트 없이 이 시간이 지나면 컨슈머가 죽은 것으로 판단
        # → 해당 컨슈머의 파티션이 다른 컨슈머에게 재할당 (리밸런싱)
        session_timeout_ms=30000,
        # heartbeat_interval_ms: 컨슈머가 브로커에 보내는 하트비트 간격
        # session_timeout_ms의 1/3 이하로 설정 권장
        heartbeat_interval_ms=10000,

        # ── 페치(Fetch) 설정 ──
        # max_poll_records: poll() 한 번에 가져오는 최대 레코드 수
        # 값이 작으면 자주 poll() 해야 하고, 크면 처리 시간이 길어짐
        max_poll_records=100,
        # fetch_max_bytes: 한 번의 fetch 요청으로 가져올 최대 데이터 크기 (바이트)
        fetch_max_bytes=1048576,  # 1MB
        # max_partition_fetch_bytes: 파티션 당 최대 fetch 크기
        max_partition_fetch_bytes=1048576,  # 1MB

        # ── 기타 설정 ──
        # 클라이언트 식별자
        client_id="python-consumer-auto",
        # consumer_timeout_ms: poll()에서 메시지를 기다리는 최대 시간
        # 이 시간 동안 메시지가 없으면 빈 결과 반환
        consumer_timeout_ms=1000,
    )

    print("[컨슈머] 자동 커밋 컨슈머가 생성되었습니다.")
    return consumer


def create_manual_commit_consumer():
    """
    ■■■ 수동 오프셋 커밋 컨슈머 생성 ■■■

    enable_auto_commit=False 로 설정하고, 메시지 처리 후 직접 commit()을 호출합니다.

    장점: 메시지 처리 완료 후에만 커밋하므로 데이터 손실 최소화
    단점: 커밋을 직접 관리해야 하므로 구현이 복잡

    Returns:
        KafkaConsumer: 수동 커밋이 설정된 컨슈머 인스턴스
    """
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id=f"{CONSUMER_GROUP}-manual",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        key_deserializer=lambda k: k.decode("utf-8") if k else None,
        auto_offset_reset="earliest",
        # 자동 커밋 비활성화 → 수동으로 커밋해야 함
        enable_auto_commit=False,
        session_timeout_ms=30000,
        heartbeat_interval_ms=10000,
        max_poll_records=10,
        client_id="python-consumer-manual",
        consumer_timeout_ms=1000,
    )

    print("[컨슈머] 수동 커밋 컨슈머가 생성되었습니다.")
    return consumer


def consume_with_auto_commit():
    """
    ■■■ 자동 커밋 모드로 메시지 소비 ■■■

    가장 기본적인 컨슈머 패턴입니다.
    메시지를 읽고 처리하면, 일정 간격으로 오프셋이 자동 커밋됩니다.

    주의: 자동 커밋 간격(5초) 사이에 컨슈머가 죽으면,
    이미 처리한 메시지를 다시 처리할 수 있습니다 (at-least-once).
    """
    global running

    print(f"\n{'='*60}")
    print("■■■ 자동 커밋 컨슈머 시작 ■■■")
    print(f"{'='*60}")
    print(f"토픽: {TOPIC_NAME}")
    print(f"컨슈머 그룹: {CONSUMER_GROUP}")
    print("Ctrl+C를 눌러 종료할 수 있습니다.\n")

    try:
        consumer = create_auto_commit_consumer()
    except NoBrokersAvailable:
        print("[오류] Kafka 브로커에 연결할 수 없습니다!")
        print("  → docker-compose up -d 로 Kafka를 먼저 시작하세요.")
        return

    # 수신한 총 메시지 수 카운터
    message_count = 0

    try:
        while running:
            # poll(): 브로커에서 메시지를 가져옴
            # timeout_ms: 메시지가 없을 때 대기하는 시간
            # 반환값: {TopicPartition: [ConsumerRecord, ...]} 딕셔너리
            message_batch = consumer.poll(timeout_ms=1000)

            # 가져온 메시지가 없으면 다음 폴링
            if not message_batch:
                continue

            # 파티션별로 메시지 처리
            for topic_partition, messages in message_batch.items():
                for message in messages:
                    message_count += 1
                    # ConsumerRecord의 주요 속성:
                    # - topic: 토픽 이름
                    # - partition: 파티션 번호
                    # - offset: 파티션 내 오프셋 (순서 번호)
                    # - key: 메시지 키 (파티셔닝에 사용)
                    # - value: 메시지 값 (실제 데이터)
                    # - timestamp: 메시지 타임스탬프
                    print(
                        f"  [메시지 #{message_count}] "
                        f"토픽={message.topic}, "
                        f"파티션={message.partition}, "
                        f"오프셋={message.offset}, "
                        f"키={message.key}"
                    )
                    print(f"    값: {message.value}")

    except Exception as e:
        print(f"[오류] 메시지 소비 중 오류 발생: {e}")
    finally:
        # 컨슈머 종료: 그룹에서 탈퇴하고 리소스 정리
        consumer.close()
        print(f"\n[종료] 자동 커밋 컨슈머 종료. 총 {message_count}건 처리.")


def consume_with_manual_commit():
    """
    ■■■ 수동 커밋 모드로 메시지 소비 ■■■

    메시지를 처리한 후 직접 오프셋을 커밋합니다.
    이를 통해 메시지 처리 완료를 보장할 수 있습니다.

    오프셋 커밋 방식:
    1. commitSync(): 동기 커밋 - 커밋 완료까지 블로킹 (안전하지만 느림)
    2. commitAsync(): 비동기 커밋 - 백그라운드 커밋 (빠르지만 실패 감지 어려움)
    """
    global running
    running = True  # 플래그 초기화

    print(f"\n{'='*60}")
    print("■■■ 수동 커밋 컨슈머 시작 ■■■")
    print(f"{'='*60}")
    print(f"토픽: {TOPIC_NAME}")
    print(f"컨슈머 그룹: {CONSUMER_GROUP}-manual")
    print("Ctrl+C를 눌러 종료할 수 있습니다.\n")

    try:
        consumer = create_manual_commit_consumer()
    except NoBrokersAvailable:
        print("[오류] Kafka 브로커에 연결할 수 없습니다!")
        return

    message_count = 0

    try:
        while running:
            message_batch = consumer.poll(timeout_ms=1000)

            if not message_batch:
                continue

            for topic_partition, messages in message_batch.items():
                for message in messages:
                    message_count += 1

                    # ── 메시지 처리 (비즈니스 로직) ──
                    try:
                        print(
                            f"  [수동커밋 #{message_count}] "
                            f"파티션={message.partition}, "
                            f"오프셋={message.offset}, "
                            f"키={message.key}"
                        )
                        print(f"    값: {message.value}")

                        # 여기에 실제 비즈니스 로직을 구현
                        # 예: 데이터베이스 저장, API 호출, 파일 쓰기 등
                        process_message(message)

                    except Exception as e:
                        # 메시지 처리 실패 시 → 오프셋을 커밋하지 않음
                        # → 다음 폴링에서 같은 메시지를 다시 받을 수 있음
                        print(f"    [처리 실패] {e}")
                        # Dead Letter Queue(DLQ)로 실패 메시지를 보내는 것을 권장
                        continue

            # ── 배치 단위 오프셋 커밋 ──
            # poll()로 가져온 모든 메시지를 처리한 후 한번에 커밋
            try:
                # commitSync(): 커밋이 완료될 때까지 블로킹
                # 커밋 실패 시 CommitFailedError 예외 발생
                consumer.commit()
                print(f"    [커밋 완료] 오프셋 커밋 성공")
            except CommitFailedError as e:
                # 리밸런싱 중에 커밋하면 실패할 수 있음
                print(f"    [커밋 실패] {e}")

    except Exception as e:
        print(f"[오류] 메시지 소비 중 오류 발생: {e}")
    finally:
        # 종료 전 마지막으로 오프셋 커밋 시도
        try:
            consumer.commit()
        except Exception:
            pass
        consumer.close()
        print(f"\n[종료] 수동 커밋 컨슈머 종료. 총 {message_count}건 처리.")


def process_message(message):
    """
    ■■■ 메시지 처리 함수 (비즈니스 로직) ■■■

    실제 서비스에서는 여기에 비즈니스 로직을 구현합니다.

    예시:
    - 데이터베이스에 메시지 저장
    - 외부 API 호출
    - 다른 시스템으로 메시지 전달
    - 집계/통계 처리

    Args:
        message: ConsumerRecord 객체
    """
    # 실습에서는 단순히 메시지 내용을 출력
    data = message.value

    # 메시지 타입에 따라 다른 처리 수행 (예시)
    if isinstance(data, dict):
        msg_type = data.get("type", "unknown")
        content = data.get("content", "")
        # 실제로는 여기에 비즈니스 로직 구현
        # 예: if msg_type == "order": save_to_db(data)

    # 처리 시뮬레이션 (실제 서비스에서는 제거)
    # time.sleep(0.1)


def check_consumer_group_info(consumer):
    """
    ■■■ 컨슈머 그룹 정보 확인 ■■■

    현재 컨슈머에 할당된 파티션과 오프셋 정보를 출력합니다.
    모니터링 및 디버깅에 유용합니다.

    Args:
        consumer: KafkaConsumer 인스턴스
    """
    print(f"\n{'='*60}")
    print("■■■ 컨슈머 그룹 정보 ■■■")
    print(f"{'='*60}")

    # 현재 컨슈머에 할당된 파티션 목록
    assigned = consumer.assignment()
    print(f"할당된 파티션: {assigned}")

    # 각 파티션의 현재 오프셋 위치 확인
    for tp in assigned:
        # position(): 다음에 읽을 오프셋
        position = consumer.position(tp)
        # committed(): 마지막으로 커밋된 오프셋
        committed = consumer.committed(tp)
        print(
            f"  파티션 {tp.partition}: "
            f"현재 위치={position}, "
            f"커밋된 오프셋={committed}"
        )


def main():
    """
    ■■■ 메인 실행 함수 ■■■

    실행 모드를 선택하여 컨슈머를 시작합니다.

    사용법:
        python consumer.py           # 자동 커밋 모드 (기본)
        python consumer.py auto      # 자동 커밋 모드
        python consumer.py manual    # 수동 커밋 모드
    """
    print("=" * 60)
    print("■■■ Kafka Consumer 실습 ■■■")
    print("=" * 60)

    # 커맨드라인 인자로 모드 선택
    mode = sys.argv[1] if len(sys.argv) > 1 else "auto"

    if mode == "manual":
        print("[모드] 수동 커밋 모드로 시작합니다.")
        consume_with_manual_commit()
    else:
        print("[모드] 자동 커밋 모드로 시작합니다.")
        print("  → 수동 커밋 모드: python consumer.py manual")
        consume_with_auto_commit()


if __name__ == "__main__":
    main()
