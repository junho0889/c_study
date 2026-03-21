public class Student {
    /*
      이 클래스는 MVC에서 Model 역할입니다.
      학생 이름과 점수라는 "진짜 데이터"를 들고 있습니다.

      비유:
      - Model = 학생 정보가 적힌 카드
      컨트롤러와 서비스가 이 카드를 읽고,
      화면에 어떤 문장을 보여 줄지 정하게 됩니다.
    */

    private final String name;
    private final int score;

    public Student(String name, int score) {
        this.name = name;
        this.score = score;
    }

    public String getName() {
        return name;
    }

    public int getScore() {
        return score;
    }

    public String toDisplayLine() {
        return name + " 학생은 " + score + "점입니다.";
    }
}
