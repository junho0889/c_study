# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   TensorFlow/Keras 학습 01단계: 텐서(Tensor) 기초
#   ─ 텐서 개념, 연산, 형변환, 자동 미분, 경사하강법 ─
#   ■ 실행 방법: python 01_tensor_basics.py (개념 학습용 코드, TF 없이 실행 가능)
#   ■ TensorFlow 설치: pip install tensorflow
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import random

# ═══════════════════════════════════════════════════════════════════════════════
# 1. 텐서란 무엇인가?
# ═══════════════════════════════════════════════════════════════════════════════
# 텐서(Tensor)는 다차원 배열의 일반화입니다.
# 비유: 텐서는 "데이터를 담는 그릇"입니다.
#   - 점 하나 = 스칼라 (0차원)      → 온도: 36.5
#   - 줄 하나 = 벡터 (1차원)        → 주가: [100, 102, 98, 105]
#   - 표 하나 = 행렬 (2차원)        → 엑셀 시트
#   - 상자    = 3D 텐서             → 컬러 이미지 (높이 x 너비 x 채널)
#   - 상자들  = 4D 텐서             → 이미지 배치 (배치 x 높이 x 너비 x 채널)

print("=" * 70)
print("1. 텐서의 차원(Rank) 이해하기")
print("=" * 70)

# --- 스칼라 (0D 텐서) ---
# 단일 숫자. 차원(rank)이 0입니다.
scalar = 42.0
print(f"\n■ 스칼라 (0D 텐서): {scalar}")
print(f"  - 차원(rank): 0")
print(f"  - 형태(shape): ()  ← 빈 튜플")
print(f"  - 예시: 온도, 확률값, 손실(loss)값")

# 실제 코드: tf.constant(42.0)  → shape=(), dtype=float32
# 실제 코드: scalar.ndim        → 0

# --- 벡터 (1D 텐서) ---
# 숫자들의 1차원 나열
vector = [1.0, 2.0, 3.0, 4.0]
print(f"\n■ 벡터 (1D 텐서): {vector}")
print(f"  - 차원(rank): 1")
print(f"  - 형태(shape): ({len(vector)},)")
print(f"  - 예시: 단어 임베딩, 특성(feature) 벡터")

# 실제 코드: tf.constant([1.0, 2.0, 3.0, 4.0])  → shape=(4,)

# --- 행렬 (2D 텐서) ---
# 숫자들의 2차원 배열
matrix = [
    [1, 2, 3],
    [4, 5, 6]
]
print(f"\n■ 행렬 (2D 텐서):")
for row in matrix:
    print(f"  {row}")
rows = len(matrix)
cols = len(matrix[0])
print(f"  - 차원(rank): 2")
print(f"  - 형태(shape): ({rows}, {cols})")
print(f"  - 예시: 흑백 이미지, 데이터 테이블(행=샘플, 열=특성)")

# 실제 코드: tf.constant([[1, 2, 3], [4, 5, 6]])  → shape=(2, 3)

# --- 3D 텐서 ---
# 행렬들의 스택
tensor_3d = [
    [[1, 2], [3, 4]],
    [[5, 6], [7, 8]],
    [[9, 10], [11, 12]]
]
print(f"\n■ 3D 텐서:")
print(f"  - 차원(rank): 3")
d1 = len(tensor_3d)
d2 = len(tensor_3d[0])
d3 = len(tensor_3d[0][0])
print(f"  - 형태(shape): ({d1}, {d2}, {d3})")
print(f"  - 예시: 컬러 이미지 (높이 x 너비 x RGB채널)")
print(f"  - 예시: 시계열 데이터 (시간 x 특성 x 채널)")

# 실제 코드: tf.constant([[[1,2],[3,4]], [[5,6],[7,8]], [[9,10],[11,12]]])


# ═══════════════════════════════════════════════════════════════════════════════
# 2. tf.constant vs tf.Variable
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("2. 상수(Constant) vs 변수(Variable)")
print("=" * 70)

