/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C++ 학습 15단계: 네트워크 프로그래밍 개념과 소켓 기초
  ─ TCP/IP 개념, 소켓, HTTP, 직렬화 ─

  네트워크 프로그래밍의 핵심 개념을 배우고,
  실무에서 사용하는 라이브러리와 패턴을 이해합니다.

  ※ 이 파일은 개념 설명 + 의사 코드 위주입니다.
     실제 소켓은 OS별로 다르므로 (Winsock / POSIX),
     실무에서는 Boost.Asio, cpp-httplib 등 라이브러리를 사용합니다.

  ■ 컴파일: g++ -std=c++17 -Wall -o 15_network main.cpp

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <sstream>
#include <functional>
using namespace std;

void lesson1_network_basics();
void lesson2_socket_concept();
void lesson3_http_concept();
void lesson4_serialization();
void lesson5_libraries();
void lesson6_architecture();

int main() {
    cout << "========================================\n";
    cout << "  C++ 15단계 : 네트워크 프로그래밍\n";
    cout << "========================================\n\n";

    lesson1_network_basics();
    lesson2_socket_concept();
    lesson3_http_concept();
    lesson4_serialization();
    lesson5_libraries();
    lesson6_architecture();

    cout << "\n15단계 학습 완료!\n";
    return 0;
}


// =========================================================================
//  레슨 1 — 네트워크 기초 개념
// =========================================================================
void lesson1_network_basics() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 1 : 네트워크 기초 개념         │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    cout << R"(
  ■ TCP/IP 4계층 모델
  ───────────────────────────────────────
  ┌─────────────┐
  │ 응용 계층   │  HTTP, FTP, DNS, SMTP
  │ (Application)│  ← 우리가 프로그래밍하는 영역
  ├─────────────┤
  │ 전송 계층   │  TCP (신뢰성), UDP (속도)
  │ (Transport) │  포트 번호로 프로세스 구분
  ├─────────────┤
  │ 인터넷 계층 │  IP
  │ (Internet)  │  IP 주소로 컴퓨터 구분
  ├─────────────┤
  │ 링크 계층   │  이더넷, Wi-Fi
  │ (Link)      │  물리적 연결
  └─────────────┘

  ■ TCP vs UDP
  ┌──────────┬─────────────────┬─────────────────┐
  │          │ TCP             │ UDP              │
  ├──────────┼─────────────────┼─────────────────┤
  │ 연결     │ 연결 기반       │ 비연결           │
  │ 신뢰성   │ 순서 보장, 재전송│ 보장 안 함       │
  │ 속도     │ 상대적 느림     │ 빠름             │
  │ 용도     │ 웹, 파일 전송   │ 게임, 스트리밍   │
  └──────────┴─────────────────┴─────────────────┘

  ■ 핵심 용어
  ─────────────────────────────────────
  IP 주소    : 컴퓨터의 주소 (192.168.1.1)
  포트(Port) : 프로그램의 문 번호 (80=HTTP, 443=HTTPS)
  소켓       : 네트워크 통신의 끝점 (IP + 포트)
  localhost  : 내 컴퓨터 자신 (127.0.0.1)
)" << endl;
}


