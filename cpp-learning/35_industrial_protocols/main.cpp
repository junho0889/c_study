/*
=============================================================================
  C++ 학습 35단계: 산업용 프로토콜 (Modbus / CAN / OPC UA / EtherCAT / MQTT)
=============================================================================
  [학습 목표]
  1. IT 네트워크와 OT(Operational Technology) 네트워크 차이 이해
  2. Modbus RTU(시리얼) / TCP 프레임 직접 인코딩 / 디코딩
  3. CAN bus / CANopen 메시지 구조
  4. OPC UA 구조와 노드 모델 (개념 + 라이브러리 선택)
  5. EtherCAT / Profinet 실시간 산업 이더넷 비교
  6. MQTT(IIoT) 미니 CONNECT / PUBLISH 패킷 인코더
  7. 산업 현장 연결 시 반드시 알아야 할 전기/EMI/타이밍 함정
  8. 임베디드 / 산업용 코드의 메모리 관리 (DMA, ISR-safe, 캐시 일관성)

  [실무 배경]
    공장 / 발전소 / 빌딩 자동화 / 자동차 ECU에서 마주칠 프로토콜.
    잘못 작성한 산업 코드 = 라인 정지, 안전사고, 수억 손실.
    학교/책에서 거의 안 가르치고, 입사 후 어깨너머로 배우는 영역.

  [컴파일]
    g++ -std=c++17 -Wall -Wextra -O2 -o 35_indproto main.cpp
=============================================================================
*/

#include <iostream>
#include <iomanip>
#include <vector>
#include <array>
#include <cstdint>
#include <cstring>
#include <string>
#include <stdexcept>
#include <chrono>
using namespace std;

void lesson1_it_vs_ot();
void lesson2_modbus();
void lesson3_can_bus();
void lesson4_opc_ua();
void lesson5_realtime_ethernet();
void lesson6_mqtt();
void lesson7_connection_pitfalls();
void lesson8_embedded_memory();

/*
=============================================================================
  레슨별 출력 흐름 가이드
=============================================================================
  lesson1 (IT vs OT): 비교표, Purdue 모델

  lesson2 (Modbus):
    RTU 요청 (8B): 01 03 00 00 00 0a c5 cd
      → slave=1, func=03 (read holding), addr=0x0000, count=10
      → CRC = 0xCDC5 (low high 순서)
    TCP 요청 (12B): 00 01 00 00 00 06 01 03 00 00 00 0a
    응답 디코드: 5개 레지스터 → 100, 200, 300, 400, 500
    예외 응답 0x83 0x02 → throw "Modbus exception code 2"

  lesson3 (CAN/CANopen):
    CAN ID: 0x181 (PDO1, node 1), DLC=4
    Data: b8 0b fa 00  (rpm=3000, torque=250 little-endian)
    디코드: RPM=3000, Torque=250

  lesson4 (OPC UA): 메시지 흐름, 노드 모델 다이어그램

  lesson5 (실시간 이더넷): EtherCAT/Profinet/EthIP 비교표

  lesson6 (MQTT):
    CONNECT 패킷 (15B): 10 0d 00 04 4d 51 54 54 04 02 00 1e 00 03 70 6c 63 2d 30 30 31
      → Protocol "MQTT", level=4, flags=0x02, keepalive=30, client_id="plc-001"
    PUBLISH retain (32B): 31 1e ...
      → topic="factory/line1/temperature", payload="23.5", retain=true

  lesson7 (연결 시 주의사항): 5가지 카테고리
    전기/타이밍/데이터/보안/운영 함정

  lesson8 (임베디드 메모리):
    SpscRing<T,N> 패턴 (lock-free)
    Memory Pool 패턴 (O(1) alloc/free)
=============================================================================
*/

int main() {
    cout << "================================================\n";
    cout << "  C++ 35단계 : 산업용 프로토콜\n";
    cout << "================================================\n\n";

    lesson1_it_vs_ot();
    lesson2_modbus();
    lesson3_can_bus();
    lesson4_opc_ua();
    lesson5_realtime_ethernet();
    lesson6_mqtt();
    lesson7_connection_pitfalls();
    lesson8_embedded_memory();

    cout << "\n35단계 학습 완료!\n";
    return 0;
}


// =============================================================================
//  레슨 1 — IT 네트워크 vs OT(산업) 네트워크
// =============================================================================

void lesson1_it_vs_ot() {
    cout << "[레슨 1] IT vs OT 네트워크 차이\n";
    cout << R"(
  ┌─ 핵심 차이 ───────────────────────────────────────────┐
  │              │ IT 네트워크          │ OT(산업)         │
  │──────────────┼──────────────────────┼──────────────────│
  │ 우선순위      │ 기밀(C)>무결성>가용성│ 가용성(A)>무결성>기밀│
  │ 지연          │ ms 단위 OK           │ μs ~ 수십μs 단위 │
  │ 결정성        │ best-effort         │ 실시간 보장 필수 │
  │ 다운타임      │ 분~시간             │ 초당 수백만원 손실│
  │ 수명          │ 5년 (장비 교체)     │ 20~30년          │
  │ 패치          │ 매월               │ 검증된 후 1~2년 │
  │ 트래픽        │ 변동 (사람)         │ 일정 (기계)     │
  │ 우선          │ 처리량(throughput) │ 지터(jitter) 최소│
  │ 인증          │ 사용자 → 시스템    │ 시스템 ↔ 시스템 │
  │ 안전(Safety) │ 거의 없음           │ 인명 보호 필수  │
  └──────────────┴──────────────────────┴─────────────────┘

  ■ 산업 프로토콜 스펙트럼

   필드버스(Fieldbus)        산업 이더넷           IIoT
   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
   │ Modbus RTU       │  │ Modbus TCP      │  │ MQTT             │
   │ (RS-485)         │  │ EtherNet/IP     │  │ MQTT-SN          │
   │ Profibus         │  │ Profinet        │  │ AMQP             │
   │ CAN / CANopen    │  │ EtherCAT        │  │ OPC UA           │
   │ DeviceNet        │  │ POWERLINK       │  │ HTTP REST        │
   │ HART             │  │ SERCOS III      │  │                  │
   └─────────────────┘  └─────────────────┘  └─────────────────┘
   < 1Mbps              10/100/1000Mbps      Wi-Fi / 셀룰러
   km 단위 거리          shop floor          글로벌
   고립                 부분 라우팅         완전 인터넷

  ■ 결정성(Determinism)이 왜 중요한가
    로봇 팔이 100ms 늦게 멈추면 → 사람 다침 / 제품 파손.
    그래서:
      - 프로토콜이 사이클 시간 보장 (예: EtherCAT 31.25μs)
      - 네트워크 jitter < 1μs
      - 우선순위 큐, TSN(Time-Sensitive Networking)

  ■ Purdue 모델 (산업 네트워크 계층)
    Level 5 : 기업 IT (ERP, 이메일)
    Level 4 : 사업장 IT (MES)
    ─────── DMZ ───────
    Level 3 : 운영 (히스토리안, OPC UA 서버)
    Level 2 : 감독 (HMI, SCADA)
    Level 1 : 제어 (PLC, DCS)
    Level 0 : 물리 (센서, 액추에이터)
    레벨 간 방화벽 / 단방향 게이트웨이가 보안 핵심
)";
    cout << endl;
}


