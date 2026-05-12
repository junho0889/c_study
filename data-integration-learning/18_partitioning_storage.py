# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [데이터 연계] 학습 18단계: DB 파티셔닝 / 샤딩 / 보존 전략
#   ─ Range/List/Hash · 분기·월 파티션 · 시계열 DB · Tiering · Retention ─
#   ■ 실행 방법: python 18_partitioning_storage.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 왜 파티셔닝/샤딩인가 — 성능 / 보존 / 운영 관점
#   2. 파티션의 4 가지 종류 (Range / List / Hash / Composite)
#   3. 시간 기반 파티션 — 일 / 월 / 분기 / 연 (SQL 실전)
#   4. DBMS 별 구현 차이 (PostgreSQL / MySQL / Oracle / SQL Server)
#   5. 시계열 특화 저장 (TimescaleDB / InfluxDB / ClickHouse / Iceberg)
#   6. Sharding vs Partitioning, Tiering(Hot/Warm/Cold), Retention 정책
#   7. 실전: 1 년 4 분기 파티션 + 분기 자동 추가 + 5 년 후 자동 폐기
#
# ─────────────────────────────────────────────────────────────────────────


def lesson1_why_partition():
    # =========================================================================
    #   레슨 1 — 왜 파티셔닝/샤딩인가
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 왜 파티셔닝/샤딩            │")
    print("└──────────────────────────────────────┘")
    # ■ 한 테이블이 수십억 행이면 다음 문제가 생긴다:
    #   1) 쿼리 느림              — 인덱스만으론 부족
    #   2) DELETE/ARCHIVE 느림     — “2020년치 지우기” 가 며칠
    #   3) VACUUM/ANALYZE 비싸짐  — Postgres 의 운영 비용 폭증
    #   4) 통계 / 메타데이터 폭증
    #
    # ■ 파티셔닝의 4 가지 이득:
    #   1) 쿼리 가지치기(partition pruning) — 한 분기만 읽음
    #   2) 빠른 보존 정책 — DROP PARTITION 한 번
    #   3) 백업/유지보수 작업의 단위 축소
    #   4) 분기/월 별 ‘병렬 처리’ 자연스러움
    #
    # ■ 단점:
    #   - 파티션 키 설계 잘못 = 회복 불가
    #   - 너무 잘게 자르면 ‘많은 작은 파티션’ 자체가 부하
    print(" 파티셔닝 = ‘큰 테이블 1개’ 를 ‘작은 테이블 N개’로 보이게 만드는 기술.")
    print()


def lesson2_partition_kinds():
    # =========================================================================
    #   레슨 2 — 파티션의 4 종류
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : 4 종류                     │")
    print("└──────────────────────────────────────┘")
    # ■ Range partitioning (범위):
    #   - 시간/금액/ID 범위로 자름
    #   - 가장 흔함. 시계열 데이터의 90% 가 이 방식.
    #     2026 Q1 / Q2 / Q3 / Q4 → 4 개 파티션
    #
    # ■ List partitioning (목록):
    #   - 카테고리 값으로 자름
    #     country IN ('KR','JP') / IN ('US','CA') / IN (...)
    #
    # ■ Hash partitioning (해시):
    #   - 키의 해시로 균등 분포
    #     PARTITION BY HASH(user_id) PARTITIONS 16
    #   - 핫 파티션 방지, 단점은 ‘pruning’ 효과가 약함
    #
    # ■ Composite (복합):
    #   - 흔한 조합: Range(month) + Hash(user_id)
    #   - 시간으로 큰 분할, 그 안에서 사용자 균등 분산
    #
    # ■ 어느 걸 쓸까?
    #   ┌────────────────────────┬───────────────┐
    #   │ 데이터의 핵심 축       │ 권장 파티션    │
    #   ├────────────────────────┼───────────────┤
    #   │ 시간 (이벤트, 매출)    │ Range(시간)   │
    #   │ 지역/카테고리          │ List          │
    #   │ 균등 분산이 핵심       │ Hash          │
    #   │ 시간 + 사용자 모두     │ Composite     │
    #   └────────────────────────┴───────────────┘
    print(" 시계열 = Range,  카테고리 = List,  분산 = Hash,  둘 다 = Composite.")
    print()


