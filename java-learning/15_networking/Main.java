/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Java 학습 15단계: 네트워킹
  ─ HTTP 개념, REST API, 요청/응답, Socket, URL 처리 ─

  [학습 목표]
  1. HTTP 프로토콜의 기본 개념을 안다
  2. REST API의 구조(GET/POST/PUT/DELETE)를 이해한다
  3. Java HttpClient로 HTTP 요청을 보낸다
  4. JSON 요청/응답을 처리한다
  5. Socket 통신의 기본 개념을 안다
  6. URL과 URI를 이해한다

  ■ 컴파일: javac Main.java
  ■ 실행:   java Main

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

import java.util.*;
import java.util.stream.*;


// =====================================================================
// 레슨 1 — HTTP 프로토콜 기초
// =====================================================================
/*
★ HTTP = HyperText Transfer Protocol (웹의 통신 규칙)
  → 클라이언트(브라우저)와 서버 사이의 "대화 규칙"

  ┌──────────────────────────────────────────────────┐
  │  비유: HTTP는 "편지 양식"                         │
  │                                                  │
  │  보내는 사람: 클라이언트 (브라우저, 앱)           │
  │  받는 사람:   서버 (웹 서버)                      │
  │                                                  │
  │  편지(요청)에는:                                  │
  │    "뭘 해달라" (GET/POST) + "주소" (URL)          │
  │  답장(응답)에는:                                  │
  │    "결과" (200 OK) + "내용" (HTML/JSON)           │
  └──────────────────────────────────────────────────┘

★ HTTP 메서드
  ┌─────────┬──────────────────────────────────────┐
  │ GET     │ 데이터 조회 (읽기)                    │
  │         │ "학생 목록을 보여줘"                  │
  ├─────────┼──────────────────────────────────────┤
  │ POST    │ 데이터 생성 (쓰기)                    │
  │         │ "새 학생을 등록해줘"                  │
  ├─────────┼──────────────────────────────────────┤
  │ PUT     │ 데이터 수정 (전체 교체)               │
  │         │ "학생 정보를 바꿔줘"                  │
  ├─────────┼──────────────────────────────────────┤
  │ PATCH   │ 데이터 부분 수정                      │
  │         │ "학생 점수만 바꿔줘"                  │
  ├─────────┼──────────────────────────────────────┤
  │ DELETE  │ 데이터 삭제                           │
  │         │ "학생을 삭제해줘"                     │
  └─────────┴──────────────────────────────────────┘

★ HTTP 상태 코드
  ┌──────┬────────────┬──────────────────────────────┐
  │ 코드 │ 의미       │ 설명                          │
  ├──────┼────────────┼──────────────────────────────┤
  │ 200  │ OK         │ 성공!                         │
  │ 201  │ Created    │ 생성 성공!                    │
  │ 204  │ No Content │ 성공했지만 반환할 내용 없음   │
  │ 400  │ Bad Request│ 잘못된 요청 (클라이언트 실수) │
  │ 401  │ Unauthorized│ 인증 필요                    │
  │ 403  │ Forbidden  │ 권한 없음                     │
  │ 404  │ Not Found  │ 리소스 없음 (주소 틀림)       │
  │ 500  │ Server Error│ 서버 에러                    │
  └──────┴────────────┴──────────────────────────────┘
*/


// =====================================================================
// 레슨 2 — REST API 구조
// =====================================================================
/*
★ REST = REpresentational State Transfer
  → 자원(Resource)을 URL로 표현하고, HTTP 메서드로 조작!

  ┌──────────────────────────────────────────────────┐
  │  비유: REST API는 "도서관 시스템"                 │
  │                                                  │
  │  GET /books          → 모든 책 목록              │
  │  GET /books/42       → 42번 책 정보              │
  │  POST /books         → 새 책 등록                │
  │  PUT /books/42       → 42번 책 수정              │
  │  DELETE /books/42    → 42번 책 삭제              │
  │                                                  │
  │  URL은 "명사" (자원), HTTP 메서드는 "동사" (행동)│
  └──────────────────────────────────────────────────┘

★ REST API 설계 규칙
  ┌──────────────────────────────────────────────┐
  │ ✓ /students         (복수형 명사)            │
  │ ✗ /getStudents      (동사 사용 금지!)        │
  │ ✗ /student-list     (리스트 표현 금지)       │
  │                                              │
  │ ✓ /students/42/scores  (계층 구조)           │
  │ ✓ /students?grade=A    (필터는 쿼리 파라미터)│
  └──────────────────────────────────────────────┘
*/


