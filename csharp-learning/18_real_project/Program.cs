/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C# 학습 18단계: 실전 미니 프로젝트
  ─ 학교 성적 관리 시스템 (CRUD + LINQ + 보고서 + JSON 저장) ─

  ■ 컴파일: dotnet build
  ■ 실행:   dotnet run

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  [프로젝트 개요]
  학교 성적 관리 콘솔 앱을 만들며 지금까지 배운 모든 것을 활용합니다.

  사용하는 기능:
  - 클래스와 OOP (06단계)
  - 인터페이스 (07단계)
  - 예외 처리 (08단계)
  - LINQ (09단계)
  - 현대 C# 문법 (10단계)
  - 파일 I/O + JSON (08, 12단계)
  - 디자인 패턴 (13단계)

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;

namespace Lesson18
{
    // =====================================================================
    // 모델 클래스
    // =====================================================================

    // ★ 인터페이스: 출력 가능한 객체의 약속
    interface IPrintable
    {
        string ToDisplayString();
    }

    // ★ 학생 레코드
    class StudentRecord : IPrintable
    {
        public int Id { get; }
        public string Name { get; }
        public string ClassName { get; }
        public int Score { get; private set; }
        public int HomeworkCount { get; private set; }
        public DateTime EnrolledDate { get; }

        public StudentRecord(int id, string name, string className, int score, int homeworkCount)
        {
            if (string.IsNullOrWhiteSpace(name))
                throw new ArgumentException("이름은 비어있을 수 없습니다.", nameof(name));
            if (score < 0 || score > 100)
                throw new ArgumentOutOfRangeException(nameof(score), "점수는 0-100 범위여야 합니다.");
            if (homeworkCount < 0)
                throw new ArgumentOutOfRangeException(nameof(homeworkCount), "숙제 수는 0 이상이어야 합니다.");

            Id = id;
            Name = name;
            ClassName = className;
            Score = score;
            HomeworkCount = homeworkCount;
            EnrolledDate = DateTime.Now;
        }

        // ★ 등급 계산 — switch 식 활용 (10단계)
        public string Grade => Score switch
        {
            >= 90 => "A",
            >= 80 => "B",
            >= 70 => "C",
            >= 60 => "D",
            _ => "F"
        };

        public string GradeLabel => Score switch
        {
            >= 90 => "우수",
            >= 80 => "양호",
            >= 70 => "통과",
            >= 60 => "노력",
            _ => "복습 필요"
        };

        public bool IsHonor => Score >= 90 && HomeworkCount >= 5;
        public bool NeedsReview => Score < 60;

        // ★ 점수 업데이트 (유효성 검사 포함)
        public void UpdateScore(int newScore)
        {
            if (newScore < 0 || newScore > 100)
                throw new ArgumentOutOfRangeException(nameof(newScore));
            Score = newScore;
        }

        public void AddHomework(int count = 1)
        {
            HomeworkCount += count;
        }

        public void AddBonus(int points)
        {
            Score = Math.Min(100, Score + points);
        }

        // ★ IPrintable 구현
        public string ToDisplayString()
        {
            string honor = IsHonor ? " ★" : "";
            return $"[{Id:D3}] {Name,-6} ({ClassName}) {Score,3}점 ({Grade}/{GradeLabel}) 숙제:{HomeworkCount}개{honor}";
        }
    }

    // ★ JSON 직렬화용 DTO
    class StudentDto
    {
        public int Id { get; set; }
        public string Name { get; set; } = "";
        public string ClassName { get; set; } = "";
        public int Score { get; set; }
        public int HomeworkCount { get; set; }
    }


    // =====================================================================
    // 저장소 (Repository 패턴)
    // =====================================================================

    interface IStudentRepository
    {
        void Add(StudentRecord student);
        bool Remove(int id);
        StudentRecord? FindById(int id);
        StudentRecord? FindByName(string name);
        List<StudentRecord> GetAll();
        int Count { get; }
    }

