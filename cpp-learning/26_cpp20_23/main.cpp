/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C++ 학습 26단계: C++20/23 실전 코드 (Modern C++ Deep Dive)
  ─ Concepts, Ranges, Coroutines, <=>, expected, Modules, span, jthread ─

  C++20은 C++11 이래 가장 큰 표준 업데이트입니다.
  C++23은 그 위에 편의 기능과 안전성을 추가합니다.

  ■ 컴파일 (C++17 모드 - 기본 안전 모드):
    g++ -std=c++17 -Wall -o 26_modern main.cpp
  ■ C++20 기능을 활성화하려면:
    g++ -std=c++20 -Wall -fconcepts -fcoroutines -o 26_modern main.cpp
  ■ C++23 기능 (GCC 13+, Clang 17+):
    g++ -std=c++2b -Wall -o 26_modern main.cpp
  ■ MSVC:
    cl /EHsc /std:c++20 main.cpp
    cl /EHsc /std:c++latest main.cpp   (C++23)

  ■ 참고: 많은 C++20/23 기능은 컴파일러 지원이 다를 수 있으므로
    조건부 컴파일(#if)을 사용하여 C++17에서도 컴파일 가능하게 했습니다.

  ■ 목차:
    레슨 1 — Concepts (C++20)             (제약 조건, requires)
    레슨 2 — Ranges (C++20)               (views, 파이프라인)
    레슨 3 — Coroutines (C++20)           (co_yield, co_await)
    레슨 4 — Three-way Comparison (<=>)   (우주선 연산자)
    레슨 5 — std::expected (C++23)        (에러 처리 새 패턴)
    레슨 6 — Modules (C++20)              (import/export)
    레슨 7 — 기타 유용한 기능             (span, jthread, source_location)

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// ── C++ 버전 감지 매크로 ──
// __cplusplus 값:
//   201703L → C++17
//   202002L → C++20
//   202302L → C++23

#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <numeric>
#include <functional>
#include <optional>
#include <variant>
#include <type_traits>
#include <cassert>
#include <cmath>
#include <memory>
#include <sstream>
#include <array>
#include <tuple>

// ── C++20 전용 헤더 (조건부 포함) ──
#if __cplusplus >= 202002L
    #include <concepts>
    #include <ranges>
    #include <span>
    #include <compare>
    #include <coroutine>
    // jthread는 일부 컴파일러에서 <thread>에 포함
    #if __has_include(<stop_token>)
        #include <thread>
        #include <stop_token>
        #define HAS_JTHREAD 1
    #else
        #define HAS_JTHREAD 0
    #endif
    #if __has_include(<source_location>)
        #include <source_location>
        #define HAS_SOURCE_LOCATION 1
    #else
        #define HAS_SOURCE_LOCATION 0
    #endif
    #define CPP20_AVAILABLE 1
#else
    #define CPP20_AVAILABLE 0
    #define HAS_JTHREAD 0
    #define HAS_SOURCE_LOCATION 0
#endif

// ── C++23 전용 헤더 ──
#if __cplusplus >= 202302L
    #if __has_include(<expected>)
        #include <expected>
        #define HAS_EXPECTED 1
    #else
        #define HAS_EXPECTED 0
    #endif
    #if __has_include(<stacktrace>)
        #include <stacktrace>
        #define HAS_STACKTRACE 1
    #else
        #define HAS_STACKTRACE 0
    #endif
#else
    #define HAS_EXPECTED 0
    #define HAS_STACKTRACE 0
#endif

using namespace std;

// ─── 전방 선언 ───
void lesson1_concepts();
void lesson2_ranges();
void lesson3_coroutines();
void lesson4_spaceship();
void lesson5_expected();
void lesson6_modules();
void lesson7_misc_features();

/*
=============================================================================
  레슨별 출력 흐름 가이드 (C++20 사용 가능 환경 기준)
=============================================================================
  lesson1 (Concepts):
    template<integral T> T add(T,T)
    add(1,2) = 3 (OK)
    add(1.5,2.5) → 컴파일 에러 (constraint 미충족)

  lesson2 (Ranges):
    auto evens = nums | views::filter(is_even) | views::transform(square);
    [1,2,3,4,5] → filter → [2,4] → transform → [4,16]

  lesson3 (Coroutines):
    co_yield로 lazy generator
    fibonacci_generator() → 0, 1, 1, 2, 3, 5, ...

  lesson4 (<=> 우주선 연산자):
    operator<=>(other) = default
    <, <=, >, >=, ==, != 모두 자동 생성

  lesson5 (expected, C++23):
    expected<int, string> result = parse_int("42");
    if (result) → *result = 42
    expected<int, string> err = parse_int("abc");
    if (!err) → err.error() = "invalid"

  lesson6 (Modules):
    import std; (전통 #include 대체)
    컴파일 시간 단축, 매크로 격리
    아직 컴파일러 지원 부분적

  lesson7 (기타):
    std::format("{} is {}", "x", 42) → "x is 42"
    std::span<int> 뷰 / jthread (auto join)
    constinit, consteval, designated initializers
=============================================================================
*/

int main() {
    cout << "========================================================\n";
    cout << "  C++ 26단계 : C++20/23 실전 코드\n";
    cout << "========================================================\n";
    cout << "  컴파일러 __cplusplus = " << __cplusplus << "\n";
    // > 출력 예: 컴파일러 __cplusplus = 202002 (C++20) 또는 201703 (C++17)
#if CPP20_AVAILABLE
    cout << "  ✓ C++20 기능 사용 가능\n";
#else
    cout << "  ✗ C++20 미지원 → C++17 대체 코드로 실행\n";
#endif
    cout << "\n";

    lesson1_concepts();
    lesson2_ranges();
    lesson3_coroutines();
    lesson4_spaceship();
    lesson5_expected();
    lesson6_modules();
    lesson7_misc_features();

    cout << "\n26단계 학습 완료! Modern C++의 세계에 오신 것을 환영합니다.\n";
    return 0;
}


// =========================================================================
//  레슨 1 — Concepts (C++20)
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────────┐
    │  Concepts = 템플릿 매개변수에 대한 "계약서"                        │
    │                                                                     │
    │  C++17 이전의 문제:                                                 │
    │    template<typename T>                                             │
    │    T add(T a, T b) { return a + b; }                               │
    │    // add("hello", "world") → 컴파일 에러! 하지만 에러 메시지가    │
    │    // 수백 줄의 암호 같은 내용...                                   │
    │                                                                     │
    │  C++20 Concepts:                                                    │
    │    template<typename T> requires std::integral<T>                   │
    │    T add(T a, T b) { return a + b; }                               │
    │    // add("hello", "world") → "T가 integral을 만족하지 않음"       │
    │    // 에러 메시지가 명확!                                           │
    │                                                                     │
    │  ┌──────────────────────────────────────────────────────────┐      │
    │  │  Concept 정의 방법:                                      │      │
    │  │                                                          │      │
    │  │  template<typename T>                                    │      │
    │  │  concept Addable = requires(T a, T b) {                  │      │
    │  │      { a + b } -> std::convertible_to<T>;  // a+b 가능  │      │
    │  │      { a - b } -> std::convertible_to<T>;  // a-b 가능  │      │
    │  │  };                                                      │      │
    │  └──────────────────────────────────────────────────────────┘      │
    │                                                                     │
    │  주요 표준 Concepts (<concepts> 헤더):                              │
    │  ┌────────────────────────┬──────────────────────────────┐         │
    │  │ concept                │ 의미                         │         │
    │  ├────────────────────────┼──────────────────────────────┤         │
    │  │ std::integral          │ 정수 타입 (int, long, ...)   │         │
    │  │ std::floating_point    │ 부동소수점 (float, double)   │         │
    │  │ std::signed_integral   │ 부호 있는 정수               │         │
    │  │ std::same_as<T, U>     │ T와 U가 같은 타입            │         │
    │  │ std::derived_from<D,B> │ D가 B의 파생 클래스          │         │
    │  │ std::convertible_to    │ 암시적 변환 가능             │         │
    │  │ std::regular           │ 복사+비교+기본생성 가능      │         │
    │  │ std::invocable         │ 호출 가능한 객체             │         │
    │  │ std::ranges::range     │ begin/end를 가진 범위        │         │
    │  └────────────────────────┴──────────────────────────────┘         │
    │                                                                     │
    │  4가지 사용 방법:                                                   │
    │                                                                     │
    │  // 방법 1: requires 절                                             │
    │  template<typename T> requires std::integral<T>                     │
    │  T func(T x);                                                       │
    │                                                                     │
    │  // 방법 2: 약식 (terse syntax)                                     │
    │  template<std::integral T>                                          │
    │  T func(T x);                                                       │
    │                                                                     │
    │  // 방법 3: auto + concept                                          │
    │  auto func(std::integral auto x);                                   │
    │                                                                     │
    │  // 방법 4: 후위 requires                                           │
    │  template<typename T>                                               │
    │  T func(T x) requires std::integral<T>;                             │
    └─────────────────────────────────────────────────────────────────────┘
*/

// ── C++17 호환 SFINAE 방식 (Concepts 없을 때) ──
// enable_if로 비슷한 효과를 낼 수 있지만 읽기 어려움
template<typename T,
         typename = enable_if_t<is_integral_v<T>>>
T safe_add_cpp17(T a, T b) {
    return a + b;
}

// ── C++17에서도 동작하는 타입 검사 유틸 ──
template<typename T>
struct has_size {
private:
    template<typename U>
    static auto test(int) -> decltype(declval<U>().size(), true_type{});
    template<typename>
    static false_type test(...);
public:
    static constexpr bool value = decltype(test<T>(0))::value;
};

#if CPP20_AVAILABLE
// ── Concept 정의 예제 (C++20) ──

// 기본 concept: 숫자 타입인지 확인
template<typename T>
concept Number = std::integral<T> || std::floating_point<T>;

// 복합 concept: 컨테이너처럼 동작하는지 확인
template<typename T>
concept Container = requires(T c) {
    { c.size() } -> std::convertible_to<size_t>;
    { c.begin() };
    { c.end() };
    typename T::value_type;        // 중첩 타입이 있어야 함
};

// requires 표현식으로 세밀한 제약 조건
template<typename T>
concept Printable = requires(T val, std::ostream& os) {
    { os << val } -> std::same_as<std::ostream&>;
};

// concept를 사용한 함수 오버로딩
template<Number T>
string describe_type(T val) {
    if constexpr (std::integral<T>)
        return "정수: " + to_string(val);
    else
        return "실수: " + to_string(val);
}

template<Container T>
string describe_type(const T& c) {
    return "컨테이너 (크기: " + to_string(c.size()) + ")";
}

#endif  // CPP20_AVAILABLE

void lesson1_concepts() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 1 : Concepts (C++20)           │\n";
    cout << "└──────────────────────────────────────┘\n\n";

#if CPP20_AVAILABLE
    // ── Concept 기반 함수 호출 ──
    cout << "  [C++20 Concepts 실행]\n";
    cout << "  " << describe_type(42) << "\n";
    cout << "  " << describe_type(3.14) << "\n";
    cout << "  " << describe_type(vector<int>{1,2,3}) << "\n";

    // describe_type("hello");  // 컴파일 에러! 명확한 에러 메시지

    // ── concept로 제약된 템플릿 ──
    auto max_of = []<Number T>(T a, T b) -> T {
        return (a > b) ? a : b;
    };
    cout << "  max_of(3, 7) = " << max_of(3, 7) << "\n";
    cout << "  max_of(1.5, 2.5) = " << max_of(1.5, 2.5) << "\n";

#else
    // ── C++17 대체 코드 ──
    cout << "  [C++17 모드: SFINAE로 대체]\n";
    cout << "  safe_add_cpp17(3, 5) = " << safe_add_cpp17(3, 5) << "\n";
    // safe_add_cpp17(3.14, 2.0);  // 컴파일 에러 (정수만 허용)

    cout << "  has_size<vector<int>> = "
         << (has_size<vector<int>>::value ? "true" : "false") << "\n";
    cout << "  has_size<int> = "
         << (has_size<int>::value ? "true" : "false") << "\n";

    cout << "\n  [Concepts C++17 vs C++20 비교]\n";
    cout << "  C++17 SFINAE:                        C++20 Concepts:\n";
    cout << "  template<typename T,                 template<std::integral T>\n";
    cout << "    enable_if_t<is_integral_v<T>>*>    T add(T a, T b) { ... }\n";
    cout << "  T add(T a, T b) { ... }\n";
    cout << "  → 에러 메시지 암호화               → 에러 메시지 명확\n";
#endif
    cout << "\n";
}


