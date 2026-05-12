# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [데이터 연계] 학습 17단계: 매니지드 ETL & 이벤트 아키텍처
#   ─ AWS Glue · Dataflow · Data Factory · EventBridge · Lambda ─
#   ■ 실행 방법: python 17_managed_etl_events.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 매니지드 ETL 의 등장 배경
#   2. AWS Glue / Dataflow / Data Factory 의 공통 모델
#   3. iPaaS 와 SaaS ELT (Airbyte / Fivetran / Hevo)
#   4. 이벤트 기반 아키텍처 (EventBridge / Cloud Functions / Lambda)
#   5. Step Functions / Workflows — 분기/재시도 자동화
#   6. 서버리스 비용 사고 회피
#   7. 실전: ‘파일 업로드 → ETL → DW → 알림’ 이벤트 흐름 도해
#
# ─────────────────────────────────────────────────────────────────────────


def lesson1_why_managed():
    # =========================================================================
    #   레슨 1 — 매니지드 ETL
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 매니지드 ETL               │")
    print("└──────────────────────────────────────┘")
    # ■ 자체 운영 부담 ↓
    #   - 인프라(쿠버, 스파크 클러스터) 관리 X
    #   - 자동 확장/롤백/모니터링 기본 제공
    #
    # ■ trade-off:
    #   - 벤더 락인
    #   - 커스터마이즈 한계
    #   - 비용이 ‘쉽게 통제 안 됨’ (서버리스 폭주)
    #
    # ■ 적합 케이스:
    #   - 운영 인력이 작음
    #   - 표준 변환(SQL/PySpark/SaaS connector) 으로 충분
    print(" 매니지드 = ‘운영 인력 절감’ 의 큰 가치. 단, 비용 모니터링 / 락인 / 한계 인지.")
    print()


def lesson2_glue_dataflow_adf():
    # =========================================================================
    #   레슨 2 — Glue / Dataflow / Data Factory
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : 매니지드 ETL 비교          │")
    print("└──────────────────────────────────────┘")
    # ■ AWS Glue:
    #   - 서버리스 Spark + DataBrew(노코드) + Crawler(스키마 자동 추출)
    #   - 카탈로그 = Glue Data Catalog (Athena, EMR 공통)
    #
    # ■ GCP Dataflow:
    #   - Apache Beam 기반. 배치 + 스트림 통합 SDK
    #   - 자동 셔플/오토스케일
    #
    # ■ Azure Data Factory:
    #   - 풍부한 connector + 시각 파이프라인
    #   - Mapping Data Flow 가 Spark 위에서 동작
    #
    # ■ 공통 모델:
    #   - 소스(connector) → 변환(Spark/Beam) → 싱크 → 모니터링/카탈로그
    print(" 셋 다 ‘서버리스 Spark/Beam’ 위에서 connector 와 노코드를 더한 형태.")
    print()


def lesson3_ipaas_saas_elt():
    # =========================================================================
    #   레슨 3 — Airbyte / Fivetran / Hevo
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : SaaS ELT                   │")
    print("└──────────────────────────────────────┘")
    # ■ 컨셉:
    #   - “수십~수백 개 SaaS 데이터 소스 → DW” 의 ‘배관’을 SaaS 가 제공
    #   - 사용자는 connector 선택 + 인증 + 일정만 설정
    #
    # ■ 도구:
    #   - Fivetran: 상용, connector 가장 풍부
    #   - Airbyte:  오픈소스, self-host 가능
    #   - Hevo, Stitch, Rivery: 경쟁자
    #
    # ■ 한계:
    #   - 표준 connector 외 커스텀 변환은 별도(dbt 등)
    #   - 비용이 ‘row 단위’ 라 갑자기 폭증할 수 있음
    print(" SaaS ELT = 사내 ETL 인력의 ‘배관 노가다’ 시간을 환산해서 비용 평가.")
    print()


