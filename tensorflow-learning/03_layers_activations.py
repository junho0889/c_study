# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   TensorFlow/Keras 학습 03단계: 레이어와 활성화 함수
#   ─ Dense, Conv2D, Pooling, Dropout, BatchNorm, 활성화 함수 ─
#   ■ 실행 방법: python 03_layers_activations.py (개념 학습용 코드, TF 없이 실행 가능)
#   ■ TensorFlow 설치: pip install tensorflow
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import random

random.seed(42)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. Dense (완전연결) 레이어 - 동작 원리, 파라미터 수 공식
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("1. Dense(완전연결) 레이어 심화")
print("=" * 70)

print("""
■ Dense 레이어 = Fully Connected Layer
  - 모든 입력 뉴런이 모든 출력 뉴런과 연결
  - 파라미터 수 = input_dim * units + units(bias)

  예시: Dense(128, input_shape=(784,))
    가중치(W): 784 x 128 = 100,352개
    편향(b):   128개
    총 파라미터: 100,480개

■ 언제 사용하나?
  - 분류기의 마지막 레이어
  - 특성(feature)을 조합해서 판단할 때
  - 입력이 1D 벡터일 때
""")

def dense_forward(inputs, weights, biases, activation='relu'):
    """Dense 레이어 순전파"""
    output_size = len(biases)
    input_size = len(inputs)
    outputs = []
    for j in range(output_size):
        z = sum(inputs[i] * weights[i][j] for i in range(input_size)) + biases[j]
        if activation == 'relu':
            z = max(0.0, z)
        elif activation == 'sigmoid':
            z = 1.0 / (1.0 + math.exp(-max(-500, min(500, z))))
        elif activation == 'tanh':
            z = math.tanh(z)
        outputs.append(z)
    if activation == 'softmax':
        max_val = max(outputs)
        exp_vals = [math.exp(o - max_val) for o in outputs]
        total = sum(exp_vals)
        outputs = [e / total for e in exp_vals]
    return outputs

# Dense 동작 시연
input_data = [0.5, -0.3, 0.8, 0.1]
W = [[random.gauss(0, 0.5) for _ in range(3)] for _ in range(4)]
b = [0.0, 0.0, 0.0]

result = dense_forward(input_data, W, b, 'relu')
print(f"■ Dense 순전파 시연:")
print(f"  입력 (4,): {input_data}")
print(f"  출력 (3,): {[f'{r:.4f}' for r in result]}")
print(f"  파라미터: {4*3 + 3} = 4*3(가중치) + 3(편향)")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Conv2D - 합성곱 레이어
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("2. Conv2D (합성곱 레이어)")
print("=" * 70)

print("""
■ Conv2D란?
  이미지에서 특징(패턴)을 추출하는 레이어

  비유: 돋보기로 이미지를 훑으면서 패턴 찾기!
  - 3x3 필터(커널)가 이미지 위를 슬라이딩
  - 각 위치에서 필터와 원소별 곱 → 합산
  - 결과: 특징 맵 (Feature Map)

■ 핵심 파라미터:
  Conv2D(filters=32,       # 필터 수 (추출할 특징 종류)
         kernel_size=(3,3), # 필터 크기
         strides=(1,1),     # 이동 보폭
         padding='same',    # 출력 크기 유지 여부
         activation='relu')

■ 파라미터 수 공식:
  params = (kernel_h * kernel_w * input_channels + 1) * filters
  예: Conv2D(32, (3,3)), 입력 채널=3(RGB)
  params = (3 * 3 * 3 + 1) * 32 = 896
""")

def conv2d_forward(image, kernel, stride=1, padding=0):
    """2D 합성곱 연산 (단일 채널)"""
    h, w = len(image), len(image[0])
    kh, kw = len(kernel), len(kernel[0])

    # 패딩 적용
    if padding > 0:
        padded = [[0.0] * (w + 2 * padding) for _ in range(h + 2 * padding)]
        for i in range(h):
            for j in range(w):
                padded[i + padding][j + padding] = image[i][j]
        image = padded
        h, w = len(image), len(image[0])

    # 출력 크기 계산
    out_h = (h - kh) // stride + 1
    out_w = (w - kw) // stride + 1

    output = [[0.0] * out_w for _ in range(out_h)]
    for i in range(out_h):
        for j in range(out_w):
            total = 0.0
            for ki in range(kh):
                for kj in range(kw):
                    total += image[i * stride + ki][j * stride + kj] * kernel[ki][kj]
            output[i][j] = total

    return output

