/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Go 학습 10단계: 표준 라이브러리
  ─ strings · strconv · sort · time · os · io · encoding/json ─

  [학습 목표]
  1. strings 패키지로 문자열을 자유자재로 다룬다
  2. strconv로 문자열-숫자 변환을 안다
  3. sort로 슬라이스를 정렬한다
  4. time으로 시간을 다룬다
  5. os, io로 파일을 읽고 쓴다
  6. encoding/json으로 JSON을 파싱하고 만든다

  ■ 실행: go run main.go
  ■ 빌드: go build -o 10_stdlib main.go

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

package main

import (
	"encoding/json"
	"fmt"
	"os"
	"sort"
	"strconv"
	"strings"
	"time"
)

func main() {
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println("  Go 10단계 : 표준 라이브러리")
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println()

	lesson1Strings()
	lesson2Strconv()
	lesson3Sort()
	lesson4Time()
	lesson5FileIO()
	lesson6JSON()
	lesson7FmtVerbs()
	lesson8UsefulPackages()

	fmt.Println("10단계 학습 완료!")
}

// =====================================================================
// 레슨 1 — strings 패키지
// =====================================================================
func lesson1Strings() {
	fmt.Println("[레슨 1] strings 패키지: 문자열 다루기의 만능 칼")
	fmt.Println()

	text := "  Go is Simple and Fast  "

	/*
	   ┌──────────────────────────────────────────────────────────┐
	   │  함수                │  설명                │  결과       │
	   ├──────────────────────────────────────────────────────────┤
	   │  ToUpper(s)          │  대문자로             │  GO IS...  │
	   │  ToLower(s)          │  소문자로             │  go is...  │
	   │  TrimSpace(s)        │  앞뒤 공백 제거       │  Go is...  │
	   │  Contains(s, sub)    │  포함 여부            │  true/false│
	   │  HasPrefix(s, pre)   │  시작 문자열 확인     │  true/false│
	   │  HasSuffix(s, suf)   │  끝 문자열 확인       │  true/false│
	   │  Replace(s,old,new,n)│  교체 (n=-1이면 전부) │            │
	   │  Split(s, sep)       │  분리 → 슬라이스      │            │
	   │  Join(slice, sep)    │  합치기               │            │
	   │  Count(s, sub)       │  등장 횟수            │  int       │
	   │  Index(s, sub)       │  첫 위치 (-1=없음)    │  int       │
	   │  Repeat(s, n)        │  n번 반복             │            │
	   └──────────────────────────────────────────────────────────┘
	*/

	fmt.Println("  원본:", text)
	fmt.Println("  TrimSpace:", strings.TrimSpace(text))
	fmt.Println("  ToUpper:", strings.ToUpper(text))
	fmt.Println("  Contains(\"Simple\"):", strings.Contains(text, "Simple"))
	fmt.Println("  Replace:", strings.Replace(text, "Simple", "Easy", 1))

	// Split & Join
	csv := "민수,지우,서연,하준"
	names := strings.Split(csv, ",")
	fmt.Println("  Split:", names)
	fmt.Println("  Join:", strings.Join(names, " & "))

	// Count & Index
	fmt.Println("  Count('i'):", strings.Count(text, "i"))
	fmt.Println("  Index('Simple'):", strings.Index(text, "Simple"))

	// Repeat
	fmt.Println("  Repeat(\"Go \", 3):", strings.Repeat("Go ", 3))

	// Builder — 많은 문자열을 효율적으로 합칠 때
	var b strings.Builder
	for i := 0; i < 5; i++ {
		fmt.Fprintf(&b, "(%d)", i)
	}
	fmt.Println("  Builder:", b.String())

	fmt.Println()
}

