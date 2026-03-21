# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   NumPy 학습 07단계: 성능 최적화(Performance)
#   ─ 벡터화, 메모리 레이아웃, 뷰 vs 복사, dtype, 구조화 배열 ─
#   ■ 실행 방법: python 07_performance.py
#   ■ NumPy 설치: pip install numpy
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


import time
import math
import random
import sys


# ═══════════════════════════════════════════════════════════════════════════════
#  1. 벡터화 - for 루프 vs NumPy
# ═══════════════════════════════════════════════════════════════════════════════
#
#  벡터화 = "한 번에 처리!"
#  for 루프: 학생 30명에게 한 명씩 시험지 나눠주기
#  벡터화:  30명에게 동시에 시험지 뿌리기!
#
#  왜 빠를까?
#  1. C 언어로 된 내부 루프 (파이썬 인터프리터 오버헤드 없음)
#  2. SIMD 명령어 (CPU가 여러 데이터를 동시 처리)
#  3. 캐시 효율 (연속 메모리 접근)

print("=" * 70)
print("1. 벡터화 vs for 루프 - 속도 비교")
print("=" * 70)


def benchmark(func, *args, repeat=3):
    """함수 실행 시간 측정 (가장 빠른 결과 반환)"""
    times = []
    result = None
    for _ in range(repeat):
        start = time.perf_counter()
        result = func(*args)
        end = time.perf_counter()
        times.append(end - start)
    return min(times), result


# ── 벤치마크 1: 원소별 제곱 ──
print(f"\n── 벤치마크 1: 100만 개 원소 제곱 ──")
N = 1_000_000
data = [random.random() for _ in range(N)]


def loop_square(data):
    """for 루프로 제곱"""
    result = [0.0] * len(data)
    for i in range(len(data)):
        result[i] = data[i] ** 2
    return result


def listcomp_square(data):
    """리스트 컴프리헨션으로 제곱"""
    return [x ** 2 for x in data]


def map_square(data):
    """map으로 제곱"""
    return list(map(lambda x: x ** 2, data))


t_loop, _ = benchmark(loop_square, data)
t_comp, _ = benchmark(listcomp_square, data)
t_map, _ = benchmark(map_square, data)

print(f"  for 루프:          {t_loop:.4f}초")
print(f"  리스트 컴프리헨션: {t_comp:.4f}초")
print(f"  map():             {t_map:.4f}초")
fastest = min(t_loop, t_comp, t_map)
print(f"\n  리스트 컴프리헨션이 for 루프보다 {t_loop/t_comp:.1f}배 빠름")
print(f"  → 그래도 NumPy 벡터화보다는 10~100배 느림!")

# 【NumPy】
# arr = np.random.rand(1_000_000)
# result = arr ** 2    ← 벡터화! for 루프의 50~100배 빠름!


# ── 벤치마크 2: 조건부 연산 ──
print(f"\n── 벤치마크 2: 조건부 연산 (음수 → 0으로) ──")
mixed_data = [random.uniform(-10, 10) for _ in range(N)]


def loop_clip(data):
    """for 루프로 음수를 0으로"""
    result = [0.0] * len(data)
    for i in range(len(data)):
        result[i] = max(0, data[i])
    return result


def comp_clip(data):
    """리스트 컴프리헨션으로"""
    return [x if x > 0 else 0 for x in data]


t_loop2, _ = benchmark(loop_clip, mixed_data)
t_comp2, _ = benchmark(comp_clip, mixed_data)

print(f"  for 루프:          {t_loop2:.4f}초")
print(f"  리스트 컴프리헨션: {t_comp2:.4f}초")

# 【NumPy】
# np.maximum(arr, 0)       # 또는
# np.clip(arr, 0, None)    # → for 루프의 50배+ 빠름!


# ── 벤치마크 3: 벡터 내적 ──
print(f"\n── 벤치마크 3: 벡터 내적 (100만 차원) ──")
vec_a = [random.random() for _ in range(N)]
vec_b = [random.random() for _ in range(N)]


