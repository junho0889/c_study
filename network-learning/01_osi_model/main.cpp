/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  네트워크 학습 01단계: OSI 7계층 완전 정복
  ─────────────────────────────────────────────────
  Physical, Data Link, Network, Transport,
  Session, Presentation, Application

  ■ 컴파일 방법:
      g++ -std=c++17 -Wall -lws2_32 -o osi_model main.cpp

  ■ 이 파일을 배우면 할 수 있는 것:
      - 네트워크가 어떻게 계층별로 동작하는지 이해
      - 각 계층의 역할과 장비 구분
      - 데이터가 어떻게 캡슐화(encapsulation) 되는지 파악
      - C++ struct로 각 계층 헤더를 직접 구현

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#include <iostream>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <iomanip>
#include <sstream>
#include <array>

// ┌───────────────────────────────────────────────────────────────────┐
// │  ★ 주의: 이 파일은 네트워크 개념 학습용입니다.                    │
// │  실제 네트워크 프로그래밍은 03_tcp_udp, 05_http_protocol에서!     │
// │  여기서는 OSI 모델의 "구조"와 "원리"에 집중합니다.                │
// └───────────────────────────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  택배 비유로 이해하는 OSI 7계층 (전체 흐름)
// ════════════════════════════════════════════════════════════════════
//
//  당신이 친구에게 편지를 보낸다고 상상해보세요:
//
//  [7] Application    = 편지 내용을 작성 ("안녕! 잘 지내?")
//  [6] Presentation   = 편지를 한국어→영어 번역 + 암호화
//  [5] Session        = 대화 시작/끝 관리 ("편지 주고받기 시작!")
//  [4] Transport      = 편지에 발신/수신 전화번호 적기 (포트)
//  [3] Network        = 봉투에 발신/수신 주소 적기 (IP)
//  [2] Data Link      = 택배 송장에 현재→다음 중계소 적기 (MAC)
//  [1] Physical       = 실제 택배 트럭이 도로를 달림 (전기 신호)
//
//  ┌─────────────────────────────────────────────────┐
//  │          데이터 캡슐화 과정 (Encapsulation)      │
//  │                                                  │
//  │  Application:  [       데이터       ]            │
//  │  Presentation: [  변환된 데이터     ]            │
//  │  Session:      [  세션+데이터       ]            │
//  │  Transport:    [TCP헤더|  세그먼트  ]            │
//  │  Network:      [IP헤더|TCP|세그먼트 ]            │
//  │  Data Link:    [MAC|IP|TCP|세그먼트|FCS]         │
//  │  Physical:     01101001110100101...  (비트)      │
//  │                                                  │
//  │  ★ 보내는 쪽: 위→아래 (헤더 추가)               │
//  │  ★ 받는 쪽:   아래→위 (헤더 제거)               │
//  └─────────────────────────────────────────────────┘
//

// ════════════════════════════════════════════════════════════════════
//  1계층: Physical Layer (물리 계층) - "도로와 트럭"
// ════════════════════════════════════════════════════════════════════
//
//  ┌───────────────────────────────────────────────────────────────┐
//  │  역할: 비트(0, 1)를 전기 신호/광 신호/전파로 변환하여 전송    │
//  │                                                               │
//  │  비유: 택배를 운반하는 "도로"와 "트럭"                        │
//  │        - 케이블 = 도로                                        │
//  │        - 전기 신호 = 트럭에 실린 화물                         │
//  │        - 허브/리피터 = 신호를 증폭하는 중계기                 │
//  │                                                               │
//  │  주요 장비:                                                   │
//  │    - 허브 (Hub): 신호를 모든 포트로 복사 (바보 같은 장비)     │
//  │    - 리피터 (Repeater): 약해진 신호를 증폭                    │
//  │    - 케이블: UTP, STP, 광섬유, 동축 케이블                    │
//  │                                                               │
//  │  전송 단위: 비트 (Bit) - 0 또는 1                             │
//  └───────────────────────────────────────────────────────────────┘
//
//  케이블 종류 비교:
//
//  ┌──────────────┬────────────┬────────────┬────────────────────┐
//  │   케이블      │ 최대 거리  │   속도     │    특징             │
//  ├──────────────┼────────────┼────────────┼────────────────────┤
//  │ UTP Cat5e    │  100m      │ 1 Gbps     │ 가장 흔함, 저렴     │
//  │ UTP Cat6     │  55-100m   │ 10 Gbps    │ 데이터센터 표준     │
//  │ 광섬유 싱글  │  40km+     │ 100 Gbps+  │ 장거리, 비쌈       │
//  │ 광섬유 멀티  │  2km       │ 10 Gbps    │ 건물 내부           │
//  │ 동축 케이블  │  500m      │ 10 Mbps    │ 구식, TV 케이블     │
//  └──────────────┴────────────┴────────────┴────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  2계층: Data Link Layer (데이터 링크 계층) - "택배 송장"
// ════════════════════════════════════════════════════════════════════
//
//  ┌───────────────────────────────────────────────────────────────┐
//  │  역할: 같은 네트워크(LAN) 안에서 프레임 단위로 데이터 전송    │
//  │                                                               │
//  │  비유: 택배 송장 - "현재 중계소 → 다음 중계소" 주소           │
//  │        최종 목적지가 아니라 "바로 다음 경유지"만 적음!        │
//  │                                                               │
//  │  주요 장비:                                                   │
//  │    - 스위치 (Switch): MAC 주소 보고 해당 포트로만 전달        │
//  │    - 브리지 (Bridge): 두 네트워크 세그먼트 연결               │
//  │                                                               │
//  │  주요 프로토콜:                                               │
//  │    - ARP: IP → MAC 주소 변환 ("이 IP 누구꺼야?")             │
//  │    - Ethernet: LAN의 표준 프로토콜                            │
//  │                                                               │
//  │  전송 단위: 프레임 (Frame)                                    │
//  │                                                               │
//  │  MAC 주소: 48비트, 장비 고유 번호 (주민등록번호 같은 것)      │
//  │    예: AA:BB:CC:DD:EE:FF                                      │
//  └───────────────────────────────────────────────────────────────┘

