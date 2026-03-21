# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [ML 기초] 학습 04단계: 특성 스케일링 (Feature Scaling)
#   ─ Min-Max, Z-Score, Robust, 원-핫 인코딩, 전처리 파이프라인 ─
#   ■ 실행 방법: python 04_feature_scaling.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 왜 스케일링이 필요한가? - 단위 차이 문제, 시각적 비교
#   2. Min-Max 정규화 - 공식, 직접 구현, 0~1 범위
#   3. Z-Score 표준화 - 평균0/표준편차1, 직접 구현
#   4. Robust 스케일링 - 중앙값/IQR 기반, 이상치에 강한 이유
#   5. 스케일링 비교 실험 - 같은 데이터에 3가지 방법 적용 비교
#   6. 스케일링 주의사항 - 테스트 데이터 누출 금지, fit_transform 패턴
#   7. 원-핫 인코딩 - 범주형 변수 처리, 더미 변수 트랩
#   8. 실전: 학생 데이터 전처리 파이프라인
#
# ─────────────────────────────────────────────────────────────────────────


def lesson1_why_scaling():
    # =========================================================================
    #
    #   레슨 1 — 왜 스케일링이 필요한가?
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 왜 스케일링이 필요한가?    │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 문제: 단위가 다른 특성을 함께 사용할 때
    # ─────────────────────────────────────────────────────────────────────
    #
    #   학생 A: 키 170cm, 몸무게 65kg
    #   학생 B: 키 175cm, 몸무게 80kg
    #
    #   유클리드 거리를 구하면:
    #   d = sqrt((175-170)² + (80-65)²)
    #     = sqrt(25 + 225)
    #     = sqrt(250) ≈ 15.81
    #
    #   여기서 몸무게 차이(15)가 키 차이(5)보다 3배나 크다
    #   → 거리 계산에서 몸무게가 압도적으로 큰 영향을 미친다!
    #
    #   만약 키를 mm로 바꾸면? 1700mm vs 1750mm
    #   d = sqrt((1750-1700)² + (80-65)²)
    #     = sqrt(2500 + 225) ≈ 52.2
    #
    #   → 단위만 바꿨는데 결과가 완전히 달라진다!
    #

    print("  [문제 시연: 단위에 따라 거리가 달라진다]")
    print()

    # cm 단위
    a_cm = [170, 65]    # 키cm, 몸무게kg
    b_cm = [175, 80]
    dist_cm = ((b_cm[0] - a_cm[0])**2 + (b_cm[1] - a_cm[1])**2) ** 0.5

    # mm 단위
    a_mm = [1700, 65]   # 키mm, 몸무게kg
    b_mm = [1750, 80]
    dist_mm = ((b_mm[0] - a_mm[0])**2 + (b_mm[1] - a_mm[1])**2) ** 0.5

    print(f"  키(cm) 사용: 거리 = {dist_cm:.2f}")
    print(f"  키(mm) 사용: 거리 = {dist_mm:.2f}")
    print(f"  → 같은 데이터인데 단위만 바꿨더니 거리가 {dist_mm/dist_cm:.1f}배 차이!")
    print()

    # 각 특성의 기여도 비교
    print("  [각 특성의 거리 기여도]")
    print()
    ki_contrib = (b_cm[0] - a_cm[0])**2
    weight_contrib = (b_cm[1] - a_cm[1])**2
    total = ki_contrib + weight_contrib
    print(f"    키 기여:     {ki_contrib:>6} ({ki_contrib/total*100:>5.1f}%)")
    print(f"    몸무게 기여: {weight_contrib:>6} ({weight_contrib/total*100:>5.1f}%)")
    print(f"    → 몸무게가 거리의 {weight_contrib/total*100:.0f}%를 차지!")
    print()

    # 스케일링이 필요한 알고리즘
    print("  [스케일링이 중요한 알고리즘]")
    print("    O 필요: KNN, SVM, K-Means, 경사하강법, PCA")
    print("    X 불필요: 결정 트리, 랜덤 포레스트 (분할 기반이라 크기 무관)")
    print()


