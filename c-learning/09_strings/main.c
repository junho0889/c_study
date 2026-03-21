/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C 학습 09단계: 문자열
  ─ char 배열, 널 문자, string.h 함수, 안전한 문자열 처리 ─

  C에는 string 타입이 없습니다.
  문자열은 "널 문자('\0')로 끝나는 char 배열"일 뿐입니다.
  이 단순한 구조가 수많은 버그의 원인이기도 합니다.

  ■ 컴파일: gcc -std=c11 -Wall -o 09_strings main.c
  ■ 실행:   ./09_strings

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdlib.h>

void lesson1_char_array_basics(void);
void lesson2_null_terminator(void);
void lesson3_string_functions(void);
void lesson4_string_search(void);
void lesson5_string_conversion(void);
void lesson6_safe_string(void);
void lesson7_common_mistakes(void);
void lesson8_practical(void);

int main(void) {
    printf("========================================\n");
    printf("  C 09단계 : 문자열\n");
    printf("========================================\n\n");

    lesson1_char_array_basics();
    lesson2_null_terminator();
    lesson3_string_functions();
    lesson4_string_search();
    lesson5_string_conversion();
    lesson6_safe_string();
    lesson7_common_mistakes();
    lesson8_practical();

    printf("\n09단계 학습 완료!\n");
    return 0;
}


/* =========================================================================
 *  레슨 1 — 문자 배열 기초
 * ========================================================================= */
void lesson1_char_array_basics(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 1 : 문자 배열 기초              │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ C 문자열 = 널 문자('\0')로 끝나는 char 배열

    ★ 비유:
      문자열은 기차 객차와 같습니다.
      각 객차(char)에 한 글자씩 탑승하고,
      맨 뒤 객차에는 "끝" 표시('\0')가 붙어 있습니다.
      이 표시가 없으면 기차가 어디서 끝나는지 모릅니다!

    ★ 문자열 선언 방법:
    ┌───────────────────────────────┬────────────────────────┐
    │ 방법                         │ 설명                    │
    ├───────────────────────────────┼────────────────────────┤
    │ char s[] = "Hello";          │ 크기 자동 (6바이트)     │
    │ char s[10] = "Hello";        │ 크기 명시 (여유 공간)   │
    │ char s[] = {'H','e','l',0};  │ 한 글자씩 + 널문자     │
    │ char* s = "Hello";           │ 문자열 리터럴 포인터    │
    │                              │ ★ 수정 불가!            │
    └───────────────────────────────┴────────────────────────┘
    */

    /* ── 배열 방식 (수정 가능) ── */
    printf("  ■ char 배열 방식\n");
    char greeting[] = "Hello";
    printf("    greeting = \"%s\"\n", greeting);
    printf("    sizeof   = %zu (널 문자 포함)\n", sizeof(greeting));
    printf("    strlen   = %zu (널 문자 미포함)\n", strlen(greeting));

    greeting[0] = 'h';     /* 수정 가능 */
    printf("    수정 후: \"%s\"\n", greeting);

    /* ── 포인터 방식 (수정 불가) ── */
    printf("\n  ■ 포인터 방식 (읽기 전용)\n");
    const char* message = "World";
    printf("    message = \"%s\"\n", message);
    /* message[0] = 'w';  ← 이러면 정의되지 않은 동작! */
    printf("    ★ 문자열 리터럴은 수정하면 안 됩니다!\n");

    /* ── 메모리 배치 ── */
    /*
      char name[] = "Cat";

      메모리 배치:
      ┌─────┬─────┬─────┬─────┐
      │ 'C' │ 'a' │ 't' │ '\0'│
      ├─────┼─────┼─────┼─────┤
      │ [0] │ [1] │ [2] │ [3] │
      └─────┴─────┴─────┴─────┘
      sizeof = 4,  strlen = 3
    */

    printf("\n");
}


/* =========================================================================
 *  레슨 2 — 널 문자의 중요성
 * ========================================================================= */
