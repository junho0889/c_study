# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   Pandas 학습 10단계: 실전 패턴과 고급 기능
#   ─ 메서드 체이닝, 윈도우 함수, 멀티인덱스, 카테고리, 대용량 처리 ─
#   ■ 실행 방법: python 10_practical_patterns.py
#   ■ Pandas 설치: pip install pandas
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# =========================================================================
#  드디어 마지막 단계! 실전에서 쓰는 고급 패턴을 배워요!
# =========================================================================
#
#  지금까지 배운 것들을 조합해서 실전 프로젝트를 해봅니다.
#  - 메서드 체이닝: 여러 작업을 한 줄로!
#  - 윈도우 함수: 이동 평균, 누적 합계
#  - 멀티 인덱스: 계층적 인덱스
#  - 카테고리 타입: 메모리 절약
#  - 실전 프로젝트: 쇼핑몰 매출 분석
# =========================================================================

print("=" * 70)
print(" 10단계: 실전 패턴과 고급 기능")
print("=" * 70)

import random
import math
from datetime import datetime, timedelta
random.seed(42)


class PracticalDF:
    """실전 패턴 학습용 DataFrame"""

    def __init__(self, data, index=None):
        self._columns = list(data.keys())
        n = len(data[self._columns[0]])
        self._data = {col: list(data[col]) for col in self._columns}
        self._index = list(index) if index else list(range(n))

    @property
    def shape(self):
        return (len(self._index), len(self._columns))

    def display(self, title=None, max_rows=15):
        if title:
            print(f"\n  [{title}]")
        n = len(self._index)
        show_all = n <= max_rows

        idx_w = max(len(str(i)) for i in self._index) + 2
        col_w = {}
        for c in self._columns:
            w = len(str(c))
            for v in self._data[c]:
                display_v = 'NaN' if v is None else str(v)
                w = max(w, len(display_v))
            col_w[c] = min(w + 2, 15)

        header = " " * idx_w + "".join(f"{c:>{col_w[c]}}" for c in self._columns)
        print(header)
        print("  " + "─" * (len(header) - 2))

        if show_all:
            rows_to_show = range(n)
        else:
            rows_to_show = list(range(5)) + [-1] + list(range(n - 3, n))

        for ri in rows_to_show:
            if ri == -1:
                print(f"  {'...':<{idx_w}}" + "".join(f"{'...':>{col_w[c]}}" for c in self._columns))
                continue
            line = f"{str(self._index[ri]):<{idx_w}}"
            for c in self._columns:
                val = self._data[c][ri]
                display_val = 'NaN' if val is None else str(val)
                if len(display_val) > col_w[c] - 1:
                    display_val = display_val[:col_w[c] - 2] + '..'
                line += f"{display_val:>{col_w[c]}}"
            print(line)

        print(f"  [{n} rows x {len(self._columns)} cols]")

    def copy(self):
        new_data = {col: list(vals) for col, vals in self._data.items()}
        return PracticalDF(new_data, index=list(self._index))

    def add_column(self, name, values):
        if isinstance(values, (int, float, str)):
            self._data[name] = [values] * len(self._index)
        else:
            self._data[name] = list(values)
        if name not in self._columns:
            self._columns.append(name)
        return self

    def sort_values(self, by, ascending=True):
        n = len(self._index)
        indices = list(range(n))
        indices.sort(key=lambda i: (self._data[by][i] is None, self._data[by][i]),
                     reverse=not ascending)
        new_data = {c: [self._data[c][i] for i in indices] for c in self._columns}
        new_idx = [self._index[i] for i in indices]
        return PracticalDF(new_data, index=new_idx)

    def groupby_agg(self, by, agg_dict):
        groups = {}
        for i in range(len(self._index)):
            key = self._data[by][i]
            if key not in groups:
                groups[key] = []
            groups[key].append(i)

        result = {by: []}
        for col, func in agg_dict.items():
            result[f"{col}_{func}"] = []

        for key in sorted(groups.keys()):
            result[by].append(key)
            indices = groups[key]
            for col, func in agg_dict.items():
                vals = [self._data[col][i] for i in indices
                        if self._data[col][i] is not None
                        and isinstance(self._data[col][i], (int, float))]
                if func == 'sum':
                    result[f"{col}_{func}"].append(sum(vals) if vals else 0)
                elif func == 'mean':
                    result[f"{col}_{func}"].append(round(sum(vals) / len(vals), 1) if vals else 0)
                elif func == 'count':
                    result[f"{col}_{func}"].append(len(vals))
                elif func == 'max':
                    result[f"{col}_{func}"].append(max(vals) if vals else None)
                elif func == 'min':
                    result[f"{col}_{func}"].append(min(vals) if vals else None)

        return PracticalDF(result)

    def where(self, col, op, value):
        import operator
        ops = {'>': operator.gt, '<': operator.lt, '>=': operator.ge,
               '<=': operator.le, '==': operator.eq, '!=': operator.ne}
        op_func = ops[op]
        keep = [i for i in range(len(self._index))
                if self._data[col][i] is not None and op_func(self._data[col][i], value)]
        new_data = {c: [self._data[c][i] for i in keep] for c in self._columns}
        return PracticalDF(new_data, index=[self._index[i] for i in keep])


