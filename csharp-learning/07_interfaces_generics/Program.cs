/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C# 학습 07단계: 인터페이스와 제네릭
  ─ interface, 다중 구현, 제네릭 클래스/메서드, 제약 조건 ─

  ■ 컴파일: dotnet build
  ■ 실행:   dotnet run

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  [학습 목표]
  1. 인터페이스(interface)의 개념과 문법을 이해한다
  2. 다중 인터페이스 구현을 할 수 있다
  3. 인터페이스 vs 추상 클래스 차이를 안다
  4. 제네릭(Generic) 클래스와 메서드를 만든다
  5. where 제약 조건으로 타입을 제한한다
  6. 공변성(covariance)과 반공변성(contravariance) 개념을 안다

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

using System;
using System.Collections.Generic;
using System.Text;

namespace Lesson07
{
    // =====================================================================
    // 레슨 1 — 인터페이스 기본
    // =====================================================================
    /*
    ★ 인터페이스 = "이 기능을 할 수 있다"는 약속(계약)
      - 메서드 시그니처만 정의, 구현은 클래스가 담당
      - C#에서는 관례적으로 이름 앞에 I를 붙임 (IDisposable, IComparable 등)

    ┌──────────────────────────────────────────────────┐
    │  interface IPrintable                            │
    │  {                                               │
    │      void Print();  // 선언만! 본문 없음         │
    │  }                                               │
    │                                                  │
    │  class Report : IPrintable                       │
    │  {                                               │
    │      public void Print() { ... }  // 반드시 구현 │
    │  }                                               │
    └──────────────────────────────────────────────────┘

    ★ 비유: 콘센트 규격
      전자제품 회사가 달라도 콘센트 규격(interface)이 같으면
      같은 멀티탭에 꽂을 수 있다!
      → IPrintable을 구현하면 어떤 객체든 Print()를 호출할 수 있다
    */

    interface IPrintable
    {
        void Print();
    }

    interface ISaveable
    {
        bool Save(string path);
    }

    // ★ C# 8.0+: 인터페이스에 기본 구현(Default Implementation)을 넣을 수 있음
    interface ILoggable
    {
        void Log(string message);

        // 기본 구현 — 구현 클래스가 override 하지 않으면 이것이 사용됨
        void LogError(string message)
        {
            Log($"[ERROR] {message}");
        }
    }


    // =====================================================================
    // 레슨 2 — 다중 인터페이스 구현
    // =====================================================================
    /*
    ★ C#은 다중 상속 불가! (class A : B, C → 에러)
      하지만 인터페이스는 여러 개 구현 가능!

    ┌──────────────────────────────────────────────────┐
    │  class Document : IPrintable, ISaveable, ILoggable│
    │  {                                               │
    │      // 세 인터페이스의 메서드를 모두 구현       │
    │  }                                               │
    └──────────────────────────────────────────────────┘

    ★ 인터페이스 vs 추상 클래스
    ┌──────────────────┬──────────────────┬──────────────────┐
    │                  │  인터페이스      │  추상 클래스     │
    ├──────────────────┼──────────────────┼──────────────────┤
    │ 다중 적용        │ ✓ 여러 개 가능  │ ✗ 하나만 상속   │
    │ 필드(상태)       │ ✗ 불가          │ ✓ 가능          │
    │ 생성자           │ ✗ 불가          │ ✓ 가능          │
    │ 접근 제한자      │ 기본 public     │ 자유롭게 설정   │
    │ 기본 구현(C# 8+)│ ✓ 가능          │ ✓ 가능          │
    │ 사용 시점        │ "할 수 있다"    │ "~이다" 관계    │
    └──────────────────┴──────────────────┴──────────────────┘
    */

    class Document : IPrintable, ISaveable, ILoggable
    {
        public string Title { get; }
        public string Content { get; }

        public Document(string title, string content)
        {
            Title = title;
            Content = content;
        }

        // IPrintable 구현
        public void Print()
        {
            Console.WriteLine($"  📄 [{Title}] {Content}");
        }

        // ISaveable 구현
        public bool Save(string path)
        {
            Console.WriteLine($"  💾 '{Title}'을(를) {path}에 저장합니다.");
            return true;  // 실제로는 파일 I/O
        }

