/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C++ 학습 27단계: 시스템 프로그래밍 & 비트 조작
  ─ Systems Programming & Bit Manipulation ─

  이 파일 하나로 비트 연산, 비트 조작 기법, 비트 필드, 엔디안,
  메모리 정렬, volatile, 그리고 실전 활용 예제를 모두 배웁니다.

  ■ 컴파일 방법 (터미널에 입력)
    Windows (MinGW) : g++ -std=c++17 -Wall -o 27_systems.exe main.cpp
    Windows (MSVC)  : cl /EHsc /std:c++17 /W4 main.cpp
    Linux / Mac     : g++ -std=c++17 -Wall -o 27_systems main.cpp

  ■ 실행 방법
    Windows : .\27_systems.exe
    Linux   : ./27_systems

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#include <iostream>
#include <cstdint>      // uint8_t, uint16_t, uint32_t 등 고정 크기 정수
#include <bitset>       // 이진수 표현을 위한 bitset
#include <cstring>      // memcpy
#include <iomanip>      // setw, setfill
#include <string>
#include <sstream>
#include <array>
#include <cassert>
#include <type_traits>  // underlying_type

using namespace std;


// =========================================================================
//  레슨 1: 비트 연산 기초
//  ─ AND, OR, XOR, NOT, 시프트, 실전 활용 (플래그, 권한 관리) ─
// =========================================================================
//
//  ┌──────────────────────────────────────────────────────────────────────┐
//  │  컴퓨터는 모든 데이터를 0과 1(비트)로 저장합니다.                    │
//  │  비트 연산은 이 0과 1을 직접 조작하는 가장 저수준 연산입니다.         │
//  │                                                                      │
//  │  비트 연산자 요약:                                                   │
//  │  ─────────────────────────────────────────────────────────────────── │
//  │  연산자   기호   설명                  예시 (4비트)                   │
//  │  ─────── ───── ──────────────────── ────────────────────            │
//  │  AND      &     둘 다 1이면 1        1010 & 1100 = 1000             │
//  │  OR       |     하나라도 1이면 1     1010 | 1100 = 1110             │
//  │  XOR      ^     다르면 1             1010 ^ 1100 = 0110             │
//  │  NOT      ~     비트 반전            ~1010 = 0101                    │
//  │  LEFT <<  <<    왼쪽 시프트(×2)      0011 << 1 = 0110               │
//  │  RIGHT >> >>    오른쪽 시프트(÷2)    1100 >> 1 = 0110               │
//  └──────────────────────────────────────────────────────────────────────┘
//
//  ■ 핵심 진리표 (Truth Table):
//
//     A  B  │ A&B  A|B  A^B  ~A
//    ───────┼─────────────────────
//     0  0  │  0    0    0    1
//     0  1  │  0    1    1    1
//     1  0  │  0    1    1    0
//     1  1  │  1    1    0    0
//

void lesson1_bit_operations_basics() {
    cout << "=== 레슨 1: 비트 연산 기초 ===\n\n";

    // ── 1.1 기본 비트 연산 ──
    uint8_t a = 0b1010;  // 10 (이진수 1010)
    uint8_t b = 0b1100;  // 12 (이진수 1100)

    cout << "a = " << bitset<8>(a) << " (" << (int)a << ")\n";
    cout << "b = " << bitset<8>(b) << " (" << (int)b << ")\n\n";

    // AND: 둘 다 1인 비트만 1
    // 용도: 특정 비트가 켜져 있는지 확인 (마스킹)
    cout << "a & b  = " << bitset<8>(a & b) << " (AND - 공통 비트 추출)\n";

    // OR: 하나라도 1이면 1
    // 용도: 비트를 켜기 (설정)
    cout << "a | b  = " << bitset<8>(a | b) << " (OR  - 비트 합치기)\n";

    // XOR: 다른 비트만 1
    // 용도: 비트 토글, 암호화, 두 값 교환
    cout << "a ^ b  = " << bitset<8>(a ^ b) << " (XOR - 차이점 찾기)\n";

    // NOT: 모든 비트 반전
    cout << "~a     = " << bitset<8>(static_cast<uint8_t>(~a)) << " (NOT - 비트 반전)\n";

    // 왼쪽 시프트: 2를 곱하는 효과
    cout << "a << 1 = " << bitset<8>(a << 1) << " (LEFT SHIFT - ×2)\n";

    // 오른쪽 시프트: 2로 나누는 효과
    cout << "a >> 1 = " << bitset<8>(a >> 1) << " (RIGHT SHIFT - ÷2)\n";

    // ── 1.2 실전 활용: 파일 권한 시스템 ──
    //
    //  유닉스 파일 권한 모델 (rwxrwxrwx):
    //
    //   비트 위치:  8  7  6  5  4  3  2  1  0
    //   의미:       r  w  x  r  w  x  r  w  x
    //              ─────── ─────── ───────
    //              소유자   그룹    기타
    //
    //   rwxr-xr-- = 111 101 100 = 0754 (8진수)
    //
    cout << "\n── 파일 권한 시스템 예제 ──\n";

    constexpr uint16_t OWNER_READ  = 0400;  // 소유자 읽기
    constexpr uint16_t OWNER_WRITE = 0200;  // 소유자 쓰기
    constexpr uint16_t OWNER_EXEC  = 0100;  // 소유자 실행
    constexpr uint16_t GROUP_READ  = 0040;  // 그룹 읽기
    constexpr uint16_t GROUP_EXEC  = 0010;  // 그룹 실행
    constexpr uint16_t OTHER_READ  = 0004;  // 기타 읽기

    // 권한 설정: OR로 여러 권한 결합
    uint16_t permissions = OWNER_READ | OWNER_WRITE | OWNER_EXEC
                         | GROUP_READ | GROUP_EXEC
                         | OTHER_READ;
    cout << "권한: " << oct << permissions << dec << " (8진수)\n";

    // 권한 확인: AND로 특정 권한 검사
    if (permissions & OWNER_WRITE) {
        cout << "  -> 소유자 쓰기 권한 있음!\n";
    }

    // 권한 제거: AND + NOT으로 특정 비트 끄기
    permissions &= ~OWNER_WRITE;  // 소유자 쓰기 권한 제거
    cout << "쓰기 권한 제거 후: " << oct << permissions << dec << "\n";

    // 권한 토글: XOR로 토글
    permissions ^= OWNER_EXEC;  // 실행 권한 토글
    cout << "실행 권한 토글 후: " << oct << permissions << dec << "\n";

    // ── 1.3 XOR 스왑 (임시 변수 없이 두 값 교환) ──
    cout << "\n── XOR 스왑 ──\n";
    int x = 42, y = 99;
    cout << "교환 전: x=" << x << ", y=" << y << "\n";
    x ^= y;   // x = x ^ y
    y ^= x;   // y = y ^ (x ^ y) = 원래 x
    x ^= y;   // x = (x ^ y) ^ 원래 x = 원래 y
    cout << "교환 후: x=" << x << ", y=" << y << "\n";

    cout << "\n";
}


