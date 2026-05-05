/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C++ 학습 16단계: 테스트와 TDD
  ─ 단위 테스트, 테스트 프레임워크, TDD 패턴 ─

  "테스트 없는 코드는 레거시 코드다" — Michael Feathers

  이 파일에서는 Google Test 없이 테스트 개념을 직접 구현하며 배우고,
  실무 프레임워크 사용법을 가이드합니다.

  ■ 컴파일: g++ -std=c++17 -Wall -o 16_test main.cpp

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/
#include <iostream>
#include <string>
#include <vector>
#include <cmath>
#include <functional>
#include <stdexcept>
#include <sstream>
using namespace std;


// =========================================================================
//  미니 테스트 프레임워크 (학습용으로 직접 만들기!)
// =========================================================================
//
//  실무에서는 Google Test, Catch2, doctest 등을 쓰지만,
//  원리를 이해하기 위해 직접 만들어봅니다.

class TestRunner {
    int total_ = 0;
    int passed_ = 0;
    int failed_ = 0;
    vector<string> failures_;

public:
    // 같은지 확인
    template <typename T>
    void assert_eq(T actual, T expected, const string& name) {
        total_++;
        if (actual == expected) {
            passed_++;
            cout << "    [PASS] " << name << "\n";
        } else {
            failed_++;
            ostringstream oss;
            oss << name << " : expected=" << expected
                << ", actual=" << actual;
            failures_.push_back(oss.str());
            cout << "    [FAIL] " << oss.str() << "\n";
        }
    }

    // 참인지 확인
    void assert_true(bool condition, const string& name) {
        total_++;
        if (condition) {
            passed_++;
            cout << "    [PASS] " << name << "\n";
        } else {
            failed_++;
            failures_.push_back(name + " : expected true but got false");
            cout << "    [FAIL] " << name << "\n";
        }
    }

    // 거짓인지 확인
    void assert_false(bool condition, const string& name) {
        assert_true(!condition, name);
    }

    // 예외가 발생하는지 확인
    template <typename ExcType>
    void assert_throws(function<void()> func, const string& name) {
        total_++;
        try {
            func();
            failed_++;
            failures_.push_back(name + " : no exception thrown");
            cout << "    [FAIL] " << name << " (예외 없음)\n";
        } catch (const ExcType&) {
            passed_++;
            cout << "    [PASS] " << name << "\n";
        } catch (...) {
            failed_++;
            failures_.push_back(name + " : wrong exception type");
            cout << "    [FAIL] " << name << " (다른 예외)\n";
        }
    }

    // 실수 비교 (오차 범위)
    void assert_near(double actual, double expected,
                     double epsilon, const string& name) {
        total_++;
        if (abs(actual - expected) < epsilon) {
            passed_++;
            cout << "    [PASS] " << name << "\n";
        } else {
            failed_++;
            ostringstream oss;
            oss << name << " : expected~" << expected
                << ", actual=" << actual << ", eps=" << epsilon;
            failures_.push_back(oss.str());
            cout << "    [FAIL] " << oss.str() << "\n";
        }
    }

    // 결과 요약
    void summary() const {
        cout << "\n  ═══════════════════════════════════\n";
        cout << "  테스트 결과: " << total_ << "개 중 "
             << passed_ << "개 통과, "
             << failed_ << "개 실패\n";
        if (failed_ > 0) {
            cout << "\n  실패 목록:\n";
            for (const auto& f : failures_) {
                cout << "    - " << f << "\n";
            }
        }
        cout << "  ═══════════════════════════════════\n";
    }
};


// =========================================================================
//  테스트 대상 코드 (이 코드를 테스트합니다)
// =========================================================================

// 간단한 계산기
class Calculator {
public:
    static int add(int a, int b) { return a + b; }
    static int sub(int a, int b) { return a - b; }
    static int mul(int a, int b) { return a * b; }

    static double div(int a, int b) {
        if (b == 0) throw invalid_argument("0으로 나눌 수 없습니다");
        return static_cast<double>(a) / b;
    }
};