        // ILoggable 구현
        public void Log(string message)
        {
            Console.WriteLine($"  📝 로그: {message}");
        }
        // LogError는 기본 구현을 그대로 사용
    }


    // =====================================================================
    // 레슨 3 — 명시적 인터페이스 구현
    // =====================================================================
    /*
    ★ 두 인터페이스에 같은 이름의 메서드가 있을 때?
      → 명시적 구현(Explicit Implementation)으로 구분!

    ┌──────────────────────────────────────────────────┐
    │  interface IKorean  { string Greet(); }           │
    │  interface IEnglish { string Greet(); }           │
    │                                                  │
    │  class Translator : IKorean, IEnglish             │
    │  {                                               │
    │      string IKorean.Greet()  => "안녕하세요";    │
    │      string IEnglish.Greet() => "Hello";         │
    │  }                                               │
    └──────────────────────────────────────────────────┘

    ★ 명시적 구현된 메서드는 인터페이스 타입으로만 호출 가능!
      Translator t = new Translator();
      // t.Greet();  // 에러!
      ((IKorean)t).Greet();   // OK: "안녕하세요"
      ((IEnglish)t).Greet();  // OK: "Hello"
    */

    interface IKoreanGreeter
    {
        string Greet();
    }

    interface IEnglishGreeter
    {
        string Greet();
    }

    class Translator : IKoreanGreeter, IEnglishGreeter
    {
        // 명시적 구현: 인터페이스명.메서드명
        string IKoreanGreeter.Greet() => "안녕하세요!";
        string IEnglishGreeter.Greet() => "Hello!";

        // 일반 메서드로 둘 다 보여주기
        public void GreetBoth()
        {
            string kr = ((IKoreanGreeter)this).Greet();
            string en = ((IEnglishGreeter)this).Greet();
            Console.WriteLine($"  한국어: {kr}  영어: {en}");
        }
    }


    // =====================================================================
    // 레슨 4 — 제네릭 클래스
    // =====================================================================
    /*
    ★ 제네릭 = 타입을 매개변수로 받는 것
      → 같은 로직을 int, string, Student 등 다양한 타입에 재사용!

    ┌──────────────────────────────────────────────────┐
    │  class Box<T>                                    │
    │  {                                               │
    │      public T Value { get; set; }                │
    │  }                                               │
    │                                                  │
    │  Box<int> intBox = new Box<int>();                │
    │  Box<string> strBox = new Box<string>();          │
    │  // T가 int로, string으로 교체됨!               │
    └──────────────────────────────────────────────────┘

    ★ 비유: 택배 상자
      같은 모양 상자에 신발을 넣으면 신발 상자,
      책을 넣으면 책 상자 → 상자 틀(Box<T>)은 하나!
    */

    class Box<T>
    {
        public T Value { get; }

        public Box(T value)
        {
            Value = value;
        }

        public override string ToString()
        {
            return $"Box<{typeof(T).Name}>({Value})";
        }
    }

    // 제네릭 클래스: 키-값 쌍
    class Pair<TKey, TValue>
    {
        public TKey Key { get; }
        public TValue Val { get; }

        public Pair(TKey key, TValue value)
        {
            Key = key;
            Val = value;
        }

        public override string ToString()
        {
            return $"({Key}: {Val})";
        }
    }

    // 제네릭 스택 (자료구조 직접 구현)
    class SimpleStack<T>
    {
        private readonly List<T> items = new List<T>();

        public int Count => items.Count;

        public void Push(T item)
        {
            items.Add(item);
        }

        public T Pop()
        {
            if (items.Count == 0)
                throw new InvalidOperationException("스택이 비어있습니다!");

            T item = items[items.Count - 1];
            items.RemoveAt(items.Count - 1);
            return item;
        }

        public T Peek()
        {
            if (items.Count == 0)
                throw new InvalidOperationException("스택이 비어있습니다!");

            return items[items.Count - 1];
        }
    }


