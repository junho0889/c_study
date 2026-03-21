/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Go 학습 05단계: 구조체와 메서드
  ─ struct 정의 · 메서드 · 값/포인터 리시버 · 임베딩 · 생성자 패턴 ─

  [학습 목표]
  1. struct로 여러 값을 하나로 묶는 법을 안다
  2. 값 리시버와 포인터 리시버의 차이를 이해한다
  3. 구조체 임베딩(상속 대용)을 이해한다
  4. 생성자 패턴(NewXxx)과 태그를 안다

  ■ 실행: go run main.go
  ■ 빌드: go build -o 05_structs main.go

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

package main

import "fmt"

// ─────────────────────────────────────────────────────────────────────────
// 구조체 정의
// ─────────────────────────────────────────────────────────────────────────

/*
   ★ 구조체 = 서로 관련된 데이터를 한 묶음으로 모아 놓은 것

   비유: "학생"이라는 한 명을 설명하려면
         이름, 점수, 숙제 수 등 여러 정보가 필요하다.
         이것을 한 상자에 담아 놓은 것이 구조체!

   ┌──────────────────────────────┐
   │  Student 구조체              │
   ├──────────────────────────────┤
   │  Name          string       │
   │  Score         int          │
   │  HomeworkCount int          │
   └──────────────────────────────┘
*/

// Student — 학생 정보를 담는 구조체
type Student struct {
	Name          string
	Score         int
	HomeworkCount int
}

// Animal — 동물 정보 (임베딩 레슨에서 사용)
type Animal struct {
	Name  string
	Legs  int
	Sound string
}

// Dog — Animal을 임베딩한 구조체
type Dog struct {
	Animal       // 임베딩! (이름 없이 타입만 쓴다)
	Breed  string // 견종
}

// Rect — 사각형 (포인터 리시버 레슨)
type Rect struct {
	Width  float64
	Height float64
}

// Counter — 카운터 (포인터 리시버의 필요성 설명)
type Counter struct {
	Name  string
	Count int
}

func main() {
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println("  Go 05단계 : 구조체와 메서드")
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println()

	lesson1StructBasics()
	lesson2StructMethods()
	lesson3ValueVsPointerReceiver()
	lesson4ConstructorPattern()
	lesson5Embedding()
	lesson6StructComparison()
	lesson7AnonymousStruct()

	fmt.Println("05단계 학습 완료!")
}

// =====================================================================
// 레슨 1 — 구조체 기초: 만들기, 읽기, 바꾸기
// =====================================================================
func lesson1StructBasics() {
	fmt.Println("[레슨 1] 구조체 기초: 만들고, 읽고, 바꾸기")
	fmt.Println()

	// 방법 1: 필드 이름을 명시 (권장!)
	s1 := Student{
		Name:          "민수",
		Score:         85,
		HomeworkCount: 3,
	}
	fmt.Println("  학생1:", s1)
	fmt.Println("  이름:", s1.Name) // 점(.)으로 필드 접근

	// 방법 2: 순서대로 넣기 (필드 이름 생략)
	s2 := Student{"지우", 92, 5}
	fmt.Println("  학생2:", s2)

	/*
	   ★ 주의: 순서대로 넣으면 나중에 필드가 추가될 때 버그가 생긴다!
	   → 항상 필드 이름을 명시하는 것을 권장
	*/

	// 방법 3: 빈 구조체(제로값)
	var s3 Student
	fmt.Println("  빈 학생:", s3) // {"" 0 0}

	/*
	   ★ 제로값 정리:
	   ┌──────────┬─────────┐
	   │ 타입      │ 제로값   │
	   ├──────────┼─────────┤
	   │ string   │ ""      │
	   │ int      │ 0       │
	   │ bool     │ false   │
	   │ 포인터    │ nil     │
	   └──────────┴─────────┘
	*/

	// 필드 값 수정
	s1.Score = 90
	fmt.Println("  민수 점수 수정 후:", s1.Score)

	fmt.Println()
}

// =====================================================================
// 레슨 2 — 메서드: 구조체에 '행동'을 붙이기
// =====================================================================

/*
   ★ 메서드 = 특정 타입에 '소속된' 함수
   func (받는사람 타입) 이름() 반환타입 { ... }
        ^^^^^^^^^^^^^^
        이것을 "리시버(receiver)"라고 부른다

   비유: "학생"이라는 상자에 "성적표 출력"이라는 버튼을 달아 놓는 느낌
*/

