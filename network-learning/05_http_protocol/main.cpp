/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  네트워크 학습 05단계: HTTP 프로토콜 완전 정복
  ─────────────────────────────────────────────────
  HTTP/1.0~3, 요청/응답 구조, 상태 코드,
  HTTPS/TLS, C++로 HTTP 서버/클라이언트 구현

  ■ 컴파일 방법:
      g++ -std=c++17 -Wall -lws2_32 -o http_protocol main.cpp

  ■ 이 파일을 배우면 할 수 있는 것:
      - HTTP 프로토콜의 구조와 동작 원리 완전 이해
      - 상태 코드, 헤더, 메서드의 의미 파악
      - HTTPS와 TLS 핸드셰이크 과정 이해
      - C++로 간단한 HTTP 서버/클라이언트 구현

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
#include <fstream>

// ┌───────────────────────────────────────────────────────────────────┐
// │  ★ HTTP (HyperText Transfer Protocol)란?                        │
// │                                                                   │
// │  웹 브라우저와 웹 서버가 통신하는 규칙 (프로토콜)                │
// │                                                                   │
// │  비유: 식당에서 주문하기                                          │
// │    손님(클라이언트):  "김치찌개 하나 주세요" (요청/Request)       │
// │    주방(서버):        "네, 여기 있습니다!" (응답/Response)        │
// │                                                                   │
// │  특징:                                                            │
// │    - 텍스트 기반 (사람이 읽을 수 있음!)                          │
// │    - 비연결성 (요청→응답→연결끝, HTTP/1.0)                      │
// │    - 무상태성 (이전 요청을 기억하지 않음)                        │
// │    - TCP 포트 80 (HTTP), 443 (HTTPS)                              │
// └───────────────────────────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  HTTP 버전별 비교
// ════════════════════════════════════════════════════════════════════
//
//  ┌──────────┬─────────────────────────────────────────────────────┐
//  │ 버전     │ 특징                                                │
//  ├──────────┼─────────────────────────────────────────────────────┤
//  │ HTTP/1.0 │ - 요청마다 새 TCP 연결 (느림!)                      │
//  │ (1996)   │ - 1요청 = 1연결 = 1응답                             │
//  │          │ - Connection: close가 기본                          │
//  ├──────────┼─────────────────────────────────────────────────────┤
//  │ HTTP/1.1 │ - Keep-Alive (연결 재사용!) ← 큰 개선              │
//  │ (1997)   │ - 파이프라이닝 (여러 요청 연속 전송)                │
//  │          │ - Host 헤더 필수 (가상 호스팅 가능)                 │
//  │          │ - Chunked Transfer (스트리밍)                        │
//  │          │ ★ 단점: Head-of-Line Blocking                      │
//  ├──────────┼─────────────────────────────────────────────────────┤
//  │ HTTP/2   │ - 바이너리 프로토콜 (더 이상 텍스트 아님)           │
//  │ (2015)   │ - 멀티플렉싱 (하나의 연결로 동시 요청/응답)        │
//  │          │ - 헤더 압축 (HPACK)                                  │
//  │          │ - 서버 푸시 (요청 안 했는데 미리 보냄)              │
//  │          │ ★ TCP 기반이라 TCP HOL Blocking은 남아있음          │
//  ├──────────┼─────────────────────────────────────────────────────┤
//  │ HTTP/3   │ - QUIC 기반 (UDP 위에 구축!)                        │
//  │ (2022)   │ - TCP HOL Blocking 해결                              │
//  │          │ - 0-RTT 연결 (빠른 연결 수립)                       │
//  │          │ - 기본 TLS 1.3 내장                                  │
//  │          │ ★ 구글이 개발, 점점 확산 중                         │
//  └──────────┴─────────────────────────────────────────────────────┘
//
//  비유로 이해하기:
//    HTTP/1.0 = 매번 새 택배 기사 호출 (비효율)
//    HTTP/1.1 = 한 택배 기사가 여러 번 왕복 (효율적)
//    HTTP/2   = 택배 기사가 동시에 여러 소포 배달 (매우 효율적)
//    HTTP/3   = 드론 배달 (TCP 도로 막힘 자체를 우회!)

