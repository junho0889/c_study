# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   Pandas 학습 03단계: 데이터 조작
#   ─ 열 추가/삭제, apply, map, sort, rank ─
#   ■ 실행 방법: python 03_data_manipulation.py
#   ■ Pandas 설치: pip install pandas
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# =========================================================================
#  데이터를 "변형"하고 "가공"하는 방법을 배워요!
# =========================================================================
#
#  데이터 분석의 80%는 데이터를 원하는 모양으로 바꾸는 작업이에요.
#  - 새로운 열 추가하기
#  - 불필요한 열 삭제하기
#  - 함수를 적용해서 값 변환하기
#  - 정렬하기, 순위 매기기
# =========================================================================

print("=" * 70)
print(" 03단계: 데이터 조작 (Data Manipulation)")
print("=" * 70)


# ── 순수 파이썬 DataFrame ──

class MiniDF:
    """데이터 조작 학습용 간단한 DataFrame"""

    def __init__(self, data, index=None):
        self._columns = list(data.keys())
        first_key = self._columns[0]
        n = len(data[first_key])
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
            for r in range(len(self._index)):
                w = max(w, len(str(self._data[c][r])))
            col_w[c] = w + 2
        header = " " * idx_w + "".join(f"{c:>{col_w[c]}}" for c in self._columns)
        print(header)
        print("  " + "─" * (len(header) - 2))
        for ri, idx in enumerate(self._index):
            line = f"{str(idx):<{idx_w}}"
            for c in self._columns:
                line += f"{str(self._data[c][ri]):>{col_w[c]}}"
            print(line)
        print(f"  [{self.shape[0]} rows x {self.shape[1]} cols]")

    def copy(self):
        """깊은 복사"""
        new_data = {col: list(vals) for col, vals in self._data.items()}
        return MiniDF(new_data, index=list(self._index))

    # ── 열 추가/삭제 ──
    def add_column(self, name, values):
        """새 열 추가: df['새열'] = [값들]"""
        if isinstance(values, (int, float, str)):
            self._data[name] = [values] * len(self._index)
        else:
            self._data[name] = list(values)
        if name not in self._columns:
            self._columns.append(name)
        return self

    def drop(self, columns=None, rows=None):
        """열 또는 행 삭제: df.drop(columns=['열']) 또는 df.drop(rows=[인덱스])"""
        new_data = {c: list(self._data[c]) for c in self._columns}
        new_idx = list(self._index)
        new_cols = list(self._columns)

        if columns:
            for col in (columns if isinstance(columns, list) else [columns]):
                if col in new_data:
                    del new_data[col]
                    new_cols.remove(col)

        if rows:
            row_list = rows if isinstance(rows, list) else [rows]
            positions = [self._index.index(r) for r in row_list if r in self._index]
            positions.sort(reverse=True)
            for pos in positions:
                for c in new_cols:
                    new_data[c].pop(pos)
                new_idx.pop(pos)

        result = MiniDF.__new__(MiniDF)
        result._data = new_data
        result._columns = new_cols
        result._index = new_idx
        return result

    # ── apply: 함수 적용 ──
    def apply_col(self, col, func):
        """
        열에 함수 적용.

        Pandas에서:
          df['수학'].apply(lambda x: x * 1.1)
          df['이름'].apply(len)
        """
        return [func(v) for v in self._data[col]]

    def apply_row(self, func, cols=None):
        """
        행에 함수 적용 (axis=1).

        Pandas에서:
          df.apply(lambda row: row['수학'] + row['영어'], axis=1)
        """
        if cols is None:
            cols = self._columns
        results = []
        for i in range(len(self._index)):
            row = {c: self._data[c][i] for c in cols}
            results.append(func(row))
        return results

    # ── map: 값 매핑 ──
    def map_col(self, col, mapping):
        """
        값을 다른 값으로 변환 (사전 매핑 또는 함수).

        Pandas에서:
          df['학년'].map({1: '1학년', 2: '2학년', 3: '3학년'})
          df['이름'].map(str.upper)
        """
        if isinstance(mapping, dict):
            return [mapping.get(v, v) for v in self._data[col]]
        elif callable(mapping):
            return [mapping(v) for v in self._data[col]]
        return self._data[col]

    # ── replace: 값 치환 ──
    def replace(self, col, old, new):
        """
        특정 값을 다른 값으로 치환.

        Pandas에서:
          df['열'].replace('old', 'new')
          df.replace({'열': {1: '일', 2: '이'}})
        """
        return [new if v == old else v for v in self._data[col]]

    # ── rename: 이름 변경 ──
    def rename(self, columns=None, index=None):
        """
        열 이름 또는 인덱스 이름 변경.

        Pandas에서:
          df.rename(columns={'수학': 'Math', '영어': 'English'})
          df.rename(index={0: 'first'})
        """
        result = self.copy()
        if columns:
            result._columns = [columns.get(c, c) for c in result._columns]
            new_data = {}
            for old_name, new_name in zip(self._columns, result._columns):
                new_data[new_name] = result._data[old_name]
            result._data = new_data
        if index:
            result._index = [index.get(i, i) for i in result._index]
        return result

    # ── sort: 정렬 ──
    def sort_values(self, by, ascending=True):
        """
        값 기준 정렬.

        Pandas에서:
          df.sort_values('수학')                 # 오름차순
          df.sort_values('수학', ascending=False) # 내림차순
          df.sort_values(['학년', '수학'])        # 다중 열 정렬
        """
        n = len(self._index)
        indices = list(range(n))

        if isinstance(by, list):
            # 다중 열 정렬 (뒤의 열부터 안정 정렬)
            for col in reversed(by):
                indices.sort(key=lambda i: self._data[col][i],
                             reverse=not ascending)
        else:
            indices.sort(key=lambda i: self._data[by][i],
                         reverse=not ascending)

        new_data = {c: [self._data[c][i] for i in indices] for c in self._columns}
        new_idx = [self._index[i] for i in indices]
        return MiniDF(new_data, index=new_idx)

    def sort_index(self, ascending=True):
        """인덱스 기준 정렬."""
        pairs = list(enumerate(self._index))
        pairs.sort(key=lambda x: x[1], reverse=not ascending)
        indices = [p[0] for p in pairs]
        new_data = {c: [self._data[c][i] for i in indices] for c in self._columns}
        new_idx = [self._index[i] for i in indices]
        return MiniDF(new_data, index=new_idx)

    # ── rank: 순위 ──
    def rank(self, col, ascending=True):
        """
        순위 매기기.

        Pandas에서:
          df['수학'].rank()                     # 오름차순 순위
          df['수학'].rank(ascending=False)      # 내림차순 순위
          df['수학'].rank(method='min')         # 동순위 처리 방법
        """
        values = list(self._data[col])
        n = len(values)
        sorted_vals = sorted(enumerate(values), key=lambda x: x[1],
                             reverse=not ascending)
        ranks = [0] * n
        for rank_pos, (orig_idx, _) in enumerate(sorted_vals, 1):
            ranks[orig_idx] = rank_pos
        return ranks

    def nlargest(self, n, col):
        """상위 n개 행. Pandas: df.nlargest(3, '수학')"""
        sorted_df = self.sort_values(col, ascending=False)
        new_data = {c: sorted_df._data[c][:n] for c in sorted_df._columns}
        return MiniDF(new_data, index=sorted_df._index[:n])

    def nsmallest(self, n, col):
        """하위 n개 행. Pandas: df.nsmallest(3, '수학')"""
        sorted_df = self.sort_values(col, ascending=True)
        new_data = {c: sorted_df._data[c][:n] for c in sorted_df._columns}
        return MiniDF(new_data, index=sorted_df._index[:n])


