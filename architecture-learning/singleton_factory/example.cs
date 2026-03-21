using System;
using System.Collections.Generic;

namespace ArchitectureLearning.SingletonFactory
{
    /*
    ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
      싱글턴 + 팩토리 패턴 (Singleton & Factory Pattern)
      실행 방법: dotnet script example.cs  또는  csc example.cs && example.exe
    ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

      싱글턴이란?
      프로그램 전체에서 "딱 하나만" 존재하는 객체를 만드는 패턴입니다.
      비유: 학교에 교장 선생님은 한 분만! 아무리 호출해도 같은 분.

      팩토리란?
      객체를 직접 new로 만들지 않고, "공장(Factory)"에 부탁하는 패턴입니다.
      비유: 장난감 가게에서 "자동차 하나 주세요" 하면
            가게가 알아서 만들어 줌. 어떻게 만드는지는 내가 몰라도 됨.
    ═══════════════════════════════════════════════════════════════════════
    */

    // ┌─────────────────────────────────────────────┐
    // │  싱글턴: 데이터베이스 연결 (하나만!)           │
    // └─────────────────────────────────────────────┘

    // 방법 1: 기본 싱글턴 (스레드 안전 X)
    public class SimpleDatabase
    {
        // private 생성자: 바깥에서 new로 못 만듦!
        private SimpleDatabase()
        {
            Console.WriteLine("    [DB] 데이터베이스 연결 생성 (비용 큼!)");
            ConnectionId = Guid.NewGuid().ToString().Substring(0, 8);
        }

        private static SimpleDatabase _instance;

