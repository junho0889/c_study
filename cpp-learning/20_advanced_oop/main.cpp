/*
 * =============================================================================
 *  C++ 학습 20장: 고급 OOP (Advanced Object-Oriented Programming)
 * =============================================================================
 *
 *  이 파일은 C++의 고급 객체지향 프로그래밍 개념을 심도 있게 다룹니다.
 *  실무에서 자주 발생하는 함정과 올바른 설계 방법을 학습합니다.
 *
 *  목차:
 *    레슨 1: 복사 생성자 & 대입 연산자 (얕은 복사 vs 깊은 복사)
 *    레슨 2: 이동 생성자 & 이동 대입 (rvalue 참조, std::move)
 *    레슨 3: Rule of 3/5/0
 *    레슨 4: CRTP (Curiously Recurring Template Pattern)
 *    레슨 5: 다중 상속과 가상 상속 (다이아몬드 문제)
 *    레슨 6: 타입 캐스팅 심화 (4가지 C++ 캐스트)
 *    레슨 7: 객체 슬라이싱 & 실전 종합 예제
 *
 *  컴파일: g++ -std=c++17 -o advanced_oop main.cpp
 *  실행:   ./advanced_oop
 *
 * =============================================================================
 *
 *  ┌──────────────────────────────────────────────────────────────────┐
 *  │              특수 멤버 함수 (Special Member Functions)            │
 *  ├──────────────────────────────────────────────────────────────────┤
 *  │                                                                  │
 *  │  1. 기본 생성자         MyClass()                                │
 *  │  2. 소멸자              ~MyClass()                               │
 *  │  3. 복사 생성자         MyClass(const MyClass&)                  │
 *  │  4. 복사 대입 연산자    MyClass& operator=(const MyClass&)       │
 *  │  5. 이동 생성자         MyClass(MyClass&&)                       │
 *  │  6. 이동 대입 연산자    MyClass& operator=(MyClass&&)            │
 *  │                                                                  │
 *  │  Rule of 3: 3,4 중 하나를 정의하면 2,3,4 모두 정의하라          │
 *  │  Rule of 5: 위에 5,6까지 추가                                    │
 *  │  Rule of 0: 가능하면 아무것도 정의하지 마라 (스마트 포인터 사용) │
 *  │                                                                  │
 *  └──────────────────────────────────────────────────────────────────┘
 *
 * =============================================================================
 */

#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <utility>
#include <cstring>
#include <cassert>
#include <algorithm>
#include <chrono>
#include <typeinfo>

using namespace std;


// =============================================================================
// 레슨 1: 복사 생성자 & 대입 연산자
// =============================================================================
/*
 *  얕은 복사 (Shallow Copy) vs 깊은 복사 (Deep Copy)
 *
 *  얕은 복사의 위험성:
 *  ┌──────────┐     ┌──────────┐
 *  │  obj1    │     │  obj2    │
 *  │ data ────┼──┐  │ data ────┼──┐
 *  └──────────┘  │  └──────────┘  │
 *                │                │
 *                v                v
 *            ┌──────────────────────┐
 *            │  같은 메모리 영역!!    │   <- 두 객체가 같은 메모리를 가리킴
 *            │  [H][e][l][l][o][\0] │       obj1 소멸 시 메모리 해제
 *            └──────────────────────┘       -> obj2가 댕글링 포인터!
 *
 *  깊은 복사:
 *  ┌──────────┐     ┌──────────┐
 *  │  obj1    │     │  obj2    │
 *  │ data ────┼──┐  │ data ────┼──┐
 *  └──────────┘  │  └──────────┘  │
 *                v                v
 *  ┌──────────────────┐  ┌──────────────────┐
 *  │  [H][e][l][l][o] │  │  [H][e][l][l][o] │  <- 독립된 메모리 복사본
 *  └──────────────────┘  └──────────────────┘
 */

namespace Lesson1 {

// 위험한 클래스: 기본 복사 생성자가 얕은 복사를 함
class DangerousString {
private:
    char* data;
    size_t length;

public:
    DangerousString(const char* str = "") {
        length = strlen(str);
        data = new char[length + 1];
        strcpy(data, str);
        cout << "  [생성자] \"" << data << "\" 생성 (주소: "
             << (void*)data << ")" << endl;
    }

    ~DangerousString() {
        cout << "  [소멸자] \"" << data << "\" 소멸 (주소: "
             << (void*)data << ")" << endl;
        delete[] data;
    }

    // 주의: 복사 생성자와 대입 연산자를 정의하지 않으면
    // 컴파일러가 자동으로 '얕은 복사'를 수행합니다!
    // -> 동일한 메모리를 두 번 delete하는 더블 프리 발생!

    const char* c_str() const { return data; }
};

// 안전한 클래스: 깊은 복사를 직접 구현
class SafeString {
private:
    char* data;
    size_t length;

public:
    // 기본 생성자
    SafeString(const char* str = "") {
        length = strlen(str);
        data = new char[length + 1];
        strcpy(data, str);
        cout << "  [생성자] \"" << data << "\" (주소: "
             << (void*)data << ")" << endl;
    }

    // 복사 생성자 - 깊은 복사!
    /*
     *  SafeString b = a;  또는  SafeString b(a);  일 때 호출됨
     *
     *  1. 새로운 메모리 할당
     *  2. 원본 데이터를 새 메모리에 복사
     *  3. 원본과 완전히 독립된 객체 생성
     */
    SafeString(const SafeString& other) {
        length = other.length;
        data = new char[length + 1];      // 새 메모리 할당!
        strcpy(data, other.data);          // 데이터 복사!
        cout << "  [복사 생성자] \"" << data << "\" 복사됨 (새 주소: "
             << (void*)data << ")" << endl;
    }

    // 복사 대입 연산자 - 깊은 복사!
    /*
     *  a = b;  일 때 호출됨 (이미 초기화된 객체에 대입)
     *
     *  주의사항:
     *  1. 자기 대입 검사 (a = a 방지)
     *  2. 기존 메모리 해제
     *  3. 새 메모리 할당 및 복사
     */
    SafeString& operator=(const SafeString& other) {
        cout << "  [복사 대입] ";
        if (this == &other) {    // 자기 대입 검사!
            cout << "자기 대입 감지, 무시" << endl;
            return *this;
        }

        delete[] data;           // 기존 메모리 해제

        length = other.length;
        data = new char[length + 1];
        strcpy(data, other.data);
        cout << "\"" << data << "\" 대입됨 (새 주소: "
             << (void*)data << ")" << endl;
        return *this;            // 연쇄 대입을 위해 *this 반환
    }