// =========================================================================
//  레슨 2 — 소켓 프로그래밍 개념
// =========================================================================
void lesson2_socket_concept() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 2 : 소켓 프로그래밍 개념       │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    cout << R"(
  ■ TCP 통신 흐름  (전화 비유)
  ───────────────────────────────────────

  서버 (전화 받는 쪽)          클라이언트 (전화 거는 쪽)
  ─────────────────          ────────────────────
  1. socket()    소켓 생성    1. socket()    소켓 생성
  2. bind()      주소 배정
  3. listen()    대기 시작
  4. accept()    연결 수락 ←  2. connect()   연결 요청
       ↕ 연결 수립 ↕
  5. recv/send   데이터 교환  3. send/recv   데이터 교환
  6. close()     연결 종료    4. close()     연결 종료

  ■ 의사 코드 — TCP 서버
  ───────────────────────────────────────
  // 1. 소켓 생성
  int server_socket = socket(AF_INET, SOCK_STREAM, 0);

  // 2. 주소 바인딩
  sockaddr_in addr;
  addr.sin_family = AF_INET;
  addr.sin_port = htons(8080);        // 포트 8080
  addr.sin_addr.s_addr = INADDR_ANY;  // 모든 IP에서 접속 허용
  bind(server_socket, &addr, sizeof(addr));

  // 3. 리슨 (대기)
  listen(server_socket, 5);  // 최대 5개 대기열

  // 4. 연결 수락 (블로킹 — 연결 올 때까지 기다림)
  int client_socket = accept(server_socket, ...);

  // 5. 데이터 교환
  char buffer[1024];
  recv(client_socket, buffer, sizeof(buffer), 0);   // 받기
  send(client_socket, "Hello!", 6, 0);               // 보내기

  // 6. 종료
  close(client_socket);
  close(server_socket);

  ■ 의사 코드 — TCP 클라이언트
  ───────────────────────────────────────
  int sock = socket(AF_INET, SOCK_STREAM, 0);

  sockaddr_in server_addr;
  server_addr.sin_family = AF_INET;
  server_addr.sin_port = htons(8080);
  inet_pton(AF_INET, "127.0.0.1", &server_addr.sin_addr);

  connect(sock, &server_addr, sizeof(server_addr));
  send(sock, "Hello Server!", 13, 0);

  char buffer[1024];
  recv(sock, buffer, sizeof(buffer), 0);
  cout << "서버 응답: " << buffer;

  close(sock);
)" << endl;
}


// =========================================================================
//  레슨 3 — HTTP 프로토콜 이해
// =========================================================================

// 간단한 HTTP 요청/응답 파서 (학습용)
struct HttpRequest {
    string method;      // GET, POST, PUT, DELETE
    string path;        // /api/users
    map<string, string> headers;
    string body;

    string to_string() const {
        ostringstream oss;
        oss << method << " " << path << " HTTP/1.1\r\n";
        for (const auto& [k, v] : headers) {
            oss << k << ": " << v << "\r\n";
        }
        oss << "\r\n" << body;
        return oss.str();
    }
};

struct HttpResponse {
    int status_code;
    string status_text;
    map<string, string> headers;
    string body;

    string to_string() const {
        ostringstream oss;
        oss << "HTTP/1.1 " << status_code << " " << status_text << "\r\n";
        for (const auto& [k, v] : headers) {
            oss << k << ": " << v << "\r\n";
        }
        oss << "\r\n" << body;
        return oss.str();
    }
};

void lesson3_http_concept() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 3 : HTTP 프로토콜              │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    // HTTP 요청 만들기
    HttpRequest req;
    req.method = "POST";
    req.path = "/api/users";
    req.headers["Content-Type"] = "application/json";
    req.headers["Host"] = "example.com";
    req.body = R"({"name":"홍길동","age":25})";

    cout << "  ■ HTTP 요청 예시\n";
    cout << "  ─────────────────────────────────────\n";
    cout << "  " << req.method << " " << req.path << "\n";
    for (const auto& [k, v] : req.headers) {
        cout << "  " << k << ": " << v << "\n";
    }
    cout << "  Body: " << req.body << "\n\n";

    // HTTP 응답 만들기
    HttpResponse res;
    res.status_code = 200;
    res.status_text = "OK";
    res.headers["Content-Type"] = "application/json";
    res.body = R"({"id":1,"name":"홍길동"})";

    cout << "  ■ HTTP 응답 예시\n";
    cout << "  ─────────────────────────────────────\n";
    cout << "  " << res.status_code << " " << res.status_text << "\n";
    for (const auto& [k, v] : res.headers) {
        cout << "  " << k << ": " << v << "\n";
    }
    cout << "  Body: " << res.body << "\n\n";

    cout << R"(
  ■ HTTP 메서드
  ┌─────────┬────────────────────────────┐
  │ GET     │ 데이터 조회                 │
  │ POST    │ 데이터 생성                 │
  │ PUT     │ 데이터 전체 수정            │
  │ PATCH   │ 데이터 일부 수정            │
  │ DELETE  │ 데이터 삭제                 │
  └─────────┴────────────────────────────┘

  ■ 주요 상태 코드
  ┌──────┬───────────────────────────────┐
  │ 200  │ OK (성공)                      │
  │ 201  │ Created (생성됨)               │
  │ 400  │ Bad Request (잘못된 요청)      │
  │ 401  │ Unauthorized (인증 필요)       │
  │ 403  │ Forbidden (권한 없음)          │
  │ 404  │ Not Found (없는 리소스)        │
  │ 500  │ Internal Server Error (서버 에러)│
  └──────┴───────────────────────────────┘
)" << endl;
}


