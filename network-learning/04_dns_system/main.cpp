/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  네트워크 학습 04단계: DNS 완전 정복
  ─────────────────────────────────────────────────
  DNS 질의 과정, 레코드 종류, DNS 보안,
  C++로 DNS 질의기/간이 DNS 서버 구현

  ■ 컴파일 방법:
      g++ -std=c++17 -Wall -lws2_32 -o dns_system main.cpp

  ■ 이 파일을 배우면 할 수 있는 것:
      - DNS가 왜 필요하고 어떻게 동작하는지 완벽 이해
      - DNS 레코드 종류와 용도 구분
      - C++로 직접 DNS 쿼리 패킷을 만들어서 질의
      - 로컬 DNS 캐시 서버 구현

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#ifdef _WIN32
    #ifndef WIN32_LEAN_AND_MEAN
    #define WIN32_LEAN_AND_MEAN
    #endif
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #define SOCKET_INIT() do { WSADATA wsa; WSAStartup(MAKEWORD(2,2), &wsa); } while(0)
    #define SOCKET_CLEANUP() WSACleanup()
    #define CLOSE_SOCKET(s) closesocket(s)
    #define SOCKET_ERROR_CODE WSAGetLastError()
    typedef int socklen_t;
#else
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <unistd.h>
    #include <netdb.h>
    #define SOCKET int
    #define INVALID_SOCKET (-1)
    #define SOCKET_ERROR (-1)
    #define SOCKET_INIT() ((void)0)
    #define SOCKET_CLEANUP() ((void)0)
    #define CLOSE_SOCKET(s) close(s)
    #define SOCKET_ERROR_CODE errno
#endif

#include <iostream>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <map>
#include <iomanip>
#include <sstream>
#include <algorithm>
#include <chrono>

// ┌───────────────────────────────────────────────────────────────────┐
// │  ★ DNS (Domain Name System)란?                                   │
// │                                                                   │
// │  인터넷의 "전화번호부"                                           │
// │  사람이 읽기 쉬운 도메인 이름을 컴퓨터가 이해하는 IP로 변환      │
// │                                                                   │
// │  비유: 전화번호부                                                 │
// │    - 이름: "김철수"     → 전화번호: 010-1234-5678                │
// │    - 도메인: "google.com" → IP: 142.250.196.110                  │
// │                                                                   │
// │  왜 필요한가?                                                     │
// │    - 142.250.196.110 기억하기 어려움                              │
// │    - google.com은 기억하기 쉬움!                                  │
// │    - IP가 바뀌어도 도메인은 그대로 유지 가능                      │
// └───────────────────────────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  DNS 질의 과정 - "전화번호 찾기"
// ════════════════════════════════════════════════════════════════════
//
//  www.example.com 의 IP를 찾는 과정:
//
//  ┌──────────────────────────────────────────────────────────────┐
//  │              DNS 재귀 질의 (Recursive Query)                  │
//  │                                                               │
//  │  [1] 브라우저 → 로컬 DNS 캐시 확인                           │
//  │      "이전에 찾아본 적 있나?"                                 │
//  │      → 있으면 바로 반환! (캐시 히트)                          │
//  │                                                               │
//  │  [2] OS DNS 캐시 확인 + hosts 파일 확인                       │
//  │      C:\Windows\System32\drivers\etc\hosts                    │
//  │      /etc/hosts (Linux)                                       │
//  │                                                               │
//  │  [3] 설정된 DNS 서버에 질의 (보통 ISP의 DNS)                  │
//  │                                                               │
//  │  [4] DNS 서버가 모르면 → 반복 질의 시작:                      │
//  │                                                               │
//  │   로컬DNS                  루트DNS        .com DNS   example  │
//  │   Resolver                 서버           TLD서버    권한DNS   │
//  │     │                        │              │          │      │
//  │     │── "www.example.com?"──>│              │          │      │
//  │     │<─ ".com은 여기 물어봐"─│              │          │      │
//  │     │                        │              │          │      │
//  │     │── "www.example.com?" ─────────────>│  │          │      │
//  │     │<─ "example.com은 여기" ────────────│  │          │      │
//  │     │                        │              │          │      │
//  │     │── "www.example.com?" ─────────────────────────>│ │      │
//  │     │<─ "IP는 93.184.216.34!" ──────────────────────│ │      │
//  │     │                                                         │
//  │  [5] 결과를 캐시에 저장 (TTL 기간 동안)                       │
//  │  [6] 클라이언트에게 IP 반환                                   │
//  └──────────────────────────────────────────────────────────────┘
//
//  ★ 루트 DNS 서버: 전 세계 13개 (a~m.root-servers.net)
//  ★ TLD 서버: .com, .net, .org, .kr 등 최상위 도메인 관리
//  ★ 권한 DNS: 실제 도메인의 레코드를 가진 서버

