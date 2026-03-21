# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   NumPy 학습 02단계: 인덱싱과 슬라이싱
#   ─ 기본 인덱싱, 슬라이싱, Boolean/팬시 인덱싱, 뷰 vs 복사 ─
#   ■ 실행 방법: python 02_indexing_slicing.py
#   ■ NumPy 설치: pip install numpy
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ═══════════════════════════════════════════════════════════════════════════════
#  1. 기본 인덱싱 - 배열에서 원소 꺼내기
# ═══════════════════════════════════════════════════════════════════════════════
#
#  인덱싱은 "주소"로 집 찾기야!
#  1D 배열: 아파트 호수 (101호, 102호...)
#  2D 배열: 아파트 동+호수 (1동 101호)
#  3D 배열: 아파트 단지+동+호수 (A단지 1동 101호)

print("=" * 70)
print("1. 기본 인덱싱 - 1D, 2D, 3D 배열 접근")
print("=" * 70)

# ── 1D 배열 인덱싱 ──
arr_1d = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
print(f"\n1D 배열: {arr_1d}")
print(f"  arr[0]  = {arr_1d[0]}   ← 첫 번째 (0부터 시작!)")
print(f"  arr[3]  = {arr_1d[3]}   ← 네 번째")
print(f"  arr[-1] = {arr_1d[-1]}  ← 마지막! (뒤에서 첫 번째)")
print(f"  arr[-3] = {arr_1d[-3]}  ← 뒤에서 세 번째")

# 【NumPy】 arr = np.array([10, 20, ..., 100])
#           arr[0], arr[-1]  ← 파이썬과 동일!

# ── 2D 배열 인덱싱 ──
arr_2d = [
    [1,  2,  3,  4],
    [5,  6,  7,  8],
    [9, 10, 11, 12]
]
print(f"\n2D 배열 (3×4):")
for row in arr_2d:
    print(f"  {row}")

print(f"\n  arr[0][1]  = {arr_2d[0][1]}   ← 0행 1열")
print(f"  arr[2][3]  = {arr_2d[2][3]}  ← 2행 3열")
print(f"  arr[-1][0] = {arr_2d[-1][0]}   ← 마지막행 첫열")

# 【NumPy 차이점!】
# 파이썬 리스트: arr[0][1]  (대괄호 두 번)
# NumPy 배열:   arr[0, 1]  (쉼표로 한 번에!)  ← 더 빠르고 편리!

# ── 3D 배열 인덱싱 ──
arr_3d = [
    [[1, 2], [3, 4], [5, 6]],      # 0번째 "페이지"
    [[7, 8], [9, 10], [11, 12]]     # 1번째 "페이지"
]
print(f"\n3D 배열 (2×3×2):")
print(f"  arr[0][1][0] = {arr_3d[0][1][0]}  ← 0페이지, 1행, 0열")
print(f"  arr[1][2][1] = {arr_3d[1][2][1]}  ← 1페이지, 2행, 1열")
print(f"  → 3D는 '책의 페이지-행-열'로 생각하면 돼!")

# 【NumPy】 arr_3d[1, 2, 1]  ← 쉼표 하나로!


# ═══════════════════════════════════════════════════════════════════════════════
#  2. 슬라이싱 - 배열의 일부분 잘라내기
# ═══════════════════════════════════════════════════════════════════════════════
#
#  슬라이싱은 "빵 자르기"야!
#  빵 한 덩어리에서 원하는 만큼 잘라내는 거지!
#  문법: arr[start:stop:step]
#  - start: 시작 위치 (포함)
#  - stop:  끝 위치 (미포함!)  ← 주의!!
#  - step:  건너뛰기 간격

print("\n" + "=" * 70)
print("2. 슬라이싱 - start:stop:step")
print("=" * 70)

arr = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
print(f"\n원본 배열: {arr}")
print(f"인덱스:    0  1  2  3  4  5  6  7  8  9")

