# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   TensorFlow/Keras 학습 04단계: 옵티마이저와 손실 함수
#   ─ SGD, Adam, RMSprop, 학습률 스케줄링, 다양한 Loss 함수 ─
#   ■ 실행 방법: python 04_optimizers_loss.py (개념 학습용 코드, TF 없이 실행 가능)
#   ■ TensorFlow 설치: pip install tensorflow
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import random

random.seed(42)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. 옵티마이저란?
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("1. 옵티마이저(Optimizer)란?")
print("=" * 70)

print("""
■ 옵티마이저 = 가중치 업데이트 전략
  손실(Loss)을 최소화하도록 가중치를 조정하는 알고리즘

  비유: 눈을 가리고 산에서 내려가기
  - SGD:     발밑 경사만 느끼고 한 걸음씩
  - Momentum: 관성(이전 방향의 가속도)을 이용
  - Adam:    경사 + 관성 + 적응적 학습률 → 가장 똑똑!

  핵심 아이디어: w_new = w_old - learning_rate * gradient
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. SGD (Stochastic Gradient Descent)
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("2. SGD - 확률적 경사하강법")
print("=" * 70)

class ToySGD:
    """기본 SGD 옵티마이저"""
    def __init__(self, lr=0.01):
        self.lr = lr
        self.name = "SGD"

    def update(self, params, grads):
        """파라미터 업데이트: w = w - lr * grad"""
        return [p - self.lr * g for p, g in zip(params, grads)]

class ToySGDMomentum:
    """SGD with Momentum"""
    def __init__(self, lr=0.01, momentum=0.9):
        self.lr = lr
        self.momentum = momentum
        self.velocity = None
        self.name = f"SGD(momentum={momentum})"

    def update(self, params, grads):
        if self.velocity is None:
            self.velocity = [0.0] * len(params)
        new_params = []
        for i in range(len(params)):
            # v = momentum * v - lr * grad
            self.velocity[i] = self.momentum * self.velocity[i] - self.lr * grads[i]
            # w = w + v
            new_params.append(params[i] + self.velocity[i])
        return new_params

class ToySGDNesterov:
    """SGD with Nesterov Momentum (NAG)"""
    def __init__(self, lr=0.01, momentum=0.9):
        self.lr = lr
        self.momentum = momentum
        self.velocity = None
        self.name = f"SGD(Nesterov, momentum={momentum})"

    def update(self, params, grads):
        if self.velocity is None:
            self.velocity = [0.0] * len(params)
        new_params = []
        for i in range(len(params)):
            v_prev = self.velocity[i]
            self.velocity[i] = self.momentum * self.velocity[i] - self.lr * grads[i]
            # 미래 위치를 미리 계산하여 보정
            new_params.append(params[i] - self.momentum * v_prev + (1 + self.momentum) * self.velocity[i])
        return new_params

print("""
■ SGD 변형 비교:
  1. 기본 SGD:     w = w - lr * grad
     → 단순하지만 느림, 지그재그 경로

  2. SGD + Momentum: 이전 업데이트 방향을 기억
     v = momentum * v_prev + lr * grad
     w = w - v
     비유: 볼링공이 굴러가듯 관성 이용!

  3. SGD + Nesterov: 미래 위치에서 기울기 계산
     → Momentum보다 더 빠른 수렴
     비유: "한 발 먼저 내딛고 기울기 계산"
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Adam - 가장 많이 쓰는 옵티마이저
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("3. Adam (Adaptive Moment Estimation)")
print("=" * 70)

class ToyAdam:
    """Adam 옵티마이저"""
    def __init__(self, lr=0.001, beta1=0.9, beta2=0.999, epsilon=1e-8):
        self.lr = lr
        self.beta1 = beta1        # 1차 모멘트(평균) 감쇠율
        self.beta2 = beta2        # 2차 모멘트(분산) 감쇠율
        self.epsilon = epsilon    # 0으로 나누기 방지
        self.m = None             # 1차 모멘트 (기울기의 평균)
        self.v = None             # 2차 모멘트 (기울기 제곱의 평균)
        self.t = 0                # 타임스텝
        self.name = "Adam"

    def update(self, params, grads):
        if self.m is None:
            self.m = [0.0] * len(params)
            self.v = [0.0] * len(params)

        self.t += 1
        new_params = []

        for i in range(len(params)):
            # 1차 모멘트 업데이트 (기울기의 이동 평균)
            self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * grads[i]
            # 2차 모멘트 업데이트 (기울기 제곱의 이동 평균)
            self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * grads[i] ** 2

            # 편향 보정 (초기 단계에서 0에 치우치는 것 방지)
            m_hat = self.m[i] / (1 - self.beta1 ** self.t)
            v_hat = self.v[i] / (1 - self.beta2 ** self.t)

            # 파라미터 업데이트
            new_params.append(params[i] - self.lr * m_hat / (math.sqrt(v_hat) + self.epsilon))

        return new_params

print("""
■ Adam이 왜 인기인가?
  SGD + Momentum + RMSprop의 장점을 합침!

  핵심 아이디어:
  1. m (1차 모멘트): 기울기의 이동 평균 → 방향 정보
     → Momentum과 비슷한 역할

  2. v (2차 모멘트): 기울기 제곱의 이동 평균 → 크기 정보
     → 자주 업데이트되는 파라미터는 학습률 ↓
     → 드물게 업데이트되는 파라미터는 학습률 ↑

  3. 편향 보정: 초기 단계에서 0에 치우치는 것 방지

■ 하이퍼파라미터:
  - lr=0.001      : 대부분의 경우 이 값으로 시작 (기본값)
  - beta1=0.9     : 1차 모멘트 감쇠 (거의 안 바꿈)
  - beta2=0.999   : 2차 모멘트 감쇠 (거의 안 바꿈)
  - epsilon=1e-8  : 수치 안정성 (거의 안 바꿈)
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 4. RMSprop, Adagrad
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("4. RMSprop, Adagrad")
print("=" * 70)

class ToyAdagrad:
    """Adagrad 옵티마이저"""
    def __init__(self, lr=0.01, epsilon=1e-8):
        self.lr = lr
        self.epsilon = epsilon
        self.accumulated = None
        self.name = "Adagrad"

    def update(self, params, grads):
        if self.accumulated is None:
            self.accumulated = [0.0] * len(params)
        new_params = []
        for i in range(len(params)):
            self.accumulated[i] += grads[i] ** 2
            # 적응적 학습률: 자주 업데이트된 파라미터일수록 학습률 감소
            new_params.append(
                params[i] - self.lr * grads[i] / (math.sqrt(self.accumulated[i]) + self.epsilon)
            )
        return new_params

class ToyRMSprop:
    """RMSprop 옵티마이저"""
    def __init__(self, lr=0.001, rho=0.9, epsilon=1e-8):
        self.lr = lr
        self.rho = rho
        self.epsilon = epsilon
        self.avg_sq = None
        self.name = "RMSprop"

    def update(self, params, grads):
        if self.avg_sq is None:
            self.avg_sq = [0.0] * len(params)
        new_params = []
        for i in range(len(params)):
            # 이동 평균으로 기울기 제곱의 평균 추적
            self.avg_sq[i] = self.rho * self.avg_sq[i] + (1 - self.rho) * grads[i] ** 2
            new_params.append(
                params[i] - self.lr * grads[i] / (math.sqrt(self.avg_sq[i]) + self.epsilon)
            )
        return new_params

print("""
■ Adagrad:
  - 각 파라미터별 학습률을 적응적으로 조절
  - 자주 등장하는 특성 → 학습률 감소
  - 문제점: 학습률이 계속 감소 → 나중에 학습 멈춤

■ RMSprop (Hinton 교수 제안):
  - Adagrad의 학습률 감소 문제 해결
  - 이동 평균(moving average)으로 최근 기울기만 반영
  - RNN 학습에서 특히 효과적

■ 옵티마이저 비교 정리:
  ┌───────────┬──────────────────────────────────────┐
  │ 옵티마이저│ 특징                                  │
  ├───────────┼──────────────────────────────────────┤
  │ SGD       │ 단순, 느림, 일반화 성능 좋을 수 있음 │
  │ Momentum  │ 관성 이용, 빠른 수렴                 │
  │ Adagrad   │ 적응적 lr, NLP에 유용               │
  │ RMSprop   │ Adagrad 개선, RNN에 좋음            │
  │ Adam      │ 만능, 기본 선택                      │
  │ AdamW     │ Adam + 가중치 감쇠 분리             │
  └───────────┴──────────────────────────────────────┘
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 5. 학습률 스케줄링
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("5. 학습률 스케줄링 (Learning Rate Scheduling)")
print("=" * 70)

print("""
■ 왜 학습률을 바꿔야 하나?
  - 처음: 높은 학습률로 빠르게 탐색 (넓게 보기)
  - 나중: 낮은 학습률로 정밀 조정 (좁게 보기)

  비유: 축구장에서 열쇠 찾기
  1단계: 큰 보폭으로 넓은 영역 탐색
  2단계: 발견 근처에서 작은 보폭으로 정밀 탐색
""")

def step_decay(initial_lr, epoch, drop_rate=0.5, epochs_drop=10):
    """StepDecay: 일정 에포크마다 학습률을 일정 비율로 감소"""
    return initial_lr * (drop_rate ** (epoch // epochs_drop))

def exponential_decay(initial_lr, epoch, decay_rate=0.96):
    """ExponentialDecay: 매 에포크 지수적으로 감소"""
    return initial_lr * (decay_rate ** epoch)

def cosine_annealing(initial_lr, epoch, total_epochs):
    """CosineAnnealing: 코사인 곡선을 따라 감소"""
    return initial_lr * 0.5 * (1 + math.cos(math.pi * epoch / total_epochs))

def warmup_cosine(initial_lr, epoch, warmup_epochs=5, total_epochs=100):
    """Warmup + Cosine: 처음에 천천히 올리다가 코사인으로 감소"""
    if epoch < warmup_epochs:
        return initial_lr * epoch / warmup_epochs
    else:
        progress = (epoch - warmup_epochs) / (total_epochs - warmup_epochs)
        return initial_lr * 0.5 * (1 + math.cos(math.pi * progress))

initial_lr = 0.01
total_epochs = 50

print(f"\n■ 학습률 스케줄링 비교 (초기 lr={initial_lr}):")
print(f"  {'Epoch':>5}  {'Step':>8}  {'Exponential':>12}  {'Cosine':>8}  {'Warmup+Cos':>10}")
print(f"  {'─'*5}  {'─'*8}  {'─'*12}  {'─'*8}  {'─'*10}")

for epoch in [0, 5, 10, 15, 20, 25, 30, 40, 49]:
    sd = step_decay(initial_lr, epoch)
    ed = exponential_decay(initial_lr, epoch)
    ca = cosine_annealing(initial_lr, epoch, total_epochs)
    wc = warmup_cosine(initial_lr, epoch, warmup_epochs=5, total_epochs=total_epochs)
    print(f"  {epoch:5d}  {sd:8.6f}  {ed:12.6f}  {ca:8.6f}  {wc:10.6f}")

# 학습률 스케줄링 ASCII 시각화
print(f"\n■ 코사인 어닐링 시각화:")
cos_lrs = [cosine_annealing(initial_lr, e, total_epochs) for e in range(total_epochs)]
max_lr = max(cos_lrs)
for row in range(5, -1, -1):
    threshold = max_lr * row / 5
    line = ""
    for lr in cos_lrs:
        line += "█" if lr >= threshold else " "
    print(f"  {threshold:.4f} │{line}│")
print(f"  {'':6s}  └{'─' * total_epochs}┘")
print(f"  {'':7s}  0{' ' * (total_epochs - 5)}Epoch {total_epochs}")

# 실제 코드: 학습률 스케줄링
# 실제 코드: lr_schedule = tf.keras.optimizers.schedules.CosineDecay(
# 실제 코드:     initial_learning_rate=0.01,
# 실제 코드:     decay_steps=1000
# 실제 코드: )
# 실제 코드: optimizer = tf.keras.optimizers.Adam(learning_rate=lr_schedule)
# 실제 코드:
# 실제 코드: # 또는 콜백 사용
# 실제 코드: reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
# 실제 코드:     monitor='val_loss', factor=0.5, patience=5
# 실제 코드: )


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Loss 함수 - 손실 함수 총정리
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("6. 손실(Loss) 함수 총정리")
print("=" * 70)

print("""
■ 손실 함수 = 모델의 예측이 얼마나 틀렸는지 측정하는 함수
  손실이 작을수록 좋은 모델!

  문제 유형별 손실 함수:
  ┌──────────────────────────────────────────────────┐
  │ 문제 유형        │ 손실 함수           │ 출력층  │
  ├──────────────────────────────────────────────────┤
  │ 이진 분류        │ binary_crossentropy │sigmoid │
  │ 다중 분류(원핫)  │ categorical_CE      │softmax │
  │ 다중 분류(정수)  │ sparse_categorical  │softmax │
  │ 회귀             │ mse / mae           │linear  │
  └──────────────────────────────────────────────────┘
""")

# --- MSE (Mean Squared Error) ---
def mse_loss(y_true, y_pred):
    """평균 제곱 오차: 회귀 문제의 기본 손실 함수"""
    n = len(y_true)
    return sum((t - p) ** 2 for t, p in zip(y_true, y_pred)) / n

# --- MAE (Mean Absolute Error) ---
def mae_loss(y_true, y_pred):
    """평균 절대 오차: 이상치에 MSE보다 강건"""
    n = len(y_true)
    return sum(abs(t - p) for t, p in zip(y_true, y_pred)) / n

# --- Binary Cross-Entropy ---
def binary_crossentropy(y_true, y_pred):
    """이진 교차 엔트로피: 이진 분류 문제"""
    eps = 1e-7
    n = len(y_true)
    loss = 0
    for t, p in zip(y_true, y_pred):
        p = max(eps, min(1 - eps, p))  # 클리핑
        loss += -(t * math.log(p) + (1 - t) * math.log(1 - p))
    return loss / n

# --- Categorical Cross-Entropy ---
def categorical_crossentropy(y_true_onehot, y_pred_probs):
    """범주형 교차 엔트로피: 다중 분류 (원핫 인코딩)"""
    eps = 1e-7
    loss = 0
    for t, p in zip(y_true_onehot, y_pred_probs):
        p = max(eps, min(1 - eps, p))
        loss += -t * math.log(p)
    return loss

# --- Sparse Categorical Cross-Entropy ---
def sparse_categorical_crossentropy(y_true_index, y_pred_probs):
    """희소 범주형 교차 엔트로피: 다중 분류 (정수 라벨)"""
    eps = 1e-7
    p = max(eps, min(1 - eps, y_pred_probs[y_true_index]))
    return -math.log(p)

# 손실 함수 비교
print("■ 회귀 손실 함수 비교:")
y_true = [3.0, 5.0, 7.0, 9.0]
y_pred = [2.8, 5.3, 6.5, 9.2]
print(f"  실제값: {y_true}")
print(f"  예측값: {y_pred}")
print(f"  MSE: {mse_loss(y_true, y_pred):.4f}")
print(f"  MAE: {mae_loss(y_true, y_pred):.4f}")

# 이상치의 영향
y_true_outlier = [3.0, 5.0, 7.0, 100.0]
y_pred_outlier = [2.8, 5.3, 6.5, 9.2]
print(f"\n  이상치 포함 데이터:")
print(f"  실제값: {y_true_outlier}")
print(f"  MSE: {mse_loss(y_true_outlier, y_pred_outlier):.1f}  ← 이상치에 민감!")
print(f"  MAE: {mae_loss(y_true_outlier, y_pred_outlier):.1f}  ← 상대적으로 강건")

# 분류 손실 함수
print(f"\n■ 분류 손실 함수:")
print(f"\n  이진 분류 (Binary Cross-Entropy):")
y_true_bin = [1, 0, 1, 1, 0]
y_pred_good = [0.9, 0.1, 0.8, 0.95, 0.05]
y_pred_bad = [0.5, 0.5, 0.5, 0.5, 0.5]
print(f"  실제:       {y_true_bin}")
print(f"  좋은 예측:  {y_pred_good}  → BCE = {binary_crossentropy(y_true_bin, y_pred_good):.4f}")
print(f"  나쁜 예측:  {y_pred_bad}  → BCE = {binary_crossentropy(y_true_bin, y_pred_bad):.4f}")

print(f"\n  다중 분류 (Categorical Cross-Entropy):")
y_true_cat = [0, 0, 1]  # 원핫: 클래스 2
y_pred_cat1 = [0.1, 0.1, 0.8]  # 좋은 예측
y_pred_cat2 = [0.3, 0.4, 0.3]  # 나쁜 예측
print(f"  실제 (원핫): {y_true_cat}  (클래스 2)")
print(f"  좋은 예측:   {y_pred_cat1}  → CE = {categorical_crossentropy(y_true_cat, y_pred_cat1):.4f}")
print(f"  나쁜 예측:   {y_pred_cat2}  → CE = {categorical_crossentropy(y_true_cat, y_pred_cat2):.4f}")

print(f"\n  Sparse Categorical Cross-Entropy:")
y_true_idx = 2  # 클래스 2 (정수)
print(f"  실제 (정수): {y_true_idx}")
print(f"  예측 확률:   {y_pred_cat1}")
print(f"  → Loss = {sparse_categorical_crossentropy(y_true_idx, y_pred_cat1):.4f}")
print(f"  → Categorical CE와 동일한 결과! (표현 방식만 다름)")


# ═══════════════════════════════════════════════════════════════════════════════
# 7. Cross-Entropy 직관적 이해
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("7. Cross-Entropy 직관적 이해")
print("=" * 70)

print("""
■ Cross-Entropy(교차 엔트로피)란?
  두 확률 분포가 얼마나 다른지 측정하는 지표

  비유: 정답 배팅 게임
  - 정답: 고양이 (확률=1.0)
  - 모델 A: "고양이 90%" → 손실 적음 (확신있게 맞춤)
  - 모델 B: "고양이 10%" → 손실 큼 (확신있게 틀림!)

  수학적으로: CE = -sum(y_true * log(y_pred))
  → 정답에 해당하는 예측 확률의 -log 값
""")

# 확률 vs 손실 관계
print("■ 예측 확률 vs 손실값:")
print(f"  {'정답확률':>8}  {'-log(p)':>8}  {'의미':>20}")
print(f"  {'─'*8}  {'─'*8}  {'─'*20}")
for p in [0.99, 0.9, 0.8, 0.5, 0.3, 0.1, 0.01]:
    loss = -math.log(p)
    bar = "█" * int(loss * 5)
    meaning = ""
    if p >= 0.9:
        meaning = "매우 확신 → 낮은 손실"
    elif p >= 0.5:
        meaning = "어느 정도 → 중간 손실"
    else:
        meaning = "틀린 방향 → 높은 손실!"
    print(f"  {p:8.2f}  {loss:8.4f}  {meaning}")

# 실제 코드: tf.keras.losses.BinaryCrossentropy()
# 실제 코드: tf.keras.losses.CategoricalCrossentropy()
# 실제 코드: tf.keras.losses.SparseCategoricalCrossentropy()
# 실제 코드: tf.keras.losses.MeanSquaredError()


# ═══════════════════════════════════════════════════════════════════════════════
# 8. [실습] 옵티마이저별 수렴 속도 비교
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("8. [실습] 옵티마이저별 수렴 속도 비교")
print("=" * 70)

# 목적 함수: Rosenbrock 함수 (최적화 벤치마크)
# f(x, y) = (1 - x)^2 + 100*(y - x^2)^2
# 최솟값: f(1, 1) = 0

def rosenbrock(x, y):
    """Rosenbrock 함수 - 최적화 벤치마크"""
    return (1 - x) ** 2 + 100 * (y - x ** 2) ** 2

def rosenbrock_grad(x, y):
    """Rosenbrock 기울기"""
    dx = -2 * (1 - x) + 100 * 2 * (y - x ** 2) * (-2 * x)
    dy = 100 * 2 * (y - x ** 2)
    return [dx, dy]

# 간단한 함수로 테스트: f(x, y) = x^2 + 10*y^2 (타원형 계곡)
def ellipse(x, y):
    return x ** 2 + 10 * y ** 2

def ellipse_grad(x, y):
    return [2 * x, 20 * y]

print("■ 최적화 문제: f(x,y) = x^2 + 10*y^2")
print("  최솟값: f(0, 0) = 0")
print("  시작점: (5.0, 5.0)")

optimizers = [
    ToySGD(lr=0.01),
    ToySGDMomentum(lr=0.01, momentum=0.9),
    ToyRMSprop(lr=0.01),
    ToyAdam(lr=0.1),
]

results = {}
n_steps = 100

for opt in optimizers:
    params = [5.0, 5.0]
    history = [(params[0], params[1], ellipse(params[0], params[1]))]

    for step in range(n_steps):
        grads = ellipse_grad(params[0], params[1])
        params = opt.update(params, grads)
        loss = ellipse(params[0], params[1])
        history.append((params[0], params[1], loss))

    results[opt.name] = history

# 결과 출력
print(f"\n  {'Step':>4}  ", end="")
for opt in optimizers:
    print(f"  {opt.name:>15}", end="")
print()
print(f"  {'─'*4}  ", end="")
for _ in optimizers:
    print(f"  {'─'*15}", end="")
print()

for step in [0, 5, 10, 20, 50, 99]:
    print(f"  {step:4d}  ", end="")
    for opt in optimizers:
        loss = results[opt.name][step][2]
        print(f"  {loss:15.4f}", end="")
    print()

# 최종 결과
print(f"\n  최종 위치:")
for opt in optimizers:
    x, y, loss = results[opt.name][-1]
    print(f"  {opt.name:20s}  x={x:.6f}, y={y:.6f}, loss={loss:.6f}")

# ASCII 수렴 그래프
print(f"\n■ 수렴 속도 비교 (손실의 로그):")
for opt in optimizers:
    losses = [max(1e-10, h[2]) for h in results[opt.name]]
    log_losses = [math.log10(max(1e-10, l)) for l in losses[:50]]
    if log_losses:
        max_log = max(log_losses)
        min_log = min(log_losses)
        range_log = max_log - min_log if max_log != min_log else 1.0
        bar = ""
        for ll in log_losses[::5]:
            normalized = int(5 * (ll - min_log) / range_log) if range_log > 0 else 0
            bar += "▁▂▃▄▅▆"[min(normalized, 5)]
        print(f"  {opt.name:20s}  {bar}")

# 실제 코드: 옵티마이저 사용
# 실제 코드: model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
# 실제 코드:               loss='sparse_categorical_crossentropy',
# 실제 코드:               metrics=['accuracy'])
# 실제 코드:
# 실제 코드: # 또는 커스텀 설정
# 실제 코드: optimizer = tf.keras.optimizers.SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
# 실제 코드: optimizer = tf.keras.optimizers.RMSprop(learning_rate=0.001, rho=0.9)
# 실제 코드: optimizer = tf.keras.optimizers.Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999)


# ═══════════════════════════════════════════════════════════════════════════════
# 9. 옵티마이저 선택 가이드
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("9. 옵티마이저 선택 가이드")
print("=" * 70)

print("""
■ 실용적 선택 가이드:

  1. 처음 시작할 때 → Adam (lr=0.001)
     - 대부분의 문제에서 잘 동작
     - 하이퍼파라미터 튜닝 필요 적음

  2. 높은 정확도가 필요할 때 → SGD + Momentum + 학습률 스케줄링
     - 컴퓨터 비전(ImageNet)에서 자주 사용
     - 일반화 성능이 Adam보다 좋을 수 있음
     - 하지만 튜닝이 더 어려움

  3. RNN/시계열 → Adam 또는 RMSprop
     - 그래디언트가 불안정한 경우에 효과적

  4. Transformer/대규모 모델 → AdamW
     - Adam + 가중치 감쇠(weight decay)
     - GPT, BERT 등에서 표준

■ 학습률 설정 팁:
  - 너무 크면: 발산 (loss가 NaN 또는 증가)
  - 너무 작으면: 수렴이 매우 느림
  - Learning Rate Finder: 작은 lr부터 시작해 점점 키우며 loss 관찰
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 10. 정규화(Regularization)와 가중치 감쇠
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("10. 정규화(Regularization) - 과적합 방지")
print("=" * 70)

print("""
■ L1 정규화 (Lasso):
  Loss_total = Loss_data + lambda * sum(|w|)
  → 가중치를 0으로 만듦 (특성 선택 효과)
  비유: "불필요한 연결은 끊어라!"

■ L2 정규화 (Ridge / Weight Decay):
  Loss_total = Loss_data + lambda * sum(w^2)
  → 가중치를 작게 만듦 (극단적 값 방지)
  비유: "모든 연결의 강도를 줄여라!"

■ 비교:
  L1: 일부 가중치가 정확히 0 → 희소(sparse) 모델
  L2: 모든 가중치가 작아짐 → 부드러운(smooth) 모델
""")

# L2 정규화 시연
def loss_with_l2(y_true, y_pred, weights, lambda_l2=0.01):
    """L2 정규화가 적용된 손실"""
    data_loss = mse_loss(y_true, y_pred)
    l2_penalty = sum(w ** 2 for w in weights) * lambda_l2
    return data_loss, l2_penalty, data_loss + l2_penalty

weights_large = [5.0, -3.0, 4.0, -2.0]
weights_small = [0.5, -0.3, 0.4, -0.2]
y_true_demo = [1.0]
y_pred_demo = [0.9]

dl_l, l2_l, total_l = loss_with_l2(y_true_demo, y_pred_demo, weights_large)
dl_s, l2_s, total_s = loss_with_l2(y_true_demo, y_pred_demo, weights_small)

print(f"\n■ L2 정규화 효과:")
print(f"  큰 가중치 {weights_large}:")
print(f"    데이터 손실={dl_l:.4f}, L2 페널티={l2_l:.4f}, 총={total_l:.4f}")
print(f"  작은 가중치 {weights_small}:")
print(f"    데이터 손실={dl_s:.4f}, L2 페널티={l2_s:.4f}, 총={total_s:.4f}")
print(f"  → 같은 예측이라도 가중치가 크면 패널티!")

# 실제 코드: L2 정규화 사용
# 실제 코드: from tensorflow.keras import regularizers
# 실제 코드: tf.keras.layers.Dense(64, activation='relu',
# 실제 코드:                       kernel_regularizer=regularizers.l2(0.01))
# 실제 코드:
# 실제 코드: # AdamW (Adam + Weight Decay)
# 실제 코드: optimizer = tf.keras.optimizers.AdamW(learning_rate=0.001, weight_decay=0.01)


print("\n" + "=" * 70)
print("요약: 옵티마이저와 손실 함수 학습 완료!")
print("=" * 70)
print("""
  1. SGD: 기본, momentum/nesterov로 개선 가능
  2. Adam: 만능 옵티마이저, lr=0.001로 시작
  3. 학습률 스케줄링: Cosine Annealing, Warmup+Cosine
  4. MSE: 회귀, Binary CE: 이진분류, Categorical CE: 다중분류
  5. Cross-Entropy: 확률 분포 간 차이 측정
  6. L1/L2 정규화: 과적합 방지

  다음 단계 → 05_cnn_image.py (CNN으로 이미지 분류!)
""")
