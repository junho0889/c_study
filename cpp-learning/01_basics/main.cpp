/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C++ 학습 01단계: 기초의 기초
  ─ 변수, 자료형, 입출력, 연산자, 형변환 ─

  이 파일 하나로 C++의 가장 기본적인 문법을 전부 배웁니다.
  코드를 직접 타이핑하고, 값을 바꿔보면서 실험하세요.

  ■ 컴파일 방법 (터미널에 입력)
    Windows (MinGW) : g++ -std=c++17 -Wall -o 01_basics.exe main.cpp
    Windows (MSVC)  : cl /EHsc /std:c++17 /W4 main.cpp
    Linux / Mac     : g++ -std=c++17 -Wall -o 01_basics main.cpp

  ■ 실행 방법
    Windows : .\01_basics.exe
    Linux   : ./01_basics

  ■ 주석 표기 규칙 (이번 학습 자료 전체 공통)
    // > 출력: ...     ← 실제 화면에 찍히는 내용
    // → x = 5        ← 해당 시점 변수 값
    // ▶ true 분기     ← 조건문에서 어느 쪽 분기 타는지

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/


// ─────────────────────────────────────────────────────────────────────────
// ■ #include 란?
// ─────────────────────────────────────────────────────────────────────────
//
//   "다른 파일에 미리 만들어둔 기능을 가져다 쓰겠다" 라는 뜻입니다.
//
//   비유: 요리할 때 "냉장고에서 재료를 꺼내는 것"
//         → #include는 "도구 상자에서 도구를 꺼내는 것"
//
//   <iostream> : 화면 출력(cout)과 키보드 입력(cin) 도구
//   <string>   : 문자열(글자 여러 개) 도구
//   <cmath>    : 수학 함수(sqrt, pow, abs 등) 도구
//   <iomanip>  : 출력 형식 조절(소수점 자릿수 등) 도구
//
// ─────────────────────────────────────────────────────────────────────────
#include <iostream>
#include <string>
#include <cmath>
#include <iomanip>


// ─────────────────────────────────────────────────────────────────────────
// ■ using namespace std;
// ─────────────────────────────────────────────────────────────────────────
using namespace std;


// ─── 함수 선언 ───
void lesson1_hello_world();
void lesson2_variables();
void lesson3_constants();
void lesson4_arithmetic_operators();
void lesson5_comparison_and_logic();
void lesson6_type_conversion();
void lesson7_math_functions();
void lesson8_input_output();


// ─────────────────────────────────────────────────────────────────────────
// ■■■ main 함수 — 모든 C++ 프로그램의 시작점 ■■■
// ─────────────────────────────────────────────────────────────────────────
int main() {
    cout << "========================================" << endl;
    // > 출력: ========================================
    cout << "  C++ 01단계 : 기초의 기초" << endl;
    // > 출력:   C++ 01단계 : 기초의 기초
    cout << "========================================" << endl;
    // > 출력: ========================================
    cout << endl;
    // > 출력: (빈 줄)

    // 각 레슨을 순서대로 실행합니다
    lesson1_hello_world();
    lesson2_variables();
    lesson3_constants();
    lesson4_arithmetic_operators();
    lesson5_comparison_and_logic();
    lesson6_type_conversion();
    lesson7_math_functions();
    // lesson8_input_output();   ← 키보드 입력 필요. 주석 해제 시 실행

    cout << endl;
    cout << "========================================" << endl;
    cout << "  01단계 학습 완료!" << endl;
    cout << "========================================" << endl;
    // > 출력 (마지막 4줄):
    //         (빈 줄)
    //         ========================================
    //           01단계 학습 완료!
    //         ========================================

    return 0;   // 운영체제에게 "정상 종료" 알림
    // → 종료 코드 0 = 정상. 셸에서 echo $? (Linux) / echo %errorlevel% (Win)로 확인
}


