# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [딥러닝] 학습 03단계: 순전파 (Forward Pass)
#   ─ 신경망 구조, 가중치 행렬, 다층 순전파, 초기화 전략 ─
#   ■ 실행 방법: python 03_forward_pass.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import random


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 신경망 구조 - 입력층/은닉층/출력층
#   2. 가중치 행렬 - 행렬로 연결 표현, 초기화
#   3. 순전파 한 단계 - 가중합→활성화→출력
#   4. 다층 순전파 - 2층, 3층 네트워크
#   5. 행렬 곱셈으로 순전파 - 벡터화, 배치 처리
#   6. 바이어스의 역할 - 없으면 어떻게 되는지
#   7. 가중치 초기화 전략 - Xavier, He 초기화
#   8. 실전: 3층 신경망 순전파 완전 구현
#
# ─────────────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────────────
# ■ 공통 유틸리티 함수
# ─────────────────────────────────────────────────────────────────────────

def sigmoid(z):
    z = max(-500, min(500, z))
    return 1.0 / (1.0 + math.exp(-z))

def relu(z):
    return max(0, z)

def softmax(z_list):
    max_z = max(z_list)
    exp_z = [math.exp(z - max_z) for z in z_list]
    s = sum(exp_z)
    return [e / s for e in exp_z]


def lesson1_network_structure():
    # =========================================================================
    #
    #   레슨 1 — 신경망 구조
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 신경망 구조                │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 신경망 = 층(Layer)의 연결
    # ─────────────────────────────────────────────────────────────────────
    #
    #   입력층 (Input Layer):    데이터를 받는 층 (학습 X)
    #   은닉층 (Hidden Layer):   중간 계산 층 (학습 O)
    #   출력층 (Output Layer):   최종 결과 출력 (학습 O)
    #
    #   용어:
    #     노드(Node): 각 층의 하나의 뉴런
    #     엣지(Edge): 노드 간 연결 = 가중치
    #     깊이(Depth): 은닉층 수 → "딥"러닝!
    #     너비(Width): 각 층의 노드 수
    #

    print("  [신경망 구조 (ASCII)]")
    print()
    print("    입력층     은닉층1    은닉층2    출력층")
    print("    (2노드)    (3노드)    (2노드)    (1노드)")
    print()
    print("      x1 ──┬── h1 ──┬── h4 ──┐")
    print("            ├── h2 ──┤        ├── y")
    print("      x2 ──┴── h3 ──┴── h5 ──┘")
    print()
    print("    구조 표기: 2-3-2-1")
    print("    입력 2개 → 은닉1 3개 → 은닉2 2개 → 출력 1개")
    print()

    # 구조에 따른 파라미터 수 계산
    print("  [파라미터(가중치+편향) 수 계산]")
    print()

    structures = [
        ("2-3-1",   [(2, 3), (3, 1)]),
        ("2-3-2-1", [(2, 3), (3, 2), (2, 1)]),
        ("3-4-4-2", [(3, 4), (4, 4), (4, 2)]),
        ("784-128-64-10", [(784, 128), (128, 64), (64, 10)]),
    ]

    for name, layers in structures:
        total_weights = sum(inp * out for inp, out in layers)
        total_biases = sum(out for _, out in layers)
        total = total_weights + total_biases
        print(f"    {name:>15}: 가중치 {total_weights:>6} + 편향 {total_biases:>4} = 총 {total:>6}개")
    print()
    print("  → MNIST(784-128-64-10)는 약 10만 개의 학습 파라미터!")
    print()


