/*
=============================================================================
  C++ 학습 05단계: 클래스와 객체지향 기초 (OOP)
=============================================================================
  [컴파일] g++ -std=c++17 -o 05_oop main.cpp
  [주석 표기] // > 출력  // → 변수값  // ▶ 흐름
=============================================================================
*/
#include <iostream>
#include <string>
using namespace std;


// =====================================================================
// 레슨 1 — 클래스 기본
// =====================================================================
class Dog {
private:
    string name_;
    int    age_;

public:
    Dog(const string& name, int age)
        : name_(name), age_(age)
    {
        // → 객체가 만들어질 때 호출. name_, age_ 초기화 후 본문 실행.
        cout << "  [생성] " << name_ << " 탄생!\n";
    }

    Dog() : name_("이름없음"), age_(0) {
        cout << "  [생성] 이름 없는 강아지 탄생!\n";
    }

    ~Dog() {
        // → 객체 수명 종료 시 자동 호출. 블록 끝, vector pop, delete 등.
        cout << "  [소멸] " << name_ << " 안녕...\n";
    }

    void bark() const {
        cout << "  " << name_ << ": 멍멍!\n";
    }

    void info() const {
        cout << "  이름: " << name_ << " / 나이: " << age_ << "살\n";
    }

    string get_name() const { return name_; }
    int    get_age() const  { return age_; }
    void   set_age(int age) {
        if (age >= 0) age_ = age;
        // ▶ age >= 0 검사 → 음수면 무시, 양수면 갱신
    }
};


// =====================================================================
// 레슨 2 — this 포인터 & static 멤버
// =====================================================================
class Player {
private:
    string name_;
    int    hp_;
    static int total_count_;   // 모든 객체가 공유

public:
    Player(const string& name, int hp) : name_(name), hp_(hp) {
        total_count_++;
        // → 객체 생성마다 +1
    }

    ~Player() {
        total_count_--;
        // → 객체 소멸마다 -1
    }

    Player& set_hp(int hp) {
        this->hp_ = hp;
        return *this;
        // → 자기 자신 반환 → 메서드 체이닝 가능
    }

    Player& heal(int amount) {
        this->hp_ += amount;
        return *this;
    }

    void info() const {
        cout << "  " << name_ << " (HP: " << hp_ << ")\n";
    }

    static int get_count() { return total_count_; }
};

int Player::total_count_ = 0;
// → 프로그램 시작 시 0으로 초기화


// =====================================================================
// 레슨 3 — 연산자 오버로딩 기초
// =====================================================================
class Vector2D {
public:
    double x, y;

    Vector2D(double x = 0, double y = 0) : x(x), y(y) {}

    Vector2D operator+(const Vector2D& other) const {
        return Vector2D(x + other.x, y + other.y);
        // → 새 Vector2D 생성하여 반환 (원본 변경 X)
    }

    bool operator==(const Vector2D& other) const {
        return x == other.x && y == other.y;
    }

    friend ostream& operator<<(ostream& os, const Vector2D& v) {
        os << "(" << v.x << ", " << v.y << ")";
        return os;
    }
};


// =====================================================================
// main
// =====================================================================
int main() {
    cout << "========================================\n";
    cout << "  C++ 05단계 : 클래스와 OOP 기초\n";
    cout << "========================================\n\n";

    // ── 레슨 1: 클래스 기본 ──
    cout << "[레슨 1] 클래스 기본\n\n";
    {
        Dog dog1("바둑이", 3);
        // > 출력:   [생성] 바둑이 탄생!
        // → dog1.name_="바둑이", dog1.age_=3

        Dog dog2("흰둥이", 1);
        // > 출력:   [생성] 흰둥이 탄생!
        // → dog2.name_="흰둥이", dog2.age_=1

        dog1.bark();
        // > 출력:   바둑이: 멍멍!

        dog1.info();
        // > 출력:   이름: 바둑이 / 나이: 3살

        dog2.info();
        // > 출력:   이름: 흰둥이 / 나이: 1살

        dog1.set_age(4);
        // → dog1.age_ = 4 (4 >= 0이므로 갱신)
        cout << "  바둑이 나이 변경: " << dog1.get_age() << "\n";
        // > 출력:   바둑이 나이 변경: 4

        cout << "  -- 블록 끝, 소멸자 호출됨 --\n";
        // > 출력:   -- 블록 끝, 소멸자 호출됨 --
    }
    // ▶ 블록 종료 시점에 LIFO 순으로 소멸자 호출
    //   → dog2 먼저 (나중에 만들어졌으니), 그 다음 dog1
    // > 출력:
    //   [소멸] 흰둥이 안녕...
    //   [소멸] 바둑이 안녕...

    cout << "\n";

    // ── 레슨 2: this, static ──
    cout << "[레슨 2] this 포인터 & static\n\n";
    {
        Player p1("전사", 100);
        // → total_count_: 0 → 1
        Player p2("마법사", 80);
        // → total_count_: 1 → 2

        cout << "  플레이어 수: " << Player::get_count() << "\n";
        // > 출력:   플레이어 수: 2

        p1.set_hp(50).heal(20).heal(10);
        // ▶ 체이닝 흐름:
        //   set_hp(50): p1.hp_ = 50, return *this
        //   .heal(20):  p1.hp_ = 70, return *this
        //   .heal(10):  p1.hp_ = 80, return *this
        // → p1.hp_ = 80

        p1.info();
        // > 출력:   전사 (HP: 80)
        p2.info();
        // > 출력:   마법사 (HP: 80)
    }
    // ▶ 블록 종료: p2 소멸 (count: 2→1), p1 소멸 (count: 1→0)
    cout << "  블록 후 플레이어 수: " << Player::get_count() << "\n";
    // > 출력:   블록 후 플레이어 수: 0

    cout << "\n";

    // ── 레슨 3: 연산자 오버로딩 ──
    cout << "[레슨 3] 연산자 오버로딩\n\n";
    {
        Vector2D v1(3, 4);
        Vector2D v2(1, 2);
        Vector2D v3 = v1 + v2;
        // → operator+ 호출: Vector2D(3+1, 4+2) = Vector2D(4, 6)
        // → v3 = (4, 6)

        cout << "  v1 = " << v1 << "\n";
        // > 출력:   v1 = (3, 4)
        cout << "  v2 = " << v2 << "\n";
        // > 출력:   v2 = (1, 2)
        cout << "  v1 + v2 = " << v3 << "\n";
        // > 출력:   v1 + v2 = (4, 6)
        cout << "  v1 == v2 ? " << (v1 == v2 ? "같다" : "다르다") << "\n";
        // → 3==1 false → 다르다
        // > 출력:   v1 == v2 ? 다르다
    }

    cout << "\n05단계 학습 완료!\n";
    return 0;
}
