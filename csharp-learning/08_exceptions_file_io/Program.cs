/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C# 학습 08단계: 예외 처리와 파일 입출력
  ─ try/catch/finally/when, 사용자 정의 예외, File, StreamReader/Writer ─

  ■ 컴파일: dotnet build
  ■ 실행:   dotnet run

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  [학습 목표]
  1. 예외(Exception)의 개념과 흐름을 이해한다
  2. try/catch/finally 구문을 정확히 사용한다
  3. catch when 필터로 조건부 예외 처리를 한다
  4. 사용자 정의 예외를 만든다
  5. 내부 예외(InnerException) 체이닝을 이해한다
  6. File, StreamReader/Writer로 파일 읽기/쓰기를 한다
  7. using 문으로 자원을 안전하게 해제한다
  8. JSON 직렬화/역직렬화 기초를 익힌다

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.Json;

namespace Lesson08
{
    // =====================================================================
    // 레슨 1 — 예외(Exception)의 개념
    // =====================================================================
    /*
    ★ 예외 = 프로그램 실행 중 발생하는 비정상적 상황을 알리는 신호

    ★ 비유: 요리 중 가스 불이 꺼지면 요리를 계속할 수 없음
      → 예외 = "가스 불이 꺼졌어!" 라는 알림
      → catch = "꺼진 불을 다시 켜는" 대응 코드

    ★ 예외 흐름
    ┌──────────────────────────────────────────────────┐
    │  try                                             │
    │  {                                               │
    │      // 위험할 수 있는 코드                      │
    │      int result = 10 / 0;  // 예외 발생!        │
    │  }                                               │
    │  catch (DivideByZeroException ex)                │
    │  {                                               │
    │      // 예외 처리                                │
    │  }                                               │
    │  finally                                         │
    │  {                                               │
    │      // 예외 여부와 관계없이 항상 실행           │
    │  }                                               │
    └──────────────────────────────────────────────────┘

    ★ .NET 주요 예외 계층
    ┌─ Exception
    │  ├─ SystemException
    │  │  ├─ NullReferenceException    (null 참조)
    │  │  ├─ IndexOutOfRangeException  (배열 범위 초과)
    │  │  ├─ DivideByZeroException     (0으로 나누기)
    │  │  ├─ InvalidOperationException (잘못된 상태에서 호출)
    │  │  ├─ ArgumentException         (잘못된 인자)
    │  │  │  └─ ArgumentNullException  (null 인자)
    │  │  ├─ FormatException           (형식 변환 실패)
    │  │  └─ IOException               (입출력 오류)
    │  │     └─ FileNotFoundException  (파일 없음)
    │  └─ ApplicationException         (사용자 정의 기반)
    └──────────────────────────────────────────────────
    */


    // =====================================================================
    // 레슨 3 — 사용자 정의 예외
    // =====================================================================
    /*
    ★ 왜 커스텀 예외를 만드는가?
      - 도메인(업무)에 맞는 의미 있는 예외 이름
      - 추가 정보(에러 코드, 필드명 등)를 담을 수 있음

    ★ 규칙
      1. Exception을 상속
      2. 이름 끝에 Exception 붙이기
      3. 최소 3개 생성자 제공 (권장)
    */

    class ScoreOutOfRangeException : Exception
    {
        public int AttemptedScore { get; }

        public ScoreOutOfRangeException(int attemptedScore)
            : base($"점수 {attemptedScore}은(는) 유효 범위(0-100)를 벗어났습니다.")
        {
            AttemptedScore = attemptedScore;
        }

        public ScoreOutOfRangeException(int attemptedScore, Exception innerException)
            : base($"점수 {attemptedScore}은(는) 유효 범위를 벗어났습니다.", innerException)
        {
            AttemptedScore = attemptedScore;
        }
    }

    class StudentNotFoundException : Exception
    {
        public string StudentName { get; }

        public StudentNotFoundException(string studentName)
            : base($"학생 '{studentName}'을(를) 찾을 수 없습니다.")
        {
            StudentName = studentName;
        }
    }


    // =====================================================================
    // 파일 I/O용 DTO
    // =====================================================================
    class StudentDto
    {
        public string Name { get; set; } = "";
        public int Score { get; set; }
        public int HomeworkCount { get; set; }
    }


    // =====================================================================
    // Main
    // =====================================================================
    class Program
    {
        private static readonly string DataFolder = Path.Combine(
            AppContext.BaseDirectory, "lesson08_data"
        );

