# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   Pandas 학습 06단계: Merge & Join (테이블 결합)
#   ─ concat, merge(inner/left/right/outer), join, 키 충돌 처리 ─
#   ■ 실행 방법: python 06_merge_join.py
#   ■ Pandas 설치: pip install pandas
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# =========================================================================
#  테이블 결합이 왜 필요할까요?
# =========================================================================
#
#  현실에서 데이터는 여러 테이블로 나뉘어 있어요:
#    - 학생 기본정보 테이블
#    - 성적 테이블
#    - 동아리 테이블
#
#  이 테이블들을 합쳐서 하나로 만들어야 분석할 수 있어요!
#  SQL의 JOIN, 엑셀의 VLOOKUP과 비슷한 개념입니다.
# =========================================================================

print("=" * 70)
print(" 06단계: Merge & Join (테이블 결합)")
print("=" * 70)


class JoinDF:
    """테이블 결합 학습용 DataFrame"""

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
                w = max(w, len(str(v) if v is not None else 'NaN'))
            col_w[c] = w + 2
        header = " " * idx_w + "".join(f"{c:>{col_w[c]}}" for c in self._columns)
        print(header)
        print("  " + "─" * (len(header) - 2))
        for ri, idx in enumerate(self._index):
            line = f"{str(idx):<{idx_w}}"
            for c in self._columns:
                val = self._data[c][ri]
                display_val = str(val) if val is not None else 'NaN'
                line += f"{display_val:>{col_w[c]}}"
            print(line)
        print(f"  [{self.shape[0]} rows x {self.shape[1]} cols]")


# ─────────────────────────────────────────────────────────────────────────
# 1. concat() — 위아래/좌우 합치기
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 1. concat() — 단순 합치기")
print("─" * 70)

print("""
  concat()은 "단순히 테이블을 이어 붙이는" 도구예요.

  위아래로 (axis=0):       좌우로 (axis=1):
  ┌───────┐               ┌────┬────┐
  │  A B  │               │A B │C D │
  │ 1 2   │               │1 2 │5 6 │
  │ 3 4   │               │3 4 │7 8 │
  ├───────┤               └────┴────┘
  │  A B  │
  │ 5 6   │
  │ 7 8   │
  └───────┘
""")

def concat_vertical(dfs, ignore_index=False):
    """
    위아래로 합치기 (axis=0).

    Pandas에서:
      pd.concat([df1, df2], ignore_index=True)
    """
    # 모든 열 합집합
    all_cols = []
    for df in dfs:
        for c in df._columns:
            if c not in all_cols:
                all_cols.append(c)

    result_data = {c: [] for c in all_cols}

    for df in dfs:
        n = len(df._index)
        for c in all_cols:
            if c in df._data:
                result_data[c].extend(df._data[c])
            else:
                result_data[c].extend([None] * n)

    if ignore_index:
        idx = list(range(len(result_data[all_cols[0]])))
    else:
        idx = []
        for df in dfs:
            idx.extend(df._index)

    return JoinDF(result_data, index=idx)


def concat_horizontal(dfs):
    """
    좌우로 합치기 (axis=1).

    Pandas에서:
      pd.concat([df1, df2], axis=1)
    """
    result_data = {}
    for df in dfs:
        for c in df._columns:
            result_data[c] = list(df._data[c])
    max_len = max(len(v) for v in result_data.values())
    for c in result_data:
        while len(result_data[c]) < max_len:
            result_data[c].append(None)
    return JoinDF(result_data)


# 위아래 합치기 예시
class_a = JoinDF({
    '이름': ['김민수', '이영희'],
    '점수': [90, 88],
})
class_b = JoinDF({
    '이름': ['박철수', '최지영'],
    '점수': [75, 98],
})

class_a.display("A반")
class_b.display("B반")

result = concat_vertical([class_a, class_b], ignore_index=True)
result.display("위아래 합치기 (ignore_index=True)")
# ── Pandas: pd.concat([class_a, class_b], ignore_index=True) ──

# 좌우 합치기
scores_df = JoinDF({'수학': [90, 88, 75], '영어': [78, 95, 82]})
extra_df = JoinDF({'국어': [85, 85, 90], '과학': [88, 92, 78]})
result2 = concat_horizontal([scores_df, extra_df])
result2.display("좌우 합치기 (axis=1)")
# ── Pandas: pd.concat([scores_df, extra_df], axis=1) ──


# ─────────────────────────────────────────────────────────────────────────
# 2. merge() — 키(Key) 기반 결합
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 2. merge() — 키 기반 결합")
print("─" * 70)