// ════════════════════════════════════════════════════════════════════
//  HTTP 요청 구조
// ════════════════════════════════════════════════════════════════════
//
//  ┌───────────────────────────────────────────────────┐
//  │  HTTP 요청 (Request) 구조                         │
//  │                                                    │
//  │  ┌───── 요청 라인 (Request Line) ─────┐           │
//  │  │  GET /index.html HTTP/1.1          │           │
//  │  │  ^메서드  ^경로       ^버전        │           │
//  │  └────────────────────────────────────┘           │
//  │  ┌───── 헤더 (Headers) ───────────────┐           │
//  │  │  Host: www.example.com             │           │
//  │  │  User-Agent: Mozilla/5.0           │           │
//  │  │  Accept: text/html                 │           │
//  │  │  Accept-Language: ko-KR            │           │
//  │  │  Connection: keep-alive            │           │
//  │  └────────────────────────────────────┘           │
//  │  (빈 줄 = 헤더의 끝)                              │
//  │  ┌───── 바디 (Body, 선택) ────────────┐           │
//  │  │  (POST 요청 시 데이터)             │           │
//  │  │  username=admin&password=1234      │           │
//  │  └────────────────────────────────────┘           │
//  └───────────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  HTTP 메서드 (동사)
// ════════════════════════════════════════════════════════════════════
//
//  ┌─────────┬───────────────────────────────────────────────┐
//  │ 메서드  │ 설명                                           │
//  ├─────────┼───────────────────────────────────────────────┤
//  │ GET     │ 리소스 조회 (읽기) - 가장 많이 사용!           │
//  │         │ 비유: "메뉴판 보여주세요"                      │
//  ├─────────┼───────────────────────────────────────────────┤
//  │ POST    │ 리소스 생성 (쓰기)                             │
//  │         │ 비유: "김치찌개 하나 주문합니다"               │
//  ├─────────┼───────────────────────────────────────────────┤
//  │ PUT     │ 리소스 전체 수정                                │
//  │         │ 비유: "주문 변경 - 된장찌개로 바꿔주세요"      │
//  ├─────────┼───────────────────────────────────────────────┤
//  │ PATCH   │ 리소스 부분 수정                                │
//  │         │ 비유: "밥 곱빼기로 변경해주세요"               │
//  ├─────────┼───────────────────────────────────────────────┤
//  │ DELETE  │ 리소스 삭제                                     │
//  │         │ 비유: "주문 취소합니다"                        │
//  ├─────────┼───────────────────────────────────────────────┤
//  │ HEAD    │ GET과 동일하지만 바디 없이 헤더만 응답         │
//  │ OPTIONS │ 지원하는 메서드 목록 조회 (CORS 프리플라이트)  │
//  └─────────┴───────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  HTTP 응답 구조
// ════════════════════════════════════════════════════════════════════
//
//  ┌───────────────────────────────────────────────────┐
//  │  HTTP 응답 (Response) 구조                        │
//  │                                                    │
//  │  ┌───── 상태 라인 (Status Line) ──────┐           │
//  │  │  HTTP/1.1 200 OK                   │           │
//  │  │  ^버전    ^코드 ^설명              │           │
//  │  └────────────────────────────────────┘           │
//  │  ┌───── 헤더 (Headers) ───────────────┐           │
//  │  │  Content-Type: text/html           │           │
//  │  │  Content-Length: 1234              │           │
//  │  │  Server: Apache/2.4               │           │
//  │  │  Set-Cookie: session=abc123       │           │
//  │  └────────────────────────────────────┘           │
//  │  (빈 줄)                                          │
//  │  ┌───── 바디 (Body) ──────────────────┐           │
//  │  │  <html>                            │           │
//  │  │    <body>Hello World!</body>       │           │
//  │  │  </html>                           │           │
//  │  └────────────────────────────────────┘           │
//  └───────────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  HTTP 상태 코드 - "서버의 대답 종류"
// ════════════════════════════════════════════════════════════════════
//
//  ┌──────┬──────────────────────────────────────────────────────┐
//  │ 코드 │ 의미                                                  │
//  ├──────┼──────────────────────────────────────────────────────┤
//  │      │ ★ 1xx: 정보 (처리 중)                               │
//  │ 100  │ Continue - "계속 보내세요"                            │
//  │ 101  │ Switching Protocols - "프로토콜 변경" (WebSocket)     │
//  ├──────┼──────────────────────────────────────────────────────┤
//  │      │ ★ 2xx: 성공                                         │
//  │ 200  │ OK - "요청 성공!"                                    │
//  │ 201  │ Created - "새로 만들었어요" (POST 성공)              │
//  │ 204  │ No Content - "성공했지만 응답 바디 없음"             │
//  ├──────┼──────────────────────────────────────────────────────┤
//  │      │ ★ 3xx: 리다이렉션 (다른 곳으로 이동)               │
//  │ 301  │ Moved Permanently - "영구 이동" (SEO에 중요)        │
//  │ 302  │ Found - "임시 이동"                                  │
//  │ 304  │ Not Modified - "변경 없음, 캐시 사용해"             │
//  ├──────┼──────────────────────────────────────────────────────┤
//  │      │ ★ 4xx: 클라이언트 오류 (네 잘못!)                  │
//  │ 400  │ Bad Request - "요청이 잘못됐어"                      │
//  │ 401  │ Unauthorized - "인증 필요" (로그인 해!)             │
//  │ 403  │ Forbidden - "권한 없음" (로그인 했지만 금지)        │
//  │ 404  │ Not Found - "페이지 없음" (가장 유명!)              │
//  │ 405  │ Method Not Allowed - "이 메서드는 안 됨"            │
//  │ 429  │ Too Many Requests - "너무 많이 요청!" (Rate Limit)  │
//  ├──────┼──────────────────────────────────────────────────────┤
//  │      │ ★ 5xx: 서버 오류 (내 잘못!)                        │
//  │ 500  │ Internal Server Error - "서버에 뭔가 문제 발생"     │
//  │ 502  │ Bad Gateway - "게이트웨이가 잘못된 응답 받음"       │
//  │ 503  │ Service Unavailable - "서버 과부하/점검 중"         │
//  │ 504  │ Gateway Timeout - "게이트웨이 타임아웃"             │
//  └──────┴──────────────────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  주요 HTTP 헤더
// ════════════════════════════════════════════════════════════════════
//
//  ┌──────────────────┬──────────────────────────────────────────┐
//  │ 헤더             │ 설명                                      │
//  ├──────────────────┼──────────────────────────────────────────┤
//  │ Host             │ 요청 대상 도메인 (가상 호스팅 필수)       │
//  │ Content-Type     │ 바디의 형식 (text/html, application/json)│
//  │ Content-Length   │ 바디의 크기 (바이트)                      │
//  │ Authorization    │ 인증 정보 (Bearer token, Basic auth)     │
//  │ Cookie           │ 클라이언트 → 서버로 쿠키 전송            │
//  │ Set-Cookie       │ 서버 → 클라이언트로 쿠키 설정            │
//  │ Cache-Control    │ 캐싱 정책 (max-age, no-cache, no-store) │
//  │ Accept           │ 클라이언트가 원하는 응답 형식            │
//  │ User-Agent       │ 브라우저/클라이언트 정보                 │
//  │ Referer          │ 이전 페이지 URL                          │
//  │ X-Forwarded-For  │ 프록시 경유 시 원래 클라이언트 IP        │
//  │ Access-Control-* │ CORS 관련 헤더 (교차 출처 요청)          │
//  └──────────────────┴──────────────────────────────────────────┘

