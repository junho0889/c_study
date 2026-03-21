# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   NumPy 학습 04단계: 배열 변형(Reshape & Manipulation)
#   ─ reshape, flatten, transpose, 합치기/나누기, 차원 조작 ─
#   ■ 실행 방법: python 04_reshape_manipulation.py
#   ■ NumPy 설치: pip install numpy
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ═══════════════════════════════════════════════════════════════════════════════
#  1. reshape() - 배열의 모양 바꾸기
# ═══════════════════════════════════════════════════════════════════════════════
#
#  reshape은 "같은 레고 블록으로 다른 모양 만들기"야!
#  원소 개수는 그대로, 모양만 바꾸는 거!
#  12개 블록 → 3×4, 4×3, 2×6, 6×2, 2×2×3 다 가능!
#  하지만 12개 블록으로 5×3 = 15칸은 불가능! (개수가 안 맞아!)

print("=" * 70)
print("1. reshape() - 배열 모양 바꾸기")
print("=" * 70)


def py_reshape(flat_data, new_shape):
    """1D 배열을 new_shape 모양으로 변환
    핵심: 원소 개수가 맞아야 함!
    """
    # 전체 원소 수 확인
    total = 1
    neg_one_idx = -1
    for i, s in enumerate(new_shape):
        if s == -1:
            neg_one_idx = i
        else:
            total *= s

    # -1 자동 계산
    actual_shape = list(new_shape)
    if neg_one_idx >= 0:
        actual_shape[neg_one_idx] = len(flat_data) // total

    # 원소 수 검증
    check = 1
    for s in actual_shape:
        check *= s
    if check != len(flat_data):
        raise ValueError(f"reshape 불가! {len(flat_data)}개 원소를 {tuple(actual_shape)} 모양으로 못 만듦!")

    # reshape 실행
    if len(actual_shape) == 1:
        return list(flat_data)
    elif len(actual_shape) == 2:
        rows, cols = actual_shape
        return [flat_data[i * cols:(i + 1) * cols] for i in range(rows)]
    elif len(actual_shape) == 3:
        d0, d1, d2 = actual_shape
        result = []
        for i in range(d0):
            layer = []
            for j in range(d1):
                start = i * d1 * d2 + j * d2
                layer.append(flat_data[start:start + d2])
            result.append(layer)
        return result


# 기본 reshape
data = list(range(1, 13))  # [1, 2, 3, ..., 12]
print(f"\n원본 (12개): {data}")

r_3x4 = py_reshape(data, (3, 4))
print(f"\nreshape(3, 4):")
for row in r_3x4:
    print(f"  {row}")

r_4x3 = py_reshape(data, (4, 3))
print(f"\nreshape(4, 3):")
for row in r_4x3:
    print(f"  {row}")

r_2x2x3 = py_reshape(data, (2, 2, 3))
print(f"\nreshape(2, 2, 3):")
for i, layer in enumerate(r_2x2x3):
    print(f"  페이지 {i}: {layer}")

# 【NumPy】
# arr = np.arange(1, 13)
# arr.reshape(3, 4)
# arr.reshape(4, 3)
# arr.reshape(2, 2, 3)

# ── -1 자동 계산 ──
print(f"\n── -1 자동 계산 (편리!) ──")
r_auto = py_reshape(data, (3, -1))
print(f"reshape(3, -1) → (3, 4):  {r_auto}")
r_auto2 = py_reshape(data, (-1, 6))
print(f"reshape(-1, 6) → (2, 6):  {r_auto2}")
print(f"→ -1을 넣으면 나머지 차원을 자동 계산!")
print(f"   12 ÷ 3 = 4이니까 (3, -1) → (3, 4)")

# 【NumPy】 arr.reshape(3, -1)  # 열 자동 계산
#           arr.reshape(-1, 6)  # 행 자동 계산

# ── reshape 실패 케이스 ──
print(f"\n── reshape 실패 케이스 ──")
try:
    py_reshape(data, (5, 3))  # 12 ≠ 15!
except ValueError as e:
    print(f"  reshape(5, 3): ❌ {e}")

# ── 주의: reshape은 뷰를 반환! ──
print(f"\n── ⚠️ reshape은 뷰(View)! ──")
print(f"  NumPy에서 reshape 결과를 바꾸면 원본도 바뀜!")
print(f"  안전하게 하려면: arr.reshape(3, 4).copy()")