// =============================================================================
//  레슨 2 — Modbus RTU / TCP
// =============================================================================
//
//  [Modbus 개요 - 1979년 Modicon]
//    가장 단순하고 가장 널리 쓰이는 산업 프로토콜.
//    클라이언트(마스터)가 서버(슬레이브)에게 read/write 요청.
//
//  [데이터 모델 - 4가지 테이블]
//    Coils             : 1비트 R/W   (디지털 출력, 릴레이)
//    Discrete Inputs   : 1비트 R     (디지털 입력, 스위치)
//    Holding Registers : 16비트 R/W (설정값, 제어값)
//    Input Registers   : 16비트 R   (센서값, 상태)
//
//  [주요 함수 코드]
//    0x01 Read Coils
//    0x02 Read Discrete Inputs
//    0x03 Read Holding Registers
//    0x04 Read Input Registers
//    0x05 Write Single Coil
//    0x06 Write Single Register
//    0x0F Write Multiple Coils
//    0x10 Write Multiple Registers
//    0x80+ : 예외 응답 (에러)
//
//  [Modbus RTU 프레임 - 시리얼(RS-485)]
//    ┌─────┬──────┬───────┬──────┐
//    │Slave│Func  │Data   │CRC16 │
//    │ 1B  │ 1B   │ 0~252B│ 2B   │
//    └─────┴──────┴───────┴──────┘
//    프레임 간 silent gap = 3.5 char time (구분자)
//
//  [Modbus TCP 프레임 - 이더넷]
//    ┌─────────────────┬────────┬───────┐
//    │ MBAP Header(7B) │UnitID  │ PDU   │
//    │                 │ 1B     │       │
//    └─────────────────┴────────┴───────┘
//    MBAP = Transaction(2) + Protocol(2,=0) + Length(2)
//    CRC 없음 (TCP가 보장), 그러나 응용 검증은 권장
// =============================================================================

class Modbus {
public:
    // CRC-16 / Modbus (polynomial 0xA001, init 0xFFFF, no final xor)
    // [메모리/성능] 테이블 lookup이 일반적이지만, 작은 데이터엔 비트 방식도 OK.
    static uint16_t crc16(const uint8_t* data, size_t len) {
        uint16_t crc = 0xFFFF;
        for (size_t i = 0; i < len; ++i) {
            crc ^= data[i];
            for (int b = 0; b < 8; ++b) {
                if (crc & 0x0001) crc = (crc >> 1) ^ 0xA001;
                else              crc >>= 1;
            }
        }
        return crc;
    }

    // [Read Holding Registers 요청 인코딩 - RTU]
    //   slave=1, addr=0x0000, count=10
    //   → 01 03 00 00 00 0A C5 CD
    static vector<uint8_t> rtu_read_holding(uint8_t slave,
                                            uint16_t addr, uint16_t count) {
        if (count > 125) throw runtime_error("max 125 registers per request");
        vector<uint8_t> f;
        f.reserve(8);                   // 정확히 8바이트
        f.push_back(slave);
        f.push_back(0x03);
        f.push_back((uint8_t)(addr >> 8));     // big-endian
        f.push_back((uint8_t)(addr & 0xFF));
        f.push_back((uint8_t)(count >> 8));
        f.push_back((uint8_t)(count & 0xFF));
        uint16_t crc = crc16(f.data(), f.size());
        f.push_back((uint8_t)(crc & 0xFF));    // CRC는 little-endian (예외!)
        f.push_back((uint8_t)(crc >> 8));
        return f;
    }

    // [Modbus TCP 동일 요청 인코딩]
    //   transaction=0x0001, protocol=0x0000, length=6, unit=1
    //   + func=03, addr=0000, count=000A
    static vector<uint8_t> tcp_read_holding(uint16_t txn, uint8_t unit,
                                            uint16_t addr, uint16_t count) {
        if (count > 125) throw runtime_error("max 125 registers per request");
        vector<uint8_t> f;
        f.reserve(12);
        // MBAP
        f.push_back((uint8_t)(txn >> 8));
        f.push_back((uint8_t)(txn & 0xFF));
        f.push_back(0x00);              // protocol identifier (Modbus = 0)
        f.push_back(0x00);
        f.push_back(0x00);              // length high
        f.push_back(0x06);              // unit + func + addr(2) + count(2) = 6
        f.push_back(unit);
        // PDU
        f.push_back(0x03);
        f.push_back((uint8_t)(addr >> 8));
        f.push_back((uint8_t)(addr & 0xFF));
        f.push_back((uint8_t)(count >> 8));
        f.push_back((uint8_t)(count & 0xFF));
        return f;
    }

    // [응답 디코더 - holding registers]
    // 응답 PDU: func(1) + byte_count(1) + data(N*2)
    static vector<uint16_t> decode_holding_response(const uint8_t* pdu,
                                                    size_t pdu_len) {
        if (pdu_len < 2) throw runtime_error("PDU too short");
        if (pdu[0] & 0x80) {
            // 예외 응답: 0x80+func, exception_code
            // 코드 의미: 1=Illegal Function, 2=Illegal Data Address,
            //          3=Illegal Data Value, 4=Server Failure, 5=Acknowledge,
            //          6=Server Busy, 8=Memory Parity Error
            throw runtime_error("Modbus exception code " +
                                to_string(pdu_len > 1 ? pdu[1] : 0));
        }
        if (pdu[0] != 0x03) throw runtime_error("function code mismatch");
        uint8_t bc = pdu[1];
        if (bc & 1) throw runtime_error("byte count not even");
        if (pdu_len < 2u + bc) throw runtime_error("truncated");
        vector<uint16_t> regs;
        regs.reserve(bc / 2);
        for (size_t i = 0; i < bc; i += 2) {
            uint16_t v = ((uint16_t)pdu[2 + i] << 8) | pdu[2 + i + 1];
            regs.push_back(v);
        }
        return regs;
    }
};

// 헬퍼: 바이트 배열 hex 출력
void dump_hex(const vector<uint8_t>& v, const string& label) {
    cout << "  " << label << " (" << v.size() << "B):";
    for (auto b : v) cout << " " << hex << setw(2) << setfill('0') << (int)b;
    cout << dec << "\n";
}

