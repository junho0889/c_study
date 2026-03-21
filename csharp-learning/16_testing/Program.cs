/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C# 학습 16단계: 테스트
  ─ 단위 테스트 개념, xUnit, Assert, [Fact], [Theory], Moq, TDD ─

  ■ 컴파일: dotnet build
  ■ 실행:   dotnet run

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  [학습 목표]
  1. 테스트의 필요성과 종류를 이해한다
  2. 단위 테스트의 AAA 패턴을 안다
  3. xUnit의 [Fact]와 [Theory]를 이해한다
  4. Assert의 다양한 검증 방법을 익힌다
  5. 테스트 가능한 코드 설계를 안다
  6. Mock 객체의 개념과 용도를 안다
  7. TDD(Test-Driven Development) 사이클을 이해한다

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Lesson16
{
    // =====================================================================
    // 테스트 대상 코드 (SUT: System Under Test)
    // =====================================================================

    static class GradeCalculator
    {
        public static string GetLabel(int score)
        {
            if (score < 0 || score > 100)
                throw new ArgumentOutOfRangeException(nameof(score), "점수는 0-100 범위여야 합니다.");

            if (score >= 90) return "우수";
            if (score >= 80) return "양호";
            if (score >= 70) return "통과";
            if (score >= 60) return "노력";
            return "복습 필요";
        }

        public static double CalculateAverage(IEnumerable<int> scores)
        {
            var list = scores.ToList();
            if (list.Count == 0)
                throw new InvalidOperationException("점수 목록이 비어있습니다.");

            return list.Average();
        }

        public static bool IsHonorStudent(int score, int homeworkCount)
        {
            return score >= 90 && homeworkCount >= 5;
        }
    }

    static class StringHelper
    {
        public static string Reverse(string input)
        {
            if (input == null) throw new ArgumentNullException(nameof(input));
            char[] chars = input.ToCharArray();
            Array.Reverse(chars);
            return new string(chars);
        }

        public static bool IsPalindrome(string input)
        {
            if (input == null) throw new ArgumentNullException(nameof(input));
            string cleaned = input.ToLower().Replace(" ", "");
            return cleaned == Reverse(cleaned);
        }

        public static string Truncate(string input, int maxLength)
        {
            if (input == null) throw new ArgumentNullException(nameof(input));
            if (maxLength < 0) throw new ArgumentOutOfRangeException(nameof(maxLength));

            if (input.Length <= maxLength) return input;
            return input.Substring(0, maxLength) + "...";
        }
    }

    // DI를 활용한 테스트 가능한 설계
    interface IScoreRepository
    {
        List<int> GetScores(string studentName);
    }

    class ReportService
    {
        private readonly IScoreRepository repository;

        public ReportService(IScoreRepository repository)
        {
            this.repository = repository;
        }

        public string GenerateReport(string studentName)
        {
            var scores = repository.GetScores(studentName);
            if (scores.Count == 0) return $"{studentName}: 데이터 없음";

            double avg = scores.Average();
            string label = GradeCalculator.GetLabel((int)avg);
            return $"{studentName}: 평균 {avg:F1}점 ({label})";
        }
    }


    // =====================================================================
    // 미니 테스트 프레임워크 (xUnit 모방)
    // =====================================================================
    /*
    ★ 실제로는 xUnit을 사용하지만,
      여기서는 직접 만들어서 테스트 개념을 체험합니다.

    ★ 실제 xUnit 프로젝트 만들기:
      dotnet new xunit -n MyProject.Tests
      dotnet add reference ../MyProject/MyProject.csproj
      dotnet test
    */

    static class MiniAssert
    {
        private static int passCount;
        private static int failCount;

        public static void Reset()
        {
            passCount = 0;
            failCount = 0;
        }

        public static (int Pass, int Fail) GetResults() => (passCount, failCount);

        public static void Equal<T>(T expected, T actual, string testName)
        {
            if (EqualityComparer<T>.Default.Equals(expected, actual))
            {
                passCount++;
                Console.WriteLine($"    ✓ {testName}");
            }
            else
            {
                failCount++;
                Console.WriteLine($"    ✗ {testName}: expected={expected}, actual={actual}");
            }
        }

        public static void True(bool condition, string testName)
        {
            if (condition)
            {
                passCount++;
                Console.WriteLine($"    ✓ {testName}");
            }
            else
            {
                failCount++;
                Console.WriteLine($"    ✗ {testName}: expected True but was False");
            }
        }

        public static void False(bool condition, string testName)
        {
            True(!condition, testName);
        }

        public static void Throws<TException>(Action action, string testName) where TException : Exception
        {
            try
            {
                action();
                failCount++;
                Console.WriteLine($"    ✗ {testName}: 예외가 발생하지 않음");
            }
            catch (TException)
            {
                passCount++;
                Console.WriteLine($"    ✓ {testName}: {typeof(TException).Name} 발생 확인");
            }
            catch (Exception ex)
            {
                failCount++;
                Console.WriteLine($"    ✗ {testName}: {typeof(TException).Name} 예상, {ex.GetType().Name} 발생");
            }
        }

        public static void NotNull(object? value, string testName)
        {
            if (value != null)
            {
                passCount++;
                Console.WriteLine($"    ✓ {testName}");
            }
            else
            {
                failCount++;
                Console.WriteLine($"    ✗ {testName}: null이 아니어야 함");
            }
        }
    }

    // Mock 객체 (가짜 구현)
    class FakeScoreRepository : IScoreRepository
    {
        private readonly Dictionary<string, List<int>> data = new();

        public void Setup(string name, List<int> scores)
        {
            data[name] = scores;
        }

        public List<int> GetScores(string studentName)
        {
            return data.TryGetValue(studentName, out var scores)
                ? scores
                : new List<int>();
        }
    }


    // =====================================================================
    // Main
    // =====================================================================
    class Program
    {
        // ─────────────────────────────────────────────
        // 레슨 1: 테스트의 필요성
        // ─────────────────────────────────────────────
        static void Lesson1WhyTesting()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 1: 왜 테스트를 작성하는가?");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            /*
            ★ 테스트를 쓰는 이유
              1. 코드가 올바르게 동작하는지 자동으로 확인
              2. 버그를 조기에 발견 (비용 절감!)
              3. 리팩토링할 때 안전망 역할
              4. 코드의 사용법을 문서화하는 효과

            ★ 비유: 자동차 검사
              매번 직접 타고 돌아다니며 확인하는 대신,
              자동 검사 장치로 브레이크, 엔진 등을 체크!
            */

            Console.WriteLine("  ★ 테스트의 종류:");
            Console.WriteLine("  ┌──────────────────────────────────────────────────┐");
            Console.WriteLine("  │ 단위 테스트 (Unit Test)                         │");
            Console.WriteLine("  │  → 함수/메서드 하나를 독립적으로 검증          │");
            Console.WriteLine("  │  → 가장 빠르고 가장 많이 작성                  │");
            Console.WriteLine("  │                                                  │");
            Console.WriteLine("  │ 통합 테스트 (Integration Test)                  │");
            Console.WriteLine("  │  → 여러 컴포넌트를 함께 검증 (DB, API 등)      │");
            Console.WriteLine("  │                                                  │");
            Console.WriteLine("  │ E2E 테스트 (End-to-End Test)                    │");
            Console.WriteLine("  │  → 전체 시스템을 사용자 관점에서 검증          │");
            Console.WriteLine("  │  → 가장 느리고 유지보수 비용 높음              │");
            Console.WriteLine("  └──────────────────────────────────────────────────┘");
            Console.WriteLine();

            Console.WriteLine("  ★ 테스트 피라미드:");
            Console.WriteLine("         /\\");
            Console.WriteLine("        /E2E\\        ← 적게");
            Console.WriteLine("       /──────\\");
            Console.WriteLine("      / 통합   \\     ← 중간");
            Console.WriteLine("     /──────────\\");
            Console.WriteLine("    /  단위 테스트 \\  ← 많이!");
            Console.WriteLine("   /──────────────\\");
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 2: AAA 패턴과 기본 테스트
        // ─────────────────────────────────────────────
        static void Lesson2AAAPattern()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 2: AAA 패턴 — 테스트의 기본 구조");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            /*
            ★ AAA 패턴 (Arrange-Act-Assert)
              Arrange: 테스트 준비 (입력값, 객체 생성)
              Act:     테스트 대상 실행
              Assert:  결과 검증

            ★ xUnit 코드 형태:
              [Fact]
              public void GetLabel_Score95_Returns우수()
              {
                  // Arrange
                  int score = 95;

                  // Act
                  string result = GradeCalculator.GetLabel(score);

                  // Assert
                  Assert.Equal("우수", result);
              }
            */

            MiniAssert.Reset();
            Console.WriteLine("  [GradeCalculator.GetLabel 테스트]");

            // ── 정상 케이스 ──
            MiniAssert.Equal("우수", GradeCalculator.GetLabel(95), "95점 → 우수");
            MiniAssert.Equal("우수", GradeCalculator.GetLabel(90), "90점 → 우수 (경계)");
            MiniAssert.Equal("양호", GradeCalculator.GetLabel(85), "85점 → 양호");
            MiniAssert.Equal("양호", GradeCalculator.GetLabel(80), "80점 → 양호 (경계)");
            MiniAssert.Equal("통과", GradeCalculator.GetLabel(75), "75점 → 통과");
            MiniAssert.Equal("통과", GradeCalculator.GetLabel(70), "70점 → 통과 (경계)");
            MiniAssert.Equal("노력", GradeCalculator.GetLabel(65), "65점 → 노력");
            MiniAssert.Equal("복습 필요", GradeCalculator.GetLabel(55), "55점 → 복습 필요");
            MiniAssert.Equal("복습 필요", GradeCalculator.GetLabel(0), "0점 → 복습 필요");
            MiniAssert.Equal("우수", GradeCalculator.GetLabel(100), "100점 → 우수");

            // ── 예외 케이스 ──
            MiniAssert.Throws<ArgumentOutOfRangeException>(
                () => GradeCalculator.GetLabel(-1), "-1점 → 예외");
            MiniAssert.Throws<ArgumentOutOfRangeException>(
                () => GradeCalculator.GetLabel(101), "101점 → 예외");

            Console.WriteLine();
            var (pass, fail) = MiniAssert.GetResults();
            Console.WriteLine($"  결과: {pass} 통과, {fail} 실패");
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 3: 경계값 테스트
        // ─────────────────────────────────────────────
        static void Lesson3BoundaryTesting()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 3: 경계값 테스트 — 버그가 숨는 곳");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            /*
            ★ 경계값 = 동작이 바뀌는 지점의 값
              → 대부분의 버그는 경계에서 발생!

            ★ xUnit에서 [Theory]와 [InlineData]로 표현:
              [Theory]
              [InlineData(89, "양호")]
              [InlineData(90, "우수")]
              [InlineData(91, "우수")]
              public void GetLabel_BoundaryValues(int score, string expected)
              {
                  Assert.Equal(expected, GradeCalculator.GetLabel(score));
              }
            */

            MiniAssert.Reset();
            Console.WriteLine("  [경계값 테스트 — 등급 전환점]");

            // 각 등급 경계 앞뒤 값 테스트
            var boundaryTests = new (int Score, string Expected)[]
            {
                (59, "복습 필요"), (60, "노력"),    // 60점 경계
                (69, "노력"),     (70, "통과"),     // 70점 경계
                (79, "통과"),     (80, "양호"),     // 80점 경계
                (89, "양호"),     (90, "우수"),     // 90점 경계
            };

            foreach (var (score, expected) in boundaryTests)
            {
                MiniAssert.Equal(expected, GradeCalculator.GetLabel(score),
                    $"경계: {score}점 → {expected}");
            }

            Console.WriteLine();
            var (pass, fail) = MiniAssert.GetResults();
            Console.WriteLine($"  결과: {pass} 통과, {fail} 실패");
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 4: 다양한 Assert 유형
        // ─────────────────────────────────────────────
        static void Lesson4AssertTypes()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 4: Assert 유형 — 다양한 검증 방법");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            MiniAssert.Reset();

            // ── Equal ──
            Console.WriteLine("  [Equal — 값 비교]");
            MiniAssert.Equal("OLLEH", StringHelper.Reverse("HELLO"), "문자열 뒤집기");
            MiniAssert.Equal("", StringHelper.Reverse(""), "빈 문자열 뒤집기");
            Console.WriteLine();

            // ── True / False ──
            Console.WriteLine("  [True/False — 조건 검증]");
            MiniAssert.True(StringHelper.IsPalindrome("aba"), "aba는 회문");
            MiniAssert.True(StringHelper.IsPalindrome("A B A"), "공백 무시 회문");
            MiniAssert.False(StringHelper.IsPalindrome("hello"), "hello는 회문 아님");
            MiniAssert.True(GradeCalculator.IsHonorStudent(95, 5), "95점+5과제 → 우등");
            MiniAssert.False(GradeCalculator.IsHonorStudent(85, 5), "85점 → 우등 아님");
            MiniAssert.False(GradeCalculator.IsHonorStudent(95, 4), "과제4개 → 우등 아님");
            Console.WriteLine();

            // ── Throws ──
            Console.WriteLine("  [Throws — 예외 발생 검증]");
            MiniAssert.Throws<ArgumentNullException>(
                () => StringHelper.Reverse(null!), "null 입력 → ArgumentNull");
            MiniAssert.Throws<ArgumentOutOfRangeException>(
                () => StringHelper.Truncate("hello", -1), "음수 길이 → 예외");
            MiniAssert.Throws<InvalidOperationException>(
                () => GradeCalculator.CalculateAverage(Array.Empty<int>()), "빈 목록 → 예외");
            Console.WriteLine();

            // ── 문자열 Truncate 테스트 ──
            Console.WriteLine("  [Truncate 테스트]");
            MiniAssert.Equal("Hel...", StringHelper.Truncate("Hello World", 3), "3글자 자르기");
            MiniAssert.Equal("Hello", StringHelper.Truncate("Hello", 10), "길이보다 짧으면 그대로");
            MiniAssert.Equal("Hello", StringHelper.Truncate("Hello", 5), "정확히 같은 길이");
            Console.WriteLine();

            var (pass, fail) = MiniAssert.GetResults();
            Console.WriteLine($"  결과: {pass} 통과, {fail} 실패");
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 5: Mock 객체
        // ─────────────────────────────────────────────
        static void Lesson5MockObjects()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 5: Mock — 가짜 객체로 테스트");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            /*
            ★ Mock = 실제 의존성 대신 사용하는 가짜 객체
              → DB, API 등을 실제로 호출하지 않고 테스트!

            ★ 비유: 비행기 시뮬레이터
              진짜 비행기를 띄우지 않고도 조종 연습 가능!

            ★ 실제 Moq 라이브러리 사용:
              var mock = new Mock<IScoreRepository>();
              mock.Setup(r => r.GetScores("민수"))
                  .Returns(new List<int> { 80, 90, 85 });
            */

            MiniAssert.Reset();

            // FakeScoreRepository로 Mock 시뮬레이션
            var fakeRepo = new FakeScoreRepository();
            fakeRepo.Setup("민수", new List<int> { 80, 90, 85 });
            fakeRepo.Setup("지우", new List<int> { 95, 98, 92 });

            var service = new ReportService(fakeRepo);

            Console.WriteLine("  [ReportService 테스트 — Mock 사용]");

            string report1 = service.GenerateReport("민수");
            MiniAssert.Equal("민수: 평균 85.0점 (양호)", report1, "민수 보고서");

            string report2 = service.GenerateReport("지우");
            MiniAssert.Equal("지우: 평균 95.0점 (우수)", report2, "지우 보고서");

            string report3 = service.GenerateReport("없는학생");
            MiniAssert.Equal("없는학생: 데이터 없음", report3, "없는 학생 보고서");

            Console.WriteLine();
            var (pass, fail) = MiniAssert.GetResults();
            Console.WriteLine($"  결과: {pass} 통과, {fail} 실패");
            Console.WriteLine();

            Console.WriteLine("  ★ Mock의 핵심:");
            Console.WriteLine("    - 실제 DB/API 없이도 서비스 로직을 테스트");
            Console.WriteLine("    - 특정 시나리오(데이터 없음 등)를 쉽게 재현");
            Console.WriteLine("    - 테스트가 빠르고 결정적(deterministic)");
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 6: TDD와 xUnit 실전
        // ─────────────────────────────────────────────
        static void Lesson6TddAndXunit()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 6: TDD와 xUnit 실전 가이드");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            /*
            ★ TDD = Test-Driven Development
              1. RED:   실패하는 테스트를 먼저 작성
              2. GREEN: 테스트를 통과하는 최소한의 코드 작성
              3. REFACTOR: 코드를 정리 (테스트는 계속 통과해야!)
            */

            Console.WriteLine("  ★ TDD 사이클:");
            Console.WriteLine("    ┌─────────┐");
            Console.WriteLine("    │  RED    │ ← 실패하는 테스트 작성");
            Console.WriteLine("    └────┬────┘");
            Console.WriteLine("         ↓");
            Console.WriteLine("    ┌─────────┐");
            Console.WriteLine("    │  GREEN  │ ← 통과하는 코드 작성");
            Console.WriteLine("    └────┬────┘");
            Console.WriteLine("         ↓");
            Console.WriteLine("    ┌──────────┐");
            Console.WriteLine("    │ REFACTOR │ ← 코드 정리");
            Console.WriteLine("    └────┬─────┘");
            Console.WriteLine("         └──→ 반복!");
            Console.WriteLine();

            Console.WriteLine("  ★ xUnit 프로젝트 만들기:");
            Console.WriteLine("    dotnet new xunit -n MyApp.Tests");
            Console.WriteLine("    dotnet add reference ../MyApp/MyApp.csproj");
            Console.WriteLine("    dotnet test");
            Console.WriteLine();

            Console.WriteLine("  ★ xUnit 코드 예시:");
            Console.WriteLine("    public class GradeTests");
            Console.WriteLine("    {");
            Console.WriteLine("        [Fact]  // 단일 케이스");
            Console.WriteLine("        public void GetLabel_95_ReturnsExcellent()");
            Console.WriteLine("        {");
            Console.WriteLine("            Assert.Equal(\"우수\", GradeCalculator.GetLabel(95));");
            Console.WriteLine("        }");
            Console.WriteLine();
            Console.WriteLine("        [Theory]  // 여러 케이스");
            Console.WriteLine("        [InlineData(95, \"우수\")]");
            Console.WriteLine("        [InlineData(85, \"양호\")]");
            Console.WriteLine("        [InlineData(55, \"복습 필요\")]");
            Console.WriteLine("        public void GetLabel_VariousScores(int score, string expected)");
            Console.WriteLine("        {");
            Console.WriteLine("            Assert.Equal(expected, GradeCalculator.GetLabel(score));");
            Console.WriteLine("        }");
            Console.WriteLine("    }");
            Console.WriteLine();

            Console.WriteLine("  ★ 좋은 테스트 이름 규칙:");
            Console.WriteLine("    메서드명_조건_기대결과");
            Console.WriteLine("    예: GetLabel_ScoreBelow60_ReturnsNeedsReview");
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 7: 테스트 모범 사례
        // ─────────────────────────────────────────────
        static void Lesson7BestPractices()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 7: 테스트 모범 사례");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            Console.WriteLine("  ┌──────────────────────────────────────────────────┐");
            Console.WriteLine("  │ ★ 좋은 테스트의 조건 (FIRST)                   │");
            Console.WriteLine("  ├──────────────────────────────────────────────────┤");
            Console.WriteLine("  │ F - Fast:       빠르게 실행 (DB 안 쓰면 더 빠름)│");
            Console.WriteLine("  │ I - Independent: 테스트끼리 독립적              │");
            Console.WriteLine("  │ R - Repeatable:  반복 실행해도 같은 결과        │");
            Console.WriteLine("  │ S - Self-validating: 자동으로 성공/실패 판단    │");
            Console.WriteLine("  │ T - Timely:      코드와 함께 작성              │");
            Console.WriteLine("  └──────────────────────────────────────────────────┘");
            Console.WriteLine();

            Console.WriteLine("  ┌──────────────────────────────────────────────────┐");
            Console.WriteLine("  │ ★ 흔한 실수                                     │");
            Console.WriteLine("  ├──────────────────────────────────────────────────┤");
            Console.WriteLine("  │ 1. 한 테스트에 여러 Assert → 하나만!           │");
            Console.WriteLine("  │ 2. 테스트 간 상태 공유 → 독립적으로!           │");
            Console.WriteLine("  │ 3. 구현 세부사항 테스트 → 동작을 테스트!       │");
            Console.WriteLine("  │ 4. 너무 많은 Mock → 설계 문제 의심!            │");
            Console.WriteLine("  │ 5. 테스트 안 돌리기 → CI/CD에 통합!            │");
            Console.WriteLine("  └──────────────────────────────────────────────────┘");
            Console.WriteLine();

            Console.WriteLine("  ★ 코드 커버리지:");
            Console.WriteLine("    dotnet test --collect:\"XPlat Code Coverage\"");
            Console.WriteLine("    → 테스트가 코드의 몇 %를 실행했는지 측정");
            Console.WriteLine("    → 80% 이상이 일반적인 목표 (100%는 비현실적)");
            Console.WriteLine();
        }

        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine("  C# 16단계: 테스트");
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine();

            Lesson1WhyTesting();
            Lesson2AAAPattern();
            Lesson3BoundaryTesting();
            Lesson4AssertTypes();
            Lesson5MockObjects();
            Lesson6TddAndXunit();
            Lesson7BestPractices();

            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  ★ 정리");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  1. 테스트: 코드가 올바른지 자동 검증");
            Console.WriteLine("  2. AAA: Arrange → Act → Assert");
            Console.WriteLine("  3. 경계값: 등급 전환점 앞뒤를 반드시 테스트");
            Console.WriteLine("  4. [Fact]: 단일 케이스, [Theory]: 여러 케이스");
            Console.WriteLine("  5. Mock: 가짜 객체로 의존성 격리");
            Console.WriteLine("  6. TDD: RED → GREEN → REFACTOR 사이클");
            Console.WriteLine("  7. FIRST: 좋은 테스트의 5가지 조건");
            Console.WriteLine();
        }
    }
}