# ─── 테스트 데이터 ───
df = MiniDF({
    '이름':   ['김민수', '이영희', '박철수', '최지영', '정하늘'],
    '학년':   [3, 3, 2, 3, 2],
    '수학':   [90, 88, 65, 98, 72],
    '영어':   [78, 95, 82, 90, 85],
    '국어':   [85, 85, 90, 82, 88],
})

df.display("원본 데이터")


# ─────────────────────────────────────────────────────────────────────────
# 1. 열 추가와 삭제
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 1. 열 추가와 삭제")
print("─" * 70)

# 새 열 추가 — 계산으로
df_copy = df.copy()
totals = [df_copy._data['수학'][i] + df_copy._data['영어'][i] + df_copy._data['국어'][i]
          for i in range(df_copy.shape[0])]
df_copy.add_column('총점', totals)
df_copy.add_column('평균', [round(t / 3, 1) for t in totals])
df_copy.display("총점, 평균 열 추가")

# ── Pandas로 하면? ──
# df['총점'] = df['수학'] + df['영어'] + df['국어']
# df['평균'] = df[['수학', '영어', '국어']].mean(axis=1).round(1)

# 상수 열 추가
df_copy.add_column('학교', '서울초등학교')
df_copy.display("상수 열 추가")
# ── Pandas: df['학교'] = '서울초등학교' ──

