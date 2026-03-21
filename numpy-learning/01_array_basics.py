# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   NumPy 학습 01단계: 배열(Array)의 기초
#   ─ ndarray란?, 배열 생성, 속성, dtype, 랜덤 배열 ─
#   ■ 실행 방법: python 01_array_basics.py
#   ■ NumPy 설치: pip install numpy
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ═══════════════════════════════════════════════════════════════════════════════
#  1. ndarray란? - 파이썬 리스트와 뭐가 다를까?
# ═══════════════════════════════════════════════════════════════════════════════
#
#  생각해봐! 파이썬 리스트는 "서랍장"이야.
#  각 서랍에 뭐든 넣을 수 있어 - 사과, 연필, 장난감, 뭐든!
#  근데 NumPy 배열(ndarray)은 "계란판"이야.
#  모든 칸이 똑같은 크기고, 같은 종류만 넣을 수 있어!
#
#  왜 계란판이 더 빠를까?
#  - 서랍장: 각 서랍이 어디 있는지 하나하나 찾아야 해 (포인터 추적)
#  - 계란판: 첫 번째 칸 위치만 알면 나머지는 계산으로 바로 찾아! (연속 메모리)
#
#  컴퓨터 메모리에서:
#  파이썬 리스트: [주소1] → 값, [주소2] → 값, [주소3] → 값  (여기저기 흩어짐)
#  NumPy 배열:   [값][값][값][값][값]  (한 줄로 쭉 붙어있음 = C 메모리 레이아웃)

print("=" * 70)
print("1. ndarray vs 파이썬 리스트 - 왜 NumPy가 빠를까?")
print("=" * 70)

# ── 순수 파이썬으로 "배열" 흉내내기 ──
class SimpleArray:
    """NumPy 배열이 내부적으로 하는 일을 간단히 보여주는 클래스"""
    def __init__(self, data):
        # 모든 원소를 같은 타입으로 강제 변환!
        # 이게 핵심이야 - 같은 타입이니까 메모리 크기가 일정해
        self.data = [float(x) for x in data]
        self.size = len(self.data)
        self.itemsize = 8  # float64는 8바이트
        self.nbytes = self.size * self.itemsize

    def __repr__(self):
        return f"SimpleArray({self.data})"

    def __getitem__(self, index):
        return self.data[index]

    def __add__(self, other):
        """원소별 덧셈 - NumPy의 핵심 기능!"""
        if isinstance(other, SimpleArray):
            # 배열 + 배열: 같은 위치끼리 더하기
            result = [a + b for a, b in zip(self.data, other.data)]
        else:
            # 배열 + 숫자: 모든 원소에 숫자 더하기 (브로드캐스팅!)
            result = [x + other for x in self.data]
        return SimpleArray(result)


# 파이썬 리스트 vs SimpleArray(NumPy 흉내)
python_list = [1, 2, 3, 4, 5]
simple_arr = SimpleArray([1, 2, 3, 4, 5])

print(f"\n파이썬 리스트: {python_list}")
print(f"SimpleArray:  {simple_arr}")
print(f"메모리 크기:  {simple_arr.nbytes} 바이트 (원소 {simple_arr.size}개 × {simple_arr.itemsize}바이트)")

# 파이썬 리스트로 원소별 덧셈하려면?
list_add = [a + b for a, b in zip(python_list, python_list)]  # 귀찮아!
arr_add = simple_arr + simple_arr  # 깔끔!

print(f"\n리스트 원소별 덧셈: {list_add}")
print(f"배열 원소별 덧셈:  {arr_add}")

# 【실제 NumPy 코드】
# import numpy as np
# np_arr = np.array([1, 2, 3, 4, 5])
# result = np_arr + np_arr  # array([2, 4, 6, 8, 10])


# ═══════════════════════════════════════════════════════════════════════════════
#  2. 배열 생성 함수들 - 다양한 방법으로 배열 만들기
# ═══════════════════════════════════════════════════════════════════════════════
#
#  NumPy는 배열을 만드는 다양한 함수를 제공해!
#  마치 레고 블록을 여러 방법으로 조립하듯이!

print("\n" + "=" * 70)
print("2. 배열 생성 함수들")
print("=" * 70)


# ── 순수 파이썬 구현: np.array() ──
def py_array(data):
    """리스트를 받아서 배열로 변환 (np.array 흉내)"""
    if isinstance(data[0], list):
        # 2D 배열
        return [list(row) for row in data]
    return list(data)


