/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C++ 학습 25단계: 성능 최적화 & 프로파일링
  ─ Benchmarking, Cache, Move, Containers, Algorithms, Memory Pool, Profiling ─

  "측정하지 않으면 최적화할 수 없다." ── 도널드 크누스

  이 파일은 C++ 프로그램의 성능을 체계적으로 분석하고 개선하는
  핵심 기법을 다룹니다. 각 레슨은 실제 벤치마크 코드와 함께
  제공되므로 직접 실행하며 차이를 체감할 수 있습니다.

  ■ 컴파일:
    g++ -std=c++17 -O2 -Wall -o 25_perf main.cpp
    (최적화 비교 시: -O0, -O1, -O2, -O3, -Ofast 로 바꿔 실행)
  ■ Windows (MSVC):
    cl /EHsc /std:c++17 /O2 main.cpp

  ■ 목차:
    레슨 1 — 벤치마킹 기초           (chrono, 벤치마크 유틸)
    레슨 2 — 캐시와 메모리 레이아웃   (캐시 라인, DoD, SoA vs AoS)
    레슨 3 — 복사 회피               (RVO, const ref, move, string_view)
    레슨 4 — 컨테이너 성능 비교       (vector, list, deque, map, unordered_map)
    레슨 5 — 알고리즘 최적화          (분기예측, 루프언롤링, SIMD, 꼬리재귀)
    레슨 6 — 메모리 풀과 커스텀 할당자 (MemoryPool 구현)
    레슨 7 — 프로파일링 도구 가이드    (perf, Valgrind, VS Profiler, gprof)

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <list>
#include <deque>
#include <map>
#include <unordered_map>
#include <array>
#include <chrono>
#include <algorithm>
#include <numeric>
#include <functional>
#include <memory>
#include <cstring>
#include <cstdlib>
#include <random>
#include <cassert>
using namespace std;

// ─── 전방 선언 ───
void lesson1_benchmarking();
void lesson2_cache_memory();
void lesson3_copy_avoidance();
void lesson4_container_perf();
void lesson5_algorithm_opt();
void lesson6_memory_pool();
void lesson7_profiling_guide();

/*
=============================================================================
  레슨별 출력 흐름 가이드 (대략, 시간 값은 환경에 따라 다름)
=============================================================================
  lesson1 (벤치마킹):
    chrono::high_resolution_clock으로 측정
    1M 회 반복 → 약 5~50ms 출력

  lesson2 (캐시 효과):
    행 우선 순회 vs 열 우선 순회 (1024×1024)
    → 행 우선: 약 5ms / 열 우선: 약 50ms (10배 차이)
    cache miss 패턴 시각화

  lesson3 (Copy Avoidance):
    값 반환 vs 이동 vs 참조
    RVO 활성: 복사 0회 / NRVO: 가능한 경우만
    move(v): 이동 1회 (포인터만 교환)

  lesson4 (컨테이너):
    vector vs list vs deque 삽입/접근 비교
    vector push_back: O(amortized 1)
    list 중간 삽입: O(1) but 캐시 불리
    실제 측정: vector가 list보다 종종 빠름 (캐시 효과)

  lesson5 (알고리즘):
    O(n²) vs O(n log n) - 1M 원소에서 차이 측정
    버블 정렬: ~수십 분 / 퀵 정렬: ~100ms

  lesson6 (메모리 풀):
    new/delete 1M회: 약 100ms
    풀 alloc/free 1M회: 약 10ms (10배 빠름)
    단편화 없음

  lesson7 (프로파일링 가이드):
    perf, gprof, Valgrind/Callgrind, Tracy 사용법 안내
=============================================================================
*/

int main() {
    cout << "========================================================\n";
    cout << "  C++ 25단계 : 성능 최적화 & 프로파일링\n";
    cout << "========================================================\n\n";

    lesson1_benchmarking();
    lesson2_cache_memory();
    lesson3_copy_avoidance();
    lesson4_container_perf();
    lesson5_algorithm_opt();
    lesson6_memory_pool();
    lesson7_profiling_guide();

    cout << "\n25단계 학습 완료! 이제 여러분의 코드를 측정하고 최적화하세요.\n";
    return 0;
}


// =========================================================================
//  레슨 1 — 벤치마킹 기초
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────┐
    │  왜 벤치마킹이 중요한가?                                       │
    │                                                                 │
    │  • "감"으로 최적화하면 오히려 느려질 수 있다                    │
    │  • 컴파일러 최적화가 코드를 완전히 바꿀 수 있다                │
    │  • 반복 측정 → 통계적 유의성 확보 필요                         │
    │                                                                 │
    │  측정 도구 비교:                                                │
    │  ┌─────────────────┬────────────┬─────────────┐                │
    │  │ 방법            │ 정밀도     │ 비고        │                │
    │  ├─────────────────┼────────────┼─────────────┤                │
    │  │ clock()         │ ~15ms      │ CPU 시간    │                │
    │  │ time()          │ 1초       │ 벽시계 시간 │                │
    │  │ chrono::steady  │ ~1ns      │ ★ 권장      │                │
    │  │ rdtsc           │ 사이클     │ 비이식성    │                │
    │  └─────────────────┴────────────┴─────────────┘                │
    └─────────────────────────────────────────────────────────────────┘
*/

// ── 범용 벤치마크 유틸리티 ──
// 임의의 함수를 N회 반복 실행하고 평균 시간을 반환한다.
template<typename Func>
double benchmark_ms(Func&& func, int iterations = 100) {
    // ── warm-up: 캐시 워밍 및 JIT 안정화 ──
    for (int i = 0; i < 3; ++i) func();

    auto start = chrono::steady_clock::now();
    for (int i = 0; i < iterations; ++i) {
        func();
    }
    auto end = chrono::steady_clock::now();

    double total_ms = chrono::duration<double, milli>(end - start).count();
    return total_ms / iterations;
}

// ── 결과 출력 헬퍼 ──
void print_bench(const string& label, double ms) {
    cout << "  " << label << ": ";
    if (ms < 1.0) {
        cout << (ms * 1000.0) << " us\n";
    } else {
        cout << ms << " ms\n";
    }
}

