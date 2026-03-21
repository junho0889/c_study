# #########################################################################
#
#   PyTorch 학습 05단계: CNN (합성곱 신경망)
#   - Conv2d, Pooling, BatchNorm, Dropout, LeNet/VGG 스타일 -
#   # 실행 방법: python 05_cnn.py (개념 학습용, PyTorch 없이 실행 가능)
#   # PyTorch 설치: pip install torch torchvision
#
# #########################################################################

import math
import random

random.seed(42)

# ===============================================================================
#  1. CNN이란?
# ===============================================================================
print("=" * 70)
print("Part 1: CNN (합성곱 신경망) 개요")
print("=" * 70)

print("""
CNN = Convolutional Neural Network (합성곱 신경망)
이미지 인식의 핵심 아키텍처입니다.

비유: 돋보기로 그림 분석하기
  - 작은 돋보기(커널)로 그림의 각 부분을 살펴봄
  - 테두리, 질감, 패턴 등의 특징을 추출
  - 작은 특징 → 중간 특징 → 큰 특징 순서로 인식
    (가장자리 → 눈코입 → 얼굴)

완전연결(FC)과의 차이:
  FC: 모든 픽셀을 일렬로 펴서 처리 → 공간 정보 상실
  CNN: 공간 구조를 유지하며 처리 → 위치/패턴 인식 가능
""")


# ===============================================================================
#  2. nn.Conv2d - 2차원 합성곱
# ===============================================================================
print("\n" + "=" * 70)
print("Part 2: nn.Conv2d (2차원 합성곱)")
print("=" * 70)

print("""
Conv2d(in_channels, out_channels, kernel_size, stride=1, padding=0)

  - in_channels: 입력 채널 수 (흑백=1, RGB=3)
  - out_channels: 출력 채널 수 (= 필터/커널 개수)
  - kernel_size: 커널(필터) 크기 (3이면 3x3)
  - stride: 커널 이동 간격 (기본 1)
  - padding: 입력 테두리에 0을 추가 (크기 유지용)
""")


def conv2d(input_2d, kernel, stride=1, padding=0):
    """2D 합성곱 연산 구현"""
    H, W = len(input_2d), len(input_2d[0])
    KH, KW = len(kernel), len(kernel[0])

    # 패딩 적용
    if padding > 0:
        padded = [[0.0] * (W + 2 * padding) for _ in range(H + 2 * padding)]
        for i in range(H):
            for j in range(W):
                padded[i + padding][j + padding] = input_2d[i][j]
        input_2d = padded
        H, W = len(padded), len(padded[0])

    # 출력 크기 계산
    out_H = (H - KH) // stride + 1
    out_W = (W - KW) // stride + 1
    output = [[0.0] * out_W for _ in range(out_H)]

    # 합성곱 수행
    for i in range(out_H):
        for j in range(out_W):
            val = 0.0
            for ki in range(KH):
                for kj in range(KW):
                    val += input_2d[i * stride + ki][j * stride + kj] * kernel[ki][kj]
            output[i][j] = val

    return output


# 합성곱 예제
print("\n--- 합성곱 연산 예제 ---")
input_image = [
    [1, 2, 3, 0, 1],
    [0, 1, 2, 3, 1],
    [1, 3, 1, 0, 2],
    [2, 1, 0, 1, 3],
    [0, 2, 1, 2, 1],
]

# 가장자리 감지 커널 (수직)
vertical_edge_kernel = [
    [-1, 0, 1],
    [-1, 0, 1],
    [-1, 0, 1],
]

# 가장자리 감지 커널 (수평)
horizontal_edge_kernel = [
    [-1, -1, -1],
    [ 0,  0,  0],
    [ 1,  1,  1],
]

result = conv2d(input_image, vertical_edge_kernel, stride=1, padding=0)
print(f"입력 (5x5):")
for row in input_image:
    print(f"  {row}")
print(f"\n수직 에지 커널 (3x3):")
for row in vertical_edge_kernel:
    print(f"  {row}")
print(f"\n합성곱 결과 (3x3):")
for row in result:
    print(f"  [{', '.join(f'{v:5.1f}' for v in row)}]")

# 패딩 적용
result_padded = conv2d(input_image, vertical_edge_kernel, stride=1, padding=1)
print(f"\n패딩=1 적용 결과 (5x5 → 5x5, 크기 유지!):")
for row in result_padded:
    print(f"  [{', '.join(f'{v:5.1f}' for v in row)}]")

