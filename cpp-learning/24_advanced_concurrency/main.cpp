/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C++ 학습 24단계: 고급 동시성 프로그래밍 (Advanced Concurrency)
  ─ condition_variable, 스레드 풀, shared_mutex, atomic, 병렬 알고리즘 ─

  14단계에서 기초를 배웠다면, 이제 실전에서 필요한 고급 동시성 기법을
  학습합니다. 생산자-소비자, 스레드 풀, 락프리 프로그래밍까지!

  ╔═══════════════════════════════════════════════════════════════════╗
  ║  고급 동시성의 핵심 개념                                         ║
  ╠═══════════════════════════════════════════════════════════════════╣
  ║  1. condition_variable  - 스레드 간 이벤트 통지                  ║
  ║  2. 스레드 풀 (Thread Pool) - 스레드 재사용으로 성능 향상        ║
  ║  3. shared_mutex   - 다수 읽기 / 단일 쓰기 동시성               ║
  ║  4. 락프리 (Lock-free) - atomic으로 락 없이 동기화              ║
  ║  5. 병렬 알고리즘  - C++17 실행 정책 (execution policy)         ║
  ║  6. 동시성 패턴    - Active Object, Monitor, DCLP               ║
  ╚═══════════════════════════════════════════════════════════════════╝

  ■ 컴파일 (pthread 링크 필요 - Linux/MinGW):
    g++ -std=c++17 -Wall -pthread -o 24_concurrency main.cpp
  ■ Windows (MSVC):
    cl /EHsc /std:c++17 main.cpp

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/
#include <iostream>
#include <string>
#include <vector>
#include <queue>
#include <map>
#include <thread>
#include <mutex>
#include <shared_mutex>
#include <condition_variable>
#include <atomic>
#include <future>
#include <functional>
#include <chrono>
#include <numeric>
#include <algorithm>
#include <sstream>
#include <cassert>
#include <memory>

using namespace std;
using namespace std::chrono;

// ─── 함수 전방 선언 ─────────────────────────────────────────────────────
void lesson1_condition_variable();
void lesson2_thread_pool();
void lesson3_reader_writer();
void lesson4_lock_free();
void lesson5_parallel_algorithms();
void lesson6_concurrency_patterns();
void lesson7_practical();

/*
=============================================================================
  레슨별 출력 흐름 가이드 (대략)
=============================================================================
  lesson1 (condition_variable):
    Producer-Consumer: 생산자가 push 후 cv.notify_one
    소비자는 cv.wait 후 깨어나 처리
    → "produced 1 / consumed 1 / produced 2 / consumed 2 / ..."

  lesson2 (Thread Pool):
    enqueue 8개 작업, 4개 워커 → 병렬 실행
    각 작업 결과 future로 수집
    → 합계 / 처리 시간 출력

  lesson3 (shared_mutex):
    여러 reader 동시 접근 OK
    writer는 단독 접근. starvation 시뮬레이션

  lesson4 (Lock-Free):
    atomic<int> + compare_exchange_weak로 카운터 증가
    뮤텍스 없이 100k+ ops/sec 가능

  lesson5 (Parallel Algorithms - C++17):
    std::sort + execution::par_unseq → 멀티코어 정렬
    1M 원소 → 단일 vs 병렬 시간 비교

  lesson6 (패턴):
    Active Object, Future-Promise, Pipeline 등
    각 패턴별 짧은 데모

  lesson7 (실전):
    웹 크롤러 시뮬레이션: 큐 기반 작업 분배
    또는 데이터 처리 파이프라인 (input → transform → output)

  ※ 출력 순서는 비결정적 (인터리빙). 같은 코드도 매 실행마다 다를 수 있음.
=============================================================================
*/

int main() {
    cout << "═══════════════════════════════════════════════\n";
    cout << "  C++ 24단계 : 고급 동시성 프로그래밍\n";
    cout << "═══════════════════════════════════════════════\n\n";

    lesson1_condition_variable();
    lesson2_thread_pool();
    lesson3_reader_writer();
    lesson4_lock_free();
    lesson5_parallel_algorithms();
    lesson6_concurrency_patterns();
    lesson7_practical();

    cout << "\n═══════════════════════════════════════════════\n";
    cout << "  24단계 학습 완료! 동시성 프로그래밍 마스터!\n";
    cout << "═══════════════════════════════════════════════\n";
    return 0;
}


// =========================================================================
//  레슨 1 — condition_variable (조건 변수)
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────┐
    │  condition_variable: 스레드 간 이벤트 통지 메커니즘             │
    │                                                                 │
    │  생산자-소비자 패턴 (Producer-Consumer Pattern)                 │
    │                                                                 │
    │  ┌──────────┐  push()   ┌────────────┐  pop()   ┌──────────┐  │
    │  │ Producer │ ────────▶│   Queue    │────────▶ │ Consumer │  │
    │  │ (생산자) │  notify   │ ┌──┬──┬──┐ │  wait    │ (소비자) │  │
    │  └──────────┘  ──────▶ │ │A │B │C │ │ ◀────── └──────────┘  │
    │                         │ └──┴──┴──┘ │                        │
    │                         └────────────┘                        │
    │                                                                 │
    │  wait():        조건이 만족될 때까지 스레드를 대기              │
    │  notify_one():  대기 중인 스레드 하나를 깨움                   │
    │  notify_all():  대기 중인 모든 스레드를 깨움                   │
    │                                                                 │
    │  주의! Spurious wakeup (가짜 깨어남) 방지를 위해               │
    │  항상 조건을 람다로 체크해야 합니다.                            │
    └─────────────────────────────────────────────────────────────────┘
