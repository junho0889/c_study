/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Java 학습 11단계: 디버깅
  ─ 버그 재현, 로깅, 스택 트레이스, 디버거 사용법, 흔한 버그 ─

  [학습 목표]
  1. 버그를 체계적으로 재현하고 원인을 찾는 법을 안다
  2. System.out 대신 로깅을 활용한다
  3. 스택 트레이스를 읽고 해석할 수 있다
  4. IDE 디버거의 기본 기능을 안다
  5. 자주 발생하는 Java 버그 패턴을 인식한다
  6. 방어적 프로그래밍으로 버그를 예방한다

  ■ 컴파일: javac Main.java
  ■ 실행:   java Main

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

import java.util.*;
import java.util.logging.*;


// =====================================================================
// 레슨 1 — 버그 재현의 중요성
// =====================================================================
/*
★ 디버깅의 첫 단계 = "버그를 재현할 수 있는가?"
  → 재현할 수 없으면 고칠 수도 없다!

  ┌──────────────────────────────────────────┐
  │  디버깅 5단계 프로세스                    │
  │                                          │
  │  1. 재현 → 버그가 발생하는 조건 찾기     │
  │  2. 격리 → 문제 범위를 좁히기            │
  │  3. 진단 → 원인 파악                     │
  │  4. 수정 → 코드 고치기                   │
  │  5. 검증 → 다시 테스트하여 확인          │
  └──────────────────────────────────────────┘

  ┌──────────────────────────────────────────────┐
  │  비유: 디버깅은 "의사의 진찰"                 │
  │                                              │
  │  1단계: "어디가 아프세요?" (증상 확인)        │
  │  2단계: "언제부터요?" (재현 조건)             │
  │  3단계: "검사해봅시다" (원인 파악)             │
  │  4단계: "약 처방" (수정)                      │
  │  5단계: "다음 주 내원" (검증)                 │
  └──────────────────────────────────────────────┘
*/


// =====================================================================
// 레슨 2 — 스택 트레이스 읽기
// =====================================================================
/*
★ 스택 트레이스 = 예외가 발생했을 때 "어디서 무엇이 잘못됐는지" 알려주는 추적 기록

  java.lang.NullPointerException: Cannot invoke "String.length()"
      at Main.processName(Main.java:42)     ← 여기서 발생!
      at Main.handleStudent(Main.java:35)   ← 이 메서드가 호출
      at Main.main(Main.java:10)            ← main에서 시작

  ★ 읽는 법: 위에서부터 아래로!
    1번째 줄: 예외 종류와 메시지
    2번째 줄: 실제 발생 위치 (가장 중요!)
    나머지:   호출 순서 (아래가 먼저 호출됨)

  ┌──────────────────────────────────────────┐
  │  비유: 스택 트레이스는 "빵 부스러기 자국"│
  │                                          │
  │  main → handleStudent → processName     │
  │                             ↑ 여기서 폭발!│
  │                                          │
  │  자국을 따라가면 범인(버그)을 찾을 수 있다│
  └──────────────────────────────────────────┘
*/


// =====================================================================
// 레슨 3 — IDE 디버거 기본 기능
// =====================================================================
/*
★ IDE 디버거의 핵심 기능들

  ┌──────────────────┬──────────────────────────────────┐
  │ 기능             │ 설명                              │
  ├──────────────────┼──────────────────────────────────┤
  │ 브레이크포인트   │ 코드 실행을 멈출 위치 지정        │
  │ (Breakpoint)     │ → 줄 번호 클릭!                  │
  ├──────────────────┼──────────────────────────────────┤
  │ Step Over (F8)   │ 현재 줄 실행, 다음 줄로           │
  │                  │ → 메서드 안으로 들어가지 않음     │
  ├──────────────────┼──────────────────────────────────┤
  │ Step Into (F7)   │ 메서드 안으로 들어감              │
  │                  │ → 메서드 내부를 자세히 볼 때      │
  ├──────────────────┼──────────────────────────────────┤
  │ Step Out         │ 현재 메서드를 빠져나감            │
  │                  │ → 호출한 곳으로 돌아감            │
  ├──────────────────┼──────────────────────────────────┤
  │ Resume (F9)      │ 다음 브레이크포인트까지 계속 실행 │
  ├──────────────────┼──────────────────────────────────┤
  │ Watch            │ 변수 값을 실시간으로 감시         │
  │                  │ → 변수 이름 우클릭 → Add Watch   │
  ├──────────────────┼──────────────────────────────────┤
  │ Evaluate         │ 실행 중에 식을 평가               │
  │ Expression       │ → 원하는 코드를 즉석에서 실행!   │
  └──────────────────┴──────────────────────────────────┘

  ┌──────────────────────────────────────────────┐
  │  비유: 디버거는 "느린 재생 리모컨"             │
  │                                              │
  │  Step Over: ▶ 한 줄씩 천천히                 │
  │  Step Into: 🔍 자세히 보기                    │
  │  Resume:   ⏩ 빨리감기                       │
  │  Watch:    👀 실시간 모니터                   │
  └──────────────────────────────────────────────┘
*/


