/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C# 학습 15단계: 네트워킹
  ─ HTTP 개념, REST API, HttpClient, 요청/응답, 상태 코드, 라우팅 ─

  ■ 컴파일: dotnet build
  ■ 실행:   dotnet run

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  [학습 목표]
  1. HTTP 프로토콜의 기본 개념을 이해한다
  2. REST API의 설계 원칙을 안다
  3. HTTP 메서드(GET, POST, PUT, DELETE)를 이해한다
  4. 상태 코드(200, 201, 400, 404, 500)의 의미를 안다
  5. 요청/응답 시뮬레이션으로 API 동작을 체험한다
  6. HttpClient 사용 패턴을 안다
  7. JSON API 설계의 기본을 익힌다

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json;

namespace Lesson15
{
    // =====================================================================
    // 데이터 모델
    // =====================================================================
    record Request(string Method, string Path, string Body, Dictionary<string, string>? Headers = null);
    record Response(int StatusCode, string StatusText, string Body);
    record Student(int Id, string Name, int Score);

    // =====================================================================
    // 레슨 1 — HTTP 프로토콜 기초
    // =====================================================================
    /*
    ★ HTTP = HyperText Transfer Protocol
      → 웹에서 클라이언트와 서버가 대화하는 규칙

    ★ 비유: 식당 주문 시스템
      클라이언트(손님) → 요청(Request) → 서버(주방)
      서버(주방) → 응답(Response) → 클라이언트(손님)

    ★ HTTP 요청 구조
    ┌──────────────────────────────────────────────────┐
    │  GET /api/students/1 HTTP/1.1                    │
    │  Host: school.example.com                        │
    │  Accept: application/json                        │
    │  Authorization: Bearer eyJhbG...                 │
    │                                                  │
    │  (본문 — POST/PUT에서 사용)                      │
    └──────────────────────────────────────────────────┘

    ★ HTTP 메서드
    ┌──────────┬─────────────────────────────────────────┐
    │  GET     │ 데이터 조회 (읽기만, 부작용 없음)      │
    │  POST    │ 데이터 생성 (새로 만들기)              │
    │  PUT     │ 데이터 전체 수정 (교체)                │
    │  PATCH   │ 데이터 부분 수정                       │
    │  DELETE  │ 데이터 삭제                            │
    └──────────┴─────────────────────────────────────────┘

    ★ HTTP 상태 코드
    ┌──────────┬─────────────────────────────────────────┐
    │  2xx     │ 성공                                   │
    │  200 OK  │ 요청 성공                              │
    │  201     │ Created — 생성 성공                    │
    │  204     │ No Content — 성공, 응답 본문 없음      │
    ├──────────┼─────────────────────────────────────────┤
    │  4xx     │ 클라이언트 오류 (요청이 잘못됨)        │
    │  400     │ Bad Request — 잘못된 요청              │
    │  401     │ Unauthorized — 인증 필요               │
    │  403     │ Forbidden — 권한 없음                  │
    │  404     │ Not Found — 리소스 없음                │
    │  409     │ Conflict — 충돌                        │
    ├──────────┼─────────────────────────────────────────┤
    │  5xx     │ 서버 오류                              │
    │  500     │ Internal Server Error — 서버 버그      │
    │  503     │ Service Unavailable — 서버 과부하      │
    └──────────┴─────────────────────────────────────────┘
    */


    // =====================================================================
    // 레슨 2 — REST API 설계 원칙
    // =====================================================================
    /*
    ★ REST = Representational State Transfer
      → 리소스(자원)를 URL로 표현하고, HTTP 메서드로 조작

    ★ RESTful URL 설계
    ┌──────────────────────────────────────────────────────────┐
    │ GET    /api/students          전체 학생 목록 조회       │
    │ GET    /api/students/1        1번 학생 조회             │
    │ POST   /api/students          새 학생 생성              │
    │ PUT    /api/students/1        1번 학생 수정             │
    │ DELETE /api/students/1        1번 학생 삭제             │
    │                                                          │
    │ GET    /api/students/1/scores 1번 학생의 점수 목록      │
    └──────────────────────────────────────────────────────────┘

    ★ 좋은 URL vs 나쁜 URL
      ✗ /getStudentList         (동사 사용)
      ✗ /api/student/delete/1   (동사+동작)
      ✓ /api/students           (복수 명사)
      ✓ DELETE /api/students/1  (HTTP 메서드로 동작 표현)
    */