// ════════════════════════════════════════════════════════════════════
//  DNS 레코드 종류 - "전화번호부의 항목 종류"
// ════════════════════════════════════════════════════════════════════
//
//  ┌──────┬──────────────────────────────────────────────────────┐
//  │ 타입 │ 설명                                                  │
//  ├──────┼──────────────────────────────────────────────────────┤
//  │ A    │ 도메인 → IPv4 주소                                   │
//  │      │ example.com → 93.184.216.34                          │
//  ├──────┼──────────────────────────────────────────────────────┤
//  │ AAAA │ 도메인 → IPv6 주소                                   │
//  │      │ example.com → 2606:2800:220:1:248:1893:25c8:1946    │
//  ├──────┼──────────────────────────────────────────────────────┤
//  │ CNAME│ 도메인 → 다른 도메인 (별칭)                         │
//  │      │ www.example.com → example.com                        │
//  │      │ 비유: "김철수" → "철수네 집" (같은 사람, 다른 이름)  │
//  ├──────┼──────────────────────────────────────────────────────┤
//  │ MX   │ 메일 서버 주소 (우선순위 포함)                       │
//  │      │ example.com → mail.example.com (priority: 10)       │
//  │      │ 비유: "이 주소로 편지 보내면 여기 우체국이 처리"     │
//  ├──────┼──────────────────────────────────────────────────────┤
//  │ TXT  │ 텍스트 정보 (SPF, DKIM, 소유 인증 등)               │
//  │      │ "v=spf1 include:_spf.google.com ~all"               │
//  ├──────┼──────────────────────────────────────────────────────┤
//  │ NS   │ 네임서버 (이 도메인을 관리하는 DNS 서버)             │
//  │      │ example.com → ns1.example.com                        │
//  ├──────┼──────────────────────────────────────────────────────┤
//  │ SOA  │ 권한 시작 (도메인의 핵심 관리 정보)                  │
//  │      │ 주 네임서버, 관리자 메일, 시리얼 번호 등              │
//  ├──────┼──────────────────────────────────────────────────────┤
//  │ PTR  │ IP → 도메인 (역방향 조회, 역DNS)                    │
//  │      │ 93.184.216.34 → example.com                          │
//  ├──────┼──────────────────────────────────────────────────────┤
//  │ SRV  │ 서비스 위치 (특정 서비스의 호스트:포트)               │
//  │      │ _sip._tcp.example.com → sip.example.com:5060        │
//  └──────┴──────────────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  DNS 패킷 구조
// ════════════════════════════════════════════════════════════════════
//
//  DNS는 UDP 포트 53 사용 (512바이트 초과 시 TCP)
//
//  ┌──────────────────────────────────┐
//  │          DNS 헤더 (12바이트)      │
//  ├──────────────────────────────────┤
//  │          Question Section        │  ← 질문 (도메인 이름 + 타입)
//  ├──────────────────────────────────┤
//  │          Answer Section          │  ← 답변 (IP 주소 등)
//  ├──────────────────────────────────┤
//  │          Authority Section       │  ← 권한 네임서버
//  ├──────────────────────────────────┤
//  │          Additional Section      │  ← 추가 정보
//  └──────────────────────────────────┘

// ── DNS 헤더 구조체 (12바이트) ──
#pragma pack(push, 1)
struct DNSHeader {
    uint16_t id;             // 트랜잭션 ID (질의/응답 매칭용)
    uint16_t flags;          // 플래그 (QR, OPCODE, AA, TC, RD, RA, RCODE)
    uint16_t qd_count;      // Question 수 (보통 1)
    uint16_t an_count;      // Answer 수
    uint16_t ns_count;      // Authority 수
    uint16_t ar_count;      // Additional 수
};
#pragma pack(pop)

// DNS 레코드 타입 상수
namespace DNSType {
    constexpr uint16_t A     = 1;    // IPv4 주소
    constexpr uint16_t NS    = 2;    // 네임서버
    constexpr uint16_t CNAME = 5;    // 별칭
    constexpr uint16_t SOA   = 6;    // 권한 시작
    constexpr uint16_t PTR   = 12;   // 역방향 조회
    constexpr uint16_t MX    = 15;   // 메일 서버
    constexpr uint16_t TXT   = 16;   // 텍스트
    constexpr uint16_t AAAA  = 28;   // IPv6 주소
    constexpr uint16_t SRV   = 33;   // 서비스 위치
}

// DNS 레코드 타입을 문자열로
std::string dns_type_to_string(uint16_t type) {
    switch (type) {
        case DNSType::A:     return "A";
        case DNSType::NS:    return "NS";
        case DNSType::CNAME: return "CNAME";
        case DNSType::SOA:   return "SOA";
        case DNSType::PTR:   return "PTR";
        case DNSType::MX:    return "MX";
        case DNSType::TXT:   return "TXT";
        case DNSType::AAAA:  return "AAAA";
        case DNSType::SRV:   return "SRV";
        default:             return "TYPE" + std::to_string(type);
    }
}

// ════════════════════════════════════════════════════════════════════
//  DNS 캐시 엔트리
// ════════════════════════════════════════════════════════════════════

struct DNSCacheEntry {
    std::string domain;        // 도메인 이름
    uint16_t type;             // 레코드 타입
    std::string value;         // 값 (IP 주소 등)
    uint32_t ttl;              // Time To Live (초)
    std::chrono::steady_clock::time_point created;  // 생성 시각

    // TTL 만료 확인
    bool is_expired() const {
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(
            now - created).count();
        return elapsed >= ttl;
    }