print(f"\n  arr[2:5]   = {arr[2:5]}      ← 2번~4번 (5번 미포함!)")
print(f"  arr[:4]    = {arr[:4]}     ← 처음~3번")
print(f"  arr[6:]    = {arr[6:]}     ← 6번~끝")
print(f"  arr[::2]   = {arr[::2]}  ← 처음부터 2칸 간격")
print(f"  arr[1::2]  = {arr[1::2]}  ← 1번부터 2칸 간격")
print(f"  arr[::-1]  = {arr[::-1]}  ← 뒤집기!")
print(f"  arr[-3:]   = {arr[-3:]}      ← 뒤에서 3개")
print(f"  arr[:-2]   = {arr[:-2]}  ← 뒤 2개 빼고")

# ── 2D 슬라이싱 ──
matrix = [
    [1,  2,  3,  4,  5],
    [6,  7,  8,  9,  10],
    [11, 12, 13, 14, 15],
    [16, 17, 18, 19, 20]
]
print(f"\n2D 배열 (4×5):")
for row in matrix:
    print(f"  {row}")

# 순수 파이썬으로 2D 슬라이싱
def slice_2d(mat, row_slice, col_slice):
    """2D 배열의 행과 열을 동시에 슬라이싱"""
    rows = mat[row_slice]
    return [row[col_slice] for row in rows]

sub1 = slice_2d(matrix, slice(0, 2), slice(1, 4))
sub2 = slice_2d(matrix, slice(1, 3), slice(None))  # 모든 열
sub3 = slice_2d(matrix, slice(None), slice(0, 3))   # 모든 행

print(f"\n  arr[0:2, 1:4] (처음 2행, 1~3열):")
for row in sub1:
    print(f"    {row}")

print(f"\n  arr[1:3, :] (1~2행, 모든 열):")
for row in sub2:
    print(f"    {row}")

print(f"\n  arr[:, 0:3] (모든 행, 처음 3열):")
for row in sub3:
    print(f"    {row}")

# 【NumPy】 arr[0:2, 1:4]  ← 쉼표 하나로 행/열 동시 슬라이싱!


# ═══════════════════════════════════════════════════════════════════════════════
#  3. ⚠️ 뷰(View) vs 복사(Copy) - 가장 중요한 주의사항!
# ═══════════════════════════════════════════════════════════════════════════════
#
#  NumPy에서 슬라이싱하면 "뷰"가 생겨!
#  뷰는 "창문"이야 - 같은 집(데이터)을 다른 창문으로 보는 거!
#  창문을 통해 집 안의 가구를 바꾸면, 다른 창문으로 봐도 바뀌어 있어!
#
#  파이썬 리스트는 슬라이싱하면 "복사"가 되지만,
#  NumPy는 슬라이싱하면 "뷰"가 돼! (메모리를 공유함!)

print("\n" + "=" * 70)
print("3. ⚠️ 뷰(View) vs 복사(Copy)")
print("=" * 70)

# ── 파이썬 리스트: 슬라이싱 = 복사! ──
print("\n── 파이썬 리스트 (복사됨 - 안전!) ──")
original_list = [1, 2, 3, 4, 5]
sliced_list = original_list[1:4]  # 복사본!
sliced_list[0] = 999              # 복사본 변경
print(f"  원본: {original_list}      ← 영향 없음!")
print(f"  슬라이스: {sliced_list}  ← 독립적으로 변경됨")

# ── NumPy 배열: 슬라이싱 = 뷰! (시뮬레이션) ──
print("\n── NumPy 배열 (뷰 - 주의!) 시뮬레이션 ──")

class ViewArray:
    """NumPy의 뷰 동작을 시뮬레이션하는 클래스"""
    def __init__(self, data, offset=0, length=None, source=None):
        if source is None:
            self._data = list(data)  # 원본 데이터
            self._source = self._data
        else:
            self._data = None
            self._source = source
        self._offset = offset
        self._length = length if length else len(self._source) - offset

    def __getitem__(self, index):
        if isinstance(index, slice):
            start, stop, step = index.indices(self._length)
            # 뷰 반환! (같은 데이터를 공유)
            return ViewArray(None, offset=self._offset + start,
                           length=stop - start, source=self._source)
        return self._source[self._offset + index]

    def __setitem__(self, index, value):
        self._source[self._offset + index] = value

    def to_list(self):
        return self._source[self._offset:self._offset + self._length]

    def __repr__(self):
        return f"ViewArray({self.to_list()})"

