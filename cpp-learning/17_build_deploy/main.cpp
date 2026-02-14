/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C++ 학습 17단계: 빌드, 배포, CI/CD
  ─ CMake 심화, 패키징, Docker, GitHub Actions ─

  코드를 작성하는 것만큼 빌드·테스트·배포 파이프라인도 중요합니다.
  이 파일은 실무 빌드/배포 워크플로우의 전체 그림을 가이드합니다.

  ■ 컴파일: g++ -std=c++17 -Wall -o 17_build main.cpp

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/
#include <iostream>
#include <string>
using namespace std;

void lesson1_cmake_advanced();
void lesson2_build_types();
void lesson3_packaging();
void lesson4_docker();
void lesson5_cicd();
void lesson6_deployment();

int main() {
    cout << "========================================\n";
    cout << "  C++ 17단계 : 빌드, 배포, CI/CD\n";
    cout << "========================================\n\n";

    lesson1_cmake_advanced();
    lesson2_build_types();
    lesson3_packaging();
    lesson4_docker();
    lesson5_cicd();
    lesson6_deployment();

    cout << "\n17단계 학습 완료!\n";
    return 0;
}


// =========================================================================
//  레슨 1 — CMake 심화
// =========================================================================
void lesson1_cmake_advanced() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 1 : CMake 심화                 │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    cout << R"(
  ■ 실전 CMakeLists.txt (멀티 파일 프로젝트)
  ═══════════════════════════════════════════

  cmake_minimum_required(VERSION 3.16)
  project(MyApp
      VERSION 1.0.0           # 버전 관리
      LANGUAGES CXX
      DESCRIPTION "내 앱"
  )

  # ── C++ 표준 설정 ──
  set(CMAKE_CXX_STANDARD 17)
  set(CMAKE_CXX_STANDARD_REQUIRED ON)
  set(CMAKE_CXX_EXTENSIONS OFF)    # GNU 확장 비활성화

  # ── 빌드 타입 기본값 설정 ──
  if(NOT CMAKE_BUILD_TYPE)
      set(CMAKE_BUILD_TYPE Release)
  endif()

  # ── 컴파일 옵션 ──
  add_compile_options(-Wall -Wextra -Wpedantic)

  # ── 라이브러리 만들기 ──
  add_library(mylib STATIC         # 정적 라이브러리
      src/player.cpp
      src/enemy.cpp
      src/item.cpp
  )
  target_include_directories(mylib PUBLIC include)

  # ── 실행 파일 만들기 ──
  add_executable(myapp src/main.cpp)
  target_link_libraries(myapp PRIVATE mylib)

  # ── 외부 라이브러리 가져오기 (FetchContent) ──
  include(FetchContent)

  FetchContent_Declare(
      fmt
      GIT_REPOSITORY https://github.com/fmtlib/fmt.git
      GIT_TAG 10.0.0
  )
  FetchContent_Declare(
      nlohmann_json
      GIT_REPOSITORY https://github.com/nlohmann/json.git
      GIT_TAG v3.11.3
  )
  FetchContent_MakeAvailable(fmt nlohmann_json)

  target_link_libraries(myapp PRIVATE
      fmt::fmt
      nlohmann_json::nlohmann_json
  )

  # ── 테스트 설정 ──
  enable_testing()

  FetchContent_Declare(
      googletest
      GIT_REPOSITORY https://github.com/google/googletest.git
      GIT_TAG v1.14.0
  )
  FetchContent_MakeAvailable(googletest)

  add_executable(tests
      tests/test_player.cpp
      tests/test_enemy.cpp
  )
  target_link_libraries(tests PRIVATE
      mylib
      GTest::gtest_main
  )
  add_test(NAME unit_tests COMMAND tests)

  # ── 인스톨 설정 ──
  install(TARGETS myapp DESTINATION bin)
  install(DIRECTORY include/ DESTINATION include)

)" << endl;
}