// ── 이더넷 프레임 구조 ──
//
//  ┌──────────┬──────────┬──────┬─────────────────┬─────┐
//  │ 목적지   │ 출발지   │ 타입 │     데이터       │ FCS │
//  │ MAC 주소 │ MAC 주소 │ 2B   │  46~1500 bytes  │ 4B  │
//  │ 6 bytes  │ 6 bytes  │      │                 │     │
//  └──────────┴──────────┴──────┴─────────────────┴─────┘
//        │          │       │          │              │
//   누구에게?  누가보냄? IP인지?   실제내용    오류검증용

// ★ ARP (Address Resolution Protocol) 동작 과정:
//
//  PC-A (192.168.1.10, MAC: AA:AA)
//    │
//    ├── 1. "192.168.1.20의 MAC 주소가 뭐야?" (브로드캐스트)
//    │       → 같은 네트워크의 모든 장비에게 물어봄
//    │
//    │   PC-B (192.168.1.20, MAC: BB:BB)
//    │     │
//    │     └── 2. "나야! MAC 주소는 BB:BB야!" (유니캐스트 응답)
//    │
//    └── 3. ARP 테이블에 저장: 192.168.1.20 → BB:BB
//            (다음부터는 물어볼 필요 없음)

// ── 이더넷 프레임 헤더 구조체 ──
#pragma pack(push, 1)  // 패딩 없이 메모리에 딱 맞게 배치
struct EthernetHeader {
    uint8_t  dest_mac[6];    // 목적지 MAC 주소 (6바이트)
    uint8_t  src_mac[6];     // 출발지 MAC 주소 (6바이트)
    uint16_t ether_type;     // 상위 프로토콜 타입 (0x0800 = IPv4)
    // ★ 총 14바이트 - 모든 이더넷 프레임의 시작 부분
};
#pragma pack(pop)

// ════════════════════════════════════════════════════════════════════
//  3계층: Network Layer (네트워크 계층) - "봉투의 주소"
// ════════════════════════════════════════════════════════════════════
//
//  ┌───────────────────────────────────────────────────────────────┐
//  │  역할: 서로 다른 네트워크 간 패킷 전달 (라우팅)               │
//  │                                                               │
//  │  비유: 편지 봉투에 적는 "최종 목적지 주소"                    │
//  │        택배 기사는 봉투 주소를 보고 어느 도시로 보낼지 결정    │
//  │                                                               │
//  │  주요 장비:                                                   │
//  │    - 라우터 (Router): 최적 경로 찾아 패킷 전달                │
//  │    - L3 스위치: 스위치+라우터 기능 합친 것                    │
//  │                                                               │
//  │  주요 프로토콜:                                               │
//  │    - IP (Internet Protocol): 주소 지정 + 라우팅               │
//  │    - ICMP: 네트워크 진단 (ping이 이것!)                       │
//  │    - IGMP: 멀티캐스트 관리                                    │
//  │                                                               │
//  │  전송 단위: 패킷 (Packet)                                     │
//  └───────────────────────────────────────────────────────────────┘

// ── IPv4 헤더 구조 (20~60 바이트) ──
//
//   0                   1                   2                   3
//   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
//  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//  |Version|  IHL  |Type of Service|         Total Length          |
//  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//  |         Identification        |Flags|      Fragment Offset    |
//  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//  |  Time to Live |    Protocol   |         Header Checksum       |
//  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//  |                       Source Address                          |
//  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//  |                    Destination Address                        |
//  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//  |                    Options (if IHL > 5)                       |
//  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

#pragma pack(push, 1)
struct IPv4Header {
    // ★ 비트필드 - 바이트 안에서 비트 단위로 필드를 나눔
    uint8_t  ihl : 4;           // 헤더 길이 (보통 5 = 20바이트)
    uint8_t  version : 4;       // IP 버전 (4 = IPv4)
    uint8_t  tos;               // 서비스 유형 (QoS용)
    uint16_t total_length;      // 전체 패킷 크기
    uint16_t identification;    // 분할된 패킷 식별 번호
    uint16_t flags_fragment;    // 플래그(3비트) + 조각 오프셋(13비트)
    uint8_t  ttl;               // Time To Live (라우터 통과 시 -1, 0이면 폐기)
    uint8_t  protocol;          // 상위 프로토콜 (6=TCP, 17=UDP)
    uint16_t header_checksum;   // 헤더 무결성 검사
    uint32_t src_ip;            // 출발지 IP 주소 (32비트)
    uint32_t dst_ip;            // 목적지 IP 주소 (32비트)
    // ★ 총 20바이트 (옵션 없을 때)
};
#pragma pack(pop)

// ── ICMP 동작 (ping의 원리) ──
//
//  내 PC (192.168.1.10)          서버 (8.8.8.8)
//     │                              │
//     │── ICMP Echo Request ────────>│  "살아있니?"
//     │                              │
//     │<── ICMP Echo Reply ─────────│  "응, 살아있어!"
//     │                              │
//     │  RTT = 15ms (왕복 시간)     │
//
//  ★ TTL (Time To Live) 원리:
//     TTL=64로 시작 → 라우터 지날 때마다 -1
//     0이 되면 패킷 폐기 + ICMP "Time Exceeded" 전송
//     → 이 원리를 이용한 것이 traceroute!

