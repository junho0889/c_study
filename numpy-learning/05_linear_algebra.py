# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   NumPy 학습 05단계: 선형대수(Linear Algebra)
#   ─ 벡터, 행렬 곱셈, 역행렬, 행렬식, 고유값, 연립방정식 ─
#   ■ 실행 방법: python 05_linear_algebra.py
#   ■ NumPy 설치: pip install numpy
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


import math


# ═══════════════════════════════════════════════════════════════════════════════
#  1. 벡터 - 방향과 크기를 가진 화살표
# ═══════════════════════════════════════════════════════════════════════════════
#
#  벡터는 "방향이 있는 숫자 묶음"이야!
#  예: [3, 4] = "오른쪽 3, 위로 4" 가는 화살표
#
#  내적(dot product): 두 벡터가 얼마나 같은 방향인지!
#  - 같은 방향: 내적 > 0 (양수, 큰 값)
#  - 수직:     내적 = 0
#  - 반대 방향: 내적 < 0 (음수)

print("=" * 70)
print("1. 벡터 - 내적(dot product)과 크기(norm)")
print("=" * 70)


def py_dot(a, b):
    """벡터 내적 (np.dot 흉내)
    a·b = a1*b1 + a2*b2 + ... + an*bn
    """
    return sum(ai * bi for ai, bi in zip(a, b))


def py_norm(v):
    """벡터의 크기/길이 (np.linalg.norm 흉내)
    ||v|| = sqrt(v1² + v2² + ... + vn²)
    피타고라스 정리의 확장!
    """
    return math.sqrt(sum(x ** 2 for x in v))


def py_normalize(v):
    """단위 벡터로 변환 (크기를 1로!)"""
    n = py_norm(v)
    return [x / n for x in v]


# 벡터 기본
v1 = [3, 4]
v2 = [1, 0]
v3 = [0, 1]
v4 = [-3, -4]

print(f"\nv1 = {v1}")
print(f"||v1|| = {py_norm(v1):.1f}")
print(f"→ [3, 4] 벡터의 길이 = √(3²+4²) = √25 = 5!")

print(f"\n── 내적 ──")
print(f"v1·v2 = {py_dot(v1, v2)}  (v1과 x축 방향의 유사도)")
print(f"v1·v3 = {py_dot(v1, v3)}  (v1과 y축 방향의 유사도)")
print(f"v2·v3 = {py_dot(v2, v3)}  (수직! 내적=0)")
print(f"v1·v4 = {py_dot(v1, v4)}  (반대 방향! 음수)")

# 단위 벡터
unit_v1 = py_normalize(v1)
print(f"\nv1의 단위벡터: [{unit_v1[0]:.3f}, {unit_v1[1]:.3f}]")
print(f"단위벡터 크기: {py_norm(unit_v1):.1f}  (항상 1!)")

# 코사인 유사도 (추천 시스템의 핵심!)
def py_cosine_similarity(a, b):
    """코사인 유사도 = 내적 / (||a|| × ||b||)
    -1 ~ 1 범위: 1이면 같은 방향, 0이면 수직, -1이면 반대
    """
    return py_dot(a, b) / (py_norm(a) * py_norm(b))


print(f"\n── 코사인 유사도 ──")
user_a = [5, 4, 1, 2]  # 영화 평점
user_b = [4, 5, 1, 1]  # 비슷한 취향!
user_c = [1, 1, 5, 4]  # 다른 취향!
print(f"유저A 평점: {user_a}")
print(f"유저B 평점: {user_b}")
print(f"유저C 평점: {user_c}")
print(f"A-B 유사도: {py_cosine_similarity(user_a, user_b):.4f} (비슷한 취향!)")
print(f"A-C 유사도: {py_cosine_similarity(user_a, user_c):.4f} (다른 취향!)")

# 【NumPy】
# np.dot(v1, v2)
# np.linalg.norm(v1)
# cosine_sim = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# ═══════════════════════════════════════════════════════════════════════════════
#  2. 행렬 곱셈 - @ 연산자
# ═══════════════════════════════════════════════════════════════════════════════
#
#  행렬 곱셈은 "변환"이야!
#  예: 회전 행렬을 점에 곱하면 점이 회전해!
#
#  규칙: (m×n) @ (n×p) = (m×p)
#  - 왼쪽의 열 수(n)와 오른쪽의 행 수(n)가 같아야 함!
#  - 결과는 왼쪽의 행 수(m) × 오른쪽의 열 수(p)

print("\n" + "=" * 70)
print("2. 행렬 곱셈 - 규칙과 구현")
print("=" * 70)