// =========================================================================
//
//  레슨 1 — Hello, World!
//
// =========================================================================
void lesson1_hello_world() {
    cout << "┌──────────────────────────────────────┐" << endl;
    cout << "│  레슨 1 : Hello, World!              │" << endl;
    cout << "└──────────────────────────────────────┘" << endl;
    cout << endl;
    // > 출력:
    //   ┌──────────────────────────────────────┐
    //   │  레슨 1 : Hello, World!              │
    //   └──────────────────────────────────────┘
    //   (빈 줄)

    // ─── cout / << / endl ───
    //   cout = 화면 출력 도구
    //   <<   = "이것을 출력해라"
    //   endl = 줄바꿈 + 버퍼 flush
    //   "\n" = 줄바꿈만 (더 빠름)

    cout << "  Hello, World!" << endl;
    // > 출력:   Hello, World!

    cout << "  안녕하세요, C++ 세계!" << endl;
    // > 출력:   안녕하세요, C++ 세계!
    // ※ Windows 콘솔에서 한글이 깨지면: chcp 65001 입력 후 재실행

    cout << "  숫자 출력: " << 42 << endl;
    // > 출력:   숫자 출력: 42

    cout << "  계산 결과: " << 3 + 5 << endl;
    // > 출력:   계산 결과: 8        ← 3+5 = 8 이 즉시 계산되어 출력

    // 여러 값을 << 로 연결해서 한번에 출력
    cout << "  이름: " << "홍길동" << ", 나이: " << 25 << "세" << endl;
    // > 출력:   이름: 홍길동, 나이: 25세

    cout << endl;
    // > 출력: (빈 줄)

    //   ★ 초보자 실수 TOP 3
    //   1. 문장 끝 세미콜론(;) 빠뜨림 ← 가장 흔한 실수!
    //   2. 중괄호 { } 짝이 안 맞음
    //   3. 대소문자 구분 안 함  (Main ≠ main, Cout ≠ cout)
}