# 실제 PyTorch 코드:
# conv = nn.Conv2d(in_channels=1, out_channels=16, kernel_size=3, stride=1, padding=1)
# # 입력: (batch, channels, H, W) = (1, 1, 5, 5)
# x = torch.randn(1, 1, 5, 5)
# out = conv(x)  # (1, 16, 5, 5) - padding=1이므로 크기 유지


# ===============================================================================
#  3. 출력 크기 계산 공식
# ===============================================================================
print("\n" + "=" * 70)
print("Part 3: 출력 크기 계산 공식")
print("=" * 70)

print("""
출력 크기 = (입력크기 - 커널크기 + 2*패딩) / 스트라이드 + 1
         = (H - K + 2P) / S + 1

이 공식은 매우 중요합니다! CNN 설계 시 항상 사용합니다.
""")

def calc_output_size(input_size, kernel_size, stride=1, padding=0):
    return (input_size - kernel_size + 2 * padding) // stride + 1

examples = [
    (28, 3, 1, 0),   # MNIST: 28x28, 3x3 커널
    (28, 3, 1, 1),   # 패딩으로 크기 유지
    (28, 5, 1, 2),   # 5x5 커널, 패딩 2
    (28, 3, 2, 0),   # 스트라이드 2 (다운샘플링)
    (224, 7, 2, 3),  # ResNet 첫 레이어
]

print(f"{'입력':>6} {'커널':>6} {'스트라이드':>8} {'패딩':>6} {'출력':>6}")
print("-" * 40)
for h, k, s, p in examples:
    out = calc_output_size(h, k, s, p)
    print(f"{h:>6} {k:>6} {s:>8} {p:>6} {out:>6}")


# ===============================================================================
#  4. 풀링 (Pooling)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 4: Pooling (풀링)")
print("=" * 70)

print("""
풀링 = 특성 맵의 크기를 줄이는 다운샘플링 연산

MaxPool2d: 영역 내 최대값 선택 (가장 강한 특징 유지)
AvgPool2d: 영역 내 평균값 계산

비유: 사진 축소
  - MaxPool: 각 영역에서 가장 밝은 점만 남기기
  - AvgPool: 각 영역의 평균 밝기로 대체
""")

def max_pool2d(input_2d, pool_size=2, stride=None):
    """MaxPool2d 구현"""
    if stride is None:
        stride = pool_size
    H, W = len(input_2d), len(input_2d[0])
    out_H = (H - pool_size) // stride + 1
    out_W = (W - pool_size) // stride + 1
    output = [[0.0] * out_W for _ in range(out_H)]

    for i in range(out_H):
        for j in range(out_W):
            max_val = float('-inf')
            for ki in range(pool_size):
                for kj in range(pool_size):
                    val = input_2d[i * stride + ki][j * stride + kj]
                    max_val = max(max_val, val)
            output[i][j] = max_val
    return output

def avg_pool2d(input_2d, pool_size=2, stride=None):
    """AvgPool2d 구현"""
    if stride is None:
        stride = pool_size
    H, W = len(input_2d), len(input_2d[0])
    out_H = (H - pool_size) // stride + 1
    out_W = (W - pool_size) // stride + 1
    output = [[0.0] * out_W for _ in range(out_H)]

    for i in range(out_H):
        for j in range(out_W):
            total = 0.0
            for ki in range(pool_size):
                for kj in range(pool_size):
                    total += input_2d[i * stride + ki][j * stride + kj]
            output[i][j] = total / (pool_size * pool_size)
    return output

feature_map = [
    [1, 3, 2, 4],
    [5, 6, 1, 2],
    [3, 2, 8, 1],
    [7, 4, 3, 5],
]

max_result = max_pool2d(feature_map, pool_size=2)
avg_result = avg_pool2d(feature_map, pool_size=2)

print(f"\n입력 (4x4):")
for row in feature_map:
    print(f"  {row}")
print(f"\nMaxPool2d(2) 결과 (2x2):")
for row in max_result:
    print(f"  {row}")
print(f"\nAvgPool2d(2) 결과 (2x2):")
for row in avg_result:
    print(f"  {row}")

# 실제 PyTorch 코드:
# pool = nn.MaxPool2d(kernel_size=2, stride=2)
# x = torch.tensor([[[[1,3,2,4],[5,6,1,2],[3,2,8,1],[7,4,3,5]]]], dtype=torch.float)
# out = pool(x)  # (1,1,2,2) → [[6,4],[7,8]]


# ===============================================================================
#  5. BatchNorm2d
# ===============================================================================
print("\n" + "=" * 70)
print("Part 5: BatchNorm2d (배치 정규화)")
print("=" * 70)

