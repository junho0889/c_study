/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C++ 학습 14단계: 멀티스레딩과 동시성
  ─ thread, mutex, async, atomic ─

  현대 CPU는 코어가 여러 개 → 여러 작업을 동시에 처리 가능!
  하지만 동시성은 매우 어려운 주제이므로 신중하게 사용해야 합니다.

  ■ 컴파일 (pthread 링크 필요 - Linux/MinGW):
    g++ -std=c++17 -Wall -pthread -o 14_thread main.cpp
  ■ Windows (MSVC):
    cl /EHsc /std:c++17 main.cpp

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/
#include <iostream>
#include <string>
#include <vector>
#include <thread>
#include <mutex>
#include <atomic>
#include <future>
#include <chrono>
#include <numeric>
using namespace std;

void lesson1_thread_basics();
void lesson2_mutex();
void lesson3_atomic();
void lesson4_async_future();
void lesson5_practical();

int main() {
    cout << "========================================\n";
    cout << "  C++ 14단계 : 멀티스레딩\n";
    cout << "========================================\n\n";

    lesson1_thread_basics();
    lesson2_mutex();
    lesson3_atomic();
    lesson4_async_future();
    lesson5_practical();

    cout << "\n14단계 학습 완료!\n";
    return 0;
}


// =========================================================================
//  레슨 1 — 스레드 기초
// =========================================================================
void lesson1_thread_basics() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 1 : 스레드 기초                │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    // ─── 스레드란? ───
    //
    //   프로세스 = 실행 중인 프로그램 전체
    //   스레드   = 프로세스 안의 실행 흐름 하나
    //
    //   비유:
    //     프로세스 = 식당  (독립된 공간)
    //     스레드   = 요리사 (같은 주방에서 동시에 일함)
    //
    //   main() 자체도 하나의 스레드 (메인 스레드)
    //
    //   ┌─ 프로세스 ───────────────────────┐
    //   │                                   │
    //   │  메인 스레드 ──→ 실행...          │
    //   │                                   │
    //   │  스레드 1 ──→ 동시에 실행...      │
    //   │                                   │
    //   │  스레드 2 ──→ 동시에 실행...      │
    //   │                                   │
    //   │  (같은 메모리를 공유!)             │
    //   └───────────────────────────────────┘

    // ── 기본 스레드 생성 ──
    auto worker = [](int id, int count) {
        for (int i = 0; i < count; i++) {
            cout << "    스레드 " << id << ": 작업 " << (i + 1) << "\n";
            this_thread::sleep_for(chrono::milliseconds(50));
        }
    };

    cout << "  ■ 스레드 생성과 join\n";
    cout << "  ─────────────────────────────────────\n";

    thread t1(worker, 1, 3);   // 스레드 생성 → 바로 실행 시작!
    thread t2(worker, 2, 3);

    // ★ join() = 스레드가 끝날 때까지 기다림
    //   join 안 하면? → 프로그램 비정상 종료! (terminate 호출)
    t1.join();
    t2.join();

    cout << "  두 스레드 모두 완료!\n\n";

    // ── detach: 스레드를 분리 (백그라운드 실행) ──
    //
    //   t.detach();  → 메인 스레드와 독립적으로 실행
    //   → 끝나는 시점을 알 수 없음, 보통 비추천
    //
    //   ★ 규칙: join() 또는 detach() 중 하나를 반드시 호출!
    //           안 하면 소멸자에서 terminate 호출됨

    // ── 하드웨어 동시성 확인 ──
    cout << "  이 컴퓨터의 코어 수: "
         << thread::hardware_concurrency() << "\n";
    cout << endl;
}


