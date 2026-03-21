/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  네트워크 학습 10단계: 산업 현장 네트워크 진단 도구
  ─ IP 검증, 서브넷 계산, 포트 스캐너, SNMP 시뮬, 설정 파서 ─

  이 파일은 실무에서 사용되는 네트워크 진단/관리 도구를 C++로 구현합니다.
  guide.md와 함께 학습하세요.

  ■ 컴파일 방법 (터미널에 입력)
    Windows (MinGW) : g++ -std=c++17 -Wall -o 10_diag.exe main.cpp -lws2_32
    Windows (MSVC)  : cl /EHsc /std:c++17 /W4 main.cpp ws2_32.lib
    Linux / Mac     : g++ -std=c++17 -Wall -o 10_diag main.cpp

  ■ 실행 방법
    Windows : .\10_diag.exe
    Linux   : ./10_diag

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <sstream>
#include <iomanip>
#include <cstdint>
#include <bitset>
#include <algorithm>
#include <regex>
#include <cstring>

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
    #define closesocket close
#endif

using namespace std;


// ─────────────────────────────────────────────────────────────────────────
// ■ 도구 1: IP 주소 검증기
// ─────────────────────────────────────────────────────────────────────────
//
//  ┌──────────┬───────────────────┬──────────────┐
//  │ 클래스   │ 범위              │ 기본 마스크  │
//  ├──────────┼───────────────────┼──────────────┤
//  │ A        │ 1~126.x.x.x      │ /8           │
//  │ B        │ 128~191.x.x.x    │ /16          │
//  │ C        │ 192~223.x.x.x    │ /24          │
//  │ D        │ 224~239.x.x.x    │ 멀티캐스트   │
//  └──────────┴───────────────────┴──────────────┘
//
//  사설 IP: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
//
// ─────────────────────────────────────────────────────────────────────────

class IPValidator {
public:
    struct IPInfo {
        bool valid;
        string ip;
        uint32_t numericIP;
        string ipClass;
        string type;
        string binaryStr;
    };

    static uint32_t toUint(const string& ip) {
        uint32_t r = 0; stringstream ss(ip); string o; int s = 24;
        while (getline(ss, o, '.')) { r |= (stoi(o) << s); s -= 8; }
        return r;
    }

    static string fromUint(uint32_t ip) {
        return to_string((ip>>24)&0xFF) + "." + to_string((ip>>16)&0xFF) + "." +
               to_string((ip>>8)&0xFF) + "." + to_string(ip&0xFF);
    }

    static bool isValidFormat(const string& ip) {
        regex pat(R"(^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$)");
        smatch m;
        if (!regex_match(ip, m, pat)) return false;
        for (int i = 1; i <= 4; i++) if (stoi(m[i]) > 255) return false;
        return true;
    }

    static IPInfo analyze(const string& ip) {
        IPInfo info{false, ip, 0, "N/A", "Invalid", ""};
        if (!(info.valid = isValidFormat(ip))) return info;
        info.numericIP = toUint(ip);
        info.binaryStr = bitset<32>(info.numericIP).to_string();
        int f = (info.numericIP >> 24) & 0xFF;

        if (f >= 1 && f <= 126)      info.ipClass = "A";
        else if (f >= 128 && f <= 191) info.ipClass = "B";
        else if (f >= 192 && f <= 223) info.ipClass = "C";
        else if (f >= 224 && f <= 239) info.ipClass = "D (Multicast)";
        else if (f >= 240)             info.ipClass = "E (Reserved)";
        else if (f == 127)             info.ipClass = "Loopback";

        if (f == 127)                    info.type = "Loopback";
        else if (f == 10)                info.type = "Private (10.0.0.0/8)";
        else if (f == 172 && ((info.numericIP>>16)&0xFF) >= 16 && ((info.numericIP>>16)&0xFF) <= 31)
                                         info.type = "Private (172.16.0.0/12)";
        else if (f == 192 && ((info.numericIP>>16)&0xFF) == 168)
                                         info.type = "Private (192.168.0.0/16)";
        else if (f == 169 && ((info.numericIP>>16)&0xFF) == 254)
                                         info.type = "Link-Local (APIPA)";
        else if (f >= 224)               info.type = "Multicast/Reserved";
        else                             info.type = "Public";
        return info;
    }

