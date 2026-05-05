#include <iostream>
#include <memory>
#include <vector>
#include <string>

// ============================================
// 1. 스택 vs 힙 - 메모리 위치의 차이
// ============================================
void stack_vs_heap() {
    std::cout << "=== 스택 vs 힙 ===" << std::endl;

    // 스택: 함수 끝나면 자동으로 사라짐 (빠름)
    int a = 10;              // 4바이트, 스택
    double b = 3.14;         // 8바이트, 스택
    int arr[3] = {1, 2, 3};  // 12바이트, 스택

    // 힙: 내가 직접 관리 (느리지만 크기 자유)
    int* p = new int(42);           // 4바이트, 힙에 할당
    int* big = new int[1000000];    // 400만바이트, 힙에 할당

    std::cout << "스택 변수 a: " << a << " (주소: " << &a << ")" << std::endl;
    std::cout << "힙 변수 p:   " << *p << " (주소: " << p << ")" << std::endl;

    // 힙은 반드시 해제해야 함 (안 하면 메모리 누수!)
    delete p;
    delete[] big;  // 배열은 delete[]
}

// ============================================
// 2. 메모리 누수 예시 (이렇게 하면 안 됨)
// ============================================
void memory_leak_bad() {
    std::cout << "\n=== 메모리 누수 (나쁜 예) ===" << std::endl;

    for (int i = 0; i < 3; i++) {
        int* leak = new int(i);  // 매번 할당
        std::cout << *leak << " ";
        // delete를 안 함! → 메모리 누수!
        delete leak;  // 이걸 빼먹으면 누수
    }
    std::cout << std::endl;
}

// ============================================
// 3. 스마트 포인터 - 자동으로 메모리 해제
//    C#의 IDisposable + using, Python의 with 같은 것
// ============================================
void smart_pointers() {
    std::cout << "\n=== 스마트 포인터 ===" << std::endl;

    // unique_ptr: 소유자가 딱 1명 (가장 많이 씀)
    // 스코프 벗어나면 자동 delete
    {
        auto ptr = std::make_unique<int>(100);
        std::cout << "unique_ptr: " << *ptr << std::endl;
    } // 여기서 자동 해제! delete 안 써도 됨

    // shared_ptr: 여러 곳에서 공유 가능
    // 마지막 사용자가 사라지면 자동 delete
    {
        auto sp1 = std::make_shared<std::string>("공유 데이터");
        std::cout << "shared_ptr 참조 수: " << sp1.use_count() << std::endl;  // 1
        {
            auto sp2 = sp1;  // 공유!
            std::cout << "shared_ptr 참조 수: " << sp1.use_count() << std::endl;  // 2
        } // sp2 사라짐
        std::cout << "shared_ptr 참조 수: " << sp1.use_count() << std::endl;  // 1
    } // sp1 사라짐 → 자동 해제
}

// ============================================
// 4. move - 복사 대신 이동 (성능 차이 큼)
// ============================================
void move_semantics() {
    std::cout << "\n=== move 의미론 ===" << std::endl;

    std::vector<int> v1 = {1, 2, 3, 4, 5};
    std::cout << "v1 크기(이동 전): " << v1.size() << std::endl;

    // 복사: 데이터를 통째로 복제 (느림)
    std::vector<int> v2 = v1;  // 복사
    std::cout << "복사 후 v1 크기: " << v1.size() << std::endl;  // 5 (그대로)

    // 이동: 소유권만 넘김 (빠름)
    std::vector<int> v3 = std::move(v1);  // 이동
    std::cout << "이동 후 v1 크기: " << v1.size() << std::endl;  // 0 (비워짐!)
    std::cout << "이동 후 v3 크기: " << v3.size() << std::endl;  // 5

    // 비유: 복사 = 책을 복사기로 복사, 이동 = 책을 그냥 건네줌
}

