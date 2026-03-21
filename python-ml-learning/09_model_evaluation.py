# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#   파이썬 ML 학습 09단계: 모델 평가 (Model Evaluation)
#   ─ 모델의 성적표를 제대로 읽는 법 ─
#
#   비유: 병원 진단 검사의 정확도
#     "이 검사의 정확도가 99%!" 라고 해도
#     실제로는 쓸모없을 수 있습니다.
#     1000명 중 1명만 아픈 병이면, "모두 건강"이라 해도 99.9%!
#     정확도만으로는 부족합니다.
#
#   실행 방법:
#     python 09_model_evaluation.py
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import random


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 1: 혼동 행렬 (Confusion Matrix)
# ─────────────────────────────────────────────────────────────────────────

def lesson1_confusion_matrix():
    """
    비유: 암 검진 결과표
      TP = 암인 사람을 암이라고 정확히 진단 (참 양성)
      FP = 건강한 사람을 암이라고 잘못 진단 (거짓 양성, 헛놀람)
      FN = 암인 사람을 건강하다고 놓침 (거짓 음성, 위험!)
      TN = 건강한 사람을 건강하다고 정확히 진단 (참 음성)
    """
    print("=" * 70)
    print("[레슨 1] 혼동 행렬 (Confusion Matrix)")
    print("=" * 70)
    print()
    print("  비유: 암 검진 결과")
    print()

    tp = 8    # 암 환자를 암이라 함 (정확!)
    fp = 3    # 건강한 사람을 암이라 함 (헛놀람)
    fn = 2    # 암 환자를 놓침 (위험!)
    tn = 87   # 건강한 사람을 건강하다 함 (정확!)

    print("  ┌──────────────────┬────────────────┬────────────────┐")
    print("  │                  │ 예측: 양성(암)  │ 예측: 음성(건강)│")
    print("  ├──────────────────┼────────────────┼────────────────┤")
    print(f"  │ 실제: 양성(암)   │  TP = {tp:<5}   │  FN = {fn:<5}   │")
    print(f"  │ 실제: 음성(건강) │  FP = {fp:<5}   │  TN = {tn:<5}   │")
    print("  └──────────────────┴────────────────┴────────────────┘")
    print()
    print("  TP(True Positive):  정답=양성, 예측=양성 → 맞음!")
    print("  FP(False Positive): 정답=음성, 예측=양성 → 헛놀람")
    print("  FN(False Negative): 정답=양성, 예측=음성 → 놓침! (위험)")
    print("  TN(True Negative):  정답=음성, 예측=음성 → 맞음!")
    print()

    return tp, fp, fn, tn


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 2: 정확도, 정밀도, 재현율, F1
# ─────────────────────────────────────────────────────────────────────────

def lesson2_metrics(tp, fp, fn, tn):
    """
    비유: 경찰 수사
      정밀도 = 체포한 사람 중 진짜 범인 비율 ("무고한 사람 잡지 마!")
      재현율 = 전체 범인 중 잡은 비율 ("범인 놓치지 마!")
      둘 다 높으면 좋지만, 보통 하나를 올리면 다른 하나가 내려감.
    """
    print("=" * 70)
    print("[레슨 2] 정확도 / 정밀도 / 재현율 / F1")
    print("=" * 70)
    print()

    total = tp + fp + fn + tn
    accuracy = (tp + tn) / total
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    print(f"  정확도 (Accuracy) = (TP+TN)/전체 = ({tp}+{tn})/{total} = {accuracy:.3f}")
    print(f"    → 전체 중 맞힌 비율")
    print()

    print(f"  정밀도 (Precision) = TP/(TP+FP) = {tp}/({tp}+{fp}) = {precision:.3f}")
    print(f"    → '양성'이라 했을 때 진짜 양성인 비율")
    print(f"    → 비유: 체포한 사람 중 실제 범인 비율")
    print()

    print(f"  재현율 (Recall) = TP/(TP+FN) = {tp}/({tp}+{fn}) = {recall:.3f}")
    print(f"    → 실제 양성 중 찾아낸 비율")
    print(f"    → 비유: 전체 범인 중 잡은 비율")
    print()

    print(f"  F1 Score = 2×P×R/(P+R) = 2×{precision:.3f}×{recall:.3f}/({precision:.3f}+{recall:.3f}) = {f1:.3f}")
    print(f"    → 정밀도와 재현율의 조화 평균")
    print()

    # 정확도의 함정 예시
    print("  [주의] 정확도의 함정:")
    print("    1000명 중 암 환자 10명인 경우")
    print("    '모두 건강'이라 예측하면:")
    print(f"    정확도 = 990/1000 = 99% → 높지만 쓸모없음!")
    print(f"    재현율 = 0/10 = 0% → 암 환자를 하나도 못 찾음!")
    print()

    # 상황별 중요 지표
    print("  상황별 중요 지표:")
    print("  ┌───────────────┬──────────────┬──────────────────────┐")
    print("  │  상황         │  중요 지표   │  이유                │")
    print("  ├───────────────┼──────────────┼──────────────────────┤")
    print("  │ 암 검진       │  재현율      │  환자를 놓치면 위험  │")
    print("  │ 스팸 필터     │  정밀도      │  중요 메일 걸러지면↓ │")
    print("  │ 균형 잡힌 문제│  F1 Score    │  둘 다 중요          │")
    print("  └───────────────┴──────────────┴──────────────────────┘")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 3: ROC 곡선과 AUC
