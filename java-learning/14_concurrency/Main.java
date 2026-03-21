/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Java 학습 14단계: 동시성 (Concurrency)
  ─ Thread, Runnable, synchronized, ExecutorService, Future ─

  [학습 목표]
  1. 스레드의 개념과 생성 방법을 안다
  2. 경쟁 조건(race condition)과 동기화(synchronized)를 이해한다
  3. ExecutorService로 스레드 풀을 관리한다
  4. Future로 비동기 결과를 받는다
  5. 원자적(Atomic) 변수를 안다
  6. 동시성의 위험성과 주의사항을 안다

  ■ 컴파일: javac Main.java
  ■ 실행:   java Main

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.*;


// =====================================================================
// 레슨 1 — 스레드란?
// =====================================================================
/*
★ 스레드(Thread) = 프로그램 안에서 동시에 실행되는 "작업 흐름"
  → 하나의 프로그램이 여러 일을 동시에 할 수 있게 해줌!

  ┌──────────────────────────────────────────────────┐
  │  비유: 스레드는 "식당 직원"                       │
  │                                                  │
  │  직원 1명(단일 스레드): 주문 → 요리 → 서빙       │
  │    → 한 번에 한 손님만 처리! 느림!               │
  │                                                  │
  │  직원 3명(멀티 스레드):                           │
  │    직원1: 주문 받기                               │
  │    직원2: 요리하기                                │
  │    직원3: 서빙하기                                │
  │    → 동시에 여러 손님 처리! 빠름!                │
  └──────────────────────────────────────────────────┘

★ 프로세스 vs 스레드
  ┌────────────────┬──────────────────────────────────┐
  │ 프로세스       │ 독립적인 프로그램 (별도 메모리)    │
  │                │ 예: 크롬, 메모장 각각              │
  ├────────────────┼──────────────────────────────────┤
  │ 스레드         │ 프로세스 안의 실행 단위 (메모리 공유)│
  │                │ 예: 크롬 안의 각 탭               │
  └────────────────┴──────────────────────────────────┘

★ 스레드 생성 방법
  ┌─────────────────────┬──────────────────────────────┐
  │ 방법                │ 특징                          │
  ├─────────────────────┼──────────────────────────────┤
  │ Thread 상속         │ 다른 클래스 상속 불가          │
  │ Runnable 구현       │ 유연함 (람다 사용 가능)       │
  │ ExecutorService     │ 스레드 풀 관리 (권장!)        │
  └─────────────────────┴──────────────────────────────┘
*/


// =====================================================================
// 레슨 2 — 경쟁 조건과 동기화
// =====================================================================
/*
★ 경쟁 조건(Race Condition)
  = 여러 스레드가 같은 데이터를 동시에 수정할 때 발생하는 버그!

  ┌──────────────────────────────────────────────────────┐
  │  비유: 경쟁 조건은 "공용 화이트보드"                   │
  │                                                      │
  │  보드에 "5"라고 적혀있음                              │
  │  직원A: 5를 읽음 → 5+1=6을 쓰려고 준비              │
  │  직원B: 5를 읽음 → 5+1=6을 쓰려고 준비              │
  │  직원A: 6을 씀                                       │
  │  직원B: 6을 씀  ← 7이 되어야 하는데 6이 됨!         │
  └──────────────────────────────────────────────────────┘

★ synchronized = "한 번에 한 명만!" 잠금 표지판
  → 한 스레드가 작업 중이면 다른 스레드는 대기!

★ 동기화 방법들
  ┌────────────────────┬──────────────────────────────┐
  │ 방법               │ 설명                          │
  ├────────────────────┼──────────────────────────────┤
  │ synchronized 메서드│ 메서드 전체를 잠금             │
  │ synchronized 블록  │ 특정 부분만 잠금 (더 효율적)  │
  │ AtomicInteger      │ 원자적 연산 (락 없이!)        │
  │ ReentrantLock      │ 더 세밀한 잠금 제어           │
  └────────────────────┴──────────────────────────────┘
*/

