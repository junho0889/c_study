# C++ 메모리 관리 횡단 가이드 (모든 챕터별)

이 문서는 32 + 4개 챕터 각각에서 **반드시 알아야 할 메모리 함정**을
모아둔 "체크리스트"입니다. 각 항목은 **WHY (왜 위험)** + **HOW (어떻게 피함)** 형식.

> 일반론은 ch08 (메모리 관리)을 먼저 정독하세요. 이 가이드는 *각 주제 영역에
> 특화된* 위험만 모았습니다.

## 빠른 색인

| 영역 | 챕터 | 핵심 위험 |
|------|------|-----------|
| 변수/타입 | 01 | 미초기화 / 정수 오버플로 / 부호 변환 |
| 제어문 | 02 | 루프 변수 댕글링 / switch fallthrough |
| 함수 | 03 | 지역 참조 반환 / 람다 캡처 수명 |
| 배열/포인터 | 04 | new/delete 짝 / 배열 decay / OOB |
| OOP 기초 | 05 | 깊은 복사 / 소멸자 누락 / new 후 예외 |
| 상속 | 06 | 가상 소멸자 / 슬라이싱 |
| STL | 07 | iterator 무효화 / move-from |
| 메모리 관리 | 08 | (메인 챕터) |
| 파일/예외 | 09 | RAII 보장 / 부분 쓰기 |
| Modern C++ | 10 | **auto 추론 함정** / optional / variant / structured binding 수명 |
| 디버깅 | 11 | sanitizer 한계 / valgrind 비용 |
| 빌드 | 12 | ABI / 정적-동적 혼합 |
| 디자인 패턴 | 13 | Singleton 정적 초기화 순서 / Observer 댕글링 |
| 멀티스레딩 | 14 | 데이터 레이스 / spurious wakeup / TLS |
| 네트워크 | 15, 34 | partial recv / 콜백 수명 / 버퍼 풀 |
| 테스트 | 16 | leak detection / fixture 공유 |
| 빌드/배포 | 17 | 정적 분석 / valgrind on CI |
| 실전 | 18 | 통합 시 누수 |
| 자료구조 | 19 | 노드 소유 / 포인터 안정성 |
| 고급 OOP | 20 | Rule of 5 / 가상 상속 / CRTP |
| 고급 템플릿 | 21 | 템플릿 인스턴스 폭발 / SFINAE 함정 |
| 문자열/정규식 | 22 | string_view 댕글링 / regex 백트래킹 OOM |
| 함수형 | 23 | 클로저 캡처 / std::function heap 할당 |
| 고급 동시성 | 24 | use-after-free / 락프리 ABA |
| 성능 | 25 | false sharing / SBO / 캐시 |
| C++20/23 | 26 | coroutine frame / ranges view 수명 |
| 시스템 | 27 | strict aliasing / volatile 오용 |
| 보안 | 28 | OOB / format string / TOCTOU |
| 이벤트 | 29 | callback 수명 / weak_ptr |
| 하드웨어 | 30 | MMIO / DMA 일관성 |
| ADC/센서 | 31 | 링버퍼 / 정밀도 손실 |
| RTOS | 32 | 우선순위 역전 / 스택 / heap 금지 |
| **데이터 포맷** | **33** | **string_view 댕글링 / mmap / 큰 파일** |
| **네트워크 계층** | **34** | **partial recv / 콜백 캡처 / TLS 누수** |
| **산업용 프로토콜** | **35** | **DMA / ISR-safe / 실시간 lock-free** |
| **Docker** | **36** | **cgroup limit / OOM / jemalloc** |
| **ML 추론** | **37** | **GPU 메모리 / 비동기 동기화 / pinned / 워크스페이스 / 양자화** |

---

## 챕터별 상세

### Ch 01 — 기초 변수/타입

