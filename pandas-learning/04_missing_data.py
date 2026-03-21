# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   Pandas 학습 04단계: 결측값 처리 (Missing Data)
#   ─ NaN 이해, isna/notna, fillna, dropna, interpolate ─
#   ■ 실행 방법: python 04_missing_data.py
#   ■ Pandas 설치: pip install pandas
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# =========================================================================
#  결측값(Missing Value)이 뭐예요?
# =========================================================================
#
#  현실의 데이터는 완벽하지 않아요!
#  - 설문조사에서 답하지 않은 문항
#  - 센서가 고장나서 기록되지 않은 온도
#  - 전학 온 학생의 이전 성적이 없는 경우
#
#  이런 "빈 칸"을 결측값(Missing Value)이라고 해요.
#  Pandas에서는 NaN (Not a Number)으로 표현합니다.
# =========================================================================

print("=" * 70)
print(" 04단계: 결측값 처리 (Missing Data)")
print("=" * 70)

# 파이썬에서 "없음"을 나타내는 것들
import math

print("\n" + "─" * 70)
print(" 1. '없음'을 표현하는 세 가지")
print("─" * 70)

print("""
  파이썬과 Pandas에서 "값이 없다"를 나타내는 방법:

  1) None     — 파이썬의 "아무것도 없음"
     - type: NoneType
     - 용도: 일반 파이썬 객체

  2) float('nan') 또는 math.nan — "숫자가 아님"
     - type: float
     - 특이점: nan != nan (자기 자신과도 같지 않아요!)
     - 용도: Pandas가 내부적으로 사용

  3) pd.NA    — Pandas 1.0+에서 도입
     - 정수, 불리언 등에서도 결측값 표현 가능
     - 용도: 최신 nullable 타입

  Pandas에서는 이 셋 모두 "결측값"으로 인식합니다!
""")

# NaN의 특이한 성질
nan = float('nan')
print("  [NaN의 특이한 성질]")
print(f"  nan == nan → {nan == nan}  (자기 자신과도 같지 않아요!)")
print(f"  nan != nan → {nan != nan}  (항상 True)")
print(f"  math.isnan(nan) → {math.isnan(nan)}  (이걸로 확인해야 해요!)")
print(f"  None == None → {None is None}  (None은 is로 비교)")


# ─── 결측값 처리용 DataFrame ───

NaN = float('nan')  # 결측값 표기

