/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Go 학습 09단계: 패키지와 모듈
  ─ 패키지 구조 · 공개/비공개 · go mod · init() · 내부 패키지 시뮬레이션 ─

  [학습 목표]
  1. 패키지의 역할과 구조를 안다
  2. 대문자/소문자로 공개(exported)/비공개(unexported) 구분을 안다
  3. go mod init, go mod tidy의 역할을 안다
  4. init() 함수의 실행 시점을 안다
  5. 패키지 설계 원칙을 안다

  ■ 실행: go run main.go
  ■ 빌드: go build -o 09_packages main.go

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

package main

import (
	"fmt"
	"math"
	"strings"
)

func main() {
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println("  Go 09단계 : 패키지와 모듈")
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println()

	lesson1PackageBasics()
	lesson2ExportedVsUnexported()
	lesson3GoModules()
	lesson4InitFunction()
	lesson5PackageDesign()
	lesson6InternalPackageSimulation()
	lesson7ImportPatterns()
	lesson8PackageOrganization()

	fmt.Println("09단계 학습 완료!")
}

// =====================================================================
// 레슨 1 — 패키지 기초: 코드를 서랍에 나눠 담기
// =====================================================================
func lesson1PackageBasics() {
	fmt.Println("[레슨 1] 패키지: 관련 코드를 한 서랍에 모으기")
	fmt.Println()

	/*
	   ★ 패키지 = 같은 폴더에 있는 .go 파일들의 묶음

	   비유: 학교에서 "수학 프린트"는 수학 서랍에,
	         "영어 프린트"는 영어 서랍에 넣는 것!

	   ┌──────────────────────────────────────────────┐
	   │  프로젝트 구조 예시                            │
	   ├──────────────────────────────────────────────┤
	   │  myapp/                                      │
	   │  ├── go.mod         ← 모듈 정의               │
	   │  ├── main.go        ← package main           │
	   │  ├── student/                                │
	   │  │   ├── student.go ← package student        │
	   │  │   └── grade.go   ← package student (같음!) │
	   │  └── report/                                 │
	   │      └── report.go  ← package report         │
	   └──────────────────────────────────────────────┘

	   ★ 규칙:
	   1. 한 폴더 = 하나의 패키지 (같은 폴더의 모든 .go는 같은 package 선언)
	   2. package main 은 실행 가능한 프로그램 (main() 함수 포함)
	   3. 그 외 패키지는 라이브러리 (다른 코드가 import해서 사용)
	*/

	// 표준 라이브러리 패키지 사용 예시
	fmt.Println("  math.Pi =", math.Pi)
	fmt.Println("  strings.ToUpper(\"hello\") =", strings.ToUpper("hello"))

	fmt.Println()
}

// =====================================================================
// 레슨 2 — 공개(Exported) vs 비공개(Unexported)
// =====================================================================

// Student — 대문자 시작 → 다른 패키지에서 접근 가능 (공개)
type Student struct {
	Name  string // 대문자 → 공개
	Score int    // 대문자 → 공개
	memo  string // 소문자 → 비공개! (같은 패키지에서만 접근)
}

// GradeLabel — 대문자 시작 → 공개 함수
func GradeLabel(score int) string {
	if score >= 90 {
		return "우수"
	}
	if score >= 70 {
		return "통과"
	}
	return "복습 필요"
}

// helperFormat — 소문자 시작 → 비공개 (같은 패키지에서만 사용)
func helperFormat(name string) string {
	return fmt.Sprintf("[%s]", name)
}

