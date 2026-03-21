/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Java 학습 08단계: 예외 처리와 파일 입출력
  ─ try/catch/finally, throws, 커스텀 예외, File I/O ─

  [학습 목표]
  1. 예외의 개념과 종류(checked vs unchecked)를 안다
  2. try-catch-finally 문법을 이해한다
  3. throw와 throws의 차이를 안다
  4. 커스텀 예외를 만들 수 있다
  5. 파일 읽기/쓰기를 할 수 있다
  6. try-with-resources를 이해한다

  ■ 컴파일: javac Main.java
  ■ 실행:   java Main

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

import java.io.*;
import java.nio.file.*;
import java.util.List;


// =====================================================================
// 레슨 1 — 예외란 무엇인가?
// =====================================================================
/*
★ 예외(Exception) = 프로그램 실행 중 발생하는 "비정상적인 상황"
  → 숫자를 기대했는데 글자가 들어왔다!
  → 파일을 열려는데 파일이 없다!
  → 배열 범위를 벗어났다!

  ┌──────────────────────────────────────────┐
  │  비유: 예외는 "비상벨"                    │
  │                                          │
  │  요리 중 불이 나면 → 비상벨이 울림        │
  │  그냥 무시하면   → 건물이 타버림 (crash!)│
  │  대응하면        → 불을 끄고 계속 요리!  │
  │                                          │
  │  try { 요리한다 }                        │
  │  catch (불Exception e) { 소화기 사용 }   │
  │  finally { 가스 잠근다 }                 │
  └──────────────────────────────────────────┘

★ 예외 계층 구조
  ┌─────────────────────────────────────────┐
  │  Throwable                               │
  │  ├── Error (심각! 복구 불가)             │
  │  │   ├── OutOfMemoryError               │
  │  │   └── StackOverflowError             │
  │  └── Exception                           │
  │      ├── IOException (checked)           │
  │      ├── SQLException (checked)          │
  │      └── RuntimeException (unchecked)    │
  │          ├── NullPointerException        │
  │          ├── ArrayIndexOutOfBoundsException│
  │          ├── NumberFormatException        │
  │          └── IllegalArgumentException    │
  └─────────────────────────────────────────┘

★ Checked vs Unchecked 예외
  ┌──────────────┬────────────────────────────────┐
  │ Checked      │ 컴파일러가 처리를 강제함         │
  │              │ try-catch 또는 throws 필수      │
  │              │ 예: IOException, SQLException   │
  ├──────────────┼────────────────────────────────┤
  │ Unchecked    │ 컴파일러가 강제하지 않음         │
  │              │ RuntimeException의 하위 클래스  │
  │              │ 예: NullPointerException        │
  └──────────────┴────────────────────────────────┘
*/


// =====================================================================
// 레슨 2 — try-catch-finally
// =====================================================================
/*
★ 기본 구조:
  try {
      // 위험한 코드 (예외가 발생할 수 있는 부분)
  } catch (예외타입1 e) {
      // 예외 처리 1
  } catch (예외타입2 e) {
      // 예외 처리 2
  } finally {
      // 항상 실행 (선택사항)
  }

★ finally 블록
  → 예외 발생 여부와 상관없이 항상 실행됨!
  → 파일 닫기, 연결 끊기 등 "정리 작업"에 사용

★ 멀티 캐치 (Java 7+)
  catch (IOException | SQLException e) {
      // 여러 예외를 한 번에 처리
  }
*/


// =====================================================================
// 레슨 3 — throw와 throws
// =====================================================================
/*
★ throw vs throws
  ┌───────────┬──────────────────────────────────┐
  │ throw     │ 예외를 직접 "던지는" 행동         │
  │           │ throw new IllegalArgumentException│
  ├───────────┼──────────────────────────────────┤
  │ throws    │ 메서드 선언에 붙여 "이 메서드는  │
  │           │ 이런 예외를 던질 수 있다"고 알림  │
  │           │ void read() throws IOException   │
  └───────────┴──────────────────────────────────┘
*/


// =====================================================================
// 레슨 4 — 커스텀 예외
// =====================================================================
/*
★ 자신만의 예외를 만들 수 있음!
  → Exception을 상속하면 checked 예외
  → RuntimeException을 상속하면 unchecked 예외

  ┌─────────────────────────────────────────┐
  │  비유: 가게 자체 규칙                    │
  │                                         │
  │  "나이 확인 실패!" → AgeException       │
  │  "잔액 부족!" → InsufficientFundException│
  │                                         │
  │  기본 예외로는 표현 못하는 비즈니스 규칙│
  │  을 명확하게 표현!                      │
  └─────────────────────────────────────────┘
*/

