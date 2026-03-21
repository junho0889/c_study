# #########################################################################
#
#   PyTorch 학습 10단계: 배포와 프로덕션
#   - TorchScript, ONNX, 추론 최적화, 양자화, 분산 학습, 모델 서빙 -
#   # 실행 방법: python 10_deployment_production.py (개념 학습용, PyTorch 없이 실행 가능)
#   # PyTorch 설치: pip install torch torchvision
#
# #########################################################################

import math
import random
import json
import time

random.seed(42)

# ===============================================================================
#  1. TorchScript - 모델 직렬화
# ===============================================================================
print("=" * 70)
print("Part 1: TorchScript")
print("=" * 70)

print("""
TorchScript = PyTorch 모델을 Python 없이 실행 가능한 형태로 변환

왜 필요한가?
  - Python 없는 환경에서 실행 (C++, 모바일)
  - 최적화된 추론 속도
  - 모델 배포의 표준 방법

두 가지 변환 방법:
  1. torch.jit.trace: 예제 입력을 따라가며 변환 (간단하지만 조건문 무시)
  2. torch.jit.script: 코드를 분석하여 변환 (조건문 지원, 더 정확)
""")


# TorchScript 개념 시뮬레이션
class SimpleModel:
    """간단한 모델"""
    def __init__(self):
        self.w = [0.5, -0.3, 0.8]
        self.b = 0.1

    def forward(self, x):
        return sum(self.w[i] * x[i] for i in range(len(x))) + self.b


# --- torch.jit.trace 시뮬레이션 ---
print("\n--- torch.jit.trace 시뮬레이션 ---")

class TracedModel:
    """trace 방식: 예제 입력으로 실행 경로 기록"""

    def __init__(self, original_model, example_input):
        self.operations = []
        # 예제 입력을 실행하며 연산 기록
        self.operations.append(f"입력: {example_input}")
        result = original_model.forward(example_input)
        self.operations.append(f"Linear: w={original_model.w}, b={original_model.b}")
        self.operations.append(f"출력: {result}")
        self.model = original_model
        print(f"  Trace 완료! 기록된 연산: {len(self.operations)}개")

    def __call__(self, x):
        return self.model.forward(x)

model = SimpleModel()
example = [1.0, 2.0, 3.0]
traced = TracedModel(model, example)
print(f"  기록된 연산:")
for op in traced.operations:
    print(f"    {op}")

print(f"\n  [주의] trace의 한계: if/for 등 제어문이 고정됨!")
print(f"     → trace 시 True 경로를 탔다면, False 경로는 영영 무시")

# --- torch.jit.script 시뮬레이션 ---
print("\n--- torch.jit.script 시뮬레이션 ---")
print("""
  script 방식: 코드 자체를 분석하여 변환
  → if/for 같은 제어문도 올바르게 처리
  → 하지만 Python 기능을 100% 지원하지는 않음 (동적 타입 등)

  권장: 간단한 모델 → trace, 복잡한 모델 → script
""")

# 실제 PyTorch 코드:
# # trace 방식
# model.eval()
# example_input = torch.randn(1, 3, 224, 224)
# traced_model = torch.jit.trace(model, example_input)
# traced_model.save("model_traced.pt")
#
# # script 방식
# scripted_model = torch.jit.script(model)
# scripted_model.save("model_scripted.pt")
#
# # 로드 (Python 없이도 가능!)
# loaded = torch.jit.load("model_traced.pt")
# output = loaded(input_tensor)


# ===============================================================================
#  2. ONNX 내보내기
# ===============================================================================
print("\n" + "=" * 70)
print("Part 2: ONNX 내보내기")
print("=" * 70)

print("""
ONNX = Open Neural Network Exchange (개방형 신경망 교환 형식)

서로 다른 프레임워크 간 모델 교환이 가능!
  PyTorch → ONNX → TensorRT (NVIDIA GPU 최적화)
  PyTorch → ONNX → TensorFlow
  PyTorch → ONNX → ONNX Runtime (마이크로소프트)
  PyTorch → ONNX → Core ML (Apple)

장점:
  - 프레임워크 독립적 배포
  - 다양한 런타임 환경 지원
  - 추론 최적화 도구(TensorRT 등) 활용 가능
""")

