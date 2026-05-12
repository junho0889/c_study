# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [데이터 연계] 학습 08단계: 데이터 품질
#   ─ Great Expectations · 스키마 검증 · DQ 메트릭 · Data Contract ─
#   ■ 실행 방법: python 08_data_quality.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 데이터 품질의 6 가지 차원
#   2. 스키마 검증 — pydantic / pandera / Great Expectations
#   3. 비즈니스 규칙 — Soda / dbt test / Custom
#   4. Data Contract — 생산자/소비자 사이의 ‘API 명세’
#   5. 통계 기반 모니터링 — drift, anomaly
#   6. Quarantine 패턴 — 불량 데이터를 격리
#   7. 실전: 간단한 룰 엔진을 손으로 구현
#
# ─────────────────────────────────────────────────────────────────────────


def lesson1_six_dimensions():
    # =========================================================================
    #   레슨 1 — 데이터 품질 6 차원
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 6 차원                     │")
    print("└──────────────────────────────────────┘")
    # ■ Accuracy(정확성)     : 값이 사실에 부합
    # ■ Completeness(완전성) : 필수 값이 모두 있음
    # ■ Consistency(일관성)  : 시스템 간 같은 값
    # ■ Timeliness(적시성)   : 약속된 시간 안에 도착
    # ■ Validity(유효성)     : 스키마/규칙 준수
    # ■ Uniqueness(유일성)   : 중복 없음
    print(" 모든 품질 사건은 이 6 가지 중 하나(또는 조합) 으로 분류된다.")
    print()


def lesson2_schema_validation():
    # =========================================================================
    #   레슨 2 — 스키마 검증
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : 스키마 검증                │")
    print("└──────────────────────────────────────┘")
    # ■ pydantic:
    #     class Order(BaseModel):
    #         order_id: int
    #         amount: condecimal(ge=0)
    #         currency: Literal["KRW","USD"]
    #     Order(**row)   # 자동 검증
    #
    # ■ pandera:
    #     schema = pa.DataFrameSchema({
    #       "order_id": pa.Column(int, unique=True, nullable=False),
    #       "amount":   pa.Column(float, pa.Check.ge(0)),
    #     })
    #     schema.validate(df)
    #
    # ■ Great Expectations:
    #     expect_column_values_to_be_in_set("currency", ["KRW","USD"])
    #     expect_column_values_to_not_be_null("order_id")
    print(" 스키마 검증은 ‘파이프라인 입구의 metal detector’.  여기서 막아야 가장 싸다.")
    print()


def lesson3_business_rules():
    # =========================================================================
    #   레슨 3 — 비즈니스 규칙
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : 비즈니스 룰                │")
    print("└──────────────────────────────────────┘")
    # ■ 예시:
    #   - “주문 금액 < 0 금지”
    #   - “환불 amount 는 원 주문 amount 이하”
    #   - “한 사용자의 일일 결제 합계 < 신용 한도”
    #
    # ■ 도구:
    #   - dbt test: SQL 한 줄로 표현
    #   - Soda SQL/Cloud: yaml 로 표현, 알림 라우팅
    #   - Custom Python: 복잡한 도메인 룰
    #
    # ■ 운영:
    #   - 모든 룰은 ‘심각도(severity)’ 가 있어야 함 — fail vs warn
    #   - 다운스트림 ‘차단’ 룰과 ‘알림’ 룰을 분리
    print(" 룰은 코드/SQL/yaml 중 어디든 좋다.  ‘심각도 + 라우팅’이 핵심.")
    print()


def lesson4_data_contract():
    # =========================================================================
    #   레슨 4 — Data Contract
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : Data Contract              │")
    print("└──────────────────────────────────────┘")
    # ■ 생산자 ↔ 소비자 간 명세서. API contract 와 같은 개념을 데이터에 적용.
    #
    # ■ 내용:
    #   - 스키마(컬럼, 타입, nullable)
    #   - SLA (신선도, 가용성)
    #   - 의미(definition): 매출 = ‘세금 포함? 환불 차감?’
    #   - 변경 정책: 호환성 BACKWARD 보장
    #   - 소유자(owner), 연락 채널
    #
    # ■ 도구:
    #   - dbt-checkpoint, datacontract.cli, OpenLineage
    print(" Data Contract = ‘분석 영역의 OpenAPI’.  공식 발행본을 가지면 운영이 안정된다.")
    print()