void lesson1_benchmarking() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 1 : 벤치마킹 기초              │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    // ── chrono 기본 사용법 ──
    //
    //   steady_clock: 단조 증가하는 시계 → 벤치마크에 적합
    //   system_clock: 벽시계 → 날짜/시간 표시용
    //   high_resolution_clock: 가장 높은 정밀도 (보통 steady_clock과 동일)
    //
    //   사용 패턴:
    //     auto t1 = steady_clock::now();
    //     ... 측정 대상 코드 ...
    //     auto t2 = steady_clock::now();
    //     auto elapsed = duration_cast<microseconds>(t2 - t1);

    cout << "  [예제 1] vector push_back vs reserve + push_back\n";

    const int N = 100000;

    double no_reserve = benchmark_ms([&]() {
        vector<int> v;
        for (int i = 0; i < N; ++i) v.push_back(i);
    }, 50);

    double with_reserve = benchmark_ms([&]() {
        vector<int> v;
        v.reserve(N);
        for (int i = 0; i < N; ++i) v.push_back(i);
    }, 50);

    print_bench("reserve 없이", no_reserve);
    print_bench("reserve 사용", with_reserve);
    cout << "  → reserve가 약 " << (no_reserve / with_reserve)
         << "배 빠름\n\n";

    // ── 벤치마킹 주의사항 ──
    //
    //  1. 컴파일러가 사용되지 않는 결과를 제거할 수 있음 (Dead Code Elimination)
    //     → volatile 또는 결과를 stdout으로 출력해서 방지
    //  2. -O0으로 측정하면 실제 성능과 다름 → -O2 이상으로 측정
    //  3. 첫 실행은 캐시 cold → warm-up 반복 필요
    //  4. 다른 프로세스의 영향 → 여러 번 반복 후 중앙값 사용

    cout << "  [벤치마킹 팁]\n";
    cout << "  • volatile 싱크로 Dead Code Elimination 방지\n";
    cout << "  • warm-up 3회 이상 실행 후 측정 시작\n";
    cout << "  • 최소 50~100회 반복하여 평균값 사용\n";
    cout << "  • -O2 이상으로 컴파일하여 측정\n\n";
}


// =========================================================================
//  레슨 2 — 캐시와 메모리 레이아웃
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────┐
    │  CPU 캐시 계층 구조                                            │
    │                                                                 │
    │   CPU 코어                                                      │
    │   ┌──────┐                                                      │
    │   │ 레지 │ ← ~0.3ns (가장 빠름)                                │
    │   │ 스터 │                                                      │
    │   └──┬───┘                                                      │
    │      ↓                                                          │
    │   ┌──────┐                                                      │
    │   │  L1  │ ← ~1ns,  32~64 KB (코어 전용)                      │
    │   │캐시  │                                                      │
    │   └──┬───┘                                                      │
    │      ↓                                                          │
    │   ┌──────┐                                                      │
    │   │  L2  │ ← ~4ns,  256 KB~1 MB (코어 전용 또는 공유)         │
    │   │캐시  │                                                      │
    │   └──┬───┘                                                      │
    │      ↓                                                          │
    │   ┌──────┐                                                      │
    │   │  L3  │ ← ~10ns, 8~64 MB (모든 코어 공유)                  │
    │   │캐시  │                                                      │
    │   └──┬───┘                                                      │
    │      ↓                                                          │
    │   ┌──────┐                                                      │
    │   │ RAM  │ ← ~100ns, 수 GB                                     │
    │   └──┬───┘                                                      │
    │      ↓                                                          │
    │   ┌──────┐                                                      │
    │   │ SSD  │ ← ~100,000ns (디스크)                               │
    │   └──────┘                                                      │
    │                                                                 │
    │  캐시 라인 = 보통 64 bytes                                      │
    │  → 64바이트 단위로 메모리를 가져옴                             │
    │  → 연속된 데이터가 유리 (공간적 지역성)                        │
    └─────────────────────────────────────────────────────────────────┘
*/

void lesson2_cache_memory() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 2 : 캐시와 메모리 레이아웃     │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    // ── AoS (Array of Structs) vs SoA (Struct of Arrays) ──
    //
    //  AoS (전통적 OOP 방식):
    //    struct Particle { float x, y, z, vx, vy, vz; int life; };
    //    vector<Particle> particles;   // [x,y,z,vx,vy,vz,life, x,y,z,...]
    //
    //    → 하나의 파티클 데이터가 연속 배치
    //    → 위치만 순회할 때도 속도·생명 데이터가 캐시에 같이 올라옴 (낭비!)
    //
    //  SoA (데이터 지향 설계):
    //    struct Particles {
    //        vector<float> x, y, z;
    //        vector<float> vx, vy, vz;
    //        vector<int> life;
    //    };
    //
    //    → 같은 필드끼리 연속 배치
    //    → 위치만 순회하면 x, y, z만 캐시에 올라옴 (효율적!)
    //
    //  ┌────────────────────────────────────────────────┐
    //  │  AoS 메모리 레이아웃 (캐시 라인 64B)           │
    //  │  [x y z vx vy vz life][x y z vx vy vz life].. │
    //  │  ~~~~~~~~~ 캐시 라인 ~~~~~~~~~~                │
    //  │  → 위치(x)만 필요해도 전체가 캐시에 올라옴     │
    //  │                                                │
    //  │  SoA 메모리 레이아웃                           │
    //  │  x: [x0 x1 x2 x3 x4 x5 x6 x7 ...]            │
    //  │  y: [y0 y1 y2 y3 y4 y5 y6 y7 ...]            │
    //  │     ~~~~~~~~~ 캐시 라인 ~~~~~~~~~~             │
    //  │  → x만 필요하면 x만 캐시에 올라옴!            │
    //  └────────────────────────────────────────────────┘

    const int COUNT = 500000;

    // ── AoS 방식 ──
    struct ParticleAoS {
        float x, y, z;
        float vx, vy, vz;
        int life;
    };

    vector<ParticleAoS> aos(COUNT);
    for (int i = 0; i < COUNT; ++i) {
        aos[i] = {1.0f * i, 2.0f * i, 3.0f * i,
                  0.1f, 0.2f, 0.3f, 100};
    }

    // ── SoA 방식 ──
    struct ParticlesSoA {
        vector<float> x, y, z;
        vector<float> vx, vy, vz;
        vector<int> life;
    };

    ParticlesSoA soa;
    soa.x.resize(COUNT); soa.y.resize(COUNT); soa.z.resize(COUNT);
    soa.vx.resize(COUNT); soa.vy.resize(COUNT); soa.vz.resize(COUNT);
    soa.life.resize(COUNT);
    for (int i = 0; i < COUNT; ++i) {
        soa.x[i] = 1.0f * i; soa.y[i] = 2.0f * i; soa.z[i] = 3.0f * i;
        soa.vx[i] = 0.1f; soa.vy[i] = 0.2f; soa.vz[i] = 0.3f;
        soa.life[i] = 100;
    }

    // 위치 업데이트만 수행 (x += vx)
    volatile float sink = 0;

    double aos_time = benchmark_ms([&]() {
        for (int i = 0; i < COUNT; ++i) {
            aos[i].x += aos[i].vx;
            aos[i].y += aos[i].vy;
            aos[i].z += aos[i].vz;
        }
        sink = aos[0].x;
    }, 30);

    double soa_time = benchmark_ms([&]() {
        for (int i = 0; i < COUNT; ++i) {
            soa.x[i] += soa.vx[i];
            soa.y[i] += soa.vy[i];
            soa.z[i] += soa.vz[i];
        }
        sink = soa.x[0];
    }, 30);

    print_bench("AoS (전통적)", aos_time);
    print_bench("SoA (데이터지향)", soa_time);
    cout << "  → SoA가 약 " << (aos_time / soa_time) << "배 빠름\n\n";

    // ── 순차 접근 vs 랜덤 접근 ──
    cout << "  [예제 2] 순차 vs 랜덤 메모리 접근\n";

    vector<int> data(1000000);
    iota(data.begin(), data.end(), 0);

    // 랜덤 인덱스 배열 생성
    vector<int> indices(data.size());
    iota(indices.begin(), indices.end(), 0);
    mt19937 rng(42);
    shuffle(indices.begin(), indices.end(), rng);

    volatile long long sum_sink = 0;

    double seq_time = benchmark_ms([&]() {
        long long s = 0;
        for (size_t i = 0; i < data.size(); ++i) s += data[i];
        sum_sink = s;
    }, 30);

    double rand_time = benchmark_ms([&]() {
        long long s = 0;
        for (size_t i = 0; i < indices.size(); ++i) s += data[indices[i]];
        sum_sink = s;
    }, 30);

    print_bench("순차 접근", seq_time);
    print_bench("랜덤 접근", rand_time);
    cout << "  → 순차가 약 " << (rand_time / seq_time) << "배 빠름\n";
    cout << "  (캐시 미스가 성능에 미치는 영향이 매우 크다!)\n\n";
}


