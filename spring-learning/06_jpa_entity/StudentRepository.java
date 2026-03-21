/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Spring 학습 06단계: JPA Repository (StudentRepository.java)
  ─ Spring Data JPA, findBy 메서드, @Query, JPQL ─

  Spring Data JPA는 SQL을 직접 쓰지 않아도
  메서드 이름만으로 DB 쿼리를 만들어 줍니다!

  ■ 이 파일은 개념 설명용입니다 (컴파일하려면 Spring Boot 프로젝트 필요)

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// import org.springframework.data.jpa.repository.JpaRepository;
// import org.springframework.data.jpa.repository.Query;
// import org.springframework.data.repository.query.Param;
// import java.util.List;
// import java.util.Optional;

/*
┌─────────────────────────────────────────────────────────────┐
│  JpaRepository란?                                          │
│                                                             │
│  비유: 도서관 사서가 "책 찾기, 등록, 삭제"를                │
│  우리 대신 해주는 것처럼,                                   │
│  JpaRepository가 "DB 조회, 저장, 삭제"를 대신 해줍니다!     │
│                                                             │
│  JpaRepository<Student, Long>                               │
│                  ↑        ↑                                 │
│              엔티티 타입  기본키 타입                         │
│                                                             │
│  기본 제공 메서드 (우리가 구현하지 않아도 됨!):              │
│    save(entity)      → 저장 또는 수정                       │
│    findById(id)      → ID로 조회                            │
│    findAll()         → 전체 조회                            │
│    deleteById(id)    → ID로 삭제                            │
│    count()           → 총 개수                              │
│    existsById(id)    → 존재 여부                            │
└─────────────────────────────────────────────────────────────┘
*/

// public interface StudentRepository extends JpaRepository<Student, Long> {

    /*
     * ┌───────────────────────────────────────────────────────┐
     * │  메서드 이름 규칙으로 쿼리 자동 생성!                 │
     * │                                                       │
     * │  비유: "3학년 학생 찾아줘" 라고 말하면                │
     * │  Spring이 SQL을 자동으로 만들어 줍니다!               │
     * │                                                       │
     * │  findBy + 필드이름 → WHERE 조건 자동 생성             │
     * └───────────────────────────────────────────────────────┘
     */

    // ─────────────────────────────────────────────────────
    // ■ 기본 findBy 메서드들
    // ─────────────────────────────────────────────────────

    // 이름으로 학생 목록 조회
    // → SELECT * FROM students WHERE name = ?
    // List<Student> findByName(String name);

    // 학년으로 학생 목록 조회
    // → SELECT * FROM students WHERE grade = ?
    // List<Student> findByGrade(int grade);

    // 이메일로 학생 1명 조회 (Optional = 없을 수도 있으니까)
    // → SELECT * FROM students WHERE email = ?
    // Optional<Student> findByEmail(String email);


    // ─────────────────────────────────────────────────────
    // ■ 조건 조합 (And, Or)
    // ─────────────────────────────────────────────────────

    // 학년 AND 점수 이상
    // → SELECT * FROM students WHERE grade = ? AND score >= ?
    // List<Student> findByGradeAndScoreGreaterThanEqual(int grade, int score);

    // 이름에 특정 글자 포함 OR 점수가 특정 값 이상
    // → SELECT * FROM students WHERE name LIKE '%?%' OR score >= ?
    // List<Student> findByNameContainingOrScoreGreaterThanEqual(String name, int score);


    // ─────────────────────────────────────────────────────
    // ■ 정렬과 제한
    // ─────────────────────────────────────────────────────

    // 점수 내림차순 정렬
    // → SELECT * FROM students ORDER BY score DESC
    // List<Student> findAllByOrderByScoreDesc();

    // 상위 3명
    // → SELECT * FROM students ORDER BY score DESC LIMIT 3
    // List<Student> findTop3ByOrderByScoreDesc();


    // ─────────────────────────────────────────────────────
    // ■ 존재 여부, 개수
    // ─────────────────────────────────────────────────────

    // 이메일 존재 여부
    // → SELECT COUNT(*) > 0 FROM students WHERE email = ?
    // boolean existsByEmail(String email);

    // 학년별 학생 수
    // → SELECT COUNT(*) FROM students WHERE grade = ?
    // long countByGrade(int grade);


    /*
     * ┌───────────────────────────────────────────────────────┐
     * │  @Query = JPQL 또는 네이티브 SQL 직접 작성             │
     * │                                                       │
     * │  메서드 이름 규칙으로 표현하기 어려운 복잡한 쿼리는    │
     * │  @Query 어노테이션으로 직접 작성합니다.                │
     * │                                                       │
     * │  JPQL = Java Persistence Query Language                │
     * │  SQL과 비슷하지만 테이블 대신 엔티티 클래스를 사용!    │
     * │                                                       │
     * │  SQL:  SELECT * FROM students WHERE grade = 3          │
     * │  JPQL: SELECT s FROM Student s WHERE s.grade = 3      │
     * │                ↑                       ↑               │
     * │           엔티티 별칭             필드 이름 사용       │
     * └───────────────────────────────────────────────────────┘
     */

    // JPQL로 평균 점수 이상인 학생 조회
    // @Query("SELECT s FROM Student s WHERE s.score >= :minScore")
    // List<Student> findStudentsAboveScore(@Param("minScore") int minScore);

    // JPQL로 학년별 평균 점수 조회
    // @Query("SELECT s.grade, AVG(s.score) FROM Student s GROUP BY s.grade")
    // List<Object[]> findAverageScoreByGrade();

    // 네이티브 SQL (진짜 SQL 그대로 사용)
    // @Query(value = "SELECT * FROM students WHERE score >= ?1", nativeQuery = true)
    // List<Student> findByScoreNative(int minScore);

