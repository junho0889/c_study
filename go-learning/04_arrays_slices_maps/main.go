/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Go 학습 04단계: 배열, 슬라이스, 맵
  ─ 고정 배열 · 슬라이스(make/append/len/cap) · 맵(조회/삭제/순회) ─

  [학습 목표]
  1. 배열(array)의 선언, 고정 크기 특성을 안다
  2. 슬라이스의 내부 구조(포인터, len, cap)를 이해한다
  3. make, append, copy, 서브슬라이스를 다룬다
  4. 맵(map)의 생성, 조회, 삭제, 순회를 안다
  5. range 키워드로 컬렉션을 순회하는 법을 안다

  ■ 실행: go run main.go
  ■ 빌드: go build -o 04_collections main.go

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

package main

import "fmt"

// ─────────────────────────────────────────────────────────────────────────
// 함수 목록 (전방 선언 불필요 — Go는 같은 패키지 안에서 순서 무관)
// ─────────────────────────────────────────────────────────────────────────

func main() {
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println("  Go 04단계 : 배열, 슬라이스, 맵")
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println()

	lesson1ArrayBasics()
	lesson2SliceBasics()
	lesson3SliceInternals()
	lesson4SliceAppendAndCopy()
	lesson5SubSlice()
	lesson6MapBasics()
	lesson7MapAdvanced()
	lesson8RangeLoop()

	fmt.Println("04단계 학습 완료!")
}

// =====================================================================
// 레슨 1 — 배열 기초
// =====================================================================
func lesson1ArrayBasics() {
	fmt.Println("[레슨 1] 배열은 칸 수가 '처음부터 딱 정해진' 상자입니다.")
	fmt.Println()

	/*
	   ★ 배열 = 같은 타입의 값을 고정된 칸에 나란히 저장하는 구조

	   ┌──────────────────────────────────────────┐
	   │  var scores [3]int = [3]int{70, 80, 90}  │
	   │       ↑        ↑                          │
	   │     이름     크기(고정!)                   │
	   └──────────────────────────────────────────┘

	   사탕 상자가 3칸이면 4번째 칸을 추가할 수 없는 것과 같습니다.
	   Go에서는 배열을 직접 쓰는 일이 드물고, 대부분 "슬라이스"를 씁니다.
	*/

	// 방법 1: 크기를 직접 쓴다
	var scores [3]int = [3]int{70, 80, 90}
	fmt.Println("  점수 배열:", scores)

	// 방법 2: ... 을 쓰면 개수를 자동으로 세 준다
	fruits := [...]string{"사과", "바나나", "포도"}
	fmt.Println("  과일 배열:", fruits)

	// 인덱스는 0부터 시작!
	scores[1] = 88
	fmt.Println("  scores[1]을 88로 바꾼 뒤:", scores)

	// 배열의 길이
	fmt.Println("  배열 길이:", len(scores))

	/*
	   ★ 주의: 배열의 크기는 '타입의 일부'입니다!
	   [3]int 와 [5]int 는 완전히 다른 타입이라 서로 대입 불가!
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 2 — 슬라이스 기초
// =====================================================================
func lesson2SliceBasics() {
	fmt.Println("[레슨 2] 슬라이스는 '늘어나는 배열'입니다.")
	fmt.Println()

	/*
	   ┌─────────────────────────────────────────────────────┐
	   │  슬라이스 vs 배열                                    │
	   ├──────────────┬──────────────────────────────────────┤
	   │  배열         │ [3]int{1,2,3}  — 크기 고정           │
	   │  슬라이스     │ []int{1,2,3}   — 크기 유동           │
	   └──────────────┴──────────────────────────────────────┘

	   슬라이스를 만드는 3가지 방법:
	   1) 리터럴:    s := []int{10, 20, 30}
	   2) make:      s := make([]int, 길이, 용량)
	   3) 배열 잘라내기: s := arr[1:3]
	*/

	// 방법 1: 리터럴
	colors := []string{"빨강", "파랑", "초록"}
	fmt.Println("  리터럴로 만든 슬라이스:", colors)

	// 방법 2: make(타입, 길이, 용량)
	nums := make([]int, 3, 5)
	fmt.Println("  make로 만든 슬라이스:", nums)
	fmt.Printf("  len=%d  cap=%d\n", len(nums), cap(nums))

	/*
	   ★ len = 지금 사용 중인 칸 수
	   ★ cap = 내부 배열이 확보해 둔 칸 수(여유 공간)

	   비유: 10칸짜리 빈 공책(cap=10)에 3페이지까지 썼다(len=3)
	        아직 7페이지 여유가 있어서 append 해도 공책을 새로 살 필요 없음!
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 3 — 슬라이스 내부 구조 (매우 중요!)
// =====================================================================
func lesson3SliceInternals() {
	fmt.Println("[레슨 3] 슬라이스 내부: 포인터 + len + cap")
	fmt.Println()

	/*
	   슬라이스는 사실 3개의 정보를 묶은 '헤더'입니다:

	   ┌──────────────────────────┐
	   │  슬라이스 헤더            │
	   ├──────────┬───────────────┤
	   │ ptr      │ → 내부 배열    │  ← 데이터가 실제로 저장된 곳
	   │ len      │ 3             │  ← 쓰고 있는 칸 수
	   │ cap      │ 5             │  ← 확보된 칸 수
	   └──────────┴───────────────┘

	   ★★★ 핵심 함정 ★★★
	   두 슬라이스가 같은 내부 배열을 가리킬 수 있다!
	   한쪽을 바꾸면 다른 쪽도 바뀐다!
	*/

	original := []int{10, 20, 30, 40, 50}
	sub := original[1:3] // 20, 30 을 가리키는 슬라이스

	fmt.Println("  원본:", original)
	fmt.Println("  sub (original[1:3]):", sub)

	// sub를 바꾸면 원본도 바뀐다!
	sub[0] = 999
	fmt.Println("  sub[0]=999 후 원본:", original) // [10, 999, 30, 40, 50]

	/*
	   ★ 이 함정을 피하려면?
	   → copy()를 써서 독립적인 복사본을 만든다 (레슨 4에서 배움)
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 4 — append 와 copy
// =====================================================================
func lesson4SliceAppendAndCopy() {
	fmt.Println("[레슨 4] append로 늘리기, copy로 안전하게 복사하기")
	fmt.Println()

	/*
	   ★ append(슬라이스, 새값...)  →  새 슬라이스를 반환
	   ★ 반드시 결과를 다시 대입해야 한다!  s = append(s, 값)

	   ┌──────────────────────────────────────────────┐
	   │  cap이 남아있으면 → 같은 배열에 추가           │
	   │  cap이 꽉 찼으면 → 새 배열을 할당 후 복사!     │
	   └──────────────────────────────────────────────┘
	*/

	s := make([]int, 0, 3)
	fmt.Printf("  시작: len=%d cap=%d\n", len(s), cap(s))

	s = append(s, 10)
	s = append(s, 20)
	s = append(s, 30)
	fmt.Printf("  3개 추가 후: len=%d cap=%d  값=%v\n", len(s), cap(s), s)

	// cap(3)인데 4번째를 넣으면?  → 내부 배열이 더 큰 것으로 교체된다
	s = append(s, 40)
	fmt.Printf("  4번째 추가: len=%d cap=%d  값=%v\n", len(s), cap(s), s)
	fmt.Println("  → cap이 늘어남! Go가 자동으로 큰 배열을 만들어 줌")

	// 여러 개를 한번에 추가
	s = append(s, 50, 60, 70)
	fmt.Printf("  여러 개 추가: len=%d cap=%d  값=%v\n", len(s), cap(s), s)

	fmt.Println()

	// ── copy: 안전한 복사 ──
	original := []int{1, 2, 3, 4, 5}
	backup := make([]int, len(original))
	copied := copy(backup, original)
	fmt.Printf("  copy: %d개 복사됨, backup=%v\n", copied, backup)

	// backup을 바꿔도 original에 영향 없음!
	backup[0] = 999
	fmt.Println("  backup[0]=999 후 original:", original) // 영향 없음
	fmt.Println("  backup:", backup)

	fmt.Println()
}

