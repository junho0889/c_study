/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Go 학습 12단계: 테스팅
  ─ testing 패키지 · 테이블 테스트 · 서브테스트 · 벤치마크 · 커버리지 ─

  [학습 목표]
  1. Go의 testing 패키지 규칙을 안다
  2. 테이블 주도 테스트(table-driven test) 패턴을 안다
  3. 서브테스트(t.Run)를 안다
  4. 벤치마크(b.N)를 안다
  5. 테스트 커버리지를 측정하는 법을 안다

  ■ 실행: go run main.go
  ■ 빌드: go build -o 12_testing main.go

  ★ 이 파일은 main에서 테스트를 "시뮬레이션"합니다.
    실제로는 _test.go 파일에 작성합니다.

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

package main

import "fmt"

func main() {
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println("  Go 12단계 : 테스팅")
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println()

	lesson1TestingRules()
	lesson2BasicTestSimulation()
	lesson3TableDrivenTest()
	lesson4SubtestSimulation()
	lesson5BenchmarkConcept()
	lesson6TestCoverage()
	lesson7TestHelpers()
	lesson8TestingBestPractices()

	fmt.Println("12단계 학습 완료!")
}

// ── 테스트 대상 함수들 ──

// GradeLabel — 점수를 등급으로 변환
func GradeLabel(score int) string {
	if score >= 90 {
		return "우수"
	}
	if score >= 70 {
		return "통과"
	}
	return "복습 필요"
}

// Add — 단순 덧셈
func Add(a, b int) int {
	return a + b
}

// Abs — 절대값
func Abs(n int) int {
	if n < 0 {
		return -n
	}
	return n
}

// IsPalindrome — 회문 판별
func IsPalindrome(s string) bool {
	runes := []rune(s)
	for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
		if runes[i] != runes[j] {
			return false
		}
	}
	return true
}

// =====================================================================
// 레슨 1 — Go 테스팅 규칙
// =====================================================================
func lesson1TestingRules() {
	fmt.Println("[레슨 1] Go 테스팅 규칙 (외워야 할 것!)")
	fmt.Println()

	/*
	   ★ Go 테스팅의 4가지 철칙:

	   ┌─────────────────────────────────────────────────────────┐
	   │  1. 파일 이름: xxx_test.go 로 끝나야 한다!               │
	   │     → main.go의 테스트 → main_test.go                   │
	   │                                                        │
	   │  2. 함수 이름: Test로 시작하고 대문자가 이어져야 한다!      │
	   │     → func TestGradeLabel(t *testing.T) { ... }         │
	   │     ×  func testGradeLabel(t *testing.T)  ← 소문자! 무시됨│
	   │                                                        │
	   │  3. 인자: *testing.T 하나만 받는다                        │
	   │                                                        │
	   │  4. 실행: go test ./...                                  │
	   └─────────────────────────────────────────────────────────┘

	   ★ 주요 명령어:
	   go test                    → 현재 폴더의 테스트 실행
	   go test ./...              → 모든 하위 폴더 테스트
	   go test -v                 → 자세한 출력
	   go test -run TestGrade     → 이름이 일치하는 테스트만
	   go test -count=1           → 캐시 무시하고 다시 실행
	*/

	fmt.Println("  파일: xxx_test.go")
	fmt.Println("  함수: func TestXxx(t *testing.T)")
	fmt.Println("  실행: go test -v ./...")
	fmt.Println("  필터: go test -run TestGrade")

	fmt.Println()
}

