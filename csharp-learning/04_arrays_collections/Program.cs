/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C# 학습 04단계: 배열과 컬렉션
  ─────────────────────────────────────────────────
  Array, List<T>, Dictionary<K,V>, HashSet<T>,
  Queue<T>, Stack<T>, LINQ 활용

  ■ 실행 방법: dotnet run (프로젝트 폴더에서)

  ■ 이 파일을 배우면 할 수 있는 것:
      - 여러 데이터를 한 번에 관리하기
      - 데이터를 빠르게 찾고 정렬하기
      - 상황에 맞는 컬렉션 선택하기

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

using System;
using System.Collections.Generic;
using System.Linq;

namespace ArraysAndCollections
{
    class Program
    {
        static void Main(string[] args)
        {
            // ════════════════════════════════════════════════
            //  1. 배열 (Array) - "같은 종류 데이터 보관함"
            // ════════════════════════════════════════════════

            /*
             * 배열이란 무엇인가요?
             * ────────────────────
             * 같은 종류의 데이터를 나란히 저장하는 그릇이에요.
             *
             * 마치 계란판처럼요!
             * 계란판의 각 칸에 번호가 있고 (0, 1, 2, 3...),
             * 각 칸에 계란(데이터)이 들어있어요.
             *
             * 특징:
             * - 크기가 고정됨 (한 번 만들면 크기 못 바꿔요)
             * - 인덱스(번호)로 빠르게 접근
             * - 인덱스는 항상 0부터 시작!
             *
             * ┌───┬───┬───┬───┬───┐
             * │ 0 │ 1 │ 2 │ 3 │ 4 │  ← 인덱스
             * ├───┼───┼───┼───┼───┤
             * │ 사 │ 바 │ 딸 │ 포 │ 수 │  ← 값
             * │ 과 │ 나 │ 기 │ 도 │ 박 │
             * └───┴───┴───┴───┴───┘
             */

            Console.WriteLine("══ 1. 배열 (1차원) ══\n");

            // 배열 선언 방법들
            // 방법 1: 크기만 정하기 (기본값으로 채워짐)
            int[] 성적 = new int[5];  // 5개 칸 (기본값 0)
            성적[0] = 90;
            성적[1] = 85;
            성적[2] = 78;
            성적[3] = 92;
            성적[4] = 88;

            // 방법 2: 값과 함께 초기화
            string[] 과일 = { "사과", "바나나", "딸기", "포도", "수박" };

            // 방법 3: new 키워드와 함께 초기화
            double[] 온도 = new double[] { 23.5, 25.0, 21.3, 28.7, 26.1 };

            // 배열 출력
            Console.WriteLine("성적 배열:");
            for (int i = 0; i < 성적.Length; i++)
            {
                Console.WriteLine($"  성적[{i}] = {성적[i]}점");
            }

            Console.WriteLine("\n과일 배열 (foreach):");
            foreach (string f in 과일)
            {
                Console.WriteLine($"  {f}");
            }

            // 배열 정보
            Console.WriteLine($"\n배열 길이: {성적.Length}개");
            Console.WriteLine($"첫 번째: {성적[0]}");
            Console.WriteLine($"마지막: {성적[성적.Length - 1]}");
            // C# 8+: ^1은 마지막에서 첫 번째
            Console.WriteLine($"마지막(^1): {성적[^1]}");

            // 배열 정렬
            int[] 무작위 = { 5, 2, 8, 1, 9, 3, 7, 4, 6 };
            Console.WriteLine("\n정렬 전: " + string.Join(", ", 무작위));
            Array.Sort(무작위);
            Console.WriteLine("오름차순: " + string.Join(", ", 무작위));
            Array.Reverse(무작위);
            Console.WriteLine("내림차순: " + string.Join(", ", 무작위));

            // 배열에서 찾기
            int 찾는값 = 7;
            int 인덱스 = Array.IndexOf(무작위, 찾는값);
            Console.WriteLine($"\n{찾는값}은 인덱스 {인덱스}에 있어요");

            Console.WriteLine("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

            // ════════════════════════════════════════════════
            //  2. 2차원 배열 - "바둑판 모양"
            // ════════════════════════════════════════════════

            /*
             * 2차원 배열이란?
             * ───────────────
             * 행(가로줄)과 열(세로줄)이 있는 표 모양이에요.
             *
             * 마치 학교 시간표처럼요!
             * 시간표[요일][교시]
             *
             *      1교시  2교시  3교시
             * 월요일  국어   수학   과학
             * 화요일  영어   미술   음악
             */

            Console.WriteLine("\n══ 2. 2차원 배열 ══\n");

            // 3행 4열 배열
            int[,] 점수표 = new int[3, 4]
            {
                { 90, 85, 78, 92 },  // 1행
                { 88, 91, 70, 85 },  // 2행
                { 75, 80, 95, 88 }   // 3행
            };

            Console.WriteLine("점수표:");
            Console.Write("      ");
            for (int j = 0; j < 4; j++)
                Console.Write($"수학{j+1}  ");
            Console.WriteLine();

            for (int i = 0; i < 3; i++)
            {
                Console.Write($"{i+1}학생: ");
                for (int j = 0; j < 4; j++)
                {
                    Console.Write($"{점수표[i, j],5}");
                }
                int 평균 = (점수표[i, 0] + 점수표[i, 1] + 점수표[i, 2] + 점수표[i, 3]) / 4;
                Console.WriteLine($"  (평균: {평균}점)");
            }

            Console.WriteLine($"\n배열 행 수: {점수표.GetLength(0)}");
            Console.WriteLine($"배열 열 수: {점수표.GetLength(1)}");

            Console.WriteLine("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

            // ════════════════════════════════════════════════
            //  3. List<T> - "늘어나는 배열"
            // ════════════════════════════════════════════════

            /*
             * List<T>란 무엇인가요?
             * ─────────────────────
             * 배열처럼 데이터를 순서대로 저장하지만,
             * 크기가 자동으로 늘어나고 줄어들어요!
             *
             * 마치 늘어나는 쇼핑 목록처럼요.
             * 처음엔 빈 목록이었다가,
             * 항목을 추가할수록 목록이 길어지죠.
             *
             * 배열과의 차이:
             * - 배열: 크기 고정 (5칸 만들면 5칸!)
             * - List: 크기 자동 조절 (필요하면 늘어남!)
             *
             * <T>는 제네릭이에요 (07단계에서 자세히 배워요)
             * T 자리에 int, string 등 타입을 쓰면 돼요.
             */

            Console.WriteLine("\n══ 3. List<T> ══\n");

            // List 만들기
            List<string> 쇼핑목록 = new List<string>();

            // 항목 추가
            쇼핑목록.Add("우유");
            쇼핑목록.Add("빵");
            쇼핑목록.Add("달걀");
            쇼핑목록.Add("버터");
            쇼핑목록.Add("사과");

            Console.WriteLine("쇼핑 목록:");
            foreach (string 항목 in 쇼핑목록)
                Console.WriteLine($"  □ {항목}");

            Console.WriteLine($"\n항목 수: {쇼핑목록.Count}개");

            // 특정 위치에 삽입
            쇼핑목록.Insert(2, "치즈");  // 인덱스 2에 삽입
            Console.WriteLine("\n'치즈' 추가 후:");
            for (int i = 0; i < 쇼핑목록.Count; i++)
                Console.WriteLine($"  [{i}] {쇼핑목록[i]}");

            // 항목 제거
            쇼핑목록.Remove("빵");           // 값으로 제거
            쇼핑목록.RemoveAt(0);            // 인덱스로 제거
            Console.WriteLine($"\n'빵'과 0번 항목 제거 후 남은 수: {쇼핑목록.Count}개");

            // 포함 여부 확인
            Console.WriteLine($"\n'달걀' 있나요? {쇼핑목록.Contains("달걀")}");
            Console.WriteLine($"'빵' 있나요? {쇼핑목록.Contains("빵")}");

            // 정렬
            쇼핑목록.Sort();
            Console.WriteLine("\n정렬된 목록:");
            쇼핑목록.ForEach(항목 => Console.WriteLine($"  {항목}"));

            // 초기값과 함께 만들기
            List<int> 점수들 = new List<int> { 95, 87, 73, 91, 68, 82 };
            Console.WriteLine($"\n점수 평균: {점수들.Average():F1}점");
            Console.WriteLine($"최고점: {점수들.Max()}점");
            Console.WriteLine($"합계: {점수들.Sum()}점");

            Console.WriteLine("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

            // ════════════════════════════════════════════════
            //  4. Dictionary<K,V> - "단어장 / 사전"
            // ════════════════════════════════════════════════

            /*
             * Dictionary란 무엇인가요?
             * ────────────────────────
             * 키(Key)와 값(Value)의 쌍으로 저장해요.
             *
             * 마치 진짜 사전처럼요!
             * "사과" → "apple"
             * "바나나" → "banana"
             *
             * 또는 전화번호부처럼요!
             * "김민준" → "010-1234-5678"
             *
             * 특징:
             * - 키로 값을 빠르게 찾을 수 있어요
             * - 키는 중복될 수 없어요 (유일해야 해요)
             * - 순서가 없어요 (순서가 중요하면 List 쓰세요)
             */

            Console.WriteLine("\n══ 4. Dictionary<K,V> ══\n");

            // 영어-한국어 사전
            Dictionary<string, string> 영한사전 = new Dictionary<string, string>();

            영한사전.Add("apple", "사과");
            영한사전.Add("banana", "바나나");
            영한사전.Add("cherry", "체리");
            영한사전["grape"] = "포도";         // [] 방식으로도 추가 가능
            영한사전["strawberry"] = "딸기";

            Console.WriteLine("영한 사전:");
            foreach (var 쌍 in 영한사전)
            {
                Console.WriteLine($"  {쌍.Key} → {쌍.Value}");
            }

            // 특정 키로 값 찾기
            string 찾을단어 = "banana";
            if (영한사전.ContainsKey(찾을단어))
            {
                Console.WriteLine($"\n'{찾을단어}'의 한국어: {영한사전[찾을단어]}");
            }

            // 안전하게 가져오기 (없어도 오류 안 남)
            if (영한사전.TryGetValue("mango", out string 번역))
            {
                Console.WriteLine($"mango = {번역}");
            }
            else
            {
                Console.WriteLine("\n'mango'는 사전에 없어요!");
            }

            // 학생 성적 관리
            Dictionary<string, int> 성적표 = new Dictionary<string, int>
            {
                { "김민준", 92 },
                { "이수진", 88 },
                { "박철수", 75 },
                { "최영희", 95 }
            };

            Console.WriteLine("\n성적표:");
            foreach (var 학생 in 성적표.OrderByDescending(s => s.Value))
            {
                Console.WriteLine($"  {학생.Key}: {학생.Value}점 ({등급매기기(학생.Value)}등급)");
            }

            // 키만, 값만 가져오기
            Console.WriteLine("\n학생 이름들:");
            foreach (string 이름 in 성적표.Keys)
                Console.Write($"{이름} ");
            Console.WriteLine();

            Console.WriteLine("점수들:");
            foreach (int 점수 in 성적표.Values)
                Console.Write($"{점수} ");
            Console.WriteLine();

            Console.WriteLine("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

            // ════════════════════════════════════════════════
            //  5. HashSet<T> - "중복 없는 집합"
            // ════════════════════════════════════════════════

            /*
             * HashSet이란 무엇인가요?
             * ────────────────────────
             * 같은 값을 두 번 저장하지 않아요!
             *
             * 마치 출석부처럼요.
             * 같은 이름이 두 번 올 수 없죠.
             *
             * 또는 주민등록번호처럼 유일한 값의 목록이에요.
             *
             * 사용 예:
             * - 중복 제거
             * - 특정 값이 있는지 빠른 확인
             * - 집합 연산 (합집합, 교집합, 차집합)
             */

            Console.WriteLine("\n══ 5. HashSet<T> ══\n");

            HashSet<string> 동아리원 = new HashSet<string>();

            동아리원.Add("김민준");
            동아리원.Add("이수진");
            동아리원.Add("박철수");
            동아리원.Add("김민준");  // 중복! 무시됨
            동아리원.Add("이수진");  // 중복! 무시됨
            동아리원.Add("최영희");

            Console.WriteLine("동아리 명단 (중복 제거됨):");
            foreach (string 이름 in 동아리원)
                Console.WriteLine($"  {이름}");
            Console.WriteLine($"총 {동아리원.Count}명");

            // 집합 연산
            HashSet<string> 수학반 = new HashSet<string> { "김민준", "이수진", "박철수", "정하늘" };
            HashSet<string> 과학반 = new HashSet<string> { "이수진", "박철수", "최영희", "홍길동" };

            // 교집합 (둘 다 있는 것)
            HashSet<string> 교집합 = new HashSet<string>(수학반);
            교집합.IntersectWith(과학반);
            Console.WriteLine("\n수학반 AND 과학반 (교집합):");
            foreach (string s in 교집합) Console.Write($"{s} ");
            Console.WriteLine();

            // 합집합 (모두 합치기)
            HashSet<string> 합집합 = new HashSet<string>(수학반);
            합집합.UnionWith(과학반);
            Console.WriteLine("수학반 OR 과학반 (합집합):");
            foreach (string s in 합집합) Console.Write($"{s} ");
            Console.WriteLine();

            // 차집합 (수학반에만 있는 것)
            HashSet<string> 차집합 = new HashSet<string>(수학반);
            차집합.ExceptWith(과학반);
            Console.WriteLine("수학반에만 있는 학생:");
            foreach (string s in 차집합) Console.Write($"{s} ");
            Console.WriteLine();

            Console.WriteLine("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

            // ════════════════════════════════════════════════
            //  6. Queue<T> - "줄 서기 (선입선출)"
            // ════════════════════════════════════════════════

            /*
             * Queue(큐)란 무엇인가요?
             * ────────────────────────
             * 먼저 들어온 것이 먼저 나가요 (FIFO: First In, First Out)
             *
             * 마치 편의점 계산대 줄처럼요!
             * 먼저 줄 선 사람이 먼저 계산해요.
             *
             * ← 나가기  ┌───┬───┬───┬───┐  ← 들어오기
             *           │ 1 │ 2 │ 3 │ 4 │
             *           └───┴───┴───┴───┘
             *           앞      →      뒤
             */

            Console.WriteLine("\n══ 6. Queue<T> (선입선출) ══\n");

            Queue<string> 계산대줄 = new Queue<string>();

            // Enqueue = 줄 끝에 추가
            계산대줄.Enqueue("김민준");
            계산대줄.Enqueue("이수진");
            계산대줄.Enqueue("박철수");
            계산대줄.Enqueue("최영희");

            Console.WriteLine("줄 상황:");
            foreach (string 고객 in 계산대줄)
                Console.Write($"[{고객}] → ");
            Console.WriteLine("계산대");

            // Dequeue = 맨 앞에서 꺼내기
            Console.WriteLine("\n계산 처리:");
            while (계산대줄.Count > 0)
            {
                string 현재고객 = 계산대줄.Dequeue();  // 앞에서 꺼냄
                Console.WriteLine($"  '{현재고객}' 고객 계산 완료! (남은 줄: {계산대줄.Count}명)");
            }

            // Peek = 꺼내지 않고 앞 항목 확인
            Queue<int> 숫자큐 = new Queue<int>(new[] { 10, 20, 30 });
            Console.WriteLine($"\n앞 항목 미리보기(Peek): {숫자큐.Peek()} (꺼내지 않음)");
            Console.WriteLine($"현재 크기: {숫자큐.Count}");

            Console.WriteLine("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

            // ════════════════════════════════════════════════
            //  7. Stack<T> - "접시 쌓기 (후입선출)"
            // ════════════════════════════════════════════════

            /*
             * Stack(스택)이란 무엇인가요?
             * ──────────────────────────
             * 나중에 들어온 것이 먼저 나가요 (LIFO: Last In, First Out)
             *
             * 마치 접시 쌓기처럼요!
             * 나중에 쌓은 접시를 먼저 꺼내죠.
             *
             * 또는 실행 취소(Ctrl+Z) 기능처럼요.
             * 가장 최근에 한 일을 먼저 취소해요.
             *
             *       ↑ 꺼내기 (Pop)
             *   ┌─────────┐
             *   │  4번째  │ ← 넣기 (Push)
             *   ├─────────┤
             *   │  3번째  │
             *   ├─────────┤
             *   │  2번째  │
             *   ├─────────┤
             *   │  1번째  │  (맨 처음 넣은 것)
             *   └─────────┘
             */

            Console.WriteLine("\n══ 7. Stack<T> (후입선출) ══\n");

            Stack<string> 실행취소기록 = new Stack<string>();

            // Push = 위에 쌓기
            실행취소기록.Push("글자 입력: '안녕'");
            실행취소기록.Push("글자 삭제");
            실행취소기록.Push("글자 입력: '하세요'");
            실행취소기록.Push("복사/붙여넣기");

            Console.WriteLine("현재 작업 기록 (위가 최근):");
            foreach (string 기록 in 실행취소기록)
                Console.WriteLine($"  📝 {기록}");

            Console.WriteLine("\n실행 취소 (Ctrl+Z) x2:");
            for (int i = 0; i < 2; i++)
            {
                string 취소된작업 = 실행취소기록.Pop();  // 맨 위에서 꺼냄
                Console.WriteLine($"  취소: {취소된작업}");
            }

            Console.WriteLine($"\n남은 기록 수: {실행취소기록.Count}개");

            // 괄호 짝 확인 (스택의 전통적인 활용)
            Console.WriteLine("\n── 괄호 짝 확인기 ──");
            string[] 수식들 = { "(1+2)*(3-4)", "((1+2)", "(1+(2*3))" };

            foreach (string 수식 in 수식들)
            {
                Console.WriteLine($"'{수식}' → {괄호확인(수식)}");
            }

            Console.WriteLine("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

            // ════════════════════════════════════════════════
            //  8. LINQ로 컬렉션 다루기
            // ════════════════════════════════════════════════

            Console.WriteLine("\n══ 8. LINQ 활용 ══\n");

            List<학생> 학생목록 = new List<학생>
            {
                new 학생 { 이름 = "김민준", 나이 = 12, 점수 = 92, 과목 = "수학" },
                new 학생 { 이름 = "이수진", 나이 = 11, 점수 = 88, 과목 = "과학" },
                new 학생 { 이름 = "박철수", 나이 = 13, 점수 = 75, 과목 = "수학" },
                new 학생 { 이름 = "최영희", 나이 = 12, 점수 = 95, 과목 = "영어" },
                new 학생 { 이름 = "정하늘", 나이 = 11, 점수 = 68, 과목 = "수학" },
                new 학생 { 이름 = "홍길동", 나이 = 13, 점수 = 83, 과목 = "과학" }
            };

            // Where - 조건으로 필터링
            Console.WriteLine("90점 이상 학생:");
            foreach (var s in 학생목록.Where(s => s.점수 >= 90))
                Console.WriteLine($"  {s.이름}: {s.점수}점");

            // OrderBy - 정렬
            Console.WriteLine("\n점수 순 정렬 (높은 순):");
            foreach (var s in 학생목록.OrderByDescending(s => s.점수))
                Console.WriteLine($"  {s.이름}: {s.점수}점");

            // Select - 변환
            Console.WriteLine("\n학생 이름만 추출:");
            var 이름목록 = 학생목록.Select(s => s.이름);
            Console.WriteLine(string.Join(", ", 이름목록));

            // GroupBy - 그룹 지어 묶기
            Console.WriteLine("\n과목별 학생 수:");
            var 과목별 = 학생목록.GroupBy(s => s.과목);
            foreach (var 그룹 in 과목별)
            {
                Console.WriteLine($"  {그룹.Key}: {그룹.Count()}명, 평균 {그룹.Average(s => s.점수):F1}점");
            }

            // 복합 LINQ
            Console.WriteLine("\n12살이고 80점 이상인 학생:");
            var 복합조건 = 학생목록
                .Where(s => s.나이 == 12 && s.점수 >= 80)
                .OrderBy(s => s.이름);
            foreach (var s in 복합조건)
                Console.WriteLine($"  {s.이름} ({s.나이}살): {s.점수}점");

            // ════════════════════════════════════════════════
            //  언제 어떤 컬렉션을 쓸까요?
            // ════════════════════════════════════════════════
            Console.WriteLine("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
            Console.WriteLine("📌 컬렉션 선택 가이드:");
            Console.WriteLine();
            Console.WriteLine("┌─────────────┬─────────────────────────────────────┐");
            Console.WriteLine("│ 컬렉션 타입  │ 언제 사용하나요?                     │");
            Console.WriteLine("├─────────────┼─────────────────────────────────────┤");
            Console.WriteLine("│ Array       │ 크기 고정, 빠른 인덱스 접근          │");
            Console.WriteLine("│ List<T>     │ 크기 가변, 순서 있는 목록            │");
            Console.WriteLine("│ Dictionary  │ 키-값 쌍, 빠른 검색                 │");
            Console.WriteLine("│ HashSet<T>  │ 중복 없는 집합, 포함 여부 확인      │");
            Console.WriteLine("│ Queue<T>    │ 선입선출 (대기열, 작업 큐)           │");
            Console.WriteLine("│ Stack<T>    │ 후입선출 (실행취소, 괄호 확인)      │");
            Console.WriteLine("└─────────────┴─────────────────────────────────────┘");

            Console.WriteLine("\n프로그램 종료. 아무 키나 누르세요...");
            Console.ReadKey();
        }

        // 괄호 짝 확인 메서드
        static string 괄호확인(string 수식)
        {
            Stack<char> 스택 = new Stack<char>();
            foreach (char c in 수식)
            {
                if (c == '(') 스택.Push(c);
                else if (c == ')')
                {
                    if (스택.Count == 0) return "짝 안 맞음!";
                    스택.Pop();
                }
            }
            return 스택.Count == 0 ? "짝 맞음!" : "여는 괄호 더 많음!";
        }

        // 등급 매기기 헬퍼
        static string 등급매기기(int 점수)
        {
            if (점수 >= 90) return "A";
            if (점수 >= 80) return "B";
            if (점수 >= 70) return "C";
            return "D";
        }
    }

    // 데이터 클래스 (05단계에서 자세히!)
    class 학생
    {
        public string 이름 { get; set; } = "";
        public int 나이 { get; set; }
        public int 점수 { get; set; }
        public string 과목 { get; set; } = "";
    }
}
