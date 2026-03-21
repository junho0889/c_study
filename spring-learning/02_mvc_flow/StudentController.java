public class StudentController {
    private final StudentService studentService = new StudentService();

    public void lesson1ReceiveRequest() {
        System.out.println("[레슨 1] Controller는 요청을 가장 먼저 받는 창구다");
        System.out.println();

        Student student = new Student("민수", 82);
        System.out.println("  요청으로 받은 학생: " + student.getName());
        System.out.println("  아직 판정 전 데이터: " + student.toDisplayLine());
        System.out.println();
    }

    public void lesson2AskServiceForBusinessRule() {
        System.out.println("[레슨 2] 점수 규칙 계산은 Service에게 맡긴다");
        System.out.println();

        Student student = new Student("지우", 95);
        String result = studentService.getResultLabel(student);
        System.out.println("  Service 계산 결과: " + result);
        System.out.println("  설명: Controller가 직접 if(score >= 90) 같은 규칙을 다 쓰지 않게 분리합니다.");
        System.out.println();
    }

    public void lesson3ReturnResponseText() {
        System.out.println("[레슨 3] Controller는 Service 결과를 보기 좋은 응답으로 돌려준다");
        System.out.println();

        Student student = new Student("서연", 68);
        String comment = studentService.buildAdvice(student);
        System.out.println("  응답 문장: " + comment);
        System.out.println();
    }

    public static void main(String[] args) {
        System.out.println("========================================================================");
        System.out.println("Spring 02단계: MVC 흐름");
        System.out.println("========================================================================");
        System.out.println();

        StudentController controller = new StudentController();
        controller.lesson1ReceiveRequest();
        controller.lesson2AskServiceForBusinessRule();
        controller.lesson3ReturnResponseText();
    }
}