# 뷰 동작 시뮬레이션
original = ViewArray([10, 20, 30, 40, 50])
view = original[1:4]  # 뷰! 데이터 공유!

print(f"  원본: {original}")
print(f"  뷰:   {view}")

view[0] = 999  # 뷰를 변경하면...
print(f"\n  뷰[0]을 999로 변경한 후:")
print(f"  원본: {original}  ← 원본도 변경됨!!! ⚠️")
print(f"  뷰:   {view}")
print(f"\n  → NumPy 슬라이싱은 메모리를 공유하는 '뷰'를 만들어!")
print(f"  → 원본을 보호하려면 .copy()를 사용해야 해!")

# 【NumPy】
# original = np.array([10, 20, 30, 40, 50])
# view = original[1:4]       # 뷰!
# copy = original[1:4].copy() # 복사!
# view.base is original      # True (뷰는 원본을 참조)
# copy.base is None           # None (독립적)


# ═══════════════════════════════════════════════════════════════════════════════
#  4. Boolean 인덱싱 - 조건으로 필터링!
# ═══════════════════════════════════════════════════════════════════════════════
#
#  Boolean 인덱싱은 "시험관" 같아!
#  True/False 마스크로 원하는 것만 골라내는 거야!
#  마치 체에 콩을 거르듯이!

print("\n" + "=" * 70)
print("4. Boolean 인덱싱 - 조건으로 필터링")
print("=" * 70)


# ── 순수 파이썬 구현 ──
def bool_index(arr, mask):
    """Boolean 마스크로 필터링 (NumPy의 arr[mask] 흉내)"""
    return [val for val, m in zip(arr, mask) if m]


def condition_mask(arr, condition_func):
    """조건에 맞는 마스크 생성 (NumPy의 arr > 5 같은 것)"""
    return [condition_func(x) for x in arr]


scores = [85, 42, 93, 67, 78, 55, 98, 31, 72, 88]
print(f"\n성적: {scores}")

# 조건 1: 70점 이상
mask_pass = condition_mask(scores, lambda x: x >= 70)
passed = bool_index(scores, mask_pass)
print(f"\n마스크(>=70): {mask_pass}")
print(f"합격자 점수:  {passed}")

# 조건 2: 60점 이상 AND 90점 미만
mask_mid = [a >= 60 and a < 90 for a in scores]
mid_range = bool_index(scores, mask_mid)
print(f"\n60~89점: {mid_range}")

# 【NumPy】
# scores = np.array([85, 42, 93, 67, 78, 55, 98, 31, 72, 88])
# scores[scores >= 70]                    # → [85, 93, 78, 98, 72, 88]
# scores[(scores >= 60) & (scores < 90)]  # → [85, 67, 78, 72, 88]
#                                          ← & 사용! (and 아님!)
#                                          ← 각 조건에 괄호 필수!

# ── 다중 조건 주의사항 ──
print("\n── 다중 조건 연산자 ──")
print("  파이썬:  a >= 60 and a < 90")
print("  NumPy:   (arr >= 60) & (arr < 90)")
print("          ← & (and), | (or), ~ (not)")
print("          ← 각 조건에 꼭 괄호를 붙여야 해!")
print("          ← and/or 사용하면 에러남!")

# Boolean 인덱싱으로 값 변경
print("\n── Boolean 인덱싱으로 값 변경 ──")
grades = list(scores)  # 복사
for i, s in enumerate(grades):
    if s < 60:
        grades[i] = 60  # 최소 60점으로 올림
print(f"원본:          {scores}")
print(f"최소 60점 적용: {grades}")

# 【NumPy】
# grades = scores.copy()
# grades[grades < 60] = 60  ← 한 줄로 끝!


# ═══════════════════════════════════════════════════════════════════════════════
#  5. 팬시 인덱싱 - 정수 배열로 원하는 것만 골라내기
# ═══════════════════════════════════════════════════════════════════════════════
#
#  팬시 인덱싱은 "쇼핑 리스트"야!
#  "3번, 7번, 1번 상품 주세요!" 하듯이 인덱스 목록으로 골라내기!

