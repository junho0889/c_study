# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [데이터 연계] 학습 06단계: 워크플로 오케스트레이션
#   ─ Airflow · Prefect · Dagster · DAG · 백필 · 의존성 ─
#   ■ 실행 방법: python 06_orchestration.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 왜 오케스트레이터가 필요한가
#   2. DAG (Directed Acyclic Graph) 의 본질
#   3. Airflow vs Prefect vs Dagster 비교
#   4. 스케줄링 & 백필
#   5. Task 의존성 / Sensor / Branching
#   6. 관측성 — 로그, 알림, SLA
#   7. 실전: 작은 DAG 의사코드 (cron, source, transform, load)
#
# ─────────────────────────────────────────────────────────────────────────


def lesson1_why():
    # =========================================================================
    #   레슨 1 — 왜 오케스트레이션이 필요한가
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 왜 오케스트레이션          │")
    print("└──────────────────────────────────────┘")
    # ■ 단일 cron 스크립트의 한계:
    #   - 의존성(B 는 A 다음) 표현 어려움
    #   - 재시도/백필 자동화 부족
    #   - 관측성/알림 부족
    #   - 다양한 시스템(API, Spark, dbt) 호출 통합 어려움
    #
    # ■ 오케스트레이터의 역할:
    #   1) DAG 정의 — 누가 누구 뒤에 오는가
    #   2) 스케줄 — 언제 시작하는가
    #   3) 실행 엔진 — 어디서 어떻게 돌리는가 (executor)
    #   4) 관측 — 실패 알림, lineage, SLA
    print(" 오케스트레이터 = ‘여러 시스템에 걸친 작업의 빌드 시스템’.")
    print()


def lesson2_dag():
    # =========================================================================
    #   레슨 2 — DAG
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : DAG                        │")
    print("└──────────────────────────────────────┘")
    # ■ DAG = 방향성 + 순환 없음
    #     extract_orders ──▶ transform_orders ──▶ load_dw ──▶ refresh_dashboard
    #     extract_users  ──▶ transform_users  ─┘
    #
    # ■ 순환이 있으면? 작업이 영원히 끝나지 않음 → DAG 제약은 ‘안정성의 본질’.
    print(" DAG = 데이터 작업의 ‘제약 만족 문제’.  실행은 토폴로지 정렬.")
    print()


def lesson3_compare_tools():
    # =========================================================================
    #   레슨 3 — 도구 비교
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : Airflow / Prefect / Dagster │")
    print("└──────────────────────────────────────┘")
    # ■ Airflow:
    #   - 가장 광범위한 생태계, 오래된 표준
    #   - DAG = Python 코드, 풍부한 operator
    #   - 단점: backfill / dynamic DAG / 테스트 어려움
    #
    # ■ Prefect:
    #   - “Python 함수에 @task 데코레이터”
    #   - 동적 DAG 자연스러움, 코드 친화
    #   - Cloud 매니지드 강점
    #
    # ■ Dagster:
    #   - “데이터 자산(asset)” 1급 시민
    #   - SDA (Software Defined Assets): 출력 데이터 자체가 노드
    #   - 강력한 타입/체크/lineage
    print(" 신규 도입: Prefect/Dagster 가 부드러움.  사내 표준화엔 Airflow 가 여전히 강력.")
    print()


def lesson4_schedule_backfill():
    # =========================================================================
    #   레슨 4 — 스케줄링 & 백필
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : 스케줄링 / 백필            │")
    print("└──────────────────────────────────────┘")
    # ■ cron 표현: "0 2 * * *"   매일 02:00
    # ■ Logical / Execution date:
    #   - Airflow: ‘이 DAG run 이 표현하는 시점’ 과 ‘실제 실행 시점’ 이 다름
    #     → ETL 의 ‘처리 대상 일자’ 가 logical date.
    # ■ 백필:
    #   - 같은 DAG 를 ‘과거 날짜’ 로 다시 트리거 → 멱등성이 무조건 필요.
    print(" 스케줄/백필을 잘 다루려면 ‘logical date = 처리 대상 윈도우’ 라는 사고가 핵심.")
    print()


