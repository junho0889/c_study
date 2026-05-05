/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C++ 학습 28단계: 보안 & 베스트 프랙티스
  ─ Security & Best Practices ─

  이 파일 하나로 C++ 보안 취약점의 원리, 방어 기법, 안전한 코딩 규칙,
  코드 품질 도구, 그리고 C++ Core Guidelines 핵심을 모두 배웁니다.

  ⚠ 이 파일의 취약점 예제는 오직 교육/방어 목적입니다.
     실제 공격에 사용하지 마세요.

  ■ 컴파일 방법 (터미널에 입력)
    Windows (MinGW) : g++ -std=c++17 -Wall -Wextra -o 28_security.exe main.cpp
    Windows (MSVC)  : cl /EHsc /std:c++17 /W4 main.cpp
    Linux / Mac     : g++ -std=c++17 -Wall -Wextra -o 28_security main.cpp

  ■ 실행 방법
    Windows : .\28_security.exe
    Linux   : ./28_security

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#include <iostream>
#include <string>
#include <cstring>       // strlen, strncpy, memset
#include <vector>
#include <memory>        // unique_ptr, shared_ptr
#include <array>
#include <algorithm>
#include <limits>        // numeric_limits
#include <cstdint>
#include <stdexcept>
#include <cassert>
#include <sstream>
#include <functional>
#include <optional>
#include <type_traits>

using namespace std;


// =========================================================================
//  레슨 1: 버퍼 오버플로우
//  ─ 원리, 위험성, 방지법 (bounds checking, safe functions) ─
// =========================================================================
//
//  ┌──────────────────────────────────────────────────────────────────────┐
//  │  버퍼 오버플로우(Buffer Overflow):                                  │
//  │  배열이나 버퍼의 경계를 넘어서 데이터를 쓰는 취약점                  │
//  │                                                                      │
//  │  스택 메모리 구조:                                                   │
//  │  ┌──────────────────┐ 높은 주소                                     │
//  │  │ 복귀 주소 (RET)  │  ← 공격자가 덮어쓰고 싶은 곳!               │
//  │  ├──────────────────┤                                               │
//  │  │ 이전 프레임 포인터│                                               │
//  │  ├──────────────────┤                                               │
//  │  │ 지역 변수들      │                                               │
//  │  │  ...             │                                               │
//  │  │ buffer[8]        │  ← 여기서 오버플로우 발생!                    │
//  │  ├──────────────────┤                                               │
//  │  │ (다른 변수들)    │                                               │
//  │  └──────────────────┘ 낮은 주소                                     │
//  │                                                                      │
//  │  공격 시나리오:                                                      │
//  │  1. buffer[8]에 8바이트 이상의 데이터를 씀                          │
//  │  2. 인접 변수, 프레임 포인터, 복귀 주소를 덮어씀                    │
//  │  3. 복귀 주소를 공격자 코드로 변경 → 임의 코드 실행!               │
//  │                                                                      │
//  │  방어법:                                                             │
//  │  ● 경계 검사 (bounds checking)                                      │
//  │  ● 안전한 함수 사용 (strncpy 대신 std::string)                     │
//  │  ● std::array, std::vector + at() 사용                              │
//  │  ● 스택 카나리 (컴파일러 보호 기능)                                 │
//  │  ● ASLR (주소 공간 레이아웃 무작위화)                               │
//  └──────────────────────────────────────────────────────────────────────┘
//

void lesson1_buffer_overflow() {
    cout << "=== 레슨 1: 버퍼 오버플로우 ===\n\n";

    // ── 1.1 취약한 코드 (교육 목적 - 이렇게 하면 안 됩니다!) ──
    cout << "── 취약한 C 스타일 코드 (하지 마세요!) ──\n";
    {
        char buffer[8];     // 8바이트 버퍼
        int secret = 0x41414141;  // 인접 변수

        cout << "오버플로우 전 secret: 0x" << hex << secret << dec << "\n";

        // 위험! strcpy는 길이를 확인하지 않음!
        // strcpy(buffer, "AAAAAAAAAAAAAAAA");  // 16바이트 → 오버플로우!
        // 위 코드는 실제로 실행하면 인접 메모리를 손상시킵니다.
        // 교육 목적으로 주석 처리합니다.
        cout << "strcpy(buffer, 긴_문자열) → 인접 변수 'secret' 손상 가능!\n";
        cout << "(실제 실행 시 크래시 또는 보안 침해 발생)\n";

        // strncpy도 완벽하지 않음 - null 종료 보장 안 됨!
        strncpy(buffer, "Hello!!", 7);
        buffer[7] = '\0';  // 수동으로 null 종료 필요
        cout << "strncpy 사용: \"" << buffer << "\"\n";
    }

    // ── 1.2 안전한 코드 (이렇게 하세요!) ──
    cout << "\n── 안전한 C++ 코드 ──\n";
    {
        // 방법 1: std::string 사용 (자동 메모리 관리)
        string safe_buffer = "Hello, World!";
        cout << "std::string: \"" << safe_buffer << "\"\n";
        cout << "  길이: " << safe_buffer.length() << "\n";
        cout << "  용량: " << safe_buffer.capacity() << "\n";

        // 방법 2: std::array + at() (경계 검사)
        array<int, 5> arr = {10, 20, 30, 40, 50};
        try {
            cout << "arr.at(2) = " << arr.at(2) << "\n";
            cout << "arr.at(10) = ";  // 범위 밖!
            cout << arr.at(10) << "\n";  // std::out_of_range 예외!
        } catch (const out_of_range& e) {
            cout << "예외 발생! " << e.what() << "\n";
        }

        // 방법 3: std::vector + at()
        vector<int> vec = {1, 2, 3};
        try {
            vec.at(100);  // 범위 밖 → 예외
        } catch (const out_of_range&) {
            cout << "vector::at() 범위 초과 감지!\n";
        }
    }

    // ── 1.3 안전한 문자열 복사 패턴 ──
    cout << "\n── 안전한 문자열 복사 패턴 ──\n";
    {
        // C 스타일이 꼭 필요한 경우 (레거시 API 등)
        constexpr size_t BUF_SIZE = 16;
        char dest[BUF_SIZE];

        const char* src = "이것은 매우 긴 문자열입니다";
        size_t src_len = strlen(src);

        if (src_len < BUF_SIZE) {
            strcpy(dest, src);  // 안전: 길이 확인 후 복사
        } else {
            strncpy(dest, src, BUF_SIZE - 1);
            dest[BUF_SIZE - 1] = '\0';
            cout << "문자열 잘림 발생! (원본 " << src_len
                 << "바이트 > 버퍼 " << BUF_SIZE << "바이트)\n";
        }

        // 가장 좋은 방법: C++ std::string 사용!
        string safe_dest = src;  // 자동으로 크기 관리
        cout << "std::string은 항상 안전: \"" << safe_dest.substr(0, 20) << "...\"\n";
    }

    cout << "\n";
}