void lesson2_modbus() {
    cout << "[레슨 2] Modbus RTU / TCP\n\n";

    // RTU 요청 인코딩
    auto rtu = Modbus::rtu_read_holding(0x01, 0x0000, 10);
    dump_hex(rtu, "RTU 요청");
    // 검증: CRC가 0xC5 0xCD인지
    cout << "  CRC 위치 마지막 2바이트 (low, high): " << hex
         << (int)rtu[rtu.size()-2] << " " << (int)rtu[rtu.size()-1] << dec << "\n";

    // TCP 요청 인코딩
    auto tcp = Modbus::tcp_read_holding(0x0001, 0x01, 0x0000, 10);
    dump_hex(tcp, "TCP 요청");

    // 가짜 RTU 응답 디코딩: 슬레이브 1번이 5개 레지스터 반환
    //   01 03 0A 00 64 00 C8 01 2C 01 90 01 F4 [CRC2]
    vector<uint8_t> resp_pdu = {
        0x03, 0x0A,                    // func, byte count
        0x00, 0x64,                    // 100
        0x00, 0xC8,                    // 200
        0x01, 0x2C,                    // 300
        0x01, 0x90,                    // 400
        0x01, 0xF4                     // 500
    };
    auto regs = Modbus::decode_holding_response(resp_pdu.data(), resp_pdu.size());
    cout << "\n  응답 디코드:";
    for (auto r : regs) cout << " " << r;
    cout << "\n";

    // 예외 응답 디코딩 테스트
    vector<uint8_t> exc = {0x83, 0x02};  // Illegal Data Address
    try {
        Modbus::decode_holding_response(exc.data(), exc.size());
    } catch (exception& e) {
        cout << "  예외 응답 처리: " << e.what() << "\n";
    }

    cout << R"(
  ┌─ Modbus 실무 함정 ────────────────────────────────────┐
  │ ✦ 주소 헷갈림: 사용자 매뉴얼은 1-based / wire는 0-based│
  │   "40001"은 holding register #0번을 의미              │
  │ ✦ float / 32bit 표현: 2개 레지스터 사용. 바이트 순서는│
  │   장비마다 다름! (big/little endian, word swap)       │
  │   → 실측 후 byte/word swap 옵션 필수                  │
  │ ✦ 타임아웃: RTU 보통 1~2초. 통신 안 되면 fallback     │
  │ ✦ RTU silent gap: 3.5 char time. 고속(115200bps)에서  │
  │   < 200μs. OS 일반 시리얼 드라이버는 이 정밀도 부족    │
  │ ✦ 동시 요청 X (RTU). 마스터가 응답 받기 전엔 다음 X    │
  │ ✦ TCP는 동시 가능. transaction ID로 구분             │
  │ ✦ 멀티 슬레이브 RS-485: termination(120Ω) 양 끝, 분기X│
  │ ✦ 1 frame 최대: RTU 256B, TCP 260B (MBAP 포함)        │
  │ ✦ Modbus는 인증/암호화 없음 → VPN / Modbus Secure 사용│
  └───────────────────────────────────────────────────────┘
)";
    cout << endl;
}


// =============================================================================
//  레슨 3 — CAN bus / CANopen
// =============================================================================
//
//  [CAN bus - Bosch 1986년]
//    자동차 ECU 표준. 산업/의료/항공에도 폭넓게.
//    버스 토폴로지, CSMA/CR(충돌 시 우선순위로 해결).
//    Twisted pair, 차동 신호, 강한 노이즈 내성.
//
//  [CAN 프레임]
//    Standard (CAN 2.0A): ID 11비트, 데이터 0~8바이트
//    Extended (CAN 2.0B): ID 29비트
//    CAN FD (2012): 데이터 64바이트, 비트레이트 가변
//
//  [메시지 구조 (간략)]
//    SOF | ID(11/29) | RTR | IDE | r0 | DLC(4) | Data(0~8) | CRC(15) | ACK | EOF
//
//  [CANopen]
//    CAN bus 위 응용 계층 표준 (CiA 301).
//    객체 사전(Object Dictionary): 인덱스+서브인덱스로 변수 접근.
//    PDO (실시간 데이터), SDO (설정), NMT (네트워크 관리),
//    Sync, Heartbeat, Emergency.
// =============================================================================

#pragma pack(push, 1)
struct CanFrame {
    uint32_t id;          // 11 or 29 bits
    uint8_t  dlc;         // 0~8
    uint8_t  data[8];
    bool     extended;
    bool     rtr;         // remote frame (요청)
};
#pragma pack(pop)

