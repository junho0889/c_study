/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Rust 학습 05단계: 구조체와 열거형
  ─ struct, impl, enum, 패턴 매칭, 메서드 ─

  [학습 목표]
  1. struct 로 관련 데이터를 하나로 묶는다
  2. impl 블록으로 메서드와 연관 함수를 정의한다
  3. 튜플 구조체와 유닛 구조체를 이해한다
  4. enum 으로 여러 변형을 하나의 타입에 담는다
  5. match 로 열거형을 빠짐없이 처리한다
  6. 소유권과 구조체의 관계를 파악한다

  ■ 실행: cargo run
  ■ 빌드: cargo build --release

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// =====================================================================
// 레슨 1 — struct 기본: 데이터를 상자에 담기
// =====================================================================
/*
★ struct 는 "이름표가 붙은 상자"
  → 관련 있는 값들을 한 묶음으로 관리한다
  → C 의 struct 와 비슷하지만, 기본이 불변(immutable)!

  비유: 학생 카드
  ┌─────────────────────────────┐
  │  이름: "철수"               │
  │  나이: 14                   │
  │  점수: 92                   │
  └─────────────────────────────┘
  → 카드 한 장 = Student 구조체 하나

★ 소유권 주의!
  - String 필드를 가진 struct 는 기본적으로 move 됩니다
  - &str 대신 String 을 쓰면 구조체가 데이터를 "소유"합니다
  - 참조를 넣으려면 라이프타임이 필요합니다 (13단계)
*/

#[derive(Debug)]          // println!("{:?}", ...) 으로 출력 가능하게
struct Student {
    name: String,          // String → 구조체가 데이터 소유
    age: u32,
    score: f64,
}

fn lesson1_struct_basics() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 1: struct 기본");
    println!("═══════════════════════════════════════════");

    // ── 생성 ──
    let s1 = Student {
        name: String::from("철수"),
        age: 14,
        score: 92.5,
    };
    println!("  학생: {:?}", s1);

    // ── 필드 접근 ──
    println!("  이름: {}", s1.name);
    println!("  점수: {}", s1.score);

    // ── 가변 구조체 ──
    // ★ 전체 구조체가 mut 이어야 필드 변경 가능
    //    (특정 필드만 mut 으로 만들 수 없음!)
    let mut s2 = Student {
        name: String::from("영희"),
        age: 13,
        score: 88.0,
    };
    s2.score = 95.0;  // 전체가 mut 이니까 OK
    println!("  영희 변경된 점수: {}", s2.score);

    // ── 구조체 업데이트 문법 (.. 연산자) ──
    // 나머지 필드를 다른 구조체에서 복사/이동
    let s3 = Student {
        name: String::from("민수"),  // name 은 새로 지정
        ..s2                         // age, score 는 s2 에서 가져옴
    };
    // ★ 주의: s2.name 은 String 이라 move 될 수 있지만
    //         s3 에서 새 name 을 줬으니 s2.name 은 move 안 됨
    //         만약 ..s2 로 name 까지 가져왔다면 s2 는 move 됨!
    println!("  민수: {:?}", s3);
    println!("  s2 아직 사용 가능: age={}", s2.age);
    println!();
}

// =====================================================================
// 레슨 2 — impl: 구조체에 메서드 붙이기
// =====================================================================
/*
★ impl 블록 = 구조체에 "능력"을 부여
  ┌───────────────────────────────────────────┐
  │  impl Student {                           │
  │      fn greet(&self) { ... }   // 메서드  │
  │      fn new(name: &str) -> Self { ... }   │
  │                          ↑ 연관 함수      │
  │  }                                        │
  └───────────────────────────────────────────┘

★ &self, &mut self, self 의 차이
  ┌────────────┬─────────────────────────────────────────┐
  │ &self      │ 빌려서 읽기만 (대부분의 메서드)          │
  │ &mut self  │ 빌려서 수정도 함                         │
  │ self       │ 소유권을 가져감 → 호출 후 원본 못 씀     │
  └────────────┴─────────────────────────────────────────┘
*/

