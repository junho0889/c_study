/*
=============================================================================
  C++ 학습 37단계: ML 추론 런타임
                  (LibTorch / ONNX Runtime / TensorRT / OpenVINO)
=============================================================================
  [학습 목표]
  1. C++로 ML 추론하는 이유와 트레이드오프
  2. 모델 포맷 변환 경로 (PyTorch → TorchScript / ONNX → TRT/OV)
  3. LibTorch / ONNX Runtime / TensorRT / OpenVINO 비교 선택
  4. 각 런타임의 코드 스켈레톤 (실제 SDK 호출 패턴)
  5. **GPU/CPU 메모리 관리 함정** (이번 챕터의 핵심)
  6. 양자화(INT8 / FP16), 동적 입력, 배치, 멀티스트림
  7. 운영 배포 패턴 (서빙 / 풀 / 배치 / 스로틀)

  [실무 배경]
    "학습은 Python, 추론은 C++" — 운영의 정석.
    이유:
      - GIL 없음, 멀티 스레드 자유
      - GC 일시정지 없음 → tail latency 안정
      - 메모리 control (pinned, mmap, GPU pool)
      - 외부 의존성 적은 단일 바이너리
      - 임베디드/엣지 디바이스 배포

    잘못 작성하면:
      - GPU OOM (워크스페이스 / 배치 / 스트림 누수)
      - tensor 수명 / 비동기 실행 race
      - H2D/D2H 복사 폭증으로 PCIe 포화
      - 첫 추론 (warmup) 100배 느림 → SLA 미스
      - 양자화 정확도 손실 / EU(Engineering Unit) 미스매치

  [이 파일의 한계]
    각 런타임은 별도 SDK 설치 필요 (수GB).
    그래서 main.cpp는 가이드 + 패턴 출력 + 핵심 코드 스켈레톤(주석화)을 제공.
    실제 빌드는 옆 폴더의 CMakeLists.txt 템플릿 참고.

  [컴파일 - 가이드 모드]
    g++ -std=c++17 -Wall -O2 -o 37_ml main.cpp
=============================================================================
*/

#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <chrono>
#include <stdexcept>
#include <cstdint>
using namespace std;

void lesson1_why_cpp_inference();
void lesson2_format_pipeline();
void lesson3_libtorch();
void lesson4_onnxruntime();
void lesson5_tensorrt();
void lesson6_openvino();
void lesson7_runtime_selection();
void lesson8_memory_pitfalls();
void lesson9_production_patterns();

/*
=============================================================================
  레슨별 출력 가이드 (이 main.cpp 자체는 정적 텍스트 출력 가이드,
  실제 SDK 코드는 옆 CMakeLists.txt.template + 별도 .cpp 작성 필요)
=============================================================================
  lesson1: Python vs C++ 추론 비교표 (지연/메모리/배포)
  lesson2: PyTorch → TorchScript/ONNX → 각 런타임 변환 흐름
  lesson3: LibTorch 코드 스켈레톤 (memory 함정 10개)
  lesson4: ONNX Runtime 코드 스켈레톤 + Execution Providers
  lesson5: TensorRT 빌드/추론 + workspace/INT8 calibration
  lesson6: OpenVINO Core/PrePostProcessor 패턴
  lesson7: 의사결정 트리 (NVIDIA→TRT, Intel→OV, 다양한→ORT, PyTorch→LibTorch)
  lesson8: 10가지 GPU 메모리 함정 (cudaMalloc, pinned, async sync, ...)
  lesson9: 프로덕션 패턴 (Triton, dynamic batching, health/ready, 메트릭)

  실제 추론 latency 비교 (ResNet-50 batch=1, T4 GPU):
    LibTorch FP32:   5~7 ms
    ORT CUDA FP32:   3~5 ms
    ORT TRT FP16:    1.5~2 ms
    TensorRT FP16:   1.0~1.5 ms
    TensorRT INT8:   0.6~1.0 ms
=============================================================================
*/

int main() {
    cout << "================================================\n";
    cout << "  C++ 37단계 : ML 추론 런타임\n";
    cout << "================================================\n\n";

    lesson1_why_cpp_inference();
    lesson2_format_pipeline();
    lesson3_libtorch();
    lesson4_onnxruntime();
    lesson5_tensorrt();
    lesson6_openvino();
    lesson7_runtime_selection();
    lesson8_memory_pitfalls();
    lesson9_production_patterns();

    cout << "\n37단계 학습 완료!\n";
    return 0;
}


// =============================================================================
//  레슨 1 — 왜 C++로 추론하는가
// =============================================================================

void lesson1_why_cpp_inference() {
    cout << "[레슨 1] 왜 C++로 ML 추론?\n";
    cout << R"(
  ┌─ Python 추론 vs C++ 추론 ─────────────────────────────┐
  │                                                       │
  │              │ Python (PyTorch)  │ C++ 런타임          │
  │──────────────┼───────────────────┼─────────────────────│
  │ 개발 속도    │ ★★★★★         │ ★★                  │
  │ 추론 지연    │ 보통              │ 30~70% 짧음         │
  │ Tail latency │ GIL/GC spike      │ 안정적              │
  │ 메모리 제어  │ 어려움             │ 직접 제어            │
  │ 배포 크기    │ 1~5GB (venv)     │ 수십~수백 MB        │
  │ 임베디드     │ 거의 불가          │ 표준                │
  │ 멀티스레드   │ GIL 한계           │ 자유                 │
  │ 의존성 지옥  │ 자주               │ 정적 링크 가능      │
  └───────────────────────────────────────────────────────┘

  ■ "학습은 Python, 추론은 C++" 패턴
    1. 데이터 사이언티스트가 PyTorch / TensorFlow로 학습
    2. 모델을 중간 포맷으로 export (TorchScript, ONNX)
    3. C++ 런타임으로 로드 → 운영 서비스 배포
    4. 모니터링: 정확도 변동 (drift) / 지연 / 메모리

  ■ 언제 Python 추론이 더 나음?
    ✓ 짧은 프로토타입 / PoC
    ✓ 하루 수천건 미만의 배치 작업
    ✓ 모델 자체가 비결정적이고 자주 바뀜
    ✓ 운영팀이 Python에 익숙

  ■ 언제 C++ 추론이 필수
    ✓ p99 지연 < 10ms 요구 (실시간 추천 / 광고 / 트레이딩)
    ✓ 임베디드 / 자율주행 / 로봇 / 의료기기
    ✓ 초당 수만~수십만 추론
    ✓ GPU 메모리를 정밀 제어 (멀티 모델 공존)
    ✓ 외부 인터넷 안 되는 폐쇄망 (GitHub, pip 못 씀)

  ■ 일반적 오해
    "Python = 무조건 느리다" → 실제 추론 자체는 결국 BLAS/CUDA 호출.
    Python wrapper 비용이 작은 모델일수록 큼. 큰 모델은 차이 작음.
    "C++가 빠르다" → API 사용을 잘못하면 Python보다 느려질 수도.
    중요한 건 **메모리 복사 횟수와 동기화 지점**이지 언어 자체 X.
)";
    cout << endl;
}


// =============================================================================
//  레슨 2 — 모델 포맷 변환 파이프라인
// =============================================================================