# ONNX 구조 시뮬레이션
class ONNXExporter:
    """ONNX 내보내기 시뮬레이션"""

    def __init__(self, model_name):
        self.model_name = model_name
        self.graph = {
            "nodes": [],
            "inputs": [],
            "outputs": [],
        }

    def export(self, input_names, output_names, dynamic_axes=None):
        self.graph["inputs"] = input_names
        self.graph["outputs"] = output_names

        print(f"\n  ONNX 내보내기:")
        print(f"    모델: {self.model_name}")
        print(f"    입력: {input_names}")
        print(f"    출력: {output_names}")
        if dynamic_axes:
            print(f"    동적 축: {dynamic_axes}")
        print(f"    → model.onnx 저장 완료 (시뮬레이션)")

exporter = ONNXExporter("ResNet50")
exporter.export(
    input_names=["image"],
    output_names=["class_probs"],
    dynamic_axes={"image": {0: "batch_size"}, "class_probs": {0: "batch_size"}}
)

# 실제 PyTorch 코드:
# model.eval()
# dummy_input = torch.randn(1, 3, 224, 224)
#
# torch.onnx.export(
#     model,
#     dummy_input,
#     "model.onnx",
#     export_params=True,
#     opset_version=13,
#     do_constant_folding=True,
#     input_names=['input'],
#     output_names=['output'],
#     dynamic_axes={
#         'input': {0: 'batch_size'},
#         'output': {0: 'batch_size'}
#     }
# )
#
# # ONNX Runtime으로 추론:
# import onnxruntime as ort
# session = ort.InferenceSession("model.onnx")
# result = session.run(None, {"input": input_numpy})


# ===============================================================================
#  3. 추론 최적화
# ===============================================================================
print("\n" + "=" * 70)
print("Part 3: 추론 최적화")
print("=" * 70)

print("""
추론(Inference) 시 성능을 최적화하는 방법들:

1. model.eval() - 필수!
   - BatchNorm: 학습 통계 대신 이동 평균 사용
   - Dropout: 비활성화 (모든 뉴런 사용)
   - 이거 안 하면 예측 결과가 매번 달라질 수 있음!

2. torch.no_grad() - 필수!
   - 기울기 계산 비활성화
   - 메모리 절약 (기울기 저장 안 함)
   - 속도 향상 (역전파 그래프 생성 안 함)

3. 배치 추론
   - 한 번에 여러 입력을 처리 → GPU 활용 극대화

4. GPU 고정 메모리 (pin_memory)
   - CPU→GPU 전송 속도 향상
""")

# 추론 성능 비교 시뮬레이션
print("\n--- 추론 최적화 효과 (시뮬레이션) ---")

class InferenceTimer:
    """추론 시간 시뮬레이션"""

    def benchmark(self, mode, batch_size=1, num_iterations=100):
        # 시뮬레이션 시간 (ms)
        base_time = 10.0  # 기본 10ms
        times = {
            "no_optimization": base_time,
            "eval_mode": base_time * 0.95,
            "no_grad": base_time * 0.7,
            "eval_no_grad": base_time * 0.65,
            "batched": base_time * 0.3,
            "torchscript": base_time * 0.5,
            "onnx_runtime": base_time * 0.4,
            "tensorrt": base_time * 0.2,
        }
        return times.get(mode, base_time)


timer = InferenceTimer()
modes = [
    ("최적화 없음", "no_optimization"),
    ("model.eval()", "eval_mode"),
    ("torch.no_grad()", "no_grad"),
    ("eval + no_grad", "eval_no_grad"),
    ("배치 추론 (32)", "batched"),
    ("TorchScript", "torchscript"),
    ("ONNX Runtime", "onnx_runtime"),
    ("TensorRT", "tensorrt"),
]

print(f"\n{'최적화 방법':>25} {'추론 시간':>12} {'속도 향상':>10}")
print("-" * 50)
base = timer.benchmark("no_optimization")
for name, mode in modes:
    t = timer.benchmark(mode)
    speedup = base / t
    bar = "#" * int(speedup * 5)
    print(f"{name:>25} {t:>8.1f} ms {speedup:>8.1f}x  {bar}")

# 실제 PyTorch 코드:
# # 추론 최적화 패턴
# model.eval()                      # 1. eval 모드
#
# with torch.no_grad():             # 2. 기울기 추적 끄기
#     # 배치 처리
#     batch = torch.stack(images)    # 3. 배치로 묶기
#     batch = batch.to(device)
#     outputs = model(batch)
#
# # 또는 torch.inference_mode() (PyTorch 1.9+, no_grad보다 빠름)
# with torch.inference_mode():
#     outputs = model(batch)


