/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Rust 학습 17단계: 빌드와 배포
  ─ 빌드 프로파일, 조건부 컴파일, 크로스 컴파일, CI/CD ─

  [학습 목표]
  1. debug 와 release 빌드의 차이를 안다
  2. Cargo.toml 의 프로파일 설정을 이해한다
  3. 조건부 컴파일(cfg)을 사용한다
  4. 빌드 스크립트(build.rs)를 이해한다
  5. 크로스 컴파일 개념을 안다
  6. 배포 체크리스트를 파악한다

  ■ 실행: cargo run
  ■ 빌드: cargo build --release

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

use std::fs;

// =====================================================================
// 레슨 1 — 빌드 모드: debug vs release
// =====================================================================
/*
★ 두 가지 빌드 모드

  ┌────────────────────┬───────────────────────┬──────────────────────┐
  │                    │ Debug (기본)          │ Release              │
  ├────────────────────┼───────────────────────┼──────────────────────┤
  │ 명령어             │ cargo build           │ cargo build --release│
  │ 최적화             │ 없음 (opt-level=0)    │ 최대 (opt-level=3)   │
  │ 컴파일 속도        │ 빠름                  │ 느림                 │
  │ 실행 속도          │ 느림                  │ 빠름 (2~10배)        │
  │ 디버그 정보        │ 포함                  │ 기본 미포함          │
  │ 정수 오버플로우    │ panic!                │ 감싸기(wrap)         │
  │ debug_assert!      │ 실행됨                │ 무시됨               │
  │ 결과 위치          │ target/debug/         │ target/release/      │
  └────────────────────┴───────────────────────┴──────────────────────┘

  비유:
  ┌────────────────────────────────────────────────────────┐
  │ Debug   = 연필 스케치 (빠르게 그리고, 자주 고침)       │
  │ Release = 완성 포스터 (시간 들여 꼼꼼하게, 배포용)     │
  └────────────────────────────────────────────────────────┘
*/

fn lesson1_build_modes() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 1: debug vs release 빌드");
    println!("═══════════════════════════════════════════");

    // cfg! 매크로로 현재 빌드 모드 확인
    if cfg!(debug_assertions) {
        println!("  현재 모드: DEBUG");
        println!("  → 디버그 정보 포함, 최적화 없음");
    } else {
        println!("  현재 모드: RELEASE");
        println!("  → 최적화 적용, 더 빠르게 실행");
    }

    // debug_assert! 는 debug 모드에서만 실행
    debug_assert!(2 + 2 == 4, "디버그 모드에서만 이 검사 실행");
    println!("  debug_assert! 통과 (릴리스에서는 무시됨)");
    println!();

    // ── 성능 차이 데모 ──
    let n = 1_000_000;
    let start = std::time::Instant::now();
    let mut sum: u64 = 0;
    for i in 0..n {
        sum += i;
    }
    let elapsed = start.elapsed();
    println!("  1~{} 합계: {} ({:.3?})", n, sum, elapsed);
    println!("  ★ cargo build --release 로 빌드하면 훨씬 빠릅니다!");
    println!();
}

// =====================================================================
// 레슨 2 — Cargo.toml 프로파일 설정
// =====================================================================
/*
★ 프로파일 커스터마이징

  ┌────────────────────────────────────────────────────────────┐
  │ [profile.dev]                # cargo build                 │
  │ opt-level = 0                # 최적화 없음                 │
  │ debug = true                 # 디버그 정보 포함            │
  │ overflow-checks = true       # 정수 오버플로우 검사        │
  │                                                            │
  │ [profile.release]            # cargo build --release       │
  │ opt-level = 3                # 최대 최적화                 │
  │ lto = true                   # 링크 타임 최적화            │
  │ codegen-units = 1            # 단일 코드 생성 단위 (느림)  │
  │ strip = true                 # 심볼 제거 (바이너리 작아짐) │
  │ panic = "abort"              # panic 시 즉시 종료          │
  │                                                            │
  │ [profile.release-with-debug] # 커스텀 프로파일             │
  │ inherits = "release"                                       │
  │ debug = true                 # 릴리스 + 디버그 정보       │
  └────────────────────────────────────────────────────────────┘

★ opt-level 옵션
  ┌──────────────┬──────────────────────────┐
  │ 0            │ 최적화 없음 (디폴트 dev) │
  │ 1            │ 기본 최적화              │
  │ 2            │ 대부분의 최적화          │
  │ 3            │ 모든 최적화 (디폴트 rel) │
  │ "s"          │ 바이너리 크기 최적화     │
  │ "z"          │ 바이너리 크기 최소화     │
  └──────────────┴──────────────────────────┘
*/

