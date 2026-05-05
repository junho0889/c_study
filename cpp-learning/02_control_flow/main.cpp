/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C++ 학습 02단계: 제어문 (조건문, 반복문)
  ─ if, switch, for, while, break, continue ─

  프로그램의 "흐름"을 제어하는 방법을 배웁니다.

  ■ 컴파일: g++ -std=c++17 -Wall -o 02_control main.cpp

  ■ 주석 표기: // > 출력  // → 변수값  // ▶ 분기

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

    // ─── 기본 예제: 성적 등급 ───
    int score = 85;
    cout << "  ■ 성적 판정 (score = " << score << ")" << endl;
    // > 출력:   ■ 성적 판정 (score = 85)
    cout << "  ─────────────────────────────────────" << endl;

    // ▶ 검사 흐름:
    //   85 >= 90 ? false → 다음으로
    //   85 >= 80 ? true  → 이 블록 실행 후 if 사슬 종료
    if (score >= 90) {
        cout << "  등급: A (수)" << endl;
    }
    else if (score >= 80) {
        cout << "  등급: B (우)" << endl;
        // > 출력:   등급: B (우)         ← ★ 여기 실행
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
    string result = (score >= 60) ? "합격" : "불합격";
    // → 85 >= 60 ? true → "합격"
    // → result = "합격"
    cout << "  삼항 연산자: " << score << "점 → " << result << endl;
    // > 출력:   삼항 연산자: 85점 → 합격

    // 중첩 삼항
    string grade = (score >= 90) ? "A" :
                   (score >= 80) ? "B" :
                   (score >= 70) ? "C" : "F";
    // → 85 >= 90 ? false → 85 >= 80 ? true → "B"
    // → grade = "B"
    cout << "  중첩 삼항:   " << score << "점 → " << grade << "등급" << endl;
    // > 출력:   중첩 삼항:   85점 → B등급
    cout << endl;

    // ─── 논리 연산자 조합 ───
    int age = 20;
    bool has_ticket = true;
    bool is_vip = false;

    cout << "  ■ 논리 조합 (나이=" << age
         << ", 티켓=" << has_ticket
         << ", VIP=" << is_vip << ")" << endl;
    // > 출력:   ■ 논리 조합 (나이=20, 티켓=1, VIP=0)
    cout << "  ─────────────────────────────────────" << endl;

    if (age >= 18 && has_ticket) {
        // ▶ (20 >= 18) && true = true && true = true → 진입
        cout << "  입장 가능 (성인 + 티켓)" << endl;
        // > 출력:   입장 가능 (성인 + 티켓)
    }

    if (is_vip || has_ticket) {
        // ▶ false || true = true → 진입
        cout << "  입장 가능 (VIP거나 티켓)" << endl;
        // > 출력:   입장 가능 (VIP거나 티켓)
    }

    if (!is_vip) {
        // ▶ !false = true → 진입
        cout << "  VIP가 아닙니다" << endl;
        // > 출력:   VIP가 아닙니다
    }
    cout << endl;

    // ─── if with 초기화 (C++17) ───
    cout << "  ■ if + 초기화 (C++17)" << endl;
    cout << "  ─────────────────────────────────────" << endl;

    if (int remainder = 17 % 3; remainder == 0) {
        // → remainder = 17 % 3 = 2 (17 = 3*5 + 2)
        // ▶ 2 == 0 ? false → else 분기
        cout << "  17은 3의 배수" << endl;
    } else {
        cout << "  17 % 3 = " << remainder << " (3의 배수 아님)" << endl;
        // > 출력:   17 % 3 = 2 (3의 배수 아님)
    }
    cout << endl;
}


