# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [데이터 연계] 학습 04단계: Pandas / Polars 기반 ETL
#   ─ DataFrame 변환 · 청크 처리 · 메모리 관리 ─
#   ■ 실행 방법: python 04_pandas_polars_etl.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 왜 DataFrame 도구가 ETL 의 표준이 됐나
#   2. Pandas 의 강점과 한계
#   3. Polars / DuckDB 의 등장 — 단일 머신에서도 빠르게
#   4. 청크(chunk) 처리 / 스트리밍 모드
#   5. 메모리 관리 — dtype 최적화, copy-on-write
#   6. SQL ↔ DataFrame 동등성
#   7. 실전: ‘주문 + 사용자’ join 후 일별 요약 (의사코드)
#
# ─────────────────────────────────────────────────────────────────────────


def lesson1_why_dataframe():
    # =========================================================================
    #   레슨 1 — DataFrame 도구의 부상
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : DataFrame ETL              │")
    print("└──────────────────────────────────────┘")
    # ■ 이유:
    #   - 표 형식 = 대부분의 데이터 표현
    #   - SQL 보다 더 ‘프로그래밍 친화’ — 함수 합성, 모듈화
    #   - 동일 코드가 sklearn / 시각화 / DW 연동 모두 가능
    #
    # ■ ETL 에서의 역할:
    #   - 데이터 수집 후 ‘마지막 정제’ 의 표준 인터페이스
    #   - Airflow Task 안의 Python 함수가 곧 DataFrame 코드
    print(" 표 형식 ETL = DataFrame 의 시대.  SQL 은 DW 안에서 그대로 사용.")
    print()


def lesson2_pandas_strengths_limits():
    # =========================================================================
    #   레슨 2 — Pandas 강점 / 한계
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : Pandas                     │")
    print("└──────────────────────────────────────┘")
    # ■ 강점:
    #   - 가장 풍부한 생태계 (sklearn, plotly, 모든 책)
    #   - groupby/merge/pivot 의 표현력
    #
    # ■ 한계:
    #   - 단일 스레드(기본)
    #   - 메모리: 가용 메모리의 5~10 배 데이터 처리는 곤란
    #   - dtypes 가 numpy + Python object 혼합 → 종종 메모리 폭증
    #
    # ■ 보완:
    #   - chunksize 로 스트리밍 처리
    #   - PyArrow backend (pandas 2.x) 로 메모리/성능 개선
    print(" Pandas 는 ‘작은~중간’ 데이터의 황금 도구.  대용량은 Polars/DuckDB/Spark.")
    print()


def lesson3_polars_duckdb():
    # =========================================================================
    #   레슨 3 — Polars / DuckDB
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : Polars / DuckDB            │")
    print("└──────────────────────────────────────┘")
    # ■ Polars:
    #   - Rust 기반, lazy execution, 멀티스레드
    #   - 같은 코드가 단일 머신에서 수 GB ~ 수십 GB 도 처리
    #   - pandas 와 비슷한 표현력, 더 안전한 타입 시스템
    #
    # ■ DuckDB:
    #   - 임베디드 SQL 엔진 (SQLite 의 컬럼 분석 버전)
    #   - 파일/Pandas/Polars/Arrow 위에서 SQL 직접 실행
    #   - 데이터 호수에서 ‘쿼리 없이 분석’의 표준 도구로 부상
    #
    # ■ 권장 조합:
    #   - 탐색/시각화 → Pandas
    #   - 대용량 ETL → Polars 또는 DuckDB
    #   - 진짜 거대(>수백 GB) → Spark / Trino
    print(" 단일 머신의 새 표준: Polars + DuckDB.  Pandas 대안이 아니라 ‘동반자’.")
    print()


def lesson4_chunking():
    # =========================================================================
    #   레슨 4 — 청크 / 스트리밍
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : Chunking                   │")
    print("└──────────────────────────────────────┘")
    # ■ Pandas:
    #     for chunk in pd.read_csv("big.csv", chunksize=200_000):
    #         out = transform(chunk)
    #         out.to_parquet(...)
    #
    # ■ Polars (lazy):
    #     pl.scan_csv("big.csv").filter(...).select(...).collect(streaming=True)
    #
    # ■ DuckDB:
    #     duckdb.sql("SELECT ... FROM 'big.csv' WHERE ...").write_parquet("out.parquet")
    #
    # ■ 청크 처리 시:
    #   - 누적 집계(running sum) 가 필요한 경우 외부 상태(파일/DB) 필요
    #   - join 은 전체 적재 후가 안전 → DuckDB / Spark
    print(" 메모리 부족? 청크 또는 streaming engine 으로 즉시 전환.")
    print()


