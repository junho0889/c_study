# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   TensorFlow/Keras 학습 05단계: CNN과 이미지 처리
#   ─ CNN 아키텍처, 이미지 전처리, MNIST/CIFAR, LeNet, 필터 시각화 ─
#   ■ 실행 방법: python 05_cnn_image.py (개념 학습용 코드, TF 없이 실행 가능)
#   ■ TensorFlow 설치: pip install tensorflow
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import random

random.seed(42)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. CNN 아키텍처 - 왜 CNN인가?
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("1. CNN (Convolutional Neural Network) 아키텍처")
print("=" * 70)

print("""
■ 왜 이미지에 Dense 대신 CNN을 쓰나?

  28x28 흑백 이미지를 Dense로 처리하면:
  - 입력: 784개 뉴런 (28*28 = 784)
  - Dense(256): 784 * 256 + 256 = 200,960 파라미터
  - 공간 정보(위치 관계) 완전히 무시!

  CNN의 장점:
  1. 파라미터 공유: 3x3 필터 하나로 전체 이미지 스캔
     → 파라미터 수 대폭 감소! (9개 vs 수만 개)
  2. 공간 정보 보존: 이웃 픽셀 관계 유지
  3. 이동 불변성: 물체가 어디에 있든 감지 가능

  비유: CCTV 카메라처럼 화면을 작은 창으로 훑으며 패턴 발견!

■ CNN의 전형적 구조:
  ┌──────────────────────────────────────────────────────┐
  │  입력 이미지 (28x28x1)                               │
  │  ↓                                                    │
  │  [Conv2D → ReLU → MaxPool] × 2~3  ← 특징 추출부      │
  │  ↓                                                    │
  │  [Flatten → Dense → Dropout] × 1~2 ← 분류부          │
  │  ↓                                                    │
  │  Dense(num_classes, softmax)       ← 출력층           │
  └──────────────────────────────────────────────────────┘
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. 이미지 전처리
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("2. 이미지 전처리 (Preprocessing)")
print("=" * 70)

def normalize_pixels(image, method='minmax'):
    """픽셀값 정규화"""
    if method == 'minmax':
        # 0~255 → 0~1
        return [[p / 255.0 for p in row] for row in image]
    elif method == 'standard':
        # 평균=0, 표준편차=1
        flat = [p for row in image for p in row]
        mean = sum(flat) / len(flat)
        std = math.sqrt(sum((p - mean) ** 2 for p in flat) / len(flat))
        return [[(p - mean) / (std + 1e-7) for p in row] for row in image]

def resize_image(image, new_h, new_w):
    """간단한 이미지 리사이즈 (최근접 이웃 보간법)"""
    h, w = len(image), len(image[0])
    result = []
    for i in range(new_h):
        row = []
        for j in range(new_w):
            src_i = int(i * h / new_h)
            src_j = int(j * w / new_w)
            row.append(image[min(src_i, h - 1)][min(src_j, w - 1)])
        result.append(row)
    return result

# 전처리 시연
print("""
■ 이미지 전처리 단계:

  1. 정규화 (Normalization):
     0~255 → 0~1 (또는 -1~1)
     왜? 큰 값이 학습을 불안정하게 만들기 때문
""")

sample_pixels = [[200, 50, 128, 255], [0, 100, 200, 150]]
normalized = normalize_pixels(sample_pixels)
print(f"  원본:   {sample_pixels}")
print(f"  정규화: {[[f'{v:.3f}' for v in row] for row in normalized]}")

print("""
  2. 리사이즈 (Resize):
     다양한 크기의 이미지를 통일된 크기로 변환
     모델 입력이 고정 크기여야 하기 때문!
""")

img_4x4 = [[i * 4 + j for j in range(4)] for i in range(4)]
img_2x2 = resize_image(img_4x4, 2, 2)
print(f"  4x4 이미지: {img_4x4}")
print(f"  2x2 리사이즈: {img_2x2}")

# 데이터 증강
print("""
  3. 데이터 증강 (Data Augmentation):
     학습 데이터를 인위적으로 늘리는 기법!

     비유: 같은 사진을 다양한 각도로 찍어 데이터 증가
     ┌──────────────────────────────────────────┐
     │ 원본 → 좌우반전 → 회전 → 밝기조정 → 줌  │
     │  🐱      🐱       🐱      🐱       🐱    │
     │         (좌우)   (15도)  (밝게)   (확대)  │
     └──────────────────────────────────────────┘
""")

def horizontal_flip(image):
    """좌우 반전"""
    return [row[::-1] for row in image]

def add_brightness(image, delta):
    """밝기 조정"""
    return [[max(0, min(1.0, p + delta)) for p in row] for row in image]

def random_crop(image, crop_h, crop_w):
    """랜덤 크롭"""
    h, w = len(image), len(image[0])
    start_i = random.randint(0, h - crop_h)
    start_j = random.randint(0, w - crop_w)
    return [row[start_j:start_j + crop_w] for row in image[start_i:start_i + crop_h]]

# 증강 시연
sample = [[0.1, 0.5, 0.9], [0.2, 0.6, 0.8], [0.3, 0.7, 0.4]]
flipped = horizontal_flip(sample)
brighter = add_brightness(sample, 0.2)
print(f"  원본:     {sample}")
print(f"  좌우반전: {flipped}")
print(f"  밝기+0.2: {[[f'{v:.1f}' for v in row] for row in brighter]}")

# 실제 코드: 이미지 전처리
# 실제 코드: # 정규화
# 실제 코드: x_train = x_train.astype('float32') / 255.0
# 실제 코드:
# 실제 코드: # 데이터 증강
# 실제 코드: data_aug = tf.keras.Sequential([
# 실제 코드:     tf.keras.layers.RandomFlip("horizontal"),
# 실제 코드:     tf.keras.layers.RandomRotation(0.1),
# 실제 코드:     tf.keras.layers.RandomZoom(0.1),
# 실제 코드: ])


# ═══════════════════════════════════════════════════════════════════════════════
# 3. MNIST/CIFAR-10 데이터셋 구조
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("3. 유명 데이터셋 구조")
print("=" * 70)

print("""
■ MNIST (손글씨 숫자):
  - 학습: 60,000장, 테스트: 10,000장
  - 이미지 크기: 28 x 28 x 1 (흑백)
  - 클래스: 10개 (0~9)
  - 형태: x_train.shape = (60000, 28, 28)
          y_train.shape = (60000,)  ← 정수 라벨

■ CIFAR-10 (자연 이미지):
  - 학습: 50,000장, 테스트: 10,000장
  - 이미지 크기: 32 x 32 x 3 (컬러 RGB)
  - 클래스: 10개 (비행기, 자동차, 새, 고양이, ...)
  - 형태: x_train.shape = (50000, 32, 32, 3)

■ ImageNet (대규모):
  - 1,400만+ 이미지
  - 1,000개 클래스
  - 이미지 크기: 다양 (보통 224x224으로 리사이즈)
""")

# 가상 MNIST 데이터 생성
def generate_toy_mnist(n_samples=100):
    """간단한 가상 MNIST 데이터 생성"""
    X, Y = [], []
    for _ in range(n_samples):
        label = random.randint(0, 9)
        # 28x28 흑백 이미지 시뮬레이션 (단순 패턴)
        image = [[0.0] * 28 for _ in range(28)]
        # 숫자에 따라 다른 패턴 생성
        for i in range(28):
            for j in range(28):
                # label에 따라 다른 영역에 값을 넣어 차별화
                if (i + j + label) % (label + 2) == 0:
                    image[i][j] = random.uniform(0.5, 1.0)
                else:
                    image[i][j] = random.uniform(0.0, 0.2)
        X.append(image)
        Y.append(label)
    return X, Y

print("■ 가상 MNIST 데이터 생성:")
X_train, Y_train = generate_toy_mnist(200)
X_test, Y_test = generate_toy_mnist(50)
print(f"  학습 데이터: {len(X_train)}장, 테스트: {len(X_test)}장")
print(f"  이미지 크기: {len(X_train[0])}x{len(X_train[0][0])}")
print(f"  라벨 분포: ", end="")
label_counts = {}
for y in Y_train:
    label_counts[y] = label_counts.get(y, 0) + 1
for k in sorted(label_counts):
    print(f"{k}:{label_counts[k]} ", end="")
print()

# ASCII 이미지 표시
print(f"\n  가상 이미지 샘플 (라벨={Y_train[0]}):")
for i in range(0, 28, 4):  # 7줄만 표시
    line = "  "
    for j in range(0, 28, 2):  # 14칸
        val = X_train[0][i][j]
        if val > 0.7:
            line += "██"
        elif val > 0.4:
            line += "▓▓"
        elif val > 0.2:
            line += "░░"
        else:
            line += "  "
    print(line)

# 실제 코드: MNIST 로드
# 실제 코드: (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
# 실제 코드: x_train = x_train.reshape(-1, 28, 28, 1).astype('float32') / 255.0
# 실제 코드:
# 실제 코드: # CIFAR-10 로드
# 실제 코드: (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
# 실제 코드: x_train = x_train.astype('float32') / 255.0


# ═══════════════════════════════════════════════════════════════════════════════
# 4. LeNet-5 스타일 CNN 구현
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("4. LeNet-5 스타일 CNN 구현")
print("=" * 70)

print("""
■ LeNet-5 (1998, Yann LeCun)
  최초의 성공적인 CNN 아키텍처 (우편번호 인식)

  구조:
  ┌─────────────────────────────────────────────────────────┐
  │  입력: 28x28x1                                          │
  │  ↓ Conv2D(6, 5x5)  → 24x24x6                           │
  │  ↓ MaxPool(2x2)    → 12x12x6                           │
  │  ↓ Conv2D(16, 5x5) → 8x8x16                            │
  │  ↓ MaxPool(2x2)    → 4x4x16                            │
  │  ↓ Flatten          → 256                                │
  │  ↓ Dense(120, relu)                                     │
  │  ↓ Dense(84, relu)                                      │
  │  ↓ Dense(10, softmax)                                   │
  └─────────────────────────────────────────────────────────┘
""")

def conv2d(image, kernel, stride=1, padding=0):
    """2D 합성곱"""
    h, w = len(image), len(image[0])
    kh, kw = len(kernel), len(kernel[0])
    if padding > 0:
        padded = [[0.0] * (w + 2 * padding) for _ in range(h + 2 * padding)]
        for i in range(h):
            for j in range(w):
                padded[i + padding][j + padding] = image[i][j]
        image = padded
        h, w = len(image), len(image[0])
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

def relu_2d(feature_map):
    """2D ReLU"""
    return [[max(0.0, val) for val in row] for row in feature_map]

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

def flatten(tensor):
    """다차원 → 1D"""
    if isinstance(tensor[0], list):
        result = []
        for item in tensor:
            if isinstance(item[0], list):
                for sub in item:
                    result.extend(sub)
            else:
                result.extend(item)
        return result
    return tensor

# LeNet 시뮬레이션 (축소 버전: 8x8 입력)
print("■ LeNet 시뮬레이션 (축소: 8x8 입력):")
small_image = [[random.random() for _ in range(8)] for _ in range(8)]

# Step 1: Conv2D(1필터, 3x3)
kernel1 = [[random.gauss(0, 0.5) for _ in range(3)] for _ in range(3)]
conv1_out = conv2d(small_image, kernel1)
conv1_relu = relu_2d(conv1_out)
print(f"  입력:                {8}x{8}")
print(f"  Conv2D(3x3) + ReLU: {len(conv1_relu)}x{len(conv1_relu[0])}")

# Step 2: MaxPool(2x2)
pool1_out = max_pool2d(conv1_relu)
print(f"  MaxPool(2x2):       {len(pool1_out)}x{len(pool1_out[0])}")

# Step 3: Conv2D(1필터, 3x3) 한 번 더 - pool이 작아서 padding 사용
# 3x3에서 3x3 커널은 1x1 출력이므로, 바로 flatten
flat = flatten(pool1_out)
print(f"  Flatten:            ({len(flat)},)")

# Step 4: Dense
def simple_dense(inputs, out_size, activation='relu'):
    W = [[random.gauss(0, 0.3) for _ in range(out_size)] for _ in range(len(inputs))]
    b = [0.0] * out_size
    outputs = []
    for j in range(out_size):
        z = sum(inputs[i] * W[i][j] for i in range(len(inputs))) + b[j]
        if activation == 'relu':
            z = max(0.0, z)
        outputs.append(z)
    if activation == 'softmax':
        max_v = max(outputs)
        exp_v = [math.exp(o - max_v) for o in outputs]
        s = sum(exp_v)
        outputs = [e / s for e in exp_v]
    return outputs

dense1 = simple_dense(flat, 10, 'relu')
print(f"  Dense(10, relu):    ({len(dense1)},)")

output = simple_dense(dense1, 3, 'softmax')
print(f"  Dense(3, softmax):  ({len(output)},)")
print(f"  예측 확률:          {[f'{p:.4f}' for p in output]}")
print(f"  예측 클래스:        {output.index(max(output))}")

# 실제 코드: LeNet-5 구현
# 실제 코드: model = tf.keras.Sequential([
# 실제 코드:     tf.keras.layers.Conv2D(6, (5,5), activation='relu', input_shape=(28,28,1)),
# 실제 코드:     tf.keras.layers.MaxPooling2D((2,2)),
# 실제 코드:     tf.keras.layers.Conv2D(16, (5,5), activation='relu'),
# 실제 코드:     tf.keras.layers.MaxPooling2D((2,2)),
# 실제 코드:     tf.keras.layers.Flatten(),
# 실제 코드:     tf.keras.layers.Dense(120, activation='relu'),
# 실제 코드:     tf.keras.layers.Dense(84, activation='relu'),
# 실제 코드:     tf.keras.layers.Dense(10, activation='softmax')
# 실제 코드: ])


# ═══════════════════════════════════════════════════════════════════════════════
# 5. 파라미터 수 상세 계산
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("5. CNN 파라미터 수 상세 계산")
print("=" * 70)

print("""
■ 각 레이어별 파라미터 수 공식:

  Dense(units):
    params = input_size * units + units

  Conv2D(filters, kernel):
    params = (kernel_h * kernel_w * input_channels + 1) * filters
    "+1"은 각 필터의 편향(bias)

  MaxPooling2D:
    params = 0  (학습 가능 파라미터 없음!)

  BatchNormalization:
    params = 4 * channels  (gamma, beta, moving_mean, moving_var)
    학습 가능: 2 * channels (gamma, beta)

  Flatten:
    params = 0  (형태만 변환)
""")

# MNIST CNN 파라미터 계산
print("■ MNIST CNN 파라미터 계산:")
layers_info = [
    ("Conv2D(32, 3x3)", "26x26x32", (3*3*1+1)*32),
    ("MaxPool(2x2)", "13x13x32", 0),
    ("Conv2D(64, 3x3)", "11x11x64", (3*3*32+1)*64),
    ("MaxPool(2x2)", "5x5x64", 0),
    ("Flatten", "1600", 0),
    ("Dense(128, relu)", "128", 1600*128+128),
    ("Dropout(0.5)", "128", 0),
    ("Dense(10, softmax)", "10", 128*10+10),
]

total = 0
print(f"  {'레이어':<25} {'출력 크기':<15} {'파라미터':>10}")
print(f"  {'─'*25} {'─'*15} {'─'*10}")
for name, shape, params in layers_info:
    total += params
    print(f"  {name:<25} {shape:<15} {params:>10,}")
print(f"  {'─'*25} {'─'*15} {'─'*10}")
print(f"  {'총 파라미터':<25} {'':<15} {total:>10,}")


# ═══════════════════════════════════════════════════════════════════════════════
# 6. 필터(커널)가 뭘 학습하는지
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("6. 필터(커널)가 학습하는 것")
print("=" * 70)

print("""
■ 각 레이어의 필터가 학습하는 패턴:

  초기 레이어 (Conv2D #1):
  - 에지(가장자리), 색상 변화, 간단한 텍스처
  - 마치 윤곽선을 그리는 것!

  중간 레이어 (Conv2D #2~3):
  - 코너, 원, 텍스처 패턴
  - 간단한 형태 조합

  깊은 레이어 (Conv2D #4+):
  - 눈, 코, 바퀴 같은 부분 객체
  - 고수준 패턴

■ 대표적인 필터 패턴:
""")

# 유명한 에지 감지 필터들
filters = {
    "수평 에지 감지": [[-1, -1, -1], [0, 0, 0], [1, 1, 1]],
    "수직 에지 감지": [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]],
    "대각선 에지":    [[-1, -1, 0], [-1, 0, 1], [0, 1, 1]],
    "샤프닝":        [[0, -1, 0], [-1, 5, -1], [0, -1, 0]],
    "가우시안 블러":  [[1/16, 2/16, 1/16], [2/16, 4/16, 2/16], [1/16, 2/16, 1/16]],
    "소벨 X":        [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
}

# 테스트 이미지 (수직선 포함)
test_image = [
    [0, 0, 1, 1, 0, 0],
    [0, 0, 1, 1, 0, 0],
    [0, 0, 1, 1, 0, 0],
    [0, 0, 1, 1, 0, 0],
    [0, 0, 1, 1, 0, 0],
    [0, 0, 1, 1, 0, 0],
]

print("  테스트 이미지 (수직선):")
for row in test_image:
    line = "  "
    for val in row:
        line += "██" if val == 1 else "  "
    print(line)

for name, kernel in list(filters.items())[:3]:
    result = conv2d(test_image, kernel)
    print(f"\n  {name} 필터 적용 결과:")
    for row in result:
        line = "  "
        for val in row:
            if val > 1:
                line += "██"
            elif val > 0:
                line += "▓▓"
            elif val < -1:
                line += "░░"
            else:
                line += "  "
        print(line)

# 실제 코드: 필터 시각화
# 실제 코드: # 학습된 필터 가져오기
# 실제 코드: filters, biases = model.layers[0].get_weights()
# 실제 코드: print(filters.shape)  # (3, 3, 1, 32) → 32개의 3x3 필터
# 실제 코드:
# 실제 코드: # 시각화
# 실제 코드: import matplotlib.pyplot as plt
# 실제 코드: fig, axes = plt.subplots(4, 8, figsize=(12, 6))
# 실제 코드: for i, ax in enumerate(axes.flat):
# 실제 코드:     ax.imshow(filters[:, :, 0, i], cmap='gray')
# 실제 코드:     ax.axis('off')
# 실제 코드: plt.show()


# ═══════════════════════════════════════════════════════════════════════════════
# 7. 특징 맵(Feature Map) 시각화
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("7. 특징 맵(Feature Map) 시각화")
print("=" * 70)

print("""
■ 특징 맵이란?
  필터를 이미지에 적용한 결과물
  각 필터는 다른 특징을 감지 → 다른 특징 맵 생성

  32개 필터 → 32개의 특징 맵
  각 맵은 "이 위치에 내가 찾는 패턴이 있나?" 라는 열 지도
""")

# 여러 필터로 특징 맵 생성
image_6x6 = [
    [0, 0, 0, 1, 1, 0],
    [0, 0, 1, 1, 0, 0],
    [0, 1, 1, 0, 0, 0],
    [0, 1, 1, 0, 0, 0],
    [0, 0, 1, 1, 0, 0],
    [0, 0, 0, 1, 1, 0],
]

print("  입력 이미지 (다이아몬드 패턴):")
for row in image_6x6:
    line = "    "
    for val in row:
        line += "██" if val == 1 else "  "
    print(line)

for name in ["수직 에지 감지", "수평 에지 감지"]:
    kernel = filters[name]
    result = conv2d(image_6x6, kernel)
    print(f"\n  {name} 특징 맵:")
    for row in result:
        line = "    "
        for val in row:
            if abs(val) > 2:
                line += "██"
            elif abs(val) > 1:
                line += "▓▓"
            elif abs(val) > 0.5:
                line += "░░"
            else:
                line += "  "
        print(line)

# 실제 코드: 특징 맵 추출
# 실제 코드: # 중간 레이어의 출력을 보는 모델 생성
# 실제 코드: layer_outputs = [layer.output for layer in model.layers[:4]]
# 실제 코드: activation_model = tf.keras.Model(inputs=model.input, outputs=layer_outputs)
# 실제 코드: activations = activation_model.predict(test_image[np.newaxis, ...])
# 실제 코드:
# 실제 코드: # 시각화
# 실제 코드: for layer_activation in activations:
# 실제 코드:     n_features = layer_activation.shape[-1]
# 실제 코드:     for i in range(min(8, n_features)):
# 실제 코드:         plt.subplot(1, 8, i+1)
# 실제 코드:         plt.imshow(layer_activation[0, :, :, i], cmap='viridis')
# 실제 코드:     plt.show()


# ═══════════════════════════════════════════════════════════════════════════════
# 8. [실습] 손글씨 숫자 분류 (개념적 구현)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("8. [실습] 손글씨 숫자 분류 시뮬레이션")
print("=" * 70)

class ToyCNN:
    """간단한 CNN 시뮬레이션"""
    def __init__(self):
        # 3x3 필터 3개
        self.filters = [
            [[random.gauss(0, 0.3) for _ in range(3)] for _ in range(3)]
            for _ in range(3)
        ]

    def extract_features(self, image):
        """특징 추출 파이프라인"""
        features = []
        for kernel in self.filters:
            # Conv
            fm = conv2d(image, kernel, padding=0)
            # ReLU
            fm = relu_2d(fm)
            # 간이 Global Average Pooling
            total = sum(val for row in fm for val in row)
            count = sum(1 for row in fm for _ in row)
            features.append(total / max(count, 1))
        return features

    def classify(self, features, n_classes=10):
        """분류 (간이 버전)"""
        # 간단한 분류 로직
        scores = []
        for c in range(n_classes):
            score = sum(f * random.gauss(0, 1) for f in features)
            scores.append(score)
        # softmax
        max_s = max(scores)
        exp_s = [math.exp(s - max_s) for s in scores]
        total = sum(exp_s)
        probs = [e / total for e in exp_s]
        return probs

# CNN 시뮬레이션
cnn = ToyCNN()

print("\n■ CNN 분류 파이프라인 시뮬레이션:")
print(f"  필터 수: {len(cnn.filters)}")
print(f"  필터 크기: 3x3")

# 몇 개 샘플 처리
n_demo = 5
for i in range(n_demo):
    # 간소화를 위해 8x8 이미지 사용
    small_img = [[X_train[i][r][c] for c in range(0, 28, 4)] for r in range(0, 28, 4)]
    features = cnn.extract_features(small_img)
    probs = cnn.classify(features)
    predicted = probs.index(max(probs))
    print(f"  샘플 {i}: 실제={Y_train[i]}, 예측={predicted}, "
          f"확률={max(probs):.2%}, 특징={[f'{f:.3f}' for f in features]}")

print("""
  ※ 이것은 랜덤 가중치의 시뮬레이션이므로 정확도가 낮습니다.
     실제 학습(역전파 + 옵티마이저)을 통해 정확도가 올라갑니다!
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 9. 유명 CNN 아키텍처 비교
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("9. 유명 CNN 아키텍처 비교")
print("=" * 70)

print("""
■ CNN 역사와 주요 아키텍처:

  ┌──────────────┬──────┬────────────────┬────────────────────────────┐
  │ 모델          │ 년도  │ 파라미터 수    │ 핵심 아이디어               │
  ├──────────────┼──────┼────────────────┼────────────────────────────┤
  │ LeNet-5      │ 1998 │ 60K           │ CNN의 시작                  │
  │ AlexNet      │ 2012 │ 60M           │ GPU 학습, ReLU, Dropout     │
  │ VGG16        │ 2014 │ 138M          │ 3x3 필터만 사용, 깊은 구조  │
  │ GoogLeNet    │ 2014 │ 6.8M          │ Inception 모듈              │
  │ ResNet-50    │ 2015 │ 25.6M         │ 잔차 연결 (Skip Connection) │
  │ MobileNet    │ 2017 │ 3.4M          │ Depthwise Separable Conv    │
  │ EfficientNet │ 2019 │ 5.3~66M       │ 모델 스케일링 최적화        │
  └──────────────┴──────┴────────────────┴────────────────────────────┘

■ 실용적 선택:
  - 빠른 프로토타입: MobileNet, EfficientNet-B0
  - 높은 정확도:     EfficientNet-B4~B7, ResNet
  - 모바일/엣지:    MobileNet V3, EfficientNet-Lite
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 10. Receptive Field (수용 영역)
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("10. Receptive Field (수용 영역)")
print("=" * 70)

print("""
■ 수용 영역(Receptive Field)이란?
  출력의 한 뉴런이 "볼 수 있는" 입력 영역의 크기

  비유: 창문의 크기!
  - 1층 Conv(3x3): 3x3 영역을 봄
  - 2층 Conv(3x3): 5x5 영역을 봄 (3+3-1=5)
  - 3층 Conv(3x3): 7x7 영역을 봄 (5+3-1=7)

  층을 깊게 쌓을수록 → 더 넓은 영역을 보게 됨!
  → 더 큰 패턴(고수준 특징)을 인식할 수 있음

■ VGG가 3x3 필터만 쓰는 이유:
  3x3 두 번 = 5x5와 같은 수용 영역
  파라미터: 3*3*2 = 18  vs  5*5 = 25
  → 더 적은 파라미터로 같은 효과 + 비선형성 추가!
""")

# 수용 영역 계산
def calc_receptive_field(layers):
    """수용 영역 크기 계산"""
    rf = 1
    stride_product = 1
    for kernel_size, stride in layers:
        rf = rf + (kernel_size - 1) * stride_product
        stride_product *= stride
    return rf

architectures = {
    "Conv(3x3) x 1": [(3, 1)],
    "Conv(3x3) x 2": [(3, 1), (3, 1)],
    "Conv(3x3) x 3": [(3, 1), (3, 1), (3, 1)],
    "Conv(5x5) x 1": [(5, 1)],
    "Conv(3x3)+Pool(2x2)+Conv(3x3)": [(3, 1), (2, 2), (3, 1)],
}

print("\n■ 수용 영역 크기 비교:")
for name, layers in architectures.items():
    rf = calc_receptive_field(layers)
    print(f"  {name:40s} → RF = {rf}x{rf}")

# 실제 코드: 완전한 MNIST CNN 학습
# 실제 코드: import tensorflow as tf
# 실제 코드:
# 실제 코드: (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
# 실제 코드: x_train = x_train.reshape(-1, 28, 28, 1).astype('float32') / 255.0
# 실제 코드: x_test = x_test.reshape(-1, 28, 28, 1).astype('float32') / 255.0
# 실제 코드:
# 실제 코드: model = tf.keras.Sequential([
# 실제 코드:     tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=(28,28,1)),
# 실제 코드:     tf.keras.layers.MaxPooling2D((2,2)),
# 실제 코드:     tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
# 실제 코드:     tf.keras.layers.MaxPooling2D((2,2)),
# 실제 코드:     tf.keras.layers.Flatten(),
# 실제 코드:     tf.keras.layers.Dense(128, activation='relu'),
# 실제 코드:     tf.keras.layers.Dropout(0.5),
# 실제 코드:     tf.keras.layers.Dense(10, activation='softmax')
# 실제 코드: ])
# 실제 코드:
# 실제 코드: model.compile(optimizer='adam',
# 실제 코드:               loss='sparse_categorical_crossentropy',
# 실제 코드:               metrics=['accuracy'])
# 실제 코드:
# 실제 코드: model.fit(x_train, y_train, epochs=5, batch_size=64,
# 실제 코드:           validation_split=0.1)
# 실제 코드:
# 실제 코드: test_loss, test_acc = model.evaluate(x_test, y_test)
# 실제 코드: print(f"테스트 정확도: {test_acc:.4f}")  # ~99.2%


print("\n" + "=" * 70)
print("요약: CNN과 이미지 처리 학습 완료!")
print("=" * 70)
print("""
  1. CNN: 합성곱으로 공간 정보 유지하며 특징 추출
  2. 전처리: 정규화(0~1), 리사이즈, 데이터 증강
  3. MNIST: 28x28 흑백, CIFAR: 32x32 컬러
  4. LeNet: Conv→Pool→Conv→Pool→Flatten→Dense
  5. 필터: 초기=에지, 중간=텍스처, 깊은=부분 객체
  6. 수용 영역: 층이 깊을수록 넓어짐
  7. VGG 전략: 작은 필터(3x3) 여러 개 > 큰 필터 하나

  다음 단계 → 06_callbacks_training.py (콜백으로 학습 최적화!)
""")