# Conv2D 시연
print("■ Conv2D 동작 시연:")
image_5x5 = [
    [1, 0, 1, 0, 1],
    [0, 1, 0, 1, 0],
    [1, 0, 1, 0, 1],
    [0, 1, 0, 1, 0],
    [1, 0, 1, 0, 1]
]

# 에지 감지 필터
edge_kernel = [
    [-1, -1, -1],
    [-1,  8, -1],
    [-1, -1, -1]
]

print("  입력 이미지 (5x5):")
for row in image_5x5:
    print(f"    {row}")

print(f"\n  에지 감지 커널 (3x3):")
for row in edge_kernel:
    print(f"    {row}")

feature_map = conv2d_forward(image_5x5, edge_kernel)
print(f"\n  출력 특징 맵 (3x3):")
for row in feature_map:
    print(f"    {[f'{v:5.0f}' for v in row]}")

print(f"\n  출력 크기 공식: (입력-커널)/stride + 1 = (5-3)/1 + 1 = 3")

# stride와 padding의 효과
print(f"\n■ stride와 padding의 효과:")
print(f"  입력: 5x5, 커널: 3x3")
print(f"  stride=1, padding=0 → 출력: 3x3  (기본)")
result_stride2 = conv2d_forward(image_5x5, edge_kernel, stride=2)
print(f"  stride=2, padding=0 → 출력: {len(result_stride2)}x{len(result_stride2[0])}  (크기 절반)")
result_padded = conv2d_forward(image_5x5, edge_kernel, stride=1, padding=1)
print(f"  stride=1, padding=1 → 출력: {len(result_padded)}x{len(result_padded[0])}  (same padding)")

# 실제 코드: tf.keras.layers.Conv2D(32, (3,3), activation='relu', padding='same')


# ═══════════════════════════════════════════════════════════════════════════════
# 3. MaxPooling2D, AveragePooling2D
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("3. Pooling 레이어 (MaxPooling, AveragePooling)")
print("=" * 70)

print("""
■ Pooling이란?
  특징 맵의 크기를 줄이는 다운샘플링 연산

  비유: 사진의 해상도를 낮추되 중요한 정보는 유지!

  MaxPooling: 영역 내 최댓값 선택 (가장 강한 특징 보존)
  AvgPooling: 영역 내 평균값 계산 (부드러운 요약)

  장점:
  1. 계산량 감소 (크기 줄어듦)
  2. 과적합 방지
  3. 위치 변화에 강건해짐 (translation invariance)
""")

def max_pool2d(feature_map, pool_size=2, stride=2):
    """MaxPooling2D"""
    h, w = len(feature_map), len(feature_map[0])
    out_h = (h - pool_size) // stride + 1
    out_w = (w - pool_size) // stride + 1
    output = [[0.0] * out_w for _ in range(out_h)]
    for i in range(out_h):
        for j in range(out_w):
            values = []
            for pi in range(pool_size):
                for pj in range(pool_size):
                    values.append(feature_map[i * stride + pi][j * stride + pj])
            output[i][j] = max(values)
    return output

def avg_pool2d(feature_map, pool_size=2, stride=2):
    """AveragePooling2D"""
    h, w = len(feature_map), len(feature_map[0])
    out_h = (h - pool_size) // stride + 1
    out_w = (w - pool_size) // stride + 1
    output = [[0.0] * out_w for _ in range(out_h)]
    for i in range(out_h):
        for j in range(out_w):
            values = []
            for pi in range(pool_size):
                for pj in range(pool_size):
                    values.append(feature_map[i * stride + pi][j * stride + pj])
            output[i][j] = sum(values) / len(values)
    return output

# Pooling 시연
pool_input = [
    [1, 3, 2, 4],
    [5, 7, 6, 8],
    [9, 2, 4, 6],
    [3, 1, 8, 5]
]

