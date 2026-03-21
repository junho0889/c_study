/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Java 학습 16단계: 테스트
  ─ 단위 테스트, JUnit 5, 어서션, TDD 개념, Mockito 소개 ─

  [학습 목표]
  1. 테스트가 왜 중요한지 이해한다
  2. 단위 테스트(Unit Test)의 개념을 안다
  3. JUnit 5의 핵심 어노테이션과 어서션을 안다
  4. 테스트 주도 개발(TDD)의 흐름을 이해한다
  5. Mockito의 기본 개념을 안다
  6. 직접 미니 테스트 프레임워크를 만들어 본다

  ■ 컴파일: javac Main.java
  ■ 실행:   java Main

  ★ 주의: 실제 JUnit은 별도 의존성 필요!
    이 파일은 JUnit의 "개념"을 직접 구현하여 학습합니다.

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

import java.util.*;


// =====================================================================
// 레슨 1 — 테스트가 왜 중요한가?
// =====================================================================
/*
★ 테스트 = "코드가 올바르게 동작하는지 자동으로 확인하는 코드"

  ┌──────────────────────────────────────────────────┐
  │  비유: 테스트는 "자동 맞춤법 검사기"              │
  │                                                  │
  │  글을 쓸 때(코드 작성):                          │
  │    직접 읽어보기 → 시간 오래 걸림, 실수 놓침     │
  │    맞춤법 검사기 → 자동으로 오류 발견!           │
  │                                                  │
  │  코드 변경할 때마다 자동으로 검사 → 안심!        │
  └──────────────────────────────────────────────────┘

★ 테스트를 쓰면 좋은 점
  1. 버그를 빨리 발견 (변경 후 바로 확인!)
  2. 리팩토링에 자신감 (테스트가 통과하면 OK!)
  3. 문서 역할 (테스트 코드를 보면 사용법을 알 수 있음)
  4. 설계 개선 (테스트하기 어려운 코드 = 설계가 나쁜 코드)

★ 테스트 종류
  ┌────────────────┬──────────────────────────────────┐
  │ 종류           │ 설명                              │
  ├────────────────┼──────────────────────────────────┤
  │ 단위 테스트    │ 메서드/클래스 하나를 테스트        │
  │ (Unit Test)    │ 가장 작은 단위! 가장 많이 작성!   │
  ├────────────────┼──────────────────────────────────┤
  │ 통합 테스트    │ 여러 컴포넌트를 함께 테스트        │
  │ (Integration)  │ DB, API 연동 등                   │
  ├────────────────┼──────────────────────────────────┤
  │ E2E 테스트     │ 사용자 시나리오 전체 테스트        │
  │ (End-to-End)   │ 실제 사용하듯 처음부터 끝까지     │
  └────────────────┴──────────────────────────────────┘

  ★ 테스트 피라미드
         /\
        /E2E\          ← 적게 (느리고 비쌈)
       /──────\
      /통합 테스트\     ← 적당히
     /────────────\
    /  단위 테스트  \   ← 많이! (빠르고 저렴)
   /────────────────\
*/


// =====================================================================
// 레슨 2 — JUnit 5 핵심 개념
// =====================================================================
/*
★ JUnit 5 = Java의 표준 테스트 프레임워크

★ 핵심 어노테이션
  ┌───────────────────┬──────────────────────────────────┐
  │ 어노테이션         │ 설명                             │
  ├───────────────────┼──────────────────────────────────┤
  │ @Test             │ 테스트 메서드 표시                │
  │ @DisplayName      │ 테스트 이름 지정                 │
  │ @BeforeEach       │ 각 테스트 전에 실행              │
  │ @AfterEach        │ 각 테스트 후에 실행              │
  │ @BeforeAll        │ 모든 테스트 전에 1번             │
  │ @AfterAll         │ 모든 테스트 후에 1번             │
  │ @Disabled         │ 테스트 건너뛰기                  │
  │ @ParameterizedTest│ 여러 값으로 반복 테스트          │
  └───────────────────┴──────────────────────────────────┘

★ 핵심 어서션 (Assertions)
  ┌─────────────────────────┬──────────────────────────┐
  │ 어서션                   │ 의미                     │
  ├─────────────────────────┼──────────────────────────┤
  │ assertEquals(예상, 실제) │ 같은지 확인              │
  │ assertNotEquals(a, b)   │ 다른지 확인              │
  │ assertTrue(조건)         │ 조건이 참인지            │
  │ assertFalse(조건)        │ 조건이 거짓인지          │
  │ assertNull(값)           │ null인지                 │
  │ assertNotNull(값)        │ null이 아닌지            │
  │ assertThrows(예외, 코드) │ 예외가 발생하는지        │
  │ assertAll(...)           │ 여러 검증을 한 번에      │
  └─────────────────────────┴──────────────────────────┘

★ 실제 JUnit 테스트 코드 예시:
  @Test
  @DisplayName("90점 이상이면 A등급")
  void gradeA() {
      assertEquals("A", gradeFromScore(95));
      assertEquals("A", gradeFromScore(90));
  }

  @Test
  @DisplayName("음수 점수는 예외 발생")
  void negativeScore() {
      assertThrows(IllegalArgumentException.class,
          () -> gradeFromScore(-1));
  }
*/


