/*
=============================================================================
  C++ 학습 34단계: 네트워크 계층별 심화 (L2 ~ L7)
=============================================================================
  [학습 목표]
  1. OSI 7계층 / TCP/IP 4계층 정확히 구분
  2. 각 계층의 헤더 / 책임 / 단위(PDU) 이해
  3. L4(TCP/UDP) 소켓을 실제로 작성 (cross-platform)
  4. 비동기 I/O 모델 (select / poll / epoll / IOCP)
  5. TLS 핸드셰이크 흐름
  6. 각 계층별 메모리 함정 (버퍼링, MTU, partial recv, etc.)

  [기존 ch15와 차이]
    ch15: 의사코드 + 다이어그램 위주.
    ch34: 실제 컴파일/실행 가능한 cross-platform 소켓 코드 + 패킷 헤더 파싱.

  [컴파일]
    Linux/Mac:  g++ -std=c++17 -Wall -Wextra -O2 -pthread -o 34_net main.cpp
    Windows:    cl /EHsc /std:c++17 /W4 main.cpp ws2_32.lib
                또는 g++ -std=c++17 -O2 -o 34_net main.cpp -lws2_32
=============================================================================
*/

#include <iostream>
#include <string>
#include <vector>
#include <array>
#include <cstdint>
#include <cstring>
#include <thread>
#include <atomic>
#include <chrono>
#include <stdexcept>
#include <memory>
#include <algorithm>

// 플랫폼별 소켓 헤더
#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib, "ws2_32.lib")
    using socket_t  = SOCKET;
    using sock_len  = int;
    constexpr socket_t INVALID_SOCK = INVALID_SOCKET;
    inline int sock_close(socket_t s) { return closesocket(s); }
    inline int sock_errno() { return WSAGetLastError(); }
#else
    #include <sys/types.h>
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <unistd.h>
    #include <fcntl.h>
    #include <errno.h>
    #include <netdb.h>
    #include <poll.h>
    using socket_t = int;
    using sock_len = socklen_t;
    constexpr socket_t INVALID_SOCK = -1;
    inline int sock_close(socket_t s) { return close(s); }
    inline int sock_errno() { return errno; }
#endif

using namespace std;

void lesson1_layers_overview();
void lesson2_l2_ethernet();
void lesson3_l3_ip();
void lesson4_l4_tcp_udp();
void lesson5_tcp_echo();
void lesson6_async_io_models();
void lesson7_tls_handshake();
void lesson8_memory_pitfalls();

// ─── Winsock RAII 가드 (Windows 전용 - WSAStartup/Cleanup 자동) ───
struct WsaInit {
#ifdef _WIN32
    WsaInit() {
        WSADATA wsa;
        if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
            throw runtime_error("WSAStartup failed");
        }
    }
    ~WsaInit() { WSACleanup(); }
#else
    WsaInit() = default;
#endif
    WsaInit(const WsaInit&) = delete;
    WsaInit& operator=(const WsaInit&) = delete;
};

// ─── 소켓 RAII 핸들 (자동 close 보장) ───
class Socket {
public:
    Socket() = default;
    explicit Socket(socket_t s) : s_(s) {}
    ~Socket() { close(); }

    Socket(const Socket&) = delete;
    Socket& operator=(const Socket&) = delete;

    Socket(Socket&& o) noexcept : s_(o.s_) { o.s_ = INVALID_SOCK; }
    Socket& operator=(Socket&& o) noexcept {
        if (this != &o) { close(); s_ = o.s_; o.s_ = INVALID_SOCK; }
        return *this;
    }

    void close() {
        if (s_ != INVALID_SOCK) { sock_close(s_); s_ = INVALID_SOCK; }
    }

    socket_t get() const { return s_; }
    bool valid() const   { return s_ != INVALID_SOCK; }
    socket_t release()   { auto t = s_; s_ = INVALID_SOCK; return t; }

private:
    socket_t s_ = INVALID_SOCK;
};


/*
=============================================================================
  레슨별 출력 흐름 가이드
=============================================================================
  lesson1 (계층 모델): OSI vs TCP/IP 표 + 캡슐화 다이어그램

  lesson2 (L2 Ethernet/ARP):
    Dst MAC = ff:ff:ff:ff:ff:ff (브로드캐스트)
    Src MAC = aa:bb:cc:dd:ee:ff
    Type    = 0x806 (ARP)
    ARP Op = 1 (request)
    Sender = 192.168.1.100, Target = 192.168.1.1

  lesson3 (L3 IP):
    버전 = 4, IHL = 5 (= 20 bytes)
    TTL = 64, Protocol = 17 (UDP)
    Src IP = 192.168.1.100, Dst IP = 8.8.8.8
    Checksum verify = 0x0 (OK)

  lesson4 (L4 TCP/UDP):
    UDP 헤더: 53 → 54321, len=20
    TCP SYN: 54321 → 80, seq=1000

  lesson5 (TCP echo 서버+클라이언트, in-process):
    서버 시작: 127.0.0.1:<random_port>
    연결 성공
    "hello" → "ECHO: hello"
    "world" → "ECHO: world"
    "C++"   → "ECHO: C++"
    "QUIT"  → 서버 종료

  lesson6 (async I/O): 모델 비교표 출력. Windows에선 select 데모(타임아웃 0)

  lesson7 (TLS 1.3): 핸드셰이크 다이어그램, 보안 주의사항

  lesson8 (메모리 함정): 8가지 함정 카탈로그
=============================================================================
*/

