/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C 학습 13단계: 알고리즘
  ─ 정렬 (버블, 선택, 삽입, qsort), 검색 (선형, 이진) ─

  알고리즘은 "문제를 푸는 절차"입니다.
  같은 문제라도 방법에 따라 속도가 천배, 만배 달라집니다.

  ■ 컴파일: gcc -std=c11 -Wall -o 13_algo main.c
  ■ 실행:   ./13_algo

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int compare_int(const void* a, const void* b);

void lesson1_algorithm_thinking(void);
void lesson2_bubble_sort(void);
void lesson3_selection_sort(void);
void lesson4_insertion_sort(void);
void lesson5_sort_comparison(void);
void lesson6_linear_search(void);
void lesson7_binary_search(void);
void lesson8_practical(void);

int main(void) {
    printf("========================================\n");
    printf("  C 13단계 : 알고리즘\n");
    printf("========================================\n\n");

    lesson1_algorithm_thinking();
    lesson2_bubble_sort();
    lesson3_selection_sort();
    lesson4_insertion_sort();
    lesson5_sort_comparison();
    lesson6_linear_search();
    lesson7_binary_search();
    lesson8_practical();

    printf("\n13단계 학습 완료!\n");
    return 0;
}


/* ── 배열 출력 유틸리티 ── */
void print_array(const char* label, const int* arr, int n) {
    printf("    %s: ", label);
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}


/* =========================================================================
 *  레슨 1 — 알고리즘적 사고
 * ========================================================================= */
void lesson1_algorithm_thinking(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 1 : 알고리즘적 사고             │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 알고리즘 = 문제를 풀기 위한 단계별 절차

    ★ 비유:
      요리 레시피와 같습니다.
      같은 요리(문제)도 레시피(알고리즘)에 따라
      맛(결과)은 같지만 시간(성능)이 다릅니다.

    ★ 시간 복잡도 (Big-O):
      알고리즘이 데이터 크기(n)에 따라 얼마나 느려지는지 표현

    ┌─────────────┬──────────┬────────────────────────────┐
    │ 표기        │ 이름     │ 예                          │
    ├─────────────┼──────────┼────────────────────────────┤
    │ O(1)        │ 상수     │ 배열 인덱스 접근            │
    │ O(log n)    │ 로그     │ 이진 검색                   │
    │ O(n)        │ 선형     │ 배열 순회                   │
    │ O(n log n)  │ 선형로그 │ 퀵소트, 병합정렬            │
    │ O(n²)       │ 이차     │ 버블정렬, 중첩 반복문       │
    │ O(2ⁿ)       │ 지수     │ 피보나치 (단순 재귀)        │
    └─────────────┴──────────┴────────────────────────────┘

    ★ n=1000 일 때 연산 횟수 비교:
      O(n)       → 1,000
      O(n log n) → ~10,000
      O(n²)      → 1,000,000
      → n²과 n log n 의 차이는 100배!
    */

    printf("  알고리즘 = 같은 문제를 더 빠르게 푸는 방법을 찾는 것\n");
    printf("  핵심: '일단 돌아가게' 만든 후 '더 빠르게' 개선하기\n\n");
}


/* =========================================================================
 *  레슨 2 — 버블 정렬
 * ========================================================================= */
void bubble_sort(int arr[], int n) {
    for (int i = 0; i < n - 1; i++) {
        int swapped = 0;
        for (int j = 0; j < n - 1 - i; j++) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
                swapped = 1;
            }
        }
        if (!swapped) break;    /* ★ 최적화: 교환 없으면 이미 정렬됨 */
    }
}

void lesson2_bubble_sort(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 2 : 버블 정렬 (Bubble Sort)    │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 버블 정렬 = 옆에 있는 두 원소를 비교하며 교환

    ★ 비유:
      줄 서기에서 키 큰 사람이 한 칸씩 뒤로 밀려나는 모습
      → 한 바퀴 돌 때마다 가장 큰 값이 맨 뒤로 "떠오름" (bubble)

    ★ 동작 과정 (30, 10, 50, 20):
      1회차: [10,30,20,50] → 50이 맨 뒤로
      2회차: [10,20,30,50] → 30이 제자리
      완료!

    ★ 시간 복잡도: O(n²) (느림!)
      최선(이미 정렬): O(n) (swapped 최적화 시)
    */

    int arr[] = {64, 34, 25, 12, 22, 11, 90};
    int n = 7;

    print_array("정렬 전", arr, n);
    bubble_sort(arr, n);
    print_array("정렬 후", arr, n);

    printf("\n");
}


