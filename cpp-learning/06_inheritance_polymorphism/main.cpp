/*
=============================================================================
  C++ 학습 06단계: 상속과 다형성
=============================================================================
  [학습 목표]
  1. 상속의 개념과 문법을 이해한다
  2. 가상 함수(virtual)와 오버라이딩을 안다
  3. 다형성(polymorphism)으로 유연한 설계를 할 수 있다
  4. 추상 클래스와 인터페이스를 이해한다
  5. 다중 상속과 그 위험성을 안다

  [컴파일] g++ -std=c++17 -o 06_inherit main.cpp
=============================================================================
*/
#include <iostream>
#include <string>
#include <vector>
#include <memory>  // unique_ptr
using namespace std;


// =====================================================================
// 레슨 1 — 상속 기본
// =====================================================================
/*
★ 상속 = 기존 클래스의 기능을 물려받아 새 클래스를 만드는 것
  → 코드 재사용 + 계층 구조 설계

  class 자식 : public 부모 {
      // 부모의 public/protected 멤버를 물려받음
  };

★ 용어
  부모 클래스 = Base class (기반 클래스)
  자식 클래스 = Derived class (파생 클래스)

★ 접근 수준과 상속
  부모의 public     → 자식에서 public
  부모의 protected  → 자식에서 protected
  부모의 private    → 자식에서 접근 불가!
*/

class Animal {
protected:              // protected: 자식 클래스에서 접근 가능
    string name_;
    int    age_;

public:
    Animal(const string& name, int age)
        : name_(name), age_(age) {}

    void eat() const {
        cout << "  " << name_ << "이(가) 먹는다.\n";
    }

    void info() const {
        cout << "  [동물] " << name_ << " (" << age_ << "살)\n";
    }
};

// Cat은 Animal을 상속
class Cat : public Animal {
private:
    string color_;

public:
    // 부모 생성자 호출
    Cat(const string& name, int age, const string& color)
        : Animal(name, age), color_(color) {}

    void purr() const {
        cout << "  " << name_ << ": 그르릉~\n";  // protected라 접근 가능
    }

    void info() const {
        cout << "  [고양이] " << name_ << " (" << age_ << "살, "
             << color_ << ")\n";
    }
};


// =====================================================================
// 레슨 2 — 가상 함수와 다형성
// =====================================================================
/*
★ 문제: 부모 포인터로 자식 객체를 가리킬 때,
        부모의 함수가 호출됨 (자식의 것이 아니라!)

★ 해결: virtual 키워드 → 실행 시 실제 타입의 함수를 호출

★ 다형성(Polymorphism)
  = 같은 코드로 다른 동작을 하게 만드는 것
  = OOP의 가장 강력한 기능!

★ 규칙
  1. 부모의 함수에 virtual 붙이기
  2. 자식의 함수에 override 붙이기 (실수 방지)
  3. 소멸자에도 virtual 붙이기! (메모리 누수 방지)
*/

class Shape {
protected:
    string name_;

public:
    Shape(const string& name) : name_(name) {}

    // ★ virtual 소멸자: 부모 포인터로 자식을 삭제할 때 필수!
    virtual ~Shape() {}

    // virtual 함수: 자식이 재정의 가능
    virtual double area() const {
        return 0;
    }

    virtual void draw() const {
        cout << "  [도형] " << name_ << "\n";
    }

    string get_name() const { return name_; }
};

class Circle : public Shape {
    double radius_;
public:
    Circle(double r) : Shape("원"), radius_(r) {}

    // override: 부모의 virtual 함수를 재정의
    double area() const override {
        return 3.14159 * radius_ * radius_;
    }

    void draw() const override {
        cout << "  [원] 반지름=" << radius_
             << " 넓이=" << area() << "\n";
    }
};

class Rectangle : public Shape {
    double width_, height_;
public:
    Rectangle(double w, double h)
        : Shape("사각형"), width_(w), height_(h) {}

    double area() const override {
        return width_ * height_;
    }

    void draw() const override {
        cout << "  [사각형] " << width_ << "x" << height_
             << " 넓이=" << area() << "\n";
    }
};

class Triangle : public Shape {
    double base_, height_;
public:
    Triangle(double b, double h)
        : Shape("삼각형"), base_(b), height_(h) {}