    // 소멸자
    ~SafeString() {
        cout << "  [소멸자] \"" << data << "\" 해제" << endl;
        delete[] data;
    }

    const char* c_str() const { return data; }
    size_t size() const { return length; }

    // 문자열 연결 (새 객체 반환)
    SafeString operator+(const SafeString& other) const {
        char* newData = new char[length + other.length + 1];
        strcpy(newData, data);
        strcat(newData, other.data);
        SafeString result(newData);
        delete[] newData;
        return result;
    }

    friend ostream& operator<<(ostream& os, const SafeString& s) {
        return os << s.data;
    }
};

void demo() {
    cout << "=== 레슨 1: 복사 생성자 & 대입 연산자 ===" << endl << endl;

    cout << "--- 안전한 깊은 복사 ---" << endl;
    {
        SafeString original("Hello");
        SafeString copy = original;        // 복사 생성자 호출
        SafeString another("World");
        another = original;                 // 복사 대입 연산자 호출

        cout << "  original: " << original << endl;
        cout << "  copy:     " << copy << endl;
        cout << "  another:  " << another << endl;
        cout << "  (스코프 종료, 소멸자 호출...)" << endl;
    }

    cout << endl << "  ** 주의: DangerousString은 얕은 복사로 인해" << endl;
    cout << "  ** 더블 프리가 발생할 수 있습니다 (데모 생략)" << endl;
    cout << endl;
}

} // namespace Lesson1


// =============================================================================
// 레슨 2: 이동 생성자 & 이동 대입 연산자
// =============================================================================
/*
 *  이동 시맨틱스 (Move Semantics) - C++11의 혁명적 기능
 *
 *  복사 vs 이동:
 *  ┌─────────┐  복사  ┌─────────┐    새 메모리 할당 + 데이터 복사 = 비용 큼
 *  │  원본   │ =====> │  복사본  │
 *  │ [데이터]│        │ [데이터] │   원본과 복사본 모두 독립적으로 유효
 *  └─────────┘        └─────────┘
 *
 *  ┌─────────┐  이동  ┌─────────┐    포인터만 이전 = 비용 거의 없음
 *  │  원본   │ -----> │  새객체  │
 *  │ [null]  │        │ [데이터] │   원본은 비어있음 (사용하면 안 됨)
 *  └─────────┘        └─────────┘
 *
 *  lvalue vs rvalue:
 *  - lvalue: 이름이 있고, 주소를 가질 수 있는 값 (변수)
 *    int x = 10;      // x는 lvalue
 *  - rvalue: 임시 값, 곧 소멸할 값
 *    x + 5;           // (x+5)의 결과는 rvalue
 *    string("temp");  // 임시 객체는 rvalue
 *
 *  && (rvalue 참조): rvalue만 받을 수 있는 참조
 */

namespace Lesson2 {

class MoveString {
private:
    char* data;
    size_t length;
    string name;   // 디버깅용 이름

public:
    // 기본 생성자
    MoveString(const char* str = "", const string& n = "unnamed")
        : name(n) {
        length = strlen(str);
        data = new char[length + 1];
        strcpy(data, str);
        cout << "  [생성자] " << name << " = \"" << data << "\"" << endl;
    }

    // 복사 생성자 (비용: 메모리 할당 + 복사)
    MoveString(const MoveString& other) : name(other.name + "_copy") {
        length = other.length;
        data = new char[length + 1];
        strcpy(data, other.data);
        cout << "  [복사 생성자] " << name << " <- \"" << data
             << "\" (비용: new + strcpy)" << endl;
    }

    // 이동 생성자 (비용: 포인터 이전만!)
    /*
     *  핵심 동작:
     *  1. 원본의 데이터 포인터를 가져옴 (소유권 이전)
     *  2. 원본의 포인터를 nullptr로 설정 (이중 삭제 방지)
     *  3. 메모리 할당이 없으므로 매우 빠름!
     */
    MoveString(MoveString&& other) noexcept
        : data(other.data), length(other.length), name(other.name + "_moved") {
        other.data = nullptr;    // 원본의 소유권 해제!
        other.length = 0;
        cout << "  [이동 생성자] " << name << " <- 포인터 이전 (비용: 거의 0)"
             << endl;
    }

    // 복사 대입 연산자
    MoveString& operator=(const MoveString& other) {
        if (this == &other) return *this;
        delete[] data;
        length = other.length;
        data = new char[length + 1];
        strcpy(data, other.data);
        cout << "  [복사 대입] " << name << " = \"" << data << "\"" << endl;
        return *this;
    }

    // 이동 대입 연산자
    MoveString& operator=(MoveString&& other) noexcept {
        if (this == &other) return *this;
        delete[] data;           // 기존 데이터 해제

        data = other.data;       // 소유권 이전
        length = other.length;
        other.data = nullptr;    // 원본 무효화
        other.length = 0;
        cout << "  [이동 대입] " << name << " <- 포인터 이전" << endl;
        return *this;
    }

    ~MoveString() {
        if (data) {
            cout << "  [소멸자] " << name << " \"" << data << "\" 해제" << endl;
            delete[] data;
        } else {
            cout << "  [소멸자] " << name << " (이미 이동됨, 해제할 것 없음)" << endl;
        }
    }