// =========================================================================
//
//  레슨 2 — 변수와 자료형
//
// =========================================================================
void lesson2_variables() {
    cout << "┌──────────────────────────────────────┐" << endl;
    cout << "│  레슨 2 : 변수와 자료형              │" << endl;
    cout << "└──────────────────────────────────────┘" << endl;
    cout << endl;

    // ─── 변수란? ───
    //   변수 = 값을 담는 상자. 이름표를 붙여서 구분.
    //   선언:  자료형 변수이름 = 초기값;
    //   ★ 변수 이름: 영문/숫자/_ 만, 숫자로 시작 X, 예약어 X, 대소문자 구분

    // ─────────────────────────────────────────────
    // ■ 정수형
    // ─────────────────────────────────────────────
    int         age          = 25;               // → age = 25 (4바이트, ±21억)
    short       temperature  = -10;              // → temperature = -10 (2바이트)
    long long   world_pop    = 8000000000LL;     // → 8,000,000,000 (8바이트, LL 접미사)
    unsigned int item_count  = 150;              // → 150, 음수 불가

    cout << "  ■ 정수형" << endl;
    cout << "  ─────────────────────────────────────" << endl;
    cout << "  int         age         = " << age << endl;
    // > 출력:   int         age         = 25
    cout << "  short       temperature = " << temperature << endl;
    // > 출력:   short       temperature = -10
    cout << "  long long   world_pop   = " << world_pop << endl;
    // > 출력:   long long   world_pop   = 8000000000
    cout << "  unsigned    item_count  = " << item_count << endl;
    // > 출력:   unsigned    item_count  = 150
    cout << endl;

    // ─────────────────────────────────────────────
    // ■ 실수형
    // ─────────────────────────────────────────────
    float  pi_f = 3.14159f;             // → pi_f = 3.14159 (4바이트, 6~7자리 정밀도)
    double pi_d = 3.14159265358979;     // → pi_d = 3.14159265358979 (8바이트)

    cout << "  ■ 실수형" << endl;
    cout << "  ─────────────────────────────────────" << endl;
    cout << "  float  pi = " << pi_f << endl;
    // > 출력:   float  pi = 3.14159
    cout << "  double pi = " << pi_d << endl;
    // > 출력:   double pi = 3.14159         ← 기본은 6자리만 표시. setprecision으로 늘림

    // ★★★ 부동소수점 오차 ★★★
    float test = 0.1f + 0.2f;
    // → test ≈ 0.30000001192092895508  (정확히 0.3이 아님!)
    cout << endl;
    cout << "  ★ 부동소수점 오차 주의!" << endl;
    cout << "  0.1 + 0.2 = " << fixed << setprecision(20) << test << endl;
    // > 출력:   0.1 + 0.2 = 0.30000001192092895508
    //   (float은 7자리 정밀도라 그 이후는 쓰레기 비트가 보임. double로도 0.3 정확 표현 불가)
    cout << "  (정확히 0.3이 아닙니다!)" << endl;
    cout << defaultfloat;  // 출력 형식 원래대로
    cout << endl;

    // ─────────────────────────────────────────────
    // ■ 문자형 / 문자열
    // ─────────────────────────────────────────────
    char   grade   = 'A';           // → grade = 'A' (ASCII 65)
    char   newline = '\n';          // → newline = '\n' (ASCII 10) - 사용 안 함, 변수만
    string name    = "홍길동";       // → name = "홍길동" (UTF-8 9바이트, 표시 3글자)
    string empty   = "";            // → empty = "" (length 0)
    (void)newline;                  // 미사용 경고 방지

    cout << "  ■ 문자/문자열" << endl;
    cout << "  ─────────────────────────────────────" << endl;
    cout << "  char   grade = '" << grade << "'" << endl;
    // > 출력:   char   grade = 'A'
    cout << "  string name  = \"" << name << "\"" << endl;
    // > 출력:   string name  = "홍길동"
    cout << "  string empty = \"" << empty << "\" (빈 문자열, 길이="
         << empty.length() << ")" << endl;
    // > 출력:   string empty = "" (빈 문자열, 길이=0)
    cout << endl;

    // ─────────────────────────────────────────────
    // ■ 논리형 (bool)
    // ─────────────────────────────────────────────
    bool is_student = true;     // → 1
    bool is_sleeping = false;   // → 0

    cout << "  ■ 논리형 (bool)" << endl;
    cout << "  ─────────────────────────────────────" << endl;
    cout << "  is_student  = " << is_student  << "  (1 = true)" << endl;
    // > 출력:   is_student  = 1  (1 = true)
    cout << "  is_sleeping = " << is_sleeping << "  (0 = false)" << endl;
    // > 출력:   is_sleeping = 0  (0 = false)
    cout << "  boolalpha   = " << boolalpha << is_student << ", "
         << is_sleeping << noboolalpha << endl;
    // > 출력:   boolalpha   = true, false   ← boolalpha 매니퓰레이터로 단어 출력
    cout << endl;

    // ─────────────────────────────────────────────
    // ■ auto (C++11) — 타입 자동 추론
    // ─────────────────────────────────────────────
    auto number  = 100;                 // → int (정수 리터럴 → int)
    auto decimal = 3.14;                // → double (소수 리터럴 → double)
    auto letter  = 'X';                 // → char (작은따옴표 → char)
    auto text    = string("자동 추론"); // → string (string()로 명시 변환)

    cout << "  ■ auto (타입 자동 추론)" << endl;
    cout << "  ─────────────────────────────────────" << endl;
    cout << "  auto number  = " << number << endl;
    // > 출력:   auto number  = 100
    cout << "  auto decimal = " << decimal << endl;
    // > 출력:   auto decimal = 3.14
    cout << "  auto letter  = " << letter << endl;
    // > 출력:   auto letter  = X
    cout << "  auto text    = " << text << endl;
    // > 출력:   auto text    = 자동 추론
    cout << endl;

    // ─────────────────────────────────────────────
    // ■ sizeof — 메모리 크기 확인
    // ─────────────────────────────────────────────
    //   ※ 수치는 일반적인 64-bit x86 환경 기준. 플랫폼/컴파일러에 따라 다를 수 있음.

    cout << "  ■ sizeof (바이트 크기)" << endl;
    cout << "  ─────────────────────────────────────" << endl;
    cout << "  bool      = " << sizeof(bool)      << " 바이트" << endl;
    // > 출력:   bool      = 1 바이트         ← 표준은 최소 1, 보통 1
    cout << "  char      = " << sizeof(char)      << " 바이트" << endl;
    // > 출력:   char      = 1 바이트         ← 표준 보장 = 1
    cout << "  short     = " << sizeof(short)     << " 바이트" << endl;
    // > 출력:   short     = 2 바이트
    cout << "  int       = " << sizeof(int)       << " 바이트" << endl;
    // > 출력:   int       = 4 바이트         ← 거의 모든 현대 시스템에서 4
    cout << "  long long = " << sizeof(long long) << " 바이트" << endl;
    // > 출력:   long long = 8 바이트
    cout << "  float     = " << sizeof(float)     << " 바이트" << endl;
    // > 출력:   float     = 4 바이트         ← IEEE 754 single precision
    cout << "  double    = " << sizeof(double)    << " 바이트" << endl;
    // > 출력:   double    = 8 바이트         ← IEEE 754 double precision
    cout << endl;
}


