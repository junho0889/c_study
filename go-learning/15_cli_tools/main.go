/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Go 학습 15단계: CLI 도구 만들기
  ─ os.Args · flag 패키지 · 서브커맨드 · 입출력 · 종료 코드 ─

  [학습 목표]
  1. os.Args로 명령줄 인자를 받는 법을 안다
  2. flag 패키지로 옵션을 파싱하는 법을 안다
  3. 서브커맨드 패턴을 안다
  4. stdin/stdout/stderr의 역할을 안다
  5. 종료 코드와 에러 처리 패턴을 안다

  ■ 실행: go run main.go
  ■ 빌드: go build -o 15_cli main.go

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

package main

import (
	"flag"
	"fmt"
	"io"
	"os"
	"strings"
)

func main() {
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println("  Go 15단계 : CLI 도구 만들기")
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println()

	lesson1OsArgs()
	lesson2FlagPackage()
	lesson3FlagSet()
	lesson4SubcommandPattern()
	lesson5StdinStdout()
	lesson6ExitCodes()
	lesson7RealCLIExample()
	lesson8CLIBestPractices()

	fmt.Println("15단계 학습 완료!")
}

// =====================================================================
// 레슨 1 — os.Args: 가장 기본적인 인자 받기
// =====================================================================
func lesson1OsArgs() {
	fmt.Println("[레슨 1] os.Args: 명령줄 인자의 원시 접근")
	fmt.Println()

	/*
	   ★ os.Args = 프로그램 실행 시 전달된 인자들의 슬라이스

	   $ ./myapp hello world
	   os.Args[0] = "./myapp"    ← 프로그램 이름
	   os.Args[1] = "hello"
	   os.Args[2] = "world"

	   ┌────────────────────────────────────────────────┐
	   │  os.Args[0]    → 항상 프로그램 이름/경로         │
	   │  os.Args[1:]   → 실제 인자들                    │
	   │  len(os.Args)  → 인자 개수 (프로그램 이름 포함)   │
	   └────────────────────────────────────────────────┘
	*/

	// 실행 시뮬레이션
	simArgs := []string{"./student-tool", "add", "민수", "85"}
	fmt.Println("  시뮬레이션 os.Args:", simArgs)
	fmt.Println("  프로그램:", simArgs[0])
	fmt.Println("  인자들:", simArgs[1:])

	// 실제 os.Args
	fmt.Println("  실제 os.Args:", os.Args)

	/*
	   ★ os.Args는 단순하지만 불편하다:
	   - 옵션(--name, --count)을 직접 파싱해야 한다
	   - 도움말을 직접 만들어야 한다
	   → flag 패키지를 쓰자!
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 2 — flag 패키지: 옵션 파싱
// =====================================================================
func lesson2FlagPackage() {
	fmt.Println("[레슨 2] flag 패키지: --name, --count 같은 옵션 처리")
	fmt.Println()

	/*
	   ★ flag 패키지 = 명령줄 옵션을 자동으로 파싱해 준다

	   ──────────────────────────────────────────
	   // 정의
	   name := flag.String("name", "기본값", "설명")
	   count := flag.Int("count", 1, "반복 횟수")
	   verbose := flag.Bool("verbose", false, "상세 출력")

	   // 파싱
	   flag.Parse()

	   // 사용 (포인터이므로 *로 꺼내기)
	   fmt.Println(*name, *count, *verbose)

	   // 나머지 인자 (옵션이 아닌 것들)
	   fmt.Println(flag.Args())
	   ──────────────────────────────────────────

	   사용 예:
	   $ ./tool --name 민수 --count 3 extra1 extra2
	   name="민수"  count=3  Args=["extra1", "extra2"]
	*/

	// 시뮬레이션: FlagSet 사용 (기본 flag는 os.Args를 건드려서)
	fs := flag.NewFlagSet("demo", flag.ContinueOnError)
	fs.SetOutput(io.Discard) // 에러 메시지 숨기기

	name := fs.String("name", "세계", "인사 대상")
	count := fs.Int("count", 1, "반복 횟수")
	upper := fs.Bool("upper", false, "대문자로")

	// 가상 인자
	simArgs := []string{"--name", "민수", "--count", "3", "--upper"}
	fs.Parse(simArgs)

	fmt.Printf("  가상 인자: %v\n", simArgs)
	fmt.Printf("  name=%s  count=%d  upper=%v\n", *name, *count, *upper)

	// 결과 생성
	msg := fmt.Sprintf("안녕, %s!", *name)
	if *upper {
		msg = strings.ToUpper(msg)
	}
	for i := 0; i < *count; i++ {
		fmt.Printf("  [%d] %s\n", i+1, msg)
	}

	fmt.Println()
}

