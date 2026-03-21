# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   Pandas 학습 05단계: GroupBy와 집계
#   ─ split-apply-combine, agg, transform, pivot_table, crosstab ─
#   ■ 실행 방법: python 05_groupby_aggregation.py
#   ■ Pandas 설치: pip install pandas
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# =========================================================================
#  GroupBy란?
# =========================================================================
#
#  "학년별 평균 점수", "반별 학생 수" 처럼
#  그룹으로 묶어서 집계하는 작업이에요.
#
#  이건 세 단계로 이루어져요:
#    1) Split   — 그룹으로 나누기  (학년별로 쪼개기)
#    2) Apply   — 함수 적용하기    (각 그룹에 평균 계산)
#    3) Combine — 결과 합치기      (결과를 하나로)
#
#  엑셀의 피벗 테이블과 비슷해요!
# =========================================================================

print("=" * 70)
print(" 05단계: GroupBy와 집계 (Aggregation)")
print("=" * 70)

import math


class GroupDF:
    """GroupBy 학습용 DataFrame"""

    def __init__(self, data, index=None):
        self._columns = list(data.keys())
        n = len(data[self._columns[0]])
        self._data = {col: list(data[col]) for col in self._columns}
        self._index = list(index) if index else list(range(n))

    @property
    def shape(self):
        return (len(self._index), len(self._columns))

    def display(self, title=None):
        if title:
            print(f"\n  [{title}]")
        idx_w = max(len(str(i)) for i in self._index) + 2
        col_w = {}
        for c in self._columns:
            w = len(str(c))
            for v in self._data[c]:
                w = max(w, len(str(v)))
            col_w[c] = w + 2
        header = " " * idx_w + "".join(f"{c:>{col_w[c]}}" for c in self._columns)
        print(header)
        print("  " + "─" * (len(header) - 2))
        for ri, idx in enumerate(self._index):
            line = f"{str(idx):<{idx_w}}"
            for c in self._columns:
                line += f"{str(self._data[c][ri]):>{col_w[c]}}"
            print(line)

    # ─── groupby: 그룹 나누기 ───
    def groupby(self, by):
        """
        열 값 기준으로 행을 그룹으로 나누기.

        Pandas에서:
          df.groupby('학년')
          df.groupby(['학년', '반'])
        """
        if isinstance(by, str):
            by = [by]

        # 그룹 키 → 행 인덱스 매핑
        groups = {}
        for i in range(len(self._index)):
            key = tuple(self._data[col][i] for col in by)
            if len(key) == 1:
                key = key[0]
            if key not in groups:
                groups[key] = []
            groups[key].append(i)

        return GroupByResult(self, groups, by)


