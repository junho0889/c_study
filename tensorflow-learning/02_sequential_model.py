# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   TensorFlow/Keras 학습 02단계: Sequential 모델
#   ─ 레이어 쌓기, Dense, compile, fit, evaluate, predict ─
#   ■ 실행 방법: python 02_sequential_model.py (개념 학습용 코드, TF 없이 실행 가능)
#   ■ TensorFlow 설치: pip install tensorflow
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import random

random.seed(42)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. Sequential 모델이란?
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("1. Sequential 모델 - 레이어를 순서대로 쌓기")
print("=" * 70)

# Sequential 모델은 레이어를 한 층씩 차례로 쌓는 가장 간단한 방식입니다.
# 비유: 샌드위치 만들기!
#   빵 → 양상추 → 치즈 → 패티 → 빵
#   입력 → Dense(64) → Dense(32) → Dense(1) → 출력

print("""
■ Sequential 모델 구조:
  ┌──────────────────────┐
  │   Input (입력)        │  ← 데이터가 들어옴
  ├──────────────────────┤
  │   Dense(64, relu)    │  ← 은닉층 1
  ├──────────────────────┤
  │   Dense(32, relu)    │  ← 은닉층 2
  ├──────────────────────┤
  │   Dense(1, sigmoid)  │  ← 출력층
  └──────────────────────┘

  데이터는 위에서 아래로 순서대로 흐릅니다.
  각 레이어는 이전 레이어의 출력을 입력으로 받습니다.
""")

# 실제 코드: Sequential 모델 생성
# 실제 코드: model = tf.keras.Sequential([
# 실제 코드:     tf.keras.layers.Dense(64, activation='relu', input_shape=(10,)),
# 실제 코드:     tf.keras.layers.Dense(32, activation='relu'),
# 실제 코드:     tf.keras.layers.Dense(1, activation='sigmoid')
# 실제 코드: ])


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Dense 레이어 - 완전 연결 계층
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("2. Dense 레이어 내부 동작: y = activation(W @ x + b)")
print("=" * 70)

# Dense 레이어 = 완전 연결 (Fully Connected) 레이어
# 모든 입력 뉴런이 모든 출력 뉴런과 연결됩니다.
# 수식: output = activation(W @ input + bias)

print("""
■ Dense 레이어 비유:
  투표 시스템이라고 생각하세요!

  입력(3개)    가중치(W)       출력(2개)
  x0=0.5 ─── w00=0.3 ──→ ┐
  x0=0.5 ─── w01=0.7 ──→ ┤→ y0 = relu(x0*w00 + x1*w10 + x2*w20 + b0)
  x1=0.8 ─── w10=0.2 ──→ ┘
  x1=0.8 ─── w11=0.4 ──→ ┐
  x2=0.1 ─── w20=0.9 ──→ ┤→ y1 = relu(x0*w01 + x1*w11 + x2*w21 + b1)
  x2=0.1 ─── w21=0.5 ──→ ┘
""")

def relu(x):
    """ReLU 활성화 함수: max(0, x)"""
    return max(0.0, x)

def sigmoid(x):
    """시그모이드: 출력을 0~1 사이로 압축"""
    return 1.0 / (1.0 + math.exp(-max(-500, min(500, x))))

def softmax(values):
    """소프트맥스: 여러 값을 확률 분포로 변환"""
    max_val = max(values)
    exp_vals = [math.exp(v - max_val) for v in values]
    total = sum(exp_vals)
    return [e / total for e in exp_vals]

