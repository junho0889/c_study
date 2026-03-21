# #########################################################################
#
#   PyTorch 학습 03단계: 손실 함수와 옵티마이저
#   - Loss Functions, Optimizers, 학습 루프, 학습률 스케줄러 -
#   # 실행 방법: python 03_loss_optimizer.py (개념 학습용, PyTorch 없이 실행 가능)
#   # PyTorch 설치: pip install torch torchvision
#
# #########################################################################

import math
import random

random.seed(42)

# ===============================================================================
#  1. 손실 함수 (Loss Function) 개요
# ===============================================================================
print("=" * 70)
print("Part 1: 손실 함수 (Loss Function)")
print("=" * 70)

print("""
손실 함수 = "모델이 얼마나 틀렸는지" 측정하는 함수

비유: 과녁 맞추기
  - 화살이 과녁 중심에서 멀수록 손실이 큼
  - 손실을 줄이는 방향으로 계속 조정 → 학습!

회귀 문제: MSELoss (평균 제곱 오차)
분류 문제: CrossEntropyLoss (교차 엔트로피)
이진 분류: BCEWithLogitsLoss
""")


# -----------------------------------------------------------------------
#  MSELoss (Mean Squared Error)
# -----------------------------------------------------------------------
print("\n--- MSELoss (평균 제곱 오차) ---")
print("수식: MSE = (1/n) * Σ(y_pred - y_true)²")
print("용도: 회귀 문제 (집값 예측, 주가 예측 등)")

def mse_loss(y_pred, y_true):
    """Mean Squared Error Loss"""
    n = len(y_pred)
    return sum((p - t) ** 2 for p, t in zip(y_pred, y_true)) / n

pred = [2.5, 0.0, 2.1, 7.8]
true = [3.0, -0.5, 2.0, 7.5]
loss = mse_loss(pred, true)
print(f"\n예측: {pred}")
print(f"정답: {true}")
print(f"MSE Loss: {loss:.4f}")

# 실제 PyTorch 코드:
# criterion = nn.MSELoss()
# pred = torch.tensor([2.5, 0.0, 2.1, 7.8])
# true = torch.tensor([3.0, -0.5, 2.0, 7.5])
# loss = criterion(pred, true)
# print(loss)  # tensor(0.1525)


# -----------------------------------------------------------------------
#  CrossEntropyLoss (교차 엔트로피)
# -----------------------------------------------------------------------
print("\n\n--- CrossEntropyLoss (교차 엔트로피) ---")
print("""
수식: CE = -Σ y_true * log(softmax(y_pred))
용도: 다중 클래스 분류 (개/고양이/새 분류 등)

[주의] 매우 중요한 주의사항:
   PyTorch의 CrossEntropyLoss는 Softmax를 내부에 포함합니다!
   → 모델 출력에 Softmax를 적용하지 마세요! (이중 적용 방지)
   → 라벨은 원-핫이 아닌 정수 인덱스를 사용합니다!
""")

def softmax(logits):
    """Softmax: 로짓을 확률로 변환"""
    max_val = max(logits)  # overflow 방지 (수치 안정성)
    exp_vals = [math.exp(x - max_val) for x in logits]
    total = sum(exp_vals)
    return [e / total for e in exp_vals]

def cross_entropy_loss(logits, target_idx):
    """CrossEntropyLoss: Softmax + NLL Loss"""
    probs = softmax(logits)
    # 정답 클래스의 확률에 -log 적용
    return -math.log(probs[target_idx] + 1e-10)

# 예제: 3개 클래스 (개=0, 고양이=1, 새=2)
logits = [2.0, 1.0, 0.1]  # 모델의 raw 출력 (softmax 전!)
target = 0                  # 정답: 개(인덱스 0)

probs = softmax(logits)
loss = cross_entropy_loss(logits, target)

