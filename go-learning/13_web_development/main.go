/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Go 학습 13단계: HTTP와 웹 개발
  ─ net/http · 핸들러 · 미들웨어 · ServeMux · JSON API · 라우팅 ─

  [학습 목표]
  1. net/http로 HTTP 서버의 구조를 이해한다
  2. 핸들러(Handler)와 핸들러 함수를 안다
  3. JSON API의 요청/응답 패턴을 안다
  4. 미들웨어 패턴을 이해한다
  5. HTTP 클라이언트 사용법을 안다

  ■ 실행: go run main.go
  ■ 빌드: go build -o 13_web main.go

  ★ 이 파일은 실제 서버를 띄우지 않고 구조를 시뮬레이션합니다.

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

package main

import (
	"encoding/json"
	"fmt"
	"strconv"
)

func main() {
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println("  Go 13단계 : HTTP와 웹 개발")
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println()

	lesson1HTTPBasics()
	lesson2HandlerPattern()
	lesson3JSONApi()
	lesson4Router()
	lesson5Middleware()
	lesson6HTTPClient()
	lesson7ErrorResponse()
	lesson8ServerStructure()

	fmt.Println("13단계 학습 완료!")
}

// ── 시뮬레이션용 타입 ──

// Request — HTTP 요청 시뮬레이션
type Request struct {
	Method string
	Path   string
	Body   string
}

// Response — HTTP 응답 시뮬레이션
type Response struct {
	Status int
	Body   string
}

// Student — JSON API에서 사용할 구조체
type Student struct {
	ID    int    `json:"id"`
	Name  string `json:"name"`
	Score int    `json:"score"`
}

// =====================================================================
// 레슨 1 — HTTP 서버 기초
// =====================================================================
func lesson1HTTPBasics() {
	fmt.Println("[레슨 1] HTTP 서버: net/http 패키지로 웹 서버 만들기")
	fmt.Println()

	/*
	   ★ Go의 HTTP 서버는 표준 라이브러리만으로 충분하다!
	   (다른 언어처럼 프레임워크가 꼭 필요하지 않다)

	   ┌────────────────────────────────────────────────────┐
	   │  최소 HTTP 서버 (5줄!)                               │
	   ├────────────────────────────────────────────────────┤
	   │  package main                                      │
	   │                                                    │
	   │  import "net/http"                                  │
	   │                                                    │
	   │  func main() {                                     │
	   │      http.HandleFunc("/", func(w http.ResponseWriter, │
	   │          r *http.Request) {                         │
	   │          w.Write([]byte("안녕하세요!"))              │
	   │      })                                            │
	   │      http.ListenAndServe(":8080", nil)             │
	   │  }                                                 │
	   └────────────────────────────────────────────────────┘

	   ★ 핵심 개념:
	   http.Request        → 클라이언트가 보낸 요청 정보
	   http.ResponseWriter → 클라이언트에게 응답을 보내는 도구
	   http.ListenAndServe → 서버 시작! (포트 번호, 라우터)

	   ★ HTTP 메서드:
	   GET     → 데이터 조회 (읽기)
	   POST    → 데이터 생성 (쓰기)
	   PUT     → 데이터 전체 수정
	   PATCH   → 데이터 부분 수정
	   DELETE  → 데이터 삭제
	*/

	fmt.Println("  최소 서버: http.ListenAndServe(\":8080\", nil)")
	fmt.Println("  핸들러 등록: http.HandleFunc(\"/경로\", 함수)")
	fmt.Println()

	fmt.Println("  HTTP 메서드 정리:")
	fmt.Println("  GET    → 조회  POST   → 생성")
	fmt.Println("  PUT    → 수정  DELETE → 삭제")

	fmt.Println()
}

// =====================================================================
// 레슨 2 — 핸들러 패턴
// =====================================================================

/*
   ★ 핸들러 = 특정 URL에 대한 요청을 처리하는 함수

   방법 1: HandleFunc (함수)
   http.HandleFunc("/hello", helloHandler)

   방법 2: Handle (인터페이스)
   type Handler interface {
       ServeHTTP(w ResponseWriter, r *Request)
   }
*/

func handleHello(req Request) Response {
	return Response{Status: 200, Body: "안녕하세요! Go 웹 서버입니다."}
}

func handleStudents(req Request) Response {
	students := []Student{
		{ID: 1, Name: "민수", Score: 85},
		{ID: 2, Name: "지우", Score: 92},
	}
	data, _ := json.Marshal(students)
	return Response{Status: 200, Body: string(data)}
}