// =====================================================================
// 레슨 5 — 서브슬라이스 (잘라내기)
// =====================================================================
func lesson5SubSlice() {
	fmt.Println("[레슨 5] 슬라이스를 잘라내기 (a[시작:끝])")
	fmt.Println()

	/*
	   ★ s[low:high]  →  인덱스 low 이상, high 미만

	   데이터:  10  20  30  40  50
	   인덱스:   0   1   2   3   4
	                 ↑       ↑
	            s[1:3] = [20, 30]    (1 이상, 3 미만)

	   ★ 생략 규칙:
	     s[:3]  = s[0:3]   (처음부터)
	     s[2:]  = s[2:끝]  (끝까지)
	     s[:]   = s[0:끝]  (전체)
	*/

	data := []int{10, 20, 30, 40, 50}

	fmt.Println("  data:", data)
	fmt.Println("  data[1:3]:", data[1:3]) // [20, 30]
	fmt.Println("  data[:2]:", data[:2])    // [10, 20]
	fmt.Println("  data[3:]:", data[3:])    // [40, 50]

	// ★ 슬라이스에서 요소 삭제하기 (Go에는 delete 함수 없음!)
	// 방법: append로 앞뒤를 이어붙인다
	idx := 2 // 인덱스 2번(값 30)을 삭제
	data = append(data[:idx], data[idx+1:]...)
	fmt.Println("  인덱스 2 삭제 후:", data) // [10, 20, 40, 50]

	fmt.Println()
}