// ════════════════════════════════════════════════════════════════════
//  HTTPS와 TLS - "암호화된 HTTP"
// ════════════════════════════════════════════════════════════════════
//
//  HTTP vs HTTPS:
//    HTTP:  평문 전송 → 도청 가능! 위험!
//    HTTPS: TLS로 암호화 → 도청 불가! 안전!
//
//  TLS 핸드셰이크 과정 (간략):
//
//  ┌──────────────────────────────────────────────────────────┐
//  │              TLS 1.3 핸드셰이크                           │
//  │                                                           │
//  │   Client                              Server              │
//  │     │                                    │                │
//  │     │── ClientHello ───────────────────>│ 1 RTT          │
//  │     │   (지원하는 암호 스위트 목록)      │                │
//  │     │   (클라이언트 랜덤값)             │                │
//  │     │                                    │                │
//  │     │<── ServerHello ──────────────────│                 │
//  │     │   (선택한 암호 스위트)             │                │
//  │     │   (서버 인증서)                    │                │
//  │     │   (키 교환 데이터)                 │                │
//  │     │                                    │                │
//  │     │── Finished ──────────────────────>│ 핸드셰이크     │
//  │     │   (검증 완료)                      │ 완료!         │
//  │     │                                    │                │
//  │     │ ←─── 암호화된 데이터 전송 ────→ │               │
//  └──────────────────────────────────────────────────────────┘
//
//  인증서 체인:
//
//  ┌─────────────┐
//  │ 루트 CA      │ ← OS/브라우저에 내장된 신뢰할 수 있는 기관
//  │ (Root)       │    예: DigiCert, Let's Encrypt
//  └──────┬──────┘
//         │ 서명
//  ┌──────▼──────┐
//  │ 중간 CA      │ ← 루트가 서명한 중간 기관
//  │(Intermediate)│
//  └──────┬──────┘
//         │ 서명
//  ┌──────▼──────┐
//  │ 서버 인증서  │ ← 중간 CA가 서명한 서버의 인증서
//  │ (Server)     │    "이 서버는 진짜 example.com 입니다"
//  └─────────────┘

// ════════════════════════════════════════════════════════════════════
//  HTTP 요청/응답 파서 클래스
// ════════════════════════════════════════════════════════════════════

