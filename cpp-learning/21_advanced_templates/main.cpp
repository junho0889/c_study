// ============================================================================
// 21장: 고급 템플릿 & 메타프로그래밍 (Advanced Templates & Metaprogramming)
// ============================================================================
// 컴파일: g++ -std=c++17 -o advanced_templates main.cpp
//
// ┌──────────────────────────────────────────────────────────────┐
// │  학습 로드맵                                                  │
// ├──────────────────────────────────────────────────────────────┤
// │  레슨 1: 템플릿 특수화 (Full / Partial Specialization)       │
// │  레슨 2: SFINAE (enable_if, void_t, 표현식 SFINAE)          │
// │  레슨 3: 가변 인자 템플릿 (Parameter pack, fold expression)  │
// │  레슨 4: 컴파일 타임 프로그래밍 (constexpr 심화, if constexpr)│
// │  레슨 5: Type Traits 활용 (is_same, decay, conditional 등)  │
// │  레슨 6: 템플릿 메타프로그래밍 (팩토리얼, 타입 리스트)        │
// │  레슨 7: 실전 - 타입 안전 printf, 직렬화, 문자열 해시        │
// └──────────────────────────────────────────────────────────────┘
// ============================================================================

#include <iostream>
#include <string>
#include <vector>
#include <type_traits>
#include <tuple>
#include <array>
#include <sstream>
#include <functional>
#include <cstring>
#include <utility>

using namespace std;

// ============================================================================
// 레슨 1: 템플릿 특수화 (Template Specialization)
// ============================================================================
//  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐
//  │ 기본 템플릿   │    │ 완전 특수화       │    │ 부분 특수화       │
//  │ template<T>  │───>│ template<>       │    │ template<T>      │
//  │ 모든 타입    │    │ 특정 타입 전용    │    │ 포인터/배열 전용  │
//  └──────────────┘    └──────────────────┘    └──────────────────┘
namespace lesson1 {

    // --- 1-1: 기본 템플릿 + 완전 특수화 ---
    template<typename T>
    struct TypeInfo {
        static string name() { return "알 수 없는 타입"; }
        static bool is_numeric() { return false; }
    };

    // 완전 특수화: template<> 로 시작, 타입 매개변수 없음
    template<> struct TypeInfo<int> {
        static string name() { return "정수 (int)"; }
        static bool is_numeric() { return true; }
    };
    template<> struct TypeInfo<double> {
        static string name() { return "실수 (double)"; }
        static bool is_numeric() { return true; }
    };
    template<> struct TypeInfo<string> {
        static string name() { return "문자열 (string)"; }
        static bool is_numeric() { return false; }
    };

    // --- 1-2: 부분 특수화 (클래스 템플릿만 가능) ---
    // 포인터 타입 전용
    template<typename T>
    struct TypeInfo<T*> {
        static string name() { return TypeInfo<T>::name() + " 포인터"; }
        static bool is_numeric() { return false; }
    };
    // 배열 타입 전용
    template<typename T, size_t N>
    struct TypeInfo<T[N]> {
        static string name() { return TypeInfo<T>::name() + " 배열[" + to_string(N) + "]"; }
        static bool is_numeric() { return false; }
    };
    // vector 전용
    template<typename T>
    struct TypeInfo<vector<T>> {
        static string name() { return "벡터<" + TypeInfo<T>::name() + ">"; }
        static bool is_numeric() { return false; }
    };

    // --- 1-3: 함수 템플릿 완전 특수화 (부분 특수화 불가 → 오버로딩 사용) ---
    template<typename T>
    T max_value(T a, T b) { return (a > b) ? a : b; }

    template<>
    const char* max_value<const char*>(const char* a, const char* b) {
        return (strcmp(a, b) > 0) ? a : b;  // 문자열 내용 비교
    }