// =========================================================================
//  레슨 2: 정수 오버플로우
//  ─ 부호 있는/없는 정수 위험, 안전한 산술 연산 ─
// =========================================================================
//
//  ┌──────────────────────────────────────────────────────────────────────┐
//  │  정수 오버플로우: 정수의 최대/최소값을 넘어서는 연산                 │
//  │                                                                      │
//  │  부호 없는 정수 (unsigned):                                         │
//  │    uint8_t: 0 ~ 255                                                  │
//  │    255 + 1 = 0 (랩어라운드, 정의된 동작)                            │
//  │    0 - 1 = 255 (언더플로우)                                         │
//  │                                                                      │
//  │  부호 있는 정수 (signed):                                           │
//  │    int8_t: -128 ~ 127                                                │
//  │    127 + 1 = ??? (미정의 동작! UB!)                                  │
//  │                                                                      │
//  │  위험 시나리오:                                                      │
//  │  ● 배열 크기 계산에서 오버플로우 → 작은 버퍼 할당                   │
//  │  ● 루프 카운터 오버플로우 → 무한 루프                               │
//  │  ● unsigned 비교에서 음수 변환 → 경계 검사 우회                     │
//  │                                                                      │
//  │  ■ 부호 있는 정수 오버플로우는 C++에서 미정의 동작(UB)!             │
//  │    컴파일러가 오버플로우가 없다고 가정하고 최적화합니다.             │
//  └──────────────────────────────────────────────────────────────────────┘
//

// 안전한 산술 연산 클래스
class SafeArithmetic {
public:
    // 안전한 덧셈 (오버플로우 시 false 반환)
    static bool safe_add(int32_t a, int32_t b, int32_t& result) {
        // 양수 + 양수 → 오버플로우 가능
        if (b > 0 && a > numeric_limits<int32_t>::max() - b) return false;
        // 음수 + 음수 → 언더플로우 가능
        if (b < 0 && a < numeric_limits<int32_t>::min() - b) return false;
        result = a + b;
        return true;
    }

    // 안전한 곱셈
    static bool safe_multiply(int32_t a, int32_t b, int32_t& result) {
        if (a == 0 || b == 0) { result = 0; return true; }
        if (a > 0 && b > 0 && a > numeric_limits<int32_t>::max() / b) return false;
        if (a < 0 && b < 0 && a < numeric_limits<int32_t>::max() / b) return false;
        if (a > 0 && b < 0 && b < numeric_limits<int32_t>::min() / a) return false;
        if (a < 0 && b > 0 && a < numeric_limits<int32_t>::min() / b) return false;
        result = a * b;
        return true;
    }

    // unsigned 안전한 덧셈
    static bool safe_add_unsigned(uint32_t a, uint32_t b, uint32_t& result) {
        if (a > numeric_limits<uint32_t>::max() - b) return false;
        result = a + b;
        return true;
    }
};

void lesson2_integer_overflow() {
    cout << "=== 레슨 2: 정수 오버플로우 ===\n\n";

    // ── 2.1 unsigned 오버플로우 시연 ──
    cout << "── unsigned 오버플로우 (정의된 동작 - 랩어라운드) ──\n";
    {
        uint8_t a = 255;
        uint8_t b = static_cast<uint8_t>(a + 1);  // 0으로 랩어라운드
        cout << "uint8_t: 255 + 1 = " << (int)b << " (0으로 순환!)\n";

        uint8_t c = 0;
        uint8_t d = static_cast<uint8_t>(c - 1);  // 255로 언더플로우
        cout << "uint8_t: 0 - 1 = " << (int)d << " (255로 순환!)\n";
    }

    // ── 2.2 signed/unsigned 비교 위험 ──
    //
    //  signed와 unsigned를 비교하면 signed가 unsigned로 암묵적 변환!
    //  -1 (signed) → 4294967295 (unsigned) 으로 변환됨!
    //
    cout << "\n── signed/unsigned 비교 위험 ──\n";
    {
        int signed_val = -1;
        unsigned int unsigned_val = 1;

        // 위험! -1이 unsigned로 변환되어 4294967295가 됨
        if (static_cast<unsigned int>(signed_val) > unsigned_val) {
            cout << "-1 > 1u → true! (signed→unsigned 변환 때문)\n";
            cout << "  -1은 unsigned로 변환되면 "
                 << static_cast<unsigned int>(-1) << "이 됩니다!\n";
        }
    }

    // ── 2.3 실제 취약점 시나리오 ──
    cout << "\n── 취약점 시나리오: 배열 크기 계산 ──\n";
    {
        // 위험한 코드 패턴 (교육 목적)
        uint32_t num_elements = 1073741824;  // 2^30
        uint32_t element_size = 8;
        uint32_t total_size = num_elements * element_size;  // 오버플로우!

        cout << "요소 수: " << num_elements << "\n";
        cout << "요소 크기: " << element_size << "\n";
        cout << "계산된 크기: " << total_size << " (오버플로우 발생!)\n";
        cout << "실제 필요 크기: " << (uint64_t)num_elements * element_size << "\n";
        cout << "→ 작은 버퍼가 할당되어 오버플로우 발생 가능!\n";
    }

    // ── 2.4 안전한 산술 연산 ──
    cout << "\n── 안전한 산술 연산 ──\n";
    {
        int32_t result;

        // 정상 연산
        if (SafeArithmetic::safe_add(100, 200, result)) {
            cout << "100 + 200 = " << result << " (안전)\n";
        }

        // 오버플로우 감지
        if (!SafeArithmetic::safe_add(numeric_limits<int32_t>::max(), 1, result)) {
            cout << "INT32_MAX + 1 = 오버플로우 감지!\n";
        }

        // 안전한 곱셈
        if (!SafeArithmetic::safe_multiply(100000, 100000, result)) {
            cout << "100000 * 100000 = 오버플로우 감지!\n";
        }

        // GCC/Clang 내장 오버플로우 검사 (__builtin_add_overflow)
        int32_t a = numeric_limits<int32_t>::max();
        int32_t b = 1;
        int32_t c;
        if (__builtin_add_overflow(a, b, &c)) {
            cout << "__builtin_add_overflow: 오버플로우 감지!\n";
        }
    }

    cout << "\n";
}