// HTTP 요청 구조체
struct HttpRequest {
    std::string method;                           // GET, POST, etc
    std::string path;                             // /index.html
    std::string version;                          // HTTP/1.1
    std::map<std::string, std::string> headers;   // 헤더 맵
    std::string body;                             // 바디

    // 요청 문자열에서 파싱
    static HttpRequest parse(const std::string& raw) {
        HttpRequest req;
        std::istringstream stream(raw);
        std::string line;

        // 1. 요청 라인 파싱
        if (std::getline(stream, line)) {
            // 끝의 \r 제거
            if (!line.empty() && line.back() == '\r') line.pop_back();
            std::istringstream line_stream(line);
            line_stream >> req.method >> req.path >> req.version;
        }

        // 2. 헤더 파싱 (빈 줄이 나올 때까지)
        while (std::getline(stream, line)) {
            if (!line.empty() && line.back() == '\r') line.pop_back();
            if (line.empty()) break;  // 빈 줄 = 헤더의 끝

            size_t colon = line.find(':');
            if (colon != std::string::npos) {
                std::string key = line.substr(0, colon);
                std::string value = line.substr(colon + 1);
                // 앞뒤 공백 제거
                while (!value.empty() && value[0] == ' ') value.erase(0, 1);
                req.headers[key] = value;
            }
        }

        // 3. 나머지는 바디
        std::ostringstream body_stream;
        body_stream << stream.rdbuf();
        req.body = body_stream.str();

        return req;
    }

    // 요청을 문자열로 직렬화
    std::string to_string() const {
        std::ostringstream oss;
        oss << method << " " << path << " " << version << "\r\n";
        for (const auto& [key, value] : headers) {
            oss << key << ": " << value << "\r\n";
        }
        oss << "\r\n";
        oss << body;
        return oss.str();
    }

    // 요청 정보 출력
    void print() const {
        std::cout << "  ┌───────── HTTP 요청 ─────────┐" << std::endl;
        std::cout << "  │ " << method << " " << path << " " << version << std::endl;
        for (const auto& [k, v] : headers) {
            std::cout << "  │ " << k << ": " << v << std::endl;
        }
        if (!body.empty()) {
            std::cout << "  │ (바디)" << std::endl;
            std::cout << "  │ " << body << std::endl;
        }
        std::cout << "  └────────────────────────────┘" << std::endl;
    }
};

// HTTP 응답 구조체
struct HttpResponse {
    std::string version;                          // HTTP/1.1
    int status_code;                              // 200, 404, etc
    std::string status_text;                      // OK, Not Found, etc
    std::map<std::string, std::string> headers;   // 헤더 맵
    std::string body;                             // 바디

    // 응답을 문자열로 직렬화
    std::string to_string() const {
        std::ostringstream oss;
        oss << version << " " << status_code << " " << status_text << "\r\n";
        for (const auto& [key, value] : headers) {
            oss << key << ": " << value << "\r\n";
        }
        oss << "\r\n";
        oss << body;
        return oss.str();
    }

    // 응답 정보 출력
    void print() const {
        std::cout << "  ┌───────── HTTP 응답 ─────────┐" << std::endl;
        std::cout << "  │ " << version << " " << status_code << " " << status_text << std::endl;
        for (const auto& [k, v] : headers) {
            std::cout << "  │ " << k << ": " << v << std::endl;
        }
        if (!body.empty()) {
            std::cout << "  │ (바디, " << body.size() << " bytes)" << std::endl;
            // 바디가 길면 줄여서 출력
            if (body.size() > 200) {
                std::cout << "  │ " << body.substr(0, 200) << "..." << std::endl;
            } else {
                std::cout << "  │ " << body << std::endl;
            }
        }
        std::cout << "  └────────────────────────────┘" << std::endl;
    }
};

// ════════════════════════════════════════════════════════════════════
//  HTTP 상태 코드 유틸리티
// ════════════════════════════════════════════════════════════════════

std::string status_text(int code) {
    switch (code) {
        case 200: return "OK";
        case 201: return "Created";
        case 204: return "No Content";
        case 301: return "Moved Permanently";
        case 302: return "Found";
        case 304: return "Not Modified";
        case 400: return "Bad Request";
        case 401: return "Unauthorized";
        case 403: return "Forbidden";
        case 404: return "Not Found";
        case 405: return "Method Not Allowed";
        case 429: return "Too Many Requests";
        case 500: return "Internal Server Error";
        case 502: return "Bad Gateway";
        case 503: return "Service Unavailable";
        case 504: return "Gateway Timeout";
        default:  return "Unknown";
    }
}