# ── 순수 파이썬 구현: np.zeros() ──
def py_zeros(shape):
    """0으로 채운 배열 만들기"""
    if isinstance(shape, int):
        return [0.0] * shape
    elif len(shape) == 1:
        return [0.0] * shape[0]
    elif len(shape) == 2:
        return [[0.0] * shape[1] for _ in range(shape[0])]
    elif len(shape) == 3:
        return [[[0.0] * shape[2] for _ in range(shape[1])] for _ in range(shape[0])]


# ── 순수 파이썬 구현: np.ones() ──
def py_ones(shape):
    """1로 채운 배열 만들기"""
    if isinstance(shape, int):
        return [1.0] * shape
    elif len(shape) == 1:
        return [1.0] * shape[0]
    elif len(shape) == 2:
        return [[1.0] * shape[1] for _ in range(shape[0])]


# ── 순수 파이썬 구현: np.arange() ──
def py_arange(start, stop=None, step=1):
    """범위로 배열 만들기 (파이썬 range의 float 버전)"""
    if stop is None:
        stop = start
        start = 0
    result = []
    current = start
    while current < stop:
        result.append(current)
        current += step
    return result


# ── 순수 파이썬 구현: np.linspace() ──
def py_linspace(start, stop, num=50):
    """균등 간격으로 num개의 숫자 생성
    arange와 차이: arange는 '간격' 지정, linspace는 '개수' 지정!
    """
    if num == 1:
        return [start]
    step = (stop - start) / (num - 1)
    return [start + step * i for i in range(num)]


# ── 순수 파이썬 구현: np.eye() ──
def py_eye(n):
    """단위행렬 (대각선만 1, 나머지 0)
    마치 '나는 나' 같은 행렬! 곱해도 원래 값 그대로!
    """
    result = [[0.0] * n for _ in range(n)]
    for i in range(n):
        result[i][i] = 1.0
    return result


# ── 순수 파이썬 구현: np.full() ──
def py_full(shape, fill_value):
    """특정 값으로 채운 배열"""
    if isinstance(shape, int):
        return [fill_value] * shape
    elif len(shape) == 2:
        return [[fill_value] * shape[1] for _ in range(shape[0])]


# 각 함수 테스트
print("\n── np.array() 흉내 ──")
arr_1d = py_array([10, 20, 30, 40, 50])
arr_2d = py_array([[1, 2, 3], [4, 5, 6]])
print(f"1D 배열: {arr_1d}")
print(f"2D 배열: {arr_2d}")
# 【NumPy】 np.array([10, 20, 30, 40, 50])

print("\n── np.zeros() 흉내 ──")
zeros_1d = py_zeros(5)
zeros_2d = py_zeros((2, 3))
print(f"zeros(5):    {zeros_1d}")
print(f"zeros(2,3):  {zeros_2d}")
# 【NumPy】 np.zeros(5), np.zeros((2, 3))

print("\n── np.ones() 흉내 ──")
ones_1d = py_ones(4)
ones_2d = py_ones((2, 3))
print(f"ones(4):     {ones_1d}")
print(f"ones(2,3):   {ones_2d}")
# 【NumPy】 np.ones(4), np.ones((2, 3))

print("\n── np.arange() 흉내 ──")
range_1 = py_arange(10)
range_2 = py_arange(2, 10, 2)
range_3 = py_arange(0, 1, 0.2)
print(f"arange(10):        {range_1}")
print(f"arange(2, 10, 2):  {range_2}")
print(f"arange(0, 1, 0.2): {range_3}")
# 【NumPy】 np.arange(10), np.arange(2, 10, 2)

print("\n── np.linspace() 흉내 ──")
lin_1 = py_linspace(0, 1, 5)
lin_2 = py_linspace(0, 10, 6)
print(f"linspace(0, 1, 5):   {lin_1}")
print(f"linspace(0, 10, 6):  {lin_2}")
# 【NumPy】 np.linspace(0, 1, 5)  →  [0, 0.25, 0.5, 0.75, 1.0]

print("\n── np.eye() 흉내 ──")
eye_3 = py_eye(3)
print(f"eye(3):")
for row in eye_3:
    print(f"  {row}")
# 【NumPy】 np.eye(3)

