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

void lesson0_auto_type_deduction();   // C++11 auto / decltype 기초 (먼저 학습)
void lesson1_cpp17_basics();
void lesson2_optional_variant();
void lesson3_structured_bindings();
void lesson4_constexpr_if();
void lesson5_cpp20_preview();

int main() {
    cout << "========================================\n";
    cout << "  C++ 10단계 : 모던 C++\n";
    cout << "========================================\n\n";

    lesson0_auto_type_deduction();
    lesson1_cpp17_basics();
    lesson2_optional_variant();
    lesson3_structured_bindings();
    lesson4_constexpr_if();
    lesson5_cpp20_preview();

    cout << "\n10단계 학습 완료!\n";
    return 0;
}


// =====================================================================
//  레슨 0 — auto 타입 추론 (C++11~20 종합)
// =====================================================================
//  [학습 목표]
//   1. auto가 어떤 규칙으로 타입을 정하는지 이해
//   2. auto / auto& / const auto& / auto&& 차이 정확히 구분
//   3. decltype / decltype(auto) 의 미묘한 차이
//   4. 함수 반환 타입 추론, 람다, 템플릿 매개변수에서의 auto
//   5. 함정: 참조/const 떨어짐, 배열/함수 decay, 초기화자 리스트, proxy 객체
//   6. CTAD (Class Template Argument Deduction, C++17)
//   7. 메모리 관점: 의도치 않은 복사 / 참조 / 임시 객체 수명
// =====================================================================

// 헬퍼: 컴파일 시 타입 출력 (정적 어서트로 검증)
template<typename T> struct TypeInspector;   // 일부러 정의 안 함
// 사용법: TypeInspector<decltype(x)> _;     // 컴파일 에러 메시지에 타입 노출

