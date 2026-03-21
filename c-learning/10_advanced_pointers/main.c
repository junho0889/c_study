/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C 학습 10단계: 고급 포인터
  ─ 이중 포인터, 함수 포인터, void*, 포인터 연산, 배열과 포인터 ─

  포인터는 C 의 핵심이자 가장 어려운 부분입니다.
  이 단계에서는 기초를 넘어 실전에서 꼭 필요한 고급 패턴을 다룹니다.

  ■ 컴파일: gcc -std=c11 -Wall -o 10_ptr main.c
  ■ 실행:   ./10_ptr

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void lesson1_pointer_to_pointer(void);
void lesson2_pointer_arithmetic(void);
void lesson3_array_and_pointer(void);
void lesson4_function_pointers(void);
void lesson5_void_pointer(void);
void lesson6_const_pointer(void);
void lesson7_common_mistakes(void);
void lesson8_practical(void);

int main(void) {
    printf("========================================\n");
    printf("  C 10단계 : 고급 포인터\n");
    printf("========================================\n\n");

    lesson1_pointer_to_pointer();
    lesson2_pointer_arithmetic();
    lesson3_array_and_pointer();
    lesson4_function_pointers();
    lesson5_void_pointer();
    lesson6_const_pointer();
    lesson7_common_mistakes();
    lesson8_practical();

    printf("\n10단계 학습 완료!\n");
    return 0;
}


/* =========================================================================
 *  레슨 1 — 이중 포인터 (Pointer to Pointer)
 * ========================================================================= */
void lesson1_pointer_to_pointer(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 1 : 이중 포인터                 │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 이중 포인터란?
      포인터의 주소를 저장하는 포인터

    ★ 비유:
      value  = 보물 (실제 값)
      ptr    = 보물 지도 (보물의 위치)
      ptr2   = 지도가 있는 서랍 (지도의 위치)

      **ptr2 → ptr2 가 가리키는 ptr → ptr 이 가리키는 value

    ★ 메모리 구조:
      ptr2 ──→ ptr ──→ value
      (주소)    (주소)   (실제 값)

    ★ 언제 쓰나?
      1. 함수에서 포인터 자체를 변경할 때
      2. 2차원 배열을 동적 할당할 때
      3. 문자열 배열 (char**)
    */

    int value = 42;
    int* ptr = &value;
    int** ptr2 = &ptr;

    printf("  ■ 이중 포인터 추적\n");
    printf("    value       = %d\n", value);
    printf("    *ptr        = %d\n", *ptr);
    printf("    **ptr2      = %d\n", **ptr2);
    printf("    &value      = %p\n", (void*)&value);
    printf("    ptr         = %p\n", (void*)ptr);
    printf("    &ptr        = %p\n", (void*)&ptr);
    printf("    ptr2        = %p\n", (void*)ptr2);

    /* ── 함수에서 포인터 변경 예제 ── */
    printf("\n  ■ 이중 포인터로 동적 할당 (함수 내부)\n");

    /* 함수가 포인터를 변경하려면 이중 포인터 필요 */
    /* allocate(&arr, 5) 처럼 사용 */
    int* arr = NULL;
    int** pp = &arr;
    *pp = (int*)malloc(sizeof(int) * 3);
    if (*pp != NULL) {
        (*pp)[0] = 10;
        (*pp)[1] = 20;
        (*pp)[2] = 30;
        printf("    arr[0]=%d, arr[1]=%d, arr[2]=%d\n",
               arr[0], arr[1], arr[2]);
        free(arr);
        arr = NULL;
    }

    printf("\n");
}


/* =========================================================================
 *  레슨 2 — 포인터 연산 (Pointer Arithmetic)
 * ========================================================================= */
