/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  네트워크 학습 06단계: 프록시, 게이트웨이, 터널링
  ─────────────────────────────────────────────────
  Forward/Reverse Proxy, 로드밸런서, API Gateway,
  VPN, SSH 터널링, C++로 프록시/포트포워딩 구현

  ■ 컴파일 방법:
      g++ -std=c++17 -Wall -lws2_32 -o proxy_gateway main.cpp

  ■ 이 파일을 배우면 할 수 있는 것:
      - Forward/Reverse Proxy 차이 완벽 이해
      - 로드밸런서와 API Gateway 역할 파악
      - VPN, SSH 터널링의 원리 이해
      - C++로 간단한 프록시 서버 구현

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

#ifdef _WIN32
    #ifndef WIN32_LEAN_AND_MEAN
    #define WIN32_LEAN_AND_MEAN
    #endif
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #define SOCKET_INIT() do { WSADATA wsa; WSAStartup(MAKEWORD(2,2), &wsa); } while(0)
    #define SOCKET_CLEANUP() WSACleanup()
    #define CLOSE_SOCKET(s) closesocket(s)
    #define SOCKET_ERROR_CODE WSAGetLastError()
    typedef int socklen_t;
#else
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
#include <map>
#include <sstream>
#include <iomanip>
#include <algorithm>
#include <functional>
#include <thread>
#include <atomic>
#include <mutex>
#include <chrono>

// ┌───────────────────────────────────────────────────────────────────┐
// │  ★ 이 파일에서 다루는 핵심 개념들:                               │
// │                                                                   │
// │  1. Forward Proxy  - 클라이언트의 대리인                          │
// │  2. Reverse Proxy  - 서버의 대리인 (Nginx)                       │
// │  3. Load Balancer  - 부하 분산기                                  │
// │  4. API Gateway    - API 관문 (인증, 라우팅)                     │
// │  5. VPN            - 가상 사설망 (터널링)                        │
// │  6. SSH Tunneling  - SSH를 이용한 터널                           │
// │  7. SOCKS Proxy    - 범용 프록시 프로토콜                        │
// └───────────────────────────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  Forward Proxy (정방향 프록시) - "클라이언트의 대리인"
// ════════════════════════════════════════════════════════════════════
//
//  Forward Proxy란?
//  ────────────────
//  클라이언트 대신 인터넷에 접속하는 중간 서버
//
//  비유: 비서가 대신 전화해주는 것
//    사장님: "비서야, A 회사에 전화해서 견적 물어봐"
//    비서: A 회사에 전화 → 결과를 사장님에게 전달
//    A 회사는 비서의 번호만 알고, 사장님 번호는 모름!
//
//  ┌─────────────────────────────────────────────────────────┐
//  │              Forward Proxy 동작                          │
//  │                                                          │
//  │   [클라이언트A]──┐                                       │
//  │   [클라이언트B]──┼──→ [Forward Proxy] ──→ [인터넷]       │
//  │   [클라이언트C]──┘    (대리인)                            │
//  │                                                          │
//  │   ★ 서버는 프록시의 IP만 봄 (클라이언트 IP 숨김)        │
//  │                                                          │
//  │   용도:                                                  │
//  │   - 익명성 보장 (IP 숨기기)                              │
//  │   - 콘텐츠 필터링 (회사에서 유튜브 차단)                 │
//  │   - 캐싱 (자주 방문하는 사이트 캐시)                    │
//  │   - 접근 제어 (특정 사이트만 허용)                       │
//  │   - 로깅 (누가 어디 접속했는지 기록)                     │
//  └─────────────────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  Reverse Proxy (역방향 프록시) - "서버의 대리인"
// ════════════════════════════════════════════════════════════════════
//
//  Reverse Proxy란?
//  ────────────────
//  서버 앞에서 클라이언트의 요청을 대신 받아주는 중간 서버
//
//  비유: 식당의 카운터/웨이터
//    손님은 주방에 직접 가지 않고 카운터에서 주문
//    카운터가 주방에 전달 → 결과를 손님에게 전달
//    손님은 주방이 어디 있는지 몰라도 됨!
//
//  ┌─────────────────────────────────────────────────────────┐
//  │              Reverse Proxy 동작                           │
//  │                                                          │
//  │                              [서버1 (192.168.1.10)]      │
//  │   [인터넷] ──→ [Reverse   ]──→ [서버2 (192.168.1.11)]   │
//  │    클라이언트   [Proxy     ]──→ [서버3 (192.168.1.12)]   │
//  │                 (Nginx 등)                               │
//  │                                                          │
//  │   ★ 클라이언트는 Reverse Proxy의 IP만 알고,             │
//  │     실제 서버의 IP는 모름! (보안 향상)                   │
//  │                                                          │
//  │   용도:                                                  │
//  │   - 로드 밸런싱 (여러 서버에 분산)                       │
//  │   - SSL 종료 (프록시에서 HTTPS 처리)                     │
//  │   - 캐싱 (정적 파일 캐시)                               │
//  │   - 보안 (서버 IP 숨기기, WAF)                           │
//  │   - 압축 (gzip 등)                                       │
//  └─────────────────────────────────────────────────────────┘
//
//  Nginx 리버스 프록시 설정 예시:
//
//  ┌──────────────────────────────────────────┐
//  │  server {                                 │
//  │      listen 80;                           │
//  │      server_name www.example.com;         │
//  │                                           │
//  │      location / {                         │
//  │          proxy_pass http://backend;        │
//  │      }                                    │
//  │  }                                        │
//  │                                           │
//  │  upstream backend {                       │
//  │      server 192.168.1.10:8080;            │
//  │      server 192.168.1.11:8080;            │
//  │      server 192.168.1.12:8080;            │
//  │  }                                        │
//  └──────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  Forward Proxy vs Reverse Proxy 비교
// ════════════════════════════════════════════════════════════════════
//
//  ┌──────────────────────┬────────────────────────────────────────┐
//  │ 항목                 │ Forward Proxy     │ Reverse Proxy       │
//  ├──────────────────────┼───────────────────┼─────────────────────┤
//  │ 위치                 │ 클라이언트 앞      │ 서버 앞              │
//  │ 누구를 대신?         │ 클라이언트를 대리  │ 서버를 대리          │
//  │ 누가 설정?           │ 클라이언트 측      │ 서버 관리자          │
//  │ IP 숨기기            │ 클라이언트 IP 숨김 │ 서버 IP 숨김         │
//  │ 대표 예              │ Squid, 학교 프록시 │ Nginx, HAProxy      │
//  │ 클라이언트가 인식?   │ 인식함 (설정 필요) │ 인식 못함 (투명)     │
//  └──────────────────────┴───────────────────┴─────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  로드 밸런서 - "교통 경찰"
// ════════════════════════════════════════════════════════════════════
//
//  로드 밸런서란?
//  ─────────────
//  여러 서버에 트래픽을 골고루 분산하는 장비/소프트웨어
//
//  비유: 은행의 번호표 시스템
//    손님들에게 번호표를 주고 빈 창구로 안내
//    특정 창구에 손님이 몰리지 않게 분산!
//
//  ┌─────────────────────────────────────────────────────────┐
//  │              로드 밸런싱 알고리즘                         │
//  │                                                          │
//  │  1. Round Robin (순차)                                   │
//  │     요청1 → 서버1, 요청2 → 서버2, 요청3 → 서버3,      │
//  │     요청4 → 서버1, ... (돌아가면서 배분)                │
//  │                                                          │
//  │  2. Least Connections (최소 연결)                         │
//  │     현재 연결 수가 가장 적은 서버에 배분                 │
//  │     서버1(3개), 서버2(1개), 서버3(5개) → 서버2로!       │
//  │                                                          │
//  │  3. IP Hash (IP 해시)                                    │
//  │     클라이언트 IP를 해시하여 항상 같은 서버로             │
//  │     → 세션 유지에 유리! (Sticky Session)                 │
//  │                                                          │
//  │  4. Weighted Round Robin (가중치 순차)                    │
//  │     성능 좋은 서버에 더 많은 요청 배분                   │
//  │     서버1(weight=5), 서버2(weight=3), 서버3(weight=2)   │
//  │                                                          │
//  │  5. Random (랜덤)                                        │
//  │     무작위로 선택 (구현 간단, 대규모에서 의외로 효율적)   │
//  └─────────────────────────────────────────────────────────┘
//
//  로드 밸런서 vs 리버스 프록시:
//  ┌────────────────────┬────────────────────────────────────┐
//  │ 로드 밸런서         │ 리버스 프록시                       │
//  ├────────────────────┼────────────────────────────────────┤
//  │ 부하 분산이 주 목적 │ 다양한 기능 (캐싱, SSL, 라우팅)   │
//  │ L4 또는 L7         │ 주로 L7                             │
//  │ HAProxy, NLB       │ Nginx, Traefik                     │
//  │ TCP/UDP 레벨 분산  │ HTTP 레벨 처리                      │
//  └────────────────────┴────────────────────────────────────┘
//  ★ Nginx는 둘 다 할 수 있음! (리버스프록시 + 로드밸런서)