// =========================================================================
//  레슨 2: 비트 조작 테크닉
//  ─ n번째 비트 설정/해제/토글/확인, 비트 카운팅, 2의 거듭제곱 판별 ─
// =========================================================================
//
//  ┌──────────────────────────────────────────────────────────────────────┐
//  │  비트 조작 핵심 공식 (0-indexed, n번째 비트):                        │
//  │                                                                      │
//  │  ● 비트 설정 (SET)     :  value |=  (1 << n)                        │
//  │  ● 비트 해제 (CLEAR)   :  value &= ~(1 << n)                       │
//  │  ● 비트 토글 (TOGGLE)  :  value ^=  (1 << n)                       │
//  │  ● 비트 확인 (CHECK)   :  value &   (1 << n)                       │
//  │                                                                      │
//  │  ● 2의 거듭제곱 판별   :  (n & (n-1)) == 0  (n > 0)                │
//  │  ● 최하위 설정 비트    :  n & (-n)                                  │
//  │  ● 최하위 비트 끄기    :  n & (n-1)                                 │
//  └──────────────────────────────────────────────────────────────────────┘
//

void lesson2_bit_manipulation_techniques() {
    cout << "=== 레슨 2: 비트 조작 테크닉 ===\n\n";

    // ── 2.1 n번째 비트 조작 ──
    uint8_t value = 0b00000000;
    cout << "초기값: " << bitset<8>(value) << "\n";

    // 3번째 비트 설정 (SET) - 0부터 시작
    value |= (1 << 3);
    cout << "3번 비트 SET:   " << bitset<8>(value) << "\n";  // 00001000

    // 5번째 비트 설정
    value |= (1 << 5);
    cout << "5번 비트 SET:   " << bitset<8>(value) << "\n";  // 00101000

    // 3번째 비트 확인 (CHECK)
    bool is_set = (value & (1 << 3)) != 0;
    cout << "3번 비트 CHECK: " << (is_set ? "켜짐" : "꺼짐") << "\n";

    // 3번째 비트 토글 (TOGGLE)
    value ^= (1 << 3);
    cout << "3번 비트 TOGGLE: " << bitset<8>(value) << "\n"; // 00100000

    // 5번째 비트 해제 (CLEAR)
    value &= ~(1 << 5);
    cout << "5번 비트 CLEAR: " << bitset<8>(value) << "\n";  // 00000000

    // ── 2.2 비트 카운팅 (popcount - population count) ──
    //
    //  설정된 비트(1의 개수)를 세는 여러 방법:
    //
    //  방법 1: Brian Kernighan의 알고리즘
    //          n & (n-1)은 최하위 설정 비트를 하나씩 끕니다.
    //
    //          예시: n = 0b10110100
    //          반복 1: 10110100 & 10110011 = 10110000 (count=1)
    //          반복 2: 10110000 & 10101111 = 10100000 (count=2)
    //          반복 3: 10100000 & 10011111 = 10000000 (count=3)
    //          반복 4: 10000000 & 01111111 = 00000000 (count=4)
    //
    cout << "\n── 비트 카운팅 ──\n";

    auto count_bits_kernighan = [](uint32_t n) -> int {
        int count = 0;
        while (n) {
            n &= (n - 1);  // 최하위 설정 비트 제거
            count++;
        }
        return count;
    };

    uint32_t test_val = 0b10110100;
    cout << bitset<8>(test_val) << "의 1의 개수: "
         << count_bits_kernighan(test_val) << "\n";

    // 방법 2: C++20의 __builtin_popcount (GCC/Clang)
    // C++20부터는 <bit> 헤더의 popcount 사용 가능
    cout << "__builtin_popcount(0xFF): " << __builtin_popcount(0xFF) << "\n";

    // ── 2.3 2의 거듭제곱 판별 ──
    //
    //  2의 거듭제곱: 비트가 정확히 하나만 1
    //  1 = 0001, 2 = 0010, 4 = 0100, 8 = 1000
    //
    //  n & (n-1) == 0 이면 2의 거듭제곱!
    //  (단, n > 0 이어야 함)
    //
    //  예시: 8  = 1000
    //        7  = 0111
    //        8 & 7 = 0000  →  2의 거듭제곱!
    //
    //        6  = 0110
    //        5  = 0101
    //        6 & 5 = 0100  →  2의 거듭제곱 아님!
    //
    cout << "\n── 2의 거듭제곱 판별 ──\n";

    auto is_power_of_two = [](uint32_t n) -> bool {
        return n > 0 && (n & (n - 1)) == 0;
    };

    for (uint32_t i : {0u, 1u, 2u, 3u, 4u, 7u, 8u, 16u, 15u, 32u, 100u}) {
        cout << setw(4) << i << " -> "
             << (is_power_of_two(i) ? "2의 거듭제곱" : "아님") << "\n";
    }

    // ── 2.4 최하위 설정 비트 (Lowest Set Bit) ──
    cout << "\n── 최하위 설정 비트 ──\n";
    uint8_t lsb_test = 0b01010100;  // 84
    uint8_t lowest = lsb_test & (-lsb_test);  // 최하위 설정 비트만 추출
    cout << "값: " << bitset<8>(lsb_test) << "\n";
    cout << "최하위 설정 비트: " << bitset<8>(lowest) << " (위치: "
         << __builtin_ctz(lsb_test) << ")\n";

    cout << "\n";
}