# ═══════════════════════════════════════════════════════════════════════════════
#  2. ravel()과 flatten() - 다차원 → 1차원
# ═══════════════════════════════════════════════════════════════════════════════
#
#  ravel = 실을 풀다 (뷰! 원본과 연결)
#  flatten = 납작하게 만들다 (복사! 독립적)

print("\n" + "=" * 70)
print("2. ravel() vs flatten() - 다차원을 1차원으로")
print("=" * 70)


def py_flatten(matrix):
    """다차원 배열을 1차원으로 평탄화 (항상 복사)"""
    result = []
    for item in matrix:
        if isinstance(item, list):
            result.extend(py_flatten(item))
        else:
            result.append(item)
    return result


matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print(f"\n원본 (3×3):")
for row in matrix:
    print(f"  {row}")

flat = py_flatten(matrix)
print(f"\nflatten: {flat}")

# 3D도 펼칠 수 있어!
data_3d = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
flat_3d = py_flatten(data_3d)
print(f"\n3D 배열 → flatten: {flat_3d}")

# 【NumPy】
# arr = np.array([[1,2,3],[4,5,6],[7,8,9]])
# arr.ravel()    # [1,2,...,9]  ← 뷰! (가능하면)
# arr.flatten()  # [1,2,...,9]  ← 복사! (항상)

print(f"\n── ravel vs flatten 차이 ──")
print(f"  ravel():   뷰를 반환 (메모리 공유, 빠름)")
print(f"  flatten(): 복사를 반환 (독립적, 안전)")
print(f"  → 읽기만 할 거면 ravel(), 수정할 거면 flatten()!")


# ═══════════════════════════════════════════════════════════════════════════════
#  3. transpose()와 T - 행과 열 바꾸기
# ═══════════════════════════════════════════════════════════════════════════════
#
#  전치(transpose)는 "행과 열을 뒤집기"야!
#  마치 표를 90도 돌리는 것처럼!
#  (3×4) 행렬 → 전치하면 → (4×3) 행렬

print("\n" + "=" * 70)
print("3. transpose() - 전치 (행↔열)")
print("=" * 70)


def py_transpose(matrix):
    """2D 행렬 전치 (행과 열 교환)"""
    rows = len(matrix)
    cols = len(matrix[0])
    return [[matrix[r][c] for r in range(rows)] for c in range(cols)]


matrix = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12]
]
print(f"\n원본 (3×4):")
for row in matrix:
    print(f"  {row}")

transposed = py_transpose(matrix)
print(f"\n전치 (4×3):")
for row in transposed:
    print(f"  {row}")

# 확인: matrix[i][j] == transposed[j][i]
print(f"\n  matrix[0][2] = {matrix[0][2]}")
print(f"  transposed[2][0] = {transposed[2][0]}")
print(f"  같은 값! (행과 열이 바뀜)")

# 전치의 전치 = 원본!
double_t = py_transpose(transposed)
print(f"\n  전치의 전치 = 원본? {matrix == double_t}")

# 【NumPy】
# arr.T            # 속성으로 바로!
# arr.transpose()  # 메서드로도 가능
# np.transpose(arr, axes=(1, 0))  # 축 지정 가능 (3D 이상에서)


# ═══════════════════════════════════════════════════════════════════════════════
#  4. 배열 합치기 - concatenate, vstack, hstack, dstack
# ═══════════════════════════════════════════════════════════════════════════════
#
#  배열을 합치는 건 "레고 블록 연결"이야!
#  vstack: 위아래로 쌓기 (vertical)    ┃ A ┃
#                                      ┃ B ┃
#  hstack: 옆으로 붙이기 (horizontal)  ┃ A ┃ B ┃
#  dstack: 깊이 방향으로 (depth)       3D!

print("\n" + "=" * 70)
print("4. 배열 합치기")
print("=" * 70)


def py_concatenate_1d(arrays):
    """1D 배열 이어 붙이기"""
    result = []
    for arr in arrays:
        result.extend(arr)
    return result


def py_vstack(arrays):
    """세로로 쌓기 (행 추가)"""
    result = []
    for arr in arrays:
        if isinstance(arr[0], list):
            result.extend(arr)
        else:
            result.append(list(arr))
    return result


