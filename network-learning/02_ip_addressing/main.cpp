/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  네트워크 학습 02단계: IP 주소 완전 정복
  ─────────────────────────────────────────────────
  IPv4 주소 체계, 서브넷팅, NAT, DHCP, IPv6 기초

  ■ 컴파일 방법:
      g++ -std=c++17 -Wall -lws2_32 -o ip_addressing main.cpp

  ■ 이 파일을 배우면 할 수 있는 것:
      - IP 주소의 구조와 의미 완전 이해
      - 서브넷 계산을 직접 할 수 있음
      - NAT(공유기)의 동작 원리 파악
      - DHCP 자동 IP 할당 과정 이해
      - C++로 서브넷 계산기/IP 검증기 구현

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#include <iostream>
#include <cstdint>
#include <string>
#include <vector>
#include <sstream>
#include <iomanip>
#include <bitset>
#include <algorithm>
#include <array>
#include <cmath>

// ┌───────────────────────────────────────────────────────────────────┐
// │  ★ 주의: 이 파일은 IP 주소 개념 학습 + 계산기 구현입니다.        │
// │  실제 소켓 프로그래밍은 03_tcp_udp에서 다룹니다.                  │
// └───────────────────────────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  IPv4 주소 기초 - "인터넷의 우편번호"
// ════════════════════════════════════════════════════════════════════
//
//  IP 주소란?
//  ─────────
//  인터넷에 연결된 모든 장치에 부여되는 고유 번호
//  마치 집마다 고유한 주소(서울시 강남구 ...)가 있는 것처럼
//  컴퓨터도 네트워크에서 고유한 주소가 필요합니다.
//
//  IPv4 주소 구조 (32비트):
//
//  ┌────────┬────────┬────────┬────────┐
//  │ 옥텟1  │ 옥텟2  │ 옥텟3  │ 옥텟4  │
//  │ 8비트  │ 8비트  │ 8비트  │ 8비트  │
//  └────────┴────────┴────────┴────────┘
//     192  .  168   .   1    .   10
//
//  ★ 각 옥텟: 0 ~ 255 (8비트 = 2^8 = 256가지)
//  ★ 총 IP 개수: 2^32 = 약 43억 개 (부족해서 IPv6 등장!)
//
//  이진수 표현:
//  192.168.1.10
//  = 11000000.10101000.00000001.00001010
//    ^^^^^^^^ ^^^^^^^^ ^^^^^^^^ ^^^^^^^^
//    옥텟1    옥텟2    옥텟3    옥텟4

// ════════════════════════════════════════════════════════════════════
//  서브넷 마스크 - "네트워크와 호스트 구분선"
// ════════════════════════════════════════════════════════════════════
//
//  서브넷 마스크란?
//  ───────────────
//  IP 주소에서 "네트워크 부분"과 "호스트 부분"을 구분하는 마스크
//
//  비유: 우편번호의 "지역 코드" vs "상세 번호"
//    06000 (강남구) = 지역코드: 06, 상세번호: 000
//    IP도 마찬가지:
//    192.168.1.10 / 255.255.255.0
//    ^^^^^^^^^^^    ← 네트워크 부분 (동네)
//             ^^    ← 호스트 부분 (집 번호)
//
//  CIDR 표기법:
//  ┌──────────────────┬────────┬───────────┬──────────┐
//  │ 서브넷 마스크     │ CIDR   │ 네트워크  │ 호스트수 │
//  ├──────────────────┼────────┼───────────┼──────────┤
//  │ 255.0.0.0        │ /8     │ Class A   │ 16M      │
//  │ 255.255.0.0      │ /16    │ Class B   │ 65,534   │
//  │ 255.255.255.0    │ /24    │ Class C   │ 254      │
//  │ 255.255.255.128  │ /25    │           │ 126      │
//  │ 255.255.255.192  │ /26    │           │ 62       │
//  │ 255.255.255.224  │ /27    │           │ 30       │
//  │ 255.255.255.240  │ /28    │           │ 14       │
//  │ 255.255.255.248  │ /29    │           │ 6        │
//  │ 255.255.255.252  │ /30    │           │ 2        │
//  └──────────────────┴────────┴───────────┴──────────┘
//
//  ★ 호스트 수 = 2^(32-CIDR) - 2
//     (-2인 이유: 네트워크 주소 + 브로드캐스트 주소 제외)