# tf.constant → 값이 변하지 않는 텐서 (입력 데이터, 하이퍼파라미터)
# tf.Variable → 값이 변할 수 있는 텐서 (가중치, 편향 등 학습 파라미터)

# 비유: constant = 칠판에 새긴 글씨 (지울 수 없음)
#       Variable = 화이트보드 글씨 (지우고 다시 쓸 수 있음)

class ToyConstant:
    """tf.constant의 토이 구현"""
    def __init__(self, value, dtype="float32"):
        if isinstance(value, (int, float)):
            self.value = value
            self.shape = ()
        elif isinstance(value, list):
            self.value = value
            self.shape = self._compute_shape(value)
        self.dtype = dtype
        self._trainable = False  # 상수는 학습 불가

    def _compute_shape(self, v):
        if isinstance(v, list):
            return (len(v),) + self._compute_shape(v[0]) if v else (0,)
        return ()

    def __repr__(self):
        return f"ToyConstant(value={self.value}, shape={self.shape}, dtype={self.dtype})"

class ToyVariable:
    """tf.Variable의 토이 구현"""
    def __init__(self, initial_value, trainable=True, name="Variable"):
        self.value = initial_value
        self.trainable = trainable
        self.name = name

    def assign(self, new_value):
        """변수 값 업데이트 (tf.Variable.assign 대응)"""
        self.value = new_value
        return self

    def assign_sub(self, delta):
        """변수에서 값 빼기 (경사하강법에서 사용)"""
        self.value = self.value - delta
        return self

    def __repr__(self):
        return f"ToyVariable(name='{self.name}', value={self.value}, trainable={self.trainable})"

const_a = ToyConstant(3.14)
var_w = ToyVariable(0.5, name="weight")
print(f"\n■ 상수: {const_a}")
print(f"■ 변수: {var_w}")

# 변수 값 업데이트
var_w.assign(0.7)
print(f"■ 변수 업데이트 후: {var_w}")

var_w.assign_sub(0.1)  # 0.7 - 0.1 = 0.6
print(f"■ assign_sub(0.1) 후: value={var_w.value:.1f}")

# 실제 코드: a = tf.constant(3.14)
# 실제 코드: w = tf.Variable(0.5, name="weight")
# 실제 코드: w.assign(0.7)
# 실제 코드: w.assign_sub(0.1)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. 텐서 연산 - 사칙연산, 행렬곱, 브로드캐스팅
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("3. 텐서 연산")
print("=" * 70)

def element_wise_op(a, b, op):
    """원소별(element-wise) 연산"""
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return op(a, b)
    return [element_wise_op(ai, bi, op) for ai, bi in zip(a, b)]

def tensor_add(a, b):
    return element_wise_op(a, b, lambda x, y: x + y)

def tensor_sub(a, b):
    return element_wise_op(a, b, lambda x, y: x - y)

def tensor_mul(a, b):
    return element_wise_op(a, b, lambda x, y: x * y)

def tensor_div(a, b):
    return element_wise_op(a, b, lambda x, y: x / y)

a = [1.0, 2.0, 3.0]
b = [4.0, 5.0, 6.0]
print(f"\n■ 원소별 연산 (Element-wise Operations)")
print(f"  a = {a}")
print(f"  b = {b}")
print(f"  a + b = {tensor_add(a, b)}")
print(f"  a - b = {tensor_sub(a, b)}")
print(f"  a * b = {tensor_mul(a, b)}")
print(f"  a / b = {tensor_div(a, b)}")

# 실제 코드: tf.add(a, b) 또는 a + b
# 실제 코드: tf.subtract(a, b) 또는 a - b
# 실제 코드: tf.multiply(a, b) 또는 a * b
# 실제 코드: tf.divide(a, b) 또는 a / b

# --- 행렬곱 (Matrix Multiplication) ---
print(f"\n■ 행렬곱 (Matrix Multiplication)")

def matmul(A, B):
    """행렬곱: (m x n) @ (n x p) → (m x p)"""
    m = len(A)
    n = len(A[0])
    p = len(B[0])
    result = [[0.0] * p for _ in range(m)]
    for i in range(m):
        for j in range(p):
            for k in range(n):
                result[i][j] += A[i][k] * B[k][j]
    return result

