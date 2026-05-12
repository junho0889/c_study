# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [데이터 연계] 학습 16단계: 메시지 & 스트리밍
#   ─ Kafka · Kinesis · Pub/Sub · exactly-once · Schema Registry ─
#   ■ 실행 방법: python 16_messaging_streaming.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 메시지 큐의 두 모델 — Queue vs Log
#   2. Apache Kafka 핵심 개념 (Topic / Partition / Offset / Consumer Group)
#   3. 클라우드 매니지드 — Kinesis / Pub/Sub / EventBridge
#   4. 전달 보장: at-most / at-least / exactly-once
#   5. Schema Registry 와 호환성
#   6. 스트림 처리 — Kafka Streams / Flink / Spark Structured Streaming
#   7. 실전: producer → consumer 시뮬레이션 + 오프셋 관리
#
# ─────────────────────────────────────────────────────────────────────────


def lesson1_two_models():
    # =========================================================================
    #   레슨 1 — 메시지 큐 두 모델
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : Queue vs Log               │")
    print("└──────────────────────────────────────┘")
    # ■ Queue 모델 (RabbitMQ, SQS):
    #   - 메시지가 소비되면 큐에서 제거
    #   - 1개 메시지 = 1 소비자
    #   - 잡 큐(job queue) 에 적합
    #
    # ■ Log 모델 (Kafka, Kinesis, Pub/Sub Lite):
    #   - 메시지는 디스크 로그에 ‘영구 저장’
    #   - 여러 소비자(그룹) 가 독립적으로 자신만의 오프셋 진행
    #   - 이벤트 소싱 / 다중 소비 / 재처리에 강함
    print(" 잡 큐 = Queue 모델, 이벤트 스트리밍 = Log 모델. 둘은 본질이 다르다.")
    print()


def lesson2_kafka():
    # =========================================================================
    #   레슨 2 — Kafka 핵심
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : Kafka                      │")
    print("└──────────────────────────────────────┘")
    # ■ Topic    : 메시지의 ‘카테고리’
    # ■ Partition: 토픽을 N 조각으로 나눠 ‘병렬성’ 확보
    # ■ Offset   : 파티션 내부의 순번
    # ■ Producer : 메시지를 토픽에 발행. key 가 같으면 같은 파티션 → 순서 보장
    # ■ Consumer Group: 같은 그룹 내 소비자는 ‘파티션을 나눠 가짐’
    # ■ Broker   : 파티션을 호스팅하는 서버 (보통 3+ 복제)
    #
    # ■ 보관:
    #   - retention.ms (기간) 또는 retention.bytes (용량)
    #   - 압축 보존(compact) 모드: 키 별 최신 1개만 유지 (CDC 단일 진실)
    print(" Kafka 4 핵심: Topic / Partition / Offset / Consumer Group.  나머지는 다 응용.")
    print()


def lesson3_cloud_managed():
    # =========================================================================
    #   레슨 3 — Kinesis / Pub/Sub / EventBridge
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : 매니지드 서비스            │")
    print("└──────────────────────────────────────┘")
    # ■ Kinesis Data Streams (AWS):
    #   - Kafka 와 유사한 ‘샤드 + 시퀀스 번호’
    #   - Lambda/Glue 와 결합이 매끄러움
    # ■ Pub/Sub (GCP):
    #   - 자동 확장. 순서 보장은 ‘ordering key’ 필요
    # ■ EventBridge (AWS):
    #   - “SaaS / AWS 이벤트의 라우터”. 룰 기반 분기
    # ■ Confluent Cloud / Aiven / Redpanda Cloud:
    #   - 매니지드 Kafka. Kafka 표준 호환.
    #
    # ■ 선택 기준:
    #   - Kafka 생태계 강력 필요 → Confluent
    #   - AWS 기반 + 단순함 → Kinesis
    #   - GCP + 글로벌/자동확장 → Pub/Sub
    print(" 매니지드는 운영 단순화의 큰 가치.  운영 인력이 작으면 강력 권장.")
    print()


def lesson4_delivery_semantics():
    # =========================================================================
    #   레슨 4 — 전달 보장
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : 전달 보장                  │")
    print("└──────────────────────────────────────┘")
    # ■ At-most-once: 한 번 또는 0번. 메시지 손실 가능.
    # ■ At-least-once: 최소 1번 (중복 가능).  실무 표준 + dedupe 결합.
    # ■ Exactly-once: 정확히 1번.  Kafka 의 transactional producer + Idempotent producer + transactional consumer.
    #
    # ■ 실무 권장:
    #   - Producer: enable.idempotence=true (중복 발행 방지)
    #   - 트랜잭션 필요(컨슈머→프로듀서 체인) → transactional API
    #   - 단순 운영은 ‘at-least-once + 멱등 적재’
    print(" Exactly-once 는 ‘닫힌 시스템’(Kafka 내부) 에서만 진짜 보장.  외부 시스템 끝까지는 결국 멱등.")
    print()