// ════════════════════════════════════════════════════════════════════
//  Private IP vs Public IP - "사내 내선번호 vs 실제 전화번호"
// ════════════════════════════════════════════════════════════════════
//
//  ┌───────────────────────────────────────────────────────────────┐
//  │  Private IP (사설 IP) - 내부 네트워크에서만 사용              │
//  │                                                               │
//  │  비유: 회사 내선번호 (101, 102, 103...)                      │
//  │        회사 밖에서는 내선번호로 전화할 수 없음!               │
//  │                                                               │
//  │  ┌──────────────────────┬───────────────────────────────┐    │
//  │  │ 클래스 │ IP 범위                                      │    │
//  │  ├────────┼──────────────────────────────────────────────┤    │
//  │  │ A      │ 10.0.0.0    ~ 10.255.255.255   (/8)         │    │
//  │  │ B      │ 172.16.0.0  ~ 172.31.255.255   (/12)        │    │
//  │  │ C      │ 192.168.0.0 ~ 192.168.255.255  (/16)        │    │
//  │  └────────┴──────────────────────────────────────────────┘    │
//  │                                                               │
//  │  ★ 집에서 쓰는 192.168.x.x가 바로 Private IP!               │
//  │  ★ 회사에서 쓰는 10.x.x.x도 Private IP!                     │
//  └───────────────────────────────────────────────────────────────┘
//
//  ┌───────────────────────────────────────────────────────────────┐
//  │  Public IP (공인 IP) - 인터넷에서 유일한 주소                │
//  │                                                               │
//  │  비유: 실제 전화번호 (02-1234-5678)                          │
//  │        전 세계 어디서든 이 번호로 연결 가능!                  │
//  │                                                               │
//  │  ISP(인터넷 서비스 제공자)로부터 할당받음                    │
//  │  예: 211.xxx.xxx.xxx (KT), 125.xxx.xxx.xxx (SKT) 등         │
//  └───────────────────────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  NAT (Network Address Translation) - "공유기의 핵심 원리"
// ════════════════════════════════════════════════════════════════════
//
//  NAT란?
//  ──────
//  Private IP ↔ Public IP 변환 기술
//  하나의 공인 IP로 여러 장치가 인터넷 사용 가능!
//
//  비유: 회사 대표 전화번호
//    외부 → 02-1234-0000 (대표번호)
//    교환원이 내선 101, 102, 103으로 연결해줌
//
//  ┌─────────────────────────────────────────────────────┐
//  │                 NAT 동작 과정                        │
//  │                                                      │
//  │  [PC1: 192.168.1.10]──┐                              │
//  │  [PC2: 192.168.1.20]──┼── [공유기/NAT] ── Internet  │
//  │  [PC3: 192.168.1.30]──┘  211.100.1.1                │
//  │                                                      │
//  │  PC1 → 구글 요청:                                   │
//  │  ┌──────────────────────────────────────────┐       │
//  │  │ 출발: 192.168.1.10:50000 (사설IP:포트)   │       │
//  │  │ 도착: 8.8.8.8:443                        │       │
//  │  └──────────────────────────────────────────┘       │
//  │          ↓ NAT 변환                                  │
//  │  ┌──────────────────────────────────────────┐       │
//  │  │ 출발: 211.100.1.1:40001 (공인IP:변환포트)│       │
//  │  │ 도착: 8.8.8.8:443                        │       │
//  │  └──────────────────────────────────────────┘       │
//  │                                                      │
//  │  ★ NAT 테이블에 매핑 저장:                           │
//  │    211.100.1.1:40001 ↔ 192.168.1.10:50000           │
//  │    211.100.1.1:40002 ↔ 192.168.1.20:50000           │
//  └─────────────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  DHCP (Dynamic Host Configuration Protocol) - "자동 IP 할당"
// ════════════════════════════════════════════════════════════════════
//
//  DHCP란?
//  ──────
//  네트워크에 연결하면 자동으로 IP를 받는 시스템
//  "카페 와이파이에 연결하면 자동으로 IP가 잡히는 것!"
//
//  DHCP 4단계 과정 (DORA):
//
//  ┌─────────────────────────────────────────────────────┐
//  │  Client                         DHCP Server         │
//  │    │                                │               │
//  │    │── 1. Discover ────────────────>│ "IP 필요!"   │
//  │    │   (브로드캐스트 255.255.255.255)│               │
//  │    │                                │               │
//  │    │<── 2. Offer ──────────────────│ "192.168.1.50"│
//  │    │   "이 IP 쓸래?"               │   드려요!"    │
//  │    │                                │               │
//  │    │── 3. Request ────────────────>│ "그 IP 쓸게!" │
//  │    │   "192.168.1.50 주세요!"      │               │
//  │    │                                │               │
//  │    │<── 4. ACK ────────────────────│ "확인! 사용"  │
//  │    │   임대 시간: 24시간           │   하세요!"    │
//  │    │                                │               │
//  │    │  ★ 이제 192.168.1.50 사용 가능!│              │
//  └─────────────────────────────────────────────────────┘
//
//  DHCP가 할당하는 정보:
//    - IP 주소
//    - 서브넷 마스크
//    - 기본 게이트웨이 (공유기 주소)
//    - DNS 서버 주소
//    - 임대 시간 (lease time)

