/*
=============================================================================
  C++ 학습 03단계: 함수
=============================================================================
  [학습 목표]
  1. 함수를 선언·정의·호출할 수 있다
  2. 값 전달 / 참조 전달의 차이를 안다
  3. 오버로딩과 기본 매개변수를 쓸 수 있다
  4. 변수의 스코프(유효범위)를 이해한다
  5. 재귀 함수를 작성할 수 있다
  6. 람다(익명 함수)를 이해한다

  [컴파일] g++ -std=c++17 -o 03_func main.cpp
=============================================================================
*/
#include <iostream>
#include <string>
using namespace std;

// ── 함수 선언 (프로토타입) ──
// main() 아래에 본문을 쓸 때, 여기에 미리 알려줘야 한다
int  add(int a, int b);
void greet(const string& name);
void swap_values(int& a, int& b);
int  multiply(int a, int b);
double multiply(double a, double b);
void print_info(const string& name, int age = 0);

void lesson1_basic();
void lesson2_parameters();
void lesson3_overloading();
void lesson4_scope();
void lesson5_recursion();
void lesson6_lambda();

int main() {
    cout << "========================================\n";
    cout << "  C++ 03단계 : 함수\n";
    cout << "========================================\n\n";

    lesson1_basic();
    lesson2_parameters();
    lesson3_overloading();
    lesson4_scope();
    lesson5_recursion();
    lesson6_lambda();

    cout << "\n03단계 학습 완료!\n";
    return 0;
}


// =====================================================================
// 레슨 1 — 함수 기본
// =====================================================================
/*
★ 함수 = 코드를 묶어서 이름을 붙인 것 (재사용 가능)

    반환형  함수이름(매개변수) {
        처리
        return 결과;   ← void면 생략 가능
    }

    예시:
    int add(int a, int b) {
        return a + b;
    }

★ 왜 함수를 쓰나?
  1. 같은 코드를 반복 안 써도 됨
  2. 코드를 논리 단위로 나눠서 읽기 쉬움
  3. 버그 수정 시 한 곳만 고치면 됨
*/

int add(int a, int b) {
    return a + b;
}

void greet(const string& name) {   // void = 반환값 없음
    cout << "  안녕하세요, " << name << "님!\n";
}

void lesson1_basic() {
    cout << "[레슨 1] 함수 기본\n\n";

    int result = add(3, 5);
    cout << "  add(3, 5) = " << result << "\n";
    greet("홍길동");
    cout << endl;
}


// =====================================================================
// 레슨 2 — 매개변수 전달 방식
// =====================================================================
/*
★ 3가지 전달 방식 — 가장 중요한 개념 중 하나!

┌──────────────────┬──────────────────────┬──────────────┐
│ 방법             │ 선언                  │ 원본 변경?   │
├──────────────────┼──────────────────────┼──────────────┤
│ 값 전달          │ void f(int x)        │ X (복사)     │
│ 참조 전달        │ void f(int& x)       │ O (원본)     │
│ const 참조 전달  │ void f(const int& x) │ X (읽기전용) │
└──────────────────┴──────────────────────┴──────────────┘

언제 뭘 쓸까?
- 작은 값(int, double) 읽기 → 값 전달
- 큰 객체(string, vector) 읽기 → const 참조
- 원본을 바꿔야 할 때 → 참조
*/

void double_by_value(int x) {
    x = x * 2;   // 복사본을 바꿈 → 원본 무관
}

void double_by_ref(int& x) {
    x = x * 2;   // 원본을 직접 바꿈!
}

void swap_values(int& a, int& b) {
    int temp = a;
    a = b;
    b = temp;
}

void lesson2_parameters() {
    cout << "[레슨 2] 매개변수 전달 방식\n\n";

    int num = 10;

    cout << "  --- 값 전달 ---\n";
    cout << "  전: " << num << "\n";
    double_by_value(num);
    cout << "  후: " << num << "  (안 바뀜 → 복사본만 바뀜)\n\n";

    cout << "  --- 참조 전달 ---\n";
    cout << "  전: " << num << "\n";
    double_by_ref(num);
    cout << "  후: " << num << "  (바뀜! → 원본이 바뀜)\n\n";

    int a = 100, b = 200;
    cout << "  --- swap ---\n";
    cout << "  전: a=" << a << " b=" << b << "\n";
    swap_values(a, b);
    cout << "  후: a=" << a << " b=" << b << "\n";
    cout << endl;
}


// =====================================================================
// 레슨 3 — 함수 오버로딩 & 기본 매개변수
// =====================================================================
/*
★ 오버로딩 = 같은 이름, 다른 매개변수 → 여러 함수 정의 가능
  - 컴파일러가 매개변수 타입/개수 보고 어떤 것을 호출할지 결정
  - 반환형만 다른 건 안 됨!

★ 기본 매개변수 = 호출 시 생략하면 미리 정한 값 사용
  - 오른쪽부터 지정해야 함
    void f(int a, int b = 10);        // OK
    void f(int a = 10, int b);        // 에러!
*/

int multiply(int a, int b) {
    return a * b;
}

double multiply(double a, double b) {
    return a * b;
}

void print_info(const string& name, int age) {
    cout << "  이름: " << name;
    if (age > 0) cout << " / 나이: " << age;
    cout << "\n";
}

void lesson3_overloading() {
    cout << "[레슨 3] 오버로딩 & 기본 매개변수\n\n";

    // 같은 이름이지만 타입이 다르면 알아서 구분
    cout << "  multiply(3, 4)     = " << multiply(3, 4) << "\n";
    cout << "  multiply(2.5, 3.0) = " << multiply(2.5, 3.0) << "\n\n";

    // 기본 매개변수
    print_info("홍길동", 25);
    print_info("김철수");         // age 생략 → 기본값 0
    cout << endl;
}


