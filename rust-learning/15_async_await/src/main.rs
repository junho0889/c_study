/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Rust 학습 15단계: async 와 await
  ─ Future, async fn, .await, Poll, 미니 런타임 ─

  [학습 목표]
  1. 비동기 프로그래밍이 왜 필요한지 이해한다
  2. Future 트레이트의 구조를 안다
  3. async fn 과 .await 문법을 사용한다
  4. 직접 만든 미니 런타임으로 동작 원리를 파악한다
  5. tokio 등 런타임의 역할을 이해한다
  6. 비동기와 소유권의 관계를 안다

  ■ 실행: cargo run
  ■ 빌드: cargo build --release

  ★ 이 파일은 외부 크레이트 없이 표준 라이브러리만 사용합니다.
    실제 프로젝트에서는 tokio 또는 async-std 를 사용하세요.

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll, RawWaker, RawWakerVTable, Waker};

// =====================================================================
// 레슨 1 — 비동기가 왜 필요한가?
// =====================================================================
/*
★ 동기(Synchronous) vs 비동기(Asynchronous)

  비유: 카페에서 주문하기
  ┌────────────────────────────────────────────────────────┐
  │ 동기 = 줄 서서 기다리기                                │
  │   → 커피가 나올 때까지 그 자리에서 꼼짝 못 함         │
  │   → 100명이 주문하면 99명이 기다림                    │
  │                                                        │
  │ 비동기 = 진동벨 받고 자리에서 다른 일 하기             │
  │   → 커피가 준비되면 벨이 울림                          │
  │   → 기다리는 동안 책 읽기, 채팅 등 다른 일 가능       │
  └────────────────────────────────────────────────────────┘

★ 스레드 vs 비동기

  ┌──────────────┬──────────────────────────────────────────┐
  │ 스레드       │ OS 가 관리, 무겁다 (스택 메모리 큼)      │
  │              │ CPU 집중 작업에 적합                     │
  │              │ 수천 개 만들면 리소스 부담               │
  ├──────────────┼──────────────────────────────────────────┤
  │ 비동기       │ 런타임이 관리, 가볍다                    │
  │              │ I/O 대기가 많은 작업에 적합              │
  │              │ 수만~수십만 개의 태스크 가능             │
  │              │ 웹서버, DB 쿼리, API 호출 등             │
  └──────────────┴──────────────────────────────────────────┘
*/

fn lesson1_why_async() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 1: 비동기가 왜 필요한가?");
    println!("═══════════════════════════════════════════");

    println!("  동기 코드:");
    println!("    파일 읽기... (5초 기다림)");
    println!("    DB 조회...  (3초 기다림)");
    println!("    → 총 8초 (순차 실행)");
    println!();
    println!("  비동기 코드:");
    println!("    파일 읽기 시작 + DB 조회 시작 (동시에!)");
    println!("    → 총 5초 (가장 느린 작업 시간만큼)");
    println!();
    println!("  ★ I/O 대기가 많은 프로그램에서 큰 성능 향상!");
    println!();
}

// =====================================================================
// 레슨 2 — Future 트레이트: 비동기의 핵심
// =====================================================================
/*
★ Future = "아직 안 끝났지만, 나중에 결과를 줄 약속"

  trait Future {
      type Output;                                      // 최종 결과 타입
      fn poll(self: Pin<&mut Self>, cx: &mut Context)  // 진행 상태 확인
          -> Poll<Self::Output>;
  }

  Poll 의 두 가지 상태:
  ┌──────────────────────────────────────────────────────┐
  │ Poll::Ready(value)  → 작업 완료! 결과를 가져가세요   │
  │ Poll::Pending       → 아직 안 끝났어요, 나중에 다시 │
  └──────────────────────────────────────────────────────┘

  비유: 진동벨
  ┌────────────────────────────────────────────────────────┐
  │ poll() = "제 주문 됐나요?" 확인                       │
  │ Pending = "아직이요, 벨 울리면 와주세요"              │
  │ Ready   = "네! 여기 커피요!"                          │
  └────────────────────────────────────────────────────────┘

★ Pin 이란?
  → Future 가 메모리에서 움직이지 않도록 고정
  → 자기 참조(self-referential) 구조체의 안전을 위해
  → 지금은 "Future 에 필요한 안전 장치" 정도로 이해!
*/

// ── 직접 만드는 Future: 한 번 Pending 후 Ready ──
struct YieldOnce {
    yielded: bool,
    label: &'static str,
}

impl Future for YieldOnce {
    type Output = &'static str;

    fn poll(mut self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<Self::Output> {
        if self.yielded {
            // 두 번째 poll → 결과 준비됨!
            Poll::Ready(self.label)
        } else {
            // 첫 번째 poll → "아직이요"
            self.yielded = true;
            Poll::Pending
        }
    }
}

fn lesson2_future_trait() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 2: Future 트레이트");
    println!("═══════════════════════════════════════════");

