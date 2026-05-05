/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C++ 학습 23단계: 함수형 프로그래밍 (Functional Programming)
  ─ Functor, std::function, std::bind, 고차 함수, 클로저, 파이프라인 ─

  함수형 프로그래밍(FP)은 함수를 "일급 시민"(first-class citizen)으로 다루는
  프로그래밍 패러다임입니다. C++은 순수 함수형 언어는 아니지만, C++11 이후
  람다, std::function, std::bind 등을 통해 강력한 FP 기능을 제공합니다.

  ╔═══════════════════════════════════════════════════════════════════╗
  ║  함수형 프로그래밍의 핵심 원칙                                     ║
  ╠═══════════════════════════════════════════════════════════════════╣
  ║  1. 순수 함수 (Pure Function)  - 같은 입력 → 항상 같은 출력      ║
  ║  2. 불변성 (Immutability)      - 데이터를 변경하지 않음            ║
  ║  3. 일급 함수 (First-class)    - 함수를 변수처럼 전달/반환        ║
  ║  4. 고차 함수 (Higher-order)   - 함수를 인자로 받거나 반환        ║
  ║  5. 합성 (Composition)         - 작은 함수를 조합해 큰 함수 생성  ║
  ╚═══════════════════════════════════════════════════════════════════╝

  ■ 컴파일:
    g++ -std=c++17 -Wall -o 23_functional main.cpp
  ■ Windows (MSVC):
    cl /EHsc /std:c++17 main.cpp

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/
#include <iostream>
#include <string>
#include <vector>
#include <functional>   // std::function, std::bind
#include <algorithm>    // std::transform, std::for_each, std::sort
#include <numeric>      // std::accumulate
#include <map>
#include <memory>
#include <cassert>
#include <sstream>
#include <type_traits>

using namespace std;

// ─── 함수 전방 선언 ─────────────────────────────────────────────────────
void lesson1_functor();
void lesson2_std_function();
void lesson3_bind_partial();
void lesson4_higher_order();
void lesson5_closure_advanced();
void lesson6_pipeline();
void lesson7_practical();

/*
=============================================================================
  레슨별 출력 흐름 가이드 (대략)
=============================================================================
  lesson1 (Functor):
    Multiplier(3) → operator()(5) = 15
    상태(state)를 가진 함수 객체. 호출 간 상태 유지.

  lesson2 (std::function):
    함수 포인터, 람다, functor를 통합 추상화
    function<int(int)> f = [](int x){ return x*2; };  → f(5) = 10

  lesson3 (bind / partial):
    auto add5 = bind(add, 5, _1);  → add5(10) = 15
    부분 적용으로 함수 변형

  lesson4 (Higher-Order):
    map([](int x){return x*x;}, [1,2,3]) → [1,4,9]
    filter(is_even, [1,2,3,4]) → [2,4]
    reduce(+, 0, [1,2,3,4]) → 10

  lesson5 (클로저 심화):
    auto counter = make_counter();  → counter()=1, counter()=2, counter()=3
    내부 변수 캡처로 상태 유지

  lesson6 (Pipeline / Compose):
    compose(double_it, add_one)(5) → double_it(add_one(5)) = double_it(6) = 12
    파이프라인 스타일: x | f1 | f2 | f3

  lesson7 (실전):
    함수형 스타일로 데이터 변환 체인
    [1,2,3,4,5] | filter(>2) | map(*2) | sum → 24
=============================================================================
*/

int main() {
    cout << "═══════════════════════════════════════════════\n";
    cout << "  C++ 23단계 : 함수형 프로그래밍\n";
    cout << "═══════════════════════════════════════════════\n\n";

    lesson1_functor();
    lesson2_std_function();
    lesson3_bind_partial();
    lesson4_higher_order();
    lesson5_closure_advanced();
    lesson6_pipeline();
    lesson7_practical();

    cout << "\n═══════════════════════════════════════════════\n";
    cout << "  23단계 학습 완료! 함수형 프로그래밍 마스터!\n";
    cout << "═══════════════════════════════════════════════\n";
    return 0;
}


// =========================================================================
//  레슨 1 — 함수 객체 (Functor)
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────┐
    │  함수 객체(Functor)란?                                          │
    │                                                                 │
    │  operator()를 오버로딩한 클래스의 인스턴스.                      │
    │  일반 함수처럼 호출할 수 있지만, "상태"를 가질 수 있다!          │
    │                                                                 │
    │  일반 함수:    int add(int a, int b) { return a+b; }            │
    │  함수 객체:    struct Add {                                      │
    │                  int operator()(int a, int b) { return a+b; }   │
    │                };                                                │
    │                                                                 │
    │    ┌──────────┐     호출 문법 동일      ┌──────────┐            │
    │    │ 일반함수 │  ─────────────────────▶ │ Functor  │            │
    │    │ f(x, y)  │                         │ f(x, y)  │            │
    │    └──────────┘                         │ + 상태!  │            │
    │                                         └──────────┘            │
    └─────────────────────────────────────────────────────────────────┘
