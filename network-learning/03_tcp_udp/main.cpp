/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  네트워크 학습 03단계: TCP/UDP 완전 정복
  ─────────────────────────────────────────────────
  TCP 3-way Handshake, 흐름 제어, 혼잡 제어,
  TCP/UDP 에코 서버/클라이언트 (Winsock)

  ■ 컴파일 방법:
      g++ -std=c++17 -Wall -lws2_32 -o tcp_udp main.cpp

  ■ 이 파일을 배우면 할 수 있는 것:
      - TCP와 UDP의 차이를 완벽히 이해
      - 3-way handshake 과정을 설명 가능
      - 슬라이딩 윈도우, 혼잡 제어 원리 파악
      - Winsock으로 실제 소켓 프로그래밍 가능!

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// ┌───────────────────────────────────────────────────────────────────┐
// │  ★ 플랫폼 분기: Windows(Winsock2)와 Linux(POSIX) 모두 지원!     │
// │  #ifdef _WIN32 로 분기하여 양쪽 모두 컴파일 가능                  │
// └───────────────────────────────────────────────────────────────────┘

#ifdef _WIN32
    // ── Windows (Winsock2) ──
    #ifndef WIN32_LEAN_AND_MEAN
    #define WIN32_LEAN_AND_MEAN
    #endif
    #include <winsock2.h>
    #include <ws2tcpip.h>
    // ★ 링크: -lws2_32
    // Winsock 초기화/정리 매크로
    #define SOCKET_INIT() do { \
        WSADATA wsa; \
        WSAStartup(MAKEWORD(2, 2), &wsa); \
    } while(0)
    #define SOCKET_CLEANUP() WSACleanup()
    #define CLOSE_SOCKET(s) closesocket(s)
    #define SOCKET_ERROR_CODE WSAGetLastError()
    typedef int socklen_t;
#else
    // ── Linux/macOS (POSIX) ──
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
#include <iomanip>
#include <sstream>
#include <algorithm>
#include <array>
#include <thread>
#include <chrono>
#include <functional>

// ════════════════════════════════════════════════════════════════════
//  TCP vs UDP 비교 - "전화 통화 vs 편지"
// ════════════════════════════════════════════════════════════════════
//
//  ┌─────────────────────┬──────────────────┬───────────────────┐
//  │ 항목                │ TCP              │ UDP                │
//  ├─────────────────────┼──────────────────┼───────────────────┤
//  │ 비유                │ 전화 통화         │ 편지 보내기        │
//  │ 연결                │ 연결 지향 (O)     │ 비연결 (X)         │
//  │ 신뢰성              │ 보장 (재전송)     │ 미보장             │
//  │ 순서                │ 보장              │ 미보장             │
//  │ 속도                │ 느림              │ 빠름               │
//  │ 헤더 크기           │ 20~60 bytes      │ 8 bytes            │
//  │ 흐름 제어           │ 있음              │ 없음               │
//  │ 혼잡 제어           │ 있음              │ 없음               │
//  │ 브로드캐스트        │ 불가              │ 가능               │
//  │ 사용 예             │ HTTP, FTP, SSH   │ DNS, 게임, 스트림  │
//  └─────────────────────┴──────────────────┴───────────────────┘
//
//  ★ TCP를 선택하는 경우:
//    - 데이터가 정확히 전달되어야 할 때 (웹, 파일 전송, 이메일)
//    - 순서가 중요할 때 (파일 다운로드)
//
//  ★ UDP를 선택하는 경우:
//    - 속도가 중요할 때 (온라인 게임, 영상 통화)
//    - 일부 손실 허용 (실시간 스트리밍)
//    - 브로드캐스트/멀티캐스트 필요 시 (DHCP, DNS)

// ════════════════════════════════════════════════════════════════════
//  TCP 3-way Handshake - "전화 연결 과정"
// ════════════════════════════════════════════════════════════════════
//
//  비유: 전화 통화 시작
//    나:   "여보세요?" (SYN)
//    상대: "네, 여보세요!" (SYN+ACK)
//    나:   "잘 들리네요, 얘기해요!" (ACK)
//
//  ┌─────────────────────────────────────────────────────────┐
//  │              TCP 3-way Handshake                         │
//  │                                                          │
//  │   Client (CLOSED)                Server (LISTEN)         │
//  │        │                              │                  │
//  │        │─── SYN (seq=x) ─────────>│  SYN_SENT          │
//  │        │    "연결해줘!"               │                  │
//  │        │                              │ SYN_RECEIVED     │
//  │        │<── SYN+ACK (seq=y,ack=x+1)──│                  │
//  │        │    "OK, 나도 연결!"          │                  │
//  │        │                              │                  │
//  │        │─── ACK (seq=x+1,ack=y+1) ──>│  ESTABLISHED    │
//  │        │    "연결 완료!"              │                  │
//  │        │                              │                  │
//  │   ESTABLISHED                    ESTABLISHED             │
//  │        │ ←── 데이터 전송 시작 ──→ │                     │
//  └─────────────────────────────────────────────────────────┘
//
//  ★ 왜 3-way인가?
//     1. Client → Server: "내가 보낸 거 받을 수 있어?" (SYN)
//     2. Server → Client: "응 받을 수 있어, 너도 받을 수 있어?" (SYN+ACK)
//     3. Client → Server: "응 나도 받을 수 있어!" (ACK)
//     → 양방향 모두 통신 가능함을 확인!