class MissingDF:
    """결측값 처리 학습용 DataFrame"""

    def __init__(self, data, index=None):
        self._columns = list(data.keys())
        first_key = self._columns[0]
        n = len(data[first_key])
        self._data = {col: list(data[col]) for col in self._columns}
        self._index = list(index) if index else list(range(n))

    @property
    def shape(self):
        return (len(self._index), len(self._columns))

    def _is_na(self, value):
        """값이 결측값인지 확인"""
        if value is None:
            return True
        if isinstance(value, float) and math.isnan(value):
            return True
        return False

    def display(self, title=None):
        if title:
            print(f"\n  [{title}]")
        idx_w = max(len(str(i)) for i in self._index) + 2
        col_w = {}
        for c in self._columns:
            w = len(str(c))
            for r in range(len(self._index)):
                val = self._data[c][r]
                display_val = 'NaN' if self._is_na(val) else str(val)
                w = max(w, len(display_val))
            col_w[c] = w + 2

        header = " " * idx_w + "".join(f"{c:>{col_w[c]}}" for c in self._columns)
        print(header)
        print("  " + "─" * (len(header) - 2))
        for ri, idx in enumerate(self._index):
            line = f"{str(idx):<{idx_w}}"
            for c in self._columns:
                val = self._data[c][ri]
                display_val = 'NaN' if self._is_na(val) else str(val)
                line += f"{display_val:>{col_w[c]}}"
            print(line)

    def copy(self):
        new_data = {col: list(vals) for col, vals in self._data.items()}
        return MissingDF(new_data, index=list(self._index))

    # ── isna(): 결측값 확인 ──
    def isna(self, col=None):
        """
        결측값이면 True, 아니면 False.

        Pandas에서:
          df.isna()         → 전체 DataFrame에 대해
          df['열'].isna()   → 특정 열에 대해
          df.isnull()       → isna()와 동일 (별칭)
        """
        if col:
            return [self._is_na(v) for v in self._data[col]]
        result = {}
        for c in self._columns:
            result[c] = [self._is_na(v) for v in self._data[c]]
        return result

    # ── notna(): 유효값 확인 ──
    def notna(self, col=None):
        """
        유효값이면 True, 결측값이면 False.

        Pandas에서:
          df.notna()         → 전체
          df['열'].notna()   → 특정 열
          df.notnull()       → notna()와 동일 (별칭)
        """
        if col:
            return [not self._is_na(v) for v in self._data[col]]
        result = {}
        for c in self._columns:
            result[c] = [not self._is_na(v) for v in self._data[c]]
        return result

    # ── 결측값 개수 세기 ──
    def na_count(self):
        """각 열의 결측값 개수"""
        counts = {}
        for c in self._columns:
            counts[c] = sum(1 for v in self._data[c] if self._is_na(v))
        return counts

    def info(self):
        """DataFrame 정보 (결측값 포함)"""
        print(f"\n  <MissingDF 정보>")
        print(f"  행: {self.shape[0]}, 열: {self.shape[1]}")
        na_counts = self.na_count()
        for c in self._columns:
            valid = self.shape[0] - na_counts[c]
            print(f"    {c:>10}: {valid}/{self.shape[0]} 유효 ({na_counts[c]}개 결측)")

    # ── fillna(): 결측값 채우기 ──
    def fillna(self, col=None, value=None, method=None):
        """
        결측값을 지정한 값으로 채우기.

        Pandas에서:
          df.fillna(0)                    → 모든 NaN을 0으로
          df['열'].fillna(df['열'].mean()) → 평균으로 채우기
          df.fillna(method='ffill')       → 앞의 값으로 채우기
          df.fillna(method='bfill')       → 뒤의 값으로 채우기
          df.fillna({'수학': 0, '영어': 50}) → 열별로 다른 값
        """
        result = self.copy()

        if col:
            cols_to_fill = [col]
        else:
            cols_to_fill = self._columns

        for c in cols_to_fill:
            if method == 'ffill':
                # Forward fill: 앞의 유효한 값으로 채우기
                last_valid = None
                for i in range(len(result._data[c])):
                    if self._is_na(result._data[c][i]):
                        if last_valid is not None:
                            result._data[c][i] = last_valid
                    else:
                        last_valid = result._data[c][i]

            elif method == 'bfill':
                # Backward fill: 뒤의 유효한 값으로 채우기
                next_valid = None
                for i in range(len(result._data[c]) - 1, -1, -1):
                    if self._is_na(result._data[c][i]):
                        if next_valid is not None:
                            result._data[c][i] = next_valid
                    else:
                        next_valid = result._data[c][i]

            elif value is not None:
                # 지정한 값으로 채우기
                if isinstance(value, dict):
                    fill_val = value.get(c, None)
                else:
                    fill_val = value
                if fill_val is not None:
                    for i in range(len(result._data[c])):
                        if self._is_na(result._data[c][i]):
                            result._data[c][i] = fill_val
        return result

    # ── dropna(): 결측값 행/열 삭제 ──
    def dropna(self, axis=0, how='any', thresh=None, subset=None):
        """
        결측값이 있는 행 또는 열 삭제.

        Pandas에서:
          df.dropna()                → NaN 있는 행 삭제 (any)
          df.dropna(how='all')       → 모든 값이 NaN인 행만 삭제
          df.dropna(axis=1)          → NaN 있는 열 삭제
          df.dropna(thresh=3)        → 유효값 3개 미만인 행 삭제
          df.dropna(subset=['수학']) → 수학 열에 NaN 있는 행 삭제
        """
        result_data = {c: list(self._data[c]) for c in self._columns}
        result_idx = list(self._index)

        if axis == 0:  # 행 삭제
            check_cols = subset if subset else self._columns
            rows_to_keep = []

            for i in range(len(self._index)):
                na_in_row = sum(1 for c in check_cols if self._is_na(self._data[c][i]))
                valid_in_row = len(check_cols) - na_in_row

                if thresh is not None:
                    if valid_in_row >= thresh:
                        rows_to_keep.append(i)
                elif how == 'any':
                    if na_in_row == 0:
                        rows_to_keep.append(i)
                elif how == 'all':
                    if na_in_row < len(check_cols):
                        rows_to_keep.append(i)

            new_data = {}
            for c in self._columns:
                new_data[c] = [self._data[c][i] for i in rows_to_keep]
            new_idx = [self._index[i] for i in rows_to_keep]
            return MissingDF(new_data, index=new_idx)

        else:  # 열 삭제 (axis=1)
            cols_to_keep = []
            for c in self._columns:
                na_count = sum(1 for v in self._data[c] if self._is_na(v))
                if how == 'any' and na_count == 0:
                    cols_to_keep.append(c)
                elif how == 'all' and na_count < len(self._index):
                    cols_to_keep.append(c)
            new_data = {c: list(self._data[c]) for c in cols_to_keep}
            return MissingDF(new_data, index=list(self._index))

    # ── interpolate(): 보간 ──
    def interpolate(self, col, method='linear'):
        """
        결측값을 주변 값으로부터 추정 (보간).

        Pandas에서:
          df['열'].interpolate()              → 선형 보간
          df['열'].interpolate(method='time')  → 시간 기반 보간
        """
        values = list(self._data[col])
        n = len(values)

        if method == 'linear':
            # 선형 보간: 양쪽 유효값 사이를 직선으로 이어서 추정
            i = 0
            while i < n:
                if self._is_na(values[i]):
                    # NaN 시작 지점 찾기
                    start = i - 1  # 이전 유효값
                    while i < n and self._is_na(values[i]):
                        i += 1
                    end = i  # 다음 유효값

                    if start >= 0 and end < n:
                        # 양쪽 값 사이를 직선으로 보간
                        gap = end - start
                        for j in range(start + 1, end):
                            ratio = (j - start) / gap
                            values[j] = round(
                                values[start] + (values[end] - values[start]) * ratio, 1
                            )
                else:
                    i += 1

        return values