fn lesson2_profile_settings() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 2: Cargo.toml 프로파일 설정");
    println!("═══════════════════════════════════════════");

    println!("  ★ 최소 바이너리 크기를 위한 설정:");
    println!("    [profile.release]");
    println!("    opt-level = \"z\"");
    println!("    lto = true");
    println!("    codegen-units = 1");
    println!("    strip = true");
    println!("    panic = \"abort\"");
    println!();

    println!("  ★ 최대 성능을 위한 설정:");
    println!("    [profile.release]");
    println!("    opt-level = 3");
    println!("    lto = \"fat\"");
    println!("    codegen-units = 1");
    println!("    target-cpu = \"native\"  (RUSTFLAGS)");
    println!();
}

// =====================================================================
// 레슨 3 — 조건부 컴파일 (cfg)
// =====================================================================
/*
★ cfg = 조건에 따라 코드를 포함/제외

  ┌──────────────────────────────────────────────────────────┐
  │ #[cfg(target_os = "windows")]                            │
  │ fn platform_greeting() { println!("Windows!"); }        │
  │                                                          │
  │ #[cfg(target_os = "linux")]                              │
  │ fn platform_greeting() { println!("Linux!"); }          │
  │                                                          │
  │ #[cfg(debug_assertions)]                                 │
  │ fn debug_only() { println!("디버그 모드에서만!"); }     │
  │                                                          │
  │ #[cfg(feature = "my_feature")]                           │
  │ fn optional_feature() { ... }                            │
  └──────────────────────────────────────────────────────────┘

★ cfg 조건 종류
  ┌──────────────────────┬──────────────────────────────────┐
  │ target_os            │ "windows", "linux", "macos"      │
  │ target_arch          │ "x86_64", "aarch64"              │
  │ target_family        │ "unix", "windows"                │
  │ debug_assertions     │ 디버그 모드인가?                 │
  │ test                 │ 테스트 중인가?                   │
  │ feature = "이름"     │ 피처 플래그                      │
  └──────────────────────┴──────────────────────────────────┘
*/

#[cfg(target_os = "windows")]
fn get_platform() -> &'static str { "Windows" }

#[cfg(target_os = "linux")]
fn get_platform() -> &'static str { "Linux" }

#[cfg(target_os = "macos")]
fn get_platform() -> &'static str { "macOS" }

#[cfg(not(any(target_os = "windows", target_os = "linux", target_os = "macos")))]
fn get_platform() -> &'static str { "기타 OS" }

fn lesson3_conditional_compilation() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 3: 조건부 컴파일 (cfg)");
    println!("═══════════════════════════════════════════");

    println!("  현재 플랫폼: {}", get_platform());
    println!("  아키텍처: {}", std::env::consts::ARCH);
    println!("  OS: {}", std::env::consts::OS);

    // cfg! 매크로 (표현식에서 사용)
    let is_64bit = cfg!(target_pointer_width = "64");
    println!("  64비트? {}", is_64bit);

    // 디버그 모드 분기
    if cfg!(debug_assertions) {
        println!("  [DEBUG] 추가 검사 활성화");
    } else {
        println!("  [RELEASE] 최적화 모드");
    }

    // ── 피처 플래그 설명 ──
    println!();
    println!("  ★ 피처 플래그 (Cargo.toml):");
    println!("    [features]");
    println!("    default = [\"json\"]");
    println!("    json = [\"serde_json\"]");
    println!("    xml = [\"quick-xml\"]");
    println!();
    println!("    사용: cargo build --features \"json,xml\"");
    println!("    코드: #[cfg(feature = \"json\")]");
    println!();
}