def loop_dot(a, b):
    """for 루프로 내적"""
    result = 0.0
    for i in range(len(a)):
        result += a[i] * b[i]
    return result


def zip_dot(a, b):
    """sum + zip으로 내적"""
    return sum(ai * bi for ai, bi in zip(a, b))


t_loop3, r1 = benchmark(loop_dot, vec_a, vec_b)
t_zip3, r2 = benchmark(zip_dot, vec_a, vec_b)

print(f"  for 루프: {t_loop3:.4f}초  (결과: {r1:.4f})")
print(f"  sum+zip:  {t_zip3:.4f}초  (결과: {r2:.4f})")

# 【NumPy】
# np.dot(a, b)  또는  a @ b  → 0.001초 정도!


# ═══════════════════════════════════════════════════════════════════════════════
#  2. 메모리 레이아웃 - C order vs Fortran order
# ═══════════════════════════════════════════════════════════════════════════════
#
#  메모리는 1차원이야! 2D 배열을 메모리에 저장하려면
#  "행 우선(C order)" 또는 "열 우선(Fortran order)"으로 펼쳐야 해!
#
#  [[1, 2, 3],
#   [4, 5, 6]]
#
#  C order (행 우선):      [1, 2, 3, 4, 5, 6]  ← 행을 쭉 이어서
#  Fortran order (열 우선): [1, 4, 2, 5, 3, 6]  ← 열을 쭉 이어서

print("\n" + "=" * 70)
print("2. 메모리 레이아웃 - 행 우선 vs 열 우선")
print("=" * 70)


def to_c_order(matrix):
    """2D → 1D (행 우선, C order)
    행을 하나씩 쭉 이어붙이기
    """
    result = []
    for row in matrix:
        result.extend(row)
    return result


def to_fortran_order(matrix):
    """2D → 1D (열 우선, Fortran order)
    열을 하나씩 쭉 이어붙이기
    """
    rows = len(matrix)
    cols = len(matrix[0])
    result = []
    for c in range(cols):
        for r in range(rows):
            result.append(matrix[r][c])
    return result


def from_c_order(flat, rows, cols):
    """1D → 2D (행 우선으로 읽기)"""
    return [flat[r * cols:(r + 1) * cols] for r in range(rows)]


def from_fortran_order(flat, rows, cols):
    """1D → 2D (열 우선으로 읽기)"""
    result = [[0] * cols for _ in range(rows)]
    for idx, val in enumerate(flat):
        c = idx // rows
        r = idx % rows
        result[r][c] = val
    return result


matrix = [[1, 2, 3], [4, 5, 6]]
print(f"\n원본 행렬:")
for row in matrix:
    print(f"  {row}")

c_flat = to_c_order(matrix)
f_flat = to_fortran_order(matrix)
print(f"\nC order (행 우선):      {c_flat}")
print(f"Fortran order (열 우선): {f_flat}")

# 왜 중요한지 - 캐시 효율!
print(f"\n── 왜 중요할까? 캐시 효율! ──")
print(f"""
  CPU가 메모리를 읽을 때 "캐시 라인" 단위로 가져와 (보통 64바이트).
  연속된 메모리를 접근하면 이미 캐시에 있어서 빠르고,
  띄엄띄엄 접근하면 캐시 미스가 생겨서 느려!

  행 단위 처리 (대부분의 경우):
    C order가 유리! → 행이 메모리에 연속
  열 단위 처리 (과학 계산):
    Fortran order가 유리! → 열이 메모리에 연속

  NumPy 기본값: C order
""")

# ── 캐시 효율 시뮬레이션 ──
print(f"── 캐시 효율 시뮬레이션 ──")
SIZE = 1000
matrix_big = [[random.random() for _ in range(SIZE)] for _ in range(SIZE)]

# 행 우선 접근 (cache-friendly)
def row_major_sum(mat):
    total = 0
    for r in range(len(mat)):
        for c in range(len(mat[0])):
            total += mat[r][c]
    return total