*/
void lesson1_condition_variable() {
    cout << "┌──────────────────────────────────────────┐\n";
    cout << "│  레슨 1 : condition_variable             │\n";
    cout << "└──────────────────────────────────────────┘\n\n";

    // ─── 1-1: 기본 wait/notify 패턴 ────────────────────────────────
    // 한 스레드가 데이터를 준비하면 다른 스레드에 통지

    {
        mutex mtx;
        condition_variable cv;
        bool data_ready = false;
        string shared_data;

        cout << "  [기본 wait/notify]\n";

        // 생산자 스레드
        thread producer([&]() {
            this_thread::sleep_for(milliseconds(100));  // 작업 시뮬레이션
            {
                lock_guard<mutex> lock(mtx);
                shared_data = "Hello from producer!";
                data_ready = true;
            }
            cv.notify_one();  // 소비자에게 통지!
        });

        // 소비자 스레드 (현재 스레드)
        {
            unique_lock<mutex> lock(mtx);
            // 조건이 참이 될 때까지 대기 (spurious wakeup 방지)
            cv.wait(lock, [&]() { return data_ready; });
            cout << "    수신한 데이터: " << shared_data << "\n";
        }

        producer.join();
        cout << "\n";
    }

    // ─── 1-2: 생산자-소비자 문제 (Bounded Buffer) ───────────────────
    /*
        ┌──────────────────────────────────────────────┐
        │  Bounded Buffer (크기 제한 큐)               │
        │                                               │
        │  Producer ──▶ [  ][  ][  ][  ][  ] ──▶ Consumer
        │                    max_size = 5               │
        │                                               │
        │  큐가 가득 찼으면: Producer는 wait            │
        │  큐가 비었으면:    Consumer는 wait            │
        └──────────────────────────────────────────────┘
    */

    {
        queue<int> buffer;
        const int MAX_SIZE = 5;
        mutex mtx;
        condition_variable cv_not_full;   // 큐가 가득 차지 않았음을 통지
        condition_variable cv_not_empty;  // 큐가 비어있지 않음을 통지
        bool done = false;

        cout << "  [생산자-소비자 (Bounded Buffer)]\n";

        // 생산자: 1~10 데이터 생산
        thread producer([&]() {
            for (int i = 1; i <= 10; ++i) {
                unique_lock<mutex> lock(mtx);
                // 큐가 가득 차면 대기
                cv_not_full.wait(lock, [&]() {
                    return buffer.size() < static_cast<size_t>(MAX_SIZE);
                });

                buffer.push(i);
                cout << "    [생산] " << i
                     << " (큐 크기: " << buffer.size() << ")\n";

                lock.unlock();
                cv_not_empty.notify_one();  // 소비자에게 "데이터 있음" 통지

                this_thread::sleep_for(milliseconds(20));  // 생산 속도 조절
            }
            // 생산 완료 통지
            {
                lock_guard<mutex> lock(mtx);
                done = true;
            }
            cv_not_empty.notify_all();
        });

        // 소비자: 데이터를 소비
        thread consumer([&]() {
            while (true) {
                unique_lock<mutex> lock(mtx);
                cv_not_empty.wait(lock, [&]() {
                    return !buffer.empty() || done;
                });

                if (buffer.empty() && done) break;  // 종료 조건

                int val = buffer.front();
                buffer.pop();
                cout << "    [소비] " << val
                     << " (큐 크기: " << buffer.size() << ")\n";

                lock.unlock();
                cv_not_full.notify_one();  // 생산자에게 "공간 있음" 통지

                this_thread::sleep_for(milliseconds(50));  // 소비 속도 조절
            }
        });

        producer.join();
        consumer.join();
        cout << "\n";
    }

    // ─── 1-3: notify_all과 여러 소비자 ──────────────────────────────
    {
        mutex mtx;
        condition_variable cv;
        bool start_signal = false;

        cout << "  [notify_all - 다수 스레드 동시 시작]\n";

        vector<thread> workers;
        for (int i = 0; i < 3; ++i) {
            workers.emplace_back([&, i]() {
                unique_lock<mutex> lock(mtx);
                cv.wait(lock, [&]() { return start_signal; });
                cout << "    워커 " << i << " 시작!\n";
            });
        }

        this_thread::sleep_for(milliseconds(100));
        {
            lock_guard<mutex> lock(mtx);
            start_signal = true;
        }
        cv.notify_all();  // 모든 워커를 동시에 깨움!

        for (auto& w : workers) w.join();
        cout << "\n";
    }
}


// =========================================================================
//  레슨 2 — 스레드 풀 (Thread Pool)
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────┐
    │  스레드 풀: 미리 생성한 스레드들이 작업 큐에서 작업을 가져감   │
    │                                                                 │
    │                  ┌─────────────────────┐                       │
    │  enqueue(task)─▶│     작업 큐 (Queue)  │                       │
    │  enqueue(task)─▶│  [T1] [T2] [T3] ... │                       │
    │                  └────────┬────────────┘                       │
    │                           │ 작업 할당                          │
    │              ┌────────────┼────────────┐                       │
    │              ▼            ▼            ▼                       │
    │         ┌────────┐  ┌────────┐  ┌────────┐                    │
    │         │Worker 0│  │Worker 1│  │Worker 2│  ← 미리 생성됨    │
    │         └────────┘  └────────┘  └────────┘                    │
    │                                                                 │
    │  장점: 스레드 생성/소멸 비용 제거, 스레드 수 제한              │
    └─────────────────────────────────────────────────────────────────┘