print(f"로짓(raw 출력): {logits}")
print(f"Softmax 확률: [{', '.join(f'{p:.4f}' for p in probs)}]")
print(f"정답 클래스: {target}")
print(f"CrossEntropy Loss: {loss:.4f}")

# 오답일 때
logits_wrong = [0.1, 2.0, 0.5]  # 고양이(1)에 높은 점수
loss_wrong = cross_entropy_loss(logits_wrong, 0)  # 정답은 개(0)
print(f"\n오답 로짓: {logits_wrong}")
print(f"오답 Loss: {loss_wrong:.4f}")
print(f"→ 틀릴수록 Loss가 크다!")

# 실제 PyTorch 코드:
# criterion = nn.CrossEntropyLoss()
# logits = torch.tensor([[2.0, 1.0, 0.1]])  # (batch, classes)
# target = torch.tensor([0])                  # 정수 인덱스!
# loss = criterion(logits, target)
#
# # [주의] 잘못된 사용:
# # output = F.softmax(model(x))  ← 이미 softmax 적용
# # loss = criterion(output, target)  ← CrossEntropyLoss가 또 softmax → 이중 적용!


# -----------------------------------------------------------------------
#  BCEWithLogitsLoss (이진 교차 엔트로피)
# -----------------------------------------------------------------------
print("\n\n--- BCEWithLogitsLoss (이진 교차 엔트로피) ---")
print("용도: 이진 분류 (스팸/정상, 양성/음성)")
print("내부에 Sigmoid 포함 → 모델 출력에 Sigmoid 적용 금지!")

def sigmoid(x):
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    exp_x = math.exp(x)
    return exp_x / (1.0 + exp_x)

def bce_with_logits_loss(logit, target):
    """BCEWithLogitsLoss = Sigmoid + BCE"""
    # Sigmoid 적용 후 BCE 계산
    prob = sigmoid(logit)
    return -(target * math.log(prob + 1e-10) + (1 - target) * math.log(1 - prob + 1e-10))

logit = 2.0    # 모델 raw 출력 (sigmoid 전!)
target = 1.0   # 양성
loss = bce_with_logits_loss(logit, target)
print(f"\n로짓: {logit}, Sigmoid 확률: {sigmoid(logit):.4f}")
print(f"정답: {target}")
print(f"BCEWithLogits Loss: {loss:.4f}")

# 실제 PyTorch 코드:
# criterion = nn.BCEWithLogitsLoss()
# logit = torch.tensor([2.0])
# target = torch.tensor([1.0])
# loss = criterion(logit, target)


# ===============================================================================
#  2. 옵티마이저 (Optimizer)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 2: 옵티마이저 (Optimizer)")
print("=" * 70)

print("""
옵티마이저 = "손실을 줄이기 위해 파라미터를 어떻게 업데이트할지" 결정

비유: 산에서 내려가는 방법
  SGD  = 기본 걸어 내려가기 (단순하지만 확실)
  Adam = GPS + 스마트 신발 (방향과 보폭을 자동 조절)
""")


# --- SGD (Stochastic Gradient Descent) ---
print("\n--- SGD (확률적 경사하강법) ---")
print("수식: θ = θ - lr * grad")
print("모멘텀: v = β * v + grad, θ = θ - lr * v (관성 추가)")

class SGD:
    """Stochastic Gradient Descent 옵티마이저"""

    def __init__(self, params, lr=0.01, momentum=0.0):
        self.params = params
        self.lr = lr
        self.momentum = momentum
        self.velocities = [0.0] * len(params) if momentum > 0 else None

    def step(self):
        """파라미터 업데이트"""
        for i, param in enumerate(self.params):
            if param.get('grad') is not None:
                if self.momentum > 0:
                    self.velocities[i] = self.momentum * self.velocities[i] + param['grad']
                    param['value'] -= self.lr * self.velocities[i]
                else:
                    param['value'] -= self.lr * param['grad']

    def zero_grad(self):
        """기울기 초기화"""
        for param in self.params:
            param['grad'] = None