    class InMemoryStudentRepository : IStudentRepository
    {
        private readonly List<StudentRecord> students = new();
        private int nextId = 1;

        public int Count => students.Count;

        public void Add(StudentRecord student)
        {
            students.Add(student);
            if (student.Id >= nextId) nextId = student.Id + 1;
        }

        public int GetNextId() => nextId++;

        public bool Remove(int id)
        {
            var student = FindById(id);
            if (student == null) return false;
            students.Remove(student);
            return true;
        }

        public StudentRecord? FindById(int id)
        {
            return students.FirstOrDefault(s => s.Id == id);
        }

        public StudentRecord? FindByName(string name)
        {
            return students.FirstOrDefault(s =>
                s.Name.Equals(name, StringComparison.OrdinalIgnoreCase));
        }

        public List<StudentRecord> GetAll()
        {
            return new List<StudentRecord>(students);
        }
    }


    // =====================================================================
    // 서비스 계층
    // =====================================================================

    class GradeService
    {
        private readonly IStudentRepository repository;

        public GradeService(IStudentRepository repository)
        {
            this.repository = repository;
        }

        // ── LINQ 활용 조회 메서드들 ──

        public List<StudentRecord> GetTopStudents(int count)
        {
            return repository.GetAll()
                .OrderByDescending(s => s.Score)
                .Take(count)
                .ToList();
        }

        public List<StudentRecord> GetStudentsNeedingReview()
        {
            return repository.GetAll()
                .Where(s => s.NeedsReview)
                .OrderBy(s => s.Score)
                .ToList();
        }

        public List<StudentRecord> GetHonorStudents()
        {
            return repository.GetAll()
                .Where(s => s.IsHonor)
                .OrderByDescending(s => s.Score)
                .ToList();
        }

        public List<StudentRecord> GetByClass(string className)
        {
            return repository.GetAll()
                .Where(s => s.ClassName == className)
                .OrderByDescending(s => s.Score)
                .ToList();
        }

        public List<StudentRecord> SearchByName(string keyword)
        {
            return repository.GetAll()
                .Where(s => s.Name.Contains(keyword, StringComparison.OrdinalIgnoreCase))
                .ToList();
        }

        // ── 통계 ──

        public (double Average, int Max, int Min, int PassCount, int FailCount) GetStatistics()
        {
            var all = repository.GetAll();
            if (all.Count == 0) return (0, 0, 0, 0, 0);

            return (
                Average: all.Average(s => s.Score),
                Max: all.Max(s => s.Score),
                Min: all.Min(s => s.Score),
                PassCount: all.Count(s => s.Score >= 60),
                FailCount: all.Count(s => s.Score < 60)
            );
        }

        // ── 반별 통계 (GroupBy) ──
        public List<(string ClassName, int Count, double Average, string TopStudent)> GetClassStatistics()
        {
            return repository.GetAll()
                .GroupBy(s => s.ClassName)
                .Select(g => (
                    ClassName: g.Key,
                    Count: g.Count(),
                    Average: g.Average(s => s.Score),
                    TopStudent: g.OrderByDescending(s => s.Score).First().Name
                ))
                .OrderBy(c => c.ClassName)
                .ToList();
        }

        // ── 등급 분포 ──
        public Dictionary<string, int> GetGradeDistribution()
        {
            return repository.GetAll()
                .GroupBy(s => s.Grade)
                .ToDictionary(g => g.Key, g => g.Count());
        }
    }


    // =====================================================================
    // JSON 파일 저장/로드
    // =====================================================================

    class JsonStorage
    {
        private readonly string filePath;
        private readonly JsonSerializerOptions options;

        public JsonStorage(string filePath)
        {
            this.filePath = filePath;
            options = new JsonSerializerOptions
            {
                WriteIndented = true,
                Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
            };
        }

