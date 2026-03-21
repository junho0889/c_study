/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Rust 학습 13단계: 제네릭과 라이프타임
  ─ 제네릭 함수/구조체, trait bound, 라이프타임 'a, 엘리전 규칙 ─

  [학습 목표]
  1. 제네릭으로 타입에 독립적인 코드를 작성한다
  2. trait bound 로 제네릭에 제약을 건다
  3. 라이프타임의 개념과 필요성을 이해한다
  4. 라이프타임 표기법 'a 를 읽고 쓸 수 있다
  5. 라이프타임 엘리전 규칙을 안다
  6. 'static 라이프타임을 이해한다

  ■ 실행: cargo run
  ■ 빌드: cargo build --release

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

use std::fmt;

// =====================================================================
// 레슨 1 — 제네릭 함수: 타입을 매개변수로
// =====================================================================
/*
★ 제네릭 = "틀은 하나, 타입은 나중에"

  비유: 쿠키 틀
  ┌────────────────────────────────────────────────────┐
  │ 같은 쿠키 틀로 초코 쿠키, 딸기 쿠키, 치즈 쿠키를 │
  │ 만들 수 있듯이                                    │
  │ 같은 제네릭 함수로 i32, f64, String 을 처리!      │
  └────────────────────────────────────────────────────┘

  없으면 이렇게 해야 합니다:
  ┌────────────────────────────────────────────────────┐
  │ fn largest_i32(a: i32, b: i32) -> i32 { ... }     │
  │ fn largest_f64(a: f64, b: f64) -> f64 { ... }     │
  │ fn largest_str(a: &str, b: &str) -> &str { ... }  │
  │  → 같은 로직을 타입별로 반복! 비효율적!           │
  └────────────────────────────────────────────────────┘

  제네릭을 쓰면:
  ┌────────────────────────────────────────────────────┐
  │ fn largest<T: PartialOrd>(a: T, b: T) -> T { ... }│
  │  → 하나의 함수로 모든 비교 가능 타입 처리!        │
  └────────────────────────────────────────────────────┘
*/

fn largest<T: PartialOrd + Copy>(a: T, b: T) -> T {
    if a > b { a } else { b }
}

// 여러 trait bound
fn print_largest<T: PartialOrd + Copy + fmt::Display>(a: T, b: T) {
    let big = largest(a, b);
    println!("    큰 값: {}", big);
}

// where 절 (가독성이 좋음)
fn compare_and_show<T>(a: T, b: T)
where
    T: PartialOrd + Copy + fmt::Display + fmt::Debug,
{
    println!("    a={:?}, b={:?}, 큰 쪽={}", a, b, largest(a, b));
}

fn lesson1_generic_functions() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 1: 제네릭 함수");
    println!("═══════════════════════════════════════════");

    println!("  정수 비교:");
    print_largest(10, 20);

    println!("  실수 비교:");
    print_largest(3.14, 2.71);

    println!("  문자 비교:");
    print_largest('a', 'z');

    println!("  where 절:");
    compare_and_show(100, 42);
    println!();
}

// =====================================================================
// 레슨 2 — 제네릭 구조체와 enum
// =====================================================================
/*
★ 구조체와 enum 도 제네릭 가능!

  표준 라이브러리의 대표 제네릭들:
  ┌──────────────────────────────────────────────┐
  │ Option<T>     = Some(T) | None               │
  │ Result<T, E>  = Ok(T) | Err(E)               │
  │ Vec<T>        = 가변 길이 배열               │
  │ HashMap<K, V> = 키-값 맵                     │
  └──────────────────────────────────────────────┘
*/

#[derive(Debug)]
struct Pair<T> {
    first: T,
    second: T,
}

impl<T: PartialOrd + Copy + fmt::Display> Pair<T> {
    fn new(first: T, second: T) -> Self {
        Pair { first, second }
    }

    fn larger(&self) -> &T {
        if self.first > self.second { &self.first } else { &self.second }
    }

    fn show(&self) {
        println!("    Pair({}, {}), 큰 쪽: {}", self.first, self.second, self.larger());
    }
}

// 서로 다른 타입의 제네릭
#[derive(Debug)]
struct KeyValue<K, V> {
    key: K,
    value: V,
}

impl<K: fmt::Display, V: fmt::Display> KeyValue<K, V> {
    fn display(&self) {
        println!("    {} → {}", self.key, self.value);
    }
}

