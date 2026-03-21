# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   NumPy 학습 03단계: 연산(Operations)
#   ─ 원소별 연산, 브로드캐스팅, ufunc, 비교, 집계 ─
#   ■ 실행 방법: python 03_operations.py
#   ■ NumPy 설치: pip install numpy
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ═══════════════════════════════════════════════════════════════════════════════
#  1. 원소별 연산 (Element-wise Operations)
# ═══════════════════════════════════════════════════════════════════════════════
#
#  NumPy의 마법: 배열끼리 +, -, *, / 하면 "같은 위치끼리" 연산!
#  파이썬 리스트: [1,2,3] + [4,5,6] = [1,2,3,4,5,6]  ← 이어붙이기!
#  NumPy 배열:   [1,2,3] + [4,5,6] = [5,7,9]         ← 원소별 덧셈!

print("=" * 70)
print("1. 원소별 연산 - 배열끼리 +, -, *, /")
print("=" * 70)


def elementwise_op(a, b, op):
    """원소별 연산 (NumPy의 배열 연산 흉내)"""
    if isinstance(b, (int, float)):
        # 스칼라와 연산
        b = [b] * len(a)
    ops = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y,
        '**': lambda x, y: x ** y,
        '//': lambda x, y: x // y,
        '%': lambda x, y: x % y,
    }
    return [ops[op](ai, bi) for ai, bi in zip(a, b)]


a = [1, 2, 3, 4, 5]
b = [10, 20, 30, 40, 50]

print(f"\na = {a}")
print(f"b = {b}")
print(f"\n  a + b  = {elementwise_op(a, b, '+')}")
print(f"  a - b  = {elementwise_op(a, b, '-')}")
print(f"  a * b  = {elementwise_op(a, b, '*')}")
print(f"  b / a  = {elementwise_op(b, a, '/')}")
print(f"  a ** 2 = {elementwise_op(a, 2, '**')}  ← 제곱")
print(f"  b // 3 = {elementwise_op(b, 3, '//')}  ← 몫")
print(f"  b % 3  = {elementwise_op(b, 3, '%')}   ← 나머지")

# 【NumPy】
# a = np.array([1, 2, 3, 4, 5])
# b = np.array([10, 20, 30, 40, 50])
# a + b, a - b, a * b, b / a, a ** 2, b // 3, b % 3

# 파이썬 리스트와의 차이!
print(f"\n── 파이썬 리스트 vs NumPy ──")
py_result = [1, 2, 3] + [4, 5, 6]  # 이어붙이기!
print(f"  파이썬: [1,2,3] + [4,5,6] = {py_result}  ← 이어붙이기!")
np_result = elementwise_op([1, 2, 3], [4, 5, 6], '+')
print(f"  NumPy:  [1,2,3] + [4,5,6] = {np_result}       ← 원소별 덧셈!")


# ═══════════════════════════════════════════════════════════════════════════════
#  2. 브로드캐스팅 - 크기가 다른 배열도 연산 가능!
# ═══════════════════════════════════════════════════════════════════════════════
#
#  브로드캐스팅은 "복사해서 맞추기"야!
#  마치 벽지를 붙일 때, 작은 패턴을 반복해서 큰 벽을 채우듯이!
#
#  규칙:
#  1. 두 배열의 차원을 오른쪽부터 비교한다
#  2. 각 차원에서: 크기가 같거나, 하나가 1이면 OK!
#  3. 크기가 1인 차원을 늘려서 맞춘다
#
#  예시: (3, 4) + (1, 4) → (3, 4) + (3, 4)  ← 행 방향으로 복사!
#        (3, 4) + (4,)   → (3, 4) + (3, 4)  ← 차원 맞추고 복사!
#        (3, 4) + (3, 1) → (3, 4) + (3, 4)  ← 열 방향으로 복사!
#        (3, 4) + (2, 4) → ❌ 에러! (3과 2는 다르고 1도 아님!)

print("\n" + "=" * 70)
print("2. 브로드캐스팅 - 크기가 다른 배열도 연산!")
print("=" * 70)