def py_matmul(A, B):
    """행렬 곱셈 (np.matmul / @ 흉내)
    C[i][j] = sum(A[i][k] * B[k][j] for k)
    """
    rows_A = len(A)
    cols_A = len(A[0])
    cols_B = len(B[0])

    # 크기 검증
    rows_B = len(B)
    if cols_A != rows_B:
        raise ValueError(f"행렬 곱셈 불가! ({rows_A}×{cols_A}) @ ({rows_B}×{cols_B})")

    # 곱셈 실행
    result = [[0] * cols_B for _ in range(rows_A)]
    for i in range(rows_A):
        for j in range(cols_B):
            for k in range(cols_A):
                result[i][j] += A[i][k] * B[k][j]
    return result


A = [[1, 2], [3, 4]]    # 2×2
B = [[5, 6], [7, 8]]    # 2×2
C = py_matmul(A, B)

print(f"\nA = {A}")
print(f"B = {B}")
print(f"A @ B = {C}")
print(f"\n계산 과정:")
print(f"  C[0][0] = 1×5 + 2×7 = {1*5+2*7}")
print(f"  C[0][1] = 1×6 + 2×8 = {1*6+2*8}")
print(f"  C[1][0] = 3×5 + 4×7 = {3*5+4*7}")
print(f"  C[1][1] = 3×6 + 4×8 = {3*6+4*8}")

# 크기가 다른 행렬 곱셈
D = [[1, 2, 3], [4, 5, 6]]  # 2×3
E = [[7, 8], [9, 10], [11, 12]]  # 3×2
F = py_matmul(D, E)  # (2×3) @ (3×2) = (2×2)

print(f"\n(2×3) @ (3×2) = (2×2):")
print(f"D = {D}")
print(f"E = {E}")
print(f"D @ E = {F}")

# 곱셈 순서 중요! A@B ≠ B@A
BA = py_matmul(B, A)
print(f"\n⚠️ 행렬 곱셈은 순서가 중요!")
print(f"A @ B = {C}")
print(f"B @ A = {BA}")
print(f"같은가? {C == BA}  ← A@B ≠ B@A!")

# 곱셈 불가능한 경우
print(f"\n곱셈 불가능:")
try:
    py_matmul([[1, 2, 3]], [[4, 5, 6]])  # (1×3) @ (1×3)
except ValueError as e:
    print(f"  (1×3) @ (1×3): ❌ {e}")

# 【NumPy】
# A @ B                    # @ 연산자 (Python 3.5+)
# np.dot(A, B)             # 같은 결과
# np.matmul(A, B)          # 같은 결과
# A.dot(B)                 # 메서드 호출


# ═══════════════════════════════════════════════════════════════════════════════
#  3. 전치행렬, 단위행렬, 역행렬
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("3. 특수 행렬들 - 단위행렬, 역행렬")
print("=" * 70)


# ── 단위행렬 (Identity Matrix) ──
def py_eye(n):
    """단위행렬: 대각선만 1, 나머지 0
    어떤 행렬에 곱해도 그대로! (숫자에서 1과 같은 역할)
    A × I = A
    """
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


I = py_eye(3)
print(f"\n단위행렬 I₃:")
for row in I:
    print(f"  {row}")
print(f"→ 숫자에서 '1'과 같은 역할! A × I = A")


# ── 역행렬 (Inverse Matrix) ──
def py_inverse_2x2(M):
    """2×2 역행렬
    [[a, b], [c, d]] 의 역행렬 = (1/det) × [[d, -b], [-c, a]]
    det = ad - bc
    """
    a, b = M[0]
    c, d = M[1]
    det = a * d - b * c
    if abs(det) < 1e-10:
        raise ValueError("역행렬이 존재하지 않습니다! (det = 0)")
    return [[d / det, -b / det], [-c / det, a / det]]


# ── 행렬식 (Determinant) ──
def py_det_2x2(M):
    """2×2 행렬식"""
    return M[0][0] * M[1][1] - M[0][1] * M[1][0]


def py_det_3x3(M):
    """3×3 행렬식 (사루스 법칙)"""
    a, b, c = M[0]
    d, e, f = M[1]
    g, h, i = M[2]
    return a*(e*i - f*h) - b*(d*i - f*g) + c*(d*h - e*g)


A = [[4, 7], [2, 6]]
print(f"\nA = {A}")
det_A = py_det_2x2(A)
print(f"det(A) = {det_A}")
print(f"→ 행렬식이 0이 아니면 역행렬이 존재!")