void lesson3_can_bus() {
    cout << "[레슨 3] CAN bus / CANopen\n\n";

    // 가상 CAN 메시지: 엔진 RPM (CANopen-style)
    CanFrame f{};
    f.id  = 0x181;             // PDO1, node 1
    f.dlc = 4;
    uint16_t rpm    = 3000;
    uint16_t torque = 250;
    // 리틀 엔디안 (CANopen 표준)
    f.data[0] = (uint8_t)(rpm & 0xFF);
    f.data[1] = (uint8_t)(rpm >> 8);
    f.data[2] = (uint8_t)(torque & 0xFF);
    f.data[3] = (uint8_t)(torque >> 8);

    cout << "  CAN ID: 0x" << hex << f.id << dec << " (DLC=" << (int)f.dlc << ")\n";
    cout << "  Data:";
    for (int i = 0; i < f.dlc; ++i)
        cout << " " << hex << setw(2) << setfill('0') << (int)f.data[i];
    cout << dec << "\n";

    // 디코딩
    uint16_t r = f.data[0] | (f.data[1] << 8);
    uint16_t t = f.data[2] | (f.data[3] << 8);
    cout << "  디코드: RPM=" << r << ", Torque=" << t << "\n";

    cout << R"(
  ┌─ CAN 핵심 특징 ───────────────────────────────────────┐
  │ ✦ Lossless 우선순위: ID 작을수록 높은 우선순위       │
  │   여러 노드가 동시 송신 → ID bit 단위 비교로 충돌 해결│
  │ ✦ 비트레이트: 보통 250kbps~1Mbps, CAN FD는 8Mbps      │
  │ ✦ 길이 한계: 1Mbps에서 40m, 125kbps에서 500m           │
  │ ✦ Termination: 120Ω 양 끝 필수                        │
  │ ✦ DLC=0 (RTR) 으로 데이터 요청 가능                   │
  │ ✦ 자동 재전송 (NACK 시) - 응답성 보장 X (DoS 가능)     │
  │ ✦ Bit stuffing: 5연속 같은 비트 후 반대 비트 삽입     │
  │   → 와이어 길이가 데이터에 따라 변동 (지터 원인)      │
  └───────────────────────────────────────────────────────┘

  ┌─ CANopen 핵심 객체 ───────────────────────────────────┐
  │ COB-ID 분배                                           │
  │   0x000      : NMT (네트워크 관리)                    │
  │   0x080      : SYNC (동기화 트리거)                   │
  │   0x080+ID   : Emergency                              │
  │   0x180+ID   : TPDO1 (송신 실시간 데이터)             │
  │   0x200+ID   : RPDO1 (수신 실시간 데이터)             │
  │   0x580+ID   : SDO 응답                               │
  │   0x600+ID   : SDO 요청 (설정 read/write)             │
  │   0x700+ID   : Heartbeat (생존 신호)                  │
  │ Object Dictionary 예시                                │
  │   0x1000 : Device Type                                │
  │   0x1008 : Manufacturer Device Name                   │
  │   0x1017 : Heartbeat Producer Time (ms)               │
  │   0x6040 : ControlWord (CiA 402 모터 드라이브)         │
  │   0x6041 : StatusWord                                 │
  └───────────────────────────────────────────────────────┘

  ┌─ CAN 메모리 / 코드 함정 ──────────────────────────────┐
  │ ✦ 수신 버퍼 풀: ISR이 받자마자 ring buffer push     │
  │   → 응용은 polling으로 pop. ISR 안에서 long 작업 X   │
  │ ✦ DLC=8 고정으로 코딩 → CAN FD 도입 시 망가짐        │
  │ ✦ socketcan (Linux): write/read 표준 fd. 단순!       │
  │   PCAN, Vector 드라이버는 SDK 다름. 추상화 필수.     │
  │ ✦ bus-off 상태: 에러 카운터 256 초과 → 자동 복구 X    │
  │   → 수동 reset 필요. 무시하면 통신 끊김              │
  │ ✦ 멀티 마스터: 우선순위 낮은 메시지가 starvation 가능│
  └───────────────────────────────────────────────────────┘

  [라이브러리]
    Linux : SocketCAN (커널 표준)
    크로스: CANopenNode (https://github.com/CANopenNode/CANopenNode)
            오픈소스 CANopen 스택, 임베디드 친화
)";
    cout << endl;
}


// =============================================================================
//  레슨 4 — OPC UA
// =============================================================================
//
//  [OPC UA - 산업용 IIoT 표준 (IEC 62541)]
//    Modbus가 너무 단순/낡아서 새로 만든 현대 표준.
//    객체지향 모델, 보안, 인증, TLS, 다양한 전송(TCP/HTTPS/MQTT/AMQP).
//    "산업의 HTTP" 라고 불림.
//
//  [노드 모델]
//    모든 것이 노드(Node).
//    노드 종류: Object, Variable, Method, ObjectType, VariableType,
//             ReferenceType, DataType, View
//    노드 간 관계는 Reference로 표현.
//
//    예:
//      Server
//        └─ Objects
//            └─ Plant  (Object)
//                ├─ Pump1  (Object, type=PumpType)
//                │   ├─ Status   (Variable, Boolean)
//                │   ├─ Speed    (Variable, Double, EU=rpm)
//                │   └─ Start()  (Method)
//                └─ Tank1  (Object, type=TankType)
//                    └─ Level    (Variable, Double, EU=%)
//
//  [핵심 서비스]
//    Browse           : 노드 트리 탐색
//    Read / Write     : 변수 값 읽기/쓰기
//    Subscribe / MonitoredItem : 값 변경 푸시 알림
//    HistoryRead      : 시계열 데이터
//    Method Call      : 원격 메소드 호출
//
//  [라이브러리]
//    open62541    : 오픈소스 C, C++ 래퍼 가능. 가장 활성
//    Eclipse Milo : Java 기준이지만 .NET / C++ 포팅
//    UASDK (OPC Foundation 공식): 유료, 최고 호환성
// =============================================================================

void lesson4_opc_ua() {
    cout << "[레슨 4] OPC UA — 현대 산업 표준\n\n";

    cout << R"(
  ■ OPC UA 메시지 흐름 (TCP, binary 인코딩)
  ─────────────────────────────────────────
  Client                          Server
    │                                │
    │ ── Hello ────────────────────▶ │   (버전 / 청크 사이즈 협상)
    │ ◀── Acknowledge ────────────── │
    │ ── OpenSecureChannel ───────▶ │   (TLS 키 교환과 유사)
    │ ◀── OSC Response ─────────────│
    │ ── CreateSession ───────────▶ │   (사용자 인증)
    │ ◀── Session Response ─────────│
    │ ── ActivateSession ─────────▶ │
    │ ◀── Active ──────────────────│
    │ ── Read / Browse / Subscribe ▶│   (실제 작업)
    │ ◀── Response ─────────────────│
    │ ── CloseSession ───────────▶ │
    │                                │

  ■ 보안 (실무 필수)
    Security Mode: None / Sign / SignAndEncrypt
    User Token   : Anonymous / Username / X.509 Certificate
    프로덕션은 SignAndEncrypt + 인증서 기반 권장.
    인증서 디렉토리(트러스트 리스트) 관리는 운영 부담.

  ■ Subscription / MonitoredItem (이벤트 푸시)
    Client: "Pump1.Speed가 0.1 rpm 이상 변하면 100ms 이내 알려줘"
    Server: 변경 시 Publish 응답으로 즉시 푸시
    → polling 대신 변경량만 받음 (대역폭 절약, 실시간성 확보)

  ■ 데이터 모델 - 표준 정보 모델
    Companion Spec : 업종별 표준 모델
      예: PackML, AutoID, Robotics, Machine Tool, RT/PROFINET 통합
    설치 시점에 모델만 import → 코드 변경 없이 새 장비 통합

  ┌─ OPC UA 메모리 / 성능 함정 ───────────────────────────┐
  │ ✦ 노드 수가 수만 개 → metadata 만 수MB                │
  │   → AddressSpace 압축, namespace 분리                 │
  │ ✦ 인증서 체인 검증 비용 큼 → 세션 재사용              │
  │ ✦ Subscription 너무 많으면 publishing interval 충돌   │
  │   → 적절한 sampling/publishing interval 분리         │
  │ ✦ open62541 클라이언트는 단일 스레드 → 병렬 시 별도   │
  │   client 인스턴스 또는 비동기 큐                      │
  │ ✦ Variant 타입 메모리 - C 구조체에 union, 사용 후      │
  │   UA_Variant_clear() 호출 안 하면 누수               │
  │ ✦ 한 응답 메시지 max chunk → 큰 array는 분할 송수신   │
  │ ✦ Reverse Hello (서버가 클라에 connect 시도) -        │
  │   방화벽 통과용. NAT 환경에서 자주 사용              │
  └───────────────────────────────────────────────────────┘

  [언제 OPC UA를 선택?]
    - 다중 벤더 장비를 한 시스템으로 통합 (★)
    - 보안 / 감사 로그 / 인증 필수 (제약, 발전 등)
    - 클라우드/IT 통합 (Pub/Sub MQTT 매핑 가능)
    - HMI/SCADA → PLC 연결의 차세대
    [Modbus를 유지할 때]
    - 단순 1:1 / 1:N, 저비용
    - 기존 장비가 Modbus만 지원
    - 보안이 네트워크 segregation으로 충분
)";
    cout << endl;
}