// =====================================================================
// 레슨 3 — FlagSet: 여러 명령 세트
// =====================================================================
func lesson3FlagSet() {
	fmt.Println("[레슨 3] FlagSet: 서브커맨드별로 다른 옵션 세트")
	fmt.Println()

	/*
	   ★ flag.NewFlagSet = 독립적인 옵션 세트를 만든다

	   왜 필요한가?
	   기본 flag는 전역이라 서브커맨드마다 다른 옵션을 줄 수 없다!

	   $ myapp add --name 민수 --score 85
	   $ myapp list --min-score 70
	   → add와 list의 옵션이 다르다!
	*/

	// add 서브커맨드
	addCmd := flag.NewFlagSet("add", flag.ContinueOnError)
	addCmd.SetOutput(io.Discard)
	addName := addCmd.String("name", "", "학생 이름")
	addScore := addCmd.Int("score", 0, "점수")

	// list 서브커맨드
	listCmd := flag.NewFlagSet("list", flag.ContinueOnError)
	listCmd.SetOutput(io.Discard)
	listMin := listCmd.Int("min-score", 0, "최소 점수 필터")

	// add 시뮬레이션
	addCmd.Parse([]string{"--name", "서연", "--score", "92"})
	fmt.Printf("  [add] name=%s score=%d\n", *addName, *addScore)

	// list 시뮬레이션
	listCmd.Parse([]string{"--min-score", "80"})
	fmt.Printf("  [list] min-score=%d\n", *listMin)

	fmt.Println()
}

// =====================================================================
// 레슨 4 — 서브커맨드 패턴
// =====================================================================

type CLIApp struct {
	students []struct {
		Name  string
		Score int
	}
}

func (app *CLIApp) RunAdd(name string, score int) string {
	app.students = append(app.students, struct {
		Name  string
		Score int
	}{name, score})
	return fmt.Sprintf("'%s'(%d점) 추가 완료", name, score)
}

func (app *CLIApp) RunList(minScore int) string {
	var b strings.Builder
	for _, s := range app.students {
		if s.Score >= minScore {
			fmt.Fprintf(&b, "  %s: %d점\n", s.Name, s.Score)
		}
	}
	if b.Len() == 0 {
		return "  (조건에 맞는 학생 없음)"
	}
	return b.String()
}

func lesson4SubcommandPattern() {
	fmt.Println("[레슨 4] 서브커맨드: git처럼 동작별로 명령 나누기")
	fmt.Println()

	/*
	   ★ 서브커맨드 패턴:
	   $ myapp add --name 민수 --score 85
	   $ myapp list --min-score 70
	   $ myapp version

	   구현:
	   switch os.Args[1] {
	   case "add":
	       addCmd.Parse(os.Args[2:])
	   case "list":
	       listCmd.Parse(os.Args[2:])
	   default:
	       fmt.Println("알 수 없는 명령:", os.Args[1])
	       os.Exit(1)
	   }
	*/

	app := &CLIApp{}

	// 시뮬레이션
	commands := []struct {
		cmd  string
		args string
	}{
		{"add", "--name 민수 --score 85"},
		{"add", "--name 지우 --score 92"},
		{"add", "--name 하준 --score 68"},
		{"list", "--min-score 70"},
		{"list", "--min-score 0"},
	}

	for _, c := range commands {
		fmt.Printf("  $ myapp %s %s\n", c.cmd, c.args)
		switch c.cmd {
		case "add":
			fs := flag.NewFlagSet("add", flag.ContinueOnError)
			fs.SetOutput(io.Discard)
			n := fs.String("name", "", "")
			s := fs.Int("score", 0, "")
			fs.Parse(strings.Split(c.args, " "))
			fmt.Println("   →", app.RunAdd(*n, *s))
		case "list":
			fs := flag.NewFlagSet("list", flag.ContinueOnError)
			fs.SetOutput(io.Discard)
			min := fs.Int("min-score", 0, "")
			fs.Parse(strings.Split(c.args, " "))
			fmt.Println("   →")
			fmt.Print(app.RunList(*min))
		}
	}

	fmt.Println()
}