# ─── 테스트 데이터: 결측값이 있는 설문 데이터 ───

survey = MissingDF({
    '이름':   ['민수', '영희', '철수', '지영', '하늘', '서준', '다은'],
    '나이':   [12, 13, NaN, 12, 13, NaN, 11],
    '수학':   [90, NaN, 65, 98, NaN, 85, 45],
    '영어':   [78, 95, NaN, NaN, 85, 60, 92],
    '만족도': [4, 5, NaN, 3, NaN, NaN, 4],
})

survey.display("결측값이 있는 설문 데이터")


# ─────────────────────────────────────────────────────────────────────────
# 2. 결측값 확인하기 — isna(), notna(), info()
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 2. 결측값 확인하기")
print("─" * 70)

# isna() — True면 결측값
print("\n[isna()] 수학 열의 결측값 여부:")
math_na = survey.isna('수학')
print(f"  수학 값:   {[v if not survey._is_na(v) else 'NaN' for v in survey._data['수학']]}")
print(f"  isna:     {math_na}")
# ── Pandas: df['수학'].isna() ──

# 전체 결측값 확인
print("\n[isna()] 전체 결측값 현황:")
all_na = survey.isna()
for col, mask in all_na.items():
    na_positions = [i for i, v in enumerate(mask) if v]
    if na_positions:
        print(f"  {col}: {sum(mask)}개 결측 (위치: {na_positions})")
    else:
        print(f"  {col}: 결측 없음")
# ── Pandas: df.isna().sum() ──

# info() — 한눈에 보기
survey.info()
# ── Pandas: df.info() ──