    const char* c_str() const { return data ? data : "(이동됨)"; }
};

// std::move의 역할: lvalue를 rvalue 참조로 캐스팅
// 실제로 이동하지는 않음! 이동 가능하다고 표시만 함
void demo() {
    cout << "=== 레슨 2: 이동 생성자 & 이동 대입 ===" << endl << endl;

    cout << "--- 복사 vs 이동 비교 ---" << endl;
    {
        MoveString a("Very long string data for testing", "a");
        cout << endl;

        // 복사: 새 메모리 할당 + 데이터 복사
        MoveString b = a;
        cout << "  a = \"" << a.c_str() << "\"" << endl;
        cout << "  b = \"" << b.c_str() << "\"" << endl;
        cout << endl;

        // 이동: 포인터만 이전 (훨씬 빠름!)
        MoveString c = std::move(a);   // a를 rvalue로 캐스팅
        cout << "  a = \"" << a.c_str() << "\"  (이동 후 비어있음!)" << endl;
        cout << "  c = \"" << c.c_str() << "\"" << endl;
        cout << endl;

        cout << "  ** std::move 후 원본(a)은 유효하지만 비어있는 상태" << endl;
        cout << "  ** 이동된 객체를 다시 사용하면 안 됩니다!" << endl;
        cout << endl;

        cout << "  (스코프 종료...)" << endl;
    }

    // 실전: vector에서의 이동
    cout << endl << "--- vector의 이동 활용 ---" << endl;
    cout << "  vector가 재할당할 때 이동 생성자를 사용하면" << endl;
    cout << "  복사 대신 포인터만 옮기므로 성능이 크게 향상됩니다." << endl;
    cout << "  (noexcept 선언이 중요! 없으면 vector는 복사를 사용)" << endl;
    cout << endl;
}

} // namespace Lesson2


// =============================================================================
// 레슨 3: Rule of 3/5/0
// =============================================================================
/*
 *  ┌──────────────────────────────────────────────────────────────────┐
 *  │                    Rule of Three (3의 규칙)                       │
 *  ├──────────────────────────────────────────────────────────────────┤
 *  │  다음 셋 중 하나를 직접 정의한다면, 나머지 둘도 정의하라:        │
 *  │                                                                  │
 *  │  1. 소멸자              ~MyClass()                               │
 *  │  2. 복사 생성자         MyClass(const MyClass&)                  │
 *  │  3. 복사 대입 연산자    MyClass& operator=(const MyClass&)       │
 *  │                                                                  │
 *  │  이유: 셋 중 하나가 필요하다면, 클래스가 자원을 관리하고 있다는  │
 *  │        의미이므로 나머지도 올바르게 처리해야 한다.                │
 *  └──────────────────────────────────────────────────────────────────┘
 *
 *  ┌──────────────────────────────────────────────────────────────────┐
 *  │                    Rule of Five (5의 규칙)                        │
 *  ├──────────────────────────────────────────────────────────────────┤
 *  │  C++11 이후: Rule of Three에 두 가지를 추가:                     │
 *  │                                                                  │
 *  │  4. 이동 생성자         MyClass(MyClass&&)                       │
 *  │  5. 이동 대입 연산자    MyClass& operator=(MyClass&&)            │
 *  │                                                                  │
 *  │  이동 시맨틱스를 지원하여 성능을 최적화한다.                     │
 *  └──────────────────────────────────────────────────────────────────┘
 *
 *  ┌──────────────────────────────────────────────────────────────────┐
 *  │                    Rule of Zero (0의 규칙)                        │
 *  ├──────────────────────────────────────────────────────────────────┤
 *  │  가장 권장되는 방법!                                              │
 *  │                                                                  │
 *  │  특수 멤버 함수를 하나도 직접 정의하지 마라.                      │
 *  │  대신 스마트 포인터(unique_ptr, shared_ptr)와 RAII를 사용하라.   │
 *  │  컴파일러가 자동 생성하는 기본 함수가 올바르게 동작하도록 설계.  │
 *  └──────────────────────────────────────────────────────────────────┘
 */

namespace Lesson3 {

// --- Rule of Five 완전한 예제 ---
class ResourceManager {
private:
    int* data;
    size_t size;
    string label;

public:
    // 생성자
    ResourceManager(size_t sz, const string& lbl = "unnamed")
        : size(sz), label(lbl) {
        data = new int[size];
        for (size_t i = 0; i < size; i++) data[i] = static_cast<int>(i);
        cout << "  [생성] " << label << " (크기: " << size << ")" << endl;
    }

    // 1. 소멸자
    ~ResourceManager() {
        cout << "  [소멸] " << label << endl;
        delete[] data;
    }

    // 2. 복사 생성자
    ResourceManager(const ResourceManager& other)
        : size(other.size), label(other.label + "_copy") {
        data = new int[size];
        copy(other.data, other.data + size, data);
        cout << "  [복사생성] " << label << endl;
    }

    // 3. 복사 대입 연산자 (copy-and-swap 관용구)
    /*
     *  Copy-and-Swap 관용구:
     *  1. 매개변수를 값으로 받음 (복사 발생)
     *  2. 복사본과 swap
     *  3. 함수 종료 시 복사본(구 데이터)이 자동 소멸
     *
     *  장점: 예외 안전성, 자기 대입 안전, 코드 간결
     */
    ResourceManager& operator=(ResourceManager other) {  // 값으로 받기!
        cout << "  [복사대입] " << label << " (copy-and-swap)" << endl;
        swap(data, other.data);
        swap(size, other.size);
        // other가 함수 종료 시 기존 데이터를 가지고 소멸됨
        return *this;
    }

    // 4. 이동 생성자
    ResourceManager(ResourceManager&& other) noexcept
        : data(other.data), size(other.size),
          label(std::move(other.label) + "_moved") {
        other.data = nullptr;
        other.size = 0;
        cout << "  [이동생성] " << label << endl;
    }

    // 5. 이동 대입 연산자
    // 주의: copy-and-swap을 사용하면 이동 대입도 자동으로 처리됨
    // (매개변수가 값이므로 rvalue면 이동 생성자가 호출됨)

    void print() const {
        cout << "  " << label << ": [";
        for (size_t i = 0; i < size && i < 5; i++) {
            cout << data[i];
            if (i < size - 1 && i < 4) cout << ", ";
        }
        if (size > 5) cout << ", ...";
        cout << "] (크기: " << size << ")" << endl;
    }
};

// --- Rule of Zero 예제 ---
// 스마트 포인터를 사용하면 특수 멤버 함수가 필요 없다!
class ModernResource {
private:
    unique_ptr<int[]> data;     // 스마트 포인터가 자원 관리
    size_t size;
    string label;

public:
    ModernResource(size_t sz, const string& lbl = "modern")
        : data(make_unique<int[]>(sz)), size(sz), label(lbl) {
        for (size_t i = 0; i < size; i++) data[i] = static_cast<int>(i * 10);
        cout << "  [Modern 생성] " << label << endl;
    }

    // 소멸자, 복사, 이동 -> 전부 정의하지 않음!
    // unique_ptr은 복사 불가, 이동만 가능
    // 필요시 복사를 원한다면 clone() 메서드를 만들 수 있음