// =========================================================================
//  레슨 2 — 빌드 타입과 최적화
// =========================================================================
void lesson2_build_types() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 2 : 빌드 타입과 최적화         │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    cout << R"(
  ■ 빌드 타입  (cmake -DCMAKE_BUILD_TYPE=...)
  ───────────────────────────────────────

  ┌───────────────┬──────────────┬───────────────────────────┐
  │ 빌드 타입     │ 최적화       │ 용도                       │
  ├───────────────┼──────────────┼───────────────────────────┤
  │ Debug         │ -O0 -g       │ 개발, 디버깅 (기본)        │
  │ Release       │ -O3 -DNDEBUG │ 출시, 배포 (최대 성능)     │
  │ RelWithDebInfo│ -O2 -g       │ 성능 + 디버깅 정보         │
  │ MinSizeRel    │ -Os -DNDEBUG │ 임베디드 (크기 최소화)     │
  └───────────────┴──────────────┴───────────────────────────┘

  ■ 빌드 명령 예시
  ───────────────────────────────────────

  # Debug 빌드 (개발 중)
  mkdir build-debug && cd build-debug
  cmake -DCMAKE_BUILD_TYPE=Debug ..
  cmake --build .

  # Release 빌드 (배포용)
  mkdir build-release && cd build-release
  cmake -DCMAKE_BUILD_TYPE=Release ..
  cmake --build .

  # 병렬 빌드 (빠르게)
  cmake --build . -- -j$(nproc)    # Linux
  cmake --build . -- /m            # MSVC

  ■ 최적화 옵션 상세
  ───────────────────────────────────────
  -O0 : 최적화 없음 (디버깅 쉬움)
  -O1 : 기본 최적화
  -O2 : 대부분의 최적화 (추천)
  -O3 : 공격적 최적화 (약간 더 빠를 수 있음)
  -Os : 크기 최적화
  -Ofast : O3 + 정밀도 무시 (위험할 수 있음)

  ■ 유용한 컴파일 옵션
  ───────────────────────────────────────
  -Wall -Wextra -Wpedantic   모든 경고 켜기 (필수!)
  -Werror                    경고를 에러로 (CI에서 유용)
  -fsanitize=address         메모리 버그 감지
  -fsanitize=undefined       정의되지 않은 동작 감지
  -fPIC                      공유 라이브러리용
  -march=native              현재 CPU에 최적화
)" << endl;
}


// =========================================================================
//  레슨 3 — 패키징과 설치
// =========================================================================
void lesson3_packaging() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 3 : 패키징과 설치              │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    cout << R"(
  ■ CPack (CMake 내장 패키징 도구)
  ───────────────────────────────────────

  # CMakeLists.txt 마지막에 추가
  set(CPACK_PACKAGE_NAME "MyApp")
  set(CPACK_PACKAGE_VERSION "1.0.0")
  set(CPACK_GENERATOR "ZIP;TGZ")      # 패키지 형식
  include(CPack)

  # 사용법
  cd build
  cmake --build .
  cpack                                 # 패키지 생성

  ■ 패키지 형식
  ───────────────────────────────────────
  ZIP / TGZ    : 단순 압축 파일
  DEB          : Ubuntu/Debian 패키지
  RPM          : CentOS/Fedora 패키지
  NSIS / WIX   : Windows 설치 프로그램
  DMG          : macOS 디스크 이미지

  ■ 정적 라이브러리 vs 동적 라이브러리
  ───────────────────────────────────────

  ┌──────────┬─────────────────┬─────────────────────┐
  │          │ 정적 (.a/.lib)  │ 동적 (.so/.dll)      │
  ├──────────┼─────────────────┼─────────────────────┤
  │ 링크     │ 컴파일 시 합침  │ 실행 시 로드         │
  │ 실행파일 │ 크기 큼         │ 크기 작음            │
  │ 배포     │ 단독 실행 가능  │ DLL도 같이 배포      │
  │ 업데이트 │ 재컴파일 필요   │ DLL만 교체 가능      │
  └──────────┴─────────────────┴─────────────────────┘

  # CMake에서
  add_library(mylib STATIC ...)   # 정적
  add_library(mylib SHARED ...)   # 동적

  ■ vcpkg로 의존성 관리 (실무)
  ───────────────────────────────────────

  # 1. vcpkg 설치
  git clone https://github.com/microsoft/vcpkg.git
  cd vcpkg && bootstrap-vcpkg.bat     # Windows
  cd vcpkg && ./bootstrap-vcpkg.sh    # Linux

  # 2. 패키지 설치
  ./vcpkg install fmt nlohmann-json spdlog boost-asio

  # 3. CMake에서 사용
  cmake -B build -DCMAKE_TOOLCHAIN_FILE=vcpkg/scripts/buildsystems/vcpkg.cmake
  cmake --build build
)" << endl;
}


// =========================================================================
//  레슨 4 — Docker
// =========================================================================
void lesson4_docker() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 4 : Docker로 빌드/배포         │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    cout << R"(
  ■ Docker란?
  ───────────────────────────────────────
  "내 컴퓨터에서는 되는데..." 문제를 해결!

  Docker 컨테이너 = 앱 + 환경을 통째로 패키징
  어디서든 동일한 환경에서 실행 가능

  ■ Dockerfile (C++ 프로젝트용)
  ═══════════════════════════════════════

  # 멀티 스테이지 빌드 (최종 이미지 크기 최소화)

  # ── 1단계: 빌드 ──
  FROM ubuntu:22.04 AS builder

  RUN apt-get update && apt-get install -y \
      g++ cmake make git

  WORKDIR /app
  COPY . .

  RUN mkdir build && cd build && \
      cmake -DCMAKE_BUILD_TYPE=Release .. && \
      cmake --build . -j$(nproc)

  # ── 2단계: 실행 (빌드 도구 없이 작은 이미지) ──
  FROM ubuntu:22.04

  RUN apt-get update && apt-get install -y \
      libstdc++6

  COPY --from=builder /app/build/myapp /usr/local/bin/

  EXPOSE 8080
  CMD ["myapp"]

  ■ Docker 명령어
  ═══════════════════════════════════════

  # 이미지 빌드
  docker build -t myapp:1.0 .

  # 컨테이너 실행
  docker run -p 8080:8080 myapp:1.0

  # 인터랙티브 쉘
  docker run -it myapp:1.0 /bin/bash

  # docker-compose (여러 서비스)
  docker-compose up -d

  ■ docker-compose.yml 예시
  ═══════════════════════════════════════

  version: '3.8'
  services:
    app:
      build: .
      ports:
        - "8080:8080"
      depends_on:
        - db

    db:
      image: postgres:15
      environment:
        POSTGRES_DB: mydb
        POSTGRES_PASSWORD: secret
      volumes:
        - db_data:/var/lib/postgresql/data

  volumes:
    db_data:
)" << endl;
}


