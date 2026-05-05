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
  [주석 표기] // > 출력  // → 변수값  // ▶ 흐름
=============================================================================
*/
#include <iostream>
#include <string>
using namespace std;

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
int add(int a, int b) {
    return a + b;
    // → add(3,5) 호출 시: a=3, b=5 → return 8
}

void greet(const string& name) {
    cout << "  안녕하세요, " << name << "님!\n";
}

void lesson1_basic() {
    cout << "[레슨 1] 함수 기본\n\n";

    int result = add(3, 5);
    // → result = 8
    cout << "  add(3, 5) = " << result << "\n";
    // > 출력:   add(3, 5) = 8

    greet("홍길동");
    // → 호출 시 name = "홍길동" (참조 전달, 복사 안 함)
    // > 출력:   안녕하세요, 홍길동님!

    cout << endl;
}


// =====================================================================
// 레슨 2 — 매개변수 전달 방식
// =====================================================================
void double_by_value(int x) {
    x = x * 2;
    // → x는 호출자 num의 복사본. x가 변해도 num은 그대로.
}

void double_by_ref(int& x) {
    x = x * 2;
    // → x는 호출자 num의 별명(alias). x를 바꾸면 num도 바뀜.
}

void swap_values(int& a, int& b) {
    int temp = a;       // → temp = a의 현재값 보관
    a = b;              // → a = b의 값
    b = temp;           // → b = 보관해둔 원래 a의 값
}

void lesson2_parameters() {
    cout << "[레슨 2] 매개변수 전달 방식\n\n";

    int num = 10;       // → num = 10

    cout << "  --- 값 전달 ---\n";
    cout << "  전: " << num << "\n";
    // > 출력:   전: 10
    double_by_value(num);
    // → 함수 내부: x = 10 → x = 20. 함수 종료. num은 여전히 10.
    cout << "  후: " << num << "  (안 바뀜 → 복사본만 바뀜)\n\n";
    // > 출력:   후: 10  (안 바뀜 → 복사본만 바뀜)

    cout << "  --- 참조 전달 ---\n";
    cout << "  전: " << num << "\n";
    // > 출력:   전: 10
    double_by_ref(num);
    // → 함수 내부: x는 num의 별명. x = 20 → num = 20.
    cout << "  후: " << num << "  (바뀜! → 원본이 바뀜)\n\n";
    // > 출력:   후: 20  (바뀜! → 원본이 바뀜)

    int a = 100, b = 200;
    cout << "  --- swap ---\n";
    cout << "  전: a=" << a << " b=" << b << "\n";
    // > 출력:   전: a=100 b=200
    swap_values(a, b);
    // → 내부 흐름:
    //   temp = a = 100
    //   a = b = 200
    //   b = temp = 100
    // → 결과: a=200, b=100
    cout << "  후: a=" << a << " b=" << b << "\n";
    // > 출력:   후: a=200 b=100
    cout << endl;
}


// =====================================================================
// 레슨 3 — 함수 오버로딩 & 기본 매개변수
// =====================================================================
int multiply(int a, int b) {
    return a * b;
    // → int 버전. multiply(3,4) → 12
}

double multiply(double a, double b) {
    return a * b;
    // → double 버전. multiply(2.5,3.0) → 7.5
}

void print_info(const string& name, int age) {
    cout << "  이름: " << name;
    if (age > 0) cout << " / 나이: " << age;
    cout << "\n";
}

void lesson3_overloading() {
    cout << "[레슨 3] 오버로딩 & 기본 매개변수\n\n";

    cout << "  multiply(3, 4)     = " << multiply(3, 4) << "\n";
    // → 인자가 (int, int) → int 버전 호출 → 12
    // > 출력:   multiply(3, 4)     = 12

    cout << "  multiply(2.5, 3.0) = " << multiply(2.5, 3.0) << "\n\n";
    // → 인자가 (double, double) → double 버전 호출 → 7.5
    // > 출력:   multiply(2.5, 3.0) = 7.5

    print_info("홍길동", 25);
    // → name="홍길동", age=25 → 두 줄 모두 출력
    // > 출력:   이름: 홍길동 / 나이: 25

    print_info("김철수");
    // → age 생략 → 기본값 0 → if(age>0) false → 이름만 출력
    // > 출력:   이름: 김철수
    cout << endl;
}


// =====================================================================
// 레슨 4 — 변수의 스코프
// =====================================================================
int g_count = 0;        // → 전역. 프로그램 시작 시 0으로 초기화

void lesson4_scope() {
    cout << "[레슨 4] 변수의 스코프 (유효 범위)\n\n";

    int local_var = 10;  // → local_var = 10. 이 함수 안에서만 유효.

    cout << "  전역: g_count = " << g_count << "\n";
    // > 출력:   전역: g_count = 0
    cout << "  지역: local_var = " << local_var << "\n";
    // > 출력:   지역: local_var = 10

    {
        int block_var = 99;
        // → 이 { } 안에서만 유효
        cout << "  블록: block_var = " << block_var << "\n";
        // > 출력:   블록: block_var = 99
    }
    // ← 여기서 block_var는 더 이상 존재하지 않음 (스택에서 사라짐)

    // ── static 지역 변수 ──
    cout << "\n  --- static 변수 ---\n";
    auto call_counter = []() {
        static int count = 0;
        // → static: 첫 호출 때만 0으로 초기화, 이후 호출 간 값 유지
        count++;
        cout << "  호출 횟수: " << count << "\n";
    };
    call_counter();   // → count: 0 → 1 → "호출 횟수: 1"
    call_counter();   // → count: 1 → 2 → "호출 횟수: 2"
    call_counter();   // → count: 2 → 3 → "호출 횟수: 3"
    // > 출력:
    //   호출 횟수: 1
    //   호출 횟수: 2
    //   호출 횟수: 3
    cout << endl;
}


