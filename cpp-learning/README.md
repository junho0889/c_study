# C++ 프로그래밍 학습 가이드

초보자부터 전문가까지, **36단계**로 배우는 C++ 프로그래밍 종합 교재입니다.
모든 코드에 한글 주석, 비유, ASCII 그림, 실전 예제, 연습문제가 포함되어 있습니다.

> **메모리 관리 횡단 가이드**: [`MEMORY_GUIDE.md`](MEMORY_GUIDE.md)
> 각 챕터별 메모리 함정 / 발현 / 회피 방법을 한 눈에 보는 체크리스트.
> 사이드 by 사이드로 펴두고 챕터를 학습하면 실무에서 만날 함정의 80%는 사전 예방.

## 커리큘럼

### PART 1 — 기초 (01~04)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 01 | 기초의 기초 | 변수, 자료형, 입출력, 연산자, 형변환, 수학함수 |
| 02 | 제어문 | if/else, switch, for, while, break/continue, 실전연습 |
| 03 | 함수 | 선언, 매개변수 전달방식, 오버로딩, 재귀, 람다 |
| 04 | 배열/포인터 | 배열, 포인터, 참조, C-string vs string, 동적배열 |

### PART 2 — 객체지향 (05~06)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 05 | OOP 기초 | 클래스, 생성자/소멸자, 접근제어, this, static, 연산자 오버로딩 |
| 06 | 상속/다형성 | 상속, virtual, 다형성, 추상클래스, 인터페이스 |

### PART 3 — 실전 도구 (07~10)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 07 | 템플릿/STL | 함수/클래스 템플릿, vector, map, set, sort, find, count |
| 08 | 메모리 관리 | 스택/힙, unique_ptr, shared_ptr, RAII, move semantics |
| 09 | 파일/예외 | 파일 읽기/쓰기, try/catch, 사용자정의 예외, CSV 처리 |
| 10 | 모던 C++ | optional, variant, 구조적바인딩, constexpr if, C++20 미리보기 |

### PART 4 — 도구와 환경 (11~12)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 11 | 디버깅 | 흔한 버그 TOP 10, GDB/VS 사용법, Sanitizer |
| 12 | 프레임워크 | CMake, 프로젝트 구조, 주요 라이브러리, 패키지 관리 |

### PART 5 — 심화 (13~15)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 13 | 디자인 패턴 | 싱글톤, 팩토리, 옵저버, 전략, 빌더, RAII |
| 14 | 멀티스레딩 | thread, mutex, atomic, async/future, 병렬 처리 |
| 15 | 네트워크 | TCP/IP, 소켓, HTTP, 직렬화, REST API, 서버 아키텍처 |

### PART 6 — 배포와 실전 (16~18)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 16 | 테스트/TDD | 미니 테스트 프레임워크 직접 구현, Google Test, TDD 사이클 |
| 17 | 빌드/배포 | CMake 심화, Docker, GitHub Actions CI/CD, 릴리스 체크리스트 |
| 18 | 실전 프로젝트 | TODO 앱 (모든 개념 종합: OOP, 파일IO, 이벤트, STL) |

### PART 7 — 자료구조 & 알고리즘 (19)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 19 | 자료구조/알고리즘 | 연결리스트, 스택/큐, BST, 해시테이블, 정렬(5종), 탐색, Big-O |

### PART 8 — 고급 C++ (20~23)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 20 | 고급 OOP | Rule of 3/5/0, 복사/이동 생성자, CRTP, 가상상속, 타입캐스팅 |
| 21 | 고급 템플릿 | 특수화, SFINAE, 가변인자 템플릿, 컴파일타임 프로그래밍, 메타프로그래밍 |
| 22 | 문자열/정규식 | string 심화, string_view, regex, KMP 알고리즘, CSV/JSON 파서 |
| 23 | 함수형 프로그래밍 | Functor, std::function, bind, 고차함수, 클로저, 파이프라인 패턴 |

### PART 9 — 전문가 영역 (24~28)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 24 | 고급 동시성 | condition_variable, 스레드 풀, shared_mutex, 락프리, 병렬 알고리즘 |
| 25 | 성능 최적화 | 벤치마킹, 캐시 최적화, DoD, 컨테이너 성능, 메모리 풀, 프로파일링 |
| 26 | C++20/23 실전 | Concepts, Ranges, Coroutines, <=>, expected, Modules, span, jthread |
| 27 | 시스템 프로그래밍 | 비트 연산, 비트마스크, 엔디안, 메모리 정렬, volatile, BMP/IP 파싱 |
| 28 | 보안/베스트프랙티스 | 버퍼 오버플로우, 정수 오버플로우, 입력검증, OWASP, Core Guidelines |

