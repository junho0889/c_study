import java.util.ArrayList;
import java.util.List;

public class StudentRestController {

    /*
      진짜 Spring에서는 여기에 @RestController, @GetMapping 같은 애노테이션이 붙습니다.
      하지만 이 파일은 javac/java로 바로 실행할 수 있게 순수 자바 코드로 작성합니다.

      핵심 목표:
      - REST 컨트롤러가 어떤 데이터를 돌려주는지
      - POST/PATCH 같은 요청이 들어오면 어떤 흐름으로 상태가 바뀌는지
      를 콘솔에서 바로 따라가 보는 것입니다.
    */

    private final List<Student> students = new ArrayList<Student>();
    private int nextId = 3;

    public StudentRestController() {
        students.add(new Student(1, "민수", 92));
        students.add(new Student(2, "지우", 85));
    }

    public String lesson1GetStudents() {
        return toJsonArray(students);
    }

    public String lesson2CreateStudent(String name, int score) {
        Student created = new Student(nextId, name, score);
        nextId += 1;
        students.add(created);

        return "{"
                + "\"message\":\"학생 등록 완료\","
                + "\"student\":" + created.toJson()
                + "}";
    }

    public String lesson3UpdateStudentScore(int id, int newScore) {
        Student target = findById(id);

        if (target == null) {
            return "{\"error\":\"해당 학생을 찾지 못했습니다.\"}";
        }

        target.score = newScore;

        return "{"
                + "\"message\":\"점수 수정 완료\","
                + "\"student\":" + target.toJson()
                + "}";
    }

    public String lesson4GetReviewStudents() {
        List<Student> reviewStudents = new ArrayList<Student>();

        for (Student student : students) {
            if (student.score < 70) {
                reviewStudents.add(student);
            }
        }

        return toJsonArray(reviewStudents);
    }

    private Student findById(int id) {
        for (Student student : students) {
            if (student.id == id) {
                return student;
            }
        }
        return null;
    }

    private String toJsonArray(List<Student> items) {
        StringBuilder builder = new StringBuilder();
        builder.append("[");

        for (int index = 0; index < items.size(); index += 1) {
            if (index > 0) {
                builder.append(",");
            }
            builder.append(items.get(index).toJson());
        }

        builder.append("]");
        return builder.toString();
    }

    public static void main(String[] args) {
        StudentRestController controller = new StudentRestController();

        System.out.println("========================================================================");
        System.out.println("Spring 04단계: REST 컨트롤러 흐름을 순수 자바로 따라가기");
        System.out.println("========================================================================");
        System.out.println();

        System.out.println("[레슨 1] GET /students");
        System.out.println(controller.lesson1GetStudents());
        System.out.println();

        System.out.println("[레슨 2] POST /students");
        System.out.println(controller.lesson2CreateStudent("서연", 68));
        System.out.println();

        System.out.println("[레슨 3] PATCH /students/3");
        System.out.println(controller.lesson3UpdateStudentScore(3, 76));
        System.out.println();

        System.out.println("[레슨 4] GET /students?needsReview=true");
        System.out.println(controller.lesson4GetReviewStudents());
        System.out.println();

        System.out.println("설명: 컨트롤러는 창구 직원과 비슷합니다.");
        System.out.println("요청을 받고, 데이터를 읽거나 바꾸고, 그 결과를 JSON 모양으로 돌려줍니다.");
    }

    private static class Student {
        private final int id;
        private final String name;
        private int score;

        private Student(int id, String name, int score) {
            this.id = id;
            this.name = name;
            this.score = score;
        }

        private String toJson() {
            return "{"
                    + "\"id\":" + id + ","
                    + "\"name\":\"" + name + "\","
                    + "\"score\":" + score
                    + "}";
        }
    }
}
