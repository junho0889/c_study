/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Spring 학습 09단계: 예외 처리 (GlobalExceptionHandler.java)
  ─ @ControllerAdvice, @ExceptionHandler, 커스텀 예외, @Valid ─

  모든 컨트롤러에서 발생하는 예외를 한 곳에서 처리합니다.
  에러 응답을 일관된 형식으로 보내줍니다.

  ■ 이 파일은 개념 설명용입니다 (컴파일하려면 Spring Boot 프로젝트 필요)

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// import org.springframework.http.HttpStatus;
// import org.springframework.http.ResponseEntity;
// import org.springframework.web.bind.MethodArgumentNotValidException;
// import org.springframework.web.bind.annotation.ControllerAdvice;
// import org.springframework.web.bind.annotation.ExceptionHandler;


/*
┌─────────────────────────────────────────────────────────────┐
│  @ControllerAdvice란?                                       │
│                                                             │
│  비유: 학교의 "총무부"!                                      │
│                                                             │
│  각 교실(컨트롤러)에서 문제가 생기면                         │
│  총무부(ControllerAdvice)가 중앙에서 처리합니다.             │
│                                                             │
│  ControllerAdvice가 없으면:                                 │
│    각 컨트롤러마다 try-catch 반복 → 코드 중복!               │
│    에러 형식이 컨트롤러마다 제각각!                          │
│                                                             │
│  ControllerAdvice가 있으면:                                 │
│    예외 처리를 한 곳에 집중! → 일관된 에러 응답!             │
└─────────────────────────────────────────────────────────────┘
*/


/*
┌─────────────────────────────────────────────────────────────┐
│  커스텀 예외 클래스들                                        │
│                                                             │
│  비유: "학생을 못 찾았다"는 그냥 RuntimeException보다        │
│  "StudentNotFoundException"이 훨씬 명확합니다!               │
│  에러 이름만 봐도 무슨 문제인지 알 수 있으니까요.            │
└─────────────────────────────────────────────────────────────┘
*/

// 학생을 찾을 수 없을 때
class StudentNotFoundException extends RuntimeException {
    private final Long studentId;

    public StudentNotFoundException(Long studentId) {
        super("학생을 찾을 수 없습니다. ID: " + studentId);
        this.studentId = studentId;
    }

    public Long getStudentId() { return studentId; }
}

// 중복 데이터가 있을 때
class DuplicateStudentException extends RuntimeException {
    private final String email;

    public DuplicateStudentException(String email) {
        super("이미 등록된 이메일입니다: " + email);
        this.email = email;
    }

    public String getEmail() { return email; }
}

// 권한이 없을 때
class AccessDeniedException extends RuntimeException {
    public AccessDeniedException(String message) {
        super(message);
    }
}


/*
┌─────────────────────────────────────────────────────────────┐
│  에러 응답 DTO (ErrorResponse.java 내용을 여기에 포함)       │
│                                                             │
│  모든 에러 응답을 이 형식으로 통일합니다!                    │
│  클라이언트는 항상 같은 구조의 에러를 받으니 처리가 쉽습니다.│
└─────────────────────────────────────────────────────────────┘
*/

// → ErrorResponse.java에 별도 정의됨


// @ControllerAdvice
public class GlobalExceptionHandler {

    /*
     * ┌───────────────────────────────────────────────────────┐
     * │  @ExceptionHandler = 특정 예외가 발생하면 이 메서드!   │
     * │                                                       │
     * │  비유: 소방서의 신고 접수 시스템!                      │
     * │  "화재 신고" → 소방차 출동                             │
     * │  "도난 신고" → 경찰차 출동                             │
     * │  "의료 신고" → 구급차 출동                             │
     * │                                                       │
     * │  예외 종류에 따라 다른 처리를 합니다!                  │
     * └───────────────────────────────────────────────────────┘
     */

