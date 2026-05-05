/*
=============================================================================
  C++ 학습 36단계: Docker for C++ (재현 가능 빌드 / 운영 / 디버깅)
=============================================================================
  [학습 목표]
  1. 왜 C++에 Docker가 필요한가 (glibc / ABI / 의존성 지옥)
  2. 멀티 스테이지 Dockerfile - 작은 이미지 / 빠른 CI
  3. distroless / scratch 베이스 - 보안 표면 최소화
  4. Sanitizer 이미지 (ASan/UBSan/TSan) - 자동화된 메모리 검증
  5. 크로스 컴파일 (buildx, ARM/x86, glibc/musl)
  6. 컨테이너 런타임 메모리 / cgroup / OOM
  7. 컨테이너 안에서 디버깅 (gdb, perf, core dump)

  [실무 배경]
    C++ 빌드 환경 = 재현 불가의 늪.
      "내 노트북에선 됩니다" → glibc 2.31 vs 2.17, gcc 9 vs 11.
      → CI 머신에서 빌드된 바이너리가 운영 서버에서 안 돎.
    Docker = 빌드 환경 자체를 코드로 박제.
    하지만 C++의 특수성(컴파일 시간, 정적/동적 링크, 디버그 심볼)이
    "그냥 쓰면 망하는" 함정을 만든다.

  [이 파일의 역할]
    실제 docker 명령은 셸/Dockerfile에서 실행. 이 main.cpp는:
    - 개념 설명
    - Dockerfile 템플릿 (옆 파일 Dockerfile.* 참고)
    - 운영 시나리오
    을 출력하는 가이드.
=============================================================================
*/

#include <iostream>
#include <string>
using namespace std;

void lesson1_why_docker();
void lesson2_multistage();
void lesson3_distroless_scratch();
void lesson4_sanitizer_images();
void lesson5_cross_compile();
void lesson6_runtime_memory();
void lesson7_debugging_in_container();

/*
=============================================================================
  레슨별 출력 (모두 정적 가이드 텍스트, 실제 빌드/실행은 옆 폴더 Dockerfile)
=============================================================================
  lesson1: glibc/ABI/의존성 지옥 설명
  lesson2: 멀티 스테이지 Dockerfile 예시 (50MB 운영 이미지)
  lesson3: distroless / scratch 베이스 비교 표
  lesson4: ASan/UBSan/TSan 옵션 + Sanitizer Dockerfile
  lesson5: buildx / cross-compile / multi-arch
  lesson6: cgroup memory limit, jemalloc, OOM kill
  lesson7: gdb, perf, eBPF, core dump in container

  실제 동작 검증: 옆 폴더 Dockerfile.multistage / sanitizer / alpine-static
  사용법:
    docker build -f Dockerfile.multistage -t myapp:latest ../..
    docker run --rm myapp:latest
=============================================================================
*/

int main() {
    cout << "================================================\n";
    cout << "  C++ 36단계 : Docker for C++\n";
    cout << "================================================\n\n";

    lesson1_why_docker();
    lesson2_multistage();
    lesson3_distroless_scratch();
    lesson4_sanitizer_images();
    lesson5_cross_compile();
    lesson6_runtime_memory();
    lesson7_debugging_in_container();

    cout << "\n36단계 학습 완료!\n";
    return 0;
}


// =============================================================================
//  레슨 1 — 왜 C++에 Docker인가
// =============================================================================