print("■ Pooling 시연:")
print(f"  입력 (4x4):")
for row in pool_input:
    print(f"    {row}")

max_result = max_pool2d(pool_input)
avg_result = avg_pool2d(pool_input)
print(f"\n  MaxPooling2D(2x2) → (2x2):")
for row in max_result:
    print(f"    {row}")
print(f"  → 각 2x2 영역의 최댓값: [max(1,3,5,7)=7, max(2,4,6,8)=8]")

print(f"\n  AveragePooling2D(2x2) → (2x2):")
for row in avg_result:
    print(f"    {[f'{v:.1f}' for v in row]}")

# 실제 코드: tf.keras.layers.MaxPooling2D(pool_size=(2,2))
# 실제 코드: tf.keras.layers.AveragePooling2D(pool_size=(2,2))


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Flatten, Dropout, BatchNormalization
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("4. Flatten, Dropout, BatchNormalization")
print("=" * 70)

# --- Flatten ---
print("""
■ Flatten: 다차원 텐서를 1D로 펼치기
  Conv2D/Pooling의 출력(2D)을 Dense 레이어(1D 입력)에 연결할 때 사용

  예: (batch, 7, 7, 64) → Flatten → (batch, 3136)
      7 * 7 * 64 = 3,136
""")

def flatten(tensor_2d):
    """2D → 1D 변환"""
    return [val for row in tensor_2d for val in row]

flat_example = [[1, 2, 3], [4, 5, 6]]
print(f"  입력 (2x3): {flat_example}")
print(f"  Flatten:    {flatten(flat_example)}")
print(f"  형태 변환:  (2,3) → ({2*3},)")

# 실제 코드: tf.keras.layers.Flatten()

# --- Dropout ---
print("""
■ Dropout: 과적합 방지의 핵심 기법
  학습 중 일부 뉴런을 무작위로 비활성화

  비유: 시험 공부할 때 특정 노트 없이도 잘 하도록 훈련!
  → 모든 뉴런이 고르게 학습됨

  Dropout(0.5) → 50%의 뉴런을 매 학습 스텝마다 끔
  주의: 테스트(추론) 시에는 Dropout을 끔!
""")

def dropout(inputs, rate=0.5, training=True):
    """Dropout 시뮬레이션"""
    if not training:
        return inputs  # 추론 시에는 그대로 통과

    result = []
    scale = 1.0 / (1.0 - rate)  # 스케일링 (활성 뉴런의 값을 키움)
    mask = []
    for val in inputs:
        if random.random() > rate:
            result.append(val * scale)
            mask.append(1)
        else:
            result.append(0.0)
            mask.append(0)
    return result, mask

inputs = [0.5, 0.8, 0.3, 0.9, 0.1, 0.7, 0.4, 0.6]
dropped, mask = dropout(inputs, rate=0.5)
print(f"■ Dropout(rate=0.5) 시연:")
print(f"  입력:    {[f'{v:.1f}' for v in inputs]}")
print(f"  마스크:  {mask}  (1=활성, 0=비활성)")
print(f"  출력:    {[f'{v:.2f}' for v in dropped]}")
print(f"  비활성 뉴런 수: {mask.count(0)}/{len(mask)}")

# 실제 코드: tf.keras.layers.Dropout(0.5)

# --- BatchNormalization ---
print("""
■ BatchNormalization: 학습 안정화의 핵심
  각 배치(batch)의 출력을 정규화(평균=0, 분산=1)

  비유: 학생들의 점수를 매 시험마다 표준화!
  → 학습이 빠르고 안정적

  수식: x_norm = (x - mean) / sqrt(var + epsilon)
        output = gamma * x_norm + beta

  gamma(스케일), beta(시프트)는 학습 가능한 파라미터
""")

def batch_normalize(inputs, epsilon=1e-5):
    """BatchNormalization 시뮬레이션"""
    mean = sum(inputs) / len(inputs)
    variance = sum((x - mean) ** 2 for x in inputs) / len(inputs)
    normalized = [(x - mean) / math.sqrt(variance + epsilon) for x in inputs]
    # gamma=1, beta=0 (초기값)
    return normalized, mean, variance