// =====================================================================
// 레슨 4 — 환경 변수와 빌드 정보
// =====================================================================
/*
★ 빌드 시점의 정보를 코드에 포함하기

  ┌──────────────────────────────────────────────────────────┐
  │ env!("CARGO_PKG_VERSION")  → "0.1.0" (Cargo.toml 버전) │
  │ env!("CARGO_PKG_NAME")    → "my_app" (패키지 이름)     │
  │ env!("CARGO_PKG_AUTHORS") → "작성자"                    │
  │ option_env!("MY_VAR")     → 환경 변수 (Option)         │
  │ file!()                   → 현재 파일 경로              │
  │ line!()                   → 현재 줄 번호                │
  │ column!()                 → 현재 열 번호                │
  └──────────────────────────────────────────────────────────┘
*/

fn lesson4_build_info() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 4: 환경 변수와 빌드 정보");
    println!("═══════════════════════════════════════════");

    println!("  패키지 이름: {}", env!("CARGO_PKG_NAME"));
    println!("  패키지 버전: {}", env!("CARGO_PKG_VERSION"));
    println!("  현재 파일:   {}", file!());
    println!("  현재 줄:     {}", line!());

    // 선택적 환경 변수
    match option_env!("RUST_LOG") {
        Some(level) => println!("  RUST_LOG: {}", level),
        None        => println!("  RUST_LOG: (설정 안 됨)"),
    }
    println!();
}

// =====================================================================
// 레슨 5 — 크로스 컴파일
// =====================================================================
/*
★ 크로스 컴파일 = 다른 OS/아키텍처용 바이너리를 내 컴퓨터에서 빌드

  ┌──────────────────────────────────────────────────────────┐
  │ 1. 타겟 추가                                            │
  │    rustup target add x86_64-unknown-linux-musl          │
  │    rustup target add aarch64-unknown-linux-gnu          │
  │                                                          │
  │ 2. 빌드                                                 │
  │    cargo build --release --target x86_64-unknown-linux-musl│
  │                                                          │
  │ 3. 결과물                                               │
  │    target/x86_64-unknown-linux-musl/release/my_app      │
  └──────────────────────────────────────────────────────────┘

★ 자주 쓰는 타겟
  ┌────────────────────────────────┬──────────────────────────┐
  │ x86_64-unknown-linux-gnu      │ Linux (동적 링크)        │
  │ x86_64-unknown-linux-musl     │ Linux (정적 링크, 이식성)│
  │ x86_64-pc-windows-msvc        │ Windows (MSVC)           │
  │ x86_64-pc-windows-gnu         │ Windows (MinGW)          │
  │ x86_64-apple-darwin           │ macOS (Intel)            │
  │ aarch64-apple-darwin          │ macOS (Apple Silicon)    │
  │ aarch64-unknown-linux-gnu     │ Linux ARM64              │
  │ wasm32-unknown-unknown        │ WebAssembly              │
  └────────────────────────────────┴──────────────────────────┘
*/

fn lesson5_cross_compilation() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 5: 크로스 컴파일");
    println!("═══════════════════════════════════════════");

    println!("  ★ 설치된 타겟 확인: rustup target list --installed");
    println!("  ★ 타겟 추가: rustup target add <타겟>");
    println!("  ★ 빌드: cargo build --release --target <타겟>");
    println!();
    println!("  ★ 정적 링크 (Linux musl):");
    println!("    → 시스템 라이브러리 의존성 없이 어디서든 실행!");
    println!("    → Docker 배포에 매우 유용");
    println!();
    println!("  ★ cross 도구 (Docker 기반 크로스 컴파일):");
    println!("    cargo install cross");
    println!("    cross build --release --target aarch64-unknown-linux-gnu");
    println!();
}

