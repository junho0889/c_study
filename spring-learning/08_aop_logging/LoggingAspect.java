/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Spring 학습 08단계: AOP와 로깅 (LoggingAspect.java)
  ─ @Aspect, @Before, @After, @Around, Pointcut, 성능 모니터링 ─

  AOP(Aspect-Oriented Programming)는
  여러 곳에 반복되는 코드를 한 곳에 모아서 관리하는 기술입니다.

  ■ 이 파일은 개념 설명용입니다 (컴파일하려면 Spring Boot 프로젝트 필요)

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// import org.aspectj.lang.JoinPoint;
// import org.aspectj.lang.ProceedingJoinPoint;
// import org.aspectj.lang.annotation.*;
// import org.springframework.stereotype.Component;
// import org.slf4j.Logger;
// import org.slf4j.LoggerFactory;


/*
┌─────────────────────────────────────────────────────────────┐
│  AOP란?                                                     │
│                                                             │
│  비유: CCTV 시스템!                                         │
│                                                             │
│  CCTV 없이:                                                │
│    교실마다 경비원을 배치 → 비효율적! 반복!                 │
│    모든 서비스 메서드에 로깅 코드 작성 → 비효율적! 반복!     │
│                                                             │
│  CCTV 설치(AOP):                                            │
│    복도에 CCTV 설치 → 모든 교실 출입을 자동 기록!           │
│    AOP로 로깅 설정 → 모든 메서드 호출을 자동 기록!          │
│                                                             │
│  핵심 용어:                                                 │
│    Aspect  = CCTV 시스템 전체 (로깅, 보안, 트랜잭션 등)     │
│    Pointcut = CCTV를 설치할 위치 (어떤 메서드에 적용할지)    │
│    Advice  = CCTV가 하는 일 (기록, 알림 등)                 │
│    JoinPoint = CCTV가 포착한 순간 (메서드 호출 시점)         │
└─────────────────────────────────────────────────────────────┘
*/

// @Aspect
// @Component
public class LoggingAspect {

    // private static final Logger log = LoggerFactory.getLogger(LoggingAspect.class);


    /*
     * ┌───────────────────────────────────────────────────────┐
     * │  @Before = 메서드 실행 전에 동작                       │
     * │                                                       │
     * │  비유: 교실에 들어가기 전에 출석 체크!                 │
     * │  "민수가 3교시 수학 교실에 들어갑니다" 기록            │
     * └───────────────────────────────────────────────────────┘
     */

    /*
     * Pointcut 표현식 설명:
     *
     * execution(* com.school.service.*.*(..))
     *           ↑  ↑                ↑ ↑  ↑
     *           │  │                │ │  └─ 매개변수 상관없이
     *           │  │                │ └──── 모든 메서드
     *           │  │                └────── 모든 클래스
     *           │  └─────────────────────── 패키지 경로
     *           └────────────────────────── 리턴 타입 상관없이
     *
     * 쉽게 말하면: "service 패키지의 모든 클래스의 모든 메서드"
     */

    // @Before("execution(* com.school.service.*.*(..))")
    // public void logBefore(JoinPoint joinPoint) {
    //     String methodName = joinPoint.getSignature().getName();
    //     Object[] args = joinPoint.getArgs();
    //     log.info("[호출] {} - 인자: {}", methodName, Arrays.toString(args));
    // }


    /*
     * ┌───────────────────────────────────────────────────────┐
     * │  @After = 메서드 실행 후에 동작 (성공/실패 무관)       │
     * │                                                       │
     * │  비유: 교실을 나갈 때 퇴실 기록!                       │
     * │  성공이든 실패든 무조건 기록됩니다.                    │
     * └───────────────────────────────────────────────────────┘
     */

    // @After("execution(* com.school.service.*.*(..))")
    // public void logAfter(JoinPoint joinPoint) {
    //     log.info("[완료] {}", joinPoint.getSignature().getName());
    // }


    /*
     * ┌───────────────────────────────────────────────────────┐
     * │  @AfterReturning = 메서드가 성공적으로 반환된 후       │
     * │                                                       │
     * │  비유: 시험을 잘 마친 후 "합격!" 기록                  │
     * └───────────────────────────────────────────────────────┘
     */

    // @AfterReturning(
    //     pointcut = "execution(* com.school.service.*.*(..))",
    //     returning = "result"  // 반환값을 받을 수 있음!
    // )
    // public void logAfterReturning(JoinPoint joinPoint, Object result) {
    //     log.info("[성공] {} → 반환값: {}", joinPoint.getSignature().getName(), result);
    // }


    /*
     * ┌───────────────────────────────────────────────────────┐
     * │  @AfterThrowing = 예외가 발생했을 때                   │
     * │                                                       │
     * │  비유: 화재 감지기! 문제가 생기면 자동 알림            │
     * └───────────────────────────────────────────────────────┘
     */

    // @AfterThrowing(
    //     pointcut = "execution(* com.school.service.*.*(..))",
    //     throwing = "exception"  // 발생한 예외를 받을 수 있음!
    // )
    // public void logAfterThrowing(JoinPoint joinPoint, Exception exception) {
    //     log.error("[에러] {} → 예외: {}", joinPoint.getSignature().getName(),
    //               exception.getMessage());
    // }


