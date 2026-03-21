/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Java 학습 13단계: 디자인 패턴
  ─ Singleton, Factory, Strategy, Observer, Builder ─

  [학습 목표]
  1. 디자인 패턴이 왜 필요한지 이해한다
  2. Singleton 패턴으로 단일 인스턴스를 관리한다
  3. Factory 패턴으로 객체 생성을 캡슐화한다
  4. Strategy 패턴으로 알고리즘을 교체한다
  5. Observer 패턴으로 이벤트를 처리한다
  6. Builder 패턴으로 복잡한 객체를 조립한다

  ■ 컴파일: javac Main.java
  ■ 실행:   java Main

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

import java.util.*;


// =====================================================================
// 레슨 1 — 디자인 패턴이란?
// =====================================================================
/*
★ 디자인 패턴 = 자주 발생하는 설계 문제에 대한 "검증된 해결책"
  → 선배 개발자들이 수십 년간 쌓은 지혜의 결정체!

  ┌──────────────────────────────────────────────┐
  │  비유: 디자인 패턴은 "건축 설계 도면"         │
  │                                              │
  │  집을 지을 때 처음부터 설계하지 않고          │
  │  "거실은 남향, 부엌은 북쪽" 같은              │
  │  검증된 배치 패턴을 따르는 것!                │
  └──────────────────────────────────────────────┘

★ 패턴 분류 (GoF 23가지 중 주요 5가지)
  ┌────────────────┬──────────────────────────────────┐
  │ 분류           │ 패턴                              │
  ├────────────────┼──────────────────────────────────┤
  │ 생성 패턴      │ Singleton, Factory, Builder       │
  │ (객체 만들기)  │                                   │
  ├────────────────┼──────────────────────────────────┤
  │ 행동 패턴      │ Strategy, Observer                │
  │ (객체 협력)    │                                   │
  └────────────────┴──────────────────────────────────┘
*/


// =====================================================================
// 레슨 2 — Singleton 패턴
// =====================================================================
/*
★ Singleton = "딱 하나만 존재하는 객체"
  → 애플리케이션 전체에서 인스턴스가 1개만!

  ┌──────────────────────────────────────────────┐
  │  비유: Singleton은 "대통령"                   │
  │                                              │
  │  나라에 대통령은 1명만 있음                   │
  │  누가 "대통령님!" 하면 같은 사람을 가리킴     │
  │                                              │
  │  대통령을 새로 만들 수 없고 (private 생성자)  │
  │  "현재 대통령"을 부르는 방법만 있음 (getInstance)│
  └──────────────────────────────────────────────┘

★ 사용 예: 설정 관리자, DB 커넥션 풀, 로그 매니저
*/

class AppConfig {
    // ★ 1. private static 인스턴스
    private static AppConfig instance;

    // ★ 설정값들
    private String appName;
    private String version;
    private int maxUsers;

    // ★ 2. private 생성자 (외부에서 new 불가!)
    private AppConfig() {
        appName = "학생 관리 시스템";
        version = "1.0.0";
        maxUsers = 100;
    }

    // ★ 3. getInstance()로만 접근 (게으른 초기화)
    static AppConfig getInstance() {
        if (instance == null) {
            instance = new AppConfig();
        }
        return instance;
    }

    String getAppName() { return appName; }
    String getVersion() { return version; }
    int getMaxUsers() { return maxUsers; }
    void setMaxUsers(int max) { this.maxUsers = max; }

    @Override
    public String toString() {
        return appName + " v" + version + " (최대 " + maxUsers + "명)";
    }
}


// =====================================================================
// 레슨 3 — Factory 패턴
// =====================================================================
/*
★ Factory = "객체 생성을 전담하는 공장"
  → 어떤 객체를 만들지는 팩토리가 결정!
  → 클라이언트는 구체 클래스를 몰라도 됨

  ┌──────────────────────────────────────────────┐
  │  비유: Factory는 "음식점 주문"                │
  │                                              │
  │  손님: "라면 주세요!" (종류만 말함)           │
  │  주방(Factory): 신라면? 진라면? → 알아서 결정│
  │                                              │
  │  손님은 요리 과정을 몰라도 음식을 받음!       │
  └──────────────────────────────────────────────┘
*/

// ─── 공통 인터페이스 ────────────────────────────────────
interface MessageSender {
    void send(String message);
    String getType();
}