// =========================================================================
//  레슨 3: 비트 필드와 비트마스크
//  ─ struct 비트 필드, enum class + 비트 플래그 패턴 ─
// =========================================================================
//
//  ┌──────────────────────────────────────────────────────────────────────┐
//  │  비트 필드(Bit Field): struct 멤버에 비트 단위 크기 지정             │
//  │                                                                      │
//  │  struct Color {                                                      │
//  │      uint8_t red   : 3;  // 3비트 (0~7)                             │
//  │      uint8_t green : 3;  // 3비트 (0~7)                             │
//  │      uint8_t blue  : 2;  // 2비트 (0~3)                             │
//  │  };  // 총 8비트 = 1바이트!                                          │
//  │                                                                      │
//  │  메모리 레이아웃 (1바이트):                                          │
//  │  ┌─────┬───────┬───────┐                                            │
//  │  │blue │ green │  red  │                                             │
//  │  │ 2b  │  3b   │  3b   │                                             │
//  │  └─────┴───────┴───────┘                                            │
//  │  비트: 7  6   5  4  3   2  1  0                                      │
//  └──────────────────────────────────────────────────────────────────────┘
//

// 3.1 struct 비트 필드
struct CompactColor {
    uint8_t red   : 3;  // 3비트: 0~7 범위
    uint8_t green : 3;  // 3비트: 0~7 범위
    uint8_t blue  : 2;  // 2비트: 0~3 범위
};

// TCP 헤더 플래그 (실제 네트워크 프로그래밍에서 사용)
struct TCPFlags {
    uint8_t fin : 1;  // 연결 종료
    uint8_t syn : 1;  // 연결 시작
    uint8_t rst : 1;  // 연결 리셋
    uint8_t psh : 1;  // 푸시
    uint8_t ack : 1;  // 확인 응답
    uint8_t urg : 1;  // 긴급
    uint8_t ece : 1;  // ECN 에코
    uint8_t cwr : 1;  // 혼잡 윈도우 축소
};

// 3.2 enum class + 비트 플래그 패턴
//
//  enum class를 사용하면 타입 안전한 비트 플래그를 만들 수 있습니다.
//  연산자 오버로딩으로 비트 연산을 지원합니다.
//
enum class FilePermission : uint16_t {
    None       = 0,
    Read       = 1 << 0,   // 0001
    Write      = 1 << 1,   // 0010
    Execute    = 1 << 2,   // 0100
    Delete     = 1 << 3,   // 1000
    ReadWrite  = Read | Write,                    // 편의 조합
    All        = Read | Write | Execute | Delete  // 모든 권한
};

// enum class에 비트 연산자를 사용하려면 오버로딩 필요
inline FilePermission operator|(FilePermission a, FilePermission b) {
    using T = underlying_type_t<FilePermission>;
    return static_cast<FilePermission>(static_cast<T>(a) | static_cast<T>(b));
}
inline FilePermission operator&(FilePermission a, FilePermission b) {
    using T = underlying_type_t<FilePermission>;
    return static_cast<FilePermission>(static_cast<T>(a) & static_cast<T>(b));
}
inline FilePermission operator~(FilePermission a) {
    using T = underlying_type_t<FilePermission>;
    return static_cast<FilePermission>(~static_cast<T>(a));
}
inline FilePermission& operator|=(FilePermission& a, FilePermission b) {
    a = a | b; return a;
}
inline FilePermission& operator&=(FilePermission& a, FilePermission b) {
    a = a & b; return a;
}

// 권한이 있는지 확인하는 헬퍼 함수
inline bool has_permission(FilePermission perms, FilePermission check) {
    return (perms & check) == check;
}

void lesson3_bitfields_and_bitmasks() {
    cout << "=== 레슨 3: 비트 필드와 비트마스크 ===\n\n";

    // ── 3.1 비트 필드 사용 ──
    cout << "── CompactColor 비트 필드 ──\n";
    cout << "CompactColor 크기: " << sizeof(CompactColor) << " 바이트\n";

    CompactColor color;
    color.red   = 7;   // 최대 7 (3비트)
    color.green = 5;
    color.blue  = 3;   // 최대 3 (2비트)
    cout << "Red=" << (int)color.red
         << " Green=" << (int)color.green
         << " Blue=" << (int)color.blue << "\n";

    // ── TCP 플래그 ──
    cout << "\n── TCP 플래그 비트 필드 ──\n";
    cout << "TCPFlags 크기: " << sizeof(TCPFlags) << " 바이트\n";

    TCPFlags tcp_syn{};          // 모두 0으로 초기화
    tcp_syn.syn = 1;             // SYN 플래그 설정
    cout << "SYN 패킷: SYN=" << (int)tcp_syn.syn
         << " ACK=" << (int)tcp_syn.ack << "\n";

    TCPFlags tcp_synack{};
    tcp_synack.syn = 1;
    tcp_synack.ack = 1;
    cout << "SYN-ACK 패킷: SYN=" << (int)tcp_synack.syn
         << " ACK=" << (int)tcp_synack.ack << "\n";

    // ── 3.2 enum class 비트 플래그 ──
    cout << "\n── enum class 비트 플래그 패턴 ──\n";

    FilePermission user_perms = FilePermission::Read | FilePermission::Write;
    cout << "사용자 권한값: " << static_cast<uint16_t>(user_perms) << "\n";

    // 권한 확인
    cout << "읽기 권한: " << has_permission(user_perms, FilePermission::Read) << "\n";
    cout << "실행 권한: " << has_permission(user_perms, FilePermission::Execute) << "\n";

    // 권한 추가
    user_perms |= FilePermission::Execute;
    cout << "실행 권한 추가 후: " << has_permission(user_perms, FilePermission::Execute) << "\n";

    // 권한 제거
    user_perms &= ~FilePermission::Write;
    cout << "쓰기 권한 제거 후: " << has_permission(user_perms, FilePermission::Write) << "\n";

    cout << "\n";
}


