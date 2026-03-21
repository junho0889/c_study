/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Rust 학습 08단계: 에러 처리 (Error Handling)
  ─ Result, Option, ?, unwrap, expect, 커스텀 에러 ─

  [학습 목표]
  1. panic! 과 Result 의 차이를 이해한다
  2. Result<T, E> 로 실패를 명시적으로 처리한다
  3. ? 연산자로 에러를 간결하게 전파한다
  4. 커스텀 에러 타입을 만든다
  5. Option 과 Result 를 변환한다
  6. unwrap/expect 를 언제 쓰면 안 되는지 안다

  ■ 실행: cargo run
  ■ 빌드: cargo build --release

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

use std::fmt;
use std::num::ParseIntError;

// =====================================================================
// 레슨 1 — panic! vs Result: 복구 불가능 vs 복구 가능
// =====================================================================
/*
★ Rust 에러 처리의 두 가지 길

  ┌──────────────────────────────────────────────────────┐
  │ panic!                                               │
  │ → 프로그램이 바로 멈춤 (스택 되감기)                 │
  │ → "이건 절대 일어나면 안 되는 상황" 에 사용          │
  │ → 예: 배열 범위 밖 접근, 절대 실패하면 안 되는 초기화│
  ├──────────────────────────────────────────────────────┤
  │ Result<T, E>                                         │
  │ → 성공(Ok) 또는 실패(Err) 를 호출자에게 돌려줌       │
  │ → "실패할 수도 있는 일" 에 사용                      │
  │ → 예: 파일 읽기, 네트워크 요청, 문자열 파싱          │
  └──────────────────────────────────────────────────────┘

  비유:
  ┌────────────────────────────────────────────────────────┐
  │ panic! = 화재 경보 → 건물 전체 대피 (프로그램 종료)    │
  │ Result = 우편물 반송 → "주소 틀림" 이라고 알려줌       │
  │                       → 다시 보내거나 다른 처리 가능   │
  └────────────────────────────────────────────────────────┘
*/

fn lesson1_panic_vs_result() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 1: panic! vs Result");
    println!("═══════════════════════════════════════════");

    // panic! 은 프로그램을 바로 멈춥니다
    // panic!("이건 실행하면 안 돼요!");  // ← 주석 해제하면 여기서 멈춤

    // Result 는 성공/실패를 돌려줍니다
    let result: Result<i32, String> = Ok(42);
    let error: Result<i32, String> = Err(String::from("뭔가 잘못됨"));

    println!("  성공: {:?}", result);
    println!("  실패: {:?}", error);

    // ★ 중요: 일반적인 코드에서는 Result 를 사용하세요!
    //   panic! 은 정말 복구 불가능한 버그에만!
    println!();
}

// =====================================================================
// 레슨 2 — Result<T, E> 다루기: match, if let, 메서드
// =====================================================================
/*
★ Result 를 처리하는 다양한 방법

  ┌───────────────────┬────────────────────────────────────┐
  │ match             │ 가장 명시적 (모든 경우 처리)       │
  │ if let Ok(v)      │ 성공만 관심 있을 때                │
  │ unwrap()          │ 실패 시 panic! (위험!)             │
  │ expect("메시지")  │ 실패 시 메시지와 함께 panic!       │
  │ unwrap_or(기본값) │ 실패 시 기본값 사용                │
  │ unwrap_or_else    │ 실패 시 클로저로 값 생성           │
  │ map()             │ 성공 값 변환                       │
  │ map_err()         │ 에러 값 변환                       │
  │ and_then()        │ 성공이면 다른 Result 반환 함수 연결│
  └───────────────────┴────────────────────────────────────┘
*/

fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        Err(String::from("0으로 나눌 수 없습니다"))
    } else {
        Ok(a / b)
    }
}