// ════════════════════════════════════════════════════════════════════
//  IPv6 기초 - "차세대 주소 체계"
// ════════════════════════════════════════════════════════════════════
//
//  왜 IPv6가 필요한가?
//  ─────────────────
//  IPv4: 2^32 = 약 43억 개 → 이미 고갈됨!
//  IPv6: 2^128 = 340,282,366,920,938,463,463,374,607,431,768,211,456 개
//        → 지구상 모래알 개수보다 많음
//
//  IPv4 vs IPv6 비교:
//  ┌────────────────┬──────────────────┬──────────────────────────┐
//  │ 항목           │ IPv4             │ IPv6                      │
//  ├────────────────┼──────────────────┼──────────────────────────┤
//  │ 주소 길이      │ 32비트           │ 128비트                   │
//  │ 표기법         │ 점십진 표기       │ 콜론 16진수 표기          │
//  │ 예시           │ 192.168.1.1      │ 2001:0db8:85a3::8a2e:370│
//  │ 주소 수        │ ~43억            │ ~340간(澗) 개             │
//  │ NAT 필요       │ 필수 (부족해서)  │ 불필요 (충분해서)         │
//  │ 보안           │ IPSec 선택       │ IPSec 기본 내장           │
//  │ 헤더           │ 가변 (20-60B)    │ 고정 (40B)                │
//  └────────────────┴──────────────────┴──────────────────────────┘
//
//  IPv6 주소 예시:
//  2001:0db8:85a3:0000:0000:8a2e:0370:7334
//  → 축약: 2001:db8:85a3::8a2e:370:7334
//  (연속된 0000은 :: 로 생략 가능, 앞의 0도 생략 가능)

// ════════════════════════════════════════════════════════════════════
//  특수 IP 주소들
// ════════════════════════════════════════════════════════════════════
//
//  ┌─────────────────┬──────────────────────────────────────────┐
//  │ IP 주소         │ 의미                                      │
//  ├─────────────────┼──────────────────────────────────────────┤
//  │ 0.0.0.0         │ "모든 주소" (서버 바인딩 시)              │
//  │ 127.0.0.1       │ 루프백 (자기 자신 = localhost)            │
//  │ 255.255.255.255 │ 브로드캐스트 (같은 네트워크 전체)         │
//  │ 169.254.x.x     │ APIPA (DHCP 실패 시 자동 할당)           │
//  │ 224.0.0.0/4     │ 멀티캐스트 (그룹 통신)                   │
//  └─────────────────┴──────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  IP 주소 유틸리티 클래스
// ════════════════════════════════════════════════════════════════════

class IPv4Address {
private:
    uint32_t address_;   // 내부적으로 32비트 정수로 저장

public:
    // 기본 생성자
    IPv4Address() : address_(0) {}

    // 32비트 정수로 생성
    explicit IPv4Address(uint32_t addr) : address_(addr) {}

    // 4개 옥텟으로 생성
    IPv4Address(uint8_t a, uint8_t b, uint8_t c, uint8_t d) {
        address_ = (static_cast<uint32_t>(a) << 24) |
                   (static_cast<uint32_t>(b) << 16) |
                   (static_cast<uint32_t>(c) << 8) |
                   static_cast<uint32_t>(d);
    }

    // 문자열에서 파싱 ("192.168.1.1")
    // ★ 유효성 검증 포함!
    static bool parse(const std::string& str, IPv4Address& out) {
        int a, b, c, d;
        char dot1, dot2, dot3;

        std::istringstream iss(str);
        if (!(iss >> a >> dot1 >> b >> dot2 >> c >> dot3 >> d)) {
            return false;  // 파싱 실패
        }

        // 범위 검사 (각 옥텟은 0~255)
        if (a < 0 || a > 255 || b < 0 || b > 255 ||
            c < 0 || c > 255 || d < 0 || d > 255) {
            return false;  // 범위 초과
        }

        // 구분자 검사
        if (dot1 != '.' || dot2 != '.' || dot3 != '.') {
            return false;  // 점이 아닌 다른 문자
        }

        // 추가 문자 검사 (예: "192.168.1.1abc"는 거부)
        std::string remaining;
        iss >> remaining;
        if (!remaining.empty()) {
            return false;
        }

        out = IPv4Address(
            static_cast<uint8_t>(a), static_cast<uint8_t>(b),
            static_cast<uint8_t>(c), static_cast<uint8_t>(d)
        );
        return true;
    }