func lesson2HandlerPattern() {
	fmt.Println("[레슨 2] 핸들러: URL별로 처리 함수 연결하기")
	fmt.Println()

	// 시뮬레이션
	req1 := Request{Method: "GET", Path: "/hello"}
	resp1 := handleHello(req1)
	fmt.Printf("  %s %s → [%d] %s\n", req1.Method, req1.Path, resp1.Status, resp1.Body)

	req2 := Request{Method: "GET", Path: "/students"}
	resp2 := handleStudents(req2)
	fmt.Printf("  %s %s → [%d] %s\n", req2.Method, req2.Path, resp2.Status, resp2.Body)

	/*
	   ★ 실제 핸들러 구현 패턴:

	   func studentHandler(w http.ResponseWriter, r *http.Request) {
	       switch r.Method {
	       case http.MethodGet:
	           // 조회 로직
	       case http.MethodPost:
	           // 생성 로직
	       default:
	           http.Error(w, "Method Not Allowed", 405)
	       }
	   }
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 3 — JSON API
// =====================================================================

func handleCreateStudent(req Request) Response {
	// JSON 파싱
	var s Student
	err := json.Unmarshal([]byte(req.Body), &s)
	if err != nil {
		return Response{Status: 400, Body: `{"error":"잘못된 JSON"}`}
	}

	if s.Name == "" {
		return Response{Status: 400, Body: `{"error":"이름이 필요합니다"}`}
	}

	s.ID = 3 // 자동 ID 부여 시뮬레이션
	data, _ := json.Marshal(s)
	return Response{Status: 201, Body: string(data)}
}

func lesson3JSONApi() {
	fmt.Println("[레슨 3] JSON API: 요청/응답 모두 JSON으로")
	fmt.Println()

	/*
	   ★ JSON API 패턴:

	   요청 (클라이언트 → 서버):
	   Content-Type: application/json
	   {"name": "서연", "score": 88}

	   응답 (서버 → 클라이언트):
	   Content-Type: application/json
	   {"id": 3, "name": "서연", "score": 88}

	   ★ 실제 구현에서 중요한 것:
	   1. json.NewDecoder(r.Body).Decode(&student) — 요청 파싱
	   2. w.Header().Set("Content-Type", "application/json")
	   3. json.NewEncoder(w).Encode(student) — 응답 전송
	*/

	// 정상 요청
	req := Request{
		Method: "POST",
		Path:   "/students",
		Body:   `{"name":"서연","score":88}`,
	}
	resp := handleCreateStudent(req)
	fmt.Printf("  POST %s\n", req.Path)
	fmt.Printf("  요청: %s\n", req.Body)
	fmt.Printf("  응답: [%d] %s\n", resp.Status, resp.Body)
	fmt.Println()

	// 잘못된 요청
	badReq := Request{
		Method: "POST",
		Path:   "/students",
		Body:   `{"name":""}`,
	}
	badResp := handleCreateStudent(badReq)
	fmt.Printf("  잘못된 요청: [%d] %s\n", badResp.Status, badResp.Body)

	fmt.Println()
}

// =====================================================================
// 레슨 4 — 라우터 시뮬레이션
// =====================================================================

type Route struct {
	Method  string
	Path    string
	Handler func(Request) Response
}

type Router struct {
	routes []Route
}

func (rt *Router) Add(method, path string, handler func(Request) Response) {
	rt.routes = append(rt.routes, Route{method, path, handler})
}

func (rt *Router) Dispatch(req Request) Response {
	for _, route := range rt.routes {
		if route.Method == req.Method && route.Path == req.Path {
			return route.Handler(req)
		}
	}
	return Response{Status: 404, Body: `{"error":"Not Found"}`}
}

func lesson4Router() {
	fmt.Println("[레슨 4] 라우터: URL + 메서드 → 핸들러 연결")
	fmt.Println()

	/*
	   ★ Go 1.22+ 에서는 ServeMux가 메서드 패턴을 지원!

	   mux := http.NewServeMux()
	   mux.HandleFunc("GET /students", listHandler)
	   mux.HandleFunc("POST /students", createHandler)
	   mux.HandleFunc("GET /students/{id}", getHandler)

	   ★ 외부 라우터: gorilla/mux, chi, gin 등
	*/

	router := Router{}
	router.Add("GET", "/hello", handleHello)
	router.Add("GET", "/students", handleStudents)
	router.Add("POST", "/students", handleCreateStudent)

	// 시뮬레이션
	requests := []Request{
		{Method: "GET", Path: "/hello"},
		{Method: "GET", Path: "/students"},
		{Method: "POST", Path: "/students", Body: `{"name":"하준","score":91}`},
		{Method: "GET", Path: "/unknown"},
	}

	for _, req := range requests {
		resp := router.Dispatch(req)
		fmt.Printf("  %s %-15s → [%d] %s\n",
			req.Method, req.Path, resp.Status,
			truncate(resp.Body, 50))
	}

	fmt.Println()
}