| # | 위험 | 발현 | 회피 |
|---|------|------|------|
| 1 | 미초기화 변수 | `int x; cout << x;` → 임의 값. `-fsanitize=memory`만 잡음 | 항상 초기화: `int x{};` 또는 `int x = 0;` |
| 2 | 정수 오버플로 (signed) | `INT_MAX + 1` = UB. 컴파일러가 가정으로 최적화 | `<limits>` 검사, `-fsanitize=undefined` |
| 3 | 부호 변환 | `int x = -1; size_t s = x;` → 매우 큰 양수 | `-Wsign-conversion` 활성화 |
| 4 | `auto` + 의도치 않은 타입 | `auto v = vec[0];` (참조 vs 복사) | 명시적: `auto& v` 또는 `const auto&` |
| 5 | 부동소수점 == 비교 | `0.1 + 0.2 == 0.3` 거짓 | `abs(a - b) < eps` |

### Ch 02 — 제어문

| # | 위험 | 회피 |
|---|------|------|
| 1 | switch fallthrough 누락 | `[[fallthrough]]` 명시 또는 `break` |
| 2 | range-for의 임시값 댕글링 | `for (auto& x : f())` 위험. C++23이 일부 수정 |
| 3 | `continue` 후 자원 해제 누락 | RAII 사용, raw resource 금지 |

### Ch 03 — 함수

| # | 위험 | 회피 |
|---|------|------|
| 1 | 지역 변수 참조/포인터 반환 | 절대 금지. `string&` → 호출자 UB |
| 2 | 람다가 지역 변수 by-ref 캡처 후 비동기 실행 | by-value 또는 `shared_ptr` 캡처 |
| 3 | 가변 인자 (varargs) `va_list` 타입 검증 X | `<format>` (C++20) 또는 fmt 사용 |
| 4 | 큰 객체 by-value 매개변수 | `const T&` (단, std::string은 SBO로 작으면 by-value 더 빠를 수 있음) |
| 5 | 재귀 깊이 → 스택 오버플로 | 임베디드는 특히 위험. 반복문/명시적 스택 |

### Ch 04 — 배열/포인터

| # | 위험 | 회피 |
|---|------|------|
| 1 | `new T[n]` ↔ `delete []` | unique_ptr<T[]> 또는 vector 사용 |
| 2 | 배열 decay → `sizeof(arr)` in 함수가 포인터 크기 | `std::array<T,N>` 또는 `std::span` |
| 3 | OOB read/write | `at()` 사용, ASan |
| 4 | NULL deref | smart ptr / optional |
| 5 | 댕글링 포인터 | weak_ptr / 명확한 소유권 |
| 6 | `delete` 후 nullptr 미설정 | smart ptr가 자동 처리 |
| 7 | C-string + `\0` 누락 | `std::string` |

### Ch 05 — OOP 기초

| # | 위험 | 회피 |
|---|------|------|
| 1 | 동적 멤버 + 깊은 복사 부재 | Rule of 3/5 또는 = delete |
| 2 | 생성자 중간에 예외 → 부분 초기화 객체 X (소멸자 호출 안 됨) | RAII 멤버로 자동 정리 |
| 3 | 소멸자에서 throw | noexcept 보장. throw는 std::terminate |
| 4 | static 멤버 초기화 순서 (다른 TU 간) | Meyer's singleton (정적 지역) |
| 5 | this 포인터 비동기 캡처 | enable_shared_from_this |

### Ch 06 — 상속/다형성

| # | 위험 | 회피 |
|---|------|------|
| 1 | 가상 소멸자 누락 | base에 `virtual ~Base() = default;` |
| 2 | 슬라이싱 (값 복사로 파생 정보 손실) | 포인터/참조로 다룸 |
| 3 | 가상 함수에서 this 캡처 | virtual + async 시 shared_from_this |
| 4 | 다이아몬드 상속 → 멤버 중복 | virtual inheritance |
| 5 | 객체 생성/파괴 중 가상함수 호출 | base의 virtual 호출됨 (파생 X) |

### Ch 07 — STL

| # | 위험 | 회피 |
|---|------|------|
| 1 | iterator 무효화 | vector push_back 후 기존 iter 무효 (재할당 시) |
| 2 | erase-remove 패턴 미사용 | `v.erase(remove_if(...), v.end())` |
| 3 | move-from 객체 사용 | move 후엔 reassign 또는 폐기만 |
| 4 | unordered_map 키 해시 충돌 → O(n) 공격 | 안전 해시 |
| 5 | 큰 객체를 vector에 push → 재할당 비용 | reserve |

