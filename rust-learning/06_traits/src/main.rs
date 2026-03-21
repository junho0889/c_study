/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Rust 학습 06단계: 트레이트 (Traits)
  ─ trait 정의, impl for, 기본 구현, trait bounds, dyn Trait ─

  [학습 목표]
  1. trait 로 "행동 규약(인터페이스)"을 정의한다
  2. 서로 다른 타입에 같은 trait 를 구현한다
  3. 기본 구현(default implementation)을 이해한다
  4. trait bound 로 제네릭에 제약을 건다
  5. dyn Trait 로 런타임 다형성을 사용한다
  6. 표준 라이브러리 trait (Display, From 등)을 활용한다

  ■ 실행: cargo run
  ■ 빌드: cargo build --release

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

use std::fmt;

// =====================================================================
// 레슨 1 — trait 기본: "할 수 있는 일"의 약속
// =====================================================================
/*
★ trait 는 "이 타입은 이런 일을 할 수 있다" 는 약속입니다

  비유: 자격증
  ┌─────────────────────────────────────────────────┐
  │ "요약 자격증" (Summary trait)                    │
  │  → 이 자격증이 있는 사람은 누구든 자기소개를     │
  │    한 줄로 요약할 수 있다!                       │
  │  → 의사든, 선생님이든, 학생이든 상관없이         │
  │    summarize() 를 호출하면 요약이 나온다          │
  └─────────────────────────────────────────────────┘

★ Java/C# 의 interface, C++ 의 순수 가상 함수와 비슷
  → 하지만 기본 구현도 줄 수 있어서 더 유연합니다!
*/

trait Summary {
    // ── 필수 메서드: 구현하는 쪽에서 반드시 작성 ──
    fn summarize(&self) -> String;

    // ── 기본 구현: 덮어쓰지 않으면 이 코드가 사용됨 ──
    fn preview(&self) -> String {
        format!("(미리보기) {}", self.summarize())
    }
}

struct NewsArticle {
    title: String,
    author: String,
    content: String,
}

struct Tweet {
    username: String,
    message: String,
}

// ── 서로 다른 타입에 같은 trait 구현 ──
impl Summary for NewsArticle {
    fn summarize(&self) -> String {
        format!("[뉴스] {} - by {}", self.title, self.author)
    }
    // preview() 는 기본 구현 그대로 사용
}

impl Summary for Tweet {
    fn summarize(&self) -> String {
        format!("@{}: {}", self.username, self.message)
    }

    // preview() 를 덮어써서 커스터마이징
    fn preview(&self) -> String {
        format!("트윗 미리보기 → {}", self.message)
    }
}

fn lesson1_trait_basics() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 1: trait 기본");
    println!("═══════════════════════════════════════════");

    let article = NewsArticle {
        title: String::from("Rust 2025 에디션 발표"),
        author: String::from("김개발"),
        content: String::from("올해 Rust 에디션이..."),
    };
    let tweet = Tweet {
        username: String::from("rustlover"),
        message: String::from("Rust 최고!"),
    };

    println!("  {}", article.summarize());
    println!("  {}", article.preview());    // 기본 구현 사용
    println!("  {}", tweet.summarize());
    println!("  {}", tweet.preview());      // 커스텀 구현 사용
    println!();
}

// =====================================================================
// 레슨 2 — trait bound: "이 능력이 있는 타입만 받겠다"
// =====================================================================
/*
★ 제네릭 함수에서 "아무 타입이나 다 되는 건 아니야"

  ┌─────────────────────────────────────────────────────────┐
  │  방법 1: impl Trait (간단한 경우)                        │
  │    fn notify(item: &impl Summary) { ... }               │
  │                                                          │
  │  방법 2: trait bound (여러 제약, 복잡한 경우)            │
  │    fn notify<T: Summary>(item: &T) { ... }              │
  │                                                          │
  │  방법 3: where 절 (가독성이 좋음)                        │
  │    fn notify<T>(item: &T) where T: Summary { ... }      │
  └─────────────────────────────────────────────────────────┘

★ 여러 trait 제약: + 로 연결
  fn process(item: &(impl Summary + fmt::Display)) { ... }
*/

