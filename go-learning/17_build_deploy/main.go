/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Go 학습 17단계: 빌드와 배포
  ─ go build · 크로스 컴파일 · 빌드 태그 · Docker · ldflags · Makefile ─

  [학습 목표]
  1. go build의 다양한 옵션을 안다
  2. 크로스 컴파일(GOOS/GOARCH)을 안다
  3. ldflags로 빌드 시 변수 주입을 안다
  4. Docker 멀티스테이지 빌드를 안다
  5. Makefile로 빌드를 자동화한다

  ■ 실행: go run main.go
  ■ 빌드: go build -o 17_deploy main.go

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

package main

import (
	"fmt"
	"runtime"
	"strings"
)

// 빌드 시 ldflags로 주입되는 변수들
var (
	version   = "dev"
	buildDate = "unknown"
	gitCommit = "unknown"
)

func main() {
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println("  Go 17단계 : 빌드와 배포")
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println()

	lesson1BuildBasics()
	lesson2CrossCompilation()
	lesson3LDFlags()
	lesson4BuildTags()
	lesson5DockerBuild()
	lesson6Makefile()
	lesson7CIGitHubActions()
	lesson8DeploymentChecklist()

	fmt.Println("17단계 학습 완료!")
}

// =====================================================================
// 레슨 1 — go build 기초
// =====================================================================
func lesson1BuildBasics() {
	fmt.Println("[레슨 1] go build: 소스 코드를 실행 파일로")
	fmt.Println()

	/*
	   ★ go build = Go 소스를 컴파일하여 실행 파일 생성

	   ┌─────────────────────────────────────────────────────────┐
	   │  명령어                          │  설명                 │
	   ├─────────────────────────────────────────────────────────┤
	   │  go build                        │  현재 폴더 빌드       │
	   │  go build -o myapp               │  출력 파일명 지정      │
	   │  go build -o myapp ./cmd/server  │  특정 패키지 빌드      │
	   │  go run main.go                  │  빌드+실행 (개발용)    │
	   │  go install                      │  빌드+$GOPATH/bin 설치│
	   └─────────────────────────────────────────────────────────┘

	   ★ go build vs go run:
	   go build → 실행 파일 생성 (배포용)
	   go run   → 임시 빌드 후 즉시 실행 (개발용, 파일 안 남음)
	*/

	fmt.Println("  현재 환경:")
	fmt.Printf("    OS:   %s\n", runtime.GOOS)
	fmt.Printf("    Arch: %s\n", runtime.GOARCH)
	fmt.Printf("    Go:   %s\n", runtime.Version())
	fmt.Printf("    CPU:  %d코어\n", runtime.NumCPU())

	fmt.Println()
	fmt.Println("  빌드 명령어:")
	fmt.Println("    go build -o myapp main.go")
	fmt.Println("    go build -o myapp ./cmd/server/")

	fmt.Println()
}

