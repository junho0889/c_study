#include <iostream>
#include <string>
#include <vector>

using namespace std;

struct StudyNote {
    string topic;
    string summary;
    int importance;
};

void lesson1_note_structure() {
    cout << "[레슨 1] 메모를 구조체로 묶으면 한 줄 정보가 한 덩어리가 됩니다." << endl;
    cout << endl;

    StudyNote note = {"STL vector", "push_back 과 인덱스 접근을 연습했다.", 5};

    // 구조체는 서로 관련 있는 값을 한 상자에 담는 방법입니다.
    // 공책 한 장에 제목, 요약, 별표 개수를 따로 쓰는 대신
    // '이 메모 한 건'을 한 덩어리로 잡을 수 있게 해 줍니다.
    cout << "  주제: " << note.topic << endl;
    cout << "  요약: " << note.summary << endl;
    cout << "  중요도: " << note.importance << endl;
    cout << endl;
}

void lesson2_note_list() {
    cout << "[레슨 2] vector 에 넣으면 메모 여러 장을 순서대로 다룰 수 있습니다." << endl;
    cout << endl;

    vector<StudyNote> notes = {
        {"Python dict", "키로 값을 빠르게 찾는 방법을 배웠다.", 4},
        {"Dockerfile", "FROM, COPY, CMD 의 역할을 정리했다.", 5},
        {"SQL JOIN", "두 테이블을 연결할 때 ON 조건이 중요했다.", 5},
    };

    for (const StudyNote& note : notes) {
        cout << "  - " << note.topic << " | " << note.summary << " | 중요도 " << note.importance << endl;
    }
    cout << endl;
}

void lesson3_find_important_note() {
    cout << "[레슨 3] 조건문을 쓰면 중요한 메모만 다시 볼 수 있습니다." << endl;
    cout << endl;

    vector<StudyNote> notes = {
        {"gRPC", "proto 가 계약서 역할을 한다.", 3},
        {"Redis", "캐시는 자주 쓰는 값을 가까이 둔다.", 5},
        {"Rust test", "assert_eq! 와 cargo test 를 연결했다.", 5},
    };

    for (const StudyNote& note : notes) {
        if (note.importance >= 5) {
            cout << "  다시 볼 메모: " << note.topic << " -> " << note.summary << endl;
        }
    }
    cout << endl;
}

int main() {
    cout << "============================================================" << endl;
    cout << "  note/main.cpp : 공부 메모를 코드로 정리하는 예제" << endl;
    cout << "============================================================" << endl;
    cout << endl;

    lesson1_note_structure();
    lesson2_note_list();
    lesson3_find_important_note();

    return 0;
}
