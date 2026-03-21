/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C# 학습 06단계: 상속과 다형성
  ─ virtual, override, abstract, sealed, interface 기초 ─

  ■ 컴파일: dotnet build
  ■ 실행:   dotnet run

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  [학습 목표]
  1. 상속(Inheritance)의 개념과 문법을 이해한다
  2. virtual / override 로 메서드를 재정의한다
  3. 다형성(Polymorphism)으로 유연한 설계를 할 수 있다
  4. abstract 클래스와 abstract 메서드를 이해한다
  5. sealed 클래스로 상속을 금지하는 방법을 안다
  6. base 키워드로 부모 멤버에 접근한다
  7. is / as 연산자와 패턴 매칭으로 타입을 검사한다

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

using System;
using System.Collections.Generic;
using System.Text;

namespace Lesson06
{
    // =====================================================================
    // 레슨 1 — 상속 기본
    // =====================================================================
    /*
    ★ 상속 = 기존 클래스(부모)의 기능을 물려받아 새 클래스(자식)를 만드는 것
      → 코드 재사용 + 계층 구조 설계

    ┌────────────────────────────────────────────────┐
    │  class 자식 : 부모                             │
    │  {                                             │
    │      // 부모의 public/protected 멤버를 물려받음│
    │  }                                             │
    └────────────────────────────────────────────────┘

    ★ 용어 정리
      부모 클래스 = Base class (기반 클래스)
      자식 클래스 = Derived class (파생 클래스)

    ★ 접근 수준과 상속
    ┌──────────────┬───────────────────────────┐
    │ 부모 멤버    │ 자식에서 접근             │
    ├──────────────┼───────────────────────────┤
    │ public       │ ✓ 접근 가능              │
    │ protected    │ ✓ 접근 가능              │
    │ private      │ ✗ 접근 불가!             │
    │ internal     │ ✓ 같은 어셈블리면 가능   │
    └──────────────┴───────────────────────────┘

    ★ 비유: 학교 학생증
      - Animal = 기본 학생증 틀 (이름, 학번 칸)
      - Dog/Cat  = 각 학과별 학생증 (세부 내용만 달라짐)
      이름 칸은 같이 쓰고, 전공 칸만 다르게 적는 느낌!
    */

    // ── 부모 클래스 ──
    class Animal
    {
        // protected: 자식 클래스에서 접근 가능, 외부에서는 불가
        protected string name;
        protected int age;

        public string Name => name;
        public int Age => age;

        public Animal(string name, int age)
        {
            this.name = name;
            this.age = age;
        }

        // 부모에 공통 기능을 둔다
        public void Eat()
        {
            Console.WriteLine($"  {name}이(가) 밥을 먹습니다.");
        }

        public void Sleep()
        {
            Console.WriteLine($"  {name}이(가) 잠을 잡니다. 💤");
        }
    }

    // ── 자식 클래스: Dog ──
    class Dog : Animal
    {
        private string breed;  // 견종 — 자식만의 고유 필드

        // ★ base(name, age) → 부모 생성자 호출
        public Dog(string name, int age, string breed)
            : base(name, age)
        {
            this.breed = breed;
        }

        // 자식만의 메서드
        public void Bark()
        {
            Console.WriteLine($"  {name}: 멍멍! (견종: {breed})");
        }
    }

    // ── 자식 클래스: Cat ──
    class Cat : Animal
    {
        private string color;

        public Cat(string name, int age, string color)
            : base(name, age)
        {
            this.color = color;
        }

        public void Purr()
        {
            Console.WriteLine($"  {name}: 그르릉~ ({color} 고양이)");
        }
    }


