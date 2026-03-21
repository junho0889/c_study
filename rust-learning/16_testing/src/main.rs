/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Rust 학습 16단계: 테스트 (Testing)
  ─ 단위 테스트, 통합 테스트, 문서 테스트, 테스트 조직 ─

  [학습 목표]
  1. #[test] 와 assert 매크로로 단위 테스트를 작성한다
  2. #[should_panic] 으로 패닉 테스트를 한다
  3. Result<T, E> 를 반환하는 테스트를 작성한다
  4. 테스트 필터링과 실행 옵션을 안다
  5. 통합 테스트의 구조를 이해한다
  6. 문서 테스트를 작성한다

  ■ 실행: cargo run (예시 출력)
  ■ 테스트: cargo test

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// =====================================================================
// 테스트 대상 함수들
// =====================================================================

/// 할인가를 계산합니다.
///
/// # Arguments
/// * `total` - 원래 가격
/// * `percent` - 할인율 (0~100)
///
/// # Panics
/// `percent` 가 0~100 범위 밖이면 panic
///
/// # Examples
/// ```
/// let result = apply_discount(10000, 10);
/// assert_eq!(result, 9000);
/// ```
fn apply_discount(total: i32, percent: i32) -> i32 {
    if !(0..=100).contains(&percent) {
        panic!("할인율은 0~100 사이여야 합니다. 입력값: {}", percent);
    }
    total - total * percent / 100
}

/// 두 수의 평균을 계산합니다. 빈 슬라이스면 None 반환.
fn safe_average(numbers: &[f64]) -> Option<f64> {
    if numbers.is_empty() {
        return None;
    }
    let sum: f64 = numbers.iter().sum();
    Some(sum / numbers.len() as f64)
}

/// 문자열을 정수로 파싱합니다.
fn parse_score(input: &str) -> Result<i32, String> {
    input.trim().parse::<i32>()
        .map_err(|e| format!("'{}' 파싱 실패: {}", input, e))
}

/// 성적 등급을 반환합니다.
fn grade(score: i32) -> &'static str {
    match score {
        90..=100 => "A",
        80..=89  => "B",
        70..=79  => "C",
        60..=69  => "D",
        0..=59   => "F",
        _        => "범위 밖",
    }
}

#[derive(Debug, PartialEq)]
struct Student {
    name: String,
    score: i32,
}

impl Student {
    fn new(name: &str, score: i32) -> Self {
        Student { name: name.to_string(), score }
    }

    fn is_passing(&self) -> bool {
        self.score >= 60
    }

    fn grade(&self) -> &str {
        grade(self.score)
    }
}

// =====================================================================
// 레슨 1 — 단위 테스트 기초
// =====================================================================
/*
★ 단위 테스트 = 함수 하나하나를 개별적으로 검증

  ┌──────────────────────────────────────────────────────┐
  │ #[cfg(test)]         → 테스트 빌드에서만 컴파일     │
  │ mod tests {          → 테스트 모듈                   │
  │     use super::*;    → 부모 모듈의 모든 항목 가져옴 │
  │                                                      │
  │     #[test]          → 이 함수는 테스트!            │
  │     fn test_name() {                                 │
  │         assert_eq!(1 + 1, 2);                       │
  │     }                                                │
  │ }                                                    │
  └──────────────────────────────────────────────────────┘

★ assert 매크로들
  ┌────────────────────────┬───────────────────────────────┐
  │ assert!(조건)          │ 조건이 true 인지 검증         │
  │ assert_eq!(a, b)       │ a == b 인지 (같으면 통과)    │
  │ assert_ne!(a, b)       │ a != b 인지 (다르면 통과)    │
  │ assert!(a, "메시지 {}") │ 실패 시 메시지 출력         │
  └────────────────────────┴───────────────────────────────┘
*/

fn lesson1_unit_test_basics() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 1: 단위 테스트 기초");
    println!("═══════════════════════════════════════════");

    // 테스트를 손으로 먼저 확인
    let cases = [
        (10_000, 10, 9_000),
        (5_000, 0, 5_000),
        (8_000, 25, 6_000),
        (20_000, 50, 10_000),
        (1_000, 100, 0),
    ];

    println!("  ┌──────────┬────────┬────────┬────────┬────────┐");
    println!("  │ 원가     │ 할인%  │ 예상   │ 실제   │ 결과   │");
    println!("  ├──────────┼────────┼────────┼────────┼────────┤");
    for (total, percent, expected) in cases {
        let actual = apply_discount(total, percent);
        let status = if actual == expected { "통과" } else { "실패!" };
        println!("  │ {:>8} │ {:>5}% │ {:>6} │ {:>6} │ {}   │",
                 total, percent, expected, actual, status);
    }
    println!("  └──────────┴────────┴────────┴────────┴────────┘");
    println!();
    println!("  ★ cargo test 로 자동 검증하세요!");
    println!();
}

