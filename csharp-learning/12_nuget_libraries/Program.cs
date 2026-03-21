/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C# 학습 12단계: NuGet과 라이브러리
  ─ NuGet 패키지 관리, System.Text.Json 심화, 라이브러리 활용 패턴 ─

  ■ 컴파일: dotnet build
  ■ 실행:   dotnet run

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  [학습 목표]
  1. NuGet의 개념과 역할을 이해한다
  2. dotnet CLI로 패키지를 추가/제거/관리한다
  3. .csproj 파일의 패키지 참조 구조를 안다
  4. System.Text.Json을 심도 있게 활용한다
  5. 라이브러리를 사용하는 일반적인 패턴을 익힌다
  6. 인기 NuGet 패키지들의 용도를 안다
  7. 버전 관리와 종속성 충돌을 이해한다

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Lesson12
{
    // =====================================================================
    // 레슨 1 — NuGet이란?
    // =====================================================================
    /*
    ★ NuGet = .NET의 공식 패키지 관리자
      → 다른 사람이 만든 검증된 코드를 가져다 쓰는 시스템

    ★ 비유: 레고 부품 창고
      레고 바퀴를 매번 직접 깎지 않고,
      표준 부품 상자에서 꺼내 쓰는 것!
      → NuGet = 레고 부품 온라인 창고 (nuget.org)

    ★ NuGet 패키지 구성
    ┌──────────────────────────────────────────────────┐
    │  패키지 (.nupkg)                                 │
    │  ├── DLL 파일 (컴파일된 코드)                   │
    │  ├── .nuspec (메타데이터: 이름, 버전, 작성자)   │
    │  ├── 문서/라이선스                               │
    │  └── 의존성 정보                                 │
    └──────────────────────────────────────────────────┘

    ★ 주요 CLI 명령어
    ┌──────────────────────────────────────────────────────────┐
    │ dotnet add package Newtonsoft.Json     패키지 추가      │
    │ dotnet add package Serilog --version 3.0.0  버전 지정  │
    │ dotnet remove package Newtonsoft.Json  패키지 제거      │
    │ dotnet restore                        종속성 복원       │
    │ dotnet list package                   설치 목록 확인    │
    │ dotnet list package --outdated        업데이트 확인     │
    └──────────────────────────────────────────────────────────┘
    */


    // =====================================================================
    // JSON 직렬화용 모델 클래스들
    // =====================================================================

    class StudentRecord
    {
        public string Name { get; set; } = "";
        public int Score { get; set; }
        public string Grade { get; set; } = "";

        [JsonIgnore]  // ★ 이 속성은 JSON에 포함하지 않음
        public bool NeedsReview => Score < 70;
    }

    class ClassReport
    {
        public string ClassName { get; set; } = "";
        public DateTime ReportDate { get; set; }
        public List<StudentRecord> Students { get; set; } = new();
        public Statistics Stats { get; set; } = new();
    }

    class Statistics
    {
        public int TotalCount { get; set; }
        public double Average { get; set; }
        public int MaxScore { get; set; }
        public int MinScore { get; set; }
        public int PassCount { get; set; }
    }

    // Enum도 JSON으로!
    enum Priority
    {
        Low,
        Medium,
        High,
        Critical
    }

    class Task_
    {
        public string Title { get; set; } = "";

        [JsonConverter(typeof(JsonStringEnumConverter))]  // ★ enum을 문자열로 직렬화
        public Priority Priority { get; set; }

        public bool IsComplete { get; set; }
    }


    class Program
    {
        private static readonly string DataFolder = Path.Combine(
            AppContext.BaseDirectory, "lesson12_data"
        );

        // ─────────────────────────────────────────────
        // 레슨 1: NuGet 개념과 명령어
        // ─────────────────────────────────────────────
        static void Lesson1NuGetBasics()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 1: NuGet — 패키지 관리의 기초");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            Console.WriteLine("  ★ NuGet 패키지를 추가하면 .csproj에 기록됨:");
            Console.WriteLine();
            Console.WriteLine("  <ItemGroup>");
            Console.WriteLine("    <PackageReference Include=\"Newtonsoft.Json\" Version=\"13.0.3\" />");
            Console.WriteLine("    <PackageReference Include=\"Serilog\" Version=\"3.1.1\" />");
            Console.WriteLine("  </ItemGroup>");
            Console.WriteLine();

            Console.WriteLine("  ★ 패키지 선택 기준:");
            Console.WriteLine("  ┌──────────────────────────────────────────────────┐");
            Console.WriteLine("  │ 1. 다운로드 수: 많을수록 검증된 패키지          │");
            Console.WriteLine("  │ 2. 최근 업데이트: 관리가 활발한지 확인          │");
            Console.WriteLine("  │ 3. 라이선스: MIT, Apache 2.0 등 확인            │");
            Console.WriteLine("  │ 4. 의존성: 다른 패키지를 많이 끌어오는지 확인   │");
            Console.WriteLine("  │ 5. .NET 버전 지원: 내 프로젝트와 호환되는지     │");
            Console.WriteLine("  └──────────────────────────────────────────────────┘");
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 2: System.Text.Json 기초
        // ─────────────────────────────────────────────
        static void Lesson2JsonBasics()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 2: System.Text.Json — 기본 직렬화");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            /*
            ★ System.Text.Json vs Newtonsoft.Json
            ┌──────────────────┬──────────────────┬──────────────────┐
            │                  │ System.Text.Json  │ Newtonsoft.Json  │
            ├──────────────────┼──────────────────┼──────────────────┤
            │ 성능             │ ★ 빠름          │ 보통             │
            │ 기본 포함        │ ✓ .NET 내장     │ ✗ NuGet 필요    │
            │ 기능 풍부함      │ 보통             │ ★ 매우 풍부     │
            │ 유연성           │ 보통             │ ★ 높음          │
            │ 권장 상황        │ 새 프로젝트      │ 복잡한 JSON      │
            └──────────────────┴──────────────────┴──────────────────┘
            */

            var students = new List<StudentRecord>
            {
                new StudentRecord { Name = "민수", Score = 82, Grade = "B" },
                new StudentRecord { Name = "지우", Score = 95, Grade = "A" },
                new StudentRecord { Name = "서연", Score = 68, Grade = "D" },
            };

            // 기본 직렬화
            string json1 = JsonSerializer.Serialize(students);
            Console.WriteLine("  [기본 직렬화]");
            Console.WriteLine("  " + json1);
            Console.WriteLine();

            // 예쁘게 출력
            var prettyOptions = new JsonSerializerOptions
            {
                WriteIndented = true,
                Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
            };

            string json2 = JsonSerializer.Serialize(students, prettyOptions);
            Console.WriteLine("  [예쁘게 출력 (WriteIndented)]");
            Console.WriteLine("  " + json2.Replace("\n", "\n  "));
            Console.WriteLine();

            // 역직렬화
            var parsed = JsonSerializer.Deserialize<List<StudentRecord>>(json1);
            Console.WriteLine("  [역직렬화 결과]");
            if (parsed != null)
            {
                foreach (var s in parsed)
                {
                    Console.WriteLine($"    {s.Name}: {s.Score}점 ({s.Grade}) 복습필요={s.NeedsReview}");
                }
            }
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 3: JSON 고급 옵션
        // ─────────────────────────────────────────────
        static void Lesson3JsonAdvanced()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 3: JSON 고급 — 옵션과 커스터마이즈");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // ── 속성 이름 정책 (camelCase) ──
            var camelOptions = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                WriteIndented = true,
                Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
            };

            var student = new StudentRecord { Name = "민수", Score = 82, Grade = "B" };
            string camelJson = JsonSerializer.Serialize(student, camelOptions);
            Console.WriteLine("  [CamelCase 이름 정책]");
            Console.WriteLine("  " + camelJson.Replace("\n", "\n  "));
            Console.WriteLine("  → Name → name, Score → score");
            Console.WriteLine();

            // ── 대소문자 무시 읽기 ──
            string webJson = "{\"name\":\"지우\",\"score\":95,\"grade\":\"A\"}";
            var readOptions = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true  // ★ 대소문자 무시
            };
            var fromWeb = JsonSerializer.Deserialize<StudentRecord>(webJson, readOptions);
            Console.WriteLine($"  [대소문자 무시 읽기] name → Name: {fromWeb?.Name}");
            Console.WriteLine();

            // ── Enum을 문자열로 ──
            var tasks = new List<Task_>
            {
                new Task_ { Title = "버그 수정", Priority = Priority.Critical, IsComplete = false },
                new Task_ { Title = "문서 작성", Priority = Priority.Low, IsComplete = true },
            };

            var enumOptions = new JsonSerializerOptions
            {
                WriteIndented = true,
                Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
            };
            string taskJson = JsonSerializer.Serialize(tasks, enumOptions);
            Console.WriteLine("  [Enum → 문자열 (JsonStringEnumConverter)]");
            Console.WriteLine("  " + taskJson.Replace("\n", "\n  "));
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 4: 복합 JSON 처리
        // ─────────────────────────────────────────────
        static void Lesson4ComplexJson()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 4: 복합 JSON — 중첩 객체 처리");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            var students = new List<StudentRecord>
            {
                new StudentRecord { Name = "민수", Score = 82, Grade = "B" },
                new StudentRecord { Name = "지우", Score = 95, Grade = "A" },
                new StudentRecord { Name = "서연", Score = 68, Grade = "D" },
                new StudentRecord { Name = "하린", Score = 91, Grade = "A" },
            };

            // 복합 객체 생성
            var report = new ClassReport
            {
                ClassName = "1반",
                ReportDate = new DateTime(2024, 3, 15),
                Students = students,
                Stats = new Statistics
                {
                    TotalCount = students.Count,
                    Average = students.Average(s => s.Score),
                    MaxScore = students.Max(s => s.Score),
                    MinScore = students.Min(s => s.Score),
                    PassCount = students.Count(s => s.Score >= 70),
                }
            };

            var options = new JsonSerializerOptions
            {
                WriteIndented = true,
                Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
            };

            string json = JsonSerializer.Serialize(report, options);

            // 파일로 저장
            Directory.CreateDirectory(DataFolder);
            string filePath = Path.Combine(DataFolder, "class_report.json");
            File.WriteAllText(filePath, json, Encoding.UTF8);

            Console.WriteLine("  [복합 객체 → JSON 파일]");
            Console.WriteLine("  저장 위치: " + filePath);
            Console.WriteLine();

            // 파일에서 다시 읽기
            string readJson = File.ReadAllText(filePath, Encoding.UTF8);
            var loaded = JsonSerializer.Deserialize<ClassReport>(readJson, options);
            if (loaded != null)
            {
                Console.WriteLine($"  반: {loaded.ClassName}");
                Console.WriteLine($"  날짜: {loaded.ReportDate:yyyy-MM-dd}");
                Console.WriteLine($"  학생 수: {loaded.Stats.TotalCount}");
                Console.WriteLine($"  평균: {loaded.Stats.Average:F1}점");
                Console.WriteLine($"  통과: {loaded.Stats.PassCount}명");
                Console.WriteLine();
            }
        }

        // ─────────────────────────────────────────────
        // 레슨 5: 동적 JSON (JsonDocument / JsonElement)
        // ─────────────────────────────────────────────
        static void Lesson5DynamicJson()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 5: 동적 JSON — 클래스 없이 읽기");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            /*
            ★ 클래스를 미리 정의할 수 없는 경우
              - 외부 API 응답이 자주 바뀔 때
              - JSON 구조를 미리 모를 때
              → JsonDocument / JsonElement 사용!
            */

            string jsonString = @"{
                ""school"": ""중앙초등학교"",
                ""year"": 2024,
                ""classes"": [
                    { ""name"": ""1반"", ""count"": 25 },
                    { ""name"": ""2반"", ""count"": 28 }
                ]
            }";

            using JsonDocument doc = JsonDocument.Parse(jsonString);
            JsonElement root = doc.RootElement;

            // 속성 접근
            string school = root.GetProperty("school").GetString() ?? "";
            int year = root.GetProperty("year").GetInt32();
            Console.WriteLine($"  학교: {school}, 연도: {year}");

            // 배열 순회
            Console.WriteLine("  [반 목록]");
            foreach (JsonElement cls in root.GetProperty("classes").EnumerateArray())
            {
                string name = cls.GetProperty("name").GetString() ?? "";
                int count = cls.GetProperty("count").GetInt32();
                Console.WriteLine($"    {name}: {count}명");
            }
            Console.WriteLine();

            // TryGetProperty: 안전한 접근
            if (root.TryGetProperty("principal", out JsonElement principal))
            {
                Console.WriteLine($"  교장: {principal.GetString()}");
            }
            else
            {
                Console.WriteLine("  ★ 'principal' 속성이 없음 (TryGetProperty로 안전 확인)");
            }
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 6: 인기 NuGet 패키지 소개
        // ─────────────────────────────────────────────
        static void Lesson6PopularPackages()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 6: 인기 NuGet 패키지 — 알아두면 좋은 것들");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            Console.WriteLine("  ┌──────────────────────┬──────────────────────────────────┐");
            Console.WriteLine("  │ 패키지               │ 용도                             │");
            Console.WriteLine("  ├──────────────────────┼──────────────────────────────────┤");
            Console.WriteLine("  │ Newtonsoft.Json       │ JSON 처리 (풍부한 기능)         │");
            Console.WriteLine("  │ Serilog               │ 구조화된 로깅                   │");
            Console.WriteLine("  │ AutoMapper            │ 객체 간 매핑 자동화             │");
            Console.WriteLine("  │ FluentValidation      │ 입력 유효성 검사                │");
            Console.WriteLine("  │ Dapper                │ 경량 ORM (SQL 매핑)             │");
            Console.WriteLine("  │ Entity Framework Core │ 풀 ORM (DB 추상화)              │");
            Console.WriteLine("  │ MediatR               │ 중재자 패턴 (CQRS)             │");
            Console.WriteLine("  │ Polly                 │ 재시도/회로차단기 패턴          │");
            Console.WriteLine("  │ xUnit                 │ 단위 테스트 프레임워크          │");
            Console.WriteLine("  │ Moq                   │ 목(Mock) 객체 생성              │");
            Console.WriteLine("  │ Swashbuckle           │ Swagger/OpenAPI 문서 생성       │");
            Console.WriteLine("  │ StackExchange.Redis   │ Redis 클라이언트                │");
            Console.WriteLine("  └──────────────────────┴──────────────────────────────────┘");
            Console.WriteLine();

            Console.WriteLine("  ★ 라이브러리 사용 3단계:");
            Console.WriteLine("    1. dotnet add package [이름]    (설치)");
            Console.WriteLine("    2. using [네임스페이스];        (가져오기)");
            Console.WriteLine("    3. 라이브러리 API 호출          (사용)");
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 7: 버전 관리와 종속성
        // ─────────────────────────────────────────────
        static void Lesson7VersionManagement()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 7: 버전 관리 — SemVer과 종속성");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            /*
            ★ Semantic Versioning (SemVer): Major.Minor.Patch
            ┌──────────────────────────────────────────────────┐
            │  13.0.3                                          │
            │  │  │ └── Patch: 버그 수정 (호환됨)             │
            │  │  └──── Minor: 기능 추가 (호환됨)             │
            │  └──────── Major: 큰 변경 (호환 안 될 수 있음!) │
            └──────────────────────────────────────────────────┘
            */

            Console.WriteLine("  ★ SemVer 버전 규칙:");
            Console.WriteLine("    13.0.1 → 13.0.3: Patch 업데이트 (안전)");
            Console.WriteLine("    13.0.3 → 13.1.0: Minor 업데이트 (보통 안전)");
            Console.WriteLine("    13.0.3 → 14.0.0: Major 업데이트 (★ 주의! 코드 수정 필요할 수 있음)");
            Console.WriteLine();

            Console.WriteLine("  ★ 종속성 충돌(Diamond Dependency):");
            Console.WriteLine("    내 프로젝트 → 패키지A → LibX 2.0");
            Console.WriteLine("    내 프로젝트 → 패키지B → LibX 3.0");
            Console.WriteLine("    → LibX의 버전이 충돌!");
            Console.WriteLine("    → 해결: dotnet restore가 호환 버전을 찾거나, 직접 지정");
            Console.WriteLine();

            Console.WriteLine("  ★ 안전한 업데이트 절차:");
            Console.WriteLine("    1. dotnet list package --outdated  (확인)");
            Console.WriteLine("    2. dotnet add package [이름]       (최신 버전으로 업데이트)");
            Console.WriteLine("    3. dotnet build                    (빌드 확인)");
            Console.WriteLine("    4. dotnet test                     (테스트 실행)");
            Console.WriteLine();

            Console.WriteLine("  ┌──────────────────────────────────────────────────┐");
            Console.WriteLine("  │ ★ NuGet 사용 시 흔한 실수                      │");
            Console.WriteLine("  ├──────────────────────────────────────────────────┤");
            Console.WriteLine("  │ 1. 버전 고정 안 하고 항상 최신 → 빌드 깨짐    │");
            Console.WriteLine("  │ 2. 불필요한 패키지 쌓아두기 → 프로젝트 비대화 │");
            Console.WriteLine("  │ 3. 라이선스 확인 안 함 → 법적 문제 가능       │");
            Console.WriteLine("  │ 4. dotnet restore 안 함 → 빌드 에러            │");
            Console.WriteLine("  │ 5. 여러 프로젝트에서 버전 불일치 → 충돌       │");
            Console.WriteLine("  └──────────────────────────────────────────────────┘");
            Console.WriteLine();
        }

        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine("  C# 12단계: NuGet과 라이브러리");
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine();

            Lesson1NuGetBasics();
            Lesson2JsonBasics();
            Lesson3JsonAdvanced();
            Lesson4ComplexJson();
            Lesson5DynamicJson();
            Lesson6PopularPackages();
            Lesson7VersionManagement();

            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  ★ 정리");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  1. NuGet: .NET의 패키지 관리자 (nuget.org)");
            Console.WriteLine("  2. dotnet add package: CLI로 패키지 추가");
            Console.WriteLine("  3. System.Text.Json: .NET 내장 JSON 라이브러리");
            Console.WriteLine("  4. JsonSerializerOptions: camelCase, 들여쓰기 등");
            Console.WriteLine("  5. JsonDocument: 클래스 없이 동적 JSON 읽기");
            Console.WriteLine("  6. SemVer: Major.Minor.Patch 버전 규칙");
            Console.WriteLine();
        }
    }
}