class GroupByResult:
    """GroupBy 결과 — 집계 연산을 수행"""

    def __init__(self, df, groups, by_cols):
        self._df = df
        self._groups = groups  # {그룹키: [행인덱스들]}
        self._by_cols = by_cols

    def show_groups(self):
        """그룹 구성 보기"""
        print(f"\n  [그룹 구성] 기준: {self._by_cols}")
        for key, indices in self._groups.items():
            rows_info = []
            for i in indices:
                name_col = None
                for c in self._df._columns:
                    if c not in self._by_cols:
                        name_col = c
                        break
                rows_info.append(str(self._df._data[name_col][i]) if name_col else str(i))
            print(f"    그룹 '{key}': {rows_info} ({len(indices)}명)")

    # ── 기본 집계 함수들 ──
    def _aggregate(self, func_name, cols=None):
        """내부 집계 로직"""
        if cols is None:
            # 수치형 열만 자동 선택
            cols = []
            for c in self._df._columns:
                if c not in self._by_cols:
                    sample = [v for v in self._df._data[c]
                              if isinstance(v, (int, float))]
                    if sample:
                        cols.append(c)

        result_data = {col: [] for col in self._by_cols}
        for col in cols:
            result_data[col] = []
        result_keys = []

        for key, indices in sorted(self._groups.items()):
            if isinstance(key, tuple):
                for ci, col in enumerate(self._by_cols):
                    result_data[col].append(key[ci])
            else:
                result_data[self._by_cols[0]].append(key)
            result_keys.append(key)

            for col in cols:
                values = [self._df._data[col][i] for i in indices
                          if isinstance(self._df._data[col][i], (int, float))]

                if func_name == 'sum':
                    result_data[col].append(sum(values))
                elif func_name == 'mean':
                    result_data[col].append(round(sum(values) / len(values), 1) if values else 0)
                elif func_name == 'count':
                    result_data[col].append(len(values))
                elif func_name == 'min':
                    result_data[col].append(min(values) if values else None)
                elif func_name == 'max':
                    result_data[col].append(max(values) if values else None)
                elif func_name == 'std':
                    if len(values) > 1:
                        mean = sum(values) / len(values)
                        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
                        result_data[col].append(round(variance ** 0.5, 2))
                    else:
                        result_data[col].append(0)

        return GroupDF(result_data)

    def sum(self, cols=None):
        """그룹별 합계. Pandas: df.groupby('학년').sum()"""
        return self._aggregate('sum', cols)

    def mean(self, cols=None):
        """그룹별 평균. Pandas: df.groupby('학년').mean()"""
        return self._aggregate('mean', cols)

    def count(self, cols=None):
        """그룹별 개수. Pandas: df.groupby('학년').count()"""
        return self._aggregate('count', cols)

    def min(self, cols=None):
        """그룹별 최솟값. Pandas: df.groupby('학년').min()"""
        return self._aggregate('min', cols)

    def max(self, cols=None):
        """그룹별 최댓값. Pandas: df.groupby('학년').max()"""
        return self._aggregate('max', cols)

    def std(self, cols=None):
        """그룹별 표준편차. Pandas: df.groupby('학년').std()"""
        return self._aggregate('std', cols)

    # ── agg: 다중 집계 ──
    def agg(self, funcs):
        """
        다중 집계 — 여러 함수를 동시에 적용.

        Pandas에서:
          df.groupby('학년').agg(['mean', 'std'])
          df.groupby('학년').agg({'수학': 'mean', '영어': ['min', 'max']})
        """
        result_data = {}
        for col in self._by_cols:
            result_data[col] = []

        # funcs가 딕셔너리인 경우: {'수학': ['mean', 'max'], '영어': 'sum'}
        if isinstance(funcs, dict):
            for col, func_list in funcs.items():
                if isinstance(func_list, str):
                    func_list = [func_list]
                for func_name in func_list:
                    col_name = f"{col}_{func_name}"
                    result_data[col_name] = []

            for key, indices in sorted(self._groups.items()):
                if isinstance(key, tuple):
                    for ci, col in enumerate(self._by_cols):
                        result_data[col].append(key[ci])
                else:
                    result_data[self._by_cols[0]].append(key)

                for col, func_list in funcs.items():
                    if isinstance(func_list, str):
                        func_list = [func_list]
                    values = [self._df._data[col][i] for i in indices
                              if isinstance(self._df._data[col][i], (int, float))]

                    for func_name in func_list:
                        col_name = f"{col}_{func_name}"
                        if func_name == 'mean':
                            result_data[col_name].append(round(sum(values) / len(values), 1) if values else 0)
                        elif func_name == 'sum':
                            result_data[col_name].append(sum(values))
                        elif func_name == 'min':
                            result_data[col_name].append(min(values) if values else None)
                        elif func_name == 'max':
                            result_data[col_name].append(max(values) if values else None)
                        elif func_name == 'count':
                            result_data[col_name].append(len(values))

        return GroupDF(result_data)

    # ── transform: 그룹별 변환 ──
    def transform(self, col, func_name):
        """
        그룹별 변환 — 결과가 원래 크기와 동일!

        Pandas에서:
          df.groupby('학년')['수학'].transform('mean')
          → 각 행에 자기 학년의 평균이 들어감

        사용 예:
          df['그룹평균'] = df.groupby('학년')['수학'].transform('mean')
          df['정규화'] = df['수학'] - df.groupby('학년')['수학'].transform('mean')
        """
        result = [None] * len(self._df._index)

        for key, indices in self._groups.items():
            values = [self._df._data[col][i] for i in indices
                      if isinstance(self._df._data[col][i], (int, float))]

            if func_name == 'mean':
                group_val = round(sum(values) / len(values), 1) if values else 0
            elif func_name == 'sum':
                group_val = sum(values)
            elif func_name == 'min':
                group_val = min(values) if values else None
            elif func_name == 'max':
                group_val = max(values) if values else None
            elif func_name == 'count':
                group_val = len(values)
            else:
                group_val = None

            for i in indices:
                result[i] = group_val

        return result

    # ── filter: 그룹 필터링 ──
    def filter(self, col, func):
        """
        조건을 만족하는 그룹만 남기기.

        Pandas에서:
          df.groupby('학년').filter(lambda x: x['수학'].mean() > 80)
          → 수학 평균이 80 이상인 학년의 학생만 남김
        """
        keep_indices = []
        for key, indices in self._groups.items():
            values = [self._df._data[col][i] for i in indices
                      if isinstance(self._df._data[col][i], (int, float))]
            if func(values):
                keep_indices.extend(indices)

        keep_indices.sort()
        new_data = {}
        for c in self._df._columns:
            new_data[c] = [self._df._data[c][i] for i in keep_indices]
        return GroupDF(new_data, index=[self._df._index[i] for i in keep_indices])


