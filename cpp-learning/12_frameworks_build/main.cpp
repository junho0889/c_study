/*
=============================================================================
  C++ 학습 12단계: 프레임워크, 빌드 시스템, 개발 생태계
=============================================================================
  [학습 목표]
  1. CMake 빌드 시스템을 이해하고 사용한다
  2. 주요 C++ 프레임워크와 라이브러리를 안다
  3. 프로젝트 구조를 설계할 수 있다
  4. 패키지 관리와 의존성 관리를 이해한다
  5. 테스트 프레임워크를 안다

  [컴파일] g++ -std=c++17 -o 12_frameworks main.cpp
=============================================================================
*/
#include <iostream>
#include <string>
#include <vector>
#include <map>
using namespace std;

void lesson1_cmake();
void lesson2_project_structure();
void lesson3_frameworks();
void lesson4_testing();
void lesson5_package_managers();
void lesson6_dev_workflow();

int main() {
    cout << "========================================\n";
    cout << "  C++ 12단계 : 프레임워크 & 빌드\n";
    cout << "========================================\n\n";

    lesson1_cmake();
    lesson2_project_structure();
    lesson3_frameworks();
    lesson4_testing();
    lesson5_package_managers();
    lesson6_dev_workflow();

    cout << "\n12단계 학습 완료!\n";
    cout << "\n전체 C++ 학습 커리큘럼 완료!\n";
    return 0;
}


// =====================================================================
// 레슨 1 — CMake 빌드 시스템
// =====================================================================
void lesson1_cmake() {
    cout << "[레슨 1] CMake 빌드 시스템\n\n";

    /*
    ★ 왜 CMake?
    - g++ main.cpp 는 간단하지만, 파일이 수십 개가 되면?
    - 플랫폼마다 빌드 방법이 다르면?
    - CMake = 크로스 플랫폼 빌드 시스템 (사실상 표준)

    ★ CMakeLists.txt 기본 구조
    ─────────────────────────────────────
    cmake_minimum_required(VERSION 3.16)
    project(MyProject LANGUAGES CXX)

    set(CMAKE_CXX_STANDARD 17)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)

    add_executable(myapp
        src/main.cpp
        src/player.cpp
        src/enemy.cpp
    )
    ─────────────────────────────────────

    ★ 빌드 방법
    mkdir build
    cd build
    cmake ..          # 빌드 파일 생성
    cmake --build .   # 실제 빌드

    ★ 주요 CMake 명령어
    ┌───────────────────────────┬─────────────────────────────┐
    │ 명령                      │ 설명                         │
    ├───────────────────────────┼─────────────────────────────┤
    │ project(이름)             │ 프로젝트 이름               │
    │ add_executable(이름 소스) │ 실행 파일 생성              │
    │ add_library(이름 소스)    │ 라이브러리 생성             │
    │ target_link_libraries()   │ 라이브러리 연결             │
    │ find_package(패키지)      │ 설치된 라이브러리 찾기      │
    │ target_include_directories│ 헤더 경로 추가              │
    │ add_subdirectory(경로)    │ 하위 디렉토리의 CMake 포함  │
    └───────────────────────────┴─────────────────────────────┘

    ★ 외부 라이브러리 사용 예시
    find_package(fmt REQUIRED)
    target_link_libraries(myapp PRIVATE fmt::fmt)
    */

    cout << "  CMake 사용법:\n";
    cout << "  1. CMakeLists.txt 작성\n";
    cout << "  2. mkdir build && cd build\n";
    cout << "  3. cmake ..\n";
    cout << "  4. cmake --build .\n";
    cout << endl;
}