A_inv = py_inverse_2x2(A)
print(f"\nA⁻¹ = {[[f'{x:.3f}' for x in row] for row in A_inv]}")

# 검증: A × A⁻¹ = I
product = py_matmul(A, A_inv)
print(f"A × A⁻¹ = {[[f'{x:.6f}' for x in row] for row in product]}")
print(f"→ 단위행렬! (숫자에서 5 × (1/5) = 1 과 같은 원리)")

# 역행렬이 없는 경우
print(f"\n── 역행렬이 없는 경우 ──")
singular = [[1, 2], [2, 4]]  # det = 1*4 - 2*2 = 0
print(f"B = {singular}")
print(f"det(B) = {py_det_2x2(singular)}  ← 0이면 역행렬 없음!")
try:
    py_inverse_2x2(singular)
except ValueError as e:
    print(f"  ❌ {e}")
print(f"→ 두 행이 비례관계(2배)이면 정보가 중복 → 역행렬 없음!")

# 3×3 행렬식
M3 = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
det3 = py_det_3x3(M3)
print(f"\n3×3 행렬식:")
for row in M3:
    print(f"  {row}")
print(f"det = {det3}")

# 【NumPy】
# np.eye(3)                  # 단위행렬
# np.linalg.inv(A)           # 역행렬
# np.linalg.det(A)           # 행렬식


# ═══════════════════════════════════════════════════════════════════════════════
#  4. 고유값과 고유벡터 - PCA의 기초!
# ═══════════════════════════════════════════════════════════════════════════════
#
#  고유벡터(eigenvector): 행렬을 곱해도 "방향이 안 바뀌는" 특별한 벡터!
#  고유값(eigenvalue): 그때 늘어나는 비율!
#
#  A × v = λ × v
#  (행렬) (고유벡터) (고유값) (고유벡터)
#
#  비유: 지진이 나면 건물이 흔들리는데,
#  고유벡터 = 건물이 흔들리는 방향
#  고유값 = 흔들리는 정도

print("\n" + "=" * 70)
print("4. 고유값/고유벡터 - 행렬의 DNA!")
print("=" * 70)


def py_eig_2x2(M):
    """2×2 행렬의 고유값/고유벡터 계산

    특성 방정식: det(A - λI) = 0
    2×2: λ² - (a+d)λ + (ad-bc) = 0
    """
    a, b = M[0]
    c, d = M[1]

    # 특성 방정식의 계수
    trace = a + d        # 대각합 = 고유값의 합
    det = a * d - b * c  # 행렬식 = 고유값의 곱

    # 이차방정식 풀기: λ² - trace*λ + det = 0
    discriminant = trace ** 2 - 4 * det

    if discriminant < 0:
        print("  (복소수 고유값 - 여기서는 생략)")
        return None, None

    sqrt_d = math.sqrt(discriminant)
    lambda1 = (trace + sqrt_d) / 2
    lambda2 = (trace - sqrt_d) / 2

    # 고유벡터 계산: (A - λI)v = 0
    eigenvectors = []
    for lam in [lambda1, lambda2]:
        if abs(b) > 1e-10:
            v = [b, lam - a]
        elif abs(c) > 1e-10:
            v = [lam - d, c]
        else:
            v = [1, 0] if abs(a - lam) < 1e-10 else [0, 1]
        # 정규화
        norm = math.sqrt(v[0]**2 + v[1]**2)
        v = [x / norm for x in v]
        eigenvectors.append(v)

    return [lambda1, lambda2], eigenvectors


# 대칭 행렬 (PCA에서 자주 등장!)
S = [[4, 2], [2, 3]]
print(f"\n대칭 행렬 S = {S}")

eigenvalues, eigenvectors = py_eig_2x2(S)
print(f"\n고유값: λ₁ = {eigenvalues[0]:.4f}, λ₂ = {eigenvalues[1]:.4f}")
print(f"고유벡터: v₁ = [{eigenvectors[0][0]:.4f}, {eigenvectors[0][1]:.4f}]")
print(f"         v₂ = [{eigenvectors[1][0]:.4f}, {eigenvectors[1][1]:.4f}]")

# 검증: A × v = λ × v
for i in range(2):
    lam = eigenvalues[i]
    v = eigenvectors[i]
    # A × v
    Av = [S[0][0]*v[0] + S[0][1]*v[1], S[1][0]*v[0] + S[1][1]*v[1]]
    # λ × v
    lv = [lam * v[0], lam * v[1]]
    print(f"\n  검증 (v{i+1}):")
    print(f"    A×v = [{Av[0]:.4f}, {Av[1]:.4f}]")
    print(f"    λ×v = [{lv[0]:.4f}, {lv[1]:.4f}]")
    print(f"    같은가? {'예!' if all(abs(a-b) < 1e-10 for a, b in zip(Av, lv)) else '아니오'}")

