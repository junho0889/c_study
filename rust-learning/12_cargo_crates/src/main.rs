/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Rust 학습 12단계: Cargo와 크레이트 (Modules & Crates)
  ─ mod, pub, use, Cargo.toml, 프로젝트 구조, 의존성 관리 ─

  [학습 목표]
  1. Cargo 의 주요 명령어를 안다
  2. 모듈(mod) 시스템으로 코드를 정리한다
  3. pub 으로 공개 범위를 제어한다
  4. use 로 경로를 짧게 가져온다
  5. Cargo.toml 에서 의존성을 관리한다
  6. 바이너리 크레이트와 라이브러리 크레이트를 구분한다
  7. 워크스페이스를 이해한다

  ■ 실행: cargo run
  ■ 빌드: cargo build --release

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// =====================================================================
// 레슨 1 — Cargo 필수 명령어
// =====================================================================
/*
★ Cargo = Rust 의 빌드 시스템 + 패키지 매니저
  → C/C++ 의 make + CMake + vcpkg 를 하나로 합친 것!

  ┌──────────────────────┬──────────────────────────────────────┐
  │ cargo new 프로젝트명 │ 새 프로젝트 생성                     │
  │ cargo build          │ 컴파일 (디버그 모드)                 │
  │ cargo build --release│ 컴파일 (최적화, 배포용)              │
  │ cargo run            │ 컴파일 + 실행                        │
  │ cargo test           │ 테스트 실행                          │
  │ cargo check          │ 컴파일 가능한지만 확인 (빠름!)       │
  │ cargo clippy         │ 코드 품질 검사 (린트)                │
  │ cargo fmt            │ 코드 자동 포맷팅                     │
  │ cargo doc --open     │ 문서 생성 + 브라우저 열기            │
  │ cargo update         │ 의존성 업데이트                      │
  │ cargo clean          │ 빌드 결과물 삭제                     │
  │ cargo add 크레이트명 │ 의존성 추가 (Cargo.toml 자동 수정)  │
  └──────────────────────┴──────────────────────────────────────┘

★ cargo check vs cargo build
  → check 는 실행 파일을 만들지 않아서 훨씬 빠름!
  → 코드 작성 중에는 check, 실행할 때만 build/run 사용
*/

fn lesson1_cargo_commands() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 1: Cargo 필수 명령어");
    println!("═══════════════════════════════════════════");

    println!("  ┌─────────────────────────────────────────┐");
    println!("  │ 개발 흐름 (가장 흔한 순서)              │");
    println!("  ├─────────────────────────────────────────┤");
    println!("  │ 1. cargo new my_project                 │");
    println!("  │ 2. 코드 작성                            │");
    println!("  │ 3. cargo check    (빠른 문법 확인)      │");
    println!("  │ 4. cargo run      (실행)                │");
    println!("  │ 5. cargo test     (테스트)              │");
    println!("  │ 6. cargo clippy   (품질 검사)           │");
    println!("  │ 7. cargo build --release (배포용 빌드)  │");
    println!("  └─────────────────────────────────────────┘");
    println!();
}

// =====================================================================
// 레슨 2 — 모듈(mod): 코드를 서랍장처럼 정리하기
// =====================================================================
/*
★ 모듈 = 코드를 구역별로 나누는 방법

  비유: 서랍장
  ┌──────────────────────────────────────────┐
  │ 서랍장 (크레이트)                       │
  │ ┌────────────────────┐                  │
  │ │ 1번 서랍 (mod math)│                  │
  │ │  → add(), mul()    │                  │
  │ ├────────────────────┤                  │
  │ │ 2번 서랍 (mod text)│                  │
  │ │  → format(), pad() │                  │
  │ └────────────────────┘                  │
  └──────────────────────────────────────────┘

★ 공개 범위(visibility)
  ┌──────────────┬────────────────────────────────────┐
  │ 기본         │ 비공개 (같은 모듈 내에서만)         │
  │ pub          │ 외부에서 접근 가능                  │
  │ pub(crate)   │ 같은 크레이트 내에서만              │
  │ pub(super)   │ 부모 모듈에서만                     │
  └──────────────┴────────────────────────────────────┘
*/

