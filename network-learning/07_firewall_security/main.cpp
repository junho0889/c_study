/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  네트워크 학습 07단계: 방화벽과 네트워크 보안
  ─ Firewall, IDS/IPS, WAF, DDoS, SSL/TLS, 포트 스캐너 구현 ─

  이 파일 하나로 네트워크 보안의 핵심 개념을 전부 배웁니다.
  방화벽 종류, 보안 아키텍처, 그리고 C++로 포트 스캐너를 직접 만듭니다.

  ■ 컴파일 방법 (터미널에 입력)
    Windows (MinGW) : g++ -std=c++17 -Wall -o 07_firewall.exe main.cpp -lws2_32
    Windows (MSVC)  : cl /EHsc /std:c++17 /W4 main.cpp ws2_32.lib
    Linux / Mac     : g++ -std=c++17 -Wall -o 07_firewall main.cpp

  ■ 실행 방법
    Windows : .\07_firewall.exe
    Linux   : ./07_firewall

  ★ 주의: 포트 스캐닝은 자신의 시스템에서만 테스트하세요!
          타인의 네트워크를 스캔하는 것은 불법입니다.

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <algorithm>
#include <sstream>
#include <chrono>
#include <functional>
#include <iomanip>
#include <cstring>

// ─── 플랫폼별 소켓 헤더 ───
#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib, "ws2_32.lib")
#else
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <unistd.h>
    #include <fcntl.h>
    #include <errno.h>
    #define SOCKET int
    #define INVALID_SOCKET -1
    #define SOCKET_ERROR -1
    #define closesocket close
#endif

using namespace std;


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 1: 방화벽(Firewall) 종류와 개념
// ─────────────────────────────────────────────────────────────────────────
//
//  방화벽이란?
//  ──────────
//  네트워크 트래픽을 검사하고, 허용/차단 규칙에 따라 필터링하는 보안 장치
//
//  비유: 건물의 경비원
//        → 출입증(규칙)을 확인하고 허가된 사람만 통과시킴
//
//  ┌─────────────────────────────────────────────────────────────────┐
//  │                    방화벽 종류 비교표                             │
//  ├────────────────┬───────────────┬────────────────┬───────────────┤
//  │     종류       │   동작 계층    │     특징       │    성능       │
//  ├────────────────┼───────────────┼────────────────┼───────────────┤
//  │ 패킷 필터링    │ L3/L4         │ IP/포트 기반   │ 매우 빠름     │
//  │ 상태 기반      │ L3/L4         │ 연결 상태 추적 │ 빠름          │
//  │ 애플리케이션   │ L7            │ 내용 검사      │ 느림          │
//  │ 차세대(NGFW)   │ L3~L7         │ 종합 검사      │ 보통          │
//  └────────────────┴───────────────┴────────────────┴───────────────┘
//
//  1) 패킷 필터링 방화벽 (Packet Filtering)
//     - 가장 기본적인 형태
//     - IP 주소, 포트 번호, 프로토콜로 판단
//     - 각 패킷을 독립적으로 검사 (이전 패킷과 관계 없음)
//     - 장점: 빠르다, 단점: 우회 가능
//
//  2) 상태 기반 방화벽 (Stateful Inspection)
//     - 연결 상태를 추적 (TCP 3-way handshake 등)
//     - "이미 허가된 연결의 패킷"은 자동 허용
//     - 대부분의 현대 방화벽이 이 방식
//
//  3) 애플리케이션 방화벽 (Application Layer)
//     - HTTP, FTP 등 L7 프로토콜 내용까지 검사
//     - SQL Injection, XSS 등 공격 탐지 가능
//     - WAF(Web Application Firewall)가 대표적
//
//  4) 차세대 방화벽 (NGFW - Next Generation Firewall)
//     - 위 모든 기능 + IPS + 사용자 식별 + 애플리케이션 식별
//     - FortiGate, Palo Alto, Check Point 등
//
// ─────────────────────────────────────────────────────────────────────────


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 2: iptables/nftables 규칙 개념
// ─────────────────────────────────────────────────────────────────────────
//
//  Linux 방화벽의 핵심: iptables (레거시) / nftables (신규)
//
//  ┌─────────────────────────────────────────────────────────────────┐
//  │                    iptables 체인 구조                            │
//  │                                                                 │
//  │   인터넷 ──→ [PREROUTING] ──→ 라우팅 판단                       │
//  │                                  │                              │
//  │                    ┌─────────────┼─────────────┐                │
//  │                    ▼             ▼             ▼                │
//  │              [INPUT]       [FORWARD]      [OUTPUT]              │
//  │              (로컬용)      (통과용)       (나가는용)            │
//  │                    │             │             │                │
//  │                    └─────────────┼─────────────┘                │
//  │                                  ▼                              │
//  │                          [POSTROUTING]                          │
//  │                                  │                              │
//  │                              인터넷                              │
//  └─────────────────────────────────────────────────────────────────┘
//
//  주요 체인:
//  - INPUT    : 이 서버로 들어오는 패킷 → 웹서버 접속 등
//  - OUTPUT   : 이 서버에서 나가는 패킷 → 외부 API 호출 등
//  - FORWARD  : 이 서버를 통과하는 패킷 → 라우터/게이트웨이 역할 시
//
//  iptables 규칙 예시:
//  ┌─────────────────────────────────────────────────────────────────┐
//  │ # SSH 허용 (포트 22)                                            │
//  │ iptables -A INPUT -p tcp --dport 22 -j ACCEPT                  │
//  │                                                                 │
//  │ # HTTP/HTTPS 허용                                               │
//  │ iptables -A INPUT -p tcp --dport 80 -j ACCEPT                  │
//  │ iptables -A INPUT -p tcp --dport 443 -j ACCEPT                 │
//  │                                                                 │
//  │ # 특정 IP 차단                                                  │
//  │ iptables -A INPUT -s 192.168.1.100 -j DROP                     │
//  │                                                                 │
//  │ # 기본 정책: 모든 입력 차단                                      │
//  │ iptables -P INPUT DROP                                          │
//  │                                                                 │
//  │ # 이미 허가된 연결 허용 (상태 기반)                              │
//  │ iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT│
//  └─────────────────────────────────────────────────────────────────┘
//
// ─────────────────────────────────────────────────────────────────────────


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 3: 방화벽 규칙 시뮬레이터 (C++ 구현)
// ─────────────────────────────────────────────────────────────────────────