void lesson1_why_docker() {
    cout << "[레슨 1] 왜 C++에 Docker?\n";
    cout << R"(
  ┌─ C++ 배포의 고통 ─────────────────────────────────────┐
  │                                                       │
  │  1) glibc 버전 의존                                   │
  │     Ubuntu 22.04 (glibc 2.35)에서 빌드한 바이너리를   │
  │     CentOS 7 (glibc 2.17)에서 실행 → 즉시 죽음        │
  │       /lib64/libc.so.6: version `GLIBC_2.34' not found│
  │     해결:                                             │
  │       (a) 가장 낮은 OS에서 빌드                       │
  │       (b) musl 정적 링크 (alpine)                     │
  │       (c) 컨테이너로 OS 자체를 운반                   │
  │                                                       │
  │  2) C++ ABI 비호환                                    │
  │     gcc 4.x 와 gcc 5+ 의 std::string ABI가 다름        │
  │     라이브러리 A는 4.x, B는 5+ 빌드 → 링크 실패       │
  │     해결: -D_GLIBCXX_USE_CXX11_ABI=0 또는 통일 빌드   │
  │                                                       │
  │  3) 동적 라이브러리 지옥                              │
  │     libssl 1.1 → 3.0 / libstdc++ → 다른 RPATH         │
  │     "DLL Hell"의 리눅스 버전 = "Dependency Hell"      │
  │                                                       │
  │  4) 빌드 도구 버전                                    │
  │     CMake 3.16 vs 3.25, ninja 버전, ld vs lld          │
  │     CI마다 결과 미묘하게 다름                          │
  │                                                       │
  │  5) 비공개 SDK (NVIDIA, Intel oneAPI, MKL)            │
  │     설치 절차 100줄짜리 매뉴얼 → 신규 개발자 1주일 손실│
  │                                                       │
  │  6) 시스템 패키지가 너무 오래된 OS                    │
  │     CentOS 7 default gcc=4.8 (C++17 안 됨)            │
  │     devtoolset / SCL로 우회하지만 환경 변수 헬                │
  └───────────────────────────────────────────────────────┘

  ■ Docker가 해결하는 것
    ✓ 빌드 환경 자체를 Dockerfile로 코드화 (PR 리뷰 가능)
    ✓ "내 노트북" / CI / 운영 모두 동일 이미지
    ✓ 새 개발자 onboarding: docker pull + docker run = 끝
    ✓ Multi-arch (x86/ARM) 빌드를 buildx로 한 명령
    ✓ 실험: 5개 컴파일러 버전 동시 테스트 (병렬)

  ■ Docker가 해결 못 하는 것 (착각 주의)
    ✗ 성능 - 컨테이너는 OS 격리지 가상화가 아니지만,
      네트워크/스토리지 드라이버에 따라 지연 추가 가능
    ✗ 보안 - 컨테이너 탈출 취약점 존재. root로 실행 X
    ✗ 코드 품질 - 똥 코드는 컨테이너 안에서도 똥
    ✗ Windows 네이티브 - WSL 또는 Windows 컨테이너 별개 세계
)";
    cout << endl;
}


// =============================================================================
//  레슨 2 — 멀티 스테이지 Dockerfile (필수 패턴)
// =============================================================================

void lesson2_multistage() {
    cout << "[레슨 2] 멀티 스테이지 Dockerfile\n";
    cout << R"(
  ■ 단일 스테이지의 문제
    FROM ubuntu:22.04
    RUN apt install -y g++ cmake git ...    # 빌드 도구 (~500MB)
    COPY . /src
    RUN cmake --build /src
    CMD ["/src/build/myapp"]
    → 운영 이미지에 빌드 도구 다 포함. 1GB+. 보안 표면 큼.

  ■ 멀티 스테이지 정답 (옆 파일 Dockerfile.multistage 참고)
  ─────────────────────────────────────────────────────
  # ===== Stage 1: Builder =====
  FROM ubuntu:22.04 AS builder
  RUN apt-get update && apt-get install -y --no-install-recommends \
        g++ cmake ninja-build git ca-certificates \
        && rm -rf /var/lib/apt/lists/*
  WORKDIR /src
  # 의존성 먼저 복사 (캐시 최적화)
  COPY CMakeLists.txt vcpkg.json /src/
  RUN cmake -GNinja -B build -DCMAKE_BUILD_TYPE=Release
  # 소스 복사 후 빌드 (이전 레이어 캐시 활용)
  COPY src/ /src/src/
  RUN cmake --build build --parallel

  # ===== Stage 2: Runtime =====
  FROM ubuntu:22.04
  RUN apt-get update && apt-get install -y --no-install-recommends \
        libstdc++6 ca-certificates \
        && rm -rf /var/lib/apt/lists/*
  COPY --from=builder /src/build/myapp /usr/local/bin/myapp
  USER 65532:65532   # nonroot
  ENTRYPOINT ["/usr/local/bin/myapp"]
  ─────────────────────────────────────────────────────
  → builder 약 1GB, runtime 약 80MB. 보안 표면도 작음.

  ■ 캐시 활용 전략
    1) 의존성만 따로 가져와 의존성 단계 캐시
       COPY package.json / vcpkg.json / Cargo.toml 먼저
       RUN install_deps
       그 다음 COPY 소스
    2) ARG / ENV로 컴파일러 버전 고정 (재현성)
    3) buildkit 캐시 마운트
       RUN --mount=type=cache,target=/var/cache/apt apt-get install ...
       RUN --mount=type=cache,target=/root/.ccache cmake --build ...

  ■ ccache로 재빌드 가속
    builder 안에 ccache 설치 / CCACHE_DIR을 cache mount.
    → 같은 코드 재빌드 시 1초. CI 시간 50% 절감 자주 봄.

  ■ Dockerfile 안티패턴
    ✗ ADD 대신 COPY. ADD는 URL/tar 자동 풀기로 의외성 큼
    ✗ root 사용자로 ENTRYPOINT 실행
    ✗ apt-get install 후 rm -rf /var/lib/apt/lists/* 누락
    ✗ COPY . /src - .dockerignore 없으면 .git까지 다 들어감
    ✗ CMD에서 셸 형식 사용 ("./app") - PID 1 시그널 처리 망함
       → exec 형식 ["app", "arg1"] 권장
    ✗ HEALTHCHECK 누락 → orchestrator가 죽은 컨테이너 감지 못함
)";
    cout << endl;
}


// =============================================================================
//  레슨 3 — distroless / scratch 베이스
// =============================================================================

void lesson3_distroless_scratch() {
    cout << "[레슨 3] distroless / scratch 베이스 이미지\n";
    cout << R"(
  ■ 베이스 이미지 비교
  ┌──────────────┬─────────┬───────────┬─────────────────┐
  │ 베이스        │ 크기    │ 셸 / 도구 │ 용도            │
  ├──────────────┼─────────┼───────────┼─────────────────┤
  │ ubuntu:22.04 │ 80MB    │ 다 있음   │ 디버깅 편리      │
  │ debian:slim  │ 30MB    │ 기본만    │ 표준              │
  │ alpine       │ 7MB     │ busybox   │ 작지만 musl libc│
  │ distroless   │ 20MB    │ 없음      │ 보안/운영 권장  │
  │ scratch      │ 0MB     │ 없음      │ 정적 링크 only  │
  └──────────────┴─────────┴───────────┴─────────────────┘

  ■ Alpine (musl)의 함정
    musl libc != glibc.
    glibc 가정한 코드 / 라이브러리 깨질 수 있음:
      - DNS 해석 동작 다름 (특히 멀티 A 레코드)
      - getaddrinfo, regex 일부 다름
      - tcmalloc / jemalloc 일부 패치 필요
      - 스택 사이즈 기본 작음 (80KB) → recursion 깊은 코드 segfault
    이점:
      - 정적 링크 깔끔
      - 이미지 작음 (CDN 비용 절감)
      - 보안 패치 빠름
    선택 기준: 단순 서버 = alpine, 복잡 의존 = debian/ubuntu slim

  ■ distroless (Google) - 최선의 운영 이미지
    https://github.com/GoogleContainerTools/distroless
    구성: 최소 시스템 라이브러리 + ca-certificates + tzdata + nonroot 사용자.
    셸 없음 → 컨테이너 침투해도 명령 실행 어려움.
    종류:
      gcr.io/distroless/static       : 정적 링크 바이너리 (5MB)
      gcr.io/distroless/cc           : libc/libstdc++ 포함 (20MB)
      gcr.io/distroless/cc:debug     : busybox 포함 (디버깅용)

  ■ scratch (완전 비어있음)
    FROM scratch
    COPY myapp /myapp
    ENTRYPOINT ["/myapp"]

    조건:
      - 정적 링크 (-static)
      - musl 또는 glibc 정적 (license 주의 - LGPL)
      - DNS / TLS 인증서 직접 포함
      - timezone 데이터 직접 포함
    이미지 크기 = 바이너리 크기 그대로 (수 MB).

  ■ 보안 측면
    "셸 없음" = "exec /bin/sh 못 함" = 침투 후 도구 다운로드 어려움.
    하지만 만능 아님:
      - 라이브러리 취약점은 그대로
      - 코드 인젝션은 동일하게 가능
      - 단, post-exploitation 도구 사용은 어려워짐 (실제 큰 차이)

  ■ 메모리 측면
    distroless / scratch는 OS 레벨 캐시 / tmpfs / /proc 정보 제공.
    cgroup memory.limit_in_bytes를 컨테이너가 인식하려면:
      - C++14 std::thread::hardware_concurrency()는 host CPU 반환 (잘못)
      - 직접 /sys/fs/cgroup/cpu.max 읽거나 sched_getaffinity() 사용
    JeMalloc / tcmalloc는 컨테이너 메모리 인식 옵션 있음.
)";
    cout << endl;
}


// =============================================================================
//  레슨 4 — Sanitizer 이미지 (자동화된 메모리 / 동시성 검증)
// =============================================================================

void lesson4_sanitizer_images() {
    cout << "[레슨 4] Sanitizer 이미지로 자동 검증\n";
    cout << R"(
  ■ Sanitizer 종류
    ASan  (-fsanitize=address)        : use-after-free, heap overflow, leak
    UBSan (-fsanitize=undefined)      : 정수 오버플로, null deref, alignment
    TSan  (-fsanitize=thread)         : 데이터 레이스
    MSan  (-fsanitize=memory)         : 미초기화 읽기 (clang 전용)
    LSan  (-fsanitize=leak)           : 메모리 누수
    CFI   (-fsanitize=cfi)            : 제어 흐름 무결성

  ■ 권장 조합
    개발 빌드: ASan + UBSan (빠르고 자주 잡힘)
    야간 CI : ASan + UBSan / 별도 잡: TSan / 별도 잡: MSan
    릴리즈   : 모두 끔. -fstack-protector-strong 정도만

  ■ Dockerfile 패턴 - sanitizer 전용 stage
  ─────────────────────────────────────────────────────
  FROM ubuntu:22.04 AS sanitizer
  RUN apt-get update && apt-get install -y --no-install-recommends \
        clang lld cmake ninja-build libc++-dev libc++abi-dev
  WORKDIR /src
  COPY . /src
  RUN cmake -GNinja -B build-asan \
        -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ \
        -DCMAKE_BUILD_TYPE=RelWithDebInfo \
        -DCMAKE_CXX_FLAGS="-fsanitize=address,undefined -fno-omit-frame-pointer"
  RUN cmake --build build-asan --parallel
  ENV ASAN_OPTIONS=detect_leaks=1:halt_on_error=1:abort_on_error=1
  ENV UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1
  CMD ["/src/build-asan/tests"]
  ─────────────────────────────────────────────────────

  ■ 메모리 / 성능 영향
    ASan : 메모리 2~3배, 속도 2배 느림
    UBSan: 미미 (5~10% 느림)
    TSan : 메모리 5~10배, 속도 5~15배 느림
    → 운영에선 절대 켜지 않음. CI / nightly 전용.

  ■ Sanitizer가 잡지 못하는 것 (오해 주의)
    - 모든 코드 경로를 실행해야 잡음 (커버리지의 함수)
    - 컴파일러 최적화로 사라진 UB는 못 잡음
    - 하드웨어 레지스터 / DMA 영역은 모름 (volatile 영역)
    → 정적 분석 (clang-tidy, cppcheck, PVS-Studio) 병행 필수

  ■ 컨테이너 + Sanitizer 의 함정
    1) 컨테이너 메모리 제한 < ASan 사용량 → OOM 즉시 죽음
       → docker run --memory=8g 등으로 큼지막하게
    2) seccomp 프로파일이 ptrace 차단 → ASan 일부 기능 불가
       → --security-opt seccomp=unconfined (개발 환경만)
    3) 코어 덤프 활성화: ulimit -c unlimited + /proc/sys/kernel/core_pattern
       → docker run --ulimit core=-1
    4) 심볼화: 빌드 이미지의 .debug_info 필요. release 이미지에선 망함.
       → 별도 sanitizer 이미지 유지
)";
    cout << endl;
}


// =============================================================================
//  레슨 5 — 크로스 컴파일 (multi-arch)
// =============================================================================

void lesson5_cross_compile() {
    cout << "[레슨 5] 크로스 컴파일 / multi-arch 빌드\n";
    cout << R"(
  ■ 시나리오
    - ARM64 서버 / Graviton / Apple Silicon에 배포
    - 임베디드 (Raspberry Pi, NVIDIA Jetson)
    - 사내 x86 빌드머신 → 다 만들어주기

  ■ buildx + QEMU (가장 단순)
    docker buildx create --use
    docker buildx build --platform linux/amd64,linux/arm64 \
                        -t myapp:latest --push .
    → QEMU emulation으로 ARM 빌드. 느리지만 동작.

  ■ Cross-compiler toolchain (빠름)
    FROM --platform=$BUILDPLATFORM ubuntu:22.04 AS builder
    ARG TARGETARCH
    RUN apt-get install -y g++-aarch64-linux-gnu
    ENV CC=aarch64-linux-gnu-gcc CXX=aarch64-linux-gnu-g++
    RUN cmake -B build -DCMAKE_TOOLCHAIN_FILE=arm64.toolchain.cmake
    → host 네이티브 속도로 cross compile.

  ■ Conan / vcpkg + 컨테이너
    의존성도 cross compile 해야 함. 라이브러리 ABI 호환성 검증 필수.
    Conan profile / vcpkg triplet으로 명시:
      vcpkg install boost --triplet=arm64-linux

  ■ 함정
    1) 라이브러리 일부는 host 도구를 빌드 시 호출 (codegen).
       → "build for host first" 패턴 필요 (LLVM, Qt 등)
    2) 시간 - QEMU emulation은 5~10배 느림. CI 1시간 → 8시간.
    3) ABI 미스매치 - 정적 라이브러리는 cross OK, 동적은 검증
    4) glibc 버전 불일치 - 가장 낮은 OS 사용
    5) /proc/cpuinfo 다름 - SIMD 자동 감지 코드 깨짐

  ■ Apple Silicon 개발자 / x86 운영
    M1/M2 노트북에서 docker run 하면 ARM 컨테이너 돌아감.
    x86 운영 서버에 push할 때는 buildx --platform linux/amd64 명시.
    잊으면 ARM 이미지가 운영에 나가서 exec format error.

  ■ 메모리 측면
    크로스 빌드 시 host RAM 부담 큼 (병렬 컴파일 + emulation).
    docker daemon에 RAM 16GB+ 권장. CI는 RAM 32GB 이상.
)";
    cout << endl;
}


// =============================================================================
//  레슨 6 — 컨테이너 런타임 메모리 / cgroup / OOM
// =============================================================================

void lesson6_runtime_memory() {
    cout << "[레슨 6] 컨테이너 런타임 메모리 관리\n";
    cout << R"(
  ■ cgroup v2 메모리 제한
    docker run --memory=512m --memory-swap=512m myapp
    → 512MB 초과 시 OOM Killer가 컨테이너의 PID 1 죽임 (kubectl describe로 확인)

  ■ OOM 동작
    1) 컨테이너 안의 프로세스 메모리 사용 → cgroup 카운트 증가
    2) limit 도달 → kernel OOM killer 작동
    3) PID 1 죽으면 컨테이너 재시작 (restart policy)
    4) 큐브에선 Pod의 OOMKilled exit code 137

  ■ C++ 코드의 메모리 인식 함정
    - new (std::nothrow) 또는 set_new_handler 도 OOM kill 못 막음
    - cgroup limit는 RSS 기반 (가상 메모리 X)
    - JVM처럼 -Xmx 옵션 없음. 직접 application-side budget 관리
      예: 큰 캐시는 50% 이상 안 쓰도록 조절

  ■ jemalloc / tcmalloc - 단편화 방지
    glibc 기본 ptmalloc은 long-running 서버에서 단편화 누적 → RSS 무한 증가
    → jemalloc/tcmalloc 사용:
      LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so myapp
    → 재컴파일 없이 효과 측정 가능

  ■ 메모리 메트릭 모니터링
    /proc/[pid]/status      : VmRSS, VmPeak, VmHWM
    /sys/fs/cgroup/memory.* : current, max, swap
    cAdvisor / Prometheus으로 시계열 수집

  ■ Slim down 체크리스트
    1) 정적 링크로 베이스 의존 줄이기
    2) -Os / -Oz 컴파일 (크기 우선)
    3) strip 으로 심볼 제거 (디버그 이미지 별도 유지)
    4) 사용 안 하는 라이브러리 제거
    5) C++17 RTTI / 예외 끄기 (-fno-rtti -fno-exceptions, 가능한 곳만)

  ■ 컨테이너 메모리와 std::thread::hardware_concurrency()
    호스트 CPU 반환 → cgroup CPU 제한 무시
    → C++ 코드가 호스트 코어 수만큼 스레드 만들면 throttling 폭주
    해결:
      // pseudo: 컨테이너 인식 코어 수
      long get_container_cpus() {
          // /sys/fs/cgroup/cpu.max 또는 cpu.shares 파싱
          // 또는 sched_getaffinity()
      }

  ■ Swap의 역설
    컨테이너에서 swap 켜면 OOM 늦어지지만 응답 시간 폭주.
    → 운영은 swap=0 (memory == memory-swap) 권장
    → ML 추론처럼 일시적 큰 메모리는 명시적 mmap + advise
)";
    cout << endl;
}


// =============================================================================
//  레슨 7 — 컨테이너 안에서 디버깅
// =============================================================================

void lesson7_debugging_in_container() {
    cout << "[레슨 7] 컨테이너 안에서 디버깅\n";
    cout << R"(
  ■ 운영 컨테이너 진입 (가능하면)
    docker exec -it <container> /bin/bash
    → distroless엔 셸 없음. :debug 태그 또는 ephemeral container

  ■ ephemeral container (Kubernetes)
    kubectl debug -it <pod> --image=busybox --share-processes
    → 같은 PID namespace 공유. 운영 이미지 안 건드리고 진단 도구 추가

  ■ gdb 사용
    docker run --cap-add=SYS_PTRACE --security-opt seccomp=unconfined ...
    apt install -y gdb
    gdb -p <pid>
    또는 core dump 분석:
      docker cp container:/cores/core.1234 ./
      gdb /usr/local/bin/myapp ./core.1234

  ■ core dump 활성화
    호스트 (cgroup v1):
      sysctl -w kernel.core_pattern=/cores/core.%p
      docker run --ulimit core=-1 -v /cores:/cores ...
    호스트 (cgroup v2 / systemd):
      systemd-coredump 사용
    컨테이너 안 쓰기 가능한 경로 + 충분한 디스크 + 권한

  ■ perf / strace (성능 / 시스템콜 추적)
    docker run --cap-add=SYS_ADMIN --cap-add=SYS_PTRACE ...
    perf record -F 99 -p $(pidof myapp) -- sleep 30
    perf report
    flamegraph → 핫스팟 시각화

  ■ symbol 분리 (작은 운영 + 디버깅 가능)
    objcopy --only-keep-debug myapp myapp.debug
    objcopy --strip-all myapp
    objcopy --add-gnu-debuglink=myapp.debug myapp
    → myapp는 작아지고, myapp.debug는 별도 보관
    → gdb는 자동으로 .debug 파일 찾음 (debuginfod 활용 가능)

  ■ 메모리 누수 디버깅
    valgrind는 컨테이너 안에서 동작하나 매우 느림 (10~50배)
    대안:
      LD_PRELOAD=libjemalloc.so + MALLOC_CONF=prof:true
      → jeprof로 heap profile 분석. 운영 적용 가능

  ■ 라이브 프로파일링
    eBPF (BCC, bpftrace) - 컨테이너 외부 / 호스트에서
      bpftrace -e 'tracepoint:syscalls:sys_enter_open { @[comm] = count(); }'
    USDT (User Statically Defined Tracing) - 코드에 마커

  ■ 컨테이너 디버깅 황금률
    1) 운영 이미지 = release 이미지 (작고 보안적)
    2) 디버그 이미지 = 별도 태그 (:debug). 같은 코드 + 심볼 + 도구
    3) ephemeral container로 운영에 일시 도구 주입
    4) 모든 진단은 호스트 / 외부 관측 (eBPF, perf) 우선
    5) 코어덤프 → 빌드 산출물에서 심볼 매칭하여 분석

  ┌─ 메모리 함정 종합 ────────────────────────────────────┐
  │ ✦ glibc tcmalloc/jemalloc 차이로 RSS 다름 (착시)      │
  │ ✦ malloc_trim() 또는 jemalloc::purge로 미사용 반환    │
  │ ✦ memcg 통계 갱신 지연 - peak는 약간 underestimate    │
  │ ✦ 작은 컨테이너에서 코어덤프 OOM 직격                 │
  │ ✦ ASan은 shadow memory 8배 가상메모리 사용            │
  │ ✦ fork-exec 패턴은 RSS 일시 2배 (COW) → limit 초과 OOM│
  │   - posix_spawn 대안                                  │
  └───────────────────────────────────────────────────────┘
)";
    cout << endl;
}


// =============================================================================
//  연습문제
// =============================================================================
//
//  [연습 1] 위 챕터 33의 main.cpp를 대상으로 멀티 스테이지 Dockerfile 작성
//   → builder + distroless runtime, 이미지 50MB 이하 목표
//
//  [연습 2] sanitizer 이미지 빌드 + 일부러 use-after-free 코드 추가
//   → ASan이 stack trace로 잡는지 확인. 라인 번호 확실히 나오게.
//
//  [연습 3] buildx로 ARM64 / x86_64 동시 빌드 후 manifest 확인
//   → docker buildx imagetools inspect myapp:latest
//
//  [연습 4] cgroup memory 제한 직접 인식하는 헬퍼 함수
//   → /sys/fs/cgroup/memory.max 파싱. v1/v2 모두 처리.
//
//  [연습 5] ch15 또는 ch34 네트워크 코드를 컨테이너로 패키징
//   → host network vs bridge 모드 차이 측정
//   → 컨테이너 간 통신 (docker network)
//
//  [연습 6] 운영 이미지에 심볼 분리 - .debug 별도 보관 → gdb 분석 흐름 시연
//
//  [연습 7] jemalloc LD_PRELOAD로 ch08의 메모리 풀 코드 RSS 비교
//   → 5분 부하테스트 후 RSS 추이 그래프
//
//  [연습 8] healthcheck 추가
//   → HEALTHCHECK CMD 명령으로 자체 진단. unhealthy 시 자동 재시작 정책.
// =============================================================================