func lesson2ExportedVsUnexported() {
	fmt.Println("[레슨 2] 대문자 = 공개, 소문자 = 비공개")
	fmt.Println()

	/*
	   ★ Go의 접근 제어는 '대소문자' 하나로 결정!

	   ┌──────────────────────────────────────────────┐
	   │  대문자 시작     │  공개(Exported)              │
	   │  Student        │  → 다른 패키지에서 접근 가능   │
	   │  GradeLabel()   │                              │
	   ├──────────────────────────────────────────────┤
	   │  소문자 시작     │  비공개(Unexported)           │
	   │  memo           │  → 같은 패키지에서만 접근 가능  │
	   │  helperFormat() │                              │
	   └──────────────────────────────────────────────┘

	   ★ Java의 public/private 키워드가 필요 없다!
	   ★ 타입, 함수, 변수, 상수, 메서드, 필드 모두 같은 규칙!
	*/

	s := Student{Name: "민수", Score: 85, memo: "내부 메모"}
	fmt.Println("  이름(공개):", s.Name)
	fmt.Println("  메모(비공개):", s.memo) // 같은 패키지라 접근 가능
	fmt.Println("  등급:", GradeLabel(s.Score))
	fmt.Println("  헬퍼:", helperFormat(s.Name))

	fmt.Println()
}

// =====================================================================
// 레슨 3 — Go 모듈 (go.mod)
// =====================================================================
func lesson3GoModules() {
	fmt.Println("[레슨 3] Go 모듈: go.mod로 의존성 관리")
	fmt.Println()

	/*
	   ★ go.mod = 이 프로젝트가 어떤 Go 버전을 쓰고,
	              어떤 외부 패키지에 의존하는지 기록한 파일

	   ┌──────────────────────────────────────────────┐
	   │  주요 명령어                                   │
	   ├──────────────────────────────────────────────┤
	   │  go mod init 모듈이름                         │
	   │  → go.mod 파일 생성, 모듈 이름 설정             │
	   │  → 보통: go mod init github.com/user/project  │
	   │                                              │
	   │  go mod tidy                                  │
	   │  → 사용하지 않는 의존성 제거, 필요한 것 추가     │
	   │  → 프로젝트 정리할 때 습관적으로 실행!           │
	   │                                              │
	   │  go get 패키지@버전                            │
	   │  → 외부 패키지 다운로드 및 go.mod에 추가         │
	   │                                              │
	   │  go mod vendor                                │
	   │  → 의존성을 vendor/ 폴더에 복사 (오프라인 빌드)  │
	   └──────────────────────────────────────────────┘
	*/

	fmt.Println("  go.mod 예시:")
	fmt.Println("  ──────────────────────────────────")
	fmt.Println("  module github.com/student/myapp")
	fmt.Println("")
	fmt.Println("  go 1.21")
	fmt.Println("")
	fmt.Println("  require (")
	fmt.Println("      github.com/gin-gonic/gin v1.9.1")
	fmt.Println("      github.com/lib/pq v1.10.9")
	fmt.Println("  )")
	fmt.Println("  ──────────────────────────────────")

	fmt.Println()
}

// =====================================================================
// 레슨 4 — init() 함수
// =====================================================================

/*
   ★ init() 함수 = 패키지가 import될 때 자동으로 실행되는 함수

   실행 순서:
   1. 패키지 수준 변수 초기화
   2. init() 함수 실행
   3. main() 함수 실행 (package main일 때)

   ★ 한 파일에 여러 개의 init()을 쓸 수 있다! (하지만 비추)
   ★ init()은 인자도 반환값도 없다
*/

var appName string
var maxRetry int

func init() {
	// 이 함수는 main()보다 먼저 실행된다!
	appName = "학생 관리 시스템"
	maxRetry = 3
}

