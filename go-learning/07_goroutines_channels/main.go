/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Go 학습 07단계: 고루틴과 채널
  ─ go 키워드 · chan · 버퍼 채널 · select · WaitGroup · 동시성 기초 ─

  [학습 목표]
  1. 고루틴으로 동시 작업을 시작하는 법을 안다
  2. 채널로 고루틴 사이에 데이터를 주고받는다
  3. 버퍼 있는 채널과 없는 채널의 차이를 안다
  4. select로 여러 채널을 동시에 기다린다
  5. WaitGroup으로 모든 고루틴이 끝날 때까지 기다린다

  ■ 실행: go run main.go
  ■ 빌드: go build -o 07_goroutines main.go

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

package main

import (
	"fmt"
	"sync"
	"time"
)

func main() {
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println("  Go 07단계 : 고루틴과 채널")
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println()

	lesson1GoroutineBasics()
	lesson2ChannelBasics()
	lesson3BufferedChannel()
	lesson4ChannelDirection()
	lesson5SelectStatement()
	lesson6WaitGroup()
	lesson7ChannelRange()
	lesson8CommonMistakes()

	fmt.Println("07단계 학습 완료!")
}

// =====================================================================
// 레슨 1 — 고루틴 기초
// =====================================================================
func lesson1GoroutineBasics() {
	fmt.Println("[레슨 1] 고루틴: go 키워드 하나로 동시에 일시키기")
	fmt.Println()

	/*
	   ★ 고루틴 = Go만의 초경량 실행 단위

	   비유: 식당에서 혼자 요리하면 순서대로 해야 하지만,
	         요리사를 여러 명 고용하면 동시에 여러 요리를 할 수 있다.
	         고루틴 = 아주 가벼운 요리사 (스레드보다 100배 가벼움!)

	   ┌──────────────────────────────────────────────┐
	   │  go 함수이름()   ← 이게 끝! 고루틴 시작!        │
	   │                                              │
	   │  ★ 주의: main()이 끝나면 모든 고루틴도 즉시 죽음! │
	   │  → 기다리는 방법이 필요 (채널 또는 WaitGroup)    │
	   └──────────────────────────────────────────────┘
	*/

	// done 채널로 고루틴이 끝날 때까지 기다린다
	done := make(chan bool)

	go func() {
		fmt.Println("  (고루틴) 안녕! 나는 별도로 실행 중이야!")
		time.Sleep(50 * time.Millisecond)
		fmt.Println("  (고루틴) 일 끝났어!")
		done <- true
	}()

	fmt.Println("  (메인) 고루틴을 기다리는 중...")
	<-done // 고루틴이 done에 값을 보낼 때까지 여기서 멈춤
	fmt.Println("  (메인) 고루틴이 끝남!")

	fmt.Println()
}

// =====================================================================
// 레슨 2 — 채널 기초
// =====================================================================
func lesson2ChannelBasics() {
	fmt.Println("[레슨 2] 채널: 고루틴끼리 데이터를 주고받는 파이프")
	fmt.Println()

	/*
	   ★ 채널 = 고루틴 사이의 안전한 통신 파이프

	   비유: 공장에서 컨베이어 벨트로 물건을 전달하는 것과 같다.
	         한쪽이 올려놓고(send), 다른 쪽이 집어간다(receive).

	   ┌───────────────────────────────────────────────┐
	   │  만들기:  ch := make(chan 타입)                  │
	   │  보내기:  ch <- 값                              │
	   │  받기:    값 := <-ch                            │
	   │                                               │
	   │  ★ 비버퍼 채널: 보내는 쪽은 받는 쪽이 올 때까지 │
	   │    멈춰서 기다린다 (동기화 효과!)                 │
	   └───────────────────────────────────────────────┘
	*/

	ch := make(chan string) // string을 주고받는 채널

	// 물 끓이기 고루틴
	go func() {
		time.Sleep(100 * time.Millisecond)
		ch <- "물이 끓었습니다!" // 채널에 보내기
	}()

	// 빵 굽기 고루틴
	go func() {
		time.Sleep(50 * time.Millisecond)
		ch <- "빵이 구워졌습니다!"
	}()

	// 두 결과를 받기
	msg1 := <-ch // 먼저 끝나는 쪽에서 받음
	msg2 := <-ch
	fmt.Println(" ", msg1)
	fmt.Println(" ", msg2)

	fmt.Println()
}