// ── 인라인 모듈 정의 ──
mod math {
    // pub 이 없으면 모듈 바깥에서 사용 불가!
    pub fn add(a: i32, b: i32) -> i32 {
        a + b
    }

    pub fn multiply(a: i32, b: i32) -> i32 {
        a * b
    }

    // 비공개 함수: 이 모듈 안에서만 사용 가능
    fn _internal_helper() -> i32 {
        42
    }

    // ── 중첩 모듈 ──
    pub mod advanced {
        pub fn power(base: i32, exp: u32) -> i32 {
            (0..exp).fold(1, |acc, _| acc * base)
        }
    }
}

mod text {
    pub fn repeat_string(s: &str, n: usize) -> String {
        s.repeat(n)
    }

    pub fn capitalize_first(s: &str) -> String {
        let mut chars = s.chars();
        match chars.next() {
            None    => String::new(),
            Some(c) => c.to_uppercase().to_string() + chars.as_str(),
        }
    }
}

fn lesson2_modules() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 2: 모듈 시스템");
    println!("═══════════════════════════════════════════");

    // ── 전체 경로로 접근 ──
    println!("  math::add(3, 4) = {}", math::add(3, 4));
    println!("  math::multiply(5, 6) = {}", math::multiply(5, 6));

    // ── 중첩 모듈 접근 ──
    println!("  math::advanced::power(2, 10) = {}", math::advanced::power(2, 10));

    // ── use 로 짧게 가져오기 ──
    use text::capitalize_first;
    println!("  capitalize: {}", capitalize_first("hello rust"));
    println!("  repeat: {}", text::repeat_string("ha", 3));
    println!();
}

// =====================================================================
// 레슨 3 — use 경로와 재내보내기(re-export)
// =====================================================================
/*
★ use 의 다양한 형태

  ┌──────────────────────────────────────────────────────────┐
  │ use std::collections::HashMap;      // 하나만 가져오기   │
  │ use std::collections::{HashMap, HashSet};  // 여러 개    │
  │ use std::io::*;                     // 전부 가져오기     │
  │ use std::io::Result as IoResult;    // 별칭 붙이기       │
  │ pub use internal::Config;           // 재내보내기        │
  └──────────────────────────────────────────────────────────┘

★ 재내보내기(re-export)
  → 내부 모듈의 항목을 상위 모듈에서 직접 접근 가능하게
  → 라이브러리 API 설계에서 매우 중요!

  비유: 백화점 1층 안내 데스크
  → 3층에 있는 매장을 1층에서도 안내해주는 것
*/

mod store {
    // 내부 모듈
    mod inventory {
        pub struct Product {
            pub name: String,
            pub price: u32,
        }

        impl Product {
            pub fn new(name: &str, price: u32) -> Self {
                Product { name: name.to_string(), price }
            }
        }
    }

    // pub use 로 재내보내기 → store::Product 로 접근 가능!
    pub use inventory::Product;

    pub fn create_sample_products() -> Vec<Product> {
        vec![
            Product::new("노트북", 1_500_000),
            Product::new("마우스", 35_000),
            Product::new("키보드", 89_000),
        ]
    }
}

fn lesson3_use_and_reexport() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 3: use 경로와 재내보내기");
    println!("═══════════════════════════════════════════");

    // 재내보내기 덕분에 store::Product 로 바로 접근
    use store::Product;
    let laptop = Product::new("태블릿", 800_000);
    println!("  제품: {} - {}원", laptop.name, laptop.price);

    let products = store::create_sample_products();
    for p in &products {
        println!("    {} → {}원", p.name, p.price);
    }
    println!();
}