// =====================================================================
// 레슨 2 — 다양한 테스트 패턴
// =====================================================================
/*
★ 테스트 패턴 모음

  ┌────────────────────────┬──────────────────────────────────┐
  │ #[should_panic]        │ panic 이 발생해야 통과           │
  │ #[should_panic(        │ 특정 메시지가 포함된 panic       │
  │   expected = "메시지")]│                                  │
  │ #[ignore]              │ 기본 실행 시 건너뜀              │
  │                        │ cargo test -- --ignored 로 실행 │
  │ Result<(), E> 반환     │ ? 연산자 사용 가능              │
  └────────────────────────┴──────────────────────────────────┘
*/

fn lesson2_test_patterns() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 2: 다양한 테스트 패턴");
    println!("═══════════════════════════════════════════");

    println!("  [패턴 1] 기본 assert_eq!");
    println!("    assert_eq!(apply_discount(10000, 10), 9000);");
    println!();

    println!("  [패턴 2] should_panic 테스트");
    println!("    #[should_panic(expected = \"0~100\")]");
    println!("    fn test_invalid_percent() {{");
    println!("        apply_discount(1000, 150);  // panic 발생!");
    println!("    }}");
    println!();

    println!("  [패턴 3] Result 반환 테스트");
    println!("    #[test]");
    println!("    fn test_parse() -> Result<(), String> {{");
    println!("        let score = parse_score(\"85\")?;");
    println!("        assert_eq!(score, 85);");
    println!("        Ok(())");
    println!("    }}");
    println!();

    println!("  [패턴 4] ignore 테스트 (느린 테스트)");
    println!("    #[test]");
    println!("    #[ignore]");
    println!("    fn test_heavy_computation() {{ ... }}");
    println!("    → cargo test -- --ignored 로 실행");
    println!();
}

// =====================================================================
// 레슨 3 — 테스트 실행 옵션
// =====================================================================
/*
★ cargo test 옵션들

  ┌──────────────────────────────────┬──────────────────────────────┐
  │ cargo test                      │ 모든 테스트 실행             │
  │ cargo test 함수이름             │ 이름에 맞는 테스트만         │
  │ cargo test -- --nocapture       │ println! 출력 보이기         │
  │ cargo test -- --test-threads=1  │ 단일 스레드로 실행           │
  │ cargo test -- --ignored         │ #[ignore] 테스트만 실행      │
  │ cargo test -- --include-ignored │ 무시 + 일반 모두 실행       │
  │ cargo test --lib                │ lib 테스트만                 │
  │ cargo test --doc                │ 문서 테스트만                │
  └──────────────────────────────────┴──────────────────────────────┘

★ 테스트 출력 형식:
  ┌──────────────────────────────────────────────────────────────┐
  │ running 5 tests                                              │
  │ test tests::test_discount_10 ... ok                         │
  │ test tests::test_discount_0 ... ok                          │
  │ test tests::test_invalid_panic ... ok                       │
  │ test tests::test_average_empty ... ok                       │
  │ test tests::test_parse_ok ... ok                            │
  │                                                              │
  │ test result: ok. 5 passed; 0 failed; 0 ignored              │
  └──────────────────────────────────────────────────────────────┘
*/

fn lesson3_test_options() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 3: 테스트 실행 옵션");
    println!("═══════════════════════════════════════════");

    println!("  ★ 자주 쓰는 명령어:");
    println!("    cargo test                         전체 실행");
    println!("    cargo test discount                discount 포함 테스트만");
    println!("    cargo test -- --nocapture           출력 보기");
    println!("    cargo test -- --test-threads=1      순차 실행");
    println!();
}