def broadcast_add_scalar(matrix, scalar):
    """행렬 + 스칼라 (가장 간단한 브로드캐스팅)
    스칼라를 행렬 크기만큼 복사해서 더하기
    """
    return [[val + scalar for val in row] for row in matrix]


def broadcast_add_row(matrix, row_vector):
    """(m×n) 행렬 + (n,) 벡터 = 각 행에 벡터를 더하기
    벡터를 행 수만큼 복사!
    """
    return [[matrix[i][j] + row_vector[j]
             for j in range(len(row_vector))]
            for i in range(len(matrix))]


def broadcast_add_col(matrix, col_vector):
    """(m×n) 행렬 + (m,1) 벡터 = 각 열에 벡터를 더하기
    벡터를 열 수만큼 복사!
    """
    n_cols = len(matrix[0])
    return [[matrix[i][j] + col_vector[i]
             for j in range(n_cols)]
            for i in range(len(matrix))]


# 예시 1: 행렬 + 스칼라
print("\n── 예시 1: 행렬 + 스칼라 ──")
mat = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
result = broadcast_add_scalar(mat, 10)
print(f"행렬:")
for row in mat:
    print(f"  {row}")
print(f"+ 10 =")
for row in result:
    print(f"  {row}")

# 예시 2: 행렬 + 행 벡터
print("\n── 예시 2: (3×3) 행렬 + (3,) 벡터 ──")
row_vec = [100, 200, 300]
result = broadcast_add_row(mat, row_vec)
print(f"행렬 + {row_vec} =")
for row in result:
    print(f"  {row}")
print(f"→ 벡터가 각 행에 복사되어 더해짐!")

# 예시 3: 행렬 + 열 벡터
print("\n── 예시 3: (3×3) 행렬 + (3,1) 벡터 ──")
col_vec = [10, 20, 30]
result = broadcast_add_col(mat, col_vec)
print(f"행렬 + [[10],[20],[30]] =")
for row in result:
    print(f"  {row}")
print(f"→ 벡터가 각 열에 복사되어 더해짐!")

# 【NumPy】
# mat = np.array([[1,2,3],[4,5,6],[7,8,9]])
# mat + 10                                    # 스칼라 브로드캐스팅
# mat + np.array([100, 200, 300])             # 행 브로드캐스팅
# mat + np.array([[10],[20],[30]])            # 열 브로드캐스팅

# 브로드캐스팅 규칙 시각화
print("\n── 브로드캐스팅 규칙 ──")
print("""
  오른쪽부터 차원을 비교!

  (3, 4)  +  (4,)   → OK!  (4와 4 같음, 없는 차원은 1로 추가)
  (3, 4)  +  (1, 4) → OK!  (4와 4 같음, 1은 3으로 확장)
  (3, 4)  +  (3, 1) → OK!  (3과 3 같음, 1은 4로 확장)
  (3, 4)  +  (2, 4) → ❌   (3과 2 다르고 1도 아님!)

  (2, 3, 4) + (3, 4) → OK!  (뒤 두 차원 일치, 앞은 확장)
  (2, 3, 4) + (1, 4) → OK!  (4 일치, 1→3 확장, 앞 확장)
""")

# 주의사항!
print("── ⚠️ 브로드캐스팅 주의사항 ──")
print("  1. 의도치 않은 브로드캐스팅 발생 가능!")
print("  2. 큰 배열이 생성되어 메모리 폭발 가능!")
print("  3. shape을 항상 확인하는 습관을 들이자!")


# ═══════════════════════════════════════════════════════════════════════════════
#  3. 유니버셜 함수(ufunc) - 수학 함수들
# ═══════════════════════════════════════════════════════════════════════════════
#
#  ufunc은 "배열의 모든 원소에 함수를 적용"하는 거야!
#  for 루프 없이 한 번에! 그래서 빠르고 편리해!

print("\n" + "=" * 70)
print("3. 유니버셜 함수(ufunc)")
print("=" * 70)

import math


def py_sqrt(arr):
    """np.sqrt 흉내 - 모든 원소에 제곱근"""
    return [math.sqrt(x) for x in arr]


def py_exp(arr):
    """np.exp 흉내 - 모든 원소에 e^x"""
    return [math.exp(x) for x in arr]