def lesson3_time_range_sql():
    # =========================================================================
    #   레슨 3 — 시간 기반 파티션 SQL
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : 분기/월/일 파티션 SQL      │")
    print("└──────────────────────────────────────┘")
    # ■ PostgreSQL 14+ (선언적 파티셔닝)
    pg_sql = r"""
-- 부모 테이블 (선언적 파티셔닝)
CREATE TABLE sales (
    id         BIGSERIAL,
    user_id    BIGINT NOT NULL,
    amount     NUMERIC(12,2),
    created_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (id, created_at)            -- 파티션 키가 PK 에 포함되어야 함
) PARTITION BY RANGE (created_at);

-- 분기 파티션 (1년 4분할)
CREATE TABLE sales_2026q1 PARTITION OF sales
  FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');
CREATE TABLE sales_2026q2 PARTITION OF sales
  FOR VALUES FROM ('2026-04-01') TO ('2026-07-01');
CREATE TABLE sales_2026q3 PARTITION OF sales
  FOR VALUES FROM ('2026-07-01') TO ('2026-10-01');
CREATE TABLE sales_2026q4 PARTITION OF sales
  FOR VALUES FROM ('2026-10-01') TO ('2027-01-01');

-- 분기 파티션 안에 인덱스 만들기 (자식이 알아서 상속)
CREATE INDEX ON sales (user_id);

-- 보존 정책: 5 년 이전 분기 통째 폐기
DROP TABLE sales_2021q1;     -- 디스크 즉시 회수, FK 영향 없음
"""
    print(pg_sql)

    # ■ 월 파티션 (더 잘게)
    print(" -- 월 파티션 예 -----------------------------------------")
    print(" CREATE TABLE sales_2026_01 PARTITION OF sales")
    print("   FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');")
    print(" -- ... 12 개")
    print()

    # ■ 주의:
    #   - 파티션 키는 INSERT 마다 결정되므로 ‘created_at 가 NULL 이면 안 됨’
    #   - default 파티션을 두면 ‘예상치 못한 미래 데이터’ 도 안전하게 받지만
    #     운영자는 매 분기 새 파티션 추가가 필수 (pg_partman / 직접 cron)


def lesson4_dbms_differences():
    # =========================================================================
    #   레슨 4 — DBMS 별 구현 차이
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : DBMS 별 차이                │")
    print("└──────────────────────────────────────┘")
    # ■ PostgreSQL 14+:
    #   - 선언적 파티셔닝, default 파티션, attach/detach 빠름
    #   - pg_partman 익스텐션이 ‘자동 생성/폐기’ 처리
    #
    # ■ MySQL 8:
    #   - RANGE/LIST/HASH/KEY 지원
    #   - 단점: 외래키와 파티션 함께 쓰기 제약, 인스턴스당 8192 파티션 제한
    #
    # ■ Oracle:
    #   - 가장 성숙. Interval Partitioning 으로 ‘파티션 자동 생성’
    #   - PARTITION BY RANGE (created_at) INTERVAL (NUMTOYMINTERVAL(3,'MONTH'))
    #     → 분기 자동 추가
    #
    # ■ SQL Server:
    #   - Partition function + Partition scheme + 파일그룹
    #   - 디스크 분리까지 함께 설계
    #
    # ■ 클라우드 DW:
    #   - BigQuery: PARTITION BY DATE_TRUNC(ts, MONTH) + 클러스터링
    #   - Snowflake: 명시적 파티션 없음. ‘마이크로 파티션 + 클러스터링 키’ 자동
    #   - Redshift: SORTKEY + DISTKEY (정렬키가 사실상 파티션 역할)
    #
    # ■ Lakehouse:
    #   - Iceberg / Delta: hidden partitioning, partition evolution(과거 데이터 재정렬 X)
    print(" 클래식 RDB = 직접 선언, 클라우드 DW = ‘선언 + 자동 마이크로’ 형태가 표준.")
    print()


