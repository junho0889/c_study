/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C 학습 16단계: 테스트 기초
  ─ 단위 테스트, assert 기반 테스트, 테스트 매크로, TDD ─

  테스트는 "코드가 올바르게 동작하는지 자동으로 확인하는 코드"입니다.
  C 에는 기본 테스트 프레임워크가 없으므로
  직접 만들어 사용하는 방법을 배웁니다.

  ■ 컴파일: gcc -std=c11 -Wall -o 16_test main.c
  ■ 실행:   ./16_test

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

/* =========================================================================
 *  미니 테스트 프레임워크
 * ========================================================================= */

/*
★ 테스트 매크로 설계:
  ASSERT_EQ(expected, actual)   → 같은지 확인
  ASSERT_NEQ(a, b)              → 다른지 확인
  ASSERT_TRUE(cond)             → 참인지 확인
  ASSERT_FALSE(cond)            → 거짓인지 확인
  ASSERT_STR_EQ(a, b)           → 문자열 같은지 확인
  RUN_TEST(func)                → 테스트 실행 + 결과 출력
*/

static int tests_run = 0;
static int tests_passed = 0;
static int tests_failed = 0;

#define ASSERT_EQ(expected, actual) \
    do { \
        if ((expected) == (actual)) { \
            /* 통과 */ \
        } else { \
            printf("    FAIL: %s:%d: expected %d, got %d\n", \
                   __FILE__, __LINE__, (int)(expected), (int)(actual)); \
            return 0; \
        } \
    } while(0)

#define ASSERT_NEQ(a, b) \
    do { \
        if ((a) != (b)) { /* 통과 */ } \
        else { \
            printf("    FAIL: %s:%d: values should differ\n", \
                   __FILE__, __LINE__); \
            return 0; \
        } \
    } while(0)

#define ASSERT_TRUE(cond) \
    do { \
        if (cond) { /* 통과 */ } \
        else { \
            printf("    FAIL: %s:%d: condition is false\n", \
                   __FILE__, __LINE__); \
            return 0; \
        } \
    } while(0)

#define ASSERT_FALSE(cond) \
    do { \
        if (!(cond)) { /* 통과 */ } \
        else { \
            printf("    FAIL: %s:%d: condition should be false\n", \
                   __FILE__, __LINE__); \
            return 0; \
        } \
    } while(0)

#define ASSERT_STR_EQ(expected, actual) \
    do { \
        if (strcmp((expected), (actual)) == 0) { /* 통과 */ } \
        else { \
            printf("    FAIL: %s:%d: expected \"%s\", got \"%s\"\n", \
                   __FILE__, __LINE__, (expected), (actual)); \
            return 0; \
        } \
    } while(0)

#define ASSERT_NEAR(expected, actual, epsilon) \
    do { \
        if (fabs((expected) - (actual)) <= (epsilon)) { /* 통과 */ } \
        else { \
            printf("    FAIL: %s:%d: expected ~%.4f, got %.4f\n", \
                   __FILE__, __LINE__, (double)(expected), (double)(actual)); \
            return 0; \
        } \
    } while(0)

