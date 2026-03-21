# #########################################################################
#
#   PyTorch 학습 01단계: 텐서(Tensor)와 자동 미분(Autograd)
#   - 텐서 생성, 속성, 연산, GPU, Autograd, 계산 그래프 -
#   # 실행 방법: python 01_tensor_autograd.py (개념 학습용, PyTorch 없이 실행 가능)
#   # PyTorch 설치: pip install torch torchvision
#
# #########################################################################

import math
import random

# ===============================================================================
#  1. 텐서(Tensor)란 무엇인가?
# ===============================================================================
# 텐서는 다차원 배열입니다. NumPy의 ndarray와 비슷하지만 GPU 연산과 자동 미분을 지원합니다.
#
# 비유: 텐서는 "데이터를 담는 상자"입니다.
#   - 스칼라(0차원): 숫자 하나 (온도계의 눈금 하나)
#   - 벡터(1차원): 숫자들의 줄 (학생 5명의 시험 점수)
#   - 행렬(2차원): 숫자들의 표 (엑셀 시트)
#   - 3차원 텐서: 행렬의 묶음 (컬러 이미지 = RGB 3채널)

print("=" * 70)
print("Part 1: 텐서(Tensor) 개념 이해")
print("=" * 70)


# -----------------------------------------------------------------------
#  순수 파이썬으로 텐서 구현
# -----------------------------------------------------------------------
class Tensor:
    """PyTorch 텐서의 핵심 개념을 순수 파이썬으로 구현"""

    def __init__(self, data, requires_grad=False):
        # 데이터를 중첩 리스트로 저장
        if isinstance(data, (int, float)):
            self.data = data
            self.shape = ()
        elif isinstance(data, list):
            self.data = data
            self.shape = self._compute_shape(data)
        else:
            self.data = data
            self.shape = ()

        self.requires_grad = requires_grad
        self.grad = None            # 기울기 저장
        self._grad_fn = None        # 어떤 연산으로 만들어졌는지
        self._parents = []          # 부모 텐서들 (계산 그래프)
        self.dtype = "float32"      # 데이터 타입
        self.device = "cpu"         # 디바이스

    def _compute_shape(self, data):
        """중첩 리스트의 shape 계산"""
        shape = []
        current = data
        while isinstance(current, list):
            shape.append(len(current))
            if len(current) > 0:
                current = current[0]
            else:
                break
        return tuple(shape)

    def __repr__(self):
        grad_info = f", requires_grad={self.requires_grad}" if self.requires_grad else ""
        return f"Tensor({self.data}{grad_info})"

    def __add__(self, other):
        """텐서 덧셈"""
        if isinstance(other, (int, float)):
            other = Tensor(other)
        result_data = self._elementwise_op(self.data, other.data, lambda a, b: a + b)
        result = Tensor(result_data, requires_grad=(self.requires_grad or other.requires_grad))
        result._grad_fn = "AddBackward"
        result._parents = [self, other]
        return result

    def __mul__(self, other):
        """텐서 원소별 곱셈"""
        if isinstance(other, (int, float)):
            other = Tensor(other)
        result_data = self._elementwise_op(self.data, other.data, lambda a, b: a * b)
        result = Tensor(result_data, requires_grad=(self.requires_grad or other.requires_grad))
        result._grad_fn = "MulBackward"
        result._parents = [self, other]
        return result

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            other = Tensor(other)
        result_data = self._elementwise_op(self.data, other.data, lambda a, b: a - b)
        result = Tensor(result_data, requires_grad=(self.requires_grad or other.requires_grad))
        result._grad_fn = "SubBackward"
        result._parents = [self, other]
        return result

    def _elementwise_op(self, a, b, op):
        """원소별 연산 수행 (재귀)"""
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return op(a, b)
        elif isinstance(a, list) and isinstance(b, list):
            return [self._elementwise_op(ai, bi, op) for ai, bi in zip(a, b)]
        elif isinstance(a, list) and isinstance(b, (int, float)):
            # 브로드캐스팅: 스칼라를 리스트에 적용
            return [self._elementwise_op(ai, b, op) for ai in a]
        elif isinstance(a, (int, float)) and isinstance(b, list):
            return [self._elementwise_op(a, bi, op) for bi in b]
        return op(a, b)


