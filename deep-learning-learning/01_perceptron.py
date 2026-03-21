# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [딥러닝] 학습 01단계: 퍼셉트론 (Perceptron)
#   ─ 인공 뉴런, AND/OR/XOR, 학습 알고리즘, 학습률, 수렴 ─
#   ■ 실행 방법: python 01_perceptron.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 뉴런이란? - 생물학적 뉴런 → 인공 뉴런
#   2. 퍼셉트론 구조 - 가중합, 편향, 활성화 함수
#   3. AND/OR 게이트 학습 - 퍼셉트론으로 논리 게이트 구현
#   4. XOR 문제 - 왜 단층으로 안 되는지, MLP 필요성
#   5. 학습 알고리즘 - 가중치 초기화, 예측→에러→업데이트 반복
#   6. 학습률의 영향 - 너무 크면/작으면 어떻게 되는지
#   7. 수렴 시각화 - 에폭별 에러 변화 추적
#   8. 실전: 퍼셉트론으로 간단한 분류기 만들기
#
# ─────────────────────────────────────────────────────────────────────────

import random


def lesson1_neuron():
    # =========================================================================
    #
    #   레슨 1 — 뉴런이란?
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 뉴런이란?                  │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 생물학적 뉴런 → 인공 뉴런
    # ─────────────────────────────────────────────────────────────────────
    #
    #   생물학적 뉴런:
    #     수상돌기(dendrite) → 입력 신호 수신
    #     세포체(cell body)  → 신호 합산 및 처리
    #     축삭돌기(axon)     → 출력 신호 전달
    #     시냅스(synapse)    → 다음 뉴런과의 연결 (강도 = 가중치)
    #
    #   인공 뉴런:
    #     입력(x)    → 데이터
    #     가중치(w)  → 각 입력의 중요도
    #     편향(b)    → 기본 성향
    #     활성화(f)  → 출력 여부 결정
    #

    print("  [생물학적 뉴런 → 인공 뉴런]")
    print()
    print("    생물학적 뉴런          인공 뉴런")
    print("    ──────────────      ──────────────")
    print("    수상돌기 (입력)  →   입력 x1, x2, ...")
    print("    시냅스 (강도)    →   가중치 w1, w2, ...")
    print("    세포체 (합산)    →   가중합 Σ(xi*wi) + b")
    print("    축삭돌기 (출력)  →   활성화 함수 f(z)")
    print()

    # 인공 뉴런의 계산 과정
    print("  [인공 뉴런 계산 과정]")
    print()
    print("    입력: x1=0.8, x2=0.6")
    print("    가중치: w1=0.5, w2=0.3")
    print("    편향: b=0.1")
    print()

    x = [0.8, 0.6]
    w = [0.5, 0.3]
    b = 0.1

    weighted_sum = sum(xi * wi for xi, wi in zip(x, w))
    z = weighted_sum + b
    output = 1 if z >= 0.5 else 0  # 단순 임계값 활성화

    print(f"    가중합: {x[0]}*{w[0]} + {x[1]}*{w[1]} = {weighted_sum:.2f}")
    print(f"    편향 더하기: {weighted_sum:.2f} + {b} = {z:.2f}")
    print(f"    활성화 (임계값 0.5): {z:.2f} >= 0.5? → {'발화!' if output else '억제'}")
    print()

    # 비유
    print("  [비유: 카페에서 커피 주문 결정]")
    print("    입력1: 졸림 정도 (0~1)     × 가중치 0.8 (중요)")
    print("    입력2: 지갑 사정 (0~1)     × 가중치 0.3 (덜 중요)")
    print("    편향: -0.5 (기본적으로 안 마시려는 성향)")
    print("    결과 = 졸림*0.8 + 지갑*0.3 - 0.5")
    print("    결과 > 0 이면 → 커피 주문!")
    print()