# 열 삭제
df_dropped = df_copy.drop(columns=['학교', '총점'])
df_dropped.display("학교, 총점 열 삭제 후")
# ── Pandas: df.drop(columns=['학교', '총점']) ──
# 또는: df.drop(['학교', '총점'], axis=1)
# ⚠️ inplace=True를 붙이면 원본 수정, 안 붙이면 새 DataFrame 반환

# 행 삭제
df_dropped2 = df.drop(rows=[2, 4])
df_dropped2.display("2번, 4번 행 삭제 후")
# ── Pandas: df.drop(index=[2, 4]) ──
# 또는: df.drop([2, 4], axis=0)


# ─────────────────────────────────────────────────────────────────────────
# 2. apply() — 함수 적용의 마법
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 2. apply() — 함수 적용")
print("─" * 70)

print("""
  apply()는 "각 원소(또는 행/열)에 함수를 적용"하는 도구예요.

  ┌─────────────────────────────────────────────┐
  │ [90, 88, 65, 98, 72]                        │
  │      ↓  apply(등급_함수)                     │
  │ ['A', 'B+', 'D', 'A+', 'C']                │
  │                                              │
  │ → 각 원소에 함수가 적용됩니다!               │
  └─────────────────────────────────────────────┘
""")

# 열에 함수 적용 (각 원소에)
def grade(score):
    """점수를 등급으로 변환"""
    if score >= 95: return 'A+'
    if score >= 90: return 'A'
    if score >= 85: return 'B+'
    if score >= 80: return 'B'
    if score >= 75: return 'C+'
    if score >= 70: return 'C'
    if score >= 65: return 'D'
    return 'F'

math_grades = df.apply_col('수학', grade)
print(f"  수학 점수: {df._data['수학']}")
print(f"  수학 등급: {math_grades}")

# ── Pandas로 하면? ──
# df['수학등급'] = df['수학'].apply(grade)

# lambda와 함께
bonus_scores = df.apply_col('수학', lambda x: x + 5)
print(f"\n  수학 보너스(+5): {bonus_scores}")
# ── Pandas: df['수학'].apply(lambda x: x + 5) ──
# 또는 더 간단하게: df['수학'] + 5

# 행에 함수 적용 (axis=1)
def total_score(row):
    return row['수학'] + row['영어'] + row['국어']

totals = df.apply_row(total_score, cols=['수학', '영어', '국어'])
print(f"\n  행별 총점 계산: {totals}")
# ── Pandas: df.apply(lambda row: row['수학'] + row['영어'] + row['국어'], axis=1) ──

# 복잡한 함수 적용
def evaluate(row):
    """종합 평가"""
    avg = (row['수학'] + row['영어'] + row['국어']) / 3
    if avg >= 90:
        return '우수'
    elif avg >= 80:
        return '보통'
    else:
        return '노력필요'

