# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# ■ 파일명: Dockerfile.go
# ■ 목적: Go 멀티스테이지 빌드 - scratch 기반 초경량 이미지
# ■ 비교: golang 이미지 ~800MB → scratch ~10MB
# ■ 빌드: docker build -f Dockerfile.go -t go-optimized .
# ■ 날짜: 2026-03-21
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ============================================================
# 스테이지 1: 빌드 (Build)
# ============================================================
# Go 컴파일러가 있는 이미지에서 빌드
FROM golang:1.23-alpine AS builder

# 빌드에 필요한 도구 설치
# git = go mod가 의존성을 다운로드할 때 필요
# ca-certificates = HTTPS 통신에 필요한 인증서
RUN apk add --no-cache git ca-certificates

WORKDIR /build

# 의존성 파일 먼저 복사 (레이어 캐싱!)
# go.mod, go.sum이 바뀌지 않으면 다시 다운로드 안 해
COPY go.mod go.sum* ./
RUN go mod download

# 소스코드 복사
COPY . .

# Go 바이너리 컴파일
# CGO_ENABLED=0 = C 라이브러리 의존성 없이 순수 Go로 컴파일
#   → scratch 이미지에서 실행 가능! (C 라이브러리가 없으니까)
# GOOS=linux = Linux용으로 컴파일
# -ldflags="-s -w" = 디버그 정보 제거 → 바이너리 크기 줄이기
#   -s = 심볼 테이블 제거
#   -w = DWARF 디버그 정보 제거
# -o /app = 출력 파일 경로
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-s -w" \
    -o /app \
    ./cmd/server

# ============================================================
# 스테이지 2: 프로덕션 (scratch)
# ============================================================
# scratch = 완전히 비어있는 이미지! (0 바이트)
# OS도 없고, 셸도 없고, 아무것도 없어
# Go 바이너리 하나만 넣으면 그것만 실행돼
# 장점: 공격 표면이 거의 없어 (보안 최강!)
# 단점: 셸이 없어서 exec으로 디버깅 불가
FROM scratch

# builder에서 인증서 복사 (HTTPS 호출 시 필요)
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# 컴파일된 바이너리 하나만 복사!
# Go는 의존성을 모두 바이너리에 포함하기 때문에 이것만 있으면 돼
COPY --from=builder /app /app

# 포트 문서화
EXPOSE 8080

# 바이너리 직접 실행
ENTRYPOINT ["/app"]

# ============================================================
# 결과:
# golang:1.23 이미지: ~800MB
# 최종 이미지 (scratch + 바이너리): ~5~15MB
#
# 80배 이상 줄어들어!
# 그리고 OS가 없으니 취약점도 거의 없어
# ============================================================