    // 각 옥텟 접근
    uint8_t octet(int index) const {
        // index: 0=첫번째, 1=두번째, 2=세번째, 3=네번째
        return (address_ >> (24 - index * 8)) & 0xFF;
    }

    // 32비트 정수 값 반환
    uint32_t value() const { return address_; }

    // 문자열 변환 ("192.168.1.1")
    std::string to_string() const {
        return std::to_string(octet(0)) + "." +
               std::to_string(octet(1)) + "." +
               std::to_string(octet(2)) + "." +
               std::to_string(octet(3));
    }

    // 이진수 문자열 변환 ("11000000.10101000.00000001.00000001")
    std::string to_binary_string() const {
        return std::bitset<8>(octet(0)).to_string() + "." +
               std::bitset<8>(octet(1)).to_string() + "." +
               std::bitset<8>(octet(2)).to_string() + "." +
               std::bitset<8>(octet(3)).to_string();
    }

    // 비트 연산자 오버로딩 (서브넷 계산에 필수!)
    IPv4Address operator&(const IPv4Address& other) const {
        return IPv4Address(address_ & other.address_);
    }
    IPv4Address operator|(const IPv4Address& other) const {
        return IPv4Address(address_ | other.address_);
    }
    IPv4Address operator~() const {
        return IPv4Address(~address_);
    }

    // 비교 연산자
    bool operator==(const IPv4Address& other) const {
        return address_ == other.address_;
    }
    bool operator!=(const IPv4Address& other) const {
        return address_ != other.address_;
    }

    // Private IP 확인
    // ★ RFC 1918에 정의된 사설 IP 범위
    bool is_private() const {
        // 10.0.0.0/8
        if (octet(0) == 10) return true;
        // 172.16.0.0/12 (172.16.x.x ~ 172.31.x.x)
        if (octet(0) == 172 && octet(1) >= 16 && octet(1) <= 31) return true;
        // 192.168.0.0/16
        if (octet(0) == 192 && octet(1) == 168) return true;
        return false;
    }

    // 루프백 주소 확인 (127.x.x.x)
    bool is_loopback() const {
        return octet(0) == 127;
    }

    // 멀티캐스트 주소 확인 (224.0.0.0 ~ 239.255.255.255)
    bool is_multicast() const {
        return octet(0) >= 224 && octet(0) <= 239;
    }

    // 브로드캐스트 주소 확인
    bool is_broadcast() const {
        return address_ == 0xFFFFFFFF;
    }

    // APIPA 주소 확인 (169.254.x.x) - DHCP 실패 시 자동 할당
    bool is_apipa() const {
        return octet(0) == 169 && octet(1) == 254;
    }

    // IP 주소 분류 (클래스 기반 - 역사적 분류법)
    char get_class() const {
        if (octet(0) <= 127) return 'A';       // 0xxxxxxx (0~127)
        if (octet(0) <= 191) return 'B';       // 10xxxxxx (128~191)
        if (octet(0) <= 223) return 'C';       // 110xxxxx (192~223)
        if (octet(0) <= 239) return 'D';       // 1110xxxx (224~239, 멀티캐스트)
        return 'E';                             // 1111xxxx (240~255, 예약)
    }
};

// ════════════════════════════════════════════════════════════════════
//  서브넷 계산기 클래스
// ════════════════════════════════════════════════════════════════════

class SubnetCalculator {
private:
    IPv4Address ip_;
    IPv4Address mask_;
    int cidr_;

public:
    // CIDR 표기법으로 생성 (/24, /16 등)
    SubnetCalculator(const IPv4Address& ip, int cidr)
        : ip_(ip), cidr_(cidr) {
        // CIDR → 서브넷 마스크 변환
        // /24 → 11111111.11111111.11111111.00000000
        uint32_t mask_val = 0;
        if (cidr > 0) {
            mask_val = 0xFFFFFFFF << (32 - cidr);
        }
        mask_ = IPv4Address(mask_val);
    }

    // 서브넷 마스크로 생성
    SubnetCalculator(const IPv4Address& ip, const IPv4Address& mask)
        : ip_(ip), mask_(mask) {
        // 서브넷 마스크 → CIDR 변환
        // 1의 개수를 세면 됨
        uint32_t m = mask.value();
        cidr_ = 0;
        while (m & 0x80000000) {
            cidr_++;
            m <<= 1;
        }
    }

    // ── 핵심 계산 함수들 ──

    // 네트워크 주소 = IP AND 서브넷마스크
    // "이 IP가 속한 동네의 대표 주소"
    IPv4Address network_address() const {
        return ip_ & mask_;
    }