/* =========================================================================
 *  레슨 3 — 선택 정렬
 * ========================================================================= */
void selection_sort(int arr[], int n) {
    for (int i = 0; i < n - 1; i++) {
        int min_idx = i;
        for (int j = i + 1; j < n; j++) {
            if (arr[j] < arr[min_idx]) {
                min_idx = j;
            }
        }
        if (min_idx != i) {
            int temp = arr[i];
            arr[i] = arr[min_idx];
            arr[min_idx] = temp;
        }
    }
}

void lesson3_selection_sort(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 3 : 선택 정렬 (Selection Sort) │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 선택 정렬 = 매번 최솟값을 찾아서 앞에 배치

    ★ 비유:
      카드를 정렬할 때 가장 작은 카드를 찾아 왼쪽에 놓고,
      나머지에서 다시 가장 작은 걸 찾아 그 옆에 놓는 방식

    ★ 동작 과정 (64, 25, 12, 22):
      1회: 최솟값 12 → [12, 25, 64, 22]
      2회: 최솟값 22 → [12, 22, 64, 25]
      3회: 최솟값 25 → [12, 22, 25, 64]

    ★ 시간 복잡도: 항상 O(n²)
      교환 횟수는 O(n) 으로 적음 (버블보다 교환이 적음)
    */

    int arr[] = {64, 25, 12, 22, 11};
    int n = 5;

    print_array("정렬 전", arr, n);
    selection_sort(arr, n);
    print_array("정렬 후", arr, n);

    printf("\n");
}


/* =========================================================================
 *  레슨 4 — 삽입 정렬
 * ========================================================================= */
void insertion_sort(int arr[], int n) {
    for (int i = 1; i < n; i++) {
        int key = arr[i];
        int j = i - 1;

        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;
    }
}

void lesson4_insertion_sort(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 4 : 삽입 정렬 (Insertion Sort) │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 삽입 정렬 = 새 카드를 정렬된 패에 올바른 위치에 끼워넣기

    ★ 비유:
      카드 게임에서 손패를 정리하는 방식과 동일합니다.
      새 카드를 받으면 이미 정리된 카드 사이의
      올바른 위치에 끼워 넣습니다.

    ★ 동작 과정 (5, 2, 4, 6, 1):
      [5] 2 4 6 1  → 2를 5앞에: [2,5] 4 6 1
      [2,5] 4 6 1  → 4를 5앞에: [2,4,5] 6 1
      [2,4,5] 6 1  → 6은 제자리: [2,4,5,6] 1
      [2,4,5,6] 1  → 1을 맨앞에: [1,2,4,5,6]

    ★ 시간 복잡도:
      최선(이미 정렬): O(n) ← 매우 빠름!
      최악(역순):      O(n²)
      → 거의 정렬된 데이터에 강합니다.
    */

    int arr[] = {5, 2, 4, 6, 1, 3};
    int n = 6;

    print_array("정렬 전", arr, n);
    insertion_sort(arr, n);
    print_array("정렬 후", arr, n);

    printf("\n");
}


/* =========================================================================
 *  레슨 5 — 정렬 알고리즘 비교
 * ========================================================================= */
