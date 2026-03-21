/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Rust 학습 14단계: 동시성 (Concurrency)
  ─ thread, Mutex, Arc, 채널, Send/Sync ─

  [학습 목표]
  1. thread::spawn 으로 스레드를 생성한다
  2. move 클로저로 데이터를 스레드에 넘긴다
  3. 채널(channel)로 스레드 간 메시지를 전달한다
  4. Mutex<T> 로 공유 데이터를 보호한다
  5. Arc<T> 로 여러 스레드에 소유권을 공유한다
  6. Send 와 Sync 트레이트를 이해한다

  ■ 실행: cargo run
  ■ 빌드: cargo build --release

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

use std::sync::{Arc, Mutex, mpsc};
use std::thread;
use std::time::Duration;

// =====================================================================
// 레슨 1 — 스레드 기본: 동시에 여러 일 하기
// =====================================================================
/*
★ 스레드 = 프로그램 안의 독립적인 실행 흐름

  비유: 주방에서 요리
  ┌──────────────────────────────────────────────────────┐
  │ 스레드 1개 = 혼자 요리                               │
  │   → 국 끓이고, 밥 하고, 반찬 만들고... 순서대로     │
  │                                                      │
  │ 스레드 여러 개 = 여러 요리사                         │
  │   → 한 명은 국, 한 명은 밥, 한 명은 반찬            │
  │   → 동시에 진행! 하지만 같은 냄비를 쓰면 충돌!     │
  └──────────────────────────────────────────────────────┘

★ Rust 의 특별한 점:
  → 컴파일러가 데이터 경쟁(data race) 을 원천 차단!
  → "두 스레드가 동시에 같은 데이터를 수정" → 컴파일 에러!
  → 다른 언어에서는 런타임에 터지는 버그를 Rust 는 컴파일 시점에 잡음
*/

fn lesson1_thread_basics() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 1: 스레드 기본");
    println!("═══════════════════════════════════════════");

    // ── 스레드 생성 ──
    let handle = thread::spawn(|| {
        for i in 1..=3 {
            println!("    작업 스레드: {}", i);
            thread::sleep(Duration::from_millis(1));
        }
    });

    // 메인 스레드도 동시에 실행
    for i in 1..=2 {
        println!("    메인 스레드: {}", i);
        thread::sleep(Duration::from_millis(1));
    }

    // ★ join() 으로 스레드가 끝날 때까지 기다림
    handle.join().unwrap();
    println!("  모든 스레드 완료!");
    println!();
}

// =====================================================================
// 레슨 2 — move 클로저: 데이터를 스레드에 넘기기
// =====================================================================
/*
★ 스레드에 데이터를 넘기려면 move 필수!

  왜?
  ┌──────────────────────────────────────────────────────┐
  │ 스레드는 메인 스레드보다 오래 살 수 있음              │
  │ → 참조로 빌려주면 메인이 먼저 끝날 수 있음           │
  │ → 댕글링 참조 위험!                                  │
  │ → Rust: "소유권을 통째로 넘기세요" (move)            │
  └──────────────────────────────────────────────────────┘
*/

fn lesson2_move_closure() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 2: move 클로저로 데이터 넘기기");
    println!("═══════════════════════════════════════════");

    let names = vec!["철수", "영희", "민수"];

    // move: names 의 소유권을 스레드로 이동
    let handle = thread::spawn(move || {
        println!("    스레드에서 받은 이름들: {:?}", names);
    });
    // println!("{:?}", names);  // ← 컴파일 에러! names 는 move 됨

    handle.join().unwrap();

    // ── 여러 스레드에 각각 다른 데이터 ──
    let mut handles = vec![];
    for i in 0..5 {
        let handle = thread::spawn(move || {
            // i 는 Copy 타입이라 자동 복사됨
            println!("    스레드 {} 시작", i);
        });
        handles.push(handle);
    }

    for h in handles {
        h.join().unwrap();
    }
    println!("  모든 스레드 완료!");
    println!();
}