fn lesson2_generic_structs() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 2: 제네릭 구조체");
    println!("═══════════════════════════════════════════");

    let int_pair = Pair::new(10, 20);
    int_pair.show();

    let float_pair = Pair::new(3.14, 2.71);
    float_pair.show();

    let kv1 = KeyValue { key: "이름", value: "철수" };
    let kv2 = KeyValue { key: 1, value: 100.5 };
    kv1.display();
    kv2.display();
    println!();
}

// =====================================================================
// 레슨 3 — 라이프타임: 참조가 얼마나 오래 유효한가
// =====================================================================
/*
★ 라이프타임 = "이 참조가 얼마나 오래 안전하게 살아있는가"

  비유: 도서관 대출
  ┌────────────────────────────────────────────────────────┐
  │ 책(원본 데이터)이 도서관에 있는 동안만 빌릴 수 있음    │
  │ 책이 폐기되면 대출 카드(참조)도 무효!                  │
  │                                                        │
  │ Rust 컴파일러 = 엄격한 사서                            │
  │ → "이 참조가 원본보다 오래 살지 않을까?" 항상 검사     │
  │ → 위험하면 컴파일 거부!                                │
  └────────────────────────────────────────────────────────┘

★ 왜 필요한가?
  ┌────────────────────────────────────────────────────────┐
  │ fn dangerous() -> &String {                            │
  │     let s = String::from("hello");                     │
  │     &s   // ← s 는 함수가 끝나면 사라짐!              │
  │          //   반환된 참조는 허공을 가리키게 됨         │
  │          //   → 이것을 "댕글링 참조" 라고 함          │
  │          //   → Rust 는 이걸 컴파일 시점에 차단!      │
  │ }                                                      │
  └────────────────────────────────────────────────────────┘
*/

fn lesson3_lifetime_concept() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 3: 라이프타임 개념");
    println!("═══════════════════════════════════════════");

    // ── 라이프타임이 잘 동작하는 경우 ──
    let string1 = String::from("긴 문자열입니다");
    let result;
    {
        let string2 = String::from("짧은");
        result = longest(string1.as_str(), string2.as_str());
        // string2 가 아직 살아있으므로 result 사용 OK
        println!("  더 긴 문자열: {}", result);
    }
    // ★ 여기서 result 를 사용하면 위험할 수 있음
    //   (string2 가 이미 drop 되었으므로)
    //   컴파일러가 이를 감지하고 방지!

    println!("  string1 은 아직 유효: {}", string1);
    println!();
}

// =====================================================================
// 레슨 4 — 라이프타임 표기법 'a
// =====================================================================
/*
★ 라이프타임 표기법: 'a (틱 + 이름)

  ┌──────────────────────────────────────────────────────────┐
  │ fn longest<'a>(x: &'a str, y: &'a str) -> &'a str       │
  │            ^^       ^^          ^^          ^^            │
  │  선언      제네릭   x 의 수명  y 의 수명   반환값 수명   │
  │                                                          │
  │ 의미: "x 와 y 중 더 짧은 수명 동안 반환값이 유효하다"   │
  └──────────────────────────────────────────────────────────┘

  ★ 'a 는 실제 수명을 바꾸는 게 아님!
    → 컴파일러에게 "이 참조들의 관계"를 알려주는 것
    → "반환값의 수명 ≤ 입력 참조들 중 가장 짧은 수명"
*/

fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

// 하나의 입력만 참조로 반환 → 그 입력의 라이프타임만 필요
fn first_word(s: &str) -> &str {
    let bytes = s.as_bytes();
    for (i, &byte) in bytes.iter().enumerate() {
        if byte == b' ' {
            return &s[..i];
        }
    }
    s
}

fn lesson4_lifetime_annotations() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 4: 라이프타임 표기법");
    println!("═══════════════════════════════════════════");

    let s1 = "hello world";
    let s2 = "hi";
    println!("  longest: {}", longest(s1, s2));
    println!("  first_word: {}", first_word(s1));

    // 소유권과 라이프타임
    let result;
    let outer = String::from("outer string");
    {
        let inner = String::from("inner");
        result = longest(outer.as_str(), inner.as_str());
        println!("  블록 안에서 결과: {}", result);
    }
    // println!("  블록 밖에서 결과: {}", result);
    // ↑ inner 가 drop 되었으므로 result 가 inner 를 가리킬 수 있어 위험
    //   컴파일러가 이를 방지합니다!
    println!();
}