#define RUN_TEST(test_func) \
    do { \
        tests_run++; \
        if (test_func()) { \
            tests_passed++; \
            printf("    PASS: %s\n", #test_func); \
        } else { \
            tests_failed++; \
        } \
    } while(0)


/* =========================================================================
 *  테스트할 함수들 (프로덕션 코드)
 * ========================================================================= */

int add(int a, int b) { return a + b; }
int subtract(int a, int b) { return a - b; }
int multiply(int a, int b) { return a * b; }

int safe_divide(int a, int b, int* result) {
    if (b == 0) return -1;
    *result = a / b;
    return 0;
}

int factorial(int n) {
    if (n < 0) return -1;
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

int is_palindrome(const char* str) {
    int len = (int)strlen(str);
    for (int i = 0; i < len / 2; i++) {
        if (str[i] != str[len - 1 - i]) return 0;
    }
    return 1;
}

int max_in_array(const int* arr, int n) {
    if (n <= 0) return 0;
    int max = arr[0];
    for (int i = 1; i < n; i++) {
        if (arr[i] > max) max = arr[i];
    }
    return max;
}

double average(const int* arr, int n) {
    if (n <= 0) return 0.0;
    int sum = 0;
    for (int i = 0; i < n; i++) sum += arr[i];
    return (double)sum / n;
}


void lesson1_why_test(void);
void lesson2_test_framework(void);
void lesson3_writing_tests(void);
void lesson4_edge_cases(void);
void lesson5_test_patterns(void);
void lesson6_tdd(void);
void lesson7_practical(void);

int main(void) {
    printf("========================================\n");
    printf("  C 16단계 : 테스트 기초\n");
    printf("========================================\n\n");

    lesson1_why_test();
    lesson2_test_framework();
    lesson3_writing_tests();
    lesson4_edge_cases();
    lesson5_test_patterns();
    lesson6_tdd();
    lesson7_practical();

    /* 최종 결과 */
    printf("  ═══════════════════════════════════\n");
    printf("  전체 결과: %d 실행, %d 성공, %d 실패\n",
           tests_run, tests_passed, tests_failed);
    printf("  ═══════════════════════════════════\n");

    printf("\n16단계 학습 완료!\n");
    return tests_failed > 0 ? 1 : 0;
}


/* =========================================================================
 *  레슨 1 — 왜 테스트가 필요한가?
 * ========================================================================= */
void lesson1_why_test(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 1 : 왜 테스트가 필요한가?       │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 테스트 = 코드가 예상대로 동작하는지 자동 확인

    ★ 비유:
      자동차 출고 전 검사와 같습니다.
      엔진, 브레이크, 조향 등을 하나하나 확인하듯
      함수 하나하나가 올바른 결과를 내는지 확인합니다.

    ★ 테스트가 필요한 이유:
    ┌────┬──────────────────────────────────────────┐
    │ #  │ 이유                                      │
    ├────┼──────────────────────────────────────────┤
    │ 1  │ 수정 후 기존 기능이 안 깨졌는지 확인      │
    │ 2  │ 버그를 빨리 찾을 수 있음                  │
    │ 3  │ 코드의 동작을 문서처럼 설명               │
    │ 4  │ 리팩토링할 때 안전망 역할                  │
    │ 5  │ 팀원과의 신뢰 (이 코드는 검증됨!)         │
    └────┴──────────────────────────────────────────┘

    ★ 테스트 종류:
      단위 테스트 (Unit Test)    → 함수 하나 검증
      통합 테스트 (Integration) → 여러 모듈 조합 검증
      시스템 테스트 (E2E)       → 전체 프로그램 검증
    */

    printf("  테스트 없이 코드를 고치는 것은\n");
    printf("  안전벨트 없이 운전하는 것과 같습니다.\n\n");
}


/* =========================================================================
 *  레슨 2 — 미니 테스트 프레임워크
 * ========================================================================= */
void lesson2_test_framework(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 2 : 미니 테스트 프레임워크      │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ C 에는 표준 테스트 프레임워크가 없음
      → 직접 만들거나 외부 라이브러리 사용

    ★ 외부 프레임워크:
    ┌────────────────┬──────────────────────────┐
    │ 이름           │ 특징                      │
    ├────────────────┼──────────────────────────┤
    │ CUnit          │ 구조화된 테스트 스위트    │
    │ Unity          │ 임베디드 친화적, 경량     │
    │ Check          │ fork 기반 격리 테스트     │
    │ CMocka         │ mock 지원                │
    │ 직접 만들기    │ 간단한 매크로로 충분      │
    └────────────────┴──────────────────────────┘

    ★ 우리의 미니 프레임워크 구조:
      - ASSERT_EQ : 값 비교
      - ASSERT_TRUE / FALSE : 조건 확인
      - ASSERT_STR_EQ : 문자열 비교
      - ASSERT_NEAR : 실수 근사 비교
      - RUN_TEST : 테스트 실행 + 통계
    */

    printf("  이 파일 상단에 정의된 매크로를 활용합니다.\n");
    printf("  RUN_TEST(func) 로 테스트를 실행하고,\n");
    printf("  ASSERT_EQ 등으로 결과를 검증합니다.\n\n");
}


/* =========================================================================
 *  레슨 3 — 테스트 작성하기
 * ========================================================================= */

/* ── 테스트 함수들 (1이면 성공, 0이면 실패) ── */
int test_add_basic(void) {
    ASSERT_EQ(5, add(2, 3));
    ASSERT_EQ(0, add(0, 0));
    ASSERT_EQ(-1, add(-3, 2));
    return 1;
}

int test_add_negative(void) {
    ASSERT_EQ(-5, add(-2, -3));
    ASSERT_EQ(0, add(-5, 5));
    return 1;
}

int test_subtract(void) {
    ASSERT_EQ(2, subtract(5, 3));
    ASSERT_EQ(-2, subtract(3, 5));
    ASSERT_EQ(0, subtract(7, 7));
    return 1;
}

int test_multiply(void) {
    ASSERT_EQ(15, multiply(3, 5));
    ASSERT_EQ(0, multiply(0, 100));
    ASSERT_EQ(-6, multiply(-2, 3));
    ASSERT_EQ(6, multiply(-2, -3));
    return 1;
}

void lesson3_writing_tests(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 3 : 테스트 작성하기             │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 좋은 테스트의 조건 (AAA 패턴):
      Arrange → 테스트 데이터 준비
      Act     → 테스트 대상 함수 호출
      Assert  → 결과 검증

    ★ 테스트 이름 관례:
      test_함수명_시나리오
      예: test_add_negative, test_divide_by_zero
    */

    printf("  ■ 산술 함수 테스트\n");
    RUN_TEST(test_add_basic);
    RUN_TEST(test_add_negative);
    RUN_TEST(test_subtract);
    RUN_TEST(test_multiply);

    printf("\n");
}


/* =========================================================================
 *  레슨 4 — 경계값 테스트
 * ========================================================================= */

int test_divide_normal(void) {
    int result;
    ASSERT_EQ(0, safe_divide(10, 3, &result));
    ASSERT_EQ(3, result);
    return 1;
}

int test_divide_by_zero(void) {
    int result;
    ASSERT_EQ(-1, safe_divide(10, 0, &result));
    return 1;
}

int test_factorial_basic(void) {
    ASSERT_EQ(1, factorial(0));
    ASSERT_EQ(1, factorial(1));
    ASSERT_EQ(120, factorial(5));
    ASSERT_EQ(720, factorial(6));
    return 1;
}

int test_factorial_negative(void) {
    ASSERT_EQ(-1, factorial(-1));
    ASSERT_EQ(-1, factorial(-100));
    return 1;
}

void lesson4_edge_cases(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 4 : 경계값 (Edge Case) 테스트  │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 경계값 테스트 = 극단적인 입력으로 테스트

    ★ 경계값 예시:
    ┌──────────────────┬──────────────────────────┐
    │ 상황             │ 테스트할 값               │
    ├──────────────────┼──────────────────────────┤
    │ 0으로 나누기     │ divide(10, 0)            │
    │ 빈 배열          │ max_in_array(arr, 0)     │
    │ 음수 입력        │ factorial(-1)            │
    │ NULL 포인터      │ func(NULL)               │
    │ 빈 문자열        │ is_palindrome("")        │
    │ 매우 큰 값       │ INT_MAX, INT_MIN         │
    │ 원소 1개 배열    │ sort(arr, 1)             │
    └──────────────────┴──────────────────────────┘
    */

    printf("  ■ 나눗셈 경계값 테스트\n");
    RUN_TEST(test_divide_normal);
    RUN_TEST(test_divide_by_zero);

    printf("\n  ■ 팩토리얼 경계값 테스트\n");
    RUN_TEST(test_factorial_basic);
    RUN_TEST(test_factorial_negative);

    printf("\n");
}


/* =========================================================================
 *  레슨 5 — 테스트 패턴
 * ========================================================================= */

int test_palindrome_yes(void) {
    ASSERT_TRUE(is_palindrome("aba"));
    ASSERT_TRUE(is_palindrome("abba"));
    ASSERT_TRUE(is_palindrome("a"));
    ASSERT_TRUE(is_palindrome(""));
    return 1;
}

int test_palindrome_no(void) {
    ASSERT_FALSE(is_palindrome("abc"));
    ASSERT_FALSE(is_palindrome("ab"));
    return 1;
}

int test_max_in_array_basic(void) {
    int arr[] = {3, 7, 1, 9, 4};
    ASSERT_EQ(9, max_in_array(arr, 5));
    return 1;
}

int test_max_in_array_single(void) {
    int arr[] = {42};
    ASSERT_EQ(42, max_in_array(arr, 1));
    return 1;
}

int test_average_basic(void) {
    int arr[] = {10, 20, 30};
    ASSERT_NEAR(20.0, average(arr, 3), 0.01);
    return 1;
}

void lesson5_test_patterns(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 5 : 테스트 패턴                 │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 테스트 작성 패턴:
    ┌──────────────────┬──────────────────────────────┐
    │ 패턴             │ 설명                          │
    ├──────────────────┼──────────────────────────────┤
    │ 정상 경로        │ 일반적인 입력으로 테스트      │
    │ 경계값           │ 극단적 입력 (0, 빈값, 최대값)│
    │ 에러 경로        │ 잘못된 입력에 에러 처리 확인  │
    │ 역 테스트        │ 결과가 거짓인 경우도 확인     │
    │ 조합 테스트      │ 여러 조건 조합                │
    └──────────────────┴──────────────────────────────┘

    ★ 테스트 격리:
      각 테스트는 독립적이어야 합니다.
      다른 테스트의 결과에 영향받으면 안 됩니다.
    */

    printf("  ■ 회문 검사 테스트\n");
    RUN_TEST(test_palindrome_yes);
    RUN_TEST(test_palindrome_no);

    printf("\n  ■ 배열 최댓값 테스트\n");
    RUN_TEST(test_max_in_array_basic);
    RUN_TEST(test_max_in_array_single);

    printf("\n  ■ 평균 테스트 (실수 비교)\n");
    RUN_TEST(test_average_basic);

    printf("\n");
}


/* =========================================================================
 *  레슨 6 — TDD 소개
 * ========================================================================= */
void lesson6_tdd(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 6 : TDD (Test-Driven Dev)      │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ TDD = Test-Driven Development (테스트 주도 개발)

    ★ TDD 사이클 (Red-Green-Refactor):

      ┌─────────────────────────────────┐
      │  1. RED    : 실패하는 테스트 작성│
      │             ↓                   │
      │  2. GREEN  : 테스트 통과하게 구현│
      │             ↓                   │
      │  3. REFACTOR: 코드 정리         │
      │             ↓                   │
      │       1로 돌아감                │
      └─────────────────────────────────┘

    ★ 비유:
      건축의 설계도(테스트)를 먼저 그리고,
      그 설계도에 맞게 건물(코드)을 짓는 것

    ★ TDD 의 장점:
      1. 코드 작성 전에 요구사항이 명확해짐
      2. 항상 테스트가 있는 코드가 만들어짐
      3. 과도한 설계를 방지 (필요한 것만 구현)
      4. 리팩토링에 자신감
    */

    printf("  ■ TDD 순서\n");
    printf("    1. 테스트를 먼저 작성 (이 시점엔 컴파일도 안 됨)\n");
    printf("    2. 컴파일되게 빈 함수를 만듦\n");
    printf("    3. 테스트가 통과하도록 구현\n");
    printf("    4. 코드를 깔끔하게 정리\n");
    printf("    5. 다음 테스트 작성 → 반복\n\n");

    printf("  ■ 예시\n");
    printf("    // 1단계: 테스트 먼저\n");
    printf("    ASSERT_EQ(6, multiply(2, 3));\n\n");
    printf("    // 2단계: 함수 구현\n");
    printf("    int multiply(int a, int b) { return a * b; }\n\n");
    printf("    // 3단계: 테스트 통과 확인!\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 7 — 실전: 종합 테스트 스위트
 * ========================================================================= */

/* 문자열 뒤집기 함수 (테스트 대상) */
void str_reverse(char* str) {
    int len = (int)strlen(str);
    for (int i = 0; i < len / 2; i++) {
        char t = str[i];
        str[i] = str[len - 1 - i];
        str[len - 1 - i] = t;
    }
}

int test_str_reverse_normal(void) {
    char s[] = "Hello";
    str_reverse(s);
    ASSERT_STR_EQ("olleH", s);
    return 1;
}

int test_str_reverse_single(void) {
    char s[] = "A";
    str_reverse(s);
    ASSERT_STR_EQ("A", s);
    return 1;
}

int test_str_reverse_empty(void) {
    char s[] = "";
    str_reverse(s);
    ASSERT_STR_EQ("", s);
    return 1;
}

int test_str_reverse_palindrome(void) {
    char s[] = "abcba";
    str_reverse(s);
    ASSERT_STR_EQ("abcba", s);
    return 1;
}

void lesson7_practical(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 7 : 실전 — 종합 테스트 스위트  │\n");
    printf("└──────────────────────────────────────┘\n\n");

    printf("  ■ 문자열 뒤집기 테스트\n");
    RUN_TEST(test_str_reverse_normal);
    RUN_TEST(test_str_reverse_single);
    RUN_TEST(test_str_reverse_empty);
    RUN_TEST(test_str_reverse_palindrome);

    /*
    ★ 테스트 체크리스트
    ─────────────────────────────────────
    □ 정상 입력을 테스트했는가?
    □ 경계값 (0, 빈값, 최대값) 을 테스트했는가?
    □ 에러 입력 (NULL, 음수) 을 테스트했는가?
    □ 각 테스트가 독립적인가?
    □ 테스트 이름이 무엇을 검증하는지 명확한가?
    □ 실수 비교에 ASSERT_NEAR 를 사용했는가?
    ─────────────────────────────────────
    */

    printf("\n");
}