### Ch 08 — 메모리 관리 (메인)

전체가 메모리 관리 챕터. 핵심:

- **stack vs heap**: 스택 자동, 힙 명시
- **unique_ptr**: 단독 소유. 이동만 가능
- **shared_ptr**: 참조 카운트. 순환 시 weak_ptr
- **RAII**: 자원 = 객체 수명
- **move semantics**: 비싼 복사 → 포인터 교환

**추가 함정**:
- shared_ptr 제어 블록은 별도 heap 할당 → make_shared로 통합
- weak_ptr.lock()는 가능한 lock 해서 shared_ptr 받기 (자체 expired 체크 race)
- shared_ptr<T> 의 deleter는 type-erased → 같은 T 다른 deleter 가능

### Ch 09 — 파일/예외

| # | 위험 | 회피 |
|---|------|------|
| 1 | 파일 핸들 누수 (예외 경로) | RAII (ifstream/ofstream가 자동) |
| 2 | 부분 쓰기 후 크래시 | atomic write: temp + rename |
| 3 | exception slicing (catch by value) | catch by const reference |
| 4 | 소멸자 throw → terminate | noexcept |
| 5 | bad_alloc 다음 동작 정의 안 함 | 메모리 풀 / 사전 reserve |

### Ch 10 — Modern C++

| # | 위험 | 회피 |
|---|------|------|
| 1 | `optional<T&>`는 C++23+ 만 | reference_wrapper |
| 2 | structured binding이 참조 vs 복사 | `auto& [a, b]` |
| 3 | variant.get<T> 잘못된 타입 → bad_variant_access | get_if |
| 4 | `if constexpr` 안에서 dependent 이름 | requires (C++20) 권장 |
| 5 | NRVO 의존 코드 | C++17 보장 RVO 활용 |

#### Ch 10 — auto 타입 추론 함정 (Lesson 0)

| # | 위험 | 발현 | 회피 |
|---|------|------|------|
| A1 | `auto x = ref;` → 참조/const 떨어짐 | 의도치 않은 복사 / 원본 수정 안 됨 | `auto&` / `const auto&` 명시 |
| A2 | range-for `auto kv : map` | pair 매번 복사 (큰 비용) | `const auto& [k, v]` |
| A3 | `auto x{42};` C++11 vs C++17 | 같은 코드가 표준 따라 다름 | `=` 또는 `()` 사용 |
| A4 | `auto x = vec[0]` on `vector<bool>` | proxy 객체, 일반 bool처럼 동작 X | `bool x = vec[0]` |
| A5 | `auto x = a + b` (Eigen lazy) | 임시 표현식 보유, 원본 변경 시 결과 다름 | 명시적 타입으로 즉시 평가 |
| A6 | `decltype(i)` vs `decltype((i))` | 괄호 유무로 타입 다름 (& 추가) | 의식하고 사용 |
| A7 | `auto` return + 지역 변수 참조 | 댕글링 참조 반환 | 값 반환 또는 수명 보장 |
| A8 | `auto&` for 임시 객체 | 컴파일은 되지만 의도 불명 | `const auto&` 또는 `auto&&` |
| A9 | `auto` + 배열 → 포인터 decay | `sizeof` 망가짐 | `auto&` 사용 |
| A10 | CTAD `vector v(10)` | 단일 정수면 size 해석, CTAD 안 함 | `vector v{10}` 또는 명시적 |
| A11 | `decltype(auto)` 잘못 적용 | 의도치 않은 참조 보존 | 의도 명확할 때만 사용 |
| A12 | 람다 `[&]` 자동 캡처 + auto 변수 | 캡처된 ref가 함수 끝나면 댕글링 | `[=]` 또는 명시적 캡처 |

### Ch 11 — 디버깅

| # | 위험 | 회피 |
|---|------|------|
| 1 | ASan 못 잡는 UB (정수 오버플로 등) | UBSan 병행 |
| 2 | TSan은 소수의 데이터 레이스만 | 모든 코드 경로 실행 필요 |
| 3 | valgrind 컨테이너에서 매우 느림 | jemalloc heap profile 또는 sampling |
| 4 | release 빌드는 디버그 정보 손실 | RelWithDebInfo |
| 5 | `assert` -DNDEBUG 비활성 | release에선 검증 빠짐. 보안 검증은 항상 작동 |