fn lesson2_result_handling() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 2: Result 다루기");
    println!("═══════════════════════════════════════════");

    // ── match: 가장 명시적 ──
    match divide(10.0, 3.0) {
        Ok(val) => println!("  10 / 3 = {:.2}", val),
        Err(e)  => println!("  에러: {}", e),
    }

    match divide(10.0, 0.0) {
        Ok(val) => println!("  10 / 0 = {:.2}", val),
        Err(e)  => println!("  에러: {}", e),
    }

    // ── unwrap_or: 실패하면 기본값 ──
    let safe = divide(10.0, 0.0).unwrap_or(0.0);
    println!("  unwrap_or(0.0): {}", safe);

    // ── map: 성공 값 변환 ──
    let doubled = divide(10.0, 4.0).map(|v| v * 2.0);
    println!("  map(x2): {:?}", doubled);

    // ── and_then: 체이닝 ──
    let result = divide(100.0, 5.0)
        .and_then(|v| divide(v, 2.0));   // 100/5 = 20, 그 다음 20/2 = 10
    println!("  100 / 5 / 2 = {:?}", result);

    // ★ unwrap() 은 위험합니다!
    // divide(10.0, 0.0).unwrap();  // ← panic!
    println!("  ★ unwrap() 은 실패 가능성이 없을 때만 사용하세요!");
    println!();
}

// =====================================================================
// 레슨 3 — ? 연산자: 에러를 간결하게 위로 전파
// =====================================================================
/*
★ ? 연산자 = "에러면 바로 돌려보내, 성공이면 값을 꺼내"

  ┌─────────────────────────────────────────────────────────┐
  │ fn process() -> Result<i32, String> {                   │
  │     let a = might_fail()?;  // 에러면 즉시 Err 반환    │
  │     let b = might_fail()?;  // 성공이면 값 꺼냄        │
  │     Ok(a + b)                                           │
  │ }                                                       │
  └─────────────────────────────────────────────────────────┘

  ? 없이 쓰면 이렇게 길어집니다:
  ┌─────────────────────────────────────────────────────────┐
  │ let a = match might_fail() {                            │
  │     Ok(v)  => v,                                        │
  │     Err(e) => return Err(e),  // 직접 반환              │
  │ };                                                      │
  └─────────────────────────────────────────────────────────┘

★ ? 는 Result 를 반환하는 함수 안에서만 사용 가능!
  → main() 에서 쓰려면 main() 도 Result 를 반환해야 함
*/

fn parse_and_add(a: &str, b: &str) -> Result<i32, ParseIntError> {
    let x: i32 = a.parse()?;    // 실패하면 ParseIntError 바로 반환
    let y: i32 = b.parse()?;
    Ok(x + y)
}

fn calculate_average(numbers: &str) -> Result<f64, String> {
    let parts: Vec<&str> = numbers.split(',').collect();
    if parts.is_empty() {
        return Err(String::from("빈 입력"));
    }

    let mut total = 0.0;
    for part in &parts {
        let n: f64 = part.trim().parse()
            .map_err(|e: std::num::ParseFloatError| {
                format!("'{}' 파싱 실패: {}", part, e)
            })?;   // map_err 로 에러 타입 변환 후 ? 사용
        total += n;
    }
    Ok(total / parts.len() as f64)
}

fn lesson3_question_mark() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 3: ? 연산자");
    println!("═══════════════════════════════════════════");

    // 성공 사례
    match parse_and_add("10", "20") {
        Ok(sum) => println!("  10 + 20 = {}", sum),
        Err(e)  => println!("  에러: {}", e),
    }

    // 실패 사례
    match parse_and_add("10", "abc") {
        Ok(sum) => println!("  10 + abc = {}", sum),
        Err(e)  => println!("  에러: {}", e),
    }

    // 평균 계산
    match calculate_average("10, 20, 30") {
        Ok(avg) => println!("  평균: {:.1}", avg),
        Err(e)  => println!("  에러: {}", e),
    }
    match calculate_average("10, abc, 30") {
        Ok(avg) => println!("  평균: {:.1}", avg),
        Err(e)  => println!("  에러: {}", e),
    }
    println!();
}

