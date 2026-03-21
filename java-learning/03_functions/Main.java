/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Java 학습 03단계: 메서드 (함수)
  ─ 메서드 선언, 오버로딩, 가변인자, 재귀, static vs instance ─

  ■ 컴파일: javac Main.java
  ■ 실행:   java Main

  메서드(Method)는 "할 일 묶음"이에요!
  자주 하는 일을 한 곳에 모아두고 이름을 붙여서
  필요할 때마다 불러 쓸 수 있어요!
  마치 수학 공식처럼요: 원넓이 = π × r²

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

public class Main {

    /*
    ┌─────────────────────────────────────────────────────────┐
    │  메서드 기본 구조                                        │
    │                                                         │
    │  [접근제어자] [static] 반환타입 메서드이름(매개변수) {  │
    │      // 실행할 코드                                      │
    │      return 반환값;  // 반환타입이 void면 생략           │
    │  }                                                      │
    │                                                         │
    │  접근제어자: public, private, protected, (기본)          │
    │  static: 객체 없이 바로 쓸 수 있는 메서드               │
    │  반환타입: 결과로 돌려줄 값의 자료형 (없으면 void)       │
    │  매개변수: 메서드에게 전달할 값들                        │
    └─────────────────────────────────────────────────────────┘
    */

    // ═══════════════════════════════════════════════════════
    //  메서드 1: 반환값이 없는 메서드 (void)
    // ═══════════════════════════════════════════════════════

    /*
     * void 메서드 - 결과를 돌려주지 않고 그냥 실행만 해요.
     * 마치 선생님이 "인사해!"라고 하면 "안녕하세요!"라고
     * 말하는 것처럼요. 결과물이 남는 게 아니에요.
     */
    static void sayHello(String name) {
        System.out.println("안녕하세요, " + name + "님!");
    }

    static void printLine(int length) {
        // length 만큼 = 기호를 출력해요
        for (int i = 0; i < length; i++) {
            System.out.print("=");
        }
        System.out.println();
    }

    static void printStars(int rows) {
        // rows 만큼 별 삼각형을 그려요
        for (int i = 1; i <= rows; i++) {
            for (int j = 1; j <= i; j++) {
                System.out.print("★");
            }
            System.out.println();
        }
    }

    // ═══════════════════════════════════════════════════════
    //  메서드 2: 반환값이 있는 메서드
    // ═══════════════════════════════════════════════════════

    /*
     * 반환값이 있는 메서드 - 계산 결과를 돌려줘요.
     * 마치 가게에서 물건을 사면 거스름돈을 받는 것처럼요!
     * "넣어준 값(매개변수)"으로 계산해서 "결과(반환값)"를 줘요.
     */

    // 두 수를 더하는 메서드
    static int add(int a, int b) {
        return a + b;  // return = 이 값을 돌려줘요!
    }

    // 원의 넓이 계산 메서드
    static double calculateCircleArea(double radius) {
        return Math.PI * radius * radius;
    }

    // 학점 계산 메서드
    static String getGrade(int score) {
        if (score >= 90) return "A";
        else if (score >= 80) return "B";
        else if (score >= 70) return "C";
        else if (score >= 60) return "D";
        else return "F";
    }

    // 두 수 중 최대값 반환
    static int max(int a, int b) {
        return (a > b) ? a : b;
    }

    // 팩토리얼 계산 (반복문 방식)
    static long factorial(int n) {
        // 팩토리얼: n! = 1 × 2 × 3 × ... × n
        // 예: 5! = 1 × 2 × 3 × 4 × 5 = 120
        long result = 1;
        for (int i = 2; i <= n; i++) {
            result *= i;
        }
        return result;
    }

    // ═══════════════════════════════════════════════════════
    //  메서드 3: 메서드 오버로딩 (Method Overloading)
    // ═══════════════════════════════════════════════════════

    /*
     * 메서드 오버로딩이란?
     *
     * 같은 이름의 메서드를 여러 개 만드는 것이에요!
     * 단, 매개변수의 종류나 개수가 달라야 해요.
     *
     * 마치 "찍다"라는 말이
     * "사진을 찍다" / "도장을 찍다" / "떡을 찍다"
     * 로 상황에 따라 다른 의미가 되는 것처럼요!
     *
     * Java가 매개변수를 보고 어떤 메서드를 쓸지 자동으로 결정해요!
     */