    double area() const override {
        return base_ * height_ / 2;
    }

    void draw() const override {
        cout << "  [삼각형] 밑변=" << base_ << " 높이=" << height_
             << " 넓이=" << area() << "\n";
    }
};


// =====================================================================
// 레슨 3 — 추상 클래스와 인터페이스
// =====================================================================
/*
★ 순수 가상 함수: = 0 으로 선언 → 자식이 반드시 구현해야 함
★ 추상 클래스: 순수 가상 함수가 1개 이상 → 직접 객체 생성 불가
★ 인터페이스: 모든 함수가 순수 가상인 클래스 (C++에서의 인터페이스 패턴)

  class Animal {
      virtual void speak() = 0;  // 순수 가상 (자식이 반드시 구현)
  };
  Animal a;  // 에러!  추상 클래스는 객체 생성 불가
*/

class Printable {
public:
    virtual ~Printable() {}
    virtual string to_string() const = 0;  // 순수 가상 함수
};

class Document : public Printable {
    string title_;
public:
    Document(const string& title) : title_(title) {}

    // 반드시 구현해야 컴파일 가능
    string to_string() const override {
        return "[문서] " + title_;
    }
};


// =====================================================================
// main
// =====================================================================
int main() {
    cout << "========================================\n";
    cout << "  C++ 06단계 : 상속과 다형성\n";
    cout << "========================================\n\n";

    // ── 레슨 1: 상속 기본 ──
    cout << "[레슨 1] 상속 기본\n\n";
    {
        Cat cat("나비", 3, "검정");
        cat.info();    // Cat의 info
        cat.eat();     // 부모(Animal)에서 물려받은 함수
        cat.purr();    // Cat만의 함수
    }

    cout << "\n";

    // ── 레슨 2: 다형성 ──
    cout << "[레슨 2] 다형성 (Polymorphism)\n\n";
    {
        // ★ 핵심: 부모 포인터로 여러 자식 타입을 다룰 수 있다!
        //   이것이 다형성의 진짜 위력
        vector<unique_ptr<Shape>> shapes;
        shapes.push_back(make_unique<Circle>(5));
        shapes.push_back(make_unique<Rectangle>(4, 6));
        shapes.push_back(make_unique<Triangle>(3, 8));

        // 같은 코드로 다른 동작 실행!
        double total_area = 0;
        for (const auto& shape : shapes) {
            shape->draw();              // 각 도형에 맞는 draw 호출
            total_area += shape->area();
        }
        cout << "  총 넓이: " << total_area << "\n";
    }

    /*
    ★ 위 코드에서 virtual이 없었다면?
      Shape::draw()만 호출됨 → 모두 "[도형]..."으로 출력
      virtual 덕분에 Circle::draw(), Rectangle::draw() 등이 호출됨
    */

    cout << "\n";

    // ── 레슨 3: 추상 클래스 ──
    cout << "[레슨 3] 추상 클래스\n\n";
    {
        // Printable p;          // 에러!  추상 클래스는 직접 생성 불가
        Document doc("보고서");
        cout << "  " << doc.to_string() << "\n";

        // 부모 포인터로도 사용 가능
        Printable* ptr = &doc;
        cout << "  " << ptr->to_string() << "\n";
    }

    cout << "\n";

    // ── 참고: virtual 소멸자가 없으면 생기는 문제 ──
    cout << "[참고] virtual 소멸자의 중요성\n\n";
    cout << "  부모 포인터로 자식을 delete할 때:\n";
    cout << "  virtual ~Base()   → 자식 소멸자도 호출됨 (정상)\n";
    cout << "  ~Base() (non-virt)→ 부모 소멸자만 호출 (메모리 누수!)\n";
    cout << "  → 상속할 클래스는 항상 virtual 소멸자를 쓰자!\n";

    /*
    ★ 다중 상속 (간단 참고)
    class A { };
    class B { };
    class C : public A, public B { };  // A와 B 둘 다 상속

    문제: 다이아몬드 문제 (두 부모가 같은 조상일 때)
    해결: virtual 상속
    실무: 다중 상속은 가능하면 피하고, 인터페이스만 다중 상속
    */

    cout << "\n06단계 학습 완료!\n";
    return 0;
}