    // --- 1-4: 실전 - 타입별 직렬화기 ---
    template<typename T> struct Serializer {
        static string serialize(const T&) { return "RAW:unsupported"; }
    };
    template<> struct Serializer<int> {
        static string serialize(const int& v) { return "INT:" + to_string(v); }
    };
    template<> struct Serializer<string> {
        static string serialize(const string& v) { return "STR:" + to_string(v.size()) + ":" + v; }
    };
    template<typename T> struct Serializer<vector<T>> {
        static string serialize(const vector<T>& vec) {
            string r = "VEC:" + to_string(vec.size()) + ":[";
            for (size_t i = 0; i < vec.size(); ++i) {
                if (i > 0) r += ",";
                r += Serializer<T>::serialize(vec[i]);
            }
            return r + "]";
        }
    };

    void run() {
        cout << "=== 레슨 1: 템플릿 특수화 ===\n\n";
        cout << "  int: " << TypeInfo<int>::name() << "\n";
        cout << "  int*: " << TypeInfo<int*>::name() << "\n";
        cout << "  int[5]: " << TypeInfo<int[5]>::name() << "\n";
        cout << "  vector<int>: " << TypeInfo<vector<int>>::name() << "\n";
        cout << "  max(\"apple\",\"banana\") = " << max_value<const char*>("apple","banana") << "\n";
        cout << "  직렬화: " << Serializer<vector<int>>::serialize({1,2,3}) << "\n\n";
    }
}

// ============================================================================
// 레슨 2: SFINAE (Substitution Failure Is Not An Error)
// ============================================================================
//  컴파일러가 템플릿 인자 치환 시 실패하면 에러가 아니라 후보에서 제외됨
//
//  호출: foo(42)
//   ├─> 후보1: foo(T) [T=int] → 치환 성공 ✓ → 선택됨
//   └─> 후보2: foo(T) [T::value_type 필요] → 치환 실패 → 제외 ✗
namespace lesson2 {

    // --- 2-1: enable_if - 조건부 함수 활성화 ---
    template<typename T>
    typename enable_if<is_integral<T>::value, T>::type
    safe_divide(T a, T b) {
        if (b == 0) { cerr << "  [경고] 0으로 나눌 수 없습니다!\n"; return 0; }
        return a / b;
    }

    template<typename T>
    typename enable_if<is_floating_point<T>::value, T>::type
    safe_divide(T a, T b) {
        if (abs(b) < 1e-10) { cerr << "  [경고] 0에 가까운 수!\n"; return 0.0; }
        return a / b;
    }

    // --- 2-2: void_t를 활용한 타입 특성 감지 ---
    //  void_t<표현식>이 유효하면 → 특수화 선택, 무효하면 → 기본 선택
    template<typename T, typename = void>
    struct has_begin : false_type {};
    template<typename T>
    struct has_begin<T, void_t<decltype(declval<T>().begin())>> : true_type {};

    template<typename T, typename = void>
    struct has_size : false_type {};
    template<typename T>
    struct has_size<T, void_t<decltype(declval<T>().size())>> : true_type {};

    template<typename T, typename = void>
    struct has_push_back : false_type {};
    template<typename T>
    struct has_push_back<T, void_t<decltype(
        declval<T>().push_back(declval<typename T::value_type>()))>> : true_type {};

    // --- 2-3: is_addable - 직접 만드는 트레이트 ---
    template<typename T, typename U, typename = void>
    struct is_addable : false_type {};
    template<typename T, typename U>
    struct is_addable<T, U, void_t<decltype(declval<T>() + declval<U>())>> : true_type {};

    // --- 2-4: enable_if로 컨테이너만 출력 ---
    template<typename C>
    enable_if_t<has_begin<C>::value>
    print_container(const string& name, const C& c) {
        cout << "  " << name << ": [";
        bool first = true;
        for (const auto& e : c) { if (!first) cout << ", "; cout << e; first = false; }
        cout << "]\n";
    }