// =========================================================================
//  레슨 4: 엔디안과 바이트 순서
//  ─ 빅/리틀 엔디안, 네트워크 바이트 순서, 바이트 스왑 ─
// =========================================================================
//
//  ┌──────────────────────────────────────────────────────────────────────┐
//  │  엔디안(Endianness): 멀티바이트 데이터의 바이트 저장 순서            │
//  │                                                                      │
//  │  예시: 0x12345678 (4바이트)                                         │
//  │                                                                      │
//  │  빅 엔디안 (Big-Endian):                                            │
//  │  메모리:  [0x12] [0x34] [0x56] [0x78]                               │
//  │  주소:     0      1      2      3                                    │
//  │  → 사람이 읽는 순서와 동일 (네트워크 표준)                           │
//  │                                                                      │
//  │  리틀 엔디안 (Little-Endian):                                       │
//  │  메모리:  [0x78] [0x56] [0x34] [0x12]                               │
//  │  주소:     0      1      2      3                                    │
//  │  → 낮은 주소에 하위 바이트 (x86/x64 CPU)                            │
//  │                                                                      │
//  │  ※ 네트워크 통신 시 항상 빅 엔디안(네트워크 바이트 순서)으로         │
//  │     변환해야 합니다! → htonl(), ntohl() 함수                        │
//  └──────────────────────────────────────────────────────────────────────┘
//

// 현재 시스템의 엔디안 확인
bool is_little_endian() {
    uint16_t test = 0x0001;
    uint8_t* byte_ptr = reinterpret_cast<uint8_t*>(&test);
    return byte_ptr[0] == 0x01;  // 첫 바이트가 하위 바이트면 리틀 엔디안
}

// 바이트 스왑 함수들
uint16_t swap_bytes_16(uint16_t value) {
    return (value >> 8) | (value << 8);
}

uint32_t swap_bytes_32(uint32_t value) {
    return ((value >> 24) & 0x000000FF) |
           ((value >>  8) & 0x0000FF00) |
           ((value <<  8) & 0x00FF0000) |
           ((value << 24) & 0xFF000000);
}

void lesson4_endianness() {
    cout << "=== 레슨 4: 엔디안과 바이트 순서 ===\n\n";

    // ── 4.1 시스템 엔디안 확인 ──
    cout << "현재 시스템: "
         << (is_little_endian() ? "리틀 엔디안" : "빅 엔디안") << "\n";

    // ── 4.2 메모리에 실제 저장되는 순서 확인 ──
    cout << "\n── 메모리 저장 순서 ──\n";
    uint32_t value = 0x12345678;
    uint8_t* bytes = reinterpret_cast<uint8_t*>(&value);

    cout << "값: 0x" << hex << value << dec << "\n";
    cout << "메모리 바이트 순서:\n";
    for (int i = 0; i < 4; i++) {
        cout << "  주소+" << i << ": 0x" << hex << setw(2) << setfill('0')
             << (int)bytes[i] << dec << "\n";
    }
    cout << setfill(' ');

    // ── 4.3 바이트 스왑 ──
    //
    //  네트워크 통신 시 바이트 순서 변환이 필수입니다.
    //  빅 엔디안 ↔ 리틀 엔디안 변환
    //
    cout << "\n── 바이트 스왑 ──\n";
    uint16_t port = 0x1F90;  // 포트 8080
    cout << "원본 (16비트): 0x" << hex << port
         << " -> 스왑: 0x" << swap_bytes_16(port) << dec << "\n";

    uint32_t ip = 0xC0A80001;  // 192.168.0.1
    cout << "원본 (32비트): 0x" << hex << ip
         << " -> 스왑: 0x" << swap_bytes_32(ip) << dec << "\n";

    // ── 4.4 GCC/Clang 내장 바이트 스왑 ──
    cout << "\n── 컴파일러 내장 바이트 스왑 ──\n";
    uint32_t original = 0xAABBCCDD;
    uint32_t swapped = __builtin_bswap32(original);
    cout << "원본: 0x" << hex << original
         << " -> __builtin_bswap32: 0x" << swapped << dec << "\n";

    cout << "\n";
}


// =========================================================================
//  레슨 5: 메모리 정렬과 패딩
//  ─ alignas, alignof, struct 패딩, #pragma pack ─
// =========================================================================
//
//  ┌──────────────────────────────────────────────────────────────────────┐
//  │  CPU는 메모리에서 데이터를 읽을 때 "정렬된" 주소에서 더 빠르게       │
//  │  읽을 수 있습니다.                                                   │
//  │                                                                      │
//  │  정렬 규칙: 타입의 크기가 N이면, N의 배수 주소에 배치               │
//  │    char  (1바이트) → 아무 주소                                       │
//  │    short (2바이트) → 2의 배수 주소                                   │
//  │    int   (4바이트) → 4의 배수 주소                                   │
//  │    double(8바이트) → 8의 배수 주소                                   │
//  │                                                                      │
//  │  struct 패딩 예시:                                                   │
//  │                                                                      │
//  │  struct Bad {       메모리:                                          │
//  │    char  a;  1B     [a][P][P][P]  ← 3바이트 패딩                    │
//  │    int   b;  4B     [b][b][b][b]                                     │
//  │    char  c;  1B     [c][P][P][P]  ← 3바이트 패딩                    │
//  │  };  // 총 12바이트!  (실제 데이터: 6바이트)                         │
//  │                                                                      │
//  │  struct Good {      메모리:                                          │
//  │    int   b;  4B     [b][b][b][b]                                     │
//  │    char  a;  1B     [a]                                              │
//  │    char  c;  1B     [c][P][P]    ← 2바이트 패딩                     │
//  │  };  // 총 8바이트!  (멤버 순서만 바꿔도 절약)                       │
//  └──────────────────────────────────────────────────────────────────────┘
//

struct BadLayout {
    char  a;   // 1바이트 + 3바이트 패딩
    int   b;   // 4바이트
    char  c;   // 1바이트 + 3바이트 패딩
};  // 총 12바이트

struct GoodLayout {
    int   b;   // 4바이트
    char  a;   // 1바이트
    char  c;   // 1바이트 + 2바이트 패딩
};  // 총 8바이트