# ===============================================================================
#  4. 양자화 (Quantization)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 4: 양자화 (Quantization)")
print("=" * 70)

print("""
양자화 = 모델의 가중치/활성화를 더 적은 비트로 표현

FP32 (32비트) → INT8 (8비트)
  - 모델 크기 약 4배 감소
  - 추론 속도 2~4배 향상
  - 정확도 약간 감소 (보통 1% 이내)

양자화 종류:
  1. 동적 양자화 (Dynamic): 가중치만 양자화, 런타임에 활성화 양자화
  2. 정적 양자화 (Static): 가중치 + 활성화 양자화 (보정 데이터 필요)
  3. 양자화 인지 학습 (QAT): 학습 중 양자화 시뮬레이션 → 최고 정확도

비유: 사진 압축
  - 원본 (FP32): 고화질, 큰 파일
  - 압축 (INT8): 약간 흐리지만 충분히 쓸만, 작은 파일
""")


def simulate_quantization(values, bits=8):
    """양자화 시뮬레이션: FP32 → INT8 → FP32"""
    min_val = min(values)
    max_val = max(values)
    num_levels = 2 ** bits

    # 양자화: 연속값 → 이산값
    scale = (max_val - min_val) / (num_levels - 1)
    if scale == 0:
        scale = 1e-8

    quantized = [round((v - min_val) / scale) for v in values]
    quantized = [max(0, min(num_levels - 1, q)) for q in quantized]

    # 역양자화: 이산값 → 근사 연속값
    dequantized = [q * scale + min_val for q in quantized]

    return quantized, dequantized, scale


# 양자화 데모
print("\n--- 양자화 시뮬레이션 ---")
original = [0.123, -0.456, 0.789, -0.012, 0.345, -0.678, 0.901, -0.234]

for bits in [8, 4, 2]:
    quant, dequant, scale = simulate_quantization(original, bits)
    errors = [abs(o - d) for o, d in zip(original, dequant)]
    avg_error = sum(errors) / len(errors)
    print(f"\n  {bits}-bit 양자화 (scale={scale:.6f}):")
    print(f"    원본:     [{', '.join(f'{v:7.4f}' for v in original[:4])} ...]")
    print(f"    양자화:   [{', '.join(f'{v:7d}' for v in quant[:4])} ...]")
    print(f"    복원:     [{', '.join(f'{v:7.4f}' for v in dequant[:4])} ...]")
    print(f"    평균 오차: {avg_error:.6f}")

print("\n→ 8비트면 오차가 매우 작고, 4비트도 실용적!")

# 실제 PyTorch 코드:
# # 동적 양자화 (가장 간단)
# quantized_model = torch.quantization.quantize_dynamic(
#     model,
#     {nn.Linear},          # 양자화할 레이어 타입
#     dtype=torch.qint8     # 8비트 정수
# )
#
# # 정적 양자화
# model.qconfig = torch.quantization.get_default_qconfig('fbgemm')  # x86
# torch.quantization.prepare(model, inplace=True)
# # 보정 데이터로 실행
# for batch in calibration_loader:
#     model(batch)
# torch.quantization.convert(model, inplace=True)
#
# # 양자화 인지 학습 (QAT)
# model.qconfig = torch.quantization.get_default_qat_qconfig('fbgemm')
# torch.quantization.prepare_qat(model, inplace=True)
# # 학습 진행...
# torch.quantization.convert(model, inplace=True)


# ===============================================================================
#  5. 분산 학습 (Distributed Training)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 5: 분산 학습")
print("=" * 70)

print("""
분산 학습 = 여러 GPU/머신에서 동시에 학습

1. DataParallel (DP) - 간단하지만 비효율적
   - 하나의 GPU가 마스터, 나머지는 복사본
   - 마스터 GPU에 병목 발생
   - model = nn.DataParallel(model)

2. DistributedDataParallel (DDP) - 권장!
   - 각 GPU가 독립적으로 학습
   - All-Reduce로 기울기 동기화
   - 거의 선형적 속도 향상
   - 설정이 복잡하지만 성능이 훨씬 좋음

비유:
  DP = 한 명의 팀장이 일을 나눠주고 결과를 취합 (팀장에게 부담)
  DDP = 각자 독립적으로 일하고, 중간중간 결과 공유 (균등한 부담)
""")