void lesson5_sort_comparison(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 5 : 정렬 알고리즘 비교          │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 정렬 알고리즘 비교표:
    ┌────────────┬──────────┬──────────┬──────────┬──────────┐
    │ 알고리즘   │ 최선     │ 평균     │ 최악     │ 안정성   │
    ├────────────┼──────────┼──────────┼──────────┼──────────┤
    │ 버블       │ O(n)     │ O(n²)    │ O(n²)    │ 안정     │
    │ 선택       │ O(n²)    │ O(n²)    │ O(n²)    │ 불안정   │
    │ 삽입       │ O(n)     │ O(n²)    │ O(n²)    │ 안정     │
    │ 퀵소트     │ O(nlogn) │ O(nlogn) │ O(n²)    │ 불안정   │
    │ 병합정렬   │ O(nlogn) │ O(nlogn) │ O(nlogn) │ 안정     │
    └────────────┴──────────┴──────────┴──────────┴──────────┘

    ★ 안정 정렬이란?
      같은 값의 원래 순서가 유지되는 정렬
      예: (3a, 1, 3b, 2) → 안정: (1, 2, 3a, 3b)
                         → 불안정: (1, 2, 3b, 3a) 가능

    ★ C 표준 라이브러리의 qsort:
      대부분의 경우 qsort 를 사용하는 것이 가장 실용적!
    */

    /* ── qsort 사용 ── */
    printf("  ■ qsort (C 표준 라이브러리)\n");
    int arr[] = {50, 10, 40, 20, 30};
    int n = 5;

    print_array("정렬 전", arr, n);

    /* qsort(배열, 개수, 원소크기, 비교함수) */
    qsort(arr, n, sizeof(int), compare_int);
    print_array("정렬 후", arr, n);

    printf("\n  ■ 실전 선택 가이드\n");
    printf("    데이터 적음 (<50)    → 삽입 정렬\n");
    printf("    거의 정렬됨          → 삽입 정렬\n");
    printf("    일반적인 경우        → qsort (라이브러리)\n");
    printf("    안정 정렬 필요       → 병합 정렬\n\n");
}

/* qsort 비교 함수 */
int compare_int(const void* a, const void* b) {
    return (*(const int*)a) - (*(const int*)b);
}


/* =========================================================================
 *  레슨 6 — 선형 검색
 * ========================================================================= */
int linear_search(const int arr[], int n, int target) {
    for (int i = 0; i < n; i++) {
        if (arr[i] == target) return i;
    }
    return -1;    /* 못 찾음 */
}

void lesson6_linear_search(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 6 : 선형 검색 (Linear Search)  │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 선형 검색 = 처음부터 끝까지 하나씩 확인

    ★ 비유:
      책상 서랍을 첫 번째부터 열어보며 찾는 것

    ★ 시간 복잡도: O(n)
      최선: O(1) (첫 원소에 있을 때)
      최악: O(n) (마지막이거나 없을 때)

    ★ 장점: 정렬되지 않은 데이터에서도 사용 가능
    */

    int arr[] = {23, 45, 12, 67, 34, 89, 56};
    int n = 7;

    printf("  ■ 선형 검색\n");
    print_array("배열", arr, n);

    int target = 67;
    int idx = linear_search(arr, n, target);
    printf("    %d 검색 → 인덱스 %d\n", target, idx);

    target = 99;
    idx = linear_search(arr, n, target);
    printf("    %d 검색 → %s\n", target, idx >= 0 ? "발견" : "없음");

    printf("\n");
}


/* =========================================================================
 *  레슨 7 — 이진 검색
 * ========================================================================= */
int binary_search(const int arr[], int n, int target) {
    int low = 0, high = n - 1;

    while (low <= high) {
        int mid = low + (high - low) / 2;    /* ★ 오버플로 방지 */

        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) low = mid + 1;
        else high = mid - 1;
    }
    return -1;
}

