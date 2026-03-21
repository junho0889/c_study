/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C 학습 06단계: 메모리 관리
  ─ 스택 vs 힙, malloc, calloc, realloc, free ─

  C 에서는 메모리를 직접 빌리고 직접 반납해야 합니다.
  이 단계에서는 메모리가 어떻게 배치되는지 그림으로 이해하고,
  동적 할당의 4가지 함수를 완벽히 익힙니다.

  ■ 컴파일: gcc -std=c11 -Wall -o 06_memory main.c
  ■ 실행:   ./06_memory

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void lesson1_memory_layout(void);
void lesson2_malloc_free(void);
void lesson3_calloc(void);
void lesson4_realloc(void);
void lesson5_common_mistakes(void);
void lesson6_practical(void);

int main(void) {
    printf("========================================\n");
    printf("  C 06단계 : 메모리 관리\n");
    printf("========================================\n\n");

    lesson1_memory_layout();
    lesson2_malloc_free();
    lesson3_calloc();
    lesson4_realloc();
    lesson5_common_mistakes();
    lesson6_practical();

    printf("\n06단계 학습 완료!\n");
    return 0;
}


/* =========================================================================
 *  레슨 1 — 메모리 구조: 스택 vs 힙
 * ========================================================================= */
void lesson1_memory_layout(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 1 : 스택 vs 힙 메모리          │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 프로그램 실행 시 메모리 배치도

    ┌─────────────────────────┐  높은 주소
    │       스택 (Stack)       │  ← 지역 변수, 함수 호출 정보
    │     ↓ 아래로 자람         │     빠름, 자동 해제, 크기 제한
    │                          │
    │     ↑ 위로 자람           │
    │        힙 (Heap)         │  ← malloc 으로 할당한 메모리
    │                          │     느림, 수동 해제, 크기 큼
    ├──────────────────────────┤
    │    데이터 영역 (Data)     │  ← 전역 변수, static 변수
    ├──────────────────────────┤
    │    코드 영역 (Text)      │  ← 컴파일된 기계어 코드
    └─────────────────────────┘  낮은 주소

    ★ 비유:
      스택 = 자동 보관함 (물건을 넣으면 나갈 때 자동 회수)
      힙   = 대여 창고 (직접 빌리고, 다 쓰면 직접 반납해야 함)

    ★ 스택 vs 힙 비교표
    ┌───────────┬──────────────────┬──────────────────┐
    │           │  스택 (Stack)     │  힙 (Heap)       │
    ├───────────┼──────────────────┼──────────────────┤
    │ 할당      │ 자동 (선언만)     │ malloc 등 수동    │
    │ 해제      │ 자동 (스코프 끝)  │ free 로 수동      │
    │ 속도      │ 매우 빠름         │ 상대적 느림       │
    │ 크기      │ 작음 (1~8MB)     │ 큼 (GB 가능)     │
    │ 위험      │ 안전함            │ 누수, 이중해제    │
    │ 유연성    │ 크기 고정         │ 크기 변경 가능    │
    └───────────┴──────────────────┴──────────────────┘
    */

    /* ── 스택 변수: 함수가 끝나면 자동 정리 ── */
    int local_a = 10;
    int local_b = 20;
    printf("  스택 변수 local_a = %d (주소: %p)\n", local_a, (void*)&local_a);
    printf("  스택 변수 local_b = %d (주소: %p)\n", local_b, (void*)&local_b);

    /* ── 힙 변수: malloc 으로 빌리고 free 로 반납 ── */
    int* heap_var = (int*)malloc(sizeof(int));
    if (heap_var != NULL) {
        *heap_var = 99;
        printf("  힙 변수 *heap_var = %d (주소: %p)\n", *heap_var, (void*)heap_var);
        free(heap_var);
        heap_var = NULL;    /* ★ free 후 NULL 대입 습관! */
    }

    /*
    ★ 스택 주소는 높은 쪽에서 낮은 쪽으로 내려가고,
      힙 주소는 낮은 쪽에서 높은 쪽으로 올라갑니다.
      두 영역이 서로를 향해 자라는 구조입니다.
    */

    printf("\n");
}