// =========================================================================
//
//  레슨 3 — 상수
//
// =========================================================================
void lesson3_constants() {
    cout << "┌──────────────────────────────────────┐" << endl;
    cout << "│  레슨 3 : 상수                       │" << endl;
    cout << "└──────────────────────────────────────┘" << endl;
    cout << endl;

    // ─── const vs constexpr ───
    //   const     : 런타임 상수. 실행 중 정해질 수도 있음.
    //   constexpr : 컴파일 타임 상수. 선언 시 값 알아야 함. 더 빠르고 엄격.
    //   관례: 상수는 UPPER_SNAKE_CASE

    const double PI          = 3.14159265358979;   // → 런타임에 메모리 차지
    const int    MAX_HP      = 100;                // → 컴파일러 최적화로 immediate 가능
    const string GAME_TITLE  = "나의 첫 게임";

    constexpr int    SCREEN_WIDTH  = 1920;
    constexpr int    SCREEN_HEIGHT = 1080;
    constexpr double GRAVITY       = 9.80665;

    cout << "  ■ const" << endl;
    cout << "  PI         = " << PI << endl;
    // > 출력:   PI         = 3.14159         (기본 정밀도 6자리)
    cout << "  MAX_HP     = " << MAX_HP << endl;
    // > 출력:   MAX_HP     = 100
    cout << "  GAME_TITLE = " << GAME_TITLE << endl;
    // > 출력:   GAME_TITLE = 나의 첫 게임
    cout << endl;

    cout << "  ■ constexpr" << endl;
    cout << "  SCREEN     = " << SCREEN_WIDTH << " x " << SCREEN_HEIGHT << endl;
    // > 출력:   SCREEN     = 1920 x 1080
    cout << "  GRAVITY    = " << GRAVITY << endl;
    // > 출력:   GRAVITY    = 9.80665
    cout << endl;

    // PI = 3.0;   ← 컴파일 에러: assignment of read-only variable 'PI'
}