void lesson2_null_terminator(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 2 : 널 문자 ('\\0') 의 중요성   │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 널 문자('\0') = 문자열의 끝 표시 = 정수 0

    ★ 비유:
      책의 "끝" 표시가 없으면 어디까지 읽어야 할지 모르듯,
      '\0' 이 없으면 printf, strlen, strcpy 등 모든 함수가
      메모리를 쓰레기 값까지 계속 읽어갑니다.

    ★ '\0' vs '0' vs 0 vs NULL:
    ┌───────────┬─────────┬─────────────────────────┐
    │ 표현      │ 값      │ 의미                     │
    ├───────────┼─────────┼─────────────────────────┤
    │ '\0'      │ 0       │ 널 문자 (문자열 끝)      │
    │ '0'       │ 48      │ 숫자 0 의 문자           │
    │ 0         │ 0       │ 정수 0                   │
    │ NULL      │ 0       │ 널 포인터                │
    └───────────┴─────────┴─────────────────────────┘
    */

    /* ── 널 문자 확인 ── */
    printf("  ■ 널 문자 확인\n");
    char word[] = "ABC";
    printf("    word[0] = '%c' (%d)\n", word[0], word[0]);
    printf("    word[1] = '%c' (%d)\n", word[1], word[1]);
    printf("    word[2] = '%c' (%d)\n", word[2], word[2]);
    printf("    word[3] = '%c' (%d)  ← 널 문자!\n", word[3] ? word[3] : '?', word[3]);

    /* ── 널 문자가 없으면? ── */
    printf("\n  ■ 널 문자가 없는 경우 (위험!)\n");
    char bad[3] = {'A', 'B', 'C'};    /* '\0' 없음! */
    printf("    sizeof(bad) = %zu\n", sizeof(bad));
    /* printf("  bad = %%s", bad);  ← 쓰레기 값까지 읽을 수 있어 위험 */
    printf("    ★ 이 배열을 %%s 로 출력하면 널 문자를 만날 때까지\n");
    printf("      메모리를 계속 읽으므로 위험합니다!\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 3 — string.h 주요 함수
 * ========================================================================= */
void lesson3_string_functions(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 3 : string.h 주요 함수         │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ string.h 핵심 함수:
    ┌─────────────────────┬──────────────────────────────────┐
    │ 함수                │ 설명                              │
    ├─────────────────────┼──────────────────────────────────┤
    │ strlen(s)           │ 문자열 길이 ('\0' 미포함)         │
    │ strcpy(dst, src)    │ 문자열 복사 ★위험!               │
    │ strncpy(d, s, n)    │ 최대 n 글자 복사 (더 안전)       │
    │ strcat(dst, src)    │ 문자열 이어붙이기 ★위험!         │
    │ strncat(d, s, n)    │ 최대 n 글자 이어붙이기            │
    │ strcmp(a, b)         │ 비교: 0이면 같음                 │
    │ strncmp(a, b, n)    │ 최대 n 글자만 비교                │
    │ memset(ptr, val, n) │ n 바이트를 val 로 채우기          │
    │ memcpy(d, s, n)     │ n 바이트 복사                    │
    └─────────────────────┴──────────────────────────────────┘
    */

    /* ── strlen ── */
    printf("  ■ strlen\n");
    char text[] = "Hello, C!";
    printf("    strlen(\"%s\") = %zu\n", text, strlen(text));

    /* ── strcpy / strncpy ── */
    printf("\n  ■ strcpy / strncpy\n");
    char src[] = "Original";
    char dst[20];

    strcpy(dst, src);
    printf("    strcpy  → dst = \"%s\"\n", dst);

    char safe_dst[5];
    strncpy(safe_dst, src, sizeof(safe_dst) - 1);
    safe_dst[sizeof(safe_dst) - 1] = '\0';    /* ★ 반드시 널 종료! */
    printf("    strncpy → safe_dst = \"%s\" (잘림)\n", safe_dst);

    /* ── strcat / strncat ── */
    printf("\n  ■ strcat / strncat\n");
    char buf[30] = "Hello";
    strcat(buf, " ");
    strcat(buf, "World");
    printf("    strcat → \"%s\"\n", buf);

    char buf2[15] = "Hi";
    strncat(buf2, " there everyone!", sizeof(buf2) - strlen(buf2) - 1);
    printf("    strncat → \"%s\" (안전하게 잘림)\n", buf2);

    /* ── strcmp ── */
    printf("\n  ■ strcmp\n");
    printf("    strcmp(\"abc\", \"abc\") = %d (같음)\n", strcmp("abc", "abc"));
    printf("    strcmp(\"abc\", \"abd\") = %d (abc < abd)\n", strcmp("abc", "abd"));
    printf("    strcmp(\"abd\", \"abc\") = %d (abd > abc)\n", strcmp("abd", "abc"));

    /*
    ★ strcmp 반환값:
      0  → 같음
      <0 → 첫 번째가 사전순으로 앞
      >0 → 첫 번째가 사전순으로 뒤
    */

    printf("\n");
}


/* =========================================================================
 *  레슨 4 — 문자열 검색
 * ========================================================================= */
void lesson4_string_search(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 4 : 문자열 검색                 │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 검색 함수:
    ┌────────────────────┬──────────────────────────────┐
    │ 함수               │ 설명                          │
    ├────────────────────┼──────────────────────────────┤
    │ strchr(s, c)       │ 문자 c 의 첫 위치 찾기       │
    │ strrchr(s, c)      │ 문자 c 의 마지막 위치 찾기   │
    │ strstr(hay, needle)│ 부분 문자열 찾기              │
    │ strcspn(s, reject) │ reject 에 없는 문자 길이     │
    │ strspn(s, accept)  │ accept 에 있는 문자 길이     │
    │ strtok(s, delim)   │ 문자열 토큰 분리              │
    └────────────────────┴──────────────────────────────┘
    */

    char sentence[] = "The quick brown fox jumps over the lazy dog";

    /* ── strchr / strrchr ── */
    printf("  ■ strchr / strrchr\n");
    char* found = strchr(sentence, 'o');
    if (found) printf("    첫 번째 'o' 위치: 인덱스 %td\n", found - sentence);

    found = strrchr(sentence, 'o');
    if (found) printf("    마지막 'o' 위치: 인덱스 %td\n", found - sentence);

    /* ── strstr ── */
    printf("\n  ■ strstr (부분 문자열 찾기)\n");
    found = strstr(sentence, "fox");
    if (found) printf("    \"fox\" 발견! 위치: 인덱스 %td\n", found - sentence);

    found = strstr(sentence, "cat");
    printf("    \"cat\" 검색: %s\n", found ? "발견" : "없음");

    /* ── strtok (토큰 분리) ── */
    printf("\n  ■ strtok (쉼표로 분리)\n");
    char csv[] = "apple,banana,cherry,date";
    char* token = strtok(csv, ",");
    int idx = 1;
    while (token != NULL) {
        printf("    토큰 %d: %s\n", idx++, token);
        token = strtok(NULL, ",");   /* 이후 호출은 NULL 전달 */
    }
    /*
    ★ strtok 주의!
      - 원본 문자열을 수정함! (구분자를 '\0'으로 바꿈)
      - 내부 상태를 유지하므로 스레드 안전하지 않음
      - 원본을 보존하려면 복사본을 만들어 사용
    */

    printf("\n");
}


/* =========================================================================
 *  레슨 5 — 문자열 변환
 * ========================================================================= */
void lesson5_string_conversion(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 5 : 문자열 ↔ 숫자 변환         │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 변환 함수:
    ┌────────────────────┬──────────────────────────────┐
    │ 함수               │ 설명                          │
    ├────────────────────┼──────────────────────────────┤
    │ atoi(s)            │ 문자열 → int                  │
    │ atof(s)            │ 문자열 → double               │
    │ atol(s)            │ 문자열 → long                 │
    │ strtol(s, end, b)  │ 문자열 → long (더 안전)       │
    │ strtod(s, end)     │ 문자열 → double (더 안전)     │
    │ sprintf(buf, ...)  │ 숫자 → 문자열                 │
    │ snprintf(b, n, ...)│ 안전한 숫자 → 문자열           │
    └────────────────────┴──────────────────────────────┘
    */

    /* ── 문자열 → 숫자 ── */
    printf("  ■ 문자열 → 숫자\n");
    printf("    atoi(\"42\")   = %d\n", atoi("42"));
    printf("    atoi(\"  -7\") = %d\n", atoi("  -7"));
    printf("    atof(\"3.14\") = %.2f\n", atof("3.14"));

    /* ── strtol (더 안전한 변환) ── */
    printf("\n  ■ strtol (에러 감지 가능)\n");
    char* endptr;
    long val = strtol("123abc", &endptr, 10);
    printf("    strtol(\"123abc\") = %ld\n", val);
    printf("    변환 안 된 부분: \"%s\"\n", endptr);

    /* ── 숫자 → 문자열 ── */
    printf("\n  ■ 숫자 → 문자열 (snprintf)\n");
    char buffer[50];
    snprintf(buffer, sizeof(buffer), "점수: %d, 평균: %.1f", 95, 87.5);
    printf("    결과: \"%s\"\n", buffer);

    /* ── ctype.h: 문자 분류/변환 ── */
    printf("\n  ■ ctype.h 문자 분류\n");
    char ch = 'A';
    printf("    isalpha('%c') = %d\n", ch, isalpha(ch) != 0);
    printf("    isdigit('3')  = %d\n", isdigit('3') != 0);
    printf("    toupper('a')  = '%c'\n", toupper('a'));
    printf("    tolower('Z')  = '%c'\n", tolower('Z'));

    printf("\n");
}


/* =========================================================================
 *  레슨 6 — 안전한 문자열 처리
 * ========================================================================= */
void lesson6_safe_string(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 6 : 안전한 문자열 처리          │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ C 문자열의 3대 위험:
      1. 버퍼 오버플로 (Buffer Overflow)
         → 배열 크기보다 긴 문자열 복사
      2. 널 종료 누락
         → strncpy 가 널 문자를 안 넣을 수 있음
      3. off-by-one 에러
         → 널 문자 자리를 깜빡하고 1 부족하게 할당

    ★ 안전한 패턴:
      strncpy(dst, src, sizeof(dst) - 1);
      dst[sizeof(dst) - 1] = '\0';

    ★ snprintf 는 항상 널 종료를 보장합니다 (추천!)
    */

    printf("  ■ 위험한 예 (strcpy 오버플로)\n");
    printf("    char small[5];\n");
    printf("    strcpy(small, \"Very long string\"); ← 버퍼 오버플로!\n\n");

    printf("  ■ 안전한 예 (snprintf 사용)\n");
    char safe[10];
    snprintf(safe, sizeof(safe), "%s", "Very long string");
    printf("    snprintf 결과: \"%s\" (자동 잘림, 널 종료 보장)\n", safe);

    /* ── 안전한 문자열 이어붙이기 ── */
    printf("\n  ■ 안전한 이어붙이기\n");
    char result[20] = "Hello";
    size_t remaining = sizeof(result) - strlen(result) - 1;
    strncat(result, " World!!", remaining);
    printf("    결과: \"%s\"\n", result);
    printf("    남은 공간 계산이 핵심입니다.\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 7 — 자주 하는 실수
 * ========================================================================= */
void lesson7_common_mistakes(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 7 : 문자열 실수 모음            │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 문자열 실수 모음:

    ┌────┬────────────────────────┬──────────────────────────┐
    │ #  │ 실수                   │ 올바른 방법              │
    ├────┼────────────────────────┼──────────────────────────┤
    │ 1  │ == 로 문자열 비교      │ strcmp 사용               │
    │ 2  │ 배열에 = 로 대입       │ strcpy / snprintf 사용   │
    │ 3  │ sizeof 로 길이 구하기  │ strlen 사용              │
    │ 4  │ 리터럴 수정 시도       │ char 배열에 복사 후 수정 │
    │ 5  │ gets 사용              │ fgets 사용 (gets 는 금지)│
    └────┴────────────────────────┴──────────────────────────┘
    */

    /* ── 실수 1: == 로 비교 ── */
    printf("  ■ 실수 1: == 로 문자열 비교\n");
    char a[] = "hello";
    char b[] = "hello";
    printf("    a == b ? %s (주소 비교!)\n", a == b ? "같음" : "다름");
    printf("    strcmp(a,b) == 0 ? %s (내용 비교!)\n",
           strcmp(a, b) == 0 ? "같음" : "다름");

    /* ── 실수 2: 배열에 = 대입 ── */
    printf("\n  ■ 실수 2: 배열에 = 로 대입 불가\n");
    printf("    char s[10]; s = \"hello\";  ← 컴파일 에러!\n");
    printf("    올바른: strcpy(s, \"hello\");\n");

    /* ── 실수 3: sizeof vs strlen ── */
    printf("\n  ■ 실수 3: sizeof 와 strlen 혼동\n");
    char arr[20] = "Hi";
    printf("    sizeof(arr) = %zu (배열 전체 크기)\n", sizeof(arr));
    printf("    strlen(arr) = %zu (실제 문자 수)\n", strlen(arr));

    /* ── 실수 5: gets 사용 금지 ── */
    printf("\n  ■ 실수 5: gets() 사용 금지!\n");
    printf("    gets 는 입력 길이를 제한하지 않아\n");
    printf("    버퍼 오버플로 공격의 원인이 됩니다.\n");
    printf("    ★ C11 에서 gets 는 제거되었습니다.\n");
    printf("    → fgets(buf, sizeof(buf), stdin) 을 사용하세요.\n");

    printf("\n");
}


/* =========================================================================
 *  레슨 8 — 실전: 문자열 유틸리티
 * ========================================================================= */

/* 문자열 뒤집기 */
void reverse_string(char* str) {
    int len = (int)strlen(str);
    for (int i = 0; i < len / 2; i++) {
        char temp = str[i];
        str[i] = str[len - 1 - i];
        str[len - 1 - i] = temp;
    }
}

/* 단어 수 세기 */
int count_words(const char* str) {
    int count = 0;
    int in_word = 0;
    while (*str) {
        if (*str == ' ' || *str == '\t' || *str == '\n') {
            in_word = 0;
        } else if (!in_word) {
            in_word = 1;
            count++;
        }
        str++;
    }
    return count;
}

/* 대문자로 변환 */
void to_uppercase(char* str) {
    while (*str) {
        *str = (char)toupper((unsigned char)*str);
        str++;
    }
}

void lesson8_practical(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 8 : 실전 — 문자열 유틸리티      │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /* ── 문자열 뒤집기 ── */
    printf("  ■ 문자열 뒤집기\n");
    char rev[] = "Hello World";
    printf("    원본: \"%s\"\n", rev);
    reverse_string(rev);
    printf("    뒤집기: \"%s\"\n", rev);

    /* ── 단어 수 세기 ── */
    printf("\n  ■ 단어 수 세기\n");
    const char* text = "  The quick   brown fox  ";
    printf("    문장: \"%s\"\n", text);
    printf("    단어 수: %d\n", count_words(text));

    /* ── 대문자 변환 ── */
    printf("\n  ■ 대문자 변환\n");
    char upper[] = "hello world";
    printf("    원본: \"%s\"\n", upper);
    to_uppercase(upper);
    printf("    변환: \"%s\"\n", upper);

    /*
    ★ 문자열 처리 체크리스트
    ─────────────────────────────────────
    □ 버퍼 크기에 널 문자 자리(+1) 를 포함했는가?
    □ strncpy 후 널 종료를 보장했는가?
    □ strcmp 로 비교했는가? (== 사용 금지)
    □ 사용자 입력은 fgets 로 받았는가?
    □ 문자열 리터럴을 수정하지 않았는가?
    ─────────────────────────────────────
    */

    printf("\n");
}