void lesson2_format_pipeline() {
    cout << "[레슨 2] 모델 포맷 변환 파이프라인\n";
    cout << R"(
  ■ 변환 흐름도

   학습 프레임워크          중간 포맷            최적화 런타임
   ─────────────────       ─────────────        ─────────────────
                                              ┌─ TensorRT (NVIDIA)
   PyTorch ──┐         ┌─ TorchScript .pt ─── └─ LibTorch C++
             │         │
             └─ ONNX ──┼─ .onnx              ┌─ ONNX Runtime
                       │                      ├─ TensorRT (ONNX→TRT)
   TensorFlow ──┐      │                      ├─ OpenVINO (ONNX→IR)
                ├─ SavedModel              ┌─ TFLite (모바일)
                └─ Keras .h5               └─ TF Serving

   (Hugging Face / JAX / scikit-learn 등도 ONNX export 가능)

  ■ TorchScript (PyTorch 전용 IR)
    torch.jit.script(model)   # 코드 분석으로 변환
    torch.jit.trace(model, x) # 예시 입력으로 그래프 캡처
    model.save("model.pt")    # 직렬화

    장점: PyTorch 기능 거의 그대로
    단점: NVIDIA 외 가속기 지원 부족, 그래프 최적화 제한적

  ■ ONNX (Open Neural Network Exchange)
    프레임워크 독립 표준. opset 버전 중요 (opset 13, 17, 19 등).
    torch.onnx.export(model, x, "model.onnx", opset_version=17)

    장점: 거의 모든 런타임에서 로드. 그래프 최적화 도구 풍부.
    단점: 일부 PyTorch 기능 변환 안 됨 (동적 컨트롤 플로우 등),
          opset 호환성 매트릭스 신경써야 함.

  ■ TensorRT 엔진 (.engine / .plan)
    NVIDIA GPU 특화. 빌드 시 해당 GPU/드라이버에 맞춰 커널 선택.
    → 빌드한 GPU와 다른 GPU에서는 동작 안 할 수 있음
    → CI에서 미리 빌드 X. 배포 후 첫 부팅 시 빌드하거나
      각 타겟 별 엔진 prebuild

  ■ OpenVINO IR (.xml + .bin)
    Intel 특화. xml = 그래프 구조, bin = 가중치.
    Intel CPU / iGPU / VPU(Movidius) / NPU 가속.
    Model Optimizer (mo) 또는 ovc 명령으로 변환:
      ovc model.onnx --output_model model.xml

  ■ 변환 단계에서 망가지는 흔한 케이스
    1) Custom op (예: torch.scatter, einsum 일부) → 변환 실패
       해결: 모델을 변환 친화적으로 재작성, 또는 custom plugin 작성
    2) Dynamic shape - 학습 시점은 batch=32, 추론은 가변
       → ONNX는 dynamic_axes 명시 필요
       → TRT는 optimization profile 명시
    3) Float64 → 대부분 런타임이 float32만 → 정밀도 손실 / 변환 실패
    4) Layer fusion 후 그래프 최적화로 중간 텐서 사라짐
       → 디버깅 어려움 (--keep_unused 등 옵션)
    5) 양자화 후 정확도 손실 → 품질 평가 데이터셋 별도 필수

  ┌─ 변환 검증 체크리스트 ────────────────────────────────┐
  │ ✓ 동일 입력에 대해 PyTorch vs 변환 모델 출력 일치     │
  │   (atol=1e-4, rtol=1e-3 정도가 일반적, FP16은 더 큼)  │
  │ ✓ 배치 사이즈별 정확도 동일 (batch norm 함정)         │
  │ ✓ 학습 vs 추론 모드 차이 (dropout, batchnorm 통계)    │
  │ ✓ 입력 전처리 / 후처리도 함께 export 또는 명시 문서화 │
  │ ✓ 모델 메타데이터 (입력 shape, 단위, scale) 첨부       │
  └───────────────────────────────────────────────────────┘
)";
    cout << endl;
}


// =============================================================================
//  레슨 3 — LibTorch (PyTorch C++ 프론트엔드)
// =============================================================================
//
//  [개요]
//    PyTorch 코드 그대로의 C++ API.
//    Python 모델을 거의 그대로 C++로 옮겨 추론 가능.
//
//  [설치]
//    https://pytorch.org/cppdocs/installing.html
//    libtorch 압축파일 (CPU 버전 ~200MB, CUDA 버전 ~1GB+)
//    CMake에서 find_package(Torch REQUIRED)
//
//  [장점]
//    - PyTorch 학습 코드와 거의 동일 API
//    - 동적 그래프 (즉, 일반 PyTorch 모델 그대로)
//    - autograd 사용 가능 (서버에서 학습도 가능)
//
//  [단점]
//    - 바이너리 크기 큼 (수백 MB)
//    - 다른 런타임보다 느림 (NVIDIA GPU에서도 TRT 대비 2~5배)
//    - libtorch 버전 ↔ CUDA / cuDNN 버전 호환성 까다로움
// =============================================================================