// =====================================================================
// 레슨 4 — 통합 테스트
// =====================================================================
/*
★ 통합 테스트 = 외부 사용자 관점에서 공개 API 테스트

  ┌──────────────────────────────────────────────────────┐
  │ 프로젝트 구조:                                       │
  │                                                      │
  │ my_project/                                          │
  │ ├── src/                                             │
  │ │   ├── main.rs  또는  lib.rs                        │
  │ ├── tests/              ← 통합 테스트 폴더          │
  │ │   ├── discount_test.rs                             │
  │ │   └── student_test.rs                              │
  │ └── Cargo.toml                                       │
  └──────────────────────────────────────────────────────┘

  tests/discount_test.rs:
  ┌──────────────────────────────────────────────────────┐
  │ use my_project::apply_discount;  // pub 함수만 접근 │
  │                                                      │
  │ #[test]                                              │
  │ fn test_from_outside() {                             │
  │     assert_eq!(apply_discount(10000, 10), 9000);    │
  │ }                                                    │
  └──────────────────────────────────────────────────────┘

★ 단위 테스트 vs 통합 테스트
  ┌─────────────┬──────────────────┬──────────────────────┐
  │             │ 단위 테스트      │ 통합 테스트          │
  ├─────────────┼──────────────────┼──────────────────────┤
  │ 위치        │ src/ 안 같은 파일│ tests/ 폴더          │
  │ 접근 범위   │ 비공개 함수도 OK │ pub 함수만           │
  │ 목적        │ 함수 하나 검증   │ 모듈 간 연동 검증   │
  │ #[cfg(test)]│ 필요             │ 불필요 (자동 적용)  │
  └─────────────┴──────────────────┴──────────────────────┘
*/

fn lesson4_integration_tests() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 4: 통합 테스트");
    println!("═══════════════════════════════════════════");

    println!("  ★ 통합 테스트는 tests/ 폴더에 작성합니다");
    println!("  ★ lib.rs 의 pub 함수만 테스트 가능합니다");
    println!("  ★ 바이너리 크레이트(main.rs만)는 통합 테스트 불가!");
    println!("    → 해결: main.rs + lib.rs 구조로 분리");
    println!("    → lib.rs 에 로직, main.rs 에서 호출");
    println!();
}

// =====================================================================
// 레슨 5 — 문서 테스트
// =====================================================================
/*
★ 문서 테스트 = 문서 주석(///) 안의 코드 블록이 자동으로 테스트됨!

  ┌──────────────────────────────────────────────────────┐
  │ /// 두 수를 더합니다.                                │
  │ ///                                                  │
  │ /// # Examples                                       │
  │ ///                                                  │
  │ /// ```                                              │
  │ /// let result = my_crate::add(2, 3);               │
  │ /// assert_eq!(result, 5);                           │
  │ /// ```                                              │
  │ pub fn add(a: i32, b: i32) -> i32 {                 │
  │     a + b                                            │
  │ }                                                    │
  └──────────────────────────────────────────────────────┘

  → cargo test --doc 으로 문서 예제 코드를 실행!
  → 문서와 코드가 항상 동기화됨!
*/

fn lesson5_doc_tests() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 5: 문서 테스트");
    println!("═══════════════════════════════════════════");

    println!("  문서 주석 안의 코드 블록이 자동 테스트됩니다!");
    println!();
    println!("  /// # Examples");
    println!("  /// ```");
    println!("  /// assert_eq!(add(2, 3), 5);");
    println!("  /// ```");
    println!();
    println!("  ★ 장점: 문서 예제가 항상 최신 상태!");
    println!("  ★ cargo doc --open 으로 문서 생성/확인");
    println!();
}

// =====================================================================
// 레슨 6 — 테스트 설계 원칙
// =====================================================================
/*
★ 좋은 테스트의 원칙

  ┌────────────────────────────────────────────────────────────┐
  │ 1. AAA 패턴: Arrange → Act → Assert                      │
  │    → 준비 → 실행 → 검증                                  │
  │                                                            │
  │ 2. 하나의 테스트 = 하나의 동작 검증                       │
  │                                                            │
  │ 3. 경계값 테스트 (0, 1, MAX, 빈 값, None)                │
  │                                                            │
  │ 4. 실패하는 경우도 테스트 (에러 경로)                     │
  │                                                            │
  │ 5. 테스트 이름은 "무엇을_어떤상황에서_어떻게" 형식       │
  │    예: test_discount_zero_percent_returns_original        │
  └────────────────────────────────────────────────────────────┘
*/

fn lesson6_test_principles() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 6: 테스트 설계 원칙");
    println!("═══════════════════════════════════════════");

    println!("  AAA 패턴 예시:");
    println!("    // Arrange (준비)");
    println!("    let student = Student::new(\"철수\", 85);");
    println!();
    println!("    // Act (실행)");
    println!("    let result = student.grade();");
    println!();
    println!("    // Assert (검증)");
    println!("    assert_eq!(result, \"B\");");
    println!();

    // 실제 검증
    let student = Student::new("철수", 85);
    assert_eq!(student.grade(), "B");
    assert!(student.is_passing());
    println!("  ★ 수동 검증 통과!");
    println!();
}

// =====================================================================
// 레슨 7 — 테스트 체크리스트
// =====================================================================