int main() {
    cout << "================================================\n";
    cout << "  C++ 34단계 : 네트워크 계층별 심화 (L2~L7)\n";
    cout << "================================================\n\n";

    WsaInit wsa;

    lesson1_layers_overview();
    lesson2_l2_ethernet();
    lesson3_l3_ip();
    lesson4_l4_tcp_udp();
    lesson5_tcp_echo();
    lesson6_async_io_models();
    lesson7_tls_handshake();
    lesson8_memory_pitfalls();

    cout << "\n34단계 학습 완료!\n";
    return 0;
}


// =============================================================================
//  레슨 1 — 계층 모델 정확한 비교
// =============================================================================

void lesson1_layers_overview() {
    cout << "[레슨 1] 계층 모델 비교\n";
    cout << R"(
  ┌─ OSI 7계층 vs TCP/IP 4계층 ───────────────────────────┐
  │ OSI                  │ TCP/IP    │ 단위(PDU)│ 예시      │
  │──────────────────────┼───────────┼─────────┼───────────│
  │ 7. 응용 (Application)│           │         │ HTTP/FTP  │
  │ 6. 표현 (Presentation│ 응용      │ Message │ TLS/JPEG  │
  │ 5. 세션 (Session)    │           │         │ NetBIOS   │
  │──────────────────────┼───────────┼─────────┼───────────│
  │ 4. 전송 (Transport)  │ 전송      │ Segment │ TCP/UDP   │
  │──────────────────────┼───────────┼─────────┼───────────│
  │ 3. 네트워크 (Network)│ 인터넷    │ Packet  │ IP/ICMP   │
  │──────────────────────┼───────────┼─────────┼───────────│
  │ 2. 데이터링크        │           │ Frame   │ Ethernet  │
  │ 1. 물리               │ 링크      │ Bit     │ 케이블/Wi-Fi│
  └──────────────────────┴───────────┴─────────┴───────────┘

  ■ 캡슐화 (Encapsulation) — 데이터가 아래로 내려갈 때 헤더가 추가됨
    [Application Data]
    └─ TCP: [TCP Header | Application Data]                     <- Segment
    └─ IP : [IP Header | TCP Header | Application Data]         <- Packet
    └─ Eth: [Eth Header | IP Header | TCP Header | App Data | FCS] <- Frame

  ■ MTU (Maximum Transmission Unit)
    Ethernet 일반: 1500 bytes (페이로드)
    Ethernet 점보: 9000 bytes (LAN 환경)
    PPPoE        : 1492 (8 bytes 오버헤드)
    인터넷 안전값 : 1280 (IPv6 최소), 576 (IPv4 최소)
    초과 시 IP 단편화 → 성능/순서 문제. 실무는 PMTUD로 동적 조정.

  ■ 흔한 오해
    "포트는 OS가 정한다" → 클라이언트 포트는 OS가 동적 할당, 서버는 명시 바인딩
    "TCP는 데이터 무결성 보장" → 비트 오류는 16비트 체크섬으로만 검출 (약함)
                                  실제 무결성은 응용 계층 / TLS가 보장
    "IP는 경로 보장" → IP는 best-effort. 패킷 분실/순서뒤바뀜/중복 모두 가능
                       → 그래서 TCP가 위에 있음
)";
    cout << endl;
}


// =============================================================================
//  레슨 2 — L2: 이더넷 프레임
// =============================================================================
//
//  [메모리 레이아웃 - Big Endian으로 와이어 전송]
//    ┌────────┬────────┬─────┬──────────────┬─────┐
//    │ Dst MAC│ Src MAC│Type │ Payload(46~1500)│ FCS │
//    │  6 byte│  6 byte│2 byte│              │  4byte│
//    └────────┴────────┴─────┴──────────────┴─────┘
//    Type:  0x0800=IPv4, 0x0806=ARP, 0x86DD=IPv6, 0x8100=VLAN
//
//  [메모리 함정]
//    - struct로 매핑할 때 패딩 주의: __attribute__((packed)) 필수
//    - sizeof(EthernetHeader) = 14 (반드시), 16 아님
//    - alignof도 1로 강제하지 않으면 unaligned access UB
// =============================================================================

#pragma pack(push, 1)
struct EthernetHeader {
    uint8_t  dst_mac[6];
    uint8_t  src_mac[6];
    uint16_t ether_type;   // 네트워크 바이트 오더 (big-endian)
};
struct ArpPacket {
    uint16_t hw_type;      // 1 = Ethernet
    uint16_t proto_type;   // 0x0800 = IPv4
    uint8_t  hw_size;      // 6
    uint8_t  proto_size;   // 4
    uint16_t op;           // 1=request, 2=reply
    uint8_t  sender_mac[6];
    uint8_t  sender_ip[4];
    uint8_t  target_mac[6];
    uint8_t  target_ip[4];
};
#pragma pack(pop)

static_assert(sizeof(EthernetHeader) == 14, "Ethernet header must be 14 bytes");
static_assert(sizeof(ArpPacket) == 28, "ARP packet must be 28 bytes");