A = [[1, 2], [3, 4]]       # 2x2
B = [[5, 6], [7, 8]]       # 2x2
C = matmul(A, B)            # 2x2
print(f"  A = {A}")
print(f"  B = {B}")
print(f"  A @ B = {C}")
print(f"  검증: [1*5+2*7, 1*6+2*8] = [{1*5+2*7}, {1*6+2*8}]")

# 실제 코드: tf.matmul(A, B) 또는 A @ B

# --- 브로드캐스팅 ---
print(f"\n■ 브로드캐스팅 (Broadcasting)")
print("  작은 텐서를 큰 텐서에 맞게 자동 확장")

def broadcast_add_scalar(matrix, scalar):
    """스칼라를 행렬에 브로드캐스팅하여 더하기"""
    return [[val + scalar for val in row] for row in matrix]

def broadcast_add_vector(matrix, vector):
    """벡터를 행렬의 각 행에 브로드캐스팅하여 더하기"""
    return [[matrix[i][j] + vector[j] for j in range(len(vector))] for i in range(len(matrix))]

mat = [[1, 2, 3], [4, 5, 6]]
print(f"  행렬: {mat}")
print(f"  + 스칼라 10: {broadcast_add_scalar(mat, 10)}")
print(f"  + 벡터 [100, 200, 300]: {broadcast_add_vector(mat, [100, 200, 300])}")

# 실제 코드: tf.constant([[1,2,3],[4,5,6]]) + 10  → 자동 브로드캐스팅
# 실제 코드: tf.constant([[1,2,3],[4,5,6]]) + tf.constant([100,200,300])


# ═══════════════════════════════════════════════════════════════════════════════
# 4. 형변환 - tf.cast(), dtype
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("4. 형변환 (Type Casting)")
print("=" * 70)

# TensorFlow에서 dtype(데이터 타입)은 매우 중요합니다.
# 연산 시 양쪽 텐서의 dtype이 일치해야 합니다.

# 주요 dtype:
# - tf.float32  : 기본 실수형 (가장 많이 사용)
# - tf.float64  : 높은 정밀도 실수
# - tf.int32    : 정수형
# - tf.bool     : 불리언
# - tf.string   : 문자열

print("\n■ 주요 데이터 타입과 메모리 사용량:")
dtypes = {
    "float16 (반정밀도)": 2,
    "float32 (단정밀도)": 4,
    "float64 (배정밀도)": 8,
    "int8": 1,
    "int32": 4,
    "int64": 8,
}
for name, size in dtypes.items():
    print(f"  {name:25s} → {size} bytes per element")

def toy_cast(value, target_type):
    """형변환 시뮬레이션"""
    if isinstance(value, list):
        return [toy_cast(v, target_type) for v in value]
    return target_type(value)

float_vals = [1.7, 2.3, 3.9]
int_vals = toy_cast(float_vals, int)
bool_vals = toy_cast([0, 1, 0, 2, -1], bool)
print(f"\n■ float → int: {float_vals} → {int_vals}  (소수점 버림)")
print(f"■ int → bool: [0, 1, 0, 2, -1] → {bool_vals}  (0만 False)")

# 실제 코드: x = tf.constant([1.7, 2.3, 3.9])
# 실제 코드: tf.cast(x, tf.int32)   → [1, 2, 3]
# 실제 코드: tf.cast(x, tf.float64) → [1.7, 2.3, 3.9] (float64)

# 흔한 실수: int 텐서끼리 나누면 결과도 int!
print(f"\n■ 주의: 정수 나눗셈")
print(f"  Python: 7 / 2 = {7/2}  (자동 float 변환)")
print(f"  TF int: tf.constant(7) / tf.constant(2) → 먼저 cast 필요!")
# 실제 코드: tf.cast(tf.constant(7), tf.float32) / tf.cast(tf.constant(2), tf.float32)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. GPU/CPU 배치 - tf.device() 개념
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("5. GPU/CPU 배치 (Device Placement)")
print("=" * 70)

