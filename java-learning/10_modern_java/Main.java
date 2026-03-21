/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Java 학습 10단계: 현대 Java 기능
  ─ var, record, sealed, switch 표현식, 텍스트 블록, 패턴 매칭 ─

  [학습 목표]
  1. var (지역 변수 타입 추론, Java 10)를 안다
  2. record (불변 데이터 클래스, Java 16)를 안다
  3. switch 표현식 (Java 14)을 사용할 수 있다
  4. 텍스트 블록 (Java 15)을 안다
  5. sealed class (봉인 클래스, Java 17)를 이해한다
  6. 패턴 매칭 instanceof (Java 16)를 안다

  ■ 컴파일: javac Main.java
  ■ 실행:   java Main

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

import java.util.*;
import java.util.stream.*;


// =====================================================================
// 레슨 1 — var (지역 변수 타입 추론)
// =====================================================================
/*
★ var = 컴파일러가 오른쪽 값을 보고 타입을 알아내는 키워드
  → 타입을 없애는 게 아니라 "생략"할 수 있게 해주는 것!
  → Java 10부터 사용 가능

  ┌──────────────────────────────────────────┐
  │  비유: var는 "알아서 적어줘"              │
  │                                          │
  │  기존: "사과 3개를 사과 바구니에 넣어"    │
  │  var:  "이걸 바구니에 넣어" (보면 알잖아!)│
  └──────────────────────────────────────────┘

★ var 사용 가능/불가능
  ┌──────────────────┬───────────────────────────┐
  │ O 사용 가능      │ X 사용 불가               │
  ├──────────────────┼───────────────────────────┤
  │ 지역 변수        │ 필드(멤버 변수)           │
  │ for문 변수       │ 매개변수                  │
  │ try-with 변수    │ 반환 타입                 │
  │                  │ 초기값이 없는 경우         │
  │                  │ null 초기화               │
  └──────────────────┴───────────────────────────┘

★ var를 쓰면 좋은 경우
  var list = new ArrayList<String>();           // 오른쪽에 타입이 보임
  var entry = map.entrySet().iterator().next(); // 타입이 너무 길 때

★ var를 쓰면 안 좋은 경우
  var result = process();  // 뭐가 반환되는지 모름! 가독성 ↓
*/


// =====================================================================
// 레슨 2 — record (불변 데이터 클래스)
// =====================================================================
/*
★ record = 데이터를 담기 위한 "자동 완성" 클래스 (Java 16)
  → 생성자, getter, equals, hashCode, toString을 자동 생성!

  ┌──────────────────────────────────────────┐
  │  비유: record는 "자동 양식 서류"          │
  │                                          │
  │  이름:___  나이:___  ← 칸만 정하면       │
  │  나머지(비교, 출력 등)는 자동 처리!       │
  └──────────────────────────────────────────┘

★ record가 자동으로 만들어주는 것
  ┌────────────────────────────────┐
  │ 1. private final 필드들        │
  │ 2. 모든 필드를 받는 생성자     │
  │ 3. 각 필드의 접근자 (getter)   │
  │    → name() (getName() 아님!) │
  │ 4. equals() & hashCode()      │
  │ 5. toString()                 │
  └────────────────────────────────┘

★ class 100줄 → record 1줄!
  // 기존 방식 (보일러플레이트 가득!)
  class Student {
      private final String name;
      private final int score;
      // 생성자, getter, equals, hashCode, toString...
  }

  // record 방식 (1줄!)
  record Student(String name, int score) {}
*/

// ─── record 예제 ────────────────────────────────────────
record Student(String name, int score, int homeworkCount) {
    // record 안에 메서드를 추가할 수 있음!
    String gradeLabel() {
        if (score >= 90) return "우수";
        if (score >= 70) return "통과";
        return "복습 필요";
    }

    boolean isPassed() {
        return score >= 60;
    }

    // ★ compact constructor: 유효성 검사에 사용
    Student {
        if (score < 0 || score > 100) {
            throw new IllegalArgumentException("점수는 0~100 사이여야 합니다: " + score);
        }
        if (homeworkCount < 0) {
            throw new IllegalArgumentException("숙제 횟수는 0 이상이어야 합니다: " + homeworkCount);
        }
    }
}