// =========================================================================
//  레슨 2 — Ranges (C++20)
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────────┐
    │  Ranges = 반복자(Iterator) 쌍을 하나로 묶은 추상화                 │
    │                                                                     │
    │  C++17 (반복자 쌍):                                                │
    │    sort(v.begin(), v.end());                                        │
    │    auto it = find(v.begin(), v.end(), 42);                         │
    │                                                                     │
    │  C++20 (Ranges):                                                    │
    │    ranges::sort(v);                                                 │
    │    auto it = ranges::find(v, 42);                                  │
    │                                                                     │
    │  파이프라인 (가장 강력한 기능!):                                   │
    │    auto result = numbers                                            │
    │        | views::filter([](int n){ return n % 2 == 0; })            │
    │        | views::transform([](int n){ return n * n; })              │
    │        | views::take(5);                                            │
    │                                                                     │
    │  ┌─────────────────────────────────────────────────────────┐       │
    │  │  파이프라인 데이터 흐름:                                 │       │
    │  │                                                         │       │
    │  │  [1,2,3,4,5,6,7,8,9,10]                                │       │
    │  │       │                                                 │       │
    │  │       ▼ filter(짝수)                                    │       │
    │  │  [2, 4, 6, 8, 10]                                      │       │
    │  │       │                                                 │       │
    │  │       ▼ transform(제곱)                                 │       │
    │  │  [4, 16, 36, 64, 100]                                  │       │
    │  │       │                                                 │       │
    │  │       ▼ take(3)                                         │       │
    │  │  [4, 16, 36]                                            │       │
    │  │                                                         │       │
    │  │  ★ 핵심: 지연 평가(Lazy Evaluation)!                   │       │
    │  │  → 실제로 원소를 요청할 때만 계산됨                    │       │
    │  │  → 중간 컨테이너 생성 없음 → 메모리/성능 절약         │       │
    │  └─────────────────────────────────────────────────────────┘       │
    │                                                                     │
    │  주요 Views:                                                        │
    │  ┌────────────────────────┬──────────────────────────────┐         │
    │  │ view                   │ 설명                         │         │
    │  ├────────────────────────┼──────────────────────────────┤         │
    │  │ views::filter(pred)    │ 조건에 맞는 원소만           │         │
    │  │ views::transform(fn)   │ 변환 적용                    │         │
    │  │ views::take(n)         │ 처음 n개만                   │         │
    │  │ views::drop(n)         │ 처음 n개 건너뛰기            │         │
    │  │ views::reverse         │ 역순                         │         │
    │  │ views::split(delim)    │ 분할                         │         │
    │  │ views::join            │ 중첩 범위 평탄화             │         │
    │  │ views::zip (C++23)     │ 여러 범위 병합               │         │
    │  │ views::enumerate(C++23)│ 인덱스+값 쌍                 │         │
    │  │ views::iota(start)     │ 무한 수열 생성               │         │
    │  └────────────────────────┴──────────────────────────────┘         │
    └─────────────────────────────────────────────────────────────────────┘