// ════════════════════════════════════════════════════════════════════
//  TCP 4-way Teardown - "전화 끊기 과정"
// ════════════════════════════════════════════════════════════════════
//
//  비유: 전화 끊기
//    나:   "나 끊을게" (FIN)
//    상대: "알겠어" (ACK)
//    상대: "나도 끊을게" (FIN)
//    나:   "알겠어, 끊자" (ACK) → TIME_WAIT 후 종료
//
//  ┌─────────────────────────────────────────────────────────┐
//  │              TCP 4-way Teardown                           │
//  │                                                          │
//  │   Client (ESTABLISHED)        Server (ESTABLISHED)       │
//  │        │                              │                  │
//  │        │─── FIN (seq=u) ────────────>│  FIN_WAIT_1      │
//  │        │    "끊을게!"                 │                  │
//  │        │                              │ CLOSE_WAIT       │
//  │        │<── ACK (ack=u+1) ───────────│                  │
//  │        │    "알겠어"            FIN_WAIT_2               │
//  │        │                              │                  │
//  │        │<── FIN (seq=v) ─────────────│  LAST_ACK        │
//  │        │    "나도 끊을게!"            │                  │
//  │        │                              │                  │
//  │        │─── ACK (ack=v+1) ──────────>│  CLOSED          │
//  │        │    "알겠어"                  │                  │
//  │   TIME_WAIT                                              │
//  │   (2MSL 대기 후 CLOSED)                                  │
//  └─────────────────────────────────────────────────────────┘
//
//  ★ TIME_WAIT (2MSL):
//     - MSL = Maximum Segment Lifetime (보통 2분)
//     - 마지막 ACK가 유실되었을 때 재전송 가능하도록 대기
//     - 서버에서 netstat 시 TIME_WAIT가 많으면 정상!

// ════════════════════════════════════════════════════════════════════
//  TCP 상태 다이어그램
// ════════════════════════════════════════════════════════════════════
//
//  ┌─────────────────────────────────────────────────────────────┐
//  │                   TCP 상태 전이 다이어그램                    │
//  │                                                              │
//  │              ┌──────────┐                                    │
//  │              │  CLOSED  │                                    │
//  │              └────┬─────┘                                    │
//  │         (서버)    │    (클라이언트)                           │
//  │        listen()   │     connect()                            │
//  │            ↓      │       ↓                                  │
//  │      ┌────────┐   │   ┌──────────┐                          │
//  │      │ LISTEN │   │   │ SYN_SENT │                          │
//  │      └───┬────┘   │   └────┬─────┘                          │
//  │   SYN수신 │        │        │ SYN+ACK수신                   │
//  │          ↓        │        ↓                                │
//  │   ┌──────────────┐│   ┌─────────────┐                      │
//  │   │ SYN_RECEIVED ││   │ ESTABLISHED │                      │
//  │   └──────┬───────┘│   └──────┬──────┘                      │
//  │    ACK수신│        │          │ close()                     │
//  │          ↓        │          ↓                              │
//  │   ┌─────────────┐ │   ┌──────────┐                         │
//  │   │ ESTABLISHED │ │   │FIN_WAIT_1│                         │
//  │   └─────────────┘ │   └────┬─────┘                         │
//  │                    │   ACK수신│                              │
//  │                    │        ↓                                │
//  │                    │   ┌──────────┐   ┌──────────┐         │
//  │                    │   │FIN_WAIT_2│──→│TIME_WAIT │         │
//  │                    │   └──────────┘   └────┬─────┘         │
//  │                    │                  2MSL후│               │
//  │                    │                       ↓               │
//  │                    │                 ┌──────────┐           │
//  │                    └────────────────→│  CLOSED  │           │
//  │                                      └──────────┘           │
//  └─────────────────────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  TCP 헤더 구조 (상세)
// ════════════════════════════════════════════════════════════════════
//
//   0                   1                   2                   3
//   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
//  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//  |          Source Port          |       Destination Port        |
//  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//  |                        Sequence Number                       |
//  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//  |                    Acknowledgment Number                     |
//  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//  |  Data |       |U|A|P|R|S|F|                                  |
//  | Offset| Rsrvd |R|C|S|S|Y|I|            Window Size           |
//  |       |       |G|K|H|T|N|N|                                  |
//  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//  |           Checksum            |         Urgent Pointer        |
//  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

// ── TCP 헤더 구조체 ──
#pragma pack(push, 1)
struct TCPHeader {
    uint16_t src_port;          // 출발지 포트 번호
    uint16_t dst_port;          // 목적지 포트 번호
    uint32_t seq_num;           // 시퀀스 번호 (보낸 바이트 순서)
    uint32_t ack_num;           // 확인 번호 ("여기까지 받았어")
    uint8_t  data_offset : 4;   // 헤더 길이 (4바이트 단위)
    uint8_t  reserved : 3;      // 예약 비트
    uint8_t  ns : 1;            // ECN-nonce
    uint8_t  flags;             // 제어 플래그 (URG,ACK,PSH,RST,SYN,FIN)
    uint16_t window_size;       // 수신 윈도우 크기 (흐름 제어)
    uint16_t checksum;          // 체크섬 (무결성)
    uint16_t urgent_ptr;        // 긴급 포인터
};
#pragma pack(pop)

// ── UDP 헤더 구조체 (8바이트!) ──
#pragma pack(push, 1)
struct UDPHeader {
    uint16_t src_port;          // 출발지 포트
    uint16_t dst_port;          // 목적지 포트
    uint16_t length;            // 헤더+데이터 전체 길이
    uint16_t checksum;          // 체크섬 (IPv4에서는 선택)
};
#pragma pack(pop)

