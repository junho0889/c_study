# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   Pandas 학습 02단계: 인덱싱과 선택
#   ─ loc, iloc, Boolean indexing, 조건 필터링 ─
#   ■ 실행 방법: python 02_indexing_selection.py
#   ■ Pandas 설치: pip install pandas
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# =========================================================================
#  데이터를 "선택"하는 건 가장 중요한 기술이에요!
# =========================================================================
#
#  엑셀에서 특정 셀을 클릭하거나, 범위를 드래그하는 것처럼
#  Pandas에서도 원하는 행/열을 골라내는 방법이 있어요.
#
#  크게 4가지:
#    1) loc  — 라벨(이름)으로 선택    "민수의 수학 점수"
#    2) iloc — 위치(번호)로 선택      "0번째 행, 1번째 열"
#    3) Boolean — 조건으로 선택       "80점 이상인 학생"
#    4) at/iat — 단일 값 빠르게 접근
# =========================================================================

print("=" * 70)
print(" 02단계: 인덱싱과 선택 (Indexing & Selection)")
print("=" * 70)


# ── 테스트용 DataFrame (순수 파이썬) ──

class SimpleDF:
    """인덱싱 학습을 위한 간단한 DataFrame"""

    def __init__(self, data, index=None):
        self._columns = list(data.keys())
        first_col = self._columns[0]
        n_rows = len(data[first_col])
        self._data = {col: list(data[col]) for col in self._columns}
        self._index = list(index) if index else list(range(n_rows))

    @property
    def shape(self):
        return (len(self._index), len(self._columns))

    def _display(self, rows=None, cols=None):
        """선택된 행/열만 출력"""
        if rows is None:
            rows = list(range(len(self._index)))
        if cols is None:
            cols = self._columns

        # 헤더
        idx_w = max(len(str(self._index[r])) for r in rows) + 2 if rows else 4
        col_widths = {}
        for c in cols:
            w = len(str(c))
            for r in rows:
                w = max(w, len(str(self._data[c][r])))
            col_widths[c] = w + 2

        header = " " * idx_w + "".join(f"{c:>{col_widths[c]}}" for c in cols)
        print(header)
        print("  " + "─" * (len(header) - 2))
        for r in rows:
            line = f"{str(self._index[r]):<{idx_w}}"
            for c in cols:
                line += f"{str(self._data[c][r]):>{col_widths[c]}}"
            print(line)

    def __repr__(self):
        import io
        self._display()
        return ""

    # ─── loc: 라벨 기반 선택 ───
    def loc(self, row_label, col_label=None):
        """
        라벨(이름)으로 데이터 선택.

        Pandas에서:
          df.loc['민수', '수학']       → 단일 값
          df.loc['민수':'철수', '수학'] → 슬라이스 (끝 포함!)
          df.loc[['민수','철수'], ['수학','영어']] → 여러 행/열
        """
        # 단일 행 라벨
        if isinstance(row_label, str) and row_label in self._index:
            ri = self._index.index(row_label)
            if col_label is None:
                # 행 전체 반환
                result = {col: self._data[col][ri] for col in self._columns}
                return result
            elif isinstance(col_label, str):
                # 단일 값
                return self._data[col_label][ri]
            elif isinstance(col_label, list):
                # 여러 열
                return {col: self._data[col][ri] for col in col_label}

        # 여러 행 라벨 (리스트)
        if isinstance(row_label, list):
            row_indices = [self._index.index(r) for r in row_label]
            if col_label is None:
                cols = self._columns
            elif isinstance(col_label, list):
                cols = col_label
            else:
                cols = [col_label]
            result = {}
            for c in cols:
                result[c] = [self._data[c][ri] for ri in row_indices]
            return SimpleDF(result, index=row_label)

        # 슬라이스 (라벨 기반 — 끝 포함!)
        if isinstance(row_label, tuple) and len(row_label) == 2:
            start_label, end_label = row_label
            si = self._index.index(start_label)
            ei = self._index.index(end_label) + 1  # loc는 끝 포함!
            row_indices = list(range(si, ei))
            if col_label is None:
                cols = self._columns
            elif isinstance(col_label, list):
                cols = col_label
            else:
                cols = [col_label]
            new_idx = [self._index[ri] for ri in row_indices]
            result = {}
            for c in cols:
                result[c] = [self._data[c][ri] for ri in row_indices]
            return SimpleDF(result, index=new_idx)

        raise KeyError(f"'{row_label}' 를 찾을 수 없어요!")

    # ─── iloc: 위치 기반 선택 ───
    def iloc(self, row_pos, col_pos=None):
        """
        위치(정수 번호)로 데이터 선택.

        Pandas에서:
          df.iloc[0, 1]      → 0행 1열의 값
          df.iloc[0:3, 1:3]  → 슬라이스 (끝 미포함! 파이썬 규칙)
          df.iloc[[0,2], [1,3]] → 여러 행/열
        """
        # 단일 행
        if isinstance(row_pos, int):
            if col_pos is None:
                return {col: self._data[col][row_pos] for col in self._columns}
            elif isinstance(col_pos, int):
                return self._data[self._columns[col_pos]][row_pos]
            elif isinstance(col_pos, list):
                cols = [self._columns[ci] for ci in col_pos]
                return {c: self._data[c][row_pos] for c in cols}

        # 여러 행 (리스트)
        if isinstance(row_pos, list):
            if col_pos is None:
                col_indices = list(range(len(self._columns)))
            elif isinstance(col_pos, list):
                col_indices = col_pos
            else:
                col_indices = [col_pos]
            cols = [self._columns[ci] for ci in col_indices]
            new_idx = [self._index[ri] for ri in row_pos]
            result = {c: [self._data[c][ri] for ri in row_pos] for c in cols}
            return SimpleDF(result, index=new_idx)

        # 슬라이스 (위치 기반 — 끝 미포함!)
        if isinstance(row_pos, tuple) and len(row_pos) == 2:
            si, ei = row_pos  # iloc는 끝 미포함! (파이썬 규칙)
            row_indices = list(range(si, ei))
            if col_pos is None:
                cols = self._columns
            elif isinstance(col_pos, tuple):
                cs, ce = col_pos
                cols = self._columns[cs:ce]
            else:
                cols = self._columns
            new_idx = [self._index[ri] for ri in row_indices]
            result = {c: [self._data[c][ri] for ri in row_indices] for c in cols}
            return SimpleDF(result, index=new_idx)

        raise IndexError(f"잘못된 위치: {row_pos}")

    # ─── at/iat: 단일 값 빠른 접근 ───
    def at(self, row_label, col_label):
        """단일 값 접근 (라벨 기반). loc보다 빠름!"""
        ri = self._index.index(row_label)
        return self._data[col_label][ri]

    def iat(self, row_pos, col_pos):
        """단일 값 접근 (위치 기반). iloc보다 빠름!"""
        return self._data[self._columns[col_pos]][row_pos]

    # ─── Boolean Indexing ───
    def where(self, col, op, value):
        """
        조건으로 행 필터링.

        Pandas에서:
          df[df['수학'] > 80]
          df[df['이름'] == '민수']
        """
        import operator
        ops = {
            '>': operator.gt, '<': operator.lt,
            '>=': operator.ge, '<=': operator.le,
            '==': operator.eq, '!=': operator.ne,
        }
        op_func = ops[op]

        # 1단계: 불리언 마스크 만들기
        mask = [op_func(v, value) for v in self._data[col]]

        # 2단계: True인 행만 선택
        selected_rows = [i for i, m in enumerate(mask) if m]
        new_idx = [self._index[ri] for ri in selected_rows]
        result = {}
        for c in self._columns:
            result[c] = [self._data[c][ri] for ri in selected_rows]
        return SimpleDF(result, index=new_idx), mask

    def multi_where(self, conditions, logic='and'):
        """
        다중 조건 필터링.

        Pandas에서:
          df[(df['수학'] > 80) & (df['영어'] > 80)]   # AND
          df[(df['수학'] > 90) | (df['영어'] > 90)]   # OR
          df[~(df['수학'] > 80)]                       # NOT
        """
        masks = []
        for col, op, value in conditions:
            _, mask = self.where(col, op, value)
            masks.append(mask)

        if logic == 'and':
            combined = [all(m[i] for m in masks) for i in range(len(self._index))]
        elif logic == 'or':
            combined = [any(m[i] for m in masks) for i in range(len(self._index))]
        elif logic == 'not':
            combined = [not masks[0][i] for i in range(len(self._index))]
        else:
            combined = masks[0]

        selected_rows = [i for i, m in enumerate(combined) if m]
        new_idx = [self._index[ri] for ri in selected_rows]
        result = {}
        for c in self._columns:
            result[c] = [self._data[c][ri] for ri in selected_rows]
        return SimpleDF(result, index=new_idx)

    def query(self, col, op, value):
        """
        query() 스타일 필터링.

        Pandas에서:
          df.query('수학 > 80')
          df.query('학년 == 3 and 수학 > 85')
        """
        result, _ = self.where(col, op, value)
        return result