# 열 우선 접근 (cache-unfriendly)
def col_major_sum(mat):
    total = 0
    for c in range(len(mat[0])):
        for r in range(len(mat)):
            total += mat[r][c]
    return total

t_row, _ = benchmark(row_major_sum, matrix_big, repeat=2)
t_col, _ = benchmark(col_major_sum, matrix_big, repeat=2)
print(f"  행 우선 합계: {t_row:.4f}초")
print(f"  열 우선 합계: {t_col:.4f}초")
print(f"  차이: {t_col/t_row:.1f}배  (열 우선이 더 느림!)")
print(f"  → 캐시 미스 때문!")

# 【NumPy】
# arr_c = np.array(data, order='C')        # C order (기본)
# arr_f = np.array(data, order='F')        # Fortran order
# arr_c.flags['C_CONTIGUOUS']              # True
# arr_f.flags['F_CONTIGUOUS']              # True


# ═══════════════════════════════════════════════════════════════════════════════
#  3. 뷰 vs 복사 - 메모리 공유 확인
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("3. 뷰(View) vs 복사(Copy) - 메모리 절약")
print("=" * 70)


class MemoryTracker:
    """메모리 사용량 추적을 시뮬레이션"""
    _allocated = 0

    @classmethod
    def allocate(cls, name, data, is_view=False):
        if is_view:
            print(f"  {name}: 뷰 생성 (추가 메모리 0 바이트, 원본 공유!)")
        else:
            size = sys.getsizeof(data)
            cls._allocated += size
            print(f"  {name}: {size} 바이트 할당")


print(f"\n── 뷰가 메모리를 절약하는 방법 ──")
big_data = list(range(100000))
data_size = sys.getsizeof(big_data)
print(f"  원본 데이터 크기: {data_size:,} 바이트")

# 복사하면 메모리 2배!
copy_data = list(big_data)
copy_size = sys.getsizeof(copy_data)
print(f"  복사본 크기:     {copy_size:,} 바이트")
print(f"  총 메모리:       {data_size + copy_size:,} 바이트 (2배!)")

# 뷰(슬라이스)면 추가 메모리 거의 없음
# (파이썬 리스트는 실제로 뷰를 지원하지 않지만, 개념 설명)
print(f"\n  NumPy 뷰라면:    ~100 바이트 (메타데이터만!)")
print(f"  → 1GB 배열의 슬라이스도 추가 메모리 ~100 바이트!")

print(f"""
  ┌─────────────────────────────────────────────────┐
  │        메모리 절약 규칙                          │
  ├─────────────────────────────────────────────────┤
  │  1. 가능하면 뷰 사용 (슬라이싱, reshape)       │
  │  2. 불필요한 copy() 피하기                      │
  │  3. 수정이 필요할 때만 copy()                   │
  │  4. del 사용으로 불필요한 배열 삭제             │
  │  5. 인플레이스 연산: arr += 1 (새 배열 안 만듦) │
  │     vs arr = arr + 1 (새 배열 생성!)            │
  └─────────────────────────────────────────────────┘
""")

# 인플레이스 연산 차이
print(f"── 인플레이스 연산 ──")
print(f"  arr = arr + 1   → 새 배열 생성 후 대입 (메모리 2배 사용!)")
print(f"  arr += 1        → 기존 배열 직접 수정 (추가 메모리 없음!)")
print(f"  → 큰 배열에서는 차이가 커!")

# 【NumPy】
# view = arr[::2]           # 뷰
# view.base is arr           # True
# copy = arr[::2].copy()    # 복사
# copy.base is None          # None (독립적)


# ═══════════════════════════════════════════════════════════════════════════════
#  4. dtype 최적화 - 메모리 절약
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("4. dtype 최적화 - 적절한 타입 선택")
print("=" * 70)

print(f"\n── 100만 개 데이터의 메모리 사용량 ──")
n = 1_000_000
dtypes = {
    'float64': 8,
    'float32': 4,
    'float16': 2,
    'int64':   8,
    'int32':   4,
    'int16':   2,
    'int8':    1,
    'bool':    1,
}