# ===============================================================================
#  2. 텐서 생성 방법
# ===============================================================================
print("\n--- 텐서 생성 방법 ---")

# (1) 데이터로부터 직접 생성
t1 = Tensor([1.0, 2.0, 3.0])
print(f"데이터로부터 생성: {t1}")
print(f"  shape: {t1.shape}")
# 실제 PyTorch 코드: t1 = torch.tensor([1.0, 2.0, 3.0])

# (2) zeros - 0으로 채운 텐서
def zeros(*shape):
    """0으로 채운 텐서 생성"""
    if len(shape) == 1:
        return Tensor([0.0] * shape[0])
    else:
        return Tensor([[0.0] * shape[1] for _ in range(shape[0])])

t_zeros = zeros(2, 3)
print(f"zeros(2,3): {t_zeros}")
# 실제 PyTorch 코드: t_zeros = torch.zeros(2, 3)

# (3) ones - 1로 채운 텐서
def ones(*shape):
    if len(shape) == 1:
        return Tensor([1.0] * shape[0])
    else:
        return Tensor([[1.0] * shape[1] for _ in range(shape[0])])

t_ones = ones(2, 3)
print(f"ones(2,3): {t_ones}")
# 실제 PyTorch 코드: t_ones = torch.ones(2, 3)

# (4) rand - 0~1 균일분포 난수
def rand(*shape):
    if len(shape) == 1:
        return Tensor([random.random() for _ in range(shape[0])])
    else:
        return Tensor([[random.random() for _ in range(shape[1])] for _ in range(shape[0])])

t_rand = rand(2, 3)
print(f"rand(2,3): {t_rand}")
# 실제 PyTorch 코드: t_rand = torch.rand(2, 3)

# (5) randn - 표준정규분포 난수
def randn(*shape):
    if len(shape) == 1:
        return Tensor([random.gauss(0, 1) for _ in range(shape[0])])
    else:
        return Tensor([[random.gauss(0, 1) for _ in range(shape[1])] for _ in range(shape[0])])

t_randn = randn(2, 3)
print(f"randn(2,3): {t_randn}")
# 실제 PyTorch 코드: t_randn = torch.randn(2, 3)

# (6) arange - 범위로 생성
def arange(start, end, step=1):
    result = []
    current = start
    while current < end:
        result.append(float(current))
        current += step
    return Tensor(result)

t_arange = arange(0, 10, 2)
print(f"arange(0,10,2): {t_arange}")
# 실제 PyTorch 코드: t_arange = torch.arange(0, 10, 2)

# (7) linspace - 균등 간격으로 생성
def linspace(start, end, steps):
    if steps == 1:
        return Tensor([float(start)])
    step = (end - start) / (steps - 1)
    return Tensor([start + i * step for i in range(steps)])

t_linspace = linspace(0, 1, 5)
print(f"linspace(0,1,5): {t_linspace}")
# 실제 PyTorch 코드: t_linspace = torch.linspace(0, 1, 5)


# ===============================================================================
#  3. 텐서 속성
# ===============================================================================
print("\n--- 텐서 속성 ---")

t = Tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
print(f"텐서: {t}")
print(f"  shape: {t.shape}")          # (2, 3) - 2행 3열
print(f"  dtype: {t.dtype}")          # float32
print(f"  device: {t.device}")        # cpu
print(f"  requires_grad: {t.requires_grad}")  # False

# 실제 PyTorch 코드:
# t = torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
# print(t.shape)          # torch.Size([2, 3])
# print(t.dtype)          # torch.float32
# print(t.device)         # cpu
# print(t.requires_grad)  # False


# ===============================================================================
#  4. 텐서 연산
# ===============================================================================
print("\n" + "=" * 70)
print("Part 2: 텐서 연산")
print("=" * 70)

# --- 사칙연산 ---
a = Tensor([1.0, 2.0, 3.0])
b = Tensor([4.0, 5.0, 6.0])

print(f"\na = {a}")
print(f"b = {b}")
print(f"a + b = {a + b}")
print(f"a * b = {a * b}")
print(f"a - b = {a - b}")