record Point(double x, double y) {
    double distanceTo(Point other) {
        return Math.sqrt(Math.pow(x - other.x, 2) + Math.pow(y - other.y, 2));
    }

    // 정적 팩토리 메서드
    static Point origin() {
        return new Point(0, 0);
    }
}


// =====================================================================
// 레슨 3 — switch 표현식 (Java 14)
// =====================================================================
/*
★ switch 표현식 = switch가 "값을 반환"할 수 있게 됨!
  → 화살표(->)를 사용하여 더 깔끔하게!
  → break 대신 yield (여러 줄일 때)

  ┌───────────────────────────────────────────┐
  │  기존 switch (문장)                       │
  │  switch(x) {                              │
  │      case 1: result = "one"; break;       │
  │      case 2: result = "two"; break;       │
  │      default: result = "?";               │
  │  }                                        │
  │                                           │
  │  새 switch (표현식)                        │
  │  var result = switch(x) {                 │
  │      case 1 -> "one";                     │
  │      case 2 -> "two";                     │
  │      default -> "?";                      │
  │  };                                       │
  └───────────────────────────────────────────┘

★ switch 표현식 장점
  1. break를 안 써도 됨 (fall-through 없음!)
  2. 값을 반환할 수 있음
  3. 여러 case를 쉼표로 묶을 수 있음
  4. 컴파일러가 모든 경우를 검사 (exhaustiveness check)
*/


// =====================================================================
// 레슨 4 — 텍스트 블록 (Java 15)
// =====================================================================
/*
★ 텍스트 블록 = 여러 줄 문자열을 깔끔하게 작성

  기존: "line1\n" + "line2\n" + "line3"
  텍스트 블록:
  \"\"\"
  line1
  line2
  line3
  \"\"\"

  → HTML, JSON, SQL 등 여러 줄 텍스트에 완벽!
*/


// =====================================================================
// 레슨 5 — sealed class (봉인 클래스, Java 17)
// =====================================================================
/*
★ sealed = "허가된 자식만 상속 가능"
  → 상속을 제한하여 타입 계층을 완벽하게 제어!

  ┌──────────────────────────────────────────────┐
  │  비유: sealed는 "초대장 파티"                 │
  │                                              │
  │  일반 class: 아무나 상속 가능 (개방 파티)     │
  │  final class: 아무도 상속 불가 (파티 없음)    │
  │  sealed class: 초대받은 사람만! (VIP 파티)    │
  └──────────────────────────────────────────────┘

★ 허가된 자식은 3가지 중 하나를 선택:
  final    → 더 이상 상속 불가
  sealed   → 또 다른 sealed 계층
  non-sealed → 자유롭게 상속 가능
*/

// ─── sealed class 예제 ──────────────────────────────────
sealed interface PaymentMethod permits CreditCard, Cash, BankTransfer {}

record CreditCard(String cardNumber, String owner) implements PaymentMethod {}
record Cash(int amount) implements PaymentMethod {}
record BankTransfer(String bankName, String accountNumber) implements PaymentMethod {}


// =====================================================================
// 레슨 6 — 패턴 매칭 instanceof (Java 16)
// =====================================================================
/*
★ 패턴 매칭 = instanceof 검사와 캐스팅을 한 번에!

  // 기존 방식 (2단계)
  if (obj instanceof String) {
      String s = (String) obj;  // 캐스팅 따로!
      s.length();
  }

  // 패턴 매칭 (1단계)
  if (obj instanceof String s) {  // 검사 + 캐스팅 동시!
      s.length();
  }
*/


// =====================================================================
//  메인 실행
// =====================================================================
public class Main {

    // ─── switch 표현식 활용 메서드 ──────────────────────
    static String dayType(String day) {
        return switch (day) {
            case "월", "화", "수", "목", "금" -> "평일";
            case "토", "일" -> "주말";
            default -> "알 수 없는 요일";
        };
    }