// =====================================================================
// 레슨 2 — 프로젝트 구조
// =====================================================================
void lesson2_project_structure() {
    cout << "[레슨 2] 프로젝트 구조\n\n";

    /*
    ★ 권장 프로젝트 구조

    my_project/
    ├── CMakeLists.txt          ← 최상위 빌드 설정
    ├── README.md               ← 프로젝트 설명
    ├── .gitignore              ← Git 무시 파일
    │
    ├── include/                ← 공개 헤더 파일 (.h / .hpp)
    │   └── my_project/
    │       ├── player.hpp
    │       └── enemy.hpp
    │
    ├── src/                    ← 소스 파일 (.cpp)
    │   ├── main.cpp
    │   ├── player.cpp
    │   └── enemy.cpp
    │
    ├── tests/                  ← 테스트 코드
    │   ├── CMakeLists.txt
    │   ├── test_player.cpp
    │   └── test_enemy.cpp
    │
    ├── lib/                    ← 외부 라이브러리 (또는 third_party/)
    │
    ├── build/                  ← 빌드 결과물 (gitignore에 추가)
    │
    └── docs/                   ← 문서

    ★ 헤더 파일 (.h / .hpp)
    - 클래스 선언, 함수 선언을 담는 파일
    - 여러 .cpp 파일에서 #include로 공유

    ★ 소스 파일 (.cpp)
    - 함수/클래스의 실제 구현을 담는 파일
    - 헤더에서 선언한 것을 여기서 정의

    ★ 헤더 가드 (Include Guard)
    ─────────────────────────────
    // player.hpp
    #pragma once           ← 현대적 방식 (추천)

    // 또는 전통적 방식:
    #ifndef PLAYER_HPP
    #define PLAYER_HPP
    class Player { ... };
    #endif
    ─────────────────────────────
    → 같은 헤더가 2번 포함되는 것을 방지
    */

    cout << "  프로젝트 구조 핵심:\n";
    cout << "  include/ → 헤더 (.hpp)   선언\n";
    cout << "  src/     → 소스 (.cpp)   구현\n";
    cout << "  tests/   → 테스트 코드\n";
    cout << "  build/   → 빌드 결과 (gitignore)\n";
    cout << endl;
}


// =====================================================================
// 레슨 3 — 주요 프레임워크와 라이브러리
// =====================================================================
void lesson3_frameworks() {
    cout << "[레슨 3] 주요 C++ 프레임워크 & 라이브러리\n\n";

    /*
    ═══════════════════════════════════════════
     분야별 주요 라이브러리
    ═══════════════════════════════════════════

    ★ GUI (그래픽 사용자 인터페이스)
    ┌─────────────┬─────────────────────────────────┐
    │ Qt          │ 가장 인기 있는 C++ GUI 프레임워크 │
    │             │ 크로스 플랫폼, 시그널/슬롯 패턴  │
    │ wxWidgets   │ 네이티브 룩앤필 GUI              │
    │ Dear ImGui  │ 게임/도구용 즉시 모드 GUI        │
    │ FLTK        │ 가벼운 GUI                      │
    └─────────────┴─────────────────────────────────┘

    ★ 게임 개발
    ┌─────────────┬─────────────────────────────────┐
    │ Unreal Engine│ AAA급 게임 엔진 (C++)          │
    │ SDL2        │ 2D 게임, 멀티미디어              │
    │ SFML        │ 2D 그래픽, 소리, 네트워크        │
    │ OpenGL/Vulkan│ 3D 그래픽 API                  │
    │ Raylib      │ 간단한 게임 라이브러리            │
    └─────────────┴─────────────────────────────────┘

    ★ 웹 / 네트워크
    ┌─────────────┬─────────────────────────────────┐
    │ Boost.Asio  │ 비동기 네트워크 IO               │
    │ cpp-httplib │ 간단한 HTTP 서버/클라이언트      │
    │ Crow/Drogon │ 웹 프레임워크                    │
    │ gRPC        │ RPC 프레임워크                   │
    │ libcurl     │ HTTP 클라이언트                  │
    └─────────────┴─────────────────────────────────┘

    ★ 데이터 / 직렬화
    ┌─────────────┬─────────────────────────────────┐
    │ nlohmann/json│ JSON 라이브러리 (가장 인기)     │
    │ protobuf    │ Google의 직렬화 프레임워크       │
    │ SQLite      │ 임베디드 데이터베이스             │
    │ fmt         │ 포맷 라이브러리 (printf 대체)    │
    │ spdlog      │ 빠른 로깅 라이브러리             │
    └─────────────┴─────────────────────────────────┘

    ★ 수학 / 과학
    ┌─────────────┬─────────────────────────────────┐
    │ Eigen       │ 선형 대수 (행렬, 벡터)           │
    │ OpenCV      │ 컴퓨터 비전, 이미지 처리         │
    │ TensorFlow  │ 머신러닝 (C++ API 있음)          │
    └─────────────┴─────────────────────────────────┘

    ★ 유틸리티
    ┌─────────────┬─────────────────────────────────┐
    │ Boost       │ C++ 확장 라이브러리 모음          │
    │ abseil      │ Google의 C++ 유틸리티            │
    │ range-v3    │ 범위 라이브러리                   │
    │ cxxopts     │ 명령줄 인자 파서                 │
    └─────────────┴─────────────────────────────────┘
    */

    // 간단히 표로 출력
    struct Library {
        string name, category, description;
    };

    vector<Library> libs = {
        {"Qt",            "GUI",    "크로스 플랫폼 GUI 프레임워크"},
        {"SDL2/SFML",     "게임",   "2D 게임 / 멀티미디어"},
        {"Unreal Engine", "게임",   "AAA 게임 엔진"},
        {"Boost",         "유틸",   "C++ 확장 라이브러리 모음"},
        {"nlohmann/json", "데이터", "JSON 파싱/생성"},
        {"OpenCV",        "영상",   "컴퓨터 비전"},
        {"GoogleTest",    "테스트", "단위 테스트 프레임워크"},
        {"spdlog",        "로깅",   "고속 로깅"},
        {"fmt",           "포맷",   "문자열 포맷팅"},
    };
    // → libs.size() = 9

    cout << "  주요 라이브러리 요약:\n\n";
    for (const auto& lib : libs) {
        // 9회 반복, 입력 순서대로 출력
        cout << "  [" << lib.category << "] "
             << lib.name << " - " << lib.description << "\n";
    }
    // > 출력:
    //   [GUI] Qt - 크로스 플랫폼 GUI 프레임워크
    //   [게임] SDL2/SFML - 2D 게임 / 멀티미디어
    //   [게임] Unreal Engine - AAA 게임 엔진
    //   [유틸] Boost - C++ 확장 라이브러리 모음
    //   [데이터] nlohmann/json - JSON 파싱/생성
    //   [영상] OpenCV - 컴퓨터 비전
    //   [테스트] GoogleTest - 단위 테스트 프레임워크
    //   [로깅] spdlog - 고속 로깅
    //   [포맷] fmt - 문자열 포맷팅
    cout << endl;
}


