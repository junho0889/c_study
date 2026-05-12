# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [데이터 연계] 학습 07단계: CDC (Change Data Capture)
#   ─ Debezium · log-based · outbox · 멱등 적재 ─
#   ■ 실행 방법: python 07_cdc.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 왜 CDC 인가 — high-watermark 의 한계
#   2. CDC 의 3 가지 방식 (timestamp / trigger / log)
#   3. Debezium 한 줄 그림
#   4. Outbox 패턴 — 어플리케이션과 함께 트랜잭션으로 발행
#   5. CDC 적재의 멱등성 — primary key + 최신성
#   6. 사용 사례 — 검색/캐시 동기화, 마이크로서비스 통합
#   7. 실전: CDC 이벤트 시퀀스 시뮬레이션
#
# ─────────────────────────────────────────────────────────────────────────


def lesson1_why_cdc():
    # =========================================================================
    #   레슨 1 — 왜 CDC?
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 왜 CDC                     │")
    print("└──────────────────────────────────────┘")
    # ■ Polling(타임스탬프) 방식의 문제:
    #   - 짧은 주기 → DB 부하
    #   - 긴 주기 → latency
    #   - DELETE 캐치 어려움 (updated_at 이 사라지므로)
    #   - 시계열 정합성/순서 보장 X
    #
    # ■ CDC:
    #   - DB 의 트랜잭션 로그(WAL/binlog) 를 읽어 INSERT/UPDATE/DELETE 이벤트로 변환
    #   - 거의 실시간, 순서 보장, DELETE 캐치 가능
    print(" CDC = ‘DB 의 일기장’을 읽는다.  실시간 + DELETE + 순서 보장.")
    print()


def lesson2_three_ways():
    # =========================================================================
    #   레슨 2 — CDC 3 방식
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : 3 가지 방식                │")
    print("└──────────────────────────────────────┘")
    # ■ 1) Timestamp-based:
    #   - WHERE updated_at > :last  — 가장 단순. 단점은 위와 같음.
    #
    # ■ 2) Trigger-based:
    #   - 모든 변경에 트리거가 ‘로그 테이블’에 기록
    #   - 단점: 트리거 자체가 DB 부하
    #
    # ■ 3) Log-based (CDC 의 표준):
    #   - MySQL binlog, PostgreSQL WAL, Oracle redo, SQL Server CDC
    #   - DB 운영에 부담 거의 없음
    #   - Debezium 이 대표 오픈소스 커넥터
    print(" 운영 표준 = log-based.  Debezium + Kafka 가 가장 흔한 조합.")
    print()


def lesson3_debezium():
    # =========================================================================
    #   레슨 3 — Debezium
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : Debezium 그림              │")
    print("└──────────────────────────────────────┘")
    diagram = r"""
   +-------------------+        +-----------------+        +-------------------+
   |  PostgreSQL/MySQL |  WAL/  |    Debezium     |  Kafka |   Consumer        |
   |       (운영 DB)   |─binlog─▶  (Connector)   ▶ Topic ▶│ (DW, 검색, 캐시) │
   +-------------------+        +-----------------+        +-------------------+
                              (LSN / GTID 체크포인트)
"""
    print(diagram)
    # ■ 토픽 구조:
    #   - 보통 ‘테이블 1 개 = 토픽 1 개’
    #   - 메시지 내용: before/after/op/source/ts_ms
    #   - schema: Avro + Schema Registry 권장
    print(" Debezium 이벤트는 ‘before/after/op/ts_ms’ 의 표준 형식.")
    print()


def lesson4_outbox():
    # =========================================================================
    #   레슨 4 — Outbox 패턴
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : Outbox                     │")
    print("└──────────────────────────────────────┘")
    # ■ 문제: 마이크로서비스가 DB 에 쓰기 + Kafka 에 발행 → 둘 중 하나 실패 시 일관성 깨짐
    # ■ 해법: outbox 테이블 — 같은 DB 트랜잭션 안에서 INSERT
    #     INSERT INTO orders ...
    #     INSERT INTO outbox(event_type, payload, status) VALUES ('order_created', ..., 'NEW')
    #   → 트랜잭션 커밋되면 둘 다, 실패면 둘 다 롤백.
    #
    # ■ 그 다음:
    #   - Debezium 이 outbox 테이블의 변경을 캐치 → Kafka 토픽 발행
    #   - Single Message Transform (SMT) 으로 payload 만 깔끔히 추출
    #
    # ■ 이점:
    #   - exactly-once 발행에 가깝게
    #   - 어플리케이션 코드에서 Kafka client 직접 호출 제거
    print(" Outbox = ‘DB + 메시지 큐 일관성’ 의 표준 해법.")
    print()


