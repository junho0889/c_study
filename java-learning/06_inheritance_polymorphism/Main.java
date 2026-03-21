/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Java 학습 06단계: 상속과 다형성
  ─ extends, super, override, abstract, 다형성 ─

  [학습 목표]
  1. 상속(extends)의 개념과 문법을 이해한다
  2. 메서드 오버라이딩(@Override)을 안다
  3. super 키워드로 부모에게 접근하는 법을 안다
  4. 추상 클래스(abstract)와 인터페이스(interface)를 구분한다
  5. 다형성(polymorphism)으로 유연한 코드를 작성한다
  6. final, protected 접근제어를 이해한다

  ■ 컴파일: javac Main.java
  ■ 실행:   java Main

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/


// =====================================================================
// 레슨 1 — 상속 기본 (extends)
// =====================================================================
/*
★ 상속 = 부모 클래스의 기능을 물려받아 자식 클래스를 만드는 것
  → 코드를 반복하지 않고 공통 기능을 재사용!

  ┌──────────────────────────────────────┐
  │  비유: 상속은 "가족 레시피"           │
  │                                      │
  │  할머니 레시피 (부모 클래스)          │
  │    → 기본 반죽 만들기                │
  │    → 오븐 예열하기                   │
  │                                      │
  │  엄마 레시피 (자식 클래스)            │
  │    → 할머니 레시피 전부 물려받음      │
  │    → + 초콜릿 토핑 추가 (확장!)      │
  └──────────────────────────────────────┘

★ 접근 제어와 상속
  ┌────────────┬──────────────────────────┐
  │ 부모 멤버  │ 자식에서 접근 가능?      │
  ├────────────┼──────────────────────────┤
  │ public     │ O (가능)                 │
  │ protected  │ O (같은 패키지+자식)     │
  │ private    │ X (불가능!)              │
  └────────────┴──────────────────────────┘

★ Java는 단일 상속만 허용! (extends 뒤에 클래스 1개만)
  → 다중 상속이 필요하면 interface를 사용
*/

// ─── 부모 클래스: 동물 ───────────────────────────────────
class Animal {
    // protected: 자식 클래스에서 접근 가능, 외부에서는 불가
    protected String name;
    protected int age;

    // 부모 생성자
    Animal(String name, int age) {
        this.name = name;
        this.age = age;
    }

    // 부모의 일반 메서드 → 자식이 그대로 물려받음
    void eat() {
        System.out.println("  " + name + "이(가) 밥을 먹는다.");
    }

    void sleep() {
        System.out.println("  " + name + "이(가) 잠을 잔다.");
    }

    void info() {
        System.out.println("  [동물] " + name + " (" + age + "살)");
    }
}

// ─── 자식 클래스: 개 ─────────────────────────────────────
/*
★ extends = "확장하다" → 부모의 기능을 물려받고 새 기능을 추가
  Dog는 Animal의 모든 것(eat, sleep, info)을 갖고 있음 + fetch() 추가
*/
class Dog extends Animal {
    private String breed;  // 자식만의 필드 추가

    Dog(String name, int age, String breed) {
        super(name, age);   // ★ super(): 부모 생성자 호출 (반드시 첫 줄!)
        this.breed = breed;
    }

    // 자식만의 새 메서드
    void fetch() {
        System.out.println("  " + name + "이(가) 공을 물어온다!");
    }

    // 부모 info()에 품종 정보를 추가하고 싶다면? → 오버라이딩!
}

// ─── 자식 클래스: 고양이 ─────────────────────────────────
class Cat extends Animal {
    private boolean isIndoor;

    Cat(String name, int age, boolean isIndoor) {
        super(name, age);
        this.isIndoor = isIndoor;
    }

    void purr() {
        System.out.println("  " + name + "이(가) 그르르르...");
    }
}