// =====================================================================
// 레슨 2 — strconv: 문자열 ↔ 숫자 변환
// =====================================================================
func lesson2Strconv() {
	fmt.Println("[레슨 2] strconv: 문자열과 숫자 사이의 다리")
	fmt.Println()

	/*
	   ★ 문자열 → 숫자: Atoi, ParseInt, ParseFloat
	   ★ 숫자 → 문자열: Itoa, FormatInt, FormatFloat
	*/

	// 문자열 → 정수
	num, err := strconv.Atoi("42")
	if err == nil {
		fmt.Println("  Atoi(\"42\"):", num)
	}

	// 실패하는 경우
	_, err = strconv.Atoi("abc")
	if err != nil {
		fmt.Println("  Atoi(\"abc\"): 에러 →", err)
	}

	// 문자열 → 실수
	pi, _ := strconv.ParseFloat("3.14159", 64)
	fmt.Printf("  ParseFloat(\"3.14159\"): %.5f\n", pi)

	// 문자열 → bool
	b, _ := strconv.ParseBool("true")
	fmt.Println("  ParseBool(\"true\"):", b)

	// 숫자 → 문자열
	s := strconv.Itoa(100)
	fmt.Println("  Itoa(100):", s)

	// FormatFloat
	fs := strconv.FormatFloat(3.14, 'f', 2, 64)
	fmt.Println("  FormatFloat(3.14):", fs)

	fmt.Println()
}

// =====================================================================
// 레슨 3 — sort: 정렬
// =====================================================================
func lesson3Sort() {
	fmt.Println("[레슨 3] sort: 슬라이스 정렬하기")
	fmt.Println()

	// 정수 정렬
	nums := []int{42, 15, 88, 3, 67}
	fmt.Println("  정렬 전:", nums)
	sort.Ints(nums)
	fmt.Println("  정렬 후:", nums)

	// 문자열 정렬
	names := []string{"지우", "민수", "서연", "하준"}
	sort.Strings(names)
	fmt.Println("  이름 정렬:", names)

	// 커스텀 정렬: 점수 높은 순
	type Student struct {
		Name  string
		Score int
	}
	students := []Student{
		{"민수", 85}, {"지우", 92}, {"서연", 78}, {"하준", 96},
	}

	sort.Slice(students, func(i, j int) bool {
		return students[i].Score > students[j].Score // 내림차순
	})

	fmt.Println("  점수 높은 순:")
	for _, s := range students {
		fmt.Printf("    %s: %d점\n", s.Name, s.Score)
	}

	// 이진 탐색
	sorted := []int{3, 15, 42, 67, 88}
	idx := sort.SearchInts(sorted, 42)
	fmt.Printf("  이진 탐색: 42는 인덱스 %d에 있음\n", idx)

	fmt.Println()
}

// =====================================================================
// 레슨 4 — time: 시간 다루기
// =====================================================================
func lesson4Time() {
	fmt.Println("[레슨 4] time: 시간과 날짜 다루기")
	fmt.Println()

	/*
	   ★ Go의 시간 포맷은 독특하다!
	   다른 언어: "YYYY-MM-DD HH:mm:ss"
	   Go:        "2006-01-02 15:04:05"  ← 이 숫자를 외워야 한다!

	   왜 2006-01-02 15:04:05 인가?
	   → Mon Jan 2 15:04:05 MST 2006
	   → 1월 2일 3시(15시) 4분 5초 2006년
	   → 1-2-3-4-5-6 순서!
	*/

	now := time.Now()
	fmt.Println("  현재 시각:", now)
	fmt.Println("  포맷:", now.Format("2006-01-02 15:04:05"))
	fmt.Println("  날짜만:", now.Format("2006/01/02"))
	fmt.Println("  시간만:", now.Format("15:04"))

	// 시간 만들기
	birthday := time.Date(2000, time.March, 15, 0, 0, 0, 0, time.Local)
	fmt.Println("  생일:", birthday.Format("2006-01-02"))

	// 시간 차이
	age := now.Sub(birthday)
	fmt.Printf("  나이: 약 %.0f일\n", age.Hours()/24)

	// 시간 더하기
	tomorrow := now.Add(24 * time.Hour)
	fmt.Println("  내일:", tomorrow.Format("2006-01-02"))

	// 시간 비교
	fmt.Println("  now > birthday:", now.After(birthday))

	// 타이머 (실행 시간 측정에 유용)
	start := time.Now()
	time.Sleep(10 * time.Millisecond)
	elapsed := time.Since(start)
	fmt.Printf("  경과 시간: %v\n", elapsed)

	fmt.Println()
}