# 실제 PyTorch 코드:
# a = torch.tensor([1.0, 2.0, 3.0])
# b = torch.tensor([4.0, 5.0, 6.0])
# print(a + b)  # tensor([5., 7., 9.])
# print(a * b)  # tensor([4., 10., 18.])
# print(a / b)  # tensor([0.25, 0.4, 0.5])

# --- 행렬 곱셈 ---
print("\n--- 행렬 곱셈 ---")

def matmul(a_data, b_data):
    """행렬 곱셈: (m x n) @ (n x p) = (m x p)"""
    m = len(a_data)
    n = len(b_data)
    p = len(b_data[0])
    result = [[0.0] * p for _ in range(m)]
    for i in range(m):
        for j in range(p):
            for k in range(n):
                result[i][j] += a_data[i][k] * b_data[k][j]
    return result

mat_a = [[1.0, 2.0], [3.0, 4.0]]
mat_b = [[5.0, 6.0], [7.0, 8.0]]
mat_c = matmul(mat_a, mat_b)

print(f"A = {mat_a}")
print(f"B = {mat_b}")
print(f"A @ B = {mat_c}")
# 결과: [[19.0, 22.0], [43.0, 50.0]]

# 실제 PyTorch 코드:
# A = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
# B = torch.tensor([[5.0, 6.0], [7.0, 8.0]])
# C = A @ B              # 또는 torch.mm(A, B) 또는 torch.matmul(A, B)
# print(C)               # tensor([[19., 22.], [43., 50.]])

# --- 브로드캐스팅 ---
print("\n--- 브로드캐스팅 ---")
print("브로드캐스팅: 크기가 다른 텐서 간 연산을 자동으로 맞춰주는 기능")
print("비유: 선생님 한 명이 학생 전체에게 같은 점수를 더해주는 것")

vec = [1.0, 2.0, 3.0]
scalar = 10.0
broadcast_result = [v + scalar for v in vec]
print(f"[1,2,3] + 10 = {broadcast_result}")  # 스칼라가 벡터 크기로 확장

matrix = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
row_vec = [10.0, 20.0, 30.0]
broadcast_mat = [[matrix[i][j] + row_vec[j] for j in range(3)] for i in range(2)]
print(f"행렬 + 행벡터 = {broadcast_mat}")  # 행벡터가 각 행에 더해짐

# 실제 PyTorch 코드:
# mat = torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
# vec = torch.tensor([10.0, 20.0, 30.0])
# print(mat + vec)  # 자동 브로드캐스팅


# ===============================================================================
#  5. GPU 사용
# ===============================================================================
print("\n" + "=" * 70)
print("Part 3: GPU 사용")
print("=" * 70)

print("""
GPU(Graphics Processing Unit)는 원래 그래픽 처리용이지만,
수천 개의 코어로 병렬 연산을 수행할 수 있어 딥러닝에 적합합니다.

비유: CPU는 박사급 직원 몇 명, GPU는 고졸 직원 수천 명
     복잡한 작업은 CPU, 단순 반복 작업은 GPU가 빠름

PyTorch에서 GPU 사용 패턴:
""")

# GPU 사용 시뮬레이션
class DeviceSimulator:
    """GPU/CPU 디바이스 이동 시뮬레이션"""

    def __init__(self, name="cpu"):
        self.name = name

    def __repr__(self):
        return f"device('{self.name}')"

cpu = DeviceSimulator("cpu")
cuda = DeviceSimulator("cuda:0")

print(f"CPU 디바이스: {cpu}")
print(f"GPU 디바이스: {cuda}")

# 실제 PyTorch 코드:
# # GPU 사용 가능 여부 확인
# print(torch.cuda.is_available())       # True/False
# print(torch.cuda.device_count())       # GPU 개수
# print(torch.cuda.get_device_name(0))   # GPU 이름
#
# # 텐서를 GPU로 이동
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# x = torch.tensor([1.0, 2.0, 3.0])
# x_gpu = x.to(device)        # GPU로 이동
# x_cpu = x_gpu.cpu()          # 다시 CPU로
# x_gpu2 = x.cuda()            # 직접 GPU로
#
# # [주의] 주의: CPU 텐서와 GPU 텐서는 직접 연산 불가!
# # x_cpu + x_gpu  → 에러 발생
# # 같은 디바이스에 있어야 연산 가능