// TCP 플래그 상수
namespace TCPFlags {
    constexpr uint8_t FIN = 0x01;  // 연결 종료
    constexpr uint8_t SYN = 0x02;  // 연결 시작
    constexpr uint8_t RST = 0x04;  // 강제 리셋
    constexpr uint8_t PSH = 0x08;  // 즉시 전달
    constexpr uint8_t ACK = 0x10;  // 확인 응답
    constexpr uint8_t URG = 0x20;  // 긴급 데이터
}

// TCP 플래그를 문자열로 변환
std::string flags_to_string(uint8_t flags) {
    std::string result;
    if (flags & TCPFlags::SYN) result += "SYN ";
    if (flags & TCPFlags::ACK) result += "ACK ";
    if (flags & TCPFlags::FIN) result += "FIN ";
    if (flags & TCPFlags::RST) result += "RST ";
    if (flags & TCPFlags::PSH) result += "PSH ";
    if (flags & TCPFlags::URG) result += "URG ";
    return result.empty() ? "(none)" : result;
}

// ════════════════════════════════════════════════════════════════════
//  슬라이딩 윈도우 - "흐름 제어의 핵심"
// ════════════════════════════════════════════════════════════════════
//
//  슬라이딩 윈도우란?
//  ─────────────────
//  ACK를 기다리지 않고 한번에 여러 패킷을 보내는 기술
//  "윈도우 크기"만큼 미리 전송 가능
//
//  비유: 택배 기사에게 미리 10개 맡기기
//    - Stop-and-Wait: 1개 보내고 → 확인 → 1개 보내고 → (느림!)
//    - Sliding Window: 10개 한번에 → 확인 → 10개 한번에 → (빠름!)
//
//  ┌────────────────────────────────────────────────────────────┐
//  │              슬라이딩 윈도우 동작                           │
//  │                                                            │
//  │  전송 버퍼:                                                │
//  │  [1][2][3][4][5][6][7][8][9][10][11][12]...                │
//  │   ▲─────────▲                                              │
//  │   │  윈도우  │                                              │
//  │   │  (크기=4)│                                              │
//  │                                                            │
//  │  시간 흐름:                                                │
//  │  t=0: [1][2][3][4] 전송 ←── 윈도우 크기만큼 한번에!       │
//  │  t=1: ACK(1) 수신                                          │
//  │  t=2: [2][3][4][5] ←── 윈도우가 1칸 슬라이드!             │
//  │  t=3: ACK(2) 수신                                          │
//  │  t=4: [3][4][5][6] ←── 계속 슬라이드                      │
//  │                                                            │
//  │  ★ 수신측이 window_size=0 보내면 → 전송 중단 (수신 버퍼   │
//  │    가득 참) → 이것이 "흐름 제어"!                          │
//  └────────────────────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  혼잡 제어 - "도로 교통 관리"
// ════════════════════════════════════════════════════════════════════
//
//  혼잡 제어란?
//  ───────────
//  네트워크가 혼잡할 때 전송 속도를 줄이는 기술
//  "도로가 막히면 차를 덜 보내는 것!"
//
//  ┌────────────────────────────────────────────────────────────┐
//  │              TCP 혼잡 제어 알고리즘                         │
//  │                                                            │
//  │  cwnd (Congestion Window) 변화:                            │
//  │                                                            │
//  │  cwnd                                                      │
//  │   ↑     ┌─── ssthresh (Slow Start Threshold)              │
//  │   │     │         ╱╲                                       │
//  │   │     │        ╱  ╲                                      │
//  │   │     │       ╱    ╲  ← 패킷 손실!                      │
//  │   │     │      ╱      ╲                                    │
//  │   │     │     ╱ 선형증가╲    ssthresh = cwnd/2             │
//  │   │     │    ╱(Congestion╲   cwnd = 1                      │
//  │   │     │   ╱  Avoidance) ╲                                │
//  │   │     │  ╱               ╲╱                              │
//  │   │     │ ╱                 ╱╲                              │
//  │   │   지수증가              ╱  ╲                            │
//  │   │  (Slow Start)          ╱    ╲                           │
//  │   │ ╱                                                      │
//  │   │╱                                                       │
//  │   └──────────────────────────────────→ 시간               │
//  │                                                            │
//  │  1단계: Slow Start (느린 시작)                              │
//  │    - cwnd = 1 MSS에서 시작                                  │
//  │    - ACK 받을 때마다 cwnd × 2 (지수적 증가)                │
//  │    - ssthresh에 도달하면 2단계로                            │
//  │                                                            │
//  │  2단계: Congestion Avoidance (혼잡 회피)                    │
//  │    - cwnd를 RTT마다 1 MSS씩 증가 (선형적 증가)             │
//  │    - 패킷 손실 감지 시 ssthresh = cwnd/2, cwnd = 1        │
//  │                                                            │
//  │  ★ MSS (Maximum Segment Size): 최대 세그먼트 크기          │
//  │    보통 1460 bytes (1500 MTU - 20 IP - 20 TCP)             │
//  └────────────────────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  슬라이딩 윈도우 시뮬레이션 클래스
// ════════════════════════════════════════════════════════════════════

class SlidingWindowSimulator {
private:
    int window_size_;               // 윈도우 크기
    int total_segments_;            // 전체 세그먼트 수
    std::vector<bool> acked_;       // ACK 수신 여부
    int base_;                      // 윈도우 시작 위치

public:
    SlidingWindowSimulator(int window_size, int total_segments)
        : window_size_(window_size),
          total_segments_(total_segments),
          acked_(total_segments, false),
          base_(0) {}