void lesson3_libtorch() {
    cout << "[레슨 3] LibTorch — PyTorch C++ 프론트엔드\n";
    cout << R"(
  ■ 코드 스켈레톤 (libtorch 설치 후 실제 빌드/실행 가능)
  ─────────────────────────────────────────────────────
  #include <torch/torch.h>
  #include <torch/script.h>

  int main() {
      // 1) 모델 로드 (TorchScript .pt)
      torch::jit::script::Module model;
      try {
          model = torch::jit::load("model.pt");
      } catch (const c10::Error& e) {
          std::cerr << "load failed: " << e.what() << std::endl;
          return 1;
      }

      // 2) 디바이스 선택 (메모리 함정 ①)
      torch::Device device(torch::kCUDA, 0);  // GPU 0
      // CPU fallback 자동 처리는 안 함 - 직접 try/catch
      if (!torch::cuda::is_available()) device = torch::kCPU;

      model.to(device);
      model.eval();             // dropout/batchnorm 추론 모드

      // 3) 입력 텐서 (메모리 함정 ②)
      // torch::from_blob는 외부 데이터를 zero-copy 참조 → 수명 주의!
      std::vector<float> input_data(1 * 3 * 224 * 224);
      // ... fill input_data ...
      auto input_tensor = torch::from_blob(
          input_data.data(),
          {1, 3, 224, 224},
          torch::kFloat32
      ).to(device);
      // ↑ 만약 input_data가 함수 끝나기 전 사라지면 input_tensor도 invalid

      // → 안전 패턴: clone() 으로 텐서가 자체 메모리 갖게
      auto input_safe = torch::from_blob(...).clone().to(device);

      // 4) 추론
      torch::NoGradGuard no_grad;          // autograd off → 메모리 절감
      std::vector<torch::jit::IValue> inputs{input_tensor};
      auto output = model.forward(inputs).toTensor();

      // 5) 결과를 CPU로 가져오기 (메모리 함정 ③)
      auto output_cpu = output.to(torch::kCPU);
      auto accessor = output_cpu.accessor<float, 2>();
      // ↑ to(kCPU)는 새 텐서 생성. 비동기 디바이스라면 .item() / .data_ptr()
      //   접근 시 자동 동기화. 명시적으로 torch::cuda::synchronize() 가능.

      // 6) 후처리
      auto top1 = output.argmax(1).item<int64_t>();
      std::cout << "predicted class: " << top1 << std::endl;
  }
  ─────────────────────────────────────────────────────

  ■ CMake 빌드
  ─────────────────────────────────────────────────────
  cmake_minimum_required(VERSION 3.18)
  project(my_inference)

  list(APPEND CMAKE_PREFIX_PATH "/path/to/libtorch")
  find_package(Torch REQUIRED)

  add_executable(my_inference main.cpp)
  target_link_libraries(my_inference "${TORCH_LIBRARIES}")
  set_property(TARGET my_inference PROPERTY CXX_STANDARD 17)

  # CUDA 라이브러리 런타임 검색 경로
  if(MSVC)
      file(GLOB TORCH_DLLS "${TORCH_INSTALL_PREFIX}/lib/*.dll")
      add_custom_command(TARGET my_inference POST_BUILD
          COMMAND ${CMAKE_COMMAND} -E copy_if_different
                  ${TORCH_DLLS} $<TARGET_FILE_DIR:my_inference>)
  endif()
  ─────────────────────────────────────────────────────

  ┌─ LibTorch 메모리 함정 ────────────────────────────────┐
  │ 1. torch::from_blob 외부 메모리 참조                   │
  │    → 외부 버퍼 수명 ≥ 텐서 수명 보장 또는 .clone()    │
  │ 2. NoGradGuard 누락 → autograd 그래프 누적 → OOM      │
  │ 3. .to(device) 는 비동기. 즉시 사용은 동기화 발생     │
  │    pinned memory (cuda::pin_memory) 활용으로 H2D 빠름 │
  │ 4. CUDA cache는 lazy free. 다른 텐서가 못 잡으면      │
  │    torch::cuda::empty_cache() 호출 (단, 비용 큼)      │
  │ 5. shared_ptr<Module> 패턴 - 멀티 스레드 추론 시      │
  │    같은 module 공유 가능 (모델 자체는 read-only)      │
  │    단, 입력 텐서는 스레드별 독립                       │
  │ 6. Tensor::operator= 는 view 공유 (deep copy 아님)    │
  │    → 한쪽 수정 시 다른 쪽 영향. .clone() 명시         │
  │ 7. AOT 컴파일 X (즉시 그래프 실행) → 첫 추론 느림     │
  │    실제로는 cuDNN benchmark 모드 첫 호출이 매우 느림   │
  │ 8. 멀티 GPU - .to("cuda:1") 명시. P2P 메모리 복사 비용│
  │ 9. torch::cuda::CUDAStream으로 스트림 분리 가능       │
  │    동시 추론 처리량 ↑                                  │
  │ 10. Mixed precision: torch::autocast (학습 위주, 추론은│
  │     model.half() 또는 model.to(torch::kFloat16))       │
  └───────────────────────────────────────────────────────┘

  ■ 성능 팁
    - 모델 to(device) 한 번만, 추론 루프엔 텐서만 옮김
    - 배치 추론 권장 (GPU 활용도 ↑)
    - 첫 호출은 워밍업으로 따로 (실제 부하 측정 전)
    - cudnn benchmark mode: torch::globalContext().setBenchmarkCuDNN(true)
)";
    cout << endl;
}


// =============================================================================
//  레슨 4 — ONNX Runtime (Microsoft)
// =============================================================================
//
//  [개요]
//    ONNX 모델을 다양한 백엔드 (CPU / CUDA / TensorRT / DirectML / CoreML /
//    OpenVINO / ROCm / WebGL ...)에서 실행하는 통합 런타임.
//    Microsoft가 주도하지만 오픈소스 (MIT).
//
//  [장점]
//    - 가장 폭넓은 플랫폼 지원
//    - 가벼움 (CPU 전용 ~10MB)
//    - 모델 한 번 export → 어디서든 실행
//    - Execution Provider (EP) 추상화로 백엔드 교체 쉬움
//
//  [단점]
//    - 절대 성능은 TRT / OV 보다 보통 약간 낮음
//    - 일부 op 미지원 (opset / EP 별로 다름)
//
//  [설치]
//    https://github.com/microsoft/onnxruntime/releases
//    NuGet / pip / 미리 빌드된 바이너리 / 직접 빌드
// =============================================================================

void lesson4_onnxruntime() {
    cout << "[레슨 4] ONNX Runtime — 통합 추론 엔진\n";
    cout << R"(
  ■ 코드 스켈레톤 (C++ API)
  ─────────────────────────────────────────────────────
  #include <onnxruntime_cxx_api.h>

  int main() {
      // 1) Environment - 프로세스 단위 1개 (메모리 함정 ①)
      // Env는 thread-pool / 로깅 관리. 여러 번 만들지 말 것.
      Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "MyApp");

      // 2) SessionOptions
      Ort::SessionOptions opt;
      opt.SetIntraOpNumThreads(1);     // op 내부 병렬 (보통 1, 외부에서 배치)
      opt.SetInterOpNumThreads(1);
      opt.SetGraphOptimizationLevel(GraphOptimizationLevel::ORT_ENABLE_ALL);

      // 3) Execution Provider 선택 (메모리 함정 ②)
      // 우선순위 순으로 추가. 못 쓰는 EP는 자동 fallback.
      // 단, 명시 안 한 EP는 사용 안 함.
      OrtCUDAProviderOptions cuda_opt{};
      cuda_opt.device_id = 0;
      cuda_opt.gpu_mem_limit = SIZE_MAX;
      cuda_opt.arena_extend_strategy = 0;       // kNextPowerOfTwo
      cuda_opt.cudnn_conv_algo_search = OrtCudnnConvAlgoSearchExhaustive;
      cuda_opt.do_copy_in_default_stream = 1;
      opt.AppendExecutionProvider_CUDA(cuda_opt);

      // (TensorRT EP - 더 빠르지만 첫 호출 시 빌드 시간 큼)
      // OrtTensorRTProviderOptions trt_opt{};
      // trt_opt.device_id = 0;
      // trt_opt.trt_max_workspace_size = 2147483648;   // 2GB
      // trt_opt.trt_fp16_enable = true;
      // trt_opt.trt_engine_cache_enable = true;        // 빌드 캐시
      // trt_opt.trt_engine_cache_path = "./trt_cache";
      // opt.AppendExecutionProvider_TensorRT(trt_opt);

      // 4) Session 로드
      Ort::Session session(env, L"model.onnx", opt);

      // 5) 입력/출력 메타데이터
      Ort::AllocatorWithDefaultOptions allocator;
      auto input_name  = session.GetInputNameAllocated(0, allocator);
      auto output_name = session.GetOutputNameAllocated(0, allocator);
      auto type_info   = session.GetInputTypeInfo(0);
      auto tensor_info = type_info.GetTensorTypeAndShapeInfo();
      auto input_shape = tensor_info.GetShape();
      // input_shape에 -1이 있으면 동적 차원 - 추론 시 실제 값 채움

      // 6) 입력 텐서 생성 (메모리 함정 ③)
      std::vector<float> input_data(1 * 3 * 224 * 224);
      // ... fill ...

      auto memory_info = Ort::MemoryInfo::CreateCpu(
          OrtArenaAllocator, OrtMemTypeDefault);

      std::vector<int64_t> shape{1, 3, 224, 224};
      auto input_tensor = Ort::Value::CreateTensor<float>(
          memory_info,
          input_data.data(), input_data.size(),
          shape.data(), shape.size()
      );
      // ↑ 외부 버퍼 참조. 추론 끝날 때까지 input_data 살아있어야 함

      // 7) 추론
      const char* input_names[]  = {input_name.get()};
      const char* output_names[] = {output_name.get()};

      auto output_tensors = session.Run(
          Ort::RunOptions{nullptr},
          input_names, &input_tensor, 1,
          output_names, 1
      );

      // 8) 결과 읽기
      float* out_data = output_tensors[0].GetTensorMutableData<float>();
      auto out_shape  = output_tensors[0]
                          .GetTensorTypeAndShapeInfo().GetShape();
      // ... use out_data ...

      // 9) IoBinding (메모리 함정 ④) - 고성능 패턴
      // 매 Run마다 입출력 텐서 만들지 않고 바인딩 재사용
      Ort::IoBinding io_binding(session);
      io_binding.BindInput("input", input_tensor);
      io_binding.BindOutput("output", memory_info);
      session.Run(Ort::RunOptions{}, io_binding);
  }
  ─────────────────────────────────────────────────────

  ┌─ ONNX Runtime 메모리 함정 ────────────────────────────┐
  │ 1. Env는 프로세스 1개. 여러 Session 공유               │
  │    → Env 내부 thread pool 공유 → CPU 사용 효율 ↑     │
  │ 2. CreateTensor의 외부 버퍼 (Wrapper)                  │
  │    → 추론 완료까지 살아있어야 함                       │
  │    → 비동기 Run에선 더 길게                           │
  │ 3. Run() 반환 텐서는 ORT가 소유 (자동 해제)            │
  │    → out_data 포인터는 Ort::Value 살아있을 때만        │
  │ 4. Arena Allocator: 한 번 잡은 큰 청크를 재사용        │
  │    → 처음엔 메모리 ↑, 안정 후엔 빠름                   │
  │    arena_extend_strategy 조정으로 단편화 제어         │
  │ 5. CUDA 텐서: BindInput에 GPU 메모리 직접 전달 가능    │
  │    → H2D 복사 회피                                     │
  │ 6. Dynamic shape: ORT가 매 Run마다 메모리 재할당       │
  │    → 가능하면 batch size를 한정 / 묶음 처리           │
  │ 7. SessionOptions::SetMemPattern - 첫 추론으로         │
  │    메모리 패턴 학습 → 이후 빠름. 단, dynamic shape면 끔│
  │ 8. ORT_DISABLE_ALL 그래프 최적화로 디버깅              │
  │ 9. DML EP (Windows Direct ML) → AMD/Intel GPU 활용    │
  │ 10. Web (ort-web) WASM 빌드 - SIMD/threads 켤지 결정  │
  │     SharedArrayBuffer 헤더 필요 (COOP/COEP)           │
  └───────────────────────────────────────────────────────┘

  ■ EP 우선순위 (전형 패턴)
    NVIDIA GPU:  TensorRT EP > CUDA EP > CPU EP
    Intel:       OpenVINO EP > CPU EP
    Apple:       CoreML EP > CPU EP
    AMD GPU:     ROCm EP / DML EP > CPU EP
    Windows:     DML EP (벤더 무관) > CPU EP

  ■ 권장 사용 시나리오
    ★ 첫 선택 (대부분의 경우)
      → 모델 한 번 export, 다양한 환경 배포 가능
      → 성능이 충분히 좋음 (CPU/GPU 모두)
      → 의존성 가볍고 바이너리 작음
)";
    cout << endl;
}