// =====================================================================
// 레슨 3 — 요청과 응답 시뮬레이션
// =====================================================================
/*
★ 실제 네트워크 없이 HTTP 요청/응답 구조를 이해하기 위한 시뮬레이션!
  → Request, Response 객체로 구조를 체험
*/

// ─── HTTP 요청 시뮬레이션 ───────────────────────────────
record HttpRequest(String method, String path, String body, Map<String, String> headers) {
    HttpRequest(String method, String path) {
        this(method, path, "", Map.of());
    }

    HttpRequest(String method, String path, String body) {
        this(method, path, body, Map.of("Content-Type", "application/json"));
    }
}

record HttpResponse(int statusCode, String statusText, String body) {
    boolean isSuccess() {
        return statusCode >= 200 && statusCode < 300;
    }

    static HttpResponse ok(String body) {
        return new HttpResponse(200, "OK", body);
    }

    static HttpResponse created(String body) {
        return new HttpResponse(201, "Created", body);
    }

    static HttpResponse notFound(String message) {
        return new HttpResponse(404, "Not Found", message);
    }

    static HttpResponse badRequest(String message) {
        return new HttpResponse(400, "Bad Request", message);
    }
}


// =====================================================================
// 레슨 4 — REST API 서버 시뮬레이션
// =====================================================================
record StudentData(int id, String name, int score) {}

class StudentApiServer {
    private final List<StudentData> students = new ArrayList<>();
    private int nextId = 1;

    StudentApiServer() {
        // 초기 데이터
        students.add(new StudentData(nextId++, "김철수", 92));
        students.add(new StudentData(nextId++, "이영희", 78));
        students.add(new StudentData(nextId++, "박민수", 55));
    }

    // ★ 요청을 받아 처리하는 라우터
    HttpResponse handleRequest(HttpRequest request) {
        return switch (request.method()) {
            case "GET" -> handleGet(request);
            case "POST" -> handlePost(request);
            case "DELETE" -> handleDelete(request);
            default -> HttpResponse.badRequest("지원하지 않는 메서드: " + request.method());
        };
    }

    private HttpResponse handleGet(HttpRequest request) {
        // GET /students → 전체 목록
        if ("/students".equals(request.path())) {
            String json = students.stream()
                    .map(s -> "    {\"id\":" + s.id()
                            + ", \"name\":\"" + s.name()
                            + "\", \"score\":" + s.score() + "}")
                    .collect(Collectors.joining(",\n", "  [\n", "\n  ]"));
            return HttpResponse.ok(json);
        }

        // GET /students/{id} → 개별 조회
        if (request.path().startsWith("/students/")) {
            try {
                int id = Integer.parseInt(request.path().replace("/students/", ""));
                return students.stream()
                        .filter(s -> s.id() == id)
                        .findFirst()
                        .map(s -> HttpResponse.ok(
                                "  {\"id\":" + s.id() + ", \"name\":\"" + s.name()
                                        + "\", \"score\":" + s.score() + "}"))
                        .orElse(HttpResponse.notFound("학생 ID " + id + "을(를) 찾을 수 없습니다."));
            } catch (NumberFormatException e) {
                return HttpResponse.badRequest("잘못된 ID 형식");
            }
        }

        return HttpResponse.notFound("경로를 찾을 수 없습니다: " + request.path());
    }

