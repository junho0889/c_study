/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C 학습 18단계: 실전 미니 프로젝트 - 연락처 관리 프로그램
  ─ 구조체, 동적 메모리, 파일 I/O, 검색, 정렬, 테스트 통합 ─

  지금까지 배운 모든 개념을 하나의 프로그램에 통합합니다.
  이 프로그램은 연락처를 추가, 검색, 정렬, 저장, 불러오기할 수 있습니다.

  ■ 컴파일: gcc -std=c11 -Wall -o 18_project main.c
  ■ 실행:   ./18_project

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
★ 이 프로젝트에서 사용하는 C 기능 목록:
  06단계: 동적 메모리 (malloc, realloc, free)
  07단계: 파일 입출력 (fopen, fprintf, fscanf, fclose)
  08단계: 전처리기 (#define, 매크로)
  09단계: 문자열 (strlen, strcmp, strcpy, strstr)
  10단계: 포인터 (함수 포인터, void*, qsort)
  11단계: 디버깅 (assert, 방어적 프로그래밍)
  12단계: 자료구조 (동적 배열)
  13단계: 알고리즘 (정렬, 검색)
  14단계: 비트 연산 (플래그)
  16단계: 테스트 (assert 기반 자동 테스트)
*/


/* =========================================================================
 *  데이터 구조 정의
 * ========================================================================= */

#define MAX_NAME   50
#define MAX_PHONE  20
#define MAX_EMAIL  50
#define INITIAL_CAPACITY 4
#define DATA_FILE  "18_contacts.dat"

/* ── 연락처 구조체 ── */
typedef struct {
    char name[MAX_NAME];
    char phone[MAX_PHONE];
    char email[MAX_EMAIL];
    unsigned int flags;     /* 비트 플래그로 속성 관리 */
} Contact;

/* ── 비트 플래그 정의 (14단계) ── */
#define FLAG_FAVORITE  (1 << 0)    /* 즐겨찾기 */
#define FLAG_BLOCKED   (1 << 1)    /* 차단됨 */
#define FLAG_WORK      (1 << 2)    /* 업무용 */

/* ── 연락처 관리자 (동적 배열) ── */
typedef struct {
    Contact* data;      /* 동적 배열 (06단계) */
    int size;           /* 현재 연락처 수 */
    int capacity;       /* 할당된 용량 */
} ContactManager;

/* ── 테스트 매크로 (16단계) ── */
#define TEST_ASSERT(cond, msg) \
    do { \
        if (cond) { printf("    PASS: %s\n", msg); test_pass++; } \
        else { printf("    FAIL: %s\n", msg); test_fail++; } \
        test_total++; \
    } while(0)

static int test_total = 0;
static int test_pass = 0;
static int test_fail = 0;


/* =========================================================================
 *  함수 선언 (헤더 파일 역할)
 * ========================================================================= */

/* ── 관리자 생성/소멸 ── */
ContactManager* cm_create(void);
void cm_destroy(ContactManager* cm);

/* ── CRUD 연산 ── */
int cm_add(ContactManager* cm, const char* name,
           const char* phone, const char* email);
int cm_remove(ContactManager* cm, int index);
Contact* cm_find_by_name(ContactManager* cm, const char* name);
int cm_find_index(ContactManager* cm, const char* name);

/* ── 정렬 (13단계: qsort + 함수 포인터) ── */
void cm_sort_by_name(ContactManager* cm);

/* ── 파일 I/O (07단계) ── */
int cm_save(const ContactManager* cm, const char* filename);
int cm_load(ContactManager* cm, const char* filename);

/* ── 출력 ── */
void cm_print_all(const ContactManager* cm);
void cm_print_contact(const Contact* c);

/* ── 비트 플래그 (14단계) ── */
void cm_set_flag(Contact* c, unsigned int flag);
void cm_clear_flag(Contact* c, unsigned int flag);
int cm_has_flag(const Contact* c, unsigned int flag);

/* ── 테스트 ── */
void run_all_tests(void);


/* =========================================================================
 *  구현
 * ========================================================================= */

/* ── 관리자 생성 (06단계: malloc) ── */
ContactManager* cm_create(void) {
    ContactManager* cm = (ContactManager*)malloc(sizeof(ContactManager));
    if (cm == NULL) return NULL;

    cm->data = (Contact*)calloc(INITIAL_CAPACITY, sizeof(Contact));
    if (cm->data == NULL) {
        free(cm);
        return NULL;
    }

    cm->size = 0;
    cm->capacity = INITIAL_CAPACITY;
    return cm;
}

/* ── 관리자 소멸 (06단계: free) ── */
void cm_destroy(ContactManager* cm) {
    if (cm == NULL) return;
    free(cm->data);
    cm->data = NULL;
    cm->size = 0;
    cm->capacity = 0;
    free(cm);
}

/* ── 연락처 추가 (06단계: realloc, 12단계: 동적 배열) ── */
int cm_add(ContactManager* cm, const char* name,
           const char* phone, const char* email) {
    /* 방어적 프로그래밍 (11단계) */
    if (cm == NULL || name == NULL) return -1;

    /* 용량 부족 시 2배 확장 */
    if (cm->size >= cm->capacity) {
        int new_cap = cm->capacity * 2;
        Contact* temp = (Contact*)realloc(cm->data,
                                          sizeof(Contact) * new_cap);
        if (temp == NULL) return -1;
        cm->data = temp;
        cm->capacity = new_cap;
    }

    /* 안전한 문자열 복사 (09단계) */
    Contact* c = &cm->data[cm->size];
    snprintf(c->name,  MAX_NAME,  "%s", name ? name : "");
    snprintf(c->phone, MAX_PHONE, "%s", phone ? phone : "");
    snprintf(c->email, MAX_EMAIL, "%s", email ? email : "");
    c->flags = 0;

    cm->size++;
    return 0;
}

/* ── 연락처 삭제 ── */
int cm_remove(ContactManager* cm, int index) {
    if (cm == NULL || index < 0 || index >= cm->size) return -1;

    /* 삭제: 뒤의 원소들을 한 칸씩 앞으로 이동 */
    for (int i = index; i < cm->size - 1; i++) {
        cm->data[i] = cm->data[i + 1];
    }
    cm->size--;
    return 0;
}

/* ── 이름으로 검색 (13단계: 선형 검색 + 09단계: strstr) ── */
Contact* cm_find_by_name(ContactManager* cm, const char* name) {
    if (cm == NULL || name == NULL) return NULL;

    for (int i = 0; i < cm->size; i++) {
        /* 부분 문자열 검색 (대소문자 구분) */
        if (strstr(cm->data[i].name, name) != NULL) {
            return &cm->data[i];
        }
    }
    return NULL;
}

int cm_find_index(ContactManager* cm, const char* name) {
    if (cm == NULL || name == NULL) return -1;
    for (int i = 0; i < cm->size; i++) {
        if (strcmp(cm->data[i].name, name) == 0) return i;
    }
    return -1;
}

/* ── 정렬 (13단계: qsort + 10단계: 함수 포인터) ── */
int compare_contacts(const void* a, const void* b) {
    const Contact* ca = (const Contact*)a;
    const Contact* cb = (const Contact*)b;
    return strcmp(ca->name, cb->name);
}

void cm_sort_by_name(ContactManager* cm) {
    if (cm == NULL || cm->size <= 1) return;
    qsort(cm->data, cm->size, sizeof(Contact), compare_contacts);
}

/* ── 파일 저장 (07단계: fprintf) ── */
int cm_save(const ContactManager* cm, const char* filename) {
    if (cm == NULL || filename == NULL) return -1;

    FILE* fp = fopen(filename, "w");
    if (fp == NULL) return -1;

    fprintf(fp, "%d\n", cm->size);
    for (int i = 0; i < cm->size; i++) {
        const Contact* c = &cm->data[i];
        fprintf(fp, "%s\n%s\n%s\n%u\n",
                c->name, c->phone, c->email, c->flags);
    }

    fclose(fp);
    return 0;
}

/* ── 파일 불러오기 (07단계: fgets, fscanf) ── */
int cm_load(ContactManager* cm, const char* filename) {
    if (cm == NULL || filename == NULL) return -1;

    FILE* fp = fopen(filename, "r");
    if (fp == NULL) return -1;

    int count;
    if (fscanf(fp, "%d\n", &count) != 1) {
        fclose(fp);
        return -1;
    }

    char name[MAX_NAME], phone[MAX_PHONE], email[MAX_EMAIL];
    unsigned int flags;

    for (int i = 0; i < count; i++) {
        if (fgets(name, MAX_NAME, fp) == NULL) break;
        if (fgets(phone, MAX_PHONE, fp) == NULL) break;
        if (fgets(email, MAX_EMAIL, fp) == NULL) break;
        if (fscanf(fp, "%u\n", &flags) != 1) break;

        /* 줄바꿈 제거 */
        name[strcspn(name, "\n")] = '\0';
        phone[strcspn(phone, "\n")] = '\0';
        email[strcspn(email, "\n")] = '\0';

        cm_add(cm, name, phone, email);
        cm->data[cm->size - 1].flags = flags;
    }

    fclose(fp);
    return 0;
}

/* ── 출력 ── */
void cm_print_contact(const Contact* c) {
    if (c == NULL) return;
    printf("    이름: %-15s 전화: %-15s 이메일: %s",
           c->name, c->phone, c->email);

    /* 플래그 표시 (14단계) */
    if (c->flags) {
        printf(" [");
        if (cm_has_flag(c, FLAG_FAVORITE)) printf("★");
        if (cm_has_flag(c, FLAG_BLOCKED))  printf("차단");
        if (cm_has_flag(c, FLAG_WORK))     printf("업무");
        printf("]");
    }
    printf("\n");
}

void cm_print_all(const ContactManager* cm) {
    if (cm == NULL || cm->size == 0) {
        printf("    (연락처가 비어있습니다)\n");
        return;
    }
    for (int i = 0; i < cm->size; i++) {
        printf("    [%d] ", i);
        cm_print_contact(&cm->data[i]);
    }
    printf("    ── 총 %d명 (용량: %d) ──\n", cm->size, cm->capacity);
}

/* ── 비트 플래그 (14단계) ── */
void cm_set_flag(Contact* c, unsigned int flag) {
    if (c) c->flags |= flag;
}
void cm_clear_flag(Contact* c, unsigned int flag) {
    if (c) c->flags &= ~flag;
}
int cm_has_flag(const Contact* c, unsigned int flag) {
    return c ? (c->flags & flag) != 0 : 0;
}


/* =========================================================================
 *  메인: 데모 실행
 * ========================================================================= */
int main(void) {
    printf("========================================\n");
    printf("  C 18단계 : 실전 미니 프로젝트\n");
    printf("  ── 연락처 관리 프로그램 ──\n");
    printf("========================================\n\n");


    /* ─────────────────────────────────────────── */
    printf("┌──────────────────────────────────────┐\n");
    printf("│  1. 연락처 추가 및 출력               │\n");
    printf("└──────────────────────────────────────┘\n\n");

    ContactManager* cm = cm_create();
    if (cm == NULL) {
        printf("  메모리 할당 실패!\n");
        return 1;
    }

    cm_add(cm, "Kim",  "010-1234-5678", "kim@email.com");
    cm_add(cm, "Lee",  "010-9876-5432", "lee@email.com");
    cm_add(cm, "Park", "010-5555-1234", "park@email.com");
    cm_add(cm, "Choi", "010-7777-8888", "choi@email.com");
    cm_add(cm, "Jung", "010-3333-4444", "jung@email.com");

    printf("  ■ 전체 연락처\n");
    cm_print_all(cm);


    /* ─────────────────────────────────────────── */
    printf("\n┌──────────────────────────────────────┐\n");
    printf("│  2. 이름순 정렬                       │\n");
    printf("└──────────────────────────────────────┘\n\n");

    cm_sort_by_name(cm);
    printf("  ■ 정렬 후\n");
    cm_print_all(cm);


    /* ─────────────────────────────────────────── */
    printf("\n┌──────────────────────────────────────┐\n");
    printf("│  3. 검색                              │\n");
    printf("└──────────────────────────────────────┘\n\n");

    printf("  ■ 'Lee' 검색\n");
    Contact* found = cm_find_by_name(cm, "Lee");
    if (found) {
        printf("    발견! ");
        cm_print_contact(found);
    } else {
        printf("    없음\n");
    }

    printf("\n  ■ 'Yoo' 검색\n");
    found = cm_find_by_name(cm, "Yoo");
    printf("    %s\n", found ? "발견" : "없음");


    /* ─────────────────────────────────────────── */
    printf("\n┌──────────────────────────────────────┐\n");
    printf("│  4. 비트 플래그 설정                  │\n");
    printf("└──────────────────────────────────────┘\n\n");

    found = cm_find_by_name(cm, "Kim");
    if (found) {
        cm_set_flag(found, FLAG_FAVORITE);
        cm_set_flag(found, FLAG_WORK);
    }

    found = cm_find_by_name(cm, "Park");
    if (found) {
        cm_set_flag(found, FLAG_BLOCKED);
    }

    printf("  ■ 플래그 설정 후\n");
    cm_print_all(cm);


    /* ─────────────────────────────────────────── */
    printf("\n┌──────────────────────────────────────┐\n");
    printf("│  5. 삭제                              │\n");
    printf("└──────────────────────────────────────┘\n\n");

    int idx = cm_find_index(cm, "Park");
    if (idx >= 0) {
        printf("  ■ 'Park' 삭제 (인덱스 %d)\n", idx);
        cm_remove(cm, idx);
    }
    cm_print_all(cm);


    /* ─────────────────────────────────────────── */
    printf("\n┌──────────────────────────────────────┐\n");
    printf("│  6. 파일 저장 및 불러오기              │\n");
    printf("└──────────────────────────────────────┘\n\n");

    printf("  ■ 파일에 저장\n");
    if (cm_save(cm, DATA_FILE) == 0) {
        printf("    %s 에 저장 완료 (%d명)\n", DATA_FILE, cm->size);
    }

    /* 새 관리자에 불러오기 */
    printf("\n  ■ 새 관리자에 불러오기\n");
    ContactManager* cm2 = cm_create();
    if (cm_load(cm2, DATA_FILE) == 0) {
        printf("    %s 에서 불러오기 완료\n", DATA_FILE);
        cm_print_all(cm2);
    }
    cm_destroy(cm2);


    /* ─────────────────────────────────────────── */
    printf("\n┌──────────────────────────────────────┐\n");
    printf("│  7. 자동 테스트                       │\n");
    printf("└──────────────────────────────────────┘\n\n");

    run_all_tests();


    /* 정리 */
    cm_destroy(cm);

    /*
    ★ 프로젝트 체크리스트
    ─────────────────────────────────────
    □ 모든 malloc 에 대응하는 free 가 있는가?
    □ NULL 검사를 빠뜨리지 않았는가?
    □ 파일을 열었으면 반드시 닫았는가?
    □ 문자열 복사 시 버퍼 오버플로를 방지했는가?
    □ 경계값으로 테스트했는가?
    □ 함수 포인터를 활용해 확장성을 확보했는가?
    ─────────────────────────────────────
    */

    printf("\n18단계 학습 완료!\n");
    printf("축하합니다! C 언어 전체 학습 과정을 마쳤습니다.\n");
    return 0;
}


/* =========================================================================
 *  자동 테스트 (16단계)
 * ========================================================================= */
void run_all_tests(void) {
    printf("  ■ 자동화 테스트 실행\n\n");

    /* ── 테스트 1: 생성/소멸 ── */
    {
        ContactManager* t = cm_create();
        TEST_ASSERT(t != NULL, "cm_create 성공");
        TEST_ASSERT(t->size == 0, "초기 size == 0");
        TEST_ASSERT(t->capacity == INITIAL_CAPACITY, "초기 capacity");
        cm_destroy(t);
    }

    /* ── 테스트 2: 추가 ── */
    {
        ContactManager* t = cm_create();
        TEST_ASSERT(cm_add(t, "A", "010", "a@b") == 0, "add 성공");
        TEST_ASSERT(t->size == 1, "add 후 size == 1");
        TEST_ASSERT(strcmp(t->data[0].name, "A") == 0, "name 확인");
        cm_destroy(t);
    }

    /* ── 테스트 3: 용량 확장 ── */
    {
        ContactManager* t = cm_create();
        for (int i = 0; i < 10; i++) {
            char name[10];
            snprintf(name, sizeof(name), "P%d", i);
            cm_add(t, name, "", "");
        }
        TEST_ASSERT(t->size == 10, "10개 추가 성공");
        TEST_ASSERT(t->capacity >= 10, "용량 자동 확장");
        cm_destroy(t);
    }

    /* ── 테스트 4: 검색 ── */
    {
        ContactManager* t = cm_create();
        cm_add(t, "Alice", "010", "");
        cm_add(t, "Bob", "011", "");
        TEST_ASSERT(cm_find_by_name(t, "Alice") != NULL, "Alice 검색 성공");
        TEST_ASSERT(cm_find_by_name(t, "Charlie") == NULL, "없는 이름 검색");
        cm_destroy(t);
    }

    /* ── 테스트 5: 삭제 ── */
    {
        ContactManager* t = cm_create();
        cm_add(t, "X", "", "");
        cm_add(t, "Y", "", "");
        cm_add(t, "Z", "", "");
        cm_remove(t, 1);   /* Y 삭제 */
        TEST_ASSERT(t->size == 2, "삭제 후 size == 2");
        TEST_ASSERT(strcmp(t->data[1].name, "Z") == 0, "삭제 후 Z가 인덱스 1");
        cm_destroy(t);
    }

    /* ── 테스트 6: 정렬 ── */
    {
        ContactManager* t = cm_create();
        cm_add(t, "Charlie", "", "");
        cm_add(t, "Alice", "", "");
        cm_add(t, "Bob", "", "");
        cm_sort_by_name(t);
        TEST_ASSERT(strcmp(t->data[0].name, "Alice") == 0, "정렬 후 첫번째");
        TEST_ASSERT(strcmp(t->data[2].name, "Charlie") == 0, "정렬 후 마지막");
        cm_destroy(t);
    }

    /* ── 테스트 7: 비트 플래그 ── */
    {
        Contact c;
        memset(&c, 0, sizeof(c));
        cm_set_flag(&c, FLAG_FAVORITE);
        TEST_ASSERT(cm_has_flag(&c, FLAG_FAVORITE), "즐겨찾기 설정");
        TEST_ASSERT(!cm_has_flag(&c, FLAG_BLOCKED), "차단 미설정");
        cm_clear_flag(&c, FLAG_FAVORITE);
        TEST_ASSERT(!cm_has_flag(&c, FLAG_FAVORITE), "즐겨찾기 해제");
    }

    /* ── 테스트 8: 방어적 프로그래밍 ── */
    {
        TEST_ASSERT(cm_add(NULL, "A", "", "") == -1, "NULL cm 에 add 실패");
        TEST_ASSERT(cm_find_by_name(NULL, "A") == NULL, "NULL cm 에서 검색");
        TEST_ASSERT(cm_remove(NULL, 0) == -1, "NULL cm 에서 삭제");
    }

    /* ── 테스트 9: 파일 저장/불러오기 ── */
    {
        ContactManager* t1 = cm_create();
        cm_add(t1, "Save", "010", "save@test");
        cm_set_flag(&t1->data[0], FLAG_WORK);
        cm_save(t1, "18_test_save.dat");

        ContactManager* t2 = cm_create();
        cm_load(t2, "18_test_save.dat");
        TEST_ASSERT(t2->size == 1, "파일 로드 후 size == 1");
        TEST_ASSERT(strcmp(t2->data[0].name, "Save") == 0, "파일 로드 이름");
        TEST_ASSERT(cm_has_flag(&t2->data[0], FLAG_WORK), "파일 로드 플래그");

        cm_destroy(t1);
        cm_destroy(t2);
        remove("18_test_save.dat");     /* 테스트 파일 정리 */
    }

    /* ── 결과 출력 ── */
    printf("\n  ═══════════════════════════════════\n");
    printf("  테스트 결과: %d 실행, %d 성공, %d 실패\n",
           test_total, test_pass, test_fail);
    printf("  ═══════════════════════════════════\n");
}
