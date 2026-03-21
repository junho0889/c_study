/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  네트워크 학습 09단계: 네트워크 모니터링과 분석
  ─ SNMP, ICMP/Ping, Traceroute, 대역폭 측정, Wireshark 가이드 ─

  이 파일 하나로 네트워크 모니터링의 핵심 개념을 전부 배웁니다.
  C++로 Ping, Traceroute 시뮬레이션, 네트워크 모니터를 구현합니다.

  ■ 컴파일 방법 (터미널에 입력)
    Windows (MinGW) : g++ -std=c++17 -Wall -o 09_monitor.exe main.cpp -lws2_32
    Windows (MSVC)  : cl /EHsc /std:c++17 /W4 main.cpp ws2_32.lib
    Linux / Mac     : g++ -std=c++17 -Wall -o 09_monitor main.cpp

  ■ 실행 방법
    Windows : .\09_monitor.exe
    Linux   : ./09_monitor

  ★ 참고: Raw Socket을 사용하는 ICMP는 관리자 권한이 필요합니다.
          이 파일에서는 시뮬레이션과 TCP 기반 모니터링을 구현합니다.

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <algorithm>
#include <sstream>
#include <chrono>
#include <iomanip>
#include <cstring>
#include <random>
#include <functional>

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
    #define SOCKET int
    #define INVALID_SOCKET -1
    #define SOCKET_ERROR -1
    #define closesocket close
#endif

using namespace std;


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 1: SNMP 개념과 시뮬레이터
// ─────────────────────────────────────────────────────────────────────────
//
//  SNMP: 네트워크 장비를 모니터링/관리하기 위한 표준 프로토콜
//  UDP 161 (Agent), UDP 162 (Trap)
//
//  ┌─────────────────────────────────────────────────────────────────┐
//  │  SNMP 동작:                                                     │
//  │  GET      : Manager -> Agent (값 요청)                         │
//  │  SET      : Manager -> Agent (값 변경)                         │
//  │  TRAP     : Agent -> Manager (이벤트 알림)                     │
//  │                                                                 │
//  │  OID 예시:                                                      │
//  │  1.3.6.1.2.1.1.1.0  = sysDescr (시스템 설명)                  │
//  │  1.3.6.1.2.1.1.3.0  = sysUpTime (가동 시간)                   │
//  │  1.3.6.1.2.1.1.5.0  = sysName (호스트명)                      │
//  │                                                                 │
//  │  버전: v1(평문), v2c(평문/개선), v3(암호화+인증, 권장)         │
//  └─────────────────────────────────────────────────────────────────┘
//
// ─────────────────────────────────────────────────────────────────────────

class SNMPSimulator {
public:
    struct MIBEntry {
        string oid, name, value, type;
    };

private:
    map<string, MIBEntry> mib_;
    string community_;

public:
    SNMPSimulator(const string& community = "public") : community_(community) {
        mib_["1.3.6.1.2.1.1.1.0"] = {"1.3.6.1.2.1.1.1.0", "sysDescr",
            "Linux server01 5.15.0 x86_64", "STRING"};
        mib_["1.3.6.1.2.1.1.3.0"] = {"1.3.6.1.2.1.1.3.0", "sysUpTime",
            "12345678", "TIMETICKS"};
        mib_["1.3.6.1.2.1.1.5.0"] = {"1.3.6.1.2.1.1.5.0", "sysName",
            "core-router-01", "STRING"};
        mib_["1.3.6.1.2.1.2.1.0"] = {"1.3.6.1.2.1.2.1.0", "ifNumber",
            "4", "INTEGER"};
        mib_["1.3.6.1.4.1.2021.11.9.0"] = {"1.3.6.1.4.1.2021.11.9.0", "ssCpuUser",
            "35", "INTEGER"};
        mib_["1.3.6.1.4.1.2021.4.5.0"] = {"1.3.6.1.4.1.2021.4.5.0", "memTotalReal",
            "16384000", "INTEGER"};
        mib_["1.3.6.1.4.1.2021.4.6.0"] = {"1.3.6.1.4.1.2021.4.6.0", "memAvailReal",
            "8192000", "INTEGER"};
    }

