/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C 학습 08단계: 전처리기
  ─ #define, #ifdef, #ifndef, 매크로 함수, #pragma ─

  전처리기는 컴파일 전에 소스코드를 가공하는 "문장 치환 도구"입니다.
  매크로, 조건부 컴파일, 헤더 가드 등 C 프로그래밍의 기반을 배웁니다.

  ■ 컴파일: gcc -std=c11 -Wall -o 08_preproc main.c
  ■ 실행:   ./08_preproc

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#include <stdio.h>
#include <stdlib.h>

/* ── 레슨 1에서 사용할 매크로 상수 ── */
#define PI          3.14159265358979
#define MAX_SIZE    100
#define APP_NAME    "전처리기 학습기"
#define APP_VERSION "1.0.0"

/* ── 레슨 2에서 사용할 매크로 함수 ── */
#define SQUARE(x)       ((x) * (x))
#define MAX(a, b)       ((a) > (b) ? (a) : (b))
#define MIN(a, b)       ((a) < (b) ? (a) : (b))
#define ABS(x)          ((x) < 0 ? -(x) : (x))
#define SWAP(a, b, T)   do { T temp_ = (a); (a) = (b); (b) = temp_; } while(0)

/* ── 레슨 3에서 사용할 디버그 매크로 ── */
#define DEBUG_MODE

#ifdef DEBUG_MODE
    #define LOG(msg)    printf("[DEBUG] %s:%d: %s\n", __FILE__, __LINE__, msg)
#else
    #define LOG(msg)    /* 아무 것도 안 함 */
#endif

/* ── 레슨 4에서 사용할 매크로 ── */
#define PRINT_VAR(var)  printf("  " #var " = %d\n", var)
#define CONCAT(a, b)    a##b

void lesson1_define_constants(void);
void lesson2_macro_functions(void);
void lesson3_conditional_compilation(void);
void lesson4_advanced_macros(void);
void lesson5_predefined_macros(void);
void lesson6_header_guard(void);
void lesson7_common_mistakes(void);

int main(void) {
    printf("========================================\n");
    printf("  C 08단계 : 전처리기\n");
    printf("========================================\n\n");

    lesson1_define_constants();
    lesson2_macro_functions();
    lesson3_conditional_compilation();
    lesson4_advanced_macros();
    lesson5_predefined_macros();
    lesson6_header_guard();
    lesson7_common_mistakes();

    printf("\n08단계 학습 완료!\n");
    return 0;
}


/* =========================================================================
 *  레슨 1 — #define 상수
 * ========================================================================= */
void lesson1_define_constants(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 1 : #define 상수               │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ #define 이란?
      컴파일 전에 "이 이름이 보이면 이 값으로 바꿔치기" 하는 지시문

    ★ 비유:
      워드프로세서의 "찾아 바꾸기" 기능과 같습니다.
      PI 라고 쓰면 컴파일 전에 3.14159... 로 바뀝니다.

    ★ #define vs const 비교:
    ┌────────────────┬───────────────────┬───────────────────┐
    │                │ #define           │ const              │
    ├────────────────┼───────────────────┼───────────────────┤
    │ 처리 시점      │ 전처리기 (컴파일전)│ 컴파일러           │
    │ 타입 검사      │ 없음              │ 있음               │
    │ 디버깅         │ 이름 안 보임      │ 이름 보임          │
    │ 스코프         │ 파일 전체         │ 선언 위치부터      │
    │ 메모리         │ 없음 (치환)       │ 있음               │
    └────────────────┴───────────────────┴───────────────────┘

    ★ 관례: 매크로 이름은 모두 대문자 + 밑줄 (MAX_SIZE, PI 등)
    */

    printf("  ■ 매크로 상수 사용 예\n");
    printf("    앱 이름   : %s\n", APP_NAME);
    printf("    앱 버전   : %s\n", APP_VERSION);
    printf("    PI 값     : %.15f\n", PI);
    printf("    MAX_SIZE  : %d\n", MAX_SIZE);

    double radius = 5.0;
    double area = PI * radius * radius;
    printf("    반지름 %.1f 인 원의 넓이: %.2f\n", radius, area);

    printf("\n");
}


/* =========================================================================
 *  레슨 2 — 매크로 함수
 * ========================================================================= */
