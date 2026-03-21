/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Rust 학습 10단계: 모던 Rust 패턴
  ─ if let, while let, let-else, 패턴 심화, 타입 별칭, 뉴타입 ─

  [학습 목표]
  1. if let / while let 으로 간결하게 패턴 매칭한다
  2. let-else 패턴을 사용한다
  3. 구조체/튜플/슬라이스 디스트럭처링을 안다
  4. matches! 매크로를 활용한다
  5. 타입 별칭과 뉴타입 패턴을 이해한다
  6. 제로 비용 추상화 원칙을 이해한다

  ■ 실행: cargo run
  ■ 빌드: cargo build --release

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// =====================================================================
// 레슨 1 — if let / while let: 간결한 패턴 매칭
// =====================================================================
/*
★ if let = "이 패턴에 맞으면 실행해줘"
  → match 로 모든 경우를 쓰기 번거로울 때 사용

  비유:
  ┌────────────────────────────────────────────────────────┐
  │ match 상자 {                   if let Some(x) = 상자 {│
  │     Some(x) => 사용(x),   →       사용(x);           │
  │     None => {},                }                       │
  │ }                                                      │
  └────────────────────────────────────────────────────────┘
  → 관심 있는 경우만 처리, 나머지는 무시!

★ while let = "패턴에 맞는 동안 반복"
  → 스택에서 원소를 하나씩 꺼낼 때 유용
*/

fn lesson1_if_let_while_let() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 1: if let / while let");
    println!("═══════════════════════════════════════════");

    // ── if let: Option 에서 값 꺼내기 ──
    let nickname: Option<&str> = Some("코딩왕");
    if let Some(name) = nickname {
        println!("  별명: {}", name);
    }

    let empty: Option<&str> = None;
    if let Some(name) = empty {
        println!("  이건 출력 안 됨: {}", name);
    } else {
        println!("  별명 없음!");
    }

    // ── if let: enum 에서 특정 변형만 처리 ──
    #[derive(Debug)]
    enum Command {
        Quit,
        Echo(String),
        Move { x: i32, y: i32 },
    }

    let cmd = Command::Move { x: 10, y: 20 };
    if let Command::Move { x, y } = &cmd {
        println!("  이동: ({}, {})", x, y);
    }

    // ── while let: 스택에서 하나씩 꺼내기 ──
    let mut stack = vec![1, 2, 3, 4, 5];
    print!("  스택 pop: ");
    while let Some(top) = stack.pop() {
        print!("{} ", top);
    }
    println!();
    println!();
}

// =====================================================================
// 레슨 2 — let-else: 실패하면 빠져나가기
// =====================================================================
/*
★ let-else = "패턴에 맞으면 바인딩, 아니면 분기"
  → Rust 1.65+ 에서 사용 가능

  ┌──────────────────────────────────────────────────────┐
  │ let Some(value) = option else {                      │
  │     return;  // 또는 continue, break, panic!         │
  │ };                                                    │
  │ // 여기서 value 사용 가능!                            │
  └──────────────────────────────────────────────────────┘

  비유: 문 앞 검사원
  "신분증 있으면 들어오세요, 없으면 돌아가세요"
*/

fn process_name(input: Option<&str>) -> String {
    let Some(name) = input else {
        return String::from("(이름 없음)");
    };
    // 여기부터 name 은 확정적으로 &str
    format!("환영합니다, {}님!", name)
}

fn parse_port(s: &str) -> Result<u16, String> {
    let Ok(port) = s.parse::<u16>() else {
        return Err(format!("'{}' 는 유효한 포트 번호가 아닙니다", s));
    };
    if port < 1024 {
        return Err(format!("포트 {} 는 예약 포트입니다", port));
    }
    Ok(port)
}

fn lesson2_let_else() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 2: let-else 패턴");
    println!("═══════════════════════════════════════════");

    println!("  {}", process_name(Some("철수")));
    println!("  {}", process_name(None));

    println!("  포트 8080: {:?}", parse_port("8080"));
    println!("  포트 abc: {:?}", parse_port("abc"));
    println!("  포트 80: {:?}", parse_port("80"));
    println!();
}

