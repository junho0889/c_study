# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [ML 기초] 학습 02단계: 데이터 분할 (Train/Test Split)
#   ─ 과적합, 셔플링, 검증 세트, 시드, 계층화, 시계열, K-Fold ─
#   ■ 실행 방법: python 02_train_test_split.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import random


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 왜 데이터를 나누는가? - 시험 전에 답지 보기 비유, 과적합
#   2. 훈련 세트 vs 테스트 세트 - 비율, 셔플링
#   3. 검증 세트 - 왜 3개로 나누는지, 하이퍼파라미터 튜닝
#   4. 랜덤 시드(seed) - 재현성, random.seed() 중요성
#   5. 계층화 분할(Stratified) - 클래스 불균형 시 비율 유지
#   6. 시계열 분할 - 시간 순서 유지, 미래 데이터 누출 방지
#   7. K-Fold 교차검증 - 모든 데이터를 훈련/테스트로 활용
#   8. 실전: 다양한 분할 방법 비교 실험
#
# ─────────────────────────────────────────────────────────────────────────


def lesson1_why_split():
    # =========================================================================
    #
    #   레슨 1 — 왜 데이터를 나누는가?
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 왜 데이터를 나누는가?      │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 비유: 시험 전에 답지를 보고 시험을 치르면?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   학생이 시험 문제를 미리 보고 외우면 → 100점!
    #   하지만 새로운 문제를 만나면? → 못 푼다!
    #
    #   ML에서도 똑같다:
    #     학습 데이터를 외워버리면(과적합, overfitting)
    #     새 데이터에서 성능이 떨어진다
    #
    #   해결: 데이터를 나눠서 "안 본 데이터"로 평가한다
    #

    print("  [과적합 비유]")
    print()
    print("  학생A: 기출문제만 달달 외움 → 같은 문제 100점, 새 문제 30점")
    print("  학생B: 개념을 이해함        → 같은 문제 90점,  새 문제 85점")
    print()
    print("  학생A = 과적합된 모델  (훈련 데이터에서만 잘함)")
    print("  학생B = 잘 학습된 모델 (새 데이터에서도 잘함)")
    print()

    # 과적합 예시를 코드로 보여주기
    # 데이터: 공부시간 → 점수
    train_data = [(1, 45), (2, 55), (3, 60), (4, 70), (5, 75)]
    test_data  = [(6, 82), (7, 88), (8, 92)]

    # 모델 1: 단순 직선 (일반화 잘 됨)
    w1, b1 = 7.5, 38.0  # 대략적 직선

    # 각 데이터에 대해 예측
    print("  [모델이 훈련 데이터를 외운 경우 vs 일반화한 경우]")
    print()
    print("  훈련 데이터 평가:")
    train_error = 0
    for x, y in train_data:
        pred = w1 * x + b1
        err = abs(y - pred)
        train_error += err
        print(f"    x={x}, 실제={y}, 예측={pred:.1f}, 오차={err:.1f}")
    print(f"    평균 오차: {train_error / len(train_data):.2f}")
    print()

    print("  테스트 데이터 평가 (처음 보는 데이터):")
    test_error = 0
    for x, y in test_data:
        pred = w1 * x + b1
        err = abs(y - pred)
        test_error += err
        print(f"    x={x}, 실제={y}, 예측={pred:.1f}, 오차={err:.1f}")
    print(f"    평균 오차: {test_error / len(test_data):.2f}")
    print()
    print("  → 테스트 데이터의 오차가 훈련 데이터와 비슷하면 좋은 모델!")
    print()


