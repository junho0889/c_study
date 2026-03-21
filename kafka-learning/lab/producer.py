##############################################################################
# ■■■ Kafka Producer 실습 코드 ■■■
#
# 이 스크립트는 Kafka 토픽에 메시지를 발행(Produce)하는 방법을 보여줍니다.
#
# 사전 준비:
#   pip install kafka-python
#
# 실행 방법:
#   python producer.py
#
# 주요 학습 내용:
#   1. KafkaProducer 생성 및 설정
#   2. 토픽 생성 (AdminClient 사용)
#   3. 메시지 전송 (동기/비동기)
#   4. 키 기반 파티셔닝
#   5. 콜백 함수를 통한 전송 결과 확인
##############################################################################

import json
import time
import sys
from datetime import datetime

# kafka-python 라이브러리에서 필요한 클래스 임포트
from kafka import KafkaProducer                    # 메시지 발행자
from kafka.admin import KafkaAdminClient, NewTopic  # 토픽 관리용 Admin 클라이언트
from kafka.errors import (
    TopicAlreadyExistsError,  # 토픽이 이미 존재할 때 발생하는 예외
    NoBrokersAvailable,       # 브로커에 연결할 수 없을 때 발생하는 예외
    KafkaError,               # Kafka 관련 일반 예외
)


# ■■■ 설정 상수 ■■■
# Kafka 브로커 접속 주소 목록 (docker-compose에서 매핑한 외부 포트 사용)
BOOTSTRAP_SERVERS = ["localhost:9092", "localhost:9093", "localhost:9094"]
# 사용할 토픽 이름
TOPIC_NAME = "test-topic"
# 토픽 파티션 수 (병렬 처리 단위)
NUM_PARTITIONS = 3
# 리플리케이션 팩터 (데이터 복제본 수, 브로커 수 이하로 설정)
REPLICATION_FACTOR = 3


def create_topic():
    """
    ■■■ 토픽 생성 함수 ■■■

    KafkaAdminClient를 사용하여 토픽을 프로그래밍 방식으로 생성합니다.
    이미 존재하는 토픽이면 무시합니다.

    토픽 생성 시 고려사항:
    - 파티션 수: 한번 늘리면 줄일 수 없음 (키 기반 파티셔닝 시 주의)
    - 리플리케이션 팩터: 브로커 수 이하로 설정해야 함
    """
    print(f"[토픽 생성] 토픽 '{TOPIC_NAME}' 생성을 시도합니다...")

    try:
        # AdminClient 생성 (브로커 관리 API 사용)
        admin_client = KafkaAdminClient(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            # 클라이언트 식별자 (로그에서 구분용)
            client_id="topic-creator",
        )

        # 새 토픽 정의
        topic = NewTopic(
            name=TOPIC_NAME,
            # 파티션 수: 컨슈머 병렬 처리 수와 동일하게 설정하는 것이 이상적
            num_partitions=NUM_PARTITIONS,
            # 리플리케이션 팩터: 데이터 안정성을 위해 최소 2 이상 권장
            replication_factor=REPLICATION_FACTOR,
            # 토픽 레벨 설정 (글로벌 설정을 오버라이드)
            topic_configs={
                # 메시지 보존 기간 (밀리초): 24시간
                "retention.ms": "86400000",
                # 세그먼트 파일 크기: 100MB
                "segment.bytes": "104857600",
                # 압축 타입: 프로듀서가 보낸 압축 형식 그대로 유지
                "compression.type": "producer",
            },
        )

        # 토픽 생성 요청
        admin_client.create_topics(
            new_topics=[topic],
            # 토픽 생성이 모든 브로커에 전파될 때까지 대기하는 시간 (초)
            validate_only=False,
        )
        print(f"[토픽 생성] 토픽 '{TOPIC_NAME}' 이 성공적으로 생성되었습니다.")
        print(f"  - 파티션 수: {NUM_PARTITIONS}")
        print(f"  - 리플리케이션 팩터: {REPLICATION_FACTOR}")

    except TopicAlreadyExistsError:
        # 토픽이 이미 존재하면 에러가 아니므로 무시
        print(f"[토픽 생성] 토픽 '{TOPIC_NAME}' 이 이미 존재합니다. 건너뜁니다.")
    except NoBrokersAvailable:
        print("[오류] Kafka 브로커에 연결할 수 없습니다!")
        print("  → docker-compose up -d 로 Kafka를 먼저 시작하세요.")
        sys.exit(1)
    finally:
        # AdminClient 리소스 정리
        if "admin_client" in locals():
            admin_client.close()


def on_send_success(record_metadata):
    """
    ■■■ 전송 성공 콜백 함수 ■■■

    비동기 전송이 성공했을 때 호출되는 콜백입니다.
    record_metadata에서 전송 결과 정보를 확인할 수 있습니다.

    Args:
        record_metadata: 전송된 메시지의 메타데이터
            - topic: 토픽 이름
            - partition: 저장된 파티션 번호
            - offset: 파티션 내 오프셋 (메시지 순서 번호)
    """
    print(
        f"  [전송 성공] 토픽={record_metadata.topic}, "
        f"파티션={record_metadata.partition}, "
        f"오프셋={record_metadata.offset}"
    )