class ToyDense:
    """Dense 레이어의 토이 구현"""
    def __init__(self, input_size, units, activation=None, name="dense"):
        self.input_size = input_size
        self.units = units
        self.activation = activation
        self.name = name

        # 가중치 초기화 (Xavier/Glorot 초기화 근사)
        limit = math.sqrt(6.0 / (input_size + units))
        self.weights = [
            [random.uniform(-limit, limit) for _ in range(units)]
            for _ in range(input_size)
        ]
        self.biases = [0.0] * units  # 편향은 0으로 초기화

    def forward(self, inputs):
        """순전파: y = activation(Wx + b)"""
        outputs = []
        for j in range(self.units):
            # 가중합 계산
            z = sum(inputs[i] * self.weights[i][j] for i in range(self.input_size))
            z += self.biases[j]

            # 활성화 함수 적용
            if self.activation == 'relu':
                z = relu(z)
            elif self.activation == 'sigmoid':
                z = sigmoid(z)
            # softmax는 전체 출력에 대해 적용해야 하므로 나중에 처리

            outputs.append(z)

        if self.activation == 'softmax':
            outputs = softmax(outputs)

        return outputs

    def param_count(self):
        """파라미터 수 = input_size * units + units(bias)"""
        return self.input_size * self.units + self.units

    def __repr__(self):
        return (f"ToyDense('{self.name}', input={self.input_size}, "
                f"units={self.units}, activation={self.activation}, "
                f"params={self.param_count()})")

# Dense 레이어 동작 시연
layer1 = ToyDense(3, 4, activation='relu', name='dense_1')
layer2 = ToyDense(4, 2, activation='sigmoid', name='dense_2')

inputs = [0.5, 0.8, 0.1]
hidden = layer1.forward(inputs)
output = layer2.forward(hidden)

print(f"\n■ Dense 레이어 순전파 시연:")
print(f"  입력:       {inputs}")
print(f"  은닉층 출력: {[f'{h:.4f}' for h in hidden]}")
print(f"  최종 출력:   {[f'{o:.4f}' for o in output]}")
print(f"\n  {layer1}")
print(f"  {layer2}")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Sequential 모델 토이 구현
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("3. Sequential 모델 구현")
print("=" * 70)