// ─── 안전하지 않은 카운터 ───────────────────────────────
class UnsafeCounter {
    private int value = 0;

    void increase() {
        value++;  // ★ 이 한 줄이 실제로는 3단계: 읽기→더하기→쓰기
                  //    중간에 다른 스레드가 끼어들 수 있음!
    }

    int getValue() { return value; }
}

// ─── 안전한 카운터 (synchronized) ────────────────────────
class SafeCounter {
    private int value = 0;

    // ★ synchronized: 한 번에 한 스레드만 이 메서드 실행
    synchronized void increase() {
        value++;
    }

    int getValue() { return value; }
}

// ─── 안전한 카운터 (Atomic) ─────────────────────────────
class AtomicCounter {
    // ★ AtomicInteger: 하드웨어 수준에서 원자적 연산 보장!
    private final AtomicInteger value = new AtomicInteger(0);

    void increase() {
        value.incrementAndGet();  // 원자적으로 +1
    }

    int getValue() { return value.get(); }
}


// =====================================================================
// 레슨 3 — ExecutorService (스레드 풀)
// =====================================================================
/*
★ ExecutorService = "스레드 관리자" (스레드 풀)
  → 스레드를 직접 만들지 않고 풀에서 빌려 쓰고 반환!

  ┌──────────────────────────────────────────────┐
  │  비유: ExecutorService는 "택시 회사"           │
  │                                              │
  │  직접 운전(Thread):                          │
  │    손님마다 차 1대 구입 → 낭비!              │
  │                                              │
  │  택시 회사(ExecutorService):                  │
  │    택시 5대를 미리 준비 (풀)                  │
  │    손님이 오면 빈 택시 배정                   │
  │    다 타면 택시 반납 → 재사용!               │
  └──────────────────────────────────────────────┘

★ ExecutorService 종류
  ┌────────────────────────┬──────────────────────────────┐
  │ 종류                   │ 설명                          │
  ├────────────────────────┼──────────────────────────────┤
  │ newFixedThreadPool(n)  │ 고정 n개 스레드               │
  │ newCachedThreadPool()  │ 필요할 때 생성, 재사용        │
  │ newSingleThreadExecutor│ 스레드 1개 (순차 실행)        │
  │ newScheduledThreadPool │ 일정 시간마다 반복 실행       │
  └────────────────────────┴──────────────────────────────┘
*/


// =====================================================================
// 레슨 4 — Future (비동기 결과)
// =====================================================================
/*
★ Future = "나중에 받을 결과 예약증"
  → 작업을 제출하고, 결과가 준비되면 가져옴!

  ┌──────────────────────────────────────────────┐
  │  비유: Future는 "세탁소 영수증"               │
  │                                              │
  │  옷을 맡기면(submit) 영수증(Future)을 받음    │
  │  나중에 영수증으로 옷을 찾으러 감(get)        │
  │                                              │
  │  아직 안 됐으면? → 기다림 (blocking)         │
  │  다 됐으면?      → 바로 받음                 │
  └──────────────────────────────────────────────┘

★ Callable vs Runnable
  ┌────────────┬─────────────────────────────┐
  │ Runnable   │ void run() → 반환값 없음    │
  │ Callable   │ T call() → 반환값 있음!     │
  └────────────┴─────────────────────────────┘
*/


// =====================================================================
// 레슨 5 — 흔한 동시성 문제
// =====================================================================
/*
★ 데드락(Deadlock) = 두 스레드가 서로 상대의 자원을 기다리며 영원히 멈춤!

  ┌──────────────────────────────────────────────────┐
  │  비유: 데드락은 "좁은 골목 마주침"                │
  │                                                  │
  │  A: "너 먼저 비켜!"                              │
  │  B: "아니, 너 먼저 비켜!"                        │
  │  → 둘 다 안 비키고 영원히 대치!                  │
  └──────────────────────────────────────────────────┘

★ 동시성 주의사항
  1. 공유 데이터 최소화 → 불변 객체 사용!
  2. synchronized 범위를 최소화 → 성능!
  3. 가능하면 java.util.concurrent 클래스 사용
  4. Thread.sleep() 대신 적절한 동기화 메커니즘 사용
  5. 데드락 예방: 항상 같은 순서로 잠금 획득
*/