// =====================================================================
// 레슨 2 — 기본 테스트 시뮬레이션
// =====================================================================
func lesson2BasicTestSimulation() {
	fmt.Println("[레슨 2] 기본 테스트: 기대값과 실제값을 비교")
	fmt.Println()

	/*
	   실제 _test.go 파일의 모습:

	   func TestAdd(t *testing.T) {
	       result := Add(2, 3)
	       if result != 5 {
	           t.Errorf("Add(2, 3) = %d, want 5", result)
	       }
	   }

	   ★ Go에는 assert 라이브러리가 기본으로 없다!
	   if + t.Errorf 또는 t.Fatalf로 직접 비교한다.

	   ★ t.Errorf vs t.Fatalf:
	   t.Errorf → 실패 기록하고 계속 진행
	   t.Fatalf → 실패 기록하고 즉시 중단
	*/

	// 시뮬레이션: 기본 테스트
	fmt.Println("  --- TestAdd 시뮬레이션 ---")
	testCases := []struct {
		a, b     int
		expected int
	}{
		{2, 3, 5},
		{0, 0, 0},
		{-1, 1, 0},
		{100, 200, 300},
	}

	for _, tc := range testCases {
		result := Add(tc.a, tc.b)
		status := "PASS"
		if result != tc.expected {
			status = "FAIL"
		}
		fmt.Printf("    Add(%d, %d) = %d (기대: %d) [%s]\n",
			tc.a, tc.b, result, tc.expected, status)
	}

	fmt.Println()
}

// =====================================================================
// 레슨 3 — 테이블 주도 테스트 (★ Go의 핵심 패턴!)
// =====================================================================
func lesson3TableDrivenTest() {
	fmt.Println("[레슨 3] 테이블 주도 테스트: Go에서 가장 많이 쓰는 패턴!")
	fmt.Println()

	/*
	   ★ 테이블 주도 테스트(Table-Driven Test)
	   = 테스트 케이스를 구조체 슬라이스에 모아 놓고 for로 돌리는 패턴

	   왜 좋은가?
	   1. 새 케이스 추가가 쉽다 (한 줄만 추가!)
	   2. 중복 코드가 없다
	   3. 실패 시 어떤 케이스인지 이름으로 바로 알 수 있다

	   실제 코드:
	   ──────────────────────────────────────────
	   func TestGradeLabel(t *testing.T) {
	       tests := []struct {
	           name     string
	           score    int
	           expected string
	       }{
	           {"우수 경계", 90, "우수"},
	           {"통과 경계", 70, "통과"},
	           {"복습 필요", 69, "복습 필요"},
	           {"만점", 100, "우수"},
	           {"0점", 0, "복습 필요"},
	       }

	       for _, tt := range tests {
	           t.Run(tt.name, func(t *testing.T) {
	               result := GradeLabel(tt.score)
	               if result != tt.expected {
	                   t.Errorf("GradeLabel(%d) = %q, want %q",
	                       tt.score, result, tt.expected)
	               }
	           })
	       }
	   }
	   ──────────────────────────────────────────
	*/

	tests := []struct {
		name     string
		score    int
		expected string
	}{
		{"만점", 100, "우수"},
		{"우수 경계", 90, "우수"},
		{"우수 직전", 89, "통과"},
		{"통과 경계", 70, "통과"},
		{"통과 직전", 69, "복습 필요"},
		{"0점", 0, "복습 필요"},
		{"마이너스", -10, "복습 필요"},
	}

	failures := 0
	for _, tt := range tests {
		result := GradeLabel(tt.score)
		status := "PASS"
		if result != tt.expected {
			status = "FAIL"
			failures++
		}
		fmt.Printf("    %-12s: GradeLabel(%3d) = %-8s (기대: %-8s) [%s]\n",
			tt.name, tt.score, result, tt.expected, status)
	}
	fmt.Printf("  결과: %d/%d 통과\n", len(tests)-failures, len(tests))

	fmt.Println()
}