    ModernResource(ModernResource&&) = default;             // 이동 허용
    ModernResource& operator=(ModernResource&&) = default;  // 이동 대입 허용

    void print() const {
        cout << "  " << label << ": [";
        for (size_t i = 0; i < size && i < 5; i++) {
            cout << data[i];
            if (i < size - 1 && i < 4) cout << ", ";
        }
        cout << "]" << endl;
    }
};

void demo() {
    cout << "=== 레슨 3: Rule of 3/5/0 ===" << endl << endl;

    cout << "--- Rule of Five (ResourceManager) ---" << endl;
    {
        ResourceManager rm1(5, "rm1");
        rm1.print();

        ResourceManager rm2 = rm1;       // 복사 생성자
        rm2.print();

        ResourceManager rm3(3, "rm3");
        rm3 = rm1;                        // 복사 대입 (copy-and-swap)

        ResourceManager rm4 = std::move(rm1);  // 이동 생성자
        rm4.print();
        cout << "  (스코프 종료...)" << endl;
    }

    cout << endl << "--- Rule of Zero (ModernResource) ---" << endl;
    {
        ModernResource mr1(5, "mr1");
        mr1.print();

        // ModernResource mr2 = mr1;     // 컴파일 오류! unique_ptr은 복사 불가
        ModernResource mr2 = std::move(mr1);  // 이동은 가능
        mr2.print();
        cout << "  (스코프 종료...)" << endl;
    }
    cout << endl;
}

} // namespace Lesson3


// =============================================================================
// 레슨 4: CRTP (Curiously Recurring Template Pattern)
// =============================================================================
/*
 *  CRTP: 파생 클래스가 자기 자신을 기반 클래스의 템플릿 인자로 전달
 *
 *  일반 다형성 (가상 함수):          CRTP (정적 다형성):
 *  ┌──────────┐                     ┌──────────────────┐
 *  │  Base    │                     │  Base<Derived>   │
 *  │ virtual  │                     │  (템플릿)         │
 *  │ func()   │                     │  func()           │
 *  └────┬─────┘                     └────────┬─────────┘
 *       │                                    │
 *  ┌────┴─────┐                     ┌────────┴─────────┐
 *  │ Derived  │                     │   Derived        │
 *  │ func()   │                     │   : Base<Derived>│
 *  │ override │                     │   impl()          │
 *  └──────────┘                     └──────────────────┘
 *
 *  가상 함수: vtable 조회 비용 (런타임)
 *  CRTP:      컴파일 타임에 바인딩 -> 인라인 가능, 더 빠름!
 */

namespace Lesson4 {

// --- CRTP 기본 패턴 ---
template <typename Derived>
class Shape {
public:
    // 정적 다형성: 컴파일 타임에 올바른 함수가 결정됨
    double area() const {
        // static_cast로 파생 클래스로 캐스팅
        return static_cast<const Derived*>(this)->areaImpl();
    }

    string name() const {
        return static_cast<const Derived*>(this)->nameImpl();
    }

    // CRTP로 공통 기능 제공
    void describe() const {
        cout << "  도형: " << name() << ", 면적: " << area() << endl;
    }
};

class Circle : public Shape<Circle> {
    double radius;
public:
    Circle(double r) : radius(r) {}

    double areaImpl() const { return 3.14159265 * radius * radius; }
    string nameImpl() const { return "원 (반지름=" + to_string(radius) + ")"; }
};

class Rectangle : public Shape<Rectangle> {
    double width, height;
public:
    Rectangle(double w, double h) : width(w), height(h) {}

    double areaImpl() const { return width * height; }
    string nameImpl() const {
        return "직사각형 (" + to_string(width) + "x" + to_string(height) + ")";
    }
};

// --- CRTP 실전 활용: 자동 비교 연산자 생성 ---
/*
 *  < 연산자만 정의하면 나머지 비교 연산자를 자동 생성!
 *  (C++20의 <=> 연산자 이전에 사용하던 기법)
 */
template <typename Derived>
class Comparable {
public:
    bool operator>(const Derived& other) const {
        return other < static_cast<const Derived&>(*this);
    }
    bool operator<=(const Derived& other) const {
        return !(static_cast<const Derived&>(*this) > other);
    }
    bool operator>=(const Derived& other) const {
        return !(static_cast<const Derived&>(*this) < other);
    }
    bool operator==(const Derived& other) const {
        return !(static_cast<const Derived&>(*this) < other) &&
               !(other < static_cast<const Derived&>(*this));
    }
    bool operator!=(const Derived& other) const {
        return !(static_cast<const Derived&>(*this) == other);
    }
};

class Score : public Comparable<Score> {
    int value;
public:
    Score(int v) : value(v) {}
    bool operator<(const Score& other) const { return value < other.value; }
    int getValue() const { return value; }
};

// --- 가상 함수 vs CRTP 성능 비교 데모 ---
// 가상 함수 버전
class VShape {
public:
    virtual double area() const = 0;
    virtual ~VShape() = default;
};

class VCircle : public VShape {
    double radius;
public:
    VCircle(double r) : radius(r) {}
    double area() const override { return 3.14159265 * radius * radius; }
};

void demo() {
    cout << "=== 레슨 4: CRTP (정적 다형성) ===" << endl << endl;

    cout << "--- CRTP 도형 ---" << endl;
    Circle c(5.0);
    Rectangle r(3.0, 4.0);
    c.describe();
    r.describe();

    cout << endl << "--- CRTP 자동 비교 연산자 ---" << endl;
    Score s1(85), s2(90), s3(85);
    cout << "  85 < 90: " << (s1 < s2 ? "true" : "false") << endl;
    cout << "  85 > 90: " << (s1 > s2 ? "true" : "false") << endl;
    cout << "  85 == 85: " << (s1 == s3 ? "true" : "false") << endl;
    cout << "  85 != 90: " << (s1 != s2 ? "true" : "false") << endl;

    // 성능 비교
    cout << endl << "--- 가상 함수 vs CRTP 성능 비교 ---" << endl;
    const int ITERATIONS = 10'000'000;

    // CRTP 버전
    auto start = chrono::high_resolution_clock::now();
    double sum1 = 0;
    Circle crtp_circle(5.0);
    for (int i = 0; i < ITERATIONS; i++) {
        sum1 += crtp_circle.area();    // 컴파일 타임 바인딩, 인라인 가능
    }
    auto end = chrono::high_resolution_clock::now();
    auto crtp_time = chrono::duration_cast<chrono::microseconds>(end - start);

    // 가상 함수 버전
    start = chrono::high_resolution_clock::now();
    double sum2 = 0;
    VCircle vcircle(5.0);
    VShape* vshape = &vcircle;
    for (int i = 0; i < ITERATIONS; i++) {
        sum2 += vshape->area();        // 런타임 vtable 조회
    }
    end = chrono::high_resolution_clock::now();
    auto vtable_time = chrono::duration_cast<chrono::microseconds>(end - start);

    cout << "  CRTP 시간:      " << crtp_time.count() << " us" << endl;
    cout << "  가상함수 시간:  " << vtable_time.count() << " us" << endl;
    cout << "  (결과 검증: " << sum1 << " == " << sum2 << ")" << endl;
    cout << endl;
}

} // namespace Lesson4