print("""
  merge()는 두 테이블에서 "공통 열(키)"을 기준으로 합치는 도구예요.
  SQL의 JOIN과 동일한 개념입니다!

  학생정보:                  성적:
  학번  이름                 학번  수학  영어
  001   민수                 001   90    78
  002   영희                 002   88    95
  003   철수                 003   75    82

  → 학번을 키로 merge하면?

  학번  이름  수학  영어
  001   민수  90    78
  002   영희  88    95
  003   철수  75    82
""")


def merge(left, right, on=None, left_on=None, right_on=None,
          how='inner', suffixes=('_x', '_y')):
    """
    키 기반 테이블 결합.

    Pandas에서:
      pd.merge(df1, df2, on='학번')                       # 공통 키
      pd.merge(df1, df2, left_on='ID', right_on='학번')   # 다른 키 이름
      pd.merge(df1, df2, on='학번', how='left')            # LEFT JOIN
    """
    # 키 열 결정
    if on:
        left_key = on
        right_key = on
    else:
        left_key = left_on
        right_key = right_on

    # 왼쪽 키 → 인덱스 매핑
    left_map = {}
    for i in range(len(left._index)):
        key = left._data[left_key][i]
        if key not in left_map:
            left_map[key] = []
        left_map[key].append(i)

    # 오른쪽 키 → 인덱스 매핑
    right_map = {}
    for i in range(len(right._index)):
        key = right._data[right_key][i]
        if key not in right_map:
            right_map[key] = []
        right_map[key].append(i)

    # 결과 열 결정 (키 열 중복 제거)
    result_cols = list(left._columns)
    for c in right._columns:
        if c == right_key and right_key == left_key:
            continue  # 키 열은 한 번만
        if c in result_cols:
            # 이름 충돌 시 접미사 추가
            result_cols.append(c + suffixes[1])
            # 왼쪽도 접미사 추가
            idx = result_cols.index(c)
            result_cols[idx] = c + suffixes[0]
        else:
            result_cols.append(c)

    result_data = {c: [] for c in result_cols}

    # 키 집합 결정
    all_keys_left = set(left_map.keys())
    all_keys_right = set(right_map.keys())

    if how == 'inner':
        keys_to_process = all_keys_left & all_keys_right
        include_left_only = False
        include_right_only = False
    elif how == 'left':
        keys_to_process = all_keys_left & all_keys_right
        include_left_only = True
        include_right_only = False
    elif how == 'right':
        keys_to_process = all_keys_left & all_keys_right
        include_left_only = False
        include_right_only = True
    elif how == 'outer':
        keys_to_process = all_keys_left & all_keys_right
        include_left_only = True
        include_right_only = True
    else:
        keys_to_process = all_keys_left & all_keys_right
        include_left_only = False
        include_right_only = False

    def add_row(left_idx, right_idx):
        for c in result_cols:
            # 왼쪽 데이터
            original_left_col = c.rstrip(suffixes[0]) if c.endswith(suffixes[0]) else c
            original_right_col = c.rstrip(suffixes[1]) if c.endswith(suffixes[1]) else c

            if c.endswith(suffixes[0]) and original_left_col in left._columns:
                val = left._data[original_left_col][left_idx] if left_idx is not None else None
            elif c.endswith(suffixes[1]) and original_right_col in right._columns:
                val = right._data[original_right_col][right_idx] if right_idx is not None else None
            elif c in left._columns and left_idx is not None:
                val = left._data[c][left_idx]
            elif c in right._columns and right_idx is not None:
                val = right._data[c][right_idx]
            else:
                val = None
            result_data[c].append(val)

    # 매칭되는 키
    for key in sorted(keys_to_process):
        for li in left_map[key]:
            for ri in right_map[key]:
                add_row(li, ri)

    # 왼쪽에만 있는 키
    if include_left_only:
        for key in sorted(all_keys_left - all_keys_right):
            for li in left_map[key]:
                add_row(li, None)

    # 오른쪽에만 있는 키
    if include_right_only:
        for key in sorted(all_keys_right - all_keys_left):
            for ri in right_map[key]:
                add_row(None, ri)

    return JoinDF(result_data)


# ─── 테스트 데이터 ───
students_info = JoinDF({
    '학번': ['S001', 'S002', 'S003', 'S004', 'S005'],
    '이름': ['김민수', '이영희', '박철수', '최지영', '정하늘'],
    '학년': [3, 3, 2, 3, 2],
})