// ════════════════════════════════════════════════════════════════════
//  4계층: Transport Layer (전송 계층) - "전화번호 (포트)"
// ════════════════════════════════════════════════════════════════════
//
//  ┌───────────────────────────────────────────────────────────────┐
//  │  역할: 프로세스 간 통신, 데이터 신뢰성 보장                   │
//  │                                                               │
//  │  비유: 편지에 적는 "발신자 전화번호, 수신자 전화번호"         │
//  │        IP만으로는 "어떤 프로그램"에게 보내는지 모름!           │
//  │        포트 번호가 있어야 "웹 브라우저"인지 "카카오톡"인지    │
//  │        구분 가능                                              │
//  │                                                               │
//  │  주요 프로토콜:                                               │
//  │    - TCP: 신뢰성 있는 연결 (전화 통화처럼)                    │
//  │    - UDP: 빠르지만 신뢰성 없음 (편지처럼)                     │
//  │                                                               │
//  │  전송 단위: 세그먼트 (TCP) / 데이터그램 (UDP)                 │
//  └───────────────────────────────────────────────────────────────┘
//
//  주요 포트 번호:
//  ┌──────────┬────────────────┬──────────────────────┐
//  │ 포트     │ 프로토콜        │ 설명                  │
//  ├──────────┼────────────────┼──────────────────────┤
//  │ 20, 21   │ FTP            │ 파일 전송              │
//  │ 22       │ SSH            │ 보안 원격 접속         │
//  │ 23       │ Telnet         │ 원격 접속 (비보안)     │
//  │ 25       │ SMTP           │ 메일 보내기            │
//  │ 53       │ DNS            │ 도메인→IP 변환        │
//  │ 80       │ HTTP           │ 웹 (비보안)            │
//  │ 443      │ HTTPS          │ 웹 (보안)              │
//  │ 3306     │ MySQL          │ 데이터베이스           │
//  │ 3389     │ RDP            │ 윈도우 원격 데스크톱   │
//  │ 5432     │ PostgreSQL     │ 데이터베이스           │
//  │ 6379     │ Redis          │ 캐시 서버              │
//  │ 8080     │ HTTP Alt       │ 개발용 웹 서버         │
//  └──────────┴────────────────┴──────────────────────┘

// ── TCP 헤더 구조체 (20 바이트, 옵션 제외) ──
#pragma pack(push, 1)
struct TCPHeader {
    uint16_t src_port;       // 출발지 포트 (0~65535)
    uint16_t dst_port;       // 목적지 포트 (0~65535)
    uint32_t seq_num;        // 시퀀스 번호 (바이트 단위 순서)
    uint32_t ack_num;        // 응답 번호 ("여기까지 잘 받았어")
    uint8_t  data_offset : 4;// 헤더 길이 (4바이트 단위)
    uint8_t  reserved : 3;   // 예약 (사용 안 함)
    uint8_t  ns : 1;         // ECN-nonce
    uint8_t  flags;          // CWR,ECE,URG,ACK,PSH,RST,SYN,FIN
    uint16_t window_size;    // 수신 버퍼 크기 (흐름 제어)
    uint16_t checksum;       // 무결성 검사
    uint16_t urgent_ptr;     // 긴급 데이터 포인터
    // ★ 총 20바이트 - 옵션은 별도 추가 가능
};
#pragma pack(pop)

// ── UDP 헤더 구조체 (단 8바이트! 초간단!) ──
#pragma pack(push, 1)
struct UDPHeader {
    uint16_t src_port;       // 출발지 포트
    uint16_t dst_port;       // 목적지 포트
    uint16_t length;         // 헤더 + 데이터 길이
    uint16_t checksum;       // 무결성 검사 (선택)
    // ★ 총 8바이트 - TCP보다 12바이트 적음!
    // ★ 연결 설정 없음, 순서 보장 없음, 재전송 없음
    //    → 빠르지만 신뢰성 없음 (게임, 영상 통화에 적합)
};
#pragma pack(pop)

// ════════════════════════════════════════════════════════════════════
//  5계층: Session Layer (세션 계층) - "대화 관리자"
// ════════════════════════════════════════════════════════════════════
//
//  ┌───────────────────────────────────────────────────────────────┐
//  │  역할: 통신 세션의 시작, 유지, 종료를 관리                    │
//  │                                                               │
//  │  비유: 전화 통화의 "여보세요?"(시작) ~ "끊을게요"(종료)       │
//  │        대화 중 끊기면 다시 이어서 대화할 수 있게 관리         │
//  │                                                               │
//  │  주요 프로토콜:                                               │
//  │    - NetBIOS: Windows 네트워크 이름 서비스                     │
//  │    - RPC: 원격 프로시저 호출 (다른 컴퓨터의 함수 실행)        │
//  │    - PPTP: 포인트-투-포인트 터널링                             │
//  │                                                               │
//  │  ★ 실제 TCP/IP에서는 4, 5, 6, 7계층이 명확히 구분되지 않음   │
//  │    OSI 모델은 "이론적" 구분, TCP/IP 모델은 "실용적" 구분      │
//  └───────────────────────────────────────────────────────────────┘
//
//  세션의 3가지 모드:
//    - 전이중 (Full Duplex): 양쪽 동시 통신 (전화 통화)
//    - 반이중 (Half Duplex): 한 번에 한쪽만 (무전기 - 오버!)
//    - 단방향 (Simplex): 한쪽만 보냄 (TV 방송)