// ============================================
// 5. 실전: 게임 오브젝트 관리
// ============================================
class GameObject {
    std::string name;
    int hp;
public:
    GameObject(const std::string& n, int h) : name(n), hp(h) {
        std::cout << "  [생성] " << name << std::endl;
    }
    ~GameObject() {
        std::cout << "  [파괴] " << name << std::endl;
    }
    void info() {
        std::cout << "  " << name << " (HP: " << hp << ")" << std::endl;
    }
};

void game_example() {
    std::cout << "\n=== 게임 오브젝트 관리 ===" << std::endl;

    // unique_ptr로 오브젝트 관리 → 벡터에서 빠지면 자동 파괴
    std::vector<std::unique_ptr<GameObject>> objects;

    objects.push_back(std::make_unique<GameObject>("용사", 100));
    objects.push_back(std::make_unique<GameObject>("마법사", 80));
    objects.push_back(std::make_unique<GameObject>("몬스터", 200));

    std::cout << "\n현재 오브젝트:" << std::endl;
    for (auto& obj : objects) {
        obj->info();
    }

    // 몬스터 제거 → 자동으로 메모리 해제됨
    std::cout << "\n몬스터 제거:" << std::endl;
    objects.pop_back();

    std::cout << "\n함수 끝 → 나머지도 자동 파괴:" << std::endl;
}

// ============================================
// ============================================
//
//     포인터 완전 정복 가이드
//     (여기서부터 포인터만 집중!)
//
// ============================================
// ============================================

// ============================================
// 6. 포인터가 뭔데? - 주소를 담는 변수
// ============================================
//
// 비유: 집(데이터)과 집 주소(포인터)
//
//   int a = 42;     ← 집을 짓고 42라는 사람이 삼
//   int* p = &a;    ← 그 집의 주소를 메모장에 적음
//
//   a  → 42가 들어있는 "집" 그 자체
//   &a → 그 집의 "주소" (& = "주소를 알려줘")
//   p  → 주소를 적어놓은 "메모장" (포인터 변수)
//   *p → 메모장에 적힌 주소로 찾아가서 "집 안을 봄" (* = "찾아가!")
//
void pointer_basics() {
    std::cout << "\n\n========================================" << std::endl;
    std::cout << "  6. 포인터가 뭔데?" << std::endl;
    std::cout << "========================================" << std::endl;

    int a = 42;

    // & → "주소를 알려줘" 연산자
    std::cout << "a의 값:  " << a << std::endl;    // 42
    std::cout << "a의 주소: " << &a << std::endl;   // 0x7fff... (메모리 주소)

    // 포인터 = 주소를 저장하는 변수
    // int* → "int형 데이터의 주소를 담을 변수"라는 뜻
    int* p = &a;   // p에 a의 주소를 저장

    std::cout << "\np의 값(= a의 주소): " << p << std::endl;   // a의 주소
    std::cout << "*p (주소로 찾아간 값): " << *p << std::endl;  // 42

    // * → "그 주소로 찾아가!" (역참조)
    *p = 100;  // p가 가리키는 곳(= a)의 값을 100으로 변경
    std::cout << "\n*p = 100 한 후:" << std::endl;
    std::cout << "a의 값: " << a << std::endl;   // 100 (a가 바뀜!)
    std::cout << "*p의 값: " << *p << std::endl;  // 100

    // 정리:
    //   int a = 42;    → 값을 담는 변수
    //   int* p = &a;   → 주소를 담는 변수 (포인터)
    //   *p             → 주소를 따라가서 값을 봄/바꿈
    //   &a             → 변수의 주소를 가져옴
}