def lesson5_drift_monitoring():
    # =========================================================================
    #   레슨 5 — 통계 기반 모니터링
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : Drift / 통계 모니터링      │")
    print("└──────────────────────────────────────┘")
    # ■ 행 수 추세:    어제 100만 → 오늘 1만? 알림
    # ■ Null 비율 변화: 5% → 70% ? 사고
    # ■ 분포 변화:    PSI, KS test, KL divergence
    # ■ 카테고리 신규: 갑자기 ‘unknown’ 값 등장
    #
    # ■ 도구:
    #   - Soda, Monte Carlo, Bigeye, Anomalo
    #   - 직접 만들 땐 dbt test + macro + 알림 + 대시보드
    print(" 스키마 통과 = ‘옷차림 점검’,  통계 모니터링 = ‘건강검진’. 둘 다 필요.")
    print()


def lesson6_quarantine():
    # =========================================================================
    #   레슨 6 — Quarantine 패턴
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : Quarantine                 │")
    print("└──────────────────────────────────────┘")
    # ■ 불량 데이터는 ‘버리지 말고 격리’:
    #   - 별도 quarantine 테이블/버킷에 적재
    #   - 사유(reason), 원본(payload), 검출 시각 보관
    #   - 사람 검토 후 재처리 또는 폐기
    #
    # ■ 효과:
    #   - 다운스트림 보호 + 사후 분석
    #   - “왜 이런 데이터가 들어왔는가”의 학습 자산
    print(" 불량은 격리 후 학습 자료로.  단순 삭제는 운영 지식의 손실.")
    print()


def lesson7_practice_rule_engine():
    # =========================================================================
    #   레슨 7 — 작은 룰 엔진 손코딩
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 룰 엔진                    │")
    print("└──────────────────────────────────────┘")
    rules = [
        {"name": "amount_non_negative", "severity": "fail",
         "check": lambda r: r["amount"] >= 0},
        {"name": "currency_known", "severity": "fail",
         "check": lambda r: r["currency"] in ("KRW", "USD")},
        {"name": "user_id_present", "severity": "warn",
         "check": lambda r: r.get("user_id") is not None},
    ]
    rows = [
        {"id": 1, "amount":  100, "currency": "KRW", "user_id": 10},
        {"id": 2, "amount": -50,  "currency": "KRW", "user_id": 11},
        {"id": 3, "amount":  90,  "currency": "EUR", "user_id": None},
        {"id": 4, "amount":  10,  "currency": "USD", "user_id": 13},
    ]
    good, quarantine = [], []
    for r in rows:
        fails = [rule for rule in rules if not rule["check"](r) and rule["severity"] == "fail"]
        warns = [rule for rule in rules if not rule["check"](r) and rule["severity"] == "warn"]
        if fails:
            quarantine.append({**r, "reasons": [f["name"] for f in fails]})
        else:
            good.append({**r, "warns": [w["name"] for w in warns]})

    print(" 통과:")
    for g in good:
        print(" ", g)
    print(" 격리:")
    for q in quarantine:
        print(" ", q)
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 연습문제
# ─────────────────────────────────────────────────────────────────────────
#  Q1. ‘BACKWARD compatible’ 만 허용하는 Data Contract 가 결국 시스템 진화를 어떻게 돕는가?
#  Q2. dbt test 의 unique 와 PK 의 차이를 한 줄로 적어라.
#  Q3. drift 알림이 ‘오탐 폭주’ 하지 않도록 만드는 4 가지 운영 팁?
#  Q4. quarantine 데이터의 보유 기간 정책을 정할 때 고려할 두 가지 요인?
#  Q5. 데이터 품질 점수(KPI) 를 한 회사 차원에서 단일 숫자로 만들 수 있는지, 가능/불가능 이유를 적어라.


if __name__ == "__main__":
    lesson1_six_dimensions()
    lesson2_schema_validation()
    lesson3_business_rules()
    lesson4_data_contract()
    lesson5_drift_monitoring()
    lesson6_quarantine()
    lesson7_practice_rule_engine()