func lesson4InitFunction() {
	fmt.Println("[레슨 4] init() 함수: main보다 먼저 실행!")
	fmt.Println()

	fmt.Println("  앱 이름:", appName)  // init에서 설정됨
	fmt.Println("  최대 재시도:", maxRetry)

	/*
	   ★ init()의 주요 용도:
	   1. 설정값 초기화
	   2. 데이터베이스 드라이버 등록
	   3. 환경 검증

	   ★ init() 남용 주의!
	   - init에서 무거운 작업을 하면 프로그램 시작이 느려진다
	   - init에서 에러가 나면 복구가 어렵다 (error를 반환할 수 없으므로)
	   - 가능하면 명시적 초기화 함수를 쓰는 것이 더 좋다

	   ┌────────────────────────────────────────────┐
	   │  나쁜 예: init() { db = connectDB() }       │
	   │  좋은 예: func SetupDB() (*DB, error) {...}  │
	   └────────────────────────────────────────────┘
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 5 — 패키지 설계 원칙
// =====================================================================
func lesson5PackageDesign() {
	fmt.Println("[레슨 5] 좋은 패키지 설계 원칙")
	fmt.Println()

	/*
	   ┌───────────────────────────────────────────────────────────┐
	   │  원칙 1: 패키지 이름은 짧고 명확하게                        │
	   │  ───────────────────────────────                          │
	   │  ○ net, http, fmt, io, os                                │
	   │  × utilities, helpers, common, misc  ← 너무 모호!        │
	   │                                                          │
	   │  원칙 2: 패키지 이름과 내용이 일치해야 한다                   │
	   │  ───────────────────────────────                          │
	   │  student 패키지에 날씨 함수가 있으면 안 된다!                │
	   │                                                          │
	   │  원칙 3: 패키지 이름을 함수 이름에 반복하지 않는다            │
	   │  ───────────────────────────────                          │
	   │  ○ student.New()       → student.New()                   │
	   │  × student.NewStudent() → student.NewStudent() (반복!)    │
	   │                                                          │
	   │  원칙 4: 순환 import 금지!                                 │
	   │  ───────────────────────────────                          │
	   │  A가 B를 import하고 B가 A를 import하면 컴파일 에러!         │
	   │  → 인터페이스나 공통 패키지로 해결                           │
	   │                                                          │
	   │  원칙 5: 가능하면 적게 공개(export)하라                      │
	   │  ───────────────────────────────                          │
	   │  내부 구현은 소문자로 숨기고, 필요한 것만 대문자로 공개        │
	   └───────────────────────────────────────────────────────────┘
	*/

	fmt.Println("  1. 패키지 이름: 짧고 명확하게 (net, http, io)")
	fmt.Println("  2. 이름과 내용이 일치해야 한다")
	fmt.Println("  3. 패키지 이름을 함수에 반복하지 않는다")
	fmt.Println("  4. 순환 import 금지!")
	fmt.Println("  5. 가능하면 적게 공개하라")

	fmt.Println()
}

// =====================================================================
// 레슨 6 — 내부 패키지 시뮬레이션
// =====================================================================

// ── 가상의 "mathutil" 패키지 ──

// Average — 공개 함수 (대문자 시작)
func Average(scores []int) float64 {
	if len(scores) == 0 {
		return 0
	}
	total := sumAll(scores) // 비공개 헬퍼 사용
	return float64(total) / float64(len(scores))
}

// Max — 공개 함수
func Max(scores []int) int {
	if len(scores) == 0 {
		return 0
	}
	m := scores[0]
	for _, s := range scores[1:] {
		if s > m {
			m = s
		}
	}
	return m
}

// sumAll — 비공개 헬퍼 (소문자 시작)
func sumAll(nums []int) int {
	total := 0
	for _, n := range nums {
		total += n
	}
	return total
}