struct Rectangle {
    width: f64,
    height: f64,
}

impl Rectangle {
    // ── 연관 함수 (생성자 역할) ──
    // Self 는 Rectangle 자체를 뜻함
    fn new(w: f64, h: f64) -> Self {
        Rectangle { width: w, height: h }
    }

    // ── 메서드: &self 로 읽기 전용 ──
    fn area(&self) -> f64 {
        self.width * self.height
    }

    fn perimeter(&self) -> f64 {
        2.0 * (self.width + self.height)
    }

    fn is_square(&self) -> bool {
        (self.width - self.height).abs() < f64::EPSILON
    }

    // ── 메서드: &mut self 로 크기 변경 ──
    fn scale(&mut self, factor: f64) {
        self.width *= factor;
        self.height *= factor;
    }

    // ── 메서드: self 로 소유권 소비 ──
    // 호출 후 원본 사용 불가!
    fn into_description(self) -> String {
        format!("{}x{} 직사각형 (넓이={})", self.width, self.height, self.area())
    }
}

fn lesson2_impl_methods() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 2: impl 메서드");
    println!("═══════════════════════════════════════════");

    let mut rect = Rectangle::new(10.0, 5.0);
    println!("  넓이: {}", rect.area());
    println!("  둘레: {}", rect.perimeter());
    println!("  정사각형? {}", rect.is_square());

    rect.scale(2.0);
    println!("  2배 확대 후 넓이: {}", rect.area());

    // self 를 소비하는 메서드
    let desc = rect.into_description();
    println!("  설명: {}", desc);
    // println!("{}", rect.area());  // ← 컴파일 에러! rect 은 이미 move 됨
    println!();
}

// =====================================================================
// 레슨 3 — 튜플 구조체와 뉴타입 패턴
// =====================================================================
/*
★ 튜플 구조체: 필드 이름 없이 순서만으로 구분
  → 새로운 타입을 빠르게 만들고 싶을 때 유용

★ 뉴타입 패턴(Newtype Pattern)
  → 기존 타입을 감싸서 의미를 부여
  → 단위 혼동 사고를 방지!

  ┌──────────────────────────────────────────────────┐
  │ struct Color(u8, u8, u8);       // 튜플 구조체   │
  │ struct Meters(f64);             // 뉴타입 패턴   │
  │ struct Marker;                  // 유닛 구조체   │
  └──────────────────────────────────────────────────┘

★ 유닛 구조체: 필드가 아예 없음
  → 트레이트만 구현할 때 사용 (06단계에서 다시)
*/

struct Color(u8, u8, u8);
struct Meters(f64);
struct Kilometers(f64);

impl Meters {
    fn to_km(&self) -> Kilometers {
        Kilometers(self.0 / 1000.0)
    }
}

fn lesson3_tuple_and_unit_structs() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 3: 튜플 구조체 & 뉴타입 패턴");
    println!("═══════════════════════════════════════════");

    let red = Color(255, 0, 0);
    println!("  빨강: ({}, {}, {})", red.0, red.1, red.2);

    // ★ 뉴타입 패턴: 단위 혼동 방지!
    // Meters 와 Kilometers 는 둘 다 f64 이지만 서로 다른 타입
    let distance = Meters(5000.0);
    let km = distance.to_km();
    println!("  {}m = {}km", distance.0, km.0);
    // let wrong: Meters = km;  // 컴파일 에러! 타입이 다름
    println!();
}