// =====================================================================
// 레슨 5 — 파일 I/O
// =====================================================================
func lesson5FileIO() {
	fmt.Println("[레슨 5] 파일 읽기/쓰기: os 패키지")
	fmt.Println()

	/*
	   ★ 파일 쓰기/읽기의 가장 간단한 방법:
	   os.WriteFile(이름, 데이터, 권한)
	   os.ReadFile(이름)
	*/

	filename := "temp_test_file.txt"

	// 파일 쓰기
	content := "안녕하세요!\nGo로 파일을 써 봤습니다.\n점수: 100점"
	err := os.WriteFile(filename, []byte(content), 0644)
	if err != nil {
		fmt.Println("  쓰기 에러:", err)
		return
	}
	fmt.Println("  파일 쓰기 완료:", filename)

	// 파일 읽기
	data, err := os.ReadFile(filename)
	if err != nil {
		fmt.Println("  읽기 에러:", err)
		return
	}
	fmt.Println("  파일 내용:")
	for i, line := range strings.Split(string(data), "\n") {
		fmt.Printf("    %d: %s\n", i+1, line)
	}

	// 파일 정보
	info, err := os.Stat(filename)
	if err == nil {
		fmt.Printf("  파일 크기: %d 바이트\n", info.Size())
		fmt.Println("  수정 시각:", info.ModTime().Format("15:04:05"))
	}

	// 정리: 임시 파일 삭제
	os.Remove(filename)
	fmt.Println("  임시 파일 삭제 완료")

	// 파일 존재 여부 확인
	_, err = os.Stat(filename)
	if os.IsNotExist(err) {
		fmt.Println("  파일이 삭제되어 존재하지 않음 (확인)")
	}

	fmt.Println()
}

// =====================================================================
// 레슨 6 — JSON 다루기
// =====================================================================

// StudentJSON — JSON 변환용 구조체
type StudentJSON struct {
	Name  string `json:"name"`           // JSON 키 이름 지정
	Score int    `json:"score"`          // 소문자로 변환
	Grade string `json:"grade,omitempty"` // 비어있으면 JSON에서 생략
}

func lesson6JSON() {
	fmt.Println("[레슨 6] encoding/json: Go ↔ JSON 변환")
	fmt.Println()

	/*
	   ★ 구조체 태그로 JSON 키 이름을 제어한다:
	   `json:"name"`            → 키를 "name"으로
	   `json:"score,omitempty"` → 제로값이면 생략
	   `json:"-"`               → JSON에 포함 안 함
	*/

	// Go → JSON (Marshal)
	s := StudentJSON{Name: "민수", Score: 95, Grade: "우수"}
	jsonBytes, _ := json.Marshal(s)
	fmt.Println("  Marshal:", string(jsonBytes))

	// 예쁘게 출력 (MarshalIndent)
	pretty, _ := json.MarshalIndent(s, "  ", "    ")
	fmt.Println("  MarshalIndent:")
	fmt.Println(" ", string(pretty))

	// JSON → Go (Unmarshal)
	jsonStr := `{"name":"지우","score":88}`
	var s2 StudentJSON
	json.Unmarshal([]byte(jsonStr), &s2)
	fmt.Printf("  Unmarshal: %+v\n", s2)

	// 슬라이스 JSON
	students := []StudentJSON{
		{Name: "서연", Score: 92},
		{Name: "하준", Score: 78},
	}
	listJSON, _ := json.Marshal(students)
	fmt.Println("  슬라이스 JSON:", string(listJSON))

	// map → JSON
	data := map[string]any{
		"school": "Go 초등학교",
		"year":   2024,
		"open":   true,
	}
	mapJSON, _ := json.MarshalIndent(data, "  ", "    ")
	fmt.Println("  맵 JSON:")
	fmt.Println(" ", string(mapJSON))

	fmt.Println()
}