// 방화벽 규칙의 액션
enum class FirewallAction {
    ACCEPT,     // 허용
    DROP,       // 조용히 차단 (응답 없음)
    REJECT,     // 차단 + 거부 메시지 전송
    LOG         // 로그 기록 후 통과
};

// 프로토콜 타입
enum class Protocol {
    TCP,
    UDP,
    ICMP,
    ANY
};

// 방화벽 규칙 하나를 표현하는 구조체
struct FirewallRule {
    int ruleNumber;             // 규칙 번호 (우선순위)
    string chain;               // INPUT, OUTPUT, FORWARD
    Protocol protocol;          // TCP, UDP, ICMP, ANY
    string sourceIP;            // 출발지 IP ("0.0.0.0" = any)
    string destIP;              // 목적지 IP ("0.0.0.0" = any)
    int sourcePort;             // 출발지 포트 (0 = any)
    int destPort;               // 목적지 포트 (0 = any)
    FirewallAction action;      // ACCEPT, DROP, REJECT, LOG
    string description;         // 규칙 설명
};

// 패킷 구조체 (검사 대상)
struct Packet {
    string sourceIP;
    string destIP;
    int sourcePort;
    int destPort;
    Protocol protocol;
    string chain;               // 어느 체인을 통과하는지
};

// ★ 방화벽 시뮬레이터 클래스
class FirewallSimulator {
private:
    vector<FirewallRule> rules_;                  // 규칙 목록
    FirewallAction defaultPolicy_;                // 기본 정책
    vector<string> logs_;                         // 로그 저장

    // 프로토콜을 문자열로 변환
    string protocolToString(Protocol p) const {
        switch(p) {
            case Protocol::TCP:  return "TCP";
            case Protocol::UDP:  return "UDP";
            case Protocol::ICMP: return "ICMP";
            case Protocol::ANY:  return "ANY";
        }
        return "UNKNOWN";
    }

    // 액션을 문자열로 변환
    string actionToString(FirewallAction a) const {
        switch(a) {
            case FirewallAction::ACCEPT: return "ACCEPT";
            case FirewallAction::DROP:   return "DROP";
            case FirewallAction::REJECT: return "REJECT";
            case FirewallAction::LOG:    return "LOG";
        }
        return "UNKNOWN";
    }

    // IP 매칭 ("0.0.0.0"은 any로 처리)
    bool matchIP(const string& ruleIP, const string& packetIP) const {
        if (ruleIP == "0.0.0.0" || ruleIP == "any") return true;

        // 간단한 서브넷 매칭: 192.168.1.0/24 형태
        size_t slashPos = ruleIP.find('/');
        if (slashPos != string::npos) {
            string network = ruleIP.substr(0, slashPos);
            // 단순화: 앞 부분만 비교 (실제로는 비트 연산 필요)
            string prefix = network.substr(0, network.rfind('.'));
            string packetPrefix = packetIP.substr(0, packetIP.rfind('.'));
            return prefix == packetPrefix;
        }

        return ruleIP == packetIP;
    }

    // 포트 매칭 (0은 any)
    bool matchPort(int rulePort, int packetPort) const {
        return rulePort == 0 || rulePort == packetPort;
    }

    // 규칙이 패킷과 일치하는지 검사
    bool matchRule(const FirewallRule& rule, const Packet& pkt) const {
        if (rule.chain != pkt.chain && rule.chain != "ALL") return false;
        if (rule.protocol != Protocol::ANY && rule.protocol != pkt.protocol) return false;
        if (!matchIP(rule.sourceIP, pkt.sourceIP)) return false;
        if (!matchIP(rule.destIP, pkt.destIP)) return false;
        if (!matchPort(rule.sourcePort, pkt.sourcePort)) return false;
        if (!matchPort(rule.destPort, pkt.destPort)) return false;
        return true;
    }

public:
    FirewallSimulator() : defaultPolicy_(FirewallAction::DROP) {}