// =========================================================================
//
//  레슨 4 — 산술 연산자
//
// =========================================================================
void lesson4_arithmetic_operators() {
    cout << "┌──────────────────────────────────────┐" << endl;
    cout << "│  레슨 4 : 산술 연산자                │" << endl;
    cout << "└──────────────────────────────────────┘" << endl;
    cout << endl;

    int a = 17;
    int b = 5;
    // → a = 17, b = 5

    cout << "  ■ 사칙연산  (a = " << a << ", b = " << b << ")" << endl;
    // > 출력:   ■ 사칙연산  (a = 17, b = 5)
    cout << "  ─────────────────────────────────────" << endl;
    cout << "  a + b  = " << (a + b)  << "    덧셈" << endl;
    // > 출력:   a + b  = 22    덧셈           ← 17 + 5 = 22
    cout << "  a - b  = " << (a - b)  << "   뺄셈" << endl;
    // > 출력:   a - b  = 12   뺄셈            ← 17 - 5 = 12
    cout << "  a * b  = " << (a * b)  << "   곱셈" << endl;
    // > 출력:   a * b  = 85   곱셈            ← 17 * 5 = 85
    cout << "  a / b  = " << (a / b)  << "    나눗셈 (몫만!)" << endl;
    // > 출력:   a / b  = 3    나눗셈 (몫만!)  ← 17/5 = 3.4 → 정수 나눗셈으로 3
    cout << "  a % b  = " << (a % b)  << "    나머지 (모듈로)" << endl;
    // > 출력:   a % b  = 2    나머지 (모듈로) ← 17 = 5*3 + 2
    cout << endl;

    // ★★★ 정수 ÷ 정수 = 정수! ★★★
    cout << "  ★ 정수 나눗셈 함정!" << endl;
    cout << "  ─────────────────────────────────────" << endl;
    cout << "  17 / 5     = " << (17 / 5)     << "    ← 틀림! (소수점 버려짐)" << endl;
    // > 출력:   17 / 5     = 3    ← 틀림! (소수점 버려짐)
    cout << "  17.0 / 5   = " << (17.0 / 5)   << "  ← 맞음!" << endl;
    // > 출력:   17.0 / 5   = 3.4  ← 맞음!
    cout << "  17 / 5.0   = " << (17 / 5.0)   << "  ← 맞음!" << endl;
    // > 출력:   17 / 5.0   = 3.4  ← 맞음!
    cout << endl;

    // ─────────────────────────────────────────────
    // ■ 증감 연산자 (++, --)
    // ─────────────────────────────────────────────
    cout << "  ■ 증감 연산자" << endl;
    cout << "  ─────────────────────────────────────" << endl;

    int c = 10;
    cout << "  c = " << c << endl;
    // > 출력:   c = 10                            → c = 10

    cout << "  ++c (전위) = " << (++c) << "  ← 먼저 증가, 그 값 사용" << endl;
    // → 평가 순서: ++c → c는 11로 증가, 표현식 값도 11
    // > 출력:   ++c (전위) = 11  ← 먼저 증가, 그 값 사용
    // → c = 11

    cout << "  c++ (후위) = " << (c++) << "  ← 현재 값 사용, 그 다음 증가" << endl;
    // → 평가 순서: 표현식 값은 현재 c=11, 그 후 c는 12로 증가
    // > 출력:   c++ (후위) = 11  ← 현재 값 사용, 그 다음 증가
    // → c = 12

    cout << "  현재 c     = " << c << endl;
    // > 출력:   현재 c     = 12
    cout << endl;

    // ─────────────────────────────────────────────
    // ■ 복합 대입 연산자 (+=, -=, *=, /=, %=)
    // ─────────────────────────────────────────────
    cout << "  ■ 복합 대입 연산자" << endl;
    cout << "  ─────────────────────────────────────" << endl;

    int n = 100;
    cout << "  n = " << n << endl;
    // > 출력:   n = 100                            → n = 100

    n += 50;
    // → n = 100 + 50 = 150
    cout << "  n += 50  → n = " << n << "  (n = n + 50)" << endl;
    // > 출력:   n += 50  → n = 150  (n = n + 50)

    n -= 30;
    // → n = 150 - 30 = 120
    cout << "  n -= 30  → n = " << n << "  (n = n - 30)" << endl;
    // > 출력:   n -= 30  → n = 120  (n = n - 30)

    n *= 2;
    // → n = 120 * 2 = 240
    cout << "  n *= 2   → n = " << n << "  (n = n * 2)" << endl;
    // > 출력:   n *= 2   → n = 240  (n = n * 2)

    n /= 4;
    // → n = 240 / 4 = 60
    cout << "  n /= 4   → n = " << n << "   (n = n / 4)" << endl;
    // > 출력:   n /= 4   → n = 60   (n = n / 4)

    n %= 7;
    // → n = 60 % 7 = 4   (60 = 7*8 + 4)
    cout << "  n %= 7   → n = " << n << "    (n = n % 7)" << endl;
    // > 출력:   n %= 7   → n = 4    (n = n % 7)
    cout << endl;
}