// ── impl Trait 방식 ──
fn print_summary(item: &impl Summary) {
    println!("    요약: {}", item.summarize());
}

// ── trait bound 방식 (같은 의미, 더 명시적) ──
fn print_two_summaries<T: Summary>(a: &T, b: &T) {
    println!("    A: {}", a.summarize());
    println!("    B: {}", b.summarize());
}

// ── 반환 타입에 impl Trait ──
fn create_default_tweet() -> impl Summary {
    Tweet {
        username: String::from("bot"),
        message: String::from("자동 생성 메시지"),
    }
}

fn lesson2_trait_bounds() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 2: trait bound");
    println!("═══════════════════════════════════════════");

    let t1 = Tweet {
        username: String::from("user1"),
        message: String::from("안녕하세요"),
    };
    let t2 = Tweet {
        username: String::from("user2"),
        message: String::from("반갑습니다"),
    };

    print_summary(&t1);
    print_two_summaries(&t1, &t2);

    let bot = create_default_tweet();
    println!("    봇: {}", bot.summarize());
    println!();
}

// =====================================================================
// 레슨 3 — dyn Trait: 런타임 다형성 (동적 디스패치)
// =====================================================================
/*
★ impl Trait vs dyn Trait

  ┌──────────────┬──────────────────────────────────────────┐
  │ impl Trait   │ 컴파일 타임에 타입 결정 (정적 디스패치)  │
  │              │ → 빠름, 하지만 한 가지 타입만 반환 가능  │
  ├──────────────┼──────────────────────────────────────────┤
  │ dyn Trait    │ 런타임에 타입 결정 (동적 디스패치)       │
  │              │ → 약간 느림, 하지만 여러 타입 섞기 가능  │
  │              │ → Box<dyn Trait> 또는 &dyn Trait 로 사용 │
  └──────────────┴──────────────────────────────────────────┘

  비유: 우체통
  ┌────────────────────────────────────────────────────┐
  │ impl Trait = 전용 우체통 (편지만 넣을 수 있음)     │
  │ dyn Trait  = 범용 우체통 (편지든 소포든 상관없음)  │
  └────────────────────────────────────────────────────┘

★ 소유권 주의:
  Box<dyn Trait> → trait 객체의 소유권을 Box 가 가짐
  &dyn Trait     → 빌림 (라이프타임 필요)
*/

fn make_feed() -> Vec<Box<dyn Summary>> {
    vec![
        Box::new(NewsArticle {
            title: String::from("AI 기술 발전"),
            author: String::from("이기자"),
            content: String::from("..."),
        }),
        Box::new(Tweet {
            username: String::from("dev_kim"),
            message: String::from("오늘도 코딩!"),
        }),
    ]
}

fn lesson3_dyn_trait() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 3: dyn Trait (동적 디스패치)");
    println!("═══════════════════════════════════════════");

    let feed = make_feed();
    for item in &feed {
        println!("  {}", item.summarize());
    }

    // ★ Vec<Box<dyn Summary>> 는
    //    "Summary 를 구현한 아무 타입이나 담을 수 있는 상자 목록"
    println!("  피드 아이템 수: {}", feed.len());
    println!();
}

// =====================================================================
// 레슨 4 — 표준 라이브러리 trait 구현하기
// =====================================================================
/*
★ Rust 에서 자주 구현하는 표준 trait 들

  ┌─────────────┬──────────────────────────────────────────┐
  │ Display     │ {} 으로 사용자 친화적 출력                │
  │ Debug       │ {:?} 으로 디버그 출력 (#[derive] 가능)   │
  │ From/Into   │ 타입 변환                                │
  │ PartialEq   │ == 비교                                  │
  │ Clone/Copy  │ 복사                                     │
  │ Default     │ 기본값 생성                              │
  │ Iterator    │ for 루프 사용 가능                       │
  └─────────────┴──────────────────────────────────────────┘
*/

#[derive(Debug, Clone)]
struct Temperature {
    celsius: f64,
}

// ── Display trait 구현: println!("{}", temp) 가능하게 ──
impl fmt::Display for Temperature {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:.1}°C", self.celsius)
    }
}