def lesson2_weight_matrix():
    # =========================================================================
    #
    #   레슨 2 — 가중치 행렬
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : 가중치 행렬                │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 가중치를 행렬로 표현
    # ─────────────────────────────────────────────────────────────────────
    #
    #   입력 2개 → 은닉 3개 연결:
    #
    #   x1 → h1: w11    x1 → h2: w12    x1 → h3: w13
    #   x2 → h1: w21    x2 → h2: w22    x2 → h3: w23
    #
    #   행렬로 표현:
    #   W = [[w11, w12, w13],    ← x1에서 나가는 가중치
    #        [w21, w22, w23]]    ← x2에서 나가는 가중치
    #
    #   크기: (입력 수) x (출력 수) = 2 x 3
    #

    # 예시 가중치 행렬
    W1 = [[0.5, -0.3, 0.8],    # 입력1 → 은닉1,2,3
          [0.2,  0.7, -0.1]]   # 입력2 → 은닉1,2,3
    b1 = [0.1, -0.2, 0.3]     # 은닉층 편향

    print("  [가중치 행렬 W1 (2x3)]")
    print()
    print("    입력 → 은닉 연결:")
    for i, row in enumerate(W1):
        print(f"    x{i+1} → [{', '.join(f'{w:>+5.1f}' for w in row)}]")
    print(f"    편향: [{', '.join(f'{b:>+5.1f}' for b in b1)}]")
    print()

    # 각 연결의 의미
    print("  [각 가중치의 의미]")
    labels = [
        ("W[0][0]=+0.5", "x1이 h1에 양의 영향"),
        ("W[0][1]=-0.3", "x1이 h2에 음의 영향"),
        ("W[1][1]=+0.7", "x2가 h2에 강한 양의 영향"),
    ]
    for weight, meaning in labels:
        print(f"    {weight}: {meaning}")
    print()

    # 가중합 계산 과정
    x = [0.8, 0.6]  # 입력
    print(f"  [가중합 계산] 입력 x = {x}")
    print()

    for j in range(3):
        terms = " + ".join(f"{x[i]}*{W1[i][j]:+.1f}" for i in range(2))
        weighted_sum = sum(x[i] * W1[i][j] for i in range(2))
        total = weighted_sum + b1[j]
        print(f"    h{j+1} = {terms} + {b1[j]:+.1f}")
        print(f"        = {weighted_sum:.2f} + {b1[j]:+.1f} = {total:.2f}")
    print()


def lesson3_single_layer_forward():
    # =========================================================================
    #
    #   레슨 3 — 순전파 한 단계
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : 순전파 한 단계             │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 순전파 한 층: 입력 → 가중합 → 활성화 → 출력
    # ─────────────────────────────────────────────────────────────────────

    # 입력
    x = [0.8, 0.6]

    # 가중치와 편향
    W = [[0.5, -0.3, 0.8],
         [0.2,  0.7, -0.1]]
    b = [0.1, -0.2, 0.3]

    print("  [순전파 과정: 입력(2) → 은닉(3)]")
    print()
    print(f"  입력: x = {x}")
    print()

    # Step 1: 가중합
    print("  Step 1: 가중합 z = W^T * x + b")
    z = []
    for j in range(3):
        wsum = sum(x[i] * W[i][j] for i in range(2))
        z_j = wsum + b[j]
        z.append(z_j)
        print(f"    z{j+1} = {' + '.join(f'{x[i]}*{W[i][j]:.1f}' for i in range(2))} + {b[j]:.1f} = {z_j:.3f}")
    print()

    # Step 2: 활성화 (ReLU)
    print("  Step 2: 활성화 a = ReLU(z)")
    a = []
    for j in range(3):
        a_j = relu(z[j])
        a.append(a_j)
        print(f"    a{j+1} = ReLU({z[j]:.3f}) = {a_j:.3f}")
    print()

    print(f"  출력: a = {[round(v, 3) for v in a]}")
    print()

    # 다른 활성화 함수 비교
    print("  [같은 z에 다른 활성화 적용]")
    print(f"    {'z':>7} | {'ReLU':>7} | {'Sigmoid':>8} | {'Tanh':>8}")
    print("    " + "-" * 40)
    for j in range(3):
        print(f"    {z[j]:>+7.3f} | {relu(z[j]):>7.3f} | {sigmoid(z[j]):>8.4f} | {math.tanh(z[j]):>+8.4f}")
    print()

    return a