// =============================================================================
//  레슨 5 — 실시간 산업 이더넷 (EtherCAT, Profinet, EtherNet/IP)
// =============================================================================

void lesson5_realtime_ethernet() {
    cout << "[레슨 5] 실시간 산업 이더넷 비교\n\n";

    cout << R"(
  ┌─ 비교표 ──────────────────────────────────────────────┐
  │            │ EtherCAT         │ Profinet IRT     │ EthIP │
  │────────────┼──────────────────┼──────────────────┼───────│
  │ 사이클      │ 31.25μs ~ 100μs  │ 250μs ~ 1ms     │ 1ms+ │
  │ 지터       │ < 1μs            │ < 1μs           │ ms     │
  │ 토폴로지    │ Line/Ring        │ Line/Star/Ring   │ Star  │
  │ HW 의존     │ ESC ASIC 슬레이브│ Profinet ASIC   │ 표준NIC│
  │ TSN 호환    │ 부분             │ 표준 (장기)      │ 가능  │
  │ 시장        │ 유럽 / 모터제어   │ 독일 / Siemens  │ 미국/Rockwell│
  │ 라이선스    │ BeckHoff (무료)  │ Profibus회원    │ ODVA  │
  │ 패킷 처리   │ "On the fly"    │ TDMA 슬롯       │ CIP   │
  └────────────┴──────────────────┴──────────────────┴───────┘

  ■ EtherCAT 동작 원리 (천재적)
    1. 마스터가 한 프레임을 라인 끝까지 흘려보냄
    2. 각 슬레이브가 "내 데이터만" 즉석에서 읽고/쓰기 (FPGA 속도)
    3. 마지막 슬레이브가 프레임 반사
    4. 마스터에게 돌아옴
    → 1프레임으로 N슬레이브 모두 R/W. 100M 라인 1000노드 < 100μs.

    └─ 메모리 / 코드 영향:
       - 마스터 코드는 PDO(매핑된 메모리 영역) 직접 read/write 처럼 보임
       - 실제 송수신은 백그라운드. 일관성 위해 cyclic copy 시점에 lock
       - SOEM (Simple Open EtherCAT Master) 오픈소스 라이브러리 활용

  ■ Profinet IRT (Isochronous Real-Time)
    - 표준 이더넷 + 동기화 (PTP/IEEE 1588)
    - 슬롯 기반: RT 트래픽은 정해진 시간 슬롯에만
    - Siemens TIA Portal에서 설정. PLCnext, S7 호환

  ■ EtherNet/IP
    - CIP(Common Industrial Protocol)을 TCP/UDP 위에 올림
    - Implicit (UDP, 실시간) / Explicit (TCP, 설정)
    - Rockwell ControlLogix 생태계

  ■ TSN (Time-Sensitive Networking, IEEE 802.1)
    - 표준 이더넷에 시간동기 + QoS 우선순위 + 시간슬롯 추가
    - 산업 이더넷의 차세대 통합 (모든 벤더가 표준 위에 동작)
    - 키 표준: 802.1AS (gPTP), 802.1Qbv (TAS), 802.1Qbu (preemption)

  ┌─ 메모리 / 실시간 코드 함정 ───────────────────────────┐
  │ ✦ malloc / new는 실시간 제어 루프에서 절대 금지        │
  │   → page fault, GC, lock으로 ms 단위 spike 가능        │
  │ ✦ 사이클 시작 전 모든 메모리 pre-allocate / mlock     │
  │ ✦ 페이지 fault 방지: mlockall(MCL_CURRENT | MCL_FUTURE)│
  │ ✦ CPU isolation (isolcpus) + 인터럽트 affinity 고정   │
  │ ✦ RT 커널(PREEMPT_RT) 사용 → priority inversion 방지   │
  │ ✦ 캐시 워밍업: 사이클 첫 회 매우 느림. 사전 더미 실행 │
  │ ✦ 로깅도 위험 - 디스크 I/O가 사이클 jitter. ring buffer│
  │   에 누적 → 별도 스레드가 비실시간 우선순위로 기록    │
  └───────────────────────────────────────────────────────┘
)";
    cout << endl;
}


// =============================================================================
//  레슨 6 — MQTT (IIoT 메시징)
// =============================================================================
//
//  [MQTT - IBM 1999, 현재 OASIS 표준 (3.1.1, 5.0)]
//    경량 pub/sub. TCP/TLS 위에서 동작. 작은 패킷, 모바일/IoT 친화.
//    QoS 0/1/2: 최선/최소1회/정확1회.
//    Last Will: 클라가 죽으면 브로커가 미리 정한 메시지 발행.
//    Retained: 새 구독자가 즉시 받는 마지막 값.
//
//  [패킷 구조]
//    고정 헤더 (1~5 byte): type + flags + remaining length
//    가변 헤더 (type별 다름)
//    페이로드
//
//  [Remaining Length 인코딩 - 가변 길이 정수]
//    7비트씩 little-endian, MSB(=0x80)는 continuation bit
//    127 → 0x7F (1byte)
//    128 → 0x80 0x01 (2byte)
//    16383 → 0xFF 0x7F (2byte)
//    최대 4byte → 268,435,455 byte (256MB)
// =============================================================================

class Mqtt {
public:
    // CONNECT 패킷 (MQTT 3.1.1) 인코딩
    //   client_id 만 받는 단순 버전. clean_session=true.
    static vector<uint8_t> encode_connect(const string& client_id,
                                          uint16_t keepalive = 60) {
        vector<uint8_t> var_payload;

        // ── 가변 헤더 ──
        // Protocol Name "MQTT"
        write_string(var_payload, "MQTT");
        var_payload.push_back(0x04);            // Protocol Level (4 = 3.1.1)
        var_payload.push_back(0x02);            // Connect flags: clean session
        var_payload.push_back((uint8_t)(keepalive >> 8));
        var_payload.push_back((uint8_t)(keepalive & 0xFF));
        // ── 페이로드 ──
        write_string(var_payload, client_id);

        // ── 고정 헤더 ──
        vector<uint8_t> packet;
        packet.push_back(0x10);                 // CONNECT (1) << 4
        encode_remaining_length(packet, var_payload.size());
        packet.insert(packet.end(), var_payload.begin(), var_payload.end());
        return packet;
    }