// =====================================================================
// 레슨 2 — 크로스 컴파일
// =====================================================================
func lesson2CrossCompilation() {
	fmt.Println("[레슨 2] 크로스 컴파일: 다른 OS/아키텍처용 빌드")
	fmt.Println()

	/*
	   ★ Go의 강력한 기능: 환경 변수만 바꾸면 다른 OS용 바이너리 생성!

	   ┌──────────────────────────────────────────────────────────────┐
	   │  GOOS=linux   GOARCH=amd64  go build -o myapp-linux         │
	   │  GOOS=darwin  GOARCH=arm64  go build -o myapp-mac           │
	   │  GOOS=windows GOARCH=amd64  go build -o myapp.exe           │
	   └──────────────────────────────────────────────────────────────┘

	   ★ 주요 GOOS 값: linux, darwin(macOS), windows, freebsd
	   ★ 주요 GOARCH 값: amd64(x86_64), arm64(Apple Silicon, ARM), 386

	   ★ 지원되는 모든 조합 확인:
	   go tool dist list
	*/

	targets := []struct {
		os   string
		arch string
		ext  string
	}{
		{"linux", "amd64", ""},
		{"linux", "arm64", ""},
		{"darwin", "amd64", ""},
		{"darwin", "arm64", ""},
		{"windows", "amd64", ".exe"},
	}

	fmt.Println("  주요 크로스 컴파일 명령어:")
	for _, t := range targets {
		name := fmt.Sprintf("myapp-%s-%s%s", t.os, t.arch, t.ext)
		cmd := fmt.Sprintf("GOOS=%s GOARCH=%s go build -o %s", t.os, t.arch, name)
		fmt.Printf("    %s\n", cmd)
	}

	/*
	   ★ CGO와 크로스 컴파일:
	   CGO를 사용하는 패키지(예: go-sqlite3)는 크로스 컴파일이 어렵다!
	   → CGO_ENABLED=0 으로 순수 Go만 사용하도록 강제 가능
	   → 또는 Docker로 해당 OS에서 빌드
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 3 — ldflags: 빌드 시 변수 주입
// =====================================================================
func lesson3LDFlags() {
	fmt.Println("[레슨 3] ldflags: 빌드할 때 버전/날짜를 코드에 심기")
	fmt.Println()

	/*
	   ★ ldflags = 링커 플래그. 빌드할 때 Go 변수의 값을 주입!

	   코드:
	   var version = "dev"      ← 기본값

	   빌드:
	   go build -ldflags "-X main.version=1.2.3" -o myapp

	   → 실행하면 version이 "1.2.3"으로 바뀌어 있다!

	   ★ 실전에서 자주 주입하는 값:
	   -X main.version=$(git describe --tags)
	   -X main.buildDate=$(date -u +%Y-%m-%dT%H:%M:%SZ)
	   -X main.gitCommit=$(git rev-parse --short HEAD)
	*/

	fmt.Println("  현재 빌드 정보:")
	fmt.Printf("    version:   %s\n", version)
	fmt.Printf("    buildDate: %s\n", buildDate)
	fmt.Printf("    gitCommit: %s\n", gitCommit)

	fmt.Println()
	fmt.Println("  빌드 명령어 예시:")
	fmt.Println("    go build -ldflags \"-X main.version=1.0.0 \\")
	fmt.Println("      -X main.buildDate=$(date -u +%Y-%m-%dT%H:%M:%SZ) \\")
	fmt.Println("      -X main.gitCommit=$(git rev-parse --short HEAD)\" \\")
	fmt.Println("      -o myapp main.go")

	/*
	   ★ 바이너리 크기 줄이기:
	   go build -ldflags "-s -w" -o myapp
	   -s → 심볼 테이블 제거
	   -w → DWARF 디버그 정보 제거
	   → 보통 20~30% 크기 감소!
	*/

	fmt.Println()
	fmt.Println("  바이너리 크기 줄이기:")
	fmt.Println("    go build -ldflags \"-s -w\" -o myapp")
	fmt.Println("    → 심볼/디버그 제거로 20~30% 감소")

	fmt.Println()
}

// =====================================================================
// 레슨 4 — 빌드 태그
// =====================================================================
func lesson4BuildTags() {
	fmt.Println("[레슨 4] 빌드 태그: 조건부 컴파일")
	fmt.Println()

	/*
	   ★ 빌드 태그 = 특정 조건에서만 파일을 컴파일에 포함

	   파일 맨 위에 작성:
	   //go:build linux
	   → 이 파일은 Linux에서만 컴파일된다!

	   //go:build !windows
	   → Windows를 제외한 모든 OS에서 컴파일

	   //go:build integration
	   → go test -tags integration 할 때만 포함

	   ★ 활용 예:
	   ┌──────────────────────────────────────────────┐
	   │  db_postgres.go   //go:build postgres         │
	   │  db_mysql.go      //go:build mysql            │
	   │  db_sqlite.go     //go:build sqlite           │
	   │                                              │
	   │  go build -tags postgres  ← PostgreSQL 전용!  │
	   └──────────────────────────────────────────────┘

	   ★ 파일 이름으로도 가능:
	   utils_linux.go    → Linux에서만 컴파일
	   utils_windows.go  → Windows에서만 컴파일
	   utils_test.go     → 테스트에서만 컴파일
	*/

	fmt.Println("  파일 상단: //go:build linux")
	fmt.Println("  빌드: go build -tags integration")
	fmt.Println("  파일명: xxx_linux.go → 자동으로 Linux 전용")

	fmt.Println()
}

// =====================================================================
// 레슨 5 — Docker 멀티스테이지 빌드
// =====================================================================
func lesson5DockerBuild() {
	fmt.Println("[레슨 5] Docker: 멀티스테이지 빌드로 최소 이미지 만들기")
	fmt.Println()

	/*
	   ★ 멀티스테이지 빌드 = 빌드 환경과 실행 환경을 분리

	   빌드 스테이지: Go 컴파일러 + 소스 → 바이너리
	   실행 스테이지: 바이너리만 복사 → 아주 작은 이미지!
	*/

	dockerfile := `# ── Dockerfile ──
# 1단계: 빌드 (Go 이미지 사용)
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags "-s -w" -o /app/server ./cmd/server

# 2단계: 실행 (최소 이미지!)
FROM alpine:3.19
RUN apk add --no-cache ca-certificates tzdata
COPY --from=builder /app/server /usr/local/bin/server
EXPOSE 8080
CMD ["server"]`

	fmt.Println("  Dockerfile (멀티스테이지):")
	for _, line := range strings.Split(dockerfile, "\n") {
		fmt.Println("    " + line)
	}

	/*
	   ★ 이미지 크기 비교:
	   golang:1.22         → ~800MB
	   golang:1.22-alpine  → ~250MB
	   alpine:3.19         → ~7MB
	   scratch             → ~0MB (빈 이미지!)

	   멀티스테이지로 최종 이미지: ~15MB (바이너리 + alpine)
	   scratch 사용 시: 바이너리 크기만큼 (~10MB)
	*/

	fmt.Println()
	fmt.Println("  이미지 크기 비교:")
	fmt.Println("    golang:1.22  → ~800MB")
	fmt.Println("    alpine:3.19  → ~7MB")
	fmt.Println("    최종 (멀티스테이지) → ~15MB!")

	fmt.Println()
}