// =====================================================================
// 레슨 5 — stdin/stdout/stderr
// =====================================================================
func lesson5StdinStdout() {
	fmt.Println("[레슨 5] stdin/stdout/stderr: 3개의 표준 스트림")
	fmt.Println()

	/*
	   ★ 3개의 표준 스트림:

	   ┌──────────────────────────────────────────────────┐
	   │  stdin  (os.Stdin)   ← 입력 (키보드, 파이프)       │
	   │  stdout (os.Stdout)  ← 정상 출력                   │
	   │  stderr (os.Stderr)  ← 에러 출력                   │
	   └──────────────────────────────────────────────────┘

	   ★ 왜 stdout과 stderr를 구분하나?
	   $ myapp > output.txt
	   → stdout만 파일로 가고, 에러는 화면에 남는다!
	   → 정상 결과와 에러 메시지를 분리할 수 있다!

	   ★ 파이프로 다른 프로그램에 전달:
	   $ echo "hello" | myapp    ← stdin으로 "hello" 전달
	   $ myapp | grep "결과"     ← stdout을 grep에 전달
	*/

	// stdout으로 출력 (기본)
	fmt.Fprintln(os.Stdout, "  이것은 stdout (정상 출력)")

	// stderr로 출력
	fmt.Fprintln(os.Stderr, "  이것은 stderr (에러 출력)")

	/*
	   ★ stdin에서 읽기:
	   scanner := bufio.NewScanner(os.Stdin)
	   for scanner.Scan() {
	       line := scanner.Text()
	       // 한 줄씩 처리
	   }
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 6 — 종료 코드
// =====================================================================
func lesson6ExitCodes() {
	fmt.Println("[레슨 6] 종료 코드: 프로그램이 성공했는지 알려주기")
	fmt.Println()

	/*
	   ★ 종료 코드 (Exit Code):
	   0   → 성공!
	   1   → 일반 에러
	   2   → 잘못된 사용법 (인자 오류)

	   ┌────────────────────────────────────────────────┐
	   │  os.Exit(0)    → 정상 종료 (defer 실행 안 됨!)   │
	   │  os.Exit(1)    → 에러 종료                      │
	   │  return        → main에서 return은 Exit(0)과 같음 │
	   └────────────────────────────────────────────────┘

	   ★★★ 주의: os.Exit()는 defer를 실행하지 않는다! ★★★
	   → 정리 작업이 있으면 os.Exit 전에 직접 실행해야 한다

	   ★ 쉘에서 종료 코드 확인:
	   $ myapp; echo $?
	   0    ← 성공

	   $ myapp --invalid; echo $?
	   2    ← 사용법 에러
	*/

	// 패턴: main에서 실제 로직 함수를 호출하고 종료 코드를 반환
	fmt.Println("  권장 패턴:")
	fmt.Println("  func main() {")
	fmt.Println("      os.Exit(run())")
	fmt.Println("  }")
	fmt.Println("  func run() int {")
	fmt.Println("      // 로직...")
	fmt.Println("      if err != nil { return 1 }")
	fmt.Println("      return 0")
	fmt.Println("  }")

	fmt.Println()
}

// =====================================================================
// 레슨 7 — 실전 CLI 예제: 간식 보고서 생성기
// =====================================================================

type SnackConfig struct {
	Name   string
	Count  int
	Upper  bool
	Output string
}