# ─────────────────────────────────────────────────────────────────────────
# 1. 메서드 체이닝 (Method Chaining)
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 1. 메서드 체이닝 (Method Chaining)")
print("─" * 70)

print("""
  메서드 체이닝 = 여러 작업을 점(.)으로 연결해서 한번에!

  ❌ 체이닝 없이 (단계별):
    df1 = df[df['학년'] == 3]
    df2 = df1.groupby('반').mean()
    df3 = df2.sort_values('수학', ascending=False)
    df4 = df3.head(3)

  ✅ 체이닝으로 (한 줄로):
    result = (
        df.query('학년 == 3')
          .groupby('반')
          .mean()
          .sort_values('수학', ascending=False)
          .head(3)
    )

  → 데이터가 파이프라인을 따라 흘러가는 것처럼 읽혀요!
  → 중간 변수가 필요 없어서 코드가 깔끔!
""")

# 순수 파이썬으로 체이닝 시뮬레이션
print("\n[체이닝 시뮬레이션]")

students = PracticalDF({
    '이름': ['김민수', '이영희', '박철수', '최지영', '정하늘',
             '한서준', '윤다은', '장예린', '송민호', '오수빈'],
    '학년': [3, 3, 2, 3, 2, 1, 1, 2, 3, 1],
    '반':   [1, 2, 1, 2, 1, 1, 2, 1, 2, 1],
    '수학': [90, 88, 65, 98, 72, 85, 45, 78, 92, 68],
    '영어': [78, 95, 82, 90, 85, 60, 92, 88, 80, 75],
})

# 체이닝: 3학년 → 수학 내림차순 정렬
result = students.where('학년', '==', 3).sort_values('수학', ascending=False)
result.display("3학년 수학 내림차순")

# ── Pandas 메서드 체이닝 예시: ──
# result = (
#     df.query('학년 == 3')
#       .assign(총점=lambda x: x['수학'] + x['영어'])
#       .sort_values('총점', ascending=False)
#       .head(3)
#       .reset_index(drop=True)
# )


# ─────────────────────────────────────────────────────────────────────────
# 2. pipe() — 커스텀 함수 체이닝
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 2. pipe() — 커스텀 함수 체이닝")
print("─" * 70)

print("""
  pipe()는 "내가 만든 함수"도 체이닝에 끼워넣을 수 있게 해줘요!

  def add_grade_column(df):
      df['등급'] = df['평균'].apply(grade_func)
      return df

  def filter_top_students(df, n=5):
      return df.nlargest(n, '평균')

  # pipe()로 체이닝!
  result = (
      df.pipe(add_grade_column)
        .pipe(filter_top_students, n=3)
  )

  → 복잡한 변환 로직도 깔끔하게!
""")

# pipe 시뮬레이션
def add_total(df):
    """총점 열 추가"""
    totals = [df._data['수학'][i] + df._data['영어'][i]
              for i in range(df.shape[0])]
    df.add_column('총점', totals)
    return df

def add_grade(df):
    """등급 열 추가"""
    grades = []
    for i in range(df.shape[0]):
        avg = df._data['총점'][i] / 2
        if avg >= 90: grades.append('A')
        elif avg >= 80: grades.append('B')
        elif avg >= 70: grades.append('C')
        else: grades.append('D')
    df.add_column('등급', grades)
    return df