def lesson5_schema_registry():
    # =========================================================================
    #   레슨 5 — Schema Registry
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : Schema Registry            │")
    print("└──────────────────────────────────────┘")
    # ■ 목적:
    #   - Producer/Consumer 가 ‘서로 다른 시간에 배포’ 되어도 호환성 보장
    #
    # ■ 방식:
    #   - Avro/Protobuf/JSON Schema 를 중앙에 등록
    #   - 메시지 앞 4 byte 에 schema id → 디시리얼라이저가 자동 조회
    #
    # ■ 호환성 모드(02단계 복습): BACKWARD / FORWARD / FULL / NONE
    #
    # ■ 권장:
    #   - 운영 토픽은 BACKWARD 또는 FULL
    #   - PR 단계에서 호환성 검사 자동화 (CI)
    print(" Schema Registry = ‘토픽의 API 명세’.  없으면 시간이 지나며 카오스.")
    print()


def lesson6_stream_processing():
    # =========================================================================
    #   레슨 6 — 스트림 처리
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 스트림 처리                │")
    print("└──────────────────────────────────────┘")
    # ■ Kafka Streams:
    #   - JVM 라이브러리. 토픽 → 토픽 변환.
    # ■ Apache Flink:
    #   - 상태/시간/EXACTLY-ONCE 가 가장 성숙. 대규모 표준.
    # ■ Spark Structured Streaming:
    #   - 마이크로 배치 + 연속 모드. 기존 Spark 자산 재사용.
    # ■ Materialize / RisingWave / Pinot / Druid:
    #   - 실시간 분석 SQL 데이터베이스
    #
    # ■ 핵심 개념:
    #   - Event time vs Processing time
    #   - Watermark (지연 허용 한도)
    #   - Stateful operator + RocksDB 백엔드
    print(" 실시간 SQL 의 새 흐름: ‘Materialize / Pinot / Druid 와 Kafka 의 결합’.")
    print()


def lesson7_practice_pub_sub_sim():
    # =========================================================================
    #   레슨 7 — producer/consumer 시뮬레이션
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 시뮬레이션                 │")
    print("└──────────────────────────────────────┘")
    # 토픽 = 리스트, 오프셋 = 인덱스
    topic = []

    def produce(msg, key=None):
        topic.append({"offset": len(topic), "key": key, "value": msg})

    # 그룹 별 오프셋 추적
    group_offsets = {"order-loader": 0, "audit-logger": 0}

    def consume(group):
        off = group_offsets[group]
        records = topic[off:]
        # 처리 후 commit
        for r in records:
            print(f"  [{group}] consumed offset={r['offset']} value={r['value']}")
        group_offsets[group] = len(topic)
        return len(records)

    # 발행
    for i in range(5):
        produce({"id": i, "amount": i * 10})

    # 두 개의 그룹이 같은 데이터를 ‘각자 진행’
    consume("order-loader")
    consume("audit-logger")
    # 새 메시지 추가
    produce({"id": 5, "amount": 50})
    # order-loader 만 따라잡음
    consume("order-loader")
    # audit-logger 는 잠시 셧다운이었다 가정
    print(" 현재 group offsets:", group_offsets)
    print()
    # → Log 모델의 본질: ‘하나의 진실 + 그룹별 독립 진행’.


# ─────────────────────────────────────────────────────────────────────────
# ■ 연습문제
# ─────────────────────────────────────────────────────────────────────────
#  Q1. Kafka 파티션 수를 무작정 늘리면 어떤 부작용이 생기나?
#  Q2. 압축 토픽(compact) 의 사용 사례 한 가지를 적어라.
#  Q3. Exactly-once 가 ‘외부 시스템까지’ 보장 안 되는 이유와 그 보완책?
#  Q4. Watermark 가 너무 크면/작으면 각각 어떤 trade-off?
#  Q5. 위 시뮬레이션에서 ‘consumer crash → 재시작’ 을 추가하려면 어떤 코드가 필요?


if __name__ == "__main__":
    lesson1_two_models()
    lesson2_kafka()
    lesson3_cloud_managed()
    lesson4_delivery_semantics()
    lesson5_schema_registry()
    lesson6_stream_processing()
    lesson7_practice_pub_sub_sim()