// =============================================================================
//  레슨 5 — TensorRT (NVIDIA)
// =============================================================================
//
//  [개요]
//    NVIDIA GPU 전용 추론 엔진. ONNX 또는 직접 정의 그래프 → 엔진 빌드.
//    Layer fusion, kernel auto-tuning, INT8/FP16 양자화로 극강 성능.
//
//  [장점]
//    - NVIDIA GPU에서 가장 빠름 (보통 LibTorch 대비 2~5배)
//    - 양자화 워크플로우 성숙 (INT8 calibration)
//    - 다중 스트림 / 다중 컨텍스트로 throughput 최대화
//
//  [단점]
//    - NVIDIA 전용
//    - 엔진은 GPU/드라이버/TRT 버전 종속 → 배포 환경 별 빌드
//    - API 복잡 / 학습 곡선 가파름
//    - 빌드 시간 오래 걸림 (몇 분 ~ 수십 분)
// =============================================================================

void lesson5_tensorrt() {
    cout << "[레슨 5] TensorRT — NVIDIA GPU 최강 추론\n";
    cout << R"(
  ■ 워크플로우
  ─────────────────────────────────────────────────────
   .onnx → trtexec / API → .engine → C++ 추론
   (호스트 PC: 빌드)        (대상 GPU: 실행)

   trtexec --onnx=model.onnx \
           --saveEngine=model.engine \
           --fp16 \
           --workspace=2048 \
           --minShapes=input:1x3x224x224 \
           --optShapes=input:8x3x224x224 \
           --maxShapes=input:32x3x224x224

  ■ 코드 스켈레톤 (C++ API, TRT 8.x+)
  ─────────────────────────────────────────────────────
  #include <NvInfer.h>
  #include <cuda_runtime_api.h>
  #include <fstream>

  using namespace nvinfer1;

  // RAII deleter (메모리 함정 ①)
  template<typename T>
  struct TrtDestroyer { void operator()(T* p) const { delete p; } };
  template<typename T>
  using TrtUnique = std::unique_ptr<T, TrtDestroyer<T>>;

  class Logger : public ILogger {
      void log(Severity s, const char* msg) noexcept override {
          if (s <= Severity::kWARNING) std::cerr << msg << std::endl;
      }
  } gLogger;

  int main() {
      // 1) 엔진 파일 로드
      std::ifstream f("model.engine", std::ios::binary);
      f.seekg(0, std::ios::end); size_t sz = f.tellg(); f.seekg(0);
      std::vector<char> data(sz); f.read(data.data(), sz);

      // 2) Runtime / Engine / Context (메모리 함정 ②)
      TrtUnique<IRuntime> runtime{ createInferRuntime(gLogger) };
      TrtUnique<ICudaEngine> engine{
          runtime->deserializeCudaEngine(data.data(), sz)
      };
      // 한 engine은 여러 context 생성 가능 (멀티스레드 추론 패턴)
      TrtUnique<IExecutionContext> ctx{ engine->createExecutionContext() };

      // 3) Stream (메모리 함정 ③)
      cudaStream_t stream;
      cudaStreamCreate(&stream);

      // 4) GPU 버퍼 할당 (메모리 함정 ④)
      // 입출력 인덱스 / shape는 엔진에서 조회
      auto in_idx  = engine->getBindingIndex("input");
      auto out_idx = engine->getBindingIndex("output");
      auto in_dims = engine->getBindingDimensions(in_idx);

      // dynamic shape면 setBindingDimensions로 실제값 지정
      ctx->setBindingDimensions(in_idx, Dims4{1, 3, 224, 224});

      size_t in_size  = 1 * 3 * 224 * 224 * sizeof(float);
      size_t out_size = 1 * 1000 * sizeof(float);

      void* d_in;  cudaMalloc(&d_in,  in_size);
      void* d_out; cudaMalloc(&d_out, out_size);

      void* bindings[2];
      bindings[in_idx]  = d_in;
      bindings[out_idx] = d_out;

      // 5) 호스트 → GPU 복사 (Pinned memory 권장 - 메모리 함정 ⑤)
      float* h_in;
      cudaMallocHost(&h_in, in_size);   // Pinned (page-locked)
      // ... fill h_in ...
      cudaMemcpyAsync(d_in, h_in, in_size, cudaMemcpyHostToDevice, stream);

      // 6) 추론 실행
      ctx->enqueueV2(bindings, stream, nullptr);

      // 7) GPU → 호스트
      float* h_out;
      cudaMallocHost(&h_out, out_size);
      cudaMemcpyAsync(h_out, d_out, out_size, cudaMemcpyDeviceToHost, stream);

      // 8) 동기화 (메모리 함정 ⑥)
      cudaStreamSynchronize(stream);
      // 동기화 전에 h_out 읽으면 stale 데이터

      // ... use h_out ...

      // 9) 정리
      cudaFreeHost(h_in);
      cudaFreeHost(h_out);
      cudaFree(d_in);
      cudaFree(d_out);
      cudaStreamDestroy(stream);
      // RAII로 engine / runtime / context 자동 해제
  }
  ─────────────────────────────────────────────────────

  ┌─ TensorRT 메모리 함정 ────────────────────────────────┐
  │ 1. RAII 누락 - delete 직접 호출은 잊기 쉬움            │
  │    → unique_ptr custom deleter 패턴 강제                │
  │ 2. Engine은 read-only, Context는 mutable               │
  │    → 1 engine + N context로 멀티 스레드 추론           │
  │    (스레드 별 별도 context, 별도 stream)              │
  │ 3. Workspace 크기 - 빌드 시 max workspace 설정.       │
  │    크면 더 빠른 커널 선택 / 너무 크면 OOM              │
  │    → 운영 GPU 메모리에 맞춰 조정 (1~4GB 일반적)        │
  │ 4. Binding buffer 수명: enqueue 호출 후 stream sync    │
  │    전엔 절대 free / 변경 X (비동기 실행 중)             │
  │ 5. Pinned (page-locked) 메모리                         │
  │    cudaMallocHost - H2D/D2H 빠름 (PCIe DMA 가능)        │
  │    너무 많이 잡으면 OS 페이징 시스템 압박             │
  │ 6. Stream synchronization 잊으면 stale read           │
  │    → cudaStreamSynchronize 또는 cudaEventSynchronize │
  │ 7. Dynamic shape: setBindingDimensions 매 Run마다      │
  │    잘못 호출하면 wrong dims로 NaN 결과                 │
  │ 8. INT8 calibration: 대표 데이터셋 100~500 샘플 필요   │
  │    잘못된 샘플 → 정확도 폭락                            │
  │ 9. Engine 빌드 caching - .engine 파일은 GPU/TRT 버전   │
  │    의존. 다른 환경엔 다시 빌드 (또는 prebuild 매트릭스)│
  │ 10. Multi-GPU: cudaSetDevice(N) → 각 GPU에 별도 engine │
  │    P2P 메모리 복사 비용은 NVLink 유무로 차이 큼         │
  │ 11. 메모리 풀: TRT 8.5+의 IGpuAsyncAllocator로 커스텀  │
  │    → 추론 중 cudaMalloc 호출 회피로 latency 안정       │
  │ 12. 디버그: cudaGetLastError() / cuda-memcheck 활용    │
  └───────────────────────────────────────────────────────┘

  ■ 양자화 (INT8) 사용 패턴
    1. FP32 모델 export → ONNX
    2. trtexec --int8 --calib=calib_data.cache
       또는 IInt8EntropyCalibrator2 구현 (직접 calibration)
    3. 검증 데이터로 정확도 측정
    4. 정확도 손실 < 1% 이면 운영 가능
    5. 일부 layer만 INT8 (--precisionConstraints=obey 등으로 hybrid)

  ■ Multi-stream으로 throughput ↑
    Stream A: enqueueV2 → ... → sync
    Stream B: enqueueV2 → ... → sync     (병렬 실행)
    → SM 활용도 ↑. 단, 메모리 사용량은 stream 수만큼.
)";
    cout << endl;
}


