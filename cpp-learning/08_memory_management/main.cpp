/*
=============================================================================
  C++ 학습 08단계: 메모리 관리와 스마트 포인터
=============================================================================
  [학습 목표]
  1. 스택 메모리와 힙 메모리의 차이를 이해한다
  2. new/delete의 위험성을 알고 스마트 포인터를 사용한다
  3. unique_ptr, shared_ptr, weak_ptr을 구분한다
  4. RAII 패턴을 이해한다
  5. 이동 시맨틱스(move semantics) 기초를 안다

  [컴파일] g++ -std=c++17 -o 08_mem main.cpp
=============================================================================
*/
#include <iostream>
#include <string>
#include <memory>   // smart pointers
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

    /*
    ★ 메모리 구조 (프로그램 실행 시)

    ┌─────────────────────┐ 높은 주소
    │      스택 (Stack)    │  ← 지역 변수, 함수 호출 정보
    │    ↓ 아래로 자람      │     빠름, 자동 해제, 크기 제한
    │                      │
    │    ↑ 위로 자람        │
    │       힙 (Heap)      │  ← new로 할당한 메모리
    │                      │     느림, 수동 해제, 크기 큼
    ├─────────────────────┤
    │   데이터 영역        │  ← 전역 변수, static 변수
    ├─────────────────────┤
    │   코드 영역          │  ← 실행할 코드
    └─────────────────────┘ 낮은 주소

    ★ 스택 vs 힙
    ┌──────────┬───────────────┬───────────────┐
    │          │ 스택 (Stack)   │ 힙 (Heap)     │
    ├──────────┼───────────────┼───────────────┤
    │ 할당     │ 자동           │ new 로 수동    │
    │ 해제     │ 자동 (스코프)  │ delete 로 수동 │
    │ 속도     │ 매우 빠름      │ 상대적 느림    │
    │ 크기     │ 작음 (1~8MB)  │ 큼 (GB 단위)  │
    │ 위험     │ 안전           │ 누수, 해제 후  │
    │          │                │ 사용 등 위험   │
    └──────────┴───────────────┴───────────────┘
    */

    // 스택: 자동 할당, 자동 해제
    int stack_var = 42;
    cout << "  스택 변수: " << stack_var << "\n";

    // 힙: 수동 할당, 수동 해제
    int* heap_var = new int(99);
    cout << "  힙 변수:   " << *heap_var << "\n";
    delete heap_var;   // 반드시 해제!
    heap_var = nullptr;

    /*
    ★ new/delete의 3대 위험
    1. 메모리 누수 (Memory Leak): delete 안 함
    2. 이중 해제 (Double Free): 같은 메모리를 2번 delete
    3. 댕글링 포인터 (Dangling Pointer): delete 후에도 접근

    → 해결: 스마트 포인터를 쓰자!
    */

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

    /*
    ★ unique_ptr = 메모리를 '단독 소유'하는 스마트 포인터
      → 스코프를 벗어나면 자동으로 delete (메모리 누수 없음!)
      → 복사 불가, 이동만 가능

    사용법:
      auto ptr = make_unique<타입>(생성자 인자);
    */

    {
        // make_unique로 생성 (추천!)
        auto goblin = make_unique<Monster>("고블린");
        goblin->attack();

        // 소유권 이전 (move)
        auto transferred = move(goblin);
        // goblin은 이제 nullptr!
        if (!goblin) {
            cout << "  goblin은 이제 비어있음 (소유권 이전됨)\n";
        }
        transferred->attack();

        cout << "  -- 블록 끝, 자동 해제 --\n";
    }  // transferred가 자동으로 delete됨!

    cout << "\n  --- unique_ptr + vector ---\n";
    {
        vector<unique_ptr<Monster>> monsters;
        monsters.push_back(make_unique<Monster>("슬라임"));
        monsters.push_back(make_unique<Monster>("드래곤"));

        for (const auto& m : monsters) {
            m->attack();
        }
        cout << "  -- vector 끝, 전부 자동 해제 --\n";
    }

    cout << endl;
}