def lesson4_multi_layer_forward():
    # =========================================================================
    #
    #   레슨 4 — 다층 순전파
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : 다층 순전파                │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 2층 네트워크: 입력(2) → 은닉(3) → 출력(1)
    # ─────────────────────────────────────────────────────────────────────

    x = [0.8, 0.6]

    # 1층: 입력(2) → 은닉(3)
    W1 = [[0.5, -0.3, 0.8],
          [0.2,  0.7, -0.1]]
    b1 = [0.1, -0.2, 0.3]

    # 2층: 은닉(3) → 출력(1)
    W2 = [[0.6],
          [0.4],
          [-0.5]]
    b2 = [0.2]

    print("  [2층 네트워크: 2-3-1]")
    print(f"  입력: x = {x}")
    print()

    # 1층 순전파
    print("  ── 1층 (입력→은닉) ──")
    z1 = []
    a1 = []
    for j in range(3):
        wsum = sum(x[i] * W1[i][j] for i in range(2))
        z = wsum + b1[j]
        a = relu(z)
        z1.append(z)
        a1.append(a)
        print(f"    h{j+1}: z={z:>+.3f} → ReLU → a={a:.3f}")
    print()

    # 2층 순전파
    print("  ── 2층 (은닉→출력) ──")
    z2 = sum(a1[j] * W2[j][0] for j in range(3)) + b2[0]
    output = sigmoid(z2)

    terms = " + ".join(f"{a1[j]:.3f}*{W2[j][0]:.1f}" for j in range(3))
    print(f"    z = {terms} + {b2[0]:.1f}")
    print(f"      = {z2:.4f}")
    print(f"    output = sigmoid({z2:.4f}) = {output:.4f}")
    print()

    # 해석
    if output > 0.5:
        print(f"    → 출력 {output:.4f} > 0.5 → 양성(1) 예측")
    else:
        print(f"    → 출력 {output:.4f} <= 0.5 → 음성(0) 예측")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 3층 네트워크: 입력(2) → 은닉1(3) → 은닉2(2) → 출력(1)
    # ─────────────────────────────────────────────────────────────────────
    print("  [3층 네트워크: 2-3-2-1]")
    print()

    # 3층 추가
    W3 = [[0.7, -0.4],
          [0.3,  0.6],
          [-0.2, 0.5]]
    b3 = [0.1, -0.1]

    W4 = [[0.8],
          [-0.3]]
    b4 = [0.1]

    # 은닉2
    a2 = []
    for j in range(2):
        z = sum(a1[k] * W3[k][j] for k in range(3)) + b3[j]
        a = relu(z)
        a2.append(a)
        print(f"    은닉2 h{j+1}: z={z:>+.3f} → ReLU → a={a:.3f}")

    # 출력
    z_out = sum(a2[j] * W4[j][0] for j in range(2)) + b4[0]
    final = sigmoid(z_out)
    print(f"    출력: z={z_out:.4f} → sigmoid → {final:.4f}")
    print()

    # 중간값 흐름 시각화
    print("  [값의 흐름]")
    print(f"    입력:  {x}")
    print(f"    은닉1: {[round(v, 3) for v in a1]}")
    print(f"    은닉2: {[round(v, 3) for v in a2]}")
    print(f"    출력:  {final:.4f}")
    print()