    static String gradeMessage(String grade) {
        return switch (grade) {
            case "A" -> "훌륭합니다!";
            case "B" -> "잘했습니다!";
            case "C" -> "괜찮습니다. 조금 더 노력해보세요.";
            case "D" -> "분발이 필요합니다.";
            case "F" -> {
                // 여러 줄일 때 yield 사용
                String msg = "재시험이 필요합니다.";
                yield "⚠ " + msg;
            }
            default -> "알 수 없는 등급";
        };
    }

    // ─── 패턴 매칭 활용 메서드 ──────────────────────────
    static String describePayment(PaymentMethod pm) {
        // sealed + 패턴 매칭 = 완벽한 조합!
        if (pm instanceof CreditCard cc) {
            return "카드 결제: " + cc.owner() + "의 " + cc.cardNumber();
        } else if (pm instanceof Cash c) {
            return "현금 결제: " + c.amount() + "원";
        } else if (pm instanceof BankTransfer bt) {
            return "계좌 이체: " + bt.bankName() + " " + bt.accountNumber();
        }
        return "알 수 없는 결제";
    }

    static String describeObject(Object obj) {
        // 패턴 매칭으로 타입별 처리
        if (obj instanceof Integer i) {
            return "정수: " + i;
        } else if (obj instanceof String s && !s.isEmpty()) {
            return "문자열(길이=" + s.length() + "): " + s;
        } else if (obj instanceof double[] arr) {
            return "실수 배열(길이=" + arr.length + ")";
        } else if (obj instanceof List<?> list) {
            return "리스트(크기=" + list.size() + ")";
        } else if (obj == null) {
            return "null!";
        }
        return "기타: " + obj.getClass().getSimpleName();
    }