// =====================================================================
// 레슨 3 — 채널 (Channel): 스레드 간 메시지 전달
// =====================================================================
/*
★ 채널 = 스레드 사이의 우편함

  비유: 편지 주고받기
  ┌───────────────────────────────────────────────────┐
  │ 보내는 쪽 (tx)  ──────────▶  받는 쪽 (rx)        │
  │ (transmitter)     채널      (receiver)            │
  │                                                   │
  │ tx.send("안녕")  ──────▶  rx.recv() → "안녕"     │
  └───────────────────────────────────────────────────┘

★ mpsc = Multiple Producer, Single Consumer
  → 보내는 쪽은 여러 개 (clone 가능)
  → 받는 쪽은 하나만

★ 소유권: send() 는 데이터의 소유권을 넘김!
  → 보낸 후에는 원래 스레드에서 사용 불가
*/

fn lesson3_channels() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 3: 채널 (Channel)");
    println!("═══════════════════════════════════════════");

    // ── 기본 채널 ──
    let (tx, rx) = mpsc::channel();

    thread::spawn(move || {
        let msg = String::from("안녕하세요, 메인 스레드!");
        tx.send(msg).unwrap();
        // println!("{}", msg);  // ← 컴파일 에러! msg 는 send 로 소유권 이동
    });

    let received = rx.recv().unwrap();  // 메시지가 올 때까지 대기
    println!("  받은 메시지: {}", received);

    // ── 여러 메시지 보내기 ──
    let (tx2, rx2) = mpsc::channel();

    thread::spawn(move || {
        let messages = vec!["하나", "둘", "셋", "넷"];
        for msg in messages {
            tx2.send(msg).unwrap();
            thread::sleep(Duration::from_millis(10));
        }
    });

    // rx2 를 이터레이터로 사용 (채널이 닫힐 때까지 수신)
    print!("  순서대로 수신: ");
    for msg in rx2 {
        print!("{} ", msg);
    }
    println!();

    // ── 여러 송신자 (Multiple Producers) ──
    let (tx3, rx3) = mpsc::channel();
    let tx3_clone = tx3.clone();

    thread::spawn(move || {
        tx3.send("A팀에서 보냄").unwrap();
    });
    thread::spawn(move || {
        tx3_clone.send("B팀에서 보냄").unwrap();
    });

    for _ in 0..2 {
        println!("  다중 송신: {}", rx3.recv().unwrap());
    }
    println!();
}

// =====================================================================
// 레슨 4 — Mutex<T>: 공유 데이터 보호
// =====================================================================
/*
★ Mutex = 한 번에 하나의 스레드만 접근할 수 있는 잠금

  비유: 화장실 문 잠금
  ┌──────────────────────────────────────────────────────┐
  │ 화장실(데이터) 에 들어가려면 문을 잠그고(lock)       │
  │ 나올 때 문을 열어야(unlock) 다음 사람이 들어감       │
  │                                                      │
  │ Rust 에서는 lock() 의 반환값이 스코프를 벗어나면     │
  │ 자동으로 잠금 해제! (Drop 트레이트)                  │
  └──────────────────────────────────────────────────────┘

★ Mutex<T> 사용법
  1. lock() 으로 잠금 획득 → MutexGuard 반환
  2. MutexGuard 를 통해 데이터 접근/수정
  3. MutexGuard 가 스코프를 벗어나면 자동 잠금 해제

★ 주의: 단일 스레드에서만 Mutex 를 사용하면 의미 없음!
  → 여러 스레드에서 같은 데이터를 쓸 때 필요
*/

fn lesson4_mutex() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 4: Mutex<T>");
    println!("═══════════════════════════════════════════");

    // ── 기본 Mutex 사용 ──
    let data = Mutex::new(0);

    {
        let mut num = data.lock().unwrap();  // 잠금 획득
        *num = 42;
        // lock 해제는 이 블록이 끝날 때 자동!
    }

    println!("  Mutex 값: {:?}", data.lock().unwrap());

    // ── 단일 스레드 Mutex 예시 ──
    let counter = Mutex::new(vec![]);
    {
        let mut list = counter.lock().unwrap();
        list.push("항목1");
        list.push("항목2");
    }
    println!("  Mutex 리스트: {:?}", counter.lock().unwrap());
    println!();
}

