"""
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  Kafka 07단계: Kafka Streams와 Kafka Connect                    ■
■  Stateless 연산(filter, map), Stateful 연산(aggregate, join),   ■
■  Source/Sink Connector, ETL 파이프라인                           ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
"""


# ============================================================
#  토이 Kafka 스트림 처리기
# ============================================================
class KStream:
    """
    Kafka Streams의 KStream을 흉내 낸 클래스.
    비유: 공장의 컨베이어 벨트 - 물건(레코드)이 하나씩 흘러가며
    각 공정(filter, map, aggregate)을 거칩니다.
    """

    def __init__(self, records):
        self.records = list(records)  # [{key, value}, ...]

    def filter(self, predicate):
        """조건에 맞는 레코드만 통과 (불량품 제거 공정)"""
        filtered = [r for r in self.records if predicate(r)]
        return KStream(filtered)

    def map(self, transform):
        """각 레코드를 변환 (포장 공정)"""
        mapped = [transform(r) for r in self.records]
        return KStream(mapped)

    def map_values(self, transform):
        """값만 변환, 키는 유지"""
        mapped = [{"key": r["key"], "value": transform(r["value"])} for r in self.records]
        return KStream(mapped)

    def flat_map(self, transform):
        """하나의 레코드를 여러 개로 펼침"""
        result = []
        for r in self.records:
            result.extend(transform(r))
        return KStream(result)

    def group_by_key(self):
        """키별로 그룹화"""
        groups = {}
        for r in self.records:
            groups.setdefault(r["key"], []).append(r["value"])
        return KTable(groups)

    def join(self, other_stream, key_extractor=None):
        """두 스트림을 키 기준으로 조인"""
        other_map = {}
        for r in other_stream.records:
            other_map[r["key"]] = r["value"]

        joined = []
        for r in self.records:
            if r["key"] in other_map:
                joined.append({
                    "key": r["key"],
                    "value": {"left": r["value"], "right": other_map[r["key"]]}
                })
        return KStream(joined)

    def to_list(self):
        return self.records

    def peek(self, label=""):
        """디버깅용: 현재 스트림 내용 출력"""
        for r in self.records:
            print(f"    {label} key={r['key']}, value={r['value']}")
        return self


class KTable:
    """
    Kafka Streams의 KTable - 키별 최신 상태를 유지하는 테이블.
    비유: 학생별 최종 성적표 - 새 점수가 오면 덮어쓰기.
    """

    def __init__(self, groups):
        self.groups = groups  # {key: [values]}

    def aggregate(self, initializer, aggregator):
        """키별로 값을 모아서 계산 (합계, 평균 등)"""
        result = {}
        for key, values in self.groups.items():
            acc = initializer()
            for v in values:
                acc = aggregator(acc, v)
            result[key] = acc
        return result

    def count(self):
        """키별 개수 세기"""
        return {key: len(values) for key, values in self.groups.items()}

    def reduce(self, reducer):
        """키별로 값을 하나로 줄이기"""
        result = {}
        for key, values in self.groups.items():
            acc = values[0]
            for v in values[1:]:
                acc = reducer(acc, v)
            result[key] = acc
        return result


# ============================================================
#  토이 Kafka Connect
# ============================================================
class SourceConnector:
    """
    Source Connector: 외부 시스템 -> Kafka 토픽.
    비유: 우체통에서 편지를 수거해 우체국(Kafka)으로 가져오는 집배원.
    """

    def __init__(self, name, source_data):
        self.name = name
        self.source_data = source_data

    def poll(self):
        """외부 시스템에서 데이터를 가져옴"""
        records = []
        for row in self.source_data:
            records.append({"key": str(row.get("id", "")), "value": row})
        return records