    void run() {
        cout << "=== 레슨 2: SFINAE ===\n\n";
        cout << "  정수 나눗셈: 10/3 = " << safe_divide(10, 3) << "\n";
        cout << "  실수 나눗셈: 10.0/3.0 = " << safe_divide(10.0, 3.0) << "\n";
        cout << "  vector에 begin()? " << (has_begin<vector<int>>::value ? "예" : "아니오") << "\n";
        cout << "  int에 begin()? " << (has_begin<int>::value ? "예" : "아니오") << "\n";
        cout << "  vector에 push_back()? " << (has_push_back<vector<int>>::value ? "예" : "아니오") << "\n";
        cout << "  int+int 가능? " << (is_addable<int,int>::value ? "예" : "아니오") << "\n";
        cout << "  int+string 가능? " << (is_addable<int,string>::value ? "예" : "아니오") << "\n";
        print_container("벡터", vector<int>{10, 20, 30});
        cout << "\n";
    }
}

// ============================================================================
// 레슨 3: 가변 인자 템플릿 (Variadic Templates)
// ============================================================================
//  template<typename... Args>  // Args는 매개변수 팩
//  void foo(Args... args) {    // args는 함수 매개변수 팩
//      // args...              // 팩 확장 (pack expansion)
//  }
//
//  Fold Expression (C++17):
//   (args op ...)      → 우측 접기:  a1 op (a2 op a3)
//   (... op args)      → 좌측 접기:  (a1 op a2) op a3
//   (init op ... op args) → 초기값 있는 좌측 접기
namespace lesson3 {

    // --- 3-1: 재귀 패턴 (고전적 방식) ---
    void print_all() { cout << "\n"; }
    template<typename First, typename... Rest>
    void print_all(const First& first, const Rest&... rest) {
        cout << first;
        if (sizeof...(rest) > 0) cout << ", ";
        print_all(rest...);
    }

    // --- 3-2: Fold expression (C++17) ---
    template<typename... Args> auto sum(Args... args) { return (args + ...); }
    template<typename... Args> auto product(Args... args) { return (1 * ... * args); }
    template<typename... Args> bool all_true(Args... args) { return (args && ...); }
    template<typename... Args> bool any_true(Args... args) { return (args || ...); }

    // --- 3-3: 인덱스 출력 (콤마 fold 트릭) ---
    template<typename... Args>
    void print_with_index(const Args&... args) {
        size_t i = 0;
        ((cout << "  [" << i++ << "] " << args << "\n"), ...);
    }

    // --- 3-4: 변환 적용 ---
    template<typename F, typename... Args>
    auto transform_all(F func, Args... args) {
        return make_tuple(func(args)...);
    }

    // --- 3-5: 가변 인자 최대값 ---
    template<typename T> T find_max(T v) { return v; }
    template<typename T, typename... Rest>
    T find_max(T first, Rest... rest) {
        T r = find_max(rest...);
        return (first > r) ? first : r;
    }

    void run() {
        cout << "=== 레슨 3: 가변 인자 템플릿 ===\n\n";
        cout << "  print_all: "; print_all(1, 2.5, "hello", 'A');
        cout << "  sum(1..5) = " << sum(1,2,3,4,5) << "\n";
        cout << "  product(1..4) = " << product(1,2,3,4) << "\n";
        cout << "  all_true(T,T,T) = " << (all_true(true,true,true)?"참":"거짓") << "\n";
        cout << "  any_true(F,T,F) = " << (any_true(false,true,false)?"참":"거짓") << "\n";
        print_with_index("사과", 42, 3.14);
        cout << "  find_max(3,1,4,1,5,9) = " << find_max(3,1,4,1,5,9) << "\n";
        auto d = transform_all([](int x){return x*2;}, 1, 2, 3);
        cout << "  transform *2: (" << get<0>(d) << "," << get<1>(d) << "," << get<2>(d) << ")\n\n";
    }
}

// ============================================================================
// 레슨 4: 컴파일 타임 프로그래밍 (constexpr, if constexpr)
// ============================================================================
//  C++11: constexpr 함수 (단일 return)
//  C++14: constexpr 확장 (반복문, 지역변수)
//  C++17: if constexpr (조건부 컴파일 - 불일치 분기 완전 제거)
//  C++20: consteval (반드시 컴파일 타임 실행)
namespace lesson4 {

