# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [ML 기초] 학습 01단계: 선형 회귀 (Linear Regression)
#   ─ 회귀 개념, OLS, 잔차, R², 다중 회귀, 경사하강법 ─
#   ■ 실행 방법: python 01_linear_regression.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 회귀란? - 연속 값 예측, 산점도 개념, 추세선
#   2. 단순 선형 회귀 - y = wx + b, 기울기와 절편의 의미
#   3. 최소제곱법(OLS) - 공식 유도(쉽게!), 직접 계산
#   4. 예측과 잔차 - 예측값 vs 실제값, 잔차 분석
#   5. 결정계수(R²) - 모델이 얼마나 잘 맞는지, 해석 방법
#   6. 다중 선형 회귀 개념 - 변수 2개 이상, 행렬 표현
#   7. 경사하강법으로 학습 - 수동 기울기 업데이트, 학습률 실험
#   8. 실전: 공부시간→시험점수 예측기
#
# ─────────────────────────────────────────────────────────────────────────


def lesson1_what_is_regression():
    # =========================================================================
    #
    #   레슨 1 — 회귀란? (Regression)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 회귀란?                    │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 회귀 = "연속적인 숫자"를 예측하는 문제
    # ─────────────────────────────────────────────────────────────────────
    #
    #   분류(Classification): "고양이냐 강아지냐" → 범주(카테고리)를 맞힌다
    #   회귀(Regression):     "몇 점이냐, 몇 원이냐" → 숫자를 맞힌다
    #
    #   실생활 예시:
    #     - 공부 시간 → 시험 점수 예측
    #     - 집 면적(평수) → 집 가격 예측
    #     - 온도 → 아이스크림 판매량 예측
    #     - 광고비 → 매출액 예측
    #

    print("  [회귀 vs 분류 비교]")
    print()
    print("    분류: 이메일이 스팸인가 아닌가? → '스팸' 또는 '정상'")
    print("    회귀: 이번 달 매출이 얼마일까?  → '3,200만원'")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 산점도 개념 - 데이터를 점으로 찍어보자
    # ─────────────────────────────────────────────────────────────────────
    #
    #   x축: 공부 시간, y축: 점수
    #   데이터를 찍으면 "대충 오른쪽 위로 올라가는 패턴"이 보인다
    #

    hours  = [1, 2, 3, 4, 5, 6, 7, 8]
    scores = [45, 50, 58, 65, 72, 78, 85, 90]

    print("  [산점도 - ASCII 시각화]")
    print()

    # 간단한 ASCII 산점도
    max_score = 100
    rows = 10  # 10줄로 표현
    for row in range(rows, 0, -1):
        threshold = max_score * row / rows
        line = f"  {threshold:>5.0f} |"
        for i in range(len(hours)):
            if scores[i] >= threshold - 5 and scores[i] < threshold + 5:
                line += " * "
            else:
                line += "   "
        print(line)
    print("        +" + "---" * len(hours))
    print("         " + "  ".join(str(h) for h in hours) + "  (시간)")
    print()
    print("  → 점들이 오른쪽 위로 올라가는 추세선이 보입니다!")
    print()