    // =====================================================================
    // 레슨 5 — 제네릭 메서드
    // =====================================================================
    /*
    ★ 메서드 하나에도 제네릭을 적용할 수 있음
      → 타입마다 같은 함수를 새로 쓰지 않아도 됨!

    ┌──────────────────────────────────────────────────┐
    │  static T Max<T>(T a, T b) where T : IComparable │
    │  {                                               │
    │      return a.CompareTo(b) >= 0 ? a : b;         │
    │  }                                               │
    │                                                  │
    │  Max(3, 5);        // T = int  → 5               │
    │  Max("a", "z");    // T = string → "z"           │
    └──────────────────────────────────────────────────┘
    */


    // =====================================================================
    // 레슨 6 — where 제약 조건
    // =====================================================================
    /*
    ★ 제네릭 타입에 "아무 타입이나" 들어오면 곤란할 때가 있음
      → where로 제약을 걸어 안전하게 만듦!

    ┌──────────────────────────────────────────────────────────┐
    │  제약 조건               │ 의미                         │
    ├──────────────────────────┼──────────────────────────────┤
    │  where T : class         │ 참조 타입만                  │
    │  where T : struct        │ 값 타입만                    │
    │  where T : new()         │ 매개변수 없는 생성자 필요    │
    │  where T : 인터페이스    │ 해당 인터페이스 구현 필수    │
    │  where T : 기반클래스    │ 해당 클래스 상속 필수        │
    │  where T : notnull       │ null 불가 (C# 8+)           │
    └──────────────────────────┴──────────────────────────────┘
    */

    interface IIdentifiable
    {
        int Id { get; }
        string DisplayName { get; }
    }

    class Student : IIdentifiable, IPrintable
    {
        public int Id { get; }
        public string Name { get; }
        public int Score { get; }
        public string DisplayName => $"{Name}({Score}점)";

        public Student(int id, string name, int score)
        {
            Id = id;
            Name = name;
            Score = score;
        }

        public void Print()
        {
            Console.WriteLine($"  학생 #{Id}: {Name} - {Score}점");
        }
    }

    class Product : IIdentifiable
    {
        public int Id { get; }
        public string ProductName { get; }
        public int Price { get; }
        public string DisplayName => $"{ProductName}({Price}원)";

        public Product(int id, string productName, int price)
        {
            Id = id;
            ProductName = productName;
            Price = price;
        }
    }

    // ★ where T : IIdentifiable → T는 반드시 IIdentifiable을 구현해야 함
    class Repository<T> where T : IIdentifiable
    {
        private readonly List<T> items = new List<T>();

        public void Add(T item)
        {
            items.Add(item);
        }

        public T? FindById(int id)
        {
            foreach (T item in items)
            {
                if (item.Id == id)
                    return item;
            }
            return default;
        }

        public List<T> GetAll() => new List<T>(items);

        public void PrintAll()
        {
            foreach (T item in items)
            {
                Console.WriteLine($"  [{item.Id}] {item.DisplayName}");
            }
        }
    }


    // =====================================================================
    // Main — 모든 레슨 실행
    // =====================================================================
    class Program
    {
        // ── 제네릭 메서드들 ──
        static T PickFirst<T>(List<T> items)
        {
            if (items.Count == 0)
                throw new InvalidOperationException("목록이 비어있습니다!");
            return items[0];
        }

        static T Max<T>(T a, T b) where T : IComparable<T>
        {
            return a.CompareTo(b) >= 0 ? a : b;
        }

        static T Min<T>(T a, T b) where T : IComparable<T>
        {
            return a.CompareTo(b) <= 0 ? a : b;
        }

        static void Swap<T>(ref T a, ref T b)
        {
            T temp = a;
            a = b;
            b = temp;
        }

        static void Lesson1InterfaceBasics()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 1: 인터페이스 — 기능의 약속");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            Document doc = new Document("보고서", "1분기 매출 현황");

            // IPrintable로 사용
            IPrintable printable = doc;
            printable.Print();

            // ISaveable로 사용
            ISaveable saveable = doc;
            saveable.Save("/reports/q1.txt");

            // ILoggable로 사용
            ILoggable loggable = doc;
            loggable.Log("문서가 열렸습니다.");
            loggable.LogError("저장 실패!");  // 기본 구현 사용
            Console.WriteLine();

