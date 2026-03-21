# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [ML 기초] 학습 03단계: 분류 기초 (Classification Basics)
#   ─ 이진/다중 분류, 결정 경계, 로지스틱 회귀, KNN, 정밀도/재현율 ─
#   ■ 실행 방법: python 03_classification_basics.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import random


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 분류란? - 이진 분류 vs 다중 클래스, 실생활 예시
#   2. 결정 경계 - 임계값, 선형/비선형 경계 개념
#   3. 로지스틱 회귀 개념 - 시그모이드, 확률 출력, 임계값 조절
#   4. KNN 분류기 구현 - 거리 계산, 다수결 투표, k값 실험
#   5. 정밀도 vs 재현율 - 스팸 필터 비유, 트레이드오프
#   6. 혼동 행렬 시각화 - TP/FP/FN/TN, ASCII 행렬 출력
#   7. 다중 클래스 전략 - One-vs-Rest, One-vs-One
#   8. 실전: 과일 분류기 만들기
#
# ─────────────────────────────────────────────────────────────────────────


def lesson1_what_is_classification():
    # =========================================================================
    #
    #   레슨 1 — 분류란?
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 분류란?                    │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 분류 = "어떤 범주에 속하는지" 예측하는 문제
    # ─────────────────────────────────────────────────────────────────────
    #
    #   회귀: "82점" 같은 연속적인 숫자 예측
    #   분류: "합격/불합격" 같은 범주(카테고리) 예측
    #
    #   이진 분류 (Binary): 2개 중 하나
    #     - 스팸 / 정상 이메일
    #     - 합격 / 불합격
    #     - 양성 / 음성 (질병 검사)
    #
    #   다중 클래스 분류 (Multi-class): 3개 이상 중 하나
    #     - 개 / 고양이 / 새
    #     - A / B / C / D / F 학점
    #     - 사과 / 바나나 / 포도 / 오렌지
    #

    print("  [분류 vs 회귀]")
    print()
    print("    회귀:  입력 → 숫자 (82점, 3200만원)")
    print("    분류:  입력 → 범주 (합격, 강아지, A학점)")
    print()

    # 이진 분류 예시
    print("  [이진 분류 예시: 시험 합격 예측]")
    students = [
        (2, "불합격"), (3, "불합격"), (4, "불합격"),
        (5, "합격"),   (6, "합격"),   (8, "합격"),
    ]
    for hours, result in students:
        emoji = "O" if result == "합격" else "X"
        print(f"    공부 {hours}시간 → {result} [{emoji}]")
    print()

    # 다중 클래스 예시
    print("  [다중 클래스 예시: 학점 분류]")
    grades = [
        (95, "A"), (85, "B"), (75, "C"), (65, "D"), (50, "F"),
    ]
    for score, grade in grades:
        print(f"    {score}점 → {grade}학점")
    print()


def lesson2_decision_boundary():
    # =========================================================================
    #
    #   레슨 2 — 결정 경계 (Decision Boundary)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : 결정 경계                  │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 결정 경계 = "여기부터는 A, 여기부터는 B"를 가르는 선
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유: 키 160cm 이상이면 놀이기구 탑승 가능
    #         → 160cm가 "결정 경계"
    #
    #   1차원: 숫자 하나로 판단 → 임계값(threshold) 하나
    #   2차원: 점 2개로 판단  → 직선 하나
    #   비선형: 곡선, 원 등 복잡한 모양
    #

    # 1차원 결정 경계 시각화
    print("  [1차원 결정 경계 - 임계값 4시간]")
    print()
    print("    불합격    |    합격")
    print("    X  X  X   |   O  O  O")
    print("    1  2  3   4   5  6  7  (공부 시간)")
    print("              ↑")
    print("          결정 경계")
    print()

    # 다양한 임계값 실험
    data = [(1, 0), (2, 0), (3, 0), (4, 0), (5, 1), (6, 1), (7, 1), (8, 1)]

    print("  [임계값에 따른 정확도 변화]")
    print()

    for threshold in [3, 4, 5, 6]:
        correct = 0
        for hours, label in data:
            pred = 1 if hours >= threshold else 0
            if pred == label:
                correct += 1
        accuracy = correct / len(data) * 100
        print(f"    임계값={threshold}: 정확도 {correct}/{len(data)} = {accuracy:.0f}%")

    print()

    # 2차원 결정 경계 (ASCII)
    print("  [2차원 결정 경계 - 공부시간 & 출석률]")
    print()
    print("    출석률")
    print("    100 |  X  .  .  O  O")
    print("     80 |  X  X  .  O  O")
    print("     60 |  X  X  .  .  O")
    print("     40 |  X  X  X  .  .")
    print("     20 |  X  X  X  X  .")
    print("        +─────────────────")
    print("          1  2  3  4  5  (시간)")
    print()
    print("  → '.'은 경계 근처, 직선으로 X와 O를 나눌 수 있다!")
    print()