    // 남은 TTL
    int remaining_ttl() const {
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(
            now - created).count();
        int remaining = static_cast<int>(ttl) - static_cast<int>(elapsed);
        return remaining > 0 ? remaining : 0;
    }
};

// ════════════════════════════════════════════════════════════════════
//  DNS 캐시 (로컬 DNS 캐시 서버 시뮬레이션)
// ════════════════════════════════════════════════════════════════════
//
//  ★ DNS 캐싱이 왜 중요한가?
//     - 매번 루트 DNS부터 찾으면 느림!
//     - 한번 찾은 결과를 TTL 동안 저장
//     - 다음에 같은 질의가 오면 캐시에서 바로 응답
//
//  비유: 전화번호부에서 찾은 번호를 메모장에 적어두기
//        메모장 먼저 확인 → 없으면 전화번호부 검색

class DNSCache {
private:
    std::vector<DNSCacheEntry> cache_;

public:
    // 캐시에 추가
    void add(const std::string& domain, uint16_t type,
             const std::string& value, uint32_t ttl) {
        DNSCacheEntry entry;
        entry.domain = domain;
        entry.type = type;
        entry.value = value;
        entry.ttl = ttl;
        entry.created = std::chrono::steady_clock::now();

        // 기존 엔트리 제거 후 추가
        cache_.erase(
            std::remove_if(cache_.begin(), cache_.end(),
                [&](const DNSCacheEntry& e) {
                    return e.domain == domain && e.type == type;
                }),
            cache_.end()
        );
        cache_.push_back(entry);
    }

    // 캐시 조회
    bool lookup(const std::string& domain, uint16_t type, std::string& value) const {
        for (const auto& entry : cache_) {
            if (entry.domain == domain && entry.type == type && !entry.is_expired()) {
                value = entry.value;
                return true;  // 캐시 히트!
            }
        }
        return false;  // 캐시 미스 → 실제 DNS 질의 필요
    }

    // 만료된 엔트리 정리
    void cleanup() {
        cache_.erase(
            std::remove_if(cache_.begin(), cache_.end(),
                [](const DNSCacheEntry& e) { return e.is_expired(); }),
            cache_.end()
        );
    }

    // 캐시 상태 출력
    void print() const {
        std::cout << "\n  ┌─────────────────────────────────────────────────────────┐" << std::endl;
        std::cout << "  │                    DNS 캐시 상태                         │" << std::endl;
        std::cout << "  ├────────────────────┬──────┬──────────────────┬──────────┤" << std::endl;
        std::cout << "  │ 도메인             │ 타입 │ 값               │ TTL(초)  │" << std::endl;
        std::cout << "  ├────────────────────┼──────┼──────────────────┼──────────┤" << std::endl;

        for (const auto& entry : cache_) {
            std::cout << "  │ " << std::setw(18) << std::left << entry.domain
                      << " │ " << std::setw(4) << dns_type_to_string(entry.type)
                      << " │ " << std::setw(16) << entry.value
                      << " │ " << std::setw(8) << entry.remaining_ttl()
                      << " │" << std::endl;
        }
        std::cout << "  └────────────────────┴──────┴──────────────────┴──────────┘" << std::endl;
    }
};

// ════════════════════════════════════════════════════════════════════
//  DNS 레코드 데이터베이스 (간이 DNS 서버용)
// ════════════════════════════════════════════════════════════════════

struct DNSRecord {
    std::string domain;
    uint16_t type;
    std::string value;
    uint32_t ttl;
    int priority;      // MX 레코드의 우선순위
};

class DNSZone {
private:
    std::vector<DNSRecord> records_;

public:
    // 레코드 추가
    void add_record(const std::string& domain, uint16_t type,
                    const std::string& value, uint32_t ttl = 3600,
                    int priority = 0) {
        records_.push_back({domain, type, value, ttl, priority});
    }

    // 레코드 조회
    std::vector<DNSRecord> query(const std::string& domain, uint16_t type) const {
        std::vector<DNSRecord> results;
        for (const auto& rec : records_) {
            if (rec.domain == domain && rec.type == type) {
                results.push_back(rec);
            }
        }
        return results;
    }

    // 모든 레코드 출력
    void print() const {
        std::cout << "\n  ┌─────────────────────────────────────────────────────────────┐" << std::endl;
        std::cout << "  │                    DNS 존(Zone) 레코드                        │" << std::endl;
        std::cout << "  ├────────────────────┬──────┬──────────────────────┬──────────┤" << std::endl;
        std::cout << "  │ 도메인             │ 타입 │ 값                   │ TTL      │" << std::endl;
        std::cout << "  ├────────────────────┼──────┼──────────────────────┼──────────┤" << std::endl;

        for (const auto& rec : records_) {
            std::string display_val = rec.value;
            if (rec.type == DNSType::MX) {
                display_val = std::to_string(rec.priority) + " " + rec.value;
            }
            std::cout << "  │ " << std::setw(18) << std::left << rec.domain
                      << " │ " << std::setw(4) << dns_type_to_string(rec.type)
                      << " │ " << std::setw(20) << display_val
                      << " │ " << std::setw(8) << rec.ttl
                      << " │" << std::endl;
        }
        std::cout << "  └────────────────────┴──────┴──────────────────────┴──────────┘" << std::endl;
    }
};