            // ★ 핵심: 하나의 객체를 여러 인터페이스 타입으로 다룰 수 있다!
            Console.WriteLine("  → 같은 Document 객체를 IPrintable, ISaveable, ILoggable로 다룸");
            Console.WriteLine();
        }

        static void Lesson2MultipleInterfaces()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 2: 다중 인터페이스 구현");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // 다양한 IPrintable 객체를 같은 배열에 담기
            IPrintable[] printables = new IPrintable[]
            {
                new Document("공지사항", "내일은 체육대회"),
                new Document("시험 결과", "평균 82점"),
                new Student(1, "민수", 95),  // Student도 IPrintable 구현!
            };

            Console.WriteLine("  [모두 출력하기 — 다형성!]");
            foreach (IPrintable p in printables)
            {
                p.Print();
            }
            Console.WriteLine();
        }

        static void Lesson3ExplicitImplementation()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 3: 명시적 인터페이스 구현");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            Translator translator = new Translator();
            translator.GreetBoth();

            // 인터페이스 타입으로 캐스팅해서 호출
            IKoreanGreeter kr = translator;
            IEnglishGreeter en = translator;
            Console.WriteLine($"  IKoreanGreeter.Greet()  → {kr.Greet()}");
            Console.WriteLine($"  IEnglishGreeter.Greet() → {en.Greet()}");
            Console.WriteLine();
        }

        static void Lesson4GenericClass()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 4: 제네릭 클래스 — 타입을 매개변수로");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // Box<T>: 같은 틀에 다른 타입을 넣기
            var intBox = new Box<int>(42);
            var strBox = new Box<string>("안녕하세요");
            var studentBox = new Box<Student>(new Student(1, "지우", 95));

            Console.WriteLine($"  {intBox}");
            Console.WriteLine($"  {strBox}");
            Console.WriteLine($"  {studentBox}");
            Console.WriteLine();

            // Pair<TKey, TValue>: 두 개의 타입 매개변수
            var pair1 = new Pair<string, int>("나이", 25);
            var pair2 = new Pair<int, string>(1, "민수");
            Console.WriteLine($"  Pair1: {pair1}");
            Console.WriteLine($"  Pair2: {pair2}");
            Console.WriteLine();

            // SimpleStack<T>: 직접 만든 제네릭 스택
            var stack = new SimpleStack<string>();
            stack.Push("첫 번째");
            stack.Push("두 번째");
            stack.Push("세 번째");

            Console.WriteLine("  [스택에서 꺼내기 — LIFO]");
            while (stack.Count > 0)
            {
                Console.WriteLine($"    Pop: {stack.Pop()}");
            }
            Console.WriteLine();
        }

        static void Lesson5GenericMethod()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 5: 제네릭 메서드 — 타입마다 함수를 새로 쓰지 않기");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // PickFirst<T>
            var numbers = new List<int> { 10, 20, 30 };
            var names = new List<string> { "민수", "지우", "서연" };
            Console.WriteLine($"  숫자 목록 첫 값: {PickFirst(numbers)}");
            Console.WriteLine($"  이름 목록 첫 값: {PickFirst(names)}");
            Console.WriteLine();

            // Max<T>, Min<T> — where T : IComparable<T> 제약
            Console.WriteLine($"  Max(3, 7) = {Max(3, 7)}");
            Console.WriteLine($"  Min(3, 7) = {Min(3, 7)}");
            Console.WriteLine($"  Max(\"apple\", \"zebra\") = {Max("apple", "zebra")}");
            Console.WriteLine();

            // Swap<T>
            int a = 10, b = 20;
            Console.WriteLine($"  Swap 전: a={a}, b={b}");
            Swap(ref a, ref b);
            Console.WriteLine($"  Swap 후: a={a}, b={b}");
            Console.WriteLine();
        }

        static void Lesson6WhereConstraints()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 6: where 제약 조건 — 타입 제한");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // Repository<T> where T : IIdentifiable
            var studentRepo = new Repository<Student>();
            studentRepo.Add(new Student(1, "민수", 82));
            studentRepo.Add(new Student(2, "지우", 95));
            studentRepo.Add(new Student(3, "서연", 68));

            Console.WriteLine("  [학생 저장소]");
            studentRepo.PrintAll();

            var found = studentRepo.FindById(2);
            Console.WriteLine($"  ID=2 검색: {found?.DisplayName ?? "없음"}");
            Console.WriteLine();

            // 같은 Repository를 Product에도 사용
            var productRepo = new Repository<Product>();
            productRepo.Add(new Product(101, "연필", 500));
            productRepo.Add(new Product(102, "지우개", 300));

            Console.WriteLine("  [상품 저장소]");
            productRepo.PrintAll();
            Console.WriteLine();

            // ★ Repository<int>는 불가!
            // int는 IIdentifiable을 구현하지 않으므로 컴파일 에러
            // var intRepo = new Repository<int>();  // 에러!
            Console.WriteLine("  ★ Repository<int>는 컴파일 에러! (int는 IIdentifiable이 아님)");
            Console.WriteLine();
        }

        static void Lesson7PracticalExample()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 7: 실전 — 인터페이스 + 제네릭 조합");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            /*
            ★ 실전에서 가장 많이 보는 패턴:
              - IEnumerable<T>: foreach로 순회 가능
              - IComparable<T>: 비교/정렬 가능
              - IDisposable: 자원 해제 필요
              - IList<T>, IDictionary<TKey, TValue>: 컬렉션
            */

            // .NET의 주요 제네릭 컬렉션들
            Console.WriteLine("  .NET 기본 제공 제네릭 컬렉션:");
            Console.WriteLine("  ┌────────────────────────────────────────────────┐");
            Console.WriteLine("  │ List<T>              동적 배열               │");
            Console.WriteLine("  │ Dictionary<K,V>      키-값 쌍               │");
            Console.WriteLine("  │ HashSet<T>           중복 없는 집합          │");
            Console.WriteLine("  │ Queue<T>             선입선출(FIFO)          │");
            Console.WriteLine("  │ Stack<T>             후입선출(LIFO)          │");
            Console.WriteLine("  │ LinkedList<T>        연결 리스트             │");
            Console.WriteLine("  │ SortedSet<T>         정렬된 집합             │");
            Console.WriteLine("  │ SortedDictionary<K,V>정렬된 딕셔너리        │");
            Console.WriteLine("  └────────────────────────────────────────────────┘");
            Console.WriteLine();

            // Dictionary 사용 예
            var gradebook = new Dictionary<string, List<int>>();
            gradebook["민수"] = new List<int> { 85, 90, 78 };
            gradebook["지우"] = new List<int> { 92, 88, 95 };

            Console.WriteLine("  [성적표 — Dictionary<string, List<int>>]");
            foreach (var entry in gradebook)
            {
                double avg = 0;
                foreach (int score in entry.Value) avg += score;
                avg /= entry.Value.Count;
                Console.WriteLine($"  {entry.Key}: 평균 {avg:F1}점");
            }
            Console.WriteLine();

            // HashSet 사용 예
            var attendees = new HashSet<string>();
            attendees.Add("민수");
            attendees.Add("지우");
            attendees.Add("민수");  // 중복! 무시됨
            Console.WriteLine($"  HashSet 출석: {string.Join(", ", attendees)} (중복 자동 제거)");
            Console.WriteLine();
        }

        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine("  C# 07단계: 인터페이스와 제네릭");
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine();

            Lesson1InterfaceBasics();
            Lesson2MultipleInterfaces();
            Lesson3ExplicitImplementation();
            Lesson4GenericClass();
            Lesson5GenericMethod();
            Lesson6WhereConstraints();
            Lesson7PracticalExample();

            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  ★ 정리");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  1. interface: '할 수 있다'는 약속 (다중 구현 가능)");
            Console.WriteLine("  2. 명시적 구현: 같은 이름 메서드 충돌 해결");
            Console.WriteLine("  3. 제네릭 클래스: Box<T>, Stack<T> — 타입 재사용");
            Console.WriteLine("  4. 제네릭 메서드: Max<T>, Swap<T> — 함수 재사용");
            Console.WriteLine("  5. where 제약: 타입 안전성 보장");
            Console.WriteLine("  6. .NET 컬렉션: List<T>, Dictionary<K,V> 등 제네릭 활용");
            Console.WriteLine();
        }
    }
}