def py_hstack(arrays):
    """가로로 붙이기 (열 추가)"""
    if not isinstance(arrays[0][0], list):
        # 1D 배열이면 그냥 이어 붙이기
        return py_concatenate_1d(arrays)
    # 2D 배열이면 각 행을 이어 붙이기
    rows = len(arrays[0])
    result = []
    for r in range(rows):
        row = []
        for arr in arrays:
            row.extend(arr[r])
        result.append(row)
    return result


# 1D 합치기
a = [1, 2, 3]
b = [4, 5, 6]
print(f"\n── 1D 합치기 ──")
print(f"  a = {a}")
print(f"  b = {b}")
print(f"  concatenate: {py_concatenate_1d([a, b])}")

# 2D vstack
A = [[1, 2, 3], [4, 5, 6]]
B = [[7, 8, 9]]
print(f"\n── vstack (세로로 쌓기) ──")
print(f"  A (2×3):")
for row in A:
    print(f"    {row}")
print(f"  B (1×3):")
for row in B:
    print(f"    {row}")
stacked = py_vstack([A, B])
print(f"  vstack 결과 (3×3):")
for row in stacked:
    print(f"    {row}")

# 2D hstack
C = [[1, 2], [3, 4]]
D = [[5, 6, 7], [8, 9, 10]]
print(f"\n── hstack (가로로 붙이기) ──")
print(f"  C (2×2):")
for row in C:
    print(f"    {row}")
print(f"  D (2×3):")
for row in D:
    print(f"    {row}")
h_result = py_hstack([C, D])
print(f"  hstack 결과 (2×5):")
for row in h_result:
    print(f"    {row}")

# 【NumPy】
# np.concatenate([a, b])            # 1D 이어붙이기
# np.vstack([A, B])                 # 세로 쌓기
# np.hstack([C, D])                 # 가로 붙이기
# np.dstack([E, F])                 # 깊이 방향 (3D)
# np.concatenate([A, B], axis=0)    # vstack과 같음
# np.concatenate([C, D], axis=1)    # hstack과 같음

# ── 합칠 때 주의사항 ──
print(f"\n── ⚠️ 합치기 주의사항 ──")
print(f"  vstack: 열 수가 같아야 함!  (2×3) + (1×3) = OK")
print(f"  hstack: 행 수가 같아야 함!  (2×2) + (2×3) = OK")
print(f"  맞지 않으면 에러!")


# ═══════════════════════════════════════════════════════════════════════════════
#  5. 배열 나누기 - split, vsplit, hsplit
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("5. 배열 나누기")
print("=" * 70)


def py_split(arr, indices_or_sections):
    """배열 나누기"""
    if isinstance(indices_or_sections, int):
        # n등분
        n = indices_or_sections
        size = len(arr) // n
        return [arr[i * size:(i + 1) * size] for i in range(n)]
    else:
        # 인덱스 위치에서 나누기
        result = []
        prev = 0
        for idx in indices_or_sections:
            result.append(arr[prev:idx])
            prev = idx
        result.append(arr[prev:])
        return result


def py_vsplit(matrix, n):
    """세로 방향으로 나누기 (행 기준)"""
    rows_per = len(matrix) // n
    return [matrix[i * rows_per:(i + 1) * rows_per] for i in range(n)]


def py_hsplit(matrix, n):
    """가로 방향으로 나누기 (열 기준)"""
    cols_per = len(matrix[0]) // n
    return [[row[i * cols_per:(i + 1) * cols_per] for row in matrix] for i in range(n)]


# 1D split
data = list(range(0, 12))
print(f"\n원본: {data}")

parts = py_split(data, 3)
print(f"\n3등분:")
for i, part in enumerate(parts):
    print(f"  파트 {i}: {part}")

parts_idx = py_split(data, [3, 7])
print(f"\n인덱스 [3, 7]에서 나누기:")
for i, part in enumerate(parts_idx):
    print(f"  파트 {i}: {part}")

# 2D split
matrix = [
    [1,  2,  3,  4,  5,  6],
    [7,  8,  9,  10, 11, 12],
    [13, 14, 15, 16, 17, 18],
    [19, 20, 21, 22, 23, 24]
]
print(f"\n2D 배열 (4×6):")
for row in matrix:
    print(f"  {row}")