// =========================================================================
//  레슨 3: 입력 검증
//  ─ 사용자 입력 신뢰 금지, sanitization, whitelisting ─
// =========================================================================
//
//  ┌──────────────────────────────────────────────────────────────────────┐
//  │  보안의 황금 규칙: "절대로 사용자 입력을 신뢰하지 마세요!"          │
//  │                                                                      │
//  │  입력 검증 전략:                                                     │
//  │                                                                      │
//  │  1. 화이트리스트 (Whitelist) - 허용된 것만 통과 (권장)              │
//  │     예: 숫자만 허용, 특정 문자만 허용                                │
//  │                                                                      │
//  │  2. 블랙리스트 (Blacklist) - 금지된 것만 차단 (비권장)              │
//  │     예: SQL 키워드 차단 → 우회 가능성 높음!                         │
//  │                                                                      │
//  │  3. 이스케이핑 (Escaping) - 특수 문자를 안전하게 변환               │
//  │     예: ' → \', < → &lt;                                            │
//  │                                                                      │
//  │  검증 순서 (입력 → 처리):                                           │
//  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐            │
//  │  │ 입력   │→│ 타입   │→│ 범위   │→│ 형식   │→│ 비즈니스│            │
//  │  │ 수신   │ │ 검사   │ │ 검사   │ │ 검사   │ │ 로직   │            │
//  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘            │
//  └──────────────────────────────────────────────────────────────────────┘
//

class InputValidator {
public:
    // 숫자 입력 검증 (범위 포함)
    static optional<int> parse_int_safe(const string& input,
                                         int min_val = numeric_limits<int>::min(),
                                         int max_val = numeric_limits<int>::max()) {
        if (input.empty()) return nullopt;

        try {
            size_t pos = 0;
            long long val = stoll(input, &pos);

            // 전체 문자열이 숫자인지 확인
            if (pos != input.length()) return nullopt;

            // 범위 검사
            if (val < min_val || val > max_val) return nullopt;

            return static_cast<int>(val);
        } catch (...) {
            return nullopt;
        }
    }

    // 화이트리스트 기반 문자열 검증
    static bool is_alphanumeric(const string& input) {
        return all_of(input.begin(), input.end(), [](char c) {
            return (c >= 'a' && c <= 'z') ||
                   (c >= 'A' && c <= 'Z') ||
                   (c >= '0' && c <= '9') ||
                   c == '_';
        });
    }

    // 이메일 형식 기본 검증 (간략화)
    static bool is_valid_email_basic(const string& email) {
        size_t at_pos = email.find('@');
        if (at_pos == string::npos || at_pos == 0) return false;
        size_t dot_pos = email.find('.', at_pos);
        if (dot_pos == string::npos || dot_pos == at_pos + 1) return false;
        if (dot_pos == email.length() - 1) return false;
        return true;
    }

    // SQL 인젝션 방지를 위한 이스케이핑 (교육 목적)
    //
    //  실제로는 Prepared Statement / Parameterized Query를 사용하세요!
    //  이 함수는 원리 설명을 위한 것입니다.
    //
    static string escape_sql_string(const string& input) {
        string result;
        result.reserve(input.length() * 2);
        for (char c : input) {
            switch (c) {
                case '\'': result += "\\'"; break;  // 작은따옴표
                case '\"': result += "\\\""; break; // 큰따옴표
                case '\\': result += "\\\\"; break; // 백슬래시
                case '\0': result += "\\0"; break;  // 널 문자
                default:   result += c; break;
            }
        }
        return result;
    }

    // 경로 순회 공격(Path Traversal) 방지
    //
    //  ../../../etc/passwd 같은 경로 차단
    //
    static bool is_safe_filename(const string& filename) {
        // 빈 문자열 거부
        if (filename.empty()) return false;

        // ".." 포함 시 거부 (경로 순회 방지)
        if (filename.find("..") != string::npos) return false;

        // 절대 경로 거부
        if (filename[0] == '/' || filename[0] == '\\') return false;
        if (filename.length() >= 2 && filename[1] == ':') return false;  // C:\

        // 화이트리스트 문자만 허용
        return all_of(filename.begin(), filename.end(), [](char c) {
            return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
                   (c >= '0' && c <= '9') || c == '.' || c == '_' || c == '-';
        });
    }
};

void lesson3_input_validation() {
    cout << "=== 레슨 3: 입력 검증 ===\n\n";

    // ── 3.1 숫자 입력 검증 ──
    cout << "── 숫자 입력 검증 ──\n";
    vector<string> test_inputs = {"42", "-10", "999999999999", "abc", "12.34",
                                   "100", "  5", ""};

    for (const auto& input : test_inputs) {
        auto result = InputValidator::parse_int_safe(input, 0, 1000);
        cout << "  \"" << input << "\" → ";
        if (result.has_value()) {
            cout << result.value() << " (유효)\n";
        } else {
            cout << "거부됨 (무효)\n";
        }
    }

    // ── 3.2 화이트리스트 검증 ──
    cout << "\n── 화이트리스트 문자열 검증 ──\n";
    vector<string> names = {"user_name", "DROP TABLE", "admin123",
                             "hack'; --", "normal_user"};
    for (const auto& name : names) {
        cout << "  \"" << name << "\" → "
             << (InputValidator::is_alphanumeric(name) ? "허용" : "거부") << "\n";
    }

    // ── 3.3 SQL 인젝션 방지 ──
    //
    //  SQL 인젝션 공격 예시:
    //  입력: ' OR '1'='1
    //  쿼리: SELECT * FROM users WHERE name = '' OR '1'='1'
    //  → 모든 레코드 반환! (인증 우회)
    //
    cout << "\n── SQL 인젝션 방지 ──\n";
    string malicious = "'; DROP TABLE users; --";
    cout << "  악의적 입력: " << malicious << "\n";
    cout << "  이스케이핑 후: " << InputValidator::escape_sql_string(malicious) << "\n";
    cout << "  ※ 실무에서는 반드시 Prepared Statement를 사용하세요!\n";

    // ── 3.4 경로 순회 공격 방지 ──
    cout << "\n── 경로 순회 공격 방지 ──\n";
    vector<string> filenames = {"report.pdf", "../../../etc/passwd",
                                 "image.png", "C:\\secret.txt",
                                 "/etc/shadow", "normal_file-1.txt"};
    for (const auto& f : filenames) {
        cout << "  \"" << f << "\" → "
             << (InputValidator::is_safe_filename(f) ? "안전" : "위험! 차단") << "\n";
    }

    cout << "\n";
}


// =========================================================================
//  레슨 4: 안전한 메모리 사용
//  ─ use-after-free 방지, 이중 해제 방지, RAII 철저히 ─
// =========================================================================
//
//  ┌──────────────────────────────────────────────────────────────────────┐
//  │  메모리 안전 취약점 Top 3:                                          │
//  │                                                                      │
//  │  1. Use-After-Free (UAF):                                           │
//  │     해제된 메모리를 다시 사용 → 크래시, 임의 코드 실행              │
//  │     int* p = new int(42);                                            │
//  │     delete p;                                                        │
//  │     *p = 100;  // 위험! p는 이미 해제됨                             │
//  │                                                                      │
//  │  2. Double Free:                                                     │
//  │     같은 메모리를 두 번 해제 → 힙 메타데이터 손상                   │
//  │     int* p = new int(42);                                            │
//  │     delete p;                                                        │
//  │     delete p;  // 위험! 이미 해제됨                                 │
//  │                                                                      │
//  │  3. Memory Leak:                                                     │
//  │     할당된 메모리를 해제하지 않음 → 메모리 고갈                     │
//  │     void f() { int* p = new int(42); }  // p를 delete 안 함!        │
//  │                                                                      │
//  │  해결책: RAII (Resource Acquisition Is Initialization)               │
//  │  객체 생성 시 리소스 획득, 소멸 시 자동 해제                        │
//  │  → unique_ptr, shared_ptr 사용!                                     │
//  └──────────────────────────────────────────────────────────────────────┘
//