    // 기본 정책 설정
    void setDefaultPolicy(FirewallAction action) {
        defaultPolicy_ = action;
        logs_.push_back("[정책] 기본 정책 변경: " + actionToString(action));
    }

    // 규칙 추가
    void addRule(const FirewallRule& rule) {
        rules_.push_back(rule);
        sort(rules_.begin(), rules_.end(),
             [](const FirewallRule& a, const FirewallRule& b) {
                 return a.ruleNumber < b.ruleNumber;
             });
    }

    // 패킷 검사 ─ 규칙을 순서대로 검사하여 첫 번째 일치하는 규칙 적용
    FirewallAction inspectPacket(const Packet& pkt) {
        stringstream logEntry;
        logEntry << "[검사] " << pkt.sourceIP << ":" << pkt.sourcePort
                 << " -> " << pkt.destIP << ":" << pkt.destPort
                 << " (" << protocolToString(pkt.protocol) << "/" << pkt.chain << ")";

        for (const auto& rule : rules_) {
            if (matchRule(rule, pkt)) {
                logEntry << " => 규칙 #" << rule.ruleNumber
                         << " " << actionToString(rule.action)
                         << " (" << rule.description << ")";
                logs_.push_back(logEntry.str());
                return rule.action;
            }
        }

        logEntry << " => 기본 정책 " << actionToString(defaultPolicy_);
        logs_.push_back(logEntry.str());
        return defaultPolicy_;
    }

    // 규칙 목록 출력
    void printRules() const {
        cout << "\n┌────┬────────┬──────┬─────────────────┬─────────────────┬───────┬───────┬────────┬──────────────────────┐\n";
        cout << "│ #  │ Chain  │Proto │ Source IP        │ Dest IP         │ SPort │ DPort │ Action │ Description          │\n";
        cout << "├────┼────────┼──────┼─────────────────┼─────────────────┼───────┼───────┼────────┼──────────────────────┤\n";

        for (const auto& r : rules_) {
            cout << "│ " << setw(2) << r.ruleNumber
                 << " │ " << setw(6) << left << r.chain
                 << " │ " << setw(4) << protocolToString(r.protocol)
                 << " │ " << setw(15) << r.sourceIP
                 << " │ " << setw(15) << r.destIP
                 << " │ " << setw(5) << (r.sourcePort == 0 ? "*" : to_string(r.sourcePort))
                 << " │ " << setw(5) << (r.destPort == 0 ? "*" : to_string(r.destPort))
                 << " │ " << setw(6) << actionToString(r.action)
                 << " │ " << setw(20) << r.description
                 << " │" << right << "\n";
        }
        cout << "└────┴────────┴──────┴─────────────────┴─────────────────┴───────┴───────┴────────┴──────────────────────┘\n";
    }