def on_send_error(exception):
    """
    ■■■ 전송 실패 콜백 함수 ■■■

    비동기 전송이 실패했을 때 호출됩니다.
    실패 원인을 로깅하고 적절한 재시도/알림 처리를 해야 합니다.

    Args:
        exception: 발생한 예외 객체
    """
    print(f"  [전송 실패] 에러: {exception}")


def create_producer():
    """
    ■■■ KafkaProducer 생성 함수 ■■■

    프로듀서 인스턴스를 생성하고 주요 설정을 적용합니다.
    각 설정값의 의미와 프로덕션 권장값을 주석으로 설명합니다.

    Returns:
        KafkaProducer: 설정이 완료된 프로듀서 인스턴스
    """
    producer = KafkaProducer(
        # 브로커 접속 주소 목록
        bootstrap_servers=BOOTSTRAP_SERVERS,

        # ── 직렬화 설정 ──
        # key_serializer: 메시지 키를 바이트로 변환하는 함수
        # 키는 파티션 결정에 사용됨 (같은 키 → 같은 파티션)
        key_serializer=lambda k: k.encode("utf-8") if k else None,
        # value_serializer: 메시지 값을 바이트로 변환하는 함수
        # JSON 직렬화를 사용하여 구조화된 데이터 전송
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),

        # ── 안정성 설정 ──
        # acks: 프로듀서가 메시지 전송 완료로 간주하는 조건
        #   0: 브로커 응답을 기다리지 않음 (가장 빠르지만 데이터 손실 가능)
        #   1: 리더 브로커만 확인 (리더 장애 시 데이터 손실 가능)
        #   'all'(-1): 모든 ISR이 확인 (가장 안전, 프로덕션 권장)
        acks="all",

        # 전송 실패 시 재시도 횟수 (네트워크 일시 장애 대비)
        retries=3,
        # 재시도 간격 (밀리초) - 너무 짧으면 브로커에 부담
        retry_backoff_ms=100,

        # ── 배치 설정 (처리량 최적화) ──
        # batch_size: 같은 파티션으로 가는 메시지를 모아서 한번에 전송하는 크기 (바이트)
        # 16384 = 16KB (기본값)
        batch_size=16384,
        # linger_ms: 배치를 채우기 위해 대기하는 시간 (밀리초)
        # 0이면 즉시 전송, 값이 클수록 배치 효율 증가하지만 지연시간도 증가
        linger_ms=10,
        # buffer_memory: 프로듀서의 전체 전송 버퍼 크기 (바이트)
        # 33554432 = 32MB (기본값)
        buffer_memory=33554432,

        # ── 압축 설정 ──
        # 메시지 압축 방식 (none, gzip, snappy, lz4, zstd)
        # gzip: 높은 압축률, CPU 사용 높음
        # snappy: 낮은 CPU, 적당한 압축률 (프로덕션 권장)
        # lz4: 가장 빠른 압축/해제 속도
        compression_type="gzip",

        # ── 멱등성(Idempotence) 설정 ──
        # enable_idempotence=True: 네트워크 재시도로 인한 메시지 중복 방지
        # acks='all', retries > 0 일 때 사용 가능
        enable_idempotence=True,

        # 클라이언트 식별자
        client_id="python-producer",
    )

    print("[프로듀서] KafkaProducer가 생성되었습니다.")
    return producer