# ─── 테스트 데이터 ───
students = SimpleDF(
    {
        '이름': ['김민수', '이영희', '박철수', '최지영', '정하늘', '한서준', '윤다은'],
        '학년': [3, 3, 2, 3, 2, 1, 1],
        '반':   [1, 2, 1, 2, 1, 1, 2],
        '수학': [90, 88, 65, 98, 72, 85, 45],
        '영어': [78, 95, 82, 90, 85, 60, 92],
        '국어': [85, 85, 90, 82, 88, 75, 78],
    },
    index=['s001', 's002', 's003', 's004', 's005', 's006', 's007']
)

print("\n[원본 데이터]")
students._display()


# ─────────────────────────────────────────────────────────────────────────
# 1. loc — 라벨(이름) 기반 선택
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 1. loc — 라벨(이름) 기반 선택")
print("─" * 70)

# 단일 행
print("\n[loc] s001 학생의 모든 정보:")
row = students.loc('s001')
for k, v in row.items():
    print(f"  {k}: {v}")

# ── Pandas: df.loc['s001'] ──

# 단일 값
print(f"\n[loc] s002 학생의 수학 점수: {students.loc('s002', '수학')}")
# ── Pandas: df.loc['s002', '수학'] ──

# 여러 열
print(f"\n[loc] s003 학생의 수학, 영어:")
result = students.loc('s003', ['수학', '영어'])
for k, v in result.items():
    print(f"  {k}: {v}")