print("""
BatchNorm = 각 배치의 활성화 값을 정규화 (평균 0, 분산 1로)

왜 필요한가?
  - Internal Covariate Shift 방지 (레이어 통과할수록 분포가 변하는 문제)
  - 학습 속도 향상 + 큰 학습률 사용 가능
  - 약한 정규화 효과 (과적합 방지)

[주의] 학습/추론 차이:
  학습(train): 현재 배치의 평균/분산 사용 + 이동 평균 업데이트
  추론(eval):  학습 중 축적한 이동 평균/분산 사용
  → model.eval() 호출 필수!

수식: y = (x - mean) / sqrt(var + eps) * gamma + beta
  gamma, beta: 학습 가능한 파라미터 (스케일, 시프트)
""")

def batch_norm_1d(data, gamma=1.0, beta=0.0, eps=1e-5):
    """1D 배치 정규화 시뮬레이션"""
    mean = sum(data) / len(data)
    var = sum((x - mean) ** 2 for x in data) / len(data)
    normalized = [(x - mean) / math.sqrt(var + eps) for x in data]
    output = [gamma * x + beta for x in normalized]
    return output, mean, var

data = [10.0, 20.0, 30.0, 40.0, 50.0]
bn_out, mean, var = batch_norm_1d(data)
print(f"\n입력: {data}")
print(f"평균: {mean}, 분산: {var}")
print(f"정규화 후: [{', '.join(f'{v:.4f}' for v in bn_out)}]")

# 실제 PyTorch 코드:
# bn = nn.BatchNorm2d(num_features=16)  # 16채널
# x = torch.randn(32, 16, 28, 28)       # (batch, channels, H, W)
# out = bn(x)                            # 같은 shape


# ===============================================================================
#  6. Dropout
# ===============================================================================
print("\n" + "=" * 70)
print("Part 6: Dropout")
print("=" * 70)

print("""
Dropout = 학습 시 일부 뉴런을 랜덤하게 비활성화

비유: 팀 프로젝트에서 매번 다른 팀원이 결석
  → 한 명에게 의존하지 않고 모두가 역할을 배움
  → 과적합 방지!

주의: 추론 시에는 모든 뉴런 사용 (model.eval()로 전환)
""")

def dropout(data, p=0.5, training=True):
    """Dropout 구현"""
    if not training:
        return data  # 추론 시에는 그대로 통과

    scale = 1.0 / (1 - p)  # 스케일 보정 (학습 시 꺼진 만큼 키워줌)
    return [x * scale if random.random() > p else 0.0 for x in data]

data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
print(f"\n원본: {data}")
for i in range(3):
    dropped = dropout(data, p=0.5, training=True)
    print(f"Dropout(p=0.5) 학습 {i+1}: [{', '.join(f'{v:.1f}' for v in dropped)}]")
no_drop = dropout(data, p=0.5, training=False)
print(f"Dropout(p=0.5) 추론:    [{', '.join(f'{v:.1f}' for v in no_drop)}]")

# 실제 PyTorch 코드:
# dropout = nn.Dropout(p=0.5)
# model.train()  # dropout 활성
# model.eval()   # dropout 비활성


# ===============================================================================
#  7. LeNet / VGG 스타일 CNN
# ===============================================================================
print("\n" + "=" * 70)
print("Part 7: LeNet / VGG 스타일 CNN 구현")
print("=" * 70)

print("""
LeNet-5 (1998, Yann LeCun):
  최초의 성공적인 CNN. 손글씨 숫자 인식용.
  구조: Conv → Pool → Conv → Pool → FC → FC → FC

VGG (2014, Oxford):
  "작은 필터(3x3)를 깊게 쌓자"
  구조: [Conv3x3 → Conv3x3 → Pool] × N → FC × 3
""")


class LeNet5Simulator:
    """LeNet-5 구조 시뮬레이션 (크기 변화 추적)"""

    def __init__(self):
        self.layers = [
            ("Conv2d(1, 6, 5)", 5, 1, 0, 6),       # 28→24
            ("MaxPool2d(2)", 2, 2, 0, 6),            # 24→12
            ("Conv2d(6, 16, 5)", 5, 1, 0, 16),      # 12→8
            ("MaxPool2d(2)", 2, 2, 0, 16),           # 8→4
            ("Flatten", 0, 0, 0, 256),               # 16*4*4=256
            ("Linear(256, 120)", 0, 0, 0, 120),
            ("Linear(120, 84)", 0, 0, 0, 84),
            ("Linear(84, 10)", 0, 0, 0, 10),
        ]

    def trace(self, input_size=28, in_channels=1):
        """각 레이어의 출력 크기 추적"""
        h = input_size
        ch = in_channels
        print(f"\n  입력: ({ch}, {h}, {h})")
        for name, k, s, p, out_ch in self.layers:
            if "Conv" in name or "Pool" in name:
                h = (h - k + 2 * p) // s + 1
                ch = out_ch
                print(f"  → {name:25s} → ({ch}, {h}, {h})")
            elif "Flatten" in name:
                flat = ch * h * h
                print(f"  → {'Flatten':25s} → ({flat},)")
            elif "Linear" in name:
                print(f"  → {name:25s} → ({out_ch},)")