*/

void lesson2_ranges() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 2 : Ranges (C++20)             │\n";
    cout << "└──────────────────────────────────────┘\n\n";

#if CPP20_AVAILABLE
    namespace rv = std::views;

    // ── 기본 ranges 알고리즘 ──
    cout << "  [기본 Ranges 사용]\n";
    vector<int> nums = {5, 3, 1, 4, 2, 8, 7, 6, 9, 10};

    std::ranges::sort(nums);
    cout << "  정렬 후: ";
    for (int n : nums) cout << n << " ";
    cout << "\n";

    auto it = std::ranges::find(nums, 7);
    cout << "  7 찾음: " << (it != nums.end() ? "Yes" : "No") << "\n\n";

    // ── 파이프라인 연산 ──
    cout << "  [파이프라인: filter | transform | take]\n";
    vector<int> data = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};

    // 짝수만 → 제곱 → 처음 4개
    auto pipeline = data
        | rv::filter([](int n) { return n % 2 == 0; })
        | rv::transform([](int n) { return n * n; })
        | rv::take(4);

    cout << "  짝수의 제곱 (처음 4개): ";
    for (int val : pipeline) cout << val << " ";
    cout << "\n\n";

    // ── iota: 무한 수열 ──
    cout << "  [무한 수열 views::iota]\n";
    // 1부터 시작하는 무한 수열에서 3의 배수만, 처음 5개
    auto threes = rv::iota(1)
        | rv::filter([](int n) { return n % 3 == 0; })
        | rv::take(5);

    cout << "  3의 배수 (처음 5개): ";
    for (int val : threes) cout << val << " ";
    cout << "\n\n";

    // ── 문자열 처리 ──
    cout << "  [문자열에 ranges 적용]\n";
    string text = "Hello, C++20 Ranges World!";

    auto vowels = text | rv::filter([](char c) {
        return string("aeiouAEIOU").find(c) != string::npos;
    });

    cout << "  모음만: ";
    for (char c : vowels) cout << c;
    cout << "\n\n";

    // ── 복합 파이프라인 ──
    cout << "  [복합 예제: 학생 성적 처리]\n";
    struct Student { string name; int score; };
    vector<Student> students = {
        {"김철수", 85}, {"이영희", 92}, {"박민수", 68},
        {"정수진", 95}, {"최동현", 78}, {"한미래", 88}
    };

    // 80점 이상 학생의 이름 추출
    auto honor_scores = students
        | rv::filter([](const Student& s) { return s.score >= 80; })
        | rv::transform([](const Student& s) { return s.name + "(" + to_string(s.score) + ")"; });

    cout << "  80점 이상: ";
    for (const auto& name : honor_scores) cout << name << " ";
    cout << "\n";

#else
    // ── C++17 대체: STL 알고리즘 체이닝 ──
    cout << "  [C++17 모드: STL 알고리즘으로 대체]\n";
    vector<int> data = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};

    // C++17에서 같은 결과를 얻으려면:
    vector<int> even_nums;
    copy_if(data.begin(), data.end(), back_inserter(even_nums),
            [](int n) { return n % 2 == 0; });

    vector<int> squared;
    transform(even_nums.begin(), even_nums.end(), back_inserter(squared),
              [](int n) { return n * n; });

    // 처음 4개만
    if (squared.size() > 4) squared.resize(4);

    cout << "  짝수의 제곱 (처음 4개): ";
    for (int val : squared) cout << val << " ";
    cout << "\n";
    cout << "  → C++17에서는 중간 벡터가 필요하고 코드가 장황함\n";
    cout << "  → C++20 Ranges는 파이프라인으로 간결 + 지연 평가\n";

    cout << "\n  [Ranges vs STL 비교]\n";
    cout << "  ┌──────────────────────────────────────────────────────┐\n";
    cout << "  │ 기능        │ C++17 STL          │ C++20 Ranges     │\n";
    cout << "  ├─────────────┼────────────────────┼──────────────────┤\n";
    cout << "  │ 정렬        │ sort(v.begin(),    │ ranges::sort(v)  │\n";
    cout << "  │             │      v.end())      │                  │\n";
    cout << "  │ 필터        │ copy_if + 새 벡터  │ views::filter()  │\n";
    cout << "  │ 변환        │ transform + 새벡터 │ views::transform │\n";
    cout << "  │ 체이닝      │ 수동 (중간 저장)   │ | 파이프 연산    │\n";
    cout << "  │ 지연 평가   │ 불가능             │ 자동             │\n";
    cout << "  │ 무한 수열   │ 불가능             │ views::iota      │\n";
    cout << "  └──────────────────────────────────────────────────────┘\n";
#endif
    cout << "\n";
}