    // 브로드캐스트 주소 = 네트워크주소 OR ~서브넷마스크
    // "이 동네의 모든 집에게 방송하는 주소"
    IPv4Address broadcast_address() const {
        return network_address() | ~mask_;
    }

    // 첫 번째 호스트 = 네트워크 주소 + 1
    IPv4Address first_host() const {
        return IPv4Address(network_address().value() + 1);
    }

    // 마지막 호스트 = 브로드캐스트 주소 - 1
    IPv4Address last_host() const {
        return IPv4Address(broadcast_address().value() - 1);
    }

    // 사용 가능한 호스트 수 = 2^(32-CIDR) - 2
    uint32_t host_count() const {
        if (cidr_ >= 31) return 0;  // /31, /32는 특수
        return (1u << (32 - cidr_)) - 2;
    }

    // 총 IP 수 (네트워크+브로드캐스트 포함)
    uint32_t total_addresses() const {
        return 1u << (32 - cidr_);
    }

    // 와일드카드 마스크 (ACL에서 사용, 서브넷 마스크의 반대)
    IPv4Address wildcard_mask() const {
        return ~mask_;
    }

    // 주어진 IP가 같은 서브넷에 있는지 확인
    bool is_same_subnet(const IPv4Address& other_ip) const {
        return (ip_ & mask_) == (other_ip & mask_);
    }

    // 전체 정보 출력
    void print_info() const {
        std::cout << "\n  ┌─────────────────────────────────────────────────┐" << std::endl;
        std::cout << "  │            서브넷 계산 결과                       │" << std::endl;
        std::cout << "  ├─────────────────────────────────────────────────┤" << std::endl;
        std::cout << "  │  IP 주소:        " << std::setw(20) << std::left
                  << ip_.to_string() << "         │" << std::endl;
        std::cout << "  │  서브넷 마스크:  " << std::setw(20)
                  << mask_.to_string() << " (/" << cidr_ << ")   │" << std::endl;
        std::cout << "  │  네트워크 주소:  " << std::setw(20)
                  << network_address().to_string() << "         │" << std::endl;
        std::cout << "  │  브로드캐스트:   " << std::setw(20)
                  << broadcast_address().to_string() << "         │" << std::endl;
        std::cout << "  │  첫 번째 호스트: " << std::setw(20)
                  << first_host().to_string() << "         │" << std::endl;
        std::cout << "  │  마지막 호스트:  " << std::setw(20)
                  << last_host().to_string() << "         │" << std::endl;
        std::cout << "  │  사용 가능 호스트: " << std::setw(10)
                  << host_count() << " 개              │" << std::endl;
        std::cout << "  │  와일드카드:     " << std::setw(20)
                  << wildcard_mask().to_string() << "         │" << std::endl;
        std::cout << "  └─────────────────────────────────────────────────┘" << std::endl;

        // 이진수 표현도 출력
        std::cout << "\n  이진수 표현:" << std::endl;
        std::cout << "  IP:   " << ip_.to_binary_string() << std::endl;
        std::cout << "  Mask: " << mask_.to_binary_string() << std::endl;
        std::cout << "  Net:  " << network_address().to_binary_string() << std::endl;
    }
};

// ════════════════════════════════════════════════════════════════════
//  NAT 테이블 시뮬레이션
// ════════════════════════════════════════════════════════════════════

struct NATEntry {
    // 내부 (사설) 측
    IPv4Address internal_ip;
    uint16_t internal_port;

    // 외부 (공인) 측
    IPv4Address external_ip;
    uint16_t external_port;

    // 목적지
    IPv4Address remote_ip;
    uint16_t remote_port;

    // 상태
    std::string protocol;    // "TCP" 또는 "UDP"
    int timeout;             // 만료 시간 (초)
};

class NATTable {
private:
    std::vector<NATEntry> entries_;
    IPv4Address public_ip_;       // 공유기의 공인 IP
    uint16_t next_port_ = 40000; // 다음 할당할 외부 포트

public:
    NATTable(const IPv4Address& public_ip)
        : public_ip_(public_ip) {}

    // 패킷이 나갈 때: 사설→공인 변환
    // ★ 이것이 공유기가 하는 핵심 동작!
    NATEntry translate_outbound(
        const IPv4Address& src_ip, uint16_t src_port,
        const IPv4Address& dst_ip, uint16_t dst_port,
        const std::string& protocol)
    {
        NATEntry entry;
        entry.internal_ip = src_ip;
        entry.internal_port = src_port;
        entry.external_ip = public_ip_;
        entry.external_port = next_port_++;  // 고유한 외부 포트 할당
        entry.remote_ip = dst_ip;
        entry.remote_port = dst_port;
        entry.protocol = protocol;
        entry.timeout = 300;  // 5분

        entries_.push_back(entry);
        return entry;
    }

