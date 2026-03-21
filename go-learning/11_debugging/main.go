/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Go 학습 11단계: 디버깅
  ─ 로그 출력 · fmt 디버깅 · 흔한 버그 패턴 · race detector · pprof 개요 ─

  [학습 목표]
  1. fmt.Println 디버깅과 log 패키지를 비교한다
  2. Go에서 자주 발생하는 버그 패턴을 안다
  3. 데이터 경쟁(race condition)과 감지 방법을 안다
  4. delve 디버거 사용법을 안다
  5. pprof로 성능 분석하는 개념을 안다

  ■ 실행: go run main.go
  ■ 빌드: go build -o 11_debugging main.go

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

package main

import (
	"fmt"
	"log"
	"os"
	"strings"
	"sync"
)

func main() {
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println("  Go 11단계 : 디버깅")
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println()

	lesson1FmtDebugging()
	lesson2LogPackage()
	lesson3CommonBugWrongAverage()
	lesson4CommonBugSliceTrap()
	lesson5CommonBugNilMap()
	lesson6RaceCondition()
	lesson7DelveDebugger()
	lesson8ProfilingOverview()

	fmt.Println("11단계 학습 완료!")
}

// =====================================================================
// 레슨 1 — fmt.Println 디버깅 (가장 기본)
// =====================================================================
func lesson1FmtDebugging() {
	fmt.Println("[레슨 1] fmt 디버깅: 가장 원시적이지만 빠른 방법")
	fmt.Println()

	/*
	   ★ 디버깅 = 코드에서 버그를 찾아 고치는 과정

	   가장 빠른 방법: 의심되는 곳에 fmt.Println을 넣어서 값을 확인!

	   ┌──────────────────────────────────────────┐
	   │  fmt.Println("DEBUG:", 변수)              │  ← 가장 기본
	   │  fmt.Printf("DEBUG: x=%d y=%d\n", x, y)  │  ← 포맷 지정
	   │  fmt.Printf("DEBUG: %+v\n", 구조체)       │  ← 필드명 포함
	   │  fmt.Printf("DEBUG: %#v\n", 구조체)       │  ← Go 문법 형식
	   └──────────────────────────────────────────┘
	*/

	type Student struct {
		Name  string
		Score int
	}

	s := Student{Name: "민수", Score: 85}

	// 디버깅에 유용한 출력 방법들
	fmt.Printf("  %%v:  %v\n", s)   // {민수 85}
	fmt.Printf("  %%+v: %+v\n", s)  // {Name:민수 Score:85}  ← 필드명!
	fmt.Printf("  %%#v: %#v\n", s)  // main.Student{Name:"민수", Score:85}

	/*
	   ★ 팁: 디버깅 코드에 "DEBUG" 접두사를 붙이면
	   나중에 검색해서 쉽게 찾아 지울 수 있다!
	   → grep -n "DEBUG" main.go
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 2 — log 패키지: 더 나은 디버깅
// =====================================================================
func lesson2LogPackage() {
	fmt.Println("[레슨 2] log 패키지: 타임스탬프가 붙는 로깅")
	fmt.Println()

	/*
	   ★ log vs fmt:
	   ┌──────────────────────────────────────────────────┐
	   │  fmt.Println       │  그냥 출력                   │
	   │  log.Println       │  날짜+시간 자동 추가!         │
	   │  log.Fatal         │  출력 후 프로그램 종료!        │
	   │  log.SetPrefix     │  접두사 설정                  │
	   │  log.SetFlags      │  출력 형식 설정               │
	   └──────────────────────────────────────────────────┘
	*/

	// 기본 로그
	log.Println("기본 로그 출력 (날짜+시간 포함)")

	// 커스텀 로거
	logger := log.New(os.Stdout, "[DEBUG] ", log.Ltime|log.Lshortfile)
	logger.Println("커스텀 로거 (시간+파일위치)")

	/*
	   ★ log.SetFlags 옵션:
	   log.Ldate      → 날짜
	   log.Ltime      → 시간
	   log.Lshortfile → 파일명:줄번호
	   log.Llongfile  → 전체 경로:줄번호
	   log.Lmicroseconds → 마이크로초
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 3 — 흔한 버그: 잘못된 평균 계산
// =====================================================================
func lesson3CommonBugWrongAverage() {
	fmt.Println("[레슨 3] 흔한 버그: 나누기에서 생기는 실수")
	fmt.Println()

	scores := []int{80, 90, 70}

	/*
	   ★ 버그 1: 정수 나눗셈으로 소수점이 사라진다!
	   total / len(scores)  → 240 / 3 = 80  (int 나눗셈)
	   실제 평균이 80.0이면 괜찮지만, 85.3 같은 건 85로 잘린다!
	*/

	// 잘못된 방법 (정수 나눗셈)
	total := 0
	for _, s := range scores {
		total += s
	}
	wrongAvg := total / len(scores)
	fmt.Println("  정수 나눗셈 (잘못됨):", wrongAvg)

	// 올바른 방법 (float64로 변환)
	correctAvg := float64(total) / float64(len(scores))
	fmt.Printf("  실수 나눗셈 (올바름): %.2f\n", correctAvg)

	/*
	   ★ 버그 2: 빈 슬라이스로 나누면 panic!
	   var empty []int
	   avg := total / len(empty)  → 0으로 나누기! panic!

	   → 반드시 len > 0 확인!
	*/

	fmt.Println("  ★ 빈 슬라이스 나누기 → panic! 꼭 길이 확인!")

	fmt.Println()
}