    // =====================================================================
    // 레슨 2 — virtual / override : 다형성의 핵심
    // =====================================================================
    /*
    ★ 문제 상황
      부모 타입 변수로 자식 객체를 가리킬 때,
      부모에 정의된 메서드가 호출됨 → 자식의 동작이 안 나옴!

    ★ 해결: virtual + override
      부모 메서드에 virtual → "자식이 재정의해도 돼"
      자식 메서드에 override → "부모 것 대신 내 것을 써"

    ★ 다형성(Polymorphism)
      = 같은 코드(같은 메서드 호출)로 다른 동작을 하게 만드는 것
      = OOP의 가장 강력한 기능!

    ┌──────────────────────────────────────────────────┐
    │  Animal animal = new Dog("초코", 3, "시바");     │
    │  animal.Speak();  // Dog의 Speak가 호출됨!       │
    │                                                  │
    │  → virtual이 없으면 Animal의 Speak가 호출됨      │
    └──────────────────────────────────────────────────┘

    ★ 주의: new 키워드(하이딩)와 override의 차이
      - new: 부모 메서드를 "숨김" → 부모 타입으로 호출하면 부모 것 실행
      - override: 부모 메서드를 "대체" → 부모 타입으로 호출해도 자식 것 실행
    */

    class Shape
    {
        public string ShapeName { get; }

        public Shape(string shapeName)
        {
            ShapeName = shapeName;
        }

        // ★ virtual: 자식이 재정의 가능
        public virtual double Area()
        {
            return 0;
        }

        public virtual void Draw()
        {
            Console.WriteLine($"  [도형] {ShapeName}");
        }

        public virtual string Description()
        {
            return $"{ShapeName} (넓이: {Area():F2})";
        }
    }

    class Circle : Shape
    {
        public double Radius { get; }

        public Circle(double radius) : base("원")
        {
            Radius = radius;
        }

        // ★ override: 부모의 virtual 메서드를 재정의
        public override double Area()
        {
            return Math.PI * Radius * Radius;
        }

        public override void Draw()
        {
            Console.WriteLine($"  [원] 반지름={Radius}, 넓이={Area():F2}");
        }
    }

    class Rectangle : Shape
    {
        public double Width { get; }
        public double Height { get; }

        public Rectangle(double width, double height) : base("사각형")
        {
            Width = width;
            Height = height;
        }

        public override double Area()
        {
            return Width * Height;
        }

        public override void Draw()
        {
            Console.WriteLine($"  [사각형] {Width}x{Height}, 넓이={Area():F2}");
        }
    }

    class Triangle : Shape
    {
        public double Base_ { get; }
        public double Height_ { get; }

        public Triangle(double base_, double height) : base("삼각형")
        {
            Base_ = base_;
            Height_ = height;
        }

        public override double Area()
        {
            return Base_ * Height_ / 2.0;
        }

        public override void Draw()
        {
            Console.WriteLine($"  [삼각형] 밑변={Base_}, 높이={Height_}, 넓이={Area():F2}");
        }
    }


    // =====================================================================
    // 레슨 3 — abstract 클래스와 abstract 메서드
    // =====================================================================
    /*
    ★ abstract 클래스
      - 직접 new로 만들 수 없는 클래스 (불완전한 설계도)
      - 자식이 반드시 구현해야 할 "빈 칸"을 남겨둘 수 있음

    ★ abstract 메서드
      - 본문(body)이 없는 메서드
      - 자식 클래스가 반드시 override 해야 함

    ┌────────────────────────────────────────────────────┐
    │  abstract class Vehicle                            │
    │  {                                                 │
    │      public abstract void Move();  // 본문 없음!  │
    │      public void Honk() { ... }    // 일반 메서드  │
    │  }                                                 │
    │                                                    │
    │  class Car : Vehicle                               │
    │  {                                                 │
    │      public override void Move() { ... } // 필수! │
    │  }                                                 │
    └────────────────────────────────────────────────────┘

    ★ 비유: 시험지 양식
      - abstract class = 시험지 틀 (문제 번호, 이름 칸은 있지만 답은 비어있음)
      - 자식 class = 학생이 답을 채운 시험지
      - 답을 안 쓰면(override 안 하면) 컴파일 에러!
    */

    abstract class Vehicle
    {
        public string VehicleName { get; }