        // 전체 프로그램에서 이 메서드로만 접근
        public static SimpleDatabase Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = new SimpleDatabase();
                }
                return _instance;
            }
        }

        public string ConnectionId { get; }

        public void Query(string sql)
        {
            Console.WriteLine($"    [DB-{ConnectionId}] 실행: {sql}");
        }
    }

    // 방법 2: 스레드 안전 싱글턴 (Lazy<T> 사용 — 추천!)
    public class ThreadSafeDatabase
    {
        /*
          Lazy<T>는 처음 접근할 때만 생성하고,
          이후로는 같은 인스턴스를 돌려줍니다.
          스레드 안전도 자동으로 보장합니다!

          비유: 냉장고에 우유가 없으면 처음 한 번만 사러 가고,
                그 다음부터는 있는 걸 쓰는 것.
                두 사람이 동시에 가려고 해도 한 명만 감.
        */

        private ThreadSafeDatabase()
        {
            Console.WriteLine("    [SafeDB] 스레드 안전한 DB 연결 생성!");
            ConnectionId = Guid.NewGuid().ToString().Substring(0, 8);
        }

        // Lazy<T>로 선언하면 스레드 안전 + 지연 초기화 자동!
        private static readonly Lazy<ThreadSafeDatabase> _lazy =
            new Lazy<ThreadSafeDatabase>(() => new ThreadSafeDatabase());

        public static ThreadSafeDatabase Instance => _lazy.Value;

        public string ConnectionId { get; }

        public void Query(string sql)
        {
            Console.WriteLine($"    [SafeDB-{ConnectionId}] 실행: {sql}");
        }
    }

    // ┌─────────────────────────────────────────────┐
    // │  팩토리 메서드: 도형 만들기                   │
    // └─────────────────────────────────────────────┘
    // "어떤 도형을 만들지"를 팩토리가 결정합니다.
    // 사용하는 쪽은 "도형 하나 줘" 하면 됩니다.

    // 도형 인터페이스
    public interface IShape
    {
        string Name { get; }
        double Area();
        void Draw();
    }

    // 구체적인 도형들
    public class Circle : IShape
    {
        public string Name => "원";
        public double Radius { get; }

        public Circle(double radius) { Radius = radius; }

        public double Area() => Math.PI * Radius * Radius;

        public void Draw()
        {
            Console.WriteLine($"    ○ {Name} (반지름: {Radius}, 넓이: {Area():F2})");
        }
    }

    public class Rectangle : IShape
    {
        public string Name => "직사각형";
        public double Width { get; }
        public double Height { get; }

        public Rectangle(double width, double height)
        {
            Width = width;
            Height = height;
        }

        public double Area() => Width * Height;

        public void Draw()
        {
            Console.WriteLine($"    □ {Name} ({Width}x{Height}, 넓이: {Area():F2})");
        }
    }

    public class Triangle : IShape
    {
        public string Name => "삼각형";
        public double Base { get; }
        public double Height { get; }

        public Triangle(double baseLen, double height)
        {
            Base = baseLen;
            Height = height;
        }

        public double Area() => Base * Height / 2;

        public void Draw()
        {
            Console.WriteLine($"    △ {Name} (밑변: {Base}, 높이: {Height}, 넓이: {Area():F2})");
        }
    }

    // ┌─────────────────────────────────────────────┐
    // │  팩토리 메서드 패턴                           │
    // └─────────────────────────────────────────────┘
    // 비유: "원 하나 주세요" → 팩토리가 Circle을 만들어서 줌.
    //       어떻게 만드는지는 팩토리 안에 숨겨져 있음.

    public static class ShapeFactory
    {
        public static IShape Create(string type, params double[] args)
        {
            switch (type.ToLower())
            {
                case "circle":
                case "원":
                    return new Circle(args.Length > 0 ? args[0] : 1);

                case "rectangle":
                case "직사각형":
                    return new Rectangle(
                        args.Length > 0 ? args[0] : 1,
                        args.Length > 1 ? args[1] : 1);

                case "triangle":
                case "삼각형":
                    return new Triangle(
                        args.Length > 0 ? args[0] : 1,
                        args.Length > 1 ? args[1] : 1);

                default:
                    throw new ArgumentException($"알 수 없는 도형: {type}");
            }
        }
    }

    // ┌─────────────────────────────────────────────┐
    // │  추상 팩토리: 테마별 UI 컴포넌트              │
    // └─────────────────────────────────────────────┘
    // 추상 팩토리는 "관련된 객체들을 세트로" 만드는 패턴입니다.
    // 비유: "밝은 테마 세트" 또는 "어두운 테마 세트"를 통째로 만드는 것.

    // UI 컴포넌트 인터페이스들
    public interface IButton
    {
        void Render();
    }

    public interface ITextBox
    {
        void Render();
    }

    // 밝은 테마
    public class LightButton : IButton
    {
        public void Render() => Console.WriteLine("    [ 밝은 버튼 ] 흰 배경, 검정 글씨");
    }

    public class LightTextBox : ITextBox
    {
        public void Render() => Console.WriteLine("    [ 밝은 입력칸 ] 흰 배경, 검정 테두리");
    }

    // 어두운 테마
    public class DarkButton : IButton
    {
        public void Render() => Console.WriteLine("    [ 어두운 버튼 ] 검정 배경, 흰 글씨");
    }

    public class DarkTextBox : ITextBox
    {
        public void Render() => Console.WriteLine("    [ 어두운 입력칸 ] 회색 배경, 파란 테두리");
    }

    // 추상 팩토리 인터페이스
    public interface IUIFactory
    {
        IButton CreateButton();
        ITextBox CreateTextBox();
    }

    public class LightThemeFactory : IUIFactory
    {
        public IButton CreateButton() => new LightButton();
        public ITextBox CreateTextBox() => new LightTextBox();
    }

    public class DarkThemeFactory : IUIFactory
    {
        public IButton CreateButton() => new DarkButton();
        public ITextBox CreateTextBox() => new DarkTextBox();
    }

    // ┌─────────────────────────────────────────────┐
    // │  실행                                        │
    // └─────────────────────────────────────────────┘
    internal class Program
    {
        static void Main()
        {
            Console.WriteLine(new string('=', 60));
            Console.WriteLine("  싱글턴 + 팩토리 패턴");
            Console.WriteLine(new string('=', 60));
            Console.WriteLine();

            Lesson1_Singleton();
            Lesson2_ThreadSafeSingleton();
            Lesson3_FactoryMethod();
            Lesson4_AbstractFactory();
            Lesson5_Summary();
        }

        static void Lesson1_Singleton()
        {
            Console.WriteLine("[레슨 1] 싱글턴 — 세상에 딱 하나");
            Console.WriteLine();

            // 여러 번 호출해도 같은 객체!
            var db1 = SimpleDatabase.Instance;
            var db2 = SimpleDatabase.Instance;

            Console.WriteLine($"    db1 ID: {db1.ConnectionId}");
            Console.WriteLine($"    db2 ID: {db2.ConnectionId}");
            Console.WriteLine($"    같은 객체? {ReferenceEquals(db1, db2)}");

            db1.Query("SELECT * FROM students");
            Console.WriteLine();
        }

        static void Lesson2_ThreadSafeSingleton()
        {
            Console.WriteLine("[레슨 2] 스레드 안전 싱글턴 — Lazy<T>");
            Console.WriteLine();

            var db1 = ThreadSafeDatabase.Instance;
            var db2 = ThreadSafeDatabase.Instance;

            Console.WriteLine($"    같은 객체? {ReferenceEquals(db1, db2)}");
            db1.Query("INSERT INTO grades VALUES (1, 95)");
            Console.WriteLine();
        }

        static void Lesson3_FactoryMethod()
        {
            Console.WriteLine("[레슨 3] 팩토리 메서드 — 도형 공장");
            Console.WriteLine();

            // 사용하는 쪽은 new Circle(), new Rectangle()을 모릅니다.
            // "원 하나 줘" 하면 팩토리가 알아서 만들어 줍니다.

            var shapes = new List<IShape>
            {
                ShapeFactory.Create("원", 5),
                ShapeFactory.Create("직사각형", 4, 6),
                ShapeFactory.Create("삼각형", 3, 8),
            };

            foreach (var shape in shapes)
            {
                shape.Draw();
            }

            // 장점: 새 도형(오각형 등)을 추가해도
            // ShapeFactory와 새 클래스만 수정하면 됩니다.
            // 사용하는 쪽 코드는 변경 불필요!
            Console.WriteLine();
        }

        static void Lesson4_AbstractFactory()
        {
            Console.WriteLine("[레슨 4] 추상 팩토리 — 테마 세트 만들기");
            Console.WriteLine();

            // 테마를 바꿀 때 팩토리만 교체하면 됩니다!
            Console.WriteLine("  === 밝은 테마 ===");
            RenderUI(new LightThemeFactory());

            Console.WriteLine("  === 어두운 테마 ===");
            RenderUI(new DarkThemeFactory());

            Console.WriteLine();
        }

        static void RenderUI(IUIFactory factory)
        {
            // 이 함수는 어떤 테마인지 모릅니다!
            // 팩토리가 만들어 주는 대로 쓸 뿐입니다.
            var button = factory.CreateButton();
            var textBox = factory.CreateTextBox();
            button.Render();
            textBox.Render();
        }

        static void Lesson5_Summary()
        {
            Console.WriteLine("[레슨 5] 정리");
            Console.WriteLine();

            Console.WriteLine("  ┌───────────────────┬────────────────────────────────┐");
            Console.WriteLine("  │  패턴              │  핵심                          │");
            Console.WriteLine("  ├───────────────────┼────────────────────────────────┤");
            Console.WriteLine("  │  싱글턴            │  인스턴스가 딱 하나만 존재        │");
            Console.WriteLine("  │  팩토리 메서드     │  생성을 서브클래스/메서드에 위임   │");
            Console.WriteLine("  │  추상 팩토리       │  관련 객체 세트를 통째로 생성     │");
            Console.WriteLine("  └───────────────────┴────────────────────────────────┘");
            Console.WriteLine();
            Console.WriteLine("  싱글턴 주의사항:");
            Console.WriteLine("    - 전역 상태이므로 남용하면 테스트가 어려워짐");
            Console.WriteLine("    - 가능하면 DI(의존성 주입)로 대체하는 것을 권장");
            Console.WriteLine();
        }
    }
}