    println!("  Future 의 생명주기:");
    println!("    1. async fn 호출 → Future 생성 (아직 실행 안 됨!)");
    println!("    2. 런타임이 poll() 호출 → Pending / Ready");
    println!("    3. Pending 이면 나중에 다시 poll()");
    println!("    4. Ready 이면 결과 수확!");
    println!();
    println!("  ★ 핵심: async fn 을 호출해도 바로 실행되지 않습니다!");
    println!("    → Future 를 반환할 뿐");
    println!("    → .await 또는 런타임이 poll 해야 실행됩니다");
    println!();
}

// =====================================================================
// 레슨 3 — 미니 런타임 만들기
// =====================================================================
/*
★ 런타임(executor) = Future 를 poll 해주는 엔진

  실제 런타임(tokio 등) 은 복잡하지만,
  최소 원리를 이해하기 위해 미니 런타임을 만들어 봅시다!

  ┌──────────────────────────────────────────────────────┐
  │ block_on(future):                                    │
  │   loop {                                             │
  │       match future.poll() {                          │
  │           Ready(value) → return value                │
  │           Pending → (실제론 다른 일, 여기선 재시도)  │
  │       }                                              │
  │   }                                                  │
  └──────────────────────────────────────────────────────┘
*/

// ── 아무것도 하지 않는 Waker (최소 구현) ──
fn create_noop_waker() -> Waker {
    fn clone(_: *const ()) -> RawWaker {
        RawWaker::new(std::ptr::null(), &VTABLE)
    }
    fn wake(_: *const ()) {}
    fn wake_by_ref(_: *const ()) {}
    fn drop(_: *const ()) {}

    static VTABLE: RawWakerVTable = RawWakerVTable::new(clone, wake, wake_by_ref, drop);
    let raw = RawWaker::new(std::ptr::null(), &VTABLE);
    unsafe { Waker::from_raw(raw) }
}

// ── 미니 런타임: Future 를 끝까지 실행 ──
fn block_on<F: Future>(future: F) -> F::Output {
    let waker = create_noop_waker();
    let mut cx = Context::from_waker(&waker);
    let mut future = Box::pin(future);

    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return value,
            Poll::Pending => {
                // 실제 런타임은 여기서 다른 태스크로 전환
                // 우리는 바로 다시 시도
            }
        }
    }
}

fn lesson3_mini_runtime() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 3: 미니 런타임");
    println!("═══════════════════════════════════════════");

    // YieldOnce: 첫 poll 은 Pending, 두 번째 poll 은 Ready
    let result = block_on(YieldOnce {
        yielded: false,
        label: "첫 번째 Future 완료!",
    });
    println!("  {}", result);
    println!();
}

// =====================================================================
// 레슨 4 — async fn 과 .await
// =====================================================================
/*
★ async fn = Future 를 반환하는 함수를 쉽게 작성

  ┌──────────────────────────────────────────────────────┐
  │ async fn greet() -> String {                         │
  │     "안녕".to_string()                               │
  │ }                                                    │
  │                                                      │
  │ 위 코드는 컴파일러가 이렇게 변환합니다:             │
  │ fn greet() -> impl Future<Output = String> {         │
  │     // 상태 머신으로 변환                            │
  │ }                                                    │
  └──────────────────────────────────────────────────────┘

★ .await = "이 Future 가 끝날 때까지 여기서 양보"
  → 현재 태스크를 일시 중지하고
  → 런타임이 다른 태스크를 실행할 수 있게 함
  → Future 가 Ready 되면 이어서 진행

  ★ .await 는 async fn 안에서만 사용 가능!
*/

async fn prepare_bread() -> &'static str {
    YieldOnce { yielded: false, label: "빵 굽기 완료" }.await
}

async fn pour_milk() -> &'static str {
    YieldOnce { yielded: false, label: "우유 따르기 완료" }.await
}

async fn make_breakfast() -> Vec<&'static str> {
    // .await 로 순차 실행
    let bread = prepare_bread().await;
    let milk = pour_milk().await;
    vec![bread, milk]
}

fn lesson4_async_await() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 4: async fn 과 .await");
    println!("═══════════════════════════════════════════");

    let breakfast = block_on(make_breakfast());
    for step in &breakfast {
        println!("  {}", step);
    }

    // async 블록도 가능
    let result = block_on(async {
        let a = 10;
        let b = 20;
        a + b
    });
    println!("  async 블록 결과: {}", result);
    println!();
}

// =====================================================================
// 레슨 5 — async 와 소유권
// =====================================================================
/*
★ async 에서 소유권은 더 까다로워집니다!

  ┌──────────────────────────────────────────────────────────┐
  │ 이유: async fn 은 상태 머신으로 변환됨                   │
  │ → .await 지점마다 "여기까지의 상태"를 저장해야 함       │
  │ → 참조가 .await 를 넘으면 라이프타임 문제 발생!        │
  └──────────────────────────────────────────────────────────┘

  ★ 규칙:
  1. .await 를 넘기는 변수는 소유(owned) 타입이어야 안전
  2. 참조(&T) 는 .await 전에 사용 완료해야 함
  3. 스레드로 보내려면 Send 여야 함
*/