    // PUBLISH 패킷 (QoS 0)
    static vector<uint8_t> encode_publish(const string& topic,
                                          const string& payload,
                                          bool retain = false) {
        vector<uint8_t> var_payload;
        write_string(var_payload, topic);
        // QoS 0이면 packet identifier 없음
        var_payload.insert(var_payload.end(), payload.begin(), payload.end());

        vector<uint8_t> packet;
        uint8_t flags = 0;
        if (retain) flags |= 0x01;
        packet.push_back(0x30 | flags);          // PUBLISH (3) << 4
        encode_remaining_length(packet, var_payload.size());
        packet.insert(packet.end(), var_payload.begin(), var_payload.end());
        return packet;
    }

private:
    static void write_string(vector<uint8_t>& buf, const string& s) {
        if (s.size() > 65535) throw runtime_error("string too long");
        buf.push_back((uint8_t)(s.size() >> 8));    // big-endian length prefix
        buf.push_back((uint8_t)(s.size() & 0xFF));
        buf.insert(buf.end(), s.begin(), s.end());
    }

    static void encode_remaining_length(vector<uint8_t>& buf, size_t len) {
        if (len > 268435455) throw runtime_error("remaining length too big");
        do {
            uint8_t enc = len & 0x7F;
            len >>= 7;
            if (len > 0) enc |= 0x80;
            buf.push_back(enc);
        } while (len > 0);
    }
};

void lesson6_mqtt() {
    cout << "[레슨 6] MQTT — IIoT 메시징\n\n";

    auto connect_pkt = Mqtt::encode_connect("plc-001", 30);
    dump_hex(connect_pkt, "CONNECT 패킷");

    auto pub_pkt = Mqtt::encode_publish("factory/line1/temperature", "23.5", true);
    dump_hex(pub_pkt, "PUBLISH 패킷 (retain)");

    cout << R"(
  ┌─ MQTT 핵심 패턴 ──────────────────────────────────────┐
  │ ✦ 토픽 계층 설계가 시스템 성패 결정                   │
  │   factory/{site}/{line}/{device}/{metric}             │
  │   wildcards: + (single-level), # (multi-level, 끝만)  │
  │ ✦ QoS 선택                                            │
  │   0 (최선): 센서 측정값(잃어도 다음 값 옴)            │
  │   1 (최소1회): 알람, 로그 (중복 OK)                   │
  │   2 (정확1회): 결제, 명령 (중복 안됨)                 │
  │   QoS 높을수록 메모리/대역폭 비용 증가                 │
  │ ✦ Last Will: 클라가 갑자기 죽으면 브로커가 발행       │
  │   "device/X/status" → "offline" retained             │
  │ ✦ Retained: 새 구독자가 즉시 받는 마지막 값.          │
  │   상태 토픽엔 적합, 이벤트엔 부적합                   │
  │ ✦ MQTT 5.0 추가: shared subscriptions ($share/group/) │
  │   메시지 큐 패턴. 워커 분산                          │
  └───────────────────────────────────────────────────────┘

  ┌─ MQTT 메모리 / 성능 함정 ────────────────────────────┐
  │ ✦ 브로커 메모리: retained 메시지 누적 → 모니터링 필수 │
  │ ✦ 클라이언트 큐: 오프라인 동안 발행 → 메모리 폭증     │
  │   inflight 큐 크기 제한 / 디스크 spool 옵션           │
  │ ✦ 토픽 수 폭증 시 브로커 라우팅 느려짐 (특히 wildcard)│
  │ ✦ TLS 핸드셰이크 비용 - 모바일은 keepalive 짧게 X     │
  │ ✦ 페이로드 크기: 기본 max 268MB, 실무는 수KB 권장     │
  │   대용량은 별도 채널 + 토픽으로 알림                  │
  │ ✦ 클라이언트 ID 유니크 보장 - 중복 시 브로커가 강제   │
  │   disconnect 양쪽 → ping-pong 연결 끊김 무한 루프     │
  │ ✦ paho.mqtt.cpp는 MQTTAsync_destroy 등 RAII 누락 시   │
  │   누수 - unique_ptr custom deleter 권장               │
  └───────────────────────────────────────────────────────┘

  [브로커 추천]
    Mosquitto    : 가벼움, 표준
    EMQX         : 백만 동접
    HiveMQ       : 엔터프라이즈
    AWS IoT Core / Azure IoT Hub : 클라우드 매니지드
)";
    cout << endl;
}


// =============================================================================
//  레슨 7 — 산업 현장 연결 시 반드시 알아야 할 것
// =============================================================================
//
//  소프트웨어만 보면 안 보이는 함정들. 현장 가서 새벽까지 디버깅하는 원인.
// =============================================================================