// =====================================================================
// 레슨 4 — 흔한 버그: 슬라이스 공유 함정
// =====================================================================
func lesson4CommonBugSliceTrap() {
	fmt.Println("[레슨 4] 흔한 버그: 슬라이스가 원본을 바꿔버리는 함정")
	fmt.Println()

	/*
	   ★ 함수에 슬라이스를 넘기면 원본이 바뀔 수 있다!
	   슬라이스는 내부 배열의 "참조"를 전달하기 때문
	*/

	original := []int{1, 2, 3, 4, 5}
	fmt.Println("  원본 (전):", original)

	// 잘못된 예: 함수가 원본을 바꿈
	doubleValues(original)
	fmt.Println("  원본 (후):", original) // [2, 4, 6, 8, 10] ← 바뀜!

	// 올바른 방법: copy로 복사 후 넘기기
	original2 := []int{1, 2, 3, 4, 5}
	backup := make([]int, len(original2))
	copy(backup, original2)
	doubleValues(backup)
	fmt.Println("  원본2 (보존):", original2) // [1, 2, 3, 4, 5]
	fmt.Println("  백업 (변경):", backup)      // [2, 4, 6, 8, 10]

	/*
	   ★ append 함정:
	   sub := original[:3]
	   sub = append(sub, 99)  ← original[3]이 99로 바뀔 수 있다!
	   → 용량(cap)이 남아있으면 원본 배열에 덮어씀!
	*/

	fmt.Println()
}

func doubleValues(s []int) {
	for i := range s {
		s[i] *= 2
	}
}

// =====================================================================
// 레슨 5 — 흔한 버그: nil 맵에 쓰기
// =====================================================================
func lesson5CommonBugNilMap() {
	fmt.Println("[레슨 5] 흔한 버그: nil 맵에 쓰면 panic!")
	fmt.Println()

	/*
	   ★ 맵을 선언만 하면 nil 맵!
	   var m map[string]int   ← nil
	   m["key"] = 1           ← panic: assignment to entry in nil map

	   ★ nil 맵에서 읽기는 된다! (제로값 반환)
	   val := m["key"]        ← 0 (panic 아님!)

	   → 반드시 make 또는 리터럴로 초기화!
	*/

	// 안전한 방법
	safeMap := make(map[string]int)
	safeMap["테스트"] = 100
	fmt.Println("  안전한 맵:", safeMap)

	// nil 맵 읽기 (에러 없음!)
	var nilMap map[string]int
	val := nilMap["없는키"]
	fmt.Println("  nil 맵 읽기:", val) // 0

	// nil 맵 쓰기 → panic! (여기서는 복구)
	func() {
		defer func() {
			if r := recover(); r != nil {
				fmt.Println("  nil 맵 쓰기 → panic 발생:", r)
			}
		}()
		var m map[string]int
		m["key"] = 1 // panic!
	}()

	fmt.Println()
}

// =====================================================================
// 레슨 6 — 데이터 경쟁 (Race Condition)
// =====================================================================
func lesson6RaceCondition() {
	fmt.Println("[레슨 6] 데이터 경쟁: 여러 고루틴이 같은 변수를 동시에 쓸 때")
	fmt.Println()

	/*
	   ★ 데이터 경쟁 = 두 개 이상의 고루틴이 같은 변수를
	                  동시에 읽고 쓸 때 발생하는 버그

	   비유: 두 사람이 동시에 같은 통장에서 돈을 빼면
	         잔액이 꼬이는 것!

	   ┌────────────────────────────────────────────────┐
	   │  감지: go run -race main.go                     │
	   │  → "DATA RACE" 라는 경고가 출력된다!             │
	   │                                                │
	   │  해결:                                          │
	   │  1. sync.Mutex로 잠그기                          │
	   │  2. 채널로 통신하기                               │
	   │  3. sync/atomic 패키지 사용                      │
	   └────────────────────────────────────────────────┘
	*/

	// 잘못된 방법 (경쟁 발생 가능!)
	counter := 0
	var wg sync.WaitGroup

	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			counter++ // ★ 위험! 여러 고루틴이 동시에 수정!
		}()
	}
	wg.Wait()
	fmt.Println("  경쟁 있는 카운터 (불안정):", counter)

	// 올바른 방법: Mutex 사용
	var mu sync.Mutex
	safeCounter := 0

	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			mu.Lock()         // 잠그기
			safeCounter++
			mu.Unlock()       // 풀기
		}()
	}
	wg.Wait()
	fmt.Println("  Mutex 보호 카운터 (안전):", safeCounter)

	fmt.Println()
}