// =========================================================================
//
//  레슨 5 — 비교 연산자와 논리 연산자
//
// =========================================================================
void lesson5_comparison_and_logic() {
    cout << "┌──────────────────────────────────────┐" << endl;
    cout << "│  레슨 5 : 비교 & 논리 연산자         │" << endl;
    cout << "└──────────────────────────────────────┘" << endl;
    cout << endl;

    int x = 10, y = 20;
    // → x = 10, y = 20

    cout << "  ■ 비교 연산자  (x = " << x << ", y = " << y << ")" << endl;
    // > 출력:   ■ 비교 연산자  (x = 10, y = 20)
    cout << "  ─────────────────────────────────────" << endl;
    cout << "  x == y  → " << (x == y)  << "  같은가?" << endl;
    // > 출력:   x == y  → 0  같은가?         ← 10 != 20 → false → 0
    cout << "  x != y  → " << (x != y)  << "  다른가?" << endl;
    // > 출력:   x != y  → 1  다른가?         ← 10 != 20 → true → 1
    cout << "  x < y   → " << (x < y)   << "  작은가?" << endl;
    // > 출력:   x < y   → 1  작은가?         ← 10 < 20 → true
    cout << "  x > y   → " << (x > y)   << "  큰가?" << endl;
    // > 출력:   x > y   → 0  큰가?           ← 10 > 20 → false
    cout << "  x <= y  → " << (x <= y)  << "  작거나 같은가?" << endl;
    // > 출력:   x <= y  → 1  작거나 같은가?  ← 10 <= 20 → true
    cout << "  x >= y  → " << (x >= y)  << "  크거나 같은가?" << endl;
    // > 출력:   x >= y  → 0  크거나 같은가?  ← 10 >= 20 → false
    cout << endl;

    cout << "  ★ 주의: = (대입) ≠ == (비교)" << endl;
    cout << "  if (x = 5)  → 대입! 항상 true! (버그)" << endl;
    cout << "  if (x == 5) → 비교! 올바름!" << endl;
    cout << endl;

    // ─────────────────────────────────────────────
    // ■ 논리 연산자
    // ─────────────────────────────────────────────
    bool a = true, b = false;
    // → a = true(1), b = false(0)

    cout << "  ■ 논리 연산자  (a = true, b = false)" << endl;
    cout << "  ─────────────────────────────────────" << endl;
    cout << "  a && b (AND) = " << (a && b) << "  둘 다 참?" << endl;
    // > 출력:   a && b (AND) = 0  둘 다 참?       ← true && false = false
    cout << "  a || b (OR)  = " << (a || b) << "  하나라도 참?" << endl;
    // > 출력:   a || b (OR)  = 1  하나라도 참?    ← true || false = true
    cout << "  !a     (NOT) = " << (!a)     << "  반전" << endl;
    // > 출력:   !a     (NOT) = 0  반전            ← !true = false
    cout << endl;

    // 실용 예제
    int age = 20;
    bool has_id = true;
    // → age = 20, has_id = true

    cout << "  ■ 실용 예제" << endl;
    cout << "  ─────────────────────────────────────" << endl;
    cout << "  나이: " << age << ", 신분증: " << (has_id ? "있음" : "없음") << endl;
    // → 삼항 연산자: has_id가 true → "있음"
    // > 출력:   나이: 20, 신분증: 있음

    bool can_enter = (age >= 18) && has_id;
    // → (20 >= 18) && true = true && true = true
    // → can_enter = true
    cout << "  입장 가능? (18세 이상 AND 신분증) → "
         << (can_enter ? "가능" : "불가") << endl;
    // > 출력:   입장 가능? (18세 이상 AND 신분증) → 가능

    bool is_discount = (age < 13) || (age >= 65);
    // → (20 < 13) || (20 >= 65) = false || false = false
    // → is_discount = false
    cout << "  할인 대상? (13세 미만 OR 65세 이상) → "
         << (is_discount ? "대상" : "비대상") << endl;
    // > 출력:   할인 대상? (13세 미만 OR 65세 이상) → 비대상
    cout << endl;
}