def lesson2_train_test():
    # =========================================================================
    #
    #   레슨 2 — 훈련 세트 vs 테스트 세트
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : 훈련/테스트 세트           │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 분할 비율: 보통 70:30 또는 80:20
    # ─────────────────────────────────────────────────────────────────────
    #
    #   데이터 100개라면:
    #     80:20 → 학습 80개, 테스트 20개
    #     70:30 → 학습 70개, 테스트 30개
    #
    #   데이터가 많으면 (10만개+): 90:10도 OK
    #   데이터가 적으면 (100개 이하): 교차검증 추천
    #

    # 직접 구현: train_test_split
    def my_train_test_split(data, test_ratio=0.2, seed=42):
        """데이터를 셔플 후 비율에 따라 나누기"""
        shuffled = data[:]
        random.Random(seed).shuffle(shuffled)
        split_idx = int(len(shuffled) * (1 - test_ratio))
        return shuffled[:split_idx], shuffled[split_idx:]

    # 예제 데이터: 학생 10명의 정보
    students = [
        {"id": 1,  "hours": 2, "score": 50},
        {"id": 2,  "hours": 3, "score": 55},
        {"id": 3,  "hours": 5, "score": 72},
        {"id": 4,  "hours": 1, "score": 40},
        {"id": 5,  "hours": 7, "score": 85},
        {"id": 6,  "hours": 4, "score": 65},
        {"id": 7,  "hours": 6, "score": 78},
        {"id": 8,  "hours": 8, "score": 92},
        {"id": 9,  "hours": 3, "score": 58},
        {"id": 10, "hours": 5, "score": 70},
    ]

    print(f"  전체 데이터: {len(students)}개")
    print()

    # 다양한 비율로 분할
    for ratio in [0.2, 0.3, 0.4]:
        train, test = my_train_test_split(students, test_ratio=ratio)
        train_ids = [s["id"] for s in train]
        test_ids = [s["id"] for s in test]
        print(f"  비율 {int((1-ratio)*100)}:{int(ratio*100)} → "
              f"학습 {len(train)}개 {train_ids} / 테스트 {len(test)}개 {test_ids}")

    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 셔플링이 중요한 이유
    # ─────────────────────────────────────────────────────────────────────
    print("  [셔플링이 없으면 생기는 문제]")
    print()

    # 데이터가 정렬되어 있다면
    sorted_labels = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    print(f"    원본 데이터 라벨: {sorted_labels}")
    print(f"    셔플 없이 80:20 분할:")
    print(f"      학습: {sorted_labels[:8]} → 0이 5개, 1이 3개")
    print(f"      테스트: {sorted_labels[8:]} → 1만 2개!")
    print(f"    → 테스트에 한 클래스만 있어서 편향된 평가!")
    print()

    # 셔플 후
    shuffled_labels = sorted_labels[:]
    random.Random(42).shuffle(shuffled_labels)
    print(f"    셔플 후 데이터: {shuffled_labels}")
    print(f"    셔플 후 80:20 분할:")
    print(f"      학습: {shuffled_labels[:8]}")
    print(f"      테스트: {shuffled_labels[8:]}")
    print(f"    → 클래스가 골고루 섞여서 공정한 평가!")
    print()


def lesson3_validation_set():
    # =========================================================================
    #
    #   레슨 3 — 검증 세트 (Validation Set)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : 검증 세트                  │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 왜 3개로 나누는가?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유: 시험 준비
    #     교과서로 공부  → 훈련 세트 (Training Set)
    #     모의고사 풀기  → 검증 세트 (Validation Set)
    #     수능 시험      → 테스트 세트 (Test Set)
    #
    #   검증 세트는 "모의고사"처럼 학습 중에 성능을 확인하는 데 사용
    #   테스트 세트는 "수능"처럼 최종 평가에만 사용
    #
    #   하이퍼파라미터 튜닝:
    #     학습률, 에폭 수, 모델 복잡도 등을 검증 세트로 조절
    #     테스트 세트로 조절하면 → 테스트 세트에 과적합!
    #

    data = list(range(1, 101))  # 100개 데이터
    random.Random(42).shuffle(data)

    # 60:20:20 분할
    train = data[:60]
    val   = data[60:80]
    test  = data[80:]

    print("  [3-way 분할: 60:20:20]")
    print(f"    전체 데이터: {len(data)}개")
    print(f"    훈련 세트:  {len(train)}개 → 모델 학습용")
    print(f"    검증 세트:  {len(val)}개 → 하이퍼파라미터 조절용")
    print(f"    테스트 세트: {len(test)}개 → 최종 평가용 (한 번만!)")
    print()

    # 하이퍼파라미터 튜닝 시뮬레이션
    print("  [하이퍼파라미터 튜닝 시뮬레이션]")
    print()
    print("    학습률   | 훈련 MSE | 검증 MSE | 선택?")
    print("    " + "-" * 45)

    # 시뮬레이션 결과 (실제로는 학습을 반복)
    results = [
        (0.001, 15.2, 16.8, ""),
        (0.010, 5.1,  6.3,  ""),
        (0.050, 2.3,  3.1,  " ← 최적"),
        (0.100, 1.8,  8.5,  " ← 과적합!"),
        (0.500, 25.0, 30.2, " ← 발산!"),
    ]

    for lr, train_mse, val_mse, note in results:
        print(f"    {lr:.3f}  | {train_mse:>8.1f} | {val_mse:>8.1f} |{note}")
    print()
    print("  → 검증 MSE가 가장 낮은 학습률 0.050을 선택!")
    print("  → 그 후 테스트 세트로 최종 성능만 확인")
    print()