# TensorFlow는 자동으로 GPU를 감지하고 연산을 배치합니다.
# 비유: CPU = 소수의 똑똑한 일꾼 (직렬 처리에 강함)
#       GPU = 수천 명의 단순 일꾼 (병렬 처리에 강함)

print("""
■ CPU vs GPU 비유:
  ┌─────────────────────────────────────────────────┐
  │  CPU: 교수님 1명이 복잡한 수학 문제 풀기        │
  │       → 순차적이지만 복잡한 로직 처리 가능      │
  │                                                  │
  │  GPU: 학생 1000명이 각자 간단한 곱셈 하기       │
  │       → 동시에 수천 개의 행렬 연산 가능!        │
  └─────────────────────────────────────────────────┘
""")

# 실제 코드: 사용 가능한 디바이스 확인
# 실제 코드: print(tf.config.list_physical_devices('GPU'))
# 실제 코드: print(tf.config.list_physical_devices('CPU'))

# 실제 코드: 특정 디바이스에서 연산 실행
# 실제 코드: with tf.device('/GPU:0'):
# 실제 코드:     a = tf.constant([[1, 2], [3, 4]])
# 실제 코드:     b = tf.constant([[5, 6], [7, 8]])
# 실제 코드:     c = tf.matmul(a, b)  # GPU에서 실행

# 실제 코드: GPU 메모리 제한 (OOM 방지)
# 실제 코드: gpus = tf.config.experimental.list_physical_devices('GPU')
# 실제 코드: if gpus:
# 실제 코드:     tf.config.experimental.set_memory_growth(gpus[0], True)

class ToyDevice:
    """디바이스 배치 시뮬레이션"""
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        print(f"  [디바이스 {self.name}에서 연산 시작]")
        return self

    def __exit__(self, *args):
        print(f"  [디바이스 {self.name} 연산 완료]")

with ToyDevice("/CPU:0"):
    result = sum([i * i for i in range(10)])
    print(f"  CPU 연산 결과: {result}")

with ToyDevice("/GPU:0"):
    # GPU에서는 큰 행렬 연산이 빠름
    big_matrix = [[random.random() for _ in range(5)] for _ in range(5)]
    print(f"  GPU 행렬 연산 (5x5 행렬 생성됨)")


# ═══════════════════════════════════════════════════════════════════════════════
# 6. tf.GradientTape - 자동 미분의 마법
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("6. 자동 미분 (Automatic Differentiation)")
print("=" * 70)

# GradientTape = "연산을 녹화하는 테이프"
# 비유: VCR처럼 순방향 연산을 '녹화'하고,
#       '되감기'하면서 각 단계의 기울기(미분)를 계산합니다.

# 수학적 배경:
# f(x) = x^2 → f'(x) = 2x
# x=3일 때, f(3) = 9, f'(3) = 6

print("""
■ GradientTape 개념:
  ┌──────────────────────────────────────┐
  │  1. 테이프 녹화 시작                  │
  │  2. 순방향 연산 수행 (y = x^2 + 3x) │
  │  3. 테이프 되감기 (역전파)            │
  │  4. 기울기(gradient) 추출             │
  │     dy/dx = 2x + 3                   │
  └──────────────────────────────────────┘
""")

def numerical_gradient(f, x, h=1e-5):
    """수치 미분: f'(x) ≈ (f(x+h) - f(x-h)) / 2h"""
    return (f(x + h) - f(x - h)) / (2 * h)

def analytical_gradient_x_squared(x):
    """해석적 미분: d/dx(x^2) = 2x"""
    return 2 * x

# 예제 1: f(x) = x^2
f1 = lambda x: x ** 2
x_val = 3.0
numerical = numerical_gradient(f1, x_val)
analytical = analytical_gradient_x_squared(x_val)
print(f"■ f(x) = x^2, x = {x_val}")
print(f"  수치 미분:  f'({x_val}) = {numerical:.6f}")
print(f"  해석적 미분: f'({x_val}) = {analytical:.6f}")