def py_log(arr):
    """np.log 흉내 - 모든 원소에 자연로그"""
    return [math.log(x) for x in arr]


def py_sin(arr):
    """np.sin 흉내 - 모든 원소에 사인"""
    return [math.sin(x) for x in arr]


def py_abs(arr):
    """np.abs 흉내 - 모든 원소에 절대값"""
    return [abs(x) for x in arr]


values = [1, 4, 9, 16, 25]
print(f"\n원본: {values}")
print(f"sqrt: {[f'{x:.2f}' for x in py_sqrt(values)]}")
# 【NumPy】 np.sqrt([1, 4, 9, 16, 25])  → [1., 2., 3., 4., 5.]

exp_input = [0, 1, 2, 3]
print(f"\nexp({exp_input}): {[f'{x:.4f}' for x in py_exp(exp_input)]}")
# 【NumPy】 np.exp([0, 1, 2, 3])  → [1., 2.7183, 7.3891, 20.0855]

log_input = [1, math.e, math.e**2, 10]
print(f"log({[f'{x:.2f}' for x in log_input]}): {[f'{x:.4f}' for x in py_log(log_input)]}")
# 【NumPy】 np.log([1, np.e, np.e**2, 10])

angles = [0, math.pi/6, math.pi/4, math.pi/3, math.pi/2]
angle_names = ["0°", "30°", "45°", "60°", "90°"]
sin_values = py_sin(angles)
print(f"\nsin 함수:")
for name, angle, val in zip(angle_names, angles, sin_values):
    print(f"  sin({name}) = {val:.4f}")
# 【NumPy】 np.sin([0, np.pi/6, np.pi/4, np.pi/3, np.pi/2])

neg_values = [-3, -1, 0, 2, -5, 4]
print(f"\nabs({neg_values}): {py_abs(neg_values)}")
# 【NumPy】 np.abs([-3, -1, 0, 2, -5, 4])


# ═══════════════════════════════════════════════════════════════════════════════
#  4. 비교 연산 - 배열끼리 비교하기
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("4. 비교 연산과 부동소수점 주의사항")
print("=" * 70)


def elementwise_compare(a, b, op):
    """원소별 비교 (NumPy의 배열 비교 흉내)"""
    if isinstance(b, (int, float)):
        b = [b] * len(a)
    ops = {
        '==': lambda x, y: x == y,
        '!=': lambda x, y: x != y,
        '>':  lambda x, y: x > y,
        '>=': lambda x, y: x >= y,
        '<':  lambda x, y: x < y,
        '<=': lambda x, y: x <= y,
    }
    return [ops[op](ai, bi) for ai, bi in zip(a, b)]


scores = [85, 92, 67, 78, 95, 43, 88]
print(f"\n점수: {scores}")
print(f"  >= 80: {elementwise_compare(scores, 80, '>=')}")
print(f"  == 92: {elementwise_compare(scores, 92, '==')}")
print(f"  < 60:  {elementwise_compare(scores, 60, '<')}")

# 【NumPy】 scores >= 80  →  array([True, True, False, False, True, False, True])

# ⚠️ 부동소수점 비교 주의!
print("\n── ⚠️ 부동소수점 비교 함정! ──")
a = 0.1 + 0.2
b = 0.3
print(f"  0.1 + 0.2 = {a}")
print(f"  0.3       = {b}")
print(f"  0.1 + 0.2 == 0.3 ? {a == b}  ← False!!! 😱")
print(f"  차이: {abs(a - b):.20f}")
print(f"  → 컴퓨터는 소수를 2진수로 저장해서 작은 오차가 생겨!")


def py_allclose(a, b, atol=1e-8):
    """np.allclose 흉내 - '거의 같은지' 비교"""
    if isinstance(a, (int, float)):
        a = [a]
    if isinstance(b, (int, float)):
        b = [b]
    return all(abs(ai - bi) <= atol for ai, bi in zip(a, b))


print(f"\n  allclose(0.1+0.2, 0.3) = {py_allclose(a, b)}")
print(f"  → 부동소수점 비교는 항상 allclose() 사용!")

# 【NumPy】 np.allclose(0.1 + 0.2, 0.3)  → True


