/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  STL 학습 10단계: C++20 Ranges와 Views
  실행 방법: g++ -std=c++20 main.cpp -o main && ./main
  (C++20을 지원하는 컴파일러 필요: GCC 10+, Clang 13+, MSVC 19.29+)
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Ranges란?
  기존 STL 알고리즘을 더 간결하고 안전하게 쓸 수 있게 해주는 C++20 기능입니다.
  begin/end를 직접 쓸 필요 없이 컨테이너를 통째로 넘길 수 있습니다.

  Views란?
  데이터를 실제로 바꾸지 않고, "이렇게 보여줘"라는 필터/변환을 거는 것입니다.
  실제 계산은 결과를 사용할 때만 일어납니다 (lazy evaluation = 게으른 계산).

  비유:
  - 기존 STL = "이 상자의 시작과 끝을 알려줄게, 이 범위에서 찾아줘"
  - Ranges   = "이 상자에서 찾아줘" (더 간단!)
  - Views    = 인스타그램 필터처럼, 원본 사진은 그대로 두고
               "보여주는 방식"만 바꾸는 것.
===============================================================================
*/

#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <numeric>
#include <ranges>
using namespace std;

// ┌─────────────────────────────────────────────┐
// │  레슨 1: ranges 기본 — begin/end 없이!        │
// └─────────────────────────────────────────────┘
void lesson1_ranges_basics() {
    cout << "[레슨 1] ranges 기본 — 더 간결한 알고리즘" << endl;
    cout << endl;

    /*
      기존: sort(v.begin(), v.end());
      C++20: ranges::sort(v);

      비유: 예전에는 "이 줄의 처음부터 끝까지 정렬해"라고 했다면,
            이제는 "이거 정렬해"라고만 하면 됩니다.
    */

    vector<int> scores = {85, 92, 78, 95, 88, 65, 73};

    // 기존 방식
    // sort(scores.begin(), scores.end());

    // Ranges 방식 — 훨씬 깔끔!
    ranges::sort(scores);

    cout << "  정렬 결과: ";
    for (int s : scores) cout << s << " ";
    cout << endl;

    // ranges::find
    auto it = ranges::find(scores, 88);
    if (it != scores.end()) {
        cout << "  88점 찾음! (위치: " << distance(scores.begin(), it) << ")" << endl;
    }

    // ranges::count_if
    int high_count = ranges::count_if(scores, [](int s) { return s >= 90; });
    cout << "  90점 이상: " << high_count << "명" << endl;

    // ranges::min, ranges::max
    cout << "  최저: " << ranges::min(scores) << ", 최고: " << ranges::max(scores) << endl;

    // ranges::reverse
    ranges::reverse(scores);
    cout << "  역순:  ";
    for (int s : scores) cout << s << " ";
    cout << endl;
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 2: views::filter — 걸러보기             │
// └─────────────────────────────────────────────┘
void lesson2_views_filter() {
    cout << "[레슨 2] views::filter — 조건에 맞는 것만 보기" << endl;
    cout << endl;

    /*
      views::filter는 조건에 맞는 요소만 "보여 줍니다."
      원본 데이터는 전혀 바뀌지 않습니다!

      비유: 사진첩에서 "풍경 사진만 보기" 필터를 거는 것.
            사진을 지우는 게 아니라, 풍경 사진만 보이게 하는 것.
    */

    vector<int> scores = {92, 65, 78, 95, 88, 55, 73, 85};

    // 80점 이상만 보기
    cout << "  80점 이상만: ";
    for (int s : scores | views::filter([](int s) { return s >= 80; })) {
        cout << s << " ";
    }
    cout << endl;

    // 홀수만 보기
    cout << "  홀수만:     ";
    for (int s : scores | views::filter([](int s) { return s % 2 == 1; })) {
        cout << s << " ";
    }
    cout << endl;

    // 원본은 변하지 않음!
    cout << "  원본:       ";
    for (int s : scores) cout << s << " ";
    cout << endl;
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 3: views::transform — 변환해서 보기     │
// └─────────────────────────────────────────────┘
void lesson3_views_transform() {
    cout << "[레슨 3] views::transform — 바꿔서 보기" << endl;
    cout << endl;

    /*
      views::transform은 각 요소를 변환해서 "보여 줍니다."
      원본을 바꾸는 게 아니라, 변환된 모습만 보여주는 것입니다.

      비유: 모든 가격에 10% 할인을 적용한 가격표를 "보기만" 하는 것.
            실제 가격은 안 바뀌고, 계산된 가격만 화면에 보입니다.
    */

    vector<int> prices = {1000, 2000, 3000, 4500, 5000};

    // 10% 할인 가격으로 보기
    cout << "  원래 가격: ";
    for (int p : prices) cout << p << " ";
    cout << endl;

    cout << "  10% 할인: ";
    for (auto p : prices | views::transform([](int p) { return p * 0.9; })) {
        cout << p << " ";
    }
    cout << endl;

    // 문자열 길이로 변환
    vector<string> names = {"민수", "지우", "서연이", "하준"};
    cout << "  이름 길이: ";
    for (auto len : names | views::transform([](const string& s) { return s.size(); })) {
        cout << len << " ";
    }
    cout << endl;
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 4: 파이프(|) 연산자 — 체이닝             │
// └─────────────────────────────────────────────┘
void lesson4_pipe_chaining() {
    cout << "[레슨 4] 파이프(|) 연산자 — 여러 필터 연결하기" << endl;
    cout << endl;

    /*
      | (파이프) 연산자로 views를 줄줄이 연결할 수 있습니다.
      왼쪽 결과가 오른쪽의 입력이 됩니다.

      비유: 공장의 컨베이어 벨트!
            원재료 → 1단계(거르기) → 2단계(가공) → 3단계(포장)
            각 단계를 파이프(|)로 연결합니다.
    */

    vector<int> numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15};

    // 짝수만 골라서 → 3배로 → 처음 4개만
    cout << "  짝수 → 3배 → 처음 4개: ";
    for (int n : numbers
            | views::filter([](int n) { return n % 2 == 0; })
            | views::transform([](int n) { return n * 3; })
            | views::take(4)) {
        cout << n << " ";
    }
    cout << endl;
    // 2→6, 4→12, 6→18, 8→24
    cout << "  (2*3=6, 4*3=12, 6*3=18, 8*3=24)" << endl;
    cout << endl;

    // 학생 성적 처리 체이닝
    vector<int> scores = {92, 65, 78, 95, 88, 55, 73, 85, 97, 60};

    cout << "  80점 이상 상위 3명의 등급:" << endl;
    int rank_num = 1;
    for (auto score : scores
            | views::filter([](int s) { return s >= 80; })
            | views::take(5)) {
        string grade = score >= 95 ? "A+" :
                       score >= 90 ? "A" :
                       score >= 85 ? "B+" : "B";
        cout << "    " << rank_num++ << "등: " << score << "점 (" << grade << ")" << endl;
    }
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 5: views::take, drop, reverse           │
// └─────────────────────────────────────────────┘
void lesson5_take_drop_reverse() {
    cout << "[레슨 5] take, drop, reverse — 자르고 뒤집기" << endl;
    cout << endl;

    /*
      views::take(n)    = 처음 n개만 보기
      views::drop(n)    = 처음 n개를 건너뛰고 보기
      views::reverse    = 거꾸로 보기

      비유:
        take(3) = 줄에서 앞 3명만
        drop(3) = 줄에서 앞 3명 건너뛰기
        reverse = 줄을 뒤에서부터 보기
    */

    vector<int> nums = {10, 20, 30, 40, 50, 60, 70, 80};

    cout << "  원본:     ";
    for (int n : nums) cout << n << " ";
    cout << endl;

    cout << "  take(3):  ";
    for (int n : nums | views::take(3)) cout << n << " ";
    cout << endl;

    cout << "  drop(3):  ";
    for (int n : nums | views::drop(3)) cout << n << " ";
    cout << endl;

    cout << "  reverse:  ";
    for (int n : nums | views::reverse) cout << n << " ";
    cout << endl;

    // 조합: 뒤에서 3개만
    cout << "  뒤 3개:   ";
    for (int n : nums | views::reverse | views::take(3)) cout << n << " ";
    cout << endl;
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 6: views::iota — 숫자 생성기            │
// └─────────────────────────────────────────────┘
void lesson6_iota_and_generation() {
    cout << "[레슨 6] iota — 숫자 자동 생성" << endl;
    cout << endl;

    /*
      views::iota(시작) 또는 views::iota(시작, 끝)
      시작부터 1씩 증가하는 숫자를 생성합니다.

      비유: "1부터 100까지 세어 봐"를 코드 한 줄로!
    */

    // 1부터 10까지
    cout << "  1~10: ";
    for (int n : views::iota(1, 11)) {
        cout << n << " ";
    }
    cout << endl;

    // 1~20 중 3의 배수만
    cout << "  1~20 중 3의 배수: ";
    for (int n : views::iota(1, 21)
            | views::filter([](int n) { return n % 3 == 0; })) {
        cout << n << " ";
    }
    cout << endl;

    // 구구단 5단 (iota + transform)
    cout << "  5단: ";
    for (auto result : views::iota(1, 10)
            | views::transform([](int n) { return 5 * n; })) {
        cout << result << " ";
    }
    cout << endl;
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 7: Lazy Evaluation — 게으른 계산         │
// └─────────────────────────────────────────────┘
void lesson7_lazy_evaluation() {
    cout << "[레슨 7] Lazy Evaluation — 필요할 때만 계산" << endl;
    cout << endl;

    /*
      Views의 가장 큰 장점: "게으른 계산" (Lazy Evaluation)
      모든 데이터를 미리 처리하지 않고, 실제로 사용할 때만 계산합니다.

      비유: 뷔페에서 모든 음식을 접시에 담아오는 게 아니라,
            먹고 싶을 때 하나씩 가져오는 것.

      장점:
        1) 메모리를 적게 씀 (중간 결과를 저장하지 않으니까)
        2) 필요한 만큼만 계산 (take(3)이면 3개만 계산하고 멈춤)
    */

    // 이 코드는 1부터 무한히 세지만, take(5)이므로 5개만 계산합니다!
    cout << "  무한 수열에서 짝수 5개: ";
    for (int n : views::iota(1)
            | views::filter([](int n) { return n % 2 == 0; })
            | views::take(5)) {
        cout << n << " ";
    }
    cout << endl;
    // 2 4 6 8 10 — 무한 수열인데도 5개에서 멈춤!

    // 기존 방식이면 전부 계산한 뒤에 5개를 골라야 했을 것.
    // Views는 5개를 찾는 순간 멈추므로 훨씬 효율적입니다.

    // 피보나치 없이 제곱수 중 100 이하인 것만 보기
    cout << "  100 이하 제곱수: ";
    for (int n : views::iota(1)
            | views::transform([](int n) { return n * n; })
            | views::take_while([](int n) { return n <= 100; })) {
        cout << n << " ";
    }
    cout << endl;
    // 1 4 9 16 25 36 49 64 81 100
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 8: 종합 예제 — 성적 처리 파이프라인       │
// └─────────────────────────────────────────────┘
void lesson8_comprehensive_example() {
    cout << "[레슨 8] 종합 — 성적 처리 파이프라인" << endl;
    cout << endl;

    struct Student {
        string name;
        int score;
    };

    vector<Student> students = {
        {"민수", 92}, {"지우", 65}, {"서연", 97}, {"하준", 78},
        {"유나", 88}, {"도윤", 55}, {"소율", 95}, {"시우", 73}
    };

    // 합격자(70점 이상)의 이름만 뽑아서 출력
    cout << "  합격자 명단:" << endl;
    for (const auto& name : students
            | views::filter([](const Student& s) { return s.score >= 70; })
            | views::transform([](const Student& s) { return s.name + " (" + to_string(s.score) + "점)"; })) {
        cout << "    - " << name << endl;
    }
    cout << endl;

    // 상위 3명 (먼저 정렬 필요 — ranges::sort)
    ranges::sort(students, [](const Student& a, const Student& b) {
        return a.score > b.score;  // 내림차순
    });

    cout << "  상위 3명:" << endl;
    int rank = 1;
    for (const auto& s : students | views::take(3)) {
        cout << "    " << rank++ << "등: " << s.name << " (" << s.score << "점)" << endl;
    }
    cout << endl;
}

int main() {
    cout << "============================================================" << endl;
    cout << "  STL 10단계 : C++20 Ranges와 Views" << endl;
    cout << "============================================================" << endl;
    cout << endl;

    lesson1_ranges_basics();
    lesson2_views_filter();
    lesson3_views_transform();
    lesson4_pipe_chaining();
    lesson5_take_drop_reverse();
    lesson6_iota_and_generation();
    lesson7_lazy_evaluation();
    lesson8_comprehensive_example();

    return 0;
}
