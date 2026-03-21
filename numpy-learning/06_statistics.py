# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   NumPy 학습 06단계: 통계(Statistics)
#   ─ 기술통계, 상관계수, 히스토그램, 랜덤 분포, 샘플링 ─
#   ■ 실행 방법: python 06_statistics.py
#   ■ NumPy 설치: pip install numpy
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


import math
import random


# ═══════════════════════════════════════════════════════════════════════════════
#  1. 기술통계 - 데이터를 숫자 하나로 요약!
# ═══════════════════════════════════════════════════════════════════════════════
#
#  기술통계는 "데이터의 특징을 숫자로 설명"하는 거야!
#  마치 반 친구 30명의 키를 "평균 165cm, 가장 큰 애 180cm" 이렇게!

print("=" * 70)
print("1. 기술통계 - mean, median, std, var, percentile")
print("=" * 70)


def py_mean(data):
    """평균: 모든 값을 더해서 개수로 나누기"""
    return sum(data) / len(data)


def py_median(data):
    """중앙값: 정렬했을 때 가운데 값
    왜 필요해? 평균은 극단값에 약하거든!
    예: [10, 20, 30, 40, 1000] → 평균=220(엉뚱!), 중앙값=30(합리적!)
    """
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n % 2 == 1:
        return sorted_data[n // 2]
    else:
        return (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2


def py_var(data, ddof=0):
    """분산: 데이터가 평균에서 얼마나 퍼져있는지
    ddof=0: 모분산 (NumPy 기본), ddof=1: 표본분산 (통계학 기본)
    """
    mean = py_mean(data)
    return sum((x - mean) ** 2 for x in data) / (len(data) - ddof)


def py_std(data, ddof=0):
    """표준편차: 분산의 제곱근 (단위를 원래대로!)
    분산이 cm²이면 표준편차는 cm
    """
    return math.sqrt(py_var(data, ddof))


def py_percentile(data, q):
    """백분위수: 하위 q%에 해당하는 값
    25%: 1사분위수(Q1), 50%: 중앙값, 75%: 3사분위수(Q3)
    """
    sorted_data = sorted(data)
    n = len(sorted_data)
    idx = (n - 1) * q / 100.0
    lower = int(idx)
    upper = lower + 1
    if upper >= n:
        return sorted_data[-1]
    frac = idx - lower
    return sorted_data[lower] * (1 - frac) + sorted_data[upper] * frac


# 시험 점수 데이터
scores = [72, 85, 90, 65, 78, 92, 88, 55, 76, 83,
          94, 67, 81, 73, 86, 91, 79, 60, 84, 77]

print(f"\n시험 점수 ({len(scores)}명): {scores}")
print(f"\n  평균(mean):     {py_mean(scores):.1f}")
print(f"  중앙값(median):  {py_median(scores):.1f}")
print(f"  분산(var):       {py_var(scores):.1f}")
print(f"  표준편차(std):   {py_std(scores):.1f}")
print(f"  최솟값(min):     {min(scores)}")
print(f"  최댓값(max):     {max(scores)}")
print(f"  범위(range):     {max(scores) - min(scores)}")

print(f"\n── 백분위수 ──")
for q in [25, 50, 75, 90]:
    print(f"  {q}%ile: {py_percentile(scores, q):.1f}")

print(f"\n  Q1(25%): {py_percentile(scores, 25):.1f}")
print(f"  Q3(75%): {py_percentile(scores, 75):.1f}")
iqr = py_percentile(scores, 75) - py_percentile(scores, 25)
print(f"  IQR(Q3-Q1): {iqr:.1f}  ← 중간 50%의 범위")

# 평균 vs 중앙값 차이
print(f"\n── 평균 vs 중앙값: 극단값의 영향 ──")
normal_data = [50, 55, 60, 65, 70]
skewed_data = [50, 55, 60, 65, 500]  # 극단값!
print(f"  정상 데이터: {normal_data}")
print(f"    평균={py_mean(normal_data):.1f}, 중앙값={py_median(normal_data):.1f}")
print(f"  극단값 포함: {skewed_data}")
print(f"    평균={py_mean(skewed_data):.1f}, 중앙값={py_median(skewed_data):.1f}")
print(f"    → 중앙값은 극단값에 안 흔들려! 더 안정적!")

# 【NumPy】
# np.mean(scores), np.median(scores)
# np.var(scores), np.std(scores)
# np.percentile(scores, [25, 50, 75])
# np.min(scores), np.max(scores), np.ptp(scores)  # ptp = peak-to-peak = 범위


# ═══════════════════════════════════════════════════════════════════════════════
#  2. 상관계수 - 두 변수의 관계
# ═══════════════════════════════════════════════════════════════════════════════
#
#  상관계수는 "두 변수가 함께 움직이는 정도"야!
#  -1: 완전히 반대로 움직임 (하나 오르면 하나 내려감)
#   0: 관계 없음
#  +1: 완전히 같이 움직임 (하나 오르면 같이 올라감)

print("\n" + "=" * 70)
print("2. 상관계수 - 두 변수의 관계")
print("=" * 70)


def py_corrcoef(x, y):
    """피어슨 상관계수 (np.corrcoef 흉내)
    r = Σ(xi - x̄)(yi - ȳ) / √(Σ(xi - x̄)² × Σ(yi - ȳ)²)
    """
    n = len(x)
    x_mean = py_mean(x)
    y_mean = py_mean(y)

    numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
    denom_x = math.sqrt(sum((xi - x_mean) ** 2 for xi in x))
    denom_y = math.sqrt(sum((yi - y_mean) ** 2 for yi in y))

    if denom_x == 0 or denom_y == 0:
        return 0
    return numerator / (denom_x * denom_y)


# 예시 데이터
study_hours = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
test_scores = [35, 42, 50, 55, 62, 68, 75, 80, 88, 95]
sleep_hours = [9, 8, 7, 8, 7, 6, 5, 6, 5, 4]

print(f"\n공부시간: {study_hours}")
print(f"시험점수: {test_scores}")
print(f"수면시간: {sleep_hours}")

r_study_score = py_corrcoef(study_hours, test_scores)
r_study_sleep = py_corrcoef(study_hours, sleep_hours)
r_score_sleep = py_corrcoef(test_scores, sleep_hours)

print(f"\n  공부↔점수 상관: {r_study_score:+.4f}  ← 강한 양의 상관! (공부할수록 점수↑)")
print(f"  공부↔수면 상관: {r_study_sleep:+.4f}  ← 강한 음의 상관! (공부할수록 수면↓)")
print(f"  점수↔수면 상관: {r_score_sleep:+.4f}  ← 강한 음의 상관!")

print(f"\n── 상관계수 해석 기준 ──")
print(f"  |r| >= 0.7: 강한 상관")
print(f"  |r| >= 0.4: 보통 상관")
print(f"  |r| >= 0.2: 약한 상관")
print(f"  |r| < 0.2:  거의 무관")
print(f"\n  ⚠️ 주의: 상관 ≠ 인과! 아이스크림과 익사 사고가 상관 있지만,")
print(f"     아이스크림이 익사를 유발하는 건 아니야! (공통 원인: 여름 더위)")

# 【NumPy】
# np.corrcoef(study_hours, test_scores)  → 2×2 상관행렬
# np.corrcoef(study_hours, test_scores)[0, 1]  → 상관계수


# ═══════════════════════════════════════════════════════════════════════════════
#  3. 히스토그램 - 빈도 분석
# ═══════════════════════════════════════════════════════════════════════════════
#
#  히스토그램은 "데이터를 구간별로 세기"야!
#  "60~70점 몇 명, 70~80점 몇 명..." 이런 식!

print("\n" + "=" * 70)
print("3. 히스토그램 - 빈도 분석")
print("=" * 70)


def py_histogram(data, bins=10, range_=None):
    """히스토그램 계산 (np.histogram 흉내)

    Returns:
        counts: 각 구간의 빈도
        edges: 구간 경계값들
    """
    if range_ is None:
        min_val, max_val = min(data), max(data)
    else:
        min_val, max_val = range_

    bin_width = (max_val - min_val) / bins
    edges = [min_val + i * bin_width for i in range(bins + 1)]
    counts = [0] * bins

    for val in data:
        if val == max_val:
            counts[-1] += 1
        else:
            bin_idx = int((val - min_val) / bin_width)
            if 0 <= bin_idx < bins:
                counts[bin_idx] += 1

    return counts, edges


# 100명의 시험 점수
random.seed(42)
exam_scores = [int(random.gauss(70, 15)) for _ in range(100)]
exam_scores = [max(0, min(100, s)) for s in exam_scores]  # 0~100 제한

counts, edges = py_histogram(exam_scores, bins=10, range_=(0, 100))

print(f"\n100명 시험 점수 분포:")
print(f"{'구간':>12} {'빈도':>6} {'막대그래프'}")
print("-" * 50)
max_count = max(counts)
for i in range(len(counts)):
    bar = "█" * int(counts[i] / max_count * 30) if max_count > 0 else ""
    print(f"  {edges[i]:>3.0f}~{edges[i+1]:>3.0f}점 {counts[i]:>4}명  {bar}")

print(f"\n  총 {sum(counts)}명")
print(f"  최빈 구간: {edges[counts.index(max(counts))]:.0f}~{edges[counts.index(max(counts))+1]:.0f}점 ({max(counts)}명)")

# 【NumPy】
# counts, edges = np.histogram(exam_scores, bins=10, range=(0, 100))


# ═══════════════════════════════════════════════════════════════════════════════
#  4. 랜덤 분포 - 확률의 세계
# ═══════════════════════════════════════════════════════════════════════════════
#
#  분포는 "확률의 모양"이야!
#  주사위: 균일분포 (모든 면이 1/6)
#  키:    정규분포 (평균 근처에 몰려있고 양쪽으로 퍼짐)

print("\n" + "=" * 70)
print("4. 랜덤 분포")
print("=" * 70)


# ── 균일분포 (Uniform) ──
def py_uniform(low, high, size):
    """균일분포: low~high 사이에서 모든 값이 동일한 확률"""
    return [random.uniform(low, high) for _ in range(size)]


# ── 정규분포 (Normal/Gaussian) ──
def py_normal(loc, scale, size):
    """정규분포 (종 모양)
    loc: 평균 (종의 꼭대기 위치)
    scale: 표준편차 (종의 폭)
    """
    return [random.gauss(loc, scale) for _ in range(size)]


# ── 이항분포 (Binomial) ──
def py_binomial(n, p, size):
    """이항분포: n번 시행에서 성공(확률 p)하는 횟수
    예: 동전 10번 던져서 앞면 나오는 횟수
    """
    results = []
    for _ in range(size):
        successes = sum(1 for _ in range(n) if random.random() < p)
        results.append(successes)
    return results


# ── 포아송분포 (Poisson) ──
def py_poisson(lam, size):
    """포아송분포: 단위 시간당 평균 lam번 발생하는 사건
    예: 1시간에 평균 5명 방문하는 가게에서 실제 방문 수

    알고리즘: Knuth의 방법
    """
    results = []
    for _ in range(size):
        L = math.exp(-lam)
        k = 0
        p = 1.0
        while p > L:
            k += 1
            p *= random.random()
        results.append(k - 1)
    return results


random.seed(42)

print(f"\n── 균일분포 (Uniform) ──")
uniform_data = py_uniform(0, 10, 1000)
print(f"  0~10 사이 균일분포 1000개 생성")
print(f"  평균: {py_mean(uniform_data):.2f} (이론값: 5.0)")
print(f"  표준편차: {py_std(uniform_data):.2f} (이론값: {10/math.sqrt(12):.2f})")
print(f"  → 모든 값이 비슷한 빈도로 나타남!")

print(f"\n── 정규분포 (Normal) ──")
normal_data = py_normal(170, 10, 1000)
print(f"  키 분포: 평균 170cm, 표준편차 10cm, 1000명")
print(f"  평균: {py_mean(normal_data):.2f} (이론값: 170)")
print(f"  표준편차: {py_std(normal_data):.2f} (이론값: 10)")
# 68-95-99.7 법칙
within_1std = sum(1 for x in normal_data if 160 <= x <= 180) / len(normal_data)
within_2std = sum(1 for x in normal_data if 150 <= x <= 190) / len(normal_data)
print(f"  ±1σ (160~180cm) 비율: {within_1std*100:.1f}% (이론값: 68.3%)")
print(f"  ±2σ (150~190cm) 비율: {within_2std*100:.1f}% (이론값: 95.4%)")

print(f"\n── 이항분포 (Binomial) ──")
coin_flips = py_binomial(10, 0.5, 1000)
print(f"  동전 10번 던지기 × 1000회")
print(f"  앞면 평균: {py_mean(coin_flips):.2f}회 (이론값: 5.0)")
print(f"  표준편차: {py_std(coin_flips):.2f} (이론값: {math.sqrt(10*0.5*0.5):.2f})")

print(f"\n── 포아송분포 (Poisson) ──")
visitors = py_poisson(5, 1000)
print(f"  1시간당 평균 5명 방문 × 1000시간")
print(f"  평균: {py_mean(visitors):.2f} (이론값: 5.0)")
print(f"  표준편차: {py_std(visitors):.2f} (이론값: {math.sqrt(5):.2f})")

# 【NumPy】
# rng = np.random.default_rng(42)
# rng.uniform(0, 10, 1000)
# rng.normal(170, 10, 1000)
# rng.binomial(10, 0.5, 1000)
# rng.poisson(5, 1000)


# ═══════════════════════════════════════════════════════════════════════════════
#  5. 시드(Seed)와 재현성
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("5. 시드(Seed) - 재현 가능한 랜덤")
print("=" * 70)

print(f"\n── 왜 시드가 중요할까? ──")
print(f"  1. 실험 재현: 다른 사람이 같은 결과를 얻을 수 있어야!")
print(f"  2. 디버깅: 버그를 재현하려면 같은 데이터가 필요!")
print(f"  3. 비교: 알고리즘 A vs B를 같은 데이터로 테스트!")

# 같은 시드 = 같은 결과
print(f"\n── 같은 시드 → 같은 결과 ──")
random.seed(123)
run1 = [random.randint(1, 100) for _ in range(5)]
random.seed(123)
run2 = [random.randint(1, 100) for _ in range(5)]
random.seed(456)
run3 = [random.randint(1, 100) for _ in range(5)]

print(f"  시드 123 (1회차): {run1}")
print(f"  시드 123 (2회차): {run2}")
print(f"  같은가? {run1 == run2}")
print(f"  시드 456:        {run3}")
print(f"  같은가? {run1 == run3}")

# 【NumPy 최신 권장 방식】
# # 옛날 방식 (전역 상태 - 비추천)
# np.random.seed(42)
# np.random.rand(5)
#
# # 최신 방식 (Generator 객체 - 추천!)
# rng = np.random.default_rng(42)
# rng.random(5)
# # → 각 Generator가 독립적! 다른 코드에 영향 안 미침!


# ═══════════════════════════════════════════════════════════════════════════════
#  6. 샘플링 - 데이터에서 뽑기
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("6. 샘플링 - choice, shuffle, permutation")
print("=" * 70)

random.seed(42)


def py_choice(arr, size=1, replace=True, p=None):
    """배열에서 랜덤 선택 (np.random.choice 흉내)
    replace=True:  복원추출 (뽑고 다시 넣기, 중복 가능)
    replace=False: 비복원추출 (뽑으면 안 넣기, 중복 불가)
    p: 각 원소의 선택 확률
    """
    if p is not None:
        # 가중치 기반 선택
        result = []
        for _ in range(size):
            r = random.random()
            cumsum = 0
            for i, prob in enumerate(p):
                cumsum += prob
                if r <= cumsum:
                    result.append(arr[i])
                    break
        return result
    elif replace:
        return [random.choice(arr) for _ in range(size)]
    else:
        pool = list(arr)
        random.shuffle(pool)
        return pool[:size]


def py_shuffle(arr):
    """배열을 제자리에서 섞기 (원본 변경!)"""
    result = list(arr)
    random.shuffle(result)
    return result


def py_permutation(n):
    """0~n-1의 랜덤 순열"""
    perm = list(range(n))
    random.shuffle(perm)
    return perm


# choice - 복원추출
fruits = ["사과", "바나나", "체리", "딸기", "포도"]
print(f"\n과일: {fruits}")

sample1 = py_choice(fruits, size=3, replace=True)
print(f"\n복원추출(3개): {sample1}")
print(f"→ 같은 과일이 또 나올 수 있어!")

sample2 = py_choice(fruits, size=3, replace=False)
print(f"비복원추출(3개): {sample2}")
print(f"→ 중복 없이 3개 선택!")

# 가중치 기반 선택
items = ["전설", "영웅", "희귀", "일반"]
probs = [0.01, 0.05, 0.20, 0.74]  # 가챠 확률!
gacha_results = py_choice(items, size=100, replace=True, p=probs)
gacha_counts = {item: gacha_results.count(item) for item in items}
print(f"\n── 가챠 시뮬레이션 (100회) ──")
print(f"  확률: {dict(zip(items, probs))}")
print(f"  결과: {gacha_counts}")
print(f"  → 전설 확률 1%... 100번 뽑아도 안 나올 수 있어!")

# shuffle
print(f"\n── shuffle (섞기) ──")
deck = list(range(1, 11))
print(f"  원본: {deck}")
shuffled = py_shuffle(deck)
print(f"  섞기: {shuffled}")

# permutation
print(f"\n── permutation (순열) ──")
perm = py_permutation(10)
print(f"  0~9 랜덤 순서: {perm}")
print(f"  → 인덱스를 섞어서 데이터를 랜덤하게 재배치할 때 사용!")

# 【NumPy】
# rng = np.random.default_rng(42)
# rng.choice(fruits, size=3, replace=False)
# rng.choice(items, size=100, p=probs)
# rng.shuffle(deck)    # 제자리 섞기 (원본 변경)
# rng.permutation(10)  # 순열 (새 배열 반환)


# ═══════════════════════════════════════════════════════════════════════════════
#  7. 실습: 주사위 시뮬레이션과 확률 실험
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("실습: 주사위 확률 실험")
print("=" * 70)

random.seed(42)

# 실험 1: 주사위 1개 던지기
print(f"\n── 실험 1: 주사위 1개, 10000번 ──")
n_rolls = 10000
dice_rolls = [random.randint(1, 6) for _ in range(n_rolls)]
dice_counts = {i: dice_rolls.count(i) for i in range(1, 7)}
print(f"  이론 확률: 각 면 {1/6*100:.2f}%")
print(f"  실험 결과:")
for face, count in dice_counts.items():
    pct = count / n_rolls * 100
    bar = "█" * int(pct * 2)
    print(f"    {face}: {count:>4}회 ({pct:>5.2f}%) {bar}")

# 실험 2: 주사위 2개의 합
print(f"\n── 실험 2: 주사위 2개 합, 10000번 ──")
two_dice_sums = [random.randint(1, 6) + random.randint(1, 6) for _ in range(n_rolls)]
sum_counts = {i: two_dice_sums.count(i) for i in range(2, 13)}
print(f"  합   빈도    확률     막대그래프")
max_freq = max(sum_counts.values())
for s in range(2, 13):
    count = sum_counts[s]
    pct = count / n_rolls * 100
    # 이론 확률
    theory = (6 - abs(s - 7)) / 36 * 100
    bar = "█" * int(count / max_freq * 25)
    print(f"  {s:>2}  {count:>5}  {pct:>5.1f}% ({theory:>4.1f}%)  {bar}")

print(f"\n  → 합 7이 가장 많이 나옴! (6가지 조합: 1+6, 2+5, 3+4, ...)")
print(f"  → 합 2, 12는 1가지씩만! (1+1, 6+6)")

# 실험 3: 몬테카를로로 원주율(π) 추정!
print(f"\n── 실험 3: 몬테카를로 π 추정 ──")
n_points = 100000
inside_circle = 0
for _ in range(n_points):
    x = random.uniform(-1, 1)
    y = random.uniform(-1, 1)
    if x*x + y*y <= 1:
        inside_circle += 1

pi_estimate = 4 * inside_circle / n_points
print(f"  정사각형 안에 {n_points:,}개 점 랜덤 배치")
print(f"  원 안에 들어간 점: {inside_circle:,}개")
print(f"  π 추정값: {pi_estimate:.6f}")
print(f"  실제 π:   {math.pi:.6f}")
print(f"  오차:     {abs(pi_estimate - math.pi):.6f}")
print(f"  → 점을 더 많이 뿌릴수록 정확해져! (큰 수의 법칙)")

# 실험 4: 생일 역설
print(f"\n── 실험 4: 생일 역설 ──")
print(f"  23명이 모이면 생일이 같은 쌍이 있을 확률은 50% 이상!")

def birthday_experiment(n_people, n_trials=10000):
    """n명 중 생일이 같은 쌍이 있는 확률"""
    match_count = 0
    for _ in range(n_trials):
        birthdays = [random.randint(1, 365) for _ in range(n_people)]
        if len(set(birthdays)) < len(birthdays):  # 중복이 있으면!
            match_count += 1
    return match_count / n_trials

for n in [10, 20, 23, 30, 50, 70]:
    prob = birthday_experiment(n)
    bar = "█" * int(prob * 30)
    print(f"  {n:>2}명: {prob*100:>5.1f}% {bar}")

print(f"\n  → 23명만 모여도 50%! 직관과 다르지? 이게 '역설'!")


# ═══════════════════════════════════════════════════════════════════════════════
#  핵심 정리
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("핵심 정리")
print("=" * 70)
print("""
  1. 기술통계:
     - mean(평균), median(중앙값), std(표준편차), var(분산)
     - percentile(백분위수), min/max
     - 극단값 있으면 median이 mean보다 안정적!
  2. 상관계수: -1(반비례) ~ 0(무관) ~ +1(비례)
     - ⚠️ 상관 ≠ 인과!
  3. 히스토그램: 데이터를 구간별로 세기
  4. 랜덤 분포:
     - uniform: 균일  | normal: 정규(종 모양)
     - binomial: 이항 | poisson: 포아송
  5. 시드(seed): 재현성! np.random.default_rng(42) 추천
  6. 샘플링:
     - choice(복원/비복원), shuffle(섞기), permutation(순열)
     - 가중치(p) 지정으로 확률 조절 가능!
""")
