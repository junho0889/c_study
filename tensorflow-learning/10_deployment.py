# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   TensorFlow/Keras 학습 10단계: 모델 배포 (Deployment)
#   ─ 모델 저장, TFLite, TF Serving, ONNX, 모델 최적화, 추론 파이프라인 ─
#   ■ 실행 방법: python 10_deployment.py (개념 학습용 코드, TF 없이 실행 가능)
#   ■ TensorFlow 설치: pip install tensorflow
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import random
import json
import time

random.seed(42)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. 모델 저장과 로드
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("1. 모델 저장과 로드 (model.save)")
print("=" * 70)

print("""
■ 모델 저장 형식:

  1. Keras 형식 (.keras) - 추천!
     model.save('model.keras')
     → 단일 파일, 가장 최신 형식
     → 아키텍처 + 가중치 + 옵티마이저 상태 + 설정

  2. HDF5 형식 (.h5) - 레거시
     model.save('model.h5')
     → 단일 파일, 이전 버전 호환
     → 일부 커스텀 객체에서 문제 가능

  3. SavedModel 형식 (폴더) - TF Serving용
     model.save('saved_model/')
     → 폴더 구조, TF Serving/TFLite/TF.js 호환
     → 프로덕션 배포에 가장 적합

  4. 가중치만 저장
     model.save_weights('weights.h5')
     → 아키텍처는 코드로 재생성 필요
""")

class ToyModelSaver:
    """모델 저장/로드 시뮬레이션"""
    @staticmethod
    def save_keras(model_config, filepath):
        """Keras 형식으로 저장 시뮬레이션"""
        saved = {
            'format': 'keras',
            'architecture': model_config.get('layers', []),
            'weights': model_config.get('weights', {}),
            'optimizer': model_config.get('optimizer', 'adam'),
            'loss': model_config.get('loss', 'categorical_crossentropy'),
        }
        print(f"  [저장] {filepath}")
        print(f"    형식: Keras (.keras)")
        print(f"    내용: 아키텍처 + 가중치 + 옵티마이저")
        return saved

    @staticmethod
    def save_savedmodel(model_config, dirpath):
        """SavedModel 형식으로 저장 시뮬레이션"""
        print(f"  [저장] {dirpath}/")
        print(f"    ├── saved_model.pb          (그래프 정의)")
        print(f"    ├── keras_metadata.pb        (Keras 메타데이터)")
        print(f"    └── variables/")
        print(f"        ├── variables.index      (변수 인덱스)")
        print(f"        └── variables.data-00000 (변수 데이터)")

    @staticmethod
    def save_weights(weights, filepath):
        """가중치만 저장 시뮬레이션"""
        print(f"  [저장] {filepath}")
        print(f"    가중치만 저장 (아키텍처 코드 필요)")

# 시뮬레이션
model_config = {
    'layers': ['Conv2D(32, 3x3)', 'MaxPool', 'Dense(128)', 'Dense(10)'],
    'weights': {'total_params': 52650},
    'optimizer': 'adam',
    'loss': 'sparse_categorical_crossentropy'
}

print("■ 모델 저장 시뮬레이션:")
ToyModelSaver.save_keras(model_config, 'my_model.keras')
print()
ToyModelSaver.save_savedmodel(model_config, 'saved_model')

# 실제 코드: 모델 저장/로드
# 실제 코드: # 전체 모델 저장
# 실제 코드: model.save('my_model.keras')  # Keras 형식 (추천)
# 실제 코드: model.save('saved_model/')    # SavedModel 형식
# 실제 코드:
# 실제 코드: # 모델 로드
# 실제 코드: loaded_model = tf.keras.models.load_model('my_model.keras')
# 실제 코드: loaded_model = tf.saved_model.load('saved_model/')
# 실제 코드:
# 실제 코드: # 가중치만 저장/로드
# 실제 코드: model.save_weights('weights.h5')
# 실제 코드: model.load_weights('weights.h5')


# ═══════════════════════════════════════════════════════════════════════════════
# 2. TFLite - 모바일/엣지 배포
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("2. TFLite - 모바일/엣지 디바이스 배포")
print("=" * 70)