def lesson5_idempotent_cdc():
    # =========================================================================
    #   레슨 5 — CDC 멱등 적재
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : CDC 멱등 적재              │")
    print("└──────────────────────────────────────┘")
    # ■ CDC 메시지 키 = primary key
    # ■ 적재:
    #   1) op='c' (create) → INSERT (또는 UPSERT)
    #   2) op='u' (update) → UPSERT
    #   3) op='d' (delete) → DELETE 또는 soft delete (deleted_at)
    #   4) op='r' (snapshot read) → 초기 스냅샷
    #
    # ■ 순서 보장:
    #   - 같은 키는 같은 파티션으로 → 순서 보장
    #   - DW 적재 시 ‘최신 ts 만 살리기’: MERGE … WHERE source.ts > target.ts
    #
    # ■ 메시지 중복:
    #   - exactly-once 가 어려운 시스템에선 ‘at-least-once + dedupe’ 흔함
    print(" CDC = at-least-once + dedupe + 최신성 비교가 운영 표준.")
    print()


def lesson6_use_cases():
    # =========================================================================
    #   레슨 6 — 사용 사례
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 사용 사례                  │")
    print("└──────────────────────────────────────┘")
    # ■ 1) 검색 인덱스 동기화 (DB → Elasticsearch / OpenSearch)
    # ■ 2) 캐시 갱신 (DB → Redis)
    # ■ 3) 마이크로서비스 통합 (DB → Event → 다른 서비스)
    # ■ 4) DW/Lake 실시간 적재 (DB → Kafka → Iceberg/Delta)
    # ■ 5) Replica / DR — 서로 다른 DB 간 복제
    print(" CDC 는 ‘운영 DB 를 그 자리에 두고도 모든 다운스트림에 동기화’를 가능케 함.")
    print()


def lesson7_practice_cdc_events():
    # =========================================================================
    #   레슨 7 — CDC 이벤트 시퀀스 시뮬레이션
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : CDC 이벤트 시뮬레이션      │")
    print("└──────────────────────────────────────┘")
    events = [
        {"op": "c", "ts": 100, "id": 1, "amount": 10},
        {"op": "u", "ts": 110, "id": 1, "amount": 15},
        {"op": "c", "ts": 120, "id": 2, "amount": 22},
        {"op": "u", "ts": 130, "id": 2, "amount": 25},
        # 메시지 중복 (재시도 시 흔함)
        {"op": "u", "ts": 110, "id": 1, "amount": 15},
        {"op": "d", "ts": 140, "id": 1, "amount": 0},
    ]

    target = {}        # id → row
    seen_ts = {}       # id → 최신 ts (dedup용)

    for ev in events:
        last_ts = seen_ts.get(ev["id"], -1)
        if ev["ts"] < last_ts:
            print(f"  skip stale ts: {ev}")
            continue
        if ev["op"] == "d":
            target.pop(ev["id"], None)
        else:
            target[ev["id"]] = {"id": ev["id"], "amount": ev["amount"]}
        seen_ts[ev["id"]] = ev["ts"]

    print(" 최종 적재 결과:")
    for v in target.values():
        print(" ", v)
    print()
    # → 중복/순서 역행에도 동일 결과 — 멱등 + dedupe 의 효과.


# ─────────────────────────────────────────────────────────────────────────
# ■ 연습문제
# ─────────────────────────────────────────────────────────────────────────
#  Q1. CDC 가 캐치하기 어려운 변경 한 가지(예: TRUNCATE) 와 대응 방법?
#  Q2. outbox 패턴이 ‘dual write 문제’ 를 해결하는 메커니즘을 설명하라.
#  Q3. Kafka 파티션 키를 PK 로 설정해도 ‘재분배 도중’ 순서가 흐트러질 수 있는 경우는?
#  Q4. CDC 적재에서 soft delete 와 hard delete 의 trade-off 두 가지를 적어라.
#  Q5. 운영 DB 에 CDC 를 켤 때 DBA 가 우려하는 두 가지를 적고 완화 방법을 제시하라.


if __name__ == "__main__":
    lesson1_why_cdc()
    lesson2_three_ways()
    lesson3_debezium()
    lesson4_outbox()
    lesson5_idempotent_cdc()
    lesson6_use_cases()
    lesson7_practice_cdc_events()