print("\n--- LeNet-5 구조 ---")
lenet = LeNet5Simulator()
lenet.trace(input_size=28)


class VGGBlockSimulator:
    """VGG 스타일 블록 시뮬레이션"""

    def __init__(self):
        self.blocks = [
            # block 1: Conv3x3 x2 + Pool
            [("Conv2d(3, 64, 3, p=1)", 3, 1, 1, 64),
             ("Conv2d(64, 64, 3, p=1)", 3, 1, 1, 64),
             ("MaxPool2d(2)", 2, 2, 0, 64)],
            # block 2
            [("Conv2d(64, 128, 3, p=1)", 3, 1, 1, 128),
             ("Conv2d(128, 128, 3, p=1)", 3, 1, 1, 128),
             ("MaxPool2d(2)", 2, 2, 0, 128)],
            # block 3
            [("Conv2d(128, 256, 3, p=1)", 3, 1, 1, 256),
             ("Conv2d(256, 256, 3, p=1)", 3, 1, 1, 256),
             ("Conv2d(256, 256, 3, p=1)", 3, 1, 1, 256),
             ("MaxPool2d(2)", 2, 2, 0, 256)],
        ]

    def trace(self, input_size=224, in_channels=3):
        h = input_size
        ch = in_channels
        print(f"\n  입력: ({ch}, {h}, {h})")
        for block_idx, block in enumerate(self.blocks):
            for name, k, s, p, out_ch in block:
                h = (h - k + 2 * p) // s + 1
                ch = out_ch
                print(f"  → {name:30s} → ({ch}, {h}, {h})")
            print()

print("\n--- VGG 스타일 구조 (처음 3블록) ---")
vgg = VGGBlockSimulator()
vgg.trace()


# ===============================================================================
#  8. 실습: CNN 분류기 완전 구현
# ===============================================================================
print("\n" + "=" * 70)
print("Part 8: 실습 - CNN 분류기 (순수 파이썬)")
print("=" * 70)

print("간단한 4x4 패턴 분류기 구현 (커널 기반 특징 추출)")

# 패턴 데이터: 4x4 이미지에서 수직선/수평선 분류
vertical_patterns = [
    [[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]],  # 수직선
    [[0,0,1,0],[0,0,1,0],[0,0,1,0],[0,0,1,0]],
    [[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0]],
]
horizontal_patterns = [
    [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],  # 수평선
    [[0,0,0,0],[0,0,0,0],[1,1,1,1],[0,0,0,0]],
    [[1,1,1,1],[0,0,0,0],[0,0,0,0],[0,0,0,0]],
]

# 수작업 커널 정의
v_kernel = [[1, -1], [1, -1]]   # 수직 감지
h_kernel = [[1, 1], [-1, -1]]   # 수평 감지

def simple_cnn_classify(image, v_kern, h_kern):
    """간단한 CNN 분류: 수직선 vs 수평선"""
    # Conv: 2x2 커널 적용
    v_map = conv2d(image, v_kern)
    h_map = conv2d(image, h_kern)

    # Global Average Pooling (특성 맵 전체 평균)
    v_score = sum(sum(abs(val) for val in row) for row in v_map) / (len(v_map) * len(v_map[0]))
    h_score = sum(sum(abs(val) for val in row) for row in h_map) / (len(h_map) * len(h_map[0]))

    return "수직선" if v_score > h_score else "수평선", v_score, h_score

print("\n--- 패턴 분류 결과 ---")
print("\n수직선 패턴:")
for i, pattern in enumerate(vertical_patterns):
    pred, v_s, h_s = simple_cnn_classify(pattern, v_kernel, h_kernel)
    print(f"  패턴 {i}: {pred} (수직점수={v_s:.2f}, 수평점수={h_s:.2f})")

print("\n수평선 패턴:")
for i, pattern in enumerate(horizontal_patterns):
    pred, v_s, h_s = simple_cnn_classify(pattern, v_kernel, h_kernel)
    print(f"  패턴 {i}: {pred} (수직점수={v_s:.2f}, 수평점수={h_s:.2f})")