    // --- 4-1: constexpr 함수 ---
    constexpr int factorial(int n) {
        int r = 1;
        for (int i = 2; i <= n; ++i) r *= i;
        return r;
    }
    constexpr long long fibonacci(int n) {
        if (n <= 1) return n;
        return fibonacci(n-1) + fibonacci(n-2);
    }

    // --- 4-2: constexpr 배열 생성 ---
    template<size_t N>
    constexpr array<int, N> generate_squares() {
        array<int, N> r{};
        for (size_t i = 0; i < N; ++i) r[i] = static_cast<int>(i * i);
        return r;
    }

    // --- 4-3: constexpr 문자열 처리 ---
    constexpr int constexpr_strlen(const char* s) {
        int len = 0; while (s[len]) ++len; return len;
    }
    constexpr bool constexpr_streq(const char* a, const char* b) {
        while (*a && *b) { if (*a != *b) return false; ++a; ++b; }
        return *a == *b;
    }

    // --- 4-4: if constexpr (C++17) ---
    //  일반 if: 두 분기 모두 컴파일됨
    //  if constexpr: 조건 불일치 분기는 컴파일에서 제거
    template<typename T>
    string smart_to_string(const T& v) {
        if constexpr (is_integral<T>::value) return "정수: " + to_string(v);
        else if constexpr (is_floating_point<T>::value) return "실수: " + to_string(v);
        else if constexpr (is_same<T, string>::value) return "문자열: " + v;
        else return "기타 타입";
    }

    // --- 4-5: 컴파일 타임 소수 판별 ---
    constexpr bool is_prime(int n) {
        if (n < 2) return false;
        if (n < 4) return true;
        if (n % 2 == 0 || n % 3 == 0) return false;
        for (int i = 5; i * i <= n; i += 6)
            if (n % i == 0 || n % (i+2) == 0) return false;
        return true;
    }
    constexpr int count_primes(int n) {
        int c = 0; for (int i = 2; i <= n; ++i) if (is_prime(i)) ++c; return c;
    }

    // --- 4-6: constexpr 클래스 ---
    class ConstexprPoint {
        double x_, y_;
    public:
        constexpr ConstexprPoint(double x=0, double y=0) : x_(x), y_(y) {}
        constexpr double x() const { return x_; }
        constexpr double y() const { return y_; }
        constexpr ConstexprPoint operator+(const ConstexprPoint& o) const {
            return {x_+o.x_, y_+o.y_};
        }
        constexpr double dist_sq(const ConstexprPoint& o) const {
            return (x_-o.x_)*(x_-o.x_) + (y_-o.y_)*(y_-o.y_);
        }
    };

    void run() {
        cout << "=== 레슨 4: 컴파일 타임 프로그래밍 ===\n\n";
        constexpr int f5 = factorial(5);
        constexpr long long fib10 = fibonacci(10);
        constexpr auto squares = generate_squares<8>();
        constexpr int primes100 = count_primes(100);
        constexpr ConstexprPoint p1(3,4), p2(6,8);
        constexpr auto p3 = p1 + p2;

        cout << "  5! = " << f5 << ", 10! = " << factorial(10) << "\n";
        cout << "  fib(10) = " << fib10 << "\n";
        cout << "  제곱수: "; for (auto s : squares) cout << s << " "; cout << "\n";
        cout << "  strlen(\"Hi!\") = " << constexpr_strlen("Hi!") << "\n";
        cout << "  smart_to_string: " << smart_to_string(42) << ", " << smart_to_string(3.14) << "\n";
        cout << "  100이하 소수: " << primes100 << "개, 17은 소수? " << (is_prime(17)?"예":"아니오") << "\n";
        cout << "  p1+p2 = (" << p3.x() << "," << p3.y() << "), 거리^2 = " << p1.dist_sq(p2) << "\n\n";
    }
}

