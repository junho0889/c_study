#include <algorithm>
#include <iostream>
#include <numeric>
#include <vector>

using namespace std;

void lesson1_sort_and_find() {
    cout << "[레슨 1] sort 와 find 는 가장 자주 보는 STL 알고리즘입니다." << endl;
    cout << endl;

    vector<int> scores = {88, 72, 95, 80};
    sort(scores.begin(), scores.end());

    for (int score : scores) {
        cout << "  정렬 후 점수: " << score << endl;
    }

    auto found = find(scores.begin(), scores.end(), 95);
    cout << "  95점 찾았는가? " << (found != scores.end() ? "예" : "아니오") << endl;
    cout << endl;
}

void lesson2_transform_and_accumulate() {
    cout << "[레슨 2] transform 은 바꾸기, accumulate 는 모으기입니다." << endl;
    cout << endl;

    vector<int> counts = {1, 2, 3};
    vector<int> doubled(counts.size());

    transform(counts.begin(), counts.end(), doubled.begin(), [](int value) {
        return value * 2;
    });

    int total = accumulate(doubled.begin(), doubled.end(), 0);

    for (int value : doubled) {
        cout << "  두 배 수량: " << value << endl;
    }
    cout << "  전체 합계: " << total << endl;
    cout << endl;
}

int main() {
    lesson1_sort_and_find();
    lesson2_transform_and_accumulate();
    return 0;
}