// ============================================
// 7. 왜 포인터를 쓰는데? - 3가지 이유
// ============================================
//
//  이유 1: 함수에서 원본을 바꾸고 싶을 때
//  이유 2: 큰 데이터를 복사 없이 전달하고 싶을 때
//  이유 3: 동적으로 메모리를 할당하고 싶을 때
//
void why_pointers() {
    std::cout << "\n\n========================================" << std::endl;
    std::cout << "  7. 왜 포인터를 쓰는데?" << std::endl;
    std::cout << "========================================" << std::endl;

    // ---- 이유 1: 원본을 바꾸고 싶을 때 ----
    std::cout << "\n--- 이유 1: 원본 변경 ---" << std::endl;

    int hp = 100;
    int* hp_ptr = &hp;

    std::cout << "공격 전 HP: " << hp << std::endl;
    *hp_ptr = *hp_ptr - 30;   // 포인터로 원본 HP를 직접 깎음
    std::cout << "공격 후 HP: " << hp << std::endl;   // 70

    // C#에서는 ref 키워드로 하는 것:
    //   void Attack(ref int hp) { hp -= 30; }
    // C++에서는 포인터로 함:
    //   void Attack(int* hp) { *hp -= 30; }

    // ---- 이유 2: 큰 데이터를 복사 없이 전달 ----
    std::cout << "\n--- 이유 2: 복사 없이 전달 ---" << std::endl;

    // 100만개짜리 배열
    int big_data[10] = {1,2,3,4,5,6,7,8,9,10};

    int* data_ptr = big_data;  // 배열의 주소만 전달 (8바이트)
    // 만약 복사했으면 40바이트 복사해야 함
    // 100만개면 400만바이트(4MB) 복사 vs 8바이트 포인터 전달

    std::cout << "포인터로 접근: " << data_ptr[0] << ", " << data_ptr[1] << std::endl;

    // ---- 이유 3: 동적 할당 ----
    std::cout << "\n--- 이유 3: 동적 할당 ---" << std::endl;

    int size;
    size = 5;  // 실행 중에 크기가 정해짐

    int* dynamic_arr = new int[size];  // 실행 중에 크기 결정 가능!
    for (int i = 0; i < size; i++) {
        dynamic_arr[i] = i * 10;
        std::cout << dynamic_arr[i] << " ";
    }
    std::cout << std::endl;

    delete[] dynamic_arr;
}

// ============================================
// 8. * 와 & 헷갈리지 않기
// ============================================
//
//  * 는 2가지 의미가 있음 (헷갈리는 이유!)
//
//  1) 선언할 때: "이 변수는 포인터입니다"
//     int* p;    → p는 int의 주소를 담는 포인터
//
//  2) 사용할 때: "주소를 따라가!"  (역참조)
//     *p = 10;   → p가 가리키는 곳에 10을 넣어
//
//  & 도 2가지 의미가 있음
//
//  1) 변수 앞에: "주소를 알려줘"
//     &a         → a의 주소
//
//  2) 선언할 때: "참조(별명)입니다"
//     int& ref = a;  → ref는 a의 별명
//
void star_and_ampersand() {
    std::cout << "\n\n========================================" << std::endl;
    std::cout << "  8. * 와 & 정리" << std::endl;
    std::cout << "========================================" << std::endl;

    int a = 42;

    // --- * 의 2가지 의미 ---
    std::cout << "--- * 의 2가지 ---" << std::endl;
    int* p = &a;    // 선언: "p는 포인터야"
    std::cout << "*p = " << *p << std::endl;  // 사용: "따라가서 값 봐" → 42

    // --- & 의 2가지 의미 ---
    std::cout << "\n--- & 의 2가지 ---" << std::endl;
    std::cout << "&a = " << &a << std::endl;  // "a의 주소 알려줘"

    int& ref = a;   // 선언: "ref는 a의 별명이야"
    ref = 99;
    std::cout << "ref = 99 후, a = " << a << std::endl;  // 99

    // 표로 정리:
    //
    //  기호    선언할 때              사용할 때
    //  ─────────────────────────────────────────
    //   *     int* p (포인터 변수)    *p (따라가서 값 봐)
    //   &     int& r (참조/별명)     &a (주소 알려줘)
    //

    // --- 참조 vs 포인터 차이 ---
    std::cout << "\n--- 참조 vs 포인터 ---" << std::endl;

    int x = 10;

    int* ptr = &x;   // 포인터: 주소를 담는 변수, nullptr 가능
    int& ref2 = x;   // 참조: 별명, 반드시 대상 필요, null 불가

    *ptr = 20;        // 포인터는 *를 붙여야 값 접근
    ref2 = 30;        // 참조는 그냥 쓰면 됨 (편함)

    std::cout << "x = " << x << std::endl;  // 30

    // C#과 비교:
    //   C#의 ref 매개변수 = C++의 참조(&)
    //   C#은 포인터를 거의 안 씀 (unsafe에서만)
    //   C++은 둘 다 자주 씀
}