// =========================================================================
//  레슨 5 — CI/CD (지속적 통합/배포)
// =========================================================================
void lesson5_cicd() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 5 : CI/CD 파이프라인           │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    cout << R"(
  ■ CI/CD란?
  ───────────────────────────────────────

  CI (Continuous Integration) = 지속적 통합
    → 코드를 push할 때마다 자동으로 빌드 + 테스트

  CD (Continuous Deployment) = 지속적 배포
    → 테스트 통과 시 자동으로 서버에 배포

  코드 변경 → [빌드] → [테스트] → [배포]
              ←── 자동! ──→

  ■ GitHub Actions 예시  (.github/workflows/ci.yml)
  ═══════════════════════════════════════════════

  name: C++ CI

  on:
    push:
      branches: [main]
    pull_request:
      branches: [main]

  jobs:
    build:
      runs-on: ubuntu-latest    # 또는 windows-latest, macos-latest

      steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y cmake g++

      - name: Configure
        run: cmake -B build -DCMAKE_BUILD_TYPE=Release

      - name: Build
        run: cmake --build build -j$(nproc)

      - name: Test
        run: cd build && ctest --output-on-failure

    # Windows에서도 빌드
    build-windows:
      runs-on: windows-latest

      steps:
      - uses: actions/checkout@v4

      - name: Configure
        run: cmake -B build

      - name: Build
        run: cmake --build build --config Release

      - name: Test
        run: cd build && ctest -C Release --output-on-failure

  ■ GitLab CI 예시  (.gitlab-ci.yml)
  ═══════════════════════════════════════

  stages:
    - build
    - test
    - deploy

  build:
    stage: build
    image: gcc:latest
    script:
      - mkdir build && cd build
      - cmake -DCMAKE_BUILD_TYPE=Release ..
      - cmake --build . -j$(nproc)
    artifacts:
      paths:
        - build/

  test:
    stage: test
    script:
      - cd build && ctest --output-on-failure

  deploy:
    stage: deploy
    only:
      - main
    script:
      - echo "배포 스크립트 실행"
)" << endl;
}


// =========================================================================
//  레슨 6 — 배포 전략
// =========================================================================
void lesson6_deployment() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 6 : 배포 전략                  │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    cout << R"(
  ■ 배포 방식 비교
  ───────────────────────────────────────

  ┌─────────────────┬───────────────────────────────────┐
  │ 방식            │ 설명                               │
  ├─────────────────┼───────────────────────────────────┤
  │ 바이너리 배포   │ 실행 파일만 복사 (가장 간단)       │
  │ 패키지 배포     │ deb/rpm/msi 패키지 (설치 관리)     │
  │ 컨테이너 배포   │ Docker 이미지 (환경 통일)          │
  │ 클라우드 배포   │ AWS/GCP/Azure (자동 확장)          │
  └─────────────────┴───────────────────────────────────┘

  ■ 릴리스 체크리스트
  ───────────────────────────────────────

  [ ] 모든 테스트 통과 (단위, 통합, E2E)
  [ ] Release 빌드로 컴파일
  [ ] Sanitizer로 메모리 버그 검사
  [ ] 성능 벤치마크 확인
  [ ] 버전 번호 업데이트 (Semantic Versioning)
  [ ] CHANGELOG 작성
  [ ] Git 태그 생성  (git tag v1.0.0)
  [ ] 패키지/이미지 빌드
  [ ] 스테이징 환경에서 테스트
  [ ] 프로덕션 배포
  [ ] 모니터링 확인

  ■ Semantic Versioning  (MAJOR.MINOR.PATCH)
  ───────────────────────────────────────

  1.0.0 → 1.0.1 : 버그 수정 (PATCH)
  1.0.0 → 1.1.0 : 기능 추가, 호환성 유지 (MINOR)
  1.0.0 → 2.0.0 : 호환되지 않는 변경 (MAJOR)

  ■ 로깅과 모니터링
  ───────────────────────────────────────

  로그 라이브러리: spdlog (가장 인기)

  #include "spdlog/spdlog.h"
  spdlog::info("서버 시작 포트={}", 8080);
  spdlog::warn("연결 수 {}개 초과", max_conn);
  spdlog::error("DB 연결 실패: {}", e.what());

  로그 레벨: trace < debug < info < warn < error < critical

  모니터링 도구: Prometheus + Grafana (메트릭)
                 ELK Stack (로그 수집/분석)
)" << endl;
}
