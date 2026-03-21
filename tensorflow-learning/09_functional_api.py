# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   TensorFlow/Keras 학습 09단계: Functional API
#   ─ 다중 입력/출력, 공유 레이어, Skip Connection, Model 서브클래싱 ─
#   ■ 실행 방법: python 09_functional_api.py (개념 학습용 코드, TF 없이 실행 가능)
#   ■ TensorFlow 설치: pip install tensorflow
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import random

random.seed(42)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. Sequential vs Functional API
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("1. Sequential vs Functional API")
print("=" * 70)

print("""
■ Sequential 모델의 한계:
  - 입력이 1개, 출력이 1개만 가능
  - 레이어가 순서대로만 연결 (분기/합류 불가)
  - 가지치기(branching) 불가

  Sequential = 직선 도로 (A → B → C → D)
  Functional = 교차로가 있는 도로 (분기, 합류, 우회)

■ Functional API가 필요한 경우:
  1. 다중 입력 (이미지 + 텍스트 동시 입력)
  2. 다중 출력 (여러 가지를 동시에 예측)
  3. 공유 레이어 (같은 가중치를 여러 곳에서 사용)
  4. 잔차 연결 (Skip Connection, ResNet)
  5. 비선형 토폴로지 (DAG 형태)

■ 코드 스타일 비교:

  # Sequential:
  model = Sequential([Dense(64), Dense(32), Dense(1)])

  # Functional:
  inputs = Input(shape=(10,))
  x = Dense(64)(inputs)
  x = Dense(32)(x)
  outputs = Dense(1)(x)
  model = Model(inputs, outputs)
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Functional API 기본 구조
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("2. Functional API 토이 구현")
print("=" * 70)

class ToyTensor:
    """텐서 (레이어 간 데이터 흐름 표현)"""
    def __init__(self, shape, name="tensor", data=None):
        self.shape = shape
        self.name = name
        self.data = data or [0.0] * (shape[-1] if isinstance(shape, tuple) else shape)
        self.source_layer = None

    def __repr__(self):
        return f"ToyTensor(name='{self.name}', shape={self.shape})"

class ToyInput:
    """Input 레이어"""
    def __init__(self, shape, name="input"):
        self.shape = shape
        self.name = name

    def __call__(self, data=None):
        t = ToyTensor(shape=(None,) + self.shape, name=self.name, data=data)
        return t

class ToyDenseLayer:
    """Dense 레이어 (Functional API 스타일)"""
    def __init__(self, units, activation=None, name="dense"):
        self.units = units
        self.activation = activation
        self.name = name
        self.weights = None
        self.bias = None

    def build(self, input_size):
        limit = math.sqrt(6.0 / (input_size + self.units))
        self.weights = [[random.uniform(-limit, limit) for _ in range(self.units)]
                        for _ in range(input_size)]
        self.bias = [0.0] * self.units

    def __call__(self, input_tensor):
        if isinstance(input_tensor, ToyTensor):
            input_size = len(input_tensor.data)
        else:
            input_size = len(input_tensor)

        if self.weights is None:
            self.build(input_size)

        data = input_tensor.data if isinstance(input_tensor, ToyTensor) else input_tensor

        outputs = []
        for j in range(self.units):
            val = sum(data[i] * self.weights[i % len(self.weights)][j]
                     for i in range(len(data))) + self.bias[j]
            if self.activation == 'relu':
                val = max(0.0, val)
            elif self.activation == 'sigmoid':
                val = 1.0 / (1.0 + math.exp(-max(-20, min(20, val))))
            outputs.append(val)

        if self.activation == 'softmax':
            max_v = max(outputs)
            exp_v = [math.exp(o - max_v) for o in outputs]
            s = sum(exp_v)
            outputs = [e / s for e in exp_v]

        result = ToyTensor(shape=(None, self.units), name=f"{self.name}_output", data=outputs)
        result.source_layer = self
        return result

class ToyConcatenate:
    """여러 텐서 연결 (Concatenate)"""
    def __init__(self, name="concat"):
        self.name = name

    def __call__(self, tensors):
        combined_data = []
        for t in tensors:
            data = t.data if isinstance(t, ToyTensor) else t
            combined_data.extend(data)
        total_dim = sum(len(t.data) if isinstance(t, ToyTensor) else len(t) for t in tensors)
        return ToyTensor(shape=(None, total_dim), name=f"{self.name}_output", data=combined_data)

class ToyAdd:
    """텐서 더하기 (잔차 연결용)"""
    def __init__(self, name="add"):
        self.name = name

    def __call__(self, tensors):
        data_list = [t.data if isinstance(t, ToyTensor) else t for t in tensors]
        min_len = min(len(d) for d in data_list)
        summed = [sum(d[i] for d in data_list) for i in range(min_len)]
        return ToyTensor(shape=(None, min_len), name=f"{self.name}_output", data=summed)

class ToyModel:
    """Functional API 모델"""
    def __init__(self, inputs, outputs, name="model"):
        self.inputs = inputs if isinstance(inputs, list) else [inputs]
        self.outputs = outputs if isinstance(outputs, list) else [outputs]
        self.name = name

    def predict(self, input_data):
        """실제 예측은 위에서 이미 수행됨 (eager execution)"""
        return [o.data for o in self.outputs]

    def summary(self):
        print(f"\n  Model: '{self.name}'")
        print(f"  입력: {[i.name for i in self.inputs]}")
        print(f"  출력: {[o.name for o in self.outputs]}")

# 기본 Functional API 시연
print("\n■ Functional API 기본 사용:")

input_layer = ToyInput(shape=(10,), name="input_1")
input_tensor = input_layer(data=[random.random() for _ in range(10)])

x = ToyDenseLayer(64, activation='relu', name='dense_1')(input_tensor)
x = ToyDenseLayer(32, activation='relu', name='dense_2')(x)
output = ToyDenseLayer(1, activation='sigmoid', name='output')(x)

model = ToyModel(inputs=input_tensor, outputs=output, name="basic_functional")
model.summary()
print(f"  예측: {output.data[0]:.4f}")

# 실제 코드: Functional API
# 실제 코드: inputs = tf.keras.Input(shape=(10,))
# 실제 코드: x = tf.keras.layers.Dense(64, activation='relu')(inputs)
# 실제 코드: x = tf.keras.layers.Dense(32, activation='relu')(x)
# 실제 코드: outputs = tf.keras.layers.Dense(1, activation='sigmoid')(x)
# 실제 코드: model = tf.keras.Model(inputs=inputs, outputs=outputs)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. 다중 입력 모델
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("3. 다중 입력 모델 (Multiple Inputs)")
print("=" * 70)

print("""
■ 다중 입력 모델이 필요한 경우:
  - 이미지 + 메타데이터 (예: 제품 사진 + 가격/설명)
  - 텍스트 + 숫자 특성 (예: 리뷰 텍스트 + 별점)
  - 여러 센서 데이터 (예: 온도 + 습도 + 조도)

  ┌──────────┐   ┌──────────┐
  │ 이미지    │   │ 메타데이터│
  │ (CNN)     │   │ (Dense)  │
  └─────┬────┘   └────┬─────┘
        │              │
        └──────┬───────┘
               │ Concatenate
        ┌──────┴──────┐
        │  Dense      │
        │  (분류기)    │
        └─────────────┘
""")

# 다중 입력 모델 구현
print("■ 다중 입력 모델 시연:")
print("  시나리오: 영화 포스터(이미지) + 장르/감독(메타데이터) → 흥행 예측")

# 입력 1: 이미지 특징 (이미 CNN으로 추출된 것으로 가정)
image_input = ToyInput(shape=(8,), name="image_features")
image_data = [random.random() for _ in range(8)]
image_tensor = image_input(data=image_data)
img_x = ToyDenseLayer(16, activation='relu', name='img_dense')(image_tensor)

# 입력 2: 메타데이터
meta_input = ToyInput(shape=(4,), name="metadata")
meta_data = [0.8, 0.3, 0.5, 0.9]  # 장르, 감독 인기도 등
meta_tensor = meta_input(data=meta_data)
meta_x = ToyDenseLayer(8, activation='relu', name='meta_dense')(meta_tensor)

# 합치기 (Concatenate)
concat = ToyConcatenate(name="concat")
combined = concat([img_x, meta_x])
print(f"  이미지 특징: {len(img_x.data)} 차원")
print(f"  메타데이터:  {len(meta_x.data)} 차원")
print(f"  합친 후:    {len(combined.data)} 차원")

# 최종 예측
final = ToyDenseLayer(8, activation='relu', name='combined_dense')(combined)
output = ToyDenseLayer(1, activation='sigmoid', name='prediction')(final)
print(f"  예측 (흥행 확률): {output.data[0]:.4f}")

multi_model = ToyModel(
    inputs=[image_tensor, meta_tensor],
    outputs=output,
    name="multi_input_model"
)
multi_model.summary()

# 실제 코드: 다중 입력 모델
# 실제 코드: image_input = tf.keras.Input(shape=(224, 224, 3), name='image')
# 실제 코드: meta_input = tf.keras.Input(shape=(10,), name='metadata')
# 실제 코드:
# 실제 코드: # 이미지 처리
# 실제 코드: x1 = tf.keras.applications.MobileNetV2(include_top=False)(image_input)
# 실제 코드: x1 = tf.keras.layers.GlobalAveragePooling2D()(x1)
# 실제 코드:
# 실제 코드: # 메타데이터 처리
# 실제 코드: x2 = tf.keras.layers.Dense(32, activation='relu')(meta_input)
# 실제 코드:
# 실제 코드: # 합치기
# 실제 코드: combined = tf.keras.layers.Concatenate()([x1, x2])
# 실제 코드: x = tf.keras.layers.Dense(64, activation='relu')(combined)
# 실제 코드: output = tf.keras.layers.Dense(1, activation='sigmoid')(x)
# 실제 코드:
# 실제 코드: model = tf.keras.Model(inputs=[image_input, meta_input], outputs=output)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. 다중 출력 모델
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("4. 다중 출력 모델 (Multiple Outputs)")
print("=" * 70)

print("""
■ 다중 출력 모델이 필요한 경우:
  하나의 입력으로 여러 가지를 동시에 예측!

  예시: 얼굴 이미지 입력 →
  - 출력 1: 나이 (회귀)
  - 출력 2: 성별 (이진 분류)
  - 출력 3: 감정 (다중 분류: 행복/슬픔/화남/무표정)

               ┌──────────────┐
               │ 입력 이미지   │
               │ (공통 CNN)    │
               └──────┬───────┘
                 ┌────┼────┐
                 ↓    ↓    ↓
              ┌──┐ ┌──┐ ┌──┐
              │나이│ │성별│ │감정│
              │회귀│ │분류│ │분류│
              └──┘ └──┘ └──┘

■ 각 출력에 다른 손실 함수를 적용할 수 있음!
  model.compile(
      loss={'age': 'mse', 'gender': 'binary_crossentropy',
            'emotion': 'categorical_crossentropy'},
      loss_weights={'age': 0.5, 'gender': 1.0, 'emotion': 1.0}
  )
""")

# 다중 출력 모델 구현
print("■ 다중 출력 모델 시연:")
print("  시나리오: 얼굴 이미지 → 나이 + 성별 + 감정")

face_input = ToyInput(shape=(16,), name="face_features")
face_data = [random.random() for _ in range(16)]
face_tensor = face_input(data=face_data)

# 공통 특징 추출
shared = ToyDenseLayer(32, activation='relu', name='shared_dense')(face_tensor)

# 출력 1: 나이 (회귀)
age_output = ToyDenseLayer(1, activation=None, name='age_output')(shared)
print(f"  나이 예측: {abs(age_output.data[0] * 50 + 25):.1f}세")

# 출력 2: 성별 (이진 분류)
gender_output = ToyDenseLayer(1, activation='sigmoid', name='gender_output')(shared)
gender = "남성" if gender_output.data[0] > 0.5 else "여성"
print(f"  성별 예측: {gender} ({gender_output.data[0]:.2%})")

# 출력 3: 감정 (다중 분류)
emotion_output = ToyDenseLayer(4, activation='softmax', name='emotion_output')(shared)
emotions = ['행복', '슬픔', '화남', '무표정']
print(f"  감정 예측:")
for em, prob in zip(emotions, emotion_output.data):
    bar = "█" * int(prob * 30)
    print(f"    {em}: {prob:.2%} {bar}")

# 실제 코드: 다중 출력 모델
# 실제 코드: inputs = tf.keras.Input(shape=(64, 64, 3))
# 실제 코드: x = tf.keras.layers.Conv2D(32, 3, activation='relu')(inputs)
# 실제 코드: x = tf.keras.layers.GlobalAveragePooling2D()(x)
# 실제 코드: x = tf.keras.layers.Dense(64, activation='relu')(x)
# 실제 코드:
# 실제 코드: age = tf.keras.layers.Dense(1, name='age')(x)
# 실제 코드: gender = tf.keras.layers.Dense(1, activation='sigmoid', name='gender')(x)
# 실제 코드: emotion = tf.keras.layers.Dense(4, activation='softmax', name='emotion')(x)
# 실제 코드:
# 실제 코드: model = tf.keras.Model(inputs=inputs, outputs=[age, gender, emotion])
# 실제 코드: model.compile(
# 실제 코드:     optimizer='adam',
# 실제 코드:     loss={'age': 'mse', 'gender': 'binary_crossentropy',
# 실제 코드:           'emotion': 'categorical_crossentropy'},
# 실제 코드:     loss_weights={'age': 0.5, 'gender': 1.0, 'emotion': 1.0}
# 실제 코드: )


# ═══════════════════════════════════════════════════════════════════════════════
# 5. 공유 레이어 (Shared Layers) - Siamese Network
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("5. 공유 레이어 - Siamese Network")
print("=" * 70)

print("""
■ 공유 레이어란?
  같은 가중치를 가진 레이어를 여러 입력에 동시 적용!

  비유: 같은 교수님이 두 반을 동시에 가르치는 것
  → 두 반 학생들이 같은 기준으로 평가됨!

■ Siamese Network (샴 네트워크):
  두 입력이 같은 네트워크를 통과 → 유사도 비교

  ┌───────┐     ┌───────────┐     ┌───────┐
  │입력 A │ ──→ │           │ ──→ │특징 A │
  └───────┘     │ 공유 네트워크│     └───┬───┘
                │ (가중치 동일) │         │ 유사도
  ┌───────┐     │           │     ┌───┴───┐
  │입력 B │ ──→ │           │ ──→ │특징 B │
  └───────┘     └───────────┘     └───────┘

  응용: 얼굴 인식, 서명 확인, 문장 유사도
""")

# Siamese Network 시뮬레이션
print("■ Siamese Network 시연:")
print("  시나리오: 두 문장이 비슷한지 판별")

# 공유 레이어 (하나의 인스턴스를 두 번 사용!)
shared_dense1 = ToyDenseLayer(8, activation='relu', name='shared_1')
shared_dense2 = ToyDenseLayer(4, activation='relu', name='shared_2')

# 입력 A
input_a = [random.random() for _ in range(6)]
feat_a = shared_dense1(ToyTensor(shape=(None, 6), data=input_a))
feat_a = shared_dense2(feat_a)

# 입력 B (같은 레이어 사용!)
input_b = [random.random() for _ in range(6)]
feat_b = shared_dense1(ToyTensor(shape=(None, 6), data=input_b))
feat_b = shared_dense2(feat_b)

# 코사인 유사도 계산
def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x ** 2 for x in a))
    norm_b = math.sqrt(sum(x ** 2 for x in b))
    return dot / (norm_a * norm_b + 1e-8)

similarity = cosine_similarity(feat_a.data, feat_b.data)
print(f"  특징 A: {[f'{v:.3f}' for v in feat_a.data]}")
print(f"  특징 B: {[f'{v:.3f}' for v in feat_b.data]}")
print(f"  코사인 유사도: {similarity:.4f}")
print(f"  → 같은 레이어(가중치)로 추출한 특징을 비교!")

# 실제 코드: Siamese Network
# 실제 코드: shared_encoder = tf.keras.Sequential([
# 실제 코드:     tf.keras.layers.Dense(128, activation='relu'),
# 실제 코드:     tf.keras.layers.Dense(64, activation='relu'),
# 실제 코드: ])
# 실제 코드:
# 실제 코드: input_a = tf.keras.Input(shape=(100,))
# 실제 코드: input_b = tf.keras.Input(shape=(100,))
# 실제 코드:
# 실제 코드: encoded_a = shared_encoder(input_a)  # 같은 인코더!
# 실제 코드: encoded_b = shared_encoder(input_b)  # 같은 인코더!
# 실제 코드:
# 실제 코드: # L1 거리
# 실제 코드: distance = tf.keras.layers.Lambda(
# 실제 코드:     lambda x: tf.abs(x[0] - x[1]))([encoded_a, encoded_b])
# 실제 코드: output = tf.keras.layers.Dense(1, activation='sigmoid')(distance)
# 실제 코드:
# 실제 코드: model = tf.keras.Model(inputs=[input_a, input_b], outputs=output)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. 잔차 연결 (Skip Connection) - ResNet
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("6. 잔차 연결 (Skip Connection) - ResNet")
print("=" * 70)

print("""
■ 잔차 연결이란?
  입력을 레이어의 출력에 직접 더하는 구조!

  일반 네트워크:     x → [레이어] → F(x)
  잔차 네트워크:     x → [레이어] → F(x) + x  ← 입력을 더함!

  ┌────────────────────────────┐
  │  x ─────────────────┐      │
  │  ↓                  │      │
  │  Dense(64, relu)    │      │
  │  ↓                  │      │
  │  Dense(64)          │      │
  │  ↓                  ↓      │
  │  Add ← ─ ─ ─ ─ ─ ─ ┘      │
  │  ↓                         │
  │  ReLU                      │
  └────────────────────────────┘

■ 왜 효과적인가?
  1. 기울기 소실 해결: 기울기가 스킵 연결을 통해 직접 전달
  2. 항등 함수 학습 용이: 최소한 입력을 그대로 전달
  3. 매우 깊은 네트워크 가능: ResNet-152, ResNet-1001!

  비유: 고속도로의 추월 차선!
  일반 도로(레이어)가 막히면 추월 차선(스킵)으로 우회
""")

def residual_block(x_data, hidden_size):
    """잔차 블록 시뮬레이션"""
    # 입력 저장 (잔차 연결용)
    identity = x_data[:]

    # Dense → ReLU
    layer1 = ToyDenseLayer(hidden_size, activation='relu', name='res_dense1')
    x = layer1(ToyTensor(shape=(None, len(x_data)), data=x_data))

    # Dense (활성화 없이)
    layer2 = ToyDenseLayer(len(identity), activation=None, name='res_dense2')
    x = layer2(x)

    # 잔차 연결: output = F(x) + x
    output = [x.data[i % len(x.data)] + identity[i] for i in range(len(identity))]

    # ReLU
    output = [max(0.0, v) for v in output]

    return output

# 잔차 블록 시연
print("\n■ 잔차 블록 시연:")
input_data = [0.5, -0.3, 0.8, 0.1]
print(f"  입력: {input_data}")

output_no_skip = ToyDenseLayer(4, activation='relu', name='no_skip')(
    ToyTensor(shape=(None, 4), data=input_data)).data
print(f"  스킵 없이: {[f'{v:.4f}' for v in output_no_skip]}")

output_with_skip = residual_block(input_data, hidden_size=8)
print(f"  스킵 있음: {[f'{v:.4f}' for v in output_with_skip]}")
print(f"  → 입력 정보가 출력에 직접 전달되어 보존됨!")

# 깊은 잔차 네트워크 시뮬레이션
print(f"\n■ 깊은 잔차 네트워크 (5블록):")
x = [random.random() for _ in range(4)]
print(f"  입력: {[f'{v:.3f}' for v in x]}")
for block_idx in range(5):
    x = residual_block(x, hidden_size=8)
    if block_idx % 2 == 0 or block_idx == 4:
        print(f"  Block {block_idx+1} 출력: {[f'{v:.3f}' for v in x]}")
print(f"  → 5개 블록을 통과해도 값이 안정적!")

# 실제 코드: 잔차 블록
# 실제 코드: def residual_block(x, filters):
# 실제 코드:     shortcut = x
# 실제 코드:     x = tf.keras.layers.Conv2D(filters, 3, padding='same')(x)
# 실제 코드:     x = tf.keras.layers.BatchNormalization()(x)
# 실제 코드:     x = tf.keras.layers.ReLU()(x)
# 실제 코드:     x = tf.keras.layers.Conv2D(filters, 3, padding='same')(x)
# 실제 코드:     x = tf.keras.layers.BatchNormalization()(x)
# 실제 코드:     x = tf.keras.layers.Add()([x, shortcut])
# 실제 코드:     x = tf.keras.layers.ReLU()(x)
# 실제 코드:     return x


# ═══════════════════════════════════════════════════════════════════════════════
# 7. Model 서브클래싱
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("7. Model 서브클래싱 (가장 자유로운 방식)")
print("=" * 70)

print("""
■ 3가지 모델 생성 방식 비교:

  1. Sequential: 가장 간단, 직선 구조만
     model = Sequential([Dense(64), Dense(1)])

  2. Functional API: 복잡한 구조 가능, 선언적
     inputs = Input(shape=(10,))
     outputs = Dense(1)(Dense(64)(inputs))
     model = Model(inputs, outputs)

  3. Model 서브클래싱: 완전한 자유, 파이썬 코드로 로직
     class MyModel(tf.keras.Model):
         def __init__(self):
             self.dense = Dense(64)
         def call(self, x):
             return self.dense(x)

■ 언제 서브클래싱?
  - 조건부 로직이 필요할 때 (if문)
  - 동적 그래프가 필요할 때
  - 연구/실험에서 완전한 자유가 필요할 때
""")

class ToySubclassModel:
    """tf.keras.Model 서브클래싱 시뮬레이션"""
    def __init__(self, hidden_size=32, num_classes=10):
        self.dense1 = ToyDenseLayer(hidden_size, activation='relu', name='dense_1')
        self.dense2 = ToyDenseLayer(hidden_size, activation='relu', name='dense_2')
        self.classifier = ToyDenseLayer(num_classes, activation='softmax', name='classifier')
        self.use_skip = True  # 조건부 로직!

    def call(self, x):
        """순전파 - 파이썬으로 자유롭게 정의"""
        h1 = self.dense1(ToyTensor(shape=(None, len(x)), data=x))

        if self.use_skip:
            # 조건부 스킵 연결 (Functional API로는 복잡)
            h2 = self.dense2(h1)
            # 간이 스킵: h1과 h2의 합 (크기가 같을 때)
            h2_data = [h1.data[i] + h2.data[i] for i in range(len(h2.data))]
            h2 = ToyTensor(shape=h2.shape, data=h2_data)
        else:
            h2 = self.dense2(h1)

        output = self.classifier(h2)
        return output.data

# 서브클래싱 모델 사용
subclass_model = ToySubclassModel(hidden_size=8, num_classes=3)
test_input = [random.random() for _ in range(5)]

# 스킵 연결 있음
subclass_model.use_skip = True
output_with = subclass_model.call(test_input)
print(f"\n■ 서브클래싱 모델 시연:")
print(f"  입력: {[f'{v:.3f}' for v in test_input]}")
print(f"  스킵 있음: {[f'{v:.4f}' for v in output_with]}")

subclass_model.use_skip = False
output_without = subclass_model.call(test_input)
print(f"  스킵 없음: {[f'{v:.4f}' for v in output_without]}")

# 실제 코드: Model 서브클래싱
# 실제 코드: class MyModel(tf.keras.Model):
# 실제 코드:     def __init__(self, num_classes):
# 실제 코드:         super().__init__()
# 실제 코드:         self.conv1 = tf.keras.layers.Conv2D(32, 3, activation='relu')
# 실제 코드:         self.flatten = tf.keras.layers.Flatten()
# 실제 코드:         self.dense1 = tf.keras.layers.Dense(64, activation='relu')
# 실제 코드:         self.classifier = tf.keras.layers.Dense(num_classes, activation='softmax')
# 실제 코드:
# 실제 코드:     def call(self, x, training=False):
# 실제 코드:         x = self.conv1(x)
# 실제 코드:         x = self.flatten(x)
# 실제 코드:         x = self.dense1(x)
# 실제 코드:         if training:
# 실제 코드:             x = tf.nn.dropout(x, rate=0.5)
# 실제 코드:         return self.classifier(x)
# 실제 코드:
# 실제 코드: model = MyModel(num_classes=10)
# 실제 코드: model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')


# ═══════════════════════════════════════════════════════════════════════════════
# 8. Inception 모듈 (다중 경로)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("8. Inception 모듈 - 다중 경로 처리")
print("=" * 70)

print("""
■ Inception 모듈:
  같은 입력에 대해 여러 크기의 필터를 동시에 적용!

  입력 ─────┬──────┬──────┬──────┐
            ↓      ↓      ↓      ↓
         1x1    3x3    5x5   MaxPool
         Conv   Conv   Conv   3x3
            ↓      ↓      ↓      ↓
            └──────┴──────┴──────┘
                 Concatenate
                     ↓

  → 다양한 스케일의 특징을 동시에 추출!
""")

# Inception 모듈 시뮬레이션
def inception_block(x_data):
    """Inception 모듈 시뮬레이션"""
    # 경로 1: 1x1 conv (채널 축소)
    path1 = ToyDenseLayer(4, activation='relu', name='1x1')
    out1 = path1(ToyTensor(shape=(None, len(x_data)), data=x_data))

    # 경로 2: 3x3 conv 시뮬레이션
    path2 = ToyDenseLayer(4, activation='relu', name='3x3')
    out2 = path2(ToyTensor(shape=(None, len(x_data)), data=x_data))

    # 경로 3: 5x5 conv 시뮬레이션
    path3 = ToyDenseLayer(2, activation='relu', name='5x5')
    out3 = path3(ToyTensor(shape=(None, len(x_data)), data=x_data))

    # Concatenate
    combined = out1.data + out2.data + out3.data
    return combined

x = [random.random() for _ in range(8)]
inception_out = inception_block(x)
print(f"\n■ Inception 블록 시연:")
print(f"  입력: {len(x)} 차원")
print(f"  1x1 경로: 4 차원")
print(f"  3x3 경로: 4 차원")
print(f"  5x5 경로: 2 차원")
print(f"  합친 출력: {len(inception_out)} 차원 (4+4+2)")


# ═══════════════════════════════════════════════════════════════════════════════
# 9. [실습] 다중 입력/출력 모델 설계
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("9. [실습] 다중 입력/출력 모델 설계")
print("=" * 70)

print("""
■ 시나리오: 중고차 가격 예측 시스템
  입력 1: 차량 이미지 (외관 상태)
  입력 2: 차량 스펙 (연식, 주행거리, 배기량 등)

  출력 1: 예상 가격 (회귀)
  출력 2: 상태 등급 (분류: 상/중/하)
""")

# 모델 구현
print("■ 중고차 가격 예측 모델:")

# 입력 1: 이미지 특징 (CNN으로 추출된 것으로 가정)
car_image = [random.random() for _ in range(12)]
img_tensor = ToyTensor(shape=(None, 12), data=car_image, name="car_image")

# 이미지 처리
img_branch = ToyDenseLayer(8, activation='relu', name='img_1')(img_tensor)
img_branch = ToyDenseLayer(4, activation='relu', name='img_2')(img_branch)

# 입력 2: 차량 스펙
car_specs = [0.3, 0.7, 0.5, 0.2, 0.8]  # 연식, 주행거리, 배기량 등 정규화
spec_tensor = ToyTensor(shape=(None, 5), data=car_specs, name="car_specs")

# 스펙 처리
spec_branch = ToyDenseLayer(8, activation='relu', name='spec_1')(spec_tensor)
spec_branch = ToyDenseLayer(4, activation='relu', name='spec_2')(spec_branch)

# 합치기
concat = ToyConcatenate(name='merge')
merged = concat([img_branch, spec_branch])

# 공통 처리
shared = ToyDenseLayer(16, activation='relu', name='shared')(merged)

# 출력 1: 가격 예측 (회귀)
price = ToyDenseLayer(1, activation=None, name='price')(shared)
estimated_price = abs(price.data[0]) * 5000 + 500  # 스케일링

# 출력 2: 상태 등급 (분류)
condition = ToyDenseLayer(3, activation='softmax', name='condition')(shared)
conditions = ['상(좋음)', '중(보통)', '하(나쁨)']

print(f"\n  이미지 특징: {len(car_image)}D → 처리 후 {len(img_branch.data)}D")
print(f"  차량 스펙:   {len(car_specs)}D → 처리 후 {len(spec_branch.data)}D")
print(f"  합친 후:     {len(merged.data)}D")
print(f"  공통 처리:   {len(shared.data)}D")

print(f"\n  출력 1 - 예상 가격: ${estimated_price:,.0f}")
print(f"  출력 2 - 상태 등급:")
for cond, prob in zip(conditions, condition.data):
    bar = "█" * int(prob * 25)
    print(f"    {cond}: {prob:.2%} {bar}")

best_condition = conditions[condition.data.index(max(condition.data))]
print(f"  → 예측: ${estimated_price:,.0f}, 상태: {best_condition}")

# 실제 코드: 다중 입출력 모델
# 실제 코드: img_input = tf.keras.Input(shape=(224, 224, 3), name='image')
# 실제 코드: spec_input = tf.keras.Input(shape=(10,), name='specs')
# 실제 코드:
# 실제 코드: x1 = tf.keras.applications.MobileNetV2(include_top=False)(img_input)
# 실제 코드: x1 = tf.keras.layers.GlobalAveragePooling2D()(x1)
# 실제 코드: x2 = tf.keras.layers.Dense(32, activation='relu')(spec_input)
# 실제 코드:
# 실제 코드: merged = tf.keras.layers.Concatenate()([x1, x2])
# 실제 코드: shared = tf.keras.layers.Dense(64, activation='relu')(merged)
# 실제 코드:
# 실제 코드: price = tf.keras.layers.Dense(1, name='price')(shared)
# 실제 코드: condition = tf.keras.layers.Dense(3, activation='softmax', name='condition')(shared)
# 실제 코드:
# 실제 코드: model = tf.keras.Model(
# 실제 코드:     inputs=[img_input, spec_input],
# 실제 코드:     outputs=[price, condition]
# 실제 코드: )


# ═══════════════════════════════════════════════════════════════════════════════
# 10. 모델 생성 방식 선택 가이드
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("10. 모델 생성 방식 선택 가이드")
print("=" * 70)

print("""
■ 상황별 추천:

  ┌────────────────────┬──────────────────────────────────────┐
  │ 상황                │ 추천 방식                            │
  ├────────────────────┼──────────────────────────────────────┤
  │ 간단한 분류/회귀   │ Sequential (가장 빠르고 쉬움)       │
  │ 다중 입력/출력     │ Functional API                       │
  │ 잔차 연결          │ Functional API                       │
  │ 공유 레이어        │ Functional API                       │
  │ 조건부 로직        │ Model 서브클래싱                     │
  │ 커스텀 학습 루프   │ Model 서브클래싱 + GradientTape      │
  │ 연구/논문 구현     │ Model 서브클래싱                     │
  │ 프로덕션 배포      │ Functional API (저장/변환 용이)      │
  └────────────────────┴──────────────────────────────────────┘

■ 실무에서 가장 많이 쓰는 것:
  1. Functional API (~60%)  ← 가장 추천!
  2. Sequential (~25%)      ← 간단한 경우
  3. 서브클래싱 (~15%)      ← 연구/실험
""")


print("\n" + "=" * 70)
print("요약: Functional API 학습 완료!")
print("=" * 70)
print("""
  1. Sequential: 직선 구조만 (입력→출력 일직선)
  2. Functional: 분기/합류 가능 (다중 입력/출력, 스킵)
  3. 다중 입력: Concatenate로 합치기
  4. 다중 출력: 각각 다른 loss 적용 가능
  5. 공유 레이어: 같은 가중치로 여러 입력 처리 (Siamese)
  6. Skip Connection: 입력을 출력에 더하기 (ResNet)
  7. 서브클래싱: 완전한 자유, 파이썬 로직 사용

  다음 단계 → 10_deployment.py (모델 배포!)
""")