// ============================================
// 9. 포인터와 배열의 관계
// ============================================
//
//  배열 이름 = 첫 번째 원소의 주소 (포인터처럼 동작!)
//
//  int arr[3] = {10, 20, 30};
//
//  메모리:  [10] [20] [30]
//  주소:    100  104  108  (int는 4바이트씩)
//
//  arr     = 100 (첫 번째 주소)
//  arr + 1 = 104 (두 번째 주소, 자동으로 4바이트 뒤)
//  arr + 2 = 108 (세 번째 주소)
//
void pointer_and_array() {
    std::cout << "\n\n========================================" << std::endl;
    std::cout << "  9. 포인터와 배열" << std::endl;
    std::cout << "========================================" << std::endl;

    int arr[5] = {10, 20, 30, 40, 50};

    // 배열 이름 = 포인터
    int* p = arr;  // arr은 이미 주소라서 &안 붙여도 됨

    std::cout << "--- 배열을 포인터로 접근 ---" << std::endl;
    std::cout << "arr[0] = " << arr[0] << ",  *p     = " << *p << std::endl;
    std::cout << "arr[1] = " << arr[1] << ",  *(p+1) = " << *(p+1) << std::endl;
    std::cout << "arr[2] = " << arr[2] << ",  *(p+2) = " << *(p+2) << std::endl;

    // arr[i] 는 사실 *(arr + i) 의 줄임말!
    // 둘은 완전히 같음

    // 포인터 이동
    std::cout << "\n--- 포인터 이동 ---" << std::endl;
    p = arr;  // 처음으로
    for (int i = 0; i < 5; i++) {
        std::cout << "p[" << i << "] = " << *p << "  (주소: " << p << ")" << std::endl;
        p++;  // 다음 칸으로 (자동으로 4바이트 이동)
    }
}

// ============================================
// 10. nullptr - 아무것도 안 가리키는 포인터
// ============================================
//
//  비유: 빈 메모장 (주소가 안 적혀있음)
//
//  C#의 null과 같은 개념
//  null인 포인터를 따라가면 (*p) 프로그램이 죽음!
//
void nullptr_example() {
    std::cout << "\n\n========================================" << std::endl;
    std::cout << "  10. nullptr" << std::endl;
    std::cout << "========================================" << std::endl;

    int* p = nullptr;  // 아무것도 안 가리킴

    // 반드시 확인하고 사용해야 함!
    if (p != nullptr) {
        std::cout << *p << std::endl;
    } else {
        std::cout << "p는 nullptr! 접근하면 프로그램 죽음" << std::endl;
    }

    // 실전 패턴
    int value = 42;
    p = &value;  // 이제 가리키는 곳이 생김

    if (p) {  // nullptr이 아니면 (if문에서 자동으로 체크)
        std::cout << "p가 가리키는 값: " << *p << std::endl;
    }

    // C#과 비교:
    //   C#: if (obj != null) obj.Method();
    //   C#: obj?.Method();  (null 조건 연산자)
    //   C++: if (p != nullptr) p->Method();
    //   C++: null 조건 연산자 없음! 직접 체크해야 함
}