*/
void lesson2_thread_pool() {
    cout << "┌──────────────────────────────────────────┐\n";
    cout << "│  레슨 2 : 스레드 풀 (Thread Pool)        │\n";
    cout << "└──────────────────────────────────────────┘\n\n";

    // ─── 2-1: 간단한 스레드 풀 직접 구현 ────────────────────────────

    class ThreadPool {
    public:
        // 생성자: num_threads개의 워커 스레드 생성
        ThreadPool(size_t num_threads) : stop_(false) {
            for (size_t i = 0; i < num_threads; ++i) {
                workers_.emplace_back([this, i]() {
                    // 워커 루프: 작업이 올 때까지 대기 → 실행 → 반복
                    while (true) {
                        function<void()> task;
                        {
                            unique_lock<mutex> lock(mtx_);
                            // 작업이 있거나 종료 신호가 올 때까지 대기
                            cv_.wait(lock, [this]() {
                                return stop_ || !tasks_.empty();
                            });

                            if (stop_ && tasks_.empty()) return;

                            task = move(tasks_.front());
                            tasks_.pop();
                        }
                        task();  // 작업 실행!
                    }
                    (void)i;  // 사용하지 않는 경고 방지
                });
            }
        }

        // 작업 추가 (future로 결과를 받을 수 있게)
        template<typename F>
        auto enqueue(F&& f) -> future<decltype(f())> {
            using ReturnType = decltype(f());
            auto task = make_shared<packaged_task<ReturnType()>>(forward<F>(f));
            future<ReturnType> result = task->get_future();
            {
                lock_guard<mutex> lock(mtx_);
                tasks_.push([task]() { (*task)(); });
            }
            cv_.notify_one();
            return result;
        }

        // 소멸자: 모든 워커 정리
        ~ThreadPool() {
            {
                lock_guard<mutex> lock(mtx_);
                stop_ = true;
            }
            cv_.notify_all();
            for (auto& worker : workers_) {
                if (worker.joinable()) worker.join();
            }
        }

    private:
        vector<thread> workers_;       // 워커 스레드들
        queue<function<void()>> tasks_; // 작업 큐
        mutex mtx_;                     // 큐 보호용 뮤텍스
        condition_variable cv_;         // 작업 대기용 조건변수
        bool stop_;                     // 종료 플래그
    };

    // ─── 2-2: 스레드 풀 사용 예제 ───────────────────────────────────

    cout << "  [스레드 풀 - 기본 사용]\n";
    {
        ThreadPool pool(3);  // 워커 3개

        // 작업 제출 & future로 결과 받기
        vector<future<int>> results;
        for (int i = 0; i < 8; ++i) {
            results.push_back(pool.enqueue([i]() {
                this_thread::sleep_for(milliseconds(50));
                return i * i;  // 제곱 계산
            }));
        }

        // 결과 수집
        cout << "    작업 결과: ";
        for (auto& f : results) {
            cout << f.get() << " ";
        }
        cout << "\n\n";
    }

    // ─── 2-3: 실용 예제 - 병렬 데이터 처리 ─────────────────────────
    cout << "  [스레드 풀 - 병렬 합계 계산]\n";
    {
        ThreadPool pool(4);

        vector<int> data(1000);
        iota(data.begin(), data.end(), 1);  // 1~1000

        // 4개 청크로 분할하여 병렬 합산
        const int num_chunks = 4;
        int chunk_size = static_cast<int>(data.size()) / num_chunks;
        vector<future<long long>> chunk_sums;

        for (int c = 0; c < num_chunks; ++c) {
            int start = c * chunk_size;
            int end = (c == num_chunks - 1) ? static_cast<int>(data.size()) : start + chunk_size;

            chunk_sums.push_back(pool.enqueue([&data, start, end]() {
                long long sum = 0;
                for (int i = start; i < end; ++i) {
                    sum += data[i];
                }
                return sum;
            }));
        }

        long long total = 0;
        for (int c = 0; c < num_chunks; ++c) {
            long long partial = chunk_sums[c].get();
            cout << "    청크 " << c << " 합계: " << partial << "\n";
            total += partial;
        }
        cout << "    총 합계: " << total << " (검증: " << 1000LL * 1001 / 2 << ")\n\n";
    }
}


// =========================================================================
//  레슨 3 — Reader-Writer Lock (shared_mutex)
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────┐
    │  shared_mutex: 다수 읽기 / 단일 쓰기 패턴                     │
    │                                                                 │
    │  ┌────────┐  shared_lock    ┌──────────────┐                   │
    │  │Reader 1│ ──────────────▶│              │                   │
    │  ├────────┤  shared_lock    │   shared     │ ← 여러 Reader    │
    │  │Reader 2│ ──────────────▶│   resource   │   동시 접근 OK   │
    │  ├────────┤  shared_lock    │              │                   │
    │  │Reader 3│ ──────────────▶│              │                   │
    │  └────────┘                 └──────┬───────┘                   │
    │                                    │                           │
    │  ┌────────┐  unique_lock    ┌──────▼───────┐                   │
    │  │Writer  │ ──────────────▶│  독점 쓰기   │ ← Writer는       │
    │  └────────┘                 │  (모두 대기) │   단독 접근      │
    │                             └──────────────┘                   │
    │                                                                 │
    │  shared_lock  → 읽기 전용, 동시에 여러 스레드 가능            │
    │  unique_lock  → 쓰기 전용, 하나의 스레드만 가능               │
    └─────────────────────────────────────────────────────────────────┘