// =====================================================================
// 레슨 3 — shared_ptr & weak_ptr
// =====================================================================
void lesson3_shared_ptr() {
    cout << "[레슨 3] shared_ptr & weak_ptr\n\n";

    /*
    ★ shared_ptr = 메모리를 '공유 소유' (참조 카운트 방식)
      → 마지막 shared_ptr이 사라질 때 자동 delete
      → 여러 곳에서 같은 객체를 쓸 때 유용

    ★ weak_ptr = shared_ptr이 가리키는 객체를 '관찰'만
      → 소유하지 않음 (참조 카운트 증가 안 함)
      → 순환 참조 방지용
    */

    // shared_ptr
    cout << "  --- shared_ptr ---\n";
    auto sp1 = make_shared<Monster>("보스");
    cout << "  참조 수: " << sp1.use_count() << "\n";

    {
        auto sp2 = sp1;  // 복사 가능! 참조 수 증가
        cout << "  sp2 복사 후 참조 수: " << sp1.use_count() << "\n";
        sp2->attack();
    }  // sp2 소멸, 참조 수 감소

    cout << "  sp2 소멸 후 참조 수: " << sp1.use_count() << "\n";
    // sp1이 마지막이므로 sp1 소멸 시 delete됨

    // weak_ptr
    cout << "\n  --- weak_ptr ---\n";
    weak_ptr<Monster> wp;
    {
        auto sp = make_shared<Monster>("유령");
        wp = sp;   // weak_ptr에 대입 (참조 수 안 늘어남)
        cout << "  expired? " << wp.expired() << "  (0=살아있음)\n";

        // weak_ptr로 객체 사용하려면 lock()으로 shared_ptr 획득
        if (auto locked = wp.lock()) {
            locked->attack();
        }
    }  // sp 소멸 → 객체 삭제됨

    cout << "  sp 소멸 후 expired? " << wp.expired() << "  (1=죽었음)\n";

    /*
    ★ 선택 가이드
    unique_ptr  : 하나만 소유 (기본 선택, 90%는 이것으로 충분)
    shared_ptr  : 여러 곳에서 공유해야 할 때
    weak_ptr    : 순환 참조 방지, 객체 존재 확인용
    raw pointer : 소유하지 않는 '관찰용' (함수 매개변수 등)
    */

    cout << endl;
}


// =====================================================================
// 레슨 4 — RAII
// =====================================================================
/*
★ RAII = Resource Acquisition Is Initialization
  = "자원 획득은 초기화다"
  = 생성자에서 자원 획득, 소멸자에서 자원 해제

  → C++에서 가장 중요한 패턴!
  → 스마트 포인터, lock_guard, fstream 등 모두 RAII 패턴

  예: fstream → 생성 시 파일 열림, 소멸 시 자동으로 닫힘
      unique_ptr → 생성 시 메모리 할당, 소멸 시 자동 해제
      lock_guard → 생성 시 잠금, 소멸 시 자동 해제
*/

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
        file.write("Hello RAII");
        // 예외가 발생해도 소멸자가 호출되어 파일이 닫힘!
        cout << "  -- 블록 끝 --\n";
    }  // 소멸자 자동 호출

    cout << endl;
}


// =====================================================================
// 레슨 5 — 이동 시맨틱스 (Move Semantics) 기초
// =====================================================================
void lesson5_move_semantics() {
    cout << "[레슨 5] 이동 시맨틱스 기초\n\n";

    /*
    ★ 이동(move) = 데이터를 '복사'하지 않고 '옮기기'
      → 큰 데이터(vector, string 등)를 넘길 때 성능 향상

    복사: 원본 유지, 새 복사본 생성 (느림)
    이동: 원본의 데이터를 가져감, 원본은 빈 상태 (빠름)

    std::move(x) → x를 '이동 가능'하다고 표시
    */

    // string 이동 예시
    string original = "매우 긴 문자열이라고 가정합니다";
    cout << "  원본: \"" << original << "\"\n";

    string moved = move(original);  // 이동!
    cout << "  이동 후 moved:    \"" << moved << "\"\n";
    cout << "  이동 후 original: \"" << original << "\"  (비어있음)\n\n";

    // vector 이동 예시
    vector<int> v1 = {1, 2, 3, 4, 5};
    cout << "  v1 크기: " << v1.size() << "\n";

    vector<int> v2 = move(v1);
    cout << "  이동 후 v2 크기: " << v2.size() << "\n";
    cout << "  이동 후 v1 크기: " << v1.size() << "  (비어있음)\n";

    /*
    ★ 언제 move를 쓸까?
    1. 함수에서 큰 객체를 반환할 때 (컴파일러가 자동 적용하기도 함)
    2. unique_ptr 소유권 이전
    3. 더 이상 사용 안 할 객체를 넘길 때

    ★ 주의: move 후에 원본 객체를 사용하면 안 됨!
           (빈 상태이므로 예측 불가)
    */

    cout << endl;
}