// =====================================================================
// 레슨 5 — 구조체의 라이프타임
// =====================================================================
/*
★ 구조체에 참조를 넣으려면 라이프타임 표기 필수!

  ┌──────────────────────────────────────────────────────┐
  │ struct Excerpt<'a> {                                 │
  │     text: &'a str,   // 빌려온 문자열 조각          │
  │ }                                                    │
  │                                                      │
  │ 의미: Excerpt 인스턴스는 text 가 가리키는 데이터보다│
  │       오래 살 수 없다!                               │
  └──────────────────────────────────────────────────────┘

  ★ 왜 String 대신 &str 을 쓰나?
    → 소유권을 가져가지 않고 빌려만 쓰고 싶을 때
    → 복사 비용을 아끼고 싶을 때
    → 대신 라이프타임을 명시해야 하는 대가가 있음!
*/

#[derive(Debug)]
struct Excerpt<'a> {
    text: &'a str,
    page: u32,
}

impl<'a> Excerpt<'a> {
    fn new(text: &'a str, page: u32) -> Self {
        Excerpt { text, page }
    }

    // &self 를 반환 → self 의 라이프타임 자동 적용
    fn first_sentence(&self) -> &str {
        self.text.split('.').next().unwrap_or(self.text)
    }

    fn display(&self) {
        println!("    p.{}: \"{}\"", self.page, self.text);
    }
}

fn lesson5_struct_lifetime() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 5: 구조체의 라이프타임");
    println!("═══════════════════════════════════════════");

    let novel = String::from("Rust 는 안전한 언어입니다. 메모리 버그를 방지합니다.");
    let excerpt = Excerpt::new(first_word(&novel), 1);
    excerpt.display();
    println!("    첫 문장: {}", excerpt.first_sentence());

    // 라이프타임 덕분에 안전
    // let dangling;
    // {
    //     let temp = String::from("임시");
    //     dangling = Excerpt::new(&temp, 1);  // ← 컴파일 에러!
    // }  // temp drop → dangling.text 가 댕글링 참조가 됨
    println!("  ★ 컴파일러가 댕글링 참조를 방지합니다!");
    println!();
}

// =====================================================================
// 레슨 6 — 라이프타임 엘리전 규칙
// =====================================================================
/*
★ 엘리전(Elision) = 컴파일러가 라이프타임을 자동으로 추론

  매번 'a 를 쓰기 귀찮으니, 규칙에 맞으면 생략 가능!

  ┌──────────────────────────────────────────────────────────┐
  │ 규칙 1: 각 입력 참조에 고유한 라이프타임 부여            │
  │   fn foo(x: &str, y: &str)                              │
  │   → fn foo<'a, 'b>(x: &'a str, y: &'b str)             │
  │                                                          │
  │ 규칙 2: 입력 참조가 하나뿐이면 출력에 동일 라이프타임   │
  │   fn foo(x: &str) -> &str                               │
  │   → fn foo<'a>(x: &'a str) -> &'a str                  │
  │                                                          │
  │ 규칙 3: &self 가 있으면 self 의 라이프타임 적용         │
  │   fn method(&self, x: &str) -> &str                     │
  │   → fn method<'a, 'b>(&'a self, x: &'b str) -> &'a str │
  └──────────────────────────────────────────────────────────┘

★ 규칙으로 결정 안 되면? → 명시적으로 써야 함!
  → longest 함수가 대표 예: 입력이 2개라 규칙 2 적용 불가
*/

// 엘리전 덕분에 라이프타임 생략 가능한 경우들
fn first_char(s: &str) -> &str {
    // 규칙 2 적용: 입력 1개 → 출력과 같은 라이프타임
    &s[..s.chars().next().map_or(0, |c| c.len_utf8())]
}

fn lesson6_elision_rules() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 6: 라이프타임 엘리전 규칙");
    println!("═══════════════════════════════════════════");

    // 엘리전으로 생략 가능
    println!("  first_char(\"Hello\") = {}", first_char("Hello"));
    println!("  first_char(\"안녕\") = {}", first_char("안녕"));

    println!();
    println!("  ★ 라이프타임을 생략할 수 있는 경우:");
    println!("    → 입력 참조가 1개인 함수");
    println!("    → &self 가 있는 메서드");
    println!();
    println!("  ★ 라이프타임을 명시해야 하는 경우:");
    println!("    → 입력 참조가 2개 이상이고 반환이 참조인 함수");
    println!("    → 구조체에 참조 필드가 있을 때");
    println!();
}