        protected Vehicle(string vehicleName)
        {
            VehicleName = vehicleName;
        }

        // ★ abstract 메서드: 자식이 반드시 구현해야 함
        public abstract void Move();
        public abstract int MaxSpeed();

        // 일반 메서드: 자식이 그대로 쓸 수 있음
        public void Honk()
        {
            Console.WriteLine($"  {VehicleName}: 빵빵!");
        }

        // virtual 메서드: 자식이 재정의 '할 수도 있음' (선택)
        public virtual void DisplayInfo()
        {
            Console.WriteLine($"  [{VehicleName}] 최대속도: {MaxSpeed()}km/h");
        }
    }

    class Car : Vehicle
    {
        public Car() : base("자동차") { }

        public override void Move()
        {
            Console.WriteLine("  자동차가 도로를 달립니다. 🚗");
        }

        public override int MaxSpeed() => 200;
    }

    class Bicycle : Vehicle
    {
        public Bicycle() : base("자전거") { }

        public override void Move()
        {
            Console.WriteLine("  자전거가 자전거 도로를 달립니다. 🚲");
        }

        public override int MaxSpeed() => 40;

        // virtual 메서드를 재정의 (선택사항)
        public override void DisplayInfo()
        {
            Console.WriteLine($"  [{VehicleName}] 최대속도: {MaxSpeed()}km/h (사람 힘으로!)");
        }
    }

    class Airplane : Vehicle
    {
        public Airplane() : base("비행기") { }

        public override void Move()
        {
            Console.WriteLine("  비행기가 하늘을 납니다. ✈");
        }

        public override int MaxSpeed() => 900;
    }


    // =====================================================================
    // 레슨 4 — sealed 클래스: 상속 금지
    // =====================================================================
    /*
    ★ sealed = "이 클래스는 더 이상 상속하지 마세요"
      → 보안, 성능, 설계 의도를 지키기 위해 사용

    ┌──────────────────────────────────────────────┐
    │  sealed class FinalReport : Report           │
    │  {                                           │
    │      // 이 클래스를 상속하면 컴파일 에러!    │
    │  }                                           │
    │                                              │
    │  // class SuperReport : FinalReport { }      │
    │  // ↑ 컴파일 에러! sealed라서 상속 불가      │
    └──────────────────────────────────────────────┘

    ★ sealed override: 특정 메서드만 더 이상 재정의 못하게 막기
      class B : A
      {
          public sealed override void DoWork() { ... }
      }
      → B의 자식은 DoWork를 override 할 수 없음!
    */

    class Report
    {
        public virtual string Generate()
        {
            return "기본 보고서";
        }
    }

    sealed class FinalReport : Report
    {
        public override string Generate()
        {
            return "최종 보고서 (더 이상 변경 불가)";
        }
    }

    // ★ 아래 주석을 풀면 컴파일 에러!
    // class SuperReport : FinalReport { }


    // =====================================================================
    // 레슨 5 — base 키워드: 부모 멤버 호출
    // =====================================================================
    /*
    ★ base 키워드의 두 가지 역할
      1. base(...) → 부모 생성자 호출
      2. base.메서드() → 부모의 메서드 호출

    ┌──────────────────────────────────────────────┐
    │  class Child : Parent                        │
    │  {                                           │
    │      Child() : base("인자") { }  // 생성자  │
    │                                              │
    │      override void Work()                    │
    │      {                                       │
    │          base.Work();  // 부모 로직 먼저     │
    │          // 자식 추가 로직                   │
    │      }                                       │
    │  }                                           │
    └──────────────────────────────────────────────┘
    */

    class Employee
    {
        public string Name { get; }
        public int BaseSalary { get; }

        public Employee(string name, int baseSalary)
        {
            Name = name;
            BaseSalary = baseSalary;
        }

        public virtual int CalculatePay()
        {
            return BaseSalary;
        }

        public virtual string GetTitle()
        {
            return "직원";
        }
    }

