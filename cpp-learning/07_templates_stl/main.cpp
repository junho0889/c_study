/*
=============================================================================
  C++ 학습 07단계: 템플릿과 STL (표준 라이브러리)
=============================================================================
  [학습 목표]
  1. 함수 템플릿과 클래스 템플릿을 이해한다
  2. STL 컨테이너 (vector, map, set 등)를 사용할 수 있다
  3. 반복자(iterator)를 이해한다
  4. STL 알고리즘 (sort, find, count 등)을 활용한다

  [컴파일] g++ -std=c++17 -o 07_stl main.cpp
=============================================================================
*/
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <unordered_map>
#include <algorithm>  // sort, find, count...
#include <numeric>    // accumulate
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
/*
★ 템플릿 = 타입을 매개변수로 만드는 '틀'
  → 같은 로직을 int, double, string 등 어떤 타입이든 쓸 수 있게

  왜 쓸까?
  int    max_int(int a, int b)    { return a > b ? a : b; }
  double max_dbl(double a, double b) { return a > b ? a : b; }
  → 로직이 같은데 타입만 다름!  → 템플릿으로 하나만 만들면 됨
*/

// 함수 템플릿
template <typename T>       // T = 아무 타입이든 가능
T my_max(T a, T b) {
    return (a > b) ? a : b;
}

// 클래스 템플릿
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

    // 함수 템플릿: 타입 자동 추론
    cout << "  max(3, 7)     = " << my_max(3, 7) << "\n";
    cout << "  max(3.5, 2.1) = " << my_max(3.5, 2.1) << "\n";
    cout << "  max 타입 명시 = " << my_max<int>(3, 7) << "\n\n";

    // 클래스 템플릿
    Box<int>    int_box(42);
    Box<string> str_box("Hello");
    cout << "  Box<int>    = " << int_box.get() << "\n";
    cout << "  Box<string> = " << str_box.get() << "\n";
    cout << endl;
}


// =====================================================================
// 레슨 2 — vector (동적 배열)
// =====================================================================
void lesson2_vector() {
    cout << "[레슨 2] vector (동적 배열)\n\n";

    /*
    ★ vector = 크기가 자동으로 늘어나는 배열 (가장 많이 쓰는 STL!)
      → new/delete 안 써도 됨!
      → 배열 대신 vector를 쓰자

    주요 멤버 함수:
      push_back(val)  맨 뒤에 추가
      pop_back()      맨 뒤 삭제
      size()          현재 개수
      empty()         비어있는가?
      clear()         전부 삭제
      at(i)           i번째 요소 (범위 검사 O)
      [i]             i번째 요소 (범위 검사 X, 더 빠름)
      front() / back() 첫/마지막 요소
    */

    // 생성
    vector<int> nums;                      // 빈 벡터
    vector<int> scores = {95, 82, 71, 88}; // 초기값
    vector<int> zeros(5, 0);               // 0이 5개

    // 추가
    nums.push_back(10);
    nums.push_back(20);
    nums.push_back(30);

    // 순회 (3가지 방법)
    cout << "  --- 순회 방법 ---\n";

    // 1) 인덱스
    cout << "  인덱스:  ";
    for (size_t i = 0; i < nums.size(); i++) {
        cout << nums[i] << " ";
    }
    cout << "\n";

    // 2) 범위 기반 for (추천!)
    cout << "  범위for: ";
    for (int n : nums) {
        cout << n << " ";
    }
    cout << "\n";

    // 3) 반복자 (iterator)
    cout << "  iterator: ";
    for (auto it = nums.begin(); it != nums.end(); ++it) {
        cout << *it << " ";
    }
    cout << "\n\n";

    // 유용한 기능들
    cout << "  크기:   " << nums.size() << "\n";
    cout << "  첫번째: " << nums.front() << "\n";
    cout << "  마지막: " << nums.back() << "\n";

    nums.pop_back();  // 마지막 삭제
    cout << "  pop 후: ";
    for (int n : nums) cout << n << " ";
    cout << "\n";

    // 2차원 벡터
    cout << "\n  --- 2차원 vector ---\n";
    vector<vector<int>> matrix = {
        {1, 2, 3},
        {4, 5, 6}
    };
    for (const auto& row : matrix) {
        cout << "  ";
        for (int val : row) cout << val << " ";
        cout << "\n";
    }
    cout << endl;
}