    private HttpResponse handlePost(HttpRequest request) {
        if ("/students".equals(request.path())) {
            // 간단한 JSON 파싱 시뮬레이션
            String body = request.body();
            if (body.isEmpty()) {
                return HttpResponse.badRequest("요청 본문이 비어있습니다.");
            }
            // 실제로는 JSON 파서 사용, 여기서는 간단히 시뮬레이션
            StudentData newStudent = new StudentData(nextId++, "새학생", 80);
            students.add(newStudent);
            return HttpResponse.created(
                    "  {\"id\":" + newStudent.id() + ", \"name\":\"" + newStudent.name()
                            + "\", \"score\":" + newStudent.score() + "}");
        }
        return HttpResponse.notFound("경로를 찾을 수 없습니다.");
    }

    private HttpResponse handleDelete(HttpRequest request) {
        if (request.path().startsWith("/students/")) {
            try {
                int id = Integer.parseInt(request.path().replace("/students/", ""));
                boolean removed = students.removeIf(s -> s.id() == id);
                if (removed) {
                    return new HttpResponse(204, "No Content", "삭제 완료");
                }
                return HttpResponse.notFound("학생 ID " + id + "을(를) 찾을 수 없습니다.");
            } catch (NumberFormatException e) {
                return HttpResponse.badRequest("잘못된 ID 형식");
            }
        }
        return HttpResponse.notFound("경로를 찾을 수 없습니다.");
    }
}


// =====================================================================
// 레슨 5 — Socket 기본 개념
// =====================================================================
/*
★ Socket = 네트워크 통신의 "끝점" (endpoint)
  → 두 프로그램이 네트워크를 통해 데이터를 주고받는 통로

  ┌──────────────────────────────────────────────────┐
  │  비유: Socket은 "전화기"                          │
  │                                                  │
  │  서버 소켓: 전화를 기다리는 전화기 (accept)       │
  │  클라이언트 소켓: 전화를 거는 전화기 (connect)    │
  │                                                  │
  │  연결되면 양방향 대화 가능!                       │
  │  (InputStream = 듣기, OutputStream = 말하기)      │
  └──────────────────────────────────────────────────┘

★ TCP vs UDP
  ┌────────────┬──────────────────┬──────────────────┐
  │            │ TCP              │ UDP              │
  ├────────────┼──────────────────┼──────────────────┤
  │ 연결       │ 연결 지향        │ 비연결           │
  │ 신뢰성     │ 높음 (순서 보장) │ 낮음 (손실 가능) │
  │ 속도       │ 상대적으로 느림  │ 빠름             │
  │ 사용 예    │ 웹, 이메일, 파일 │ 동영상, 게임     │
  └────────────┴──────────────────┴──────────────────┘

★ Socket 통신 흐름
  서버:                        클라이언트:
  1. ServerSocket(포트) 생성   1. Socket(IP, 포트) 생성
  2. accept() 대기             2. 연결됨!
  3. 연결됨!                   3. 데이터 보내기
  4. 데이터 받기               4. 데이터 받기
  5. 응답 보내기               5. 연결 종료
  6. 연결 종료
*/


// =====================================================================
// 레슨 6 — Java HttpClient (Java 11+)
// =====================================================================
/*
★ Java 11부터 기본 제공되는 HTTP 클라이언트!
  → 외부 라이브러리 없이 HTTP 요청 가능!

  HttpClient client = HttpClient.newHttpClient();

  HttpRequest request = HttpRequest.newBuilder()
      .uri(URI.create("https://api.example.com/data"))
      .GET()
      .build();

  HttpResponse<String> response = client.send(
      request, HttpResponse.BodyHandlers.ofString());

  System.out.println(response.statusCode());
  System.out.println(response.body());

★ 주요 HTTP 클라이언트 라이브러리
  ┌──────────────────┬──────────────────────────────┐
  │ 라이브러리        │ 특징                         │
  ├──────────────────┼──────────────────────────────┤
  │ java.net.http    │ Java 11+ 기본 제공           │
  │ OkHttp           │ 간결하고 효율적              │
  │ Apache HttpClient│ 가장 오래된 라이브러리       │
  │ Retrofit         │ REST API 전용 (Android 인기)│
  │ WebClient        │ Spring의 비동기 HTTP 클라이언트│
  └──────────────────┴──────────────────────────────┘
*/


