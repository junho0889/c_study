/*
===============================================================================
  STL 학습 01단계: vector, map, set
===============================================================================
*/

#include <iostream>
#include <vector>
#include <map>
#include <set>
using namespace std;

void lesson1_vector() {
    /*
      vector = 길이가 늘어나는 배열
      공책에 줄을 더 붙여서 계속 적는 느낌입니다.
    */
    vector<int> numbers = {10, 20, 30};

    cout << "[레슨 1] vector" << endl;
    for (int number : numbers) {
        cout << "  " << number << endl;
    }
    cout << endl;
}

void lesson2_map() {
    /*
      map = 이름표가 붙은 서랍장
      "민수" 칸에는 90, "지우" 칸에는 95 같은 식으로 저장합니다.
    */
    map<string, int> scores = {
        {"민수", 90},
        {"지우", 95}
    };

    cout << "[레슨 2] map" << endl;
    for (const auto& pair : scores) {
        cout << "  " << pair.first << " : " << pair.second << endl;
    }
    cout << endl;
}

void lesson3_set() {
    /*
      set = 중복이 없는 모임
      같은 학생 이름을 두 번 넣어도 하나만 남기는 느낌입니다.
    */
    set<int> unique_numbers = {1, 2, 2, 3, 3, 3};

    cout << "[레슨 3] set" << endl;
    for (int number : unique_numbers) {
        cout << "  " << number << endl;
    }
    cout << endl;
}

int main() {
    cout << "============================================================" << endl;
    cout << "  STL 01단계 : vector, map, set" << endl;
    cout << "============================================================" << endl;
    cout << endl;

    lesson1_vector();
    lesson2_map();
    lesson3_set();
}