# 예제 2: f(x) = x^3 + 2x^2 - 5x + 1
f2 = lambda x: x**3 + 2*x**2 - 5*x + 1
# f'(x) = 3x^2 + 4x - 5
f2_grad = lambda x: 3*x**2 + 4*x - 5
x_val = 2.0
print(f"\n■ f(x) = x^3 + 2x^2 - 5x + 1, x = {x_val}")
print(f"  수치 미분:  f'({x_val}) = {numerical_gradient(f2, x_val):.6f}")
print(f"  해석적 미분: f'({x_val}) = {f2_grad(x_val):.6f}")

# 실제 코드: GradientTape 사용
# 실제 코드: x = tf.Variable(3.0)
# 실제 코드: with tf.GradientTape() as tape:
# 실제 코드:     y = x ** 2
# 실제 코드: grad = tape.gradient(y, x)
# 실제 코드: print(grad)  # tf.Tensor(6.0, shape=(), dtype=float32)

# GradientTape으로 여러 변수에 대한 기울기
print(f"\n■ 다변수 함수의 기울기")
def multi_var_gradient():
    """f(x, y) = x^2 * y + y^3"""
    x, y = 2.0, 3.0
    # ∂f/∂x = 2xy = 2*2*3 = 12
    # ∂f/∂y = x^2 + 3y^2 = 4 + 27 = 31
    f = lambda x, y: x**2 * y + y**3
    dx = numerical_gradient(lambda x_: f(x_, y), x)
    dy = numerical_gradient(lambda y_: f(x, y_), y)
    print(f"  f(x,y) = x^2*y + y^3")
    print(f"  x={x}, y={y}")
    print(f"  ∂f/∂x = {dx:.4f} (이론값: {2*x*y:.1f})")
    print(f"  ∂f/∂y = {dy:.4f} (이론값: {x**2 + 3*y**2:.1f})")

multi_var_gradient()

# 실제 코드: x = tf.Variable(2.0)
# 실제 코드: y = tf.Variable(3.0)
# 실제 코드: with tf.GradientTape() as tape:
# 실제 코드:     f = x**2 * y + y**3
# 실제 코드: grads = tape.gradient(f, [x, y])
# 실제 코드: print(grads)  # [12.0, 31.0]


# ═══════════════════════════════════════════════════════════════════════════════
# 7. 실습: 경사하강법 직접 구현
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("7. [실습] 경사하강법으로 함수 최솟값 찾기")
print("=" * 70)

# 문제: f(x) = (x - 3)^2 + 2 의 최솟값을 찾아라!
# 답: x = 3일 때 f(x) = 2가 최소
# 경사하강법: x_new = x_old - learning_rate * f'(x_old)

print("""
■ 경사하강법 비유:
  눈을 가리고 산에서 내려가기!
  1. 현재 위치에서 발밑의 경사(기울기)를 느낀다
  2. 경사가 내려가는 방향으로 한 걸음 이동
  3. 반복하면 계곡(최저점)에 도달!

  학습률(learning_rate) = 걸음 크기
  - 너무 크면: 계곡을 넘어감 (발산)
  - 너무 작으면: 너무 오래 걸림
""")

def gradient_descent_demo():
    """경사하강법으로 f(x) = (x-3)^2 + 2 의 최솟값 찾기"""
    f = lambda x: (x - 3) ** 2 + 2
    f_grad = lambda x: 2 * (x - 3)  # f'(x) = 2(x-3)

    x = 10.0           # 시작점 (임의로 설정)
    lr = 0.1            # 학습률
    history = []

    print(f"\n  초기값: x = {x}, f(x) = {f(x)}")
    print(f"  학습률: {lr}")
    print(f"  목표: x = 3, f(x) = 2\n")
    print(f"  {'Step':>4}  {'x':>10}  {'f(x)':>10}  {'gradient':>10}")
    print(f"  {'-'*4}  {'-'*10}  {'-'*10}  {'-'*10}")

    for step in range(20):
        grad = f_grad(x)
        fx = f(x)
        history.append((x, fx))

        if step < 10 or step % 5 == 0:
            print(f"  {step:4d}  {x:10.4f}  {fx:10.4f}  {grad:10.4f}")

        x = x - lr * grad  # 핵심 업데이트 규칙!

    print(f"\n  최종 결과: x = {x:.6f}, f(x) = {f(x):.6f}")
    print(f"  이론적 최솟값: x = 3.000000, f(x) = 2.000000")

