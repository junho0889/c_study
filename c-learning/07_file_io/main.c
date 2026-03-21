/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C 학습 07단계: 파일 입출력
  ─ fopen, fclose, fprintf, fscanf, fgets, fread, fwrite ─

  파일은 프로그램이 꺼져도 데이터가 남는 유일한 방법입니다.
  이 단계에서는 텍스트 파일과 바이너리 파일을 모두 다룹니다.

  ■ 컴파일: gcc -std=c11 -Wall -o 07_fileio main.c
  ■ 실행:   ./07_fileio

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void lesson1_fopen_modes(void);
void lesson2_text_write(void);
void lesson3_text_read(void);
void lesson4_binary_io(void);
void lesson5_file_position(void);
void lesson6_error_handling(void);
void lesson7_practical(void);

int main(void) {
    printf("========================================\n");
    printf("  C 07단계 : 파일 입출력\n");
    printf("========================================\n\n");

    lesson1_fopen_modes();
    lesson2_text_write();
    lesson3_text_read();
    lesson4_binary_io();
    lesson5_file_position();
    lesson6_error_handling();
    lesson7_practical();

    printf("\n07단계 학습 완료!\n");
    return 0;
}


/* =========================================================================
 *  레슨 1 — fopen 모드 총정리
 * ========================================================================= */
void lesson1_fopen_modes(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 1 : fopen 열기 모드             │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ fopen 함수 원형:
      FILE* fopen(const char* filename, const char* mode);

    ★ 비유:
      파일 열기는 책을 펼치는 것과 같습니다.
      - "r" = 읽기 전용으로 책 펼치기
      - "w" = 새 노트에 쓰기 (기존 내용은 지워짐!)
      - "a" = 기존 노트 뒤에 이어 쓰기
      닫기(fclose) = 책을 덮는 것

    ★ 파일 열기 모드 표
    ┌──────┬──────────────┬─────────────┬──────────────────┐
    │ 모드 │ 의미         │ 파일 없으면 │ 파일 있으면       │
    ├──────┼──────────────┼─────────────┼──────────────────┤
    │ "r"  │ 읽기         │ 실패(NULL)  │ 처음부터 읽기     │
    │ "w"  │ 쓰기         │ 새로 생성   │ 내용 지우고 쓰기  │
    │ "a"  │ 이어쓰기     │ 새로 생성   │ 끝에 이어 쓰기    │
    │ "r+" │ 읽기+쓰기    │ 실패(NULL)  │ 처음부터          │
    │ "w+" │ 읽기+쓰기    │ 새로 생성   │ 내용 지우고       │
    │ "a+" │ 읽기+이어쓰기│ 새로 생성   │ 읽기는 처음부터,  │
    │      │              │             │ 쓰기는 끝에       │
    ├──────┼──────────────┴─────────────┴──────────────────┤
    │ "rb" │ 바이너리 읽기 ("r" + 바이너리)               │
    │ "wb" │ 바이너리 쓰기 ("w" + 바이너리)               │
    │ "ab" │ 바이너리 이어쓰기                             │
    └──────┴───────────────────────────────────────────────┘

    ★ 주의!
      "w" 모드는 기존 파일 내용을 완전히 지웁니다!
      기존 데이터를 보존하려면 "a" 를 쓰세요.
    */

    printf("  파일 모드는 위 주석의 표를 참고하세요.\n");
    printf("  핵심: r=읽기, w=쓰기(덮어씀!), a=이어쓰기\n");
    printf("  바이너리: 뒤에 b 를 붙임 (rb, wb, ab)\n\n");
}


/* =========================================================================
 *  레슨 2 — 텍스트 파일 쓰기
 * ========================================================================= */