// =========================================================================
//  레슨 2 — switch
// =========================================================================
void lesson2_switch() {
    cout << "┌──────────────────────────────────────┐" << endl;
    cout << "│  레슨 2 : switch 문                  │" << endl;
    cout << "└──────────────────────────────────────┘" << endl;
    cout << endl;

    int menu = 2;
    cout << "  ■ 메뉴 선택 (menu = " << menu << ")" << endl;
    // > 출력:   ■ 메뉴 선택 (menu = 2)
    cout << "  ─────────────────────────────────────" << endl;

    // ▶ menu=2 → case 2: 진입
    switch (menu) {
        case 1:
            cout << "  새 게임" << endl;
            break;
        case 2:
            cout << "  이어하기" << endl;
            // > 출력:   이어하기                ← ★ 여기 실행
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
    char grade = 'B';
    cout << "  ■ 등급 판정 (grade = '" << grade << "')" << endl;
    // > 출력:   ■ 등급 판정 (grade = 'B')
    cout << "  ─────────────────────────────────────" << endl;

    // ▶ grade='B' → case 'A': fall-through → case 'B': 진입
    //   case 'A'에 break 없음 → 그대로 case 'B' 본문 실행
    switch (grade) {
        case 'A':
        case 'B':
            cout << "  우수한 성적!" << endl;
            // > 출력:   우수한 성적!         ← ★ 여기 실행
            break;
        case 'C':
        case 'D':
            cout << "  보통 성적" << endl;
            break;
        case 'F':
            cout << "  재수강 필요" << endl;
            break;
        default:
            cout << "  알 수 없는 등급" << endl;
    }
    cout << endl;
}


// =========================================================================
//  레슨 3 — for 반복문
// =========================================================================
void lesson3_for_loop() {
    cout << "┌──────────────────────────────────────┐" << endl;
    cout << "│  레슨 3 : for 반복문                 │" << endl;
    cout << "└──────────────────────────────────────┘" << endl;
    cout << endl;

    // ── 기본: 1부터 5까지 ──
    cout << "  ■ 기본 for문" << endl;
    cout << "  1~5: ";
    for (int i = 1; i <= 5; i++) {
        // 반복: i = 1, 2, 3, 4, 5 (5회)
        cout << i << " ";
    }
    cout << endl;
    // > 출력:   1~5: 1 2 3 4 5

    // ── 역순: 5부터 1까지 ──
    cout << "  5~1: ";
    for (int i = 5; i >= 1; i--) {
        // 반복: i = 5, 4, 3, 2, 1
        cout << i << " ";
    }
    cout << endl;
    // > 출력:   5~1: 5 4 3 2 1

    // ── 짝수만: 2씩 증가 ──
    cout << "  짝수: ";
    for (int i = 2; i <= 10; i += 2) {
        // 반복: i = 2, 4, 6, 8, 10
        cout << i << " ";
    }
    cout << endl;
    // > 출력:   짝수: 2 4 6 8 10

    // ── 3씩 감소 ──
    cout << "  30부터 3씩 감소: ";
    for (int i = 30; i > 0; i -= 3) {
        // 반복: i = 30, 27, 24, 21, 18, 15, 12, 9, 6, 3
        //   (i=0이 되면 i>0 false라 종료)
        cout << i << " ";
    }
    cout << endl;
    // > 출력:   30부터 3씩 감소: 30 27 24 21 18 15 12 9 6 3
    cout << endl;

    // ─── 범위 기반 for (C++11) ───
    cout << "  ■ 범위 기반 for (C++11)" << endl;
    cout << "  ─────────────────────────────────────" << endl;

    int scores[] = {95, 82, 71, 88, 63};
    // → 5개 요소

    cout << "  점수: ";
    for (int s : scores) {
        // 반복: s = 95, 82, 71, 88, 63
        cout << s << " ";
    }
    cout << endl;
    // > 출력:   점수: 95 82 71 88 63

    cout << "  과일: ";
    string fruits[] = {"사과", "바나나", "체리", "딸기"};
    for (const auto& f : fruits) {
        // 반복: f = "사과", "바나나", "체리", "딸기"
        // const auto& : 복사 없이 참조
        cout << f << " ";
    }
    cout << endl;
    // > 출력:   과일: 사과 바나나 체리 딸기

    int sum = 0;
    for (int s : scores) {
        sum += s;
        // 누적: 0+95=95 → +82=177 → +71=248 → +88=336 → +63=399
    }
    // → sum = 399
    int count = sizeof(scores) / sizeof(scores[0]);
    // → 20 / 4 = 5
    cout << "  합계: " << sum << "  평균: " << (sum / count) << endl;
    // > 출력:   합계: 399  평균: 79      ← 399/5 = 79.8 → 정수 나눗셈으로 79
    cout << endl;
}


// =========================================================================
//  레슨 4 — while / do-while
// =========================================================================
void lesson4_while_loop() {
    cout << "┌──────────────────────────────────────┐" << endl;
    cout << "│  레슨 4 : while / do-while           │" << endl;
    cout << "└──────────────────────────────────────┘" << endl;
    cout << endl;

    // ── while: 2의 거듭제곱 ──
    cout << "  ■ while (2의 거듭제곱, 1000 미만)" << endl;
    cout << "  ";
    int power = 1;
    while (power < 1000) {
        // 반복: power = 1, 2, 4, 8, 16, 32, 64, 128, 256, 512
        //   1024 = 1000보다 크므로 출력 후 다음 *2 직전이 아니라
        //   "조건 검사 시 1024 < 1000 false"로 종료
        // 자세히:
        //   power=1   → 출력, power=2
        //   power=2   → 출력, power=4
        //   ...
        //   power=512 → 출력, power=1024
        //   power=1024→ 1024<1000 false → 종료
        cout << power << " ";
        power *= 2;
    }
    cout << endl;
    // > 출력:   1 2 4 8 16 32 64 128 256 512

    // ── while: 자릿수 세기 ──
    int number = 123456;
    int digits = 0;
    int temp = number;
    while (temp > 0) {
        // temp 변화: 123456 → 12345 → 1234 → 123 → 12 → 1 → 0
        // digits   :       0 →     1 →    2 →   3 →  4 →  5 → 6
        digits++;
        temp /= 10;
    }
    // → digits = 6
    cout << "  " << number << "의 자릿수: " << digits << endl;
    // > 출력:   123456의 자릿수: 6
    cout << endl;

    // ── do-while: 최소 1번 실행 ──
    cout << "  ■ do-while (최소 1번 실행)" << endl;
    int count = 0;
    do {
        // count=0 → 출력 후 count=1
        // 조건 1<1 false → 탈출
        cout << "  실행 #" << count << endl;
        // > 출력:   실행 #0
        count++;
    } while (count < 1);
    cout << endl;

    // ─── 무한루프 + break 패턴 ───
    cout << "  ■ 무한루프 + break 패턴" << endl;
    int attempt = 0;
    while (true) {
        attempt++;
        // attempt: 1, 2, 3
        cout << "  시도 #" << attempt << endl;
        // > 출력 (총 3회):
        //   시도 #1
        //   시도 #2
        //   시도 #3
        if (attempt >= 3) {
            // ▶ attempt=3 일 때만 진입
            cout << "  → 3번 시도 후 탈출!" << endl;
            // > 출력:   → 3번 시도 후 탈출!
            break;
        }
    }
    cout << endl;
}


// =========================================================================
//  레슨 5 — break와 continue
// =========================================================================
void lesson5_break_continue() {
    cout << "┌──────────────────────────────────────┐" << endl;
    cout << "│  레슨 5 : break와 continue           │" << endl;
    cout << "└──────────────────────────────────────┘" << endl;
    cout << endl;

    // ── break: 찾으면 즉시 중단 ──
    cout << "  ■ break — 배열에서 30 찾기" << endl;
    int arr[] = {10, 20, 30, 40, 50};

    // 반복: i=0 → 10, i=1 → 20, i=2 → 30(=찾음, break)
    //   i=3, 4는 검사 안 함
    for (int i = 0; i < 5; i++) {
        cout << "  검사: arr[" << i << "] = " << arr[i];
        if (arr[i] == 30) {
            cout << " ← 찾았다! 중단!" << endl;
            break;
        }
        cout << endl;
    }
    // > 출력:
    //   검사: arr[0] = 10
    //   검사: arr[1] = 20
    //   검사: arr[2] = 30 ← 찾았다! 중단!
    cout << endl;

    // ── continue: 건너뛰기 ──
    cout << "  ■ continue — 짝수만 출력" << endl;
    cout << "  ";
    for (int i = 1; i <= 10; i++) {
        // i: 1(홀, skip) 2(출력) 3(skip) 4(출력) 5(skip) 6(출력)
        //    7(skip) 8(출력) 9(skip) 10(출력)
        if (i % 2 != 0) {
            continue;
        }
        cout << i << " ";
    }
    cout << endl;
    // > 출력:   2 4 6 8 10
    cout << endl;

    // ── 실용 예제: 음수 무시하고 합계 ──
    cout << "  ■ 실용 — 양수만 합산" << endl;
    int data[] = {5, -3, 8, -1, 7, -4, 2};
    int sum = 0;
    for (int val : data) {
        // val = 5 → sum=5
        //        -3 → continue
        //         8 → sum=13
        //        -1 → continue
        //         7 → sum=20
        //        -4 → continue
        //         2 → sum=22
        if (val < 0) continue;
        sum += val;
    }
    // → sum = 5 + 8 + 7 + 2 = 22
    cout << "  양수 합계: " << sum << endl;
    // > 출력:   양수 합계: 22
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

    // ── 구구단 ──
    cout << "  ■ 구구단 (2~3단)" << endl;
    cout << "  ─────────────────────────────────────" << endl;
    for (int dan = 2; dan <= 3; dan++) {
        // 바깥: dan = 2, 3
        cout << "  [" << dan << "단]" << endl;
        for (int i = 1; i <= 9; i++) {
            // 안쪽: i = 1..9
            cout << "    " << dan << " x " << i << " = " << (dan * i) << endl;
        }
    }
    // > 출력:
    //   [2단]
    //     2 x 1 = 2
    //     2 x 2 = 4
    //     2 x 3 = 6
    //     2 x 4 = 8
    //     2 x 5 = 10
    //     2 x 6 = 12
    //     2 x 7 = 14
    //     2 x 8 = 16
    //     2 x 9 = 18
    //   [3단]
    //     3 x 1 = 3
    //     3 x 2 = 6
    //     3 x 3 = 9
    //     3 x 4 = 12
    //     3 x 5 = 15
    //     3 x 6 = 18
    //     3 x 7 = 21
    //     3 x 8 = 24
    //     3 x 9 = 27
    cout << endl;

    // ── 별 찍기: 직각 삼각형 ──
    cout << "  ■ 직각 삼각형" << endl;
    for (int row = 1; row <= 5; row++) {
        // row=1: "* "
        // row=2: "* * "
        // row=3: "* * * "
        // row=4: "* * * * "
        // row=5: "* * * * * "
        cout << "  ";
        for (int col = 0; col < row; col++) {
            cout << "* ";
        }
        cout << endl;
    }
    // > 출력:
    //   *
    //   * *
    //   * * *
    //   * * * *
    //   * * * * *
    cout << endl;

    // ── 별 찍기: 피라미드 ──
    cout << "  ■ 피라미드" << endl;
    int height = 5;
    for (int row = 1; row <= height; row++) {
        // row=1: 공백 4개 + 별 1개
        // row=2: 공백 3개 + 별 3개
        // row=3: 공백 2개 + 별 5개
        // row=4: 공백 1개 + 별 7개
        // row=5: 공백 0개 + 별 9개
        cout << "  ";
        for (int sp = 0; sp < height - row; sp++) {
            cout << " ";
        }
        for (int st = 0; st < 2 * row - 1; st++) {
            cout << "*";
        }
        cout << endl;
    }
    // > 출력:
    //       *
    //      ***
    //     *****
    //    *******
    //   *********
    cout << endl;

    // ── 중첩 break (플래그 방식) ──
    cout << "  ■ 중첩 break (플래그 방식)" << endl;
    bool found = false;
    for (int i = 0; i < 3 && !found; i++) {
        // 진행: i=0,1,2 (단, found가 true면 중단)
        for (int j = 0; j < 3; j++) {
            // 진행: j=0,1,2
            cout << "  (" << i << "," << j << ")";
            if (i == 1 && j == 1) {
                // ▶ i=1, j=1 일 때 도달 → found=true, 안쪽 break
                cout << " ← 찾음!";
                found = true;
                break;
            }
        }
        cout << endl;
    }
    // ▶ 흐름:
    //   i=0: (0,0)(0,1)(0,2) 한 줄
    //   i=1: (1,0)(1,1)←찾음! 한 줄, 안쪽 break, 바깥은 found=true로 다음 반복 안 함
    // > 출력:
    //   (0,0)(0,1)(0,2)
    //   (1,0)(1,1) ← 찾음!
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
    cout << "  ■ FizzBuzz (1~20)" << endl;
    cout << "  ";
    for (int i = 1; i <= 20; i++) {
        // i  | %15  | %3  | %5  | 출력
        // 1  | 1    | 1   | 1   | 1
        // 2  | 2    | 2   | 2   | 2
        // 3  | 3    | 0★ | 3   | Fizz
        // 4  | 4    | 1   | 4   | 4
        // 5  | 5    | 2   | 0★ | Buzz
        // 6  | 6    | 0★ | 1   | Fizz
        // 7  | 7    | 1   | 2   | 7
        // 8  | 8    | 2   | 3   | 8
        // 9  | 9    | 0★ | 4   | Fizz
        // 10 | 10   | 1   | 0★ | Buzz
        // 11 | 11   | 2   | 1   | 11
        // 12 | 12   | 0★ | 2   | Fizz
        // 13 | 13   | 1   | 3   | 13
        // 14 | 14   | 2   | 4   | 14
        // 15 | 0★  | 0   | 0   | FizzBuzz  ← %15 먼저 검사
        // 16 | 1    | 1   | 1   | 16
        // 17 | 2    | 2   | 2   | 17
        // 18 | 3    | 0★ | 3   | Fizz
        // 19 | 4    | 1   | 4   | 19
        // 20 | 5    | 2   | 0★ | Buzz
        if (i % 15 == 0)      cout << "FizzBuzz ";
        else if (i % 3 == 0)  cout << "Fizz ";
        else if (i % 5 == 0)  cout << "Buzz ";
        else                  cout << i << " ";
    }
    cout << endl << endl;
    // > 출력:
    //   1 2 Fizz 4 Buzz Fizz 7 8 Fizz Buzz 11 Fizz 13 14 FizzBuzz 16 17 Fizz 19 Buzz

    // ── 연습 2: 소수 판별 ──
    cout << "  ■ 소수 판별 (2~30)" << endl;
    cout << "  소수: ";
    for (int num = 2; num <= 30; num++) {
        bool is_prime = true;
        // div는 √num 이하만 검사 (div*div <= num)
        // num=2: 검사 안 함 (2*2=4>2) → is_prime 그대로 true
        // num=4: div=2 → 4%2==0 → false
        // num=9: div=2(9%2=1), div=3(3*3=9, 9%3=0) → false
        for (int div = 2; div * div <= num; div++) {
            if (num % div == 0) {
                is_prime = false;
                break;
            }
        }
        if (is_prime) cout << num << " ";
    }
    cout << endl << endl;
    // > 출력:
    //   소수: 2 3 5 7 11 13 17 19 23 29

    // ── 연습 3: 배열에서 최대값 찾기 ──
    cout << "  ■ 최대값 찾기" << endl;
    int data[] = {34, 67, 23, 89, 12, 56, 78, 45};
    int max_val = data[0];      // → 34
    int max_idx = 0;
    // 진행:
    //   i=1: data[1]=67 > 34 → max_val=67, max_idx=1
    //   i=2: data[2]=23 < 67 → 변화 없음
    //   i=3: data[3]=89 > 67 → max_val=89, max_idx=3
    //   i=4: data[4]=12 < 89 → 변화 없음
    //   i=5: data[5]=56 < 89
    //   i=6: data[6]=78 < 89
    //   i=7: data[7]=45 < 89
    // → 최종 max_val=89, max_idx=3
    for (int i = 1; i < 8; i++) {
        if (data[i] > max_val) {
            max_val = data[i];
            max_idx = i;
        }
    }
    cout << "  데이터: ";
    for (int d : data) cout << d << " ";
    cout << endl;
    // > 출력:   데이터: 34 67 23 89 12 56 78 45
    cout << "  최대값: " << max_val << " (인덱스: " << max_idx << ")" << endl;
    // > 출력:   최대값: 89 (인덱스: 3)
    cout << endl;
}