*/
void lesson1_functor() {
    cout << "┌──────────────────────────────────────────┐\n";
    cout << "│  레슨 1 : 함수 객체 (Functor)            │\n";
    cout << "└──────────────────────────────────────────┘\n\n";

    // ─── 1-1: 기본 함수 객체 ─────────────────────────────────────────
    // operator()를 오버로딩하면, 객체를 함수처럼 호출할 수 있다.

    struct Adder {
        int value;  // 내부 상태를 가짐!

        // 생성자: 더할 값을 설정
        Adder(int v) : value(v) {}

        // operator() 오버로딩 → 함수처럼 호출 가능
        int operator()(int x) const {
            return x + value;
        }
    };

    Adder add5(5);      // 5를 더하는 함수 객체 생성
    Adder add10(10);    // 10을 더하는 함수 객체 생성

    cout << "  [기본 Functor]\n";
    cout << "  add5(3)  = " << add5(3)  << "  (3 + 5 = 8)\n";
    cout << "  add10(3) = " << add10(3) << "  (3 + 10 = 13)\n\n";

    // ─── 1-2: 상태를 가진 함수 객체 ─────────────────────────────────
    // 호출될 때마다 내부 카운터를 증가시키는 Functor
    //
    //   호출 1회 → count=1 → 반환값 영향
    //   호출 2회 → count=2 → 반환값 영향
    //   호출 3회 → count=3 → ...

    struct Counter {
        int count = 0;

        int operator()() {
            return ++count;  // 호출 시마다 카운터 증가
        }
    };

    Counter counter;
    cout << "  [상태를 가진 Functor - Counter]\n";
    cout << "  counter() = " << counter() << "\n";   // 1
    cout << "  counter() = " << counter() << "\n";   // 2
    cout << "  counter() = " << counter() << "\n";   // 3
    cout << "  → 일반 함수로는 불가능한 '상태 보존'이 가능!\n\n";

    // ─── 1-3: STL 알고리즘과 함수 객체 ──────────────────────────────
    // STL의 알고리즘은 함수 객체를 인자로 받을 수 있다.

    struct Multiplier {
        int factor;
        Multiplier(int f) : factor(f) {}
        int operator()(int x) const { return x * factor; }
    };

    vector<int> nums = {1, 2, 3, 4, 5};
    vector<int> result(nums.size());

    // std::transform에 함수 객체 전달
    transform(nums.begin(), nums.end(), result.begin(), Multiplier(3));

    cout << "  [STL + Functor]\n";
    cout << "  원본:   ";
    for (int n : nums) cout << n << " ";
    cout << "\n  x3 변환: ";
    for (int n : result) cout << n << " ";
    cout << "\n\n";

    // ─── 1-4: 비교 함수 객체 ────────────────────────────────────────
    // std::sort에 커스텀 비교 함수 객체 전달

    struct DescendingOrder {
        bool operator()(int a, int b) const {
            return a > b;  // 내림차순
        }
    };

    vector<int> data = {5, 2, 8, 1, 9, 3};
    sort(data.begin(), data.end(), DescendingOrder());

    cout << "  [비교 Functor로 정렬]\n";
    cout << "  내림차순: ";
    for (int n : data) cout << n << " ";
    cout << "\n\n";

    // ─── 1-5: 제네릭 함수 객체 (템플릿) ─────────────────────────────
    // 템플릿을 사용하여 타입에 독립적인 함수 객체 생성

    struct Print {
        template<typename T>
        void operator()(const T& val) const {
            cout << "    " << val << "\n";
        }
    };

    cout << "  [제네릭 Functor]\n";
    Print printer;
    printer(42);
    printer(3.14);
    printer(string("Hello, Functor!"));
    cout << "\n";
}


// =========================================================================
//  레슨 2 — std::function
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────┐
    │  std::function<반환형(인자형...)>                                │
    │                                                                 │
    │  함수 포인터, 람다, 함수 객체를 모두 담을 수 있는 통합 래퍼     │
    │                                                                 │
    │  ┌────────────┐                                                 │
    │  │ 함수 포인터 │──┐                                             │
    │  └────────────┘  │    ┌────────────────────┐                   │
    │  ┌────────────┐  ├──▶│ std::function<...> │                   │
    │  │   람 다    │──┤    └────────────────────┘                   │
    │  └────────────┘  │                                              │
    │  ┌────────────┐  │                                              │
    │  │  Functor   │──┘                                              │
    │  └────────────┘                                                 │
    └─────────────────────────────────────────────────────────────────┘
