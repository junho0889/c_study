/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Go 학습 08단계: 에러 처리
  ─ error 인터페이스 · fmt.Errorf · errors.Is/As · 커스텀 에러 · panic/recover ─

  [학습 목표]
  1. Go의 에러 처리 철학 (예외 없음, 값으로 에러 전달)을 안다
  2. error 인터페이스와 fmt.Errorf를 안다
  3. 에러 래핑(%w)과 errors.Is / errors.As를 안다
  4. 커스텀 에러 타입을 만든다
  5. panic/recover의 용도와 제한을 안다

  ■ 실행: go run main.go
  ■ 빌드: go build -o 08_errors main.go

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

package main

import (
	"errors"
	"fmt"
	"strconv"
)

func main() {
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println("  Go 08단계 : 에러 처리")
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println()

	lesson1ErrorBasics()
	lesson2FmtErrorf()
	lesson3ErrorWrapping()
	lesson4ErrorsIsAs()
	lesson5CustomError()
	lesson6MultipleErrorCheck()
	lesson7PanicRecover()
	lesson8BestPractices()

	fmt.Println("08단계 학습 완료!")
}

// =====================================================================
// 레슨 1 — Go의 에러 처리 철학
// =====================================================================
func lesson1ErrorBasics() {
	fmt.Println("[레슨 1] Go의 에러 = 그냥 '값'이다 (예외가 아니다!)")
	fmt.Println()

	/*
	   ★ 다른 언어: try-catch로 예외를 던지고 잡는다
	   ★ Go:       함수가 (결과, error) 를 돌려준다. error가 nil이 아니면 실패!

	   ┌────────────────────────────────────────────────────┐
	   │  type error interface {                            │
	   │      Error() string                                │
	   │  }                                                 │
	   │                                                    │
	   │  error는 그냥 인터페이스! Error() 메서드만 있으면 됨  │
	   └────────────────────────────────────────────────────┘

	   비유: 식당에서 "주문 결과"와 "문제 메모"를 같이 돌려주는 것
	         문제 메모가 비어있으면(nil) → 성공!
	         문제 메모에 뭔가 적혀있으면 → 확인 필요!
	*/

	result, err := divide(10, 3)
	if err != nil {
		fmt.Println("  에러:", err)
	} else {
		fmt.Printf("  10 / 3 = %.2f\n", result)
	}

	result, err = divide(10, 0)
	if err != nil {
		fmt.Println("  에러:", err)
	} else {
		fmt.Printf("  10 / 0 = %.2f\n", result)
	}

	/*
	   ★ if err != nil { ... } 패턴
	   Go 코드에서 가장 많이 보는 패턴!
	   "에러가 nil이 아니면 처리하고 돌아가라"
	*/

	fmt.Println()
}

func divide(a, b float64) (float64, error) {
	if b == 0 {
		return 0, fmt.Errorf("0으로 나눌 수 없습니다")
	}
	return a / b, nil
}

// =====================================================================
// 레슨 2 — fmt.Errorf와 errors.New
// =====================================================================

// 센티널 에러: 패키지 수준에서 미리 정의한 에러 값
var ErrNegativeScore = errors.New("점수는 음수가 될 수 없습니다")
var ErrTooHighScore = errors.New("점수는 100을 넘을 수 없습니다")

func lesson2FmtErrorf() {
	fmt.Println("[레슨 2] 에러 만들기: errors.New vs fmt.Errorf")
	fmt.Println()

	/*
	   ★ 에러를 만드는 두 가지 방법:

	   1) errors.New("고정 메시지")
	      → 항상 같은 메시지 (변수 포함 불가)
	      → "센티널 에러"로 쓸 때 적합

	   2) fmt.Errorf("메시지 %d", 변수)
	      → Printf처럼 변수를 넣을 수 있다
	      → 상세한 에러 메시지에 적합
	*/

	// errors.New — 센티널 에러
	err1 := validateScore(-5)
	fmt.Println("  -5점 검증:", err1)

	err2 := validateScore(150)
	fmt.Println("  150점 검증:", err2)

	// fmt.Errorf — 동적 메시지
	err3 := parseAndDouble("abc")
	fmt.Println("  'abc' 파싱:", err3)

	err4 := parseAndDouble("21")
	fmt.Println("  '21' 파싱:", err4) // nil (성공)

	fmt.Println()
}

func validateScore(score int) error {
	if score < 0 {
		return ErrNegativeScore
	}
	if score > 100 {
		return ErrTooHighScore
	}
	return nil
}

func parseAndDouble(s string) error {
	num, err := strconv.Atoi(s)
	if err != nil {
		return fmt.Errorf("'%s'를 숫자로 바꿀 수 없습니다: %v", s, err)
	}
	fmt.Printf("  %s × 2 = %d\n", s, num*2)
	return nil
}

