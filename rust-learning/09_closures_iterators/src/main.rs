/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Rust 학습 09단계: 클로저와 이터레이터
  ─ Fn/FnMut/FnOnce, 이터레이터 어댑터, 지연 평가 ─

  [학습 목표]
  1. 클로저의 문법과 환경 캡처 방식을 이해한다
  2. Fn, FnMut, FnOnce 트레이트의 차이를 안다
  3. move 클로저의 소유권 이동을 파악한다
  4. 이터레이터 어댑터 체이닝을 능숙하게 쓴다
  5. 지연 평가(lazy evaluation)의 장점을 이해한다
  6. 커스텀 이터레이터를 만들 수 있다

  ■ 실행: cargo run
  ■ 빌드: cargo build --release

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// =====================================================================
// 레슨 1 — 클로저 기본: "들고 다니는 미니 함수"
// =====================================================================
/*
★ 클로저 = 이름 없는 함수 + 바깥 변수 캡처

  비유: 메모지를 손에 쥔 도우미
  ┌────────────────────────────────────────────────────┐
  │ 일반 함수 = 매뉴얼대로만 일하는 직원               │
  │ 클로저    = 메모지(바깥 변수)를 참고하며 일하는     │
  │             유연한 도우미                           │
  └────────────────────────────────────────────────────┘

  문법 비교:
  ┌──────────────────────────────────────────────────┐
  │ fn add(a: i32, b: i32) -> i32 { a + b }         │  함수
  │ let add = |a: i32, b: i32| -> i32 { a + b };    │  클로저 (타입 명시)
  │ let add = |a, b| a + b;                          │  클로저 (타입 추론)
  └──────────────────────────────────────────────────┘
*/

fn lesson1_closure_basics() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 1: 클로저 기본");
    println!("═══════════════════════════════════════════");

    // ── 기본 클로저 ──
    let double = |x: i32| x * 2;
    let add = |a, b| a + b;
    println!("  double(5) = {}", double(5));
    println!("  add(3, 4) = {}", add(3, 4));

    // ── 바깥 변수 캡처 ──
    let bonus = 10;
    let add_bonus = |score| score + bonus;  // bonus 를 캡처!
    println!("  80점 + 보너스 = {}", add_bonus(80));

    // ── 여러 줄 클로저 ──
    let grade = |score: i32| -> &str {
        if score >= 90 { "A" }
        else if score >= 80 { "B" }
        else if score >= 70 { "C" }
        else { "F" }
    };
    println!("  85점 = {} 등급", grade(85));
    println!();
}

// =====================================================================
// 레슨 2 — 캡처 방식: Fn, FnMut, FnOnce
// =====================================================================
/*
★ 클로저가 바깥 변수를 어떻게 잡느냐에 따라 타입이 결정됩니다

  ┌──────────────┬──────────────────────────────────────────────┐
  │ Fn           │ &self 로 캡처 (읽기만, 여러 번 호출 가능)    │
  │ FnMut        │ &mut self 로 캡처 (수정 가능)               │
  │ FnOnce       │ self 로 캡처 (소유권 가져감, 한 번만 호출)  │
  └──────────────┴──────────────────────────────────────────────┘

  ★ 컴파일러가 자동으로 가장 적절한 트레이트를 선택합니다!
    → 읽기만 하면 Fn
    → 수정하면 FnMut
    → 소유권을 가져가면 FnOnce

  ★ 포함 관계: FnOnce ⊃ FnMut ⊃ Fn
    → Fn 을 구현하면 FnMut 도, FnOnce 도 구현됨
*/

fn apply_fn<F: Fn(i32) -> i32>(f: F, val: i32) -> i32 {
    f(val)
}

fn apply_fn_mut<F: FnMut()>(mut f: F) {
    f();
    f();  // FnMut 이므로 여러 번 호출 가능
}

fn apply_fn_once<F: FnOnce() -> String>(f: F) -> String {
    f()   // FnOnce 이므로 한 번만 호출 가능
    // f()  // ← 두 번째 호출은 컴파일 에러!
}

fn lesson2_fn_traits() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 2: Fn / FnMut / FnOnce");
    println!("═══════════════════════════════════════════");

    // ── Fn: 읽기만 ──
    let multiplier = 3;
    let result = apply_fn(|x| x * multiplier, 10);
    println!("  Fn: 10 * {} = {}", multiplier, result);

    // ── FnMut: 수정 ──
    let mut count = 0;
    apply_fn_mut(|| {
        count += 1;    // count 를 변경 → FnMut
        println!("  FnMut 호출: count = {}", count);
    });

    // ── FnOnce: 소유권 이동 ──
    let name = String::from("Rust");
    let greeting = apply_fn_once(|| {
        format!("안녕, {}!", name)  // name 의 소유권을 가져감
        // name 은 클로저 내부로 move 됨
    });
    println!("  FnOnce: {}", greeting);
    // println!("{}", name);  // ← 컴파일 에러! name 은 이미 move 됨
    println!();
}