# ── Pandas: df.loc['s003', ['수학', '영어']] ──

# 여러 행 + 여러 열
print("\n[loc] s001, s003, s005 학생의 이름과 수학:")
sub = students.loc(['s001', 's003', 's005'], ['이름', '수학'])
sub._display()
# ── Pandas: df.loc[['s001','s003','s005'], ['이름','수학']] ──

# 슬라이스 (라벨 기반 — 끝 포함!)
print("\n[loc] s002~s004 범위 (끝 포함!):")
sub2 = students.loc(('s002', 's004'))
sub2._display()
# ── Pandas: df.loc['s002':'s004'] ──
# ⚠️ loc 슬라이스는 끝 라벨을 포함해요! (iloc과 다른 점)

print("""
  💡 loc 핵심 규칙:
  ┌──────────────────────────────────────────┐
  │ df.loc[행라벨]             → 행 선택     │
  │ df.loc[행라벨, 열라벨]     → 단일 값     │
  │ df.loc[[행1,행2], [열1,열2]] → 부분표    │
  │ df.loc['a':'c']          → 슬라이스     │
  │                          (끝 포함!)      │
  └──────────────────────────────────────────┘
""")


# ─────────────────────────────────────────────────────────────────────────
# 2. iloc — 위치(번호) 기반 선택
# ─────────────────────────────────────────────────────────────────────────

print("─" * 70)
print(" 2. iloc — 위치(번호) 기반 선택")
print("─" * 70)

# 단일 행 (0번째 행)
print("\n[iloc] 0번째 행 (첫 번째 학생):")
row = students.iloc(0)
for k, v in row.items():
    print(f"  {k}: {v}")
# ── Pandas: df.iloc[0] ──

# 단일 값 (0번째 행, 3번째 열)
val = students.iloc(0, 3)
print(f"\n[iloc] 0행 3열의 값: {val}")
# ── Pandas: df.iloc[0, 3] ──

# 여러 행/열 (리스트)
print("\n[iloc] [0, 2, 4]행, [0, 3]열:")
sub = students.iloc([0, 2, 4], [0, 3])
sub._display()
# ── Pandas: df.iloc[[0,2,4], [0,3]] ──

# 슬라이스 (위치 기반 — 끝 미포함!)
print("\n[iloc] 1~3행 범위 (끝 미포함!):")
sub2 = students.iloc((1, 4))  # 1,2,3 (4 미포함)
sub2._display()
# ── Pandas: df.iloc[1:4] ──
# ⚠️ iloc 슬라이스는 끝 번호를 미포함! (파이썬 리스트와 같은 규칙)