evaluations = df.apply_row(evaluate, cols=['수학', '영어', '국어'])
print(f"  종합 평가: {evaluations}")
# ── Pandas: df.apply(evaluate, axis=1) ──


# ─────────────────────────────────────────────────────────────────────────
# 3. map() — 값 매핑 (치환)
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 3. map() — 값 매핑")
print("─" * 70)

print("""
  map()은 "이 값을 저 값으로 바꿔!"라는 뜻이에요.

  딕셔너리 매핑:
    {1: '1학년', 2: '2학년', 3: '3학년'}
    → 1이 나오면 '1학년'으로 바꿔!

  함수 매핑:
    str.upper → 모두 대문자로!
""")

# 딕셔너리 매핑
grade_map = {1: '1학년', 2: '2학년', 3: '3학년'}
grade_names = df.map_col('학년', grade_map)
print(f"  학년 숫자: {df._data['학년']}")
print(f"  학년 이름: {grade_names}")
# ── Pandas: df['학년'].map({1: '1학년', 2: '2학년', 3: '3학년'}) ──

# 함수 매핑
name_lengths = df.map_col('이름', len)
print(f"\n  이름:       {df._data['이름']}")
print(f"  이름 길이:  {name_lengths}")
# ── Pandas: df['이름'].map(len) ──

print("""
  💡 apply() vs map() 차이:
  ┌───────────────────────────────────────────┐
  │ map():   Series 전용, 원소별 변환         │
  │          딕셔너리 매핑 가능               │
  │                                           │
  │ apply(): Series + DataFrame 둘 다 가능    │
  │          axis=1로 행 단위도 가능           │
  │          더 복잡한 함수 적용               │
  │                                           │
  │ 단순 치환 → map()                         │
  │ 복잡한 계산 → apply()                     │
  └───────────────────────────────────────────┘
""")

# ── applymap() / map() (DataFrame 전체) ──
# Pandas 2.1+에서는 DataFrame.map()으로 통합!
# df.map(lambda x: x * 2)  # 모든 셀에 적용

print("[applymap/map 개념] 모든 점수를 문자열로 변환:")
for col in ['수학', '영어', '국어']:
    converted = [str(v) + '점' for v in df._data[col]]
    print(f"  {col}: {converted}")
# ── Pandas (2.1+): df[['수학','영어','국어']].map(lambda x: f'{x}점') ──
# ── Pandas (구버전): df[['수학','영어','국어']].applymap(lambda x: f'{x}점') ──


# ─────────────────────────────────────────────────────────────────────────
# 4. replace() — 값 치환
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 4. replace() — 값 치환")
print("─" * 70)

# 단순 치환
replaced = df.replace('이름', '박철수', '박철수(전학생)')
print(f"  원래: {df._data['이름']}")
print(f"  치환: {replaced}")
# ── Pandas: df['이름'].replace('박철수', '박철수(전학생)') ──

# 여러 값 동시 치환
grade_data = [1, 2, 3, 1, 2]
replace_map = {1: 'A반', 2: 'B반', 3: 'C반'}
replaced_grades = [replace_map.get(v, v) for v in grade_data]
print(f"\n  원래: {grade_data}")
print(f"  치환: {replaced_grades}")
# ── Pandas: df['반'].replace({1: 'A반', 2: 'B반', 3: 'C반'}) ──


# ─────────────────────────────────────────────────────────────────────────
# 5. rename() — 이름 변경
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 5. rename() — 이름 변경")
print("─" * 70)

df_renamed = df.rename(columns={'수학': 'Math', '영어': 'English', '국어': 'Korean'})
df_renamed.display("열 이름 변경")
# ── Pandas: df.rename(columns={'수학': 'Math', '영어': 'English'}) ──