// =====================================================================
// 레슨 4 — enum: 가능한 변형을 나열하기
// =====================================================================
/*
★ Rust 의 enum 은 C/C++ 보다 훨씬 강력합니다!
  → 각 변형(variant)에 데이터를 넣을 수 있습니다
  → 함수형 언어의 "대수적 데이터 타입" 과 같습니다

  비유: 택배 상태
  ┌──────────────────────────────────────────┐
  │ 주문됨                     → 데이터 없음 │
  │ 배송 중(위치: "인천 허브") → String 포함 │
  │ 배달 완료(일시: 14:30)    → 시간 포함    │
  │ 반품(사유: "파손")        → String 포함  │
  └──────────────────────────────────────────┘

★ 소유권: enum 변형이 데이터를 가지면, enum 이 소유합니다
*/

#[derive(Debug)]
enum DeliveryStatus {
    Ordered,                         // 데이터 없음
    Shipping { location: String },   // 이름 있는 필드 (구조체 변형)
    Delivered(String),               // 튜플형 변형
    Returned { reason: String },
}

#[derive(Debug)]
enum Shape {
    Circle(f64),                          // 반지름
    Rect(f64, f64),                       // 가로, 세로
    Triangle { base: f64, height: f64 },  // 이름 있는 필드
}

impl Shape {
    fn area(&self) -> f64 {
        match self {
            Shape::Circle(r)                 => std::f64::consts::PI * r * r,
            Shape::Rect(w, h)                => w * h,
            Shape::Triangle { base, height } => 0.5 * base * height,
        }
    }

    fn name(&self) -> &str {
        match self {
            Shape::Circle(_)       => "원",
            Shape::Rect(_, _)      => "직사각형",
            Shape::Triangle { .. } => "삼각형",   // .. 은 나머지 필드 무시
        }
    }
}

fn lesson4_enum() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 4: enum 기본");
    println!("═══════════════════════════════════════════");

    let status = DeliveryStatus::Shipping {
        location: String::from("인천 허브"),
    };
    println!("  택배 상태: {:?}", status);

    let shapes = [
        Shape::Circle(5.0),
        Shape::Rect(4.0, 6.0),
        Shape::Triangle { base: 3.0, height: 8.0 },
    ];
    for s in &shapes {
        println!("  {} 넓이: {:.2}", s.name(), s.area());
    }
    println!();
}

// =====================================================================
// 레슨 5 — match: 빠짐없는 패턴 매칭
// =====================================================================
/*
★ match 는 if-else 의 상위 호환
  → 모든 경우를 빠짐없이 처리해야 컴파일됨 (exhaustive)
  → 빠뜨리면 컴파일러가 알려줌 → 버그 방지!

  ┌───────────────────────────────────────────────┐
  │ match 값 {                                    │
  │     패턴1 => 결과1,                            │
  │     패턴2 if 조건 => 결과2,   // 가드          │
  │     _ => 기본값,               // 나머지 전부  │
  │ }                                              │
  └───────────────────────────────────────────────┘

★ 패턴에서 값을 꺼낼 수 있습니다 (destructuring)
  → enum 안의 데이터를 바로 변수로 바인딩!
*/

fn describe_delivery(status: &DeliveryStatus) -> String {
    match status {
        DeliveryStatus::Ordered => {
            String::from("주문이 접수되었습니다")
        }
        DeliveryStatus::Shipping { location } => {
            format!("현재 {} 에서 배송 중입니다", location)
        }
        DeliveryStatus::Delivered(time) => {
            format!("{} 에 배달 완료되었습니다", time)
        }
        DeliveryStatus::Returned { reason } => {
            format!("반품 처리됨 (사유: {})", reason)
        }
    }
}

