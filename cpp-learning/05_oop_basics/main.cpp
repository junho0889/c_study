/*
=============================================================================
  C++ 학습 05단계: 클래스와 객체지향 기초 (OOP)
=============================================================================
  [학습 목표]
  1. 클래스와 객체의 개념을 이해한다
  2. 멤버 변수와 멤버 함수를 작성할 수 있다
  3. 접근 제어(public/private/protected)를 이해한다
  4. 생성자와 소멸자를 이해한다
  5. this 포인터, static 멤버를 안다
  6. 연산자 오버로딩 기초를 안다

  [컴파일] g++ -std=c++17 -o 05_oop main.cpp
=============================================================================
*/
#include <iostream>
#include <string>
using namespace std;


// =====================================================================
// 레슨 1 — 클래스 기본
// =====================================================================
/*
★ 클래스 = 변수(데이터)와 함수(동작)를 하나로 묶은 것
  → 붕어빵 '틀' 이고, 객체는 그 틀로 만든 '붕어빵'

★ 구조:
  class 클래스이름 {
  public:       ← 외부에서 접근 가능
      함수들...
  private:      ← 외부에서 접근 불가 (데이터 보호)
      변수들...
  };            ← 세미콜론 필수!

★ 접근 제어
  public    : 아무데서나 접근 가능
  private   : 클래스 내부에서만 (기본값)
  protected : 클래스 내부 + 자식 클래스에서 (06단계)
*/

class Dog {
private:
    // ── 멤버 변수 (데이터) ──
    // private: 외부에서 직접 접근 불가 → getter/setter로 접근
    string name_;
    int    age_;

public:
    // ── 생성자 (Constructor) ──
    // 객체가 만들어질 때 자동 호출되는 특수 함수
    // 이름이 클래스명과 같고, 반환형이 없다
    Dog(const string& name, int age)
        : name_(name), age_(age)   // ← 초기화 리스트 (권장 방식)
    {
        cout << "  [생성] " << name_ << " 탄생!\n";
    }

    // 기본 생성자 (매개변수 없음)
    Dog() : name_("이름없음"), age_(0) {
        cout << "  [생성] 이름 없는 강아지 탄생!\n";
    }

    // ── 소멸자 (Destructor) ──
    // 객체가 사라질 때 자동 호출
    // 메모리 해제 등 정리 작업에 사용
    ~Dog() {
        cout << "  [소멸] " << name_ << " 안녕...\n";
    }

    // ── 멤버 함수 (메서드) ──
    void bark() const {   // const = 이 함수는 멤버 변수를 바꾸지 않는다
        cout << "  " << name_ << ": 멍멍!\n";
    }

    void info() const {
        cout << "  이름: " << name_ << " / 나이: " << age_ << "살\n";
    }

    // ── Getter / Setter ──
    // private 변수에 대한 간접 접근 방법
    string get_name() const { return name_; }
    int    get_age() const  { return age_; }
    void   set_age(int age) {
        if (age >= 0) age_ = age;    // 유효성 검사도 가능
    }
};


// =====================================================================
// 레슨 2 — this 포인터 & static 멤버
// =====================================================================
class Player {
private:
    string name_;
    int    hp_;
    static int total_count_;   // static: 모든 객체가 공유하는 변수

public:
    Player(const string& name, int hp) : name_(name), hp_(hp) {
        total_count_++;
    }

    ~Player() {
        total_count_--;
    }

    // this = 현재 객체 자신을 가리키는 포인터
    // this->name_ 과 name_ 은 같지만, 매개변수와 이름이 겹칠 때 구분용
    Player& set_hp(int hp) {
        this->hp_ = hp;       // this->hp_ = 멤버, hp = 매개변수
        return *this;         // 자기 자신 반환 → 메서드 체이닝 가능
    }

    Player& heal(int amount) {
        this->hp_ += amount;
        return *this;
    }

    void info() const {
        cout << "  " << name_ << " (HP: " << hp_ << ")\n";
    }

    // static 함수: 객체 없이 호출 가능 (Player::get_count())
    static int get_count() { return total_count_; }
};

int Player::total_count_ = 0;   // static 변수 초기화 (클래스 밖에서!)


// =====================================================================
// 레슨 3 — 연산자 오버로딩 기초
// =====================================================================
/*
★ 연산자 오버로딩 = +, -, ==, << 등을 내 클래스에 맞게 재정의

예: Vector2D 끼리 더하기를 v1 + v2 로 쓸 수 있게 하기
*/
class Vector2D {
public:
    double x, y;

    Vector2D(double x = 0, double y = 0) : x(x), y(y) {}

    // + 연산자 오버로딩
    Vector2D operator+(const Vector2D& other) const {
        return Vector2D(x + other.x, y + other.y);
    }

    // == 연산자 오버로딩
    bool operator==(const Vector2D& other) const {
        return x == other.x && y == other.y;
    }

    // << 출력 연산자 (friend: 클래스 외부 함수인데 private 접근 허용)
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
        Dog dog1("바둑이", 3);    // 생성자 호출
        Dog dog2("흰둥이", 1);

        dog1.bark();
        dog1.info();
        dog2.info();

        dog1.set_age(4);
        cout << "  바둑이 나이 변경: " << dog1.get_age() << "\n";

        // dog1.name_ = "test";  // 에러! private이라 접근 불가

        cout << "  -- 블록 끝, 소멸자 호출됨 --\n";
    }  // ← 여기서 dog1, dog2 소멸자 자동 호출!

    cout << "\n";

    // ── 레슨 2: this, static ──
    cout << "[레슨 2] this 포인터 & static\n\n";
    {
        Player p1("전사", 100);
        Player p2("마법사", 80);
        cout << "  플레이어 수: " << Player::get_count() << "\n";

        // 메서드 체이닝: this 반환 덕분에 연속 호출 가능
        p1.set_hp(50).heal(20).heal(10);
        p1.info();   // HP: 80
        p2.info();
    }
    cout << "  블록 후 플레이어 수: " << Player::get_count() << "\n";

    cout << "\n";

    // ── 레슨 3: 연산자 오버로딩 ──
    cout << "[레슨 3] 연산자 오버로딩\n\n";
    {
        Vector2D v1(3, 4);
        Vector2D v2(1, 2);
        Vector2D v3 = v1 + v2;   // operator+ 호출

        cout << "  v1 = " << v1 << "\n";
        cout << "  v2 = " << v2 << "\n";
        cout << "  v1 + v2 = " << v3 << "\n";
        cout << "  v1 == v2 ? " << (v1 == v2 ? "같다" : "다르다") << "\n";
    }

    cout << "\n05단계 학습 완료!\n";
    return 0;
}