    // =====================================================================
    // 미니 API 서버 시뮬레이션
    // =====================================================================
    class MiniApiServer
    {
        private readonly List<Student> students;
        private int nextId;

        public MiniApiServer()
        {
            students = new List<Student>
            {
                new Student(1, "민수", 82),
                new Student(2, "지우", 95),
                new Student(3, "서연", 68),
            };
            nextId = 4;
        }

        public Response HandleRequest(Request request)
        {
            // ── GET /api/students — 전체 목록 ──
            if (request.Method == "GET" && request.Path == "/api/students")
            {
                string json = JsonSerializer.Serialize(students);
                return new Response(200, "OK", json);
            }

            // ── GET /api/students/{id} — 개별 조회 ──
            if (request.Method == "GET" && request.Path.StartsWith("/api/students/"))
            {
                string idText = request.Path.Replace("/api/students/", "");
                if (!int.TryParse(idText, out int id))
                {
                    return new Response(400, "Bad Request", "ID는 숫자여야 합니다.");
                }

                Student? found = students.FirstOrDefault(s => s.Id == id);
                if (found == null)
                {
                    return new Response(404, "Not Found", $"ID={id} 학생을 찾을 수 없습니다.");
                }

                string json = JsonSerializer.Serialize(found);
                return new Response(200, "OK", json);
            }

            // ── POST /api/students — 새 학생 생성 ──
            if (request.Method == "POST" && request.Path == "/api/students")
            {
                if (string.IsNullOrWhiteSpace(request.Body))
                {
                    return new Response(400, "Bad Request", "요청 본문이 비어있습니다.");
                }

                try
                {
                    var dto = JsonSerializer.Deserialize<StudentCreateDto>(request.Body);
                    if (dto == null || string.IsNullOrWhiteSpace(dto.Name))
                    {
                        return new Response(400, "Bad Request", "이름은 필수입니다.");
                    }

                    var newStudent = new Student(nextId++, dto.Name, dto.Score);
                    students.Add(newStudent);

                    string json = JsonSerializer.Serialize(newStudent);
                    return new Response(201, "Created", json);
                }
                catch (JsonException)
                {
                    return new Response(400, "Bad Request", "잘못된 JSON 형식입니다.");
                }
            }

            // ── DELETE /api/students/{id} — 삭제 ──
            if (request.Method == "DELETE" && request.Path.StartsWith("/api/students/"))
            {
                string idText = request.Path.Replace("/api/students/", "");
                if (!int.TryParse(idText, out int id))
                {
                    return new Response(400, "Bad Request", "ID는 숫자여야 합니다.");
                }

                Student? found = students.FirstOrDefault(s => s.Id == id);
                if (found == null)
                {
                    return new Response(404, "Not Found", $"ID={id} 학생 없음");
                }

                students.Remove(found);
                return new Response(204, "No Content", "");
            }

            // ── 매칭 안 됨 ──
            return new Response(404, "Not Found", $"경로를 찾을 수 없습니다: {request.Method} {request.Path}");
        }
    }

    // POST용 DTO
    class StudentCreateDto
    {
        public string Name { get; set; } = "";
        public int Score { get; set; }
    }