// ════════════════════════════════════════════════════════════════════
//  6계층: Presentation Layer (표현 계층) - "통역사"
// ════════════════════════════════════════════════════════════════════
//
//  ┌───────────────────────────────────────────────────────────────┐
//  │  역할: 데이터 형식 변환, 암호화, 압축                         │
//  │                                                               │
//  │  비유: 편지를 보내기 전에 번역하고 암호화하는 "통역사"        │
//  │        상대가 이해할 수 있는 형식으로 변환                    │
//  │                                                               │
//  │  주요 기능:                                                   │
//  │    - 인코딩: ASCII, UTF-8, EBCDIC 등 변환                    │
//  │    - 암호화: SSL/TLS (HTTPS의 핵심!)                          │
//  │    - 압축: 데이터 크기 줄이기 (gzip 등)                      │
//  │    - 직렬화: JSON, XML, Protocol Buffers 등                   │
//  │                                                               │
//  │  ★ 실무에서 가장 중요한 것: TLS 암호화!                      │
//  │    HTTP → HTTPS 전환의 핵심이 바로 이 계층                   │
//  └───────────────────────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  7계층: Application Layer (응용 계층) - "사용자 인터페이스"
// ════════════════════════════════════════════════════════════════════
//
//  ┌───────────────────────────────────────────────────────────────┐
//  │  역할: 사용자와 직접 상호작용하는 네트워크 서비스              │
//  │                                                               │
//  │  비유: "편지를 쓰는 사람" - 내용 자체에 집중                  │
//  │        아래 계층은 배달 과정이고, 여기는 편지 내용            │
//  │                                                               │
//  │  주요 프로토콜:                                               │
//  │    - HTTP/HTTPS: 웹 페이지                                    │
//  │    - DNS: 도메인 이름 → IP 주소 변환                         │
//  │    - FTP: 파일 전송                                           │
//  │    - SMTP/POP3/IMAP: 이메일                                   │
//  │    - SSH: 보안 원격 접속                                      │
//  │    - DHCP: IP 주소 자동 할당                                  │
//  │    - SNMP: 네트워크 장비 관리                                 │
//  └───────────────────────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  OSI 7계층 vs TCP/IP 4계층 비교
// ════════════════════════════════════════════════════════════════════
//
//  ┌──────────────────────┬───────────────────────┐
//  │    OSI 7계층          │   TCP/IP 4계층         │
//  ├──────────────────────┼───────────────────────┤
//  │ 7. Application       │                       │
//  │ 6. Presentation      │  4. Application       │
//  │ 5. Session           │     (HTTP,DNS,FTP)    │
//  ├──────────────────────┼───────────────────────┤
//  │ 4. Transport         │  3. Transport         │
//  │                      │     (TCP, UDP)        │
//  ├──────────────────────┼───────────────────────┤
//  │ 3. Network           │  2. Internet          │
//  │                      │     (IP, ICMP)        │
//  ├──────────────────────┼───────────────────────┤
//  │ 2. Data Link         │  1. Network Access    │
//  │ 1. Physical          │     (Ethernet, WiFi)  │
//  └──────────────────────┴───────────────────────┘
//
//  ★ 실무에서는 TCP/IP 4계층 모델을 주로 사용
//  ★ OSI 7계층은 네트워크 이론과 트러블슈팅에서 참조

// ════════════════════════════════════════════════════════════════════
//  각 계층에서 사용하는 장비 비교표
// ════════════════════════════════════════════════════════════════════
//
//  ┌────────┬────────────┬──────────┬─────────────────────────────┐
//  │ 계층   │   장비      │ 주소     │ 특징                        │
//  ├────────┼────────────┼──────────┼─────────────────────────────┤
//  │ L1     │ 허브,리피터 │ 없음     │ 신호 복사/증폭만 함         │
//  │ L2     │ 스위치     │ MAC 주소 │ 같은 LAN 내 프레임 전달     │
//  │ L3     │ 라우터     │ IP 주소  │ 다른 네트워크 간 패킷 전달  │
//  │ L4     │ 방화벽     │ 포트번호 │ 포트 기반 필터링            │
//  │ L7     │ WAF,LB     │ URL 등   │ 콘텐츠 기반 처리            │
//  └────────┴────────────┴──────────┴─────────────────────────────┘
//
//  ★ 허브 vs 스위치 차이점:
//
//  [허브]  A→허브→B,C,D  (모든 포트로 복사 = 비효율적)
//  [스위치] A→스위치→B    (MAC 테이블로 목적지만 전달 = 효율적)

// ════════════════════════════════════════════════════════════════════
//  유틸리티 함수들
// ════════════════════════════════════════════════════════════════════

// MAC 주소를 문자열로 변환하는 함수
// 6바이트 배열 → "AA:BB:CC:DD:EE:FF" 형태
std::string mac_to_string(const uint8_t mac[6]) {
    std::ostringstream oss;
    for (int i = 0; i < 6; i++) {
        if (i > 0) oss << ":";
        oss << std::hex << std::setw(2) << std::setfill('0')
            << static_cast<int>(mac[i]);
    }
    return oss.str();
}

// IP 주소를 문자열로 변환하는 함수
// uint32_t → "192.168.1.1" 형태
std::string ip_to_string(uint32_t ip) {
    return std::to_string((ip >> 24) & 0xFF) + "." +
           std::to_string((ip >> 16) & 0xFF) + "." +
           std::to_string((ip >> 8) & 0xFF) + "." +
           std::to_string(ip & 0xFF);
}

// 문자열에서 IP 주소를 uint32_t로 변환
// "192.168.1.1" → uint32_t
uint32_t string_to_ip(const std::string& ip_str) {
    uint32_t result = 0;
    uint32_t octet = 0;
    int shift = 24;

    for (char c : ip_str) {
        if (c == '.') {
            result |= (octet << shift);
            shift -= 8;
            octet = 0;
        } else {
            octet = octet * 10 + (c - '0');
        }
    }
    result |= (octet << shift);  // 마지막 옥텟 처리
    return result;
}

// 바이트 배열을 16진수로 출력하는 함수
void print_hex_dump(const uint8_t* data, size_t length) {
    for (size_t i = 0; i < length; i++) {
        std::cout << std::hex << std::setw(2) << std::setfill('0')
                  << static_cast<int>(data[i]) << " ";
        if ((i + 1) % 16 == 0) std::cout << std::endl;
    }
    if (length % 16 != 0) std::cout << std::endl;
    std::cout << std::dec;  // 다시 10진수 모드로 복원
}