// =====================================================================
// 레슨 4 — 서브테스트 시뮬레이션
// =====================================================================
func lesson4SubtestSimulation() {
	fmt.Println("[레슨 4] 서브테스트: t.Run으로 테스트를 그룹핑")
	fmt.Println()

	/*
	   ★ t.Run("이름", func(t *testing.T) { ... })

	   장점:
	   1. 테스트를 논리적으로 그룹핑
	   2. -run 플래그로 특정 서브테스트만 실행 가능
	      go test -run TestGrade/만점
	   3. 각 서브테스트가 독립적으로 실패/성공

	   ★ 회문 테스트 시뮬레이션:
	*/

	palindromeTests := []struct {
		name     string
		input    string
		expected bool
	}{
		{"한글 회문", "토마토", true},
		{"영어 회문", "racecar", true},
		{"비회문", "hello", false},
		{"한 글자", "a", true},
		{"빈 문자열", "", true},
		{"두 글자 회문", "aa", true},
		{"두 글자 비회문", "ab", false},
	}

	fmt.Println("  --- TestIsPalindrome 서브테스트 ---")
	for _, tt := range palindromeTests {
		result := IsPalindrome(tt.input)
		status := "PASS"
		if result != tt.expected {
			status = "FAIL"
		}
		fmt.Printf("    [%s] IsPalindrome(%q) = %v (기대: %v) [%s]\n",
			tt.name, tt.input, result, tt.expected, status)
	}

	fmt.Println()
}

// =====================================================================
// 레슨 5 — 벤치마크 개념
// =====================================================================
func lesson5BenchmarkConcept() {
	fmt.Println("[레슨 5] 벤치마크: 함수 성능 측정")
	fmt.Println()

	/*
	   ★ 벤치마크 = "이 함수가 얼마나 빠른가?" 측정

	   규칙:
	   1. 함수 이름: Benchmark로 시작
	   2. 인자: *testing.B
	   3. b.N 만큼 반복해야 한다 (Go가 자동으로 N을 조절)

	   ──────────────────────────────────────────
	   func BenchmarkGradeLabel(b *testing.B) {
	       for i := 0; i < b.N; i++ {
	           GradeLabel(85)
	       }
	   }
	   ──────────────────────────────────────────

	   실행:
	   go test -bench=.                  → 모든 벤치마크
	   go test -bench=BenchmarkGrade     → 이름 필터
	   go test -bench=. -benchmem        → 메모리 할당도 표시

	   출력 예시:
	   BenchmarkGradeLabel-8   500000000   2.34 ns/op   0 B/op   0 allocs/op
	                    ↑          ↑          ↑            ↑          ↑
	                  CPU수     반복 수    1회 시간    메모리사용   할당 횟수
	*/

	fmt.Println("  벤치마크 작성:")
	fmt.Println("    func BenchmarkXxx(b *testing.B) {")
	fmt.Println("        for i := 0; i < b.N; i++ {")
	fmt.Println("            함수호출()")
	fmt.Println("        }")
	fmt.Println("    }")
	fmt.Println()
	fmt.Println("  실행: go test -bench=. -benchmem")
	fmt.Println("  비교: go test -bench=. -count=5 | benchstat")

	fmt.Println()
}

// =====================================================================
// 레슨 6 — 테스트 커버리지
// =====================================================================
func lesson6TestCoverage() {
	fmt.Println("[레슨 6] 커버리지: 테스트가 코드의 몇 %를 실행했는가?")
	fmt.Println()

	/*
	   ★ 커버리지 측정 명령어:

	   ┌──────────────────────────────────────────────────────┐
	   │  go test -cover                                      │
	   │  → "coverage: 78.5% of statements"                   │
	   │                                                      │
	   │  go test -coverprofile=coverage.out                   │
	   │  go tool cover -html=coverage.out                     │
	   │  → 브라우저에서 어떤 줄이 실행되었는지 초록/빨강으로 표시! │
	   │                                                      │
	   │  go tool cover -func=coverage.out                     │
	   │  → 함수별 커버리지 퍼센트 출력                          │
	   └──────────────────────────────────────────────────────┘

	   ★ 커버리지 100%가 목표는 아니다!
	   → 핵심 로직, 경계값, 에러 경로를 커버하는 것이 중요
	   → getter/setter 같은 단순 코드는 테스트 불필요
	*/

	fmt.Println("  측정: go test -cover")
	fmt.Println("  시각화: go test -coverprofile=c.out && go tool cover -html=c.out")
	fmt.Println("  함수별: go tool cover -func=c.out")
	fmt.Println("  ★ 70~80% 커버리지면 충분한 경우가 많다!")

	fmt.Println()
}