// =====================================================================
// 레슨 7 — fmt 포맷 동사(verb) 총정리
// =====================================================================
func lesson7FmtVerbs() {
	fmt.Println("[레슨 7] fmt 포맷 동사 총정리")
	fmt.Println()

	/*
	   ┌──────────┬──────────────────────────────┐
	   │  동사     │  설명                         │
	   ├──────────┼──────────────────────────────┤
	   │  %v      │  기본 형식                     │
	   │  %+v     │  필드 이름 포함 (구조체)        │
	   │  %#v     │  Go 문법 형식                  │
	   │  %T      │  타입 이름                     │
	   │  %d      │  정수 (10진수)                 │
	   │  %b      │  정수 (2진수)                  │
	   │  %x      │  정수 (16진수)                 │
	   │  %f      │  실수                         │
	   │  %.2f    │  소수점 2자리                  │
	   │  %s      │  문자열                        │
	   │  %q      │  따옴표 포함 문자열             │
	   │  %p      │  포인터 주소                   │
	   │  %t      │  bool (true/false)            │
	   │  %%      │  리터럴 %                      │
	   └──────────┴──────────────────────────────┘
	*/

	s := StudentJSON{Name: "민수", Score: 95}
	num := 42

	fmt.Printf("  %%v:  %v\n", s)
	fmt.Printf("  %%+v: %+v\n", s)
	fmt.Printf("  %%#v: %#v\n", s)
	fmt.Printf("  %%T:  %T\n", s)
	fmt.Printf("  %%d:  %d\n", num)
	fmt.Printf("  %%b:  %b\n", num)
	fmt.Printf("  %%x:  %x\n", num)
	fmt.Printf("  %%s:  %s\n", "hello")
	fmt.Printf("  %%q:  %q\n", "hello")
	fmt.Printf("  %%t:  %t\n", true)
	fmt.Printf("  %%09d: %09d (0으로 채우기)\n", num)
	fmt.Printf("  %%-10s: '%-10s' (왼쪽 정렬)\n", "Go")

	fmt.Println()
}

// =====================================================================
// 레슨 8 — 알아두면 좋은 표준 라이브러리 패키지들
// =====================================================================
func lesson8UsefulPackages() {
	fmt.Println("[레슨 8] 자주 쓰는 표준 라이브러리 패키지 목록")
	fmt.Println()

	fmt.Println("  ┌──────────────────┬──────────────────────────────────┐")
	fmt.Println("  │  패키지           │  용도                            │")
	fmt.Println("  ├──────────────────┼──────────────────────────────────┤")
	fmt.Println("  │  fmt             │  출력, 포맷팅                     │")
	fmt.Println("  │  strings         │  문자열 조작                      │")
	fmt.Println("  │  strconv         │  문자열 ↔ 숫자 변환               │")
	fmt.Println("  │  sort            │  정렬                            │")
	fmt.Println("  │  time            │  시간, 타이머                     │")
	fmt.Println("  │  os              │  파일, 환경변수, 프로세스          │")
	fmt.Println("  │  io              │  Reader/Writer 인터페이스          │")
	fmt.Println("  │  bufio           │  버퍼 I/O (줄 단위 읽기)          │")
	fmt.Println("  │  encoding/json   │  JSON 변환                       │")
	fmt.Println("  │  net/http        │  HTTP 서버/클라이언트              │")
	fmt.Println("  │  path/filepath   │  파일 경로 조작                   │")
	fmt.Println("  │  sync            │  동기화 (Mutex, WaitGroup 등)     │")
	fmt.Println("  │  context         │  취소 신호, 타임아웃               │")
	fmt.Println("  │  errors          │  에러 래핑, Is, As                │")
	fmt.Println("  │  log             │  로깅                            │")
	fmt.Println("  │  regexp          │  정규 표현식                      │")
	fmt.Println("  │  math            │  수학 함수                        │")
	fmt.Println("  │  crypto/sha256   │  해시                            │")
	fmt.Println("  └──────────────────┴──────────────────────────────────┘")

	fmt.Println()
}