// =====================================================================
// 레슨 4 — 커스텀 에러 타입 만들기
// =====================================================================
/*
★ 실무에서는 자기만의 에러 타입을 만듭니다

  이유:
  ┌────────────────────────────────────────────────────────┐
  │ 1. 여러 종류의 에러를 하나의 타입으로 통합             │
  │ 2. 에러에 추가 정보(필드)를 담을 수 있음               │
  │ 3. 호출자가 에러 종류별로 다르게 처리 가능             │
  └────────────────────────────────────────────────────────┘

  방법:
  ┌────────────────────────────────────────────────────────┐
  │ 방법 1: enum 으로 직접 만들기                          │
  │ 방법 2: thiserror 크레이트 (라이브러리용)             │
  │ 방법 3: anyhow 크레이트 (애플리케이션용)              │
  └────────────────────────────────────────────────────────┘
*/

// ── 커스텀 에러 enum ──
#[derive(Debug)]
enum AppError {
    NotFound(String),
    ParseError(String),
    DivisionByZero,
    InvalidInput { field: String, reason: String },
}

// Display 구현 → {} 로 출력 가능
impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AppError::NotFound(name) =>
                write!(f, "'{}' 을(를) 찾을 수 없습니다", name),
            AppError::ParseError(msg) =>
                write!(f, "파싱 에러: {}", msg),
            AppError::DivisionByZero =>
                write!(f, "0으로 나눌 수 없습니다"),
            AppError::InvalidInput { field, reason } =>
                write!(f, "'{}' 필드 오류: {}", field, reason),
        }
    }
}

// std::error::Error 구현 → 에러 체인에 참여 가능
impl std::error::Error for AppError {}

// From 구현 → ? 연산자에서 자동 변환
impl From<ParseIntError> for AppError {
    fn from(e: ParseIntError) -> Self {
        AppError::ParseError(e.to_string())
    }
}

fn find_score(name: &str) -> Result<i32, AppError> {
    match name {
        "철수" => Ok(92),
        "영희" => Ok(88),
        _      => Err(AppError::NotFound(name.to_string())),
    }
}

fn safe_divide(a: i32, b: i32) -> Result<i32, AppError> {
    if b == 0 {
        Err(AppError::DivisionByZero)
    } else {
        Ok(a / b)
    }
}

fn process_input(input: &str) -> Result<i32, AppError> {
    if input.is_empty() {
        return Err(AppError::InvalidInput {
            field: String::from("input"),
            reason: String::from("빈 값이 입력되었습니다"),
        });
    }
    let num: i32 = input.parse()?;   // ParseIntError → AppError 자동 변환
    Ok(num * 2)
}

fn lesson4_custom_error() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 4: 커스텀 에러 타입");
    println!("═══════════════════════════════════════════");

    // 다양한 에러 케이스
    let cases: Vec<(&str, Result<i32, AppError>)> = vec![
        ("철수 점수", find_score("철수")),
        ("모르는 학생", find_score("모르는학생")),
        ("10 / 0", safe_divide(10, 0)),
        ("빈 입력", process_input("")),
        ("abc 파싱", process_input("abc")),
        ("42 파싱", process_input("42")),
    ];

    for (desc, result) in cases {
        match result {
            Ok(v)  => println!("  {} → 성공: {}", desc, v),
            Err(e) => println!("  {} → 실패: {}", desc, e),
        }
    }
    println!();
}

// =====================================================================
// 레슨 5 — Option 과 Result 변환
// =====================================================================
/*
★ Option 과 Result 는 서로 변환할 수 있습니다

  ┌─────────────────────────────────────────────────────────┐
  │ Option → Result                                         │
  │   some_value.ok_or("에러 메시지")                       │
  │   some_value.ok_or_else(|| make_error())                │
  │                                                          │
  │ Result → Option                                         │
  │   result.ok()   → 성공이면 Some, 실패면 None            │
  │   result.err()  → 실패면 Some, 성공이면 None            │
  └─────────────────────────────────────────────────────────┘
*/

fn find_first_even(numbers: &[i32]) -> Option<i32> {
    numbers.iter().find(|&&n| n % 2 == 0).copied()
}