### Ch 12 — 빌드/프레임워크

| # | 위험 | 회피 |
|---|------|------|
| 1 | -DCMAKE_BUILD_TYPE 누락 → Debug 운영 | 명시적 Release |
| 2 | _GLIBCXX_USE_CXX11_ABI 혼용 | 모든 라이브러리 통일 |
| 3 | `target_link_libraries PRIVATE` 누락 → transitive 의존 | PUBLIC/PRIVATE 명시 |
| 4 | 동적/정적 혼합 → 두 번 초기화 | static 라이브러리 일관 |

### Ch 13 — 디자인 패턴

| # | 위험 | 회피 |
|---|------|------|
| 1 | Singleton: 정적 초기화 순서 fiasco | Meyer's (함수 안 정적) |
| 2 | Singleton: 멀티 스레드 첫 호출 race | C++11+ 정적 초기화 자동 thread-safe |
| 3 | Observer: 옵저버 dangling | weak_ptr 또는 명시적 unsubscribe |
| 4 | Builder: 부분 구축 후 예외 | strong exception safety |
| 5 | RAII: 소멸자 안에서 throw 금지 | noexcept |

### Ch 14 — 멀티스레딩

| # | 위험 | 회피 |
|---|------|------|
| 1 | 데이터 레이스 (UB) | mutex / atomic |
| 2 | spurious wakeup | while (predicate) wait |
| 3 | TLS 변수 + thread join 전 종료 | TLS 정리 핸들러 |
| 4 | atomic vs volatile (다름) | atomic 사용 |
| 5 | thread::join 누락 → terminate | RAII jthread (C++20) |
| 6 | mutex unlock 누락 (예외) | lock_guard |
| 7 | 데드락 (락 순서) | std::lock 또는 hierarchy |

### Ch 15, 34 — 네트워크

(Ch 34에서 자세히. 핵심만 재요약)
- partial recv → 길이 prefix 또는 delimiter
- send/recv 콜백 도중 객체 소멸 → shared_from_this
- TLS (OpenSSL) X509 / EVP_PKEY / BIO 누수 → unique_ptr deleter
- buffer pool (heap fragmentation 방지)
- getaddrinfo → freeaddrinfo

### Ch 16 — 테스트

| # | 위험 | 회피 |
|---|------|------|
| 1 | 테스트 fixture 간 정적 상태 공유 | SetUp/TearDown 명시 |
| 2 | 비동기 테스트 → 스레드 누수 | future.get() 또는 timeout |
| 3 | mock의 기대값 vs 실제 호출 누락 | gtest의 EXPECT_CALL |
| 4 | leak detector 비활성 (release) | RelWithDebInfo + LSan |

### Ch 17 — 빌드/배포

| # | 위험 | 회피 |
|---|------|------|
| 1 | CI는 통과, 운영 다운 | sanitizer / valgrind on CI |
| 2 | 다른 OS의 미정의 함수 의존 | feature 검사 (CMake) |
| 3 | core dump 비활성 → 디버깅 불가 | ulimit / coredump 정책 |

### Ch 18 — 실전

여러 챕터 통합. 각 모듈의 함정 모두 발생 가능.

### Ch 19 — 자료구조

| # | 위험 | 회피 |
|---|------|------|
| 1 | 노드 소유권 불명확 → 누수 | unique_ptr 명시적 |
| 2 | iterator 무효화 (벡터 vs 리스트) | 컨테이너 보장 명시 |
| 3 | 재귀 트리 소멸 → 스택 오버플로 | iterative 소멸 |
| 4 | 해시 테이블 rehash → reference 무효화 | unordered_map 변경 시 주의 |

### Ch 20 — 고급 OOP

| # | 위험 | 회피 |
|---|------|------|
| 1 | Rule of 5 일부만 정의 | =default / =delete 명시 |
| 2 | move ctor noexcept 누락 → vector 안에서 copy fallback | noexcept 보장 |
| 3 | virtual inheritance 기본 인자 호출 책임 | most-derived가 호출 |
| 4 | CRTP 잘못된 cast → UB | static_assert |