gradient_descent_demo()

# 실제 코드: TensorFlow로 경사하강법
# 실제 코드: x = tf.Variable(10.0)
# 실제 코드: optimizer = tf.keras.optimizers.SGD(learning_rate=0.1)
# 실제 코드:
# 실제 코드: for step in range(20):
# 실제 코드:     with tf.GradientTape() as tape:
# 실제 코드:         loss = (x - 3) ** 2 + 2
# 실제 코드:     grad = tape.gradient(loss, [x])
# 실제 코드:     optimizer.apply_gradients(zip(grad, [x]))
# 실제 코드:     print(f"Step {step}: x={x.numpy():.4f}, loss={loss.numpy():.4f}")

# ═══════════════════════════════════════════════════════════════════════════════
# 8. 선형 회귀를 경사하강법으로 풀기
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("8. [실습] 선형 회귀: y = wx + b 학습하기")
print("=" * 70)

def linear_regression_gd():
    """y = 2x + 1 데이터에 대해 w, b를 경사하강법으로 학습"""
    # 데이터 생성 (y = 2x + 1 + noise)
    random.seed(42)
    n_samples = 20
    X = [i * 0.5 for i in range(n_samples)]
    Y = [2 * x + 1 + random.gauss(0, 0.5) for x in X]

    # 학습 파라미터 초기화
    w = 0.0  # 가중치 (목표: 2.0)
    b = 0.0  # 편향 (목표: 1.0)
    lr = 0.002  # 학습률

    print(f"  데이터: y = 2x + 1 (+ 노이즈)")
    print(f"  초기 파라미터: w={w}, b={b}")
    print(f"  학습률: {lr}\n")

    for epoch in range(100):
        # 순방향: 예측
        predictions = [w * x + b for x in X]

        # 손실 계산 (MSE)
        loss = sum((pred - y) ** 2 for pred, y in zip(predictions, Y)) / n_samples

        # 기울기 계산
        dw = sum(2 * (pred - y) * x for pred, y, x in zip(predictions, Y, X)) / n_samples
        db = sum(2 * (pred - y) for pred, y in zip(predictions, Y)) / n_samples

        # 파라미터 업데이트
        w -= lr * dw
        b -= lr * db

        if epoch % 20 == 0 or epoch == 99:
            print(f"  Epoch {epoch:3d}: w={w:.4f}, b={b:.4f}, loss={loss:.4f}")

    print(f"\n  학습 결과: y = {w:.4f}x + {b:.4f}")
    print(f"  정답:     y = 2.0000x + 1.0000")

linear_regression_gd()

# 실제 코드: TensorFlow로 선형 회귀
# 실제 코드: w = tf.Variable(0.0)
# 실제 코드: b = tf.Variable(0.0)
# 실제 코드: optimizer = tf.keras.optimizers.SGD(learning_rate=0.002)
# 실제 코드:
# 실제 코드: for epoch in range(100):
# 실제 코드:     with tf.GradientTape() as tape:
# 실제 코드:         predictions = w * X + b
# 실제 코드:         loss = tf.reduce_mean((predictions - Y) ** 2)
# 실제 코드:     grads = tape.gradient(loss, [w, b])
# 실제 코드:     optimizer.apply_gradients(zip(grads, [w, b]))


# ═══════════════════════════════════════════════════════════════════════════════
# 9. 텐서 인덱싱과 슬라이싱
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("9. 텐서 인덱싱과 슬라이싱")
print("=" * 70)

tensor_2d = [
    [10, 20, 30, 40],
    [50, 60, 70, 80],
    [90, 100, 110, 120]
]