// MIME 타입 결정 (파일 확장자 기반)
std::string get_mime_type(const std::string& path) {
    if (path.find(".html") != std::string::npos) return "text/html";
    if (path.find(".css") != std::string::npos) return "text/css";
    if (path.find(".js") != std::string::npos) return "application/javascript";
    if (path.find(".json") != std::string::npos) return "application/json";
    if (path.find(".png") != std::string::npos) return "image/png";
    if (path.find(".jpg") != std::string::npos) return "image/jpeg";
    if (path.find(".gif") != std::string::npos) return "image/gif";
    if (path.find(".svg") != std::string::npos) return "image/svg+xml";
    if (path.find(".ico") != std::string::npos) return "image/x-icon";
    if (path.find(".txt") != std::string::npos) return "text/plain";
    if (path.find(".xml") != std::string::npos) return "application/xml";
    return "application/octet-stream";  // 기본값 (바이너리)
}

// ════════════════════════════════════════════════════════════════════
//  간단한 HTTP 서버 구현
// ════════════════════════════════════════════════════════════════════
//
//  ★ 이것은 학습용 간이 서버입니다!
//     실제 프로덕션에서는 nginx, Apache, Node.js 등을 사용하세요.
//
//  동작 흐름:
//  1. TCP 소켓 생성 및 바인딩
//  2. 클라이언트 연결 대기 (listen)
//  3. 연결 수락 (accept)
//  4. HTTP 요청 수신 및 파싱
//  5. 라우팅 (URL에 따라 다른 처리)
//  6. HTTP 응답 전송
//  7. 연결 종료

// 라우트 핸들러 타입
using RouteHandler = std::function<HttpResponse(const HttpRequest&)>;

class SimpleHttpServer {
private:
    uint16_t port_;
    std::map<std::string, RouteHandler> routes_;  // 라우팅 테이블

public:
    SimpleHttpServer(uint16_t port) : port_(port) {}

    // 라우트 등록
    // ★ REST API 패턴: "GET /users", "POST /users" 등
    void route(const std::string& method_path, RouteHandler handler) {
        routes_[method_path] = handler;
    }

    // 서버 실행
    void run() {
        std::cout << "\n  ── HTTP 서버 시작 ──" << std::endl;
        std::cout << "  포트: " << port_ << std::endl;
        std::cout << "  http://localhost:" << port_ << " 에서 접속 가능!" << std::endl;

        SOCKET_INIT();

        SOCKET server_sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (server_sock == INVALID_SOCKET) {
            std::cerr << "  ✗ 소켓 생성 실패" << std::endl;
            SOCKET_CLEANUP();
            return;
        }

        // SO_REUSEADDR 설정
        int opt = 1;
        setsockopt(server_sock, SOL_SOCKET, SO_REUSEADDR,
                   reinterpret_cast<const char*>(&opt), sizeof(opt));

        struct sockaddr_in addr = {};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(port_);

        if (bind(server_sock, reinterpret_cast<struct sockaddr*>(&addr),
                 sizeof(addr)) == SOCKET_ERROR) {
            std::cerr << "  ✗ 바인딩 실패: " << SOCKET_ERROR_CODE << std::endl;
            CLOSE_SOCKET(server_sock);
            SOCKET_CLEANUP();
            return;
        }

        if (listen(server_sock, 10) == SOCKET_ERROR) {
            std::cerr << "  ✗ 리스닝 실패" << std::endl;
            CLOSE_SOCKET(server_sock);
            SOCKET_CLEANUP();
            return;
        }

        std::cout << "  등록된 라우트:" << std::endl;
        for (const auto& [route, _] : routes_) {
            std::cout << "    " << route << std::endl;
        }
        std::cout << "\n  대기 중... (Ctrl+C로 종료)" << std::endl;

        // 클라이언트 처리 루프 (1회만 처리 후 종료하는 데모 모드)
        struct sockaddr_in client_addr = {};
        socklen_t client_len = sizeof(client_addr);

        SOCKET client_sock = accept(server_sock,
                                    reinterpret_cast<struct sockaddr*>(&client_addr),
                                    &client_len);
        if (client_sock == INVALID_SOCKET) {
            CLOSE_SOCKET(server_sock);
            SOCKET_CLEANUP();
            return;
        }

        char client_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, sizeof(client_ip));
        std::cout << "\n  클라이언트 연결: " << client_ip << ":"
                  << ntohs(client_addr.sin_port) << std::endl;