// =====================================================================
// 레슨 5 — Arc<Mutex<T>>: 여러 스레드에서 공유
// =====================================================================
/*
★ Arc = Atomic Reference Counted (원자적 참조 카운팅)
  → Rc<T> 의 스레드 안전 버전
  → 여러 스레드에서 같은 데이터의 소유권을 공유

  ┌──────────────────────────────────────────────────────┐
  │ Rc<T>  → 단일 스레드 전용 (Send 아님!)              │
  │ Arc<T> → 여러 스레드에서 안전하게 공유               │
  │                                                      │
  │ Arc<Mutex<T>> = 여러 스레드가 안전하게 수정 가능!    │
  └──────────────────────────────────────────────────────┘

  비유:
  ┌──────────────────────────────────────────────────────┐
  │ Arc  = 여러 사람이 같은 금고를 가리키는 열쇠 복사본  │
  │ Mutex = 금고의 잠금 장치                             │
  │ 열쇠(Arc)로 금고를 찾고, 잠금(Mutex)으로 안전 접근  │
  └──────────────────────────────────────────────────────┘
*/

fn lesson5_arc_mutex() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 5: Arc<Mutex<T>>");
    println!("═══════════════════════════════════════════");

    // 여러 스레드에서 카운터 증가
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for _ in 0..10 {
        let counter = Arc::clone(&counter);  // Arc 복제 (데이터 복제 아님!)
        let handle = thread::spawn(move || {
            let mut num = counter.lock().unwrap();
            *num += 1;
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("  최종 카운터: {}", *counter.lock().unwrap());

    // ── 여러 스레드에서 벡터에 추가 ──
    let results = Arc::new(Mutex::new(Vec::new()));
    let mut handles2 = vec![];

    for i in 0..5 {
        let results = Arc::clone(&results);
        let handle = thread::spawn(move || {
            let value = i * i;
            results.lock().unwrap().push(value);
        });
        handles2.push(handle);
    }

    for h in handles2 {
        h.join().unwrap();
    }

    let mut final_results = results.lock().unwrap();
    final_results.sort();
    println!("  제곱 결과: {:?}", *final_results);
    println!();
}

// =====================================================================
// 레슨 6 — Send 와 Sync: 스레드 안전성 보증
// =====================================================================
/*
★ Rust 가 동시성 버그를 컴파일 시점에 잡는 비밀!

  ┌──────────────────────────────────────────────────────────┐
  │ Send 트레이트                                            │
  │ → "이 타입의 소유권을 다른 스레드로 보낼 수 있다"       │
  │ → 대부분의 타입이 Send (Rc<T> 는 아님!)                │
  │                                                          │
  │ Sync 트레이트                                            │
  │ → "이 타입의 참조를 여러 스레드에서 공유할 수 있다"     │
  │ → &T 가 Send 이면 T 는 Sync                            │
  └──────────────────────────────────────────────────────────┘

  ┌───────────────────┬────────┬────────┐
  │ 타입              │ Send   │ Sync   │
  ├───────────────────┼────────┼────────┤
  │ i32, String       │  O     │  O     │
  │ Vec<T>            │  O     │  O     │
  │ Rc<T>             │  X     │  X     │
  │ Arc<T>            │  O     │  O     │
  │ Mutex<T>          │  O     │  O     │
  │ Cell<T>           │  O     │  X     │
  │ MutexGuard        │  X     │  O     │
  └───────────────────┴────────┴────────┘

★ 컴파일러가 자동으로 Send/Sync 를 확인!
  → Rc<T> 를 스레드에 넘기려고 하면 컴파일 에러!
  → Arc<T> 로 바꾸라고 알려줌!
*/

fn lesson6_send_sync() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 6: Send 와 Sync");
    println!("═══════════════════════════════════════════");

    println!("  ★ Send: 소유권을 스레드 간 이동 가능");
    println!("    → i32, String, Vec, Arc → Send O");
    println!("    → Rc → Send X (thread::spawn 불가!)");
    println!();
    println!("  ★ Sync: 참조를 여러 스레드에서 공유 가능");
    println!("    → &i32, &String → Sync O");
    println!("    → Rc, Cell → Sync X");
    println!();
    println!("  ★ 이 트레이트들은 자동 구현됩니다!");
    println!("    → 모든 필드가 Send 면 구조체도 Send");
    println!("    → Rc 필드가 하나라도 있으면 Send X");

    // ── 증명: 컴파일러가 자동으로 검사 ──
    fn assert_send<T: Send>() {}
    fn assert_sync<T: Sync>() {}

    assert_send::<String>();
    assert_sync::<i32>();
    assert_send::<Arc<Mutex<Vec<i32>>>>();
    // assert_send::<Rc<i32>>();  // ← 컴파일 에러!

    println!("  String, i32, Arc<Mutex<Vec<i32>>> → Send/Sync 확인!");
    println!();
}

// =====================================================================
// 레슨 7 — 실전 패턴: 병렬 데이터 처리
// =====================================================================

fn lesson7_parallel_processing() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 7: 병렬 데이터 처리 예제");
    println!("═══════════════════════════════════════════");

    // 학생 점수를 여러 스레드에서 동시에 처리
    let students = vec![
        ("철수", vec![80, 90, 85]),
        ("영희", vec![92, 88, 95]),
        ("민수", vec![70, 75, 68]),
        ("서연", vec![95, 100, 98]),
    ];

    let results = Arc::new(Mutex::new(Vec::new()));
    let mut handles = vec![];

    for (name, scores) in students {
        let results = Arc::clone(&results);
        let handle = thread::spawn(move || {
            // 각 스레드에서 평균 계산
            let avg: f64 = scores.iter().sum::<i32>() as f64 / scores.len() as f64;
            let grade = if avg >= 90.0 { "A" }
                       else if avg >= 80.0 { "B" }
                       else if avg >= 70.0 { "C" }
                       else { "F" };

            results.lock().unwrap().push(format!(
                "  {} → 평균 {:.1}점 → {} 등급", name, avg, grade
            ));
        });
        handles.push(handle);
    }

    for h in handles {
        h.join().unwrap();
    }

    println!("  === 성적 처리 결과 (병렬) ===");
    for line in results.lock().unwrap().iter() {
        println!("{}", line);
    }
    println!();

    // ── Rayon 소개 (외부 크레이트) ──
    println!("  ★ 더 쉬운 병렬 처리: rayon 크레이트");
    println!("    → par_iter() 로 이터레이터를 병렬화!");
    println!("    → cargo add rayon");
    println!("    예: data.par_iter().map(|x| x * 2).collect()");
    println!();
}