// =====================================================================
// 레슨 3 — 에러 래핑 (%w)
// =====================================================================
func lesson3ErrorWrapping() {
	fmt.Println("[레슨 3] 에러 래핑: 원인을 감싸서 전달하기 (%w)")
	fmt.Println()

	/*
	   ★ 에러 래핑 = 원래 에러를 보존하면서 맥락을 추가하는 것

	   fmt.Errorf("파일 읽기 실패: %w", originalErr)
	                                ^^
	                           %v 대신 %w를 쓴다!

	   비유: 택배가 파손되었을 때
	         "포장 안의 상자 안의 물건이 깨짐" 처럼
	         각 단계의 맥락을 겹겹이 감싸는 것

	   ┌───────────────────────────────────────────┐
	   │  %v → 에러 메시지만 포함 (원본 에러 소실!)   │
	   │  %w → 에러 메시지 + 원본 에러 보존 (연결!)   │
	   └───────────────────────────────────────────┘
	*/

	err := loadStudentScore("민수")
	if err != nil {
		fmt.Println("  최종 에러:", err)

		// Unwrap으로 원본 에러를 꺼낼 수 있다
		unwrapped := errors.Unwrap(err)
		if unwrapped != nil {
			fmt.Println("  한 겹 벗기면:", unwrapped)
		}
	}

	fmt.Println()
}

func readFromDB(name string) (int, error) {
	// 데이터베이스에서 찾지 못한 상황을 시뮬레이션
	return 0, fmt.Errorf("'%s' 레코드 없음", name)
}

func loadStudentScore(name string) error {
	_, err := readFromDB(name)
	if err != nil {
		// %w로 원본 에러를 감싸면서 맥락을 추가
		return fmt.Errorf("학생 점수 조회 실패: %w", err)
	}
	return nil
}

// =====================================================================
// 레슨 4 — errors.Is와 errors.As
// =====================================================================

var ErrNotFound = errors.New("데이터를 찾을 수 없습니다")

func findStudent(name string) error {
	// 센티널 에러를 래핑해서 반환
	return fmt.Errorf("DB 조회 중: %w", ErrNotFound)
}

func lesson4ErrorsIsAs() {
	fmt.Println("[레슨 4] errors.Is / errors.As: 래핑된 에러 검사")
	fmt.Println()

	/*
	   ★ errors.Is(err, target)
	   → err 또는 err 안에 래핑된 에러 중 target과 같은 게 있는가?

	   ★ errors.As(err, &target)
	   → err 또는 래핑된 에러 중 target 타입인 것이 있으면 꺼내기

	   ┌────────────────────────────────────────────────────┐
	   │  err == ErrNotFound          ← 래핑되면 false!     │
	   │  errors.Is(err, ErrNotFound) ← 래핑 안까지 확인!    │
	   │                              → 이것을 써야 한다!    │
	   └────────────────────────────────────────────────────┘
	*/

	err := findStudent("철수")

	// 잘못된 비교 (래핑된 에러는 == 로 못 찾는다!)
	fmt.Println("  err == ErrNotFound:", err == ErrNotFound) // false!

	// 올바른 비교
	fmt.Println("  errors.Is(err, ErrNotFound):", errors.Is(err, ErrNotFound)) // true!

	fmt.Println()
}

// =====================================================================
// 레슨 5 — 커스텀 에러 타입
// =====================================================================

/*
   ★ 커스텀 에러 = error 인터페이스를 구현한 구조체

   에러에 추가 정보(코드, 필드명 등)를 담고 싶을 때 사용
*/

// ValidationError — 검증 실패 시 어떤 필드에서 실패했는지 담는 에러
type ValidationError struct {
	Field   string
	Message string
}

func (e *ValidationError) Error() string {
	return fmt.Sprintf("검증 실패 [%s]: %s", e.Field, e.Message)
}

func validateStudent(name string, score int) error {
	if name == "" {
		return &ValidationError{Field: "Name", Message: "이름이 비어있습니다"}
	}
	if score < 0 || score > 100 {
		return &ValidationError{
			Field:   "Score",
			Message: fmt.Sprintf("%d는 0~100 범위를 벗어났습니다", score),
		}
	}
	return nil
}

func lesson5CustomError() {
	fmt.Println("[레슨 5] 커스텀 에러: 에러에 구조화된 정보 담기")
	fmt.Println()

	testCases := []struct {
		name  string
		score int
	}{
		{"", 80},
		{"민수", -10},
		{"지우", 95},
	}

	for _, tc := range testCases {
		err := validateStudent(tc.name, tc.score)
		if err != nil {
			fmt.Printf("  이름='%s' 점수=%d → %s\n", tc.name, tc.score, err)

			// errors.As로 커스텀 에러의 필드에 접근
			var ve *ValidationError
			if errors.As(err, &ve) {
				fmt.Printf("    → 문제 필드: %s\n", ve.Field)
			}
		} else {
			fmt.Printf("  이름='%s' 점수=%d → 검증 통과!\n", tc.name, tc.score)
		}
	}

	fmt.Println()
}

