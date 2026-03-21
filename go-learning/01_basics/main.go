/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Go 학습 01단계: 기초의 기초
  ─ 변수, 자료형, 입출력, 연산자, 상수 ─

  Go 언어는 2009년 구글에서 만든 프로그래밍 언어예요.
  마치 레고처럼 간단한 조각들을 모아서 큰 프로그램을 만들 수 있어요!

  ■ 실행 방법: go run main.go
  ■ 빌드 방법: go build -o basics.exe main.go

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// package main: 이 파일이 "프로그램의 시작점"이라는 표시예요.
// 마치 학교에서 "1학년 1반" 이름표를 붙이는 것처럼,
// Go의 모든 실행 가능한 프로그램은 반드시 "main" 패키지여야 해요.
package main

// import: 다른 곳에서 만들어 놓은 도구들을 가져와 사용하는 것이에요.
// 마치 요리할 때 주방에서 냄비, 도마, 칼을 꺼내 오는 것처럼요!
//
// "fmt"는 Format의 줄임말로, 화면에 글자를 출력하거나
// 키보드에서 입력을 받을 때 사용하는 도구 모음이에요.
// "bufio"는 Buffered I/O의 줄임말로, 줄 단위로 입력을 받을 때 사용해요.
// "os"는 Operating System의 줄임말로, 컴퓨터 시스템과 대화할 때 써요.
// "math"는 수학 계산을 도와주는 도구 모음이에요.
// "strings"는 글자(문자열)를 다루는 도구 모음이에요.
// "strconv"는 숫자와 글자를 서로 바꿔주는 도구예요.
import (
	"bufio"
	"fmt"
	"math"
	"os"
	"strconv"
	"strings"
)

// ┌─────────────────────────────────────────────────────────────┐
// │                    상수 선언 (Constants)                     │
// │  상수는 한번 정해지면 절대 바뀌지 않는 값이에요.              │
// │  마치 원주율(π = 3.14159...)처럼 항상 같은 값이죠!           │
// └─────────────────────────────────────────────────────────────┘

// const: 상수를 선언하는 키워드예요.
// 상수는 변수와 달리 프로그램이 실행되는 동안 절대 바뀌지 않아요.
const (
	// 일반 상수
	AppName    = "Go 기초 학습"
	AppVersion = "1.0.0"
	MaxScore   = 100

	// iota: 0부터 자동으로 1씩 증가하는 마법의 숫자예요!
	// 마치 출석부에서 번호를 자동으로 매기는 것처럼요.
	// 아래 예시에서 Monday=0, Tuesday=1, Wednesday=2, ... 이렇게 돼요.
	Monday    = iota // 0
	Tuesday          // 1
	Wednesday        // 2
	Thursday         // 3
	Friday           // 4
	Saturday         // 5
	Sunday           // 6
)

// iota를 활용한 비트 플래그 (조금 어려운 내용이에요)
// 1 << iota는 2의 거듭제곱을 만들어요: 1, 2, 4, 8, 16...
// 마치 종이를 반으로 접을 때마다 2배씩 두꺼워지는 것처럼!
const (
	ReadPermission  = 1 << iota // 1  (이진수: 001) - 읽기 권한
	WritePermission             // 2  (이진수: 010) - 쓰기 권한
	ExecPermission              // 4  (이진수: 100) - 실행 권한
)

