/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C++ 학습 02단계: 제어문 (조건문, 반복문)
  ─ if, switch, for, while, break, continue ─

  프로그램의 "흐름"을 제어하는 방법을 배웁니다.
  조건에 따라 다른 코드를 실행하거나, 같은 코드를 반복할 수 있습니다.

  ■ 컴파일: g++ -std=c++17 -Wall -o 02_control main.cpp

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/
#include <iostream>
#include <string>
#include <vector>
using namespace std;

void lesson1_if_else();
void lesson2_switch();
void lesson3_for_loop();
void lesson4_while_loop();
void lesson5_break_continue();
void lesson6_nested_loops();
void lesson7_practical_exercises();

int main() {
    cout << "========================================" << endl;
    cout << "  C++ 02단계 : 제어문" << endl;
    cout << "========================================" << endl;
    cout << endl;

    lesson1_if_else();
    lesson2_switch();
    lesson3_for_loop();
    lesson4_while_loop();
    lesson5_break_continue();
    lesson6_nested_loops();
    lesson7_practical_exercises();

    cout << "\n02단계 학습 완료!\n";
    return 0;
}


// =========================================================================
//  레슨 1 — if / else if / else
// =========================================================================
void lesson1_if_else() {
    cout << "┌──────────────────────────────────────┐" << endl;
    cout << "│  레슨 1 : if / else if / else        │" << endl;
    cout << "└──────────────────────────────────────┘" << endl;
    cout << endl;

    // ─── if문이란? ───
    //
    //   "만약 ~라면, 이것을 해라"
    //
    //   비유: 신호등
    //     초록불이면 → 건넌다
    //     빨간불이면 → 멈춘다
    //
    //   구조:
    //   ┌───────────────────────────────────┐
    //   │  if (조건) {                      │
    //   │      조건이 참(true)이면 실행     │
    //   │  }                                │
    //   │  else if (다른 조건) {             │
    //   │      위가 거짓이고 이것이 참이면  │
    //   │  }                                │
    //   │  else {                           │
    //   │      위 모든 조건이 거짓이면      │
    //   │  }                                │
    //   └───────────────────────────────────┘
    //
    //   핵심: 위에서 아래로 순서대로 검사하고,
    //         처음 참인 블록 하나만 실행!

    // ─── 기본 예제: 성적 등급 ───
    int score = 85;
    cout << "  ■ 성적 판정 (score = " << score << ")" << endl;
    cout << "  ─────────────────────────────────────" << endl;

    if (score >= 90) {
        cout << "  등급: A (수)" << endl;
    }
    else if (score >= 80) {
        cout << "  등급: B (우)" << endl;     // ← 여기 실행! (85 >= 80)
    }
    else if (score >= 70) {
        cout << "  등급: C (미)" << endl;
    }
    else if (score >= 60) {
        cout << "  등급: D (양)" << endl;
    }
    else {
        cout << "  등급: F (가)" << endl;
    }
    cout << endl;

    // ─── 삼항 연산자 ───
    //
    //   if/else를 한 줄로 줄인 것
    //   형식:  조건 ? 참일때값 : 거짓일때값
    //
    //   비유: "합격했어?" → "응" or "아니"

    string result = (score >= 60) ? "합격" : "불합격";
    cout << "  삼항 연산자: " << score << "점 → " << result << endl;

    // 중첩 삼항 (가독성 나쁨 → 복잡하면 if/else 쓸 것!)
    string grade = (score >= 90) ? "A" :
                   (score >= 80) ? "B" :
                   (score >= 70) ? "C" : "F";
    cout << "  중첩 삼항:   " << score << "점 → " << grade << "등급" << endl;
    cout << endl;

    // ─── 논리 연산자 조합 ───
    int age = 20;
    bool has_ticket = true;
    bool is_vip = false;

    cout << "  ■ 논리 조합 (나이=" << age
         << ", 티켓=" << has_ticket
         << ", VIP=" << is_vip << ")" << endl;
    cout << "  ─────────────────────────────────────" << endl;

    // && (AND): 둘 다 참이어야 참
    if (age >= 18 && has_ticket) {
        cout << "  입장 가능 (성인 + 티켓)" << endl;
    }

    // || (OR): 하나만 참이면 참
    if (is_vip || has_ticket) {
        cout << "  입장 가능 (VIP거나 티켓)" << endl;
    }

    // ! (NOT): 반전
    if (!is_vip) {
        cout << "  VIP가 아닙니다" << endl;
    }
    cout << endl;

    // ─── if with 초기화 (C++17) ───
    //
    //   변수를 if 안에서만 쓰고 싶을 때
    //   변수의 범위(스코프)가 if 블록으로 제한되어 깔끔!

    cout << "  ■ if + 초기화 (C++17)" << endl;
    cout << "  ─────────────────────────────────────" << endl;

    if (int remainder = 17 % 3; remainder == 0) {
        cout << "  17은 3의 배수" << endl;
    } else {
        cout << "  17 % 3 = " << remainder << " (3의 배수 아님)" << endl;
    }
    // remainder는 여기서 접근 불가! (스코프가 if 안으로 제한)
    cout << endl;

    // ─── 흔한 실수들 ───
    //
    //   ★ 실수 #1: = 와 == 혼동
    //     if (x = 5)   ← 대입! 항상 true!
    //     if (x == 5)  ← 비교! 올바름!
    //
    //   ★ 실수 #2: 중괄호 빠뜨림
    //     if (x > 0)
    //         cout << "양수";
    //         cout << "이 줄은 항상 실행됨!";  ← if와 무관!
    //
    //     → 항상 중괄호 {}를 쓰는 습관을 들이자!
    //
    //   ★ 실수 #3: 세미콜론 잘못 넣기
    //     if (x > 0);   ← 이 세미콜론 때문에 if가 아무것도 안 함!
    //     {
    //         cout << "양수";  ← 항상 실행됨
    //     }
}