        public void Save(List<StudentRecord> students)
        {
            var dtos = students.Select(s => new StudentDto
            {
                Id = s.Id,
                Name = s.Name,
                ClassName = s.ClassName,
                Score = s.Score,
                HomeworkCount = s.HomeworkCount,
            }).ToList();

            string dir = Path.GetDirectoryName(filePath) ?? "";
            if (!string.IsNullOrEmpty(dir))
                Directory.CreateDirectory(dir);

            string json = JsonSerializer.Serialize(dtos, options);
            File.WriteAllText(filePath, json, Encoding.UTF8);
        }

        public List<StudentDto> Load()
        {
            if (!File.Exists(filePath))
                return new List<StudentDto>();

            string json = File.ReadAllText(filePath, Encoding.UTF8);
            return JsonSerializer.Deserialize<List<StudentDto>>(json, options)
                   ?? new List<StudentDto>();
        }
    }


    // =====================================================================
    // 보고서 생성기
    // =====================================================================

    class ReportGenerator
    {
        private readonly GradeService gradeService;
        private readonly IStudentRepository repository;

        public ReportGenerator(GradeService gradeService, IStudentRepository repository)
        {
            this.gradeService = gradeService;
            this.repository = repository;
        }

        public void PrintFullReport()
        {
            var all = repository.GetAll();
            if (all.Count == 0)
            {
                Console.WriteLine("  (학생 데이터가 없습니다)");
                return;
            }

            // ── 전체 학생 목록 ──
            Console.WriteLine("  ┌─────────────────────────────────────────────────────────────┐");
            Console.WriteLine("  │                    전체 학생 목록                           │");
            Console.WriteLine("  ├─────────────────────────────────────────────────────────────┤");
            foreach (var s in all.OrderBy(s => s.Id))
            {
                Console.WriteLine($"  │ {s.ToDisplayString(),-57} │");
            }
            Console.WriteLine("  └─────────────────────────────────────────────────────────────┘");
            Console.WriteLine();

            // ── 전체 통계 ──
            var stats = gradeService.GetStatistics();
            Console.WriteLine("  ┌─────────────────────────────────┐");
            Console.WriteLine("  │        전체 성적 통계           │");
            Console.WriteLine("  ├─────────────────────────────────┤");
            Console.WriteLine($"  │ 전체 인원:    {all.Count,5}명          │");
            Console.WriteLine($"  │ 평균 점수:    {stats.Average,8:F1}점   │");
            Console.WriteLine($"  │ 최고 점수:    {stats.Max,5}점          │");
            Console.WriteLine($"  │ 최저 점수:    {stats.Min,5}점          │");
            Console.WriteLine($"  │ 통과 인원:    {stats.PassCount,5}명          │");
            Console.WriteLine($"  │ 복습 대상:    {stats.FailCount,5}명          │");
            Console.WriteLine("  └─────────────────────────────────┘");
            Console.WriteLine();

            // ── 반별 통계 ──
            var classStats = gradeService.GetClassStatistics();
            Console.WriteLine("  ┌───────────┬──────┬──────────┬──────────┐");
            Console.WriteLine("  │ 반        │ 인원 │ 평균     │ 수석     │");
            Console.WriteLine("  ├───────────┼──────┼──────────┼──────────┤");
            foreach (var cs in classStats)
            {
                Console.WriteLine($"  │ {cs.ClassName,-7}   │ {cs.Count,4} │ {cs.Average,7:F1}점 │ {cs.TopStudent,-6}   │");
            }
            Console.WriteLine("  └───────────┴──────┴──────────┴──────────┘");
            Console.WriteLine();

            // ── 등급 분포 ──
            var dist = gradeService.GetGradeDistribution();
            Console.WriteLine("  [등급 분포]");
            foreach (string grade in new[] { "A", "B", "C", "D", "F" })
            {
                int count = dist.GetValueOrDefault(grade, 0);
                string bar = new string('█', count * 3);
                Console.WriteLine($"    {grade}: {bar} ({count}명)");
            }
            Console.WriteLine();

            // ── 우등생 ──
            var honors = gradeService.GetHonorStudents();
            if (honors.Count > 0)
            {
                Console.WriteLine("  [★ 우등생 (90점 이상 + 숙제 5개 이상)]");
                foreach (var h in honors)
                {
                    Console.WriteLine($"    ★ {h.Name}: {h.Score}점, 숙제 {h.HomeworkCount}개");
                }
                Console.WriteLine();
            }

            // ── 복습 대상 ──
            var review = gradeService.GetStudentsNeedingReview();
            if (review.Count > 0)
            {
                Console.WriteLine("  [⚠ 복습 대상 (60점 미만)]");
                foreach (var r in review)
                {
                    Console.WriteLine($"    ⚠ {r.Name}: {r.Score}점 → 보충 학습 필요");
                }
                Console.WriteLine();
            }

            // ── TOP 3 ──
            var top3 = gradeService.GetTopStudents(3);
            Console.WriteLine("  [🏆 TOP 3]");
            for (int i = 0; i < top3.Count; i++)
            {
                string medal = i switch { 0 => "🥇", 1 => "🥈", 2 => "🥉", _ => "  " };
                Console.WriteLine($"    {medal} {i + 1}위: {top3[i].Name} ({top3[i].Score}점)");
            }
            Console.WriteLine();
        }
    }