// =====================================================================
// 레슨 7 — 'static 라이프타임
// =====================================================================
/*
★ 'static = 프로그램 전체 수명 동안 유효한 참조

  ┌──────────────────────────────────────────────────────┐
  │ 'static 이 되는 것들:                                │
  │                                                      │
  │ 1. 문자열 리터럴: let s: &'static str = "hello";    │
  │    → 바이너리에 포함되어 프로그램 내내 존재          │
  │                                                      │
  │ 2. const / static 변수                               │
  │    → const MAX: i32 = 100;                           │
  │    → static COUNTER: AtomicI32 = AtomicI32::new(0); │
  │                                                      │
  │ 3. T: 'static bound                                 │
  │    → "참조가 아닌 소유 타입" 또는 'static 참조      │
  │    → String, i32, Vec<T> 등은 T: 'static 만족!     │
  └──────────────────────────────────────────────────────┘

★ 주의: T: 'static ≠ "영원히 사는 값"
  → "T 안에 임시 참조가 없다" 는 뜻!
  → String 은 T: 'static (소유 타입이니까)
  → &'a str 은 T: 'static 아님 ('a 가 임시일 수 있으니까)
*/

fn lesson7_static_lifetime() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 7: 'static 라이프타임");
    println!("═══════════════════════════════════════════");

    // 문자열 리터럴은 'static
    let s: &'static str = "나는 프로그램 끝까지 유효합니다";
    println!("  'static str: {}", s);

    // const 는 항상 'static
    const PI: f64 = 3.14159265;
    println!("  const PI: {}", PI);

    // T: 'static bound 예시
    fn print_if_static<T: fmt::Display + 'static>(val: &T) {
        println!("    'static 만족: {}", val);
    }
    let owned = String::from("소유 타입");
    print_if_static(&owned);      // String 은 T: 'static OK
    print_if_static(&42);         // i32 도 T: 'static OK

    println!();
    println!("  ★ 'static 은 '영원히 사는 것' 이 아닙니다!");
    println!("    → '안에 임시 참조가 없다' 는 의미입니다");
    println!("    → String, i32, Vec<T> 등 소유 타입은 모두 'static");
    println!();
}

// =====================================================================
// 레슨 8 — 제네릭 + 라이프타임 + trait bound 종합
// =====================================================================

fn longest_with_announcement<'a, T>(x: &'a str, y: &'a str, ann: T) -> &'a str
where
    T: fmt::Display,
{
    println!("    알림: {}", ann);
    if x.len() > y.len() { x } else { y }
}

#[derive(Debug)]
struct ImportantExcerpt<'a> {
    content: &'a str,
    level: u32,
}

impl<'a> ImportantExcerpt<'a> {
    fn level(&self) -> u32 {
        self.level
    }

    // 규칙 3: &self 가 있으므로 반환값 라이프타임 = self 의 라이프타임
    fn announce_and_return(&self, announcement: &str) -> &str {
        println!("    알림: {}", announcement);
        self.content
    }
}

impl<'a> fmt::Display for ImportantExcerpt<'a> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[Lv.{}] {}", self.level, self.content)
    }
}

fn lesson8_comprehensive() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 8: 종합 예제");
    println!("═══════════════════════════════════════════");

    // 제네릭 + 라이프타임 + trait bound
    let result = longest_with_announcement(
        "긴 문자열",
        "짧은",
        "비교를 시작합니다!",
    );
    println!("    결과: {}", result);

    // 구조체 + 라이프타임 + impl + Display
    let text = String::from("Rust 는 시스템 프로그래밍 언어입니다");
    let excerpt = ImportantExcerpt {
        content: &text,
        level: 3,
    };
    println!("    {}", excerpt);
    println!("    레벨: {}", excerpt.level());
    let content = excerpt.announce_and_return("중요 발췌!");
    println!("    내용: {}", content);
    println!();
}

// =====================================================================
//  main
// =====================================================================

fn main() {
    println!();
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  Rust 13단계: 제네릭과 라이프타임");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!();

    lesson1_generic_functions();
    lesson2_generic_structs();
    lesson3_lifetime_concept();
    lesson4_lifetime_annotations();
    lesson5_struct_lifetime();
    lesson6_elision_rules();
    lesson7_static_lifetime();
    lesson8_comprehensive();

    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  13단계 완료! 다음은 14_concurrency 입니다");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
}
