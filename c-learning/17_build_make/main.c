/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C 학습 17단계: 빌드와 Make
  ─ 컴파일 과정, Makefile, CMake, 멀티 파일 프로젝트 ─

  프로그램이 커지면 파일을 나누고 빌드 자동화가 필수입니다.
  이 단계에서는 C 프로그램이 실행파일이 되기까지의 전체 과정과
  빌드 도구를 배웁니다.

  ■ 컴파일: gcc -std=c11 -Wall -o 17_build main.c
  ■ 실행:   ./17_build

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#include <stdio.h>

void lesson1_compile_stages(void);
void lesson2_multi_file(void);
void lesson3_header_files(void);
void lesson4_makefile_basics(void);
void lesson5_makefile_advanced(void);
void lesson6_cmake_intro(void);
void lesson7_practical(void);

int main(void) {
    printf("========================================\n");
    printf("  C 17단계 : 빌드와 Make\n");
    printf("========================================\n\n");

    lesson1_compile_stages();
    lesson2_multi_file();
    lesson3_header_files();
    lesson4_makefile_basics();
    lesson5_makefile_advanced();
    lesson6_cmake_intro();
    lesson7_practical();

    printf("\n17단계 학습 완료!\n");
    return 0;
}


/* =========================================================================
 *  레슨 1 — 컴파일 과정 4단계
 * ========================================================================= */
