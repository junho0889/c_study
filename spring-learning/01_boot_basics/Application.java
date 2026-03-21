public class Application {

    public static void lesson1BootStartsFast() {
        System.out.println("[레슨 1] Spring Boot 는 시작 준비를 많이 대신해 줍니다.");
        System.out.println();
        System.out.println("  복잡한 설정을 손으로 일일이 묶기보다");
        System.out.println("  필요한 기본값을 미리 챙겨 준다고 생각하면 이해가 쉽습니다.");
        System.out.println();
    }

    public static void lesson2TypicalFlow() {
        System.out.println("[레슨 2] 요청 흐름을 먼저 머릿속에 그려 둡니다.");
        System.out.println();
        System.out.println("  브라우저 -> Controller -> Service -> Repository -> 응답");
        System.out.println();
    }

    public static void lesson3RealEntryPoint() {
        System.out.println("[레슨 3] 실제 프로젝트에서는 아래 한 줄이 출발 버튼입니다.");
        System.out.println();
        System.out.println("  SpringApplication.run(Application.class, args);");
        System.out.println();
    }

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  Spring 01단계 : Boot 기초");
        System.out.println("============================================================");
        System.out.println();

        lesson1BootStartsFast();
        lesson2TypicalFlow();
        lesson3RealEntryPoint();
    }
}