print("""
■ TFLite란?
  TensorFlow 모델을 모바일/임베디드 기기에서 실행하기 위한 경량 포맷

  ┌──────────────────────────────────────────────────┐
  │  TF 모델 (수백 MB)                               │
  │  ↓ 변환 (TFLiteConverter)                        │
  │  TFLite 모델 (.tflite) (수 MB)                   │
  │  ↓ 배포                                          │
  │  스마트폰, 라즈베리파이, 마이크로컨트롤러        │
  └──────────────────────────────────────────────────┘

■ 양자화 (Quantization):
  모델의 가중치를 float32 → int8로 변환!
  - 모델 크기: ~4배 감소
  - 추론 속도: ~2-4배 향상
  - 정확도: 약간 감소 (보통 1% 미만)

  ┌────────────────────────────────────────────────┐
  │ 양자화 유형        │ 크기 감소 │ 속도 향상     │
  ├────────────────────────────────────────────────┤
  │ 동적 범위 (기본)   │ ~4x      │ ~2-3x        │
  │ 정수 전용 (int8)   │ ~4x      │ ~3-4x        │
  │ float16            │ ~2x      │ ~1.5-2x      │
  └────────────────────────────────────────────────┘
""")

def simulate_quantization(weights, bits=8):
    """양자화 시뮬레이션: float32 → int8"""
    min_val = min(weights)
    max_val = max(weights)
    scale = (max_val - min_val) / (2 ** bits - 1)
    zero_point = round(-min_val / scale) if scale != 0 else 0

    # 양자화
    quantized = []
    for w in weights:
        q = round(w / scale) + zero_point if scale != 0 else 0
        q = max(0, min(2 ** bits - 1, q))
        quantized.append(int(q))

    # 역양자화 (추론 시)
    dequantized = [(q - zero_point) * scale for q in quantized]

    return quantized, dequantized, scale, zero_point

# 양자화 시연
print("■ 양자화 시뮬레이션:")
original_weights = [0.523, -0.187, 0.891, -0.342, 0.156, 0.678, -0.945, 0.234]
quantized, dequantized, scale, zp = simulate_quantization(original_weights)

print(f"  원본 (float32):   {[f'{w:.3f}' for w in original_weights]}")
print(f"  양자화 (int8):    {quantized}")
print(f"  역양자화 (float): {[f'{w:.3f}' for w in dequantized]}")
print(f"  스케일: {scale:.6f}, 영점: {zp}")

# 오차 계산
errors = [abs(o - d) for o, d in zip(original_weights, dequantized)]
print(f"  양자화 오차:      {[f'{e:.4f}' for e in errors]}")
print(f"  최대 오차:        {max(errors):.4f}")
print(f"  메모리 절약:      {4 * len(original_weights)}B → {len(original_weights)}B "
      f"({4 * len(original_weights) / len(original_weights):.0f}배 절약!)")

# 실제 코드: TFLite 변환
# 실제 코드: # 기본 변환
# 실제 코드: converter = tf.lite.TFLiteConverter.from_saved_model('saved_model/')
# 실제 코드: tflite_model = converter.convert()
# 실제 코드: with open('model.tflite', 'wb') as f:
# 실제 코드:     f.write(tflite_model)
# 실제 코드:
# 실제 코드: # 동적 범위 양자화
# 실제 코드: converter.optimizations = [tf.lite.Optimize.DEFAULT]
# 실제 코드: tflite_quant = converter.convert()
# 실제 코드:
# 실제 코드: # 정수 전용 양자화 (대표 데이터셋 필요)
# 실제 코드: converter.optimizations = [tf.lite.Optimize.DEFAULT]
# 실제 코드: converter.representative_dataset = representative_dataset_gen
# 실제 코드: converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
# 실제 코드: converter.inference_input_type = tf.uint8
# 실제 코드: converter.inference_output_type = tf.uint8
# 실제 코드:
# 실제 코드: # TFLite 추론
# 실제 코드: interpreter = tf.lite.Interpreter(model_path='model.tflite')
# 실제 코드: interpreter.allocate_tensors()
# 실제 코드: input_details = interpreter.get_input_details()
# 실제 코드: output_details = interpreter.get_output_details()
# 실제 코드: interpreter.set_tensor(input_details[0]['index'], input_data)
# 실제 코드: interpreter.invoke()
# 실제 코드: output = interpreter.get_tensor(output_details[0]['index'])


# ═══════════════════════════════════════════════════════════════════════════════
# 3. TF Serving - REST API로 모델 서빙
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("3. TF Serving - REST API로 모델 서빙")
print("=" * 70)