    // =====================================================================
    // Main
    // =====================================================================
    class Program
    {
        static void PrintResponse(Request req, Response res)
        {
            Console.WriteLine($"    {req.Method} {req.Path}");
            Console.WriteLine($"    → {res.StatusCode} {res.StatusText}");
            if (!string.IsNullOrEmpty(res.Body))
            {
                // JSON 예쁘게 출력 시도
                try
                {
                    var doc = JsonDocument.Parse(res.Body);
                    string pretty = JsonSerializer.Serialize(doc, new JsonSerializerOptions { WriteIndented = true });
                    foreach (string line in pretty.Split('\n'))
                    {
                        Console.WriteLine($"      {line.TrimEnd()}");
                    }
                }
                catch
                {
                    Console.WriteLine($"      {res.Body}");
                }
            }
            Console.WriteLine();
        }

        static void Lesson1HttpBasics()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 1: HTTP 기초 — 요청과 응답");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            Console.WriteLine("  ★ HTTP = 클라이언트와 서버의 대화 규칙");
            Console.WriteLine();
            Console.WriteLine("  ┌──────────┐      요청(Request)      ┌──────────┐");
            Console.WriteLine("  │          │ ──────────────────────→ │          │");
            Console.WriteLine("  │ 클라이언트│                         │   서버   │");
            Console.WriteLine("  │ (브라우저)│ ←────────────────────── │ (API)    │");
            Console.WriteLine("  │          │      응답(Response)     │          │");
            Console.WriteLine("  └──────────┘                         └──────────┘");
            Console.WriteLine();

            Console.WriteLine("  요청(Request) 구성요소:");
            Console.WriteLine("    1. 메서드: GET, POST, PUT, DELETE");
            Console.WriteLine("    2. URL/경로: /api/students/1");
            Console.WriteLine("    3. 헤더: Content-Type, Authorization");
            Console.WriteLine("    4. 본문: JSON 데이터 (POST/PUT)");
            Console.WriteLine();

            Console.WriteLine("  응답(Response) 구성요소:");
            Console.WriteLine("    1. 상태 코드: 200, 404, 500");
            Console.WriteLine("    2. 헤더: Content-Type, Cache-Control");
            Console.WriteLine("    3. 본문: JSON 데이터");
            Console.WriteLine();
        }

        static void Lesson2RestApiDesign()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 2: REST API 설계 원칙");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            Console.WriteLine("  ★ RESTful URL 설계 규칙:");
            Console.WriteLine("    1. 리소스는 명사로 (동사 금지!)");
            Console.WriteLine("    2. 복수형 사용: /students (O), /student (X)");
            Console.WriteLine("    3. 계층 관계: /students/1/scores");
            Console.WriteLine("    4. 소문자 사용: /api/students (O)");
            Console.WriteLine("    5. 하이픈 사용: /course-reviews (O)");
            Console.WriteLine();