scores = JoinDF({
    '학번': ['S001', 'S002', 'S003', 'S004', 'S006'],
    '수학': [90, 88, 65, 98, 85],
    '영어': [78, 95, 82, 90, 60],
})

clubs = JoinDF({
    '학번': ['S001', 'S002', 'S005', 'S006'],
    '동아리': ['축구부', '밴드부', '미술부', '축구부'],
})

students_info.display("학생 기본정보")
scores.display("성적")
clubs.display("동아리")


# ─────────────────────────────────────────────────────────────────────────
# 3. merge 종류: inner, left, right, outer
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 3. merge 종류 — 4가지 JOIN")
print("─" * 70)

print("""
  4가지 JOIN 방식:

  학생정보: S001~S005        성적: S001~S004, S006

  ┌─ INNER JOIN ──────────────────────────────┐
  │ 양쪽 모두에 있는 것만 (교집합)             │
  │ → S001, S002, S003, S004                  │
  │ S005(학생만), S006(성적만) 제외            │
  └────────────────────────────────────────────┘

  ┌─ LEFT JOIN ───────────────────────────────┐
  │ 왼쪽(학생)은 전부 + 오른쪽(성적)은 매칭만  │
  │ → S001~S005 (S005는 성적=NaN)             │
  │ S006 제외                                  │
  └────────────────────────────────────────────┘

  ┌─ RIGHT JOIN ──────────────────────────────┐
  │ 오른쪽(성적)은 전부 + 왼쪽(학생)은 매칭만  │
  │ → S001~S004, S006 (S006은 이름=NaN)       │
  │ S005 제외                                  │
  └────────────────────────────────────────────┘

  ┌─ OUTER JOIN ──────────────────────────────┐
  │ 양쪽 모두 포함 (합집합)                    │
  │ → S001~S006 (없는 값은 NaN)               │
  └────────────────────────────────────────────┘
""")

# INNER JOIN (기본값)
print("[INNER JOIN] 양쪽 다 있는 학번만:")
inner = merge(students_info, scores, on='학번', how='inner')
inner.display()
# ── Pandas: pd.merge(students_info, scores, on='학번', how='inner') ──

# LEFT JOIN
print("\n[LEFT JOIN] 학생 전부 + 성적은 있는 것만:")
left = merge(students_info, scores, on='학번', how='left')
left.display()
# ── Pandas: pd.merge(students_info, scores, on='학번', how='left') ──

# RIGHT JOIN
print("\n[RIGHT JOIN] 성적 전부 + 학생은 있는 것만:")
right = merge(students_info, scores, on='학번', how='right')
right.display()
# ── Pandas: pd.merge(students_info, scores, on='학번', how='right') ──

# OUTER JOIN
print("\n[OUTER JOIN] 양쪽 모두 포함:")
outer = merge(students_info, scores, on='학번', how='outer')
outer.display()
# ── Pandas: pd.merge(students_info, scores, on='학번', how='outer') ──


# ─────────────────────────────────────────────────────────────────────────
# 4. 다른 이름의 키 열 — left_on, right_on
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 4. 키 열 이름이 다를 때 — left_on, right_on")
print("─" * 70)

table_a = JoinDF({
    '학생ID': ['S001', 'S002', 'S003'],
    '이름': ['민수', '영희', '철수'],
})

table_b = JoinDF({
    '학번': ['S001', 'S002', 'S003'],
    '점수': [90, 88, 75],
})

table_a.display("테이블 A (학생ID)")
table_b.display("테이블 B (학번)")

# 키 이름이 다를 때
result = merge(table_a, table_b, left_on='학생ID', right_on='학번')
result.display("left_on='학생ID', right_on='학번'으로 결합")
# ── Pandas: pd.merge(table_a, table_b, left_on='학생ID', right_on='학번') ──


# ─────────────────────────────────────────────────────────────────────────
# 5. suffixes — 키 충돌 처리
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 5. suffixes — 열 이름 충돌 처리")
print("─" * 70)

midterm = JoinDF({
    '학번': ['S001', 'S002', 'S003'],
    '수학': [90, 88, 75],
    '영어': [78, 95, 82],
})

final = JoinDF({
    '학번': ['S001', 'S002', 'S003'],
    '수학': [85, 92, 80],
    '영어': [80, 90, 88],
})

midterm.display("중간고사")
final.display("기말고사")

print("\n  두 테이블에 '수학', '영어' 열이 중복!")
print("  → suffixes로 구분해요")

result = merge(midterm, final, on='학번', suffixes=('_중간', '_기말'))
result.display("suffixes=('_중간', '_기말')")
# ── Pandas: pd.merge(midterm, final, on='학번', suffixes=('_중간', '_기말')) ──