// ─── 커스텀 예외 정의 ───────────────────────────────────
class InvalidScoreException extends RuntimeException {
    private final int score;

    InvalidScoreException(int score) {
        super("유효하지 않은 점수: " + score + " (0~100 사이여야 합니다)");
        this.score = score;
    }

    int getScore() {
        return score;
    }
}

class InsufficientBalanceException extends Exception {
    private final int requested;
    private final int available;

    InsufficientBalanceException(int requested, int available) {
        super("잔액 부족! 요청: " + requested + "원, 잔액: " + available + "원");
        this.requested = requested;
        this.available = available;
    }

    int getShortage() {
        return requested - available;
    }
}


// =====================================================================
// 레슨 5 — 파일 입출력 (File I/O)
// =====================================================================
/*
★ Java 파일 I/O 방법들
  ┌─────────────────────────┬──────────────────────────────┐
  │ 방법                    │ 특징                          │
  ├─────────────────────────┼──────────────────────────────┤
  │ Files.readString()      │ 파일 전체를 문자열로 (간단!) │
  │ Files.readAllLines()    │ 줄 단위 List<String>          │
  │ Files.writeString()     │ 문자열을 파일에 쓰기          │
  │ BufferedReader/Writer   │ 대용량 파일에 효율적          │
  │ Scanner                 │ 파싱에 편리                   │
  └─────────────────────────┴──────────────────────────────┘

★ try-with-resources (Java 7+)
  → 자원(파일, 연결 등)을 자동으로 닫아줌!
  → AutoCloseable 인터페이스를 구현한 객체 사용

  try (BufferedReader br = new BufferedReader(...)) {
      // br 사용
  }  // ← 여기서 자동으로 br.close() 호출!

  ┌──────────────────────────────────────────┐
  │  비유: try-with-resources는 "자동 수도꼭지"│
  │                                          │
  │  일반 수도꼭지: 물 쓰고 잠그는 걸 잊으면 │
  │                물이 계속 흐름! (자원 누수)│
  │                                          │
  │  자동 수도꼭지: 손 떼면 자동으로 잠김!    │
  │                (자원 자동 해제)           │
  └──────────────────────────────────────────┘
*/


// =====================================================================
// 레슨 6 — 흔한 실수 모음
// =====================================================================
/*
★ 실수 1: 너무 넓은 catch
  catch (Exception e) { }  ← 모든 예외를 삼켜버림! 디버깅 불가!
  → 구체적인 예외 타입을 잡을 것!

★ 실수 2: catch 블록을 비워둠
  catch (IOException e) { }  ← 아무것도 안 함! 문제가 사라진 게 아님!
  → 최소한 로그라도 남기자: e.printStackTrace();

★ 실수 3: finally에서 return
  try { return 1; } finally { return 2; }
  → 결과는 2! finally의 return이 덮어씀! 절대 하지 말 것!

★ 실수 4: 파일 닫기를 잊음
  FileReader fr = new FileReader("file.txt");
  // ... 사용 ...
  // fr.close()를 잊으면 자원 누수!
  → try-with-resources를 사용하면 자동으로 해결!
*/


// =====================================================================
//  도우미 클래스: 간단한 은행 계좌
// =====================================================================
class BankAccount {
    private String owner;
    private int balance;

    BankAccount(String owner, int balance) {
        this.owner = owner;
        this.balance = balance;
    }

    // throws → checked 예외를 던질 수 있다고 선언
    void withdraw(int amount) throws InsufficientBalanceException {
        if (amount <= 0) {
            // throw → 예외를 직접 던짐 (unchecked이므로 throws 선언 불필요)
            throw new IllegalArgumentException("출금액은 양수여야 합니다: " + amount);
        }
        if (amount > balance) {
            throw new InsufficientBalanceException(amount, balance);
        }
        balance -= amount;
    }

    void deposit(int amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("입금액은 양수여야 합니다: " + amount);
        }
        balance += amount;
    }

    int getBalance() { return balance; }
    String getOwner() { return owner; }
}


// =====================================================================
//  메인 실행
// =====================================================================
public class Main {
    private static final Path LESSON_FOLDER = Path.of("java-learning", "08_exceptions_file_io");
    private static final Path SAMPLE_FILE = LESSON_FOLDER.resolve("sample.txt");