// =========================================================================
//  레슨 4 — 직렬화 (Serialization)
// =========================================================================

// 간단한 JSON 직렬화 예제 (학습용, 실무에서는 nlohmann/json 사용)
struct Player {
    string name;
    int level;
    double hp;
    vector<string> items;

    // 직렬화: 객체 → 문자열 (저장/전송용)
    string to_json() const {
        ostringstream oss;
        oss << "{\n";
        oss << "  \"name\": \"" << name << "\",\n";
        oss << "  \"level\": " << level << ",\n";
        oss << "  \"hp\": " << hp << ",\n";
        oss << "  \"items\": [";
        for (size_t i = 0; i < items.size(); i++) {
            oss << "\"" << items[i] << "\"";
            if (i + 1 < items.size()) oss << ", ";
        }
        oss << "]\n}";
        return oss.str();
    }
};

void lesson4_serialization() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 4 : 직렬화 (Serialization)     │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    // ─── 직렬화란? ───
    //
    //   직렬화   : 객체 → 문자열/바이트 (저장·전송 가능한 형태로 변환)
    //   역직렬화 : 문자열/바이트 → 객체 (복원)
    //
    //   왜 필요한가?
    //   - 네트워크로 데이터 전송 (서버↔클라이언트)
    //   - 파일에 저장 (세이브/로드)
    //   - 프로세스 간 통신 (IPC)

    Player player{"전사", 10, 85.5, {"검", "방패", "물약"}};

    cout << "  ■ Player 객체 → JSON 직렬화\n";
    cout << "  ─────────────────────────────────────\n";
    cout << player.to_json() << "\n\n";

    cout << R"(
  ■ 직렬화 형식 비교
  ┌─────────────┬────────────────────────────────────┐
  │ JSON        │ 사람이 읽기 쉬움, 웹 표준           │
  │             │ 라이브러리: nlohmann/json            │
  ├─────────────┼────────────────────────────────────┤
  │ Protocol    │ 바이너리, 매우 빠름, 크기 작음      │
  │ Buffers     │ Google 개발, gRPC에서 사용          │
  ├─────────────┼────────────────────────────────────┤
  │ MessagePack │ 바이너리 JSON, 빠르고 작음          │
  ├─────────────┼────────────────────────────────────┤
  │ XML         │ 오래된 형식, 무겁지만 표준 많음     │
  ├─────────────┼────────────────────────────────────┤
  │ CSV         │ 테이블 형식 데이터, 스프레드시트    │
  └─────────────┴────────────────────────────────────┘

  ★ 실무 추천: JSON(일반), Protobuf(고성능)
)" << endl;
}