// =====================================================================
// 레슨 4 — java.util.logging
// =====================================================================
/*
★ System.out.println() 대신 Logger 사용!

  왜?
  ┌────────────────────┬────────────────────────────────┐
  │ System.out.println │ Logger                          │
  ├────────────────────┼────────────────────────────────┤
  │ 레벨 구분 없음     │ SEVERE/WARNING/INFO/FINE 등    │
  │ 끄기 어려움        │ 레벨별로 on/off 가능            │
  │ 콘솔만 출력        │ 파일, 콘솔, 네트워크 등        │
  │ 성능 영향          │ 비활성 로그는 영향 없음         │
  └────────────────────┴────────────────────────────────┘

★ 로그 레벨 (높은 순)
  SEVERE  → 심각한 오류 (시스템 중단급)
  WARNING → 경고 (문제가 될 수 있음)
  INFO    → 정보 (일반적인 진행 상황)
  CONFIG  → 설정 정보
  FINE    → 디버깅 정보 (상세)
  FINER   → 더 상세
  FINEST  → 가장 상세
*/


// =====================================================================
// 레슨 5 — 흔한 Java 버그 패턴
// =====================================================================
/*
★ 버그 패턴 TOP 10

  ┌──────┬──────────────────────────┬──────────────────────────┐
  │ 순위 │ 버그                     │ 원인                     │
  ├──────┼──────────────────────────┼──────────────────────────┤
  │  1   │ NullPointerException     │ null 체크 누락            │
  │  2   │ Off-by-one 에러          │ 배열 인덱스 ±1 실수      │
  │  3   │ == vs equals             │ 문자열 비교 실수          │
  │  4   │ Integer overflow         │ int 범위 초과             │
  │  5   │ ConcurrentModification   │ 순회 중 컬렉션 수정      │
  │  6   │ 부동소수점 비교          │ 0.1 + 0.2 != 0.3        │
  │  7   │ 잘못된 평균 계산         │ 정수 나눗셈              │
  │  8   │ autoboxing NPE           │ Integer unboxing 시 null │
  │  9   │ StringBuilder 미사용     │ 반복문에서 + 연결        │
  │ 10   │ 리소스 누수              │ close() 호출 누락        │
  └──────┴──────────────────────────┴──────────────────────────┘
*/


// =====================================================================
// 레슨 6 — 방어적 프로그래밍
// =====================================================================
/*
★ 방어적 프로그래밍 = "믿지 말고, 확인하라!"
  → 입력값을 항상 검증하고, 예상치 못한 상황에 대비

  ┌──────────────────────────────────────────────┐
  │  규칙 1: null 체크를 습관화                   │
  │  규칙 2: 매개변수 유효성 검사                 │
  │  규칙 3: 불변 객체 선호                       │
  │  규칙 4: assert로 전제 조건 명시             │
  │  규칙 5: Objects.requireNonNull() 활용       │
  └──────────────────────────────────────────────┘
*/


// =====================================================================
//  버그 시연용 클래스들
// =====================================================================
class BuggyCalculator {
    // ★ 버그 1: Off-by-one 에러 (잘못된 평균 계산)
    static int wrongAverage(int[] values) {
        int total = 0;
        for (int value : values) {
            total += value;
        }
        return total / (values.length - 1);  // ★ 버그! length - 1이 아님!
    }

    // 수정된 버전
    static double correctAverage(int[] values) {
        if (values.length == 0) return 0;  // 방어 코드
        int total = 0;
        for (int value : values) {
            total += value;
        }
        return (double) total / values.length;  // ★ double 캐스팅도 중요!
    }

    // ★ 버그 2: == vs equals
    static boolean wrongStringCompare(String a, String b) {
        return a == b;  // ★ 버그! 참조 비교 (주소가 같은지)
    }