inputs_bn = [10.0, 20.0, 30.0, 40.0, 50.0]
normalized, mean, var = batch_normalize(inputs_bn)
print(f"■ BatchNormalization 시연:")
print(f"  입력:     {inputs_bn}")
print(f"  평균:     {mean}")
print(f"  분산:     {var}")
print(f"  정규화:   {[f'{v:.4f}' for v in normalized]}")
print(f"  정규화 평균: {sum(normalized)/len(normalized):.6f} (≈ 0)")
norm_var = sum(v**2 for v in normalized) / len(normalized)
print(f"  정규화 분산: {norm_var:.6f} (≈ 1)")

# 실제 코드: tf.keras.layers.BatchNormalization()


# ═══════════════════════════════════════════════════════════════════════════════
# 5. 활성화 함수 총정리
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("5. 활성화 함수 (Activation Functions) 총정리")
print("=" * 70)

print("""
■ 활성화 함수가 왜 필요한가?
  활성화 함수가 없으면 → 아무리 층을 쌓아도 그냥 선형 변환!
  활성화 함수 = 비선형성 도입 → 복잡한 패턴 학습 가능

  비유: 레고 블록에 관절을 달아 다양한 모양을 만들 수 있게!
""")

# 모든 활성화 함수 구현
def relu(x):
    """ReLU: max(0, x) - 가장 기본, 은닉층에서 주로 사용"""
    return max(0.0, x)

def leaky_relu(x, alpha=0.01):
    """Leaky ReLU: 음수도 작은 기울기 허용"""
    return x if x > 0 else alpha * x

def elu(x, alpha=1.0):
    """ELU: 음수 영역에서 부드러운 곡선"""
    return x if x > 0 else alpha * (math.exp(x) - 1)

def sigmoid(x):
    """Sigmoid: 출력을 0~1로 압축 - 이진 분류 출력에 사용"""
    return 1.0 / (1.0 + math.exp(-max(-500, min(500, x))))

def tanh_fn(x):
    """Tanh: 출력을 -1~1로 압축 - RNN에서 자주 사용"""
    return math.tanh(x)

def softmax_fn(values):
    """Softmax: 여러 값을 확률 분포로 변환 - 다중 분류 출력에 사용"""
    max_val = max(values)
    exp_vals = [math.exp(v - max_val) for v in values]
    total = sum(exp_vals)
    return [e / total for e in exp_vals]

def swish(x):
    """Swish: x * sigmoid(x) - 구글 제안, 최근 인기"""
    return x * sigmoid(x)

# 각 활성화 함수의 출력 비교
test_values = [-3.0, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 3.0]

print(f"\n■ 활성화 함수 출력 비교:")
print(f"  {'입력':>6}  {'ReLU':>7}  {'LeakyReLU':>9}  {'Sigmoid':>8}  {'Tanh':>7}  {'Swish':>7}")
print(f"  {'─'*6}  {'─'*7}  {'─'*9}  {'─'*8}  {'─'*7}  {'─'*7}")
for x in test_values:
    print(f"  {x:6.1f}  {relu(x):7.3f}  {leaky_relu(x):9.3f}  "
          f"{sigmoid(x):8.4f}  {tanh_fn(x):7.4f}  {swish(x):7.4f}")

# Softmax 시연
logits = [2.0, 1.0, 0.5, -1.0]
probs = softmax_fn(logits)
print(f"\n■ Softmax 시연 (다중 분류 출력):")
print(f"  로짓(logits): {logits}")
print(f"  확률(probs):  {[f'{p:.4f}' for p in probs]}")
print(f"  합계:         {sum(probs):.4f} (항상 1.0)")

# 각 활성화 함수를 ASCII로 시각화
print(f"\n■ 활성화 함수 그래프 (ASCII):")
functions = {
    'ReLU': relu,
    'Sigmoid': sigmoid,
    'Tanh': tanh_fn,
}