        // ─────────────────────────────────────────────
        // 레슨 1: 기본 예외 처리
        // ─────────────────────────────────────────────
        static void Lesson1BasicException()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 1: 예외 — 비정상 상황의 신호");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // ── FormatException ──
            try
            {
                int count = int.Parse("세 개");
                Console.WriteLine("  파싱 결과: " + count);
            }
            catch (FormatException ex)
            {
                Console.WriteLine("  ★ FormatException 발생!");
                Console.WriteLine("    메시지: " + ex.Message);
            }
            Console.WriteLine();

            // ── DivideByZeroException ──
            try
            {
                int a = 10, b = 0;
                int result = a / b;
                Console.WriteLine("  결과: " + result);
            }
            catch (DivideByZeroException)
            {
                Console.WriteLine("  ★ DivideByZeroException: 0으로 나눌 수 없습니다!");
            }
            Console.WriteLine();

            // ── IndexOutOfRangeException ──
            try
            {
                int[] arr = { 1, 2, 3 };
                Console.WriteLine(arr[10]);
            }
            catch (IndexOutOfRangeException ex)
            {
                Console.WriteLine("  ★ IndexOutOfRangeException: " + ex.Message);
            }
            Console.WriteLine();

            // ── NullReferenceException ──
            try
            {
                string? text = null;
                Console.WriteLine(text!.Length);
            }
            catch (NullReferenceException)
            {
                Console.WriteLine("  ★ NullReferenceException: null에 접근했습니다!");
            }
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 2: 다중 catch와 finally
        // ─────────────────────────────────────────────
        static void Lesson2MultipleCatchAndFinally()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 2: 다중 catch와 finally");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            /*
            ★ catch 순서 규칙:
              - 구체적인 예외를 먼저, 일반적인 예외를 나중에!
              - Exception을 먼저 쓰면 뒤의 catch에 도달 불가!

            ┌─────────────────────────────────────────┐
            │  catch (FormatException)     ← 구체적  │
            │  catch (ArgumentException)   ← 중간    │
            │  catch (Exception)           ← 일반    │
            └─────────────────────────────────────────┘
            */

            string[] inputs = { "42", "abc", "", null! };

            foreach (string input in inputs)
            {
                Console.Write($"  입력 \"{input ?? "null"}\" → ");
                try
                {
                    if (input == null)
                        throw new ArgumentNullException(nameof(input));

                    if (input.Length == 0)
                        throw new ArgumentException("빈 문자열은 안 됩니다.");

                    int value = int.Parse(input);
                    Console.WriteLine($"성공: {value}");
                }
                catch (ArgumentNullException ex)
                {
                    Console.WriteLine($"ArgumentNullException: {ex.ParamName}");
                }
                catch (ArgumentException ex)
                {
                    Console.WriteLine($"ArgumentException: {ex.Message}");
                }
                catch (FormatException)
                {
                    Console.WriteLine("FormatException: 숫자가 아님");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"기타 예외: {ex.Message}");
                }
                finally
                {
                    // ★ finally: 예외가 나든 안 나든 항상 실행!
                    // 주로 자원 해제(파일 닫기, DB 연결 끊기)에 사용
                }
            }