# ─── pivot_table 함수 ───
def pivot_table(df, values, index, columns, aggfunc='mean'):
    """
    피벗 테이블 만들기.

    Pandas에서:
      pd.pivot_table(df, values='수학', index='학년', columns='반', aggfunc='mean')
    """
    # 고유 행/열 값 구하기
    row_vals = sorted(set(df._data[index]))
    col_vals = sorted(set(df._data[columns]))

    # 그룹별 값 모으기
    result = {index: row_vals}
    for cv in col_vals:
        result[f"{columns}={cv}"] = []

    for rv in row_vals:
        for cv in col_vals:
            vals = []
            for i in range(len(df._index)):
                if df._data[index][i] == rv and df._data[columns][i] == cv:
                    v = df._data[values][i]
                    if isinstance(v, (int, float)):
                        vals.append(v)

            if aggfunc == 'mean':
                result[f"{columns}={cv}"].append(round(sum(vals) / len(vals), 1) if vals else '-')
            elif aggfunc == 'sum':
                result[f"{columns}={cv}"].append(sum(vals) if vals else 0)
            elif aggfunc == 'count':
                result[f"{columns}={cv}"].append(len(vals))

    return GroupDF(result)


# ─── crosstab 함수 ───
def crosstab(series1_name, series1_data, series2_name, series2_data):
    """
    교차표 만들기.

    Pandas에서:
      pd.crosstab(df['학년'], df['반'])
    """
    vals1 = sorted(set(series1_data))
    vals2 = sorted(set(series2_data))

    result = {series1_name: vals1}
    for v2 in vals2:
        col_name = f"{series2_name}={v2}"
        counts = []
        for v1 in vals1:
            count = sum(1 for a, b in zip(series1_data, series2_data)
                        if a == v1 and b == v2)
            counts.append(count)
        result[col_name] = counts

    return GroupDF(result)


# ─── 테스트 데이터 ───
students = GroupDF({
    '이름':   ['김민수', '이영희', '박철수', '최지영', '정하늘',
              '한서준', '윤다은', '장예린', '송민호', '오수빈'],
    '학교':   ['서울초', '서울초', '서울초', '서울초', '부산초',
              '부산초', '부산초', '대전초', '대전초', '대전초'],
    '학년':   [3, 3, 2, 3, 2, 1, 1, 2, 3, 1],
    '반':     [1, 2, 1, 2, 1, 1, 2, 1, 2, 1],
    '수학':   [90, 88, 65, 98, 72, 85, 45, 78, 92, 68],
    '영어':   [78, 95, 82, 90, 85, 60, 92, 88, 80, 75],
    '국어':   [85, 85, 90, 82, 88, 75, 78, 95, 87, 80],
})

students.display("학생 데이터")


# ─────────────────────────────────────────────────────────────────────────
# 1. GroupBy 기본 — Split-Apply-Combine
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 1. GroupBy 기본 — Split-Apply-Combine")
print("─" * 70)

print("""
  GroupBy의 세 단계:

  ┌─ Split (나누기) ──────────────────────────────────┐
  │                                                    │
  │  전체 데이터    →   학년=1 그룹  [한서준, 윤다은, 오수빈]  │
  │                     학년=2 그룹  [박철수, 정하늘, 장예린]  │
  │                     학년=3 그룹  [김민수, 이영희, 최지영, 송민호]  │
  │                                                    │
  ├─ Apply (적용) ────────────────────────────────────┤
  │                                                    │
  │  학년=1 → 수학 평균: (85+45+68)/3 = 66.0          │
  │  학년=2 → 수학 평균: (65+72+78)/3 = 71.7          │
  │  학년=3 → 수학 평균: (90+88+98+92)/4 = 92.0       │
  │                                                    │
  ├─ Combine (합치기) ────────────────────────────────┤
  │                                                    │
  │  학년  수학_평균                                    │
  │   1     66.0                                       │
  │   2     71.7                                       │
  │   3     92.0                                       │
  └────────────────────────────────────────────────────┘
""")