// =====================================================================
// 레슨 3 — map (키-값 쌍)
// =====================================================================
void lesson3_map() {
    cout << "[레슨 3] map (키-값 저장소)\n\n";

    /*
    ★ map = 키(key)로 값(value)을 저장/조회  (파이썬 dict과 비슷)
      → 키 기준 자동 정렬됨 (내부: 레드-블랙 트리)

    ★ unordered_map = 정렬 없이 더 빠름 (내부: 해시 테이블)
      → 순서 불필요하면 이쪽이 성능 좋음
    */

    // map: 키 기준 자동 정렬
    map<string, int> ages;
    ages["홍길동"] = 25;
    ages["김철수"] = 30;
    ages["이영희"] = 22;
    ages.insert({"박지민", 28});  // insert로도 추가 가능

    cout << "  --- map (정렬됨) ---\n";
    for (const auto& [name, age] : ages) {   // C++17 구조적 바인딩
        cout << "  " << name << " : " << age << "세\n";
    }

    // 조회
    cout << "\n  홍길동 나이: " << ages["홍길동"] << "\n";

    // 키 존재 확인
    if (ages.count("김철수")) {    // 0 또는 1
        cout << "  김철수 존재함\n";
    }
    if (ages.find("없는사람") == ages.end()) {
        cout << "  없는사람 없음\n";
    }

    // 삭제
    ages.erase("이영희");
    cout << "  삭제 후 크기: " << ages.size() << "\n";

    // unordered_map (더 빠름, 정렬 없음)
    cout << "\n  --- unordered_map ---\n";
    unordered_map<string, string> capitals;
    capitals["한국"] = "서울";
    capitals["일본"] = "도쿄";
    capitals["미국"] = "워싱턴";

    for (const auto& [country, capital] : capitals) {
        cout << "  " << country << " → " << capital << "\n";
    }
    cout << endl;
}


// =====================================================================
// 레슨 4 — set (중복 없는 집합)
// =====================================================================
void lesson4_set() {
    cout << "[레슨 4] set (집합)\n\n";

    /*
    ★ set = 중복 없이 값 저장, 자동 정렬
      → 중복 확인, 존재 여부 검사에 유용
    */

    set<int> numbers = {5, 3, 8, 1, 3, 5};  // 중복 자동 제거

    cout << "  set (중복 제거 + 정렬): ";
    for (int n : numbers) {
        cout << n << " ";
    }
    cout << "\n";

    numbers.insert(4);
    numbers.insert(3);   // 이미 있으면 무시됨

    cout << "  insert(4,3) 후: ";
    for (int n : numbers) cout << n << " ";
    cout << "\n";

    cout << "  3이 있나? " << (numbers.count(3) ? "있음" : "없음") << "\n";
    cout << "  9가 있나? " << (numbers.count(9) ? "있음" : "없음") << "\n";
    cout << endl;
}


// =====================================================================
// 레슨 5 — STL 알고리즘
// =====================================================================
void lesson5_algorithms() {
    cout << "[레슨 5] STL 알고리즘\n\n";

    /*
    ★ <algorithm> 헤더에 있는 유용한 함수들
      sort, find, count, min_element, max_element,
      reverse, accumulate, for_each ...

    ★ 대부분 iterator(반복자) 범위를 인자로 받음:
      algorithm(begin, end, ...)
    */

    vector<int> v = {5, 2, 8, 1, 9, 3, 7, 4, 6};

    // 정렬
    sort(v.begin(), v.end());
    cout << "  오름차순: ";
    for (int n : v) cout << n << " ";
    cout << "\n";

    // 내림차순 정렬
    sort(v.begin(), v.end(), greater<int>());
    cout << "  내림차순: ";
    for (int n : v) cout << n << " ";
    cout << "\n";

    // 람다로 커스텀 정렬
    sort(v.begin(), v.end(), [](int a, int b) {
        return a < b;  // 오름차순
    });

    // 찾기
    auto it = find(v.begin(), v.end(), 5);
    if (it != v.end()) {
        cout << "  5 찾음! 위치: " << (it - v.begin()) << "\n";
    }

    // 개수 세기
    vector<int> data = {1, 2, 3, 2, 1, 2, 3};
    cout << "  2의 개수: " << count(data.begin(), data.end(), 2) << "\n";

    // 최소/최대
    auto min_it = min_element(v.begin(), v.end());
    auto max_it = max_element(v.begin(), v.end());
    cout << "  최소: " << *min_it << "  최대: " << *max_it << "\n";

    // 합계 (<numeric>)
    int sum = accumulate(v.begin(), v.end(), 0);
    cout << "  합계: " << sum << "\n";

    // 뒤집기
    reverse(v.begin(), v.end());
    cout << "  뒤집기: ";
    for (int n : v) cout << n << " ";
    cout << "\n";

    // 조건 만족하는 것만 세기
    int even_count = count_if(v.begin(), v.end(), [](int n) {
        return n % 2 == 0;
    });
    cout << "  짝수 개수: " << even_count << "\n";

    /*
    ★ 자주 쓰는 STL 알고리즘 정리
    ┌─────────────────┬────────────────────────┐
    │ 함수            │ 기능                    │
    ├─────────────────┼────────────────────────┤
    │ sort            │ 정렬                    │
    │ find            │ 값 찾기                 │
    │ count           │ 값 세기                 │
    │ count_if        │ 조건 만족하는 개수      │
    │ min/max_element │ 최소/최대 위치          │
    │ accumulate      │ 합계                    │
    │ reverse         │ 뒤집기                  │
    │ unique          │ 연속 중복 제거          │
    │ binary_search   │ 이진 탐색 (정렬 필요)   │
    │ for_each        │ 각 요소에 함수 적용     │
    │ transform       │ 변환하여 새 컨테이너    │
    └─────────────────┴────────────────────────┘
    */

    cout << endl;
}