    class Manager : Employee
    {
        private int bonus;

        // base(name, baseSalary) → 부모 생성자 호출
        public Manager(string name, int baseSalary, int bonus)
            : base(name, baseSalary)
        {
            this.bonus = bonus;
        }

        public override int CalculatePay()
        {
            // base.CalculatePay() → 부모의 로직을 재활용
            return base.CalculatePay() + bonus;
        }

        public override string GetTitle()
        {
            return "매니저";
        }
    }

    class Director : Manager
    {
        private int stockOption;

        public Director(string name, int baseSalary, int bonus, int stockOption)
            : base(name, baseSalary, bonus)
        {
            this.stockOption = stockOption;
        }

        public override int CalculatePay()
        {
            return base.CalculatePay() + stockOption;
        }

        public override string GetTitle()
        {
            return "이사";
        }
    }


    // =====================================================================
    // 레슨 6 — is / as 연산자와 패턴 매칭
    // =====================================================================
    /*
    ★ 타입 검사가 필요한 경우
      - 부모 타입 배열에 여러 자식이 섞여 있을 때
      - 특정 자식 타입에만 있는 기능을 호출하고 싶을 때

    ┌──────────────────────────────────────────────────────────┐
    │  if (animal is Dog dog)          // C# 7+ 패턴 매칭     │
    │  {                                                      │
    │      dog.Bark();                 // Dog 전용 메서드     │
    │  }                                                      │
    │                                                         │
    │  Cat? cat = animal as Cat;       // 실패하면 null       │
    │  cat?.Purr();                                           │
    │                                                         │
    │  Dog d = (Dog)animal;            // 실패하면 예외 발생! │
    └──────────────────────────────────────────────────────────┘

    ★ 추천 순서
      1. is + 패턴 매칭 (가장 안전하고 읽기 쉬움)
      2. as + null 체크
      3. 직접 캐스팅 (확실할 때만!)
    */


    // =====================================================================
    // 레슨 7 — 다형성 실전 예제: 동물원 시뮬레이션
    // =====================================================================

    abstract class ZooAnimal
    {
        public string AnimalName { get; }
        public string Species { get; }

        protected ZooAnimal(string animalName, string species)
        {
            AnimalName = animalName;
            Species = species;
        }

        public abstract string MakeSound();
        public abstract string FeedingInfo();

        public virtual void ShowInfo()
        {
            Console.WriteLine($"  ┌─────────────────────────────────┐");
            Console.WriteLine($"  │ 이름: {AnimalName,-10} 종: {Species,-8}│");
            Console.WriteLine($"  │ 소리: {MakeSound(),-25}│");
            Console.WriteLine($"  │ 먹이: {FeedingInfo(),-25}│");
            Console.WriteLine($"  └─────────────────────────────────┘");
        }
    }

    class ZooDog : ZooAnimal
    {
        public ZooDog(string name) : base(name, "개") { }
        public override string MakeSound() => "멍멍!";
        public override string FeedingInfo() => "사료 200g, 물";
    }

    class ZooCat : ZooAnimal
    {
        public ZooCat(string name) : base(name, "고양이") { }
        public override string MakeSound() => "야옹~";
        public override string FeedingInfo() => "사료 150g, 물, 간식";
    }

    class ZooBird : ZooAnimal
    {
        public bool CanFly { get; }

        public ZooBird(string name, bool canFly) : base(name, "새")
        {
            CanFly = canFly;
        }

        public override string MakeSound() => "짹짹!";
        public override string FeedingInfo() => "모이 50g, 물";

        // sealed override — 이 메서드는 ZooBird의 자식이 더 이상 재정의 불가
        public sealed override void ShowInfo()
        {
            base.ShowInfo();
            Console.WriteLine($"    비행 가능: {(CanFly ? "예" : "아니오")}");
        }
    }