// =========================================================================
//  레슨 2 — 뮤텍스 (Mutex)
// =========================================================================
void lesson2_mutex() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 2 : 뮤텍스 (데이터 보호)       │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    // ─── 왜 뮤텍스가 필요한가? ───
    //
    //   여러 스레드가 같은 변수를 동시에 수정하면?
    //   → 데이터 경쟁(Race Condition)! → 결과가 예측 불가!
    //
    //   예: 두 스레드가 동시에 count++ 실행
    //       읽기(count=5) → 증가(6) → 쓰기
    //       읽기(count=5) → 증가(6) → 쓰기  ← 같은 값을 읽음!
    //       결과: count = 6 (7이어야 정상!)
    //
    //   ★ 해결: 뮤텍스(Mutex) = 상호 배제 (Mutual Exclusion)
    //     "한번에 하나의 스레드만 이 코드를 실행할 수 있다"

    // ── 문제: 뮤텍스 없이 동시 접근 ──
    cout << "  ■ 문제: 뮤텍스 없이 (데이터 경쟁!)\n";
    {
        int counter = 0;
        auto increment = [&counter]() {
            for (int i = 0; i < 100000; i++) {
                counter++;   // 데이터 경쟁!
            }
        };
        thread t1(increment);
        thread t2(increment);
        t1.join();
        t2.join();
        cout << "    기대값: 200000, 실제값: " << counter
             << " (다를 수 있음!)\n\n";
    }

    // ── 해결: 뮤텍스 사용 ──
    cout << "  ■ 해결: lock_guard + mutex\n";
    {
        int counter = 0;
        mutex mtx;

        auto safe_increment = [&counter, &mtx]() {
            for (int i = 0; i < 100000; i++) {
                // lock_guard = RAII 스타일 잠금
                // 생성 시 잠금, 소멸 시(스코프 끝) 자동 해제
                lock_guard<mutex> lock(mtx);
                counter++;
            }
        };
        thread t1(safe_increment);
        thread t2(safe_increment);
        t1.join();
        t2.join();
        cout << "    기대값: 200000, 실제값: " << counter << " (정확!)\n\n";
    }

    // ─── lock_guard vs unique_lock ───
    //
    //   lock_guard<mutex>   : 단순 잠금/해제 (RAII)  ← 기본 선택
    //   unique_lock<mutex>  : 유연한 잠금 (시도 잠금, 조건 변수 등)
    //   scoped_lock         : C++17, 여러 뮤텍스 동시 잠금
    //
    //   ★ 교착 상태(Deadlock) 주의!
    //     스레드A가 뮤텍스1 잠그고 뮤텍스2 기다림
    //     스레드B가 뮤텍스2 잠그고 뮤텍스1 기다림
    //     → 둘 다 영원히 기다림! (프로그램 멈춤)
    //
    //     예방: 항상 같은 순서로 잠그기, scoped_lock 사용

    cout << "  ■ 뮤텍스 요약\n";
    cout << "  ─────────────────────────────────────\n";
    cout << "  mutex              : 기본 잠금\n";
    cout << "  lock_guard<mutex>  : RAII 자동 잠금/해제 (추천)\n";
    cout << "  unique_lock<mutex> : 유연한 잠금\n";
    cout << "  scoped_lock        : 여러 뮤텍스 동시 (C++17)\n";
    cout << endl;
}


// =========================================================================
//  레슨 3 — atomic
// =========================================================================
void lesson3_atomic() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 3 : atomic (원자적 연산)        │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    // ─── atomic이란? ───
    //
    //   단순한 정수 연산(++, --, +=)은 뮤텍스 대신 atomic 사용!
    //   → 뮤텍스보다 훨씬 빠름 (하드웨어 수준 지원)
    //   → 복잡한 연산에는 여전히 뮤텍스 필요

    atomic<int> counter{0};   // 원자적 정수

    auto increment = [&counter]() {
        for (int i = 0; i < 100000; i++) {
            counter++;   // 원자적! 뮤텍스 없이도 안전!
        }
    };

    thread t1(increment);
    thread t2(increment);
    t1.join();
    t2.join();

    cout << "  atomic<int> counter = " << counter
         << " (정확히 200000!)\n";

    // ── atomic 주요 연산 ──
    cout << "\n  ■ atomic 주요 연산\n";
    cout << "  ─────────────────────────────────────\n";

    atomic<int> val{10};
    cout << "  load()       = " << val.load() << "  (값 읽기)\n";
    val.store(20);
    cout << "  store(20)    = " << val.load() << "  (값 쓰기)\n";
    int old = val.exchange(30);
    cout << "  exchange(30) → 이전값=" << old
         << ", 현재값=" << val.load() << "\n";
    val.fetch_add(5);
    cout << "  fetch_add(5) = " << val.load() << "\n";

    // ── atomic<bool>: 플래그로 자주 사용 ──
    atomic<bool> running{true};
    // running = false;  로 다른 스레드에서 중단 신호 보내기

    cout << endl;
}