# 분산 학습 효과 시뮬레이션
print("\n--- 분산 학습 속도 시뮬레이션 ---")

def estimate_training_time(num_gpus, mode="ddp"):
    base_time = 100  # 1 GPU 기준 100분
    if mode == "single":
        return base_time
    elif mode == "dp":
        # DataParallel: 병목 있음 (~70% 효율)
        return base_time / (num_gpus * 0.7)
    elif mode == "ddp":
        # DDP: 거의 선형 (~90% 효율)
        return base_time / (num_gpus * 0.9)

print(f"\n{'GPU 수':>8} {'단일 GPU':>12} {'DataParallel':>14} {'DDP':>12}")
print("-" * 50)
for gpus in [1, 2, 4, 8]:
    t_single = estimate_training_time(gpus, "single")
    t_dp = estimate_training_time(gpus, "dp")
    t_ddp = estimate_training_time(gpus, "ddp")
    print(f"{gpus:>8} {t_single:>10.1f}분 {t_dp:>12.1f}분 {t_ddp:>10.1f}분")

print("\n→ DDP가 더 효율적! (GPU 수에 거의 비례하여 빨라짐)")

# 실제 PyTorch 코드:
# # DataParallel (간단, 비권장)
# model = nn.DataParallel(model)
# model = model.to(device)
#
# # DistributedDataParallel (권장)
# import torch.distributed as dist
# from torch.nn.parallel import DistributedDataParallel as DDP
# from torch.utils.data.distributed import DistributedSampler
#
# # 초기화
# dist.init_process_group(backend='nccl')
# local_rank = int(os.environ['LOCAL_RANK'])
# torch.cuda.set_device(local_rank)
#
# model = model.to(local_rank)
# model = DDP(model, device_ids=[local_rank])
#
# sampler = DistributedSampler(dataset)
# loader = DataLoader(dataset, sampler=sampler, batch_size=32)
#
# # 실행: torchrun --nproc_per_node=4 train.py


# ===============================================================================
#  6. 모델 서빙 (Model Serving)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 6: 모델 서빙")
print("=" * 70)

print("""
모델 서빙 = 학습된 모델을 API로 제공하여 실시간 예측

주요 서빙 방법:
  1. TorchServe (PyTorch 공식)
  2. FastAPI + 직접 로딩
  3. Triton Inference Server (NVIDIA)
  4. BentoML, MLflow 등

고려사항:
  - 지연 시간 (Latency): 요청 → 응답 시간
  - 처리량 (Throughput): 초당 처리 요청 수
  - 확장성 (Scalability): 트래픽 증가 대응
  - 모니터링: 성능, 에러, 드리프트 감시
""")


# FastAPI 기반 서빙 시뮬레이션
class ModelServingSimulator:
    """모델 서빙 시뮬레이션"""

    def __init__(self, model_name):
        self.model_name = model_name
        self.request_count = 0
        self.total_latency = 0

    def predict(self, input_data):
        """예측 요청 처리"""
        start = time.time()

        # 모델 추론 시뮬레이션
        result = {
            "class": random.choice(["cat", "dog", "bird"]),
            "confidence": random.uniform(0.8, 0.99),
            "latency_ms": random.uniform(5, 20),
        }

        self.request_count += 1
        self.total_latency += result["latency_ms"]
        return result

    def health_check(self):
        return {"status": "healthy", "model": self.model_name}

    def metrics(self):
        avg_latency = self.total_latency / max(1, self.request_count)
        return {
            "total_requests": self.request_count,
            "avg_latency_ms": round(avg_latency, 2),
            "model": self.model_name,
        }


server = ModelServingSimulator("ResNet50-v2")
print(f"\n헬스 체크: {server.health_check()}")

print("\n--- API 요청 시뮬레이션 ---")
for i in range(5):
    result = server.predict({"image": f"cat_{i}.jpg"})
    print(f"  요청 {i+1}: class={result['class']:5s}, "
          f"confidence={result['confidence']:.2%}, "
          f"latency={result['latency_ms']:.1f}ms")

print(f"\n서버 메트릭: {server.metrics()}")