class EmailSender implements MessageSender {
    @Override
    public void send(String message) {
        System.out.println("    [이메일] " + message);
    }
    @Override
    public String getType() { return "이메일"; }
}

class SmsSender implements MessageSender {
    @Override
    public void send(String message) {
        System.out.println("    [SMS] " + message);
    }
    @Override
    public String getType() { return "SMS"; }
}

class PushSender implements MessageSender {
    @Override
    public void send(String message) {
        System.out.println("    [PUSH] " + message);
    }
    @Override
    public String getType() { return "푸시알림"; }
}

// ★ 팩토리 클래스
class MessageSenderFactory {
    // 정적 팩토리 메서드
    static MessageSender create(String type) {
        return switch (type.toLowerCase()) {
            case "email" -> new EmailSender();
            case "sms"   -> new SmsSender();
            case "push"  -> new PushSender();
            default -> throw new IllegalArgumentException("지원하지 않는 타입: " + type);
        };
    }
}


// =====================================================================
// 레슨 4 — Strategy 패턴
// =====================================================================
/*
★ Strategy = "알고리즘을 갈아 끼울 수 있는 구조"
  → 행동을 캡슐화하여 실행 시점에 교체 가능!

  ┌──────────────────────────────────────────────┐
  │  비유: Strategy는 "네비게이션 경로"            │
  │                                              │
  │  같은 목적지라도:                             │
  │    최단 거리 전략 → 좁은 골목길               │
  │    최단 시간 전략 → 고속도로                  │
  │    최저 비용 전략 → 무료 도로                 │
  │                                              │
  │  네비(Context)에 전략만 바꿔 끼우면 됨!       │
  └──────────────────────────────────────────────┘
*/

// ★ 전략 인터페이스
interface SortStrategy {
    void sort(int[] arr);
    String getName();
}