// =====================================================================
//  메인 실행
// =====================================================================
public class Main {

    static void printRequest(HttpRequest req) {
        System.out.println("  ─── 요청 ──────────────────────────");
        System.out.println("  " + req.method() + " " + req.path());
        if (!req.body().isEmpty()) {
            System.out.println("  Body: " + req.body());
        }
    }

    static void printResponse(HttpResponse res) {
        System.out.println("  ─── 응답 ──────────────────────────");
        System.out.println("  Status: " + res.statusCode() + " " + res.statusText()
                + (res.isSuccess() ? " (성공)" : " (실패)"));
        if (!res.body().isEmpty()) {
            System.out.println("  Body:");
            System.out.println(res.body());
        }
    }

    public static void main(String[] args) {
        System.out.println("■■■ Java 15단계: 네트워킹 ■■■\n");

        // ─── 레슨 1~2: HTTP 기본 개념 ───────────────────
        System.out.println("── 레슨 1~2: HTTP와 REST API 개념 ──────────────");
        System.out.println("  HTTP 요청 구조:");
        System.out.println("    ┌──────────────────────────────────┐");
        System.out.println("    │ GET /students HTTP/1.1           │ ← 요청줄");
        System.out.println("    │ Host: api.school.com            │ ← 헤더");
        System.out.println("    │ Accept: application/json        │");
        System.out.println("    │                                 │ ← 빈 줄");
        System.out.println("    │ (본문 없음 - GET이므로)          │ ← 본문");
        System.out.println("    └──────────────────────────────────┘");
        System.out.println();
        System.out.println("  HTTP 응답 구조:");
        System.out.println("    ┌──────────────────────────────────┐");
        System.out.println("    │ HTTP/1.1 200 OK                 │ ← 상태줄");
        System.out.println("    │ Content-Type: application/json  │ ← 헤더");
        System.out.println("    │                                 │");
        System.out.println("    │ [{\"name\":\"Kim\",\"score\":92}] │ ← 본문");
        System.out.println("    └──────────────────────────────────┘");
        System.out.println();

        // ─── 레슨 3~4: REST API 시뮬레이션 ──────────────
        System.out.println("── 레슨 3~4: REST API 서버 시뮬레이션 ──────────");

        StudentApiServer server = new StudentApiServer();

        // ★ GET /students - 전체 목록 조회
        System.out.println("\n  [1] 전체 학생 조회");
        HttpRequest req1 = new HttpRequest("GET", "/students");
        printRequest(req1);
        HttpResponse res1 = server.handleRequest(req1);
        printResponse(res1);

        // ★ GET /students/1 - 개별 조회
        System.out.println("\n  [2] 학생 1번 조회");
        HttpRequest req2 = new HttpRequest("GET", "/students/1");
        printRequest(req2);
        HttpResponse res2 = server.handleRequest(req2);
        printResponse(res2);

        // ★ GET /students/99 - 없는 학생 조회 (404)
        System.out.println("\n  [3] 없는 학생 조회 (404)");
        HttpRequest req3 = new HttpRequest("GET", "/students/99");
        printRequest(req3);
        HttpResponse res3 = server.handleRequest(req3);
        printResponse(res3);

        // ★ POST /students - 학생 생성
        System.out.println("\n  [4] 새 학생 등록");
        HttpRequest req4 = new HttpRequest("POST", "/students",
                "{\"name\":\"최지은\",\"score\":88}");
        printRequest(req4);
        HttpResponse res4 = server.handleRequest(req4);
        printResponse(res4);

        // ★ DELETE /students/2 - 학생 삭제
        System.out.println("\n  [5] 학생 2번 삭제");
        HttpRequest req5 = new HttpRequest("DELETE", "/students/2");
        printRequest(req5);
        HttpResponse res5 = server.handleRequest(req5);
        printResponse(res5);

        // 삭제 후 전체 목록 확인
        System.out.println("\n  [6] 삭제 후 전체 목록");
        HttpResponse res6 = server.handleRequest(new HttpRequest("GET", "/students"));
        printResponse(res6);
        System.out.println();

        // ─── 레슨 5: Socket 개념 ────────────────────────
        System.out.println("── 레슨 5: Socket 통신 개념 ────────────────────");
        System.out.println("  Socket 통신 흐름:");
        System.out.println("  ┌──────────────┐          ┌──────────────┐");
        System.out.println("  │  서버         │          │  클라이언트   │");
        System.out.println("  │              │          │              │");
        System.out.println("  │ ServerSocket │          │              │");
        System.out.println("  │ accept()     │←─연결──→│ Socket()     │");
        System.out.println("  │              │          │              │");
        System.out.println("  │ read()       │←─데이터──│ write()      │");
        System.out.println("  │ write()      │──데이터─→│ read()       │");
        System.out.println("  │              │          │              │");
        System.out.println("  │ close()      │          │ close()      │");
        System.out.println("  └──────────────┘          └──────────────┘");
        System.out.println();

        System.out.println("  ★ Socket 코드 예시 (개념만):");
        System.out.println("    // 서버:");
        System.out.println("    ServerSocket server = new ServerSocket(8080);");
        System.out.println("    Socket client = server.accept();  // 대기");
        System.out.println("    BufferedReader in = new BufferedReader(");
        System.out.println("        new InputStreamReader(client.getInputStream()));");
        System.out.println("    String msg = in.readLine();");
        System.out.println();
        System.out.println("    // 클라이언트:");
        System.out.println("    Socket socket = new Socket(\"localhost\", 8080);");
        System.out.println("    PrintWriter out = new PrintWriter(");
        System.out.println("        socket.getOutputStream(), true);");
        System.out.println("    out.println(\"Hello Server!\");");
        System.out.println();

        // ─── 레슨 6: HttpClient 코드 예시 ───────────────
        System.out.println("── 레슨 6: Java HttpClient (Java 11+) ──────────");
        System.out.println("  ★ 실제 HTTP 요청 코드 (개념):");
        System.out.println();
        System.out.println("  // GET 요청");
        System.out.println("  var client = HttpClient.newHttpClient();");
        System.out.println("  var request = HttpRequest.newBuilder()");
        System.out.println("      .uri(URI.create(\"https://api.example.com/users\"))");
        System.out.println("      .GET()");
        System.out.println("      .build();");
        System.out.println("  var response = client.send(request,");
        System.out.println("      BodyHandlers.ofString());");
        System.out.println("  System.out.println(response.body());");
        System.out.println();
        System.out.println("  // POST 요청 (JSON)");
        System.out.println("  var postRequest = HttpRequest.newBuilder()");
        System.out.println("      .uri(URI.create(\"https://api.example.com/users\"))");
        System.out.println("      .header(\"Content-Type\", \"application/json\")");
        System.out.println("      .POST(BodyPublishers.ofString(");
        System.out.println("          \"{\\\"name\\\":\\\"Kim\\\"}\"))");
        System.out.println("      .build();");
        System.out.println();

        // ─── 종합 정리 ──────────────────────────────────
        System.out.println("── 종합: 네트워킹 핵심 정리 ────────────────────");
        System.out.println("  ┌──────────────────────────────────────────────┐");
        System.out.println("  │  네트워킹 핵심                              │");
        System.out.println("  ├──────────────────────────────────────────────┤");
        System.out.println("  │  1. HTTP는 요청-응답 기반의 프로토콜        │");
        System.out.println("  │  2. REST는 URL(자원) + 메서드(동작)         │");
        System.out.println("  │  3. 상태 코드로 결과를 알 수 있음           │");
        System.out.println("  │  4. JSON이 데이터 교환의 표준               │");
        System.out.println("  │  5. Socket은 저수준, HttpClient는 고수준    │");
        System.out.println("  │  6. Spring Boot가 서버 개발의 표준!         │");
        System.out.println("  └──────────────────────────────────────────────┘");
        System.out.println();

        System.out.println("■■■ 15단계 학습 완료! ■■■");
    }
}