def lesson5_timeseries_db():
    # =========================================================================
    #   레슨 5 — 시계열 특화 저장
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 시계열 DB                  │")
    print("└──────────────────────────────────────┘")
    # ■ TimescaleDB (PostgreSQL 확장):
    #   - “hypertable”: 자동 시간 파티셔닝(chunks)
    #   - 압축 컬럼 저장, continuous aggregates (실시간 마트)
    #   - 일반 SQL 그대로
    #
    #     SELECT create_hypertable('sales', 'created_at', chunk_time_interval => INTERVAL '1 month');
    #     ALTER TABLE sales SET (timescaledb.compress);
    #     SELECT add_compression_policy('sales', INTERVAL '7 days');
    #     SELECT add_retention_policy('sales', INTERVAL '5 years');
    #
    # ■ InfluxDB:
    #   - shard = 일정 기간 데이터 묶음 (예: 7일)
    #   - retention policy 가 1 급 시민
    #   - 카디널리티 폭증 주의 (태그 조합)
    #
    # ■ ClickHouse:
    #   - MergeTree 엔진의 PARTITION BY 표현식
    #     PARTITION BY toYYYYMM(event_time)
    #     ORDER BY (user_id, event_time)
    #   - 압축율/스캔 속도가 압도적, IoT/로그/광고에 표준
    #
    # ■ Apache Iceberg / Delta:
    #   - hidden partitioning, partition evolution(과거 데이터를 손대지 않고 분할 정책 변경)
    print(" 시계열 전용 DB = ‘시간 파티션 + 압축 + retention’ 이 빌트인.")
    print()


def lesson6_sharding_tier_retention():
    # =========================================================================
    #   레슨 6 — Sharding / Tiering / Retention
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : Sharding / Tier / Retention │")
    print("└──────────────────────────────────────┘")
    # ■ 파티셔닝 vs 샤딩:
    #     파티셔닝 = ‘한 DB 안에서’ 자르기
    #     샤딩    = ‘여러 DB 인스턴스’ 에 분산 (수평 확장)
    #
    #   샤드 키 후보: user_id 해시 / region / tenant_id
    #   샤딩의 어려움:
    #     - cross-shard join / 트랜잭션 비쌈
    #     - rebalance (샤드 추가) 가 운영 사고 자주
    #
    #   현대 도구: Vitess(MySQL), Citus(PostgreSQL), CockroachDB, YugabyteDB
    #
    # ■ Tiering — Hot / Warm / Cold:
    #     Hot   = 최근 7일,   SSD + 메모리 인덱스
    #     Warm  = 최근 90일,  HDD or 일반 클래스
    #     Cold  = 그 이상,    S3 Standard-IA / Glacier
    #
    #   클라우드 객체 스토리지의 lifecycle 규칙으로 자동 이행.
    #   DW: BigQuery Long-Term Storage(90일 무수정 → 자동 50% 할인)
    #
    # ■ Retention 정책:
    #   - 규제 요건(개인정보 90일/3년) 과 비즈니스 요건 매트릭스
    #   - “지움 ↔ 마스킹 ↔ 아카이브” 셋 중 무엇인지 명확히
    #
    # ■ ETL/CDC 측 시사점:
    #   - 파티션 단위 멱등 적재 → 백필 안전
    #   - retention 정책은 ‘소스/원본/마트’ 별로 따로 (서로 다른 보존 기간)
    print(" 파티션 = 한 DB,  샤딩 = 여러 DB,  Tier = ‘얼마나 빨리’,  Retention = ‘얼마나 오래’.")
    print()


