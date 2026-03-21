# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   Pandas 학습 01단계: Series와 DataFrame
#   ─ 1차원 배열(Series), 2차원 테이블(DataFrame), 생성과 기본 속성 ─
#   ■ 실행 방법: python 01_series_dataframe.py
#   ■ Pandas 설치: pip install pandas
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# =========================================================================
#  Pandas가 뭐예요?
# =========================================================================
#
#  Pandas는 "표(테이블) 형태의 데이터"를 다루는 파이썬 라이브러리예요.
#  엑셀 스프레드시트를 파이썬으로 다룬다고 생각하면 됩니다!
#
#  Pandas의 핵심 구조 두 가지:
#    1) Series   → 인덱스가 달린 1차원 배열 (세로 한 줄)
#    2) DataFrame → 인덱스가 달린 2차원 테이블 (엑셀 시트 한 장)
#
#  우리는 먼저 순수 파이썬으로 이 구조를 직접 만들어 보고,
#  그 다음 Pandas가 어떻게 같은 일을 하는지 비교할 거예요!
# =========================================================================

print("=" * 70)
print(" 01단계: Series와 DataFrame 이해하기")
print("=" * 70)


# ─────────────────────────────────────────────────────────────────────────
# 1. Series란? — 인덱스가 있는 1차원 배열
# ─────────────────────────────────────────────────────────────────────────
#
#  일반 리스트:  [90, 85, 78]          → 위치(0,1,2)로만 접근
#  Series:      {'수학': 90, '영어': 85, '국어': 78}  → 이름(라벨)로 접근 가능!
#
#  Series = 리스트 + 사전(dict)의 장점을 합친 것!

print("\n" + "─" * 70)
print(" 1. Series 직접 만들어보기 (순수 파이썬)")
print("─" * 70)


class MySeries:
    """
    Pandas Series를 흉내 낸 간단한 클래스.
    내부적으로 '인덱스 리스트'와 '값 리스트'를 따로 저장합니다.

    실제 Pandas Series도 비슷한 구조예요:
      - index: 라벨(이름) 배열
      - values: 실제 데이터 배열
    """

    def __init__(self, data, index=None, name=None):
        """
        data: 리스트 또는 딕셔너리
        index: 인덱스 라벨 리스트 (None이면 0, 1, 2... 자동 부여)
        name: 이 Series의 이름
        """
        if isinstance(data, dict):
            # 딕셔너리로 만들면 키가 인덱스, 값이 데이터
            self._index = list(data.keys())
            self._values = list(data.values())
        else:
            self._values = list(data)
            if index is not None:
                self._index = list(index)
            else:
                # 인덱스를 안 주면 0부터 자동 번호
                self._index = list(range(len(data)))

        self.name = name

        # 인덱스와 값의 개수가 같아야 해요!
        assert len(self._index) == len(self._values), \
            "인덱스 개수와 값 개수가 달라요!"

    def __getitem__(self, key):
        """인덱스 라벨로 값 가져오기 (series['수학'] 처럼)"""
        if key in self._index:
            pos = self._index.index(key)
            return self._values[pos]
        raise KeyError(f"'{key}' 라벨이 없어요!")

    def __setitem__(self, key, value):
        """값 설정하기"""
        if key in self._index:
            pos = self._index.index(key)
            self._values[pos] = value
        else:
            # 새 라벨이면 추가
            self._index.append(key)
            self._values.append(value)

    def __len__(self):
        return len(self._values)

    def __repr__(self):
        lines = []
        max_idx_len = max(len(str(i)) for i in self._index) if self._index else 0
        for idx, val in zip(self._index, self._values):
            lines.append(f"  {str(idx):<{max_idx_len}}    {val}")
        if self.name:
            lines.append(f"  Name: {self.name}")
        lines.append(f"  Length: {len(self._values)}")
        return "\n".join(lines)

    @property
    def index(self):
        return self._index

    @property
    def values(self):
        return self._values

    @property
    def shape(self):
        """모양: (원소 개수,)"""
        return (len(self._values),)

    @property
    def dtype(self):
        """데이터 타입 추론"""
        types = set(type(v).__name__ for v in self._values)
        if len(types) == 1:
            return types.pop()
        return "mixed"

    def mean(self):
        """평균"""
        nums = [v for v in self._values if isinstance(v, (int, float))]
        return sum(nums) / len(nums) if nums else None

    def sum(self):
        """합계"""
        nums = [v for v in self._values if isinstance(v, (int, float))]
        return sum(nums)

    def describe(self):
        """기본 통계 (숫자 데이터만)"""
        nums = sorted(v for v in self._values if isinstance(v, (int, float)))
        if not nums:
            return "숫자 데이터가 없어요!"
        n = len(nums)
        mean_val = sum(nums) / n
        return {
            'count': n,
            'mean': round(mean_val, 2),
            'min': nums[0],
            'max': nums[-1],
        }


