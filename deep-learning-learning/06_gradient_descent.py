# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#   딥러닝 학습 06단계: 경사 하강법 (Gradient Descent)
#   ─ 손실이 줄어드는 방향으로 한 발짝씩 걸어가기 ─
#
#   비유: 안개 낀 산에서 하산하기
#     정상에서 내려가고 싶은데 안개가 자욱해 산 전체가 안 보입니다.
#     발밑의 경사만 느껴서 "이쪽이 내리막이네?" 하고 한 발짝 내딛습니다.
#     이걸 반복하면 결국 골짜기(최적점)에 도달합니다.
#
#   실행 방법:
#     python 06_gradient_descent.py
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import random


# ─────────────────────────────────────────────────────────────────────────
# ■ 도우미 함수
# ─────────────────────────────────────────────────────────────────────────

def simple_loss(w):
    """간단한 2차 함수 손실: L(w) = (w - 3)^2 + 1  → 최소점은 w=3"""
    return (w - 3.0) ** 2 + 1.0


def simple_loss_gradient(w):
    """위 함수의 미분: dL/dw = 2(w - 3)"""
    return 2.0 * (w - 3.0)


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 1: 배치 경사 하강법 (Batch GD)
# ─────────────────────────────────────────────────────────────────────────

def lesson1_batch_gradient_descent():
    """
    배치 경사 하강법: 전체 데이터를 한 번에 보고 기울기를 계산합니다.

    비유: 산에서 하산할 때, 주변 360도를 전부 살펴보고
          가장 가파른 내리막을 골라 한 발짝 내딛는 방법.
          정확하지만 360도 전부 보느라 시간이 오래 걸림.
    """
    print("=" * 70)
    print("[레슨 1] 배치 경사 하강법 (Batch GD)")
    print("=" * 70)
    print()
    print("  전체 데이터를 다 보고 평균 기울기로 이동")
    print("  장점: 안정적   단점: 데이터가 많으면 느림")
    print()

    # 간단한 선형 회귀: y = w*x, 데이터 4개로 w 찾기
    data_x = [1.0, 2.0, 3.0, 4.0]
    data_y = [2.0, 4.0, 6.0, 8.0]  # 정답: w = 2
    w = 0.0
    lr = 0.01

    print(f"  데이터: x={data_x}, y={data_y}")
    print(f"  정답 가중치: 2.0")
    print(f"  시작 w={w}, 학습률={lr}")
    print()

    for epoch in range(6):
        # 전체 데이터로 기울기 계산
        total_grad = 0.0
        total_loss = 0.0
        for xi, yi in zip(data_x, data_y):
            pred = w * xi
            error = pred - yi
            total_loss += error ** 2
            total_grad += 2 * error * xi  # dL/dw = 2(wx-y)x

        avg_grad = total_grad / len(data_x)
        avg_loss = total_loss / len(data_x)
        w = w - lr * avg_grad

        print(f"    에폭 {epoch+1}: w={w:.4f}, 평균손실={avg_loss:.4f}")

    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 2: 확률적 경사 하강법 (SGD)
# ─────────────────────────────────────────────────────────────────────────

def lesson2_stochastic_gradient_descent():
    """
    SGD: 데이터 하나를 뽑아 기울기를 계산하고 바로 이동합니다.

    비유: 한 사람한테만 길을 물어보고 바로 걸어가는 것.
          빠르지만 가끔 엉뚱한 방향으로 갈 수도 있음.
          하지만 평균적으로는 올바른 방향을 향함.
    """
    print("=" * 70)
    print("[레슨 2] 확률적 경사 하강법 (SGD)")
    print("=" * 70)
    print()
    print("  데이터 1개씩 보고 바로 업데이트")
    print("  장점: 빠름   단점: 경로가 울퉁불퉁")
    print()

    data_x = [1.0, 2.0, 3.0, 4.0]
    data_y = [2.0, 4.0, 6.0, 8.0]
    w = 0.0
    lr = 0.01

    random.seed(42)
    for epoch in range(6):
        indices = list(range(len(data_x)))
        random.shuffle(indices)
        epoch_loss = 0.0

        for i in indices:
            xi, yi = data_x[i], data_y[i]
            pred = w * xi
            error = pred - yi
            epoch_loss += error ** 2
            grad = 2 * error * xi
            w = w - lr * grad  # 하나씩 바로 업데이트!

        avg_loss = epoch_loss / len(data_x)
        print(f"    에폭 {epoch+1}: w={w:.4f}, 평균손실={avg_loss:.4f}")

    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 3: 미니배치 경사 하강법