// ════════════════════════════════════════════════════════════════════
//  로드 밸런서 시뮬레이션
// ════════════════════════════════════════════════════════════════════

struct BackendServer {
    std::string name;            // 서버 이름
    std::string address;         // IP:포트
    int weight;                  // 가중치
    int active_connections;      // 현재 연결 수
    bool healthy;                // 헬스 체크 상태
    int total_requests;          // 총 처리 요청 수
};

class LoadBalancer {
private:
    std::vector<BackendServer> servers_;
    int rr_index_ = 0;          // Round Robin 인덱스

public:
    // 백엔드 서버 추가
    void add_server(const std::string& name, const std::string& addr,
                    int weight = 1) {
        servers_.push_back({name, addr, weight, 0, true, 0});
    }

    // Round Robin 알고리즘
    BackendServer* round_robin() {
        if (servers_.empty()) return nullptr;

        int attempts = 0;
        while (attempts < static_cast<int>(servers_.size())) {
            int idx = rr_index_ % servers_.size();
            rr_index_++;
            if (servers_[idx].healthy) {
                servers_[idx].active_connections++;
                servers_[idx].total_requests++;
                return &servers_[idx];
            }
            attempts++;
        }
        return nullptr;  // 모든 서버 다운
    }

    // Least Connections 알고리즘
    BackendServer* least_connections() {
        BackendServer* best = nullptr;
        for (auto& s : servers_) {
            if (s.healthy) {
                if (!best || s.active_connections < best->active_connections) {
                    best = &s;
                }
            }
        }
        if (best) {
            best->active_connections++;
            best->total_requests++;
        }
        return best;
    }