// =========================================================================
//
//  레슨 6 — 형 변환 (Type Conversion / Casting)
//
// =========================================================================
void lesson6_type_conversion() {
    cout << "┌──────────────────────────────────────┐" << endl;
    cout << "│  레슨 6 : 형 변환 (캐스팅)           │" << endl;
    cout << "└──────────────────────────────────────┘" << endl;
    cout << endl;

    // ─────────────────────────────────────────────
    // ■ 암시적 변환 (자동)
    // ─────────────────────────────────────────────
    cout << "  ■ 암시적 변환 (자동)" << endl;
    cout << "  ─────────────────────────────────────" << endl;

    int    i = 42;
    double d = i;       // → d = 42.0 (int → double, 안전)
    cout << "  int 42 → double = " << d << "  (안전)" << endl;
    // > 출력:   int 42 → double = 42  (안전)
    //   ※ 42는 42.0이지만 기본 출력은 정수처럼 보임

    double pi = 3.99;
    int    t  = pi;     // → t = 3 (소수점 버림, double → int)
    cout << "  double 3.99 → int = " << t << "    (소수점 잘림!)" << endl;
    // > 출력:   double 3.99 → int = 3    (소수점 잘림!)

    char ch = 'A';      // → ch = 'A' (ASCII 65)
    int  ascii = ch;    // → ascii = 65
    cout << "  char 'A' → int = " << ascii << "  (ASCII 코드)" << endl;
    // > 출력:   char 'A' → int = 65  (ASCII 코드)

    int  num = 65;
    char letter = num;  // → letter = 'A' (ASCII 65 → 문자)
    cout << "  int 65 → char = '" << letter << "' (문자로 변환)" << endl;
    // > 출력:   int 65 → char = 'A' (문자로 변환)
    cout << endl;

    // ─────────────────────────────────────────────
    // ■ 명시적 변환 (캐스팅)
    // ─────────────────────────────────────────────
    cout << "  ■ 명시적 변환 (캐스팅)" << endl;
    cout << "  ─────────────────────────────────────" << endl;

    double value = 9.87;

    int c_style   = (int)value;                  // → 9 (소수점 버림)
    int cpp_style = static_cast<int>(value);     // → 9 (같은 결과, 권장 문법)

    cout << "  C 스타일:   (int)9.87         = " << c_style << endl;
    // > 출력:   C 스타일:   (int)9.87         = 9
    cout << "  C++ 스타일: static_cast<int>  = " << cpp_style << endl;
    // > 출력:   C++ 스타일: static_cast<int>  = 9
    cout << endl;

    // ─────────────────────────────────────────────
    // ■ 실전 활용: 정수 나눗셈에서 소수점 얻기
    // ─────────────────────────────────────────────
    cout << "  ■ 실전 활용" << endl;
    cout << "  ─────────────────────────────────────" << endl;

    int total = 17;
    int count = 5;

    double wrong = total / count;
    // → 17 / 5 = 3 (정수 나눗셈) → 3.0으로 double에 저장
    cout << "  틀림: 17 / 5              = " << wrong << endl;
    // > 출력:   틀림: 17 / 5              = 3

    double correct = static_cast<double>(total) / count;
    // → 17.0 / 5 = 3.4 (실수 나눗셈)
    cout << "  맞음: static_cast(17) / 5 = " << correct << endl;
    // > 출력:   맞음: static_cast(17) / 5 = 3.4
    cout << endl;
}