// ════════════════════════════════════════════════════════════════════
//  ARP 테이블 시뮬레이션
// ════════════════════════════════════════════════════════════════════

// ARP 테이블 엔트리 - IP와 MAC의 매핑
struct ARPEntry {
    uint32_t ip_address;                // IP 주소
    uint8_t  mac_address[6];            // MAC 주소
    std::string interface_name;         // 네트워크 인터페이스 이름
    int      ttl;                       // 캐시 유효 시간 (초)

    // 엔트리 정보 출력
    void print() const {
        std::cout << "  " << ip_to_string(ip_address)
                  << "\t→ " << mac_to_string(mac_address)
                  << "\t[" << interface_name << "]"
                  << "\tTTL=" << ttl << "s" << std::endl;
    }
};

// 간단한 ARP 테이블 클래스
class ARPTable {
private:
    std::vector<ARPEntry> entries_;

public:
    // ARP 엔트리 추가 (학습)
    void add_entry(uint32_t ip, const uint8_t mac[6],
                   const std::string& iface, int ttl = 300) {
        ARPEntry entry;
        entry.ip_address = ip;
        std::memcpy(entry.mac_address, mac, 6);
        entry.interface_name = iface;
        entry.ttl = ttl;
        entries_.push_back(entry);
    }

    // IP로 MAC 주소 찾기
    bool lookup(uint32_t ip, uint8_t out_mac[6]) const {
        for (const auto& entry : entries_) {
            if (entry.ip_address == ip) {
                std::memcpy(out_mac, entry.mac_address, 6);
                return true;
            }
        }
        return false;  // 없으면 ARP Request 보내야 함!
    }

    // 테이블 전체 출력
    void print_table() const {
        std::cout << "\n  ┌─────────────────────────────────────────────┐" << std::endl;
        std::cout << "  │            ARP 테이블 (ARP Table)            │" << std::endl;
        std::cout << "  ├─────────────────────────────────────────────┤" << std::endl;
        for (const auto& entry : entries_) {
            entry.print();
        }
        std::cout << "  └─────────────────────────────────────────────┘" << std::endl;
    }
};

// ════════════════════════════════════════════════════════════════════
//  패킷 캡슐화 시뮬레이션
// ════════════════════════════════════════════════════════════════════

// 시뮬레이션용 패킷 구조체
// 실제 패킷처럼 각 계층의 헤더를 순서대로 쌓는다
struct SimulatedPacket {
    // Layer 2 - Data Link
    EthernetHeader eth_header;

    // Layer 3 - Network
    IPv4Header ip_header;

    // Layer 4 - Transport (TCP 사용)
    TCPHeader tcp_header;

    // Layer 7 - Application (간단한 데이터)
    char payload[256];
    size_t payload_length;
};

// 패킷 생성 과정을 보여주는 함수
// ★ 핵심: 상위 계층부터 하위 계층 순서로 헤더를 추가
SimulatedPacket create_packet(
    const uint8_t src_mac[6], const uint8_t dst_mac[6],
    uint32_t src_ip, uint32_t dst_ip,
    uint16_t src_port, uint16_t dst_port,
    const char* data)
{
    SimulatedPacket pkt = {};

    // ── 7계층: Application Layer - 데이터 준비 ──
    std::cout << "\n  [7] Application Layer: 데이터 준비" << std::endl;
    strncpy(pkt.payload, data, sizeof(pkt.payload) - 1);
    pkt.payload_length = strlen(pkt.payload);
    std::cout << "      데이터: \"" << pkt.payload << "\"" << std::endl;
    std::cout << "      크기: " << pkt.payload_length << " bytes" << std::endl;

    // ── 6계층: Presentation Layer - 인코딩 (여기서는 ASCII 그대로) ──
    std::cout << "\n  [6] Presentation Layer: 인코딩/암호화" << std::endl;
    std::cout << "      (이 시뮬레이션에서는 평문 그대로 전송)" << std::endl;

    // ── 5계층: Session Layer - 세션 관리 ──
    std::cout << "\n  [5] Session Layer: 세션 관리" << std::endl;
    std::cout << "      (TCP가 세션 관리를 포함하므로 별도 처리 없음)" << std::endl;

    // ── 4계층: Transport Layer - TCP 헤더 추가 ──
    std::cout << "\n  [4] Transport Layer: TCP 헤더 추가" << std::endl;
    pkt.tcp_header.src_port = src_port;
    pkt.tcp_header.dst_port = dst_port;
    pkt.tcp_header.seq_num = 1000;          // 초기 시퀀스 번호
    pkt.tcp_header.ack_num = 0;
    pkt.tcp_header.data_offset = 5;         // 20바이트 (옵션 없음)
    pkt.tcp_header.flags = 0x02;            // SYN 플래그
    pkt.tcp_header.window_size = 65535;     // 수신 윈도우 크기
    std::cout << "      출발 포트: " << src_port << std::endl;
    std::cout << "      도착 포트: " << dst_port << std::endl;
    std::cout << "      + TCP 헤더 20 bytes 추가됨" << std::endl;

    // ── 3계층: Network Layer - IP 헤더 추가 ──
    std::cout << "\n  [3] Network Layer: IP 헤더 추가" << std::endl;
    pkt.ip_header.version = 4;
    pkt.ip_header.ihl = 5;                  // 20바이트
    pkt.ip_header.ttl = 64;                 // 기본 TTL
    pkt.ip_header.protocol = 6;             // TCP
    pkt.ip_header.src_ip = src_ip;
    pkt.ip_header.dst_ip = dst_ip;
    pkt.ip_header.total_length = 20 + 20 + static_cast<uint16_t>(pkt.payload_length);
    std::cout << "      출발 IP: " << ip_to_string(src_ip) << std::endl;
    std::cout << "      도착 IP: " << ip_to_string(dst_ip) << std::endl;
    std::cout << "      TTL: " << (int)pkt.ip_header.ttl << std::endl;
    std::cout << "      + IP 헤더 20 bytes 추가됨" << std::endl;

    // ── 2계층: Data Link Layer - 이더넷 헤더 추가 ──
    std::cout << "\n  [2] Data Link Layer: Ethernet 헤더 추가" << std::endl;
    std::memcpy(pkt.eth_header.src_mac, src_mac, 6);
    std::memcpy(pkt.eth_header.dest_mac, dst_mac, 6);
    pkt.eth_header.ether_type = 0x0800;     // IPv4
    std::cout << "      출발 MAC: " << mac_to_string(src_mac) << std::endl;
    std::cout << "      도착 MAC: " << mac_to_string(dst_mac) << std::endl;
    std::cout << "      + Ethernet 헤더 14 bytes 추가됨" << std::endl;

    // ── 1계층: Physical Layer - 비트로 변환 ──
    std::cout << "\n  [1] Physical Layer: 비트 스트림으로 변환" << std::endl;
    size_t total_size = 14 + 20 + 20 + pkt.payload_length;
    std::cout << "      전체 프레임 크기: " << total_size << " bytes" << std::endl;
    std::cout << "      = " << total_size * 8 << " bits" << std::endl;
    std::cout << "      → 전기 신호로 케이블에 전송!" << std::endl;

    return pkt;
}

