/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C# 학습 09단계: LINQ와 람다
  ─ 람다식, 메서드 구문, 쿼리 구문, Join, GroupBy, Aggregate ─

  ■ 컴파일: dotnet build
  ■ 실행:   dotnet run

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  [학습 목표]
  1. 람다식(Lambda Expression)의 개념과 문법을 이해한다
  2. LINQ 메서드 구문 (Where, Select, OrderBy 등)을 사용한다
  3. LINQ 쿼리 구문 (from, where, select)을 사용한다
  4. 집계 함수 (Count, Sum, Average, Min, Max)를 활용한다
  5. GroupBy로 데이터를 그룹화한다
  6. Join으로 두 컬렉션을 연결한다
  7. 지연 평가(Lazy Evaluation)의 개념을 이해한다

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Lesson09
{
    // ── 데이터 모델 ──
    record Student(string Name, int Score, string Class);
    record Teacher(string Name, string Class);
    record Product(string Name, string Category, int Price);

    class Program
    {
        // =====================================================================
        // 레슨 1 — 람다식 기본
        // =====================================================================
        /*
        ★ 람다식 = 이름 없는 작은 함수를 짧게 적는 방법

        ┌──────────────────────────────────────────────────────┐
        │  (매개변수) => 표현식                                │
        │  (매개변수) => { 문장들; return 값; }                │
        │                                                      │
        │  x => x * 2           // int를 받아 2배 반환         │
        │  (a, b) => a + b      // 두 수를 받아 합 반환        │
        │  () => "Hello"        // 매개변수 없이 값 반환       │
        │  x => { ... }         // 여러 줄                     │
        └──────────────────────────────────────────────────────┘

        ★ 비유: 메모지에 적은 계산 규칙
          "이 숫자를 받으면 2배로 만들어" → x => x * 2
          함수 이름을 따로 짓지 않아도 규칙만 전달!
        */
        static void Lesson1Lambda()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 1: 람다식 — 짧게 적는 작은 규칙");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // ── 기본 람다 ──
            Func<int, int> doubleIt = x => x * 2;
            Func<int, int, int> add = (a, b) => a + b;
            Func<string, int> getLength = s => s.Length;
            Action<string> greet = name => Console.WriteLine($"  안녕, {name}!");

            Console.WriteLine($"  doubleIt(5)     = {doubleIt(5)}");
            Console.WriteLine($"  add(3, 7)       = {add(3, 7)}");
            Console.WriteLine($"  getLength(\"안녕\") = {getLength("안녕")}");
            greet("민수");
            Console.WriteLine();

            // ── 여러 줄 람다 ──
            Func<int, string> classify = score =>
            {
                if (score >= 90) return "우수";
                if (score >= 70) return "통과";
                return "복습 필요";
            };

            int[] scores = { 95, 72, 58, 88 };
            foreach (int s in scores)
            {
                Console.WriteLine($"  {s}점 → {classify(s)}");
            }
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 2 — LINQ 메서드 구문
        // =====================================================================
        /*
        ★ LINQ = Language INtegrated Query (언어 통합 질의)
          → 컬렉션 데이터를 SQL처럼 고르고, 바꾸고, 정렬하는 기능

        ★ 주요 메서드
        ┌─────────────────────┬──────────────────────────────────┐
        │ Where(조건)         │ 조건에 맞는 것만 골라냄          │
        │ Select(변환)        │ 각 요소를 변환                   │
        │ OrderBy(키)         │ 오름차순 정렬                    │
        │ OrderByDescending   │ 내림차순 정렬                    │
        │ ThenBy(키)          │ 2차 정렬                         │
        │ First() / Last()    │ 첫 번째 / 마지막 요소           │
        │ FirstOrDefault()    │ 없으면 기본값 반환               │
        │ Take(n) / Skip(n)   │ 앞에서 n개 / n개 건너뛰기       │
        │ Distinct()          │ 중복 제거                        │
        │ Any(조건)           │ 하나라도 만족하면 true           │
        │ All(조건)           │ 모두 만족하면 true               │
        │ Count(조건)         │ 조건 만족 개수                   │
        │ ToList() / ToArray()│ 결과를 List/Array로 확정         │
        └─────────────────────┴──────────────────────────────────┘

        ★ 비유: 카드 뭉치 정리
          1. 빨간 카드만 골라냄 (Where)
          2. 카드에 적힌 숫자를 2배로 바꿈 (Select)
          3. 숫자 순으로 정렬 (OrderBy)
          → 이 과정을 줄줄이 이어서 적는 것이 LINQ!
        */
        static void Lesson2MethodSyntax()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 2: LINQ 메서드 구문 — 파이프라인 연결");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            var students = new List<Student>
            {
                new Student("민수", 82, "1반"),
                new Student("지우", 95, "1반"),
                new Student("서연", 68, "2반"),
                new Student("하린", 91, "2반"),
                new Student("도윤", 55, "1반"),
                new Student("수아", 78, "2반"),
            };

            // ── Where + OrderBy + Select 체이닝 ──
            var topStudents = students
                .Where(s => s.Score >= 70)          // 70점 이상만
                .OrderByDescending(s => s.Score)    // 점수 높은 순
                .Select(s => $"{s.Name}({s.Score}점)");  // 표시 형식 변환

            Console.WriteLine("  [70점 이상, 높은 순]");
            foreach (string text in topStudents)
            {
                Console.WriteLine($"    {text}");
            }
            Console.WriteLine();

            // ── First / Last / FirstOrDefault ──
            Student top = students.OrderByDescending(s => s.Score).First();
            Student? maybe = students.FirstOrDefault(s => s.Name == "없는사람");
            Console.WriteLine($"  최고 점수: {top.Name} ({top.Score}점)");
            Console.WriteLine($"  '없는사람' 찾기: {maybe?.Name ?? "null"}");
            Console.WriteLine();

            // ── Take / Skip (페이징) ──
            var page1 = students.OrderBy(s => s.Name).Take(3);
            var page2 = students.OrderBy(s => s.Name).Skip(3).Take(3);
            Console.WriteLine("  [이름순 1페이지] " + string.Join(", ", page1.Select(s => s.Name)));
            Console.WriteLine("  [이름순 2페이지] " + string.Join(", ", page2.Select(s => s.Name)));
            Console.WriteLine();

            // ── Any / All ──
            bool anyFail = students.Any(s => s.Score < 60);
            bool allPass = students.All(s => s.Score >= 60);
            Console.WriteLine($"  60점 미만 존재? {anyFail}");
            Console.WriteLine($"  전원 60점 이상? {allPass}");
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 3 — LINQ 쿼리 구문
        // =====================================================================
        /*
        ★ 쿼리 구문: SQL과 비슷한 형태

        ┌──────────────────────────────────────────────┐
        │  var result = from s in students             │
        │               where s.Score >= 80            │
        │               orderby s.Score descending     │
        │               select s.Name;                 │
        └──────────────────────────────────────────────┘

        ★ 메서드 구문 vs 쿼리 구문
          - 기능은 동일! 취향 차이
          - 복잡한 Join/GroupBy는 쿼리 구문이 읽기 쉬울 수 있음
          - 대부분의 실무에서는 메서드 구문을 더 많이 사용
        */
        static void Lesson3QuerySyntax()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 3: LINQ 쿼리 구문 — SQL 느낌으로");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            var students = new List<Student>
            {
                new Student("민수", 82, "1반"),
                new Student("지우", 95, "1반"),
                new Student("서연", 68, "2반"),
                new Student("하린", 91, "2반"),
                new Student("도윤", 55, "1반"),
            };

            // ── 쿼리 구문 ──
            var honor = from s in students
                        where s.Score >= 80
                        orderby s.Score descending
                        select new { s.Name, s.Score, Label = "우등" };

            Console.WriteLine("  [쿼리 구문: 80점 이상 우등생]");
            foreach (var h in honor)
            {
                Console.WriteLine($"    {h.Name}: {h.Score}점 ({h.Label})");
            }
            Console.WriteLine();

            // ── 같은 쿼리를 메서드 구문으로 ──
            var honorMethod = students
                .Where(s => s.Score >= 80)
                .OrderByDescending(s => s.Score)
                .Select(s => new { s.Name, s.Score, Label = "우등" });

            Console.WriteLine("  [메서드 구문: 동일한 결과]");
            foreach (var h in honorMethod)
            {
                Console.WriteLine($"    {h.Name}: {h.Score}점 ({h.Label})");
            }
            Console.WriteLine();

            // ── let 절: 중간 변수 ──
            var withGrade = from s in students
                            let grade = s.Score >= 90 ? "A"
                                      : s.Score >= 80 ? "B"
                                      : s.Score >= 70 ? "C" : "F"
                            select new { s.Name, s.Score, Grade = grade };

            Console.WriteLine("  [let 절: 중간 계산]");
            foreach (var item in withGrade)
            {
                Console.WriteLine($"    {item.Name}: {item.Score}점 → {item.Grade}");
            }
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 4 — 집계 함수
        // =====================================================================
        static void Lesson4Aggregation()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 4: 집계 함수 — 요약 계산");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            var students = new List<Student>
            {
                new Student("민수", 82, "1반"),
                new Student("지우", 95, "1반"),
                new Student("서연", 68, "2반"),
                new Student("하린", 91, "2반"),
                new Student("도윤", 55, "1반"),
            };

            // ── 기본 집계 ──
            int count = students.Count;
            int passCount = students.Count(s => s.Score >= 70);
            int sum = students.Sum(s => s.Score);
            double avg = students.Average(s => s.Score);
            int max = students.Max(s => s.Score);
            int min = students.Min(s => s.Score);

            Console.WriteLine("  ┌──────────────────────────────┐");
            Console.WriteLine("  │      성적 통계 요약          │");
            Console.WriteLine("  ├──────────────────────────────┤");
            Console.WriteLine($"  │ 전체 인원:    {count,5}명      │");
            Console.WriteLine($"  │ 통과 인원:    {passCount,5}명      │");
            Console.WriteLine($"  │ 점수 합계:    {sum,5}점      │");
            Console.WriteLine($"  │ 평균 점수:    {avg,8:F1}점   │");
            Console.WriteLine($"  │ 최고 점수:    {max,5}점      │");
            Console.WriteLine($"  │ 최저 점수:    {min,5}점      │");
            Console.WriteLine("  └──────────────────────────────┘");
            Console.WriteLine();

            // ── Aggregate: 커스텀 누적 계산 ──
            /*
            ★ Aggregate = 직접 누적 규칙을 정하는 집계
              예: 모든 이름을 콤마로 이어 붙이기
            */
            string allNames = students
                .Select(s => s.Name)
                .Aggregate((current, next) => current + ", " + next);
            Console.WriteLine("  Aggregate로 이름 이어 붙이기: " + allNames);

            // 곱 계산
            int[] numbers = { 2, 3, 4 };
            int product = numbers.Aggregate(1, (acc, n) => acc * n);
            Console.WriteLine($"  Aggregate 곱: 2 * 3 * 4 = {product}");
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 5 — GroupBy
        // =====================================================================
        /*
        ★ GroupBy = 데이터를 특정 기준으로 묶기
          → SQL의 GROUP BY와 같은 역할

          비유: 학생들을 반별로 줄 세우기
            1반: 민수, 지우, 도윤
            2반: 서연, 하린, 수아
        */
        static void Lesson5GroupBy()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 5: GroupBy — 데이터 그룹화");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            var students = new List<Student>
            {
                new Student("민수", 82, "1반"),
                new Student("지우", 95, "1반"),
                new Student("서연", 68, "2반"),
                new Student("하린", 91, "2반"),
                new Student("도윤", 55, "1반"),
                new Student("수아", 78, "2반"),
            };

            // ── 반별 그룹화 ──
            var groups = students.GroupBy(s => s.Class);

            foreach (var group in groups)
            {
                double avg = group.Average(s => s.Score);
                Console.WriteLine($"  [{group.Key}] 학생 수: {group.Count()}, 평균: {avg:F1}점");
                foreach (var s in group.OrderByDescending(s => s.Score))
                {
                    Console.WriteLine($"    - {s.Name}: {s.Score}점");
                }
            }
            Console.WriteLine();

            // ── 점수 구간별 그룹화 ──
            var gradeGroups = students.GroupBy(s =>
                s.Score >= 90 ? "A등급" :
                s.Score >= 80 ? "B등급" :
                s.Score >= 70 ? "C등급" : "F등급"
            );

            Console.WriteLine("  [점수 구간별 분류]");
            foreach (var group in gradeGroups.OrderBy(g => g.Key))
            {
                Console.WriteLine($"    {group.Key}: {string.Join(", ", group.Select(s => s.Name))}");
            }
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 6 — Join
        // =====================================================================
        /*
        ★ Join = 두 컬렉션을 특정 키로 연결
          → SQL의 JOIN과 같은 역할

        ┌────────────────────────────────────────────────┐
        │  students.Join(                                │
        │      teachers,               // 합칠 대상     │
        │      s => s.Class,           // 학생 키       │
        │      t => t.Class,           // 교사 키       │
        │      (s, t) => new { ... }   // 합친 결과     │
        │  )                                             │
        └────────────────────────────────────────────────┘
        */
        static void Lesson6Join()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 6: Join — 두 컬렉션 연결");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            var students = new List<Student>
            {
                new Student("민수", 82, "1반"),
                new Student("지우", 95, "1반"),
                new Student("서연", 68, "2반"),
                new Student("하린", 91, "2반"),
            };

            var teachers = new List<Teacher>
            {
                new Teacher("김선생", "1반"),
                new Teacher("이선생", "2반"),
            };

            // ── 메서드 구문 Join ──
            var joined = students.Join(
                teachers,
                s => s.Class,
                t => t.Class,
                (s, t) => new { s.Name, s.Score, Teacher = t.Name, s.Class }
            );

            Console.WriteLine("  [학생-담임 매칭]");
            foreach (var item in joined)
            {
                Console.WriteLine($"    {item.Class} {item.Teacher} → {item.Name} ({item.Score}점)");
            }
            Console.WriteLine();

            // ── 쿼리 구문 Join ──
            var joinedQuery = from s in students
                              join t in teachers on s.Class equals t.Class
                              select new { s.Name, s.Score, Teacher = t.Name };

            Console.WriteLine("  [쿼리 구문으로 같은 결과]");
            foreach (var item in joinedQuery)
            {
                Console.WriteLine($"    {item.Teacher} → {item.Name} ({item.Score}점)");
            }
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 7 — 지연 평가(Lazy Evaluation)
        // =====================================================================
        /*
        ★ LINQ는 기본적으로 "지연 평가"
          → ToList(), ToArray(), foreach 등으로 실제 사용할 때까지 실행 안 함!

        ┌──────────────────────────────────────────────────┐
        │  var query = students.Where(s => s.Score >= 80); │
        │  // ↑ 아직 실행 안 됨! 질의 정의만 해 둠       │
        │                                                  │
        │  foreach (var s in query) { ... }                │
        │  // ↑ 이 시점에 실제로 필터링 실행!             │
        │                                                  │
        │  var list = query.ToList();                      │
        │  // ↑ ToList()도 즉시 실행을 유발               │
        └──────────────────────────────────────────────────┘

        ★ 왜 지연 평가?
          - 필요한 만큼만 처리 → 성능 향상
          - 무한 시퀀스도 가능 (필요한 만큼만 꺼냄)

        ★ 주의: 소스 데이터가 변하면 결과도 달라질 수 있음!
        */
        static void Lesson7LazyEvaluation()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 7: 지연 평가 — 쓸 때까지 기다린다");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            var numbers = new List<int> { 1, 2, 3, 4, 5 };

            // ★ 쿼리 정의 (아직 실행 안 됨!)
            var evens = numbers.Where(n =>
            {
                Console.WriteLine($"    필터 검사: {n}");
                return n % 2 == 0;
            });

            Console.WriteLine("  [쿼리 정의 직후 — 아직 출력 없음!]");
            Console.WriteLine();

            Console.WriteLine("  [foreach로 실행 시작]");
            foreach (int n in evens)
            {
                Console.WriteLine($"    → 결과: {n}");
            }
            Console.WriteLine();

            // ★ 소스 변경 후 다시 실행하면 결과가 달라짐!
            numbers.Add(6);
            numbers.Add(7);
            Console.WriteLine("  [리스트에 6, 7 추가 후 다시 실행]");
            var evenList = evens.ToList();
            Console.WriteLine("  짝수 결과: " + string.Join(", ", evenList));
            Console.WriteLine();

            Console.WriteLine("  ★ 주의: 지연 평가 쿼리는 실행할 때마다 소스를 다시 읽음!");
            Console.WriteLine("  ★ 결과를 고정하고 싶으면 .ToList()나 .ToArray()를 사용");
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 8 — 실전 종합 예제
        // =====================================================================
        static void Lesson8PracticalExample()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 8: 실전 — 상품 분석 보고서");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            var products = new List<Product>
            {
                new Product("연필", "문구", 500),
                new Product("지우개", "문구", 300),
                new Product("공책", "문구", 1500),
                new Product("우유", "음료", 1200),
                new Product("주스", "음료", 1800),
                new Product("물", "음료", 800),
                new Product("빵", "간식", 2000),
                new Product("과자", "간식", 1500),
                new Product("사탕", "간식", 500),
            };

            // 카테고리별 통계
            var categoryStats = products
                .GroupBy(p => p.Category)
                .Select(g => new
                {
                    Category = g.Key,
                    Count = g.Count(),
                    TotalPrice = g.Sum(p => p.Price),
                    AvgPrice = g.Average(p => p.Price),
                    MostExpensive = g.OrderByDescending(p => p.Price).First().Name,
                })
                .OrderByDescending(c => c.TotalPrice);

            Console.WriteLine("  ┌──────────────────────────────────────────────────┐");
            Console.WriteLine("  │           카테고리별 상품 분석 보고서            │");
            Console.WriteLine("  ├─────────┬──────┬──────────┬──────────┬──────────┤");
            Console.WriteLine("  │ 카테고리│ 수량 │ 총 가격  │ 평균     │ 최고가   │");
            Console.WriteLine("  ├─────────┼──────┼──────────┼──────────┼──────────┤");

            foreach (var stat in categoryStats)
            {
                Console.WriteLine(
                    $"  │ {stat.Category,-5}   │ {stat.Count,4} │ {stat.TotalPrice,7}원 │ {stat.AvgPrice,7:F0}원 │ {stat.MostExpensive,-7}  │"
                );
            }
            Console.WriteLine("  └─────────┴──────┴──────────┴──────────┴──────────┘");
            Console.WriteLine();

            // 1000원 이하 저가 상품
            var budget = products.Where(p => p.Price <= 1000)
                                 .OrderBy(p => p.Price);
            Console.WriteLine("  [1000원 이하 상품]");
            foreach (var p in budget)
            {
                Console.WriteLine($"    {p.Name}: {p.Price}원 ({p.Category})");
            }
            Console.WriteLine();

            // 전체 통계
            Console.WriteLine($"  전체 상품 수: {products.Count}");
            Console.WriteLine($"  전체 평균 가격: {products.Average(p => p.Price):F0}원");
            Console.WriteLine($"  카테고리 수: {products.Select(p => p.Category).Distinct().Count()}");
            Console.WriteLine();
        }


        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine("  C# 09단계: LINQ와 람다");
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine();

            Lesson1Lambda();
            Lesson2MethodSyntax();
            Lesson3QuerySyntax();
            Lesson4Aggregation();
            Lesson5GroupBy();
            Lesson6Join();
            Lesson7LazyEvaluation();
            Lesson8PracticalExample();

            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  ★ 정리");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  1. 람다식: x => x * 2 (이름 없는 함수)");
            Console.WriteLine("  2. 메서드 구문: .Where().Select().OrderBy() 체이닝");
            Console.WriteLine("  3. 쿼리 구문: from s in list where ... select ...");
            Console.WriteLine("  4. 집계: Count, Sum, Average, Min, Max, Aggregate");
            Console.WriteLine("  5. GroupBy: 데이터 그룹화 + 그룹별 통계");
            Console.WriteLine("  6. Join: 두 컬렉션을 키로 연결");
            Console.WriteLine("  7. 지연 평가: 실행 시점까지 계산을 미룸");
            Console.WriteLine();
        }
    }
}
