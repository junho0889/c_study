# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [딥러닝] 학습 02단계: 활성화 함수 (Activation Functions)
#   ─ Sigmoid, Tanh, ReLU, Leaky ReLU, ELU, GELU, Softmax ─
#   ■ 실행 방법: python 02_activation.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 활성화 함수가 왜 필요한가? - 비선형성
#   2. 시그모이드(Sigmoid) - 공식, 장단점, 기울기 소실
#   3. 하이퍼볼릭 탄젠트(tanh) - 시그모이드와 비교
#   4. ReLU - 장점, 죽은 뉴런 문제
#   5. Leaky ReLU, ELU, GELU - ReLU 변형들
#   6. Softmax - 다중 클래스, 확률 합=1
#   7. 활성화 함수 선택 가이드
#   8. 실전: 모든 활성화 함수 비교 시각화(ASCII)
#
# ─────────────────────────────────────────────────────────────────────────


def lesson1_why_activation():
    # =========================================================================
    #
    #   레슨 1 — 활성화 함수가 왜 필요한가?
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 왜 활성화 함수가 필요한가? │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 비선형성이 없으면 층을 아무리 쌓아도 하나의 선형 변환!
    # ─────────────────────────────────────────────────────────────────────
    #
    #   선형 변환만 있는 2층 네트워크:
    #     z1 = w1 * x + b1    (1층)
    #     z2 = w2 * z1 + b2   (2층)
    #
    #   풀어쓰면:
    #     z2 = w2 * (w1 * x + b1) + b2
    #        = (w2*w1) * x + (w2*b1 + b2)
    #        = W * x + B
    #
    #   → 아무리 층을 쌓아도 결국 y = Wx + B (하나의 직선!)
    #   → 비선형 활성화 함수가 있어야 곡선을 표현할 수 있다
    #

    print("  [활성화 함수 없이 2층 쌓기]")
    print()

    # 2층 선형 변환
    w1, b1 = 3.0, 1.0   # 1층
    w2, b2 = 2.0, -1.0  # 2층

    print(f"    1층: z1 = {w1}*x + {b1}")
    print(f"    2층: z2 = {w2}*z1 + {b2}")
    print(f"    합치면: z2 = {w2}*({w1}*x + {b1}) + {b2}")
    print(f"           = {w2*w1}*x + {w2*b1 + b2}")
    print(f"    → 결국 하나의 직선 y = {w2*w1}x + {w2*b1 + b2}")
    print()

    # 수치 확인
    print("    수치 확인:")
    for x in [-2, -1, 0, 1, 2]:
        z1 = w1 * x + b1
        z2 = w2 * z1 + b2
        direct = (w2 * w1) * x + (w2 * b1 + b2)
        print(f"      x={x:>2}: 2층 거침={z2:.1f}, 1층 직접={direct:.1f} → 같다!")
    print()

    # 활성화 함수가 있으면
    print("  [ReLU 활성화 함수를 넣으면]")
    print()
    print("    1층: z1 = ReLU(3*x + 1)")
    print("    2층: z2 = 2*z1 - 1")
    print()
    for x in [-2, -1, 0, 1, 2]:
        z1 = max(0, w1 * x + b1)  # ReLU
        z2 = w2 * z1 + b2
        print(f"      x={x:>2}: z1={z1:.1f}, z2={z2:.1f}")
    print()
    print("    → x=-2,-1에서 z2가 같아져서 '꺾인 직선' 형태!")
    print("    → 비선형! 층을 더 쌓으면 더 복잡한 패턴 표현 가능!")
    print()