*/
void lesson3_reader_writer() {
    cout << "┌──────────────────────────────────────────┐\n";
    cout << "│  레슨 3 : Reader-Writer Lock             │\n";
    cout << "└──────────────────────────────────────────┘\n\n";

    // ─── 3-1: 스레드 안전 설정 저장소 ───────────────────────────────
    // 읽기는 자주, 쓰기는 드문 데이터에 최적

    class ThreadSafeConfig {
    public:
        // 설정 읽기 (shared_lock: 동시 읽기 허용)
        string get(const string& key) const {
            shared_lock<shared_mutex> lock(mtx_);
            auto it = data_.find(key);
            return (it != data_.end()) ? it->second : "(없음)";
        }

        // 설정 쓰기 (unique_lock: 독점 접근)
        void set(const string& key, const string& value) {
            unique_lock<shared_mutex> lock(mtx_);
            data_[key] = value;
        }

        // 모든 키 조회 (shared_lock)
        vector<string> keys() const {
            shared_lock<shared_mutex> lock(mtx_);
            vector<string> result;
            for (const auto& [k, v] : data_) {
                result.push_back(k);
            }
            return result;
        }

    private:
        mutable shared_mutex mtx_;
        map<string, string> data_;
    };

    ThreadSafeConfig config;
    config.set("host", "localhost");
    config.set("port", "8080");
    config.set("debug", "true");

    cout << "  [ThreadSafeConfig - shared_mutex]\n";

    // 여러 리더와 하나의 라이터를 동시에 실행
    vector<thread> threads;
    atomic<int> read_count{0};

    // 리더 스레드 5개
    for (int i = 0; i < 5; ++i) {
        threads.emplace_back([&config, &read_count, i]() {
            for (int j = 0; j < 3; ++j) {
                string val = config.get("host");
                read_count++;
                this_thread::sleep_for(milliseconds(10));
                (void)val; (void)i; (void)j;
            }
        });
    }

    // 라이터 스레드 1개
    threads.emplace_back([&config]() {
        this_thread::sleep_for(milliseconds(30));
        config.set("host", "192.168.1.100");
        config.set("port", "9090");
    });

    for (auto& t : threads) t.join();

    cout << "    총 읽기 횟수: " << read_count << "\n";
    cout << "    최종 host: " << config.get("host") << "\n";
    cout << "    최종 port: " << config.get("port") << "\n\n";

    // ─── 3-2: shared_mutex vs mutex 성능 비교 개념 ──────────────────
    /*
        ┌──────────────────────────────────────────────┐
        │  mutex (일반)           │  shared_mutex       │
        │                         │                     │
        │  R1 ─── R2 ─── R3 ─── │  R1 ┬ R2 ┬ R3      │
        │  (순차적 = 느림)        │  (동시 = 빠름!)    │
        │                         │                     │
        │  읽기 비율이 높을수록   │  shared_mutex가     │
        │  성능 차이가 커짐!      │  유리!              │
        └──────────────────────────────────────────────┘
    */

    cout << "  [성능 특성 요약]\n";
    cout << "    - 읽기 위주 작업: shared_mutex >> mutex\n";
    cout << "    - 쓰기 위주 작업: shared_mutex ~= mutex\n";
    cout << "    - 오버헤드: shared_mutex > mutex (약간)\n\n";
}


// =========================================================================
//  레슨 4 — 락프리 프로그래밍 기초 (Lock-Free Basics)
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────┐
    │  락프리(Lock-Free): 뮤텍스 없이 원자적 연산으로 동기화         │
    │                                                                 │
    │  atomic 연산:                                                   │
    │  ┌──────────────────┐                                          │
    │  │ load()           │ 원자적 읽기                               │
    │  │ store()          │ 원자적 쓰기                               │
    │  │ exchange()       │ 원자적 교환 (swap)                        │
    │  │ compare_exchange  │ CAS: 기대값과 같으면 교환                │
    │  │ fetch_add/sub    │ 원자적 산술 연산                          │
    │  └──────────────────┘                                          │
    │                                                                 │
    │  CAS (Compare-And-Swap) 동작 원리:                             │
    │                                                                 │
    │    expected = 현재값이라 예상하는 값                             │
    │    desired  = 바꾸고 싶은 새 값                                 │
    │                                                                 │
    │    if (변수 == expected)                                        │
    │        변수 = desired;   // 성공!                               │
    │        return true;                                             │
    │    else                                                         │
    │        expected = 변수;  // 실패, expected를 현재값으로 갱신    │
    │        return false;                                            │
    └─────────────────────────────────────────────────────────────────┘
*/
void lesson4_lock_free() {
    cout << "┌──────────────────────────────────────────┐\n";
    cout << "│  레슨 4 : 락프리 프로그래밍 기초         │\n";
    cout << "└──────────────────────────────────────────┘\n\n";

    // ─── 4-1: atomic 기본 연산 ──────────────────────────────────────

    atomic<int> counter{0};

    cout << "  [atomic 기본 연산]\n";

    // 여러 스레드에서 동시에 증가
    vector<thread> threads;
    for (int i = 0; i < 10; ++i) {
        threads.emplace_back([&counter]() {
            for (int j = 0; j < 1000; ++j) {
                counter.fetch_add(1, memory_order_relaxed);
            }
        });
    }
    for (auto& t : threads) t.join();

    cout << "    10스레드 x 1000증가 = " << counter.load() << " (기대: 10000)\n\n";

    // ─── 4-2: compare_exchange (CAS) ────────────────────────────────
    // 락프리 알고리즘의 핵심!

    cout << "  [compare_exchange_strong (CAS)]\n";

    atomic<int> value{10};

    // CAS 성공 예시
    int expected = 10;
    bool success = value.compare_exchange_strong(expected, 20);
    cout << "    CAS(expected=10, desired=20): "
         << (success ? "성공" : "실패")
         << ", value=" << value.load() << "\n";

    // CAS 실패 예시
    expected = 10;  // value는 이제 20인데, 10을 기대
    success = value.compare_exchange_strong(expected, 30);
    cout << "    CAS(expected=10, desired=30): "
         << (success ? "성공" : "실패")
         << ", expected가 " << expected << "로 갱신됨\n\n";

    // ─── 4-3: CAS 루프로 락프리 최대값 갱신 ────────────────────────
    /*
        CAS 루프 패턴:
        do {
            old_val = atomic.load();
            new_val = 계산(old_val);
        } while (!atomic.compare_exchange_weak(old_val, new_val));

        다른 스레드가 먼저 변경했으면 재시도!
    */

    cout << "  [CAS 루프 - 락프리 최대값]\n";

    atomic<int> max_value{0};
    vector<thread> max_threads;

    // 여러 스레드가 동시에 최대값을 갱신
    vector<int> test_values = {42, 17, 88, 95, 33, 71, 99, 56};

    for (int val : test_values) {
        max_threads.emplace_back([&max_value, val]() {
            int current = max_value.load();
            while (val > current) {
                // current가 아직 val보다 작으면 val로 교체 시도
                if (max_value.compare_exchange_weak(current, val)) {
                    break;  // 성공!
                }
                // 실패하면 current가 최신값으로 갱신됨 → 루프 재시도
            }
        });
    }

    for (auto& t : max_threads) t.join();
    cout << "    락프리 최대값: " << max_value.load() << " (기대: 99)\n\n";

    // ─── 4-4: atomic_flag를 이용한 스핀락 ───────────────────────────
    /*
        스핀락(Spinlock): 락을 얻을 때까지 루프(spin)하며 대기
        mutex보다 가볍지만, 대기 시간이 길면 CPU를 낭비!

        ┌──────────────────────────────────────────┐
        │  mutex:    대기 시 OS가 스레드를 sleep    │
        │  spinlock: 대기 시 busy-wait (CPU 사용)  │
        │                                           │
        │  짧은 임계 구간 → spinlock이 유리         │
        │  긴 임계 구간   → mutex가 유리            │
        └──────────────────────────────────────────┘
    */

    class SpinLock {
    public:
        void lock() {
            while (flag_.test_and_set(memory_order_acquire)) {
                // 스핀 (바쁜 대기)
                this_thread::yield();  // 다른 스레드에 양보
            }
        }
        void unlock() {
            flag_.clear(memory_order_release);
        }
    private:
        atomic_flag flag_ = ATOMIC_FLAG_INIT;
    };

    SpinLock spin;
    int shared_counter = 0;

    cout << "  [스핀락 (SpinLock)]\n";

    vector<thread> spin_threads;
    for (int i = 0; i < 4; ++i) {
        spin_threads.emplace_back([&spin, &shared_counter]() {
            for (int j = 0; j < 1000; ++j) {
                spin.lock();
                ++shared_counter;
                spin.unlock();
            }
        });
    }
    for (auto& t : spin_threads) t.join();

    cout << "    4스레드 x 1000 = " << shared_counter << " (기대: 4000)\n\n";

    // ─── 4-5: ABA 문제 설명 ────────────────────────────────────────
    /*
        ┌─────────────────────────────────────────────────────┐
        │  ABA 문제: CAS의 함정                               │
        │                                                      │
        │  스레드1:  읽기 A → (중단) → CAS(A→C) 성공!?       │
        │  스레드2:       A → B → A  (원래값으로 되돌림)       │
        │                                                      │
        │  스레드1은 값이 변경되지 않았다고 착각!             │
        │  실제로는 A→B→A로 바뀌었는데 A→C가 성공!           │
        │                                                      │
        │  해결책:                                             │
        │  1. 버전 카운터 추가 (값 + 버전번호)                │
        │  2. 해저드 포인터 (Hazard Pointer)                   │
        │  3. RCU (Read-Copy-Update)                           │
        └─────────────────────────────────────────────────────┘
    */

    cout << "  [ABA 문제 - 개념 설명]\n";
    cout << "    CAS는 '값이 같다'만 확인하지, '중간에 변경됐는지'는 모름!\n";
    cout << "    해결: 버전 카운터 사용 → {값, 버전} 쌍으로 CAS\n\n";
}