# 결측값 비율 계산
print("\n[결측값 비율]")
na_counts = survey.na_count()
total = survey.shape[0]
for col, count in na_counts.items():
    pct = count / total * 100
    bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
    print(f"  {col:>6}: {bar} {pct:.0f}% ({count}/{total})")
# ── Pandas: (df.isna().sum() / len(df) * 100).round(1) ──


# ─────────────────────────────────────────────────────────────────────────
# 3. fillna() — 결측값 채우기
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 3. fillna() — 결측값 채우기")
print("─" * 70)

# 방법 1: 고정값으로 채우기
print("\n[fillna] 수학 결측값을 0으로 채우기:")
filled = survey.fillna(col='수학', value=0)
filled.display("수학 NaN → 0")
# ── Pandas: df['수학'].fillna(0) ──

# 방법 2: 평균으로 채우기
print("\n[fillna] 수학 결측값을 평균으로 채우기:")
valid_math = [v for v in survey._data['수학'] if not survey._is_na(v)]
math_mean = round(sum(valid_math) / len(valid_math), 1)
print(f"  수학 평균 (결측 제외): {math_mean}")
filled_mean = survey.fillna(col='수학', value=math_mean)
filled_mean.display("수학 NaN → 평균")
# ── Pandas: df['수학'].fillna(df['수학'].mean()) ──

# 방법 3: 전방 채우기 (ffill) — 바로 앞의 값으로!
print("\n[fillna] 만족도를 전방 채우기 (ffill):")
print("  원리: NaN을 바로 위(앞)의 유효한 값으로 채워요")
print("  [4, 5, NaN, 3, NaN, NaN, 4]")
print("  [4, 5, →5,  3, →3,  →3,  4]")
filled_ffill = survey.fillna(col='만족도', method='ffill')
print(f"  결과: {filled_ffill._data['만족도']}")
# ── Pandas: df['만족도'].fillna(method='ffill') ──
# ── 또는: df['만족도'].ffill() ──  (Pandas 2.0+)

# 방법 4: 후방 채우기 (bfill) — 바로 뒤의 값으로!
print("\n[fillna] 만족도를 후방 채우기 (bfill):")
print("  원리: NaN을 바로 아래(뒤)의 유효한 값으로 채워요")
print("  [4, 5, NaN, 3, NaN, NaN, 4]")
print("  [4, 5, ←3,  3, ←4,  ←4,  4]")
filled_bfill = survey.fillna(col='만족도', method='bfill')
print(f"  결과: {filled_bfill._data['만족도']}")
# ── Pandas: df['만족도'].fillna(method='bfill') ──
# ── 또는: df['만족도'].bfill() ──  (Pandas 2.0+)

# 방법 5: 열별로 다른 값으로 채우기
print("\n[fillna] 열별로 다른 값으로 채우기:")
filled_multi = survey.copy()
filled_multi = filled_multi.fillna(value={'수학': 0, '영어': 0, '만족도': 3})
filled_multi.display("열별 다른 기본값")
# ── Pandas: df.fillna({'수학': 0, '영어': 0, '만족도': 3}) ──

print("""
  💡 fillna 전략 비교:
  ┌───────────────┬────────────────────────────────────┐
  │ 방법          │ 언제 사용?                         │
  ├───────────────┼────────────────────────────────────┤
  │ 고정값 (0)    │ NaN이 0을 의미할 때                │
  │ 평균/중앙값   │ 일반적인 수치 데이터               │
  │ 최빈값        │ 범주형 데이터                      │
  │ ffill (전방)  │ 시계열: 이전 상태 유지             │
  │ bfill (후방)  │ 시계열: 다음 상태 참조             │
  │ interpolate   │ 연속적인 수치: 추세 유지           │
  └───────────────┴────────────────────────────────────┘
""")


# ─────────────────────────────────────────────────────────────────────────
# 4. dropna() — 결측값 행/열 삭제
# ─────────────────────────────────────────────────────────────────────────