// =====================================================================
// 레슨 2 — 메서드 오버라이딩 (@Override)
// =====================================================================
/*
★ 오버라이딩 = 부모의 메서드를 자식이 "재정의"하는 것
  → 같은 이름, 같은 매개변수, 다른 동작!

  ┌──────────────────────────────────────────────┐
  │  비유: "발표하기"라는 행동                   │
  │                                              │
  │  부모(사람): 일어서서 말한다                  │
  │  자식(가수): 일어서서 노래를 부른다 (재정의!)│
  │  자식(개그맨): 일어서서 개그한다 (재정의!)   │
  │                                              │
  │  행동의 "이름"은 같지만 "내용"이 다르다!     │
  └──────────────────────────────────────────────┘

★ @Override 어노테이션
  → 붙이면 컴파일러가 "정말 부모에 이 메서드가 있는지" 확인
  → 오타로 다른 이름을 쓰면 컴파일 에러로 잡아줌!
  → 항상 붙이는 습관을 들이자!

  ┌─────────────────────────────────────┐
  │ ★ 오버라이딩 vs 오버로딩            │
  ├─────────────────────────────────────┤
  │ 오버라이딩: 같은 이름 + 같은 매개변수│
  │            → 부모 것을 덮어씀       │
  │                                     │
  │ 오버로딩:  같은 이름 + 다른 매개변수│
  │            → 새로운 메서드 추가     │
  └─────────────────────────────────────┘
*/

class Bird extends Animal {
    private boolean canFly;

    Bird(String name, int age, boolean canFly) {
        super(name, age);
        this.canFly = canFly;
    }

    // ★ 부모의 info()를 오버라이딩
    @Override
    void info() {
        System.out.println("  [새] " + name + " (" + age + "살)"
                + (canFly ? " - 날 수 있음" : " - 날 수 없음"));
    }

    // ★ super.메서드(): 부모 버전을 호출할 수 있음
    void detailedInfo() {
        super.info();  // 부모의 info() 호출
        System.out.println("    → 비행 가능: " + canFly);
    }
}


// =====================================================================
// 레슨 3 — 추상 클래스 (abstract)
// =====================================================================
/*
★ 추상 클래스 = "미완성 설계도"
  → 직접 객체를 만들 수 없고, 자식이 반드시 구현해야 하는 메서드 포함

  ┌──────────────────────────────────────────┐
  │  비유: 추상 클래스는 "시험 문제지"        │
  │                                          │
  │  문제지(추상 클래스):                     │
  │    "1번 문제에 답을 쓰시오" ← abstract    │
  │    "이름을 쓰시오" ← 이미 구현됨          │
  │                                          │
  │  학생(자식 클래스):                       │
  │    반드시 1번 문제에 답을 적어야 제출 가능│
  └──────────────────────────────────────────┘

★ abstract class vs 일반 class
  ┌──────────────┬────────────┬────────────────┐
  │              │ 일반 class │ abstract class  │
  ├──────────────┼────────────┼────────────────┤
  │ 객체 생성    │ O          │ X              │
  │ 일반 메서드  │ O          │ O              │
  │ 추상 메서드  │ X          │ O              │
  │ 생성자       │ O          │ O (자식이 호출)│
  └──────────────┴────────────┴────────────────┘
*/

abstract class Shape {
    protected String name;

    Shape(String name) {
        this.name = name;
    }

    // ★ 추상 메서드: 본문(body)이 없음! 자식이 반드시 구현
    abstract double area();
    abstract String description();

    // 일반 메서드: 이미 구현되어 있어 자식이 그대로 사용 가능
    void printArea() {
        System.out.printf("  [%s] 넓이 = %.2f%n", name, area());
    }
}

class Circle extends Shape {
    private double radius;

    Circle(double radius) {
        super("원");
        this.radius = radius;
    }

    @Override
    double area() {
        return Math.PI * radius * radius;
    }

    @Override
    String description() {
        return "반지름 " + radius + "인 원";
    }
}

class Rectangle extends Shape {
    private double width, height;

    Rectangle(double width, double height) {
        super("사각형");
        this.width = width;
        this.height = height;
    }