print("\n[시뮬레이션] 디바이스 이동:")
t_data = [1.0, 2.0, 3.0]
t_device = "cpu"
print(f"  텐서 생성: data={t_data}, device={t_device}")
t_device = "cuda:0"
print(f"  .to('cuda'): data={t_data}, device={t_device}")
t_device = "cpu"
print(f"  .cpu(): data={t_data}, device={t_device}")


# ===============================================================================
#  6. Autograd - 자동 미분
# ===============================================================================
print("\n" + "=" * 70)
print("Part 4: Autograd (자동 미분)")
print("=" * 70)

print("""
Autograd는 PyTorch의 핵심 기능으로, 기울기(gradient)를 자동으로 계산합니다.

비유: 미분을 수학적으로 직접 풀지 않아도,
     PyTorch가 알아서 "이 방향으로 가면 손실이 줄어든다"를 알려줍니다.
     마치 산에서 내려갈 때 GPS가 자동으로 가장 가파른 내리막을 찾아주는 것.
""")


# --- 수동 미분 vs 자동 미분 ---
print("--- 수동 미분 예시: y = x^2 일 때, dy/dx = 2x ---")

x_val = 3.0
y_val = x_val ** 2
dy_dx_manual = 2 * x_val  # 수학적으로 직접 미분

print(f"x = {x_val}")
print(f"y = x^2 = {y_val}")
print(f"dy/dx = 2x = {dy_dx_manual}")


# --- 수치 미분 (Numerical Differentiation) ---
print("\n--- 수치 미분: 아주 작은 변화로 기울기 근사 ---")

def numerical_gradient(f, x, h=1e-5):
    """중앙 차분법으로 수치 미분 계산"""
    return (f(x + h) - f(x - h)) / (2 * h)

f = lambda x: x ** 2
grad_numerical = numerical_gradient(f, 3.0)
print(f"수치 미분 dy/dx at x=3: {grad_numerical:.6f}")  # ~= 6.0


# --- Autograd 시뮬레이션 ---
print("\n--- Autograd 시뮬레이션 ---")

class AutogradScalar:
    """스칼라 값에 대한 자동 미분 구현"""

    def __init__(self, value, requires_grad=False):
        self.value = float(value)
        self.grad = 0.0
        self.requires_grad = requires_grad
        self._backward_fn = None
        self._parents = []

    def __repr__(self):
        return f"AutogradScalar(value={self.value:.4f}, grad={self.grad:.4f})"

    def __add__(self, other):
        if isinstance(other, (int, float)):
            other = AutogradScalar(other)
        result = AutogradScalar(self.value + other.value, requires_grad=True)
        result._parents = [self, other]

        def _backward():
            # d(a+b)/da = 1, d(a+b)/db = 1
            if self.requires_grad:
                self.grad += result.grad * 1.0
            if other.requires_grad:
                other.grad += result.grad * 1.0

        result._backward_fn = _backward
        return result

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            other = AutogradScalar(other)
        result = AutogradScalar(self.value * other.value, requires_grad=True)
        result._parents = [self, other]

        def _backward():
            # d(a*b)/da = b, d(a*b)/db = a
            if self.requires_grad:
                self.grad += result.grad * other.value
            if other.requires_grad:
                other.grad += result.grad * self.value

        result._backward_fn = _backward
        return result

    def __pow__(self, power):
        result = AutogradScalar(self.value ** power, requires_grad=True)
        result._parents = [self]

        def _backward():
            # d(x^n)/dx = n * x^(n-1)
            if self.requires_grad:
                self.grad += result.grad * power * (self.value ** (power - 1))

        result._backward_fn = _backward
        return result

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            other = AutogradScalar(other)
        result = AutogradScalar(self.value - other.value, requires_grad=True)
        result._parents = [self, other]

        def _backward():
            if self.requires_grad:
                self.grad += result.grad * 1.0
            if other.requires_grad:
                other.grad += result.grad * (-1.0)

        result._backward_fn = _backward
        return result

    def backward(self):
        """역전파: 계산 그래프를 역순으로 순회하며 기울기 계산"""
        # 위상 정렬 (Topological Sort)
        topo_order = []
        visited = set()

        def build_topo(node):
            if id(node) not in visited:
                visited.add(id(node))
                for parent in node._parents:
                    build_topo(parent)
                topo_order.append(node)

        build_topo(self)

        # 출발점의 기울기는 1
        self.grad = 1.0

        # 역순으로 기울기 전파
        for node in reversed(topo_order):
            if node._backward_fn:
                node._backward_fn()