            Console.WriteLine("\n  ★ finally 블록은 예외 여부와 무관하게 항상 실행됩니다.");
            Console.WriteLine("  ★ 용도: 파일 닫기, DB 연결 해제, 로그 기록 등");
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 3: catch when 필터
        // ─────────────────────────────────────────────
        static void Lesson3CatchWhenFilter()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 3: catch when — 조건부 예외 처리 (C# 6+)");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            /*
            ★ catch when: 예외 타입뿐 아니라 조건까지 검사
              catch (HttpRequestException ex) when (ex.StatusCode == 404)

            ★ 비유: 병원에서 환자를 분류하는 것과 같음
              - 같은 "배 아픔"이라도 원인(식중독 vs 맹장염)에 따라 다른 처방
            */

            int[] scores = { 85, 105, -3, 72 };

            foreach (int score in scores)
            {
                try
                {
                    if (score < 0 || score > 100)
                        throw new ScoreOutOfRangeException(score);

                    Console.WriteLine($"  점수 {score}: 정상");
                }
                catch (ScoreOutOfRangeException ex) when (ex.AttemptedScore > 100)
                {
                    Console.WriteLine($"  점수 {score}: ★ 100 초과! (입력 실수 의심)");
                }
                catch (ScoreOutOfRangeException ex) when (ex.AttemptedScore < 0)
                {
                    Console.WriteLine($"  점수 {score}: ★ 음수! (데이터 오류 의심)");
                }
            }
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 4: 사용자 정의 예외 & InnerException
        // ─────────────────────────────────────────────
        static int ParseScore(string text)
        {
            try
            {
                int score = int.Parse(text);
                if (score < 0 || score > 100)
                    throw new ScoreOutOfRangeException(score);
                return score;
            }
            catch (FormatException ex)
            {
                // ★ InnerException: 원래 예외를 감싸서 더 의미 있는 예외로 변환
                throw new ScoreOutOfRangeException(-1, ex);
            }
        }

        static void Lesson4CustomExceptionAndInner()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 4: 사용자 정의 예외 & InnerException");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            string[] inputs = { "85", "150", "abc" };

            foreach (string input in inputs)
            {
                try
                {
                    int score = ParseScore(input);
                    Console.WriteLine($"  \"{input}\" → 점수: {score}");
                }
                catch (ScoreOutOfRangeException ex)
                {
                    Console.WriteLine($"  \"{input}\" → ★ {ex.Message}");
                    if (ex.InnerException != null)
                    {
                        Console.WriteLine($"    └─ 원인: {ex.InnerException.GetType().Name}: {ex.InnerException.Message}");
                    }
                }
            }

            Console.WriteLine();
            Console.WriteLine("  ★ InnerException 체이닝: 원래 예외 정보를 보존하면서 의미 추가");
            Console.WriteLine("  ★ 디버깅 시 예외의 '원인 사슬'을 추적할 수 있음!");
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 5: 파일 쓰기와 읽기
        // ─────────────────────────────────────────────
        static void Lesson5FileWriteAndRead()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 5: 파일 쓰기와 읽기 — File 클래스");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            /*
            ★ File 클래스: 간단한 파일 작업에 최적
            ┌──────────────────────────────────────────────────┐
            │ File.WriteAllText(path, text)  전체 텍스트 저장 │
            │ File.ReadAllText(path)         전체 텍스트 읽기 │
            │ File.WriteAllLines(path, lines) 줄 단위 저장    │
            │ File.ReadAllLines(path)         줄 단위 읽기    │
            │ File.AppendAllText(path, text)  뒤에 추가       │
            │ File.Exists(path)              파일 존재 확인   │
            │ File.Delete(path)              파일 삭제        │
            │ File.Copy(src, dst)            파일 복사        │
            └──────────────────────────────────────────────────┘
            */

            Directory.CreateDirectory(DataFolder);

            // ── 줄 단위 쓰기/읽기 ──
            string snackPath = Path.Combine(DataFolder, "snacks.txt");
            string[] snackLines =
            {
                "우유,3",
                "사과,2",
                "빵,5",
                "초콜릿,1"
            };

            File.WriteAllLines(snackPath, snackLines, Encoding.UTF8);
            Console.WriteLine("  [파일 쓰기 완료] " + snackPath);

            string[] loaded = File.ReadAllLines(snackPath, Encoding.UTF8);
            Console.WriteLine("  [파일 읽기]");
            foreach (string line in loaded)
            {
                string[] parts = line.Split(',');
                Console.WriteLine($"    이름: {parts[0]}, 수량: {parts[1]}");
            }
            Console.WriteLine();

            // ── 전체 텍스트 쓰기/읽기 ──
            string memoPath = Path.Combine(DataFolder, "memo.txt");
            File.WriteAllText(memoPath, "오늘의 메모: C# 파일 I/O 공부 완료!\n날짜: 2024-01-15");
            string memoContent = File.ReadAllText(memoPath, Encoding.UTF8);
            Console.WriteLine("  [메모 파일 내용]");
            Console.WriteLine("    " + memoContent.Replace("\n", "\n    "));
            Console.WriteLine();

            // ── AppendAllText: 기존 파일 끝에 추가 ──
            File.AppendAllText(memoPath, "\n추가 메모: 예외 처리도 배움!");
            Console.WriteLine("  [메모에 한 줄 추가 완료]");
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 6: StreamReader/StreamWriter
        // ─────────────────────────────────────────────
        static void Lesson6StreamReaderWriter()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 6: StreamReader/Writer — 큰 파일 처리");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            /*
            ★ File.ReadAllText vs StreamReader
              - File.ReadAllText: 파일 전체를 메모리에 한 번에 올림
              - StreamReader: 한 줄씩 읽어서 메모리 절약!

            ★ 비유:
              - File.ReadAllText = 물통의 물을 한 번에 붓기
              - StreamReader = 빨대로 조금씩 빨아 마시기

            ★ using 문: IDisposable 자원을 자동으로 해제
              using (var reader = new StreamReader(path))
              {
                  // 사용 후 자동으로 reader.Dispose() 호출
              }
            */

            string logPath = Path.Combine(DataFolder, "scores.log");

            // ── StreamWriter로 쓰기 ──
            using (var writer = new StreamWriter(logPath, false, Encoding.UTF8))
            {
                writer.WriteLine("=== 점수 기록 ===");
                for (int i = 1; i <= 5; i++)
                {
                    writer.WriteLine($"학생{i}: {60 + i * 7}점");
                }
                writer.WriteLine("=== 기록 끝 ===");
            }
            // ★ using 블록을 벗어나면 자동으로 writer.Close() + Dispose()

            Console.WriteLine("  [StreamWriter로 파일 작성 완료]");

            // ── StreamReader로 한 줄씩 읽기 ──
            Console.WriteLine("  [StreamReader로 한 줄씩 읽기]");
            using (var reader = new StreamReader(logPath, Encoding.UTF8))
            {
                string? line;
                int lineNum = 0;
                while ((line = reader.ReadLine()) != null)
                {
                    lineNum++;
                    Console.WriteLine($"    {lineNum,3}| {line}");
                }
            }
            Console.WriteLine();

            // ── C# 8+ using 선언 (블록 없이 간결하게) ──
            Console.WriteLine("  ★ C# 8+에서는 using 선언으로 더 간결하게:");
            Console.WriteLine("    using var reader = new StreamReader(path);");
            Console.WriteLine("    // 변수가 스코프를 벗어나면 자동 Dispose");
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 7: 디렉토리 조작
        // ─────────────────────────────────────────────
        static void Lesson7DirectoryOperations()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 7: 디렉토리(폴더) 조작 — Directory, Path");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            /*
            ★ Path 클래스: 경로 조작 전용 (직접 문자열 합치지 말 것!)
            ┌────────────────────────────────────────────────────────┐
            │ Path.Combine(a, b)     경로 합치기                   │
            │ Path.GetFileName(p)    파일명만 추출                 │
            │ Path.GetExtension(p)   확장자 추출                   │
            │ Path.GetDirectoryName  디렉토리 부분 추출            │
            │ Path.GetTempPath()     임시 폴더 경로                │
            └────────────────────────────────────────────────────────┘
            */

            string subDir = Path.Combine(DataFolder, "reports", "2024");
            Directory.CreateDirectory(subDir);
            Console.WriteLine("  폴더 생성: " + subDir);

            // 파일 몇 개 만들기
            File.WriteAllText(Path.Combine(subDir, "jan.txt"), "1월 보고서");
            File.WriteAllText(Path.Combine(subDir, "feb.txt"), "2월 보고서");

            // 디렉토리 내 파일 목록
            Console.WriteLine("  [폴더 내 파일 목록]");
            foreach (string file in Directory.GetFiles(subDir))
            {
                string name = Path.GetFileName(file);
                string ext = Path.GetExtension(file);
                Console.WriteLine($"    파일: {name}  확장자: {ext}");
            }
            Console.WriteLine();

            // Path 클래스 활용
            string samplePath = @"C:\Users\student\Documents\report.docx";
            Console.WriteLine("  [Path 클래스 분석]");
            Console.WriteLine($"    전체 경로: {samplePath}");
            Console.WriteLine($"    파일명:   {Path.GetFileName(samplePath)}");
            Console.WriteLine($"    확장자:   {Path.GetExtension(samplePath)}");
            Console.WriteLine($"    디렉토리: {Path.GetDirectoryName(samplePath)}");
            Console.WriteLine($"    이름만:   {Path.GetFileNameWithoutExtension(samplePath)}");
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 8: JSON 직렬화
        // ─────────────────────────────────────────────
        static void Lesson8JsonSerialization()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 8: JSON 직렬화 — System.Text.Json");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            /*
            ★ 직렬화(Serialization): 객체 → 텍스트(JSON)
              역직렬화(Deserialization): 텍스트(JSON) → 객체

            ★ 비유: 택배 보내기
              - 직렬화 = 물건을 상자에 넣고 포장하기
              - 역직렬화 = 상자를 열고 물건 꺼내기
            */

            var students = new List<StudentDto>
            {
                new StudentDto { Name = "민수", Score = 82, HomeworkCount = 3 },
                new StudentDto { Name = "지우", Score = 95, HomeworkCount = 5 },
                new StudentDto { Name = "서연", Score = 68, HomeworkCount = 2 },
            };

            // 직렬화 (예쁘게 출력 옵션)
            var options = new JsonSerializerOptions
            {
                WriteIndented = true,                    // 들여쓰기
                Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
            };

            string json = JsonSerializer.Serialize(students, options);
            Console.WriteLine("  [직렬화 결과]");
            Console.WriteLine("  " + json.Replace("\n", "\n  "));
            Console.WriteLine();

            // JSON 파일로 저장
            string jsonPath = Path.Combine(DataFolder, "students.json");
            File.WriteAllText(jsonPath, json, Encoding.UTF8);
            Console.WriteLine("  [JSON 파일 저장] " + jsonPath);

            // 파일에서 읽어서 역직렬화
            string readJson = File.ReadAllText(jsonPath, Encoding.UTF8);
            var parsed = JsonSerializer.Deserialize<List<StudentDto>>(readJson);

            Console.WriteLine("  [역직렬화 결과]");
            if (parsed != null)
            {
                foreach (var s in parsed)
                {
                    Console.WriteLine($"    {s.Name}: {s.Score}점, 숙제 {s.HomeworkCount}개");
                }
            }
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 9: 안전한 파일 처리 패턴
        // ─────────────────────────────────────────────
        static void Lesson9SafeFilePatterns()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 9: 안전한 파일 처리 — 실전 패턴");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // ── 패턴 1: 존재 확인 후 읽기 ──
            string missingPath = Path.Combine(DataFolder, "missing.txt");
            if (File.Exists(missingPath))
            {
                string content = File.ReadAllText(missingPath);
                Console.WriteLine("  내용: " + content);
            }
            else
            {
                Console.WriteLine("  ★ 파일 없음: " + Path.GetFileName(missingPath));
            }
            Console.WriteLine();

            // ── 패턴 2: try-catch로 IO 예외 처리 ──
            try
            {
                File.ReadAllText(@"X:\impossible\path\file.txt");
            }
            catch (DirectoryNotFoundException)
            {
                Console.WriteLine("  ★ DirectoryNotFoundException: 경로가 존재하지 않음");
            }
            catch (IOException ex)
            {
                Console.WriteLine($"  ★ IOException: {ex.Message}");
            }
            Console.WriteLine();

            // ── 패턴 3: 임시 파일 사용 ──
            string tempPath = Path.GetTempFileName();
            File.WriteAllText(tempPath, "임시 데이터");
            Console.WriteLine("  임시 파일 생성: " + tempPath);
            File.Delete(tempPath);
            Console.WriteLine("  임시 파일 삭제 완료");
            Console.WriteLine();

            // ── 흔한 실수 정리 ──
            Console.WriteLine("  ┌──────────────────────────────────────────────────┐");
            Console.WriteLine("  │ ★ 파일 I/O 흔한 실수                           │");
            Console.WriteLine("  ├──────────────────────────────────────────────────┤");
            Console.WriteLine("  │ 1. 파일을 열고 닫지 않음 → using 사용!         │");
            Console.WriteLine("  │ 2. 경로를 + 로 합침 → Path.Combine 사용!      │");
            Console.WriteLine("  │ 3. 인코딩 안 지정 → UTF8 명시!                │");
            Console.WriteLine("  │ 4. 파일 존재 확인 안 함 → File.Exists 체크!   │");
            Console.WriteLine("  │ 5. 큰 파일을 ReadAllText로 읽음 → Stream 사용!│");
            Console.WriteLine("  └──────────────────────────────────────────────────┘");
            Console.WriteLine();
        }

        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine("  C# 08단계: 예외 처리와 파일 입출력");
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine();

            Lesson1BasicException();
            Lesson2MultipleCatchAndFinally();
            Lesson3CatchWhenFilter();
            Lesson4CustomExceptionAndInner();
            Lesson5FileWriteAndRead();
            Lesson6StreamReaderWriter();
            Lesson7DirectoryOperations();
            Lesson8JsonSerialization();
            Lesson9SafeFilePatterns();

            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  ★ 정리");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  1. try/catch/finally: 예외 처리의 기본 구조");
            Console.WriteLine("  2. catch when: 조건부 예외 필터 (C# 6+)");
            Console.WriteLine("  3. 커스텀 예외: 도메인에 맞는 의미 있는 예외");
            Console.WriteLine("  4. InnerException: 원인 예외 체이닝");
            Console.WriteLine("  5. File 클래스: 간단한 파일 읽기/쓰기");
            Console.WriteLine("  6. Stream: 큰 파일 처리, using으로 자원 해제");
            Console.WriteLine("  7. Path/Directory: 안전한 경로/폴더 조작");
            Console.WriteLine("  8. JSON: System.Text.Json으로 직렬화/역직렬화");
            Console.WriteLine();
        }
    }
}