// ════════════════════════════════════════════════════════════════════
//  DNS 쿼리 패킷 빌더
// ════════════════════════════════════════════════════════════════════

// 도메인 이름을 DNS 형식으로 인코딩
// "www.example.com" → "\x03www\x07example\x03com\x00"
// ★ 각 라벨의 길이를 앞에 붙이는 형식
std::vector<uint8_t> encode_domain_name(const std::string& domain) {
    std::vector<uint8_t> encoded;
    std::istringstream iss(domain);
    std::string label;

    // 점(.)으로 구분된 각 라벨 처리
    while (std::getline(iss, label, '.')) {
        encoded.push_back(static_cast<uint8_t>(label.size()));  // 라벨 길이
        for (char c : label) {
            encoded.push_back(static_cast<uint8_t>(c));
        }
    }
    encoded.push_back(0);  // 끝 표시 (루트 라벨)

    return encoded;
}

// DNS 쿼리 패킷 생성
std::vector<uint8_t> build_dns_query(const std::string& domain,
                                      uint16_t query_type = DNSType::A) {
    std::vector<uint8_t> packet;

    // 1. DNS 헤더 (12바이트)
    DNSHeader header = {};
    header.id = htons(0x1234);       // 트랜잭션 ID (임의)
    header.flags = htons(0x0100);    // RD=1 (재귀 질의 요청)
    header.qd_count = htons(1);     // 질문 1개

    // 헤더를 패킷에 추가
    const uint8_t* hdr_bytes = reinterpret_cast<const uint8_t*>(&header);
    packet.insert(packet.end(), hdr_bytes, hdr_bytes + sizeof(DNSHeader));

    // 2. Question 섹션
    // 2a. 도메인 이름 인코딩
    auto encoded_name = encode_domain_name(domain);
    packet.insert(packet.end(), encoded_name.begin(), encoded_name.end());

    // 2b. 쿼리 타입 (2바이트, 빅 엔디안)
    uint16_t qtype = htons(query_type);
    packet.push_back(static_cast<uint8_t>(qtype >> 8));
    packet.push_back(static_cast<uint8_t>(qtype & 0xFF));

    // 2c. 쿼리 클래스 (2바이트, IN = Internet = 1)
    uint16_t qclass = htons(1);
    packet.push_back(static_cast<uint8_t>(qclass >> 8));
    packet.push_back(static_cast<uint8_t>(qclass & 0xFF));

    return packet;
}

// ════════════════════════════════════════════════════════════════════
//  DNS 응답 파서
// ════════════════════════════════════════════════════════════════════

// DNS 응답에서 IP 주소 추출 (A 레코드)
struct DNSAnswer {
    std::string name;
    uint16_t type;
    uint32_t ttl;
    std::string rdata;    // A 레코드면 IP 주소
};

// 간단한 DNS 응답 파서 (A 레코드 전용)
std::vector<DNSAnswer> parse_dns_response(const uint8_t* data, int length) {
    std::vector<DNSAnswer> answers;

    if (length < static_cast<int>(sizeof(DNSHeader))) return answers;

    const DNSHeader* header = reinterpret_cast<const DNSHeader*>(data);
    int an_count = ntohs(header->an_count);
    int qd_count = ntohs(header->qd_count);

    // Question 섹션 건너뛰기
    int offset = sizeof(DNSHeader);
    for (int q = 0; q < qd_count; q++) {
        // 도메인 이름 건너뛰기
        while (offset < length && data[offset] != 0) {
            if ((data[offset] & 0xC0) == 0xC0) {
                offset += 2;  // 포인터 (2바이트)
                goto skip_qtype;
            }
            offset += data[offset] + 1;  // 라벨 길이 + 라벨
        }
        offset++;  // 0 (루트) 건너뛰기
        skip_qtype:
        offset += 4;  // QTYPE(2) + QCLASS(2)
    }

    // Answer 섹션 파싱
    for (int a = 0; a < an_count && offset < length; a++) {
        DNSAnswer answer;

        // 이름 필드 (포인터일 수 있음)
        if ((data[offset] & 0xC0) == 0xC0) {
            offset += 2;  // 포인터 건너뛰기
        } else {
            while (offset < length && data[offset] != 0) {
                offset += data[offset] + 1;
            }
            offset++;
        }

        if (offset + 10 > length) break;

        // 타입, 클래스, TTL, 데이터 길이
        answer.type = (static_cast<uint16_t>(data[offset]) << 8) | data[offset + 1];
        offset += 2;  // TYPE
        offset += 2;  // CLASS
        answer.ttl = (static_cast<uint32_t>(data[offset]) << 24) |
                     (static_cast<uint32_t>(data[offset + 1]) << 16) |
                     (static_cast<uint32_t>(data[offset + 2]) << 8) |
                     data[offset + 3];
        offset += 4;  // TTL

        uint16_t rdlength = (static_cast<uint16_t>(data[offset]) << 8) | data[offset + 1];
        offset += 2;  // RDLENGTH

        // A 레코드 (IPv4 주소, 4바이트)
        if (answer.type == DNSType::A && rdlength == 4 && offset + 4 <= length) {
            answer.rdata = std::to_string(data[offset]) + "." +
                          std::to_string(data[offset + 1]) + "." +
                          std::to_string(data[offset + 2]) + "." +
                          std::to_string(data[offset + 3]);
        } else {
            answer.rdata = "(type=" + dns_type_to_string(answer.type) +
                          ", len=" + std::to_string(rdlength) + ")";
        }

        offset += rdlength;
        answers.push_back(answer);
    }

    return answers;
}