void print_mac(const uint8_t mac[6]) {
    char buf[18];
    snprintf(buf, sizeof(buf), "%02x:%02x:%02x:%02x:%02x:%02x",
             mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    cout << buf;
}

void lesson2_l2_ethernet() {
    cout << "[레슨 2] L2 — 이더넷 프레임 / ARP\n\n";

    // 가짜 ARP 요청 프레임 생성 (실제 raw socket은 root/admin 필요 - 여기선 메모리 시뮬)
    uint8_t broadcast[6] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
    uint8_t my_mac[6]    = {0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF};

    EthernetHeader eth{};
    memcpy(eth.dst_mac, broadcast, 6);
    memcpy(eth.src_mac, my_mac, 6);
    eth.ether_type = htons(0x0806);    // ARP

    ArpPacket arp{};
    arp.hw_type    = htons(1);
    arp.proto_type = htons(0x0800);
    arp.hw_size    = 6;
    arp.proto_size = 4;
    arp.op         = htons(1);          // request
    memcpy(arp.sender_mac, my_mac, 6);
    arp.sender_ip[0] = 192; arp.sender_ip[1] = 168;
    arp.sender_ip[2] = 1;   arp.sender_ip[3] = 100;
    arp.target_ip[0] = 192; arp.target_ip[1] = 168;
    arp.target_ip[2] = 1;   arp.target_ip[3] = 1;

    cout << "  Ethernet 헤더\n";
    cout << "    Dst MAC = "; print_mac(eth.dst_mac); cout << "\n";
    cout << "    Src MAC = "; print_mac(eth.src_mac); cout << "\n";
    cout << "    Type    = 0x" << hex << ntohs(eth.ether_type) << dec << " (ARP)\n";

    cout << "\n  ARP 요청\n";
    cout << "    Op      = " << ntohs(arp.op) << " (1=request)\n";
    cout << "    Sender  = ";
    for (int i = 0; i < 4; ++i) cout << (int)arp.sender_ip[i] << (i<3?".":"");
    cout << " ("; print_mac(arp.sender_mac); cout << ")\n";
    cout << "    Target  = ";
    for (int i = 0; i < 4; ++i) cout << (int)arp.target_ip[i] << (i<3?".":"");
    cout << " (?)\n";

    cout << R"(
  ┌─ L2 메모리 / 실무 함정 ───────────────────────────────┐
  │ ✦ struct에 #pragma pack(1) 또는 packed 안 붙이면      │
  │    컴파일러가 4바이트 정렬 → 14가 16이 됨 → 와이어 깨짐│
  │ ✦ 멀티바이트 필드는 반드시 ntohs/ntohl 변환           │
  │   (호스트가 little-endian인데 와이어는 big-endian)    │
  │ ✦ raw socket은 root/Administrator 필요. 일반 앱은 사용X│
  │ ✦ ARP 캐시 포이즈닝 → 보안 취약. switch에서 DAI 활성화│
  │ ✦ VLAN 태그(802.1Q) 4바이트 추가 → MTU 1500 → 1496   │
  │ ✦ 점보 프레임은 모든 경로 장비가 지원해야 함          │
  └───────────────────────────────────────────────────────┘
)";
    cout << endl;
}


// =============================================================================
//  레슨 3 — L3: IP 헤더
// =============================================================================
//
//  IPv4 헤더 (20~60 byte, options 포함 시 가변)
//    0       4       8              16              24            31
//    +-------+-------+---------------+-------------------------------+
//    |Version|  IHL  |Type of Service|         Total Length          |
//    +-------+-------+---------------+-------+-----------------------+
//    |       Identification          | Flags |   Fragment Offset     |
//    +---------------+---------------+-------+-----------------------+
//    | Time to Live  |   Protocol    |       Header Checksum         |
//    +---------------+---------------+-------------------------------+
//    |                       Source IP Address                       |
//    +---------------------------------------------------------------+
//    |                    Destination IP Address                     |
//    +---------------------------------------------------------------+
//    |                    Options                    |    Padding    |
//    +---------------------------------------------------------------+
//
//  [Protocol 필드]
//    1 = ICMP, 6 = TCP, 17 = UDP, 41 = IPv6, 50 = ESP, 89 = OSPF
//
//  [메모리 함정]
//    - IHL은 4바이트 단위 (5 = 20바이트)
//    - 체크섬은 헤더만 (페이로드 X) - 16비트 1의 보수
//    - Total Length는 헤더+페이로드 합계 (max 65535)
//    - Identification + Flags + Fragment Offset → 단편화 재조립용
// =============================================================================

#pragma pack(push, 1)
struct Ipv4Header {
    uint8_t  ver_ihl;         // 상위 4비트=ver(4), 하위 4비트=IHL
    uint8_t  tos;
    uint16_t total_len;
    uint16_t id;
    uint16_t flags_frag;      // 상위 3비트=flags, 하위 13비트=offset
    uint8_t  ttl;
    uint8_t  protocol;
    uint16_t checksum;
    uint32_t src_ip;
    uint32_t dst_ip;
    // options 가변
};
#pragma pack(pop)

static_assert(sizeof(Ipv4Header) == 20, "IPv4 header without options must be 20 bytes");

// 16비트 1의 보수 체크섬 - IP/TCP/UDP 공통
uint16_t internet_checksum(const void* data, size_t len) {
    const uint16_t* words = static_cast<const uint16_t*>(data);
    uint32_t sum = 0;
    while (len >= 2) {
        sum += *words++;
        len -= 2;
    }
    if (len) {                                          // 홀수 바이트 패딩
        sum += *reinterpret_cast<const uint8_t*>(words);
    }
    while (sum >> 16) sum = (sum & 0xFFFF) + (sum >> 16);
    return (uint16_t)~sum;
}