### Ch 21 — 고급 템플릿

| # | 위험 | 회피 |
|---|------|------|
| 1 | 템플릿 폭발 (10만 인스턴스) → 컴파일 OOM | 헤더만 / extern template |
| 2 | SFINAE 미스매치로 런타임 선택 | concepts (C++20) |
| 3 | constexpr → 런타임 폴백 비용 | static_assert |
| 4 | 가변 인자 fold expression empty case | 명시 base |

### Ch 22 — 문자열/정규식

| # | 위험 | 회피 |
|---|------|------|
| 1 | string_view 댕글링 | 원본 수명 명시 |
| 2 | regex 백트래킹 폭주 (catastrophic) | 안 쓰거나 입력 검증 / re2 |
| 3 | UTF-8 바이트 단위 vs 문자 단위 | ICU |
| 4 | `std::tolower` locale 의존 | locale-independent 직접 |

### Ch 23 — 함수형

| # | 위험 | 회피 |
|---|------|------|
| 1 | std::function의 type erasure → heap 할당 | 큰 캡처는 비용. inplace_function 고려 |
| 2 | 람다 캡처 by-ref + 비동기 → 댕글링 | by-value 또는 shared 캡처 |
| 3 | std::bind 깊은 매개변수 추적 어려움 | 람다로 대체 |

### Ch 24 — 고급 동시성

| # | 위험 | 회피 |
|---|------|------|
| 1 | parallel_reduce에 by-ref 캡처 → use-after-free | 명시적 move / shared_ptr |
| 2 | shared_mutex 우선순위 starvation | 정책 명시 |
| 3 | 락프리 ABA 문제 | hazard pointer / sequence number |
| 4 | thread pool 종료 시 미완 task | future 정리 |
| 5 | condition_variable 외부 락 미보호 | 항상 unique_lock + wait |

### Ch 25 — 성능

| # | 위험 | 회피 |
|---|------|------|
| 1 | false sharing (cache line) | alignas(64) |
| 2 | SBO 조건부 동작 | 측정 |
| 3 | 컴파일러 최적화 가정 | godbolt 확인 |
| 4 | 메모리 풀 단편화 | 풀 size 분석 |

### Ch 26 — C++20/23

| # | 위험 | 회피 |
|---|------|------|
| 1 | coroutine frame heap 할당 | HALO 최적화 / inline |
| 2 | ranges view + 임시 → 댕글링 | view를 즉시 소비 |
| 3 | std::span에 임시 vector → 댕글링 | 명시적 owner 유지 |
| 4 | jthread cancel 토큰 | stop_token 체크 |

### Ch 27 — 시스템 프로그래밍

| # | 위험 | 회피 |
|---|------|------|
| 1 | strict aliasing 위반 (UB) | memcpy / std::bit_cast |
| 2 | volatile 잘못된 사용 (스레드 동기화) | atomic |
| 3 | 정렬 안 된 read/write (UB on ARM) | alignas |
| 4 | 엔디언 가정 | htons/htonl |

### Ch 28 — 보안

| # | 위험 | 회피 |
|---|------|------|
| 1 | OOB read (heartbleed류) | bounds check |
| 2 | format string injection | -Wformat-security |
| 3 | TOCTOU 파일 검사 | open + fstat |
| 4 | 암호 메모리 leak | OPENSSL_cleanse / memset_s |
| 5 | 정수 오버플로로 buffer 작아짐 | checked arithmetic |

### Ch 29 — 이벤트/콜백

| # | 위험 | 회피 |
|---|------|------|
| 1 | 콜백이 객체보다 오래 살아남음 | weak_ptr / unsubscribe |
| 2 | 시그널 핸들러에서 malloc | signal-safe 함수만 |
| 3 | 이벤트 큐 무한 누적 | 백프레셔 |

### Ch 30 — 하드웨어 제어

| # | 위험 | 회피 |
|---|------|------|
| 1 | MMIO에 일반 메모리 접근 → 캐시 stale | volatile + 메모리 배리어 |
| 2 | DMA 캐시 일관성 | cache flush API |
| 3 | 정렬되지 않은 레지스터 접근 | alignas |
| 4 | ISR 안에서 동적 할당 | 풀 사전 할당 |

