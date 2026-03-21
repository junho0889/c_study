# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [딥러닝] 학습 04단계: 손실 함수 기초 (Loss Functions)
#   ─ MSE, MAE, 이진 교차 엔트로피, 범주형 교차 엔트로피, 기울기 ─
#   ■ 실행 방법: python 04_loss_basics.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 손실 함수란? - 예측과 정답의 차이, 왜 필요한지
#   2. MSE (평균 제곱 오차) - 회귀에서 사용
#   3. MAE (평균 절대 오차) - MSE와 비교, 이상치에 강함
#   4. 이진 교차 엔트로피 - 확률 예측에서 사용
#   5. 범주형 교차 엔트로피 - 다중 클래스
#   6. 손실 함수의 기울기 - 왜 미분이 필요한지
#   7. 손실 함수 선택 가이드
#   8. 실전: 다양한 손실 함수 비교 실험
#
# ─────────────────────────────────────────────────────────────────────────


def lesson1_what_is_loss():
    # =========================================================================
    #
    #   레슨 1 — 손실 함수란?
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 손실 함수란?               │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 손실 함수(Loss Function) = 예측이 얼마나 틀렸는지 숫자로 표현
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유: 시험에서 감점
    #     정답: 80점, 예측: 75점 → 감점(손실) = 5점
    #     정답: 80점, 예측: 80점 → 감점(손실) = 0점
    #
    #   학습 = 손실을 줄이는 방향으로 가중치를 조금씩 조절
    #
    #   손실이 크면 → "많이 틀렸다" → 많이 수정
    #   손실이 작으면 → "조금 틀렸다" → 조금 수정
    #   손실이 0이면 → "완벽하다!" → 수정 안 함
    #

    print("  [손실 함수의 역할]")
    print()
    print("    입력 → [모델] → 예측값")
    print("                      ↕ 비교")
    print("                    정답값")
    print("                      ↓")
    print("                   손실(Loss)")
    print("                      ↓")
    print("              가중치 업데이트")
    print()

    # 간단한 예시
    print("  [예시: 시험 점수 예측]")
    predictions = [75, 82, 60, 90]
    actuals     = [80, 80, 65, 88]

    print(f"    {'예측':>6} | {'정답':>6} | {'오차':>6} | 시각화")
    print("    " + "-" * 40)
    for pred, actual in zip(predictions, actuals):
        error = abs(actual - pred)
        bar = "X" * error
        print(f"    {pred:>6} | {actual:>6} | {error:>6} | {bar}")
    print()
    print(f"    평균 오차: {sum(abs(a-p) for a,p in zip(actuals, predictions))/len(actuals):.2f}")
    print()

    # 왜 하나의 숫자로 표현해야 하는가
    print("  [왜 하나의 숫자로 표현하는가?]")
    print("    '이 모델이 더 좋다'를 비교하려면 하나의 점수가 필요!")
    print("    모델A 손실=3.5 vs 모델B 손실=2.1 → 모델B가 더 좋다!")
    print()