func lesson6InternalPackageSimulation() {
	fmt.Println("[레슨 6] 패키지 시뮬레이션: 공개/비공개 역할 분리")
	fmt.Println()

	scores := []int{85, 92, 78, 96, 88}
	fmt.Println("  점수:", scores)
	fmt.Printf("  Average (공개): %.1f\n", Average(scores))
	fmt.Printf("  Max (공개): %d\n", Max(scores))
	fmt.Printf("  sumAll (비공개): %d (같은 패키지라 접근 가능)\n", sumAll(scores))

	/*
	   다른 패키지에서는:
	   mathutil.Average(scores)  ← OK (대문자)
	   mathutil.sumAll(scores)   ← 컴파일 에러! (소문자)
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 7 — import 패턴들
// =====================================================================
func lesson7ImportPatterns() {
	fmt.Println("[레슨 7] import 다양한 패턴")
	fmt.Println()

	/*
	   ┌────────────────────────────────────────────────────────────┐
	   │  패턴 1: 기본 import                                       │
	   │  import "fmt"                                              │
	   │  → fmt.Println()                                           │
	   │                                                            │
	   │  패턴 2: 그룹 import                                       │
	   │  import (                                                  │
	   │      "fmt"                                                 │
	   │      "os"                                                  │
	   │  )                                                         │
	   │                                                            │
	   │  패턴 3: 별칭 import                                       │
	   │  import f "fmt"                                            │
	   │  → f.Println()                                             │
	   │                                                            │
	   │  패턴 4: 점(dot) import (비추!)                             │
	   │  import . "fmt"                                            │
	   │  → Println()  (패키지 이름 생략 — 혼란 유발!)               │
	   │                                                            │
	   │  패턴 5: 빈칸(blank) import — 사이드 이펙트만 실행           │
	   │  import _ "github.com/lib/pq"                              │
	   │  → pq 패키지의 init()만 실행 (DB 드라이버 등록 등)           │
	   │                                                            │
	   │  ★ import 순서 관례:                                       │
	   │  1. 표준 라이브러리                                         │
	   │  2. 외부 패키지                                             │
	   │  3. 내부 패키지                                             │
	   │  (goimports 도구가 자동 정렬해 준다)                         │
	   └────────────────────────────────────────────────────────────┘
	*/

	fmt.Println("  기본:    import \"fmt\"         → fmt.Println()")
	fmt.Println("  별칭:    import f \"fmt\"       → f.Println()")
	fmt.Println("  사이드:  import _ \"lib/pq\"    → init()만 실행")
	fmt.Println("  점:      import . \"fmt\"       → Println() (비추!)")

	fmt.Println()
}

// =====================================================================
// 레슨 8 — 프로젝트 구조 권장 패턴
// =====================================================================
func lesson8PackageOrganization() {
	fmt.Println("[레슨 8] 프로젝트 구조 권장 패턴")
	fmt.Println()

	/*
	   ★ 작은 프로젝트 (처음 시작할 때):
	   ┌──────────────────────────┐
	   │  myapp/                  │
	   │  ├── go.mod              │
	   │  ├── main.go             │
	   │  └── helpers.go          │
	   └──────────────────────────┘

	   ★ 중간 프로젝트:
	   ┌──────────────────────────┐
	   │  myapp/                  │
	   │  ├── go.mod              │
	   │  ├── main.go             │
	   │  ├── student/            │
	   │  │   ├── student.go      │
	   │  │   └── student_test.go │
	   │  └── report/             │
	   │      ├── report.go       │
	   │      └── report_test.go  │
	   └──────────────────────────┘

	   ★ 큰 프로젝트 (표준 레이아웃):
	   ┌──────────────────────────┐
	   │  myapp/                  │
	   │  ├── cmd/                │
	   │  │   └── server/         │
	   │  │       └── main.go     │
	   │  ├── internal/           │
	   │  │   ├── student/        │
	   │  │   └── report/         │
	   │  ├── pkg/                │
	   │  │   └── mathutil/       │
	   │  ├── go.mod              │
	   │  └── go.sum              │
	   └──────────────────────────┘

	   ★ 핵심 폴더 설명:
	   cmd/       → 실행 가능한 바이너리들 (여러 개 가능)
	   internal/  → 외부에서 import 불가! (Go가 강제)
	   pkg/       → 외부에서 import 가능한 라이브러리
	*/

	fmt.Println("  작은 프로젝트: 한 폴더에 main.go와 헬퍼")
	fmt.Println("  중간 프로젝트: 기능별 패키지 분리")
	fmt.Println("  큰 프로젝트: cmd/ + internal/ + pkg/ 구조")
	fmt.Println("  ★ internal/ 폴더는 Go가 외부 import를 강제로 막아준다!")

	fmt.Println()
}