    @Override
    double area() {
        return width * height;
    }

    @Override
    String description() {
        return width + " x " + height + " 사각형";
    }
}

class Triangle extends Shape {
    private double base, height;

    Triangle(double base, double height) {
        super("삼각형");
        this.base = base;
        this.height = height;
    }

    @Override
    double area() {
        return 0.5 * base * height;
    }

    @Override
    String description() {
        return "밑변 " + base + ", 높이 " + height + " 삼각형";
    }
}


// =====================================================================
// 레슨 4 — 인터페이스 (interface)
// =====================================================================
/*
★ 인터페이스 = "약속" 또는 "계약서"
  → "이 메서드를 반드시 구현하겠습니다!"라는 약속

  ┌──────────────────────────────────────────────┐
  │  비유: 인터페이스는 "자격증 시험 기준표"      │
  │                                              │
  │  요리사 자격증(Cookable 인터페이스):          │
  │    - 칼질하기()  ← 반드시 할 줄 알아야 함    │
  │    - 불조절하기() ← 반드시 할 줄 알아야 함   │
  │                                              │
  │  김요리사(implements Cookable):               │
  │    - 칼질하기() { 정말 잘 자른다 }            │
  │    - 불조절하기() { 약불로 한다 }             │
  └──────────────────────────────────────────────┘

★ 인터페이스 vs 추상 클래스
  ┌──────────────────┬────────────────┬──────────────┐
  │                  │ interface      │ abstract     │
  ├──────────────────┼────────────────┼──────────────┤
  │ 다중 구현/상속   │ O (여러개)     │ X (1개만)    │
  │ 필드(변수)       │ static final만 │ 자유롭게     │
  │ 생성자           │ X              │ O            │
  │ 메서드 구현      │ default만 가능 │ 자유롭게     │
  │ 키워드           │ implements     │ extends      │
  └──────────────────┴────────────────┴──────────────┘
*/

interface Drawable {
    void draw();  // 추상 메서드 (abstract 생략 가능)

    // ★ default 메서드: Java 8부터! 구현을 가진 메서드
    default void drawWithBorder() {
        System.out.println("  ┌─── 테두리 ───┐");
        draw();
        System.out.println("  └──────────────┘");
    }
}

interface Resizable {
    void resize(double factor);
}

// ★ 인터페이스는 여러 개를 동시에 구현 가능!
class DrawableCircle extends Circle implements Drawable, Resizable {
    private double radius;

    DrawableCircle(double radius) {
        super(radius);
        this.radius = radius;
    }

    @Override
    public void draw() {
        System.out.println("  ●  (반지름=" + radius + ")");
    }

    @Override
    public void resize(double factor) {
        radius *= factor;
        System.out.println("  크기 변경! 새 반지름=" + radius);
    }
}


// =====================================================================
// 레슨 5 — 다형성 (Polymorphism)
// =====================================================================
/*
★ 다형성 = "하나의 타입으로 여러 형태를 다루는 것"
  → 부모 타입의 변수로 자식 객체를 가리킬 수 있음!

  ┌──────────────────────────────────────────────────┐
  │  비유: 다형성은 "리모컨"                          │
  │                                                  │
  │  TV 리모컨(부모 타입)으로:                        │
  │    삼성 TV(자식1)도 켤 수 있고                    │
  │    LG TV(자식2)도 켤 수 있다!                     │
  │                                                  │
  │  "전원 버튼"을 누르면 각 TV가 자기 방식으로 켜짐  │
  │  → 같은 명령, 다른 동작!                          │
  └──────────────────────────────────────────────────┘

★ 핵심 규칙
  부모 변수 = new 자식();  ← 가능!  (업캐스팅)
  자식 변수 = new 부모();  ← 불가능! (컴파일 에러)

★ instanceof 연산자
  → 객체가 특정 클래스의 인스턴스인지 확인
  → if (animal instanceof Dog d) { d.fetch(); }  ← Java 16+ 패턴 매칭
*/