// RAII 래퍼 예제: 파일 핸들 관리
class SafeFileHandle {
    FILE* handle_;
    string filename_;

public:
    explicit SafeFileHandle(const string& filename, const char* mode)
        : handle_(nullptr), filename_(filename) {
        // 리소스 획득 (생성자에서)
        handle_ = fopen(filename.c_str(), mode);
        if (!handle_) {
            throw runtime_error("파일 열기 실패: " + filename);
        }
    }

    // 복사 금지 (리소스 소유권 중복 방지)
    SafeFileHandle(const SafeFileHandle&) = delete;
    SafeFileHandle& operator=(const SafeFileHandle&) = delete;

    // 이동 허용
    SafeFileHandle(SafeFileHandle&& other) noexcept
        : handle_(other.handle_), filename_(move(other.filename_)) {
        other.handle_ = nullptr;  // 원본의 소유권 해제
    }

    // 소멸자에서 리소스 자동 해제
    ~SafeFileHandle() {
        if (handle_) {
            fclose(handle_);
            handle_ = nullptr;
        }
    }

    FILE* get() const { return handle_; }
    bool is_valid() const { return handle_ != nullptr; }
};

// 댕글링 포인터 안전 패턴
class SafePointerDemo {
public:
    static void demonstrate() {
        cout << "── unique_ptr로 UAF/Double-Free 방지 ──\n";

        // 안전: unique_ptr 사용
        {
            auto ptr = make_unique<int>(42);
            cout << "값: " << *ptr << "\n";
            // ptr이 스코프를 벗어나면 자동 해제
            // delete를 직접 호출할 필요 없음!
        }
        // 여기서 ptr은 이미 해제됨 - 접근 불가 (컴파일 에러)

        // 안전: shared_ptr 사용 (공유 소유권)
        cout << "\n── shared_ptr로 소유권 공유 ──\n";
        shared_ptr<int> shared1;
        {
            auto shared2 = make_shared<int>(100);
            shared1 = shared2;  // 참조 카운트 증가
            cout << "shared2 스코프 내: use_count=" << shared1.use_count() << "\n";
        }
        // shared2가 소멸해도 shared1이 있으므로 메모리 유지
        cout << "shared2 소멸 후: use_count=" << shared1.use_count()
             << ", 값=" << *shared1 << "\n";

        // weak_ptr로 순환 참조 방지
        cout << "\n── weak_ptr로 순환 참조 방지 ──\n";
        auto strong = make_shared<string>("리소스");
        weak_ptr<string> weak = strong;
        cout << "strong 존재: expired=" << weak.expired() << "\n";
        strong.reset();  // 강한 참조 해제
        cout << "strong 해제: expired=" << weak.expired() << "\n";
    }
};

void lesson4_safe_memory() {
    cout << "=== 레슨 4: 안전한 메모리 사용 ===\n\n";

    // ── 4.1 위험한 패턴 vs 안전한 패턴 ──
    cout << "── 위험한 코드 패턴 (하지 마세요!) ──\n";
    cout << R"(
  // 위험 1: Use-After-Free
  int* p = new int(42);
  delete p;
  *p = 100;         // UB! 해제된 메모리 접근

  // 위험 2: Double Free
  int* q = new int(10);
  delete q;
  delete q;          // UB! 이중 해제

  // 위험 3: 배열에 delete (delete[] 아님) 사용
  int* arr = new int[100];
  delete arr;        // UB! delete[] 사용해야 함
)";
    cout << "\n";

    // ── 4.2 안전한 패턴 시연 ──
    SafePointerDemo::demonstrate();

    // ── 4.3 컨테이너 사용으로 안전하게 ──
    cout << "\n── 컨테이너 사용 (raw 포인터 대신) ──\n";
    {
        // 위험: int* data = new int[100];
        // 안전: vector 사용
        vector<int> data(100, 0);
        data[0] = 42;
        cout << "vector 크기: " << data.size() << "\n";
        // 자동 해제됨 - delete[] 불필요!
    }

    // ── 4.4 민감한 데이터 안전하게 지우기 ──
    cout << "\n── 민감한 데이터 안전하게 지우기 ──\n";
    {
        // 비밀번호 같은 민감한 데이터는 사용 후 메모리에서 지워야 함
        string password = "s3cr3t_p@ssw0rd";

        // 사용 후 메모리 덮어쓰기
        // volatile을 사용하여 컴파일러가 최적화로 제거하지 못하게 함
        volatile char* vp = const_cast<volatile char*>(password.data());
        for (size_t i = 0; i < password.size(); i++) {
            vp[i] = 0;
        }

        cout << "비밀번호 지움 (길이: " << password.size() << ", 내용: 제로화됨)\n";

        // C에서는 explicit_bzero() 또는 SecureZeroMemory() 사용
        // C++에서는 위와 같이 volatile 포인터로 덮어쓰기
    }

    cout << "\n";
}


// =========================================================================
//  레슨 5: OWASP C++ 가이드라인
//  ─ 안전한 코딩 규칙, CWE 주요 취약점 ─
// =========================================================================
//
//  ┌──────────────────────────────────────────────────────────────────────┐
//  │  OWASP (Open Web Application Security Project)                      │
//  │  안전한 C++ 코딩 핵심 규칙 10가지                                   │
//  │                                                                      │
//  │  1. 입력 검증: 모든 외부 입력을 검증하세요                          │
//  │  2. 버퍼 관리: 경계를 항상 확인하세요                               │
//  │  3. 정수 안전: 오버플로우/언더플로우를 방지하세요                    │
//  │  4. 메모리 관리: RAII와 스마트 포인터를 사용하세요                   │
//  │  5. 최소 권한: 필요한 최소 권한만 요청하세요                        │
//  │  6. 에러 처리: 예외를 안전하게 처리하세요 (정보 누출 금지)          │
//  │  7. 암호화: 검증된 라이브러리 사용 (직접 구현 금지)                 │
//  │  8. 로깅: 민감 정보를 로그에 남기지 마세요                          │
//  │  9. 코드 리뷰: 정적 분석 도구를 사용하세요                          │
//  │ 10. 의존성 관리: 서드파티 라이브러리를 최신으로 유지하세요          │
//  │                                                                      │
//  │  CWE (Common Weakness Enumeration) 주요 항목:                       │
//  │  ─────────────────────────────────────────────                       │
//  │  CWE-119: 부적절한 메모리 버퍼 경계 제한                            │
//  │  CWE-120: 입력 크기 미확인 버퍼 복사                                │
//  │  CWE-190: 정수 오버플로우 또는 랩어라운드                           │
//  │  CWE-416: Use After Free                                             │
//  │  CWE-415: Double Free                                                │
//  │  CWE-476: NULL 포인터 역참조                                        │
//  │  CWE-787: 범위를 벗어난 쓰기 (Out-of-Bounds Write)                  │
//  │  CWE-125: 범위를 벗어난 읽기 (Out-of-Bounds Read)                   │
//  └──────────────────────────────────────────────────────────────────────┘
//

