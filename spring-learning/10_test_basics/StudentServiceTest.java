/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Spring 학습 10단계: 테스트 기초 (StudentServiceTest.java)
  ─ JUnit5, @MockBean, 단위 테스트, 서비스 테스트 ─

  테스트 코드는 "내 코드가 올바르게 동작하는지" 자동으로 확인합니다.
  사람이 매번 실행해서 눈으로 확인하는 대신,
  컴퓨터가 자동으로 검사해 줍니다!

  ■ 이 파일은 개념 설명용입니다 (컴파일하려면 Spring Boot 프로젝트 필요)

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// import org.junit.jupiter.api.*;
// import org.junit.jupiter.api.extension.ExtendWith;
// import org.mockito.InjectMocks;
// import org.mockito.Mock;
// import org.mockito.junit.jupiter.MockitoExtension;
// import static org.junit.jupiter.api.Assertions.*;
// import static org.mockito.Mockito.*;
// import java.util.Optional;


/*
┌─────────────────────────────────────────────────────────────┐
│  단위 테스트(Unit Test)란?                                   │
│                                                             │
│  비유: 자동차 공장의 부품 검사!                              │
│                                                             │
│  자동차 전체를 조립하기 전에                                │
│  바퀴, 엔진, 브레이크 각각을 따로 검사합니다.               │
│                                                             │
│  마찬가지로, 전체 앱을 실행하기 전에                         │
│  Service, Repository, Controller 각각을 따로 테스트합니다.   │
│                                                             │
│  Mock이란?                                                  │
│  바퀴를 테스트할 때 진짜 도로가 필요 없듯이,                │
│  Service를 테스트할 때 진짜 DB가 필요 없습니다.             │
│  가짜(Mock) DB를 만들어서 테스트합니다!                      │
└─────────────────────────────────────────────────────────────┘
*/


// @ExtendWith(MockitoExtension.class)  // Mockito 사용 선언
public class StudentServiceTest {

    /*
     * @Mock = 가짜 객체 생성
     *
     * 비유: 영화 촬영용 소품!
     * 진짜 총이 아니라 모형 총을 쓰는 것처럼,
     * 진짜 Repository가 아니라 가짜 Repository를 만듭니다.
     * → DB 연결 없이도 Service 로직을 테스트할 수 있음!
     */
    // @Mock
    // private StudentRepository studentRepository;

    /*
     * @InjectMocks = Mock을 주입받는 대상
     *
     * StudentService 안에 있는 StudentRepository를
     * 위에서 만든 가짜(Mock) Repository로 교체합니다.
     */
    // @InjectMocks
    // private StudentService studentService;


    /*
     * ┌───────────────────────────────────────────────────────┐
     * │  @Test = "이 메서드는 테스트입니다" 표시               │
     * │                                                       │
     * │  테스트 메서드 이름 규칙:                              │
     * │  "무엇을_어떤상황에서_어떤결과" 형식이 읽기 좋습니다  │
     * │                                                       │
     * │  테스트 3단계 (AAA 패턴):                              │
     * │  1. Arrange (준비) → 테스트 데이터 준비                │
     * │  2. Act (실행)     → 테스트할 메서드 실행              │
     * │  3. Assert (검증)  → 결과가 기대한 대로인지 확인       │
     * └───────────────────────────────────────────────────────┘
     */


    // ─── 테스트 1: 학생 조회 성공 ───

    // @Test
    // @DisplayName("ID로 학생을 조회하면 학생 정보를 반환한다")
    // void findById_ExistingId_ReturnsStudent() {
    //     // 1. Arrange (준비)
    //     Student mockStudent = new Student("민수", 3, 92, "minsu@school.kr");
    //     when(studentRepository.findById(1L))  // findById(1)이 호출되면
    //         .thenReturn(Optional.of(mockStudent));  // mockStudent를 반환해!
    //
    //     // 2. Act (실행)
    //     Student result = studentService.findById(1L);
    //
    //     // 3. Assert (검증)
    //     assertNotNull(result);              // null이 아닌지 확인
    //     assertEquals("민수", result.getName());  // 이름이 "민수"인지 확인
    //     assertEquals(92, result.getScore());     // 점수가 92인지 확인
    //
    //     // Repository가 정확히 1번 호출되었는지 확인
    //     verify(studentRepository, times(1)).findById(1L);
    // }


    // ─── 테스트 2: 없는 학생 조회 시 예외 ───

    // @Test
    // @DisplayName("존재하지 않는 ID로 조회하면 예외가 발생한다")
    // void findById_NonExistingId_ThrowsException() {
    //     // 1. Arrange
    //     when(studentRepository.findById(999L))
    //         .thenReturn(Optional.empty());  // 빈 결과 반환
    //
    //     // 2. Act & Assert (예외가 발생하는지 확인)
    //     assertThrows(StudentNotFoundException.class, () -> {
    //         studentService.findById(999L);
    //     });
    // }