func parseSnackCommand(args []string) (SnackConfig, error) {
	var config SnackConfig

	fs := flag.NewFlagSet("snack", flag.ContinueOnError)
	fs.SetOutput(io.Discard)
	fs.StringVar(&config.Name, "name", "", "간식 이름")
	fs.IntVar(&config.Count, "count", 1, "반복 횟수")
	fs.BoolVar(&config.Upper, "upper", false, "대문자 출력")
	fs.StringVar(&config.Output, "output", "", "출력 파일 (비면 stdout)")

	err := fs.Parse(args)
	if err != nil {
		return config, err
	}

	if config.Name == "" {
		return config, fmt.Errorf("--name 은 필수입니다")
	}
	if config.Count < 1 {
		return config, fmt.Errorf("--count 는 1 이상이어야 합니다")
	}

	return config, nil
}

func generateSnackReport(config SnackConfig) string {
	var b strings.Builder
	b.WriteString("=== 간식 보고서 ===\n")
	for i := 1; i <= config.Count; i++ {
		line := fmt.Sprintf("%d. %s", i, config.Name)
		if config.Upper {
			line = strings.ToUpper(line)
		}
		b.WriteString(line + "\n")
	}
	b.WriteString("==================\n")
	return b.String()
}

func lesson7RealCLIExample() {
	fmt.Println("[레슨 7] 실전 예제: 간식 보고서 생성기")
	fmt.Println()

	testCases := []struct {
		desc string
		args []string
	}{
		{"정상", []string{"--name", "초코파이", "--count", "3"}},
		{"대문자", []string{"--name", "cookies", "--count", "2", "--upper"}},
		{"이름 누락", []string{"--count", "5"}},
		{"잘못된 횟수", []string{"--name", "사탕", "--count", "0"}},
	}

	for _, tc := range testCases {
		fmt.Printf("  [%s] 인자: %v\n", tc.desc, tc.args)
		config, err := parseSnackCommand(tc.args)
		if err != nil {
			fmt.Printf("    에러: %s\n", err)
		} else {
			report := generateSnackReport(config)
			for _, line := range strings.Split(strings.TrimSpace(report), "\n") {
				fmt.Printf("    %s\n", line)
			}
		}
		fmt.Println()
	}
}

// =====================================================================
// 레슨 8 — CLI 모범 사례
// =====================================================================
func lesson8CLIBestPractices() {
	fmt.Println("[레슨 8] CLI 도구 모범 사례")
	fmt.Println()

	fmt.Println("  ┌────────────────────────────────────────────────────────┐")
	fmt.Println("  │  1. --help를 반드시 제공 (flag는 자동 생성!)            │")
	fmt.Println("  │  2. 종료 코드: 0=성공, 1=에러, 2=사용법 오류           │")
	fmt.Println("  │  3. 에러 메시지는 stderr로 (fmt.Fprintln(os.Stderr))   │")
	fmt.Println("  │  4. 정상 출력은 stdout으로 (파이프 호환)                │")
	fmt.Println("  │  5. 무음 모드(--quiet)와 상세 모드(--verbose) 제공      │")
	fmt.Println("  │  6. 긴 옵션 이름 사용 (--output vs -o)                 │")
	fmt.Println("  │  7. 설정 파일 지원 (JSON/YAML/TOML)                   │")
	fmt.Println("  │  8. 버전 표시 (myapp --version)                       │")
	fmt.Println("  │  9. 시그널 처리 (Ctrl+C → 깔끔한 종료)                 │")
	fmt.Println("  │  10. 큰 CLI는 cobra/urfave/cli 라이브러리 사용         │")
	fmt.Println("  └────────────────────────────────────────────────────────┘")

	fmt.Println()
	fmt.Println("  ★ 인기 CLI 라이브러리:")
	fmt.Println("    cobra   → kubectl, docker, hugo가 사용")
	fmt.Println("    urfave/cli → 간단한 CLI에 적합")
	fmt.Println("    pflag   → POSIX 호환 플래그 파싱")

	fmt.Println()
}