// #pragma pack으로 패딩 제거 (주의: 성능 저하 가능!)
#pragma pack(push, 1)
struct PackedLayout {
    char  a;   // 1바이트
    int   b;   // 4바이트 (패딩 없음!)
    char  c;   // 1바이트
};  // 총 6바이트
#pragma pack(pop)

// alignas로 특정 정렬 요구
struct alignas(64) CacheAligned {
    int data[4];
};  // 64바이트 경계에 정렬 (캐시 라인 크기)

void lesson5_memory_alignment() {
    cout << "=== 레슨 5: 메모리 정렬과 패딩 ===\n\n";

    // ── 5.1 struct 크기 비교 ──
    cout << "── struct 크기 비교 ──\n";
    cout << "BadLayout  크기: " << sizeof(BadLayout)  << " 바이트 (비효율적 배치)\n";
    cout << "GoodLayout 크기: " << sizeof(GoodLayout) << " 바이트 (효율적 배치)\n";
    cout << "PackedLayout 크기: " << sizeof(PackedLayout) << " 바이트 (패딩 제거)\n";

    // ── 5.2 alignof - 타입의 정렬 요구사항 확인 ──
    cout << "\n── 타입별 정렬 요구사항 (alignof) ──\n";
    cout << "char:    alignof = " << alignof(char) << "\n";
    cout << "short:   alignof = " << alignof(short) << "\n";
    cout << "int:     alignof = " << alignof(int) << "\n";
    cout << "double:  alignof = " << alignof(double) << "\n";
    cout << "int*:    alignof = " << alignof(int*) << "\n";

    // ── 5.3 alignas - 커스텀 정렬 ──
    cout << "\n── 캐시 정렬 (alignas) ──\n";
    cout << "CacheAligned 크기: " << sizeof(CacheAligned) << " 바이트\n";
    cout << "CacheAligned 정렬: " << alignof(CacheAligned) << " 바이트\n";

    CacheAligned aligned_data;
    cout << "실제 주소: " << &aligned_data << "\n";
    cout << "64바이트 정렬 여부: "
         << ((reinterpret_cast<uintptr_t>(&aligned_data) % 64 == 0) ? "예" : "아니오")
         << "\n";

    // ── 5.4 멤버 오프셋 확인 ──
    cout << "\n── BadLayout 멤버 오프셋 ──\n";
    BadLayout bad{};
    cout << "a의 오프셋: " << (reinterpret_cast<char*>(&bad.a) - reinterpret_cast<char*>(&bad)) << "\n";
    cout << "b의 오프셋: " << (reinterpret_cast<char*>(&bad.b) - reinterpret_cast<char*>(&bad)) << "\n";
    cout << "c의 오프셋: " << (reinterpret_cast<char*>(&bad.c) - reinterpret_cast<char*>(&bad)) << "\n";

    cout << "\n";
}


// =========================================================================
//  레슨 6: volatile과 하드웨어 레지스터
//  ─ volatile 키워드, memory-mapped I/O 개념 ─
// =========================================================================
//
//  ┌──────────────────────────────────────────────────────────────────────┐
//  │  volatile: "이 변수는 프로그램 외부에서 바뀔 수 있으니                │
//  │             최적화하지 마세요!" 라고 컴파일러에게 알리는 키워드        │
//  │                                                                      │
//  │  사용 사례:                                                          │
//  │  1. 하드웨어 레지스터 (Memory-Mapped I/O)                            │
//  │  2. 인터럽트 서비스 루틴(ISR)에서 수정되는 변수                      │
//  │  3. 신호 핸들러(signal handler)에서 수정되는 변수                    │
//  │                                                                      │
//  │  ※ volatile은 멀티스레드 동기화에 사용하면 안 됩니다!               │
//  │     (C++에서는 std::atomic을 사용하세요)                             │
//  │                                                                      │
//  │  Memory-Mapped I/O 개념도:                                          │
//  │  ┌────────────┐    주소 버스     ┌────────────┐                     │
//  │  │   CPU      │──────────────→│  메모리      │                     │
//  │  │            │    데이터 버스   │  0x0000~    │                     │
//  │  │            │←─────────────→│  0x7FFF      │                     │
//  │  │            │                 ├────────────┤                     │
//  │  │            │──────────────→│ I/O 장치    │                     │
//  │  │            │←─────────────→│ 0x8000~     │                     │
//  │  └────────────┘                 └────────────┘                     │
//  │                                                                      │
//  │  특정 메모리 주소에 읽기/쓰기 → 하드웨어 장치와 통신                │
//  └──────────────────────────────────────────────────────────────────────┘
//

// 시뮬레이션용 하드웨어 레지스터 (실제로는 메모리 매핑된 주소)
struct HardwareTimer {
    volatile uint32_t control;     // 제어 레지스터
    volatile uint32_t counter;     // 카운터 (하드웨어가 자동 증가)
    volatile uint32_t status;      // 상태 레지스터 (하드웨어가 설정)
};

// volatile이 필요한 이유를 보여주는 예제
volatile bool interrupt_flag = false;  // ISR에서 설정될 수 있는 플래그