// =========================================================================
//  레슨 5 — 병렬 알고리즘 (C++17 Parallel Algorithms)
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────┐
    │  C++17 실행 정책 (Execution Policy)                            │
    │                                                                 │
    │  std::execution::seq     → 순차 실행 (기본)                    │
    │  std::execution::par     → 병렬 실행                           │
    │  std::execution::par_unseq → 병렬 + 벡터화                    │
    │                                                                 │
    │  ┌─────────────────────────────────┐                           │
    │  │ 순차 (seq):   [1][2][3][4][5]   │ ← 하나씩 처리            │
    │  │ 병렬 (par):   [1][2] [3][4] [5] │ ← 여러 코어로 분산      │
    │  └─────────────────────────────────┘                           │
    │                                                                 │
    │  주의: <execution> 헤더는 컴파일러 지원 필요                   │
    │  MSVC: 기본 지원  /  GCC: -ltbb 필요  /  Clang: 제한적        │
    │                                                                 │
    │  여기서는 수동 병렬화로 개념을 보여줍니다.                     │
    └─────────────────────────────────────────────────────────────────┘
*/
void lesson5_parallel_algorithms() {
    cout << "┌──────────────────────────────────────────┐\n";
    cout << "│  레슨 5 : 병렬 알고리즘                  │\n";
    cout << "└──────────────────────────────────────────┘\n\n";

    // ─── 5-1: 수동 병렬 for_each ────────────────────────────────────
    /*
        데이터를 청크로 나눠 각 스레드가 처리

        전체 데이터:  [1][2][3][4][5][6][7][8]
        스레드 0:     [1][2]
        스레드 1:     [3][4]
        스레드 2:     [5][6]
        스레드 3:     [7][8]
    */

    auto parallel_for_each = [](vector<int>& data,
                                 function<void(int&)> func,
                                 int num_threads = 4) {
        vector<thread> threads;
        int chunk_size = static_cast<int>(data.size()) / num_threads;

        for (int t = 0; t < num_threads; ++t) {
            int start = t * chunk_size;
            int end = (t == num_threads - 1)
                      ? static_cast<int>(data.size())
                      : start + chunk_size;

            threads.emplace_back([&data, &func, start, end]() {
                for (int i = start; i < end; ++i) {
                    func(data[i]);
                }
            });
        }

        for (auto& th : threads) th.join();
    };

    vector<int> data(20);
    iota(data.begin(), data.end(), 1);  // 1~20

    cout << "  [수동 병렬 for_each]\n";
    cout << "    원본: ";
    for (int x : data) cout << x << " ";
    cout << "\n";

    // 병렬로 각 원소를 제곱
    parallel_for_each(data, [](int& x) { x = x * x; });

    cout << "    제곱: ";
    for (int x : data) cout << x << " ";
    cout << "\n\n";

    // ─── 5-2: 수동 병렬 reduce (합산) ──────────────────────────────

    auto parallel_reduce = [](const vector<int>& data, int num_threads = 4) -> long long {
        vector<future<long long>> futures;
        int chunk_size = static_cast<int>(data.size()) / num_threads;

        for (int t = 0; t < num_threads; ++t) {
            int start = t * chunk_size;
            int end = (t == num_threads - 1)
                      ? static_cast<int>(data.size())
                      : start + chunk_size;

            futures.push_back(async(launch::async, [&data, start, end]() {
                long long sum = 0;
                for (int i = start; i < end; ++i) sum += data[i];
                return sum;
            }));
        }

        long long total = 0;
        for (auto& f : futures) total += f.get();
        return total;
    };

    vector<int> big_data(10000);
    iota(big_data.begin(), big_data.end(), 1);

    cout << "  [수동 병렬 reduce]\n";
    long long sum = parallel_reduce(big_data);
    cout << "    1~10000 합계: " << sum
         << " (검증: " << 10000LL * 10001 / 2 << ")\n\n";

    // ─── 5-3: 수동 병렬 sort 개념 ──────────────────────────────────
    /*
        병렬 정렬 전략 (Merge Sort 기반):

        ┌────────────────────────────────────┐
        │  [5, 3, 8, 1, 9, 2, 7, 4]         │
        │           ↓ 분할                   │
        │  [5,3,8,1]     [9,2,7,4]           │
        │  Thread 0       Thread 1            │
        │     ↓ sort        ↓ sort            │
        │  [1,3,5,8]     [2,4,7,9]           │
        │           ↓ merge                  │
        │  [1,2,3,4,5,7,8,9]                │
        └────────────────────────────────────┘
    */

    cout << "  [수동 병렬 sort (2-way merge)]\n";

    vector<int> sort_data = {15, 3, 42, 8, 27, 1, 99, 56, 33, 12, 77, 5};
    size_t mid = sort_data.size() / 2;

    // 두 절반을 병렬로 정렬
    auto left_future = async(launch::async, [&sort_data, mid]() {
        sort(sort_data.begin(), sort_data.begin() + mid);
    });
    auto right_future = async(launch::async, [&sort_data, mid]() {
        sort(sort_data.begin() + mid, sort_data.end());
    });

    left_future.get();
    right_future.get();

    // 두 정렬된 절반을 병합
    inplace_merge(sort_data.begin(),
                  sort_data.begin() + mid,
                  sort_data.end());

    cout << "    정렬 결과: ";
    for (int x : sort_data) cout << x << " ";
    cout << "\n\n";
}