// 문자열 유틸리티
class StringUtils {
public:
    static string to_upper(const string& s) {
        string result = s;
        for (char& c : result) {
            if (c >= 'a' && c <= 'z') c -= 32;
        }
        return result;
    }

    static string trim(const string& s) {
        size_t start = s.find_first_not_of(" \t\n");
        size_t end = s.find_last_not_of(" \t\n");
        if (start == string::npos) return "";
        return s.substr(start, end - start + 1);
    }

    static bool starts_with(const string& s, const string& prefix) {
        if (prefix.size() > s.size()) return false;
        return s.compare(0, prefix.size(), prefix) == 0;
    }

    static vector<string> split(const string& s, char delim) {
        vector<string> tokens;
        istringstream iss(s);
        string token;
        while (getline(iss, token, delim)) {
            tokens.push_back(token);
        }
        return tokens;
    }
};

// 스택 자료구조
class IntStack {
    vector<int> data_;
public:
    void push(int val) { data_.push_back(val); }

    int pop() {
        if (data_.empty()) throw runtime_error("스택이 비어있습니다");
        int val = data_.back();
        data_.pop_back();
        return val;
    }

    int top() const {
        if (data_.empty()) throw runtime_error("스택이 비어있습니다");
        return data_.back();
    }

    bool empty() const { return data_.empty(); }
    size_t size() const { return data_.size(); }
};