# Autograd 테스트
print("\n예제 1: y = x^2, x=3에서 dy/dx = ?")
x = AutogradScalar(3.0, requires_grad=True)
y = x ** 2
y.backward()
print(f"  x = {x.value}, y = x^2 = {y.value}")
print(f"  dy/dx = {x.grad}")  # 6.0 (= 2 * 3)

print("\n예제 2: z = (x * y) + y^2, x=2, y=3에서 dz/dx, dz/dy = ?")
x = AutogradScalar(2.0, requires_grad=True)
y_var = AutogradScalar(3.0, requires_grad=True)
z = (x * y_var) + (y_var ** 2)
z.backward()
print(f"  x={x.value}, y={y_var.value}, z=(x*y)+y^2 = {z.value}")
print(f"  dz/dx = {x.grad}")       # 3.0 (= y)
print(f"  dz/dy = {y_var.grad}")    # 8.0 (= x + 2y = 2 + 6)

# 실제 PyTorch 코드:
# x = torch.tensor(3.0, requires_grad=True)
# y = x ** 2
# y.backward()
# print(x.grad)  # tensor(6.)
#
# x = torch.tensor(2.0, requires_grad=True)
# y = torch.tensor(3.0, requires_grad=True)
# z = (x * y) + (y ** 2)
# z.backward()
# print(x.grad)  # tensor(3.)
# print(y.grad)  # tensor(8.)


# ===============================================================================
#  7. 계산 그래프 (Computation Graph)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 5: 계산 그래프")
print("=" * 70)

print("""
계산 그래프는 연산 과정을 그래프로 표현한 것입니다.

PyTorch: 동적 계산 그래프 (Define-by-Run)
  - 코드를 실행할 때마다 그래프가 새로 생성됨
  - if/for 같은 제어문을 자유롭게 사용 가능
  - 디버깅이 쉬움 (print 찍어볼 수 있음)

TensorFlow 1.x: 정적 계산 그래프 (Define-and-Run)
  - 그래프를 먼저 정의하고, 나중에 실행
  - 최적화에 유리하지만 디버깅이 어려움
  (TF 2.x에서는 Eager Mode로 동적 그래프도 지원)

비유:
  PyTorch = 즉석 요리 (재료 넣으면서 바로바로 조리)
  TF 1.x = 레시피 작성 후 요리 (레시피 먼저 다 쓰고 나서 조리 시작)
""")

# 동적 그래프 장점 시연
print("--- 동적 그래프의 장점: 조건부 연산 ---")

def dynamic_computation(x_val, use_square=True):
    """입력 조건에 따라 다른 연산 수행 - PyTorch의 동적 그래프"""
    x = AutogradScalar(x_val, requires_grad=True)
    if use_square:
        y = x ** 2      # 조건에 따라 다른 연산!
    else:
        y = x * AutogradScalar(3.0)
    y.backward()
    return x.grad

grad1 = dynamic_computation(4.0, use_square=True)
grad2 = dynamic_computation(4.0, use_square=False)
print(f"use_square=True:  dy/dx = {grad1}")   # 8.0 (= 2*4)
print(f"use_square=False: dy/dx = {grad2}")   # 3.0


# ===============================================================================
#  8. 실습: Autograd로 경사하강법 직접 구현
# ===============================================================================
print("\n" + "=" * 70)
print("Part 6: 실습 - Autograd로 경사하강법 구현")
print("=" * 70)

print("""
문제: y = 2x + 1 관계를 가진 데이터에서 w와 b를 찾자
     (y_pred = w * x + b, w=2, b=1이 정답)

경사하강법은 산에서 내려가는 것과 같습니다:
  1. 현재 위치에서 가장 가파른 내리막 방향을 찾고 (기울기 계산)
  2. 그 방향으로 한 걸음 이동 (파라미터 업데이트)
  3. 산 아래에 도착할 때까지 반복 (손실이 충분히 작아질 때까지)
""")