// =============================================================================
// 레슨 5: 다중 상속과 가상 상속
// =============================================================================
/*
 *  다이아몬드 문제 (Diamond Problem):
 *
 *       ┌──────────┐
 *       │  Animal  │       Animal이 두 번 존재!
 *       │  name    │
 *       └────┬─────┘
 *            │
 *     ┌──────┴──────┐
 *     │             │
 *  ┌──┴─────┐  ┌───┴────┐
 *  │  Dog   │  │  Bird  │
 *  │  bark()│  │  fly() │
 *  └──┬─────┘  └───┬────┘
 *     │             │
 *     └──────┬──────┘
 *       ┌────┴─────┐
 *       │ FlyingDog│    <- Animal::name이 두 개?!
 *       │          │       Dog::Animal::name vs Bird::Animal::name
 *       └──────────┘
 *
 *  해결: virtual 상속
 *
 *       ┌──────────┐
 *       │  Animal  │       Animal이 하나만 존재!
 *       │  name    │
 *       └────┬─────┘
 *            │ (virtual)
 *     ┌──────┴──────┐
 *     │             │
 *  ┌──┴─────┐  ┌───┴────┐
 *  │  Dog   │  │  Bird  │
 *  │  bark()│  │  fly() │
 *  └──┬─────┘  └───┬────┘
 *     │             │
 *     └──────┬──────┘
 *       ┌────┴─────┐
 *       │ FlyingDog│    <- Animal이 하나만 있음!
 *       └──────────┘
 */

namespace Lesson5 {

// --- 다이아몬드 문제 재현 ---
class Animal {
protected:
    string name;
public:
    Animal(const string& n) : name(n) {
        cout << "  [Animal 생성] " << name << endl;
    }
    virtual ~Animal() = default;
    virtual void identify() const {
        cout << "  나는 " << name << " 입니다." << endl;
    }
};

// virtual 상속: Animal을 공유 기반 클래스로 만듦
class Dog : virtual public Animal {
public:
    Dog(const string& n) : Animal(n) {
        cout << "  [Dog 생성]" << endl;
    }
    void bark() const { cout << "  " << name << ": 멍멍!" << endl; }
};

class Bird : virtual public Animal {
public:
    Bird(const string& n) : Animal(n) {
        cout << "  [Bird 생성]" << endl;
    }
    void fly() const { cout << "  " << name << ": 날아간다!" << endl; }
};

// 다중 상속: Dog과 Bird를 모두 상속
/*
 *  메모리 레이아웃 (가상 상속):
 *  ┌─────────────────────────┐
 *  │      FlyingDog          │
 *  ├─────────────────────────┤
 *  │  Dog 부분               │
 *  │  ├ vptr (Dog의 vtable)  │
 *  │  └ Dog 고유 멤버        │
 *  ├─────────────────────────┤
 *  │  Bird 부분              │
 *  │  ├ vptr (Bird의 vtable) │
 *  │  └ Bird 고유 멤버       │
 *  ├─────────────────────────┤
 *  │  Animal 부분 (공유!)    │  <- 단 한 번만 존재
 *  │  ├ name                 │
 *  │  └ ...                  │
 *  └─────────────────────────┘
 */
class FlyingDog : public Dog, public Bird {
public:
    // 가상 상속에서는 가장 파생된 클래스가 기반 클래스 생성자를 호출
    FlyingDog(const string& n) : Animal(n), Dog(n), Bird(n) {
        cout << "  [FlyingDog 생성]" << endl;
    }

    void identify() const override {
        cout << "  나는 날 수 있는 강아지 " << name << " 입니다!" << endl;
    }
};

// --- 인터페이스 다중 상속 (실전에서 더 흔한 패턴) ---
class IDrawable {
public:
    virtual void draw() const = 0;
    virtual ~IDrawable() = default;
};

class IClickable {
public:
    virtual void onClick() = 0;
    virtual ~IClickable() = default;
};

class IResizable {
public:
    virtual void resize(int w, int h) = 0;
    virtual ~IResizable() = default;
};

// 여러 인터페이스를 구현하는 버튼
class Button : public IDrawable, public IClickable, public IResizable {
    string text;
    int width, height;
public:
    Button(const string& t, int w, int h) : text(t), width(w), height(h) {}

    void draw() const override {
        cout << "  ┌" << string(width, '-') << "┐" << endl;
        int padding = (width - (int)text.size()) / 2;
        if (padding < 0) padding = 0;
        cout << "  |" << string(padding, ' ') << text
             << string(width - padding - (int)text.size(), ' ') << "|" << endl;
        cout << "  └" << string(width, '-') << "┘" << endl;
    }

    void onClick() override {
        cout << "  [" << text << "] 버튼이 클릭되었습니다!" << endl;
    }

    void resize(int w, int h) override {
        width = w;
        height = h;
        cout << "  [" << text << "] 크기 변경: " << w << "x" << h << endl;
    }
};

void demo() {
    cout << "=== 레슨 5: 다중 상속과 가상 상속 ===" << endl << endl;

    cout << "--- 다이아몬드 문제 해결 (가상 상속) ---" << endl;
    FlyingDog fd("코코");
    fd.identify();
    fd.bark();
    fd.fly();

    cout << endl << "--- 인터페이스 다중 상속 ---" << endl;
    Button btn("확인", 12, 3);
    btn.draw();
    btn.onClick();
    btn.resize(20, 5);
    btn.draw();
    cout << endl;
}

} // namespace Lesson5