print(f"\n■ 2D 텐서 (3x4):")
for i, row in enumerate(tensor_2d):
    print(f"  행 {i}: {row}")

print(f"\n■ 인덱싱:")
print(f"  tensor[0]    = {tensor_2d[0]}          ← 첫 번째 행")
print(f"  tensor[1][2] = {tensor_2d[1][2]}            ← 2행 3열")
print(f"  tensor[-1]   = {tensor_2d[-1]}  ← 마지막 행")

print(f"\n■ 슬라이싱:")
print(f"  tensor[0:2]   = {tensor_2d[0:2]}  ← 0~1행")
col_1 = [row[1] for row in tensor_2d]
print(f"  tensor[:, 1]  = {col_1}       ← 2번째 열")
sub = [row[1:3] for row in tensor_2d[:2]]
print(f"  tensor[:2, 1:3] = {sub}    ← 부분 행렬")

# 실제 코드: t = tf.constant([[10,20,30,40],[50,60,70,80],[90,100,110,120]])
# 실제 코드: t[0]        → [10, 20, 30, 40]
# 실제 코드: t[1, 2]     → 70
# 실제 코드: t[:2, 1:3]  → [[20, 30], [60, 70]]


# ═══════════════════════════════════════════════════════════════════════════════
# 10. 유용한 텐서 연산 모음
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("10. 유용한 텐서 연산 모음")
print("=" * 70)

data = [3.0, 1.0, 4.0, 1.0, 5.0, 9.0, 2.0, 6.0]

print(f"\n■ 데이터: {data}")
print(f"  tf.reduce_sum  → sum  = {sum(data)}")
print(f"  tf.reduce_mean → mean = {sum(data)/len(data):.4f}")
print(f"  tf.reduce_max  → max  = {max(data)}")
print(f"  tf.reduce_min  → min  = {min(data)}")
print(f"  tf.argmax      → argmax = {data.index(max(data))} (인덱스)")
print(f"  tf.argmin      → argmin = {data.index(min(data))} (인덱스)")

# Reshape
print(f"\n■ 텐서 변형 (Reshape)")
flat = list(range(1, 13))
print(f"  원본 (12,): {flat}")
reshaped_3x4 = [flat[i*4:(i+1)*4] for i in range(3)]
print(f"  reshape(3,4): {reshaped_3x4}")
reshaped_2x6 = [flat[i*6:(i+1)*6] for i in range(2)]
print(f"  reshape(2,6): {reshaped_2x6}")
reshaped_2x2x3 = [[flat[i*6+j*3:i*6+j*3+3] for j in range(2)] for i in range(2)]
print(f"  reshape(2,2,3): {reshaped_2x2x3}")

# 실제 코드: t = tf.constant(list(range(1, 13)))
# 실제 코드: tf.reshape(t, (3, 4))
# 실제 코드: tf.reshape(t, (2, -1))  # -1은 자동 계산
# 실제 코드: tf.reshape(t, (2, 2, 3))

# Concatenate, Stack
print(f"\n■ 텐서 결합")
a = [1, 2, 3]
b = [4, 5, 6]
print(f"  concat([{a}, {b}])  = {a + b}           ← 이어붙이기")
print(f"  stack([{a}, {b}])   = [{a}, {b}]  ← 새 차원 추가")

# 실제 코드: tf.concat([a, b], axis=0)
# 실제 코드: tf.stack([a, b], axis=0)  → shape=(2, 3)

print("\n" + "=" * 70)
print("요약: 텐서 기초 학습 완료!")
print("=" * 70)
print("""
  1. 텐서 = 다차원 배열 (0D~nD)
  2. Constant(상수) vs Variable(변수, 학습 가능)
  3. 원소별 연산, 행렬곱, 브로드캐스팅
  4. dtype 형변환: tf.cast()
  5. GPU/CPU: tf.device() 로 배치
  6. GradientTape: 자동 미분 → 딥러닝의 핵심!
  7. 경사하강법: x = x - lr * gradient

  다음 단계 → 02_sequential_model.py (첫 번째 신경망 만들기!)
""")