    // =====================================================================
    // Main — 프로젝트 실행
    // =====================================================================
    class Program
    {
        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine("  C# 18단계: 실전 미니 프로젝트");
            Console.WriteLine("  ─ 학교 성적 관리 시스템 ─");
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine();

            // ── 1단계: 데이터 초기화 ──
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  1단계: 데이터 초기화 — 학생 등록");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            var repo = new InMemoryStudentRepository();
            var service = new GradeService(repo);
            var report = new ReportGenerator(service, repo);
            var storage = new JsonStorage(Path.Combine(
                AppContext.BaseDirectory, "lesson18_data", "students.json"));

            // 샘플 데이터 등록
            var sampleData = new (string Name, string Class, int Score, int Hw)[]
            {
                ("민수", "1반", 92, 6),
                ("지우", "1반", 95, 7),
                ("서연", "1반", 68, 2),
                ("하린", "2반", 91, 5),
                ("도윤", "2반", 55, 1),
                ("수아", "2반", 78, 4),
                ("준서", "1반", 83, 3),
                ("시은", "2반", 97, 8),
                ("예준", "1반", 45, 0),
                ("소율", "2반", 72, 3),
            };

            foreach (var (name, cls, score, hw) in sampleData)
            {
                int id = repo.GetNextId();
                repo.Add(new StudentRecord(id, name, cls, score, hw));
                Console.WriteLine($"  등록: [{id:D3}] {name} ({cls}) {score}점");
            }
            Console.WriteLine($"\n  총 {repo.Count}명 등록 완료");
            Console.WriteLine();


            // ── 2단계: 전체 보고서 ──
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  2단계: 전체 보고서 출력");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            report.PrintFullReport();


            // ── 3단계: 데이터 수정 ──
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  3단계: 데이터 수정 — 점수 업데이트 & 보너스");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // 서연 학생에게 보너스 점수
            var seoYeon = repo.FindByName("서연");
            if (seoYeon != null)
            {
                Console.WriteLine($"  [수정 전] {seoYeon.ToDisplayString()}");
                seoYeon.AddBonus(15);
                seoYeon.AddHomework(2);
                Console.WriteLine($"  [수정 후] {seoYeon.ToDisplayString()}");
                Console.WriteLine("  → 보너스 15점 + 숙제 2개 추가");
                Console.WriteLine();
            }

            // 예준 학생 점수 업데이트
            var yeJun = repo.FindByName("예준");
            if (yeJun != null)
            {
                Console.WriteLine($"  [수정 전] {yeJun.ToDisplayString()}");
                yeJun.UpdateScore(65);
                yeJun.AddHomework(3);
                Console.WriteLine($"  [수정 후] {yeJun.ToDisplayString()}");
                Console.WriteLine("  → 재시험 65점 + 숙제 3개 제출");
                Console.WriteLine();
            }