// =====================================================================
// 레슨 3 — 디스트럭처링: 구조체/튜플/슬라이스 분해
// =====================================================================
/*
★ 디스트럭처링 = 복합 데이터를 개별 변수로 분해

  ┌───────────────────────────────────────────────────────┐
  │ 튜플:     let (x, y, z) = (1, 2, 3);                │
  │ 구조체:   let Point { x, y } = point;                │
  │ 슬라이스: let [first, .., last] = &arr;              │
  │ 참조:     let &n = &42;                               │
  └───────────────────────────────────────────────────────┘
*/

#[derive(Debug)]
struct Point {
    x: f64,
    y: f64,
}

#[derive(Debug)]
struct Student {
    name: String,
    score: i32,
    grade: i32,
}

fn lesson3_destructuring() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 3: 디스트럭처링");
    println!("═══════════════════════════════════════════");

    // ── 튜플 분해 ──
    let (name, age, score) = ("철수", 14, 92);
    println!("  튜플: {} {}세 {}점", name, age, score);

    // 일부만 필요할 때: _ 로 무시
    let (_, _, only_score) = ("영희", 13, 88);
    println!("  점수만: {}", only_score);

    // ── 구조체 분해 ──
    let p = Point { x: 3.0, y: 4.0 };
    let Point { x, y } = &p;
    println!("  Point: x={}, y={}", x, y);

    // 필드 이름 바꾸기
    let Point { x: px, y: py } = p;
    println!("  Point(renamed): px={}, py={}", px, py);

    // ── 중첩 분해 ──
    let ((a, b), Point { x, y }) = ((1, 2), Point { x: 5.0, y: 6.0 });
    println!("  중첩: a={}, b={}, x={}, y={}", a, b, x, y);

    // ── 함수 매개변수에서 분해 ──
    fn print_point(&Point { x, y }: &Point) {
        println!("  함수 내 분해: ({}, {})", x, y);
    }
    let p2 = Point { x: 10.0, y: 20.0 };
    print_point(&p2);

    // ── 슬라이스 분해 ──
    let numbers = [1, 2, 3, 4, 5];
    if let [first, .., last] = numbers {
        println!("  슬라이스: first={}, last={}", first, last);
    }
    if let [a, b, rest @ ..] = &numbers[..] {
        println!("  rest 패턴: a={}, b={}, rest={:?}", a, b, rest);
    }
    println!();
}

// =====================================================================
// 레슨 4 — matches! 매크로와 고급 패턴
// =====================================================================
/*
★ matches! = "이 값이 이 패턴에 맞나?" → bool 반환

  ┌──────────────────────────────────────────────────────┐
  │ matches!(value, pattern)                             │
  │ matches!(value, pattern if guard)                    │
  │                                                      │
  │ 예: matches!(x, 1..=5)     → x 가 1~5 인지?        │
  │ 예: matches!(s, "a" | "b") → s 가 "a" 또는 "b" ?   │
  └──────────────────────────────────────────────────────┘

★ @ 바인딩: 패턴 매칭하면서 동시에 변수에 바인딩

  match score {
      s @ 90..=100 => println!("A: {}", s),
      s @ 80..=89  => println!("B: {}", s),
      _ => {}
  }
*/