// =====================================================================
// 레슨 3 — move 클로저: 소유권을 강제로 이동
// =====================================================================
/*
★ move 키워드: 캡처하는 변수의 소유권을 강제로 클로저 안으로 이동

  언제 필요한가?
  ┌────────────────────────────────────────────────────────┐
  │ 1. 클로저가 원래 스코프보다 오래 살아야 할 때          │
  │    → 스레드에 클로저를 넘길 때 (14단계)                │
  │ 2. 클로저가 데이터의 소유자가 되어야 할 때             │
  └────────────────────────────────────────────────────────┘

  비유:
  ┌────────────────────────────────────────────────────────┐
  │ 일반 캡처 = 책을 빌려서 읽기 (원본 자리에 있음)       │
  │ move 캡처 = 책을 들고 다른 방으로 가기 (원래 자리 空) │
  └────────────────────────────────────────────────────────┘
*/

fn lesson3_move_closure() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 3: move 클로저");
    println!("═══════════════════════════════════════════");

    // ── move 없이: 참조로 캡처 ──
    let message = String::from("안녕");
    let greet = || println!("  인사: {}", message);  // &message
    greet();
    println!("  원본 사용 가능: {}", message);

    // ── move 사용: 소유권 이동 ──
    let data = vec![1, 2, 3];
    let own_data = move || {
        println!("  move 클로저 안: {:?}", data);
    };
    own_data();
    // println!("{:?}", data);  // ← 컴파일 에러! data 는 move 됨

    // ── move + Copy 타입: 복사됨 (이동이 아님) ──
    let number = 42;
    let show = move || println!("  숫자: {}", number);
    show();
    println!("  number 아직 사용 가능: {} (i32 는 Copy)", number);
    println!();
}

// =====================================================================
// 레슨 4 — 클로저를 인자로 / 반환값으로
// =====================================================================
/*
★ 함수의 인자로 클로저 받기
  → fn do_something(f: impl Fn(i32) -> i32) { ... }

★ 함수에서 클로저 반환하기
  → fn make_adder(n: i32) -> impl Fn(i32) -> i32 { ... }
  → Box<dyn Fn(...)> 로 반환할 수도 있음

★ 소유권 관점:
  → 반환하는 클로저가 바깥 변수를 캡처하면 move 필수!
    (함수가 끝나면 지역 변수가 사라지니까)
*/

fn apply_twice(f: impl Fn(i32) -> i32, val: i32) -> i32 {
    f(f(val))
}

fn make_adder(n: i32) -> impl Fn(i32) -> i32 {
    move |x| x + n   // n 을 move 로 캡처
}

fn make_multiplier(factor: i32) -> Box<dyn Fn(i32) -> i32> {
    Box::new(move |x| x * factor)
}

fn lesson4_closures_as_args_and_returns() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 4: 클로저를 인자/반환값으로");
    println!("═══════════════════════════════════════════");

    // 클로저를 인자로
    let result = apply_twice(|x| x + 3, 10);
    println!("  (10 + 3) + 3 = {}", result);

    // 클로저를 반환값으로
    let add5 = make_adder(5);
    let add10 = make_adder(10);
    println!("  add5(20) = {}", add5(20));
    println!("  add10(20) = {}", add10(20));

    // Box<dyn Fn> 으로 반환
    let double = make_multiplier(2);
    let triple = make_multiplier(3);
    println!("  double(7) = {}", double(7));
    println!("  triple(7) = {}", triple(7));

    // ★ 클로저 배열 (같은 타입이 아니면 Box 필요!)
    let operations: Vec<Box<dyn Fn(i32) -> i32>> = vec![
        Box::new(|x| x + 1),
        Box::new(|x| x * 2),
        Box::new(|x| x - 5),
    ];
    let mut val = 10;
    for op in &operations {
        val = op(val);
        print!("  → {} ", val);
    }
    println!();
    println!();
}