def lesson2_perceptron_structure():
    # =========================================================================
    #
    #   레슨 2 — 퍼셉트론 구조
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : 퍼셉트론 구조              │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 퍼셉트론 = 가중합 + 편향 + 계단 함수
    # ─────────────────────────────────────────────────────────────────────
    #
    #   z = w1*x1 + w2*x2 + ... + wn*xn + b   (가중합)
    #   y = step(z) = 1 if z >= 0 else 0       (계단 함수)
    #
    #   계단 함수(Step Function):
    #     입력이 0 이상이면 → 1 출력 (활성화)
    #     입력이 0 미만이면 → 0 출력 (비활성화)
    #

    def step_function(z):
        """계단 함수: z >= 0이면 1, 아니면 0"""
        return 1 if z >= 0 else 0

    def perceptron(x, w, b):
        """퍼셉트론 계산"""
        z = sum(xi * wi for xi, wi in zip(x, w)) + b
        return step_function(z), z

    # 계단 함수 그래프 (ASCII)
    print("  [계단 함수 그래프]")
    print()
    print("    y")
    print("    1 |          ########")
    print("      |          #")
    print("    0 | ########")
    print("      +──────────────────")
    print("         -3  -1  0  1  3   z")
    print()

    # 다양한 입력으로 퍼셉트론 실행
    print("  [퍼셉트론 실행 예제]")
    w = [0.5, 0.3]
    b = -0.4

    print(f"    가중치: w={w}, 편향: b={b}")
    print()

    test_inputs = [[0, 0], [0, 1], [1, 0], [1, 1]]
    print(f"    {'x1':>3} {'x2':>3} | {'z':>7} | {'y':>3}")
    print("    " + "-" * 25)

    for x in test_inputs:
        y, z = perceptron(x, w, b)
        print(f"    {x[0]:>3} {x[1]:>3} | {z:>+7.2f} | {y:>3}")
    print()

    # 편향의 역할
    print("  [편향(bias)의 역할]")
    print()
    print("    편향 없으면 (b=0): 결정 경계가 반드시 원점을 지남")
    print("    편향 있으면: 결정 경계를 좌/우로 이동 가능")
    print()
    print("    b > 0: 활성화되기 쉬워짐 (기본적으로 '예')")
    print("    b < 0: 활성화되기 어려워짐 (기본적으로 '아니오')")
    print()


def lesson3_and_or_gate():
    # =========================================================================
    #
    #   레슨 3 — AND/OR 게이트 학습
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : AND/OR 게이트 학습         │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 논리 게이트를 퍼셉트론으로 구현
    # ─────────────────────────────────────────────────────────────────────
    #
    #   AND 진리표:        OR 진리표:
    #   x1 x2 | y          x1 x2 | y
    #    0  0  | 0           0  0  | 0
    #    0  1  | 0           0  1  | 1
    #    1  0  | 0           1  0  | 1
    #    1  1  | 1           1  1  | 1
    #

    def step(z):
        return 1 if z >= 0 else 0

    def perceptron_predict(x, w, b):
        z = sum(xi * wi for xi, wi in zip(x, w)) + b
        return step(z)

    inputs = [[0, 0], [0, 1], [1, 0], [1, 1]]

    # AND 게이트: w1=0.5, w2=0.5, b=-0.7
    # z = 0.5*x1 + 0.5*x2 - 0.7
    # (1,1) → 0.3 → 1, 나머지 → 음수 → 0
    w_and = [0.5, 0.5]
    b_and = -0.7

    print("  [AND 게이트]")
    print(f"    w={w_and}, b={b_and}")
    print(f"    {'x1':>4} {'x2':>4} | {'z':>7} | {'예측':>4} | {'정답':>4}")
    print("    " + "-" * 35)

    and_truth = [0, 0, 0, 1]
    for i, x in enumerate(inputs):
        z = sum(xi * wi for xi, wi in zip(x, w_and)) + b_and
        pred = step(z)
        check = "O" if pred == and_truth[i] else "X"
        print(f"    {x[0]:>4} {x[1]:>4} | {z:>+7.2f} | {pred:>4} | {and_truth[i]:>4} {check}")
    print()

    # OR 게이트: w1=0.5, w2=0.5, b=-0.2
    w_or = [0.5, 0.5]
    b_or = -0.2

    print("  [OR 게이트]")
    print(f"    w={w_or}, b={b_or}")
    print(f"    {'x1':>4} {'x2':>4} | {'z':>7} | {'예측':>4} | {'정답':>4}")
    print("    " + "-" * 35)

    or_truth = [0, 1, 1, 1]
    for i, x in enumerate(inputs):
        z = sum(xi * wi for xi, wi in zip(x, w_or)) + b_or
        pred = step(z)
        check = "O" if pred == or_truth[i] else "X"
        print(f"    {x[0]:>4} {x[1]:>4} | {z:>+7.2f} | {pred:>4} | {or_truth[i]:>4} {check}")
    print()

    # NAND 게이트: AND의 반대
    w_nand = [-0.5, -0.5]
    b_nand = 0.7

    print("  [NAND 게이트] (AND의 반대)")
    print(f"    w={w_nand}, b={b_nand}")
    nand_truth = [1, 1, 1, 0]
    for i, x in enumerate(inputs):
        pred = perceptron_predict(x, w_nand, b_nand)
        check = "O" if pred == nand_truth[i] else "X"
        print(f"    {x[0]:>4} {x[1]:>4} | 예측={pred} | 정답={nand_truth[i]} {check}")
    print()

    print("  → AND, OR, NAND 모두 퍼셉트론 하나로 구현 가능!")
    print()