# ─────────────────────────────────────────────────────────────────────────

def lesson3_minibatch_gradient_descent():
    """
    미니배치: 몇 개씩 묶어서 기울기를 계산합니다.
    Batch와 SGD의 중간 지점.

    비유: 3~4명한테 길을 물어보고 다수결로 방향을 정하는 것.
          한 명보다 정확하고, 전원보다 빠름. 실무에서 가장 많이 씀!
    """
    print("=" * 70)
    print("[레슨 3] 미니배치 경사 하강법")
    print("=" * 70)
    print()

    data_x = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    data_y = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0]
    w = 0.0
    lr = 0.01
    batch_size = 2

    print(f"  배치 크기: {batch_size}")
    print()

    for epoch in range(6):
        epoch_loss = 0.0
        for start in range(0, len(data_x), batch_size):
            batch_x = data_x[start:start+batch_size]
            batch_y = data_y[start:start+batch_size]

            batch_grad = 0.0
            for xi, yi in zip(batch_x, batch_y):
                pred = w * xi
                error = pred - yi
                epoch_loss += error ** 2
                batch_grad += 2 * error * xi

            batch_grad /= len(batch_x)
            w = w - lr * batch_grad

        avg_loss = epoch_loss / len(data_x)
        print(f"    에폭 {epoch+1}: w={w:.4f}, 평균손실={avg_loss:.4f}")

    print()
    print("  세 방법 비교:")
    print("  ┌──────────┬────────────┬────────────┬──────────────┐")
    print("  │  방법    │ 한번에 보는│   속도     │   안정성     │")
    print("  │          │ 데이터 수  │            │              │")
    print("  ├──────────┼────────────┼────────────┼──────────────┤")
    print("  │ Batch GD │ 전체       │ 느림       │ 매우 안정    │")
    print("  │ SGD      │ 1개        │ 빠름       │ 불안정       │")
    print("  │ Mini-Bat │ N개 묶음   │ 중간       │ 적당히 안정  │")
    print("  └──────────┴────────────┴────────────┴──────────────┘")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 4: 모멘텀 (Momentum)
# ─────────────────────────────────────────────────────────────────────────