// =====================================================================
// 레슨 5 — 이터레이터 심화: 어댑터 체이닝
// =====================================================================
/*
★ 이터레이터 체인 = 컨베이어 벨트

  데이터 → filter → map → take → collect → 결과!
  ┌──────┐   ┌────────┐   ┌─────┐   ┌──────┐   ┌─────────┐
  │ 원본 │──▶│ 걸러냄 │──▶│변환 │──▶│ n개만│──▶│ 모으기  │
  └──────┘   └────────┘   └─────┘   └──────┘   └─────────┘

★ 핵심: 이터레이터는 게으르다 (lazy)!
  → filter, map 을 호출해도 아직 실행 안 됨
  → collect, sum, for_each 같은 "소비자"가 호출될 때 비로소 실행
  → 불필요한 연산을 건너뛸 수 있어서 효율적!
*/

fn lesson5_iterator_chaining() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 5: 이터레이터 체이닝");
    println!("═══════════════════════════════════════════");

    let scores = vec![55, 72, 88, 91, 64, 78, 95, 43, 82];

    // ── 70점 이상을 골라서 등급 매기기 ──
    let report: Vec<String> = scores.iter()
        .filter(|&&s| s >= 70)
        .map(|&s| {
            let grade = if s >= 90 { "A" } else if s >= 80 { "B" } else { "C" };
            format!("{}점({})", s, grade)
        })
        .collect();
    println!("  통과자: {:?}", report);

    // ── enumerate: 인덱스와 함께 ──
    for (i, score) in scores.iter().enumerate().filter(|(_, &s)| s >= 90) {
        println!("  [{}번째] {}점 → 우수!", i, score);
    }

    // ── zip: 두 이터레이터 짝짓기 ──
    let names = ["철수", "영희", "민수"];
    let grades = ["A", "B", "C"];
    let pairs: Vec<_> = names.iter().zip(grades.iter()).collect();
    println!("  zip 결과: {:?}", pairs);

    // ── take / skip ──
    let first3: Vec<&i32> = scores.iter().take(3).collect();
    let after3: Vec<&i32> = scores.iter().skip(3).take(3).collect();
    println!("  처음 3개: {:?}", first3);
    println!("  4~6번째:  {:?}", after3);

    // ── chain: 이어붙이기 ──
    let a = vec![1, 2, 3];
    let b = vec![4, 5, 6];
    let combined: Vec<&i32> = a.iter().chain(b.iter()).collect();
    println!("  chain: {:?}", combined);

    // ── flatten: 중첩 풀기 ──
    let nested = vec![vec![1, 2], vec![3, 4], vec![5]];
    let flat: Vec<&i32> = nested.iter().flat_map(|v| v.iter()).collect();
    println!("  flatten: {:?}", flat);
    println!();
}

// =====================================================================
// 레슨 6 — fold 와 scan: 누적 연산
// =====================================================================
/*
★ fold = 모든 원소를 하나의 결과로 접기

  비유: 저금통에 동전을 차례로 넣기
  ┌─────────────────────────────────────────────────────┐
  │ [10, 20, 30].iter().fold(0, |acc, &x| acc + x)     │
  │                                                      │
  │  acc=0  → +10 → acc=10                              │
  │  acc=10 → +20 → acc=30                              │
  │  acc=30 → +30 → acc=60  ← 최종 결과                │
  └─────────────────────────────────────────────────────┘
*/

fn lesson6_fold_and_reduce() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 6: fold 와 누적 연산");
    println!("═══════════════════════════════════════════");

    let numbers = vec![10, 20, 30, 40, 50];

    // ── fold: 합계 ──
    let sum = numbers.iter().fold(0, |acc, &x| acc + x);
    println!("  합계: {}", sum);

    // ── fold: 곱 ──
    let product = vec![2, 3, 4].iter().fold(1, |acc, &x| acc * x);
    println!("  2*3*4 = {}", product);

    // ── fold: 문자열 연결 ──
    let words = vec!["Rust", "는", "재미있다"];
    let sentence = words.iter().fold(String::new(), |mut acc, &w| {
        if !acc.is_empty() { acc.push(' '); }
        acc.push_str(w);
        acc
    });
    println!("  문장: {}", sentence);

    // ── fold: 최댓값 찾기 (수동) ──
    let max = numbers.iter().fold(i32::MIN, |acc, &x| if x > acc { x } else { acc });
    println!("  최댓값: {}", max);

    // ── sum, min, max (간편한 방법) ──
    let total: i32 = numbers.iter().sum();
    println!("  sum(): {}", total);
    println!("  min(): {:?}", numbers.iter().min());
    println!("  max(): {:?}", numbers.iter().max());
    println!();
}

// =====================================================================
// 레슨 7 — 커스텀 이터레이터 만들기
// =====================================================================
/*
★ Iterator 트레이트를 직접 구현하면 for 루프에서 사용 가능!

  trait Iterator {
      type Item;                       // 반환할 원소의 타입
      fn next(&mut self) -> Option<Self::Item>;  // 다음 원소
  }

  → next() 가 None 을 반환하면 이터레이션 종료
*/