def lesson4_xor_problem():
    # =========================================================================
    #
    #   레슨 4 — XOR 문제
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : XOR 문제                   │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ XOR 진리표:
    #   x1 x2 | y
    #    0  0  | 0
    #    0  1  | 1
    #    1  0  | 1
    #    1  1  | 0
    #
    # ■ 왜 단층 퍼셉트론으로 안 되는가?
    #   직선 하나로는 (0,0)/(1,1)과 (0,1)/(1,0)을 분리할 수 없다!
    #
    #   시각적으로:
    #     x2
    #     1 | O(0,1)    X(1,1)
    #       |
    #     0 | X(0,0)    O(1,0)
    #       +──────────────
    #         0          1   x1
    #
    #   O끼리, X끼리 직선 하나로 나눌 수 없다!
    #

    def step(z):
        return 1 if z >= 0 else 0

    inputs = [[0, 0], [0, 1], [1, 0], [1, 1]]
    xor_truth = [0, 1, 1, 0]

    print("  [XOR을 단층 퍼셉트론으로 시도]")
    print()
    print("    x2")
    print("    1 | 1(0,1)    0(1,1)")
    print("      |")
    print("    0 | 0(0,0)    1(1,0)")
    print("      +──────────────────")
    print("        0          1   x1")
    print()
    print("    → 직선 하나로 1과 0을 분리 불가능!")
    print()

    # 여러 가중치 시도
    print("  [다양한 가중치로 시도]")
    attempts = [
        ([1, 1], -0.5, "w=[1,1], b=-0.5"),
        ([1, 1], -1.5, "w=[1,1], b=-1.5"),
        ([-1, 1], 0.5, "w=[-1,1], b=0.5"),
        ([1, -1], 0.5, "w=[1,-1], b=0.5"),
    ]

    for w, b, desc in attempts:
        preds = [step(sum(xi * wi for xi, wi in zip(x, w)) + b) for x in inputs]
        correct = sum(1 for p, t in zip(preds, xor_truth) if p == t)
        print(f"    {desc}: 예측={preds}, 정답={xor_truth}, 맞은 수={correct}/4")
    print()
    print("    → 어떤 가중치를 써도 4개 모두 맞출 수 없다!")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 해결: 다층 퍼셉트론 (MLP)
    # ─────────────────────────────────────────────────────────────────────
    print("  [해결: 다층 퍼셉트론 (MLP)]")
    print()
    print("    XOR = NAND AND OR 조합!")
    print("    NAND(x1,x2) AND OR(x1,x2) = XOR(x1,x2)")
    print()

    # XOR을 NAND + OR로 구현
    def nand(x1, x2):
        return step(-0.5 * x1 - 0.5 * x2 + 0.7)

    def or_gate(x1, x2):
        return step(0.5 * x1 + 0.5 * x2 - 0.2)

    def and_gate(x1, x2):
        return step(0.5 * x1 + 0.5 * x2 - 0.7)

    def xor_gate(x1, x2):
        s1 = nand(x1, x2)     # 1층: NAND
        s2 = or_gate(x1, x2)  # 1층: OR
        return and_gate(s1, s2)  # 2층: AND

    print(f"    {'x1':>4} {'x2':>4} | {'NAND':>5} {'OR':>4} | {'AND(XOR)':>9} | {'정답':>4}")
    print("    " + "-" * 45)

    for i, (x1, x2) in enumerate(inputs):
        s1 = nand(x1, x2)
        s2 = or_gate(x1, x2)
        result = and_gate(s1, s2)
        check = "O" if result == xor_truth[i] else "X"
        print(f"    {x1:>4} {x2:>4} | {s1:>5} {s2:>4} | {result:>9} | {xor_truth[i]:>4} {check}")
    print()
    print("    → 2층으로 만들면 XOR 해결! 이것이 딥러닝의 시작!")
    print()