*/
void lesson2_std_function() {
    cout << "┌──────────────────────────────────────────┐\n";
    cout << "│  레슨 2 : std::function                  │\n";
    cout << "└──────────────────────────────────────────┘\n\n";

    // ─── 2-1: 일반 함수를 std::function에 저장 ─────────────────────

    // 일반 함수 정의 (람다로 대체)
    auto regular_add = [](int a, int b) -> int { return a + b; };

    function<int(int, int)> func;
    func = regular_add;  // 일반 함수 저장

    cout << "  [일반 함수 저장]\n";
    cout << "  func(3, 4) = " << func(3, 4) << "\n\n";

    // ─── 2-2: 람다를 std::function에 저장 ───────────────────────────

    function<int(int, int)> lambda_func = [](int a, int b) {
        return a * b;
    };

    cout << "  [람다 저장]\n";
    cout << "  lambda_func(3, 4) = " << lambda_func(3, 4) << "\n\n";

    // ─── 2-3: Functor를 std::function에 저장 ────────────────────────

    struct Power {
        int operator()(int base, int exp) const {
            int result = 1;
            for (int i = 0; i < exp; ++i) result *= base;
            return result;
        }
    };

    function<int(int, int)> functor_func = Power();

    cout << "  [Functor 저장]\n";
    cout << "  functor_func(2, 8) = " << functor_func(2, 8) << "\n\n";

    // ─── 2-4: std::function을 컨테이너에 저장 ───────────────────────
    // 다양한 종류의 호출 가능 객체를 하나의 벡터에!

    vector<function<int(int, int)>> operations;
    operations.push_back([](int a, int b) { return a + b; });  // 덧셈
    operations.push_back([](int a, int b) { return a - b; });  // 뺄셈
    operations.push_back([](int a, int b) { return a * b; });  // 곱셈

    string op_names[] = {"덧셈", "뺄셈", "곱셈"};

    cout << "  [연산 함수 벡터] (10, 3) 에 대해:\n";
    for (size_t i = 0; i < operations.size(); ++i) {
        cout << "    " << op_names[i] << ": " << operations[i](10, 3) << "\n";
    }
    cout << "\n";

    // ─── 2-5: 콜백 패턴 ────────────────────────────────────────────
    // std::function을 사용한 콜백(callback) 패턴 구현

    // 콜백을 받아 처리하는 함수
    auto process_with_callback = [](int value,
                                     function<void(int)> on_success,
                                     function<void(string)> on_error) {
        if (value > 0) {
            on_success(value * 2);
        } else {
            on_error("음수 값은 처리할 수 없습니다!");
        }
    };

    cout << "  [콜백 패턴]\n";

    // 성공 콜백
    process_with_callback(5,
        [](int result) { cout << "    성공! 결과: " << result << "\n"; },
        [](string err)  { cout << "    실패: " << err << "\n"; }
    );

    // 실패 콜백
    process_with_callback(-3,
        [](int result) { cout << "    성공! 결과: " << result << "\n"; },
        [](string err)  { cout << "    실패: " << err << "\n"; }
    );

    // ─── 2-6: std::function의 빈 상태 확인 ─────────────────────────
    function<void()> empty_func;

    cout << "\n  [빈 상태 확인]\n";
    cout << "  empty_func이 비어있는가? " << (empty_func ? "아니오" : "예") << "\n";

    empty_func = []() { cout << "    이제 할당됨!\n"; };
    cout << "  할당 후 비어있는가?      " << (empty_func ? "아니오" : "예") << "\n";
    empty_func();
    cout << "\n";
}


// =========================================================================
//  레슨 3 — std::bind & 부분 적용 (Partial Application)
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────┐
    │  std::bind와 부분 적용(Partial Application)                     │
    │                                                                 │
    │  함수의 일부 인자를 미리 고정하여 새 함수를 생성!               │
    │                                                                 │
    │  원본: f(a, b, c)                                               │
    │  바인드: g = bind(f, 10, _1, _2)                                │
    │  결과: g(b, c) → f(10, b, c)                                    │
    │                                                                 │
    │  ┌──────────────────────┐     bind(f, 10, _1)                  │
    │  │ f(x, y) = x + y     │ ──────────────────────▶ g(y) = 10+y  │
    │  └──────────────────────┘     x를 10으로 고정                  │
    └─────────────────────────────────────────────────────────────────┘
*/
void lesson3_bind_partial() {
    cout << "┌──────────────────────────────────────────┐\n";
    cout << "│  레슨 3 : std::bind & 부분 적용          │\n";
    cout << "└──────────────────────────────────────────┘\n\n";

    using namespace std::placeholders;  // _1, _2, _3...

    // ─── 3-1: 기본 bind 사용법 ──────────────────────────────────────
    auto multiply = [](int a, int b) { return a * b; };

    // 첫 번째 인자를 10으로 고정 → 새 함수 생성
    auto times10 = bind(multiply, 10, _1);

    cout << "  [기본 bind]\n";
    cout << "  times10(5) = " << times10(5) << "  (10 * 5)\n";
    cout << "  times10(3) = " << times10(3) << "  (10 * 3)\n\n";

    // ─── 3-2: 인자 순서 변경 ────────────────────────────────────────
    auto divide = [](double a, double b) { return a / b; };

    // _2, _1을 사용하여 인자 순서를 바꿀 수 있다!
    auto reverse_divide = bind(divide, _2, _1);

    cout << "  [인자 순서 변경]\n";
    cout << "  divide(10, 2)         = " << divide(10, 2) << "\n";
    cout << "  reverse_divide(10, 2) = " << reverse_divide(10, 2) << "  (2/10)\n\n";

    // ─── 3-3: 멤버 함수 바인딩 ──────────────────────────────────────
    struct Calculator {
        string name;
        Calculator(string n) : name(n) {}

        int add(int a, int b) const {
            return a + b;
        }
        int sub(int a, int b) const {
            return a - b;
        }
    };

    Calculator calc("MyCalc");

    // 멤버 함수 + 객체를 바인딩
    auto calc_add = bind(&Calculator::add, &calc, _1, _2);
    auto add_to_100 = bind(&Calculator::add, &calc, 100, _1);

    cout << "  [멤버 함수 바인딩]\n";
    cout << "  calc_add(3, 4)  = " << calc_add(3, 4) << "\n";
    cout << "  add_to_100(50)  = " << add_to_100(50) << "\n\n";

    // ─── 3-4: 커링(Currying) 패턴 ──────────────────────────────────
    /*
        커링: 다인자 함수를 단일 인자 함수의 체인으로 변환
        f(a, b, c) → f(a)(b)(c)

        ┌───────────────────┐      커링       ┌───┐ ┌───┐ ┌───┐
        │ f(a, b, c) = a+b+c│  ──────────▶   │f(a)│→│g(b)│→│h(c)│
        └───────────────────┘                 └───┘ └───┘ └───┘
    */

    // C++ 스타일 커링: 람다를 반환하는 람다
    auto curried_add = [](int a) {
        return [a](int b) {
            return [a, b](int c) {
                return a + b + c;
            };
        };
    };

    cout << "  [커링 (Currying)]\n";
    cout << "  curried_add(1)(2)(3) = " << curried_add(1)(2)(3) << "\n";

    // 부분 적용으로 재사용
    auto add1 = curried_add(1);
    auto add1_2 = add1(2);
    cout << "  add1 = curried_add(1)\n";
    cout << "  add1_2 = add1(2)\n";
    cout << "  add1_2(3) = " << add1_2(3) << "\n\n";

    // ─── 3-5: 실용적인 부분 적용 예제 ──────────────────────────────
    // 로그 함수에 레벨을 미리 바인딩

    auto log_message = [](const string& level, const string& module,
                           const string& msg) {
        cout << "    [" << level << "] " << module << ": " << msg << "\n";
    };

    // 레벨을 고정한 전문 로거 생성
    auto log_error = bind(log_message, "ERROR", _1, _2);
    auto log_info  = bind(log_message, "INFO",  _1, _2);

    // 레벨 + 모듈을 고정
    auto db_error = bind(log_message, "ERROR", "Database", _1);

    cout << "  [실용 - 로그 바인딩]\n";
    log_error("Network", "연결 실패");
    log_info("App", "시작됨");
    db_error("쿼리 타임아웃");
    cout << "\n";
}


