/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C 학습 12단계: 자료구조
  ─ 연결 리스트, 스택, 큐, 해시 테이블 ─

  자료구조는 "데이터를 어떤 모양으로 정리하느냐"의 기술입니다.
  같은 데이터도 정리 방식에 따라 넣고 꺼내는 속도가 달라집니다.

  ■ 컴파일: gcc -std=c11 -Wall -o 12_ds main.c
  ■ 실행:   ./12_ds

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void lesson1_why_data_structures(void);
void lesson2_linked_list(void);
void lesson3_stack(void);
void lesson4_queue(void);
void lesson5_comparison(void);
void lesson6_practical(void);

int main(void) {
    printf("========================================\n");
    printf("  C 12단계 : 자료구조\n");
    printf("========================================\n\n");

    lesson1_why_data_structures();
    lesson2_linked_list();
    lesson3_stack();
    lesson4_queue();
    lesson5_comparison();
    lesson6_practical();

    printf("\n12단계 학습 완료!\n");
    return 0;
}


/* =========================================================================
 *  레슨 1 — 자료구조가 필요한 이유
 * ========================================================================= */
void lesson1_why_data_structures(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 1 : 왜 자료구조를 배울까?       │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 자료구조 = 데이터를 "어떤 규칙으로 정리"하는 방법

    ★ 비유:
      같은 옷이라도:
      - 서랍에 넣으면 → 찾기 쉬움 (배열, 해시)
      - 줄에 걸면     → 순서대로 꺼내기 쉬움 (큐)
      - 쌓아두면      → 맨 위만 빠르게 접근 (스택)
      - 체인으로 연결 → 중간 추가/삭제 쉬움 (연결 리스트)

    ★ 핵심 자료구조 비교:
    ┌─────────────┬────────┬────────┬────────┬───────────────┐
    │ 자료구조    │ 삽입   │ 삭제   │ 검색   │ 특징           │
    ├─────────────┼────────┼────────┼────────┼───────────────┤
    │ 배열        │ O(n)   │ O(n)   │ O(1)*  │ 인덱스 접근    │
    │ 연결리스트  │ O(1)** │ O(1)** │ O(n)   │ 유연한 크기    │
    │ 스택        │ O(1)   │ O(1)   │ O(n)   │ LIFO           │
    │ 큐          │ O(1)   │ O(1)   │ O(n)   │ FIFO           │
    │ 해시테이블  │ O(1)   │ O(1)   │ O(1)   │ 키-값 저장     │
    └─────────────┴────────┴────────┴────────┴───────────────┘
    * 인덱스를 알 때   ** 위치를 알 때
    */

    printf("  자료구조 선택은 '무엇을 자주 하느냐'에 달려 있습니다.\n");
    printf("  - 순서대로 처리? → 큐\n");
    printf("  - 되돌리기 기능? → 스택\n");
    printf("  - 중간 삽입/삭제? → 연결 리스트\n");
    printf("  - 키로 빠른 검색? → 해시 테이블\n\n");
}


/* =========================================================================
 *  레슨 2 — 연결 리스트 (Linked List)
 * ========================================================================= */

/* ── 노드 정의 ── */
typedef struct Node {
    int data;
    struct Node* next;
} Node;

/* 맨 앞에 삽입 */
Node* list_prepend(Node* head, int data) {
    Node* new_node = (Node*)malloc(sizeof(Node));
    if (new_node == NULL) return head;
    new_node->data = data;
    new_node->next = head;
    return new_node;
}

/* 맨 뒤에 삽입 */
Node* list_append(Node* head, int data) {
    Node* new_node = (Node*)malloc(sizeof(Node));
    if (new_node == NULL) return head;
    new_node->data = data;
    new_node->next = NULL;

    if (head == NULL) return new_node;

    Node* curr = head;
    while (curr->next != NULL) {
        curr = curr->next;
    }
    curr->next = new_node;
    return head;
}

/* 출력 */
void list_print(const Node* head) {
    const Node* curr = head;
    while (curr != NULL) {
        printf("%d", curr->data);
        if (curr->next) printf(" -> ");
        curr = curr->next;
    }
    printf(" -> NULL\n");
}

