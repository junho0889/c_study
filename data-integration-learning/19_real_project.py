# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [데이터 연계] 학습 18단계: End-to-End 통합 실전
#   ─ 멀티 소스 → CDC + ETL → DW → API → 알림 ─
#   ■ 실행 방법: python 18_real_project.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 프로젝트 시나리오
# ─────────────────────────────────────────────────────────────────────────
#
#   가상 e-commerce 회사:
#     - 주문 (PostgreSQL, CDC)
#     - 사용자 (PostgreSQL, CDC)
#     - 상품/카탈로그 (CSV 일배치)
#     - 결제 (외부 SaaS API)
#     - 행동 로그 (Kafka 스트림)
#
#   목표:
#     1) 모든 소스를 통합 DW(Iceberg + Snowflake) 에 일관성 있게 적재
#     2) 분석/대시보드 + API 서비스 동시 제공
#     3) 이상 알림(매출 급락, 신뢰성 SLA 위반) 자동화
#
#   본 파일은 ‘설계 + 의사코드’ 위주이며, 각 단계의 키 코드 조각을 함께 보여줍니다.
#
# ─────────────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────────────
# 1) 전체 아키텍처 다이어그램
# ─────────────────────────────────────────────────────────────────────────
def show_architecture():
    diagram = r"""
   ┌────────────────────┐
   │ Postgres (orders)  │── Debezium ──┐
   ├────────────────────┤              │
   │ Postgres (users)   │── Debezium ──┤
   ├────────────────────┤              │
   │ CSV (catalog,일배치) │── Airflow ───┤              ┌──────────────────┐
   ├────────────────────┤              ├──── Kafka ───▶│  Iceberg (Lake)  │
   │ Payment SaaS API   │── Connector──┤              └────────┬─────────┘
   ├────────────────────┤              │                       │ dbt + Spark
   │ App Behavior (Web) │── Kafka producer ─────────────────────┘
   └────────────────────┘
                                                      ┌──────────────────┐
                                                      │  Snowflake/BQ DW │
                                                      └────────┬─────────┘
                                  ┌────────────┬─────────────┐
                                  ▼            ▼             ▼
                            BI 대시보드     Internal API  ML 학습/추론
                                                                │
                                       이상 알림 / Slack ◀──────┘
"""
    print(diagram)


# ─────────────────────────────────────────────────────────────────────────
# 2) 단계별 핵심 의사코드
# ─────────────────────────────────────────────────────────────────────────
def step_a_cdc():
    print("┌─── A. CDC (운영 DB → Kafka) ───────────┐")
    code = r"""
# Debezium connector config (json) 예
{
  "name": "orders-pg-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "pg-prod.internal",
    "database.dbname": "shop",
    "table.include.list": "public.orders,public.users",
    "snapshot.mode": "initial",
    "publication.autocreate.mode": "filtered",
    "transforms": "unwrap",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "value.converter.schemas.enable": "true"
  }
}
"""
    print(code)


def step_b_batch_csv():
    print("┌─── B. 일배치 CSV (Airflow + Polars) ───┐")
    code = r"""
@task
def load_catalog_csv(execution_date):
    df = pl.read_csv(f"s3://landing/catalog/{execution_date}.csv")
    cleaned = (
        df.with_columns([
            pl.col("price").cast(pl.Float64),
            pl.col("active").cast(pl.Boolean),
        ])
        .filter(pl.col("price") >= 0)
    )
    cleaned.write_parquet(f"s3://lake/raw/catalog/dt={execution_date}/part.parquet")
"""
    print(code)


def step_c_streaming_log():
    print("┌─── C. 행동 로그(Kafka → Iceberg, Flink) ─┐")
    code = r"""
-- Flink SQL: Kafka → Iceberg sink
CREATE TABLE behavior_kafka (
  user_id BIGINT, event STRING, ts TIMESTAMP(3), props STRING,
  WATERMARK FOR ts AS ts - INTERVAL '5' SECOND
) WITH ('connector'='kafka','topic'='behavior','...'='...');

CREATE TABLE behavior_iceberg (
  user_id BIGINT, event STRING, ts TIMESTAMP(3), props STRING
) PARTITIONED BY (DATE(ts))
WITH ('connector'='iceberg','catalog-name'='nessie','warehouse'='s3://lake/');

INSERT INTO behavior_iceberg SELECT * FROM behavior_kafka;
"""
    print(code)


