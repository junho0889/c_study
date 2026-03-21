/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C# 학습 02단계: 흐름 제어
  ─────────────────────────────────────────────────
  if/else, switch, for, while, foreach, break, continue

  ■ 실행 방법: dotnet run (프로젝트 폴더에서)

  ■ 이 파일을 배우면 할 수 있는 것:
      - 조건에 따라 다르게 행동하기
      - 반복 작업 자동화하기
      - 특정 상황에서 멈추거나 건너뛰기

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

using System;
using System.Collections.Generic;
using System.Linq;

namespace ControlFlow
{
    class Program
    {
        static void Main(string[] args)
        {
            // ════════════════════════════════════════════════
            //  1. if / else if / else - "갈림길에서 선택하기"
            // ════════════════════════════════════════════════

            /*
             * if문이란 무엇인가요?
             * ────────────────────
             * "만약에..." 라는 조건을 달아서
             * 조건이 맞으면 한 가지 일을 하고,
             * 아니면 다른 일을 하는 거예요.
             *
             * 실생활 예시:
             * "만약에 비가 오면 → 우산을 가져가요"
             * "그렇지 않으면   → 우산은 집에 두어요"
             *
             * 코드 구조:
             * if (조건) {
             *     // 조건이 참일 때 실행
             * } else {
             *     // 조건이 거짓일 때 실행
             * }
             */

            Console.WriteLine("══ 1. if/else 문 ══\n");

            int 점수 = 85;

            // 기본 if-else
            if (점수 >= 60)
            {
                Console.WriteLine($"{점수}점: 합격입니다! 축하해요!");
            }
            else
            {
                Console.WriteLine($"{점수}점: 아쉽지만 불합격이에요.");
            }

            // if - else if - else (여러 조건 사다리)
            // 마치 학교 성적표 등급 매기기처럼요!
            Console.WriteLine();
            if (점수 >= 90)
            {
                Console.WriteLine($"{점수}점 → A등급 (최우수)");
            }
            else if (점수 >= 80)
            {
                Console.WriteLine($"{점수}점 → B등급 (우수)");
            }
            else if (점수 >= 70)
            {
                Console.WriteLine($"{점수}점 → C등급 (보통)");
            }
            else if (점수 >= 60)
            {
                Console.WriteLine($"{점수}점 → D등급 (미흡)");
            }
            else
            {
                Console.WriteLine($"{점수}점 → F등급 (불합격)");
            }

            // 비교 연산자들
            /*
             * ==  : 같다     (5 == 5 → true)
             * !=  : 다르다   (5 != 3 → true)
             * >   : 크다     (5 > 3  → true)
             * <   : 작다     (3 < 5  → true)
             * >=  : 크거나같다 (5 >= 5 → true)
             * <=  : 작거나같다 (3 <= 5 → true)
             */

            // 논리 연산자
            /*
             * &&  : 그리고 (AND) - 둘 다 참이어야 참
             * ||  : 또는  (OR)  - 하나만 참이어도 참
             * !   : 아니다 (NOT) - 참을 거짓으로, 거짓을 참으로
             *
             * 예시:
             * 비가 오고 AND 우산이 없으면 → 옷이 젖어요
             * 비가 오거나 OR 눈이 오면  → 우산 챙겨요
             */

            int 나이 = 12;
            bool 회원 = true;

            Console.WriteLine();
            if (나이 >= 10 && 나이 <= 13)
            {
                Console.WriteLine($"{나이}살: 초등학교 고학년이에요!");
            }

            if (나이 < 7 || 나이 > 18)
            {
                Console.WriteLine("학교에 다니지 않아요.");
            }
            else
            {
                Console.WriteLine("학교에 다니는 나이예요!");
            }

            if (!회원)
            {
                Console.WriteLine("회원이 아니에요. 가입해 주세요!");
            }
            else
            {
                Console.WriteLine("환영합니다! 회원이시군요!");
            }

            // 삼항 연산자 (조건 ? 참일때 : 거짓일때)
            // 짧게 쓰는 if-else예요!
            string 결과 = 점수 >= 60 ? "합격" : "불합격";
            Console.WriteLine($"\n삼항 연산자: {점수}점 → {결과}");

            Console.WriteLine("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

            // ════════════════════════════════════════════════
            //  2. switch 문 - "메뉴 선택기"
            // ════════════════════════════════════════════════

            /*
             * switch문이란 무엇인가요?
             * ────────────────────────
             * 여러 선택지 중 하나를 고르는 것처럼,
             * 값에 따라 다른 코드를 실행해요.
             *
             * 마치 식당 메뉴판처럼:
             * 1번 → 짜장면
             * 2번 → 짬뽕
             * 3번 → 탕수육
             * 기타 → "없는 메뉴예요"
             */

            Console.WriteLine("\n══ 2. switch 문 ══\n");

            int 메뉴선택 = 2;

            // 전통적인 switch 문
            switch (메뉴선택)
            {
                case 1:
                    Console.WriteLine("짜장면을 선택했어요!");
                    break;  // 여기서 switch 밖으로 나가요
                case 2:
                    Console.WriteLine("짬뽕을 선택했어요!");
                    break;
                case 3:
                    Console.WriteLine("탕수육을 선택했어요!");
                    break;
                default:  // 아무것도 해당 안 될 때
                    Console.WriteLine("없는 메뉴예요.");
                    break;
            }

            // 여러 case 묶기
            int 월 = 7;
            switch (월)
            {
                case 3:
                case 4:
                case 5:
                    Console.WriteLine($"{월}월은 봄이에요 🌸");
                    break;
                case 6:
                case 7:
                case 8:
                    Console.WriteLine($"{월}월은 여름이에요 ☀");
                    break;
                case 9:
                case 10:
                case 11:
                    Console.WriteLine($"{월}월은 가을이에요 🍂");
                    break;
                default:
                    Console.WriteLine($"{월}월은 겨울이에요 ❄");
                    break;
            }

            // C# 8+ switch 표현식 (더 깔끔한 방법!)
            string 계절 = 월 switch
            {
                3 or 4 or 5 => "봄",
                6 or 7 or 8 => "여름",
                9 or 10 or 11 => "가을",
                12 or 1 or 2 => "겨울",
                _ => "알 수 없음"  // _ 는 default와 같아요
            };
            Console.WriteLine($"{월}월의 계절: {계절}");

            // 문자열 switch
            string 요일 = "월요일";
            string 학교여부 = 요일 switch
            {
                "월요일" or "화요일" or "수요일" or "목요일" or "금요일" => "학교 가는 날!",
                "토요일" or "일요일" => "주말이에요!",
                _ => "알 수 없는 요일"
            };
            Console.WriteLine($"{요일}: {학교여부}");

            Console.WriteLine("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

            // ════════════════════════════════════════════════
            //  3. for 반복문 - "정해진 횟수만큼 반복"
            // ════════════════════════════════════════════════

            /*
             * for문이란 무엇인가요?
             * ─────────────────────
             * "몇 번 반복할지 정해두고 반복"하는 거예요.
             *
             * for (시작; 조건; 매번 할 일) {
             *     반복할 내용
             * }
             *
             * 마치 운동할 때:
             * for (횟수 = 1; 횟수 <= 10; 횟수++) {
             *     팔굽혀펴기 한 번!
             * }
             *
             * 이렇게 정확히 10번 하는 것처럼요.
             */

            Console.WriteLine("\n══ 3. for 반복문 ══\n");

            // 기본 for 반복
            Console.WriteLine("1부터 5까지:");
            for (int i = 1; i <= 5; i++)
            {
                Console.Write($"{i} ");
            }
            Console.WriteLine();

            // 역순 반복
            Console.WriteLine("카운트다운:");
            for (int i = 5; i >= 1; i--)
            {
                Console.Write($"{i} ");
            }
            Console.WriteLine("발사!");

            // 구구단 만들기!
            int 단 = 3;
            Console.WriteLine($"\n{단}단 구구단:");
            for (int i = 1; i <= 9; i++)
            {
                Console.WriteLine($"  {단} × {i} = {단 * i}");
            }

            // 중첩 for 반복 (for 안에 for)
            Console.WriteLine("\n별 삼각형 만들기:");
            for (int 행 = 1; 행 <= 5; 행++)
            {
                for (int 열 = 1; 열 <= 행; 열++)
                {
                    Console.Write("★ ");
                }
                Console.WriteLine();
            }

            // 2차원처럼 출력
            Console.WriteLine("\n구구단 전체 (2단~9단):");
            for (int 단번호 = 2; 단번호 <= 9; 단번호++)
            {
                Console.Write($"{단번호}단: ");
                for (int 곱하는수 = 1; 곱하는수 <= 9; 곱하는수++)
                {
                    Console.Write($"{단번호 * 곱하는수,3}");  // ,3 = 3칸 너비로 맞춤
                }
                Console.WriteLine();
            }

            Console.WriteLine("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

            // ════════════════════════════════════════════════
            //  4. foreach 반복문 - "모든 것을 하나씩 꺼내기"
            // ════════════════════════════════════════════════

            /*
             * foreach란 무엇인가요?
             * ─────────────────────
             * "컬렉션(목록)에서 하나씩 꺼내서 처리"해요.
             *
             * 마치 사탕 봉지에서 사탕을 하나씩 꺼내
             * 색깔을 확인하는 것과 같아요!
             *
             * foreach (항목 in 목록) {
             *     항목으로 할 일
             * }
             */

            Console.WriteLine("\n══ 4. foreach 반복문 ══\n");

            // 배열 순회
            string[] 과일들 = { "사과", "바나나", "딸기", "포도", "수박" };

            Console.WriteLine("과일 목록:");
            foreach (string 과일 in 과일들)
            {
                Console.WriteLine($"  🍎 {과일}");
            }

            // 숫자 배열 합계
            int[] 숫자들 = { 10, 20, 30, 40, 50 };
            int 합계 = 0;
            foreach (int 숫자 in 숫자들)
            {
                합계 += 숫자;
            }
            Console.WriteLine($"\n숫자들의 합: {합계}");

            // 문자열의 각 글자 순회
            string 단어 = "안녕하세요";
            Console.WriteLine($"\n'{단어}'의 각 글자:");
            foreach (char 글자 in 단어)
            {
                Console.Write($"[{글자}] ");
            }
            Console.WriteLine();

            Console.WriteLine("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

            // ════════════════════════════════════════════════
            //  5. while 반복문 - "조건이 맞는 동안 계속"
            // ════════════════════════════════════════════════

            /*
             * while이란 무엇인가요?
             * ─────────────────────
             * "조건이 참인 동안 계속 반복"해요.
             *
             * 마치 배가 고픈 동안 계속 밥을 먹는 것처럼요.
             * (배가 부르면 멈추죠!)
             *
             * while (배가 고프다) {
             *     밥 먹기
             * }
             *
             * ⚠ 주의: 조건이 절대 false가 되지 않으면
             *          영원히 반복하는 "무한 루프"가 돼요!
             */

            Console.WriteLine("\n══ 5. while 반복문 ══\n");

            // 기본 while
            int 카운터 = 1;
            Console.WriteLine("while로 1~5 출력:");
            while (카운터 <= 5)
            {
                Console.Write($"{카운터} ");
                카운터++;  // 이걸 빼면 무한 루프! 꼭 증가시켜줘야 해요!
            }
            Console.WriteLine();

            // 사용자 입력 받아서 반복 (실제로는 테스트용으로 미리 값 설정)
            Console.WriteLine("\n숫자 맞추기 게임 시뮬레이션:");
            int 정답 = 7;
            int[] 시도들 = { 3, 5, 9, 7 };  // 실제로는 Console.ReadLine() 사용
            int 시도인덱스 = 0;

            while (시도인덱스 < 시도들.Length)
            {
                int 시도값 = 시도들[시도인덱스];
                Console.Write($"  시도: {시도값} → ");

                if (시도값 == 정답)
                {
                    Console.WriteLine("정답! 게임 종료!");
                    break;
                }
                else if (시도값 < 정답)
                {
                    Console.WriteLine("더 큰 숫자예요!");
                }
                else
                {
                    Console.WriteLine("더 작은 숫자예요!");
                }
                시도인덱스++;
            }

            Console.WriteLine("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

            // ════════════════════════════════════════════════
            //  6. do-while - "일단 하고 나서 조건 확인"
            // ════════════════════════════════════════════════

            /*
             * do-while이란 무엇인가요?
             * ────────────────────────
             * while과 비슷하지만,
             * 조건 확인 전에 일단 한 번은 실행해요.
             *
             * 마치 음식을 먼저 맛보고
             * "맛있으면 더 먹자!"를 결정하는 것처럼요.
             *
             * do {
             *     실행할 내용 (최소 1번은 실행됨!)
             * } while (조건);
             */

            Console.WriteLine("\n══ 6. do-while 반복문 ══\n");

            int 실행횟수 = 0;
            do
            {
                Console.WriteLine($"  실행 #{실행횟수 + 1}: do-while은 한 번은 꼭 실행해요!");
                실행횟수++;
            } while (실행횟수 < 3);

            // while과 do-while의 차이 비교
            Console.WriteLine("\nwhile vs do-while 비교 (처음부터 조건이 false일 때):");

            int w = 10;
            Console.Write("while: ");
            while (w < 5)  // 처음부터 false
            {
                Console.Write("실행됨 ");
            }
            Console.WriteLine("(실행 안 됨)");

            int d = 10;
            Console.Write("do-while: ");
            do
            {
                Console.Write("한 번은 실행됨! ");
                d++;
            } while (d < 5);  // 처음부터 false지만 이미 한 번 실행 후 확인
            Console.WriteLine();

            Console.WriteLine("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

            // ════════════════════════════════════════════════
            //  7. break와 continue - "반복 조종하기"
            // ════════════════════════════════════════════════

            /*
             * break = "반복문 탈출!"
             * ─────────────────────
             * 마치 수업 시간에 갑자기 비상벨이 울리면
             * 수업을 멈추고 나가는 것처럼요.
             *
             * continue = "이번 건 건너뛰고 다음으로!"
             * ────────────────────────────────────────
             * 마치 과일 주스 만들 때 상한 과일은 건너뛰고
             * 다음 과일을 사용하는 것처럼요.
             */

            Console.WriteLine("\n══ 7. break와 continue ══\n");

            // break 예시
            Console.WriteLine("break - 5를 만나면 멈춰요:");
            for (int i = 1; i <= 10; i++)
            {
                if (i == 5)
                {
                    Console.WriteLine($"  {i}에서 break!");
                    break;
                }
                Console.Write($"{i} ");
            }
            Console.WriteLine();

            // continue 예시
            Console.WriteLine("\ncontinue - 짝수는 건너뛰어요:");
            for (int i = 1; i <= 10; i++)
            {
                if (i % 2 == 0)
                {
                    continue;  // 짝수면 건너뜀
                }
                Console.Write($"{i} ");  // 홀수만 출력
            }
            Console.WriteLine();

            // 실용적인 예: 배열에서 특정 값 찾기
            int[] 성적들 = { 85, 70, 55, 92, 45, 88, 60 };
            Console.WriteLine("\n60점 미만인 낙제 점수 (건너뜀):");
            foreach (int 성적 in 성적들)
            {
                if (성적 < 60)
                {
                    Console.Write($"[{성적}낙제] ");
                    continue;
                }
                Console.Write($"{성적} ");
            }
            Console.WriteLine();

            // 첫 번째 90점 이상 찾기
            Console.WriteLine("\n처음으로 90점 이상인 점수 찾기:");
            foreach (int 성적 in 성적들)
            {
                if (성적 >= 90)
                {
                    Console.WriteLine($"  찾았어요! {성적}점");
                    break;
                }
            }

            Console.WriteLine("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

            // ════════════════════════════════════════════════
            //  8. 실전 예제 - FizzBuzz 게임
            // ════════════════════════════════════════════════

            /*
             * FizzBuzz 규칙:
             * 1~30 숫자를 출력하되,
             * 3의 배수면 "Fizz"
             * 5의 배수면 "Buzz"
             * 15의 배수면 "FizzBuzz"
             * 나머지는 숫자 그대로
             *
             * 유명한 프로그래밍 면접 문제예요!
             */

            Console.WriteLine("\n══ FizzBuzz 게임 (1~30) ══\n");

            for (int i = 1; i <= 30; i++)
            {
                if (i % 15 == 0)      // 15의 배수 먼저 확인!
                    Console.Write("FizzBuzz ");
                else if (i % 3 == 0)  // 3의 배수
                    Console.Write("Fizz ");
                else if (i % 5 == 0)  // 5의 배수
                    Console.Write("Buzz ");
                else
                    Console.Write($"{i} ");
            }
            Console.WriteLine();

            Console.WriteLine("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

            // ════════════════════════════════════════════════
            //  9. LINQ 미리보기 - 컬렉션 다루는 강력한 도구
            // ════════════════════════════════════════════════

            /*
             * LINQ(링크)란 무엇인가요?
             * ─────────────────────────
             * 목록(컬렉션)에서 원하는 것을 쉽게 찾고,
             * 정렬하고, 변환하는 도구예요.
             *
             * 마치 도서관에서:
             * "제목에 '모험'이 들어간 책들을 찾아줘"
             * "작가 이름 순으로 정렬해줘"
             * 같은 요청을 코드로 하는 거예요!
             */

            Console.WriteLine("\n══ 9. LINQ 미리보기 ══\n");

            int[] 숫자배열 = { 1, 5, 3, 8, 2, 9, 4, 7, 6, 10 };

            // Where = 조건에 맞는 것만 골라내기
            var 짝수들 = 숫자배열.Where(n => n % 2 == 0);
            Console.Write("짝수만: ");
            foreach (var n in 짝수들) Console.Write($"{n} ");
            Console.WriteLine();

            // OrderBy = 정렬
            var 정렬됨 = 숫자배열.OrderBy(n => n);
            Console.Write("오름차순: ");
            foreach (var n in 정렬됨) Console.Write($"{n} ");
            Console.WriteLine();

            // 조건에 맞는 첫 번째 요소
            int 첫번째짝수 = 숫자배열.First(n => n % 2 == 0);
            Console.WriteLine($"첫 번째 짝수: {첫번째짝수}");

            // 개수 세기
            int 짝수개수 = 숫자배열.Count(n => n % 2 == 0);
            Console.WriteLine($"짝수 개수: {짝수개수}개");

            // 합계, 최댓값, 최솟값
            Console.WriteLine($"합계: {숫자배열.Sum()}");
            Console.WriteLine($"최댓값: {숫자배열.Max()}");
            Console.WriteLine($"최솟값: {숫자배열.Min()}");
            Console.WriteLine($"평균: {숫자배열.Average():F1}");

            // ════════════════════════════════════════════════
            //  자주 하는 실수들!
            // ════════════════════════════════════════════════

            Console.WriteLine("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
            Console.WriteLine("⚠ 자주 하는 실수들:");
            Console.WriteLine();
            Console.WriteLine("1. switch에서 break 빠뜨리기");
            Console.WriteLine("   → 다음 case까지 실행됨 (의도치 않은 결과)");
            Console.WriteLine();
            Console.WriteLine("2. while 무한 루프");
            Console.WriteLine("   → 루프 변수를 바꾸지 않으면 영원히 실행!");
            Console.WriteLine("   → Ctrl+C 로 강제 종료할 수 있어요");
            Console.WriteLine();
            Console.WriteLine("3. for 반복문 인덱스 범위 초과");
            Console.WriteLine("   → for(i=0; i<=배열.Length; i++) ← 틀림!");
            Console.WriteLine("   → for(i=0; i<배열.Length; i++)  ← 맞음!");

            Console.WriteLine("\n프로그램 종료. 아무 키나 누르세요...");
            Console.ReadKey();
        }
    }
}