print("─" * 70)
print(" 4. dropna() — 결측값 행/열 삭제")
print("─" * 70)

survey.display("원본 (참고)")

# how='any': NaN이 하나라도 있으면 삭제 (기본값)
dropped_any = survey.dropna(how='any')
dropped_any.display("dropna(how='any') — NaN 있으면 행 삭제")
print(f"  → {survey.shape[0]}행 중 {dropped_any.shape[0]}행만 남음!")
# ── Pandas: df.dropna() ──

# how='all': 모든 값이 NaN인 행만 삭제
dropped_all = survey.dropna(how='all')
dropped_all.display("dropna(how='all') — 모두 NaN인 행만 삭제")
# ── Pandas: df.dropna(how='all') ──

# thresh: 최소 유효값 개수 지정
dropped_thresh = survey.dropna(thresh=4)
dropped_thresh.display("dropna(thresh=4) — 유효값 4개 이상인 행만")
# ── Pandas: df.dropna(thresh=4) ──

# subset: 특정 열 기준으로만
dropped_subset = survey.dropna(subset=['수학', '영어'])
dropped_subset.display("dropna(subset=['수학','영어']) — 수학/영어 기준")
# ── Pandas: df.dropna(subset=['수학', '영어']) ──

# axis=1: 열 삭제
dropped_cols = survey.dropna(axis=1)
dropped_cols.display("dropna(axis=1) — NaN 있는 열 삭제")
# ── Pandas: df.dropna(axis=1) ──

print("""
  ⚠️ dropna() 주의사항:
  ┌──────────────────────────────────────────────┐
  │ how='any'는 데이터를 너무 많이 삭제할 수 있어요! │
  │                                                │
  │ 10개 열, 1000행 데이터에서                      │
  │ 각 열에 10%씩 NaN이 있으면...                   │
  │ → any로 dropna하면 약 65%의 행이 삭제됩니다!    │
  │                                                │
  │ 대안: thresh 사용 또는 특정 열만 fillna         │
  └──────────────────────────────────────────────┘
""")


# ─────────────────────────────────────────────────────────────────────────
# 5. interpolate() — 보간법
# ─────────────────────────────────────────────────────────────────────────

print("─" * 70)
print(" 5. interpolate() — 보간법")
print("─" * 70)

print("""
  보간(interpolation)이란?
  → 주변 값들로부터 결측값을 "추정"하는 방법

  선형 보간 예시:
  온도: [10, NaN, NaN, 40]
  →     [10, 20,  30,  40]  (10과 40 사이를 균등하게!)

  시간순 데이터(온도, 주가 등)에 특히 유용해요!
""")

# 온도 데이터로 보간 시연
temp_data = MissingDF({
    '시간': ['06시', '08시', '10시', '12시', '14시', '16시', '18시'],
    '온도': [5.0, NaN, NaN, 20.0, NaN, 15.0, 10.0],
})

temp_data.display("보간 전 온도 데이터")

# 선형 보간
interpolated = temp_data.interpolate('온도', method='linear')
print(f"\n  보간 전: {[v if not temp_data._is_na(v) else 'NaN' for v in temp_data._data['온도']]}")
print(f"  보간 후: {interpolated}")

# 시각화 (ASCII)
print("\n  [온도 변화 그래프 — ASCII]")
max_temp = max(v for v in interpolated if not math.isnan(v) if isinstance(v, (int, float)))
for i, (time, temp) in enumerate(zip(temp_data._data['시간'], interpolated)):
    if temp is not None and not (isinstance(temp, float) and math.isnan(temp)):
        bar_len = int(temp / max_temp * 30)
        was_nan = temp_data._is_na(temp_data._data['온도'][i])
        marker = " (보간)" if was_nan else ""
        print(f"  {time} │{'▓' * bar_len} {temp}°C{marker}")

# ── Pandas로 하면? ──
# df['온도'].interpolate()                  → 선형 보간
# df['온도'].interpolate(method='quadratic') → 2차 다항식 보간
# df['온도'].interpolate(method='time')      → 시간 가중 보간


