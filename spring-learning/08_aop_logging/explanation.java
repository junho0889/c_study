/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Spring 학습 08단계: AOP 성능 모니터링 Aspect 예제
  ─ 성능 측정, 슬로우 쿼리 감지, 메서드 호출 통계 ─

  실전에서 AOP가 어떻게 활용되는지 보여 주는 예제입니다.

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/


/*
┌─────────────────────────────────────────────────────────────┐
│  성능 모니터링 Aspect                                       │
│                                                             │
│  비유: 학교 수업 시간 기록부!                                │
│  각 수업(메서드)이 몇 분 걸리는지 자동 기록.                │
│  너무 오래 걸리는 수업은 빨간 표시로 경고!                  │
└─────────────────────────────────────────────────────────────┘
*/

// @Aspect
// @Component
// public class PerformanceAspect {
//
//     private static final Logger log = LoggerFactory.getLogger(PerformanceAspect.class);
//     private static final long SLOW_THRESHOLD_MS = 500;  // 500ms 이상이면 느린 것
//
//     @Around("execution(* com.school.service.*.*(..))")
//     public Object measurePerformance(ProceedingJoinPoint joinPoint) throws Throwable {
//         long start = System.currentTimeMillis();
//         String method = joinPoint.getSignature().toShortString();
//
//         try {
//             Object result = joinPoint.proceed();
//             long elapsed = System.currentTimeMillis() - start;
//
//             if (elapsed > SLOW_THRESHOLD_MS) {
//                 log.warn("[느림] {} → {}ms (임계값: {}ms)", method, elapsed, SLOW_THRESHOLD_MS);
//             } else {
//                 log.info("[정상] {} → {}ms", method, elapsed);
//             }
//
//             return result;
//         } catch (Exception e) {
//             long elapsed = System.currentTimeMillis() - start;
//             log.error("[에러] {} → {}ms, 예외: {}", method, elapsed, e.getMessage());
//             throw e;
//         }
//     }
// }


public class explanation {

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  Spring 08단계 : AOP 실전 활용 예제");
        System.out.println("============================================================");
        System.out.println();

        lesson1PerformanceMonitoring();
        lesson2AopUseCases();
        lesson3AopVsInterceptor();
    }

    public static void lesson1PerformanceMonitoring() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 1 : 성능 모니터링 Aspect               │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  @Around로 모든 서비스 메서드의 실행 시간을 측정!");
        System.out.println();
        System.out.println("  시뮬레이션:");
        System.out.println("    [정상] StudentService.findById() → 23ms");
        System.out.println("    [정상] StudentService.findAll()  → 45ms");
        System.out.println("    [느림] ReportService.generate()  → 1200ms (임계값 초과!)");
        System.out.println("    [에러] ScoreService.update()     → 15ms, 예외: 권한 없음");
        System.out.println();
        System.out.println("  이렇게 하면:");
        System.out.println("    - 느린 메서드를 자동으로 감지");
        System.out.println("    - 서비스 코드를 전혀 수정하지 않고도 성능 측정 가능!");
        System.out.println("    - 로그 분석으로 병목 지점 파악");
        System.out.println();
    }

    public static void lesson2AopUseCases() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 2 : AOP 실전 활용 사례                 │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  1. 로깅 (Logging)");
        System.out.println("     - 메서드 호출/반환 기록");
        System.out.println("     - 에러 발생 시 자동 로그");
        System.out.println();
        System.out.println("  2. 트랜잭션 관리 (@Transactional)");
        System.out.println("     - Spring의 @Transactional이 바로 AOP!");
        System.out.println("     - 메서드 시작 시 트랜잭션 시작");
        System.out.println("     - 성공 → commit, 실패 → rollback");
        System.out.println();
        System.out.println("  3. 보안 (@PreAuthorize)");
        System.out.println("     - 메서드 실행 전 권한 확인");
        System.out.println("     - 이것도 AOP로 구현되어 있음!");
        System.out.println();
        System.out.println("  4. 캐싱 (@Cacheable)");
        System.out.println("     - 같은 인자로 호출하면 캐시된 결과 반환");
        System.out.println("     - 실제 메서드를 실행하지 않아 속도 향상");
        System.out.println();
        System.out.println("  5. 재시도 (@Retryable)");
        System.out.println("     - 실패 시 자동 재시도");
        System.out.println("     - 외부 API 호출 시 유용");
        System.out.println();
        System.out.println("  핵심: 서비스 코드는 비즈니스 로직에만 집중!");
        System.out.println("       나머지 공통 기능은 AOP가 알아서 처리!");
        System.out.println();
    }

    public static void lesson3AopVsInterceptor() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 3 : AOP vs Interceptor vs Filter      │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  세 가지 모두 '가로채기' 기능이지만 적용 범위가 다릅니다:");
        System.out.println();
        System.out.println("  요청 → [Filter] → [Interceptor] → [AOP] → Controller");
        System.out.println("                                      ↓");
        System.out.println("                                    Service");
        System.out.println();
        System.out.println("  Filter (서블릿 필터):");
        System.out.println("    - 가장 바깥쪽, 모든 요청에 적용");
        System.out.println("    - Spring 밖에서 동작");
        System.out.println("    - 예: 인코딩 설정, CORS");
        System.out.println();
        System.out.println("  Interceptor (스프링 인터셉터):");
        System.out.println("    - Controller 전후에 동작");
        System.out.println("    - Spring 안에서 동작 (Bean 접근 가능)");
        System.out.println("    - 예: 인증 확인, 로그인 체크");
        System.out.println();
        System.out.println("  AOP:");
        System.out.println("    - 메서드 수준에서 동작");
        System.out.println("    - Service, Repository 등 어디든 적용 가능");
        System.out.println("    - 예: 로깅, 트랜잭션, 성능 측정");
        System.out.println();
    }
}