    // 윈도우 상태를 시각화
    void print_window() const {
        std::cout << "    ";
        for (int i = 0; i < total_segments_; i++) {
            if (i < base_) {
                // 이미 ACK 받은 것
                std::cout << "[" << std::setw(2) << (i + 1) << "]";
            } else if (i < base_ + window_size_ && i < total_segments_) {
                // 현재 윈도우 내
                std::cout << "<" << std::setw(2) << (i + 1) << ">";
            } else {
                // 아직 보내지 못함
                std::cout << " " << std::setw(2) << (i + 1) << " ";
            }
        }
        std::cout << std::endl;
        std::cout << "    ";
        for (int i = 0; i < total_segments_; i++) {
            if (i < base_) std::cout << " OK  ";
            else if (i == base_) std::cout << " ^── ";
            else if (i == std::min(base_ + window_size_ - 1, total_segments_ - 1))
                std::cout << " ──^ ";
            else if (i < base_ + window_size_) std::cout << "     ";
            else std::cout << "     ";
        }
        std::cout << std::endl;
    }

    // ACK 수신 시뮬레이션
    void receive_ack(int segment_num) {
        if (segment_num > 0 && segment_num <= total_segments_) {
            acked_[segment_num - 1] = true;
            // 윈도우 슬라이드: base부터 연속된 ACK 받은 것까지 이동
            while (base_ < total_segments_ && acked_[base_]) {
                base_++;
            }
        }
    }

    // 시뮬레이션 실행
    void simulate() {
        std::cout << "\n  ── 슬라이딩 윈도우 시뮬레이션 (윈도우=" << window_size_
                  << ", 세그먼트=" << total_segments_ << ") ──" << std::endl;

        std::cout << "\n  초기 상태:" << std::endl;
        print_window();

        // 라운드 1: 윈도우 크기만큼 전송
        std::cout << "\n  라운드 1: 세그먼트 1~" << window_size_ << " 전송" << std::endl;
        for (int i = 1; i <= std::min(window_size_, total_segments_); i++) {
            std::cout << "    → 세그먼트 " << i << " 전송" << std::endl;
        }

        // ACK 수신
        std::cout << "    ← ACK(1) 수신" << std::endl;
        receive_ack(1);
        std::cout << "    ← ACK(2) 수신" << std::endl;
        receive_ack(2);
        print_window();

        // 라운드 2: 윈도우 슬라이드 후 추가 전송
        std::cout << "\n  라운드 2: 윈도우 슬라이드 → 세그먼트 "
                  << (base_ + window_size_) << " 전송" << std::endl;
        print_window();

        std::cout << "\n    ★ 핵심: ACK 받은 만큼 윈도우가 오른쪽으로 슬라이드!" << std::endl;
    }
};

// ════════════════════════════════════════════════════════════════════
//  혼잡 제어 시뮬레이션 클래스
// ════════════════════════════════════════════════════════════════════

class CongestionControlSimulator {
private:
    double cwnd_;           // 혼잡 윈도우 (MSS 단위)
    double ssthresh_;       // Slow Start 임계값
    int round_;             // 현재 라운드

public:
    CongestionControlSimulator(double initial_ssthresh = 16.0)
        : cwnd_(1.0), ssthresh_(initial_ssthresh), round_(0) {}

    // 시뮬레이션 실행
    void simulate(int rounds, int loss_at_round = -1) {
        std::cout << "\n  ── 혼잡 제어 시뮬레이션 ──" << std::endl;
        std::cout << "  ┌──────┬────────┬───────────┬──────────────────────┐" << std::endl;
        std::cout << "  │Round │ cwnd   │ ssthresh  │ 상태                 │" << std::endl;
        std::cout << "  ├──────┼────────┼───────────┼──────────────────────┤" << std::endl;

        cwnd_ = 1.0;
        for (round_ = 0; round_ < rounds; round_++) {
            std::string state;

            // 패킷 손실 감지!
            if (round_ == loss_at_round) {
                ssthresh_ = cwnd_ / 2.0;
                cwnd_ = 1.0;
                state = "★ 패킷 손실! 리셋";
            }
            // Slow Start 단계 (지수 증가)
            else if (cwnd_ < ssthresh_) {
                state = "Slow Start (x2)";
                if (round_ > 0 && round_ != loss_at_round + 1) {
                    cwnd_ *= 2;
                    if (cwnd_ > ssthresh_) cwnd_ = ssthresh_;
                }
            }
            // Congestion Avoidance 단계 (선형 증가)
            else {
                state = "Cong. Avoidance (+1)";
                if (round_ > 0) cwnd_ += 1;
            }

            std::cout << "  │ " << std::setw(4) << round_
                      << " │ " << std::setw(6) << std::fixed << std::setprecision(0) << cwnd_
                      << " │ " << std::setw(9) << ssthresh_
                      << " │ " << std::setw(20) << std::left << state << std::right
                      << " │" << std::endl;
        }
        std::cout << "  └──────┴────────┴───────────┴──────────────────────┘" << std::endl;
    }
};

// ════════════════════════════════════════════════════════════════════
//  TCP 3-way Handshake 시뮬레이션
// ════════════════════════════════════════════════════════════════════