# 인덱스 변경
df_idx = df.rename(index={0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e'})
df_idx.display("인덱스 변경")
# ── Pandas: df.rename(index={0: 'a', 1: 'b'}) ──

# 함수로 변경
# ── Pandas: df.rename(columns=str.upper) → 모든 열 이름 대문자로! ──
# ── Pandas: df.columns = ['A', 'B', 'C', 'D', 'E'] → 직접 덮어쓰기 ──


# ─────────────────────────────────────────────────────────────────────────
# 6. sort_values() — 정렬
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 6. sort_values() — 정렬")
print("─" * 70)

# 수학 점수 오름차순
df_asc = df.sort_values('수학', ascending=True)
df_asc.display("수학 오름차순 (낮은→높은)")
# ── Pandas: df.sort_values('수학') ──

# 수학 점수 내림차순
df_desc = df.sort_values('수학', ascending=False)
df_desc.display("수학 내림차순 (높은→낮은)")
# ── Pandas: df.sort_values('수학', ascending=False) ──

# 다중 열 정렬 (학년 → 수학)
df_multi = df.sort_values(['학년', '수학'])
df_multi.display("학년 오름차순 → 수학 오름차순")
# ── Pandas: df.sort_values(['학년', '수학']) ──
# ── Pandas: df.sort_values(['학년', '수학'], ascending=[True, False]) ── # 열별로 다른 방향

# 인덱스 정렬
df_sorted_idx = df_desc.sort_index()
df_sorted_idx.display("인덱스 기준 정렬")
# ── Pandas: df.sort_index() ──


# ─────────────────────────────────────────────────────────────────────────
# 7. rank(), nlargest(), nsmallest() — 순위
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 7. rank(), nlargest(), nsmallest()")
print("─" * 70)

# 순위 매기기
math_ranks = df.rank('수학', ascending=False)
print(f"  이름:     {df._data['이름']}")
print(f"  수학:     {df._data['수학']}")
print(f"  수학순위: {math_ranks}")
# ── Pandas: df['수학'].rank(ascending=False) ──
# ── Pandas 순위 방법: method='average'(기본), 'min', 'max', 'first', 'dense' ──

# 상위 N명
print("\n[nlargest] 수학 상위 3명:")
top3 = df.nlargest(3, '수학')
top3.display()
# ── Pandas: df.nlargest(3, '수학') ──

# 하위 N명
print("\n[nsmallest] 수학 하위 2명:")
bottom2 = df.nsmallest(2, '수학')
bottom2.display()
# ── Pandas: df.nsmallest(2, '수학') ──


# ─────────────────────────────────────────────────────────────────────────
# ★ 실습: 성적 등급 부여 시스템
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "═" * 70)
print(" ★ 실습: 성적 등급 부여 시스템")
print("═" * 70)

# 원본 데이터
students = MiniDF({
    '이름':   ['김민수', '이영희', '박철수', '최지영', '정하늘',
              '한서준', '윤다은', '장예린'],
    '학년':   [3, 3, 2, 3, 2, 1, 1, 2],
    '수학':   [90, 88, 65, 98, 72, 85, 45, 78],
    '영어':   [78, 95, 82, 90, 85, 60, 92, 88],
    '국어':   [85, 85, 90, 82, 88, 75, 78, 95],
})

students.display("원본 학생 데이터")

# 1단계: 총점과 평균 계산
print("\n── 1단계: 총점과 평균 추가 ──")
subjects = ['수학', '영어', '국어']
totals = []
avgs = []
for i in range(students.shape[0]):
    total = sum(students._data[s][i] for s in subjects)
    totals.append(total)
    avgs.append(round(total / len(subjects), 1))

students.add_column('총점', totals)
students.add_column('평균', avgs)
# ── Pandas: ──
# students['총점'] = students[subjects].sum(axis=1)
# students['평균'] = students[subjects].mean(axis=1).round(1)

# 2단계: 등급 부여
print("── 2단계: 등급 부여 ──")
grades = students.apply_col('평균', grade)
students.add_column('등급', grades)
# ── Pandas: students['등급'] = students['평균'].apply(grade) ──

# 3단계: 순위 매기기
print("── 3단계: 순위 매기기 ──")
ranks = students.rank('평균', ascending=False)
students.add_column('순위', ranks)
# ── Pandas: students['순위'] = students['평균'].rank(ascending=False).astype(int) ──

# 4단계: 합격/불합격 판정
print("── 4단계: 합격/불합격 판정 ──")
def pass_fail(row):
    # 모든 과목 60점 이상이고 평균 70점 이상이면 합격
    for s in ['수학', '영어', '국어']:
        if row[s] < 60:
            return '불합격(과목미달)'
    if row['평균'] < 70:
        return '불합격(평균미달)'
    return '합격'

results = students.apply_row(pass_fail, cols=['수학', '영어', '국어', '평균'])
students.add_column('판정', results)
# ── Pandas: ──
# def pass_fail(row):
#     if (row[subjects] < 60).any():
#         return '불합격(과목미달)'
#     if row['평균'] < 70:
#         return '불합격(평균미달)'
#     return '합격'
# students['판정'] = students.apply(pass_fail, axis=1)

# 5단계: 결과 정렬
students_sorted = students.sort_values('평균', ascending=False)
students_sorted.display("최종 성적표 (평균 내림차순)")

# 6단계: 통계 요약
print("\n── 통계 요약 ──")
for subj in subjects:
    vals = students._data[subj]
    avg = sum(vals) / len(vals)
    max_v = max(vals)
    min_v = min(vals)
    max_name = students._data['이름'][vals.index(max_v)]
    min_name = students._data['이름'][vals.index(min_v)]
    print(f"  {subj}: 평균={avg:.1f}, 최고={max_v}({max_name}), 최저={min_v}({min_name})")

# 등급별 학생 수
print("\n  [등급별 학생 수]")
grade_counts = {}
for g in students._data['등급']:
    grade_counts[g] = grade_counts.get(g, 0) + 1
for g in sorted(grade_counts.keys()):
    bar = "█" * grade_counts[g]
    print(f"    {g:>3}: {bar} ({grade_counts[g]}명)")
# ── Pandas: students['등급'].value_counts() ──

# 합격/불합격 집계
print("\n  [합격 현황]")
pass_counts = {}
for p in students._data['판정']:
    pass_counts[p] = pass_counts.get(p, 0) + 1
for p, c in pass_counts.items():
    print(f"    {p}: {c}명")


# ─────────────────────────────────────────────────────────────────────────
# 정리
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "═" * 70)
print(" 정리: 데이터 조작 도구 모음")
print("═" * 70)