# 실제 FastAPI 서빙 코드:
# from fastapi import FastAPI, File, UploadFile
# import torch
# from torchvision import transforms
# from PIL import Image
# import io
#
# app = FastAPI()
# model = torch.jit.load("model.pt")
# model.eval()
#
# transform = transforms.Compose([
#     transforms.Resize(256),
#     transforms.CenterCrop(224),
#     transforms.ToTensor(),
#     transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
# ])
#
# @app.post("/predict")
# async def predict(file: UploadFile = File(...)):
#     image = Image.open(io.BytesIO(await file.read())).convert("RGB")
#     tensor = transform(image).unsqueeze(0)
#
#     with torch.no_grad():
#         output = model(tensor)
#         probs = torch.softmax(output, dim=1)
#         top_prob, top_idx = probs.topk(1)
#
#     return {"class": top_idx.item(), "confidence": top_prob.item()}
#
# # 실행: uvicorn serving:app --host 0.0.0.0 --port 8000


# TorchServe 설정:
# # 1. 모델 아카이브 생성
# # torch-model-archiver --model-name resnet50 \
# #     --version 1.0 \
# #     --model-file model.py \
# #     --serialized-file model.pth \
# #     --handler image_classifier
#
# # 2. TorchServe 시작
# # torchserve --start --model-store model_store \
# #     --models resnet50=resnet50.mar
#
# # 3. 추론 요청
# # curl http://localhost:8080/predictions/resnet50 -T cat.jpg


# ===============================================================================
#  7. 실습: 추론 파이프라인 완전 구현
# ===============================================================================
print("\n" + "=" * 70)
print("Part 7: 실습 - 완전한 추론 파이프라인")
print("=" * 70)


class InferencePipeline:
    """프로덕션 추론 파이프라인 시뮬레이션"""

    def __init__(self, model_path, device="cpu"):
        self.model_path = model_path
        self.device = device
        self.model = None
        self.classes = ["고양이", "강아지", "새", "물고기", "토끼"]

    def load_model(self):
        """모델 로드"""
        print(f"\n[1] 모델 로드: {self.model_path}")
        print(f"    디바이스: {self.device}")
        # 시뮬레이션: 모델 로드
        self.model = SimpleModel()
        print(f"    → 로드 완료!")

    def preprocess(self, input_data):
        """전처리"""
        print(f"\n[2] 전처리:")
        # ImageNet 정규화 시뮬레이션
        processed = {
            "resize": "256x256",
            "center_crop": "224x224",
            "normalize": "ImageNet (mean/std)",
            "to_tensor": True,
        }
        print(f"    Resize → CenterCrop → ToTensor → Normalize")
        return [random.gauss(0, 1) for _ in range(3)]  # 시뮬레이션

    def predict(self, processed_input):
        """추론"""
        print(f"\n[3] 추론:")
        print(f"    model.eval() + torch.no_grad()")

        # 시뮬레이션
        logits = [random.gauss(0, 1) for _ in range(len(self.classes))]
        # Softmax
        max_val = max(logits)
        exp_vals = [math.exp(x - max_val) for x in logits]
        total = sum(exp_vals)
        probs = [e / total for e in exp_vals]

        return logits, probs

    def postprocess(self, probs):
        """후처리"""
        print(f"\n[4] 후처리:")
        top_idx = probs.index(max(probs))
        top_prob = probs[top_idx]

        # Top-3 정렬
        indexed = list(enumerate(probs))
        indexed.sort(key=lambda x: x[1], reverse=True)
        top3 = [(self.classes[idx], prob) for idx, prob in indexed[:3]]

        result = {
            "prediction": self.classes[top_idx],
            "confidence": top_prob,
            "top3": top3,
        }
        return result

    def run(self, input_data):
        """전체 파이프라인 실행"""
        print(f"\n{'='*50}")
        print(f"추론 파이프라인 실행")
        print(f"{'='*50}")

        # 1. 모델 로드 (보통 한 번만)
        if self.model is None:
            self.load_model()

        # 2. 전처리
        processed = self.preprocess(input_data)

        # 3. 추론
        start_time = time.time()
        logits, probs = self.predict(processed)
        inference_time = (time.time() - start_time) * 1000  # ms

        # 4. 후처리
        result = self.postprocess(probs)

        # 결과 출력
        print(f"\n{'='*50}")
        print(f"결과:")
        print(f"  예측: {result['prediction']}")
        print(f"  신뢰도: {result['confidence']:.2%}")
        print(f"  Top-3:")
        for cls, prob in result['top3']:
            bar = "#" * int(prob * 40)
            print(f"    {cls:>8}: {prob:.2%} {bar}")
        print(f"  추론 시간: {inference_time:.2f}ms")
        print(f"{'='*50}")

        return result


