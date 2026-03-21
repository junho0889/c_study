/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  STL 학습 09단계: 멀티스레딩과 비동기 (Thread & Async)
  실행 방법: g++ -std=c++17 -pthread main.cpp -o main && ./main
  (Windows: g++ -std=c++17 main.cpp -o main && main)
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  스레드란?
  프로그램 안에서 동시에 여러 일을 하는 "일꾼"입니다.

  비유:
  - 싱글 스레드 = 혼자서 요리하기 (하나씩 순서대로)
  - 멀티 스레드 = 여러 명이 함께 요리 (동시에 여러 작업)
    → 빠르지만, 같은 냄비를 동시에 저으면 사고 발생!
    → 그래서 "이 냄비는 한 명만 저어!" 하는 규칙(mutex)이 필요합니다.
===============================================================================
*/

#include <iostream>
#include <thread>
#include <mutex>
#include <atomic>
#include <future>
#include <vector>
#include <string>
#include <numeric>
#include <chrono>
using namespace std;

// ┌─────────────────────────────────────────────┐
// │  레슨 1: std::thread — 일꾼 만들기            │
// └─────────────────────────────────────────────┘

void do_homework(const string& subject, int seconds) {
    cout << "  [시작] " << subject << " 숙제 시작!" << endl;
    this_thread::sleep_for(chrono::milliseconds(seconds * 100));
    cout << "  [완료] " << subject << " 숙제 끝!" << endl;
}