def lesson5_memory_optim():
    # =========================================================================
    #   레슨 5 — 메모리 최적화
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 메모리 최적화              │")
    print("└──────────────────────────────────────┘")
    # ■ dtype 다이어트:
    #   - int64 → int32/16
    #   - object → category (반복 카테고리)
    #   - float64 → float32 (정밀도 손실 허용 시)
    #
    # ■ PyArrow backend:
    #   - pd.options.future.infer_string = True
    #   - df.convert_dtypes(dtype_backend="pyarrow")
    #
    # ■ copy-on-write (pandas 3.x):
    #   - chained assignment 의 ‘이상한 부작용’ 제거
    #   - 메모리 사본 횟수 ↓
    print(" 메모리 = 행 수 × 컬럼 수 × dtype 크기.  dtype 만 손봐도 절반 절감 흔함.")
    print()


def lesson6_sql_dataframe_equivalence():
    # =========================================================================
    #   레슨 6 — SQL ↔ DataFrame 매핑
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : SQL ↔ DataFrame            │")
    print("└──────────────────────────────────────┘")
    # ■ SELECT a, b      ↔  df[["a","b"]]
    # ■ WHERE x > 10     ↔  df[df.x > 10]
    # ■ GROUP BY id      ↔  df.groupby("id").agg(...)
    # ■ JOIN             ↔  df1.merge(df2, on=..., how=...)
    # ■ WINDOW           ↔  df.groupby(...).rolling(...).sum()
    # ■ UNION ALL        ↔  pd.concat([df1, df2])
    #
    # ■ 둘 다 알면:
    #   - 큰 데이터는 DW SQL/dbt 에서, 정밀 변환은 DataFrame 으로 — 자유롭게 이동.
    print(" SQL ↔ DataFrame 은 두 언어가 아니라 ‘동일한 관계대수’의 두 표기.")
    print()


def lesson7_practice_pseudo_etl():
    # =========================================================================
    #   레슨 7 — 의사코드 ETL
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 의사코드 ETL               │")
    print("└──────────────────────────────────────┘")
    # 가상 데이터
    orders = [
        {"order_id": 1, "user_id": 10, "ts": "2026-05-13 10:00", "amount": 5},
        {"order_id": 2, "user_id": 11, "ts": "2026-05-13 10:05", "amount": 12},
        {"order_id": 3, "user_id": 10, "ts": "2026-05-13 12:30", "amount":  8},
        {"order_id": 4, "user_id": 12, "ts": "2026-05-14 09:30", "amount": 20},
    ]
    users = [
        {"user_id": 10, "country": "KR"},
        {"user_id": 11, "country": "KR"},
        {"user_id": 12, "country": "US"},
    ]
    # 1) 조인
    uid_to_country = {u["user_id"]: u["country"] for u in users}
    enriched = []
    for o in orders:
        enriched.append({**o, "country": uid_to_country.get(o["user_id"])})

    # 2) 일별 집계
    from collections import defaultdict
    daily = defaultdict(lambda: defaultdict(float))
    for e in enriched:
        day = e["ts"][:10]
        daily[day][e["country"]] += e["amount"]

    print(" 일별 / 국가별 매출")
    for day, by_country in sorted(daily.items()):
        for country, total in sorted(by_country.items()):
            print(f"  {day}  {country}  {total:>6.2f}")
    print()
    # 위 의사코드를 pandas / polars / SQL 로 옮기면 그대로 작동.


# ─────────────────────────────────────────────────────────────────────────
# ■ 연습문제
# ─────────────────────────────────────────────────────────────────────────
#  Q1. pandas 의 chunked 처리에서 ‘월별 합계’ 같은 광역 집계가 어려운 이유와 해결책은?
#  Q2. Polars 의 lazy mode 가 메모리 효율에서 갖는 이점을 한 줄로 설명하라.
#  Q3. DuckDB 가 ‘파이프라인 안’에서 어떤 위치를 차지할 수 있는지 (예: dbt + DuckDB 모드) 적어라.
#  Q4. object dtype 컬럼이 category 로 바뀌면 메모리/속도가 좋아지지만 주의점은?
#  Q5. 같은 ETL 을 Pandas/Polars 로 작성한 후 결과가 다르면 어떤 점을 의심?


if __name__ == "__main__":
    lesson1_why_dataframe()
    lesson2_pandas_strengths_limits()
    lesson3_polars_duckdb()
    lesson4_chunking()
    lesson5_memory_optim()
    lesson6_sql_dataframe_equivalence()
    lesson7_practice_pseudo_etl()