def lesson5_learning_algorithm():
    # =========================================================================
    #
    #   레슨 5 — 학습 알고리즘
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 학습 알고리즘              │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 퍼셉트론 학습 규칙
    # ─────────────────────────────────────────────────────────────────────
    #
    #   1. 가중치를 랜덤으로 초기화
    #   2. 각 데이터에 대해:
    #      a. 예측값 계산: y_pred = step(w*x + b)
    #      b. 오차 계산: error = y_true - y_pred
    #      c. 가중치 업데이트:
    #         wi = wi + lr * error * xi
    #         b  = b  + lr * error
    #   3. 모든 데이터를 맞출 때까지 반복 (에폭)
    #
    #   핵심 아이디어:
    #     error = 0 (맞았으면) → 업데이트 없음
    #     error = 1 (1인데 0으로 예측) → 가중치 증가
    #     error = -1 (0인데 1로 예측) → 가중치 감소
    #

    def step(z):
        return 1 if z >= 0 else 0

    # AND 게이트 학습
    X = [[0, 0], [0, 1], [1, 0], [1, 1]]
    y = [0, 0, 0, 1]

    lr = 0.1
    w = [0.0, 0.0]
    b = 0.0

    print("  [AND 게이트 학습 과정]")
    print(f"    초기 가중치: w={w}, b={b}")
    print(f"    학습률: {lr}")
    print()

    for epoch in range(10):
        errors = 0
        details = []
        for i in range(len(X)):
            z = sum(xi * wi for xi, wi in zip(X[i], w)) + b
            pred = step(z)
            error = y[i] - pred

            if error != 0:
                # 가중치 업데이트
                for j in range(len(w)):
                    w[j] = w[j] + lr * error * X[i][j]
                b = b + lr * error
                errors += 1
                details.append(f"x={X[i]}, pred={pred}, true={y[i]}, "
                              f"error={error:+d}")

        if epoch < 5 or errors == 0:
            preds = [step(sum(xi * wi for xi, wi in zip(x, w)) + b) for x in X]
            print(f"    에폭 {epoch+1}: 예측={preds}, 오류={errors}건, "
                  f"w=[{w[0]:.1f},{w[1]:.1f}], b={b:.1f}")

        if errors == 0:
            print(f"\n    → {epoch+1}번째 에폭에서 수렴! 모든 데이터 정확!")
            break
    print()

    # 최종 검증
    print("  [최종 검증]")
    for i in range(len(X)):
        z = sum(xi * wi for xi, wi in zip(X[i], w)) + b
        pred = step(z)
        print(f"    {X[i]} → z={z:.1f}, 예측={pred}, 정답={y[i]}")
    print()