// =====================================================================
// 레슨 7 — 테스트 헬퍼와 TestMain
// =====================================================================
func lesson7TestHelpers() {
	fmt.Println("[레슨 7] 테스트 헬퍼: 반복 코드를 줄이는 기법")
	fmt.Println()

	/*
	   ★ t.Helper() — 이 함수가 헬퍼임을 표시
	   에러 발생 시 헬퍼 내부가 아닌 "호출한 줄"을 표시해 준다!

	   ──────────────────────────────────────────
	   func assertEqual(t *testing.T, got, want int) {
	       t.Helper()  ← 이것!
	       if got != want {
	           t.Errorf("got %d, want %d", got, want)
	       }
	   }

	   func TestAdd(t *testing.T) {
	       assertEqual(t, Add(2, 3), 5)  ← 에러 시 이 줄이 표시됨
	   }
	   ──────────────────────────────────────────

	   ★ TestMain — 테스트 전체의 setup/teardown
	   ──────────────────────────────────────────
	   func TestMain(m *testing.M) {
	       // 테스트 전: DB 연결, 파일 준비 등
	       setup()

	       code := m.Run()  // 모든 테스트 실행

	       // 테스트 후: DB 정리, 파일 삭제 등
	       teardown()

	       os.Exit(code)
	   }
	   ──────────────────────────────────────────

	   ★ t.Cleanup — Go 1.14+ 개별 테스트의 정리
	   func TestSomething(t *testing.T) {
	       t.Cleanup(func() { /* 이 테스트 끝나면 실행 */ })
	   }
	*/

	fmt.Println("  t.Helper(): 에러 위치를 호출 지점으로 표시")
	fmt.Println("  TestMain(): 전체 테스트의 setup/teardown")
	fmt.Println("  t.Cleanup(): 개별 테스트의 정리 작업")
	fmt.Println("  t.Parallel(): 병렬 실행 허용")

	fmt.Println()
}

// =====================================================================
// 레슨 8 — 테스팅 모범 사례
// =====================================================================
func lesson8TestingBestPractices() {
	fmt.Println("[레슨 8] 테스팅 모범 사례 정리")
	fmt.Println()

	fmt.Println("  ┌────────────────────────────────────────────────────────────┐")
	fmt.Println("  │  1. 테이블 주도 테스트를 기본 패턴으로 쓴다                   │")
	fmt.Println("  │  2. 테스트 이름을 설명적으로 (\"음수_입력_시_에러_반환\")       │")
	fmt.Println("  │  3. 경계값을 반드시 테스트 (0, 최소, 최대, 바로 위/아래)       │")
	fmt.Println("  │  4. 에러 경로도 테스트 (\"이것은 실패해야 한다\")              │")
	fmt.Println("  │  5. 테스트는 독립적이어야 한다 (순서 의존 금지!)               │")
	fmt.Println("  │  6. t.Parallel()로 병렬 실행 가능하게                        │")
	fmt.Println("  │  7. 외부 의존성은 인터페이스로 모킹                           │")
	fmt.Println("  │  8. testdata/ 폴더에 테스트용 파일 보관                      │")
	fmt.Println("  │  9. go test -race 로 경쟁 조건 검사                          │")
	fmt.Println("  │  10. CI에서 자동 실행 (go test ./...)                        │")
	fmt.Println("  └────────────────────────────────────────────────────────────┘")

	fmt.Println()
}
