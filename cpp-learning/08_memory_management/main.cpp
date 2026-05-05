/*
=============================================================================
  C++ 학습 08단계: 메모리 관리와 스마트 포인터
=============================================================================
  [컴파일] g++ -std=c++17 -o 08_mem main.cpp
  [주석 표기] // > 출력  // → 변수값  // ▶ 흐름
=============================================================================
*/
#include <iostream>
#include <string>
#include <memory>
#include <vector>
using namespace std;

void lesson1_stack_heap();
void lesson2_smart_pointers();
void lesson3_shared_ptr();
void lesson4_raii();
void lesson5_move_semantics();

int main() {
    cout << "========================================\n";
    cout << "  C++ 08단계 : 메모리 관리\n";
    cout << "========================================\n\n";

    lesson1_stack_heap();
    lesson2_smart_pointers();
    lesson3_shared_ptr();
    lesson4_raii();
    lesson5_move_semantics();

    cout << "\n08단계 학습 완료!\n";
    return 0;
}


// =====================================================================
// 레슨 1 — 스택 vs 힙
// =====================================================================
void lesson1_stack_heap() {
    cout << "[레슨 1] 스택 vs 힙 메모리\n\n";

    int stack_var = 42;
    // → 스택에 저장. 함수 끝나면 자동 해제.
    cout << "  스택 변수: " << stack_var << "\n";
    // > 출력:   스택 변수: 42

    int* heap_var = new int(99);
    // → 힙에 4바이트 할당, 99로 초기화. heap_var = 그 주소.
    cout << "  힙 변수:   " << *heap_var << "\n";
    // > 출력:   힙 변수:   99

    delete heap_var;
    // → 힙 메모리 해제. heap_var는 댕글링 상태.
    heap_var = nullptr;
    // → 명시적 무효화.

    cout << endl;
}


// =====================================================================
// 레슨 2 — unique_ptr
// =====================================================================
class Monster {
    string name_;
public:
    Monster(const string& name) : name_(name) {
        cout << "  [생성] " << name_ << "\n";
    }
    ~Monster() {
        cout << "  [소멸] " << name_ << "\n";
    }
    void attack() const {
        cout << "  " << name_ << " 공격!\n";
    }
};

void lesson2_smart_pointers() {
    cout << "[레슨 2] unique_ptr (단독 소유)\n\n";

    {
        auto goblin = make_unique<Monster>("고블린");
        // > 출력:   [생성] 고블린

        goblin->attack();
        // > 출력:   고블린 공격!

        auto transferred = move(goblin);
        // → goblin이 가진 포인터를 transferred로 이전.
        // → goblin 내부 포인터 = nullptr.

        if (!goblin) {
            // → goblin은 nullptr → !goblin = true
            cout << "  goblin은 이제 비어있음 (소유권 이전됨)\n";
            // > 출력:   goblin은 이제 비어있음 (소유권 이전됨)
        }
        transferred->attack();
        // > 출력:   고블린 공격!

        cout << "  -- 블록 끝, 자동 해제 --\n";
        // > 출력:   -- 블록 끝, 자동 해제 --
    }
    // ▶ 블록 종료 → transferred 소멸 → Monster 소멸자 호출
    // > 출력:   [소멸] 고블린

    cout << "\n  --- unique_ptr + vector ---\n";
    {
        vector<unique_ptr<Monster>> monsters;
        monsters.push_back(make_unique<Monster>("슬라임"));
        // > 출력:   [생성] 슬라임
        monsters.push_back(make_unique<Monster>("드래곤"));
        // > 출력:   [생성] 드래곤

        for (const auto& m : monsters) {
            m->attack();
        }
        // > 출력:
        //   슬라임 공격!
        //   드래곤 공격!

        cout << "  -- vector 끝, 전부 자동 해제 --\n";
    }
    // ▶ vector 소멸 → 안에 든 unique_ptr 소멸 → Monster 소멸 (역순으로)
    // > 출력:
    //   [소멸] 슬라임
    //   [소멸] 드래곤
    //   ※ 실제로는 vector 안 인덱스 순서대로 소멸 (앞→뒤)

    cout << endl;
}