void lesson3_l3_ip() {
    cout << "[레슨 3] L3 — IP 헤더 파싱 / 체크섬\n\n";

    // 가짜 IP 헤더 만들기
    Ipv4Header ip{};
    ip.ver_ihl    = (4 << 4) | 5;        // version=4, IHL=5(=20byte)
    ip.tos        = 0;
    ip.total_len  = htons(20 + 8);       // IP 헤더 + UDP 헤더만
    ip.id         = htons(0x1234);
    ip.flags_frag = htons(0x4000);       // Don't Fragment
    ip.ttl        = 64;
    ip.protocol   = 17;                  // UDP
    ip.checksum   = 0;
    ip.src_ip     = htonl((192 << 24) | (168 << 16) | (1 << 8) | 100);
    ip.dst_ip     = htonl((8 << 24) | (8 << 16) | (8 << 8) | 8);
    ip.checksum   = internet_checksum(&ip, sizeof(ip));

    cout << "  버전     = " << (ip.ver_ihl >> 4) << "\n";
    cout << "  IHL      = " << (ip.ver_ihl & 0x0F) << " (= "
                            << ((ip.ver_ihl & 0x0F) * 4) << " bytes)\n";
    cout << "  TTL      = " << (int)ip.ttl << "\n";
    cout << "  Protocol = " << (int)ip.protocol << " (UDP)\n";
    cout << "  Total Len= " << ntohs(ip.total_len) << "\n";

    char buf[INET_ADDRSTRLEN];
    in_addr src{}; src.s_addr = ip.src_ip;
    in_addr dst{}; dst.s_addr = ip.dst_ip;
    inet_ntop(AF_INET, &src, buf, sizeof(buf)); cout << "  Src IP   = " << buf << "\n";
    inet_ntop(AF_INET, &dst, buf, sizeof(buf)); cout << "  Dst IP   = " << buf << "\n";
    cout << "  Checksum = 0x" << hex << ip.checksum << dec << "\n";

    // 검증: 체크섬 포함하여 다시 계산하면 0이 나와야 함
    uint16_t verify = internet_checksum(&ip, sizeof(ip));
    cout << "  Checksum verify = 0x" << hex << verify << dec
         << " " << (verify == 0 ? "(OK)" : "(FAIL)") << "\n";

    cout << R"(
  ┌─ L3 함정 ─────────────────────────────────────────────┐
  │ ✦ TTL=0이면 라우터가 ICMP Time Exceeded 응답         │
  │   → traceroute는 TTL을 1,2,3.. 늘려가며 활용          │
  │ ✦ Don't Fragment + 큰 패킷 → 라우터 drop, 응답 ICMP   │
  │   PMTUD: 그 응답을 받아 size 줄임. 방화벽이 막으면     │
  │   "PMTUD black hole" → 일부 사이트만 안 됨            │
  │ ✦ 단편화 공격: 작은 조각 다수 → 재조립 메모리 폭증    │
  │   현대 OS는 큐 사이즈 제한 + 타임아웃                 │
  │ ✦ IP 옵션은 거의 안 씀 (라우터가 slow-path로 처리)    │
  │ ✦ IPv6는 헤더 고정 40byte + 확장 헤더 체인            │
  │   체크섬 필드 없음 (TCP/UDP 의사헤더에서만)           │
  └───────────────────────────────────────────────────────┘
)";
    cout << endl;
}


// =============================================================================
//  레슨 4 — L4: TCP / UDP
// =============================================================================
//
//  [TCP 3-way handshake]
//    Client                          Server
//      │ ── SYN, seq=x ───────────▶ │      LISTEN
//      │                            │      → SYN_RCVD (반쪽열림 큐)
//      │ ◀── SYN+ACK, seq=y, ack=x+1 │
//      │ ── ACK, ack=y+1 ─────────▶ │      ESTABLISHED
//
//    SYN flood 공격: 클라가 ACK 안 보내면 SYN_RCVD가 누적 → 서버 OOM
//    방어: SYN cookie - 서버가 상태 저장 안 하고 ACK seq에 검증값 인코딩
//
//  [TCP 4-way teardown]
//    A → FIN ──────────▶ B (CLOSE_WAIT)
//    A ◀── ACK ────────  B
//    A ◀── FIN ────────  B
//    A → ACK ──────────▶ B
//    A: TIME_WAIT (2*MSL ≈ 2분) ← 짝 ACK 분실 대비
//    실무: TIME_WAIT 누적이 포트 고갈 → SO_REUSEADDR / SO_REUSEPORT
//
//  [TCP 슬라이딩 윈도우]
//    송신측이 수신측 윈도우 크기만큼 ACK 없이 보낼 수 있음
//    혼잡 제어: cwnd (slow start, congestion avoidance, fast recovery)
//    BBR(구글), CUBIC(리눅스 기본), Reno(전통) 알고리즘
//
//  [UDP는 단순]
//    8바이트 헤더: src port, dst port, length, checksum
//    상태 없음, 재전송 없음, 순서 없음. 응용이 다 처리.
//    DNS, NTP, VoIP, 게임, QUIC(기반)
// =============================================================================

#pragma pack(push, 1)
struct UdpHeader {
    uint16_t src_port;
    uint16_t dst_port;
    uint16_t length;        // 헤더 + 페이로드
    uint16_t checksum;
};
struct TcpHeader {
    uint16_t src_port;
    uint16_t dst_port;
    uint32_t seq;
    uint32_t ack;
    uint8_t  data_offset;   // 상위 4비트=data offset(*4=헤더크기)
    uint8_t  flags;         // CWR ECE URG ACK PSH RST SYN FIN
    uint16_t window;
    uint16_t checksum;
    uint16_t urgent;
};
#pragma pack(pop)