print(f"  {'dtype':<10} {'1개 크기':>8} {'100만개':>10} {'절약률':>8}")
print(f"  {'-'*40}")
base_size = dtypes['float64'] * n
for dtype, size in dtypes.items():
    total = size * n
    saving = (1 - total / base_size) * 100
    print(f"  {dtype:<10} {size:>6} B  {total/1024/1024:>7.1f} MB  {saving:>6.0f}%")

print(f"\n── dtype 선택 가이드 ──")
print(f"""
  용도별 추천:
  ┌──────────────────────────────────────────────────┐
  │ float64: 과학 계산, 정밀한 값 (기본값)          │
  │ float32: 딥러닝, GPU 연산 (정밀도 충분!)       │
  │ float16: 추론 최적화, 메모리 극한 절약          │
  │ int32:   일반 정수, 인덱스                      │
  │ int16:   이미지 픽셀(가끔), 작은 범위 정수      │
  │ int8:    이미지 픽셀(0~255는 uint8!)            │
  │ bool:    마스크, 플래그                          │
  └──────────────────────────────────────────────────┘

  ⚠️ 주의: 타입 변환 시 정보 손실!
  float64 → float32: 소수점 7자리 이후 부정확
  float → int: 소수점 버림!
  int32 → int16: 32767 초과 시 오버플로우!
""")

# 실제 예시: 이미지 데이터
print(f"── 예시: 1920×1080 RGB 이미지 ──")
pixels = 1920 * 1080 * 3
for dtype, size in [('float64', 8), ('float32', 4), ('uint8', 1)]:
    total_mb = pixels * size / 1024 / 1024
    print(f"  {dtype:<10}: {total_mb:>6.1f} MB")
print(f"  → 이미지는 uint8(0~255)이면 충분! float64는 낭비!")

# 【NumPy】
# arr = np.array([1.5, 2.5, 3.5], dtype=np.float32)
# arr = arr.astype(np.int32)   # 타입 변환
# arr.nbytes                    # 메모리 사용량(바이트)


# ═══════════════════════════════════════════════════════════════════════════════
#  5. 구조화 배열 - 테이블 같은 배열
# ═══════════════════════════════════════════════════════════════════════════════
#
#  구조화 배열은 "엑셀 표"를 배열로 만든 거야!
#  각 열이 다른 타입을 가질 수 있어! (이름: 문자열, 나이: 정수, 키: 실수)

print("\n" + "=" * 70)
print("5. 구조화 배열 - 테이블처럼 사용하기")
print("=" * 70)


class StructuredArray:
    """구조화 배열 시뮬레이션 (np.dtype으로 필드 정의)"""

    def __init__(self, dtype_spec, data):
        """
        dtype_spec: [('name', str), ('age', int), ('height', float)]
        data: [('민수', 15, 168.5), ('지영', 14, 155.0), ...]
        """
        self.fields = {name: i for i, (name, _) in enumerate(dtype_spec)}
        self.types = {name: typ for name, typ in dtype_spec}
        self.data = [list(row) for row in data]

    def __getitem__(self, key):
        if isinstance(key, str):
            # 필드 이름으로 접근
            idx = self.fields[key]
            return [row[idx] for row in self.data]
        elif isinstance(key, int):
            # 행 인덱스로 접근
            return dict(zip(self.fields.keys(),
                          [self.types[name](self.data[key][i])
                           for name, i in self.fields.items()]))
        return None

    def sort_by(self, field, reverse=False):
        """특정 필드로 정렬"""
        idx = self.fields[field]
        self.data.sort(key=lambda row: row[idx], reverse=reverse)

    def filter(self, field, condition):
        """조건에 맞는 행 필터링"""
        idx = self.fields[field]
        return [row for row in self.data if condition(row[idx])]

    def display(self):
        """테이블 형태로 출력"""
        headers = list(self.fields.keys())
        print("  " + "  ".join(f"{h:>8}" for h in headers))
        print("  " + "-" * (10 * len(headers)))
        for row in self.data:
            formatted = []
            for val, (name, typ) in zip(row, self.types.items()):
                if typ == float:
                    formatted.append(f"{val:>8.1f}")
                else:
                    formatted.append(f"{str(val):>8}")
            print("  " + "  ".join(formatted))