// =====================================================================
// 레슨 6 — Makefile
// =====================================================================
func lesson6Makefile() {
	fmt.Println("[레슨 6] Makefile: 빌드 명령을 자동화")
	fmt.Println()

	makefile := `# ── Makefile ──
APP_NAME := student-api
VERSION  := $(shell git describe --tags --always)
BUILD    := $(shell date -u +%Y-%m-%dT%H:%M:%SZ)
LDFLAGS  := -ldflags "-X main.version=$(VERSION) -X main.buildDate=$(BUILD) -s -w"

.PHONY: build run test clean docker

build:
    go build $(LDFLAGS) -o bin/$(APP_NAME) ./cmd/server

run:
    go run ./cmd/server

test:
    go test -v -race ./...

cover:
    go test -cover -coverprofile=coverage.out ./...
    go tool cover -html=coverage.out

lint:
    golangci-lint run ./...

clean:
    rm -rf bin/ coverage.out

docker:
    docker build -t $(APP_NAME):$(VERSION) .

cross:
    GOOS=linux GOARCH=amd64 go build $(LDFLAGS) -o bin/$(APP_NAME)-linux-amd64
    GOOS=darwin GOARCH=arm64 go build $(LDFLAGS) -o bin/$(APP_NAME)-darwin-arm64
    GOOS=windows GOARCH=amd64 go build $(LDFLAGS) -o bin/$(APP_NAME).exe`

	fmt.Println("  Makefile 예시:")
	for _, line := range strings.Split(makefile, "\n") {
		fmt.Println("    " + line)
	}

	fmt.Println()
	fmt.Println("  사용: make build / make test / make docker")

	fmt.Println()
}

// =====================================================================
// 레슨 7 — CI/CD (GitHub Actions)
// =====================================================================
func lesson7CIGitHubActions() {
	fmt.Println("[레슨 7] GitHub Actions: 자동 빌드/테스트/배포")
	fmt.Println()

	workflow := `# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
      - run: go mod download
      - run: go test -v -race ./...
      - run: go build -o /dev/null ./...`

	fmt.Println("  GitHub Actions 예시:")
	for _, line := range strings.Split(workflow, "\n") {
		fmt.Println("    " + line)
	}

	fmt.Println()

}

// =====================================================================
// 레슨 8 — 배포 체크리스트
// =====================================================================
func lesson8DeploymentChecklist() {
	fmt.Println("[레슨 8] 배포 전 체크리스트")
	fmt.Println()

	fmt.Println("  ┌────────────────────────────────────────────────────────┐")
	fmt.Println("  │  □ go test -race ./... 통과                           │")
	fmt.Println("  │  □ go vet ./... 경고 없음                             │")
	fmt.Println("  │  □ golangci-lint 통과                                 │")
	fmt.Println("  │  □ go mod tidy 실행 (불필요한 의존성 정리)              │")
	fmt.Println("  │  □ 버전 태그 (git tag v1.0.0)                         │")
	fmt.Println("  │  □ ldflags로 버전 정보 주입                            │")
	fmt.Println("  │  □ -s -w 플래그로 바이너리 크기 최적화                  │")
	fmt.Println("  │  □ 크로스 컴파일 대상 OS 확인                          │")
	fmt.Println("  │  □ Docker 이미지 멀티스테이지 빌드                     │")
	fmt.Println("  │  □ 환경 변수로 설정 분리 (하드코딩 금지!)               │")
	fmt.Println("  │  □ 헬스체크 엔드포인트 (/health)                       │")
	fmt.Println("  │  □ 로그 레벨 설정 가능                                 │")
	fmt.Println("  │  □ graceful shutdown 구현                             │")
	fmt.Println("  │  □ CI/CD 파이프라인 설정                               │")
	fmt.Println("  └────────────────────────────────────────────────────────┘")

	fmt.Println()
}