void lesson7_connection_pitfalls() {
    cout << "[레슨 7] 산업 연결 시 주의사항 (전기/EMI/타이밍)\n\n";

    cout << R"(
  ┌─ 1. 전기적 함정 ──────────────────────────────────────┐
  │                                                       │
  │  ✦ Ground Loop (접지 루프)                            │
  │    PLC와 PC를 다른 콘센트에 연결 → 접지 전위차        │
  │    → 통신선에 수십V 전류 → 포트 고장 / 노이즈         │
  │    해결: 광 절연 (Optical isolation),                 │
  │          광케이블 컨버터, 접지 분리 트랜스            │
  │                                                       │
  │  ✦ EMI / EMC                                          │
  │    인버터 / VFD 옆 케이블 → 하이프리퀀시 노이즈        │
  │    → CRC 에러 폭증, 통신 끊김                         │
  │    해결: 차폐 케이블 (shielded twisted pair),         │
  │          ferrite bead, 24V 라인과 신호선 분리         │
  │                                                       │
  │  ✦ 서지 / Lightning                                   │
  │    공장 옥외 센서 - 번개 한 번에 전 라인 손상         │
  │    해결: 서지 보호기(SPD), 광 절연, 저항 종단         │
  │                                                       │
  │  ✦ RS-485 종단 (Termination)                          │
  │    버스 양 끝에 120Ω. 한 쪽만 있거나 중간에 있으면    │
  │    반사파 → 통신 불량. 분기(stub) 길면 망함           │
  │                                                       │
  │  ✦ 24V vs 5V 신호 혼용                                │
  │    PLC 24V 출력에 5V MCU 직결 → MCU 죽음              │
  │    → optocoupler / level shifter / relay              │
  └───────────────────────────────────────────────────────┘

  ┌─ 2. 타이밍 / 응답성 함정 ─────────────────────────────┐
  │                                                       │
  │  ✦ 워치독(Watchdog) 누락                              │
  │    통신 끊겨도 출력 그대로 유지 → 안전 실패           │
  │    → 슬레이브가 N ms 안에 폴 안 받으면 안전 상태로     │
  │                                                       │
  │  ✦ 폴링 주기                                          │
  │    너무 짧음 → 버스 포화                              │
  │    너무 길음 → 알람 늦음                              │
  │    실무: 알람 50~100ms, 트렌드 1s, 설정값 on-change   │
  │                                                       │
  │  ✦ 첫 연결 시 모든 값 읽기                            │
  │    재시작 후 stale 값 표시 위험                       │
  │    → boot 시 명시적 동기화 phase                      │
  │                                                       │
  │  ✦ Time sync                                          │
  │    각 PLC 시간 다르면 트렌드 분석 망함                │
  │    → NTP / PTP / IEEE 1588                            │
  │                                                       │
  │  ✦ Backoff / Retry 정책                               │
  │    실패 즉시 재시도 → 폭주 → 버스 마비                │
  │    → exponential backoff + 최대 시도 + jitter         │
  └───────────────────────────────────────────────────────┘

  ┌─ 3. 데이터 표현 함정 ─────────────────────────────────┐
  │                                                       │
  │  ✦ 엔디안                                             │
  │    Modbus는 big-endian per register지만               │
  │    32bit float 두 register 중 어느 쪽이 high word?    │
  │    장비마다 다름. 대표 4가지:                         │
  │      AB CD (big-endian, big word)                     │
  │      CD AB (big-endian, little word)                  │
  │      BA DC (byte swap, big word)                      │
  │      DC BA (byte swap, little word = 진정한 little)   │
  │    → 시운전 시 alidate. byte/word swap 옵션 제공      │
  │                                                       │
  │  ✦ 단위(EU - Engineering Unit)                        │
  │    "Speed=1500" → rpm? mm/s? %?                       │
  │    → 항상 단위와 스케일 명시. EU max/min 메타데이터   │
  │                                                       │
  │  ✦ Sign extension                                     │
  │    16bit 음수를 32bit로 그냥 캐스팅 → 잘못된 값        │
  │    → int16_t로 받아 int32_t로 변환                    │
  │                                                       │
  │  ✦ NaN / Inf                                          │
  │    센서 disconnect → 0xFFFFFFFF (NaN) 보내는 장비       │
  │    → 응용 코드가 NaN 처리 안 하면 평균/적분 오염       │
  └───────────────────────────────────────────────────────┘

  ┌─ 4. 보안 함정 ────────────────────────────────────────┐
  │                                                       │
  │  ✦ 산업 프로토콜 대부분 평문                          │
  │    Modbus RTU/TCP, EtherNet/IP, Profinet              │
  │    → IT/OT 분리, VPN, 일방향 게이트웨이               │
  │                                                       │
  │  ✦ 기본 패스워드 미변경                               │
  │    PLC, HMI 출고 기본 패스워드 → 바이러스 표적        │
  │                                                       │
  │  ✦ USB 매개체                                         │
  │    Stuxnet 사례. 엔지니어 노트북 → PLC 감염           │
  │    → 격리 노트북, USB 화이트리스트                    │
  │                                                       │
  │  ✦ Firmware 무결성                                    │
  │    펌웨어 업데이트 검증 없음 → 위조 펌웨어             │
  │    → 서명 검증 / Secure Boot                          │
  │                                                       │
  │  ✦ 안전 PLC와 일반 PLC 분리                            │
  │    SIL/PL 등급 안전 PLC는 별도 네트워크               │
  │    일반 IT 패치로 안전 PLC 건드리면 안전 인증 무효     │
  └───────────────────────────────────────────────────────┘

  ┌─ 5. 운영 함정 ────────────────────────────────────────┐
  │  ✦ 시운전 vs 운영 차이                                │
  │    시운전: 혼자 뚱딱. 운영: 24/7, 가동 중 패치 못함   │
  │  ✦ 문서화                                             │
  │    "이 코드 만든 사람 퇴사" → 6개월 후 라인 정지      │
  │  ✦ 백업                                               │
  │    PLC 프로그램 / OPC 설정 / 인증서 → 정기 백업       │
  │  ✦ 변경 관리 (CC)                                     │
  │    제약/식품 GMP는 변경 추적 의무. 코드 검증 재진행   │
  └───────────────────────────────────────────────────────┘
)";
    cout << endl;
}


// =============================================================================
//  레슨 8 — 임베디드 / 산업 코드 메모리 관리
// =============================================================================