// =========================================================================
//  레슨 4 — 고차 함수 (Higher-Order Functions)
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────┐
    │  고차 함수: 함수를 인자로 받거나 함수를 반환하는 함수           │
    │                                                                 │
    │  ┌──────┐    함수를 인자로    ┌──────────┐    함수를 반환       │
    │  │ map  │ ◀─────────────── │ compose  │ ─────────────▶ 새함수 │
    │  │filter│   transform(f)    │ pipe     │   f∘g               │
    │  │reduce│                   └──────────┘                       │
    │  └──────┘                                                       │
    │                                                                 │
    │  map(f, [1,2,3])    → [f(1), f(2), f(3)]                      │
    │  filter(p, [1,2,3]) → [x | p(x) == true]                      │
    │  reduce(f, [1,2,3]) → f(f(1,2), 3)                            │
    └─────────────────────────────────────────────────────────────────┘
*/
void lesson4_higher_order() {
    cout << "┌──────────────────────────────────────────┐\n";
    cout << "│  레슨 4 : 고차 함수 (Higher-Order)       │\n";
    cout << "└──────────────────────────────────────────┘\n\n";

    // ─── 4-1: map 직접 구현 ─────────────────────────────────────────
    // 벡터의 모든 원소에 함수 f를 적용하여 새 벡터 반환

    auto my_map = [](const vector<int>& v, function<int(int)> f) {
        vector<int> result;
        result.reserve(v.size());
        for (int x : v) {
            result.push_back(f(x));
        }
        return result;
    };

    vector<int> numbers = {1, 2, 3, 4, 5, 6, 7, 8};

    auto doubled = my_map(numbers, [](int x) { return x * 2; });
    auto squared = my_map(numbers, [](int x) { return x * x; });

    cout << "  [my_map 구현]\n";
    cout << "  원본:   ";
    for (int n : numbers) cout << n << " ";
    cout << "\n  x2:     ";
    for (int n : doubled) cout << n << " ";
    cout << "\n  제곱:   ";
    for (int n : squared) cout << n << " ";
    cout << "\n\n";

    // ─── 4-2: filter 직접 구현 ──────────────────────────────────────
    // 조건 함수(predicate)를 만족하는 원소만 남기기

    auto my_filter = [](const vector<int>& v, function<bool(int)> pred) {
        vector<int> result;
        for (int x : v) {
            if (pred(x)) result.push_back(x);
        }
        return result;
    };

    auto evens = my_filter(numbers, [](int x) { return x % 2 == 0; });
    auto greater_than_4 = my_filter(numbers, [](int x) { return x > 4; });

    cout << "  [my_filter 구현]\n";
    cout << "  짝수만:    ";
    for (int n : evens) cout << n << " ";
    cout << "\n  4보다 큰:  ";
    for (int n : greater_than_4) cout << n << " ";
    cout << "\n\n";

    // ─── 4-3: reduce 직접 구현 ──────────────────────────────────────
    // 벡터를 하나의 값으로 축약 (fold/accumulate)
    //
    //  reduce(+, 0, [1,2,3,4]) 의 동작:
    //    0 + 1 = 1
    //    1 + 2 = 3
    //    3 + 3 = 6
    //    6 + 4 = 10

    auto my_reduce = [](const vector<int>& v, int init,
                         function<int(int, int)> f) {
        int acc = init;
        for (int x : v) {
            acc = f(acc, x);
        }
        return acc;
    };

    int sum = my_reduce(numbers, 0, [](int a, int b) { return a + b; });
    int product = my_reduce(numbers, 1, [](int a, int b) { return a * b; });
    int max_val = my_reduce(numbers, numbers[0],
                            [](int a, int b) { return a > b ? a : b; });

    cout << "  [my_reduce 구현]\n";
    cout << "  합계:   " << sum << "\n";
    cout << "  곱:     " << product << "\n";
    cout << "  최대값: " << max_val << "\n\n";

    // ─── 4-4: 함수를 반환하는 함수 ──────────────────────────────────
    // "함수 공장" - 함수를 생성하여 반환

    auto make_adder = [](int n) -> function<int(int)> {
        return [n](int x) { return x + n; };
    };

    auto make_multiplier = [](int n) -> function<int(int)> {
        return [n](int x) { return x * n; };
    };

    auto add5  = make_adder(5);
    auto mul3  = make_multiplier(3);

    cout << "  [함수 공장]\n";
    cout << "  add5(10)  = " << add5(10) << "\n";
    cout << "  mul3(10)  = " << mul3(10) << "\n\n";

    // ─── 4-5: map + filter + reduce 체이닝 ──────────────────────────
    //  "1~8에서 짝수만 골라서 제곱하고 합산"
    //  filter(짝수) → map(제곱) → reduce(합산)

    auto step1 = my_filter(numbers, [](int x) { return x % 2 == 0; });
    auto step2 = my_map(step1, [](int x) { return x * x; });
    auto step3 = my_reduce(step2, 0, [](int a, int b) { return a + b; });

    cout << "  [체이닝: filter → map → reduce]\n";
    cout << "  원본:           ";
    for (int n : numbers) cout << n << " ";
    cout << "\n  짝수 필터:      ";
    for (int n : step1) cout << n << " ";
    cout << "\n  제곱:           ";
    for (int n : step2) cout << n << " ";
    cout << "\n  합산:           " << step3 << "\n";
    cout << "  (4+16+36+64 = " << step3 << ")\n\n";
}