// ── From trait 구현: 화씨 → 섭씨 변환 ──
impl From<f64> for Temperature {
    fn from(fahrenheit: f64) -> Self {
        Temperature {
            celsius: (fahrenheit - 32.0) * 5.0 / 9.0,
        }
    }
}

impl Default for Temperature {
    fn default() -> Self {
        Temperature { celsius: 0.0 }
    }
}

impl PartialEq for Temperature {
    fn eq(&self, other: &Self) -> bool {
        (self.celsius - other.celsius).abs() < 0.01
    }
}

fn lesson4_std_traits() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 4: 표준 라이브러리 trait");
    println!("═══════════════════════════════════════════");

    let temp = Temperature { celsius: 36.5 };
    println!("  Display: {}", temp);          // Display trait
    println!("  Debug:   {:?}", temp);        // Debug trait

    // From trait → 화씨 100도를 섭씨로
    let boiling = Temperature::from(212.0);
    println!("  화씨 212 → {}", boiling);

    // Into trait (From 을 구현하면 Into 는 자동!)
    let body: Temperature = 98.6_f64.into();
    println!("  화씨 98.6 → {}", body);

    // Default
    let zero = Temperature::default();
    println!("  기본값: {}", zero);

    // PartialEq
    let t1 = Temperature { celsius: 36.5 };
    let t2 = Temperature { celsius: 36.5 };
    println!("  t1 == t2 ? {}", t1 == t2);
    println!();
}

// =====================================================================
// 레슨 5 — 여러 trait 동시 구현과 trait 상속
// =====================================================================
/*
★ trait 도 다른 trait 를 요구할 수 있습니다 (supertrait)

  trait Printable: fmt::Display + fmt::Debug { ... }
  → Printable 을 구현하려면 Display 와 Debug 도 있어야 함

★ 하나의 타입에 여러 trait 를 구현하는 것은 자유!
  → Rust 의 "합성(composition)" 방식
  → 상속 대신 trait 조합으로 기능을 붙여나감
*/

trait Describable: fmt::Display {
    fn describe(&self) -> String {
        format!("설명: {}", self)   // Display 가 있으니 {} 사용 가능
    }
}

// Temperature 에 Describable 추가 (Display 가 이미 있으므로 OK)
impl Describable for Temperature {}

trait Loggable {
    fn log(&self, prefix: &str);
}

impl Loggable for Temperature {
    fn log(&self, prefix: &str) {
        println!("    [LOG] {} → {}", prefix, self);
    }
}

fn lesson5_multiple_traits() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 5: 여러 trait 조합");
    println!("═══════════════════════════════════════════");

    let temp = Temperature { celsius: 22.0 };

    // Summary 가 아닌 다른 trait 들을 자유롭게 조합
    println!("  {}", temp.describe());      // Describable
    temp.log("실내 온도");                   // Loggable
    println!("  출력: {}", temp);            // Display

    // 함수에서 여러 trait 동시 요구
    fn log_and_display(item: &(impl fmt::Display + Loggable)) {
        println!("    화면: {}", item);
        item.log("함수 내부");
    }
    log_and_display(&temp);
    println!();
}

// =====================================================================
// 레슨 6 — 실전 패턴: 전략 패턴과 trait 객체
// =====================================================================
/*
★ trait 을 이용한 전략 패턴 (Strategy Pattern)
  → 같은 인터페이스, 다른 구현을 런타임에 선택

  비유: 내비게이션 앱
  ┌──────────────────────────────────────────┐
  │ trait Router {                           │
  │     fn route(&self) -> String;           │
  │ }                                        │
  │                                          │
  │ struct FastRoute;   // 최단 시간         │
  │ struct ShortRoute;  // 최단 거리         │
  │ struct SafeRoute;   // 안전 경로         │
  │                                          │
  │ → 사용자가 선택한 전략으로 경로 계산!    │
  └──────────────────────────────────────────┘
*/

trait Sorter {
    fn name(&self) -> &str;
    fn sort(&self, data: &mut Vec<i32>);
}

struct BubbleSort;
struct QuickishSort;   // 간단한 예시용