void simulate_tcp_handshake() {
    std::cout << "\n  ── TCP 3-way Handshake 시뮬레이션 ──" << std::endl;

    // 시퀀스 번호 초기화 (실제로는 랜덤)
    uint32_t client_isn = 1000;   // Client의 ISN (Initial Sequence Number)
    uint32_t server_isn = 5000;   // Server의 ISN

    // 1단계: SYN
    std::cout << "\n  [1] Client → Server: SYN" << std::endl;
    std::cout << "      flags: SYN, seq=" << client_isn
              << ", ack=0" << std::endl;
    std::cout << "      Client 상태: SYN_SENT" << std::endl;

    // 2단계: SYN+ACK
    std::cout << "\n  [2] Server → Client: SYN+ACK" << std::endl;
    std::cout << "      flags: SYN ACK, seq=" << server_isn
              << ", ack=" << (client_isn + 1) << std::endl;
    std::cout << "      Server 상태: SYN_RECEIVED" << std::endl;

    // 3단계: ACK
    std::cout << "\n  [3] Client → Server: ACK" << std::endl;
    std::cout << "      flags: ACK, seq=" << (client_isn + 1)
              << ", ack=" << (server_isn + 1) << std::endl;
    std::cout << "      양쪽 상태: ESTABLISHED" << std::endl;

    // 데이터 전송 시뮬레이션
    std::cout << "\n  [DATA] 데이터 전송:" << std::endl;
    std::string data = "Hello, Server!";
    std::cout << "      Client → Server: \"" << data << "\" ("
              << data.size() << " bytes)" << std::endl;
    std::cout << "      seq=" << (client_isn + 1)
              << ", ack=" << (server_isn + 1) << std::endl;

    std::cout << "\n      Server → Client: ACK" << std::endl;
    std::cout << "      ack=" << (client_isn + 1 + data.size())
              << " (\"" << data.size() << "바이트까지 잘 받았어\")" << std::endl;
}

// ════════════════════════════════════════════════════════════════════
//  TCP 4-way Teardown 시뮬레이션
// ════════════════════════════════════════════════════════════════════

void simulate_tcp_teardown() {
    std::cout << "\n  ── TCP 4-way Teardown 시뮬레이션 ──" << std::endl;

    uint32_t client_seq = 1015;
    uint32_t server_seq = 5001;

    // 1단계: FIN
    std::cout << "\n  [1] Client → Server: FIN" << std::endl;
    std::cout << "      flags: FIN ACK, seq=" << client_seq << std::endl;
    std::cout << "      Client 상태: FIN_WAIT_1" << std::endl;

    // 2단계: ACK
    std::cout << "\n  [2] Server → Client: ACK" << std::endl;
    std::cout << "      flags: ACK, ack=" << (client_seq + 1) << std::endl;
    std::cout << "      Client 상태: FIN_WAIT_2" << std::endl;
    std::cout << "      Server 상태: CLOSE_WAIT" << std::endl;

    // 3단계: FIN
    std::cout << "\n  [3] Server → Client: FIN" << std::endl;
    std::cout << "      flags: FIN ACK, seq=" << server_seq << std::endl;
    std::cout << "      Server 상태: LAST_ACK" << std::endl;

    // 4단계: ACK
    std::cout << "\n  [4] Client → Server: ACK" << std::endl;
    std::cout << "      flags: ACK, ack=" << (server_seq + 1) << std::endl;
    std::cout << "      Client 상태: TIME_WAIT (2MSL 대기)" << std::endl;
    std::cout << "      Server 상태: CLOSED" << std::endl;
    std::cout << "\n      ... 2MSL(약 4분) 후 ..." << std::endl;
    std::cout << "      Client 상태: CLOSED" << std::endl;
}

// ════════════════════════════════════════════════════════════════════
//  TCP 에코 서버 (Winsock / POSIX)
// ════════════════════════════════════════════════════════════════════
//
//  에코 서버란?
//  ───────────
//  클라이언트가 보낸 데이터를 그대로 돌려보내는 서버
//  네트워크 프로그래밍의 "Hello World"!
//
//  동작 흐름:
//  Client: "Hello!" → Server → "Hello!" (되돌려줌)