class SinkConnector:
    """
    Sink Connector: Kafka 토픽 -> 외부 시스템.
    비유: 우체국(Kafka)에서 편지를 배달하는 집배원.
    """

    def __init__(self, name):
        self.name = name
        self.destination = []

    def put(self, records):
        """Kafka에서 읽은 데이터를 외부 시스템에 저장"""
        for r in records:
            self.destination.append(r)
        return len(records)


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 1: Stateless 연산 - filter, map                      │
# │  비유: 컨베이어 벨트에서 불량품 제거 & 포장                   │
# └─────────────────────────────────────────────────────────────┘
def lesson1_stateless_operations():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 1: Stateless 연산 - filter, map               │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Stateless(상태 없는) 연산은 각 레코드를 독립적으로 처리합니다.
    # 공장 컨베이어 벨트에서 불량품을 제거하거나(filter),
    # 포장지를 씌우는(map) 것과 같아요. 이전 물건을 기억할 필요가 없습니다!

    orders = KStream([
        {"key": "order1", "value": {"item": "노트북", "amount": 1200000, "status": "paid"}},
        {"key": "order2", "value": {"item": "마우스", "amount": 25000, "status": "pending"}},
        {"key": "order3", "value": {"item": "키보드", "amount": 89000, "status": "paid"}},
        {"key": "order4", "value": {"item": "모니터", "amount": 450000, "status": "paid"}},
        {"key": "order5", "value": {"item": "USB", "amount": 8000, "status": "cancelled"}},
    ])

    # filter: 결제 완료된 주문만
    paid_orders = orders.filter(lambda r: r["value"]["status"] == "paid")
    print("  [filter] 결제 완료 주문만:")
    paid_orders.peek("  ")

    # map: 금액에 부가세 10% 추가
    with_tax = paid_orders.map(lambda r: {
        "key": r["key"],
        "value": {**r["value"], "amount_with_tax": int(r["value"]["amount"] * 1.1)}
    })
    print("\n  [map] 부가세 포함 금액 추가:")
    with_tax.peek("  ")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 2: Stateful 연산 - aggregate, count                   │
# │  비유: 반별 점수 합계를 내려면 이전 점수를 기억해야 함         │
# └─────────────────────────────────────────────────────────────┘
def lesson2_stateful_operations():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 2: Stateful 연산 - aggregate, count           │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Stateful(상태 있는) 연산은 이전 레코드를 기억하며 처리합니다.
    # 반별 점수 합계를 내려면 '지금까지 합'을 기억해야 하는 것처럼요!

    page_views = KStream([
        {"key": "homepage", "value": 1},
        {"key": "products", "value": 1},
        {"key": "homepage", "value": 1},
        {"key": "cart", "value": 1},
        {"key": "homepage", "value": 1},
        {"key": "products", "value": 1},
        {"key": "checkout", "value": 1},
    ])

    # count: 페이지별 조회수
    counts = page_views.group_by_key().count()
    print("  [count] 페이지별 조회수:")
    for page, cnt in sorted(counts.items(), key=lambda x: -x[1]):
        bar = "#" * cnt
        print(f"    {page:12s} {bar} ({cnt})")

    # aggregate: 카테고리별 매출 합계
    sales = KStream([
        {"key": "전자제품", "value": 1200000},
        {"key": "의류", "value": 89000},
        {"key": "전자제품", "value": 450000},
        {"key": "식품", "value": 35000},
        {"key": "의류", "value": 120000},
        {"key": "식품", "value": 28000},
    ])

    totals = sales.group_by_key().aggregate(
        initializer=lambda: 0,
        aggregator=lambda acc, val: acc + val
    )
    print("\n  [aggregate] 카테고리별 매출 합계:")
    for category, total in totals.items():
        print(f"    {category}: {total:,}원")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 3: Stream Join - 두 스트림 합치기                      │
# │  비유: 학생 명단과 성적표를 학번으로 합치기                    │
# └─────────────────────────────────────────────────────────────┘
def lesson3_join():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 3: Stream Join - 두 스트림 합치기              │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Join은 두 스트림(또는 스트림과 테이블)을 키 기준으로 합치는 것입니다.
    # 학생 명단과 성적표를 학번으로 합쳐서 '이름 + 점수'를 만드는 것과 같아요.

    users = KStream([
        {"key": "u1001", "value": {"name": "김민수", "class": "5-3"}},
        {"key": "u1002", "value": {"name": "이지우", "class": "5-1"}},
        {"key": "u1003", "value": {"name": "박서연", "class": "5-3"}},
    ])

    scores = KStream([
        {"key": "u1001", "value": {"subject": "수학", "score": 95}},
        {"key": "u1002", "value": {"subject": "수학", "score": 88}},
        {"key": "u1004", "value": {"subject": "수학", "score": 72}},  # u1004는 users에 없음
    ])

    joined = users.join(scores)
    print("  [join] 학생 정보 + 성적 (키 기준):")
    for r in joined.to_list():
        user = r["value"]["left"]
        score = r["value"]["right"]
        print(f"    {r['key']}: {user['name']}({user['class']}) - {score['subject']} {score['score']}점")
    print("  -> u1003은 성적이 없고, u1004는 학생 정보가 없어서 결과에 빠졌습니다.")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 4: Kafka Connect - Source와 Sink Connector            │
