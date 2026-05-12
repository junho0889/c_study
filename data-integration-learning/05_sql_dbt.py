# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [데이터 연계] 학습 05단계: SQL 기반 ETL & dbt
#   ─ CTE · Window · dbt 모델 / 테스트 / lineage ─
#   ■ 실행 방법: python 05_sql_dbt.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. ELT 시대의 SQL — DW 안에서 변환
#   2. CTE / Window Function — 가독성과 성능
#   3. Incremental SQL 모델 — “지난 1일치만 처리”
#   4. dbt 가 무엇을 자동화하나
#   5. dbt 의 yml: tests / docs / sources
#   6. SQLGlot / lineage — 의존 그래프 시각화
#   7. 실전: dbt 모델 SQL 작성 흉내
#
# ─────────────────────────────────────────────────────────────────────────


def lesson1_elt_sql():
    # =========================================================================
    #   레슨 1 — ELT 시대의 SQL
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : ELT 시대의 SQL             │")
    print("└──────────────────────────────────────┘")
    # ■ Snowflake/BigQuery/Redshift/Databricks 등 클라우드 DW 는 ‘무제한 컴퓨트’.
    # ■ 변환을 DW 내 SQL 로 → 데이터 이동 비용 ↓, 협업 ↑
    # ■ ‘Analyst → 데이터 엔지니어’ 경계가 흐려짐.
    print(" ELT 시대 = DW 안 SQL 이 ‘메인 코드’.  dbt 가 표준 도구.")
    print()


def lesson2_cte_window():
    # =========================================================================
    #   레슨 2 — CTE & Window
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : CTE / Window               │")
    print("└──────────────────────────────────────┘")
    # ■ CTE (Common Table Expression):
    #     WITH base AS (
    #       SELECT user_id, DATE(ts) AS d, SUM(amount) AS amt
    #       FROM orders GROUP BY 1,2
    #     ),
    #     ranked AS (
    #       SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY d) AS day_no
    #       FROM base
    #     )
    #     SELECT * FROM ranked WHERE day_no = 1;   -- 사용자별 첫 구매일 매출
    #
    # ■ Window 자주 쓰는 패턴:
    #   - ROW_NUMBER / RANK / DENSE_RANK
    #   - LAG / LEAD : 직전/직후 값
    #   - SUM/AVG OVER (PARTITION BY ... ORDER BY ... ROWS BETWEEN ...)
    #
    # ■ 이점:
    #   - 서브쿼리 지옥 회피
    #   - 옵티마이저 최적화 친화
    print(" CTE + Window 두 기둥만 잘 알아도 분석 SQL 90% 커버.")
    print()


def lesson3_incremental_sql():
    # =========================================================================
    #   레슨 3 — Incremental SQL
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : Incremental                │")
    print("└──────────────────────────────────────┘")
    # ■ dbt 의 incremental 모델:
    #     {{ config(materialized='incremental', unique_key='order_id') }}
    #
    #     SELECT * FROM {{ ref('stg_orders') }}
    #     {% if is_incremental() %}
    #       WHERE updated_at >= (SELECT MAX(updated_at) FROM {{ this }}) - INTERVAL '1 day'
    #     {% endif %}
    #
    # ■ 핵심:
    #   - is_incremental() 분기로 첫 풀 빌드 vs 증분 분리
    #   - unique_key 로 멱등 보장
    print(" Incremental = ‘하루치 처리 + 멱등’.  운영 안정성과 비용 둘 다 좋아짐.")
    print()


def lesson4_dbt():
    # =========================================================================
    #   레슨 4 — dbt 가 자동화하는 것
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : dbt                        │")
    print("└──────────────────────────────────────┘")
    # ■ dbt 가 자동화:
    #   1) SELECT 만 작성 → 자동으로 CREATE TABLE / INSERT 실행 (materialization 선택)
    #   2) 모델 의존성(ref) 그래프 자동 생성 → 토폴로지 순서 실행
    #   3) 테스트(not_null, unique 등) 통합
    #   4) 문서 자동 생성 (lineage 포함)
    #   5) Snapshot — SCD2 (Slowly Changing Dimension type 2)
    #
    # ■ 구조:
    #     models/staging/stg_orders.sql       — 원본 정제
    #     models/marts/sales/daily_sales.sql — 분석 마트
    #     tests/, snapshots/, macros/, seeds/
    print(" dbt = ‘SQL 위의 빌드 시스템’.  의존성 + 테스트 + 문서까지.")
    print()