// =====================================================================
// 레슨 5 — 재귀 함수
// =====================================================================
int factorial(int n) {
    if (n <= 1) return 1;          // 기저 조건
    return n * factorial(n - 1);   // 재귀
    // 호출 트리 (n=4 예):
    //   factorial(4) = 4 * factorial(3)
    //   factorial(3) = 3 * factorial(2)
    //   factorial(2) = 2 * factorial(1)
    //   factorial(1) = 1                ← 기저
    //   되돌아가며: 2*1=2, 3*2=6, 4*6=24
}

int fibonacci(int n) {
    if (n <= 0) return 0;
    if (n == 1) return 1;
    return fibonacci(n - 1) + fibonacci(n - 2);
    // 시퀀스: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, ...
    // ※ O(2^n) - 매우 비효율. 학습용. 실무는 메모이제이션/iter.
}

void lesson5_recursion() {
    cout << "[레슨 5] 재귀 함수\n\n";

    cout << "  --- 팩토리얼 ---\n";
    for (int i = 1; i <= 7; i++) {
        // i=1 → 1!=1
        // i=2 → 2!=2
        // i=3 → 3!=6
        // i=4 → 4!=24
        // i=5 → 5!=120
        // i=6 → 6!=720
        // i=7 → 7!=5040
        cout << "  " << i << "! = " << factorial(i) << "\n";
    }
    // > 출력:
    //   1! = 1
    //   2! = 2
    //   3! = 6
    //   4! = 24
    //   5! = 120
    //   6! = 720
    //   7! = 5040

    cout << "\n  --- 피보나치 수열 ---\n  ";
    for (int i = 0; i < 10; i++) {
        // i: 0 1 2 3 4 5 6 7 8 9
        // fib: 0 1 1 2 3 5 8 13 21 34
        cout << fibonacci(i) << " ";
    }
    cout << "\n";
    // > 출력:   0 1 1 2 3 5 8 13 21 34
    cout << endl;
}


// =====================================================================
// 레슨 6 — 람다 (익명 함수)  (C++11)
// =====================================================================
void lesson6_lambda() {
    cout << "[레슨 6] 람다 (익명 함수)\n\n";

    // 기본 람다
    auto say_hi = []() {
        cout << "  안녕! (람다)\n";
    };
    say_hi();
    // > 출력:   안녕! (람다)

    // 매개변수 + 반환
    auto add = [](int a, int b) {
        return a + b;
        // 반환형 자동 추론: int + int → int
    };
    cout << "  add(3,4) = " << add(3, 4) << "\n";
    // → add(3,4) = 7
    // > 출력:   add(3,4) = 7

    // 캡처: 값 복사
    int factor = 3;
    auto times = [factor](int x) {
        // → 람다 생성 시 factor=3을 복사. 이후 외부 factor 변경되어도
        //   람다 내부 사본은 3 그대로.
        return x * factor;
    };
    cout << "  5 * " << factor << " = " << times(5) << "\n";
    // → times(5) = 5 * 3 = 15
    // > 출력:   5 * 3 = 15

    // 참조 캡처: 외부 직접 수정
    int counter = 0;
    auto inc = [&counter]() { counter++; };
    // → counter를 참조로 캡처
    inc();   // counter: 0 → 1
    inc();   // counter: 1 → 2
    inc();   // counter: 2 → 3
    cout << "  counter (3번 증가) = " << counter << "\n";
    // > 출력:   counter (3번 증가) = 3

    // ── 정렬 기준에 람다 사용 ──
    int nums[] = {5, 2, 8, 1, 9};
    int size = 5;

    auto compare = [](int a, int b) { return a > b; };
    // → 내림차순 비교: a가 더 크면 true

    // 버블 정렬 (학습용)
    // 진행 (간략):
    //   초기:    [5, 2, 8, 1, 9]
    //   pass 1:  [5, 8, 2, 9, 1]   (인접 pair 비교 후 큰 게 앞으로)
    //   pass 2:  [8, 5, 9, 2, 1]
    //   pass 3:  [8, 9, 5, 2, 1]
    //   pass 4:  [9, 8, 5, 2, 1]
    for (int i = 0; i < size - 1; i++)
        for (int j = 0; j < size - i - 1; j++)
            if (compare(nums[j + 1], nums[j]))
                swap(nums[j], nums[j + 1]);

    cout << "  내림차순: ";
    for (int n : nums) cout << n << " ";
    cout << "\n";
    // > 출력:   내림차순: 9 8 5 2 1
    cout << endl;
}