# ─────────────────────────────────────────────────────────────────────────
# 6. 1:1, 1:N, N:N 관계
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 6. 1:1, 1:N, N:N 관계")
print("─" * 70)

print("""
  ┌─ 1:1 (일대일) ────────────────────────────┐
  │ 각 키가 양쪽 테이블에 한 번씩만            │
  │ 예: 학생-주민번호                          │
  │                                            │
  │ 학번: S001 ─── 주민번호: 123456            │
  │ 학번: S002 ─── 주민번호: 789012            │
  └────────────────────────────────────────────┘

  ┌─ 1:N (일대다) ────────────────────────────┐
  │ 한 키가 한쪽에서 여러 번 등장              │
  │ 예: 학생-시험성적 (학생 1명의 여러 시험)   │
  │                                            │
  │ 학번: S001 ──┬── 중간고사                  │
  │              └── 기말고사                  │
  └────────────────────────────────────────────┘

  ┌─ N:N (다대다) ────────────────────────────┐
  │ 양쪽 모두 키가 여러 번 등장                │
  │ 예: 학생-수강과목 (한 학생이 여러 과목,    │
  │     한 과목에 여러 학생)                   │
  │ ⚠️ 행이 크게 늘어날 수 있어요!            │
  └────────────────────────────────────────────┘
""")

# 1:N 예시
student_one = JoinDF({
    '학번': ['S001', 'S002'],
    '이름': ['민수', '영희'],
})

exams_many = JoinDF({
    '학번': ['S001', 'S001', 'S002', 'S002'],
    '시험': ['중간', '기말', '중간', '기말'],
    '점수': [90, 85, 88, 92],
})

student_one.display("학생 (1)")
exams_many.display("시험 (N)")

result = merge(student_one, exams_many, on='학번')
result.display("1:N 결합 결과 (행이 늘어남!)")
# ── Pandas: pd.merge(student_one, exams_many, on='학번') ──


# ─────────────────────────────────────────────────────────────────────────
# 7. join() — 인덱스 기반 합치기
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 7. join() — 인덱스 기반 합치기")
print("─" * 70)

print("""
  join()은 merge()와 비슷하지만, 인덱스를 키로 사용해요.

  Pandas에서:
    df1.join(df2)                    → 인덱스로 합치기
    df1.join(df2, how='outer')       → 외부 결합
    df1.set_index('학번').join(df2.set_index('학번'))  → 열을 인덱스로

  merge vs join:
    merge → 열(column) 기반 합치기
    join  → 인덱스(index) 기반 합치기
""")

# 인덱스 기반 합치기 시뮬레이션
df_a = JoinDF({'수학': [90, 88, 75]}, index=['민수', '영희', '철수'])
df_b = JoinDF({'영어': [78, 95, 82]}, index=['민수', '영희', '철수'])

df_a.display("A (수학)")
df_b.display("B (영어)")

result = concat_horizontal([df_a, df_b])
result.display("인덱스 기반 합치기 결과")
# ── Pandas: df_a.join(df_b) ──


# ─────────────────────────────────────────────────────────────────────────
# ★ 실습: 학생 정보 + 성적 + 동아리 테이블 결합
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "═" * 70)
print(" ★ 실습: 3개 테이블 결합")
print("═" * 70)

# 테이블 정의
info = JoinDF({
    '학번': ['S001', 'S002', 'S003', 'S004', 'S005'],
    '이름': ['김민수', '이영희', '박철수', '최지영', '정하늘'],
    '학년': [3, 3, 2, 3, 2],
    '반':   [1, 2, 1, 2, 1],
})

score = JoinDF({
    '학번': ['S001', 'S002', 'S003', 'S004', 'S005'],
    '수학': [90, 88, 65, 98, 72],
    '영어': [78, 95, 82, 90, 85],
    '국어': [85, 85, 90, 82, 88],
})

club = JoinDF({
    '학번':   ['S001', 'S002', 'S003', 'S005'],
    '동아리': ['축구부', '밴드부', '과학부', '미술부'],
    '역할':   ['부장', '회원', '회원', '부장'],
})

info.display("1) 학생 기본정보")
score.display("2) 성적 데이터")
club.display("3) 동아리 데이터")

# 1단계: 학생정보 + 성적 (INNER — 모든 학생에게 성적 있음)
print("\n── 1단계: 학생정보 + 성적 결합 ──")
step1 = merge(info, score, on='학번', how='inner')
step1.display("학생정보 + 성적")
# ── Pandas: step1 = pd.merge(info, score, on='학번') ──