void lesson2_macro_functions(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 2 : 매크로 함수                 │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 매크로 함수란?
      인자를 받아서 코드를 치환하는 매크로
      함수처럼 보이지만 진짜 함수가 아님!

    ★ 비유:
      매크로 함수 = "문장 틀" (빈칸에 값을 끼워 넣어서 문장 완성)
      진짜 함수   = "계산기" (입력을 받아 결과를 돌려줌)

    ★ 매크로 함수에서 괄호가 중요한 이유:
      #define SQUARE(x)  x * x        ← 위험!
      SQUARE(3+1)  → 3+1 * 3+1 → 3+3+1 = 7  (기대: 16)

      #define SQUARE(x)  ((x) * (x))  ← 안전!
      SQUARE(3+1)  → ((3+1) * (3+1)) → 4*4 = 16  (정확!)
    */

    printf("  ■ SQUARE 매크로\n");
    int n = 5;
    printf("    SQUARE(%d) = %d\n", n, SQUARE(n));
    printf("    SQUARE(3+1) = %d (괄호 덕에 정확)\n", SQUARE(3 + 1));

    printf("\n  ■ MAX / MIN 매크로\n");
    int a = 10, b = 25;
    printf("    MAX(%d, %d) = %d\n", a, b, MAX(a, b));
    printf("    MIN(%d, %d) = %d\n", a, b, MIN(a, b));

    printf("\n  ■ ABS 매크로\n");
    int x = -7;
    printf("    ABS(%d) = %d\n", x, ABS(x));

    printf("\n  ■ SWAP 매크로\n");
    int p = 100, q = 200;
    printf("    바꾸기 전: p=%d, q=%d\n", p, q);
    SWAP(p, q, int);
    printf("    바꾼 후 : p=%d, q=%d\n", p, q);

    /*
    ★ do { ... } while(0) 패턴:
      여러 줄 매크로를 안전하게 감싸는 관용 표현입니다.
      if 문 안에서도 세미콜론과 충돌 없이 동작합니다.
    */

    printf("\n");
}


/* =========================================================================
 *  레슨 3 — 조건부 컴파일
 * ========================================================================= */
void lesson3_conditional_compilation(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 3 : 조건부 컴파일               │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 조건부 컴파일 지시문:
    ┌──────────────────┬──────────────────────────────────┐
    │ 지시문           │ 의미                              │
    ├──────────────────┼──────────────────────────────────┤
    │ #ifdef NAME      │ NAME 이 정의되어 있으면           │
    │ #ifndef NAME     │ NAME 이 정의되지 않았으면         │
    │ #if 조건         │ 조건이 참이면                     │
    │ #elif 조건       │ 이전이 거짓이고 이 조건이 참이면  │
    │ #else            │ 위 조건이 모두 거짓이면           │
    │ #endif           │ 조건부 블록 끝                    │
    │ #undef NAME      │ NAME 정의 해제                   │
    └──────────────────┴──────────────────────────────────┘

    ★ 비유:
      조건부 컴파일 = "레시피에서 재료에 따라 다른 조리법 선택"
      채식주의자용이면 이 코드, 아니면 저 코드
    */

    /* ── #ifdef / #ifndef 예제 ── */
    printf("  ■ DEBUG_MODE 활성화 여부\n");
#ifdef DEBUG_MODE
    printf("    DEBUG_MODE 가 정의되어 있습니다!\n");
    LOG("이것은 디버그 로그입니다");
#else
    printf("    DEBUG_MODE 가 정의되어 있지 않습니다.\n");
#endif

    /* ── 플랫폼별 분기 예제 (설명용) ── */
    printf("\n  ■ 플랫폼별 조건 컴파일 (개념)\n");
#if defined(_WIN32)
    printf("    Windows 환경에서 실행 중\n");
#elif defined(__linux__)
    printf("    Linux 환경에서 실행 중\n");
#elif defined(__APPLE__)
    printf("    macOS 환경에서 실행 중\n");
#else
    printf("    알 수 없는 플랫폼\n");
#endif

    /* ── 버전별 기능 분기 ── */
    printf("\n  ■ 버전별 기능 분기\n");
#define FEATURE_LEVEL 2

#if FEATURE_LEVEL >= 3
    printf("    고급 기능 활성화\n");
#elif FEATURE_LEVEL >= 2
    printf("    중급 기능 활성화 (현재 레벨: %d)\n", FEATURE_LEVEL);
#else
    printf("    기본 기능만 활성화\n");
#endif

    printf("\n");
}