            Console.WriteLine("  ★ CRUD와 HTTP 메서드 매핑:");
            Console.WriteLine("  ┌──────────┬──────────┬──────────────────────────┐");
            Console.WriteLine("  │ CRUD     │ HTTP     │ URL 예시                 │");
            Console.WriteLine("  ├──────────┼──────────┼──────────────────────────┤");
            Console.WriteLine("  │ Create   │ POST     │ POST /api/students       │");
            Console.WriteLine("  │ Read     │ GET      │ GET  /api/students/1     │");
            Console.WriteLine("  │ Update   │ PUT      │ PUT  /api/students/1     │");
            Console.WriteLine("  │ Delete   │ DELETE   │ DELETE /api/students/1   │");
            Console.WriteLine("  └──────────┴──────────┴──────────────────────────┘");
            Console.WriteLine();
        }

        static void Lesson3ApiSimulation()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 3: API 시뮬레이션 — CRUD 체험");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            var server = new MiniApiServer();

            // ── GET: 전체 목록 ──
            Console.WriteLine("  [1. 전체 학생 목록 조회]");
            var req1 = new Request("GET", "/api/students", "");
            PrintResponse(req1, server.HandleRequest(req1));

            // ── GET: 개별 조회 ──
            Console.WriteLine("  [2. 특정 학생 조회]");
            var req2 = new Request("GET", "/api/students/2", "");
            PrintResponse(req2, server.HandleRequest(req2));

            // ── GET: 없는 학생 ──
            Console.WriteLine("  [3. 없는 학생 조회 → 404]");
            var req3 = new Request("GET", "/api/students/999", "");
            PrintResponse(req3, server.HandleRequest(req3));

            // ── POST: 학생 생성 ──
            Console.WriteLine("  [4. 새 학생 생성]");
            string newStudentJson = JsonSerializer.Serialize(new StudentCreateDto { Name = "하린", Score = 91 });
            var req4 = new Request("POST", "/api/students", newStudentJson);
            PrintResponse(req4, server.HandleRequest(req4));

            // ── POST: 잘못된 요청 ──
            Console.WriteLine("  [5. 잘못된 JSON → 400]");
            var req5 = new Request("POST", "/api/students", "잘못된 데이터");
            PrintResponse(req5, server.HandleRequest(req5));

            // ── DELETE: 학생 삭제 ──
            Console.WriteLine("  [6. 학생 삭제]");
            var req6 = new Request("DELETE", "/api/students/1", "");
            PrintResponse(req6, server.HandleRequest(req6));

            // ── 삭제 후 목록 확인 ──
            Console.WriteLine("  [7. 삭제 후 목록 확인]");
            PrintResponse(req1, server.HandleRequest(req1));
        }

        static void Lesson4HttpClientPattern()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 4: HttpClient — 실제 HTTP 호출 패턴");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            /*
            ★ HttpClient 사용 규칙
              1. HttpClient는 재사용! (매번 new 하지 말 것)
              2. IHttpClientFactory 또는 static으로 관리
              3. 비동기 메서드 사용 (GetAsync, PostAsync)
            */

            Console.WriteLine("  ★ HttpClient 기본 사용법:");
            Console.WriteLine();
            Console.WriteLine("    // ✗ 나쁜 예: 매번 새로 만들면 소켓 고갈!");
            Console.WriteLine("    using var client = new HttpClient();");
            Console.WriteLine();
            Console.WriteLine("    // ✓ 좋은 예: 정적 필드로 재사용");
            Console.WriteLine("    private static readonly HttpClient client = new();");
            Console.WriteLine();
            Console.WriteLine("    // ✓ 가장 좋은 예: DI + IHttpClientFactory");
            Console.WriteLine("    services.AddHttpClient<MyService>();");
            Console.WriteLine();

            Console.WriteLine("  ★ GET 요청 코드:");
            Console.WriteLine("    var response = await client.GetAsync(\"https://api.example.com/data\");");
            Console.WriteLine("    response.EnsureSuccessStatusCode();");
            Console.WriteLine("    string json = await response.Content.ReadAsStringAsync();");
            Console.WriteLine("    var data = JsonSerializer.Deserialize<MyData>(json);");
            Console.WriteLine();

            Console.WriteLine("  ★ POST 요청 코드:");
            Console.WriteLine("    var content = new StringContent(json, Encoding.UTF8, \"application/json\");");
            Console.WriteLine("    var response = await client.PostAsync(url, content);");
            Console.WriteLine();

            Console.WriteLine("  ★ 타임아웃 설정:");
            Console.WriteLine("    client.Timeout = TimeSpan.FromSeconds(30);");
            Console.WriteLine();
        }

        static void Lesson5StatusCodeMeaning()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 5: 상태 코드 — 의미와 적절한 사용");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            var scenarios = new (int Code, string Status, string Scenario)[]
            {
                (200, "OK", "학생 목록 조회 성공"),
                (201, "Created", "새 학생 등록 성공"),
                (204, "No Content", "학생 삭제 성공 (본문 없음)"),
                (400, "Bad Request", "점수에 문자열을 넣음"),
                (401, "Unauthorized", "로그인 안 한 상태로 접근"),
                (403, "Forbidden", "학생이 관리자 페이지 접근"),
                (404, "Not Found", "존재하지 않는 학생 ID 요청"),
                (409, "Conflict", "이미 같은 학번이 존재"),
                (500, "Server Error", "서버 코드에 버그 (null 참조 등)"),
                (503, "Unavailable", "서버 점검 중"),
            };

            Console.WriteLine("  ┌──────┬──────────────────┬────────────────────────────────┐");
            Console.WriteLine("  │ 코드 │ 상태             │ 상황 예시                      │");
            Console.WriteLine("  ├──────┼──────────────────┼────────────────────────────────┤");
            foreach (var (code, status, scenario) in scenarios)
            {
                Console.WriteLine($"  │ {code}  │ {status,-16} │ {scenario,-28} │");
            }
            Console.WriteLine("  └──────┴──────────────────┴────────────────────────────────┘");
            Console.WriteLine();

            Console.WriteLine("  ★ 구분법:");
            Console.WriteLine("    2xx = 성공 → 클라이언트가 올바르게 요청");
            Console.WriteLine("    4xx = 클라이언트 잘못 → 요청을 고쳐야 함");
            Console.WriteLine("    5xx = 서버 잘못 → 서버 코드를 고쳐야 함");
            Console.WriteLine();
        }

        static void Lesson6CommonMistakes()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 6: 흔한 실수와 모범 사례");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            Console.WriteLine("  ┌──────────────────────────────────────────────────┐");
            Console.WriteLine("  │ ★ 네트워킹 흔한 실수                           │");
            Console.WriteLine("  ├──────────────────────────────────────────────────┤");
            Console.WriteLine("  │ 1. GET으로 데이터 삭제 → DELETE 사용!          │");
            Console.WriteLine("  │ 2. 모든 에러에 200 반환 → 적절한 상태 코드!    │");
            Console.WriteLine("  │ 3. URL에 동사 사용 → 명사 + HTTP 메서드!       │");
            Console.WriteLine("  │ 4. 에러 메시지에 내부 정보 노출 → 일반 메시지! │");
            Console.WriteLine("  │ 5. 타임아웃 설정 안 함 → 반드시 설정!          │");
            Console.WriteLine("  │ 6. 재시도 로직 없음 → Polly 등 활용!           │");
            Console.WriteLine("  │ 7. HTTPS 안 쓰기 → 반드시 HTTPS!              │");
            Console.WriteLine("  └──────────────────────────────────────────────────┘");
            Console.WriteLine();

            Console.WriteLine("  ★ ASP.NET Core로 실제 API 만들기:");
            Console.WriteLine("    dotnet new webapi -n MyApi");
            Console.WriteLine("    → Controllers/, Program.cs 자동 생성");
            Console.WriteLine("    → Swagger UI로 API 테스트 가능!");
            Console.WriteLine();
        }

        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine("  C# 15단계: 네트워킹");
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine();

            Lesson1HttpBasics();
            Lesson2RestApiDesign();
            Lesson3ApiSimulation();
            Lesson4HttpClientPattern();
            Lesson5StatusCodeMeaning();
            Lesson6CommonMistakes();

            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  ★ 정리");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  1. HTTP: 클라이언트-서버 대화 규칙");
            Console.WriteLine("  2. REST: 리소스 중심 URL + HTTP 메서드");
            Console.WriteLine("  3. GET/POST/PUT/DELETE: CRUD 매핑");
            Console.WriteLine("  4. 상태 코드: 2xx 성공, 4xx 클라이언트 오류, 5xx 서버 오류");
            Console.WriteLine("  5. HttpClient: 재사용, IHttpClientFactory 권장");
            Console.WriteLine("  6. ASP.NET Core: 실제 API 서버 구축 프레임워크");
            Console.WriteLine();
        }
    }
}