// 안전한 에러 처리 패턴
class SecureError : public runtime_error {
    int error_code_;
public:
    SecureError(int code, const string& safe_message)
        : runtime_error(safe_message), error_code_(code) {}

    int code() const { return error_code_; }

    // 사용자에게 보여줄 메시지 (내부 정보 숨김)
    string user_message() const {
        return "오류가 발생했습니다. (코드: " + to_string(error_code_) + ")";
    }
};

// NULL 포인터 안전 역참조 (CWE-476 방지)
template<typename T>
T& safe_deref(T* ptr, const string& context = "") {
    if (!ptr) {
        throw SecureError(476, "널 포인터 역참조 방지: " + context);
    }
    return *ptr;
}

void lesson5_owasp_guidelines() {
    cout << "=== 레슨 5: OWASP C++ 가이드라인 ===\n\n";

    // ── 5.1 안전한 에러 처리 ──
    cout << "── 안전한 에러 처리 (정보 누출 방지) ──\n";
    {
        // 나쁜 예: 내부 정보를 에러 메시지에 노출
        // throw runtime_error("DB 연결 실패: host=192.168.1.100, user=admin, pass=secret");

        // 좋은 예: 안전한 에러 메시지
        try {
            throw SecureError(5001, "데이터베이스 연결 실패");
        } catch (const SecureError& e) {
            // 내부 로그: 상세 정보 (관리자만 접근)
            cout << "[내부 로그] " << e.what() << " (코드: " << e.code() << ")\n";
            // 사용자에게: 일반적인 메시지만
            cout << "[사용자에게] " << e.user_message() << "\n";
        }
    }

    // ── 5.2 NULL 포인터 안전 처리 (CWE-476) ──
    cout << "\n── NULL 포인터 안전 처리 ──\n";
    {
        int value = 42;
        int* valid_ptr = &value;
        int* null_ptr = nullptr;

        try {
            cout << "유효한 포인터: " << safe_deref(valid_ptr, "valid_ptr") << "\n";
            cout << "널 포인터: " << safe_deref(null_ptr, "null_ptr") << "\n";
        } catch (const SecureError& e) {
            cout << "감지됨! " << e.what() << "\n";
        }
    }

    // ── 5.3 안전한 타입 변환 ──
    cout << "\n── 안전한 타입 변환 ──\n";
    {
        // 위험: C 스타일 캐스트 (모든 것을 허용)
        // int* p = (int*)some_pointer;  // 위험!

        // 안전: C++ 캐스트 (의도 명확)
        double pi = 3.14;
        int int_pi = static_cast<int>(pi);  // 의도적 축소 변환
        cout << "static_cast<int>(3.14) = " << int_pi << "\n";

        // dynamic_cast: 다형성 객체의 안전한 다운캐스트
        // reinterpret_cast: 최후의 수단 (주의!)
        // const_cast: const 제거 (매우 주의!)

        cout << "C 스타일 캐스트 대신 C++ 캐스트를 사용하세요:\n";
        cout << "  static_cast    - 일반적인 타입 변환\n";
        cout << "  dynamic_cast   - 다형성 다운캐스트 (안전)\n";
        cout << "  reinterpret_cast - 비트 패턴 재해석 (주의)\n";
        cout << "  const_cast     - const 제거 (최후의 수단)\n";
    }

    // ── 5.4 CWE 취약점 체크리스트 ──
    cout << "\n── CWE 주요 취약점 체크리스트 ──\n";
    cout << "  [방어] CWE-119/120: std::vector, std::array 사용\n";
    cout << "  [방어] CWE-190: SafeArithmetic 또는 __builtin_*_overflow 사용\n";
    cout << "  [방어] CWE-416: unique_ptr/shared_ptr 사용\n";
    cout << "  [방어] CWE-415: 스마트 포인터로 자동 해제\n";
    cout << "  [방어] CWE-476: safe_deref 패턴 또는 optional 사용\n";
    cout << "  [방어] CWE-787/125: at() 메서드로 경계 검사\n";

    cout << "\n";
}


// =========================================================================
//  레슨 6: 코드 품질 도구
//  ─ clang-tidy, cppcheck, Coverity, 정적 분석 활용법 ─
// =========================================================================
//
//  ┌──────────────────────────────────────────────────────────────────────┐
//  │  정적 분석 도구: 코드를 실행하지 않고 버그/취약점을 찾는 도구        │
//  │                                                                      │
//  │  ┌─────────────┬──────────────────────────────────────────────┐     │
//  │  │ 도구        │ 특징                                         │     │
//  │  ├─────────────┼──────────────────────────────────────────────┤     │
//  │  │ clang-tidy  │ LLVM 기반, 수백 개 검사 규칙, 자동 수정     │     │
//  │  │             │ 실행: clang-tidy main.cpp -- -std=c++17     │     │
//  │  ├─────────────┼──────────────────────────────────────────────┤     │
//  │  │ cppcheck    │ 오픈소스, 낮은 오탐률, 간편한 사용          │     │
//  │  │             │ 실행: cppcheck --enable=all main.cpp        │     │
//  │  ├─────────────┼──────────────────────────────────────────────┤     │
//  │  │ Coverity    │ 상용, 가장 정밀, 대규모 프로젝트에 적합     │     │
//  │  │             │ (오픈소스 프로젝트 무료)                     │     │
//  │  ├─────────────┼──────────────────────────────────────────────┤     │
//  │  │ PVS-Studio  │ 상용, C/C++ 특화, 우수한 진단 품질          │     │
//  │  ├─────────────┼──────────────────────────────────────────────┤     │
//  │  │ Valgrind    │ 동적 분석, 메모리 누수/오류 감지             │     │
//  │  │             │ 실행: valgrind ./program                     │     │
//  │  ├─────────────┼──────────────────────────────────────────────┤     │
//  │  │ ASan/UBSan  │ 컴파일러 내장 sanitizer                     │     │
//  │  │             │ -fsanitize=address,undefined                 │     │
//  │  └─────────────┴──────────────────────────────────────────────┘     │
//  │                                                                      │
//  │  권장 조합: clang-tidy (정적) + ASan (동적) + cppcheck (추가)       │
//  └──────────────────────────────────────────────────────────────────────┘
//