async fn process_data(data: String) -> usize {
    // data 의 소유권은 이 async fn 이 가짐
    // .await 를 넘어도 안전!
    let step1 = YieldOnce {
        yielded: false,
        label: "처리 중...",
    }.await;
    println!("    {}", step1);
    data.len()  // data 는 여기까지 살아있음
}

fn lesson5_async_ownership() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 5: async 와 소유권");
    println!("═══════════════════════════════════════════");

    let data = String::from("안녕하세요, 비동기 세계!");
    let len = block_on(process_data(data));
    // println!("{}", data);  // ← 컴파일 에러! data 는 move 됨
    println!("  데이터 길이: {} 바이트", len);

    println!();
    println!("  ★ async 소유권 규칙:");
    println!("    → String, Vec 등 소유 타입을 전달하면 안전");
    println!("    → &T 참조는 .await 를 넘기지 않도록 주의");
    println!("    → 필요하면 .clone() 후 전달");
    println!();
}

// =====================================================================
// 레슨 6 — 실제 런타임: tokio 소개
// =====================================================================
/*
★ 실제 프로젝트에서는 tokio 를 사용합니다

  Cargo.toml:
  ┌──────────────────────────────────────────────────────┐
  │ [dependencies]                                       │
  │ tokio = { version = "1", features = ["full"] }       │
  └──────────────────────────────────────────────────────┘

  코드:
  ┌──────────────────────────────────────────────────────┐
  │ #[tokio::main]                                       │
  │ async fn main() {                                    │
  │     let result = do_something().await;               │
  │     println!("{}", result);                          │
  │ }                                                    │
  └──────────────────────────────────────────────────────┘

★ tokio 주요 기능:
  ┌─────────────────────┬────────────────────────────────┐
  │ tokio::spawn        │ 비동기 태스크 생성             │
  │ tokio::join!        │ 여러 Future 동시 실행          │
  │ tokio::select!      │ 먼저 끝나는 Future 선택       │
  │ tokio::time::sleep  │ 비동기 대기                    │
  │ tokio::fs           │ 비동기 파일 I/O               │
  │ tokio::net          │ 비동기 네트워크                │
  │ tokio::sync         │ 비동기 채널, Mutex             │
  └─────────────────────┴────────────────────────────────┘

★ tokio::join! vs tokio::spawn
  ┌──────────────────────────────────────────────────────┐
  │ join!(a, b, c)  → 세 Future 를 동시에 실행          │
  │                  → 모두 끝날 때까지 기다림           │
  │                                                      │
  │ spawn(future)   → 독립적인 태스크로 분리             │
  │                  → JoinHandle 로 나중에 결과 수확    │
  └──────────────────────────────────────────────────────┘
*/

fn lesson6_tokio_intro() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 6: tokio 런타임 소개");
    println!("═══════════════════════════════════════════");

    println!("  tokio 사용 예시 (이 파일은 tokio 없이 실행):");
    println!();
    println!("    #[tokio::main]");
    println!("    async fn main() {{");
    println!("        // 두 작업을 동시에 실행");
    println!("        let (a, b) = tokio::join!(");
    println!("            fetch_data(\"url1\"),");
    println!("            fetch_data(\"url2\"),");
    println!("        );");
    println!("        println!(\"결과: {{}}, {{}}\", a, b);");
    println!("    }}");
    println!();
    println!("  ★ 핵심 정리:");
    println!("    → 이 단계에서 만든 block_on = 미니 런타임");
    println!("    → tokio = 프로덕션급 런타임 (멀티스레드, I/O, 타이머)");
    println!("    → async-std = tokio 의 대안");
    println!();
}

// =====================================================================
// 레슨 7 — 정리: 핵심 요약
// =====================================================================

fn lesson7_summary() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 7: 핵심 요약");
    println!("═══════════════════════════════════════════");

    println!("  ┌─────────────────────────────────────────────────┐");
    println!("  │ 1. async fn → Future 를 반환 (바로 실행 안 됨) │");
    println!("  │ 2. .await   → Future 완료까지 양보              │");
    println!("  │ 3. Future   → poll() 로 진행 상태 확인          │");
    println!("  │ 4. 런타임   → Future 를 poll 해주는 엔진        │");
    println!("  │ 5. tokio    → 실제 프로젝트의 표준 런타임       │");
    println!("  │ 6. 소유권   → .await 넘는 데이터는 소유 타입!   │");
    println!("  └─────────────────────────────────────────────────┘");
    println!();
}

// =====================================================================
//  main
// =====================================================================

fn main() {
    println!();
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  Rust 15단계: async 와 await");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!();

    lesson1_why_async();
    lesson2_future_trait();
    lesson3_mini_runtime();
    lesson4_async_await();
    lesson5_async_ownership();
    lesson6_tokio_intro();
    lesson7_summary();

    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  15단계 완료! 다음은 16_testing 입니다");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
}