// TCP 에코 서버 함수
void run_tcp_echo_server(uint16_t port) {
    std::cout << "\n  ── TCP 에코 서버 시작 (포트: " << port << ") ──" << std::endl;

    SOCKET_INIT();  // Winsock 초기화 (Windows에서만 필요)

    // 1. 소켓 생성
    // AF_INET = IPv4, SOCK_STREAM = TCP
    SOCKET server_sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (server_sock == INVALID_SOCKET) {
        std::cerr << "  ✗ 소켓 생성 실패: " << SOCKET_ERROR_CODE << std::endl;
        SOCKET_CLEANUP();
        return;
    }
    std::cout << "  [1] 소켓 생성 완료 (TCP)" << std::endl;

    // SO_REUSEADDR 설정 (주소 재사용 - TIME_WAIT 문제 방지)
    int opt = 1;
    setsockopt(server_sock, SOL_SOCKET, SO_REUSEADDR,
               reinterpret_cast<const char*>(&opt), sizeof(opt));

    // 2. 주소 바인딩
    // "이 소켓을 특정 IP:포트에 묶기"
    struct sockaddr_in server_addr = {};
    server_addr.sin_family = AF_INET;           // IPv4
    server_addr.sin_addr.s_addr = INADDR_ANY;   // 모든 인터페이스 (0.0.0.0)
    server_addr.sin_port = htons(port);          // 포트 (네트워크 바이트 순서)
    // ★ htons(): Host TO Network Short (바이트 순서 변환)
    //    리틀 엔디안(x86) → 빅 엔디안(네트워크)

    if (bind(server_sock, reinterpret_cast<struct sockaddr*>(&server_addr),
             sizeof(server_addr)) == SOCKET_ERROR) {
        std::cerr << "  ✗ 바인딩 실패: " << SOCKET_ERROR_CODE << std::endl;
        CLOSE_SOCKET(server_sock);
        SOCKET_CLEANUP();
        return;
    }
    std::cout << "  [2] 바인딩 완료 (0.0.0.0:" << port << ")" << std::endl;

    // 3. 리스닝 (연결 대기)
    // 백로그 = 5 (대기열 최대 5개)
    if (listen(server_sock, 5) == SOCKET_ERROR) {
        std::cerr << "  ✗ 리스닝 실패: " << SOCKET_ERROR_CODE << std::endl;
        CLOSE_SOCKET(server_sock);
        SOCKET_CLEANUP();
        return;
    }
    std::cout << "  [3] 리스닝 시작 (백로그: 5)" << std::endl;
    std::cout << "      대기 중... (다른 터미널에서 클라이언트 실행)" << std::endl;

    // 4. 클라이언트 연결 수락
    struct sockaddr_in client_addr = {};
    socklen_t client_len = sizeof(client_addr);

    SOCKET client_sock = accept(server_sock,
                                reinterpret_cast<struct sockaddr*>(&client_addr),
                                &client_len);
    if (client_sock == INVALID_SOCKET) {
        std::cerr << "  ✗ Accept 실패: " << SOCKET_ERROR_CODE << std::endl;
        CLOSE_SOCKET(server_sock);
        SOCKET_CLEANUP();
        return;
    }

    char client_ip[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, sizeof(client_ip));
    std::cout << "  [4] 클라이언트 연결됨: " << client_ip
              << ":" << ntohs(client_addr.sin_port) << std::endl;

    // 5. 데이터 수신 및 에코
    char buffer[1024];
    while (true) {
        // recv(): 데이터 수신 (블로킹)
        int bytes_recv = recv(client_sock, buffer, sizeof(buffer) - 1, 0);

        if (bytes_recv <= 0) {
            if (bytes_recv == 0) {
                std::cout << "  클라이언트 연결 종료" << std::endl;
            } else {
                std::cerr << "  ✗ 수신 오류: " << SOCKET_ERROR_CODE << std::endl;
            }
            break;
        }

        buffer[bytes_recv] = '\0';
        std::cout << "  수신 (" << bytes_recv << " bytes): " << buffer << std::endl;

        // send(): 데이터 에코 (그대로 돌려보냄)
        int bytes_sent = send(client_sock, buffer, bytes_recv, 0);
        if (bytes_sent == SOCKET_ERROR) {
            std::cerr << "  ✗ 전송 오류: " << SOCKET_ERROR_CODE << std::endl;
            break;
        }
        std::cout << "  에코 (" << bytes_sent << " bytes): " << buffer << std::endl;
    }

    // 6. 정리
    CLOSE_SOCKET(client_sock);
    CLOSE_SOCKET(server_sock);
    SOCKET_CLEANUP();
    std::cout << "  서버 종료" << std::endl;
}

// ════════════════════════════════════════════════════════════════════
//  TCP 에코 클라이언트
// ════════════════════════════════════════════════════════════════════

void run_tcp_echo_client(const char* server_ip, uint16_t port) {
    std::cout << "\n  ── TCP 에코 클라이언트 시작 ──" << std::endl;

    SOCKET_INIT();

    // 1. 소켓 생성
    SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock == INVALID_SOCKET) {
        std::cerr << "  ✗ 소켓 생성 실패" << std::endl;
        SOCKET_CLEANUP();
        return;
    }
    std::cout << "  [1] 소켓 생성 완료" << std::endl;

    // 2. 서버에 연결 (여기서 3-way handshake 발생!)
    struct sockaddr_in server_addr = {};
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    inet_pton(AF_INET, server_ip, &server_addr.sin_addr);

    if (connect(sock, reinterpret_cast<struct sockaddr*>(&server_addr),
                sizeof(server_addr)) == SOCKET_ERROR) {
        std::cerr << "  ✗ 연결 실패: " << SOCKET_ERROR_CODE << std::endl;
        CLOSE_SOCKET(sock);
        SOCKET_CLEANUP();
        return;
    }
    std::cout << "  [2] 서버 연결 완료: " << server_ip << ":" << port << std::endl;

    // 3. 데이터 송수신
    const char* message = "Hello, TCP Server!";
    int bytes_sent = send(sock, message, static_cast<int>(strlen(message)), 0);
    std::cout << "  [3] 전송 (" << bytes_sent << " bytes): " << message << std::endl;

    char buffer[1024];
    int bytes_recv = recv(sock, buffer, sizeof(buffer) - 1, 0);
    if (bytes_recv > 0) {
        buffer[bytes_recv] = '\0';
        std::cout << "  [4] 수신 (" << bytes_recv << " bytes): " << buffer << std::endl;
    }

    // 4. 종료 (여기서 4-way teardown 발생!)
    CLOSE_SOCKET(sock);
    SOCKET_CLEANUP();
    std::cout << "  클라이언트 종료" << std::endl;
}

// ════════════════════════════════════════════════════════════════════
//  UDP 에코 서버
// ════════════════════════════════════════════════════════════════════
//
//  TCP와의 차이:
//  - listen(), accept() 없음! (연결 개념 없으므로)
//  - recvfrom()/sendto() 사용 (상대 주소를 매번 지정)
//  - 3-way handshake 없음 → 바로 데이터 전송!