# ── 사용 예제 ──

# 방법 1: 리스트로 만들기 (인덱스 자동 부여)
scores = MySeries([90, 85, 78, 92])
print("\n[리스트로 만든 Series]")
print(scores)
print(f"  shape: {scores.shape}, dtype: {scores.dtype}")

# 방법 2: 딕셔너리로 만들기 (키가 인덱스)
subject_scores = MySeries(
    {'수학': 90, '영어': 85, '국어': 78, '과학': 92},
    name='김철수_성적'
)
print("\n[딕셔너리로 만든 Series]")
print(subject_scores)
print(f"  수학 점수: {subject_scores['수학']}")

# 방법 3: 리스트 + 커스텀 인덱스
heights = MySeries(
    [165, 172, 158, 180],
    index=['민수', '영희', '철수', '지영'],
    name='키(cm)'
)
print("\n[커스텀 인덱스 Series]")
print(heights)
print(f"  영희의 키: {heights['영희']}cm")

# ── Pandas로 하면? ──
# import pandas as pd
# scores = pd.Series([90, 85, 78, 92])
# subject_scores = pd.Series({'수학': 90, '영어': 85, '국어': 78, '과학': 92}, name='김철수_성적')
# heights = pd.Series([165, 172, 158, 180], index=['민수', '영희', '철수', '지영'], name='키(cm)')
# print(heights['영희'])  # 172


# ─────────────────────────────────────────────────────────────────────────
# 2. DataFrame이란? — 2차원 테이블
# ─────────────────────────────────────────────────────────────────────────
#
#  DataFrame = 여러 Series를 옆으로 나란히 붙인 것!
#
#  이름    수학   영어   국어
#  민수    90     85     78
#  영희    88     92     85
#  철수    75     80     90
#
#  → 각 열(수학, 영어, 국어)이 하나의 Series
#  → 행(민수, 영희, 철수)이 인덱스

print("\n" + "─" * 70)
print(" 2. DataFrame 직접 만들어보기 (순수 파이썬)")
print("─" * 70)