# 학년별 그룹
grouped = students.groupby('학년')
grouped.show_groups()

# ── Pandas: grouped = df.groupby('학년') ──


# ─────────────────────────────────────────────────────────────────────────
# 2. 기본 집계 함수: sum, mean, count, min, max
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 2. 기본 집계 함수")
print("─" * 70)

# 학년별 평균
result = grouped.mean()
result.display("학년별 평균")
# ── Pandas: df.groupby('학년').mean(numeric_only=True) ──

# 학년별 합계
result = grouped.sum()
result.display("학년별 합계")
# ── Pandas: df.groupby('학년').sum(numeric_only=True) ──

# 학년별 학생 수
result = grouped.count()
result.display("학년별 학생 수")
# ── Pandas: df.groupby('학년').count() ──
# ── 또는: df.groupby('학년').size()  (모든 열에 대해 동일한 카운트) ──

# 학년별 최고점
result = grouped.max(cols=['수학', '영어', '국어'])
result.display("학년별 최고점")
# ── Pandas: df.groupby('학년')[['수학', '영어', '국어']].max() ──

# 학년별 최저점
result = grouped.min(cols=['수학', '영어', '국어'])
result.display("학년별 최저점")

# 학년별 표준편차
result = grouped.std(cols=['수학'])
result.display("학년별 수학 표준편차")
# ── Pandas: df.groupby('학년')['수학'].std() ──


# ─────────────────────────────────────────────────────────────────────────
# 3. agg() — 다중 집계
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 3. agg() — 다중 집계")
print("─" * 70)

# 열별로 다른 집계 함수 적용
result = grouped.agg({
    '수학': ['mean', 'max'],
    '영어': ['mean', 'min', 'max'],
})
result.display("학년별 다중 집계")

# ── Pandas로 하면? ──
# df.groupby('학년').agg({
#     '수학': ['mean', 'max'],
#     '영어': ['mean', 'min', 'max'],
# })
#
# 결과:
#        수학              영어
#       mean  max   mean  min  max
# 학년
# 1     66.0   85   75.7   60   92
# 2     71.7   78   85.0   82   88
# 3     92.0   98   85.8   78   95

print("""
  💡 agg()의 장점:
  ┌──────────────────────────────────────────┐
  │ 1) 여러 집계를 한번에!                   │
  │    .agg(['mean', 'std', 'min', 'max'])   │
  │                                          │
  │ 2) 열마다 다른 집계!                     │
  │    .agg({'수학': 'mean', '영어': 'sum'}) │
  │                                          │
  │ 3) 커스텀 함수도 가능!                   │
  │    .agg(lambda x: x.max() - x.min())    │
  │    → 범위(range) 계산                    │
  └──────────────────────────────────────────┘
""")


# ─────────────────────────────────────────────────────────────────────────
# 4. transform() — 그룹별 변환
# ─────────────────────────────────────────────────────────────────────────

print("─" * 70)
print(" 4. transform() — 그룹별 변환")
print("─" * 70)

print("""
  transform()은 집계 결과를 "원래 크기로" 돌려줘요!

  groupby().mean():        groupby().transform('mean'):
  학년  수학평균            이름    학년  수학  그룹평균
   1    66.0               한서준   1    85    66.0
   2    71.7               윤다은   1    45    66.0
   3    92.0               오수빈   1    68    66.0
                           박철수   2    65    71.7
                           ...     ...   ...   ...

  → 각 행에 자기 그룹의 값이 들어감!
  → 그룹 평균과의 차이 계산 등에 유용!
""")

# 학년별 수학 평균을 각 학생에게
group_means = grouped.transform('수학', 'mean')
print("  [transform] 학년별 수학 평균:")
for i in range(students.shape[0]):
    name = students._data['이름'][i]
    grade = students._data['학년'][i]
    score = students._data['수학'][i]
    gmean = group_means[i]
    diff = round(score - gmean, 1)
    sign = "+" if diff >= 0 else ""
    print(f"    {name} ({grade}학년): 수학={score}, 학년평균={gmean}, 차이={sign}{diff}")

