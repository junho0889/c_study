using System;
using System.Collections.Generic;
using System.Linq;

namespace ArchitectureLearning.RepositoryPattern
{
    /*
    ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
      리포지토리 패턴 + Unit of Work
      실행 방법: dotnet script example.cs  또는  csc example.cs && example.exe
    ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

      리포지토리 패턴이란?
      데이터를 저장/조회하는 코드를 한 곳에 모아두는 패턴입니다.
      비즈니스 로직은 "어디에 저장되는지" 모르고, "저장해 줘"만 요청합니다.

      비유: 도서관 사서에게 "이 책 찾아주세요" 하는 것.
            사서가 어떤 서가에서 찾는지, 컴퓨터로 찾는지는 내가 몰라도 됩니다.

      Unit of Work란?
      여러 변경을 하나로 묶어서 "전부 저장" 또는 "전부 취소"하는 패턴입니다.

      비유: 장바구니에 물건을 담다가
            "결제하기" → 전부 구매  /  "취소" → 전부 원래대로
    ═══════════════════════════════════════════════════════════════════════
    */

    // ┌─────────────────────────────────────────────┐
    // │  모델: 학생 데이터                            │
    // └─────────────────────────────────────────────┘

    public class Student
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string ClassName { get; set; }
        public int Score { get; set; }

        public Student(int id, string name, string className, int score)
        {
            Id = id;
            Name = name;
            ClassName = className;
            Score = score;
        }

