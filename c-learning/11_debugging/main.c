/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C 학습 11단계: 디버깅
  ─ assert, 디버그 매크로, gdb, valgrind, 방어적 프로그래밍 ─

  버그를 고치는 능력은 코드를 짜는 능력만큼 중요합니다.
  이 단계에서는 체계적인 디버깅 방법과 도구를 익힙니다.

  ■ 컴파일: gcc -std=c11 -Wall -Wextra -g -o 11_debug main.c
  ■ 실행:   ./11_debug
  ■ gdb:    gdb ./11_debug

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

/* ── 디버그 로그 매크로 ── */
#define DEBUG 1

#if DEBUG
    #define DBG_LOG(fmt, ...) \
        fprintf(stderr, "[DEBUG %s:%d] " fmt "\n", \
                __FILE__, __LINE__, ##__VA_ARGS__)
#else
    #define DBG_LOG(fmt, ...) ((void)0)
#endif

#define CHECK(cond, msg) \
    do { \
        if (!(cond)) { \
            fprintf(stderr, "[ERROR %s:%d] %s\n", __FILE__, __LINE__, msg); \
            return; \
        } \
    } while(0)

void lesson1_debug_mindset(void);
void lesson2_printf_debugging(void);
void lesson3_assert(void);
void lesson4_debug_macros(void);
void lesson5_gdb_basics(void);
void lesson6_valgrind(void);
void lesson7_defensive_programming(void);
void lesson8_practical(void);

int main(void) {
    printf("========================================\n");
    printf("  C 11단계 : 디버깅\n");
    printf("========================================\n\n");

    lesson1_debug_mindset();
    lesson2_printf_debugging();
    lesson3_assert();
    lesson4_debug_macros();
    lesson5_gdb_basics();
    lesson6_valgrind();
    lesson7_defensive_programming();
    lesson8_practical();

    printf("\n11단계 학습 완료!\n");
    return 0;
}


/* =========================================================================
 *  레슨 1 — 디버깅 마인드셋
 * ========================================================================= */
void lesson1_debug_mindset(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 1 : 디버깅 마인드셋             │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 디버깅 = 버그를 찾고 고치는 체계적 과정

    ★ 비유:
      디버깅 = 의사의 진단
      1. 증상 관찰 (어떤 에러? 어떤 입력?)
      2. 가설 수립 ("이 변수가 잘못된 것 같다")
      3. 검사 (값 출력, 단계 실행)
      4. 원인 확정 & 치료 (수정)
      5. 재발 방지 (테스트 추가)

    ★ 디버깅 5단계:
    ┌────┬──────────────────┬──────────────────────────┐
    │ #  │ 단계             │ 행동                      │
    ├────┼──────────────────┼──────────────────────────┤
    │ 1  │ 재현             │ 버그를 확실히 재현한다    │
    │ 2  │ 격리             │ 어디서 발생하는지 좁힌다  │
    │ 3  │ 추적             │ 변수 값을 단계별 확인     │
    │ 4  │ 수정             │ 원인을 고친다             │
    │ 5  │ 검증             │ 고친 후 다시 테스트한다   │
    └────┴──────────────────┴──────────────────────────┘

    ★ 흔한 버그 유형:
      - Off-by-one (경계값 1 차이)
      - Null pointer dereference
      - Buffer overflow
      - Memory leak
      - Use after free
      - Uninitialized variable
      - Integer overflow
    */

    printf("  디버깅은 감(感)이 아니라 과학적 과정입니다.\n");
    printf("  '왜 안 되지?' 가 아니라 '어디서 값이 달라지지?' 를 추적하세요.\n\n");
}


/* =========================================================================
 *  레슨 2 — printf 디버깅
 * ========================================================================= */
void lesson2_printf_debugging(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 2 : printf 디버깅               │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ printf 디버깅 = 가장 기본적인 디버깅 방법
      값을 출력해서 프로그램의 실행 흐름을 추적

    ★ 좋은 printf 디버깅 팁:
      1. 변수 이름도 함께 출력
      2. 함수 진입/퇴장 표시
      3. 조건문 분기 표시
      4. stderr 사용 (stdout 과 분리)
    */

    printf("  ■ 버그가 있는 평균 계산 함수\n");

    /* 의도적으로 "0으로 나누기" 가능한 코드 */
    int scores[] = {80, 90, 70};
    int count = 3;

    /* ── 디버깅 출력으로 값 추적 ── */
    DBG_LOG("count = %d", count);

    int total = 0;
    for (int i = 0; i < count; i++) {
        total += scores[i];
        DBG_LOG("scores[%d] = %d, total = %d", i, scores[i], total);
    }

    if (count > 0) {
        int avg = total / count;
        DBG_LOG("average = %d", avg);
        printf("    평균: %d\n", avg);
    } else {
        DBG_LOG("count 가 0! 나누기 불가!");
        printf("    ★ count 가 0이므로 평균 계산 불가\n");
    }

    printf("\n  ■ stderr vs stdout\n");
    printf("    stdout: 일반 출력 (버퍼링 됨)\n");
    printf("    stderr: 에러/디버그 출력 (즉시 출력)\n");
    printf("    → 프로그램 충돌 시 stdout 은 출력 안 될 수 있지만\n");
    printf("      stderr 는 즉시 출력되므로 더 안전\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 3 — assert
 * ========================================================================= */
void lesson3_assert(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 3 : assert (가정 검증)          │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ assert(조건)
      - 조건이 참이면 → 아무 일 없음
      - 조건이 거짓이면 → 프로그램 즉시 중단 + 에러 메시지

    ★ 비유:
      assert = "보안 검문소"
      통과 조건을 만족하면 지나가고,
      못 만족하면 즉시 차단합니다.

    ★ assert vs if 의 차이:
    ┌───────────────┬────────────────────┬───────────────────┐
    │               │ assert             │ if + 에러 처리     │
    ├───────────────┼────────────────────┼───────────────────┤
    │ 목적          │ 개발 중 가정 검증  │ 정상 에러 처리     │
    │ 릴리스 시     │ NDEBUG 로 제거     │ 그대로 유지        │
    │ 실패 시       │ 프로그램 중단      │ 복구 가능          │
    │ 용도          │ "절대 일어나면     │ "일어날 수 있는    │
    │               │  안 되는 상황"     │  에러 상황"        │
    └───────────────┴────────────────────┴───────────────────┘

    ★ 릴리스 빌드에서 assert 제거:
      gcc -DNDEBUG main.c   ← assert 가 모두 사라짐
    */

    printf("  ■ assert 사용 예\n");

    int* ptr = (int*)malloc(sizeof(int));
    assert(ptr != NULL);    /* 메모리 할당 실패 시 중단 */
    *ptr = 42;
    printf("    *ptr = %d (assert 통과)\n", *ptr);
    free(ptr);

    /* ── assert 로 전제 조건 검증 ── */
    int divisor = 3;
    assert(divisor != 0);   /* 0으로 나누기 방지 */
    printf("    10 / %d = %d (assert 통과)\n", divisor, 10 / divisor);

    printf("\n  ■ assert 에 넣으면 안 되는 것\n");
    printf("    assert(malloc(100));  ← 릴리스에서 malloc 자체가 사라짐!\n");
    printf("    ★ 부작용(side effect) 있는 표현식을 assert 에 넣지 마세요!\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 4 — 디버그 매크로
 * ========================================================================= */
void lesson4_debug_macros(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 4 : 디버그 매크로               │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 디버그 매크로를 만들어 사용하면:
      1. 파일명, 줄 번호가 자동 포함
      2. DEBUG 플래그로 켜고 끌 수 있음
      3. printf 를 일일이 지울 필요 없음

    ★ 이 파일 상단에 정의한 DBG_LOG 매크로:
      #if DEBUG
          #define DBG_LOG(fmt, ...) \
              fprintf(stderr, "[DEBUG %s:%d] " fmt "\n", \
                      __FILE__, __LINE__, ##__VA_ARGS__)
      #else
          #define DBG_LOG(fmt, ...) ((void)0)
      #endif

    ★ CHECK 매크로:
      조건이 거짓이면 에러 메시지 + return
      assert 와 달리 프로그램을 중단시키지 않음
    */

    printf("  ■ DBG_LOG 매크로 출력 (stderr)\n");
    int x = 42;
    DBG_LOG("x 의 값은 %d", x);
    DBG_LOG("이 메시지는 stderr 로 출력됩니다");
    printf("    (위 DBG_LOG 출력은 stderr 에 나옵니다)\n");

    printf("\n  ■ CHECK 매크로\n");
    printf("    함수 앞에서 전제 조건을 검사하는 패턴\n");
    printf("    CHECK(ptr != NULL, \"포인터가 NULL입니다\");\n");
    printf("    → 실패 시 에러 메시지 출력 + 함수 종료\n");

    printf("\n  ■ __FILE__, __LINE__ 활용\n");
    printf("    현재 파일: %s\n", __FILE__);
    printf("    현재 줄:   %d\n", __LINE__);
    printf("    → 에러 발생 위치를 정확히 알 수 있습니다\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 5 — gdb 기초
 * ========================================================================= */
void lesson5_gdb_basics(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 5 : gdb 디버거 기초             │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ gdb = GNU Debugger
      프로그램을 한 줄씩 실행하며 변수 값을 확인하는 도구

    ★ 비유:
      gdb = "프로그램의 슬로우 모션 재생기"
      원하는 지점에서 멈추고 모든 변수를 들여다볼 수 있습니다.

    ★ gdb 사용 준비:
      gcc -g main.c -o program    ← -g 플래그로 디버그 정보 포함!

    ★ gdb 핵심 명령어:
    ┌────────────────────┬──────────────────────────────────┐
    │ 명령어             │ 설명                              │
    ├────────────────────┼──────────────────────────────────┤
    │ gdb ./program      │ gdb 시작                         │
    │ run (r)            │ 프로그램 실행                     │
    │ break main (b)     │ main 에 중단점 설정               │
    │ break 42           │ 42번 줄에 중단점                  │
    │ next (n)           │ 다음 줄 실행 (함수 안 들어가지X)  │
    │ step (s)           │ 다음 줄 실행 (함수 안으로 들어감) │
    │ print x (p)        │ 변수 x 의 값 출력                │
    │ print *ptr         │ 포인터가 가리키는 값              │
    │ backtrace (bt)     │ 호출 스택 표시                    │
    │ continue (c)       │ 다음 중단점까지 계속 실행         │
    │ watch x            │ x 가 바뀔 때마다 멈춤            │
    │ info locals        │ 지역 변수 전부 출력               │
    │ quit (q)           │ gdb 종료                         │
    └────────────────────┴──────────────────────────────────┘

    ★ gdb 실전 예:
      $ gdb ./11_debug
      (gdb) break lesson1_debug_mindset
      (gdb) run
      (gdb) next
      (gdb) print scores[0]
      $1 = 80
      (gdb) continue
    */

    printf("  ■ gdb 핵심 명령어 (위 주석 참조)\n");
    printf("    run    → 실행\n");
    printf("    break  → 중단점 설정\n");
    printf("    next   → 다음 줄\n");
    printf("    step   → 함수 안으로\n");
    printf("    print  → 값 출력\n");
    printf("    bt     → 호출 스택\n\n");

    printf("  ■ gdb 팁\n");
    printf("    1. -g 플래그로 컴파일해야 줄 번호가 보입니다\n");
    printf("    2. 최적화(-O2 등)를 끄면 디버깅이 쉬워집니다\n");
    printf("    3. Segfault 발생 시 bt 로 충돌 위치 확인\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 6 — valgrind (메모리 검사)
 * ========================================================================= */
void lesson6_valgrind(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 6 : valgrind (메모리 검사)      │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ valgrind = 메모리 관련 버그를 찾아주는 도구 (Linux)

    ★ 비유:
      valgrind = "메모리 감사관"
      프로그램이 빌린 메모리를 제대로 돌려줬는지,
      빌리지 않은 메모리를 건드리지 않았는지 검사합니다.

    ★ 사용법:
      valgrind --leak-check=full ./program

    ★ valgrind 가 찾아주는 문제:
    ┌────┬──────────────────────────────────────┐
    │ #  │ 찾아주는 문제                         │
    ├────┼──────────────────────────────────────┤
    │ 1  │ Memory Leak (메모리 누수)             │
    │ 2  │ Use after free (해제 후 사용)         │
    │ 3  │ Invalid read/write (범위 밖 접근)     │
    │ 4  │ Double free (이중 해제)               │
    │ 5  │ Uninitialized value (초기화 안 된 값) │
    │ 6  │ Mismatched free (malloc/free 짝 불일치)│
    └────┴──────────────────────────────────────┘

    ★ valgrind 출력 예:
      ==12345== 4 bytes in 1 blocks are definitely lost
      ==12345==    at malloc (in ...)
      ==12345==    by main (main.c:42)

    ★ Windows 대안:
      - Dr. Memory
      - AddressSanitizer (gcc -fsanitize=address)
    */

    printf("  ■ 메모리 누수 예시 (valgrind 로 검출)\n");
    printf("    int* p = malloc(100);\n");
    printf("    // free(p) 를 안 하면 → memory leak!\n\n");

    /* ── AddressSanitizer (ASan) ── */
    printf("  ■ AddressSanitizer (모든 OS 지원)\n");
    printf("    gcc -fsanitize=address -g main.c -o program\n");
    printf("    ./program\n");
    printf("    → 메모리 에러 발생 시 상세 보고서 출력\n\n");

    printf("  ■ 검출 가능한 예:\n");
    printf("    - heap-buffer-overflow\n");
    printf("    - stack-buffer-overflow\n");
    printf("    - use-after-free\n");
    printf("    - double-free\n");
    printf("    - memory leak\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 7 — 방어적 프로그래밍
 * ========================================================================= */
void lesson7_defensive_programming(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 7 : 방어적 프로그래밍           │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 방어적 프로그래밍 = 버그를 미리 방지하는 코딩 습관

    ★ 비유:
      안전벨트를 매는 것과 같습니다.
      사고(버그)가 안 나면 좋지만,
      나더라도 피해를 최소화합니다.

    ★ 방어적 프로그래밍 원칙:
    ┌────┬───────────────────────────────────────┐
    │ #  │ 원칙                                   │
    ├────┼───────────────────────────────────────┤
    │ 1  │ 함수 시작에서 입력값 검증              │
    │ 2  │ 포인터 사용 전 NULL 검사               │
    │ 3  │ 배열 인덱스 범위 확인                  │
    │ 4  │ malloc 반환값 확인                     │
    │ 5  │ 0 으로 나누기 방지                     │
    │ 6  │ 변수를 선언 즉시 초기화                │
    │ 7  │ free 후 NULL 대입                      │
    │ 8  │ 컴파일러 경고를 모두 켜기 (-Wall)      │
    └────┴───────────────────────────────────────┘
    */

    /* ── 방어적 나눗셈 함수 ── */
    printf("  ■ 방어적 나눗셈 함수\n");

    /* 나쁜 코드 */
    printf("    나쁜: return a / b;  ← b 가 0 이면 충돌!\n");

    /* 좋은 코드 */
    int a = 10, b = 0;
    if (b != 0) {
        printf("    결과: %d\n", a / b);
    } else {
        printf("    좋은: b 가 0 이므로 나누기 건너뜀\n");
    }

    /* ── -Wall -Wextra 경고 ── */
    printf("\n  ■ 컴파일러 경고 옵션\n");
    printf("    -Wall    : 주요 경고 활성화\n");
    printf("    -Wextra  : 추가 경고 활성화\n");
    printf("    -Werror  : 경고를 에러로 취급\n");
    printf("    -pedantic: 표준 엄격 준수\n");
    printf("    ★ 경고는 무시하지 말고 모두 고치세요!\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 8 — 실전: 안전한 배열 함수
 * ========================================================================= */

/* 안전한 배열 평균 계산 (모든 에러 처리 포함) */
int safe_average(const int* arr, int size, double* result) {
    /* 전제 조건 검사 */
    if (arr == NULL) {
        DBG_LOG("arr 이 NULL 입니다");
        return -1;   /* 에러 코드 반환 */
    }
    if (size <= 0) {
        DBG_LOG("size 가 %d (0 이하)", size);
        return -2;
    }
    if (result == NULL) {
        DBG_LOG("result 가 NULL 입니다");
        return -3;
    }

    long long total = 0;    /* 오버플로 방지를 위해 long long */
    for (int i = 0; i < size; i++) {
        total += arr[i];
    }
    *result = (double)total / size;

    DBG_LOG("계산 완료: total=%lld, size=%d, avg=%.2f",
            total, size, *result);
    return 0;   /* 성공 */
}

void lesson8_practical(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 8 : 실전 — 안전한 배열 함수     │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /* ── 정상 호출 ── */
    printf("  ■ 정상 호출\n");
    int scores[] = {85, 92, 78, 95, 88};
    double avg;
    int err = safe_average(scores, 5, &avg);
    if (err == 0) {
        printf("    평균: %.2f\n", avg);
    }

    /* ── NULL 배열 ── */
    printf("\n  ■ NULL 배열 전달\n");
    err = safe_average(NULL, 5, &avg);
    printf("    반환값: %d (에러 코드 -1)\n", err);

    /* ── size 0 ── */
    printf("\n  ■ size = 0 전달\n");
    err = safe_average(scores, 0, &avg);
    printf("    반환값: %d (에러 코드 -2)\n", err);

    /*
    ★ 디버깅 체크리스트
    ─────────────────────────────────────
    □ 컴파일 시 -Wall -Wextra -g 옵션을 사용했는가?
    □ 모든 경고를 수정했는가?
    □ 경계값 (0, -1, 최댓값) 으로 테스트했는가?
    □ NULL 입력으로 테스트했는가?
    □ valgrind / ASan 으로 메모리 검사했는가?
    □ assert 로 전제 조건을 검증했는가?
    ─────────────────────────────────────
    */

    printf("\n");
}