    // IP Hash 알고리즘
    BackendServer* ip_hash(const std::string& client_ip) {
        // 간단한 해시: IP 문자열의 각 문자 합
        uint32_t hash = 0;
        for (char c : client_ip) {
            hash = hash * 31 + c;
        }

        // 건강한 서버만 필터링
        std::vector<int> healthy_indices;
        for (size_t i = 0; i < servers_.size(); i++) {
            if (servers_[i].healthy) healthy_indices.push_back(static_cast<int>(i));
        }

        if (healthy_indices.empty()) return nullptr;

        int idx = healthy_indices[hash % healthy_indices.size()];
        servers_[idx].active_connections++;
        servers_[idx].total_requests++;
        return &servers_[idx];
    }

    // 서버 상태 출력
    void print_status() const {
        std::cout << "\n  ┌─────────────────────────────────────────────────────────┐" << std::endl;
        std::cout << "  │              로드 밸런서 서버 상태                       │" << std::endl;
        std::cout << "  ├──────────┬──────────────────┬──────┬───────┬──────┬─────┤" << std::endl;
        std::cout << "  │ 서버     │ 주소             │ 가중 │ 연결  │ 총요청│상태 │" << std::endl;
        std::cout << "  ├──────────┼──────────────────┼──────┼───────┼──────┼─────┤" << std::endl;

        for (const auto& s : servers_) {
            std::cout << "  │ " << std::setw(8) << std::left << s.name
                      << " │ " << std::setw(16) << s.address
                      << " │ " << std::setw(4) << s.weight
                      << " │ " << std::setw(5) << s.active_connections
                      << " │ " << std::setw(4) << s.total_requests
                      << " │ " << (s.healthy ? "UP  " : "DOWN")
                      << " │" << std::endl;
        }
        std::cout << "  └──────────┴──────────────────┴──────┴───────┴──────┴─────┘" << std::endl;
    }

    // 연결 해제 (시뮬레이션)
    void disconnect(BackendServer* server) {
        if (server && server->active_connections > 0) {
            server->active_connections--;
        }
    }

    // 서버 다운 시뮬레이션
    void set_health(const std::string& name, bool healthy) {
        for (auto& s : servers_) {
            if (s.name == name) {
                s.healthy = healthy;
                break;
            }
        }
    }
};

// ════════════════════════════════════════════════════════════════════
//  API Gateway - "API의 정문"
// ════════════════════════════════════════════════════════════════════
//
//  API Gateway란?
//  ─────────────
//  마이크로서비스 아키텍처에서 모든 API 요청의 단일 진입점
//
//  비유: 호텔 프론트 데스크
//    손님: "수영장 가고 싶어요" → 프론트: "3층 왼쪽이요"
//    손님: "식당 가고 싶어요" → 프론트: "2층 오른쪽이요"
//    프론트가 없으면 모든 시설 위치를 직접 알아야 함!
//
//  ┌─────────────────────────────────────────────────────────┐
//  │              API Gateway 아키텍처                         │
//  │                                                          │
//  │  [모바일 앱]──┐                    [인증 서비스]         │
//  │  [웹 브라우저]─┤   ┌──────────┐    [사용자 서비스]       │
//  │  [IoT 장치]───┤──→│   API    │───→[주문 서비스]         │
//  │  [외부 API]───┘   │ Gateway  │───→[결제 서비스]         │
//  │                    └──────────┘    [알림 서비스]         │
//  │                                                          │
//  │  API Gateway 기능:                                       │
//  │  ┌──────────────┬────────────────────────────────────┐  │
//  │  │ 기능         │ 설명                                │  │
//  │  ├──────────────┼────────────────────────────────────┤  │
//  │  │ 인증/인가    │ JWT 토큰 검증, API Key 확인        │  │
//  │  │ 라우팅       │ URL별로 적절한 서비스로 전달        │  │
//  │  │ 레이트 리밋  │ 초당 요청 수 제한 (DoS 방지)       │  │
//  │  │ 로깅/모니터링│ 모든 요청 기록, 메트릭 수집        │  │
//  │  │ 캐싱         │ 자주 요청되는 데이터 캐시           │  │
//  │  │ 변환         │ 요청/응답 형식 변환                 │  │
//  │  │ 서킷 브레이커│ 장애 서비스 자동 차단               │  │
//  │  └──────────────┴────────────────────────────────────┘  │
//  │                                                          │
//  │  대표 제품: Kong, AWS API Gateway, Traefik, Zuul        │
//  └─────────────────────────────────────────────────────────┘

// ── API Gateway 시뮬레이션 ──

struct APIRoute {
    std::string path_prefix;      // URL 접두사
    std::string backend_service;  // 대상 서비스
    bool auth_required;           // 인증 필요 여부
    int rate_limit;               // 초당 최대 요청 수
};

class APIGateway {
private:
    std::vector<APIRoute> routes_;
    std::map<std::string, int> request_counts_;  // 클라이언트별 요청 수

public:
    // 라우트 등록
    void add_route(const std::string& prefix, const std::string& service,
                   bool auth = false, int rate_limit = 100) {
        routes_.push_back({prefix, service, auth, rate_limit});
    }

