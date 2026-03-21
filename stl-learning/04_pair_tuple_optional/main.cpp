#include <iostream>
#include <optional>
#include <tuple>
#include <utility>

using namespace std;

void lesson1_pair_and_tuple() {
    cout << "[레슨 1] pair 는 두 값, tuple 은 여러 값을 묶는 상자입니다." << endl;
    cout << endl;

    pair<string, int> student = {"민수", 90};
    tuple<int, int, int> rgb = {255, 200, 100};

    cout << "  pair: " << student.first << ", " << student.second << endl;
    cout << "  tuple RGB: "
         << get<0>(rgb) << ", "
         << get<1>(rgb) << ", "
         << get<2>(rgb) << endl;
    cout << endl;
}

void lesson2_optional() {
    cout << "[레슨 2] optional 은 값이 있을 수도 없을 수도 있음을 안전하게 표현합니다." << endl;
    cout << endl;

    optional<int> perfectScore = 100;
    optional<int> missingScore;

    if (perfectScore.has_value()) {
        cout << "  있는 값: " << perfectScore.value() << endl;
    }

    cout << "  없는 값 기본 출력: " << missingScore.value_or(-1) << endl;
    cout << endl;
}

int main() {
    lesson1_pair_and_tuple();
    lesson2_optional();
    return 0;
}