// =============================================================================
//  레슨 6 — OpenVINO (Intel)
// =============================================================================

void lesson6_openvino() {
    cout << "[레슨 6] OpenVINO — Intel CPU/iGPU/VPU/NPU\n";
    cout << R"(
  ■ 개요
    Intel Open Visual Inference & Neural Network Optimization.
    Intel CPU(AVX-512, AMX), iGPU(UHD/Arc), VPU(Movidius), NPU(Meteor Lake+).
    오픈소스 (Apache 2.0). GPU/CPU 통합 추론으로 엣지 배포에 강함.

  ■ 변환 흐름
    .onnx → ovc 또는 read_model() → .xml + .bin → 추론

  ■ 코드 스켈레톤 (OpenVINO 2023.x C++ API)
  ─────────────────────────────────────────────────────
  #include <openvino/openvino.hpp>

  int main() {
      ov::Core core;

      // 1) 사용 가능한 디바이스 확인
      auto devs = core.get_available_devices();
      // "CPU", "GPU", "NPU", "AUTO", "MULTI:GPU,CPU", "HETERO:GPU,CPU"

      // 2) 모델 로드 (메모리 함정 ①)
      auto model = core.read_model("model.xml");

      // 3) 전처리 그래프에 통합 (성능 ★)
      ov::preprocess::PrePostProcessor ppp(model);
      ppp.input().tensor()
          .set_element_type(ov::element::u8)
          .set_layout("NHWC")
          .set_color_format(ov::preprocess::ColorFormat::BGR);
      ppp.input().preprocess()
          .convert_element_type(ov::element::f32)
          .mean({103.939, 116.779, 123.68})  // BGR mean
          .convert_layout("NCHW");
      model = ppp.build();
      // ↑ 이렇게 하면 추론 호출 한 번에 전처리 + 추론 + 후처리

      // 4) Compile (메모리 함정 ②)
      // 디바이스에 맞춰 그래프 최적화 / 커널 선택. 한 번만 수행.
      auto compiled = core.compile_model(model, "GPU", ov::AnyMap{
          {ov::hint::performance_mode.name(),
           ov::hint::PerformanceMode::THROUGHPUT},
          {ov::cache_dir.name(), "./ov_cache"}
      });

      // 5) Infer Request (메모리 함정 ③)
      auto req = compiled.create_infer_request();

      // 6) 입력 데이터 - 외부 버퍼 zero-copy 가능
      std::vector<uint8_t> img_bgr(640 * 640 * 3);
      // ... fill from camera ...

      ov::Tensor input_t(ov::element::u8, {1, 640, 640, 3}, img_bgr.data());
      req.set_input_tensor(input_t);

      // 7) 추론 (동기)
      req.infer();
      // 비동기: req.start_async(); req.wait();

      // 8) 결과
      auto output = req.get_output_tensor();
      const float* out_data = output.data<const float>();
      auto shape = output.get_shape();
      // ... post process ...
  }
  ─────────────────────────────────────────────────────

  ■ 디바이스 hint (간편 모드)
    "AUTO"     - 런타임이 가장 적합한 디바이스 자동 선택
    "MULTI:GPU,CPU"
               - 여러 디바이스에 요청 분산 (load balancing)
    "HETERO:GPU,CPU"
               - 모델 일부는 GPU, 일부는 CPU (지원되는 op 따라)

  ■ 성능 hint
    PerformanceMode::LATENCY    - 단일 추론 빠르게
    PerformanceMode::THROUGHPUT - 많은 동시 요청 처리
    PerformanceMode::CUMULATIVE_THROUGHPUT - 모든 디바이스 합산

  ┌─ OpenVINO 메모리 함정 ────────────────────────────────┐
  │ 1. Core는 프로세스 1개 권장 (캐시 공유)                │
  │ 2. compile_model은 비싸므로 1회만. cache_dir로 디스크  │
  │    캐시하여 재시작 시 빠름                             │
  │ 3. 입력 텐서를 외부 버퍼로 만들면 zero-copy            │
  │    수명: req.infer() 끝날 때까지 살아있어야 함         │
  │ 4. CPU 추론 시 NUMA - 큰 모델은 메모리 노드 binding    │
  │    numactl 또는 ov::hint::scheduling_core_type        │
  │ 5. iGPU - host 메모리 공유 (CPU와 같은 RAM)            │
  │    → H2D 복사 비용 거의 없음 (DDR 대역폭만)            │
  │ 6. NPU (Intel Core Ultra) - 별도 메모리 공간           │
  │    데이터 복사 필요. 작은 모델일수록 유리              │
  │ 7. 비동기 큐 - InferRequest 여러 개로 파이프라이닝     │
  │    cpu와 gpu 동시 활용                                 │
  │ 8. 입력 layout (NHWC vs NCHW) - 모델과 일치 안 하면     │
  │    OpenVINO가 자동 변환 (느림). PrePostProcessor로 통합│
  │ 9. ov::Tensor 복사 vs 참조 - 명시적                    │
  │ 10. NUC / 엣지 디바이스에서 메모리 부족 - 모델 양자화  │
  │     POT (Post-training Optimization) / NNCF로 INT8     │
  └───────────────────────────────────────────────────────┘
)";
    cout << endl;
}