void lesson2_text_write(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 2 : 텍스트 파일 쓰기            │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 텍스트 파일 쓰기 함수들:
      fprintf(fp, format, ...)  → printf 와 동일, 대상이 파일
      fputs(str, fp)            → 문자열 그대로 쓰기 (줄바꿈 안 붙음)
      fputc(ch, fp)             → 문자 하나 쓰기
    */

    /* ── fprintf 로 쓰기 ── */
    printf("  ■ fprintf 로 파일 쓰기\n");
    FILE* fp = fopen("07_output.txt", "w");
    if (fp == NULL) {
        printf("    파일 열기 실패!\n\n");
        return;
    }

    fprintf(fp, "이름: 민수\n");
    fprintf(fp, "점수: %d\n", 95);
    fprintf(fp, "등급: %c\n", 'A');

    fclose(fp);     /* ★ 반드시 닫기! */
    printf("    07_output.txt 에 3줄 기록 완료\n");

    /* ── fputs 로 이어쓰기 ── */
    printf("\n  ■ fputs 로 이어쓰기 (append)\n");
    fp = fopen("07_output.txt", "a");
    if (fp != NULL) {
        fputs("--- 추가 메모 ---\n", fp);
        fputs("C 파일 입출력 연습 중\n", fp);
        fclose(fp);
        printf("    2줄 추가 기록 완료\n");
    }

    printf("\n");
}


/* =========================================================================
 *  레슨 3 — 텍스트 파일 읽기
 * ========================================================================= */
void lesson3_text_read(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 3 : 텍스트 파일 읽기            │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 텍스트 파일 읽기 함수들:
    ┌───────────────────┬──────────────────────────────────┐
    │ 함수              │ 설명                              │
    ├───────────────────┼──────────────────────────────────┤
    │ fgets(buf, n, fp) │ 한 줄 읽기 (최대 n-1 글자)       │
    │                   │ ★ 줄바꿈 문자도 포함됨!          │
    │ fscanf(fp, ...)   │ 형식에 맞춰 읽기 (scanf 와 비슷) │
    │ fgetc(fp)         │ 문자 하나 읽기                    │
    │ feof(fp)          │ 파일 끝인지 확인                  │
    └───────────────────┴──────────────────────────────────┘

    ★ 비유:
      fgets  = 한 줄씩 읽는 것 (줄 단위 번역)
      fscanf = 정해진 양식에서 값을 뽑아내는 것 (설문지 판독)
      fgetc  = 한 글자씩 읽는 것 (돋보기로 한 자 한 자)
    */

    /* ── fgets 로 한 줄씩 읽기 ── */
    printf("  ■ fgets 로 한 줄씩 읽기\n");
    FILE* fp = fopen("07_output.txt", "r");
    if (fp == NULL) {
        printf("    파일 열기 실패 (레슨 2 먼저 실행하세요)\n\n");
        return;
    }

    char line[256];
    int line_num = 1;
    while (fgets(line, sizeof(line), fp) != NULL) {
        /* fgets 는 줄바꿈을 포함하므로 그대로 출력 */
        printf("    %d: %s", line_num, line);
        line_num++;
    }
    fclose(fp);

    /* ── fscanf 로 형식 읽기 ── */
    printf("\n  ■ fscanf 로 형식 데이터 읽기\n");

    /* 먼저 형식 파일 생성 */
    fp = fopen("07_scores.txt", "w");
    if (fp != NULL) {
        fprintf(fp, "Kim 85\nLee 92\nPark 78\n");
        fclose(fp);
    }

    fp = fopen("07_scores.txt", "r");
    if (fp != NULL) {
        char name[50];
        int score;
        while (fscanf(fp, "%49s %d", name, &score) == 2) {
            printf("    이름: %-6s 점수: %d\n", name, score);
        }
        fclose(fp);
    }

    printf("\n");
}


/* =========================================================================
 *  레슨 4 — 바이너리 파일 입출력
 * ========================================================================= */
typedef struct {
    char name[20];
    int age;
    double height;
} Person;