    // 요청 처리 시뮬레이션
    std::string handle_request(const std::string& path,
                                const std::string& client_ip,
                                const std::string& auth_token = "") {
        std::cout << "\n  [Gateway] 요청: " << path
                  << " from " << client_ip << std::endl;

        // 1. 라우트 매칭
        const APIRoute* matched = nullptr;
        for (const auto& route : routes_) {
            if (path.find(route.path_prefix) == 0) {
                matched = &route;
                break;
            }
        }

        if (!matched) {
            std::cout << "  [Gateway] ✗ 라우트 없음: 404" << std::endl;
            return "404 Not Found";
        }

        std::cout << "  [Gateway] 라우트 매칭: " << matched->path_prefix
                  << " → " << matched->backend_service << std::endl;

        // 2. 인증 확인
        if (matched->auth_required && auth_token.empty()) {
            std::cout << "  [Gateway] ✗ 인증 필요: 401" << std::endl;
            return "401 Unauthorized";
        }
        if (matched->auth_required) {
            std::cout << "  [Gateway] ✓ 인증 확인: " << auth_token.substr(0, 10) << "..." << std::endl;
        }

        // 3. 레이트 리밋 확인
        request_counts_[client_ip]++;
        if (request_counts_[client_ip] > matched->rate_limit) {
            std::cout << "  [Gateway] ✗ 레이트 리밋 초과: 429" << std::endl;
            return "429 Too Many Requests";
        }
        std::cout << "  [Gateway] 요청 수: " << request_counts_[client_ip]
                  << "/" << matched->rate_limit << std::endl;

        // 4. 백엔드 서비스에 전달
        std::cout << "  [Gateway] → " << matched->backend_service << "에 전달" << std::endl;
        return "200 OK (from " + matched->backend_service + ")";
    }

    // 라우팅 테이블 출력
    void print_routes() const {
        std::cout << "\n  ┌─────────────────────────────────────────────────────┐" << std::endl;
        std::cout << "  │              API Gateway 라우팅 테이블               │" << std::endl;
        std::cout << "  ├──────────────┬──────────────────┬──────┬────────────┤" << std::endl;
        std::cout << "  │ 경로 접두사  │ 백엔드 서비스     │ 인증 │ Rate Limit │" << std::endl;
        std::cout << "  ├──────────────┼──────────────────┼──────┼────────────┤" << std::endl;
        for (const auto& r : routes_) {
            std::cout << "  │ " << std::setw(12) << std::left << r.path_prefix
                      << " │ " << std::setw(16) << r.backend_service
                      << " │ " << std::setw(4) << (r.auth_required ? "YES" : "NO")
                      << " │ " << std::setw(10) << (std::to_string(r.rate_limit) + "/s")
                      << " │" << std::endl;
        }
        std::cout << "  └──────────────┴──────────────────┴──────┴────────────┘" << std::endl;
    }
};

