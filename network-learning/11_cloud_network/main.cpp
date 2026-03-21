/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  네트워크 학습 11단계: 클라우드 인프라 시뮬레이터
  ─ VPC, 서브넷, Security Group, 라우팅 테이블 모델링 ─

  이 파일은 클라우드 네트워크 구성을 C++로 시뮬레이션합니다.
  guide.md와 함께 학습하세요.

  ■ 컴파일 방법 (터미널에 입력)
    Windows (MinGW) : g++ -std=c++17 -Wall -o 11_cloud.exe main.cpp -lws2_32
    Windows (MSVC)  : cl /EHsc /std:c++17 /W4 main.cpp ws2_32.lib
    Linux / Mac     : g++ -std=c++17 -Wall -o 11_cloud main.cpp

  ■ 실행 방법
    Windows : .\11_cloud.exe
    Linux   : ./11_cloud

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <sstream>
#include <iomanip>
#include <cstdint>
#include <algorithm>
#include <functional>

using namespace std;


// ─────────────────────────────────────────────────────────────────────────
// ■ 유틸리티: IP 주소 변환
// ─────────────────────────────────────────────────────────────────────────

namespace IPUtil {
    uint32_t toUint(const string& ip) {
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

    string fromUint(uint32_t ip) {
        return to_string((ip >> 24) & 0xFF) + "." +
               to_string((ip >> 16) & 0xFF) + "." +
               to_string((ip >> 8) & 0xFF) + "." +
               to_string(ip & 0xFF);
    }

    uint32_t prefixToMask(int prefix) {
        if (prefix == 0) return 0;
        return ~((1u << (32 - prefix)) - 1);
    }

    bool isInSubnet(const string& ip, const string& network, int prefix) {
        uint32_t ipNum = toUint(ip);
        uint32_t netNum = toUint(network);
        uint32_t mask = prefixToMask(prefix);
        return (ipNum & mask) == (netNum & mask);
    }
}


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 1: Security Group (보안 그룹) 엔진
// ─────────────────────────────────────────────────────────────────────────
//
//  Security Group = 인스턴스 레벨 방화벽 (Stateful)
//
//  ┌─────────────────────────────────────────────────────────────────┐
//  │  Stateful의 의미:                                               │
//  │                                                                 │
//  │  인바운드에서 포트 80을 허용하면                                │
//  │  → 그 응답(아웃바운드)은 자동으로 허용됨                       │
//  │  → 아웃바운드에 별도 규칙 불필요!                               │
//  │                                                                 │
//  │  비유: "들어온 손님은 나갈 때 별도 허가 불필요"                 │
//  └─────────────────────────────────────────────────────────────────┘
//
// ─────────────────────────────────────────────────────────────────────────

class SecurityGroup {
public:
    enum class Direction { INBOUND, OUTBOUND };
    enum class Protocol { TCP, UDP, ICMP, ALL };

    struct Rule {
        Direction direction;
        Protocol protocol;
        int fromPort;
        int toPort;         // 범위 지원 (fromPort ~ toPort)
        string source;      // CIDR 또는 Security Group ID
        string description;
    };

private:
    string id_;
    string name_;
    string vpcId_;
    vector<Rule> rules_;

    string protocolStr(Protocol p) const {
        switch(p) {
            case Protocol::TCP: return "TCP";
            case Protocol::UDP: return "UDP";
            case Protocol::ICMP: return "ICMP";
            case Protocol::ALL: return "ALL";
        }
        return "?";
    }

    string directionStr(Direction d) const {
        return d == Direction::INBOUND ? "INBOUND" : "OUTBOUND";
    }

    bool matchCIDR(const string& sourceIP, const string& cidr) const {
        if (cidr == "0.0.0.0/0") return true;

        size_t slashPos = cidr.find('/');
        if (slashPos == string::npos) return sourceIP == cidr;

        string network = cidr.substr(0, slashPos);
        int prefix = stoi(cidr.substr(slashPos + 1));
        return IPUtil::isInSubnet(sourceIP, network, prefix);
    }

public:
    SecurityGroup(const string& id, const string& name, const string& vpcId)
        : id_(id), name_(name), vpcId_(vpcId) {}