# 실제 PyTorch CNN:
# class CNN(nn.Module):
#     def __init__(self, num_classes=10):
#         super().__init__()
#         self.features = nn.Sequential(
#             nn.Conv2d(1, 32, 3, padding=1),   # (1,28,28) → (32,28,28)
#             nn.BatchNorm2d(32),
#             nn.ReLU(),
#             nn.MaxPool2d(2),                   # → (32,14,14)
#
#             nn.Conv2d(32, 64, 3, padding=1),   # → (64,14,14)
#             nn.BatchNorm2d(64),
#             nn.ReLU(),
#             nn.MaxPool2d(2),                   # → (64,7,7)
#         )
#         self.classifier = nn.Sequential(
#             nn.Dropout(0.5),
#             nn.Linear(64 * 7 * 7, 128),
#             nn.ReLU(),
#             nn.Dropout(0.25),
#             nn.Linear(128, num_classes),
#         )
#
#     def forward(self, x):
#         x = self.features(x)
#         x = x.view(x.size(0), -1)   # Flatten
#         x = self.classifier(x)
#         return x
#
# model = CNN(num_classes=10)
# print(model)
# x = torch.randn(1, 1, 28, 28)
# out = model(x)  # (1, 10)


# ===============================================================================
#  9. CNN 전체 파이프라인 크기 추적
# ===============================================================================
print("\n" + "=" * 70)
print("Part 9: CNN 전체 파이프라인 설계")
print("=" * 70)

def design_cnn_pipeline(input_h, input_w, in_ch):
    """CNN 파이프라인 설계 및 크기 추적"""
    print(f"\n  입력: ({in_ch}, {input_h}, {input_w})")
    h, w, ch = input_h, input_w, in_ch

    layers = [
        ("Conv2d({}, 32, 3, p=1)".format(ch), 3, 1, 1, 32),
        ("ReLU", 0, 0, 0, 32),
        ("BatchNorm2d(32)", 0, 0, 0, 32),
        ("MaxPool2d(2)", 2, 2, 0, 32),
        ("Conv2d(32, 64, 3, p=1)", 3, 1, 1, 64),
        ("ReLU", 0, 0, 0, 64),
        ("BatchNorm2d(64)", 0, 0, 0, 64),
        ("MaxPool2d(2)", 2, 2, 0, 64),
        ("Conv2d(64, 128, 3, p=1)", 3, 1, 1, 128),
        ("ReLU", 0, 0, 0, 128),
        ("MaxPool2d(2)", 2, 2, 0, 128),
    ]

    for name, k, s, p, out_ch in layers:
        if "Conv" in name or "Pool" in name:
            h = (h - k + 2 * p) // s + 1
            w = (w - k + 2 * p) // s + 1
            ch = out_ch
        elif "ReLU" in name or "Batch" in name:
            pass  # 크기 변화 없음
        print(f"  → {name:30s} → ({ch}, {h}, {w})")

    flat = ch * h * w
    print(f"  → {'Flatten':30s} → ({flat},)")
    print(f"  → {'Linear({}, 256)'.format(flat):30s} → (256,)")
    print(f"  → {'Linear(256, 10)':30s} → (10,)")
    return flat

print("MNIST (28x28 흑백):")
design_cnn_pipeline(28, 28, 1)

print("\nCIFAR-10 (32x32 컬러):")
design_cnn_pipeline(32, 32, 3)


# ===============================================================================
#  핵심 정리
# ===============================================================================
print("\n" + "=" * 70)
print("핵심 정리")
print("=" * 70)
print("""
1. Conv2d: 커널(필터)로 특징 추출 (가장자리, 질감, 패턴)
2. 출력 크기: (H - K + 2P) / S + 1 (반드시 암기!)
3. MaxPool2d: 다운샘플링 (중요한 특징만 유지)
4. BatchNorm2d: 학습 안정화 (train/eval 모드 차이 주의)
5. Dropout: 과적합 방지 (학습 시만 활성)
6. CNN 구조: [Conv → BN → ReLU → Pool] × N → Flatten → FC

[주의] 흔한 실수:
   - Flatten 후 Linear 입력 크기 계산 틀림 (공식 확인!)
   - BatchNorm + Dropout 순서 혼동 (Conv → BN → ReLU → Dropout 권장)
   - model.eval() 안 하고 추론 → BN/Dropout 결과 달라짐
   - 입력 텐서 shape 착각 (PyTorch: batch, channels, H, W)
""")