void lesson4_l4_tcp_udp() {
    cout << "[레슨 4] L4 — TCP / UDP\n\n";

    cout << R"(
  ■ TCP 상태 머신 (간략)
  ┌────────┐ open()  ┌─────────┐ SYN sent ┌────────┐
  │CLOSED  ├────────▶│SYN_SENT ├──────────▶│ESTABL. │
  └────┬───┘         └─────────┘           └───┬────┘
       │ listen()                              │ close()
       ▼                                       ▼
  ┌────────┐ SYN+ACK ┌─────────┐ ACK 받음   ┌─────────┐
  │LISTEN  ├────────▶│SYN_RCVD ├──────────▶ │ESTABL.  │
  └────────┘         └─────────┘            └───┬─────┘
                                                ▼
                                           ┌────────┐
                                           │FIN_WAIT1│ → ... → TIME_WAIT
                                           └────────┘

  ■ TCP 플래그
    SYN  - 연결 시작
    ACK  - 확인 응답
    FIN  - 정상 종료
    RST  - 비정상 종료 (즉시 종료, 응답 없음)
    PSH  - 즉시 전달
    URG  - 긴급 데이터 (현대엔 거의 안 씀)
)";

    UdpHeader udp{};
    udp.src_port = htons(53);          // DNS
    udp.dst_port = htons(54321);
    udp.length   = htons(20);
    udp.checksum = 0;                  // IPv4에선 선택, IPv6에선 필수
    cout << "  UDP 헤더: " << ntohs(udp.src_port) << " → "
         << ntohs(udp.dst_port) << ", len=" << ntohs(udp.length) << "\n";

    TcpHeader tcp{};
    tcp.src_port    = htons(54321);
    tcp.dst_port    = htons(80);
    tcp.seq         = htonl(1000);
    tcp.ack         = 0;
    tcp.data_offset = (5 << 4);        // 5*4 = 20 bytes
    tcp.flags       = 0x02;            // SYN
    tcp.window      = htons(65535);
    cout << "  TCP SYN: " << ntohs(tcp.src_port) << " → "
         << ntohs(tcp.dst_port) << " seq=" << ntohl(tcp.seq) << "\n";

    cout << R"(
  ┌─ L4 메모리 / 실무 함정 ───────────────────────────────┐
  │ ✦ Nagle 알고리즘 (TCP_NODELAY로 끄기)                 │
  │   기본: 작은 패킷 모았다 보냄 → 지연 ↑                │
  │   대화형(SSH, 게임)에선 끄기                          │
  │ ✦ Delayed ACK: 수신측이 ACK 즉시 X, 200ms 지연        │
  │   Nagle + Delayed ACK 조합 → 핑퐁 지연 (40~200ms)     │
  │ ✦ TIME_WAIT 누적: SO_REUSEADDR, 짧은 timewait 튜닝   │
  │ ✦ recv는 partial - 한 번에 다 안 옴                   │
  │   → 길이 prefix 또는 delimiter로 메시지 경계 표시 필수│
  │ ✦ 보낸 측은 send 다 했는데 받는 측은 절반?            │
  │   → TCP는 byte stream, message X. 응용 프레이밍 필수  │
  │ ✦ keepalive: 기본 OFF / 2시간. 짧게 튜닝하거나        │
  │   응용 ping/pong 직접 구현                            │
  │ ✦ SO_LINGER: close()시 미전송 데이터 처리 정책        │
  │ ✦ UDP 메시지가 MTU 초과 → 단편화 / 분실 시 전체 무효  │
  │ ✦ UDP 체크섬 0 → IPv4 검증 안 함, IPv6는 drop         │
  └───────────────────────────────────────────────────────┘
)";
    cout << endl;
}


// =============================================================================
//  레슨 5 — 실제 TCP 에코 서버 + 클라이언트 (인-프로세스 데모)
// =============================================================================
//
//  [동작]
//    스레드 1: TCP 서버, 127.0.0.1:0 (OS가 포트 자동 할당)
//    스레드 2(메인): 클라이언트, 메시지 송신 / 응답 수신
//
//  [학습 포인트]
//    - listen / accept / send / recv 흐름
//    - partial recv 처리 패턴
//    - 길이 prefix 프레이밍
//    - RAII 소켓 관리
//    - 에러 처리 (errno / WSAGetLastError)
// =============================================================================

// 메시지 프레이밍: [4바이트 길이(big-endian)] [페이로드]
// 이렇게 안 하면 recv가 메시지 경계를 모름 (TCP는 byte stream).
bool send_all(socket_t s, const void* buf, size_t len) {
    const char* p = static_cast<const char*>(buf);
    size_t left = len;
    while (left > 0) {
        int n = ::send(s, p, (int)left, 0);
        if (n <= 0) return false;
        p += n;
        left -= n;
    }
    return true;
}

bool recv_all(socket_t s, void* buf, size_t len) {
    char* p = static_cast<char*>(buf);
    size_t left = len;
    while (left > 0) {
        int n = ::recv(s, p, (int)left, 0);
        if (n <= 0) return false;          // 0 = 정상 종료, <0 = 에러
        p += n;
        left -= n;
    }
    return true;
}

bool send_message(socket_t s, const string& msg) {
    // [메모리 함정] message 크기가 4GB 넘으면 prefix가 truncate.
    // 실무는 max 크기 강제 (예: 16MB) - DoS 방어.
    if (msg.size() > 16 * 1024 * 1024) return false;
    uint32_t len = htonl((uint32_t)msg.size());
    if (!send_all(s, &len, 4)) return false;
    return send_all(s, msg.data(), msg.size());
}

bool recv_message(socket_t s, string& out) {
    uint32_t len_be;
    if (!recv_all(s, &len_be, 4)) return false;
    uint32_t len = ntohl(len_be);
    if (len > 16 * 1024 * 1024) return false;   // DoS 가드
    out.resize(len);
    if (len == 0) return true;
    return recv_all(s, &out[0], len);
}