# ── Pandas로 하면? ──
# df['그룹평균'] = df.groupby('학년')['수학'].transform('mean')
# df['차이'] = df['수학'] - df['그룹평균']


# ─────────────────────────────────────────────────────────────────────────
# 5. filter() — 그룹 필터링
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 5. filter() — 그룹 필터링")
print("─" * 70)

# 수학 평균이 70 이상인 학년의 학생만
print("\n[filter] 수학 평균 >= 70인 학년의 학생만:")
filtered = grouped.filter(
    '수학',
    lambda values: sum(values) / len(values) >= 70 if values else False
)
filtered.display()
# ── Pandas: df.groupby('학년').filter(lambda x: x['수학'].mean() >= 70) ──

# 학생 수가 3명 이상인 학년만
print("\n[filter] 학생 3명 이상인 학년:")
filtered2 = grouped.filter(
    '수학',
    lambda values: len(values) >= 3
)
filtered2.display()
# ── Pandas: df.groupby('학년').filter(lambda x: len(x) >= 3) ──


# ─────────────────────────────────────────────────────────────────────────
# 6. 다중 열 GroupBy
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 6. 다중 열 GroupBy")
print("─" * 70)

# 학교 + 학년별 그룹
multi_grouped = students.groupby(['학교', '학년'])
multi_grouped.show_groups()

result = multi_grouped.mean(cols=['수학', '영어'])
result.display("학교+학년별 평균")
# ── Pandas: df.groupby(['학교', '학년'])[['수학', '영어']].mean() ──


# ─────────────────────────────────────────────────────────────────────────
# 7. pivot_table() — 피벗 테이블
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 7. pivot_table() — 피벗 테이블")
print("─" * 70)

print("""
  피벗 테이블은 엑셀의 피벗 테이블과 같아요!
  행/열을 지정하고, 교차점에 집계값을 넣습니다.

  예: 학년(행) × 반(열) → 수학 평균

          반=1   반=2
  학년=1  76.5   45.0
  학년=2  71.7    -
  학년=3  90.0   93.0
""")

result = pivot_table(students, values='수학', index='학년', columns='반', aggfunc='mean')
result.display("학년×반 수학 평균 피벗")
# ── Pandas: pd.pivot_table(df, values='수학', index='학년', columns='반', aggfunc='mean') ──

result2 = pivot_table(students, values='수학', index='학교', columns='학년', aggfunc='mean')
result2.display("학교×학년 수학 평균 피벗")
# ── Pandas: pd.pivot_table(df, values='수학', index='학교', columns='학년', aggfunc='mean') ──


# ─────────────────────────────────────────────────────────────────────────
# 8. crosstab() — 교차표
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 8. crosstab() — 교차표")
print("─" * 70)

print("""
  교차표(crosstab)는 두 범주형 변수의 빈도를 표로 만든 것!

  예: 학년 × 반 → 몇 명?

          반=1  반=2
  학년=1   2     1
  학년=2   3     0
  학년=3   1     3
""")

result = crosstab('학년', students._data['학년'], '반', students._data['반'])
result.display("학년×반 교차표")
# ── Pandas: pd.crosstab(df['학년'], df['반']) ──

result2 = crosstab('학교', students._data['학교'], '학년', students._data['학년'])
result2.display("학교×학년 교차표")
# ── Pandas: pd.crosstab(df['학교'], df['학년']) ──


# ─────────────────────────────────────────────────────────────────────────
# ★ 실습: 학교별/과목별 성적 분석
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "═" * 70)
print(" ★ 실습: 학교별/과목별 성적 분석")
print("═" * 70)

students.display("분석 대상 데이터")

# 1. 학교별 전체 평균
print("\n── 1. 학교별 전체 평균 ──")
school_grouped = students.groupby('학교')
school_means = school_grouped.mean(cols=['수학', '영어', '국어'])
school_means.display()

# 2. 학교별 수학 최고점자 찾기
print("\n── 2. 학교별 수학 최고점자 ──")
for school in sorted(set(students._data['학교'])):
    max_score = -1
    max_name = ""
    for i in range(students.shape[0]):
        if students._data['학교'][i] == school:
            if students._data['수학'][i] > max_score:
                max_score = students._data['수학'][i]
                max_name = students._data['이름'][i]
    print(f"  {school}: {max_name} ({max_score}점)")
