public class StudentService {

    /*
      Service는 "규칙 계산 담당"입니다.
      컨트롤러가 창구 직원이라면,
      서비스는 안쪽 사무실에서 채점 규칙을 적용하는 담당자와 비슷합니다.
    */

    public String getResultLabel(Student student) {
        if (student.getScore() >= 90) {
            return "우수";
        }

        if (student.getScore() >= 70) {
            return "통과";
        }

        return "복습 필요";
    }

    public boolean needsReview(Student student) {
        return student.getScore() < 70;
    }

    public String buildAdvice(Student student) {
        String result = getResultLabel(student);

        if (needsReview(student)) {
            return student.toDisplayLine() + " 결과는 '" + result + "'이며 쉬운 문제부터 다시 풀어 보는 것이 좋습니다.";
        }

        return student.toDisplayLine() + " 결과는 '" + result + "'이며 다음 단원으로 넘어가도 됩니다.";
    }
}