# 파이프라인 실행
pipeline = InferencePipeline(model_path="best_model.pth", device="cpu")
result = pipeline.run("cat_photo.jpg")


# ===============================================================================
#  8. 배포 체크리스트
# ===============================================================================
print("\n" + "=" * 70)
print("Part 8: 프로덕션 배포 체크리스트")
print("=" * 70)

checklist = [
    ("모델 준비", [
        "model.eval() 호출 확인",
        "torch.no_grad() 또는 torch.inference_mode() 사용",
        "불필요한 레이어 제거 (Dropout 등은 eval에서 자동 비활성)",
        "입력 전처리가 학습 시와 동일한지 확인",
    ]),
    ("최적화", [
        "TorchScript 또는 ONNX로 변환",
        "양자화 적용 여부 검토 (INT8)",
        "배치 추론 구현",
        "GPU 사용 시 CUDA 최적화",
    ]),
    ("서빙", [
        "헬스 체크 엔드포인트 구현",
        "입력 검증 (크기, 형식, 범위)",
        "에러 핸들링 (타임아웃, 잘못된 입력)",
        "로깅 (요청, 응답, 에러, 지연 시간)",
    ]),
    ("모니터링", [
        "추론 지연 시간 모니터링",
        "GPU/CPU 사용률 모니터링",
        "모델 드리프트 감지 (정확도 변화)",
        "A/B 테스트 인프라",
    ]),
    ("보안", [
        "입력 크기 제한 (DoS 방지)",
        "인증/인가 구현",
        "모델 파일 접근 제한",
        "HTTPS 사용",
    ]),
]

for category, items in checklist:
    print(f"\n  [{category}]")
    for item in items:
        print(f"    [ ] {item}")


# ===============================================================================
#  핵심 정리
# ===============================================================================
print("\n" + "=" * 70)
print("핵심 정리")
print("=" * 70)
print("""
1. TorchScript: Python 없이 실행 가능한 모델 형식
   - trace: 간단한 모델용
   - script: 조건문 있는 모델용

2. ONNX: 프레임워크 간 교환 형식
   → TensorRT, ONNX Runtime 등으로 최적화 가능

3. 추론 최적화: model.eval() + torch.no_grad() 필수!
   → 배치 추론, inference_mode() 활용

4. 양자화: FP32 → INT8
   → 모델 크기 4배 감소, 속도 2~4배 향상

5. 분산 학습: DDP > DataParallel
   → torchrun으로 실행

6. 모델 서빙: FastAPI, TorchServe, Triton
   → 헬스 체크, 로깅, 모니터링 필수

[주의] 프로덕션 필수 체크:
   - model.eval() 호출했는가?
   - 전처리가 학습 시와 동일한가?
   - 에러 핸들링이 되어 있는가?
   - 모니터링이 설정되어 있는가?
""")

print("\n" + "=" * 70)
print("PyTorch 학습 전체 과정 완료!")
print("=" * 70)
print("""
축하합니다! 10단계의 PyTorch 학습을 모두 완료했습니다.

학습 순서 요약:
  01. 텐서와 Autograd      → 기본 자료형과 자동 미분
  02. nn.Module             → 신경망 구조 설계
  03. 손실 함수와 옵티마이저 → 학습의 핵심 요소
  04. Dataset과 DataLoader  → 데이터 파이프라인
  05. CNN                   → 이미지 처리
  06. RNN과 NLP             → 시퀀스/텍스트 처리
  07. 학습 트릭             → 성능 최적화
  08. 전이 학습             → 사전학습 모델 활용
  09. 고급 아키텍처         → ResNet, Transformer
  10. 배포와 프로덕션       → 실서비스 적용

다음 단계:
  - 실제 PyTorch를 설치하고 위 코드를 실행해 보세요
  - Kaggle 등에서 실제 데이터로 프로젝트를 진행해 보세요
  - Hugging Face의 Transformers 라이브러리도 살펴보세요
""")
