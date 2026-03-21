/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Java 학습 01단계: 기초의 기초
  ─ 변수, 자료형, 입출력, 연산자, 문자열 ─

  ■ 컴파일: javac Main.java
  ■ 실행:   java Main

  이 파일을 읽는 여러분, 환영합니다! 🎉
  Java 프로그래밍의 첫걸음을 함께 배워봐요!

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// import는 Java에서 미리 만들어진 도구상자를 가져오는 것이에요.
// Scanner는 키보드로 입력을 받을 때 쓰는 도구예요.
// 마치 선생님이 학용품 상자에서 자를 꺼내는 것처럼요!
import java.util.Scanner;

/*
┌─────────────────────────────────────────────────────┐
│  Main 클래스 - 프로그램의 집                          │
│                                                     │
│  클래스(class)는 무엇인가요?                          │
│  클래스는 프로그램을 담는 "상자" 같은 거예요.          │
│  집에 비유하면, 클래스는 집 설계도이고                 │
│  그 설계도로 만든 실제 집이 "객체(object)"예요.        │
└─────────────────────────────────────────────────────┘
*/
public class Main {

    /*
    ┌─────────────────────────────────────────────────────┐
    │  main 메서드 - 프로그램이 시작되는 곳                │
    │                                                     │
    │  프로그램을 실행하면 Java는 제일 먼저               │
    │  main 메서드를 찾아서 실행해요.                      │
    │  마치 학교에서 선생님이 "출석 불러요!" 하면          │
    │  학생들이 준비하는 것처럼요.                        │
    │                                                     │
    │  public  = 누구나 이 메서드를 쓸 수 있어요          │
    │  static  = 객체 없이도 바로 쓸 수 있어요            │
    │  void    = 결과값을 돌려주지 않아요                 │
    │  String[] args = 실행할 때 추가 정보를 받아요       │
    └─────────────────────────────────────────────────────┘
    */
    public static void main(String[] args) {

        // ═══════════════════════════════════════════════════
        //  섹션 1: 화면에 글자 출력하기
        // ═══════════════════════════════════════════════════

        /*
         * System.out.println() 과 System.out.print() 의 차이
         *
         * println = "print line" 의 줄임말
         *           글자를 출력하고 나서 줄을 바꿔요.
         *           마치 노트에 한 줄 쓰고 다음 줄로 넘어가는 것처럼요!
         *
         * print   = 글자만 출력하고 줄을 바꾸지 않아요.
         *           마치 노트에 쓰다가 멈추고 같은 줄에 계속 쓰는 것처럼요!
         */

        System.out.println("=== 01단계: Java 기초 배우기 ===");
        System.out.println();  // 빈 줄 출력 (줄바꿈만 해요)

        System.out.println("--- println 예제 ---");
        System.out.println("첫 번째 줄");   // 출력 후 줄바꿈 O
        System.out.println("두 번째 줄");   // 출력 후 줄바꿈 O

        System.out.println("--- print 예제 ---");
        System.out.print("사과 ");    // 줄바꿈 없이 계속 이어져요
        System.out.print("바나나 ");  // 줄바꿈 없이 계속 이어져요
        System.out.print("포도");     // 줄바꿈 없이 계속 이어져요
        System.out.println();        // 이제 줄을 바꿔요

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 2: 변수 - 정보를 저장하는 상자
        // ═══════════════════════════════════════════════════

        /*
         * 변수(Variable)란 무엇인가요?
         *
         * 변수는 정보를 저장하는 "상자"예요.
         * 마치 서랍장에 이름표를 붙이고 물건을 넣어두는 것처럼요!
         *
         * 예를 들어:
         *   나이 상자에는 숫자를 넣을 수 있어요 → int age = 10;
         *   이름 상자에는 글자를 넣을 수 있어요 → String name = "철수";
         *
         * 자료형(Data Type) = 상자의 종류예요.
         * 상자마다 넣을 수 있는 물건이 달라요!
         */

        System.out.println("=== 변수와 자료형 ===");

        // ── 정수형 (int) ──────────────────────────────────
        // int = integer(정수)의 줄임말
        // 소수점 없는 숫자를 저장해요. (-21억 ~ 21억)
        // 마치 개수를 세는 것처럼요: 사과 3개, 나이 10살
        int age = 10;
        int appleCount = 5;
        int temperature = -3;  // 음수도 됩니다!
        System.out.println("나이: " + age + "살");
        System.out.println("사과 개수: " + appleCount + "개");
        System.out.println("온도: " + temperature + "도");

        // ── 실수형 (double) ───────────────────────────────
        // double = 소수점이 있는 숫자를 저장해요.
        // 마치 1.5개, 3.14처럼 정확한 숫자가 필요할 때요!
        // double이 float보다 더 정확해요 (소수점 아래 자리가 더 많아요)
        double height = 145.5;   // 키 145.5cm
        double pi = 3.14159;     // 원주율
        System.out.println("키: " + height + "cm");
        System.out.println("원주율: " + pi);

        // ── 문자열 (String) ───────────────────────────────
        // String = 글자들의 묶음이에요.
        // 큰따옴표(" ")로 감싸줘야 해요!
        // 마치 이름표에 이름을 쓰는 것처럼요.
        // String은 대문자 S로 시작해요 - 특별한 클래스이기 때문이에요!
        String name = "홍길동";
        String greeting = "안녕하세요!";
        String school = "행복초등학교";
        System.out.println("이름: " + name);
        System.out.println(greeting);
        System.out.println("학교: " + school);

        // ── 논리형 (boolean) ──────────────────────────────
        // boolean = 참(true) 또는 거짓(false) 중 하나만 저장해요.
        // 마치 전등 스위치처럼요: 켜져있다(true) / 꺼져있다(false)
        boolean isHappy = true;
        boolean isRaining = false;
        boolean hasHomework = true;
        System.out.println("행복한가요? " + isHappy);
        System.out.println("비가 오나요? " + isRaining);
        System.out.println("숙제가 있나요? " + hasHomework);

        // ── 문자형 (char) ─────────────────────────────────
        // char = character(문자)의 줄임말
        // 딱 하나의 글자만 저장해요!
        // 작은따옴표(' ')로 감싸줘야 해요.
        // String은 여러 글자, char는 딱 한 글자예요!
        char grade = 'A';
        char initial = '홍';
        System.out.println("학점: " + grade);
        System.out.println("성씨: " + initial);

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 3: 기본형 vs 참조형 타입
        // ═══════════════════════════════════════════════════

        /*
         * 기본형(Primitive Type) vs 참조형(Reference Type)
         *
         * 기본형: 값 자체를 저장하는 상자예요.
         *   예: int, double, boolean, char, byte, short, long, float
         *   마치 저금통에 동전을 직접 넣는 것처럼요!
         *
         * 참조형: 값이 저장된 곳의 "주소"를 저장하는 상자예요.
         *   예: String, Integer, Double, 배열, 모든 클래스
         *   마치 집 열쇠(주소)를 갖고 있는 것처럼요.
         *   열쇠가 있으면 집(실제 값)을 찾아갈 수 있어요!
         *
         * ┌──────────────┬──────────────────────────────┐
         * │   기본형     │    참조형                    │
         * ├──────────────┼──────────────────────────────┤
         * │ int          │ Integer                      │
         * │ double       │ Double                       │
         * │ boolean      │ Boolean                      │
         * │ char         │ Character                    │
         * │ byte         │ Byte                         │
         * │ short        │ Short                        │
         * │ long         │ Long                         │
         * │ float        │ Float                        │
         * └──────────────┴──────────────────────────────┘
         */

        System.out.println("=== 기본형 vs 참조형 ===");

        // 기본형 - 값 자체를 담아요
        int primitiveInt = 42;
        System.out.println("기본형 int 값: " + primitiveInt);

        // 참조형 - 주소(참조)를 담아요
        // String은 참조형이에요
        String referenceString = "안녕";
        System.out.println("참조형 String 값: " + referenceString);

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 4: 래퍼 클래스 (Wrapper Class)
        // ═══════════════════════════════════════════════════

        /*
         * 래퍼 클래스(Wrapper Class)란?
         *
         * 기본형 숫자나 문자를 "포장지"로 감싸서
         * 참조형처럼 쓸 수 있게 만든 클래스예요!
         *
         * 왜 필요할까요?
         * Java의 컬렉션(ArrayList 등)은 기본형을 직접 쓸 수 없어요.
         * 래퍼 클래스로 감싸야 해요!
         *
         * 마치 선물을 포장지로 싸는 것처럼요.
         * 포장된 선물은 선물 그 자체와 똑같지만,
         * 선물 상자에 넣어서 보낼 수 있어요!
         *
         * 오토박싱(Auto-boxing): int → Integer 자동 변환
         * 언박싱(Unboxing):     Integer → int 자동 변환
         */

        System.out.println("=== 래퍼 클래스 ===");

        // Integer - int를 감싼 클래스
        Integer wrappedInt = 100;           // 오토박싱: int → Integer 자동 변환
        int unwrapped = wrappedInt;         // 언박싱: Integer → int 자동 변환
        System.out.println("래퍼 Integer: " + wrappedInt);
        System.out.println("언박싱 int: " + unwrapped);

        // 래퍼 클래스의 유용한 메서드들
        String numberStr = "123";
        int parsedInt = Integer.parseInt(numberStr);  // 문자열 → 정수 변환
        System.out.println("문자열 \"123\"을 정수로: " + parsedInt);

        int maxInt = Integer.MAX_VALUE;  // int의 최대값
        int minInt = Integer.MIN_VALUE;  // int의 최소값
        System.out.println("int 최대값: " + maxInt);
        System.out.println("int 최소값: " + minInt);

        // Double 래퍼 클래스
        Double wrappedDouble = 3.14;
        System.out.println("래퍼 Double: " + wrappedDouble);
        System.out.println("Double 최대값: " + Double.MAX_VALUE);

        // Boolean 래퍼 클래스
        String boolStr = "true";
        boolean parsedBool = Boolean.parseBoolean(boolStr);
        System.out.println("문자열 \"true\"를 boolean으로: " + parsedBool);

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 5: 상수 (Constants)
        // ═══════════════════════════════════════════════════

        /*
         * 상수(Constant)란?
         *
         * 한번 정하면 절대 바꿀 수 없는 값이에요!
         * final 키워드를 붙여서 만들어요.
         *
         * 마치 수학에서 원주율(π = 3.14159...)처럼
         * 절대 변하지 않는 값이에요!
         *
         * 상수 이름은 보통 대문자로 써요.
         * 여러 단어면 _ 로 연결해요.
         * 예: MAX_SPEED, PI, SCHOOL_NAME
         */

        System.out.println("=== 상수 (final) ===");

        final double PI = 3.14159265358979;      // 원주율 - 절대 변경 불가!
        final int MAX_STUDENTS = 30;              // 최대 학생 수
        final String SCHOOL_NAME = "행복초등학교"; // 학교 이름

        System.out.println("원주율 PI = " + PI);
        System.out.println("최대 학생 수: " + MAX_STUDENTS + "명");
        System.out.println("학교 이름: " + SCHOOL_NAME);

        // PI = 3.14;  // 이렇게 하면 오류! 상수는 바꿀 수 없어요!

        // 상수로 원의 넓이 계산해보기
        double radius = 5.0;  // 반지름 5cm
        double circleArea = PI * radius * radius;
        System.out.println("반지름 " + radius + "cm인 원의 넓이: " + circleArea + "cm²");

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 6: 산술 연산자
        // ═══════════════════════════════════════════════════

        /*
         * 산술 연산자 (Arithmetic Operators)
         *
         * 수학 시간에 배운 더하기, 빼기, 곱하기, 나누기를
         * 컴퓨터에서도 똑같이 할 수 있어요!
         *
         * +  더하기 (덧셈)
         * -  빼기  (뺄셈)
         * *  곱하기 (곱셈) → 수학의 ×
         * /  나누기 (나눗셈의 몫) → 수학의 ÷
         * %  나머지 (나눗셈의 나머지) → 수학에 없는 특별한 연산!
         */

        System.out.println("=== 산술 연산자 ===");

        int a = 10;
        int b = 3;

        System.out.println("a = " + a + ", b = " + b);
        System.out.println("a + b = " + (a + b));   // 덧셈: 10 + 3 = 13
        System.out.println("a - b = " + (a - b));   // 뺄셈: 10 - 3 = 7
        System.out.println("a * b = " + (a * b));   // 곱셈: 10 × 3 = 30
        System.out.println("a / b = " + (a / b));   // 정수 나눗셈의 몫: 10 ÷ 3 = 3 (나머지 버림!)
        System.out.println("a % b = " + (a % b));   // 나머지: 10 ÷ 3 = 3...나머지 1

        // 주의! 정수끼리 나누면 소수점이 잘려요!
        // 마치 사과 10개를 3명에게 나눠주면 각자 3개씩 받고 1개 남는 것처럼요!
        System.out.println("\n주의: 정수 나눗셈 (소수점 버림)");
        System.out.println("10 / 3 = " + (10 / 3));      // 3 (소수점 버림!)
        System.out.println("10.0 / 3 = " + (10.0 / 3)); // 3.333... (실수 나눗셈)

        // 나머지(%) 연산의 활용
        // 짝수/홀수 판별에 많이 써요!
        System.out.println("\n나머지 연산 활용:");
        System.out.println("10 % 2 = " + (10 % 2) + " → 10은 짝수!");
        System.out.println("7 % 2 = " + (7 % 2) + " → 7은 홀수!");

        // 복합 대입 연산자 (축약형)
        // += : a = a + 값 을 줄여서 쓴 것
        // 마치 "사탕이 5개 있었는데 3개 더 받았어" = "사탕 += 3"
        System.out.println("\n복합 대입 연산자:");
        int score = 100;
        System.out.println("시작 점수: " + score);
        score += 20;   // score = score + 20
        System.out.println("점수 +20: " + score);
        score -= 5;    // score = score - 5
        System.out.println("점수 -5: " + score);
        score *= 2;    // score = score * 2
        System.out.println("점수 ×2: " + score);
        score /= 3;    // score = score / 3
        System.out.println("점수 ÷3: " + score);

        // 증가/감소 연산자
        // ++ : 1 증가  -- : 1 감소
        System.out.println("\n증가/감소 연산자:");
        int count = 5;
        System.out.println("count = " + count);
        count++;  // count = count + 1 (1 증가)
        System.out.println("count++ 후: " + count);
        count--;  // count = count - 1 (1 감소)
        System.out.println("count-- 후: " + count);

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 7: String 클래스 메서드
        // ═══════════════════════════════════════════════════

        /*
         * String 클래스의 다양한 메서드들
         *
         * String은 단순히 글자 묶음이 아니라,
         * 다양한 기능을 가진 "스마트 클래스"예요!
         * 마치 스마트폰처럼 기본 통화뿐 아니라
         * 다양한 앱을 쓸 수 있는 것처럼요!
         */

        System.out.println("=== String 메서드 ===");

        String text = "Hello, Java World!";
        System.out.println("원본 문자열: " + text);

        // length() - 문자열의 길이 (글자 수)
        System.out.println("길이: " + text.length() + "글자");

        // toUpperCase() - 모든 글자를 대문자로
        // toLowerCase() - 모든 글자를 소문자로
        System.out.println("대문자: " + text.toUpperCase());
        System.out.println("소문자: " + text.toLowerCase());

        // charAt(index) - 특정 위치의 글자 가져오기
        // 위치는 0부터 시작해요! (0번째가 첫 번째 글자)
        // 마치 줄 세운 친구들 번호가 0번부터 시작하는 것처럼요!
        System.out.println("0번째 글자: " + text.charAt(0));   // H
        System.out.println("7번째 글자: " + text.charAt(7));   // J

        // substring(start, end) - 일부 글자만 잘라내기
        // start 위치부터 end-1 위치까지 잘라요
        System.out.println("7~10번째 글자: " + text.substring(7, 11)); // Java

        // contains() - 특정 글자가 포함되어 있는지 확인
        System.out.println("\"Java\" 포함?: " + text.contains("Java"));
        System.out.println("\"Python\" 포함?: " + text.contains("Python"));

        // replace() - 특정 글자를 다른 글자로 바꾸기
        String replaced = text.replace("Java", "Python");
        System.out.println("Java → Python 교체: " + replaced);

        // trim() - 앞뒤 공백 제거
        String spacedText = "   안녕하세요!   ";
        System.out.println("공백 제거 전: \"" + spacedText + "\"");
        System.out.println("공백 제거 후: \"" + spacedText.trim() + "\"");

        // split() - 특정 문자를 기준으로 나누기
        String fruits = "사과,바나나,포도,수박";
        String[] fruitArray = fruits.split(",");  // 쉼표로 나누기
        System.out.println("과일 목록:");
        for (String fruit : fruitArray) {
            System.out.println("  - " + fruit);
        }

        // equals() vs == 비교
        // String에서는 == 대신 equals()를 써야 해요!
        // == 는 주소(참조)를 비교하고, equals()는 실제 내용을 비교해요!
        String str1 = new String("안녕");
        String str2 = new String("안녕");
        System.out.println("\nString 비교:");
        System.out.println("== 비교: " + (str1 == str2));           // false (주소 다름)
        System.out.println("equals() 비교: " + str1.equals(str2));  // true (내용 같음)

        // indexOf() - 특정 문자의 위치 찾기
        System.out.println("\n\"World\"의 위치: " + text.indexOf("World"));

        // startsWith(), endsWith() - 시작/끝 확인
        System.out.println("\"Hello\"로 시작?: " + text.startsWith("Hello"));
        System.out.println("\"!\"로 끝남?: " + text.endsWith("!"));

        // isEmpty(), isBlank() - 빈 문자열 확인
        String empty = "";
        String blank = "   ";
        System.out.println("\n빈 문자열 확인:");
        System.out.println("empty.isEmpty(): " + empty.isEmpty());   // true
        System.out.println("blank.isBlank(): " + blank.isBlank());   // true (공백만 있어도 blank!)

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 8: String.format() 과 printf
        // ═══════════════════════════════════════════════════

        /*
         * String.format() 과 printf
         *
         * 복잡한 문장을 깔끔하게 만들 수 있어요!
         * 마치 빈칸 채우기 문제처럼요:
         * "저는 ___ 살이고, 이름은 ___ 입니다."
         *
         * %d = 정수 (decimal)
         * %f = 실수 (float)
         * %s = 문자열 (string)
         * %c = 문자 (character)
         * %b = 논리값 (boolean)
         * %n = 줄바꿈
         */

        System.out.println("=== String.format() 과 printf ===");

        String studentName = "김철수";
        int studentAge = 11;
        double studentScore = 95.5;

        // String.format() - 형식에 맞게 문자열 만들기
        String formatted = String.format("이름: %s, 나이: %d살, 점수: %.1f점",
                                          studentName, studentAge, studentScore);
        System.out.println(formatted);

        // printf - 바로 출력하기
        System.out.printf("이름: %s%n", studentName);           // %n은 줄바꿈
        System.out.printf("나이: %d살%n", studentAge);
        System.out.printf("점수: %.2f점%n", studentScore);       // .2f = 소수점 2자리
        System.out.printf("정수: %5d%n", 42);                    // 5칸 공간에 오른쪽 정렬
        System.out.printf("정수: %-5d|%n", 42);                  // 5칸 공간에 왼쪽 정렬

        // 표 형식으로 출력하기
        System.out.println("\n성적표:");
        System.out.println("┌────────────┬────────┬─────────┐");
        System.out.println("│  이름      │ 나이   │  점수   │");
        System.out.println("├────────────┼────────┼─────────┤");
        System.out.printf( "│ %-10s │  %3d살 │ %6.1f  │%n", "김철수", 11, 95.5);
        System.out.printf( "│ %-10s │  %3d살 │ %6.1f  │%n", "이영희", 12, 88.0);
        System.out.printf( "│ %-10s │  %3d살 │ %6.1f  │%n", "박민준", 10, 100.0);
        System.out.println("└────────────┴────────┴─────────┘");

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 9: Scanner - 키보드 입력 받기
        // ═══════════════════════════════════════════════════

        /*
         * Scanner로 키보드 입력 받기
         *
         * 프로그램이 사용자에게 "뭔가를 물어보고" 싶을 때 써요!
         * 마치 선생님이 "이름이 뭐예요?"라고 물어보면
         * 학생이 대답하는 것처럼요.
         *
         * Scanner sc = new Scanner(System.in);
         * System.in = 키보드 입력 (Standard Input)
         *
         * nextLine()  = 한 줄 전체 읽기
         * nextInt()   = 정수 읽기
         * nextDouble() = 실수 읽기
         * next()      = 단어 하나 읽기 (공백 전까지)
         */

        System.out.println("=== Scanner 입력 (주석으로 설명) ===");
        System.out.println("실제 입력 데모는 미리 값을 정해서 보여줄게요:");

        // Scanner 사용 예시 (실제로는 키보드 입력을 받지만, 여기선 설명용)
        /*
         * 실제 사용 예시:
         *
         * Scanner sc = new Scanner(System.in);
         * System.out.print("이름을 입력하세요: ");
         * String inputName = sc.nextLine();
         * System.out.print("나이를 입력하세요: ");
         * int inputAge = sc.nextInt();
         * System.out.println("안녕하세요, " + inputName + "님! " + inputAge + "살이군요!");
         * sc.close();  // 다 쓴 Scanner는 닫아줘요!
         */

        // 문자열을 Stream으로 만들어 Scanner 사용 예시
        Scanner demoScanner = new Scanner("김민수\n13\n");
        String inputName = demoScanner.nextLine();
        int inputAge = demoScanner.nextInt();
        System.out.println("입력된 이름: " + inputName);
        System.out.println("입력된 나이: " + inputAge + "살");
        System.out.println("안녕하세요, " + inputName + "님! " + inputAge + "살이군요!");
        demoScanner.close();  // Scanner는 다 쓰고 나면 꼭 닫아줘요!

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 10: Math 클래스
        // ═══════════════════════════════════════════════════

        /*
         * Math 클래스 - 수학 계산 도우미!
         *
         * Java에는 복잡한 수학 계산을 쉽게 해주는
         * Math 클래스가 있어요!
         * 마치 계산기처럼 어려운 계산도 척척 해내요!
         */

        System.out.println("=== Math 클래스 ===");

        // Math.abs() - 절대값 (음수를 양수로)
        System.out.println("abs(-5) = " + Math.abs(-5));      // 5
        System.out.println("abs(3) = " + Math.abs(3));        // 3

        // Math.max(), Math.min() - 최대값, 최소값
        System.out.println("max(10, 20) = " + Math.max(10, 20));  // 20
        System.out.println("min(10, 20) = " + Math.min(10, 20));  // 10

        // Math.pow() - 거듭제곱 (power)
        // 2의 10제곱 = 2×2×2×2×2×2×2×2×2×2 = 1024
        System.out.println("2의 10제곱 = " + (int)Math.pow(2, 10));  // 1024
        System.out.println("3의 3제곱 = " + (int)Math.pow(3, 3));   // 27

        // Math.sqrt() - 제곱근 (square root)
        // 4의 제곱근 = 2 (2×2=4 이니까요!)
        System.out.println("√4 = " + Math.sqrt(4));    // 2.0
        System.out.println("√9 = " + Math.sqrt(9));    // 3.0
        System.out.println("√2 = " + Math.sqrt(2));    // 1.414...

        // Math.round() - 반올림
        // Math.floor() - 내림 (항상 작은 정수로)
        // Math.ceil()  - 올림 (항상 큰 정수로)
        System.out.println("round(3.4) = " + Math.round(3.4));   // 3 (반올림)
        System.out.println("round(3.5) = " + Math.round(3.5));   // 4 (반올림)
        System.out.println("floor(3.9) = " + Math.floor(3.9));   // 3.0 (내림)
        System.out.println("ceil(3.1)  = " + Math.ceil(3.1));    // 4.0 (올림)

        // Math.random() - 0.0 이상 1.0 미만의 랜덤 숫자
        // 1~6 사이의 주사위 숫자 만들기:
        // (int)(Math.random() * 6) + 1 → 0~5에 1을 더하면 1~6!
        int diceRoll = (int)(Math.random() * 6) + 1;
        System.out.println("주사위 굴리기: " + diceRoll + "!");

        // Math.PI - 원주율 상수
        System.out.println("Math.PI = " + Math.PI);

        System.out.println();
        System.out.println("╔══════════════════════════════════════╗");
        System.out.println("║  01단계 기초 학습 완료! 수고했어요!  ║");
        System.out.println("╚══════════════════════════════════════╝");
    }
}