// =========================================================================
//  레슨 3 — 복사 회피
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────┐
    │  복사를 줄이는 기법 비교표                                      │
    │                                                                 │
    │  ┌──────────────────┬─────────┬───────────────────────┐        │
    │  │ 기법             │ 비용    │ 적용 상황             │        │
    │  ├──────────────────┼─────────┼───────────────────────┤        │
    │  │ 값 복사          │ O(n)    │ 작은 POD 타입         │        │
    │  │ const 참조       │ O(1)    │ 읽기 전용 큰 객체     │        │
    │  │ move 시맨틱스    │ O(1)*   │ 소유권 이전           │        │
    │  │ RVO/NRVO         │ O(0)    │ 함수 반환값 (자동)    │        │
    │  │ string_view      │ O(1)    │ 문자열 읽기 전용 참조 │        │
    │  └──────────────────┴─────────┴───────────────────────┘        │
    │  * move는 내부 포인터 교환이므로 O(1), 복사는 O(n)             │
    │                                                                 │
    │  RVO (Return Value Optimization):                               │
    │    ┌─────────────────────────────────────────┐                  │
    │    │ vector<int> make() {                    │                  │
    │    │     vector<int> v = {1,2,3};  ← 여기서 │                  │
    │    │     return v;  ← 복사 없이 호출자에게  │                  │
    │    │ }               직접 구축됨 (C++17 보장)│                  │
    │    └─────────────────────────────────────────┘                  │
    └─────────────────────────────────────────────────────────────────┘
*/

// RVO 테스트용 클래스
struct HeavyObject {
    vector<int> data;
    static int copy_count;
    static int move_count;

    HeavyObject() : data(10000, 42) {}

    HeavyObject(const HeavyObject& other) : data(other.data) {
        ++copy_count;
    }
    HeavyObject(HeavyObject&& other) noexcept : data(move(other.data)) {
        ++move_count;
    }
    HeavyObject& operator=(const HeavyObject&) = default;
    HeavyObject& operator=(HeavyObject&&) noexcept = default;

    static void reset() { copy_count = 0; move_count = 0; }
};
int HeavyObject::copy_count = 0;
int HeavyObject::move_count = 0;

// RVO가 적용되는 경우
HeavyObject create_heavy_rvo() {
    HeavyObject obj;
    return obj;   // NRVO: 이름 있는 객체 반환 → 복사/이동 생략
}

// move를 명시적으로 사용하는 경우
HeavyObject create_heavy_moved() {
    HeavyObject obj;
    return move(obj);  // 주의: move()를 쓰면 NRVO가 깨질 수 있음!
}

// ── string_view 데모 ──
// string_view는 문자열의 "뷰"만 제공 (복사 없음)
//
//  string 전달:      [호출자 메모리] → 복사 → [함수 메모리]
//  string_view 전달: [호출자 메모리] ← 참조만 ← [함수: 포인터+길이]
//
size_t count_words_string(const string& s) {
    size_t count = 0;
    bool in_word = false;
    for (char c : s) {
        if (c == ' ' || c == '\n' || c == '\t') {
            in_word = false;
        } else if (!in_word) {
            in_word = true;
            ++count;
        }
    }
    return count;
}

size_t count_words_sv(string_view s) {
    size_t count = 0;
    bool in_word = false;
    for (char c : s) {
        if (c == ' ' || c == '\n' || c == '\t') {
            in_word = false;
        } else if (!in_word) {
            in_word = true;
            ++count;
        }
    }
    return count;
}

