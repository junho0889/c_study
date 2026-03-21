/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  STL 학습 07단계: 함수형 프로그래밍 도구들
  실행 방법: g++ -std=c++17 main.cpp -o main && ./main
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  std::function = 함수를 변수에 담는 상자
  lambda        = 이름 없는 즉석 함수 (그 자리에서 바로 만들기)
  std::bind     = 함수의 매개변수를 미리 채워두기
  std::invoke   = 어떤 종류의 함수든 통일된 방법으로 호출하기

  비유:
  - function = 여러 종류의 리모컨을 꽂을 수 있는 만능 슬롯
  - lambda   = 급하게 손으로 쓴 메모 쪽지 (한 번 쓰고 바로 사용)
  - bind     = "이 번호는 자동 입력" 같은 단축 다이얼
  - invoke   = "이거 실행해 줘" 하면 종류에 관계없이 실행하는 비서
===============================================================================
*/

#include <iostream>
#include <functional>
#include <vector>
#include <algorithm>
#include <string>
#include <numeric>
using namespace std;

// ┌─────────────────────────────────────────────┐
// │  레슨 1: lambda 기본 — 이름 없는 함수          │
// └─────────────────────────────────────────────┘
void lesson1_lambda_basics() {
    cout << "[레슨 1] lambda 기본 — 즉석에서 함수 만들기" << endl;
    cout << endl;

    /*
      lambda 문법:
        [캡처](매개변수) -> 반환타입 { 본문 }

      비유: 메모지에 "이 숫자에 2를 곱해서 돌려줘"라고 적어서
            바로 사용하는 것. 함수 이름을 따로 지을 필요가 없어요.
    */

    // 가장 간단한 lambda
    auto greet = []() {
        cout << "  안녕하세요!" << endl;
    };
    greet();  // 함수처럼 호출

    // 매개변수가 있는 lambda
    auto add = [](int a, int b) -> int {
        return a + b;
    };
    cout << "  3 + 5 = " << add(3, 5) << endl;

    // 반환 타입은 보통 생략 가능 (컴파일러가 알아냄)
    auto multiply = [](int a, int b) { return a * b; };
    cout << "  4 * 7 = " << multiply(4, 7) << endl;

    // STL 알고리즘과 함께 사용
    vector<int> scores = {85, 92, 78, 95, 88};
    int count_high = count_if(scores.begin(), scores.end(),
        [](int s) { return s >= 90; });
    cout << "  90점 이상: " << count_high << "명" << endl;
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 2: lambda 캡처 — 바깥 변수 가져오기      │
// └─────────────────────────────────────────────┘
void lesson2_lambda_capture() {
    cout << "[레슨 2] lambda 캡처 — 바깥 변수 사용하기" << endl;
    cout << endl;

    /*
      캡처(capture)란?
      lambda 바깥에 있는 변수를 lambda 안에서 쓸 수 있게 하는 것입니다.

      [=]  = 바깥 변수를 전부 복사해서 가져옴 (읽기만 가능)
      [&]  = 바깥 변수를 전부 참조로 가져옴 (수정 가능)
      [x]  = x만 복사
      [&x] = x만 참조
      [=, &y] = 전부 복사, y만 참조

      비유: 교실 밖 칠판의 내용을
        [=] = 공책에 옮겨 적기 (원본 안 바뀜)
        [&] = 칠판을 직접 보면서 고치기 (원본 바뀜)
    */

    int pass_score = 80;
    int fail_count = 0;

    vector<int> scores = {92, 65, 78, 88, 55, 95};

    // [=] 복사 캡처: pass_score를 읽기만
    auto is_pass = [=](int s) { return s >= pass_score; };

    // [&] 참조 캡처: fail_count를 수정
    for_each(scores.begin(), scores.end(), [&](int s) {
        if (s < pass_score) {
            fail_count++;
            cout << "  " << s << "점: 불합격" << endl;
        }
    });
    cout << "  총 불합격자: " << fail_count << "명" << endl;
    cout << endl;

    // 개별 캡처
    string class_name = "1반";
    auto print_score = [class_name, pass_score](int s) {
        cout << "  " << class_name << " 학생 " << s << "점 → "
             << (s >= pass_score ? "합격" : "불합격") << endl;
    };
    print_score(75);
    print_score(92);
    cout << endl;

    // mutable: 복사 캡처한 값을 lambda 안에서 수정 (원본은 안 바뀜)
    int counter = 0;
    auto increment = [counter]() mutable {
        counter++;
        cout << "  lambda 안의 counter: " << counter << endl;
    };
    increment();
    increment();
    cout << "  lambda 밖의 counter: " << counter << " (안 바뀜!)" << endl;
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 3: std::function — 함수를 변수에 담기    │
// └─────────────────────────────────────────────┘

// 일반 함수
int subtract(int a, int b) { return a - b; }

// 함수 객체 (functor)
struct Divider {
    double operator()(double a, double b) const {
        return b != 0 ? a / b : 0;
    }
};

void lesson3_std_function() {
    cout << "[레슨 3] std::function — 만능 함수 담기 상자" << endl;
    cout << endl;

    /*
      std::function<반환타입(매개변수들)>은
      일반 함수, lambda, 함수 객체 등 "무엇이든" 담을 수 있습니다.

      비유: USB 포트처럼, 키보드든 마우스든 USB 규격이면 다 꽂을 수 있듯이
            function은 "호출 규격"만 맞으면 무엇이든 담습니다.
    */

    // 일반 함수 담기
    function<int(int, int)> op1 = subtract;
    cout << "  일반 함수: 10 - 3 = " << op1(10, 3) << endl;

    // lambda 담기
    function<int(int, int)> op2 = [](int a, int b) { return a + b; };
    cout << "  lambda:    10 + 3 = " << op2(10, 3) << endl;

    // 함수 객체 담기
    function<double(double, double)> op3 = Divider();
    cout << "  functor:   10 / 3 = " << op3(10.0, 3.0) << endl;
    cout << endl;

    // function을 벡터에 담아서 순서대로 실행
    vector<function<int(int, int)>> operations = {
        [](int a, int b) { return a + b; },
        [](int a, int b) { return a - b; },
        [](int a, int b) { return a * b; },
    };

    vector<string> op_names = {"+", "-", "*"};
    for (size_t i = 0; i < operations.size(); i++) {
        cout << "  5 " << op_names[i] << " 3 = " << operations[i](5, 3) << endl;
    }
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 4: std::bind — 매개변수 미리 채우기      │
// └─────────────────────────────────────────────┘
void greet_student(const string& greeting, const string& name, int score) {
    cout << "  " << greeting << " " << name << "! (" << score << "점)" << endl;
}

void lesson4_bind() {
    cout << "[레슨 4] std::bind — 매개변수 미리 채우기" << endl;
    cout << endl;

    /*
      bind는 함수의 일부 매개변수를 미리 고정하고,
      나머지만 나중에 받는 새 함수를 만듭니다.

      비유: "안녕, ___야!" 에서 "안녕"은 미리 적어놓고
            이름만 나중에 채우는 빈칸 편지.

      placeholders::_1 = "이 자리는 나중에 받을 첫 번째 값"
      placeholders::_2 = "이 자리는 나중에 받을 두 번째 값"
    */

    using namespace placeholders;

    // greeting을 "안녕하세요"로 고정, 나머지는 나중에
    auto korean_greet = bind(greet_student, "안녕하세요", _1, _2);
    korean_greet("민수", 92);
    korean_greet("지우", 85);

    // greeting과 name을 모두 고정, score만 나중에
    auto minsu_greet = bind(greet_student, "축하해요", "민수", _1);
    minsu_greet(100);  // score만 전달

    cout << endl;

    // 참고: 요즘은 bind 대신 lambda를 더 많이 씁니다.
    // 위의 korean_greet를 lambda로 쓰면:
    auto korean_greet_v2 = [](const string& name, int score) {
        greet_student("안녕하세요", name, score);
    };
    korean_greet_v2("서연", 97);
    cout << "  (lambda가 더 읽기 쉽죠?)" << endl;
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 5: std::invoke — 통일된 호출             │
// └─────────────────────────────────────────────┘
class Calculator {
public:
    int value = 10;
    int add(int x) const { return value + x; }
};

void lesson5_invoke() {
    cout << "[레슨 5] std::invoke — 무엇이든 호출하기" << endl;
    cout << endl;

    /*
      std::invoke는 함수, lambda, 멤버 함수, 멤버 변수 등
      "호출 가능한 모든 것"을 같은 방법으로 호출합니다.

      비유: 리모컨 종류(TV, 에어컨, 선풍기)에 관계없이
            "전원 버튼 눌러 줘"라고 하면 알아서 눌러주는 만능 비서.
    */

    // 일반 함수 호출
    auto result1 = invoke(subtract, 10, 3);
    cout << "  일반 함수: " << result1 << endl;

    // lambda 호출
    auto result2 = invoke([](int x) { return x * x; }, 5);
    cout << "  lambda: " << result2 << endl;

    // 멤버 함수 호출
    Calculator calc;
    auto result3 = invoke(&Calculator::add, calc, 5);
    cout << "  멤버 함수: " << result3 << endl;

    // 멤버 변수 접근
    auto result4 = invoke(&Calculator::value, calc);
    cout << "  멤버 변수: " << result4 << endl;
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 6: 고차 함수 — 함수를 받거나 돌려주기    │
// └─────────────────────────────────────────────┘

// 함수를 매개변수로 받는 고차 함수
void apply_to_scores(const vector<int>& scores,
                     const function<void(int)>& action) {
    for (int s : scores) {
        action(s);
    }
}

// 함수를 돌려주는 고차 함수
function<bool(int)> make_threshold_checker(int threshold) {
    return [threshold](int value) {
        return value >= threshold;
    };
}

void lesson6_higher_order() {
    cout << "[레슨 6] 고차 함수 — 함수를 주고받기" << endl;
    cout << endl;

    /*
      고차 함수(Higher-Order Function)란?
      함수를 매개변수로 받거나, 함수를 반환하는 함수입니다.

      비유: "선생님, 이 규칙(함수)으로 채점해 주세요"처럼
            규칙 자체를 넘기는 것.
    */

    vector<int> scores = {85, 92, 78, 95, 65, 88};

    // 함수를 넘겨서 각 점수에 적용
    cout << "  각 점수 출력:" << endl;
    apply_to_scores(scores, [](int s) {
        cout << "    " << s << "점" << endl;
    });
    cout << endl;

    // 함수를 만들어서 돌려받기
    auto is_pass = make_threshold_checker(80);
    auto is_excellent = make_threshold_checker(90);

    cout << "  합격 여부 (80점 기준):" << endl;
    for (int s : scores) {
        cout << "    " << s << "점 → " << (is_pass(s) ? "합격" : "불합격") << endl;
    }
    cout << endl;

    // accumulate와 lambda로 합계/최대값 구하기
    int sum = accumulate(scores.begin(), scores.end(), 0);
    int max_score = accumulate(scores.begin(), scores.end(), 0,
        [](int a, int b) { return a > b ? a : b; });

    cout << "  합계: " << sum << ", 최고점: " << max_score << endl;
    cout << endl;
}

int main() {
    cout << "============================================================" << endl;
    cout << "  STL 07단계 : function, lambda, bind, invoke" << endl;
    cout << "============================================================" << endl;
    cout << endl;

    lesson1_lambda_basics();
    lesson2_lambda_capture();
    lesson3_std_function();
    lesson4_bind();
    lesson5_invoke();
    lesson6_higher_order();

    return 0;
}