// =========================================================================
//  레슨 3 — Coroutines (C++20)
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────────┐
    │  Coroutines = 일시 중단(suspend) 가능한 함수                       │
    │                                                                     │
    │  일반 함수:                                                         │
    │    호출 ─────→ 실행 ─────→ 반환 (한 번에 끝)                      │
    │                                                                     │
    │  코루틴:                                                            │
    │    호출 ──→ 실행 ──→ 중단(co_yield) ──→ 재개 ──→ 중단 ──→ 종료  │
    │                                                                     │
    │  키워드:                                                            │
    │  ┌──────────────┬────────────────────────────────────────┐         │
    │  │ co_yield val  │ 값을 반환하고 중단 (제너레이터)       │         │
    │  │ co_return val │ 최종값 반환 후 종료                   │         │
    │  │ co_await expr │ 비동기 작업 대기 (중단 가능)          │         │
    │  └──────────────┴────────────────────────────────────────┘         │
    │                                                                     │
    │  사용 사례:                                                         │
    │  • 제너레이터: 피보나치, 무한 수열 등 (co_yield)                   │
    │  • 비동기 I/O: 네트워크, 파일 (co_await)                           │
    │  • 스트리밍: 대용량 데이터 처리                                    │
    │                                                                     │
    │  ┌──────────────────────────────────────────────────────────┐      │
    │  │  제너레이터 실행 흐름:                                    │      │
    │  │                                                          │      │
    │  │  Generator<int> fib() {        caller:                   │      │
    │  │      int a=0, b=1;             gen = fib();              │      │
    │  │      while (true) {            gen.next() → 값 0        │      │
    │  │          co_yield a; ←─────── gen.next() → 값 1         │      │
    │  │          tie(a,b) = {b,a+b};   gen.next() → 값 1        │      │
    │  │      }                         gen.next() → 값 2        │      │
    │  │  }                             ...                       │      │
    │  └──────────────────────────────────────────────────────────┘      │
    └─────────────────────────────────────────────────────────────────────┘
*/

#if CPP20_AVAILABLE
// ── 간단한 Generator 타입 구현 ──
// C++23에는 std::generator가 있지만, C++20에서는 직접 구현 필요
template<typename T>
struct Generator {
    struct promise_type {
        T current_value;
        auto get_return_object() {
            return Generator{
                std::coroutine_handle<promise_type>::from_promise(*this)
            };
        }
        auto initial_suspend() { return std::suspend_always{}; }
        auto final_suspend() noexcept { return std::suspend_always{}; }
        auto yield_value(T value) {
            current_value = value;
            return std::suspend_always{};
        }
        void return_void() {}
        void unhandled_exception() { std::terminate(); }
    };

    std::coroutine_handle<promise_type> handle;

    Generator(std::coroutine_handle<promise_type> h) : handle(h) {}
    ~Generator() { if (handle) handle.destroy(); }

    // 이동만 허용
    Generator(const Generator&) = delete;
    Generator(Generator&& other) noexcept : handle(other.handle) {
        other.handle = nullptr;
    }

    bool next() {
        handle.resume();
        return !handle.done();
    }

    T value() const { return handle.promise().current_value; }
};

// ── 피보나치 제너레이터 ──
Generator<long long> fibonacci() {
    long long a = 0, b = 1;
    while (true) {
        co_yield a;
        auto temp = a;
        a = b;
        b = temp + b;
    }
}

// ── 범위 제너레이터 ──
Generator<int> range_gen(int start, int end, int step = 1) {
    for (int i = start; i < end; i += step) {
        co_yield i;
    }
}

#endif  // CPP20_AVAILABLE

void lesson3_coroutines() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 3 : Coroutines (C++20)         │\n";
    cout << "└──────────────────────────────────────┘\n\n";

#if CPP20_AVAILABLE
    // ── 피보나치 제너레이터 사용 ──
    cout << "  [피보나치 제너레이터 co_yield]\n";
    auto fib = fibonacci();
    cout << "  피보나치 처음 10개: ";
    for (int i = 0; i < 10 && fib.next(); ++i) {
        cout << fib.value() << " ";
    }
    cout << "\n\n";

    // ── 범위 제너레이터 ──
    cout << "  [범위 제너레이터]\n";
    auto rng = range_gen(0, 20, 3);
    cout << "  0부터 20 미만, 3씩: ";
    while (rng.next()) {
        cout << rng.value() << " ";
    }
    cout << "\n";

#else
    // ── C++17 대체: 반복자 기반 제너레이터 ──
    cout << "  [C++17 모드: 클래스 기반 제너레이터로 대체]\n\n";

    // 코루틴 없이 제너레이터 패턴 구현
    class FibonacciGenerator {
        long long a_ = 0, b_ = 1;
        bool started_ = false;
    public:
        bool next() {
            if (!started_) { started_ = true; return true; }
            auto temp = a_;
            a_ = b_;
            b_ = temp + b_;
            return true;
        }
        long long value() const { return a_; }
    };

    FibonacciGenerator fib;
    cout << "  피보나치 처음 10개: ";
    for (int i = 0; i < 10 && fib.next(); ++i) {
        cout << fib.value() << " ";
    }
    cout << "\n\n";

    cout << "  [코루틴 vs 클래스 제너레이터 비교]\n";
    cout << "  ┌────────────────────┬──────────────────────────────────┐\n";
    cout << "  │ 코루틴(C++20)      │ 클래스(C++17)                    │\n";
    cout << "  ├────────────────────┼──────────────────────────────────┤\n";
    cout << "  │ co_yield로 간결    │ 상태를 멤버변수로 수동 관리      │\n";
    cout << "  │ 로컬 변수 자동 유지│ 모든 상태를 명시적 저장 필요     │\n";
    cout << "  │ 중첩 루프도 쉬움   │ 복잡한 상태 머신 필요            │\n";
    cout << "  │ 비동기 I/O 지원    │ 콜백/future 필요                 │\n";
    cout << "  └────────────────────┴──────────────────────────────────┘\n";
#endif
    cout << "\n";
}


// =========================================================================
//  레슨 4 — Three-way Comparison (<=>)  우주선 연산자
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────────┐
    │  <=> (우주선 연산자, spaceship operator)                            │
    │                                                                     │
    │  C++17: 6개 연산자를 모두 정의해야 함                              │
    │    ==, !=, <, <=, >, >=                                             │
    │                                                                     │
    │  C++20: <=>  하나로 6개 모두 자동 생성!                            │
    │                                                                     │
    │  반환 타입:                                                         │
    │  ┌────────────────────────┬─────────────────────────────────┐      │
    │  │ 반환 타입              │ 의미                            │      │
    │  ├────────────────────────┼─────────────────────────────────┤      │
    │  │ strong_ordering        │ 완전한 순서 (a==b이면 동일)     │      │
    │  │                        │ int, string, 대부분의 타입      │      │
    │  │ weak_ordering          │ 동등하지만 동일하지 않을 수 있음│      │
    │  │                        │ 대소문자 무시 비교 등           │      │
    │  │ partial_ordering       │ 비교 불가능한 경우 존재         │      │
    │  │                        │ float (NaN != NaN)              │      │
    │  └────────────────────────┴─────────────────────────────────┘      │
    │                                                                     │
    │  // C++20:                                                          │
    │  struct Point {                                                     │
    │      int x, y;                                                      │
    │      auto operator<=>(const Point&) const = default;               │
    │      // → ==, !=, <, <=, >, >= 모두 자동 생성!                     │
    │  };                                                                 │
    └─────────────────────────────────────────────────────────────────────┘
*/

// ── C++17 호환 방식 ──
struct VersionCpp17 {
    int major, minor, patch;