void lesson0_auto_type_deduction() {
    cout << "[레슨 0] auto 타입 추론 — 정확하게 이해하기\n\n";

    // ─────────────────────────────────────────────────────────────────
    //  1. auto의 기본 추론 규칙 (= 템플릿 매개변수 추론과 동일)
    //
    //  template<typename T> void f(T x);     int i;  f(i);  → T = int
    //  auto x = i;                                          → x : int
    //
    //  핵심: auto는 "표현식의 값 타입"을 가져옴.
    //        ★ 참조성(&)과 최상위(top-level) const는 자동 제거됨 ★
    // ─────────────────────────────────────────────────────────────────
    cout << "  [1] 기본 추론 - 참조/const 자동 제거\n";
    {
        const int   ci = 42;
        const int&  cr = ci;
        int*        ip = nullptr; (void)ip;

        auto a = ci;     // a : int       (const 떨어짐!)
        auto b = cr;     // b : int       (& 떨어짐, const 도 떨어짐)
        auto c = ip;     // c : int*      (포인터의 const-ness는 다른 문제)

        a = 99;          // OK - const 아님
        b = 99;          // OK
        cout << "    a=" << a << " b=" << b << " (const/ref 모두 제거)\n";
    }

    // ─────────────────────────────────────────────────────────────────
    //  2. auto& / const auto& / auto&& - 의도 명시
    // ─────────────────────────────────────────────────────────────────
    cout << "\n  [2] 참조 / forwarding reference\n";
    {
        vector<int> v{1, 2, 3, 4, 5};

        // (a) auto - 복사. 큰 객체엔 비싸다
        for (auto x : v) (void)x;

        // (b) auto& - 참조. 수정 가능
        for (auto& x : v) x *= 2;
        cout << "    수정 후: ";
        for (const auto& x : v) cout << x << " ";
        cout << "\n";

        // (c) const auto& - 읽기 전용 참조. 가장 안전한 기본
        // (d) auto&& - "universal/forwarding reference" 같이 쓸 때
        //     proxy 컨테이너(vector<bool>) 호환에 유리
        vector<bool> vb{true, false, true};
        for (auto&& b : vb) {
            // vb의 원소는 bit proxy → auto&는 컴파일 에러
            // auto&&는 OK (proxy를 받음)
            (void)b;
        }
        cout << "    auto&& 는 vector<bool>의 proxy 객체도 받음\n";

        // ★ 메모리 관점 정리:
        //   auto       = 복사 (의도치 않은 큰 비용 발생 위험)
        //   auto&      = 참조 (원본 수정 가능, lvalue 만)
        //   const auto&= 읽기 전용 참조 (★ 디폴트 추천)
        //   auto&&     = forwarding (lvalue/rvalue 모두, proxy 호환)
    }

    // ─────────────────────────────────────────────────────────────────
    //  3. auto + 포인터 / 배열 / 함수 decay
    // ─────────────────────────────────────────────────────────────────
    cout << "\n  [3] decay 규칙 - 배열/함수가 포인터로 변함\n";
    {
        int arr[5] = {1, 2, 3, 4, 5};
        auto a1 = arr;          // a1 : int*  (배열 → 포인터, decay)
        auto& a2 = arr;         // a2 : int(&)[5]  (참조라 decay 없음)

        cout << "    auto = int* (decay), auto& = int(&)[5]\n";
        cout << "    sizeof(arr)=" << sizeof(arr)
             << "  sizeof(a1)=" << sizeof(a1)
             << "  sizeof(a2)=" << sizeof(a2) << "\n";
        // sizeof(a1) = 포인터 크기, sizeof(a2) = 배열 크기 (20 bytes)
        // → 함수 매개변수에서 auto는 배열을 못 받음 (포인터로 변환됨)
        //   배열 크기 보존하려면 auto& 또는 std::span / std::array
    }

    // ─────────────────────────────────────────────────────────────────
    //  4. 초기화자 리스트의 함정
    // ─────────────────────────────────────────────────────────────────
    cout << "\n  [4] 초기화자 리스트 함정\n";
    {
        auto x1 = 42;            // int
        auto x2(42);             // int  (직접 초기화)
        auto x3{42};             // ★ C++17부터 int. C++11에서는 initializer_list<int>!
        auto x4 = {42};          // ★ initializer_list<int> (모든 표준)

        cout << "    auto x = {42};   → initializer_list<int>\n";
        cout << "    auto x{42};      → C++17부터 int (이전엔 list)\n";

        // 권장: =, () 사용. {} 는 의도가 list가 아니면 피한다
        // 또는 std::initializer_list<int>를 명시
        (void)x1; (void)x2; (void)x3; (void)x4;
    }

    // ─────────────────────────────────────────────────────────────────
    //  5. 의도치 않은 복사 - proxy 객체 / 큰 객체
    // ─────────────────────────────────────────────────────────────────
    cout << "\n  [5] 의도치 않은 복사 함정\n";
    {
        map<string, vector<int>> big{
            {"odd", {1, 3, 5, 7, 9}},
            {"even", {2, 4, 6, 8, 10}}
        };

        // 잘못: auto 사용 → pair<KEY,VAL>를 매번 복사 (큰 비용)
        for (auto kv : big) (void)kv;          // ❌ 복사 발생

        // 또 다른 함정: pair의 첫 멤버가 const string이라
        //   auto&로 받아야 정확. const auto&가 가장 안전
        for (const auto& [k, v] : big) {
            cout << "    " << k << ": " << v.size() << " items\n";
        }

        // map<K,V>::value_type 은 pair<const K, V> 라서
        //   auto& [k, v] : big   →  k : const string, v : vector<int>&
        //   auto  [k, v] : big   →  k : string (복사됨!), v : vector<int> (복사됨!)
    }

    // ─────────────────────────────────────────────────────────────────
    //  6. 함수 반환 타입 추론 (C++14)
    // ─────────────────────────────────────────────────────────────────
    cout << "\n  [6] 함수 반환 타입 auto (C++14)\n";
    {
        // 람다로 시연 (함수 정의는 파일 범위라 람다로)
        auto add = [](int a, int b) -> auto { return a + b; };
        // ↑ 명시적 trailing return type. -> auto는 보통 생략.

        // 더 단순:
        auto mul = [](double a, double b) { return a * b; };  // 반환 = double

        // 함정: 같은 함수에서 다른 타입 반환 → 컴파일 에러
        // auto bad = [](bool c) { if (c) return 1; else return 1.0; };  // ❌

        // 또 다른 함정: 지역 변수 참조 반환
        // auto f = []() -> auto& {
        //     int local = 0;
        //     return local;            // ⚠ 댕글링 참조!
        // };

        cout << "    add(3, 4) = " << add(3, 4) << "\n";
        cout << "    mul(2.5, 4) = " << mul(2.5, 4) << "\n";

        // ★ 메모리 관점:
        //   - auto return은 RVO/NRVO로 복사 안 됨 (대부분)
        //   - decltype(auto)로 참조성 보존 가능 (다음 항목)
    }

    // ─────────────────────────────────────────────────────────────────
    //  7. decltype vs decltype(auto) - 미묘한 차이
    // ─────────────────────────────────────────────────────────────────
    cout << "\n  [7] decltype / decltype(auto)\n";
    {
        int   i = 42;
        int&  ri = i;
        const int ci = 100;

        // decltype: 표현식 자체의 타입 (참조/const 모두 보존)
        decltype(i)  d1 = 0;        // int
        decltype(ri) d2 = i;        // int& (참조 보존)
        decltype(ci) d3 = 0;        // const int (const 보존)
        (void)d1; (void)d3;

        // 단, decltype은 "표현식 형태"에 민감
        decltype(i)   x = 0;        // x : int        (변수명: 선언된 그대로)
        decltype((i)) y = i;        // ★ y : int&    (괄호 = 표현식 → lvalue)
        // → 같은 이름인데 괄호 유무로 타입이 다름. 함정 1위.
        (void)x; (void)y;

        // decltype(auto) : auto 자리에 decltype 규칙 적용
        // "표현식의 타입을 그대로 받음" — 참조성 보존 ★
        auto           v1 = ri;     // int   (& 떨어짐)
        decltype(auto) v2 = ri;     // int&  (& 보존)
        v2 = 99;
        cout << "    decltype(auto) v2 = ri 후 i = " << i << "\n";  // 99

        cout << "    auto는 참조/const 떨어뜨리지만, decltype(auto)는 보존\n";
        d2 = 50;
        cout << "    decltype(ri) d2 도 참조라 i = " << i << "\n";
    }

    // ─────────────────────────────────────────────────────────────────
    //  8. 제네릭 람다 (C++14) / auto 매개변수
    // ─────────────────────────────────────────────────────────────────
    cout << "\n  [8] 제네릭 람다\n";
    {
        // 매개변수 자리에 auto → 컴파일러가 템플릿처럼 인스턴스화
        auto print = [](const auto& x) { cout << x << " "; };
        cout << "    제네릭 람다: ";
        print(42); print(3.14); print("hello"); cout << "\n";

        // C++20: 명시적 템플릿 매개변수
        // auto compare = []<typename T>(const T& a, const T& b) { ... };
    }

    // ─────────────────────────────────────────────────────────────────
    //  9. CTAD - 클래스 템플릿 인자 추론 (C++17)
    // ─────────────────────────────────────────────────────────────────
    cout << "\n  [9] CTAD (Class Template Argument Deduction)\n";
    {
        // C++14: 템플릿 인자 항상 명시
        // pair<int, double> p1(1, 3.14);
        // vector<int> v1{1, 2, 3};

        // C++17: 인자에서 추론
        pair p1(1, 3.14);            // pair<int, double>
        vector v1{1, 2, 3};          // vector<int>
        // tuple t1(1, 2.0, "x");    // tuple<int, double, const char*>

        cout << "    pair p1(1, 3.14) → pair<int,double>: "
             << p1.first << ", " << p1.second << "\n";
        cout << "    vector v1{1,2,3} → vector<int>, size=" << v1.size() << "\n";

        // 함정: vector<int> v2{1};   → 1개짜리 벡터
        //       vector v2{1};        → 1개짜리 vector<int> (의도대로)
        //       vector v3 = {1, 2};  → vector<int>
        //       vector v4(10);       → vector<int>(10), CTAD 안 함!
        //                              ← 단일 정수 인자는 size로 해석
    }

    // ─────────────────────────────────────────────────────────────────
    // 10. 임시 객체 수명 / 댕글링 참조 함정
    // ─────────────────────────────────────────────────────────────────
    cout << "\n  [10] 임시 객체 수명과 auto&&\n";
    {
        auto make_str = []() -> string { return "임시 문자열"; };

        // (a) 안전: const& - 임시 객체 수명 연장됨
        const auto& s1 = make_str();
        cout << "    const auto& s1 = " << s1 << "\n";

        // (b) 안전: auto&& - 임시 객체 수명 연장됨
        auto&& s2 = make_str();
        cout << "    auto&& s2     = " << s2 << "\n";

        // (c) 안전: auto - 복사 (move 발생, RVO)
        auto s3 = make_str();
        cout << "    auto s3       = " << s3 << "\n";

        // (d) ⚠ 댕글링: 임시의 멤버를 참조
        //   auto& bad = string("temp").c_str();   // ❌ const char* → 임시 이미 사라짐
        //   const auto& bad2 = vector<int>{1,2,3}[0];   // 정상이긴 하지만 위험
        //   for (const auto& x : returns_temporary().get_vec()) ... // ★ 흔한 함정
        //     C++23부터 일부 해결되지만 아직 컴파일러 따라 다름

        // ★ C++17 보장 RVO:
        //   return string("...");   // 복사/이동 없음. 호출자에 직접 생성
        //   auto x = func();        // RVO 활성. 비싼 객체도 안전
    }

    // ─────────────────────────────────────────────────────────────────
    // 11. auto가 절대 복사 못 잡는 케이스
    // ─────────────────────────────────────────────────────────────────
    cout << "\n  [11] auto가 잘못 추론하는 케이스\n";
    {
        // (a) vector<bool>의 proxy
        vector<bool> vb{true, false, true};
        // auto x = vb[0];   // x : vector<bool>::reference (proxy!)
                            // 일반 bool처럼 동작 안 함, 참조 의미 모호
        // 권장: bool b = vb[0];   // 명시적

        // (b) Eigen / 행렬 라이브러리의 lazy expression
        //   Eigen::MatrixXd a, b, c;
        //   auto x = a + b;   // x : Sum<...> (계산 안 된 임시 표현식)
        //   ...
        //   cout << x;        // 여기서 a, b 변경되면 결과 다름
        // 권장: Eigen::MatrixXd x = a + b;   // 즉시 평가

        // (c) string * char 등
        //   const char* s = "hello";
        //   auto t = s + 1;   // t : const char*  (포인터 산술)
        //   직관과 다를 수 있음
    }

    // ─────────────────────────────────────────────────────────────────
    // 12. AAA (Almost Always Auto) 스타일 가이드
    // ─────────────────────────────────────────────────────────────────
    cout << "\n  [12] auto 사용 가이드\n";
    cout << R"(
  ┌─ 권장 (auto 적극 사용) ───────────────────────────────┐
  │ ✓ 반복자: auto it = vec.begin();                       │
  │ ✓ 람다 결과: auto f = [](){...};                        │
  │ ✓ make_xxx: auto p = make_unique<Foo>(...);             │
  │ ✓ 긴 타입: auto m = unordered_map<string,vector<int>>{};│
  │ ✓ 범위 for: for (const auto& x : container)             │
  │ ✓ 구조적 바인딩: auto [k, v] = pair;                    │
  └───────────────────────────────────────────────────────┘
  ┌─ 비권장 (명시적 타입이 더 나음) ──────────────────────┐
  │ ✗ 의도가 명확해야 하는 인터페이스: int port;            │
  │ ✗ proxy 객체 (vector<bool>, Eigen lazy): 명시적 타입   │
  │ ✗ 한 줄짜리 단순 변수: int n = 0;                       │
  │ ✗ 초보자 코드 (학습 단계): 타입 명시로 학습 효과         │
  │ ✗ 매직 넘버 의미 부여: int64_t timestamp_ms = ...;      │
  └───────────────────────────────────────────────────────┘
  ┌─ 메모리 / 성능 체크리스트 ────────────────────────────┐
  │ □ for 루프에서 의도치 않은 복사 없는지 (const auto&)   │
  │ □ proxy 객체 (vector<bool>) 사용 시 auto 결과 확인     │
  │ □ 큰 객체 반환 시 RVO 의존 OK인지                       │
  │ □ 람다 캡처 [&] 자동 캡처 시 댕글링 가능성              │
  │ □ decltype(auto)로 참조 의도 명확화                     │
  │ □ auto&&와 std::forward 함께 쓰는 perfect forwarding   │
  └───────────────────────────────────────────────────────┘
)";

    cout << endl;
}