def lesson2_mse():
    # =========================================================================
    #
    #   레슨 2 — MSE (Mean Squared Error, 평균 제곱 오차)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : MSE (평균 제곱 오차)       │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ MSE = (1/n) * Σ(yi - y_pred_i)²
    # ─────────────────────────────────────────────────────────────────────
    #
    #   제곱하는 이유:
    #     1. 양수/음수 상관없이 오차 크기만 봄
    #     2. 큰 오차에 더 큰 벌점 (2배 차이 → 4배 벌점)
    #     3. 미분이 깔끔함 → 경사하강법에 유리
    #

    def mse(y_true, y_pred):
        n = len(y_true)
        return sum((t - p) ** 2 for t, p in zip(y_true, y_pred)) / n

    # 수동 계산
    y_true = [80, 65, 90, 75]
    y_pred = [78, 70, 85, 72]
    n = len(y_true)

    print("  [MSE 공식] MSE = (1/n) * sum((yi - pi)^2)")
    print()
    print(f"    정답: {y_true}")
    print(f"    예측: {y_pred}")
    print()

    total = 0
    for i in range(n):
        diff = y_true[i] - y_pred[i]
        sq = diff ** 2
        total += sq
        print(f"    ({y_true[i]} - {y_pred[i]})^2 = ({diff:+d})^2 = {sq}")

    result = total / n
    print(f"    합계: {total}")
    print(f"    MSE = {total} / {n} = {result:.2f}")
    print()

    # 제곱의 효과 시연
    print("  [제곱의 효과: 큰 오차에 더 큰 벌점]")
    print()
    print(f"    {'오차':>6} | {'제곱':>8} | 비율")
    print("    " + "-" * 30)
    for err in [1, 2, 3, 5, 10]:
        sq = err ** 2
        bar = "#" * (sq // 2 if sq < 50 else 50)
        print(f"    {err:>6} | {sq:>8} | {bar}")
    print()
    print("    → 오차 1→10 (10배) → 제곱 1→100 (100배!)")
    print("    → 큰 오차를 줄이는 데 집중하게 만든다")
    print()

    # RMSE
    rmse = result ** 0.5
    print(f"  [RMSE (Root MSE)] = sqrt(MSE) = sqrt({result:.2f}) = {rmse:.4f}")
    print("    → 원래 단위로 해석 가능 (점수 단위)")
    print()


def lesson3_mae():
    # =========================================================================
    #
    #   레슨 3 — MAE (Mean Absolute Error, 평균 절대 오차)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : MAE (평균 절대 오차)       │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ MAE = (1/n) * Σ|yi - y_pred_i|
    # ─────────────────────────────────────────────────────────────────────
    #
    #   MSE와의 차이:
    #     MSE: 제곱 → 큰 오차에 큰 벌점
    #     MAE: 절대값 → 모든 오차에 동일한 가중치
    #
    #   이상치에 강한 이유:
    #     이상치(outlier)는 오차가 매우 큰 데이터
    #     MSE는 제곱하므로 이상치의 영향이 폭발적
    #     MAE는 절대값이므로 이상치의 영향이 선형적
    #

    def mae(y_true, y_pred):
        n = len(y_true)
        return sum(abs(t - p) for t, p in zip(y_true, y_pred)) / n

    def mse(y_true, y_pred):
        n = len(y_true)
        return sum((t - p) ** 2 for t, p in zip(y_true, y_pred)) / n

    # 일반 데이터
    y_true_normal = [80, 65, 90, 75]
    y_pred_normal = [78, 70, 85, 72]

    print("  [일반 데이터]")
    print(f"    정답: {y_true_normal}")
    print(f"    예측: {y_pred_normal}")
    print()

    print(f"    MAE 계산:")
    total = 0
    for t, p in zip(y_true_normal, y_pred_normal):
        abs_err = abs(t - p)
        total += abs_err
        print(f"      |{t} - {p}| = {abs_err}")
    print(f"      MAE = {total} / {len(y_true_normal)} = {total/len(y_true_normal):.2f}")
    print(f"      MSE = {mse(y_true_normal, y_pred_normal):.2f}")
    print()

    # 이상치 포함 데이터
    y_true_outlier = [80, 65, 90, 75, 70]
    y_pred_outlier = [78, 70, 85, 72, 20]  # 20은 이상치 (70에 대해 50 차이)

    print("  [이상치 포함 데이터]")
    print(f"    정답: {y_true_outlier}")
    print(f"    예측: {y_pred_outlier}  ← 마지막이 이상치!")
    print()

    mae_val = mae(y_true_outlier, y_pred_outlier)
    mse_val = mse(y_true_outlier, y_pred_outlier)

    print(f"    MAE = {mae_val:.2f}")
    print(f"    MSE = {mse_val:.2f}")
    print()

    # 이상치 영향 비교
    mae_normal = mae(y_true_normal, y_pred_normal)
    mse_normal = mse(y_true_normal, y_pred_normal)

    mae_change = mae_val / mae_normal if mae_normal > 0 else 0
    mse_change = mse_val / mse_normal if mse_normal > 0 else 0

    print(f"    이상치 추가 전후 비교:")
    print(f"      MAE: {mae_normal:.2f} → {mae_val:.2f} ({mae_change:.1f}배)")
    print(f"      MSE: {mse_normal:.2f} → {mse_val:.2f} ({mse_change:.1f}배)")
    print(f"    → MSE가 이상치에 훨씬 민감!")
    print()

    # MSE vs MAE 정리
    print("  [MSE vs MAE 비교]")
    print("    ┌──────────┬────────────────┬────────────────┐")
    print("    │          │ MSE            │ MAE            │")
    print("    ├──────────┼────────────────┼────────────────┤")
    print("    │ 수식     │ (y-p)^2의 평균 │ |y-p|의 평균   │")
    print("    │ 큰 오차  │ 크게 벌점      │ 동일하게 벌점  │")
    print("    │ 이상치   │ 매우 민감       │ 덜 민감        │")
    print("    │ 미분     │ 매끄러움       │ z=0에서 불연속  │")
    print("    │ 기본값   │ 대부분 기본     │ 이상치 많을 때 │")
    print("    └──────────┴────────────────┴────────────────┘")
    print()


def lesson4_binary_cross_entropy():
    # =========================================================================
    #
    #   레슨 4 — 이진 교차 엔트로피 (Binary Cross-Entropy)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : 이진 교차 엔트로피         │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ BCE = -(1/n) * Σ[yi*log(pi) + (1-yi)*log(1-pi)]
    # ─────────────────────────────────────────────────────────────────────
    #
    #   이진 분류에서 사용 (합격/불합격, 스팸/정상)
    #   예측값(p)는 시그모이드 출력 → 0~1 사이 확률
    #
    #   왜 MSE 대신 교차 엔트로피?
    #     MSE로 확률을 학습하면 기울기가 너무 작아서 느림
    #     교차 엔트로피는 확률이 틀릴수록 기울기가 커짐 → 빠른 학습
    #

    def bce_single(y_true, y_pred):
        """단일 샘플의 BCE"""
        eps = 1e-7  # log(0) 방지
        y_pred = max(eps, min(1 - eps, y_pred))
        return -(y_true * math.log(y_pred) + (1 - y_true) * math.log(1 - y_pred))

    def bce(y_true_list, y_pred_list):
        """배치 BCE"""
        n = len(y_true_list)
        return sum(bce_single(t, p) for t, p in zip(y_true_list, y_pred_list)) / n

    # 수치 예제: y=1 (양성)일 때
    print("  [y=1 (양성)일 때 예측 확률에 따른 손실]")
    print()
    print(f"    {'예측(p)':>8} | {'손실':>8} | 시각화")
    print("    " + "-" * 40)

    for p in [0.99, 0.9, 0.7, 0.5, 0.3, 0.1, 0.01]:
        loss = bce_single(1, p)
        bar = "#" * int(loss * 5)
        print(f"    {p:>8.2f} | {loss:>8.4f} | {bar}")
    print()
    print("    → p=0.99(거의 확신) → 손실 약 0 (잘 맞춤)")
    print("    → p=0.01(거의 틀림) → 손실 약 4.6 (큰 벌점)")
    print()

    # y=0 (음성)일 때
    print("  [y=0 (음성)일 때 예측 확률에 따른 손실]")
    print()
    for p in [0.01, 0.1, 0.3, 0.5, 0.7, 0.9, 0.99]:
        loss = bce_single(0, p)
        bar = "#" * int(loss * 5)
        print(f"    p={p:.2f} → 손실={loss:.4f} {bar}")
    print()

    # 수동 계산 예시
    print("  [배치 BCE 수동 계산]")
    y_true = [1,   0,   1,   0  ]
    y_pred = [0.9, 0.2, 0.7, 0.1]

    print(f"    정답: {y_true}")
    print(f"    예측: {y_pred}")
    print()

    total = 0
    for i in range(len(y_true)):
        loss_i = bce_single(y_true[i], y_pred[i])
        total += loss_i
        if y_true[i] == 1:
            formula = f"-log({y_pred[i]})"
        else:
            formula = f"-log(1-{y_pred[i]})"
        print(f"    샘플{i+1}: y={y_true[i]}, p={y_pred[i]} → {formula} = {loss_i:.4f}")

    result = total / len(y_true)
    print(f"\n    BCE = {total:.4f} / {len(y_true)} = {result:.4f}")
    print()


def lesson5_categorical_cross_entropy():
    # =========================================================================
    #
    #   레슨 5 — 범주형 교차 엔트로피 (Categorical Cross-Entropy)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 범주형 교차 엔트로피       │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ CCE = -Σ yi * log(pi)   (원-핫 인코딩된 yi에 대해)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   다중 클래스 분류에서 사용 (개/고양이/새, A/B/C 학점 등)
    #   예측은 Softmax 출력 → 각 클래스의 확률
    #   정답은 원-핫 인코딩 → [0, 0, 1] (정답 클래스만 1)
    #
    #   사실 정답이 1인 클래스의 -log(p)만 계산하면 됨!
    #   (나머지는 y=0이므로 0*log(p)=0)
    #

    def cce(y_true_onehot, y_pred_probs):
        """단일 샘플의 범주형 교차 엔트로피"""
        eps = 1e-7
        loss = 0
        for y, p in zip(y_true_onehot, y_pred_probs):
            loss -= y * math.log(max(p, eps))
        return loss

    # 예제: 3클래스 (사과, 바나나, 포도)
    classes = ["사과", "바나나", "포도"]

    print("  [3클래스 분류 예제]")
    print(f"    클래스: {classes}")
    print()

    # 정답: 사과 [1, 0, 0]
    y_true = [1, 0, 0]

    # 다양한 예측 비교
    predictions = [
        ([0.9, 0.05, 0.05], "거의 확신 (좋은 예측)"),
        ([0.7, 0.2,  0.1],  "꽤 확신"),
        ([0.4, 0.3,  0.3],  "불확실"),
        ([0.1, 0.1,  0.8],  "완전히 틀림 (포도라고 예측)"),
    ]

    print(f"    정답: 사과 {y_true}")
    print()
    print(f"    {'예측 확률':>25} | {'손실':>8} | 평가")
    print("    " + "-" * 55)

    for pred, desc in predictions:
        loss = cce(y_true, pred)
        print(f"    {str(pred):>25} | {loss:>8.4f} | {desc}")
    print()

    # 원-핫 인코딩 설명
    print("  [원-핫 인코딩이란?]")
    print()
    for i, cls in enumerate(classes):
        onehot = [0] * len(classes)
        onehot[i] = 1
        print(f"    정답이 '{cls}'일 때: {onehot}")
    print()

    # CCE가 실제로 -log(정답 클래스 확률)임을 보여줌
    print("  [CCE 계산 = -log(정답 클래스의 확률)]")
    print()
    for pred, desc in predictions:
        full_calc = " + ".join(f"{y}*log({p})" for y, p in zip(y_true, pred))
        simple = f"-log({pred[0]})"  # 정답이 첫 번째 클래스
        loss = cce(y_true, pred)
        print(f"    -({full_calc})")
        print(f"    = {simple} = {loss:.4f}")
        print()


def lesson6_loss_gradient():
    # =========================================================================
    #
    #   레슨 6 — 손실 함수의 기울기
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 손실 함수의 기울기         │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 기울기(Gradient) = 손실을 줄이는 방향
    # ─────────────────────────────────────────────────────────────────────
    #
    #   손실 함수를 가중치(w)에 대해 미분하면:
    #     dL/dw > 0 → w를 줄여야 손실이 줄어든다
    #     dL/dw < 0 → w를 늘려야 손실이 줄어든다
    #     dL/dw = 0 → 최적점 (또는 안장점)
    #
    #   업데이트: w_new = w_old - lr * (dL/dw)
    #

    # MSE의 기울기 시연
    print("  [MSE 기울기 시연]")
    print()
    print("    MSE = (y - (w*x + b))^2 의 w에 대한 미분:")
    print("    dMSE/dw = -2 * x * (y - (w*x + b))")
    print()

    # 단일 데이터: x=2, y=10
    x, y = 2, 10
    b = 0

    print(f"    데이터: x={x}, y={y}, b={b}")
    print()
    print(f"    {'w':>5} | {'예측':>6} | {'MSE':>8} | {'기울기':>8} | 방향")
    print("    " + "-" * 50)

    for w in [0, 1, 2, 3, 4, 5, 6]:
        pred = w * x + b
        loss = (y - pred) ** 2
        grad = -2 * x * (y - pred)
        direction = "w 줄여!" if grad > 0 else ("w 늘려!" if grad < 0 else "최적!")
        print(f"    {w:>5} | {pred:>6} | {loss:>8} | {grad:>+8} | {direction}")
    print()
    print("    → w=5일 때 예측=10, MSE=0, 기울기=0 → 최적!")
    print()

    # 기울기의 크기 = 업데이트 크기
    print("  [기울기 크기와 학습 속도]")
    print()
    print("    기울기가 크면 → 많이 틀렸다 → 많이 수정")
    print("    기울기가 작으면 → 조금 틀렸다 → 조금 수정")
    print()

    # 수치적 미분 vs 해석적 미분 비교
    print("  [수치적 미분 (확인용)]")
    w = 3.0
    h = 0.0001

    def mse_loss(w_val):
        pred = w_val * x + b
        return (y - pred) ** 2

    numerical_grad = (mse_loss(w + h) - mse_loss(w - h)) / (2 * h)
    analytical_grad = -2 * x * (y - (w * x + b))

    print(f"    w={w}에서:")
    print(f"    수치적 기울기:  {numerical_grad:.4f}")
    print(f"    해석적 기울기:  {analytical_grad:.4f}")
    print(f"    차이: {abs(numerical_grad - analytical_grad):.8f} (거의 같다!)")
    print()


def lesson7_selection_guide():
    # =========================================================================
    #
    #   레슨 7 — 손실 함수 선택 가이드
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 손실 함수 선택 가이드      │")
    print("└──────────────────────────────────────┘")
    print()

    print("  [문제 유형별 손실 함수 추천]")
    print()
    print("  ┌────────────────────┬──────────────────────┬──────────────────┐")
    print("  │ 문제 유형          │ 손실 함수            │ 출력층 활성화    │")
    print("  ├────────────────────┼──────────────────────┼──────────────────┤")
    print("  │ 회귀               │ MSE (기본)           │ 없음 (선형)      │")
    print("  │ 회귀 (이상치 많음) │ MAE 또는 Huber       │ 없음 (선형)      │")
    print("  │ 이진 분류          │ Binary Cross-Entropy │ Sigmoid          │")
    print("  │ 다중 분류          │ Categorical CE       │ Softmax          │")
    print("  └────────────────────┴──────────────────────┴──────────────────┘")
    print()

    # Huber Loss 설명
    print("  [보너스: Huber Loss (MSE + MAE 혼합)]")
    print()
    print("    작은 오차 → MSE처럼 (매끄러운 기울기)")
    print("    큰 오차   → MAE처럼 (이상치에 덜 민감)")
    print()

    def huber_loss(y_true, y_pred, delta=1.0):
        error = abs(y_true - y_pred)
        if error <= delta:
            return 0.5 * error ** 2
        else:
            return delta * error - 0.5 * delta ** 2

    print(f"    delta={1.0}일 때:")
    print(f"    {'오차':>6} | {'MSE':>8} | {'MAE':>8} | {'Huber':>8}")
    print("    " + "-" * 40)
    for err in [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]:
        mse_val = err ** 2
        mae_val = abs(err)
        hub_val = huber_loss(0, err, delta=1.0)
        print(f"    {err:>6.1f} | {mse_val:>8.2f} | {mae_val:>8.2f} | {hub_val:>8.2f}")
    print()

    # 자주 하는 실수
    print("  [자주 하는 실수]")
    print("    1. 분류 문제에 MSE 사용")
    print("       → 확률 학습이 느리고 불안정")
    print("    2. 회귀 문제에 Cross-Entropy 사용")
    print("       → log에 음수/0이 들어가면 오류!")
    print("    3. 이진 분류에 Categorical CE 사용")
    print("       → 불필요하게 복잡 (BCE로 충분)")
    print()


def lesson8_practice():
    # =========================================================================
    #
    #   레슨 8 — 실전: 다양한 손실 함수 비교 실험
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 8 : 손실 함수 비교 실험        │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 실험 1: 회귀 - MSE vs MAE
    # ─────────────────────────────────────────────────────────────────────

    def mse(y_true, y_pred):
        n = len(y_true)
        return sum((t - p) ** 2 for t, p in zip(y_true, y_pred)) / n

    def mae(y_true, y_pred):
        n = len(y_true)
        return sum(abs(t - p) for t, p in zip(y_true, y_pred)) / n

    # 데이터: y = 3x + 5
    x_data = [1, 2, 3, 4, 5]
    y_true = [8, 11, 14, 17, 20]

    print("  [실험 1: 회귀 - MSE로 최적 w 찾기]")
    print(f"    정답: y = 3x + 5")
    print()

    b = 5  # 편향 고정, w만 변화
    print(f"    {'w':>5} | {'MSE':>10} | {'MAE':>10} | MSE 그래프")
    print("    " + "-" * 50)

    for w in [0, 1, 2, 2.5, 3, 3.5, 4, 5]:
        y_pred = [w * x + b for x in x_data]
        mse_val = mse(y_true, y_pred)
        mae_val = mae(y_true, y_pred)
        bar = "#" * int(mse_val / 2) if mse_val < 60 else "#" * 30 + ">"
        print(f"    {w:>5.1f} | {mse_val:>10.2f} | {mae_val:>10.2f} | {bar}")
    print()
    print("    → w=3일 때 MSE=0, MAE=0 → 최적!")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 실험 2: 분류 - MSE vs BCE
    # ─────────────────────────────────────────────────────────────────────

    def bce(y_true, y_pred):
        eps = 1e-7
        n = len(y_true)
        total = 0
        for t, p in zip(y_true, y_pred):
            p = max(eps, min(1 - eps, p))
            total -= t * math.log(p) + (1 - t) * math.log(1 - p)
        return total / n

    print("  [실험 2: 분류 - MSE vs BCE 비교]")
    print()

    y_true_cls = [1, 0, 1, 1, 0]

    # 다양한 예측 품질
    pred_sets = [
        ([0.9, 0.1, 0.8, 0.9, 0.2], "좋은 예측"),
        ([0.7, 0.3, 0.6, 0.7, 0.4], "보통 예측"),
        ([0.5, 0.5, 0.5, 0.5, 0.5], "랜덤 예측"),
        ([0.2, 0.8, 0.3, 0.2, 0.7], "나쁜 예측"),
    ]

    print(f"    정답: {y_true_cls}")
    print()
    print(f"    {'설명':>10} | {'MSE':>8} | {'BCE':>8}")
    print("    " + "-" * 35)

    for preds, desc in pred_sets:
        mse_val = mse(y_true_cls, preds)
        bce_val = bce(y_true_cls, preds)
        print(f"    {desc:>10} | {mse_val:>8.4f} | {bce_val:>8.4f}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 실험 3: 경사하강법으로 학습 비교
    # ─────────────────────────────────────────────────────────────────────

    print("  [실험 3: MSE 경사하강법으로 w 학습]")
    print()

    w = 0.0
    b_fixed = 5.0
    lr = 0.01
    n = len(x_data)

    print(f"    초기 w={w}, 학습률={lr}")
    print(f"    {'에폭':>6} | {'w':>8} | {'MSE':>10}")
    print("    " + "-" * 32)

    for epoch in range(20):
        # 예측
        y_pred = [w * x + b_fixed for x in x_data]

        # MSE
        loss = mse(y_true, y_pred)

        # 기울기: dMSE/dw = (-2/n) * sum(xi * (yi - pi))
        dw = (-2 / n) * sum(x_data[i] * (y_true[i] - y_pred[i]) for i in range(n))

        # 업데이트
        w = w - lr * dw

        if epoch < 5 or epoch % 5 == 4:
            print(f"    {epoch+1:>6} | {w:>8.4f} | {loss:>10.4f}")

    print()
    print(f"    최종 w = {w:.4f} (정답: 3.0)")
    print()

    # 최종 정리
    print("  [손실 함수 핵심 정리]")
    print("    1. 손실 함수 = 모델이 얼마나 틀렸는지의 점수")
    print("    2. 학습 = 손실을 줄이는 방향으로 가중치 수정")
    print("    3. 기울기 = 어느 방향으로 수정할지 알려주는 나침반")
    print("    4. 문제 유형에 맞는 손실 함수를 선택하라!")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# ■ 메인 실행
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 72)
    print("  [딥러닝] 04단계: 손실 함수 기초 (Loss Functions)")
    print("=" * 72)
    print()

    lesson1_what_is_loss()
    lesson2_mse()
    lesson3_mae()
    lesson4_binary_cross_entropy()
    lesson5_categorical_cross_entropy()
    lesson6_loss_gradient()
    lesson7_selection_guide()
    lesson8_practice()

    print("=" * 72)
    print("  04단계 완료!")
    print("=" * 72)


if __name__ == "__main__":
    main()