    // C++17: 6개 연산자를 수동 정의 (지루하고 에러 발생 가능!)
    bool operator==(const VersionCpp17& o) const {
        return tie(major, minor, patch) == tie(o.major, o.minor, o.patch);
    }
    bool operator!=(const VersionCpp17& o) const { return !(*this == o); }
    bool operator<(const VersionCpp17& o) const {
        return tie(major, minor, patch) < tie(o.major, o.minor, o.patch);
    }
    bool operator<=(const VersionCpp17& o) const { return !(o < *this); }
    bool operator>(const VersionCpp17& o) const { return o < *this; }
    bool operator>=(const VersionCpp17& o) const { return !(*this < o); }
};

#if CPP20_AVAILABLE
// ── C++20 방식: 우주선 연산자 ──
struct VersionCpp20 {
    int major, minor, patch;

    // 이 한 줄로 6개 비교 연산자 모두 자동 생성!
    auto operator<=>(const VersionCpp20&) const = default;
};

// ── 커스텀 비교 순서 ──
struct CaseInsensitiveString {
    string value;

    // 대소문자 무시 비교 → weak_ordering (동등하지만 동일하지 않음)
    std::weak_ordering operator<=>(const CaseInsensitiveString& other) const {
        string a = value, b = other.value;
        transform(a.begin(), a.end(), a.begin(), ::tolower);
        transform(b.begin(), b.end(), b.begin(), ::tolower);
        if (a < b) return std::weak_ordering::less;
        if (a > b) return std::weak_ordering::greater;
        return std::weak_ordering::equivalent;
    }

    bool operator==(const CaseInsensitiveString& other) const {
        return (*this <=> other) == 0;
    }
};
#endif

void lesson4_spaceship() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 4 : Three-way Comparison (<=>)│\n";
    cout << "└──────────────────────────────────────┘\n\n";

    // ── C++17 방식 ──
    cout << "  [C++17: 수동 비교 연산자]\n";
    VersionCpp17 v1{1, 2, 3}, v2{1, 3, 0};
    cout << "  v1(1.2.3) < v2(1.3.0) = " << (v1 < v2 ? "true" : "false") << "\n";
    cout << "  v1 == v1 = " << (v1 == v1 ? "true" : "false") << "\n";

#if CPP20_AVAILABLE
    // ── C++20 방식 ──
    cout << "\n  [C++20: 우주선 연산자 (= default)]\n";
    VersionCpp20 v3{1, 2, 3}, v4{1, 3, 0};
    cout << "  v3(1.2.3) < v4(1.3.0) = " << (v3 < v4 ? "true" : "false") << "\n";
    cout << "  v3 == v3 = " << (v3 == v3 ? "true" : "false") << "\n";

    // 우주선 연산자 직접 사용
    auto result = v3 <=> v4;
    if (result < 0) cout << "  v3 <=> v4: v3이 작음\n";
    else if (result > 0) cout << "  v3 <=> v4: v3이 큼\n";
    else cout << "  v3 <=> v4: 동일\n";

    // 대소문자 무시 비교
    cout << "\n  [커스텀 weak_ordering: 대소문자 무시]\n";
    CaseInsensitiveString s1{"Hello"}, s2{"hello"}, s3{"World"};
    cout << "  \"Hello\" == \"hello\" : " << (s1 == s2 ? "true" : "false") << "\n";
    cout << "  \"Hello\" < \"World\"  : " << (s1 < s3 ? "true" : "false") << "\n";
#else
    cout << "\n  [C++17 모드: tie()를 활용한 비교]\n";
    cout << "  → tie()로 멤버별 비교를 간결하게 작성 가능\n";
    cout << "  → 하지만 여전히 6개 연산자를 개별 정의해야 함\n";
    cout << "  → C++20 <=> = default;  한 줄이면 끝!\n";
#endif
    cout << "\n";
}


// =========================================================================
//  레슨 5 — std::expected (C++23)
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────────┐
    │  에러 처리 패러다임 비교                                            │
    │                                                                     │
    │  ┌──────────────────┬────────────────────┬───────────────────────┐ │
    │  │ 방법             │ 장점               │ 단점                  │ │
    │  ├──────────────────┼────────────────────┼───────────────────────┤ │
    │  │ 에러코드 반환    │ 간단               │ 값과 에러 분리 어려움 │ │
    │  │ 예외(exception)  │ 깨끗한 정상 경로   │ 성능 비용, 예측 어려움│ │
    │  │ std::optional    │ 값 없음 표현       │ 에러 원인 모름        │ │
    │  │ std::expected    │ 값 또는 에러 정보  │ C++23 필요 ★         │ │
    │  └──────────────────┴────────────────────┴───────────────────────┘ │
    │                                                                     │
    │  expected<T, E>:                                                    │
    │    성공 시: T 값을 보유                                            │
    │    실패 시: E 에러를 보유                                          │
    │                                                                     │
    │  ┌──────────────────────────────────────────────────────┐          │
    │  │  expected<int, string> divide(int a, int b) {       │          │
    │  │      if (b == 0)                                     │          │
    │  │          return unexpected("0으로 나눌 수 없음");    │          │
    │  │      return a / b;  // 성공                          │          │
    │  │  }                                                   │          │
    │  │                                                      │          │
    │  │  auto result = divide(10, 0);                        │          │
    │  │  if (result)  // 또는 result.has_value()              │          │
    │  │      cout << result.value();                         │          │
    │  │  else                                                │          │
    │  │      cout << result.error();                         │          │
    │  └──────────────────────────────────────────────────────┘          │
    └─────────────────────────────────────────────────────────────────────┘
*/

// ── C++17에서 expected를 흉내 내는 간단한 구현 ──
// (실제 std::expected의 부분집합만 구현)
template<typename T, typename E>
class SimpleExpected {
    bool has_val_;
    union {
        T value_;
        E error_;
    };
public:
    // 성공 생성자
    SimpleExpected(const T& val) : has_val_(true), value_(val) {}
    // 에러를 구분하기 위한 태그 타입
    struct unexpected_tag {};
    SimpleExpected(unexpected_tag, const E& err) : has_val_(false), error_(err) {}

    ~SimpleExpected() {
        if (has_val_) value_.~T();
        else error_.~E();
    }

    bool has_value() const { return has_val_; }
    explicit operator bool() const { return has_val_; }

    const T& value() const { return value_; }
    const E& error() const { return error_; }
};

// unexpected 헬퍼
template<typename E>
auto make_unexpected(const E& err) {
    // 이 함수는 SimpleExpected의 에러 생성에 사용
    return err;
}

// ── 에러 처리 예제 ──
enum class ParseError {
    EmptyInput,
    InvalidFormat,
    OutOfRange
};

string to_string(ParseError e) {
    switch (e) {
        case ParseError::EmptyInput:    return "빈 입력";
        case ParseError::InvalidFormat: return "잘못된 형식";
        case ParseError::OutOfRange:    return "범위 초과";
    }
    return "알 수 없는 에러";
}