// =====================================================================
// 레슨 4 — 테스트 프레임워크
// =====================================================================
void lesson4_testing() {
    cout << "[레슨 4] 테스트\n\n";

    /*
    ★ 왜 테스트?
    - 코드가 제대로 동작하는지 자동으로 검증
    - 수정 후 기존 기능이 깨지지 않았는지 확인 (회귀 테스트)
    - 리팩토링할 때 자신감을 준다

    ★ 대표적 C++ 테스트 프레임워크
    1. Google Test (gtest) — 가장 널리 사용
    2. Catch2             — 헤더 하나로 사용 가능
    3. doctest            — 가장 빠른 컴파일

    ★ Google Test 예시
    ─────────────────────────────────────
    #include <gtest/gtest.h>

    int add(int a, int b) { return a + b; }

    TEST(AddTest, PositiveNumbers) {
        EXPECT_EQ(add(2, 3), 5);
        EXPECT_EQ(add(0, 0), 0);
    }

    TEST(AddTest, NegativeNumbers) {
        EXPECT_EQ(add(-1, -1), -2);
        EXPECT_EQ(add(-1, 1), 0);
    }
    ─────────────────────────────────────

    ★ 주요 매크로
    EXPECT_EQ(a, b)    같은가?
    EXPECT_NE(a, b)    다른가?
    EXPECT_TRUE(cond)  참인가?
    EXPECT_FALSE(cond) 거짓인가?
    EXPECT_THROW(f(), ExType)  예외 발생하나?

    ASSERT_* 는 실패 시 즉시 중단
    EXPECT_* 는 실패해도 계속 진행

    ★ CMake에서 테스트 설정
    ─────────────────────────────────────
    find_package(GTest REQUIRED)
    add_executable(tests test_main.cpp)
    target_link_libraries(tests GTest::gtest_main)
    add_test(NAME my_tests COMMAND tests)
    ─────────────────────────────────────
    */

    // 간단한 수동 테스트 예시
    cout << "  간단한 수동 테스트 예시:\n\n";

    auto assert_eq = [](auto actual, auto expected, const string& name) {
        if (actual == expected) {
            cout << "  [PASS] " << name << "\n";
        } else {
            cout << "  [FAIL] " << name
                 << " (expected=" << expected
                 << " actual=" << actual << ")\n";
        }
    };

    auto add = [](int a, int b) { return a + b; };

    assert_eq(add(2, 3), 5, "2+3=5");
    // → add(2,3) = 5, expected 5 → 일치 → PASS
    // > 출력:   [PASS] 2+3=5
    assert_eq(add(-1, 1), 0, "-1+1=0");
    // → -1+1=0 → PASS
    // > 출력:   [PASS] -1+1=0
    assert_eq(add(0, 0), 0, "0+0=0");
    // → 0+0=0 → PASS
    // > 출력:   [PASS] 0+0=0
    assert_eq(add(100, -100), 0, "100+(-100)=0");
    // → 0 → PASS
    // > 출력:   [PASS] 100+(-100)=0

    cout << endl;
}