### Ch 31 — ADC/DAC/센서

| # | 위험 | 회피 |
|---|------|------|
| 1 | 링버퍼 wraparound 시 partial read | atomic head/tail |
| 2 | 정밀도 손실 (12bit ADC를 float로) | int 단위 우선, 마지막에 변환 |
| 3 | 센서 disconnect → NaN | 검증 가드 |

### Ch 32 — RTOS

| # | 위험 | 회피 |
|---|------|------|
| 1 | 우선순위 역전 | 우선순위 상속 mutex |
| 2 | 스택 오버플로 (작은 task) | -fstack-usage 분석 |
| 3 | malloc / new 사용 | 정적 풀 |
| 4 | mutex deadlock (인터럽트 vs task) | 우선순위 명확화 |

---

## Ch 33 — 데이터 포맷 (이번 챕터)

| # | 위험 | 발현 | 회피 |
|---|------|------|------|
| 1 | string_view를 임시 string에서 만듦 | UB (zombie view) | 원본 수명 명시 + lifetime extension 안 의존 |
| 2 | 4GB CSV를 string으로 통째 로드 | OOM, 32-bit는 즉시 bad_alloc | 스트리밍 파서, mmap |
| 3 | nlohmann::json deep copy | 큰 트리 복사 비용 폭발 | std::move, const& 전달 |
| 4 | JSON 깊이 제한 없음 | 스택 오버플로 / DoS | depth 카운터 |
| 5 | YAML billion-laughs (anchor 폭탄) | 노드 폭증, OOM | 노드 수 / 깊이 제한 |
| 6 | UTF-8 BOM 미처리 | 첫 키 미스매치 | BOM 검출 후 스킵 |
| 7 | locale 의존 strtod | "1,5" 파싱 다름 | from_chars |
| 8 | INI 같은 키 중복 정책 | 데이터 손실 | 명시적 정책 |
| 9 | 큰 multiline 스칼라 | 메모리 폭발 | streaming |
| 10 | regex로 CSV 파싱 시도 | 백트래킹 폭주 | 상태머신 파서 |

## Ch 34 — 네트워크 계층

| # | 위험 | 발현 | 회피 |
|---|------|------|------|
| 1 | partial recv 미처리 | 메시지 일부만 받고 망가짐 | 길이 prefix 프레이밍 |
| 2 | RAII 없는 socket | 예외 경로에 fd 누수 | RAII Socket |
| 3 | sockaddr_in으로 IPv6 처리 | 8 바이트 truncate | sockaddr_storage (128) |
| 4 | epoll edge-triggered + read 한 번 | 다음 이벤트 안 옴, 데드락 | EAGAIN까지 read |
| 5 | 콜백 캡처 vs 소켓 객체 수명 | use-after-free | enable_shared_from_this |
| 6 | TLS X509/SSL/BIO 누수 | 메모리 누수 | unique_ptr custom deleter |
| 7 | recv 0 = 정상 종료 (에러 X) | 버그 처리 | 명시적 종료 분기 |
| 8 | EINTR 미재시도 | 시그널로 끊김 | 재시도 루프 |
| 9 | SIGPIPE → 프로세스 종료 | EPIPE처럼 처리 못 함 | MSG_NOSIGNAL / signal(SIGPIPE, SIG_IGN) |
| 10 | DoS: 길이 prefix 4GB | 즉시 bad_alloc | max 크기 강제 |
| 11 | UDP 단편화 (>MTU) | 일부 분실 시 전체 무효 | 1280 이하 권장 |
| 12 | TIME_WAIT 누적 | ephemeral 포트 고갈 | SO_REUSEADDR / 짧은 대기 |
| 13 | Nagle + Delayed ACK | 200ms 지연 (인터랙티브 망함) | TCP_NODELAY |

## Ch 35 — 산업용 프로토콜