v_parts = py_vsplit(matrix, 2)
print(f"\nvsplit(2) - 세로 2등분:")
for i, part in enumerate(v_parts):
    print(f"  파트 {i}:")
    for row in part:
        print(f"    {row}")

h_parts = py_hsplit(matrix, 3)
print(f"\nhsplit(3) - 가로 3등분:")
for i, part in enumerate(h_parts):
    print(f"  파트 {i}:")
    for row in part:
        print(f"    {row}")

# 【NumPy】
# np.split(arr, 3)              # 3등분
# np.split(arr, [3, 7])         # 인덱스에서 나누기
# np.vsplit(matrix, 2)          # 세로 2등분
# np.hsplit(matrix, 3)          # 가로 3등분


# ═══════════════════════════════════════════════════════════════════════════════
#  6. 차원 추가/제거 - newaxis, expand_dims, squeeze
# ═══════════════════════════════════════════════════════════════════════════════
#
#  차원을 추가하는 건 "봉투에 넣기"야!
#  [1, 2, 3] → [[1, 2, 3]]  (행 벡터: 1×3)
#  [1, 2, 3] → [[1], [2], [3]]  (열 벡터: 3×1)
#
#  왜 필요해? 브로드캐스팅 때문!

print("\n" + "=" * 70)
print("6. 차원 추가/제거")
print("=" * 70)


def py_expand_dims(arr, axis):
    """차원 추가
    axis=0: 바깥에 대괄호 추가  [1,2,3] → [[1,2,3]]
    axis=1: 각 원소를 리스트로  [1,2,3] → [[1],[2],[3]]
    """
    if axis == 0:
        return [arr]  # (3,) → (1, 3)
    elif axis == 1:
        return [[x] for x in arr]  # (3,) → (3, 1)


def py_squeeze(arr):
    """크기 1인 차원 제거
    [[1,2,3]] → [1,2,3]
    [[[1]],[[2]],[[3]]] → [1,2,3]
    """
    while isinstance(arr, list) and len(arr) == 1 and isinstance(arr[0], list):
        arr = arr[0]
    if isinstance(arr, list) and all(isinstance(x, list) and len(x) == 1 for x in arr):
        arr = [x[0] for x in arr]
    return arr


vec = [10, 20, 30]
print(f"\n원본 1D: {vec}  shape: (3,)")

row = py_expand_dims(vec, axis=0)
print(f"\nexpand_dims(axis=0): {row}")
print(f"  shape: (1, 3) ← 행 벡터!")

col = py_expand_dims(vec, axis=1)
print(f"\nexpand_dims(axis=1): {col}")
print(f"  shape: (3, 1) ← 열 벡터!")

# squeeze로 되돌리기
print(f"\nsqueeze({row}): {py_squeeze(row)}")
print(f"  → 크기 1인 차원 제거!")

# 【NumPy】
# arr = np.array([10, 20, 30])
# arr[np.newaxis, :]  또는 arr[None, :]    # (1, 3)
# arr[:, np.newaxis]  또는 arr[:, None]    # (3, 1)
# np.expand_dims(arr, axis=0)              # (1, 3)
# np.squeeze(arr_with_1_dim)               # 1인 차원 제거

# 왜 필요한지 - 브로드캐스팅 예시
print(f"\n── 왜 차원 추가가 필요할까? ──")
a = [1, 2, 3]     # shape (3,)
b = [10, 20, 30]  # shape (3,)

# 외적(outer product)을 만들고 싶을 때!
# a를 열 벡터로 만들고, b를 행 벡터로 두면
a_col = py_expand_dims(a, axis=1)  # (3, 1)
# 브로드캐스팅으로 (3, 1) * (3,) → (3, 3)!
outer = [[ai[0] * bj for bj in b] for ai in a_col]
print(f"외적 (outer product):")
for row in outer:
    print(f"  {row}")
print(f"→ 구구단 표처럼! a의 각 원소 × b의 각 원소")

# 【NumPy】 a[:, None] * b  또는  np.outer(a, b)


# ═══════════════════════════════════════════════════════════════════════════════
#  7. tile과 repeat - 배열 반복하기
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("7. tile과 repeat - 배열 반복")
print("=" * 70)


