#include <functional>
#include <iostream>
#include <queue>
#include <stack>

using namespace std;

void lesson1_queue() {
    cout << "[레슨 1] queue 는 먼저 들어온 일이 먼저 나갑니다." << endl;
    cout << endl;

    queue<string> line;
    line.push("민수");
    line.push("지우");

    while (!line.empty()) {
        cout << "  처리 순서: " << line.front() << endl;
        line.pop();
    }
    cout << endl;
}

void lesson2_stack_and_priority_queue() {
    cout << "[레슨 2] stack 은 맨 위, priority_queue 는 우선순위가 높은 것부터" << endl;
    cout << endl;

    stack<string> trays;
    trays.push("파란 쟁반");
    trays.push("초록 쟁반");
    cout << "  stack top: " << trays.top() << endl;

    priority_queue<int> scores;
    scores.push(75);
    scores.push(98);
    scores.push(83);
    cout << "  가장 높은 점수: " << scores.top() << endl;
    cout << endl;
}

int main() {
    lesson1_queue();
    lesson2_stack_and_priority_queue();
    return 0;
}