// =========================================================================
//  레슨 6 — 동시성 패턴
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────┐
    │  고급 동시성 디자인 패턴                                       │
    │                                                                 │
    │  1. Monitor 패턴:   mutex + condition_variable 캡슐화          │
    │  2. Active Object:  비동기 메서드 호출을 큐에 저장             │
    │  3. DCLP:           Double-Checked Locking Pattern             │
    └─────────────────────────────────────────────────────────────────┘
*/
void lesson6_concurrency_patterns() {
    cout << "┌──────────────────────────────────────────┐\n";
    cout << "│  레슨 6 : 동시성 패턴                    │\n";
    cout << "└──────────────────────────────────────────┘\n\n";

    // ─── 6-1: Monitor 패턴 ─────────────────────────────────────────
    /*
        Monitor: 동기화를 내부에 캡슐화하여 외부에서 락을 직접 다루지 않게 함

        ┌──────────────────────────────────┐
        │  Monitor (BoundedQueue)          │
        │  ┌────────────────────────────┐  │
        │  │  mutex + condition_variable│  │
        │  │  (외부에 노출하지 않음)    │  │
        │  ├────────────────────────────┤  │
        │  │  push(item)  → 자동 동기화│  │
        │  │  pop()       → 자동 동기화│  │
        │  └────────────────────────────┘  │
        └──────────────────────────────────┘
    */

    class BoundedQueue {
    public:
        BoundedQueue(size_t capacity) : capacity_(capacity) {}

        void push(int item) {
            unique_lock<mutex> lock(mtx_);
            cv_not_full_.wait(lock, [this]() {
                return queue_.size() < capacity_;
            });
            queue_.push(item);
            cv_not_empty_.notify_one();
        }

        int pop() {
            unique_lock<mutex> lock(mtx_);
            cv_not_empty_.wait(lock, [this]() {
                return !queue_.empty();
            });
            int item = queue_.front();
            queue_.pop();
            cv_not_full_.notify_one();
            return item;
        }

        size_t size() const {
            lock_guard<mutex> lock(mtx_);
            return queue_.size();
        }

    private:
        queue<int> queue_;
        size_t capacity_;
        mutable mutex mtx_;
        condition_variable cv_not_full_;
        condition_variable cv_not_empty_;
    };

    cout << "  [Monitor 패턴 - BoundedQueue]\n";
    {
        BoundedQueue bq(3);

        thread producer([&bq]() {
            for (int i = 1; i <= 6; ++i) {
                bq.push(i);
                cout << "    생산: " << i << "\n";
            }
        });

        thread consumer([&bq]() {
            for (int i = 0; i < 6; ++i) {
                this_thread::sleep_for(milliseconds(30));
                int val = bq.pop();
                cout << "    소비: " << val << "\n";
            }
        });

        producer.join();
        consumer.join();
    }
    cout << "\n";

    // ─── 6-2: Active Object 패턴 ───────────────────────────────────
    /*
        Active Object: 메서드 호출을 비동기적으로 처리
        내부에 전용 스레드와 작업 큐를 가짐

        ┌──────────┐  request   ┌───────────────────────┐
        │  Client  │ ─────────▶│  Active Object        │
        │          │  (비동기)  │  ┌──────────────────┐ │
        │          │           │  │  작업 큐          │ │
        │          │ ◀─────── │  │  [t1][t2][t3]    │ │
        │          │  future   │  └────────┬─────────┘ │
        └──────────┘           │           │ 전용 스레드│
                                │  ┌────────▼─────────┐ │
                                │  │  실행 스레드     │ │
                                │  └──────────────────┘ │
                                └───────────────────────┘
    */

    class ActiveObject {
    public:
        ActiveObject() : stop_(false) {
            worker_ = thread([this]() {
                while (true) {
                    function<void()> task;
                    {
                        unique_lock<mutex> lock(mtx_);
                        cv_.wait(lock, [this]() {
                            return stop_ || !tasks_.empty();
                        });
                        if (stop_ && tasks_.empty()) return;
                        task = move(tasks_.front());
                        tasks_.pop();
                    }
                    task();
                }
            });
        }

        // 비동기 작업 제출 - future로 결과를 받음
        template<typename F>
        auto submit(F&& f) -> future<decltype(f())> {
            using ReturnType = decltype(f());
            auto task = make_shared<packaged_task<ReturnType()>>(forward<F>(f));
            auto result = task->get_future();
            {
                lock_guard<mutex> lock(mtx_);
                tasks_.push([task]() { (*task)(); });
            }
            cv_.notify_one();
            return result;
        }

        ~ActiveObject() {
            {
                lock_guard<mutex> lock(mtx_);
                stop_ = true;
            }
            cv_.notify_one();
            if (worker_.joinable()) worker_.join();
        }

    private:
        thread worker_;
        queue<function<void()>> tasks_;
        mutex mtx_;
        condition_variable cv_;
        bool stop_;
    };

    cout << "  [Active Object 패턴]\n";
    {
        ActiveObject ao;

        auto f1 = ao.submit([]() { return 10 + 20; });
        auto f2 = ao.submit([]() { return string("Hello Active!"); });
        auto f3 = ao.submit([]() {
            int sum = 0;
            for (int i = 1; i <= 100; ++i) sum += i;
            return sum;
        });

        cout << "    결과1: " << f1.get() << "\n";
        cout << "    결과2: " << f2.get() << "\n";
        cout << "    결과3: " << f3.get() << "\n";
    }
    cout << "\n";

    // ─── 6-3: Double-Checked Locking Pattern (DCLP) ────────────────
    /*
        싱글턴 생성 시 불필요한 락 획득을 방지하는 패턴

        일반적 방법:
          lock();           ← 매번 락! (비효율)
          if (!instance) instance = new T;
          unlock();

        DCLP:
          if (!instance) {     ← 1차 체크 (락 없이)
              lock();
              if (!instance) { ← 2차 체크 (락 안에서)
                  instance = new T;
              }
              unlock();
          }
          return instance;    ← 이미 생성된 경우 락 없이 반환

        C++11: std::call_once가 더 안전하고 간편!
    */

    class Singleton {
    public:
        static Singleton& instance() {
            // C++11 이후: static 지역 변수는 스레드 안전!
            // 이것이 가장 권장되는 싱글턴 패턴 (Meyer's Singleton)
            static Singleton inst;
            return inst;
        }
        void greet() const { cout << "    Singleton 인스턴스 인사!\n"; }

    private:
        Singleton() = default;
    };

    // std::call_once를 이용한 대안
    static once_flag init_flag;
    static shared_ptr<string> resource;

    auto get_resource = [&]() -> shared_ptr<string> {
        call_once(init_flag, []() {
            resource = make_shared<string>("초기화된 리소스");
        });
        return resource;
    };

    cout << "  [DCLP / call_once / Meyer's Singleton]\n";
    Singleton::instance().greet();

    // 여러 스레드에서 동시에 초기화 시도
    vector<thread> init_threads;
    for (int i = 0; i < 3; ++i) {
        init_threads.emplace_back([&get_resource, i]() {
            auto r = get_resource();
            cout << "    스레드 " << i << ": " << *r << "\n";
        });
    }
    for (auto& t : init_threads) t.join();
    cout << "\n";
}