void run_udp_echo_server(uint16_t port) {
    std::cout << "\n  ── UDP 에코 서버 시작 (포트: " << port << ") ──" << std::endl;

    SOCKET_INIT();

    // 1. 소켓 생성 (SOCK_DGRAM = UDP)
    SOCKET sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock == INVALID_SOCKET) {
        std::cerr << "  ✗ 소켓 생성 실패" << std::endl;
        SOCKET_CLEANUP();
        return;
    }
    std::cout << "  [1] 소켓 생성 완료 (UDP)" << std::endl;

    // 2. 바인딩
    struct sockaddr_in server_addr = {};
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);

    if (bind(sock, reinterpret_cast<struct sockaddr*>(&server_addr),
             sizeof(server_addr)) == SOCKET_ERROR) {
        std::cerr << "  ✗ 바인딩 실패" << std::endl;
        CLOSE_SOCKET(sock);
        SOCKET_CLEANUP();
        return;
    }
    std::cout << "  [2] 바인딩 완료" << std::endl;
    std::cout << "      대기 중... (UDP는 listen/accept 불필요!)" << std::endl;

    // 3. 수신 및 에코 (연결 없이 바로!)
    char buffer[1024];
    struct sockaddr_in client_addr = {};
    socklen_t client_len = sizeof(client_addr);

    int bytes_recv = recvfrom(sock, buffer, sizeof(buffer) - 1, 0,
                              reinterpret_cast<struct sockaddr*>(&client_addr),
                              &client_len);
    if (bytes_recv > 0) {
        buffer[bytes_recv] = '\0';
        char client_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, sizeof(client_ip));

        std::cout << "  수신 from " << client_ip << ":"
                  << ntohs(client_addr.sin_port) << " → \"" << buffer << "\"" << std::endl;

        // 에코: 보낸 사람에게 그대로 돌려보냄
        sendto(sock, buffer, bytes_recv, 0,
               reinterpret_cast<struct sockaddr*>(&client_addr), client_len);
        std::cout << "  에코 전송 완료" << std::endl;
    }

    CLOSE_SOCKET(sock);
    SOCKET_CLEANUP();
    std::cout << "  서버 종료" << std::endl;
}

// ════════════════════════════════════════════════════════════════════
//  UDP 에코 클라이언트
// ════════════════════════════════════════════════════════════════════

void run_udp_echo_client(const char* server_ip, uint16_t port) {
    std::cout << "\n  ── UDP 에코 클라이언트 시작 ──" << std::endl;

    SOCKET_INIT();

    // 1. 소켓 생성
    SOCKET sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock == INVALID_SOCKET) {
        std::cerr << "  ✗ 소켓 생성 실패" << std::endl;
        SOCKET_CLEANUP();
        return;
    }

    // 2. 서버 주소 설정 (★ connect() 불필요!)
    struct sockaddr_in server_addr = {};
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    inet_pton(AF_INET, server_ip, &server_addr.sin_addr);

    // 3. 데이터 전송 (바로! 핸드셰이크 없이!)
    const char* message = "Hello, UDP Server!";
    sendto(sock, message, static_cast<int>(strlen(message)), 0,
           reinterpret_cast<struct sockaddr*>(&server_addr), sizeof(server_addr));
    std::cout << "  전송: \"" << message << "\"" << std::endl;

    // 4. 응답 수신
    char buffer[1024];
    struct sockaddr_in from_addr = {};
    socklen_t from_len = sizeof(from_addr);
    int bytes_recv = recvfrom(sock, buffer, sizeof(buffer) - 1, 0,
                              reinterpret_cast<struct sockaddr*>(&from_addr),
                              &from_len);
    if (bytes_recv > 0) {
        buffer[bytes_recv] = '\0';
        std::cout << "  수신: \"" << buffer << "\"" << std::endl;
    }

    CLOSE_SOCKET(sock);
    SOCKET_CLEANUP();
    std::cout << "  클라이언트 종료" << std::endl;
}

// ════════════════════════════════════════════════════════════════════
//  소켓 API 흐름 비교 (TCP vs UDP)
// ════════════════════════════════════════════════════════════════════

void print_socket_api_comparison() {
    std::cout << R"(
  ┌─────────────────────────────────────────────────────────────┐
  │           소켓 API 흐름 비교: TCP vs UDP                     │
  ├──────────────────────────┬──────────────────────────────────┤
  │        TCP 서버           │         UDP 서버                 │
  ├──────────────────────────┼──────────────────────────────────┤
  │  socket(SOCK_STREAM)     │  socket(SOCK_DGRAM)             │
  │         ↓                │         ↓                        │
  │  bind()                  │  bind()                          │
  │         ↓                │         ↓                        │
  │  listen()                │  (listen 불필요!)                │
  │         ↓                │         ↓                        │
  │  accept() ← 3way        │  recvfrom() ← 바로 수신!        │
  │         ↓   handshake    │         ↓                        │
  │  recv() / send()         │  sendto() ← 바로 응답!          │
  │         ↓                │         ↓                        │
  │  close() ← 4way         │  close() ← 그냥 닫기            │
  │            teardown      │                                  │
  ├──────────────────────────┼──────────────────────────────────┤
  │        TCP 클라이언트     │         UDP 클라이언트            │
  ├──────────────────────────┼──────────────────────────────────┤
  │  socket(SOCK_STREAM)     │  socket(SOCK_DGRAM)             │
  │         ↓                │         ↓                        │
  │  connect() ← 3way       │  (connect 불필요!)               │
  │         ↓   handshake    │         ↓                        │
  │  send() / recv()         │  sendto() ← 바로 전송!          │
  │         ↓                │         ↓                        │
  │  close() ← 4way         │  recvfrom() ← 응답 수신         │
  │            teardown      │         ↓                        │
  │                          │  close()                         │
  └──────────────────────────┴──────────────────────────────────┘
)" << std::endl;
}

// ════════════════════════════════════════════════════════════════════
//  메인 함수
// ════════════════════════════════════════════════════════════════════

