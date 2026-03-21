/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  STL 학습 06단계: 스마트 포인터 (Smart Pointers)
  실행 방법: g++ -std=c++17 main.cpp -o main && ./main
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  스마트 포인터란?
  new로 만든 메모리를 "자동으로 치워 주는" 똑똑한 포인터입니다.

  비유:
  - 일반 포인터(raw pointer) = 빌린 책을 직접 반납해야 함 (까먹으면 분실!)
  - unique_ptr = 나만 읽는 도서관 책. 반납은 자동! (한 명만 소유)
  - shared_ptr = 여러 명이 같이 읽는 스터디 교재. 마지막 사람이 반납.
  - weak_ptr   = 교재 목록에 "이 책 있나?" 확인만 하는 것. 소유하지 않음.
===============================================================================
*/

#include <iostream>
#include <memory>
#include <string>
#include <vector>
using namespace std;

// 예제용 클래스: 학생
// 생성자와 소멸자에서 메시지를 출력해서 "언제 만들어지고 사라지는지" 볼 수 있습니다.
class Student {
public:
    string name;
    int score;

    Student(const string& n, int s) : name(n), score(s) {
        cout << "    [생성] " << name << " 학생이 만들어졌습니다." << endl;
    }

    ~Student() {
        cout << "    [소멸] " << name << " 학생이 메모리에서 사라졌습니다." << endl;
    }

    void introduce() const {
        cout << "    저는 " << name << "이고, " << score << "점입니다." << endl;
    }
};

