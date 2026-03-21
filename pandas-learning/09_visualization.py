# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   Pandas 학습 09단계: 시각화 (Visualization)
#   ─ plot() 기본, 다양한 차트, ASCII 시각화 ─
#   ■ 실행 방법: python 09_visualization.py
#   ■ Pandas 설치: pip install pandas matplotlib
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# =========================================================================
#  데이터를 그림으로 보면 이해가 훨씬 쉬워요!
# =========================================================================
#
#  Pandas는 matplotlib을 기반으로 한 .plot() 메서드를 제공해요.
#  → df.plot() 한 줄이면 그래프가 뿅!
#
#  이 파일에서는:
#  1) Pandas plot()의 API를 설명하고
#  2) ASCII로 차트를 직접 구현해서 원리를 이해해요!
#     (외부 라이브러리 없이 실행 가능)
# =========================================================================

print("=" * 70)
print(" 09단계: 시각화 (Visualization)")
print("=" * 70)

import random
import math
random.seed(42)


# ─── ASCII 차트 도구 모음 ───

class ASCIIChart:
    """외부 라이브러리 없이 콘솔에서 차트를 그리는 도구"""

    @staticmethod
    def bar_horizontal(data, title="", width=40):
        """
        수평 막대 그래프.

        Pandas에서:
          df.plot(kind='barh')
          # 또는
          df.plot.barh()
        """
        print(f"\n  ┌─ {title} {'─' * (width - len(title))}┐")
        max_val = max(data.values()) if data else 1

        for label, value in data.items():
            bar_len = int(value / max_val * width)
            bar = "█" * bar_len
            print(f"  │ {str(label):>8} {bar} {value}")

        print(f"  └{'─' * (width + 12)}┘")

    @staticmethod
    def bar_vertical(data, title="", height=15):
        """
        수직 막대 그래프.

        Pandas에서:
          df.plot(kind='bar')
          # 또는
          df.plot.bar()
        """
        print(f"\n  [{title}]")
        labels = list(data.keys())
        values = list(data.values())
        max_val = max(values) if values else 1
        col_width = max(len(str(l)) for l in labels) + 2

        for row in range(height, 0, -1):
            threshold = max_val * row / height
            line = "  │"
            for v in values:
                if v >= threshold:
                    line += ("██" + " " * (col_width - 2))
                else:
                    line += " " * col_width
            print(line)

        print("  └" + "─" * (col_width * len(values) + 1))
        label_line = "   "
        for l in labels:
            label_line += f"{str(l):<{col_width}}"
        print(label_line)

    @staticmethod
    def line_chart(x_labels, y_values, title="", height=15, width=50):
        """
        라인 차트.

        Pandas에서:
          df.plot(kind='line')
          # 또는
          df.plot()  (기본이 line)
        """
        print(f"\n  [{title}]")
        min_val = min(y_values)
        max_val = max(y_values)
        val_range = max_val - min_val if max_val != min_val else 1

        # 그리드 생성
        grid = [[' ' for _ in range(width)] for _ in range(height)]

        # 값을 그리드 위치로 변환
        for i, val in enumerate(y_values):
            x = int(i / (len(y_values) - 1) * (width - 1)) if len(y_values) > 1 else 0
            y = int((val - min_val) / val_range * (height - 1))
            grid[height - 1 - y][x] = '●'

            # 포인트 사이를 선으로 연결
            if i > 0:
                prev_x = int((i - 1) / (len(y_values) - 1) * (width - 1))
                prev_y = int((y_values[i - 1] - min_val) / val_range * (height - 1))
                curr_y = y

                steps = abs(x - prev_x)
                if steps > 0:
                    for step in range(1, steps):
                        sx = prev_x + step
                        sy_f = prev_y + (curr_y - prev_y) * step / steps
                        sy = int(sy_f)
                        if 0 <= height - 1 - sy < height and 0 <= sx < width:
                            if grid[height - 1 - sy][sx] == ' ':
                                grid[height - 1 - sy][sx] = '·'

        # 출력
        for row_idx, row in enumerate(grid):
            val = max_val - (max_val - min_val) * row_idx / (height - 1)
            print(f"  {val:>8.0f} │{''.join(row)}│")
        print(f"  {'':>8} └{'─' * width}┘")

        # X축 라벨
        if len(x_labels) <= 10:
            x_line = "           "
            for i, label in enumerate(x_labels):
                pos = int(i / (len(x_labels) - 1) * width) if len(x_labels) > 1 else 0
                x_line = x_line[:11 + pos] + str(label) + x_line[11 + pos + len(str(label)):]
            print(x_line[:11 + width])

    @staticmethod
    def histogram(values, bins=10, title="", width=40):
        """
        히스토그램 (분포도).

        Pandas에서:
          df['수학'].plot(kind='hist', bins=10)
          # 또는
          df['수학'].hist(bins=10)
        """
        print(f"\n  [{title}]")
        min_val = min(values)
        max_val = max(values)
        bin_width = (max_val - min_val) / bins

        # 빈별 카운트
        counts = [0] * bins
        for v in values:
            idx = min(int((v - min_val) / bin_width), bins - 1)
            counts[idx] += 1

        max_count = max(counts) if counts else 1

        for i in range(bins):
            low = min_val + i * bin_width
            high = low + bin_width
            bar_len = int(counts[i] / max_count * width)
            bar = "▓" * bar_len
            print(f"  {low:>6.0f}~{high:<6.0f} │{bar} {counts[i]}")

    @staticmethod
    def scatter(x_values, y_values, title="", height=15, width=40):
        """
        산점도.

        Pandas에서:
          df.plot(kind='scatter', x='수학', y='영어')
          # 또는
          df.plot.scatter(x='수학', y='영어')
        """
        print(f"\n  [{title}]")
        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)
        x_range = x_max - x_min if x_max != x_min else 1
        y_range = y_max - y_min if y_max != y_min else 1

        grid = [[' ' for _ in range(width)] for _ in range(height)]

        for x, y in zip(x_values, y_values):
            gx = int((x - x_min) / x_range * (width - 1))
            gy = int((y - y_min) / y_range * (height - 1))
            grid[height - 1 - gy][gx] = '◆'

        for row_idx, row in enumerate(grid):
            val = y_max - (y_max - y_min) * row_idx / (height - 1)
            print(f"  {val:>6.0f} │{''.join(row)}│")
        print(f"  {'':>6} └{'─' * width}┘")
        print(f"  {'':>8}{x_min:<10.0f}{'':>{width - 20}}{x_max:>10.0f}")

    @staticmethod
    def pie_chart(data, title=""):
        """
        파이 차트 (텍스트).

        Pandas에서:
          df.plot(kind='pie')
          # 또는
          df.plot.pie()
        """
        print(f"\n  [{title}]")
        total = sum(data.values())
        for label, value in data.items():
            pct = value / total * 100
            bar_len = int(pct / 2)
            bar = "█" * bar_len
            print(f"  {str(label):>10}: {bar} {pct:.1f}% ({value})")

    @staticmethod
    def box_plot(data_dict, title=""):
        """
        박스 플롯 (상자 그림).

        Pandas에서:
          df.plot(kind='box')
          # 또는
          df.boxplot()
        """
        print(f"\n  [{title}]")
        for label, values in data_dict.items():
            sorted_v = sorted(values)
            n = len(sorted_v)
            min_v = sorted_v[0]
            q1 = sorted_v[n // 4]
            median = sorted_v[n // 2]
            q3 = sorted_v[3 * n // 4]
            max_v = sorted_v[-1]
            print(f"  {str(label):>8}: "
                  f"min={min_v:>3} ├─[{q1:>3}──{median:>3}──{q3:>3}]─┤ max={max_v:>3}")


chart = ASCIIChart()


# ─────────────────────────────────────────────────────────────────────────
# 1. 막대 그래프 (Bar Chart)
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 1. 막대 그래프 (Bar Chart)")
print("─" * 70)

print("""
  막대 그래프: 카테고리별 값을 비교할 때!

  Pandas 사용법:
    df.plot(kind='bar')                    # 수직 막대
    df.plot(kind='barh')                   # 수평 막대
    df.plot(kind='bar', figsize=(10, 6))   # 크기 지정
    df.plot(kind='bar', color='skyblue')   # 색상 지정
    df.plot(kind='bar', title='제목')      # 제목
""")

# 학생별 수학 점수
student_scores = {
    '김민수': 90, '이영희': 88, '박철수': 65,
    '최지영': 98, '정하늘': 72, '한서준': 85,
}

chart.bar_horizontal(student_scores, "학생별 수학 점수")
# ── Pandas: df.set_index('이름')['수학'].plot(kind='barh') ──

chart.bar_vertical(student_scores, "학생별 수학 점수 (수직)")
# ── Pandas: df.set_index('이름')['수학'].plot(kind='bar') ──


# ─────────────────────────────────────────────────────────────────────────
# 2. 라인 차트 (Line Chart)
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 2. 라인 차트 (Line Chart)")
print("─" * 70)

print("""
  라인 차트: 시간에 따른 변화를 볼 때!

  Pandas 사용법:
    df.plot()                              # 기본이 line!
    df.plot(kind='line')                   # 명시적
    df.plot(kind='line', marker='o')       # 점 표시
    df.plot(kind='line',
            xlabel='월', ylabel='매출',
            title='월별 매출 추이')
""")

# 월별 매출
months = ['1월', '2월', '3월', '4월', '5월', '6월',
          '7월', '8월', '9월', '10월', '11월', '12월']
sales = [120, 135, 148, 162, 155, 170,
         180, 195, 175, 160, 190, 210]

chart.line_chart(months, sales, "월별 매출 추이 (만원)", height=12, width=50)
# ── Pandas: ──
# df = pd.DataFrame({'월': months, '매출': sales})
# df.set_index('월')['매출'].plot(kind='line', marker='o', title='월별 매출')


# ─────────────────────────────────────────────────────────────────────────
# 3. 히스토그램 (Histogram)
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 3. 히스토그램 (Histogram)")
print("─" * 70)

print("""
  히스토그램: 값의 분포(빈도)를 볼 때!

  Pandas 사용법:
    df['수학'].plot(kind='hist', bins=10)
    df['수학'].hist(bins=10)
    df.plot(kind='hist', bins=20, alpha=0.7)  # 투명도

  bins = 구간 수 (많을수록 세밀하게)
""")

# 100명의 시험 점수 생성 (정규분포 비슷하게)
test_scores = []
for _ in range(100):
    # Box-Muller 변환으로 정규분포 생성
    u1 = random.random()
    u2 = random.random()
    z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
    score = int(70 + z * 15)  # 평균 70, 표준편차 15
    score = max(0, min(100, score))
    test_scores.append(score)

chart.histogram(test_scores, bins=10, title="시험 점수 분포 (100명)")
# ── Pandas: df['점수'].hist(bins=10) ──

avg = sum(test_scores) / len(test_scores)
print(f"  평균: {avg:.1f}점")


# ─────────────────────────────────────────────────────────────────────────
# 4. 산점도 (Scatter Plot)
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 4. 산점도 (Scatter Plot)")
print("─" * 70)

print("""
  산점도: 두 변수 사이의 관계를 볼 때!

  Pandas 사용법:
    df.plot(kind='scatter', x='수학', y='영어')
    df.plot.scatter(x='수학', y='영어',
                    c='학년',          # 색상을 학년으로
                    s=df['총점'] * 0.5, # 점 크기를 총점으로
                    title='수학-영어 관계')
""")

# 수학 vs 영어 점수 (상관관계)
math_scores = [random.randint(40, 100) for _ in range(30)]
eng_scores = [int(s * 0.7 + random.randint(-10, 20) + 20) for s in math_scores]
eng_scores = [max(0, min(100, e)) for e in eng_scores]

chart.scatter(math_scores, eng_scores, "수학 vs 영어 점수 (상관관계)",
              height=12, width=40)
# ── Pandas: df.plot.scatter(x='수학', y='영어') ──

# 상관계수 계산
n = len(math_scores)
mean_m = sum(math_scores) / n
mean_e = sum(eng_scores) / n
cov = sum((m - mean_m) * (e - mean_e) for m, e in zip(math_scores, eng_scores)) / n
std_m = (sum((m - mean_m) ** 2 for m in math_scores) / n) ** 0.5
std_e = (sum((e - mean_e) ** 2 for e in eng_scores) / n) ** 0.5
corr = cov / (std_m * std_e) if std_m * std_e > 0 else 0
print(f"  상관계수(r): {corr:.3f} ({'양의 상관' if corr > 0.3 else '약한 상관'})")
# ── Pandas: df[['수학', '영어']].corr() ──


# ─────────────────────────────────────────────────────────────────────────
# 5. 파이 차트 (Pie Chart)
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 5. 파이 차트 (Pie Chart)")
print("─" * 70)

print("""
  파이 차트: 전체 대비 비율을 볼 때!

  Pandas 사용법:
    df['카테고리'].value_counts().plot(kind='pie')
    df.plot(kind='pie', y='열', autopct='%1.1f%%')
""")

# 혈액형 분포
blood_types = {'A형': 34, 'B형': 27, 'O형': 28, 'AB형': 11}
chart.pie_chart(blood_types, "혈액형 분포 (100명)")
# ── Pandas: df['혈액형'].value_counts().plot(kind='pie', autopct='%1.1f%%') ──


# ─────────────────────────────────────────────────────────────────────────
# 6. 박스 플롯 (Box Plot)
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 6. 박스 플롯 (Box Plot)")
print("─" * 70)

print("""
  박스 플롯: 데이터의 분포, 중앙값, 이상치를 한눈에!

  ├─[Q1──중앙값──Q3]─┤
  │   │      │     │  │
  최소 25%   50%  75% 최대

  Pandas 사용법:
    df.plot(kind='box')
    df.boxplot(column=['수학', '영어', '국어'])
    df.boxplot(column='수학', by='학년')  # 그룹별!
""")

# 과목별 점수 분포
subject_data = {
    '수학': [random.randint(40, 100) for _ in range(30)],
    '영어': [random.randint(50, 95) for _ in range(30)],
    '국어': [random.randint(60, 100) for _ in range(30)],
    '과학': [random.randint(30, 90) for _ in range(30)],
}

chart.box_plot(subject_data, "과목별 점수 분포")
# ── Pandas: df[['수학', '영어', '국어', '과학']].plot(kind='box') ──


# ─────────────────────────────────────────────────────────────────────────
# 7. 서브플롯 — 여러 그래프 한번에
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 7. 서브플롯 (여러 그래프)")
print("─" * 70)

print("""
  하나의 그림에 여러 그래프를 배치할 수 있어요!

  Pandas 사용법:
    # 방법 1: subplots=True
    df.plot(subplots=True, layout=(2, 2), figsize=(12, 8))

    # 방법 2: matplotlib 직접 사용
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    df['수학'].plot(ax=axes[0, 0], kind='hist', title='수학')
    df['영어'].plot(ax=axes[0, 1], kind='hist', title='영어')
    df.plot(ax=axes[1, 0], kind='scatter', x='수학', y='영어')
    df['학년'].value_counts().plot(ax=axes[1, 1], kind='pie')
""")

# ASCII로 여러 차트를 연속으로
print("\n  [서브플롯 시뮬레이션 — 4개 차트]")

# 차트 1: 학생별 점수
chart.bar_horizontal(
    {'민수': 90, '영희': 88, '철수': 65, '지영': 98},
    "차트 1: 학생별 수학 점수"
)

# 차트 2: 점수 분포
chart.histogram(
    [random.randint(40, 100) for _ in range(50)],
    bins=6, title="차트 2: 점수 분포"
)

# 차트 3: 등급 비율
chart.pie_chart(
    {'A': 8, 'B': 15, 'C': 12, 'D': 4, 'F': 1},
    "차트 3: 등급 비율"
)

# 차트 4: 과목 비교
chart.box_plot(
    {'수학': [85, 90, 78, 92, 65], '영어': [88, 95, 82, 90, 70]},
    "차트 4: 과목별 비교"
)


# ─────────────────────────────────────────────────────────────────────────
# 8. 실전 차트 패턴
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 8. 실전 차트 패턴")
print("─" * 70)

# 시계열 차트 — 주가 변동
print("\n[실전 1] 시계열 — 주가 변동:")
prices = [50000]
for _ in range(29):
    change = random.uniform(-0.03, 0.035)
    prices.append(int(prices[-1] * (1 + change)))

days = [f'D{i+1}' for i in range(30)]
chart.line_chart(days, prices, "30일 주가 변동", height=10, width=50)
# ── Pandas: df.set_index('날짜')['종가'].plot(title='주가') ──

# 비교 차트 — 여러 시리즈
print("\n[실전 2] 비교 차트 — A반 vs B반:")
class_a_avg = {'수학': 82, '영어': 78, '국어': 85, '과학': 80}
class_b_avg = {'수학': 75, '영어': 88, '국어': 80, '과학': 72}
print("\n  A반 vs B반 과목별 평균:")
for subj in class_a_avg:
    a = class_a_avg[subj]
    b = class_b_avg[subj]
    bar_a = "█" * (a // 5)
    bar_b = "▓" * (b // 5)
    print(f"  {subj:>4} A반 │{bar_a} {a}")
    print(f"       B반 │{bar_b} {b}")
    print(f"       {'':>4} │")
# ── Pandas: df.groupby('반')[['수학','영어','국어','과학']].mean().plot(kind='bar') ──

# 히트맵 — 상관관계 매트릭스
print("\n[실전 3] 상관관계 히트맵:")
subjects_names = ['수학', '영어', '국어', '과학']
# 간단한 상관계수 시뮬레이션
corr_matrix = [
    [1.00, 0.75, 0.60, 0.82],
    [0.75, 1.00, 0.55, 0.70],
    [0.60, 0.55, 1.00, 0.45],
    [0.82, 0.70, 0.45, 1.00],
]

header = "       " + "  ".join(f"{s:>4}" for s in subjects_names)
print(header)
for i, subj in enumerate(subjects_names):
    line = f"  {subj:>4} "
    for j in range(len(subjects_names)):
        val = corr_matrix[i][j]
        if val >= 0.8:
            symbol = "████"
        elif val >= 0.6:
            symbol = "▓▓▓▓"
        elif val >= 0.4:
            symbol = "▒▒▒▒"
        else:
            symbol = "░░░░"
        line += f" {symbol}"
    line += f"  ({', '.join(f'{v:.2f}' for v in corr_matrix[i])})"
    print(line)
print("  범례: ████ ≥0.8  ▓▓▓▓ ≥0.6  ▒▒▒▒ ≥0.4  ░░░░ <0.4")
# ── Pandas: df[['수학','영어','국어','과학']].corr().style.background_gradient() ──
# ── 또는: import seaborn as sns; sns.heatmap(df.corr(), annot=True) ──


# ─────────────────────────────────────────────────────────────────────────
# ★ 실습: 매출 데이터 대시보드
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "═" * 70)
print(" ★ 실습: 매출 데이터 대시보드")
print("═" * 70)

# 매출 데이터 생성
categories = ['전자제품', '의류', '식품', '도서', '가구']
months_data = {}
for cat in categories:
    base = random.randint(500, 2000)
    months_data[cat] = [base + random.randint(-200, 300) for _ in range(12)]

month_labels = [f'{m}월' for m in range(1, 13)]

# 대시보드 1: 카테고리별 연간 총 매출
print("\n── 대시보드 1: 카테고리별 연간 총 매출 ──")
annual_totals = {cat: sum(months_data[cat]) for cat in categories}
chart.bar_horizontal(annual_totals, "카테고리별 연간 총 매출 (만원)", width=35)

# 대시보드 2: 월별 전체 매출 추이
print("\n── 대시보드 2: 월별 전체 매출 추이 ──")
monthly_totals = [sum(months_data[cat][m] for cat in categories) for m in range(12)]
chart.line_chart(month_labels, monthly_totals, "월별 전체 매출 (만원)", height=10, width=50)

# 대시보드 3: 매출 비율
print("\n── 대시보드 3: 카테고리별 매출 비중 ──")
chart.pie_chart(annual_totals, "매출 비중")

# 대시보드 4: 카테고리별 월 매출 분포
print("\n── 대시보드 4: 카테고리별 월 매출 분포 ──")
chart.box_plot(months_data, "월별 매출 분포")

# 대시보드 5: 요약 통계
print("\n── 대시보드 5: 요약 통계 ──")
print(f"\n  {'카테고리':>8}  {'평균':>8}  {'최소':>8}  {'최대':>8}  {'합계':>10}")
print("  " + "─" * 50)
grand_total = 0
for cat in categories:
    vals = months_data[cat]
    avg = sum(vals) / len(vals)
    total = sum(vals)
    grand_total += total
    print(f"  {cat:>8}  {avg:>8.0f}  {min(vals):>8}  {max(vals):>8}  {total:>10,}")
print("  " + "─" * 50)
print(f"  {'전체':>8}  {'':>8}  {'':>8}  {'':>8}  {grand_total:>10,}")

# ── Pandas로 대시보드: ──
# import matplotlib.pyplot as plt
#
# fig, axes = plt.subplots(2, 2, figsize=(14, 10))
#
# # 차트 1: 카테고리별 총 매출
# df.sum().plot(kind='barh', ax=axes[0,0], title='카테고리별 총 매출')
#
# # 차트 2: 월별 추이
# df.sum(axis=1).plot(ax=axes[0,1], marker='o', title='월별 매출 추이')
#
# # 차트 3: 비율
# df.sum().plot(kind='pie', ax=axes[1,0], autopct='%1.1f%%')
#
# # 차트 4: 분포
# df.plot(kind='box', ax=axes[1,1], title='매출 분포')
#
# plt.tight_layout()
# plt.savefig('dashboard.png', dpi=150)
# plt.show()


# ─────────────────────────────────────────────────────────────────────────
# 정리
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "═" * 70)
print(" 정리: 시각화 도구 모음")
print("═" * 70)

print("""
  ┌───────────┬─────────────────────┬────────────────────┐
  │ 차트 종류 │ Pandas 코드         │ 언제 사용?         │
  ├───────────┼─────────────────────┼────────────────────┤
  │ line      │ df.plot()           │ 시계열, 추이       │
  │ bar       │ df.plot(kind='bar') │ 카테고리 비교      │
  │ barh      │ df.plot(kind='barh')│ 긴 라벨            │
  │ hist      │ df.hist()           │ 분포               │
  │ scatter   │ df.plot.scatter()   │ 두 변수 관계       │
  │ pie       │ df.plot(kind='pie') │ 비율               │
  │ box       │ df.boxplot()        │ 분포 요약          │
  │ area      │ df.plot.area()      │ 누적 면적          │
  │ hexbin    │ df.plot.hexbin()    │ 밀도 산점도        │
  └───────────┴─────────────────────┴────────────────────┘

  스타일 옵션:
    figsize=(12, 6)     → 그림 크기
    color='skyblue'     → 색상
    title='제목'        → 제목
    xlabel='X축'        → X축 라벨
    ylabel='Y축'        → Y축 라벨
    legend=True         → 범례
    grid=True           → 격자선
    alpha=0.7           → 투명도
    rot=45              → 라벨 회전
""")

print("✅ 09단계 완료! 다음은 10_practical_patterns.py에서 실전 패턴을 배워요!")