def lesson2_sigmoid():
    # =========================================================================
    #
    #   레슨 2 — 시그모이드 (Sigmoid)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : 시그모이드 (Sigmoid)       │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ sigmoid(z) = 1 / (1 + e^(-z))
    # ─────────────────────────────────────────────────────────────────────
    #
    #   출력 범위: (0, 1) → 확률로 해석 가능
    #
    #   특징:
    #     z → +∞: sigmoid → 1
    #     z → -∞: sigmoid → 0
    #     z = 0:  sigmoid = 0.5
    #
    #   미분:
    #     sigmoid'(z) = sigmoid(z) * (1 - sigmoid(z))
    #     최대 미분값 = 0.25 (z=0일 때)
    #

    def sigmoid(z):
        z = max(-500, min(500, z))
        return 1.0 / (1.0 + math.exp(-z))

    def sigmoid_derivative(z):
        s = sigmoid(z)
        return s * (1 - s)

    # ASCII 그래프
    print("  [시그모이드 함수 그래프]")
    print()
    width = 50
    for row in range(10, -1, -1):
        y_val = row / 10  # 0.0 ~ 1.0
        line = f"  {y_val:.1f} |"
        for col in range(-25, 26):
            z = col / 4  # -6.25 ~ 6.25
            s = sigmoid(z)
            if abs(s - y_val) < 0.06:
                line += "*"
            else:
                line += " "
        print(line)
    print("       " + "-" * 51)
    print("       -6        -3         0         3         6")
    print()

    # 수치 테이블
    print("  [수치 테이블]")
    print(f"    {'z':>5} | {'sigmoid(z)':>10} | {'미분':>10} | 시각화")
    print("    " + "-" * 50)
    for z in [-5, -3, -1, 0, 1, 3, 5]:
        s = sigmoid(z)
        d = sigmoid_derivative(z)
        bar = "#" * int(s * 30)
        print(f"    {z:>+5.1f} | {s:>10.6f} | {d:>10.6f} | {bar}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 기울기 소실 문제 (Vanishing Gradient)
    # ─────────────────────────────────────────────────────────────────────
    print("  [기울기 소실 문제]")
    print()
    print("    시그모이드 미분의 최대값 = 0.25 (z=0)")
    print("    층이 깊어질수록 기울기가 곱해지면서 점점 작아진다!")
    print()
    print("    5층 네트워크 기울기 예시:")

    grad = 1.0
    for layer in range(1, 6):
        grad *= 0.25  # 최대 미분값
        print(f"      {layer}층 통과 후: {grad:.6f}")
    print()
    print("    → 5층만 통과해도 기울기가 0.001 이하로 줄어든다!")
    print("    → 앞쪽 층의 가중치가 거의 업데이트 안 됨 = 학습 불가")
    print()

    # 장단점 정리
    print("  [시그모이드 장단점]")
    print("    장점: 출력이 0~1 → 확률 해석 가능")
    print("    장점: 매끄러운 곡선 → 미분 가능")
    print("    단점: 기울기 소실 (깊은 네트워크에서)")
    print("    단점: 출력 중심이 0이 아님 (0.5 중심)")
    print("    단점: exp 계산이 비교적 느림")
    print("    용도: 출력층의 이진 분류 (은닉층에는 비추천)")
    print()


def lesson3_tanh():
    # =========================================================================
    #
    #   레슨 3 — 하이퍼볼릭 탄젠트 (tanh)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : tanh                       │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ tanh(z) = (e^z - e^(-z)) / (e^z + e^(-z))
    #           = 2 * sigmoid(2z) - 1
    # ─────────────────────────────────────────────────────────────────────
    #
    #   출력 범위: (-1, 1) → 0 중심!
    #   시그모이드와의 관계: tanh(z) = 2*sigmoid(2z) - 1
    #
    #   시그모이드보다 좋은 점:
    #     출력이 0 중심 → 다음 층 입력의 평균이 0에 가까움
    #     → 학습이 더 안정적
    #

    # 수치 비교
    def sigmoid(z):
        z = max(-500, min(500, z))
        return 1.0 / (1.0 + math.exp(-z))

    print("  [sigmoid vs tanh 비교]")
    print()
    print(f"    {'z':>5} | {'sigmoid':>8} | {'tanh':>8} | sigmoid 그래프      | tanh 그래프")
    print("    " + "-" * 75)

    for z in [-4, -3, -2, -1, 0, 1, 2, 3, 4]:
        s = sigmoid(z)
        t = math.tanh(z)

        # sigmoid 바 (0~1 범위를 0~20칸으로)
        s_bar = "#" * int(s * 20)

        # tanh 바 (-1~1 범위를 10칸 중심으로)
        t_pos = int((t + 1) / 2 * 20)
        t_bar = " " * min(10, t_pos) + "#" * abs(t_pos - 10) if t_pos >= 10 else " " * t_pos + "#" * (10 - t_pos)

        print(f"    {z:>+5.1f} | {s:>8.4f} | {t:>+8.4f} | {s_bar:<20} | {t_bar}")
    print()

    # 핵심 차이
    print("  [핵심 차이]")
    print("    sigmoid: 출력 범위 (0, 1),  중심 0.5")
    print("    tanh:    출력 범위 (-1, 1), 중심 0.0 ← 이게 좋다!")
    print()
    print("    0 중심이 왜 좋은가?")
    print("    → 다음 층의 입력이 양수/음수 균형 → 가중치 업데이트 방향 다양")
    print("    → sigmoid는 항상 양수 출력 → 업데이트 방향이 편향됨")
    print()

    # tanh도 기울기 소실 존재
    print("  [tanh의 한계]")
    print("    tanh 미분의 최대값 = 1.0 (z=0)")
    print("    z가 크거나 작으면 미분 → 0 (포화)")
    print("    → 기울기 소실 문제는 여전히 존재 (sigmoid보다는 나음)")
    print()


def lesson4_relu():
    # =========================================================================
    #
    #   레슨 4 — ReLU (Rectified Linear Unit)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : ReLU                       │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ ReLU(z) = max(0, z)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   z > 0 이면 → z 그대로 출력
    #   z <= 0 이면 → 0 출력
    #
    #   미분:
    #     z > 0: 미분 = 1 (기울기 1 → 기울기 소실 없음!)
    #     z < 0: 미분 = 0 (완전 차단)
    #     z = 0: 수학적으로 미분 불가, 실무에서는 0으로 처리
    #

    def relu(z):
        return max(0, z)

    def relu_derivative(z):
        return 1 if z > 0 else 0

    print("  [ReLU 함수]")
    print("    ReLU(z) = max(0, z)")
    print()

    # ASCII 그래프
    print("  [ReLU 그래프]")
    print()
    for y in range(5, -1, -1):
        line = f"  {y:>2} |"
        for x_val in range(-5, 6):
            r = relu(x_val)
            if r == y:
                line += " * "
            elif x_val <= 0 and y == 0:
                line += " * "
            else:
                line += "   "
        print(line)
    print("     +" + "---" * 11)
    print("      -5 -4 -3 -2 -1  0  1  2  3  4  5")
    print()

    # 수치 테이블
    print("  [수치 테이블]")
    print(f"    {'z':>5} | {'ReLU(z)':>8} | {'미분':>5}")
    print("    " + "-" * 28)
    for z in [-3, -2, -1, 0, 1, 2, 3]:
        r = relu(z)
        d = relu_derivative(z)
        print(f"    {z:>+5.1f} | {r:>8.1f} | {d:>5}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ ReLU의 장점
    # ─────────────────────────────────────────────────────────────────────
    print("  [ReLU 장점]")
    print("    1. 계산이 매우 빠름 (max만 하면 됨, exp 없음)")
    print("    2. 양수 영역에서 미분=1 → 기울기 소실 없음!")
    print("    3. 희소 활성화: 음수 입력은 0 → 네트워크가 가벼워짐")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 죽은 뉴런 문제 (Dead Neuron Problem)
    # ─────────────────────────────────────────────────────────────────────
    print("  [죽은 뉴런 문제 (Dead Neuron)]")
    print()
    print("    z가 항상 음수인 뉴런 → ReLU 출력 항상 0")
    print("    미분도 항상 0 → 가중치 업데이트 불가 → 영원히 죽음!")
    print()
    print("    원인:")
    print("    - 가중치 초기화가 나빴을 때")
    print("    - 학습률이 너무 클 때 (가중치가 큰 음수로 갈 수 있음)")
    print()
    print("    해결:")
    print("    - Leaky ReLU, ELU 등 변형 사용")
    print("    - 적절한 가중치 초기화 (He 초기화)")
    print()


def lesson5_relu_variants():
    # =========================================================================
    #
    #   레슨 5 — ReLU 변형들: Leaky ReLU, ELU, GELU
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : ReLU 변형들                │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Leaky ReLU: 음수 영역에서도 작은 기울기 허용
    #   LeakyReLU(z) = z if z > 0 else alpha * z  (alpha = 0.01)
    #
    # ■ ELU (Exponential Linear Unit):
    #   ELU(z) = z if z > 0 else alpha * (e^z - 1)
    #   음수 영역이 매끄럽고 포화됨
    #
    # ■ GELU (Gaussian Error Linear Unit):
    #   GELU(z) = z * Φ(z)  (Φ = 정규분포 CDF)
    #   최신 모델(GPT, BERT)에서 사용
    # ─────────────────────────────────────────────────────────────────────

    def relu(z):
        return max(0, z)

    def leaky_relu(z, alpha=0.01):
        return z if z > 0 else alpha * z

    def elu(z, alpha=1.0):
        return z if z > 0 else alpha * (math.exp(z) - 1)

    def gelu(z):
        # 근사: z * sigmoid(1.702 * z)
        return z * (1.0 / (1.0 + math.exp(-1.702 * z)))

    # 비교 테이블
    print("  [ReLU 변형 비교]")
    print()
    print(f"    {'z':>5} | {'ReLU':>7} | {'Leaky':>7} | {'ELU':>7} | {'GELU':>7}")
    print("    " + "-" * 50)

    for z in [-3, -2, -1, -0.5, 0, 0.5, 1, 2, 3]:
        r = relu(z)
        lr = leaky_relu(z)
        e = elu(z)
        g = gelu(z)
        print(f"    {z:>+5.1f} | {r:>7.3f} | {lr:>+7.3f} | {e:>+7.3f} | {g:>+7.3f}")
    print()

    # 각 함수의 특징
    print("  [각 변형의 특징]")
    print()
    print("  Leaky ReLU:")
    print("    f(z) = z (z>0), 0.01*z (z<=0)")
    print("    장점: 죽은 뉴런 방지 (음수에서도 작은 기울기)")
    print("    단점: alpha 값을 직접 정해야 함")
    print()
    print("  ELU:")
    print("    f(z) = z (z>0), alpha*(e^z - 1) (z<=0)")
    print("    장점: 출력 평균이 0에 가까움, 매끄러운 곡선")
    print("    단점: exp 계산이 느림")
    print()
    print("  GELU:")
    print("    f(z) = z * CDF(z)")
    print("    장점: GPT, BERT 등 최신 모델에서 사용")
    print("    특징: 확률적 개념 (입력이 얼마나 '큰지'에 따라 통과)")
    print()


def lesson6_softmax():
    # =========================================================================
    #
    #   레슨 6 — Softmax
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : Softmax                    │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Softmax: 여러 출력을 "확률 분포"로 변환
    # ─────────────────────────────────────────────────────────────────────
    #
    #   softmax(zi) = e^zi / Σ(e^zj)
    #
    #   특징:
    #     모든 출력이 0~1 사이
    #     모든 출력의 합 = 1 (확률의 조건!)
    #
    #   용도: 다중 클래스 분류의 출력층
    #     예) 개(0.7), 고양이(0.2), 새(0.1) → 가장 높은 '개' 선택
    #

    def softmax(z_list):
        """오버플로우 방지를 위해 최대값을 뺀다"""
        max_z = max(z_list)
        exp_z = [math.exp(z - max_z) for z in z_list]
        sum_exp = sum(exp_z)
        return [e / sum_exp for e in exp_z]

    # 예제 1: 과일 분류
    print("  [Softmax 예제: 과일 분류]")
    print()
    classes = ["사과", "바나나", "포도"]
    logits = [2.0, 1.0, 0.5]

    print(f"    로짓 (네트워크 출력): {logits}")
    print(f"    클래스: {classes}")
    print()

    probs = softmax(logits)
    print("    Softmax 변환 과정:")
    max_z = max(logits)
    exp_vals = [math.exp(z - max_z) for z in logits]
    sum_exp = sum(exp_vals)
    for i, (cls, logit) in enumerate(zip(classes, logits)):
        print(f"      e^{logit} = {exp_vals[i]:.4f}")
    print(f"      합계: {sum_exp:.4f}")
    print()

    for cls, prob in zip(classes, probs):
        bar = "#" * int(prob * 40)
        print(f"      {cls:>4}: {prob:.4f} ({prob*100:.1f}%) {bar}")

    print(f"\n      확률 합계: {sum(probs):.6f} (= 1.0)")
    print()

    # 예제 2: 온도(temperature) 효과
    print("  [Softmax 온도(Temperature) 효과]")
    print()
    print("    T=1: 기본 → 차이가 적당히 유지")
    print("    T<1: 날카롭게 → 가장 큰 값에 집중")
    print("    T>1: 부드럽게 → 균등에 가까워짐")
    print()

    for temp in [0.5, 1.0, 2.0, 5.0]:
        scaled = [z / temp for z in logits]
        probs_t = softmax(scaled)
        bars = "  ".join(f"{p:.3f}" for p in probs_t)
        print(f"    T={temp:.1f}: [{bars}]")
    print()


def lesson7_selection_guide():
    # =========================================================================
    #
    #   레슨 7 — 활성화 함수 선택 가이드
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 선택 가이드                │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 은닉층(Hidden Layer) 추천
    # ─────────────────────────────────────────────────────────────────────
    print("  [은닉층 활성화 함수 추천]")
    print()
    print("    1순위: ReLU         → 기본! 대부분 여기서 시작")
    print("    2순위: Leaky ReLU   → 죽은 뉴런이 걱정될 때")
    print("    3순위: GELU         → Transformer 계열 모델")
    print("    4순위: ELU          → 출력 평균 0이 중요할 때")
    print("    비추천: Sigmoid/Tanh → 기울기 소실 위험")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 출력층(Output Layer) 추천
    # ─────────────────────────────────────────────────────────────────────
    print("  [출력층 활성화 함수 추천]")
    print()
    print("    ┌───────────────────┬──────────────┬───────────────┐")
    print("    │ 문제 유형         │ 활성화 함수  │ 출력 범위     │")
    print("    ├───────────────────┼──────────────┼───────────────┤")
    print("    │ 이진 분류         │ Sigmoid      │ (0, 1)        │")
    print("    │ 다중 클래스 분류  │ Softmax      │ (0,1), 합=1   │")
    print("    │ 회귀              │ 없음 (선형)  │ (-inf, +inf)  │")
    print("    │ 회귀 (양수만)     │ ReLU         │ [0, +inf)     │")
    print("    └───────────────────┴──────────────┴───────────────┘")
    print()

    # 자주 하는 실수
    print("  [자주 하는 실수]")
    print("    1. 은닉층에 Sigmoid 사용 → 기울기 소실!")
    print("    2. 회귀 출력에 ReLU 사용 → 음수 예측 불가!")
    print("    3. 이진 분류에 Softmax 사용 → 불필요하게 복잡")
    print("    4. 다중 분류에 Sigmoid 사용 → 확률 합이 1이 안 됨!")
    print()


def lesson8_practice():
    # =========================================================================
    #
    #   레슨 8 — 실전: 모든 활성화 함수 비교 시각화
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 8 : 전체 비교 시각화           │")
    print("└──────────────────────────────────────┘")
    print()

    def sigmoid(z):
        z = max(-500, min(500, z))
        return 1.0 / (1.0 + math.exp(-z))

    def relu(z):
        return max(0, z)

    def leaky_relu(z, alpha=0.01):
        return z if z > 0 else alpha * z

    def elu(z, alpha=1.0):
        return z if z > 0 else alpha * (math.exp(z) - 1)

    def gelu(z):
        return z * (1.0 / (1.0 + math.exp(-1.702 * z)))

    # 종합 비교 테이블
    print("  [전체 활성화 함수 종합 비교]")
    print()
    print(f"    {'z':>5} | {'Sigmoid':>8} | {'Tanh':>8} | {'ReLU':>8} | "
          f"{'LeakyR':>8} | {'ELU':>8} | {'GELU':>8}")
    print("    " + "-" * 72)

    for z_val in [-4, -3, -2, -1, -0.5, 0, 0.5, 1, 2, 3, 4]:
        s = sigmoid(z_val)
        t = math.tanh(z_val)
        r = relu(z_val)
        lr = leaky_relu(z_val)
        e = elu(z_val)
        g = gelu(z_val)
        print(f"    {z_val:>+5.1f} | {s:>8.4f} | {t:>+8.4f} | {r:>8.3f} | "
              f"{lr:>+8.3f} | {e:>+8.3f} | {g:>+8.3f}")
    print()

    # ASCII 시각화: 각 함수의 대표 특성
    print("  [각 함수의 모양 요약]")
    print()
    funcs = [
        ("Sigmoid", "      _____", "     /", "____/", "  0~1, S자"),
        ("Tanh",    "      _____", "     /", "____/", " -1~1, S자"),
        ("ReLU",    "         /", "        /", "-------/", "  꺾인 직선"),
        ("Leaky",   "       /", "      /", "  ___/", "  기울어진 직선"),
    ]
    for name, l1, l2, l3, desc in funcs:
        print(f"    {name:>8}: {l1}")
        print(f"              {l2}")
        print(f"              {l3}  {desc}")
        print()

    # 뉴런 하나에 다양한 활성화 함수 적용
    print("  [같은 뉴런에 다양한 활성화 적용]")
    print()

    x = [0.5, -0.3, 0.8]
    w = [0.7, 0.4, -0.2]
    b = 0.1

    z = sum(xi * wi for xi, wi in zip(x, w)) + b
    print(f"    입력: x={x}")
    print(f"    가중치: w={w}, b={b}")
    print(f"    가중합 z = {z:.4f}")
    print()

    results = [
        ("Sigmoid",    sigmoid(z)),
        ("Tanh",       math.tanh(z)),
        ("ReLU",       relu(z)),
        ("Leaky ReLU", leaky_relu(z)),
        ("ELU",        elu(z)),
        ("GELU",       gelu(z)),
    ]

    for name, val in results:
        bar = "#" * int(abs(val) * 20)
        sign = "+" if val >= 0 else "-"
        print(f"    {name:>12}: {val:>+8.4f} {bar}")
    print()

    print("  [정리]")
    print("    - 은닉층: ReLU 먼저 시도, 문제시 Leaky ReLU/GELU")
    print("    - 이진 분류 출력: Sigmoid")
    print("    - 다중 분류 출력: Softmax")
    print("    - 회귀 출력: 활성화 없음 (선형)")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# ■ 메인 실행
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 72)
    print("  [딥러닝] 02단계: 활성화 함수 (Activation Functions)")
    print("=" * 72)
    print()

    lesson1_why_activation()
    lesson2_sigmoid()
    lesson3_tanh()
    lesson4_relu()
    lesson5_relu_variants()
    lesson6_softmax()
    lesson7_selection_guide()
    lesson8_practice()

    print("=" * 72)
    print("  02단계 완료! 다음: 03_forward_pass.py")
    print("=" * 72)


if __name__ == "__main__":
    main()