    /*
     * ┌───────────────────────────────────────────────────────┐
     * │  @Around = 메서드 실행 전후를 모두 감싸기 (가장 강력!) │
     * │                                                       │
     * │  비유: 포장 배달!                                      │
     * │  주문 접수(전) → 요리(실행) → 포장(후) → 배달          │
     * │  전체 과정을 하나의 Advice에서 관리!                   │
     * │                                                       │
     * │  주의: proceed()를 호출해야 실제 메서드가 실행됩니다!   │
     * │  호출 안 하면 원래 메서드가 실행되지 않음!             │
     * └───────────────────────────────────────────────────────┘
     */

    // @Around("execution(* com.school.service.*.*(..))")
    // public Object logAround(ProceedingJoinPoint joinPoint) throws Throwable {
    //     String methodName = joinPoint.getSignature().getName();
    //
    //     // ── 실행 전 ──
    //     long startTime = System.currentTimeMillis();
    //     log.info("[시작] {}", methodName);
    //
    //     try {
    //         // ── 실제 메서드 실행 ──
    //         Object result = joinPoint.proceed();  // ← 이걸 호출해야 원래 메서드 실행!
    //
    //         // ── 실행 후 (성공) ──
    //         long elapsed = System.currentTimeMillis() - startTime;
    //         log.info("[끝] {} ({}ms) → 결과: {}", methodName, elapsed, result);
    //
    //         return result;  // 원래 반환값을 돌려줘야 함!
    //
    //     } catch (Exception e) {
    //         // ── 실행 후 (실패) ──
    //         long elapsed = System.currentTimeMillis() - startTime;
    //         log.error("[실패] {} ({}ms) → 예외: {}", methodName, elapsed, e.getMessage());
    //         throw e;  // 예외를 다시 던져야 원래 예외 처리 흐름이 유지됨!
    //     }
    // }


    // ─────────────────────────────────────────────────────────
    // 개념 설명용 main 메서드
    // ─────────────────────────────────────────────────────────

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  Spring 08단계 : AOP와 로깅");
        System.out.println("============================================================");
        System.out.println();

        lesson1AopConcepts();
        lesson2AdviceTypes();
        lesson3PointcutExpressions();
    }

    public static void lesson1AopConcepts() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 1 : AOP 핵심 개념                     │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  AOP 용어 정리:");
        System.out.println();
        System.out.println("  Aspect(관점)   = 공통 관심사를 모듈화한 것");
        System.out.println("                   예: 로깅 Aspect, 보안 Aspect, 트랜잭션 Aspect");
        System.out.println();
        System.out.println("  Pointcut(지점) = 어디에 적용할지 (대상 선택)");
        System.out.println("                   예: service 패키지의 모든 메서드");
        System.out.println();
        System.out.println("  Advice(충고)   = 무엇을 할지 (실행 코드)");
        System.out.println("                   예: 로그 출력, 시간 측정, 권한 확인");
        System.out.println();
        System.out.println("  JoinPoint      = 실제 적용 시점 (메서드 호출 순간)");
        System.out.println("                   메서드 이름, 인자 등 정보를 담고 있음");
        System.out.println();
        System.out.println("  비유: AOP = 영화 촬영 세트");
        System.out.println("    Aspect  = 조명팀, 음향팀, 분장팀 (각 담당)");
        System.out.println("    Pointcut = 어떤 장면에 참여할지");
        System.out.println("    Advice  = 어떤 일을 할지");
        System.out.println("    배우(서비스 코드)는 연기에만 집중! 나머지는 팀이 알아서!");
        System.out.println();
    }

    public static void lesson2AdviceTypes() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 2 : Advice 종류 정리                   │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  Advice 타입      실행 시점                   사용 예");
        System.out.println("  ─────────────    ──────────────────────     ──────────────");
        System.out.println("  @Before          메서드 실행 전              권한 확인");
        System.out.println("  @After           메서드 실행 후 (항상)       리소스 정리");
        System.out.println("  @AfterReturning  성공 반환 후                결과 로깅");
        System.out.println("  @AfterThrowing   예외 발생 후                에러 알림");
        System.out.println("  @Around          전후 모두 (가장 강력)       시간 측정");
        System.out.println();
        System.out.println("  실행 순서:");
        System.out.println("    @Around(전) → @Before → 메서드 실행 → @AfterReturning/@AfterThrowing → @After → @Around(후)");
        System.out.println();
    }

    public static void lesson3PointcutExpressions() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 3 : Pointcut 표현식                    │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  자주 쓰는 Pointcut 패턴:");
        System.out.println();
        System.out.println("  execution(* com.school.service.*.*(..))");
        System.out.println("    → service 패키지의 모든 클래스, 모든 메서드");
        System.out.println();
        System.out.println("  execution(public * *(..))");
        System.out.println("    → 모든 public 메서드");
        System.out.println();
        System.out.println("  execution(* com.school..*Service.*(..))");
        System.out.println("    → 이름이 Service로 끝나는 모든 클래스의 메서드");
        System.out.println();
        System.out.println("  @annotation(com.school.annotation.Loggable)");
        System.out.println("    → @Loggable 어노테이션이 붙은 메서드만");
        System.out.println();
        System.out.println("  within(com.school.controller..*)");
        System.out.println("    → controller 패키지 내 모든 클래스의 메서드");
        System.out.println();
    }
}