# SGD 테스트
print("\nSGD 시뮬레이션 (y = x^2의 최솟값 찾기):")
param_x = {'value': 5.0, 'grad': None}
optimizer = SGD([param_x], lr=0.1)

for step in range(20):
    # 기울기 계산: d(x^2)/dx = 2x
    param_x['grad'] = 2 * param_x['value']
    optimizer.step()
    optimizer.zero_grad()
    if step % 5 == 0:
        print(f"  Step {step:2d}: x={param_x['value']:.4f}, f(x)={param_x['value']**2:.4f}")

# 실제 PyTorch 코드:
# optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9)


# --- Adam ---
print("\n--- Adam (Adaptive Moment Estimation) ---")
print("""
Adam = SGD + 모멘텀 + 학습률 자동 조절
  - 각 파라미터마다 다른 학습률 적용
  - 대부분의 경우 기본 선택으로 좋음
  - 기본 학습률: lr=0.001
""")

class Adam:
    """Adam 옵티마이저 (간소화)"""

    def __init__(self, params, lr=0.001, beta1=0.9, beta2=0.999, eps=1e-8):
        self.params = params
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.eps = eps
        self.t = 0
        self.m = [0.0] * len(params)  # 1차 모멘트 (평균)
        self.v = [0.0] * len(params)  # 2차 모멘트 (분산)

    def step(self):
        self.t += 1
        for i, param in enumerate(self.params):
            if param.get('grad') is not None:
                g = param['grad']
                # 모멘트 업데이트
                self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * g
                self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * g ** 2
                # 편향 보정
                m_hat = self.m[i] / (1 - self.beta1 ** self.t)
                v_hat = self.v[i] / (1 - self.beta2 ** self.t)
                # 업데이트
                param['value'] -= self.lr * m_hat / (math.sqrt(v_hat) + self.eps)

    def zero_grad(self):
        for param in self.params:
            param['grad'] = None


# Adam 테스트
print("Adam 시뮬레이션 (y = x^2의 최솟값 찾기):")
param_x = {'value': 5.0, 'grad': None}
optimizer = Adam([param_x], lr=0.5)

for step in range(20):
    param_x['grad'] = 2 * param_x['value']
    optimizer.step()
    optimizer.zero_grad()
    if step % 5 == 0:
        print(f"  Step {step:2d}: x={param_x['value']:.6f}, f(x)={param_x['value']**2:.6f}")

# 실제 PyTorch 코드:
# optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
# optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
# AdamW: Adam + 가중치 감쇠 (정규화, 과적합 방지)


# ===============================================================================
#  3. 학습 루프 (Training Loop)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 3: 학습 루프")
print("=" * 70)

print("""
PyTorch 학습 루프의 정석 5단계:

for epoch in range(num_epochs):
    for batch in dataloader:
        ① optimizer.zero_grad()     # 기울기 초기화
        ② output = model(input)     # 순전파 (Forward)
        ③ loss = criterion(output, target)  # 손실 계산
        ④ loss.backward()           # 역전파 (Backward)
        ⑤ optimizer.step()          # 파라미터 업데이트

이 순서를 반드시 기억하세요!
비유: 시험 공부
  ① 깨끗한 연습장 준비 (zero_grad)
  ② 문제 풀기 (forward)
  ③ 채점하기 (loss)
  ④ 틀린 부분 분석 (backward)
  ⑤ 오답 노트 반영 (step)
""")


# ===============================================================================
#  4. 왜 zero_grad()가 필요한가?
# ===============================================================================
print("\n" + "=" * 70)
print("Part 4: 왜 zero_grad()가 필요한가?")
print("=" * 70)