void lesson3_copy_avoidance() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 3 : 복사 회피                  │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    // ── RVO 테스트 ──
    cout << "  [예제 1] RVO (Return Value Optimization)\n";

    HeavyObject::reset();
    HeavyObject a = create_heavy_rvo();
    cout << "  RVO:  복사=" << HeavyObject::copy_count
         << ", 이동=" << HeavyObject::move_count << "\n";

    HeavyObject::reset();
    HeavyObject b = create_heavy_moved();
    cout << "  move: 복사=" << HeavyObject::copy_count
         << ", 이동=" << HeavyObject::move_count << "\n";
    cout << "  → return에 std::move()를 쓰면 NRVO가 방해받을 수 있다!\n\n";

    // ── const 참조 vs 값 복사 벤치마크 ──
    cout << "  [예제 2] 큰 vector 전달: 값 복사 vs const 참조\n";

    vector<int> big_vec(1000000);
    iota(big_vec.begin(), big_vec.end(), 0);

    auto sum_by_value = [](vector<int> v) {
        long long s = 0;
        for (int x : v) s += x;
        return s;
    };

    auto sum_by_ref = [](const vector<int>& v) {
        long long s = 0;
        for (int x : v) s += x;
        return s;
    };

    volatile long long sink;

    double val_time = benchmark_ms([&]() { sink = sum_by_value(big_vec); }, 30);
    double ref_time = benchmark_ms([&]() { sink = sum_by_ref(big_vec); }, 30);

    print_bench("값 복사", val_time);
    print_bench("const 참조", ref_time);
    cout << "  → const 참조가 약 " << (val_time / ref_time) << "배 빠름\n\n";

    // ── string_view 벤치마크 ──
    cout << "  [예제 3] string vs string_view\n";

    string long_text(100000, 'a');
    for (size_t i = 0; i < long_text.size(); i += 5) long_text[i] = ' ';

    volatile size_t word_sink;

    double str_time = benchmark_ms([&]() {
        word_sink = count_words_string(long_text);
    }, 100);

    double sv_time = benchmark_ms([&]() {
        word_sink = count_words_sv(long_text);
    }, 100);

    print_bench("string const&", str_time);
    print_bench("string_view", sv_time);
    cout << "  → string_view는 부분 문자열에서 진가를 발휘\n";
    cout << "    (substr이 복사 없이 O(1)로 가능!)\n\n";

    // ── move 시맨틱스 실전 ──
    cout << "  [예제 4] move 시맨틱스 효과\n";

    double copy_time = benchmark_ms([&]() {
        vector<int> src(100000, 42);
        vector<int> dst = src;        // 복사: O(n)
        (void)dst;
    }, 50);

    double move_time = benchmark_ms([&]() {
        vector<int> src(100000, 42);
        vector<int> dst = std::move(src);  // 이동: O(1)
        (void)dst;
    }, 50);

    print_bench("복사 대입", copy_time);
    print_bench("이동 대입", move_time);
    cout << "  → move가 약 " << (copy_time / move_time) << "배 빠름\n\n";
}


// =========================================================================
//  레슨 4 — 컨테이너 성능 비교
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────────┐
    │  주요 컨테이너 시간 복잡도 비교                                    │
    │                                                                     │
    │  ┌──────────────────┬──────────┬──────────┬──────────┬──────────┐  │
    │  │ 연산             │ vector   │ list     │ deque    │ 비고     │  │
    │  ├──────────────────┼──────────┼──────────┼──────────┼──────────┤  │
    │  │ 뒤에 추가        │ O(1)*   │ O(1)     │ O(1)     │          │  │
    │  │ 앞에 추가        │ O(n)     │ O(1)     │ O(1)     │          │  │
    │  │ 중간 삽입        │ O(n)     │ O(1)**  │ O(n)     │ **반복자 │  │
    │  │ 랜덤 접근        │ O(1)     │ O(n)     │ O(1)     │   있을때 │  │
    │  │ 순회             │ 매우빠름 │ 느림     │ 빠름     │ 캐시!    │  │
    │  │ 메모리 오버헤드  │ 낮음     │ 높음     │ 중간     │          │  │
    │  └──────────────────┴──────────┴──────────┴──────────┴──────────┘  │
    │  * 재할당 시 O(n)이지만 분할 상환(amortized) O(1)                  │
    │                                                                     │
    │  ┌──────────────────┬──────────────────┬──────────────────┐        │
    │  │ 연산             │ map (트리)       │ unordered_map    │        │
    │  ├──────────────────┼──────────────────┼──────────────────┤        │
    │  │ 삽입             │ O(log n)         │ O(1) 평균       │        │
    │  │ 검색             │ O(log n)         │ O(1) 평균       │        │
    │  │ 삭제             │ O(log n)         │ O(1) 평균       │        │
    │  │ 정렬된 순회      │ 가능 (자동정렬)  │ 불가능           │        │
    │  │ 최악의 경우      │ O(log n)         │ O(n) 해시충돌   │        │
    │  └──────────────────┴──────────────────┴──────────────────┘        │
    └─────────────────────────────────────────────────────────────────────┘
*/

void lesson4_container_perf() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 4 : 컨테이너 성능 비교         │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    const int N = 100000;

    // ── push_back 비교: vector vs list vs deque ──
    cout << "  [벤치마크 1] push_back " << N << "회\n";

    double vec_pb = benchmark_ms([&]() {
        vector<int> v; v.reserve(N);
        for (int i = 0; i < N; ++i) v.push_back(i);
    }, 50);

    double list_pb = benchmark_ms([&]() {
        list<int> l;
        for (int i = 0; i < N; ++i) l.push_back(i);
    }, 50);

    double deq_pb = benchmark_ms([&]() {
        deque<int> d;
        for (int i = 0; i < N; ++i) d.push_back(i);
    }, 50);

    print_bench("vector (reserved)", vec_pb);
    print_bench("list             ", list_pb);
    print_bench("deque            ", deq_pb);
    cout << "\n";

    // ── 순회 비교 ──
    cout << "  [벤치마크 2] 순회(합산) " << N << "개 원소\n";

    vector<int> vec(N);  iota(vec.begin(), vec.end(), 0);
    list<int> lst(vec.begin(), vec.end());
    deque<int> deq(vec.begin(), vec.end());

    volatile long long sink;

    double vec_iter = benchmark_ms([&]() {
        long long s = 0; for (int x : vec) s += x; sink = s;
    }, 50);

    double lst_iter = benchmark_ms([&]() {
        long long s = 0; for (int x : lst) s += x; sink = s;
    }, 50);

    double deq_iter = benchmark_ms([&]() {
        long long s = 0; for (int x : deq) s += x; sink = s;
    }, 50);

    print_bench("vector 순회", vec_iter);
    print_bench("list   순회", lst_iter);
    print_bench("deque  순회", deq_iter);
    cout << "  → vector가 캐시 친화적이라 순회가 가장 빠름!\n";
    cout << "  → list는 노드마다 힙 할당 → 캐시 미스 폭발\n\n";

    // ── map vs unordered_map ──
    cout << "  [벤치마크 3] map vs unordered_map 삽입/검색\n";

    double map_insert = benchmark_ms([&]() {
        map<int, int> m;
        for (int i = 0; i < N; ++i) m[i] = i * 2;
    }, 20);

    double umap_insert = benchmark_ms([&]() {
        unordered_map<int, int> m;
        m.reserve(N);
        for (int i = 0; i < N; ++i) m[i] = i * 2;
    }, 20);

    print_bench("map 삽입          ", map_insert);
    print_bench("unordered_map 삽입", umap_insert);

    // 검색 벤치마크
    map<int, int> test_map;
    unordered_map<int, int> test_umap;
    test_umap.reserve(N);
    for (int i = 0; i < N; ++i) { test_map[i] = i; test_umap[i] = i; }

    mt19937 rng(123);
    vector<int> queries(10000);
    for (auto& q : queries) q = rng() % N;

    volatile int found_sink;
    double map_find = benchmark_ms([&]() {
        for (int q : queries) { auto it = test_map.find(q); found_sink = it->second; }
    }, 30);

    double umap_find = benchmark_ms([&]() {
        for (int q : queries) { auto it = test_umap.find(q); found_sink = it->second; }
    }, 30);

    print_bench("map 검색          ", map_find);
    print_bench("unordered_map 검색", umap_find);
    cout << "  → 정렬이 필요 없다면 unordered_map이 훨씬 빠름\n";
    cout << "  → 단, 해시 충돌이 많으면 O(n)까지 느려질 수 있음\n\n";

    // ── 실전 가이드라인 ──
    cout << "  [컨테이너 선택 가이드]\n";
    cout << "  • 기본값: vector (90% 이상의 경우에 최선)\n";
    cout << "  • 앞뒤 삽입/삭제: deque\n";
    cout << "  • 중간 삽입이 빈번 + 랜덤접근 불필요: list (드문 경우)\n";
    cout << "  • 키-값 검색, 정렬 필요: map\n";
    cout << "  • 키-값 검색, 정렬 불필요: unordered_map\n";
    cout << "  • 작은 집합 (<100): 정렬된 vector가 map보다 빠를 수 있음\n\n";
}