| # | 위험 | 발현 | 회피 |
|---|------|------|------|
| 1 | malloc / new in 실시간 루프 | μs spike, 결정성 깨짐 | 사전 할당, 풀 |
| 2 | ISR에서 std::queue / mutex | 데드락, UB | lock-free SPSC ring |
| 3 | DMA + CPU 캐시 미일관 | 스테일 데이터 / corruption | cache flush/invalidate |
| 4 | DMA 버퍼 정렬 미준수 | hardfault | alignas(32) |
| 5 | 32bit float endian 4가지 | 잘못된 값 | byte/word swap 옵션 |
| 6 | 16→32bit sign 미확장 | 음수 → 큰 양수 | int16_t로 받아 변환 |
| 7 | Modbus RTU silent gap < 200μs | 일반 OS 시리얼 무리 | DMA + timer |
| 8 | watchdog 누락 | 통신 끊겨도 출력 유지 | timeout 안전 상태 |
| 9 | volatile 잘못된 사용 (멀티스레드) | race | atomic 사용 |
| 10 | mlock 누락 → page fault | μs spike | mlockall |
| 11 | OPC UA UA_Variant_clear 누락 | 누수 | RAII 래퍼 |
| 12 | MQTT inflight 큐 무한 | 오프라인에 메모리 폭증 | 디스크 spool / 한도 |
| 13 | CAN bus-off 미감지 | 통신 영구 끊김 | 에러 카운터 모니터링 |

## Ch 36 — Docker for C++

| # | 위험 | 발현 | 회피 |
|---|------|------|------|
| 1 | cgroup memory limit 인식 못 함 | OOM kill | /sys/fs/cgroup 직접 읽기 |
| 2 | hardware_concurrency() = host 코어 | 컨테이너 limit 무시 | sched_getaffinity |
| 3 | glibc malloc 단편화 | RSS 무한 증가 | jemalloc LD_PRELOAD |
| 4 | ASan + 작은 컨테이너 | OOM 즉사 | --memory=8g |
| 5 | musl libc + glibc 가정 코드 | DNS / regex 미세 차이 | 검증 |
| 6 | scratch + 동적 링크 | 실행 안 됨 | 정적 링크 |
| 7 | 정적 LGPL 위반 | 라이선스 문제 | 동의 / 별도 라이선스 |
| 8 | core dump 비활성 | 디버깅 불가 | --ulimit core=-1 |
| 9 | 운영에 sanitizer 켠 채 배포 | 메모리/성능 폭주 | Dockerfile target 분리 |
| 10 | fork-exec → COW로 RSS 2배 | OOM | posix_spawn |
| 11 | 심볼 stripped → trace 무용 | 디버깅 무력 | .debug 별도 보관 |
| 12 | 컨테이너 안 root 실행 | 침투 시 escape | USER nonroot |

## Ch 37 — ML 추론 런타임 (LibTorch / ORT / TRT / OpenVINO)

### 공통 메모리 함정

| # | 위험 | 발현 | 회피 |
|---|------|------|------|
| 1 | 추론 루프 내부 cudaMalloc/free | ms 단위 spike, 단편화 | arena/pool, 사전 할당 |
| 2 | 비동기 실행 중 입출력 버퍼 free | 비결정적 corruption / NaN | stream synchronize 후 free |
| 3 | pageable host memory로 H2D | DMA 못 써서 2배 느림 | cudaMallocHost (pinned) |
| 4 | 워크스페이스 너무 큼 | GPU OOM | 운영 GPU에 맞춰 1~4GB |
| 5 | 워크스페이스 너무 작음 | 느린 커널 선택 | trtexec --workspace 늘림 |
| 6 | 첫 추론으로 SLA 측정 | 지연 100배 | warmup N회 후 측정 |
| 7 | dynamic shape 매번 재할당 | latency 변동, 단편화 | shape 한정 / max로 사전 |
| 8 | 동일 모델 weight 중복 로드 | GPU 메모리 N배 | Engine 공유 + Context별 분리 |
| 9 | 양자화 calibration 분포 미일치 | 정확도 폭락 | 운영 데이터 분포 그대로 |
| 10 | Tensor 외부 버퍼 수명 부족 | UB / stale | 추론 끝까지 살리거나 clone |
| 11 | autograd 그래프 누적 (LibTorch) | OOM | NoGradGuard |
| 12 | 멀티스레드 IoBinding 공유 (ORT) | race / corruption | binding은 스레드별 |
| 13 | TRT context 공유 멀티스레드 | UB | 1 engine + N context |
| 14 | NaN 입력 → NaN 전파 | 출력 무의미 | 입력 sanitize |
| 15 | GPU memory leak는 valgrind 못 잡음 | 누적 OOM | compute-sanitizer / nvidia-smi |
| 16 | Unified memory (Managed) | 페이지 폴트로 비결정적 | 명시적 cudaMalloc + memcpy |
| 17 | 모델 로드 시점 메모리 2배 | 임시로 weight 2개 동시 | streaming load API 활용 |
| 18 | INT8 calibration 중 메모리 폭증 | OOM during 빌드 | 큰 GPU에서 빌드 후 deploy |
| 19 | 비동기 callback 스택에 lambda 캡처 | use-after-free | shared_ptr 캡처 |
| 20 | 멀티 GPU P2P 복사 | NVLink 없으면 매우 느림 | 같은 GPU에 task 묶기 |