# ─────────────────────────────────────────────────────────────────────────
# 6. 결측값 전략 선택 가이드
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 6. 결측값 전략 선택 가이드")
print("─" * 70)

print("""
  결측값을 발견했을 때, 어떤 전략을 쓸까요?

  ┌─ 1단계: 결측값 확인 ──────────────────────────────────┐
  │  df.isna().sum()           → 열별 결측값 수            │
  │  df.isna().sum() / len(df) → 열별 결측값 비율          │
  │  df.info()                 → 전체 요약                 │
  └────────────────────────────────────────────────────────┘

  ┌─ 2단계: 결측값 비율에 따른 전략 ──────────────────────┐
  │                                                       │
  │  < 5%:   dropna()로 행 삭제 (데이터 손실 적음)        │
  │  5~30%:  fillna()로 적절한 값으로 채우기              │
  │  > 30%:  해당 열 자체를 삭제 고려                     │
  │          또는 결측 여부를 새 특성으로 만들기           │
  │                                                       │
  └────────────────────────────────────────────────────────┘

  ┌─ 3단계: 데이터 유형별 채우기 전략 ───────────────────┐
  │                                                       │
  │  수치형 (나이, 점수 등):                              │
  │    - 평균(mean): 정규분포일 때                        │
  │    - 중앙값(median): 이상치가 있을 때                 │
  │    - interpolate(): 시계열일 때                       │
  │                                                       │
  │  범주형 (성별, 학년 등):                              │
  │    - 최빈값(mode): 가장 많은 값으로                   │
  │    - '미응답' 카테고리 추가                            │
  │                                                       │
  │  시계열 (날짜별 데이터):                              │
  │    - ffill: 이전 상태 유지                            │
  │    - bfill: 다음 상태 참조                            │
  │    - interpolate: 추세 유지                           │
  │                                                       │
  └────────────────────────────────────────────────────────┘
""")


# ─────────────────────────────────────────────────────────────────────────
# ★ 실습: 불완전한 설문 데이터 정제
# ─────────────────────────────────────────────────────────────────────────

print("═" * 70)
print(" ★ 실습: 불완전한 설문 데이터 정제")
print("═" * 70)

# 학교 건강검진 설문 데이터 (결측값 포함)
health = MissingDF({
    '이름':   ['민수', '영희', '철수', '지영', '하늘', '서준', '다은', '예린'],
    '학년':   [3, 3, NaN, 3, 2, NaN, 1, 2],
    '키':     [155.2, 160.5, NaN, 158.0, 148.3, NaN, 140.0, 152.7],
    '몸무게': [45.0, 52.3, NaN, 48.5, NaN, 42.0, 35.5, NaN],
    '시력':   [1.0, NaN, 0.8, 1.2, NaN, 0.5, NaN, 1.0],
    '혈액형': ['A', 'B', NaN, 'O', 'AB', NaN, 'A', 'B'],
    '운동시간': [3, NaN, 2, NaN, 5, 1, NaN, 4],
})

health.display("원본 건강검진 데이터")
health.info()

# 1단계: 결측값 현황 분석
print("\n── 1단계: 결측값 현황 분석 ──")
na_counts = health.na_count()
total_rows = health.shape[0]
print("\n  열별 결측값:")
for col, count in na_counts.items():
    pct = count / total_rows * 100
    status = "⚠️ 주의" if pct > 20 else "✅ 양호" if pct <= 10 else "⚡ 보통"
    print(f"    {col:>8}: {count}개 ({pct:.0f}%) {status}")

# 2단계: 전략 수립 및 처리
print("\n── 2단계: 결측값 처리 ──")

cleaned = health.copy()

# 학년: 최빈값으로 채우기 (범주형)
valid_grades = [v for v in cleaned._data['학년'] if not cleaned._is_na(v)]
mode_grade = max(set(valid_grades), key=valid_grades.count)
print(f"\n  학년: 최빈값 {mode_grade}로 채우기")
cleaned = cleaned.fillna(col='학년', value=mode_grade)
# ── Pandas: df['학년'].fillna(df['학년'].mode()[0]) ──