void lesson6_code_quality_tools() {
    cout << "=== 레슨 6: 코드 품질 도구 ===\n\n";

    // ── 6.1 컴파일러 경고 활용 ──
    cout << "── 컴파일러 경고 플래그 (첫 번째 방어선) ──\n";
    cout << R"(
  GCC/Clang 권장 플래그:
    -Wall          : 주요 경고 활성화
    -Wextra        : 추가 경고 활성화
    -Wpedantic     : 표준 준수 경고
    -Werror        : 경고를 에러로 취급 (CI에서 유용)
    -Wshadow       : 변수 가림(shadowing) 경고
    -Wconversion   : 타입 변환 경고
    -Wnull-dereference : NULL 역참조 경고

  MSVC 권장 플래그:
    /W4            : 높은 경고 수준
    /WX            : 경고를 에러로 취급
    /analyze       : 정적 분석 활성화
)";

    // ── 6.2 clang-tidy 사용법 ──
    cout << "── clang-tidy 사용법 ──\n";
    cout << R"(
  설치: (대부분 clang과 함께 설치됨)
    Ubuntu: sudo apt install clang-tidy
    macOS:  brew install llvm

  기본 실행:
    clang-tidy main.cpp -- -std=c++17

  설정 파일 (.clang-tidy):
    ---
    Checks: >
      -*,
      bugprone-*,
      cert-*,
      cppcoreguidelines-*,
      modernize-*,
      performance-*,
      readability-*
    WarningsAsErrors: 'bugprone-*,cert-*'
    HeaderFilterRegex: '.*'

  주요 검사 카테고리:
    bugprone-*           : 버그 가능성이 높은 패턴
    cert-*               : CERT 보안 코딩 표준
    cppcoreguidelines-*  : C++ Core Guidelines
    modernize-*          : 최신 C++ 문법으로 변환
    performance-*        : 성능 개선 제안
)";

    // ── 6.3 Sanitizer 사용법 ──
    cout << "── Sanitizer (동적 분석) ──\n";
    cout << R"(
  AddressSanitizer (ASan):
    컴파일: g++ -fsanitize=address -g main.cpp
    감지 가능:
      - 버퍼 오버플로우 (스택, 힙, 전역)
      - Use-after-free
      - Use-after-return
      - Double free
      - Memory leaks

  UndefinedBehaviorSanitizer (UBSan):
    컴파일: g++ -fsanitize=undefined -g main.cpp
    감지 가능:
      - 정수 오버플로우
      - NULL 역참조
      - 정렬 오류
      - 배열 범위 초과

  ThreadSanitizer (TSan):
    컴파일: g++ -fsanitize=thread -g main.cpp
    감지: 데이터 레이스 (멀티스레드)

  조합 사용 (권장):
    g++ -fsanitize=address,undefined -fno-omit-frame-pointer -g main.cpp
)";

    // ── 6.4 Valgrind 사용법 ──
    cout << "── Valgrind (Linux 전용) ──\n";
    cout << R"(
  실행: valgrind --leak-check=full --show-leak-kinds=all ./program

  출력 예시:
    ==12345== HEAP SUMMARY:
    ==12345==     in use at exit: 72,704 bytes in 1 blocks
    ==12345==   total heap usage: 10 allocs, 9 frees, 73,728 bytes allocated
    ==12345==
    ==12345== 40 bytes in 1 blocks are definitely lost
    ==12345==    at 0x4C2AB80: operator new(unsigned long)
    ==12345==    by 0x400A1B: main (main.cpp:42)
)";

    cout << "\n";
}


// =========================================================================
//  레슨 7: C++ Core Guidelines
//  ─ 핵심 규칙 요약, GSL, const 정확성, 예외 안전성 보장 레벨 ─
// =========================================================================
//
//  ┌──────────────────────────────────────────────────────────────────────┐
//  │  C++ Core Guidelines (isocpp.github.io/CppCoreGuidelines)           │
//  │  Bjarne Stroustrup와 Herb Sutter가 관리하는 권위 있는 코딩 지침     │
//  │                                                                      │
//  │  핵심 철학:                                                         │
//  │  ● 타입 안전성을 지키세요                                           │
//  │  ● 리소스 누수를 방지하세요                                         │
//  │  ● 댕글링 포인터를 만들지 마세요                                    │
//  │  ● 명확한 의도를 표현하세요                                         │
//  │                                                                      │
//  │  예외 안전성 보장 레벨:                                              │
//  │  ─────────────────────────────────────────                           │
//  │  레벨 0: 보장 없음 (No guarantee)                                   │
//  │    → 예외 발생 시 리소스 누수, 불변 조건 깨짐                       │
//  │                                                                      │
//  │  레벨 1: 기본 보장 (Basic guarantee)                                │
//  │    → 예외 발생 시에도 리소스 누수 없음, 유효한 상태 유지            │
//  │    → 단, 예외 전 상태로 복원되지는 않을 수 있음                     │
//  │                                                                      │
//  │  레벨 2: 강력한 보장 (Strong guarantee)                             │
//  │    → 예외 발생 시 예외 전 상태로 완전히 복원 (commit-or-rollback)   │
//  │    → copy-and-swap 이디엄으로 구현                                  │
//  │                                                                      │
//  │  레벨 3: 무예외 보장 (No-throw guarantee)                           │
//  │    → 절대 예외를 던지지 않음 (noexcept)                             │
//  │    → 소멸자, move 연산, swap에 필수                                 │
//  └──────────────────────────────────────────────────────────────────────┘
//

// ── 7.1 const 정확성 (const correctness) ──
//
// 규칙: 변경하지 않는 것은 반드시 const로 선언하세요!
//
class ConstCorrectExample {
    string name_;
    int value_;

public:
    ConstCorrectExample(string name, int value)
        : name_(move(name)), value_(value) {}

    // const 멤버 함수: 객체를 변경하지 않음을 보장
    const string& name() const { return name_; }
    int value() const { return value_; }

    // non-const: 객체를 변경하는 함수
    void set_value(int v) { value_ = v; }

    // const 참조로 전달: 불필요한 복사 방지 + 변경 방지
    void print_info(const string& prefix) const {
        cout << prefix << ": " << name_ << " = " << value_ << "\n";
    }
};

// ── 7.2 예외 안전성 보장: Copy-and-Swap 이디엄 ──
class ExceptionSafeVector {
    int* data_;
    size_t size_;
    size_t capacity_;

public:
    explicit ExceptionSafeVector(size_t cap = 0)
        : data_(cap > 0 ? new int[cap]{} : nullptr), size_(0), capacity_(cap) {}

    // 복사 생성자
    ExceptionSafeVector(const ExceptionSafeVector& other)
        : data_(other.size_ > 0 ? new int[other.size_] : nullptr),
          size_(other.size_), capacity_(other.size_) {
        if (data_) {
            copy(other.data_, other.data_ + other.size_, data_);
        }
    }