# ─────────────────────────────────────────────────────────────────────────

def lesson3_roc_auc():
    """
    ROC 곡선: 임계값을 바꿔가며 TPR vs FPR을 그린 곡선.
    AUC: ROC 곡선 아래 면적 (1에 가까울수록 좋음).

    비유: 금속탐지기 감도 조절
      감도 높이면 → 금속 잘 찾지만 쓰레기도 울림 (TPR↑, FPR↑)
      감도 낮추면 → 안 울리지만 금속도 놓침 (TPR↓, FPR↓)
      좋은 탐지기 = 감도 올려도 쓰레기에는 안 울림!
    """
    print("=" * 70)
    print("[레슨 3] ROC 곡선과 AUC")
    print("=" * 70)
    print()
    print("  TPR = 재현율 = TP/(TP+FN)")
    print("  FPR = FP/(FP+TN)")
    print()

    # 모델의 예측 확률과 실제 라벨
    random.seed(42)
    predictions = []
    for _ in range(20):
        true_label = random.choice([0, 1])
        if true_label == 1:
            score = random.uniform(0.4, 1.0)  # 양성은 높은 점수 경향
        else:
            score = random.uniform(0.0, 0.6)  # 음성은 낮은 점수 경향
        predictions.append((score, true_label))

    predictions.sort(key=lambda x: -x[0])

    # 임계값별 TPR, FPR 계산
    total_pos = sum(1 for _, l in predictions if l == 1)
    total_neg = sum(1 for _, l in predictions if l == 0)

    print("  임계값별 TPR, FPR:")
    print("  ┌──────────┬──────────┬──────────┐")
    print("  │ 임계값   │  TPR     │  FPR     │")
    print("  ├──────────┼──────────┼──────────┤")

    roc_points = []
    for threshold in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
        tp = sum(1 for s, l in predictions if s >= threshold and l == 1)
        fp = sum(1 for s, l in predictions if s >= threshold and l == 0)
        fn = sum(1 for s, l in predictions if s < threshold and l == 1)
        tn = sum(1 for s, l in predictions if s < threshold and l == 0)

        tpr = tp / total_pos if total_pos > 0 else 0
        fpr = fp / total_neg if total_neg > 0 else 0
        roc_points.append((fpr, tpr))

        print(f"  │  {threshold:>5.1f}   │  {tpr:>6.2f}  │  {fpr:>6.2f}  │")

    print("  └──────────┴──────────┴──────────┘")
    print()

    # 간단한 ASCII ROC 곡선
    print("  ROC 곡선 (ASCII):")
    print("  TPR")
    print("  1.0 ┤")

    grid = [[" "] * 20 for _ in range(10)]
    for fpr, tpr in roc_points:
        x = min(int(fpr * 19), 19)
        y = min(9 - int(tpr * 9), 9)
        if 0 <= x < 20 and 0 <= y < 10:
            grid[y][x] = "●"

    # 대각선 (무작위 모델)
    for i in range(10):
        grid[9-i][i*2] = "·" if grid[9-i][i*2] == " " else grid[9-i][i*2]

    for i, row in enumerate(grid):
        label = f"{1.0 - i*0.1:.1f}" if i % 2 == 0 else "   "
        print(f"  {label} │{''.join(row)}│")

    print("  0.0 └" + "─" * 20 + "→ FPR")
    print("       0.0              1.0")
    print()

    # AUC 근사 계산
    roc_points.sort()
    auc = 0.0
    for i in range(1, len(roc_points)):
        dx = roc_points[i][0] - roc_points[i-1][0]
        avg_y = (roc_points[i][1] + roc_points[i-1][1]) / 2
        auc += dx * avg_y

    print(f"  AUC ~= {auc:.3f}")
    print("    AUC = 1.0 → 완벽한 모델")
    print("    AUC = 0.5 → 동전 던지기 수준")
    print("    AUC < 0.5 → 예측을 반대로 하면 더 나음!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 4: 교차 검증 (K-Fold Cross Validation)
# ─────────────────────────────────────────────────────────────────────────

def lesson4_cross_validation():
    """
    교차 검증: 데이터를 K개로 나눠 번갈아 검증하는 방법.

    비유: 모의고사 5번 보기
      1차: 1~4장으로 공부, 5장으로 시험
      2차: 1,2,3,5장으로 공부, 4장으로 시험
      ... 5번 반복하면 모든 데이터가 한 번씩 시험에 나옴.
      평균 성적이 실제 실력에 가장 가까움!
    """
    print("=" * 70)
    print("[레슨 4] 교차 검증 (K-Fold Cross Validation)")
    print("=" * 70)
    print()

    data = list(range(1, 21))  # 20개 데이터
    k = 5
    fold_size = len(data) // k

    print(f"  데이터 {len(data)}개, {k}-Fold 교차 검증")
    print()

    random.seed(42)
    fold_scores = []

    for fold in range(k):
        start = fold * fold_size
        end = start + fold_size
        test = data[start:end]
        train = data[:start] + data[end:]

        # 가상 정확도
        accuracy = 0.80 + random.uniform(-0.05, 0.05)
        fold_scores.append(accuracy)

        test_str = str(test)
        print(f"    Fold {fold+1}: 테스트={test_str:>20s}  정확도={accuracy:.3f}")

    avg_score = sum(fold_scores) / len(fold_scores)
    std_score = math.sqrt(sum((s - avg_score)**2 for s in fold_scores) / len(fold_scores))

    print()
    print(f"  평균 정확도: {avg_score:.3f} (± {std_score:.3f})")
    print()
    print("  교차 검증의 장점:")
    print("    1. 모든 데이터가 한 번씩 테스트에 사용됨")
    print("    2. 한 번의 운 좋은/나쁜 분할에 의존하지 않음")
    print("    3. 모델의 실제 성능을 더 정확히 추정")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 5: 편향-분산 트레이드오프
# ─────────────────────────────────────────────────────────────────────────

def lesson5_bias_variance_tradeoff():
    """
    편향-분산 트레이드오프: 모델 복잡도의 균형.

    비유: 활쏘기
      편향(Bias) = 과녁 중심에서 평균적으로 얼마나 벗어나나 (정확도)
      분산(Variance) = 화살이 얼마나 흩어지나 (일관성)

      단순한 모델: 높은 편향, 낮은 분산 (과소적합)
      복잡한 모델: 낮은 편향, 높은 분산 (과적합)
    """
    print("=" * 70)
    print("[레슨 5] 편향-분산 트레이드오프")
    print("=" * 70)
    print()
    print("  비유: 과녁 맞히기")
    print()
    print("  높은편향+낮은분산    낮은편향+높은분산    낮은편향+낮은분산")
    print("  (과소적합)          (과적합)            (이상적!)")
    print("  ┌─────────┐        ┌─────────┐        ┌─────────┐")
    print("  │  · · ·  │        │ ·       │        │         │")
    print("  │  · · ·  │        │       · │        │  · · ·  │")
    print("  │  · · · ●│        │  ·●     │        │  ·●· ·  │")
    print("  │         │        │      ·  │        │  · · ·  │")
    print("  │         │        │   ·     │        │         │")
    print("  └─────────┘        └─────────┘        └─────────┘")
    print("   중심에서 멀지만      중심 근처지만       중심 근처에")
    print("   모여있음             흩어져있음          모여있음")
    print()

    # 모델 복잡도별 편향-분산
    complexities = [
        ("직선 (너무 단순)",  0.8, 0.1, "과소적합"),
        ("2차 곡선",         0.3, 0.2, "약간 부족"),
        ("적당한 다항식",     0.1, 0.15, "적절!"),
        ("10차 다항식",      0.05, 0.5, "과적합 시작"),
        ("100차 다항식",     0.01, 2.0, "심한 과적합"),
    ]

    print("  ┌─────────────────┬──────────┬──────────┬──────────────┐")
    print("  │  모델           │  편향    │  분산    │  상태        │")
    print("  ├─────────────────┼──────────┼──────────┼──────────────┤")

    for name, bias, var, status in complexities:
        total_error = bias + var
        print(f"  │ {name:>15s} │  {bias:>6.2f}  │  {var:>6.2f}  │ {status:<12s} │")

    print("  └─────────────────┴──────────┴──────────┴──────────────┘")
    print()
    print("  총 오차 = 편향² + 분산 + 노이즈")
    print("  → 편향과 분산이 동시에 최소인 지점을 찾는 것이 핵심!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■" * 72)
    print("  파이썬 ML 09단계 : 모델 평가 (Model Evaluation)")
    print("  비유: 병원 검사의 정확도를 제대로 읽는 법")
    print("■" * 72)
    print()

    tp, fp, fn, tn = lesson1_confusion_matrix()
    lesson2_metrics(tp, fp, fn, tn)
    lesson3_roc_auc()
    lesson4_cross_validation()
    lesson5_bias_variance_tradeoff()


if __name__ == "__main__":
    main()