// ============================================================================
// 레슨 5: Type Traits 활용
// ============================================================================
//  ┌──────────────────────────────────────────────────────┐
//  │  분류            예시                                │
//  ├──────────────────────────────────────────────────────┤
//  │  기본 타입 검사  is_integral, is_floating_point      │
//  │  합성 타입 검사  is_pointer, is_array, is_class      │
//  │  타입 관계       is_same, is_base_of, is_convertible │
//  │  타입 변환       remove_const, decay, add_pointer    │
//  │  조건부 선택     conditional                          │
//  └──────────────────────────────────────────────────────┘
namespace lesson5 {

    // --- 5-1: 타입 분석 유틸리티 ---
    template<typename T>
    void analyze_type(const string& name) {
        cout << "  [" << name << "] 정수:" << is_integral<T>::value
             << " 실수:" << is_floating_point<T>::value
             << " 포인터:" << is_pointer<T>::value
             << " 클래스:" << is_class<T>::value
             << " const:" << is_const<T>::value
             << " 크기:" << sizeof(T) << "\n";
    }

    // --- 5-2: conditional - 조건부 타입 선택 ---
    //  conditional<조건, TrueType, FalseType>::type
    template<typename T>
    struct SafeContainer {
        // 작은 타입은 값으로, 큰 타입은 참조로
        using storage_type = conditional_t<(sizeof(T)<=8), T, const T&>;
        storage_type data;
        SafeContainer(storage_type d) : data(d) {}
        void info() const {
            cout << "    저장: " << (sizeof(T)<=8 ? "값 복사" : "참조") << "\n";
        }
    };

    // --- 5-3: is_base_of - 상속 관계 확인 ---
    struct Animal {};
    struct Dog : Animal {};
    struct Cat : Animal {};
    struct Car {};  // 동물 아님

    template<typename T>
    string classify() {
        if constexpr (is_base_of<Animal, T>::value) return "동물";
        else return "동물 아님";
    }

    // --- 5-4: common_type ---
    template<typename T, typename U>
    auto safe_add(T a, U b) -> common_type_t<T, U> { return a + b; }

    // --- 5-5: decay ---
    //  decay: 함수 인자처럼 변환 (참조 제거, 배열→포인터, 함수→함수포인터)
    //  int& → int,  int[5] → int*,  const int& → int

    void run() {
        cout << "=== 레슨 5: Type Traits 활용 ===\n\n";
        analyze_type<int>("int");
        analyze_type<double>("double");
        analyze_type<string>("string");
        analyze_type<int*>("int*");
        analyze_type<const int>("const int");

        cout << "\n  [conditional]\n";
        SafeContainer<int> sc(42); sc.info();
        string big = "긴 문자열"; SafeContainer<string> bc(big); bc.info();

        cout << "  [is_base_of] Dog:" << classify<Dog>() << " Car:" << classify<Car>() << "\n";
        cout << "  [common_type] 1+2.5=" << safe_add(1,2.5) << "\n";

        // decay 확인
        cout << "  [decay] int& == int? "
             << (is_same<decay_t<int&>, int>::value ? "예" : "아니오") << "\n\n";
    }
}

// ============================================================================
// 레슨 6: 템플릿 메타프로그래밍 실전
// ============================================================================
//  TMP에서의 대응 관계:
//  ┌──────────────┬─────────────────┐
//  │ 런타임       │ TMP             │
//  ├──────────────┼─────────────────┤
//  │ 변수         │ typedef / using │
//  │ 값           │ ::value         │
//  │ if-else      │ 부분 특수화     │
//  │ 반복문       │ 재귀 특수화     │
//  │ 함수         │ 템플릿 구조체   │
//  └──────────────┴─────────────────┘
namespace lesson6 {

    // --- 6-1: 컴파일 타임 팩토리얼 (TMP 방식) ---
    template<int N> struct Factorial {
        static constexpr long long value = N * Factorial<N-1>::value;
    };
    template<> struct Factorial<0> { static constexpr long long value = 1; };