    // 이동 생성자 (noexcept - 무예외 보장)
    ExceptionSafeVector(ExceptionSafeVector&& other) noexcept
        : data_(other.data_), size_(other.size_), capacity_(other.capacity_) {
        other.data_ = nullptr;
        other.size_ = 0;
        other.capacity_ = 0;
    }

    // 소멸자 (noexcept - 절대 예외 없음!)
    ~ExceptionSafeVector() {
        delete[] data_;
    }

    // Copy-and-Swap: 강력한 예외 안전성!
    //
    //   작동 원리:
    //   1. 매개변수를 값으로 받아 복사본 생성 (여기서 예외 발생 가능)
    //   2. 복사가 성공하면 swap (절대 실패 안 함)
    //   3. 예외 발생 시 원본은 변경되지 않음!
    //
    ExceptionSafeVector& operator=(ExceptionSafeVector other) noexcept {
        swap(*this, other);
        return *this;
    }

    // swap (noexcept - 무예외 보장)
    friend void swap(ExceptionSafeVector& a, ExceptionSafeVector& b) noexcept {
        using std::swap;
        swap(a.data_, b.data_);
        swap(a.size_, b.size_);
        swap(a.capacity_, b.capacity_);
    }

    void push_back(int value) {
        if (size_ >= capacity_) {
            // 강력한 보장: 새 메모리 할당 성공 후에만 데이터 이동
            size_t new_cap = capacity_ == 0 ? 1 : capacity_ * 2;
            int* new_data = new int[new_cap];  // 예외 가능
            // 할당 성공 → 기존 데이터 복사 (여기서 실패하면 new_data만 해제)
            if (data_) {
                copy(data_, data_ + size_, new_data);
                delete[] data_;
            }
            data_ = new_data;
            capacity_ = new_cap;
        }
        data_[size_++] = value;
    }

    size_t size() const { return size_; }
    int at(size_t index) const {
        if (index >= size_) throw out_of_range("인덱스 범위 초과");
        return data_[index];
    }
};

// ── 7.3 GSL (Guidelines Support Library) 개념 ──
//
//  GSL은 C++ Core Guidelines를 지원하는 작은 라이브러리입니다.
//  Microsoft에서 제공: https://github.com/microsoft/GSL
//
//  주요 타입:
//  ● gsl::not_null<T>  - nullptr이 될 수 없는 포인터
//  ● gsl::span<T>      - 배열/버퍼의 안전한 뷰 (C++20에 std::span)
//  ● gsl::narrow<T>    - 안전한 축소 변환 (데이터 손실 시 예외)
//  ● gsl::finally       - 스코프 종료 시 실행할 코드 (RAII)
//
//  아래는 GSL 개념을 직접 구현한 간단한 버전입니다.

// gsl::not_null 간이 구현
template<typename T>
class NotNull {
    T ptr_;
public:
    NotNull(T ptr) : ptr_(ptr) {
        if (!ptr_) throw invalid_argument("NotNull에 nullptr 전달!");
    }
    T get() const { return ptr_; }
    auto operator->() const { return ptr_; }
    auto& operator*() const { return *ptr_; }
};

// gsl::narrow 간이 구현 (안전한 축소 변환)
template<typename To, typename From>
To narrow(From value) {
    auto converted = static_cast<To>(value);
    if (static_cast<From>(converted) != value) {
        throw runtime_error("narrow 변환 시 데이터 손실!");
    }
    // 부호 변환 검사
    if ((value < From{}) != (converted < To{})) {
        throw runtime_error("narrow 변환 시 부호 변경!");
    }
    return converted;
}

// gsl::finally 간이 구현 (스코프 가드)
template<typename F>
class FinalAction {
    F action_;
    bool active_;
public:
    explicit FinalAction(F action) : action_(move(action)), active_(true) {}
    ~FinalAction() { if (active_) action_(); }
    FinalAction(FinalAction&& other) noexcept
        : action_(move(other.action_)), active_(other.active_) {
        other.active_ = false;
    }
    FinalAction(const FinalAction&) = delete;
    FinalAction& operator=(const FinalAction&) = delete;
};

template<typename F>
FinalAction<F> finally(F action) { return FinalAction<F>(move(action)); }

void lesson7_core_guidelines() {
    cout << "=== 레슨 7: C++ Core Guidelines ===\n\n";

    // ── 7.1 const 정확성 시연 ──
    cout << "── const 정확성 ──\n";
    {
        const ConstCorrectExample obj("설정값", 42);
        obj.print_info("const 객체");
        // obj.set_value(100);  // 컴파일 에러! const 객체에서 non-const 함수 호출 불가

        ConstCorrectExample mutable_obj("변경가능", 10);
        mutable_obj.set_value(100);
        mutable_obj.print_info("수정 후");
    }

    // ── 7.2 예외 안전 벡터 시연 ──
    cout << "\n── 예외 안전 벡터 (Copy-and-Swap) ──\n";
    {
        ExceptionSafeVector v1(4);
        v1.push_back(10);
        v1.push_back(20);
        v1.push_back(30);

        // 복사 대입 (강력한 예외 안전성)
        ExceptionSafeVector v2 = v1;
        cout << "v2 크기: " << v2.size() << "\n";
        cout << "v2[0]=" << v2.at(0) << " v2[1]=" << v2.at(1)
             << " v2[2]=" << v2.at(2) << "\n";

        // 이동 대입 (noexcept)
        ExceptionSafeVector v3 = move(v1);
        cout << "이동 후 v3 크기: " << v3.size() << "\n";
        cout << "이동 후 v1 크기: " << v1.size() << " (비어있음)\n";
    }

    // ── 7.3 NotNull 시연 ──
    cout << "\n── NotNull (GSL 패턴) ──\n";
    {
        int value = 42;
        try {
            NotNull<int*> safe_ptr(&value);
            cout << "NotNull 값: " << *safe_ptr << "\n";

            // NotNull<int*> bad_ptr(nullptr);  // 예외 발생!
            cout << "nullptr 전달 시도 시 예외 발생 보장\n";
        } catch (const invalid_argument& e) {
            cout << "감지: " << e.what() << "\n";
        }
    }

    // ── 7.4 narrow 변환 시연 ──
    cout << "\n── narrow 변환 (안전한 축소 변환) ──\n";
    {
        try {
            int8_t safe = narrow<int8_t>(42);       // 안전: 42는 int8_t 범위
            cout << "narrow<int8_t>(42) = " << (int)safe << " (안전)\n";

            int8_t overflow = narrow<int8_t>(200);   // 예외! 200 > 127
            cout << "이 줄은 실행되지 않음: " << (int)overflow << "\n";
        } catch (const runtime_error& e) {
            cout << "narrow 예외: " << e.what() << "\n";
        }
    }

    // ── 7.5 finally (스코프 가드) 시연 ──
    cout << "\n── finally (스코프 가드) ──\n";
    {
        cout << "스코프 시작\n";
        auto cleanup = finally([]{ cout << "스코프 종료 시 자동 정리 실행!\n"; });
        cout << "스코프 내부 작업 수행...\n";
        // cleanup의 소멸자가 finally 블록을 자동 실행
    }

    // ── 7.6 핵심 규칙 요약 ──
    cout << "\n── C++ Core Guidelines 핵심 규칙 ──\n";
    cout << R"(
  [P.1]  아이디어를 코드로 직접 표현하세요
  [I.11] 원시 포인터(T*)로 소유권을 전달하지 마세요
  [F.7]  일반 용도로는 T& 또는 T*가 아닌 smart pointer를 사용하세요
  [C.20] 기본 연산을 정의하지 않아도 되면 정의하지 마세요 (Rule of Zero)
  [C.21] 하나라도 정의하면 모두 정의하세요 (Rule of Five)
  [R.1]  원시 포인터 대신 리소스 핸들(RAII)을 사용하세요
  [R.11] new와 delete를 직접 호출하지 마세요
  [R.20] 소유권을 표현하려면 unique_ptr을 사용하세요
  [ES.20] 객체를 항상 초기화하세요
  [ES.22] 초기값이 정해질 때까지 변수 선언을 미루세요
  [Con.1] 기본적으로 객체를 const로 만드세요
  [E.6]  RAII를 사용하여 리소스 누수를 방지하세요
)";

    cout << "\n";
}