// main 함수: 프로그램이 시작되는 곳이에요.
// 마치 운동회의 시작을 알리는 출발 신호총 같은 역할을 해요!
// Go 프로그램은 반드시 main 패키지 안에 main() 함수가 있어야 실행돼요.
func main() {
	// ┌─────────────────────────────────────────────────────────┐
	// │              섹션 1: 화면에 글자 출력하기                 │
	// └─────────────────────────────────────────────────────────┘
	demonstratePrinting()

	// ┌─────────────────────────────────────────────────────────┐
	// │              섹션 2: 변수 선언과 사용                    │
	// └─────────────────────────────────────────────────────────┘
	demonstrateVariables()

	// ┌─────────────────────────────────────────────────────────┐
	// │              섹션 3: 제로값 (Zero Values)                │
	// └─────────────────────────────────────────────────────────┘
	demonstrateZeroValues()

	// ┌─────────────────────────────────────────────────────────┐
	// │              섹션 4: 자료형 (Data Types)                 │
	// └─────────────────────────────────────────────────────────┘
	demonstrateDataTypes()

	// ┌─────────────────────────────────────────────────────────┐
	// │              섹션 5: 형변환 (Type Conversion)            │
	// └─────────────────────────────────────────────────────────┘
	demonstrateTypeConversion()

	// ┌─────────────────────────────────────────────────────────┐
	// │              섹션 6: 연산자 (Operators)                  │
	// └─────────────────────────────────────────────────────────┘
	demonstrateOperators()

	// ┌─────────────────────────────────────────────────────────┐
	// │              섹션 7: 상수와 iota                         │
	// └─────────────────────────────────────────────────────────┘
	demonstrateConstants()

	// ┌─────────────────────────────────────────────────────────┐
	// │              섹션 8: 문자열 다루기                        │
	// └─────────────────────────────────────────────────────────┘
	demonstrateStrings()

	// ┌─────────────────────────────────────────────────────────┐
	// │              섹션 9: 사용자 입력받기                      │
	// └─────────────────────────────────────────────────────────┘
	demonstrateInput()
}