for name, func in functions.items():
    x_range = [i * 0.5 for i in range(-8, 9)]
    y_vals = [func(x) for x in x_range]
    min_y, max_y = min(y_vals), max(y_vals)

    print(f"\n  {name}:")
    height = 6
    for row in range(height, -1, -1):
        if max_y != min_y:
            threshold = min_y + (max_y - min_y) * row / height
        else:
            threshold = min_y
        line = ""
        for y in y_vals:
            if abs(y - threshold) < (max_y - min_y) / height / 2 + 0.01:
                line += "●"
            elif y >= threshold:
                line += "│"
            else:
                line += " "
        label = f"{threshold:6.2f}"
        print(f"    {label} │{line}│")
    print(f"    {'':6s} └{'─' * len(y_vals)}┘")

# 실제 코드: 활성화 함수 사용 방법 (2가지)
# 실제 코드: # 방법 1: 레이어 인자로
# 실제 코드: tf.keras.layers.Dense(64, activation='relu')
# 실제 코드:
# 실제 코드: # 방법 2: 별도 레이어로
# 실제 코드: tf.keras.layers.Dense(64)
# 실제 코드: tf.keras.layers.Activation('relu')
# 실제 코드:
# 실제 코드: # 방법 2가 유용한 경우: BatchNorm을 Conv와 활성화 사이에 넣을 때
# 실제 코드: # Conv2D → BatchNorm → ReLU


# ═══════════════════════════════════════════════════════════════════════════════
# 6. 활성화 함수 선택 가이드
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("6. 활성화 함수 선택 가이드")
print("=" * 70)

print("""
■ 어떤 활성화 함수를 써야 하나?

  ┌──────────────────────────────────────────────────────────────┐
  │  위치          │  추천 활성화 함수    │  이유               │
  ├──────────────────────────────────────────────────────────────┤
  │  은닉층        │  ReLU (기본)        │  빠르고 효과적      │
  │                │  LeakyReLU          │  dying ReLU 방지    │
  │                │  Swish/GELU         │  최신 모델에서 인기 │
  ├──────────────────────────────────────────────────────────────┤
  │  출력층 (이진) │  Sigmoid            │  0~1 확률 출력      │
  │  출력층 (다중) │  Softmax            │  확률 분포 출력     │
  │  출력층 (회귀) │  없음 (linear)      │  범위 제한 없이     │
  └──────────────────────────────────────────────────────────────┘

■ ReLU의 문제점 - "Dying ReLU":
  입력이 항상 음수 → 출력 항상 0 → 기울기 항상 0 → 학습 멈춤!
  해결: LeakyReLU, ELU, PReLU 사용
""")

# Dying ReLU 시연
print("■ Dying ReLU 현상:")
negative_inputs = [-2.5, -1.0, -0.5, -3.0, -0.1]
relu_outputs = [relu(x) for x in negative_inputs]
leaky_outputs = [leaky_relu(x) for x in negative_inputs]
print(f"  입력:      {negative_inputs}")
print(f"  ReLU:      {relu_outputs}  ← 전부 0! 기울기도 0 → 학습 불가")
print(f"  LeakyReLU: {[f'{v:.3f}' for v in leaky_outputs]}  ← 작은 기울기 유지")


# ═══════════════════════════════════════════════════════════════════════════════
# 7. [실습] 각 레이어가 데이터를 어떻게 변환하는지 시각화
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("7. [실습] CNN 파이프라인 데이터 변환 추적")
print("=" * 70)

print("""
■ CNN 전형적 파이프라인:
  입력 이미지 → Conv2D → ReLU → MaxPool → Conv2D → ReLU → MaxPool
              → Flatten → Dense → ReLU → Dense → Softmax → 예측
""")

# 8x8 가상 이미지 생성
print("■ 단계별 데이터 변환 추적:")
image_8x8 = [[random.random() for _ in range(8)] for _ in range(8)]
print(f"\n  Step 0: 입력 이미지")
print(f"  형태: (8, 8, 1)  ← 8x8 흑백 이미지")
for i, row in enumerate(image_8x8[:4]):
    print(f"    행{i}: {[f'{v:.2f}' for v in row[:4]]} ...")

# Step 1: Conv2D (3x3 필터, 1개)
kernel1 = [[random.gauss(0, 0.5) for _ in range(3)] for _ in range(3)]
conv_out = conv2d_forward(image_8x8, kernel1)
print(f"\n  Step 1: Conv2D(filters=1, kernel=3x3)")
print(f"  형태: (8,8,1) → ({len(conv_out)}, {len(conv_out[0])}, 1)")