// =====================================================================
// 레슨 3 — shared_ptr & weak_ptr
// =====================================================================
void lesson3_shared_ptr() {
    cout << "[레슨 3] shared_ptr & weak_ptr\n\n";

    cout << "  --- shared_ptr ---\n";
    auto sp1 = make_shared<Monster>("보스");
    // > 출력:   [생성] 보스
    // → 참조 카운트 = 1

    cout << "  참조 수: " << sp1.use_count() << "\n";
    // > 출력:   참조 수: 1

    {
        auto sp2 = sp1;
        // → 같은 객체 가리킴. 참조 카운트 = 2.
        cout << "  sp2 복사 후 참조 수: " << sp1.use_count() << "\n";
        // > 출력:   sp2 복사 후 참조 수: 2
        sp2->attack();
        // > 출력:   보스 공격!
    }
    // ▶ sp2 블록 종료 → 소멸 → 참조 카운트 1 → 객체 살아있음

    cout << "  sp2 소멸 후 참조 수: " << sp1.use_count() << "\n";
    // > 출력:   sp2 소멸 후 참조 수: 1

    cout << "\n  --- weak_ptr ---\n";
    weak_ptr<Monster> wp;
    {
        auto sp = make_shared<Monster>("유령");
        // > 출력:   [생성] 유령
        // → sp 참조 카운트 1
        wp = sp;
        // → wp는 weak. 참조 카운트 안 늘어남. (sp 카운트 = 1 유지)

        cout << "  expired? " << wp.expired() << "  (0=살아있음)\n";
        // → wp.expired() = false → 0
        // > 출력:   expired? 0  (0=살아있음)

        if (auto locked = wp.lock()) {
            // → lock()은 sp가 살아있으면 새 shared_ptr 반환.
            // → 안에서 일시적으로 카운트 +1.
            locked->attack();
            // > 출력:   유령 공격!
        }
        // ▶ locked 소멸 → 카운트 다시 1
    }
    // ▶ sp 소멸 → 카운트 0 → 객체 삭제 → wp는 expired 상태
    // > 출력:   [소멸] 유령

    cout << "  sp 소멸 후 expired? " << wp.expired() << "  (1=죽었음)\n";
    // > 출력:   sp 소멸 후 expired? 1  (1=죽었음)

    cout << endl;
}
// ▶ 함수 종료 시 sp1 소멸 → 카운트 0 → 보스 객체 삭제
// > 출력 (함수 종료 후):   [소멸] 보스


// =====================================================================
// 레슨 4 — RAII
// =====================================================================
class FileHandle {
    string filename_;
public:
    FileHandle(const string& name) : filename_(name) {
        cout << "  [RAII] 파일 열기: " << filename_ << "\n";
    }
    ~FileHandle() {
        cout << "  [RAII] 파일 닫기: " << filename_ << "\n";
    }
    void write(const string& data) {
        cout << "  [RAII] 쓰기: " << data << "\n";
    }
};

void lesson4_raii() {
    cout << "[레슨 4] RAII 패턴\n\n";
    {
        FileHandle file("data.txt");
        // > 출력:   [RAII] 파일 열기: data.txt

        file.write("Hello RAII");
        // > 출력:   [RAII] 쓰기: Hello RAII

        cout << "  -- 블록 끝 --\n";
        // > 출력:   -- 블록 끝 --
    }
    // ▶ 블록 종료 → file 소멸 → 자동으로 ~FileHandle()
    // > 출력:   [RAII] 파일 닫기: data.txt

    cout << endl;
}


// =====================================================================
// 레슨 5 — 이동 시맨틱스 (Move Semantics) 기초
// =====================================================================
void lesson5_move_semantics() {
    cout << "[레슨 5] 이동 시맨틱스 기초\n\n";

    string original = "매우 긴 문자열이라고 가정합니다";
    cout << "  원본: \"" << original << "\"\n";
    // > 출력:   원본: "매우 긴 문자열이라고 가정합니다"

    string moved = move(original);
    // → original 내부 버퍼 포인터를 moved로 이전.
    // → original은 "moved-from" 상태 (보통 빈 문자열, 표준은 "유효하나 미정의")
    cout << "  이동 후 moved:    \"" << moved << "\"\n";
    // > 출력:   이동 후 moved:    "매우 긴 문자열이라고 가정합니다"
    cout << "  이동 후 original: \"" << original << "\"  (비어있음)\n\n";
    // > 출력:   이동 후 original: ""  (비어있음)
    //   ※ 거의 모든 표준 라이브러리 구현에서 빈 문자열로 됨.

    vector<int> v1 = {1, 2, 3, 4, 5};
    cout << "  v1 크기: " << v1.size() << "\n";
    // > 출력:   v1 크기: 5

    vector<int> v2 = move(v1);
    // → v1 내부 버퍼 포인터 → v2로. v1은 빈 vector(size 0).
    cout << "  이동 후 v2 크기: " << v2.size() << "\n";
    // > 출력:   이동 후 v2 크기: 5
    cout << "  이동 후 v1 크기: " << v1.size() << "  (비어있음)\n";
    // > 출력:   이동 후 v1 크기: 0  (비어있음)

    cout << endl;
}