    // NAT 테이블 출력
    void print_table() const {
        std::cout << "\n  ┌─────────────────────────────────────────────────────────────────┐" << std::endl;
        std::cout << "  │                    NAT 변환 테이블                                │" << std::endl;
        std::cout << "  ├─────────────────────────────────────────────────────────────────┤" << std::endl;
        std::cout << "  │  내부 IP:포트         →  외부 IP:포트         → 목적지           │" << std::endl;
        std::cout << "  ├─────────────────────────────────────────────────────────────────┤" << std::endl;

        for (const auto& e : entries_) {
            std::ostringstream internal, external, remote;
            internal << e.internal_ip.to_string() << ":" << e.internal_port;
            external << e.external_ip.to_string() << ":" << e.external_port;
            remote << e.remote_ip.to_string() << ":" << e.remote_port;

            std::cout << "  │  " << std::setw(20) << std::left << internal.str()
                      << " →  " << std::setw(20) << external.str()
                      << " → " << std::setw(15) << remote.str()
                      << " │" << std::endl;
        }
        std::cout << "  └─────────────────────────────────────────────────────────────────┘" << std::endl;
    }
};

// ════════════════════════════════════════════════════════════════════
//  IP 주소 검증기
// ════════════════════════════════════════════════════════════════════

// 다양한 IP 주소 문자열을 검증하고 분석하는 함수
void validate_ip_address(const std::string& ip_str) {
    std::cout << "\n  검증: \"" << ip_str << "\"" << std::endl;

    IPv4Address addr;
    if (!IPv4Address::parse(ip_str, addr)) {
        std::cout << "    ✗ 유효하지 않은 IP 주소!" << std::endl;
        return;
    }

    std::cout << "    ✓ 유효한 IP 주소" << std::endl;
    std::cout << "    클래스: " << addr.get_class() << std::endl;
    std::cout << "    이진수: " << addr.to_binary_string() << std::endl;

    // 특수 주소 확인
    if (addr.is_private())    std::cout << "    → 사설 IP (Private)" << std::endl;
    if (addr.is_loopback())   std::cout << "    → 루프백 (Loopback)" << std::endl;
    if (addr.is_multicast())  std::cout << "    → 멀티캐스트" << std::endl;
    if (addr.is_broadcast())  std::cout << "    → 브로드캐스트" << std::endl;
    if (addr.is_apipa())      std::cout << "    → APIPA (DHCP 실패)" << std::endl;
}

// ════════════════════════════════════════════════════════════════════
//  DHCP 시뮬레이션
// ════════════════════════════════════════════════════════════════════

struct DHCPLease {
    IPv4Address ip;
    std::string hostname;
    int lease_time;           // 임대 시간 (초)
    bool active;
};

class DHCPServer {
private:
    IPv4Address pool_start_;    // IP 풀 시작
    IPv4Address pool_end_;      // IP 풀 끝
    IPv4Address gateway_;       // 기본 게이트웨이
    IPv4Address dns_server_;    // DNS 서버
    IPv4Address subnet_mask_;   // 서브넷 마스크
    std::vector<DHCPLease> leases_;
    uint32_t next_ip_;          // 다음 할당할 IP

public:
    DHCPServer(const IPv4Address& start, const IPv4Address& end,
               const IPv4Address& gateway, const IPv4Address& dns,
               const IPv4Address& mask)
        : pool_start_(start), pool_end_(end),
          gateway_(gateway), dns_server_(dns),
          subnet_mask_(mask), next_ip_(start.value()) {}

    // DHCP DORA 프로세스 시뮬레이션
    DHCPLease allocate(const std::string& hostname) {
        std::cout << "\n  ── DHCP DORA 프로세스 ──" << std::endl;

        // 1. Discover
        std::cout << "  [D] Discover: " << hostname
                  << "이(가) IP를 요청합니다 (브로드캐스트)" << std::endl;

        // 2. Offer
        IPv4Address offered_ip(next_ip_);
        std::cout << "  [O] Offer: 서버가 " << offered_ip.to_string()
                  << "을(를) 제안합니다" << std::endl;

        // 3. Request
        std::cout << "  [R] Request: " << hostname << "이(가) "
                  << offered_ip.to_string() << "을(를) 요청합니다" << std::endl;

        // 4. ACK
        DHCPLease lease;
        lease.ip = offered_ip;
        lease.hostname = hostname;
        lease.lease_time = 86400;  // 24시간
        lease.active = true;

        leases_.push_back(lease);
        next_ip_++;

        std::cout << "  [A] ACK: 할당 완료!" << std::endl;
        std::cout << "      IP: " << lease.ip.to_string() << std::endl;
        std::cout << "      마스크: " << subnet_mask_.to_string() << std::endl;
        std::cout << "      게이트웨이: " << gateway_.to_string() << std::endl;
        std::cout << "      DNS: " << dns_server_.to_string() << std::endl;
        std::cout << "      임대 시간: " << lease.lease_time << "초 (24시간)" << std::endl;

        return lease;
    }