void lesson2_pointer_arithmetic(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 2 : 포인터 연산                 │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 포인터 연산 규칙:
      포인터 + 1  → 다음 원소의 주소 (타입 크기만큼 이동)
      포인터 - 1  → 이전 원소의 주소
      p2 - p1     → 두 포인터 사이의 원소 개수

    ★ 비유:
      int 배열에서 포인터 +1 = "다음 방으로 이동"
      int 가 4바이트이면, 실제 주소는 +4 만큼 이동

    ★ 타입별 이동 크기:
    ┌──────────┬────────────┬──────────────────────┐
    │ 타입     │ sizeof     │ ptr+1 의 이동 바이트  │
    ├──────────┼────────────┼──────────────────────┤
    │ char*    │ 1          │ +1                    │
    │ int*     │ 4          │ +4                    │
    │ double*  │ 8          │ +8                    │
    │ 구조체*  │ 구조체크기 │ +구조체크기           │
    └──────────┴────────────┴──────────────────────┘
    */

    int arr[] = {10, 20, 30, 40, 50};
    int* p = arr;

    printf("  ■ 포인터로 배열 순회\n");
    for (int i = 0; i < 5; i++) {
        printf("    *(p + %d) = %d  (주소: %p)\n", i, *(p + i), (void*)(p + i));
    }

    /* ── 포인터 간 차이 ── */
    printf("\n  ■ 포인터 뺄셈\n");
    int* start = &arr[0];
    int* end = &arr[4];
    printf("    end - start = %td 칸\n", end - start);

    /* ── 배열 역순 순회 ── */
    printf("\n  ■ 포인터로 역순 순회\n");
    int* last = arr + 4;    /* 마지막 원소 */
    while (last >= arr) {
        printf("    %d ", *last);
        last--;
    }
    printf("\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 3 — 배열과 포인터의 관계
 * ========================================================================= */
void lesson3_array_and_pointer(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 3 : 배열과 포인터의 관계        │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 배열 이름 = 첫 원소의 주소 (대부분의 문맥에서)

    ★ 배열 ≠ 포인터 (중요한 차이!):
    ┌───────────────────┬──────────────┬───────────────┐
    │                   │ 배열         │ 포인터         │
    ├───────────────────┼──────────────┼───────────────┤
    │ sizeof            │ 전체 크기    │ 포인터 크기    │
    │ & 연산            │ 배열 주소    │ 포인터의 주소  │
    │ 대입 가능?        │ 불가         │ 가능           │
    │ 함수 전달 시      │ 포인터로 변환│ 그대로 전달    │
    └───────────────────┴──────────────┴───────────────┘

    ★ arr[i] 는 *(arr + i) 와 완전히 같습니다!
    */

    int arr[] = {100, 200, 300};

    printf("  ■ 배열 이름 = 첫 원소 주소\n");
    printf("    arr    = %p\n", (void*)arr);
    printf("    &arr[0]= %p\n", (void*)&arr[0]);

    printf("\n  ■ arr[i] == *(arr + i)\n");
    for (int i = 0; i < 3; i++) {
        printf("    arr[%d] = %d,  *(arr+%d) = %d\n",
               i, arr[i], i, *(arr + i));
    }

    printf("\n  ■ sizeof 차이\n");
    int* p = arr;
    printf("    sizeof(arr) = %zu (배열 전체)\n", sizeof(arr));
    printf("    sizeof(p)   = %zu (포인터 크기)\n", sizeof(p));

    /* ── 2차원 배열과 포인터 ── */
    printf("\n  ■ 2차원 배열\n");
    int matrix[2][3] = {
        {1, 2, 3},
        {4, 5, 6}
    };

    for (int r = 0; r < 2; r++) {
        for (int c = 0; c < 3; c++) {
            printf("    matrix[%d][%d] = %d\n", r, c, matrix[r][c]);
        }
    }

    printf("\n");
}


/* =========================================================================
 *  레슨 4 — 함수 포인터
 * ========================================================================= */

/* 콜백으로 사용할 함수들 */
int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }
int mul(int a, int b) { return a * b; }

/* 비교 함수 (qsort 용) */
int compare_asc(const void* a, const void* b) {
    return (*(const int*)a) - (*(const int*)b);
}
int compare_desc(const void* a, const void* b) {
    return (*(const int*)b) - (*(const int*)a);
}

void lesson4_function_pointers(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 4 : 함수 포인터                 │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 함수 포인터란?
      함수의 주소를 저장하는 변수
      → 어떤 함수를 호출할지 실행 시점에 결정 가능!

    ★ 선언 형식:
      반환타입 (*이름)(매개변수타입들);
      int (*fp)(int, int);  → int 2개 받고 int 반환하는 함수 포인터

    ★ 비유:
      함수 포인터 = "리모컨"
      리모컨에 어떤 기기를 등록하느냐에 따라
      같은 버튼으로 다른 동작을 실행

    ★ 용도:
      1. 콜백 함수 (callback)
      2. qsort 등 정렬 함수의 비교 기준
      3. 이벤트 핸들러
      4. 전략 패턴 (Strategy Pattern)
    */

    /* ── 기본 사용 ── */
    printf("  ■ 함수 포인터 기본\n");
    int (*operation)(int, int);     /* 함수 포인터 선언 */

    operation = add;
    printf("    add(10, 3) = %d\n", operation(10, 3));

    operation = sub;
    printf("    sub(10, 3) = %d\n", operation(10, 3));

    operation = mul;
    printf("    mul(10, 3) = %d\n", operation(10, 3));

    /* ── 함수 포인터 배열 (계산기) ── */
    printf("\n  ■ 함수 포인터 배열 (계산기)\n");
    int (*ops[])(int, int) = {add, sub, mul};
    const char* names[] = {"더하기", "빼기", "곱하기"};

    for (int i = 0; i < 3; i++) {
        printf("    %s: %d\n", names[i], ops[i](20, 5));
    }

    /* ── qsort 와 함수 포인터 ── */
    printf("\n  ■ qsort 와 함수 포인터\n");
    int numbers[] = {50, 10, 40, 20, 30};
    int n = 5;

    qsort(numbers, n, sizeof(int), compare_asc);
    printf("    오름차순: ");
    for (int i = 0; i < n; i++) printf("%d ", numbers[i]);
    printf("\n");

    qsort(numbers, n, sizeof(int), compare_desc);
    printf("    내림차순: ");
    for (int i = 0; i < n; i++) printf("%d ", numbers[i]);
    printf("\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 5 — void 포인터
 * ========================================================================= */
void lesson5_void_pointer(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 5 : void* (범용 포인터)         │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ void* 란?
      어떤 타입의 주소든 저장할 수 있는 "범용 포인터"
      단, 사용하려면 반드시 올바른 타입으로 캐스팅해야 함

    ★ 비유:
      void* = "만능 봉투"
      안에 뭐가 들었는지는 직접 기억해야 합니다.
      잘못 꺼내면(잘못된 캐스팅) 엉뚱한 값이 나옵니다.

    ★ void* 특징:
      - 어떤 포인터도 void* 에 대입 가능
      - void* 를 역참조하려면 캐스팅 필요
      - 포인터 연산 불가 (크기를 모르므로)
      - malloc 의 반환 타입이 void*
    */

    int i_val = 42;
    double d_val = 3.14;
    char c_val = 'A';

    void* generic;

    printf("  ■ void* 로 다양한 타입 저장\n");

    generic = &i_val;
    printf("    int:    %d\n", *(int*)generic);

    generic = &d_val;
    printf("    double: %.2f\n", *(double*)generic);

    generic = &c_val;
    printf("    char:   '%c'\n", *(char*)generic);

    /* ── void* 와 함수 ── */
    printf("\n  ■ void* 를 활용한 범용 출력\n");
    printf("    qsort, bsearch 등 표준 라이브러리가\n");
    printf("    void* 로 어떤 타입이든 처리합니다.\n");
    printf("    malloc 도 void* 를 반환합니다.\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 6 — const 와 포인터
 * ========================================================================= */
void lesson6_const_pointer(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 6 : const 와 포인터             │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ const 와 포인터 조합:
    ┌──────────────────────────┬─────────────────────────────┐
    │ 선언                     │ 의미                         │
    ├──────────────────────────┼─────────────────────────────┤
    │ const int* p             │ *p 수정 불가 (값 보호)       │
    │ (= int const* p)        │ p 자체는 다른 주소 가능      │
    │                          │                              │
    │ int* const p             │ p 수정 불가 (주소 고정)      │
    │                          │ *p 는 수정 가능              │
    │                          │                              │
    │ const int* const p       │ 둘 다 수정 불가              │
    └──────────────────────────┴─────────────────────────────┘

    ★ 읽는 법: 오른쪽에서 왼쪽으로!
      const int* p → "p 는 포인터, int 를 가리키는데, const"
                    → "가리키는 값이 상수"

      int* const p → "p 는 const 포인터, int 를 가리킴"
                    → "포인터 자체가 상수"
    */

    int x = 10, y = 20;

    /* ── const int* : 값 수정 불가 ── */
    printf("  ■ const int* p (값 보호)\n");
    const int* cp = &x;
    printf("    *cp = %d\n", *cp);
    /* *cp = 99;  ← 컴파일 에러! */
    cp = &y;        /* 주소 변경은 OK */
    printf("    cp 를 y 로 변경 후 *cp = %d\n", *cp);

    /* ── int* const : 주소 변경 불가 ── */
    printf("\n  ■ int* const p (주소 고정)\n");
    int* const fp = &x;
    *fp = 99;       /* 값 변경은 OK */
    printf("    *fp = %d (값 변경 가능)\n", *fp);
    /* fp = &y;  ← 컴파일 에러! */

    printf("\n  ■ 함수 매개변수에서 const 사용\n");
    printf("    void print(const char* str)\n");
    printf("    → 함수 안에서 str 내용을 수정하지 않겠다는 약속\n");
    printf("    ★ 읽기 전용 매개변수에는 항상 const 를 붙이세요!\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 7 — 자주 하는 실수
 * ========================================================================= */
void lesson7_common_mistakes(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 7 : 포인터 실수 모음            │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 포인터 5대 실수:
    ┌────┬──────────────────────────┬────────────────────────┐
    │ #  │ 실수                     │ 결과                    │
    ├────┼──────────────────────────┼────────────────────────┤
    │ 1  │ 초기화 안 한 포인터 사용 │ 쓰레기 주소 접근 → 충돌│
    │ 2  │ NULL 포인터 역참조       │ Segmentation Fault     │
    │ 3  │ 댕글링 포인터            │ 해제된 메모리 접근     │
    │ 4  │ 타입 불일치 캐스팅       │ 잘못된 값 해석         │
    │ 5  │ 배열 범위 밖 접근        │ 메모리 오염            │
    └────┴──────────────────────────┴────────────────────────┘
    */

    printf("  ■ 실수 1: 초기화 안 한 포인터\n");
    printf("    int* p;     ← 쓰레기 주소!\n");
    printf("    *p = 10;    ← 어디에 쓸지 모름 → 충돌\n");
    printf("    해결: int* p = NULL; 또는 즉시 주소 대입\n\n");

    printf("  ■ 실수 2: NULL 포인터 역참조\n");
    printf("    int* p = NULL;\n");
    printf("    *p = 10;    ← Segmentation Fault!\n");
    printf("    해결: 사용 전 if (p != NULL) 검사\n\n");

    printf("  ■ 실수 3: & 와 * 혼동\n");
    printf("    & = 주소를 구하는 연산자\n");
    printf("    * = 주소에서 값을 꺼내는 연산자\n");
    printf("    int x = 10;\n");
    printf("    int* p = &x;   // p 에 x의 주소 저장\n");
    printf("    int y = *p;    // p가 가리키는 값(10) 읽기\n\n");

    printf("  ■ 실수 4: 지역 변수 주소 반환\n");
    printf("    int* bad_func() {\n");
    printf("        int x = 42;\n");
    printf("        return &x;  ← 함수 끝나면 x 사라짐!\n");
    printf("    }\n");
    printf("    해결: malloc 으로 힙에 할당하거나 static 사용\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 8 — 실전: 콜백 패턴
 * ========================================================================= */

/* 배열의 각 원소에 함수를 적용하는 범용 함수 */
void array_map(int* arr, int size, int (*transform)(int)) {
    for (int i = 0; i < size; i++) {
        arr[i] = transform(arr[i]);
    }
}

/* 조건에 맞는 원소만 세는 범용 함수 */
int array_count_if(const int* arr, int size, int (*predicate)(int)) {
    int count = 0;
    for (int i = 0; i < size; i++) {
        if (predicate(arr[i])) count++;
    }
    return count;
}

int double_it(int x) { return x * 2; }
int square_it(int x) { return x * x; }
int is_even(int x) { return x % 2 == 0; }
int is_positive(int x) { return x > 0; }

void lesson8_practical(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 8 : 실전 — 콜백 패턴           │\n");
    printf("└──────────────────────────────────────┘\n\n");

    int data[] = {1, 2, 3, 4, 5};
    int n = 5;

    /* ── array_map: 모든 원소 2배 ── */
    printf("  ■ array_map (모든 원소 2배)\n");
    printf("    원본: ");
    for (int i = 0; i < n; i++) printf("%d ", data[i]);
    printf("\n");

    array_map(data, n, double_it);
    printf("    결과: ");
    for (int i = 0; i < n; i++) printf("%d ", data[i]);
    printf("\n");

    /* ── array_count_if: 조건 세기 ── */
    printf("\n  ■ array_count_if\n");
    printf("    짝수 개수: %d\n", array_count_if(data, n, is_even));

    int mixed[] = {-3, 0, 5, -1, 8, 2};
    printf("    양수 개수: %d (배열: -3,0,5,-1,8,2)\n",
           array_count_if(mixed, 6, is_positive));

    /*
    ★ 포인터 체크리스트
    ─────────────────────────────────────
    □ 모든 포인터를 선언 시 초기화했는가?
    □ NULL 검사를 빠뜨리지 않았는가?
    □ free 후 NULL 로 초기화했는가?
    □ 지역 변수의 주소를 반환하지 않았는가?
    □ void* 캐스팅이 올바른가?
    □ 배열 범위를 넘지 않았는가?
    ─────────────────────────────────────
    */

    printf("\n");
}