def lesson5_deps_sensor_branch():
    # =========================================================================
    #   레슨 5 — 의존성 / Sensor / Branching
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 의존성 패턴                │")
    print("└──────────────────────────────────────┘")
    # ■ Sensor: 외부 조건이 만족될 때까지 대기
    #   - ExternalTaskSensor: 다른 DAG 의 특정 task 완료 대기
    #   - S3KeySensor: 특정 키가 존재할 때까지
    #   - 권장: poke 모드 X, reschedule 모드 O (slot 점유 방지)
    #
    # ■ Branch:
    #   - 조건에 따라 분기 (월말이면 추가 검증 task, 아니면 skip)
    #
    # ■ Dataset / Asset based scheduling (현대 트렌드):
    #   - “데이터셋 X 가 갱신되면 DAG Y 실행”
    print(" Sensor = 시간 의존이 아니라 ‘이벤트 의존’.  Dataset trigger 가 더 효율적.")
    print()


def lesson6_observability():
    # =========================================================================
    #   레슨 6 — 관측성
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 관측성                     │")
    print("└──────────────────────────────────────┘")
    # ■ 필수 신호:
    #   1) Task 성공/실패율, 평균/최대 소요 시간
    #   2) SLA 미스 (예: 09:00 까지 완료 못하면 알림)
    #   3) 데이터 신선도(freshness) — 마지막 적재 시각
    #   4) 데이터 양 추이(row count) — 갑작스런 변동 알림
    #
    # ■ 도구: Airflow UI, OpenTelemetry, DataDog, OpenLineage
    # ■ 알림: Slack / Pager / 이메일.  ‘비치 알람’ 만들지 않기 (passive alert 만 쌓이면 무용)
    print(" 관측성은 ‘운영자의 5분 안 의사결정’을 돕는 신호여야 한다.  알림 시각화 + 라우팅.")
    print()


def lesson7_practice_pseudo_dag():
    # =========================================================================
    #   레슨 7 — DAG 의사코드
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : DAG 의사코드               │")
    print("└──────────────────────────────────────┘")
    code = r"""
# Airflow 2.x TaskFlow API 의사코드
from airflow.decorators import dag, task
from datetime import datetime, timedelta

default_args = {"retries": 3, "retry_delay": timedelta(minutes=5)}

@dag(
    schedule="0 2 * * *",                    # 매일 02:00
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["daily", "sales"],
)
def daily_sales_etl():

    @task
    def extract_orders(logical_date):
        # SELECT * FROM orders WHERE updated_at::date = logical_date
        return f"/tmp/orders_{logical_date}.parquet"

    @task
    def extract_users(logical_date):
        return f"/tmp/users_{logical_date}.parquet"

    @task
    def transform(orders_path, users_path):
        # pandas/polars 로 정제 + 조인
        return f"{orders_path}.merged.parquet"

    @task
    def load_dw(merged_path):
        # MERGE INTO dw.daily_sales USING ...
        return True

    o = extract_orders("{{ ds }}")
    u = extract_users("{{ ds }}")
    m = transform(o, u)
    load_dw(m)

dag = daily_sales_etl()
"""
    print(code)


# ─────────────────────────────────────────────────────────────────────────
# ■ 연습문제
# ─────────────────────────────────────────────────────────────────────────
#  Q1. ‘logical date’와 ‘execution date’의 차이를 한 줄로 정의하라.
#  Q2. ExternalTaskSensor 의 poke 모드와 reschedule 모드의 차이는?
#  Q3. Dagster 의 asset-based 스케줄링이 Airflow 의 time-based 스케줄링과 비교했을 때 강점?
#  Q4. ‘실패 알림이 너무 많아 무시되는 현상’ 을 줄이기 위한 운영 전략 3가지를 적어라.
#  Q5. 동일 DAG 를 다른 환경(dev/stage/prod) 에 안전히 배포하기 위한 두 가지 패턴?


if __name__ == "__main__":
    lesson1_why()
    lesson2_dag()
    lesson3_compare_tools()
    lesson4_schedule_backfill()
    lesson5_deps_sensor_branch()
    lesson6_observability()
    lesson7_practice_pseudo_dag()