// C++17 호환 에러 처리 함수
SimpleExpected<int, ParseError> parse_int(const string& s) {
    if (s.empty())
        return {SimpleExpected<int, ParseError>::unexpected_tag{},
                ParseError::EmptyInput};

    try {
        size_t pos;
        long val = stol(s, &pos);
        if (pos != s.size())
            return {SimpleExpected<int, ParseError>::unexpected_tag{},
                    ParseError::InvalidFormat};
        if (val > INT_MAX || val < INT_MIN)
            return {SimpleExpected<int, ParseError>::unexpected_tag{},
                    ParseError::OutOfRange};
        return static_cast<int>(val);
    } catch (...) {
        return {SimpleExpected<int, ParseError>::unexpected_tag{},
                ParseError::InvalidFormat};
    }
}

void lesson5_expected() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 5 : std::expected (C++23)      │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    // ── expected 사용 데모 ──
    cout << "  [에러 처리 예제: 정수 파싱]\n";

    auto test_parse = [](const string& input) {
        auto result = parse_int(input);
        if (result) {
            cout << "  \"" << input << "\" → 성공: " << result.value() << "\n";
        } else {
            cout << "  \"" << input << "\" → 에러: "
                 << to_string(result.error()) << "\n";
        }
    };

    test_parse("42");
    test_parse("");
    test_parse("12abc");
    test_parse("999999999999999999");

#if HAS_EXPECTED
    cout << "\n  [std::expected (C++23) 네이티브 사용]\n";

    auto divide = [](double a, double b)
        -> std::expected<double, string> {
        if (b == 0.0)
            return std::unexpected("0으로 나눌 수 없습니다");
        return a / b;
    };

    auto r1 = divide(10.0, 3.0);
    auto r2 = divide(10.0, 0.0);

    cout << "  10/3 = " << (r1 ? to_string(r1.value()) : r1.error()) << "\n";
    cout << "  10/0 = " << (r2 ? to_string(r2.value()) : r2.error()) << "\n";

    // ── 체이닝 (monadic operations) ──
    // and_then: 성공 시 다음 함수 호출
    // or_else:  실패 시 대체 함수 호출
    // transform: 성공 값 변환
    cout << "\n  [체이닝: and_then, transform]\n";
    auto result = divide(100.0, 4.0)
        .transform([](double v) { return v * 2; })         // 50
        .transform([](double v) { return to_string(v); }); // "50.0"

    if (result)
        cout << "  100/4 * 2 = " << result.value() << "\n";
#else
    cout << "\n  [std::expected는 C++23에서 사용 가능]\n";
    cout << "  → optional과의 차이: 에러의 원인을 알 수 있음\n";
    cout << "  → 예외를 사용하지 않고도 풍부한 에러 정보 전달\n";
    cout << "  → 함수형 체이닝(and_then, transform) 지원\n";
#endif

    cout << "\n  [에러 처리 방법 선택 가이드]\n";
    cout << "  • 단순한 값 부재: std::optional\n";
    cout << "  • 에러 원인 필요 + 성능 중요: std::expected (C++23)\n";
    cout << "  • 복구 불가 오류: 예외(exception)\n";
    cout << "  • 임베디드/게임: 에러코드 또는 expected\n\n";
}


// =========================================================================
//  레슨 6 — Modules (C++20)
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────────┐
    │  Modules = #include를 대체하는 새로운 코드 구성 방법               │
    │                                                                     │
    │  ┌───────────────────────────────────────────────────────────────┐ │
    │  │  #include의 문제점:                                           │ │
    │  │  1. 텍스트 붙여넣기 → 같은 헤더를 수천 번 파싱               │ │
    │  │  2. 매크로 오염: #define이 다른 파일에 영향                    │ │
    │  │  3. 포함 순서에 따라 결과가 달라질 수 있음                    │ │
    │  │  4. 대규모 프로젝트에서 컴파일 시간 폭발                      │ │
    │  │                                                               │ │
    │  │  Modules의 장점:                                              │ │
    │  │  1. 한 번만 컴파일 → BMI(Binary Module Interface) 생성       │ │
    │  │  2. 매크로 격리: 모듈 안의 #define이 밖에 안 나감            │ │
    │  │  3. import 순서 무관                                          │ │
    │  │  4. 컴파일 속도 대폭 향상 (2~10배)                           │ │
    │  └───────────────────────────────────────────────────────────────┘ │
    │                                                                     │
    │  ─── 기본 문법 ───                                                 │
    │                                                                     │
    │  // math_lib.cppm (모듈 인터페이스 파일)                           │
    │  export module math_lib;       // 모듈 이름 선언                   │
    │                                                                     │
    │  export int add(int a, int b) {   // export = 외부 공개           │
    │      return a + b;                                                  │
    │  }                                                                  │
    │                                                                     │
    │  int internal_helper() {          // export 없음 = 내부용         │
    │      return 42;                                                     │
    │  }                                                                  │
    │                                                                     │
    │  // main.cpp (사용하는 쪽)                                         │
    │  import math_lib;              // #include 대신 import!            │
    │  cout << add(1, 2);            // OK                                │
    │  cout << internal_helper();    // 에러! 비공개 함수                │
    │                                                                     │
    │  ─── 서브모듈 ───                                                  │
    │                                                                     │
    │  // math_lib-vector.cppm (서브모듈)                                │
    │  export module math_lib:vector;                                     │
    │  export struct Vec3 { float x, y, z; };                            │
    │                                                                     │
    │  // math_lib.cppm (메인 모듈에서 서브모듈 재공개)                  │
    │  export module math_lib;                                            │
    │  export import :vector;                                             │
    │                                                                     │
    │  ─── 빌드 시스템 지원 현황 ───                                    │
    │  ┌──────────────┬────────────────────────────────────────┐         │
    │  │ 빌드 시스템   │ 모듈 지원 현황                        │         │
    │  ├──────────────┼────────────────────────────────────────┤         │
    │  │ CMake 3.28+  │ import std; 지원 (실험적)             │         │
    │  │ MSVC (VS2022)│ 가장 완성도 높음                       │         │
    │  │ GCC 14+      │ 기본 지원                              │         │
    │  │ Clang 17+    │ 진행 중                                │         │
    │  └──────────────┴────────────────────────────────────────┘         │
    └─────────────────────────────────────────────────────────────────────┘
*/