// ┌─────────────────────────────────────────────┐
// │  레슨 1: unique_ptr — 나만의 소유권            │
// └─────────────────────────────────────────────┘
void lesson1_unique_ptr() {
    cout << "[레슨 1] unique_ptr — 한 명만 소유할 수 있는 포인터" << endl;
    cout << endl;

    /*
      unique_ptr의 규칙:
      1) 한 번에 하나의 unique_ptr만 객체를 소유합니다.
      2) 복사가 불가능합니다 (= 으로 다른 변수에 넘기기 불가).
      3) 이동(move)은 가능합니다 (소유권을 넘기는 것).
      4) 스코프(중괄호)를 벗어나면 자동으로 메모리를 해제합니다.

      비유: 왕관은 한 명만 쓸 수 있습니다.
            "이거 네가 써" 하고 넘기면(move) 나는 더 이상 왕이 아닙니다.
    */

    // make_unique로 만드는 게 가장 안전합니다.
    {
        auto student = make_unique<Student>("민수", 92);
        student->introduce();

        // unique_ptr<Student> copy = student;  // ❌ 복사 불가! 컴파일 에러

        // 소유권 이동 (move)
        unique_ptr<Student> transferred = move(student);
        // 이제 student는 비어 있습니다 (nullptr)

        if (!student) {
            cout << "    student는 이제 비어 있습니다 (소유권 이동됨)" << endl;
        }
        transferred->introduce();

        cout << "    --- 스코프 끝 → 자동 소멸 ---" << endl;
    }
    // 여기서 transferred가 자동으로 delete됩니다!
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 2: unique_ptr과 함수                    │
// └─────────────────────────────────────────────┘
// unique_ptr을 함수에 넘길 때는 move로 소유권을 넘기거나,
// get()으로 raw pointer를 빌려줍니다.

unique_ptr<Student> create_student(const string& name, int score) {
    // 함수가 unique_ptr을 만들어서 돌려줍니다.
    // 반환할 때 자동으로 move됩니다.
    return make_unique<Student>(name, score);
}

void show_student(const Student* s) {
    // raw pointer로 빌려받아서 읽기만 합니다.
    // 이 함수는 메모리를 해제하지 않습니다.
    if (s) {
        s->introduce();
    }
}

void lesson2_unique_with_functions() {
    cout << "[레슨 2] unique_ptr과 함수" << endl;
    cout << endl;

    // 팩토리 함수에서 만들어 받기
    auto s1 = create_student("지우", 88);

    // get()으로 빌려주기 (소유권은 유지!)
    show_student(s1.get());

    // release()로 소유권 포기 (직접 delete 해야 함 — 비추천)
    Student* raw = s1.release();
    cout << "    release 후 s1은 비어 있음: " << (s1 == nullptr ? "예" : "아니오") << endl;
    delete raw;  // 직접 정리해야 함

    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 3: shared_ptr — 여러 명이 공유           │
// └─────────────────────────────────────────────┘
void lesson3_shared_ptr() {
    cout << "[레슨 3] shared_ptr — 여러 명이 함께 소유" << endl;
    cout << endl;

    /*
      shared_ptr은 "참조 카운트"를 관리합니다.
      누군가 가리키면 카운트 +1, 놓으면 -1.
      카운트가 0이 되면 그때 메모리를 해제합니다.

      비유: 스터디 교재를 여러 명이 공유.
            마지막 사람이 다 읽고 반납하면 그때 도서관에 돌려줍니다.
    */

    shared_ptr<Student> s1;

    {
        auto s2 = make_shared<Student>("서연", 97);
        cout << "    참조 카운트: " << s2.use_count() << endl;  // 1

        s1 = s2;  // 복사 가능! (unique_ptr과 다름)
        cout << "    s1과 s2가 공유, 참조 카운트: " << s1.use_count() << endl;  // 2

        auto s3 = s2;  // 또 공유
        cout << "    s1, s2, s3가 공유, 참조 카운트: " << s1.use_count() << endl;  // 3

        cout << "    --- s2, s3 스코프 끝 ---" << endl;
    }
    // s2, s3가 사라졌지만, s1이 아직 가리키고 있으므로 살아있음!
    cout << "    s1만 남음, 참조 카운트: " << s1.use_count() << endl;  // 1
    s1->introduce();

    cout << "    --- s1 스코프 끝 → 메모리 해제 ---" << endl;
    s1.reset();  // 수동으로 놓기 (또는 스코프 끝에서 자동)
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 4: weak_ptr — 순환 참조 방지             │
// └─────────────────────────────────────────────┘

// 순환 참조 예시를 위한 클래스
class ClassRoom;

class Teacher {
public:
    string name;
    shared_ptr<ClassRoom> classroom;  // 선생님은 교실을 알고 있음

    Teacher(const string& n) : name(n) {
        cout << "    [생성] " << name << " 선생님" << endl;
    }
    ~Teacher() {
        cout << "    [소멸] " << name << " 선생님" << endl;
    }
};

class ClassRoom {
public:
    string room_name;
    // shared_ptr<Teacher> teacher;  // ❌ 이렇게 하면 순환 참조!
    weak_ptr<Teacher> teacher;       // ✅ weak_ptr로 순환 방지!

    ClassRoom(const string& n) : room_name(n) {
        cout << "    [생성] " << room_name << " 교실" << endl;
    }
    ~ClassRoom() {
        cout << "    [소멸] " << room_name << " 교실" << endl;
    }

    void show_teacher() {
        // weak_ptr은 직접 쓸 수 없고, lock()으로 shared_ptr을 얻어야 합니다.
        // 이미 사라졌을 수도 있으니까 확인하는 것!
        if (auto t = teacher.lock()) {
            cout << "    교실 담임: " << t->name << endl;
        } else {
            cout << "    담임 선생님이 없습니다 (이미 사라짐)" << endl;
        }
    }
};

void lesson4_weak_ptr() {
    cout << "[레슨 4] weak_ptr — 순환 참조 방지" << endl;
    cout << endl;

    /*
      순환 참조 문제:
        선생님 → 교실을 가리킴 (shared_ptr)
        교실 → 선생님을 가리킴 (shared_ptr)
        → 둘 다 참조 카운트가 0이 안 됨 → 메모리 누수!

      해결: 한 쪽을 weak_ptr로 만들면 참조 카운트에 포함되지 않습니다.

      비유: 친구 사이에서 "나 → 친구" 연락처는 저장하지만,
            친구 쪽에서는 "있으면 연락, 없으면 말고" 식으로 가볍게 기억.
    */

    {
        auto teacher = make_shared<Teacher>("김선생");
        auto room = make_shared<ClassRoom>("1반");

        teacher->classroom = room;
        room->teacher = teacher;  // weak_ptr이라 참조 카운트 안 올라감

        room->show_teacher();

        cout << "    teacher 참조 카운트: " << teacher.use_count() << " (1이어야 정상)" << endl;
        cout << "    room 참조 카운트: " << room.use_count() << endl;

        cout << "    --- 스코프 끝 ---" << endl;
    }
    // 모두 정상적으로 소멸됩니다!
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 5: 컨테이너에 스마트 포인터 담기         │
// └─────────────────────────────────────────────┘
void lesson5_smart_ptr_in_container() {
    cout << "[레슨 5] vector에 스마트 포인터 담기" << endl;
    cout << endl;

    // shared_ptr은 vector에 쉽게 담을 수 있습니다.
    vector<shared_ptr<Student>> class_list;

    class_list.push_back(make_shared<Student>("하준", 78));
    class_list.push_back(make_shared<Student>("유나", 90));
    class_list.push_back(make_shared<Student>("도윤", 85));

    cout << "  반 학생 목록:" << endl;
    for (const auto& s : class_list) {
        s->introduce();
    }
    cout << endl;

    // unique_ptr은 move로 담아야 합니다.
    vector<unique_ptr<Student>> unique_list;
    unique_list.push_back(make_unique<Student>("소율", 93));

    auto temp = make_unique<Student>("시우", 87);
    unique_list.push_back(move(temp));  // move 필수!

    cout << "  unique_ptr 목록:" << endl;
    for (const auto& s : unique_list) {
        s->introduce();
    }

    cout << endl;
    cout << "  --- 함수 끝 → 모든 학생 자동 소멸 ---" << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 6: 언제 어떤 포인터를 쓸까?              │
// └─────────────────────────────────────────────┘
void lesson6_when_to_use() {
    cout << "[레슨 6] 언제 어떤 스마트 포인터를 쓸까?" << endl;
    cout << endl;

    cout << "  ┌──────────────┬────────────────────────────────────┐" << endl;
    cout << "  │  종류        │  언제 쓸까?                         │" << endl;
    cout << "  ├──────────────┼────────────────────────────────────┤" << endl;
    cout << "  │  unique_ptr  │  소유자가 딱 1명일 때 (기본 선택!)   │" << endl;
    cout << "  │  shared_ptr  │  여러 곳에서 공유해야 할 때           │" << endl;
    cout << "  │  weak_ptr    │  순환 참조를 끊을 때, 캐시용           │" << endl;
    cout << "  │  raw pointer │  소유하지 않고 빌려볼 때만            │" << endl;
    cout << "  └──────────────┴────────────────────────────────────┘" << endl;
    cout << endl;
    cout << "  팁: 모르겠으면 unique_ptr부터 시작하세요!" << endl;
    cout << "       공유가 정말 필요하면 그때 shared_ptr로 바꾸면 됩니다." << endl;
    cout << endl;
}

int main() {
    cout << "============================================================" << endl;
    cout << "  STL 06단계 : 스마트 포인터 (unique, shared, weak)" << endl;
    cout << "============================================================" << endl;
    cout << endl;

    lesson1_unique_ptr();
    lesson2_unique_with_functions();
    lesson3_shared_ptr();
    lesson4_weak_ptr();
    lesson5_smart_ptr_in_container();
    lesson6_when_to_use();

    return 0;
}