// =========================================================================
//  레슨 5 — 알고리즘 최적화
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────┐
    │  분기 예측 (Branch Prediction)                                  │
    │                                                                 │
    │  현대 CPU는 파이프라인을 사용:                                  │
    │    Fetch → Decode → Execute → Write                            │
    │                                                                 │
    │  if/else에서 CPU는 결과를 "예측"하여 미리 실행:                │
    │    예측 성공 → 파이프라인 계속 (빠름)                          │
    │    예측 실패 → 파이프라인 비움 (15~20 사이클 손실!)            │
    │                                                                 │
    │  정렬된 배열에서 if (a[i] > threshold) 는                      │
    │  예측 성공률이 매우 높음 (연속된 같은 결과)                     │
    │                                                                 │
    │  ┌────────────────────────────────────────────┐                │
    │  │ 정렬 전: T F T T F F T F T F T F ← 예측 어려움  │          │
    │  │ 정렬 후: F F F F F F T T T T T T ← 예측 쉬움    │          │
    │  └────────────────────────────────────────────┘                │
    │                                                                 │
    │  SIMD (Single Instruction, Multiple Data):                      │
    │    하나의 명령으로 여러 데이터를 동시에 처리                    │
    │                                                                 │
    │    일반:   a1+b1, a2+b2, a3+b3, a4+b4  → 4개 명령             │
    │    SIMD:  [a1,a2,a3,a4] + [b1,b2,b3,b4] → 1개 명령!           │
    │                                                                 │
    │    컴파일러 자동 벡터화: -O2 이상 + 단순 루프 → 자동 SIMD     │
    │    수동: #include <immintrin.h> → _mm256_add_ps 등             │
    └─────────────────────────────────────────────────────────────────┘
*/

void lesson5_algorithm_opt() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 5 : 알고리즘 최적화            │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    // ── 분기 예측 데모 ──
    cout << "  [예제 1] 분기 예측: 정렬 vs 비정렬 배열\n";

    const int N = 500000;
    vector<int> sorted_data(N), unsorted_data(N);
    mt19937 rng(42);
    for (int i = 0; i < N; ++i) unsorted_data[i] = rng() % 256;
    sorted_data = unsorted_data;
    sort(sorted_data.begin(), sorted_data.end());

    const int THRESHOLD = 128;
    volatile long long sink;

    double unsorted_time = benchmark_ms([&]() {
        long long sum = 0;
        for (int i = 0; i < N; ++i) {
            if (unsorted_data[i] >= THRESHOLD) sum += unsorted_data[i];
        }
        sink = sum;
    }, 30);

    double sorted_time = benchmark_ms([&]() {
        long long sum = 0;
        for (int i = 0; i < N; ++i) {
            if (sorted_data[i] >= THRESHOLD) sum += sorted_data[i];
        }
        sink = sum;
    }, 30);

    print_bench("비정렬 (분기 예측 실패 많음)", unsorted_time);
    print_bench("정렬됨 (분기 예측 성공 높음)", sorted_time);
    cout << "  → 정렬 후 약 " << (unsorted_time / sorted_time) << "배 빠름\n\n";

    // ── 분기 없는 코드 (Branchless) ──
    cout << "  [예제 2] 분기 제거 (Branchless) 기법\n";

    double branch_time = benchmark_ms([&]() {
        long long sum = 0;
        for (int i = 0; i < N; ++i) {
            if (unsorted_data[i] >= THRESHOLD) sum += unsorted_data[i];
        }
        sink = sum;
    }, 30);

    double branchless_time = benchmark_ms([&]() {
        long long sum = 0;
        for (int i = 0; i < N; ++i) {
            // 비트 연산으로 분기 제거
            // (data >= 128) ? data : 0 을 분기 없이 계산
            int val = unsorted_data[i];
            int mask = -(val >= THRESHOLD);  // 조건 참이면 -1(0xFFFF...), 거짓이면 0
            sum += (val & mask);
        }
        sink = sum;
    }, 30);

    print_bench("분기 있는 코드  ", branch_time);
    print_bench("분기 없는 코드  ", branchless_time);
    cout << "\n";

    // ── 루프 언롤링 ──
    //
    //  원본:
    //    for (i = 0; i < N; ++i) sum += a[i];
    //
    //  4x 언롤링:
    //    for (i = 0; i < N; i += 4) {
    //        sum += a[i] + a[i+1] + a[i+2] + a[i+3];
    //    }
    //
    //  장점: 루프 오버헤드(비교, 점프) 감소, 파이프라인 활용
    //  주의: 컴파일러가 -O2에서 자동으로 해줌 → 수동은 거의 불필요

    cout << "  [예제 3] 루프 언롤링 (수동 vs 자동)\n";

    vector<int> arr(1000000);
    iota(arr.begin(), arr.end(), 1);
    int sz = static_cast<int>(arr.size());

    double normal_loop = benchmark_ms([&]() {
        long long s = 0;
        for (int i = 0; i < sz; ++i) s += arr[i];
        sink = s;
    }, 50);

    double unrolled_loop = benchmark_ms([&]() {
        long long s0 = 0, s1 = 0, s2 = 0, s3 = 0;
        int i = 0;
        for (; i + 3 < sz; i += 4) {
            s0 += arr[i];
            s1 += arr[i + 1];
            s2 += arr[i + 2];
            s3 += arr[i + 3];
        }
        long long s = s0 + s1 + s2 + s3;
        for (; i < sz; ++i) s += arr[i];
        sink = s;
    }, 50);

    print_bench("일반 루프   ", normal_loop);
    print_bench("4x 언롤링   ", unrolled_loop);
    cout << "  → -O2에서는 컴파일러가 자동 언롤링하므로 차이 적음\n";
    cout << "  → 수동 언롤링은 가독성 해침, 보통 컴파일러에 맡길 것\n\n";

    // ── 꼬리 재귀 최적화 개념 ──
    //
    //  꼬리 재귀(Tail Recursion): 함수의 마지막 동작이 재귀 호출인 경우
    //  컴파일러가 이를 루프로 변환할 수 있음 (스택 오버플로 방지)
    //
    //  일반 재귀:
    //    int factorial(int n) { return n * factorial(n-1); }
    //    → 마지막 동작이 "곱셈"이므로 꼬리 재귀가 아님
    //
    //  꼬리 재귀:
    //    int factorial(int n, int acc = 1) {
    //        if (n <= 1) return acc;
    //        return factorial(n-1, n * acc);  ← 마지막이 재귀 호출 자체
    //    }
    //    → 컴파일러가 루프로 최적화 가능 (-O2, GCC/Clang)

    cout << "  [꼬리 재귀 최적화]\n";
    cout << "  • C++ 표준에서 보장하지는 않지만 GCC/Clang -O2에서 적용됨\n";
    cout << "  • 확실하게 하려면 직접 반복문으로 작성하는 것이 안전\n\n";
}