### LibTorch 특화

| # | 위험 | 회피 |
|---|------|------|
| L1 | from_blob 외부 데이터 수명 | clone() 또는 외부 lifetime 관리 |
| L2 | Tensor::operator= = view 공유 | clone() 명시 |
| L3 | autograd ON 추론 → OOM | NoGradGuard |
| L4 | Module 복사 시 가중치 deep copy | shared_ptr<Module> |
| L5 | cudaCachingAllocator lazy free | 다른 텐서 못 잡으면 empty_cache() |

### ONNX Runtime 특화

| # | 위험 | 회피 |
|---|------|------|
| O1 | Env 다중 생성 | 프로세스당 1개 |
| O2 | 외부 버퍼 텐서 수명 | Run() 끝날 때까지 보장 |
| O3 | dynamic shape + MemPattern 켬 | dynamic이면 끔 |
| O4 | EP 누락 → 자동 fallback 안 함 | 명시적 추가 |
| O5 | TRT EP 빌드 매번 | trt_engine_cache_path 설정 |

### TensorRT 특화

| # | 위험 | 회피 |
|---|------|------|
| T1 | engine 다른 GPU/드라이버 | 환경별 빌드 또는 prebuild matrix |
| T2 | binding 잘못된 인덱스 | getBindingIndex로 이름 매핑 |
| T3 | enqueue 후 binding 해제 | stream sync 필수 |
| T4 | INT8 calibration 다른 분포 | 운영 데이터 |
| T5 | RAII 누락 | unique_ptr custom deleter |
| T6 | optimization profile 미설정 → 동적 입력 X | trtexec min/opt/max shapes |

### OpenVINO 특화

| # | 위험 | 회피 |
|---|------|------|
| V1 | compile_model 매번 | cache_dir 활성 |
| V2 | NUMA 무시 | scheduling_core_type / numactl |
| V3 | 외부 input tensor 수명 | infer() 끝까지 |
| V4 | NPU 메모리 별도 공간 | 작은 모델일수록 NPU 유리 |
| V5 | 전처리 외부 OpenCV | PrePostProcessor로 그래프 통합 |

---

## 도구 모음

**정적 분석**
- clang-tidy (`bugprone-*`, `cert-*`, `cppcoreguidelines-*`)
- cppcheck
- PVS-Studio (상용)
- include-what-you-use (IWYU)

**런타임 검증**
- AddressSanitizer (ASan)
- UndefinedBehaviorSanitizer (UBSan)
- ThreadSanitizer (TSan)
- MemorySanitizer (MSan, clang)
- valgrind (memcheck, helgrind)

**프로파일링**
- perf, perf flamegraph
- jemalloc heap profile (jeprof)
- Tracy / chrome-trace
- Intel VTune (상용)

**설계 가이드라인**
- C++ Core Guidelines (Bjarne / Sutter)
- MISRA C++ 2008 / AUTOSAR C++14 (산업 안전)
- CERT C++ Secure Coding

---

이 문서를 기반으로 자기 코드를 리뷰할 때, 해당 챕터의 함정 표를 한 번 훑고
컴파일/CI에 sanitizer를 켜면 80%의 메모리 버그는 자동으로 잡힙니다.
나머지 20%는 정적 분석 + 코드 리뷰 + 운영 모니터링의 영역.