def lesson2_min_max():
    # =========================================================================
    #
    #   레슨 2 — Min-Max 정규화 (Normalization)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : Min-Max 정규화             │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 공식: x_scaled = (x - min) / (max - min)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   결과: 모든 값이 0~1 사이로 변환됨
    #   최솟값 → 0, 최댓값 → 1
    #
    #   비유: 시험 점수를 0~100으로 환산하는 것과 비슷
    #

    def min_max_scale(values):
        """Min-Max 정규화 직접 구현"""
        v_min = min(values)
        v_max = max(values)
        if v_max == v_min:
            return [0.0] * len(values)
        return [(v - v_min) / (v_max - v_min) for v in values]

    # 예제 1: 키 데이터
    heights = [155, 160, 165, 170, 175, 180, 190]
    scaled = min_max_scale(heights)

    print("  [공식] x_scaled = (x - min) / (max - min)")
    print()
    print("  [키 데이터 변환]")
    print(f"    원본: {heights}")
    print(f"    min={min(heights)}, max={max(heights)}")
    print()

    for i, (orig, sc) in enumerate(zip(heights, scaled)):
        bar = "#" * int(sc * 30)
        print(f"    {orig}cm → ({orig}-{min(heights)})/({max(heights)}-{min(heights)}) "
              f"= {sc:.4f} {bar}")
    print()

    # 예제 2: 수동 계산 따라하기
    print("  [수동 계산 연습]")
    print()
    values = [10, 20, 30, 40, 50]
    print(f"    데이터: {values}")
    print(f"    min=10, max=50, 범위=40")
    print()
    for v in values:
        result = (v - 10) / (50 - 10)
        print(f"    ({v} - 10) / 40 = {result:.2f}")
    print()

    # 장단점
    print("  [Min-Max 장단점]")
    print("    장점: 값의 범위가 명확 (0~1)")
    print("    장점: 해석이 직관적")
    print("    단점: 이상치에 매우 민감!")
    print()

    # 이상치 영향 시연
    normal_data = [10, 20, 30, 40, 50]
    outlier_data = [10, 20, 30, 40, 500]  # 500은 이상치

    print("  [이상치 영향]")
    print(f"    정상 데이터:   {normal_data} → 스케일링: {[round(v, 3) for v in min_max_scale(normal_data)]}")
    print(f"    이상치 포함:   {outlier_data} → 스케일링: {[round(v, 3) for v in min_max_scale(outlier_data)]}")
    print("    → 이상치 때문에 나머지 데이터가 0 근처로 몰린다!")
    print()


def lesson3_z_score():
    # =========================================================================
    #
    #   레슨 3 — Z-Score 표준화 (Standardization)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : Z-Score 표준화             │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 공식: z = (x - 평균) / 표준편차
    # ─────────────────────────────────────────────────────────────────────
    #
    #   결과: 평균이 0, 표준편차가 1인 분포로 변환
    #
    #   z값의 의미:
    #     z =  0 → 평균과 같다
    #     z =  1 → 평균보다 표준편차 1만큼 크다
    #     z = -2 → 평균보다 표준편차 2만큼 작다
    #
    #   비유: 전교생 중 자신이 어디쯤인지 보여주는 "편차값"
    #

    def z_score_scale(values):
        """Z-Score 표준화 직접 구현"""
        n = len(values)
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / n
        std = variance ** 0.5
        if std == 0:
            return [0.0] * n
        return [(v - mean) / std for v in values]

    # 예제: 시험 점수
    scores = [55, 60, 65, 70, 75, 80, 85, 90, 95]

    mean = sum(scores) / len(scores)
    variance = sum((s - mean) ** 2 for s in scores) / len(scores)
    std = variance ** 0.5

    print("  [공식] z = (x - 평균) / 표준편차")
    print()
    print(f"  데이터: {scores}")
    print(f"  평균: {mean:.2f}")
    print(f"  분산: {variance:.2f}")
    print(f"  표준편차: {std:.2f}")
    print()

    scaled = z_score_scale(scores)
    print(f"  {'원본':>6} | {'z-score':>8} | 해석")
    print("  " + "-" * 42)

    for orig, z in zip(scores, scaled):
        if abs(z) < 0.01:
            interp = "평균과 같음"
        elif z > 0:
            interp = f"평균보다 {z:.2f}σ 위"
        else:
            interp = f"평균보다 {abs(z):.2f}σ 아래"
        print(f"  {orig:>6} | {z:>+8.4f} | {interp}")
    print()

    # 검증: 변환 후 평균=0, 표준편차=1
    new_mean = sum(scaled) / len(scaled)
    new_var = sum((v - new_mean) ** 2 for v in scaled) / len(scaled)
    new_std = new_var ** 0.5

    print(f"  [변환 후 검증]")
    print(f"    새 평균: {new_mean:.6f} (약 0)")
    print(f"    새 표준편차: {new_std:.6f} (약 1)")
    print()

    # 장단점
    print("  [Z-Score 장단점]")
    print("    장점: 이상치에 Min-Max보다 덜 민감")
    print("    장점: 정규분포 가정 모델에 적합")
    print("    단점: 범위가 정해져 있지 않음 (-3~+3 정도가 보통)")
    print()