    // int 두 개 더하기
    static int sum(int a, int b) {
        System.out.println("  [int + int 메서드 호출]");
        return a + b;
    }

    // int 세 개 더하기
    static int sum(int a, int b, int c) {
        System.out.println("  [int + int + int 메서드 호출]");
        return a + b + c;
    }

    // double 두 개 더하기
    static double sum(double a, double b) {
        System.out.println("  [double + double 메서드 호출]");
        return a + b;
    }

    // String 두 개 이어붙이기
    static String sum(String a, String b) {
        System.out.println("  [String + String 메서드 호출]");
        return a + b;
    }

    // ═══════════════════════════════════════════════════════
    //  메서드 4: 가변 인자 (Varargs)
    // ═══════════════════════════════════════════════════════

    /*
     * 가변 인자(varargs)란?
     *
     * 매개변수의 개수가 몇 개인지 모를 때 써요!
     * 마치 "몇 명이 올지 모르지만 다 앉을 수 있는 긴 의자"처럼요.
     *
     * 타입... 변수명 → 이 형식으로 쓰면 돼요
     * 안에서는 배열처럼 사용해요!
     */

    // 몇 개의 숫자든 모두 더하기
    static int sumAll(int... numbers) {
        // numbers는 int 배열처럼 사용해요
        int total = 0;
        for (int num : numbers) {
            total += num;
        }
        return total;
    }

    // 메시지와 여러 이름을 받아서 인사하기
    static void greetAll(String message, String... names) {
        // message는 고정, names는 가변
        for (String name : names) {
            System.out.println(message + ", " + name + "!");
        }
    }

    // ═══════════════════════════════════════════════════════
    //  메서드 5: 재귀 (Recursion)
    // ═══════════════════════════════════════════════════════

    /*
     * 재귀(Recursion)란?
     *
     * 메서드가 자기 자신을 호출하는 것이에요!
     * 마치 거울 두 개를 마주보게 세우면
     * 무한히 반복되는 것처럼요.
     *
     * 하지만 재귀는 반드시 "탈출 조건"이 있어야 해요!
     * (안 그러면 영원히 멈추지 않아요 → StackOverflowError!)
     *
     * 예: 5! = 5 × 4!
     *          4! = 4 × 3!
     *               3! = 3 × 2!
     *                    2! = 2 × 1!
     *                         1! = 1 ← 탈출 조건!
     */

    // 재귀로 팩토리얼 계산
    static long factorialRecursive(int n) {
        // 탈출 조건: 1! = 1
        if (n <= 1) {
            return 1;
        }
        // 재귀 호출: n! = n × (n-1)!
        return n * factorialRecursive(n - 1);
    }

    // 재귀로 피보나치 수열 계산
    // 피보나치: 1, 1, 2, 3, 5, 8, 13, 21, ...
    // 앞의 두 수를 더하면 다음 수가 돼요!
    static int fibonacci(int n) {
        if (n <= 1) return n;  // 탈출 조건
        return fibonacci(n - 1) + fibonacci(n - 2);  // 재귀 호출
    }

    // 재귀로 카운트다운
    static void countdown(int n) {
        if (n <= 0) {  // 탈출 조건
            System.out.println("발사!!!");
            return;
        }
        System.out.println(n + "...");
        countdown(n - 1);  // 재귀 호출
    }

    // ═══════════════════════════════════════════════════════
    //  메서드 6: 값에 의한 전달 (Pass by Value)
    // ═══════════════════════════════════════════════════════

    /*
     * Java는 항상 "값에 의한 전달"이에요!
     *
     * 기본형(int, double 등)을 메서드에 넘기면
     * 원본이 아닌 복사본을 넘겨요.
     *
     * 마치 내 노트를 친구에게 주는 게 아니라
     * 복사해서 주는 것처럼요!
     * 친구가 복사본에 낙서해도 내 원본은 안 바뀌어요.
     */

    static void tryToChange(int value) {
        value = 999;  // 복사본을 바꿔도 원본은 안 바뀌어요!
        System.out.println("메서드 안 value: " + value);
    }