print("""
  💡 iloc 핵심 규칙:
  ┌──────────────────────────────────────────┐
  │ df.iloc[행번호]             → 행 선택    │
  │ df.iloc[행번호, 열번호]     → 단일 값    │
  │ df.iloc[[0,2], [1,3]]     → 부분표      │
  │ df.iloc[1:4]              → 슬라이스    │
  │                          (끝 미포함!)    │
  └──────────────────────────────────────────┘
""")


# ─────────────────────────────────────────────────────────────────────────
# 3. loc vs iloc 비교
# ─────────────────────────────────────────────────────────────────────────

print("─" * 70)
print(" 3. loc vs iloc 비교")
print("─" * 70)

print("""
  ┌────────────┬────────────────────┬────────────────────┐
  │            │       loc          │       iloc         │
  ├────────────┼────────────────────┼────────────────────┤
  │ 기준       │ 라벨(이름)         │ 위치(정수 번호)    │
  │ 행 선택    │ df.loc['s001']     │ df.iloc[0]         │
  │ 값 선택    │ df.loc['s001','수학']│ df.iloc[0, 3]     │
  │ 슬라이스   │ 끝 포함!           │ 끝 미포함!         │
  │ 사용 시점  │ 라벨을 알 때       │ 위치만 알 때       │
  └────────────┴────────────────────┴────────────────────┘

  기억하기 쉬운 팁:
    loc  = label-oriented  (라벨!)
    iloc = integer-oriented (정수!)
""")


# ─────────────────────────────────────────────────────────────────────────
# 4. at / iat — 단일 값 빠른 접근
# ─────────────────────────────────────────────────────────────────────────

print("─" * 70)
print(" 4. at / iat — 단일 값 빠른 접근")
print("─" * 70)

# at: 라벨로 단일 값 (loc보다 빠름!)
val1 = students.at('s001', '수학')
print(f"\n[at] s001의 수학 점수: {val1}")
# ── Pandas: df.at['s001', '수학'] ──

# iat: 위치로 단일 값 (iloc보다 빠름!)
val2 = students.iat(0, 3)
print(f"[iat] 0행 3열의 값: {val2}")
# ── Pandas: df.iat[0, 3] ──

print("""
  💡 at/iat는 언제 쓰나요?
  → "딱 하나의 값"만 가져올 때!
  → loc/iloc보다 빠릅니다 (오버헤드가 적어서)
  → 반복문 안에서 값을 읽을 때 특히 유용해요
""")


# ─────────────────────────────────────────────────────────────────────────
# 5. Boolean Indexing — 조건으로 선택
# ─────────────────────────────────────────────────────────────────────────

print("─" * 70)
print(" 5. Boolean Indexing — 조건으로 선택")
print("─" * 70)

# Boolean 마스크가 뭐예요?
# → True/False로 된 리스트!
# → True인 행만 선택됩니다

print("\n[1단계] 불리언 마스크 만들기")
math_scores = students._data['수학']
mask = [score > 80 for score in math_scores]
print(f"  수학 점수:  {math_scores}")
print(f"  > 80 마스크: {mask}")
print(f"  → True인 위치의 학생만 선택됩니다!")

# ── Pandas: df['수학'] > 80 → Series([True, True, False, True, False, True, False])

print("\n[2단계] 마스크로 필터링")
filtered, _ = students.where('수학', '>', 80)
print("  수학 80점 초과 학생:")
filtered._display()

# ── Pandas: df[df['수학'] > 80] ──

# 다양한 조건
print("\n[다양한 조건 예제]")

# 수학 90점 이상
print("\n  ▶ 수학 90점 이상:")
r, _ = students.where('수학', '>=', 90)
r._display()
# ── Pandas: df[df['수학'] >= 90] ──

# 3학년 학생
print("\n  ▶ 3학년 학생:")
r, _ = students.where('학년', '==', 3)
r._display()
# ── Pandas: df[df['학년'] == 3] ──

# 영어 80점 미만
print("\n  ▶ 영어 80점 미만:")
r, _ = students.where('영어', '<', 80)
r._display()
# ── Pandas: df[df['영어'] < 80] ──

print("""
  💡 Boolean Indexing 원리:
  ┌───────────────────────────────────────────┐
  │ 1) df['수학'] > 80                        │
  │    → [True, True, False, True, ...]       │
  │                                           │
  │ 2) df[mask]                               │
  │    → True인 행만 골라서 새 DataFrame!      │
  │                                           │
  │ 마치 체로 거르는 것과 같아요!              │
  │ 조건에 맞는 것만 통과! ⬇️                  │
  └───────────────────────────────────────────┘
""")


