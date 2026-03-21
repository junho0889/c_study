/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Spring 학습 06단계: JPA 엔티티 (Student.java)
  ─ @Entity, @Id, @GeneratedValue, @Column, @Table, JPA 어노테이션 ─

  JPA(Java Persistence API)는 자바 객체를 데이터베이스 테이블에
  자동으로 연결해 주는 기술입니다.

  ■ 이 파일은 개념 설명용입니다 (컴파일하려면 Spring Boot 프로젝트 필요)

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/


/*
┌─────────────────────────────────────────────────────────────┐
│  JPA 엔티티란?                                              │
│                                                             │
│  비유: 엑셀 시트의 한 줄(행)을 자바 객체로 만든 것!          │
│                                                             │
│  엑셀 시트 "students" 테이블:                                │
│  ┌────┬──────┬──────┬───────┬─────────────────┐             │
│  │ id │ name │ grade│ score │ email           │             │
│  ├────┼──────┼──────┼───────┼─────────────────┤             │
│  │ 1  │ 민수 │  3   │  92   │ minsu@school.kr │             │
│  │ 2  │ 지우 │  2   │  88   │ jiwoo@school.kr │             │
│  └────┴──────┴──────┴───────┴─────────────────┘             │
│                                                             │
│  이 테이블의 각 행(Row)이 Student 객체 1개가 됩니다!         │
│  JPA가 자동으로 테이블 ↔ 객체를 변환해 줍니다.              │
└─────────────────────────────────────────────────────────────┘
*/


// ─────────────────────────────────────────────────────────────
// 실제 프로젝트에서는 아래 import가 필요합니다.
// 이 파일은 개념 설명용이므로 주석으로 표시합니다.
// ─────────────────────────────────────────────────────────────
// import javax.persistence.*;
// import java.time.LocalDateTime;


/*
┌─────────────────────────────────────────────────────────────┐
│  @Entity                                                    │
│                                                             │
│  "이 클래스는 데이터베이스 테이블에 대응하는 엔티티입니다"    │
│  이 어노테이션이 없으면 JPA가 이 클래스를 무시합니다!        │
│                                                             │
│  @Table(name = "students")                                  │
│  테이블 이름을 직접 지정합니다.                              │
│  안 쓰면 클래스 이름 그대로 테이블 이름이 됩니다.            │
│  (Student → student 테이블)                                 │
└─────────────────────────────────────────────────────────────┘
*/

// @Entity
// @Table(name = "students")
public class Student {

    /*
     * ┌───────────────────────────────────────────────────────┐
     * │  @Id = 기본키 (Primary Key)                           │
     * │                                                       │
     * │  비유: 학생의 학번!                                    │
     * │  학번은 절대 중복되지 않고, 각 학생을 유일하게 식별함  │
     * │                                                       │
     * │  @GeneratedValue = 기본키 자동 생성 전략               │
     * │                                                       │
     * │  전략 종류:                                           │
     * │  IDENTITY → DB가 알아서 1, 2, 3... 번호 매김          │
     * │             (MySQL의 AUTO_INCREMENT)                   │
     * │  SEQUENCE → DB의 시퀀스 객체 사용 (Oracle, PostgreSQL)│
     * │  TABLE    → 별도 테이블로 번호 관리                   │
     * │  AUTO     → DB에 맞게 자동 선택 (기본값)              │
     * └───────────────────────────────────────────────────────┘
     */
    // @Id
    // @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /*
     * ┌───────────────────────────────────────────────────────┐
     * │  @Column = 컬럼(열) 세부 설정                         │
     * │                                                       │
     * │  nullable = false → NULL 값 불허 (필수 입력)          │
     * │  length = 50 → 최대 50자                              │
     * │  unique = true → 중복 불허                            │
     * │  name = "student_name" → 컬럼 이름 직접 지정          │
     * │                                                       │
     * │  @Column을 안 붙이면?                                 │
     * │  → 필드 이름이 그대로 컬럼 이름이 됩니다.             │
     * │  → 모든 설정이 기본값 (nullable=true 등)              │
     * └───────────────────────────────────────────────────────┘
     */
    // @Column(nullable = false, length = 50)
    private String name;

    // @Column(nullable = false)
    private int grade;

    // @Column(name = "test_score")  // 컬럼 이름을 직접 지정
    private int score;