void lesson6_volatile_and_hardware() {
    cout << "=== 레슨 6: volatile과 하드웨어 레지스터 ===\n\n";

    // ── 6.1 volatile의 효과 ──
    //
    //  volatile이 없으면:
    //    컴파일러가 "이 변수는 루프 안에서 안 바뀌네?" → 최적화
    //    while (flag == false) { }  →  if (flag == false) while(true) { }
    //
    //  volatile이 있으면:
    //    매번 메모리에서 값을 새로 읽어옴 → 외부 변경 감지 가능
    //
    cout << "── volatile 키워드 설명 ──\n";
    cout << "volatile은 컴파일러 최적화를 방지합니다.\n";
    cout << "매번 메모리에서 실제 값을 읽어옵니다.\n\n";

    // ── 6.2 Memory-Mapped I/O 시뮬레이션 ──
    cout << "── Memory-Mapped I/O 시뮬레이션 ──\n";

    // 실제 임베디드에서는: volatile uint32_t* timer = (uint32_t*)0x40000000;
    // 여기서는 일반 메모리로 시뮬레이션
    uint32_t fake_hw_memory[3] = {0, 0, 0};
    volatile uint32_t* control = &fake_hw_memory[0];
    volatile uint32_t* counter = &fake_hw_memory[1];
    volatile uint32_t* status  = &fake_hw_memory[2];

    // 레지스터 비트 정의
    constexpr uint32_t TIMER_ENABLE  = (1 << 0);  // 비트 0: 타이머 활성화
    constexpr uint32_t TIMER_IRQ_EN  = (1 << 1);  // 비트 1: 인터럽트 활성화
    constexpr uint32_t TIMER_ONESHOT = (1 << 2);  // 비트 2: 원샷 모드
    constexpr uint32_t STATUS_DONE   = (1 << 0);  // 비트 0: 완료 플래그

    // 타이머 설정
    *control = TIMER_ENABLE | TIMER_IRQ_EN;  // 활성화 + 인터럽트 켜기
    *counter = 1000;                          // 카운터 초기값
    cout << "제어 레지스터: 0b" << bitset<8>(*control) << "\n";
    cout << "카운터 값: " << *counter << "\n";

    // 하드웨어가 완료했다고 가정 (시뮬레이션)
    fake_hw_memory[2] = STATUS_DONE;

    // 상태 확인 (volatile이므로 매번 실제 메모리 읽기)
    if (*status & STATUS_DONE) {
        cout << "타이머 완료! (상태 레지스터 확인)\n";
        *status = 0;  // 상태 클리어
    }

    // ── 6.3 volatile과 const의 조합 ──
    cout << "\n── volatile const 조합 ──\n";
    cout << "volatile const: 우리는 못 바꾸지만, 하드웨어가 바꿀 수 있는 값\n";
    cout << "예: const volatile uint32_t* read_only_reg = ...;\n";
    cout << "    읽기 전용 상태 레지스터에 사용\n";

    cout << "\n";
}


// =========================================================================
//  레슨 7: 실전 예제
//  ─ 비트맵 이미지 헤더, IP 주소 조작, 체크섬, 비트보드 ─
// =========================================================================

// ── 7.1 BMP 이미지 헤더 파싱 (비트맵 파일 구조) ──
//
//  BMP 파일 구조:
//  ┌─────────────────────────────────────────────┐
//  │ File Header (14바이트)                       │
//  │  - 매직 넘버: 'BM' (0x42, 0x4D)            │
//  │  - 파일 크기 (4바이트)                      │
//  │  - 예약 (4바이트)                           │
//  │  - 데이터 오프셋 (4바이트)                  │
//  ├─────────────────────────────────────────────┤
//  │ Info Header (40바이트, BITMAPINFOHEADER)     │
//  │  - 헤더 크기 (4바이트)                      │
//  │  - 너비 (4바이트)                           │
//  │  - 높이 (4바이트)                           │
//  │  - 색상 평면 (2바이트)                      │
//  │  - 비트 깊이 (2바이트)                      │
//  │  ...                                         │
//  ├─────────────────────────────────────────────┤
//  │ 픽셀 데이터                                  │
//  └─────────────────────────────────────────────┘
//

#pragma pack(push, 1)
struct BMPFileHeader {
    uint16_t signature;      // 'BM' = 0x4D42
    uint32_t file_size;      // 파일 전체 크기
    uint16_t reserved1;
    uint16_t reserved2;
    uint32_t data_offset;    // 픽셀 데이터 시작 오프셋
};

struct BMPInfoHeader {
    uint32_t header_size;    // 이 헤더의 크기 (40)
    int32_t  width;          // 이미지 너비 (픽셀)
    int32_t  height;         // 이미지 높이 (픽셀)
    uint16_t planes;         // 색상 평면 수 (항상 1)
    uint16_t bit_depth;      // 비트 깊이 (1, 4, 8, 16, 24, 32)
    uint32_t compression;    // 압축 방식 (0 = 없음)
    uint32_t image_size;     // 이미지 데이터 크기
    int32_t  x_ppm;          // 수평 해상도
    int32_t  y_ppm;          // 수직 해상도
    uint32_t colors_used;
    uint32_t colors_important;
};
#pragma pack(pop)

// ── 7.2 IP 주소 조작 ──
//
//  IPv4 주소: 32비트 정수로 표현
//
//  192.168.1.100 = 0xC0A80164
//
//  ┌──────────┬──────────┬──────────┬──────────┐
//  │   192    │   168    │    1     │   100    │
//  │ 비트31-24│ 비트23-16│ 비트15-8 │ 비트7-0  │
//  └──────────┴──────────┴──────────┴──────────┘
//

uint32_t ip_to_uint32(uint8_t a, uint8_t b, uint8_t c, uint8_t d) {
    return (static_cast<uint32_t>(a) << 24) |
           (static_cast<uint32_t>(b) << 16) |
           (static_cast<uint32_t>(c) << 8)  |
           static_cast<uint32_t>(d);
}

string uint32_to_ip(uint32_t ip) {
    ostringstream oss;
    oss << ((ip >> 24) & 0xFF) << "."
        << ((ip >> 16) & 0xFF) << "."
        << ((ip >> 8)  & 0xFF) << "."
        << (ip & 0xFF);
    return oss.str();
}

// 서브넷 마스크로 네트워크/호스트 분리
void analyze_subnet(uint32_t ip, uint32_t mask) {
    uint32_t network = ip & mask;       // 네트워크 주소
    uint32_t host    = ip & ~mask;      // 호스트 주소
    uint32_t broadcast = network | ~mask; // 브로드캐스트

    cout << "  IP 주소:       " << uint32_to_ip(ip) << "\n";
    cout << "  서브넷 마스크: " << uint32_to_ip(mask) << "\n";
    cout << "  네트워크:      " << uint32_to_ip(network) << "\n";
    cout << "  호스트:        " << uint32_to_ip(host) << "\n";
    cout << "  브로드캐스트:  " << uint32_to_ip(broadcast) << "\n";
}

// ── 7.3 인터넷 체크섬 (RFC 1071 스타일) ──
uint16_t internet_checksum(const uint8_t* data, size_t length) {
    uint32_t sum = 0;

    // 16비트 단위로 합산
    while (length > 1) {
        sum += (static_cast<uint16_t>(data[0]) << 8) | data[1];
        data += 2;
        length -= 2;
    }

    // 홀수 바이트 처리
    if (length == 1) {
        sum += static_cast<uint16_t>(data[0]) << 8;
    }

    // 캐리 접기 (fold carry)
    while (sum >> 16) {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }

    return static_cast<uint16_t>(~sum);
}