// =====================================================================
//  메인 실행
// =====================================================================
public class Main {

    public static void main(String[] args) throws Exception {
        System.out.println("■■■ Java 14단계: 동시성 (Concurrency) ■■■\n");

        // ─── 레슨 1: 스레드 기본 ────────────────────────
        System.out.println("── 레슨 1: 스레드 생성과 실행 ──────────────────");

        // 방법 1: Runnable (람다)
        Thread t1 = new Thread(() -> {
            for (int i = 0; i < 3; i++) {
                System.out.println("  [스레드1] 작업 " + i);
            }
        });

        Thread t2 = new Thread(() -> {
            for (int i = 0; i < 3; i++) {
                System.out.println("  [스레드2] 작업 " + i);
            }
        });

        t1.start();  // ★ start()로 시작 (run()이 아님!)
        t2.start();

        t1.join();   // ★ t1이 끝날 때까지 기다림
        t2.join();   // ★ t2가 끝날 때까지 기다림

        System.out.println("  (두 스레드 모두 완료)");
        System.out.println();

        // ─── 레슨 2: 경쟁 조건 시연 ─────────────────────
        System.out.println("── 레슨 2: 경쟁 조건과 동기화 ──────────────────");

        // ★ 안전하지 않은 카운터
        UnsafeCounter unsafeCounter = new UnsafeCounter();
        Thread[] unsafeThreads = new Thread[10];
        for (int i = 0; i < 10; i++) {
            unsafeThreads[i] = new Thread(() -> {
                for (int j = 0; j < 1000; j++) {
                    unsafeCounter.increase();
                }
            });
            unsafeThreads[i].start();
        }
        for (Thread t : unsafeThreads) t.join();
        System.out.println("  Unsafe 카운터 (기대값 10000): " + unsafeCounter.getValue()
                + (unsafeCounter.getValue() != 10000 ? " ← 경쟁 조건!" : ""));

        // ★ synchronized 카운터
        SafeCounter safeCounter = new SafeCounter();
        Thread[] safeThreads = new Thread[10];
        for (int i = 0; i < 10; i++) {
            safeThreads[i] = new Thread(() -> {
                for (int j = 0; j < 1000; j++) {
                    safeCounter.increase();
                }
            });
            safeThreads[i].start();
        }
        for (Thread t : safeThreads) t.join();
        System.out.println("  Safe 카운터 (기대값 10000):   " + safeCounter.getValue());

        // ★ Atomic 카운터
        AtomicCounter atomicCounter = new AtomicCounter();
        Thread[] atomicThreads = new Thread[10];
        for (int i = 0; i < 10; i++) {
            atomicThreads[i] = new Thread(() -> {
                for (int j = 0; j < 1000; j++) {
                    atomicCounter.increase();
                }
            });
            atomicThreads[i].start();
        }
        for (Thread t : atomicThreads) t.join();
        System.out.println("  Atomic 카운터 (기대값 10000): " + atomicCounter.getValue());
        System.out.println();

        // ─── 레슨 3: ExecutorService ─────────────────────
        System.out.println("── 레슨 3: ExecutorService (스레드 풀) ──────────");

        // ★ 고정 크기 스레드 풀 (3개)
        ExecutorService executor = Executors.newFixedThreadPool(3);

        System.out.println("  스레드 풀(3개)에 5개 작업 제출:");
        for (int i = 1; i <= 5; i++) {
            final int taskId = i;
            executor.submit(() -> {
                System.out.println("    작업" + taskId + " 시작 ["
                        + Thread.currentThread().getName() + "]");
                try { Thread.sleep(100); } catch (InterruptedException ignored) {}
                System.out.println("    작업" + taskId + " 완료 ["
                        + Thread.currentThread().getName() + "]");
            });
        }

        executor.shutdown();  // ★ 새 작업 접수 중단
        executor.awaitTermination(5, TimeUnit.SECONDS);  // 모든 작업 완료 대기
        System.out.println("  (모든 작업 완료)");
        System.out.println();

        // ─── 레슨 4: Future ─────────────────────────────
        System.out.println("── 레슨 4: Future (비동기 결과) ─────────────────");

        ExecutorService executor2 = Executors.newFixedThreadPool(3);

        // ★ Callable: 결과를 반환하는 작업
        List<Future<String>> futures = new ArrayList<>();
        String[] students = {"김철수", "이영희", "박민수"};

        for (String name : students) {
            Future<String> future = executor2.submit(() -> {
                Thread.sleep(200);  // 시뮬레이션: 성적 계산 중...
                int score = (int) (Math.random() * 40 + 60);
                return name + ": " + score + "점";
            });
            futures.add(future);
        }

        System.out.println("  작업 제출 완료! 결과를 기다리는 중...");
        for (Future<String> future : futures) {
            // ★ get(): 결과가 준비될 때까지 기다림
            String result = future.get();
            System.out.println("  결과: " + result);
        }

        executor2.shutdown();
        System.out.println();

        // ─── 레슨 5: 스레드 안전한 컬렉션 ───────────────
        System.out.println("── 레슨 5: 스레드 안전한 컬렉션 ────────────────");
        System.out.println("  ┌─────────────────────┬────────────────────────┐");
        System.out.println("  │ 일반 컬렉션          │ 스레드 안전 대체       │");
        System.out.println("  ├─────────────────────┼────────────────────────┤");
        System.out.println("  │ ArrayList           │ CopyOnWriteArrayList   │");
        System.out.println("  │ HashMap             │ ConcurrentHashMap      │");
        System.out.println("  │ HashSet             │ CopyOnWriteArraySet    │");
        System.out.println("  │ LinkedList          │ ConcurrentLinkedQueue  │");
        System.out.println("  └─────────────────────┴────────────────────────┘");

        // ConcurrentHashMap 예제
        ConcurrentHashMap<String, Integer> scoreMap = new ConcurrentHashMap<>();
        ExecutorService executor3 = Executors.newFixedThreadPool(3);

        for (String name : students) {
            executor3.submit(() -> {
                int score = (int) (Math.random() * 40 + 60);
                scoreMap.put(name, score);  // ★ 스레드 안전한 put!
            });
        }
        executor3.shutdown();
        executor3.awaitTermination(2, TimeUnit.SECONDS);

        System.out.println("  ConcurrentHashMap 결과:");
        scoreMap.forEach((name, score) ->
                System.out.println("    " + name + ": " + score + "점"));
        System.out.println();

        // ─── 종합 정리 ──────────────────────────────────
        System.out.println("── 종합: 동시성 핵심 정리 ──────────────────────");
        System.out.println("  ┌──────────────────────────────────────────────┐");
        System.out.println("  │  동시성 규칙                                 │");
        System.out.println("  ├──────────────────────────────────────────────┤");
        System.out.println("  │  1. 공유 데이터를 최소화하라                 │");
        System.out.println("  │  2. 불변 객체를 선호하라 (record!)           │");
        System.out.println("  │  3. Thread 직접 사용보다 ExecutorService     │");
        System.out.println("  │  4. synchronized는 범위를 최소화             │");
        System.out.println("  │  5. 단순 카운터는 AtomicInteger 사용         │");
        System.out.println("  │  6. 컬렉션은 Concurrent 버전 사용            │");
        System.out.println("  │  7. shutdown()을 잊지 말 것!                │");
        System.out.println("  └──────────────────────────────────────────────┘");
        System.out.println();

        System.out.println("■■■ 14단계 학습 완료! ■■■");
    }
}