// ════════════════════════════════════════════════════════════════════
//  DNS 질의기 (실제 DNS 서버에 UDP로 질의!)
// ════════════════════════════════════════════════════════════════════

// 실제 DNS 서버에 쿼리를 보내고 응답을 받는 함수
// ★ 이것이 실제로 동작하는 DNS 클라이언트!
bool dns_query(const std::string& domain, const std::string& dns_server,
               uint16_t query_type = DNSType::A) {
    std::cout << "\n  ── DNS 질의 ──" << std::endl;
    std::cout << "  도메인: " << domain << std::endl;
    std::cout << "  타입: " << dns_type_to_string(query_type) << std::endl;
    std::cout << "  DNS 서버: " << dns_server << std::endl;

    SOCKET_INIT();

    // UDP 소켓 생성 (DNS는 UDP 포트 53 사용)
    SOCKET sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock == INVALID_SOCKET) {
        std::cerr << "  ✗ 소켓 생성 실패" << std::endl;
        SOCKET_CLEANUP();
        return false;
    }

    // 타임아웃 설정 (3초)
    #ifdef _WIN32
    DWORD timeout = 3000;
    #else
    struct timeval timeout;
    timeout.tv_sec = 3;
    timeout.tv_usec = 0;
    #endif
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO,
               reinterpret_cast<const char*>(&timeout), sizeof(timeout));

    // DNS 서버 주소 설정
    struct sockaddr_in server_addr = {};
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(53);  // DNS 포트
    inet_pton(AF_INET, dns_server.c_str(), &server_addr.sin_addr);

    // DNS 쿼리 패킷 생성
    auto query_packet = build_dns_query(domain, query_type);

    std::cout << "  쿼리 패킷 크기: " << query_packet.size() << " bytes" << std::endl;

    // 쿼리 전송
    int sent = sendto(sock, reinterpret_cast<const char*>(query_packet.data()),
                      static_cast<int>(query_packet.size()), 0,
                      reinterpret_cast<struct sockaddr*>(&server_addr),
                      sizeof(server_addr));
    if (sent == SOCKET_ERROR) {
        std::cerr << "  ✗ 전송 실패: " << SOCKET_ERROR_CODE << std::endl;
        CLOSE_SOCKET(sock);
        SOCKET_CLEANUP();
        return false;
    }

    // 응답 수신
    uint8_t response[512];
    struct sockaddr_in from_addr = {};
    socklen_t from_len = sizeof(from_addr);

    int received = recvfrom(sock, reinterpret_cast<char*>(response),
                            sizeof(response), 0,
                            reinterpret_cast<struct sockaddr*>(&from_addr),
                            &from_len);

    CLOSE_SOCKET(sock);
    SOCKET_CLEANUP();

    if (received <= 0) {
        std::cerr << "  ✗ 응답 없음 (타임아웃)" << std::endl;
        return false;
    }

    std::cout << "  응답 크기: " << received << " bytes" << std::endl;

    // 응답 파싱
    auto answers = parse_dns_response(response, received);

    if (answers.empty()) {
        std::cout << "  결과: 레코드 없음 (NXDOMAIN?)" << std::endl;
        return false;
    }

    std::cout << "\n  ┌────────────────────────────────────────┐" << std::endl;
    std::cout << "  │          DNS 질의 결과                  │" << std::endl;
    std::cout << "  ├──────┬──────────────────┬──────────────┤" << std::endl;
    std::cout << "  │ 타입 │ 값               │ TTL          │" << std::endl;
    std::cout << "  ├──────┼──────────────────┼──────────────┤" << std::endl;
    for (const auto& ans : answers) {
        std::cout << "  │ " << std::setw(4) << std::left << dns_type_to_string(ans.type)
                  << " │ " << std::setw(16) << ans.rdata
                  << " │ " << std::setw(12) << ans.ttl
                  << " │" << std::endl;
    }
    std::cout << "  └──────┴──────────────────┴──────────────┘" << std::endl;

    return true;
}

// ════════════════════════════════════════════════════════════════════
//  hosts 파일 파서
// ════════════════════════════════════════════════════════════════════
//
//  hosts 파일이란?
//  ──────────────
//  DNS보다 먼저 확인되는 로컬 도메인-IP 매핑 파일
//  위치:
//    - Windows: C:\Windows\System32\drivers\etc\hosts
//    - Linux:   /etc/hosts
//
//  형식:
//    127.0.0.1       localhost
//    192.168.1.100   myserver.local
//    # 주석
//
//  ★ 용도:
//    - 개발 환경에서 로컬 도메인 설정
//    - 특정 사이트 차단 (0.0.0.0 광고서버.com)
//    - DNS 우회 테스트

class HostsFile {
private:
    std::map<std::string, std::string> entries_;

public:
    // 엔트리 추가 (hosts 파일 형식으로)
    void add_entry(const std::string& ip, const std::string& hostname) {
        entries_[hostname] = ip;
    }