# 데이터 생성
random.seed(42)
X_data = [float(i) for i in range(10)]
Y_data = [2.0 * x + 1.0 + random.gauss(0, 0.1) for x in X_data]

print("학습 데이터:")
for x, y in zip(X_data[:5], Y_data[:5]):
    print(f"  x={x:.1f}, y={y:.2f}")
print("  ...")

# 파라미터 초기화
w = AutogradScalar(random.gauss(0, 1), requires_grad=True)
b = AutogradScalar(0.0, requires_grad=True)
learning_rate = 0.01
print(f"\n초기 파라미터: w={w.value:.4f}, b={b.value:.4f}")
print(f"정답: w=2.0, b=1.0")

# 학습 루프
print(f"\n--- 경사하강법 학습 (lr={learning_rate}) ---")

for epoch in range(100):
    # 1. 기울기 초기화 (매 에폭마다!)
    w.grad = 0.0
    b.grad = 0.0

    total_loss = 0.0

    for x_val, y_val in zip(X_data, Y_data):
        # 2. 순전파 (Forward)
        x = AutogradScalar(x_val)
        y_pred = w * x + b

        # 3. 손실 계산 (MSE)
        diff = y_pred - AutogradScalar(y_val)
        loss = diff ** 2
        total_loss += loss.value

        # 4. 역전파 (Backward)
        loss.backward()

    avg_loss = total_loss / len(X_data)

    # 5. 파라미터 업데이트
    w.value -= learning_rate * w.grad / len(X_data)
    b.value -= learning_rate * b.grad / len(X_data)

    if epoch % 20 == 0:
        print(f"  Epoch {epoch:3d}: loss={avg_loss:.4f}, w={w.value:.4f}, b={b.value:.4f}")

print(f"\n최종 결과: w={w.value:.4f}, b={b.value:.4f}")
print(f"정답:     w=2.0000, b=1.0000")
print(f"오차:     w_err={abs(w.value - 2.0):.4f}, b_err={abs(b.value - 1.0):.4f}")

# 실제 PyTorch 코드:
# import torch
#
# X = torch.tensor([0., 1., 2., 3., 4., 5., 6., 7., 8., 9.])
# Y = 2 * X + 1 + torch.randn(10) * 0.1
#
# w = torch.tensor(0.0, requires_grad=True)
# b = torch.tensor(0.0, requires_grad=True)
# lr = 0.01
#
# for epoch in range(100):
#     y_pred = w * X + b
#     loss = ((y_pred - Y) ** 2).mean()
#
#     loss.backward()           # 자동 미분!
#
#     with torch.no_grad():     # 기울기 추적 끄기
#         w -= lr * w.grad
#         b -= lr * b.grad
#
#     w.grad.zero_()            # 기울기 초기화
#     b.grad.zero_()
#
#     if epoch % 20 == 0:
#         print(f"Epoch {epoch}: loss={loss.item():.4f}, w={w.item():.4f}, b={b.item():.4f}")


# ===============================================================================
#  핵심 정리
# ===============================================================================
print("\n" + "=" * 70)
print("핵심 정리")
print("=" * 70)
print("""
1. 텐서 = 다차원 배열 (NumPy ndarray + GPU + 자동 미분)
2. 텐서 생성: tensor(), zeros(), ones(), rand(), randn(), arange(), linspace()
3. 텐서 속성: shape, dtype, device, requires_grad
4. 행렬 곱: @ 연산자, torch.mm(), torch.matmul()
5. GPU: .to('cuda'), .cpu(), torch.cuda.is_available()
6. Autograd: requires_grad=True → 연산 → .backward() → .grad
7. PyTorch = 동적 그래프 (Define-by-Run), 디버깅 쉬움
8. 경사하강법: 기울기 → 파라미터 업데이트 → 반복

[주의] 주의사항:
   - backward() 호출 전 기울기를 반드시 초기화! (zero_grad)
   - with torch.no_grad(): 파라미터 업데이트 시 기울기 추적 끄기
   - CPU/GPU 텐서 혼합 연산 불가 → 같은 디바이스로 이동 필요
""")