// =========================================================================
//
//  레슨 7 — 수학 함수
//
// =========================================================================
void lesson7_math_functions() {
    cout << "┌──────────────────────────────────────┐" << endl;
    cout << "│  레슨 7 : 수학 함수 (<cmath>)        │" << endl;
    cout << "└──────────────────────────────────────┘" << endl;
    cout << endl;

    cout << "  ■ 주요 수학 함수" << endl;
    cout << "  ─────────────────────────────────────" << endl;
    cout << "  sqrt(16)    = " << sqrt(16)     << "   제곱근" << endl;
    // > 출력:   sqrt(16)    = 4   제곱근            ← √16 = 4
    cout << "  pow(2, 10)  = " << pow(2, 10)   << "  2의 10승" << endl;
    // > 출력:   pow(2, 10)  = 1024  2의 10승        ← 2^10 = 1024
    cout << "  abs(-7)     = " << abs(-7)      << "    절대값" << endl;
    // > 출력:   abs(-7)     = 7    절대값
    cout << "  ceil(3.2)   = " << ceil(3.2)    << "    올림" << endl;
    // > 출력:   ceil(3.2)   = 4    올림             ← 3.2 → 4
    cout << "  floor(3.8)  = " << floor(3.8)   << "    내림" << endl;
    // > 출력:   floor(3.8)  = 3    내림             ← 3.8 → 3
    cout << "  round(3.5)  = " << round(3.5)   << "    반올림" << endl;
    // > 출력:   round(3.5)  = 4    반올림           ← 3.5 → 4 (사사오입)
    cout << "  fmod(7, 3)  = " << fmod(7, 3)   << "    실수 나머지" << endl;
    // > 출력:   fmod(7, 3)  = 1    실수 나머지      ← 7 = 3*2 + 1
    cout << endl;

    // 실용 예제: 원의 넓이
    const double PI = 3.14159265358979;
    double radius = 5.0;
    double area = PI * pow(radius, 2);
    // → area = 3.14159265358979 * 25 = 78.5398163397448

    cout << "  ■ 실용 예제: 원의 넓이" << endl;
    cout << "  ─────────────────────────────────────" << endl;
    cout << "  반지름 = " << radius << endl;
    // > 출력:   반지름 = 5
    cout << "  넓이   = PI * r^2 = " << area << endl;
    // > 출력:   넓이   = PI * r^2 = 78.5398

    // 실용 예제: 두 점 사이의 거리
    double x1 = 1, y1 = 2;
    double x2 = 4, y2 = 6;
    // → 차: dx=3, dy=4 → 거리 = √(9+16) = √25 = 5
    double distance = sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2));
    // → distance = 5.0

    cout << endl;
    cout << "  ■ 실용 예제: 두 점 사이 거리" << endl;
    cout << "  ─────────────────────────────────────" << endl;
    cout << "  점1 = (" << x1 << ", " << y1 << ")" << endl;
    // > 출력:   점1 = (1, 2)
    cout << "  점2 = (" << x2 << ", " << y2 << ")" << endl;
    // > 출력:   점2 = (4, 6)
    cout << "  거리 = " << distance << endl;
    // > 출력:   거리 = 5         ← 3-4-5 직각삼각형
    cout << endl;
}


// =========================================================================
//
//  레슨 8 — 콘솔 입출력 (키보드 입력)
//   ※ 이 레슨은 사용자 입력을 받음. main에서 주석 해제 시 실행.
// =========================================================================
void lesson8_input_output() {
    cout << "┌──────────────────────────────────────┐" << endl;
    cout << "│  레슨 8 : 키보드 입력 (cin)          │" << endl;
    cout << "└──────────────────────────────────────┘" << endl;
    cout << endl;

    cout << "  ■ 이름을 입력하세요: ";
    string name;
    getline(cin, name);
    // → 사용자 입력 예: "홍길동" → name = "홍길동" (공백 포함, 한 줄)

    cout << "  ■ 나이를 입력하세요: ";
    int age;
    cin >> age;
    // → 사용자 입력 예: "30" → age = 30
    // → 입력 버퍼에 '\n'이 남음

    cin.ignore();
    // → 버퍼에 남은 '\n' 폐기. 안 하면 다음 getline이 빈 줄 받음.

    cout << "  ■ 취미를 입력하세요: ";
    string hobby;
    getline(cin, hobby);
    // → 사용자 입력 예: "독서" → hobby = "독서"

    cout << endl;
    cout << "  ─────────────────────────────────────" << endl;
    cout << "  이름: " << name << endl;
    // > 출력 예:   이름: 홍길동
    cout << "  나이: " << age << "세" << endl;
    // > 출력 예:   나이: 30세
    cout << "  취미: " << hobby << endl;
    // > 출력 예:   취미: 독서
    cout << endl;

    cout << "  ■ 두 정수를 공백으로 구분하여 입력 (예: 10 20): ";
    int x, y;
    cin >> x >> y;
    // → 사용자 입력 예: "10 20" → x = 10, y = 20

    cout << "  입력한 값: " << x << " 와 " << y << endl;
    // > 출력 예:   입력한 값: 10 와 20
    cout << "  합계: " << (x + y) << endl;
    // > 출력 예:   합계: 30
    cout << "  차이: " << (x - y) << endl;
    // > 출력 예:   차이: -10        ← 10 - 20 = -10
    cout << endl;

    // ─── 입력 에러 처리 (참고) ───
    //   숫자에 글자 입력 → cin이 fail 상태 → 이후 입력 무시.
    //   해결:
    //     if (cin.fail()) { cin.clear(); cin.ignore(10000, '\n'); }
}