print(f"\n── PCA와의 연결 ──")
print(f"  PCA(주성분분석)는 데이터의 공분산 행렬에서 고유벡터를 구해!")
print(f"  고유값이 큰 고유벡터 = 데이터의 분산이 가장 큰 방향!")
print(f"  → 차원 축소의 핵심! (100차원 → 2차원으로 요약 가능)")

# 【NumPy】
# eigenvalues, eigenvectors = np.linalg.eig(S)
# eigenvalues   → [5.5616, 1.4384]
# eigenvectors  → 각 열이 고유벡터


# ═══════════════════════════════════════════════════════════════════════════════
#  5. 연립방정식 풀기 - Ax = b
# ═══════════════════════════════════════════════════════════════════════════════
#
#  2x + 3y = 8
#  4x + 1y = 6
#
#  이것을 행렬로 쓰면:
#  [[2, 3], [4, 1]] × [[x], [y]] = [[8], [6]]
#        A          ×     x       =     b
#
#  해: x = A⁻¹ × b

print("\n" + "=" * 70)
print("5. 연립방정식 풀기 - Ax = b")
print("=" * 70)


def py_solve_2x2(A, b):
    """2×2 연립방정식 풀기 (np.linalg.solve 흉내)
    크래머 공식 사용
    """
    a11, a12 = A[0]
    a21, a22 = A[1]
    b1, b2 = b

    det = a11 * a22 - a12 * a21
    if abs(det) < 1e-10:
        raise ValueError("해가 없거나 무한히 많습니다! (det = 0)")

    x = (b1 * a22 - b2 * a12) / det
    y = (a11 * b2 - a21 * b1) / det
    return [x, y]


# 문제: 사과 2개 + 바나나 3개 = 8000원
#        사과 4개 + 바나나 1개 = 6000원
print(f"\n문제: 사과와 바나나의 가격은?")
print(f"  사과 2개 + 바나나 3개 = 8000원")
print(f"  사과 4개 + 바나나 1개 = 6000원")

A = [[2, 3], [4, 1]]
b = [8000, 6000]

solution = py_solve_2x2(A, b)
print(f"\n풀이: Ax = b")
print(f"  A = {A}")
print(f"  b = {b}")
print(f"  x = {solution}")
print(f"\n  사과 1개 = {solution[0]:.0f}원")
print(f"  바나나 1개 = {solution[1]:.0f}원")

# 검증
check1 = 2 * solution[0] + 3 * solution[1]
check2 = 4 * solution[0] + 1 * solution[1]
print(f"\n  검증: 2×{solution[0]:.0f} + 3×{solution[1]:.0f} = {check1:.0f}")
print(f"        4×{solution[0]:.0f} + 1×{solution[1]:.0f} = {check2:.0f}")

# 【NumPy】
# x = np.linalg.solve(A, b)  ← 한 줄!

# 해가 없는 경우
print(f"\n── 해가 없는 경우 ──")
try:
    py_solve_2x2([[1, 2], [2, 4]], [3, 7])  # 두 식이 평행!
except ValueError as e:
    print(f"  {e}")
print(f"  → 두 직선이 평행하면 만나지 않아!")


# ═══════════════════════════════════════════════════════════════════════════════
#  6. 실습: 선형회귀를 행렬로 풀기 (정규방정식)
# ═══════════════════════════════════════════════════════════════════════════════
#
#  선형회귀: y = ax + b 에서 a, b를 찾는 것!
#  정규방정식: θ = (X^T X)^(-1) X^T y
#
#  "데이터에 가장 잘 맞는 직선 찾기!"

print("\n" + "=" * 70)
print("실습: 선형회귀 - 정규방정식으로 풀기")
print("=" * 70)

# 데이터: 공부시간 → 시험점수
study_hours = [1, 2, 3, 4, 5, 6, 7, 8]
test_scores = [35, 45, 50, 60, 65, 75, 80, 90]

print(f"\n공부시간: {study_hours}")
print(f"시험점수: {test_scores}")

# X 행렬 구성: [[1, x1], [1, x2], ...] (1은 절편 b를 위한 것)
X = [[1, h] for h in study_hours]
y = test_scores

print(f"\nX 행렬 (8×2):")
for row in X:
    print(f"  {row}")