// =========================================================================
//  레슨 2 — switch
// =========================================================================
void lesson2_switch() {
    cout << "┌──────────────────────────────────────┐" << endl;
    cout << "│  레슨 2 : switch 문                  │" << endl;
    cout << "└──────────────────────────────────────┘" << endl;
    cout << endl;

    // ─── switch란? ───
    //
    //   하나의 값을 여러 값과 비교할 때 if/else보다 깔끔!
    //
    //   비유: 엘리베이터 버튼
    //     1 누르면 → 1층
    //     2 누르면 → 2층
    //     3 누르면 → 3층
    //     그 외   → "없는 층입니다"
    //
    //   ★ 제한: int, char, enum만 가능!
    //           string, double은 switch 사용 불가 → if/else 써야 함
    //
    //   ★ break를 빼먹으면 다음 case로 "떨어진다" (fall-through)!
    //     → 가장 흔한 switch 버그!

    int menu = 2;
    cout << "  ■ 메뉴 선택 (menu = " << menu << ")" << endl;
    cout << "  ─────────────────────────────────────" << endl;

    switch (menu) {
        case 1:
            cout << "  새 게임" << endl;
            break;      // ← break 필수! 없으면 다음 case도 실행됨!
        case 2:
            cout << "  이어하기" << endl;
            break;
        case 3:
            cout << "  설정" << endl;
            break;
        case 4:
            cout << "  종료" << endl;
            break;
        default:
            cout << "  잘못된 입력!" << endl;
            break;
    }
    cout << endl;

    // ─── 의도적 fall-through ───
    //
    //   여러 case를 같은 방식으로 처리할 때
    //   break를 생략하여 합침

    char grade = 'B';
    cout << "  ■ 등급 판정 (grade = '" << grade << "')" << endl;
    cout << "  ─────────────────────────────────────" << endl;

    switch (grade) {
        case 'A':
        case 'B':          // A 또는 B → 같은 처리
            cout << "  우수한 성적!" << endl;
            break;
        case 'C':
        case 'D':          // C 또는 D → 같은 처리
            cout << "  보통 성적" << endl;
            break;
        case 'F':
            cout << "  재수강 필요" << endl;
            break;
        default:
            cout << "  알 수 없는 등급" << endl;
    }
    cout << endl;

    // ─── switch에서 변수 선언 시 주의 ───
    //
    //   case 안에서 변수를 선언하려면 {} 블록으로 감싸야 함!
    //
    //   switch (x) {
    //       case 1: {          // {} 필요!
    //           int value = 10;
    //           cout << value;
    //           break;
    //       }
    //   }
}