print("""
■ TF Serving이란?
  학습된 모델을 REST/gRPC API로 배포하는 서버

  ┌──────────────┐     HTTP/gRPC     ┌──────────────┐
  │   클라이언트  │ ───────────────→ │  TF Serving   │
  │   (앱/웹)    │ ←─────────────── │  (모델 서버)  │
  └──────────────┘     JSON 응답     └──────────────┘

■ 장점:
  - 모델 버전 관리 (A/B 테스트)
  - 자동 배치 처리 (batching)
  - GPU 가속 지원
  - 모델 핫 리로드 (재시작 없이 교체)
""")

class ToyModelServer:
    """TF Serving 시뮬레이션"""
    def __init__(self, model_name, version=1):
        self.model_name = model_name
        self.version = version
        self.models = {}

    def load_model(self, version, model_fn):
        """모델 로드"""
        self.models[version] = model_fn
        print(f"  [서버] 모델 로드: {self.model_name}/v{version}")

    def predict(self, instances, version=None):
        """REST API 예측 시뮬레이션"""
        v = version or self.version
        start = time.time()

        results = []
        for instance in instances:
            # 간단한 예측 시뮬레이션
            prediction = [random.random() for _ in range(3)]
            total = sum(prediction)
            prediction = [p / total for p in prediction]
            results.append(prediction)

        elapsed = time.time() - start

        response = {
            "model_name": self.model_name,
            "model_version": v,
            "predictions": results,
            "latency_ms": f"{elapsed * 1000:.2f}"
        }
        return response

    def get_status(self):
        return {
            "model_name": self.model_name,
            "versions": list(self.models.keys()),
            "status": "AVAILABLE"
        }

# TF Serving 시뮬레이션
print("\n■ TF Serving 시뮬레이션:")

server = ToyModelServer("image_classifier")
server.load_model(1, lambda x: [0.1, 0.8, 0.1])
server.load_model(2, lambda x: [0.05, 0.9, 0.05])

# 상태 확인
status = server.get_status()
print(f"\n  서버 상태: {json.dumps(status, indent=4)}")

# REST API 요청 시뮬레이션
print(f"\n■ REST API 요청/응답:")

request = {
    "instances": [
        [0.5, 0.3, 0.8, 0.1],
        [0.2, 0.7, 0.4, 0.9],
    ]
}
print(f"  요청 (POST /v1/models/image_classifier:predict):")
print(f"  {json.dumps(request, indent=4)[:200]}...")

response = server.predict(request["instances"])
print(f"\n  응답:")
print(f"  {json.dumps(response, indent=4)}")

# 실제 코드: TF Serving
# 실제 코드: # 1. 모델 저장 (SavedModel 형식)
# 실제 코드: model.save('models/image_classifier/1/')  # 버전 1
# 실제 코드:
# 실제 코드: # 2. Docker로 TF Serving 실행
# 실제 코드: # docker run -p 8501:8501 \
# 실제 코드: #   --mount type=bind,source=/path/to/models,target=/models \
# 실제 코드: #   -e MODEL_NAME=image_classifier \
# 실제 코드: #   tensorflow/serving
# 실제 코드:
# 실제 코드: # 3. REST API 호출
# 실제 코드: import requests
# 실제 코드: data = json.dumps({"instances": [[1.0, 2.0, 3.0]]})
# 실제 코드: response = requests.post(
# 실제 코드:     'http://localhost:8501/v1/models/image_classifier:predict',
# 실제 코드:     data=data,
# 실제 코드:     headers={'Content-Type': 'application/json'}
# 실제 코드: )
# 실제 코드: predictions = response.json()['predictions']


# ═══════════════════════════════════════════════════════════════════════════════
# 4. ONNX - 프레임워크 간 변환
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("4. ONNX - 프레임워크 간 변환")
print("=" * 70)

print("""
■ ONNX (Open Neural Network Exchange)란?
  다양한 딥러닝 프레임워크 간 모델을 교환하기 위한 표준 형식

  ┌────────────┐     ┌──────┐     ┌────────────┐
  │ TensorFlow │ ──→ │ ONNX │ ──→ │ PyTorch    │
  │ Keras      │     │ 형식  │     │ ONNX RT    │
  │ PyTorch    │ ──→ │      │ ──→ │ TensorRT   │
  └────────────┘     └──────┘     └────────────┘

■ 왜 ONNX를 쓰나?
  1. TF로 학습 → PyTorch로 서빙 (또는 그 반대)
  2. ONNX Runtime으로 최적화된 추론
  3. NVIDIA TensorRT로 GPU 가속 추론
  4. 다양한 하드웨어 지원 (CPU, GPU, NPU)

■ ONNX Runtime 장점:
  - TF보다 추론 속도 1.5~3배 빠를 수 있음
  - 크로스 플랫폼 (Windows, Linux, Mac, 모바일)
  - 최적화 자동 적용
""")