# 학생 데이터
student_dtype = [('이름', str), ('나이', int), ('키', float), ('몸무게', float)]
student_data = [
    ('민수', 16, 175.2, 68.5),
    ('지영', 15, 162.8, 52.3),
    ('태호', 17, 180.1, 78.0),
    ('수진', 15, 158.5, 48.7),
    ('현우', 16, 172.0, 65.2),
    ('미라', 17, 165.3, 55.8),
    ('준서', 16, 178.5, 72.1),
    ('하늘', 15, 160.0, 50.5),
]

students = StructuredArray(student_dtype, student_data)

print(f"\n학생 데이터:")
students.display()

# 필드별 접근
print(f"\n이름 필드: {students['이름']}")
print(f"키 필드:   {students['키']}")

# 행별 접근
print(f"\n0번 학생: {students[0]}")

# 정렬
print(f"\n── 키 순 정렬 ──")
students.sort_by('키', reverse=True)
students.display()

# 필터링
print(f"\n── 키 170cm 이상 ──")
tall = students.filter('키', lambda x: x >= 170)
for row in tall:
    print(f"  {row}")

# 【NumPy】
# dt = np.dtype([('이름', 'U10'), ('나이', 'i4'), ('키', 'f8'), ('몸무게', 'f8')])
# students = np.array([('민수', 16, 175.2, 68.5), ...], dtype=dt)
# students['이름']           # 이름 필드 접근
# students[students['키'] >= 170]  # 조건 필터링
# np.sort(students, order='키')    # 필드 기준 정렬


# ═══════════════════════════════════════════════════════════════════════════════
#  6. np.vectorize - 커스텀 함수 벡터화
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("6. np.vectorize - 커스텀 함수를 배열에 적용")
print("=" * 70)


def py_vectorize(func):
    """np.vectorize 흉내
    스칼라 함수를 배열 전체에 적용할 수 있게 만들기
    """
    def wrapper(arr):
        if isinstance(arr, list):
            if isinstance(arr[0], list):
                return [[func(x) for x in row] for row in arr]
            return [func(x) for x in arr]
        return func(arr)
    return wrapper


# 성적 등급 함수
def grade(score):
    """점수 → 등급 변환"""
    if score >= 90: return 'A'
    elif score >= 80: return 'B'
    elif score >= 70: return 'C'
    elif score >= 60: return 'D'
    else: return 'F'


# 벡터화!
vec_grade = py_vectorize(grade)

scores = [95, 82, 67, 73, 88, 45, 91, 56, 78, 84]
grades = vec_grade(scores)
print(f"\n점수:  {scores}")
print(f"등급:  {grades}")

# 2D에도 적용!
score_matrix = [[85, 92], [67, 78], [91, 55]]
grade_matrix = vec_grade(score_matrix)
print(f"\n2D 점수: {score_matrix}")
print(f"2D 등급: {grade_matrix}")

# BMI 계산
def calculate_bmi(height_cm, weight_kg):
    height_m = height_cm / 100
    return weight_kg / (height_m ** 2)

def bmi_category(bmi):
    if bmi < 18.5: return "저체중"
    elif bmi < 25: return "정상"
    elif bmi < 30: return "과체중"
    else: return "비만"

vec_bmi_cat = py_vectorize(bmi_category)

heights = [175, 162, 180, 158, 172]
weights = [68, 52, 78, 48, 65]
bmis = [calculate_bmi(h, w) for h, w in zip(heights, weights)]
categories = vec_bmi_cat(bmis)

print(f"\n── BMI 계산 ──")
for h, w, b, c in zip(heights, weights, bmis, categories):
    print(f"  {h}cm, {w}kg → BMI {b:.1f} ({c})")