    // --- 6-2: 컴파일 타임 피보나치 (TMP 방식) ---
    template<int N> struct Fibonacci {
        static constexpr long long value = Fibonacci<N-1>::value + Fibonacci<N-2>::value;
    };
    template<> struct Fibonacci<0> { static constexpr long long value = 0; };
    template<> struct Fibonacci<1> { static constexpr long long value = 1; };

    // --- 6-3: 거듭제곱 ---
    template<int B, int E> struct Power {
        static constexpr long long value = B * Power<B, E-1>::value;
    };
    template<int B> struct Power<B, 0> { static constexpr long long value = 1; };

    // --- 6-4: 타입 리스트 ---
    //  TypeList<int, double, string>
    //   ├─ size = 3,  head = int
    //   └─ tail = TypeList<double, string>
    template<typename... Ts> struct TypeList {
        static constexpr size_t size = sizeof...(Ts);
    };

    // Front: 첫 번째 타입
    template<typename L> struct Front;
    template<typename H, typename... T>
    struct Front<TypeList<H, T...>> { using type = H; };

    // PopFront: 첫 번째 제거
    template<typename L> struct PopFront;
    template<typename H, typename... T>
    struct PopFront<TypeList<H, T...>> { using type = TypeList<T...>; };

    // PushFront: 앞에 추가
    template<typename T, typename L> struct PushFront;
    template<typename T, typename... Ts>
    struct PushFront<T, TypeList<Ts...>> { using type = TypeList<T, Ts...>; };

    // TypeAt: N번째 타입
    template<typename L, size_t N> struct TypeAt;
    template<typename H, typename... T>
    struct TypeAt<TypeList<H, T...>, 0> { using type = H; };
    template<typename H, typename... T, size_t N>
    struct TypeAt<TypeList<H, T...>, N> { using type = typename TypeAt<TypeList<T...>, N-1>::type; };

    // Contains: 포함 여부
    template<typename L, typename T> struct Contains;
    template<typename T> struct Contains<TypeList<>, T> : false_type {};
    template<typename H, typename... Ts, typename T>
    struct Contains<TypeList<H, Ts...>, T>
        : conditional_t<is_same<H,T>::value, true_type, Contains<TypeList<Ts...>, T>> {};

    // --- 6-5: 컴파일 타임 GCD ---
    template<int A, int B> struct GCD { static constexpr int value = GCD<B, A%B>::value; };
    template<int A> struct GCD<A, 0> { static constexpr int value = A; };

    void run() {
        cout << "=== 레슨 6: 템플릿 메타프로그래밍 실전 ===\n\n";
        cout << "  5! = " << Factorial<5>::value << ", 15! = " << Factorial<15>::value << "\n";
        cout << "  fib(10) = " << Fibonacci<10>::value << ", fib(20) = " << Fibonacci<20>::value << "\n";
        cout << "  2^10 = " << Power<2,10>::value << ", 3^5 = " << Power<3,5>::value << "\n";

        using MyTypes = TypeList<int, double, string, char>;
        cout << "  TypeList 크기: " << MyTypes::size << "\n";
        cout << "  첫 번째=int? " << (is_same<Front<MyTypes>::type, int>::value?"예":"아니오") << "\n";
        cout << "  [1]=double? " << (is_same<TypeAt<MyTypes,1>::type, double>::value?"예":"아니오") << "\n";
        cout << "  string 포함? " << (Contains<MyTypes,string>::value?"예":"아니오") << "\n";
        cout << "  float 포함? " << (Contains<MyTypes,float>::value?"예":"아니오") << "\n";
        cout << "  GCD(12,8) = " << GCD<12,8>::value << ", GCD(100,75) = " << GCD<100,75>::value << "\n\n";
    }
}

// ============================================================================
// 레슨 7: 실전 예제
// ============================================================================
//  1. 타입 안전한 format 함수
//  2. 직렬화 프레임워크 기초
//  3. 컴파일 타임 문자열 해시 (switch문에서 문자열 비교)
//  4. Overloaded 방문자 패턴
namespace lesson7 {