struct Countdown {
    count: i32,
}

impl Countdown {
    fn new(start: i32) -> Self {
        Countdown { count: start }
    }
}

impl Iterator for Countdown {
    type Item = i32;

    fn next(&mut self) -> Option<Self::Item> {
        if self.count > 0 {
            let current = self.count;
            self.count -= 1;
            Some(current)
        } else {
            None   // 이터레이션 종료
        }
    }
}

// ── 피보나치 수열 이터레이터 ──
struct Fibonacci {
    a: u64,
    b: u64,
}

impl Fibonacci {
    fn new() -> Self {
        Fibonacci { a: 0, b: 1 }
    }
}

impl Iterator for Fibonacci {
    type Item = u64;

    fn next(&mut self) -> Option<Self::Item> {
        let result = self.a;
        let next = self.a + self.b;
        self.a = self.b;
        self.b = next;
        Some(result)   // 무한 이터레이터! (take 로 제한)
    }
}

fn lesson7_custom_iterator() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 7: 커스텀 이터레이터");
    println!("═══════════════════════════════════════════");

    // ── 카운트다운 ──
    print!("  카운트다운: ");
    for n in Countdown::new(5) {
        print!("{} ", n);
    }
    println!("발사!");

    // ── 이터레이터 어댑터와 조합 ──
    let sum: i32 = Countdown::new(10)
        .filter(|&n| n % 2 == 0)
        .sum();
    println!("  10부터 카운트다운 중 짝수 합: {}", sum);

    // ── 피보나치 (무한 이터레이터 + take) ──
    let fibs: Vec<u64> = Fibonacci::new().take(10).collect();
    println!("  피보나치 10개: {:?}", fibs);

    // 100 이하의 피보나치 수
    let small_fibs: Vec<u64> = Fibonacci::new()
        .take_while(|&n| n <= 100)
        .collect();
    println!("  100 이하 피보나치: {:?}", small_fibs);
    println!();
}

// =====================================================================
// 레슨 8 — 실전 예제: 데이터 처리 파이프라인
// =====================================================================

#[derive(Debug)]
struct Student {
    name: &'static str,
    score: i32,
    grade: i32,   // 학년
}

fn lesson8_real_world_pipeline() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 8: 실전 데이터 파이프라인");
    println!("═══════════════════════════════════════════");

    let students = vec![
        Student { name: "철수", score: 92, grade: 3 },
        Student { name: "영희", score: 88, grade: 2 },
        Student { name: "민수", score: 75, grade: 3 },
        Student { name: "서연", score: 95, grade: 2 },
        Student { name: "지우", score: 68, grade: 1 },
        Student { name: "현우", score: 82, grade: 3 },
    ];

    // 3학년 중 80점 이상인 학생 이름
    let top_3rd: Vec<&str> = students.iter()
        .filter(|s| s.grade == 3 && s.score >= 80)
        .map(|s| s.name)
        .collect();
    println!("  3학년 우수자: {:?}", top_3rd);

    // 학년별 평균 점수
    for grade in 1..=3 {
        let grade_students: Vec<&Student> = students.iter()
            .filter(|s| s.grade == grade)
            .collect();
        if !grade_students.is_empty() {
            let avg: f64 = grade_students.iter()
                .map(|s| s.score as f64)
                .sum::<f64>() / grade_students.len() as f64;
            println!("  {}학년 평균: {:.1}점", grade, avg);
        }
    }

    // 전교 최고점 학생
    if let Some(top) = students.iter().max_by_key(|s| s.score) {
        println!("  전교 1등: {} ({}점)", top.name, top.score);
    }

    // 점수 분포 (구간별)
    let count_90_plus = students.iter().filter(|s| s.score >= 90).count();
    let count_80_89 = students.iter().filter(|s| (80..90).contains(&s.score)).count();
    let count_below = students.iter().filter(|s| s.score < 80).count();
    println!("  90점 이상: {}명 | 80~89: {}명 | 80 미만: {}명",
             count_90_plus, count_80_89, count_below);
    println!();
}

// =====================================================================
//  main
// =====================================================================

fn main() {
    println!();
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  Rust 09단계: 클로저와 이터레이터");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!();

    lesson1_closure_basics();
    lesson2_fn_traits();
    lesson3_move_closure();
    lesson4_closures_as_args_and_returns();
    lesson5_iterator_chaining();
    lesson6_fold_and_reduce();
    lesson7_custom_iterator();
    lesson8_real_world_pipeline();

    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  09단계 완료! 다음은 10_modern_rust 입니다");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
}
