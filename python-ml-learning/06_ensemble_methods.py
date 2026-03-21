# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#   파이썬 ML 학습 06단계: 앙상블 방법 (Ensemble Methods)
#   ─ 여러 모델의 힘을 합치면 더 강해진다 ─
#
#   비유: 여러 전문가에게 물어보기
#     한 명의 의견보다 여러 전문가의 의견을 종합하면
#     더 정확한 판단을 내릴 수 있습니다.
#     "삼인행 필유아사 (세 사람이 가면 반드시 스승이 있다)"
#
#   실행 방법:
#     python 06_ensemble_methods.py
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import random
import math


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 1: 왜 앙상블이 더 좋은가?
# ─────────────────────────────────────────────────────────────────────────

def lesson1_why_ensemble():
    """
    비유: 퀴즈 대회에서 팀전 vs 개인전
      혼자면 모르는 문제에서 막히지만,
      팀이면 누군가는 알 수 있어서 정답률이 올라감.
    """
    print("=" * 70)
    print("[레슨 1] 왜 앙상블이 더 좋은가?")
    print("=" * 70)
    print()

    random.seed(42)

    # 개별 모델 5개의 정답률 시뮬레이션
    n_questions = 20
    n_models = 5
    individual_accuracy = 0.65  # 각 모델 65% 정답률

    print(f"  {n_questions}문제, {n_models}개 모델, 개별 정답률 약 65%")
    print()

    # 각 모델의 예측 생성
    true_answers = [random.choice([0, 1]) for _ in range(n_questions)]
    model_predictions = []

    for m in range(n_models):
        preds = []
        for true in true_answers:
            if random.random() < individual_accuracy:
                preds.append(true)   # 정답
            else:
                preds.append(1 - true)  # 오답
        model_predictions.append(preds)

    # 개별 정확도
    print("  개별 모델 정확도:")
    for m in range(n_models):
        correct = sum(1 for p, t in zip(model_predictions[m], true_answers) if p == t)
        acc = correct / n_questions
        bar = "#" * int(acc * 30)
        print(f"    모델{m+1}: {acc:.0%} {bar}")

    # 다수결 앙상블
    ensemble_preds = []
    for q in range(n_questions):
        votes = [model_predictions[m][q] for m in range(n_models)]
        majority = 1 if sum(votes) > n_models / 2 else 0
        ensemble_preds.append(majority)

    correct = sum(1 for p, t in zip(ensemble_preds, true_answers) if p == t)
    ensemble_acc = correct / n_questions
    bar = "#" * int(ensemble_acc * 30)
    print(f"    앙상블: {ensemble_acc:.0%} {bar}  ← 다수결!")
    print()
    print("  → 개별 모델보다 앙상블이 더 높은 정확도!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 2: 배깅 (Bagging) - 랜덤 포레스트
# ─────────────────────────────────────────────────────────────────────────

def lesson2_bagging():
    """
    배깅: 데이터를 무작위로 뽑아 여러 모델을 만들고 다수결.
    랜덤 포레스트 = 배깅 + 결정 트리 여러 개.

    비유: 전문가 패널 구성
      각 전문가에게 다른 자료를 주고 독립적으로 판단하게 함.
      모든 전문가의 의견을 종합해서 최종 결정.
    """
    print("=" * 70)
    print("[레슨 2] 배깅 (Bagging) - 랜덤 포레스트 개념")
    print("=" * 70)
    print()

    random.seed(42)

    # 원본 데이터
    data = list(range(1, 11))  # [1, 2, ..., 10]
    print(f"  원본 데이터: {data}")
    print()

    # 부트스트랩 샘플링 (복원 추출)
    print("  부트스트랩 샘플링 (같은 크기, 복원 추출):")
    for tree_id in range(3):
        bootstrap = [random.choice(data) for _ in range(len(data))]
        not_selected = [d for d in data if d not in bootstrap]
        print(f"    트리{tree_id+1} 훈련용: {sorted(bootstrap)}")
        print(f"          빠진 것: {not_selected} (검증용)")
        print()

    print("  랜덤 포레스트 핵심:")
    print("    1. 데이터를 무작위로 뽑아 여러 트리를 만듦")
    print("    2. 각 트리는 특징도 무작위로 일부만 사용")
    print("    3. 모든 트리의 다수결로 최종 예측")
    print()

    # 간단한 랜덤 포레스트 시뮬레이션
    # 데이터: 키, 몸무게 → 운동선수 유형
    train_data = [
        ([180, 80], "농구"), ([175, 78], "농구"), ([185, 85], "농구"),
        ([160, 55], "체조"), ([163, 58], "체조"), ([158, 52], "체조"),
        ([170, 90], "역도"), ([168, 88], "역도"), ([172, 92], "역도"),
    ]

    test_sample = [171, 75]
    print(f"  테스트: 키={test_sample[0]}, 몸무게={test_sample[1]}")
    print()

    # 3개의 "트리" (단순 규칙 기반)
    tree_results = []
    for tree_id in range(5):
        # 부트스트랩 + 무작위 특징
        bootstrap = [random.choice(train_data) for _ in range(len(train_data))]
        use_feature = random.choice([0, 1])  # 키 또는 몸무게

        # 가장 가까운 이웃 찾기 (매우 단순화된 트리)
        best_dist = float('inf')
        best_label = ""
        for features, label in bootstrap:
            dist = abs(features[use_feature] - test_sample[use_feature])
            if dist < best_dist:
                best_dist = dist
                best_label = label

        tree_results.append(best_label)
        feat_name = "키" if use_feature == 0 else "몸무게"
        print(f"    트리{tree_id+1} (특징: {feat_name}): {best_label}")

    from collections import Counter
    final = Counter(tree_results).most_common(1)[0][0]
    print(f"    다수결 결과: {final}")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 3: 부스팅 (Boosting) - AdaBoost 개념
# ─────────────────────────────────────────────────────────────────────────

def lesson3_boosting():
    """
    부스팅: 틀린 데이터에 더 집중해서 순차적으로 모델을 만듦.

    비유: 오답 노트 공부법
      1차 시험 → 틀린 문제 체크
      2차 공부 → 틀린 문제 위주로 집중
      3차 시험 → 또 틀린 문제에 더 집중
      → 약한 부분이 점점 보강됨!
    """
    print("=" * 70)
    print("[레슨 3] 부스팅 (Boosting) - AdaBoost 개념")
    print("=" * 70)
    print()
    print("  비유: 오답 노트 공부법")
    print("    1라운드: 전체 공부 → 틀린 문제 발견")
    print("    2라운드: 틀린 문제 위주 공부 → 또 틀린 것 발견")
    print("    3라운드: 여전히 어려운 문제에 집중")
    print()

    # AdaBoost 시뮬레이션
    random.seed(42)
    n_samples = 8
    # 데이터 (1차원 분류)
    X = [1, 2, 3, 4, 5, 6, 7, 8]
    y = [1, 1, 1, -1, -1, -1, 1, 1]  # 비선형 패턴

    # 초기 가중치: 균등
    weights = [1.0 / n_samples] * n_samples

    print("  AdaBoost 과정:")
    print(f"  데이터:   X={X}")
    print(f"  라벨:     y={y}")
    print()

    for round_num in range(3):
        print(f"  --- 라운드 {round_num + 1} ---")
        print(f"    가중치: [{', '.join(f'{w:.3f}' for w in weights)}]")

        # 가장 단순한 분류기: 특정 임계값으로 나누기
        best_error = float('inf')
        best_threshold = 0
        best_direction = 1

        for threshold in range(1, 9):
            for direction in [1, -1]:
                error = 0.0
                for i in range(n_samples):
                    pred = direction if X[i] <= threshold else -direction
                    if pred != y[i]:
                        error += weights[i]
                if error < best_error:
                    best_error = error
                    best_threshold = threshold
                    best_direction = direction

        # 분류기 가중치
        if best_error == 0:
            best_error = 0.001
        alpha = 0.5 * math.log((1 - best_error) / best_error)

        print(f"    최적 규칙: X<={best_threshold} → {best_direction}")
        print(f"    오류율: {best_error:.3f}, 분류기 가중치(α): {alpha:.3f}")

        # 예측하고 가중치 업데이트
        predictions = []
        for i in range(n_samples):
            pred = best_direction if X[i] <= best_threshold else -best_direction
            predictions.append(pred)

        new_weights = []
        for i in range(n_samples):
            if predictions[i] != y[i]:
                new_weights.append(weights[i] * math.exp(alpha))
            else:
                new_weights.append(weights[i] * math.exp(-alpha))

        # 정규화
        total_w = sum(new_weights)
        weights = [w / total_w for w in new_weights]

        wrong = [i+1 for i in range(n_samples) if predictions[i] != y[i]]
        print(f"    틀린 데이터: {wrong}")
        print(f"    → 틀린 데이터의 가중치가 올라감!")
        print()

    print("  배깅 vs 부스팅:")
    print("  ┌──────────┬─────────────────┬─────────────────┐")
    print("  │          │    배깅         │    부스팅       │")
    print("  ├──────────┼─────────────────┼─────────────────┤")
    print("  │ 학습방식 │ 병렬 (독립적)   │ 순차적 (의존적) │")
    print("  │ 초점     │ 분산 줄이기     │ 편향 줄이기     │")
    print("  │ 대표모델 │ 랜덤 포레스트   │ AdaBoost, XGB   │")
    print("  │ 과적합   │ 잘 안 됨        │ 될 수 있음      │")
    print("  └──────────┴─────────────────┴─────────────────┘")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 4: 투표 분류기 (Voting Classifier)
# ─────────────────────────────────────────────────────────────────────────

def lesson4_voting_classifier():
    """
    투표 분류기: 서로 다른 종류의 모델들을 합침.

    비유: 의사 소견
      내과 의사 + 외과 의사 + 영상의학과 의사가
      각자 진단을 내리고 다수결로 최종 진단.
      전문 분야가 달라서 서로 보완됨!
    """
    print("=" * 70)
    print("[레슨 4] 투표 분류기 (Voting Classifier)")
    print("=" * 70)
    print()

    # 세 가지 다른 "모델" 시뮬레이션
    # 모델 1: 키 기준 (키 > 170이면 "키큼")
    # 모델 2: 몸무게 기준 (몸무게 > 70이면 "키큼")
    # 모델 3: BMI 기준

    test_data = [
        [175, 65, "키큼"],
        [165, 80, "키작음"],
        [172, 70, "키큼"],
        [168, 60, "키작음"],
        [178, 75, "키큼"],
    ]

    print("  세 가지 모델로 예측 후 투표:")
    print()
    print("  ┌──────┬──────┬─────────┬─────────┬─────────┬──────────┬──────┐")
    print("  │  키  │몸무게│ 모델1   │ 모델2   │ 모델3   │  다수결  │정답  │")
    print("  │      │      │ (키>170)│(몸>70)  │(BMI)    │          │      │")
    print("  ├──────┼──────┼─────────┼─────────┼─────────┼──────────┼──────┤")

    correct = 0
    for height, weight, true_label in test_data:
        # 모델1: 키 기준
        pred1 = "키큼" if height > 170 else "키작음"
        # 모델2: 몸무게 기준
        pred2 = "키큼" if weight > 70 else "키작음"
        # 모델3: BMI 기준
        bmi = weight / ((height / 100) ** 2)
        pred3 = "키큼" if bmi < 25 and height > 168 else "키작음"

        votes = [pred1, pred2, pred3]
        from collections import Counter
        final = Counter(votes).most_common(1)[0][0]

        if final == true_label:
            correct += 1

        print(f"  │ {height:>4} │ {weight:>4} │ {pred1:>7s} │ {pred2:>7s} │ {pred3:>7s} │ {final:>8s} │{true_label:>5s} │")

    print("  └──────┴──────┴─────────┴─────────┴─────────┴──────────┴──────┘")
    acc = correct / len(test_data)
    print(f"  투표 분류기 정확도: {acc:.0%}")
    print()
    print("  하드 투표: 각 모델의 예측 결과로 다수결")
    print("  소프트 투표: 각 모델의 확률을 평균 → 더 정확할 수 있음")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■" * 72)
    print("  파이썬 ML 06단계 : 앙상블 방법 (Ensemble Methods)")
    print("  비유: 여러 전문가의 의견을 합쳐 더 정확한 판단")
    print("■" * 72)
    print()

    lesson1_why_ensemble()
    lesson2_bagging()
    lesson3_boosting()
    lesson4_voting_classifier()


if __name__ == "__main__":
    main()