def lesson4_robust_scaling():
    # =========================================================================
    #
    #   레슨 4 — Robust 스케일링
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : Robust 스케일링            │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 공식: x_scaled = (x - 중앙값) / IQR
    # ─────────────────────────────────────────────────────────────────────
    #
    #   중앙값 (Median): 정렬했을 때 가운데 값
    #   IQR (사분위 범위): Q3 - Q1 (75%위치 - 25%위치)
    #
    #   이상치에 강한 이유:
    #     평균/표준편차는 이상치에 크게 영향 받지만
    #     중앙값/IQR은 이상치에 거의 영향 받지 않는다!
    #

    def median(values):
        """중앙값 계산"""
        sorted_v = sorted(values)
        n = len(sorted_v)
        if n % 2 == 1:
            return sorted_v[n // 2]
        return (sorted_v[n // 2 - 1] + sorted_v[n // 2]) / 2

    def quartiles(values):
        """Q1, Q2(중앙값), Q3 계산"""
        sorted_v = sorted(values)
        n = len(sorted_v)
        q2 = median(sorted_v)
        lower = sorted_v[:n // 2]
        upper = sorted_v[(n + 1) // 2:]
        q1 = median(lower) if lower else q2
        q3 = median(upper) if upper else q2
        return q1, q2, q3

    def robust_scale(values):
        """Robust 스케일링 직접 구현"""
        q1, q2, q3 = quartiles(values)
        iqr = q3 - q1
        if iqr == 0:
            return [0.0] * len(values)
        return [(v - q2) / iqr for v in values]

    # 이상치가 있는 데이터
    data_with_outlier = [20, 25, 28, 30, 32, 35, 38, 40, 45, 200]

    q1, q2, q3 = quartiles(data_with_outlier)
    iqr = q3 - q1

    print(f"  데이터: {data_with_outlier}")
    print(f"  (200은 이상치!)")
    print()
    print(f"  Q1 (25%): {q1}")
    print(f"  Q2 (중앙값): {q2}")
    print(f"  Q3 (75%): {q3}")
    print(f"  IQR = Q3 - Q1 = {q3} - {q1} = {iqr}")
    print()

    # 수동 계산
    print(f"  [Robust 스케일링 결과]")
    scaled = robust_scale(data_with_outlier)
    for orig, sc in zip(data_with_outlier, scaled):
        indicator = " ← 이상치" if orig == 200 else ""
        print(f"    ({orig} - {q2}) / {iqr} = {sc:>+7.3f}{indicator}")
    print()

    # 비교: 이상치가 다른 스케일링에 미치는 영향
    print("  [이상치 영향 비교]")
    print()

    # Min-Max
    v_min, v_max = min(data_with_outlier), max(data_with_outlier)
    mm_scaled = [(v - v_min) / (v_max - v_min) for v in data_with_outlier]

    # Z-Score
    mean_v = sum(data_with_outlier) / len(data_with_outlier)
    var_v = sum((v - mean_v) ** 2 for v in data_with_outlier) / len(data_with_outlier)
    std_v = var_v ** 0.5
    zs_scaled = [(v - mean_v) / std_v for v in data_with_outlier]

    print(f"    {'값':>5} | {'Min-Max':>8} | {'Z-Score':>8} | {'Robust':>8}")
    print("    " + "-" * 42)
    for i in range(len(data_with_outlier)):
        mark = "*" if data_with_outlier[i] == 200 else " "
        print(f"    {data_with_outlier[i]:>4}{mark}| {mm_scaled[i]:>8.3f} | "
              f"{zs_scaled[i]:>+8.3f} | {scaled[i]:>+8.3f}")
    print()
    print("  → Min-Max: 이상치 때문에 나머지가 0~0.14에 몰림")
    print("  → Robust: 이상치의 영향이 제한적, 나머지가 잘 펼쳐짐")
    print()


def lesson5_scaling_comparison():
    # =========================================================================
    #
    #   레슨 5 — 스케일링 비교 실험
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 스케일링 비교 실험         │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 같은 데이터에 3가지 스케일링 적용 후 KNN 거리 비교
    # ─────────────────────────────────────────────────────────────────────

    # 학생 데이터: [키(cm), 용돈(만원)]
    students = [
        [155, 5], [160, 8], [165, 12], [170, 15],
        [175, 20], [180, 25], [185, 30], [190, 50],
    ]

    def min_max_scale_2d(data):
        cols = list(zip(*data))
        scaled_cols = []
        params = []
        for col in cols:
            v_min, v_max = min(col), max(col)
            params.append((v_min, v_max))
            if v_max == v_min:
                scaled_cols.append([0.0] * len(col))
            else:
                scaled_cols.append([(v - v_min) / (v_max - v_min) for v in col])
        return [list(row) for row in zip(*scaled_cols)], params

    def z_score_scale_2d(data):
        cols = list(zip(*data))
        scaled_cols = []
        params = []
        for col in cols:
            mean = sum(col) / len(col)
            std = (sum((v - mean) ** 2 for v in col) / len(col)) ** 0.5
            params.append((mean, std))
            if std == 0:
                scaled_cols.append([0.0] * len(col))
            else:
                scaled_cols.append([(v - mean) / std for v in col])
        return [list(row) for row in zip(*scaled_cols)], params

    print("  [원본 데이터]")
    print(f"    {'학생':>4} | {'키(cm)':>6} | {'용돈(만원)':>10}")
    print("    " + "-" * 30)
    for i, s in enumerate(students):
        print(f"    {i+1:>4} | {s[0]:>6} | {s[1]:>10}")
    print()

    # 스케일링 전 거리
    def euclidean(a, b):
        return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5

    p1, p2 = students[0], students[-1]  # 첫 번째와 마지막

    print(f"  학생1 {p1} vs 학생8 {p2} 거리 비교:")
    print()

    # 원본
    dist_raw = euclidean(p1, p2)
    ki_d = (p2[0] - p1[0])**2
    money_d = (p2[1] - p1[1])**2
    total_d = ki_d + money_d
    print(f"  [원본] 거리 = {dist_raw:.2f}")
    print(f"    키 기여: {ki_d} ({ki_d/total_d*100:.1f}%)")
    print(f"    용돈 기여: {money_d} ({money_d/total_d*100:.1f}%)")
    print()

    # Min-Max
    mm_data, _ = min_max_scale_2d(students)
    dist_mm = euclidean(mm_data[0], mm_data[-1])
    print(f"  [Min-Max] 거리 = {dist_mm:.4f}")
    print(f"    학생1: {[round(v, 3) for v in mm_data[0]]}")
    print(f"    학생8: {[round(v, 3) for v in mm_data[-1]]}")
    print()

    # Z-Score
    zs_data, _ = z_score_scale_2d(students)
    dist_zs = euclidean(zs_data[0], zs_data[-1])
    print(f"  [Z-Score] 거리 = {dist_zs:.4f}")
    print(f"    학생1: {[round(v, 3) for v in zs_data[0]]}")
    print(f"    학생8: {[round(v, 3) for v in zs_data[-1]]}")
    print()

    print("  → 스케일링 후 두 특성이 비슷한 영향력을 가진다!")
    print()


def lesson6_scaling_pitfalls():
    # =========================================================================
    #
    #   레슨 6 — 스케일링 주의사항
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 스케일링 주의사항          │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 핵심 규칙: 학습 데이터의 통계로만 스케일링한다!
    # ─────────────────────────────────────────────────────────────────────
    #
    #   잘못된 방법:
    #     전체 데이터로 평균/표준편차 계산 → 학습/테스트 나눔
    #     → 테스트 데이터의 정보가 학습에 누출! (Data Leakage)
    #
    #   올바른 방법:
    #     1. 학습/테스트 데이터 나눔
    #     2. 학습 데이터로만 평균/표준편차 계산 (fit)
    #     3. 학습 데이터에 적용 (transform)
    #     4. 같은 평균/표준편차로 테스트 데이터에 적용 (transform)
    #
    #   비유: 모의고사의 평균/표준편차로 수능 점수를 환산해야지,
    #         수능 결과를 미리 알고 환산하면 안 된다!
    #

    print("  [잘못된 방법 vs 올바른 방법]")
    print()
    print("    잘못됨:")
    print("    1. 전체 데이터로 평균 계산")
    print("    2. 전체 데이터 스케일링")
    print("    3. 학습/테스트 분리")
    print("    → 테스트 정보가 스케일링에 포함됨!")
    print()
    print("    올바름:")
    print("    1. 학습/테스트 분리")
    print("    2. 학습 데이터로만 평균/표준편차 계산 (fit)")
    print("    3. 학습 데이터 스케일링 (transform)")
    print("    4. 같은 통계로 테스트 데이터 스케일링 (transform)")
    print()

    # 코드로 시연
    train_data = [10, 20, 30, 40, 50]
    test_data  = [25, 55]  # 55는 학습 데이터 범위 밖

    # fit: 학습 데이터의 통계 계산
    train_mean = sum(train_data) / len(train_data)
    train_std = (sum((v - train_mean) ** 2 for v in train_data) / len(train_data)) ** 0.5

    print(f"  학습 데이터: {train_data}")
    print(f"  테스트 데이터: {test_data}")
    print(f"  학습 평균: {train_mean}, 학습 표준편차: {train_std:.2f}")
    print()

    # transform: 같은 통계로 두 데이터 모두 변환
    print("  [학습 데이터의 통계로 변환]")
    print(f"    학습 스케일링:")
    for v in train_data:
        scaled = (v - train_mean) / train_std
        print(f"      ({v} - {train_mean}) / {train_std:.2f} = {scaled:>+.4f}")

    print(f"    테스트 스케일링:")
    for v in test_data:
        scaled = (v - train_mean) / train_std
        print(f"      ({v} - {train_mean}) / {train_std:.2f} = {scaled:>+.4f}")
    print()

    # fit_transform 패턴
    print("  [fit_transform 패턴 (클래스 구현)]")
    print()

    class SimpleScaler:
        """간단한 Z-Score 스케일러"""
        def __init__(self):
            self.mean = None
            self.std = None

        def fit(self, data):
            """학습 데이터의 통계량 저장"""
            self.mean = sum(data) / len(data)
            self.std = (sum((v - self.mean)**2 for v in data) / len(data)) ** 0.5

        def transform(self, data):
            """저장된 통계량으로 변환"""
            return [(v - self.mean) / self.std for v in data]

        def fit_transform(self, data):
            """fit + transform 동시 실행"""
            self.fit(data)
            return self.transform(data)

    scaler = SimpleScaler()
    train_scaled = scaler.fit_transform(train_data)
    test_scaled = scaler.transform(test_data)  # fit 없이 transform만!

    print(f"    scaler.fit_transform(학습): {[round(v, 4) for v in train_scaled]}")
    print(f"    scaler.transform(테스트):   {[round(v, 4) for v in test_scaled]}")
    print()


def lesson7_one_hot_encoding():
    # =========================================================================
    #
    #   레슨 7 — 원-핫 인코딩 (One-Hot Encoding)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 원-핫 인코딩              │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 범주형 변수를 숫자로 바꾸는 방법
    # ─────────────────────────────────────────────────────────────────────
    #
    #   컴퓨터는 "서울", "부산", "제주" 같은 문자를 직접 계산 못한다
    #   → 숫자로 바꿔야 한다!
    #
    #   방법 1: 라벨 인코딩 (0, 1, 2...)
    #     서울=0, 부산=1, 제주=2
    #     문제: 모델이 "제주(2) > 부산(1) > 서울(0)"이라고 오해!
    #           실제로는 순서가 없는데!
    #
    #   방법 2: 원-핫 인코딩
    #     서울 = [1, 0, 0]
    #     부산 = [0, 1, 0]
    #     제주 = [0, 0, 1]
    #     → 순서/크기 관계 없이 독립적으로 표현!
    #

    # 라벨 인코딩의 문제점
    print("  [라벨 인코딩의 문제]")
    cities = ["서울", "부산", "제주", "대전"]
    label_encoded = {city: i for i, city in enumerate(cities)}
    print(f"    {label_encoded}")
    print(f"    → 모델이 '제주(2) - 서울(0) = 2'처럼 계산할 수 있다!")
    print(f"    → 도시 간에 수학적 관계가 없는데 생겨버림!")
    print()

    # 원-핫 인코딩
    def one_hot_encode(categories, value):
        """범주를 원-핫 벡터로 변환"""
        vector = [0] * len(categories)
        if value in categories:
            vector[categories.index(value)] = 1
        return vector

    print("  [원-핫 인코딩]")
    for city in cities:
        encoded = one_hot_encode(cities, city)
        print(f"    {city:>2} → {encoded}")
    print()

    # 실제 데이터에 적용
    print("  [실제 데이터 변환 예시]")
    students = [
        {"이름": "철수", "도시": "서울", "점수": 85},
        {"이름": "영희", "도시": "부산", "점수": 92},
        {"이름": "민수", "도시": "제주", "점수": 78},
        {"이름": "수진", "도시": "서울", "점수": 90},
    ]

    print(f"    {'이름':>4} | {'도시':>4} | {'점수':>4} | 원-핫 인코딩")
    print("    " + "-" * 45)
    for s in students:
        encoded = one_hot_encode(cities, s["도시"])
        print(f"    {s['이름']:>4} | {s['도시']:>4} | {s['점수']:>4} | {encoded}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 더미 변수 트랩 (Dummy Variable Trap)
    # ─────────────────────────────────────────────────────────────────────
    print("  [더미 변수 트랩]")
    print()
    print("    도시가 3개면 원-핫 벡터도 3개 컬럼:")
    print("    [서울, 부산, 제주]")
    print()
    print("    하지만! 서울=0, 부산=0이면 자동으로 제주=1")
    print("    → 3번째 컬럼은 불필요 (다중공선성)")
    print("    → 해결: 하나를 빼고 2개만 사용")
    print()
    print("    서울 = [1, 0]")
    print("    부산 = [0, 1]")
    print("    제주 = [0, 0]  ← 기준(reference)")
    print()


def lesson8_practice():
    # =========================================================================
    #
    #   레슨 8 — 실전: 학생 데이터 전처리 파이프라인
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 8 : 전처리 파이프라인          │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 전체 전처리 과정을 처음부터 끝까지 실행
    # ─────────────────────────────────────────────────────────────────────

    # 원본 데이터
    raw_data = [
        {"이름": "김철수", "키": 175, "몸무게": 70, "공부시간": 5, "도시": "서울", "합격": 1},
        {"이름": "이영희", "키": 162, "몸무게": 52, "공부시간": 8, "도시": "부산", "합격": 1},
        {"이름": "박민수", "키": 180, "몸무게": 85, "공부시간": 2, "도시": "서울", "합격": 0},
        {"이름": "최수진", "키": 158, "몸무게": 48, "공부시간": 7, "도시": "제주", "합격": 1},
        {"이름": "정대한", "키": 172, "몸무게": 68, "공부시간": 3, "도시": "부산", "합격": 0},
        {"이름": "한지윤", "키": 165, "몸무게": 55, "공부시간": 6, "도시": "서울", "합격": 1},
        {"이름": "송재현", "키": 185, "몸무게": 90, "공부시간": 1, "도시": "제주", "합격": 0},
        {"이름": "윤서연", "키": 160, "몸무게": 50, "공부시간": 9, "도시": "부산", "합격": 1},
    ]

    print("  [1단계] 원본 데이터 확인")
    print(f"    {'이름':>6} {'키':>4} {'몸무게':>4} {'공부':>4} {'도시':>4} {'합격':>4}")
    print("    " + "-" * 35)
    for d in raw_data:
        print(f"    {d['이름']:>6} {d['키']:>4} {d['몸무게']:>4} "
              f"{d['공부시간']:>4} {d['도시']:>4} {d['합격']:>4}")
    print()

    # 2단계: 학습/테스트 분리
    train_raw = raw_data[:6]
    test_raw = raw_data[6:]

    print(f"  [2단계] 데이터 분리: 학습 {len(train_raw)}개, 테스트 {len(test_raw)}개")
    print()

    # 3단계: 수치형 특성 스케일링 (학습 데이터 기준)
    numeric_features = ["키", "몸무게", "공부시간"]

    print("  [3단계] 수치형 특성 Z-Score 스케일링")
    print()

    scalers = {}
    for feat in numeric_features:
        train_values = [d[feat] for d in train_raw]
        mean = sum(train_values) / len(train_values)
        std = (sum((v - mean)**2 for v in train_values) / len(train_values)) ** 0.5
        scalers[feat] = (mean, std)
        print(f"    {feat}: 평균={mean:.2f}, 표준편차={std:.2f}")
    print()

    # 학습 데이터 스케일링
    def scale_record(record, scalers):
        scaled = {}
        for feat, (mean, std) in scalers.items():
            scaled[feat] = (record[feat] - mean) / std if std > 0 else 0
        return scaled

    # 4단계: 범주형 특성 원-핫 인코딩
    cities = ["서울", "부산", "제주"]

    print("  [4단계] 범주형 특성 원-핫 인코딩")
    print(f"    도시 카테고리: {cities}")
    print()

    # 5단계: 최종 변환 결과
    print("  [5단계] 최종 변환 결과")
    print(f"    {'이름':>6} | {'키z':>6} {'몸무게z':>7} {'공부z':>6} | {'서울':>4} {'부산':>4} {'제주':>4} | {'y':>2}")
    print("    " + "-" * 60)

    for d in train_raw:
        sc = scale_record(d, scalers)
        city_oh = [1 if c == d["도시"] else 0 for c in cities]
        print(f"    {d['이름']:>6} | {sc['키']:>+6.2f} {sc['몸무게']:>+7.2f} {sc['공부시간']:>+6.2f} "
              f"| {city_oh[0]:>4} {city_oh[1]:>4} {city_oh[2]:>4} | {d['합격']:>2}")

    print("    " + "-" * 60)
    print("    [테스트]")
    for d in test_raw:
        sc = scale_record(d, scalers)
        city_oh = [1 if c == d["도시"] else 0 for c in cities]
        print(f"    {d['이름']:>6} | {sc['키']:>+6.2f} {sc['몸무게']:>+7.2f} {sc['공부시간']:>+6.2f} "
              f"| {city_oh[0]:>4} {city_oh[1]:>4} {city_oh[2]:>4} | {d['합격']:>2}")
    print()

    print("  [전처리 파이프라인 정리]")
    print("    1. 데이터 분리 (학습/테스트)")
    print("    2. 학습 데이터로 통계 계산 (fit)")
    print("    3. 수치형: Z-Score 스케일링 (transform)")
    print("    4. 범주형: 원-핫 인코딩")
    print("    5. 같은 통계로 테스트 데이터도 변환")
    print("    → 이제 모델에 넣을 준비 완료!")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# ■ 메인 실행
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 72)
    print("  [ML 기초] 04단계: 특성 스케일링 (Feature Scaling)")
    print("=" * 72)
    print()

    lesson1_why_scaling()
    lesson2_min_max()
    lesson3_z_score()
    lesson4_robust_scaling()
    lesson5_scaling_comparison()
    lesson6_scaling_pitfalls()
    lesson7_one_hot_encoding()
    lesson8_practice()

    print("=" * 72)
    print("  04단계 완료!")
    print("=" * 72)


if __name__ == "__main__":
    main()