    // 호스트명으로 IP 조회
    bool lookup(const std::string& hostname, std::string& ip) const {
        auto it = entries_.find(hostname);
        if (it != entries_.end()) {
            ip = it->second;
            return true;
        }
        return false;
    }

    // hosts 파일 내용 출력
    void print() const {
        std::cout << "\n  ┌──────────────────────────────────────────┐" << std::endl;
        std::cout << "  │          hosts 파일 내용                   │" << std::endl;
        std::cout << "  ├──────────────────────────────────────────┤" << std::endl;
        for (const auto& [hostname, ip] : entries_) {
            std::cout << "  │  " << std::setw(16) << std::left << ip
                      << " " << hostname << std::endl;
        }
        std::cout << "  └──────────────────────────────────────────┘" << std::endl;
    }
};

// ════════════════════════════════════════════════════════════════════
//  DNS 보안 개요
// ════════════════════════════════════════════════════════════════════
//
//  ┌───────────────────────────────────────────────────────────────┐
//  │  DNS 보안 위협과 대응                                         │
//  │                                                               │
//  │  위협 1: DNS 스푸핑 (Spoofing)                                │
//  │    공격자가 가짜 DNS 응답을 보내서 잘못된 IP로 유도           │
//  │    → 대응: DNSSEC (응답에 디지털 서명 추가)                  │
//  │                                                               │
//  │  위협 2: DNS 도청                                             │
//  │    DNS 질의를 엿봐서 어떤 사이트 방문하는지 추적             │
//  │    → 대응: DoH (DNS over HTTPS, 포트 443)                    │
//  │           DoT (DNS over TLS, 포트 853)                       │
//  │                                                               │
//  │  위협 3: DNS 터널링                                           │
//  │    DNS 질의/응답에 데이터를 숨겨서 방화벽 우회               │
//  │    → 대응: DNS 트래픽 모니터링                               │
//  │                                                               │
//  │  ★ DDNS (Dynamic DNS):                                       │
//  │    유동 IP에서도 도메인 사용 가능                             │
//  │    IP가 바뀔 때마다 DNS 레코드 자동 업데이트                 │
//  │    예: 집 서버를 mypc.duckdns.org로 접속                     │
//  └───────────────────────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  간이 DNS 서버 (로컬 DNS 캐시/프록시)
// ════════════════════════════════════════════════════════════════════

void run_simple_dns_server(uint16_t port = 5353) {
    std::cout << "\n  ── 간이 DNS 서버 시작 (포트: " << port << ") ──" << std::endl;

    SOCKET_INIT();

    SOCKET sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock == INVALID_SOCKET) {
        std::cerr << "  ✗ 소켓 생성 실패" << std::endl;
        SOCKET_CLEANUP();
        return;
    }

    struct sockaddr_in server_addr = {};
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);

    if (bind(sock, reinterpret_cast<struct sockaddr*>(&server_addr),
             sizeof(server_addr)) == SOCKET_ERROR) {
        std::cerr << "  ✗ 바인딩 실패: " << SOCKET_ERROR_CODE << std::endl;
        CLOSE_SOCKET(sock);
        SOCKET_CLEANUP();
        return;
    }

    std::cout << "  DNS 서버 대기 중... (nslookup -port=" << port
              << " domain 127.0.0.1 로 테스트)" << std::endl;

    // 로컬 레코드 설정
    DNSZone zone;
    zone.add_record("myapp.local", DNSType::A, "127.0.0.1", 3600);
    zone.add_record("db.local", DNSType::A, "192.168.1.100", 3600);
    zone.add_record("api.local", DNSType::A, "192.168.1.200", 3600);
    zone.print();

    // 질의 수신 (1회만)
    uint8_t buffer[512];
    struct sockaddr_in client_addr = {};
    socklen_t client_len = sizeof(client_addr);

    int received = recvfrom(sock, reinterpret_cast<char*>(buffer),
                            sizeof(buffer), 0,
                            reinterpret_cast<struct sockaddr*>(&client_addr),
                            &client_len);

    if (received > 0) {
        char client_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, sizeof(client_ip));
        std::cout << "\n  질의 수신 from " << client_ip << ":"
                  << ntohs(client_addr.sin_port) << std::endl;
        std::cout << "  패킷 크기: " << received << " bytes" << std::endl;

        // ★ 실제 DNS 서버 구현은 매우 복잡하므로
        //    여기서는 수신 확인만 하고 종료합니다.
        //    (응답 생성은 질의의 역과정)
    }

    CLOSE_SOCKET(sock);
    SOCKET_CLEANUP();
    std::cout << "  DNS 서버 종료" << std::endl;
}

// ════════════════════════════════════════════════════════════════════
//  DNS 질의 과정 시뮬레이션 (교육용)
// ════════════════════════════════════════════════════════════════════