print("\n── np.full() 흉내 ──")
full_1d = py_full(4, 7)
full_2d = py_full((2, 3), -1)
print(f"full(4, 7):      {full_1d}")
print(f"full((2,3), -1): {full_2d}")
# 【NumPy】 np.full(4, 7), np.full((2, 3), -1)


# ═══════════════════════════════════════════════════════════════════════════════
#  3. 배열의 속성들 - shape, ndim, size, dtype
# ═══════════════════════════════════════════════════════════════════════════════
#
#  배열은 "모양"을 가지고 있어!
#  마치 택배 상자에 가로, 세로, 높이가 있듯이!
#
#  shape: 배열의 모양 (각 차원의 크기)  → (3, 4)면 3행 4열
#  ndim:  차원 수                        → 2 (2차원)
#  size:  전체 원소 개수                 → 12 (3×4)
#  dtype: 원소의 데이터 타입             → float64

print("\n" + "=" * 70)
print("3. 배열의 속성 - shape, ndim, size, dtype")
print("=" * 70)


class ArrayWithInfo:
    """배열 속성을 보여주는 클래스"""
    def __init__(self, data):
        self.data = data
        self._compute_shape()

    def _compute_shape(self):
        """shape 계산 - 재귀적으로 각 차원의 크기를 알아내기"""
        shape = []
        current = self.data
        while isinstance(current, list):
            shape.append(len(current))
            if len(current) > 0:
                current = current[0]
            else:
                break
        self.shape = tuple(shape)
        self.ndim = len(self.shape)
        self.size = 1
        for s in self.shape:
            self.size *= s

    def info(self):
        print(f"  shape: {self.shape}  (모양)")
        print(f"  ndim:  {self.ndim}        (차원 수)")
        print(f"  size:  {self.size}       (전체 원소 수)")


# 1차원 배열
arr1 = ArrayWithInfo([1, 2, 3, 4, 5])
print(f"\n1D 배열 [1, 2, 3, 4, 5]:")
arr1.info()

# 2차원 배열
arr2 = ArrayWithInfo([[1, 2, 3], [4, 5, 6]])
print(f"\n2D 배열 [[1,2,3],[4,5,6]]:")
arr2.info()

# 3차원 배열 (예: 2장의 3×4 이미지)
arr3_data = [[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],
             [[13, 14, 15, 16], [17, 18, 19, 20], [21, 22, 23, 24]]]
arr3 = ArrayWithInfo(arr3_data)
print(f"\n3D 배열 (2×3×4):")
arr3.info()
print(f"  → 2장의 3행 4열 데이터로 생각하면 돼!")

# 【NumPy】
# arr = np.array([[1,2,3],[4,5,6]])
# arr.shape  → (2, 3)
# arr.ndim   → 2
# arr.size   → 6
# arr.dtype  → int64


# ═══════════════════════════════════════════════════════════════════════════════
#  4. dtype 종류 - 데이터 타입과 메모리 크기
# ═══════════════════════════════════════════════════════════════════════════════
#
#  dtype은 "이 배열에 뭘 넣을 건지" 정하는 거야!
#  마치 서류 양식에서 "숫자만 쓰세요" "글자만 쓰세요" 같은 거!
#
#  왜 중요해?
#  - int32 (정수 32비트):  4바이트, 약 ±21억 범위
#  - int64 (정수 64비트):  8바이트, 약 ±922경 범위
#  - float32 (실수 32비트): 4바이트, 소수점 약 7자리 정밀도
#  - float64 (실수 64비트): 8바이트, 소수점 약 15자리 정밀도 (기본값!)
#  - bool (참/거짓):        1바이트
#
#  메모리 비교 예시: 100만 개 숫자를 저장할 때
#  - int32:   4MB
#  - float64: 8MB  ← 두 배!

print("\n" + "=" * 70)
print("4. dtype - 데이터 타입과 메모리 크기 비교")
print("=" * 70)

import struct
import sys

# 각 dtype의 메모리 크기를 순수 파이썬으로 보여주기
dtype_info = {
    'bool':    {'size': 1, 'example': True,    'range': '0 또는 1'},
    'int8':    {'size': 1, 'example': 127,     'range': '-128 ~ 127'},
    'int16':   {'size': 2, 'example': 32767,   'range': '-32,768 ~ 32,767'},
    'int32':   {'size': 4, 'example': 2**31-1, 'range': '약 ±21억'},
    'int64':   {'size': 8, 'example': 2**63-1, 'range': '약 ±922경'},
    'float32': {'size': 4, 'example': 3.14,    'range': '소수점 ~7자리'},
    'float64': {'size': 8, 'example': 3.141592653589793, 'range': '소수점 ~15자리'},
}