// =========================================================================
//  레슨 6 — 메모리 풀과 커스텀 할당자
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────┐
    │  왜 메모리 풀이 필요한가?                                       │
    │                                                                 │
    │  new/delete (malloc/free)의 문제:                               │
    │  1. 시스템 콜 → 느림 (커널 전환 오버헤드)                      │
    │  2. 메모리 단편화 → 연속 메모리 부족                           │
    │  3. 스레드 안전 → 잠금 오버헤드                                │
    │                                                                 │
    │  메모리 풀: 미리 큰 블록을 할당 → 작은 조각으로 나눠 사용     │
    │                                                                 │
    │  ┌─────────────────────────────────────────────┐               │
    │  │   미리 할당된 큰 메모리 블록                 │               │
    │  │  ┌────┬────┬────┬────┬────┬────┬────┐      │               │
    │  │  │ A  │ B  │FREE│ C  │FREE│FREE│ D  │      │               │
    │  │  └────┴────┴──↑─┴────┴──↑─┴──↑─┴────┘      │               │
    │  │               │         │    │              │               │
    │  │  free_list: ──┘─────────┘────┘              │               │
    │  │  (사용 가능한 블록들의 연결 리스트)          │               │
    │  └─────────────────────────────────────────────┘               │
    │                                                                 │
    │  할당: free_list에서 하나 꺼냄 → O(1)                          │
    │  해제: free_list에 되돌림 → O(1)                               │
    │  vs new/delete: 시스템 콜, 탐색 → O(가변)                      │
    └─────────────────────────────────────────────────────────────────┘
*/

// ── 간단한 고정 크기 메모리 풀 구현 ──
class MemoryPool {
public:
    // block_size: 각 블록의 크기 (바이트)
    // block_count: 총 블록 수
    MemoryPool(size_t block_size, size_t block_count)
        : block_size_(block_size), block_count_(block_count)
    {
        // 전체 메모리를 한 번에 할당
        pool_ = static_cast<char*>(malloc(block_size_ * block_count_));

        // free list 구축: 각 블록의 첫 sizeof(void*) 바이트에
        // 다음 빈 블록의 주소를 저장
        free_head_ = pool_;
        char* current = pool_;
        for (size_t i = 0; i < block_count_ - 1; ++i) {
            char* next = current + block_size_;
            // 현재 블록에 다음 블록 주소 저장
            *reinterpret_cast<void**>(current) = next;
            current = next;
        }
        // 마지막 블록은 nullptr
        *reinterpret_cast<void**>(current) = nullptr;

        alloc_count_ = 0;
    }

    ~MemoryPool() {
        free(pool_);
    }

    // ── O(1) 할당 ──
    void* allocate() {
        if (!free_head_) return nullptr;  // 풀 소진

        void* block = free_head_;
        // free_head를 다음 빈 블록으로 이동
        free_head_ = *reinterpret_cast<void**>(free_head_);
        ++alloc_count_;
        return block;
    }

    // ── O(1) 해제 ──
    void deallocate(void* ptr) {
        // 반환된 블록을 free list 앞에 연결
        *reinterpret_cast<void**>(ptr) = free_head_;
        free_head_ = static_cast<char*>(ptr);
        --alloc_count_;
    }

    size_t alloc_count() const { return alloc_count_; }

private:
    char* pool_;            // 전체 메모리 블록
    void* free_head_;       // 다음 사용 가능한 블록
    size_t block_size_;     // 개별 블록 크기
    size_t block_count_;    // 총 블록 수
    size_t alloc_count_;    // 현재 할당된 블록 수

    // 복사 방지
    MemoryPool(const MemoryPool&) = delete;
    MemoryPool& operator=(const MemoryPool&) = delete;
};