# ═══════════════════════════════════════════════════════════════════════════════
#  5. 집계 함수 - sum, mean, std, min, max (axis 개념!)
# ═══════════════════════════════════════════════════════════════════════════════
#
#  axis는 "어느 방향으로 합칠 거야?" 하는 거야!
#  2D 배열에서:
#  axis=0: 세로 방향(↓)으로 합치기 → 결과는 행 하나
#  axis=1: 가로 방향(→)으로 합치기 → 결과는 열 하나
#  axis=None: 전부 합치기 → 결과는 숫자 하나

print("\n" + "=" * 70)
print("5. 집계 함수와 axis 개념")
print("=" * 70)


def py_sum(matrix, axis=None):
    """합계 (axis 지원)"""
    if axis is None:
        return sum(val for row in matrix for val in row)
    elif axis == 0:
        # 세로 방향: 각 열의 합
        cols = len(matrix[0])
        return [sum(matrix[r][c] for r in range(len(matrix))) for c in range(cols)]
    elif axis == 1:
        # 가로 방향: 각 행의 합
        return [sum(row) for row in matrix]


def py_mean(matrix, axis=None):
    """평균 (axis 지원)"""
    if axis is None:
        total = sum(val for row in matrix for val in row)
        count = sum(len(row) for row in matrix)
        return total / count
    elif axis == 0:
        cols = len(matrix[0])
        rows = len(matrix)
        return [sum(matrix[r][c] for r in range(rows)) / rows for c in range(cols)]
    elif axis == 1:
        return [sum(row) / len(row) for row in matrix]


def py_std(data_list):
    """표준편차 계산"""
    n = len(data_list)
    mean = sum(data_list) / n
    variance = sum((x - mean) ** 2 for x in data_list) / n
    return math.sqrt(variance)


def py_argmin(data_list):
    """최솟값의 인덱스"""
    return min(range(len(data_list)), key=lambda i: data_list[i])


def py_argmax(data_list):
    """최댓값의 인덱스"""
    return max(range(len(data_list)), key=lambda i: data_list[i])


# 성적 데이터 (3명 × 4과목)
scores = [
    [85, 92, 78, 96],   # 학생 A
    [72, 88, 91, 64],   # 학생 B
    [93, 75, 82, 88],   # 학생 C
]
subjects = ["국어", "영어", "수학", "과학"]
students = ["학생A", "학생B", "학생C"]

print(f"\n성적표:")
print(f"{'':>8} {subjects[0]:>6} {subjects[1]:>6} {subjects[2]:>6} {subjects[3]:>6}")
for i, name in enumerate(students):
    print(f"{name:>8} {scores[i][0]:>6} {scores[i][1]:>6} {scores[i][2]:>6} {scores[i][3]:>6}")

# axis=None: 전체
print(f"\n전체 합계 (axis=None): {py_sum(scores)}")
print(f"전체 평균 (axis=None): {py_mean(scores):.1f}")

# axis=0: 세로 방향 (과목별)
col_sums = py_sum(scores, axis=0)
col_means = py_mean(scores, axis=0)
print(f"\n과목별 합계 (axis=0): {col_sums}")
print(f"과목별 평균 (axis=0): {[f'{x:.1f}' for x in col_means]}")

# axis=1: 가로 방향 (학생별)
row_sums = py_sum(scores, axis=1)
row_means = py_mean(scores, axis=1)
print(f"\n학생별 합계 (axis=1): {row_sums}")
print(f"학생별 평균 (axis=1): {[f'{x:.1f}' for x in row_means]}")

# 【NumPy】
# scores = np.array([[85,92,78,96],[72,88,91,64],[93,75,82,88]])
# scores.sum()          # 전체 합
# scores.sum(axis=0)    # 과목별 합  [250, 255, 251, 248]
# scores.sum(axis=1)    # 학생별 합  [351, 315, 338]
# scores.mean(axis=0)   # 과목별 평균

