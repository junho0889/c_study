/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Spring 학습 09단계: 에러 응답 DTO (ErrorResponse.java)
  ─ 일관된 에러 응답 형식 정의 ─

  모든 에러 응답이 이 형식을 따르면
  프론트엔드에서 에러 처리가 훨씬 쉬워집니다!

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;


/*
┌─────────────────────────────────────────────────────────────┐
│  에러 응답 DTO = 에러 정보를 담는 그릇                       │
│                                                             │
│  비유: 병원 진단서 양식!                                     │
│  어떤 병원에서든 같은 양식의 진단서를 쓰듯,                  │
│  어떤 API 에러든 같은 형식의 응답을 보냅니다.                │
│                                                             │
│  응답 예시:                                                 │
│  {                                                          │
│    "status": 404,                                           │
│    "code": "STUDENT_NOT_FOUND",                             │
│    "message": "학생을 찾을 수 없습니다",                    │
│    "timestamp": "2026-03-21T10:30:00",                      │
│    "path": "/api/students/999",                             │
│    "validationErrors": []                                   │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
*/
public class ErrorResponse {

    // ─── 필드 ───

    private int status;              // HTTP 상태 코드 (404, 400, 500 등)
    private String code;             // 커스텀 에러 코드 (STUDENT_NOT_FOUND 등)
    private String message;          // 사람이 읽을 수 있는 에러 메시지
    private String timestamp;        // 에러 발생 시각
    private String path;             // 에러가 발생한 API 경로

    /*
     * 유효성 검증 에러 목록
     *
     * @Valid 실패 시 여러 필드에 동시에 오류가 있을 수 있으므로
     * 리스트로 모든 오류를 한번에 알려 줍니다.
     *
     * 예: ["name: 이름은 필수입니다", "score: 0 이상이어야 합니다"]
     */
    private List<String> validationErrors;


    // ─── 생성자 ───

    public ErrorResponse() {
        this.timestamp = LocalDateTime.now().toString();
        this.validationErrors = new ArrayList<>();
    }

    public ErrorResponse(int status, String code, String message, String path) {
        this();
        this.status = status;
        this.code = code;
        this.message = message;
        this.path = path;
    }


    // ─── Getter / Setter ───

    public int getStatus() { return status; }
    public void setStatus(int status) { this.status = status; }

    public String getCode() { return code; }
    public void setCode(String code) { this.code = code; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }

    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }

    public String getPath() { return path; }
    public void setPath(String path) { this.path = path; }

    public List<String> getValidationErrors() { return validationErrors; }
    public void setValidationErrors(List<String> validationErrors) {
        this.validationErrors = validationErrors;
    }


    @Override
    public String toString() {
        return "ErrorResponse{"
                + "status=" + status
                + ", code='" + code + "'"
                + ", message='" + message + "'"
                + ", timestamp='" + timestamp + "'"
                + ", path='" + path + "'"
                + ", validationErrors=" + validationErrors
                + "}";
    }


    // ─────────────────────────────────────────────────────────
    // 개념 설명용 main
    // ─────────────────────────────────────────────────────────

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  Spring 09단계 : 에러 응답 DTO");
        System.out.println("============================================================");
        System.out.println();

        // 404 에러 예시
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  예시 1 : 404 Not Found                     │");
        System.out.println("└──────────────────────────────────────────────┘");
        ErrorResponse notFound = new ErrorResponse(
            404, "STUDENT_NOT_FOUND",
            "학생을 찾을 수 없습니다. ID: 999",
            "/api/students/999"
        );
        System.out.println("  " + notFound);
        System.out.println();

        // 400 유효성 검증 에러 예시
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  예시 2 : 400 Validation Error              │");
        System.out.println("└──────────────────────────────────────────────┘");
        ErrorResponse validationError = new ErrorResponse(
            400, "VALIDATION_FAILED",
            "입력 데이터 유효성 검증에 실패했습니다",
            "/api/students"
        );
        List<String> errors = new ArrayList<>();
        errors.add("name: 이름은 필수입니다");
        errors.add("score: 0 이상이어야 합니다");
        errors.add("email: 이메일 형식이 올바르지 않습니다");
        validationError.setValidationErrors(errors);
        System.out.println("  " + validationError);
        System.out.println();

        // 500 서버 에러 예시
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  예시 3 : 500 Internal Server Error         │");
        System.out.println("└──────────────────────────────────────────────┘");
        ErrorResponse serverError = new ErrorResponse(
            500, "INTERNAL_ERROR",
            "서버 내부 오류가 발생했습니다. 관리자에게 문의하세요.",
            "/api/students"
        );
        System.out.println("  " + serverError);
        System.out.println();
        System.out.println("  주의: 500 에러의 상세 내용(스택 트레이스)은");
        System.out.println("       절대 클라이언트에게 노출하면 안 됩니다!");
        System.out.println("       보안 취약점이 될 수 있습니다.");
        System.out.println();
    }
}
