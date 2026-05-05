/*
=============================================================================
  C++ 학습 07단계: 템플릿과 STL (표준 라이브러리)
=============================================================================
  [컴파일] g++ -std=c++17 -o 07_stl main.cpp
  [주석 표기] // > 출력  // → 변수값  // ▶ 흐름
=============================================================================
*/
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <unordered_map>
#include <algorithm>
#include <numeric>
using namespace std;

void lesson1_templates();
void lesson2_vector();
void lesson3_map();
void lesson4_set();
void lesson5_algorithms();

int main() {
    cout << "========================================\n";
    cout << "  C++ 07단계 : 템플릿과 STL\n";
    cout << "========================================\n\n";

    lesson1_templates();
    lesson2_vector();
    lesson3_map();
    lesson4_set();
    lesson5_algorithms();

    cout << "\n07단계 학습 완료!\n";
    return 0;
}


// =====================================================================
// 레슨 1 — 템플릿
// =====================================================================
template <typename T>
T my_max(T a, T b) {
    return (a > b) ? a : b;
}

template <typename T>
class Box {
    T value_;
public:
    Box(T val) : value_(val) {}
    T get() const { return value_; }
    void set(T val) { value_ = val; }
};

void lesson1_templates() {
    cout << "[레슨 1] 템플릿\n\n";

    cout << "  max(3, 7)     = " << my_max(3, 7) << "\n";
    // → my_max<int>(3, 7) → (3 > 7) false → 7
    // > 출력:   max(3, 7)     = 7

    cout << "  max(3.5, 2.1) = " << my_max(3.5, 2.1) << "\n";
    // → my_max<double>(3.5, 2.1) → (3.5 > 2.1) true → 3.5
    // > 출력:   max(3.5, 2.1) = 3.5

    cout << "  max 타입 명시 = " << my_max<int>(3, 7) << "\n\n";
    // → 명시적 인스턴스화. 결과 동일.
    // > 출력:   max 타입 명시 = 7

    Box<int>    int_box(42);
    // → Box<int> 인스턴스. value_ = 42.
    Box<string> str_box("Hello");
    // → Box<string> 인스턴스. value_ = "Hello".

    cout << "  Box<int>    = " << int_box.get() << "\n";
    // > 출력:   Box<int>    = 42
    cout << "  Box<string> = " << str_box.get() << "\n";
    // > 출력:   Box<string> = Hello
    cout << endl;
}


// =====================================================================
// 레슨 2 — vector (동적 배열)
// =====================================================================
void lesson2_vector() {
    cout << "[레슨 2] vector (동적 배열)\n\n";

    vector<int> nums;
    // → 빈 vector. size=0, capacity=0
    vector<int> scores = {95, 82, 71, 88};
    // → size=4, 내용 [95, 82, 71, 88]
    vector<int> zeros(5, 0);
    // → size=5, 내용 [0, 0, 0, 0, 0]
    (void)scores; (void)zeros;

    nums.push_back(10);     // → nums = [10]
    nums.push_back(20);     // → nums = [10, 20]
    nums.push_back(30);     // → nums = [10, 20, 30]

    cout << "  --- 순회 방법 ---\n";

    cout << "  인덱스:  ";
    for (size_t i = 0; i < nums.size(); i++) {
        // i: 0, 1, 2 → nums[i]: 10, 20, 30
        cout << nums[i] << " ";
    }
    cout << "\n";
    // > 출력:   인덱스:  10 20 30

    cout << "  범위for: ";
    for (int n : nums) {
        // n: 10, 20, 30
        cout << n << " ";
    }
    cout << "\n";
    // > 출력:   범위for: 10 20 30

    cout << "  iterator: ";
    for (auto it = nums.begin(); it != nums.end(); ++it) {
        // *it: 10, 20, 30
        cout << *it << " ";
    }
    cout << "\n\n";
    // > 출력:   iterator: 10 20 30

    cout << "  크기:   " << nums.size() << "\n";
    // > 출력:   크기:   3
    cout << "  첫번째: " << nums.front() << "\n";
    // > 출력:   첫번째: 10
    cout << "  마지막: " << nums.back() << "\n";
    // > 출력:   마지막: 30

    nums.pop_back();
    // → nums = [10, 20] (size=2)
    cout << "  pop 후: ";
    for (int n : nums) cout << n << " ";
    cout << "\n";
    // > 출력:   pop 후: 10 20

    cout << "\n  --- 2차원 vector ---\n";
    vector<vector<int>> matrix = {
        {1, 2, 3},
        {4, 5, 6}
    };
    for (const auto& row : matrix) {
        // row: [1,2,3] → [4,5,6]
        cout << "  ";
        for (int val : row) cout << val << " ";
        cout << "\n";
    }
    // > 출력:
    //   1 2 3
    //   4 5 6
    cout << endl;
}