// =====================================================================
// 레슨 7 — delve 디버거
// =====================================================================
func lesson7DelveDebugger() {
	fmt.Println("[레슨 7] delve: Go 전용 디버거")
	fmt.Println()

	/*
	   ★ delve = Go 코드를 한 줄씩 실행하며 변수를 살펴보는 도구

	   ┌───────────────────────────────────────────────┐
	   │  설치:                                         │
	   │  go install github.com/go-delve/delve/cmd/dlv@latest │
	   │                                               │
	   │  사용:                                         │
	   │  dlv debug main.go          ← 디버그 시작      │
	   │                                               │
	   │  주요 명령어:                                   │
	   │  break main.go:42    → 42번째 줄에 중단점       │
	   │  continue (c)        → 다음 중단점까지 실행     │
	   │  next (n)            → 한 줄 실행              │
	   │  step (s)            → 함수 안으로 들어가기     │
	   │  print 변수 (p)      → 변수 값 출력            │
	   │  locals              → 지역 변수 모두 출력      │
	   │  goroutines          → 고루틴 목록              │
	   │  exit (q)            → 종료                    │
	   └───────────────────────────────────────────────┘

	   ★ VS Code에서도 사용 가능!
	   Go 확장 설치 → F5로 디버깅 (launch.json 자동 생성)
	*/

	fmt.Println("  설치: go install github.com/go-delve/delve/cmd/dlv@latest")
	fmt.Println("  실행: dlv debug main.go")
	fmt.Println("  중단점: break main.go:42")
	fmt.Println("  계속: continue / 한줄: next / 진입: step")
	fmt.Println("  변수: print 변수명 / 지역변수: locals")

	fmt.Println()
}

// =====================================================================
// 레슨 8 — 프로파일링 개요 (pprof)
// =====================================================================
func lesson8ProfilingOverview() {
	fmt.Println("[레슨 8] pprof: 성능 병목 찾기")
	fmt.Println()

	/*
	   ★ 프로파일링 = "어디서 시간을 많이 쓰는가?" 분석

	   ┌────────────────────────────────────────────────────┐
	   │  CPU 프로파일링:  어떤 함수가 CPU를 많이 먹는가?      │
	   │  메모리 프로파일링: 어디서 메모리를 많이 할당하는가?   │
	   │  고루틴 프로파일링: 고루틴이 어디서 막혀있는가?        │
	   ├────────────────────────────────────────────────────┤
	   │  사용법:                                            │
	   │  1. import _ "net/http/pprof"                       │
	   │  2. go func() { http.ListenAndServe(":6060", nil) }│
	   │  3. 브라우저: http://localhost:6060/debug/pprof     │
	   │                                                    │
	   │  CLI:                                              │
	   │  go tool pprof http://localhost:6060/debug/pprof/profile │
	   │  (top, list, web 등 명령으로 분석)                  │
	   ├────────────────────────────────────────────────────┤
	   │  벤치마크 프로파일링:                                │
	   │  go test -bench=. -cpuprofile=cpu.prof             │
	   │  go tool pprof cpu.prof                            │
	   └────────────────────────────────────────────────────┘
	*/

	fmt.Println("  CPU: go test -bench=. -cpuprofile=cpu.prof")
	fmt.Println("  메모리: go test -bench=. -memprofile=mem.prof")
	fmt.Println("  분석: go tool pprof cpu.prof → top / list / web")
	fmt.Println()

	// 간단한 성능 비교 예시: 문자열 합치기
	fmt.Println("  --- 문자열 합치기 성능 비교 (개념) ---")
	fmt.Println("  s += \"a\" (반복)  → 느림! (매번 새 문자열 생성)")
	fmt.Println("  strings.Builder  → 빠름! (내부 버퍼 재사용)")

	// Builder가 왜 빠른지 보여주기
	var b strings.Builder
	for i := 0; i < 10; i++ {
		fmt.Fprintf(&b, "%d", i)
	}
	fmt.Println("  Builder 결과:", b.String())

	fmt.Println()
}