// ResultLabel — 점수에 따라 등급을 반환 (값 리시버)
func (s Student) ResultLabel() string {
	if s.Score >= 90 {
		return "우수"
	}
	if s.Score >= 70 {
		return "통과"
	}
	return "복습 필요"
}

// Summary — 학생 정보를 한 줄로 요약
func (s Student) Summary() string {
	return fmt.Sprintf("%s — %d점 — 숙제 %d개 — %s",
		s.Name, s.Score, s.HomeworkCount, s.ResultLabel())
}

// Area — 사각형 넓이
func (r Rect) Area() float64 {
	return r.Width * r.Height
}

// Perimeter — 사각형 둘레
func (r Rect) Perimeter() float64 {
	return 2 * (r.Width + r.Height)
}

func lesson2StructMethods() {
	fmt.Println("[레슨 2] 메서드: 구조체에 '행동'을 붙인다")
	fmt.Println()

	s := Student{Name: "서연", Score: 88, HomeworkCount: 4}
	fmt.Println("  요약:", s.Summary())

	r := Rect{Width: 10, Height: 5}
	fmt.Printf("  사각형: 넓이=%.1f  둘레=%.1f\n", r.Area(), r.Perimeter())

	fmt.Println()
}

// =====================================================================
// 레슨 3 — 값 리시버 vs 포인터 리시버 (★ 핵심!)
// =====================================================================

/*
   ┌──────────────────────────────────────────────────────┐
   │            값 리시버              포인터 리시버          │
   ├──────────────────────────────────────────────────────┤
   │ func (s Student)          func (s *Student)          │
   │ 복사본을 받는다             원본을 가리킨다              │
   │ 안에서 바꿔도 원본 그대로    안에서 바꾸면 원본도 바뀜!    │
   │ "읽기 전용"에 적합          "수정"이 필요할 때 필수       │
   └──────────────────────────────────────────────────────┘

   ★ 규칙:
   1. 필드를 바꿔야 하면 → 포인터 리시버
   2. 구조체가 크면      → 포인터 리시버 (복사 비용 줄이기)
   3. 읽기만 하면        → 값 리시버도 OK
   4. 한 타입에 포인터 리시버가 하나라도 있으면 → 전부 포인터로 통일 권장
*/

// Increment — 포인터 리시버: 원본의 Count를 1 올린다
func (c *Counter) Increment() {
	c.Count++
}

// Reset — 포인터 리시버: 원본의 Count를 0으로
func (c *Counter) Reset() {
	c.Count = 0
}

// Display — 읽기용
func (c Counter) Display() string {
	return fmt.Sprintf("[%s] 현재 횟수: %d", c.Name, c.Count)
}