def lesson4_momentum():
    """
    모멘텀: 이전에 움직이던 방향의 관성을 유지합니다.

    비유: 산에서 공을 굴리면, 내리막에서 점점 빨라지고
          작은 올라감은 관성으로 넘어갑니다.
          안개 속에서 걷는 사람(일반 GD)보다 공이 더 빨리 내려갑니다.
    """
    print("=" * 70)
    print("[레슨 4] 모멘텀 (Momentum)")
    print("=" * 70)
    print()
    print("  v = momentum × v_이전 - 학습률 × 기울기")
    print("  w = w + v")
    print()

    w_plain = 10.0    # 일반 GD 시작점
    w_mom = 10.0      # 모멘텀 GD 시작점
    lr = 0.1
    momentum = 0.9
    velocity = 0.0

    print("  ┌───────┬──────────────┬──────────────┬──────────────┬──────────────┐")
    print("  │ 스텝  │ 일반GD w     │ 일반GD 손실  │ 모멘텀 w     │ 모멘텀 손실  │")
    print("  ├───────┼──────────────┼──────────────┼──────────────┼──────────────┤")

    for step in range(12):
        loss_plain = simple_loss(w_plain)
        loss_mom = simple_loss(w_mom)
        print(f"  │  {step+1:>3}  │ {w_plain:>12.4f} │ {loss_plain:>12.4f} │ {w_mom:>12.4f} │ {loss_mom:>12.4f} │")

        # 일반 GD
        grad_plain = simple_loss_gradient(w_plain)
        w_plain = w_plain - lr * grad_plain

        # 모멘텀 GD
        grad_mom = simple_loss_gradient(w_mom)
        velocity = momentum * velocity - lr * grad_mom
        w_mom = w_mom + velocity

    print("  └───────┴──────────────┴──────────────┴──────────────┴──────────────┘")
    print()
    print("  → 모멘텀이 더 빨리 최적점(w=3)에 수렴하는 것을 볼 수 있습니다!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 5: 학습률 스케줄링
# ─────────────────────────────────────────────────────────────────────────

def lesson5_learning_rate_scheduling():
    """
    학습률을 학습 중에 줄여나가는 기법입니다.

    비유: 산에서 처음엔 큰 보폭으로 빠르게 내려가다가,
          골짜기 근처에서는 작은 보폭으로 조심스럽게 움직이는 것.
    """
    print("=" * 70)
    print("[레슨 5] 학습률 스케줄링")
    print("=" * 70)
    print()

    initial_lr = 1.0
    w = 10.0

    print("  Step Decay: 일정 간격마다 학습률을 절반으로")
    print("  ┌───────┬────────────┬──────────┬──────────┐")
    print("  │ 스텝  │  학습률    │    w     │   손실   │")
    print("  ├───────┼────────────┼──────────┼──────────┤")

    for step in range(10):
        # Step decay: 매 3스텝마다 절반
        lr = initial_lr * (0.5 ** (step // 3))
        grad = simple_loss_gradient(w)
        w = w - lr * grad
        loss = simple_loss(w)
        print(f"  │  {step+1:>3}  │ {lr:>10.4f} │ {w:>8.4f} │ {loss:>8.4f} │")

    print("  └───────┴────────────┴──────────┴──────────┘")
    print()

    # 지수 감쇠
    print("  Exponential Decay: lr = lr_0 × 0.9^step")
    w = 10.0
    for step in range(8):
        lr = initial_lr * (0.9 ** step)
        grad = simple_loss_gradient(w)
        w = w - lr * grad
        print(f"    스텝 {step+1}: lr={lr:.4f}, w={w:.4f}, 손실={simple_loss(w):.4f}")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 6: 기울기 소실/폭발 문제
# ─────────────────────────────────────────────────────────────────────────

def lesson6_vanishing_exploding_gradient():
    """
    깊은 신경망에서 기울기가 너무 작아지거나 커지는 문제.

    비유: 전화 게임 (귓속말 전달)
      - 소실: 메시지를 전달할 때마다 소리가 작아져서 마지막 사람은 못 들음
      - 폭발: 전달할 때마다 소리가 커져서 마지막 사람은 귀가 아픔
    """
    print("=" * 70)
    print("[레슨 6] 기울기 소실 / 기울기 폭발")
    print("=" * 70)
    print()
    print("  기울기 소실 (Vanishing Gradient):")
    print("  시그모이드의 미분값 최대 = 0.25 → 층이 깊으면 곱할수록 작아짐")
    print()

    # 시그모이드 미분값을 계속 곱하는 시뮬레이션
    grad = 1.0
    sig_deriv = 0.25  # 시그모이드 미분의 최대값
    print("  시그모이드 미분(0.25)을 층마다 곱할 때:")
    for layer in range(10):
        grad *= sig_deriv
        bar = "#" * max(1, int(grad * 1000))
        print(f"    {layer+1}층 후 기울기: {grad:.10f}  {bar}")

    print()
    print("  → 10층만 지나도 기울기가 거의 0! 앞쪽 층은 학습이 안 됩니다.")
    print()

    # 폭발 시뮬레이션
    print("  기울기 폭발 (Exploding Gradient):")
    print("  가중치가 크면 곱할수록 기울기가 급격히 커짐")
    print()

    grad = 1.0
    large_weight = 2.0
    for layer in range(10):
        grad *= large_weight
        display = f"{grad:.0f}" if grad < 1e10 else f"{grad:.2e}"
        print(f"    {layer+1}층 후 기울기: {display}")

    print()
    print("  해결책:")
    print("    소실 → ReLU 활성화 함수 사용, 잔차 연결(ResNet)")
    print("    폭발 → 기울기 클리핑(일정 크기 이상이면 잘라냄)")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■" * 72)
    print("  딥러닝 06단계 : 경사 하강법 (Gradient Descent)")
    print("  비유: 안개 낀 산에서 발밑 경사만 느끼며 하산하기")
    print("■" * 72)
    print()

    lesson1_batch_gradient_descent()
    lesson2_stochastic_gradient_descent()
    lesson3_minibatch_gradient_descent()
    lesson4_momentum()
    lesson5_learning_rate_scheduling()
    lesson6_vanishing_exploding_gradient()


if __name__ == "__main__":
    main()