    static void printInfo(const IPInfo& info) {
        cout << "\n  ┌──────────────────────────────────────────────┐\n";
        cout << "  │  IP: " << setw(15) << left << info.ip;
        if (info.valid)
            cout << "  Class: " << setw(5) << info.ipClass << "  " << setw(6) << info.type;
        else
            cout << "  INVALID                   ";
        cout << right << "│\n";
        cout << "  └──────────────────────────────────────────────┘\n";
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 도구 2: 서브넷 계산기
// ─────────────────────────────────────────────────────────────────────────

class SubnetCalculator {
public:
    struct SubnetInfo {
        string networkAddress, broadcastAddress, subnetMask, wildcardMask;
        string firstHost, lastHost;
        int prefixLength;
        uint32_t totalHosts, usableHosts;
    };

    static uint32_t prefixToMask(int p) { return p == 0 ? 0 : ~((1u<<(32-p))-1); }

    static SubnetInfo calculate(const string& ip, int prefix) {
        SubnetInfo info; info.prefixLength = prefix;
        uint32_t ipN = IPValidator::toUint(ip);
        uint32_t mask = prefixToMask(prefix), wc = ~mask;
        uint32_t net = ipN & mask, bc = net | wc;
        info.networkAddress = IPValidator::fromUint(net);
        info.broadcastAddress = IPValidator::fromUint(bc);
        info.subnetMask = IPValidator::fromUint(mask);
        info.wildcardMask = IPValidator::fromUint(wc);
        info.firstHost = IPValidator::fromUint(net + 1);
        info.lastHost = IPValidator::fromUint(bc - 1);
        info.totalHosts = wc + 1;
        info.usableHosts = wc > 1 ? wc - 1 : 0;
        return info;
    }

    static void printInfo(const SubnetInfo& info) {
        cout << "\n  ┌────────────────────────────────────────────────────┐\n";
        cout << "  │  네트워크   : " << setw(37) << left << info.networkAddress << right << "│\n";
        cout << "  │  브로드캐스트: " << setw(36) << left << info.broadcastAddress << right << "│\n";
        cout << "  │  마스크     : " << setw(37) << left
             << (info.subnetMask + " (/" + to_string(info.prefixLength) + ")") << right << "│\n";
        cout << "  │  호스트 범위: " << setw(36) << left
             << (info.firstHost + " ~ " + info.lastHost) << right << "│\n";
        cout << "  │  사용 가능  : " << setw(37) << left << info.usableHosts << right << "│\n";
        cout << "  └────────────────────────────────────────────────────┘\n";
    }

    static void printSubnetPlan(const vector<pair<string, int>>& vlans) {
        cout << "\n  ═══ VLAN 서브넷 계획표 ═══\n";
        cout << "  ┌──────┬────────────────┬──────────────────┬───────────┐\n";
        cout << "  │ VLAN │ 이름           │ 서브넷           │ 호스트수  │\n";
        cout << "  ├──────┼────────────────┼──────────────────┼───────────┤\n";
        for (const auto& [name, vid] : vlans) {
            string subnet = "10.1." + to_string(vid) + ".0/24";
            cout << "  │ " << setw(4) << vid << " │ " << setw(14) << left << name
                 << " │ " << setw(16) << subnet << " │ " << setw(9) << 254 << right << " │\n";
        }
        cout << "  └──────┴────────────────┴──────────────────┴───────────┘\n";
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 도구 3: 포트 스캐너
// ─────────────────────────────────────────────────────────────────────────

class DiagPortScanner {
    static string serviceName(int port) {
        static const map<int, string> s = {
            {21,"FTP"},{22,"SSH"},{23,"Telnet"},{25,"SMTP"},{53,"DNS"},{80,"HTTP"},
            {110,"POP3"},{143,"IMAP"},{443,"HTTPS"},{3306,"MySQL"},{5432,"PostgreSQL"},
            {6379,"Redis"},{8080,"HTTP-Proxy"},{3389,"RDP"},{1433,"MSSQL"},{27017,"MongoDB"},
        };
        auto it = s.find(port); return it != s.end() ? it->second : "-";
    }
public:
    static bool testPort(const string& host, int port, int timeoutMs = 500) {
        SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (sock == INVALID_SOCKET) return false;
#ifdef _WIN32
        unsigned long mode = 1; ioctlsocket(sock, FIONBIO, &mode);
#else
        fcntl(sock, F_SETFL, fcntl(sock, F_GETFL, 0) | O_NONBLOCK);
#endif
        sockaddr_in addr{}; addr.sin_family = AF_INET;
        addr.sin_port = htons((unsigned short)port);
        inet_pton(AF_INET, host.c_str(), &addr.sin_addr);
        connect(sock, (sockaddr*)&addr, sizeof(addr));
        fd_set ws; FD_ZERO(&ws); FD_SET(sock, &ws);
        timeval tv{timeoutMs/1000, (timeoutMs%1000)*1000};
        int r = select((int)sock+1, nullptr, &ws, nullptr, &tv);
        bool open = false;
        if (r > 0) { int e=0;
#ifdef _WIN32
            int l=sizeof(e); getsockopt(sock, SOL_SOCKET, SO_ERROR, (char*)&e, &l);
#else
            socklen_t l=sizeof(e); getsockopt(sock, SOL_SOCKET, SO_ERROR, &e, &l);
#endif
            open = (e==0);
        }
        closesocket(sock); return open;
    }

    static void scanCommonPorts(const string& host) {
        vector<int> ports = {21,22,23,25,53,80,110,143,443,1433,3306,3389,5432,6379,8080,27017};
        cout << "\n  포트 스캔: " << host << "\n";
        cout << "  ┌────────┬─────────┬───────────────┐\n";
        cout << "  │  Port  │ Status  │ Service       │\n";
        cout << "  ├────────┼─────────┼───────────────┤\n";
        int cnt = 0;
        for (int p : ports) {
            if (testPort(host, p, 300)) {
                cout << "  │  " << setw(5) << p << " │ OPEN    │ " << setw(13) << left << serviceName(p) << right << " │\n";
                cnt++;
            }
        }
        if (cnt == 0) cout << "  │  (열린 포트 없음)            │\n";
        cout << "  └────────┴─────────┴───────────────┘\n";
        cout << "  " << cnt << "개 열림 / " << ports.size() << "개 테스트\n";
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 도구 4: SNMP GET 시뮬레이션
// ─────────────────────────────────────────────────────────────────────────

class SNMPGetSimulator {
    struct Device { string hostname, sysDescr; int uptime, cpuUsage, memTotal, memUsed; };
    map<string, Device> devices_;
public:
    SNMPGetSimulator() {
        devices_["10.1.99.1"]  = {"core-switch-01", "Cisco IOS XE, C9300", 8640000, 35, 8192, 4096};
        devices_["10.1.99.2"]  = {"fw-fortigate-01", "FortiGate-60F v7.4",  2592000, 42, 4096, 2048};
        devices_["10.1.99.10"] = {"server-web-01",   "Linux 5.15.0 Ubuntu", 604800,  65, 32768, 24576};
    }

    void printDeviceSummary() {
        cout << "\n  ┌─────────────────┬──────────────────┬──────────┬────────┬──────────┐\n";
        cout << "  │ IP              │ Hostname         │ Uptime   │ CPU    │ Mem      │\n";
        cout << "  ├─────────────────┼──────────────────┼──────────┼────────┼──────────┤\n";
        for (const auto& [ip, d] : devices_) {
            cout << "  │ " << setw(15) << left << ip
                 << " │ " << setw(16) << d.hostname
                 << " │ " << setw(4) << (d.uptime/86400) << "일"
                 << "   │ " << setw(3) << d.cpuUsage << "%"
                 << "   │ " << setw(3) << (d.memUsed*100/d.memTotal) << "%"
                 << "     " << right << "│\n";
        }
        cout << "  └─────────────────┴──────────────────┴──────────┴────────┴──────────┘\n";
    }

    void snmpGet(const string& ip, const string& oid) {
        auto it = devices_.find(ip);
        if (it == devices_.end()) { cout << "  [SNMP] " << ip << ": Timeout\n"; return; }
        const auto& d = it->second;
        if (oid == "sysName") cout << "  sysName = \"" << d.hostname << "\"\n";
        else if (oid == "sysDescr") cout << "  sysDescr = \"" << d.sysDescr << "\"\n";
        else if (oid == "sysUpTime") cout << "  sysUpTime = " << d.uptime << " (" << d.uptime/86400 << "일)\n";
        else if (oid == "cpu") cout << "  cpuUsage = " << d.cpuUsage << "%\n";
        else if (oid == "memory") cout << "  memUsed = " << d.memUsed << "/" << d.memTotal << " MB (" << d.memUsed*100/d.memTotal << "%)\n";
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 도구 5: 네트워크 구성 파서
// ─────────────────────────────────────────────────────────────────────────

class NetworkConfigParser {
public:
    struct InterfaceConfig {
        string name, ipAddress, description;
        int prefixLen, vlan;
        bool shutdown;
    };
    struct DeviceConfig {
        string hostname, deviceType, defaultGateway, ntpServer;
        vector<InterfaceConfig> interfaces;
        vector<string> dnsServers;
    };

    static DeviceConfig parse(const string& text) {
        DeviceConfig config;
        istringstream stream(text); string line;
        InterfaceConfig curIface{}; bool inIf = false;

        while (getline(stream, line)) {
            size_t c = line.find('#'); if (c != string::npos) line = line.substr(0, c);
            if (line.find_first_not_of(" \t") == string::npos) continue;
            size_t eq = line.find('='); if (eq == string::npos) continue;
            string key = line.substr(0, eq), val = line.substr(eq+1);
            auto trim = [](string& s) { s.erase(0, s.find_first_not_of(" \t")); s.erase(s.find_last_not_of(" \t")+1); };
            trim(key); trim(val);

            if (key == "hostname") config.hostname = val;
            else if (key == "type") config.deviceType = val;
            else if (key == "dns") config.dnsServers.push_back(val);
            else if (key == "gateway") config.defaultGateway = val;
            else if (key == "ntp") config.ntpServer = val;
            else if (key == "interface") {
                if (inIf) config.interfaces.push_back(curIface);
                curIface = {}; curIface.name = val; inIf = true;
            }
            else if (inIf) {
                if (key == "ip") { size_t sl = val.find('/'); if (sl != string::npos) { curIface.ipAddress = val.substr(0,sl); curIface.prefixLen = stoi(val.substr(sl+1)); }}
                else if (key == "vlan") curIface.vlan = stoi(val);
                else if (key == "description") curIface.description = val;
                else if (key == "shutdown") curIface.shutdown = (val == "true" || val == "yes");
            }
        }
        if (inIf) config.interfaces.push_back(curIface);
        return config;
    }

    static void printConfig(const DeviceConfig& config) {
        cout << "\n  ┌────────────────────────────────────────────────────────┐\n";
        cout << "  │  호스트: " << setw(14) << left << config.hostname
             << "  유형: " << setw(25) << config.deviceType << right << "│\n";
        cout << "  │  GW: " << setw(17) << left << config.defaultGateway
             << "  NTP: " << setw(26) << config.ntpServer << right << "│\n";
        cout << "  ├────────────────────────────────────────────────────────┤\n";
        for (const auto& i : config.interfaces) {
            cout << "  │  " << setw(8) << left << i.name << " "
                 << setw(18) << (i.ipAddress + "/" + to_string(i.prefixLen))
                 << " V" << setw(4) << i.vlan << " "
                 << setw(4) << (i.shutdown ? "DOWN" : "UP") << " "
                 << setw(12) << i.description << right << "│\n";
        }
        cout << "  └────────────────────────────────────────────────────────┘\n";

        // 검증
        vector<string> warnings;
        if (config.hostname.empty()) warnings.push_back("[ERROR] 호스트명 없음");
        if (config.dnsServers.empty()) warnings.push_back("[WARN] DNS 미설정");
        if (config.ntpServer.empty()) warnings.push_back("[WARN] NTP 미설정");
        for (const auto& i : config.interfaces)
            if (!i.shutdown && i.ipAddress.empty()) warnings.push_back("[WARN] " + i.name + ": IP 없음");
        if (!warnings.empty()) {
            cout << "  검증 결과:\n";
            for (const auto& w : warnings) cout << "  " << w << "\n";
        } else cout << "  검증: 모든 항목 통과\n";
    }
};


// ─────────────────────────────────────────────────────────────────────────
// ■ 메인 함수
// ─────────────────────────────────────────────────────────────────────────
int main() {
    cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■\n";
    cout << "■  네트워크 학습 10: 산업 현장 네트워크 진단 도구        ■\n";
    cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■\n";

#ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2,2), &wsaData) != 0) { cout << "  Winsock 실패\n"; return 1; }
#endif

    // 도구 1: IP 검증기
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  도구 1: IP 주소 검증기\n";
    cout << "══════════════════════════════════════════════════\n";

    for (const auto& ip : {"192.168.1.100", "10.0.0.1", "172.16.0.1", "8.8.8.8", "127.0.0.1",
                            "224.0.0.1", "169.254.1.1", "256.1.2.3", "192.168.1"}) {
        IPValidator::printInfo(IPValidator::analyze(ip));
    }

    // 도구 2: 서브넷 계산기
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  도구 2: 서브넷 계산기\n";
    cout << "══════════════════════════════════════════════════\n";

    struct { string ip; int p; } subs[] = {
        {"192.168.1.0",24}, {"10.0.0.0",8}, {"172.16.0.0",16}, {"192.168.1.0",28}, {"192.168.1.0",30},
    };
    for (const auto& s : subs) SubnetCalculator::printInfo(SubnetCalculator::calculate(s.ip, s.p));

    SubnetCalculator::printSubnetPlan({
        {"Server",10}, {"Office",20}, {"Dev",30}, {"IoT",40},
        {"Guest",50}, {"VoIP",60}, {"Mgmt",99}, {"DMZ",200}
    });

    // 도구 3: 포트 스캐너
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  도구 3: 포트 스캐너\n";
    cout << "══════════════════════════════════════════════════\n";
    cout << "  ★ 자신의 시스템만 스캔하세요!\n";
    DiagPortScanner::scanCommonPorts("127.0.0.1");

    // 도구 4: SNMP 시뮬레이션
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  도구 4: SNMP GET 시뮬레이션\n";
    cout << "══════════════════════════════════════════════════\n";

    SNMPGetSimulator snmp;
    snmp.printDeviceSummary();
    for (const auto& ip : {"10.1.99.1", "10.1.99.2", "10.1.99.10"}) {
        cout << "\n  === " << ip << " ===\n";
        snmp.snmpGet(ip, "sysName"); snmp.snmpGet(ip, "sysDescr");
        snmp.snmpGet(ip, "sysUpTime"); snmp.snmpGet(ip, "cpu"); snmp.snmpGet(ip, "memory");
    }
    cout << "\n  === 10.1.99.100 ===\n";
    snmp.snmpGet("10.1.99.100", "sysName");

    // 도구 5: 설정 파서
    cout << "\n\n══════════════════════════════════════════════════\n";
    cout << "  도구 5: 네트워크 구성 파서\n";
    cout << "══════════════════════════════════════════════════\n";

    string configText = R"(
# Core Switch Configuration
hostname = core-switch-01
type = L3 Switch
dns = 8.8.8.8
dns = 8.8.4.4
gateway = 10.1.99.1
ntp = time.google.com

interface = Gi1/0/1
ip = 10.1.10.1/24
vlan = 10
description = Server-VLAN
shutdown = false

interface = Gi1/0/2
ip = 10.1.20.1/24
vlan = 20
description = Office-VLAN
shutdown = false

interface = Gi1/0/3
ip = 10.1.30.1/24
vlan = 30
description = Dev-VLAN
shutdown = false

interface = Gi1/0/4
ip = 10.1.99.1/24
vlan = 99
description = Mgmt-VLAN
shutdown = false

interface = Gi1/0/5
ip = 0.0.0.0/0
vlan = 999
description = Unused
shutdown = true
)";

    auto config = NetworkConfigParser::parse(configText);
    NetworkConfigParser::printConfig(config);

#ifdef _WIN32
    WSACleanup();
#endif
    cout << "\n\n■ 학습 완료! 다음 단계: 11_cloud_network\n\n";
    return 0;
}