// ============================================
// 11. 화살표(->) - 포인터로 멤버 접근
// ============================================
//
//  . (점)   → 객체에서 직접 멤버 접근
//  -> (화살표) → 포인터에서 멤버 접근
//
//  player.hp      ← player가 객체일 때
//  player->hp     ← player가 포인터일 때
//
//  player->hp 는 (*player).hp 의 줄임말
//
void arrow_operator() {
    std::cout << "\n\n========================================" << std::endl;
    std::cout << "  11. 화살표 연산자 (->)" << std::endl;
    std::cout << "========================================" << std::endl;

    // 간단한 구조체
    struct Player {
        std::string name;
        int hp;
    };

    Player hero = {"용사", 100};
    Player* p = &hero;

    // 점(.) vs 화살표(->)
    std::cout << "hero.name  = " << hero.name << std::endl;   // 객체로 접근
    std::cout << "p->name    = " << p->name << std::endl;     // 포인터로 접근
    std::cout << "(*p).name  = " << (*p).name << std::endl;   // 이것과 같음

    // p->hp 는 (*p).hp 를 편하게 쓰는 것!
    // 매번 (*p).hp 쓰기 귀찮으니까 -> 를 만든 것

    p->hp -= 30;
    std::cout << "\n공격 후: " << p->name << " HP = " << p->hp << std::endl;
}

// ============================================
// 12. 포인터 총정리 - 한눈에 보기
// ============================================
void pointer_summary() {
    std::cout << "\n\n========================================" << std::endl;
    std::cout << "  12. 포인터 총정리" << std::endl;
    std::cout << "========================================" << std::endl;

    std::cout << R"(
    ┌─────────────────────────────────────────────────┐
    │              포인터 치트시트                      │
    ├──────────────┬──────────────────────────────────┤
    │  int a = 42  │  값이 42인 변수                   │
    │  int* p      │  포인터 변수 선언                  │
    │  p = &a      │  a의 주소를 p에 저장               │
    │  *p          │  p가 가리키는 값 (42)              │
    │  *p = 10     │  p가 가리키는 곳에 10 넣기          │
    │  nullptr     │  아무것도 안 가리킴 (C#의 null)     │
    │  p->member   │  포인터로 멤버 접근 (= (*p).member) │
    │  p++         │  다음 메모리 칸으로 이동             │
    ├──────────────┴──────────────────────────────────┤
    │  비유 정리:                                      │
    │  변수(a)  = 집                                   │
    │  값(42)   = 집에 사는 사람                        │
    │  주소(&a) = 집 주소                               │
    │  포인터(p)= 집 주소가 적힌 메모장                  │
    │  *p       = 메모장 보고 집에 찾아감                │
    │  nullptr  = 빈 메모장 (주소 안 적힘)               │
    └────────────────────────────────────────────────┘
    )" << std::endl;
}

// ============================================
// ============================================
//
//     포인터 고급편
//     (이중 포인터, 함수 포인터, void*, const)
//
//     어렵게 생각하지 마세요!
//     하나씩 천천히 비유로 설명합니다.
//
// ============================================
// ============================================