// }  // interface 닫기


/*
┌─────────────────────────────────────────────────────────────┐
│  메서드 이름 키워드 정리표                                   │
│                                                             │
│  키워드          예시                      SQL 변환          │
│  ─────────────  ────────────────────────  ─────────────────  │
│  findBy         findByName(name)          WHERE name = ?     │
│  And            findByNameAndGrade(n,g)   AND                │
│  Or             findByNameOrGrade(n,g)    OR                 │
│  Between        findByScoreBetween(a,b)   BETWEEN a AND b   │
│  LessThan       findByScoreLessThan(s)    < s               │
│  GreaterThan    findByScoreGreaterThan(s) > s                │
│  Like           findByNameLike(pattern)   LIKE pattern       │
│  Containing     findByNameContaining(s)   LIKE %s%           │
│  StartingWith   findByNameStartingWith(s) LIKE s%            │
│  EndingWith     findByNameEndingWith(s)   LIKE %s            │
│  OrderBy        findByOrderByScoreDesc()  ORDER BY score DESC│
│  Not            findByNameNot(name)       != name            │
│  In             findByGradeIn(list)       IN (...)           │
│  IsNull         findByEmailIsNull()       IS NULL            │
│  IsNotNull      findByEmailIsNotNull()    IS NOT NULL        │
│  True/False     findByActiveTrue()        = true             │
│  Top/First      findTop3By...()           LIMIT 3            │
│  Count          countByGrade(g)           SELECT COUNT(*)    │
│  Exists         existsByEmail(e)          EXISTS             │
│  Delete         deleteByName(n)           DELETE WHERE       │
└─────────────────────────────────────────────────────────────┘
*/


public class StudentRepositoryExplanation {

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  Spring 06단계 : Spring Data JPA Repository");
        System.out.println("============================================================");
        System.out.println();

        lesson1BasicMethods();
        lesson2MethodNaming();
        lesson3JpqlQuery();
    }

    public static void lesson1BasicMethods() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 1 : JpaRepository 기본 메서드          │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  JpaRepository를 상속하면 이 메서드들이 자동 제공됩니다:");
        System.out.println();
        System.out.println("  save(entity)          → 저장 (새로 생성 또는 수정)");
        System.out.println("  findById(id)          → ID로 1건 조회");
        System.out.println("  findAll()             → 전체 조회");
        System.out.println("  findAllById(ids)      → 여러 ID로 조회");
        System.out.println("  deleteById(id)        → ID로 삭제");
        System.out.println("  delete(entity)        → 엔티티로 삭제");
        System.out.println("  count()               → 총 개수");
        System.out.println("  existsById(id)        → 존재 여부");
        System.out.println();
        System.out.println("  비유: 사서에게 '이 책 찾아줘', '이 책 넣어줘' 하면 끝!");
        System.out.println("       SQL을 한 줄도 쓸 필요 없습니다!");
        System.out.println();
    }

    public static void lesson2MethodNaming() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 2 : 메서드 이름 규칙                   │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  메서드 이름만 잘 쓰면 Spring이 SQL을 자동 생성합니다!");
        System.out.println();
        System.out.println("  예시:");
        System.out.println("    findByName(\"민수\")");
        System.out.println("    → SELECT * FROM students WHERE name = '민수'");
        System.out.println();
        System.out.println("    findByGradeAndScoreGreaterThan(3, 90)");
        System.out.println("    → SELECT * FROM students WHERE grade = 3 AND score > 90");
        System.out.println();
        System.out.println("    findTop3ByOrderByScoreDesc()");
        System.out.println("    → SELECT * FROM students ORDER BY score DESC LIMIT 3");
        System.out.println();
        System.out.println("  비유: '3학년이면서 90점 이상인 학생 찾아줘'를");
        System.out.println("       영어 메서드 이름으로 적으면 Spring이 이해합니다!");
        System.out.println();
    }

    public static void lesson3JpqlQuery() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 3 : @Query와 JPQL                     │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  메서드 이름이 너무 길어지면 @Query를 사용합니다.");
        System.out.println();
        System.out.println("  JPQL 예시:");
        System.out.println("    @Query(\"SELECT s FROM Student s WHERE s.score >= :min\")");
        System.out.println("    List<Student> findAbove(@Param(\"min\") int min);");
        System.out.println();
        System.out.println("  네이티브 SQL 예시:");
        System.out.println("    @Query(value = \"SELECT * FROM students\", nativeQuery = true)");
        System.out.println("    List<Student> findAllNative();");
        System.out.println();
        System.out.println("  JPQL vs SQL:");
        System.out.println("    SQL:  SELECT * FROM students WHERE grade = 3");
        System.out.println("    JPQL: SELECT s FROM Student s WHERE s.grade = 3");
        System.out.println("    차이: JPQL은 테이블이 아니라 엔티티 클래스를 기준으로!");
        System.out.println();
    }
}