fn lesson7_checklist() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 7: 테스트 체크리스트");
    println!("═══════════════════════════════════════════");

    println!("  ┌──────────────────────────────────────────────┐");
    println!("  │ 테스트 작성 체크리스트                       │");
    println!("  ├──────────────────────────────────────────────┤");
    println!("  │ [ ] 정상 경로 (happy path) 테스트            │");
    println!("  │ [ ] 에러 경로 (error path) 테스트            │");
    println!("  │ [ ] 경계값 (0, 빈 값, MAX) 테스트            │");
    println!("  │ [ ] panic 이 예상되면 #[should_panic]       │");
    println!("  │ [ ] 테스트 이름이 동작을 설명하는가?        │");
    println!("  │ [ ] 각 테스트가 독립적인가?                  │");
    println!("  │ [ ] cargo test 가 모두 통과하는가?           │");
    println!("  │ [ ] cargo clippy 경고가 없는가?              │");
    println!("  └──────────────────────────────────────────────┘");
    println!();
}

// =====================================================================
//  main
// =====================================================================

fn main() {
    println!();
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  Rust 16단계: 테스트 (Testing)");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!();

    lesson1_unit_test_basics();
    lesson2_test_patterns();
    lesson3_test_options();
    lesson4_integration_tests();
    lesson5_doc_tests();
    lesson6_test_principles();
    lesson7_checklist();

    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  16단계 완료! 다음은 17_build_deploy 입니다");
    println!("  ★ cargo test 로 아래 테스트를 실행해보세요!");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
}

// =====================================================================
// 실제 테스트 모듈
// =====================================================================
#[cfg(test)]
mod tests {
    use super::*;

    // ── 기본 할인 테스트 ──
    #[test]
    fn test_discount_10_percent() {
        assert_eq!(apply_discount(10_000, 10), 9_000);
    }

    #[test]
    fn test_discount_zero_percent_returns_original() {
        assert_eq!(apply_discount(5_000, 0), 5_000);
    }

    #[test]
    fn test_discount_100_percent_returns_zero() {
        assert_eq!(apply_discount(8_000, 100), 0);
    }

    #[test]
    fn test_discount_25_percent() {
        assert_eq!(apply_discount(8_000, 25), 6_000);
    }

    // ── panic 테스트 ──
    #[test]
    #[should_panic(expected = "0~100")]
    fn test_discount_negative_panics() {
        apply_discount(1_000, -10);
    }

    #[test]
    #[should_panic(expected = "0~100")]
    fn test_discount_over_100_panics() {
        apply_discount(1_000, 150);
    }

    // ── 평균 테스트 ──
    #[test]
    fn test_average_normal() {
        let result = safe_average(&[80.0, 90.0, 100.0]);
        assert_eq!(result, Some(90.0));
    }

    #[test]
    fn test_average_empty_returns_none() {
        assert_eq!(safe_average(&[]), None);
    }

    #[test]
    fn test_average_single() {
        assert_eq!(safe_average(&[42.0]), Some(42.0));
    }

    // ── 파싱 테스트 (Result 반환) ──
    #[test]
    fn test_parse_valid() -> Result<(), String> {
        let score = parse_score("85")?;
        assert_eq!(score, 85);
        Ok(())
    }

    #[test]
    fn test_parse_invalid() {
        assert!(parse_score("abc").is_err());
    }

    #[test]
    fn test_parse_with_whitespace() -> Result<(), String> {
        let score = parse_score("  42  ")?;
        assert_eq!(score, 42);
        Ok(())
    }

    // ── 등급 테스트 ──
    #[test]
    fn test_grade_boundaries() {
        assert_eq!(grade(100), "A");
        assert_eq!(grade(90), "A");
        assert_eq!(grade(89), "B");
        assert_eq!(grade(80), "B");
        assert_eq!(grade(79), "C");
        assert_eq!(grade(70), "C");
        assert_eq!(grade(69), "D");
        assert_eq!(grade(60), "D");
        assert_eq!(grade(59), "F");
        assert_eq!(grade(0), "F");
    }

    // ── Student 테스트 ──
    #[test]
    fn test_student_passing() {
        let student = Student::new("철수", 85);
        assert!(student.is_passing());
        assert_eq!(student.grade(), "B");
    }

    #[test]
    fn test_student_failing() {
        let student = Student::new("영희", 55);
        assert!(!student.is_passing());
        assert_eq!(student.grade(), "F");
    }

    #[test]
    fn test_student_equality() {
        let s1 = Student::new("철수", 90);
        let s2 = Student::new("철수", 90);
        assert_eq!(s1, s2);  // PartialEq derive 덕분
    }
}