    // --- 7-1: 타입 안전한 format ---
    // C의 printf는 타입 안전하지 않음: printf("%d","hello") → 정의되지 않은 동작!
    string safe_format(const string& fmt) {
        string r;
        for (size_t i = 0; i < fmt.size(); ++i) {
            if (fmt[i]=='{' && i+1<fmt.size() && fmt[i+1]=='}') { r += "<??>"; ++i; }
            else r += fmt[i];
        }
        return r;
    }
    template<typename First, typename... Rest>
    string safe_format(const string& fmt, const First& first, const Rest&... rest) {
        string r;
        for (size_t i = 0; i < fmt.size(); ++i) {
            if (fmt[i]=='{' && i+1<fmt.size() && fmt[i+1]=='}') {
                ostringstream oss; oss << first;
                return r + oss.str() + safe_format(fmt.substr(i+2), rest...);
            }
            r += fmt[i];
        }
        return r;
    }

    // --- 7-2: 직렬화 버퍼 ---
    class SerializeBuffer {
        string data_;
    public:
        template<typename T>
        enable_if_t<is_arithmetic<T>::value> write(const T& v) {
            data_ += "[" + string(typeid(T).name()) + ":" + to_string(v) + "]";
        }
        void write(const string& v) { data_ += "[s:" + to_string(v.size()) + ":" + v + "]"; }
        template<typename T> void write(const vector<T>& vec) {
            data_ += "[v:" + to_string(vec.size()) + ":";
            for (const auto& e : vec) write(e);
            data_ += "]";
        }
        // fold expression으로 여러 값 한번에 직렬화
        template<typename... Args> void write_all(const Args&... args) { (write(args), ...); }
        string str() const { return data_; }
        void clear() { data_.clear(); }
    };

    // --- 7-3: 컴파일 타임 문자열 해시 (FNV-1a) ---
    // switch문에서 문자열 비교에 유용
    constexpr unsigned int fnv1a(const char* s, unsigned int h = 2166136261u) {
        return (*s == '\0') ? h : fnv1a(s+1, (h ^ (unsigned int)(*s)) * 16777619u);
    }
    constexpr unsigned int operator""_hash(const char* s, size_t) { return fnv1a(s); }

    string process_command(const string& cmd) {
        switch (fnv1a(cmd.c_str())) {
            case "help"_hash: return "도움말 표시";
            case "quit"_hash: return "프로그램 종료";
            case "save"_hash: return "데이터 저장";
            default:          return "알 수 없는 명령: " + cmd;
        }
    }

    // --- 7-4: Overloaded 방문자 패턴 ---
    // 여러 람다를 합성하여 하나의 방문자로 만듦
    template<typename... Fns> struct Overloaded : Fns... { using Fns::operator()...; };
    template<typename... Fns> Overloaded(Fns...) -> Overloaded<Fns...>;  // CTAD 가이드

    void run() {
        cout << "=== 레슨 7: 실전 예제 ===\n\n";

        // format
        cout << "  " << safe_format("이름: {}, 나이: {}, 점수: {}", "김철수", 25, 98.5) << "\n";
        cout << "  " << safe_format("{} + {} = {}", 10, 20, 30) << "\n";

        // 직렬화
        SerializeBuffer buf;
        buf.write_all(100, 2.718, string("세계"));
        cout << "  직렬화: " << buf.str() << "\n";
        buf.clear();
        buf.write(vector<int>{1,2,3});
        cout << "  벡터: " << buf.str() << "\n";

        // 해시
        cout << "  cmd(help): " << process_command("help") << "\n";
        cout << "  cmd(xyz): " << process_command("xyz") << "\n";

        // Overloaded
        auto visitor = Overloaded{
            [](int x)           { cout << "  정수: " << x << "\n"; },
            [](double x)        { cout << "  실수: " << x << "\n"; },
            [](const string& x) { cout << "  문자열: " << x << "\n"; }
        };
        visitor(42); visitor(3.14); visitor(string("안녕"));
        cout << "\n";
    }
}