// =========================================================================
//  레슨 3 — for 반복문
// =========================================================================
void lesson3_for_loop() {
    cout << "┌──────────────────────────────────────┐" << endl;
    cout << "│  레슨 3 : for 반복문                 │" << endl;
    cout << "└──────────────────────────────────────┘" << endl;
    cout << endl;

    // ─── for문이란? ───
    //
    //   "정해진 횟수만큼 반복"할 때 사용
    //
    //   구조:
    //   for (①초기화;  ②조건;  ④증감) {
    //       ③반복할 코드
    //   }
    //
    //   실행 순서:
    //   ① 초기화 (딱 1번만)
    //   ② 조건 검사 → false면 탈출
    //   ③ 본문 실행
    //   ④ 증감 실행
    //   ② 로 돌아감
    //
    //   비유: "1번부터 10번까지 출석 부르기"
    //     for (번호=1; 번호<=10; 번호++) { "여기!" }

    // ── 기본: 1부터 5까지 ──
    cout << "  ■ 기본 for문" << endl;
    cout << "  1~5: ";
    for (int i = 1; i <= 5; i++) {
        cout << i << " ";
    }
    cout << endl;

    // ── 역순: 5부터 1까지 ──
    cout << "  5~1: ";
    for (int i = 5; i >= 1; i--) {
        cout << i << " ";
    }
    cout << endl;

    // ── 짝수만: 2씩 증가 ──
    cout << "  짝수: ";
    for (int i = 2; i <= 10; i += 2) {
        cout << i << " ";
    }
    cout << endl;

    // ── 3씩 감소 ──
    cout << "  30부터 3씩 감소: ";
    for (int i = 30; i > 0; i -= 3) {
        cout << i << " ";
    }
    cout << endl;
    cout << endl;

    // ─── 범위 기반 for (C++11) ───
    //
    //   배열이나 vector의 모든 요소를 하나씩 꺼내서 처리
    //   파이썬의 "for item in list:" 와 같은 개념
    //
    //   for (타입 변수 : 컨테이너) { ... }
    //   for (auto 변수 : 컨테이너) { ... }   ← auto 추천

    cout << "  ■ 범위 기반 for (C++11)" << endl;
    cout << "  ─────────────────────────────────────" << endl;

    int scores[] = {95, 82, 71, 88, 63};

    // 값 복사 (원본 변경 안 됨)
    cout << "  점수: ";
    for (int s : scores) {
        cout << s << " ";
    }
    cout << endl;

    // const auto& : 복사 없이 참조로 읽기 (큰 객체에서 성능 좋음)
    cout << "  과일: ";
    string fruits[] = {"사과", "바나나", "체리", "딸기"};
    for (const auto& f : fruits) {
        cout << f << " ";
    }
    cout << endl;

    // 합계 & 평균
    int sum = 0;
    for (int s : scores) {
        sum += s;
    }
    int count = sizeof(scores) / sizeof(scores[0]);
    cout << "  합계: " << sum << "  평균: " << (sum / count) << endl;
    cout << endl;

    // ─── 언제 어떤 for를 쓸까? ───
    //
    //   인덱스가 필요하면 → 기본 for (int i = 0; ...)
    //   요소만 필요하면  → 범위 기반 for (for auto& x : v)
    //   요소를 수정하면  → for (auto& x : v) { x = ...; }  (& 필수!)
}