func truncate(s string, max int) string {
	if len(s) > max {
		return s[:max] + "..."
	}
	return s
}

// =====================================================================
// 레슨 5 — 미들웨어 패턴
// =====================================================================

type HandlerFunc func(Request) Response
type Middleware func(HandlerFunc) HandlerFunc

// loggingMiddleware — 요청/응답 로깅
func loggingMiddleware(next HandlerFunc) HandlerFunc {
	return func(req Request) Response {
		fmt.Printf("    [LOG] → %s %s\n", req.Method, req.Path)
		resp := next(req)
		fmt.Printf("    [LOG] ← %d\n", resp.Status)
		return resp
	}
}

// authMiddleware — 인증 확인 (시뮬레이션)
func authMiddleware(next HandlerFunc) HandlerFunc {
	return func(req Request) Response {
		// 실제로는 Authorization 헤더를 확인
		if req.Path == "/admin" {
			return Response{Status: 401, Body: `{"error":"인증 필요"}`}
		}
		return next(req)
	}
}

func lesson5Middleware() {
	fmt.Println("[레슨 5] 미들웨어: 핸들러를 감싸는 레이어")
	fmt.Println()

	/*
	   ★ 미들웨어 = 핸들러 전/후에 공통 처리를 넣는 패턴

	   요청 → [로깅] → [인증] → [핸들러] → [로깅] → 응답
	            ↑                              ↑
	         미들웨어                        미들웨어

	   용도: 로깅, 인증, CORS, 에러 복구, 요청 시간 측정 등
	*/

	// 미들웨어 체이닝
	handler := loggingMiddleware(authMiddleware(handleHello))

	fmt.Println("  --- /hello 요청 (미들웨어 적용) ---")
	resp := handler(Request{Method: "GET", Path: "/hello"})
	fmt.Printf("  결과: [%d] %s\n", resp.Status, resp.Body)

	fmt.Println()
}

// =====================================================================
// 레슨 6 — HTTP 클라이언트
// =====================================================================
func lesson6HTTPClient() {
	fmt.Println("[레슨 6] HTTP 클라이언트: 다른 서버에 요청 보내기")
	fmt.Println()

	/*
	   ★ Go의 HTTP 클라이언트도 표준 라이브러리!

	   ┌──────────────────────────────────────────────────────┐
	   │  // 간단한 GET                                        │
	   │  resp, err := http.Get("https://api.example.com/data")│
	   │  if err != nil { /* 에러 처리 */ }                    │
	   │  defer resp.Body.Close()                              │
	   │  body, _ := io.ReadAll(resp.Body)                     │
	   │                                                      │
	   │  // 커스텀 요청                                       │
	   │  client := &http.Client{Timeout: 10 * time.Second}    │
	   │  req, _ := http.NewRequest("POST", url, body)         │
	   │  req.Header.Set("Content-Type", "application/json")   │
	   │  resp, err := client.Do(req)                          │
	   └──────────────────────────────────────────────────────┘

	   ★★★ 중요: resp.Body.Close()를 반드시 defer로 닫자! ★★★
	   안 닫으면 커넥션이 재사용되지 않아 리소스 누수!

	   ★ 기본 http.Get()은 타임아웃이 없다!
	   → 항상 &http.Client{Timeout: ...}을 사용하자
	*/

	fmt.Println("  간단: resp, err := http.Get(url)")
	fmt.Println("  커스텀: client := &http.Client{Timeout: 10*time.Second}")
	fmt.Println("  ★ defer resp.Body.Close() 필수!")
	fmt.Println("  ★ 기본 클라이언트는 타임아웃 없음 → 직접 설정!")

	fmt.Println()
}

// =====================================================================
// 레슨 7 — 에러 응답 패턴
// =====================================================================

type APIError struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