    // ─── 점수 검증 메서드 ───────────────────────────────
    static String gradeFromScore(int score) {
        if (score < 0 || score > 100) {
            throw new InvalidScoreException(score);
        }
        if (score >= 90) return "A";
        if (score >= 80) return "B";
        if (score >= 70) return "C";
        if (score >= 60) return "D";
        return "F";
    }

    // ─── 숫자 파싱 안전하게 ─────────────────────────────
    static int safeParseInt(String text, int defaultValue) {
        try {
            return Integer.parseInt(text);
        } catch (NumberFormatException e) {
            System.out.println("    ('" + text + "'는 숫자가 아닙니다. 기본값 "
                    + defaultValue + " 사용)");
            return defaultValue;
        }
    }

    public static void main(String[] args) {
        System.out.println("■■■ Java 08단계: 예외 처리와 파일 입출력 ■■■\n");

        // ─── 레슨 1~2: try-catch-finally ─────────────────
        System.out.println("── 레슨 1~2: try-catch-finally ──────────────────");

        // 예외 1: NumberFormatException (unchecked)
        String[] inputs = {"42", "hello", "100", "3.14", "-5"};
        for (String input : inputs) {
            int result = safeParseInt(input, 0);
            System.out.println("  parseint(\"" + input + "\") = " + result);
        }
        System.out.println();

        // 예외 2: ArrayIndexOutOfBoundsException
        System.out.println("  --- 배열 범위 초과 ---");
        int[] arr = {10, 20, 30};
        try {
            System.out.println("  arr[5] = " + arr[5]);  // 범위 초과!
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("  ★ 배열 범위 초과! 인덱스 5는 없습니다.");
            System.out.println("    메시지: " + e.getMessage());
        } finally {
            System.out.println("  (finally: 배열 접근 테스트 종료)");
        }
        System.out.println();

        // 예외 3: NullPointerException
        System.out.println("  --- Null 참조 ---");
        String text = null;
        try {
            System.out.println("  길이: " + text.length());
        } catch (NullPointerException e) {
            System.out.println("  ★ NullPointerException! null에 .length() 호출 불가");
        }
        System.out.println();

        // ─── 레슨 3: throw와 throws ─────────────────────
        System.out.println("── 레슨 3: throw와 throws ──────────────────────");

        // 커스텀 예외 (unchecked)
        int[] testScores = {85, 105, -10, 72};
        for (int score : testScores) {
            try {
                String grade = gradeFromScore(score);
                System.out.println("  점수 " + score + " → 등급 " + grade);
            } catch (InvalidScoreException e) {
                System.out.println("  ★ " + e.getMessage());
            }
        }
        System.out.println();

        // ─── 레슨 4: 커스텀 예외와 은행 계좌 ────────────
        System.out.println("── 레슨 4: 커스텀 예외 (은행 계좌) ──────────────");
        BankAccount account = new BankAccount("홍길동", 10000);
        System.out.println("  계좌: " + account.getOwner()
                + ", 잔액: " + account.getBalance() + "원");

        // 정상 출금
        try {
            account.withdraw(3000);
            System.out.println("  3000원 출금 성공! 잔액: " + account.getBalance() + "원");
        } catch (InsufficientBalanceException e) {
            System.out.println("  ★ " + e.getMessage());
        }

        // 잔액 부족 출금
        try {
            account.withdraw(50000);
        } catch (InsufficientBalanceException e) {
            System.out.println("  ★ " + e.getMessage());
            System.out.println("    부족액: " + e.getShortage() + "원");
        }

        // 잘못된 금액 출금 (unchecked → throws 선언 불필요)
        try {
            account.withdraw(-100);
        } catch (IllegalArgumentException e) {
            System.out.println("  ★ " + e.getMessage());
        }
        System.out.println();

        // ─── 레슨 5: 파일 입출력 ─────────────────────────
        System.out.println("── 레슨 5: 파일 입출력 ──────────────────────────");

        // 파일 쓰기 (Files.writeString)
        try {
            Files.createDirectories(LESSON_FOLDER);
            String content = "이름: 김철수\n점수: 92\n등급: A\n"
                    + "이름: 이영희\n점수: 78\n등급: C\n"
                    + "이름: 박민수\n점수: 55\n등급: F\n";
            Files.writeString(SAMPLE_FILE, content);
            System.out.println("  파일 쓰기 완료: " + SAMPLE_FILE);
        } catch (IOException e) {
            System.out.println("  ★ 파일 쓰기 실패: " + e.getMessage());
        }

        // 파일 읽기 (Files.readAllLines)
        try {
            List<String> lines = Files.readAllLines(SAMPLE_FILE);
            System.out.println("  파일 내용 (" + lines.size() + "줄):");
            for (String line : lines) {
                System.out.println("    | " + line);
            }
        } catch (IOException e) {
            System.out.println("  ★ 파일 읽기 실패: " + e.getMessage());
        }
        System.out.println();

        // BufferedWriter/Reader로 대용량 파일 처리
        System.out.println("  --- BufferedWriter/Reader ---");
        Path bufferedFile = LESSON_FOLDER.resolve("buffered_sample.txt");

        // try-with-resources: 자동으로 파일 닫기!
        try (BufferedWriter bw = Files.newBufferedWriter(bufferedFile)) {
            for (int i = 1; i <= 5; i++) {
                bw.write("줄 " + i + ": 반복 데이터입니다.\n");
            }
            System.out.println("  BufferedWriter 쓰기 완료: " + bufferedFile);
        } catch (IOException e) {
            System.out.println("  ★ 쓰기 실패: " + e.getMessage());
        }

        try (BufferedReader br = Files.newBufferedReader(bufferedFile)) {
            String line;
            System.out.println("  BufferedReader 읽기:");
            while ((line = br.readLine()) != null) {
                System.out.println("    | " + line);
            }
        } catch (IOException e) {
            System.out.println("  ★ 읽기 실패: " + e.getMessage());
        }
        System.out.println();

        // 존재하지 않는 파일 읽기 시도
        System.out.println("  --- 존재하지 않는 파일 ---");
        try {
            Files.readString(Path.of("없는파일.txt"));
        } catch (IOException e) {
            System.out.println("  ★ 파일 없음: " + e.getClass().getSimpleName());
        }
        System.out.println();

        // ─── 레슨 6: 흔한 실수 시연 ─────────────────────
        System.out.println("── 레슨 6: 흔한 실수 정리 ───────────────────────");
        System.out.println("  ★ catch (Exception e) {} ← 모든 예외를 삼킴! 위험!");
        System.out.println("  ★ catch 블록 비워두면 문제 원인을 알 수 없음");
        System.out.println("  ★ finally에서 return하면 try의 return을 덮어씀!");
        System.out.println("  ★ 파일 닫기 → try-with-resources 사용이 최선!");
        System.out.println();

        // ─── 종합 예제: 학생 성적 파일 처리 ──────────────
        System.out.println("── 종합 예제: 학생 성적 파일 처리 ───────────────");
        Path gradeFile = LESSON_FOLDER.resolve("grades.txt");

        // 성적 파일 생성
        try (BufferedWriter bw = Files.newBufferedWriter(gradeFile)) {
            String[] students = {"홍길동,92", "성춘향,88", "이몽룡,75", "변학도,bad", "심청,95"};
            for (String s : students) {
                bw.write(s + "\n");
            }
            System.out.println("  성적 파일 생성 완료");
        } catch (IOException e) {
            System.out.println("  ★ " + e.getMessage());
        }

        // 성적 파일 읽기 + 예외 처리
        try (BufferedReader br = Files.newBufferedReader(gradeFile)) {
            String line;
            int total = 0, count = 0;
            System.out.println("  ┌─────────┬──────┬──────┐");
            System.out.println("  │ 이름    │ 점수 │ 등급 │");
            System.out.println("  ├─────────┼──────┼──────┤");
            while ((line = br.readLine()) != null) {
                String[] parts = line.split(",");
                if (parts.length != 2) continue;
                try {
                    int score = Integer.parseInt(parts[1].trim());
                    String grade = gradeFromScore(score);
                    System.out.printf("  │ %-7s │ %4d │  %s   │%n", parts[0], score, grade);
                    total += score;
                    count++;
                } catch (NumberFormatException e) {
                    System.out.printf("  │ %-7s │ 오류 │  -   │ ← 숫자가 아님!%n", parts[0]);
                }
            }
            System.out.println("  └─────────┴──────┴──────┘");
            if (count > 0) {
                System.out.printf("  평균: %.1f점 (%d명)%n", (double) total / count, count);
            }
        } catch (IOException e) {
            System.out.println("  ★ " + e.getMessage());
        }
        System.out.println();

        System.out.println("■■■ 08단계 학습 완료! ■■■");
    }
}