print("""
PyTorch는 기울기를 누적(accumulate)합니다!

왜? 일부 상황에서 기울기 누적이 유용하기 때문:
  - 큰 배치를 여러 작은 미니배치로 나눠 처리할 때
  - Gradient Accumulation 기법

하지만 일반적으로는 매 스텝마다 초기화해야 합니다.
zero_grad() 안 하면 → 이전 기울기 + 현재 기울기 = 잘못된 업데이트!
""")

# 기울기 누적 문제 시연
print("--- 기울기 누적 문제 시연 ---")
grad_value = 0.0  # 파라미터의 기울기

# zero_grad 없이 반복
for i in range(3):
    new_grad = 2.0  # 매 스텝 기울기가 2.0이라고 가정
    grad_value += new_grad  # 누적!
    print(f"  Step {i+1}: 기울기 = {grad_value} (zero_grad 없으면 계속 누적!)")

print()
grad_value = 0.0
for i in range(3):
    grad_value = 0.0  # zero_grad!
    new_grad = 2.0
    grad_value += new_grad
    print(f"  Step {i+1}: 기울기 = {grad_value} (zero_grad 하면 매번 정확!)")


# ===============================================================================
#  5. 학습률 스케줄러 (Learning Rate Scheduler)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 5: 학습률 스케줄러")
print("=" * 70)

print("""
학습률 스케줄러 = 학습 중 학습률을 동적으로 조절

비유: 산에서 내려갈 때
  - 처음에는 큰 걸음으로 빠르게 (높은 학습률)
  - 정상 근처에서는 조심조심 작은 걸음으로 (낮은 학습률)
  - 너무 큰 걸음이면 최적점을 지나칠 수 있음!
""")

# --- StepLR ---
print("--- StepLR: 일정 에폭마다 학습률 감소 ---")