// =========================================================================
//  레슨 7 — 실전 종합
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────┐
    │  실전 프로젝트                                                  │
    │                                                                 │
    │  1. 멀티스레드 로그 시스템                                      │
    │  2. 동시 다운로더 시뮬레이션                                    │
    │                                                                 │
    │  ┌──────────┐                                                   │
    │  │Thread 1  │──log("...")──┐                                   │
    │  ├──────────┤              │    ┌──────────────┐               │
    │  │Thread 2  │──log("...")──┼──▶│   Logger     │──▶ 출력      │
    │  ├──────────┤              │    │ (전용 스레드) │               │
    │  │Thread 3  │──log("...")──┘    └──────────────┘               │
    │  └──────────┘                                                   │
    └─────────────────────────────────────────────────────────────────┘
*/
void lesson7_practical() {
    cout << "┌──────────────────────────────────────────┐\n";
    cout << "│  레슨 7 : 실전 종합                      │\n";
    cout << "└──────────────────────────────────────────┘\n\n";

    // ─── 7-1: 멀티스레드 로그 시스템 ────────────────────────────────
    /*
        요구사항:
        - 여러 스레드에서 동시에 로그를 기록
        - 로그 순서 보장 (타임스탬프 기반)
        - 전용 출력 스레드로 I/O 병목 해소

        ┌─────────┐     ┌──────────────────┐     ┌─────────┐
        │Thread 0 │────▶│                  │     │         │
        │Thread 1 │────▶│  Log Queue       │────▶│ Console │
        │Thread 2 │────▶│  (thread-safe)   │     │ Output  │
        │  ...    │────▶│                  │     │         │
        └─────────┘     └──────────────────┘     └─────────┘
    */

    class AsyncLogger {
    public:
        enum class Level { INFO, WARN, ERR };

        AsyncLogger() : stop_(false) {
            writer_ = thread([this]() {
                while (true) {
                    string msg;
                    {
                        unique_lock<mutex> lock(mtx_);
                        cv_.wait(lock, [this]() {
                            return stop_ || !buffer_.empty();
                        });
                        if (stop_ && buffer_.empty()) return;
                        msg = move(buffer_.front());
                        buffer_.pop();
                    }
                    // 콘솔 출력 (실제로는 파일에 기록)
                    cout << msg;
                }
            });
        }

        void log(Level level, const string& message) {
            auto now = steady_clock::now();
            auto ms = duration_cast<milliseconds>(now.time_since_epoch()).count() % 10000;

            string level_str;
            switch (level) {
                case Level::INFO: level_str = "INFO"; break;
                case Level::WARN: level_str = "WARN"; break;
                case Level::ERR:  level_str = "ERR "; break;
            }

            ostringstream oss;
            oss << "    [" << ms << "ms][" << level_str << "] "
                << message << "\n";

            {
                lock_guard<mutex> lock(mtx_);
                buffer_.push(oss.str());
            }
            cv_.notify_one();
        }

        void shutdown() {
            {
                lock_guard<mutex> lock(mtx_);
                stop_ = true;
            }
            cv_.notify_one();
            if (writer_.joinable()) writer_.join();
        }

        ~AsyncLogger() {
            if (!stop_) shutdown();
        }

    private:
        queue<string> buffer_;
        mutex mtx_;
        condition_variable cv_;
        thread writer_;
        bool stop_;
    };

    cout << "  [멀티스레드 로그 시스템]\n";
    {
        AsyncLogger logger;

        vector<thread> workers;
        for (int i = 0; i < 3; ++i) {
            workers.emplace_back([&logger, i]() {
                logger.log(AsyncLogger::Level::INFO,
                           "워커 " + to_string(i) + " 시작");
                this_thread::sleep_for(milliseconds(20 * i));
                logger.log(AsyncLogger::Level::WARN,
                           "워커 " + to_string(i) + " 처리 중...");
                this_thread::sleep_for(milliseconds(10));
                logger.log(AsyncLogger::Level::INFO,
                           "워커 " + to_string(i) + " 완료");
            });
        }

        for (auto& w : workers) w.join();
        logger.shutdown();
    }
    cout << "\n";

    // ─── 7-2: 동시 다운로더 시뮬레이션 ─────────────────────────────
    /*
        여러 "파일"을 동시에 다운로드하는 시뮬레이션

        ┌──────────────────────────────────────────────┐
        │  다운로드 매니저                              │
        │                                               │
        │  [Thread 0] ████████░░ 80%  file_a.dat       │
        │  [Thread 1] ██████████ 100% file_b.dat ✓    │
        │  [Thread 2] ████░░░░░░ 40%  file_c.dat       │
        │  [Thread 3] ██████░░░░ 60%  file_d.dat       │
        └──────────────────────────────────────────────┘
    */

    struct DownloadTask {
        string filename;
        int size_mb;          // 파일 크기 (MB)
        atomic<int> progress{0};  // 진행률 (0~100)
        bool complete = false;
    };

    cout << "  [동시 다운로더 시뮬레이션]\n";
    {
        // 다운로드 작업 목록
        vector<shared_ptr<DownloadTask>> tasks;
        auto make_task = [](string name, int size) {
            auto t = make_shared<DownloadTask>();
            t->filename = name;
            t->size_mb = size;
            return t;
        };

        tasks.push_back(make_task("report.pdf",    50));
        tasks.push_back(make_task("video.mp4",     200));
        tasks.push_back(make_task("archive.zip",   100));
        tasks.push_back(make_task("image.png",     30));

        // 다운로드 시뮬레이션 스레드
        vector<thread> downloaders;
        mutex print_mtx;

        for (auto& task : tasks) {
            downloaders.emplace_back([&task, &print_mtx]() {
                // 크기에 비례하여 다운로드 시간 시뮬레이션
                int steps = 10;
                int delay_per_step = task->size_mb / 10;  // ms

                for (int step = 1; step <= steps; ++step) {
                    this_thread::sleep_for(milliseconds(delay_per_step));
                    task->progress = step * 10;
                }

                task->complete = true;
                lock_guard<mutex> lock(print_mtx);
                cout << "    [완료] " << task->filename
                     << " (" << task->size_mb << "MB)\n";
            });
        }

        // 진행 상황 모니터링
        bool all_done = false;
        while (!all_done) {
            this_thread::sleep_for(milliseconds(100));
            all_done = true;

            lock_guard<mutex> lock(print_mtx);
            cout << "    --- 진행 상황 ---\n";
            for (auto& task : tasks) {
                int prog = task->progress.load();
                cout << "    " << task->filename << ": ";

                // 프로그레스 바 그리기
                int bars = prog / 10;
                for (int b = 0; b < bars; ++b) cout << "#";
                for (int b = bars; b < 10; ++b) cout << ".";
                cout << " " << prog << "%";
                if (task->complete) cout << " OK";
                cout << "\n";

                if (!task->complete) all_done = false;
            }
        }

        for (auto& d : downloaders) d.join();
    }

    // ═══════════════════════════════════════════════════════════════════
    //  연습 문제 (직접 풀어보세요!)
    // ═══════════════════════════════════════════════════════════════════
    cout << "\n";
    cout << "  ┌─────────────────────────────────────────────────────┐\n";
    cout << "  │  연습 문제                                          │\n";
    cout << "  ├─────────────────────────────────────────────────────┤\n";
    cout << "  │  1. BoundedQueue를 제네릭(template)으로 만들어     │\n";
    cout << "  │     아무 타입이나 저장할 수 있게 확장하세요.       │\n";
    cout << "  │                                                     │\n";
    cout << "  │  2. 스레드 풀에 우선순위 큐(priority_queue)를      │\n";
    cout << "  │     적용하여 우선순위 기반 작업 스케줄러를          │\n";
    cout << "  │     구현하세요.                                     │\n";
    cout << "  │                                                     │\n";
    cout << "  │  3. 락프리 스택(Lock-Free Stack)을 구현하세요.     │\n";
    cout << "  │     push()와 pop()을 CAS로 구현합니다.            │\n";
    cout << "  │                                                     │\n";
    cout << "  │  4. AsyncLogger에 로그 레벨 필터링 기능을          │\n";
    cout << "  │     추가하세요. (예: WARN 이상만 출력)             │\n";
    cout << "  │                                                     │\n";
    cout << "  │  5. 다운로더에 동시 다운로드 수 제한(semaphore)을  │\n";
    cout << "  │     추가하세요. (예: 최대 2개 동시 다운로드)       │\n";
    cout << "  └─────────────────────────────────────────────────────┘\n\n";
}