class MyDataFrame:
    """
    Pandas DataFrame을 흉내 낸 간단한 클래스.
    내부적으로 '열 이름 → 값 리스트'의 딕셔너리를 저장합니다.

    실제 Pandas DataFrame의 핵심 구조:
      - columns: 열 이름 리스트
      - index: 행 라벨 리스트
      - 내부 데이터: 각 열은 numpy 배열 (우리는 리스트로 대체)
    """

    def __init__(self, data, index=None, columns=None):
        """
        data: 딕셔너리(열이름→값리스트) 또는 리스트의 리스트(행 단위)
        index: 행 라벨
        columns: 열 이름
        """
        if isinstance(data, dict):
            # 딕셔너리로 만들기 (가장 흔한 방법!)
            self._columns = list(data.keys())
            # 모든 열의 길이를 맞춰야 해요
            max_len = max(len(v) for v in data.values())
            self._data = {}
            for col in self._columns:
                vals = list(data[col])
                # 짧은 열은 None으로 채우기
                while len(vals) < max_len:
                    vals.append(None)
                self._data[col] = vals
            n_rows = max_len

        elif isinstance(data, list):
            # 리스트의 리스트로 만들기 (행 단위)
            n_rows = len(data)
            if columns is None:
                n_cols = len(data[0]) if data else 0
                self._columns = [f'col_{i}' for i in range(n_cols)]
            else:
                self._columns = list(columns)
            self._data = {}
            for ci, col in enumerate(self._columns):
                self._data[col] = [row[ci] if ci < len(row) else None
                                   for row in data]
        else:
            raise TypeError("dict 또는 list로 만들어주세요!")

        # 인덱스 설정
        if index is not None:
            self._index = list(index)
        else:
            self._index = list(range(n_rows))

    @property
    def shape(self):
        """(행 수, 열 수) 튜플"""
        n_rows = len(self._index)
        n_cols = len(self._columns)
        return (n_rows, n_cols)

    @property
    def columns(self):
        return self._columns

    @property
    def index(self):
        return self._index

    @property
    def dtypes(self):
        """각 열의 데이터 타입"""
        result = {}
        for col in self._columns:
            types = set(type(v).__name__ for v in self._data[col] if v is not None)
            result[col] = types.pop() if len(types) == 1 else 'mixed'
        return result

    def __getitem__(self, col_name):
        """열 선택: df['수학']"""
        if col_name in self._data:
            return MySeries(
                self._data[col_name],
                index=self._index,
                name=col_name
            )
        raise KeyError(f"'{col_name}' 열이 없어요!")

    def __setitem__(self, col_name, values):
        """열 추가/수정: df['새열'] = [...]"""
        if isinstance(values, (list, tuple)):
            self._data[col_name] = list(values)
        else:
            # 스칼라 값이면 모든 행에 같은 값
            self._data[col_name] = [values] * len(self._index)
        if col_name not in self._columns:
            self._columns.append(col_name)

    def __repr__(self):
        # 예쁘게 테이블 출력
        col_widths = {}
        for col in self._columns:
            max_w = len(str(col))
            for val in self._data[col]:
                max_w = max(max_w, len(str(val)))
            col_widths[col] = max_w + 2

        idx_width = max(len(str(i)) for i in self._index) + 2 if self._index else 4

        # 헤더
        header = " " * idx_width
        for col in self._columns:
            header += f"{str(col):>{col_widths[col]}}"

        lines = [header]
        lines.append("  " + "─" * (len(header) - 2))

        # 데이터 행
        for ri, idx in enumerate(self._index):
            row_str = f"{str(idx):<{idx_width}}"
            for col in self._columns:
                val = self._data[col][ri]
                row_str += f"{str(val):>{col_widths[col]}}"
            lines.append(row_str)

        lines.append(f"\n  [{self.shape[0]} rows x {self.shape[1]} columns]")
        return "\n".join(lines)

    def head(self, n=5):
        """처음 n개 행 보기"""
        n = min(n, len(self._index))
        new_data = {col: self._data[col][:n] for col in self._columns}
        return MyDataFrame(new_data, index=self._index[:n])

    def tail(self, n=5):
        """마지막 n개 행 보기"""
        n = min(n, len(self._index))
        new_data = {col: self._data[col][-n:] for col in self._columns}
        return MyDataFrame(new_data, index=self._index[-n:])

    def info(self):
        """DataFrame 정보 출력 (Pandas의 df.info() 흉내)"""
        print(f"\n  <MyDataFrame>")
        print(f"  행 수: {self.shape[0]}, 열 수: {self.shape[1]}")
        print(f"  인덱스: {self._index[0]} ~ {self._index[-1]}")
        print(f"  열 정보:")
        dtypes = self.dtypes
        for col in self._columns:
            non_null = sum(1 for v in self._data[col] if v is not None)
            print(f"    {col:>10}: {non_null}개 값, 타입={dtypes[col]}")

    def describe(self):
        """숫자 열에 대한 기본 통계"""
        print("\n  [기본 통계]")
        for col in self._columns:
            nums = [v for v in self._data[col] if isinstance(v, (int, float))]
            if nums:
                avg = sum(nums) / len(nums)
                print(f"    {col}: 평균={avg:.1f}, "
                      f"최소={min(nums)}, 최대={max(nums)}, "
                      f"개수={len(nums)}")


