/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Go 학습 03단계: 함수 (Functions)
  ─ 다중 반환값, 가변인수, 익명함수, defer ─

  함수는 반복되는 일을 묶어서 이름을 붙인 것이에요.
  마치 레시피처럼, 한 번 만들어 놓으면 언제든지 꺼내 쓸 수 있어요!

  Go 함수의 특별한 점:
  ★ 여러 값을 동시에 반환할 수 있어요! (다른 언어에는 없는 기능)
  ★ 에러를 반환값으로 처리해요.
  ★ defer로 나중에 실행할 코드를 예약할 수 있어요.

  ■ 실행 방법: go run main.go

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/
package main

import (
	"errors"
	"fmt"
	"math"
)

func main() {
	fmt.Println("╔═══════════════════════════════════════════════╗")
	fmt.Println("║       Go 03단계: 함수 (Functions)               ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	demonstrateBasicFunctions()
	demonstrateMultipleReturns()
	demonstrateNamedReturns()
	demonstrateVariadicFunctions()
	demonstrateAnonymousFunctions()
	demonstrateFunctionsAsValues()
	demonstrateRecursion()
	demonstrateDefer()
	demonstrateClosures()
}

// ══════════════════════════════════════════════════════════════
// 섹션 1: 기본 함수
// ══════════════════════════════════════════════════════════════

// 기본 함수 형태:
// func 함수이름(매개변수 타입) 반환타입 { ... }
//
// 매개변수가 없는 함수
func sayHello() {
	fmt.Println("안녕하세요!")
}

// 매개변수가 있는 함수
// 매개변수는 함수에 전달하는 재료예요.
// 마치 요리할 때 재료를 넣는 것처럼요!
func greet(name string) {
	fmt.Printf("안녕하세요, %s님!\n", name)
}

// 반환값이 있는 함수
// Go의 함수는 값을 돌려줄 수 있어요.
// 마치 자판기에 돈을 넣으면 음료수가 나오는 것처럼!
func add(a, b int) int {
	return a + b
}

// 같은 타입의 매개변수는 타입을 한 번만 써도 돼요!
// add(a int, b int) → add(a, b int) 로 줄여 쓸 수 있어요.
func addThree(a, b, c int) int {
	return a + b + c
}

func demonstrateBasicFunctions() {
	fmt.Println("\n╔═══════════════════════════════════════════════╗")
	fmt.Println("║           섹션 1: 기본 함수                     ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	sayHello()
	greet("김민준")

	result := add(10, 20)
	fmt.Printf("10 + 20 = %d\n", result)

	total := addThree(1, 2, 3)
	fmt.Printf("1 + 2 + 3 = %d\n", total)

	// 함수를 직접 출력에 사용 (반환값 직접 사용)
	fmt.Printf("5 + 7 = %d\n", add(5, 7))

	fmt.Println()
}

// ══════════════════════════════════════════════════════════════
// 섹션 2: 다중 반환값 (Multiple Return Values)
// ══════════════════════════════════════════════════════════════
//
// Go의 가장 독특한 기능 중 하나예요!
// 함수가 여러 개의 값을 동시에 돌려줄 수 있어요.
// 마치 마트에서 계산할 때 "영수증과 거스름돈" 두 가지를 받는 것처럼요!
//
// 다른 언어에서는 어떻게 했을까요?
// - 구조체/객체로 묶어서 반환 (복잡!)
// - out 매개변수 사용 (C#, 복잡!)
// - 예외(exception) 던지기 (Java, 복잡!)
//
// Go: 그냥 두 값 반환하면 돼요! 간단!

// 나누기 함수: 결과와 에러를 함께 반환
func safeDivide(a, b float64) (float64, error) {
	if b == 0 {
		return 0, errors.New("0으로 나눌 수 없어요!")
	}
	return a / b, nil // nil = 에러 없음
}

// 최솟값과 최댓값을 동시에 반환
func minMax(numbers []int) (int, int) {
	if len(numbers) == 0 {
		return 0, 0
	}
	min, max := numbers[0], numbers[0]
	for _, n := range numbers[1:] {
		if n < min {
			min = n
		}
		if n > max {
			max = n
		}
	}
	return min, max
}

// 세 값 반환 (원의 둘레, 넓이, 지름)
func circleInfo(radius float64) (circumference, area, diameter float64) {
	circumference = 2 * math.Pi * radius
	area = math.Pi * radius * radius
	diameter = 2 * radius
	return // 이름 있는 반환 (섹션 3에서 자세히)
}

func demonstrateMultipleReturns() {
	fmt.Println("\n╔═══════════════════════════════════════════════╗")
	fmt.Println("║      섹션 2: 다중 반환값 (Go의 특별한 기능!)    ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// 두 값 받기
	result, err := safeDivide(10, 3)
	if err != nil {
		fmt.Println("오류:", err)
	} else {
		fmt.Printf("10 ÷ 3 = %.4f\n", result)
	}

	// 에러 발생 케이스
	_, err = safeDivide(5, 0)
	if err != nil {
		fmt.Println("에러 발생:", err)
	}

	// 최솟값과 최댓값
	nums := []int{42, 17, 83, 5, 61, 29}
	min, max := minMax(nums)
	fmt.Printf("숫자들: %v\n", nums)
	fmt.Printf("최솟값: %d, 최댓값: %d\n", min, max)

	// 세 값 받기
	c, a, d := circleInfo(5.0)
	fmt.Printf("\n반지름 5인 원:\n")
	fmt.Printf("  둘레: %.2f\n", c)
	fmt.Printf("  넓이: %.2f\n", a)
	fmt.Printf("  지름: %.2f\n", d)

	// 필요 없는 값은 _로 무시
	_, area, _ := circleInfo(3.0)
	fmt.Printf("반지름 3인 원의 넓이만: %.2f\n", area)

	fmt.Println()
}

// ══════════════════════════════════════════════════════════════
// 섹션 3: 이름 있는 반환값 (Named Return Values)
// ══════════════════════════════════════════════════════════════
//
// 반환값에 이름을 붙이면 함수 안에서 변수처럼 사용할 수 있어요.
// 마지막에 return만 쓰면 이름 있는 반환값들이 자동으로 반환돼요.
// (Naked Return이라고도 불러요)

// 이름 있는 반환값 예시
func divide(a, b float64) (result float64, err error) {
	// result와 err는 이미 선언된 변수예요 (제로값으로 초기화)
	if b == 0 {
		err = errors.New("0으로 나눌 수 없어요")
		return // result=0, err=에러 반환
	}
	result = a / b
	return // result=계산값, err=nil 반환
}

// 통계 함수: 평균, 합계, 개수를 이름 있는 반환값으로
func statistics(data []float64) (mean, sum float64, count int) {
	count = len(data)
	if count == 0 {
		return // 모두 제로값 반환
	}
	for _, v := range data {
		sum += v
	}
	mean = sum / float64(count)
	return // mean, sum, count 반환
}

func demonstrateNamedReturns() {
	fmt.Println("\n╔═══════════════════════════════════════════════╗")
	fmt.Println("║       섹션 3: 이름 있는 반환값                  ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	r, e := divide(10, 4)
	if e != nil {
		fmt.Println("에러:", e)
	} else {
		fmt.Printf("10 ÷ 4 = %.2f\n", r)
	}

	data := []float64{85.5, 92.0, 78.3, 95.1, 88.7}
	mean, sum, count := statistics(data)
	fmt.Printf("\n점수 데이터: %v\n", data)
	fmt.Printf("개수: %d, 합계: %.1f, 평균: %.2f\n", count, sum, mean)

	fmt.Println()
}

// ══════════════════════════════════════════════════════════════
// 섹션 4: 가변인수 함수 (Variadic Functions)
// ══════════════════════════════════════════════════════════════
//
// 가변인수란 개수가 정해지지 않은 매개변수예요.
// 마치 "원하는 만큼 먹어요!" 뷔페처럼,
// 몇 개의 인수를 넣어도 받아줘요!
// ...타입 형식으로 선언해요.

// 여러 숫자의 합계
func sum(numbers ...int) int {
	total := 0
	for _, n := range numbers {
		total += n
	}
	return total
}

// 형식화된 출력 (fmt.Printf처럼!)
func logMessage(prefix string, args ...interface{}) {
	fmt.Printf("[%s] ", prefix)
	fmt.Println(args...)
}

func demonstrateVariadicFunctions() {
	fmt.Println("\n╔═══════════════════════════════════════════════╗")
	fmt.Println("║       섹션 4: 가변인수 함수 (...)               ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// 인수 개수 상관없이 호출 가능!
	fmt.Println("합계 (인수 0개):", sum())
	fmt.Println("합계 (인수 1개):", sum(5))
	fmt.Println("합계 (인수 3개):", sum(1, 2, 3))
	fmt.Println("합계 (인수 5개):", sum(10, 20, 30, 40, 50))

	// 슬라이스를 가변인수로 전달할 때는 ... 을 붙여요!
	// 마치 봉투를 열어서 내용물을 꺼내 전달하는 것처럼요.
	scores := []int{85, 92, 78, 95, 88}
	fmt.Printf("슬라이스로 전달: %v의 합계 = %d\n", scores, sum(scores...))

	logMessage("정보", "사용자", "김철수", "로그인")
	logMessage("경고", "디스크 용량 부족:", "10%")
	logMessage("에러", "파일 찾기 실패")

	fmt.Println()
}

// ══════════════════════════════════════════════════════════════
// 섹션 5: 익명 함수 (Anonymous Functions)
// ══════════════════════════════════════════════════════════════
//
// 이름 없는 함수예요!
// 마치 이름 없는 편지처럼, 필요한 순간에만 만들어 사용해요.
// 한 번만 쓸 함수라면 이름을 붙일 필요가 없어요.

func demonstrateAnonymousFunctions() {
	fmt.Println("\n╔═══════════════════════════════════════════════╗")
	fmt.Println("║        섹션 5: 익명 함수 (Anonymous Functions)  ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// 즉시 실행 함수 (IIFE: Immediately Invoked Function Expression)
	// 함수를 만들자마자 바로 실행해요!
	result := func(a, b int) int {
		return a * b
	}(6, 7) // 바로 (6, 7) 인수로 호출!
	fmt.Printf("즉시 실행 함수: 6 × 7 = %d\n", result)

	// 변수에 함수 저장
	// 함수도 값이에요! 변수에 저장할 수 있어요.
	double := func(n int) int {
		return n * 2
	}
	triple := func(n int) int {
		return n * 3
	}

	fmt.Printf("2의 2배: %d\n", double(2))
	fmt.Printf("5의 3배: %d\n", triple(5))

	// 슬라이스를 정렬할 때 익명 함수 활용
	// (sort 패키지 없이 간단히 버블 정렬)
	numbers := []int{5, 3, 8, 1, 9, 2, 7}
	fmt.Printf("정렬 전: %v\n", numbers)

	// 버블 정렬 (익명 함수로 비교)
	lessThan := func(a, b int) bool {
		return a < b
	}

	for i := 0; i < len(numbers); i++ {
		for j := 0; j < len(numbers)-i-1; j++ {
			if !lessThan(numbers[j], numbers[j+1]) {
				numbers[j], numbers[j+1] = numbers[j+1], numbers[j]
			}
		}
	}
	fmt.Printf("정렬 후:  %v\n", numbers)

	fmt.Println()
}

// ══════════════════════════════════════════════════════════════
// 섹션 6: 함수를 값으로 사용 (Functions as Values)
// ══════════════════════════════════════════════════════════════
//
// Go에서 함수는 일급 시민(First-Class Citizen)이에요!
// 일급 시민이란 변수에 저장하고, 다른 함수에 전달하고,
// 함수에서 반환할 수 있다는 의미예요.
// 마치 숫자나 문자열처럼 함수도 값으로 사용할 수 있어요!

// 함수를 매개변수로 받는 함수
func applyOperation(a, b int, operation func(int, int) int) int {
	return operation(a, b)
}

// 함수를 반환하는 함수 (함수 팩토리!)
// 마치 공장에서 제품을 만들어내는 것처럼,
// 함수를 만들어서 반환해요.
func makeMultiplier(factor int) func(int) int {
	// factor를 "기억"하는 함수를 반환해요 (클로저!)
	return func(n int) int {
		return n * factor
	}
}

// 함수 타입 정의
// 마치 자료형을 만드는 것처럼 함수 타입도 만들 수 있어요.
type Transformer func(int) int

func applyAll(n int, transforms ...Transformer) int {
	result := n
	for _, transform := range transforms {
		result = transform(result)
	}
	return result
}

func demonstrateFunctionsAsValues() {
	fmt.Println("\n╔═══════════════════════════════════════════════╗")
	fmt.Println("║       섹션 6: 함수를 값으로 사용하기            ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// 함수를 인수로 전달
	fmt.Println("함수를 인수로 전달:")
	fmt.Printf("  덧셈: %d\n", applyOperation(10, 5, func(a, b int) int { return a + b }))
	fmt.Printf("  곱셈: %d\n", applyOperation(10, 5, func(a, b int) int { return a * b }))
	fmt.Printf("  최댓값: %d\n", applyOperation(10, 5, func(a, b int) int {
		if a > b {
			return a
		}
		return b
	}))

	// 함수 팩토리
	fmt.Println("\n함수 팩토리 (makeMultiplier):")
	double := makeMultiplier(2)
	triple := makeMultiplier(3)
	tenTimes := makeMultiplier(10)

	fmt.Printf("  double(5) = %d\n", double(5))
	fmt.Printf("  triple(5) = %d\n", triple(5))
	fmt.Printf("  tenTimes(5) = %d\n", tenTimes(5))

	// 함수 파이프라인 (체이닝)
	fmt.Println("\n함수 파이프라인:")
	addOne := Transformer(func(n int) int { return n + 1 })
	square := Transformer(func(n int) int { return n * n })
	negate := Transformer(func(n int) int { return -n })

	// 3에 순서대로 적용: 3 → 4(+1) → 16(제곱) → -16(부호반전)
	result := applyAll(3, addOne, square, negate)
	fmt.Printf("  3 → +1 → 제곱 → 부호반전 = %d\n", result)

	// 맵 함수 구현 (함수형 프로그래밍)
	mapInts := func(slice []int, f func(int) int) []int {
		result := make([]int, len(slice))
		for i, v := range slice {
			result[i] = f(v)
		}
		return result
	}

	nums := []int{1, 2, 3, 4, 5}
	doubled := mapInts(nums, func(n int) int { return n * 2 })
	squared := mapInts(nums, func(n int) int { return n * n })
	fmt.Printf("\n원본:   %v\n", nums)
	fmt.Printf("2배:    %v\n", doubled)
	fmt.Printf("제곱:   %v\n", squared)

	fmt.Println()
}

// ══════════════════════════════════════════════════════════════
// 섹션 7: 재귀 함수 (Recursion)
// ══════════════════════════════════════════════════════════════
//
// 재귀는 함수가 자기 자신을 호출하는 것이에요!
// 마치 거울을 거울 앞에 두면 무한히 반복되는 것처럼요.
// 하지만 반드시 "멈추는 조건"이 있어야 해요!

// 팩토리얼 (n! = n × (n-1) × ... × 1)
// 5! = 5 × 4 × 3 × 2 × 1 = 120
func factorial(n int) int {
	// 멈추는 조건 (Base Case) - 이게 없으면 무한 루프!
	if n <= 1 {
		return 1
	}
	// 재귀 호출: n! = n × (n-1)!
	return n * factorial(n-1)
}

// 피보나치 (재귀 버전)
// 0, 1, 1, 2, 3, 5, 8, 13, 21, ...
func fibonacci(n int) int {
	if n <= 1 {
		return n
	}
	return fibonacci(n-1) + fibonacci(n-2)
}

// 이진 탐색 (재귀 버전)
// 정렬된 배열에서 값을 빠르게 찾아요.
// 마치 사전에서 단어를 찾을 때 중간을 펼쳐보는 것처럼!
func binarySearch(arr []int, target, low, high int) int {
	if low > high {
		return -1 // 못 찾음
	}
	mid := (low + high) / 2
	switch {
	case arr[mid] == target:
		return mid
	case arr[mid] < target:
		return binarySearch(arr, target, mid+1, high)
	default:
		return binarySearch(arr, target, low, mid-1)
	}
}

func demonstrateRecursion() {
	fmt.Println("\n╔═══════════════════════════════════════════════╗")
	fmt.Println("║         섹션 7: 재귀 함수 (Recursion)           ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// 팩토리얼
	fmt.Println("팩토리얼:")
	for i := 0; i <= 10; i++ {
		fmt.Printf("  %2d! = %d\n", i, factorial(i))
	}

	// 피보나치
	fmt.Println("\n피보나치 수열 (처음 12개):")
	for i := 0; i < 12; i++ {
		fmt.Printf("%d ", fibonacci(i))
	}
	fmt.Println()

	// 이진 탐색
	fmt.Println("\n이진 탐색:")
	sortedArr := []int{2, 5, 8, 12, 16, 23, 38, 56, 72, 91}
	fmt.Printf("배열: %v\n", sortedArr)
	targets := []int{23, 50, 2, 91}
	for _, t := range targets {
		idx := binarySearch(sortedArr, t, 0, len(sortedArr)-1)
		if idx >= 0 {
			fmt.Printf("  %d 찾기: 인덱스 %d에 있어요!\n", t, idx)
		} else {
			fmt.Printf("  %d 찾기: 없어요!\n", t)
		}
	}

	fmt.Println()
}

// ══════════════════════════════════════════════════════════════
// 섹션 8: defer 문
// ══════════════════════════════════════════════════════════════
//
// defer는 함수가 끝날 때 실행할 코드를 미리 예약하는 것이에요!
// 마치 "이 일은 나중에 해줘!"라고 메모를 붙여두는 것처럼요.
//
// defer의 특징:
// 1. 함수가 반환되기 직전에 실행돼요.
// 2. 여러 개의 defer가 있으면 역순(LIFO)으로 실행돼요!
//    마치 접시를 쌓아놓고 꺼낼 때 위에서부터 꺼내는 것처럼.
// 3. 파일 닫기, 잠금 해제 등에 아주 유용해요!

func demonstrateDefer() {
	fmt.Println("\n╔═══════════════════════════════════════════════╗")
	fmt.Println("║         섹션 8: defer 문                        ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// 기본 defer
	fmt.Println("\n[기본 defer: 역순 실행]")
	deferExample()

	// 파일 작업 패턴 (실제 자주 쓰는 방법)
	fmt.Println("\n[defer를 이용한 리소스 정리]")
	processFile("중요한파일.txt")

	// defer와 반환값
	fmt.Println("\n[defer로 함수 실행 추적]")
	result := trackedFunction()
	fmt.Printf("결과: %d\n", result)

	// defer와 panic/recover (예외 처리)
	fmt.Println("\n[defer + recover로 패닉 복구]")
	safeOperation()
	fmt.Println("패닉 복구 후 프로그램 계속 실행 중!")

	fmt.Println()
}

func deferExample() {
	// defer는 쌓이는 순서의 반대로 실행돼요 (스택: LIFO)
	defer fmt.Println("  3번째 defer (마지막 실행)")
	defer fmt.Println("  2번째 defer")
	defer fmt.Println("  1번째 defer (첫 번째 실행)")
	fmt.Println("  함수 본문 실행 중...")
}

func processFile(filename string) {
	fmt.Printf("  파일 열기: %s\n", filename)
	defer fmt.Printf("  파일 닫기: %s (defer로 자동 실행!)\n", filename)

	// 파일 처리 코드 (여기서는 시뮬레이션)
	fmt.Println("  파일 읽기 중...")
	fmt.Println("  데이터 처리 중...")
	// 함수가 끝나면 defer가 실행되어 파일이 닫혀요
	// 에러가 발생해도 파일이 반드시 닫혀요!
}

func trackedFunction() int {
	fmt.Println("  함수 시작")
	defer fmt.Println("  함수 종료 (defer)")
	// defer는 반환값이 결정된 후에 실행돼요
	return 42
}

func safeOperation() {
	// recover()는 panic(패닉)을 잡아서 프로그램이 죽지 않게 해요.
	// defer 안에서만 작동해요!
	defer func() {
		if r := recover(); r != nil {
			fmt.Printf("  패닉 복구! 원인: %v\n", r)
		}
	}()

	fmt.Println("  위험한 작업 시작...")
	panic("테스트용 패닉 발생!") // 의도적으로 패닉 발생
	// 아래 코드는 실행되지 않아요
	fmt.Println("  이 줄은 실행 안 돼요")
}

// ══════════════════════════════════════════════════════════════
// 섹션 9: 클로저 (Closures)
// ══════════════════════════════════════════════════════════════
//
// 클로저는 자신이 만들어진 환경의 변수를 "기억"하는 함수예요!
// 마치 편지를 쓸 때 봉투에 넣으면 편지 안의 내용이 보존되듯,
// 함수가 외부 변수를 봉투처럼 감싸서 보존해요.

func demonstrateClosures() {
	fmt.Println("\n╔═══════════════════════════════════════════════╗")
	fmt.Println("║         섹션 9: 클로저 (Closures)               ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")

	// 카운터 클로저
	// makeCounter가 반환한 함수는 count 변수를 "기억"해요!
	counter := makeCounter()
	fmt.Println("카운터:")
	fmt.Printf("  %d\n", counter()) // 1
	fmt.Printf("  %d\n", counter()) // 2
	fmt.Printf("  %d\n", counter()) // 3

	// 독립적인 카운터 (각자 자신의 count를 가져요)
	counter1 := makeCounter()
	counter2 := makeCounter()
	fmt.Println("\n독립적인 카운터:")
	fmt.Printf("  counter1: %d\n", counter1())
	fmt.Printf("  counter1: %d\n", counter1())
	fmt.Printf("  counter2: %d\n", counter2()) // counter2는 따로 세요

	// 메모이제이션 (이전에 계산한 결과를 기억)
	fmt.Println("\n메모이제이션된 피보나치:")
	memoFib := makeMemoFibonacci()
	for i := 0; i < 10; i++ {
		fmt.Printf("  fib(%d) = %d\n", i, memoFib(i))
	}

	fmt.Println()
	fmt.Println("╔═══════════════════════════════════════════════╗")
	fmt.Println("║  03단계 함수 완료! 다음: 04_arrays_slices_maps ║")
	fmt.Println("╚═══════════════════════════════════════════════╝")
}

// 카운터를 만드는 함수
func makeCounter() func() int {
	count := 0 // 이 변수는 반환된 함수가 "포착"해요
	return func() int {
		count++ // 외부 변수 count를 수정해요
		return count
	}
}

// 메모이제이션된 피보나치
func makeMemoFibonacci() func(int) int {
	cache := map[int]int{} // 이 맵을 반환된 함수가 "포착"해요
	var fib func(int) int
	fib = func(n int) int {
		if n <= 1 {
			return n
		}
		if v, ok := cache[n]; ok {
			return v // 캐시에서 가져오기
		}
		result := fib(n-1) + fib(n-2)
		cache[n] = result // 결과 저장
		return result
	}
	return fib
}