// =========================================================================
//  레슨 5 — 클로저와 캡처 심화
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────┐
    │  클로저(Closure): 자신이 생성된 환경의 변수를 캡처한 함수       │
    │                                                                 │
    │  캡처 방식:                                                     │
    │  [=]       → 모든 변수를 값으로 캡처 (복사)                     │
    │  [&]       → 모든 변수를 참조로 캡처                            │
    │  [x]       → x만 값으로 캡처                                    │
    │  [&x]      → x만 참조로 캡처                                    │
    │  [=, &x]   → 기본 값 캡처, x만 참조                            │
    │  [x = expr] → 초기화 캡처 (C++14)                               │
    │                                                                 │
    │  ┌────────────────────┐                                         │
    │  │  외부 스코프        │                                         │
    │  │  int x = 10;       │                                         │
    │  │  ┌──────────────┐  │                                         │
    │  │  │  람다 내부    │  │  ← x를 캡처하여 사용                   │
    │  │  │  [x](){...}  │  │                                         │
    │  │  └──────────────┘  │                                         │
    │  └────────────────────┘                                         │
    └─────────────────────────────────────────────────────────────────┘
*/
void lesson5_closure_advanced() {
    cout << "┌──────────────────────────────────────────┐\n";
    cout << "│  레슨 5 : 클로저와 캡처 심화             │\n";
    cout << "└──────────────────────────────────────────┘\n\n";

    // ─── 5-1: mutable 람다 ──────────────────────────────────────────
    // 기본적으로 값 캡처된 변수는 const!
    // mutable 키워드로 수정 가능하게 변경

    int initial = 0;
    auto counter = [initial]() mutable -> int {
        return ++initial;  // mutable이 없으면 컴파일 에러!
    };

    cout << "  [mutable 람다]\n";
    cout << "  counter() = " << counter() << "\n";  // 1
    cout << "  counter() = " << counter() << "\n";  // 2
    cout << "  counter() = " << counter() << "\n";  // 3
    cout << "  원본 initial = " << initial << "  (변경 안 됨! 복사본이니까)\n\n";

    // ─── 5-2: 캡처 초기화 (C++14 init capture) ─────────────────────
    // 캡처 시점에 새 변수를 생성하고 초기화할 수 있다

    // unique_ptr같은 이동 전용 타입을 캡처할 때 유용!
    auto ptr = make_unique<int>(42);

    // C++14: 이동 캡처
    auto use_ptr = [p = move(ptr)]() {
        cout << "  캡처된 unique_ptr 값: " << *p << "\n";
    };

    cout << "  [캡처 초기화 (C++14)]\n";
    use_ptr();
    cout << "  ptr은 이제 nullptr (이동됨): "
         << (ptr == nullptr ? "예" : "아니오") << "\n\n";

    // 표현식으로 초기화
    int x = 10, y = 20;
    auto sum_capture = [sum = x + y]() {
        cout << "  캡처 시점의 x+y 합: " << sum << "\n";
    };

    x = 999;  // 이미 캡처했으므로 영향 없음
    cout << "  [표현식 캡처]\n";
    sum_capture();
    cout << "\n";

    // ─── 5-3: 제네릭 람다 (C++14) ──────────────────────────────────
    // auto를 인자 타입으로 사용 → 템플릿 함수 객체처럼 동작

    auto generic_print = [](const auto& value) {
        cout << "    값: " << value << "\n";
    };

    cout << "  [제네릭 람다 (auto 매개변수)]\n";
    generic_print(42);
    generic_print(3.14);
    generic_print(string("제네릭!"));
    cout << "\n";

    // 제네릭 람다로 최대값 함수 만들기
    auto generic_max = [](const auto& a, const auto& b) {
        return a > b ? a : b;
    };

    cout << "  [제네릭 max 람다]\n";
    cout << "  max(3, 7)       = " << generic_max(3, 7) << "\n";
    cout << "  max(3.14, 2.71) = " << generic_max(3.14, 2.71) << "\n";
    cout << "  max(\"abc\", \"xyz\") = " << generic_max(string("abc"), string("xyz")) << "\n\n";

    // ─── 5-4: 즉시 호출 람다 (IIFE) ────────────────────────────────
    // 람다를 정의하자마자 바로 호출하는 패턴
    // 복잡한 초기화에 유용!

    const auto config = [&]() {
        // 복잡한 초기화 로직...
        map<string, int> cfg;
        cfg["width"] = 1920;
        cfg["height"] = 1080;
        cfg["fps"] = 60;
        return cfg;
    }();  // ← () 로 즉시 호출!

    cout << "  [IIFE - 즉시 호출 람다]\n";
    cout << "  config[\"width\"]  = " << config.at("width") << "\n";
    cout << "  config[\"height\"] = " << config.at("height") << "\n";
    cout << "  config[\"fps\"]    = " << config.at("fps") << "\n\n";

    // ─── 5-5: 재귀 람다 ────────────────────────────────────────────
    // 람다가 자기 자신을 호출하려면 std::function 필요

    function<int(int)> factorial = [&factorial](int n) -> int {
        return n <= 1 ? 1 : n * factorial(n - 1);
    };

    cout << "  [재귀 람다 - 팩토리얼]\n";
    for (int i = 1; i <= 7; ++i) {
        cout << "  " << i << "! = " << factorial(i) << "\n";
    }
    cout << "\n";
}


