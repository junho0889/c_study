/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C# 학습 14단계: async와 await
  ─ Task, async/await, Task.WhenAll, 취소, 예외 처리, IAsyncEnumerable ─

  ■ 컴파일: dotnet build
  ■ 실행:   dotnet run

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  [학습 목표]
  1. 동기 vs 비동기의 차이를 이해한다
  2. Task와 Task<T>의 개념을 안다
  3. async/await 키워드를 올바르게 사용한다
  4. Task.WhenAll / Task.WhenAny로 동시 실행한다
  5. CancellationToken으로 작업을 취소한다
  6. 비동기 예외 처리를 이해한다
  7. IAsyncEnumerable로 비동기 스트림을 처리한다
  8. 흔한 async 실수를 피한다

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Lesson14
{
    class Program
    {
        // =====================================================================
        // 레슨 1 — 동기 vs 비동기
        // =====================================================================
        /*
        ★ 동기(Synchronous) = 한 줄씩 차례로 실행, 앞이 끝나야 다음으로
        ★ 비동기(Asynchronous) = 기다리는 동안 다른 일을 할 수 있음

        ★ 비유: 라면 끓이기
          동기: 물 끓을 때까지 냄비만 지켜봄 → 젓가락 못 꺼냄
          비동기: 물 끓는 동안 젓가락 꺼내고 그릇 준비 → 효율적!

        ┌──────────────────────────────────────────────────┐
        │  동기 흐름:                                      │
        │  파일읽기(3초) → 계산(1초) → 저장(2초) = 6초    │
        │                                                  │
        │  비동기 흐름:                                    │
        │  파일읽기(시작) → 계산(동시) → 파일읽기(완료)   │
        │  → 저장(시작) ... 전체 약 4초                    │
        └──────────────────────────────────────────────────┘

        ★ 비동기가 유용한 경우 (I/O 바운드)
          - 파일 읽기/쓰기
          - 네트워크 요청 (HTTP API 호출)
          - 데이터베이스 조회
          - 사용자 입력 대기

        ★ 비동기가 불필요한 경우 (CPU 바운드)
          - 수학 계산, 정렬, 암호화
          → Task.Run으로 별도 스레드에서 실행하는 것이 적절
        */


        // ── 비동기 시뮬레이션 함수들 ──
        static async Task<string> DownloadFileAsync(string fileName, int delayMs)
        {
            Console.WriteLine($"    📥 {fileName} 다운로드 시작...");
            await Task.Delay(delayMs);  // I/O 대기 시뮬레이션
            Console.WriteLine($"    ✅ {fileName} 다운로드 완료 ({delayMs}ms)");
            return $"{fileName} 데이터";
        }

        static async Task<int> CalculateScoreAsync(string name, int baseScore)
        {
            await Task.Delay(200);
            int bonus = name.Length * 2;
            return baseScore + bonus;
        }

        static async Task Lesson1AsyncBasics()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 1: async/await — 비동기의 기초");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            /*
            ★ async/await 규칙
              1. async 메서드는 Task 또는 Task<T>를 반환
              2. await는 async 메서드 안에서만 사용 가능
              3. await를 만나면 "여기서 기다리되, 스레드는 놓아줘"
              4. 메서드 이름 끝에 Async 붙이기 (관례)
            */

            Console.WriteLine("  [순차적 await]");
            var sw = Stopwatch.StartNew();

            string result = await DownloadFileAsync("성적표.csv", 300);
            Console.WriteLine($"    결과: {result}");

            sw.Stop();
            Console.WriteLine($"    소요 시간: {sw.ElapsedMilliseconds}ms");
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 2 — 순차 vs 동시 실행
        // =====================================================================
        static async Task Lesson2SequentialVsConcurrent()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 2: 순차 vs 동시 실행 — Task.WhenAll");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // ── 순차 실행: 하나씩 기다리기 ──
            Console.WriteLine("  [순차 실행]");
            var sw = Stopwatch.StartNew();

            string file1 = await DownloadFileAsync("수학.pdf", 300);
            string file2 = await DownloadFileAsync("영어.pdf", 400);
            string file3 = await DownloadFileAsync("과학.pdf", 200);

            sw.Stop();
            Console.WriteLine($"    순차 실행 시간: {sw.ElapsedMilliseconds}ms (약 900ms)");
            Console.WriteLine();

            // ── 동시 실행: 모두 시작 후 한꺼번에 기다리기 ──
            Console.WriteLine("  [동시 실행 — Task.WhenAll]");
            sw.Restart();

            // ★ 핵심: await를 바로 하지 않고 Task만 만들어 둠!
            Task<string> task1 = DownloadFileAsync("수학.pdf", 300);
            Task<string> task2 = DownloadFileAsync("영어.pdf", 400);
            Task<string> task3 = DownloadFileAsync("과학.pdf", 200);

            // ★ 세 작업이 모두 끝날 때까지 기다림
            string[] results = await Task.WhenAll(task1, task2, task3);

            sw.Stop();
            Console.WriteLine($"    동시 실행 시간: {sw.ElapsedMilliseconds}ms (약 400ms!)");
            Console.WriteLine($"    결과: {string.Join(", ", results)}");
            Console.WriteLine();

            /*
            ★ Task.WhenAll vs Task.WhenAny
              WhenAll: 모든 작업이 끝날 때까지 기다림
              WhenAny: 하나라도 끝나면 바로 반환 (경주 패턴)
            */

            // ── Task.WhenAny: 가장 빠른 결과 ──
            Console.WriteLine("  [Task.WhenAny — 가장 빠른 응답]");
            Task<string> fast = DownloadFileAsync("빠른서버.txt", 100);
            Task<string> slow = DownloadFileAsync("느린서버.txt", 500);

            Task<string> winner = await Task.WhenAny(fast, slow);
            Console.WriteLine($"    먼저 완료: {await winner}");
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 3 — CancellationToken (작업 취소)
        // =====================================================================
        /*
        ★ CancellationToken: 비동기 작업을 중간에 취소하는 메커니즘

        ┌──────────────────────────────────────────────────┐
        │  var cts = new CancellationTokenSource();        │
        │  cts.CancelAfter(TimeSpan.FromSeconds(2));       │
        │                                                  │
        │  await LongOperationAsync(cts.Token);            │
        │  // 2초 후 자동 취소!                           │
        └──────────────────────────────────────────────────┘

        ★ 비유: 음식 주문 취소
          "5분 안에 안 나오면 취소해 주세요" = CancelAfter
          "지금 당장 취소요!" = cts.Cancel()
        */

        static async Task LongOperationAsync(string name, CancellationToken token)
        {
            for (int i = 1; i <= 10; i++)
            {
                // ★ 취소 요청이 있으면 예외 발생!
                token.ThrowIfCancellationRequested();

                Console.WriteLine($"    {name}: 단계 {i}/10 진행 중...");
                await Task.Delay(200, token);
            }
            Console.WriteLine($"    {name}: 완료!");
        }

        static async Task Lesson3Cancellation()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 3: CancellationToken — 작업 취소");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // 0.5초 후 자동 취소
            using var cts = new CancellationTokenSource();
            cts.CancelAfter(TimeSpan.FromMilliseconds(500));

            try
            {
                await LongOperationAsync("데이터 처리", cts.Token);
            }
            catch (OperationCanceledException)
            {
                Console.WriteLine("    ★ 작업이 취소되었습니다! (0.5초 타임아웃)");
            }
            Console.WriteLine();

            Console.WriteLine("  ★ 실전 사용처:");
            Console.WriteLine("    - HTTP 요청 타임아웃");
            Console.WriteLine("    - 사용자가 '취소' 버튼을 누를 때");
            Console.WriteLine("    - 서버 종료 시 진행 중인 작업 취소");
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 4 — 비동기 예외 처리
        // =====================================================================
        static async Task<string> FaultyDownloadAsync(string name)
        {
            await Task.Delay(100);
            if (name.Contains("오류"))
                throw new InvalidOperationException($"'{name}' 다운로드 실패!");
            return $"{name} 성공";
        }

        static async Task Lesson4AsyncExceptionHandling()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 4: 비동기 예외 처리");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // ── 단일 Task 예외 ──
            Console.WriteLine("  [단일 Task 예외]");
            try
            {
                string result = await FaultyDownloadAsync("오류파일.txt");
                Console.WriteLine("    " + result);
            }
            catch (InvalidOperationException ex)
            {
                Console.WriteLine($"    ★ 예외 캐치: {ex.Message}");
            }
            Console.WriteLine();

            // ── WhenAll에서 여러 예외 ──
            Console.WriteLine("  [WhenAll — 여러 예외]");
            Task<string> t1 = FaultyDownloadAsync("정상파일.txt");
            Task<string> t2 = FaultyDownloadAsync("오류파일A.txt");
            Task<string> t3 = FaultyDownloadAsync("오류파일B.txt");

            try
            {
                string[] results = await Task.WhenAll(t1, t2, t3);
            }
            catch (InvalidOperationException ex)
            {
                // ★ await WhenAll은 첫 번째 예외만 throw
                Console.WriteLine($"    ★ 첫 번째 예외: {ex.Message}");
            }
            Console.WriteLine();

            // 모든 예외 확인하려면 Task를 검사
            Console.WriteLine("  [모든 예외 확인]");
            Task<string>[] tasks = {
                FaultyDownloadAsync("정상.txt"),
                FaultyDownloadAsync("오류1.txt"),
                FaultyDownloadAsync("오류2.txt"),
            };

            Task allTask = Task.WhenAll(tasks);
            try
            {
                await allTask;
            }
            catch
            {
                foreach (var task in tasks)
                {
                    if (task.IsFaulted)
                    {
                        Console.WriteLine($"    실패: {task.Exception?.InnerException?.Message}");
                    }
                    else if (task.IsCompletedSuccessfully)
                    {
                        Console.WriteLine($"    성공: {task.Result}");
                    }
                }
            }
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 5 — IAsyncEnumerable (비동기 스트림)
        // =====================================================================
        /*
        ★ IAsyncEnumerable<T>: 비동기 데이터 스트림 (C# 8+)
          → 데이터가 하나씩 준비될 때마다 yield return

        ★ 비유: 회전초밥집
          모든 초밥이 다 만들어질 때까지 기다리지 않고,
          만들어지는 대로 하나씩 벨트에 올려놓는 것!

        ┌──────────────────────────────────────────────────┐
        │  async IAsyncEnumerable<int> GetScoresAsync()    │
        │  {                                               │
        │      yield return await FetchScore(1);           │
        │      yield return await FetchScore(2);           │
        │  }                                               │
        │                                                  │
        │  await foreach (int score in GetScoresAsync())   │
        │  {                                               │
        │      Console.WriteLine(score);                   │
        │  }                                               │
        └──────────────────────────────────────────────────┘
        */

        static async IAsyncEnumerable<(string Name, int Score)> FetchStudentsAsync()
        {
            string[] names = { "민수", "지우", "서연", "하린", "도윤" };
            int[] scores = { 82, 95, 68, 91, 55 };

            for (int i = 0; i < names.Length; i++)
            {
                await Task.Delay(200);  // DB 조회 시뮬레이션
                yield return (names[i], scores[i]);
            }
        }

        static async Task Lesson5AsyncEnumerable()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 5: IAsyncEnumerable — 비동기 스트림");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            Console.WriteLine("  [학생 데이터 스트리밍]");
            var sw = Stopwatch.StartNew();

            await foreach (var (name, score) in FetchStudentsAsync())
            {
                string grade = score >= 90 ? "우수" : score >= 70 ? "통과" : "복습";
                Console.WriteLine($"    {name}: {score}점 ({grade}) — {sw.ElapsedMilliseconds}ms");
            }

            sw.Stop();
            Console.WriteLine($"\n    전체 소요: {sw.ElapsedMilliseconds}ms");
            Console.WriteLine("    → 데이터가 준비될 때마다 하나씩 처리!");
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 6 — async 흔한 실수
        // =====================================================================
        static async Task Lesson6CommonMistakes()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 6: async 흔한 실수 — 피해야 할 패턴");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            Console.WriteLine("  ┌──────────────────────────────────────────────────┐");
            Console.WriteLine("  │ ★ 실수 1: async void                           │");
            Console.WriteLine("  ├──────────────────────────────────────────────────┤");
            Console.WriteLine("  │  ✗ async void DoWork() { ... }                 │");
            Console.WriteLine("  │  ✓ async Task DoWork() { ... }                 │");
            Console.WriteLine("  │                                                  │");
            Console.WriteLine("  │  async void는 예외를 잡을 수 없음!             │");
            Console.WriteLine("  │  이벤트 핸들러(button_Click)에서만 사용         │");
            Console.WriteLine("  └──────────────────────────────────────────────────┘");
            Console.WriteLine();

            Console.WriteLine("  ┌──────────────────────────────────────────────────┐");
            Console.WriteLine("  │ ★ 실수 2: .Result / .Wait() 사용              │");
            Console.WriteLine("  ├──────────────────────────────────────────────────┤");
            Console.WriteLine("  │  ✗ var data = GetDataAsync().Result;  // 데드락!│");
            Console.WriteLine("  │  ✗ GetDataAsync().Wait();             // 데드락!│");
            Console.WriteLine("  │  ✓ var data = await GetDataAsync();             │");
            Console.WriteLine("  │                                                  │");
            Console.WriteLine("  │  → UI/ASP.NET에서 데드락 발생 가능!            │");
            Console.WriteLine("  └──────────────────────────────────────────────────┘");
            Console.WriteLine();

            Console.WriteLine("  ┌──────────────────────────────────────────────────┐");
            Console.WriteLine("  │ ★ 실수 3: 불필요한 async                       │");
            Console.WriteLine("  ├──────────────────────────────────────────────────┤");
            Console.WriteLine("  │  ✗ async Task<int> Get() {                     │");
            Console.WriteLine("  │        return await Task.FromResult(42);        │");
            Console.WriteLine("  │    }                                             │");
            Console.WriteLine("  │  ✓ Task<int> Get() {                            │");
            Console.WriteLine("  │        return Task.FromResult(42);              │");
            Console.WriteLine("  │    }                                             │");
            Console.WriteLine("  └──────────────────────────────────────────────────┘");
            Console.WriteLine();

            Console.WriteLine("  ┌──────────────────────────────────────────────────┐");
            Console.WriteLine("  │ ★ 실수 4: await 없이 Task 무시                │");
            Console.WriteLine("  ├──────────────────────────────────────────────────┤");
            Console.WriteLine("  │  ✗ SaveDataAsync();          // 결과 무시!     │");
            Console.WriteLine("  │  ✓ await SaveDataAsync();    // 제대로 기다림  │");
            Console.WriteLine("  │  ✓ _ = SaveDataAsync();      // 의도적 무시 명시│");
            Console.WriteLine("  └──────────────────────────────────────────────────┘");
            Console.WriteLine();

            // ── CPU 바운드 vs I/O 바운드 ──
            Console.WriteLine("  ★ 비동기 선택 기준:");
            Console.WriteLine("    I/O 바운드 (파일, 네트워크, DB)");
            Console.WriteLine("      → async/await 사용");
            Console.WriteLine("    CPU 바운드 (수학 계산, 정렬)");
            Console.WriteLine("      → Task.Run(() => 계산()) 사용");
            Console.WriteLine();

            // ── 간단 데모: Task.Run for CPU ──
            Console.WriteLine("  [CPU 바운드 작업 — Task.Run]");
            int cpuResult = await Task.Run(() =>
            {
                int sum = 0;
                for (int i = 0; i < 1_000_000; i++)
                    sum += i;
                return sum;
            });
            Console.WriteLine($"    100만까지 합: {cpuResult:N0}");
            Console.WriteLine();
        }


        // =====================================================================
        // Main
        // =====================================================================
        static async Task Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine("  C# 14단계: async와 await");
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine();

            await Lesson1AsyncBasics();
            await Lesson2SequentialVsConcurrent();
            await Lesson3Cancellation();
            await Lesson4AsyncExceptionHandling();
            await Lesson5AsyncEnumerable();
            await Lesson6CommonMistakes();

            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  ★ 정리");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  1. async/await: 비동기 코드를 동기처럼 읽기 쉽게");
            Console.WriteLine("  2. Task.WhenAll: 여러 작업을 동시에 실행");
            Console.WriteLine("  3. Task.WhenAny: 가장 빠른 결과 사용");
            Console.WriteLine("  4. CancellationToken: 작업 취소 메커니즘");
            Console.WriteLine("  5. IAsyncEnumerable: 비동기 스트림 처리");
            Console.WriteLine("  6. async void 금지! Task 반환 필수!");
            Console.WriteLine("  7. .Result/.Wait() 금지! await 사용!");
            Console.WriteLine();
        }
    }
}