print(f"\n{'dtype':<10} {'크기(바이트)':<14} {'100만개 메모리':<16} {'범위'}")
print("-" * 70)
for name, info in dtype_info.items():
    mb = info['size'] * 1_000_000 / (1024 * 1024)
    print(f"{name:<10} {info['size']:<14} {mb:>8.1f} MB      {info['range']}")

# float32 vs float64 정밀도 차이 보여주기
print("\n── 정밀도 차이 (왜 dtype이 중요한지!) ──")
val = 1.0 / 3.0
f32 = struct.unpack('f', struct.pack('f', val))[0]  # float32로 변환 후 되돌리기
f64 = val  # 파이썬 float은 기본 float64

print(f"float32: {f32:.20f}")
print(f"float64: {f64:.20f}")
print(f"→ float32는 소수점 7자리 이후 정확하지 않아!")

# 【NumPy】
# arr_f32 = np.array([1.0/3.0], dtype=np.float32)
# arr_f64 = np.array([1.0/3.0], dtype=np.float64)
# arr_int = np.array([1.5, 2.7], dtype=np.int32)  → [1, 2] (소수점 버림!)

# 주의! dtype 변환 시 데이터 손실
print("\n── dtype 변환 시 주의사항 ──")
float_values = [1.5, 2.7, 3.9, 4.1]
int_values = [int(x) for x in float_values]  # 소수점 버림!
print(f"float 원본: {float_values}")
print(f"int 변환:   {int_values}  ← 소수점이 잘렸어! 반올림이 아니라 버림!")

# 오버플로우 주의!
print("\n── 오버플로우 주의! ──")
max_int8 = 127
overflow = (max_int8 + 1) % 256 - 128  # int8에서 128은 -128이 됨!
print(f"int8 최대값: {max_int8}")
print(f"int8에 128 넣으면: {overflow}  ← 오버플로우! -128이 됨!")
print(f"→ 마치 시계가 12 다음에 1로 돌아가는 것처럼!")

# 【NumPy】
# np.array([128], dtype=np.int8)  → array([-128], dtype=int8)


# ═══════════════════════════════════════════════════════════════════════════════
#  5. 랜덤 배열 생성 패턴
# ═══════════════════════════════════════════════════════════════════════════════
#
#  게임에서 주사위를 던지거나, AI가 데이터를 만들 때 랜덤이 필요해!

print("\n" + "=" * 70)
print("5. 랜덤 배열 생성")
print("=" * 70)

import random

# ── 순수 파이썬 구현: np.random.rand() ──
def py_random_rand(*shape):
    """0~1 사이 균등분포 난수 배열"""
    if len(shape) == 1:
        return [random.random() for _ in range(shape[0])]
    elif len(shape) == 2:
        return [[random.random() for _ in range(shape[1])] for _ in range(shape[0])]


# ── 순수 파이썬 구현: np.random.randint() ──
def py_random_randint(low, high, size=None):
    """정수 난수 (low 이상 high 미만)"""
    if size is None:
        return random.randint(low, high - 1)
    if isinstance(size, int):
        return [random.randint(low, high - 1) for _ in range(size)]
    elif len(size) == 2:
        return [[random.randint(low, high - 1) for _ in range(size[1])]
                for _ in range(size[0])]


# ── 순수 파이썬 구현: np.random.normal() ──
def py_random_normal(loc=0.0, scale=1.0, size=None):
    """정규분포(가우시안) 난수
    loc: 평균 (종 모양의 꼭대기 위치)
    scale: 표준편차 (종이 얼마나 퍼졌는지)
    """
    if size is None:
        return random.gauss(loc, scale)
    if isinstance(size, int):
        return [random.gauss(loc, scale) for _ in range(size)]


random.seed(42)  # 재현성을 위한 시드 설정

print("\n── random.rand() 흉내 - 0~1 사이 랜덤 ──")
rand_arr = py_random_rand(5)
print(f"rand(5): {[f'{x:.4f}' for x in rand_arr]}")
# 【NumPy】 np.random.rand(5)

print("\n── random.randint() 흉내 - 정수 랜덤 ──")
randint_arr = py_random_randint(1, 7, 10)  # 주사위 10번!
print(f"randint(1, 7, 10): {randint_arr}")
# 【NumPy】 np.random.randint(1, 7, size=10)