// =====================================================================
// 레슨 3 — 버퍼 있는 채널 vs 없는 채널
// =====================================================================
func lesson3BufferedChannel() {
	fmt.Println("[레슨 3] 버퍼 채널: 우체통처럼 미리 넣어 두기")
	fmt.Println()

	/*
	   ┌─────────────────────────────────────────────────┐
	   │  비버퍼 채널        │  버퍼 채널                  │
	   │  make(chan int)     │  make(chan int, 3)          │
	   ├─────────────────────────────────────────────────┤
	   │  보내면 바로 막힘    │  버퍼가 찰 때까지 안 막힘    │
	   │  (상대가 받을때까지) │  (우체통에 편지 넣는 느낌)   │
	   │  1:1 동기화에 적합   │  생산자-소비자 패턴에 적합   │
	   └─────────────────────────────────────────────────┘
	*/

	// 버퍼 크기 3짜리 채널
	mailbox := make(chan string, 3)

	// 받는 사람 없이도 3개까지는 넣을 수 있다!
	mailbox <- "편지1"
	mailbox <- "편지2"
	mailbox <- "편지3"
	// mailbox <- "편지4"  ← 이러면 꽉 차서 막힌다! (데드락!)

	fmt.Printf("  편지함: len=%d  cap=%d\n", len(mailbox), cap(mailbox))

	// 하나씩 꺼내기
	fmt.Println(" ", <-mailbox)
	fmt.Println(" ", <-mailbox)
	fmt.Println(" ", <-mailbox)

	fmt.Println()
}

// =====================================================================
// 레슨 4 — 채널 방향 (단방향 채널)
// =====================================================================

/*
   ★ 채널의 방향을 제한할 수 있다:
   chan<- int   → 보내기만 가능 (send-only)
   <-chan int   → 받기만 가능   (receive-only)

   왜 제한하나? → 실수로 잘못된 방향으로 쓰는 걸 컴파일러가 막아준다!
*/

func produce(ch chan<- int, count int) {
	for i := 1; i <= count; i++ {
		ch <- i * 10
	}
	close(ch) // 다 보냈으면 채널을 닫는다!
}

func consume(ch <-chan int) []int {
	var results []int
	for val := range ch { // 채널이 닫힐 때까지 반복
		results = append(results, val)
	}
	return results
}

func lesson4ChannelDirection() {
	fmt.Println("[레슨 4] 단방향 채널: 보내기 전용 / 받기 전용")
	fmt.Println()

	ch := make(chan int, 5)

	go produce(ch, 5) // chan → chan<- 자동 변환
	results := consume(ch) // chan → <-chan 자동 변환

	fmt.Println("  받은 값:", results)

	/*
	   ★ close(ch) 후 규칙:
	   - 보내기 시도 → 패닉!
	   - 받기 시도   → 남은 값을 반환, 다 비면 제로값 반환
	   - range로 순회하면 닫힐 때 자동 종료 (가장 깔끔!)
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 5 — select: 여러 채널을 동시에 기다리기
// =====================================================================
func lesson5SelectStatement() {
	fmt.Println("[레슨 5] select: 여러 채널 중 준비된 것부터 처리")
	fmt.Println()

	/*
	   ★ select = switch와 비슷하지만 '채널' 전용

	   select {
	   case msg := <-ch1:
	       // ch1에서 먼저 도착하면 여기
	   case msg := <-ch2:
	       // ch2에서 먼저 도착하면 여기
	   case <-time.After(1 * time.Second):
	       // 1초 안에 아무도 안 오면 여기 (타임아웃!)
	   }
	*/

	fast := make(chan string)
	slow := make(chan string)

	go func() {
		time.Sleep(30 * time.Millisecond)
		fast <- "빠른 결과!"
	}()

	go func() {
		time.Sleep(200 * time.Millisecond)
		slow <- "느린 결과!"
	}()

	// 두 번 select해서 두 채널 모두 받기
	for i := 0; i < 2; i++ {
		select {
		case msg := <-fast:
			fmt.Println("  [fast]", msg)
		case msg := <-slow:
			fmt.Println("  [slow]", msg)
		case <-time.After(500 * time.Millisecond):
			fmt.Println("  [timeout] 너무 오래 걸림!")
		}
	}

	fmt.Println()
}