// ════════════════════════════════════════════════════════════════════
//  VPN (Virtual Private Network) - "비밀 터널"
// ════════════════════════════════════════════════════════════════════
//
//  VPN이란?
//  ───────
//  공용 네트워크(인터넷)를 통해 사설 네트워크처럼 통신하는 기술
//
//  비유: 지하 비밀 터널
//    두 건물 사이에 지하 터널을 만들면
//    외부에서는 누가 오가는지 볼 수 없음!
//    인터넷이라는 공개 도로 안에 "암호화된 터널"을 만드는 것
//
//  ┌─────────────────────────────────────────────────────────┐
//  │              VPN 동작 원리                                │
//  │                                                          │
//  │  [집 PC]                               [회사 서버]       │
//  │    │                                       │             │
//  │    │── 원본 패킷: GET /intranet ─────>│ (직접 불가!)    │
//  │    │                                       │             │
//  │    │── VPN 터널: ───────────────────>│                  │
//  │    │   ┌─────────────────────────┐        │             │
//  │    │   │ [암호화된 원본 패킷]     │        │             │
//  │    │   │  IP: VPN서버             │        │             │
//  │    │   │  내용: 알수없음(암호화)  │        │             │
//  │    │   └─────────────────────────┘        │             │
//  │    │                                       │             │
//  │    │   VPN 서버가 복호화 → 원본 패킷 전달  │             │
//  │    │                                       │             │
//  │  ★ 중간에 도청자가 있어도 암호화되어 있어서 │             │
//  │    내용을 볼 수 없음!                       │             │
//  └─────────────────────────────────────────────────────────┘
//
//  VPN 종류:
//  ┌──────────────┬────────────────────────────────────────────┐
//  │ 종류         │ 설명                                        │
//  ├──────────────┼────────────────────────────────────────────┤
//  │ IPSec VPN    │ L3 계층 암호화, 기업용, 구현 복잡           │
//  │              │ 두 네트워크 간 Site-to-Site VPN에 적합      │
//  ├──────────────┼────────────────────────────────────────────┤
//  │ SSL VPN      │ 웹 브라우저로 접속 가능, 간편              │
//  │              │ 별도 클라이언트 불필요                      │
//  ├──────────────┼────────────────────────────────────────────┤
//  │ WireGuard    │ 현대적, 빠름, 코드 4000줄 (간결!)          │
//  │              │ Linux 커널에 포함, 모바일에서도 빠름        │
//  │              │ ★ 가장 추천하는 VPN 프로토콜               │
//  ├──────────────┼────────────────────────────────────────────┤
//  │ OpenVPN      │ 오픈소스, 유연, SSL/TLS 기반               │
//  │              │ 가장 널리 사용되는 VPN                      │
//  └──────────────┴────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  SSH 터널링 - "SSH로 만드는 터널"
// ════════════════════════════════════════════════════════════════════
//
//  SSH 터널링이란?
//  ──────────────
//  SSH 연결을 이용하여 다른 포트의 트래픽을 암호화하여 전달
//
//  ┌─────────────────────────────────────────────────────────┐
//  │  1. 로컬 포워딩 (Local Port Forwarding)                  │
//  │     ssh -L 8080:remote-db:3306 user@ssh-server           │
//  │                                                          │
//  │     [내 PC:8080] ──SSH터널──> [SSH서버] ──> [DB:3306]    │
//  │                                                          │
//  │     "내 PC의 8080으로 접속하면 원격 DB에 연결됨!"        │
//  │     ★ 방화벽으로 DB에 직접 접속 못할 때 유용            │
//  │                                                          │
//  │  2. 리모트 포워딩 (Remote Port Forwarding)                │
//  │     ssh -R 9090:localhost:3000 user@ssh-server           │
//  │                                                          │
//  │     [SSH서버:9090] ──SSH터널──> [내 PC:3000]             │
//  │                                                          │
//  │     "외부에서 SSH서버의 9090으로 접속하면                │
//  │      내 로컬의 3000번으로 연결됨!"                       │
//  │     ★ 내부 개발 서버를 외부에 노출할 때 유용            │
//  │       (ngrok의 원리!)                                    │
//  │                                                          │
//  │  3. 동적 포워딩 (Dynamic Port Forwarding = SOCKS)        │
//  │     ssh -D 1080 user@ssh-server                          │
//  │                                                          │
//  │     [내 PC] ──SOCKS:1080──> [SSH서버] ──> [어디든!]      │
//  │                                                          │
//  │     "SOCKS 프록시처럼 동작 - 모든 트래픽을 SSH 서버     │
//  │      경유로 전송!"                                       │
//  │     ★ 간이 VPN처럼 사용 가능                            │
//  └─────────────────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  SOCKS 프록시 - "범용 프록시"
// ════════════════════════════════════════════════════════════════════
//
//  SOCKS란?
//  ───────
//  HTTP뿐만 아니라 모든 TCP/UDP 트래픽을 프록시할 수 있는 프로토콜
//
//  HTTP Proxy vs SOCKS Proxy:
//  ┌──────────────────┬──────────────────────────────────────┐
//  │ HTTP Proxy       │ SOCKS Proxy                           │
//  ├──────────────────┼──────────────────────────────────────┤
//  │ HTTP 전용        │ 모든 프로토콜 (TCP/UDP)               │
//  │ L7 (응용 계층)   │ L5 (세션 계층)                        │
//  │ 콘텐츠 이해 가능 │ 콘텐츠 무관 (바이트 중계만)           │
//  │ 캐싱 가능        │ 캐싱 불가                             │
//  │ 설정 간편        │ 다목적 (게임, 토렌트 등에도 사용)     │
//  └──────────────────┴──────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  각 기술의 사용 시나리오 비교
// ════════════════════════════════════════════════════════════════════
//
//  ┌────────────────────┬─────────────────────────────────────────┐
//  │ 시나리오           │ 적합한 기술                              │
//  ├────────────────────┼─────────────────────────────────────────┤
//  │ 웹 서버 앞단       │ Reverse Proxy (Nginx)                   │
//  │ 서버 부하 분산     │ Load Balancer (HAProxy)                 │
//  │ MSA API 관리       │ API Gateway (Kong)                      │
//  │ 회사 인터넷 통제   │ Forward Proxy (Squid)                   │
//  │ 재택근무 사내망    │ VPN (WireGuard)                         │
//  │ 방화벽 우회 DB접속 │ SSH Local Forwarding                    │
//  │ 로컬 서버 외부공개 │ SSH Remote Forwarding / ngrok           │
//  │ 전체 트래픽 암호화 │ VPN 또는 SSH Dynamic (SOCKS)            │
//  │ 특정 사이트 차단   │ Forward Proxy + ACL                     │
//  │ DDoS 방어          │ CDN + WAF (Cloudflare)                  │
//  └────────────────────┴─────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  TCP 포트 포워딩 구현 (간이)
// ════════════════════════════════════════════════════════════════════
//
//  포트 포워딩이란?
//  ──────────────
//  특정 포트로 들어오는 연결을 다른 호스트:포트로 전달
//  "로컬 포트 A → 원격 호스트:포트 B"
//
//  ★ SSH 로컬 포워딩의 기본 원리와 동일!

void run_port_forwarder(uint16_t listen_port,
                         const char* target_host, uint16_t target_port) {
    std::cout << "\n  ── TCP 포트 포워더 시작 ──" << std::endl;
    std::cout << "  리스닝: 0.0.0.0:" << listen_port << std::endl;
    std::cout << "  대상:   " << target_host << ":" << target_port << std::endl;

    SOCKET_INIT();

    // 리스닝 소켓 생성
    SOCKET listen_sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (listen_sock == INVALID_SOCKET) {
        std::cerr << "  ✗ 소켓 생성 실패" << std::endl;
        SOCKET_CLEANUP();
        return;
    }

    int opt = 1;
    setsockopt(listen_sock, SOL_SOCKET, SO_REUSEADDR,
               reinterpret_cast<const char*>(&opt), sizeof(opt));

    struct sockaddr_in addr = {};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(listen_port);

    if (bind(listen_sock, reinterpret_cast<struct sockaddr*>(&addr),
             sizeof(addr)) == SOCKET_ERROR) {
        std::cerr << "  ✗ 바인딩 실패: " << SOCKET_ERROR_CODE << std::endl;
        CLOSE_SOCKET(listen_sock);
        SOCKET_CLEANUP();
        return;
    }

    listen(listen_sock, 5);
    std::cout << "  대기 중..." << std::endl;

    // 클라이언트 연결 수락
    struct sockaddr_in client_addr = {};
    socklen_t client_len = sizeof(client_addr);
    SOCKET client_sock = accept(listen_sock,
                                reinterpret_cast<struct sockaddr*>(&client_addr),
                                &client_len);
    if (client_sock == INVALID_SOCKET) {
        CLOSE_SOCKET(listen_sock);
        SOCKET_CLEANUP();
        return;
    }

    char client_ip[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, sizeof(client_ip));
    std::cout << "  클라이언트 연결: " << client_ip << std::endl;

    // 대상 서버에 연결
    SOCKET target_sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    struct sockaddr_in target_addr = {};
    target_addr.sin_family = AF_INET;
    target_addr.sin_port = htons(target_port);
    inet_pton(AF_INET, target_host, &target_addr.sin_addr);

    if (connect(target_sock, reinterpret_cast<struct sockaddr*>(&target_addr),
                sizeof(target_addr)) == SOCKET_ERROR) {
        std::cerr << "  ✗ 대상 서버 연결 실패" << std::endl;
        CLOSE_SOCKET(client_sock);
        CLOSE_SOCKET(listen_sock);
        SOCKET_CLEANUP();
        return;
    }
    std::cout << "  대상 서버 연결 완료: " << target_host << ":"
              << target_port << std::endl;

    // 양방향 데이터 전달 (간단 버전: 단방향만)
    // ★ 실제 구현에서는 select/poll/IOCP로 양방향 처리 필요
    char buffer[4096];
    int received;

    // 클라이언트 → 대상 서버
    received = recv(client_sock, buffer, sizeof(buffer), 0);
    if (received > 0) {
        std::cout << "  클라이언트→대상: " << received << " bytes 전달" << std::endl;
        send(target_sock, buffer, received, 0);
    }

    // 대상 서버 → 클라이언트
    received = recv(target_sock, buffer, sizeof(buffer), 0);
    if (received > 0) {
        std::cout << "  대상→클라이언트: " << received << " bytes 전달" << std::endl;
        send(client_sock, buffer, received, 0);
    }

    CLOSE_SOCKET(target_sock);
    CLOSE_SOCKET(client_sock);
    CLOSE_SOCKET(listen_sock);
    SOCKET_CLEANUP();
    std::cout << "  포트 포워더 종료" << std::endl;
}

