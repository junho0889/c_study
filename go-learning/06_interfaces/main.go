/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Go 학습 06단계: 인터페이스
  ─ 인터페이스 정의 · 암시적 구현 · 빈 인터페이스 · 타입 단언 · 타입 스위치 ─

  [학습 목표]
  1. 인터페이스의 정의와 암시적 구현을 이해한다
  2. 다형성(여러 타입을 하나로 다루기)을 실습한다
  3. 빈 인터페이스(any)와 타입 단언을 안다
  4. 타입 스위치로 타입별 분기를 안다
  5. 인터페이스 설계 원칙을 안다

  ■ 실행: go run main.go
  ■ 빌드: go build -o 06_interfaces main.go

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

package main

import (
	"fmt"
	"math"
)

// ─────────────────────────────────────────────────────────────────────────
// 인터페이스 & 구조체 정의
// ─────────────────────────────────────────────────────────────────────────

/*
   ★ 인터페이스 = "이 메서드를 가지고 있으면 너도 이 타입이야!"

   비유: "말할 수 있는 것"이라는 기준을 세워 놓으면,
         개든 고양이든 로봇이든 Speak() 메서드만 있으면 합격!
         → Java처럼 "implements" 키워드를 쓰지 않는다! (암시적 구현)

   ┌─────────────────────────────────────────────┐
   │  type Speaker interface {                   │
   │      Label() string                         │
   │      Speak() string                         │
   │  }                                          │
   │                                             │
   │  Dog가 Label()과 Speak()를 가지면 → Speaker! │
   │  Cat이 Label()과 Speak()를 가지면 → Speaker! │
   │  "implements" 없이 자동으로 충족!              │
   └─────────────────────────────────────────────┘
*/

// Speaker — 이름표와 말하기를 할 수 있는 것
type Speaker interface {
	Label() string
	Speak() string
}

// Shape — 도형: 넓이와 둘레를 구할 수 있는 것
type Shape interface {
	Area() float64
	Perimeter() float64
}

// Stringer — fmt.Stringer 와 같은 패턴 (설명용)
type Stringer interface {
	String() string
}

// ── 구체 타입들 ──

type Dog struct{ Name string }
type Cat struct{ Name string }
type Robot struct{ Model string }

type Circle struct{ Radius float64 }
type Rectangle struct{ Width, Height float64 }
type Triangle struct{ A, B, C float64 } // 세 변의 길이

func main() {
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println("  Go 06단계 : 인터페이스")
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println()

	lesson1ImplicitImplementation()
	lesson2Polymorphism()
	lesson3ShapeInterface()
	lesson4EmptyInterface()
	lesson5TypeAssertion()
	lesson6TypeSwitch()
	lesson7InterfaceDesign()
	lesson8NilInterface()

	fmt.Println("06단계 학습 완료!")
}

// ── Speaker 메서드 구현 ──

func (d Dog) Label() string   { return d.Name }
func (d Dog) Speak() string   { return "멍멍!" }
func (c Cat) Label() string   { return c.Name }
func (c Cat) Speak() string   { return "야옹~" }
func (r Robot) Label() string { return r.Model }
func (r Robot) Speak() string { return "삐빅- 안녕하세요." }

// ── Shape 메서드 구현 ──

func (c Circle) Area() float64      { return math.Pi * c.Radius * c.Radius }
func (c Circle) Perimeter() float64  { return 2 * math.Pi * c.Radius }

func (r Rectangle) Area() float64      { return r.Width * r.Height }
func (r Rectangle) Perimeter() float64  { return 2 * (r.Width + r.Height) }

// 삼각형 넓이: 헤론의 공식
func (t Triangle) Area() float64 {
	s := (t.A + t.B + t.C) / 2
	return math.Sqrt(s * (s - t.A) * (s - t.B) * (s - t.C))
}
func (t Triangle) Perimeter() float64 { return t.A + t.B + t.C }

// =====================================================================
// 레슨 1 — 암시적 구현: implements 없이 자동으로!
// =====================================================================
func lesson1ImplicitImplementation() {
	fmt.Println("[레슨 1] 암시적 구현: '선언' 없이 메서드만 맞추면 된다")
	fmt.Println()

	/*
	   Java/C#:  class Dog implements Speaker { ... }
	   Go:       Dog에 Label()과 Speak()이 있으면 자동으로 Speaker!

	   ★ 이것이 Go의 "덕 타이핑(duck typing)":
	   "오리처럼 걷고 오리처럼 꽥꽥거리면 그건 오리다"
	*/

	var s Speaker

	s = Dog{Name: "바둑이"}
	fmt.Printf("  %-10s → %s\n", s.Label(), s.Speak())

	s = Cat{Name: "나비"}
	fmt.Printf("  %-10s → %s\n", s.Label(), s.Speak())

	s = Robot{Model: "GPT-9000"}
	fmt.Printf("  %-10s → %s\n", s.Label(), s.Speak())

	fmt.Println()
}