def lesson6_learning_rate():
    # =========================================================================
    #
    #   레슨 6 — 학습률의 영향
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 학습률의 영향              │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 학습률(Learning Rate): 한 번에 얼마나 크게 업데이트할지
    # ─────────────────────────────────────────────────────────────────────
    #
    #   너무 크면: 최적점을 지나쳐서 왔다갔다 (진동/발산)
    #   너무 작으면: 수렴은 하지만 너무 느림
    #   적당하면: 빠르게 수렴!
    #
    #   비유: 산에서 내려올 때
    #     lr 큼: 큰 보폭 → 빨리 내려가지만 골짜기를 지나칠 수 있음
    #     lr 작음: 아기 걸음 → 안전하지만 해가 질 때까지 못 내려옴
    #

    def step(z):
        return 1 if z >= 0 else 0

    X = [[0, 0], [0, 1], [1, 0], [1, 1]]
    y = [0, 0, 0, 1]

    print("  [다양한 학습률로 AND 게이트 학습]")
    print()

    for lr in [0.01, 0.1, 0.5, 1.0]:
        w = [0.0, 0.0]
        b = 0.0
        converged_at = -1

        for epoch in range(100):
            errors = 0
            for i in range(len(X)):
                z = sum(xi * wi for xi, wi in zip(X[i], w)) + b
                pred = step(z)
                error = y[i] - pred
                if error != 0:
                    for j in range(len(w)):
                        w[j] += lr * error * X[i][j]
                    b += lr * error
                    errors += 1

            if errors == 0:
                converged_at = epoch + 1
                break

        if converged_at > 0:
            print(f"    lr={lr:.2f}: {converged_at:>3}번째 에폭에서 수렴, "
                  f"최종 w=[{w[0]:.2f},{w[1]:.2f}], b={b:.2f}")
        else:
            print(f"    lr={lr:.2f}: 100번 에폭 내에 수렴 실패")
    print()

    # 학습률 선택 가이드
    print("  [학습률 선택 가이드]")
    print("    0.001 ~ 0.01 : 안전하지만 느림")
    print("    0.01  ~ 0.1  : 일반적으로 좋은 시작점")
    print("    0.1   ~ 1.0  : 빠르지만 불안정할 수 있음")
    print("    1.0+          : 대부분 발산 → 비추천")
    print()


def lesson7_convergence():
    # =========================================================================
    #
    #   레슨 7 — 수렴 시각화
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 수렴 시각화                │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 에폭별 에러 개수 변화를 추적하여 학습 진행 상황 확인
    # ─────────────────────────────────────────────────────────────────────

    def step(z):
        return 1 if z >= 0 else 0

    # OR 게이트 학습
    X = [[0, 0], [0, 1], [1, 0], [1, 1]]
    y = [0, 1, 1, 1]

    lr = 0.1
    w = [0.0, 0.0]
    b = 0.0

    error_history = []
    weight_history = []

    for epoch in range(20):
        epoch_errors = 0
        for i in range(len(X)):
            z = sum(xi * wi for xi, wi in zip(X[i], w)) + b
            pred = step(z)
            error = y[i] - pred
            if error != 0:
                for j in range(len(w)):
                    w[j] += lr * error * X[i][j]
                b += lr * error
                epoch_errors += 1

        error_history.append(epoch_errors)
        weight_history.append((w[0], w[1], b))

        if epoch_errors == 0:
            break

    print("  [OR 게이트 학습 - 에러 변화 그래프]")
    print()

    max_err = max(error_history) if error_history else 1
    for i, err in enumerate(error_history):
        bar = "#" * (err * 10) if err > 0 else ""
        print(f"    에폭 {i+1:>2}: 에러={err} {bar}")
    print()

    print("  [가중치 변화 추적]")
    print(f"    {'에폭':>4} | {'w1':>6} | {'w2':>6} | {'b':>6}")
    print("    " + "-" * 30)
    for i, (w1, w2, bias) in enumerate(weight_history):
        print(f"    {i+1:>4} | {w1:>6.2f} | {w2:>6.2f} | {bias:>6.2f}")
    print()

    # 학습 곡선 해석
    print("  [학습 곡선 해석]")
    print("    에러가 감소 → 학습이 진행 중")
    print("    에러가 0    → 수렴 완료!")
    print("    에러가 오르내림 → 학습률이 너무 크거나 데이터 문제")
    print()