// ════════════════════════════════════════════════════════════════════
//  간단한 HTTP 프록시 서버 구현
// ════════════════════════════════════════════════════════════════════
//
//  HTTP Forward Proxy:
//  클라이언트의 HTTP 요청을 대신 전달하고 응답을 돌려주는 서버
//
//  동작:
//  1. 클라이언트가 프록시에 "GET http://example.com/ HTTP/1.1" 전송
//  2. 프록시가 example.com에 연결
//  3. 프록시가 요청을 전달
//  4. 프록시가 응답을 클라이언트에게 전달

void run_http_proxy(uint16_t port) {
    std::cout << "\n  ── HTTP Forward Proxy 서버 시작 (포트: " << port << ") ──" << std::endl;

    SOCKET_INIT();

    SOCKET listen_sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (listen_sock == INVALID_SOCKET) {
        SOCKET_CLEANUP();
        return;
    }

    int opt = 1;
    setsockopt(listen_sock, SOL_SOCKET, SO_REUSEADDR,
               reinterpret_cast<const char*>(&opt), sizeof(opt));

    struct sockaddr_in addr = {};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port);

    if (bind(listen_sock, reinterpret_cast<struct sockaddr*>(&addr),
             sizeof(addr)) == SOCKET_ERROR) {
        std::cerr << "  ✗ 바인딩 실패" << std::endl;
        CLOSE_SOCKET(listen_sock);
        SOCKET_CLEANUP();
        return;
    }

    listen(listen_sock, 10);
    std::cout << "  프록시 대기 중..." << std::endl;
    std::cout << "  브라우저에서 프록시 설정: 127.0.0.1:" << port << std::endl;

    // 클라이언트 연결 수락
    struct sockaddr_in client_addr = {};
    socklen_t client_len = sizeof(client_addr);
    SOCKET client_sock = accept(listen_sock,
                                reinterpret_cast<struct sockaddr*>(&client_addr),
                                &client_len);
    if (client_sock == INVALID_SOCKET) {
        CLOSE_SOCKET(listen_sock);
        SOCKET_CLEANUP();
        return;
    }

    // 요청 수신
    char buffer[8192];
    int received = recv(client_sock, buffer, sizeof(buffer) - 1, 0);
    if (received <= 0) {
        CLOSE_SOCKET(client_sock);
        CLOSE_SOCKET(listen_sock);
        SOCKET_CLEANUP();
        return;
    }
    buffer[received] = '\0';

    std::cout << "\n  수신된 프록시 요청:" << std::endl;
    // 첫 줄만 출력
    std::string request(buffer);
    size_t first_line_end = request.find('\n');
    if (first_line_end != std::string::npos) {
        std::cout << "  " << request.substr(0, first_line_end) << std::endl;
    }

    // ★ URL에서 호스트 추출 (간단한 파싱)
    // "GET http://example.com/path HTTP/1.1" 형식
    std::string host;
    uint16_t target_port = 80;
    std::string path = "/";

    size_t http_pos = request.find("http://");
    if (http_pos != std::string::npos) {
        size_t host_start = http_pos + 7;
        size_t host_end = request.find('/', host_start);
        if (host_end == std::string::npos) host_end = request.find(' ', host_start);
        host = request.substr(host_start, host_end - host_start);

        // 포트 분리
        size_t colon = host.find(':');
        if (colon != std::string::npos) {
            target_port = std::stoi(host.substr(colon + 1));
            host = host.substr(0, colon);
        }

        // 경로 추출
        size_t path_end = request.find(' ', host_end);
        if (host_end < request.size() && request[host_end] == '/') {
            path = request.substr(host_end, path_end - host_end);
        }
    }

    std::cout << "  대상 호스트: " << host << ":" << target_port << std::endl;
    std::cout << "  경로: " << path << std::endl;

    if (host.empty()) {
        std::string error_resp = "HTTP/1.1 400 Bad Request\r\n\r\nInvalid proxy request";
        send(client_sock, error_resp.c_str(), static_cast<int>(error_resp.size()), 0);
    } else {
        // DNS 해석
        struct addrinfo hints = {}, *result;
        hints.ai_family = AF_INET;
        hints.ai_socktype = SOCK_STREAM;

        if (getaddrinfo(host.c_str(), std::to_string(target_port).c_str(),
                        &hints, &result) == 0) {
            // 대상 서버에 연결
            SOCKET target_sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
            if (connect(target_sock, result->ai_addr,
                        static_cast<int>(result->ai_addrlen)) == 0) {
                std::cout << "  대상 서버 연결 완료" << std::endl;

                // 요청을 프록시 형식에서 일반 형식으로 변환
                // "GET http://host/path" → "GET /path"
                std::string modified_request = "GET " + path + " HTTP/1.1\r\n"
                                               "Host: " + host + "\r\n"
                                               "Connection: close\r\n\r\n";

                send(target_sock, modified_request.c_str(),
                     static_cast<int>(modified_request.size()), 0);

                // 응답 수신 및 클라이언트에게 전달
                int total_forwarded = 0;
                while ((received = recv(target_sock, buffer, sizeof(buffer), 0)) > 0) {
                    send(client_sock, buffer, received, 0);
                    total_forwarded += received;
                }
                std::cout << "  전달 완료: " << total_forwarded << " bytes" << std::endl;
            }
            CLOSE_SOCKET(target_sock);
            freeaddrinfo(result);
        } else {
            std::cerr << "  ✗ DNS 해석 실패: " << host << std::endl;
        }
    }

    CLOSE_SOCKET(client_sock);
    CLOSE_SOCKET(listen_sock);
    SOCKET_CLEANUP();
    std::cout << "  프록시 종료" << std::endl;
}