void run_echo_server(uint16_t* out_port, atomic<bool>* ready, atomic<bool>* stop) {
    Socket listener(::socket(AF_INET, SOCK_STREAM, 0));
    if (!listener.valid()) { *ready = true; return; }

    // SO_REUSEADDR: TIME_WAIT 상태인 포트 재사용 허용
    int yes = 1;
    setsockopt(listener.get(), SOL_SOCKET, SO_REUSEADDR,
               (const char*)&yes, sizeof(yes));

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = 0;                      // OS가 포트 자동 할당

    if (::bind(listener.get(), (sockaddr*)&addr, sizeof(addr)) < 0) {
        cerr << "  bind 실패 errno=" << sock_errno() << "\n";
        *ready = true;
        return;
    }

    sock_len alen = sizeof(addr);
    if (::getsockname(listener.get(), (sockaddr*)&addr, &alen) < 0) {
        *ready = true;
        return;
    }
    *out_port = ntohs(addr.sin_port);

    if (::listen(listener.get(), 16) < 0) { *ready = true; return; }
    *ready = true;

    // 1개 연결만 처리 (데모)
    sockaddr_in client_addr{};
    sock_len clen = sizeof(client_addr);
    Socket client(::accept(listener.get(), (sockaddr*)&client_addr, &clen));
    if (!client.valid()) return;

    string msg;
    while (!*stop && recv_message(client.get(), msg)) {
        // [메모리 주의] msg 버퍼 재사용 - resize로 크기 조정.
        // 매 호출마다 new string 만들지 않음.
        if (msg == "QUIT") break;
        if (!send_message(client.get(), "ECHO: " + msg)) break;
    }
}

void lesson5_tcp_echo() {
    cout << "[레슨 5] 실제 TCP 에코 서버 + 클라이언트\n\n";

    uint16_t port = 0;
    atomic<bool> ready{false}, stop{false};
    thread server([&]{ run_echo_server(&port, &ready, &stop); });

    // ready 대기
    while (!ready) this_thread::sleep_for(chrono::milliseconds(10));
    if (port == 0) {
        cout << "  서버 시작 실패 - 데모 스킵\n";
        server.join();
        cout << endl;
        return;
    }
    cout << "  서버 시작: 127.0.0.1:" << port << "\n";

    // 클라이언트
    Socket cli(::socket(AF_INET, SOCK_STREAM, 0));
    sockaddr_in saddr{};
    saddr.sin_family = AF_INET;
    saddr.sin_port   = htons(port);
    saddr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    if (::connect(cli.get(), (sockaddr*)&saddr, sizeof(saddr)) < 0) {
        cout << "  connect 실패\n";
        server.join();
        return;
    }
    cout << "  연결 성공\n";

    vector<string> messages = {"hello", "world", "C++", "QUIT"};
    for (auto& m : messages) {
        if (!send_message(cli.get(), m)) break;
        if (m == "QUIT") break;
        string reply;
        if (!recv_message(cli.get(), reply)) break;
        cout << "    " << m << " → " << reply << "\n";
    }

    cli.close();
    server.join();

    cout << R"(
  ┌─ 실제 소켓 코드의 함정 모음 ──────────────────────────┐
  │ ✦ recv가 0을 반환 = 정상 종료 (에러 아님)             │
  │ ✦ recv가 -1 + EINTR = 시그널로 중단, 재시도해야 함    │
  │ ✦ recv가 -1 + EAGAIN/EWOULDBLOCK = 논블록에서 데이터X │
  │ ✦ send가 -1 + EPIPE = 상대가 닫음. SIGPIPE 차단 필요  │
  │   (Linux에선 send에 MSG_NOSIGNAL 또는 signal SIG_IGN) │
  │ ✦ accept가 -1 + ECONNABORTED = 클라가 connect 후 RST │
  │   → 서버는 무시하고 다음 accept 진행                   │
  │ ✦ 버퍼 크기: SO_RCVBUF / SO_SNDBUF 기본 64KB ~ 4MB    │
  │   응용이 빠르게 안 읽으면 송신측 send가 블록           │
  │ ✦ 메모리 누수 위험: 예외로 함수 빠질 때 close 누락    │
  │   → RAII Socket 클래스 필수 (위 코드 참고)            │
  │ ✦ 동시 접속 수가 ulimit -n (fd 제한) 초과 → accept 실패│
  │ ✦ Nagle: 실시간성 필요하면 TCP_NODELAY                │
  └───────────────────────────────────────────────────────┘
)";
    cout << endl;
}


// =============================================================================
//  레슨 6 — 비동기 I/O 모델
// =============================================================================
//
//  [모델 비교]
//    Blocking + 1 thread/connection:
//      - 단순. 스레드 폭증 (10K 연결 = 10K 스레드 = 10GB 스택)
//      - 컨텍스트 스위칭 비용
//
//    select/poll:
//      - 1 스레드가 수많은 fd 감시
//      - select: fd_set 비트맵, FD_SETSIZE(보통 1024) 제한
//      - poll: 배열, 제한 없음. 하지만 매번 전체 스캔 O(N)
//
//    epoll (Linux) / kqueue (BSD/Mac):
//      - 커널이 이벤트 큐 유지. wait는 발생한 fd만 반환 O(준비된 수)
//      - edge-triggered (ET) vs level-triggered (LT)
//      - 100K 연결 가능 (C10K 문제 해결)
//
//    IOCP (Windows):
//      - 완료 통지 모델. 워커 스레드 풀이 큐에서 꺼냄
//      - 진짜 비동기 (epoll은 readiness, IOCP는 completion)
//
//    io_uring (Linux 5.1+):
//      - 커널-유저 공유 ring buffer. syscall 거의 없음
//      - 네트워크 + 파일 + 타이머 통합
// =============================================================================