# ─────────────────────────────────────────────────────────────────────────
# 6. 다중 조건 — AND (&), OR (|), NOT (~)
# ─────────────────────────────────────────────────────────────────────────

print("─" * 70)
print(" 6. 다중 조건 — AND, OR, NOT")
print("─" * 70)

# AND: 수학 > 80 그리고 영어 > 80
print("\n[AND] 수학 > 80 AND 영어 > 80:")
r = students.multi_where([('수학', '>', 80), ('영어', '>', 80)], logic='and')
r._display()
# ── Pandas: df[(df['수학'] > 80) & (df['영어'] > 80)] ──
# ⚠️ 괄호 필수! & 연산자 우선순위 때문

# OR: 수학 > 90 또는 영어 > 90
print("\n[OR] 수학 > 90 OR 영어 > 90:")
r = students.multi_where([('수학', '>', 90), ('영어', '>', 90)], logic='or')
r._display()
# ── Pandas: df[(df['수학'] > 90) | (df['영어'] > 90)] ──

# NOT: 수학 80 초과가 아닌 학생 (= 80 이하)
print("\n[NOT] NOT (수학 > 80) → 수학 80 이하:")
r = students.multi_where([('수학', '>', 80)], logic='not')
r._display()
# ── Pandas: df[~(df['수학'] > 80)] ──

print("""
  💡 다중 조건 규칙:
  ┌───────────────────────────────────────────┐
  │ AND: (조건1) & (조건2)  → 둘 다 만족     │
  │ OR:  (조건1) | (조건2)  → 하나만 만족     │
  │ NOT: ~(조건)            → 조건의 반대     │
  │                                           │
  │ ⚠️ Pandas에서는 각 조건을 괄호()로        │
  │    감싸야 해요! (연산자 우선순위 때문)     │
  │                                           │
  │ 예: df[(df['A'] > 5) & (df['B'] < 10)]   │
  │     괄호 빼면 에러! ❌                     │
  └───────────────────────────────────────────┘
""")


# ─────────────────────────────────────────────────────────────────────────
# 7. query() 메서드 — 문자열로 조건 쓰기
# ─────────────────────────────────────────────────────────────────────────

print("─" * 70)
print(" 7. query() 메서드")
print("─" * 70)

print("\n[query] 수학 > 85:")
r = students.query('수학', '>', 85)
r._display()

# ── Pandas로 하면? ──
# df.query('수학 > 85')                    # 단일 조건
# df.query('수학 > 85 and 영어 > 80')      # 다중 조건
# df.query('학년 == 3 and 반 == 1')        # 여러 열 조건
#
# 변수 참조할 때는 @ 사용:
# min_score = 80
# df.query('수학 > @min_score')

print("""
  💡 query()의 장점:
  ┌───────────────────────────────────────────────┐
  │ Boolean indexing:                             │
  │   df[(df['수학'] > 85) & (df['영어'] > 80)]   │
  │                                               │
  │ query():                                      │
  │   df.query('수학 > 85 and 영어 > 80')         │
  │                                               │
  │ → 읽기 더 쉽고, 타이핑도 적어요!              │
  │ → 특히 열 이름이 한글이면 query가 편해요      │
  └───────────────────────────────────────────────┘
""")


# ─────────────────────────────────────────────────────────────────────────
# 8. 열 선택 방법 정리
# ─────────────────────────────────────────────────────────────────────────

print("─" * 70)
print(" 8. 열 선택 방법 정리")
print("─" * 70)

print("""
  Pandas에서 열을 선택하는 방법들:

  1) 단일 열 → Series 반환
     df['수학']
     df.수학          (열 이름이 영문일 때만 가능)

  2) 여러 열 → DataFrame 반환
     df[['수학', '영어']]       (리스트로 감싸기!)
     df.loc[:, ['수학', '영어']] (loc 사용)

  3) 열 범위
     df.loc[:, '수학':'국어']    (loc 슬라이스)
     df.iloc[:, 1:4]            (iloc 슬라이스)

  ⚠️ 주의사항:
     df['수학']    → OK (Series)
     df[['수학']]  → OK (DataFrame, 열 1개짜리)
     → 대괄호 1개 vs 2개가 결과 타입이 달라요!
""")