// =========================================================================
//  레슨 4 — while / do-while
// =========================================================================
void lesson4_while_loop() {
    cout << "┌──────────────────────────────────────┐" << endl;
    cout << "│  레슨 4 : while / do-while           │" << endl;
    cout << "└──────────────────────────────────────┘" << endl;
    cout << endl;

    // ─── while vs do-while vs for ───
    //
    //   ┌─────────────┬──────────────────────────────────┐
    //   │ for         │ 반복 횟수를 미리 알 때            │
    //   │ while       │ 조건이 참인 동안 (0번도 가능)     │
    //   │ do-while    │ 최소 1번은 반드시 실행            │
    //   └─────────────┴──────────────────────────────────┘
    //
    //   while (조건) {       do {
    //       본문                 본문
    //   }                   } while (조건);  ← 세미콜론!

    // ── while: 2의 거듭제곱 ──
    cout << "  ■ while (2의 거듭제곱, 1000 미만)" << endl;
    cout << "  ";
    int power = 1;
    while (power < 1000) {
        cout << power << " ";
        power *= 2;
    }
    cout << endl;

    // ── while: 자릿수 세기 ──
    int number = 123456;
    int digits = 0;
    int temp = number;
    while (temp > 0) {
        digits++;
        temp /= 10;     // 10으로 나누면 맨 뒤 자릿수 제거
    }
    cout << "  " << number << "의 자릿수: " << digits << endl;
    cout << endl;

    // ── do-while: 최소 1번 실행 ──
    cout << "  ■ do-while (최소 1번 실행)" << endl;
    int count = 0;
    do {
        cout << "  실행 #" << count << endl;
        count++;
    } while (count < 1);   // 조건이 false여도 이미 1번 실행됨!
    cout << endl;

    // ─── 무한루프 패턴 ───
    //
    //   while (true) { ... break; }
    //
    //   실무에서 자주 쓰이는 패턴:
    //   - 사용자 입력 대기
    //   - 게임 메인 루프
    //   - 서버 요청 대기
    //
    //   ★ 반드시 break 탈출 조건을 넣을 것!
    //     안 그러면 → Ctrl + C 로 강제 종료해야 함

    cout << "  ■ 무한루프 + break 패턴" << endl;
    int attempt = 0;
    while (true) {
        attempt++;
        cout << "  시도 #" << attempt << endl;
        if (attempt >= 3) {
            cout << "  → 3번 시도 후 탈출!" << endl;
            break;
        }
    }
    cout << endl;

    // ─── 무한루프에 빠지는 흔한 실수 ───
    //
    //   실수 1: 증감 빠뜨림
    //     int i = 0;
    //     while (i < 10) {
    //         cout << i;
    //         // i++ 깜빡함!  → 영원히 0 출력
    //     }
    //
    //   실수 2: 조건이 항상 참
    //     while (true) {
    //         // break 없음 → 영원히 반복
    //     }
    //
    //   실수 3: 부호 실수
    //     for (int i = 10; i >= 0; i++) {  // i-- 여야 하는데 i++
    //         // 영원히 증가 → 무한루프
    //     }
    //
    //   해결: Ctrl + C (터미널에서 강제 종료)
}


// =========================================================================
//  레슨 5 — break와 continue
// =========================================================================
void lesson5_break_continue() {
    cout << "┌──────────────────────────────────────┐" << endl;
    cout << "│  레슨 5 : break와 continue           │" << endl;
    cout << "└──────────────────────────────────────┘" << endl;
    cout << endl;

    // ─── break vs continue ───
    //
    //   break    : 반복문을 즉시 탈출 (바깥으로 나감)
    //   continue : 이번 회차만 건너뛰고 다음 회차로
    //
    //   그림:
    //   for (...) {           for (...) {
    //       ...                   ...
    //       break; ──→ 탈출     continue; ──┐
    //       ...  (실행 안됨)     ... (건너뜀)│
    //   } ← 여기로             }  ←─────────┘
    //   ↓ 다음 코드

    // ── break: 찾으면 즉시 중단 ──
    cout << "  ■ break — 배열에서 30 찾기" << endl;
    int arr[] = {10, 20, 30, 40, 50};
    for (int i = 0; i < 5; i++) {
        cout << "  검사: arr[" << i << "] = " << arr[i];
        if (arr[i] == 30) {
            cout << " ← 찾았다! 중단!" << endl;
            break;   // 더 이상 검사하지 않고 탈출
        }
        cout << endl;
    }
    cout << endl;

    // ── continue: 건너뛰기 ──
    cout << "  ■ continue — 짝수만 출력" << endl;
    cout << "  ";
    for (int i = 1; i <= 10; i++) {
        if (i % 2 != 0) {
            continue;   // 홀수면 아래를 건너뛰고 다음 i로
        }
        cout << i << " ";
    }
    cout << endl;
    cout << endl;

    // ── 실용 예제: 음수 무시하고 합계 ──
    cout << "  ■ 실용 — 양수만 합산" << endl;
    int data[] = {5, -3, 8, -1, 7, -4, 2};
    int sum = 0;
    for (int val : data) {
        if (val < 0) continue;   // 음수 건너뛰기
        sum += val;
    }
    cout << "  양수 합계: " << sum << endl;
    cout << endl;
}


