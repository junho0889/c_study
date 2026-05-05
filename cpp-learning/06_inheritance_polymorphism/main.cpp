/*
=============================================================================
  C++ 학습 06단계: 상속과 다형성
=============================================================================
  [컴파일] g++ -std=c++17 -o 06_inherit main.cpp
  [주석 표기] // > 출력  // → 변수값  // ▶ 흐름
=============================================================================
*/
#include <iostream>
#include <string>
#include <vector>
#include <memory>
using namespace std;


// =====================================================================
// 레슨 1 — 상속 기본
// =====================================================================
class Animal {
protected:
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

class Cat : public Animal {
private:
    string color_;

public:
    Cat(const string& name, int age, const string& color)
        : Animal(name, age), color_(color) {}
        // → 부모 생성자 먼저 호출 (name_, age_ 초기화)
        //   그 다음 자식 멤버(color_) 초기화

    void purr() const {
        cout << "  " << name_ << ": 그르릉~\n";
    }

    void info() const {
        cout << "  [고양이] " << name_ << " (" << age_ << "살, "
             << color_ << ")\n";
        // ※ Animal::info()와 다른 시그니처. 같은 이름이지만 hides parent.
        //   virtual이 아니므로 정적 바인딩 (호출 타입에 따라 결정)
    }
};


// =====================================================================
// 레슨 2 — 가상 함수와 다형성
// =====================================================================
class Shape {
protected:
    string name_;

public:
    Shape(const string& name) : name_(name) {}
    virtual ~Shape() {}

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

    double area() const override {
        return 3.14159 * radius_ * radius_;
        // → r=5: 3.14159*25 = 78.5398
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
        // → 4×6 = 24
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
        // → 3×8/2 = 12
    }

    void draw() const override {
        cout << "  [삼각형] 밑변=" << base_ << " 높이=" << height_
             << " 넓이=" << area() << "\n";
    }
};


// =====================================================================
// 레슨 3 — 추상 클래스와 인터페이스
// =====================================================================
class Printable {
public:
    virtual ~Printable() {}
    virtual string to_string() const = 0;
};

class Document : public Printable {
    string title_;
public:
    Document(const string& title) : title_(title) {}

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
        // → Animal 생성자 (name_="나비", age_=3) → Cat 멤버(color_="검정")

        cat.info();
        // → Cat::info() 호출 (정적 바인딩, virtual 아님)
        // > 출력:   [고양이] 나비 (3살, 검정)

        cat.eat();
        // → 부모 함수, 그대로 사용
        // > 출력:   나비이(가) 먹는다.

        cat.purr();
        // > 출력:   나비: 그르릉~
    }

    cout << "\n";

    // ── 레슨 2: 다형성 ──
    cout << "[레슨 2] 다형성 (Polymorphism)\n\n";
    {
        vector<unique_ptr<Shape>> shapes;
        // → 빈 vector

        shapes.push_back(make_unique<Circle>(5));
        // → Circle(r=5) 생성, unique_ptr<Shape>로 vector에 추가
        shapes.push_back(make_unique<Rectangle>(4, 6));
        shapes.push_back(make_unique<Triangle>(3, 8));
        // → shapes.size() = 3

        double total_area = 0;
        for (const auto& shape : shapes) {
            // 1회차: shape → Circle*
            //   draw() = "[원] 반지름=5 넓이=78.5398"
            //   area() = 78.5398
            //   total_area = 78.5398
            // 2회차: shape → Rectangle*
            //   draw() = "[사각형] 4x6 넓이=24"
            //   area() = 24
            //   total_area = 102.5398
            // 3회차: shape → Triangle*
            //   draw() = "[삼각형] 밑변=3 높이=8 넓이=12"
            //   area() = 12
            //   total_area = 114.5398
            shape->draw();
            total_area += shape->area();
        }
        // > 출력:
        //   [원] 반지름=5 넓이=78.5398
        //   [사각형] 4x6 넓이=24
        //   [삼각형] 밑변=3 높이=8 넓이=12

        cout << "  총 넓이: " << total_area << "\n";
        // > 출력:   총 넓이: 114.54         ← 기본 출력 6자리 정밀도
    }
    // ▶ 블록 종료: vector 소멸 → 각 unique_ptr 해제 → 각 도형의 가상 소멸자 호출
    //   virtual 소멸자 덕분에 Circle/Rectangle/Triangle 소멸자가 정확히 호출됨

    cout << "\n";

    // ── 레슨 3: 추상 클래스 ──
    cout << "[레슨 3] 추상 클래스\n\n";
    {
        Document doc("보고서");
        // → doc.title_ = "보고서"

        cout << "  " << doc.to_string() << "\n";
        // → "[문서] 보고서"
        // > 출력:   [문서] 보고서

        Printable* ptr = &doc;
        // → 부모 포인터로 자식 객체 가리킴 (다형성)
        cout << "  " << ptr->to_string() << "\n";
        // → 가상 함수 → Document::to_string() 호출
        // > 출력:   [문서] 보고서
    }

    cout << "\n";

    // ── 참고 ──
    cout << "[참고] virtual 소멸자의 중요성\n\n";
    cout << "  부모 포인터로 자식을 delete할 때:\n";
    cout << "  virtual ~Base()   → 자식 소멸자도 호출됨 (정상)\n";
    cout << "  ~Base() (non-virt)→ 부모 소멸자만 호출 (메모리 누수!)\n";
    cout << "  → 상속할 클래스는 항상 virtual 소멸자를 쓰자!\n";

    cout << "\n06단계 학습 완료!\n";
    return 0;
}