/* =========================================================================
 *  레슨 2 — malloc 과 free
 * ========================================================================= */
void lesson2_malloc_free(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 2 : malloc 과 free             │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ malloc 함수 원형:
      void* malloc(size_t size);

      - size 바이트만큼 힙 메모리를 할당
      - 성공 → 할당된 메모리의 시작 주소 반환
      - 실패 → NULL 반환
      - 할당된 메모리는 초기화되지 않음 (쓰레기 값!)

    ★ free 함수 원형:
      void free(void* ptr);

      - malloc/calloc/realloc 으로 할당한 메모리를 해제
      - NULL 을 free 해도 아무 일 없음 (안전)
      - 같은 주소를 두 번 free 하면 → 정의되지 않은 동작!

    ★ 비유:
      malloc = 도서관에서 책상을 빌리는 것
      free   = 다 쓰고 책상을 반납하는 것
      반납 안 하면? → 다른 사람이 못 쓰고 공간 낭비 (메모리 누수!)
    */

    /* ── 정수 하나 할당 ── */
    printf("  ■ 정수 하나 할당\n");
    int* single = (int*)malloc(sizeof(int));
    if (single == NULL) {
        printf("    메모리 할당 실패!\n");
        return;
    }
    *single = 42;
    printf("    *single = %d\n", *single);
    free(single);
    single = NULL;

    /* ── 배열 할당 ── */
    printf("\n  ■ 정수 배열 5개 할당\n");
    int count = 5;
    int* scores = (int*)malloc(sizeof(int) * count);
    if (scores == NULL) {
        printf("    메모리 할당 실패!\n");
        return;
    }

    /* 값 대입 */
    for (int i = 0; i < count; i++) {
        scores[i] = (i + 1) * 10;
    }

    /* 출력 */
    for (int i = 0; i < count; i++) {
        printf("    scores[%d] = %d\n", i, scores[i]);
    }

    free(scores);
    scores = NULL;

    /*
    ★ malloc 사용 패턴 (외우세요!)
      1. malloc 호출
      2. NULL 검사 (반드시!)
      3. 메모리 사용
      4. free 호출
      5. 포인터를 NULL 로 초기화

    ★ sizeof 를 쓰는 이유:
      int 가 4바이트인 환경에서 int 5개 = 20바이트
      sizeof(int) * 5 라고 쓰면 환경에 관계없이 정확함
    */

    printf("\n");
}


/* =========================================================================
 *  레슨 3 — calloc
 * ========================================================================= */
void lesson3_calloc(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 3 : calloc (0으로 초기화 할당)  │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ calloc 함수 원형:
      void* calloc(size_t count, size_t size);

      - count 개의 size 바이트 블록을 할당
      - 할당된 메모리를 0 으로 초기화!  ← malloc 과의 차이!
      - 실패 → NULL 반환

    ★ malloc vs calloc 비교:
    ┌──────────────┬────────────────────┬─────────────────────┐
    │              │ malloc             │ calloc              │
    ├──────────────┼────────────────────┼─────────────────────┤
    │ 인자         │ 총 바이트 수       │ 개수, 개당 크기      │
    │ 초기화       │ 안 됨 (쓰레기값)   │ 0 으로 초기화        │
    │ 용도         │ 일반 할당          │ 배열, 0 초기화 필요  │
    └──────────────┴────────────────────┴─────────────────────┘

    ★ 비유:
      malloc = 빈 노트를 받는데 전 주인의 낙서가 남아있을 수 있음
      calloc = 깨끗이 지워진 노트를 받음
    */

    printf("  ■ calloc 으로 정수 5개 할당 (0으로 초기화됨)\n");
    int* arr = (int*)calloc(5, sizeof(int));
    if (arr == NULL) {
        printf("    메모리 할당 실패!\n");
        return;
    }

    /* 0 으로 초기화되어 있는지 확인 */
    for (int i = 0; i < 5; i++) {
        printf("    arr[%d] = %d", i, arr[i]);
        if (arr[i] == 0) printf("  (0으로 초기화 확인!)");
        printf("\n");
    }

    free(arr);
    arr = NULL;

    /* ── malloc + memset 으로 같은 효과 ── */
    printf("\n  ■ malloc + memset 으로 같은 효과\n");
    int* arr2 = (int*)malloc(sizeof(int) * 5);
    if (arr2 != NULL) {
        memset(arr2, 0, sizeof(int) * 5);    /* 0 으로 채우기 */
        printf("    arr2[0] = %d (memset 으로 0 초기화)\n", arr2[0]);
        free(arr2);
        arr2 = NULL;
    }

    printf("\n");
}