// =========================================================================
//  main — 테스트 실행
// =========================================================================
int main() {
    cout << "========================================\n";
    cout << "  C++ 16단계 : 테스트와 TDD\n";
    cout << "========================================\n\n";

    TestRunner test;

    // ─── Calculator 테스트 ───
    cout << "  ■ Calculator 테스트\n";
    cout << "  ─────────────────────────────────────\n";

    test.assert_eq(Calculator::add(2, 3), 5, "2 + 3 = 5");
    // → add(2,3)=5, expected=5 → PASS. total=1, passed=1
    // > 출력:   [PASS] 2 + 3 = 5
    test.assert_eq(Calculator::add(-1, 1), 0, "-1 + 1 = 0");
    // → 0=0 → PASS. total=2, passed=2
    test.assert_eq(Calculator::add(0, 0), 0, "0 + 0 = 0");
    test.assert_eq(Calculator::sub(10, 3), 7, "10 - 3 = 7");
    test.assert_eq(Calculator::mul(4, 5), 20, "4 * 5 = 20");
    test.assert_eq(Calculator::mul(-2, 3), -6, "-2 * 3 = -6");
    test.assert_near(Calculator::div(10, 3), 3.333, 0.01, "10 / 3 ~ 3.33");
    // → div(10,3) = 3.33333..., |3.333-3.33333| = 0.00033 < 0.01 → PASS
    test.assert_throws<invalid_argument>(
        []() { Calculator::div(10, 0); }, "10 / 0 예외 발생");
    // → div(10, 0) → invalid_argument throw → 매치 → PASS
    // > 출력 (이 8개):
    //   [PASS] 2 + 3 = 5
    //   [PASS] -1 + 1 = 0
    //   [PASS] 0 + 0 = 0
    //   [PASS] 10 - 3 = 7
    //   [PASS] 4 * 5 = 20
    //   [PASS] -2 * 3 = -6
    //   [PASS] 10 / 3 ~ 3.33
    //   [PASS] 10 / 0 예외 발생

    cout << endl;

    // ─── StringUtils 테스트 ───
    cout << "  ■ StringUtils 테스트\n";
    cout << "  ─────────────────────────────────────\n";

    test.assert_eq(StringUtils::to_upper("hello"), string("HELLO"), "to_upper");
    // → to_upper("hello")="HELLO" → PASS
    test.assert_eq(StringUtils::to_upper("Hello123"), string("HELLO123"), "to_upper mixed");
    // → "HELLO123" (숫자는 -32 적용 안 됨, 'h'~'z'만)
    test.assert_eq(StringUtils::trim("  hello  "), string("hello"), "trim");
    // → trim 결과 "hello" (좌우 공백 제거)
    test.assert_eq(StringUtils::trim(""), string(""), "trim empty");
    // → 빈 문자열 → "" 반환 → PASS
    test.assert_true(StringUtils::starts_with("hello world", "hello"), "starts_with true");
    // → 처음 5글자가 "hello" → true → PASS
    test.assert_false(StringUtils::starts_with("hello", "world"), "starts_with false");
    // → "hello"는 "world"로 시작 안 함 → false 받아 assert_false 통과

    auto parts = StringUtils::split("a,b,c", ',');
    // → parts = ["a", "b", "c"], size=3
    test.assert_eq(parts.size(), (size_t)3, "split count");
    test.assert_eq(parts[0], string("a"), "split first");
    test.assert_eq(parts[2], string("c"), "split last");
    // > 출력 (이 9개): 모두 PASS

    cout << endl;

    // ─── IntStack 테스트 ───
    cout << "  ■ IntStack 테스트\n";
    cout << "  ─────────────────────────────────────\n";

    IntStack stack;
    // → data_=[]
    test.assert_true(stack.empty(), "새 스택은 비어있음");
    // → empty()=true → PASS
    test.assert_eq(stack.size(), (size_t)0, "크기 0");

    stack.push(10);   // → data_=[10]
    stack.push(20);   // → data_=[10, 20]
    stack.push(30);   // → data_=[10, 20, 30]
    test.assert_eq(stack.size(), (size_t)3, "push 3개 후 크기");
    test.assert_eq(stack.top(), 30, "top = 30");
    // → top = data_.back() = 30
    test.assert_eq(stack.pop(), 30, "pop = 30");
    // → pop_back, data_=[10,20], 반환 30
    test.assert_eq(stack.pop(), 20, "pop = 20");
    // → data_=[10], 반환 20
    test.assert_eq(stack.size(), (size_t)1, "pop 2개 후 크기");

    stack.pop();
    // → data_=[], 반환 10 (사용 안 함)
    test.assert_true(stack.empty(), "전부 pop 후 비어있음");
    test.assert_throws<runtime_error>(
        [&stack]() { stack.pop(); }, "빈 스택 pop 예외");
    // → 빈 상태 pop → throw runtime_error → 매치 → PASS
    test.assert_throws<runtime_error>(
        [&stack]() { stack.top(); }, "빈 스택 top 예외");
    // → 같은 이유 PASS
    // > 결과:  총 11개 모두 PASS

    // ─── 결과 요약 ───
    test.summary();
    // → total=28, passed=28, failed=0 (이상의 모든 테스트 통과)
    // > 출력:
    //   ═══════════════════════════════════
    //   테스트 결과: 28개 중 28개 통과, 0개 실패
    //   ═══════════════════════════════════

    // ─── TDD 가이드 ───
    cout << R"(

  ■ TDD (Test-Driven Development) 사이클
  ─────────────────────────────────────
      ┌──────────┐
      │ 1. RED   │  실패하는 테스트를 먼저 작성
      └────┬─────┘
           ↓
      ┌──────────┐
      │ 2. GREEN │  테스트를 통과하는 최소한의 코드 작성
      └────┬─────┘
           ↓
      ┌──────────────┐
      │ 3. REFACTOR  │  코드를 깔끔하게 정리 (테스트는 계속 통과)
      └──────┬───────┘
             ↓
         1번으로 돌아감

  ■ Google Test 사용법 (실무)
  ─────────────────────────────────────
  // CMakeLists.txt
  find_package(GTest REQUIRED)
  add_executable(tests test_main.cpp)
  target_link_libraries(tests GTest::gtest_main)
  add_test(NAME unit_tests COMMAND tests)

  // test_main.cpp
  #include <gtest/gtest.h>

  TEST(Calculator, Add) {
      EXPECT_EQ(add(2, 3), 5);
      EXPECT_EQ(add(-1, 1), 0);
  }

  TEST(Calculator, DivByZero) {
      EXPECT_THROW(div(10, 0), invalid_argument);
  }

  // 실행: ctest  또는  ./tests
)" << endl;

    cout << "16단계 학습 완료!\n";
    return 0;
}