func handleWithValidation(req Request) Response {
	// 메서드 확인
	if req.Method != "POST" {
		errJSON, _ := json.Marshal(APIError{Code: 405, Message: "POST만 허용"})
		return Response{Status: 405, Body: string(errJSON)}
	}

	// 바디 파싱
	var s Student
	if err := json.Unmarshal([]byte(req.Body), &s); err != nil {
		errJSON, _ := json.Marshal(APIError{Code: 400, Message: "잘못된 JSON"})
		return Response{Status: 400, Body: string(errJSON)}
	}

	// 검증
	if s.Name == "" {
		errJSON, _ := json.Marshal(APIError{Code: 422, Message: "이름은 필수입니다"})
		return Response{Status: 422, Body: string(errJSON)}
	}

	if s.Score < 0 || s.Score > 100 {
		errJSON, _ := json.Marshal(APIError{
			Code:    422,
			Message: "점수는 0~100 범위입니다 (입력: " + strconv.Itoa(s.Score) + ")",
		})
		return Response{Status: 422, Body: string(errJSON)}
	}

	s.ID = 1
	data, _ := json.Marshal(s)
	return Response{Status: 201, Body: string(data)}
}

func lesson7ErrorResponse() {
	fmt.Println("[레슨 7] 에러 응답: 구조화된 JSON 에러")
	fmt.Println()

	/*
	   ★ API 에러 응답도 JSON으로 보내야 한다!

	   잘못된 예:  "에러가 발생했습니다"  (그냥 문자열)
	   올바른 예:  {"code": 422, "message": "이름은 필수입니다"}

	   ★ HTTP 상태 코드 정리:
	   ┌──────┬──────────────────────────┐
	   │ 200  │ OK (성공)                  │
	   │ 201  │ Created (생성 성공)         │
	   │ 400  │ Bad Request (잘못된 요청)   │
	   │ 401  │ Unauthorized (인증 필요)    │
	   │ 403  │ Forbidden (권한 없음)       │
	   │ 404  │ Not Found (없음)           │
	   │ 405  │ Method Not Allowed         │
	   │ 422  │ Unprocessable Entity (검증 실패) │
	   │ 500  │ Internal Server Error      │
	   └──────┴──────────────────────────┘
	*/

	testCases := []Request{
		{Method: "GET", Path: "/students", Body: ""},
		{Method: "POST", Path: "/students", Body: "not json"},
		{Method: "POST", Path: "/students", Body: `{"name":"","score":50}`},
		{Method: "POST", Path: "/students", Body: `{"name":"민수","score":150}`},
		{Method: "POST", Path: "/students", Body: `{"name":"민수","score":85}`},
	}

	for _, req := range testCases {
		resp := handleWithValidation(req)
		bodyPreview := truncate(req.Body, 30)
		if bodyPreview == "" {
			bodyPreview = "(empty)"
		}
		fmt.Printf("  %s %-20s → [%d] %s\n",
			req.Method, bodyPreview, resp.Status, resp.Body)
	}

	fmt.Println()
}

// =====================================================================
// 레슨 8 — 서버 구조 권장 패턴
// =====================================================================
func lesson8ServerStructure() {
	fmt.Println("[레슨 8] 웹 서버 프로젝트 구조")
	fmt.Println()

	/*
	   ┌────────────────────────────────────────────┐
	   │  myapi/                                    │
	   │  ├── cmd/                                  │
	   │  │   └── server/                           │
	   │  │       └── main.go        ← 서버 시작점   │
	   │  ├── internal/                             │
	   │  │   ├── handler/           ← HTTP 핸들러   │
	   │  │   │   ├── student.go                    │
	   │  │   │   └── health.go                     │
	   │  │   ├── service/           ← 비즈니스 로직  │
	   │  │   │   └── student.go                    │
	   │  │   ├── repository/        ← DB 접근       │
	   │  │   │   └── student.go                    │
	   │  │   ├── model/             ← 데이터 모델   │
	   │  │   │   └── student.go                    │
	   │  │   └── middleware/        ← 미들웨어      │
	   │  │       ├── logging.go                    │
	   │  │       └── auth.go                       │
	   │  ├── go.mod                                │
	   │  └── go.sum                                │
	   └────────────────────────────────────────────┘

	   ★ 계층 흐름:
	   요청 → Handler → Service → Repository → DB
	         (HTTP)    (로직)     (데이터)
	*/

	fmt.Println("  Handler: HTTP 요청/응답 처리 (JSON 파싱, 상태코드)")
	fmt.Println("  Service: 비즈니스 로직 (검증, 계산, 규칙)")
	fmt.Println("  Repository: 데이터 저장/조회 (DB 쿼리)")
	fmt.Println("  Model: 데이터 구조 정의 (구조체)")
	fmt.Println()

	fmt.Println()
}