# │  비유: 집배원이 편지를 수거(Source)하고 배달(Sink)하기        │
# └─────────────────────────────────────────────────────────────┘
def lesson4_connect():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 4: Kafka Connect - Source & Sink Connector    │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Kafka Connect는 외부 시스템과 Kafka를 연결하는 프레임워크입니다.
    # Source Connector: 외부 -> Kafka (우체통에서 편지 수거)
    # Sink Connector: Kafka -> 외부 (편지를 집에 배달)
    # 코드를 거의 안 짜고 설정만으로 데이터를 옮길 수 있어요!

    # Source: DB에서 데이터를 가져와 Kafka로
    db_rows = [
        {"id": 1, "name": "김민수", "score": 95},
        {"id": 2, "name": "이지우", "score": 88},
        {"id": 3, "name": "박서연", "score": 100},
    ]

    source = SourceConnector("jdbc-source", db_rows)
    kafka_topic = source.poll()
    print("  [Source Connector] DB -> Kafka:")
    for r in kafka_topic:
        print(f"    key={r['key']}, value={r['value']}")

    # Sink: Kafka에서 읽어 Elasticsearch로
    sink = SinkConnector("elastic-sink")
    count = sink.put(kafka_topic)
    print(f"\n  [Sink Connector] Kafka -> Elasticsearch: {count}건 저장")
    print(f"  저장된 데이터: {sink.destination}")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 5: ETL 파이프라인 - 추출 -> 변환 -> 적재               │
# └─────────────────────────────────────────────────────────────┘
def lesson5_etl_pipeline():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 5: ETL 파이프라인                             │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # ETL = Extract(추출) -> Transform(변환) -> Load(적재)
    # Kafka Connect(E, L)와 Kafka Streams(T)를 합치면 완전한 ETL!

    # 1. Extract: 주문 DB에서 데이터 추출
    raw_orders = [
        {"id": 101, "item": "노트북", "price": 1200000, "qty": 1},
        {"id": 102, "item": "마우스", "price": 25000, "qty": 3},
        {"id": 103, "item": "키보드", "price": 89000, "qty": 2},
    ]
    source = SourceConnector("order-source", raw_orders)
    kafka_records = source.poll()
    print("  [E] Extract - DB에서 추출:")
    for r in kafka_records:
        print(f"    {r['value']}")

    # 2. Transform: Kafka Streams로 가공
    stream = KStream(kafka_records)
    transformed = stream.map(lambda r: {
        "key": r["key"],
        "value": {
            "item": r["value"]["item"],
            "total": r["value"]["price"] * r["value"]["qty"],
            "total_with_tax": int(r["value"]["price"] * r["value"]["qty"] * 1.1),
        }
    })
    print("\n  [T] Transform - 총액 & 세금 계산:")
    transformed.peek("  ")

    # 3. Load: 데이터 웨어하우스에 적재
    sink = SinkConnector("warehouse-sink")
    sink.put(transformed.to_list())
    print(f"\n  [L] Load - 데이터 웨어하우스에 {len(sink.destination)}건 적재 완료!")
    print()


def main():
    print("=" * 72)
    print("  Kafka 07단계: Kafka Streams와 Kafka Connect")
    print("=" * 72)
    print()

    lesson1_stateless_operations()
    lesson2_stateful_operations()
    lesson3_join()
    lesson4_connect()
    lesson5_etl_pipeline()


if __name__ == "__main__":
    main()
