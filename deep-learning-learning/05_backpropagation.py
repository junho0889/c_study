# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#   딥러닝 학습 05단계: 역전파 (Backpropagation)
#   ─ 틀린 만큼 되돌아가며 가중치를 고치는 핵심 원리 ─
#
#   비유: 요리 레시피 조절하기
#     케이크가 너무 달면, "설탕을 줄이자"라고 되짚어 가는 것처럼
#     신경망도 결과가 틀리면 각 가중치를 얼마나 고칠지
#     출력에서 입력 방향으로 거슬러 올라가며 계산합니다.
#
#   실행 방법:
#     python 05_backpropagation.py
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math


# ─────────────────────────────────────────────────────────────────────────
# ■ 도우미 함수들
# ─────────────────────────────────────────────────────────────────────────

def sigmoid(x):
    """시그모이드: 어떤 숫자든 0~1 사이로 눌러주는 함수"""
    return 1.0 / (1.0 + math.exp(-x))


def sigmoid_derivative(output):
    """시그모이드의 미분값 (이미 시그모이드를 통과한 값 기준)"""
    # sigmoid(x)를 s라 하면, ds/dx = s * (1 - s)
    return output * (1.0 - output)


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 1: 연쇄 법칙 (Chain Rule) 이해하기
# ─────────────────────────────────────────────────────────────────────────