// =====================================================================
// 레슨 2 — 다형성: 하나의 함수로 여러 타입 처리
// =====================================================================

// introduce — Speaker 인터페이스를 받으므로 Dog, Cat, Robot 모두 처리 가능!
func introduce(s Speaker) string {
	return fmt.Sprintf("저는 '%s'이고, %s", s.Label(), s.Speak())
}

func lesson2Polymorphism() {
	fmt.Println("[레슨 2] 다형성: 한 함수로 여러 타입을 처리한다")
	fmt.Println()

	/*
	   ★ 다형성의 장점:
	   introduce() 함수는 Speaker 인터페이스만 알면 된다.
	   Dog인지 Cat인지 Robot인지 몰라도 된다!
	   → 새로운 타입(예: Parrot)을 추가해도 introduce() 수정 불필요!
	*/

	speakers := []Speaker{
		Dog{Name: "바둑이"},
		Cat{Name: "나비"},
		Robot{Model: "R2D2"},
	}

	for _, s := range speakers {
		fmt.Println(" ", introduce(s))
	}

	fmt.Println()
}

// =====================================================================
// 레슨 3 — Shape 인터페이스: 도형 다형성
// =====================================================================

func printShapeInfo(name string, s Shape) {
	fmt.Printf("  %-8s  넓이=%.2f  둘레=%.2f\n", name, s.Area(), s.Perimeter())
}

func lesson3ShapeInterface() {
	fmt.Println("[레슨 3] Shape 인터페이스: 원, 사각형, 삼각형을 같은 방식으로")
	fmt.Println()

	shapes := []struct {
		name  string
		shape Shape
	}{
		{"원", Circle{Radius: 5}},
		{"사각형", Rectangle{Width: 4, Height: 6}},
		{"삼각형", Triangle{A: 3, B: 4, C: 5}},
	}

	for _, item := range shapes {
		printShapeInfo(item.name, item.shape)
	}

	fmt.Println()
}

// =====================================================================
// 레슨 4 — 빈 인터페이스 (any): 모든 타입을 받을 수 있다
// =====================================================================
func lesson4EmptyInterface() {
	fmt.Println("[레슨 4] 빈 인터페이스 (any): 뭐든 담을 수 있는 상자")
	fmt.Println()

	/*
	   ★ interface{} 또는 any = 메서드가 하나도 없는 인터페이스
	   → 모든 타입은 "메서드 0개" 조건을 자동 충족
	   → 그래서 모든 타입을 담을 수 있다!

	   ┌────────────────────────────────────┐
	   │  var box any                       │
	   │  box = 42          // int OK       │
	   │  box = "hello"     // string OK    │
	   │  box = true        // bool OK      │
	   │  box = Dog{...}    // struct OK    │
	   └────────────────────────────────────┘

	   ★★★ 주의: any를 남용하면 타입 안전성을 잃는다!
	   가능하면 구체적인 인터페이스를 쓰자.
	*/

	// any 슬라이스: 다양한 타입을 한 곳에
	items := []any{42, "hello", true, 3.14, Dog{Name: "바둑이"}}

	for i, item := range items {
		fmt.Printf("  [%d] 값=%v  타입=%T\n", i, item, item)
	}

	fmt.Println()
}

// =====================================================================
// 레슨 5 — 타입 단언 (Type Assertion)
// =====================================================================
func lesson5TypeAssertion() {
	fmt.Println("[레슨 5] 타입 단언: any에서 원래 타입을 꺼내기")
	fmt.Println()

	/*
	   ★ 타입 단언 = "이 인터페이스 안에 들어있는 게 진짜 XX 타입이지?"

	   문법:  값, ok := 인터페이스변수.(타입)
	   ok가 true면 변환 성공, false면 해당 타입이 아님
	*/

	var box any = "Go 언어"

	// 안전한 타입 단언 (comma-ok 패턴)
	str, ok := box.(string)
	if ok {
		fmt.Println("  string으로 변환 성공:", str)
	}

	num, ok := box.(int)
	if !ok {
		fmt.Println("  int로 변환 실패! (num의 제로값:", num, ")")
	}

	/*
	   ★★★ 위험한 방법: ok 없이 단언하면 실패 시 패닉! ★★★
	   num := box.(int)  ← 패닉 발생!

	   → 반드시 comma-ok 패턴을 쓰자
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 6 — 타입 스위치: 타입별로 분기하기
// =====================================================================

func describeValue(val any) string {
	/*
	   ★ 타입 스위치 = switch 문에서 타입을 기준으로 분기

	   switch v := val.(type) {
	   case int:     // v는 int
	   case string:  // v는 string
	   default:      // 그 외
	   }
	*/
	switch v := val.(type) {
	case int:
		return fmt.Sprintf("정수 %d (두 배: %d)", v, v*2)
	case float64:
		return fmt.Sprintf("실수 %.2f", v)
	case string:
		return fmt.Sprintf("문자열 \"%s\" (길이: %d)", v, len(v))
	case bool:
		if v {
			return "참(true)"
		}
		return "거짓(false)"
	case Speaker:
		return fmt.Sprintf("Speaker: %s → %s", v.Label(), v.Speak())
	default:
		return fmt.Sprintf("알 수 없는 타입: %T", v)
	}
}