// =====================================================================
// 레슨 4 — Cargo.toml: 프로젝트 설정 파일
// =====================================================================
/*
★ Cargo.toml 은 프로젝트의 신분증

  ┌────────────────────────────────────────────────────────────┐
  │ [package]                                                  │
  │ name = "my_project"         # 크레이트 이름               │
  │ version = "0.1.0"           # 버전 (SemVer)               │
  │ edition = "2021"            # Rust 에디션                  │
  │ authors = ["Kim <kim@ex.com>"]                            │
  │ description = "설명"                                      │
  │                                                            │
  │ [dependencies]              # 외부 의존성                  │
  │ serde = "1.0"               # 최신 1.x                    │
  │ serde = "=1.0.193"          # 정확한 버전                  │
  │ serde = { version = "1", features = ["derive"] }          │
  │ tokio = { version = "1", features = ["full"] }            │
  │                                                            │
  │ [dev-dependencies]          # 테스트/벤치마크 전용         │
  │ criterion = "0.5"                                         │
  │                                                            │
  │ [profile.release]           # 릴리스 최적화 설정          │
  │ opt-level = 3                                             │
  │ lto = true                                                │
  └────────────────────────────────────────────────────────────┘

★ SemVer (Semantic Versioning)
  ┌───────────────────────────────────────────────────────────┐
  │ major.minor.patch                                        │
  │  1   . 4  .  2                                           │
  │  ↑     ↑     ↑                                           │
  │  호환X 기능추가 버그수정                                  │
  │                                                           │
  │ "1.0"  → 1.0.0 이상 2.0.0 미만 (^1.0.0 과 동일)        │
  │ "=1.4" → 정확히 1.4.x                                   │
  │ ">=1, <2" → 1.0 이상 2.0 미만                           │
  └───────────────────────────────────────────────────────────┘
*/

fn lesson4_cargo_toml() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 4: Cargo.toml 설정");
    println!("═══════════════════════════════════════════");

    println!("  ★ 자주 사용하는 크레이트 (crates.io):");
    println!("  ┌────────────────┬─────────────────────────────┐");
    println!("  │ serde          │ 직렬화/역직렬화 (JSON 등)   │");
    println!("  │ tokio          │ 비동기 런타임                │");
    println!("  │ reqwest        │ HTTP 클라이언트             │");
    println!("  │ clap           │ CLI 인자 파싱               │");
    println!("  │ anyhow         │ 간편한 에러 처리            │");
    println!("  │ thiserror      │ 커스텀 에러 매크로          │");
    println!("  │ tracing        │ 로깅/추적                   │");
    println!("  │ rand           │ 난수 생성                   │");
    println!("  │ chrono         │ 날짜/시간 처리              │");
    println!("  │ regex          │ 정규표현식                   │");
    println!("  └────────────────┴─────────────────────────────┘");
    println!();

    println!("  ★ 의존성 추가 방법:");
    println!("    cargo add serde --features derive");
    println!("    → Cargo.toml 에 자동으로 추가됩니다");
    println!();
}

// =====================================================================
// 레슨 5 — 파일로 모듈 분리하기
// =====================================================================
/*
★ 프로젝트가 커지면 모듈을 별도 파일로 분리합니다

  방법 1 (2018 에디션 이후 권장):
  ┌─────────────────────────────┐
  │ src/                        │
  │ ├── main.rs                 │
  │ ├── math.rs      ← mod math│
  │ └── text.rs      ← mod text│
  └─────────────────────────────┘

  방법 2 (하위 모듈이 있을 때):
  ┌──────────────────────────────────┐
  │ src/                             │
  │ ├── main.rs                      │
  │ ├── math/                        │
  │ │   ├── mod.rs    ← mod math     │
  │ │   ├── basic.rs  ← 기본 연산   │
  │ │   └── advanced.rs ← 고급 연산 │
  │ └── text.rs                      │
  └──────────────────────────────────┘

  main.rs 에서:
  ┌──────────────────────────────┐
  │ mod math;     // math.rs 또는 math/mod.rs 를 찾음
  │ mod text;     // text.rs 를 찾음
  │
  │ use math::add;
  │ use text::capitalize;
  └──────────────────────────────┘
*/

fn lesson5_file_modules() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 5: 파일로 모듈 분리");
    println!("═══════════════════════════════════════════");

    println!("  실제 프로젝트 구조 예시:");
    println!();
    println!("  my_app/");
    println!("  ├── Cargo.toml");
    println!("  ├── src/");
    println!("  │   ├── main.rs       ← 진입점");
    println!("  │   ├── lib.rs        ← 라이브러리 루트 (선택)");
    println!("  │   ├── config.rs     ← mod config");
    println!("  │   ├── db/");
    println!("  │   │   ├── mod.rs    ← mod db");
    println!("  │   │   ├── models.rs");
    println!("  │   │   └── queries.rs");
    println!("  │   └── api/");
    println!("  │       ├── mod.rs    ← mod api");
    println!("  │       ├── routes.rs");
    println!("  │       └── handlers.rs");
    println!("  └── tests/            ← 통합 테스트");
    println!("      └── integration_test.rs");
    println!();
}