void lesson6_async_io_models() {
    cout << "[레슨 6] 비동기 I/O 모델\n\n";

    cout << R"(
  ┌─ 모델별 트레이드오프 ─────────────────────────────────┐
  │ 모델       │ 동시연결 │ CPU효율 │ 코드복잡 │ 플랫폼  │
  │────────────┼──────────┼─────────┼──────────┼─────────│
  │ thread/연결│ ~ 1K    │ 낮음    │ 쉬움     │ 모두    │
  │ select     │ ~ 1K    │ 낮음    │ 보통     │ 모두    │
  │ poll       │ ~ 10K   │ 보통    │ 보통     │ 모두    │
  │ epoll      │ ~ 100K+ │ 높음    │ 어려움   │ Linux   │
  │ kqueue     │ ~ 100K+ │ 높음    │ 어려움   │ BSD/Mac │
  │ IOCP       │ ~ 100K+ │ 높음    │ 어려움   │ Windows │
  │ io_uring   │ ~ 1M+   │ 최고    │ 매우어려움│ Linux 5+│
  └────────────┴──────────┴─────────┴──────────┴─────────┘

  ■ 추천 라이브러리 (직접 구현보다 거의 항상 정답)
    - Boost.Asio   : 크로스플랫폼, async/await 풍 (C++20 coroutines)
    - libuv        : Node.js 기반 엔진. C API
    - libevent     : 오랜 역사
    - Seastar      : 샤딩+코루틴 고성능 (ScyllaDB 등)

  ■ 메모리 함정
    - Edge-triggered epoll: EAGAIN 받을 때까지 read 반복 필수
      → 안 그러면 다음 이벤트 안 옴 → 데드락
    - 콜백 클로저 캡처: this 포인터가 연결 종료 후 살아있어야 함
      → shared_ptr<Connection> + enable_shared_from_this 패턴
    - 버퍼 풀: 매번 new/delete = heap fragmentation
      → 고정 크기 풀 (slab allocator) 또는 ring buffer
    - 백프레셔(backpressure): 송신 버퍼 가득 → 새 요청 거부 정책 필요
)";

    // 간단한 select() 데모 - 표준 입력 + 0.5초 타임아웃
#ifndef _WIN32
    cout << "\n  [select() 데모 스킵 - 비대화형]\n";
#else
    cout << "\n  [Winsock select() 데모 - 1초 타임아웃]\n";
    Socket dummy(::socket(AF_INET, SOCK_DGRAM, 0));
    if (dummy.valid()) {
        fd_set rfds;
        FD_ZERO(&rfds);
        FD_SET(dummy.get(), &rfds);
        timeval tv{1, 0};
        int ready = select(0, &rfds, nullptr, nullptr, &tv);
        cout << "  select 반환: " << ready << " (0=타임아웃, 데이터 없음 정상)\n";
    }
#endif
    cout << endl;
}


// =============================================================================
//  레슨 7 — TLS 핸드셰이크
// =============================================================================

void lesson7_tls_handshake() {
    cout << "[레슨 7] TLS 1.3 핸드셰이크\n\n";

    cout << R"(
  ┌─ TLS 1.3 (RFC 8446) ──────────────────────────────────┐
  │                                                       │
  │   Client                            Server            │
  │     │                                  │              │
  │     │ ── ClientHello ─────────────────▶│  (1 RTT 시작)│
  │     │   + Random                       │              │
  │     │   + 지원 cipher suites           │              │
  │     │   + KeyShare (ECDHE 공개키)      │              │
  │     │                                  │              │
  │     │ ◀── ServerHello ────────────── ──│              │
  │     │   + Random                       │              │
  │     │   + 선택된 cipher                │              │
  │     │   + KeyShare (ECDHE 공개키)      │              │
  │     │  → 여기서부터 암호화 시작        │              │
  │     │ ◀── EncryptedExtensions ─────────│              │
  │     │ ◀── Certificate ─────────────────│  (서버 인증서)│
  │     │ ◀── CertificateVerify ───────────│  (서명)       │
  │     │ ◀── Finished ────────────────────│              │
  │     │                                  │              │
  │     │ ── Finished ──────────────────▶ │  (1 RTT 끝)   │
  │     │ ── Application Data ──────────▶ │              │
  │     │                                  │              │
  └───────────────────────────────────────────────────────┘

  ■ TLS 1.2 → 1.3 차이
    - RTT: 2 → 1 (속도)
    - cipher suite 개수: ~37 → 5 (보안 단순화)
    - 0-RTT (PSK 재방문): 매우 빠르지만 replay 취약 → 멱등 요청만
    - 모든 메시지 hello 이후 암호화 (메타데이터 보호)

  ■ 서버 인증서 검증 단계
    1) 서명 체인 검증 → root CA까지
    2) hostname 매칭 (SAN, CN)
    3) 만료 / 발효 시점
    4) revocation (CRL, OCSP, OCSP stapling)
    5) HSTS / pinning (선택)

  ■ 라이브러리 선택
    OpenSSL : 사실상 표준, API 복잡, 메모리 관리 직접
    BoringSSL : 구글 fork, OpenSSL 호환되지만 ABI 안정성 X
    mbedTLS  : 임베디드, 작음, 단순 API
    wolfSSL  : 임베디드, 인증 받기 좋음

  ■ TLS 메모리 / 보안 함정
    - SSL_CTX는 프로세스 단위, SSL은 연결 단위 → 적절히 공유
    - 인증서 체인 메모리: X509_free / EVP_PKEY_free 누락 → 누수
    - BIO 추상화: 메모리 BIO에서 read 안 하면 무한 누적
    - 프라이빗 키 메모리 → 사용 후 즉시 OPENSSL_cleanse
    - heartbleed 같은 OOB read 취약점 → 항상 최신 버전
    - 압축 (TLS_compression)은 끄기 (CRIME 공격)
    - secure_getenv / mlock (스왑 방지)으로 메모리 보호 강화
)";

    cout << endl;
}