// =========================================================================
//  연습 문제
// =========================================================================

void exercises() {
    cout << "============================================================\n";
    cout << "  연습 문제 (직접 풀어보세요!)\n";
    cout << "============================================================\n\n";

    cout << "【문제 1】 안전한 문자열 파서 (Easy)\n";
    cout << "  쉼표로 구분된 정수 문자열 \"1,2,3,4,5\"를 파싱하여\n";
    cout << "  vector<int>로 반환하는 함수를 작성하세요.\n";
    cout << "  잘못된 입력(빈 문자열, 정수 아닌 값, 오버플로우)을\n";
    cout << "  모두 안전하게 처리해야 합니다.\n\n";

    cout << "【문제 2】 RAII 파일 로거 (Medium)\n";
    cout << "  파일에 로그를 기록하는 Logger 클래스를 작성하세요.\n";
    cout << "  RAII로 파일을 자동 관리하고, 복사는 금지하되\n";
    cout << "  이동은 허용해야 합니다. 민감 정보는 마스킹하세요.\n\n";

    cout << "【문제 3】 안전한 동적 배열 (Hard)\n";
    cout << "  ExceptionSafeVector를 확장하여 다음 기능을 추가하세요:\n";
    cout << "  - pop_back() (강력한 예외 안전성 보장)\n";
    cout << "  - insert(index, value) (범위 검사 포함)\n";
    cout << "  - erase(index) (강력한 예외 안전성 보장)\n";
    cout << "  - operator[] const와 non-const 버전\n\n";

    cout << "【문제 4】 입력 검증 프레임워크 (Medium)\n";
    cout << "  다양한 검증 규칙(길이, 형식, 범위)을 조합할 수 있는\n";
    cout << "  ValidationRule 클래스 체인을 설계하세요.\n";
    cout << "  Chain of Responsibility 패턴을 사용합니다.\n\n";

    cout << "【문제 5】 메모리 안전 스마트 포인터 (Hard)\n";
    cout << "  unique_ptr을 직접 구현해보세요.\n";
    cout << "  생성자, 소멸자, 이동 생성자, 이동 대입,\n";
    cout << "  복사 금지, get(), release(), reset()을 포함합니다.\n";
    cout << "  커스텀 삭제자(custom deleter)도 지원하세요.\n\n";

    // 문제 1 풀이 예시
    cout << "── 문제 1 풀이 예시 ──\n";
    auto parse_csv_ints = [](const string& input) -> vector<int> {
        vector<int> result;
        if (input.empty()) return result;

        istringstream ss(input);
        string token;

        while (getline(ss, token, ',')) {
            auto val = InputValidator::parse_int_safe(token);
            if (val.has_value()) {
                result.push_back(val.value());
            } else {
                cerr << "  경고: 잘못된 값 무시: \"" << token << "\"\n";
            }
        }
        return result;
    };

    string test_input = "1,2,hello,4,999999999999,6";
    cout << "입력: \"" << test_input << "\"\n";
    auto parsed = parse_csv_ints(test_input);
    cout << "결과: [";
    for (size_t i = 0; i < parsed.size(); i++) {
        if (i > 0) cout << ", ";
        cout << parsed[i];
    }
    cout << "]\n";
}


// =========================================================================
//  메인 함수
// =========================================================================

/*
=============================================================================
  레슨별 출력 흐름 가이드 (대략)
=============================================================================
  lesson1 (Buffer Overflow):
    char buf[10]; strcpy(buf, "1234567890123"); → UB / 크래시
    → strncpy_s, std::string, std::array 사용
    스택 보호: -fstack-protector-strong

  lesson2 (Integer Overflow):
    INT_MAX + 1 → UB (signed)
    unsigned는 wrap-around (정의됨)
    검증: __builtin_add_overflow / std::add_overflow

  lesson3 (Input Validation):
    "123abc" → stoi 결과 = 123 (나머지 무시!), validate 필요
    경로 검증: "../../etc/passwd" 차단 (디렉토리 탈출 방지)
    SQL injection: prepared statement 권장

  lesson4 (Safe Memory):
    smart pointer 사용 (new/delete 회피)
    초기화: int x{};  // 항상 초기화
    secure_zero(buf, len); // 비밀 메모리 wipe (컴파일러가 못 없애게)

  lesson5 (OWASP Top 10 for C++):
    Use-After-Free, Type Confusion, Format String,
    Race Condition, Path Traversal, Unsafe Deserialization, ...

  lesson6 (Code Quality):
    Tools: clang-tidy, cppcheck, PVS-Studio, AddressSanitizer
    각 도구 설치 / 명령 / 잡는 버그 종류

  lesson7 (Core Guidelines):
    F.21 (out: out parameter는 tuple로 묶어 반환)
    R.1 (RAII), R.10 (raw new 회피), C.20 (Rule of 0) 등

  exercises:
    안전하지 않은 코드 → 안전한 코드로 리팩토링
=============================================================================
*/

int main() {
    cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■\n";
    cout << "  C++ 학습 28단계: 보안 & 베스트 프랙티스\n";
    cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■\n\n";

    lesson1_buffer_overflow();
    lesson2_integer_overflow();
    lesson3_input_validation();
    lesson4_safe_memory();
    lesson5_owasp_guidelines();
    lesson6_code_quality_tools();
    lesson7_core_guidelines();
    exercises();

    cout << "\n■ 학습 완료! C++ 보안 기초를 마스터했습니다.\n";
    cout << "  다음 단계로 실전 프로젝트에 보안 원칙을 적용해보세요!\n";
    return 0;
}