int main(int argc, char* argv[]) {
    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;
    std::cout << "  TCP/UDP 완전 정복 - 전송 계층 프로토콜" << std::endl;
    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  명령행 인자로 서버/클라이언트 모드 선택
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if (argc > 1) {
        std::string mode = argv[1];

        // TCP 서버 모드
        if (mode == "tcp-server") {
            uint16_t port = (argc > 2) ? std::stoi(argv[2]) : 9000;
            run_tcp_echo_server(port);
            return 0;
        }
        // TCP 클라이언트 모드
        else if (mode == "tcp-client") {
            const char* ip = (argc > 2) ? argv[2] : "127.0.0.1";
            uint16_t port = (argc > 3) ? std::stoi(argv[3]) : 9000;
            run_tcp_echo_client(ip, port);
            return 0;
        }
        // UDP 서버 모드
        else if (mode == "udp-server") {
            uint16_t port = (argc > 2) ? std::stoi(argv[2]) : 9001;
            run_udp_echo_server(port);
            return 0;
        }
        // UDP 클라이언트 모드
        else if (mode == "udp-client") {
            const char* ip = (argc > 2) ? argv[2] : "127.0.0.1";
            uint16_t port = (argc > 3) ? std::stoi(argv[3]) : 9001;
            run_udp_echo_client(ip, port);
            return 0;
        }
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  인자 없이 실행하면 학습 모드
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    std::cout << R"(
  ┌───────────────────────────────────────────────────────┐
  │  사용법:                                               │
  │    ./tcp_udp tcp-server [port]      TCP 에코 서버     │
  │    ./tcp_udp tcp-client [ip] [port] TCP 에코 클라이언트│
  │    ./tcp_udp udp-server [port]      UDP 에코 서버     │
  │    ./tcp_udp udp-client [ip] [port] UDP 에코 클라이언트│
  │                                                        │
  │  예시 (2개 터미널 사용):                               │
  │    터미널1: ./tcp_udp tcp-server 9000                  │
  │    터미널2: ./tcp_udp tcp-client 127.0.0.1 9000        │
  └───────────────────────────────────────────────────────┘
)" << std::endl;

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  1. TCP 헤더 구조 분석
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  1. 헤더 크기 비교" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    std::cout << "\n  TCP 헤더: " << sizeof(TCPHeader) << " bytes (최소, 옵션 별도)" << std::endl;
    std::cout << "  UDP 헤더: " << sizeof(UDPHeader) << " bytes (고정)" << std::endl;
    std::cout << "\n  ★ UDP가 " << sizeof(TCPHeader) - sizeof(UDPHeader)
              << " bytes 더 작음 → 오버헤드 적음 → 더 빠름!" << std::endl;

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  2. TCP 3-way Handshake 시뮬레이션
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  2. TCP 3-way Handshake 시뮬레이션" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    simulate_tcp_handshake();

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  3. TCP 4-way Teardown 시뮬레이션
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  3. TCP 4-way Teardown 시뮬레이션" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    simulate_tcp_teardown();

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  4. 슬라이딩 윈도우 시뮬레이션
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  4. 슬라이딩 윈도우 시뮬레이션" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    SlidingWindowSimulator sw(4, 10);
    sw.simulate();

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  5. 혼잡 제어 시뮬레이션
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  5. 혼잡 제어 시뮬레이션 (Slow Start + Congestion Avoidance)" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    CongestionControlSimulator cc(16.0);
    cc.simulate(15, 10);  // 15라운드, 10번째에서 패킷 손실

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  6. 소켓 API 흐름 비교
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  6. 소켓 API 흐름 비교" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    print_socket_api_comparison();

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  7. TCP 플래그 분석
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  7. TCP 플래그 해석" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    struct FlagTest {
        std::string name;
        uint8_t flags;
    };

    std::vector<FlagTest> flag_tests = {
        {"연결 요청",       TCPFlags::SYN},
        {"연결 수락",       TCPFlags::SYN | TCPFlags::ACK},
        {"데이터 전송",     TCPFlags::ACK | TCPFlags::PSH},
        {"연결 종료 요청",  TCPFlags::FIN | TCPFlags::ACK},
        {"연결 강제 리셋",  TCPFlags::RST},
        {"긴급 데이터",     TCPFlags::URG | TCPFlags::ACK},
    };

    for (const auto& test : flag_tests) {
        std::cout << "  " << std::setw(18) << std::left << test.name
                  << " → flags=0x" << std::hex << std::setw(2) << std::setfill('0')
                  << static_cast<int>(test.flags) << std::dec << std::setfill(' ')
                  << " [" << flags_to_string(test.flags) << "]" << std::endl;
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  정리
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  정리: TCP/UDP 핵심 요약" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    std::cout << R"(
  ★ 기억해야 할 핵심:

  1. TCP = 신뢰성 (3-way handshake, 재전송, 순서 보장)
  2. UDP = 속도 (연결 없음, 재전송 없음, 순서 미보장)
  3. 포트 번호: 0~65535 (0~1023은 Well-Known 포트)
  4. 흐름 제어: 윈도우 크기로 수신측 과부하 방지
  5. 혼잡 제어: Slow Start → Congestion Avoidance

  ★ 소켓 프로그래밍 핵심:
  - TCP: socket→bind→listen→accept→recv/send→close
  - UDP: socket→bind→recvfrom/sendto→close
  - Windows: WSAStartup/WSACleanup 필수!
  - 바이트 순서: htons/htonl (Host→Network)

  ★ 실무 팁:
  - SO_REUSEADDR: TIME_WAIT 상태의 포트 재사용
  - 비동기 I/O: select, poll, epoll(Linux), IOCP(Windows)
  - Keep-Alive: 연결 유지 확인 (idle timeout 방지)
)" << std::endl;

    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;
    std::cout << "  TCP/UDP 학습 완료!" << std::endl;
    std::cout << "  다음: 04_dns_system (DNS 시스템)" << std::endl;
    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;

    return 0;
}