void lesson1_compile_stages(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 1 : 컴파일 4단계                │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ C 소스코드 → 실행파일까지 4단계:

    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ 전처리    │ →  │ 컴파일    │ →  │ 어셈블    │ →  │ 링킹     │
    │ (preproc) │    │ (compile)│    │ (assemble)│    │ (link)   │
    └──────────┘    └──────────┘    └──────────┘    └──────────┘
      .c → .i         .i → .s         .s → .o        .o → 실행파일

    ★ 각 단계 설명:
    ┌────┬───────────┬─────────────────────────────────┐
    │ #  │ 단계      │ 하는 일                          │
    ├────┼───────────┼─────────────────────────────────┤
    │ 1  │ 전처리    │ #include, #define 처리           │
    │    │           │ 주석 제거, 매크로 치환           │
    │ 2  │ 컴파일    │ C 코드 → 어셈블리어              │
    │    │           │ 문법 검사, 최적화                │
    │ 3  │ 어셈블    │ 어셈블리 → 기계어 (.o 파일)      │
    │ 4  │ 링킹      │ .o 파일들 + 라이브러리 결합      │
    │    │           │ → 최종 실행파일 생성             │
    └────┴───────────┴─────────────────────────────────┘

    ★ gcc 로 각 단계 직접 실행:
      gcc -E main.c -o main.i     # 전처리만
      gcc -S main.c -o main.s     # 어셈블리까지
      gcc -c main.c -o main.o     # 오브젝트까지
      gcc main.o -o program       # 링킹
      gcc main.c -o program       # 한번에 전부

    ★ 비유:
      전처리 = 레시피에서 재료 목록 정리
      컴파일 = 레시피를 공장 설계도로 번역
      어셈블 = 설계도대로 부품 제작
      링킹   = 부품들을 조립해서 완성품 만들기
    */

    printf("  ■ 컴파일 4단계\n");
    printf("    1. 전처리: .c → .i (#include, #define 처리)\n");
    printf("    2. 컴파일: .i → .s (어셈블리 코드 생성)\n");
    printf("    3. 어셈블: .s → .o (기계어 변환)\n");
    printf("    4. 링킹  : .o → 실행파일 (라이브러리 결합)\n\n");

    printf("  ■ 유용한 gcc 옵션\n");
    printf("    -Wall      : 모든 경고 활성화\n");
    printf("    -Wextra    : 추가 경고\n");
    printf("    -g         : 디버그 정보 포함\n");
    printf("    -O2        : 최적화 레벨 2\n");
    printf("    -std=c11   : C11 표준 사용\n");
    printf("    -o name    : 출력 파일 이름 지정\n");
    printf("    -lm        : 수학 라이브러리 링크\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 2 — 멀티 파일 프로젝트
 * ========================================================================= */
void lesson2_multi_file(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 2 : 멀티 파일 프로젝트          │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 왜 파일을 나누는가?
      1. 가독성: 기능별로 파일 분리
      2. 재사용: 다른 프로젝트에서 활용
      3. 컴파일 속도: 바뀐 파일만 다시 컴파일
      4. 협업: 파일 단위로 작업 분배

    ★ 전형적인 프로젝트 구조:
    ┌──────────────────────────────────┐
    │ my_project/                      │
    │ ├── src/                         │
    │ │   ├── main.c      (진입점)     │
    │ │   ├── math_util.c (수학 함수)  │
    │ │   └── string_util.c (문자열)   │
    │ ├── include/                     │
    │ │   ├── math_util.h (선언)       │
    │ │   └── string_util.h (선언)     │
    │ ├── Makefile                     │
    │ └── README.md                    │
    └──────────────────────────────────┘

    ★ 컴파일 방법:
      gcc -c src/main.c -o main.o -Iinclude
      gcc -c src/math_util.c -o math_util.o -Iinclude
      gcc main.o math_util.o -o program

      또는 한번에:
      gcc src/*.c -Iinclude -o program
    */

    printf("  ■ 파일 분리 원칙\n");
    printf("    1. 선언은 .h 파일 (헤더)\n");
    printf("    2. 구현은 .c 파일 (소스)\n");
    printf("    3. main 은 별도 파일로 분리\n\n");

    printf("  ■ 컴파일 방법\n");
    printf("    개별: gcc -c file1.c && gcc -c file2.c\n");
    printf("    링크: gcc file1.o file2.o -o program\n");
    printf("    한번에: gcc file1.c file2.c -o program\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 3 — 헤더 파일
 * ========================================================================= */
void lesson3_header_files(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 3 : 헤더 파일 (.h)             │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 헤더 파일 = 함수 선언, 구조체 정의, 매크로를 모아둔 파일

    ★ 비유:
      헤더 파일 = 계약서 (이런 함수가 있다는 약속)
      소스 파일 = 실제 업무 (함수의 구현)

    ★ 헤더 파일에 넣는 것:
    ┌──────────────────────┬──────────────────────────┐
    │ 넣는 것              │ 넣지 않는 것              │
    ├──────────────────────┼──────────────────────────┤
    │ 함수 선언 (prototype)│ 함수 구현 (body)         │
    │ 구조체/열거형 정의   │ 전역 변수 정의           │
    │ 매크로 (#define)     │ (extern 선언은 OK)       │
    │ typedef              │ static 함수 구현         │
    │ extern 변수 선언     │                          │
    │ 인라인 함수          │                          │
    └──────────────────────┴──────────────────────────┘

    ★ 헤더 파일 예시:
      ┌──────────────────────────────────┐
      │ // math_util.h                   │
      │ #ifndef MATH_UTIL_H              │
      │ #define MATH_UTIL_H              │
      │                                  │
      │ int add(int a, int b);           │
      │ int max(int a, int b);           │
      │ double average(int* arr, int n); │
      │                                  │
      │ #endif                           │
      └──────────────────────────────────┘

    ★ #include <> vs #include ""
      <stdio.h>  : 시스템 헤더 (표준 라이브러리)
      "myfile.h"  : 사용자 헤더 (프로젝트 파일)
    */

    printf("  ■ 헤더 파일 규칙\n");
    printf("    1. 반드시 include guard 사용 (#ifndef)\n");
    printf("    2. 선언만 넣기 (구현은 .c 에)\n");
    printf("    3. 헤더 이름 = 소스 파일 이름과 일치\n");
    printf("    4. 필요한 다른 헤더를 include\n\n");

    printf("  ■ extern 키워드\n");
    printf("    전역 변수를 여러 파일에서 공유할 때:\n");
    printf("    header.h: extern int count;  (선언)\n");
    printf("    source.c: int count = 0;     (정의)\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 4 — Makefile 기초
 * ========================================================================= */
void lesson4_makefile_basics(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 4 : Makefile 기초               │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ Make = 빌드 자동화 도구
      "어떤 파일이 바뀌었을 때 어떤 명령을 실행할지" 정의

    ★ 비유:
      Makefile = 요리 레시피 자동화
      "재료(소스)가 바뀌면 해당 요리(컴파일)만 다시 하세요"

    ★ Makefile 기본 문법:
      타겟: 의존성
      [TAB]명령어

    ★ 기본 Makefile 예:
      ┌──────────────────────────────────────────┐
      │ # 변수 정의                               │
      │ CC = gcc                                  │
      │ CFLAGS = -std=c11 -Wall -g                │
      │                                           │
      │ # 타겟: 의존성                             │
      │ program: main.o math.o                    │
      │ [TAB]$(CC) $(CFLAGS) -o program main.o math.o │
      │                                           │
      │ main.o: main.c math.h                     │
      │ [TAB]$(CC) $(CFLAGS) -c main.c            │
      │                                           │
      │ math.o: math.c math.h                     │
      │ [TAB]$(CC) $(CFLAGS) -c math.c            │
      │                                           │
      │ clean:                                    │
      │ [TAB]rm -f *.o program                    │
      └──────────────────────────────────────────┘
      ★ 들여쓰기는 반드시 TAB! (스페이스 불가)

    ★ Make 의 핵심 장점:
      바뀐 파일만 다시 컴파일 → 빌드 시간 절약!
    */

    printf("  ■ Makefile 핵심 규칙\n");
    printf("    타겟: 의존성\n");
    printf("    [TAB]명령어\n\n");

    printf("  ■ 주요 make 명령\n");
    printf("    make         → 첫 번째 타겟 빌드\n");
    printf("    make clean   → clean 타겟 실행\n");
    printf("    make -j4     → 4개 병렬 빌드\n");
    printf("    make -n      → 실행할 명령만 출력 (dry run)\n\n");

    printf("  ■ 자동 변수\n");
    printf("    $@  → 현재 타겟 이름\n");
    printf("    $<  → 첫 번째 의존성\n");
    printf("    $^  → 모든 의존성\n");
    printf("    $*  → 확장자를 뺀 파일명\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 5 — Makefile 고급
 * ========================================================================= */
void lesson5_makefile_advanced(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 5 : Makefile 고급               │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 패턴 규칙 (Pattern Rules):
      %.o: %.c
      [TAB]$(CC) $(CFLAGS) -c $< -o $@

      → 모든 .c 파일을 .o 로 컴파일하는 일반 규칙

    ★ 실전 Makefile:
      ┌──────────────────────────────────────────┐
      │ CC = gcc                                  │
      │ CFLAGS = -std=c11 -Wall -Wextra -g        │
      │ SRCS = $(wildcard src/*.c)                │
      │ OBJS = $(SRCS:.c=.o)                      │
      │ TARGET = myapp                            │
      │                                           │
      │ $(TARGET): $(OBJS)                        │
      │ [TAB]$(CC) $(CFLAGS) -o $@ $^             │
      │                                           │
      │ %.o: %.c                                  │
      │ [TAB]$(CC) $(CFLAGS) -c $< -o $@          │
      │                                           │
      │ .PHONY: clean test                        │
      │                                           │
      │ clean:                                    │
      │ [TAB]rm -f $(OBJS) $(TARGET)              │
      │                                           │
      │ test: $(TARGET)                           │
      │ [TAB]./$(TARGET) --test                   │
      └──────────────────────────────────────────┘

    ★ .PHONY = "이것은 파일이 아니라 명령 이름이다"
      .PHONY: clean → clean 이라는 파일이 있어도
                      make clean 은 항상 실행됨

    ★ 유용한 함수:
      $(wildcard *.c)     → 패턴에 맞는 파일 목록
      $(patsubst .c,.o,)  → 패턴 치환
      $(SRCS:.c=.o)       → .c 를 .o 로 바꾸기
    */

    printf("  ■ 패턴 규칙\n");
    printf("    %%.o: %%.c                     ← 모든 .c → .o\n");
    printf("    [TAB]$(CC) $(CFLAGS) -c $< -o $@\n\n");

    printf("  ■ .PHONY 타겟\n");
    printf("    .PHONY: clean test all\n");
    printf("    → 파일이 아닌 명령어 이름임을 선언\n\n");

    printf("  ■ 의존성 자동 생성\n");
    printf("    gcc -MMD -MP -c main.c\n");
    printf("    → main.d 파일 생성 (헤더 의존성 자동 추적)\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 6 — CMake 소개
 * ========================================================================= */
void lesson6_cmake_intro(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 6 : CMake 소개                  │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ CMake = 크로스 플랫폼 빌드 시스템 생성기
      Makefile 을 직접 만드는 대신,
      CMakeLists.txt 를 작성하면 CMake 가 Makefile 을 자동 생성

    ★ 비유:
      Makefile = 직접 설계도를 그리는 것
      CMake   = "이 건물의 조건만 말하면 설계도를 그려주는 AI"

    ★ CMake vs Make:
    ┌──────────────┬──────────────────┬──────────────────┐
    │              │ Make             │ CMake            │
    ├──────────────┼──────────────────┼──────────────────┤
    │ 설정 파일    │ Makefile         │ CMakeLists.txt   │
    │ 크로스 플랫폼│ 어려움           │ 자동 지원        │
    │ IDE 연동     │ 제한적           │ 우수             │
    │ 학습 난이도  │ 보통             │ 보통~높음        │
    │ 용도         │ 단순 프로젝트    │ 복잡한 프로젝트  │
    └──────────────┴──────────────────┴──────────────────┘

    ★ 기본 CMakeLists.txt:
      ┌──────────────────────────────────────────┐
      │ cmake_minimum_required(VERSION 3.10)      │
      │ project(MyApp C)                          │
      │                                           │
      │ set(CMAKE_C_STANDARD 11)                  │
      │                                           │
      │ add_executable(myapp                      │
      │     src/main.c                            │
      │     src/math_util.c                       │
      │     src/string_util.c                     │
      │ )                                         │
      │                                           │
      │ target_include_directories(myapp          │
      │     PRIVATE include                       │
      │ )                                         │
      └──────────────────────────────────────────┘

    ★ CMake 사용법:
      mkdir build && cd build
      cmake ..
      make
    */

    printf("  ■ CMake 기본 사용법\n");
    printf("    1. CMakeLists.txt 작성\n");
    printf("    2. mkdir build && cd build\n");
    printf("    3. cmake ..        ← Makefile 생성\n");
    printf("    4. make            ← 빌드\n\n");

    printf("  ■ CMake 핵심 명령어\n");
    printf("    cmake_minimum_required(VERSION 3.10)\n");
    printf("    project(이름 C)\n");
    printf("    add_executable(이름 소스파일들...)\n");
    printf("    target_link_libraries(이름 라이브러리)\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 7 — 실전: 프로젝트 구조 설계
 * ========================================================================= */
void lesson7_practical(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 7 : 실전 — 프로젝트 구조        │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 실전 프로젝트 구조 (추천):
    ┌──────────────────────────────────┐
    │ calculator/                      │
    │ ├── CMakeLists.txt              │
    │ ├── Makefile                    │
    │ ├── include/                    │
    │ │   ├── calculator.h            │
    │ │   └── utils.h                 │
    │ ├── src/                        │
    │ │   ├── main.c                  │
    │ │   ├── calculator.c            │
    │ │   └── utils.c                 │
    │ ├── tests/                      │
    │ │   └── test_calculator.c       │
    │ └── build/  (빌드 출력)         │
    └──────────────────────────────────┘
    */

    printf("  ■ 추천 프로젝트 구조\n");
    printf("    include/   → 헤더 파일 (.h)\n");
    printf("    src/       → 소스 파일 (.c)\n");
    printf("    tests/     → 테스트 코드\n");
    printf("    build/     → 빌드 출력 (git 에 올리지 않음)\n\n");

    printf("  ■ .gitignore 에 넣을 것\n");
    printf("    build/\n");
    printf("    *.o\n");
    printf("    *.exe\n");
    printf("    *.out\n");

    /*
    ★ 빌드 시스템 체크리스트
    ─────────────────────────────────────
    □ 모든 소스 파일이 빌드에 포함되었는가?
    □ 헤더 파일 의존성이 올바른가?
    □ clean 타겟이 있는가?
    □ 컴파일 경고 옵션 (-Wall) 을 사용했는가?
    □ 디버그/릴리스 빌드를 구분했는가?
    □ 빌드 출력물을 git 에서 제외했는가?
    ─────────────────────────────────────
    */

    printf("\n");
}