# ONNX 변환 시뮬레이션
print("■ ONNX 변환 시뮬레이션:")

class ToyONNXConverter:
    """ONNX 변환 시뮬레이션"""
    @staticmethod
    def convert(model_info, output_path):
        print(f"  [변환] TF/Keras → ONNX")
        print(f"    입력 모델: {model_info['name']}")
        print(f"    레이어 수: {len(model_info['layers'])}")
        print(f"    출력 파일: {output_path}")

        # ONNX 그래프 구조 시뮬레이션
        onnx_graph = {
            'ir_version': 8,
            'opset_import': [{'version': 15}],
            'graph': {
                'node': [{'op_type': layer} for layer in model_info['layers']],
                'input': model_info.get('input_shape', '(None, 224, 224, 3)'),
                'output': model_info.get('output_shape', '(None, 10)')
            }
        }

        print(f"    ONNX opset: {onnx_graph['opset_import'][0]['version']}")
        print(f"    노드 수: {len(onnx_graph['graph']['node'])}")
        return onnx_graph

model_info = {
    'name': 'EfficientNetB0',
    'layers': ['Conv', 'BatchNorm', 'Swish', 'DepthwiseConv', 'Conv', 'Add',
               'GlobalAvgPool', 'Dense', 'Softmax'],
    'input_shape': '(1, 224, 224, 3)',
    'output_shape': '(1, 1000)'
}

ToyONNXConverter.convert(model_info, 'model.onnx')

# 실제 코드: ONNX 변환
# 실제 코드: # pip install tf2onnx
# 실제 코드: import tf2onnx
# 실제 코드:
# 실제 코드: # 방법 1: 명령줄
# 실제 코드: # python -m tf2onnx.convert --saved-model saved_model/ --output model.onnx
# 실제 코드:
# 실제 코드: # 방법 2: Python API
# 실제 코드: spec = (tf.TensorSpec((None, 224, 224, 3), tf.float32),)
# 실제 코드: output_path = "model.onnx"
# 실제 코드: model_proto, _ = tf2onnx.convert.from_keras(model, output_path=output_path)
# 실제 코드:
# 실제 코드: # ONNX Runtime으로 추론
# 실제 코드: import onnxruntime as ort
# 실제 코드: session = ort.InferenceSession("model.onnx")
# 실제 코드: input_name = session.get_inputs()[0].name
# 실제 코드: result = session.run(None, {input_name: input_data})


# ═══════════════════════════════════════════════════════════════════════════════
# 5. 모델 최적화 기법
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("5. 모델 최적화 기법")
print("=" * 70)

print("""
■ 모델 최적화의 목표:
  정확도를 최소한으로 희생하면서 모델을 빠르고 가볍게!

  ┌──────────────────────────────────────────────────────┐
  │ 기법          │ 크기 감소 │ 속도 향상 │ 정확도 영향  │
  ├──────────────────────────────────────────────────────┤
  │ 양자화        │ 2~4x     │ 2~4x     │ 미미함       │
  │ 프루닝        │ 2~10x    │ 1~3x     │ 약간 감소    │
  │ 지식 증류     │ 자유     │ 크게 향상 │ 약간 감소    │
  │ 구조 탐색     │ 자유     │ 크게 향상 │ 유지/향상    │
  └──────────────────────────────────────────────────────┘
""")

# --- 프루닝 (Pruning) ---
print("■ 프루닝 (Pruning) - 불필요한 가중치 제거")
print("""
  비유: 나무 가지치기!
  작은 가중치(중요하지 않은 연결)를 0으로 만들어 제거

  원본 가중치:  [0.52, -0.01, 0.87, 0.003, -0.45, 0.002]
  프루닝 후:   [0.52,  0.00, 0.87, 0.000, -0.45, 0.000]
  → 0이 많아지면 희소 행렬로 압축 가능!
""")

def prune_weights(weights, sparsity=0.5):
    """가중치 프루닝: 작은 값을 0으로"""
    abs_weights = sorted([abs(w) for w in weights])
    threshold = abs_weights[int(len(abs_weights) * sparsity)]
    pruned = [w if abs(w) > threshold else 0.0 for w in weights]
    actual_sparsity = sum(1 for w in pruned if w == 0.0) / len(pruned)
    return pruned, actual_sparsity