class ToySequential:
    """tf.keras.Sequential의 토이 구현"""
    def __init__(self, layers=None):
        self.layers = layers or []
        self.optimizer = None
        self.loss_fn = None
        self.history = {'loss': [], 'val_loss': []}

    def add(self, layer):
        self.layers.append(layer)

    def predict(self, x):
        """순전파만 수행"""
        current = x
        for layer in self.layers:
            current = layer.forward(current)
        return current

    def compile(self, optimizer='sgd', loss='mse', lr=0.01):
        """학습 설정"""
        self.optimizer = optimizer
        self.loss_fn = loss
        self.lr = lr
        print(f"\n  모델 컴파일 완료:")
        print(f"    optimizer = {optimizer}")
        print(f"    loss = {loss}")
        print(f"    learning_rate = {lr}")

    def _compute_loss(self, predicted, actual):
        """손실 계산"""
        if self.loss_fn == 'mse':
            return sum((p - a) ** 2 for p, a in zip(predicted, actual)) / len(actual)
        elif self.loss_fn == 'binary_crossentropy':
            eps = 1e-7
            return -sum(
                a * math.log(p + eps) + (1 - a) * math.log(1 - p + eps)
                for p, a in zip(predicted, actual)
            ) / len(actual)
        return 0.0

    def fit(self, X, Y, epochs=10, batch_size=None, validation_split=0.0, verbose=True):
        """학습 수행 (수치 미분 기반 간소화 버전)"""
        # 검증 데이터 분리
        n = len(X)
        val_n = int(n * validation_split)
        X_train, Y_train = X[:n - val_n], Y[:n - val_n]
        X_val, Y_val = X[n - val_n:], Y[n - val_n:] if val_n > 0 else ([], [])

        print(f"\n  학습 시작: {len(X_train)} 샘플, 검증: {len(X_val)} 샘플")
        print(f"  {'Epoch':>6}  {'Train Loss':>12}  {'Val Loss':>12}")
        print(f"  {'-'*6}  {'-'*12}  {'-'*12}")

        for epoch in range(epochs):
            # 각 샘플에 대해 예측 및 손실 계산
            total_loss = 0
            for x, y in zip(X_train, Y_train):
                pred = self.predict(x)
                actual = y if isinstance(y, list) else [y]
                total_loss += self._compute_loss(pred, actual)

                # 수치 미분으로 가중치 업데이트 (간소화)
                self._update_weights_numerical(x, actual)

            train_loss = total_loss / len(X_train)
            self.history['loss'].append(train_loss)

            # 검증 손실
            val_loss = 0
            if X_val:
                for x, y in zip(X_val, Y_val):
                    pred = self.predict(x)
                    actual = y if isinstance(y, list) else [y]
                    val_loss += self._compute_loss(pred, actual)
                val_loss /= len(X_val)
                self.history['val_loss'].append(val_loss)

            if verbose and (epoch % max(1, epochs // 10) == 0 or epoch == epochs - 1):
                val_str = f"{val_loss:.6f}" if X_val else "N/A"
                print(f"  {epoch+1:6d}  {train_loss:12.6f}  {val_str:>12}")

        return self.history

    def _update_weights_numerical(self, x, y_true, h=1e-5):
        """수치 미분으로 가중치 업데이트"""
        for layer in self.layers:
            for i in range(layer.input_size):
                for j in range(layer.units):
                    # 원래 손실
                    original = layer.weights[i][j]
                    pred = self.predict(x)
                    loss1 = self._compute_loss(pred, y_true)

                    # w + h 일 때 손실
                    layer.weights[i][j] = original + h
                    pred = self.predict(x)
                    loss2 = self._compute_loss(pred, y_true)

                    # 기울기 계산 및 업데이트
                    grad = (loss2 - loss1) / h
                    layer.weights[i][j] = original - self.lr * grad

            # 편향 업데이트
            for j in range(layer.units):
                original = layer.biases[j]
                pred = self.predict(x)
                loss1 = self._compute_loss(pred, y_true)

                layer.biases[j] = original + h
                pred = self.predict(x)
                loss2 = self._compute_loss(pred, y_true)

                grad = (loss2 - loss1) / h
                layer.biases[j] = original - self.lr * grad

    def evaluate(self, X, Y):
        """평가"""
        total_loss = 0
        correct = 0
        for x, y in zip(X, Y):
            pred = self.predict(x)
            actual = y if isinstance(y, list) else [y]
            total_loss += self._compute_loss(pred, actual)
            # 정확도 (이진 분류)
            if len(pred) == 1:
                predicted_class = 1 if pred[0] > 0.5 else 0
                if predicted_class == int(actual[0]):
                    correct += 1
        avg_loss = total_loss / len(X)
        accuracy = correct / len(X)
        return avg_loss, accuracy

    def summary(self):
        """모델 요약 (model.summary() 대응)"""
        print(f"\n  {'='*55}")
        print(f"  Model Summary")
        print(f"  {'='*55}")
        print(f"  {'Layer':20s}  {'Output Shape':15s}  {'Params':>8}")
        print(f"  {'-'*20}  {'-'*15}  {'-'*8}")
        total_params = 0
        for layer in self.layers:
            params = layer.param_count()
            total_params += params
            print(f"  {layer.name:20s}  (None, {layer.units:3d})       {params:8d}")
        print(f"  {'='*55}")
        print(f"  Total params: {total_params:,}")
        print(f"  Trainable params: {total_params:,}")
        print(f"  Non-trainable params: 0")
        print(f"  {'='*55}")

# 실제 코드: model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
# 실제 코드: history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2)
# 실제 코드: loss, accuracy = model.evaluate(X_test, y_test)
# 실제 코드: predictions = model.predict(X_new)
# 실제 코드: model.summary()


# ═══════════════════════════════════════════════════════════════════════════════
# 4. model.compile() - 학습 설정
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("4. model.compile() - 학습 전 설정")
print("=" * 70)

print("""
■ compile()의 3가지 핵심 인자:

  1. optimizer (최적화기): 가중치를 어떻게 업데이트할지
     - 'sgd'   : 기본 경사하강법 (느리지만 안정적)
     - 'adam'   : 가장 많이 사용 (빠르고 효과적)
     - 'rmsprop': RNN에서 자주 사용

  2. loss (손실 함수): 예측이 얼마나 틀렸는지 측정
     - 'mse'                    : 회귀 문제
     - 'binary_crossentropy'    : 이진 분류 (0 or 1)
     - 'categorical_crossentropy': 다중 분류 (원핫 인코딩)
     - 'sparse_categorical_crossentropy': 다중 분류 (정수 라벨)

  3. metrics (평가 지표): 학습 중 모니터링할 값
     - 'accuracy'  : 정확도
     - 'mae'       : 평균 절대 오차
     - 'precision' : 정밀도
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 5. model.fit() - 학습 실행
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("5. model.fit() - 학습 실행")
print("=" * 70)

print("""
■ fit()의 핵심 인자:

  model.fit(X_train, y_train,
            epochs=50,           # 전체 데이터를 50번 반복 학습
            batch_size=32,       # 32개씩 묶어서 학습
            validation_split=0.2) # 20%는 검증용으로 분리

  epochs (에포크):
    비유: 교과서를 처음부터 끝까지 읽는 횟수
    - 1 epoch = 전체 데이터를 1번 학습
    - 너무 적으면: 학습 부족 (과소적합)
    - 너무 많으면: 외워버림 (과적합)

  batch_size (배치 크기):
    비유: 한 번에 채점하는 시험지 수
    - 전체 1000개 데이터, batch=32 → 1 epoch에 32번 업데이트
    - 작을수록: 자주 업데이트, 노이즈 많음
    - 클수록: 안정적이지만, GPU 메모리 필요

  validation_split:
    학습 데이터 중 일부를 검증용으로 분리
    → 과적합 여부를 모니터링할 수 있음
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 6. model.summary() - 파라미터 수 계산법
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("6. 파라미터 수 계산법")
print("=" * 70)

print("""
■ Dense 레이어의 파라미터 수:
  params = input_size * units + units(bias)

  예시: Dense(64, input_shape=(784,))
  params = 784 * 64 + 64 = 50,240

  ┌─────────────────────────────────────────────┐
  │ Layer              Output Shape    Params   │
  ├─────────────────────────────────────────────┤
  │ Dense(64, relu)    (None, 64)      50,240   │  ← 784*64 + 64
  │ Dense(32, relu)    (None, 32)       2,080   │  ← 64*32 + 32
  │ Dense(10, softmax) (None, 10)         330   │  ← 32*10 + 10
  ├─────────────────────────────────────────────┤
  │ Total params:                      52,650   │
  └─────────────────────────────────────────────┘

  None = 배치 크기 (학습 시 결정됨)
""")

# 파라미터 수 직접 계산
layers_config = [
    ("Input", 784, "-"),
    ("Dense(64, relu)", 64, f"{784*64 + 64:,}"),
    ("Dense(32, relu)", 32, f"{64*32 + 32:,}"),
    ("Dense(10, softmax)", 10, f"{32*10 + 10:,}")
]

total = 784*64+64 + 64*32+32 + 32*10+10
print(f"■ 파라미터 수 계산 예시:")
for name, units, params in layers_config:
    print(f"  {name:25s}  units={units:4d}  params={params}")
print(f"  {'총 파라미터':25s}  {total:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# 7. [실습] XOR 문제 해결하기
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("7. [실습] XOR 문제 해결하기")
print("=" * 70)

# XOR 문제: 단순 퍼셉트론(1층)으로는 풀 수 없는 유명한 문제!
# 은닉층을 추가하면 해결 가능 → 딥러닝의 힘!

print("""
■ XOR 진리표:
  x0  x1  │  y
  ────────┼────
  0   0   │  0
  0   1   │  1
  1   0   │  1
  1   1   │  0

■ 왜 어려운가?
  - 직선 하나로는 0과 1을 구분할 수 없음!
  - 은닉층(hidden layer)이 필요한 이유:
    비선형 결정 경계를 만들 수 있기 때문
""")

# XOR 데이터
X_xor = [[0, 0], [0, 1], [1, 0], [1, 1]]
Y_xor = [[0], [1], [1], [0]]

# 모델 구성: 2 → 4 → 1
print("■ 모델 구성: Input(2) → Dense(4, relu) → Dense(1, sigmoid)")
model = ToySequential([
    ToyDense(2, 4, activation='relu', name='hidden'),
    ToyDense(4, 1, activation='sigmoid', name='output')
])

model.summary()
model.compile(optimizer='sgd', loss='binary_crossentropy', lr=0.5)

# 학습
print("\n■ 학습 진행:")
model.fit(X_xor, Y_xor, epochs=200, verbose=True)

# 평가
print("\n■ 학습 결과:")
print(f"  {'Input':>10}  {'Expected':>8}  {'Predicted':>10}  {'Class':>6}")
for x, y in zip(X_xor, Y_xor):
    pred = model.predict(x)
    cls = 1 if pred[0] > 0.5 else 0
    print(f"  {str(x):>10}  {y[0]:>8}  {pred[0]:>10.4f}  {cls:>6}")

loss, acc = model.evaluate(X_xor, Y_xor)
print(f"\n  최종 손실: {loss:.6f}")
print(f"  최종 정확도: {acc:.2%}")

# 실제 코드: TensorFlow로 XOR 해결
# 실제 코드: import tensorflow as tf
# 실제 코드: import numpy as np
# 실제 코드:
# 실제 코드: X = np.array([[0,0],[0,1],[1,0],[1,1]], dtype=np.float32)
# 실제 코드: y = np.array([[0],[1],[1],[0]], dtype=np.float32)
# 실제 코드:
# 실제 코드: model = tf.keras.Sequential([
# 실제 코드:     tf.keras.layers.Dense(8, activation='relu', input_shape=(2,)),
# 실제 코드:     tf.keras.layers.Dense(1, activation='sigmoid')
# 실제 코드: ])
# 실제 코드:
# 실제 코드: model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
# 실제 코드: model.fit(X, y, epochs=1000, verbose=0)
# 실제 코드: print(model.predict(X))
# 실제 코드: # 출력: [[0.01], [0.98], [0.99], [0.02]] ← XOR 해결!


# ═══════════════════════════════════════════════════════════════════════════════
# 8. model.evaluate()와 model.predict()
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("8. evaluate()와 predict()")
print("=" * 70)

print("""
■ model.evaluate(X_test, y_test):
  - 테스트 데이터에 대한 손실과 메트릭을 계산
  - 학습에 사용하지 않은 새로운 데이터로 평가해야 의미 있음
  - 반환: [loss, metric1, metric2, ...]

■ model.predict(X_new):
  - 새로운 데이터에 대한 예측값 생성
  - 학습(가중치 업데이트) 없이 순전파만 수행
  - 반환: 예측값 배열

■ 사용 시나리오:
  1. 학습 (fit) → 70~80% 데이터
  2. 평가 (evaluate) → 나머지 20~30% 데이터
  3. 예측 (predict) → 실제 새 데이터
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 9. 간단한 회귀 문제
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("9. [추가 실습] 간단한 회귀 문제")
print("=" * 70)

# y = 3*x1 + 2*x2 - 1 을 학습
print("\n■ 목표: y = 3*x1 + 2*x2 - 1 학습하기")

random.seed(42)
n_samples = 50
X_reg = [[random.uniform(-1, 1), random.uniform(-1, 1)] for _ in range(n_samples)]
Y_reg = [[3 * x[0] + 2 * x[1] - 1 + random.gauss(0, 0.1)] for x in X_reg]

model_reg = ToySequential([
    ToyDense(2, 4, activation='relu', name='hidden'),
    ToyDense(4, 1, activation=None, name='output')  # 회귀: 활성화 없음
])

model_reg.compile(optimizer='sgd', loss='mse', lr=0.01)
model_reg.summary()

print("\n■ 학습 진행:")
model_reg.fit(X_reg, Y_reg, epochs=100, verbose=True)

# 예측 테스트
print("\n■ 예측 결과:")
test_inputs = [[0.5, 0.5], [-0.5, 0.3], [1.0, -1.0]]
for x in test_inputs:
    expected = 3 * x[0] + 2 * x[1] - 1
    predicted = model_reg.predict(x)
    print(f"  입력: {x}, 기대값: {expected:.2f}, 예측값: {predicted[0]:.2f}")

# 실제 코드: 회귀 모델
# 실제 코드: model = tf.keras.Sequential([
# 실제 코드:     tf.keras.layers.Dense(16, activation='relu', input_shape=(2,)),
# 실제 코드:     tf.keras.layers.Dense(1)  # 활성화 없음 = 선형 출력
# 실제 코드: ])
# 실제 코드: model.compile(optimizer='adam', loss='mse', metrics=['mae'])
# 실제 코드: model.fit(X_train, y_train, epochs=100, validation_split=0.2)


# ═══════════════════════════════════════════════════════════════════════════════
# 10. 학습 과정 시각화 개념
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("10. 학습 과정 이해하기")
print("=" * 70)

def ascii_plot(values, title, width=50, height=10):
    """간단한 ASCII 그래프"""
    if not values:
        return
    min_v = min(values)
    max_v = max(values)
    range_v = max_v - min_v if max_v != min_v else 1.0

    print(f"\n  {title}")
    print(f"  {'─' * (width + 6)}")
    for row in range(height, -1, -1):
        threshold = min_v + (range_v * row / height)
        line = ""
        step = max(1, len(values) // width)
        for i in range(0, min(len(values), width * step), step):
            if values[i] >= threshold:
                line += "█"
            else:
                line += " "
        label = f"{threshold:7.3f}" if row % 3 == 0 else "       "
        print(f"  {label} │{line}")
    print(f"  {'':7s} └{'─' * width}")
    print(f"  {'':8s} Epoch 1{' ' * (width - 14)}Epoch {len(values)}")

# 학습 손실 시뮬레이션 데이터
simulated_loss = [2.0]
for i in range(99):
    new_loss = simulated_loss[-1] * 0.95 + random.gauss(0, 0.02)
    simulated_loss.append(max(0.01, new_loss))

ascii_plot(simulated_loss, "손실(Loss) 변화 추이 - 이상적인 학습")

print("""
■ 학습 곡선 해석:
  1. 정상 학습: 손실이 점점 감소 → 좋은 신호!
  2. 과적합:   학습 손실 ↓, 검증 손실 ↑ → 조기 종료 필요
  3. 과소적합: 손실이 높은 상태에서 정체 → 모델 복잡도 증가 필요
  4. 발산:    손실이 증가 → 학습률 낮추기
""")

# 실제 코드: 학습 곡선 시각화
# 실제 코드: import matplotlib.pyplot as plt
# 실제 코드:
# 실제 코드: history = model.fit(X, y, epochs=100, validation_split=0.2)
# 실제 코드: plt.plot(history.history['loss'], label='Train Loss')
# 실제 코드: plt.plot(history.history['val_loss'], label='Val Loss')
# 실제 코드: plt.xlabel('Epoch')
# 실제 코드: plt.ylabel('Loss')
# 실제 코드: plt.legend()
# 실제 코드: plt.show()


print("\n" + "=" * 70)
print("요약: Sequential 모델 학습 완료!")
print("=" * 70)
print("""
  1. Sequential: 레이어를 순서대로 쌓는 가장 간단한 방식
  2. Dense: y = activation(Wx + b), 완전 연결 레이어
  3. compile(): optimizer, loss, metrics 설정
  4. fit(): epochs, batch_size, validation_split로 학습
  5. evaluate(): 테스트 데이터 평가
  6. predict(): 새 데이터 예측
  7. summary(): 모델 구조와 파라미터 수 확인
  8. XOR 문제: 은닉층이 있어야 비선형 문제 해결 가능!

  다음 단계 → 03_layers_activations.py (다양한 레이어와 활성화 함수!)
""")