// =====================================================================
// 레슨 3 — 미니 테스트 프레임워크 구현
// =====================================================================
/*
★ JUnit의 원리를 이해하기 위해 직접 만들어보자!
  → assertEquals, assertTrue, assertThrows 등을 직접 구현!
*/

class MiniTest {
    private static int totalTests = 0;
    private static int passedTests = 0;
    private static int failedTests = 0;
    private static final List<String> failures = new ArrayList<>();

    // ★ assertEquals: 두 값이 같은지 검사
    static void assertEquals(Object expected, Object actual, String testName) {
        totalTests++;
        if (Objects.equals(expected, actual)) {
            passedTests++;
            System.out.println("    PASS: " + testName);
        } else {
            failedTests++;
            String msg = testName + " (기대: " + expected + ", 실제: " + actual + ")";
            failures.add(msg);
            System.out.println("    FAIL: " + msg);
        }
    }

    // ★ assertTrue: 조건이 참인지 검사
    static void assertTrue(boolean condition, String testName) {
        totalTests++;
        if (condition) {
            passedTests++;
            System.out.println("    PASS: " + testName);
        } else {
            failedTests++;
            failures.add(testName + " (조건이 false)");
            System.out.println("    FAIL: " + testName + " (조건이 false)");
        }
    }

    // ★ assertFalse: 조건이 거짓인지 검사
    static void assertFalse(boolean condition, String testName) {
        assertTrue(!condition, testName);
    }

    // ★ assertThrows: 예외가 발생하는지 검사
    static void assertThrows(Class<? extends Throwable> expectedType,
                              Runnable code, String testName) {
        totalTests++;
        try {
            code.run();
            failedTests++;
            failures.add(testName + " (예외가 발생하지 않음)");
            System.out.println("    FAIL: " + testName + " (예외가 발생하지 않음)");
        } catch (Throwable e) {
            if (expectedType.isInstance(e)) {
                passedTests++;
                System.out.println("    PASS: " + testName
                        + " (" + e.getClass().getSimpleName() + " 발생)");
            } else {
                failedTests++;
                String msg = testName + " (기대: " + expectedType.getSimpleName()
                        + ", 실제: " + e.getClass().getSimpleName() + ")";
                failures.add(msg);
                System.out.println("    FAIL: " + msg);
            }
        }
    }

    // ★ 결과 출력
    static void printSummary() {
        System.out.println();
        System.out.println("  ┌────────────────────────────────────┐");
        System.out.println("  │  테스트 결과 요약                  │");
        System.out.println("  ├────────────────────────────────────┤");
        System.out.printf("  │  전체: %d | 통과: %d | 실패: %d     │%n",
                totalTests, passedTests, failedTests);
        System.out.println("  ├────────────────────────────────────┤");
        if (failures.isEmpty()) {
            System.out.println("  │  모든 테스트 통과!               │");
        } else {
            System.out.println("  │  실패 목록:                       │");
            for (String f : failures) {
                System.out.println("  │    - " + f);
            }
        }
        System.out.println("  └────────────────────────────────────┘");
    }