void lesson7_binary_search(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 7 : 이진 검색 (Binary Search)  │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 이진 검색 = 정렬된 배열에서 절반씩 줄여가며 검색
      ★ 전제 조건: 배열이 정렬되어 있어야 함!

    ★ 비유:
      사전에서 단어 찾기!
      중간 페이지를 펴서 찾는 단어보다 앞인지 뒤인지 판단하고,
      해당 절반에서 다시 중간을 펴는 과정을 반복

    ★ 동작 과정 (배열: 10,20,30,40,50,60, 찾기: 40):
      1단계: mid=30 → 40>30 → 오른쪽 절반
      2단계: mid=50 → 40<50 → 왼쪽 절반
      3단계: mid=40 → 찾았다!

    ★ 시간 복잡도: O(log n)
      n=1,000,000 이면 최대 20번만에 찾음!
      (선형 검색: 최대 1,000,000번)

    ★ 선형 vs 이진 검색:
    ┌──────────────┬──────────────┬────────────────┐
    │              │ 선형 검색    │ 이진 검색       │
    ├──────────────┼──────────────┼────────────────┤
    │ 시간 복잡도  │ O(n)         │ O(log n)       │
    │ 정렬 필요?   │ 아니오       │ 예             │
    │ n=100만 최악 │ 100만 번     │ 20번           │
    │ 구현 난이도  │ 쉬움         │ 보통           │
    └──────────────┴──────────────┴────────────────┘
    */

    int arr[] = {10, 20, 30, 40, 50, 60, 70, 80, 90, 100};
    int n = 10;

    printf("  ■ 이진 검색 (정렬된 배열)\n");
    print_array("배열", arr, n);

    int targets[] = {40, 10, 100, 55};
    for (int i = 0; i < 4; i++) {
        int idx = binary_search(arr, n, targets[i]);
        printf("    %3d 검색 → %s",
               targets[i], idx >= 0 ? "발견" : "없음");
        if (idx >= 0) printf(" (인덱스 %d)", idx);
        printf("\n");
    }

    /*
    ★ mid 계산 시 오버플로 주의:
      mid = (low + high) / 2     ← low+high 가 int 범위 초과 가능!
      mid = low + (high-low) / 2 ← 안전!
    */

    printf("\n");
}


/* =========================================================================
 *  레슨 8 — 실전: 성적 분석기
 * ========================================================================= */
void lesson8_practical(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 8 : 실전 — 성적 분석기          │\n");
    printf("└──────────────────────────────────────┘\n\n");

    int scores[] = {78, 92, 65, 88, 95, 70, 82, 55, 98, 73,
                    85, 60, 91, 77, 83};
    int n = 15;

    printf("  ■ 원본 데이터\n");
    print_array("점수", scores, n);

    /* 정렬 */
    int sorted[15];
    memcpy(sorted, scores, sizeof(scores));
    qsort(sorted, n, sizeof(int), compare_int);

    printf("\n  ■ 정렬 후\n");
    print_array("정렬", sorted, n);

    /* 통계 */
    int total = 0;
    for (int i = 0; i < n; i++) total += sorted[i];

    printf("\n  ■ 통계\n");
    printf("    최저: %d\n", sorted[0]);
    printf("    최고: %d\n", sorted[n - 1]);
    printf("    평균: %.1f\n", (double)total / n);
    printf("    중앙값: %d\n", sorted[n / 2]);

    /* 특정 점수 검색 */
    printf("\n  ■ 이진 검색으로 특정 점수 존재 여부\n");
    int find[] = {85, 90, 95};
    for (int i = 0; i < 3; i++) {
        int idx = binary_search(sorted, n, find[i]);
        printf("    %d점 → %s\n", find[i], idx >= 0 ? "있음" : "없음");
    }

    /* 등급 분포 */
    printf("\n  ■ 등급 분포\n");
    int grade_a = 0, grade_b = 0, grade_c = 0, grade_f = 0;
    for (int i = 0; i < n; i++) {
        if (scores[i] >= 90) grade_a++;
        else if (scores[i] >= 80) grade_b++;
        else if (scores[i] >= 70) grade_c++;
        else grade_f++;
    }
    printf("    A (90+): %d명\n", grade_a);
    printf("    B (80+): %d명\n", grade_b);
    printf("    C (70+): %d명\n", grade_c);
    printf("    F (<70): %d명\n", grade_f);

    /*
    ★ 알고리즘 체크리스트
    ─────────────────────────────────────
    □ 이진 검색 전에 데이터가 정렬되었는가?
    □ 정렬 알고리즘의 시간 복잡도를 고려했는가?
    □ 배열 범위를 벗어나는 접근이 없는가?
    □ 오버플로 가능성을 확인했는가?
    □ qsort 비교 함수의 반환값이 올바른가?
    ─────────────────────────────────────
    */

    printf("\n");
}