void lesson8_embedded_memory() {
    cout << "[레슨 8] 임베디드 / 산업 코드 메모리 관리\n\n";

    cout << R"(
  ┌─ 1. malloc 금지 영역 ─────────────────────────────────┐
  │                                                       │
  │  실시간 제어 루프 / ISR / 안전 critical 코드에서      │
  │  동적 할당은 사실상 금지. 이유:                       │
  │    - 단편화 (long-running 시 OOM 가능)                │
  │    - 시간 비결정 (allocator 락 / page fault)          │
  │    - 누수 디버깅 어려움                               │
  │  대안:                                                │
  │    - static / global pre-allocation                   │
  │    - 메모리 풀 (object pool)                          │
  │    - 스택 할당 + alloca 신중                          │
  │    - 사이클 시작 전 모두 reserve                      │
  └───────────────────────────────────────────────────────┘

  ┌─ 2. ISR-safe 자료구조 ────────────────────────────────┐
  │                                                       │
  │  ISR(인터럽트 핸들러)에서 std::queue / std::vector    │
  │  → 절대 안 됨. lock 잡으면 데드락, malloc 호출 시 UB.  │
  │  대신:                                                │
  │    - lock-free SPSC ring buffer (Single Prod Single Cons)│
  │    - 고정 크기, atomic head/tail                      │
  │    - 풀 / 빈 처리 명확                                │
  │                                                       │
  │  template<typename T, size_t N>                       │
  │  class SpscRing {                                     │
  │    array<T, N> buf;                                   │
  │    atomic<size_t> head{0}, tail{0};                   │
  │  public:                                              │
  │    bool push(const T& v) {                            │
  │      auto t = tail.load(memory_order_relaxed);        │
  │      auto next = (t + 1) % N;                         │
  │      if (next == head.load(memory_order_acquire))     │
  │        return false;  // full                         │
  │      buf[t] = v;                                      │
  │      tail.store(next, memory_order_release);          │
  │      return true;                                     │
  │    }                                                  │
  │    bool pop(T& v) {                                   │
  │      auto h = head.load(memory_order_relaxed);        │
  │      if (h == tail.load(memory_order_acquire))        │
  │        return false;  // empty                        │
  │      v = buf[h];                                      │
  │      head.store((h + 1) % N, memory_order_release);   │
  │      return true;                                     │
  │    }                                                  │
  │  };                                                   │
  │                                                       │
  │  ISR: ring.push(sample);                              │
  │  Main: while (ring.pop(s)) process(s);                │
  └───────────────────────────────────────────────────────┘

  ┌─ 3. DMA 버퍼 ─────────────────────────────────────────┐
  │                                                       │
  │  DMA(Direct Memory Access): CPU 안 거치고 주변기기↔메모리│
  │  주의:                                                │
  │   ✦ 캐시 일관성 (cache coherency)                     │
  │     DMA가 RAM 갱신 → CPU는 캐시 stale 읽음            │
  │     → DMA 시작 전 cache invalidate / clean            │
  │     ARM: __DSB(), __ISB(), 또는 driver의 sync API     │
  │   ✦ 정렬 (alignment)                                  │
  │     DMA 컨트롤러는 보통 4 / 8 / 32 byte 정렬 필요     │
  │     unaligned는 hardfault                             │
  │     → alignas(32) 또는 __attribute__((aligned(32)))   │
  │   ✦ MPU/MMU 영역                                      │
  │     non-cacheable 메모리 영역에 DMA 버퍼 배치        │
  │   ✦ 더블 버퍼링                                       │
  │     A 버퍼 처리 중 B 버퍼 DMA 수신 → drop 없음        │
  └───────────────────────────────────────────────────────┘

  ┌─ 4. volatile 의 진짜 의미 ────────────────────────────┐
  │                                                       │
  │  volatile은 "최적화 금지" 마크. 다음에만 사용:        │
  │    - 메모리 매핑 레지스터 (MMIO)                      │
  │    - 시그널 핸들러 / setjmp 사이의 변수               │
  │  사용하면 안 됨:                                      │
  │    - 멀티스레드 동기화 (atomic 사용)                  │
  │    - DMA 일관성 (cache flush API 사용)                │
  │                                                       │
  │  // ✓ 올바른 사용                                     │
  │  volatile uint32_t* GPIO_DATA = (uint32_t*)0x40020000;│
  │  *GPIO_DATA = 0xFF;  // 컴파일러가 최적화하지 않음     │
  │                                                       │
  │  // ✗ 잘못된 사용 (멀티스레드)                        │
  │  volatile int counter;  // race 안전성 보장 X         │
  │  // → std::atomic<int> counter; 사용                  │
  └───────────────────────────────────────────────────────┘

  ┌─ 5. 메모리 풀 패턴 ───────────────────────────────────┐
  │                                                       │
  │  template<typename T, size_t N>                       │
  │  class Pool {                                         │
  │    union Slot {                                       │
  │      T value;                                         │
  │      Slot* next;                                      │
  │      Slot() {}                                        │
  │      ~Slot() {}                                       │
  │    };                                                 │
  │    array<Slot, N> storage;                            │
  │    Slot* free_list;                                   │
  │  public:                                              │
  │    Pool() {                                           │
  │      for (size_t i = 0; i < N - 1; ++i)               │
  │        storage[i].next = &storage[i + 1];             │
  │      storage[N - 1].next = nullptr;                   │
  │      free_list = &storage[0];                         │
  │    }                                                  │
  │    T* alloc() {                                       │
  │      if (!free_list) return nullptr;                  │
  │      auto s = free_list;                              │
  │      free_list = s->next;                             │
  │      return new (&s->value) T();                      │
  │    }                                                  │
  │    void free(T* p) {                                  │
  │      p->~T();                                          │
  │      auto s = reinterpret_cast<Slot*>(p);             │
  │      s->next = free_list;                             │
  │      free_list = s;                                   │
  │    }                                                  │
  │  };                                                   │
  │                                                       │
  │  → O(1) alloc/free, 단편화 없음, 결정적 시간          │
  │  → CAN 메시지, 이벤트, 센서 샘플 등 고정 타입에 이상적│
  └───────────────────────────────────────────────────────┘

  ┌─ 6. 정적 분석 / 검증 도구 ────────────────────────────┐
  │                                                       │
  │  안전 critical 코드는 다음을 정기 실행:                │
  │   - clang-tidy + cppcheck (정적 분석)                  │
  │   - PC-lint Plus, Coverity (상용)                     │
  │   - MISRA C++ 가이드라인 준수                         │
  │   - AddressSanitizer / UBSan (개발 환경)               │
  │   - 임베디드: 시뮬레이터에서 valgrind 실행             │
  │   - Code coverage > 80% (안전 인증 요구사항)           │
  │   - 정적 호출 그래프 (재귀, 깊이 분석)                 │
  │   - 스택 사용량 분석 (-fstack-usage)                   │
  └───────────────────────────────────────────────────────┘
)";
    cout << endl;
}


// =============================================================================
//  연습문제
// =============================================================================
//
//  [연습 1] Modbus TCP 서버 구현
//    위 클라이언트 코드와 ch34의 TCP 서버를 결합. 가상 holding registers
//    1000개를 메모리에 두고 read/write 처리.
//
//  [연습 2] 32비트 float 표현 4종 모두 디코딩
//    swap 옵션을 enum으로 받아 동일 데이터를 4가지 방식으로 해석.
//    bit_cast / memcpy 활용 (reinterpret_cast는 strict aliasing 위험).
//
//  [연습 3] CAN 메시지 SPSC ring buffer
//    위 SpscRing<CanFrame, 256>을 ISR 시뮬레이션 (별도 스레드)에서 push,
//    main 스레드에서 pop. 1초간 처리량 측정.
//
//  [연습 4] MQTT 클라이언트
//    ch34의 TCP 코드와 위 MQTT 인코더를 결합. CONNECT → PUBLISH 흐름.
//    paho.mqtt.cpp 라이브러리 사용 버전과 비교.
//
//  [연습 5] OPC UA 노드 탐색기
//    open62541 또는 의사코드. 서버 connect → Browse → 트리 출력.
//    Subscribe로 한 변수 값 변경 실시간 모니터링.
//
//  [연습 6] Watchdog 패턴
//    Modbus 마스터가 100ms 안에 폴 못 받으면 슬레이브가 안전 상태로.
//    슬레이브 측 timer 기반 구현.
//
//  [연습 7] 통신 진단 도구
//    프레임 통계 (성공/실패/타임아웃/CRC오류) + 응답 시간 히스토그램.
//    실무에서 디버깅에 결정적.
//
//  [연습 8] 위 SpscRing을 lock-free MPMC로 확장
//    ABA 문제, hazard pointer 또는 sequence number 패턴 학습.
// =============================================================================