# 정규방정식: θ = (X^T X)^(-1) X^T y
def py_transpose(M):
    """전치"""
    rows, cols = len(M), len(M[0])
    return [[M[r][c] for r in range(rows)] for c in range(cols)]


def py_matmul(A, B):
    """행렬 곱"""
    rows_A, cols_A = len(A), len(A[0])
    cols_B = len(B[0])
    result = [[0] * cols_B for _ in range(rows_A)]
    for i in range(rows_A):
        for j in range(cols_B):
            for k in range(cols_A):
                result[i][j] += A[i][k] * B[k][j]
    return result


def py_mat_vec_mul(M, v):
    """행렬 × 벡터"""
    return [sum(M[i][j] * v[j] for j in range(len(v))) for i in range(len(M))]


# Step 1: X^T 계산
X_T = py_transpose(X)
print(f"\nStep 1: X^T (2×8)")

# Step 2: X^T × X (2×2)
XTX = py_matmul(X_T, X)
print(f"Step 2: X^T × X = {XTX}")

# Step 3: (X^T × X)^(-1) (2×2)
XTX_inv = py_inverse_2x2(XTX)
print(f"Step 3: (X^T X)⁻¹ = {[[f'{v:.6f}' for v in row] for row in XTX_inv]}")

# Step 4: X^T × y
y_col = [[yi] for yi in y]
XTy = py_matmul(X_T, y_col)
XTy_vec = [row[0] for row in XTy]
print(f"Step 4: X^T × y = {XTy_vec}")

# Step 5: θ = (X^T X)^(-1) × X^T y
theta = py_mat_vec_mul(XTX_inv, XTy_vec)
b, a = theta  # 절편, 기울기

print(f"\nStep 5: θ = {[f'{t:.4f}' for t in theta]}")
print(f"\n결과: y = {a:.2f}x + {b:.2f}")
print(f"→ 공부시간 1시간 늘면 점수 약 {a:.1f}점 상승!")
print(f"→ 0시간 공부하면 약 {b:.1f}점 (기본 점수)")

# 예측
print(f"\n── 예측 ──")
for h in [3, 5, 10]:
    pred = a * h + b
    print(f"  {h}시간 공부 → 예상 점수: {pred:.1f}점")

# 잔차(오차) 확인
print(f"\n── 잔차(오차) 확인 ──")
total_error = 0
for h, actual in zip(study_hours, test_scores):
    predicted = a * h + b
    error = actual - predicted
    total_error += error ** 2
    print(f"  {h}시간: 실제 {actual}, 예측 {predicted:.1f}, 오차 {error:+.1f}")

rmse = math.sqrt(total_error / len(study_hours))
print(f"\n  RMSE(평균제곱근오차): {rmse:.2f}점")

# R² (결정계수)
y_mean = sum(test_scores) / len(test_scores)
ss_tot = sum((y - y_mean) ** 2 for y in test_scores)
ss_res = total_error
r_squared = 1 - ss_res / ss_tot
print(f"  R² (결정계수): {r_squared:.4f}")
print(f"  → {r_squared*100:.1f}%의 변동을 설명! (1에 가까울수록 좋은 모델)")

# 【NumPy로 한다면 - 3줄!】
# X = np.column_stack([np.ones(len(study_hours)), study_hours])
# theta = np.linalg.inv(X.T @ X) @ X.T @ test_scores
# # 또는: theta = np.linalg.lstsq(X, test_scores, rcond=None)[0]


# ═══════════════════════════════════════════════════════════════════════════════
#  핵심 정리
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("핵심 정리")
print("=" * 70)
print("""
  1. 벡터: 방향+크기, 내적(닮은 정도), norm(크기)
     - 코사인 유사도 = 내적 / (크기×크기): 추천 시스템의 핵심!
  2. 행렬 곱셈: (m×n) @ (n×p) = (m×p)
     - ⚠️ A@B ≠ B@A (교환법칙 안 됨!)
     - @ 연산자 또는 np.dot(), np.matmul()
  3. 특수 행렬:
     - 단위행렬(I): 곱해도 그대로 (np.eye)
     - 역행렬(A⁻¹): A × A⁻¹ = I (np.linalg.inv)
     - 행렬식(det): 0이면 역행렬 없음 (np.linalg.det)
  4. 고유값/벡터: A×v = λ×v, PCA의 기초!
     - np.linalg.eig()
  5. 연립방정식: Ax = b → x = np.linalg.solve(A, b)
  6. 선형회귀: θ = (X^T X)^(-1) X^T y (정규방정식)
""")