// ── 7.4 비트보드 (체스 보드) ──
//
//  체스 보드를 64비트 정수 하나로 표현!
//
//  비트 번호:
//  56 57 58 59 60 61 62 63   ← 8랭크 (맨 위)
//  48 49 50 51 52 53 54 55
//  40 41 42 43 44 45 46 47
//  32 33 34 35 36 37 38 39
//  24 25 26 27 28 29 30 31
//  16 17 18 19 20 21 22 23
//   8  9 10 11 12 13 14 15
//   0  1  2  3  4  5  6  7   ← 1랭크 (맨 아래)
//   a  b  c  d  e  f  g  h
//

void print_bitboard(uint64_t board) {
    cout << "  a b c d e f g h\n";
    for (int rank = 7; rank >= 0; rank--) {
        cout << (rank + 1) << " ";
        for (int file = 0; file < 8; file++) {
            int sq = rank * 8 + file;
            cout << ((board >> sq) & 1 ? "# " : ". ");
        }
        cout << (rank + 1) << "\n";
    }
    cout << "  a b c d e f g h\n";
}

// 나이트의 이동 가능 위치 계산 (비트 연산만으로!)
uint64_t knight_attacks(int square) {
    uint64_t bb = 1ULL << square;
    uint64_t attacks = 0;

    // 8가지 이동 방향 (보드 밖으로 나가는 것 방지)
    constexpr uint64_t NOT_A_FILE  = 0xFEFEFEFEFEFEFEFEULL;
    constexpr uint64_t NOT_AB_FILE = 0xFCFCFCFCFCFCFCFCULL;
    constexpr uint64_t NOT_H_FILE  = 0x7F7F7F7F7F7F7F7FULL;
    constexpr uint64_t NOT_GH_FILE = 0x3F3F3F3F3F3F3F3FULL;

    attacks |= (bb << 17) & NOT_A_FILE;   // 위2 오른쪽1
    attacks |= (bb << 15) & NOT_H_FILE;   // 위2 왼쪽1
    attacks |= (bb << 10) & NOT_AB_FILE;  // 위1 오른쪽2
    attacks |= (bb << 6)  & NOT_GH_FILE;  // 위1 왼쪽2
    attacks |= (bb >> 6)  & NOT_AB_FILE;  // 아래1 오른쪽2
    attacks |= (bb >> 10) & NOT_GH_FILE;  // 아래1 왼쪽2
    attacks |= (bb >> 15) & NOT_A_FILE;   // 아래2 오른쪽1
    attacks |= (bb >> 17) & NOT_H_FILE;   // 아래2 왼쪽1

    return attacks;
}

void lesson7_practical_examples() {
    cout << "=== 레슨 7: 실전 예제 ===\n\n";

    // ── 7.1 BMP 헤더 검증 ──
    cout << "── BMP 헤더 구조 ──\n";
    cout << "BMPFileHeader 크기: " << sizeof(BMPFileHeader) << " 바이트 (기대: 14)\n";
    cout << "BMPInfoHeader 크기: " << sizeof(BMPInfoHeader) << " 바이트 (기대: 40)\n";

    // BMP 헤더 시뮬레이션
    BMPFileHeader fh{};
    fh.signature = 0x4D42;  // "BM" (리틀 엔디안)
    fh.file_size = 14 + 40 + (100 * 100 * 3);  // 100x100 24비트 BMP
    fh.data_offset = 14 + 40;

    BMPInfoHeader ih{};
    ih.header_size = 40;
    ih.width = 100;
    ih.height = 100;
    ih.planes = 1;
    ih.bit_depth = 24;

    cout << "시뮬레이션 BMP: " << ih.width << "x" << ih.height
         << " " << ih.bit_depth << "비트, 파일크기=" << fh.file_size << "\n";

    // 매직 넘버 확인
    if (fh.signature == 0x4D42) {
        cout << "유효한 BMP 시그니처 확인 (0x4D42 = 'BM')\n";
    }

    // ── 7.2 IP 주소 조작 ──
    cout << "\n── IP 주소 조작 ──\n";
    uint32_t my_ip = ip_to_uint32(192, 168, 1, 100);
    cout << "IP: " << uint32_to_ip(my_ip) << " = 0x"
         << hex << my_ip << dec << "\n";

    uint32_t subnet = ip_to_uint32(255, 255, 255, 0);  // /24
    cout << "\n서브넷 분석:\n";
    analyze_subnet(my_ip, subnet);

    // ── 7.3 체크섬 계산 ──
    cout << "\n── 인터넷 체크섬 ──\n";
    uint8_t test_data[] = {0x45, 0x00, 0x00, 0x73, 0x00, 0x00,
                           0x40, 0x00, 0x40, 0x11, 0x00, 0x00,
                           0xC0, 0xA8, 0x00, 0x01,
                           0xC0, 0xA8, 0x00, 0xC7};
    uint16_t checksum = internet_checksum(test_data, sizeof(test_data));
    cout << "체크섬: 0x" << hex << checksum << dec << "\n";

    // 검증: 체크섬을 포함하여 다시 계산하면 0이 되어야 함
    test_data[10] = (checksum >> 8) & 0xFF;
    test_data[11] = checksum & 0xFF;
    uint16_t verify = internet_checksum(test_data, sizeof(test_data));
    cout << "검증: 0x" << hex << verify << dec
         << (verify == 0 ? " (정상!)" : " (오류!)") << "\n";

    // ── 7.4 비트보드: 나이트 공격 범위 ──
    cout << "\n── 비트보드: 나이트 공격 범위 ──\n";

    // e4 위치 (칸 번호 = rank*8 + file = 3*8 + 4 = 28)
    int knight_sq = 28;  // e4
    cout << "나이트 위치 (e4):\n";
    print_bitboard(1ULL << knight_sq);

    cout << "\n나이트 공격 가능 칸:\n";
    uint64_t attacks = knight_attacks(knight_sq);
    print_bitboard(attacks);
    cout << "공격 가능 칸 수: " << __builtin_popcountll(attacks) << "\n";

    cout << "\n";
}