    static void reset() {
        totalTests = 0;
        passedTests = 0;
        failedTests = 0;
        failures.clear();
    }
}


// =====================================================================
// 레슨 4 — TDD (테스트 주도 개발)
// =====================================================================
/*
★ TDD = Test-Driven Development
  → 코드를 먼저 쓰는 게 아니라 테스트를 먼저 쓴다!

  ┌──────────────────────────────────────────────────┐
  │  TDD 3단계 사이클 (Red → Green → Refactor)      │
  │                                                  │
  │  1. RED:      실패하는 테스트를 먼저 작성         │
  │  2. GREEN:    테스트를 통과하는 최소한의 코드     │
  │  3. REFACTOR: 코드를 깔끔하게 정리               │
  │                                                  │
  │  ┌─────┐  →  ┌───────┐  →  ┌──────────┐        │
  │  │ RED │     │ GREEN │     │ REFACTOR │         │
  │  └─────┘  ←  └───────┘  ←  └──────────┘        │
  │    (반복)                                        │
  └──────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────┐
  │  비유: TDD는 "시험 문제를 먼저 보는 것"           │
  │                                                  │
  │  일반 방식: 공부 → 시험 → 틀린 부분 발견         │
  │  TDD 방식:  시험 문제 확인 → 공부 → 확인!       │
  │                                                  │
  │  어디를 공부해야 하는지 미리 아니까 효율적!       │
  └──────────────────────────────────────────────────┘
*/


// =====================================================================
// 레슨 5 — Mockito 기본 개념
// =====================================================================
/*
★ Mockito = 테스트에서 "가짜 객체(Mock)"를 만들어주는 라이브러리
  → 외부 의존성(DB, API 등)을 가짜로 대체하여 단위 테스트 가능!

  ┌──────────────────────────────────────────────────┐
  │  비유: Mock은 "대역 배우"                         │
  │                                                  │
  │  영화 촬영에서:                                  │
  │    위험한 장면 → 스턴트 대역 사용                │
  │                                                  │
  │  테스트에서:                                     │
  │    DB 접근 → Mock 객체 사용 (진짜 DB 불필요!)   │
  └──────────────────────────────────────────────────┘

★ Mockito 핵심 기능
  ┌────────────────────┬──────────────────────────────────┐
  │ 기능               │ 설명                              │
  ├────────────────────┼──────────────────────────────────┤
  │ mock(Class)        │ 가짜 객체 생성                    │
  │ when(...).then...  │ 가짜 동작 설정                    │
  │ verify(mock)       │ 메서드가 호출되었는지 확인         │
  │ any(), eq()        │ 매개변수 매칭                     │
  └────────────────────┴──────────────────────────────────┘

★ Mockito 예시 코드 (개념):
  // 가짜 저장소 생성
  UserRepository mockRepo = mock(UserRepository.class);

  // 가짜 동작 설정
  when(mockRepo.findById(1)).thenReturn(new User("홍길동"));

  // 테스트 대상에 주입
  UserService service = new UserService(mockRepo);

  // 테스트!
  assertEquals("홍길동", service.getUserName(1));
  verify(mockRepo).findById(1);  // findById가 호출되었는지 확인
*/


// =====================================================================
// 테스트 대상 코드
// =====================================================================

class Calculator {
    int add(int a, int b) { return a + b; }
    int subtract(int a, int b) { return a - b; }
    int multiply(int a, int b) { return a * b; }

    int divide(int a, int b) {
        if (b == 0) throw new ArithmeticException("0으로 나눌 수 없습니다");
        return a / b;
    }
}

class GradeCalculator {
    static String gradeFromScore(int score) {
        if (score < 0 || score > 100) {
            throw new IllegalArgumentException("점수 범위 초과: " + score);
        }
        if (score >= 90) return "A";
        if (score >= 80) return "B";
        if (score >= 70) return "C";
        if (score >= 60) return "D";
        return "F";
    }

    static boolean isPassed(int score) {
        return score >= 60;
    }

    static double average(int... scores) {
        if (scores.length == 0) return 0;
        int total = 0;
        for (int s : scores) total += s;
        return (double) total / scores.length;
    }
}