void lesson6_modules() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 6 : Modules (C++20)            │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    // Modules는 단일 파일에서 데모할 수 없으므로 개념 설명과
    // 사용 예시를 코드 주석 + 출력으로 제공

    cout << "  [Modules는 다중 파일 기능이므로 여기서는 가이드만 제공]\n\n";

    cout << "  ┌──────────────────────────────────────────────────────┐\n";
    cout << "  │  #include vs import 비교                             │\n";
    cout << "  ├──────────────────┬───────────────────────────────────┤\n";
    cout << "  │ 특성             │ #include          │ import       │\n";
    cout << "  ├──────────────────┼───────────────────┼──────────────┤\n";
    cout << "  │ 동작 방식        │ 텍스트 복붙       │ 컴파일된 인터│\n";
    cout << "  │                  │                   │ 페이스 로드  │\n";
    cout << "  │ 매크로 격리      │ 없음 (오염)       │ 있음 (격리)  │\n";
    cout << "  │ 순서 의존성      │ 있음              │ 없음         │\n";
    cout << "  │ 컴파일 속도      │ 느림 (매번 파싱)  │ 빠름 (1회)   │\n";
    cout << "  │ 접근 제어        │ 없음              │ export 키워드│\n";
    cout << "  │ ODR 위반 위험    │ 높음              │ 낮음         │\n";
    cout << "  └──────────────────┴───────────────────┴──────────────┘\n\n";

    cout << "  [모듈 파일 작성 예시]\n\n";

    cout << "  // ── 파일: math.cppm ──\n";
    cout << "  export module math;                      // 모듈 선언\n";
    cout << "  \n";
    cout << "  export namespace math {                   // 공개 API\n";
    cout << "      double sqrt(double x);               \n";
    cout << "      double pow(double base, double exp); \n";
    cout << "  }                                        \n";
    cout << "  \n";
    cout << "  // 내부 구현 (export 없음 = 비공개)      \n";
    cout << "  double approx_sqrt(double x, int iter);  \n\n";

    cout << "  // ── 파일: main.cpp ──\n";
    cout << "  import math;                              // import!\n";
    cout << "  import <iostream>;                        // 표준 헤더도 가능\n";
    cout << "  // import std;                            // C++23: 전체 표준라이브러리!\n";
    cout << "  \n";
    cout << "  int main() {\n";
    cout << "      std::cout << math::sqrt(2.0);        \n";
    cout << "  }\n\n";

    cout << "  [컴파일 방법 (GCC)]\n";
    cout << "  g++ -std=c++20 -fmodules-ts -c math.cppm  # BMI 생성\n";
    cout << "  g++ -std=c++20 -fmodules-ts main.cpp math.o -o app\n\n";

    cout << "  [실전 팁]\n";
    cout << "  • 새 프로젝트에서는 Modules 사용을 고려할 것\n";
    cout << "  • 기존 프로젝트: 점진적 마이그레이션 (헤더 래퍼 모듈)\n";
    cout << "  • MSVC(Visual Studio)가 현재 가장 완성도 높음\n";
    cout << "  • CMake 3.28+ CXX_MODULES 지원 활용\n\n";
}


// =========================================================================
//  레슨 7 — 기타 유용한 기능
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────────┐
    │  C++20/23에서 추가된 편리한 기능들                                  │
    │                                                                     │
    │  ┌──────────────────────┬──────┬────────────────────────────────┐  │
    │  │ 기능                 │ 버전 │ 설명                           │  │
    │  ├──────────────────────┼──────┼────────────────────────────────┤  │
    │  │ std::span            │ C++20│ 배열/벡터의 안전한 뷰         │  │
    │  │ std::jthread         │ C++20│ 자동 join하는 thread          │  │
    │  │ std::source_location │ C++20│ __FILE__, __LINE__ 대체       │  │
    │  │ std::stacktrace      │ C++23│ 런타임 스택 트레이스          │  │
    │  │ std::format          │ C++20│ Python 스타일 포맷팅          │  │
    │  │ consteval            │ C++20│ 반드시 컴파일 타임 실행       │  │
    │  │ constinit            │ C++20│ 컴파일 타임 초기화 보장       │  │
    │  │ [[likely]]/unlikely  │ C++20│ 분기 예측 힌트                │  │
    │  │ designated init      │ C++20│ 구조체 지정 초기화            │  │
    │  │ using enum           │ C++20│ enum 멤버를 스코프 없이 사용  │  │
    │  └──────────────────────┴──────┴────────────────────────────────┘  │
    └─────────────────────────────────────────────────────────────────────┘
*/

// ── std::span 대체 (C++17 호환) ──
// span은 배열/벡터의 "뷰"로, 복사 없이 참조만 제공
// 개념적으로 (T* data, size_t size) 쌍과 동일
template<typename T>
class SimpleSpan {
    T* data_;
    size_t size_;
public:
    SimpleSpan(T* data, size_t size) : data_(data), size_(size) {}
    SimpleSpan(vector<T>& v) : data_(v.data()), size_(v.size()) {}

    T& operator[](size_t i) { return data_[i]; }
    const T& operator[](size_t i) const { return data_[i]; }
    size_t size() const { return size_; }
    T* begin() { return data_; }
    T* end() { return data_ + size_; }

    // 부분 span (subspan)
    SimpleSpan<T> subspan(size_t offset, size_t count) {
        return {data_ + offset, count};
    }
};

// span을 받는 함수: vector, 배열, C 배열 모두 받을 수 있음!
double average(SimpleSpan<const int> data) {
    double sum = 0;
    for (size_t i = 0; i < data.size(); ++i) sum += data[i];
    return data.size() > 0 ? sum / data.size() : 0;
}

void lesson7_misc_features() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 7 : 기타 유용한 기능           │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    // ══════════════════════════════════════════════
    //  std::span (C++20)
    // ══════════════════════════════════════════════
    cout << "  [1] std::span - 배열/벡터의 안전한 뷰\n";

#if CPP20_AVAILABLE
    // ── C++20 네이티브 span ──
    vector<int> vec = {10, 20, 30, 40, 50};
    span<int> s(vec);

    cout << "  span 크기: " << s.size() << "\n";
    cout << "  첫 3개: ";
    for (int x : s.first(3)) cout << x << " ";
    cout << "\n";

    // 함수에 전달: vector, array, C배열 모두 가능
    auto print_span = [](span<const int> data) {
        for (int x : data) cout << x << " ";
        cout << "\n";
    };

    int c_arr[] = {1, 2, 3};
    array<int, 4> std_arr = {4, 5, 6, 7};

    cout << "  C 배열 span: "; print_span(c_arr);
    cout << "  std::array span: "; print_span(std_arr);
    cout << "  vector span: "; print_span(vec);
#else
    // C++17 대체
    vector<int> vec = {10, 20, 30, 40, 50};
    SimpleSpan<int> s(vec);
    cout << "  SimpleSpan 크기: " << s.size() << "\n";
    cout << "  부분 span (1~3): ";
    auto sub = s.subspan(1, 3);
    for (size_t i = 0; i < sub.size(); ++i) cout << sub[i] << " ";
    cout << "\n";

    cout << "  → std::span은 포인터+크기로 어떤 연속 메모리든 참조 가능\n";
    cout << "  → const span으로 읽기 전용 뷰 제공 (string_view의 일반화)\n";
#endif
    cout << "\n";

    // ══════════════════════════════════════════════
    //  std::jthread (C++20)
    // ══════════════════════════════════════════════
    cout << "  [2] std::jthread - 자동 join + 취소 가능 스레드\n";

    //  ┌─────────────────────────────────────────────────────────┐
    //  │  std::thread의 문제:                                     │
    //  │  • join()을 안 하면 프로그램 종료 시 terminate()         │
    //  │  • 예외 발생 시 join() 호출 누락 가능                   │
    //  │  • 외부에서 스레드 중지 요청 불가                       │
    //  │                                                         │
    //  │  std::jthread의 해결:                                    │
    //  │  • 소멸자에서 자동 join()                               │
    //  │  • stop_token으로 협력적 취소(cancellation)             │
    //  │  • request_stop() → 스레드 내에서 확인 가능             │
    //  └─────────────────────────────────────────────────────────┘