def lesson8_practice():
    # =========================================================================
    #
    #   레슨 8 — 실전: 퍼셉트론 분류기
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 8 : 퍼셉트론 분류기 만들기     │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 문제: 학생의 공부시간과 수면시간으로 합격 여부 예측
    # ─────────────────────────────────────────────────────────────────────

    # 학습 데이터 (공부시간은 /10, 수면시간은 /10으로 정규화)
    train_X = [
        [0.1, 0.8],  # 공부 적음, 수면 많음 → 불합격
        [0.2, 0.3],  # 공부 적음, 수면 적음 → 불합격
        [0.3, 0.5],  # 공부 보통, 수면 보통 → 불합격
        [0.6, 0.7],  # 공부 많음, 수면 많음 → 합격
        [0.7, 0.5],  # 공부 많음, 수면 보통 → 합격
        [0.9, 0.8],  # 공부 아주 많음       → 합격
        [0.8, 0.6],  # 공부 많음            → 합격
        [0.4, 0.4],  # 공부 중간            → 불합격
    ]
    train_y = [0, 0, 0, 1, 1, 1, 1, 0]

    def step(z):
        return 1 if z >= 0 else 0

    # 학습
    random.seed(42)
    w = [random.uniform(-0.5, 0.5) for _ in range(2)]
    b = random.uniform(-0.5, 0.5)
    lr = 0.5

    print(f"  초기 가중치: w=[{w[0]:.3f}, {w[1]:.3f}], b={b:.3f}")
    print(f"  학습률: {lr}")
    print()

    print("  [학습 과정]")
    for epoch in range(50):
        errors = 0
        for i in range(len(train_X)):
            z = sum(xi * wi for xi, wi in zip(train_X[i], w)) + b
            pred = step(z)
            error = train_y[i] - pred
            if error != 0:
                for j in range(len(w)):
                    w[j] += lr * error * train_X[i][j]
                b += lr * error
                errors += 1

        if epoch < 5 or epoch % 10 == 9 or errors == 0:
            print(f"    에폭 {epoch+1:>2}: 에러={errors}, "
                  f"w=[{w[0]:.3f}, {w[1]:.3f}], b={b:.3f}")

        if errors == 0:
            print(f"\n    → {epoch+1}번째 에폭에서 수렴!")
            break
    print()

    # 학습 결과 검증
    print("  [학습 데이터 검증]")
    print(f"    {'공부':>6} {'수면':>6} | {'예측':>4} | {'정답':>4}")
    print("    " + "-" * 30)

    correct = 0
    for i in range(len(train_X)):
        z = sum(xi * wi for xi, wi in zip(train_X[i], w)) + b
        pred = step(z)
        if pred == train_y[i]:
            correct += 1
        tag_pred = "합격" if pred == 1 else "불합"
        tag_true = "합격" if train_y[i] == 1 else "불합"
        mark = "O" if pred == train_y[i] else "X"
        print(f"    {train_X[i][0]:>6.1f} {train_X[i][1]:>6.1f} | {tag_pred:>4} | {tag_true:>4} {mark}")

    print(f"\n    정확도: {correct}/{len(train_X)} = {correct/len(train_X)*100:.0f}%")
    print()

    # 새 학생 예측
    print("  [새 학생 예측]")
    new_students = [
        ([0.5, 0.6], "공부5h, 수면6h"),
        ([0.8, 0.9], "공부8h, 수면9h"),
        ([0.2, 0.7], "공부2h, 수면7h"),
        ([0.6, 0.4], "공부6h, 수면4h"),
    ]

    for features, desc in new_students:
        z = sum(xi * wi for xi, wi in zip(features, w)) + b
        pred = step(z)
        result = "합격" if pred == 1 else "불합격"
        print(f"    {desc} → {result} (z={z:.3f})")
    print()

    print("  [퍼셉트론의 한계]")
    print("    1. 선형 분리 가능한 문제만 풀 수 있다")
    print("    2. XOR 같은 비선형 문제 불가")
    print("    3. 확률이 아닌 0/1만 출력")
    print("    → 다음 단계: 활성화 함수(02_activation.py)로 확장!")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# ■ 메인 실행
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 72)
    print("  [딥러닝] 01단계: 퍼셉트론 (Perceptron)")
    print("=" * 72)
    print()

    lesson1_neuron()
    lesson2_perceptron_structure()
    lesson3_and_or_gate()
    lesson4_xor_problem()
    lesson5_learning_algorithm()
    lesson6_learning_rate()
    lesson7_convergence()
    lesson8_practice()

    print("=" * 72)
    print("  01단계 완료! 다음: 02_activation.py")
    print("=" * 72)


if __name__ == "__main__":
    main()