/* =========================================================================
 *  레슨 4 — realloc
 * ========================================================================= */
void lesson4_realloc(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 4 : realloc (크기 변경)         │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ realloc 함수 원형:
      void* realloc(void* ptr, size_t new_size);

      - 이미 할당된 메모리의 크기를 변경
      - 기존 데이터는 보존됨 (새 크기가 더 작으면 뒷부분 잘림)
      - 새 크기가 더 크면 추가 영역은 초기화 안 됨
      - 실패 → NULL 반환 (★ 원래 메모리는 그대로 유지!)

    ★ 비유:
      원래 3칸짜리 사물함을 쓰고 있는데 5칸이 필요해졌다면,
      realloc 은 "더 큰 사물함으로 옮겨 주는 서비스" 입니다.
      기존 물건(데이터)은 그대로 가져갑니다.

    ★ 주의: realloc 이 실패하면 NULL 을 반환합니다.
      원래 포인터에 바로 대입하면 원래 메모리 주소를 잃어버립니다!
      → 반드시 임시 포인터로 받아야 합니다.
    */

    printf("  ■ realloc 으로 배열 크기 확장\n");

    /* 처음: 3개 할당 */
    int* data = (int*)malloc(sizeof(int) * 3);
    if (data == NULL) return;

    data[0] = 10;
    data[1] = 20;
    data[2] = 30;
    printf("    확장 전: ");
    for (int i = 0; i < 3; i++) printf("%d ", data[i]);
    printf("\n");

    /* 확장: 3개 → 5개 */
    int* temp = (int*)realloc(data, sizeof(int) * 5);
    if (temp == NULL) {
        printf("    realloc 실패! 기존 메모리 유지\n");
        free(data);
        return;
    }
    data = temp;    /* 성공했으므로 새 주소로 갱신 */

    data[3] = 40;
    data[4] = 50;
    printf("    확장 후: ");
    for (int i = 0; i < 5; i++) printf("%d ", data[i]);
    printf("\n");

    free(data);
    data = NULL;

    /*
    ★ realloc 안전 패턴:
      int* temp = realloc(data, new_size);
      if (temp == NULL) {
          // 실패 처리 (data 는 여전히 유효)
          free(data);
          return;
      }
      data = temp;   // 성공 시에만 갱신

    ★ realloc 특수 동작:
      realloc(NULL, size)  → malloc(size) 와 동일
      realloc(ptr, 0)      → 구현에 따라 다름 (사용 금지!)
    */

    printf("\n");
}


/* =========================================================================
 *  레슨 5 — 자주 하는 실수와 위험
 * ========================================================================= */