print(f"\n── axis 시각화 ──")
print("""
     axis=0 (세로↓)
        ↓   ↓   ↓   ↓
      [ 85, 92, 78, 96 ]  ← axis=1 (가로→)
      [ 72, 88, 91, 64 ]  ← axis=1 (가로→)
      [ 93, 75, 82, 88 ]  ← axis=1 (가로→)

  axis=0: 세로로 합치면 → 과목별 결과 (1행)
  axis=1: 가로로 합치면 → 학생별 결과 (1열)

  쉽게 외우기: axis=0은 "행이 사라지는 방향"
               axis=1은 "열이 사라지는 방향"
""")

# argmin, argmax
all_scores = [85, 92, 67, 78, 95, 43, 88, 71]
print(f"점수: {all_scores}")
print(f"최소값: {min(all_scores)} (위치: {py_argmin(all_scores)})")
print(f"최대값: {max(all_scores)} (위치: {py_argmax(all_scores)})")

# 【NumPy】
# np.argmin(scores), np.argmax(scores)

# 표준편차
print(f"\n표준편차: {py_std(all_scores):.2f}")
print(f"→ 점수가 평균에서 평균적으로 {py_std(all_scores):.1f}점 벗어남")

# 【NumPy】 np.std(all_scores)


# ═══════════════════════════════════════════════════════════════════════════════
#  6. 누적/차분 연산 - cumsum, cumprod, diff
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("6. 누적/차분 연산")
print("=" * 70)


def py_cumsum(arr):
    """누적 합계 (np.cumsum 흉내)
    [1, 2, 3, 4] → [1, 3, 6, 10]
    """
    result = []
    total = 0
    for x in arr:
        total += x
        result.append(total)
    return result


def py_cumprod(arr):
    """누적 곱 (np.cumprod 흉내)
    [1, 2, 3, 4] → [1, 2, 6, 24]
    """
    result = []
    prod = 1
    for x in arr:
        prod *= x
        result.append(prod)
    return result


def py_diff(arr):
    """차분 (np.diff 흉내)
    [1, 4, 9, 16] → [3, 5, 7]
    앞 뒤 원소의 차이!
    """
    return [arr[i+1] - arr[i] for i in range(len(arr) - 1)]


# 매출 데이터
monthly_sales = [100, 150, 120, 200, 180, 250]
months = ["1월", "2월", "3월", "4월", "5월", "6월"]

print(f"\n월별 매출: {monthly_sales}")

cumulative = py_cumsum(monthly_sales)
print(f"누적 매출: {cumulative}")
print(f"→ 6월까지 총 매출: {cumulative[-1]}만원")

changes = py_diff(monthly_sales)
print(f"\n월별 변화: {changes}")
print(f"→ 양수면 매출 증가, 음수면 감소!")

# 복리 계산에 cumprod 활용
rates = [1.05, 1.03, 1.08, 1.02, 1.06]  # 연간 수익률
cumulative_return = py_cumprod(rates)
print(f"\n연간 수익률: {[f'{(r-1)*100:.0f}%' for r in rates]}")
print(f"누적 수익률: {[f'{x:.4f}' for x in cumulative_return]}")
print(f"→ 5년 후 원금의 {cumulative_return[-1]:.4f}배 = {(cumulative_return[-1]-1)*100:.1f}% 수익!")

# 【NumPy】
# np.cumsum([100, 150, 120, 200, 180, 250])
# np.cumprod([1.05, 1.03, 1.08, 1.02, 1.06])
# np.diff([100, 150, 120, 200, 180, 250])


# ═══════════════════════════════════════════════════════════════════════════════
#  7. 실습: 브로드캐스팅으로 정규화 구현
# ═══════════════════════════════════════════════════════════════════════════════
#
#  정규화: 데이터를 0~1 범위로 맞추거나, 평균 0/표준편차 1로 맞추기
#  왜? 키(cm)와 몸무게(kg)처럼 단위가 다른 데이터를 비교하려면!

print("\n" + "=" * 70)
print("실습: 정규화(Normalization) 직접 구현")
print("=" * 70)

# 학생 데이터: [키(cm), 몸무게(kg), 시력]
data = [
    [175, 72, 1.5],
    [162, 55, 0.8],
    [180, 85, 1.2],
    [158, 48, 2.0],
    [170, 68, 1.0],
]
features = ["키(cm)", "몸무게(kg)", "시력"]
print(f"\n원본 데이터:")
print(f"  {features}")
for row in data:
    print(f"  {row}")