def lesson1_chain_rule():
    """
    연쇄 법칙은 역전파의 수학적 핵심입니다.

    비유: 요리에서 "맛이 달라진 원인"을 추적하는 것과 같습니다.
      - 케이크 맛 ← 반죽 상태 ← 설탕 양
      - "설탕을 바꾸면 맛이 얼마나 변하나?"를 알려면
        "설탕→반죽 영향" × "반죽→맛 영향" 을 곱하면 됩니다.
    """
    print("=" * 70)
    print("[레슨 1] 연쇄 법칙 (Chain Rule)")
    print("=" * 70)
    print()
    print("  비유: 설탕 양 → 반죽 단맛 → 케이크 맛")
    print("  설탕이 케이크 맛에 미치는 영향 = (설탕→반죽) × (반죽→케이크)")
    print()

    # 수학 예제: y = (2x + 1)^2 에서 dy/dx 구하기
    # u = 2x + 1 이라 하면,  y = u^2
    # dy/dx = dy/du * du/dx = 2u * 2 = 4(2x+1)
    x = 3.0
    u = 2 * x + 1       # u = 7
    y = u ** 2           # y = 49

    du_dx = 2.0          # du/dx = 2
    dy_du = 2 * u        # dy/du = 2 * 7 = 14
    dy_dx = dy_du * du_dx  # dy/dx = 14 * 2 = 28

    print("  수학 예제: y = (2x + 1)^2,  x = 3")
    print(f"    u = 2×{x} + 1 = {u}")
    print(f"    y = {u}² = {y}")
    print(f"    du/dx = {du_dx}")
    print(f"    dy/du = 2×{u} = {dy_du}")
    print(f"    dy/dx = {dy_du} × {du_dx} = {dy_dx}  (연쇄 법칙!)")
    print()

    # 검증: 아주 작은 변화를 줘서 수치적으로 확인
    h = 0.0001
    x2 = x + h
    y2 = (2 * x2 + 1) ** 2
    numerical_grad = (y2 - y) / h
    print(f"  수치 미분으로 검증: ({y2:.4f} - {y}) / {h} ~= {numerical_grad:.4f}")
    print(f"  연쇄 법칙 결과와 거의 같음 → 연쇄 법칙이 맞다!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 2: 기울기(그래디언트) 계산
# ─────────────────────────────────────────────────────────────────────────

def lesson2_gradient_calculation():
    """
    기울기는 "이 가중치를 살짝 바꾸면 손실이 얼마나 변하나?"를 알려줍니다.

    비유: 요리에서 소금을 한 꼬집 더 넣으면 짠맛이 얼마나 강해지는지.
          그 "얼마나"가 기울기(그래디언트)입니다.
    """
    print("=" * 70)
    print("[레슨 2] 기울기(그래디언트) 계산")
    print("=" * 70)
    print()
    print("  기울기 = 가중치를 조금 바꿨을 때 손실이 변하는 정도")
    print("  기울기가 크면 → 그 가중치가 결과에 큰 영향을 줌")
    print("  기울기가 작으면 → 그 가중치가 결과에 별 영향 없음")
    print()

    # 간단한 뉴런 하나로 기울기 계산
    # 출력 = sigmoid(w * x + b)
    # 손실 = (정답 - 출력)^2  (MSE)
    x = 1.5
    w = 0.5
    b = 0.1
    target = 1.0

    # 순전파
    z = w * x + b
    output = sigmoid(z)
    loss = (target - output) ** 2

    print(f"  입력 x = {x},  가중치 w = {w},  바이어스 b = {b}")
    print(f"  z = w×x + b = {w}×{x} + {b} = {z}")
    print(f"  출력 = sigmoid({z}) = {output:.4f}")
    print(f"  정답 = {target},  손실(MSE) = ({target} - {output:.4f})² = {loss:.6f}")
    print()

    # 역전파로 기울기 계산
    # dL/d(output) = -2(target - output)
    dL_dout = -2.0 * (target - output)
    # d(output)/dz = sigmoid_derivative
    dout_dz = sigmoid_derivative(output)
    # dz/dw = x,   dz/db = 1
    dz_dw = x
    dz_db = 1.0

    dL_dw = dL_dout * dout_dz * dz_dw
    dL_db = dL_dout * dout_dz * dz_db

    print("  역전파 과정 (출력 → 입력 방향으로):")
    print(f"    dL/d(출력) = -2×({target} - {output:.4f}) = {dL_dout:.4f}")
    print(f"    d(출력)/dz = sigmoid'({output:.4f}) = {dout_dz:.4f}")
    print(f"    dz/dw = x = {dz_dw}")
    print(f"    dL/dw = {dL_dout:.4f} × {dout_dz:.4f} × {dz_dw} = {dL_dw:.6f}")
    print(f"    dL/db = {dL_dout:.4f} × {dout_dz:.4f} × {dz_db} = {dL_db:.6f}")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 3: 가중치 업데이트와 학습률
# ─────────────────────────────────────────────────────────────────────────

def lesson3_weight_update():
    """
    가중치 업데이트 공식: w_new = w_old - 학습률 × 기울기

    비유: 요리 조절
      - 기울기가 "설탕이 너무 많다"라고 알려주면
      - 학습률은 "얼마나 줄일지"를 정하는 조심성
      - 학습률이 크면 확 줄이고, 작으면 조금씩 줄임
    """
    print("=" * 70)
    print("[레슨 3] 가중치 업데이트와 학습률")
    print("=" * 70)
    print()

    w = 0.5
    gradient = -0.15  # 레슨2에서 계산한 것처럼 가정

    print("  가중치 업데이트 공식: w_new = w_old - 학습률 × 기울기")
    print()
    print("  학습률별 비교:")
    print("  ┌──────────┬──────────────┬──────────────┐")
    print("  │  학습률  │   변화량     │   새 가중치  │")
    print("  ├──────────┼──────────────┼──────────────┤")

    for lr in [0.01, 0.1, 0.5, 1.0]:
        change = lr * gradient
        new_w = w - lr * gradient
        print(f"  │  {lr:<8}│  {change:>+10.4f}  │  {new_w:>10.4f}  │")

    print("  └──────────┴──────────────┴──────────────┘")
    print()
    print("  주의: 학습률이 너무 크면 → 값이 왔다갔다 발산할 수 있음")
    print("        학습률이 너무 작으면 → 학습이 너무 느림")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 4: 2층 신경망 역전파 전체 과정
# ─────────────────────────────────────────────────────────────────────────

def lesson4_two_layer_backprop():
    """
    2층 신경망에서 역전파를 처음부터 끝까지 수치로 따라갑니다.

    구조:
      입력(2개) → 은닉층(2개 뉴런) → 출력(1개 뉴런)

    비유: 2단계 요리
      1단계: 재료 → 소스 2종류 만들기 (은닉층)
      2단계: 소스 2종류 → 최종 요리 (출력층)
      맛이 이상하면, 2단계부터 거슬러 올라가며 고칩니다.
    """
    print("=" * 70)
    print("[레슨 4] 2층 신경망 역전파 전체 과정")
    print("=" * 70)
    print()
    print("  구조도:")
    print("  x1 ─┬─ [h1] ─┐")
    print("      │        ├─ [출력] → 손실")
    print("  x2 ─┴─ [h2] ─┘")
    print()

    # --- 초기 설정 ---
    x = [0.5, 0.8]       # 입력 2개
    target = 0.9          # 정답
    lr = 0.5              # 학습률

    # 가중치 (입력→은닉)
    w_ih = [[0.3, 0.6],   # x1→h1, x1→h2
            [0.4, 0.2]]   # x2→h1, x2→h2
    b_h = [0.1, -0.1]     # 은닉 바이어스

    # 가중치 (은닉→출력)
    w_ho = [0.7, 0.5]     # h1→out, h2→out
    b_o = 0.05            # 출력 바이어스

    print("  === 1단계: 순전파 ===")

    # 은닉층 계산
    z_h1 = x[0]*w_ih[0][0] + x[1]*w_ih[1][0] + b_h[0]
    z_h2 = x[0]*w_ih[0][1] + x[1]*w_ih[1][1] + b_h[1]
    h1 = sigmoid(z_h1)
    h2 = sigmoid(z_h2)

    print(f"    z_h1 = {x[0]}×{w_ih[0][0]} + {x[1]}×{w_ih[1][0]} + {b_h[0]} = {z_h1:.4f}")
    print(f"    h1 = sigmoid({z_h1:.4f}) = {h1:.4f}")
    print(f"    z_h2 = {x[0]}×{w_ih[0][1]} + {x[1]}×{w_ih[1][1]} + {b_h[1]} = {z_h2:.4f}")
    print(f"    h2 = sigmoid({z_h2:.4f}) = {h2:.4f}")

    # 출력층 계산
    z_o = h1*w_ho[0] + h2*w_ho[1] + b_o
    output = sigmoid(z_o)
    loss = (target - output) ** 2

    print(f"    z_o = {h1:.4f}×{w_ho[0]} + {h2:.4f}×{w_ho[1]} + {b_o} = {z_o:.4f}")
    print(f"    출력 = sigmoid({z_o:.4f}) = {output:.4f}")
    print(f"    손실 = ({target} - {output:.4f})² = {loss:.6f}")
    print()

    # --- 역전파 ---
    print("  === 2단계: 역전파 (출력 → 은닉 → 입력) ===")

    # 출력층 기울기
    dL_dout = -2.0 * (target - output)
    dout_dzo = sigmoid_derivative(output)
    delta_o = dL_dout * dout_dzo

    print(f"    dL/d(출력) = -2×({target}-{output:.4f}) = {dL_dout:.4f}")
    print(f"    d(출력)/dz_o = {dout_dzo:.4f}")
    print(f"    delta_o = {dL_dout:.4f} × {dout_dzo:.4f} = {delta_o:.6f}")
    print()

    # 은닉→출력 가중치 기울기
    dL_dw_ho0 = delta_o * h1
    dL_dw_ho1 = delta_o * h2
    dL_db_o = delta_o

    print(f"    dL/dw_ho[0] = delta_o × h1 = {delta_o:.6f} × {h1:.4f} = {dL_dw_ho0:.6f}")
    print(f"    dL/dw_ho[1] = delta_o × h2 = {delta_o:.6f} × {h2:.4f} = {dL_dw_ho1:.6f}")
    print()

    # 은닉층 기울기 (역전파가 한 층 더 거슬러 올라감)
    dL_dh1 = delta_o * w_ho[0]
    dL_dh2 = delta_o * w_ho[1]
    delta_h1 = dL_dh1 * sigmoid_derivative(h1)
    delta_h2 = dL_dh2 * sigmoid_derivative(h2)

    print(f"    delta_h1 = delta_o × w_ho[0] × sigmoid'(h1)")
    print(f"            = {delta_o:.6f} × {w_ho[0]} × {sigmoid_derivative(h1):.4f}")
    print(f"            = {delta_h1:.6f}")
    print(f"    delta_h2 = {delta_h2:.6f}")
    print()

    # --- 가중치 업데이트 ---
    print("  === 3단계: 가중치 업데이트 ===")

    new_w_ho = [w_ho[0] - lr * dL_dw_ho0,
                w_ho[1] - lr * dL_dw_ho1]
    new_b_o = b_o - lr * dL_db_o

    # 입력→은닉 가중치도 업데이트
    new_w_ih = [
        [w_ih[0][0] - lr * delta_h1 * x[0],
         w_ih[0][1] - lr * delta_h2 * x[0]],
        [w_ih[1][0] - lr * delta_h1 * x[1],
         w_ih[1][1] - lr * delta_h2 * x[1]]
    ]

    print(f"    w_ho: {[round(w,4) for w in w_ho]} → {[round(w,4) for w in new_w_ho]}")
    print(f"    b_o:  {b_o} → {new_b_o:.4f}")
    print(f"    w_ih[0]: {w_ih[0]} → {[round(w,4) for w in new_w_ih[0]]}")
    print(f"    w_ih[1]: {w_ih[1]} → {[round(w,4) for w in new_w_ih[1]]}")
    print()

    # 업데이트 후 순전파 다시 해보기
    z_h1_new = x[0]*new_w_ih[0][0] + x[1]*new_w_ih[1][0] + b_h[0]
    z_h2_new = x[0]*new_w_ih[0][1] + x[1]*new_w_ih[1][1] + b_h[1]
    h1_new = sigmoid(z_h1_new)
    h2_new = sigmoid(z_h2_new)
    z_o_new = h1_new*new_w_ho[0] + h2_new*new_w_ho[1] + new_b_o
    output_new = sigmoid(z_o_new)
    loss_new = (target - output_new) ** 2

    print("  === 검증: 업데이트 후 손실이 줄었나? ===")
    print(f"    이전 출력: {output:.4f},  손실: {loss:.6f}")
    print(f"    새 출력:   {output_new:.4f},  손실: {loss_new:.6f}")
    if loss_new < loss:
        print("    → 손실이 줄었습니다! 역전파가 올바른 방향으로 작동했습니다.")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 5: 여러 번 반복(에폭) 학습
# ─────────────────────────────────────────────────────────────────────────

def lesson5_multiple_epochs():
    """
    역전파를 여러 번 반복하면 손실이 점점 줄어드는 것을 봅니다.

    비유: 요리를 여러 번 해보면서 레시피를 조금씩 개선하는 것
          첫 번째 시도보다 열 번째 시도가 더 맛있어지듯이!
    """
    print("=" * 70)
    print("[레슨 5] 여러 번 반복 학습 (에폭)")
    print("=" * 70)
    print()

    # 단순한 1층 뉴런으로 반복 학습
    x = 1.5
    target = 0.8
    w = 0.1
    b = 0.0
    lr = 1.0

    print(f"  목표: sigmoid(w×{x} + b)가 {target}에 가까워지도록 학습")
    print(f"  초기 w={w}, b={b}")
    print()
    print("  ┌───────┬──────────┬──────────┬────────────┐")
    print("  │ 에폭  │   출력   │   손실   │  손실 막대 │")
    print("  ├───────┼──────────┼──────────┼────────────┤")

    for epoch in range(15):
        z = w * x + b
        out = sigmoid(z)
        loss = (target - out) ** 2

        bar = "#" * int(loss * 200)
        if epoch % 1 == 0:
            print(f"  │  {epoch+1:>3}  │ {out:>8.4f} │ {loss:>8.6f} │ {bar:<10} │")

        # 역전파
        dL_dout = -2.0 * (target - out)
        dout_dz = sigmoid_derivative(out)
        dL_dw = dL_dout * dout_dz * x
        dL_db = dL_dout * dout_dz

        w -= lr * dL_dw
        b -= lr * dL_db

    print("  └───────┴──────────┴──────────┴────────────┘")
    print()
    print("  → 에폭이 늘수록 손실이 줄고, 출력이 정답에 가까워집니다!")
    print("  → 이것이 신경망 학습의 핵심 원리입니다.")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■" * 72)
    print("  딥러닝 05단계 : 역전파 (Backpropagation)")
    print("  비유: 요리 레시피를 결과를 보고 거꾸로 되짚어 고치기")
    print("■" * 72)
    print()

    lesson1_chain_rule()
    lesson2_gradient_calculation()
    lesson3_weight_update()
    lesson4_two_layer_backprop()
    lesson5_multiple_epochs()


if __name__ == "__main__":
    main()