// =========================================================================
//  레슨 5 — 실무 라이브러리
// =========================================================================
void lesson5_libraries() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 5 : 실무 네트워크 라이브러리   │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    cout << R"(
  ■ cpp-httplib (가장 간단한 HTTP 서버/클라이언트)
  ────────────────────────────────────────────

  헤더 하나만 include하면 바로 사용 가능!

  // 서버 예시
  #include "httplib.h"

  httplib::Server svr;

  svr.Get("/hello", [](const auto& req, auto& res) {
      res.set_content("Hello World!", "text/plain");
  });

  svr.Post("/api/users", [](const auto& req, auto& res) {
      auto body = req.body;  // JSON 등
      res.set_content("{\"id\": 1}", "application/json");
  });

  svr.listen("0.0.0.0", 8080);  // 8080 포트에서 대기

  // 클라이언트 예시
  httplib::Client cli("http://localhost:8080");
  auto res = cli.Get("/hello");
  if (res) cout << res->body;


  ■ Boost.Asio (비동기 네트워크 IO)
  ────────────────────────────────────────────

  고성능 비동기 서버에 사용 (게임 서버 등)
  비동기 패턴: callback, coroutine (C++20)

  asio::io_context io;
  tcp::acceptor acceptor(io, tcp::endpoint(tcp::v4(), 8080));
  // ... 비동기 accept, read, write


  ■ gRPC (원격 프로시저 호출)
  ────────────────────────────────────────────

  Protocol Buffers + HTTP/2 기반
  마이크로서비스 간 통신에 많이 사용

  // service.proto
  service Greeter {
    rpc SayHello (HelloRequest) returns (HelloReply);
  }


  ■ 라이브러리 선택 가이드
  ┌──────────────────┬──────────────────────────┐
  │ 상황             │ 추천 라이브러리           │
  ├──────────────────┼──────────────────────────┤
  │ 간단한 REST API  │ cpp-httplib              │
  │ 고성능 서버      │ Boost.Asio, Drogon       │
  │ 마이크로서비스   │ gRPC                     │
  │ WebSocket        │ Boost.Beast, uWebSockets │
  │ HTTP 클라이언트  │ cpp-httplib, libcurl     │
  └──────────────────┴──────────────────────────┘
)" << endl;
}


// =========================================================================
//  레슨 6 — 서버 아키텍처 패턴
// =========================================================================
void lesson6_architecture() {
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  레슨 6 : 서버 아키텍처 패턴         │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    cout << R"(
  ■ 1. 단일 스레드 (싱글 스레드)
  ────────────────────────────────────────────
  클라이언트 → [처리] → 응답
              (한번에 하나만 처리)
  장점: 간단     단점: 느림

  ■ 2. 멀티 스레드 (Thread per Connection)
  ────────────────────────────────────────────
  클라1 → [스레드1]
  클라2 → [스레드2]
  클라3 → [스레드3]
  장점: 간단한 구현   단점: 스레드 많아지면 오버헤드

  ■ 3. 스레드 풀 (Thread Pool)
  ────────────────────────────────────────────
            ┌→ [워커1]
  요청 큐 → ├→ [워커2]    (고정된 스레드 수)
            └→ [워커3]
  장점: 안정적   단점: 동시 접속 수 제한

  ■ 4. 비동기 이벤트 루프 (Async/Event-driven)
  ────────────────────────────────────────────
  [이벤트 루프] → 이벤트1 처리
               → 이벤트2 처리
               → 이벤트3 처리   (단일 스레드로 수천 연결)
  장점: 높은 동시성   단점: 코드 복잡

  ■ 5. REST API 설계 원칙
  ────────────────────────────────────────────
  GET    /api/users          모든 사용자 목록
  GET    /api/users/42       42번 사용자 조회
  POST   /api/users          사용자 생성
  PUT    /api/users/42       42번 사용자 수정
  DELETE /api/users/42       42번 사용자 삭제

  → URL은 명사, HTTP 메서드가 동사 역할
  → 상태 코드로 결과 전달 (200, 201, 404 등)
)" << endl;
}