    // @Column(unique = true, length = 100)  // 이메일은 중복 불허!
    private String email;

    /*
     * @Column(updatable = false)
     * updatable = false → 한 번 저장하면 수정 불가!
     * 생성일처럼 바뀌면 안 되는 값에 사용합니다.
     */
    // @Column(updatable = false)
    // private LocalDateTime createdAt;


    // ─────────────────────────────────────────────────────────
    // 생성자
    // ─────────────────────────────────────────────────────────

    /*
     * JPA 규칙: 기본 생성자(인자 없는 생성자)가 반드시 있어야 합니다!
     *
     * 비유: JPA가 DB에서 데이터를 읽어올 때
     * 빈 학생 객체를 먼저 만들고 → 데이터를 채워 넣습니다.
     * 빈 객체를 만들려면 기본 생성자가 필요!
     */
    public Student() {
    }

    public Student(String name, int grade, int score, String email) {
        this.name = name;
        this.grade = grade;
        this.score = score;
        this.email = email;
    }


    // ─────────────────────────────────────────────────────────
    // Getter / Setter
    // ─────────────────────────────────────────────────────────
    /*
     * JPA는 getter/setter를 통해 필드에 접근합니다.
     * Lombok 라이브러리를 쓰면 @Getter, @Setter 한 줄로 대체 가능!
     */

    public Long getId() { return id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public int getGrade() { return grade; }
    public void setGrade(int grade) { this.grade = grade; }

    public int getScore() { return score; }
    public void setScore(int score) { this.score = score; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }


    @Override
    public String toString() {
        return "Student{id=" + id + ", name='" + name + "', grade=" + grade
                + ", score=" + score + ", email='" + email + "'}";
    }


    // ─────────────────────────────────────────────────────────
    // 개념 설명용 main 메서드
    // ─────────────────────────────────────────────────────────

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  Spring 06단계 : JPA 엔티티");
        System.out.println("============================================================");
        System.out.println();

        lesson1JpaAnnotations();
        lesson2EntityLifecycle();
        lesson3ColumnOptions();
    }

    public static void lesson1JpaAnnotations() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 1 : JPA 핵심 어노테이션               │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  @Entity     → 이 클래스는 DB 테이블입니다");
        System.out.println("  @Table      → 테이블 이름을 지정합니다");
        System.out.println("  @Id         → 이 필드가 기본키(PK)입니다");
        System.out.println("  @GeneratedValue → 기본키를 자동 생성합니다");
        System.out.println("  @Column     → 컬럼의 세부 설정입니다");
        System.out.println();

        Student student = new Student("민수", 3, 92, "minsu@school.kr");
        System.out.println("  생성된 엔티티: " + student);
        System.out.println();
    }

    public static void lesson2EntityLifecycle() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 2 : 엔티티 생명주기                    │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  비유: 엔티티의 4가지 상태 = 학생의 학교 생활!");
        System.out.println();
        System.out.println("  1. New (비영속)     → 아직 학교에 등록 안 한 상태");
        System.out.println("     Student s = new Student();");
        System.out.println();
        System.out.println("  2. Managed (영속)   → 학교에 등록 완료! 출석부에 있음");
        System.out.println("     em.persist(s);   // 영속성 컨텍스트에 저장");
        System.out.println();
        System.out.println("  3. Detached (준영속) → 졸업! 출석부에서 빠짐");
        System.out.println("     em.detach(s);    // 영속성 컨텍스트에서 분리");
        System.out.println();
        System.out.println("  4. Removed (삭제)   → 전학! DB에서도 삭제 예정");
        System.out.println("     em.remove(s);    // 삭제 예약");
        System.out.println();
    }

    public static void lesson3ColumnOptions() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 3 : @Column 옵션 정리                  │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  옵션           기본값    설명");
        System.out.println("  ─────────────  ────────  ──────────────────────");
        System.out.println("  name           필드이름  DB 컬럼 이름");
        System.out.println("  nullable       true      NULL 허용 여부");
        System.out.println("  unique         false     유일값 제약조건");
        System.out.println("  length         255       문자열 최대 길이");
        System.out.println("  insertable     true      INSERT 시 포함 여부");
        System.out.println("  updatable      true      UPDATE 시 포함 여부");
        System.out.println("  columnDefinition (없음)  DDL 직접 지정");
        System.out.println();
    }
}