# ── Min-Max 정규화: (x - min) / (max - min) ──
def min_max_normalize(matrix):
    """각 열(특성)을 0~1 범위로 정규화
    브로드캐스팅 활용: 열 방향 min/max를 구해서 전체 행에 적용
    """
    cols = len(matrix[0])
    rows = len(matrix)

    # 각 열의 min, max (axis=0 집계)
    col_min = [min(matrix[r][c] for r in range(rows)) for c in range(cols)]
    col_max = [max(matrix[r][c] for r in range(rows)) for c in range(cols)]
    col_range = [col_max[c] - col_min[c] for c in range(cols)]

    # 정규화 (브로드캐스팅: 각 행에서 min 빼고 range로 나누기)
    result = [[(matrix[r][c] - col_min[c]) / col_range[c]
               for c in range(cols)]
              for r in range(rows)]
    return result, col_min, col_max


# ── Z-score 표준화: (x - mean) / std ──
def z_score_normalize(matrix):
    """각 열(특성)을 평균 0, 표준편차 1로 표준화"""
    cols = len(matrix[0])
    rows = len(matrix)

    # 각 열의 평균 (axis=0)
    col_mean = [sum(matrix[r][c] for r in range(rows)) / rows for c in range(cols)]

    # 각 열의 표준편차
    col_std = []
    for c in range(cols):
        variance = sum((matrix[r][c] - col_mean[c]) ** 2 for r in range(rows)) / rows
        col_std.append(math.sqrt(variance))

    # 표준화 (브로드캐스팅!)
    result = [[(matrix[r][c] - col_mean[c]) / col_std[c]
               for c in range(cols)]
              for r in range(rows)]
    return result, col_mean, col_std


# Min-Max 적용
normalized, mins, maxs = min_max_normalize(data)
print(f"\nMin-Max 정규화 (0~1 범위):")
for row in normalized:
    print(f"  [{', '.join(f'{x:.3f}' for x in row)}]")
print(f"  → 모든 특성이 0~1 범위! 비교 가능!")

# Z-score 적용
standardized, means, stds = z_score_normalize(data)
print(f"\nZ-score 표준화 (평균 0, 표준편차 1):")
for row in standardized:
    print(f"  [{', '.join(f'{x:+.3f}' for x in row)}]")

# 검증: 표준화 후 평균은 0, 표준편차는 1?
for c in range(3):
    col = [standardized[r][c] for r in range(5)]
    col_mean = sum(col) / len(col)
    col_std = math.sqrt(sum((x - col_mean) ** 2 for x in col) / len(col))
    print(f"  {features[c]:>10}: 평균={col_mean:+.6f}, 표준편차={col_std:.6f}")

# 【NumPy로 한다면 - 한 줄!】
# data = np.array([[175,72,1.5], [162,55,0.8], ...])
# min_max = (data - data.min(axis=0)) / (data.max(axis=0) - data.min(axis=0))
# z_score = (data - data.mean(axis=0)) / data.std(axis=0)
#
# ← 브로드캐스팅 덕분에 for 루프 없이 한 줄로!


# ═══════════════════════════════════════════════════════════════════════════════
#  핵심 정리
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("핵심 정리")
print("=" * 70)
print("""
  1. 원소별 연산: +, -, *, /, **, //, % → 같은 위치끼리!
  2. 브로드캐스팅: 크기 다른 배열도 자동으로 맞춰서 연산
     - 오른쪽부터 비교, 크기 같거나 1이면 OK
  3. ufunc: np.sqrt, np.exp, np.log, np.sin → 배열 전체에 적용
  4. 비교: ==, >, < → Boolean 배열 반환
     - ⚠️ 부동소수점은 np.allclose() 사용!
  5. 집계: sum, mean, std, min, max, argmin, argmax
     - axis=0: 세로↓(행 사라짐), axis=1: 가로→(열 사라짐)
  6. 누적/차분: cumsum(누적합), cumprod(누적곱), diff(차분)
  7. 정규화: 브로드캐스팅으로 한 줄에 가능!
""")
