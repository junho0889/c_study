/*
=============================================================================
  C++ 학습 10단계: 모던 C++ (C++17 / C++20 주요 기능)
=============================================================================
  [학습 목표]
  1. C++17 핵심 기능을 사용할 수 있다
  2. C++20 주요 기능을 이해한다
  3. 실무에서 자주 쓰이는 모던 패턴을 안다

  [컴파일]
  C++17: g++ -std=c++17 -o 10_modern main.cpp
  C++20: g++ -std=c++20 -o 10_modern main.cpp
=============================================================================
*/
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <optional>     // C++17
#include <variant>      // C++17
#include <any>          // C++17
#include <tuple>
#include <algorithm>
#include <numeric>
using namespace std;

void lesson1_cpp17_basics();
void lesson2_optional_variant();
void lesson3_structured_bindings();
void lesson4_constexpr_if();
void lesson5_cpp20_preview();

int main() {
    cout << "========================================\n";
    cout << "  C++ 10단계 : 모던 C++\n";
    cout << "========================================\n\n";

    lesson1_cpp17_basics();
    lesson2_optional_variant();
    lesson3_structured_bindings();
    lesson4_constexpr_if();
    lesson5_cpp20_preview();

    cout << "\n10단계 학습 완료!\n";
    return 0;
}


// =====================================================================
// 레슨 1 — C++17 기본 개선사항
// =====================================================================
void lesson1_cpp17_basics() {
    cout << "[레슨 1] C++17 기본 개선\n\n";

    // ── 1) if / switch 초기화 문 ──
    cout << "  --- if 초기화문 ---\n";
    vector<int> v = {1, 2, 3, 4, 5};

    if (auto it = find(v.begin(), v.end(), 3); it != v.end()) {
        cout << "  찾음: " << *it << " (위치: " << (it - v.begin()) << ")\n";
    }
    // it은 if 블록 밖에서 접근 불가 (깔끔!)

    // ── 2) 중첩 네임스페이스 ──
    /*
    C++11:  namespace A { namespace B { namespace C { ... }}}
    C++17:  namespace A::B::C { ... }     ← 훨씬 깔끔!
    */

    // ── 3) string_view (C++17) ──
    // 문자열을 복사하지 않고 '참조'만 → 성능 향상
    // #include <string_view>
    // void process(string_view sv) { ... }

    // ── 4) [[nodiscard]] 속성 ──
    /*
    [[nodiscard]] int compute() { return 42; }
    compute();  // 경고!  반환값을 쓰지 않았다
    int r = compute();  // OK
    → 반환값을 무시하면 안 되는 함수에 사용
    */

    // ── 5) auto 템플릿 매개변수 ──
    auto print_all = [](const auto& container) {
        for (const auto& item : container)
            cout << item << " ";
        cout << "\n";
    };
    cout << "  auto 람다: ";
    print_all(vector<int>{10, 20, 30});

    cout << endl;
}


// =====================================================================
// 레슨 2 — optional, variant, any
// =====================================================================
void lesson2_optional_variant() {
    cout << "[레슨 2] optional, variant, any\n\n";

    /*
    ★ optional<T>  : 값이 있을 수도, 없을 수도 있음
      → nullptr 반환 대신 사용 (더 안전)
      → 다른 언어의 Nullable, Maybe와 비슷

    ★ variant<T1,T2,...> : 여러 타입 중 하나를 저장
      → C의 union을 안전하게 대체

    ★ any : 아무 타입이나 저장 (비추천, 타입 안전성 낮음)
    */

    // optional: "값이 없을 수 있다"
    cout << "  --- optional ---\n";
    auto find_user = [](int id) -> optional<string> {
        if (id == 1) return "홍길동";
        if (id == 2) return "김철수";
        return nullopt;   // 값 없음!
    };

    if (auto name = find_user(1); name.has_value()) {
        cout << "  ID 1: " << name.value() << "\n";
    }
    if (auto name = find_user(99)) {  // bool 변환도 가능
        cout << "  ID 99: " << *name << "\n";
    } else {
        cout << "  ID 99: 사용자 없음\n";
    }

    // value_or: 값이 없으면 기본값 사용
    cout << "  ID 99 (기본값): " << find_user(99).value_or("미등록") << "\n\n";

    // variant: "이 중 하나의 타입"
    cout << "  --- variant ---\n";
    variant<int, double, string> data;

    data = 42;
    cout << "  int: " << get<int>(data) << "\n";

    data = 3.14;
    cout << "  double: " << get<double>(data) << "\n";

    data = "Hello"s;
    cout << "  string: " << get<string>(data) << "\n";

    // 현재 타입 확인
    cout << "  현재 인덱스: " << data.index() << " (0=int,1=double,2=string)\n";

    // visit: variant에 저장된 값에 따라 다른 처리
    visit([](auto&& val) {
        cout << "  visit: " << val << "\n";
    }, data);

    cout << endl;
}