# 2단계: 위 결과 + 동아리 (LEFT — 동아리 없는 학생도 포함)
print("\n── 2단계: + 동아리 결합 (LEFT JOIN) ──")
step2 = merge(step1, club, on='학번', how='left')
step2.display("최종 결합 결과")
# ── Pandas: step2 = pd.merge(step1, club, on='학번', how='left') ──

# 3단계: 분석
print("\n── 3단계: 결합 데이터 분석 ──")

# 동아리 가입 현황
print("\n  [동아리 가입 현황]")
for i in range(step2.shape[0]):
    name = step2._data['이름'][i]
    club_name = step2._data['동아리'][i]
    role = step2._data['역할'][i]
    if club_name is None:
        print(f"    {name}: 동아리 미가입")
    else:
        print(f"    {name}: {club_name} ({role})")

# 동아리별 평균 성적
print("\n  [동아리별 수학 평균]")
club_scores = {}
for i in range(step2.shape[0]):
    c = step2._data['동아리'][i]
    if c is None:
        c = '미가입'
    if c not in club_scores:
        club_scores[c] = []
    club_scores[c].append(step2._data['수학'][i])

for c, scores_list in sorted(club_scores.items()):
    avg = sum(scores_list) / len(scores_list)
    print(f"    {c}: {avg:.1f}점 ({len(scores_list)}명)")

# ── Pandas로 전체를 하면? ──
# combined = (
#     pd.merge(info, score, on='학번')
#       .merge(club, on='학번', how='left')
# )
# combined['동아리'] = combined['동아리'].fillna('미가입')
# combined.groupby('동아리')['수학'].mean()


# ─────────────────────────────────────────────────────────────────────────
# 참고: merge 시 주의사항
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 참고: merge 시 주의사항")
print("─" * 70)

print("""
  ⚠️ merge 할 때 주의할 점:

  1) 키 열의 데이터 타입이 같아야 해요!
     - 한쪽은 int(1), 다른쪽은 str('1')이면 매칭 안 됨
     - Pandas: df['학번'] = df['학번'].astype(str)

  2) N:N 결합은 행이 폭발적으로 늘어날 수 있어요!
     - 왼쪽 3행 × 오른쪽 3행 = 최대 9행!
     - Pandas 2.0+: validate='one_to_one' 등으로 검증

  3) 결합 후 NaN 처리를 잊지 마세요!
     - LEFT/RIGHT/OUTER JOIN은 NaN이 생길 수 있음
     - df.fillna() 또는 df.dropna()

  4) indicator=True로 결합 출처 확인 가능
     - Pandas: pd.merge(df1, df2, indicator=True)
     - → '_merge' 열: 'left_only', 'right_only', 'both'
""")


# ─────────────────────────────────────────────────────────────────────────
# 정리
# ─────────────────────────────────────────────────────────────────────────

print("═" * 70)
print(" 정리: 테이블 결합 도구 모음")
print("═" * 70)

print("""
  ┌───────────────┬──────────────────────────────────────┐
  │ 작업          │ Pandas 코드                          │
  ├───────────────┼──────────────────────────────────────┤
  │ 위아래 합치기 │ pd.concat([df1, df2])                │
  │ 좌우 합치기   │ pd.concat([df1, df2], axis=1)        │
  │ 인덱스 초기화 │ pd.concat(..., ignore_index=True)    │
  │               │                                      │
  │ INNER JOIN    │ pd.merge(df1, df2, on='키')          │
  │ LEFT JOIN     │ pd.merge(df1, df2, on='키', how='left')│
  │ RIGHT JOIN    │ pd.merge(..., how='right')           │
  │ OUTER JOIN    │ pd.merge(..., how='outer')           │
  │               │                                      │
  │ 다른 키 이름  │ pd.merge(df1, df2,                   │
  │               │   left_on='A', right_on='B')         │
  │ 이름 충돌     │ pd.merge(..., suffixes=('_a','_b'))  │
  │ 인덱스 결합   │ df1.join(df2)                        │
  │ 결합 검증     │ pd.merge(..., validate='one_to_one') │
  └───────────────┴──────────────────────────────────────┘

  기억하기:
  • concat = 단순 붙이기 (위아래/좌우)
  • merge  = 키 기반 결합 (SQL JOIN)
  • join   = 인덱스 기반 결합
""")

print("✅ 06단계 완료! 다음은 07_string_datetime.py에서 문자열과 날짜를 배워요!")