def lesson4_random_seed():
    # =========================================================================
    #
    #   레슨 4 — 랜덤 시드의 중요성
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : 랜덤 시드 (Seed)           │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 시드를 고정하면 → 항상 같은 결과 → 재현성 보장
    # ─────────────────────────────────────────────────────────────────────
    #
    #   실험을 반복할 때 매번 다른 결과가 나오면 비교가 불가능!
    #   seed를 고정하면 "같은 랜덤 순서"를 보장한다
    #
    #   비유: 주사위를 던지는데, "마법 주사위"는 특정 번호를 넣으면
    #         항상 같은 순서로 나온다. 그 번호가 seed!
    #

    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # 시드 없이 (매번 다름)
    print("  [시드 없이 셔플 - 매번 다른 결과]")
    for trial in range(3):
        shuffled = data[:]
        random.shuffle(shuffled)
        print(f"    시도 {trial + 1}: {shuffled}")
    print()

    # 시드 고정 (항상 같음)
    print("  [시드=42로 고정 - 항상 같은 결과]")
    for trial in range(3):
        shuffled = data[:]
        random.Random(42).shuffle(shuffled)
        print(f"    시도 {trial + 1}: {shuffled}")
    print()

    # 시드 값에 따른 분할 결과 비교
    print("  [시드 값에 따른 분할 결과]")
    for seed in [0, 42, 123, 999]:
        shuffled = data[:]
        random.Random(seed).shuffle(shuffled)
        train = shuffled[:8]
        test = shuffled[8:]
        print(f"    seed={seed:>3} → 학습: {train}, 테스트: {test}")
    print()
    print("  → 논문이나 보고서에 seed 값을 기록해야 재현 가능!")
    print()


def lesson5_stratified_split():
    # =========================================================================
    #
    #   레슨 5 — 계층화 분할 (Stratified Split)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 계층화 분할                │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 클래스 불균형 데이터에서의 문제
    # ─────────────────────────────────────────────────────────────────────
    #
    #   전체 데이터: 양성 10개, 음성 90개 (1:9 비율)
    #   무작위 분할하면:
    #     테스트 세트에 양성이 0개일 수도 있다!
    #     → 공정한 평가가 불가능
    #
    #   계층화 분할: 원래 비율을 유지하면서 나눈다
    #     전체 비율 1:9 → 학습 세트도 1:9, 테스트 세트도 1:9
    #

    # 불균형 데이터 생성
    labels = [1] * 10 + [0] * 90  # 양성 10%, 음성 90%

    print(f"  전체 데이터: {len(labels)}개")
    print(f"  양성(1): {labels.count(1)}개 ({labels.count(1)/len(labels)*100:.0f}%)")
    print(f"  음성(0): {labels.count(0)}개 ({labels.count(0)/len(labels)*100:.0f}%)")
    print()

    # 일반 분할 (여러 번 시도)
    print("  [일반 분할 - 비율이 들쭉날쭉]")
    for seed in [1, 7, 13, 42]:
        shuffled = labels[:]
        random.Random(seed).shuffle(shuffled)
        test_set = shuffled[80:]
        pos_count = test_set.count(1)
        print(f"    seed={seed:>2} → 테스트 양성 비율: {pos_count}/{len(test_set)} "
              f"= {pos_count/len(test_set)*100:.0f}%")
    print()

    # 계층화 분할 직접 구현
    def stratified_split(features, labels, test_ratio=0.2, seed=42):
        """각 클래스의 비율을 유지하면서 분할"""
        # 클래스별로 인덱스 분리
        class_indices = {}
        for i, label in enumerate(labels):
            if label not in class_indices:
                class_indices[label] = []
            class_indices[label].append(i)

        train_indices = []
        test_indices = []

        rng = random.Random(seed)

        for cls, indices in class_indices.items():
            shuffled_idx = indices[:]
            rng.shuffle(shuffled_idx)
            split = int(len(shuffled_idx) * (1 - test_ratio))
            train_indices.extend(shuffled_idx[:split])
            test_indices.extend(shuffled_idx[split:])

        return train_indices, test_indices

    # 계층화 분할 실행
    features = list(range(len(labels)))
    train_idx, test_idx = stratified_split(features, labels, test_ratio=0.2, seed=42)

    test_labels = [labels[i] for i in test_idx]
    train_labels = [labels[i] for i in train_idx]

    print("  [계층화 분할 - 비율 유지!]")
    print(f"    학습 세트: {len(train_idx)}개, "
          f"양성 {train_labels.count(1)}개 "
          f"({train_labels.count(1)/len(train_labels)*100:.0f}%)")
    print(f"    테스트 세트: {len(test_idx)}개, "
          f"양성 {test_labels.count(1)}개 "
          f"({test_labels.count(1)/len(test_labels)*100:.0f}%)")
    print()
    print("  → 원래 비율 10%가 학습/테스트 모두에서 유지됨!")
    print()