// =====================================================================
// 레슨 1 — C++17 기본 개선사항
// =====================================================================
void lesson1_cpp17_basics() {
    cout << "[레슨 1] C++17 기본 개선\n\n";

    // ── 1) if / switch 초기화 문 ──
    cout << "  --- if 초기화문 ---\n";
    vector<int> v = {1, 2, 3, 4, 5};
    // → v = [1,2,3,4,5]

    if (auto it = find(v.begin(), v.end(), 3); it != v.end()) {
        // → it는 v[2]를 가리킴 (3이 인덱스 2에 있음)
        // → it != end() true → 진입
        cout << "  찾음: " << *it << " (위치: " << (it - v.begin()) << ")\n";
        // → *it = 3, it-begin = 2
        // > 출력:   찾음: 3 (위치: 2)
    }

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
    // → 람다 인스턴스화: container = vector<int>
    //   item: 10, 20, 30
    // > 출력:   auto 람다: 10 20 30

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
        return nullopt;
    };

    if (auto name = find_user(1); name.has_value()) {
        // → name = optional("홍길동"), has_value() true
        cout << "  ID 1: " << name.value() << "\n";
        // > 출력:   ID 1: 홍길동
    }
    if (auto name = find_user(99)) {
        // → find_user(99) = nullopt, bool 변환 false → else 분기
        cout << "  ID 99: " << *name << "\n";
    } else {
        cout << "  ID 99: 사용자 없음\n";
        // > 출력:   ID 99: 사용자 없음
    }

    cout << "  ID 99 (기본값): " << find_user(99).value_or("미등록") << "\n\n";
    // → nullopt → "미등록" 기본값 사용
    // > 출력:   ID 99 (기본값): 미등록

    cout << "  --- variant ---\n";
    variant<int, double, string> data;
    // → 기본 초기화: int 0 (첫 번째 타입)

    data = 42;
    cout << "  int: " << get<int>(data) << "\n";
    // → 현재 int 보유. get<int> 안전.
    // > 출력:   int: 42

    data = 3.14;
    cout << "  double: " << get<double>(data) << "\n";
    // → 현재 double 보유.
    // > 출력:   double: 3.14

    data = "Hello"s;
    cout << "  string: " << get<string>(data) << "\n";
    // → 현재 string 보유.
    // > 출력:   string: Hello

    cout << "  현재 인덱스: " << data.index() << " (0=int,1=double,2=string)\n";
    // → string은 세 번째 타입 → index 2
    // > 출력:   현재 인덱스: 2 (0=int,1=double,2=string)

    visit([](auto&& val) {
        // → val의 타입은 현재 보관 중인 타입 (string)
        cout << "  visit: " << val << "\n";
        // > 출력:   visit: Hello
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

    pair<string, int> p = {"홍길동", 25};
    auto [name, age] = p;
    // → name = "홍길동", age = 25
    cout << "  pair: " << name << " " << age << "\n";
    // > 출력:   pair: 홍길동 25

    map<string, int> scores = {{"국어", 90}, {"영어", 85}, {"수학", 92}};
    // → map 사전순 정렬: "국어", "수학", "영어"
    cout << "  map 순회:\n";
    for (const auto& [subject, score] : scores) {
        // 1회차: subject="국어", score=90
        // 2회차: subject="수학", score=92
        // 3회차: subject="영어", score=85
        cout << "    " << subject << ": " << score << "\n";
    }
    // > 출력:
    //     국어: 90
    //     수학: 92
    //     영어: 85

    auto get_info = []() -> tuple<string, int, double> {
        return {"이영희", 22, 95.5};
    };
    auto [n, a, s] = get_info();
    // → n="이영희", a=22, s=95.5
    cout << "  tuple: " << n << " " << a << "세 " << s << "점\n";
    // > 출력:   tuple: 이영희 22세 95.5점

    int arr[] = {10, 20, 30};
    auto [x, y, z] = arr;
    // → x=10, y=20, z=30 (배열은 정확히 크기와 일치해야 함)
    cout << "  배열: " << x << " " << y << " " << z << "\n";
    // > 출력:   배열: 10 20 30

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
    // → T=int, is_integral_v<int>=true → "정수형: 42"
    // > 출력:   정수형: 42
    cout << "  " << type_name(3.14) << "\n\n";
    // → T=double, is_floating_point_v=true → "실수형: 3.140000"
    // > 출력:   실수형: 3.140000
    //   ※ to_string의 double 기본은 6자리 소수점

    cout << "  sum_all(1,2,3,4,5) = " << sum_all(1, 2, 3, 4, 5) << "\n";
    // → fold: ((((1+2)+3)+4)+5) = 15
    // > 출력:   sum_all(1,2,3,4,5) = 15
    cout << "  print_all: ";
    print_all(1, 2.5, "hello", 'X');
    // → 각 인자를 cout << 로 흘려보냄
    // > 출력:   print_all: 1 2.5 hello X

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