void lesson4_binary_io(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 4 : 바이너리 파일 입출력        │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 바이너리 파일이란?
      텍스트 파일: 사람이 읽을 수 있는 문자로 저장
      바이너리 파일: 메모리 데이터를 그대로 저장

    ★ fwrite / fread 함수:
      size_t fwrite(const void* ptr, size_t size, size_t count, FILE* fp);
      size_t fread (void* ptr,       size_t size, size_t count, FILE* fp);

      - ptr   : 데이터 시작 주소
      - size  : 항목 하나의 크기 (바이트)
      - count : 항목 개수
      - 반환  : 실제로 쓴/읽은 항목 수

    ★ 비유:
      텍스트 파일 = 편지 (사람이 읽음)
      바이너리 파일 = 택배 상자 (내용물 그대로 포장)
      → 속도가 빠르고 용량이 작지만, 사람이 직접 읽기 어려움
    */

    /* ── 구조체를 바이너리로 쓰기 ── */
    printf("  ■ 구조체 배열을 바이너리로 저장\n");
    Person people[3] = {
        {"Kim",  25, 175.5},
        {"Lee",  30, 168.0},
        {"Park", 22, 180.2}
    };

    FILE* fp = fopen("07_people.bin", "wb");
    if (fp == NULL) {
        printf("    파일 열기 실패!\n\n");
        return;
    }

    size_t written = fwrite(people, sizeof(Person), 3, fp);
    printf("    %zu 명의 데이터 기록 완료\n", written);
    fclose(fp);

    /* ── 바이너리로 읽기 ── */
    printf("\n  ■ 바이너리에서 구조체 읽기\n");
    Person loaded[3];
    fp = fopen("07_people.bin", "rb");
    if (fp != NULL) {
        size_t read_count = fread(loaded, sizeof(Person), 3, fp);
        fclose(fp);

        for (size_t i = 0; i < read_count; i++) {
            printf("    %s, %d세, %.1fcm\n",
                   loaded[i].name, loaded[i].age, loaded[i].height);
        }
    }

    printf("\n");
}


/* =========================================================================
 *  레슨 5 — 파일 위치 제어
 * ========================================================================= */
void lesson5_file_position(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 5 : 파일 위치 제어 (seek/tell) │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 파일 위치 함수들:
    ┌─────────────────────┬──────────────────────────────┐
    │ 함수                │ 설명                          │
    ├─────────────────────┼──────────────────────────────┤
    │ ftell(fp)           │ 현재 위치(바이트) 반환        │
    │ fseek(fp, off, org) │ 위치 이동                     │
    │ rewind(fp)          │ 맨 앞으로 이동                │
    └─────────────────────┴──────────────────────────────┘

    ★ fseek 의 기준점 (origin):
      SEEK_SET = 파일 시작 (0)
      SEEK_CUR = 현재 위치
      SEEK_END = 파일 끝

    ★ 비유:
      ftell  = "지금 책의 몇 페이지를 보고 있는가?"
      fseek  = "50페이지로 건너뛰기"
      rewind = "표지로 돌아가기"
    */

    /* 바이너리 파일에서 2번째 레코드만 읽기 */
    printf("  ■ fseek 로 2번째 레코드만 읽기\n");
    FILE* fp = fopen("07_people.bin", "rb");
    if (fp == NULL) {
        printf("    파일 열기 실패 (레슨 4 먼저 실행)\n\n");
        return;
    }

    /* 2번째 레코드로 이동 (인덱스 1) */
    fseek(fp, sizeof(Person) * 1, SEEK_SET);
    printf("    현재 위치: %ld 바이트\n", ftell(fp));

    Person p;
    if (fread(&p, sizeof(Person), 1, fp) == 1) {
        printf("    2번째 사람: %s, %d세\n", p.name, p.age);
    }

    /* 파일 크기 구하기 */
    fseek(fp, 0, SEEK_END);
    long file_size = ftell(fp);
    printf("    파일 크기: %ld 바이트\n", file_size);

    fclose(fp);
    printf("\n");
}


/* =========================================================================
 *  레슨 6 — 에러 처리
 * ========================================================================= */