print("\n" + "=" * 70)
print("5. 팬시 인덱싱과 np.where()")
print("=" * 70)


def fancy_index(arr, indices):
    """정수 배열로 인덱싱 (팬시 인덱싱 흉내)"""
    return [arr[i] for i in indices]


fruits = ["사과", "바나나", "체리", "딸기", "포도", "키위", "망고"]
print(f"\n과일 목록: {fruits}")

pick = [0, 3, 5]
selected = fancy_index(fruits, pick)
print(f"인덱스 [0, 3, 5]로 선택: {selected}")

# 같은 인덱스를 여러 번 선택할 수도 있어!
repeat_pick = [2, 2, 0, 4, 4, 4]
repeated = fancy_index(fruits, repeat_pick)
print(f"인덱스 [2,2,0,4,4,4]: {repeated}")

# 【NumPy】
# fruits = np.array(["사과", "바나나", "체리", "딸기", "포도", "키위", "망고"])
# fruits[[0, 3, 5]]       # → ["사과", "딸기", "키위"]
# fruits[[2, 2, 0, 4, 4]] # → ["체리", "체리", "사과", "포도", "포도"]


# ── np.where() 구현 ──
def py_where(condition, x=None, y=None):
    """조건이 True인 인덱스 반환 / 조건에 따라 값 선택

    np.where(조건)        → True인 위치(인덱스) 반환
    np.where(조건, a, b)  → True면 a, False면 b
    """
    if x is None and y is None:
        # 인덱스만 반환
        return [i for i, c in enumerate(condition) if c]
    else:
        # 조건에 따라 값 선택
        return [x_val if c else y_val
                for c, x_val, y_val in zip(condition, x, y)]


temperatures = [35, 28, 42, 15, 33, 8, 39, 22]
print(f"\n기온: {temperatures}")

# 30도 이상인 위치 찾기
hot_mask = [t >= 30 for t in temperatures]
hot_indices = py_where(hot_mask)
print(f"30도 이상 위치: {hot_indices}")
print(f"30도 이상 기온: {[temperatures[i] for i in hot_indices]}")

# 조건에 따라 라벨 붙이기
labels = py_where(hot_mask, ["더움"] * len(temperatures), ["쾌적"] * len(temperatures))
print(f"라벨: {labels}")

# 【NumPy】
# temp = np.array([35, 28, 42, 15, 33, 8, 39, 22])
# np.where(temp >= 30)                        # → (array([0, 2, 4, 6]),)
# np.where(temp >= 30, "더움", "쾌적")        # → ["더움", "쾌적", "더움", ...]


# ═══════════════════════════════════════════════════════════════════════════════
#  6. 마스킹 - 잘못된 데이터 처리
# ═══════════════════════════════════════════════════════════════════════════════
#
#  측정 데이터에는 가끔 잘못된 값이 있어!
#  센서 고장, 입력 실수 등... 이런 값을 "마스킹"해서 무시할 수 있어!

print("\n" + "=" * 70)
print("6. 마스킹 - 잘못된 데이터 처리")
print("=" * 70)


class MaskedArray:
    """np.ma.masked_array 흉내 - 특정 값을 마스킹"""
    def __init__(self, data, mask=None, fill_value=-999):
        self.data = list(data)
        self.mask = mask if mask else [False] * len(data)
        self.fill_value = fill_value

    def mean(self):
        """마스킹된 값을 제외하고 평균 계산"""
        valid = [d for d, m in zip(self.data, self.mask) if not m]
        if not valid:
            return float('nan')
        return sum(valid) / len(valid)

    def count(self):
        """유효한 값의 개수"""
        return sum(1 for m in self.mask if not m)

    def filled(self, fill_value=None):
        """마스킹된 값을 fill_value로 채우기"""
        fv = fill_value if fill_value is not None else self.fill_value
        return [d if not m else fv for d, m in zip(self.data, self.mask)]

    def __repr__(self):
        items = []
        for d, m in zip(self.data, self.mask):
            items.append("--" if m else str(d))
        return f"MaskedArray([{', '.join(items)}])"