    bool snmpGet(const string& oid, const string& comm, MIBEntry& result) {
        if (comm != community_) {
            cout << "  [SNMP] 인증 실패: Community String 불일치\n";
            return false;
        }
        auto it = mib_.find(oid);
        if (it != mib_.end()) { result = it->second; return true; }
        return false;
    }

    void snmpWalk(const string& comm) {
        if (comm != community_) { cout << "  [SNMP] 인증 실패\n"; return; }
        cout << "\n  ┌────────────────────────────────┬──────────────┬──────────────────────────────┐\n";
        cout << "  │ OID                            │ Name         │ Value                        │\n";
        cout << "  ├────────────────────────────────┼──────────────┼──────────────────────────────┤\n";
        for (const auto& [oid, entry] : mib_) {
            cout << "  │ " << setw(30) << left << entry.oid
                 << " │ " << setw(12) << entry.name
                 << " │ " << setw(28) << entry.value << right << " │\n";
        }
        cout << "  └────────────────────────────────┴──────────────┴──────────────────────────────┘\n";
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 2: ICMP와 Ping (TCP 기반 시뮬레이션)
// ─────────────────────────────────────────────────────────────────────────
//
//  ICMP 메시지: Echo Request(8)/Reply(0), Dest Unreachable(3),
//               Time Exceeded(11, traceroute에 사용)
//
// ─────────────────────────────────────────────────────────────────────────

class PingSimulator {
private:
    double tcpPing(const string& host, int port, int timeoutMs) {
        SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (sock == INVALID_SOCKET) return -1;

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
        inet_pton(AF_INET, host.c_str(), &addr.sin_addr);

        auto start = chrono::high_resolution_clock::now();
        connect(sock, (struct sockaddr*)&addr, sizeof(addr));

        fd_set writeSet; FD_ZERO(&writeSet); FD_SET(sock, &writeSet);
        struct timeval tv;
        tv.tv_sec = timeoutMs / 1000;
        tv.tv_usec = (timeoutMs % 1000) * 1000;

        int result = select(static_cast<int>(sock) + 1, nullptr, &writeSet, nullptr, &tv);
        auto end = chrono::high_resolution_clock::now();
        double rtt = chrono::duration<double, milli>(end - start).count();

        bool isUp = false;
        if (result > 0) {
            int error = 0;
#ifdef _WIN32
            int len = sizeof(error);
            getsockopt(sock, SOL_SOCKET, SO_ERROR, (char*)&error, &len);
#else
            socklen_t len = sizeof(error);
            getsockopt(sock, SOL_SOCKET, SO_ERROR, &error, &len);
#endif
            isUp = (error == 0);
        }
        closesocket(sock);
        return isUp ? rtt : -1;
    }

public:
    struct PingResult { int seq; double rttMs; bool success; };

    vector<PingResult> ping(const string& host, int port, int count, int timeoutMs) {
        vector<PingResult> results;
        cout << "\n  PING " << host << " (TCP port " << port << ")\n";
        for (int i = 1; i <= count; i++) {
            double rtt = tcpPing(host, port, timeoutMs);
            bool ok = (rtt >= 0);
            results.push_back({i, rtt, ok});
            if (ok) cout << "  seq=" << setw(2) << i << "  time=" << fixed << setprecision(2) << setw(8) << rtt << " ms\n";
            else    cout << "  seq=" << setw(2) << i << "  Request timed out\n";
        }
        return results;
    }

    static void printStats(const string& host, const vector<PingResult>& results) {
        int total = results.size(), success = 0;
        double minR = 99999, maxR = 0, sumR = 0;
        for (const auto& r : results) {
            if (r.success) { success++; sumR += r.rttMs; minR = min(minR, r.rttMs); maxR = max(maxR, r.rttMs); }
        }
        cout << "\n  -- " << host << " 통계 --\n";
        cout << "  " << total << "개 전송, " << success << "개 수신, "
             << fixed << setprecision(1) << ((total-success)*100.0/max(total,1)) << "% 손실\n";
        if (success > 0)
            cout << "  RTT: min=" << setprecision(2) << minR << "ms avg=" << sumR/success << "ms max=" << maxR << "ms\n";
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 3: Traceroute 시뮬레이터
// ─────────────────────────────────────────────────────────────────────────
//
//  원리: TTL을 1부터 증가시키며, 각 홉에서 ICMP Time Exceeded 응답 수집
//
// ─────────────────────────────────────────────────────────────────────────

class TracerouteSimulator {
private:
    struct Hop { string ip; string hostname; double rttMs; string asn; };
    map<string, vector<Hop>> routes_;
    mt19937 rng_;

public:
    TracerouteSimulator() : rng_(42) {
        routes_["8.8.8.8"] = {
            {"192.168.1.1", "gateway.local", 0.5, "N/A"},
            {"10.0.0.1", "isp-router.net", 5.2, "AS1234"},
            {"72.14.215.85", "core1.isp.net", 12.3, "AS1234"},
            {"108.170.252.1", "edge1.google.net", 15.7, "AS15169"},
            {"142.251.78.14", "dns.google", 18.2, "AS15169"},
        };
        routes_["1.1.1.1"] = {
            {"192.168.1.1", "gateway.local", 0.4, "N/A"},
            {"10.0.0.1", "isp-router.net", 4.8, "AS1234"},
            {"103.4.10.1", "core2.isp.net", 8.5, "AS1234"},
            {"172.68.10.1", "cf-peer.cloudflare", 11.2, "AS13335"},
            {"1.1.1.1", "one.one.one.one", 13.9, "AS13335"},
        };
    }

    void trace(const string& target) {
        cout << "\n  traceroute to " << target << ", 30 hops max\n";
        auto it = routes_.find(target);
        if (it == routes_.end()) { cout << "  [오류] 경로 데이터 없음\n"; return; }
        uniform_real_distribution<double> jitter(-1.0, 1.0);
        for (size_t i = 0; i < it->second.size(); i++) {
            const auto& hop = it->second[i];
            cout << "  " << setw(2) << (i+1) << "  " << setw(15) << left << hop.ip << " "
                 << setw(25) << hop.hostname << right << fixed << setprecision(2)
                 << "  " << setw(6) << max(0.1, hop.rttMs + jitter(rng_)) << " ms"
                 << "  " << setw(6) << max(0.1, hop.rttMs + jitter(rng_)) << " ms"
                 << "  " << setw(6) << max(0.1, hop.rttMs + jitter(rng_)) << " ms";
            if (hop.asn != "N/A") cout << "  [" << hop.asn << "]";
            cout << "\n";
        }
        cout << "\n  경로 추적 완료: " << it->second.size() << " 홉\n";
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 4: 대역폭/Wireshark/NetFlow 개념
// ─────────────────────────────────────────────────────────────────────────
//
//  대역폭(Bandwidth): 이론적 최대 전송 속도
//  처리량(Throughput): 실제 전송 속도
//  지연(Latency): 패킷 도착 시간
//  지터(Jitter): 지연의 변동폭
//
//  Wireshark 핵심 필터:
//  ┌─────────────────────────────────────────────────────────────────┐
//  │ ip.addr == 10.0.0.1       │ 특정 IP 트래픽                     │
//  │ tcp.port == 80            │ HTTP 트래픽                         │
//  │ dns                       │ DNS 트래픽만                        │
//  │ tcp.analysis.retransmission│ 재전송 (문제 지표!)               │
//  │ http.request.method == GET│ HTTP GET만                         │
//  └─────────────────────────────────────────────────────────────────┘
//
//  NetFlow: 플로우(5-tuple) 기반 트래픽 분석
//  sFlow: 샘플링 기반 (대규모 네트워크에 적합)
//
// ─────────────────────────────────────────────────────────────────────────


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 5: 네트워크 모니터 구현
// ─────────────────────────────────────────────────────────────────────────

struct HostStatus {
    string ip, name;
    int port;
    bool isUp;
    double responseTimeMs;
    string lastCheck;
};

class NetworkMonitor {
private:
    vector<HostStatus> targets_;

    pair<bool, double> checkHost(const string& ip, int port, int timeoutMs) {
        SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (sock == INVALID_SOCKET) return {false, 0};
#ifdef _WIN32
        unsigned long mode = 1; ioctlsocket(sock, FIONBIO, &mode);
#else
        int flags = fcntl(sock, F_GETFL, 0); fcntl(sock, F_SETFL, flags | O_NONBLOCK);
#endif
        struct sockaddr_in addr;
        memset(&addr, 0, sizeof(addr));
        addr.sin_family = AF_INET;
        addr.sin_port = htons(static_cast<unsigned short>(port));
        inet_pton(AF_INET, ip.c_str(), &addr.sin_addr);

        auto start = chrono::high_resolution_clock::now();
        connect(sock, (struct sockaddr*)&addr, sizeof(addr));
        fd_set ws; FD_ZERO(&ws); FD_SET(sock, &ws);
        struct timeval tv; tv.tv_sec = timeoutMs/1000; tv.tv_usec = (timeoutMs%1000)*1000;
        int result = select(static_cast<int>(sock)+1, nullptr, &ws, nullptr, &tv);
        auto end = chrono::high_resolution_clock::now();
        double elapsed = chrono::duration<double, milli>(end - start).count();

        bool isUp = false;
        if (result > 0) {
            int error = 0;
#ifdef _WIN32
            int len = sizeof(error); getsockopt(sock, SOL_SOCKET, SO_ERROR, (char*)&error, &len);
#else
            socklen_t len = sizeof(error); getsockopt(sock, SOL_SOCKET, SO_ERROR, &error, &len);
#endif
            isUp = (error == 0);
        }
        closesocket(sock);
        return {isUp, elapsed};
    }

    string getCurrentTime() {
        auto now = chrono::system_clock::now();
        auto t = chrono::system_clock::to_time_t(now);
        stringstream ss; ss << put_time(localtime(&t), "%H:%M:%S");
        return ss.str();
    }

public:
    void addTarget(const string& ip, const string& name, int port) {
        targets_.push_back({ip, name, port, false, 0, ""});
    }

    void checkAll(int timeoutMs = 1000) {
        for (auto& t : targets_) {
            auto [up, rtt] = checkHost(t.ip, t.port, timeoutMs);
            t.isUp = up; t.responseTimeMs = up ? rtt : 0; t.lastCheck = getCurrentTime();
        }
    }

    void printDashboard() const {
        int total = targets_.size(), up = 0;
        for (const auto& t : targets_) if (t.isUp) up++;

        cout << "\n  ┌────────────────────────────────────────────────────────────────────┐\n";
        cout << "  │                    네트워크 모니터링 대시보드                        │\n";
        cout << "  │                    UP: " << up << "/" << total << "  DOWN: " << (total-up) << "/" << total
             << string(35, ' ') << "│\n";
        cout << "  ├─────────────────┬────────────────┬──────┬────────┬─────────┬────────┤\n";
        cout << "  │ IP              │ Name           │ Port │ Status │ RTT(ms) │ Time   │\n";
        cout << "  ├─────────────────┼────────────────┼──────┼────────┼─────────┼────────┤\n";
        for (const auto& t : targets_) {
            cout << "  │ " << setw(15) << left << t.ip
                 << " │ " << setw(14) << t.name
                 << " │ " << setw(4) << t.port
                 << " │ " << setw(6) << (t.isUp ? "UP" : "DOWN")
                 << " │ " << setw(7) << (t.isUp ? to_string((int)t.responseTimeMs)+"ms" : "N/A")
                 << " │ " << setw(6) << t.lastCheck << right << " │\n";
        }
        cout << "  └─────────────────┴────────────────┴──────┴────────┴─────────┴────────┘\n";
    }

    void checkAlerts() const {
        cout << "\n  === 알림 ===\n";
        bool any = false;
        for (const auto& t : targets_) {
            if (!t.isUp) { cout << "  [CRITICAL] " << t.name << " DOWN!\n"; any = true; }
            else if (t.responseTimeMs > 500) { cout << "  [WARNING] " << t.name << " 지연: " << (int)t.responseTimeMs << "ms\n"; any = true; }
        }
        if (!any) cout << "  모든 서비스 정상\n";
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 6: 로그 분석 / 트러블슈팅 개념
// ─────────────────────────────────────────────────────────────────────────
//
//  로그 수집 체계: 장비(syslog) -> 수집기(Fluentd) -> 저장(ES) -> 시각화(Grafana)
//  ELK Stack: Elasticsearch + Logstash + Kibana
//
//  Syslog 심각도: Emergency(0) ~ Debug(7)
//
//  트러블슈팅 순서:
//  ┌───────────────────────────────────────────────────────────────┐
//  │ 1. 물리: 케이블, LED                                         │
//  │ 2. 데이터링크: MAC 테이블, VLAN, STP                        │
//  │ 3. 네트워크: IP, ping, 라우팅, traceroute                   │
//  │ 4. 전송: 포트, 방화벽, netstat/ss                           │
//  │ 5. 응용: DNS, 서비스 프로세스, 로그, curl                   │
//  └───────────────────────────────────────────────────────────────┘
//
//  진단 명령어: ping, tracert, nslookup, netstat -an, ipconfig /all,
//              arp -a, route print, Test-NetConnection
//
// ─────────────────────────────────────────────────────────────────────────


// ─────────────────────────────────────────────────────────────────────────
// ■ 메인 함수
// ─────────────────────────────────────────────────────────────────────────
int main() {
    cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■\n";
    cout << "■  네트워크 학습 09: 네트워크 모니터링과 분석            ■\n";
    cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■\n";

#ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) { cout << "  Winsock 실패\n"; return 1; }
#endif

    // 데모 1: SNMP
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  데모 1: SNMP 시뮬레이터\n";
    cout << "══════════════════════════════════════════════════\n";

    SNMPSimulator snmp("public");
    cout << "\n  [SNMP GET]\n";
    for (const auto& oid : {"1.3.6.1.2.1.1.1.0", "1.3.6.1.2.1.1.3.0", "1.3.6.1.2.1.1.5.0", "1.3.6.1.4.1.2021.11.9.0"}) {
        SNMPSimulator::MIBEntry result;
        if (snmp.snmpGet(oid, "public", result))
            cout << "  " << result.name << " = " << result.value << " (" << result.type << ")\n";
    }
    cout << "\n  [SNMP Walk]\n";
    snmp.snmpWalk("public");

    cout << "\n  [잘못된 Community String]\n";
    SNMPSimulator::MIBEntry dummy;
    snmp.snmpGet("1.3.6.1.2.1.1.1.0", "wrong", dummy);

    // 데모 2: Ping
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  데모 2: TCP Ping\n";
    cout << "══════════════════════════════════════════════════\n";

    PingSimulator pinger;
    auto r1 = pinger.ping("127.0.0.1", 80, 4, 1000);
    PingSimulator::printStats("127.0.0.1:80", r1);
    auto r2 = pinger.ping("127.0.0.1", 443, 4, 1000);
    PingSimulator::printStats("127.0.0.1:443", r2);

    // 데모 3: Traceroute
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  데모 3: Traceroute 시뮬레이터\n";
    cout << "══════════════════════════════════════════════════\n";

    TracerouteSimulator tracer;
    tracer.trace("8.8.8.8");
    tracer.trace("1.1.1.1");

    // 데모 4: 네트워크 모니터
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  데모 4: 네트워크 모니터\n";
    cout << "══════════════════════════════════════════════════\n";

    NetworkMonitor monitor;
    monitor.addTarget("127.0.0.1", "localhost-http", 80);
    monitor.addTarget("127.0.0.1", "localhost-https", 443);
    monitor.addTarget("127.0.0.1", "localhost-ssh", 22);
    monitor.addTarget("127.0.0.1", "localhost-mysql", 3306);
    monitor.addTarget("127.0.0.1", "localhost-redis", 6379);
    monitor.addTarget("10.0.0.1", "gateway", 80);

    cout << "\n  모니터링 실행 중...\n";
    monitor.checkAll(500);
    monitor.printDashboard();
    monitor.checkAlerts();

    // 트러블슈팅 요약
    cout << R"(

  ┌──────────────────────────────────────────────────────────────┐
  │               네트워크 진단 명령어 빠른 참조                 │
  ├──────────────┬───────────────────────────────────────────────┤
  │ ping         │ 호스트 도달 가능성, RTT                      │
  │ tracert      │ 경로 추적 (Windows)                          │
  │ nslookup     │ DNS 조회                                     │
  │ netstat -an  │ 네트워크 연결 상태                           │
  │ ipconfig /all│ IP 설정 확인                                 │
  │ arp -a       │ ARP 캐시 확인                                │
  │ route print  │ 라우팅 테이블                                │
  │ wireshark    │ 패킷 캡처/분석                               │
  └──────────────┴───────────────────────────────────────────────┘
)";

#ifdef _WIN32
    WSACleanup();
#endif
    cout << "\n■ 학습 완료! 다음 단계: 10_industrial_network\n\n";
    return 0;
}