# ─────────────────────────────────────────────────────────────────────────
# 3. DataFrame 만드는 다양한 방법
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 3. DataFrame 만드는 다양한 방법")
print("─" * 70)

# 방법 1: 딕셔너리로 만들기 (열 기준)
print("\n[방법 1] 딕셔너리로 만들기 (가장 많이 쓰는 방법!)")
df1 = MyDataFrame({
    '이름': ['민수', '영희', '철수', '지영'],
    '수학': [90, 88, 75, 95],
    '영어': [85, 92, 80, 88],
    '국어': [78, 85, 90, 82],
})
print(df1)

# ── Pandas로 하면? ──
# import pandas as pd
# df1 = pd.DataFrame({
#     '이름': ['민수', '영희', '철수', '지영'],
#     '수학': [90, 88, 75, 95],
#     '영어': [85, 92, 80, 88],
#     '국어': [78, 85, 90, 82],
# })

# 방법 2: 리스트의 리스트로 만들기 (행 기준)
print("\n[방법 2] 리스트의 리스트로 만들기 (행 기준)")
df2 = MyDataFrame(
    [
        ['민수', 90, 85, 78],
        ['영희', 88, 92, 85],
        ['철수', 75, 80, 90],
    ],
    columns=['이름', '수학', '영어', '국어']
)
print(df2)

# ── Pandas로 하면? ──
# df2 = pd.DataFrame(
#     [['민수', 90, 85, 78], ['영희', 88, 92, 85], ['철수', 75, 80, 90]],
#     columns=['이름', '수학', '영어', '국어']
# )

# 방법 3: 커스텀 인덱스 사용
print("\n[방법 3] 커스텀 인덱스 사용")
df3 = MyDataFrame(
    {'수학': [90, 88, 75], '영어': [85, 92, 80]},
    index=['민수', '영희', '철수']
)
print(df3)

# ── Pandas로 하면? ──
# df3 = pd.DataFrame(
#     {'수학': [90, 88, 75], '영어': [85, 92, 80]},
#     index=['민수', '영희', '철수']
# )


# ─────────────────────────────────────────────────────────────────────────
# 4. 기본 속성 탐색: shape, dtypes, info(), describe()
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 4. 기본 속성 탐색")
print("─" * 70)

print(f"\n  shape (모양): {df1.shape}")
print(f"  → {df1.shape[0]}개 행, {df1.shape[1]}개 열")

print(f"\n  columns (열 이름): {df1.columns}")
print(f"\n  index (행 라벨): {df1.index}")

print(f"\n  dtypes (각 열의 타입):")
for col, dtype in df1.dtypes.items():
    print(f"    {col}: {dtype}")

# ── Pandas로 하면? ──
# print(df1.shape)       # (4, 4)
# print(df1.columns)     # Index(['이름', '수학', '영어', '국어'], dtype='object')
# print(df1.index)       # RangeIndex(start=0, stop=4, step=1)
# print(df1.dtypes)      # 이름: object, 수학: int64, 영어: int64, 국어: int64

df1.info()
df1.describe()

# ── Pandas로 하면? ──
# df1.info()       # 열 정보, null 개수, 메모리 사용량
# df1.describe()   # count, mean, std, min, 25%, 50%, 75%, max


# ─────────────────────────────────────────────────────────────────────────
# 5. head()와 tail() — 미리보기
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 5. head()와 tail() — 미리보기")
print("─" * 70)

print("\n[head(2) — 처음 2개 행]")
print(df1.head(2))