// ============================================
// 13. 이중 포인터 (**) - 메모장의 메모장
// ============================================
//
//  비유: 택배 시스템
//
//  물건(값)     = 42
//  물건 위치(주소) = 창고 A
//  포인터(*)     = "창고 A에 있어" 라고 적힌 메모
//  이중포인터(**) = "그 메모가 서랍 B에 있어" 라고 적힌 메모
//
//  즉, 메모를 찾기 위한 메모!
//
void double_pointer() {
    std::cout << "\n\n========================================" << std::endl;
    std::cout << "  13. 이중 포인터 (**)" << std::endl;
    std::cout << "========================================" << std::endl;

    // --- 기본 개념 ---
    int candy = 42;          // 사탕 42개
    int* bag = &candy;       // 가방에 사탕 위치 적어놓음
    int** locker = &bag;     // 사물함에 가방 위치 적어놓음

    std::cout << "candy  = " << candy << std::endl;    // 42 (사탕 직접 보기)
    std::cout << "*bag   = " << *bag << std::endl;     // 42 (가방 메모 따라가기)
    std::cout << "**locker = " << **locker << std::endl; // 42 (사물함→가방→사탕)

    // 그림으로 보면:
    //
    //  locker         bag          candy
    //  [bag주소]  →  [candy주소]  →  [42]
    //
    //  **locker = *(  *locker  )
    //           = *(   bag     )
    //           = candy
    //           = 42

    // --- 언제 쓰나? ---
    // 함수 안에서 "포인터가 가리키는 대상"을 바꾸고 싶을 때
    std::cout << "\n--- 실전 예시: 보물 교체 ---" << std::endl;

    int gold = 100;
    int diamond = 9999;
    int* treasure = &gold;   // 지금 보물 = 금

    std::cout << "교체 전: " << *treasure << std::endl;  // 100

    // 보물을 금 → 다이아로 바꾸는 함수
    // 포인터 자체를 바꿔야 하니까 이중 포인터 필요!
    //
    // 왜? 함수에 int* 를 넘기면 복사본이라 원본 안 바뀜
    // int** 를 넘기면 원본 포인터를 바꿀 수 있음
    auto change_treasure = [](int** ptr, int* new_target) {
        *ptr = new_target;  // 포인터가 가리키는 곳을 변경
    };

    change_treasure(&treasure, &diamond);
    std::cout << "교체 후: " << *treasure << std::endl;  // 9999

    // --- 솔직한 이야기 ---
    // 이중 포인터는 C 스타일이고, 현대 C++에서는
    // 참조를 쓰면 더 쉽게 할 수 있음:
    //
    //   void change(int*& ptr) { ptr = &diamond; }
    //               ^^^^
    //               포인터의 참조 → 이중포인터 안 써도 됨!
    //
    // 그래서 실무에서 ** 직접 쓸 일은 많지 않음
}


// ============================================
// 14. 함수 포인터 - 함수를 변수에 담기
// ============================================
//
//  비유: 리모컨
//
//  리모컨 버튼 하나에 다른 기능을 등록할 수 있듯이
//  변수 하나에 다른 함수를 넣을 수 있음
//
//  C#의 delegate, Action, Func 와 같은 개념!
//

// 먼저 함수 3개 준비
int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }
int mul(int a, int b) { return a * b; }

void function_pointer() {
    std::cout << "\n\n========================================" << std::endl;
    std::cout << "  14. 함수 포인터" << std::endl;
    std::cout << "========================================" << std::endl;

    // --- 기본: 함수를 변수에 담기 ---
    std::cout << "--- 기본 ---" << std::endl;

    // int (*calc)(int, int) 의 의미:
    //  int     → 리턴 타입
    //  (*calc) → calc는 포인터 (함수를 가리킴)
    //  (int, int) → 매개변수
    int (*calc)(int, int);

    calc = add;      // calc 리모컨에 "더하기" 등록
    std::cout << "calc(10, 3) = " << calc(10, 3) << std::endl;  // 13

    calc = sub;      // 같은 리모컨에 "빼기"로 변경
    std::cout << "calc(10, 3) = " << calc(10, 3) << std::endl;  // 7

    calc = mul;      // "곱하기"로 변경
    std::cout << "calc(10, 3) = " << calc(10, 3) << std::endl;  // 30

    // --- 배열에 담기: 계산기 만들기 ---
    std::cout << "\n--- 계산기 ---" << std::endl;

    int (*operations[3])(int, int) = {add, sub, mul};
    const char* names[3] = {"더하기", "빼기", "곱하기"};

    for (int i = 0; i < 3; i++) {
        std::cout << names[i] << ": 10, 3 = " << operations[i](10, 3) << std::endl;
    }

    // --- 콜백: 다른 함수에 함수를 넘기기 ---
    std::cout << "\n--- 콜백 ---" << std::endl;

    // "두 수를 받아서 뭘 할지"를 밖에서 정해줌
    auto apply = [](int a, int b, int (*func)(int, int)) {
        return func(a, b);
    };

    std::cout << "apply(5, 3, add) = " << apply(5, 3, add) << std::endl;
    std::cout << "apply(5, 3, mul) = " << apply(5, 3, mul) << std::endl;

    // C#으로 비교하면:
    //   Func<int, int, int> calc = Add;     // C#
    //   int (*calc)(int, int) = add;         // C++ (같은 것)
    //
    // 근데 C++에서는 std::function이 더 편함:
    //   std::function<int(int, int)> calc = add;  // 현대 C++ 방식
}


