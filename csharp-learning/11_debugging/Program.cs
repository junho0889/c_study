/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C# 학습 11단계: 디버깅
  ─ 버그 재현, 중간값 추적, 경계값 검사, 디버거 활용, 로깅 ─

  ■ 컴파일: dotnet build
  ■ 실행:   dotnet run

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  [학습 목표]
  1. 디버깅의 기본 사고방식을 이해한다
  2. 버그를 재현하고 원인을 좁혀 나간다
  3. Console.WriteLine 디버깅의 한계와 올바른 사용법
  4. Debug/Trace 클래스를 활용한다
  5. 조건부 컴파일(#if DEBUG)을 이해한다
  6. 디버거 도구(중단점, Watch, 호출 스택)를 안다
  7. 흔한 버그 패턴을 인식하고 예방한다

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;

namespace Lesson11
{
    class Program
    {
        // =====================================================================
        // 레슨 1 — 디버깅 사고방식
        // =====================================================================
        /*
        ★ 디버깅 = "이상한 결과의 원인을 찾아 고치는 과정"

        ★ 디버깅 5단계 프로세스
        ┌──────────────────────────────────────────────────┐
        │  1. 재현(Reproduce)                              │
        │     → 버그를 다시 볼 수 있어야 고칠 수 있다     │
        │                                                  │
        │  2. 격리(Isolate)                                │
        │     → 문제 범위를 좁힌다 (어떤 함수? 어떤 줄?)  │
        │                                                  │
        │  3. 원인 파악(Identify)                          │
        │     → 왜 틀린 값이 나오는지 이해한다            │
        │                                                  │
        │  4. 수정(Fix)                                    │
        │     → 원인을 제거하는 코드를 작성한다            │
        │                                                  │
        │  5. 검증(Verify)                                 │
        │     → 수정 후 다시 테스트한다                    │
        └──────────────────────────────────────────────────┘

        ★ 비유: 의사의 진단
          환자: "배가 아파요" (증상)
          의사: 어디가? 언제부터? 뭘 먹었나? (재현+격리)
          의사: 검사 결과 식중독 (원인)
          의사: 약 처방 (수정)
          의사: 내일 다시 오세요 (검증)
        */

        // ─── 버그가 있는 함수 (의도적!) ───
        static int WrongAverage(int[] values)
        {
            int total = 0;
            foreach (int value in values)
            {
                total += value;
            }
            // ★ 버그: length - 1 로 나누고 있음!
            return total / (values.Length - 1);
        }

        static double CorrectAverage(int[] values)
        {
            if (values.Length == 0) return 0;

            int total = 0;
            foreach (int value in values)
            {
                total += value;
            }
            return (double)total / values.Length;
        }

        static void Lesson1ReproduceBug()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 1: 버그 재현 — 이상한 결과 다시 보기");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            int[] scores = { 80, 90, 70 };

            Console.WriteLine("  [잘못된 함수 vs 올바른 함수]");
            Console.WriteLine($"  WrongAverage:   {WrongAverage(scores)}");
            Console.WriteLine($"  CorrectAverage: {CorrectAverage(scores):F1}");
            Console.WriteLine();

            Console.WriteLine("  ★ 80+90+70=240, 240/3=80이 정답인데");
            Console.WriteLine("    WrongAverage는 240/(3-1)=120을 반환!");
            Console.WriteLine("    → Length-1이 아니라 Length로 나눠야 함");
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 2 — 중간값 추적 (Printf 디버깅)
        // =====================================================================
        /*
        ★ 가장 원시적이지만 가장 많이 쓰는 방법!
          → 중간 계산값을 출력해서 어디서 틀렸는지 추적

        ★ 장점: 도구 없이도 가능
        ★ 단점: 출력문을 넣고 빼는 게 번거로움
        */

        static int FindBuggyMax(int[] values)
        {
            // ★ 버그: max를 0으로 초기화 → 모든 값이 음수면 오답!
            int max = 0;  // 버그 포인트!

            Console.WriteLine("    [추적 시작]");
            for (int i = 0; i < values.Length; i++)
            {
                Console.WriteLine($"      i={i}, values[i]={values[i]}, 현재 max={max}");
                if (values[i] > max)
                {
                    max = values[i];
                    Console.WriteLine($"      → max 갱신: {max}");
                }
            }
            return max;
        }

        static int CorrectMax(int[] values)
        {
            if (values.Length == 0)
                throw new ArgumentException("빈 배열!");

            int max = values[0];  // ★ 수정: 첫 번째 값으로 초기화!
            for (int i = 1; i < values.Length; i++)
            {
                if (values[i] > max)
                    max = values[i];
            }
            return max;
        }

        static void Lesson2TraceMiddleValues()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 2: 중간값 추적 — printf 디버깅");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // 정상 케이스
            int[] positives = { 3, 7, 2, 9, 1 };
            Console.WriteLine("  [정상 케이스: 양수 배열]");
            int result1 = FindBuggyMax(positives);
            Console.WriteLine($"    결과: {result1} (정답: 9) ✓");
            Console.WriteLine();

            // 버그 드러나는 케이스
            int[] negatives = { -5, -3, -8, -1 };
            Console.WriteLine("  [버그 케이스: 음수 배열]");
            int result2 = FindBuggyMax(negatives);
            Console.WriteLine($"    결과: {result2} (정답: -1) ★ 오답!");
            Console.WriteLine();

            Console.WriteLine($"  올바른 결과: {CorrectMax(negatives)}");
            Console.WriteLine();
            Console.WriteLine("  ★ 핵심: max=0으로 초기화하면 음수만 있을 때 0이 남음");
            Console.WriteLine("  ★ 해결: max=values[0]으로 첫 값 사용");
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 3 — 경계값 검사
        // =====================================================================
        /*
        ★ 경계값(Boundary) = 동작이 바뀌는 지점의 값
          → 대부분의 버그는 경계에서 발생!

        ┌──────────────────────────────────────────────────┐
        │ 흔한 경계값 검사 항목                            │
        ├──────────────────────────────────────────────────┤
        │ 빈 배열 / 빈 문자열                              │
        │ 원소 1개인 배열                                  │
        │ null 입력                                        │
        │ 0, 음수, int.MaxValue, int.MinValue             │
        │ 조건의 경계 (>=70에서 69와 70)                  │
        │ 짝수/홀수 개수                                   │
        └──────────────────────────────────────────────────┘
        */

        static string SafeDivide(int a, int b)
        {
            if (b == 0) return "0으로 나눌 수 없음";
            return $"{a} / {b} = {a / b}";
        }

        static double SafeAverage(int[] values)
        {
            if (values == null) return 0;
            if (values.Length == 0) return 0;
            return (double)values.Sum() / values.Length;
        }

        static void Lesson3BoundaryChecking()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 3: 경계값 검사 — 버그가 숨는 곳");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // ── 나눗셈 경계 ──
            Console.WriteLine("  [나눗셈 경계 테스트]");
            Console.WriteLine("    " + SafeDivide(10, 3));
            Console.WriteLine("    " + SafeDivide(10, 0));
            Console.WriteLine("    " + SafeDivide(0, 5));
            Console.WriteLine("    " + SafeDivide(-10, 3));
            Console.WriteLine();

            // ── 배열 경계 ──
            Console.WriteLine("  [배열 경계 테스트]");
            Console.WriteLine($"    null 배열:     {SafeAverage(null!):F1}");
            Console.WriteLine($"    빈 배열:       {SafeAverage(Array.Empty<int>()):F1}");
            Console.WriteLine($"    원소 1개:      {SafeAverage(new[] { 42 }):F1}");
            Console.WriteLine($"    정상 배열:     {SafeAverage(new[] { 10, 20, 30 }):F1}");
            Console.WriteLine();

            // ── Off-by-one 에러 (가장 흔한 버그!) ──
            Console.WriteLine("  [Off-by-one 에러 예시]");
            int[] arr = { 10, 20, 30, 40, 50 };

            // 잘못된 반복 범위
            Console.Write("    잘못: ");
            for (int i = 0; i <= arr.Length - 1; i++)  // 이건 사실 맞지만...
            {
                Console.Write($"{arr[i]} ");
            }
            Console.WriteLine();

            // ★ 진짜 위험한 경우
            Console.WriteLine("    ★ 문자열에서 마지막 문자 빼기:");
            string word = "Hello";
            Console.WriteLine($"      Substring(0, {word.Length - 1}) = \"{word.Substring(0, word.Length - 1)}\"");
            Console.WriteLine($"      빈 문자열이면? → 예외 발생 가능!");
            Console.WriteLine();

            // ── 경계값 체크리스트 ──
            Console.WriteLine("  ┌──────────────────────────────────────────────────┐");
            Console.WriteLine("  │ ★ 경계값 체크리스트                            │");
            Console.WriteLine("  ├──────────────────────────────────────────────────┤");
            Console.WriteLine("  │ □ 빈 컬렉션(Count=0)으로 테스트했는가?         │");
            Console.WriteLine("  │ □ null 입력을 처리했는가?                       │");
            Console.WriteLine("  │ □ 음수 입력을 고려했는가?                       │");
            Console.WriteLine("  │ □ 조건 경계(69 vs 70)를 확인했는가?            │");
            Console.WriteLine("  │ □ 정수 오버플로우를 고려했는가?                │");
            Console.WriteLine("  │ □ 원소 1개인 경우를 확인했는가?                │");
            Console.WriteLine("  └──────────────────────────────────────────────────┘");
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 4 — Debug / Trace 클래스
        // =====================================================================
        /*
        ★ System.Diagnostics.Debug
          - Debug.WriteLine: DEBUG 빌드에서만 출력 (Release에서 사라짐!)
          - Debug.Assert: 조건이 거짓이면 중단

        ★ System.Diagnostics.Trace
          - Trace.WriteLine: 모든 빌드에서 출력
          - 프로덕션 로깅에 사용

        ★ Console.WriteLine 디버깅의 문제점
          1. 배포 전에 일일이 지워야 함
          2. 출력이 많으면 화면이 복잡해짐
          → Debug/Trace를 쓰면 빌드 설정으로 자동 제어!
        */
        static void Lesson4DebugAndTrace()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 4: Debug/Trace — 체계적 디버깅 도구");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // Debug.WriteLine: DEBUG 빌드에서만 출력
            Debug.WriteLine("이 메시지는 DEBUG 빌드에서만 보입니다.");

            // Debug.Assert: 조건이 거짓이면 경고
            int score = 85;
            Debug.Assert(score >= 0 && score <= 100, "점수가 범위를 벗어남!");

            Console.WriteLine("  Debug.WriteLine → DEBUG 빌드에서만 출력");
            Console.WriteLine("  Debug.Assert    → 조건 거짓이면 중단/경고");
            Console.WriteLine("  Trace.WriteLine → 모든 빌드에서 출력");
            Console.WriteLine();

            // 조건부 컴파일
            Console.WriteLine("  [조건부 컴파일 결과]");
#if DEBUG
            Console.WriteLine("    현재 DEBUG 모드로 빌드됨");
#else
            Console.WriteLine("    현재 RELEASE 모드로 빌드됨");
#endif
            Console.WriteLine();

            // Stopwatch: 성능 측정
            var sw = Stopwatch.StartNew();
            int sum = 0;
            for (int i = 0; i < 1_000_000; i++)
            {
                sum += i;
            }
            sw.Stop();
            Console.WriteLine($"  Stopwatch: 100만 번 덧셈 = {sw.ElapsedMilliseconds}ms");
            Console.WriteLine($"  결과: {sum}");
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 5 — 흔한 버그 패턴 모음
        // =====================================================================
        static void Lesson5CommonBugPatterns()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 5: 흔한 버그 패턴 — 미리 알면 피할 수 있다");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // ── 패턴 1: 참조 vs 값 혼동 ──
            Console.WriteLine("  [패턴 1: 참조 vs 값 복사]");
            var list1 = new List<int> { 1, 2, 3 };
            var list2 = list1;  // ★ 복사가 아니라 같은 객체를 가리킴!
            list2.Add(4);
            Console.WriteLine($"    list1: [{string.Join(", ", list1)}]");
            Console.WriteLine($"    list2: [{string.Join(", ", list2)}]");
            Console.WriteLine("    ★ list2에 추가했는데 list1도 변함! (같은 참조)");

            // 올바른 복사
            var list3 = new List<int>(list1);  // 새 List 생성
            list3.Add(5);
            Console.WriteLine($"    list3(복사본): [{string.Join(", ", list3)}]");
            Console.WriteLine($"    list1(원본):   [{string.Join(", ", list1)}]");
            Console.WriteLine();

            // ── 패턴 2: 문자열 비교 ──
            Console.WriteLine("  [패턴 2: 문자열 비교 실수]");
            string a = "Hello";
            string b = "hello";
            Console.WriteLine($"    \"{a}\" == \"{b}\": {a == b}");
            Console.WriteLine($"    대소문자 무시: {string.Equals(a, b, StringComparison.OrdinalIgnoreCase)}");
            Console.WriteLine();

            // ── 패턴 3: 부동소수점 비교 ──
            Console.WriteLine("  [패턴 3: 부동소수점 비교]");
            double x = 0.1 + 0.2;
            Console.WriteLine($"    0.1 + 0.2 = {x}");
            Console.WriteLine($"    0.1 + 0.2 == 0.3: {x == 0.3}");  // false!
            Console.WriteLine($"    Math.Abs(차이) < 0.0001: {Math.Abs(x - 0.3) < 0.0001}");  // true
            Console.WriteLine("    ★ 부동소수점은 == 대신 오차 범위로 비교!");
            Console.WriteLine();

            // ── 패턴 4: foreach 중 컬렉션 수정 ──
            Console.WriteLine("  [패턴 4: foreach 중 수정 금지]");
            Console.WriteLine("    foreach 루프 안에서 Add/Remove → InvalidOperationException!");
            Console.WriteLine("    해결: ToList()로 복사 후 순회, 또는 for 루프 사용");
            Console.WriteLine();

            // ── 패턴 5: 정수 나눗셈 ──
            Console.WriteLine("  [패턴 5: 정수 나눗셈 함정]");
            int totalScore = 7;
            int count = 2;
            Console.WriteLine($"    int: {totalScore} / {count} = {totalScore / count}");
            Console.WriteLine($"    double: {totalScore} / {count} = {(double)totalScore / count}");
            Console.WriteLine("    ★ 정수끼리 나누면 소수점 아래 버림!");
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 6 — IDE 디버거 활용 가이드
        // =====================================================================
        static void Lesson6DebuggerGuide()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 6: IDE 디버거 활용 — Visual Studio / Rider");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            Console.WriteLine("  ┌──────────────────────────────────────────────────┐");
            Console.WriteLine("  │ 디버거 핵심 기능                                │");
            Console.WriteLine("  ├──────────────────────────────────────────────────┤");
            Console.WriteLine("  │                                                  │");
            Console.WriteLine("  │ 1. 중단점(Breakpoint) — F9                      │");
            Console.WriteLine("  │    특정 줄에서 실행을 멈추고 상태를 확인        │");
            Console.WriteLine("  │    조건부 중단점: score > 90 일 때만 멈춤       │");
            Console.WriteLine("  │                                                  │");
            Console.WriteLine("  │ 2. 단계 실행                                    │");
            Console.WriteLine("  │    F10: 한 줄 실행 (Step Over)                  │");
            Console.WriteLine("  │    F11: 함수 안으로 들어가기 (Step Into)        │");
            Console.WriteLine("  │    Shift+F11: 함수 밖으로 나오기 (Step Out)     │");
            Console.WriteLine("  │                                                  │");
            Console.WriteLine("  │ 3. Watch 창                                     │");
            Console.WriteLine("  │    변수 값을 실시간으로 관찰                    │");
            Console.WriteLine("  │    식(expression)도 평가 가능                   │");
            Console.WriteLine("  │                                                  │");
            Console.WriteLine("  │ 4. 호출 스택(Call Stack)                        │");
            Console.WriteLine("  │    현재 함수가 어디서 호출되었는지 추적         │");
            Console.WriteLine("  │                                                  │");
            Console.WriteLine("  │ 5. 즉시 실행 창(Immediate Window)              │");
            Console.WriteLine("  │    중단 상태에서 코드를 직접 실행               │");
            Console.WriteLine("  │                                                  │");
            Console.WriteLine("  └──────────────────────────────────────────────────┘");
            Console.WriteLine();

            // 실습용 코드 (중단점을 걸어서 확인해 보세요!)
            Console.WriteLine("  [실습: 아래 코드에 중단점을 걸어 보세요]");
            var students = new List<(string Name, int Score)>
            {
                ("민수", 82), ("지우", 95), ("서연", 68), ("하린", 91)
            };

            foreach (var (name, score) in students)
            {
                string grade = score >= 90 ? "우수" : score >= 70 ? "통과" : "복습";
                Console.WriteLine($"    {name}: {score}점 → {grade}");
                // ★ 여기에 중단점(F9)을 걸고, Watch에서 name, score, grade를 관찰!
            }
            Console.WriteLine();
        }


        // =====================================================================
        // 레슨 7 — 실전 디버깅 사례
        // =====================================================================
        static void Lesson7PracticalDebugging()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 7: 실전 — 버그를 찾아서 고치기");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // ── 사례: 학생 평균 계산에 버그 ──
            Console.WriteLine("  [사례: 통과 학생만 평균 계산]");

            var students = new List<(string Name, int Score)>
            {
                ("민수", 82), ("지우", 95), ("서연", 68), ("하린", 91), ("도윤", 55)
            };

            // 잘못된 코드
            var passing = students.Where(s => s.Score >= 70).ToList();
            int wrongTotal = 0;
            foreach (var s in passing)
                wrongTotal += s.Score;
            // ★ 버그: 전체 인원수로 나눔!
            double wrongAvg = (double)wrongTotal / students.Count;

            // 올바른 코드
            double correctAvg = passing.Average(s => s.Score);

            Console.WriteLine($"    통과 학생 수: {passing.Count}");
            Console.WriteLine($"    잘못된 평균: {wrongAvg:F1} (전체 {students.Count}명으로 나눔)");
            Console.WriteLine($"    올바른 평균: {correctAvg:F1} (통과 {passing.Count}명으로 나눔)");
            Console.WriteLine("    ★ 버그: 필터링된 인원이 아닌 전체 인원으로 나눈 것!");
            Console.WriteLine();

            // 디버깅 요약 팁
            Console.WriteLine("  ┌──────────────────────────────────────────────────┐");
            Console.WriteLine("  │ ★ 디버깅 꿀팁                                  │");
            Console.WriteLine("  ├──────────────────────────────────────────────────┤");
            Console.WriteLine("  │ 1. 오리 디버깅: 코드를 소리 내어 설명해 보기   │");
            Console.WriteLine("  │ 2. 이등분 검색: 코드 중간에 출력문 넣기        │");
            Console.WriteLine("  │ 3. 최근 변경 확인: git diff로 뭘 바꿨는지 확인 │");
            Console.WriteLine("  │ 4. 최소 재현: 문제를 가장 작은 코드로 축소     │");
            Console.WriteLine("  │ 5. 가정 의심: \"이건 당연히 맞겠지\" 의심하기    │");
            Console.WriteLine("  └──────────────────────────────────────────────────┘");
            Console.WriteLine();
        }


        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine("  C# 11단계: 디버깅");
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine();

            Lesson1ReproduceBug();
            Lesson2TraceMiddleValues();
            Lesson3BoundaryChecking();
            Lesson4DebugAndTrace();
            Lesson5CommonBugPatterns();
            Lesson6DebuggerGuide();
            Lesson7PracticalDebugging();

            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  ★ 정리");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  1. 재현 → 격리 → 원인 → 수정 → 검증");
            Console.WriteLine("  2. 중간값 출력으로 값 추적 (printf 디버깅)");
            Console.WriteLine("  3. 경계값 검사: 빈 배열, null, 0, 음수");
            Console.WriteLine("  4. Debug/Trace: 빌드 설정에 따라 자동 제어");
            Console.WriteLine("  5. IDE 디버거: 중단점, Watch, 호출 스택 활용");
            Console.WriteLine("  6. 흔한 패턴: 참조 복사, 부동소수점, 정수 나눗셈");
            Console.WriteLine();
        }
    }
}