void lesson6_error_handling(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 6 : 파일 에러 처리              │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ 파일 에러 처리 원칙:
      1. fopen 반환값 반드시 NULL 검사
      2. fread/fwrite 반환값으로 실제 처리 개수 확인
      3. ferror(fp) 로 에러 발생 여부 확인
      4. perror("메시지") 로 시스템 에러 출력
      5. 어떤 경로에서든 fclose 를 보장

    ★ 비유:
      파일을 여는 것은 수돗물 틀기와 같습니다.
      → 성공 확인 (물이 나오는지?)
      → 사용 후 반드시 잠그기 (fclose)
      → 안 잠그면 자원 낭비 (file descriptor 누수)
    */

    /* ── 존재하지 않는 파일 열기 시도 ── */
    printf("  ■ 존재하지 않는 파일 열기\n");
    FILE* fp = fopen("no_such_file_xyz.txt", "r");
    if (fp == NULL) {
        perror("    fopen 실패");   /* 시스템 에러 메시지 출력 */
        printf("    → fopen 은 실패 시 NULL 을 반환합니다.\n\n");
    }

    /* ── 안전한 파일 읽기 패턴 ── */
    printf("  ■ 안전한 파일 읽기 패턴\n");
    fp = fopen("07_output.txt", "r");
    if (fp != NULL) {
        char buf[100];
        if (fgets(buf, sizeof(buf), fp) != NULL) {
            printf("    첫 줄: %s", buf);
        }
        if (ferror(fp)) {
            printf("    ★ 읽기 중 에러 발생!\n");
        }
        fclose(fp);
    } else {
        printf("    파일 열기 실패\n");
    }

    printf("\n");
}


/* =========================================================================
 *  레슨 7 — 실전: 설정 파일 읽기/쓰기
 * ========================================================================= */
void lesson7_practical(void) {
    printf("┌──────────────────────────────────────┐\n");
    printf("│  레슨 7 : 실전 — 설정 파일 관리       │\n");
    printf("└──────────────────────────────────────┘\n\n");

    /*
    ★ key=value 형태의 간단한 설정 파일을 만들고 읽기
    */

    /* ── 설정 파일 쓰기 ── */
    printf("  ■ 설정 파일 쓰기\n");
    FILE* fp = fopen("07_config.ini", "w");
    if (fp == NULL) {
        printf("    파일 생성 실패\n\n");
        return;
    }

    fprintf(fp, "# 프로그램 설정 파일\n");
    fprintf(fp, "username=admin\n");
    fprintf(fp, "max_retry=3\n");
    fprintf(fp, "timeout=30\n");
    fprintf(fp, "debug=true\n");
    fclose(fp);
    printf("    07_config.ini 생성 완료\n");

    /* ── 설정 파일 읽기 ── */
    printf("\n  ■ 설정 파일 읽기\n");
    fp = fopen("07_config.ini", "r");
    if (fp == NULL) {
        printf("    파일 열기 실패\n\n");
        return;
    }

    char line[256];
    while (fgets(line, sizeof(line), fp) != NULL) {
        /* 주석(#) 과 빈 줄 건너뛰기 */
        if (line[0] == '#' || line[0] == '\n') continue;

        /* 줄바꿈 제거 */
        line[strcspn(line, "\n")] = '\0';

        /* key=value 파싱 */
        char* eq = strchr(line, '=');
        if (eq != NULL) {
            *eq = '\0';     /* '=' 을 널 문자로 바꿔 key 분리 */
            char* key = line;
            char* value = eq + 1;
            printf("    키: %-12s 값: %s\n", key, value);
        }
    }
    fclose(fp);

    /*
    ★ 파일 입출력 체크리스트
    ─────────────────────────────────────
    □ fopen 후 NULL 검사 했는가?
    □ 모든 경로에서 fclose 를 보장하는가?
    □ "w" 모드로 중요 파일을 덮어쓰지 않았는가?
    □ fgets 버퍼 크기를 충분히 잡았는가?
    □ 바이너리/텍스트 모드를 올바르게 선택했는가?
    ─────────────────────────────────────
    */

    printf("\n");
}
