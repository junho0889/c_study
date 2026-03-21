"""
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  Kafka 04단계: 로그 보존(Retention)과 컴팩션(Compaction)         ■
■  시간/크기 기반 삭제, 키별 최신 값만 남기기, 톰스톤 레코드        ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
"""

import time


# ============================================================
#  토이 Kafka 로그
# ============================================================
class KafkaLog:
    """Kafka의 로그(파티션)를 흉내 내는 클래스"""

    def __init__(self, retention_ms=None, retention_bytes=None):
        self.records = []          # [{offset, key, value, timestamp}, ...]
        self.next_offset = 0
        self.retention_ms = retention_ms      # 시간 기반 보존 (밀리초)
        self.retention_bytes = retention_bytes  # 크기 기반 보존 (바이트)

    def append(self, key, value):
        record = {
            "offset": self.next_offset,
            "key": key,
            "value": value,
            "timestamp": time.time(),
            "size": len(str(key or "")) + len(str(value or "")),
        }
        self.records.append(record)
        self.next_offset += 1
        return record

    def total_size(self):
        return sum(r["size"] for r in self.records)

    def apply_retention_by_time(self, current_time):
        """시간 기반 보존: retention_ms보다 오래된 레코드 삭제"""
        if self.retention_ms is None:
            return 0
        cutoff = current_time - (self.retention_ms / 1000.0)
        before = len(self.records)
        self.records = [r for r in self.records if r["timestamp"] >= cutoff]
        return before - len(self.records)

    def apply_retention_by_size(self):
        """크기 기반 보존: 전체 크기가 retention_bytes를 넘으면 오래된 것부터 삭제"""
        if self.retention_bytes is None:
            return 0
        removed = 0
        while self.total_size() > self.retention_bytes and self.records:
            self.records.pop(0)
            removed += 1
        return removed

    def compact(self):
        """
        로그 컴팩션: 같은 키에 대해 마지막 값만 남긴다.
        비유: 도서관 대출 카드에서 같은 책의 최신 기록만 남기기.
        톰스톤(value=None)은 '이 키는 삭제됨'을 의미합니다.
        """
        latest = {}   # key -> record (마지막 것만 유지)
        for record in self.records:
            if record["key"] is not None:
                latest[record["key"]] = record

        # 톰스톤(value=None)인 키는 완전히 제거
        compacted = []
        for key, record in latest.items():
            if record["value"] is not None:
                compacted.append(record)

        removed_count = len(self.records) - len(compacted)
        self.records = sorted(compacted, key=lambda r: r["offset"])
        return removed_count


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 1: 시간 기반 보존 - 오래된 빌려간 책 기록 지우기       │
# │  비유: 도서관에서 1년 이상 된 대출 기록을 정리하는 것          │
# └─────────────────────────────────────────────────────────────┘
def lesson1_time_based_retention():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 1: 시간 기반 보존 (Time-based Retention)      │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Kafka는 메시지를 영원히 보관하지 않습니다.
    # 도서관에서 1년 이상 된 대출 기록을 정리하는 것처럼,
    # 정해진 시간이 지나면 오래된 메시지를 자동으로 삭제합니다.
    # 기본값은 7일(168시간)입니다.

    log = KafkaLog(retention_ms=5000)  # 5초 보존

    # 메시지 기록
    log.records = []
    now = time.time()
    # 일부러 오래된 타임스탬프를 설정
    for i, event in enumerate(["주문생성", "결제완료", "배송시작", "배송완료", "리뷰작성"]):
        record = {
            "offset": i,
            "key": f"order_{i}",
            "value": event,
            "timestamp": now - (10 - i * 2),  # 10초 전 ~ 2초 전
            "size": len(event) + 10,
        }
        log.records.append(record)
    log.next_offset = 5

    print(f"  보존 전 레코드 수: {len(log.records)}")
    for r in log.records:
        age = now - r["timestamp"]
        print(f"    offset={r['offset']}, {r['value']:8s}, {age:.0f}초 전")

    removed = log.apply_retention_by_time(now)
    print(f"\n  보존 정책 적용 후 (5초 초과 삭제): {removed}개 삭제")
    for r in log.records:
        age = now - r["timestamp"]
        print(f"    offset={r['offset']}, {r['value']:8s}, {age:.0f}초 전 (유지)")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 2: 크기 기반 보존 - 책장이 꽉 차면 오래된 책부터 빼기  │