    public static void main(String[] args) {
        System.out.println("■■■ Java 10단계: 현대 Java 기능 ■■■\n");

        // ─── 레슨 1: var ────────────────────────────────
        System.out.println("── 레슨 1: var (타입 추론) ──────────────────────");

        var message = "Hello, Java!";  // String으로 추론
        var count = 42;                 // int로 추론
        var pi = 3.14;                  // double로 추론
        var names = new ArrayList<String>();  // ArrayList<String>으로 추론

        names.add("Alice");
        names.add("Bob");

        System.out.println("  message의 타입: " + message.getClass().getSimpleName());
        System.out.println("  names의 타입: " + names.getClass().getSimpleName());
        System.out.println("  names: " + names);

        // var + for문
        var numbers = List.of(1, 2, 3, 4, 5);
        System.out.print("  var로 for문: ");
        for (var n : numbers) {
            System.out.print(n + " ");
        }
        System.out.println("\n");

        // ─── 레슨 2: record ─────────────────────────────
        System.out.println("── 레슨 2: record (불변 데이터 클래스) ──────────");

        var s1 = new Student("김철수", 92, 10);
        var s2 = new Student("이영희", 78, 8);
        var s3 = new Student("김철수", 92, 10);  // s1과 같은 값

        System.out.println("  s1: " + s1);         // 자동 toString()
        System.out.println("  s2: " + s2);
        System.out.println("  s1 이름: " + s1.name());   // getter는 name() (getName 아님!)
        System.out.println("  s1 등급: " + s1.gradeLabel());
        System.out.println("  s1 == s3? " + s1.equals(s3));  // 자동 equals()!

        // record는 불변! setter 없음!
        // s1.name = "홍길동";  ← 컴파일 에러!

        // Point record
        var p1 = new Point(3, 4);
        var p2 = Point.origin();
        System.out.println("  p1: " + p1);
        System.out.println("  원점까지 거리: " + String.format("%.2f", p1.distanceTo(p2)));

        // compact constructor 유효성 검사
        try {
            new Student("테스트", 150, 5);  // 점수 범위 초과!
        } catch (IllegalArgumentException e) {
            System.out.println("  ★ 유효성 검사: " + e.getMessage());
        }
        System.out.println();

        // ─── 레슨 3: switch 표현식 ──────────────────────
        System.out.println("── 레슨 3: switch 표현식 (Java 14) ──────────────");

        String[] days = {"월", "수", "토", "일"};
        for (var day : days) {
            System.out.println("  " + day + "요일 → " + dayType(day));
        }

        System.out.println();
        String[] grades = {"A", "B", "C", "D", "F"};
        for (var grade : grades) {
            System.out.println("  " + grade + " → " + gradeMessage(grade));
        }
        System.out.println();

        // ─── 레슨 4: 텍스트 블록 ────────────────────────
        System.out.println("── 레슨 4: 텍스트 블록 (Java 15) ────────────────");

        // 기존 방식
        var oldJson = "{\n  \"name\": \"홍길동\",\n  \"age\": 25\n}";

        // 텍스트 블록 방식
        var newJson = """
                {
                  "name": "홍길동",
                  "age": 25,
                  "grade": "A"
                }
                """;

        System.out.println("  기존 JSON:");
        System.out.println("  " + oldJson);
        System.out.println("  텍스트 블록 JSON:");
        System.out.print("  " + newJson);

        // SQL 예제
        var sql = """
                SELECT name, score
                FROM students
                WHERE score >= 80
                ORDER BY score DESC
                """;
        System.out.println("  SQL 쿼리:");
        System.out.print("  " + sql);

        // HTML 예제
        var html = """
                <div class="student">
                  <h2>%s</h2>
                  <p>점수: %d</p>
                </div>
                """.formatted(s1.name(), s1.score());
        System.out.println("  HTML (formatted):");
        System.out.print("  " + html);
        System.out.println();

        // ─── 레슨 5: sealed class ───────────────────────
        System.out.println("── 레슨 5: sealed class (Java 17) ───────────────");

        PaymentMethod[] payments = {
            new CreditCard("1234-5678", "홍길동"),
            new Cash(50000),
            new BankTransfer("국민은행", "123-456-789")
        };

        for (var pm : payments) {
            System.out.println("  " + describePayment(pm));
        }
        System.out.println();

        // ─── 레슨 6: 패턴 매칭 instanceof ───────────────
        System.out.println("── 레슨 6: 패턴 매칭 instanceof (Java 16) ──────");

        Object[] objects = {
            42,
            "Hello Java",
            3.14,
            new double[]{1.0, 2.0, 3.0},
            List.of("a", "b", "c"),
            null,
            new Point(1, 2)
        };

        for (var obj : objects) {
            System.out.println("  " + describeObject(obj));
        }
        System.out.println();

        // ─── 종합 예제: 현대 Java 총동원 ────────────────
        System.out.println("── 종합 예제: 현대 Java 기능 총동원 ─────────────");

        var students = List.of(
            new Student("김철수", 92, 10),
            new Student("이영희", 78, 8),
            new Student("박민수", 55, 5),
            new Student("최지은", 88, 9),
            new Student("정하나", 95, 10)
        );

        // var + stream + record
        var passedNames = students.stream()
                .filter(Student::isPassed)
                .map(Student::name)
                .collect(Collectors.joining(", "));
        System.out.println("  통과자: " + passedNames);

        // switch 표현식 + record
        for (var st : students) {
            var emoji = switch (st.gradeLabel()) {
                case "우수" -> "★";
                case "통과" -> "○";
                default -> "△";
            };
            System.out.println("  " + emoji + " " + st.name()
                    + " (" + st.score() + "점, " + st.gradeLabel() + ")");
        }

        // 텍스트 블록으로 보고서 생성
        var avgScore = students.stream()
                .mapToInt(Student::score)
                .average()
                .orElse(0);
        var totalHomework = students.stream()
                .mapToInt(Student::homeworkCount)
                .sum();

        var report = """

                  ┌────────────────────────────┐
                  │     성적 분석 보고서        │
                  ├────────────────────────────┤
                  │  총 학생 수: %d명            │
                  │  평균 점수: %.1f점           │
                  │  총 숙제: %d개               │
                  │  통과율: %.0f%%              │
                  └────────────────────────────┘
                """.formatted(
                students.size(),
                avgScore,
                totalHomework,
                students.stream().filter(Student::isPassed).count() * 100.0 / students.size()
        );
        System.out.print(report);

        System.out.println("■■■ 10단계 학습 완료! ■■■");
    }
}