// =============================================================================
//  레슨 8 — 네트워크 메모리 함정 종합
// =============================================================================

void lesson8_memory_pitfalls() {
    cout << "[레슨 8] 네트워크 메모리 함정 종합\n\n";

    cout << R"(
  ┌─ 함정 1: send/recv 버퍼 정책 ─────────────────────────┐
  │ 잘못: 매 메시지마다 new char[size] / delete            │
  │   → heap 단편화. 100K connection × 100msg/s = 10M/s   │
  │     malloc 호출. tcmalloc/jemalloc 추천               │
  │ 옳음: 연결당 고정 버퍼 + ring buffer 또는 chain buffer│
  │   Boost.Asio의 streambuf, ASIO buffers 참고           │
  └───────────────────────────────────────────────────────┘

  ┌─ 함정 2: partial recv 미처리 ─────────────────────────┐
  │ 잘못: char buf[1024]; recv(s, buf, 1024);             │
  │   → 한 번에 1024 안 옴. 메시지 파편 받고 끝남          │
  │ 옳음: 길이 prefix 또는 delimiter 기반 프레이밍         │
  │   recv 결과 누적 → 메시지 완성 시점 확인              │
  └───────────────────────────────────────────────────────┘

  ┌─ 함정 3: zero-copy 환상 ──────────────────────────────┐
  │ "버퍼 복사 없이 직접 보내기 위해 string_view ..."     │
  │   → 비동기 send 큐에 들어간 동안 원본 살아있어야 함    │
  │   → C# delegate처럼 그냥 넘기면 use-after-free        │
  │ 해결:                                                 │
  │   (a) shared_ptr<vector<char>> 캡처 (수명 보장)       │
  │   (b) write(buffer) 콜백에서 release (Asio 패턴)      │
  │   (c) sendfile/splice (커널 zero-copy)                │
  └───────────────────────────────────────────────────────┘

  ┌─ 함정 4: 콜백 캡처와 객체 수명 ───────────────────────┐
  │ class Conn {                                          │
  │   void on_read(char* buf, size_t n) { ... }           │
  │   void start() {                                      │
  │     async_read([this](err, n){ on_read(...); });      │
  │     // ⚠ async 콜백 도중 *this 소멸하면 UB            │
  │   }                                                   │
  │ };                                                    │
  │ 해결: enable_shared_from_this + shared_ptr 캡처        │
  │   async_read([self=shared_from_this()](...){...});    │
  └───────────────────────────────────────────────────────┘

  ┌─ 함정 5: TLS 라이브러리 누수 ─────────────────────────┐
  │ OpenSSL 객체는 거의 모두 *_free() 짝 필요             │
  │   X509, EVP_PKEY, BIO, SSL, SSL_CTX, ...              │
  │ → unique_ptr custom deleter로 RAII화                  │
  │ struct SslDel { void operator()(SSL* s){ SSL_free(s); }};│
  │ unique_ptr<SSL, SslDel> ssl(SSL_new(ctx));            │
  └───────────────────────────────────────────────────────┘

  ┌─ 함정 6: getaddrinfo 결과 ───────────────────────────┐
  │ struct addrinfo* res; getaddrinfo(...);               │
  │ → 사용 후 freeaddrinfo(res) 필수                       │
  │ → 예외 경로에서 누수 → unique_ptr 래핑                │
  └───────────────────────────────────────────────────────┘

  ┌─ 함정 7: 멀티스레드 + 한 소켓 ────────────────────────┐
  │ 한 소켓에 여러 스레드가 send/recv ?                   │
  │ - send/recv 자체는 thread-safe (POSIX) 하지만         │
  │   메시지 인터리빙 발생 → 사용 코드 망가짐              │
  │ - read는 한 스레드, write 큐는 다른 스레드 (이벤트루프 패턴)│
  └───────────────────────────────────────────────────────┘

  ┌─ 함정 8: sockaddr_storage 사용 ───────────────────────┐
  │ IPv4/IPv6 둘 다 지원 시 sockaddr_in 16byte로는 부족   │
  │ sockaddr_storage(128byte) 사용 필수                   │
  │ accept에 sockaddr_in 넘기다 IPv6 truncate → 미스매치  │
  └───────────────────────────────────────────────────────┘
)";

    cout << endl;
}


// =============================================================================
//  연습문제
// =============================================================================
//
//  [연습 1] 위 에코 서버를 멀티 클라이언트 지원하게 확장
//   → accept 후 thread / 또는 select 기반 단일 스레드
//
//  [연습 2] UDP 에코 서버 / 클라이언트 작성
//   → connection-less, recvfrom/sendto 사용. partial 없지만 단편화 주의
//
//  [연습 3] HTTP/1.1 GET 클라이언트 손수 작성
//   → 헤더 파싱, Content-Length 처리, Transfer-Encoding: chunked 처리
//
//  [연습 4] TCP 길이-프레임 메시지에 max 크기 + 타임아웃 추가
//   → DoS 방어. recv 시 setsockopt(SO_RCVTIMEO) 사용
//
//  [연습 5] IP 헤더 패킷 캡처 (Linux: AF_PACKET, root 필요)
//   → tcpdump 미니버전. 1분 캡처 → 프로토콜별 통계
//
//  [연습 6] poll() 기반 echo 서버 - 연결 1000개 처리
//   → struct pollfd 배열 동적 관리. 연결 추가/제거
//
//  [연습 7] Boost.Asio로 동일 에코 서버 재구현 후 코드 줄 수 비교
//   → async_read_until + enable_shared_from_this
//
//  [연습 8] TLS 클라이언트 (OpenSSL)
//   → SSL_CTX 생성, SSL_connect, 인증서 검증 callback 등록
// =============================================================================