void simulate_dns_resolution(const std::string& domain) {
    std::cout << "\n  ── \"" << domain << "\" 질의 과정 시뮬레이션 ──" << std::endl;

    // hosts 파일
    HostsFile hosts;
    hosts.add_entry("127.0.0.1", "localhost");
    hosts.add_entry("192.168.1.100", "myserver.local");

    // DNS 캐시
    DNSCache cache;
    cache.add("google.com", DNSType::A, "142.250.196.110", 300);

    // 1단계: hosts 파일 확인
    std::cout << "\n  [1] hosts 파일 확인..." << std::endl;
    std::string ip;
    if (hosts.lookup(domain, ip)) {
        std::cout << "      ✓ hosts 파일에서 발견: " << domain << " → " << ip << std::endl;
        return;
    }
    std::cout << "      ✗ hosts 파일에 없음" << std::endl;

    // 2단계: DNS 캐시 확인
    std::cout << "  [2] DNS 캐시 확인..." << std::endl;
    if (cache.lookup(domain, DNSType::A, ip)) {
        std::cout << "      ✓ 캐시 히트: " << domain << " → " << ip << std::endl;
        return;
    }
    std::cout << "      ✗ 캐시 미스" << std::endl;

    // 3단계: DNS 서버에 질의 (시뮬레이션)
    std::cout << "  [3] 로컬 DNS 서버에 재귀 질의..." << std::endl;

    // 4단계: 반복 질의 과정 (시뮬레이션)
    // 도메인을 역순으로 분해: com → example → www
    std::vector<std::string> labels;
    std::istringstream iss(domain);
    std::string label;
    while (std::getline(iss, label, '.')) {
        labels.push_back(label);
    }

    std::cout << "  [4] 반복 질의 시작..." << std::endl;
    std::cout << "      → 루트 DNS 서버에 질의: \"" << domain << " 아세요?\"" << std::endl;

    if (labels.size() >= 2) {
        std::string tld = labels.back();
        std::cout << "      ← \"." << tld << " TLD 서버로 가보세요\"" << std::endl;
        std::cout << "      → ." << tld << " TLD 서버에 질의: \"" << domain << " 아세요?\"" << std::endl;

        // 2차 도메인
        std::string sld = labels[labels.size() - 2] + "." + tld;
        std::cout << "      ← \"" << sld << " 권한 DNS 서버로 가보세요\"" << std::endl;
        std::cout << "      → " << sld << " 권한 DNS에 질의: \"" << domain << " 아세요?\"" << std::endl;
    }

    // 결과 (시뮬레이션이므로 가짜 IP)
    std::string fake_ip = "203.0.113.42";
    std::cout << "      ← \"" << domain << "의 IP는 " << fake_ip << " 입니다!\"" << std::endl;

    // 캐시에 저장
    cache.add(domain, DNSType::A, fake_ip, 3600);
    std::cout << "\n  [5] 캐시에 저장 (TTL=3600초)" << std::endl;
    std::cout << "  [6] 클라이언트에게 응답: " << domain << " → " << fake_ip << std::endl;

    cache.print();
}

// ════════════════════════════════════════════════════════════════════
//  메인 함수
// ════════════════════════════════════════════════════════════════════

