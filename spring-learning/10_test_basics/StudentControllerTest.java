/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Spring 학습 10단계: 컨트롤러 테스트 (StudentControllerTest.java)
  ─ @WebMvcTest, MockMvc, @MockBean, 통합 테스트 vs 단위 테스트 ─

  컨트롤러 테스트는 "HTTP 요청을 보내고 응답을 확인"합니다.
  진짜 서버를 띄우지 않고도 테스트할 수 있습니다!

  ■ 이 파일은 개념 설명용입니다 (컴파일하려면 Spring Boot 프로젝트 필요)

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// import org.junit.jupiter.api.*;
// import org.springframework.beans.factory.annotation.Autowired;
// import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
// import org.springframework.boot.test.mock.bean.MockBean;
// import org.springframework.http.MediaType;
// import org.springframework.test.web.servlet.MockMvc;
// import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
// import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
// import static org.mockito.Mockito.*;


/*
┌─────────────────────────────────────────────────────────────┐
│  @WebMvcTest vs @SpringBootTest                             │
│                                                             │
│  비유:                                                      │
│                                                             │
│  @WebMvcTest = 자동차의 핸들만 테스트                       │
│    - Controller만 로드 (가볍고 빠름!)                        │
│    - Service, Repository는 Mock으로 대체                    │
│    - 웹 관련만 테스트 (HTTP 요청/응답)                       │
│                                                             │
│  @SpringBootTest = 자동차 전체를 시운전                      │
│    - 모든 Bean을 로드 (무겁고 느림)                          │
│    - 실제 DB 연결 가능                                      │
│    - 전체 흐름을 테스트 (통합 테스트)                        │
│                                                             │
│  ┌────────────────┐  ┌──────────────────────────────────┐  │
│  │  @WebMvcTest    │  │  @SpringBootTest                  │  │
│  │  Controller만  │  │  Controller + Service             │  │
│  │  (빠름, 가벼움)│  │  + Repository + DB                │  │
│  │                │  │  (느림, 무거움, 하지만 완전함)     │  │
│  └────────────────┘  └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
*/


// @WebMvcTest(StudentController.class)  // StudentController만 로드!
public class StudentControllerTest {

    /*
     * MockMvc = 가짜 HTTP 요청을 보내는 도구
     *
     * 비유: 실제 웹 브라우저를 열지 않고도
     * 마치 브라우저처럼 GET, POST 요청을 보내고
     * 응답을 확인할 수 있습니다!
     */
    // @Autowired
    // private MockMvc mockMvc;

    /*
     * @MockBean = Spring 컨텍스트에 가짜 Bean 등록
     *
     * @Mock과 비슷하지만 Spring 컨텍스트에 직접 등록!
     * Controller가 의존하는 Service를 가짜로 교체합니다.
     *
     * 비유: 영화 촬영 세트에서 진짜 건물 대신 세트장을 쓰는 것!
     */
    // @MockBean
    // private StudentService studentService;


    // ─── 테스트 1: GET /api/students/{id} 성공 ───

    // @Test
    // @DisplayName("GET /api/students/1 → 200 OK + 학생 정보")
    // void getStudent_ExistingId_Returns200() throws Exception {
    //     // 1. Arrange
    //     Student mockStudent = new Student("민수", 3, 92, "minsu@school.kr");
    //     when(studentService.findById(1L)).thenReturn(mockStudent);
    //
    //     // 2. Act & Assert
    //     mockMvc.perform(
    //             get("/api/students/1")            // GET 요청
    //                 .contentType(MediaType.APPLICATION_JSON)
    //         )
    //         .andExpect(status().isOk())            // 200 OK 확인
    //         .andExpect(jsonPath("$.name").value("민수"))     // JSON 필드 확인
    //         .andExpect(jsonPath("$.grade").value(3))
    //         .andExpect(jsonPath("$.score").value(92));
    // }


    // ─── 테스트 2: GET /api/students/{id} → 404 ───

    // @Test
    // @DisplayName("GET /api/students/999 → 404 Not Found")
    // void getStudent_NonExistingId_Returns404() throws Exception {
    //     // 1. Arrange
    //     when(studentService.findById(999L))
    //         .thenThrow(new StudentNotFoundException(999L));
    //
    //     // 2. Act & Assert
    //     mockMvc.perform(get("/api/students/999"))
    //         .andExpect(status().isNotFound())      // 404 확인
    //         .andExpect(jsonPath("$.code").value("STUDENT_NOT_FOUND"));
    // }


    // ─── 테스트 3: POST /api/students 성공 ───

    // @Test
    // @DisplayName("POST /api/students → 201 Created")
    // void createStudent_ValidData_Returns201() throws Exception {
    //     // 1. Arrange
    //     Student saved = new Student("지우", 2, 88, "jiwoo@school.kr");
    //     when(studentService.createStudent(any())).thenReturn(saved);
    //
    //     String requestBody = """
    //         {
    //             "name": "지우",
    //             "grade": 2,
    //             "score": 88,
    //             "email": "jiwoo@school.kr"
    //         }
    //         """;
    //
    //     // 2. Act & Assert
    //     mockMvc.perform(
    //             post("/api/students")
    //                 .contentType(MediaType.APPLICATION_JSON)
    //                 .content(requestBody)          // 요청 본문
    //         )
    //         .andExpect(status().isCreated())        // 201 확인
    //         .andExpect(jsonPath("$.name").value("지우"));
    // }


    // ─── 테스트 4: POST /api/students → 400 (유효성 검증 실패) ───