// =====================================================================
// 레슨 8 — 데드락과 주의사항
// =====================================================================
/*
★ 데드락 (Deadlock) = 서로의 잠금을 기다리며 영원히 멈춤

  ┌────────────────────────────────────────────────────┐
  │ 스레드 A: lock(1) 성공, lock(2) 대기...            │
  │ 스레드 B: lock(2) 성공, lock(1) 대기...            │
  │ → 둘 다 영원히 기다림! (데드락)                   │
  └────────────────────────────────────────────────────┘

★ 데드락 방지법:
  1. 항상 같은 순서로 잠금 획득
  2. 잠금 유지 시간 최소화
  3. try_lock() 사용 (실패하면 재시도)
  4. 가능하면 채널 방식 사용 (데드락 위험 낮음)
*/

fn lesson8_deadlock_prevention() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 8: 데드락 방지");
    println!("═══════════════════════════════════════════");

    println!("  ★ 데드락 방지 체크리스트:");
    println!("    1. 여러 Mutex 를 잠글 때 항상 같은 순서로!");
    println!("    2. lock() 유지 구간을 최대한 짧게!");
    println!("    3. 의심되면 try_lock() 사용!");
    println!("    4. 가능하면 채널(channel) 패턴 선호!");
    println!();

    // ── try_lock 예시 ──
    let data = Arc::new(Mutex::new(42));
    match data.try_lock() {
        Ok(guard) => println!("  try_lock 성공: {}", *guard),
        Err(_)    => println!("  try_lock 실패: 다른 곳에서 잠금 중"),
    }

    // ── 잠금 구간 최소화 예시 ──
    let shared = Arc::new(Mutex::new(Vec::new()));
    {
        // 잠금 구간을 블록으로 제한
        let mut v = shared.lock().unwrap();
        v.push(1);
        v.push(2);
        // 여기서 자동 잠금 해제
    }
    // 잠금 해제된 후 다른 작업
    println!("  잠금 구간 최소화 완료: {:?}", shared.lock().unwrap());
    println!();
}

// =====================================================================
//  main
// =====================================================================

fn main() {
    println!();
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  Rust 14단계: 동시성 (Concurrency)");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!();

    lesson1_thread_basics();
    lesson2_move_closure();
    lesson3_channels();
    lesson4_mutex();
    lesson5_arc_mutex();
    lesson6_send_sync();
    lesson7_parallel_processing();
    lesson8_deadlock_prevention();

    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  14단계 완료! 다음은 15_async_await 입니다");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
}