def py_tile(arr, reps):
    """배열을 타일처럼 반복 (np.tile 흉내)
    마치 화장실 타일을 반복해서 붙이듯이!
    """
    if isinstance(arr[0], list):
        # 2D
        if isinstance(reps, int):
            reps = (1, reps)
        row_rep, col_rep = reps
        tiled = [row * col_rep for row in arr] * row_rep
        return tiled
    else:
        # 1D
        if isinstance(reps, int):
            return arr * reps
        elif len(reps) == 2:
            row = arr * reps[1]
            return [row] * reps[0] if reps[0] > 1 else row


def py_repeat(arr, repeats):
    """각 원소를 repeats번 반복 (np.repeat 흉내)
    [1, 2, 3] repeat 2 → [1, 1, 2, 2, 3, 3]
    """
    result = []
    for x in arr:
        result.extend([x] * repeats)
    return result


# tile
pattern = [1, 2, 3]
print(f"\n── tile (패턴 반복) ──")
print(f"원본: {pattern}")
print(f"tile(3):    {py_tile(pattern, 3)}")

pattern_2d = [[1, 2], [3, 4]]
print(f"\n2D tile(2, 3):")
tiled = py_tile(pattern_2d, (2, 3))
for row in tiled:
    print(f"  {row}")
print(f"  → 2×3 타일 배치!")

# repeat
print(f"\n── repeat (각 원소 반복) ──")
print(f"원본: {pattern}")
print(f"repeat(3):  {py_repeat(pattern, 3)}")

# tile vs repeat 차이
print(f"\n── tile vs repeat 차이 ──")
arr = [1, 2, 3]
print(f"  원본:     {arr}")
print(f"  tile(2):   {py_tile(arr, 2)}      ← 전체를 2번!")
print(f"  repeat(2): {py_repeat(arr, 2)}  ← 각 원소를 2번!")

# 【NumPy】
# np.tile([1, 2, 3], 3)         # [1,2,3,1,2,3,1,2,3]
# np.repeat([1, 2, 3], 3)       # [1,1,1,2,2,2,3,3,3]
# np.tile([[1,2],[3,4]], (2,3))  # 2D 타일링


# ═══════════════════════════════════════════════════════════════════════════════
#  8. 실습: 이미지 데이터(3D 배열) 조작 시뮬레이션
# ═══════════════════════════════════════════════════════════════════════════════
#
#  이미지 = 3D 배열!
#  (높이, 너비, 채널)
#  예: (100, 200, 3) = 100px 높이, 200px 너비, RGB 3채널
#  각 값은 0~255 (밝기)

print("\n" + "=" * 70)
print("실습: 이미지 데이터 조작 시뮬레이션")
print("=" * 70)

import random
random.seed(42)

# 작은 "이미지" 생성 (4×6 pixels, RGB)
height, width, channels = 4, 6, 3


def create_image(h, w, ch):
    """RGB 이미지 생성 (h×w×3)"""
    return [[[random.randint(0, 255) for _ in range(ch)]
             for _ in range(w)]
            for _ in range(h)]


image = create_image(height, width, channels)

print(f"\n이미지 shape: ({height}, {width}, {channels})")
print(f"→ {height}px 높이, {width}px 너비, RGB 3채널")
print(f"\n첫 번째 행 (6개 픽셀의 RGB 값):")
for pixel in image[0]:
    print(f"  R={pixel[0]:3d}, G={pixel[1]:3d}, B={pixel[2]:3d}")


# ── 조작 1: 흑백 변환 (RGB → Grayscale) ──
def to_grayscale(img):
    """RGB → 흑백 변환
    공식: Gray = 0.299*R + 0.587*G + 0.114*B
    (사람의 눈이 초록색을 가장 잘 감지하니까 G 가중치가 높아!)
    """
    h = len(img)
    w = len(img[0])
    gray = [[0] * w for _ in range(h)]
    for i in range(h):
        for j in range(w):
            r, g, b = img[i][j]
            gray[i][j] = int(0.299 * r + 0.587 * g + 0.114 * b)
    return gray


gray_image = to_grayscale(image)
print(f"\n── 흑백 변환 ──")
print(f"원본 shape: ({height}, {width}, 3)")
print(f"흑백 shape: ({len(gray_image)}, {len(gray_image[0])})")
print(f"첫 행 밝기: {gray_image[0]}")

# 【NumPy】
# gray = np.dot(image, [0.299, 0.587, 0.114]).astype(np.uint8)