/* =========================================================================
 *  레슨 4 — 고급 매크로 기법
 * ========================================================================= */
void lesson4_advanced_macros(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 4 : 고급 매크로 기법            │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 문자열화 연산자 (#):
      매크로 인자를 "문자열"로 바꿈
      #define PRINT_VAR(var) printf(#var " = %d", var)
      PRINT_VAR(score) → printf("score" " = %d", score)

    ★ 토큰 붙이기 연산자 (##):
      두 토큰을 하나로 합침
      #define CONCAT(a, b)  a##b
      CONCAT(my, Var) → myVar

    ★ 가변 인자 매크로 (__VA_ARGS__):
      #define LOG(fmt, ...)  printf(fmt, __VA_ARGS__)
    */

    /* ── # (문자열화) 사용 ── */
    printf("  ■ # 연산자 (문자열화)\n");
    int score = 95;
    int count = 42;
    PRINT_VAR(score);       /* → printf("score = %d\n", score) */
    PRINT_VAR(count);

    /* ── ## (토큰 붙이기) 사용 ── */
    printf("\n  ■ ## 연산자 (토큰 붙이기)\n");
    int CONCAT(my, Number) = 777;   /* → int myNumber = 777; */
    printf("  myNumber = %d\n", myNumber);

    /* ── 여러 줄 매크로 ── */
    printf("\n  ■ 여러 줄 매크로 (백슬래시로 연결)\n");
    /*
      #define PRINT_HEADER(title)   \
          printf("==========\n");   \
          printf("  %s\n", title);  \
          printf("==========\n")

      줄 끝에 \ 를 붙이면 다음 줄로 이어집니다.
    */
    printf("    백슬래시(\\)로 여러 줄을 하나의 매크로로 연결 가능\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 5 — 미리 정의된 매크로
 * ========================================================================= */
void lesson5_predefined_macros(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 5 : 미리 정의된 매크로          │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ C 표준이 제공하는 미리 정의된 매크로:
    ┌────────────────┬───────────────────────────────┐
    │ 매크로         │ 설명                           │
    ├────────────────┼───────────────────────────────┤
    │ __FILE__       │ 현재 소스 파일 이름            │
    │ __LINE__       │ 현재 줄 번호                   │
    │ __DATE__       │ 컴파일 날짜 (Mmm dd yyyy)     │
    │ __TIME__       │ 컴파일 시각 (hh:mm:ss)        │
    │ __func__       │ 현재 함수 이름 (C99+)         │
    │ __STDC__       │ 표준 C 준수 시 1              │
    │ __STDC_VERSION__│ C 표준 버전                   │
    └────────────────┴───────────────────────────────┘
    */

    printf("  ■ 미리 정의된 매크로 출력\n");
    printf("    __FILE__ = %s\n", __FILE__);
    printf("    __LINE__ = %d\n", __LINE__);
    printf("    __DATE__ = %s\n", __DATE__);
    printf("    __TIME__ = %s\n", __TIME__);
    printf("    __func__ = %s\n", __func__);

#ifdef __STDC__
    printf("    __STDC__ = %d (표준 C 준수)\n", __STDC__);
#endif

#ifdef __STDC_VERSION__
    printf("    __STDC_VERSION__ = %ldL\n", __STDC_VERSION__);
    #if __STDC_VERSION__ >= 201112L
        printf("    → C11 이상입니다!\n");
    #elif __STDC_VERSION__ >= 199901L
        printf("    → C99 입니다.\n");
    #endif
#endif

    printf("\n");
}


/* =========================================================================
 *  레슨 6 — 헤더 가드 (Include Guard)
 * ========================================================================= */
void lesson6_header_guard(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 6 : 헤더 가드                   │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 헤더 가드란?
      같은 헤더 파일이 여러 번 #include 되는 것을 방지하는 패턴

    ★ 문제 상황:
      a.h 가 b.h 를 include 하고,
      main.c 가 a.h 와 b.h 를 모두 include 하면
      → b.h 의 내용이 두 번 포함됨 → 중복 선언 에러!

    ★ 해결: 헤더 가드 패턴

      ┌──────────────────────────────────┐
      │ // myheader.h                    │
      │ #ifndef MYHEADER_H               │
      │ #define MYHEADER_H               │
      │                                  │
      │ // 헤더 내용                      │
      │ void my_function(void);          │
      │                                  │
      │ #endif // MYHEADER_H             │
      └──────────────────────────────────┘

    ★ #pragma once (비표준이지만 널리 지원):

      ┌──────────────────────────────────┐
      │ // myheader.h                    │
      │ #pragma once                     │
      │                                  │
      │ void my_function(void);          │
      └──────────────────────────────────┘

    ★ 비유:
      헤더 가드 = 출입증 시스템
      "이미 들어온 사람은 다시 안 들여보냄"
    */

    printf("  ■ 헤더 가드 패턴 (개념 설명)\n");
    printf("    #ifndef HEADER_H  → 아직 정의 안 됐으면\n");
    printf("    #define HEADER_H  → 정의하고\n");
    printf("    ...내용...         → 헤더 내용 포함\n");
    printf("    #endif            → 끝\n");
    printf("    두 번째 include 시 이미 정의되어 있으므로 건너뜀!\n\n");

    printf("  ■ #pragma once (간편 대안)\n");
    printf("    파일 맨 위에 #pragma once 한 줄이면 끝\n");
    printf("    대부분의 컴파일러가 지원하지만 표준은 아님\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 7 — 매크로 사용 시 흔한 실수
 * ========================================================================= */
void lesson7_common_mistakes(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 7 : 매크로 실수 모음            │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 매크로 5대 실수

    ┌────┬──────────────────────────┬───────────────────────────┐
    │ #  │ 실수                     │ 올바른 방법               │
    ├────┼──────────────────────────┼───────────────────────────┤
    │ 1  │ 매크로 뒤에 ; 붙이기     │ #define PI 3.14 (;없이)   │
    │ 2  │ 인자에 괄호 누락         │ ((x) * (x)) 로 감싸기     │
    │ 3  │ 부작용 있는 인자         │ SQUARE(i++) 금지!         │
    │ 4  │ 여러줄 매크로 중괄호 누락│ do{...}while(0) 사용      │
    │ 5  │ 매크로 이름 충돌         │ 접두사 사용 (MY_MAX 등)   │
    └────┴──────────────────────────┴───────────────────────────┘
    */

    /* ── 실수 1: 세미콜론 실수 ── */
    printf("  ■ 실수 1: #define 뒤에 세미콜론\n");
    printf("    #define SIZE 10;  ← 위험!\n");
    printf("    int arr[SIZE];    → int arr[10;]; → 문법 에러!\n\n");

    /* ── 실수 2: 괄호 누락 ── */
    printf("  ■ 실수 2: 괄호 누락\n");
    printf("    #define DOUBLE(x) x*2\n");
    printf("    DOUBLE(3+1) → 3+1*2 → 5 (기대: 8)\n");
    printf("    올바른: #define DOUBLE(x) ((x)*2)\n\n");

    /* ── 실수 3: 부작용 있는 인자 ── */
    printf("  ■ 실수 3: 부작용 있는 인자 (side effect)\n");
    printf("    SQUARE(i++) → ((i++) * (i++)) → i 가 2번 증가!\n");
    printf("    ★ 매크로 인자에 ++, --, 함수호출 넣지 마세요!\n\n");

    /* ── 실수 4: 여러줄 매크로 ── */
    printf("  ■ 실수 4: 여러줄 매크로를 중괄호만으로 감싸기\n");
    printf("    if (ok) MY_MACRO();  ← else 와 엉킬 수 있음\n");
    printf("    해결: do { ... } while(0) 패턴 사용\n\n");

    /*
    ★ 전처리기 체크리스트
    ─────────────────────────────────────
    □ 매크로 이름은 대문자 + 밑줄인가?
    □ 매크로 함수에 괄호를 충분히 넣었는가?
    □ 헤더 파일에 include guard 가 있는가?
    □ 매크로 대신 const/inline 을 쓸 수 있는가? (가능하면 추천)
    □ 부작용 있는 표현식을 매크로 인자로 넣지 않았는가?
    ─────────────────────────────────────
    */

    printf("\n");
}