    static boolean correctStringCompare(String a, String b) {
        return Objects.equals(a, b);  // ★ 올바른 비교 (null-safe)
    }

    // ★ 버그 3: Integer overflow
    static int wrongFactorial(int n) {
        int result = 1;
        for (int i = 1; i <= n; i++) {
            result *= i;  // ★ n이 크면 int 범위 초과!
        }
        return result;
    }

    static long correctFactorial(int n) {
        long result = 1;  // ★ long 사용!
        for (int i = 1; i <= n; i++) {
            result *= i;
        }
        return result;
    }

    // ★ 버그 4: 부동소수점 비교
    static boolean wrongDoubleCompare(double a, double b) {
        return a == b;  // ★ 부동소수점은 == 비교하면 안 됨!
    }

    static boolean correctDoubleCompare(double a, double b) {
        return Math.abs(a - b) < 1e-9;  // ★ 오차 범위 내 비교!
    }
}


// =====================================================================
//  메인 실행
// =====================================================================
public class Main {
    // Logger 설정
    private static final Logger logger = Logger.getLogger(Main.class.getName());

    public static void main(String[] args) {
        System.out.println("■■■ Java 11단계: 디버깅 ■■■\n");

        // Logger 설정 (콘솔에 간단히 출력)
        logger.setLevel(Level.ALL);
        ConsoleHandler handler = new ConsoleHandler();
        handler.setLevel(Level.ALL);
        handler.setFormatter(new SimpleFormatter());
        logger.setUseParentHandlers(false);
        logger.addHandler(handler);

        // ─── 레슨 1: 버그 재현 ──────────────────────────
        System.out.println("── 레슨 1: 버그 재현 ────────────────────────────");
        int[] scores = {80, 90, 70};

        System.out.println("  ★ 버그 버전 (wrongAverage):");
        try {
            int wrong = BuggyCalculator.wrongAverage(scores);
            System.out.println("  결과: " + wrong + " ← 잘못된 값! (120 나옴)");
        } catch (Exception e) {
            System.out.println("  예외 발생: " + e.getClass().getSimpleName());
        }

        System.out.println("  ★ 수정 버전 (correctAverage):");
        double correct = BuggyCalculator.correctAverage(scores);
        System.out.println("  결과: " + correct + " ← 올바른 값!");

        // 빈 배열 테스트 (엣지 케이스)
        System.out.println("  빈 배열: " + BuggyCalculator.correctAverage(new int[]{}));
        System.out.println();

        // ─── 레슨 2: 스택 트레이스 읽기 ──────────────────
        System.out.println("── 레슨 2: 스택 트레이스 읽기 ───────────────────");
        try {
            String name = null;
            processName(name);  // NPE 발생!
        } catch (NullPointerException e) {
            System.out.println("  ★ 스택 트레이스 분석:");
            StackTraceElement[] trace = e.getStackTrace();
            for (int i = 0; i < Math.min(trace.length, 3); i++) {
                System.out.println("    " + (i + 1) + ". " + trace[i]);
            }
            System.out.println("  메시지: " + e.getMessage());
        }
        System.out.println();

        // ─── 레슨 4: Logger 사용 ────────────────────────
        System.out.println("── 레슨 4: Logger 사용 ──────────────────────────");
        logger.info("프로그램이 시작되었습니다.");
        logger.warning("메모리 사용량이 높습니다.");
        logger.fine("상세 디버깅 정보입니다.");

        // 로그 레벨 데모
        processWithLogging(85);
        processWithLogging(-5);
        System.out.println();

        // ─── 레슨 5: 흔한 버그 패턴 ─────────────────────
        System.out.println("── 레슨 5: 흔한 버그 패턴 ───────────────────────");

        // 버그 1: == vs equals
        System.out.println("  --- == vs equals ---");
        String s1 = new String("hello");
        String s2 = new String("hello");
        System.out.println("  new String == new String: "
                + BuggyCalculator.wrongStringCompare(s1, s2) + " ← 틀림!");
        System.out.println("  Objects.equals: "
                + BuggyCalculator.correctStringCompare(s1, s2) + " ← 맞음!");

        // 버그 2: Integer overflow
        System.out.println("  --- Integer overflow ---");
        System.out.println("  int 팩토리얼(20):  " + BuggyCalculator.wrongFactorial(20)
                + " ← 오버플로우!");
        System.out.println("  long 팩토리얼(20): " + BuggyCalculator.correctFactorial(20)
                + " ← 올바른 값");

        // 버그 3: 부동소수점 비교
        System.out.println("  --- 부동소수점 비교 ---");
        double sum = 0.1 + 0.2;
        System.out.println("  0.1 + 0.2 = " + sum + " (0.3이 아님!)");
        System.out.println("  ==로 비교: " + BuggyCalculator.wrongDoubleCompare(sum, 0.3)
                + " ← 실패!");
        System.out.println("  오차범위 비교: " + BuggyCalculator.correctDoubleCompare(sum, 0.3)
                + " ← 성공!");

        // 버그 4: ConcurrentModificationException
        System.out.println("  --- ConcurrentModificationException ---");
        List<Integer> list = new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5));
        try {
            for (int n : list) {
                if (n == 3) list.remove(Integer.valueOf(n));  // ★ 순회 중 삭제!
            }
        } catch (ConcurrentModificationException e) {
            System.out.println("  ★ 순회 중 삭제 시도 → " + e.getClass().getSimpleName());
        }

        // 올바른 방법: removeIf 사용
        list = new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5));
        list.removeIf(n -> n == 3);
        System.out.println("  removeIf 사용: " + list + " ← 안전!");

        // 버그 5: autoboxing NPE
        System.out.println("  --- Autoboxing NPE ---");
        Integer nullInteger = null;
        try {
            int value = nullInteger;  // ★ null을 int로 unboxing → NPE!
        } catch (NullPointerException e) {
            System.out.println("  ★ null Integer → int 변환 시 NPE 발생!");
        }
        System.out.println();

        // ─── 레슨 6: 방어적 프로그래밍 ──────────────────
        System.out.println("── 레슨 6: 방어적 프로그래밍 ────────────────────");

        // Objects.requireNonNull
        System.out.println("  --- Objects.requireNonNull ---");
        try {
            createStudent(null, 80);
        } catch (NullPointerException e) {
            System.out.println("  ★ " + e.getMessage());
        }

        // 유효성 검사
        try {
            createStudent("홍길동", -10);
        } catch (IllegalArgumentException e) {
            System.out.println("  ★ " + e.getMessage());
        }

        // 정상 호출
        String result = createStudent("김철수", 85);
        System.out.println("  정상: " + result);
        System.out.println();

        // ─── 종합 예제: 디버깅 체크리스트 ────────────────
        System.out.println("── 종합: 디버깅 체크리스트 ──────────────────────");
        System.out.println("  ┌──────────────────────────────────────┐");
        System.out.println("  │  디버깅 체크리스트                    │");
        System.out.println("  ├──────────────────────────────────────┤");
        System.out.println("  │  □ 에러 메시지를 끝까지 읽었는가?    │");
        System.out.println("  │  □ 스택 트레이스의 첫 줄을 확인?     │");
        System.out.println("  │  □ 입력값이 null일 수 있는가?        │");
        System.out.println("  │  □ 배열/리스트 인덱스가 범위 내?     │");
        System.out.println("  │  □ 문자열 비교에 equals 사용?        │");
        System.out.println("  │  □ 정수 나눗셈에서 소수점 손실?      │");
        System.out.println("  │  □ 변경 전 코드가 백업(git)되어 있나?│");
        System.out.println("  │  □ 수정 후 기존 테스트가 통과하는가?  │");
        System.out.println("  └──────────────────────────────────────┘");
        System.out.println();

        System.out.println("■■■ 11단계 학습 완료! ■■■");
    }

    // ─── 도우미 메서드들 ────────────────────────────────
    static void processName(String name) {
        // null이 들어오면 NPE 발생!
        int length = name.length();
        System.out.println("  이름 길이: " + length);
    }

    static void processWithLogging(int score) {
        logger.info("점수 처리 시작: " + score);
        if (score < 0 || score > 100) {
            logger.warning("유효하지 않은 점수: " + score);
            return;
        }
        String grade;
        if (score >= 90) grade = "A";
        else if (score >= 80) grade = "B";
        else grade = "C 이하";
        logger.info("점수 " + score + " → 등급 " + grade);
    }

    static String createStudent(String name, int score) {
        // ★ 방어적 프로그래밍: 입력값 검증!
        Objects.requireNonNull(name, "이름은 null일 수 없습니다");
        if (score < 0 || score > 100) {
            throw new IllegalArgumentException("점수는 0~100 사이여야 합니다: " + score);
        }
        return name + " (" + score + "점)";
    }
}