### PART 10 — 이벤트/콜백 & 하드웨어 제어 (29~32)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 29 | 이벤트/콜백 | 함수포인터, std::function, C# event 구현, Signal/Slot, OS 시그널, GUI 이벤트 |
| 30 | 하드웨어 제어 | MMIO, 인터럽트(ISR), DMA, GPIO, 타이머/워치독, UART/SPI/I2C |
| 31 | ADC/DAC/센서 | 아날로그 변환, 센서 드라이버, 칼만 필터, 텔레메트리, 날씨 관측소 |
| 32 | RTOS 패턴 | 실시간 OS, 태스크 스케줄링, 세마포어, 메시지 큐, 데드라인, 미니 RTOS |

### PART 11 — 실무 통합 (33~37) — *데이터 포맷 / 네트워크 / 산업 / Docker / ML 추론*
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 33 | 데이터 포맷 | CSV(RFC 4180), JSON 파서 직접 구현, YAML/INI/TOML, UTF-8 BOM, mmap |
| 34 | 네트워크 계층 심화 | OSI/TCP-IP, L2 이더넷/ARP, L3 IP/체크섬, L4 TCP/UDP, **실제 BSD 소켓 cross-platform**, async I/O 모델, TLS |
| 35 | 산업용 프로토콜 | Modbus RTU/TCP (CRC16 직접), CAN/CANopen, OPC UA, EtherCAT/Profinet, MQTT 인코더, EMI/접지/타이밍 |
| 36 | Docker for C++ | 멀티스테이지, distroless/scratch, sanitizer 이미지, multi-arch buildx, cgroup OOM, 컨테이너 디버깅 |
| 37 | ML 추론 런타임 | LibTorch / ONNX Runtime / TensorRT / OpenVINO 비교, GPU 메모리/스트림/pinned, INT8 양자화, dynamic batching, 모델 서빙 |

> Part 11은 "교과서엔 없지만 실무에선 필수"인 영역.
> 산업/임베디드/IIoT 개발자는 30~32와 함께 35단계를 우선 학습.
> 34단계는 ch15(개념)의 실행 가능 코드 보강판.
> 37단계는 P10(ml_inference 프로젝트)와 연계 - 학습은 Python, 추론은 C++ 패턴.

### PART 10 — 실전 프로젝트 (C++ 주요 활용 분야별)

C++이 **실제 산업에서 가장 많이 사용되는 분야**별 정석 프로젝트입니다.
모든 프로젝트에 C# 개발자를 위한 비유와 초등학생도 이해할 수 있는 상세 주석이 포함되어 있습니다.

| # | 프로젝트 | 분야 | C++을 쓰는 이유 |
|---|---------|------|----------------|
| P01 | 고성능 데이터 파이프라인 | **데이터 수집/처리** | GC 없는 실시간 처리, 제로카피 파싱, 캐시 친화적 |
| P02 | 게임 엔진 코어 | **게임 개발** | GC 끊김 없음, 결정적 소멸, ECS 캐시 최적화 |
| P03 | 이미지 처리 엔진 | **컴퓨터 비전** | 직접 메모리 접근, SIMD, 박싱/언박싱 없음 |
| P04 | 금융 트레이딩 시스템 | **고빈도 트레이딩** | 나노초 지연시간, 결정적 타이밍, GC 중단 없음 |
| P05 | 미니 데이터베이스 엔진 | **DB 엔진** | 디스크 I/O 제어, 페이지 메모리 관리, mmap |
| P06 | 미니 언어 인터프리터 | **컴파일러/인터프리터** | 최적화 패스 속도, 메모리 직접 제어 |
| P07 | 오디오 프로세싱 엔진 | **오디오/DAW** | 실시간 보장 지연시간, GC 없는 오디오 콜백 |
| P08 | 고성능 네트워크 서버 | **서버 인프라** | 수백만 연결, 마이크로초 응답, epoll |
| P09 | 2D 물리 엔진 | **물리 시뮬레이션** | 결정적 부동소수점, SIMD, 캐시 친화적 데이터 |
| P10 | 머신러닝 추론 엔진 | **ML/AI** | GPU 인터롭(CUDA), 텐서 메모리 레이아웃 제어 |

```
projects/
├── 01_data_pipeline/      ← 센서 데이터 수집 → 통계 분석 → CSV 리포트
├── 02_game_engine/        ← ECS, 게임 루프, 오브젝트 풀링, 충돌 감지
├── 03_image_processing/   ← BMP 파싱, 필터(블러/엣지), 색공간 변환
├── 04_trading_system/     ← 오더북, 매칭 엔진, 이동평균, 전략 백테스트
├── 05_database_engine/    ← KV스토어, B-Tree, WAL, SQL 파서, 버퍼풀
├── 06_compiler/           ← 렉서 → 파서 → AST → 인터프리터, REPL
├── 07_audio_engine/       ← 파형 생성, 이펙트, ADSR, WAV 출력, 시퀀서
├── 08_network_server/     ← 이벤트 루프, 라우터, 미들웨어, 로드밸런서
├── 09_physics_engine/     ← Vec2, 강체, 충돌감지/응답, 공간분할
└── 10_ml_inference/       ← 행렬연산, 신경망, 역전파, XOR/분류 학습
```