// =========================================================================
//  레슨 6 — 파이프라인 패턴
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────┐
    │  파이프라인: 함수를 체인처럼 연결하여 데이터를 흘려보내기       │
    │                                                                 │
    │  데이터 → [함수1] → [함수2] → [함수3] → 최종 결과              │
    │                                                                 │
    │  입력         필터        변환        출력                       │
    │  ┌───┐    ┌────────┐  ┌────────┐  ┌────────┐                   │
    │  │ D │───▶│filter  │─▶│ map    │─▶│ reduce │─▶ 결과            │
    │  │ A │    │(짝수)  │  │(제곱)  │  │(합산)  │                   │
    │  │ T │    └────────┘  └────────┘  └────────┘                   │
    │  │ A │                                                          │
    │  └───┘                                                          │
    │                                                                 │
    │  compose(f, g)(x) = f(g(x))   ← 오른쪽에서 왼쪽으로 적용      │
    │  pipe(f, g)(x)    = g(f(x))   ← 왼쪽에서 오른쪽으로 적용      │
    └─────────────────────────────────────────────────────────────────┘
*/
void lesson6_pipeline() {
    cout << "┌──────────────────────────────────────────┐\n";
    cout << "│  레슨 6 : 파이프라인 패턴                │\n";
    cout << "└──────────────────────────────────────────┘\n\n";

    // ─── 6-1: compose 함수 구현 ─────────────────────────────────────
    // 두 함수를 합성: compose(f, g)(x) = f(g(x))

    auto compose = [](auto f, auto g) {
        return [f, g](auto x) {
            return f(g(x));
        };
    };

    auto double_it = [](int x) { return x * 2; };
    auto add_one   = [](int x) { return x + 1; };

    // (x * 2) + 1  =  double 먼저, add_one 나중
    auto double_then_add = compose(add_one, double_it);

    // (x + 1) * 2  =  add_one 먼저, double 나중
    auto add_then_double = compose(double_it, add_one);

    cout << "  [compose 함수]\n";
    cout << "  compose(add1, double)(5) = " << double_then_add(5)
         << "  (5*2+1=11)\n";
    cout << "  compose(double, add1)(5) = " << add_then_double(5)
         << "  ((5+1)*2=12)\n\n";

    // ─── 6-2: pipe 함수 구현 (가변 인자 버전) ──────────────────────
    // pipe(f, g, h)(x) = h(g(f(x)))  ← 왼→오 순서

    // 두 함수 파이프 (기본)
    auto pipe2 = [](auto f, auto g) {
        return [f, g](auto x) {
            return g(f(x));
        };
    };

    // 세 함수 파이프
    auto pipe3 = [](auto f, auto g, auto h) {
        return [f, g, h](auto x) {
            return h(g(f(x)));
        };
    };

    auto negate_it = [](int x) { return -x; };

    auto pipeline = pipe3(double_it, add_one, negate_it);
    // 5 → *2 → +1 → negate = -(5*2+1) = -11

    cout << "  [pipe 함수]\n";
    cout << "  pipe(double, add1, negate)(5) = " << pipeline(5)
         << "  (-(5*2+1)=-11)\n\n";

    // ─── 6-3: 데이터 처리 파이프라인 ────────────────────────────────
    // 문자열 데이터를 단계별로 변환하는 실용 예제
    //
    //  입력 문자열 → trim → uppercase → 접두사 추가 → 출력

    auto trim = [](const string& s) {
        size_t start = s.find_first_not_of(" \t");
        size_t end = s.find_last_not_of(" \t");
        return (start == string::npos) ? "" : s.substr(start, end - start + 1);
    };

    auto to_upper = [](string s) {
        for (auto& c : s) c = static_cast<char>(toupper(c));
        return s;
    };

    auto add_prefix = [](const string& s) {
        return "[LOG] " + s;
    };

    // 문자열 파이프라인 구축
    auto log_pipeline = pipe3(trim, to_upper, add_prefix);

    cout << "  [문자열 처리 파이프라인]\n";
    vector<string> messages = {
        "  hello world  ",
        "   error occurred   ",
        " system ready "
    };

    for (const auto& msg : messages) {
        cout << "  \"" << msg << "\" → " << log_pipeline(msg) << "\n";
    }
    cout << "\n";

    // ─── 6-4: 벡터 파이프라인 (fluent interface 스타일) ─────────────
    // 체이닝을 위한 래퍼 클래스

    // Pipeline 클래스 정의 (구조체로 간단하게)
    struct VecPipe {
        vector<int> data;

        VecPipe(vector<int> d) : data(move(d)) {}

        VecPipe filter(function<bool(int)> pred) const {
            vector<int> result;
            for (int x : data) {
                if (pred(x)) result.push_back(x);
            }
            return VecPipe(result);
        }

        VecPipe map(function<int(int)> f) const {
            vector<int> result;
            for (int x : data) {
                result.push_back(f(x));
            }
            return VecPipe(result);
        }

        int reduce(int init, function<int(int, int)> f) const {
            int acc = init;
            for (int x : data) acc = f(acc, x);
            return acc;
        }

        void print(const string& label) const {
            cout << "  " << label << ": ";
            for (int x : data) cout << x << " ";
            cout << "\n";
        }
    };

    cout << "  [벡터 파이프라인 (Fluent Interface)]\n";

    VecPipe({1, 2, 3, 4, 5, 6, 7, 8, 9, 10})
        .filter([](int x) { return x % 2 == 0; })  // 짝수 필터
        .map([](int x) { return x * x; })           // 제곱
        .print("짝수→제곱");

    int total = VecPipe({1, 2, 3, 4, 5, 6, 7, 8, 9, 10})
        .filter([](int x) { return x > 5; })
        .map([](int x) { return x * 3; })
        .reduce(0, [](int a, int b) { return a + b; });

    cout << "  >5 필터→x3→합계: " << total << "\n\n";
}