print("\n── random.normal() 흉내 - 정규분포 ──")
normal_arr = py_random_normal(loc=170, scale=10, size=8)
print(f"키(cm) 랜덤 생성: {[f'{x:.1f}' for x in normal_arr]}")
print(f"→ 평균 170cm, 표준편차 10cm인 정규분포에서 8명의 키를 뽑음!")
# 【NumPy】 np.random.normal(170, 10, size=8)

# 시드(seed)의 중요성
print("\n── 시드(seed) - 왜 필요할까? ──")
random.seed(42)
run1 = [random.random() for _ in range(5)]
random.seed(42)
run2 = [random.random() for _ in range(5)]
print(f"시드 42 첫 번째: {[f'{x:.4f}' for x in run1]}")
print(f"시드 42 두 번째: {[f'{x:.4f}' for x in run2]}")
print(f"같은 결과? {run1 == run2}  ← 시드가 같으면 항상 같은 결과!")
print(f"→ 실험 결과를 재현할 수 있어! 논문이나 디버깅에 필수!")

# 【NumPy 최신 방식】
# rng = np.random.default_rng(42)   # 최신 권장 방식
# rng.random(5)                     # rand 대체
# rng.integers(1, 7, size=10)       # randint 대체
# rng.normal(170, 10, size=8)       # normal


# ═══════════════════════════════════════════════════════════════════════════════
#  6. 실습: 학생 성적 배열 만들고 기본 정보 출력하기
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("실습: 학생 성적 관리 시스템")
print("=" * 70)

random.seed(2024)

# 5명 학생, 4과목 성적 생성
subjects = ["국어", "영어", "수학", "과학"]
students = ["민수", "지영", "태호", "수진", "현우"]

# 60~100 사이 랜덤 성적
scores = py_random_randint(60, 101, (5, 4))

print("\n📊 학생 성적표:")
print(f"{'이름':>6}  ", end="")
for subj in subjects:
    print(f"{subj:>6}", end="")
print()
print("-" * 36)
for i, name in enumerate(students):
    print(f"{name:>6}  ", end="")
    for j in range(4):
        print(f"{scores[i][j]:>6}", end="")
    print()

# 배열 정보 출력
scores_info = ArrayWithInfo(scores)
print(f"\n배열 정보:")
scores_info.info()

# 기본 통계
print("\n기본 통계:")
all_scores = [s for row in scores for s in row]
print(f"  전체 평균: {sum(all_scores) / len(all_scores):.1f}점")
print(f"  최고 점수: {max(all_scores)}점")
print(f"  최저 점수: {min(all_scores)}점")

# 과목별 평균
print("\n과목별 평균:")
for j, subj in enumerate(subjects):
    col = [scores[i][j] for i in range(5)]
    avg = sum(col) / len(col)
    print(f"  {subj}: {avg:.1f}점")

# 학생별 평균
print("\n학생별 평균:")
for i, name in enumerate(students):
    avg = sum(scores[i]) / len(scores[i])
    print(f"  {name}: {avg:.1f}점")

# 【NumPy로 한다면】
# scores = np.random.randint(60, 101, size=(5, 4))
# print(f"전체 평균: {scores.mean():.1f}")
# print(f"과목별 평균: {scores.mean(axis=0)}")   ← axis=0: 행 방향(세로) 집계
# print(f"학생별 평균: {scores.mean(axis=1)}")   ← axis=1: 열 방향(가로) 집계


# ═══════════════════════════════════════════════════════════════════════════════
#  핵심 정리
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("핵심 정리")
print("=" * 70)
print("""
  1. ndarray는 '같은 타입'의 데이터가 메모리에 연속으로 저장됨 → 빠르다!
  2. 생성 함수:
     - array():    리스트 → 배열
     - zeros():    0으로 채운 배열
     - ones():     1로 채운 배열
     - arange():   범위(간격 지정)
     - linspace(): 범위(개수 지정)
     - eye():      단위행렬
     - full():     특정 값으로 채움
  3. 속성: shape(모양), ndim(차원), size(개수), dtype(타입)
  4. dtype: int32(4B), float64(8B, 기본), bool(1B)
     - 작은 dtype → 메모리 절약, 큰 dtype → 정밀도 높음
  5. 랜덤: rand(0~1), randint(정수), normal(정규분포)
     - seed 설정으로 재현 가능!
""")