#if HAS_JTHREAD && CPP20_AVAILABLE
    {
        auto worker = [](std::stop_token stoken, int id) {
            int count = 0;
            while (!stoken.stop_requested() && count < 5) {
                cout << "    스레드 " << id << ": 작업 " << count << "\n";
                ++count;
            }
            cout << "    스레드 " << id << ": 종료\n";
        };

        std::jthread t1(worker, 1);
        // 소멸자에서 자동 join → join() 호출 필요 없음!
        // t1.request_stop()으로 중지 요청 가능
    }
#else
    cout << "  [C++17 모드: thread + RAII 래퍼로 대체]\n";
    cout << "  → C++17에서는 thread를 RAII로 감싸거나\n";
    cout << "    atomic<bool>로 취소 플래그를 수동 관리해야 함\n";
    cout << "  → jthread는 이를 자동화: 소멸자 join + stop_token\n";
#endif
    cout << "\n";

    // ══════════════════════════════════════════════
    //  std::source_location (C++20)
    // ══════════════════════════════════════════════
    cout << "  [3] std::source_location - 향상된 디버그 정보\n";

    //  __FILE__, __LINE__은 매크로 → 인라인 함수에서 호출자 위치 못 잡음
    //  source_location은 함수 매개변수 기본값으로 사용 가능!

#if HAS_SOURCE_LOCATION && CPP20_AVAILABLE
    auto log_msg = [](const string& msg,
                      const std::source_location& loc
                          = std::source_location::current()) {
        cout << "    [" << loc.file_name() << ":"
             << loc.line() << " " << loc.function_name()
             << "] " << msg << "\n";
    };

    log_msg("source_location 테스트");
#else
    cout << "  [C++17 모드: __FILE__, __LINE__ 매크로 사용]\n";

    // C++17 방식: 매크로로 대체
    #define LOG_MSG(msg) \
        cout << "    [" << __FILE__ << ":" << __LINE__ \
             << "] " << msg << "\n"

    LOG_MSG("매크로 기반 로깅");
    cout << "  → 매크로는 인라인 함수 내부에서 호출자 위치를 못 잡음\n";
    cout << "  → source_location은 함수 매개변수 기본값으로 자동 전달\n";
#endif
    cout << "\n";

    // ══════════════════════════════════════════════
    //  std::stacktrace (C++23)
    // ══════════════════════════════════════════════
    cout << "  [4] std::stacktrace (C++23) - 런타임 스택 추적\n";

#if HAS_STACKTRACE
    cout << "  현재 스택 트레이스:\n";
    cout << std::stacktrace::current() << "\n";
#else
    cout << "  [C++23 기능 - 사용 불가 시 플랫폼별 대안 사용]\n";
    cout << "  • Linux: backtrace() + backtrace_symbols()\n";
    cout << "  • Windows: CaptureStackBackTrace()\n";
    cout << "  • 크로스플랫폼: boost::stacktrace\n";
#endif
    cout << "\n";

    // ══════════════════════════════════════════════
    //  C++20 소소한 편의 기능들
    // ══════════════════════════════════════════════
    cout << "  [5] C++20 소소하지만 유용한 기능들\n\n";

    // ── 지정 초기화 (Designated Initializers) ──
    //  C++20에서 공식 지원 (C에서 가져옴)
    struct Config {
        int width = 800;
        int height = 600;
        bool fullscreen = false;
        string title = "My App";
    };

    // C++20:
    // Config cfg = {.width = 1920, .height = 1080, .fullscreen = true};
    // C++17에서도 이렇게 가능:
    Config cfg;
    cfg.width = 1920;
    cfg.height = 1080;
    cfg.fullscreen = true;
    cout << "  Config: " << cfg.width << "x" << cfg.height
         << (cfg.fullscreen ? " 전체화면" : " 창모드") << "\n";

    // ── [[likely]] / [[unlikely]] 분기 힌트 ──
    cout << "\n  [[likely]]/[[unlikely]] (C++20):\n";
    cout << "  if (error_code == 0) [[likely]] {     // 보통 성공\n";
    cout << "      process();\n";
    cout << "  } else [[unlikely]] {                 // 에러는 드묾\n";
    cout << "      handle_error();\n";
    cout << "  }\n";
    cout << "  → 컴파일러에 분기 예측 힌트를 제공\n";

    // ── using enum (C++20) ──
    cout << "\n  using enum (C++20):\n";
    enum class Color { Red, Green, Blue };
    // C++20: using enum Color; 후 Red로 바로 사용 가능
    // C++17: Color::Red 로 써야 함
    cout << "  C++17: Color::Red = " << static_cast<int>(Color::Red) << "\n";
    cout << "  C++20: using enum Color; 후 Red로 바로 사용 가능\n";

    cout << "\n";

    // ──────────────────────────────────────────────────────────────
    //  ★ 종합 연습문제 ★
    // ──────────────────────────────────────────────────────────────
    cout << "  ╔═══════════════════════════════════════════════════════════╗\n";
    cout << "  ║  ★ 종합 연습문제                                         ║\n";
    cout << "  ╠═══════════════════════════════════════════════════════════╣\n";
    cout << "  ║  1. (Concepts) Iterable concept를 정의하라:              ║\n";
    cout << "  ║     begin()과 end()를 가진 타입만 허용.                  ║\n";
    cout << "  ║     이를 사용하는 print_all() 함수를 작성하라.           ║\n";
    cout << "  ║                                                           ║\n";
    cout << "  ║  2. (Ranges) 문자열 벡터에서 5글자 이상인 것만           ║\n";
    cout << "  ║     대문자로 변환하여 출력하는 파이프라인을 만들어라.    ║\n";
    cout << "  ║     (C++17: 알고리즘 체이닝으로 대체)                    ║\n";
    cout << "  ║                                                           ║\n";
    cout << "  ║  3. (Coroutines) 소수(prime)를 무한히 생성하는           ║\n";
    cout << "  ║     제너레이터를 구현하라.                               ║\n";
    cout << "  ║     (C++17: 클래스 기반 상태 머신으로 구현)              ║\n";
    cout << "  ║                                                           ║\n";
    cout << "  ║  4. (<=>)  Rectangle 클래스에 면적 기준 비교를            ║\n";
    cout << "  ║     우주선 연산자로 구현하라.                             ║\n";
    cout << "  ║                                                           ║\n";
    cout << "  ║  5. (expected) 파일 경로를 받아 내용을 읽는 함수를       ║\n";
    cout << "  ║     expected<string, FileError>로 구현하라.              ║\n";
    cout << "  ║     FileError에는 NotFound, PermissionDenied, TooLarge  ║\n";
    cout << "  ║     를 포함할 것.                                        ║\n";
    cout << "  ║                                                           ║\n";
    cout << "  ║  6. (span) 정수 배열의 이동 평균(moving average)을       ║\n";
    cout << "  ║     span으로 구현하라 (window 크기는 매개변수).          ║\n";
    cout << "  ╚═══════════════════════════════════════════════════════════╝\n\n";
}