# Step 2: ReLU
relu_out = [[max(0.0, val) for val in row] for row in conv_out]
negative_count = sum(1 for row in conv_out for val in row if val < 0)
total_count = len(conv_out) * len(conv_out[0])
print(f"\n  Step 2: ReLU 활성화")
print(f"  음수 → 0 변환: {negative_count}/{total_count} 값이 0으로 변경됨")

# Step 3: MaxPooling (2x2)
pool_out = max_pool2d(relu_out)
print(f"\n  Step 3: MaxPooling2D(2x2)")
print(f"  형태: ({len(relu_out)},{len(relu_out[0])}) → ({len(pool_out)},{len(pool_out[0])})")
print(f"  → 크기가 절반으로 줄어듦!")

# Step 4: Flatten
flat_out = flatten(pool_out)
print(f"\n  Step 4: Flatten")
print(f"  형태: ({len(pool_out)},{len(pool_out[0])}) → ({len(flat_out)},)")
print(f"  값: {[f'{v:.2f}' for v in flat_out[:8]]} ...")

# Step 5: Dense
W_dense = [[random.gauss(0, 0.5) for _ in range(4)] for _ in range(len(flat_out))]
b_dense = [0.0] * 4
dense_out = dense_forward(flat_out, W_dense, b_dense, 'relu')
print(f"\n  Step 5: Dense(4, relu)")
print(f"  형태: ({len(flat_out)},) → (4,)")
print(f"  출력: {[f'{v:.4f}' for v in dense_out]}")

# Step 6: Dense (출력층)
W_out = [[random.gauss(0, 0.5) for _ in range(3)] for _ in range(4)]
b_out = [0.0] * 3
final_out = dense_forward(dense_out, W_out, b_out, 'softmax')
print(f"\n  Step 6: Dense(3, softmax) ← 3클래스 분류")
print(f"  형태: (4,) → (3,)")
print(f"  확률: {[f'{v:.4f}' for v in final_out]}")
print(f"  예측 클래스: {final_out.index(max(final_out))}")
print(f"  확률 합계: {sum(final_out):.4f}")

# 전체 파이프라인 요약
print(f"""
■ 전체 파이프라인 요약:
  (8,8,1) → Conv2D(3x3)  → (6,6,1)   ← 특징 추출
          → ReLU          → (6,6,1)   ← 비선형성
          → MaxPool(2x2)  → (3,3,1)   ← 다운샘플링
          → Flatten        → (9,)      ← 1D로 변환
          → Dense(4,relu)  → (4,)      ← 특징 조합
          → Dense(3,soft)  → (3,)      ← 확률 출력
""")

# 실제 코드: Keras로 위 파이프라인 구현
# 실제 코드: model = tf.keras.Sequential([
# 실제 코드:     tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=(28,28,1)),
# 실제 코드:     tf.keras.layers.MaxPooling2D((2,2)),
# 실제 코드:     tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
# 실제 코드:     tf.keras.layers.MaxPooling2D((2,2)),
# 실제 코드:     tf.keras.layers.Flatten(),
# 실제 코드:     tf.keras.layers.Dense(64, activation='relu'),
# 실제 코드:     tf.keras.layers.Dropout(0.5),
# 실제 코드:     tf.keras.layers.Dense(10, activation='softmax')
# 실제 코드: ])


# ═══════════════════════════════════════════════════════════════════════════════
# 8. GlobalAveragePooling vs Flatten
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("8. GlobalAveragePooling vs Flatten")
print("=" * 70)

def global_avg_pool(feature_maps):
    """각 채널(필터)의 평균을 계산"""
    if isinstance(feature_maps[0][0], list):
        # 3D: [채널][행][열]
        return [sum(val for row in ch for val in row) / (len(ch) * len(ch[0]))
                for ch in feature_maps]
    else:
        # 2D: 단일 채널
        return sum(val for row in feature_maps for val in row) / (len(feature_maps) * len(feature_maps[0]))

# 비교
fm = [
    [[1, 2], [3, 4]],  # 채널 1
    [[5, 6], [7, 8]],  # 채널 2
    [[9, 10], [11, 12]] # 채널 3
]