// =====================================================================
// 레슨 3 — map (키-값 쌍)
// =====================================================================
void lesson3_map() {
    cout << "[레슨 3] map (키-값 저장소)\n\n";

    map<string, int> ages;
    ages["홍길동"] = 25;
    ages["김철수"] = 30;
    ages["이영희"] = 22;
    ages.insert({"박지민", 28});
    // → map은 키 사전순 자동 정렬:
    //   "김철수":30, "박지민":28, "이영희":22, "홍길동":25
    //   (한글 사전순은 유니코드 코드포인트 비교)

    cout << "  --- map (정렬됨) ---\n";
    for (const auto& [name, age] : ages) {
        cout << "  " << name << " : " << age << "세\n";
    }
    // > 출력 (정렬 순서):
    //   김철수 : 30세
    //   박지민 : 28세
    //   이영희 : 22세
    //   홍길동 : 25세

    cout << "\n  홍길동 나이: " << ages["홍길동"] << "\n";
    // > 출력:   홍길동 나이: 25

    if (ages.count("김철수")) {
        // → count = 1 (존재)
        cout << "  김철수 존재함\n";
        // > 출력:   김철수 존재함
    }
    if (ages.find("없는사람") == ages.end()) {
        // → find가 end() 반환 → 미존재
        cout << "  없는사람 없음\n";
        // > 출력:   없는사람 없음
    }

    ages.erase("이영희");
    // → 이영희 제거. size: 4 → 3
    cout << "  삭제 후 크기: " << ages.size() << "\n";
    // > 출력:   삭제 후 크기: 3

    cout << "\n  --- unordered_map ---\n";
    unordered_map<string, string> capitals;
    capitals["한국"] = "서울";
    capitals["일본"] = "도쿄";
    capitals["미국"] = "워싱턴";
    // → 해시 테이블. 순서 정해지지 않음 (실행마다 다를 수 있음)

    for (const auto& [country, capital] : capitals) {
        cout << "  " << country << " → " << capital << "\n";
    }
    // > 출력 예 (순서는 비결정적):
    //   한국 → 서울
    //   미국 → 워싱턴
    //   일본 → 도쿄
    cout << endl;
}


// =====================================================================
// 레슨 4 — set
// =====================================================================
void lesson4_set() {
    cout << "[레슨 4] set (집합)\n\n";

    set<int> numbers = {5, 3, 8, 1, 3, 5};
    // → 중복 제거 + 자동 정렬 → {1, 3, 5, 8}

    cout << "  set (중복 제거 + 정렬): ";
    for (int n : numbers) {
        cout << n << " ";
    }
    cout << "\n";
    // > 출력:   set (중복 제거 + 정렬): 1 3 5 8

    numbers.insert(4);   // → {1, 3, 4, 5, 8}
    numbers.insert(3);   // → 이미 존재 → 무시. {1, 3, 4, 5, 8}

    cout << "  insert(4,3) 후: ";
    for (int n : numbers) cout << n << " ";
    cout << "\n";
    // > 출력:   insert(4,3) 후: 1 3 4 5 8

    cout << "  3이 있나? " << (numbers.count(3) ? "있음" : "없음") << "\n";
    // → count(3) = 1 → "있음"
    // > 출력:   3이 있나? 있음

    cout << "  9가 있나? " << (numbers.count(9) ? "있음" : "없음") << "\n";
    // → count(9) = 0 → "없음"
    // > 출력:   9가 있나? 없음
    cout << endl;
}


// =====================================================================
// 레슨 5 — STL 알고리즘
// =====================================================================
void lesson5_algorithms() {
    cout << "[레슨 5] STL 알고리즘\n\n";

    vector<int> v = {5, 2, 8, 1, 9, 3, 7, 4, 6};
    // → 초기: [5, 2, 8, 1, 9, 3, 7, 4, 6]

    sort(v.begin(), v.end());
    // → [1, 2, 3, 4, 5, 6, 7, 8, 9]
    cout << "  오름차순: ";
    for (int n : v) cout << n << " ";
    cout << "\n";
    // > 출력:   오름차순: 1 2 3 4 5 6 7 8 9

    sort(v.begin(), v.end(), greater<int>());
    // → [9, 8, 7, 6, 5, 4, 3, 2, 1]
    cout << "  내림차순: ";
    for (int n : v) cout << n << " ";
    cout << "\n";
    // > 출력:   내림차순: 9 8 7 6 5 4 3 2 1

    sort(v.begin(), v.end(), [](int a, int b) {
        return a < b;
    });
    // → 다시 오름차순: [1, 2, 3, 4, 5, 6, 7, 8, 9]

    auto it = find(v.begin(), v.end(), 5);
    // → 5의 iterator. v[4]를 가리킴. (it - begin) = 4
    if (it != v.end()) {
        cout << "  5 찾음! 위치: " << (it - v.begin()) << "\n";
        // > 출력:   5 찾음! 위치: 4
    }

    vector<int> data = {1, 2, 3, 2, 1, 2, 3};
    cout << "  2의 개수: " << count(data.begin(), data.end(), 2) << "\n";
    // → 2가 등장: index 1, 3, 5 → 3개
    // > 출력:   2의 개수: 3

    auto min_it = min_element(v.begin(), v.end());     // → *min_it = 1
    auto max_it = max_element(v.begin(), v.end());     // → *max_it = 9
    cout << "  최소: " << *min_it << "  최대: " << *max_it << "\n";
    // > 출력:   최소: 1  최대: 9

    int sum = accumulate(v.begin(), v.end(), 0);
    // → 0 + 1+2+3+4+5+6+7+8+9 = 45
    cout << "  합계: " << sum << "\n";
    // > 출력:   합계: 45

    reverse(v.begin(), v.end());
    // → [9, 8, 7, 6, 5, 4, 3, 2, 1]
    cout << "  뒤집기: ";
    for (int n : v) cout << n << " ";
    cout << "\n";
    // > 출력:   뒤집기: 9 8 7 6 5 4 3 2 1

    int even_count = count_if(v.begin(), v.end(), [](int n) {
        return n % 2 == 0;
    });
    // → v={9,8,7,6,5,4,3,2,1}에서 짝수: 8,6,4,2 → 4개
    cout << "  짝수 개수: " << even_count << "\n";
    // > 출력:   짝수 개수: 4

    cout << endl;
}