print("""
  ┌───────────────┬───────────────────────────────────────┐
  │ 작업          │ Pandas 코드                           │
  ├───────────────┼───────────────────────────────────────┤
  │ 열 추가       │ df['새열'] = 값                       │
  │ 열 삭제       │ df.drop(columns=['열'])               │
  │ 행 삭제       │ df.drop(index=[0, 1])                 │
  │ 함수 적용     │ df['열'].apply(func)                  │
  │ 행 단위 적용  │ df.apply(func, axis=1)                │
  │ 값 매핑       │ df['열'].map(dict 또는 func)          │
  │ 전체 셀 변환  │ df.map(func)  (2.1+)                  │
  │ 값 치환       │ df['열'].replace(old, new)            │
  │ 이름 변경     │ df.rename(columns={old: new})         │
  │ 값 정렬       │ df.sort_values('열')                  │
  │ 인덱스 정렬   │ df.sort_index()                       │
  │ 순위          │ df['열'].rank()                       │
  │ 상위 N개      │ df.nlargest(n, '열')                  │
  │ 하위 N개      │ df.nsmallest(n, '열')                 │
  └───────────────┴───────────────────────────────────────┘
""")

print("✅ 03단계 완료! 다음은 04_missing_data.py에서 결측값 처리를 배워요!")