# 순수 파이썬으로 시연
print("[단일 열 선택] 수학 점수:")
math_only = [students._data['수학'][i] for i in range(students.shape[0])]
for idx, val in zip(students._index, math_only):
    print(f"  {idx}: {val}")

print("\n[여러 열 선택] 이름, 수학, 영어:")
selected_cols = ['이름', '수학', '영어']
sub = students.loc(students._index, selected_cols)
sub._display()


# ─────────────────────────────────────────────────────────────────────────
# ★ 실습: 조건별 학생 필터링
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "═" * 70)
print(" ★ 실습: 조건별 학생 필터링")
print("═" * 70)

# 전체 데이터 확인
print("\n[전체 학생 데이터]")
students._display()

# 과제 1: 수학 85점 이상인 학생의 이름과 수학 점수
print("\n── 과제 1: 수학 85점 이상 학생 ──")
filtered, _ = students.where('수학', '>=', 85)
for i in range(len(filtered._index)):
    name = filtered._data['이름'][i]
    score = filtered._data['수학'][i]
    print(f"  {name}: {score}점")
# ── Pandas: df.loc[df['수학'] >= 85, ['이름', '수학']] ──

# 과제 2: 3학년이면서 영어 85점 이상
print("\n── 과제 2: 3학년 AND 영어 85점 이상 ──")
r = students.multi_where([('학년', '==', 3), ('영어', '>=', 85)], logic='and')
r._display()
# ── Pandas: df[(df['학년'] == 3) & (df['영어'] >= 85)] ──

# 과제 3: 수학 또는 영어가 90점 이상인 학생
print("\n── 과제 3: 수학 >= 90 OR 영어 >= 90 ──")
r = students.multi_where([('수학', '>=', 90), ('영어', '>=', 90)], logic='or')
r._display()
# ── Pandas: df[(df['수학'] >= 90) | (df['영어'] >= 90)] ──

# 과제 4: 모든 과목 평균 계산 후 상위 3명
print("\n── 과제 4: 전과목 평균 상위 3명 ──")
subjects = ['수학', '영어', '국어']
averages = []
for i in range(students.shape[0]):
    avg = sum(students._data[s][i] for s in subjects) / len(subjects)
    averages.append(round(avg, 1))

name_avg_pairs = list(zip(students._data['이름'], averages))
name_avg_pairs.sort(key=lambda x: x[1], reverse=True)
for rank, (name, avg) in enumerate(name_avg_pairs[:3], 1):
    print(f"  {rank}등: {name} (평균: {avg})")
# ── Pandas: ──
# df['평균'] = df[['수학', '영어', '국어']].mean(axis=1)
# df.nlargest(3, '평균')[['이름', '평균']]

# 과제 5: 특정 학생 정보 수정 (at 활용 개념)
print("\n── 과제 5: s007 학생의 수학 점수 수정 ──")
print(f"  수정 전: {students.at('s007', '수학')}")
students._data['수학'][students._index.index('s007')] = 70
print(f"  수정 후: {students.at('s007', '수학')}")
# ── Pandas: df.at['s007', '수학'] = 70 ──


# ─────────────────────────────────────────────────────────────────────────
# 정리
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "═" * 70)
print(" 정리: 인덱싱 방법 총정리")
print("═" * 70)

print("""
  ┌──────────┬─────────────────┬─────────────────────────────────┐
  │ 방법     │ 기준            │ 사용 예                         │
  ├──────────┼─────────────────┼─────────────────────────────────┤
  │ df[col]  │ 열 이름         │ df['수학']                      │
  │ loc      │ 라벨(이름)      │ df.loc['s001', '수학']          │
  │ iloc     │ 위치(정수)      │ df.iloc[0, 3]                   │
  │ at       │ 라벨, 단일값    │ df.at['s001', '수학']           │
  │ iat      │ 위치, 단일값    │ df.iat[0, 3]                    │
  │ Boolean  │ 조건식          │ df[df['수학'] > 80]             │
  │ query    │ 문자열 조건     │ df.query('수학 > 80')           │
  └──────────┴─────────────────┴─────────────────────────────────┘

  loc vs iloc 슬라이스 차이:
    loc['a':'c']  → 'a', 'b', 'c' (끝 포함!)
    iloc[0:3]     → 0, 1, 2       (끝 미포함!)
""")

print("✅ 02단계 완료! 다음은 03_data_manipulation.py에서 데이터 조작을 배워요!")