# 키/몸무게: 평균으로 채우기 (수치형)
valid_heights = [v for v in cleaned._data['키'] if not cleaned._is_na(v)]
mean_height = round(sum(valid_heights) / len(valid_heights), 1)
print(f"  키: 평균 {mean_height}cm로 채우기")
cleaned = cleaned.fillna(col='키', value=mean_height)

valid_weights = [v for v in cleaned._data['몸무게'] if not cleaned._is_na(v)]
mean_weight = round(sum(valid_weights) / len(valid_weights), 1)
print(f"  몸무게: 평균 {mean_weight}kg로 채우기")
cleaned = cleaned.fillna(col='몸무게', value=mean_weight)
# ── Pandas: df['키'].fillna(df['키'].mean()) ──

# 시력: 보간 (연속 수치)
print("  시력: 선형 보간으로 채우기")
interpolated_sight = cleaned.interpolate('시력')
cleaned._data['시력'] = interpolated_sight
# ── Pandas: df['시력'].interpolate() ──

# 혈액형: '미확인'으로 채우기 (범주형)
print("  혈액형: '미확인'으로 채우기")
cleaned = cleaned.fillna(col='혈액형', value='미확인')
# ── Pandas: df['혈액형'].fillna('미확인') ──

# 운동시간: 중앙값으로 채우기
valid_exercise = sorted(v for v in cleaned._data['운동시간'] if not cleaned._is_na(v))
median_exercise = valid_exercise[len(valid_exercise) // 2]
print(f"  운동시간: 중앙값 {median_exercise}시간으로 채우기")
cleaned = cleaned.fillna(col='운동시간', value=median_exercise)
# ── Pandas: df['운동시간'].fillna(df['운동시간'].median()) ──

# 3단계: 결과 확인
print("\n── 3단계: 정제 결과 ──")
cleaned.display("정제 완료된 건강검진 데이터")
cleaned.info()

# 4단계: 기본 통계
print("\n── 4단계: 기본 통계 ──")
for col in ['키', '몸무게', '시력', '운동시간']:
    vals = [v for v in cleaned._data[col] if isinstance(v, (int, float))]
    if vals:
        avg = sum(vals) / len(vals)
        print(f"  {col:>8}: 평균={avg:.1f}, 최소={min(vals)}, 최대={max(vals)}")


# ─────────────────────────────────────────────────────────────────────────
# 정리
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "═" * 70)
print(" 정리: 결측값 처리 도구 모음")
print("═" * 70)

print("""
  ┌────────────────┬──────────────────────────────────────┐
  │ 작업           │ Pandas 코드                          │
  ├────────────────┼──────────────────────────────────────┤
  │ 결측값 확인    │ df.isna() / df.isnull()              │
  │ 유효값 확인    │ df.notna() / df.notnull()            │
  │ 결측값 수      │ df.isna().sum()                      │
  │ 결측값 비율    │ df.isna().mean() * 100               │
  │ 정보 요약      │ df.info()                            │
  │                │                                      │
  │ 값으로 채우기  │ df.fillna(값)                        │
  │ 평균으로 채우기│ df.fillna(df.mean())                 │
  │ 전방 채우기    │ df.ffill() / fillna(method='ffill')  │
  │ 후방 채우기    │ df.bfill() / fillna(method='bfill')  │
  │ 보간           │ df.interpolate()                     │
  │                │                                      │
  │ 행 삭제        │ df.dropna()                          │
  │ 열 삭제        │ df.dropna(axis=1)                    │
  │ 최소 유효값    │ df.dropna(thresh=N)                  │
  │ 특정 열 기준   │ df.dropna(subset=['열'])             │
  └────────────────┴──────────────────────────────────────┘
""")

print("✅ 04단계 완료! 다음은 05_groupby_aggregation.py에서 그룹별 집계를 배워요!")