        // 요청 수신
        char buffer[4096];
        int received = recv(client_sock, buffer, sizeof(buffer) - 1, 0);
        if (received > 0) {
            buffer[received] = '\0';

            // 요청 파싱
            HttpRequest req = HttpRequest::parse(buffer);
            std::cout << "\n  수신된 요청:" << std::endl;
            req.print();

            // 라우팅
            std::string route_key = req.method + " " + req.path;
            HttpResponse resp;

            auto it = routes_.find(route_key);
            if (it != routes_.end()) {
                resp = it->second(req);
            } else {
                // 404 Not Found
                resp.version = "HTTP/1.1";
                resp.status_code = 404;
                resp.status_text = "Not Found";
                resp.headers["Content-Type"] = "text/html; charset=utf-8";
                resp.body = "<html><body><h1>404 Not Found</h1>"
                           "<p>요청한 페이지를 찾을 수 없습니다.</p></body></html>";
                resp.headers["Content-Length"] = std::to_string(resp.body.size());
            }

            // 응답 전송
            std::string resp_str = resp.to_string();
            send(client_sock, resp_str.c_str(),
                 static_cast<int>(resp_str.size()), 0);

            std::cout << "\n  전송된 응답:" << std::endl;
            resp.print();
        }

        CLOSE_SOCKET(client_sock);
        CLOSE_SOCKET(server_sock);
        SOCKET_CLEANUP();
        std::cout << "  서버 종료" << std::endl;
    }
};

// ════════════════════════════════════════════════════════════════════
//  HTTP 클라이언트 구현
// ════════════════════════════════════════════════════════════════════

class SimpleHttpClient {
public:
    // GET 요청 전송
    static std::string get(const std::string& host, uint16_t port,
                           const std::string& path) {
        std::cout << "\n  ── HTTP GET 요청 ──" << std::endl;
        std::cout << "  대상: " << host << ":" << port << path << std::endl;

        SOCKET_INIT();

        SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (sock == INVALID_SOCKET) {
            SOCKET_CLEANUP();
            return "";
        }

        struct sockaddr_in addr = {};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port);
        inet_pton(AF_INET, host.c_str(), &addr.sin_addr);

        if (connect(sock, reinterpret_cast<struct sockaddr*>(&addr),
                    sizeof(addr)) == SOCKET_ERROR) {
            std::cerr << "  ✗ 연결 실패" << std::endl;
            CLOSE_SOCKET(sock);
            SOCKET_CLEANUP();
            return "";
        }

        // HTTP 요청 생성
        HttpRequest req;
        req.method = "GET";
        req.path = path;
        req.version = "HTTP/1.1";
        req.headers["Host"] = host + ":" + std::to_string(port);
        req.headers["User-Agent"] = "CPP-HttpClient/1.0";
        req.headers["Accept"] = "*/*";
        req.headers["Connection"] = "close";

        std::string req_str = req.to_string();
        send(sock, req_str.c_str(), static_cast<int>(req_str.size()), 0);

        // 응답 수신
        std::string response;
        char buffer[4096];
        int received;
        while ((received = recv(sock, buffer, sizeof(buffer) - 1, 0)) > 0) {
            buffer[received] = '\0';
            response += buffer;
        }

        CLOSE_SOCKET(sock);
        SOCKET_CLEANUP();

        return response;
    }
};

// ════════════════════════════════════════════════════════════════════
//  REST API 패턴 설명
// ════════════════════════════════════════════════════════════════════
//
//  REST (Representational State Transfer) API:
//  ────────────────────────────────────────────
//  리소스(자원)를 URL로 표현하고, HTTP 메서드로 조작하는 패턴
//
//  ┌─────────────────────────────────────────────────────────────┐
//  │              REST API 설계 예시 (사용자 관리)                │
//  ├────────────┬───────────────┬─────────────────────────────── ┤
//  │ 메서드     │ URL           │ 동작                           │
//  ├────────────┼───────────────┼────────────────────────────────┤
//  │ GET        │ /users        │ 전체 사용자 목록 조회          │
//  │ GET        │ /users/123    │ 123번 사용자 상세 조회         │
//  │ POST       │ /users        │ 새 사용자 생성                 │
//  │ PUT        │ /users/123    │ 123번 사용자 전체 수정         │
//  │ PATCH      │ /users/123    │ 123번 사용자 부분 수정         │
//  │ DELETE     │ /users/123    │ 123번 사용자 삭제              │
//  └────────────┴───────────────┴────────────────────────────────┘
//
//  REST API 요청/응답 예시:
//
//  요청:
//    POST /users HTTP/1.1
//    Content-Type: application/json
//    Authorization: Bearer eyJhbGciOi...
//
//    {"name": "김철수", "email": "kim@example.com"}
//
//  응답:
//    HTTP/1.1 201 Created
//    Content-Type: application/json
//
//    {"id": 42, "name": "김철수", "email": "kim@example.com"}

// ════════════════════════════════════════════════════════════════════
//  메인 함수
// ════════════════════════════════════════════════════════════════════