// =====================================================================
// 레슨 6 — final 키워드와 상속 제한
// =====================================================================
/*
★ final은 "더 이상 바꿀 수 없다!"는 의미

  ┌────────────────┬─────────────────────────────┐
  │ final 위치     │ 의미                         │
  ├────────────────┼─────────────────────────────┤
  │ final class    │ 이 클래스를 상속할 수 없음    │
  │ final method   │ 이 메서드를 오버라이딩 불가   │
  │ final variable │ 이 변수에 재대입 불가 (상수)  │
  └────────────────┴─────────────────────────────┘
*/

// final class → 상속 불가
final class MathHelper {
    static double circleArea(double r) {
        return Math.PI * r * r;
    }
    // class SuperMath extends MathHelper {} ← 컴파일 에러!
}


// =====================================================================
// 레슨 7 — 흔한 실수 모음
// =====================================================================
/*
★ 실수 1: super() 호출을 잊음
  → 부모에 기본 생성자가 없으면 반드시 super(...)를 호출해야 함!

★ 실수 2: @Override 안 붙이고 오타
  → info()를 inf()로 잘못 쓰면 새 메서드가 만들어짐 (오버라이딩 아님!)
  → @Override를 붙이면 컴파일러가 잡아줌

★ 실수 3: private 메서드를 오버라이딩 시도
  → private은 자식에서 보이지 않으므로 오버라이딩이 아니라 새 메서드!

★ 실수 4: 부모 타입 변수로 자식 전용 메서드 호출
  → Animal a = new Dog(...);
  → a.fetch();  ← 컴파일 에러! Animal에는 fetch()가 없음
  → ((Dog)a).fetch();  ← 다운캐스팅 필요 (위험할 수 있음!)
*/