    const string& getId() const { return id_; }
    const string& getName() const { return name_; }

    // 규칙 추가
    void addRule(Direction dir, Protocol proto, int fromPort, int toPort,
                 const string& source, const string& desc) {
        rules_.push_back({dir, proto, fromPort, toPort, source, desc});
    }

    // 트래픽 허용 여부 확인
    bool isAllowed(Direction dir, Protocol proto, int port,
                   const string& sourceIP) const {
        for (const auto& rule : rules_) {
            if (rule.direction != dir) continue;
            if (rule.protocol != Protocol::ALL && rule.protocol != proto) continue;

            // 포트 범위 확인
            if (rule.protocol != Protocol::ICMP && rule.protocol != Protocol::ALL) {
                if (port < rule.fromPort || port > rule.toPort) continue;
            }

            // 소스 확인
            if (matchCIDR(sourceIP, rule.source)) {
                return true;  // 허용 (SG는 허용 규칙만 있음)
            }
        }
        return false;  // 기본: 차단
    }

    // Security Group 규칙 출력
    void printRules() const {
        cout << "\n  ┌────────────────────────────────────────────────────────────────────┐\n";
        cout << "  │  Security Group: " << setw(14) << left << name_
             << "  ID: " << setw(28) << id_ << right << "│\n";
        cout << "  │  VPC: " << setw(58) << left << vpcId_ << right << "│\n";
        cout << "  ├──────────┬──────┬─────────────┬─────────────────┬──────────────────┤\n";
        cout << "  │ Direction│Proto │ Port Range  │ Source/Dest     │ Description      │\n";
        cout << "  ├──────────┼──────┼─────────────┼─────────────────┼──────────────────┤\n";

        for (const auto& r : rules_) {
            string portRange;
            if (r.protocol == Protocol::ALL || r.protocol == Protocol::ICMP) {
                portRange = "All";
            } else if (r.fromPort == r.toPort) {
                portRange = to_string(r.fromPort);
            } else {
                portRange = to_string(r.fromPort) + "-" + to_string(r.toPort);
            }

            cout << "  │ " << setw(8) << left << directionStr(r.direction)
                 << " │ " << setw(4) << protocolStr(r.protocol)
                 << " │ " << setw(11) << portRange
                 << " │ " << setw(15) << r.source
                 << " │ " << setw(16) << r.description << right << " │\n";
        }
        cout << "  └──────────┴──────┴─────────────┴─────────────────┴──────────────────┘\n";
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 2: 서브넷 모델
// ─────────────────────────────────────────────────────────────────────────

class Subnet {
public:
    enum class Type { PUBLIC, PRIVATE };

private:
    string id_;
    string name_;
    string vpcId_;
    string cidr_;
    string az_;         // 가용 영역
    Type type_;
    string routeTableId_;

public:
    Subnet(const string& id, const string& name, const string& vpcId,
           const string& cidr, const string& az, Type type)
        : id_(id), name_(name), vpcId_(vpcId), cidr_(cidr), az_(az), type_(type) {}

    const string& getId() const { return id_; }
    const string& getName() const { return name_; }
    const string& getCIDR() const { return cidr_; }
    const string& getAZ() const { return az_; }
    Type getType() const { return type_; }

    void setRouteTable(const string& rtId) { routeTableId_ = rtId; }
    const string& getRouteTableId() const { return routeTableId_; }

    bool containsIP(const string& ip) const {
        size_t slashPos = cidr_.find('/');
        string network = cidr_.substr(0, slashPos);
        int prefix = stoi(cidr_.substr(slashPos + 1));
        return IPUtil::isInSubnet(ip, network, prefix);
    }

    string typeStr() const {
        return type_ == Type::PUBLIC ? "Public" : "Private";
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 3: 라우팅 테이블
// ─────────────────────────────────────────────────────────────────────────

class RouteTable {
public:
    struct Route {
        string destination;     // CIDR (예: "0.0.0.0/0")
        string target;          // igw-xxx, nat-xxx, local, pcx-xxx
        string description;
    };

private:
    string id_;
    string name_;
    vector<Route> routes_;

public:
    RouteTable(const string& id, const string& name)
        : id_(id), name_(name) {}

    const string& getId() const { return id_; }

    void addRoute(const string& dest, const string& target, const string& desc) {
        routes_.push_back({dest, target, desc});
    }

    // 경로 조회 (Longest Prefix Match)
    string lookup(const string& destIP) const {
        const Route* bestMatch = nullptr;
        int longestPrefix = -1;

        for (const auto& route : routes_) {
            size_t slashPos = route.destination.find('/');
            string network = route.destination.substr(0, slashPos);
            int prefix = stoi(route.destination.substr(slashPos + 1));

            if (IPUtil::isInSubnet(destIP, network, prefix)) {
                if (prefix > longestPrefix) {
                    longestPrefix = prefix;
                    bestMatch = &route;
                }
            }
        }

        return bestMatch ? bestMatch->target : "no-route";
    }

    void printTable() const {
        cout << "\n  ┌────────────────────────────────────────────────────────┐\n";
        cout << "  │  Route Table: " << setw(14) << left << name_
             << "  ID: " << setw(22) << id_ << right << "│\n";
        cout << "  ├──────────────────┬───────────────────┬─────────────────┤\n";
        cout << "  │ Destination      │ Target            │ Description     │\n";
        cout << "  ├──────────────────┼───────────────────┼─────────────────┤\n";

        for (const auto& r : routes_) {
            cout << "  │ " << setw(16) << left << r.destination
                 << " │ " << setw(17) << r.target
                 << " │ " << setw(15) << r.description << right << " │\n";
        }
        cout << "  └──────────────────┴───────────────────┴─────────────────┘\n";
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 섹션 4: VPC (Virtual Private Cloud) 모델
// ─────────────────────────────────────────────────────────────────────────

class VPC {
private:
    string id_;
    string name_;
    string cidr_;
    string region_;

    vector<Subnet> subnets_;
    map<string, RouteTable> routeTables_;
    map<string, SecurityGroup> securityGroups_;

    // 게이트웨이
    bool hasIGW_ = false;
    string igwId_;
    bool hasNATGW_ = false;
    string natGWId_;
    string natGWSubnetId_;

public:
    VPC(const string& id, const string& name, const string& cidr, const string& region)
        : id_(id), name_(name), cidr_(cidr), region_(region) {}

    const string& getId() const { return id_; }
    const string& getName() const { return name_; }

    // Internet Gateway 연결
    void attachIGW(const string& igwId) {
        hasIGW_ = true;
        igwId_ = igwId;
    }

    // NAT Gateway 생성
    void createNATGW(const string& natId, const string& subnetId) {
        hasNATGW_ = true;
        natGWId_ = natId;
        natGWSubnetId_ = subnetId;
    }

    // 서브넷 추가
    void addSubnet(const Subnet& subnet) {
        subnets_.push_back(subnet);
    }

    // 라우팅 테이블 추가
    void addRouteTable(const RouteTable& rt) {
        routeTables_[rt.getId()] = rt;
    }

    // Security Group 추가
    void addSecurityGroup(const SecurityGroup& sg) {
        securityGroups_[sg.getId()] = sg;
    }

    // 서브넷 찾기 (IP 기반)
    const Subnet* findSubnet(const string& ip) const {
        for (const auto& subnet : subnets_) {
            if (subnet.containsIP(ip)) return &subnet;
        }
        return nullptr;
    }

    // 네트워크 토폴로지 출력
    void printTopology() const {
        cout << "\n  ╔════════════════════════════════════════════════════════════════╗\n";
        cout << "  ║  VPC: " << setw(15) << left << name_
             << "  CIDR: " << setw(16) << cidr_
             << "  Region: " << setw(10) << region_ << right << "║\n";
        cout << "  ║  ID: " << setw(58) << left << id_ << right << "║\n";
        cout << "  ╠════════════════════════════════════════════════════════════════╣\n";

        // 게이트웨이 정보
        if (hasIGW_) {
            cout << "  ║  [IGW] " << setw(55) << left << igwId_ << right << "║\n";
        }
        if (hasNATGW_) {
            cout << "  ║  [NAT GW] " << setw(52) << left
                 << (natGWId_ + " (in " + natGWSubnetId_ + ")") << right << "║\n";
        }

        cout << "  ╠════════════════════════════════════════════════════════════════╣\n";

        // 서브넷 정보
        cout << "  ║  Subnets:                                                      ║\n";
        for (const auto& subnet : subnets_) {
            cout << "  ║    [" << setw(7) << left << subnet.typeStr() << "] "
                 << setw(12) << subnet.getName() << " "
                 << setw(16) << subnet.getCIDR() << " "
                 << setw(12) << subnet.getAZ()
                 << "     ║\n" << right;
        }

        cout << "  ╠════════════════════════════════════════════════════════════════╣\n";

        // Security Group 정보
        cout << "  ║  Security Groups:                                              ║\n";
        for (const auto& [id, sg] : securityGroups_) {
            cout << "  ║    " << setw(15) << left << sg.getName()
                 << " (" << setw(43) << (id + ")") << right << "║\n";
        }

        cout << "  ╚════════════════════════════════════════════════════════════════╝\n";
    }

    // 상세 네트워크 다이어그램 출력
    void printDiagram() const {
        cout << R"(
  ┌────────────────────────────────────────────────────────────────┐
  │                         인터넷                                 │
  └────────────────────────────┬───────────────────────────────────┘
                               │
  )" << "                          ┌────▼────┐\n";
        if (hasIGW_) {
            cout << "                          │  IGW    │  " << igwId_ << "\n";
        } else {
            cout << "                          │ (No IGW)│\n";
        }
        cout << R"(                          └────┬────┘
                               │
  ┌────────────────────────────┼───────────────────────────────────┐
  │  VPC: )" << name_ << " (" << cidr_ << R"()                                │
  │                            │                                   │
)";

        // Public 서브넷 표시
        bool firstPub = true;
        for (const auto& s : subnets_) {
            if (s.getType() == Subnet::Type::PUBLIC) {
                if (firstPub) {
                    cout << "  │    ┌─────────────────────┐                                   │\n";
                    firstPub = false;
                }
                cout << "  │    │ " << setw(11) << left << s.getName()
                     << "          │  " << setw(16) << s.getCIDR()
                     << "  [" << s.getAZ() << "]     │\n" << right;
            }
        }
        if (!firstPub) cout << "  │    └─────────────────────┘                                   │\n";

        // NAT Gateway
        if (hasNATGW_) {
            cout << "  │              │                                                   │\n";
            cout << "  │         ┌────▼────┐                                              │\n";
            cout << "  │         │ NAT GW  │  " << natGWId_ << "                          │\n";
            cout << "  │         └────┬────┘                                              │\n";
            cout << "  │              │                                                   │\n";
        }

        // Private 서브넷 표시
        bool firstPriv = true;
        for (const auto& s : subnets_) {
            if (s.getType() == Subnet::Type::PRIVATE) {
                if (firstPriv) {
                    cout << "  │    ┌─────────────────────┐                                   │\n";
                    firstPriv = false;
                }
                cout << "  │    │ " << setw(11) << left << s.getName()
                     << "          │  " << setw(16) << s.getCIDR()
                     << "  [" << s.getAZ() << "]     │\n" << right;
            }
        }
        if (!firstPriv) cout << "  │    └─────────────────────┘                                   │\n";

        cout << "  │                                                               │\n";
        cout << "  └───────────────────────────────────────────────────────────────┘\n";
    }

    // 트래픽 시뮬레이션
    void simulateTraffic(const string& srcIP, const string& dstIP, int dstPort,
                         const string& sgId) const {
        cout << "\n  [트래픽] " << srcIP << " → " << dstIP << ":" << dstPort << "\n";

        // 1. 소스 서브넷 확인
        const Subnet* srcSubnet = findSubnet(srcIP);
        if (srcSubnet) {
            cout << "  [서브넷] 출발: " << srcSubnet->getName()
                 << " (" << srcSubnet->typeStr() << ")\n";
        }

        // 2. 목적지 서브넷 확인
        const Subnet* dstSubnet = findSubnet(dstIP);
        if (dstSubnet) {
            cout << "  [서브넷] 도착: " << dstSubnet->getName()
                 << " (" << dstSubnet->typeStr() << ")\n";
        } else {
            // VPC 외부
            cout << "  [라우팅] VPC 외부 → ";
            if (srcSubnet) {
                auto rtIt = routeTables_.find(srcSubnet->getRouteTableId());
                if (rtIt != routeTables_.end()) {
                    string target = rtIt->second.lookup(dstIP);
                    cout << "Target: " << target << "\n";

                    if (target.substr(0, 3) == "igw") {
                        cout << "  [경로] Internet Gateway 통과 → 인터넷\n";
                    } else if (target.substr(0, 3) == "nat") {
                        cout << "  [경로] NAT Gateway 통과 → 인터넷 (아웃바운드만)\n";
                    } else if (target == "no-route") {
                        cout << "  [오류] 라우팅 경로 없음!\n";
                        return;
                    }
                }
            }
        }

        // 3. Security Group 확인
        auto sgIt = securityGroups_.find(sgId);
        if (sgIt != securityGroups_.end()) {
            bool allowed = sgIt->second.isAllowed(
                SecurityGroup::Direction::INBOUND,
                SecurityGroup::Protocol::TCP,
                dstPort, srcIP
            );
            cout << "  [SG] " << sgIt->second.getName() << ": "
                 << (allowed ? "ALLOW (허용)" : "DENY (차단)") << "\n";
        }
    }

    // 라우팅 테이블 전체 출력
    void printAllRouteTables() const {
        for (const auto& [id, rt] : routeTables_) {
            rt.printTable();
        }
    }

    // Security Group 전체 출력
    void printAllSecurityGroups() const {
        for (const auto& [id, sg] : securityGroups_) {
            sg.printRules();
        }
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 메인 함수 ─ 클라우드 인프라 시뮬레이션
// ─────────────────────────────────────────────────────────────────────────
int main() {
    cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■\n";
    cout << "■  네트워크 학습 11: 클라우드 인프라 시뮬레이터          ■\n";
    cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■\n";


    // ═══════════════════════════════════════════════════════════════
    // VPC 생성
    // ═══════════════════════════════════════════════════════════════
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  1단계: VPC 생성\n";
    cout << "══════════════════════════════════════════════════\n";

    VPC vpc("vpc-0abc1234", "Production-VPC", "10.0.0.0/16", "ap-northeast-2");

    // Internet Gateway 연결
    vpc.attachIGW("igw-0def5678");

    cout << "  VPC 생성 완료: Production-VPC (10.0.0.0/16)\n";
    cout << "  IGW 연결 완료: igw-0def5678\n";


    // ═══════════════════════════════════════════════════════════════
    // 서브넷 생성
    // ═══════════════════════════════════════════════════════════════
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  2단계: 서브넷 생성\n";
    cout << "══════════════════════════════════════════════════\n";

    // Public 서브넷 (2개 AZ에 배치 - 고가용성)
    Subnet pubSubnet1("subnet-pub-1a", "Public-1a", "vpc-0abc1234",
                      "10.0.1.0/24", "ap-ne-2a", Subnet::Type::PUBLIC);
    Subnet pubSubnet2("subnet-pub-1c", "Public-1c", "vpc-0abc1234",
                      "10.0.2.0/24", "ap-ne-2c", Subnet::Type::PUBLIC);

    // Private 서브넷 (2개 AZ에 배치)
    Subnet privSubnet1("subnet-priv-1a", "Private-1a", "vpc-0abc1234",
                       "10.0.10.0/24", "ap-ne-2a", Subnet::Type::PRIVATE);
    Subnet privSubnet2("subnet-priv-1c", "Private-1c", "vpc-0abc1234",
                       "10.0.11.0/24", "ap-ne-2c", Subnet::Type::PRIVATE);

    // DB 전용 Private 서브넷
    Subnet dbSubnet1("subnet-db-1a", "DB-1a", "vpc-0abc1234",
                     "10.0.20.0/24", "ap-ne-2a", Subnet::Type::PRIVATE);
    Subnet dbSubnet2("subnet-db-1c", "DB-1c", "vpc-0abc1234",
                     "10.0.21.0/24", "ap-ne-2c", Subnet::Type::PRIVATE);

    // NAT Gateway (Public 서브넷에 배치)
    vpc.createNATGW("nat-0aaa1111", "subnet-pub-1a");

    // 라우팅 테이블 생성
    // Public 서브넷용: 0.0.0.0/0 → IGW
    RouteTable publicRT("rtb-pub-001", "Public-RT");
    publicRT.addRoute("10.0.0.0/16", "local", "VPC 내부");
    publicRT.addRoute("0.0.0.0/0", "igw-0def5678", "인터넷");

    // Private 서브넷용: 0.0.0.0/0 → NAT GW
    RouteTable privateRT("rtb-priv-001", "Private-RT");
    privateRT.addRoute("10.0.0.0/16", "local", "VPC 내부");
    privateRT.addRoute("0.0.0.0/0", "nat-0aaa1111", "NAT GW");

    // DB 서브넷용: 인터넷 라우팅 없음
    RouteTable dbRT("rtb-db-001", "DB-RT");
    dbRT.addRoute("10.0.0.0/16", "local", "VPC 내부만");

    // 서브넷에 라우팅 테이블 연결
    pubSubnet1.setRouteTable("rtb-pub-001");
    pubSubnet2.setRouteTable("rtb-pub-001");
    privSubnet1.setRouteTable("rtb-priv-001");
    privSubnet2.setRouteTable("rtb-priv-001");
    dbSubnet1.setRouteTable("rtb-db-001");
    dbSubnet2.setRouteTable("rtb-db-001");

    // VPC에 추가
    vpc.addSubnet(pubSubnet1);
    vpc.addSubnet(pubSubnet2);
    vpc.addSubnet(privSubnet1);
    vpc.addSubnet(privSubnet2);
    vpc.addSubnet(dbSubnet1);
    vpc.addSubnet(dbSubnet2);

    vpc.addRouteTable(publicRT);
    vpc.addRouteTable(privateRT);
    vpc.addRouteTable(dbRT);

    cout << "  서브넷 생성 완료:\n";
    cout << "  ┌──────────────┬──────────────────┬──────────┬──────────┐\n";
    cout << "  │ Name         │ CIDR             │ Type     │ AZ       │\n";
    cout << "  ├──────────────┼──────────────────┼──────────┼──────────┤\n";
    cout << "  │ Public-1a    │ 10.0.1.0/24      │ Public   │ ap-ne-2a │\n";
    cout << "  │ Public-1c    │ 10.0.2.0/24      │ Public   │ ap-ne-2c │\n";
    cout << "  │ Private-1a   │ 10.0.10.0/24     │ Private  │ ap-ne-2a │\n";
    cout << "  │ Private-1c   │ 10.0.11.0/24     │ Private  │ ap-ne-2c │\n";
    cout << "  │ DB-1a        │ 10.0.20.0/24     │ Private  │ ap-ne-2a │\n";
    cout << "  │ DB-1c        │ 10.0.21.0/24     │ Private  │ ap-ne-2c │\n";
    cout << "  └──────────────┴──────────────────┴──────────┴──────────┘\n";


    // ═══════════════════════════════════════════════════════════════
    // Security Group 생성
    // ═══════════════════════════════════════════════════════════════
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  3단계: Security Group 생성\n";
    cout << "══════════════════════════════════════════════════\n";

    // ALB Security Group
    SecurityGroup sgALB("sg-alb-001", "ALB-SG", "vpc-0abc1234");
    sgALB.addRule(SecurityGroup::Direction::INBOUND, SecurityGroup::Protocol::TCP,
                  80, 80, "0.0.0.0/0", "HTTP");
    sgALB.addRule(SecurityGroup::Direction::INBOUND, SecurityGroup::Protocol::TCP,
                  443, 443, "0.0.0.0/0", "HTTPS");
    sgALB.addRule(SecurityGroup::Direction::OUTBOUND, SecurityGroup::Protocol::ALL,
                  0, 65535, "0.0.0.0/0", "All outbound");

    // Web Server Security Group
    SecurityGroup sgWeb("sg-web-001", "Web-SG", "vpc-0abc1234");
    sgWeb.addRule(SecurityGroup::Direction::INBOUND, SecurityGroup::Protocol::TCP,
                  80, 80, "10.0.1.0/24", "ALB에서만");
    sgWeb.addRule(SecurityGroup::Direction::INBOUND, SecurityGroup::Protocol::TCP,
                  443, 443, "10.0.1.0/24", "ALB에서만");
    sgWeb.addRule(SecurityGroup::Direction::INBOUND, SecurityGroup::Protocol::TCP,
                  22, 22, "10.0.99.0/24", "Bastion에서만");
    sgWeb.addRule(SecurityGroup::Direction::OUTBOUND, SecurityGroup::Protocol::ALL,
                  0, 65535, "0.0.0.0/0", "All outbound");

    // DB Security Group
    SecurityGroup sgDB("sg-db-001", "DB-SG", "vpc-0abc1234");
    sgDB.addRule(SecurityGroup::Direction::INBOUND, SecurityGroup::Protocol::TCP,
                 3306, 3306, "10.0.10.0/24", "App서버(1a)");
    sgDB.addRule(SecurityGroup::Direction::INBOUND, SecurityGroup::Protocol::TCP,
                 3306, 3306, "10.0.11.0/24", "App서버(1c)");
    sgDB.addRule(SecurityGroup::Direction::INBOUND, SecurityGroup::Protocol::TCP,
                 22, 22, "10.0.99.0/24", "Bastion에서만");

    // Bastion Security Group
    SecurityGroup sgBastion("sg-bastion-001", "Bastion-SG", "vpc-0abc1234");
    sgBastion.addRule(SecurityGroup::Direction::INBOUND, SecurityGroup::Protocol::TCP,
                      22, 22, "203.0.113.0/24", "사무실 IP만");
    sgBastion.addRule(SecurityGroup::Direction::OUTBOUND, SecurityGroup::Protocol::ALL,
                      0, 65535, "10.0.0.0/16", "VPC 내부만");

    vpc.addSecurityGroup(sgALB);
    vpc.addSecurityGroup(sgWeb);
    vpc.addSecurityGroup(sgDB);
    vpc.addSecurityGroup(sgBastion);

    // 전체 SG 출력
    vpc.printAllSecurityGroups();


    // ═══════════════════════════════════════════════════════════════
    // 네트워크 토폴로지 출력
    // ═══════════════════════════════════════════════════════════════
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  4단계: 전체 네트워크 토폴로지\n";
    cout << "══════════════════════════════════════════════════\n";

    vpc.printTopology();
    vpc.printDiagram();


    // ═══════════════════════════════════════════════════════════════
    // 라우팅 테이블 출력
    // ═══════════════════════════════════════════════════════════════
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  5단계: 라우팅 테이블\n";
    cout << "══════════════════════════════════════════════════\n";

    vpc.printAllRouteTables();


    // ═══════════════════════════════════════════════════════════════
    // 트래픽 시뮬레이션
    // ═══════════════════════════════════════════════════════════════
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  6단계: 트래픽 시뮬레이션\n";
    cout << "══════════════════════════════════════════════════\n";

    cout << "\n  --- 시나리오 1: 인터넷 → ALB (HTTP) ---\n";
    vpc.simulateTraffic("203.0.113.50", "10.0.1.100", 80, "sg-alb-001");

    cout << "\n  --- 시나리오 2: ALB → Web Server ---\n";
    vpc.simulateTraffic("10.0.1.100", "10.0.10.50", 80, "sg-web-001");

    cout << "\n  --- 시나리오 3: Web Server → DB (MySQL) ---\n";
    vpc.simulateTraffic("10.0.10.50", "10.0.20.100", 3306, "sg-db-001");

    cout << "\n  --- 시나리오 4: 외부 → DB 직접 접근 (차단!) ---\n";
    vpc.simulateTraffic("203.0.113.50", "10.0.20.100", 3306, "sg-db-001");

    cout << "\n  --- 시나리오 5: Bastion → Web Server (SSH) ---\n";
    vpc.simulateTraffic("10.0.99.10", "10.0.10.50", 22, "sg-web-001");

    cout << "\n  --- 시나리오 6: 비인가 IP → Bastion (차단!) ---\n";
    vpc.simulateTraffic("192.168.1.100", "10.0.1.200", 22, "sg-bastion-001");

    cout << "\n  --- 시나리오 7: 사무실 IP → Bastion (허용) ---\n";
    vpc.simulateTraffic("203.0.113.50", "10.0.1.200", 22, "sg-bastion-001");


    // ═══════════════════════════════════════════════════════════════
    // 설계 요약
    // ═══════════════════════════════════════════════════════════════
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  클라우드 네트워크 설계 요약\n";
    cout << "══════════════════════════════════════════════════\n";

    cout << R"(
  ┌────────────────────────────────────────────────────────────┐
  │              클라우드 네트워크 설계 핵심                    │
  ├────────────────────────────────────────────────────────────┤
  │                                                            │
  │  1. VPC CIDR은 충분히 크게 (/16 권장)                     │
  │     → 나중에 변경 불가!                                   │
  │                                                            │
  │  2. 멀티 AZ 필수                                           │
  │     → 최소 2개 AZ에 서브넷 배치                           │
  │                                                            │
  │  3. Public/Private 분리                                    │
  │     → DB는 절대 Public에 놓지 마세요!                     │
  │                                                            │
  │  4. Security Group = 화이트리스트                          │
  │     → 필요한 것만 허용, 나머지 자동 차단                  │
  │                                                            │
  │  5. Bastion Host 또는 SSM                                  │
  │     → Private 인스턴스 접근 경로                          │
  │                                                            │
  │  6. VPC Flow Logs 활성화                                   │
  │     → 트래픽 감사와 트러블슈팅                            │
  │                                                            │
  │  7. 온프레미스 IP와 겹치지 않도록                          │
  │     → 하이브리드 확장 대비                                │
  │                                                            │
  │  ★ "클라우드도 결국 네트워크다"                           │
  │  ★ "기본기가 탄탄하면 어떤 클라우드든 쉽다"               │
  └────────────────────────────────────────────────────────────┘
)";


    cout << "\n■ 네트워크 학습 시리즈 완료!\n";
    cout << "  01_osi_model → 02_ip_addressing → 03_tcp_udp →\n";
    cout << "  04_dns_system → 05_http_protocol → 06_proxy_gateway →\n";
    cout << "  07_firewall_security → 08_routing_switching →\n";
    cout << "  09_network_monitoring → 10_industrial_network →\n";
    cout << "  11_cloud_network (현재)\n\n";

    return 0;
}