// =====================================================================
// 레슨 4 — 변수의 스코프
// =====================================================================
int g_count = 0;  // 전역 변수 (프로그램 전체에서 접근 가능)

void lesson4_scope() {
    cout << "[레슨 4] 변수의 스코프 (유효 범위)\n\n";

    /*
    ★ 스코프 = "이 변수를 어디서 쓸 수 있는가?"

    ┌─ 전역 (global) ─────────────────┐
    │  int g = 100;   ← 어디서나      │
    │                                  │
    │  ┌─ 함수 (local) ──────────┐    │
    │  │  int a = 10;  ← 함수 안 │    │
    │  │                          │    │
    │  │  ┌─ 블록 ──────────┐    │    │
    │  │  │  int b = 5;      │    │    │
    │  │  └──────────────────┘    │    │
    │  │  // b 접근 불가          │    │
    │  └──────────────────────────┘    │
    └──────────────────────────────────┘

    ★ 좋은 습관
    1. 전역 변수를 최소화하라 (디버깅이 어려워짐)
    2. 변수는 쓰기 직전에 선언하라
    3. 범위를 가능한 좁게 유지하라
    */

    int local_var = 10;          // 이 함수 안에서만 유효
    cout << "  전역: g_count = " << g_count << "\n";
    cout << "  지역: local_var = " << local_var << "\n";

    {
        int block_var = 99;      // 이 { } 안에서만 유효
        cout << "  블록: block_var = " << block_var << "\n";
    }
    // block_var 은 여기서 접근 불가 (컴파일 에러)

    // ── static 지역 변수 ──
    //  함수가 끝나도 값이 유지됨 (호출 횟수 세기 등에 사용)
    cout << "\n  --- static 변수 ---\n";
    auto call_counter = []() {
        static int count = 0;    // 첫 호출 때만 초기화, 이후 유지
        count++;
        cout << "  호출 횟수: " << count << "\n";
    };
    call_counter();   // 1
    call_counter();   // 2
    call_counter();   // 3
    cout << endl;
}


// =====================================================================
// 레슨 5 — 재귀 함수
// =====================================================================
/*
★ 재귀 = 함수가 자기 자신을 호출하는 것

    반드시 '기저 조건'(탈출 조건)이 있어야 멈춘다!
    없으면 → 무한 재귀 → 스택 오버플로우 (프로그램 크래시)

    factorial(4) 의 작동:
    4 * factorial(3)
    4 * 3 * factorial(2)
    4 * 3 * 2 * factorial(1)
    4 * 3 * 2 * 1            ← 기저 조건 도달!
    = 24
*/

int factorial(int n) {
    if (n <= 1) return 1;          // 기저 조건!
    return n * factorial(n - 1);   // 재귀 호출
}

int fibonacci(int n) {
    if (n <= 0) return 0;
    if (n == 1) return 1;
    return fibonacci(n - 1) + fibonacci(n - 2);
    // 주의: 이 방식은 매우 비효율적 (학습용)
    // 실무에서는 반복문이나 메모이제이션 사용
}

void lesson5_recursion() {
    cout << "[레슨 5] 재귀 함수\n\n";

    cout << "  --- 팩토리얼 ---\n";
    for (int i = 1; i <= 7; i++) {
        cout << "  " << i << "! = " << factorial(i) << "\n";
    }

    cout << "\n  --- 피보나치 수열 ---\n  ";
    for (int i = 0; i < 10; i++) {
        cout << fibonacci(i) << " ";
    }
    cout << "\n";
    cout << endl;
}


// =====================================================================
// 레슨 6 — 람다 (익명 함수)  (C++11)
// =====================================================================
void lesson6_lambda() {
    cout << "[레슨 6] 람다 (익명 함수)\n\n";

    /*
    ★ 람다 = 이름 없는 함수, 변수에 담아 쓸 수 있음
      Python: lambda x: x * 2
      JS:     (x) => x * 2
      C++:    [](int x) { return x * 2; }

    ★ 구조:
      [캡처](매개변수) -> 반환형 { 본문 }

    ★ 캡처 = 바깥 변수를 람다 안에서 쓰는 방법
      []    아무것도 안 가져옴
      [=]   바깥 변수를 값으로 복사
      [&]   바깥 변수를 참조로 가져옴
      [x]   x만 값으로 복사
      [&x]  x만 참조로 가져옴
    */

    // 기본 람다
    auto say_hi = []() {
        cout << "  안녕! (람다)\n";
    };
    say_hi();

    // 매개변수 + 반환
    auto add = [](int a, int b) {
        return a + b;
    };
    cout << "  add(3,4) = " << add(3, 4) << "\n";

    // 캡처: 바깥 변수 사용
    int factor = 3;
    auto times = [factor](int x) {     // factor를 값으로 복사
        return x * factor;
    };
    cout << "  5 * " << factor << " = " << times(5) << "\n";

    // 참조 캡처: 바깥 변수를 직접 수정
    int counter = 0;
    auto inc = [&counter]() { counter++; };
    inc(); inc(); inc();
    cout << "  counter (3번 증가) = " << counter << "\n";

    // ── 실용: 정렬 기준에 람다 사용 ──
    int nums[] = {5, 2, 8, 1, 9};
    int size = 5;

    auto compare = [](int a, int b) { return a > b; };  // 내림차순

    // 버블 정렬 (학습용, 실무에서는 std::sort 사용)
    for (int i = 0; i < size - 1; i++)
        for (int j = 0; j < size - i - 1; j++)
            if (compare(nums[j + 1], nums[j]))
                swap(nums[j], nums[j + 1]);

    cout << "  내림차순: ";
    for (int n : nums) cout << n << " ";
    cout << "\n";
    cout << endl;
}