# 온도 센서 데이터 (일부 고장)
raw_temps = [22.5, 23.1, -999, 24.0, 22.8, -999, 23.5, 25.0]
print(f"\n원시 온도 데이터: {raw_temps}")

# -999를 마스킹
sensor_mask = [t == -999 for t in raw_temps]
masked_temps = MaskedArray(raw_temps, mask=sensor_mask)

print(f"마스킹 후:       {masked_temps}")
print(f"유효 데이터 수:  {masked_temps.count()}")
print(f"평균 (마스킹 제외): {masked_temps.mean():.1f}°C")
print(f"0으로 채우기:    {masked_temps.filled(0)}")

# 마스킹 없이 평균을 구하면?
wrong_mean = sum(raw_temps) / len(raw_temps)
print(f"\n마스킹 없이 평균: {wrong_mean:.1f}°C  ← -999 때문에 완전 틀림!")
print(f"마스킹 하고 평균: {masked_temps.mean():.1f}°C  ← 정확!")

# 【NumPy】
# import numpy.ma as ma
# temps = np.array([22.5, 23.1, -999, 24.0, 22.8, -999, 23.5, 25.0])
# masked = ma.masked_equal(temps, -999)   # -999인 값 마스킹
# masked.mean()                            # 마스킹 제외 평균
# masked.filled(0)                         # 마스킹된 곳을 0으로


# ═══════════════════════════════════════════════════════════════════════════════
#  7. 슬라이싱 vs 복사 - 엣지 케이스 모음
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("7. 주의! 뷰 vs 복사 엣지 케이스들")
print("=" * 70)

print("""
  ┌─────────────────────────────────────────────────────┐
  │              NumPy에서 뷰 vs 복사 규칙              │
  ├─────────────────────────────────────────────────────┤
  │ 뷰(원본 변경됨):                                   │
  │   • 슬라이싱        arr[1:4]                       │
  │   • reshape         arr.reshape(2, 3)              │
  │   • transpose       arr.T                          │
  │   • ravel()         (가능할 때)                     │
  │                                                     │
  │ 복사(독립적):                                       │
  │   • 팬시 인덱싱     arr[[0, 2, 4]]                 │
  │   • Boolean 인덱싱  arr[arr > 5]                   │
  │   • flatten()       항상 복사                       │
  │   • .copy()         명시적 복사                     │
  └─────────────────────────────────────────────────────┘
""")

# 엣지 케이스 1: 팬시 인덱싱은 복사!
print("── 엣지 케이스 1: 팬시 인덱싱은 복사! ──")
original = [10, 20, 30, 40, 50]
fancy_copy = [original[i] for i in [1, 3]]  # 팬시 인덱싱 → 복사
fancy_copy[0] = 999
print(f"  원본: {original}  ← 변경 안 됨!")
print(f"  팬시: {fancy_copy}")
print(f"  → 팬시 인덱싱은 항상 복사본을 만들어!")

# 엣지 케이스 2: Boolean 인덱싱도 복사!
print("\n── 엣지 케이스 2: Boolean 인덱싱도 복사! ──")
data = [1, 2, 3, 4, 5, 6]
mask = [x > 3 for x in data]
filtered = [d for d, m in zip(data, mask) if m]  # Boolean 인덱싱 → 복사
filtered[0] = 999
print(f"  원본: {data}  ← 변경 안 됨!")
print(f"  필터: {filtered}")

# 엣지 케이스 3: 안전하게 복사하기
print("\n── copy() 사용하기 ──")
original = [10, 20, 30, 40, 50]
safe_copy = original[:]  # 파이썬 리스트 복사 방법
safe_copy[0] = 999
print(f"  원본: {original}")
print(f"  복사: {safe_copy}")
print(f"  → 원본이 안전해!")

# 【NumPy】
# import copy
# safe = original.copy()      # 또는 np.copy(original)
# safe = original[1:4].copy() # 슬라이스도 copy() 하면 안전!


# ═══════════════════════════════════════════════════════════════════════════════
#  8. 실습: 성적 데이터 조건별 필터링
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("실습: 학교 성적 데이터 분석")
print("=" * 70)

import random
random.seed(42)