    // ─── 테스트 3: 학생 등록 ───

    // @Test
    // @DisplayName("새 학생을 등록하면 저장된 학생을 반환한다")
    // void createStudent_ValidData_ReturnsSavedStudent() {
    //     // 1. Arrange
    //     Student newStudent = new Student("지우", 2, 88, "jiwoo@school.kr");
    //     when(studentRepository.save(any(Student.class)))
    //         .thenReturn(newStudent);
    //
    //     // 2. Act
    //     Student result = studentService.createStudent(newStudent);
    //
    //     // 3. Assert
    //     assertEquals("지우", result.getName());
    //     assertEquals(88, result.getScore());
    //     verify(studentRepository).save(any(Student.class));
    // }


    // ─── 테스트 4: 중복 이메일 등록 시 예외 ───

    // @Test
    // @DisplayName("이미 있는 이메일로 등록하면 예외가 발생한다")
    // void createStudent_DuplicateEmail_ThrowsException() {
    //     // 1. Arrange
    //     when(studentRepository.existsByEmail("minsu@school.kr"))
    //         .thenReturn(true);
    //
    //     Student duplicate = new Student("다른민수", 1, 80, "minsu@school.kr");
    //
    //     // 2. Act & Assert
    //     assertThrows(DuplicateStudentException.class, () -> {
    //         studentService.createStudent(duplicate);
    //     });
    //
    //     // save()가 호출되지 않았는지 확인 (저장 안 됐어야 함!)
    //     verify(studentRepository, never()).save(any());
    // }


    // ─────────────────────────────────────────────────────────
    // 개념 설명용 main 메서드
    // ─────────────────────────────────────────────────────────

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  Spring 10단계 : 서비스 단위 테스트");
        System.out.println("============================================================");
        System.out.println();

        lesson1UnitTestBasics();
        lesson2MockAndVerify();
        lesson3AssertionMethods();
    }

    public static void lesson1UnitTestBasics() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 1 : 단위 테스트 기초                   │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  테스트 3단계 (AAA 패턴):");
        System.out.println();
        System.out.println("  1. Arrange (준비)");
        System.out.println("     → 테스트에 필요한 데이터와 Mock 설정");
        System.out.println("     → when(mock.method()).thenReturn(값)");
        System.out.println();
        System.out.println("  2. Act (실행)");
        System.out.println("     → 테스트할 메서드 호출");
        System.out.println("     → result = service.findById(1L)");
        System.out.println();
        System.out.println("  3. Assert (검증)");
        System.out.println("     → 결과가 기대한 대로인지 확인");
        System.out.println("     → assertEquals(expected, actual)");
        System.out.println();
        System.out.println("  비유: 요리 레시피 테스트!");
        System.out.println("    준비: 재료 준비 (밀가루, 계란, 우유)");
        System.out.println("    실행: 레시피대로 요리");
        System.out.println("    검증: 맛이 기대한 대로인지 확인");
        System.out.println();
    }

    public static void lesson2MockAndVerify() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 2 : Mock과 Verify                     │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  Mock 핵심 메서드:");
        System.out.println();
        System.out.println("  when(...).thenReturn(값)");
        System.out.println("    → '이렇게 호출되면 이 값을 반환해'");
        System.out.println("    → 가짜 응답 설정");
        System.out.println();
        System.out.println("  when(...).thenThrow(예외)");
        System.out.println("    → '이렇게 호출되면 이 예외를 던져'");
        System.out.println();
        System.out.println("  verify(mock).method()");
        System.out.println("    → '이 메서드가 호출되었는지 확인'");
        System.out.println();
        System.out.println("  verify(mock, times(2)).method()");
        System.out.println("    → '정확히 2번 호출되었는지 확인'");
        System.out.println();
        System.out.println("  verify(mock, never()).method()");
        System.out.println("    → '한 번도 호출되지 않았는지 확인'");
        System.out.println();
    }

    public static void lesson3AssertionMethods() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 3 : JUnit5 Assertion 메서드            │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  JUnit5 주요 검증 메서드:");
        System.out.println();
        System.out.println("  assertEquals(expected, actual)");
        System.out.println("    → 두 값이 같은지 확인");
        System.out.println();
        System.out.println("  assertNotNull(object)");
        System.out.println("    → null이 아닌지 확인");
        System.out.println();
        System.out.println("  assertTrue(condition)");
        System.out.println("    → 조건이 true인지 확인");
        System.out.println();
        System.out.println("  assertThrows(예외.class, () -> { 코드 })");
        System.out.println("    → 해당 예외가 발생하는지 확인");
        System.out.println();
        System.out.println("  assertAll(");
        System.out.println("    () -> assertEquals(a, b),");
        System.out.println("    () -> assertEquals(c, d)");
        System.out.println("  )");
        System.out.println("    → 여러 검증을 한번에 (하나 실패해도 나머지 실행)");
        System.out.println();
    }
}