def lesson4_event_driven():
    # =========================================================================
    #   레슨 4 — 이벤트 기반 아키텍처
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : 이벤트 기반                │")
    print("└──────────────────────────────────────┘")
    # ■ 트리거:
    #   - S3 ObjectCreated → Lambda
    #   - EventBridge rule → Step Functions
    #   - Pub/Sub → Cloud Run
    #   - CloudWatch alarm → SNS → Slack
    #
    # ■ 장점:
    #   - 진정한 ‘이벤트 발생 시점’ 처리 → latency ↓
    #   - 시스템 간 결합도 ↓
    #
    # ■ 함정:
    #   - 디버깅이 ‘추적 어려움’
    #   - 무한 루프(서비스 A → B → A)
    #   - 비용 사고 (예: S3 Object 만들 때마다 Lambda 가 다시 S3 에 씀 → 폭주)
    print(" 이벤트 기반 = ‘느슨한 결합 + 낮은 latency’.  관측성/순환 방지가 필수.")
    print()


def lesson5_step_functions():
    # =========================================================================
    #   레슨 5 — Step Functions / Workflows
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : Step Functions             │")
    print("└──────────────────────────────────────┘")
    # ■ 정의:
    #   - 여러 Lambda/API 호출을 ‘상태 머신’ 으로 묶음
    #   - 분기, 병렬, 재시도, 타임아웃, 보상 트랜잭션
    #
    # ■ 예시 (Amazon States Language 의사):
    sample = r"""
{
  "StartAt": "Extract",
  "States": {
    "Extract":   {"Type":"Task","Resource":"arn:lambda:extract","Next":"Transform","Retry":[{"ErrorEquals":["States.ALL"],"MaxAttempts":3,"IntervalSeconds":2,"BackoffRate":2}]},
    "Transform": {"Type":"Task","Resource":"arn:lambda:transform","Next":"Load"},
    "Load":      {"Type":"Task","Resource":"arn:lambda:load","Next":"Notify"},
    "Notify":    {"Type":"Task","Resource":"arn:sns:publish","End":true}
  }
}
"""
    print(sample)
    # ■ GCP: Workflows / Azure: Logic Apps / Durable Functions  — 비슷한 모델


def lesson6_serverless_cost():
    # =========================================================================
    #   레슨 6 — 서버리스 비용 사고 회피
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 비용 사고 방지             │")
    print("└──────────────────────────────────────┘")
    # ■ 자주 발생:
    #   - Lambda 재귀 호출 (S3 trigger → S3 write → S3 trigger ...)
    #   - 폭주 트래픽으로 호출 수 폭증
    #   - 잘못된 로깅(매 호출 마다 큰 객체 직렬화)
    #
    # ■ 방지:
    #   - reserved concurrency (max 호출 수 제한)
    #   - budget alert
    #   - dead letter queue + circuit breaker
    #   - 명시적 ‘재귀 차단’ 키(예: S3 객체 key prefix 분리)
    print(" 서버리스 = ‘비용 폭발이 쉬움’.  reserved concurrency + budget alert 가 필수.")
    print()


def lesson7_practice_event_flow():
    # =========================================================================
    #   레슨 7 — 이벤트 흐름 도해
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 이벤트 흐름                │")
    print("└──────────────────────────────────────┘")
    diagram = r"""
   [클라이언트] ── HTTPS ──▶ API Gateway ──▶ Lambda(인증)
                                                  │
                                                  ▼
                                          S3: incoming/orders.csv
                                                  │ ObjectCreated
                                                  ▼
                                          EventBridge rule
                                                  │
                                                  ▼
                                          Step Functions
                          ┌──────────────┬───────────────┬─────────────┐
                          ▼              ▼               ▼             ▼
                       Extract λ      Transform λ      Load λ       Notify SNS
                                                          │
                                                          ▼
                                                       BigQuery / Snowflake
"""
    print(diagram)


# ─────────────────────────────────────────────────────────────────────────
# ■ 연습문제
# ─────────────────────────────────────────────────────────────────────────
#  Q1. 매니지드 ETL 도입 후 “벤더 락인”을 줄이기 위한 3 가지 전략?
#  Q2. EventBridge 와 SNS 의 차이를 한 줄로 설명하라.
#  Q3. Step Functions 의 ‘보상 트랜잭션’(Saga) 패턴이 어떤 비즈니스 문제에 어울리나?
#  Q4. Lambda 의 cold start 영향을 줄이는 방법 3 가지?
#  Q5. S3 trigger → Lambda → S3 write 의 무한 루프를 막는 두 가지 방법?


if __name__ == "__main__":
    lesson1_why_managed()
    lesson2_glue_dataflow_adf()
    lesson3_ipaas_saas_elt()
    lesson4_event_driven()
    lesson5_step_functions()
    lesson6_serverless_cost()
    lesson7_practice_event_flow()