def lesson2_simple_linear_regression():
    # =========================================================================
    #
    #   레슨 2 — 단순 선형 회귀: y = wx + b
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : 단순 선형 회귀             │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 직선의 방정식: y = wx + b
    # ─────────────────────────────────────────────────────────────────────
    #
    #   w (weight, 기울기): x가 1 늘어날 때 y가 얼마나 변하는지
    #     → "공부 1시간 더 하면 점수 몇 점 오르는지"
    #
    #   b (bias, 절편): x가 0일 때의 y값
    #     → "공부를 전혀 안 해도 받는 기본 점수"
    #
    #   비유:
    #     택시비 = (거리 * km당 요금) + 기본요금
    #     여기서 km당 요금 = w, 기본요금 = b
    #

    print("  직선의 방정식: y = w * x + b")
    print()
    print("  w(기울기) = x가 1 증가할 때 y의 변화량")
    print("  b(절편)   = x가 0일 때 y의 값")
    print()

    # 예시: w=8, b=40 이라고 가정
    w, b = 8, 40

    print(f"  예시: w={w}, b={b} → y = {w}x + {b}")
    print()

    for x in range(1, 9):
        y = w * x + b
        print(f"    공부 {x}시간 → 예측 점수: {w}*{x} + {b} = {y}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 기울기의 부호에 따른 의미
    # ─────────────────────────────────────────────────────────────────────
    print("  [기울기의 부호]")
    print("    w > 0: 양의 상관관계 (공부↑ → 점수↑)")
    print("    w < 0: 음의 상관관계 (음주↑ → 건강↓)")
    print("    w = 0: 관계 없음 (신발 크기 → 시험 점수?)")
    print()


def lesson3_ols():
    # =========================================================================
    #
    #   레슨 3 — 최소제곱법 (Ordinary Least Squares, OLS)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : 최소제곱법 (OLS)           │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 아이디어: "오차의 제곱의 합"을 가장 작게 만드는 직선을 찾자
    # ─────────────────────────────────────────────────────────────────────
    #
    #   오차(잔차) = 실제값 - 예측값
    #   제곱을 하는 이유:
    #     1) 양수/음수 상관없이 크기만 보려고
    #     2) 큰 오차에 더 큰 벌점을 주려고
    #
    #   공식 (쉽게!):
    #     w = Σ(xi - x평균)(yi - y평균) / Σ(xi - x평균)²
    #     b = y평균 - w * x평균
    #

    x_data = [1, 2, 3, 4, 5, 6, 7, 8]
    y_data = [45, 50, 58, 65, 72, 78, 85, 90]
    n = len(x_data)

    # 평균 계산
    x_mean = sum(x_data) / n
    y_mean = sum(y_data) / n

    print(f"  데이터 개수: {n}")
    print(f"  x 평균: {x_mean}")
    print(f"  y 평균: {y_mean}")
    print()

    # w 계산: 분자 = Σ(xi - x평균)(yi - y평균), 분모 = Σ(xi - x평균)²
    numerator = sum((x_data[i] - x_mean) * (y_data[i] - y_mean) for i in range(n))
    denominator = sum((x_data[i] - x_mean) ** 2 for i in range(n))

    w = numerator / denominator
    b = y_mean - w * x_mean

    print("  [OLS 공식 적용]")
    print(f"    분자 Σ(xi-x평균)(yi-y평균) = {numerator:.2f}")
    print(f"    분모 Σ(xi-x평균)²          = {denominator:.2f}")
    print(f"    w = {numerator:.2f} / {denominator:.2f} = {w:.4f}")
    print(f"    b = {y_mean:.2f} - {w:.4f} * {x_mean:.2f} = {b:.4f}")
    print()
    print(f"  최적 직선: y = {w:.4f}x + {b:.4f}")
    print()

    return w, b, x_data, y_data


def lesson4_prediction_and_residuals(w, b, x_data, y_data):
    # =========================================================================
    #
    #   레슨 4 — 예측과 잔차 (Prediction & Residuals)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : 예측과 잔차                │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 잔차(Residual) = 실제값 - 예측값
    # ─────────────────────────────────────────────────────────────────────
    #
    #   잔차가 +이면 → 실제값이 예측보다 높았다 (과소예측)
    #   잔차가 -이면 → 실제값이 예측보다 낮았다 (과대예측)
    #   잔차가 0이면 → 완벽하게 맞혔다!
    #
    #   좋은 모델: 잔차가 작고, 랜덤하게 흩어져 있다
    #   나쁜 모델: 잔차에 패턴이 보인다 → 모델이 뭔가 놓치고 있다
    #

    print(f"  모델: y = {w:.4f}x + {b:.4f}")
    print()
    print(f"  {'시간':>4} | {'실제':>6} | {'예측':>8} | {'잔차':>8} | 시각화")
    print("  " + "-" * 55)

    residuals = []
    for i in range(len(x_data)):
        pred = w * x_data[i] + b
        resid = y_data[i] - pred
        residuals.append(resid)

        # 잔차 막대 시각화
        bar_len = int(abs(resid) * 2)
        if resid >= 0:
            bar = "+" * bar_len
        else:
            bar = "-" * bar_len

        print(f"  {x_data[i]:>4} | {y_data[i]:>6} | {pred:>8.2f} | {resid:>+8.2f} | {bar}")

    print()
    print(f"  잔차 합계: {sum(residuals):.6f}  (0에 가까우면 좋다!)")
    print(f"  잔차 절대값 평균: {sum(abs(r) for r in residuals) / len(residuals):.4f}")
    print()

    return residuals


def lesson5_r_squared(y_data, w, b, x_data):
    # =========================================================================
    #
    #   레슨 5 — 결정계수 R² (Coefficient of Determination)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 결정계수 R²               │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ R²는 "모델이 데이터 변동을 얼마나 설명하는가"를 나타낸다
    # ─────────────────────────────────────────────────────────────────────
    #
    #   R² = 1 - (SS_res / SS_tot)
    #
    #   SS_res = Σ(yi - 예측값)²    → 모델이 설명 못한 변동
    #   SS_tot = Σ(yi - y평균)²     → 전체 변동
    #
    #   해석:
    #     R² = 1.0  → 완벽! 모든 데이터가 직선 위에 있다
    #     R² = 0.9  → 변동의 90%를 설명 → 아주 좋다
    #     R² = 0.5  → 변동의 50%만 설명 → 보통
    #     R² = 0.0  → 평균으로 예측한 것과 같다 → 모델 의미 없음
    #     R² < 0    → 평균보다 못하다! → 모델이 쓸모없다
    #

    n = len(y_data)
    y_mean = sum(y_data) / n

    # SS_tot: 전체 변동
    ss_tot = sum((y - y_mean) ** 2 for y in y_data)

    # SS_res: 잔차 변동
    predictions = [w * x + b for x in x_data]
    ss_res = sum((y_data[i] - predictions[i]) ** 2 for i in range(n))

    r_squared = 1 - (ss_res / ss_tot)

    print("  [R² 계산 과정]")
    print(f"    y 평균: {y_mean:.2f}")
    print(f"    SS_tot (전체 변동): {ss_tot:.4f}")
    print(f"    SS_res (잔차 변동): {ss_res:.4f}")
    print(f"    R² = 1 - ({ss_res:.4f} / {ss_tot:.4f}) = {r_squared:.6f}")
    print()

    # R² 해석
    if r_squared >= 0.9:
        grade = "매우 좋음"
    elif r_squared >= 0.7:
        grade = "좋음"
    elif r_squared >= 0.5:
        grade = "보통"
    else:
        grade = "나쁨"

    print(f"  R² = {r_squared:.6f} → 평가: {grade}")
    print(f"  → 데이터 변동의 {r_squared * 100:.2f}%를 설명합니다")
    print()

    # 비교 예시
    print("  [R² 해석 가이드]")
    print("    1.00: 완벽 (현실에서 거의 불가능)")
    print("    0.95: 매우 강한 설명력")
    print("    0.80: 실용적으로 충분한 경우 많음")
    print("    0.50: 절반만 설명 → 다른 변수 추가 필요")
    print("    0.00: 평균으로 예측한 것과 동일")
    print()


def lesson6_multiple_regression():
    # =========================================================================
    #
    #   레슨 6 — 다중 선형 회귀 개념
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 다중 선형 회귀 개념        │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 변수가 2개 이상: y = w1*x1 + w2*x2 + ... + b
    # ─────────────────────────────────────────────────────────────────────
    #
    #   단순 선형 회귀: 점수 = w * 공부시간 + b
    #   다중 선형 회귀: 점수 = w1 * 공부시간 + w2 * 수면시간 + w3 * 출석률 + b
    #
    #   비유: 라면 끓이기
    #     단순: 물 양만으로 맛 예측
    #     다중: 물 양 + 면 종류 + 스프 양 + 끓이는 시간 → 맛 예측
    #

    print("  [단순 vs 다중 비교]")
    print()
    print("  단순: y = w * x + b")
    print("    예) 점수 = 6.5 * 공부시간 + 38")
    print()
    print("  다중: y = w1*x1 + w2*x2 + w3*x3 + b")
    print("    예) 점수 = 5.0*공부시간 + 3.0*수면시간 + 0.2*출석률 + 10")
    print()

    # 다중 회귀 예시 데이터
    # [공부시간, 수면시간] → 점수
    data = [
        ([2, 8], 55),
        ([3, 7], 60),
        ([5, 6], 72),
        ([7, 8], 88),
        ([8, 5], 82),
        ([4, 9], 70),
    ]

    # 수동으로 가중치를 설정해서 예측해보기
    w1, w2, b = 5.0, 3.0, 15.0

    print(f"  [수동 가중치 실험] w1={w1}, w2={w2}, b={b}")
    print(f"  {'공부':>4} {'수면':>4} | {'실제':>6} | {'예측':>6} | {'오차':>6}")
    print("  " + "-" * 42)

    for features, actual in data:
        pred = w1 * features[0] + w2 * features[1] + b
        error = actual - pred
        print(f"  {features[0]:>4} {features[1]:>4} | {actual:>6} | {pred:>6.1f} | {error:>+6.1f}")

    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 행렬 표현 (개념만)
    # ─────────────────────────────────────────────────────────────────────
    print("  [행렬 표현]")
    print("    Y = X @ W + B")
    print()
    print("    [y1]   [x11 x12] [w1]   [b]")
    print("    [y2] = [x21 x22] [w2] + [b]")
    print("    [y3]   [x31 x32]        [b]")
    print()
    print("  → 행렬 곱셈을 사용하면 모든 데이터를 한번에 계산 가능!")
    print()


def lesson7_gradient_descent():
    # =========================================================================
    #
    #   레슨 7 — 경사하강법으로 학습 (Gradient Descent)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 경사하강법                 │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 경사하강법 = "비탈길에서 공이 굴러가는 것처럼" 최적값을 찾는 방법
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유: 안개 낀 산에서 가장 낮은 곳을 찾고 싶다
    #     1. 발밑의 경사(기울기)를 느껴본다
    #     2. 내리막 방향으로 한 걸음 내려간다
    #     3. 반복!
    #
    #   학습률(learning rate):
    #     - 한 번에 얼마나 큰 걸음을 내딛을지
    #     - 너무 크면: 최적점을 지나쳐 왔다갔다 (발산)
    #     - 너무 작으면: 너무 오래 걸림
    #     - 적당하면: 점점 좋아지다가 수렴
    #
    #   업데이트 공식:
    #     w = w - learning_rate * (dL/dw)
    #     b = b - learning_rate * (dL/db)
    #
    #   MSE의 기울기:
    #     dL/dw = (-2/n) * Σ xi * (yi - (w*xi + b))
    #     dL/db = (-2/n) * Σ (yi - (w*xi + b))
    #

    x_data = [1, 2, 3, 4, 5, 6, 7, 8]
    y_data = [45, 50, 58, 65, 72, 78, 85, 90]
    n = len(x_data)

    # 초기값: 아무 값이나 시작
    w = 0.0
    b = 0.0
    learning_rate = 0.01
    epochs = 200

    print(f"  초기값: w={w}, b={b}")
    print(f"  학습률: {learning_rate}")
    print(f"  반복 횟수: {epochs}")
    print()
    print(f"  {'에폭':>6} | {'w':>8} | {'b':>8} | {'MSE':>10}")
    print("  " + "-" * 45)

    for epoch in range(epochs):
        # 예측
        predictions = [w * x + b for x in x_data]

        # MSE 계산
        mse = sum((y_data[i] - predictions[i]) ** 2 for i in range(n)) / n

        # 기울기 계산
        dw = (-2 / n) * sum(x_data[i] * (y_data[i] - predictions[i]) for i in range(n))
        db = (-2 / n) * sum(y_data[i] - predictions[i] for i in range(n))

        # 가중치 업데이트
        w = w - learning_rate * dw
        b = b - learning_rate * db

        # 일부 에폭만 출력
        if epoch < 5 or epoch % 50 == 49 or epoch == epochs - 1:
            print(f"  {epoch + 1:>6} | {w:>8.4f} | {b:>8.4f} | {mse:>10.4f}")

    print()
    print(f"  최종 결과: y = {w:.4f}x + {b:.4f}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 학습률 비교 실험
    # ─────────────────────────────────────────────────────────────────────
    print("  [학습률 비교 실험]")
    print()

    for lr in [0.001, 0.01, 0.05]:
        w_test, b_test = 0.0, 0.0
        for _ in range(100):
            preds = [w_test * x + b_test for x in x_data]
            dw = (-2 / n) * sum(x_data[i] * (y_data[i] - preds[i]) for i in range(n))
            db = (-2 / n) * sum(y_data[i] - preds[i] for i in range(n))
            w_test -= lr * dw
            b_test -= lr * db
        mse_final = sum((y_data[i] - (w_test * x_data[i] + b_test)) ** 2 for i in range(n)) / n
        print(f"    lr={lr:.3f} → 100회 후 w={w_test:.4f}, b={b_test:.4f}, MSE={mse_final:.4f}")

    print()
    print("  → 학습률이 너무 작으면 느리고, 적당하면 빠르게 수렴!")
    print()


def lesson8_practice():
    # =========================================================================
    #
    #   레슨 8 — 실전: 공부시간 → 시험점수 예측기
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 8 : 실전 예측기                │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 전체 파이프라인: 데이터 → OLS로 학습 → 예측 → 평가
    # ─────────────────────────────────────────────────────────────────────

    # 1단계: 데이터 준비 (더 현실적인 데이터)
    study_hours = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 7.0, 8.0]
    exam_scores = [30,  35,  40,  48,  52,  58,  62,  68,  75,  82,  88,  92]

    print("  [1단계] 데이터 준비")
    print(f"    학생 수: {len(study_hours)}명")
    print(f"    공부시간: {study_hours}")
    print(f"    시험점수: {exam_scores}")
    print()

    # 2단계: 학습 데이터와 테스트 데이터 분리 (처음 8개: 학습, 나머지 4개: 테스트)
    train_x, test_x = study_hours[:8], study_hours[8:]
    train_y, test_y = exam_scores[:8], exam_scores[8:]

    print("  [2단계] 데이터 분리")
    print(f"    학습 데이터: {len(train_x)}개")
    print(f"    테스트 데이터: {len(test_x)}개")
    print()

    # 3단계: OLS로 학습
    n = len(train_x)
    x_mean = sum(train_x) / n
    y_mean = sum(train_y) / n

    numerator = sum((train_x[i] - x_mean) * (train_y[i] - y_mean) for i in range(n))
    denominator = sum((train_x[i] - x_mean) ** 2 for i in range(n))

    w = numerator / denominator
    b = y_mean - w * x_mean

    print("  [3단계] OLS 학습 결과")
    print(f"    y = {w:.4f}x + {b:.4f}")
    print(f"    해석: 공부 1시간 추가 → 약 {w:.1f}점 상승, 기본 점수 약 {b:.1f}점")
    print()

    # 4단계: 테스트 데이터로 예측
    print("  [4단계] 테스트 데이터 예측")
    print(f"    {'시간':>6} | {'실제':>6} | {'예측':>6} | {'오차':>6}")
    print("    " + "-" * 35)

    test_preds = []
    for i in range(len(test_x)):
        pred = w * test_x[i] + b
        test_preds.append(pred)
        error = test_y[i] - pred
        print(f"    {test_x[i]:>6.1f} | {test_y[i]:>6} | {pred:>6.1f} | {error:>+6.1f}")
    print()

    # 5단계: 평가 (R²)
    ss_res = sum((test_y[i] - test_preds[i]) ** 2 for i in range(len(test_y)))
    test_mean = sum(test_y) / len(test_y)
    ss_tot = sum((y - test_mean) ** 2 for y in test_y)
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

    mse = ss_res / len(test_y)

    print("  [5단계] 모델 평가")
    print(f"    테스트 MSE: {mse:.4f}")
    print(f"    테스트 R² : {r2:.6f}")
    print()

    # 6단계: 새로운 학생 예측
    print("  [6단계] 새 학생 점수 예측!")
    for new_hours in [1.5, 4.5, 9.0, 10.0]:
        pred = w * new_hours + b
        # 점수는 0~100 범위로 제한
        pred_clamped = max(0, min(100, pred))
        print(f"    공부 {new_hours}시간 → 예상 점수: {pred_clamped:.1f}점")

    print()
    print("  주의: 학습 데이터 범위(0.5~8시간) 밖의 예측은 신뢰도가 떨어집니다!")
    print("  → 이것을 '외삽(extrapolation)의 위험'이라고 합니다.")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# ■ 메인 실행
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 72)
    print("  [ML 기초] 01단계: 선형 회귀 (Linear Regression)")
    print("=" * 72)
    print()

    lesson1_what_is_regression()
    lesson2_simple_linear_regression()
    w, b, x_data, y_data = lesson3_ols()
    lesson4_prediction_and_residuals(w, b, x_data, y_data)
    lesson5_r_squared(y_data, w, b, x_data)
    lesson6_multiple_regression()
    lesson7_gradient_descent()
    lesson8_practice()

    print("=" * 72)
    print("  01단계 완료! 다음: 02_train_test_split.py")
    print("=" * 72)


if __name__ == "__main__":
    main()
