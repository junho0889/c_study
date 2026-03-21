/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Java 학습 02단계: 제어 흐름
  ─ if/else, switch, for, while, break, continue ─

  ■ 컴파일: javac Main.java
  ■ 실행:   java Main

  프로그램은 항상 위에서 아래로 실행돼요.
  하지만 "조건"에 따라 다른 길로 갈 수 있어요!
  마치 길을 걷다가 신호등이 빨간불이면 멈추고,
  초록불이면 걷는 것처럼요!

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

public class Main {

    public static void main(String[] args) {

        // ═══════════════════════════════════════════════════
        //  섹션 1: if / else if / else - 조건에 따라 결정!
        // ═══════════════════════════════════════════════════

        /*
         * if 문이란?
         *
         * "만약 ~라면, ~해라" 라는 뜻이에요.
         * 일상에서도 항상 쓰는 말이죠!
         * "만약 비가 오면 우산을 챙겨라"
         * "만약 배가 고프면 밥을 먹어라"
         *
         * if (조건) {
         *     // 조건이 true일 때 실행
         * } else if (다른조건) {
         *     // 앞 조건은 false이고 이 조건이 true일 때
         * } else {
         *     // 모든 조건이 false일 때 (기본값)
         * }
         */

        System.out.println("=== if/else 조건문 ===");

        // 점수에 따른 학점 결정
        int score = 85;
        System.out.println("점수: " + score + "점");

        if (score >= 90) {
            // score가 90 이상이면 여기 실행
            System.out.println("학점: A (아주 훌륭해요!)");
        } else if (score >= 80) {
            // score가 80~89면 여기 실행
            System.out.println("학점: B (잘했어요!)");
        } else if (score >= 70) {
            // score가 70~79면 여기 실행
            System.out.println("학점: C (조금 더 노력해요!)");
        } else if (score >= 60) {
            // score가 60~69면 여기 실행
            System.out.println("학점: D (많이 노력해야 해요!)");
        } else {
            // 60 미만이면 여기 실행
            System.out.println("학점: F (다시 공부해야 해요...)");
        }

        // 비교 연산자 정리
        System.out.println("\n비교 연산자 예제:");
        int x = 10, y = 20;
        System.out.println("x = " + x + ", y = " + y);
        System.out.println("x == y (같다): " + (x == y));     // false
        System.out.println("x != y (다르다): " + (x != y));   // true
        System.out.println("x > y (크다): " + (x > y));       // false
        System.out.println("x < y (작다): " + (x < y));       // true
        System.out.println("x >= y (크거나 같다): " + (x >= y)); // false
        System.out.println("x <= y (작거나 같다): " + (x <= y)); // true

        // 논리 연산자
        System.out.println("\n논리 연산자 예제:");
        boolean isSunny = true;
        boolean isWarm = false;
        // && (AND) - 두 조건 모두 true여야 true
        // 마치 "날씨도 좋고 따뜻해야 소풍 가자" 처럼요
        System.out.println("맑음 && 따뜻함: " + (isSunny && isWarm));  // false
        // || (OR) - 둘 중 하나만 true여도 true
        // 마치 "날씨가 좋거나 따뜻하면 나가자" 처럼요
        System.out.println("맑음 || 따뜻함: " + (isSunny || isWarm));  // true
        // ! (NOT) - true를 false로, false를 true로
        System.out.println("!맑음: " + (!isSunny));  // false

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 2: 삼항 연산자 (Ternary Operator)
        // ═══════════════════════════════════════════════════

        /*
         * 삼항 연산자란?
         *
         * if-else를 한 줄로 줄여서 쓰는 방법이에요!
         * "조건 ? 참일때값 : 거짓일때값"
         *
         * 마치 친구에게 "사탕 먹을래? 먹으면 행복, 안 먹으면 아쉬워"
         * 처럼 "?"를 기준으로 두 가지 결과가 나와요.
         */

        System.out.println("=== 삼항 연산자 ===");

        int myScore = 75;
        // if-else 방식
        String result1;
        if (myScore >= 60) {
            result1 = "합격";
        } else {
            result1 = "불합격";
        }

        // 삼항 연산자 방식 (훨씬 짧아요!)
        String result2 = (myScore >= 60) ? "합격" : "불합격";

        System.out.println("if-else 방식: " + result1);
        System.out.println("삼항 연산자 방식: " + result2);

        // 삼항 연산자 활용 예시
        int num = 7;
        String evenOdd = (num % 2 == 0) ? "짝수" : "홀수";
        System.out.println(num + "은 " + evenOdd + "입니다.");

        int temp = 25;
        String weather = (temp >= 30) ? "더워요" : (temp >= 20) ? "따뜻해요" : "추워요";
        System.out.println("온도 " + temp + "도: " + weather);

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 3: switch/case - 여러 경우 중 하나!
        // ═══════════════════════════════════════════════════

        /*
         * switch 문이란?
         *
         * if-else가 "신호등"이라면, switch는 "여러 문이 있는 복도"예요.
         * 값에 따라 딱 맞는 문으로 들어가요!
         *
         * 예: 오늘 요일이 뭐야?
         * 월요일 → 국어 수업
         * 화요일 → 수학 수업
         * 수요일 → 과학 수업
         * ...
         */

        System.out.println("=== switch/case (기존 방식) ===");

        int dayNumber = 3;  // 1=월, 2=화, 3=수, 4=목, 5=금, 6=토, 7=일
        String dayName;

        switch (dayNumber) {
            case 1:
                dayName = "월요일";
                break;  // break가 없으면 다음 case도 실행돼요! (fall-through)
            case 2:
                dayName = "화요일";
                break;
            case 3:
                dayName = "수요일";
                break;
            case 4:
                dayName = "목요일";
                break;
            case 5:
                dayName = "금요일";
                break;
            case 6:
                dayName = "토요일";
                break;
            case 7:
                dayName = "일요일";
                break;
            default:
                // 1~7 외의 값이 오면 여기 실행 (else와 같은 역할)
                dayName = "알 수 없는 날";
        }
        System.out.println("오늘은 " + dayName + "이에요.");

        // 여러 case를 한꺼번에 처리하기
        System.out.println("\n여러 case 묶기:");
        String dayType;
        switch (dayNumber) {
            case 1:
            case 2:
            case 3:
            case 4:
            case 5:
                // 1,2,3,4,5 모두 여기로 와요
                dayType = "평일 (학교 가는 날!)";
                break;
            case 6:
            case 7:
                // 6,7 모두 여기로 와요
                dayType = "주말 (신나는 날!)";
                break;
            default:
                dayType = "모름";
        }
        System.out.println(dayNumber + "번째 날은 " + dayType);

        // ── 향상된 switch (Java 14+) ─────────────────────

        /*
         * 향상된 switch 문 (Enhanced Switch)
         *
         * Java 14부터 새로운 방식의 switch가 생겼어요!
         * -> 를 사용해서 더 간결하게 쓸 수 있어요.
         * break도 필요 없어요! (자동으로 끝나요)
         */

        System.out.println("\n=== 향상된 switch (Java 14+) ===");

        int season = 3;  // 1=봄, 2=여름, 3=가을, 4=겨울
        String seasonName = switch (season) {
            case 1 -> "봄 - 꽃이 피어요!";
            case 2 -> "여름 - 수영하기 좋아요!";
            case 3 -> "가을 - 단풍이 예뻐요!";
            case 4 -> "겨울 - 눈싸움 해요!";
            default -> "알 수 없는 계절";
        };
        System.out.println("계절: " + seasonName);

        // 문자열로 switch하기
        System.out.println("\n문자열 switch 예제:");
        String fruit = "사과";
        String fruitColor = switch (fruit) {
            case "사과" -> "빨간색";
            case "바나나" -> "노란색";
            case "포도" -> "보라색";
            case "수박" -> "초록색 (속은 빨간색!)";
            default -> "모르는 색";
        };
        System.out.println(fruit + "의 색깔: " + fruitColor);

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 4: for 반복문
        // ═══════════════════════════════════════════════════

        /*
         * for 반복문이란?
         *
         * 같은 일을 여러 번 반복할 때 써요!
         * 마치 "운동장을 10바퀴 달려라!"라고 할 때
         * 1바퀴, 2바퀴, 3바퀴... 10바퀴를 세는 것처럼요!
         *
         * for (시작; 조건; 증가) {
         *     // 반복할 내용
         * }
         *
         * 시작: i = 1 (첫 바퀴 시작!)
         * 조건: i <= 10 (10바퀴 이하일 때 계속)
         * 증가: i++ (한 바퀴 돌았으니 1 증가)
         */

        System.out.println("=== for 반복문 ===");

        // 1부터 10까지 출력
        System.out.print("1부터 10까지: ");
        for (int i = 1; i <= 10; i++) {
            System.out.print(i + " ");
        }
        System.out.println();

        // 1부터 100까지 합계
        int sum = 0;
        for (int i = 1; i <= 100; i++) {
            sum += i;  // sum = sum + i
        }
        System.out.println("1~100 합계: " + sum);

        // 짝수만 출력
        System.out.print("1~20 중 짝수: ");
        for (int i = 2; i <= 20; i += 2) {  // i를 2씩 증가
            System.out.print(i + " ");
        }
        System.out.println();

        // 거꾸로 세기
        System.out.print("10부터 1까지: ");
        for (int i = 10; i >= 1; i--) {  // i를 1씩 감소
            System.out.print(i + " ");
        }
        System.out.println();

        // 구구단 3단
        System.out.println("\n구구단 3단:");
        for (int i = 1; i <= 9; i++) {
            System.out.printf("3 × %d = %d%n", i, 3 * i);
        }

        // 별 삼각형 그리기 (이중 for 루프)
        System.out.println("\n별 삼각형:");
        for (int i = 1; i <= 5; i++) {
            for (int j = 1; j <= i; j++) {
                System.out.print("★");
            }
            System.out.println();
        }

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 5: for-each 반복문 (향상된 for)
        // ═══════════════════════════════════════════════════

        /*
         * for-each 반복문이란?
         *
         * 배열이나 목록의 모든 항목을 하나씩 꺼내서 볼 때 써요!
         * 마치 선생님이 출석부를 보면서
         * "첫 번째 학생... 두 번째 학생..." 하는 것처럼요!
         *
         * for (자료형 변수 : 배열/컬렉션) {
         *     // 각 항목으로 할 일
         * }
         */

        System.out.println("=== for-each 반복문 ===");

        String[] animals = {"강아지", "고양이", "토끼", "햄스터", "금붕어"};
        System.out.println("동물 목록:");
        for (String animal : animals) {
            // animal에 배열의 각 항목이 순서대로 들어와요
            System.out.println("  🐾 " + animal);
        }

        int[] scores = {90, 85, 78, 92, 88};
        int total = 0;
        for (int s : scores) {
            total += s;
        }
        System.out.println("점수 합계: " + total);
        System.out.println("평균 점수: " + (double)total / scores.length + "점");

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 6: while 반복문
        // ═══════════════════════════════════════════════════

        /*
         * while 반복문이란?
         *
         * "조건이 참인 동안 계속 반복"해요.
         * 마치 "배가 부를 때까지 밥을 먹어라"처럼요!
         * 언제 끝날지 정확히 모를 때 많이 써요.
         *
         * while (조건) {
         *     // 반복할 내용
         * }
         */

        System.out.println("=== while 반복문 ===");

        // 10 이하인 동안 계속 더하기
        int whileCount = 1;
        int whileSum = 0;
        while (whileCount <= 10) {
            whileSum += whileCount;
            whileCount++;
        }
        System.out.println("while로 1~10 합계: " + whileSum);

        // 2를 계속 곱해서 1000을 넘을 때까지
        System.out.println("\n2를 계속 곱하기 (1000 넘을 때까지):");
        int value = 1;
        int multiplyCount = 0;
        while (value <= 1000) {
            System.out.print(value + " → ");
            value *= 2;
            multiplyCount++;
        }
        System.out.println(value);
        System.out.println(multiplyCount + "번 곱했어요!");

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 7: do-while 반복문
        // ═══════════════════════════════════════════════════

        /*
         * do-while 반복문이란?
         *
         * while과 비슷하지만, 조건 확인 전에 일단 한 번 실행해요!
         * "일단 해보고, 그 다음에 계속할지 결정해요"
         *
         * 마치 음식을 먹어보고 나서 "맛있으면 더 먹을게요" 처럼요.
         * 무조건 한 번은 먹어봐요!
         *
         * do {
         *     // 무조건 한 번은 실행
         * } while (조건);  // 이후 조건 확인
         */

        System.out.println("=== do-while 반복문 ===");

        int doNum = 1;
        System.out.println("do-while로 1~5 출력:");
        do {
            System.out.print(doNum + " ");
            doNum++;
        } while (doNum <= 5);
        System.out.println();

        // do-while vs while 차이
        System.out.println("\ndo-while vs while 차이 (조건이 처음부터 false인 경우):");

        int wNum = 10;
        System.out.print("while (처음부터 false): ");
        while (wNum < 5) {  // 처음부터 false → 한 번도 실행 안 해요
            System.out.print(wNum + " ");
        }
        System.out.println("(아무것도 출력 안 됨)");

        int dwNum = 10;
        System.out.print("do-while (처음부터 false): ");
        do {
            System.out.print(dwNum + " ");  // 조건 확인 전에 일단 한 번 실행!
            dwNum++;
        } while (dwNum < 5);  // false → 한 번만 실행하고 끝
        System.out.println("(10 한 번 출력됨)");

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 8: break와 continue
        // ═══════════════════════════════════════════════════

        /*
         * break - 반복문 완전히 탈출!
         *
         * 마치 운동장 달리기 중에 선생님이 "그만!"하면
         * 더 달리지 않고 완전히 멈추는 것처럼요!
         *
         * continue - 이번 반복만 건너뛰기!
         *
         * 마치 달리기 중에 돌이 있어서 그 구간만 건너뛰고
         * 계속 달리는 것처럼요!
         */

        System.out.println("=== break와 continue ===");

        // break 예제
        System.out.println("break 예제 (5가 나오면 멈추기):");
        for (int i = 1; i <= 10; i++) {
            if (i == 5) {
                System.out.println("  5 발견! 멈춰요!");
                break;  // for 루프 완전히 탈출
            }
            System.out.println("  " + i);
        }
        System.out.println("반복문 끝");

        // continue 예제
        System.out.println("\ncontinue 예제 (짝수만 건너뛰기):");
        for (int i = 1; i <= 10; i++) {
            if (i % 2 == 0) {
                continue;  // 짝수면 이번 반복 건너뛰고 다음으로
            }
            System.out.print(i + " ");  // 홀수만 출력돼요
        }
        System.out.println();

        // ── 레이블 break (Labeled Break) ─────────────────

        /*
         * 레이블 break (중첩 반복문 탈출)
         *
         * 반복문이 여러 겹으로 있을 때,
         * 가장 바깥 반복문까지 한 번에 탈출하고 싶을 때 써요!
         * 마치 건물 여러 층에 갇혔을 때 엘리베이터로
         * 한 번에 1층으로 내려오는 것처럼요!
         */

        System.out.println("\n레이블 break 예제:");
        outer:  // 바깥 for에 'outer'라는 이름표를 붙여요
        for (int i = 1; i <= 3; i++) {
            for (int j = 1; j <= 3; j++) {
                System.out.print("(" + i + "," + j + ") ");
                if (i == 2 && j == 2) {
                    System.out.println("← 여기서 바깥 루프도 탈출!");
                    break outer;  // 'outer' 이름표의 for문까지 탈출!
                }
            }
            System.out.println();
        }
        System.out.println("완전히 탈출했어요!");

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 9: 구구단 전체 출력 (종합 예제)
        // ═══════════════════════════════════════════════════

        System.out.println("=== 종합 예제: 구구단 전체 ===");

        for (int dan = 2; dan <= 9; dan++) {
            System.out.println("─── " + dan + "단 ───");
            for (int num = 1; num <= 9; num++) {
                System.out.printf("%d × %d = %2d   ", dan, num, dan * num);
                if (num == 4) System.out.println(); // 4번째마다 줄바꿈
            }
            System.out.println();
        }

        System.out.println("╔══════════════════════════════════════╗");
        System.out.println("║  02단계 제어 흐름 학습 완료! 짝짝짝! ║");
        System.out.println("╚══════════════════════════════════════╝");
    }
}
