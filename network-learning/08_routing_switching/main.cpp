/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  네트워크 학습 08단계: 라우팅과 스위칭
  ─ L2 스위칭, L3 라우팅, VLAN, ARP, STP, 라우팅 프로토콜 ─

  이 파일 하나로 라우팅과 스위칭의 핵심 개념을 전부 배웁니다.
  C++로 라우팅 테이블 시뮬레이터와 ARP 캐시 관리자를 직접 구현합니다.

  ■ 컴파일 방법 (터미널에 입력)
    Windows (MinGW) : g++ -std=c++17 -Wall -o 08_routing.exe main.cpp -lws2_32
    Windows (MSVC)  : cl /EHsc /std:c++17 /W4 main.cpp ws2_32.lib
    Linux / Mac     : g++ -std=c++17 -Wall -o 08_routing main.cpp

  ■ 실행 방법
    Windows : .\08_routing.exe
    Linux   : ./08_routing

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
#include <iomanip>
#include <cstring>
#include <cstdint>
#include <bitset>
#include <queue>
#include <random>

#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib, "ws2_32.lib")
#else
    #include <arpa/inet.h>
#endif

using namespace std;


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 1: L2 스위칭 기초
// ─────────────────────────────────────────────────────────────────────────
//
//  L2 스위치: MAC 주소 기반으로 프레임을 전달하는 네트워크 장비
//
//  ┌─────────────────────────────────────────────────────────────────┐
//  │  동작 원리:                                                     │
//  │  1. 학습 (Learning): 출발지 MAC → MAC 테이블에 기록            │
//  │  2. 전달 (Forwarding): 목적지 MAC이 테이블에 있으면 해당 포트로│
//  │  3. 플러딩 (Flooding): 목적지 MAC 모르면 모든 포트로           │
//  │  4. 필터링 (Filtering): 같은 포트면 전달 안 함                 │
//  └─────────────────────────────────────────────────────────────────┘
//
// ─────────────────────────────────────────────────────────────────────────

class L2Switch {
private:
    string name_;
    int portCount_;
    map<string, int> macTable_;

public:
    L2Switch(const string& name, int ports) : name_(name), portCount_(ports) {}

    vector<int> processFrame(const string& srcMAC, const string& dstMAC, int inPort) {
        vector<int> outPorts;

        // 학습
        macTable_[srcMAC] = inPort;
        cout << "  [학습] " << srcMAC << " -> Port " << inPort << "\n";

        if (dstMAC == "FF:FF:FF:FF:FF:FF") {
            cout << "  [브로드캐스트] 모든 포트로 플러딩 (Port " << inPort << " 제외)\n";
            for (int i = 1; i <= portCount_; i++)
                if (i != inPort) outPorts.push_back(i);
        } else {
            auto it = macTable_.find(dstMAC);
            if (it != macTable_.end()) {
                if (it->second == inPort) {
                    cout << "  [필터링] 같은 포트 -> 폐기\n";
                } else {
                    cout << "  [전달] " << dstMAC << " -> Port " << it->second << "\n";
                    outPorts.push_back(it->second);
                }
            } else {
                cout << "  [플러딩] " << dstMAC << " 알 수 없음 -> 모든 포트\n";
                for (int i = 1; i <= portCount_; i++)
                    if (i != inPort) outPorts.push_back(i);
            }
        }
        return outPorts;
    }