// =====================================================================
// 레슨 6 — WaitGroup: 모든 고루틴이 끝날 때까지 기다리기
// =====================================================================
func lesson6WaitGroup() {
	fmt.Println("[레슨 6] WaitGroup: 여러 고루틴을 기다리는 카운터")
	fmt.Println()

	/*
	   ★ sync.WaitGroup = "할 일 카운터"

	   wg.Add(n)    → "n개의 일이 남았어"
	   wg.Done()    → "하나 끝났어" (Add(-1)과 같음)
	   wg.Wait()    → "전부 끝날 때까지 기다려"

	   비유: 소풍에서 선생님이 학생 수를 세고,
	         모두 돌아올 때까지 버스를 출발하지 않는 것!
	*/

	var wg sync.WaitGroup
	students := []string{"민수", "지우", "서연", "하준", "예린"}

	for _, name := range students {
		wg.Add(1) // 할 일 +1

		go func(n string) {
			defer wg.Done() // 끝나면 할 일 -1

			time.Sleep(20 * time.Millisecond)
			fmt.Printf("  %s: 과제 완료!\n", n)
		}(name) // ★ name을 인자로 전달! (클로저 함정 방지)
	}

	wg.Wait() // 모든 학생이 끝날 때까지 기다림
	fmt.Println("  → 모두 완료! 버스 출발!")

	/*
	   ★★★ 클로저 함정 ★★★
	   go func() { fmt.Println(name) }()  ← name은 루프 변수!
	   → 고루틴이 실행될 때 name은 이미 마지막 값으로 바뀌어 있을 수 있다!
	   → 해결: go func(n string) { ... }(name)  ← 인자로 복사해서 전달
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 7 — 채널 range와 close
// =====================================================================
func lesson7ChannelRange() {
	fmt.Println("[레슨 7] for-range로 채널 읽기: close가 신호")
	fmt.Println()

	/*
	   ★ for val := range ch { ... }
	   → 채널이 close될 때까지 계속 값을 꺼내서 처리한다

	   ★ close를 안 하면?
	   → range가 영원히 기다린다 → 데드락!
	*/

	jobs := make(chan int, 5)

	// 작업 넣기
	for i := 1; i <= 5; i++ {
		jobs <- i
	}
	close(jobs) // ★ 반드시 close! 안 하면 range가 멈추지 않음

	// 작업 처리
	fmt.Println("  --- 작업 처리 ---")
	for job := range jobs {
		fmt.Printf("  작업 #%d 완료\n", job)
	}

	// close 후 받기 테스트
	val, ok := <-jobs
	fmt.Printf("  닫힌 채널에서 받기: val=%d, ok=%v\n", val, ok) // 0, false

	fmt.Println()
}

// =====================================================================
// 레슨 8 — 흔한 실수 모음
// =====================================================================
func lesson8CommonMistakes() {
	fmt.Println("[레슨 8] 흔한 실수와 주의사항")
	fmt.Println()

	/*
	   ★ 실수 1: 데드락 — 보내는 사람/받는 사람이 없을 때
	   ──────────────────────────────────────────────
	   ch := make(chan int)
	   ch <- 1        ← 받는 사람이 없어서 영원히 막힘!
	   → "fatal error: all goroutines are asleep - deadlock!"

	   ★ 실수 2: 닫힌 채널에 보내기
	   ──────────────────────────────────────────────
	   close(ch)
	   ch <- 1        ← 패닉! "send on closed channel"

	   ★ 실수 3: 같은 채널을 두 번 close
	   ──────────────────────────────────────────────
	   close(ch)
	   close(ch)      ← 패닉! "close of closed channel"

	   ★ 실수 4: 고루틴 누수 — 아무도 안 읽는 채널에 고루틴이 보내기 대기
	   ──────────────────────────────────────────────
	   go func() {
	       ch <- result  ← 아무도 ch를 안 읽으면 이 고루틴은 영원히 살아있음
	   }()              → 메모리 누수!

	   ★ 실수 5: 클로저에서 루프 변수 캡처
	   ──────────────────────────────────────────────
	   for i := 0; i < 5; i++ {
	       go func() { fmt.Println(i) }()  ← 전부 5가 출력될 수 있음!
	   }
	   → go func(n int) { fmt.Println(n) }(i)  로 복사해서 전달!
	*/

	fmt.Println("  ┌──────────────────────────────────────────┐")
	fmt.Println("  │  실수 1: 받는 사람 없이 보내기 → 데드락    │")
	fmt.Println("  │  실수 2: 닫힌 채널에 보내기 → 패닉         │")
	fmt.Println("  │  실수 3: 채널 두 번 닫기 → 패닉            │")
	fmt.Println("  │  실수 4: 안 읽히는 채널 → 고루틴 누수      │")
	fmt.Println("  │  실수 5: 클로저 루프 변수 → 의도와 다른 값  │")
	fmt.Println("  └──────────────────────────────────────────┘")

	fmt.Println()
}