impl Sorter for BubbleSort {
    fn name(&self) -> &str { "버블 정렬" }
    fn sort(&self, data: &mut Vec<i32>) {
        let len = data.len();
        for i in 0..len {
            for j in 0..len - 1 - i {
                if data[j] > data[j + 1] {
                    data.swap(j, j + 1);
                }
            }
        }
    }
}

impl Sorter for QuickishSort {
    fn name(&self) -> &str { "빠른 정렬 (표준 라이브러리)" }
    fn sort(&self, data: &mut Vec<i32>) {
        data.sort();  // 표준 라이브러리의 정렬 사용
    }
}

fn sort_and_print(sorter: &dyn Sorter, data: &mut Vec<i32>) {
    println!("    [{}] 정렬 전: {:?}", sorter.name(), data);
    sorter.sort(data);
    println!("    [{}] 정렬 후: {:?}", sorter.name(), data);
}

fn lesson6_strategy_pattern() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 6: 전략 패턴 (dyn Trait 활용)");
    println!("═══════════════════════════════════════════");

    let mut data1 = vec![5, 3, 8, 1, 9];
    let mut data2 = vec![5, 3, 8, 1, 9];

    sort_and_print(&BubbleSort, &mut data1);
    sort_and_print(&QuickishSort, &mut data2);

    // ★ 런타임에 전략 선택
    let user_choice = "fast";
    let sorter: Box<dyn Sorter> = match user_choice {
        "bubble" => Box::new(BubbleSort),
        _        => Box::new(QuickishSort),
    };
    let mut data3 = vec![42, 7, 15, 3];
    sort_and_print(sorter.as_ref(), &mut data3);
    println!();
}

// =====================================================================
// 레슨 7 — 흔한 실수와 주의사항
// =====================================================================
/*
★ trait 관련 흔한 실수 모음

  ┌────────────────────────────────────────────────────────────┐
  │ 실수 1: trait 메서드에서 Self 크기를 모를 때               │
  │   → dyn Trait 사용 시 Sized 가 아닐 수 있음               │
  │   → trait 에 where Self: Sized 가드 필요한 경우           │
  │                                                            │
  │ 실수 2: 다른 크레이트의 타입에 다른 크레이트의 trait 구현  │
  │   → 고아 규칙(Orphan Rule): 둘 중 하나는 내 크레이트여야! │
  │                                                            │
  │ 실수 3: dyn Trait 을 직접 값으로 사용                      │
  │   → 크기를 모르므로 Box 나 & 로 감싸야 함                 │
  └────────────────────────────────────────────────────────────┘
*/

fn lesson7_common_mistakes() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 7: 흔한 실수와 주의사항");
    println!("═══════════════════════════════════════════");

    // 고아 규칙 설명
    println!("  ★ 고아 규칙 (Orphan Rule):");
    println!("    → 외부 크레이트의 타입 + 외부 trait = 구현 불가!");
    println!("    → impl Display for Vec<i32> {} ← 컴파일 에러!");
    println!("    → 해결: 뉴타입 패턴으로 감싸기");
    println!();

    // 뉴타입 패턴으로 고아 규칙 우회
    struct Wrapper(Vec<i32>);
    impl fmt::Display for Wrapper {
        fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
            write!(f, "[{}]", self.0.iter()
                .map(|n| n.to_string())
                .collect::<Vec<_>>()
                .join(", "))
        }
    }

    let w = Wrapper(vec![1, 2, 3]);
    println!("  뉴타입 패턴: {}", w);

    // dyn Trait 크기 문제
    println!();
    println!("  ★ dyn Trait 크기 규칙:");
    println!("    → let x: dyn Summary;   ← 컴파일 에러! 크기 모름");
    println!("    → let x: Box<dyn Summary>;  ← OK! Box 가 힙에 저장");
    println!("    → let x: &dyn Summary;      ← OK! 참조는 크기 고정");
    println!();
}

// =====================================================================
//  main
// =====================================================================

fn main() {
    println!();
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  Rust 06단계: 트레이트 (Traits)");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!();

    lesson1_trait_basics();
    lesson2_trait_bounds();
    lesson3_dyn_trait();
    lesson4_std_traits();
    lesson5_multiple_traits();
    lesson6_strategy_pattern();
    lesson7_common_mistakes();

    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  06단계 완료! 다음은 07_collections 입니다");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
}