print("\n[tail(2) — 마지막 2개 행]")
print(df1.tail(2))

# ── Pandas로 하면? ──
# print(df1.head(2))  # 처음 2행
# print(df1.tail(2))  # 마지막 2행


# ─────────────────────────────────────────────────────────────────────────
# 6. 열 접근하기
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 6. 열 접근하기")
print("─" * 70)

# 대괄호로 열 접근 (가장 기본!)
math_col = df1['수학']
print("\n[df['수학'] — 수학 열 가져오기]")
print(math_col)
print(f"  수학 평균: {math_col.mean()}")
print(f"  수학 합계: {math_col.sum()}")

# ── Pandas로 하면? ──
# math_col = df1['수학']        # Series 반환
# # 또는
# math_col = df1.수학            # 점(.) 접근도 가능 (열 이름이 영문일 때)
# print(math_col.mean())        # 87.0
# print(math_col.sum())         # 348


# ─────────────────────────────────────────────────────────────────────────
# 7. Series 연산 — 벡터 연산의 마법
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 7. Series 연산 (벡터 연산)")
print("─" * 70)

# 순수 파이썬으로 "모든 점수에 5점 더하기"
print("\n[순수 파이썬] 모든 수학 점수에 5점 보너스:")
math_scores = [90, 88, 75, 95]
bonus_scores = []
for score in math_scores:
    bonus_scores.append(score + 5)
print(f"  원래: {math_scores}")
print(f"  보너스: {bonus_scores}")

# Pandas Series는 이걸 한 줄로!
# ── Pandas로 하면? ──
# df1['수학'] + 5  → Series([95, 93, 80, 100])
# 모든 원소에 동시에 5가 더해져요! (브로드캐스팅)

# 리스트 컴프리헨션으로 비슷하게:
print("\n[리스트 컴프리헨션 — Pandas 스타일 연산 흉내]")
math_plus_eng = [m + e for m, e in zip([90, 88, 75, 95], [85, 92, 80, 88])]
print(f"  수학+영어 합계: {math_plus_eng}")

# ── Pandas로 하면? ──
# df1['수학'] + df1['영어']  → Series([175, 180, 155, 183])
# 같은 위치끼리 자동으로 더해져요!


# ─────────────────────────────────────────────────────────────────────────
# 8. Series와 DataFrame의 관계
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 8. Series와 DataFrame의 관계")
print("─" * 70)

print("""
  ┌─────────────────────────────────────────────┐
  │          DataFrame (2차원 테이블)             │
  │                                              │
  │  인덱스    이름    수학    영어    국어        │
  │  ─────   ─────  ─────  ─────  ─────         │
  │    0      민수    90     85     78           │
  │    1      영희    88     92     85           │
  │    2      철수    75     80     90           │
  │    3      지영    95     88     82           │
  │                                              │
  │  ← 열1 →  ← 열2 → ← 열3 → ← 열4 →          │
  │  (Series) (Series) (Series) (Series)         │
  │                                              │
  │  DataFrame = 여러 Series가 옆으로 나란히!      │
  └─────────────────────────────────────────────┘

  핵심 포인트:
  • DataFrame에서 열 하나를 꺼내면 → Series
  • 여러 Series를 합치면 → DataFrame
  • 모든 열은 같은 인덱스를 공유해요!
""")


# ─────────────────────────────────────────────────────────────────────────
# 9. 새 열 추가하기
# ─────────────────────────────────────────────────────────────────────────

print("─" * 70)
print(" 9. 새 열 추가하기")
print("─" * 70)

# 총점 열 추가
df1['총점'] = [
    df1._data['수학'][i] + df1._data['영어'][i] + df1._data['국어'][i]
    for i in range(df1.shape[0])
]
print("\n[총점 열 추가 후]")
print(df1)

# ── Pandas로 하면? ──
# df1['총점'] = df1['수학'] + df1['영어'] + df1['국어']
# 이 한 줄이면 돼요! Series끼리 더하면 자동으로 같은 행끼리 더해져요.