# 30명 학생의 성적 데이터
student_count = 30
names = [f"학생{i+1:02d}" for i in range(student_count)]
math_scores = [random.randint(20, 100) for _ in range(student_count)]
eng_scores = [random.randint(30, 100) for _ in range(student_count)]

print(f"\n총 {student_count}명 학생 성적:")
print(f"수학 평균: {sum(math_scores)/len(math_scores):.1f}")
print(f"영어 평균: {sum(eng_scores)/len(eng_scores):.1f}")

# 과제 1: 수학 80점 이상인 학생
print("\n── 과제 1: 수학 80점 이상 ──")
math_high = [(names[i], math_scores[i]) for i in range(student_count) if math_scores[i] >= 80]
print(f"  {len(math_high)}명: {math_high}")

# 【NumPy】 names[math_scores >= 80]

# 과제 2: 수학 AND 영어 모두 70점 이상
print("\n── 과제 2: 수학 & 영어 모두 70점 이상 ──")
both_good = [(names[i], math_scores[i], eng_scores[i])
             for i in range(student_count)
             if math_scores[i] >= 70 and eng_scores[i] >= 70]
print(f"  {len(both_good)}명:")
for name, m, e in both_good:
    print(f"    {name}: 수학 {m}, 영어 {e}")

# 【NumPy】 names[(math >= 70) & (eng >= 70)]

# 과제 3: 수학 OR 영어 중 하나라도 90점 이상
print("\n── 과제 3: 수학 또는 영어 90점 이상 ──")
any_excellent = [(names[i], math_scores[i], eng_scores[i])
                 for i in range(student_count)
                 if math_scores[i] >= 90 or eng_scores[i] >= 90]
print(f"  {len(any_excellent)}명:")
for name, m, e in any_excellent:
    print(f"    {name}: 수학 {m}, 영어 {e}")

# 【NumPy】 names[(math >= 90) | (eng >= 90)]

# 과제 4: 등급 매기기 (where 활용)
print("\n── 과제 4: 수학 등급 매기기 ──")
def assign_grade(score):
    if score >= 90: return 'A'
    elif score >= 80: return 'B'
    elif score >= 70: return 'C'
    elif score >= 60: return 'D'
    else: return 'F'

grades = [assign_grade(s) for s in math_scores]
grade_counts = {g: grades.count(g) for g in ['A', 'B', 'C', 'D', 'F']}
print(f"  등급 분포: {grade_counts}")

# 【NumPy】
# grades = np.where(math >= 90, 'A',
#          np.where(math >= 80, 'B',
#          np.where(math >= 70, 'C',
#          np.where(math >= 60, 'D', 'F'))))

# 과제 5: 상위 5명, 하위 5명
print("\n── 과제 5: 수학 상위/하위 5명 ──")
sorted_indices = sorted(range(student_count), key=lambda i: math_scores[i], reverse=True)
print(f"  상위 5명: {[(names[i], math_scores[i]) for i in sorted_indices[:5]]}")
print(f"  하위 5명: {[(names[i], math_scores[i]) for i in sorted_indices[-5:]]}")

# 【NumPy】
# top5 = np.argsort(math_scores)[-5:][::-1]   # argsort: 정렬된 인덱스
# bot5 = np.argsort(math_scores)[:5]


# ═══════════════════════════════════════════════════════════════════════════════
#  핵심 정리
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("핵심 정리")
print("=" * 70)
print("""
  1. 인덱싱: arr[행, 열] (NumPy는 쉼표 한 번!)
  2. 슬라이싱: arr[start:stop:step] (stop은 미포함!)
  3. ⚠️ 슬라이싱 = 뷰(원본 공유)! copy()로 안전하게!
  4. Boolean 인덱싱: arr[arr > 5]
     - 다중 조건: & (and), | (or), ~ (not) + 괄호 필수!
  5. 팬시 인덱싱: arr[[0, 2, 4]] (인덱스 목록)
     - 팬시/Boolean 인덱싱은 항상 복사본!
  6. np.where(조건): True인 위치 찾기
     np.where(조건, a, b): True면 a, False면 b
  7. 마스킹: 잘못된 데이터를 제외하고 계산
""")