// ─── 전략 1: 버블 정렬 ──────────────────────────────────
class BubbleSortStrategy implements SortStrategy {
    @Override
    public void sort(int[] arr) {
        for (int i = 0; i < arr.length - 1; i++) {
            for (int j = 0; j < arr.length - 1 - i; j++) {
                if (arr[j] > arr[j + 1]) {
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
    }
    @Override
    public String getName() { return "버블 정렬"; }
}

// ─── 전략 2: 선택 정렬 ──────────────────────────────────
class SelectionSortStrategy implements SortStrategy {
    @Override
    public void sort(int[] arr) {
        for (int i = 0; i < arr.length - 1; i++) {
            int minIdx = i;
            for (int j = i + 1; j < arr.length; j++) {
                if (arr[j] < arr[minIdx]) minIdx = j;
            }
            int temp = arr[i];
            arr[i] = arr[minIdx];
            arr[minIdx] = temp;
        }
    }
    @Override
    public String getName() { return "선택 정렬"; }
}

// ★ Context: 전략을 사용하는 클래스
class Sorter {
    private SortStrategy strategy;

    Sorter(SortStrategy strategy) {
        this.strategy = strategy;
    }

    // ★ 전략 교체!
    void setStrategy(SortStrategy strategy) {
        this.strategy = strategy;
    }

    void performSort(int[] arr) {
        System.out.println("    " + strategy.getName() + " 사용:");
        strategy.sort(arr);
        System.out.println("    결과: " + Arrays.toString(arr));
    }
}


// =====================================================================
// 레슨 5 — Observer 패턴
// =====================================================================
/*
★ Observer = "구독-알림" 패턴
  → 상태가 변하면 등록된 모든 관찰자에게 자동으로 알림!

  ┌──────────────────────────────────────────────┐
  │  비유: Observer는 "유튜브 구독"               │
  │                                              │
  │  유튜버(Subject): 새 영상을 올리면            │
  │  구독자(Observer)들에게 자동으로 알림!        │
  │                                              │
  │  구독 취소하면 더 이상 알림을 안 받음          │
  └──────────────────────────────────────────────┘

★ 사용 예: GUI 이벤트, 메시지 시스템, 주식 알림
*/

// ★ 관찰자 인터페이스
interface EventListener {
    void onEvent(String eventType, String message);
}

// ★ 주체(Subject): 이벤트를 발행
class EventManager {
    private final Map<String, List<EventListener>> listeners = new HashMap<>();

    // 구독
    void subscribe(String eventType, EventListener listener) {
        listeners.computeIfAbsent(eventType, k -> new ArrayList<>()).add(listener);
    }

    // 구독 해제
    void unsubscribe(String eventType, EventListener listener) {
        List<EventListener> list = listeners.get(eventType);
        if (list != null) list.remove(listener);
    }

    // 알림 발행
    void notify(String eventType, String message) {
        List<EventListener> list = listeners.get(eventType);
        if (list != null) {
            for (EventListener listener : list) {
                listener.onEvent(eventType, message);
            }
        }
    }
}

// ─── 구체적인 관찰자들 ──────────────────────────────────
class LogListener implements EventListener {
    @Override
    public void onEvent(String eventType, String message) {
        System.out.println("    [LOG] " + eventType + ": " + message);
    }
}

class AlertListener implements EventListener {
    @Override
    public void onEvent(String eventType, String message) {
        System.out.println("    [ALERT] " + eventType + ": " + message);
    }
}

// ─── 이벤트를 사용하는 클래스 ───────────────────────────
class UserService {
    final EventManager events = new EventManager();

    void registerUser(String name) {
        System.out.println("    사용자 등록: " + name);
        events.notify("USER_REGISTERED", name + " 님이 가입했습니다.");
    }

    void deleteUser(String name) {
        System.out.println("    사용자 탈퇴: " + name);
        events.notify("USER_DELETED", name + " 님이 탈퇴했습니다.");
    }
}


// =====================================================================
// 레슨 6 — Builder 패턴
// =====================================================================
/*
★ Builder = "복잡한 객체를 단계별로 조립"
  → 생성자 매개변수가 많을 때 유용!
  → 메서드 체이닝으로 가독성 UP!

  ┌──────────────────────────────────────────────┐
  │  비유: Builder는 "서브웨이 주문"              │
  │                                              │
  │  빵 선택 → 고기 선택 → 야채 선택 → 소스 선택│
  │  원하는 것만 골라서 조립!                     │
  │                                              │
  │  Student.builder()                            │
  │    .name("홍길동")                            │
  │    .score(92)                                 │
  │    .club("축구부")                            │
  │    .build();                                  │
  └──────────────────────────────────────────────┘

★ 왜 Builder를 쓸까?
  // 생성자 매개변수가 많으면 헷갈림!
  new Student("홍길동", 92, 10, "축구부", true, "서울");
  //         이름? 점수? 뭐? 뭐? 뭐? 뭐?

  // Builder는 명확!
  Student.builder().name("홍길동").score(92).club("축구부").build();
*/

class StudentProfile {
    private final String name;
    private final int age;
    private final int score;
    private final String club;
    private final String address;

    // private 생성자 (Builder를 통해서만 생성)
    private StudentProfile(Builder builder) {
        this.name = builder.name;
        this.age = builder.age;
        this.score = builder.score;
        this.club = builder.club;
        this.address = builder.address;
    }

    @Override
    public String toString() {
        return "  " + name + " (" + age + "세, " + score + "점, "
                + club + ", " + address + ")";
    }

    // ★ 정적 메서드로 Builder 시작
    static Builder builder() {
        return new Builder();
    }

    // ★ Builder 내부 클래스
    static class Builder {
        private String name = "미정";
        private int age = 0;
        private int score = 0;
        private String club = "없음";
        private String address = "미정";

        // ★ 메서드 체이닝: 각 메서드가 this를 반환!
        Builder name(String name) { this.name = name; return this; }
        Builder age(int age) { this.age = age; return this; }
        Builder score(int score) { this.score = score; return this; }
        Builder club(String club) { this.club = club; return this; }
        Builder address(String address) { this.address = address; return this; }

        StudentProfile build() {
            // 유효성 검사
            if (name == null || name.isEmpty()) {
                throw new IllegalStateException("이름은 필수입니다!");
            }
            return new StudentProfile(this);
        }
    }
}


// =====================================================================
//  메인 실행
// =====================================================================
public class Main {
    public static void main(String[] args) {
        System.out.println("■■■ Java 13단계: 디자인 패턴 ■■■\n");

        // ─── 레슨 2: Singleton ──────────────────────────
        System.out.println("── 레슨 2: Singleton 패턴 ──────────────────────");
        AppConfig config1 = AppConfig.getInstance();
        AppConfig config2 = AppConfig.getInstance();

        System.out.println("  config1: " + config1);
        System.out.println("  config2: " + config2);
        System.out.println("  같은 객체? " + (config1 == config2));  // true!

        config1.setMaxUsers(200);
        System.out.println("  config1에서 수정 후 config2: " + config2.getMaxUsers());
        // → 200! 같은 객체이므로!
        System.out.println();

        // ─── 레슨 3: Factory ────────────────────────────
        System.out.println("── 레슨 3: Factory 패턴 ────────────────────────");
        String[] types = {"email", "sms", "push"};
        for (String type : types) {
            // ★ 클라이언트는 구체 클래스를 모름! 팩토리에 타입만 전달!
            MessageSender sender = MessageSenderFactory.create(type);
            System.out.println("  " + sender.getType() + " 발송기 생성");
            sender.send("Hello! 테스트 메시지입니다.");
        }

        // 지원하지 않는 타입
        try {
            MessageSenderFactory.create("pigeon");
        } catch (IllegalArgumentException e) {
            System.out.println("  ★ " + e.getMessage());
        }
        System.out.println();

        // ─── 레슨 4: Strategy ───────────────────────────
        System.out.println("── 레슨 4: Strategy 패턴 ──────────────────────");
        int[] data1 = {5, 3, 8, 1, 9, 2};
        int[] data2 = data1.clone();

        Sorter sorter = new Sorter(new BubbleSortStrategy());
        sorter.performSort(data1);

        // ★ 전략 교체! 코드 변경 없이 알고리즘만 바꿈!
        sorter.setStrategy(new SelectionSortStrategy());
        sorter.performSort(data2);
        System.out.println();

        // ─── 레슨 5: Observer ───────────────────────────
        System.out.println("── 레슨 5: Observer 패턴 ──────────────────────");
        UserService userService = new UserService();

        // 관찰자 등록
        LogListener logListener = new LogListener();
        AlertListener alertListener = new AlertListener();

        userService.events.subscribe("USER_REGISTERED", logListener);
        userService.events.subscribe("USER_REGISTERED", alertListener);
        userService.events.subscribe("USER_DELETED", logListener);

        // 이벤트 발생 → 관찰자들에게 자동 알림!
        userService.registerUser("김철수");
        System.out.println();
        userService.registerUser("이영희");
        System.out.println();

        // 구독 해제 후 다시 이벤트
        userService.events.unsubscribe("USER_REGISTERED", alertListener);
        System.out.println("  (AlertListener 구독 해제)");
        userService.deleteUser("김철수");
        System.out.println();

        // ─── 레슨 6: Builder ────────────────────────────
        System.out.println("── 레슨 6: Builder 패턴 ────────────────────────");

        // ★ 메서드 체이닝으로 명확하게 객체 생성!
        StudentProfile s1 = StudentProfile.builder()
                .name("홍길동")
                .age(17)
                .score(92)
                .club("축구부")
                .address("서울")
                .build();

        // 일부 값만 설정 (나머지는 기본값)
        StudentProfile s2 = StudentProfile.builder()
                .name("성춘향")
                .score(88)
                .build();

        StudentProfile s3 = StudentProfile.builder()
                .name("이몽룡")
                .age(18)
                .club("과학부")
                .address("부산")
                .build();

        System.out.println(s1);
        System.out.println(s2);
        System.out.println(s3);
        System.out.println();

        // ─── 종합 정리 ──────────────────────────────────
        System.out.println("── 종합: 패턴 선택 가이드 ──────────────────────");
        System.out.println("  ┌──────────────┬──────────────────────────────────┐");
        System.out.println("  │ 패턴         │ 이럴 때 사용!                    │");
        System.out.println("  ├──────────────┼──────────────────────────────────┤");
        System.out.println("  │ Singleton    │ 설정, 로거 등 1개만 필요할 때    │");
        System.out.println("  │ Factory      │ 생성 로직이 복잡하거나 종류별    │");
        System.out.println("  │ Strategy     │ 알고리즘을 실행 중에 교체할 때   │");
        System.out.println("  │ Observer     │ 이벤트 기반 알림이 필요할 때     │");
        System.out.println("  │ Builder      │ 생성자 매개변수가 많을 때        │");
        System.out.println("  └──────────────┴──────────────────────────────────┘");
        System.out.println();

        System.out.println("■■■ 13단계 학습 완료! ■■■");
    }
}
