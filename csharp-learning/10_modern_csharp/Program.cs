/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C# 학습 10단계: 현대 C# 기능
  ─ 패턴 매칭, record, nullable, init, 튜플, 범위/인덱스 ─

  ■ 컴파일: dotnet build
  ■ 실행:   dotnet run

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  [학습 목표]
  1. 패턴 매칭 (switch식, is 패턴, 프로퍼티 패턴)
  2. record 타입의 특성과 활용
  3. nullable 참조 타입 (? 연산자, null 병합)
  4. init 전용 속성과 required 키워드
  5. 튜플(Tuple) 활용
  6. 인덱스(^)와 범위(..) 연산자
  7. using 선언, global using
  8. 원시 문자열 리터럴 (C# 11)

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Lesson10
{
    // ── 데이터 타입들 ──
    record Student(string Name, int Score, int HomeworkCount);

    // record struct: 값 타입 record (C# 10)
    readonly record struct Point(double X, double Y);

    // record with 추가 멤버
    record Employee(string Name, string Department, int Salary)
    {
        // record에 추가 메서드/속성을 넣을 수 있음
        public string Grade => Salary switch
        {
            >= 8000 => "시니어",
            >= 5000 => "중급",
            _ => "주니어"
        };
    }

    // init 전용 속성 예시
    class Config
    {
        public string AppName { get; init; } = "MyApp";
        public int MaxRetries { get; init; } = 3;
        public bool DebugMode { get; init; } = false;

        public override string ToString()
        {
            return $"[{AppName}] retries={MaxRetries}, debug={DebugMode}";
        }
    }

    // 패턴 매칭용 클래스 계층
    abstract record Shape;
    record Circle(double Radius) : Shape;
    record Rect(double Width, double Height) : Shape;
    record Triangle(double Base_, double Height_) : Shape;


    class Program
    {
        // =====================================================================
        // 레슨 1 — 패턴 매칭 (switch식, 프로퍼티 패턴)
        // =====================================================================
        /*
        ★ 패턴 매칭 = "값의 모양(패턴)에 따라 분기하는 기능"
          → if-else 체인보다 읽기 쉽고 강력!

        ★ switch 식 (C# 8+)
        ┌──────────────────────────────────────────────────┐
        │  var result = value switch                       │
        │  {                                               │
        │      >= 90 => "A",     // 관계 패턴             │
        │      >= 80 => "B",                               │
        │      (_, _) => ...,    // 튜플 패턴              │
        │      { Name: "test" } => ..., // 프로퍼티 패턴   │
        │      null => ...,      // null 패턴              │
        │      _ => "F"          // 기본값 (discard)       │
        │  };                                              │
        └──────────────────────────────────────────────────┘

        ★ 비유: 우체국 분류기
          편지 모양(크기, 무게, 주소)에 따라 자동으로 다른 통에 넣는 기계
        */
        static string GetGrade(Student student) =>
            student.Score switch
            {
                >= 90 => "A (우수)",
                >= 80 => "B (양호)",
                >= 70 => "C (보통)",
                >= 60 => "D (노력)",
                _ => "F (복습 필요)"
            };

        // 프로퍼티 패턴
        static string GetScholarship(Student s) => s switch
        {
            { Score: >= 95, HomeworkCount: >= 5 } => "전액 장학금",
            { Score: >= 90, HomeworkCount: >= 3 } => "반액 장학금",
            { Score: >= 85 } => "도서 지원",
            _ => "해당 없음"
        };

        // 타입 패턴 + switch식
        static double CalculateArea(Shape shape) => shape switch
        {
            Circle c => Math.PI * c.Radius * c.Radius,
            Rect r => r.Width * r.Height,
            Triangle t => t.Base_ * t.Height_ / 2.0,
            _ => 0
        };

        static void Lesson1PatternMatching()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 1: 패턴 매칭 — 값의 모양으로 분기");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            var students = new Student[]
            {
                new Student("민수", 92, 4),
                new Student("지우", 96, 5),
                new Student("서연", 65, 1),
                new Student("하린", 87, 3),
            };

            Console.WriteLine("  [성적표 — switch 식]");
            foreach (var s in students)
            {
                Console.WriteLine($"    {s.Name}: {s.Score}점 → {GetGrade(s)}");
            }
            Console.WriteLine();

            Console.WriteLine("  [장학금 — 프로퍼티 패턴]");
            foreach (var s in students)
            {
                Console.WriteLine($"    {s.Name}: {GetScholarship(s)}");
            }
            Console.WriteLine();

            // 타입 패턴으로 도형 넓이 계산
            Shape[] shapes = { new Circle(5), new Rect(4, 6), new Triangle(3, 8) };
            Console.WriteLine("  [도형 넓이 — 타입 패턴]");
            foreach (var shape in shapes)
            {
                Console.WriteLine($"    {shape} → 넓이: {CalculateArea(shape):F2}");
            }
            Console.WriteLine();

            // 튜플 패턴
            Console.WriteLine("  [요일+시간 → 활동 — 튜플 패턴]");
            (string day, int hour)[] schedule =
            {
                ("월", 9), ("월", 15), ("토", 10), ("일", 14),
            };

            foreach (var (day, hour) in schedule)
            {
                string activity = (day, hour) switch
                {
                    ("토" or "일", _) => "주말 휴식",
                    (_, >= 9 and <= 12) => "오전 수업",
                    (_, >= 13 and <= 17) => "오후 활동",
                    _ => "자유 시간"
                };
                Console.WriteLine($"    {day}요일 {hour}시 → {activity}");
            }
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 2 — record 타입
        // =====================================================================
        /*
        ★ record = 데이터 중심 타입 (C# 9+)
          → 값 기반 동등성, ToString, with 식을 자동 제공

        ★ class vs record vs struct
        ┌──────────────┬────────────┬────────────┬──────────────┐
        │              │   class    │   record   │   struct     │
        ├──────────────┼────────────┼────────────┼──────────────┤
        │ 타입         │ 참조 타입  │ 참조 타입  │ 값 타입      │
        │ 동등성       │ 참조 비교  │ 값 비교    │ 값 비교      │
        │ 불변성       │ 수동 설정  │ 기본 불변  │ 수동 설정    │
        │ ToString     │ 타입명만   │ 모든 필드  │ 타입명만     │
        │ with 식      │ ✗ 불가    │ ✓ 가능    │ ✓ 가능      │
        │ 상속         │ ✓ 가능    │ ✓ 가능    │ ✗ 불가      │
        │ 용도         │ 동작 중심  │ 데이터 중심│ 작은 값 묶음 │
        └──────────────┴────────────┴────────────┴──────────────┘
        */
        static void Lesson2Record()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 2: record — 데이터 중심 타입");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // 자동 ToString
            var student = new Student("민수", 92, 4);
            Console.WriteLine("  ToString: " + student);
            Console.WriteLine();

            // 값 기반 동등성
            var s1 = new Student("지우", 95, 5);
            var s2 = new Student("지우", 95, 5);
            Console.WriteLine($"  s1 == s2: {s1 == s2}");  // true! (class였으면 false)
            Console.WriteLine($"  ReferenceEquals: {ReferenceEquals(s1, s2)}");  // false
            Console.WriteLine();

            // with 식: 일부만 바꾼 복사본
            var updated = student with { HomeworkCount = 5 };
            Console.WriteLine($"  원본: {student}");
            Console.WriteLine($"  복사: {updated}");
            Console.WriteLine($"  원본 변경됨? {student.HomeworkCount}");  // 4 (불변!)
            Console.WriteLine();

            // record struct
            var p1 = new Point(3.0, 4.0);
            var p2 = new Point(3.0, 4.0);
            Console.WriteLine($"  Point: {p1}");
            Console.WriteLine($"  p1 == p2: {p1 == p2}");
            Console.WriteLine();

            // record with 추가 멤버
            var emp = new Employee("김철수", "개발팀", 6000);
            Console.WriteLine($"  Employee: {emp}");
            Console.WriteLine($"  등급: {emp.Grade}");
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 3 — Nullable 참조 타입
        // =====================================================================
        /*
        ★ C# 8+: Nullable Reference Types (NRT)
          → null이 될 수 있는 참조에 ? 표시 → 컴파일러가 경고!

        ┌──────────────────────────────────────────────────┐
        │  string name = "민수";    // null 불가          │
        │  string? maybe = null;    // null 가능          │
        │                                                  │
        │  int len1 = name.Length;  // 안전               │
        │  int len2 = maybe.Length; // ★ 컴파일러 경고!  │
        │  int len3 = maybe?.Length ?? 0; // 안전 처리    │
        └──────────────────────────────────────────────────┘

        ★ null 관련 연산자 모음
        ┌──────────┬──────────────────────────────────────┐
        │ ?.       │ null 조건부 접근                     │
        │ ??       │ null 병합 (null이면 대체값)          │
        │ ??=      │ null일 때만 대입                     │
        │ !        │ null 아님 단언 (위험!)               │
        └──────────┴──────────────────────────────────────┘
        */
        static void Lesson3Nullable()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 3: Nullable — null 안전하게 다루기");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // ?. (null 조건부 접근)
            string? name = null;
            int? length = name?.Length;
            Console.WriteLine($"  name?.Length = {length?.ToString() ?? "null"}");

            // ?? (null 병합)
            string display = name ?? "(이름 없음)";
            Console.WriteLine($"  name ?? \"(이름 없음)\" = {display}");

            // ??= (null일 때만 대입)
            name ??= "기본값";
            Console.WriteLine($"  name ??= \"기본값\" → {name}");
            Console.WriteLine();

            // 실전 패턴: 딕셔너리 조회
            var scores = new Dictionary<string, int>
            {
                ["민수"] = 82,
                ["지우"] = 95,
            };

            string[] lookups = { "민수", "없는학생" };
            foreach (string key in lookups)
            {
                // TryGetValue + null 병합 패턴
                int score = scores.TryGetValue(key, out int s) ? s : -1;
                Console.WriteLine($"  {key}: {(score >= 0 ? $"{score}점" : "찾을 수 없음")}");
            }
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 4 — init 전용 속성
        // =====================================================================
        /*
        ★ init = 초기화할 때만 값을 설정할 수 있는 속성 (C# 9+)
          → set은 언제든 바꿀 수 있지만, init은 생성 시에만!

        ★ 비유: 출생증명서
          이름과 생년월일은 발급할 때 적고, 나중에 바꿀 수 없음
        */
        static void Lesson4InitOnly()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 4: init 전용 속성 — 불변 설정");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // 객체 이니셜라이저로 init 속성 설정
            var config = new Config
            {
                AppName = "학교관리",
                MaxRetries = 5,
                DebugMode = true
            };

            Console.WriteLine("  설정: " + config);
            Console.WriteLine();

            // ★ 이후 변경 불가!
            // config.AppName = "다른이름";  // 컴파일 에러!

            // 기본값 사용
            var defaultConfig = new Config();
            Console.WriteLine("  기본값: " + defaultConfig);
            Console.WriteLine();

            Console.WriteLine("  ★ init은 생성 시에만 값 설정 가능");
            Console.WriteLine("  ★ 이후 config.AppName = \"...\" → 컴파일 에러!");
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 5 — 튜플(Tuple)
        // =====================================================================
        /*
        ★ 튜플 = 여러 값을 하나로 묶는 간편 타입

        ┌──────────────────────────────────────────────────┐
        │  (string name, int age) = ("민수", 15);          │
        │  var pair = (Name: "지우", Score: 95);           │
        │                                                  │
        │  // 메서드에서 여러 값 반환                      │
        │  (int min, int max) GetRange(int[] arr) { ... }  │
        └──────────────────────────────────────────────────┘

        ★ 비유: 간이 메모지
          클래스를 만들기엔 너무 간단한 경우 메모지에 적어서 전달
        */
        static (int min, int max, double avg) GetStats(int[] numbers)
        {
            return (numbers.Min(), numbers.Max(), numbers.Average());
        }

        static void Lesson5Tuple()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 5: 튜플 — 여러 값을 가볍게 묶기");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // 기본 튜플
            var person = (Name: "민수", Age: 15, Score: 82);
            Console.WriteLine($"  이름: {person.Name}, 나이: {person.Age}, 점수: {person.Score}");

            // 분해(Deconstruction)
            var (name, age, score) = person;
            Console.WriteLine($"  분해: name={name}, age={age}, score={score}");
            Console.WriteLine();

            // 메서드에서 여러 값 반환
            int[] scores = { 55, 72, 88, 91, 64 };
            var stats = GetStats(scores);
            Console.WriteLine($"  최소: {stats.min}, 최대: {stats.max}, 평균: {stats.avg:F1}");
            Console.WriteLine();

            // _ (discard): 필요 없는 값 무시
            var (_, _, average) = GetStats(scores);
            Console.WriteLine($"  평균만 필요: {average:F1}");
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 6 — 인덱스(^)와 범위(..) 연산자
        // =====================================================================
        /*
        ★ C# 8+: 배열/문자열을 더 편하게 접근

        ┌──────────────────────────────────────────────────┐
        │  int[] arr = { 10, 20, 30, 40, 50 };            │
        │                                                  │
        │  arr[^1]      // 마지막 요소: 50                │
        │  arr[^2]      // 뒤에서 둘째: 40                │
        │  arr[1..3]    // 인덱스 1~2: { 20, 30 }         │
        │  arr[..3]     // 처음~2: { 10, 20, 30 }         │
        │  arr[2..]     // 2~끝: { 30, 40, 50 }           │
        └──────────────────────────────────────────────────┘
        */
        static void Lesson6IndexAndRange()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 6: 인덱스(^)와 범위(..) 연산자");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            int[] numbers = { 10, 20, 30, 40, 50 };

            Console.WriteLine($"  배열: [{string.Join(", ", numbers)}]");
            Console.WriteLine($"  [^1] 마지막: {numbers[^1]}");
            Console.WriteLine($"  [^2] 뒤에서 둘째: {numbers[^2]}");
            Console.WriteLine();

            // 범위 연산자
            int[] slice1 = numbers[1..3];    // 20, 30
            int[] slice2 = numbers[..3];     // 10, 20, 30
            int[] slice3 = numbers[2..];     // 30, 40, 50
            int[] slice4 = numbers[1..^1];   // 20, 30, 40

            Console.WriteLine($"  [1..3]:   [{string.Join(", ", slice1)}]");
            Console.WriteLine($"  [..3]:    [{string.Join(", ", slice2)}]");
            Console.WriteLine($"  [2..]:    [{string.Join(", ", slice3)}]");
            Console.WriteLine($"  [1..^1]:  [{string.Join(", ", slice4)}]");
            Console.WriteLine();

            // 문자열에도 적용
            string greeting = "Hello, World!";
            Console.WriteLine($"  \"{greeting}\"[..5] = \"{greeting[..5]}\"");
            Console.WriteLine($"  \"{greeting}\"[7..] = \"{greeting[7..]}\"");
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 7 — 기타 현대 C# 문법
        // =====================================================================
        static void Lesson7MiscModernFeatures()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 7: 기타 현대 C# 편의 기능");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // ── 타겟 타입 new (C# 9) ──
            List<string> names = new() { "민수", "지우", "서연" };
            Dictionary<string, int> scores = new()
            {
                ["민수"] = 82,
                ["지우"] = 95,
            };
            Console.WriteLine("  타겟 타입 new: List<string> names = new() { ... };");
            Console.WriteLine();

            // ── 문자열 보간 개선 (C# 10) ──
            const string label = "점수";
            Console.WriteLine($"  const 보간: {label} 계산 완료");
            Console.WriteLine();

            // ── 파일 범위 네임스페이스 (C# 10) ──
            Console.WriteLine("  ★ C# 10+: namespace MyApp; (세미콜론으로 간결하게)");
            Console.WriteLine("  ★ 이전: namespace MyApp { class ... { } }");
            Console.WriteLine();

            // ── global using (C# 10) ──
            Console.WriteLine("  ★ C# 10+: global using System; (프로젝트 전체 적용)");
            Console.WriteLine("  ★ GlobalUsings.cs 파일에 모아두면 편리");
            Console.WriteLine();

            // ── 원시 문자열 리터럴 (C# 11) ──
            Console.WriteLine("  ★ C# 11+: 원시 문자열 (큰따옴표 3개)");
            Console.WriteLine("    var json = \"\"\"");
            Console.WriteLine("    {");
            Console.WriteLine("        \"name\": \"민수\",");
            Console.WriteLine("        \"score\": 82");
            Console.WriteLine("    }");
            Console.WriteLine("    \"\"\";");
            Console.WriteLine();

            // ── 리스트 패턴 (C# 11) ──
            Console.WriteLine("  ★ C# 11+: 리스트 패턴");
            Console.WriteLine("    int[] arr = { 1, 2, 3 };");
            Console.WriteLine("    if (arr is [1, 2, 3]) // 정확히 매칭");
            Console.WriteLine("    if (arr is [1, .., 3]) // 처음 1, 마지막 3");
            Console.WriteLine();

            // ── 버전별 주요 기능 요약 ──
            Console.WriteLine("  ┌──────────────────────────────────────────────────┐");
            Console.WriteLine("  │ C# 버전별 핵심 기능 요약                        │");
            Console.WriteLine("  ├──────┬───────────────────────────────────────────┤");
            Console.WriteLine("  │ C# 7 │ 패턴 매칭 기초, 튜플, out var           │");
            Console.WriteLine("  │ C# 8 │ nullable 참조, switch식, 범위/인덱스    │");
            Console.WriteLine("  │ C# 9 │ record, init, 타겟타입 new              │");
            Console.WriteLine("  │ C#10 │ global using, 파일범위 namespace         │");
            Console.WriteLine("  │ C#11 │ 원시 문자열, 리스트 패턴, required       │");
            Console.WriteLine("  │ C#12 │ primary constructor, 컬렉션 리터럴       │");
            Console.WriteLine("  └──────┴───────────────────────────────────────────┘");
            Console.WriteLine();
        }


        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine("  C# 10단계: 현대 C# 기능");
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine();

            Lesson1PatternMatching();
            Lesson2Record();
            Lesson3Nullable();
            Lesson4InitOnly();
            Lesson5Tuple();
            Lesson6IndexAndRange();
            Lesson7MiscModernFeatures();

            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  ★ 정리");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  1. 패턴 매칭: switch식, 프로퍼티/타입/튜플 패턴");
            Console.WriteLine("  2. record: 값 기반 동등성, with식, 불변 데이터");
            Console.WriteLine("  3. nullable: ?. ?? ??= 으로 null 안전 처리");
            Console.WriteLine("  4. init: 생성 시에만 설정 가능한 속성");
            Console.WriteLine("  5. 튜플: 여러 값을 가볍게 묶어 전달");
            Console.WriteLine("  6. ^/.. : 인덱스와 범위 연산자");
            Console.WriteLine("  7. 최신 문법: global using, 원시 문자열 등");
            Console.WriteLine();
        }
    }
}