def step_d_dbt_marts():
    print("┌─── D. dbt 마트 (Snowflake / BigQuery) ───┐")
    code = r"""
-- models/marts/sales/fct_daily_sales.sql
{{ config(materialized='incremental', unique_key=['country','d']) }}

SELECT DATE(o.created_at) AS d,
       u.country,
       SUM(o.amount) AS revenue,
       COUNT(*)      AS orders,
       MAX(o.updated_at) OVER () AS hwm
FROM {{ ref('stg_orders') }} o
JOIN {{ ref('stg_users') }} u USING (user_id)
{% if is_incremental() %}
WHERE o.updated_at >= (SELECT MAX(hwm) FROM {{ this }}) - INTERVAL '1 day'
{% endif %}
GROUP BY 1,2;
"""
    print(code)


def step_e_data_quality():
    print("┌─── E. 데이터 품질 게이트 ─────────────┐")
    code = r"""
# dbt tests 예시 (yml)
columns:
  - name: order_id
    tests: [unique, not_null]
  - name: amount
    tests:
      - dbt_utils.accepted_range:
          min_value: 0
          max_value: 1000000
  - name: country
    tests:
      - accepted_values:
          values: ['KR','US','JP']

# Soda check 예시
checks for fct_daily_sales:
  - row_count > 0
  - missing_count(country) = 0
  - schema:
      fail:
        when required column missing: [revenue, orders, country]
"""
    print(code)


def step_f_api_service():
    print("┌─── F. API 서비스 (FastAPI + Snowflake) ──┐")
    code = r"""
@app.get("/v1/sales/daily")
def daily_sales(date: str = Query(..., regex=r"\d{4}-\d{2}-\d{2}"),
                user = Depends(auth)):
    sql = '''
      SELECT d, country, revenue, orders
      FROM mart.fct_daily_sales
      WHERE d = %s
      ORDER BY country
    '''
    rows = snowflake.fetchall(sql, (date,))
    return [Row(*r).model_dump() for r in rows]
"""
    print(code)


def step_g_alerting():
    print("┌─── G. 이상 알림 (잔차 + Slack) ──────────┐")
    code = r"""
# 매시간 cron: 직전 24h 매출이 ‘예측 구간’ 밖이면 알림
def alert_revenue_drop():
    today  = fetch_today_revenue()
    yhat   = forecaster.predict(now())     # 17단계 시계열 파이프 결과 활용
    band   = forecaster.predict_interval(now(), level=0.95)
    if today < band.low:
        slack(f":rotating_light: 매출 하락 감지: 실제 {today}, 95% 하한 {band.low}")
"""
    print(code)


# ─────────────────────────────────────────────────────────────────────────
# 3) 운영 체크리스트
# ─────────────────────────────────────────────────────────────────────────
def operational_checklist():
    print("┌─── 운영 체크리스트 ─────────────────────┐")
    items = [
        "스키마 변경 시 BACKWARD 호환성 통과 (CI)",
        "ETL 멱등성 (upsert / dedupe key) 보장",
        "Airflow SLA 미스 → PagerDuty 라우팅",
        "데이터 품질 fail 은 다운스트림 자동 차단",
        "API 응답 latency P95 < 300ms, 5xx < 0.1%",
        "DW 쿼리 scan 한도(예: 500GB) + budget alert",
        "PII 컬럼 마스킹/토큰화, 권한 분리",
        "백필 절차 문서화, 운영 환경에 ‘백필 슬롯’ 별도",
        "Disaster recovery: snapshot 보존 / 복구 RPO 1h",
    ]
    for i, it in enumerate(items, 1):
        print(f"  {i:>2}. {it}")
    print()


# ─────────────────────────────────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────────────────────────────────
def main():
    print("┌─────────────────────────────────────────────┐")
    print("│  데이터 연계 End-to-End 통합 프로젝트       │")
    print("└─────────────────────────────────────────────┘")
    show_architecture()
    step_a_cdc()
    step_b_batch_csv()
    step_c_streaming_log()
    step_d_dbt_marts()
    step_e_data_quality()
    step_f_api_service()
    step_g_alerting()
    operational_checklist()


# ─────────────────────────────────────────────────────────────────────────
# ■ 확장 아이디어
# ─────────────────────────────────────────────────────────────────────────
#  1) 시계열 모듈(15~17단계) 와 결합해 ‘실시간 이상 알림’ 자동화
#  2) Feature Store(Feast) 연동 — DW 에 만든 피처를 ML 서비스로 송출
#  3) GraphQL Federation 으로 ‘BI 대시보드 + 외부 파트너 API’ 통합
#  4) DataHub / OpenLineage 로 lineage 시각화
#  5) GenAI 코파일럿: 사내 데이터 카탈로그 + 자연어 → SQL 어시스턴트


if __name__ == "__main__":
    main()