class StepLR:
    def __init__(self, initial_lr, step_size, gamma=0.1):
        self.initial_lr = initial_lr
        self.step_size = step_size
        self.gamma = gamma

    def get_lr(self, epoch):
        return self.initial_lr * (self.gamma ** (epoch // self.step_size))

scheduler = StepLR(initial_lr=0.1, step_size=30, gamma=0.1)
for epoch in [0, 10, 29, 30, 50, 60, 90]:
    print(f"  Epoch {epoch:3d}: lr = {scheduler.get_lr(epoch):.6f}")

# 실제 PyTorch 코드:
# scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.1)
# for epoch in range(100):
#     train(...)
#     scheduler.step()

# --- CosineAnnealingLR ---
print("\n--- CosineAnnealingLR: 코사인 곡선으로 학습률 감소 ---")

class CosineAnnealingLR:
    def __init__(self, initial_lr, T_max, eta_min=0):
        self.initial_lr = initial_lr
        self.T_max = T_max
        self.eta_min = eta_min

    def get_lr(self, epoch):
        return self.eta_min + (self.initial_lr - self.eta_min) * \
               (1 + math.cos(math.pi * epoch / self.T_max)) / 2

scheduler = CosineAnnealingLR(initial_lr=0.1, T_max=100)
for epoch in [0, 25, 50, 75, 100]:
    print(f"  Epoch {epoch:3d}: lr = {scheduler.get_lr(epoch):.6f}")

# 실제 PyTorch 코드:
# scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=100)

# --- ReduceLROnPlateau ---
print("\n--- ReduceLROnPlateau: 성능 정체 시 학습률 감소 ---")
print("  검증 손실이 patience 에폭 동안 개선되지 않으면 학습률을 factor만큼 감소")

class ReduceLROnPlateau:
    def __init__(self, initial_lr, patience=10, factor=0.1):
        self.lr = initial_lr
        self.patience = patience
        self.factor = factor
        self.best_loss = float('inf')
        self.counter = 0

    def step(self, val_loss):
        if val_loss < self.best_loss:
            self.best_loss = val_loss
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.lr *= self.factor
                self.counter = 0
                print(f"    → 학습률 감소! 새 lr = {self.lr:.6f}")

scheduler = ReduceLROnPlateau(initial_lr=0.01, patience=3, factor=0.5)
fake_losses = [0.5, 0.4, 0.35, 0.35, 0.36, 0.37, 0.38, 0.30, 0.29, 0.29, 0.30, 0.30, 0.31]
for epoch, loss in enumerate(fake_losses):
    scheduler.step(loss)
    print(f"  Epoch {epoch:2d}: val_loss={loss:.2f}, lr={scheduler.lr:.6f}, patience_counter={scheduler.counter}")

# 실제 PyTorch 코드:
# scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
#     optimizer, mode='min', patience=10, factor=0.1
# )
# for epoch in range(100):
#     train(...)
#     val_loss = validate(...)
#     scheduler.step(val_loss)


# ===============================================================================
#  6. 실습: 완전한 학습 루프 구현
# ===============================================================================
print("\n" + "=" * 70)
print("Part 6: 실습 - 완전한 학습 루프")
print("=" * 70)

print("문제: 2차 함수 y = 0.5*x^2 + 3*x + 1 의 데이터를 신경망으로 학습\n")

# 데이터 생성
X_train = [random.uniform(-5, 5) for _ in range(100)]
Y_train = [0.5 * x ** 2 + 3 * x + 1 + random.gauss(0, 0.5) for x in X_train]

# 간단한 신경망 (수동 구현)
class SimpleNet:
    def __init__(self):
        # 가중치 초기화
        self.w1 = [[random.gauss(0, 0.5) for _ in range(1)] for _ in range(10)]  # 1→10
        self.b1 = [0.0] * 10
        self.w2 = [[random.gauss(0, 0.5) for _ in range(10)] for _ in range(1)]  # 10→1
        self.b2 = [0.0]

    def forward(self, x):
        # 은닉층
        h = [sum(x * self.w1[j][0] for _ in [0]) + self.b1[j] for j in range(10)]
        # 실제로는 x * w1[j][0]
        h = [max(0, val) for val in h]  # ReLU
        # 출력층
        out = sum(h[k] * self.w2[0][k] for k in range(10)) + self.b2[0]
        return out

    def get_all_params(self):
        """모든 파라미터를 flat list로"""
        params = []
        for row in self.w1:
            params.extend(row)
        params.extend(self.b1)
        for row in self.w2:
            params.extend(row)
        params.extend(self.b2)
        return params

net = SimpleNet()

# 학습 (수치 미분 기반)
lr = 0.001
print("--- 학습 시작 ---")

for epoch in range(50):
    # 전체 손실 계산
    total_loss = 0.0
    for x, y_true in zip(X_train, Y_train):
        y_pred = net.forward(x)
        total_loss += (y_pred - y_true) ** 2
    avg_loss = total_loss / len(X_train)

    if epoch % 10 == 0:
        print(f"  Epoch {epoch:3d}: MSE Loss = {avg_loss:.4f}")

    # 수치 미분으로 w1 업데이트
    h = 1e-5
    for i in range(10):
        for j in range(1):
            original = net.w1[i][j]
            net.w1[i][j] = original + h
            loss_plus = sum((net.forward(x) - y) ** 2 for x, y in zip(X_train, Y_train)) / len(X_train)
            net.w1[i][j] = original - h
            loss_minus = sum((net.forward(x) - y) ** 2 for x, y in zip(X_train, Y_train)) / len(X_train)
            net.w1[i][j] = original
            grad = (loss_plus - loss_minus) / (2 * h)
            net.w1[i][j] -= lr * grad

    # b1 업데이트
    for i in range(10):
        original = net.b1[i]
        net.b1[i] = original + h
        loss_plus = sum((net.forward(x) - y) ** 2 for x, y in zip(X_train, Y_train)) / len(X_train)
        net.b1[i] = original - h
        loss_minus = sum((net.forward(x) - y) ** 2 for x, y in zip(X_train, Y_train)) / len(X_train)
        net.b1[i] = original
        grad = (loss_plus - loss_minus) / (2 * h)
        net.b1[i] -= lr * grad

    # w2, b2 업데이트
    for i in range(1):
        for j in range(10):
            original = net.w2[i][j]
            net.w2[i][j] = original + h
            loss_plus = sum((net.forward(x) - y) ** 2 for x, y in zip(X_train, Y_train)) / len(X_train)
            net.w2[i][j] = original - h
            loss_minus = sum((net.forward(x) - y) ** 2 for x, y in zip(X_train, Y_train)) / len(X_train)
            net.w2[i][j] = original
            grad = (loss_plus - loss_minus) / (2 * h)
            net.w2[i][j] -= lr * grad

    original = net.b2[0]
    net.b2[0] = original + h
    loss_plus = sum((net.forward(x) - y) ** 2 for x, y in zip(X_train, Y_train)) / len(X_train)
    net.b2[0] = original - h
    loss_minus = sum((net.forward(x) - y) ** 2 for x, y in zip(X_train, Y_train)) / len(X_train)
    net.b2[0] = original
    grad = (loss_plus - loss_minus) / (2 * h)
    net.b2[0] -= lr * grad

# 검증
print("\n--- 학습 결과 검증 ---")
test_xs = [-3.0, -1.0, 0.0, 1.0, 3.0]
for x in test_xs:
    y_true = 0.5 * x ** 2 + 3 * x + 1
    y_pred = net.forward(x)
    print(f"  x={x:5.1f} | 정답={y_true:7.2f} | 예측={y_pred:7.2f} | 오차={abs(y_pred-y_true):5.2f}")

# 실제 PyTorch 코드:
# import torch
# import torch.nn as nn
#
# # 데이터
# X = torch.tensor(X_train, dtype=torch.float32).unsqueeze(1)  # (100, 1)
# Y = torch.tensor(Y_train, dtype=torch.float32).unsqueeze(1)  # (100, 1)
#
# # 모델
# model = nn.Sequential(
#     nn.Linear(1, 10),
#     nn.ReLU(),
#     nn.Linear(10, 1)
# )
#
# # 손실 & 옵티마이저
# criterion = nn.MSELoss()
# optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
#
# # 학습 루프
# for epoch in range(500):
#     optimizer.zero_grad()           # ① 기울기 초기화
#     output = model(X)               # ② 순전파
#     loss = criterion(output, Y)     # ③ 손실 계산
#     loss.backward()                 # ④ 역전파
#     optimizer.step()                # ⑤ 업데이트
#
#     if epoch % 100 == 0:
#         print(f"Epoch {epoch}: loss={loss.item():.4f}")


# ===============================================================================
#  핵심 정리
# ===============================================================================
print("\n" + "=" * 70)
print("핵심 정리")
print("=" * 70)
print("""
1. 손실 함수:
   - MSELoss: 회귀 문제
   - CrossEntropyLoss: 다중 분류 (Softmax 내장! 정수 라벨!)
   - BCEWithLogitsLoss: 이진 분류 (Sigmoid 내장!)

2. 옵티마이저:
   - SGD: 기본, momentum 추가 권장
   - Adam: 대부분의 경우 좋은 기본 선택 (lr=0.001)
   - AdamW: Adam + weight decay (정규화)

3. 학습 루프 5단계:
   zero_grad() → forward() → loss → backward() → step()

4. zero_grad() 필수! (기울기 누적 방지)

5. 학습률 스케줄러:
   - StepLR: 일정 간격으로 감소
   - CosineAnnealingLR: 코사인 곡선
   - ReduceLROnPlateau: 성능 정체 시 감소

[주의] 흔한 실수:
   - CrossEntropyLoss에 Softmax 이중 적용
   - zero_grad() 빼먹기
   - loss.item()으로 스칼라 추출 안 하기 (메모리 누수)
""")