# pipe 체이닝
result = add_grade(add_total(students.copy()))
result.display("pipe() 시뮬레이션 — 총점 + 등급 추가")

# ── Pandas: ──
# result = (
#     df.pipe(add_total)
#       .pipe(add_grade)
#       .sort_values('총점', ascending=False)
# )


# ─────────────────────────────────────────────────────────────────────────
# 3. 윈도우 함수: rolling(), expanding(), ewm()
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 3. 윈도우 함수 (Window Functions)")
print("─" * 70)

print("""
  윈도우 함수 = "창문을 움직이며" 계산하는 함수

  ┌─ rolling(3) — 이동 윈도우 ──────────────┐
  │ 데이터: [10, 20, 30, 40, 50, 60, 70]    │
  │                                           │
  │ 3일 이동 평균:                            │
  │ [NaN, NaN, 20, 30, 40, 50, 60]           │
  │                                           │
  │ [10, 20, 30]          → 평균 = 20         │
  │     [20, 30, 40]      → 평균 = 30         │
  │         [30, 40, 50]  → 평균 = 40         │
  │             ...                           │
  │ 창문이 오른쪽으로 한 칸씩 이동!           │
  └───────────────────────────────────────────┘

  ┌─ expanding() — 확장 윈도우 ─────────────┐
  │ 데이터: [10, 20, 30, 40, 50]            │
  │                                          │
  │ 누적 평균:                               │
  │ [10, 15, 20, 25, 30]                    │
  │                                          │
  │ [10]                → 평균 = 10          │
  │ [10, 20]            → 평균 = 15          │
  │ [10, 20, 30]        → 평균 = 20          │
  │ [10, 20, 30, 40]    → 평균 = 25          │
  │ 창문이 점점 커져요!                      │
  └──────────────────────────────────────────┘

  ┌─ ewm() — 지수 가중 이동 평균 ───────────┐
  │ 최근 데이터에 더 큰 가중치를 줘요!       │
  │ → 주가 분석, 추세 파악에 많이 사용       │
  │ ewm(span=3).mean()                      │
  └──────────────────────────────────────────┘
""")

# rolling() 구현
def rolling_mean(values, window):
    """
    이동 평균 계산.

    Pandas에서:
      df['열'].rolling(window=7).mean()
      df['열'].rolling(window=7, min_periods=1).mean()
    """
    result = []
    for i in range(len(values)):
        if i < window - 1:
            result.append(None)  # 데이터 부족
        else:
            window_data = values[i - window + 1:i + 1]
            result.append(round(sum(window_data) / len(window_data), 1))
    return result


def rolling_sum(values, window):
    """이동 합계. Pandas: df['열'].rolling(window).sum()"""
    result = []
    for i in range(len(values)):
        if i < window - 1:
            result.append(None)
        else:
            result.append(sum(values[i - window + 1:i + 1]))
    return result


# expanding() 구현
def expanding_mean(values):
    """
    누적 평균.

    Pandas에서:
      df['열'].expanding().mean()
      df['열'].cumsum()  # 누적 합
    """
    result = []
    for i in range(len(values)):
        result.append(round(sum(values[:i + 1]) / (i + 1), 1))
    return result


def expanding_sum(values):
    """누적 합. Pandas: df['열'].cumsum()"""
    result = []
    total = 0
    for v in values:
        total += v
        result.append(total)
    return result


# ewm() 구현
def ewm_mean(values, span):
    """
    지수 가중 이동 평균.

    Pandas에서:
      df['열'].ewm(span=7).mean()
    """
    alpha = 2 / (span + 1)
    result = [values[0]]
    for i in range(1, len(values)):
        ewm = alpha * values[i] + (1 - alpha) * result[-1]
        result.append(round(ewm, 1))
    return result


# 시연: 일별 매출 데이터
daily_sales = [random.randint(80, 200) for _ in range(30)]
dates = [f"D{i + 1:02d}" for i in range(30)]

print("\n[rolling(7)] 7일 이동 평균:")
rolling_avg = rolling_mean(daily_sales, 7)
print(f"  원본:    {daily_sales[:15]}...")
print(f"  이동평균: {rolling_avg[:15]}...")
# ── Pandas: df['매출'].rolling(7).mean() ──