fn lesson5_match() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 5: match 패턴 매칭");
    println!("═══════════════════════════════════════════");

    let statuses = [
        DeliveryStatus::Ordered,
        DeliveryStatus::Shipping { location: String::from("서울 강남") },
        DeliveryStatus::Delivered(String::from("14:30")),
        DeliveryStatus::Returned { reason: String::from("파손") },
    ];
    for s in &statuses {
        println!("  {}", describe_delivery(s));
    }

    // ── 숫자 범위 match ──
    let score = 85;
    let grade = match score {
        90..=100 => "A",
        80..=89  => "B",
        70..=79  => "C",
        60..=69  => "D",
        0..=59   => "F",
        _        => "범위 밖",
    };
    println!("  {}점 → {} 등급", score, grade);

    // ── 여러 패턴 (|) ──
    let day = "토";
    let is_weekend = matches!(day, "토" | "일");
    println!("  '{}' 은 주말? {}", day, is_weekend);

    // ── 가드(guard) 조건 ──
    let temperature = 38;
    let msg = match temperature {
        t if t >= 40 => "위험! 극한 더위",
        t if t >= 35 => "폭염 주의",
        t if t >= 25 => "여름 날씨",
        _            => "쾌적",
    };
    println!("  {}도 → {}", temperature, msg);
    println!();
}

// =====================================================================
// 레슨 6 — Option<T>: null 대신 안전한 "있거나 없거나"
// =====================================================================
/*
★ Rust 에는 null 이 없습니다!
  대신 Option<T> 열거형을 사용합니다:

    enum Option<T> {
        Some(T),   // 값이 있음
        None,      // 값이 없음
    }

  비유: 선물 상자
  ┌──────────────────────────────┐
  │ Some("인형")  → 열어보니 有  │
  │ None          → 열어보니 空  │
  └──────────────────────────────┘

★ 왜 좋은가?
  → None 일 때 무시할 수 없음 (컴파일러가 강제)
  → null pointer exception 같은 런타임 에러 원천 차단

★ 자주 쓰는 Option 메서드들
  ┌───────────────────┬────────────────────────────────────┐
  │ unwrap()          │ 값 꺼냄 (None 이면 panic!)         │
  │ unwrap_or(기본값) │ 값 꺼내되, None 이면 기본값 사용   │
  │ is_some()         │ 값이 있는지 bool 반환               │
  │ map(함수)         │ 값이 있으면 변환, 없으면 None 유지 │
  │ and_then(함수)    │ 값이 있으면 다른 Option 반환       │
  └───────────────────┴────────────────────────────────────┘
*/

fn find_student_score(name: &str) -> Option<f64> {
    match name {
        "철수" => Some(95.0),
        "영희" => Some(88.0),
        _      => None,
    }
}

fn lesson6_option() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 6: Option<T>");
    println!("═══════════════════════════════════════════");

    // ── match 로 안전하게 꺼내기 ──
    match find_student_score("철수") {
        Some(score) => println!("  철수 점수: {}", score),
        None        => println!("  철수를 찾을 수 없음"),
    }

    // ── if let 으로 간결하게 ──
    if let Some(score) = find_student_score("영희") {
        println!("  영희 점수: {}", score);
    }

    // ── unwrap_or: 없으면 기본값 ──
    let score = find_student_score("민수").unwrap_or(0.0);
    println!("  민수 점수 (기본값 0): {}", score);

    // ── map: 값이 있을 때만 변환 ──
    let grade = find_student_score("철수")
        .map(|s| if s >= 90.0 { "A" } else { "B" });
    println!("  철수 등급: {:?}", grade);   // Some("A")

    // ── and_then: 체이닝 (Option 을 반환하는 함수 연결) ──
    let result = find_student_score("철수")
        .and_then(|s| if s >= 90.0 { Some("장학금 대상") } else { None });
    println!("  철수 장학금: {:?}", result);

    // ★ 흔한 실수: unwrap() 을 함부로 쓰면 panic!
    // find_student_score("없는학생").unwrap();  // ← panic 발생!
    println!();
}

// =====================================================================
// 레슨 7 — 구조체와 소유권: 흔한 함정 모음
// =====================================================================
/*
★ 구조체를 함수에 넘길 때 소유권 규칙이 그대로 적용됩니다

  ┌──────────────────────────────────────────────────┐
  │ 전달 방법      │ 원본 사용 │ 수정 │ 설명         │
  ├──────────────────────────────────────────────────┤
  │ 값 전달 (move) │    X      │  -   │ 소유권 이동  │
  │ & (참조)       │    O      │  X   │ 읽기만       │
  │ &mut (가변참조)│    O      │  O   │ 수정 가능    │
  │ .clone()       │    O      │  -   │ 복사본 전달  │
  └──────────────────────────────────────────────────┘
*/