    // ─── 학생 못 찾음 (404) ───
    // @ExceptionHandler(StudentNotFoundException.class)
    // public ResponseEntity<ErrorResponse> handleStudentNotFound(StudentNotFoundException e) {
    //     ErrorResponse error = new ErrorResponse(
    //         HttpStatus.NOT_FOUND.value(),        // 404
    //         "STUDENT_NOT_FOUND",                  // 에러 코드
    //         e.getMessage(),                       // 에러 메시지
    //         "/api/students/" + e.getStudentId()   // 요청 경로
    //     );
    //     return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    // }


    // ─── 중복 데이터 (409 Conflict) ───
    // @ExceptionHandler(DuplicateStudentException.class)
    // public ResponseEntity<ErrorResponse> handleDuplicate(DuplicateStudentException e) {
    //     ErrorResponse error = new ErrorResponse(
    //         HttpStatus.CONFLICT.value(),
    //         "DUPLICATE_STUDENT",
    //         e.getMessage(),
    //         "/api/students"
    //     );
    //     return ResponseEntity.status(HttpStatus.CONFLICT).body(error);
    // }


    // ─── 권한 없음 (403) ───
    // @ExceptionHandler(AccessDeniedException.class)
    // public ResponseEntity<ErrorResponse> handleAccessDenied(AccessDeniedException e) {
    //     ErrorResponse error = new ErrorResponse(
    //         HttpStatus.FORBIDDEN.value(),
    //         "ACCESS_DENIED",
    //         e.getMessage(),
    //         null
    //     );
    //     return ResponseEntity.status(HttpStatus.FORBIDDEN).body(error);
    // }


    /*
     * ┌───────────────────────────────────────────────────────┐
     * │  유효성 검증 에러 처리 (@Valid 실패 시)                │
     * │                                                       │
     * │  @Valid와 함께 사용하면 자동으로 데이터를 검증합니다.  │
     * │                                                       │
     * │  컨트롤러에서:                                        │
     * │  @PostMapping                                         │
     * │  public Student create(@Valid @RequestBody StudentDto)│
     * │                         ↑ 이게 있으면 자동 검증!       │
     * │                                                       │
     * │  DTO에서:                                             │
     * │  @NotNull → null이면 안 됨                            │
     * │  @NotBlank → 빈 문자열이면 안 됨                      │
     * │  @Min(0) @Max(100) → 0~100 사이만                     │
     * │  @Email → 이메일 형식 확인                            │
     * │  @Size(min=1, max=50) → 길이 제한                     │
     * └───────────────────────────────────────────────────────┘
     */

    // @ExceptionHandler(MethodArgumentNotValidException.class)
    // public ResponseEntity<ErrorResponse> handleValidation(MethodArgumentNotValidException e) {
    //     List<String> errors = e.getBindingResult()
    //         .getFieldErrors()
    //         .stream()
    //         .map(error -> error.getField() + ": " + error.getDefaultMessage())
    //         .collect(Collectors.toList());
    //
    //     ErrorResponse errorResponse = new ErrorResponse(
    //         HttpStatus.BAD_REQUEST.value(),
    //         "VALIDATION_FAILED",
    //         "입력 데이터 유효성 검증에 실패했습니다",
    //         null
    //     );
    //     errorResponse.setValidationErrors(errors);
    //
    //     return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(errorResponse);
    // }


    // ─── 그 외 모든 예외 (500) ───
    // @ExceptionHandler(Exception.class)
    // public ResponseEntity<ErrorResponse> handleGeneral(Exception e) {
    //     // 예상 못한 에러는 상세 내용을 클라이언트에 노출하면 안 됨!
    //     // 대신 로그에 기록합니다.
    //     // log.error("예상하지 못한 에러", e);
    //
    //     ErrorResponse error = new ErrorResponse(
    //         HttpStatus.INTERNAL_SERVER_ERROR.value(),
    //         "INTERNAL_ERROR",
    //         "서버 내부 오류가 발생했습니다. 관리자에게 문의하세요.",
    //         null
    //     );
    //     return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    // }


    // ─────────────────────────────────────────────────────────
    // 개념 설명용 main 메서드
    // ─────────────────────────────────────────────────────────

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  Spring 09단계 : 예외 처리");
        System.out.println("============================================================");
        System.out.println();

