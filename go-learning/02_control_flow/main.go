/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Go 학습 02단계: 흐름 제어
  ─ if/else, switch, for 반복문 ─

  프로그램은 위에서 아래로 순서대로 실행되지만,
  흐름 제어를 사용하면 조건에 따라 다른 길로 갈 수 있어요!
  마치 미로에서 갈림길을 만나는 것처럼요.

  ■ 실행 방법: go run main.go

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/
package main

import (
	"fmt"
	"math/rand"
)

func main() {
	fmt.Println("╔═══════════════════════════════════════════════╗")
	fmt.Println("║     Go 02단계: 흐름 제어 (Control Flow)         ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	demonstrateIf()
	demonstrateSwitch()
	demonstrateFor()
	demonstrateBreakContinue()
	demonstrateGoto()
	practiceProject()
}

// ══════════════════════════════════════════════════════════════
// 섹션 1: if / else 조건문
// ══════════════════════════════════════════════════════════════
func demonstrateIf() {
	fmt.Println("\n╔═══════════════════════════════════════════════╗")
	fmt.Println("║         섹션 1: if / else 조건문                ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// if 문: "만약 ~하다면" 이라는 의미예요.
	// 마치 "만약 비가 온다면 우산을 가져가라"처럼요!
	//
	// Go의 if 문 특징:
	// 1. 조건에 괄호()가 없어요! (다른 언어와 달리)
	//    C/Java: if (score >= 90) { ... }
	//    Go:     if score >= 90  { ... }
	// 2. 중괄호 { } 는 반드시 있어야 해요.
	//    Go: if score >= 90 { ... } // OK
	//    Go: if score >= 90 return  // 오류! 중괄호 필수

	score := 85

	fmt.Printf("\n점수: %d\n", score)

	// 기본 if/else if/else 구조
	if score >= 90 {
		fmt.Println("등급: A (아주 잘했어요!)")
	} else if score >= 80 {
		fmt.Println("등급: B (잘했어요!)")
	} else if score >= 70 {
		fmt.Println("등급: C (괜찮아요!)")
	} else if score >= 60 {
		fmt.Println("등급: D (조금 더 노력해요!)")
	} else {
		fmt.Println("등급: F (많이 노력해야 해요!)")
	}

	// ── Go 특유의 if 초기화 문 ──
	// if 조건을 검사하기 전에 변수를 초기화할 수 있어요!
	// 문법: if 초기화문; 조건 { ... }
	//
	// 이 기능의 장점: 변수의 범위(scope)가 if 블록 안으로만 제한돼요.
	// 마치 수업 시간에만 쓰는 공책처럼, 수업 끝나면 사라져요!

	fmt.Println("\n[if 초기화 문 예시]")

	// rand.Intn(100)은 0~99 사이의 랜덤 숫자를 만들어요
	if randomScore := rand.Intn(100); randomScore >= 60 {
		fmt.Printf("랜덤 점수 %d: 합격!\n", randomScore)
	} else {
		fmt.Printf("랜덤 점수 %d: 불합격...\n", randomScore)
	}
	// randomScore 변수는 여기서 사용할 수 없어요 (범위 밖)

	// 에러 처리에서 자주 쓰는 패턴
	// err 변수를 if 문 안에서 바로 선언하고 처리해요
	fmt.Println("\n[에러 처리 패턴]")

	if val, err := divide(10, 3); err != nil {
		fmt.Println("오류:", err)
	} else {
		fmt.Printf("10 ÷ 3 = %.2f\n", val)
	}

	if _, err := divide(10, 0); err != nil {
		fmt.Println("0으로 나누기 시도:", err)
	}

	// ── 중첩 if 문 ──
	// if 안에 또 if를 넣을 수 있어요.
	// 하지만 너무 깊게 중첩하면 읽기 어려워지니 주의해요!
	fmt.Println("\n[중첩 if 문]")

	age := 15
	hasTicket := true

	if age >= 12 {
		if hasTicket {
			fmt.Printf("나이 %d, 티켓 있음: 입장 가능!\n", age)
		} else {
			fmt.Printf("나이 %d, 티켓 없음: 티켓을 구입하세요!\n", age)
		}
	} else {
		fmt.Printf("나이 %d: 12세 미만은 보호자와 함께 오세요!\n", age)
	}

	// ── Go 스타일: 일찍 반환 (Early Return) ──
	// Go에서는 중첩을 줄이기 위해 조건이 맞지 않으면 일찍 반환해요.
	// 마치 입구에서 먼저 검사하고, 통과 못하면 바로 돌려보내는 것처럼!
	fmt.Println("\n[Early Return 패턴]")

	checkAge(8)
	checkAge(12)
	checkAge(18)

	fmt.Println()
}

// divide: 나누기 함수 (에러 반환 예시)
// Go의 특징: 에러를 예외(exception)가 아닌 반환값으로 처리해요!
func divide(a, b float64) (float64, error) {
	if b == 0 {
		return 0, fmt.Errorf("0으로 나눌 수 없어요!")
	}
	return a / b, nil
}

// checkAge: Early Return 패턴 예시
func checkAge(age int) {
	// 조건에 맞지 않으면 바로 반환 → 중첩 줄이기
	if age < 12 {
		fmt.Printf("나이 %d: 어린이 구역입니다.\n", age)
		return
	}
	if age < 18 {
		fmt.Printf("나이 %d: 청소년 구역입니다.\n", age)
		return
	}
	fmt.Printf("나이 %d: 성인 구역입니다.\n", age)
}

// ══════════════════════════════════════════════════════════════
// 섹션 2: switch 문
// ══════════════════════════════════════════════════════════════
func demonstrateSwitch() {
	fmt.Println("\n╔═══════════════════════════════════════════════╗")
	fmt.Println("║           섹션 2: switch 문                     ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// switch 문은 여러 경우 중 하나를 선택할 때 사용해요.
	// 마치 메뉴판에서 음식을 고르는 것처럼요!
	//
	// Go의 switch 특징:
	// 1. case 끝에 break가 필요 없어요! (다른 언어와 달리)
	//    자동으로 break가 적용돼요.
	// 2. case에 여러 값을 쓸 수 있어요.
	// 3. 조건 없는 switch도 쓸 수 있어요. (if-else 대신!)
	// 4. fallthrough로 다음 case도 실행할 수 있어요.

	day := "수요일"
	fmt.Printf("\n오늘은 %s예요.\n", day)

	// 기본 switch 문
	switch day {
	case "월요일":
		fmt.Println("한 주의 시작! 화이팅!")
	case "화요일":
		fmt.Println("여전히 초반이에요.")
	case "수요일":
		fmt.Println("한 주의 중간! 잘 하고 있어요!")
	case "목요일":
		fmt.Println("거의 다 왔어요!")
	case "금요일":
		fmt.Println("내일은 주말이에요!")
	case "토요일", "일요일": // 여러 값을 한 case에 쓸 수 있어요!
		fmt.Println("주말이에요! 쉬어요~")
	default: // 어느 case에도 해당 안 되면 실행돼요
		fmt.Println("알 수 없는 요일이에요.")
	}

	// ── 조건 없는 switch ──
	// switch 뒤에 값을 쓰지 않으면 if-else처럼 사용할 수 있어요!
	// 이렇게 하면 코드가 더 읽기 쉬워져요.
	fmt.Println("\n[조건 없는 switch (if-else 대체)]")

	hour := 14 // 오후 2시

	switch {
	case hour < 6:
		fmt.Printf("%d시: 새벽이에요. 자야 해요!\n", hour)
	case hour < 12:
		fmt.Printf("%d시: 오전이에요. 좋은 아침!\n", hour)
	case hour < 18:
		fmt.Printf("%d시: 오후예요. 점심 먹었나요?\n", hour)
	case hour < 22:
		fmt.Printf("%d시: 저녁이에요. 저녁 먹었나요?\n", hour)
	default:
		fmt.Printf("%d시: 밤이에요. 이제 자야겠죠?\n", hour)
	}

	// ── switch 초기화 문 ──
	// if 문처럼 switch도 초기화 문을 사용할 수 있어요!
	fmt.Println("\n[switch 초기화 문]")

	switch grade := getGrade(75); grade {
	case "A":
		fmt.Printf("등급 %s: 최고예요!\n", grade)
	case "B":
		fmt.Printf("등급 %s: 잘했어요!\n", grade)
	case "C":
		fmt.Printf("등급 %s: 보통이에요.\n", grade)
	default:
		fmt.Printf("등급 %s: 더 노력해요.\n", grade)
	}

	// ── fallthrough 키워드 ──
	// 보통 switch는 일치하는 case만 실행하지만,
	// fallthrough를 쓰면 다음 case도 계속 실행해요.
	// 마치 미끄럼틀처럼 아래로 쭉 내려가요!
	fmt.Println("\n[fallthrough 예시]")

	level := 2
	fmt.Printf("레벨 %d의 능력:\n", level)
	switch level {
	case 3:
		fmt.Println("  - 날기")
		fallthrough // 아래 case도 실행!
	case 2:
		fmt.Println("  - 달리기")
		fallthrough
	case 1:
		fmt.Println("  - 걷기")
	}

	// ── 타입 switch ──
	// 인터페이스 타입의 실제 타입을 확인할 때 사용해요.
	// (인터페이스는 06단계에서 자세히 배울 거예요)
	fmt.Println("\n[타입 switch]")

	values := []interface{}{42, "안녕", true, 3.14, nil}
	for _, v := range values {
		switch t := v.(type) {
		case int:
			fmt.Printf("정수: %d\n", t)
		case string:
			fmt.Printf("문자열: '%s'\n", t)
		case bool:
			fmt.Printf("불리언: %t\n", t)
		case float64:
			fmt.Printf("소수: %.2f\n", t)
		case nil:
			fmt.Println("nil 값")
		default:
			fmt.Printf("알 수 없는 타입: %T\n", t)
		}
	}

	fmt.Println()
}

// getGrade: 점수를 받아서 등급 문자를 반환
func getGrade(score int) string {
	switch {
	case score >= 90:
		return "A"
	case score >= 80:
		return "B"
	case score >= 70:
		return "C"
	case score >= 60:
		return "D"
	default:
		return "F"
	}
}

// ══════════════════════════════════════════════════════════════
// 섹션 3: for 반복문
// ══════════════════════════════════════════════════════════════
func demonstrateFor() {
	fmt.Println("\n╔═══════════════════════════════════════════════╗")
	fmt.Println("║           섹션 3: for 반복문                    ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// Go에는 반복문이 for 하나뿐이에요!
	// 다른 언어는 while, do-while, for 등 여러 종류가 있지만,
	// Go는 for 하나로 모든 반복을 처리해요.
	// 단순하고 배우기 쉽죠!

	// ── 방법 1: 기본 for 문 (C 스타일) ──
	// for 초기화; 조건; 후처리 { ... }
	// 마치 "1부터 5까지 세어봐요!" 같은 것이에요.
	fmt.Println("\n[기본 for 문: 1부터 5까지]")
	for i := 1; i <= 5; i++ {
		fmt.Printf("  %d ", i)
	}
	fmt.Println()

	// 구구단 출력
	fmt.Println("\n[구구단 3단]")
	for i := 1; i <= 9; i++ {
		fmt.Printf("  3 × %d = %d\n", i, 3*i)
	}

	// ── 방법 2: while처럼 사용 (조건만 있는 for) ──
	// Go에는 while이 없어요! 대신 for를 이렇게 써요.
	// 마치 "배가 부를 때까지 밥을 먹어요!" 같은 것이에요.
	fmt.Println("\n[while 처럼 사용]")
	count := 1
	for count <= 5 {
		fmt.Printf("  카운트: %d\n", count)
		count++
	}

	// ── 방법 3: 무한 루프 (Infinite Loop) ──
	// for {} 는 영원히 실행되는 반복문이에요.
	// break로 빠져나올 수 있어요.
	// 마치 쳇바퀴처럼 계속 돌다가, 신호가 오면 멈추는 것처럼요!
	fmt.Println("\n[무한 루프 + break]")
	num := 1
	for {
		if num > 5 {
			break // "멈춰!" 라는 신호
		}
		fmt.Printf("  숫자: %d\n", num)
		num++
	}

	// ── 방법 4: range로 순회 ──
	// 배열, 슬라이스, 맵, 문자열, 채널을 순회할 때 사용해요.
	// range는 두 값을 반환해요: 인덱스(위치)와 값.
	// 마치 "첫 번째 항목은 사과, 두 번째 항목은 배나리, ..." 처럼요!
	fmt.Println("\n[range로 슬라이스 순회]")
	fruits := []string{"사과", "바나나", "체리", "포도", "망고"}
	for i, fruit := range fruits {
		fmt.Printf("  [%d] %s\n", i, fruit)
	}

	// 인덱스가 필요 없으면 _로 무시
	fmt.Println("\n[range: 값만 사용]")
	sum := 0
	numbers := []int{10, 20, 30, 40, 50}
	for _, n := range numbers {
		sum += n
	}
	fmt.Printf("  합계: %d\n", sum)

	// range로 맵 순회 (순서는 보장되지 않아요!)
	fmt.Println("\n[range로 맵 순회]")
	scores := map[string]int{
		"김철수": 90,
		"이영희": 85,
		"박민준": 92,
	}
	for name, s := range scores {
		fmt.Printf("  %s: %d점\n", name, s)
	}

	// range로 문자열 순회 (rune 단위로 처리!)
	fmt.Println("\n[range로 문자열 순회]")
	for i, ch := range "Go언어" {
		fmt.Printf("  인덱스 %d: '%c'\n", i, ch)
	}

	// ── 중첩 반복문 ──
	// 반복문 안에 반복문을 쓸 수 있어요.
	// 마치 서랍장의 각 서랍 안에 또 작은 서랍이 있는 것처럼요!
	fmt.Println("\n[별 그리기 (중첩 반복문)]")
	for row := 1; row <= 5; row++ {
		for col := 1; col <= row; col++ {
			fmt.Print("★ ")
		}
		fmt.Println()
	}

	fmt.Println()
}

// ══════════════════════════════════════════════════════════════
// 섹션 4: break, continue, label
// ══════════════════════════════════════════════════════════════
func demonstrateBreakContinue() {
	fmt.Println("\n╔═══════════════════════════════════════════════╗")
	fmt.Println("║       섹션 4: break, continue, label            ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// break: 반복문을 완전히 멈추고 빠져나와요.
	// 마치 비상구를 통해 건물에서 나가는 것처럼요!
	fmt.Println("\n[break: 5 이상이면 멈추기]")
	for i := 1; i <= 10; i++ {
		if i >= 5 {
			fmt.Printf("  %d에서 멈춤!\n", i)
			break
		}
		fmt.Printf("  %d\n", i)
	}

	// continue: 현재 반복만 건너뛰고 다음 반복으로 가요.
	// 마치 줄넘기할 때 한 번 틀려도 계속 이어가는 것처럼!
	fmt.Println("\n[continue: 짝수만 출력]")
	for i := 1; i <= 10; i++ {
		if i%2 != 0 { // 홀수면 건너뜀
			continue
		}
		fmt.Printf("  %d (짝수)\n", i)
	}

	// ── 레이블(Label) ──
	// 중첩 반복문에서 바깥 반복문을 break/continue할 때 사용해요.
	// 마치 "2층 반복문에서 나가!"라고 직접 지정하는 것처럼요.
	fmt.Println("\n[레이블 break: 특정 위치 탈출]")

OuterLoop: // 레이블 이름은 뒤에 콜론(:)을 붙여요
	for row := 1; row <= 5; row++ {
		for col := 1; col <= 5; col++ {
			if row == 3 && col == 3 {
				fmt.Printf("  (%d,%d)에서 OuterLoop 탈출!\n", row, col)
				break OuterLoop // 레이블이 붙은 반복문까지 탈출!
			}
			fmt.Printf("  (%d,%d) ", row, col)
		}
		fmt.Println()
	}

	fmt.Println("\n[레이블 continue: 외부 반복 다음으로]")
Outer:
	for i := 1; i <= 3; i++ {
		for j := 1; j <= 3; j++ {
			if j == 2 {
				fmt.Printf("  i=%d, j=%d → 외부 루프 다음으로!\n", i, j)
				continue Outer // 외부 for i의 다음 반복으로!
			}
			fmt.Printf("  i=%d, j=%d\n", i, j)
		}
	}

	fmt.Println()
}

// ══════════════════════════════════════════════════════════════
// 섹션 5: goto 문
// ══════════════════════════════════════════════════════════════
func demonstrateGoto() {
	fmt.Println("\n╔═══════════════════════════════════════════════╗")
	fmt.Println("║           섹션 5: goto 문 (드물게 사용)          ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// goto: 코드의 특정 위치로 바로 점프해요.
	// 실제로는 거의 사용하지 않아요!
	// 코드가 읽기 어려워지기 때문이에요.
	// 마치 미로에서 벽을 통과해 원하는 곳으로 가는 것처럼
	// 편리해 보이지만, 어디로 갔는지 따라가기 어려워요.

	fmt.Println("goto 문 예시:")

	i := 0
loop: // 레이블 정의
	if i < 3 {
		fmt.Printf("  i = %d\n", i)
		i++
		goto loop // 레이블로 점프!
	}
	fmt.Println("goto로 만든 반복 완료")

	// 실제로 goto가 유용한 경우: 에러 처리에서 정리 코드로 점프
	// 하지만 Go에서는 defer가 더 좋은 방법이에요! (03단계에서 배워요)

	fmt.Println()
}

// ══════════════════════════════════════════════════════════════
// 섹션 6: 종합 실습 - 숫자 맞추기 게임
// ══════════════════════════════════════════════════════════════
func practiceProject() {
	fmt.Println("\n╔═══════════════════════════════════════════════╗")
	fmt.Println("║      섹션 6: 종합 실습 - 숫자 패턴 출력         ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// FizzBuzz: 프로그래밍 면접에서 자주 나오는 문제예요!
	// 1부터 30까지:
	// - 3의 배수면 "Fizz" 출력
	// - 5의 배수면 "Buzz" 출력
	// - 15의 배수면 "FizzBuzz" 출력
	// - 나머지는 숫자 출력
	fmt.Println("\n[FizzBuzz: 1~30]")
	for i := 1; i <= 30; i++ {
		switch {
		case i%15 == 0: // 15의 배수 먼저 체크!
			fmt.Printf("FizzBuzz ")
		case i%3 == 0:
			fmt.Printf("Fizz ")
		case i%5 == 0:
			fmt.Printf("Buzz ")
		default:
			fmt.Printf("%d ", i)
		}
		if i%10 == 0 {
			fmt.Println()
		}
	}

	// 피보나치 수열 (Fibonacci Sequence)
	// 앞의 두 숫자를 더해서 다음 숫자를 만드는 수열이에요.
	// 1, 1, 2, 3, 5, 8, 13, 21, ...
	fmt.Println("\n[피보나치 수열: 처음 15개]")
	a, b := 0, 1
	for i := 0; i < 15; i++ {
		fmt.Printf("%d ", a)
		a, b = b, a+b // Go의 다중 대입!
	}
	fmt.Println()

	// 소수 찾기 (Prime Numbers)
	// 1과 자기 자신으로만 나눌 수 있는 수
	fmt.Println("\n[1~50 사이의 소수 찾기]")
	for n := 2; n <= 50; n++ {
		isPrime := true
		for i := 2; i*i <= n; i++ { // n의 제곱근까지만 확인하면 충분!
			if n%i == 0 {
				isPrime = false
				break
			}
		}
		if isPrime {
			fmt.Printf("%d ", n)
		}
	}
	fmt.Println()

	// 피라미드 출력
	fmt.Println("\n[숫자 피라미드]")
	height := 5
	for row := 1; row <= height; row++ {
		// 공백 출력
		for space := 1; space <= height-row; space++ {
			fmt.Print("  ")
		}
		// 숫자 출력 (왼쪽)
		for col := 1; col <= row; col++ {
			fmt.Printf("%2d", col)
		}
		// 숫자 출력 (오른쪽)
		for col := row - 1; col >= 1; col-- {
			fmt.Printf("%2d", col)
		}
		fmt.Println()
	}

	fmt.Println()
	fmt.Println("╔═══════════════════════════════════════════════╗")
	fmt.Println("║  02단계 흐름 제어 완료! 다음: 03_functions ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")
}