            // 잘못된 점수 업데이트 시도 (예외 처리)
            try
            {
                var test = repo.FindById(1);
                test?.UpdateScore(150);  // ★ 범위 초과!
            }
            catch (ArgumentOutOfRangeException ex)
            {
                Console.WriteLine($"  ★ 예외 처리: {ex.Message}");
                Console.WriteLine("  → 0-100 범위를 벗어나는 점수는 거부됨");
                Console.WriteLine();
            }


            // ── 4단계: 검색 기능 ──
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  4단계: 검색 기능 — LINQ 활용");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // 반별 조회
            Console.WriteLine("  [1반 학생 목록]");
            foreach (var s in service.GetByClass("1반"))
            {
                Console.WriteLine($"    {s.ToDisplayString()}");
            }
            Console.WriteLine();

            // 이름 검색
            Console.WriteLine("  [이름에 '수' 포함된 학생]");
            foreach (var s in service.SearchByName("수"))
            {
                Console.WriteLine($"    {s.ToDisplayString()}");
            }
            Console.WriteLine();

            // ID로 조회
            var found = repo.FindById(5);
            Console.WriteLine($"  [ID=5 조회] {found?.ToDisplayString() ?? "없음"}");
            Console.WriteLine();


            // ── 5단계: JSON 저장 & 로드 ──
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  5단계: JSON 파일 저장 & 로드");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // 저장
            storage.Save(repo.GetAll());
            Console.WriteLine("  [JSON 파일 저장 완료]");

            // 로드
            var loadedDtos = storage.Load();
            Console.WriteLine($"  [JSON 파일 로드] {loadedDtos.Count}명 데이터 확인");
            foreach (var dto in loadedDtos.Take(3))
            {
                Console.WriteLine($"    {dto.Name}: {dto.Score}점 ({dto.ClassName})");
            }
            Console.WriteLine("    ...");
            Console.WriteLine();


            // ── 6단계: 수정 후 최종 보고서 ──
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  6단계: 수정 후 최종 보고서");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            report.PrintFullReport();


            // ── 마무리 ──
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  ★ 프로젝트 정리 — 사용한 C# 기능 총정리");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();
            Console.WriteLine("  ┌──────────────────────────────────────────────────┐");
            Console.WriteLine("  │ 사용한 기능                     │ 단계          │");
            Console.WriteLine("  ├──────────────────────────────────┼───────────────┤");
            Console.WriteLine("  │ 클래스, 상속, 다형성            │ 05-06단계     │");
            Console.WriteLine("  │ 인터페이스 (IPrintable)         │ 07단계        │");
            Console.WriteLine("  │ 예외 처리 (try/catch)           │ 08단계        │");
            Console.WriteLine("  │ LINQ (Where, GroupBy, Select)   │ 09단계        │");
            Console.WriteLine("  │ 현대 C# (switch식, record 등)  │ 10단계        │");
            Console.WriteLine("  │ 파일 I/O + JSON 직렬화          │ 08, 12단계    │");
            Console.WriteLine("  │ Repository 패턴, DI             │ 13단계        │");
            Console.WriteLine("  │ 프로퍼티, 접근 제한자           │ 05단계        │");
            Console.WriteLine("  │ 튜플 반환, 패턴 매칭            │ 10단계        │");
            Console.WriteLine("  └──────────────────────────────────┴───────────────┘");
            Console.WriteLine();
            Console.WriteLine("  ★ 다음 단계 추천:");
            Console.WriteLine("    - ASP.NET Core로 Web API 만들기");
            Console.WriteLine("    - Entity Framework Core로 DB 연결");
            Console.WriteLine("    - xUnit으로 단위 테스트 작성");
            Console.WriteLine("    - Docker로 컨테이너 배포");
            Console.WriteLine();
        }
    }
}