fn lesson4_matches_and_advanced() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 4: matches! 와 고급 패턴");
    println!("═══════════════════════════════════════════");

    // ── matches! 기본 ──
    let x = 42;
    println!("  42 는 40..=50? {}", matches!(x, 40..=50));
    println!("  42 는 짝수? {}", matches!(x, n if n % 2 == 0));

    let day = "토";
    println!("  '토' 은 주말? {}", matches!(day, "토" | "일"));

    // ── 이터레이터와 matches! 조합 ──
    let scores = vec![55, 72, 88, 91, 64, 95];
    let count_a = scores.iter().filter(|&&s| matches!(s, 90..=100)).count();
    println!("  A등급(90+) 수: {}", count_a);

    // ── @ 바인딩 ──
    let score = 87;
    match score {
        s @ 90..=100 => println!("  {}점 → A등급", s),
        s @ 80..=89  => println!("  {}점 → B등급", s),
        s @ 70..=79  => println!("  {}점 → C등급", s),
        s            => println!("  {}점 → F등급", s),
    }

    // ── ref 패턴: 소유권 이동 방지 ──
    let name = String::from("Rust");
    match &name {
        n if n.len() > 3 => println!("  긴 이름: {}", n),
        n                => println!("  짧은 이름: {}", n),
    }
    println!("  name 아직 사용 가능: {}", name);
    println!();
}

// =====================================================================
// 레슨 5 — 타입 별칭과 뉴타입 패턴
// =====================================================================
/*
★ 타입 별칭 (type alias): 긴 타입에 짧은 이름 붙이기
  → 새 타입을 만드는 게 아님! 그냥 별명

  type Result<T> = std::result::Result<T, MyError>;
  type Callback = Box<dyn Fn(i32) -> i32>;

★ 뉴타입 패턴 (Newtype): 실제로 새 타입을 만듦
  → 튜플 구조체로 감싸기
  → 타입 안전성, 고아 규칙 우회에 유용

  ┌────────────────────────────────────────────────────┐
  │ type Km = f64;        // 별칭 → Km 과 f64 호환    │
  │ struct Km(f64);       // 뉴타입 → Km 과 f64 불호환│
  └────────────────────────────────────────────────────┘
*/

// 타입 별칭
type Score = i32;
type StudentMap = std::collections::HashMap<String, Score>;

// 뉴타입
struct Meters(f64);
struct Seconds(f64);

impl Meters {
    fn value(&self) -> f64 { self.0 }
}

impl Seconds {
    fn value(&self) -> f64 { self.0 }
}

// 뉴타입 덕분에 실수 방지
fn calculate_speed(distance: &Meters, time: &Seconds) -> f64 {
    distance.value() / time.value()
}

fn lesson5_type_alias_newtype() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 5: 타입 별칭 & 뉴타입");
    println!("═══════════════════════════════════════════");

    // ── 타입 별칭 ──
    let mut students: StudentMap = StudentMap::new();
    students.insert(String::from("철수"), 92);
    students.insert(String::from("영희"), 88);
    println!("  학생 맵: {:?}", students);

    // ── 뉴타입으로 단위 안전성 ──
    let dist = Meters(100.0);
    let time = Seconds(9.58);
    let speed = calculate_speed(&dist, &time);
    println!("  {}m / {}s = {:.2} m/s", dist.0, time.0, speed);

    // ★ 이렇게 하면 컴파일 에러!
    // calculate_speed(&time, &dist);  // Meters 와 Seconds 뒤바뀜 → 에러!
    println!("  ★ 뉴타입 덕분에 인자 순서 실수를 컴파일러가 잡아줍니다!");
    println!();
}

// =====================================================================
// 레슨 6 — 제로 비용 추상화 (Zero-Cost Abstractions)
// =====================================================================
/*
★ Rust 의 핵심 철학: "쓰지 않는 것에 비용을 내지 않는다"

  ┌──────────────────────────────────────────────────────────┐
  │ 1. 이터레이터 체이닝 = for 루프만큼 빠름                 │
  │    → 컴파일러가 자동으로 최적화 (인라인 + 루프 풀기)    │
  │                                                          │
  │ 2. 제네릭 = 각 타입별로 코드를 생성 (단형화)            │
  │    → 런타임 오버헤드 없음                                │
  │                                                          │
  │ 3. 뉴타입 = 런타임에 래퍼 비용 없음                     │
  │    → struct Meters(f64) 는 f64 와 동일한 기계 코드      │
  │                                                          │
  │ 4. trait 의 정적 디스패치 = 가상 함수 호출 없음          │
  │    → impl Trait 은 컴파일 시 구체 타입으로 결정          │
  └──────────────────────────────────────────────────────────┘

  비유:
  ┌────────────────────────────────────────────────────────┐
  │ 다른 언어: 편리한 기능 = 느린 코드 (트레이드오프)      │
  │ Rust: 편리한 기능 = 수작업 코드만큼 빠름 (제로 비용)   │
  └────────────────────────────────────────────────────────┘
*/