// ════════════════════════════════════════════════════════════════════
//  TCP 플래그 해석기
// ════════════════════════════════════════════════════════════════════

// TCP 플래그 비트 정의
// ★ flags 필드의 각 비트가 특정 의미를 가짐
namespace TCPFlags {
    constexpr uint8_t FIN = 0x01;   // 연결 종료 요청
    constexpr uint8_t SYN = 0x02;   // 연결 시작 요청
    constexpr uint8_t RST = 0x04;   // 연결 강제 리셋
    constexpr uint8_t PSH = 0x08;   // 데이터 즉시 전달
    constexpr uint8_t ACK = 0x10;   // 확인 응답
    constexpr uint8_t URG = 0x20;   // 긴급 데이터
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
//  프로토콜 번호 해석기
// ════════════════════════════════════════════════════════════════════

// IP 헤더의 protocol 필드 값에 대응하는 프로토콜 이름
std::string protocol_to_string(uint8_t protocol) {
    switch (protocol) {
        case 1:  return "ICMP";   // 핑, traceroute
        case 6:  return "TCP";    // 웹, 이메일 등
        case 17: return "UDP";    // DNS, 게임, 스트리밍
        case 41: return "IPv6";   // IPv6 터널링
        case 47: return "GRE";    // VPN 터널
        case 50: return "ESP";    // IPSec 암호화
        case 89: return "OSPF";   // 라우팅 프로토콜
        default: return "Unknown(" + std::to_string(protocol) + ")";
    }
}

// ════════════════════════════════════════════════════════════════════
//  간단한 라우팅 테이블 시뮬레이션
// ════════════════════════════════════════════════════════════════════

struct RouteEntry {
    uint32_t network;        // 네트워크 주소
    uint32_t netmask;        // 서브넷 마스크
    uint32_t gateway;        // 게이트웨이 (다음 홉)
    std::string interface_name;  // 나가는 인터페이스
    int      metric;         // 메트릭 (비용, 낮을수록 우선)

    // 이 라우트가 주어진 IP에 매칭되는지 확인
    bool matches(uint32_t dest_ip) const {
        return (dest_ip & netmask) == network;
    }

    // 엔트리 정보 출력
    void print() const {
        std::cout << "  " << ip_to_string(network)
                  << "/" << ip_to_string(netmask)
                  << " → GW " << ip_to_string(gateway)
                  << " [" << interface_name << "]"
                  << " metric=" << metric << std::endl;
    }
};

class RoutingTable {
private:
    std::vector<RouteEntry> routes_;

public:
    // 라우트 추가
    void add_route(uint32_t network, uint32_t netmask,
                   uint32_t gateway, const std::string& iface,
                   int metric = 10) {
        routes_.push_back({network, netmask, gateway, iface, metric});
    }

    // 목적지 IP에 대한 최적 경로 찾기 (Longest Prefix Match)
    // ★ 가장 구체적인(마스크가 긴) 경로를 우선 선택
    const RouteEntry* lookup(uint32_t dest_ip) const {
        const RouteEntry* best = nullptr;
        uint32_t best_mask = 0;

        for (const auto& route : routes_) {
            if (route.matches(dest_ip)) {
                // 더 구체적인 마스크(=더 긴 접두사)를 우선 선택
                if (route.netmask >= best_mask) {
                    best = &route;
                    best_mask = route.netmask;
                }
            }
        }
        return best;
    }