    // 임대 목록 출력
    void print_leases() const {
        std::cout << "\n  ┌──────────────────────────────────────────┐" << std::endl;
        std::cout << "  │          DHCP 임대 목록                   │" << std::endl;
        std::cout << "  ├──────────────────────────────────────────┤" << std::endl;
        for (const auto& lease : leases_) {
            std::cout << "  │  " << std::setw(15) << std::left
                      << lease.ip.to_string()
                      << " → " << std::setw(15) << lease.hostname
                      << (lease.active ? " [활성]" : " [만료]")
                      << " │" << std::endl;
        }
        std::cout << "  └──────────────────────────────────────────┘" << std::endl;
    }
};

// ════════════════════════════════════════════════════════════════════
//  메인 함수 - 모든 개념 시연
// ════════════════════════════════════════════════════════════════════

int main() {
    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;
    std::cout << "  IP 주소 완전 정복 - 네트워크 주소 체계" << std::endl;
    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  1. IP 주소 파싱 및 검증
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  1. IP 주소 파싱 및 검증" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    // 다양한 IP 주소 검증 테스트
    std::vector<std::string> test_ips = {
        "192.168.1.1",       // 유효 - 사설 C클래스
        "10.0.0.1",          // 유효 - 사설 A클래스
        "172.16.0.1",        // 유효 - 사설 B클래스
        "8.8.8.8",           // 유효 - 구글 DNS
        "127.0.0.1",         // 유효 - 루프백
        "224.0.0.1",         // 유효 - 멀티캐스트
        "255.255.255.255",   // 유효 - 브로드캐스트
        "169.254.1.1",       // 유효 - APIPA
        "256.1.1.1",         // ✗ 범위 초과
        "192.168.1",         // ✗ 옥텟 부족
        "abc.def.ghi.jkl",   // ✗ 문자열
    };

    for (const auto& ip : test_ips) {
        validate_ip_address(ip);
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  2. 서브넷 계산기
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  2. 서브넷 계산기" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    // 예제 1: 192.168.1.100/24 (가장 일반적인 가정용 네트워크)
    std::cout << "\n  ── 예제 1: 가정용 네트워크 ──" << std::endl;
    SubnetCalculator calc1(IPv4Address(192, 168, 1, 100), 24);
    calc1.print_info();

    // 예제 2: 10.0.0.50/8 (대형 사설 네트워크)
    std::cout << "\n  ── 예제 2: 대형 사설 네트워크 ──" << std::endl;
    SubnetCalculator calc2(IPv4Address(10, 0, 0, 50), 8);
    calc2.print_info();

    // 예제 3: 172.16.5.130/26 (서브넷팅 예제)
    std::cout << "\n  ── 예제 3: 서브넷팅 예제 (/26) ──" << std::endl;
    SubnetCalculator calc3(IPv4Address(172, 16, 5, 130), 26);
    calc3.print_info();

    // 예제 4: /28 서브넷 (소규모 네트워크)
    std::cout << "\n  ── 예제 4: 소규모 네트워크 (/28) ──" << std::endl;
    SubnetCalculator calc4(IPv4Address(192, 168, 10, 200), 28);
    calc4.print_info();

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  3. 같은 서브넷인지 확인
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  3. 같은 서브넷 확인" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    // ★ 같은 서브넷 = 라우터 없이 직접 통신 가능
    // ★ 다른 서브넷 = 라우터(게이트웨이) 필요!

    SubnetCalculator checker(IPv4Address(192, 168, 1, 10), 24);

    std::vector<std::pair<std::string, IPv4Address>> checks = {
        {"192.168.1.50",  IPv4Address(192, 168, 1, 50)},
        {"192.168.1.200", IPv4Address(192, 168, 1, 200)},
        {"192.168.2.10",  IPv4Address(192, 168, 2, 10)},
        {"10.0.0.1",      IPv4Address(10, 0, 0, 1)},
    };

    for (const auto& [name, ip] : checks) {
        bool same = checker.is_same_subnet(ip);
        std::cout << "  192.168.1.10/24 와 " << std::setw(15) << std::left << name
                  << " → " << (same ? "같은 서브넷 (직접 통신)" : "다른 서브넷 (라우터 필요)")
                  << std::endl;
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  4. NAT 테이블 시뮬레이션
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  4. NAT 테이블 시뮬레이션 (공유기 동작)" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    // 공유기 생성 (공인 IP: 211.100.1.1)
    NATTable nat(IPv4Address(211, 100, 1, 1));

    // 내부 장치들이 인터넷에 접속하는 시나리오
    std::cout << "\n  시나리오: 3대의 PC가 동시에 웹 서핑" << std::endl;

    nat.translate_outbound(
        IPv4Address(192, 168, 1, 10), 50000,   // PC1
        IPv4Address(142, 250, 196, 110), 443,  // Google
        "TCP"
    );

    nat.translate_outbound(
        IPv4Address(192, 168, 1, 20), 50000,   // PC2 (같은 내부 포트!)
        IPv4Address(31, 13, 71, 36), 443,      // Facebook
        "TCP"
    );

    nat.translate_outbound(
        IPv4Address(192, 168, 1, 30), 60000,   // PC3
        IPv4Address(104, 16, 249, 249), 443,   // Cloudflare
        "TCP"
    );

    nat.print_table();

    std::cout << "\n  ★ 핵심: 3대 모두 동일한 공인 IP(211.100.1.1)를 사용!" << std::endl;
    std::cout << "  ★ 외부 포트 번호로 어떤 내부 PC인지 구분!" << std::endl;

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  5. DHCP 시뮬레이션
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  5. DHCP 시뮬레이션 (자동 IP 할당)" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    // DHCP 서버 설정
    DHCPServer dhcp(
        IPv4Address(192, 168, 1, 100),    // 풀 시작
        IPv4Address(192, 168, 1, 200),    // 풀 끝
        IPv4Address(192, 168, 1, 1),      // 게이트웨이
        IPv4Address(8, 8, 8, 8),          // DNS
        IPv4Address(255, 255, 255, 0)     // 서브넷 마스크
    );

    // 장치들이 네트워크에 연결
    dhcp.allocate("노트북-김철수");
    dhcp.allocate("스마트폰-이영희");
    dhcp.allocate("태블릿-박민수");

    dhcp.print_leases();

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  6. 서브넷팅 연습 문제
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  6. 서브넷팅 연습 문제와 풀이" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    std::cout << R"(
  ┌───────────────────────────────────────────────────────┐
  │  문제: 192.168.10.0/24 네트워크를 4개 서브넷으로 나누기│
  │                                                        │
  │  풀이:                                                 │
  │  - 4개 서브넷 → 2비트 추가 필요 (2^2 = 4)             │
  │  - /24 + 2 = /26                                       │
  │  - 각 서브넷 호스트 수: 2^(32-26) - 2 = 62개          │
  └───────────────────────────────────────────────────────┘
)" << std::endl;

    // 4개 서브넷 자동 생성
    std::vector<IPv4Address> subnet_starts = {
        IPv4Address(192, 168, 10, 0),
        IPv4Address(192, 168, 10, 64),
        IPv4Address(192, 168, 10, 128),
        IPv4Address(192, 168, 10, 192),
    };

    for (size_t i = 0; i < subnet_starts.size(); i++) {
        std::cout << "  ── 서브넷 " << (i + 1) << " ──" << std::endl;
        SubnetCalculator sub(subnet_starts[i], 26);
        std::cout << "    네트워크: " << sub.network_address().to_string() << "/26" << std::endl;
        std::cout << "    호스트 범위: " << sub.first_host().to_string()
                  << " ~ " << sub.last_host().to_string() << std::endl;
        std::cout << "    브로드캐스트: " << sub.broadcast_address().to_string() << std::endl;
        std::cout << "    사용 가능: " << sub.host_count() << "개" << std::endl;
        std::cout << std::endl;
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  정리
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  정리: IP 주소 핵심 요약" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    std::cout << R"(
  ★ 기억해야 할 핵심:

  1. IP 주소 = 네트워크 부분 + 호스트 부분
  2. 서브넷 마스크로 두 부분을 구분
  3. 네트워크 주소 = IP AND 마스크
  4. 브로드캐스트  = 네트워크 OR ~마스크
  5. 호스트 수     = 2^(호스트비트) - 2

  ★ 실무 팁:
  - /24 = 254 호스트 (가정/소규모)
  - /16 = 65,534 호스트 (기업)
  - /8  = 16M 호스트 (대규모 사설망)
  - NAT 덕분에 사설 IP는 무한히 재사용 가능
  - DHCP 덕분에 IP를 수동 설정할 필요 없음
  - IPv4 고갈 → IPv6로 전환 중 (아직 느림)
)" << std::endl;

    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;
    std::cout << "  IP 주소 학습 완료!" << std::endl;
    std::cout << "  다음: 03_tcp_udp (TCP/UDP 프로토콜)" << std::endl;
    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;

    return 0;
}