void lesson5_common_mistakes(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 5 : 메모리 관련 실수 모음       │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 메모리 관련 5대 실수

    ┌────┬──────────────────────┬──────────────────────────────┐
    │ #  │ 실수                 │ 결과                          │
    ├────┼──────────────────────┼──────────────────────────────┤
    │ 1  │ NULL 검사 생략       │ NULL 역참조 → 프로그램 충돌   │
    │ 2  │ free 잊기            │ 메모리 누수 (Memory Leak)     │
    │ 3  │ 이중 free            │ 정의되지 않은 동작 → 충돌     │
    │ 4  │ 해제 후 사용         │ 댕글링 포인터 → 쓰레기값      │
    │ 5  │ 배열 범위 초과       │ 버퍼 오버플로 → 다른 데이터   │
    │    │                      │ 오염, 보안 취약점             │
    └────┴──────────────────────┴──────────────────────────────┘
    */

    /* ── 실수 1: NULL 검사 생략 ── */
    printf("  ■ 실수 1: NULL 검사 생략\n");
    printf("    나쁜 예:  int* p = malloc(sizeof(int));\n");
    printf("              *p = 10;  // ← 할당 실패하면 충돌!\n");
    printf("    좋은 예:  if (p == NULL) { 에러 처리; }\n\n");

    /* ── 실수 2: 메모리 누수 ── */
    printf("  ■ 실수 2: 메모리 누수\n");
    printf("    malloc 만 하고 free 를 안 하면\n");
    printf("    프로그램이 오래 돌수록 메모리를 점점 잡아먹습니다.\n");
    printf("    장기 실행 서버에서 특히 치명적입니다.\n\n");

    /* ── 실수 3: 이중 free ── */
    printf("  ■ 실수 3: 이중 free\n");
    printf("    free(p); free(p);  // ← 두 번째 free 에서 충돌!\n");
    printf("    해결: free 후 p = NULL; 로 초기화\n");
    printf("          (NULL 을 free 해도 안전합니다)\n\n");

    /* ── 실수 4: 댕글링 포인터 ── */
    printf("  ■ 실수 4: 댕글링 포인터 (Dangling Pointer)\n");
    int* dangling = (int*)malloc(sizeof(int));
    if (dangling != NULL) {
        *dangling = 77;
        free(dangling);
        /* dangling 은 이제 해제된 주소를 가리킴 */
        /* *dangling = 88;  ← 이러면 위험! */
        dangling = NULL;    /* ★ 이렇게 방지! */
        printf("    free 후 NULL 대입으로 방지 완료\n\n");
    }

    /* ── 실수 5: 버퍼 오버플로 ── */
    printf("  ■ 실수 5: 버퍼 오버플로\n");
    printf("    int* p = malloc(sizeof(int) * 3);\n");
    printf("    p[5] = 100;  // ← 범위 밖 접근! 다른 메모리 오염\n\n");
}


/* =========================================================================
 *  레슨 6 — 실전: 동적 배열 만들기
 * ========================================================================= */
void lesson6_practical(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 6 : 실전 — 동적 성적표         │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 시나리오: 학생 수를 미리 모르는 상황에서
      성적 데이터를 동적으로 관리하는 프로그램

    이 예제에서 malloc → realloc → free 의 전체 흐름을 봅니다.
    */

    int capacity = 2;       /* 초기 용량 */
    int size = 0;            /* 현재 데이터 수 */
    int* grades = (int*)malloc(sizeof(int) * capacity);

    if (grades == NULL) {
        printf("    초기 메모리 할당 실패\n");
        return;
    }

    /* 데이터 추가 함수를 인라인으로 구현 */
    int new_grades[] = {85, 92, 78, 95, 88};
    int total_new = 5;

    for (int i = 0; i < total_new; i++) {
        /* 용량 부족 시 2배로 확장 */
        if (size >= capacity) {
            capacity *= 2;
            int* temp = (int*)realloc(grades, sizeof(int) * capacity);
            if (temp == NULL) {
                printf("    realloc 실패! 기존 데이터 해제\n");
                free(grades);
                return;
            }
            grades = temp;
            printf("    ★ 용량 확장: %d → %d\n", capacity / 2, capacity);
        }
        grades[size] = new_grades[i];
        size++;
    }

    /* 결과 출력 */
    printf("\n    ── 성적표 ──\n");
    int total = 0;
    for (int i = 0; i < size; i++) {
        printf("    학생 %d: %d점\n", i + 1, grades[i]);
        total += grades[i];
    }
    printf("    평균: %.1f점\n", (double)total / size);
    printf("    사용 용량: %d / %d\n", size, capacity);

    free(grades);
    grades = NULL;

    /*
    ★ 메모리 관리 체크리스트
    ─────────────────────────────────────
    □ malloc/calloc 후 NULL 검사 했는가?
    □ realloc 은 임시 포인터로 받았는가?
    □ 모든 malloc 에 대응하는 free 가 있는가?
    □ free 후 포인터를 NULL 로 초기화했는가?
    □ 배열 범위를 벗어나지 않았는가?
    ─────────────────────────────────────
    */

    printf("\n");
}