// =============================================================================
//  레슨 7 — 런타임 선택 가이드
// =============================================================================

void lesson7_runtime_selection() {
    cout << "[레슨 7] 런타임 선택 가이드\n";
    cout << R"(
  ┌─ 의사결정 트리 ───────────────────────────────────────┐
  │                                                       │
  │  Q1. 어떤 하드웨어에서 돌리나?                        │
  │      ├─ NVIDIA GPU 전용 ────▶ TensorRT (성능 최강)    │
  │      ├─ Intel CPU/iGPU/NPU ─▶ OpenVINO              │
  │      ├─ Apple Silicon ──────▶ Core ML / ORT(CoreML EP) │
  │      ├─ Mobile (ARM) ──────▶ TFLite / NCNN / MNN     │
  │      ├─ 다양한 환경 ───────▶ ONNX Runtime           │
  │      └─ PyTorch 학습 그대로 ▶ LibTorch               │
  │                                                       │
  │  Q2. 모델을 자주 바꾸나?                              │
  │      ├─ 자주 (실험 단계) ──▶ LibTorch / ORT          │
  │      └─ 안정적 ────────────▶ TRT/OV (빌드 시간 OK)    │
  │                                                       │
  │  Q3. 양자화 / 정확도 trade-off 시간 있나?             │
  │      ├─ 충분 ───────────────▶ TRT INT8 / OV INT8     │
  │      └─ 부족 ───────────────▶ FP16 또는 FP32          │
  │                                                       │
  │  Q4. 폐쇄망 / 보안?                                   │
  │      └─ 정적 빌드 우선 ────▶ ORT 정적 / OpenVINO     │
  └───────────────────────────────────────────────────────┘

  ■ 성능 일반화 비교 (대표 모델 기준, 환경 따라 ±50%)
    ResNet-50 batch=1, NVIDIA T4 GPU:
      LibTorch FP32     : 5~7 ms
      ORT CUDA FP32     : 3~5 ms
      ORT TRT EP FP16   : 1.5~2 ms
      TensorRT FP16 직접 : 1.0~1.5 ms
      TensorRT INT8     : 0.6~1.0 ms

    YOLOv8n batch=1, Intel i7-12700:
      ORT CPU FP32      : 50~60 ms
      OpenVINO CPU FP32 : 25~35 ms
      OpenVINO INT8     : 15~25 ms

  ■ 라이선스 / 배포
    LibTorch  : BSD-3 (자유)
    ONNX RT   : MIT (자유)
    TensorRT  : NVIDIA EULA (NVIDIA 하드웨어 한정)
    OpenVINO  : Apache 2.0 (자유)
    실무: 라이선스 확인 + redistribution 정책 점검

  ■ 멀티 백엔드 추상화 패턴
    interface IInferenceEngine {
        virtual void load(string path) = 0;
        virtual Tensor infer(Tensor input) = 0;
    };
    LibTorchEngine : IInferenceEngine { ... };
    OnnxEngine     : IInferenceEngine { ... };
    TrtEngine      : IInferenceEngine { ... };
    OvEngine       : IInferenceEngine { ... };
    → 런타임 교체가 용이. A/B 테스트 / fallback 가능.
)";
    cout << endl;
}


// =============================================================================
//  레슨 8 — 메모리 함정 종합 (이번 챕터의 핵심)
// =============================================================================