# ── Pandas: df.loc[df.groupby('학교')['수학'].idxmax()] ──

# 3. 과목별 점수 분포 비교
print("\n── 3. 과목별 점수 분포 비교 ──")
for subj in ['수학', '영어', '국어']:
    vals = students._data[subj]
    avg = sum(vals) / len(vals)
    max_v = max(vals)
    min_v = min(vals)
    spread = max_v - min_v
    print(f"  {subj}: 평균={avg:.1f}, 최고={max_v}, 최저={min_v}, 편차={spread}")

# 4. 학년별 성적 우수자 비율 (80점 이상)
print("\n── 4. 학년별 수학 80점 이상 비율 ──")
for grade in sorted(set(students._data['학년'])):
    total = 0
    above_80 = 0
    for i in range(students.shape[0]):
        if students._data['학년'][i] == grade:
            total += 1
            if students._data['수학'][i] >= 80:
                above_80 += 1
    pct = above_80 / total * 100 if total > 0 else 0
    bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
    print(f"  {grade}학년: {bar} {pct:.0f}% ({above_80}/{total}명)")

# 5. 학교×학년 성적 히트맵 (ASCII)
print("\n── 5. 학교×학년 수학 평균 히트맵 ──")
schools = sorted(set(students._data['학교']))
grades = sorted(set(students._data['학년']))

# 헤더
header = f"{'':>8}" + "".join(f"  {g}학년" for g in grades)
print(header)
print("  " + "─" * (len(header) - 2))

for school in schools:
    line = f"  {school:>6}"
    for grade in grades:
        vals = []
        for i in range(students.shape[0]):
            if students._data['학교'][i] == school and students._data['학년'][i] == grade:
                vals.append(students._data['수학'][i])
        if vals:
            avg = sum(vals) / len(vals)
            # 점수 기반 시각화
            if avg >= 90:
                symbol = " ★★★"
            elif avg >= 80:
                symbol = " ★★ "
            elif avg >= 70:
                symbol = " ★  "
            else:
                symbol = " ·  "
            line += f"{symbol}({avg:.0f})"
        else:
            line += "    ---  "
    print(line)

# ── Pandas로 전체 분석을 하면? ──
# # 학교별 평균
# df.groupby('학교')[['수학', '영어', '국어']].mean()
#
# # 학교별 최고점자
# df.loc[df.groupby('학교')['수학'].idxmax()]
#
# # 피벗 테이블
# pd.pivot_table(df, values='수학', index='학교', columns='학년', aggfunc='mean')
#
# # 교차표
# pd.crosstab(df['학교'], df['학년'])


# ─────────────────────────────────────────────────────────────────────────
# 정리
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "═" * 70)
print(" 정리: GroupBy & 집계 도구 모음")
print("═" * 70)

print("""
  ┌─────────────────┬──────────────────────────────────────┐
  │ 작업            │ Pandas 코드                          │
  ├─────────────────┼──────────────────────────────────────┤
  │ 그룹 나누기     │ df.groupby('열')                     │
  │ 다중 열 그룹    │ df.groupby(['열1', '열2'])           │
  │                 │                                      │
  │ 합계            │ .sum()                               │
  │ 평균            │ .mean()                              │
  │ 개수            │ .count() / .size()                   │
  │ 최소/최대       │ .min() / .max()                      │
  │ 표준편차        │ .std()                               │
  │                 │                                      │
  │ 다중 집계       │ .agg(['mean', 'std'])                │
  │ 열별 다른 집계  │ .agg({'A': 'mean', 'B': 'sum'})     │
  │ 그룹별 변환     │ .transform('mean')                   │
  │ 그룹 필터링     │ .filter(lambda x: 조건)              │
  │                 │                                      │
  │ 피벗 테이블     │ pd.pivot_table(df, ...)              │
  │ 교차표          │ pd.crosstab(s1, s2)                  │
  └─────────────────┴──────────────────────────────────────┘

  핵심 기억:
  • groupby = Split → Apply → Combine
  • agg(): 여러 함수 한번에
  • transform(): 원래 크기 유지
  • filter(): 그룹 단위 필터링
""")

print("✅ 05단계 완료! 다음은 06_merge_join.py에서 테이블 결합을 배워요!")