// =========================================================================
//  레슨 6 — 중첩 반복문
// =========================================================================
void lesson6_nested_loops() {
    cout << "┌──────────────────────────────────────┐" << endl;
    cout << "│  레슨 6 : 중첩 반복문                │" << endl;
    cout << "└──────────────────────────────────────┘" << endl;
    cout << endl;

    // ─── 중첩 반복문이란? ───
    //
    //   반복문 안에 또 반복문
    //   바깥 루프 = 행(row),  안쪽 루프 = 열(column) 으로 생각
    //
    //   ★ 중첩이 3단 이상이면 함수로 분리하는 것이 좋다
    //     (가독성이 급격히 나빠짐)

    // ── 구구단 ──
    cout << "  ■ 구구단 (2~3단)" << endl;
    cout << "  ─────────────────────────────────────" << endl;
    for (int dan = 2; dan <= 3; dan++) {
        cout << "  [" << dan << "단]" << endl;
        for (int i = 1; i <= 9; i++) {
            cout << "    " << dan << " x " << i << " = " << (dan * i) << endl;
        }
    }
    cout << endl;

    // ── 별 찍기: 직각 삼각형 ──
    cout << "  ■ 직각 삼각형" << endl;
    for (int row = 1; row <= 5; row++) {
        cout << "  ";
        for (int col = 0; col < row; col++) {
            cout << "* ";
        }
        cout << endl;
    }
    cout << endl;

    // ── 별 찍기: 피라미드 ──
    cout << "  ■ 피라미드" << endl;
    int height = 5;
    for (int row = 1; row <= height; row++) {
        // 공백 출력
        cout << "  ";
        for (int sp = 0; sp < height - row; sp++) {
            cout << " ";
        }
        // 별 출력
        for (int st = 0; st < 2 * row - 1; st++) {
            cout << "*";
        }
        cout << endl;
    }
    cout << endl;

    // ── 중첩 루프에서 break 주의 ──
    //
    //   break는 가장 안쪽 루프만 탈출!
    //   바깥 루프까지 탈출하려면:
    //   1. 플래그 변수 사용
    //   2. 함수로 분리하고 return
    //   3. goto (비추천)

    cout << "  ■ 중첩 break (플래그 방식)" << endl;
    bool found = false;
    for (int i = 0; i < 3 && !found; i++) {
        for (int j = 0; j < 3; j++) {
            cout << "  (" << i << "," << j << ")";
            if (i == 1 && j == 1) {
                cout << " ← 찾음!";
                found = true;
                break;   // 안쪽 루프 탈출
            }
        }
        cout << endl;
    }
    cout << endl;
}


// =========================================================================
//  레슨 7 — 실전 연습 문제
// =========================================================================
void lesson7_practical_exercises() {
    cout << "┌──────────────────────────────────────┐" << endl;
    cout << "│  레슨 7 : 실전 연습                  │" << endl;
    cout << "└──────────────────────────────────────┘" << endl;
    cout << endl;

    // ── 연습 1: FizzBuzz ──
    //   1~30까지 수에서:
    //   3의 배수면 "Fizz", 5의 배수면 "Buzz", 둘 다면 "FizzBuzz"
    cout << "  ■ FizzBuzz (1~20)" << endl;
    cout << "  ";
    for (int i = 1; i <= 20; i++) {
        if (i % 15 == 0)      cout << "FizzBuzz ";
        else if (i % 3 == 0)  cout << "Fizz ";
        else if (i % 5 == 0)  cout << "Buzz ";
        else                  cout << i << " ";
    }
    cout << endl << endl;

    // ── 연습 2: 소수 판별 ──
    cout << "  ■ 소수 판별 (2~30)" << endl;
    cout << "  소수: ";
    for (int num = 2; num <= 30; num++) {
        bool is_prime = true;
        for (int div = 2; div * div <= num; div++) {
            if (num % div == 0) {
                is_prime = false;
                break;
            }
        }
        if (is_prime) cout << num << " ";
    }
    cout << endl << endl;

    // ── 연습 3: 배열에서 최대값 찾기 ──
    cout << "  ■ 최대값 찾기" << endl;
    int data[] = {34, 67, 23, 89, 12, 56, 78, 45};
    int max_val = data[0];
    int max_idx = 0;
    for (int i = 1; i < 8; i++) {
        if (data[i] > max_val) {
            max_val = data[i];
            max_idx = i;
        }
    }
    cout << "  데이터: ";
    for (int d : data) cout << d << " ";
    cout << endl;
    cout << "  최대값: " << max_val << " (인덱스: " << max_idx << ")" << endl;
    cout << endl;
}