func lesson6TypeSwitch() {
	fmt.Println("[레슨 6] 타입 스위치: 타입별로 다르게 처리")
	fmt.Println()

	testValues := []any{
		42,
		3.14,
		"안녕하세요",
		true,
		Dog{Name: "바둑이"},
		[]int{1, 2, 3},
	}

	for _, val := range testValues {
		fmt.Println(" ", describeValue(val))
	}

	fmt.Println()
}

// =====================================================================
// 레슨 7 — 인터페이스 설계 원칙
// =====================================================================
func lesson7InterfaceDesign() {
	fmt.Println("[레슨 7] 인터페이스 설계 원칙")
	fmt.Println()

	/*
	   ★ Go의 인터페이스 철학: "작게, 작게, 더 작게!"

	   ┌─────────────────────────────────────────────────────────┐
	   │  원칙 1: 인터페이스는 1~2개 메서드가 이상적                │
	   │  ────────────────────────────────────────────────        │
	   │  io.Reader    →  Read(p []byte) (n int, err error)      │
	   │  io.Writer    →  Write(p []byte) (n int, err error)     │
	   │  fmt.Stringer →  String() string                        │
	   │  error        →  Error() string                         │
	   │                                                         │
	   │  원칙 2: "소비자 쪽에서 인터페이스를 정의하라"              │
	   │  ────────────────────────────────────────────────        │
	   │  패키지 A가 Dog를 만들고,                                 │
	   │  패키지 B가 Speaker 인터페이스를 정의하면                   │
	   │  → A는 B를 몰라도 된다! (느슨한 결합)                     │
	   │                                                         │
	   │  원칙 3: 큰 인터페이스는 작은 것을 조합해서 만든다           │
	   │  ────────────────────────────────────────────────        │
	   │  type ReadWriter interface {                             │
	   │      Reader                                              │
	   │      Writer                                              │
	   │  }                                                       │
	   └─────────────────────────────────────────────────────────┘
	*/

	fmt.Println("  1. 인터페이스는 작을수록 좋다 (1~2개 메서드)")
	fmt.Println("  2. 소비자(사용하는 쪽)가 인터페이스를 정의한다")
	fmt.Println("  3. 큰 인터페이스 = 작은 인터페이스의 조합")
	fmt.Println("  4. '필요할 때' 인터페이스를 만든다 (미리 만들지 않는다)")

	fmt.Println()
}

// =====================================================================
// 레슨 8 — nil 인터페이스 주의사항
// =====================================================================
func lesson8NilInterface() {
	fmt.Println("[레슨 8] nil 인터페이스 주의사항")
	fmt.Println()

	/*
	   ★★★ 인터페이스의 nil은 두 가지 의미가 있다! ★★★

	   인터페이스 = (타입 정보, 값)  두 칸짜리 상자

	   ┌────────────────────────────────────────────────┐
	   │  상황 1: 완전한 nil                              │
	   │  var s Speaker           → (nil, nil)  = nil    │
	   │                                                 │
	   │  상황 2: 타입은 있지만 값이 nil                    │
	   │  var d *Dog = nil                               │
	   │  var s Speaker = d      → (*Dog, nil) ≠ nil !!  │
	   │                                                 │
	   │  ★ 상황 2는 s != nil 이다! 이것이 Go의 유명한 함정! │
	   └────────────────────────────────────────────────┘
	*/

	// 상황 1: 완전한 nil 인터페이스
	var s1 Speaker
	fmt.Println("  s1 == nil:", s1 == nil) // true

	// 상황 2: 타입 정보가 있는 nil
	var dogPtr *Dog // nil 포인터
	var s2 Speaker = dogPtr
	fmt.Println("  s2 == nil:", s2 == nil) // false!  ← 함정!

	fmt.Println("  → 타입 정보(*Dog)가 있으므로 nil이 아닌 것으로 판단된다")
	fmt.Println("  → 이 함정을 피하려면 인터페이스에 직접 nil을 대입하자")

	fmt.Println()
}