    // 로그 출력
    void printLogs() const {
        cout << "\n═══ 방화벽 로그 ═══\n";
        for (const auto& log : logs_) {
            cout << "  " << log << "\n";
        }
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 4: ACL (Access Control List)
// ─────────────────────────────────────────────────────────────────────────
//
//  ACL이란?
//  ────────
//  네트워크 트래픽을 허용/차단하는 규칙의 목록
//  라우터, 스위치, 방화벽에서 사용
//
//  ┌─────────────────────────────────────────────────────────────────┐
//  │  ACL 종류                                                       │
//  ├─────────────────┬───────────────────────────────────────────────┤
//  │ Standard ACL    │ 출발지 IP만으로 판단 (번호 1~99)              │
//  │ Extended ACL    │ 출발지/목적지 IP + 포트 + 프로토콜 (100~199)  │
//  │ Named ACL       │ 이름으로 관리 (가독성 좋음)                   │
//  └─────────────────┴───────────────────────────────────────────────┘
//
// ─────────────────────────────────────────────────────────────────────────

// ACL 엔트리 구조체
struct ACLEntry {
    int sequence;
    bool permit;
    string sourceNetwork;
    string destNetwork;
    int port;
    string description;

    string toString() const {
        stringstream ss;
        ss << setw(4) << sequence << " "
           << (permit ? "PERMIT" : "DENY  ") << " "
           << setw(18) << sourceNetwork << " -> "
           << setw(18) << destNetwork
           << " Port:" << setw(5) << (port == 0 ? string("any") : to_string(port))
           << "  // " << description;
        return ss.str();
    }
};

// ACL 관리자
class ACLManager {
private:
    string name_;
    vector<ACLEntry> entries_;

public:
    ACLManager(const string& name) : name_(name) {}

    void addEntry(int seq, bool permit, const string& src, const string& dst,
                  int port, const string& desc) {
        entries_.push_back({seq, permit, src, dst, port, desc});
        sort(entries_.begin(), entries_.end(),
             [](const ACLEntry& a, const ACLEntry& b) { return a.sequence < b.sequence; });
    }

    void display() const {
        cout << "\n┌──────────────────────────────────────────────────────────────┐\n";
        cout << "│  ACL: " << setw(53) << left << name_ << "│\n" << right;
        cout << "├──────────────────────────────────────────────────────────────┤\n";
        for (const auto& entry : entries_) {
            cout << "│  " << setw(58) << left << entry.toString() << "│\n" << right;
        }
        cout << "└──────────────────────────────────────────────────────────────┘\n";
    }

    bool isAllowed(const string& srcIP, const string& dstIP, int port) const {
        for (const auto& entry : entries_) {
            bool srcMatch = (entry.sourceNetwork == "any" || entry.sourceNetwork == srcIP);
            bool dstMatch = (entry.destNetwork == "any" || entry.destNetwork == dstIP);
            bool portMatch = (entry.port == 0 || entry.port == port);
            if (srcMatch && dstMatch && portMatch) {
                return entry.permit;
            }
        }
        return false; // 암묵적 거부
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 5: DMZ (비무장지대) 아키텍처
// ─────────────────────────────────────────────────────────────────────────
//
//  ┌─────────────────────────────────────────────────────────────────┐
//  │                     DMZ 아키텍처                                 │
//  │                                                                 │
//  │   인터넷 (외부)                                                  │
//  │       │                                                         │
//  │   ┌───▼───────────────┐                                         │
//  │   │  외부 방화벽       │  ← HTTP/HTTPS/SMTP만 허용              │
//  │   └───┬───────────────┘                                         │
//  │       │                                                         │
//  │   ┌───▼───────────────┐                                         │
//  │   │      DMZ          │                                         │
//  │   │  ┌─────┐ ┌─────┐ │                                         │
//  │   │  │ Web │ │ Mail│ │  ← 공개 서비스                           │
//  │   │  └─────┘ └─────┘ │                                         │
//  │   │  ┌─────┐         │                                         │
//  │   │  │ DNS │         │                                         │
//  │   │  └─────┘         │                                         │
//  │   └───┬───────────────┘                                         │
//  │       │                                                         │
//  │   ┌───▼───────────────┐                                         │
//  │   │  내부 방화벽       │  ← 최소 필요 포트만 허용               │
//  │   └───┬───────────────┘                                         │
//  │       │                                                         │
//  │   ┌───▼───────────────┐                                         │
//  │   │    내부 네트워크   │                                         │
//  │   │  ┌─────┐ ┌─────┐ │                                         │
//  │   │  │ DB  │ │ App │ │  ← 외부 직접 접근 불가                   │
//  │   │  └─────┘ └─────┘ │                                         │
//  │   └───────────────────┘                                         │
//  └─────────────────────────────────────────────────────────────────┘
//
//  ★ 중요 원칙:
//     1. 외부 → DMZ: 특정 포트만 허용 (80, 443, 25 등)
//     2. DMZ → 내부: 최소 필요 연결만 허용 (DB 포트 등)
//     3. 외부 → 내부: 절대 직접 연결 불가!
//     4. 내부 → 외부: 제한적 허용 (NAT 통해)
//
// ─────────────────────────────────────────────────────────────────────────


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 6: IDS/IPS (침입 탐지/방지 시스템)
// ─────────────────────────────────────────────────────────────────────────
//
//  ┌─────────────────────────────────────────────────────────────────┐
//  │              IDS vs IPS 비교                                    │
//  ├─────────────────┬──────────────────┬────────────────────────────┤
//  │                 │     IDS          │         IPS                │
//  │                 │ (탐지 시스템)     │    (방지 시스템)           │
//  ├─────────────────┼──────────────────┼────────────────────────────┤
//  │ 역할            │ 탐지 + 경고      │ 탐지 + 차단               │
//  │ 동작 방식       │ 수동적 모니터링  │ 능동적 차단               │
//  │ 네트워크 위치   │ 미러 포트(복사본)│ 인라인(트래픽 경로 상)    │
//  │ 장애 시         │ 트래픽 영향 없음 │ 트래픽 중단 가능          │
//  │ 오탐 영향       │ 불필요한 경고    │ 정상 트래픽 차단          │
//  │ 대표 제품       │ Snort, Suricata  │ Snort(inline), Suricata   │
//  └─────────────────┴──────────────────┴────────────────────────────┘
//
// ─────────────────────────────────────────────────────────────────────────

// 간단한 IDS 시뮬레이터
class SimpleIDS {
public:
    struct Signature {
        string name;
        string pattern;
        string severity;
    };

private:
    vector<Signature> signatures_;
    vector<string> alerts_;

public:
    SimpleIDS() {
        signatures_.push_back({"SQL Injection", "' OR 1=1", "CRITICAL"});
        signatures_.push_back({"SQL Injection", "UNION SELECT", "CRITICAL"});
        signatures_.push_back({"XSS Attack", "<script>", "HIGH"});
        signatures_.push_back({"Directory Traversal", "../../../", "HIGH"});
        signatures_.push_back({"Command Injection", "; rm -rf", "CRITICAL"});
        signatures_.push_back({"PHP Shell", "eval(base64_decode", "CRITICAL"});
        signatures_.push_back({"Port Scan", "SYN_FLOOD", "MEDIUM"});
    }

    bool inspect(const string& payload, const string& sourceIP) {
        bool detected = false;
        for (const auto& sig : signatures_) {
            if (payload.find(sig.pattern) != string::npos) {
                stringstream alert;
                alert << "[ALERT] " << sig.severity
                      << " - " << sig.name
                      << " detected from " << sourceIP
                      << " | Pattern: \"" << sig.pattern << "\"";
                alerts_.push_back(alert.str());
                detected = true;
            }
        }
        return detected;
    }

    void printAlerts() const {
        cout << "\n═══ IDS 경고 목록 ═══\n";
        if (alerts_.empty()) {
            cout << "  (탐지된 위협 없음)\n";
            return;
        }
        for (const auto& alert : alerts_) {
            cout << "  " << alert << "\n";
        }
        cout << "  총 " << alerts_.size() << "건의 위협 탐지\n";
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 7: WAF / DDoS 방어 개념
// ─────────────────────────────────────────────────────────────────────────
//
//  WAF (Web Application Firewall):
//  ┌─────────────────────────────────────────────────────────────────┐
//  │   클라이언트 ──→ [WAF] ──→ 웹서버 ──→ DB                       │
//  │                  ↑                                              │
//  │            HTTP 요청 검사: SQL Injection, XSS, CSRF 등         │
//  │            Rate Limiting, 요청 크기 제한                       │
//  │   제품: ModSecurity, AWS WAF, Cloudflare WAF                   │
//  └─────────────────────────────────────────────────────────────────┘
//
//  DDoS 방어 전략:
//  ┌─────────────────────────────────────────────────────────────────┐
//  │ 1. CDN/클라우드 방어: Cloudflare, AWS Shield, Akamai           │
//  │ 2. Rate Limiting: 초당 요청 수 제한                            │
//  │ 3. SYN Cookie: SYN Flood 방어 (연결 상태 저장 안 함)           │
//  │ 4. 블랙홀 라우팅: 공격 트래픽을 /dev/null로                    │
//  │ 5. Anycast: 여러 서버로 트래픽 분산                            │
//  │ 6. ISP 협력: 상위 네트워크에서 차단                            │
//  │ 7. 트래픽 스크러빙: 공격 트래픽만 걸러냄                       │
//  └─────────────────────────────────────────────────────────────────┘
//
// ─────────────────────────────────────────────────────────────────────────

// Rate Limiter 구현 (DDoS 방어의 기본)
class RateLimiter {
private:
    struct ClientInfo {
        int requestCount;
        chrono::steady_clock::time_point windowStart;
    };

    map<string, ClientInfo> clients_;
    int maxRequests_;
    int windowSeconds_;

public:
    RateLimiter(int maxReqs = 100, int windowSec = 60)
        : maxRequests_(maxReqs), windowSeconds_(windowSec) {}

    bool allowRequest(const string& clientIP) {
        auto now = chrono::steady_clock::now();
        auto it = clients_.find(clientIP);
        if (it == clients_.end()) {
            clients_[clientIP] = {1, now};
            return true;
        }
        auto& info = it->second;
        auto elapsed = chrono::duration_cast<chrono::seconds>(now - info.windowStart).count();
        if (elapsed >= windowSeconds_) {
            info.requestCount = 1;
            info.windowStart = now;
            return true;
        }
        info.requestCount++;
        return info.requestCount <= maxRequests_;
    }

    void printStatus() const {
        cout << "\n═══ Rate Limiter 상태 ═══\n";
        cout << "  제한: " << maxRequests_ << "회/" << windowSeconds_ << "초\n";
        for (const auto& [ip, info] : clients_) {
            cout << "  " << setw(15) << ip << " : "
                 << info.requestCount << "회 요청"
                 << (info.requestCount > maxRequests_ ? " [차단됨!]" : " [정상]")
                 << "\n";
        }
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 8: 포트 스캐너 구현 (C++)
// ─────────────────────────────────────────────────────────────────────────
//
//  ★ 경고: 자신의 시스템에서만 테스트하세요!
//
//  ┌─────────────────────────────────────────────────────────────────┐
//  │  포트 스캔 종류                                                  │
//  ├───────────────┬─────────────────────────────────────────────────┤
//  │ TCP Connect   │ 완전한 3-way handshake → 가장 기본적            │
//  │ SYN Scan      │ SYN만 보내고 SYN-ACK 오면 열림 (Half-open)     │
//  │ UDP Scan      │ UDP 패킷 전송 → ICMP 에러 오면 닫힘            │
//  │ FIN Scan      │ FIN 패킷 전송 → RST 오면 닫힘                  │
//  └───────────────┴─────────────────────────────────────────────────┘
//
// ─────────────────────────────────────────────────────────────────────────

// Winsock 초기화/정리 헬퍼
class WinsockHelper {
public:
    bool initialized = false;
    WinsockHelper() {
#ifdef _WIN32
        WSADATA wsaData;
        if (WSAStartup(MAKEWORD(2, 2), &wsaData) == 0) initialized = true;
#else
        initialized = true;
#endif
    }
    ~WinsockHelper() {
#ifdef _WIN32
        if (initialized) WSACleanup();
#endif
    }
};

// TCP Connect 포트 스캐너
class PortScanner {
private:
    string targetIP_;
    int timeoutMs_;

    static string getServiceName(int port) {
        static const map<int, string> services = {
            {21, "FTP"}, {22, "SSH"}, {23, "Telnet"}, {25, "SMTP"},
            {53, "DNS"}, {80, "HTTP"}, {110, "POP3"}, {143, "IMAP"},
            {443, "HTTPS"}, {993, "IMAPS"}, {995, "POP3S"},
            {3306, "MySQL"}, {5432, "PostgreSQL"}, {6379, "Redis"},
            {8080, "HTTP-Alt"}, {27017, "MongoDB"}, {3389, "RDP"},
            {1433, "MSSQL"}, {5900, "VNC"}, {8443, "HTTPS-Alt"}
        };
        auto it = services.find(port);
        return it != services.end() ? it->second : "unknown";
    }

public:
    PortScanner(const string& ip, int timeoutMs = 1000)
        : targetIP_(ip), timeoutMs_(timeoutMs) {}

    bool scanPort(int port) {
        SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (sock == INVALID_SOCKET) return false;

#ifdef _WIN32
        unsigned long mode = 1;
        ioctlsocket(sock, FIONBIO, &mode);
#else
        int flags = fcntl(sock, F_GETFL, 0);
        fcntl(sock, F_SETFL, flags | O_NONBLOCK);
#endif

        struct sockaddr_in addr;
        memset(&addr, 0, sizeof(addr));
        addr.sin_family = AF_INET;
        addr.sin_port = htons(static_cast<unsigned short>(port));
        inet_pton(AF_INET, targetIP_.c_str(), &addr.sin_addr);

        connect(sock, (struct sockaddr*)&addr, sizeof(addr));

        fd_set writeSet;
        FD_ZERO(&writeSet);
        FD_SET(sock, &writeSet);

        struct timeval tv;
        tv.tv_sec = timeoutMs_ / 1000;
        tv.tv_usec = (timeoutMs_ % 1000) * 1000;

        int result = select(static_cast<int>(sock) + 1, nullptr, &writeSet, nullptr, &tv);

        bool isOpen = false;
        if (result > 0) {
            int error = 0;
#ifdef _WIN32
            int len = sizeof(error);
            getsockopt(sock, SOL_SOCKET, SO_ERROR, (char*)&error, &len);
#else
            socklen_t len = sizeof(error);
            getsockopt(sock, SOL_SOCKET, SO_ERROR, &error, &len);
#endif
            isOpen = (error == 0);
        }

        closesocket(sock);
        return isOpen;
    }

    void printResults(const vector<int>& openPorts) const {
        cout << "\n┌─────────────────────────────────────────┐\n";
        cout << "│  포트 스캔 결과: " << setw(22) << left << targetIP_ << "│\n" << right;
        cout << "├────────┬─────────────┬────────────────────┤\n";
        cout << "│  포트  │   상태      │   서비스           │\n";
        cout << "├────────┼─────────────┼────────────────────┤\n";

        if (openPorts.empty()) {
            cout << "│  (열린 포트 없음)                       │\n";
        } else {
            for (int port : openPorts) {
                cout << "│  " << setw(5) << port
                     << " │ OPEN        │ " << setw(18) << left
                     << getServiceName(port) << right << " │\n";
            }
        }
        cout << "└────────┴─────────────┴────────────────────┘\n";
        cout << "  총 " << openPorts.size() << "개 포트 열림\n";
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 9: SSL/TLS 심화
// ─────────────────────────────────────────────────────────────────────────
//
//  SSL/TLS 핸드셰이크 과정 (상세):
//
//  ┌──────────┐                              ┌──────────┐
//  │ 클라이언트│                              │  서버    │
//  └────┬─────┘                              └────┬─────┘
//       │  1. ClientHello                         │
//       │  (TLS 버전, 암호 스위트, 랜덤 값)       │
//       │────────────────────────────────────────→│
//       │  2. ServerHello + Certificate           │
//       │  (선택된 스위트, 서버 인증서)           │
//       │←────────────────────────────────────────│
//       │  3. ClientKeyExchange                   │
//       │  (Pre-Master Secret)                    │
//       │────────────────────────────────────────→│
//       │  4. ChangeCipherSpec + Finished         │
//       │←───────────────────────────────────────→│
//       │  ═══ 암호화된 데이터 통신 시작 ═══      │
//
//  인증서 체인:
//  ┌─────────────────────────────────────────────────────────────────┐
//  │  Root CA (브라우저 내장) → 중간 CA → 서버 인증서               │
//  │  검증: 서버 인증서 → 중간 CA → Root CA (신뢰 앵커)             │
//  └─────────────────────────────────────────────────────────────────┘
//
//  TLS 버전별 비교:
//  ┌───────────┬──────────┬──────────────────────────────────────────┐
//  │ TLS 1.0/1.1│ 폐기됨  │ 보안 취약점 (BEAST, POODLE 등)          │
//  │ TLS 1.2   │ 현재 사용│ 안전, 가장 널리 사용                     │
//  │ TLS 1.3   │ 최신     │ 핸드셰이크 1-RTT, 더 빠르고 안전       │
//  └───────────┴──────────┴──────────────────────────────────────────┘
//
// ─────────────────────────────────────────────────────────────────────────


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 10: 네트워크 보안 체크리스트
// ─────────────────────────────────────────────────────────────────────────
//
//  ┌─────────────────────────────────────────────────────────────────┐
//  │             네트워크 보안 체크리스트                              │
//  ├─────────────────────────────────────────────────────────────────┤
//  │ □ 방화벽: 기본 차단 + 필요한 것만 허용 + 로그 활성화          │
//  │ □ 접근: SSH 키 인증, 관리 포트 IP 제한, 최소 권한             │
//  │ □ 암호화: TLS 1.2+, 강력한 암호 스위트, HSTS                  │
//  │ □ 모니터링: IDS/IPS, SIEM, 취약점 스캔                        │
//  │ □ 설계: VLAN 세그먼테이션, DMZ, 정기 백업                     │
//  └─────────────────────────────────────────────────────────────────┘
//
// ─────────────────────────────────────────────────────────────────────────


// ─────────────────────────────────────────────────────────────────────────
// ■ 메인 함수 ─ 모든 보안 시뮬레이션 실행
// ─────────────────────────────────────────────────────────────────────────
int main() {
    cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■\n";
    cout << "■  네트워크 보안 학습 07: 방화벽과 네트워크 보안         ■\n";
    cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■\n";


    // ═══════════════════════════════════════════════════════════════
    // 데모 1: 방화벽 시뮬레이터
    // ═══════════════════════════════════════════════════════════════
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  데모 1: 방화벽 규칙 시뮬레이터\n";
    cout << "══════════════════════════════════════════════════\n";

    FirewallSimulator fw;
    fw.setDefaultPolicy(FirewallAction::DROP);

    fw.addRule({10, "INPUT", Protocol::TCP, "0.0.0.0", "0.0.0.0", 0, 22, FirewallAction::ACCEPT, "SSH 허용"});
    fw.addRule({20, "INPUT", Protocol::TCP, "0.0.0.0", "0.0.0.0", 0, 80, FirewallAction::ACCEPT, "HTTP 허용"});
    fw.addRule({30, "INPUT", Protocol::TCP, "0.0.0.0", "0.0.0.0", 0, 443, FirewallAction::ACCEPT, "HTTPS 허용"});
    fw.addRule({40, "INPUT", Protocol::TCP, "192.168.1.0/24", "0.0.0.0", 0, 3306, FirewallAction::ACCEPT, "내부망 MySQL 허용"});
    fw.addRule({50, "INPUT", Protocol::TCP, "10.0.0.100", "0.0.0.0", 0, 0, FirewallAction::DROP, "악성IP 차단"});
    fw.addRule({60, "INPUT", Protocol::ICMP, "0.0.0.0", "0.0.0.0", 0, 0, FirewallAction::ACCEPT, "Ping 허용"});

    cout << "\n  [현재 방화벽 규칙]\n";
    fw.printRules();

    cout << "\n  [패킷 검사 테스트]\n";
    vector<Packet> testPackets = {
        {"203.0.113.1", "10.0.0.1", 54321, 80, Protocol::TCP, "INPUT"},
        {"203.0.113.2", "10.0.0.1", 54322, 443, Protocol::TCP, "INPUT"},
        {"203.0.113.3", "10.0.0.1", 54323, 22, Protocol::TCP, "INPUT"},
        {"192.168.1.50", "10.0.0.1", 54324, 3306, Protocol::TCP, "INPUT"},
        {"203.0.113.4", "10.0.0.1", 54325, 3306, Protocol::TCP, "INPUT"},
        {"10.0.0.100", "10.0.0.1", 54326, 80, Protocol::TCP, "INPUT"},
        {"203.0.113.5", "10.0.0.1", 0, 0, Protocol::ICMP, "INPUT"},
        {"203.0.113.6", "10.0.0.1", 54327, 8080, Protocol::TCP, "INPUT"},
    };

    for (const auto& pkt : testPackets) {
        FirewallAction result = fw.inspectPacket(pkt);
        string actionStr;
        switch(result) {
            case FirewallAction::ACCEPT: actionStr = "ACCEPT (허용)"; break;
            case FirewallAction::DROP:   actionStr = "DROP   (차단)"; break;
            case FirewallAction::REJECT: actionStr = "REJECT (거부)"; break;
            case FirewallAction::LOG:    actionStr = "LOG    (로그)"; break;
        }
        cout << "  " << pkt.sourceIP << " -> 포트 " << pkt.destPort << " : " << actionStr << "\n";
    }

    fw.printLogs();


    // ═══════════════════════════════════════════════════════════════
    // 데모 2: ACL
    // ═══════════════════════════════════════════════════════════════
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  데모 2: ACL (Access Control List)\n";
    cout << "══════════════════════════════════════════════════\n";

    ACLManager acl("WEB-SERVER-ACL");
    acl.addEntry(10, true, "any", "10.0.0.1", 80, "HTTP 허용");
    acl.addEntry(20, true, "any", "10.0.0.1", 443, "HTTPS 허용");
    acl.addEntry(30, true, "192.168.1.0/24", "10.0.0.1", 22, "내부 SSH");
    acl.addEntry(40, false, "10.0.0.100", "any", 0, "악성IP 차단");
    acl.addEntry(999, false, "any", "any", 0, "기본 차단");
    acl.display();

    cout << "\n  [ACL 테스트]\n";
    cout << "  외부->웹서버 HTTP: " << (acl.isAllowed("203.0.113.1", "10.0.0.1", 80) ? "허용" : "차단") << "\n";
    cout << "  내부->SSH:         " << (acl.isAllowed("192.168.1.50", "10.0.0.1", 22) ? "허용" : "차단") << "\n";
    cout << "  외부->MySQL:       " << (acl.isAllowed("203.0.113.2", "10.0.0.1", 3306) ? "허용" : "차단") << "\n";


    // ═══════════════════════════════════════════════════════════════
    // 데모 3: IDS
    // ═══════════════════════════════════════════════════════════════
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  데모 3: IDS (침입 탐지 시스템)\n";
    cout << "══════════════════════════════════════════════════\n";

    SimpleIDS ids;

    cout << "\n  [정상 트래픽]\n";
    ids.inspect("GET /index.html HTTP/1.1", "203.0.113.1");
    cout << "  GET /index.html -> 정상\n";

    cout << "\n  [악성 트래픽]\n";
    string attacks[] = {
        "GET /search?q=' OR 1=1 --",
        "POST /comment body=<script>alert('XSS')</script>",
        "GET /file?path=../../../etc/passwd",
        "POST /cmd?exec=ls; rm -rf /",
    };
    for (const auto& attack : attacks) {
        bool detected = ids.inspect(attack, "10.0.0.200");
        cout << "  " << attack.substr(0, 50) << " -> " << (detected ? "위협 탐지!" : "정상") << "\n";
    }
    ids.printAlerts();


    // ═══════════════════════════════════════════════════════════════
    // 데모 4: Rate Limiter
    // ═══════════════════════════════════════════════════════════════
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  데모 4: Rate Limiter (DDoS 방어)\n";
    cout << "══════════════════════════════════════════════════\n";

    RateLimiter limiter(5, 60);

    cout << "\n  [정상 사용자: 3회 요청]\n";
    for (int i = 0; i < 3; i++) {
        bool allowed = limiter.allowRequest("192.168.1.10");
        cout << "  요청 " << (i+1) << ": " << (allowed ? "허용" : "차단!") << "\n";
    }

    cout << "\n  [공격자: 10회 연속 요청]\n";
    for (int i = 0; i < 10; i++) {
        bool allowed = limiter.allowRequest("10.0.0.200");
        cout << "  요청 " << (i+1) << ": " << (allowed ? "허용" : "차단!")
             << (i >= 5 ? " <- Rate limit 초과!" : "") << "\n";
    }
    limiter.printStatus();


    // ═══════════════════════════════════════════════════════════════
    // 데모 5: 포트 스캐너
    // ═══════════════════════════════════════════════════════════════
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  데모 5: 포트 스캐너 (localhost)\n";
    cout << "══════════════════════════════════════════════════\n";

    cout << "\n  ★ 주의: 자신의 시스템에서만 테스트하세요!\n\n";

    WinsockHelper winsock;
    if (!winsock.initialized) {
        cout << "  [오류] Winsock 초기화 실패!\n";
        return 1;
    }

    PortScanner scanner("127.0.0.1", 500);
    vector<int> commonPorts = {22, 80, 443, 3306, 5432, 6379, 8080, 3389, 1433};
    vector<int> openPorts;

    for (int port : commonPorts) {
        if (scanner.scanPort(port)) openPorts.push_back(port);
    }
    scanner.printResults(openPorts);


    // ═══════════════════════════════════════════════════════════════
    // 보안 요약
    // ═══════════════════════════════════════════════════════════════
    cout << R"(

  ┌────────────────────────────────────────────────────────────┐
  │                    보안의 다층 방어                         │
  │              (Defense in Depth)                             │
  │                                                            │
  │   ┌──────────────────────────────────────────┐             │
  │   │ Layer 7: WAF (웹 공격 차단)              │             │
  │   │   ┌──────────────────────────────────┐   │             │
  │   │   │ Layer 4: 방화벽 (포트/IP 필터링) │   │             │
  │   │   │   ┌──────────────────────────┐   │   │             │
  │   │   │   │ Layer 3: IDS/IPS         │   │   │             │
  │   │   │   │   ┌──────────────────┐   │   │   │             │
  │   │   │   │   │ 애플리케이션     │   │   │   │             │
  │   │   │   │   │ (인증, 권한검사) │   │   │   │             │
  │   │   │   │   └──────────────────┘   │   │   │             │
  │   │   │   └──────────────────────────┘   │   │             │
  │   │   └──────────────────────────────────┘   │             │
  │   └──────────────────────────────────────────┘             │
  │                                                            │
  │  ★ 보안은 한 겹이 아니라 여러 겹으로!                     │
  └────────────────────────────────────────────────────────────┘
)";

    cout << "\n■ 학습 완료! 다음 단계: 08_routing_switching\n\n";

    return 0;
}