    void printMACTable() const {
        cout << "\n  ┌────────────────────────────────────────┐\n";
        cout << "  │  " << name_ << " - MAC 주소 테이블" << string(max(0, 22 - (int)name_.size()), ' ') << "│\n";
        cout << "  ├────────────────────┬───────────────────┤\n";
        cout << "  │ MAC Address        │ Port              │\n";
        cout << "  ├────────────────────┼───────────────────┤\n";
        for (const auto& [mac, port] : macTable_) {
            cout << "  │ " << setw(18) << left << mac
                 << " │ Port " << setw(13) << left << port << right << "│\n";
        }
        if (macTable_.empty()) cout << "  │  (비어 있음)                          │\n";
        cout << "  └────────────────────┴───────────────────┘\n";
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 2: VLAN (가상 LAN)
// ─────────────────────────────────────────────────────────────────────────
//
//  하나의 물리적 스위치를 논리적으로 여러 네트워크로 분리
//
//  왜 필요한가?
//  ┌─────────────────────────────────────────────────────────────────┐
//  │ 1. 보안: 부서 간 트래픽 분리                                   │
//  │ 2. 성능: 브로드캐스트 도메인 축소                               │
//  │ 3. 유연성: 물리적 위치와 관계없이 논리적 그룹핑                │
//  └─────────────────────────────────────────────────────────────────┘
//
//  트렁크 포트: 여러 VLAN의 트래픽을 하나의 링크로 전달
//  802.1Q 태그: 프레임에 VLAN ID(12bit, 1~4094)를 삽입
//
// ─────────────────────────────────────────────────────────────────────────

class VLANManager {
public:
    struct VLANInfo {
        int id;
        string name;
        string subnet;
        vector<int> ports;
    };

private:
    map<int, VLANInfo> vlans_;
    map<int, int> portVLAN_;
    set<int> trunkPorts_;

public:
    void createVLAN(int id, const string& name, const string& subnet) {
        vlans_[id] = {id, name, subnet, {}};
    }

    void assignPort(int port, int vlanId) {
        portVLAN_[port] = vlanId;
        vlans_[vlanId].ports.push_back(port);
    }

    void setTrunkPort(int port) { trunkPorts_.insert(port); }

    bool isSameVLAN(int port1, int port2) const {
        if (trunkPorts_.count(port1) || trunkPorts_.count(port2)) return true;
        auto it1 = portVLAN_.find(port1);
        auto it2 = portVLAN_.find(port2);
        if (it1 == portVLAN_.end() || it2 == portVLAN_.end()) return false;
        return it1->second == it2->second;
    }

    void printVLANs() const {
        cout << "\n  ┌──────┬────────────────┬──────────────────┬──────────────────────┐\n";
        cout << "  │ VLAN │ Name           │ Subnet           │ Ports                │\n";
        cout << "  ├──────┼────────────────┼──────────────────┼──────────────────────┤\n";
        for (const auto& [id, info] : vlans_) {
            stringstream ports;
            for (size_t i = 0; i < info.ports.size(); i++) {
                if (i > 0) ports << ",";
                ports << info.ports[i];
            }
            cout << "  │ " << setw(4) << id
                 << " │ " << setw(14) << left << info.name
                 << " │ " << setw(16) << info.subnet
                 << " │ " << setw(20) << ports.str() << right << " │\n";
        }
        cout << "  └──────┴────────────────┴──────────────────┴──────────────────────┘\n";
        if (!trunkPorts_.empty()) {
            cout << "  트렁크 포트: ";
            for (int p : trunkPorts_) cout << "Port" << p << " ";
            cout << "\n";
        }
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 3: L3 라우팅과 라우팅 프로토콜
// ─────────────────────────────────────────────────────────────────────────
//
//  ┌─────────────────────────────────────────────────────────────────┐
//  │                 라우팅 프로토콜 비교                              │
//  ├────────┬──────────┬───────────┬──────────┬─────────────────────┤
//  │ 프로토콜│ 유형     │ 알고리즘  │ 범위     │ 특징                │
//  ├────────┼──────────┼───────────┼──────────┼─────────────────────┤
//  │ RIP    │ IGP/DV   │ 벨만-포드 │ 소규모   │ 홉 수 기준, 최대 15│
//  │ OSPF   │ IGP/LS   │ 다익스트라│ 중/대규모│ 가장 널리 사용      │
//  │ BGP    │ EGP/PV   │ 경로 벡터 │ 인터넷   │ AS 간 라우팅        │
//  └────────┴──────────┴───────────┴──────────┴─────────────────────┘
//
// ─────────────────────────────────────────────────────────────────────────


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 4: 라우팅 테이블 시뮬레이터 (Longest Prefix Match)
// ─────────────────────────────────────────────────────────────────────────

uint32_t ipToUint(const string& ip) {
    uint32_t result = 0;
    stringstream ss(ip);
    string octet;
    int shift = 24;
    while (getline(ss, octet, '.')) {
        result |= (stoi(octet) << shift);
        shift -= 8;
    }
    return result;
}

string uintToIP(uint32_t ip) {
    return to_string((ip >> 24) & 0xFF) + "." + to_string((ip >> 16) & 0xFF) + "." +
           to_string((ip >> 8) & 0xFF) + "." + to_string(ip & 0xFF);
}

uint32_t prefixToMask(int prefix) {
    if (prefix == 0) return 0;
    return ~((1u << (32 - prefix)) - 1);
}

struct RouteEntry {
    string network;
    int prefixLen;
    string nextHop;
    string interface_;
    int metric;
    string protocol;
};

// ★ 라우팅 테이블 시뮬레이터
class RoutingTable {
private:
    string routerName_;
    vector<RouteEntry> routes_;

public:
    RoutingTable(const string& name) : routerName_(name) {}

    void addRoute(const string& network, int prefix, const string& nextHop,
                  const string& iface, int metric, const string& proto) {
        routes_.push_back({network, prefix, nextHop, iface, metric, proto});
    }

    // ★ Longest Prefix Match
    const RouteEntry* lookup(const string& destIP) const {
        uint32_t dest = ipToUint(destIP);
        const RouteEntry* bestMatch = nullptr;
        int longestPrefix = -1;

        for (const auto& route : routes_) {
            uint32_t network = ipToUint(route.network);
            uint32_t mask = prefixToMask(route.prefixLen);
            if ((dest & mask) == (network & mask)) {
                if (route.prefixLen > longestPrefix) {
                    longestPrefix = route.prefixLen;
                    bestMatch = &route;
                }
            }
        }
        return bestMatch;
    }

    void printTable() const {
        cout << "\n  ┌─────────────────────────────────────────────────────────────────────────────┐\n";
        cout << "  │  라우팅 테이블: " << setw(60) << left << routerName_ << right << "│\n";
        cout << "  ├───────────────────┬────┬─────────────────┬──────────┬────────┬──────────────┤\n";
        cout << "  │ Destination       │ /  │ Next Hop        │ Iface    │ Metric │ Protocol     │\n";
        cout << "  ├───────────────────┼────┼─────────────────┼──────────┼────────┼──────────────┤\n";
        for (const auto& r : routes_) {
            cout << "  │ " << setw(17) << left << r.network
                 << " │ " << setw(2) << r.prefixLen
                 << " │ " << setw(15) << r.nextHop
                 << " │ " << setw(8) << r.interface_
                 << " │ " << setw(6) << r.metric
                 << " │ " << setw(12) << r.protocol << right << " │\n";
        }
        cout << "  └───────────────────┴────┴─────────────────┴──────────┴────────┴──────────────┘\n";
    }

    void forwardPacket(const string& srcIP, const string& destIP) const {
        cout << "\n  [패킷] " << srcIP << " -> " << destIP << "\n";
        const RouteEntry* route = lookup(destIP);
        if (route) {
            cout << "  [매칭] " << route->network << "/" << route->prefixLen
                 << " via " << route->nextHop << " dev " << route->interface_
                 << " (" << route->protocol << ")\n";
        } else {
            cout << "  [오류] 경로를 찾을 수 없음!\n";
        }
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 5: ARP 캐시 관리자
// ─────────────────────────────────────────────────────────────────────────
//
//  ARP: IP 주소 → MAC 주소 변환 프로토콜
//
//  ┌─────────────────────────────────────────────────────────────────┐
//  │  1. ARP Request (브로드캐스트): "10.0.0.2의 MAC은?"             │
//  │  2. ARP Reply (유니캐스트): "내 MAC은 BB:BB:BB:BB:BB:BB"       │
//  │  3. ARP 캐시에 저장 (일정 시간 후 만료)                        │
//  │                                                                 │
//  │  ★ ARP 스푸핑: 거짓 ARP Reply → 중간자 공격(MITM)             │
//  │    방어: Dynamic ARP Inspection (DAI), Static ARP               │
//  └─────────────────────────────────────────────────────────────────┘
//
// ─────────────────────────────────────────────────────────────────────────

class ARPCache {
public:
    enum class EntryType { DYNAMIC, STATIC };

    struct ARPEntry {
        string ipAddress;
        string macAddress;
        EntryType type;
        int timeoutSec;
    };

private:
    map<string, ARPEntry> cache_;

public:
    void addEntry(const string& ip, const string& mac, EntryType type = EntryType::DYNAMIC) {
        cache_[ip] = {ip, mac, type, 300};
    }

    string resolve(const string& ip) const {
        auto it = cache_.find(ip);
        return it != cache_.end() ? it->second.macAddress : "";
    }

    void simulateARPRequest(const string& srcIP, const string& srcMAC, const string& targetIP) {
        cout << "\n  [ARP Request] Who has " << targetIP << "? Tell " << srcIP << "\n";
        string mac = resolve(targetIP);
        if (!mac.empty()) {
            cout << "  [ARP Reply] " << targetIP << " is at " << mac << "\n";
        } else {
            cout << "  [ARP] 캐시 미스 -> 네트워크로 브로드캐스트\n";
        }
    }

    void printCache() const {
        cout << "\n  ┌─────────────────┬────────────────────┬─────────┬───────────┐\n";
        cout << "  │ IP Address      │ MAC Address        │ Type    │ Timeout   │\n";
        cout << "  ├─────────────────┼────────────────────┼─────────┼───────────┤\n";
        for (const auto& [ip, entry] : cache_) {
            string typeStr = (entry.type == EntryType::STATIC) ? "STATIC" : "DYNAMIC";
            string timeout = (entry.type == EntryType::STATIC) ? "permanent" : to_string(entry.timeoutSec) + "s";
            cout << "  │ " << setw(15) << left << entry.ipAddress
                 << " │ " << setw(18) << entry.macAddress
                 << " │ " << setw(7) << typeStr
                 << " │ " << setw(9) << timeout << right << " │\n";
        }
        if (cache_.empty()) cout << "  │  (비어 있음)                                              │\n";
        cout << "  └─────────────────┴────────────────────┴─────────┴───────────┘\n";
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 6: STP (스패닝 트리 프로토콜) / 네트워크 토폴로지 개념
// ─────────────────────────────────────────────────────────────────────────
//
//  STP: L2 네트워크에서 루프를 방지하는 프로토콜
//
//  루프가 위험한 이유:
//  - 브로드캐스트 스톰 (프레임 무한 순환)
//  - MAC 테이블 불안정
//  → STP가 중복 경로를 차단(Blocking)하여 루프 방지
//  → RSTP (802.1w): 수렴 시간 30-50초 → 1-2초로 단축
//
//  ┌──────────┬────────────┬────────────┬────────────┬──────────────┐
//  │ 토폴로지 │ 장점       │ 단점       │ 비용       │ 용도         │
//  ├──────────┼────────────┼────────────┼────────────┼──────────────┤
//  │ 스타     │ 관리 쉬움  │ 중앙 장애  │ 보통       │ 사무실       │
//  │ 메시     │ 높은 가용성│ 비용 높음  │ 매우 높음  │ 데이터센터   │
//  │ 링       │ 균등 접근  │ 단일 장애  │ 보통       │ 레거시       │
//  │ 트리     │ 계층적     │ 루트 장애  │ 보통       │ 기업 네트워크│
//  └──────────┴────────────┴────────────┴────────────┴──────────────┘
//
// ─────────────────────────────────────────────────────────────────────────


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 7: OSPF 간단 시뮬레이터 (다익스트라 알고리즘)
// ─────────────────────────────────────────────────────────────────────────

class OSPFSimulator {
public:
    struct Link { string dest; int cost; };

private:
    map<string, vector<Link>> adjacency_;

public:
    void addLink(const string& from, const string& to, int cost) {
        adjacency_[from].push_back({to, cost});
        adjacency_[to].push_back({from, cost});
    }

    map<string, pair<int, string>> calculateSPF(const string& source) {
        map<string, pair<int, string>> dist;
        for (const auto& [node, _] : adjacency_) dist[node] = {INT_MAX, ""};
        dist[source] = {0, ""};

        priority_queue<pair<int,string>, vector<pair<int,string>>, greater<>> pq;
        pq.push({0, source});
        set<string> visited;

        while (!pq.empty()) {
            auto [cost, node] = pq.top(); pq.pop();
            if (visited.count(node)) continue;
            visited.insert(node);
            for (const auto& link : adjacency_[node]) {
                int newCost = cost + link.cost;
                if (newCost < dist[link.dest].first) {
                    dist[link.dest] = {newCost, node};
                    pq.push({newCost, link.dest});
                }
            }
        }
        return dist;
    }

    void printTopology() const {
        cout << "\n  === OSPF 네트워크 토폴로지 ===\n";
        for (const auto& [node, links] : adjacency_) {
            cout << "  [" << node << "] -> ";
            for (size_t i = 0; i < links.size(); i++) {
                if (i > 0) cout << ", ";
                cout << links[i].dest << "(cost:" << links[i].cost << ")";
            }
            cout << "\n";
        }
    }

    void printSPFResult(const string& source, const map<string, pair<int, string>>& result) const {
        cout << "\n  ┌────────────────┬──────────┬────────────────────┐\n";
        cout << "  │ Destination    │ Cost     │ Via                │\n";
        cout << "  ├────────────────┼──────────┼────────────────────┤\n";
        for (const auto& [dest, info] : result) {
            string via = info.second.empty() ? "(self)" : info.second;
            cout << "  │ " << setw(14) << left << dest
                 << " │ " << setw(8) << info.first
                 << " │ " << setw(18) << via << right << " │\n";
        }
        cout << "  └────────────────┴──────────┴────────────────────┘\n";
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 메인 함수
// ─────────────────────────────────────────────────────────────────────────
int main() {
    cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■\n";
    cout << "■  네트워크 학습 08: 라우팅과 스위칭                     ■\n";
    cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■\n";

    // 데모 1: L2 스위치
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  데모 1: L2 스위치 시뮬레이터\n";
    cout << "══════════════════════════════════════════════════\n";

    L2Switch sw("Core-Switch-1", 8);
    cout << "\n  [프레임 1] PC-A -> PC-B (처음)\n";
    sw.processFrame("AA:BB:CC:DD:EE:01", "AA:BB:CC:DD:EE:02", 1);
    cout << "\n  [프레임 2] PC-B -> PC-A (응답)\n";
    sw.processFrame("AA:BB:CC:DD:EE:02", "AA:BB:CC:DD:EE:01", 3);
    cout << "\n  [프레임 3] PC-A -> PC-B (이제 MAC 알고 있음)\n";
    sw.processFrame("AA:BB:CC:DD:EE:01", "AA:BB:CC:DD:EE:02", 1);
    cout << "\n  [프레임 4] PC-C -> 브로드캐스트\n";
    sw.processFrame("AA:BB:CC:DD:EE:03", "FF:FF:FF:FF:FF:FF", 5);
    sw.printMACTable();

    // 데모 2: VLAN
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  데모 2: VLAN 구성\n";
    cout << "══════════════════════════════════════════════════\n";

    VLANManager vlanMgr;
    vlanMgr.createVLAN(10, "Server", "10.1.10.0/24");
    vlanMgr.createVLAN(20, "Office", "10.1.20.0/24");
    vlanMgr.createVLAN(30, "Dev", "10.1.30.0/24");
    vlanMgr.createVLAN(99, "Management", "10.1.99.0/24");
    vlanMgr.assignPort(1, 10); vlanMgr.assignPort(2, 10);
    vlanMgr.assignPort(3, 20); vlanMgr.assignPort(4, 20);
    vlanMgr.assignPort(5, 30); vlanMgr.assignPort(6, 30);
    vlanMgr.assignPort(7, 99);
    vlanMgr.setTrunkPort(8);
    vlanMgr.printVLANs();

    cout << "\n  [VLAN 통신 테스트]\n";
    struct { int p1; int p2; string desc; } vlanTests[] = {
        {1, 2, "서버 내부"}, {1, 3, "서버->사무실"}, {3, 4, "사무실 내부"}, {5, 8, "개발->트렁크"},
    };
    for (const auto& t : vlanTests) {
        cout << "  Port" << t.p1 << " <-> Port" << t.p2 << " (" << t.desc << "): "
             << (vlanMgr.isSameVLAN(t.p1, t.p2) ? "통신 가능" : "L3 라우팅 필요") << "\n";
    }

    // 데모 3: 라우팅 테이블
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  데모 3: 라우팅 테이블 (Longest Prefix Match)\n";
    cout << "══════════════════════════════════════════════════\n";

    RoutingTable rt("Core-Router-1");
    rt.addRoute("10.1.10.0", 24, "0.0.0.0", "eth0", 0, "connected");
    rt.addRoute("10.1.20.0", 24, "0.0.0.0", "eth1", 0, "connected");
    rt.addRoute("10.1.30.0", 24, "0.0.0.0", "eth2", 0, "connected");
    rt.addRoute("192.168.1.0", 24, "10.1.10.1", "eth0", 10, "OSPF");
    rt.addRoute("172.16.0.0", 16, "10.1.10.2", "eth0", 20, "OSPF");
    rt.addRoute("172.16.5.0", 24, "10.1.10.3", "eth0", 15, "OSPF");
    rt.addRoute("0.0.0.0", 0, "203.0.113.1", "eth3", 100, "static");
    rt.printTable();

    rt.forwardPacket("10.1.10.100", "10.1.20.50");
    rt.forwardPacket("10.1.10.100", "172.16.5.100");  // /24 LPM!
    rt.forwardPacket("10.1.10.100", "172.16.100.1");   // /16
    rt.forwardPacket("10.1.10.100", "8.8.8.8");        // 기본 경로

    // 데모 4: ARP 캐시
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  데모 4: ARP 캐시 관리자\n";
    cout << "══════════════════════════════════════════════════\n";

    ARPCache arp;
    arp.addEntry("10.1.10.1", "00:11:22:33:44:01", ARPCache::EntryType::STATIC);
    arp.addEntry("10.1.10.100", "AA:BB:CC:DD:EE:01");
    arp.addEntry("10.1.10.101", "AA:BB:CC:DD:EE:02");
    arp.addEntry("10.1.20.50", "DD:EE:FF:00:11:22");
    arp.printCache();

    cout << "\n  [ARP 조회]\n";
    for (const auto& ip : {"10.1.10.1", "10.1.10.100", "10.1.10.200"}) {
        string mac = arp.resolve(ip);
        cout << "  " << ip << " -> " << (mac.empty() ? "??? (캐시 미스)" : mac) << "\n";
    }
    arp.simulateARPRequest("10.1.10.100", "AA:BB:CC:DD:EE:01", "10.1.10.200");

    // 데모 5: OSPF
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  데모 5: OSPF SPF 계산\n";
    cout << "══════════════════════════════════════════════════\n";

    OSPFSimulator ospf;
    ospf.addLink("R1", "R2", 10);
    ospf.addLink("R2", "R3", 5);
    ospf.addLink("R1", "R4", 20);
    ospf.addLink("R2", "R5", 15);
    ospf.addLink("R3", "R6", 10);
    ospf.addLink("R4", "R5", 5);
    ospf.addLink("R5", "R6", 25);
    ospf.printTopology();

    auto spfResult = ospf.calculateSPF("R1");
    ospf.printSPFResult("R1", spfResult);

    // IP 유틸리티
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  IP 변환 유틸리티\n";
    cout << "══════════════════════════════════════════════════\n";

    string testIP = "192.168.1.100";
    uint32_t ipNum = ipToUint(testIP);
    cout << "\n  IP: " << testIP << " -> 정수: " << ipNum
         << " -> 이진: " << bitset<32>(ipNum) << " -> 복원: " << uintToIP(ipNum) << "\n";

    cout << "\n  서브넷 마스크:\n";
    for (int p : {8, 16, 24, 25, 28, 30, 32}) {
        cout << "  /" << setw(2) << p << " -> " << uintToIP(prefixToMask(p)) << "\n";
    }

    cout << "\n\n■ 학습 완료! 다음 단계: 09_network_monitoring\n\n";
    return 0;
}