// =========================================================================
//  레슨 7 — 실전 종합
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────┐
    │  실전 종합: 함수형 프로그래밍 기법을 활용한 실용 예제           │
    │                                                                 │
    │  1. 이벤트 핸들러 시스템                                        │
    │  2. 콜백 기반 작업 시스템                                       │
    │  3. 함수형 데이터 변환 파이프라인                               │
    │                                                                 │
    │  ┌──────────┐  이벤트   ┌────────────┐  콜백   ┌────────┐     │
    │  │ 이벤트   │─────────▶│ 핸들러     │───────▶│ 결과   │     │
    │  │ 발생     │          │ 디스패처   │        │ 처리   │     │
    │  └──────────┘          └────────────┘        └────────┘     │
    └─────────────────────────────────────────────────────────────────┘
*/
void lesson7_practical() {
    cout << "┌──────────────────────────────────────────┐\n";
    cout << "│  레슨 7 : 실전 종합                      │\n";
    cout << "└──────────────────────────────────────────┘\n\n";

    // ─── 7-1: 이벤트 핸들러 시스템 ──────────────────────────────────
    /*
        이벤트 이름(문자열)에 여러 핸들러를 등록하고,
        이벤트 발생 시 등록된 모든 핸들러를 호출하는 시스템

        ┌────────┐  on("click", handler1)  ┌──────────────────────┐
        │        │  on("click", handler2)  │  EventEmitter        │
        │ 사용자 │ ─────────────────────▶ │  handlers:           │
        │        │  emit("click", data)    │    "click"→[h1,h2]  │
        │        │ ─────────────────────▶ │    "hover"→[h3]     │
        └────────┘                         └──────────────────────┘
    */

    struct EventEmitter {
        // 이벤트 이름 → 핸들러 리스트
        map<string, vector<function<void(const string&)>>> handlers;

        // 이벤트 핸들러 등록
        void on(const string& event, function<void(const string&)> handler) {
            handlers[event].push_back(handler);
        }

        // 이벤트 발생 (모든 핸들러 호출)
        void emit(const string& event, const string& data) {
            if (handlers.count(event)) {
                for (auto& handler : handlers[event]) {
                    handler(data);
                }
            }
        }
    };

    EventEmitter emitter;

    // 핸들러 등록
    emitter.on("click", [](const string& data) {
        cout << "    [버튼 핸들러] 클릭됨: " << data << "\n";
    });
    emitter.on("click", [](const string& data) {
        cout << "    [로그 핸들러] 클릭 기록: " << data << "\n";
    });
    emitter.on("hover", [](const string& data) {
        cout << "    [UI 핸들러] 마우스 오버: " << data << "\n";
    });

    cout << "  [이벤트 핸들러 시스템]\n";
    emitter.emit("click", "확인 버튼");
    emitter.emit("hover", "메뉴 아이템");
    emitter.emit("keypress", "없는 이벤트");  // 핸들러 없음
    cout << "\n";

    // ─── 7-2: 콜백 기반 작업 시스템 ─────────────────────────────────
    /*
        작업(Task)을 등록하고 순차 실행. 각 작업은 콜백으로 결과를 보고.

        ┌──────┐    ┌──────┐    ┌──────┐
        │Task1 │───▶│Task2 │───▶│Task3 │───▶ 완료
        │ (콜백)│    │ (콜백)│    │ (콜백)│
        └──────┘    └──────┘    └──────┘
    */

    struct TaskRunner {
        vector<pair<string, function<int()>>> tasks;

        void add_task(const string& name, function<int()> task) {
            tasks.push_back({name, task});
        }

        void run_all(function<void(const string&, int)> on_complete) {
            for (auto& [name, task] : tasks) {
                int result = task();
                on_complete(name, result);
            }
        }
    };

    TaskRunner runner;
    runner.add_task("데이터 로드", []() { return 100; });
    runner.add_task("데이터 변환", []() { return 200; });
    runner.add_task("결과 저장",   []() { return 300; });

    cout << "  [콜백 기반 작업 시스템]\n";
    runner.run_all([](const string& name, int result) {
        cout << "    ✓ " << name << " 완료 (결과: " << result << ")\n";
    });
    cout << "\n";

    // ─── 7-3: 함수형 데이터 변환 ────────────────────────────────────
    // 학생 데이터를 함수형으로 처리하는 종합 예제

    struct Student {
        string name;
        int score;
        string grade;
    };

    vector<Student> students = {
        {"김철수", 95, ""}, {"이영희", 72, ""}, {"박민수", 88, ""},
        {"정수진", 64, ""}, {"최강훈", 91, ""}, {"한지민", 55, ""},
        {"오세훈", 78, ""}, {"윤서연", 83, ""}
    };

    // 1단계: 등급 부여 (map/transform)
    auto assign_grade = [](Student s) -> Student {
        if (s.score >= 90)      s.grade = "A";
        else if (s.score >= 80) s.grade = "B";
        else if (s.score >= 70) s.grade = "C";
        else if (s.score >= 60) s.grade = "D";
        else                    s.grade = "F";
        return s;
    };

    vector<Student> graded;
    transform(students.begin(), students.end(), back_inserter(graded), assign_grade);

    // 2단계: 합격자 필터 (score >= 60)
    vector<Student> passed;
    copy_if(graded.begin(), graded.end(), back_inserter(passed),
            [](const Student& s) { return s.score >= 60; });

    // 3단계: 평균 점수 계산 (reduce)
    double avg = accumulate(passed.begin(), passed.end(), 0.0,
        [](double sum, const Student& s) { return sum + s.score; }
    ) / passed.size();

    cout << "  [함수형 데이터 변환 - 학생 성적]\n";
    cout << "  ┌──────────┬──────┬──────┐\n";
    cout << "  │  이 름   │ 점수 │ 등급 │\n";
    cout << "  ├──────────┼──────┼──────┤\n";
    for (const auto& s : graded) {
        // 이름 패딩 처리
        cout << "  │ " << s.name;
        // 간단한 정렬을 위해 공백 추가
        for (size_t i = s.name.size(); i < 12; ++i) cout << " ";
        cout << "│  " << s.score;
        if (s.score < 100) cout << " ";
        cout << " │  " << s.grade << "   │\n";
    }
    cout << "  └──────────┴──────┴──────┘\n";
    cout << "  합격자 수: " << passed.size() << "명\n";
    cout << "  합격자 평균: " << avg << "점\n\n";

    // ─── 7-4: 함수 합성으로 변환 파이프라인 ─────────────────────────
    // 숫자 리스트를 다양한 함수 합성으로 변환

    auto compose = [](auto f, auto g) {
        return [f, g](auto x) { return f(g(x)); };
    };

    auto to_celsius = [](double fahrenheit) { return (fahrenheit - 32) * 5.0 / 9.0; };
    auto round_to_int = [](double x) { return static_cast<int>(x + 0.5); };
    auto to_string_c = [](int x) { return to_string(x) + "°C"; };

    // 파이프라인: 화씨 → 섭씨 → 반올림 → 문자열
    auto temp_pipeline = compose(to_string_c, compose(round_to_int, to_celsius));

    vector<double> temps_f = {32.0, 68.0, 100.0, 212.0, 98.6};

    cout << "  [온도 변환 파이프라인]\n";
    for (double f : temps_f) {
        cout << "  " << f << "°F → " << temp_pipeline(f) << "\n";
    }

    // ═══════════════════════════════════════════════════════════════════
    //  연습 문제 (직접 풀어보세요!)
    // ═══════════════════════════════════════════════════════════════════
    cout << "\n";
    cout << "  ┌─────────────────────────────────────────────────────┐\n";
    cout << "  │  연습 문제                                          │\n";
    cout << "  ├─────────────────────────────────────────────────────┤\n";
    cout << "  │  1. 문자열 벡터를 받아 길이가 N 이상인 문자열만    │\n";
    cout << "  │     필터링하는 함수 객체(Functor)를 만드세요.      │\n";
    cout << "  │                                                     │\n";
    cout << "  │  2. std::function을 사용하여 사칙연산 계산기를     │\n";
    cout << "  │     map<string, function<double(double,double)>>   │\n";
    cout << "  │     으로 구현하세요.                                │\n";
    cout << "  │                                                     │\n";
    cout << "  │  3. compose를 사용하여 다음 변환 파이프라인을      │\n";
    cout << "  │     만드세요: 문자열 → 소문자 → 공백제거 → 역순   │\n";
    cout << "  │                                                     │\n";
    cout << "  │  4. 커링을 활용하여 printf 스타일의 포맷터를       │\n";
    cout << "  │     만드세요: format(패턴)(값) → 결과 문자열       │\n";
    cout << "  │                                                     │\n";
    cout << "  │  5. EventEmitter에 once() 메서드를 추가하세요.     │\n";
    cout << "  │     (한 번만 실행되고 자동으로 해제되는 핸들러)    │\n";
    cout << "  └─────────────────────────────────────────────────────┘\n\n";
}