// =============================================================================
// 레슨 6: 타입 캐스팅 심화
// =============================================================================
/*
 *  C++ 4가지 캐스트 연산자:
 *
 *  ┌──────────────────┬──────────────────────────────────────────────┐
 *  │  캐스트 종류      │  용도                                       │
 *  ├──────────────────┼──────────────────────────────────────────────┤
 *  │  static_cast     │  명시적 타입 변환 (컴파일 타임 검사)         │
 *  │                  │  - 숫자 변환 (int->double)                   │
 *  │                  │  - 업/다운 캐스팅 (검사 없음!)               │
 *  │                  │  - void* -> 구체 타입                        │
 *  ├──────────────────┼──────────────────────────────────────────────┤
 *  │  dynamic_cast    │  안전한 다운캐스팅 (런타임 검사)             │
 *  │                  │  - 실패 시 nullptr (포인터) 또는 예외(참조)  │
 *  │                  │  - 가상 함수가 있는 클래스에서만 사용 가능   │
 *  ├──────────────────┼──────────────────────────────────────────────┤
 *  │  const_cast      │  const/volatile 제거                         │
 *  │                  │  - const를 제거하고 값 수정 (주의!)          │
 *  │                  │  - 레거시 API 호환을 위해 사용               │
 *  ├──────────────────┼──────────────────────────────────────────────┤
 *  │  reinterpret_cast│  비트 레벨 재해석                            │
 *  │                  │  - 포인터 -> 정수, 정수 -> 포인터            │
 *  │                  │  - 완전히 다른 타입 간 변환                  │
 *  │                  │  - 가장 위험! 최후의 수단                    │
 *  └──────────────────┴──────────────────────────────────────────────┘
 */

namespace Lesson6 {

class Base {
public:
    virtual ~Base() = default;
    virtual void whoAmI() const { cout << "  나는 Base입니다." << endl; }
};

class DerivedA : public Base {
public:
    void whoAmI() const override { cout << "  나는 DerivedA입니다." << endl; }
    void specialA() const { cout << "  DerivedA의 고유 기능!" << endl; }
};

class DerivedB : public Base {
public:
    void whoAmI() const override { cout << "  나는 DerivedB입니다." << endl; }
    void specialB() const { cout << "  DerivedB의 고유 기능!" << endl; }
};

// const_cast 사용 예: 레거시 API와의 호환
void legacyPrint(char* str) {   // 오래된 API: const를 받지 않음
    cout << "  레거시 출력: " << str << endl;
}

void demo() {
    cout << "=== 레슨 6: 타입 캐스팅 심화 ===" << endl << endl;

    // --- static_cast ---
    cout << "--- static_cast ---" << endl;
    double pi = 3.14159;
    int intPi = static_cast<int>(pi);   // double -> int (소수점 버림)
    cout << "  double " << pi << " -> int " << intPi << endl;

    // enum class 변환
    enum class Color { Red = 0, Green = 1, Blue = 2 };
    int colorVal = static_cast<int>(Color::Blue);
    cout << "  Color::Blue -> int " << colorVal << endl;

    // --- dynamic_cast (안전한 다운캐스팅) ---
    cout << endl << "--- dynamic_cast ---" << endl;
    Base* basePtr = new DerivedA();

    // 안전한 다운캐스팅 시도
    DerivedA* aPtr = dynamic_cast<DerivedA*>(basePtr);
    if (aPtr) {
        cout << "  DerivedA로 캐스팅 성공!" << endl;
        aPtr->specialA();
    }

    // 잘못된 타입으로 캐스팅 시도
    DerivedB* bPtr = dynamic_cast<DerivedB*>(basePtr);
    if (bPtr) {
        cout << "  DerivedB로 캐스팅 성공!" << endl;
    } else {
        cout << "  DerivedB로 캐스팅 실패 (nullptr 반환)" << endl;
    }

    // 타입 확인 후 안전하게 사용하는 패턴
    auto processBase = [](Base* ptr) {
        if (auto* a = dynamic_cast<DerivedA*>(ptr)) {
            a->specialA();
        } else if (auto* b = dynamic_cast<DerivedB*>(ptr)) {
            b->specialB();
        } else {
            ptr->whoAmI();
        }
    };

    cout << "  다형적 처리:" << endl;
    Base* objects[] = {new DerivedA(), new DerivedB(), new Base()};
    for (auto* obj : objects) {
        processBase(obj);
        delete obj;
    }
    delete basePtr;

    // --- const_cast ---
    cout << endl << "--- const_cast ---" << endl;
    const char* constStr = "Hello from const";
    // 레거시 API 호출을 위해 const 제거 (값을 수정하지 않는 경우만!)
    legacyPrint(const_cast<char*>(constStr));
    cout << "  주의: 실제로 const 객체를 수정하면 미정의 동작!" << endl;

    // --- reinterpret_cast ---
    cout << endl << "--- reinterpret_cast ---" << endl;
    int value = 0x41424344;   // ASCII: ABCD
    char* charPtr = reinterpret_cast<char*>(&value);
    cout << "  int 0x41424344의 바이트: ";
    for (int i = 0; i < 4; i++) {
        cout << charPtr[i] << " ";
    }
    cout << "(리틀 엔디안 순서)" << endl;

    // 포인터 -> 정수
    int dummy = 42;
    uintptr_t addr = reinterpret_cast<uintptr_t>(&dummy);
    cout << "  변수 주소를 정수로: " << addr << endl;
    cout << "  주의: reinterpret_cast는 가장 위험한 캐스트!" << endl;
    cout << endl;
}

} // namespace Lesson6


// =============================================================================
// 레슨 7: 객체 슬라이싱 & 실전 종합 예제
// =============================================================================
/*
 *  객체 슬라이싱 (Object Slicing):
 *  파생 클래스 객체를 기반 클래스 값으로 복사하면
 *  파생 클래스의 추가 데이터가 잘려나가는 현상
 *
 *  ┌────────────────┐
 *  │   Derived      │
 *  │ ┌────────────┐ │
 *  │ │   Base     │ │  값 복사(슬라이싱)   ┌────────────┐
 *  │ │  base_data │ │  ==================> │   Base     │
 *  │ └────────────┘ │                      │  base_data │
 *  │  derived_data  │  <- 이 부분이 잘림!   └────────────┘
 *  └────────────────┘
 *
 *  해결: 포인터 또는 참조를 사용하라!
 */