    // 배열은 참조형이라 조금 다르게 동작해요
    // 배열의 주소를 복사해서 넘기기 때문에
    // 메서드 안에서 배열 내용을 바꾸면 원본도 바뀌어요!
    static void changeArray(int[] arr) {
        arr[0] = 999;  // 원본 배열의 첫 번째 값을 바꿔요!
        System.out.println("메서드 안 arr[0]: " + arr[0]);
    }

    // ═══════════════════════════════════════════════════════
    //  main 메서드 - 모든 것을 테스트해요!
    // ═══════════════════════════════════════════════════════

    public static void main(String[] args) {

        System.out.println("=== 03단계: 메서드 (함수) ===");
        System.out.println();

        // ── void 메서드 테스트 ────────────────────────────
        System.out.println("[ void 메서드 ]");
        sayHello("김철수");
        sayHello("이영희");
        printLine(30);
        printStars(4);
        System.out.println();

        // ── 반환값 메서드 테스트 ──────────────────────────
        System.out.println("[ 반환값 메서드 ]");

        int result = add(5, 3);
        System.out.println("add(5, 3) = " + result);

        double area = calculateCircleArea(5.0);
        System.out.printf("반지름 5의 원 넓이: %.2f%n", area);

        System.out.println("85점의 학점: " + getGrade(85));
        System.out.println("72점의 학점: " + getGrade(72));
        System.out.println("55점의 학점: " + getGrade(55));

        System.out.println("max(10, 20) = " + max(10, 20));

        System.out.println("5! (반복) = " + factorial(5));
        System.out.println("10! (반복) = " + factorial(10));
        System.out.println();

        // ── 메서드 오버로딩 테스트 ────────────────────────
        System.out.println("[ 메서드 오버로딩 ]");
        System.out.println("같은 이름 'sum'이지만 매개변수에 따라 다른 메서드 호출!");
        System.out.println("sum(3, 4) = " + sum(3, 4));
        System.out.println("sum(1, 2, 3) = " + sum(1, 2, 3));
        System.out.println("sum(1.5, 2.5) = " + sum(1.5, 2.5));
        System.out.println("sum(\"안녕\", \"!\") = " + sum("안녕", "!"));
        System.out.println();

        // ── 가변 인자 테스트 ──────────────────────────────
        System.out.println("[ 가변 인자 (varargs) ]");
        System.out.println("sumAll(1) = " + sumAll(1));
        System.out.println("sumAll(1,2,3) = " + sumAll(1, 2, 3));
        System.out.println("sumAll(1,2,3,4,5) = " + sumAll(1, 2, 3, 4, 5));
        System.out.println("sumAll(10,20,30,40,50,60) = " + sumAll(10,20,30,40,50,60));

        greetAll("안녕", "철수", "영희", "민준", "소연");
        System.out.println();

        // ── 재귀 테스트 ───────────────────────────────────
        System.out.println("[ 재귀 (Recursion) ]");

        System.out.println("재귀로 팩토리얼:");
        for (int i = 1; i <= 7; i++) {
            System.out.println(i + "! = " + factorialRecursive(i));
        }

        System.out.println("\n피보나치 수열 (첫 10개):");
        System.out.print("  ");
        for (int i = 0; i < 10; i++) {
            System.out.print(fibonacci(i) + " ");
        }
        System.out.println();

        System.out.println("\n카운트다운:");
        countdown(5);
        System.out.println();

        // ── Pass by Value 테스트 ──────────────────────────
        System.out.println("[ Pass by Value (값에 의한 전달) ]");

        System.out.println("기본형 int:");
        int original = 100;
        System.out.println("메서드 호출 전: " + original);
        tryToChange(original);
        System.out.println("메서드 호출 후: " + original + " (변하지 않아요!)");

        System.out.println("\n참조형 배열:");
        int[] myArray = {1, 2, 3};
        System.out.println("메서드 호출 전 arr[0]: " + myArray[0]);
        changeArray(myArray);
        System.out.println("메서드 호출 후 arr[0]: " + myArray[0] + " (바뀌었어요!)");

        System.out.println();
        System.out.println("╔══════════════════════════════════════╗");
        System.out.println("║  03단계 메서드 학습 완료! 대단해요!  ║");
        System.out.println("╚══════════════════════════════════════╝");
    }
}