// =====================================================================
// 레슨 6 — 여러 에러를 한번에 체크하는 패턴
// =====================================================================
func lesson6MultipleErrorCheck() {
	fmt.Println("[레슨 6] 여러 단계의 에러를 깔끔하게 처리하기")
	fmt.Println()

	/*
	   ★ Go에서 가장 흔한 불만: "if err != nil 이 너무 많다!"

	   방법 1: 일찍 반환 (early return) — 가장 권장!
	   방법 2: 에러를 모아서 한번에 반환
	   방법 3: 헬퍼 함수로 반복 줄이기
	*/

	// 방법 1: Early return 패턴
	result, err := processStudentData("85")
	if err != nil {
		fmt.Println("  처리 실패:", err)
	} else {
		fmt.Println("  처리 결과:", result)
	}

	result, err = processStudentData("abc")
	if err != nil {
		fmt.Println("  처리 실패:", err)
	} else {
		fmt.Println("  처리 결과:", result)
	}

	fmt.Println()
}

func processStudentData(input string) (string, error) {
	// 단계 1: 문자열 → 숫자
	score, err := strconv.Atoi(input)
	if err != nil {
		return "", fmt.Errorf("점수 파싱 실패: %w", err)
	}

	// 단계 2: 범위 검증
	if score < 0 || score > 100 {
		return "", fmt.Errorf("점수 %d는 범위 밖", score)
	}

	// 단계 3: 등급 계산
	grade := "복습 필요"
	if score >= 90 {
		grade = "우수"
	} else if score >= 70 {
		grade = "통과"
	}

	return fmt.Sprintf("%d점 → %s", score, grade), nil
}

// =====================================================================
// 레슨 7 — panic과 recover
// =====================================================================
func lesson7PanicRecover() {
	fmt.Println("[레슨 7] panic/recover: 정말 심각한 상황에서만!")
	fmt.Println()

	/*
	   ★ panic = 프로그램을 즉시 멈추는 비상 버튼

	   ┌──────────────────────────────────────────────────┐
	   │  error        → 예상 가능한 실패 (파일 없음 등)    │
	   │  panic        → 프로그래머의 실수, 복구 불가 상황   │
	   │                  (nil 포인터 접근, 범위 초과 등)    │
	   ├──────────────────────────────────────────────────┤
	   │  ★ 규칙: 라이브러리는 panic하지 마라!              │
	   │    → error를 반환해서 호출자가 결정하게 하라        │
	   │    → panic은 main이나 init에서만 쓰는 것이 관례    │
	   └──────────────────────────────────────────────────┘
	*/

	// recover 로 panic 잡기
	fmt.Println("  --- recover로 panic 잡기 ---")
	result := safeDivide(10, 0)
	fmt.Println("  safeDivide(10, 0):", result)

	result = safeDivide(10, 3)
	fmt.Println("  safeDivide(10, 3):", result)

	/*
	   ★ recover()는 반드시 defer 함수 안에서 호출해야 한다!
	   일반 함수에서 호출하면 항상 nil을 반환한다.

	   defer func() {
	       if r := recover(); r != nil {
	           // panic 값이 r에 들어있다
	       }
	   }()
	*/

	fmt.Println()
}

func safeDivide(a, b int) (result string) {
	defer func() {
		if r := recover(); r != nil {
			result = fmt.Sprintf("panic 복구: %v", r)
		}
	}()

	if b == 0 {
		panic("0으로 나누기 시도!")
	}
	return fmt.Sprintf("%d / %d = %d", a, b, a/b)
}

// =====================================================================
// 레슨 8 — 에러 처리 모범 사례
// =====================================================================
func lesson8BestPractices() {
	fmt.Println("[레슨 8] 에러 처리 모범 사례 정리")
	fmt.Println()

	fmt.Println("  ┌────────────────────────────────────────────────────────┐")
	fmt.Println("  │  1. error는 항상 확인하라 (무시하지 마라!)               │")
	fmt.Println("  │     result, _ := doSomething()  ← 위험!               │")
	fmt.Println("  │                                                       │")
	fmt.Println("  │  2. 에러 메시지에 맥락을 추가하라                        │")
	fmt.Println("  │     return fmt.Errorf(\"DB 연결 실패: %w\", err)         │")
	fmt.Println("  │                                                       │")
	fmt.Println("  │  3. 센티널 에러는 패키지 수준에서 선언                    │")
	fmt.Println("  │     var ErrNotFound = errors.New(\"not found\")          │")
	fmt.Println("  │                                                       │")
	fmt.Println("  │  4. 에러 비교에는 errors.Is/As를 쓴다 (== 대신!)         │")
	fmt.Println("  │                                                       │")
	fmt.Println("  │  5. panic은 진짜 버그에만! 라이브러리에서 쓰지 마라!      │")
	fmt.Println("  │                                                       │")
	fmt.Println("  │  6. 에러 메시지는 소문자로 시작, 마침표 없이              │")
	fmt.Println("  │     \"open file failed\" (O)  \"Open file failed.\" (X)   │")
	fmt.Println("  └────────────────────────────────────────────────────────┘")

	fmt.Println()
}