// =====================================================================
// 레슨 6 — 배포 파일 생성
// =====================================================================

fn lesson6_manifest_file() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 6: 배포 매니페스트 파일");
    println!("═══════════════════════════════════════════");

    let version = env!("CARGO_PKG_VERSION");
    let name = env!("CARGO_PKG_NAME");

    let content = format!(
        "# 배포 정보\n\
         app={}\n\
         version={}\n\
         platform={}\n\
         arch={}\n\
         build_mode={}\n\
         entry=target/release/{}\n",
        name, version, std::env::consts::OS, std::env::consts::ARCH,
        if cfg!(debug_assertions) { "debug" } else { "release" },
        name,
    );

    match fs::write("rust_publish_manifest.txt", &content) {
        Ok(_) => {
            println!("  rust_publish_manifest.txt 생성 완료!");
            println!();
            println!("  내용:");
            for line in content.lines() {
                println!("    {}", line);
            }
        }
        Err(e) => {
            println!("  파일 생성 실패: {}", e);
        }
    }
    println!();
}

// =====================================================================
// 레슨 7 — CI/CD 와 배포 체크리스트
// =====================================================================
/*
★ CI/CD 파이프라인 (GitHub Actions 예시)

  ┌──────────────────────────────────────────────────────────┐
  │ name: Rust CI                                            │
  │ on: [push, pull_request]                                │
  │ jobs:                                                    │
  │   test:                                                  │
  │     runs-on: ubuntu-latest                               │
  │     steps:                                               │
  │       - uses: actions/checkout@v4                        │
  │       - uses: dtolnay/rust-toolchain@stable             │
  │       - run: cargo fmt -- --check                       │
  │       - run: cargo clippy -- -D warnings                │
  │       - run: cargo test                                  │
  │       - run: cargo build --release                      │
  └──────────────────────────────────────────────────────────┘
*/

fn lesson7_cicd_checklist() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 7: 배포 체크리스트");
    println!("═══════════════════════════════════════════");

    println!("  ┌──────────────────────────────────────────────┐");
    println!("  │ 배포 전 체크리스트                           │");
    println!("  ├──────────────────────────────────────────────┤");
    println!("  │ [ ] cargo fmt -- --check (포맷 확인)         │");
    println!("  │ [ ] cargo clippy -- -D warnings (린트)       │");
    println!("  │ [ ] cargo test (모든 테스트 통과)            │");
    println!("  │ [ ] cargo build --release (릴리스 빌드)      │");
    println!("  │ [ ] Cargo.toml 버전 업데이트                 │");
    println!("  │ [ ] CHANGELOG 작성                           │");
    println!("  │ [ ] 의존성 보안 검사 (cargo audit)           │");
    println!("  │ [ ] 라이선스 확인                            │");
    println!("  │ [ ] README 업데이트                          │");
    println!("  │ [ ] git tag 생성                             │");
    println!("  └──────────────────────────────────────────────┘");
    println!();

    println!("  ★ crates.io 에 발행하기:");
    println!("    cargo login");
    println!("    cargo publish --dry-run   (먼저 시험)");
    println!("    cargo publish             (실제 발행)");
    println!();

    println!("  ★ Docker 배포:");
    println!("    FROM rust:1.77 as builder");
    println!("    WORKDIR /app");
    println!("    COPY . .");
    println!("    RUN cargo build --release");
    println!();
    println!("    FROM debian:bookworm-slim");
    println!("    COPY --from=builder /app/target/release/my_app /usr/local/bin/");
    println!("    CMD [\"my_app\"]");
    println!();
}

// =====================================================================
//  main
// =====================================================================

fn main() {
    println!();
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  Rust 17단계: 빌드와 배포");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!();

    lesson1_build_modes();
    lesson2_profile_settings();
    lesson3_conditional_compilation();
    lesson4_build_info();
    lesson5_cross_compilation();
    lesson6_manifest_file();
    lesson7_cicd_checklist();

    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  17단계 완료! 다음은 18_real_project 입니다");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
}