/* 전체 해제 */
void list_free(Node* head) {
    while (head != NULL) {
        Node* temp = head;
        head = head->next;
        free(temp);
    }
}

/* 길이 */
int list_length(const Node* head) {
    int count = 0;
    while (head != NULL) {
        count++;
        head = head->next;
    }
    return count;
}

void lesson2_linked_list(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 2 : 연결 리스트 (Linked List)  │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 연결 리스트란?
      각 노드가 데이터 + 다음 노드의 주소를 가진 구조

    ★ 비유:
      보물찾기 놀이와 같습니다.
      첫 번째 쪽지(노드)에 보물(data)과
      다음 쪽지 위치(next)가 적혀 있습니다.

    ★ 구조:
      head → [10|→] → [20|→] → [30|→] → NULL

    ★ 배열 vs 연결 리스트:
    ┌──────────────┬─────────────┬──────────────────┐
    │              │ 배열        │ 연결 리스트       │
    ├──────────────┼─────────────┼──────────────────┤
    │ 메모리       │ 연속        │ 분산              │
    │ 크기         │ 고정 (보통) │ 유동              │
    │ 인덱스 접근  │ O(1)        │ O(n)              │
    │ 중간 삽입    │ O(n)        │ O(1) (위치 알면)  │
    │ 메모리 효율  │ 좋음        │ 포인터 추가 비용  │
    └──────────────┴─────────────┴──────────────────┘
    */

    printf("  ■ 연결 리스트 생성 및 조작\n");

    Node* list = NULL;

    /* 맨 앞에 삽입 */
    list = list_prepend(list, 30);
    list = list_prepend(list, 20);
    list = list_prepend(list, 10);
    printf("    prepend 결과: ");
    list_print(list);

    /* 맨 뒤에 삽입 */
    list = list_append(list, 40);
    list = list_append(list, 50);
    printf("    append 결과 : ");
    list_print(list);

    printf("    길이: %d\n", list_length(list));

    list_free(list);
    list = NULL;
    printf("    ★ 모든 노드 free 완료\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 3 — 스택 (Stack)
 * ========================================================================= */

#define STACK_MAX 10

typedef struct {
    int data[STACK_MAX];
    int top;
} Stack;

void stack_init(Stack* s) { s->top = -1; }
int stack_is_empty(const Stack* s) { return s->top == -1; }
int stack_is_full(const Stack* s) { return s->top == STACK_MAX - 1; }

int stack_push(Stack* s, int value) {
    if (stack_is_full(s)) return 0;
    s->data[++(s->top)] = value;
    return 1;
}

int stack_pop(Stack* s, int* out) {
    if (stack_is_empty(s)) return 0;
    *out = s->data[(s->top)--];
    return 1;
}

int stack_peek(const Stack* s, int* out) {
    if (stack_is_empty(s)) return 0;
    *out = s->data[s->top];
    return 1;
}

void lesson3_stack(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 3 : 스택 (Stack)               │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 스택 = LIFO (Last In, First Out)
      마지막에 넣은 것이 먼저 나옵니다.

    ★ 비유:
      접시 더미 — 맨 위에 올리고, 맨 위에서 꺼냄
      또는 Ctrl+Z (실행 취소) — 가장 최근 동작부터 취소

    ★ 연산:
    ┌──────────┬───────────────────────────────┐
    │ 연산     │ 설명                           │
    ├──────────┼───────────────────────────────┤
    │ push     │ 맨 위에 넣기                   │
    │ pop      │ 맨 위에서 꺼내기               │
    │ peek     │ 맨 위 값 확인 (꺼내지 않음)    │
    │ isEmpty  │ 비어있는지 확인                 │
    │ isFull   │ 가득 찼는지 확인                │
    └──────────┴───────────────────────────────┘

    ★ 스택의 실제 용도:
      - 함수 호출 스택 (재귀)
      - 실행 취소 (Undo)
      - 괄호 짝 검사
      - 수식 계산 (후위 표기법)
      - 뒤로 가기 (브라우저)
    */

    Stack s;
    stack_init(&s);

    printf("  ■ push 연산\n");
    int values[] = {10, 20, 30, 40, 50};
    for (int i = 0; i < 5; i++) {
        stack_push(&s, values[i]);
        printf("    push(%d) → top = %d\n", values[i], s.top);
    }

    printf("\n  ■ peek 연산\n");
    int top_val;
    if (stack_peek(&s, &top_val)) {
        printf("    peek → %d (꺼내지 않고 확인만)\n", top_val);
    }

    printf("\n  ■ pop 연산 (LIFO 순서 확인)\n");
    int val;
    while (stack_pop(&s, &val)) {
        printf("    pop → %d\n", val);
    }
    printf("    ★ 넣은 순서: 10,20,30,40,50\n");
    printf("       꺼낸 순서: 50,40,30,20,10 (역순!)\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 4 — 큐 (Queue)
 * ========================================================================= */

#define QUEUE_MAX 10

typedef struct {
    int data[QUEUE_MAX];
    int front;
    int rear;
    int count;
} Queue;

void queue_init(Queue* q) { q->front = 0; q->rear = -1; q->count = 0; }
int queue_is_empty(const Queue* q) { return q->count == 0; }
int queue_is_full(const Queue* q) { return q->count == QUEUE_MAX; }

int queue_enqueue(Queue* q, int value) {
    if (queue_is_full(q)) return 0;
    q->rear = (q->rear + 1) % QUEUE_MAX;   /* 원형 큐! */
    q->data[q->rear] = value;
    q->count++;
    return 1;
}

int queue_dequeue(Queue* q, int* out) {
    if (queue_is_empty(q)) return 0;
    *out = q->data[q->front];
    q->front = (q->front + 1) % QUEUE_MAX;  /* 원형 큐! */
    q->count--;
    return 1;
}

void lesson4_queue(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 4 : 큐 (Queue)                │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 큐 = FIFO (First In, First Out)
      먼저 넣은 것이 먼저 나옵니다.

    ★ 비유:
      놀이공원 줄 서기 — 먼저 온 사람이 먼저 탑승
      프린터 대기열 — 먼저 보낸 문서가 먼저 출력

    ★ 연산:
    ┌──────────┬───────────────────────────────┐
    │ 연산     │ 설명                           │
    ├──────────┼───────────────────────────────┤
    │ enqueue  │ 뒤에 넣기                      │
    │ dequeue  │ 앞에서 꺼내기                   │
    │ isEmpty  │ 비어있는지 확인                 │
    │ isFull   │ 가득 찼는지 확인                │
    └──────────┴───────────────────────────────┘

    ★ 원형 큐 (Circular Queue):
      배열의 끝에 도달하면 다시 앞으로 돌아가는 구조
      → % (나머지) 연산으로 구현
      → 배열 공간을 낭비하지 않음

      ┌───┬───┬───┬───┬───┐
      │ 0 │ 1 │ 2 │ 3 │ 4 │
      └───┴───┴───┴───┴───┘
        ↑                 ↑
      front             rear
      dequeue          enqueue
    */

    Queue q;
    queue_init(&q);

    printf("  ■ enqueue 연산\n");
    int vals[] = {100, 200, 300, 400};
    for (int i = 0; i < 4; i++) {
        queue_enqueue(&q, vals[i]);
        printf("    enqueue(%d) → count = %d\n", vals[i], q.count);
    }

    printf("\n  ■ dequeue 연산 (FIFO 순서 확인)\n");
    int val;
    while (queue_dequeue(&q, &val)) {
        printf("    dequeue → %d\n", val);
    }
    printf("    ★ 넣은 순서: 100,200,300,400\n");
    printf("       꺼낸 순서: 100,200,300,400 (같은 순서!)\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 5 — 자료구조 비교
 * ========================================================================= */
void lesson5_comparison(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 5 : 자료구조 비교               │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 스택 vs 큐 한눈에 비교:
    ┌──────────┬──────────────────┬──────────────────┐
    │          │ 스택 (Stack)     │ 큐 (Queue)       │
    ├──────────┼──────────────────┼──────────────────┤
    │ 원리     │ LIFO             │ FIFO             │
    │ 비유     │ 접시 쌓기        │ 줄 서기          │
    │ 삽입     │ push (위에)      │ enqueue (뒤에)   │
    │ 삭제     │ pop (위에서)     │ dequeue (앞에서) │
    │ 실제 예  │ Ctrl+Z 취소      │ 프린터 대기열    │
    │          │ 재귀 호출        │ BFS 탐색         │
    │          │ 뒤로가기         │ 작업 스케줄링    │
    └──────────┴──────────────────┴──────────────────┘

    ★ 연결 리스트 vs 배열:
    ┌──────────────┬──────────────┬──────────────────┐
    │              │ 배열         │ 연결 리스트       │
    ├──────────────┼──────────────┼──────────────────┤
    │ 크기 변경    │ 어려움       │ 쉬움              │
    │ 랜덤 접근    │ O(1)         │ O(n)              │
    │ 중간 삽입    │ O(n)         │ O(1)              │
    │ 캐시 친화성  │ 좋음         │ 나쁨              │
    │ 메모리 오버헤드│ 없음       │ 포인터 크기만큼   │
    └──────────────┴──────────────┴──────────────────┘
    */

    printf("  ■ 선택 가이드\n");
    printf("    - 데이터를 순서대로 처리 → 큐\n");
    printf("    - 실행 취소, 뒤로가기    → 스택\n");
    printf("    - 빈번한 중간 삽입/삭제  → 연결 리스트\n");
    printf("    - 인덱스로 빠른 접근     → 배열\n");
    printf("    - 키-값 빠른 검색        → 해시 테이블\n\n");
}


/* =========================================================================
 *  레슨 6 — 실전: 괄호 짝 검사기 (스택 활용)
 * ========================================================================= */
int check_brackets(const char* expr) {
    /*
    ★ 괄호 짝 검사 알고리즘 (스택 활용):
      1. 여는 괄호 → 스택에 push
      2. 닫는 괄호 → 스택에서 pop, 짝이 맞는지 확인
      3. 끝까지 가서 스택이 비어있으면 → 올바른 괄호
    */
    Stack s;
    stack_init(&s);

    for (int i = 0; expr[i] != '\0'; i++) {
        char c = expr[i];

        if (c == '(' || c == '[' || c == '{') {
            stack_push(&s, c);
        } else if (c == ')' || c == ']' || c == '}') {
            int top;
            if (!stack_pop(&s, &top)) return 0;   /* 스택이 비었으면 실패 */

            if (c == ')' && top != '(') return 0;
            if (c == ']' && top != '[') return 0;
            if (c == '}' && top != '{') return 0;
        }
    }

    return stack_is_empty(&s);   /* 스택이 비어있어야 성공 */
}

void lesson6_practical(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 6 : 실전 — 괄호 짝 검사기      │\n");
    printf("└──────────────────────────────────────┘\n\n");

    const char* tests[] = {
        "(())",
        "{[()]}",
        "(()",
        "([)]",
        "{()}[]",
        ""
    };
    int n = 6;

    printf("  ■ 괄호 짝 검사 결과\n");
    for (int i = 0; i < n; i++) {
        int ok = check_brackets(tests[i]);
        printf("    \"%s\" → %s\n",
               strlen(tests[i]) > 0 ? tests[i] : "(빈 문자열)",
               ok ? "올바름" : "잘못됨");
    }

    /*
    ★ 자료구조 체크리스트
    ─────────────────────────────────────
    □ 동적 할당한 노드를 모두 free 했는가?
    □ 스택/큐의 오버플로/언더플로를 검사했는가?
    □ 연결 리스트의 head 가 NULL 인 경우를 처리했는가?
    □ 원형 큐에서 % 연산을 올바르게 사용했는가?
    □ 상황에 맞는 자료구조를 선택했는가?
    ─────────────────────────────────────
    */

    printf("\n");
}