print(f"\n  특징 맵: 3채널, 각 2x2")
print(f"  Flatten: {flatten(fm[0]) + flatten(fm[1]) + flatten(fm[2])}  ← 12개 값")
print(f"  GAP:     {global_avg_pool(fm)}  ← 3개 값 (채널당 평균)")
print(f"\n  GAP의 장점:")
print(f"    - 파라미터 수 대폭 감소 (Flatten: 12→Dense vs GAP: 3→Dense)")
print(f"    - 과적합 방지에 효과적")
print(f"    - 입력 크기에 독립적")

# 실제 코드: tf.keras.layers.GlobalAveragePooling2D()


# ═══════════════════════════════════════════════════════════════════════════════
# 9. 레이어 조합 패턴
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("9. 자주 사용하는 레이어 조합 패턴")
print("=" * 70)

print("""
■ 패턴 1: Conv Block (가장 기본)
  Conv2D → BatchNorm → ReLU → MaxPool

■ 패턴 2: Bottleneck Block (ResNet)
  Conv2D(1x1) → BatchNorm → ReLU
  Conv2D(3x3) → BatchNorm → ReLU
  Conv2D(1x1) → BatchNorm → Add(입력) → ReLU

■ 패턴 3: Separable Conv (MobileNet)
  DepthwiseConv2D → BatchNorm → ReLU
  Conv2D(1x1) → BatchNorm → ReLU
  → 파라미터 수 대폭 감소!

■ 패턴 4: Classifier Head (분류기 머리)
  GlobalAveragePooling2D → Dropout → Dense(softmax)

■ 패턴 5: Dense Block (DenseNet)
  BatchNorm → ReLU → Conv2D → Concat(이전 출력들)
  → 모든 이전 층의 출력을 합침!
""")

# 파라미터 수 비교
print("■ 파라미터 수 비교 (입력: 32x32x64):")
print(f"  일반 Conv2D(128, 3x3):  {3*3*64*128 + 128:,} params")
print(f"  Depthwise + Pointwise:  {3*3*64 + 64*128 + 64 + 128:,} params")
print(f"  → Separable이 약 {(3*3*64*128 + 128) / (3*3*64 + 64*128 + 64 + 128):.1f}배 효율적!")


# ═══════════════════════════════════════════════════════════════════════════════
# 10. 1D 합성곱 (시계열/텍스트)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("10. Conv1D - 시계열/텍스트 처리")
print("=" * 70)

def conv1d_forward(sequence, kernel):
    """1D 합성곱"""
    seq_len = len(sequence)
    k_len = len(kernel)
    out_len = seq_len - k_len + 1
    output = []
    for i in range(out_len):
        total = sum(sequence[i + j] * kernel[j] for j in range(k_len))
        output.append(total)
    return output

sequence = [0.1, 0.5, 0.9, 0.7, 0.3, 0.8, 0.2, 0.6]
kernel_1d = [0.33, 0.34, 0.33]  # 이동 평균 필터
smoothed = conv1d_forward(sequence, kernel_1d)

print(f"\n■ Conv1D 시연 (이동 평균 필터):")
print(f"  입력 시퀀스: {sequence}")
print(f"  커널 (3,):   {kernel_1d}")
print(f"  출력:        {[f'{v:.3f}' for v in smoothed]}")
print(f"  → 노이즈가 줄어들고 부드러워짐!")

# 실제 코드: tf.keras.layers.Conv1D(filters=32, kernel_size=3, activation='relu')


print("\n" + "=" * 70)
print("요약: 레이어와 활성화 함수 학습 완료!")
print("=" * 70)
print("""
  1. Dense: 완전연결, params = in * out + out
  2. Conv2D: 필터로 특징 추출, 이미지 처리의 핵심
  3. Pooling: 다운샘플링, 계산량 감소
  4. Flatten: 다차원→1D 변환
  5. Dropout: 과적합 방지 (학습 시만 활성)
  6. BatchNorm: 학습 안정화 (정규화)
  7. 활성화 함수: 은닉층=ReLU, 이진출력=Sigmoid, 다중출력=Softmax

  다음 단계 → 04_optimizers_loss.py (옵티마이저와 손실 함수!)
""")