def lesson6_time_series_split():
    # =========================================================================
    #
    #   레슨 6 — 시계열 분할
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 시계열 분할                │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 시계열 데이터는 셔플하면 안 된다!
    # ─────────────────────────────────────────────────────────────────────
    #
    #   주식 가격, 매출 데이터 등은 "시간 순서"가 중요
    #
    #   잘못된 방법:
    #     [1월, 3월, 5월, 7월, 9월, 11월] → 학습
    #     [2월, 4월, 6월, 8월, 10월, 12월] → 테스트
    #     → 미래 데이터(3월)로 학습해서 과거(2월)를 예측? 부정행위!
    #
    #   올바른 방법:
    #     [1월~8월] → 학습
    #     [9월~12월] → 테스트
    #     → 과거로 학습, 미래를 예측
    #

    # 월별 매출 데이터 (만원)
    months = ["1월", "2월", "3월", "4월", "5월", "6월",
              "7월", "8월", "9월", "10월", "11월", "12월"]
    sales  = [100, 120, 130, 150, 160, 180, 200, 210, 220, 250, 260, 280]

    print("  [월별 매출 데이터]")
    for i in range(len(months)):
        bar = "#" * (sales[i] // 10)
        print(f"    {months[i]:>4}: {sales[i]:>3}만원 {bar}")
    print()

    # 잘못된 분할 (셔플)
    print("  [잘못된 분할 - 셔플 후 나눔]")
    shuffled_months = list(range(12))
    random.Random(42).shuffle(shuffled_months)
    train_m = [months[i] for i in shuffled_months[:8]]
    test_m  = [months[i] for i in shuffled_months[8:]]
    print(f"    학습: {train_m}")
    print(f"    테스트: {test_m}")
    print("    → 10월 데이터로 학습해서 3월을 예측? 미래 누출!")
    print()

    # 올바른 분할 (시간 순서 유지)
    print("  [올바른 분할 - 시간 순서 유지]")
    split_point = 8  # 앞 8개: 학습, 뒤 4개: 테스트
    train_months = months[:split_point]
    test_months  = months[split_point:]
    train_sales  = sales[:split_point]
    test_sales   = sales[split_point:]

    print(f"    학습: {train_months} → 과거")
    print(f"    테스트: {test_months} → 미래")
    print("    → 과거(1~8월)로 학습, 미래(9~12월)를 예측!")
    print()

    # 확장 윈도우(Expanding Window) 방식
    print("  [확장 윈도우 방식]")
    print("    1차: 학습[1~4월] → 테스트[5월]")
    print("    2차: 학습[1~5월] → 테스트[6월]")
    print("    3차: 학습[1~6월] → 테스트[7월]")
    print("    → 학습 데이터가 점점 늘어남")
    print()


def lesson7_k_fold():
    # =========================================================================
    #
    #   레슨 7 — K-Fold 교차검증
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : K-Fold 교차검증            │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ K-Fold: 데이터를 K개 조각으로 나눠서 돌아가며 테스트
    # ─────────────────────────────────────────────────────────────────────
    #
    #   데이터가 적을 때 특히 유용!
    #   모든 데이터가 한 번씩은 테스트 세트가 된다
    #
    #   5-Fold 예시 (데이터 10개, K=5):
    #     Fold 1: 테스트 [1,2]  학습 [3,4,5,6,7,8,9,10]
    #     Fold 2: 테스트 [3,4]  학습 [1,2,5,6,7,8,9,10]
    #     Fold 3: 테스트 [5,6]  학습 [1,2,3,4,7,8,9,10]
    #     Fold 4: 테스트 [7,8]  학습 [1,2,3,4,5,6,9,10]
    #     Fold 5: 테스트 [9,10] 학습 [1,2,3,4,5,6,7,8]
    #
    #   최종 성능 = 5번의 성능 평균
    #

    def k_fold_split(data, k=5):
        """데이터를 K개 폴드로 나누기"""
        fold_size = len(data) // k
        folds = []
        for i in range(k):
            start = i * fold_size
            end = start + fold_size if i < k - 1 else len(data)
            test_fold = data[start:end]
            train_fold = data[:start] + data[end:]
            folds.append((train_fold, test_fold))
        return folds

    # 예제 데이터
    data = list(range(1, 21))  # 20개 데이터
    k = 5

    print(f"  데이터: {data}")
    print(f"  K = {k}")
    print()

    folds = k_fold_split(data, k=k)

    print("  [각 Fold의 분할]")
    for i, (train, test) in enumerate(folds):
        # 시각적으로 어떤 부분이 테스트인지 보여주기
        visual = ""
        for d in data:
            if d in test:
                visual += "[T]"
            else:
                visual += " . "
        print(f"    Fold {i+1}: {visual}")
        print(f"           학습 {len(train)}개, 테스트 {len(test)}개")
    print()

    # 간단한 모델로 K-Fold 적용 시뮬레이션
    # 데이터: x → y = 3x + 5 + 약간의 노이즈
    random.seed(42)
    x_all = list(range(1, 21))
    y_all = [3 * x + 5 + random.randint(-3, 3) for x in x_all]

    print("  [K-Fold 교차검증 실행]")
    print()

    fold_scores = []
    indices = list(range(len(x_all)))

    for fold_idx in range(k):
        fold_size = len(indices) // k
        start = fold_idx * fold_size
        end = start + fold_size if fold_idx < k - 1 else len(indices)

        test_idx = indices[start:end]
        train_idx = indices[:start] + indices[end:]

        # 학습 데이터로 OLS
        train_x = [x_all[i] for i in train_idx]
        train_y = [y_all[i] for i in train_idx]
        n = len(train_x)
        x_mean = sum(train_x) / n
        y_mean = sum(train_y) / n

        num = sum((train_x[i] - x_mean) * (train_y[i] - y_mean) for i in range(n))
        den = sum((train_x[i] - x_mean) ** 2 for i in range(n))

        w = num / den if den != 0 else 0
        b = y_mean - w * x_mean

        # 테스트 데이터로 평가
        test_x = [x_all[i] for i in test_idx]
        test_y = [y_all[i] for i in test_idx]
        mse = sum((test_y[j] - (w * test_x[j] + b)) ** 2 for j in range(len(test_x))) / len(test_x)
        fold_scores.append(mse)

        print(f"    Fold {fold_idx+1}: w={w:.2f}, b={b:.2f}, MSE={mse:.2f}")

    avg_mse = sum(fold_scores) / len(fold_scores)
    print()
    print(f"  평균 MSE: {avg_mse:.2f}")
    print(f"  MSE 표준편차: {(sum((s - avg_mse)**2 for s in fold_scores) / len(fold_scores))**0.5:.2f}")
    print()
    print("  → 하나의 분할이 아닌 K번 평가로 더 신뢰할 수 있는 성능 측정!")
    print()


def lesson8_practice():
    # =========================================================================
    #
    #   레슨 8 — 실전: 분할 방법 비교 실험
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 8 : 실전 비교 실험             │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 같은 데이터에 대해 다양한 분할 방법 비교
    # ─────────────────────────────────────────────────────────────────────

    # 데이터 생성: y = 2x + 10 + noise
    random.seed(42)
    n_samples = 30
    x_data = [i for i in range(1, n_samples + 1)]
    y_data = [2 * x + 10 + random.uniform(-5, 5) for x in x_data]

    print(f"  데이터: {n_samples}개 생성 (y = 2x + 10 + 노이즈)")
    print()

    def evaluate_split(train_x, train_y, test_x, test_y):
        """OLS로 학습하고 테스트 MSE 반환"""
        n = len(train_x)
        if n == 0:
            return float('inf')
        x_mean = sum(train_x) / n
        y_mean = sum(train_y) / n
        num = sum((train_x[i] - x_mean) * (train_y[i] - y_mean) for i in range(n))
        den = sum((train_x[i] - x_mean) ** 2 for i in range(n))
        w = num / den if den != 0 else 0
        b = y_mean - w * x_mean
        mse = sum((test_y[j] - (w * test_x[j] + b)) ** 2
                   for j in range(len(test_x))) / len(test_x)
        return mse

    # 방법 1: 순서대로 80:20
    split = int(n_samples * 0.8)
    mse1 = evaluate_split(x_data[:split], y_data[:split],
                          x_data[split:], y_data[split:])

    # 방법 2: 셔플 후 80:20 (여러 시드)
    mse2_list = []
    for seed in range(10):
        indices = list(range(n_samples))
        random.Random(seed).shuffle(indices)
        tr_x = [x_data[i] for i in indices[:split]]
        tr_y = [y_data[i] for i in indices[:split]]
        te_x = [x_data[i] for i in indices[split:]]
        te_y = [y_data[i] for i in indices[split:]]
        mse2_list.append(evaluate_split(tr_x, tr_y, te_x, te_y))
    mse2_avg = sum(mse2_list) / len(mse2_list)

    # 방법 3: 5-Fold 교차검증
    k = 5
    fold_mses = []
    fold_size = n_samples // k
    for i in range(k):
        start = i * fold_size
        end = start + fold_size if i < k - 1 else n_samples
        te_x = x_data[start:end]
        te_y = y_data[start:end]
        tr_x = x_data[:start] + x_data[end:]
        tr_y = y_data[:start] + y_data[end:]
        fold_mses.append(evaluate_split(tr_x, tr_y, te_x, te_y))
    mse3_avg = sum(fold_mses) / len(fold_mses)

    print("  ┌─────────────────────────────────┬──────────┐")
    print("  │ 분할 방법                       │ MSE      │")
    print("  ├─────────────────────────────────┼──────────┤")
    print(f"  │ 순서대로 80:20                  │ {mse1:>8.2f} │")
    print(f"  │ 셔플 80:20 (10회 평균)         │ {mse2_avg:>8.2f} │")
    print(f"  │ 5-Fold 교차검증                │ {mse3_avg:>8.2f} │")
    print("  └─────────────────────────────────┴──────────┘")
    print()

    # 각 Fold별 결과 시각화
    print("  [5-Fold 각 Fold별 MSE]")
    for i, mse in enumerate(fold_mses):
        bar = "#" * int(mse)
        print(f"    Fold {i+1}: MSE={mse:>6.2f} {bar}")
    print()

    print("  [결론]")
    print("    1. 데이터가 충분하면 → 셔플 + 80:20 분할이 간편")
    print("    2. 데이터가 적으면   → K-Fold 교차검증 추천")
    print("    3. 시계열 데이터면   → 시간 순서 유지 분할 필수")
    print("    4. 클래스 불균형이면 → 계층화 분할 사용")
    print("    5. 항상 seed를 기록하여 재현성 확보!")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# ■ 메인 실행
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 72)
    print("  [ML 기초] 02단계: 데이터 분할 (Train/Test Split)")
    print("=" * 72)
    print()

    lesson1_why_split()
    lesson2_train_test()
    lesson3_validation_set()
    lesson4_random_seed()
    lesson5_stratified_split()
    lesson6_time_series_split()
    lesson7_k_fold()
    lesson8_practice()

    print("=" * 72)
    print("  02단계 완료! 다음: 03_classification_basics.py")
    print("=" * 72)


if __name__ == "__main__":
    main()