int main(int argc, char* argv[]) {
    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;
    std::cout << "  HTTP 프로토콜 완전 정복" << std::endl;
    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;

    // ── 서버 모드 ──
    if (argc > 1 && std::string(argv[1]) == "server") {
        uint16_t port = (argc > 2) ? std::stoi(argv[2]) : 8080;
        SimpleHttpServer server(port);

        // 라우트 등록
        // ★ 이것이 REST API의 핵심: URL과 핸들러 매핑!

        // 메인 페이지
        server.route("GET /", [](const HttpRequest& req) -> HttpResponse {
            HttpResponse resp;
            resp.version = "HTTP/1.1";
            resp.status_code = 200;
            resp.status_text = "OK";
            resp.headers["Content-Type"] = "text/html; charset=utf-8";
            resp.body = R"(<!DOCTYPE html>
<html>
<head><title>C++ HTTP Server</title></head>
<body>
  <h1>C++ HTTP 서버에 오신 것을 환영합니다!</h1>
  <p>이 서버는 C++ 소켓으로 만들어졌습니다.</p>
  <ul>
    <li><a href="/about">소개</a></li>
    <li><a href="/api/hello">API 예제</a></li>
  </ul>
</body>
</html>)";
            resp.headers["Content-Length"] = std::to_string(resp.body.size());
            resp.headers["Server"] = "CPP-HttpServer/1.0";
            return resp;
        });

        // 소개 페이지
        server.route("GET /about", [](const HttpRequest& req) -> HttpResponse {
            HttpResponse resp;
            resp.version = "HTTP/1.1";
            resp.status_code = 200;
            resp.status_text = "OK";
            resp.headers["Content-Type"] = "text/html; charset=utf-8";
            resp.body = "<html><body><h1>About</h1>"
                        "<p>C++17 + Winsock2 HTTP 학습 서버</p></body></html>";
            resp.headers["Content-Length"] = std::to_string(resp.body.size());
            return resp;
        });

        // JSON API 엔드포인트
        server.route("GET /api/hello", [](const HttpRequest& req) -> HttpResponse {
            HttpResponse resp;
            resp.version = "HTTP/1.1";
            resp.status_code = 200;
            resp.status_text = "OK";
            resp.headers["Content-Type"] = "application/json; charset=utf-8";
            resp.body = R"({"message": "Hello from C++ HTTP Server!", "status": "ok"})";
            resp.headers["Content-Length"] = std::to_string(resp.body.size());
            return resp;
        });

        server.run();
        return 0;
    }

    // ── 클라이언트 모드 ──
    if (argc > 1 && std::string(argv[1]) == "client") {
        std::string host = (argc > 2) ? argv[2] : "127.0.0.1";
        uint16_t port = (argc > 3) ? std::stoi(argv[3]) : 8080;
        std::string path = (argc > 4) ? argv[4] : "/";

        std::string response = SimpleHttpClient::get(host, port, path);
        if (!response.empty()) {
            std::cout << "\n  응답 원문:" << std::endl;
            std::cout << response << std::endl;
        }
        return 0;
    }

    // ── 학습 모드 (인자 없이 실행) ──

    std::cout << R"(
  ┌───────────────────────────────────────────────────────┐
  │  사용법:                                               │
  │    ./http_protocol server [port]  HTTP 서버 실행       │
  │    ./http_protocol client [host] [port] [path]         │
  │                                                        │
  │  예시:                                                 │
  │    터미널1: ./http_protocol server 8080                │
  │    터미널2: ./http_protocol client 127.0.0.1 8080 /    │
  │    또는 브라우저: http://localhost:8080                 │
  └───────────────────────────────────────────────────────┘
)" << std::endl;

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  1. HTTP 요청 파싱 데모
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  1. HTTP 요청 파싱 데모" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    std::string raw_request =
        "GET /api/users?page=1 HTTP/1.1\r\n"
        "Host: api.example.com\r\n"
        "User-Agent: Mozilla/5.0\r\n"
        "Accept: application/json\r\n"
        "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9\r\n"
        "Accept-Language: ko-KR,ko;q=0.9\r\n"
        "Connection: keep-alive\r\n"
        "\r\n";

    HttpRequest req = HttpRequest::parse(raw_request);
    std::cout << "\n  파싱 결과:" << std::endl;
    req.print();

    // POST 요청 예시
    std::string raw_post =
        "POST /api/users HTTP/1.1\r\n"
        "Host: api.example.com\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: 47\r\n"
        "\r\n"
        R"({"name": "김철수", "email": "kim@test.com"})";

    HttpRequest post_req = HttpRequest::parse(raw_post);
    std::cout << "\n  POST 요청 파싱:" << std::endl;
    post_req.print();

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  2. HTTP 응답 생성 데모
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  2. HTTP 응답 생성 데모" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    HttpResponse resp;
    resp.version = "HTTP/1.1";
    resp.status_code = 200;
    resp.status_text = "OK";
    resp.headers["Content-Type"] = "application/json";
    resp.headers["Server"] = "CPP-HttpServer/1.0";
    resp.headers["Cache-Control"] = "max-age=3600";
    resp.body = R"({"users": [{"id": 1, "name": "김철수"}, {"id": 2, "name": "이영희"}]})";
    resp.headers["Content-Length"] = std::to_string(resp.body.size());

    std::cout << "\n  생성된 응답:" << std::endl;
    resp.print();
    std::cout << "\n  원문 (실제 전송되는 형태):" << std::endl;
    std::cout << "  ────────────────────────────" << std::endl;
    std::cout << resp.to_string() << std::endl;

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  3. 상태 코드 총정리
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  3. HTTP 상태 코드 총정리" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    std::vector<int> codes = {
        200, 201, 204,
        301, 302, 304,
        400, 401, 403, 404, 405, 429,
        500, 502, 503, 504
    };

    for (int code : codes) {
        std::string category;
        if (code < 200) category = "정보";
        else if (code < 300) category = "성공";
        else if (code < 400) category = "리다이렉트";
        else if (code < 500) category = "클라이언트 오류";
        else category = "서버 오류";

        std::cout << "  " << code << " " << std::setw(25) << std::left
                  << status_text(code) << " [" << category << "]" << std::endl;
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  4. MIME 타입
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  4. MIME 타입 (Content-Type)" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    std::vector<std::string> extensions = {
        "index.html", "style.css", "app.js", "data.json",
        "photo.png", "image.jpg", "logo.svg", "readme.txt"
    };

    for (const auto& ext : extensions) {
        std::cout << "  " << std::setw(15) << std::left << ext
                  << " → " << get_mime_type(ext) << std::endl;
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  5. HTTP 버전 비교 시각화
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  5. HTTP 버전별 연결 방식 비교" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    std::cout << R"(
  HTTP/1.0 (매번 새 연결):
  Client ──TCP──> Server    요청1
  Client <──────── Server   응답1
  (연결 끊김)
  Client ──TCP──> Server    요청2 (새 연결!)
  Client <──────── Server   응답2
  (연결 끊김)

  HTTP/1.1 (Keep-Alive):
  Client ──TCP──> Server    연결 수립
  Client ──────── Server    요청1 → 응답1
  Client ──────── Server    요청2 → 응답2  (같은 연결!)
  Client ──────── Server    요청3 → 응답3  (같은 연결!)
  (연결 끊김)

  HTTP/2 (멀티플렉싱):
  Client ══TCP══> Server    하나의 연결
  Client ═══════ Server    요청1 ─→ 응답1  ┐
  Client ═══════ Server    요청2 ─→ 응답2  ├ 동시 진행!
  Client ═══════ Server    요청3 ─→ 응답3  ┘

  HTTP/3 (QUIC/UDP):
  Client ~~UDP~~> Server    QUIC 연결 (0-RTT 가능!)
  Client ~~~~~~~ Server    스트림1: 요청1/응답1  ┐
  Client ~~~~~~~ Server    스트림2: 요청2/응답2  ├ 독립적!
  Client ~~~~~~~ Server    스트림3: 요청3/응답3  ┘
  (스트림 하나가 손실되어도 다른 스트림 영향 없음!)
)" << std::endl;

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //  정리
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;
    std::cout << "  정리: HTTP 핵심 요약" << std::endl;
    std::cout << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << std::endl;

    std::cout << R"(
  ★ 기억해야 할 핵심:

  1. HTTP = 텍스트 기반, 요청(Request)/응답(Response) 구조
  2. 메서드: GET(조회), POST(생성), PUT(수정), DELETE(삭제)
  3. 상태코드: 2xx(성공), 3xx(이동), 4xx(클라이언트오류), 5xx(서버오류)
  4. HTTPS = HTTP + TLS (암호화) → 포트 443
  5. HTTP/2 = 멀티플렉싱, HTTP/3 = QUIC(UDP 기반)

  ★ 실무 팁:
  - REST API: 리소스 URL + HTTP 메서드로 설계
  - Content-Type: 요청/응답 데이터 형식 명시 (중요!)
  - CORS: 다른 도메인 간 요청 시 필수 설정
  - Cache-Control: 성능 최적화의 핵심
  - Authorization: Bearer 토큰 또는 API Key로 인증
  - HTTPS 필수! (HTTP는 모든 데이터가 평문 노출)
)" << std::endl;

    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;
    std::cout << "  HTTP 프로토콜 학습 완료!" << std::endl;
    std::cout << "  다음: 06_proxy_gateway (프록시, 게이트웨이, 터널링)" << std::endl;
    std::cout << "■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■" << std::endl;

    return 0;
}
