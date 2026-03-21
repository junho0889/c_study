# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   TensorFlow/Keras 학습 07단계: 전이학습 (Transfer Learning)
#   ─ 사전학습 모델, Feature Extraction, Fine-Tuning, 데이터 증강 ─
#   ■ 실행 방법: python 07_transfer_learning.py (개념 학습용 코드, TF 없이 실행 가능)
#   ■ TensorFlow 설치: pip install tensorflow
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import random

random.seed(42)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. 전이학습이란?
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("1. 전이학습 (Transfer Learning)이란?")
print("=" * 70)

print("""
■ 전이학습 = 다른 문제에서 배운 지식을 새로운 문제에 재사용

  비유: 피아노를 배운 사람이 건반악기를 더 빨리 배우는 것!
  - 음악 이론, 손가락 근육 기억 = 공통 지식 (전이!)
  - 건반 배열만 새로 배우면 됨

■ 딥러닝에서의 전이학습:
  ImageNet(1400만장, 1000클래스)으로 학습한 모델의 지식을
  나의 작은 데이터셋에 재사용!

  ┌──────────────────────────────────────────────┐
  │  ImageNet 학습 (수백만 장)                    │
  │  ↓                                            │
  │  사전학습 모델 (에지, 텍스처, 패턴 인식 능력)  │
  │  ↓                                            │
  │  나의 데이터 (수백~수천 장)                    │
  │  ↓                                            │
  │  높은 정확도! (처음부터 학습하는 것보다 훨씬!)  │
  └──────────────────────────────────────────────┘

■ 왜 효과적인가?
  1. 초기 레이어: 에지, 색상, 텍스처 → 모든 이미지에 공통!
  2. 중간 레이어: 패턴, 형태 → 대부분의 이미지에 유용
  3. 마지막 레이어: 특정 클래스 구분 → 문제에 따라 다름
     → 1,2는 재사용, 3만 새로 학습!
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. 사전학습 모델 소개
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("2. 사전학습 모델 (Pre-trained Models)")
print("=" * 70)

print("""
■ Keras에서 제공하는 사전학습 모델:

  ┌──────────────┬─────────┬──────────────┬────────────────────────┐
  │ 모델          │ 파라미터 │ Top-5 정확도  │ 특징                    │
  ├──────────────┼─────────┼──────────────┼────────────────────────┤
  │ VGG16        │ 138M    │ 90.1%        │ 단순 구조, 큰 모델      │
  │ VGG19        │ 144M    │ 90.0%        │ VGG16보다 깊음          │
  │ ResNet50     │ 25.6M   │ 92.1%        │ 잔차 연결, 매우 인기    │
  │ ResNet152    │ 60.2M   │ 93.1%        │ 더 깊은 ResNet          │
  │ InceptionV3  │ 23.9M   │ 93.7%        │ 다양한 크기 필터 동시   │
  │ MobileNetV2  │ 3.4M    │ 90.1%        │ 모바일용, 가벼움        │
  │ EfficientB0  │ 5.3M    │ 93.3%        │ 효율적 스케일링         │
  │ EfficientB7  │ 66M     │ 97.1%        │ 최고 정확도             │
  └──────────────┴─────────┴──────────────┴────────────────────────┘

■ 선택 가이드:
  - 빠른 실험: MobileNetV2 (가벼움)
  - 높은 정확도: EfficientNet (최신)
  - 교육/학습: VGG16 (구조가 단순)
  - 서버 배포: ResNet50 (안정적)
""")

# 사전학습 모델 시뮬레이션
class ToyPretrainedModel:
    """사전학습 모델 시뮬레이션"""
    def __init__(self, name, n_layers=10, feature_dim=512):
        self.name = name
        self.n_layers = n_layers
        self.feature_dim = feature_dim
        self.layers = []
        self.trainable = True

        # 레이어 생성 (가중치는 "사전학습된" 값으로 초기화)
        sizes = self._make_sizes(n_layers, feature_dim)
        for i in range(n_layers):
            layer = {
                'name': f'{name}_block{i+1}',
                'input_size': sizes[i],
                'output_size': sizes[i + 1],
                'weights': [[random.gauss(0, 0.1)
                             for _ in range(min(sizes[i+1], 8))]
                            for _ in range(min(sizes[i], 8))],
                'trainable': True,
                'type': 'conv' if i < n_layers - 2 else 'dense'
            }
            self.layers.append(layer)

    def _make_sizes(self, n, final):
        """레이어 크기 생성"""
        sizes = [224]  # 입력
        for i in range(n):
            sizes.append(max(final, sizes[-1] // 2))
        return sizes

    def freeze(self):
        """모든 레이어 동결 (학습 방지)"""
        for layer in self.layers:
            layer['trainable'] = False
        self.trainable = False

    def unfreeze_top(self, n):
        """상위 n개 레이어 해동"""
        for i, layer in enumerate(self.layers):
            if i >= len(self.layers) - n:
                layer['trainable'] = True

    def extract_features(self, image_flat):
        """특징 추출 (순전파)"""
        current = image_flat[:min(len(image_flat), 8)]
        for layer in self.layers:
            n_in = min(len(current), len(layer['weights']))
            n_out = len(layer['weights'][0]) if layer['weights'] else 4
            new_output = []
            for j in range(n_out):
                val = sum(current[i] * layer['weights'][i % n_in][j]
                         for i in range(n_in))
                new_output.append(max(0, val))  # ReLU
            current = new_output
        return current

    def summary(self):
        """모델 요약"""
        print(f"\n  {self.name} 모델 구조:")
        print(f"  {'레이어':<20} {'타입':<8} {'출력':<8} {'학습가능':<8}")
        print(f"  {'─'*20} {'─'*8} {'─'*8} {'─'*8}")
        for layer in self.layers:
            trainable_str = "O" if layer['trainable'] else "X (동결)"
            print(f"  {layer['name']:<20} {layer['type']:<8} "
                  f"{layer['output_size']:<8} {trainable_str}")

# 실제 코드: 사전학습 모델 로드
# 실제 코드: base_model = tf.keras.applications.VGG16(
# 실제 코드:     weights='imagenet',      # ImageNet 가중치 로드
# 실제 코드:     include_top=False,       # 분류 헤드 제외 (특징 추출부만)
# 실제 코드:     input_shape=(224, 224, 3)
# 실제 코드: )
# 실제 코드:
# 실제 코드: # 다른 모델들:
# 실제 코드: # tf.keras.applications.ResNet50(...)
# 실제 코드: # tf.keras.applications.MobileNetV2(...)
# 실제 코드: # tf.keras.applications.EfficientNetB0(...)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Feature Extraction (특징 추출 방식)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("3. Feature Extraction - 기존 모델 동결 + 새 분류기 학습")
print("=" * 70)

print("""
■ Feature Extraction 전략:
  사전학습 모델의 모든 레이어를 동결(freeze)하고,
  위에 새로운 분류기(classifier)만 추가하여 학습

  ┌──────────────────────────────┐
  │  새 분류기 (학습 O)          │  ← 이것만 학습!
  │  Dense(256) → Dense(2)       │
  ├──────────────────────────────┤
  │  GlobalAveragePooling2D      │
  ├──────────────────────────────┤
  │  사전학습 모델 (학습 X 동결)  │  ← 가중치 고정!
  │  VGG16/ResNet50/...          │
  └──────────────────────────────┘

■ 장점:
  - 학습 속도 빠름 (적은 파라미터만 학습)
  - 작은 데이터셋에서도 효과적
  - GPU 메모리 절약

■ 단점:
  - 사전학습 데이터와 너무 다른 도메인이면 효과 제한
""")

# Feature Extraction 시뮬레이션
print("■ Feature Extraction 시뮬레이션:")

# 1. 사전학습 모델 로드 및 동결
base_model = ToyPretrainedModel("VGG16", n_layers=6, feature_dim=512)
base_model.freeze()
base_model.summary()

# 2. 새 분류기 추가
class ToyClassifierHead:
    """분류기 헤드"""
    def __init__(self, input_dim, hidden_dim, n_classes):
        self.w1 = [[random.gauss(0, 0.1) for _ in range(hidden_dim)]
                    for _ in range(input_dim)]
        self.b1 = [0.0] * hidden_dim
        self.w2 = [[random.gauss(0, 0.1) for _ in range(n_classes)]
                    for _ in range(hidden_dim)]
        self.b2 = [0.0] * n_classes

    def forward(self, features):
        # Dense + ReLU
        hidden = []
        for j in range(len(self.b1)):
            val = sum(features[i % len(features)] * self.w1[i % len(self.w1)][j]
                     for i in range(len(self.w1))) + self.b1[j]
            hidden.append(max(0, val))

        # Dense + Softmax
        logits = []
        for j in range(len(self.b2)):
            val = sum(hidden[i] * self.w2[i][j]
                     for i in range(len(hidden))) + self.b2[j]
            logits.append(val)

        max_l = max(logits)
        exp_l = [math.exp(l - max_l) for l in logits]
        total = sum(exp_l)
        probs = [e / total for e in exp_l]
        return probs

classifier = ToyClassifierHead(input_dim=4, hidden_dim=8, n_classes=2)

# 3. 전체 파이프라인 테스트
print(f"\n■ 전체 파이프라인:")
for i in range(5):
    # 가상 이미지
    fake_image = [random.random() for _ in range(8)]
    # 특징 추출 (동결된 모델)
    features = base_model.extract_features(fake_image)
    # 분류
    probs = classifier.forward(features)
    label = "강아지" if probs[0] > probs[1] else "고양이"
    print(f"  이미지 {i+1}: {label} (강아지={probs[0]:.2%}, 고양이={probs[1]:.2%})")

# 실제 코드: Feature Extraction
# 실제 코드: base_model = tf.keras.applications.VGG16(
# 실제 코드:     weights='imagenet', include_top=False, input_shape=(224,224,3))
# 실제 코드:
# 실제 코드: # 동결
# 실제 코드: base_model.trainable = False
# 실제 코드:
# 실제 코드: # 새 분류기 추가
# 실제 코드: model = tf.keras.Sequential([
# 실제 코드:     base_model,
# 실제 코드:     tf.keras.layers.GlobalAveragePooling2D(),
# 실제 코드:     tf.keras.layers.Dense(256, activation='relu'),
# 실제 코드:     tf.keras.layers.Dropout(0.5),
# 실제 코드:     tf.keras.layers.Dense(2, activation='softmax')
# 실제 코드: ])
# 실제 코드:
# 실제 코드: model.compile(optimizer='adam', loss='sparse_categorical_crossentropy',
# 실제 코드:               metrics=['accuracy'])


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Fine-Tuning (미세 조정)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("4. Fine-Tuning - 일부 레이어 해동 후 재학습")
print("=" * 70)

print("""
■ Fine-Tuning 전략:
  Feature Extraction 후, 사전학습 모델의 상위 레이어를 해동하여
  낮은 학습률로 전체를 함께 학습

  단계:
  1단계: Feature Extraction (기본 모델 동결)
  2단계: 상위 레이어 해동 + 매우 낮은 학습률로 재학습

  ┌──────────────────────────────┐
  │  분류기 (학습 O)             │
  ├──────────────────────────────┤
  │  Block 5 (학습 O, 해동!)     │  ← Fine-Tuning!
  │  Block 4 (학습 O, 해동!)     │  ← Fine-Tuning!
  ├──────────────────────────────┤
  │  Block 3 (학습 X, 동결)      │  ← 기본 특징 유지
  │  Block 2 (학습 X, 동결)      │
  │  Block 1 (학습 X, 동결)      │
  └──────────────────────────────┘

■ 핵심 포인트:
  - 학습률을 1/10 ~ 1/100로 낮춰야 함!
    (사전학습된 좋은 가중치를 망가뜨리지 않도록)
  - 너무 많은 레이어를 해동하면 과적합 위험
  - 데이터가 많을수록 더 많은 레이어를 해동 가능
""")

# Fine-Tuning 시뮬레이션
print("■ Fine-Tuning 시뮬레이션:")

# 상위 2개 레이어 해동
base_model.unfreeze_top(2)
base_model.summary()

print("""
■ 학습률 비교:
  Feature Extraction: lr = 0.001 (기본)
  Fine-Tuning:        lr = 0.00001 (1/100로 낮춤!)

  왜? 사전학습된 가중치는 이미 좋은 값이므로
  큰 학습률로 업데이트하면 망가짐!
""")

# 실제 코드: Fine-Tuning
# 실제 코드: # 1단계: Feature Extraction (위 코드와 동일)
# 실제 코드: model.fit(train_ds, epochs=10, validation_data=val_ds)
# 실제 코드:
# 실제 코드: # 2단계: Fine-Tuning
# 실제 코드: base_model.trainable = True
# 실제 코드:
# 실제 코드: # 상위 레이어만 해동
# 실제 코드: for layer in base_model.layers[:-4]:
# 실제 코드:     layer.trainable = False
# 실제 코드:
# 실제 코드: # 매우 낮은 학습률로 재컴파일
# 실제 코드: model.compile(optimizer=tf.keras.optimizers.Adam(1e-5),
# 실제 코드:               loss='sparse_categorical_crossentropy',
# 실제 코드:               metrics=['accuracy'])
# 실제 코드:
# 실제 코드: model.fit(train_ds, epochs=10, validation_data=val_ds)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. 데이터 증강 (Data Augmentation)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("5. 데이터 증강 (Data Augmentation)")
print("=" * 70)

print("""
■ 데이터 증강이란?
  기존 이미지를 변형하여 새로운 학습 데이터를 만드는 기법
  → 데이터가 적을 때 특히 중요!

  비유: 같은 강아지 사진을 여러 각도, 조명에서 찍은 것처럼!

■ 주요 증강 기법:
  - RandomFlip("horizontal")  : 좌우 반전
  - RandomRotation(0.1)       : ±36도 회전
  - RandomZoom(0.2)           : ±20% 확대/축소
  - RandomTranslation(0.1, 0.1): 상하좌우 이동
  - RandomBrightness(0.2)     : 밝기 변화
  - RandomContrast(0.2)        : 대비 변화
""")

def augment_image(image, augmentation):
    """이미지 증강 시뮬레이션"""
    h, w = len(image), len(image[0])
    result = [row[:] for row in image]  # 복사

    if augmentation == 'flip_h':
        result = [row[::-1] for row in result]
    elif augmentation == 'flip_v':
        result = result[::-1]
    elif augmentation == 'brightness':
        delta = random.uniform(-0.3, 0.3)
        result = [[max(0, min(1, v + delta)) for v in row] for row in result]
    elif augmentation == 'noise':
        result = [[max(0, min(1, v + random.gauss(0, 0.05))) for v in row]
                  for row in result]
    elif augmentation == 'rotate90':
        result = [[image[h - 1 - j][i] for j in range(h)] for i in range(w)]

    return result

# 증강 시연
original = [
    [0.0, 0.0, 0.8, 0.9, 0.0],
    [0.0, 0.7, 0.9, 0.9, 0.0],
    [0.6, 0.8, 0.9, 0.8, 0.0],
    [0.0, 0.7, 0.9, 0.0, 0.0],
    [0.0, 0.0, 0.8, 0.0, 0.0],
]

def show_image(img, label):
    print(f"\n  {label}:")
    for row in img:
        line = "    "
        for v in row:
            if v > 0.7:
                line += "██"
            elif v > 0.4:
                line += "▓▓"
            elif v > 0.1:
                line += "░░"
            else:
                line += "  "
        print(line)

show_image(original, "원본")

augmentations = ['flip_h', 'flip_v', 'brightness', 'rotate90']
for aug in augmentations:
    augmented = augment_image(original, aug)
    show_image(augmented, f"증강: {aug}")

print(f"\n■ 증강으로 데이터 효과적 증가:")
print(f"  원본 1,000장 × 5가지 증강 = 5,000장 효과!")
print(f"  원본 1,000장 × 조합 증강 = 수만 장 효과!")

# 실제 코드: 데이터 증강
# 실제 코드: data_augmentation = tf.keras.Sequential([
# 실제 코드:     tf.keras.layers.RandomFlip("horizontal"),
# 실제 코드:     tf.keras.layers.RandomRotation(0.2),
# 실제 코드:     tf.keras.layers.RandomZoom(0.2),
# 실제 코드:     tf.keras.layers.RandomTranslation(0.1, 0.1),
# 실제 코드: ])
# 실제 코드:
# 실제 코드: # 모델에 포함
# 실제 코드: model = tf.keras.Sequential([
# 실제 코드:     data_augmentation,
# 실제 코드:     base_model,
# 실제 코드:     tf.keras.layers.GlobalAveragePooling2D(),
# 실제 코드:     tf.keras.layers.Dense(2, activation='softmax')
# 실제 코드: ])


# ═══════════════════════════════════════════════════════════════════════════════
# 6. [실습] 강아지 vs 고양이 분류 시뮬레이션
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("6. [실습] 강아지 vs 고양이 분류 (전이학습 시뮬레이션)")
print("=" * 70)

def simulate_transfer_learning():
    """전이학습 과정 전체 시뮬레이션"""

    # 가상 데이터 생성
    n_train = 200
    n_val = 50

    print("■ 데이터 준비:")
    print(f"  학습: 강아지 {n_train//2}장 + 고양이 {n_train//2}장 = {n_train}장")
    print(f"  검증: 강아지 {n_val//2}장 + 고양이 {n_val//2}장 = {n_val}장")

    # 1단계: Feature Extraction
    print(f"\n■ 1단계: Feature Extraction")
    print(f"  사전학습 모델: MobileNetV2 (동결)")
    print(f"  분류기: GAP → Dense(256) → Dropout(0.5) → Dense(2)")
    print(f"  학습률: 0.001")

    # 학습 시뮬레이션
    fe_train_acc = []
    fe_val_acc = []
    fe_train_loss = []
    fe_val_loss = []

    for epoch in range(15):
        # Feature Extraction은 빠르게 수렴
        ta = min(0.95, 0.5 + 0.035 * epoch + random.gauss(0, 0.01))
        va = min(0.92, 0.5 + 0.03 * epoch + random.gauss(0, 0.015))
        tl = max(0.1, 0.7 - 0.04 * epoch + random.gauss(0, 0.01))
        vl = max(0.15, 0.75 - 0.035 * epoch + random.gauss(0, 0.015))

        fe_train_acc.append(ta)
        fe_val_acc.append(va)
        fe_train_loss.append(tl)
        fe_val_loss.append(vl)

        if epoch % 3 == 0 or epoch == 14:
            print(f"  Epoch {epoch+1:2d}: "
                  f"loss={tl:.4f}, acc={ta:.2%}, "
                  f"val_loss={vl:.4f}, val_acc={va:.2%}")

    # 2단계: Fine-Tuning
    print(f"\n■ 2단계: Fine-Tuning")
    print(f"  상위 20개 레이어 해동")
    print(f"  학습률: 0.00001 (1/100)")

    ft_train_acc = [fe_train_acc[-1]]
    ft_val_acc = [fe_val_acc[-1]]

    for epoch in range(10):
        ta = min(0.99, ft_train_acc[-1] + 0.005 + random.gauss(0, 0.003))
        va = min(0.97, ft_val_acc[-1] + 0.004 + random.gauss(0, 0.004))

        ft_train_acc.append(ta)
        ft_val_acc.append(va)

        if epoch % 2 == 0 or epoch == 9:
            print(f"  Epoch {epoch+1:2d}: acc={ta:.2%}, val_acc={va:.2%}")

    print(f"\n■ 결과 비교:")
    print(f"  처음부터 학습 (가상):  ~70% 정확도 (데이터 부족)")
    print(f"  Feature Extraction:    {fe_val_acc[-1]:.2%} 정확도")
    print(f"  Fine-Tuning 후:        {ft_val_acc[-1]:.2%} 정확도")
    print(f"  → 전이학습으로 {ft_val_acc[-1] - 0.70:.1%} 향상!")

simulate_transfer_learning()


# ═══════════════════════════════════════════════════════════════════════════════
# 7. 전이학습 전략 선택
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("7. 전이학습 전략 선택 가이드")
print("=" * 70)

print("""
■ 데이터 크기 × 도메인 유사도에 따른 전략:

  ┌────────────────┬──────────────────────┬──────────────────────┐
  │                │ 유사한 도메인          │ 다른 도메인            │
  │                │ (자연 이미지→동물)     │ (자연→의료/위성)      │
  ├────────────────┼──────────────────────┼──────────────────────┤
  │ 데이터 많음    │ Fine-Tuning          │ Fine-Tuning          │
  │ (수만 장+)     │ (많은 레이어 해동)    │ (많은 레이어 해동)    │
  ├────────────────┼──────────────────────┼──────────────────────┤
  │ 데이터 적음    │ Feature Extraction    │ Feature Extraction    │
  │ (수백~천 장)   │ (동결, 분류기만)      │ + 초기 레이어도 해동   │
  │                │ → 가장 일반적!        │ 또는 처음부터 학습     │
  └────────────────┴──────────────────────┴──────────────────────┘

■ 도메인별 추천 사전학습 모델:
  - 자연 이미지: ImageNet 기반 (VGG, ResNet, EfficientNet)
  - 의료 이미지: ImageNet → Fine-Tune (또는 특화 모델)
  - 텍스트: BERT, GPT (언어 모델 전이학습)
  - 음성: Wav2Vec, HuBERT
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 8. 전처리 함수
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("8. 모델별 전처리 함수")
print("=" * 70)

print("""
■ 각 사전학습 모델은 고유한 전처리가 필요합니다!

  VGG16:        0~255 → BGR → 채널별 평균 빼기
  ResNet:       0~255 → BGR → 채널별 평균 빼기
  MobileNet:    0~255 → -1~1 (/ 127.5 - 1)
  EfficientNet: 0~255 → 0~1 (/ 255.0)

  잘못된 전처리 = 정확도 급락!
""")

def preprocess_vgg(image):
    """VGG16 전처리 시뮬레이션"""
    # 채널별 평균 빼기 (ImageNet 평균)
    means = [103.939, 116.779, 123.68]  # BGR
    return [[[p - means[c % 3] for c, p in enumerate(pixel)]
             for pixel in row] for row in image] if isinstance(image[0][0], list) else image

def preprocess_mobilenet(image):
    """MobileNet 전처리: 0~255 → -1~1"""
    return [[(p / 127.5) - 1.0 for p in row] for row in image]

def preprocess_efficientnet(image):
    """EfficientNet 전처리: 0~255 → 0~1"""
    return [[p / 255.0 for p in row] for row in image]

sample = [[128, 200, 50], [100, 150, 250]]
print(f"  원본: {sample}")
print(f"  MobileNet: {[[f'{v:.2f}' for v in row] for row in preprocess_mobilenet(sample)]}")
print(f"  EfficientNet: {[[f'{v:.2f}' for v in row] for row in preprocess_efficientnet(sample)]}")

# 실제 코드: 전처리 함수 사용
# 실제 코드: from tensorflow.keras.applications.vgg16 import preprocess_input
# 실제 코드: x = preprocess_input(x)  # 자동으로 올바른 전처리 적용!
# 실제 코드:
# 실제 코드: # 또는 모델별:
# 실제 코드: tf.keras.applications.mobilenet_v2.preprocess_input(x)
# 실제 코드: tf.keras.applications.efficientnet.preprocess_input(x)


# ═══════════════════════════════════════════════════════════════════════════════
# 9. 전이학습 실전 팁
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("9. 전이학습 실전 팁")
print("=" * 70)

print("""
■ 팁 1: BatchNormalization 주의!
  Fine-Tuning 시 BN 레이어를 동결 상태로 유지해야 할 수 있음
  → 작은 배치 크기로 학습 시 BN 통계가 불안정해질 수 있음

■ 팁 2: 학습률 차별화 (Discriminative Learning Rates)
  초기 레이어: 매우 낮은 학습률 (1e-6)
  중간 레이어: 중간 학습률 (1e-5)
  분류기 헤드: 높은 학습률 (1e-3)
  → 각 레이어가 적절한 속도로 업데이트

■ 팁 3: 점진적 해동 (Gradual Unfreezing)
  1단계: 분류기만 학습 (10 epochs)
  2단계: 마지막 블록 해동 + 재학습 (10 epochs)
  3단계: 그 이전 블록 해동 + 재학습 (10 epochs)
  → 더 안정적인 Fine-Tuning

■ 팁 4: 입력 크기
  사전학습 모델의 원래 입력 크기와 비슷하게 유지
  VGG: 224x224, EfficientNet-B0: 224x224, B7: 600x600
  너무 작은 이미지 → 정보 손실
  너무 큰 이미지 → 메모리/속도 문제
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 10. 전이학습 전체 코드 (TF/Keras)
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("10. 전이학습 전체 코드 템플릿")
print("=" * 70)

print("""
■ 완전한 전이학습 파이프라인 (실제 코드):
""")

# 실제 코드: 전이학습 전체 파이프라인
# 실제 코드: import tensorflow as tf
# 실제 코드:
# 실제 코드: # ── 1. 데이터 준비 ──
# 실제 코드: IMG_SIZE = 224
# 실제 코드: BATCH_SIZE = 32
# 실제 코드:
# 실제 코드: train_ds = tf.keras.utils.image_dataset_from_directory(
# 실제 코드:     'data/train',
# 실제 코드:     image_size=(IMG_SIZE, IMG_SIZE),
# 실제 코드:     batch_size=BATCH_SIZE
# 실제 코드: )
# 실제 코드: val_ds = tf.keras.utils.image_dataset_from_directory(
# 실제 코드:     'data/val',
# 실제 코드:     image_size=(IMG_SIZE, IMG_SIZE),
# 실제 코드:     batch_size=BATCH_SIZE
# 실제 코드: )
# 실제 코드:
# 실제 코드: # ── 2. 데이터 증강 ──
# 실제 코드: data_augmentation = tf.keras.Sequential([
# 실제 코드:     tf.keras.layers.RandomFlip("horizontal"),
# 실제 코드:     tf.keras.layers.RandomRotation(0.2),
# 실제 코드:     tf.keras.layers.RandomZoom(0.2),
# 실제 코드: ])
# 실제 코드:
# 실제 코드: # ── 3. 사전학습 모델 ──
# 실제 코드: base_model = tf.keras.applications.EfficientNetB0(
# 실제 코드:     weights='imagenet', include_top=False, input_shape=(IMG_SIZE,IMG_SIZE,3)
# 실제 코드: )
# 실제 코드: base_model.trainable = False
# 실제 코드:
# 실제 코드: # ── 4. 모델 구성 ──
# 실제 코드: inputs = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
# 실제 코드: x = data_augmentation(inputs)
# 실제 코드: x = tf.keras.applications.efficientnet.preprocess_input(x)
# 실제 코드: x = base_model(x, training=False)
# 실제 코드: x = tf.keras.layers.GlobalAveragePooling2D()(x)
# 실제 코드: x = tf.keras.layers.Dropout(0.3)(x)
# 실제 코드: outputs = tf.keras.layers.Dense(2, activation='softmax')(x)
# 실제 코드: model = tf.keras.Model(inputs, outputs)
# 실제 코드:
# 실제 코드: # ── 5. Feature Extraction 학습 ──
# 실제 코드: model.compile(optimizer='adam',
# 실제 코드:               loss='sparse_categorical_crossentropy',
# 실제 코드:               metrics=['accuracy'])
# 실제 코드: model.fit(train_ds, epochs=10, validation_data=val_ds)
# 실제 코드:
# 실제 코드: # ── 6. Fine-Tuning ──
# 실제 코드: base_model.trainable = True
# 실제 코드: for layer in base_model.layers[:-20]:
# 실제 코드:     layer.trainable = False
# 실제 코드:
# 실제 코드: model.compile(optimizer=tf.keras.optimizers.Adam(1e-5),
# 실제 코드:               loss='sparse_categorical_crossentropy',
# 실제 코드:               metrics=['accuracy'])
# 실제 코드: model.fit(train_ds, epochs=10, validation_data=val_ds,
# 실제 코드:           callbacks=[
# 실제 코드:               tf.keras.callbacks.EarlyStopping(patience=5,
# 실제 코드:                   restore_best_weights=True),
# 실제 코드:               tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=3),
# 실제 코드:           ])

print("  (위 코드는 주석으로 제공됩니다. 파일 내 '실제 코드:' 검색!)")


print("\n" + "=" * 70)
print("요약: 전이학습 학습 완료!")
print("=" * 70)
print("""
  1. 전이학습: 사전학습 지식 재사용 → 적은 데이터로 높은 성능
  2. Feature Extraction: 모델 동결 + 새 분류기만 학습
  3. Fine-Tuning: 일부 해동 + 낮은 학습률로 재학습
  4. 데이터 증강: Flip, Rotation, Zoom으로 데이터 늘리기
  5. 모델 선택: MobileNet(가벼움), EfficientNet(최신), ResNet(안정)
  6. 전처리: 모델별 전처리 함수 반드시 사용!

  다음 단계 → 08_rnn_text.py (RNN으로 텍스트 처리!)
""")