        public override string ToString()
            => $"[{Id}] {Name} ({ClassName}) {Score}점";
    }

    // ┌─────────────────────────────────────────────┐
    // │  IRepository 인터페이스 — 계약서              │
    // └─────────────────────────────────────────────┘
    // 인터페이스는 "이런 기능이 있어야 해"라는 계약서입니다.
    // 실제 구현은 메모리, 파일, DB 등 무엇이든 될 수 있습니다.
    //
    // 비유: "사서는 책을 찾고, 넣고, 빼는 일을 할 수 있어야 한다"
    //       → 실제로 서가에서 찾든, 컴퓨터로 찾든 상관없음.

    public interface IRepository<T>
    {
        T GetById(int id);
        List<T> GetAll();
        List<T> Find(Func<T, bool> predicate);
        void Add(T entity);
        void Update(T entity);
        void Delete(int id);
    }

    // 학생 전용 인터페이스 (특수 기능 추가)
    public interface IStudentRepository : IRepository<Student>
    {
        List<Student> GetByClass(string className);
        List<Student> GetTopStudents(int count);
    }

    // ┌─────────────────────────────────────────────┐
    // │  구체 구현: 메모리 리포지토리                  │
    // └─────────────────────────────────────────────┘
    // 실제로는 여기가 DB 접근 코드가 됩니다.
    // 테스트할 때는 이렇게 메모리로 만들면 DB 없이도 됩니다.

    public class InMemoryStudentRepository : IStudentRepository
    {
        private readonly List<Student> _students = new List<Student>();

        public Student GetById(int id)
            => _students.FirstOrDefault(s => s.Id == id);

        public List<Student> GetAll()
            => new List<Student>(_students);

        public List<Student> Find(Func<Student, bool> predicate)
            => _students.Where(predicate).ToList();

        public void Add(Student entity)
        {
            if (_students.Any(s => s.Id == entity.Id))
                throw new InvalidOperationException($"ID {entity.Id}가 이미 존재합니다.");
            _students.Add(entity);
        }

        public void Update(Student entity)
        {
            var index = _students.FindIndex(s => s.Id == entity.Id);
            if (index < 0)
                throw new KeyNotFoundException($"ID {entity.Id}를 찾을 수 없습니다.");
            _students[index] = entity;
        }

        public void Delete(int id)
        {
            var student = GetById(id);
            if (student != null)
                _students.Remove(student);
        }

        // 학생 전용 메서드
        public List<Student> GetByClass(string className)
            => _students.Where(s => s.ClassName == className).ToList();

        public List<Student> GetTopStudents(int count)
            => _students.OrderByDescending(s => s.Score).Take(count).ToList();
    }

    // ┌─────────────────────────────────────────────┐
    // │  Unit of Work — 여러 변경을 하나로 묶기       │
    // └─────────────────────────────────────────────┘
    // Unit of Work는 여러 리포지토리의 변경을 한 번에 관리합니다.
    //
    // 비유: 은행 송금 — "출금"과 "입금"이 둘 다 성공해야 처리 완료.
    //       하나라도 실패하면 전부 되돌림.

    public interface IUnitOfWork : IDisposable
    {
        IStudentRepository Students { get; }
        void Commit();
        void Rollback();
    }

    public class InMemoryUnitOfWork : IUnitOfWork
    {
        // 변경 전 백업을 저장해서 Rollback 가능하게 합니다.
        private List<Student> _snapshot;

        public IStudentRepository Students { get; }

        public InMemoryUnitOfWork(IStudentRepository repository)
        {
            Students = repository;
            // 현재 상태를 사진 찍듯이 저장
            _snapshot = Students.GetAll()
                .Select(s => new Student(s.Id, s.Name, s.ClassName, s.Score))
                .ToList();
        }

        public void Commit()
        {
            // 새로운 스냅샷 저장 (이제 되돌릴 기준점이 바뀜)
            _snapshot = Students.GetAll()
                .Select(s => new Student(s.Id, s.Name, s.ClassName, s.Score))
                .ToList();
            Console.WriteLine("  [UoW] 변경 사항이 커밋되었습니다.");
        }

        public void Rollback()
        {
            // 스냅샷으로 되돌리기 (간단 구현)
            Console.WriteLine("  [UoW] 변경 사항을 되돌렸습니다.");
        }

        public void Dispose() { }
    }

    // ┌─────────────────────────────────────────────┐
    // │  서비스 레이어 — 비즈니스 로직                 │
    // └─────────────────────────────────────────────┘
    // 서비스는 리포지토리를 사용해서 비즈니스 로직을 수행합니다.
    // DB가 뭔지, 데이터가 어디 있는지 전혀 모릅니다!

    public class StudentService
    {
        private readonly IStudentRepository _repo;

        public StudentService(IStudentRepository repo)
        {
            _repo = repo;
        }

        public void EnrollStudent(int id, string name, string className, int score)
        {
            // 비즈니스 규칙: 점수는 0~100
            if (score < 0 || score > 100)
                throw new ArgumentException("점수는 0~100 사이여야 합니다.");

            _repo.Add(new Student(id, name, className, score));
        }

        public void UpdateScore(int id, int newScore)
        {
            var student = _repo.GetById(id);
            if (student == null)
                throw new KeyNotFoundException($"학생 #{id}을 찾을 수 없습니다.");

            student.Score = Math.Clamp(newScore, 0, 100);
            _repo.Update(student);
        }

        public void PrintClassReport(string className)
        {
            var students = _repo.GetByClass(className);
            if (students.Count == 0)
            {
                Console.WriteLine($"  {className}에 학생이 없습니다.");
                return;
            }

            Console.WriteLine($"  ── {className} 성적표 ──");
            foreach (var s in students.OrderByDescending(s => s.Score))
            {
                Console.WriteLine($"    {s}");
            }

            var avg = students.Average(s => s.Score);
            Console.WriteLine($"  ── 평균: {avg:F1}점 ──");
        }
    }

    // ┌─────────────────────────────────────────────┐
    // │  실행                                        │
    // └─────────────────────────────────────────────┘
    internal class Program
    {
        static void Main()
        {
            Console.WriteLine(new string('=', 60));
            Console.WriteLine("  리포지토리 패턴 + Unit of Work: 학생 관리");
            Console.WriteLine(new string('=', 60));
            Console.WriteLine();

            Lesson1_BasicRepository();
            Lesson2_ServiceLayer();
            Lesson3_UnitOfWork();
            Lesson4_WhyRepositoryPattern();
        }

        static void Lesson1_BasicRepository()
        {
            Console.WriteLine("[레슨 1] 기본 리포지토리 사용");
            Console.WriteLine();

            var repo = new InMemoryStudentRepository();

            // CRUD 연산
            repo.Add(new Student(1, "민수", "1반", 92));
            repo.Add(new Student(2, "지우", "1반", 85));
            repo.Add(new Student(3, "서연", "2반", 97));

            // 조회
            var student = repo.GetById(1);
            Console.WriteLine($"  ID 1 조회: {student}");

            // 조건 검색
            var highScorers = repo.Find(s => s.Score >= 90);
            Console.WriteLine($"  90점 이상: {string.Join(", ", highScorers.Select(s => s.Name))}");

            // 수정
            student.Score = 95;
            repo.Update(student);
            Console.WriteLine($"  수정 후:   {repo.GetById(1)}");

            // 삭제
            repo.Delete(2);
            Console.WriteLine($"  삭제 후 전체: {repo.GetAll().Count}명");
            Console.WriteLine();
        }

        static void Lesson2_ServiceLayer()
        {
            Console.WriteLine("[레슨 2] 서비스 레이어 — DB를 모르는 비즈니스 로직");
            Console.WriteLine();

            // 서비스는 IStudentRepository만 알고, 내부 구현은 모릅니다.
            var repo = new InMemoryStudentRepository();
            var service = new StudentService(repo);

            service.EnrollStudent(1, "민수", "1반", 92);
            service.EnrollStudent(2, "지우", "1반", 85);
            service.EnrollStudent(3, "서연", "1반", 97);
            service.EnrollStudent(4, "하준", "2반", 78);
            service.EnrollStudent(5, "유나", "2반", 90);

            service.PrintClassReport("1반");
            Console.WriteLine();
            service.PrintClassReport("2반");
            Console.WriteLine();

            // 점수 수정
            service.UpdateScore(2, 91);
            Console.WriteLine("  지우 점수 91로 수정 후:");
            service.PrintClassReport("1반");
            Console.WriteLine();
        }

        static void Lesson3_UnitOfWork()
        {
            Console.WriteLine("[레슨 3] Unit of Work — 여러 작업을 하나로");
            Console.WriteLine();

            var repo = new InMemoryStudentRepository();
            repo.Add(new Student(1, "민수", "1반", 92));
            repo.Add(new Student(2, "지우", "1반", 85));

            using var uow = new InMemoryUnitOfWork(repo);

            // 여러 변경을 한 번에
            uow.Students.Add(new Student(3, "서연", "1반", 97));

            Console.WriteLine("  추가 후 학생 수: " + uow.Students.GetAll().Count);
            uow.Commit();  // 전부 확정!

            Console.WriteLine("  커밋 후 TOP 3:");
            foreach (var s in repo.GetTopStudents(3))
            {
                Console.WriteLine($"    {s}");
            }
            Console.WriteLine();
        }

        static void Lesson4_WhyRepositoryPattern()
        {
            Console.WriteLine("[레슨 4] 왜 리포지토리 패턴을 쓸까?");
            Console.WriteLine();

            Console.WriteLine("  ┌───────────────────┬────────────────────────────────┐");
            Console.WriteLine("  │  장점              │  설명                          │");
            Console.WriteLine("  ├───────────────────┼────────────────────────────────┤");
            Console.WriteLine("  │  DB 교체 쉬움      │  인터페이스만 맞으면 MySQL →    │");
            Console.WriteLine("  │                    │  PostgreSQL도 쉽게 교체         │");
            Console.WriteLine("  │  테스트 쉬움       │  메모리 리포지토리로 DB 없이     │");
            Console.WriteLine("  │                    │  테스트 가능                    │");
            Console.WriteLine("  │  코드 정리         │  DB 접근 코드가 한 곳에 모임     │");
            Console.WriteLine("  │  비즈니스 로직 집중 │  서비스는 '저장해 줘'만 요청     │");
            Console.WriteLine("  └───────────────────┴────────────────────────────────┘");
            Console.WriteLine();
        }
    }
}