func lesson3ValueVsPointerReceiver() {
	fmt.Println("[레슨 3] 값 리시버 vs 포인터 리시버")
	fmt.Println()

	c := Counter{Name: "방문자", Count: 0}

	c.Increment()
	c.Increment()
	c.Increment()
	fmt.Println(" ", c.Display()) // 3

	c.Reset()
	fmt.Println("  리셋 후:", c.Display()) // 0

	/*
	   ★ 만약 Increment가 값 리시버였다면?
	   func (c Counter) Increment() { c.Count++ }
	   → 복사본의 Count만 올라가고, 원본은 그대로 0!
	   → 이 버그는 컴파일 에러가 안 나서 찾기 어렵다!
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 4 — 생성자 패턴 (NewXxx)
// =====================================================================

/*
   Go에는 class도 constructor도 없다.
   대신 "NewXxx" 이름의 함수를 관례적으로 만들어 구조체를 초기화한다.

   ★ 이 패턴이 필요한 이유:
   1. 유효성 검사를 넣을 수 있다
   2. 기본값을 설정할 수 있다
   3. 포인터를 반환하여 복사 비용을 줄인다
*/

func NewStudent(name string, score int) (*Student, error) {
	if name == "" {
		return nil, fmt.Errorf("이름이 비어 있습니다")
	}
	if score < 0 || score > 100 {
		return nil, fmt.Errorf("점수(%d)는 0~100 범위여야 합니다", score)
	}
	return &Student{
		Name:          name,
		Score:         score,
		HomeworkCount: 0,
	}, nil
}

func lesson4ConstructorPattern() {
	fmt.Println("[레슨 4] 생성자 패턴: NewXxx 함수")
	fmt.Println()

	s, err := NewStudent("하준", 88)
	if err != nil {
		fmt.Println("  에러:", err)
	} else {
		fmt.Println("  생성 성공:", s.Summary())
	}

	_, err = NewStudent("", 50)
	fmt.Println("  빈 이름 시도:", err)

	_, err = NewStudent("테스트", 150)
	fmt.Println("  범위 초과 시도:", err)

	fmt.Println()
}

// =====================================================================
// 레슨 5 — 구조체 임베딩 (상속 대용)
// =====================================================================
func lesson5Embedding() {
	fmt.Println("[레슨 5] 구조체 임베딩 — Go 스타일의 '상속'")
	fmt.Println()

	/*
	   ★ Go에는 클래스 상속이 없다!
	   대신 "임베딩"으로 다른 구조체의 필드와 메서드를 가져온다.

	   type Dog struct {
	       Animal        ← 임베딩 (이름 없이 타입만!)
	       Breed string
	   }

	   Dog는 Animal의 Name, Legs, Sound를 마치 자기 것처럼 쓸 수 있다!
	*/

	d := Dog{
		Animal: Animal{Name: "바둑이", Legs: 4, Sound: "멍멍"},
		Breed:  "진돗개",
	}

	// Animal의 필드를 직접 접근 가능
	fmt.Println("  이름:", d.Name) // d.Animal.Name 과 같다
	fmt.Println("  다리:", d.Legs)
	fmt.Println("  소리:", d.Sound)
	fmt.Println("  견종:", d.Breed)

	/*
	   ★ 임베딩 vs 상속:
	   ┌────────────────────┬──────────────────────┐
	   │  OOP 상속           │  Go 임베딩            │
	   ├────────────────────┼──────────────────────┤
	   │  "Dog IS-A Animal"  │  "Dog HAS-A Animal"  │
	   │  다형성 자동         │  인터페이스로 다형성   │
	   │  메서드 오버라이드   │  같은 이름 메서드 숨김 │
	   └────────────────────┴──────────────────────┘
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 6 — 구조체 비교
// =====================================================================
func lesson6StructComparison() {
	fmt.Println("[레슨 6] 구조체 비교: == 가 가능한 조건")
	fmt.Println()

	/*
	   ★ 모든 필드가 비교 가능한 타입이면 == 로 비교할 수 있다!
	   (int, string, bool 등은 비교 가능)
	   (슬라이스, 맵, 함수가 필드에 있으면 == 불가!)
	*/

	a := Student{Name: "민수", Score: 90, HomeworkCount: 5}
	b := Student{Name: "민수", Score: 90, HomeworkCount: 5}
	c := Student{Name: "지우", Score: 80, HomeworkCount: 3}

	fmt.Println("  a == b:", a == b) // true
	fmt.Println("  a == c:", a == c) // false

	fmt.Println()
}

// =====================================================================
// 레슨 7 — 익명 구조체 (임시용)
// =====================================================================
func lesson7AnonymousStruct() {
	fmt.Println("[레슨 7] 익명 구조체: 한 번만 쓸 때 편리하다")
	fmt.Println()

	/*
	   따로 type을 선언하지 않고 즉석에서 구조체를 만들 수 있다.
	   테스트 코드나 JSON 파싱에서 자주 쓰인다.
	*/

	config := struct {
		Host string
		Port int
		SSL  bool
	}{
		Host: "localhost",
		Port: 8080,
		SSL:  false,
	}

	fmt.Printf("  서버: %s:%d (SSL=%v)\n", config.Host, config.Port, config.SSL)

	// 테이블 기반 테스트에서도 많이 쓰인다
	tests := []struct {
		input    int
		expected string
	}{
		{95, "우수"},
		{75, "통과"},
		{50, "복습 필요"},
	}
	fmt.Println("  --- 익명 구조체 슬라이스 (테스트 케이스) ---")
	for _, tc := range tests {
		s := Student{Score: tc.input}
		result := s.ResultLabel()
		status := "PASS"
		if result != tc.expected {
			status = "FAIL"
		}
		fmt.Printf("    점수 %d → %s (%s)\n", tc.input, result, status)
	}

	fmt.Println()
}