    // =====================================================================
    // Main — 모든 레슨 실행
    // =====================================================================
    class Program
    {
        static void Lesson1BasicInheritance()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 1: 상속 기본 — 부모의 기능을 물려받기");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            Dog dog = new Dog("초코", 3, "시바견");
            dog.Eat();       // Animal의 메서드 → 상속받아서 사용 가능
            dog.Sleep();     // Animal의 메서드
            dog.Bark();      // Dog만의 메서드
            Console.WriteLine();

            Cat cat = new Cat("나비", 2, "흰색");
            cat.Eat();       // Animal의 메서드
            cat.Purr();      // Cat만의 메서드
            Console.WriteLine();

            // ★ 부모 타입 변수에 자식 객체를 담을 수 있다! (업캐스팅)
            Animal animal = dog;
            animal.Eat();    // OK: Animal에 있는 메서드
            // animal.Bark(); // ★ 컴파일 에러! Animal 타입에는 Bark가 없음
            Console.WriteLine("  → 부모 타입 변수에 자식을 담으면, 부모에 정의된 멤버만 보임");
            Console.WriteLine();
        }

        static void Lesson2VirtualOverride()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 2: virtual/override — 다형성의 핵심");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // 다양한 도형을 부모 타입 배열에 담기
            Shape[] shapes = new Shape[]
            {
                new Circle(5),
                new Rectangle(4, 6),
                new Triangle(3, 8),
                new Circle(2.5),
            };

            // ★ 다형성: 같은 코드(Draw 호출)인데 각자 다른 동작!
            Console.WriteLine("  [모든 도형 그리기]");
            double totalArea = 0;
            foreach (Shape shape in shapes)
            {
                shape.Draw();      // 각 자식의 override된 Draw가 호출됨!
                totalArea += shape.Area();
            }
            Console.WriteLine($"\n  전체 도형 넓이 합계: {totalArea:F2}");
            Console.WriteLine();