def lesson5_dbt_yml():
    # =========================================================================
    #   레슨 5 — dbt yml
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : schema.yml                 │")
    print("└──────────────────────────────────────┘")
    # ─ models/staging/stg_orders.yml (예시) ─────────────────────────────
    yml = r"""
version: 2

sources:
  - name: app
    schema: raw_app
    tables:
      - name: orders
        loaded_at_field: updated_at
        freshness:
          warn_after: {count: 6, period: hour}
          error_after: {count: 12, period: hour}

models:
  - name: stg_orders
    description: "주문 원본을 정제한 staging 모델"
    columns:
      - name: order_id
        tests: [not_null, unique]
      - name: user_id
        tests:
          - not_null
          - relationships:
              to: ref('stg_users')
              field: user_id
"""
    print(yml)
    # ■ tests 가 운영의 ‘데이터 unit test’ 역할.
    #   CI 에서 dbt test 가 실패하면 PR 머지 차단 — 분석 영역의 표준 절차.


def lesson6_lineage():
    # =========================================================================
    #   레슨 6 — Lineage
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : Lineage                    │")
    print("└──────────────────────────────────────┘")
    # ■ Lineage(데이터 계보):
    #   - 어떤 SQL 컬럼이 어떤 원천 컬럼에서 만들어졌는지 그래프
    #
    # ■ 도구:
    #   - dbt docs (모델 단위)
    #   - OpenLineage / Marquez (시스템 전역)
    #   - DataHub / Atlas (엔터프라이즈 카탈로그)
    #   - SQLGlot 으로 SQL 정적 분석 → 컬럼 단위 lineage 자동 추출
    #
    # ■ 활용:
    #   - 영향도 분석 — 이 컬럼을 바꾸면 어떤 대시보드가 깨질까?
    #   - 규제 — PII 가 어떤 마트까지 전파됐나?
    print(" Lineage 는 ‘변경의 영향 반경’을 가시화한다.  변경 사고를 막는 가장 강한 도구.")
    print()


def lesson7_practice_dbt_model():
    # =========================================================================
    #   레슨 7 — dbt 모델 SQL 흉내
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : dbt 모델 흉내              │")
    print("└──────────────────────────────────────┘")
    sql = r"""
-- models/marts/sales/daily_sales.sql
{{ config(materialized='incremental', unique_key=['country','d']) }}

WITH base AS (
  SELECT
    DATE(ts) AS d,
    u.country,
    SUM(o.amount) AS revenue,
    COUNT(*) AS orders
  FROM {{ ref('stg_orders') }} o
  JOIN {{ ref('stg_users') }} u USING (user_id)
  {% if is_incremental() %}
    WHERE o.updated_at >= (SELECT MAX(updated_at_max) FROM {{ this }}) - INTERVAL '1 day'
  {% endif %}
  GROUP BY 1,2
)
SELECT
  d, country, revenue, orders,
  MAX(o.updated_at) OVER ()  AS updated_at_max
FROM base
"""
    print(sql)
    # 위 SQL 을 dbt run 하면 첫 빌드는 전체, 이후는 1 일치만 증분 처리.


# ─────────────────────────────────────────────────────────────────────────
# ■ 연습문제
# ─────────────────────────────────────────────────────────────────────────
#  Q1. CTE 가 서브쿼리보다 보통 더 ‘유지보수’ 친화적인 이유 두 가지를 적어라.
#  Q2. dbt 의 SCD2 snapshot 이 다루는 비즈니스 문제는 무엇인가?
#  Q3. 컬럼 lineage 가 ‘테이블 lineage’ 보다 강력한 이유?
#  Q4. dbt 의 ref()/source() 매크로의 ‘하드코딩 회피’ 측면 효과는?
#  Q5. Snowflake/BigQuery 의 시간 여행(time travel) 이 ETL 실수에서 어떻게 도움이 되나?


if __name__ == "__main__":
    lesson1_elt_sql()
    lesson2_cte_window()
    lesson3_incremental_sql()
    lesson4_dbt()
    lesson5_dbt_yml()
    lesson6_lineage()
    lesson7_practice_dbt_model()