// =========================================================================
//  연습 문제
// =========================================================================

void exercises() {
    cout << "============================================================\n";
    cout << "  연습 문제 (직접 풀어보세요!)\n";
    cout << "============================================================\n\n";

    cout << "【문제 1】 비트 반전 (Easy)\n";
    cout << "  주어진 8비트 정수의 비트 순서를 뒤집는 함수를 작성하세요.\n";
    cout << "  예: 0b11010010 → 0b01001011\n";
    cout << "  힌트: 각 비트를 하나씩 추출하여 새 위치에 설정\n\n";

    cout << "【문제 2】 2의 보수 (Medium)\n";
    cout << "  8비트 2의 보수 표현에서 음수를 표현하고 덧셈을 수행하세요.\n";
    cout << "  -5를 2의 보수로: 5 = 00000101 → ~5+1 = 11111011\n";
    cout << "  -5 + 3 = ? 을 비트 연산으로 확인해보세요.\n\n";

    cout << "【문제 3】 비트 보드 확장 (Hard)\n";
    cout << "  체스 비숍(대각선 이동)의 공격 범위를 비트보드로 구현하세요.\n";
    cout << "  주어진 칸에서 네 대각선 방향으로 보드 끝까지의\n";
    cout << "  모든 칸을 비트보드로 반환하세요.\n\n";

    cout << "【문제 4】 서브넷 계산기 (Medium)\n";
    cout << "  CIDR 표기법(/24, /16 등)을 입력받아\n";
    cout << "  서브넷 마스크, 네트워크 주소, 브로드캐스트 주소,\n";
    cout << "  가용 호스트 수를 계산하는 프로그램을 작성하세요.\n\n";

    cout << "【문제 5】 비트 패킹 (Hard)\n";
    cout << "  RGB 색상값(각 0~255)을 32비트 정수 하나에 패킹하고\n";
    cout << "  다시 언패킹하는 함수 쌍을 작성하세요.\n";
    cout << "  형식: 0xAARRGGBB (A=알파, R=빨강, G=녹색, B=파랑)\n\n";

    // 문제 1 힌트 코드
    cout << "── 문제 1 풀이 예시 ──\n";
    auto reverse_bits = [](uint8_t n) -> uint8_t {
        uint8_t result = 0;
        for (int i = 0; i < 8; i++) {
            result = (result << 1) | (n & 1);
            n >>= 1;
        }
        return result;
    };

    uint8_t test = 0b11010010;
    cout << "입력:  " << bitset<8>(test) << "\n";
    cout << "반전:  " << bitset<8>(reverse_bits(test)) << "\n";

    // 문제 5 풀이 예시
    cout << "\n── 문제 5 풀이 예시 ──\n";
    auto pack_rgba = [](uint8_t r, uint8_t g, uint8_t b, uint8_t a) -> uint32_t {
        return (static_cast<uint32_t>(a) << 24) |
               (static_cast<uint32_t>(r) << 16) |
               (static_cast<uint32_t>(g) << 8)  |
               static_cast<uint32_t>(b);
    };

    auto unpack_rgba = [](uint32_t color) {
        uint8_t a = (color >> 24) & 0xFF;
        uint8_t r = (color >> 16) & 0xFF;
        uint8_t g = (color >> 8)  & 0xFF;
        uint8_t b = color & 0xFF;
        cout << "A=" << (int)a << " R=" << (int)r
             << " G=" << (int)g << " B=" << (int)b << "\n";
    };

    uint32_t color = pack_rgba(255, 128, 64, 200);
    cout << "패킹: 0x" << hex << color << dec << "\n";
    cout << "언패킹: ";
    unpack_rgba(color);
}


// =========================================================================
//  메인 함수
// =========================================================================

/*
=============================================================================
  레슨별 출력 흐름 가이드 (대략)
=============================================================================
  lesson1 (비트 연산):
    a=12 (0b1100), b=10 (0b1010)
    a & b = 8  (0b1000)
    a | b = 14 (0b1110)
    a ^ b = 6  (0b0110)
    ~a    = -13 (2의 보수)
    a << 2 = 48 (0b110000)
    a >> 1 = 6  (0b0110)

  lesson2 (비트 조작 기법):
    set_bit(0, 3) = 8    (3번 비트 1)
    clear_bit(15, 1) = 13
    toggle_bit(5, 0) = 4
    is_power_of_2(16) = true / 17 = false (단일 비트만 set인지)
    count_bits(7) = 3 (0b111의 1개수)

  lesson3 (bitfield, bitmask):
    struct Flags { uint8_t a:1; uint8_t b:3; uint8_t c:4; }; → 1바이트
    PERMISSION_READ | PERMISSION_WRITE → 검사 시 & 사용

  lesson4 (엔디언):
    호스트 little/big 자동 감지
    0x12345678 → little: [78][56][34][12], big: [12][34][56][78]
    htonl(0x12345678) → 네트워크 바이트 오더 변환

  lesson5 (메모리 정렬):
    struct A { char c; int i; }  → sizeof = 8 (3바이트 패딩)
    alignof(int) = 4
    alignas(64) struct CacheAligned {...}; → 64바이트 정렬

  lesson6 (volatile, MMIO):
    하드웨어 레지스터 접근 시뮬레이션
    volatile 없으면 컴파일러가 최적화로 read 제거 가능

  lesson7 (실전):
    BMP 파일 헤더 파싱 / IP 패킷 헤더 분석
    sizeof, offsetof로 구조 검증
=============================================================================
*/

int main() {
    cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■\n";
    cout << "  C++ 학습 27단계: 시스템 프로그래밍 & 비트 조작\n";
    cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■\n\n";

    lesson1_bit_operations_basics();
    lesson2_bit_manipulation_techniques();
    lesson3_bitfields_and_bitmasks();
    lesson4_endianness();
    lesson5_memory_alignment();
    lesson6_volatile_and_hardware();
    lesson7_practical_examples();
    exercises();

    cout << "\n■ 학습 완료! 다음 단계: 28_security_best_practices\n";
    return 0;
}