fn lesson5_option_result_conversion() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 5: Option ↔ Result 변환");
    println!("═══════════════════════════════════════════");

    // Option → Result
    let nums = [1, 3, 5, 7];
    let result = find_first_even(&nums)
        .ok_or("짝수가 없습니다");
    println!("  [1,3,5,7] 에서 짝수 찾기: {:?}", result);

    let nums2 = [1, 4, 5, 7];
    let result2 = find_first_even(&nums2)
        .ok_or("짝수가 없습니다");
    println!("  [1,4,5,7] 에서 짝수 찾기: {:?}", result2);

    // Result → Option
    let ok_result: Result<i32, &str> = Ok(42);
    let err_result: Result<i32, &str> = Err("에러");

    println!("  Ok(42).ok() = {:?}", ok_result.ok());
    println!("  Err.ok()    = {:?}", err_result.ok());
    println!("  Err.err()   = {:?}", err_result.err());
    println!();
}

// =====================================================================
// 레슨 6 — 에러 처리 모범 사례
// =====================================================================
/*
★ 에러 처리 가이드라인

  ┌────────────────────────────────────────────────────────────┐
  │ 상황                          │ 추천 방법                  │
  ├────────────────────────────────────────────────────────────┤
  │ 프로토타입 / 예제             │ unwrap() / expect() OK     │
  │ 라이브러리 코드               │ Result + 커스텀 에러       │
  │ 애플리케이션 코드             │ Result + anyhow           │
  │ 절대 실패하면 안 되는 곳      │ panic! / assert!          │
  │ 테스트 코드                   │ unwrap() 자유롭게         │
  └────────────────────────────────────────────────────────────┘

★ 절대 하지 말 것:
  ┌────────────────────────────────────────────────────────────┐
  │ ✗ 프로덕션 코드에서 unwrap() 남발                        │
  │ ✗ 에러를 무시하고 삼켜버리기                              │
  │ ✗ 모든 에러를 String 으로 통일 (정보 손실)               │
  │ ✗ panic! 으로 일반적인 에러 상황 처리                    │
  └────────────────────────────────────────────────────────────┘
*/

fn lesson6_best_practices() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 6: 에러 처리 모범 사례");
    println!("═══════════════════════════════════════════");

    // ── expect() 에는 이유를 적으세요 ──
    let config = "8080";
    let port: u16 = config.parse()
        .expect("설정 파일의 포트 번호가 유효한 숫자여야 합니다");
    println!("  포트: {}", port);

    // ── 에러를 체이닝할 때는 map_err ──
    let result: Result<i32, String> = "42".parse::<i32>()
        .map_err(|e| format!("설정 파싱 실패: {}", e));
    println!("  map_err 결과: {:?}", result);

    // ── 여러 에러를 묶어서 처리 ──
    fn load_config() -> Result<(String, u16), AppError> {
        let name = "my_app".to_string();
        let port_str = "3000";
        let port: u16 = port_str.parse()
            .map_err(|_| AppError::ParseError(
                format!("포트 '{}' 파싱 실패", port_str)
            ))?;
        Ok((name, port))
    }

    match load_config() {
        Ok((name, port)) => println!("  설정: {} on port {}", name, port),
        Err(e) => println!("  설정 로드 실패: {}", e),
    }

    println!();
    println!("  ★ thiserror 크레이트: 라이브러리용 에러 정의에 최적");
    println!("    → #[derive(thiserror::Error)] 로 보일러플레이트 제거");
    println!("  ★ anyhow 크레이트: 애플리케이션 코드에 최적");
    println!("    → anyhow::Result<T> 로 어떤 에러든 담기 가능");
    println!();
}

// =====================================================================
//  main
// =====================================================================

fn main() {
    println!();
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  Rust 08단계: 에러 처리");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!();

    lesson1_panic_vs_result();
    lesson2_result_handling();
    lesson3_question_mark();
    lesson4_custom_error();
    lesson5_option_result_conversion();
    lesson6_best_practices();

    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  08단계 완료! 다음은 09_closures_iterators");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
}