def send_messages_sync(producer, count=5):
    """
    ■■■ 동기 방식 메시지 전송 ■■■

    .get() 메서드를 호출하여 브로커의 응답을 기다립니다.
    전송 결과를 즉시 확인할 수 있지만 처리량이 낮습니다.

    사용 사례: 메시지 순서가 중요하거나, 전송 실패를 즉시 처리해야 할 때

    Args:
        producer: KafkaProducer 인스턴스
        count: 전송할 메시지 수
    """
    print(f"\n{'='*60}")
    print(f"■■■ 동기 전송 시작 (총 {count}건) ■■■")
    print(f"{'='*60}")

    for i in range(count):
        # 전송할 메시지 데이터 구성
        message = {
            "id": i + 1,
            "type": "sync",
            "content": f"동기 전송 메시지 #{i + 1}",
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # .send()는 Future 객체를 반환
            # .get(timeout=10)으로 최대 10초간 브로커 응답 대기
            future = producer.send(TOPIC_NAME, value=message)
            record_metadata = future.get(timeout=10)

            print(
                f"  [동기 전송 #{i+1}] "
                f"파티션={record_metadata.partition}, "
                f"오프셋={record_metadata.offset}"
            )
        except KafkaError as e:
            # 전송 실패 시 예외 처리
            print(f"  [동기 전송 실패 #{i+1}] {e}")

    print(f"[동기 전송 완료] {count}건 전송 완료")


def send_messages_async(producer, count=5):
    """
    ■■■ 비동기 방식 메시지 전송 ■■■

    콜백 함수를 등록하여 전송 결과를 비동기로 처리합니다.
    처리량이 높지만 전송 순서를 보장하기 어렵습니다.

    사용 사례: 대량 메시지 전송, 로그 수집 등 처리량이 중요한 경우

    Args:
        producer: KafkaProducer 인스턴스
        count: 전송할 메시지 수
    """
    print(f"\n{'='*60}")
    print(f"■■■ 비동기 전송 시작 (총 {count}건) ■■■")
    print(f"{'='*60}")

    for i in range(count):
        message = {
            "id": i + 1,
            "type": "async",
            "content": f"비동기 전송 메시지 #{i + 1}",
            "timestamp": datetime.now().isoformat(),
        }

        # .send() 후 .add_callback() / .add_errback()으로 콜백 등록
        # 전송 결과가 나오면 자동으로 콜백 함수가 호출됨
        producer.send(TOPIC_NAME, value=message)\
            .add_callback(on_send_success)\
            .add_errback(on_send_error)

        print(f"  [비동기 전송 #{i+1}] 메시지를 버퍼에 추가했습니다.")

    # flush(): 버퍼에 남아있는 모든 메시지를 브로커로 전송하고 완료될 때까지 대기
    # 프로그램 종료 전 반드시 호출해야 데이터 손실 방지
    producer.flush()
    print(f"[비동기 전송 완료] flush() 완료 - 모든 메시지가 브로커에 전달됨")


def send_messages_with_key(producer, count=10):
    """
    ■■■ 키 기반 파티셔닝 메시지 전송 ■■■

    메시지 키를 지정하면 같은 키를 가진 메시지는 항상 같은 파티션으로 전송됩니다.
    이를 통해 특정 키에 대한 메시지 순서를 보장할 수 있습니다.

    파티셔닝 원리:
    - 키의 해시값을 파티션 수로 나눈 나머지 → 파티션 번호
    - hash(key) % num_partitions = target_partition

    사용 사례:
    - 사용자별 이벤트 순서 보장 (key=user_id)
    - 주문별 상태 변경 순서 보장 (key=order_id)

    Args:
        producer: KafkaProducer 인스턴스
        count: 전송할 메시지 수
    """
    print(f"\n{'='*60}")
    print(f"■■■ 키 기반 파티셔닝 전송 시작 (총 {count}건) ■■■")
    print(f"{'='*60}")

    # 3개의 사용자 키를 순환하며 메시지 전송
    # 같은 user_id를 가진 메시지는 같은 파티션에 저장됨
    user_ids = ["user-A", "user-B", "user-C"]

    for i in range(count):
        # 순환적으로 사용자 키 선택
        user_id = user_ids[i % len(user_ids)]

        message = {
            "id": i + 1,
            "user_id": user_id,
            "action": f"사용자 행동 이벤트 #{i + 1}",
            "timestamp": datetime.now().isoformat(),
        }

        # key 파라미터: 파티셔닝 기준이 되는 키 (문자열)
        # 같은 key → 같은 파티션 → 순서 보장
        future = producer.send(TOPIC_NAME, key=user_id, value=message)
        record_metadata = future.get(timeout=10)

        print(
            f"  [키 전송 #{i+1}] "
            f"키={user_id}, "
            f"파티션={record_metadata.partition}, "
            f"오프셋={record_metadata.offset}"
        )

    print(f"\n[키 전송 완료] 같은 키를 가진 메시지들이 같은 파티션에 저장된 것을 확인하세요!")


def main():
    """
    ■■■ 메인 실행 함수 ■■■

    실행 순서:
    1. 토픽 생성
    2. 프로듀서 생성
    3. 동기 전송 테스트
    4. 비동기 전송 테스트
    5. 키 기반 파티셔닝 테스트
    6. 프로듀서 종료
    """
    print("=" * 60)
    print("■■■ Kafka Producer 실습 시작 ■■■")
    print("=" * 60)

    # 1단계: 토픽 생성
    create_topic()

    # 토픽이 모든 브로커에 전파될 시간을 잠시 대기
    time.sleep(2)

    # 2단계: 프로듀서 생성
    producer = create_producer()

    try:
        # 3단계: 동기 방식 메시지 전송
        send_messages_sync(producer, count=5)

        # 4단계: 비동기 방식 메시지 전송
        send_messages_async(producer, count=5)

        # 5단계: 키 기반 파티셔닝 메시지 전송
        send_messages_with_key(producer, count=10)

    except KeyboardInterrupt:
        print("\n[중단] 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n[오류] 예상치 못한 오류 발생: {e}")
    finally:
        # 6단계: 프로듀서 종료
        # close()는 내부적으로 flush()를 호출하고 리소스를 정리함
        producer.close()
        print("\n[종료] 프로듀서가 정상적으로 종료되었습니다.")


# 스크립트 직접 실행 시 main() 호출
if __name__ == "__main__":
    main()