void lesson6_memory_pool() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 6 : 메모리 풀과 커스텀 할당자  │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    const int N = 200000;

    // ── 메모리 풀 vs new/delete 벤치마크 ──
    cout << "  [벤치마크] 할당/해제 " << N << "회\n";

    struct SmallObj {
        int data[4];  // 16 바이트
    };

    // new/delete 방식
    double new_time = benchmark_ms([&]() {
        vector<SmallObj*> ptrs(N);
        for (int i = 0; i < N; ++i) {
            ptrs[i] = new SmallObj{{i, i+1, i+2, i+3}};
        }
        for (int i = 0; i < N; ++i) {
            delete ptrs[i];
        }
    }, 20);

    // 메모리 풀 방식
    double pool_time = benchmark_ms([&]() {
        MemoryPool pool(sizeof(SmallObj), N);
        vector<void*> ptrs(N);
        for (int i = 0; i < N; ++i) {
            void* mem = pool.allocate();
            SmallObj* obj = new(mem) SmallObj{{i, i+1, i+2, i+3}};
            ptrs[i] = obj;
        }
        for (int i = 0; i < N; ++i) {
            pool.deallocate(ptrs[i]);
        }
    }, 20);

    print_bench("new/delete  ", new_time);
    print_bench("메모리 풀   ", pool_time);
    cout << "  → 메모리 풀이 약 " << (new_time / pool_time) << "배 빠름\n\n";

    // ── 메모리 풀 사용 예시 ──
    cout << "  [메모리 풀 사용 흐름]\n";
    MemoryPool pool(sizeof(SmallObj), 5);

    void* p1 = pool.allocate();
    void* p2 = pool.allocate();
    void* p3 = pool.allocate();
    cout << "  할당 3개 → 현재 사용 중: " << pool.alloc_count() << "\n";

    pool.deallocate(p2);
    cout << "  p2 해제  → 현재 사용 중: " << pool.alloc_count() << "\n";

    void* p4 = pool.allocate();  // p2가 있던 공간을 재사용
    cout << "  p4 할당  → 현재 사용 중: " << pool.alloc_count() << "\n";

    pool.deallocate(p1);
    pool.deallocate(p3);
    pool.deallocate(p4);
    cout << "  모두 해제 → 현재 사용 중: " << pool.alloc_count() << "\n\n";

    // ── STL 호환 커스텀 할당자 개념 ──
    //
    //  C++ STL 컨테이너는 할당자를 템플릿 매개변수로 받음:
    //    vector<int, MyAllocator<int>> v;
    //
    //  커스텀 할당자 최소 요구사항:
    //    using value_type = T;
    //    T* allocate(size_t n);
    //    void deallocate(T* p, size_t n);
    //
    //  실전에서는:
    //    • 게임 엔진: 프레임 할당자 (매 프레임 전체 리셋)
    //    • 서버: 연결별 메모리 풀
    //    • 임베디드: 고정 크기 버퍼에서만 할당

    cout << "  [커스텀 할당자 활용 분야]\n";
    cout << "  • 게임: 프레임별 선형 할당자 (bump allocator)\n";
    cout << "  • 서버: 요청별 메모리 풀\n";
    cout << "  • 실시간 시스템: 힙 할당 금지 → 고정 풀만 사용\n";
    cout << "  • 메모리 추적/디버깅: 할당 위치 기록\n\n";
}


// =========================================================================
//  레슨 7 — 프로파일링 도구 가이드
// =========================================================================
/*
    ┌─────────────────────────────────────────────────────────────────────────┐
    │  프로파일링 도구 완전 가이드                                            │
    │                                                                         │
    │  "측정 없는 최적화는 추측일 뿐이다"                                    │
    │                                                                         │
    │  ┌──────────────────┬──────────────┬────────────┬───────────────────┐  │
    │  │ 도구             │ 플랫폼       │ 유형       │ 장점              │  │
    │  ├──────────────────┼──────────────┼────────────┼───────────────────┤  │
    │  │ perf             │ Linux        │ 샘플링     │ 저오버헤드, 강력  │  │
    │  │ Valgrind/        │ Linux        │ 계측       │ 정확, 캐시분석    │  │
    │  │   Callgrind      │              │            │                   │  │
    │  │ gprof            │ Linux/Mac    │ 계측+샘플  │ 간편함            │  │
    │  │ VS Profiler      │ Windows      │ 샘플링     │ GUI, 통합         │  │
    │  │ Intel VTune      │ 모두         │ 하드웨어   │ 캐시/SIMD 분석   │  │
    │  │ Tracy            │ 모두         │ 계측       │ 실시간, 게임용    │  │
    │  │ Google Benchmark │ 모두         │ 마이크로   │ 정밀 벤치마크     │  │
    │  └──────────────────┴──────────────┴────────────┴───────────────────┘  │
    │                                                                         │
    │  프로파일링 유형:                                                       │
    │                                                                         │
    │  1. 샘플링(Sampling): 주기적으로 실행 위치 수집                        │
    │     장점: 오버헤드 낮음                                                │
    │     단점: 통계적 (짧은 함수 놓칠 수 있음)                             │
    │                                                                         │
    │  2. 계측(Instrumentation): 함수 시작/끝에 코드 삽입                    │
    │     장점: 정확한 호출 횟수와 시간                                      │
    │     단점: 오버헤드가 큼                                                │
    │                                                                         │
    │  ───────────────── perf 사용법 ─────────────────                       │
    │                                                                         │
    │  # 컴파일 (-g 필수: 디버그 심볼)                                       │
    │  g++ -std=c++17 -O2 -g -o myapp main.cpp                               │
    │                                                                         │
    │  # 기본 프로파일링                                                      │
    │  perf record ./myapp                                                    │
    │  perf report                     ← 함수별 CPU 사용률                   │
    │                                                                         │
    │  # 상세 통계                                                            │
    │  perf stat ./myapp               ← 캐시 미스, 분기 예측 등             │
    │                                                                         │
    │  # 출력 예시:                                                           │
    │  # Performance counter stats for './myapp':                             │
    │  #    1,234,567  cache-misses       (10.5%)                             │
    │  #   98,765,432  cache-references                                       │
    │  #      567,890  branch-misses      (2.1%)                              │
    │  #   26,543,210  branches                                               │
    │                                                                         │
    │  ─────────── Valgrind / Callgrind ───────────                          │
    │                                                                         │
    │  # 캐시 시뮬레이션                                                      │
    │  valgrind --tool=cachegrind ./myapp                                     │
    │                                                                         │
    │  # 함수 호출 그래프                                                     │
    │  valgrind --tool=callgrind ./myapp                                      │
    │  kcachegrind callgrind.out.*    ← GUI 분석                             │
    │                                                                         │
    │  ─────────── gprof 사용법 ───────────                                  │
    │                                                                         │
    │  # 1. -pg 옵션으로 컴파일                                               │
    │  g++ -std=c++17 -O2 -pg -o myapp main.cpp                              │
    │                                                                         │
    │  # 2. 프로그램 실행 (gmon.out 생성됨)                                   │
    │  ./myapp                                                                │
    │                                                                         │
    │  # 3. 결과 분석                                                         │
    │  gprof myapp gmon.out > analysis.txt                                    │
    │                                                                         │
    │  ────── Visual Studio Profiler (Windows) ──────                        │
    │                                                                         │
    │  1. 디버그 → 성능 프로파일러 (Alt+F2)                                  │
    │  2. "CPU 사용량" 선택                                                   │
    │  3. 시작 → 프로그램 실행 → 중지                                       │
    │  4. 핫 경로(Hot Path) 자동 표시                                        │
    │  5. 함수별 → 줄별 CPU 사용률 확인                                     │
    │                                                                         │
    │  ─── 프로파일링 워크플로우 (최적화 절차) ───                           │
    │                                                                         │
    │  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐             │
    │  │ 1.측정  │ →  │ 2.병목  │ →  │ 3.최적화│ →  │ 4.재측정│             │
    │  │ (프로파│    │  지점   │    │         │    │         │             │
    │  │  일링) │    │  식별   │    │         │    │         │             │
    │  └─────────┘    └─────────┘    └─────────┘    └────┬────┘             │
    │       ↑                                            │                   │
    │       └────────────────────────────────────────────┘                   │
    │                   (개선될 때까지 반복)                                  │
    └─────────────────────────────────────────────────────────────────────────┘
*/