## 빠른 시작

### 방법 1: 개별 파일 컴파일 (가장 간단)
```bash
cd 01_basics
g++ -std=c++17 -Wall -o 01_basics main.cpp
./01_basics
```

### 방법 2: CMake로 전체 빌드
```bash
mkdir build && cd build
cmake ..
cmake --build .
```

### 방법 3: Windows MSVC
```cmd
cd 01_basics
cl /EHsc /std:c++17 /W4 main.cpp
main.exe
```

### 멀티스레딩 단계 (14, 24) 컴파일
```bash
g++ -std=c++17 -Wall -pthread -o 14_thread 14_multithreading/main.cpp
g++ -std=c++17 -Wall -pthread -o 24_concurrency 24_advanced_concurrency/main.cpp
```

### C++20 기능 컴파일 (26단계)
```bash
g++ -std=c++20 -Wall -o 26_cpp20 26_cpp20_23/main.cpp
```

### 네트워크 단계 (34) 컴파일 (cross-platform)
```bash
# Linux / macOS
g++ -std=c++17 -Wall -pthread -O2 -o 34_net 34_network_layers/main.cpp

# Windows MinGW
g++ -std=c++17 -Wall -O2 -o 34_net.exe 34_network_layers/main.cpp -lws2_32

# Windows MSVC
cl /EHsc /std:c++17 /W4 34_network_layers/main.cpp ws2_32.lib
```

### 36단계 Docker 사용 (이미지 빌드)
```bash
cd 36_docker_cpp
# 운영용 멀티스테이지
docker build -f Dockerfile.multistage -t myapp:latest ../..
# Sanitizer (CI 야간)
docker build -f Dockerfile.sanitizer  -t myapp:asan ../..
# 초소형 정적 바이너리
docker build -f Dockerfile.alpine-static -t myapp:tiny ../..
```

## 학습 로드맵

```
[기초]       01 → 02 → 03 → 04
                        ↓
[OOP]        05 → 06
                  ↓
[실전도구]   07 → 08 → 09 → 10
                        ↓
[도구]       11 → 12
                  ↓
[심화]       13 → 14 → 15
                  ↓
[배포]       16 → 17 → 18 (실전 프로젝트!)
                  ↓
[자료구조]   19 (알고리즘 & 자료구조)
                  ↓
[고급C++]    20 → 21 → 22 → 23
                        ↓
[전문가]     24 → 25 → 26 → 27 → 28
                  ↓
[이벤트/HW]  29 → 30 → 31 → 32
                  ↓
[실무 통합]  33 → 34 → 35 → 36 → 37   ← NEW: 데이터/네트워크/산업/Docker/ML추론
```

### 분야별 추천 경로

```
게임 개발자:      01~18 → 19 → 20 → 25 → 29 → 14,24 → 27 → 33,36
백엔드 개발자:    01~18 → 19 → 22 → 24 → 25 → 29 → 28 → 33,34,36 → 37
임베디드 개발자:  01~18 → 19 → 27 → 30 → 31 → 32 → 20 → 24 → 35
IoT 개발자:       01~18 → 27 → 30 → 31 → 32 → 29 → 34,35 → 37
산업 자동화:      01~18 → 14,24 → 27 → 30 → 32 → 35 → 34 → 33,36
DevOps/플랫폼:   01~18 → 12,17 → 14,24 → 25 → 28 → 34 → 36 → 37
ML 추론 엔지니어: 01~18 → 25 → 14,24 → 33 → 34 → 36 → 37 (P10)
면접 준비:        01~18 → 19 → 20 → 21 → 25
C# → C++ 전환:   01~18 → 29 → 20 → 08 → 25 → 33
```

## 학습 팁

- 코드를 직접 타이핑하세요 (복사 붙여넣기 X)
- 주석을 읽고 값을 바꿔가며 실험하세요
- 컴파일 에러가 나면 첫 번째 에러부터 해결하세요
- 모르는 에러 메시지는 그대로 검색하세요
- 각 단계의 연습문제를 반드시 풀어보세요
- 19단계 이후는 순서 상관없이 관심 분야부터 학습 가능

## 필요 환경

- C++17 이상 지원 컴파일러
  - Windows: MinGW-w64 또는 Visual Studio 2019+
  - Linux: GCC 7+ 또는 Clang 5+
  - Mac: Xcode Command Line Tools
- (선택) CMake 3.16 이상
- (26단계) C++20 지원 컴파일러: GCC 10+, Clang 10+, MSVC 19.29+