def lesson5_matrix_forward():
    # =========================================================================
    #
    #   레슨 5 — 행렬 곱셈으로 순전파
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 행렬 곱셈으로 순전파       │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 행렬 곱셈으로 한 번에 계산
    # ─────────────────────────────────────────────────────────────────────
    #
    #   개별 계산:
    #     z1 = w11*x1 + w21*x2 + b1
    #     z2 = w12*x1 + w22*x2 + b2
    #     z3 = w13*x1 + w23*x2 + b3
    #
    #   행렬 곱셈:
    #     Z = X @ W + B
    #     [z1, z2, z3] = [x1, x2] @ [[w11,w12,w13], [w21,w22,w23]] + [b1,b2,b3]
    #

    def mat_mul(A, B):
        """행렬 곱셈 (2D 리스트)"""
        rows_A, cols_A = len(A), len(A[0])
        cols_B = len(B[0])
        result = [[0] * cols_B for _ in range(rows_A)]
        for i in range(rows_A):
            for j in range(cols_B):
                for k in range(cols_A):
                    result[i][j] += A[i][k] * B[k][j]
        return result

    def mat_add(A, B):
        """행렬 덧셈 (B는 1행짜리도 가능 - 브로드캐스팅)"""
        result = []
        for i in range(len(A)):
            row = []
            b_row = B[0] if len(B) == 1 else B[i]
            for j in range(len(A[0])):
                row.append(A[i][j] + b_row[j])
            result.append(row)
        return result

    def apply_relu(matrix):
        return [[relu(v) for v in row] for row in matrix]

    # 단일 입력
    X = [[0.8, 0.6]]
    W = [[0.5, -0.3, 0.8],
         [0.2,  0.7, -0.1]]
    B = [[0.1, -0.2, 0.3]]

    print("  [단일 입력 행렬 곱셈]")
    print(f"    X (1x2): {X}")
    print(f"    W (2x3): {W}")
    print(f"    B (1x3): {B}")
    print()

    Z = mat_add(mat_mul(X, W), B)
    A = apply_relu(Z)
    print(f"    Z = X@W + B = {[[round(v, 3) for v in row] for row in Z]}")
    print(f"    A = ReLU(Z) = {[[round(v, 3) for v in row] for row in A]}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 배치 처리: 여러 입력을 한 번에!
    # ─────────────────────────────────────────────────────────────────────
    print("  [배치 처리: 3개 입력 동시 계산]")
    print()

    X_batch = [
        [0.8, 0.6],   # 샘플 1
        [0.3, 0.9],   # 샘플 2
        [0.5, 0.5],   # 샘플 3
    ]

    print(f"    X_batch (3x2):")
    for i, row in enumerate(X_batch):
        print(f"      샘플{i+1}: {row}")
    print()

    Z_batch = mat_mul(X_batch, W)
    # 편향 브로드캐스팅
    Z_batch = [[Z_batch[i][j] + B[0][j] for j in range(3)] for i in range(3)]
    A_batch = apply_relu(Z_batch)

    print(f"    결과 A_batch (3x3):")
    for i, row in enumerate(A_batch):
        print(f"      샘플{i+1}: {[round(v, 3) for v in row]}")
    print()
    print("    → 배치 처리로 3개를 한 번에 계산! GPU에서 매우 빠름")
    print()


def lesson6_bias_role():
    # =========================================================================
    #
    #   레슨 6 — 바이어스의 역할
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 바이어스의 역할            │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 바이어스 = 결정 경계를 이동시키는 역할
    # ─────────────────────────────────────────────────────────────────────
    #
    #   바이어스 없이: z = w*x → 경계가 반드시 원점(0)을 지남
    #   바이어스 있으면: z = w*x + b → 경계를 좌우로 이동 가능
    #

    # 비교: 바이어스 있을 때 vs 없을 때
    w = 2.0

    print("  [바이어스 없이 (b=0)]")
    print(f"    z = {w}*x, ReLU 적용")
    print()
    for x_val in [-2, -1, 0, 1, 2, 3]:
        z = w * x_val
        a = relu(z)
        bar = "#" * int(a * 3) if a > 0 else ""
        print(f"    x={x_val:>+3}: z={z:>+5.1f} → ReLU={a:.1f} {bar}")
    print("    → x=0에서 꺾임 (0 고정)")
    print()

    # 바이어스 = -3
    b = -3.0
    print(f"  [바이어스 있을 때 (b={b})]")
    print(f"    z = {w}*x + {b}")
    print()
    for x_val in [-2, -1, 0, 1, 2, 3]:
        z = w * x_val + b
        a = relu(z)
        bar = "#" * int(a * 3) if a > 0 else ""
        print(f"    x={x_val:>+3}: z={z:>+5.1f} → ReLU={a:.1f} {bar}")
    print(f"    → x=1.5에서 꺾임 (b가 경계를 이동!)")
    print()

    # 바이어스 = +2
    b2 = 2.0
    print(f"  [바이어스 = {b2}]")
    for x_val in [-2, -1, 0, 1, 2, 3]:
        z = w * x_val + b2
        a = relu(z)
        bar = "#" * int(a * 3) if a > 0 else ""
        print(f"    x={x_val:>+3}: z={z:>+5.1f} → ReLU={a:.1f} {bar}")
    print(f"    → x=-1에서 꺾임")
    print()

    print("  [결론]")
    print("    바이어스는 활성화 함수의 '시작점'을 조절한다")
    print("    없으면 모든 뉴런의 경계가 원점에 고정 → 표현력 감소")
    print()


def lesson7_weight_initialization():
    # =========================================================================
    #
    #   레슨 7 — 가중치 초기화 전략
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 가중치 초기화 전략         │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 초기화가 왜 중요한가?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   가중치를 어떻게 시작하느냐에 따라 학습 성패가 갈린다!
    #
    #   나쁜 초기화 예:
    #     1. 모두 0: 모든 뉴런이 같은 출력 → 같은 업데이트 → 쓸모없음
    #     2. 너무 큰 값: 활성화 포화 → 기울기 소실
    #     3. 너무 작은 값: 출력이 0에 가까움 → 기울기 소실
    #

    random.seed(42)

    # 문제 1: 모두 0으로 초기화
    print("  [문제 1: 모두 0으로 초기화]")
    print()

    x = [0.5, 0.8]
    W_zero = [[0, 0, 0],
              [0, 0, 0]]

    z_vals = [sum(x[i] * W_zero[i][j] for i in range(2)) for j in range(3)]
    print(f"    입력: {x}")
    print(f"    W = [[0,0,0], [0,0,0]]")
    print(f"    출력: {z_vals}")
    print("    → 모든 뉴런의 출력이 같다! 업데이트도 같다!")
    print("    → '대칭 깨기'(symmetry breaking) 실패")
    print()

    # 문제 2: 너무 큰 값
    print("  [문제 2: 너무 큰 값]")
    print()

    W_large = [[random.gauss(0, 5) for _ in range(3)] for _ in range(2)]
    z_vals = [sum(x[i] * W_large[i][j] for i in range(2)) for j in range(3)]
    sig_vals = [sigmoid(z) for z in z_vals]

    print(f"    W_large (std=5): {[[round(v,2) for v in row] for row in W_large]}")
    print(f"    z값: {[round(v, 2) for v in z_vals]}")
    print(f"    sigmoid(z): {[round(v, 6) for v in sig_vals]}")
    print("    → sigmoid 출력이 0 또는 1에 포화 → 기울기 약 0")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Xavier 초기화 (Glorot 초기화)
    # ─────────────────────────────────────────────────────────────────────
    print("  [Xavier 초기화]")
    print("    표준편차 = sqrt(2 / (입력 수 + 출력 수))")
    print("    → Sigmoid/Tanh에 적합")
    print()

    n_in, n_out = 2, 3
    xavier_std = (2 / (n_in + n_out)) ** 0.5
    W_xavier = [[random.gauss(0, xavier_std) for _ in range(n_out)] for _ in range(n_in)]
    z_xavier = [sum(x[i] * W_xavier[i][j] for i in range(n_in)) for j in range(n_out)]

    print(f"    입력={n_in}, 출력={n_out}")
    print(f"    표준편차 = sqrt(2/{n_in+n_out}) = {xavier_std:.4f}")
    print(f"    W_xavier: {[[round(v,4) for v in row] for row in W_xavier]}")
    print(f"    z값: {[round(v, 4) for v in z_xavier]}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ He 초기화 (Kaiming 초기화)
    # ─────────────────────────────────────────────────────────────────────
    print("  [He 초기화]")
    print("    표준편차 = sqrt(2 / 입력 수)")
    print("    → ReLU에 적합")
    print()

    he_std = (2 / n_in) ** 0.5
    W_he = [[random.gauss(0, he_std) for _ in range(n_out)] for _ in range(n_in)]
    z_he = [sum(x[i] * W_he[i][j] for i in range(n_in)) for j in range(n_out)]

    print(f"    입력={n_in}")
    print(f"    표준편차 = sqrt(2/{n_in}) = {he_std:.4f}")
    print(f"    W_he: {[[round(v,4) for v in row] for row in W_he]}")
    print(f"    z값: {[round(v, 4) for v in z_he]}")
    print()

    # 초기화 비교 표
    print("  [초기화 방법 비교]")
    print("    ┌────────────┬──────────────────────┬──────────────┐")
    print("    │ 방법       │ 표준편차             │ 적합한 활성화│")
    print("    ├────────────┼──────────────────────┼──────────────┤")
    print("    │ Zero       │ 0 (사용 금지!)       │ -            │")
    print("    │ Xavier     │ sqrt(2/(n_in+n_out)) │ Sigmoid/Tanh │")
    print("    │ He         │ sqrt(2/n_in)         │ ReLU         │")
    print("    └────────────┴──────────────────────┴──────────────┘")
    print()


def lesson8_practice():
    # =========================================================================
    #
    #   레슨 8 — 실전: 3층 신경망 순전파 완전 구현
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 8 : 3층 신경망 순전파 구현     │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 구조: 입력(3) → 은닉1(4) → 은닉2(3) → 출력(2)
    # ■ 문제: 학생 정보 [공부시간, 수면시간, 출석률] → [합격확률, 불합격확률]
    # ─────────────────────────────────────────────────────────────────────

    random.seed(42)

    # He 초기화
    def he_init(n_in, n_out):
        std = (2 / n_in) ** 0.5
        return [[random.gauss(0, std) for _ in range(n_out)] for _ in range(n_in)]

    # 네트워크 정의
    W1 = he_init(3, 4)  # 3→4
    b1 = [0.0] * 4
    W2 = he_init(4, 3)  # 4→3
    b2 = [0.0] * 3
    W3 = he_init(3, 2)  # 3→2
    b3 = [0.0] * 2

    print("  구조: 3(입력) → 4(은닉1) → 3(은닉2) → 2(출력)")
    print()

    def forward(x, verbose=True):
        """3층 순전파"""
        if verbose:
            print(f"    입력: {[round(v, 2) for v in x]}")

        # 1층: 입력→은닉1 (ReLU)
        z1 = [sum(x[i] * W1[i][j] for i in range(3)) + b1[j] for j in range(4)]
        a1 = [relu(z) for z in z1]
        if verbose:
            print(f"    은닉1 (ReLU): {[round(v, 4) for v in a1]}")

        # 2층: 은닉1→은닉2 (ReLU)
        z2 = [sum(a1[i] * W2[i][j] for i in range(4)) + b2[j] for j in range(3)]
        a2 = [relu(z) for z in z2]
        if verbose:
            print(f"    은닉2 (ReLU): {[round(v, 4) for v in a2]}")

        # 3층: 은닉2→출력 (Softmax)
        z3 = [sum(a2[i] * W3[i][j] for i in range(3)) + b3[j] for j in range(2)]
        a3 = softmax(z3)
        if verbose:
            print(f"    출력 (Softmax): {[round(v, 4) for v in a3]}")

        return a3

    # 학생 데이터 (정규화된 값: 0~1)
    students = [
        ([0.8, 0.7, 0.9], "공부8h, 수면7h, 출석90%"),
        ([0.3, 0.5, 0.6], "공부3h, 수면5h, 출석60%"),
        ([0.9, 0.8, 0.8], "공부9h, 수면8h, 출석80%"),
        ([0.1, 0.3, 0.4], "공부1h, 수면3h, 출석40%"),
    ]

    print("  [각 학생의 순전파 결과]")
    print()

    for features, desc in students:
        print(f"  {desc}")
        probs = forward(features)
        pred = "합격" if probs[0] > probs[1] else "불합격"
        print(f"    → 예측: {pred} (합격={probs[0]:.2%}, 불합격={probs[1]:.2%})")
        print()

    # 파라미터 수 계산
    total_weights = 3*4 + 4*3 + 3*2
    total_biases = 4 + 3 + 2
    total = total_weights + total_biases

    print("  [네트워크 통계]")
    print(f"    총 가중치: {total_weights}개")
    print(f"    총 편향: {total_biases}개")
    print(f"    총 파라미터: {total}개")
    print()

    print("  [순전파 정리]")
    print("    1. 입력을 받는다")
    print("    2. 각 층에서: 가중합 → 활성화 → 다음 층으로 전달")
    print("    3. 마지막 층에서 최종 출력 (예측값)")
    print()
    print("    → 학습은 아직 안 했으므로 예측이 랜덤!")
    print("    → 다음 단계(04_loss_basics.py)에서 '얼마나 틀렸는지' 측정!")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# ■ 메인 실행
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 72)
    print("  [딥러닝] 03단계: 순전파 (Forward Pass)")
    print("=" * 72)
    print()

    lesson1_network_structure()
    lesson2_weight_matrix()
    lesson3_single_layer_forward()
    lesson4_multi_layer_forward()
    lesson5_matrix_forward()
    lesson6_bias_role()
    lesson7_weight_initialization()
    lesson8_practice()

    print("=" * 72)
    print("  03단계 완료! 다음: 04_loss_basics.py")
    print("=" * 72)


if __name__ == "__main__":
    main()