weights_example = [0.52, -0.01, 0.87, 0.003, -0.45, 0.002, 0.31, -0.67,
                   0.008, -0.23, 0.15, -0.005, 0.92, 0.04, -0.78, 0.001]

pruned_50, sparsity_50 = prune_weights(weights_example, 0.5)
pruned_80, sparsity_80 = prune_weights(weights_example, 0.8)

print(f"  원본:       {[f'{w:.3f}' for w in weights_example[:8]]}...")
print(f"  50% 프루닝: {[f'{w:.3f}' for w in pruned_50[:8]]}... (실제 {sparsity_50:.0%} 희소)")
print(f"  80% 프루닝: {[f'{w:.3f}' for w in pruned_80[:8]]}... (실제 {sparsity_80:.0%} 희소)")

# --- 지식 증류 (Knowledge Distillation) ---
print(f"\n■ 지식 증류 (Knowledge Distillation)")
print("""
  큰 모델(Teacher)의 지식을 작은 모델(Student)에 전달!

  ┌─────────────┐
  │ Teacher     │  ← 크고 정확한 모델 (ResNet-152)
  │ (큰 모델)   │  예측: [0.02, 0.03, 0.90, 0.05]
  └──────┬──────┘
         │ "소프트 타겟" 전달
  ┌──────┴──────┐
  │ Student     │  ← 작고 빠른 모델 (MobileNet)
  │ (작은 모델)  │  Teacher의 출력 분포를 학습!
  └─────────────┘

  핵심: Hard Label [0,0,1,0] 보다
        Soft Label [0.02, 0.03, 0.90, 0.05] 가 더 많은 정보 포함!
        → "고양이인데 호랑이와 약간 비슷하다" 같은 관계 정보
""")

# 지식 증류 시뮬레이션
teacher_output = [0.02, 0.03, 0.90, 0.05]
hard_label = [0, 0, 1, 0]
classes = ['개', '새', '고양이', '호랑이']

print(f"  Hard Label: {hard_label}")
print(f"  Soft Label: {teacher_output}")
print(f"  → Soft Label에는 '호랑이와 약간 비슷' 정보가 담겨 있음!")

# Temperature Scaling
def soft_labels(logits, temperature=1.0):
    """온도 스케일링된 소프트맥스"""
    scaled = [l / temperature for l in logits]
    max_s = max(scaled)
    exp_s = [math.exp(s - max_s) for s in scaled]
    total = sum(exp_s)
    return [e / total for e in exp_s]

logits = [-2.0, -1.5, 5.0, 0.5]
print(f"\n  Temperature Scaling 효과:")
for T in [1.0, 2.0, 5.0, 10.0]:
    probs = soft_labels(logits, T)
    print(f"    T={T:4.1f}: {[f'{p:.3f}' for p in probs]}  "
          f"← {'뾰족(확신)' if T == 1.0 else '부드러움(관계 정보 풍부)' if T >= 5.0 else '중간'}")

# 실제 코드: 프루닝
# 실제 코드: import tensorflow_model_optimization as tfmot
# 실제 코드:
# 실제 코드: prune_low_magnitude = tfmot.sparsity.keras.prune_low_magnitude
# 실제 코드: pruned_model = prune_low_magnitude(model,
# 실제 코드:     pruning_schedule=tfmot.sparsity.keras.PolynomialDecay(
# 실제 코드:         initial_sparsity=0.30, final_sparsity=0.80,
# 실제 코드:         begin_step=0, end_step=1000
# 실제 코드:     ))
# 실제 코드:
# 실제 코드: # 지식 증류
# 실제 코드: class Distiller(tf.keras.Model):
# 실제 코드:     def __init__(self, student, teacher):
# 실제 코드:         super().__init__()
# 실제 코드:         self.student = student
# 실제 코드:         self.teacher = teacher
# 실제 코드:
# 실제 코드:     def train_step(self, data):
# 실제 코드:         x, y = data
# 실제 코드:         teacher_preds = self.teacher(x, training=False)
# 실제 코드:         with tf.GradientTape() as tape:
# 실제 코드:             student_preds = self.student(x, training=True)
# 실제 코드:             # 학생 손실 = CE(hard) + KL(soft) 혼합
# 실제 코드:             loss = self.compiled_loss(y, student_preds) + \
# 실제 코드:                    tf.keras.losses.KLDivergence()(teacher_preds, student_preds)
# 실제 코드:         ...


# ═══════════════════════════════════════════════════════════════════════════════
# 6. 추론 파이프라인
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("6. 추론 파이프라인 - 전처리 → 예측 → 후처리")
print("=" * 70)