void lesson8_memory_pitfalls() {
    cout << "[레슨 8] ML 추론 메모리 함정 종합\n";
    cout << R"(
  ┌─ 1. GPU 메모리 모델 이해 ─────────────────────────────┐
  │                                                       │
  │   호스트 RAM (CPU)                  GPU VRAM         │
  │   ┌─────────────┐    PCIe         ┌─────────────┐    │
  │   │ pageable    │ ←──── 느림 ──→ │ device mem  │    │
  │   │ (일반 malloc)│                │ (cudaMalloc)│    │
  │   ├─────────────┤                 │             │    │
  │   │ pinned      │ ←──── DMA ───→ │             │    │
  │   │ (cudaMallocHost)              │             │    │
  │   ├─────────────┤                 │             │    │
  │   │ unified     │ ←─── 페이지 ──→ │             │    │
  │   │ (cudaMalloc │   on-demand     │             │    │
  │   │  Managed)   │                 │             │    │
  │   └─────────────┘                 └─────────────┘    │
  │                                                       │
  │   - pageable: 가장 흔함. CPU↔GPU 전송 시 OS가 임시   │
  │     pinned 버퍼 만들어 복사 후 DMA. 2배 비용.        │
  │   - pinned: OS가 페이징 못 하게 잠금. DMA 직접.       │
  │     너무 많이 잡으면 시스템 OOM.                       │
  │   - unified (Managed): 페이지 폴트 시 자동 전송.       │
  │     쉬움. 성능 비결정적.                              │
  └───────────────────────────────────────────────────────┘

  ┌─ 2. 비동기 실행과 동기화 ─────────────────────────────┐
  │                                                       │
  │   잘못된 패턴:                                         │
  │     enqueue_inference(buf);                           │
  │     free(buf);   // ❌ GPU가 아직 쓰는 중!             │
  │                                                       │
  │   올바른 패턴:                                         │
  │     enqueue_inference(buf);                           │
  │     stream.synchronize();   // 또는 event              │
  │     free(buf);   // ✓                                 │
  │                                                       │
  │   고급 패턴 (파이프라인):                              │
  │     Stream0: H2D → infer → D2H → callback             │
  │     Stream1: H2D → infer → D2H → callback   (병렬)    │
  │     스트림별 별도 버퍼. callback에서 free.             │
  └───────────────────────────────────────────────────────┘

  ┌─ 3. Allocator 전략 ───────────────────────────────────┐
  │                                                       │
  │   추론 루프에서 cudaMalloc/cudaFree 직접 호출 = 재앙   │
  │     - cudaMalloc은 GPU context lock → ms 단위 지연    │
  │     - 단편화 누적                                      │
  │                                                       │
  │   해법:                                               │
  │   (a) Arena: 큰 청크 한 번 잡고 부분 분배 (ORT 기본)   │
  │   (b) Pool: 고정 크기 버퍼 풀 (TRT IGpuAsyncAllocator)│
  │   (c) Caching: cudaMallocAsync (CUDA 11.2+)           │
  │                                                       │
  │   가장 흔한 실수: 추론마다 입출력 텐서 재할당          │
  │   → 한 번 큰 사이즈로 잡고 reshape만                   │
  └───────────────────────────────────────────────────────┘

  ┌─ 4. 동적 입력 / 가변 배치 ────────────────────────────┐
  │                                                       │
  │   동적 batch size = 매 추론마다 메모리 요구량 변경     │
  │     → allocator가 bestFit 못 하고 단편화                │
  │   해법:                                               │
  │     (a) batch를 N개의 고정값으로 한정 (1, 4, 16, 32)   │
  │     (b) 큰 max로 미리 잡고 부분만 사용                  │
  │     (c) TRT optimization profile - 여러 shape 별 빌드  │
  │                                                       │
  │   비용 분석:                                           │
  │     batch=1 latency 5ms, batch=8 latency 8ms          │
  │     → batch=8이 throughput 5배 + 메모리 효율 좋음     │
  │     단, 첫 요청 7ms 대기 후 7개 더 모아야 → 지연 ↑     │
  │     → SLA에 따라 dynamic batching 윈도우 조정          │
  └───────────────────────────────────────────────────────┘

  ┌─ 5. Tensor 생성/복사 비용 ────────────────────────────┐
  │                                                       │
  │   잘못: float* h = new float[N]; memcpy from raw;     │
  │         cudaMemcpy(d, h, ...);                        │
  │         delete[] h;                                   │
  │                                                       │
  │   더 좋음: pinned memory + async copy + stream         │
  │                                                       │
  │   가장 좋음: GPU에서 직접 입력 생성 (예: NVDEC 비디오 │
  │              디코딩 → GPU buffer → 추론). H2D 0번      │
  │                                                       │
  │   "Zero-copy" 라는 단어 함정:                         │
  │     - 실제로 0 bytes 복사가 아니라 "추가" 복사 0       │
  │     - 카메라 → 추론 파이프라인은 결국 어딘가 복사      │
  │     - 측정: nvprof / Nsight으로 cudaMemcpy 횟수 확인   │
  └───────────────────────────────────────────────────────┘

  ┌─ 6. Multi-thread / Multi-instance ────────────────────┐
  │                                                       │
  │   1) 같은 모델, 여러 스레드, 동시 추론                 │
  │      LibTorch: 모델 to(device) 후 공유 OK (read-only)  │
  │      ORT: Session 스레드 안전. 단, IoBinding은 스레드별│
  │      TRT: 1 engine + N IExecutionContext + N stream    │
  │      OV: 1 compiled_model + N infer_request           │
  │                                                       │
  │   2) 다른 모델 동시 (GPU에서)                          │
  │      → MPS (Multi-Process Service)로 GPU 시간 분할     │
  │      → 또는 모델별 stream 분리                          │
  │                                                       │
  │   메모리: 모델 weight는 1번 로드, context/state는       │
  │           스레드별 독립. weight 복제 안 하도록 주의.    │
  └───────────────────────────────────────────────────────┘

  ┌─ 7. 양자화 메모리 영향 ───────────────────────────────┐
  │                                                       │
  │   FP32 → FP16: weight 절반, 메모리 대역폭 2배 효과     │
  │   FP32 → INT8: weight 1/4, 연산 4배 빠를 수 있음        │
  │                                                       │
  │   주의:                                               │
  │     - calibration 데이터의 분포 = 운영 분포 일치       │
  │     - 일부 layer는 양자화 손실 큼 → mixed precision    │
  │     - INT8 calibrator 구현 시 실제 데이터 흐름 그대로  │
  │     - 정확도 평가 데이터셋 별도 필수                    │
  │                                                       │
  │   메모리 함정:                                         │
  │     calibration 중에는 메모리 사용량 폭증 (FP32 +       │
  │     히스토그램). 배포보다 큰 GPU 필요할 수 있음.        │
  └───────────────────────────────────────────────────────┘

  ┌─ 8. 첫 추론 (warmup) 함정 ───────────────────────────┐
  │                                                       │
  │   첫 추론은 평소 대비 10~100배 느림. 이유:             │
  │     - cuDNN 알고리즘 검색 (ORT/LibTorch)               │
  │     - JIT 컴파일                                       │
  │     - GPU clock idle 상태에서 부스트                    │
  │     - 메모리 패턴 학습                                  │
  │                                                       │
  │   대응:                                               │
  │     - 서버 시작 시 더미 추론 N회 (대표 batch / shape)  │
  │     - SLA 측정은 warmup 후                             │
  │     - 자동 스케일링은 warmup 시간 고려                  │
  └───────────────────────────────────────────────────────┘

  ┌─ 9. 모델 / 메타 보안 ─────────────────────────────────┐
  │                                                       │
  │   - 모델 파일 무결성 (SHA256, 서명)                     │
  │     공급망 공격: 모델에 백도어 주입 → 특정 입력에       │
  │     misclassify (모델 backdoor)                       │
  │   - 입력 검증: shape / range / NaN                     │
  │   - 출력 sanitize: confidence threshold, 이상치 거부    │
  │   - Adversarial input: tiny perturbation으로 오작동     │
  │     실시간 시스템은 입력 source 신뢰성 검증            │
  └───────────────────────────────────────────────────────┘

  ┌─ 10. 메모리 누수 디버깅 ──────────────────────────────┐
  │                                                       │
  │   GPU memory leak는 valgrind로 못 잡음 (호스트만)      │
  │   - cuda-memcheck (deprecated) / compute-sanitizer    │
  │   - nvidia-smi로 실시간 RSS 추적                       │
  │   - PyTorch: torch.cuda.memory_summary()               │
  │   - TRT: context별 reportToProfiler                    │
  │   - ORT: GetMemoryUsage / GetCurrentGpuDeviceMemory   │
  │                                                       │
  │   호스트 측 누수 (input buffer 등):                    │
  │   - ASan / valgrind 일반적                            │
  │   - jemalloc heap profiling으로 핫스팟 확인            │
  └───────────────────────────────────────────────────────┘
)";
    cout << endl;
}


// =============================================================================
//  레슨 9 — 운영 배포 패턴
// =============================================================================