def lesson3_logistic_regression():
    # =========================================================================
    #
    #   레슨 3 — 로지스틱 회귀 (Logistic Regression)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : 로지스틱 회귀              │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 시그모이드 함수: 아무 숫자 → 0~1 사이 확률로 변환
    # ─────────────────────────────────────────────────────────────────────
    #
    #   sigmoid(z) = 1 / (1 + e^(-z))
    #
    #   특징:
    #     z가 매우 크면 → sigmoid ≈ 1 (거의 확실히 양성)
    #     z가 0이면    → sigmoid = 0.5 (반반)
    #     z가 매우 작으면 → sigmoid ≈ 0 (거의 확실히 음성)
    #
    #   로지스틱 회귀:
    #     z = w*x + b  (선형 회귀와 같은 계산)
    #     확률 = sigmoid(z)
    #     확률 >= 0.5 → 양성(1), 확률 < 0.5 → 음성(0)
    #

    def sigmoid(z):
        # 오버플로우 방지
        z = max(-500, min(500, z))
        return 1.0 / (1.0 + math.exp(-z))

    # 시그모이드 그래프 (ASCII)
    print("  [시그모이드 함수 그래프]")
    print()
    print("  1.0 |                        ********")
    print("      |                   *****")
    print("  0.5 |- - - - - - - -*-  - - - - - - -")
    print("      |          *****")
    print("  0.0 | ********")
    print("      +────────────────────────────────")
    print("       -6  -4  -2   0   2   4   6  (z)")
    print()

    # 수치 예제
    print("  [시그모이드 수치 예제]")
    for z in [-5, -3, -1, 0, 1, 3, 5]:
        prob = sigmoid(z)
        bar = "#" * int(prob * 30)
        print(f"    z={z:>3} → sigmoid={prob:.4f} {bar}")
    print()

    # 로지스틱 회귀 적용 예시
    # 가중치 수동 설정: w=2, b=-8 → 공부 4시간이 경계
    w, b = 2.0, -8.0

    print(f"  [로지스틱 회귀 예시] w={w}, b={b}")
    print(f"    z = {w}*시간 + ({b}) → 확률 = sigmoid(z)")
    print()

    for hours in range(1, 9):
        z = w * hours + b
        prob = sigmoid(z)
        pred = "합격" if prob >= 0.5 else "불합격"
        bar = "#" * int(prob * 20)
        print(f"    {hours}시간: z={z:>5.1f}, 확률={prob:.4f} {bar} → {pred}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 임계값 조절
    # ─────────────────────────────────────────────────────────────────────
    print("  [임계값 조절의 효과]")
    print("    임계값 0.3: 쉽게 합격 판정 → 합격 많이, 실수도 많이")
    print("    임계값 0.5: 기본값")
    print("    임계값 0.7: 까다롭게 합격 판정 → 확실한 경우만 합격")
    print()

    for threshold in [0.3, 0.5, 0.7]:
        results = []
        for hours in range(1, 9):
            z = w * hours + b
            prob = sigmoid(z)
            results.append("O" if prob >= threshold else "X")
        print(f"    임계값={threshold}: {' '.join(results)}")
    print(f"               시간: {'  '.join(str(h) for h in range(1, 9))}")
    print()


def lesson4_knn():
    # =========================================================================
    #
    #   레슨 4 — KNN 분류기 구현 (K-Nearest Neighbors)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : KNN 분류기                 │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ KNN: "가장 가까운 K개의 이웃을 보고 다수결로 결정"
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유: 새 동네에 이사 왔는데 어느 학교에 다닐지 모른다
    #         → 가장 가까운 5집을 봤더니 3집이 A학교, 2집이 B학교
    #         → "A학교에 다니겠다!" (다수결)
    #
    #   거리 계산: 유클리드 거리
    #     d = sqrt((x1-x2)² + (y1-y2)²)
    #

    # 학습 데이터: [공부시간, 수면시간] → 합격(1) / 불합격(0)
    train_data = [
        ([1, 4], 0), ([2, 3], 0), ([2, 6], 0), ([3, 5], 0),
        ([5, 7], 1), ([6, 5], 1), ([6, 8], 1), ([7, 6], 1),
        ([8, 7], 1), ([4, 4], 0),
    ]

    def euclidean_distance(p1, p2):
        return sum((a - b) ** 2 for a, b in zip(p1, p2)) ** 0.5

    def knn_predict(train_data, query, k=3):
        """KNN 분류: query에 가장 가까운 k개의 이웃으로 예측"""
        distances = []
        for features, label in train_data:
            dist = euclidean_distance(features, query)
            distances.append((dist, label))

        # 거리 순 정렬
        distances.sort(key=lambda x: x[0])

        # k개 이웃의 다수결
        k_nearest = distances[:k]
        votes = {}
        for dist, label in k_nearest:
            votes[label] = votes.get(label, 0) + 1

        return max(votes, key=votes.get), k_nearest

    # KNN 예측 시연
    test_points = [[3, 6], [5, 5], [7, 4], [4, 7]]

    print("  [학습 데이터]")
    for features, label in train_data:
        tag = "합격" if label == 1 else "불합격"
        print(f"    공부={features[0]}h, 수면={features[1]}h → {tag}")
    print()

    print("  [KNN 예측 (k=3)]")
    for point in test_points:
        pred, neighbors = knn_predict(train_data, point, k=3)
        tag = "합격" if pred == 1 else "불합격"
        neighbor_info = ", ".join(f"d={d:.2f}→{'합' if l==1 else '불'}" for d, l in neighbors)
        print(f"    입력 {point} → 이웃: [{neighbor_info}] → 예측: {tag}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ k값에 따른 결과 변화
    # ─────────────────────────────────────────────────────────────────────
    print("  [k값에 따른 예측 변화]")
    query = [4, 6]
    print(f"    입력: {query}")
    for k in [1, 3, 5, 7]:
        pred, neighbors = knn_predict(train_data, query, k=k)
        tag = "합격" if pred == 1 else "불합격"
        labels = [l for _, l in neighbors]
        print(f"    k={k}: 이웃 라벨={labels} → {tag}")
    print()
    print("  → k가 작으면 노이즈에 민감, k가 크면 경계가 부드러움")
    print()


def lesson5_precision_recall():
    # =========================================================================
    #
    #   레슨 5 — 정밀도 vs 재현율
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 정밀도 vs 재현율           │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 정확도만으로는 부족한 경우가 있다!
    # ─────────────────────────────────────────────────────────────────────
    #
    #   예: 암 환자 1%, 정상 99%
    #   "모두 정상"이라고 예측하면 → 정확도 99%!
    #   하지만 암 환자를 전부 놓쳤다 → 쓸모없는 모델
    #
    #   정밀도 (Precision): "양성이라고 예측한 것 중 실제 양성 비율"
    #     = TP / (TP + FP)
    #     → "스팸이라고 한 메일 중 진짜 스팸은?"
    #
    #   재현율 (Recall): "실제 양성 중 올바르게 양성 예측한 비율"
    #     = TP / (TP + FN)
    #     → "진짜 스팸 중 몇 개나 잡았나?"
    #

    # 스팸 필터 비유
    print("  [스팸 필터 비유]")
    print()
    print("    TP (True Positive):  스팸을 스팸으로 잡음     ← 잘했다!")
    print("    FP (False Positive): 정상을 스팸으로 잡음     ← 중요한 메일 놓침!")
    print("    FN (False Negative): 스팸을 정상으로 놓침     ← 스팸이 받은편지함에!")
    print("    TN (True Negative):  정상을 정상으로 판단     ← 잘했다!")
    print()

    # 수치 예제
    # 실제: [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
    # 예측: [1, 1, 0, 0, 1, 0, 0, 0, 0, 0]
    y_true = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
    y_pred = [1, 1, 0, 0, 1, 0, 0, 0, 0, 0]

    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    accuracy = (tp + tn) / len(y_true)
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    print("  [수치 예제]")
    print(f"    실제: {y_true}")
    print(f"    예측: {y_pred}")
    print()
    print(f"    TP={tp}, FP={fp}, FN={fn}, TN={tn}")
    print(f"    정확도 (Accuracy):  ({tp}+{tn})/{len(y_true)} = {accuracy:.2f}")
    print(f"    정밀도 (Precision): {tp}/({tp}+{fp}) = {precision:.2f}")
    print(f"    재현율 (Recall):    {tp}/({tp}+{fn}) = {recall:.2f}")
    print(f"    F1 점수:            2*{precision:.2f}*{recall:.2f}/({precision:.2f}+{recall:.2f}) = {f1:.2f}")
    print()

    # 트레이드오프 설명
    print("  [정밀도-재현율 트레이드오프]")
    print()
    print("    임계값↑ → 정밀도↑ 재현율↓ (까다롭게 판정, 놓치는 것 많음)")
    print("    임계값↓ → 정밀도↓ 재현율↑ (많이 잡지만 오판도 많음)")
    print()
    print("    암 진단: 재현율이 중요 → 놓치면 생명 위험!")
    print("    스팸 필터: 정밀도가 중요 → 중요 메일을 스팸으로 잡으면 큰일!")
    print()


def lesson6_confusion_matrix():
    # =========================================================================
    #
    #   레슨 6 — 혼동 행렬 시각화
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 혼동 행렬                  │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 혼동 행렬 (Confusion Matrix)
    # ─────────────────────────────────────────────────────────────────────
    #
    #                    예측
    #                양성(1)    음성(0)
    #   실  양성(1)  TP         FN
    #   제  음성(0)  FP         TN
    #

    def build_confusion_matrix(y_true, y_pred, classes):
        """혼동 행렬 생성"""
        n = len(classes)
        matrix = [[0] * n for _ in range(n)]
        class_to_idx = {c: i for i, c in enumerate(classes)}
        for t, p in zip(y_true, y_pred):
            matrix[class_to_idx[t]][class_to_idx[p]] += 1
        return matrix

    def print_confusion_matrix(matrix, classes):
        """혼동 행렬 ASCII 출력"""
        n = len(classes)
        # 헤더
        header = "         " + "  ".join(f"{c:>6}" for c in classes)
        print(header)
        print("         " + "  ".join("------" for _ in classes))
        for i in range(n):
            row = f"  {classes[i]:>5} |"
            for j in range(n):
                val = matrix[i][j]
                if i == j:  # 대각선 (맞은 것)
                    row += f"  [{val:>3}]"
                else:       # 비대각선 (틀린 것)
                    row += f"   {val:>3} "
            print(row)

    # 이진 분류 혼동 행렬
    y_true = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    y_pred = [1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    print("  [이진 분류 혼동 행렬]")
    print()
    print("    실제 vs 예측:")
    matrix = build_confusion_matrix(y_true, y_pred, [0, 1])
    print_confusion_matrix(matrix, ["음성", "양성"])
    print()

    tp = matrix[1][1]
    fp = matrix[0][1]
    fn = matrix[1][0]
    tn = matrix[0][0]
    print(f"    TP={tp} (양성을 양성으로 맞춤)")
    print(f"    FP={fp} (음성을 양성으로 잘못 예측)")
    print(f"    FN={fn} (양성을 음성으로 놓침)")
    print(f"    TN={tn} (음성을 음성으로 맞춤)")
    print()

    # 다중 클래스 혼동 행렬
    print("  [다중 클래스 혼동 행렬 - 학점 분류]")
    y_true_mc = ["A", "A", "B", "B", "B", "C", "C", "C", "C", "A"]
    y_pred_mc = ["A", "B", "B", "B", "C", "C", "C", "B", "C", "A"]

    matrix_mc = build_confusion_matrix(y_true_mc, y_pred_mc, ["A", "B", "C"])
    print()
    print_confusion_matrix(matrix_mc, ["A", "B", "C"])
    print()
    print("  → 대각선[...]의 합이 클수록 정확도가 높다!")
    print()


def lesson7_multiclass_strategy():
    # =========================================================================
    #
    #   레슨 7 — 다중 클래스 전략
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 다중 클래스 전략           │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 이진 분류기를 다중 클래스에 확장하는 방법
    # ─────────────────────────────────────────────────────────────────────
    #
    #   One-vs-Rest (OvR, OvA):
    #     클래스 3개(A, B, C)면 → 3개의 이진 분류기 만들기
    #       분류기1: A vs (B+C)
    #       분류기2: B vs (A+C)
    #       분류기3: C vs (A+B)
    #     → 가장 확률이 높은 클래스 선택
    #
    #   One-vs-One (OvO):
    #     클래스 3개면 → 3C2 = 3개의 이진 분류기
    #       분류기1: A vs B
    #       분류기2: A vs C
    #       분류기3: B vs C
    #     → 다수결로 결정
    #

    classes = ["사과", "바나나", "포도"]

    print("  [One-vs-Rest (OvR)]")
    print(f"    클래스: {classes}")
    print()
    for cls in classes:
        others = [c for c in classes if c != cls]
        print(f"    분류기: '{cls}' vs '{'+'.join(others)}'")
    print(f"    총 {len(classes)}개의 분류기 필요")
    print()

    # OvR 시뮬레이션
    print("  [OvR 시뮬레이션]")
    # 각 분류기의 확률 출력 (수동 설정)
    test_sample = "빨갛고 둥근 과일"
    ovr_scores = {"사과": 0.85, "바나나": 0.10, "포도": 0.30}

    print(f"    입력: '{test_sample}'")
    for cls, score in ovr_scores.items():
        bar = "#" * int(score * 20)
        print(f"    {cls:>4} 확률: {score:.2f} {bar}")
    winner = max(ovr_scores, key=ovr_scores.get)
    print(f"    → 최종 예측: {winner}")
    print()

    print("  [One-vs-One (OvO)]")
    print(f"    클래스: {classes}")
    print()
    pairs = []
    for i in range(len(classes)):
        for j in range(i + 1, len(classes)):
            pairs.append((classes[i], classes[j]))
            print(f"    분류기: '{classes[i]}' vs '{classes[j]}'")
    print(f"    총 {len(pairs)}개의 분류기 필요")
    print()

    # OvO 시뮬레이션
    print("  [OvO 시뮬레이션]")
    ovo_results = [
        ("사과", "바나나", "사과"),   # 사과 승
        ("사과", "포도",   "사과"),   # 사과 승
        ("바나나", "포도",  "포도"),   # 포도 승
    ]

    votes = {}
    for cls1, cls2, winner in ovo_results:
        print(f"    {cls1} vs {cls2} → 승자: {winner}")
        votes[winner] = votes.get(winner, 0) + 1

    print(f"    투표 결과: {votes}")
    final = max(votes, key=votes.get)
    print(f"    → 최종 예측: {final}")
    print()


def lesson8_practice():
    # =========================================================================
    #
    #   레슨 8 — 실전: 과일 분류기 만들기
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 8 : 과일 분류기 만들기         │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ KNN을 사용한 과일 분류기
    # ─────────────────────────────────────────────────────────────────────
    #
    #   특성 1: 무게 (g)
    #   특성 2: 둘레 (cm)
    #   클래스: 사과, 바나나, 포도
    #

    # 학습 데이터: [무게, 둘레] → 과일
    train_data = [
        # 사과 (무게 150~250g, 둘레 20~30cm)
        ([180, 25], "사과"), ([200, 27], "사과"), ([160, 22], "사과"),
        ([220, 28], "사과"), ([190, 24], "사과"),
        # 바나나 (무게 100~150g, 둘레 10~15cm)
        ([120, 12], "바나나"), ([130, 14], "바나나"), ([110, 11], "바나나"),
        ([140, 13], "바나나"), ([125, 12], "바나나"),
        # 포도 (무게 3~8g, 둘레 3~6cm)
        ([5, 4], "포도"), ([7, 5], "포도"), ([4, 3], "포도"),
        ([6, 5], "포도"), ([3, 3], "포도"),
    ]

    def euclidean_distance(p1, p2):
        return sum((a - b) ** 2 for a, b in zip(p1, p2)) ** 0.5

    def knn_classify(train_data, query, k=3):
        distances = []
        for features, label in train_data:
            dist = euclidean_distance(features, query)
            distances.append((dist, label))
        distances.sort(key=lambda x: x[0])
        k_nearest = distances[:k]
        votes = {}
        for _, label in k_nearest:
            votes[label] = votes.get(label, 0) + 1
        return max(votes, key=votes.get), k_nearest

    print("  [학습 데이터]")
    for features, label in train_data:
        print(f"    무게={features[0]:>3}g, 둘레={features[1]:>2}cm → {label}")
    print()

    # 테스트
    test_fruits = [
        ([170, 23], "사과"),
        ([135, 13], "바나나"),
        ([5, 4],    "포도"),
        ([195, 26], "사과"),
        ([115, 11], "바나나"),
    ]

    print("  [과일 분류 결과 (k=3)]")
    print(f"    {'무게':>4} {'둘레':>4} | {'예측':>6} | {'실제':>6} | 결과")
    print("    " + "-" * 42)

    correct = 0
    for features, actual in test_fruits:
        pred, neighbors = knn_classify(train_data, features, k=3)
        is_correct = pred == actual
        if is_correct:
            correct += 1
        mark = "O" if is_correct else "X"
        print(f"    {features[0]:>4} {features[1]:>4} | {pred:>6} | {actual:>6} | {mark}")

    accuracy = correct / len(test_fruits) * 100
    print()
    print(f"  정확도: {correct}/{len(test_fruits)} = {accuracy:.0f}%")
    print()

    # 스케일링 문제 지적
    print("  [주의: 스케일링 문제]")
    print("    무게: 3~250 범위")
    print("    둘레: 3~30 범위")
    print("    → 무게 차이가 거리 계산을 지배한다!")
    print("    → 다음 단계(04_feature_scaling.py)에서 해결 방법 학습!")
    print()

    # 성능 지표 계산
    classes = ["사과", "바나나", "포도"]
    print("  [클래스별 성능]")
    for cls in classes:
        tp = sum(1 for (_, a), (f, _) in zip(test_fruits, test_fruits)
                 if a == cls and knn_classify(train_data, f, k=3)[0] == cls)
        actual_count = sum(1 for _, a in test_fruits if a == cls)
        print(f"    {cls}: {tp}/{actual_count} 맞춤")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# ■ 메인 실행
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 72)
    print("  [ML 기초] 03단계: 분류 기초 (Classification Basics)")
    print("=" * 72)
    print()

    lesson1_what_is_classification()
    lesson2_decision_boundary()
    lesson3_logistic_regression()
    lesson4_knn()
    lesson5_precision_recall()
    lesson6_confusion_matrix()
    lesson7_multiclass_strategy()
    lesson8_practice()

    print("=" * 72)
    print("  03단계 완료! 다음: 04_feature_scaling.py")
    print("=" * 72)


if __name__ == "__main__":
    main()