// =========================================================================
//  레슨 4 — async와 future
// =========================================================================
void lesson4_async_future() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 4 : async / future             │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    // ─── async란? ───
    //
    //   "이 함수를 비동기로 실행하고, 나중에 결과를 받겠다"
    //
    //   thread보다 높은 수준의 추상화
    //   → 스레드 직접 관리 안 해도 됨
    //   → 반환값을 future로 받을 수 있음
    //
    //   비유: 배달 주문
    //     주문(async) → 배달 올 때까지 다른 일(다른 코드)
    //     → 배달 도착 확인(future.get())

    // ── 기본 사용 ──
    cout << "  ■ async + future\n";
    cout << "  ─────────────────────────────────────\n";

    auto heavy_calc = [](int n) -> long long {
        cout << "    (계산 시작: " << n << "의 합)\n";
        long long sum = 0;
        for (int i = 1; i <= n; i++) sum += i;
        this_thread::sleep_for(chrono::milliseconds(100));
        return sum;
    };

    // async로 비동기 실행 → future 반환
    future<long long> result1 = async(launch::async, heavy_calc, 1000000);
    future<long long> result2 = async(launch::async, heavy_calc, 2000000);

    cout << "    (다른 작업 수행 중...)\n";

    // get()으로 결과 대기 + 받기  (결과 나올 때까지 블록)
    long long sum1 = result1.get();
    long long sum2 = result2.get();

    cout << "    결과1: " << sum1 << "\n";
    cout << "    결과2: " << sum2 << "\n\n";

    // ── launch 정책 ──
    //
    //   launch::async    : 반드시 새 스레드에서 실행
    //   launch::deferred : get() 호출 시점에 실행 (지연 실행)
    //   기본값 (생략)     : 런타임이 판단

    // ── promise: 스레드 간 값 전달 ──
    cout << "  ■ promise + future (값 전달)\n";
    cout << "  ─────────────────────────────────────\n";

    promise<string> prom;
    future<string> fut = prom.get_future();

    thread t([&prom]() {
        this_thread::sleep_for(chrono::milliseconds(50));
        prom.set_value("스레드에서 보낸 메시지!");
    });

    cout << "    대기 중...\n";
    string msg = fut.get();
    cout << "    받은 값: " << msg << "\n";
    t.join();
    cout << endl;
}


// =========================================================================
//  레슨 5 — 실전 예제: 병렬 합산
// =========================================================================
void lesson5_practical() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 5 : 실전 — 병렬 합산           │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    // 큰 배열을 여러 스레드로 나눠 합산

    const int SIZE = 10000000;
    vector<int> data(SIZE);
    for (int i = 0; i < SIZE; i++) data[i] = 1;  // 전부 1

    int num_threads = 4;

    // ── 단일 스레드 합산 ──
    auto start = chrono::high_resolution_clock::now();
    long long single_sum = 0;
    for (int val : data) single_sum += val;
    auto end = chrono::high_resolution_clock::now();
    auto single_ms = chrono::duration_cast<chrono::milliseconds>(end - start).count();
    cout << "  단일 스레드: 합=" << single_sum
         << " (" << single_ms << "ms)\n";

    // ── 병렬 합산 ──
    start = chrono::high_resolution_clock::now();

    vector<future<long long>> futures;
    int chunk = SIZE / num_threads;

    for (int t = 0; t < num_threads; t++) {
        int begin = t * chunk;
        int end_idx = (t == num_threads - 1) ? SIZE : begin + chunk;

        futures.push_back(async(launch::async, [&data, begin, end_idx]() {
            long long sum = 0;
            for (int i = begin; i < end_idx; i++) sum += data[i];
            return sum;
        }));
    }

    long long parallel_sum = 0;
    for (auto& f : futures) parallel_sum += f.get();

    end = chrono::high_resolution_clock::now();
    auto parallel_ms = chrono::duration_cast<chrono::milliseconds>(end - start).count();
    cout << "  병렬(" << num_threads << "스레드): 합=" << parallel_sum
         << " (" << parallel_ms << "ms)\n\n";

    // ── 멀티스레딩 체크리스트 ──
    cout << "  ■ 멀티스레딩 체크리스트\n";
    cout << "  ─────────────────────────────────────\n";
    cout << "  1. 공유 데이터에 mutex 또는 atomic 사용\n";
    cout << "  2. lock_guard로 RAII 잠금 (수동 lock/unlock X)\n";
    cout << "  3. thread는 반드시 join() 또는 detach()\n";
    cout << "  4. 간단한 비동기는 async/future 사용\n";
    cout << "  5. 교착 상태 주의 (같은 순서로 잠금)\n";
    cout << "  6. 데이터 경쟁 검출: -fsanitize=thread\n";
    cout << endl;
}