#[derive(Debug, Clone)]
struct Book {
    title: String,
    pages: u32,
}

fn print_book(book: &Book) {
    println!("    제목: {}, 페이지: {}", book.title, book.pages);
}

fn add_page(book: &mut Book) {
    book.pages += 1;
}

fn consume_book(book: Book) {
    println!("    '{}' 을 다 읽고 반납했습니다", book.title);
    // book 은 이 함수 끝에서 drop
}

fn lesson7_struct_ownership() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 7: 구조체와 소유권");
    println!("═══════════════════════════════════════════");

    let mut book = Book {
        title: String::from("Rust in Action"),
        pages: 400,
    };

    // 참조로 빌림 → book 계속 사용 가능
    print_book(&book);

    // 가변 참조로 수정
    add_page(&mut book);
    println!("  페이지 수정 후: {}", book.pages);

    // clone 으로 복사본 전달
    let backup = book.clone();
    consume_book(backup);
    println!("  원본 아직 사용 가능: {:?}", book);

    // 원본을 소비
    consume_book(book);
    // println!("{:?}", book);  // ← 컴파일 에러! move 됨
    println!();
}

// =====================================================================
// 레슨 8 — derive: 자동으로 트레이트 구현 붙이기
// =====================================================================
/*
★ #[derive(...)] 로 자주 쓰는 트레이트를 자동 구현

  ┌──────────────┬──────────────────────────────────┐
  │ Debug        │ {:?} 로 출력 가능                │
  │ Clone        │ .clone() 으로 깊은 복사           │
  │ Copy         │ 대입 시 자동 복사 (move 안 함)   │
  │ PartialEq    │ == 비교 가능                      │
  │ PartialOrd   │ <, > 비교 가능                    │
  │ Default      │ 기본값 생성                       │
  └──────────────┴──────────────────────────────────┘

★ Copy 는 모든 필드가 Copy 일 때만 사용 가능!
  → String 필드가 있으면 Copy 불가 (Clone 만 가능)
  → i32, f64, bool 같은 스택 타입은 기본적으로 Copy
*/

#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
struct Point {
    x: f64,
    y: f64,
}

impl Point {
    fn distance_to(&self, other: &Point) -> f64 {
        ((self.x - other.x).powi(2) + (self.y - other.y).powi(2)).sqrt()
    }
}

impl Default for Point {
    fn default() -> Self {
        Point { x: 0.0, y: 0.0 }
    }
}

fn lesson8_derive() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 8: derive 자동 구현");
    println!("═══════════════════════════════════════════");

    let p1 = Point { x: 3.0, y: 4.0 };
    let p2 = p1;  // ★ Copy 이므로 move 가 아닌 복사!
    println!("  p1: {:?}", p1);   // 여전히 사용 가능!
    println!("  p2: {:?}", p2);

    let origin = Point::default();
    println!("  원점: {:?}", origin);
    println!("  p1 에서 원점까지 거리: {:.2}", p1.distance_to(&origin));

    // PartialEq 덕분에 비교 가능
    println!("  p1 == p2 ? {}", p1 == p2);
    println!();
}

// =====================================================================
//  main
// =====================================================================

fn main() {
    println!();
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  Rust 05단계: 구조체와 열거형");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!();

    lesson1_struct_basics();
    lesson2_impl_methods();
    lesson3_tuple_and_unit_structs();
    lesson4_enum();
    lesson5_match();
    lesson6_option();
    lesson7_struct_ownership();
    lesson8_derive();

    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  05단계 완료! 다음은 06_traits 입니다");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
}