int main(int argc, char* argv[]) {
    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;
    std::cout << "  DNS 완전 정복 - 도메인 이름 시스템" << std::endl;
    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;

    // 명령행 모드
    if (argc > 1) {
        std::string mode = argv[1];

        // DNS 서버 모드
        if (mode == "dns-server") {
            uint16_t port = (argc > 2) ? std::stoi(argv[2]) : 5353;
            run_simple_dns_server(port);
            return 0;
        }
        // DNS 질의 모드
        else if (mode == "query" && argc > 2) {
            std::string domain = argv[2];
            std::string dns_server = (argc > 3) ? argv[3] : "8.8.8.8";
            dns_query(domain, dns_server);
            return 0;
        }
    }

    std::cout << R"(
  ┌───────────────────────────────────────────────────────┐
  │  사용법:                                               │
  │    ./dns_system query <domain> [dns-server]            │
  │    ./dns_system dns-server [port]                      │
  │                                                        │
  │  예시:                                                 │
  │    ./dns_system query google.com                       │
  │    ./dns_system query example.com 1.1.1.1              │
  │    ./dns_system dns-server 5353                        │
  └───────────────────────────────────────────────────────┘
)" << std::endl;

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  1. DNS 레코드 종류 시연
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  1. DNS 레코드 종류 시연" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    DNSZone zone;
    // 가상의 example.com 존 레코드
    zone.add_record("example.com", DNSType::A, "93.184.216.34", 3600);
    zone.add_record("example.com", DNSType::AAAA, "2606:2800:220:1::34", 3600);
    zone.add_record("www.example.com", DNSType::CNAME, "example.com", 3600);
    zone.add_record("example.com", DNSType::MX, "mail.example.com", 3600, 10);
    zone.add_record("example.com", DNSType::MX, "mail2.example.com", 3600, 20);
    zone.add_record("example.com", DNSType::NS, "ns1.example.com", 86400);
    zone.add_record("example.com", DNSType::NS, "ns2.example.com", 86400);
    zone.add_record("example.com", DNSType::TXT, "v=spf1 +mx ~all", 3600);
    zone.print();

    // 레코드 질의 시연
    std::cout << "\n  질의: example.com A 레코드" << std::endl;
    auto results = zone.query("example.com", DNSType::A);
    for (const auto& r : results) {
        std::cout << "    → " << r.value << " (TTL=" << r.ttl << ")" << std::endl;
    }

    std::cout << "\n  질의: example.com MX 레코드" << std::endl;
    results = zone.query("example.com", DNSType::MX);
    for (const auto& r : results) {
        std::cout << "    → priority=" << r.priority << " " << r.value
                  << " (TTL=" << r.ttl << ")" << std::endl;
    }

    std::cout << "\n  질의: www.example.com CNAME 레코드" << std::endl;
    results = zone.query("www.example.com", DNSType::CNAME);
    for (const auto& r : results) {
        std::cout << "    → " << r.value << " (별칭 → 원본 도메인)" << std::endl;
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  2. DNS 캐시 시뮬레이션
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  2. DNS 캐시 시뮬레이션" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    DNSCache cache;
    cache.add("google.com", DNSType::A, "142.250.196.110", 300);
    cache.add("github.com", DNSType::A, "20.200.245.247", 60);
    cache.add("naver.com", DNSType::A, "223.130.200.104", 600);
    cache.print();

    // 캐시 조회 테스트
    std::string ip;
    std::cout << "\n  캐시 조회 테스트:" << std::endl;

    if (cache.lookup("google.com", DNSType::A, ip)) {
        std::cout << "    google.com → " << ip << " (캐시 히트!)" << std::endl;
    }

    if (!cache.lookup("unknown.com", DNSType::A, ip)) {
        std::cout << "    unknown.com → 캐시 미스 (DNS 질의 필요)" << std::endl;
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  3. hosts 파일 시뮬레이션
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  3. hosts 파일 시뮬레이션" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    HostsFile hosts;
    hosts.add_entry("127.0.0.1", "localhost");
    hosts.add_entry("::1", "localhost6");
    hosts.add_entry("192.168.1.100", "devserver.local");
    hosts.add_entry("192.168.1.200", "dbserver.local");
    hosts.add_entry("0.0.0.0", "ads.example.com");  // 광고 차단!
    hosts.print();

    std::cout << "\n  ★ 0.0.0.0 ads.example.com → 광고 차단 효과!" << std::endl;
    std::cout << "    해당 도메인 접속 시 0.0.0.0으로 리다이렉트 → 접속 불가" << std::endl;

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  4. DNS 질의 과정 시뮬레이션
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  4. DNS 질의 과정 시뮬레이션" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    simulate_dns_resolution("www.example.com");

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  5. DNS 패킷 빌더 시연
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  5. DNS 쿼리 패킷 구조 분석" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    auto packet = build_dns_query("www.google.com");

    std::cout << "\n  DNS 쿼리 패킷 (www.google.com A):" << std::endl;
    std::cout << "  크기: " << packet.size() << " bytes" << std::endl;
    std::cout << "\n  헥스 덤프:" << std::endl;
    std::cout << "  ";
    for (size_t i = 0; i < packet.size(); i++) {
        std::cout << std::hex << std::setw(2) << std::setfill('0')
                  << static_cast<int>(packet[i]) << " ";
        if ((i + 1) % 16 == 0) std::cout << "\n  ";
    }
    std::cout << std::dec << std::setfill(' ') << std::endl;

    // 도메인 인코딩 시연
    std::cout << "\n  도메인 인코딩 과정:" << std::endl;
    std::cout << "  \"www.google.com\" →" << std::endl;
    auto encoded = encode_domain_name("www.google.com");
    std::cout << "  ";
    for (auto b : encoded) {
        if (b >= 32 && b < 127) {
            std::cout << "'" << static_cast<char>(b) << "' ";
        } else {
            std::cout << "0x" << std::hex << std::setw(2) << std::setfill('0')
                      << static_cast<int>(b) << std::dec << std::setfill(' ') << " ";
        }
    }
    std::cout << std::endl;
    std::cout << "  = [3]www[6]google[3]com[0]" << std::endl;

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  6. 실제 DNS 질의 (네트워크 필요)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  6. 실제 DNS 질의 (Google DNS 8.8.8.8)" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    // ★ 실제 네트워크 연결이 필요합니다!
    dns_query("google.com", "8.8.8.8");
    dns_query("naver.com", "8.8.8.8");

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  정리
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  정리: DNS 핵심 요약" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    std::cout << R"(
  ★ 기억해야 할 핵심:

  1. DNS = 도메인 → IP 변환 (인터넷의 전화번호부)
  2. 조회 순서: 캐시 → hosts → DNS 서버
  3. 질의 방식: 재귀(클라이언트→리졸버) + 반복(리졸버→DNS들)
  4. 주요 레코드: A(IPv4), AAAA(IPv6), CNAME(별칭), MX(메일)
  5. DNS는 UDP 포트 53 사용 (큰 응답은 TCP)
  6. TTL로 캐시 유효 기간 관리

  ★ 실무 팁:
  - nslookup, dig 명령어로 DNS 디버깅
  - /etc/hosts로 로컬 도메인 설정 (개발환경)
  - DNS 서버: 8.8.8.8 (Google), 1.1.1.1 (Cloudflare)
  - DDNS: 유동 IP에서 고정 도메인 사용
  - DoH/DoT: 프라이버시를 위한 암호화된 DNS
)" << std::endl;

    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;
    std::cout << "  DNS 학습 완료!" << std::endl;
    std::cout << "  다음: 05_http_protocol (HTTP 프로토콜)" << std::endl;
    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;

    return 0;
}