// =====================================================================
// 레슨 3 — 구조적 바인딩 (Structured Bindings)
// =====================================================================
void lesson3_structured_bindings() {
    cout << "[레슨 3] 구조적 바인딩 (C++17)\n\n";

    /*
    ★ 구조적 바인딩 = 여러 값을 한꺼번에 변수에 대입
      → pair, tuple, struct, 배열에 사용 가능
      → Python의 a, b = (1, 2)와 비슷
    */

    // pair
    pair<string, int> p = {"홍길동", 25};
    auto [name, age] = p;   // 한번에 분해!
    cout << "  pair: " << name << " " << age << "\n";

    // map 순회
    map<string, int> scores = {{"국어", 90}, {"영어", 85}, {"수학", 92}};
    cout << "  map 순회:\n";
    for (const auto& [subject, score] : scores) {
        cout << "    " << subject << ": " << score << "\n";
    }

    // tuple
    auto get_info = []() -> tuple<string, int, double> {
        return {"이영희", 22, 95.5};
    };
    auto [n, a, s] = get_info();
    cout << "  tuple: " << n << " " << a << "세 " << s << "점\n";

    // 배열
    int arr[] = {10, 20, 30};
    auto [x, y, z] = arr;
    cout << "  배열: " << x << " " << y << " " << z << "\n";

    cout << endl;
}


// =====================================================================
// 레슨 4 — constexpr if & fold expressions
// =====================================================================
// constexpr if: 컴파일 시점에 조건 분기 (템플릿에서 유용)
template <typename T>
string type_name(T value) {
    if constexpr (is_integral_v<T>) {
        return "정수형: " + to_string(value);
    } else if constexpr (is_floating_point_v<T>) {
        return "실수형: " + to_string(value);
    } else {
        return "기타";
    }
}

// fold expression (C++17): 가변 인자 템플릿을 간결하게
template <typename... Args>
auto sum_all(Args... args) {
    return (args + ...);   // 모든 인자를 + 로 접기
}

template <typename... Args>
void print_all(Args... args) {
    ((cout << args << " "), ...);   // 각 인자를 출력
    cout << "\n";
}

void lesson4_constexpr_if() {
    cout << "[레슨 4] constexpr if & fold expressions\n\n";

    cout << "  " << type_name(42) << "\n";
    cout << "  " << type_name(3.14) << "\n\n";

    cout << "  sum_all(1,2,3,4,5) = " << sum_all(1, 2, 3, 4, 5) << "\n";
    cout << "  print_all: ";
    print_all(1, 2.5, "hello", 'X');

    cout << endl;
}


// =====================================================================
// 레슨 5 — C++20 미리보기
// =====================================================================
void lesson5_cpp20_preview() {
    cout << "[레슨 5] C++20 주요 기능 미리보기\n\n";

    /*
    ★ C++20 주요 기능 (컴파일러 지원에 따라 사용 가능)

    1) Concepts (개념)
       → 템플릿 타입에 조건 부여
       template <typename T>
         requires integral<T>
       T add(T a, T b) { return a + b; }

    2) Ranges (범위)
       → 파이프라인 스타일로 데이터 처리
       auto result = numbers | views::filter(is_even)
                             | views::transform(double_it);

    3) Coroutines (코루틴)
       → 비동기 프로그래밍, co_await, co_yield

    4) Modules (모듈)
       → #include 대체, 컴파일 속도 향상
       import std;

    5) Three-way comparison (우주선 연산자 <=>)
       → ==, <, >, <=, >= 를 한번에 정의
       auto operator<=>(const MyClass&) const = default;

    6) std::format (포맷 문자열)
       → printf의 안전한 대체
       string s = format("{} is {} years old", name, age);

    7) std::span
       → 배열이나 vector의 '뷰' (복사 없이 참조)
    */

    // C++20은 컴파일러 버전에 따라 지원 여부가 다르므로
    // 여기서는 개념 설명만 제공합니다

    cout << "  C++20은 아래 기능들을 제공합니다:\n";
    cout << "  1. Concepts   - 템플릿 타입 제약\n";
    cout << "  2. Ranges     - 파이프라인 데이터 처리\n";
    cout << "  3. Coroutines - 비동기 프로그래밍\n";
    cout << "  4. Modules    - #include 대체\n";
    cout << "  5. <=>        - 비교 연산자 자동 생성\n";
    cout << "  6. format()   - 안전한 문자열 포맷팅\n";
    cout << "  7. span       - 배열/벡터 뷰\n\n";

    cout << "  사용하려면: g++ -std=c++20 으로 컴파일\n";

    /*
    ★ C++ 버전 요약
    ┌─────────┬───────────────────────────────────────┐
    │ C++11   │ auto, 람다, 스마트포인터, move, 범위for│
    │ C++14   │ 제네릭 람다, 리터럴 개선              │
    │ C++17   │ optional, variant, 구조적바인딩, if초기화│
    │ C++20   │ concepts, ranges, coroutines, modules │
    │ C++23   │ 더 많은 ranges, expected, stacktrace  │
    └─────────┴───────────────────────────────────────┘

    실무에서는 C++17이 현재 가장 널리 사용됨 (2024~2026 기준)
    */

    cout << endl;
}