// =====================================================================
// 레슨 5 — 패키지 관리자
// =====================================================================
void lesson5_package_managers() {
    cout << "[레슨 5] 패키지 관리자\n\n";

    /*
    ★ C++에는 pip(Python)이나 npm(JS) 같은 공식 패키지 관리자가 없다!
    → 여러 도구가 경쟁 중

    ┌─────────────┬─────────────────────────────────────┐
    │ 도구        │ 특징                                 │
    ├─────────────┼─────────────────────────────────────┤
    │ vcpkg       │ Microsoft, CMake 통합 좋음           │
    │             │ vcpkg install fmt                    │
    ├─────────────┼─────────────────────────────────────┤
    │ Conan       │ Python 기반, 유연한 설정             │
    │             │ conan install .                      │
    ├─────────────┼─────────────────────────────────────┤
    │ FetchContent│ CMake 내장, 소스 자동 다운로드        │
    │             │ 별도 설치 불필요 (추천!)               │
    ├─────────────┼─────────────────────────────────────┤
    │ git submodule│ Git 내장, 간단하지만 관리 번거로움  │
    └─────────────┴─────────────────────────────────────┘

    ★ FetchContent 예시 (CMake)
    ─────────────────────────────────────
    include(FetchContent)

    FetchContent_Declare(
        fmt
        GIT_REPOSITORY https://github.com/fmtlib/fmt.git
        GIT_TAG 10.0.0
    )
    FetchContent_MakeAvailable(fmt)

    target_link_libraries(myapp PRIVATE fmt::fmt)
    ─────────────────────────────────────

    ★ vcpkg 사용법
    1. git clone https://github.com/microsoft/vcpkg.git
    2. ./vcpkg/bootstrap-vcpkg.bat   (Windows)
    3. ./vcpkg install fmt nlohmann-json spdlog
    4. cmake -DCMAKE_TOOLCHAIN_FILE=vcpkg/scripts/...
    */

    cout << "  추천 의존성 관리 방법:\n";
    cout << "  1. CMake FetchContent (가장 간단)\n";
    cout << "  2. vcpkg (대규모 프로젝트)\n";
    cout << "  3. Conan (유연한 설정)\n";
    cout << endl;
}


// =====================================================================
// 레슨 6 — 개발 워크플로우
// =====================================================================
void lesson6_dev_workflow() {
    cout << "[레슨 6] 개발 워크플로우\n\n";

    /*
    ★ 개발 환경 세팅 (추천)
    ─────────────────────────────
    에디터: VS Code + C/C++ 확장 + CMake Tools 확장
    또는:   Visual Studio (Windows), CLion (유료)

    ★ Git 기본 워크플로우
    ─────────────────────────────
    git init                    # 저장소 생성
    git add .                   # 변경사항 스테이징
    git commit -m "메시지"      # 커밋
    git push origin main        # 원격 푸시
    git branch feature          # 브랜치 생성
    git checkout feature        # 브랜치 전환
    git merge feature           # 병합

    ★ .gitignore (반드시 설정!)
    ─────────────────────────────
    build/
    *.exe
    *.o
    *.obj
    .vs/
    .vscode/
    CMakeCache.txt
    cmake_install.cmake

    ★ CI/CD (자동 빌드/테스트)
    ─────────────────────────────
    GitHub Actions, GitLab CI 등으로
    push할 때마다 자동 빌드 + 테스트

    ★ 코드 스타일
    ─────────────────────────────
    .clang-format 파일을 프로젝트 루트에 두면
    자동으로 코드 스타일을 통일할 수 있다

    ★ 전문가가 되기 위한 학습 로드맵
    ─────────────────────────────
    1단계: 이 교재 완료 (기초~모던C++)
    2단계: 작은 프로젝트 만들기 (계산기, TODO앱, 게임)
    3단계: 오픈소스 코드 읽기 (GitHub에서 star 많은 프로젝트)
    4단계: 자료구조 & 알고리즘 공부
    5단계: 디자인 패턴 학습
    6단계: 관심 분야 특화 (게임, 시스템, 임베디드 등)
    7단계: 오픈소스 기여 (PR 보내기)
    */

    cout << "  ★ C++ 전문가 로드맵 ★\n\n";
    cout << "  [1] 이 교재 (01~12단계) 완료\n";
    cout << "  [2] 작은 프로젝트 직접 만들기\n";
    cout << "  [3] 오픈소스 코드 읽기\n";
    cout << "  [4] 자료구조 & 알고리즘\n";
    cout << "  [5] 디자인 패턴\n";
    cout << "  [6] 분야 특화 (게임/시스템/임베디드)\n";
    cout << "  [7] 오픈소스 기여\n\n";

    cout << "  추천 도서:\n";
    cout << "  - C++ Primer (입문)\n";
    cout << "  - Effective C++ / Effective Modern C++\n";
    cout << "  - The C++ Programming Language (Stroustrup)\n";
    cout << endl;
}