void lesson1_thread_basic() {
    cout << "[레슨 1] std::thread — 동시에 여러 일 하기" << endl;
    cout << endl;

    /*
      std::thread는 새로운 일꾼을 만들어서 함수를 실행시킵니다.

      중요 규칙:
      1) thread를 만들면 반드시 join() 또는 detach()를 해야 합니다.
         join()   = "일꾼이 끝날 때까지 기다림"
         detach() = "일꾼을 풀어주고 알아서 하게 함" (위험할 수 있음)
      2) join()을 안 하면 프로그램이 비정상 종료됩니다!

      비유:
        join()   = "다 했어?" 하고 기다리는 것
        detach() = "알아서 해" 하고 신경 끄는 것
    */

    cout << "  === 순차 실행 (하나씩) ===" << endl;
    auto start1 = chrono::steady_clock::now();
    do_homework("수학", 3);
    do_homework("영어", 2);
    auto end1 = chrono::steady_clock::now();
    auto ms1 = chrono::duration_cast<chrono::milliseconds>(end1 - start1).count();
    cout << "  순차 실행 시간: " << ms1 << "ms" << endl;
    cout << endl;

    cout << "  === 동시 실행 (thread) ===" << endl;
    auto start2 = chrono::steady_clock::now();
    thread t1(do_homework, "수학", 3);
    thread t2(do_homework, "영어", 2);
    t1.join();  // 수학 끝날 때까지 대기
    t2.join();  // 영어 끝날 때까지 대기
    auto end2 = chrono::steady_clock::now();
    auto ms2 = chrono::duration_cast<chrono::milliseconds>(end2 - start2).count();
    cout << "  동시 실행 시간: " << ms2 << "ms (더 빠름!)" << endl;
    cout << endl;

    // 사용 가능한 스레드 수
    cout << "  CPU 스레드 수: " << thread::hardware_concurrency() << endl;
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 2: std::mutex — 한 명만 쓸 수 있는 열쇠 │
// └─────────────────────────────────────────────┘

int unsafe_counter = 0;
int safe_counter = 0;
mutex counter_mutex;

void increment_unsafe(int times) {
    for (int i = 0; i < times; i++) {
        unsafe_counter++;  // ❌ 위험! 여러 스레드가 동시에 수정
    }
}

void increment_safe(int times) {
    for (int i = 0; i < times; i++) {
        lock_guard<mutex> lock(counter_mutex);  // ✅ 잠그고
        safe_counter++;
        // lock_guard가 스코프를 벗어나면 자동으로 풀림
    }
}

void lesson2_mutex() {
    cout << "[레슨 2] mutex — 동시 접근 방지 자물쇠" << endl;
    cout << endl;

    /*
      mutex(뮤텍스)는 "한 번에 한 스레드만 사용할 수 있는 자물쇠"입니다.

      비유: 화장실에 들어갈 때 문을 잠그는 것.
            한 명이 쓰고 있으면 다른 사람은 밖에서 기다려야 합니다.

      lock_guard는 "자동 잠금/해제"를 해 줍니다.
      비유: 호텔 카드키 — 문에 넣으면 잠기고, 빠지면 열림.
            직접 unlock()을 잊어버릴 걱정이 없습니다!
    */

    unsafe_counter = 0;
    safe_counter = 0;

    // ❌ mutex 없이 — 결과가 잘못될 수 있음
    {
        vector<thread> threads;
        for (int i = 0; i < 10; i++) {
            threads.emplace_back(increment_unsafe, 1000);
        }
        for (auto& t : threads) t.join();
    }
    cout << "  mutex 없이 (기대값 10000): " << unsafe_counter
         << (unsafe_counter == 10000 ? " (운 좋게 맞음)" : " (❌ 틀림!)") << endl;

    // ✅ mutex 사용 — 항상 정확
    {
        vector<thread> threads;
        for (int i = 0; i < 10; i++) {
            threads.emplace_back(increment_safe, 1000);
        }
        for (auto& t : threads) t.join();
    }
    cout << "  mutex 사용 (기대값 10000): " << safe_counter << " (✅ 정확!)" << endl;
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 3: std::atomic — 가벼운 동기화           │
// └─────────────────────────────────────────────┘
void lesson3_atomic() {
    cout << "[레슨 3] atomic — mutex보다 가벼운 동기화" << endl;
    cout << endl;

    /*
      atomic은 간단한 값(int, bool 등)을 스레드 안전하게 다루는 방법입니다.
      mutex보다 빠르지만, 단순한 연산(++, --, 대입)에만 쓸 수 있습니다.

      비유: mutex = 방 전체를 잠그는 것
            atomic = 사물함 하나만 잠그는 것 (더 빠름)
    */

    atomic<int> atom_counter(0);

    {
        vector<thread> threads;
        for (int i = 0; i < 10; i++) {
            threads.emplace_back([&atom_counter]() {
                for (int j = 0; j < 1000; j++) {
                    atom_counter++;  // 자동으로 안전한 증가!
                }
            });
        }
        for (auto& t : threads) t.join();
    }

    cout << "  atomic 결과 (기대값 10000): " << atom_counter << " (✅ 정확!)" << endl;

    // atomic의 다른 연산들
    atomic<int> value(10);
    value.store(20);                    // 저장
    int loaded = value.load();          // 읽기
    int old = value.exchange(30);       // 교환 (이전 값 반환)

    cout << "  store(20) → load: " << loaded << endl;
    cout << "  exchange(30) → 이전 값: " << old << ", 현재 값: " << value.load() << endl;
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 4: std::async와 std::future — 결과 받기 │
// └─────────────────────────────────────────────┘

// 오래 걸리는 계산을 시뮬레이션
long long heavy_calculation(int start, int end) {
    long long sum = 0;
    for (int i = start; i <= end; i++) {
        sum += i;
    }
    this_thread::sleep_for(chrono::milliseconds(200));  // 시간이 걸리는 척
    return sum;
}

void lesson4_async_future() {
    cout << "[레슨 4] async와 future — 비동기 작업의 결과 받기" << endl;
    cout << endl;

    /*
      std::async는 함수를 "나중에 결과를 줄게" 하며 백그라운드에서 실행합니다.
      std::future는 그 결과를 받는 "약속증서"입니다.

      비유:
        async  = 배달 주문하기 (주문하고 다른 일 할 수 있음)
        future = 배달 영수증 (이걸로 나중에 음식을 받음)
        get()  = "배달 왔나?" 하고 받기 (아직 안 왔으면 기다림)

      launch::async  = 즉시 새 스레드에서 실행
      launch::deferred = get()을 호출할 때까지 미룸
    */

    cout << "  === 비동기 분할 계산 ===" << endl;
    auto start = chrono::steady_clock::now();

    // 1~50000000 합산을 두 부분으로 나눠서 동시에 계산
    auto f1 = async(launch::async, heavy_calculation, 1, 25000000);
    auto f2 = async(launch::async, heavy_calculation, 25000001, 50000000);

    // 결과가 준비될 때까지 기다리고 합치기
    long long result = f1.get() + f2.get();

    auto end_time = chrono::steady_clock::now();
    auto ms = chrono::duration_cast<chrono::milliseconds>(end_time - start).count();

    cout << "  1부터 50000000까지의 합: " << result << endl;
    cout << "  걸린 시간: " << ms << "ms (2개가 동시에 계산됨)" << endl;
    cout << endl;

    // future의 상태 확인
    auto f3 = async(launch::async, []() {
        this_thread::sleep_for(chrono::milliseconds(100));
        return 42;
    });

    // wait_for로 "끝났나?" 확인 (기다리지 않고)
    auto status = f3.wait_for(chrono::milliseconds(0));
    if (status == future_status::ready) {
        cout << "  결과 준비됨!" << endl;
    } else {
        cout << "  아직 계산 중... (기다리겠습니다)" << endl;
    }
    cout << "  결과: " << f3.get() << endl;
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 5: 실전 예제 — 병렬 성적 처리            │
// └─────────────────────────────────────────────┘
void lesson5_practical_example() {
    cout << "[레슨 5] 실전 — 여러 반의 성적을 동시에 계산" << endl;
    cout << endl;

    /*
      시나리오: 3개 반의 평균 점수를 각각 계산합니다.
      순차로 하면 느리지만, 각 반을 별도 스레드로 계산하면 빠릅니다.
    */

    struct ClassData {
        string name;
        vector<int> scores;
    };

    vector<ClassData> classes = {
        {"1반", {92, 85, 78, 95, 88, 76, 90, 82}},
        {"2반", {88, 91, 73, 86, 95, 80, 77, 84}},
        {"3반", {79, 82, 90, 88, 75, 93, 85, 81}},
    };

    // 각 반의 평균을 비동기로 계산
    vector<future<double>> futures;
    for (const auto& cls : classes) {
        futures.push_back(async(launch::async, [&cls]() {
            this_thread::sleep_for(chrono::milliseconds(150));  // 계산 시간
            double sum = accumulate(cls.scores.begin(), cls.scores.end(), 0.0);
            return sum / cls.scores.size();
        }));
    }

    // 결과 수집
    cout << "  반별 평균 점수:" << endl;
    for (size_t i = 0; i < classes.size(); i++) {
        double avg = futures[i].get();
        cout << "    " << classes[i].name << " 평균: " << avg << "점" << endl;
    }
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 6: 정리 — 언제 무엇을 쓸까?             │
// └─────────────────────────────────────────────┘
void lesson6_summary() {
    cout << "[레슨 6] 정리 — 언제 무엇을 쓸까?" << endl;
    cout << endl;

    cout << "  ┌──────────────┬───────────────────────────────────────┐" << endl;
    cout << "  │  도구        │  언제 쓸까?                            │" << endl;
    cout << "  ├──────────────┼───────────────────────────────────────┤" << endl;
    cout << "  │  thread      │  세밀하게 스레드를 제어할 때             │" << endl;
    cout << "  │  mutex       │  공유 자원을 여러 스레드가 접근할 때      │" << endl;
    cout << "  │  lock_guard  │  mutex의 자동 잠금/해제 (기본 선택)      │" << endl;
    cout << "  │  atomic      │  간단한 카운터, 플래그 등                │" << endl;
    cout << "  │  async/future│  결과가 필요한 비동기 작업 (기본 선택!)   │" << endl;
    cout << "  └──────────────┴───────────────────────────────────────┘" << endl;
    cout << endl;
    cout << "  팁: 간단한 비동기 작업은 async부터 시작하세요!" << endl;
    cout << "       thread + mutex는 더 세밀한 제어가 필요할 때만." << endl;
    cout << endl;
}

int main() {
    cout << "============================================================" << endl;
    cout << "  STL 09단계 : thread, mutex, async, atomic" << endl;
    cout << "============================================================" << endl;
    cout << endl;

    lesson1_thread_basic();
    lesson2_mutex();
    lesson3_atomic();
    lesson4_async_future();
    lesson5_practical_example();
    lesson6_summary();

    return 0;
}