// ══════════════════════════════════════════════════════════════
// 섹션 1: 화면에 글자 출력하기
// ══════════════════════════════════════════════════════════════
func demonstratePrinting() {
	fmt.Println("╔═══════════════════════════════════════════════╗")
	fmt.Println("║        섹션 1: 화면에 글자 출력하기             ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// fmt.Println: Print + line의 줄임말이에요.
	// 글자를 출력하고 자동으로 줄바꿈을 해줘요.
	// 마치 공책에 글씨를 쓰고 다음 줄로 넘어가는 것처럼!
	fmt.Println("안녕하세요, Go 세계에 오신 것을 환영해요!")
	fmt.Println("저는", AppName, "입니다.")

	// fmt.Print: 줄바꿈 없이 출력해요.
	// 마치 같은 줄에 계속 글씨를 쓰는 것처럼!
	fmt.Print("이것은 ")
	fmt.Print("같은 줄에 ")
	fmt.Print("출력돼요.\n") // \n은 줄바꿈 문자예요

	// fmt.Printf: 형식을 지정해서 출력해요.
	// %s는 문자열, %d는 정수, %f는 소수점 숫자, %v는 뭐든지 OK!
	// 마치 빈칸 채우기 문제처럼 %자리에 값이 들어가요.
	fmt.Printf("앱 이름: %s, 버전: %s\n", AppName, AppVersion)
	fmt.Printf("최고 점수: %d점\n", MaxScore)
	fmt.Printf("원주율: %.4f\n", math.Pi) // 소수점 4자리까지 출력

	// fmt.Sprintf: 화면에 출력하지 않고 문자열로 만들어요.
	// s는 string(문자열)을 의미해요.
	message := fmt.Sprintf("버전 %s 프로그램이 시작되었어요!", AppVersion)
	fmt.Println(message)

	fmt.Println() // 빈 줄 출력
}

// ══════════════════════════════════════════════════════════════
// 섹션 2: 변수 선언과 사용
// ══════════════════════════════════════════════════════════════
func demonstrateVariables() {
	fmt.Println("╔═══════════════════════════════════════════════╗")
	fmt.Println("║           섹션 2: 변수 선언과 사용              ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// 변수(Variable)는 값을 저장하는 상자예요!
	// 마치 이름이 적힌 서랍장처럼, 변수 이름으로 값을 꺼내 쓸 수 있어요.

	// 방법 1: var 키워드로 선언 (타입을 직접 명시)
	// var 변수이름 자료형 = 값
	var studentName string = "김철수"
	var studentAge int = 10
	var studentScore float64 = 95.5
	var isHappy bool = true

	fmt.Printf("이름: %s, 나이: %d세, 점수: %.1f점, 행복함: %t\n",
		studentName, studentAge, studentScore, isHappy)

	// 방법 2: var로 선언하고 나중에 값 넣기
	// 타입을 쓰면 Go가 자동으로 "제로값"을 넣어줘요
	var favoriteColor string // "" (빈 문자열)
	var luckyNumber int      // 0
	favoriteColor = "파란색"
	luckyNumber = 7
	fmt.Printf("좋아하는 색: %s, 행운의 숫자: %d\n", favoriteColor, luckyNumber)

	// 방법 3: := (짧은 선언) - Go에서 가장 많이 사용하는 방법!
	// := 는 "선언하고 동시에 값을 넣는다"는 의미예요.
	// Go가 값을 보고 타입을 자동으로 알아내요 (타입 추론!)
	// 마치 선생님이 학생 얼굴을 보고 "아, 이 학생이구나!" 하는 것처럼요.
	city := "서울"           // string으로 자동 추론
	population := 9700000   // int로 자동 추론
	temperature := 23.5     // float64로 자동 추론
	isCapital := true       // bool로 자동 추론

	fmt.Printf("도시: %s, 인구: %d명, 기온: %.1f도, 수도: %t\n",
		city, population, temperature, isCapital)

	// 방법 4: 여러 변수를 한 번에 선언
	var (
		x int     = 10
		y float64 = 20.5
		z string  = "안녕"
	)
	fmt.Printf("x=%d, y=%.1f, z=%s\n", x, y, z)

	// 방법 5: 여러 변수를 한 줄에 선언
	a, b, c := 1, 2, 3
	fmt.Printf("a=%d, b=%d, c=%d\n", a, b, c)

	// 값 교환 (Go의 멋진 기능!)
	// 다른 언어에서는 임시 변수가 필요하지만, Go는 이렇게 간단해요!
	a, b = b, a
	fmt.Printf("값 교환 후: a=%d, b=%d\n", a, b)

	// 사용하지 않는 변수 (_로 무시)
	// Go는 선언한 변수를 사용하지 않으면 오류가 나요!
	// 하지만 _를 쓰면 "이 값은 필요 없어요"라고 알릴 수 있어요.
	result1, _ := strconv.Atoi("42") // 두 번째 반환값(에러)은 무시
	fmt.Printf("문자열 '42'를 숫자로 변환: %d\n", result1)

	fmt.Println()
}

// ══════════════════════════════════════════════════════════════
// 섹션 3: 제로값 (Zero Values) - Go의 중요한 특징!
// ══════════════════════════════════════════════════════════════
func demonstrateZeroValues() {
	fmt.Println("╔═══════════════════════════════════════════════╗")
	fmt.Println("║     섹션 3: 제로값 (Go의 특별한 기능!)          ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// 제로값이란? 변수를 선언만 하고 값을 넣지 않았을 때,
	// Go가 자동으로 넣어주는 기본값이에요!
	//
	// 마치 새 공책을 사면 빈 페이지가 있는 것처럼,
	// 새로운 변수를 만들면 Go가 자동으로 빈 값을 채워줘요.
	//
	// 이것이 중요한 이유: 다른 언어(C, Java)는 초기화 안 하면
	// 이상한 쓰레기값이 들어있을 수 있어요. Go는 항상 안전!

	var i int         // 정수의 제로값 = 0
	var f float64     // 소수의 제로값 = 0.0
	var s string      // 문자열의 제로값 = "" (빈 문자열)
	var b bool        // 불리언의 제로값 = false
	var p *int        // 포인터의 제로값 = nil (아무것도 없음)
	var slice []int   // 슬라이스의 제로값 = nil
	var m map[string]int // 맵의 제로값 = nil

	fmt.Println("┌─────────────────────────────────────────┐")
	fmt.Println("│          각 타입의 제로값                 │")
	fmt.Println("├─────────────────────────────────────────┤")
	fmt.Printf("│ int의 제로값:     %d (숫자는 0으로 시작!)       │\n", i)
	fmt.Printf("│ float64의 제로값: %.1f (소수도 0으로 시작!)     │\n", f)
	fmt.Printf("│ string의 제로값:  '%s' (문자열은 빈칸!)         │\n", s)
	fmt.Printf("│ bool의 제로값:    %t (불리언은 거짓으로 시작!) │\n", b)
	fmt.Printf("│ *int의 제로값:    %v (포인터는 nil!)           │\n", p)
	fmt.Printf("│ []int의 제로값:   %v (슬라이스는 nil!)         │\n", slice)
	fmt.Printf("│ map의 제로값:     %v (맵은 nil!)               │\n", m)
	fmt.Println("└─────────────────────────────────────────┘")

	// nil 체크 방법
	if slice == nil {
		fmt.Println("슬라이스가 nil이에요! 아직 사용 준비가 안 됐어요.")
	}

	// nil 슬라이스에 append는 가능해요 (Go의 친절한 기능!)
	slice = append(slice, 1, 2, 3)
	fmt.Printf("append 후 슬라이스: %v\n", slice)

	fmt.Println()
}

// ══════════════════════════════════════════════════════════════
// 섹션 4: 자료형 (Data Types)
// ══════════════════════════════════════════════════════════════
func demonstrateDataTypes() {
	fmt.Println("╔═══════════════════════════════════════════════╗")
	fmt.Println("║           섹션 4: 자료형 (Data Types)           ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// ── 정수형 (Integer Types) ──
	// 정수는 소수점 없는 숫자예요. 1, 2, 3, -5, 100 같은 숫자들이죠!
	fmt.Println("\n[정수형]")

	var int8Val int8 = 127           // -128 ~ 127 (1바이트)
	var int16Val int16 = 32767       // -32768 ~ 32767 (2바이트)
	var int32Val int32 = 2147483647  // 약 -21억 ~ 21억 (4바이트)
	var int64Val int64 = 9223372036854775807 // 아주 큰 숫자 (8바이트)
	var intVal int = 42              // 컴퓨터 시스템에 맞게 자동 (보통 64비트)
	var uintVal uint = 100           // 음수 없는 정수 (0 이상만)

	fmt.Printf("int8 (작은 정수): %d\n", int8Val)
	fmt.Printf("int16 (중간 정수): %d\n", int16Val)
	fmt.Printf("int32 (보통 정수): %d\n", int32Val)
	fmt.Printf("int64 (큰 정수): %d\n", int64Val)
	fmt.Printf("int (기본 정수): %d\n", intVal)
	fmt.Printf("uint (양수만): %d\n", uintVal)

	// ── 소수형 (Floating-Point Types) ──
	// 소수점이 있는 숫자예요. 3.14, -2.5, 100.0 같은 숫자들이죠!
	fmt.Println("\n[소수형]")

	var float32Val float32 = 3.14    // 소수점 약 7자리 정밀도
	var float64Val float64 = 3.14159265358979 // 소수점 약 15자리 정밀도

	fmt.Printf("float32 (덜 정밀한 소수): %.7f\n", float32Val)
	fmt.Printf("float64 (더 정밀한 소수): %.15f\n", float64Val)
	fmt.Printf("원주율 π: %f\n", math.Pi)

	// ── 복소수형 (Complex Types) - 수학에서 쓰는 복소수예요
	fmt.Println("\n[복소수형]")
	var complexVal complex128 = 3 + 4i
	fmt.Printf("복소수: %v (실수부: %.0f, 허수부: %.0f)\n",
		complexVal, real(complexVal), imag(complexVal))

	// ── 문자열 (String) ──
	// 문자들의 모음이에요. "안녕", "Hello", "123" 모두 문자열이에요!
	// 마치 구슬을 실에 꿰어 놓은 것처럼, 글자들이 이어져 있어요.
	fmt.Println("\n[문자열]")

	name := "김민준"
	greeting := "안녕하세요!"
	multiLine := `여러 줄로
쓸 수 있는
문자열이에요!`  // 백틱(`)을 쓰면 여러 줄 문자열을 만들 수 있어요

	fmt.Printf("이름: %s\n", name)
	fmt.Printf("인사: %s\n", greeting)
	fmt.Printf("여러줄 문자열:\n%s\n", multiLine)

	// 문자열 길이 (바이트 수)
	fmt.Printf("'%s'의 길이: %d바이트\n", name, len(name))
	// 한글은 한 글자가 3바이트! 영어는 1바이트예요.

	// ── 불리언 (Boolean) ──
	// 참(true) 또는 거짓(false) 두 가지 값만 가질 수 있어요.
	// 마치 전등 스위치처럼 켜짐/꺼짐 두 가지만 있어요!
	fmt.Println("\n[불리언]")

	isStudent := true
	isTeacher := false
	isAdult := false

	fmt.Printf("학생인가요? %t\n", isStudent)
	fmt.Printf("선생님인가요? %t\n", isTeacher)
	fmt.Printf("성인인가요? %t\n", isAdult)
	fmt.Printf("학생이고 선생님인가요? %t\n", isStudent && isTeacher) // AND
	fmt.Printf("학생이거나 선생님인가요? %t\n", isStudent || isTeacher) // OR
	fmt.Printf("학생이 아닌가요? %t\n", !isStudent)                 // NOT

	// ── 바이트와 룬 (byte and rune) ──
	// byte는 uint8과 같아요 - 컴퓨터가 기억하는 가장 작은 단위
	// rune은 int32와 같아요 - 유니코드 문자 하나를 저장해요
	fmt.Println("\n[바이트와 룬]")

	var myByte byte = 'A'   // ASCII 코드: 65
	var myRune rune = '한'   // 유니코드 코드포인트

	fmt.Printf("byte 'A': %c (숫자로는 %d)\n", myByte, myByte)
	fmt.Printf("rune '한': %c (유니코드: %d)\n", myRune, myRune)

	fmt.Println()
}

// ══════════════════════════════════════════════════════════════
// 섹션 5: 형변환 (Type Conversion)
// ══════════════════════════════════════════════════════════════
func demonstrateTypeConversion() {
	fmt.Println("╔═══════════════════════════════════════════════╗")
	fmt.Println("║          섹션 5: 형변환 (Type Conversion)       ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// Go는 형변환을 자동으로 해주지 않아요!
	// 이것이 중요한 이유: 실수로 다른 타입끼리 계산하는 것을 방지해요.
	// 마치 원화와 달러를 헷갈리지 않도록 명확하게 표시하는 것처럼요.
	//
	// 다른 언어: int + float = float (자동 변환)
	// Go: int + float = 오류! 직접 변환해야 해요.

	// 숫자 형변환
	var i int = 42
	var f float64 = float64(i) // int → float64 변환
	var u uint = uint(f)       // float64 → uint 변환

	fmt.Printf("int %d → float64 %.1f → uint %d\n", i, f, u)

	// 주의! 큰 값을 작은 타입으로 변환하면 잘릴 수 있어요
	var big int = 300
	var small int8 = int8(big) // 300은 int8 범위(-128~127) 초과!
	fmt.Printf("300을 int8으로 변환: %d (값이 잘렸어요!)\n", small)

	// 문자열 ↔ 숫자 변환 (strconv 패키지 사용)
	// strconv = string + convert의 줄임말이에요

	// 숫자 → 문자열
	numStr := strconv.Itoa(42)      // Itoa = Integer to ASCII
	fmt.Printf("42를 문자열로: '%s'\n", numStr)

	floatStr := strconv.FormatFloat(3.14, 'f', 2, 64)
	fmt.Printf("3.14를 문자열로: '%s'\n", floatStr)

	// 문자열 → 숫자
	// Atoi는 에러도 반환해요! (Go의 특징: 에러를 명시적으로 처리)
	// 에러 처리는 뒤에서 자세히 배울 거예요~
	num, err := strconv.Atoi("123")
	if err != nil { // nil은 "에러 없음"을 의미해요
		fmt.Println("변환 실패:", err)
	} else {
		fmt.Printf("'123'을 숫자로: %d\n", num)
	}

	// 잘못된 변환 시도
	_, err = strconv.Atoi("abc")
	if err != nil {
		fmt.Println("'abc'를 숫자로 변환 실패 (당연해요!):", err)
	}

	// 문자열 ↔ 불리언 변환
	boolVal, _ := strconv.ParseBool("true")
	fmt.Printf("'true' 문자열을 bool로: %t\n", boolVal)

	fmt.Println()
}

// ══════════════════════════════════════════════════════════════
// 섹션 6: 연산자 (Operators)
// ══════════════════════════════════════════════════════════════
func demonstrateOperators() {
	fmt.Println("╔═══════════════════════════════════════════════╗")
	fmt.Println("║           섹션 6: 연산자 (Operators)            ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// ── 산술 연산자 ──
	// 마치 초등학교 수학처럼 더하기, 빼기, 곱하기, 나누기를 해요!
	fmt.Println("\n[산술 연산자]")

	a, b := 17, 5

	fmt.Printf("%d + %d = %d\n", a, b, a+b)   // 더하기
	fmt.Printf("%d - %d = %d\n", a, b, a-b)   // 빼기
	fmt.Printf("%d × %d = %d\n", a, b, a*b)   // 곱하기
	fmt.Printf("%d ÷ %d = %d\n", a, b, a/b)   // 나누기 (정수÷정수 = 정수, 소수점 버림!)
	fmt.Printf("%d %% %d = %d\n", a, b, a%b)  // 나머지 (17을 5로 나누면 나머지 2)

	// 소수점 나누기를 원하면 float64로 변환해야 해요!
	fmt.Printf("%.2f ÷ %.2f = %.2f\n",
		float64(a), float64(b), float64(a)/float64(b))

	// ── 비교 연산자 ──
	// 두 값을 비교해서 참/거짓을 돌려줘요.
	fmt.Println("\n[비교 연산자]")

	x, y := 10, 20

	fmt.Printf("%d == %d : %t (같나요?)\n", x, y, x == y)
	fmt.Printf("%d != %d : %t (다른가요?)\n", x, y, x != y)
	fmt.Printf("%d < %d : %t (작은가요?)\n", x, y, x < y)
	fmt.Printf("%d > %d : %t (큰가요?)\n", x, y, x > y)
	fmt.Printf("%d <= %d : %t (작거나 같나요?)\n", x, y, x <= y)
	fmt.Printf("%d >= %d : %t (크거나 같나요?)\n", x, y, x >= y)

	// ── 논리 연산자 ──
	// 참/거짓 값들을 조합해요.
	fmt.Println("\n[논리 연산자]")

	isRaining := true
	hasUmbrella := false

	fmt.Printf("비가 오나요? %t\n", isRaining)
	fmt.Printf("우산이 있나요? %t\n", hasUmbrella)
	fmt.Printf("비 오고 우산 있음 (&&): %t\n", isRaining && hasUmbrella) // 둘 다 참일 때만 참
	fmt.Printf("비 오거나 우산 있음 (||): %t\n", isRaining || hasUmbrella) // 하나라도 참이면 참
	fmt.Printf("비 안 옴 (!): %t\n", !isRaining)                       // 반대!

	// ── 대입 연산자 ──
	// 계산하고 바로 저장하는 편리한 방법이에요!
	fmt.Println("\n[대입 연산자]")

	score := 100
	fmt.Printf("시작 점수: %d\n", score)

	score += 10 // score = score + 10 과 같아요
	fmt.Printf("+10 후: %d\n", score)

	score -= 20 // score = score - 20 과 같아요
	fmt.Printf("-20 후: %d\n", score)

	score *= 2 // score = score * 2 와 같아요
	fmt.Printf("×2 후: %d\n", score)

	score /= 3 // score = score / 3 과 같아요
	fmt.Printf("÷3 후: %d\n", score)

	score %= 7 // score = score % 7 과 같아요
	fmt.Printf("%%7 후: %d\n", score)

	// ++ 와 -- 연산자
	count := 5
	count++ // count = count + 1 과 같아요
	fmt.Printf("count++: %d\n", count)
	count-- // count = count - 1 과 같아요
	fmt.Printf("count--: %d\n", count)

	// 주의: Go에서 ++와 --는 문장(statement)이에요.
	// 다른 언어처럼 표현식(expression)이 아니에요!
	// 그래서 i := count++ 이런 코드는 Go에서 오류예요.

	// ── 비트 연산자 ──
	// 이진수(0과 1)로 계산하는 연산자예요. (조금 어려운 내용)
	fmt.Println("\n[비트 연산자]")

	p, q := 0b1010, 0b1100 // 이진수: 10, 12
	fmt.Printf("p = %04b (%d)\n", p, p)
	fmt.Printf("q = %04b (%d)\n", q, q)
	fmt.Printf("p & q = %04b (%d) - AND: 둘 다 1인 자리\n", p&q, p&q)
	fmt.Printf("p | q = %04b (%d) - OR: 하나라도 1인 자리\n", p|q, p|q)
	fmt.Printf("p ^ q = %04b (%d) - XOR: 하나만 1인 자리\n", p^q, p^q)
	fmt.Printf("p << 1 = %04b (%d) - 왼쪽으로 1칸 이동 (×2)\n", p<<1, p<<1)
	fmt.Printf("p >> 1 = %04b (%d) - 오른쪽으로 1칸 이동 (÷2)\n", p>>1, p>>1)

	// 권한 비트 플래그 활용 예시
	fmt.Println("\n[권한 플래그 활용 예시]")
	myPermissions := ReadPermission | WritePermission // 읽기 + 쓰기 권한
	fmt.Printf("내 권한: %d\n", myPermissions)
	fmt.Printf("읽기 권한 있음? %t\n", myPermissions&ReadPermission != 0)
	fmt.Printf("실행 권한 있음? %t\n", myPermissions&ExecPermission != 0)

	fmt.Println()
}

// ══════════════════════════════════════════════════════════════
// 섹션 7: 상수와 iota
// ══════════════════════════════════════════════════════════════
func demonstrateConstants() {
	fmt.Println("╔═══════════════════════════════════════════════╗")
	fmt.Println("║           섹션 7: 상수와 iota                   ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// 상수는 변수와 달리 한번 정해지면 절대 바꿀 수 없어요.
	fmt.Printf("앱 이름: %s\n", AppName)
	fmt.Printf("앱 버전: %s\n", AppVersion)

	// iota로 만든 요일 상수 사용
	fmt.Println("\n[요일 상수 (iota 사용)]")
	days := []string{"월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"}
	fmt.Printf("월요일의 값: %d\n", Monday)
	fmt.Printf("금요일의 값: %d\n", Friday)
	fmt.Printf("3번째 요일: %s\n", days[Wednesday])

	// iota로 컴퓨터 용량 단위 만들기
	const (
		_           = iota       // 첫 번째 값(0) 버리기
		KB ByteSize = 1 << (10 * iota) // 1 << 10 = 1024
		MB                      // 1 << 20
		GB                      // 1 << 30
		TB                      // 1 << 40
	)

	type ByteSize float64

	fmt.Println("\n[용량 단위 (iota 활용)]")
	fmt.Printf("1 KB = %d 바이트\n", 1<<10)
	fmt.Printf("1 MB = %d 바이트\n", 1<<20)
	fmt.Printf("1 GB = %d 바이트\n", 1<<30)

	fmt.Println()
}

// ══════════════════════════════════════════════════════════════
// 섹션 8: 문자열 다루기
// ══════════════════════════════════════════════════════════════
func demonstrateStrings() {
	fmt.Println("╔═══════════════════════════════════════════════╗")
	fmt.Println("║           섹션 8: 문자열 다루기                  ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	sentence := "Hello, Go 세계에 오신 것을 환영합니다!"

	// 문자열 길이
	fmt.Printf("문장: %s\n", sentence)
	fmt.Printf("바이트 길이: %d\n", len(sentence))

	// strings 패키지 활용
	fmt.Println("\n[strings 패키지 활용]")

	original := "  안녕하세요, Go 언어!  "
	fmt.Printf("원본: '%s'\n", original)
	fmt.Printf("공백 제거: '%s'\n", strings.TrimSpace(original))
	fmt.Printf("대문자: '%s'\n", strings.ToUpper("hello"))
	fmt.Printf("소문자: '%s'\n", strings.ToLower("HELLO"))
	fmt.Printf("포함 여부: %t\n", strings.Contains(original, "Go"))
	fmt.Printf("시작 여부: %t\n", strings.HasPrefix(strings.TrimSpace(original), "안녕"))
	fmt.Printf("끝 여부: %t\n", strings.HasSuffix(strings.TrimSpace(original), "언어!"))
	fmt.Printf("교체: '%s'\n", strings.Replace(original, "Go", "Golang", 1))
	fmt.Printf("분리: %v\n", strings.Split("a,b,c,d", ","))
	fmt.Printf("합치기: '%s'\n", strings.Join([]string{"가", "나", "다"}, "-"))

	// 문자열은 변경 불가능해요! (immutable)
	// 수정하려면 새 문자열을 만들어야 해요.
	// 많은 변경이 필요하면 strings.Builder를 사용해요.
	fmt.Println("\n[strings.Builder 사용 (효율적인 문자열 조립)]")
	var sb strings.Builder
	for i := 1; i <= 5; i++ {
		sb.WriteString(fmt.Sprintf("항목%d ", i))
	}
	result := sb.String()
	fmt.Printf("조립된 문자열: %s\n", result)

	// 문자열 순회 (한글 처리!)
	fmt.Println("\n[문자열 순회]")
	korean := "안녕Go"
	fmt.Printf("문자열: %s\n", korean)
	for i, r := range korean {
		fmt.Printf("  인덱스 %d: '%c' (유니코드: %d)\n", i, r, r)
	}

	fmt.Println()
}

// ══════════════════════════════════════════════════════════════
// 섹션 9: 사용자 입력 받기
// ══════════════════════════════════════════════════════════════
func demonstrateInput() {
	fmt.Println("╔═══════════════════════════════════════════════╗")
	fmt.Println("║           섹션 9: 사용자 입력 받기               ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// 방법 1: fmt.Scan - 공백으로 구분된 값 읽기
	// (지금은 자동으로 테스트하기 위해 주석 처리했어요)
	/*
		var name string
		var age int
		fmt.Print("이름과 나이를 입력하세요 (예: 김철수 10): ")
		fmt.Scan(&name, &age) // & 는 변수의 주소를 넘기는 포인터예요
		fmt.Printf("안녕하세요, %s님! %d살이시군요!\n", name, age)
	*/

	// 방법 2: bufio.Scanner - 한 줄 전체 읽기 (한글 입력에 좋아요)
	fmt.Println("\n[bufio.Scanner 사용 예시 - 실제로는 직접 입력해야 해요]")
	fmt.Println("아래는 입력받는 코드의 예시예요:")
	fmt.Println(`
	scanner := bufio.NewScanner(os.Stdin)
	fmt.Print("이름을 입력하세요: ")
	scanner.Scan()
	name := scanner.Text()
	fmt.Printf("안녕하세요, %s님!\n", name)
	`)

	// 실제로 표준 입력이 있을 경우에만 읽기
	// 여기서는 데모용으로 미리 정해진 값을 사용해요
	scanner := bufio.NewScanner(strings.NewReader("김민준\n10\n"))

	fmt.Print("이름을 입력하세요: ")
	scanner.Scan()
	demoName := scanner.Text()

	fmt.Print("나이를 입력하세요: ")
	scanner.Scan()
	demoAge := scanner.Text()

	fmt.Printf("입력된 이름: %s\n", demoName)
	fmt.Printf("입력된 나이: %s\n", demoAge)

	age, err := strconv.Atoi(demoAge)
	if err != nil {
		fmt.Println("나이를 숫자로 변환할 수 없어요!")
	} else {
		fmt.Printf("10년 후 나이: %d\n", age+10)
	}

	// os.Stdin을 직접 사용하는 예시
	fmt.Println("\n[os 패키지로 프로그램 정보 출력]")
	fmt.Printf("실행 파일 경로: %s\n", os.Args[0])
	fmt.Printf("전달된 인수 개수: %d\n", len(os.Args)-1)

	fmt.Println()
	fmt.Println("╔═══════════════════════════════════════════════╗")
	fmt.Println("║   🎉 01단계 기초 학습 완료! 수고했어요!         ║")
	fmt.Println("║   다음: 02_control_flow 로 이동하세요!          ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")
}

// ByteSize는 demonstrateConstants 함수 내부의 지역 타입 충돌 방지용
type ByteSize = float64