void lesson7_profiling_guide() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 7 : 프로파일링 도구 가이드     │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    // ── 자체 내장 프로파일러 구현 ──
    //
    // 외부 도구가 없을 때 간단히 사용할 수 있는 범용 타이머
    // 실전에서는 Google Benchmark 또는 Tracy를 권장

    struct ScopeTimer {
        const char* name;
        chrono::steady_clock::time_point start;

        ScopeTimer(const char* n) : name(n), start(chrono::steady_clock::now()) {}
        ~ScopeTimer() {
            auto end = chrono::steady_clock::now();
            double ms = chrono::duration<double, milli>(end - start).count();
            cout << "    [Timer] " << name << ": " << ms << " ms\n";
        }
    };

    cout << "  [자체 ScopeTimer 데모]\n";
    {
        ScopeTimer t("vector 100만 원소 정렬");
        vector<int> v(1000000);
        mt19937 rng(42);
        for (auto& x : v) x = rng();
        sort(v.begin(), v.end());
    }
    {
        ScopeTimer t("문자열 10만개 연결");
        string result;
        result.reserve(1000000);
        for (int i = 0; i < 100000; ++i) {
            result += "hello";
        }
    }
    cout << "\n";

    // ── 프로파일링 체크리스트 ──
    cout << "  [최적화 체크리스트]\n";
    cout << "  ┌────────────────────────────────────────────────────┐\n";
    cout << "  │  □ 1. 먼저 정확한 코드를 작성한다                 │\n";
    cout << "  │  □ 2. 프로파일러로 병목 지점을 측정한다           │\n";
    cout << "  │  □ 3. 가장 느린 함수부터 최적화한다               │\n";
    cout << "  │  □ 4. 알고리즘 복잡도를 먼저 개선한다             │\n";
    cout << "  │     (O(n²) → O(n log n) 이 미시 최적화보다 효과적)│\n";
    cout << "  │  □ 5. 메모리 접근 패턴을 최적화한다               │\n";
    cout << "  │  □ 6. 불필요한 복사를 제거한다                    │\n";
    cout << "  │  □ 7. 최적화 후 반드시 재측정한다                 │\n";
    cout << "  │  □ 8. 벤치마크를 자동화 테스트에 포함한다         │\n";
    cout << "  └────────────────────────────────────────────────────┘\n\n";

    // ── 자주 하는 실수 ──
    cout << "  [흔한 최적화 실수]\n";
    cout << "  1. 측정 없이 '감'으로 최적화 → 시간 낭비\n";
    cout << "  2. -O0으로 벤치마크 → 현실과 완전히 다른 결과\n";
    cout << "  3. 작은 함수만 최적화 → 전체 성능에 영향 미미\n";
    cout << "  4. 가독성 파괴 수준의 최적화 → 유지보수 불가\n";
    cout << "  5. 캐시 효과 무시 → 복잡도는 같지만 실제 속도 차이 큼\n\n";

    // ── 추가 학습 도구 ──
    cout << "  [추천 프로파일링 도구]\n";
    cout << "  • Google Benchmark: 정밀한 마이크로벤치마크\n";
    cout << "    (github.com/google/benchmark)\n";
    cout << "  • Tracy Profiler: 실시간 프레임 프로파일러 (게임용)\n";
    cout << "    (github.com/wolfpld/tracy)\n";
    cout << "  • Compiler Explorer (godbolt.org): 어셈블리 확인\n";
    cout << "  • Quick C++ Benchmark (quick-bench.com): 온라인 벤치마크\n\n";

    // ──────────────────────────────────────────────────────────────
    //  ★ 종합 연습문제 ★
    // ──────────────────────────────────────────────────────────────
    cout << "  ╔═══════════════════════════════════════════════════╗\n";
    cout << "  ║  ★ 종합 연습문제                                 ║\n";
    cout << "  ╠═══════════════════════════════════════════════════╣\n";
    cout << "  ║  1. 10만개 정수 배열에서 짝수의 합을 구하는      ║\n";
    cout << "  ║     함수를 3가지 방법으로 구현하고 벤치마크하라:  ║\n";
    cout << "  ║     (a) for 루프 + if 분기                       ║\n";
    cout << "  ║     (b) branchless (비트마스크)                   ║\n";
    cout << "  ║     (c) std::accumulate + 람다                   ║\n";
    cout << "  ║                                                   ║\n";
    cout << "  ║  2. AoS와 SoA로 3D 벡터 100만개의 길이를        ║\n";
    cout << "  ║     계산하고 성능 차이를 측정하라.               ║\n";
    cout << "  ║                                                   ║\n";
    cout << "  ║  3. 고정 크기 메모리 풀을 확장하여:              ║\n";
    cout << "  ║     (a) 풀이 가득 차면 자동 확장하는 기능 추가   ║\n";
    cout << "  ║     (b) 할당된 메모리 통계 출력 기능 추가        ║\n";
    cout << "  ║                                                   ║\n";
    cout << "  ║  4. map, unordered_map, 정렬된 vector(+이진검색) ║\n";
    cout << "  ║     으로 10만개 문자열 키를 검색하는 벤치마크를  ║\n";
    cout << "  ║     작성하라.                                     ║\n";
    cout << "  ╚═══════════════════════════════════════════════════╝\n\n";
}