namespace Lesson7 {

// --- 슬라이싱 문제 시연 ---
class Enemy {
protected:
    string name;
    int hp;
public:
    Enemy(const string& n, int h) : name(n), hp(h) {}
    virtual ~Enemy() = default;

    virtual void attack() const {
        cout << "  " << name << "(HP:" << hp << ") 기본 공격!" << endl;
    }

    virtual unique_ptr<Enemy> clone() const {
        return make_unique<Enemy>(*this);
    }

    string getName() const { return name; }
    int getHp() const { return hp; }
};

class Dragon : public Enemy {
    int firepower;
public:
    Dragon(const string& n, int h, int fp)
        : Enemy(n, h), firepower(fp) {}

    void attack() const override {
        cout << "  " << name << "(HP:" << hp << ") 화염 브레스! (위력:"
             << firepower << ")" << endl;
    }

    unique_ptr<Enemy> clone() const override {
        return make_unique<Dragon>(*this);
    }
};

class Goblin : public Enemy {
    bool hasStealth;
public:
    Goblin(const string& n, int h, bool stealth)
        : Enemy(n, h), hasStealth(stealth) {}

    void attack() const override {
        if (hasStealth)
            cout << "  " << name << "(HP:" << hp << ") 은밀 기습!" << endl;
        else
            cout << "  " << name << "(HP:" << hp << ") 단검 공격!" << endl;
    }

    unique_ptr<Enemy> clone() const override {
        return make_unique<Goblin>(*this);
    }
};

// 슬라이싱 문제 시연
void slicingProblem(Enemy enemy) {     // 값으로 받으면 슬라이싱!
    enemy.attack();   // Dragon이어도 Enemy::attack()이 호출됨
}

void noSlicing(const Enemy& enemy) {   // 참조로 받으면 OK!
    enemy.attack();   // 올바른 가상 함수 호출
}

// --- 실전 종합 예제: 게임 엔티티 시스템 ---
/*
 *  게임 엔티티 시스템 구조:
 *
 *              ┌──────────────┐
 *              │   Entity     │
 *              │  x, y, name  │
 *              │  update()    │
 *              │  render()    │
 *              └──────┬───────┘
 *                     │
 *        ┌────────────┼────────────┐
 *        │            │            │
 *  ┌─────┴─────┐ ┌───┴────┐ ┌────┴─────┐
 *  │  Player   │ │  NPC   │ │Projectile│
 *  │  level    │ │ dialog │ │ speed    │
 *  │  attack() │ │ talk() │ │ move()   │
 *  └───────────┘ └────────┘ └──────────┘
 */

class Entity {
protected:
    float x, y;
    string name;
    bool active;

public:
    Entity(const string& n, float px, float py)
        : x(px), y(py), name(n), active(true) {}
    virtual ~Entity() = default;

    // 순수 가상 함수 - 인터페이스 정의
    virtual void update(float deltaTime) = 0;
    virtual void render() const = 0;
    virtual unique_ptr<Entity> clone() const = 0;

    // 공통 기능
    void setPosition(float px, float py) { x = px; y = py; }
    string getName() const { return name; }
    bool isActive() const { return active; }
    void deactivate() { active = false; }
};

class Player : public Entity {
    int level;
    int hp;
    int maxHp;

public:
    Player(const string& n, float px, float py, int lvl = 1)
        : Entity(n, px, py), level(lvl), hp(100), maxHp(100) {}

    void update(float deltaTime) override {
        // 플레이어 업데이트 로직 (입력 처리 등)
        (void)deltaTime;
    }

    void render() const override {
        cout << "  [@] " << name << " Lv." << level
             << " HP:" << hp << "/" << maxHp
             << " 위치:(" << x << "," << y << ")" << endl;
    }

    unique_ptr<Entity> clone() const override {
        return make_unique<Player>(*this);
    }

    void levelUp() {
        level++;
        maxHp += 20;
        hp = maxHp;
        cout << "  " << name << " 레벨 업! -> Lv." << level << endl;
    }
};

class NPC : public Entity {
    string dialog;
    bool isShop;

public:
    NPC(const string& n, float px, float py, const string& dlg, bool shop = false)
        : Entity(n, px, py), dialog(dlg), isShop(shop) {}

    void update(float deltaTime) override {
        (void)deltaTime;
        // NPC AI 로직
    }

    void render() const override {
        cout << "  [?] " << name
             << (isShop ? " (상점)" : " (NPC)")
             << " 위치:(" << x << "," << y << ")" << endl;
    }

    unique_ptr<Entity> clone() const override {
        return make_unique<NPC>(*this);
    }

    void talk() const {
        cout << "  " << name << ": \"" << dialog << "\"" << endl;
    }
};

class Projectile : public Entity {
    float speed;
    float dx, dy;   // 방향 벡터

public:
    Projectile(const string& n, float px, float py, float spd, float dirX, float dirY)
        : Entity(n, px, py), speed(spd), dx(dirX), dy(dirY) {}

    void update(float deltaTime) override {
        x += dx * speed * deltaTime;
        y += dy * speed * deltaTime;

        // 화면 밖으로 나가면 비활성화
        if (x < -100 || x > 100 || y < -100 || y > 100) {
            deactivate();
        }
    }

    void render() const override {
        cout << "  [*] " << name << " 속도:" << speed
             << " 위치:(" << x << "," << y << ")" << endl;
    }

    unique_ptr<Entity> clone() const override {
        return make_unique<Projectile>(*this);
    }
};

// --- 게임 월드: 엔티티를 관리하는 컨테이너 ---
class GameWorld {
    vector<unique_ptr<Entity>> entities;

public:
    void addEntity(unique_ptr<Entity> entity) {
        entities.push_back(std::move(entity));
    }

    void update(float deltaTime) {
        for (auto& entity : entities) {
            if (entity->isActive()) {
                entity->update(deltaTime);
            }
        }
        // 비활성화된 엔티티 제거
        entities.erase(
            remove_if(entities.begin(), entities.end(),
                [](const unique_ptr<Entity>& e) { return !e->isActive(); }),
            entities.end()
        );
    }

    void render() const {
        for (const auto& entity : entities) {
            if (entity->isActive()) {
                entity->render();
            }
        }
    }

    size_t entityCount() const { return entities.size(); }