# 【NumPy】
# vec_grade = np.vectorize(grade)
# vec_grade(np.array([95, 82, 67, 73]))  → ['A', 'B', 'C', 'C']
#
# ⚠️ 주의: np.vectorize는 편의 기능이지 성능 최적화가 아님!
#    내부적으로 여전히 파이썬 for 루프 사용
#    진짜 벡터화는 NumPy 내장 함수 사용!


# ═══════════════════════════════════════════════════════════════════════════════
#  7. 실습: 순수 파이썬 vs NumPy 성능 벤치마크
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("실습: 종합 성능 벤치마크")
print("=" * 70)

random.seed(42)
N = 500_000

# 데이터 준비
list_a = [random.random() for _ in range(N)]
list_b = [random.random() for _ in range(N)]


# 테스트 1: 원소별 덧셈
def test_add(a, b):
    return [ai + bi for ai, bi in zip(a, b)]

# 테스트 2: 합계
def test_sum(a):
    return sum(a)

# 테스트 3: 최댓값 찾기
def test_max(a):
    return max(a)

# 테스트 4: 정렬
def test_sort(a):
    return sorted(a)

# 테스트 5: 조건부 합계
def test_cond_sum(a):
    return sum(x for x in a if x > 0.5)

# 테스트 6: 유클리드 거리
def test_distance(a, b):
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))


tests = [
    ("원소별 덧셈", test_add, (list_a, list_b)),
    ("합계",       test_sum, (list_a,)),
    ("최댓값",     test_max, (list_a,)),
    ("정렬",       test_sort, (list_a,)),
    ("조건부 합",  test_cond_sum, (list_a,)),
    ("유클리드 거리", test_distance, (list_a, list_b)),
]

print(f"\n데이터 크기: {N:,}개")
print(f"\n{'테스트':<16} {'파이썬 시간':>12} {'NumPy 예상':>12} {'예상 배율':>10}")
print("-" * 55)

for name, func, args in tests:
    t, _ = benchmark(func, *args, repeat=2)

    # NumPy 예상 시간 (경험적 비율)
    numpy_ratios = {
        "원소별 덧셈": 50, "합계": 100, "최댓값": 80,
        "정렬": 10, "조건부 합": 30, "유클리드 거리": 80
    }
    ratio = numpy_ratios.get(name, 50)
    numpy_est = t / ratio

    print(f"  {name:<14} {t:>10.4f}초  ~{numpy_est:>10.5f}초  ~{ratio:>6}배")

print(f"""
  ┌──────────────────────────────────────────────────────┐
  │              NumPy 성능 최적화 체크리스트            │
  ├──────────────────────────────────────────────────────┤
  │  1. for 루프 대신 벡터화 연산 사용                  │
  │  2. 적절한 dtype 선택 (float32 vs float64)         │
  │  3. 불필요한 copy() 피하기 (뷰 활용)              │
  │  4. 인플레이스 연산: +=, *=, -= 사용               │
  │  5. 미리 배열 할당: np.empty() or np.zeros()       │
  │  6. 브로드캐스팅 활용 (임시 배열 줄이기)           │
  │  7. np.vectorize 대신 내장 ufunc 사용              │
  │  8. 큰 데이터는 청크 처리 (메모리 부족 방지)       │
  └──────────────────────────────────────────────────────┘
""")


# ═══════════════════════════════════════════════════════════════════════════════
#  핵심 정리
# ═══════════════════════════════════════════════════════════════════════════════

print("=" * 70)
print("핵심 정리")
print("=" * 70)
print("""
  1. 벡터화: for 루프 → NumPy 연산으로! (50~100배 빠름!)
  2. 메모리 레이아웃: C order(행 우선)가 기본, 캐시 효율 중요!
  3. 뷰 vs 복사: 뷰는 메모리 절약, 수정 시 주의!
  4. dtype: float32로 메모리 50% 절약, 정밀도는 충분
  5. 구조화 배열: 다른 타입의 필드를 가진 테이블 형태
  6. np.vectorize: 편의 기능이지 성능 최적화는 아님!
  7. 인플레이스(+=): 새 배열 안 만들어서 메모리 절약!
""")