print("\n[expanding()] 누적 평균:")
exp_avg = expanding_mean(daily_sales[:10])
print(f"  원본:    {daily_sales[:10]}")
print(f"  누적평균: {exp_avg}")
# ── Pandas: df['매출'].expanding().mean() ──

print("\n[cumsum()] 누적 합계:")
cum_sum = expanding_sum(daily_sales[:10])
print(f"  원본:    {daily_sales[:10]}")
print(f"  누적합계: {cum_sum}")
# ── Pandas: df['매출'].cumsum() ──

print("\n[ewm(span=7)] 지수 가중 이동 평균:")
ewm_avg = ewm_mean(daily_sales[:10], span=7)
print(f"  원본: {daily_sales[:10]}")
print(f"  EWM:  {ewm_avg}")
# ── Pandas: df['매출'].ewm(span=7).mean() ──

# 시각화
print("\n  [매출 + 7일 이동평균 비교]")
for i in range(30):
    sale = daily_sales[i]
    avg = rolling_avg[i]
    bar_sale = "█" * (sale // 10)
    if avg is not None:
        bar_avg = "▓" * (int(avg) // 10)
        print(f"  {dates[i]} 매출│{bar_sale} {sale:>3}  이동평균│{bar_avg} {avg}")
    else:
        print(f"  {dates[i]} 매출│{bar_sale} {sale:>3}")


# ─────────────────────────────────────────────────────────────────────────
# 4. 멀티 인덱스 (MultiIndex)
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 4. 멀티 인덱스 (MultiIndex)")
print("─" * 70)

print("""
  멀티 인덱스 = 여러 레벨의 계층적 인덱스

  예: 학교와 학년으로 2단계 인덱스

           수학  영어
  서울초 3학년  90   78
         2학년  82   85
  부산초 3학년  88   90
         2학년  75   80

  → "서울초 3학년"처럼 2개 키로 접근!

  Pandas에서:
    df.set_index(['학교', '학년'])      → 멀티 인덱스 설정
    df.reset_index()                     → 멀티 인덱스 해제
    df.loc[('서울초', 3)]                → 특정 그룹 접근
    df.xs(3, level='학년')              → 특정 레벨 접근
""")

# 멀티 인덱스 시뮬레이션
multi_data = {
    'school': ['서울초', '서울초', '서울초', '부산초', '부산초', '대전초'],
    'grade':  [3, 2, 1, 3, 2, 3],
    'math_avg': [88.5, 76.3, 82.0, 85.0, 71.5, 90.2],
    'eng_avg':  [82.0, 79.5, 75.0, 88.0, 80.0, 78.5],
    'count':    [45, 42, 38, 40, 35, 30],
}

print("\n[멀티 인덱스 구조]")
print(f"\n  {'학교':>6} {'학년':>4}  {'수학평균':>8} {'영어평균':>8} {'학생수':>6}")
print("  " + "─" * 40)
prev_school = None
for i in range(len(multi_data['school'])):
    school = multi_data['school'][i]
    grade = multi_data['grade'][i]
    math_a = multi_data['math_avg'][i]
    eng_a = multi_data['eng_avg'][i]
    cnt = multi_data['count'][i]
    display_school = school if school != prev_school else "      "
    print(f"  {display_school:>6} {grade:>4}학년  {math_a:>8.1f} {eng_a:>8.1f} {cnt:>6}")
    prev_school = school

# ── Pandas: ──
# df = df.set_index(['학교', '학년'])
# print(df)
#
# # 특정 학교 접근
# df.loc['서울초']
#
# # 특정 학교+학년 접근
# df.loc[('서울초', 3)]
#
# # 학년 레벨로 접근
# df.xs(3, level='학년')

# stack / unstack
print("""
  ┌─ stack() / unstack() ─────────────────────────────┐
  │                                                    │
  │ unstack(): 인덱스 레벨 → 열로 변환                │
  │                                                    │
  │ 변환 전 (멀티인덱스):      변환 후 (unstack):      │
  │         수학                  수학               │
  │ 서울 3   90                서울  부산  대전       │
  │ 서울 2   82          3학년  90    85    90        │
  │ 부산 3   85          2학년  82    72     -        │
  │ 부산 2   72          1학년  80     -     -        │
  │                                                    │
  │ stack(): 열 → 인덱스 레벨로 변환 (unstack 반대)    │
  └────────────────────────────────────────────────────┘
""")

# ── Pandas: ──
# df.unstack(level='학년')   → 학년이 열로
# df.stack()                  → 열이 인덱스로


# ─────────────────────────────────────────────────────────────────────────
# 5. 카테고리 타입 (Categorical)
# ─────────────────────────────────────────────────────────────────────────

print("─" * 70)
print(" 5. 카테고리 타입 (Categorical)")
print("─" * 70)

print("""
  카테고리 타입 = 반복되는 문자열을 효율적으로 저장!

  일반 object 타입:
    ['서울', '부산', '서울', '대전', '서울', '부산', ...]
    → 각각 별도의 문자열 객체 (메모리 낭비!)

  category 타입:
    카테고리: {서울: 0, 부산: 1, 대전: 2}
    데이터:   [0, 1, 0, 2, 0, 1, ...]
    → 숫자로 저장하고 필요할 때 변환! (메모리 절약!)

  메모리 비교 (100만 행, 도시 이름):
    object:   ~60 MB
    category: ~1 MB  (60배 절약!)
""")

# 카테고리 타입 시뮬레이션
class CategoryColumn:
    """카테고리 타입의 내부 작동 원리"""

    def __init__(self, values):
        # 카테고리 테이블 만들기
        self.categories = sorted(set(values))
        self.cat_to_code = {cat: i for i, cat in enumerate(self.categories)}

        # 데이터를 숫자(코드)로 변환
        self.codes = [self.cat_to_code[v] for v in values]

    def __getitem__(self, idx):
        return self.categories[self.codes[idx]]

    def memory_savings(self, n_values):
        """메모리 절약 계산"""
        # object: 각 문자열 ~50바이트
        object_memory = n_values * 50
        # category: 코드(int8) + 카테고리 테이블
        category_memory = n_values * 1 + len(self.categories) * 50
        return object_memory, category_memory

    def show_internal(self):
        """내부 구조 보기"""
        print("  [카테고리 타입 내부 구조]")
        print(f"  카테고리 테이블: {self.categories}")
        print(f"  코드 → 카테고리: {self.cat_to_code}")
        print(f"  실제 저장된 데이터 (코드): {self.codes}")
        print(f"  복원된 데이터: {[self[i] for i in range(len(self.codes))]}")


# 시연
cities = ['서울', '부산', '대전', '서울', '서울', '부산', '대전', '서울']
cat_col = CategoryColumn(cities)
cat_col.show_internal()

obj_mem, cat_mem = cat_col.memory_savings(1_000_000)
print(f"\n  100만 행 메모리 비교:")
print(f"    object:   {obj_mem / 1024 / 1024:.1f} MB")
print(f"    category: {cat_mem / 1024 / 1024:.1f} MB")
print(f"    절약:     {(1 - cat_mem / obj_mem) * 100:.0f}%")

# ── Pandas: ──
# df['도시'] = df['도시'].astype('category')
# print(df['도시'].cat.categories)     # 카테고리 목록
# print(df['도시'].cat.codes)          # 코드 배열
# print(df.memory_usage(deep=True))    # 메모리 사용량


# ─────────────────────────────────────────────────────────────────────────
# 6. 대용량 데이터 팁
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 6. 대용량 데이터 처리 팁")
print("─" * 70)

print("""
  ┌─ 팁 1: 메모리 최적화 ─────────────────────────────┐
  │                                                     │
  │ # 읽을 때 타입 지정                                 │
  │ df = pd.read_csv('big.csv', dtype={                 │
  │     '학년': 'int8',       # int64 → int8 (8배 절약) │
  │     '점수': 'int16',      # int64 → int16 (4배)     │
  │     '학교': 'category',   # object → category       │
  │ })                                                   │
  │                                                     │
  │ # 읽은 후 타입 변환                                 │
  │ df['학년'] = df['학년'].astype('int8')               │
  │ df['학교'] = df['학교'].astype('category')           │
  └─────────────────────────────────────────────────────┘

  ┌─ 팁 2: 청크 처리 ─────────────────────────────────┐
  │                                                     │
  │ # 10만 행씩 나눠서 처리                             │
  │ results = []                                        │
  │ for chunk in pd.read_csv('big.csv', chunksize=100000):│
  │     processed = chunk.groupby('학교')['점수'].mean()│
  │     results.append(processed)                       │
  │ final = pd.concat(results).groupby(level=0).mean() │
  └─────────────────────────────────────────────────────┘

  ┌─ 팁 3: 필요한 것만 읽기 ──────────────────────────┐
  │                                                     │
  │ # 필요한 열만                                       │
  │ df = pd.read_csv('big.csv', usecols=['이름', '점수'])│
  │                                                     │
  │ # 필요한 행만                                       │
  │ df = pd.read_csv('big.csv', nrows=1000)            │
  │                                                     │
  │ # Parquet은 열 선택이 진짜 빠름!                    │
  │ df = pd.read_parquet('big.parquet', columns=['점수'])│
  └─────────────────────────────────────────────────────┘

  ┌─ 팁 4: 벡터 연산 사용 ────────────────────────────┐
  │                                                     │
  │ # ❌ 느린 방법 (for문 + iterrows)                    │
  │ for idx, row in df.iterrows():                      │
  │     df.at[idx, '총점'] = row['수학'] + row['영어']  │
  │                                                     │
  │ # ✅ 빠른 방법 (벡터 연산)                           │
  │ df['총점'] = df['수학'] + df['영어']                 │
  │                                                     │
  │ → 벡터 연산은 for문보다 100배 이상 빠릅니다!        │
  └─────────────────────────────────────────────────────┘
""")


# ─────────────────────────────────────────────────────────────────────────
# ★ 실전 프로젝트: 쇼핑몰 매출 분석 (전체 파이프라인)
# ─────────────────────────────────────────────────────────────────────────

print("═" * 70)
print(" ★ 실전 프로젝트: 쇼핑몰 매출 분석")
print("═" * 70)

# ── 데이터 생성 ──
print("\n── 0. 데이터 생성 ──")

categories = ['전자제품', '의류', '식품', '도서', '가구']
payment_methods = ['카드', '현금', '간편결제']
cities = ['서울', '부산', '대전', '대구', '인천']

n_orders = 200
orders = {
    '주문ID': [f'ORD{i+1:04d}' for i in range(n_orders)],
    '날짜': [],
    '카테고리': [],
    '도시': [],
    '결제방식': [],
    '수량': [],
    '단가': [],
    '할인율': [],
}

base_date = datetime(2024, 1, 1)
for i in range(n_orders):
    orders['날짜'].append((base_date + timedelta(days=random.randint(0, 364))).strftime('%Y-%m-%d'))
    cat = random.choice(categories)
    orders['카테고리'].append(cat)
    orders['도시'].append(random.choice(cities))
    orders['결제방식'].append(random.choice(payment_methods))
    orders['수량'].append(random.randint(1, 5))

    # 카테고리별 단가 범위
    price_ranges = {
        '전자제품': (50000, 500000), '의류': (20000, 150000),
        '식품': (5000, 50000), '도서': (10000, 40000),
        '가구': (100000, 1000000)
    }
    low, high = price_ranges[cat]
    orders['단가'].append(random.randint(low // 1000, high // 1000) * 1000)
    orders['할인율'].append(random.choice([0, 0, 0, 5, 10, 15, 20]))

# 매출액 계산
orders['매출액'] = [
    int(orders['수량'][i] * orders['단가'][i] * (1 - orders['할인율'][i] / 100))
    for i in range(n_orders)
]

df = PracticalDF(orders)
df.display("쇼핑몰 주문 데이터", max_rows=10)
print(f"  총 주문 수: {n_orders}건")


# ── 1단계: 기본 통계 ──
print("\n── 1단계: 기본 통계 ──")

total_revenue = sum(orders['매출액'])
avg_revenue = total_revenue / n_orders
max_revenue = max(orders['매출액'])
min_revenue = min(orders['매출액'])
max_idx = orders['매출액'].index(max_revenue)

print(f"  총 매출: {total_revenue:>15,}원")
print(f"  평균 매출: {avg_revenue:>13,.0f}원")
print(f"  최대 매출: {max_revenue:>13,}원 ({orders['주문ID'][max_idx]})")
print(f"  최소 매출: {min_revenue:>13,}원")
print(f"  총 수량: {sum(orders['수량']):>15,}개")

# ── Pandas: ──
# print(df['매출액'].describe())
# print(f"총 매출: {df['매출액'].sum():,}")


# ── 2단계: 카테고리별 분석 ──
print("\n── 2단계: 카테고리별 분석 ──")

cat_stats = {}
for i in range(n_orders):
    cat = orders['카테고리'][i]
    if cat not in cat_stats:
        cat_stats[cat] = {'매출': 0, '건수': 0, '수량': 0}
    cat_stats[cat]['매출'] += orders['매출액'][i]
    cat_stats[cat]['건수'] += 1
    cat_stats[cat]['수량'] += orders['수량'][i]

print(f"\n  {'카테고리':>8} {'매출합계':>12} {'주문수':>6} {'평균매출':>10} {'비율':>6}")
print("  " + "─" * 50)
for cat in sorted(cat_stats.keys(), key=lambda x: cat_stats[x]['매출'], reverse=True):
    s = cat_stats[cat]
    avg = s['매출'] // s['건수']
    pct = s['매출'] / total_revenue * 100
    bar = "█" * int(pct / 2)
    print(f"  {cat:>8} {s['매출']:>12,} {s['건수']:>6} {avg:>10,} {pct:>5.1f}% {bar}")

# ── Pandas: df.groupby('카테고리')['매출액'].agg(['sum', 'count', 'mean']).sort_values('sum', ascending=False) ──


# ── 3단계: 월별 매출 추이 ──
print("\n── 3단계: 월별 매출 추이 ──")

monthly = {}
for i in range(n_orders):
    month = orders['날짜'][i][:7]
    if month not in monthly:
        monthly[month] = 0
    monthly[month] += orders['매출액'][i]

print(f"\n  {'월':>8} {'매출':>12}")
print("  " + "─" * 30)
max_monthly = max(monthly.values())
for month in sorted(monthly.keys()):
    rev = monthly[month]
    bar_len = int(rev / max_monthly * 25)
    print(f"  {month:>8} {rev:>12,} {'█' * bar_len}")

# ── Pandas: ──
# df['날짜'] = pd.to_datetime(df['날짜'])
# df.set_index('날짜').resample('M')['매출액'].sum().plot(kind='bar')


# ── 4단계: 도시별 분석 ──
print("\n── 4단계: 도시별 분석 ──")

city_stats = {}
for i in range(n_orders):
    city = orders['도시'][i]
    if city not in city_stats:
        city_stats[city] = 0
    city_stats[city] += orders['매출액'][i]

print(f"\n  {'도시':>6} {'매출':>12} {'비율':>6}")
print("  " + "─" * 30)
for city in sorted(city_stats.keys(), key=lambda x: city_stats[x], reverse=True):
    rev = city_stats[city]
    pct = rev / total_revenue * 100
    bar = "█" * int(pct / 2)
    print(f"  {city:>6} {rev:>12,} {pct:>5.1f}% {bar}")

# ── Pandas: df.groupby('도시')['매출액'].sum().sort_values(ascending=False) ──


# ── 5단계: 결제 방식 분석 ──
print("\n── 5단계: 결제 방식 분석 ──")

pay_stats = {}
for i in range(n_orders):
    pay = orders['결제방식'][i]
    if pay not in pay_stats:
        pay_stats[pay] = {'건수': 0, '매출': 0}
    pay_stats[pay]['건수'] += 1
    pay_stats[pay]['매출'] += orders['매출액'][i]

print(f"\n  {'결제방식':>10} {'건수':>6} {'비율':>6} {'평균매출':>12}")
print("  " + "─" * 40)
for pay, stats in sorted(pay_stats.items(), key=lambda x: x[1]['건수'], reverse=True):
    pct = stats['건수'] / n_orders * 100
    avg = stats['매출'] // stats['건수']
    print(f"  {pay:>10} {stats['건수']:>6} {pct:>5.1f}% {avg:>12,}")

# ── Pandas: pd.crosstab(df['결제방식'], df['카테고리'], values=df['매출액'], aggfunc='sum') ──


# ── 6단계: 할인 효과 분석 ──
print("\n── 6단계: 할인 효과 분석 ──")

discount_stats = {}
for i in range(n_orders):
    disc = orders['할인율'][i]
    if disc not in discount_stats:
        discount_stats[disc] = {'건수': 0, '매출': 0, '수량합': 0}
    discount_stats[disc]['건수'] += 1
    discount_stats[disc]['매출'] += orders['매출액'][i]
    discount_stats[disc]['수량합'] += orders['수량'][i]

print(f"\n  {'할인율':>6} {'건수':>6} {'평균수량':>8} {'평균매출':>12}")
print("  " + "─" * 38)
for disc in sorted(discount_stats.keys()):
    s = discount_stats[disc]
    avg_qty = s['수량합'] / s['건수']
    avg_rev = s['매출'] // s['건수']
    print(f"  {disc:>5}% {s['건수']:>6} {avg_qty:>8.1f} {avg_rev:>12,}")


# ── 7단계: 전체 파이프라인 (Pandas 코드) ──
print("\n── 7단계: Pandas 코드로 전체 파이프라인 ──")

print("""
  # ── Pandas로 이 모든 분석을 하면? ──

  import pandas as pd

  # 1. 데이터 읽기
  df = pd.read_csv('orders.csv', parse_dates=['날짜'])

  # 2. 매출액 계산
  df['매출액'] = df['수량'] * df['단가'] * (1 - df['할인율'] / 100)

  # 3. 기본 통계
  print(df['매출액'].describe())

  # 4. 카테고리별 분석 (메서드 체이닝!)
  category_report = (
      df.groupby('카테고리')['매출액']
        .agg(['sum', 'mean', 'count'])
        .sort_values('sum', ascending=False)
        .assign(비율=lambda x: x['sum'] / x['sum'].sum() * 100)
  )

  # 5. 월별 추이
  monthly = df.resample('M', on='날짜')['매출액'].sum()
  monthly.plot(kind='bar', title='월별 매출')

  # 6. 피벗 테이블
  pivot = pd.pivot_table(
      df, values='매출액',
      index='카테고리', columns='도시',
      aggfunc='sum', fill_value=0
  )

  # 7. 이동 평균
  df['7일이동평균'] = df.set_index('날짜')['매출액'].rolling(7).mean()

  # 8. 결과 저장
  category_report.to_csv('카테고리_리포트.csv')
  pivot.to_excel('매출_피벗.xlsx')

  # → 전체 분석이 20줄 이내!
""")


# ─────────────────────────────────────────────────────────────────────────
# 최종 정리
# ─────────────────────────────────────────────────────────────────────────

print("═" * 70)
print(" 최종 정리: Pandas 학습 로드맵")
print("═" * 70)

print("""
  ┌─ 01~03: 기초 ──────────────────────────────────────┐
  │ Series, DataFrame, 인덱싱, 데이터 조작              │
  │ → 데이터를 만들고, 선택하고, 변형하는 기본기!       │
  └─────────────────────────────────────────────────────┘
  ┌─ 04~06: 중급 ──────────────────────────────────────┐
  │ 결측값, GroupBy, Merge/Join                         │
  │ → 실무 데이터의 90%가 여기서 처리됩니다!            │
  └─────────────────────────────────────────────────────┘
  ┌─ 07~08: 실용 ──────────────────────────────────────┐
  │ 문자열/날짜, 파일 I/O                               │
  │ → 실제 데이터를 읽고, 다듬고, 저장!                 │
  └─────────────────────────────────────────────────────┘
  ┌─ 09~10: 고급 ──────────────────────────────────────┐
  │ 시각화, 실전 패턴                                   │
  │ → 분석 결과를 보여주고, 효율적으로 작업!            │
  └─────────────────────────────────────────────────────┘

  앞으로의 학습 방향:
    1. 이 튜토리얼의 순수 파이썬 코드를 Pandas로 바꿔보세요!
    2. 실제 CSV 데이터로 분석해보세요 (Kaggle 데이터셋 추천!)
    3. matplotlib/seaborn으로 예쁜 그래프를 그려보세요!
    4. 공식 문서: https://pandas.pydata.org/docs/

  Pandas 치트시트:
    생성:  pd.DataFrame(dict), pd.read_csv()
    선택:  df[col], df.loc[], df.iloc[], df.query()
    변형:  df.apply(), df.assign(), df.rename()
    집계:  df.groupby().agg(), df.pivot_table()
    결합:  pd.merge(), pd.concat()
    정리:  df.fillna(), df.dropna(), df.drop_duplicates()
    저장:  df.to_csv(), df.to_excel(), df.to_parquet()
""")

print("=" * 70)
print(" 축하합니다! Pandas 학습 10단계를 모두 완료했습니다!")
print("=" * 70)