print("""
■ 추론 파이프라인:
  실제 배포에서는 모델만 있으면 안 됨!
  전처리와 후처리가 필수!

  ┌──────────────┐    ┌───────────┐    ┌──────────────┐
  │ 전처리        │ →  │ 모델 추론  │ →  │ 후처리        │
  │ (Preprocessing)│    │ (Model)    │    │(Postprocessing)│
  └──────────────┘    └───────────┘    └──────────────┘

  전처리: 리사이즈, 정규화, 패딩 등
  모델:  추론 (순전파)
  후처리: 클래스 이름 매핑, 임계값 적용, NMS 등
""")

class ToyInferencePipeline:
    """추론 파이프라인"""
    def __init__(self, class_names, input_size=(224, 224)):
        self.class_names = class_names
        self.input_size = input_size

    def preprocess(self, raw_data):
        """전처리: 정규화, 리사이즈"""
        print(f"    [전처리]")
        # 1. 리사이즈
        if isinstance(raw_data, list):
            data = raw_data[:self.input_size[0]]
        else:
            data = raw_data
        print(f"      리사이즈: {self.input_size}")

        # 2. 정규화 (0~255 → 0~1)
        if isinstance(data, list):
            data = [v / 255.0 if v > 1.0 else v for v in data]
        print(f"      정규화: 0~255 → 0~1")

        # 3. 배치 차원 추가
        print(f"      배치 차원 추가: (1, ...)")
        return data

    def predict(self, preprocessed_data):
        """모델 추론"""
        print(f"    [추론] 모델 순전파 실행")
        # 시뮬레이션: 랜덤 예측
        raw_probs = [random.random() for _ in self.class_names]
        total = sum(raw_probs)
        probs = [p / total for p in raw_probs]
        return probs

    def postprocess(self, predictions, threshold=0.1, top_k=3):
        """후처리: 클래스 이름 매핑, 정렬, 필터링"""
        print(f"    [후처리]")
        results = list(zip(self.class_names, predictions))
        results.sort(key=lambda x: -x[1])

        # Top-K 필터
        results = results[:top_k]

        # 임계값 필터
        results = [(name, prob) for name, prob in results if prob >= threshold]

        print(f"      Top-{top_k} 결과, 임계값 >= {threshold}")
        return results

    def run(self, raw_data):
        """전체 파이프라인 실행"""
        print(f"\n  파이프라인 실행:")
        preprocessed = self.preprocess(raw_data)
        predictions = self.predict(preprocessed)
        results = self.postprocess(predictions)
        return results

# 파이프라인 실행
classes = ['고양이', '강아지', '새', '물고기', '햄스터']
pipeline = ToyInferencePipeline(class_names=classes)

raw_image = [random.randint(0, 255) for _ in range(100)]
results = pipeline.run(raw_image)

print(f"\n  예측 결과:")
for name, prob in results:
    bar = "█" * int(prob * 30)
    print(f"    {name}: {prob:.2%} {bar}")


# ═══════════════════════════════════════════════════════════════════════════════
# 7. 배포 플랫폼별 전략
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("7. 배포 플랫폼별 전략")
print("=" * 70)