def lesson7_practice_quarterly_partitioning():
    # =========================================================================
    #   레슨 7 — 1 년 4 분기 파티션 + 자동 분기 추가 + 5년 폐기
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 분기 자동 운영              │")
    print("└──────────────────────────────────────┘")
    # ■ 분기 경계 계산 헬퍼 (분기 시작/다음 분기 시작)
    def quarter_bounds(year, q):
        starts = {1: (1, 1), 2: (4, 1), 3: (7, 1), 4: (10, 1)}
        next_y, next_q = (year, q + 1) if q < 4 else (year + 1, 1)
        ms, ds = starts[q]
        me, de = starts[next_q]
        start = f"{year:04d}-{ms:02d}-{ds:02d}"
        end = f"{next_y:04d}-{me:02d}-{de:02d}"
        return start, end

    # 2026 ~ 2030 5 년 어치 분기 파티션 DDL 자동 생성
    print(" -- 5 년치 분기 파티션 DDL 자동 생성 -----------------")
    for y in range(2026, 2031):
        for q in (1, 2, 3, 4):
            s, e = quarter_bounds(y, q)
            print(f" CREATE TABLE sales_{y}q{q} PARTITION OF sales "
                  f"FOR VALUES FROM ('{s}') TO ('{e}');")
    print()

    # ■ 운영 패턴 1: 매 분기 “직전 분기까지의 파티션이 있는지 점검” + “다음 분기 미리 생성”
    #   - Airflow DAG 의 @quarterly 작업으로 자동화
    #   - pg_partman 의 partman.maintenance() 한 줄도 동일 효과
    #
    # ■ 운영 패턴 2: 5 년 초과 분기는 “먼저 S3 로 archive 후 DROP”
    print(" -- 5 년 이상 된 분기 폐기 절차(의사코드) -------------")
    archive_pseudo = r"""
def archive_and_drop(year, q):
    snapshot_path = f"s3://cold/sales/{year}q{q}/"
    # 1) Parquet 으로 dump
    psql(f"COPY (SELECT * FROM sales_{year}q{q}) "
         f"TO PROGRAM 'aws s3 cp - {snapshot_path}part.parquet' WITH (FORMAT parquet);")
    # 2) DROP (디스크 즉시 회수)
    psql(f"DROP TABLE sales_{year}q{q};")
    # 3) 카탈로그 / lineage 에 ‘archived’ 마킹
    catalog.mark_archived(table=f"sales_{year}q{q}", path=snapshot_path)
"""
    print(archive_pseudo)

    # ■ 분기/월/일 선택 가이드:
    #   - 분기 = ‘많은 행 + 보존 5~10년 + BI 분기 보고’ 도메인
    #   - 월   = 매출/재고/사용자 — 가장 흔한 선택
    #   - 일   = 로그/이벤트 — 작은 파티션 폭증을 견딜 수 있는 인프라일 때
    print(" 파티션 단위 = ‘쿼리 패턴 + 보존 + 운영 사이클’ 의 교집합. 분기는 BI 친화.")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 보너스: 파티션 ‘가지치기(pruning)’ 의 동작 흔적 보기
# ─────────────────────────────────────────────────────────────────────────
def bonus_pruning():
    print("┌──────────────────────────────────────┐")
    print("│  보너스 : Partition Pruning          │")
    print("└──────────────────────────────────────┘")
    plan = r"""
EXPLAIN
SELECT SUM(amount) FROM sales
WHERE created_at >= '2026-04-01' AND created_at < '2026-07-01';

-- Append (cost=...) (actual time=...)
--   ->  Seq Scan on sales_2026q2 sales_1 (... rows=...)
--   -- 다른 분기들은 ‘건드리지 않음’
"""
    print(plan)
    # ■ EXPLAIN 결과에 q2 만 등장 = pruning 성공.
    # ■ 가지치기 실패의 흔한 원인:
    #   - 파티션 키에 함수 적용 (예: WHERE EXTRACT(QUARTER FROM created_at) = 2)
    #     → 그냥 범위 조건으로 작성:  WHERE created_at >= ... AND created_at < ...
    #   - 파라미터화된 prepared statement 의 ‘일반 plan’ 으로 fallback
    print(" pruning 실패 = 파티션이 있어도 풀스캔.  쿼리 작성 습관이 결정적.")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 연습문제
# ─────────────────────────────────────────────────────────────────────────
#  Q1. 분기 파티션과 월 파티션의 trade-off 를 ‘작은 파일 문제 / BI 친화 / 백업 단위’ 관점에서 비교하라.
#  Q2. PostgreSQL 에서 WHERE EXTRACT(YEAR FROM created_at)=2026 이 pruning 을 못 받는 이유와 대안 SQL?
#  Q3. Hash partitioning 이 ‘배포 직후 한 사용자의 폭주 트래픽’ 에 어떻게 도움이 되나?
#  Q4. 샤딩으로 가야 하는 신호 3 가지를 적어라 (단일 인스턴스 한계 신호).
#  Q5. retention 정책이 ‘마스킹 vs 삭제 vs 아카이브’ 중 어느 쪽이 어울리는지 결정하는 기준은?
#  Q6. TimescaleDB 의 hypertable 이 ‘일반 PG 파티션 테이블’ 대비 갖는 운영 강점 3 가지?
#  Q7. 위 quarter_bounds 함수를 ‘회계 분기(예: 3-4-5 월 = Q1)’ 기준으로 바꾸려면?


def main():
    lesson1_why_partition()
    lesson2_partition_kinds()
    lesson3_time_range_sql()
    lesson4_dbms_differences()
    lesson5_timeseries_db()
    lesson6_sharding_tier_retention()
    lesson7_practice_quarterly_partitioning()
    bonus_pruning()


if __name__ == "__main__":
    main()
