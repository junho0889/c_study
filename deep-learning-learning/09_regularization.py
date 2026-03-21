# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#   딥러닝 학습 09단계: 정규화 (Regularization)
#   ─ 시험 공부할 때 답만 외우면 안 되는 이유 ─
#
#   비유: 시험 공부
#     기출 문제 답만 달달 외우면(과적합) 새 문제에서 망합니다.
#     원리를 이해하며 공부하면(일반화) 처음 보는 문제도 풀 수 있습니다.
#     정규화는 모델이 답만 외우지 않도록 제한을 거는 기법입니다.
#
#   실행 방법:
#     python 09_regularization.py
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import random


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 1: 과적합 vs 과소적합
# ─────────────────────────────────────────────────────────────────────────

def lesson1_overfitting_underfitting():
    """
    비유: 시험 공부 방법 세 가지
      1. 과소적합(Underfitting): 공부를 너무 안 함 → 기출도 새 문제도 못 풀음
      2. 딱 좋음(Good fit): 원리를 이해 → 기출도 새 문제도 잘 풀음
      3. 과적합(Overfitting): 기출 답만 외움 → 기출은 100점, 새 문제는 0점
    """
    print("=" * 70)
    print("[레슨 1] 과적합 vs 과소적합")
    print("=" * 70)
    print()
    print("  비유: 시험 공부 스타일")
    print()
    print("  ┌───────────────┬────────────────┬────────────────┐")
    print("  │  상태         │  훈련 데이터   │  새 데이터     │")
    print("  ├───────────────┼────────────────┼────────────────┤")
    print("  │ 과소적합      │  점수 낮음     │  점수 낮음     │")
    print("  │ 적절한 학습   │  점수 높음     │  점수 높음     │")
    print("  │ 과적합        │  점수 매우높음 │  점수 낮음     │")
    print("  └───────────────┴────────────────┴────────────────┘")
    print()

    # 과적합 시뮬레이션: 다항식으로 노이즈까지 외워버리기
    random.seed(42)

    # 실제 패턴: y = 2x + 1
    train_x = [1, 2, 3, 4, 5]
    train_y = [2*x + 1 + random.uniform(-0.5, 0.5) for x in train_x]

    # 단순 모델 (적절): y = ax + b
    # 평균으로 대략 계산
    a = (train_y[-1] - train_y[0]) / (train_x[-1] - train_x[0])
    b = train_y[0] - a * train_x[0]

    print(f"  훈련 데이터: x={train_x}")
    print(f"  훈련 데이터: y=[{', '.join(f'{v:.1f}' for v in train_y)}]")
    print(f"  단순 모델: y = {a:.2f}x + {b:.2f}")
    print()

    # 훈련 오차 vs 테스트 오차
    test_x = [6, 7, 8]
    test_y = [2*x + 1 for x in test_x]

    train_err = sum((a*x+b - y)**2 for x, y in zip(train_x, train_y)) / len(train_x)
    test_err = sum((a*x+b - y)**2 for x, y in zip(test_x, test_y)) / len(test_x)

    print(f"  적절한 모델의 훈련 오차: {train_err:.3f}")
    print(f"  적절한 모델의 테스트 오차: {test_err:.3f}")
    print("  → 둘 다 비슷하면 과적합 아님!")
    print()

    # 과적합 시뮬레이션 (모든 점을 정확히 지나는 모델)
    print("  만약 훈련 오차=0인데 테스트 오차가 크다면? → 과적합!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 2: L1 정규화 (Lasso)
# ─────────────────────────────────────────────────────────────────────────

def lesson2_l1_regularization():
    """
    L1 정규화: 가중치의 절대값 합을 손실에 더합니다.

    비유: 짐을 싸는데 무게 제한이 있는 비행기
      - 꼭 필요한 짐만 챙기고 나머지는 버림
      - L1은 불필요한 가중치를 정확히 0으로 만드는 경향
      - 결과적으로 중요한 특징만 남김 (특징 선택 효과)
    """
    print("=" * 70)
    print("[레슨 2] L1 정규화 (Lasso)")
    print("=" * 70)
    print()
    print("  손실 = 원래 손실 + lambda × |w1| + |w2| + ... + |wn|")
    print()
    print("  비유: 비행기 무게 제한 → 불필요한 짐(가중치) 버리기")
    print()

    # L1 정규화 효과 시뮬레이션
    weights = [0.5, -0.3, 0.01, 0.8, -0.02, 0.6, 0.005]
    lambda_val = 0.1

    print(f"  원래 가중치: {weights}")
    print(f"  L1 패널티(lambda={lambda_val}):")
    print()

    l1_penalty = sum(abs(w) for w in weights)
    print(f"  L1 페널티 = {' + '.join(f'|{w}|' for w in weights)}")
    print(f"            = {l1_penalty:.3f}")
    print(f"  lambda × L1 = {lambda_val} × {l1_penalty:.3f} = {lambda_val * l1_penalty:.4f}")
    print()

    # L1은 작은 가중치를 0으로 만드는 경향
    print("  L1 정규화 후 경향:")
    for w in weights:
        # 단순화된 L1 업데이트
        sign = 1 if w > 0 else -1
        new_w = w - lambda_val * sign
        # 부호가 바뀌면 0으로 클립
        if (w > 0 and new_w < 0) or (w < 0 and new_w > 0):
            new_w = 0.0
        arrow = "→ 0으로!" if new_w == 0.0 else ""
        print(f"    {w:>6.3f} → {new_w:>6.3f}  {arrow}")

    print()
    print("  → 작은 가중치들이 0이 됨! 중요한 특징만 남기는 효과")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 3: L2 정규화 (Ridge)
# ─────────────────────────────────────────────────────────────────────────

def lesson3_l2_regularization():
    """
    L2 정규화: 가중치의 제곱합을 손실에 더합니다.

    비유: "한 과목에 올인하지 말고 골고루 공부해라"
      - 한 가중치가 너무 크면 벌점을 많이 줌
      - 모든 가중치를 고르게 작게 만드는 효과
      - L1처럼 0으로 만들지는 않지만, 전체적으로 줄임
    """
    print("=" * 70)
    print("[레슨 3] L2 정규화 (Ridge / Weight Decay)")
    print("=" * 70)
    print()
    print("  손실 = 원래 손실 + lambda × (w1² + w2² + ... + wn²)")
    print()

    weights = [0.5, -0.3, 0.01, 0.8, -0.02, 0.6, 0.005]
    lambda_val = 0.1

    l2_penalty = sum(w**2 for w in weights)
    print(f"  원래 가중치: {weights}")
    print(f"  L2 페널티 = {' + '.join(f'{w}²' for w in weights)}")
    print(f"            = {l2_penalty:.4f}")
    print(f"  lambda × L2 = {lambda_val} × {l2_penalty:.4f} = {lambda_val * l2_penalty:.5f}")
    print()

    print("  L2 정규화 후 경향:")
    for w in weights:
        new_w = w * (1 - lambda_val)  # 단순화된 weight decay
        print(f"    {w:>6.3f} → {new_w:>6.3f}  (비율적으로 줄어듦)")

    print()
    print("  L1 vs L2 비교:")
    print("  ┌──────────┬───────────────────┬───────────────────┐")
    print("  │          │      L1           │      L2           │")
    print("  ├──────────┼───────────────────┼───────────────────┤")
    print("  │ 페널티   │ |w| 합            │ w² 합             │")
    print("  │ 효과     │ 가중치를 0으로    │ 가중치를 작게     │")
    print("  │ 용도     │ 특징 선택         │ 과적합 방지       │")
    print("  └──────────┴───────────────────┴───────────────────┘")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 4: 드롭아웃 (Dropout)
# ─────────────────────────────────────────────────────────────────────────

def lesson4_dropout():
    """
    드롭아웃: 학습할 때 무작위로 일부 뉴런을 꺼버립니다.

    비유: 조별 과제에서 무작위로 결석하는 학생이 있으면
          나머지 학생들이 더 열심히 해야 함.
          모든 학생이 혼자서도 할 수 있게 되면 팀이 더 강해짐.
    """
    print("=" * 70)
    print("[레슨 4] 드롭아웃 (Dropout)")
    print("=" * 70)
    print()
    print("  학습 시: 뉴런을 무작위로 p확률로 끔")
    print("  테스트 시: 모든 뉴런 사용 (출력에 (1-p)를 곱함)")
    print()

    random.seed(42)
    neurons = [0.5, 0.8, 0.3, 0.9, 0.2, 0.7, 0.4, 0.6]
    dropout_rate = 0.3  # 30% 확률로 끔

    print(f"  원래 뉴런 출력: {neurons}")
    print(f"  드롭아웃 비율: {dropout_rate} (30%를 끔)")
    print()

    # 여러 번 드롭아웃 적용
    for trial in range(4):
        dropped = []
        for n in neurons:
            if random.random() < dropout_rate:
                dropped.append(0.0)   # 꺼짐!
            else:
                dropped.append(n)

        active_count = sum(1 for d in dropped if d > 0)
        display = []
        for i, d in enumerate(dropped):
            if d == 0.0:
                display.append("  X  ")
            else:
                display.append(f"{d:.1f} ")

        print(f"    시도 {trial+1}: [{', '.join(display)}] "
              f"(활성: {active_count}/{len(neurons)})")

    print()
    print("  → 매번 다른 뉴런이 꺼짐 → 특정 뉴런에 의존하지 않게 됨!")
    print("  → 테스트할 때는 모든 뉴런을 쓰되 출력을 (1-p)로 스케일링")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 5: 조기 종료 (Early Stopping)
# ─────────────────────────────────────────────────────────────────────────

def lesson5_early_stopping():
    """
    조기 종료: 검증 손실이 더 이상 줄어들지 않으면 학습을 멈춥니다.

    비유: 시험 공부할 때 "더 공부해도 성적이 안 오르면 그만 공부하고 자자"
          오히려 너무 오래 공부하면 컨디션이 나빠져 점수가 떨어질 수도!
    """
    print("=" * 70)
    print("[레슨 5] 조기 종료 (Early Stopping)")
    print("=" * 70)
    print()

    # 시뮬레이션: 훈련/검증 손실 추이
    random.seed(42)
    train_losses = []
    val_losses = []

    for epoch in range(20):
        # 훈련 손실은 계속 줄어듦
        train_loss = 1.0 / (1 + epoch * 0.5) + random.uniform(-0.02, 0.02)
        # 검증 손실은 중간부터 올라감 (과적합!)
        if epoch < 8:
            val_loss = 1.0 / (1 + epoch * 0.4) + random.uniform(-0.03, 0.03)
        else:
            val_loss = 0.3 + (epoch - 8) * 0.05 + random.uniform(-0.02, 0.02)
        train_losses.append(train_loss)
        val_losses.append(val_loss)

    print("  에폭별 손실 변화:")
    print("  ┌───────┬───────────┬───────────┬───────────────────────────┐")
    print("  │ 에폭  │ 훈련 손실 │ 검증 손실 │ 검증 손실 시각화          │")
    print("  ├───────┼───────────┼───────────┼───────────────────────────┤")

    best_val = float('inf')
    best_epoch = 0
    patience = 3
    patience_count = 0
    stopped_epoch = -1

    for epoch in range(20):
        t = train_losses[epoch]
        v = val_losses[epoch]
        bar = "#" * int(v * 30)
        mark = ""

        if v < best_val:
            best_val = v
            best_epoch = epoch
            patience_count = 0
        else:
            patience_count += 1

        if patience_count >= patience and stopped_epoch < 0:
            mark = " ← 여기서 멈춤!"
            stopped_epoch = epoch

        print(f"  │  {epoch+1:>3}  │  {t:>7.3f}  │  {v:>7.3f}  │ {bar:<25} │{mark}")

    print("  └───────┴───────────┴───────────┴───────────────────────────┘")
    print()
    print(f"  최적 에폭: {best_epoch+1} (검증 손실 {best_val:.3f})")
    if stopped_epoch > 0:
        print(f"  조기 종료 에폭: {stopped_epoch+1} (patience={patience})")
    print()
    print("  → 검증 손실이 올라가기 시작하면 = 과적합 시작 = 학습 멈추기!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 6: 데이터 증강 개념
# ─────────────────────────────────────────────────────────────────────────

def lesson6_data_augmentation():
    """
    데이터 증강: 기존 데이터를 변형해 더 많은 훈련 데이터를 만듭니다.

    비유: 시험 공부할 때 같은 문제를 약간만 바꿔서 연습하기
      - 숫자만 바꾸기 (3+5 → 4+6)
      - 문제 순서 바꾸기
      - 같은 원리의 다른 문제 만들기
    """
    print("=" * 70)
    print("[레슨 6] 데이터 증강 (Data Augmentation)")
    print("=" * 70)
    print()

    # 3x3 이미지를 다양하게 변형
    image = [
        [0, 1, 0],
        [0, 1, 0],
        [0, 1, 1],
    ]

    print("  원본 이미지:")
    for row in image:
        print("    " + " ".join(str(v) for v in row))
    print()

    # 좌우 반전
    flipped = [row[::-1] for row in image]
    print("  1. 좌우 반전:")
    for row in flipped:
        print("    " + " ".join(str(v) for v in row))
    print()

    # 상하 반전
    vflipped = image[::-1]
    print("  2. 상하 반전:")
    for row in vflipped:
        print("    " + " ".join(str(v) for v in row))
    print()

    # 90도 회전
    rotated = [[image[2-j][i] for j in range(3)] for i in range(3)]
    print("  3. 90도 회전:")
    for row in rotated:
        print("    " + " ".join(str(v) for v in row))
    print()

    # 노이즈 추가
    random.seed(42)
    noisy = []
    for row in image:
        noisy.append([min(1, max(0, v + random.choice([-0.1, 0, 0.1]))) for v in row])
    print("  4. 노이즈 추가:")
    for row in noisy:
        print("    " + " ".join(f"{v:.1f}" for v in row))
    print()

    print("  원본 1개 → 변형 4개 = 총 5개 데이터!")
    print("  → 데이터가 부족할 때 과적합을 줄이는 효과적인 방법")
    print()
    print("  이미지 증강 기법 정리:")
    print("    - 뒤집기, 회전, 크기 변환, 자르기")
    print("    - 밝기/대비 조절, 색상 변환")
    print("    - 노이즈 추가, 흐리게 하기")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■" * 72)
    print("  딥러닝 09단계 : 정규화 (Regularization)")
    print("  비유: 시험 공부할 때 답만 외우면 안 되는 이유")
    print("■" * 72)
    print()

    lesson1_overfitting_underfitting()
    lesson2_l1_regularization()
    lesson3_l2_regularization()
    lesson4_dropout()
    lesson5_early_stopping()
    lesson6_data_augmentation()


if __name__ == "__main__":
    main()