// ============================================
// 15. void* - 아무거나 담는 포인터
// ============================================
//
//  비유: 만능 택배 상자
//
//  int* → 정수만 담는 전용 상자
//  double* → 실수만 담는 전용 상자
//  void* → 아무거나 담는 만능 상자
//          대신 꺼낼 때 "이게 뭔지" 알려줘야 함!
//
//  C#의 object와 비슷한 개념
//
void void_pointer() {
    std::cout << "\n\n========================================" << std::endl;
    std::cout << "  15. void* (만능 포인터)" << std::endl;
    std::cout << "========================================" << std::endl;

    int a = 42;
    double b = 3.14;

    void* box;   // 만능 상자

    // 정수 담기
    box = &a;
    // std::cout << *box;  // 에러! void*는 "뭐가 들었는지" 모름
    std::cout << "int 꺼내기: " << *(int*)box << std::endl;
    //                          ^^^^^^^ "이거 int야!" 라고 알려줌 (캐스팅)

    // 실수 담기
    box = &b;
    std::cout << "double 꺼내기: " << *(double*)box << std::endl;

    // 주의: 잘못된 타입으로 꺼내면?
    box = &a;   // int를 넣었는데
    // *(double*)box  → 엉뚱한 값! (타입이 안 맞으니까)
    // 컴파일은 되지만 결과가 이상해짐

    // C#과 비교:
    //   object box = 42;              // C#
    //   int val = (int)box;           // C# 언박싱
    //
    //   void* box = &a;              // C++
    //   int val = *(int*)box;        // C++ 캐스팅
    //
    // 차이: C#은 잘못 캐스팅하면 예외 발생 (안전)
    //       C++은 잘못 캐스팅하면 쓰레기 값 (위험!)
    //
    // 그래서 현대 C++에서는 void* 대신
    // std::variant, std::any, 템플릿을 씀

    std::cout << "\n실무에서 void*를 보는 곳:" << std::endl;
    std::cout << "  - C 라이브러리 연동 (malloc 리턴값)" << std::endl;
    std::cout << "  - 콜백 함수의 user_data 매개변수" << std::endl;
    std::cout << "  - 직접 만들 일은 거의 없음!" << std::endl;
}