# └─────────────────────────────────────────────────────────────┘
def lesson2_size_based_retention():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 2: 크기 기반 보존 (Size-based Retention)      │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 책장(디스크)에 공간이 정해져 있으면,
    # 꽉 찼을 때 오래된 책(메시지)부터 빼야 새 책을 넣을 수 있습니다.
    # retention.bytes 설정으로 토픽의 최대 크기를 제한합니다.

    log = KafkaLog(retention_bytes=50)  # 최대 50바이트

    for i in range(1, 8):
        log.append(f"key{i}", f"메시지내용{i}")

    print(f"  전체 크기: {log.total_size()} bytes, 레코드 수: {len(log.records)}")
    removed = log.apply_retention_by_size()
    print(f"  크기 제한(50 bytes) 적용: {removed}개 삭제")
    print(f"  남은 크기: {log.total_size()} bytes, 레코드 수: {len(log.records)}")
    for r in log.records:
        print(f"    offset={r['offset']}, {r['key']}={r['value']}")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 3: 로그 컴팩션 - 같은 키의 최신 값만 남기기            │
# │  비유: 학생별 최종 성적만 남기고 중간 기록은 정리             │
# └─────────────────────────────────────────────────────────────┘
def lesson3_log_compaction():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 3: 로그 컴팩션 - 키별 최신 값만 남기기        │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 로그 컴팩션은 같은 키에 대해 마지막(최신) 값만 남깁니다.
    # 학생 성적표에서 중간 점수는 지우고 최종 점수만 남기는 것과 같아요.
    # cleanup.policy=compact로 설정합니다.

    log = KafkaLog()

    # 같은 학생의 점수가 여러 번 업데이트됨
    log.append("민수", "70점")
    log.append("지우", "85점")
    log.append("민수", "80점")   # 민수 점수 업데이트
    log.append("서연", "95점")
    log.append("민수", "90점")   # 민수 점수 또 업데이트
    log.append("지우", "88점")   # 지우 점수 업데이트

    print("  컴팩션 전 (모든 기록):")
    for r in log.records:
        print(f"    offset={r['offset']}, {r['key']}={r['value']}")

    removed = log.compact()
    print(f"\n  컴팩션 후 (키별 최신 값만): {removed}개 제거")
    for r in log.records:
        print(f"    offset={r['offset']}, {r['key']}={r['value']}")
    print("  -> 민수의 70점, 80점은 사라지고 90점만 남았습니다!")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 4: 톰스톤 레코드 - '이 키는 삭제됨'을 알리는 표시      │
# │  비유: 도서관 카드에 '반납 완료' 도장 찍기                    │
# └─────────────────────────────────────────────────────────────┘
def lesson4_tombstone():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 4: 톰스톤 레코드 - 삭제 표시                  │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Kafka에서 레코드를 '삭제'하려면 같은 키에 value=null을 보냅니다.
    # 이것을 '톰스톤(tombstone, 묘비)'이라고 부릅니다.
    # 컴팩션 시 톰스톤이 있는 키는 완전히 제거됩니다.

    log = KafkaLog()

    log.append("user:1001", '{"name":"민수","active":true}')
    log.append("user:1002", '{"name":"지우","active":true}')
    log.append("user:1001", None)  # 톰스톤! -> 민수 계정 삭제

    print("  컴팩션 전:")
    for r in log.records:
        val_display = r["value"] if r["value"] is not None else "<톰스톤(삭제)>"
        print(f"    offset={r['offset']}, key={r['key']}, value={val_display}")

    removed = log.compact()
    print(f"\n  컴팩션 후: {removed}개 제거")
    for r in log.records:
        print(f"    offset={r['offset']}, key={r['key']}, value={r['value']}")
    print("  -> user:1001은 톰스톤 때문에 완전히 사라졌습니다!")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 5: 정리 - cleanup.policy 비교                         │
# └─────────────────────────────────────────────────────────────┘
def lesson5_summary():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 5: 정리 - cleanup.policy 비교                 │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    print("  ┌────────────┬───────────────────────────┬──────────────────────────┐")
    print("  │ 정책        │ delete (기본)              │ compact                   │")
    print("  ├────────────┼───────────────────────────┼──────────────────────────┤")
    print("  │ 동작        │ 시간/크기 초과 시 삭제     │ 키별 최신 값만 유지        │")
    print("  │ 사용 예     │ 로그, 이벤트 스트림        │ 상태 저장(사용자 프로필 등) │")
    print("  │ 데이터 손실 │ 오래된 것은 사라짐         │ 키의 최종 상태는 유지       │")
    print("  │ 톰스톤      │ 해당 없음                 │ value=null로 키 삭제        │")
    print("  └────────────┴───────────────────────────┴──────────────────────────┘")
    print()
    print("  팁: 이벤트 로그에는 delete, 현재 상태 저장에는 compact를 쓰세요!")
    print()


def main():
    print("=" * 72)
    print("  Kafka 04단계: 로그 보존(Retention)과 컴팩션(Compaction)")
    print("=" * 72)
    print()

    lesson1_time_based_retention()
    lesson2_size_based_retention()
    lesson3_log_compaction()
    lesson4_tombstone()
    lesson5_summary()


if __name__ == "__main__":
    main()