// =====================================================================
//  메인 실행
// =====================================================================
public class Main {
    public static void main(String[] args) {
        System.out.println("■■■ Java 06단계: 상속과 다형성 ■■■\n");

        // ─── 레슨 1: 상속 기본 ───────────────────────────
        System.out.println("── 레슨 1: 상속 기본 (extends) ──────────────────");
        Dog dog = new Dog("바둑이", 3, "진돗개");
        dog.info();     // 부모의 메서드를 그대로 물려받음
        dog.eat();      // 부모의 메서드
        dog.fetch();    // 자식만의 메서드

        Cat cat = new Cat("나비", 2, true);
        cat.info();
        cat.sleep();
        cat.purr();
        System.out.println();

        // ─── 레슨 2: 오버라이딩 ──────────────────────────
        System.out.println("── 레슨 2: 메서드 오버라이딩 ────────────────────");
        Bird eagle = new Bird("독수리", 5, true);
        Bird penguin = new Bird("펭귄", 3, false);

        eagle.info();       // 오버라이딩된 info() 호출
        penguin.info();     // 오버라이딩된 info() 호출

        System.out.println("  --- super로 부모 버전 호출 ---");
        eagle.detailedInfo();
        System.out.println();

        // ─── 레슨 3: 추상 클래스 ─────────────────────────
        System.out.println("── 레슨 3: 추상 클래스 (abstract) ───────────────");
        // Shape s = new Shape("모양");  ← 컴파일 에러! 추상 클래스는 객체 생성 불가

        Shape[] shapes = {
            new Circle(5),
            new Rectangle(4, 6),
            new Triangle(3, 8)
        };

        for (Shape s : shapes) {
            System.out.println("  " + s.description());
            s.printArea();
        }
        System.out.println();

        // ─── 레슨 4: 인터페이스 ──────────────────────────
        System.out.println("── 레슨 4: 인터페이스 (interface) ───────────────");
        DrawableCircle dc = new DrawableCircle(3);
        dc.draw();
        dc.drawWithBorder();  // default 메서드
        dc.resize(2.0);
        dc.draw();
        System.out.println();

        // ─── 레슨 5: 다형성 ─────────────────────────────
        System.out.println("── 레슨 5: 다형성 (Polymorphism) ────────────────");

        // ★ 부모 타입 배열에 여러 자식을 담기!
        Animal[] animals = {
            new Dog("멍멍이", 2, "푸들"),
            new Cat("야옹이", 1, false),
            new Bird("참새", 1, true),
            new Bird("타조", 5, false)
        };

        for (Animal a : animals) {
            a.info();   // 각 자식의 오버라이딩된(또는 부모) 메서드 호출!
            a.eat();    // 부모 메서드 (모두 동일)
        }

        System.out.println();
        System.out.println("  --- instanceof로 타입 확인 ---");
        for (Animal a : animals) {
            // ★ Java 16+ 패턴 매칭 instanceof
            if (a instanceof Dog d) {
                d.fetch();  // Dog 전용 메서드 안전하게 호출
            } else if (a instanceof Cat c) {
                c.purr();
            } else if (a instanceof Bird b) {
                b.detailedInfo();
            }
        }
        System.out.println();

        // ─── 레슨 6: final ──────────────────────────────
        System.out.println("── 레슨 6: final 키워드 ─────────────────────────");
        System.out.println("  MathHelper.circleArea(5) = " + MathHelper.circleArea(5));
        System.out.println("  (MathHelper는 final class → 상속 불가!)");
        System.out.println();

        // ─── 레슨 7: 흔한 실수 정리 ─────────────────────
        System.out.println("── 레슨 7: 흔한 실수 정리 ───────────────────────");
        System.out.println("  ★ super() 호출을 잊으면 → 컴파일 에러");
        System.out.println("  ★ @Override 안 붙이고 오타 → 새 메서드가 됨");
        System.out.println("  ★ private 메서드는 오버라이딩 안 됨");
        System.out.println("  ★ 부모 타입 변수로 자식 전용 메서드 호출 → 캐스팅 필요");
        System.out.println();

        // ─── 종합 예제: 직원 급여 시스템 ─────────────────
        System.out.println("── 종합 예제: 직원 급여 시스템 ──────────────────");
        Employee[] employees = {
            new FullTimeEmployee("김사원", 3000000),
            new PartTimeEmployee("이알바", 10000, 80),
            new FullTimeEmployee("박대리", 4000000),
            new PartTimeEmployee("최알바", 12000, 60)
        };

        int totalSalary = 0;
        for (Employee emp : employees) {
            emp.printSalary();
            totalSalary += emp.calculateSalary();
        }
        System.out.println("  ─────────────────────────");
        System.out.println("  총 인건비: " + String.format("%,d", totalSalary) + "원");
        System.out.println();

        System.out.println("■■■ 06단계 학습 완료! ■■■");
    }
}

// ─── 종합 예제용 클래스들 ────────────────────────────────
/*
★ 실전 예제: 직원 급여 시스템
  → 추상 클래스 + 오버라이딩 + 다형성을 모두 활용!

  ┌────────────────────────────────┐
  │  Employee (추상 클래스)        │
  │  ├── FullTimeEmployee (정규직) │
  │  └── PartTimeEmployee (시급직) │
  └────────────────────────────────┘
*/

abstract class Employee {
    protected String name;

    Employee(String name) {
        this.name = name;
    }

    abstract int calculateSalary();

    void printSalary() {
        System.out.println("  " + name + ": "
                + String.format("%,d", calculateSalary()) + "원");
    }
}

class FullTimeEmployee extends Employee {
    private int monthlySalary;

    FullTimeEmployee(String name, int monthlySalary) {
        super(name);
        this.monthlySalary = monthlySalary;
    }

    @Override
    int calculateSalary() {
        return monthlySalary;
    }
}

class PartTimeEmployee extends Employee {
    private int hourlyRate;
    private int hoursWorked;

    PartTimeEmployee(String name, int hourlyRate, int hoursWorked) {
        super(name);
        this.hourlyRate = hourlyRate;
        this.hoursWorked = hoursWorked;
    }

    @Override
    int calculateSalary() {
        return hourlyRate * hoursWorked;
    }
}