    // clone 패턴으로 엔티티 복제 (슬라이싱 없이!)
    void cloneEntity(size_t index) {
        if (index < entities.size()) {
            auto cloned = entities[index]->clone();
            cout << "  " << cloned->getName() << " 복제됨!" << endl;
            entities.push_back(std::move(cloned));
        }
    }
};

void demo() {
    cout << "=== 레슨 7: 객체 슬라이싱 & 실전 예제 ===" << endl << endl;

    // --- 슬라이싱 문제 시연 ---
    cout << "--- 객체 슬라이싱 문제 ---" << endl;
    Dragon dragon("용", 500, 100);

    cout << "  값으로 전달 (슬라이싱 발생!):" << endl;
    slicingProblem(dragon);     // Enemy::attack() 호출됨!

    cout << "  참조로 전달 (슬라이싱 없음!):" << endl;
    noSlicing(dragon);          // Dragon::attack() 호출됨!

    // --- clone 패턴 ---
    cout << endl << "--- clone 패턴 (슬라이싱 해결) ---" << endl;
    vector<unique_ptr<Enemy>> enemies;
    enemies.push_back(make_unique<Dragon>("드래곤", 500, 100));
    enemies.push_back(make_unique<Goblin>("고블린", 50, true));

    // 모든 적 복제 (다형성 유지!)
    vector<unique_ptr<Enemy>> clones;
    for (const auto& e : enemies) {
        clones.push_back(e->clone());   // 올바른 타입으로 복제
    }

    cout << "  원본:" << endl;
    for (const auto& e : enemies) e->attack();
    cout << "  복제:" << endl;
    for (const auto& e : clones) e->attack();

    // --- 실전 종합: 게임 엔티티 시스템 ---
    cout << endl << "--- 게임 엔티티 시스템 ---" << endl;
    GameWorld world;

    world.addEntity(make_unique<Player>("용사", 0, 0, 1));
    world.addEntity(make_unique<NPC>("상인", 10, 5, "무기를 사시겠습니까?", true));
    world.addEntity(make_unique<NPC>("마을주민", 3, 7, "환영합니다, 용사님!"));
    world.addEntity(make_unique<Projectile>("화살", 0, 0, 50.0f, 1.0f, 0.5f));

    cout << "  --- 초기 상태 ---" << endl;
    world.render();

    cout << endl << "  --- 1초 후 (update) ---" << endl;
    world.update(1.0f);
    world.render();

    cout << endl << "  --- 엔티티 복제 ---" << endl;
    world.cloneEntity(0);   // 플레이어 복제
    world.render();

    cout << endl << "  총 엔티티 수: " << world.entityCount() << endl;

    // --- 학습 요약 ---
    cout << endl;
    cout << "  ┌──────────────────────────────────────────────────┐" << endl;
    cout << "  │              20장 학습 포인트 요약                 │" << endl;
    cout << "  ├──────────────────────────────────────────────────┤" << endl;
    cout << "  │  1. 깊은 복사를 구현하지 않으면 버그의 온상     │" << endl;
    cout << "  │  2. 이동 시맨틱스로 불필요한 복사를 제거하라    │" << endl;
    cout << "  │  3. Rule of 0을 우선하고, 필요하면 Rule of 5    │" << endl;
    cout << "  │  4. CRTP로 컴파일 타임 다형성을 구현할 수 있다  │" << endl;
    cout << "  │  5. 다이아몬드 문제는 virtual 상속으로 해결     │" << endl;
    cout << "  │  6. dynamic_cast로 안전한 다운캐스팅을 하라     │" << endl;
    cout << "  │  7. 객체 슬라이싱을 피하려면 포인터/참조 사용   │" << endl;
    cout << "  └──────────────────────────────────────────────────┘" << endl;
    cout << endl;
}

} // namespace Lesson7


// =============================================================================
// 메인 함수: 모든 레슨 실행
// =============================================================================
/*
=============================================================================
  레슨별 demo() 출력 흐름 가이드 (대략)
=============================================================================
  Lesson1 (Rule of 0/3/5):
    DeepCopyString s1("hello");                // 생성, 힙에 "hello" 할당
    DeepCopyString s2 = s1;                    // 복사 생성 → 별도 할당
    s2 데이터 변경 → s1 영향 없음 (deep copy)
    s2 = move(s1);                              // 이동: s1 데이터 → s2, s1=empty

  Lesson2 (Move Semantics):
    MoveString a("Hello"), b = move(a);         // a는 빈 상태, b가 데이터 소유
    move 생성자는 noexcept → vector 안에서 안전한 재할당

  Lesson3 (Copy-and-Swap):
    SafeArray a = b;  → 임시 객체 + swap → 강한 예외 안전성

  Lesson4 (CRTP):
    Counter<MyClass> 상속 → MyClass에 컴파일 시점에 카운팅 기능 주입
    인스턴스 카운트 출력 (예: 3, 2, 1)

  Lesson5 (Virtual Inheritance, 다이아몬드 문제):
    FlyingDog (Animal ←Dog/Bird ← FlyingDog)
    virtual 상속 안 하면 Animal 멤버 2개 (모호)
    virtual 상속하면 Animal 1개로 통합

  Lesson6 (Type Casting):
    static_cast: 컴파일 타임 검사
    dynamic_cast: 런타임 RTTI 사용, 다운캐스트 검증
    const_cast: const 제거
    reinterpret_cast: 비트 재해석 (위험)

  Lesson7 (Clone 패턴):
    Shape* clone() → 가상 함수, 다형 객체 deep copy
    Rectangle::clone() → unique_ptr<Shape>(new Rectangle(*this))
=============================================================================
*/

int main() {
    cout << "================================================================" << endl;
    cout << "  C++ 학습 20장: 고급 OOP (Advanced Object-Oriented Programming)" << endl;
    cout << "================================================================" << endl;
    cout << endl;

    Lesson1::demo();   // Rule of 0/3/5
    Lesson2::demo();   // Move Semantics
    Lesson3::demo();   // Copy-and-Swap
    Lesson4::demo();   // CRTP
    Lesson5::demo();   // Virtual Inheritance
    Lesson6::demo();   // Type Casting
    Lesson7::demo();   // Clone 패턴

    cout << "================================================================" << endl;
    cout << "  20장 학습 완료!" << endl;
    cout << "  축하합니다! C++ 고급 OOP를 마스터했습니다!" << endl;
    cout << "================================================================" << endl;

    return 0;
}