// ════════════════════════════════════════════════════════════════════
//  메인 함수
// ════════════════════════════════════════════════════════════════════

int main(int argc, char* argv[]) {
    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;
    std::cout << "  프록시, 게이트웨이, 터널링 완전 정복" << std::endl;
    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;

    // 명령행 모드
    if (argc > 1) {
        std::string mode = argv[1];

        // HTTP 프록시 모드
        if (mode == "proxy") {
            uint16_t port = (argc > 2) ? std::stoi(argv[2]) : 8888;
            run_http_proxy(port);
            return 0;
        }
        // 포트 포워딩 모드
        else if (mode == "forward" && argc > 3) {
            uint16_t listen_port = std::stoi(argv[2]);
            std::string target = argv[3];
            uint16_t target_port = (argc > 4) ? std::stoi(argv[4]) : 80;

            run_port_forwarder(listen_port, target.c_str(), target_port);
            return 0;
        }
    }

    std::cout << R"(
  ┌───────────────────────────────────────────────────────┐
  │  사용법:                                               │
  │    ./proxy_gateway proxy [port]                        │
  │      → HTTP Forward Proxy 서버 실행                   │
  │                                                        │
  │    ./proxy_gateway forward <listen-port> <host> [port] │
  │      → TCP 포트 포워더 실행                            │
  │                                                        │
  │  예시:                                                 │
  │    ./proxy_gateway proxy 8888                          │
  │    ./proxy_gateway forward 8080 192.168.1.100 80       │
  └───────────────────────────────────────────────────────┘
)" << std::endl;

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  1. 로드 밸런서 시뮬레이션
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  1. 로드 밸런서 시뮬레이션" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    LoadBalancer lb;
    lb.add_server("web-01", "192.168.1.10:8080", 5);
    lb.add_server("web-02", "192.168.1.11:8080", 3);
    lb.add_server("web-03", "192.168.1.12:8080", 2);

    std::cout << "\n  ── Round Robin 시뮬레이션 (10개 요청) ──" << std::endl;
    for (int i = 0; i < 10; i++) {
        auto* server = lb.round_robin();
        if (server) {
            std::cout << "  요청 " << std::setw(2) << (i + 1)
                      << " → " << server->name << " (" << server->address << ")" << std::endl;
            lb.disconnect(server);
        }
    }

    lb.print_status();

    // 서버 장애 시뮬레이션
    std::cout << "\n  ── 서버 장애 시뮬레이션 ──" << std::endl;
    std::cout << "  web-02 서버 다운!" << std::endl;
    lb.set_health("web-02", false);

    std::cout << "  이후 요청은 web-01, web-03에만 분배:" << std::endl;
    for (int i = 0; i < 4; i++) {
        auto* server = lb.round_robin();
        if (server) {
            std::cout << "  요청 → " << server->name << std::endl;
            lb.disconnect(server);
        }
    }

    lb.print_status();

    // IP Hash 시뮬레이션
    lb.set_health("web-02", true);  // 복구
    std::cout << "\n  ── IP Hash 시뮬레이션 ──" << std::endl;
    std::cout << "  ★ 같은 IP는 항상 같은 서버로! (세션 유지)" << std::endl;

    std::vector<std::string> client_ips = {
        "10.0.0.1", "10.0.0.2", "10.0.0.3",
        "10.0.0.1", "10.0.0.1", "10.0.0.2"
    };

    for (const auto& ip : client_ips) {
        auto* server = lb.ip_hash(ip);
        if (server) {
            std::cout << "  " << std::setw(10) << ip
                      << " → " << server->name << std::endl;
            lb.disconnect(server);
        }
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  2. API Gateway 시뮬레이션
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  2. API Gateway 시뮬레이션" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    APIGateway gateway;
    gateway.add_route("/api/users", "user-service", true, 100);
    gateway.add_route("/api/orders", "order-service", true, 50);
    gateway.add_route("/api/products", "product-service", false, 200);
    gateway.add_route("/health", "gateway-internal", false, 1000);
    gateway.print_routes();

    // 시나리오 1: 인증 없이 인증 필요 API 접근
    gateway.handle_request("/api/users", "10.0.0.1");

    // 시나리오 2: 인증 포함 접근
    gateway.handle_request("/api/users", "10.0.0.1", "Bearer eyJhbGciOiJIUzI1NiJ9...");

    // 시나리오 3: 인증 불필요 API
    gateway.handle_request("/api/products", "10.0.0.2");

    // 시나리오 4: 존재하지 않는 API
    gateway.handle_request("/api/unknown", "10.0.0.3");

    // 시나리오 5: 헬스 체크
    gateway.handle_request("/health", "monitoring-server");

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  3. VPN 터널링 과정 시뮬레이션
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  3. VPN 터널링 시뮬레이션" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    std::cout << R"(
  ── VPN 없이 접속 ──
  [내 PC: 192.168.1.10]
    │
    │── GET http://intranet.company.com ──X── 접속 불가!
    │   (회사 내부망이라 인터넷에서 접속 못함)

  ── VPN 사용 시 ──
  [내 PC: 192.168.1.10]
    │
    │── VPN 연결 수립 (WireGuard/OpenVPN)
    │   할당받은 VPN IP: 10.8.0.2
    │
    │── 원본 패킷:
    │   src: 10.8.0.2
    │   dst: 10.0.0.50 (인트라넷)
    │   data: GET /dashboard
    │
    │── 암호화 + 캡슐화:
    │   src: 192.168.1.10 (실제 IP)
    │   dst: VPN서버 (203.0.113.1)
    │   data: [암호화된 원본 패킷]
    │
    │── 인터넷 경유 ──→ [VPN 서버: 203.0.113.1]
    │                      │
    │                      │── 복호화 + 역캡슐화
    │                      │── 원본 패킷을 내부망으로 전달
    │                      │── src: 10.8.0.2
    │                      │── dst: 10.0.0.50
    │                      │
    │                      └──→ [인트라넷: 10.0.0.50]
    │
    │  ★ 결과: 마치 회사 내부에 있는 것처럼 접속 성공!
)" << std::endl;

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  4. SSH 터널링 시나리오
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  4. SSH 터널링 실전 시나리오" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    std::cout << R"(
  ── 시나리오 1: 원격 DB 접속 (로컬 포워딩) ──

  상황: 방화벽 때문에 DB(3306)에 직접 접속 불가
        하지만 SSH(22)로는 접속 가능!

  명령어: ssh -L 3306:db-server:3306 user@jump-server

  [내 PC]                [점프 서버]        [DB 서버]
  localhost:3306 ──SSH──> jump-server ──→ db-server:3306

  MySQL 접속: mysql -h 127.0.0.1 -P 3306
  → 마치 DB가 로컬에 있는 것처럼!

  ── 시나리오 2: 개발 서버 외부 공개 (리모트 포워딩) ──

  상황: 내 PC에서 실행 중인 개발 서버(3000)를
        외부에서 접속하게 하고 싶음 (클라이언트에게 데모)

  명령어: ssh -R 9090:localhost:3000 user@public-server

  [외부 사용자]          [공개 서버]        [내 PC]
  public-server:9090 ──SSH──────────> localhost:3000

  데모 URL: http://public-server:9090
  → 내 로컬 개발 서버가 인터넷에서 접속 가능!

  ── 시나리오 3: 전체 트래픽 프록시 (동적 포워딩) ──

  상황: 해외 출장 중, 모든 인터넷 트래픽을 한국 서버 경유

  명령어: ssh -D 1080 user@korea-server
  브라우저 SOCKS 프록시: localhost:1080

  [내 PC (해외)]        [한국 서버]         [인터넷]
  브라우저 ──SOCKS1080──> korea-server ──→ 목적지
  → 한국 IP로 접속됨!
)" << std::endl;

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  정리
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  정리: 프록시/게이트웨이/터널링 핵심 요약" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    std::cout << R"(
  ★ 기억해야 할 핵심:

  1. Forward Proxy = 클라이언트 대리 (IP 숨김, 필터링)
  2. Reverse Proxy = 서버 대리 (로드밸런싱, SSL, 캐싱)
  3. Load Balancer = 트래픽 분산 (Round Robin, Least Conn)
  4. API Gateway = MSA의 단일 진입점 (인증, 라우팅, Rate Limit)
  5. VPN = 암호화된 터널로 사설망 접속
  6. SSH Tunnel = SSH로 만드는 간이 VPN/포트포워딩

  ★ 실무 팁:
  - Nginx로 리버스 프록시 + 로드밸런싱 설정 (가장 흔함!)
  - WireGuard로 간편한 VPN 구축 (OpenVPN보다 빠름)
  - SSH -L 로 방화벽 뒤 DB 접속 (개발자 필수 스킬!)
  - API Gateway는 MSA에서 필수 (Kong, AWS API GW)
  - Cloudflare = CDN + DDoS 방어 + 리버스 프록시 통합
)" << std::endl;

    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;
    std::cout << "  프록시/게이트웨이/터널링 학습 완료!" << std::endl;
    std::cout << "  네트워크 학습 전체 과정을 마칩니다." << std::endl;
    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;

    return 0;
}