// =====================================================================
// 레슨 6 — 맵 기초
// =====================================================================
func lesson6MapBasics() {
	fmt.Println("[레슨 6] 맵은 '이름표→값' 연결 상자입니다.")
	fmt.Println()

	/*
	   ┌──────────────────────────────────────────────┐
	   │  맵(map) = 사전처럼 키(key)로 값(value)을 찾는다 │
	   ├──────────┬──────────┬────────────────────────┤
	   │  키(key) │  값      │  예시                    │
	   │  "민수"  │  82      │  studentScores["민수"]   │
	   │  "지우"  │  95      │  studentScores["지우"]   │
	   └──────────┴──────────┴────────────────────────┘
	*/

	// 맵 만들기 방법 1: 리터럴
	studentScores := map[string]int{
		"민수": 82,
		"지우": 95,
		"서연": 78,
	}
	fmt.Println("  학생 점수:", studentScores)

	// 맵 만들기 방법 2: make
	ages := make(map[string]int)
	ages["민수"] = 15
	ages["지우"] = 16
	fmt.Println("  나이:", ages)

	// 값 조회
	fmt.Println("  민수 점수:", studentScores["민수"])

	/*
	   ★★★ 핵심: 맵 조회 시 '있는지' 확인하는 습관 ★★★

	   score := studentScores["없는사람"]  → 0이 나옴 (에러 아님!)
	   이게 0점인 건지, 없는 건지 구분 불가!

	   → "comma ok" 패턴을 써야 한다:
	   score, ok := studentScores["없는사람"]
	*/

	score, ok := studentScores["영희"]
	if ok {
		fmt.Println("  영희 점수:", score)
	} else {
		fmt.Println("  영희는 목록에 없습니다 (ok=false)")
	}

	fmt.Println()
}

// =====================================================================
// 레슨 7 — 맵 심화 (삭제, 순회, 주의사항)
// =====================================================================
func lesson7MapAdvanced() {
	fmt.Println("[레슨 7] 맵 삭제, 순회, 주의사항")
	fmt.Println()

	menu := map[string]int{
		"떡볶이": 4000,
		"순대":  3500,
		"김밥":  2500,
		"라면":  3000,
	}

	// 삭제: delete(맵, 키)
	delete(menu, "순대")
	fmt.Println("  순대 삭제 후:", menu)

	// 맵의 크기
	fmt.Println("  메뉴 개수:", len(menu))

	// 순회: for key, value := range 맵
	fmt.Println("  --- 메뉴 순회 ---")
	for name, price := range menu {
		fmt.Printf("    %s: %d원\n", name, price)
	}

	/*
	   ★★★ 주의: 맵의 순회 순서는 보장되지 않는다! ★★★
	   실행할 때마다 순서가 달라질 수 있다.
	   정렬이 필요하면 키를 슬라이스에 모아 sort 해야 한다.

	   ★ nil 맵에 쓰면 패닉!
	   var m map[string]int   ← nil 맵
	   m["test"] = 1          ← 패닉 발생!
	   반드시 make 또는 리터럴로 초기화 후 사용할 것!
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 8 — range 루프 총정리
// =====================================================================
func lesson8RangeLoop() {
	fmt.Println("[레슨 8] range로 컬렉션을 편하게 순회하기")
	fmt.Println()

	/*
	   range는 슬라이스, 배열, 맵, 문자열, 채널에 쓸 수 있다.

	   ┌─────────────────────────────────────────────┐
	   │  대상            │  range가 주는 값           │
	   ├─────────────────┼──────────────────────────┤
	   │  슬라이스/배열    │  인덱스, 값               │
	   │  맵              │  키, 값                   │
	   │  문자열           │  바이트 위치, 룬(rune)     │
	   │  채널            │  채널에서 꺼낸 값           │
	   └─────────────────┴──────────────────────────┘
	*/

	// 슬라이스 range
	fruits := []string{"사과", "바나나", "포도"}
	fmt.Println("  --- 슬라이스 range ---")
	for i, fruit := range fruits {
		fmt.Printf("    [%d] %s\n", i, fruit)
	}

	// 인덱스가 필요 없으면 _ 로 버린다
	fmt.Println("  --- 인덱스 생략 ---")
	for _, fruit := range fruits {
		fmt.Println("   ", fruit)
	}

	// 맵 range
	scores := map[string]int{"수학": 90, "영어": 85, "과학": 92}
	fmt.Println("  --- 맵 range ---")
	for subject, score := range scores {
		fmt.Printf("    %s: %d점\n", subject, score)
	}

	// 문자열 range (한글도 정확하게!)
	fmt.Println("  --- 문자열 range ---")
	for i, ch := range "Go언어" {
		fmt.Printf("    바이트위치=%d  글자='%c'\n", i, ch)
	}

	/*
	   ★ 팁: range에서 값만 필요하면 인덱스를 _ 로 버리고,
	         인덱스만 필요하면 값 변수를 아예 안 쓰면 된다:
	         for i := range slice { ... }  ← 인덱스만!
	*/

	fmt.Println()
}