fn lesson6_zero_cost() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 6: 제로 비용 추상화");
    println!("═══════════════════════════════════════════");

    let numbers: Vec<i32> = (1..=100).collect();

    // 방법 1: 이터레이터 체이닝 (고수준, 읽기 좋음)
    let sum1: i32 = numbers.iter()
        .filter(|&&n| n % 2 == 0)
        .map(|&n| n * n)
        .sum();

    // 방법 2: 수동 for 루프 (저수준)
    let mut sum2 = 0;
    for &n in &numbers {
        if n % 2 == 0 {
            sum2 += n * n;
        }
    }

    // ★ 둘 다 동일한 성능! 컴파일러가 같은 기계 코드로 최적화!
    println!("  이터레이터 방식: {}", sum1);
    println!("  for 루프 방식:   {}", sum2);
    assert_eq!(sum1, sum2);
    println!("  ★ 두 방식의 결과가 같고, 성능도 동일합니다!");

    // ── 단형화(Monomorphization) 예시 ──
    fn max_of<T: PartialOrd>(a: T, b: T) -> T {
        if a > b { a } else { b }
    }
    // 컴파일러는 이 함수를 i32 버전, f64 버전으로 각각 생성
    println!("  max(3, 5) = {}", max_of(3, 5));
    println!("  max(3.14, 2.71) = {}", max_of(3.14, 2.71));
    println!("  ★ 제네릭 함수는 타입별로 전용 코드가 생성됩니다 (단형화)");
    println!();
}

// =====================================================================
// 레슨 7 — 실전 패턴 모음: 빌더, From/Into, Display
// =====================================================================

#[derive(Debug)]
struct Config {
    host: String,
    port: u16,
    max_connections: u32,
    debug: bool,
}

// ── 빌더 패턴 ──
struct ConfigBuilder {
    host: String,
    port: u16,
    max_connections: u32,
    debug: bool,
}

impl ConfigBuilder {
    fn new() -> Self {
        ConfigBuilder {
            host: String::from("localhost"),
            port: 8080,
            max_connections: 100,
            debug: false,
        }
    }

    fn host(mut self, host: &str) -> Self {
        self.host = host.to_string();
        self
    }

    fn port(mut self, port: u16) -> Self {
        self.port = port;
        self
    }

    fn max_connections(mut self, max: u32) -> Self {
        self.max_connections = max;
        self
    }

    fn debug(mut self, debug: bool) -> Self {
        self.debug = debug;
        self
    }

    fn build(self) -> Config {
        Config {
            host: self.host,
            port: self.port,
            max_connections: self.max_connections,
            debug: self.debug,
        }
    }
}

fn lesson7_practical_patterns() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 7: 실전 패턴 (빌더 등)");
    println!("═══════════════════════════════════════════");

    // ── 빌더 패턴: 체이닝으로 설정 ──
    let config = ConfigBuilder::new()
        .host("0.0.0.0")
        .port(3000)
        .max_connections(500)
        .debug(true)
        .build();
    println!("  설정: {:?}", config);

    // ── 기본값으로 빌드 ──
    let default_config = ConfigBuilder::new().build();
    println!("  기본 설정: {:?}", default_config);
    println!();
}

// =====================================================================
//  main
// =====================================================================

fn main() {
    println!();
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  Rust 10단계: 모던 Rust 패턴");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!();

    lesson1_if_let_while_let();
    lesson2_let_else();
    lesson3_destructuring();
    lesson4_matches_and_advanced();
    lesson5_type_alias_newtype();
    lesson6_zero_cost();
    lesson7_practical_patterns();

    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  10단계 완료! 다음은 11_debugging 입니다");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
}