// ============================================
// 16. const 포인터 - 읽기 전용 잠금
// ============================================
//
//  비유: 박물관 vs 내 방
//
//  박물관 작품 = 보기만 가능 (const)
//  내 방 물건 = 마음대로 변경 가능
//
//  const를 붙이면 "수정 금지!"
//
void const_pointer() {
    std::cout << "\n\n========================================" << std::endl;
    std::cout << "  16. const 포인터" << std::endl;
    std::cout << "========================================" << std::endl;

    int a = 10;
    int b = 20;

    // --- 타입 1: 값을 못 바꿈 (가장 많이 씀) ---
    std::cout << "--- const int* (값 수정 금지) ---" << std::endl;
    const int* p1 = &a;
    // *p1 = 99;    // 에러! 값 변경 불가 (박물관 작품)
    p1 = &b;        // OK! 다른 곳을 가리키는 건 가능
    std::cout << "*p1 = " << *p1 << std::endl;  // 20

    // 실전: 함수에서 "보기만 하고 수정 안 할게" 약속
    // void print(const int* data, int size) { ... }

    // --- 타입 2: 가리키는 곳을 못 바꿈 ---
    std::cout << "\n--- int* const (가리키는 대상 변경 금지) ---" << std::endl;
    int* const p2 = &a;
    *p2 = 99;       // OK! 값은 바꿀 수 있음
    // p2 = &b;     // 에러! 다른 곳을 가리킬 수 없음
    std::cout << "*p2 = " << *p2 << std::endl;  // 99

    // --- 타입 3: 둘 다 못 바꿈 ---
    std::cout << "\n--- const int* const (둘 다 금지) ---" << std::endl;
    const int* const p3 = &a;
    // *p3 = 100;   // 에러!
    // p3 = &b;     // 에러!
    std::cout << "*p3 = " << *p3 << std::endl;  // 99 (위에서 바꿨으니까)

    // 외우는 법:
    //
    //  const int* p   → const가 int 앞 → "값"을 못 바꿈
    //  int* const p   → const가 p 앞  → "포인터"를 못 바꿈
    //  const int* const p → 둘 다 못 바꿈
    //
    //  * 기준으로:
    //  왼쪽에 const → 값 잠금
    //  오른쪽에 const → 포인터 잠금

    std::cout << "\n┌───────────────────────────────────────┐" << std::endl;
    std::cout << "│  const 위치      값수정  대상변경      │" << std::endl;
    std::cout << "├───────────────────────────────────────┤" << std::endl;
    std::cout << "│  const int* p     X       O           │" << std::endl;
    std::cout << "│  int* const p     O       X           │" << std::endl;
    std::cout << "│  const int* const X       X           │" << std::endl;
    std::cout << "└───────────────────────────────────────┘" << std::endl;
}


// ============================================
// 17. 포인터 단계별 가이드 - 뭘 써야 하나?
// ============================================
void pointer_level_guide() {
    std::cout << "\n\n========================================" << std::endl;
    std::cout << "  17. 뭘 써야 하나? 우선순위" << std::endl;
    std::cout << "========================================" << std::endl;

    std::cout << R"(

    현대 C++에서의 우선순위:

    ┌─────────────────────────────────────────────┐
    │  1순위: 일반 변수                             │
    │     int a = 42;                              │
    │     → 가능하면 그냥 변수 쓰세요                │
    ├─────────────────────────────────────────────┤
    │  2순위: 참조 (&)                              │
    │     void attack(Player& p) { p.hp -= 30; }   │
    │     → 원본 수정 필요하면 참조                   │
    ├─────────────────────────────────────────────┤
    │  3순위: 스마트 포인터                          │
    │     auto p = make_unique<Player>();           │
    │     → new가 필요하면 스마트 포인터              │
    ├─────────────────────────────────────────────┤
    │  4순위: 원시 포인터 (*)                        │
    │     void draw(Widget* w) { if(w) w->draw(); } │
    │     → nullptr 표현이 필요할 때만                │
    ├─────────────────────────────────────────────┤
    │  거의 안 씀: 이중 포인터 (**)                   │
    │     → C 라이브러리 연동할 때나 가끔             │
    └─────────────────────────────────────────────┘

    C#과 비교:

    ┌────────────────┬────────────────────────────┐
    │  C#             │  C++                       │
    ├────────────────┼────────────────────────────┤
    │  int x          │  int x          (같음)     │
    │  ref int x      │  int& x         (참조)     │
    │  int? x         │  int* x         (널 가능)  │
    │  using var      │  unique_ptr     (자동해제)  │
    │  object         │  void*          (만능타입)  │
    │  delegate       │  함수포인터/function        │
    └────────────────┴────────────────────────────┘

    )" << std::endl;
}


int main() {
    stack_vs_heap();
    memory_leak_bad();
    smart_pointers();
    move_semantics();
    game_example();

    // 포인터 완전 정복
    pointer_basics();
    why_pointers();
    star_and_ampersand();
    pointer_and_array();
    nullptr_example();
    arrow_operator();
    pointer_summary();

    // 포인터 고급편
    double_pointer();
    function_pointer();
    void_pointer();
    const_pointer();
    pointer_level_guide();

    return 0;
}