    // 라우팅 테이블 전체 출력
    void print_table() const {
        std::cout << "\n  ┌─────────────────────────────────────────────────────┐" << std::endl;
        std::cout << "  │              라우팅 테이블 (Routing Table)           │" << std::endl;
        std::cout << "  ├─────────────────────────────────────────────────────┤" << std::endl;
        for (const auto& route : routes_) {
            route.print();
        }
        std::cout << "  └─────────────────────────────────────────────────────┘" << std::endl;
    }
};

// ════════════════════════════════════════════════════════════════════
//  메인 함수 - 모든 개념 시연
// ════════════════════════════════════════════════════════════════════

int main() {
    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;
    std::cout << "  OSI 7계층 완전 정복 - 네트워크의 기초" << std::endl;
    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  1. 헤더 구조체 크기 확인
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  1. 각 계층 헤더 크기 확인" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    std::cout << "\n  ┌──────────────────────────────────────┐" << std::endl;
    std::cout << "  │  계층별 헤더 크기 (struct 크기)       │" << std::endl;
    std::cout << "  ├──────────────────────────────────────┤" << std::endl;
    std::cout << "  │  Ethernet Header: " << std::setw(2) << sizeof(EthernetHeader)
              << " bytes (L2)     │" << std::endl;
    std::cout << "  │  IPv4 Header:     " << std::setw(2) << sizeof(IPv4Header)
              << " bytes (L3)     │" << std::endl;
    std::cout << "  │  TCP Header:      " << std::setw(2) << sizeof(TCPHeader)
              << " bytes (L4)     │" << std::endl;
    std::cout << "  │  UDP Header:       " << std::setw(2) << sizeof(UDPHeader)
              << " bytes (L4)     │" << std::endl;
    std::cout << "  └──────────────────────────────────────┘" << std::endl;

    // ★ 오버헤드 계산
    // 1바이트 데이터를 TCP로 보내면:
    //   14(ETH) + 20(IP) + 20(TCP) + 1(DATA) = 55바이트
    //   → 데이터 1바이트 보내는데 54바이트 오버헤드!
    std::cout << "\n  ★ TCP로 1바이트 전송 시 오버헤드:" << std::endl;
    std::cout << "     ETH(14) + IP(20) + TCP(20) + DATA(1) = 55 bytes" << std::endl;
    std::cout << "     → 오버헤드 비율: 98.2%! (데이터가 겨우 1.8%)" << std::endl;
    std::cout << "     → 그래서 데이터를 모아서 보내는 것이 효율적!" << std::endl;

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  2. 패킷 캡슐화 시뮬레이션
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  2. 패킷 캡슐화 시뮬레이션" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    // 가상의 MAC 주소
    uint8_t src_mac[] = {0xAA, 0xBB, 0xCC, 0x11, 0x22, 0x33};
    uint8_t dst_mac[] = {0xDD, 0xEE, 0xFF, 0x44, 0x55, 0x66};

    // 가상의 IP 주소
    uint32_t src_ip = string_to_ip("192.168.1.10");
    uint32_t dst_ip = string_to_ip("10.0.0.50");

    // 패킷 생성 (캡슐화 과정 출력됨)
    SimulatedPacket pkt = create_packet(
        src_mac, dst_mac,
        src_ip, dst_ip,
        12345, 80,       // 출발포트, 도착포트(HTTP)
        "GET / HTTP/1.1"  // HTTP 요청 데이터
    );

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  3. ARP 테이블 시뮬레이션
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  3. ARP 테이블 시뮬레이션" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    ARPTable arp;

    // ARP 엔트리 학습 (실제로는 ARP Request/Reply로 학습)
    uint8_t mac1[] = {0x00, 0x1A, 0x2B, 0x3C, 0x4D, 0x5E};
    uint8_t mac2[] = {0x11, 0x22, 0x33, 0x44, 0x55, 0x66};
    uint8_t mac3[] = {0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF};

    arp.add_entry(string_to_ip("192.168.1.1"), mac1, "eth0", 300);
    arp.add_entry(string_to_ip("192.168.1.100"), mac2, "eth0", 120);
    arp.add_entry(string_to_ip("192.168.1.254"), mac3, "eth0", 600);

    arp.print_table();

    // ARP 조회 테스트
    uint8_t found_mac[6];
    uint32_t test_ip = string_to_ip("192.168.1.100");
    if (arp.lookup(test_ip, found_mac)) {
        std::cout << "\n  ARP 조회 성공: " << ip_to_string(test_ip)
                  << " → " << mac_to_string(found_mac) << std::endl;
    }

    test_ip = string_to_ip("192.168.1.200");
    if (!arp.lookup(test_ip, found_mac)) {
        std::cout << "  ARP 조회 실패: " << ip_to_string(test_ip)
                  << " → ARP Request 브로드캐스트 필요!" << std::endl;
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  4. 라우팅 테이블 시뮬레이션
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  4. 라우팅 테이블 시뮬레이션" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    RoutingTable rt;

    // 라우팅 엔트리 추가
    // 네트워크, 마스크, 게이트웨이, 인터페이스, 메트릭
    rt.add_route(
        string_to_ip("192.168.1.0"),     // 로컬 네트워크
        string_to_ip("255.255.255.0"),
        string_to_ip("0.0.0.0"),          // 직접 연결 (게이트웨이 없음)
        "eth0", 0
    );
    rt.add_route(
        string_to_ip("10.0.0.0"),        // 10.x.x.x 네트워크
        string_to_ip("255.0.0.0"),
        string_to_ip("192.168.1.1"),      // 게이트웨이를 통해
        "eth0", 10
    );
    rt.add_route(
        string_to_ip("0.0.0.0"),         // 기본 경로 (default route)
        string_to_ip("0.0.0.0"),
        string_to_ip("192.168.1.1"),      // 기본 게이트웨이
        "eth0", 100
    );

    rt.print_table();

    // 라우팅 조회 테스트
    std::cout << "\n  라우팅 조회 테스트:" << std::endl;

    std::vector<std::string> test_ips = {
        "192.168.1.50",   // 로컬 네트워크 → 직접 연결
        "10.0.0.100",     // 10.x 네트워크 → 게이트웨이
        "8.8.8.8",        // 구글 DNS → 기본 경로
        "172.16.0.1"      // 기타 → 기본 경로
    };

    for (const auto& ip : test_ips) {
        uint32_t dest = string_to_ip(ip);
        const RouteEntry* route = rt.lookup(dest);
        if (route) {
            std::cout << "  " << ip << " → GW "
                      << ip_to_string(route->gateway)
                      << " via " << route->interface_name << std::endl;
        }
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  5. TCP 플래그 분석
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  5. TCP 플래그 분석" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    // 3-way handshake 시뮬레이션
    std::cout << R"(
  ┌─────────────────────────────────────────────────┐
  │        TCP 3-way Handshake 시뮬레이션            │
  │                                                  │
  │   Client                           Server        │
  │     │                                │           │
  │     │── SYN (seq=100) ─────────────>│  1단계    │
  │     │                                │           │
  │     │<── SYN+ACK (seq=300,ack=101) ─│  2단계    │
  │     │                                │           │
  │     │── ACK (seq=101,ack=301) ─────>│  3단계    │
  │     │                                │           │
  │     │  ★ 연결 수립 완료! (ESTABLISHED)│          │
  └─────────────────────────────────────────────────┘
)" << std::endl;

    // 플래그 값 시연
    struct TCPFlagExample {
        std::string step;
        uint8_t flags;
        uint32_t seq;
        uint32_t ack;
    };

    std::vector<TCPFlagExample> handshake = {
        {"1. Client→Server", TCPFlags::SYN, 100, 0},
        {"2. Server→Client", TCPFlags::SYN | TCPFlags::ACK, 300, 101},
        {"3. Client→Server", TCPFlags::ACK, 101, 301},
    };

    for (const auto& step : handshake) {
        std::cout << "  " << step.step << ": "
                  << "flags=[" << flags_to_string(step.flags) << "] "
                  << "seq=" << step.seq << " ack=" << step.ack << std::endl;
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  6. 프로토콜 번호 해석
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  6. IP 헤더의 Protocol 필드 해석" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    std::vector<uint8_t> protocols = {1, 6, 17, 41, 47, 50, 89};
    for (uint8_t p : protocols) {
        std::cout << "  Protocol " << std::setw(3) << (int)p
                  << " = " << protocol_to_string(p) << std::endl;
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  7. 패킷 헥스 덤프 출력
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  7. 생성된 패킷의 헥스 덤프" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    std::cout << "\n  Ethernet Header (14 bytes):" << std::endl;
    std::cout << "  ";
    print_hex_dump(reinterpret_cast<uint8_t*>(&pkt.eth_header),
                   sizeof(EthernetHeader));

    std::cout << "\n  IPv4 Header (20 bytes):" << std::endl;
    std::cout << "  ";
    print_hex_dump(reinterpret_cast<uint8_t*>(&pkt.ip_header),
                   sizeof(IPv4Header));

    std::cout << "\n  TCP Header (20 bytes):" << std::endl;
    std::cout << "  ";
    print_hex_dump(reinterpret_cast<uint8_t*>(&pkt.tcp_header),
                   sizeof(TCPHeader));

    std::cout << "\n  Payload (" << pkt.payload_length << " bytes):" << std::endl;
    std::cout << "  ";
    print_hex_dump(reinterpret_cast<uint8_t*>(pkt.payload),
                   pkt.payload_length);

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  8. 데이터 전송 전체 흐름 요약 (택배 비유)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  8. 데이터 전송 전체 흐름 (택배 비유)" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    std::cout << R"(
  ┌─────────────────────────────────────────────────────────┐
  │  웹 브라우저에서 "www.example.com" 접속 시 벌어지는 일   │
  ├─────────────────────────────────────────────────────────┤
  │                                                         │
  │  1) DNS 조회: www.example.com → 93.184.216.34           │
  │     (전화번호부에서 주소 찾기)                           │
  │                                                         │
  │  2) TCP 3-way Handshake (연결 수립)                     │
  │     Client ──SYN──> Server                              │
  │     Client <──SYN+ACK── Server                          │
  │     Client ──ACK──> Server                              │
  │                                                         │
  │  3) HTTP 요청 (Application Layer)                       │
  │     GET / HTTP/1.1                                      │
  │     Host: www.example.com                               │
  │                                                         │
  │  4) 캡슐화 (위→아래)                                   │
  │     [ETH][IP][TCP][HTTP 데이터] → 비트 스트림           │
  │                                                         │
  │  5) 라우터들을 거쳐 서버에 도착                          │
  │     PC → 공유기 → ISP → ... → 서버                    │
  │                                                         │
  │  6) 역캡슐화 (아래→위)                                 │
  │     비트 → [ETH][IP][TCP][HTTP] → 서버 앱에 전달       │
  │                                                         │
  │  7) 서버가 HTML 응답 전송 (같은 과정 반복)              │
  │                                                         │
  │  8) TCP 4-way Teardown (연결 종료)                      │
  │     Client ──FIN──> Server                              │
  │     Client <──ACK── Server                              │
  │     Client <──FIN── Server                              │
  │     Client ──ACK──> Server                              │
  └─────────────────────────────────────────────────────────┘
)" << std::endl;

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  정리
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  정리: OSI 7계층 핵심 요약" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    std::cout << R"(
  ★ 기억해야 할 핵심:

  1. OSI 모델은 "이론", TCP/IP 모델은 "실무"
  2. 보내는 쪽: 7→1 (헤더 추가 = 캡슐화)
     받는 쪽: 1→7 (헤더 제거 = 역캡슐화)
  3. 같은 네트워크 = MAC 주소 (L2)
     다른 네트워크 = IP 주소 (L3)
  4. TCP = 신뢰성, UDP = 속도
  5. 포트 번호 = 프로그램 식별자 (L4)

  ★ 트러블슈팅 팁:
  - ping 안 됨 → L3 (IP/라우팅) 문제
  - 연결 거부 → L4 (포트/방화벽) 문제
  - 페이지 안 뜸 → L7 (HTTP/DNS) 문제
  - 케이블 뽑힘 → L1 (물리) 문제 ^^
)" << std::endl;

    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;
    std::cout << "  OSI 7계층 학습 완료!" << std::endl;
    std::cout << "  다음: 02_ip_addressing (IP 주소 체계)" << std::endl;
    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;

    return 0;
}