# ── 조작 2: 이미지 회전 (transpose) ──
def rotate_90(img):
    """이미지 90도 회전 (transpose + flip)"""
    h = len(img)
    w = len(img[0])
    # 전치 후 좌우 반전
    rotated = [[img[h - 1 - r][c] for r in range(h)] for c in range(w)]
    return rotated


rotated = rotate_90(gray_image)
print(f"\n── 90도 회전 ──")
print(f"원본 shape: ({len(gray_image)}, {len(gray_image[0])})")
print(f"회전 shape: ({len(rotated)}, {len(rotated[0])})")
print(f"→ 행과 열이 바뀜!")

# 【NumPy】 np.rot90(image)


# ── 조작 3: 이미지 뒤집기 ──
def flip_horizontal(img):
    """좌우 반전"""
    return [row[::-1] for row in img]


def flip_vertical(img):
    """상하 반전"""
    return img[::-1]


print(f"\n── 이미지 뒤집기 ──")
h_flipped = flip_horizontal(gray_image)
v_flipped = flip_vertical(gray_image)
print(f"원본 첫 행:     {gray_image[0]}")
print(f"좌우반전 첫 행: {h_flipped[0]}")
print(f"원본 마지막 행: {gray_image[-1]}")
print(f"상하반전 첫 행: {v_flipped[0]}")

# 【NumPy】 np.fliplr(image), np.flipud(image)


# ── 조작 4: 이미지 채널 분리/합치기 ──
def split_channels(img):
    """RGB 채널 분리"""
    h = len(img)
    w = len(img[0])
    r = [[img[i][j][0] for j in range(w)] for i in range(h)]
    g = [[img[i][j][1] for j in range(w)] for i in range(h)]
    b = [[img[i][j][2] for j in range(w)] for i in range(h)]
    return r, g, b


r_ch, g_ch, b_ch = split_channels(image)
print(f"\n── 채널 분리 ──")
print(f"R 채널 첫 행: {r_ch[0]}")
print(f"G 채널 첫 행: {g_ch[0]}")
print(f"B 채널 첫 행: {b_ch[0]}")

# 【NumPy】
# r, g, b = image[:, :, 0], image[:, :, 1], image[:, :, 2]
# merged = np.dstack([r, g, b])  # 다시 합치기


# ── 조작 5: 이미지 크기 변경 (간단한 리사이징) ──
def resize_nearest(img, new_h, new_w):
    """최근접 이웃 보간법으로 리사이징
    가장 간단한 방법: 가장 가까운 원본 픽셀 값을 사용
    """
    old_h = len(img)
    old_w = len(img[0])
    result = [[0] * new_w for _ in range(new_h)]
    for i in range(new_h):
        for j in range(new_w):
            src_i = int(i * old_h / new_h)
            src_j = int(j * old_w / new_w)
            result[i][j] = img[src_i][src_j]
    return result


resized = resize_nearest(gray_image, 8, 12)
print(f"\n── 리사이즈 (4×6 → 8×12) ──")
print(f"원본 shape: ({len(gray_image)}, {len(gray_image[0])})")
print(f"리사이즈: ({len(resized)}, {len(resized[0])})")
print(f"원본 첫 행:   {gray_image[0]}")
print(f"리사이즈 첫 행: {resized[0]}")
print(f"→ 각 픽셀이 2배로 복사됨! (최근접 이웃법)")


# ═══════════════════════════════════════════════════════════════════════════════
#  핵심 정리
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("핵심 정리")
print("=" * 70)
print("""
  1. reshape(m, n): 원소 수 동일하게 모양 변경, -1로 자동 계산
     - ⚠️ reshape은 뷰! (원본 공유)
  2. ravel(): 1D로 펼치기 (뷰), flatten(): 1D로 펼치기 (복사)
  3. transpose() / .T: 행↔열 교환
  4. 합치기: vstack(세로↓), hstack(가로→), dstack(깊이)
     - 합치는 방향 외 차원 크기가 같아야 함!
  5. 나누기: split, vsplit, hsplit
  6. 차원 조작:
     - expand_dims / newaxis: 차원 추가 (브로드캐스팅에 필수!)
     - squeeze: 크기 1인 차원 제거
  7. tile: 전체 패턴 반복, repeat: 각 원소 반복
  8. 이미지 = (높이, 너비, 채널) 3D 배열!
""")