            /*
            ★ 왜 다형성이 편한가?
              - 새 도형(오각형 등)을 추가해도 Shape을 상속하고
                Area, Draw만 override 하면 끝!
              - 위의 foreach 코드는 전혀 수정할 필요 없음
              - 이것이 OCP (Open-Closed Principle):
                "확장에는 열려있고, 수정에는 닫혀있다"
            */
        }

        static void Lesson3AbstractClass()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 3: abstract 클래스 — 불완전한 설계도");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // Vehicle vehicle = new Vehicle();  // ★ 컴파일 에러! abstract는 new 불가
            Vehicle[] vehicles = new Vehicle[]
            {
                new Car(),
                new Bicycle(),
                new Airplane(),
            };

            foreach (Vehicle v in vehicles)
            {
                v.Move();           // abstract 메서드 → 자식이 반드시 구현
                v.Honk();           // 일반 메서드 → 부모 것 그대로
                v.DisplayInfo();    // virtual 메서드 → 재정의한 것 or 부모 것
                Console.WriteLine();
            }
        }

        static void Lesson4SealedClass()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 4: sealed — 상속 금지 잠금장치");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            Report basic = new Report();
            FinalReport final_ = new FinalReport();

            Console.WriteLine("  기본 보고서: " + basic.Generate());
            Console.WriteLine("  최종 보고서: " + final_.Generate());
            Console.WriteLine();
            Console.WriteLine("  ★ FinalReport는 sealed이므로 더 이상 상속 불가!");
            Console.WriteLine("  ★ string, DateTime 등 .NET의 많은 타입이 sealed임");
            Console.WriteLine();
        }

        static void Lesson5BaseKeyword()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 5: base 키워드 — 부모 멤버 호출");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            Employee emp = new Employee("김철수", 3000);
            Manager mgr = new Manager("이영희", 4000, 1000);
            Director dir = new Director("박지성", 5000, 2000, 3000);

            // base.CalculatePay() 체이닝으로 급여 누적 계산
            Console.WriteLine($"  {emp.GetTitle()} {emp.Name}: {emp.CalculatePay()}만원");
            Console.WriteLine($"  {mgr.GetTitle()} {mgr.Name}: {mgr.CalculatePay()}만원 (기본+보너스)");
            Console.WriteLine($"  {dir.GetTitle()} {dir.Name}: {dir.CalculatePay()}만원 (기본+보너스+스톡옵션)");
            Console.WriteLine();

            /*
            ★ base 호출 체인:
              Director.CalculatePay()
                → Manager.CalculatePay() + stockOption
                  → Employee.CalculatePay() + bonus + stockOption
                    → baseSalary + bonus + stockOption = 5000 + 2000 + 3000 = 10000
            */
        }

        static void Lesson6TypeChecking()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 6: is / as 연산자 — 타입 검사");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            Animal[] animals = new Animal[]
            {
                new Dog("초코", 3, "시바견"),
                new Cat("나비", 2, "흰색"),
                new Dog("보리", 5, "골든리트리버"),
                new Cat("루나", 1, "검은색"),
            };

            foreach (Animal animal in animals)
            {
                // ★ is + 패턴 매칭: 타입 확인과 변환을 동시에!
                if (animal is Dog dog)
                {
                    Console.Write($"  🐕 ");
                    dog.Bark();
                }
                else if (animal is Cat cat)
                {
                    Console.Write($"  🐈 ");
                    cat.Purr();
                }
            }

            Console.WriteLine();

            // as 연산자: 변환 실패 시 null 반환 (예외 없음)
            Animal firstAnimal = animals[0];
            Cat? maybeCat = firstAnimal as Cat;
            Console.WriteLine("  as Cat 결과: " + (maybeCat == null ? "null (Dog이니까!)" : maybeCat.Name));
            Console.WriteLine();
        }

        static void Lesson7ZooSimulation()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 7: 실전 — 동물원 시뮬레이션");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            List<ZooAnimal> zoo = new List<ZooAnimal>
            {
                new ZooDog("초코"),
                new ZooCat("나비"),
                new ZooBird("참새", true),
                new ZooBird("펭귄", false),
            };

            // ★ 다형성의 진가: 코드 한 줄로 모든 동물 처리
            foreach (ZooAnimal animal in zoo)
            {
                animal.ShowInfo();
                Console.WriteLine();
            }

            // 타입별 통계
            int dogCount = 0, catCount = 0, birdCount = 0;
            foreach (ZooAnimal animal in zoo)
            {
                if (animal is ZooDog) dogCount++;
                else if (animal is ZooCat) catCount++;
                else if (animal is ZooBird) birdCount++;
            }

            Console.WriteLine("  ┌─────────────────────────────┐");
            Console.WriteLine("  │     동물원 현황 보고서      │");
            Console.WriteLine("  ├─────────────────────────────┤");
            Console.WriteLine($"  │ 개:     {dogCount}마리               │");
            Console.WriteLine($"  │ 고양이: {catCount}마리               │");
            Console.WriteLine($"  │ 새:     {birdCount}마리               │");
            Console.WriteLine($"  │ 합계:   {zoo.Count}마리               │");
            Console.WriteLine("  └─────────────────────────────┘");
            Console.WriteLine();
        }

        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine("  C# 06단계: 상속과 다형성");
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine();

            Lesson1BasicInheritance();
            Lesson2VirtualOverride();
            Lesson3AbstractClass();
            Lesson4SealedClass();
            Lesson5BaseKeyword();
            Lesson6TypeChecking();
            Lesson7ZooSimulation();

            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  ★ 정리");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  1. 상속: class 자식 : 부모 — 코드 재사용");
            Console.WriteLine("  2. virtual/override: 다형성의 핵심 메커니즘");
            Console.WriteLine("  3. abstract: 불완전한 설계도, new 불가");
            Console.WriteLine("  4. sealed: 상속 금지 잠금장치");
            Console.WriteLine("  5. base: 부모 생성자/메서드 호출");
            Console.WriteLine("  6. is/as: 안전한 타입 검사와 변환");
            Console.WriteLine();
        }
    }
}