print("""
■ 서버 배포 (Cloud):
  TF Serving + Docker + Kubernetes
  → 대규모 트래픽 처리, 자동 확장, 고가용성
  추천: SavedModel + TF Serving 또는 ONNX Runtime

■ 모바일 배포 (Android/iOS):
  TFLite + int8 양자화
  → 앱 내 직접 실행, 오프라인 가능
  추천: MobileNet/EfficientNet-Lite + TFLite

■ 웹 배포 (브라우저):
  TensorFlow.js
  → 서버 없이 브라우저에서 직접 실행
  추천: 가벼운 모델 + WebGL 가속

■ 엣지 디바이스 (IoT):
  TFLite Micro / ONNX Runtime
  → 라즈베리파이, 마이크로컨트롤러
  추천: 극도로 가벼운 모델 + int8 양자화

■ GPU 서버 (고성능):
  TensorRT (NVIDIA)
  → GPU 최적화, 최고의 추론 속도
  추천: SavedModel → ONNX → TensorRT
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 8. 성능 벤치마킹
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("8. 추론 성능 벤치마킹")
print("=" * 70)

def benchmark_inference(name, n_iterations=1000, base_time_ms=10):
    """추론 성능 벤치마킹 시뮬레이션"""
    times = []
    for _ in range(n_iterations):
        t = base_time_ms + random.gauss(0, base_time_ms * 0.1)
        times.append(max(0.1, t))

    avg = sum(times) / len(times)
    p50 = sorted(times)[len(times) // 2]
    p95 = sorted(times)[int(len(times) * 0.95)]
    p99 = sorted(times)[int(len(times) * 0.99)]
    throughput = 1000 / avg  # queries per second

    return {
        'name': name,
        'avg_ms': avg,
        'p50_ms': p50,
        'p95_ms': p95,
        'p99_ms': p99,
        'throughput': throughput
    }

configs = [
    ("TF (CPU, float32)", 45),
    ("TF (GPU, float32)", 8),
    ("TFLite (CPU, float32)", 25),
    ("TFLite (CPU, int8)", 12),
    ("ONNX RT (CPU)", 20),
    ("TensorRT (GPU)", 3),
]

print("\n■ 추론 성능 비교 (시뮬레이션):")
print(f"  {'설정':<25} {'평균':>8} {'P50':>8} {'P95':>8} {'P99':>8} {'QPS':>8}")
print(f"  {'─'*25} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*8}")

for name, base_time in configs:
    result = benchmark_inference(name, 1000, base_time)
    print(f"  {result['name']:<25} "
          f"{result['avg_ms']:7.1f}ms "
          f"{result['p50_ms']:7.1f}ms "
          f"{result['p95_ms']:7.1f}ms "
          f"{result['p99_ms']:7.1f}ms "
          f"{result['throughput']:7.0f}")


# ═══════════════════════════════════════════════════════════════════════════════
# 9. 모델 버전 관리와 CI/CD
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("9. 모델 버전 관리와 MLOps")
print("=" * 70)

print("""
■ MLOps 파이프라인:

  ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐
  │ 데이터  │→→│ 학습   │→→│ 평가   │→→│ 배포   │→→│ 모니터링│
  │ 수집    │   │ 파이프  │   │ 검증   │   │ 서빙   │   │ 알림   │
  └────────┘   └────────┘   └────────┘   └────────┘   └────────┘
       ↑                                                    │
       └────────────────────────────────────────────────────┘
                      피드백 루프 (재학습)

■ 주요 도구:
  - MLflow: 실험 추적, 모델 레지스트리
  - DVC: 데이터 버전 관리 (Data Version Control)
  - Kubeflow: K8s 기반 ML 파이프라인
  - Weights & Biases: 실험 추적 + 시각화
  - BentoML: 모델 패키징 + 서빙

■ 모델 레지스트리:
  ┌─────────────────────────────────────────────┐
  │ 모델 이름     │ 버전 │ 상태    │ 정확도    │
  ├─────────────────────────────────────────────┤
  │ image_clf    │ v1   │ 아카이브 │ 92.3%    │
  │ image_clf    │ v2   │ 스테이징 │ 94.1%    │
  │ image_clf    │ v3   │ 프로덕션 │ 95.7%    │
  └─────────────────────────────────────────────┘

■ A/B 테스트:
  트래픽의 90%는 v3(현재), 10%는 v4(신규)로 보내서
  실제 성능 비교 후 전환 결정!
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 10. [실습] 전체 ML 파이프라인 시뮬레이션
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("10. [실습] 전체 ML 파이프라인 시뮬레이션")
print("=" * 70)

def full_ml_pipeline():
    """전체 ML 파이프라인 시뮬레이션"""

    # ── Step 1: 데이터 준비 ──
    print("\n■ Step 1: 데이터 준비")
    n_train, n_test = 1000, 200
    n_classes = 5
    print(f"  학습 데이터: {n_train}개, 테스트: {n_test}개, 클래스: {n_classes}")
    print(f"  전처리: 정규화(0~1), 리사이즈(224x224), 증강(flip+rotation)")

    # ── Step 2: 모델 선택 ──
    print("\n■ Step 2: 모델 선택")
    print(f"  기본 모델: EfficientNetB0 (사전학습)")
    print(f"  전략: Feature Extraction → Fine-Tuning")
    print(f"  분류기: GAP → Dropout(0.3) → Dense({n_classes}, softmax)")

    # ── Step 3: 학습 ──
    print("\n■ Step 3: 학습")
    print(f"  옵티마이저: Adam (lr=0.001)")
    print(f"  콜백: EarlyStopping, ModelCheckpoint, ReduceLR")

    best_val_acc = 0
    for epoch in range(1, 16):
        train_acc = min(0.99, 0.5 + 0.035 * epoch + random.gauss(0, 0.01))
        val_acc = min(0.97, 0.5 + 0.03 * epoch + random.gauss(0, 0.015))
        best_val_acc = max(best_val_acc, val_acc)
        if epoch <= 3 or epoch % 5 == 0 or epoch == 15:
            print(f"  Epoch {epoch:2d}: train_acc={train_acc:.2%}, val_acc={val_acc:.2%}")

    # ── Step 4: 평가 ──
    print(f"\n■ Step 4: 모델 평가")
    test_acc = best_val_acc - random.uniform(0.01, 0.02)
    print(f"  테스트 정확도: {test_acc:.2%}")
    print(f"  혼동 행렬, 분류 리포트 생성...")

    # 혼동 행렬 시뮬레이션
    classes = ['A', 'B', 'C', 'D', 'E']
    print(f"\n  혼동 행렬 (간소화):")
    print(f"  예측→  {'   '.join(classes)}")
    for i, c in enumerate(classes):
        row = []
        for j in range(n_classes):
            if i == j:
                row.append(random.randint(35, 40))
            else:
                row.append(random.randint(0, 3))
        print(f"  {c}:    {'  '.join(f'{v:3d}' for v in row)}")

    # ── Step 5: 최적화 ──
    print(f"\n■ Step 5: 모델 최적화")
    original_size_mb = 20.3
    print(f"  원본 모델 크기: {original_size_mb:.1f} MB")

    optimizations = [
        ("양자화 (int8)", original_size_mb / 4, test_acc - 0.005),
        ("프루닝 (50%)", original_size_mb / 2.5, test_acc - 0.003),
        ("프루닝 + 양자화", original_size_mb / 8, test_acc - 0.008),
    ]

    for name, size, acc in optimizations:
        print(f"  {name:20s}: {size:5.1f} MB, 정확도={acc:.2%}")

    # ── Step 6: 변환 및 배포 ──
    print(f"\n■ Step 6: 변환 및 배포")
    print(f"  SavedModel → TFLite 변환 완료")
    print(f"  SavedModel → ONNX 변환 완료")
    print(f"  TF Serving Docker 이미지 빌드 완료")

    # ── Step 7: 서빙 ──
    print(f"\n■ Step 7: 서빙 및 모니터링")
    print(f"  REST API: POST /v1/models/classifier:predict")
    print(f"  gRPC:     port 8500")
    print(f"  평균 지연: 12ms (GPU)")
    print(f"  처리량: ~83 QPS")

    # 추론 시뮬레이션
    print(f"\n  실시간 추론 테스트:")
    for i in range(3):
        start = time.time()
        # 추론 시뮬레이션
        pred_class = classes[random.randint(0, 4)]
        confidence = random.uniform(0.85, 0.99)
        latency = random.uniform(8, 15)
        print(f"    요청 {i+1}: 예측={pred_class}, 확신도={confidence:.2%}, "
              f"지연={latency:.1f}ms")

    print(f"\n■ 파이프라인 완료!")
    print(f"  최종 정확도: {test_acc:.2%}")
    print(f"  모델 크기: {original_size_mb / 4:.1f} MB (양자화)")
    print(f"  추론 속도: ~12ms (GPU)")

full_ml_pipeline()


print("\n" + "=" * 70)
print("요약: 모델 배포 학습 완료!")
print("=" * 70)
print("""
  1. 모델 저장: .keras (추천), SavedModel (서빙), .h5 (레거시)
  2. TFLite: 모바일/엣지 배포, 양자화로 4배 경량화
  3. TF Serving: REST/gRPC API, Docker 배포, 버전 관리
  4. ONNX: 프레임워크 간 호환, ONNX Runtime 추론
  5. 양자화: float32→int8, 크기↓ 속도↑ 정확도 유지
  6. 프루닝: 불필요한 가중치 제거, 모델 압축
  7. 지식 증류: 큰 모델→작은 모델로 지식 전달
  8. 추론 파이프라인: 전처리→모델→후처리 통합

  전체 과정 완료! TensorFlow/Keras 학습을 마칩니다!

  학습 순서 복습:
  01: 텐서 기초      → 02: Sequential 모델  → 03: 레이어/활성화
  04: 옵티마이저/손실 → 05: CNN/이미지      → 06: 콜백/학습관리
  07: 전이학습       → 08: RNN/텍스트       → 09: Functional API
  10: 모델 배포

  다음 도전: 실제 프로젝트에 적용해 보세요!
""")