    // @Test
    // @DisplayName("POST /api/students 빈 이름 → 400 Bad Request")
    // void createStudent_EmptyName_Returns400() throws Exception {
    //     String invalidBody = """
    //         {
    //             "name": "",
    //             "grade": 2,
    //             "score": 150,
    //             "email": "not-an-email"
    //         }
    //         """;
    //
    //     mockMvc.perform(
    //             post("/api/students")
    //                 .contentType(MediaType.APPLICATION_JSON)
    //                 .content(invalidBody)
    //         )
    //         .andExpect(status().isBadRequest())     // 400 확인
    //         .andExpect(jsonPath("$.code").value("VALIDATION_FAILED"));
    // }


    // ─────────────────────────────────────────────────────────
    // 개념 설명용 main 메서드
    // ─────────────────────────────────────────────────────────

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  Spring 10단계 : 컨트롤러 테스트");
        System.out.println("============================================================");
        System.out.println();

        lesson1MockMvc();
        lesson2TestSlicing();
        lesson3IntegrationVsUnit();
        lesson4TestingBestPractices();
    }

    public static void lesson1MockMvc() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 1 : MockMvc 사용법                    │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  MockMvc로 HTTP 요청 보내기:");
        System.out.println();
        System.out.println("  mockMvc.perform(");
        System.out.println("      get(\"/api/students/1\")        // 요청 종류와 URL");
        System.out.println("          .contentType(JSON)          // Content-Type");
        System.out.println("          .header(\"Authorization\", ...) // 헤더");
        System.out.println("  )");
        System.out.println("  .andExpect(status().isOk())         // 상태 코드 확인");
        System.out.println("  .andExpect(jsonPath(\"$.name\").value(\"민수\")) // JSON 확인");
        System.out.println("  .andDo(print());                    // 요청/응답 출력");
        System.out.println();
        System.out.println("  요청 메서드: get(), post(), put(), patch(), delete()");
        System.out.println();
    }

    public static void lesson2TestSlicing() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 2 : 테스트 슬라이싱                    │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  Spring Boot는 필요한 부분만 로드하는 테스트를 지원합니다:");
        System.out.println();
        System.out.println("  @WebMvcTest         → Controller 레이어만");
        System.out.println("  @DataJpaTest        → Repository + JPA만");
        System.out.println("  @RestClientTest     → REST 클라이언트만");
        System.out.println("  @JsonTest           → JSON 직렬화/역직렬화만");
        System.out.println("  @SpringBootTest     → 전체 (통합 테스트)");
        System.out.println();
        System.out.println("  비유: 자동차 테스트");
        System.out.println("    @WebMvcTest    = 핸들만 테스트 (빠름)");
        System.out.println("    @DataJpaTest   = 엔진만 테스트 (빠름)");
        System.out.println("    @SpringBootTest = 전체 시운전 (느리지만 확실)");
        System.out.println();
    }

    public static void lesson3IntegrationVsUnit() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 3 : 통합 테스트 vs 단위 테스트          │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  단위 테스트 (Unit Test):");
        System.out.println("    - 클래스 하나를 독립적으로 테스트");
        System.out.println("    - 의존성은 Mock으로 대체");
        System.out.println("    - 매우 빠름 (밀리초 단위)");
        System.out.println("    - 예: StudentServiceTest");
        System.out.println();
        System.out.println("  통합 테스트 (Integration Test):");
        System.out.println("    - 여러 컴포넌트를 합쳐서 테스트");
        System.out.println("    - 실제 DB, 실제 네트워크 사용 가능");
        System.out.println("    - 느림 (초 단위)");
        System.out.println("    - 예: @SpringBootTest");
        System.out.println();
        System.out.println("  테스트 피라미드:");
        System.out.println("          /\\");
        System.out.println("         /  \\        E2E (소수)");
        System.out.println("        /────\\");
        System.out.println("       / 통합  \\     통합 테스트 (중간)");
        System.out.println("      /────────\\");
        System.out.println("     /  단위 테스트 \\  단위 테스트 (많이!)");
        System.out.println("    /──────────────\\");
        System.out.println();
        System.out.println("  단위 테스트를 가장 많이 작성하고,");
        System.out.println("  통합 테스트는 핵심 흐름만 확인합니다.");
        System.out.println();
    }

    public static void lesson4TestingBestPractices() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 4 : 테스트 작성 모범 사례              │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  1. 테스트 이름은 서술적으로");
        System.out.println("     ✗ test1(), testA()");
        System.out.println("     ✓ findById_ExistingId_ReturnsStudent()");
        System.out.println();
        System.out.println("  2. 한 테스트에 한 가지만 검증");
        System.out.println("     ✗ 조회 + 수정 + 삭제를 한 테스트에");
        System.out.println("     ✓ 조회 테스트, 수정 테스트, 삭제 테스트 분리");
        System.out.println();
        System.out.println("  3. 성공 케이스와 실패 케이스 모두 작성");
        System.out.println("     ✗ 정상 조회만 테스트");
        System.out.println("     ✓ 정상 조회 + 없는 ID + 권한 없음 모두 테스트");
        System.out.println();
        System.out.println("  4. 테스트 간 독립성 유지");
        System.out.println("     ✗ 테스트 A의 결과에 테스트 B가 의존");
        System.out.println("     ✓ 각 테스트가 독립적으로 실행 가능");
        System.out.println();
        System.out.println("  5. @DisplayName으로 한글 설명 추가");
        System.out.println("     @DisplayName(\"존재하지 않는 ID로 조회하면 404\")");
        System.out.println("     → 테스트 결과를 한글로 읽을 수 있어 이해하기 쉬움!");
        System.out.println();
    }
}