# ─────────────────────────────────────────────────────────────────────────
# ★ 실습: 학생 성적표 DataFrame 만들기
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "═" * 70)
print(" ★ 실습: 학생 성적표 DataFrame 만들기")
print("═" * 70)

# 5명 학생의 성적 데이터
report_card = MyDataFrame({
    '이름':   ['김민수', '이영희', '박철수', '최지영', '정하늘'],
    '학년':   [3, 3, 2, 3, 2],
    '반':     [1, 2, 1, 2, 1],
    '국어':   [85, 92, 78, 95, 88],
    '수학':   [90, 88, 65, 98, 72],
    '영어':   [78, 95, 82, 90, 85],
    '과학':   [88, 85, 75, 92, 90],
    '사회':   [82, 90, 88, 85, 78],
})

print("\n[학생 성적표]")
print(report_card)

# 기본 정보 확인
report_card.info()

# 기본 통계
report_card.describe()

# 총점 계산
subjects = ['국어', '수학', '영어', '과학', '사회']
totals = []
for i in range(report_card.shape[0]):
    total = sum(report_card._data[subj][i] for subj in subjects)
    totals.append(total)
report_card['총점'] = totals

# 평균 계산
report_card['평균'] = [round(t / len(subjects), 1) for t in totals]

print("\n[총점과 평균 추가 후]")
print(report_card)

# ── Pandas로 하면? ──
# subjects = ['국어', '수학', '영어', '과학', '사회']
# report_card['총점'] = report_card[subjects].sum(axis=1)
# report_card['평균'] = report_card[subjects].mean(axis=1).round(1)
# → 딱 2줄이면 돼요!

# 성적 순위 매기기
print("\n[평균 기준 순위]")
avgs = list(report_card._data['평균'])
names = list(report_card._data['이름'])
ranked = sorted(zip(names, avgs), key=lambda x: x[1], reverse=True)
for rank, (name, avg) in enumerate(ranked, 1):
    print(f"  {rank}등: {name} (평균: {avg})")

# ── Pandas로 하면? ──
# report_card['순위'] = report_card['평균'].rank(ascending=False).astype(int)
# print(report_card.sort_values('평균', ascending=False))


# ─────────────────────────────────────────────────────────────────────────
# 정리: Pandas vs 순수 파이썬 비교
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "═" * 70)
print(" 정리: Pandas vs 순수 파이썬 비교")
print("═" * 70)

print("""
  ┌─────────────────────────┬──────────────────────────────────┐
  │     순수 파이썬          │          Pandas                  │
  ├─────────────────────────┼──────────────────────────────────┤
  │ data = [90, 85, 78]     │ s = pd.Series([90, 85, 78])     │
  │ data[0]  → 90           │ s[0]  → 90                      │
  │ sum(data) → 253         │ s.sum() → 253                   │
  │                         │                                  │
  │ for문으로 열별 합계      │ df.sum() 한 줄!                  │
  │ dict로 테이블 흉내       │ pd.DataFrame(dict) 한 줄!        │
  │ 직접 통계 함수 구현      │ df.describe() 한 줄!             │
  │                         │                                  │
  │ ❌ 수십 줄 코드          │ ✅ 1~2줄로 끝!                   │
  │ ❌ 느림 (큰 데이터)      │ ✅ 빠름 (C/NumPy 기반)           │
  │ ❌ 표 출력 직접 구현     │ ✅ 예쁜 출력 자동                 │
  └─────────────────────────┴──────────────────────────────────┘

  핵심 정리:
  1. Series = 인덱스 + 1차원 값 배열
  2. DataFrame = 인덱스 + 여러 Series(열)의 모음
  3. shape로 크기, dtypes로 타입, info()로 요약, describe()로 통계
  4. df['열이름']으로 열 접근, df['새열'] = 값으로 열 추가
""")

print("✅ 01단계 완료! 다음은 02_indexing_selection.py에서 데이터 선택을 배워요!")