// =====================================================================
// 레슨 6 — 바이너리 vs 라이브러리 크레이트
// =====================================================================
/*
★ 크레이트의 두 종류

  ┌──────────────────────────────────────────────────────────┐
  │ 바이너리 크레이트 (Binary Crate)                         │
  │ → src/main.rs 가 있음                                    │
  │ → cargo run 으로 실행 가능                               │
  │ → 결과물: 실행 파일                                      │
  │ → 비유: 완성된 장난감                                    │
  ├──────────────────────────────────────────────────────────┤
  │ 라이브러리 크레이트 (Library Crate)                      │
  │ → src/lib.rs 가 있음                                     │
  │ → 다른 크레이트가 use 로 가져다 씀                       │
  │ → 결과물: .rlib 파일                                     │
  │ → 비유: 레고 부품 상자                                   │
  ├──────────────────────────────────────────────────────────┤
  │ 둘 다 가능!                                              │
  │ → main.rs + lib.rs 둘 다 있으면                          │
  │   바이너리가 자기 라이브러리를 use 할 수 있음             │
  └──────────────────────────────────────────────────────────┘
*/

fn lesson6_binary_vs_library() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 6: 바이너리 vs 라이브러리 크레이트");
    println!("═══════════════════════════════════════════");

    println!("  cargo new my_app          → 바이너리 (기본)");
    println!("  cargo new my_lib --lib    → 라이브러리");
    println!();
    println!("  ★ 실무 패턴: main.rs + lib.rs 조합");
    println!("    → lib.rs 에 핵심 로직");
    println!("    → main.rs 에서 lib.rs 의 함수 호출");
    println!("    → 테스트는 lib.rs 단위 테스트로 작성");
    println!("    → 다른 프로젝트에서도 라이브러리로 재사용 가능!");
    println!();
}

// =====================================================================
// 레슨 7 — 워크스페이스: 여러 크레이트 함께 관리
// =====================================================================
/*
★ 워크스페이스 = 여러 관련 크레이트를 하나의 Cargo.lock 으로 관리

  ┌──────────────────────────────────────────────┐
  │ my_workspace/                                │
  │ ├── Cargo.toml        ← 워크스페이스 루트    │
  │ ├── app/              ← 바이너리 크레이트    │
  │ │   ├── Cargo.toml                           │
  │ │   └── src/main.rs                          │
  │ ├── core_lib/         ← 라이브러리 크레이트  │
  │ │   ├── Cargo.toml                           │
  │ │   └── src/lib.rs                           │
  │ └── utils/            ← 유틸리티 크레이트    │
  │     ├── Cargo.toml                           │
  │     └── src/lib.rs                           │
  └──────────────────────────────────────────────┘

  루트 Cargo.toml:
  ┌──────────────────────────────────────────────┐
  │ [workspace]                                  │
  │ members = ["app", "core_lib", "utils"]       │
  └──────────────────────────────────────────────┘
*/

fn lesson7_workspace() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 7: 워크스페이스");
    println!("═══════════════════════════════════════════");

    println!("  ★ 워크스페이스의 장점:");
    println!("    1. 여러 크레이트가 같은 의존성 버전 공유");
    println!("    2. cargo build 한 번으로 전체 빌드");
    println!("    3. cargo test --workspace 로 전체 테스트");
    println!("    4. 크레이트 간 경로 의존성이 간편");
    println!();
    println!("  ★ 멤버 크레이트 간 의존:");
    println!("    [dependencies]");
    println!("    core_lib = {{ path = \"../core_lib\" }}");
    println!();
}

// =====================================================================
//  main
// =====================================================================

fn main() {
    println!();
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  Rust 12단계: Cargo와 크레이트");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!();

    lesson1_cargo_commands();
    lesson2_modules();
    lesson3_use_and_reexport();
    lesson4_cargo_toml();
    lesson5_file_modules();
    lesson6_binary_vs_library();
    lesson7_workspace();

    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  12단계 완료! 다음은 13_generics_lifetimes");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
}