void lesson9_production_patterns() {
    cout << "[레슨 9] 운영 배포 패턴\n";
    cout << R"(
  ┌─ 1. 모델 서빙 아키텍처 ───────────────────────────────┐
  │                                                       │
  │   [REST/gRPC]                                         │
  │   Client ─→ HTTP server ─→ inference queue ─→        │
  │                              (dynamic batching)       │
  │                              ↓                         │
  │                            GPU worker pool             │
  │                              ↓                         │
  │                            response queue ─→ Client    │
  │                                                       │
  │   ★ 핵심 컴포넌트                                     │
  │     - HTTP/gRPC 프론트엔드 (ch34 활용)                 │
  │     - 요청 큐 + dynamic batching                       │
  │     - GPU 워커 (n=GPU 수 또는 stream 수)               │
  │     - 메트릭 / 트레이싱 / 로깅                          │
  │                                                       │
  │   참고: NVIDIA Triton, TorchServe, KServe              │
  │         → 직접 만들지 말고 표준 서버 사용 고려         │
  └───────────────────────────────────────────────────────┘

  ┌─ 2. Dynamic Batching ─────────────────────────────────┐
  │                                                       │
  │   목표: latency 비용 적게 + throughput ↑              │
  │                                                       │
  │   알고리즘 (단순):                                     │
  │     while (running):                                   │
  │       batch = []                                       │
  │       deadline = now() + max_latency                   │
  │       while (now() < deadline and batch.size < N):     │
  │         req = queue.pop(timeout = deadline - now())    │
  │         if req: batch.append(req)                      │
  │       infer(batch)                                     │
  │       respond_each(batch)                              │
  │                                                       │
  │   파라미터:                                           │
  │     N        - 최대 배치 크기 (GPU 메모리 한계)         │
  │     max_lat  - 첫 요청부터 추론 시작까지 최대 대기      │
  │     보통 N=8~32, max_lat=5~50ms                        │
  └───────────────────────────────────────────────────────┘

  ┌─ 3. Health Check / Readiness ─────────────────────────┐
  │                                                       │
  │   /healthz (liveness)                                 │
  │     - 프로세스 살아있나? 단순 200 OK                   │
  │                                                       │
  │   /ready (readiness)                                  │
  │     - 모델 로드 완료?                                  │
  │     - Warmup 완료?                                     │
  │     - GPU 메모리 충분?                                  │
  │     - 외부 의존성(스토리지 등) 정상?                    │
  │     → Kubernetes는 ready 안 되면 traffic 안 보냄        │
  │                                                       │
  │   더미 추론 검증 - 시작 시 1회                          │
  │     예상 출력 검증 → 모델 무결성 보증                    │
  └───────────────────────────────────────────────────────┘

  ┌─ 4. 스로틀 / 백프레셔 ────────────────────────────────┐
  │                                                       │
  │   요청이 GPU 처리량 넘으면?                            │
  │   (a) 큐 무한 누적 → OOM                                │
  │   (b) 큐 max 초과 시 503 즉시 반환                       │
  │   (c) 적응적: 큐 깊이로 latency 증가 → SLA breach 사전 │
  │                                                       │
  │   추가 방어선:                                         │
  │     - 입력 크기 제한 (이미지 max 4096x4096 등)          │
  │     - 요청별 timeout                                   │
  │     - circuit breaker (다운스트림 장애 시 fast fail)    │
  └───────────────────────────────────────────────────────┘

  ┌─ 5. 메트릭 / SLI ─────────────────────────────────────┐
  │                                                       │
  │   추론 metric                                          │
  │     - 지연: p50/p95/p99 (히스토그램)                    │
  │     - 처리량: req/sec, throughput                       │
  │     - 큐 깊이                                           │
  │     - GPU 활용도 (DCGM / nvidia-smi exporter)           │
  │     - 모델 정확도 drift (요청 sample vs ground truth)   │
  │     - 오류율: model error / out-of-range / timeout      │
  │                                                       │
  │   주요 운영 alarm                                       │
  │     - p99 latency > SLA                                │
  │     - GPU memory > 90%                                  │
  │     - inference success rate < 99.9%                   │
  │     - 모델 confidence 분포 이상치 (drift 신호)          │
  └───────────────────────────────────────────────────────┘

  ┌─ 6. A/B 테스트 / Canary 배포 ─────────────────────────┐
  │                                                       │
  │   - 새 모델은 트래픽 1% → 5% → 20% → 100% 점진 확대     │
  │   - 정확도 / 지연 / 비즈니스 메트릭 비교                  │
  │   - 자동 rollback - 회귀 감지 시 즉시 이전 모델          │
  │                                                       │
  │   기술적으로는 같은 서버 안에 두 모델 동시 로드,         │
  │   요청별 hash로 버전 라우팅. GPU 메모리 2배 필요.         │
  └───────────────────────────────────────────────────────┘

  ┌─ 7. Docker로 패키징 (ch36 연계) ─────────────────────┐
  │                                                       │
  │   FROM nvidia/cuda:12.2-cudnn8-runtime-ubuntu22.04    │
  │   COPY libtorch /opt/libtorch                          │
  │   COPY model.pt /app/model.pt                          │
  │   COPY app /usr/local/bin/app                          │
  │   ENTRYPOINT ["/usr/local/bin/app"]                    │
  │                                                       │
  │   주의:                                               │
  │     - cuda runtime / cuDNN / driver 호환 매트릭스       │
  │     - GPU 컨테이너: --gpus all + nvidia-container-toolkit│
  │     - 모델 파일은 image 내장 vs volume mount 선택        │
  │       (자주 바꾸면 mount, 안전성은 내장)                  │
  │     - 메모리 제한 vs GPU 추론 - cgroup CPU/RAM 한계      │
  │       GPU 메모리는 cgroup으로 직접 제한 안 됨           │
  │       → MIG (Multi-Instance GPU, A100+) 활용            │
  └───────────────────────────────────────────────────────┘
)";
    cout << endl;
}


// =============================================================================
//  연습문제
// =============================================================================
//
//  [연습 1] PyTorch 모델 export → ONNX → ORT 추론
//    파이썬에서 ResNet18 학습된 가중치 로드 → torch.onnx.export
//    C++에서 onnxruntime으로 동일 입력에 대해 출력 일치 검증.
//    atol=1e-4 이내인지 확인.
//
//  [연습 2] LibTorch와 ORT 동일 모델 latency 비교
//    1000회 추론 평균 / p99 / p999 측정. warmup 100회 후 측정.
//    pinned vs pageable 메모리 차이도 측정.
//
//  [연습 3] TensorRT 엔진 빌드 + INT8 양자화
//    trtexec로 FP16 / INT8 엔진 두 개 빌드.
//    100장 검증셋으로 정확도 손실 측정.
//
//  [연습 4] OpenVINO PrePostProcessor로 전처리 통합
//    BGR uint8 입력 → 모델은 NCHW float. 전처리를 그래프에 통합.
//    이전(외부 OpenCV 전처리)과 비교하여 latency 차이 측정.
//
//  [연습 5] 추론 서버 (간단)
//    ch34의 TCP 서버 + ORT를 결합. 길이 prefix로 이미지 받기 →
//    추론 → JSON 결과. 동시 4 연결 처리.
//
//  [연습 6] Dynamic batching 구현
//    50ms 윈도우 또는 batch=16 도달 시 추론 트리거.
//    부하 부하시뮬레이터 (req 200/sec)로 throughput / latency 측정.
//
//  [연습 7] GPU memory leak 시뮬레이션
//    의도적으로 cudaMalloc만 하고 cudaFree 누락 → nvidia-smi로 RSS 증가 관찰.
//    compute-sanitizer로 검출.
//
//  [연습 8] 다중 백엔드 추상화
//    interface IInferenceEngine 정의 후 ORT / LibTorch 구현.
//    런타임 환경변수로 백엔드 선택. fallback 정책.
//
//  [연습 9] 모델 핫스왑
//    운영 중 모델 파일 변경 감지 → atomic shared_ptr<Engine> 교체.
//    in-flight 요청은 이전 모델로 완료. 새 요청은 새 모델로.
//
//  [연습 10] Docker GPU 이미지
//    위 추론 서버를 nvidia/cuda 베이스로 패키징. 멀티스테이지로
//    최종 이미지 < 1GB 목표. healthcheck 추가.
// =============================================================================