        lesson1ControllerAdvice();
        lesson2CustomExceptions();
        lesson3ValidationAnnotations();
        lesson4ErrorResponseDesign();
    }

    public static void lesson1ControllerAdvice() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 1 : @ControllerAdvice                 │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  @ControllerAdvice 없이:");
        System.out.println("    StudentController에 try-catch");
        System.out.println("    ScoreController에 try-catch");
        System.out.println("    AdminController에 try-catch");
        System.out.println("    → 반복! 불일치! 실수!");
        System.out.println();
        System.out.println("  @ControllerAdvice 사용:");
        System.out.println("    GlobalExceptionHandler 하나로 모든 예외 처리!");
        System.out.println("    → 깔끔! 일관된 에러 형식! 유지보수 쉬움!");
        System.out.println();
    }

    public static void lesson2CustomExceptions() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 2 : 커스텀 예외                        │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  나쁜 예:");
        System.out.println("    throw new RuntimeException(\"학생 없음\");");
        System.out.println("    → 어떤 종류의 에러인지 알기 어렵고, HTTP 코드 매핑도 애매");
        System.out.println();
        System.out.println("  좋은 예:");
        System.out.println("    throw new StudentNotFoundException(id);");
        System.out.println("    → 에러 이름이 명확하고, @ExceptionHandler로 정확히 매핑");
        System.out.println();

        // 실제 예외 발생 시뮬레이션
        try {
            throw new StudentNotFoundException(999L);
        } catch (StudentNotFoundException e) {
            System.out.println("  시뮬레이션: " + e.getMessage());
            System.out.println("  → 이 예외를 @ExceptionHandler가 잡아서 404로 응답!");
        }
        System.out.println();
    }

    public static void lesson3ValidationAnnotations() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 3 : 유효성 검증 어노테이션             │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  DTO 클래스에 붙이는 검증 어노테이션:");
        System.out.println();
        System.out.println("  @NotNull          → null이면 안 됨");
        System.out.println("  @NotBlank         → null, 빈 문자열, 공백만 있으면 안 됨");
        System.out.println("  @NotEmpty         → null, 빈 컬렉션이면 안 됨");
        System.out.println("  @Size(min, max)   → 문자열/컬렉션 크기 제한");
        System.out.println("  @Min(0) @Max(100) → 숫자 범위 제한");
        System.out.println("  @Email            → 이메일 형식 확인");
        System.out.println("  @Pattern(regexp)  → 정규식 패턴 확인");
        System.out.println("  @Past / @Future   → 과거/미래 날짜 확인");
        System.out.println();
        System.out.println("  사용법:");
        System.out.println("    public class CreateStudentRequest {");
        System.out.println("        @NotBlank(message = \"이름은 필수입니다\")");
        System.out.println("        private String name;");
        System.out.println();
        System.out.println("        @Min(value = 0, message = \"점수는 0 이상\")");
        System.out.println("        @Max(value = 100, message = \"점수는 100 이하\")");
        System.out.println("        private int score;");
        System.out.println("    }");
        System.out.println();
    }

    public static void lesson4ErrorResponseDesign() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 4 : 에러 응답 설계 모범 사례           │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  좋은 에러 응답에 필요한 것:");
        System.out.println();
        System.out.println("  {");
        System.out.println("    \"status\": 404,");
        System.out.println("    \"code\": \"STUDENT_NOT_FOUND\",");
        System.out.println("    \"message\": \"학생을 찾을 수 없습니다. ID: 999\",");
        System.out.println("    \"timestamp\": \"2026-03-21T10:30:00\",");
        System.out.println("    \"path\": \"/api/students/999\"");
        System.out.println("  }");
        System.out.println();
        System.out.println("  원칙:");
        System.out.println("    1. HTTP 상태 코드와 body의 status를 일치시키기");
        System.out.println("    2. 고유한 에러 코드(code)로 프론트엔드가 분기 가능");
        System.out.println("    3. 사용자에게 보여줄 수 있는 message 제공");
        System.out.println("    4. 500 에러의 상세 내용(스택 트레이스)은 절대 노출하지 않기!");
        System.out.println();
    }
}