class StringUtils {
    static String reverse(String s) {
        if (s == null) return null;
        return new StringBuilder(s).reverse().toString();
    }

    static boolean isPalindrome(String s) {
        if (s == null) return false;
        String cleaned = s.toLowerCase().replaceAll("[^a-z0-9가-힣]", "");
        return cleaned.equals(new StringBuilder(cleaned).reverse().toString());
    }

    static int countVowels(String s) {
        if (s == null) return 0;
        return (int) s.toLowerCase().chars()
                .filter(c -> "aeiou".indexOf(c) >= 0)
                .count();
    }
}


// =====================================================================
//  메인 실행
// =====================================================================
public class Main {

    public static void main(String[] args) {
        System.out.println("■■■ Java 16단계: 테스트 ■■■\n");

        // ─── 레슨 2~3: 미니 테스트 프레임워크 ────────────
        System.out.println("── Calculator 테스트 ────────────────────────────");
        Calculator calc = new Calculator();

        MiniTest.assertEquals(5, calc.add(2, 3), "2 + 3 = 5");
        MiniTest.assertEquals(0, calc.add(-1, 1), "-1 + 1 = 0");
        MiniTest.assertEquals(7, calc.subtract(10, 3), "10 - 3 = 7");
        MiniTest.assertEquals(12, calc.multiply(3, 4), "3 * 4 = 12");
        MiniTest.assertEquals(5, calc.divide(10, 2), "10 / 2 = 5");

        // ★ 예외 테스트
        MiniTest.assertThrows(ArithmeticException.class,
                () -> calc.divide(10, 0),
                "10 / 0은 ArithmeticException");
        System.out.println();

        // ─── GradeCalculator 테스트 ──────────────────────
        System.out.println("── GradeCalculator 테스트 ───────────────────────");
        MiniTest.assertEquals("A", GradeCalculator.gradeFromScore(95), "95점 → A");
        MiniTest.assertEquals("A", GradeCalculator.gradeFromScore(90), "90점 → A (경계값)");
        MiniTest.assertEquals("B", GradeCalculator.gradeFromScore(89), "89점 → B");
        MiniTest.assertEquals("B", GradeCalculator.gradeFromScore(80), "80점 → B (경계값)");
        MiniTest.assertEquals("C", GradeCalculator.gradeFromScore(75), "75점 → C");
        MiniTest.assertEquals("D", GradeCalculator.gradeFromScore(65), "65점 → D");
        MiniTest.assertEquals("F", GradeCalculator.gradeFromScore(55), "55점 → F");
        MiniTest.assertEquals("F", GradeCalculator.gradeFromScore(0), "0점 → F (경계값)");

        // 경계값 테스트
        MiniTest.assertThrows(IllegalArgumentException.class,
                () -> GradeCalculator.gradeFromScore(-1),
                "음수 점수는 예외");
        MiniTest.assertThrows(IllegalArgumentException.class,
                () -> GradeCalculator.gradeFromScore(101),
                "101점은 예외");

        // 통과 여부
        MiniTest.assertTrue(GradeCalculator.isPassed(60), "60점은 통과");
        MiniTest.assertFalse(GradeCalculator.isPassed(59), "59점은 미통과");

        // 평균
        MiniTest.assertEquals(80.0, GradeCalculator.average(70, 80, 90), "평균 (70,80,90) = 80");
        MiniTest.assertEquals(0.0, GradeCalculator.average(), "빈 배열 평균 = 0");
        System.out.println();

        // ─── StringUtils 테스트 ──────────────────────────
        System.out.println("── StringUtils 테스트 ───────────────────────────");
        MiniTest.assertEquals("olleh", StringUtils.reverse("hello"), "reverse(hello) = olleh");
        MiniTest.assertEquals("", StringUtils.reverse(""), "reverse(\"\") = \"\"");
        MiniTest.assertEquals(null, StringUtils.reverse(null), "reverse(null) = null");

        MiniTest.assertTrue(StringUtils.isPalindrome("racecar"), "racecar는 회문");
        MiniTest.assertTrue(StringUtils.isPalindrome("A man a plan a canal Panama"),
                "Panama 문장은 회문");
        MiniTest.assertFalse(StringUtils.isPalindrome("hello"), "hello는 회문 아님");
        MiniTest.assertFalse(StringUtils.isPalindrome(null), "null은 회문 아님");

        MiniTest.assertEquals(2, StringUtils.countVowels("hello"), "hello 모음 2개");
        MiniTest.assertEquals(5, StringUtils.countVowels("aeiou"), "aeiou 모음 5개");
        MiniTest.assertEquals(0, StringUtils.countVowels("xyz"), "xyz 모음 0개");
        System.out.println();

        // ─── 테스트 결과 요약 ────────────────────────────
        System.out.println("── 테스트 결과 요약 ─────────────────────────────");
        MiniTest.printSummary();
        System.out.println();

        // ─── 레슨 4: TDD 개념 정리 ──────────────────────
        System.out.println("── 레슨 4: TDD 단계별 시뮬레이션 ───────────────");
        System.out.println("  [TDD 예시: FizzBuzz 구현]");
        System.out.println();
        System.out.println("  1단계 RED: 실패하는 테스트 작성");
        System.out.println("    assertEquals(\"Fizz\", fizzBuzz(3));  // 아직 구현 안 됨!");
        System.out.println();
        System.out.println("  2단계 GREEN: 최소한의 코드로 통과");
        System.out.println("    String fizzBuzz(int n) {");
        System.out.println("        if (n % 15 == 0) return \"FizzBuzz\";");
        System.out.println("        if (n % 3 == 0)  return \"Fizz\";");
        System.out.println("        if (n % 5 == 0)  return \"Buzz\";");
        System.out.println("        return String.valueOf(n);");
        System.out.println("    }");
        System.out.println();
        System.out.println("  3단계 REFACTOR: 깔끔하게 정리 (이미 깔끔!)");
        System.out.println();

        // FizzBuzz 구현 및 테스트
        MiniTest.reset();
        System.out.println("  [FizzBuzz 테스트]");
        MiniTest.assertEquals("1", fizzBuzz(1), "1 → 1");
        MiniTest.assertEquals("Fizz", fizzBuzz(3), "3 → Fizz");
        MiniTest.assertEquals("Buzz", fizzBuzz(5), "5 → Buzz");
        MiniTest.assertEquals("FizzBuzz", fizzBuzz(15), "15 → FizzBuzz");
        MiniTest.assertEquals("FizzBuzz", fizzBuzz(30), "30 → FizzBuzz");
        MiniTest.assertEquals("7", fizzBuzz(7), "7 → 7");
        MiniTest.printSummary();
        System.out.println();

        // ─── 레슨 5: 좋은 테스트의 조건 ─────────────────
        System.out.println("── 레슨 5: 좋은 테스트 작성법 ──────────────────");
        System.out.println("  ┌──────────────────────────────────────────────┐");
        System.out.println("  │  좋은 테스트의 FIRST 원칙                   │");
        System.out.println("  ├──────────────────────────────────────────────┤");
        System.out.println("  │  F - Fast:       빠르게 실행                │");
        System.out.println("  │  I - Independent: 다른 테스트와 독립적      │");
        System.out.println("  │  R - Repeatable:  반복해도 같은 결과        │");
        System.out.println("  │  S - Self-validating: 스스로 pass/fail 판단│");
        System.out.println("  │  T - Timely:      코드와 함께 작성          │");
        System.out.println("  └──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  ★ 테스트 작성 팁:");
        System.out.println("    1. 한 테스트에 하나의 검증 (Single Assert)");
        System.out.println("    2. 테스트 이름은 행동을 설명 (given_when_then)");
        System.out.println("    3. 경계값을 꼭 테스트 (0, 빈 문자열, null)");
        System.out.println("    4. 예외 상황도 테스트 (assertThrows)");
        System.out.println("    5. AAA 패턴: Arrange → Act → Assert");
        System.out.println();

        System.out.println("■■■ 16단계 학습 완료! ■■■");
    }

    // ─── FizzBuzz 구현 (TDD 결과물) ─────────────────────
    static String fizzBuzz(int n) {
        if (n % 15 == 0) return "FizzBuzz";
        if (n % 3 == 0) return "Fizz";
        if (n % 5 == 0) return "Buzz";
        return String.valueOf(n);
    }
}