// ============================================================================
// 연습 문제
// ============================================================================
//  [연습 1] Printer<bool> 특수화: true→"참", false→"거짓" 출력
//  [연습 2] enable_if로 signed 정수만 받는 abs_value 함수 작성
//           힌트: is_signed<T>::value && is_integral<T>::value
//  [연습 3] find_min: 가변 인자 최소값 (find_max와 같은 구조)
//  [연습 4] constexpr nCr(이항 계수): nCr = n!/(r!*(n-r)!) 또는 재귀 공식
//  [연습 5] TypeList Back 메타함수: 마지막 타입 반환 (크기 1이 베이스 케이스)
namespace exercises {
    template<typename T> struct Printer {
        static void print(const T& v) { cout << v; }
    };
    // TODO: template<> struct Printer<bool> { ... };

    // TODO: template<typename T> enable_if_t<...> abs_value(T x) { ... }
    // TODO: template<typename T> T find_min(T v) { return v; } + 재귀 버전
    // TODO: constexpr long long nCr(int n, int r) { ... }
    // TODO: template<typename L> struct Back; (TypeList 마지막 타입)

    void run() {
        cout << "=== 연습 문제 (직접 풀어보세요!) ===\n";
        cout << "  위의 TODO를 구현하고 아래 테스트를 주석 해제하세요.\n";
        // Printer<bool>::print(true); cout << "\n";   // "참"
        // cout << abs_value(-42) << "\n";             // 42
        // cout << find_min(3,1,4,1,5) << "\n";        // 1
        // cout << nCr(10,3) << "\n";                   // 120
        cout << "\n";
    }
}

/*
=============================================================================
  레슨별 run() 출력 흐름 가이드 (대략)
=============================================================================
  lesson1 (특수화):
    Container<int>, Container<string>, Container<double> 각각 다른 동작
    int: 숫자 처리 / string: 문자열 / double: 정밀 출력

  lesson2 (SFINAE / void_t):
    has_size<vector<int>> → true
    has_size<int>          → false (size 멤버 없음)

  lesson3 (가변 인자 템플릿):
    sum(1, 2, 3, 4, 5) = 15  (fold expression)
    product(1.0, 2.0, 3.0, 4.0) = 24
    print(1, "hello", 3.14) → "1 hello 3.14"

  lesson4 (constexpr 메타프로그래밍):
    factorial<5> = 120 (컴파일 타임 계산)
    fibonacci<10> = 55
    is_prime<7> = true, is_prime<8> = false
    generate_squares<8> = [0, 1, 4, 9, 16, 25, 36, 49]

  lesson5 (Type Traits):
    is_integral<int> = true
    is_pointer<int*> = true
    decay<const int&> → int
    common_type<int, double> → double

  lesson6 (CRTP 응용 / Mixin):
    상속 받은 클래스에 컴파일 시점에 기능 주입

  lesson7 (정책 기반 설계):
    Logger<ConsolePolicy> vs Logger<FilePolicy>
    동일 인터페이스, 다른 출력 대상
=============================================================================
*/

// ============================================================================
int main() {
    cout << "========================================================\n";
    cout << "  21장: 고급 템플릿 & 메타프로그래밍\n";
    cout << "========================================================\n\n";

    lesson1::run();   // 특수화
    lesson2::run();   // SFINAE
    lesson3::run();   // 가변 인자
    lesson4::run();   // constexpr 메타
    lesson5::run();   // Type Traits
    lesson6::run();   // CRTP / Mixin
    lesson7::run();   // 정책 기반 설계
    exercises::run();

    cout << "========================================================\n";
    cout << "  학습 완료! 다음 단계:\n";
    cout << "  - Concepts (C++20)로 더 깔끔한 제약 조건 작성\n";
    cout << "  - Ranges 라이브러리와 템플릿의 결합\n";
    cout << "  - 실전 프로젝트에서 메타프로그래밍 활용\n";
    cout << "========================================================\n";
    return 0;
}
