// ============================================================================
// 08_network_server/main.cpp
// 고성능 네트워크 서버 시뮬레이터 (High-Performance Network Server Simulator)
// ============================================================================
// *** 왜 C++로 서버를 만들까요? ***
// Nginx, game servers, cloud infrastructure 모두 C++입니다!
// 이유: 수백만 동시 접속, 마이크로초 지연시간, GC 멈춤 없음
// C#의 ASP.NET Core도 훌륭하지만, C++은 하드웨어에 더 가깝습니다.
//
// ┌─────────────────────────────────────────────────┐
// │  클라이언트 ──┐                                 │
// │  클라이언트 ──┤──▶ [이벤트 루프] ──▶ [미들웨어] │
// │  클라이언트 ──┘        │              │         │
// │                        ▼              ▼         │
// │               [커넥션 풀]      [라우터]──▶[핸들러]
// │                        │              │         │
// │               [세션 관리]      [JSON 응답 빌더] │
// │  [로드 밸런서] ──▶ 서버1, 서버2, 서버3          │
// └─────────────────────────────────────────────────┘
// ============================================================================

#include <iostream>      // 화면 출력 (cout). C#의 Console.WriteLine과 같아요!
#include <string>        // 문자열. C#의 string과 같아요!
#include <vector>        // 동적 배열. C#의 List<T>와 같아요!
#include <map>           // 정렬된 키-값. C#의 SortedDictionary와 같아요!
#include <unordered_map> // 해시 키-값. C#의 Dictionary와 같아요!
#include <functional>    // 함수 객체. C#의 Func<T>와 같아요!
#include <queue>         // 큐. C#의 Queue<T>와 같아요!
#include <list>          // 연결 리스트. C#의 LinkedList<T>와 같아요!
#include <sstream>       // 문자열 스트림 (파싱에 사용)
#include <chrono>        // 시간 측정. C#의 Stopwatch와 같아요!
#include <algorithm>     // 정렬, 검색. C#의 LINQ와 비슷해요!
#include <memory>        // 스마트 포인터 (자동 메모리 관리)
#include <random>        // 난수 생성. C#의 Random과 같아요!
#include <cassert>       // 디버그 검증
#include <numeric>       // 숫자 알고리즘
#include <iomanip>       // 출력 형식

// ============================================================================
// 1. 이벤트 시스템 (Event System)
// ============================================================================
// 이벤트 루프는 C#의 async/await 뒤에서 돌아가는 TaskScheduler입니다
// 서버는 무한 루프를 돌면서 이벤트가 오면 처리합니다 (epoll/kqueue 시뮬레이션)

enum class EventType { NewConnection, DataReceived, ConnectionClosed, Timeout };

struct Event {
    EventType type;
    int connection_id;
    std::string data;
    uint64_t timestamp;
};

class EventLoop {
    std::queue<Event> event_queue_;
    bool running_ = false;
    std::map<EventType, std::function<void(const Event&)>> handlers_;
public:
    // 이벤트 핸들러 등록 (C#의 이벤트 구독 += 과 같아요!)
    void on(EventType type, std::function<void(const Event&)> handler) {
        handlers_[type] = handler;
    }
    void push_event(Event event) { event_queue_.push(std::move(event)); }
    int run() {
        running_ = true;
        int processed = 0;
        while (running_ && !event_queue_.empty()) {
            Event event = event_queue_.front();
            event_queue_.pop();
            auto it = handlers_.find(event.type);
            if (it != handlers_.end()) it->second(event);
            processed++;
        }
        running_ = false;
        return processed;
    }
    void stop() { running_ = false; }
    size_t pending() const { return event_queue_.size(); }
};

// ============================================================================
// 2. 커넥션 풀 관리 (Connection Pool)
// ============================================================================
// 커넥션 풀은 C#의 DbConnection pooling과 같은 개념입니다
// 연결을 미리 만들어두고 재사용하면 훨씬 빠릅니다!
//  [사용가능] ──▶ 빌려줌 ──▶ [사용중] ──▶ 반납 ──▶ [사용가능]

struct Connection {
    int id;
    bool in_use = false;
    std::string client_address;
    uint64_t last_used = 0;
    int request_count = 0;
};

class ConnectionPool {
    std::vector<Connection> connections_;
    int max_connections_, next_id_ = 1;
public:
    explicit ConnectionPool(int max_conn) : max_connections_(max_conn) {
        connections_.reserve(max_conn);
    }
    // 연결 획득 (빌려쓰기)
    Connection* acquire(const std::string& client_addr, uint64_t now) {
        for (auto& conn : connections_) {
            if (!conn.in_use) {
                conn.in_use = true;
                conn.client_address = client_addr;
                conn.last_used = now;
                conn.request_count++;
                return &conn;
            }
        }
        if (static_cast<int>(connections_.size()) < max_connections_) {
            connections_.push_back({next_id_++, true, client_addr, now, 1});
            return &connections_.back();
        }
        return nullptr;  // 풀이 꽉 참! (nullptr = C#의 null)
    }
    void release(int connection_id) {
        for (auto& conn : connections_)
            if (conn.id == connection_id) { conn.in_use = false; return; }
    }
    int active_count() const {
        int c = 0; for (const auto& x : connections_) if (x.in_use) c++; return c;
    }
    int total_count() const { return static_cast<int>(connections_.size()); }
};

// ============================================================================
// 3. HTTP 요청 파서 (HTTP Request Parser)
// ============================================================================
// HTTP 요청 형태:
//  GET /api/users?page=1 HTTP/1.1    ← 요청 줄
//  Host: example.com                  ← 헤더들
//  Content-Type: application/json
//                                     ← 빈 줄 (헤더 끝)
//  {"name":"홍길동"}                  ← 본문

struct HttpRequest {
    std::string method, path, version;
    std::unordered_map<std::string, std::string> headers;
    std::string body;
    std::unordered_map<std::string, std::string> query_params;
};

class HttpParser {
public:
    static HttpRequest parse(const std::string& raw) {
        HttpRequest req;
        std::istringstream stream(raw);
        std::string line;
        // 첫 줄: "GET /path HTTP/1.1"
        if (std::getline(stream, line)) {
            if (!line.empty() && line.back() == '\r') line.pop_back();
            std::istringstream fl(line);
            fl >> req.method >> req.path >> req.version;
        }
        // 쿼리 파라미터 분리
        auto qmark = req.path.find('?');
        if (qmark != std::string::npos) {
            std::string qs = req.path.substr(qmark + 1);
            req.path = req.path.substr(0, qmark);
            std::istringstream qs_stream(qs);
            std::string pair;
            while (std::getline(qs_stream, pair, '&')) {
                auto eq = pair.find('=');
                if (eq != std::string::npos)
                    req.query_params[pair.substr(0, eq)] = pair.substr(eq + 1);
            }
        }
        // 헤더 파싱
        while (std::getline(stream, line)) {
            if (!line.empty() && line.back() == '\r') line.pop_back();
            if (line.empty()) break;
            auto colon = line.find(':');
            if (colon != std::string::npos) {
                std::string val = line.substr(colon + 1);
                while (!val.empty() && val.front() == ' ') val.erase(val.begin());
                req.headers[line.substr(0, colon)] = val;
            }
        }
        // 본문
        std::string bl;
        while (std::getline(stream, bl)) {
            if (!req.body.empty()) req.body += "\n";
            req.body += bl;
        }
        return req;
    }
};

// ============================================================================
// 4. JSON 응답 빌더
// ============================================================================

class JsonBuilder {
    std::ostringstream stream_;
    bool first_ = true;
    void add_comma() { if (!first_) stream_ << ","; first_ = false; }
public:
    JsonBuilder& begin_object() { stream_ << "{"; first_ = true; return *this; }
    JsonBuilder& end_object() { stream_ << "}"; first_ = false; return *this; }
    JsonBuilder& begin_array(const std::string& key) { add_comma(); stream_ << "\"" << key << "\":["; first_ = true; return *this; }
    JsonBuilder& end_array() { stream_ << "]"; first_ = false; return *this; }
    JsonBuilder& add_string(const std::string& k, const std::string& v) { add_comma(); stream_ << "\"" << k << "\":\"" << v << "\""; return *this; }
    JsonBuilder& add_number(const std::string& k, double v) { add_comma(); stream_ << "\"" << k << "\":" << v; return *this; }
    JsonBuilder& add_bool(const std::string& k, bool v) { add_comma(); stream_ << "\"" << k << "\":" << (v?"true":"false"); return *this; }
    std::string build() const { return stream_.str(); }
};

struct HttpResponse {
    int status_code = 200;
    std::string status_text = "OK";
    std::unordered_map<std::string, std::string> headers;
    std::string body;
    std::string to_string() const {
        std::ostringstream ss;
        ss << "HTTP/1.1 " << status_code << " " << status_text << "\r\n";
        for (const auto& [k, v] : headers) ss << k << ": " << v << "\r\n";
        ss << "Content-Length: " << body.size() << "\r\n\r\n" << body;
        return ss.str();
    }
};

// ============================================================================
// 5. 미들웨어 체인 (Middleware Chain)
// ============================================================================
// 미들웨어는 ASP.NET Core의 app.UseMiddleware<T>()와 같습니다
//  요청 ──▶ [로깅] ──▶ [인증] ──▶ [속도제한] ──▶ [핸들러]
//  응답 ◀── [로깅] ◀── [인증] ◀── [속도제한] ◀── [핸들러]

struct MiddlewareContext {
    HttpRequest& request;
    HttpResponse& response;
    bool should_continue = true;
    std::unordered_map<std::string, std::string> metadata;
};

using MiddlewareFunc = std::function<void(MiddlewareContext&)>;

class MiddlewareChain {
    std::vector<MiddlewareFunc> middlewares_;
public:
    void use(MiddlewareFunc mw) { middlewares_.push_back(std::move(mw)); }
    void execute(MiddlewareContext& ctx) {
        for (const auto& mw : middlewares_) {
            mw(ctx);
            if (!ctx.should_continue) break;
        }
    }
};

// 로깅 미들웨어
MiddlewareFunc create_logging_middleware(std::vector<std::string>& log_storage) {
    return [&log_storage](MiddlewareContext& ctx) {
        log_storage.push_back("[LOG] " + ctx.request.method + " " + ctx.request.path);
    };
}

// 인증 미들웨어
MiddlewareFunc create_auth_middleware() {
    return [](MiddlewareContext& ctx) {
        auto it = ctx.request.headers.find("Authorization");
        if (it != ctx.request.headers.end() && it->second.find("Bearer ") == 0) {
            ctx.metadata["user"] = "authenticated_user";
        } else if (ctx.request.path.find("/api/") == 0) {
            ctx.response.status_code = 401;
            ctx.response.status_text = "Unauthorized";
            ctx.response.body = "{\"error\":\"Authentication required\"}";
            ctx.should_continue = false;
        }
    };
}

// 속도 제한 미들웨어 (C#의 app.UseRateLimiter()와 비슷합니다)
class RateLimiter {
    std::unordered_map<std::string, int> request_counts_;
    int max_requests_;
public:
    explicit RateLimiter(int max_req) : max_requests_(max_req) {}
    MiddlewareFunc as_middleware() {
        return [this](MiddlewareContext& ctx) {
            std::string client = ctx.request.headers.count("X-Client-IP")
                ? ctx.request.headers["X-Client-IP"] : "unknown";
            if (++request_counts_[client] > max_requests_) {
                ctx.response.status_code = 429;
                ctx.response.status_text = "Too Many Requests";
                ctx.response.body = "{\"error\":\"Rate limit exceeded\"}";
                ctx.should_continue = false;
            }
        };
    }
    void reset() { request_counts_.clear(); }
};

// ============================================================================
// 6. 라우터 (Router)
// ============================================================================
// 라우터는 ASP.NET의 [Route("/api/users")] 속성과 같은 역할입니다

using HandlerFunc = std::function<HttpResponse(const HttpRequest&)>;

class Router {
    std::map<std::string, HandlerFunc> routes_;
    HandlerFunc not_found_ = [](const HttpRequest&) -> HttpResponse {
        return {404, "Not Found", {{"Content-Type","application/json"}}, "{\"error\":\"Not found\"}"};
    };
public:
    void add_route(const std::string& method, const std::string& path, HandlerFunc h) {
        routes_[method + " " + path] = std::move(h);
    }
    void get(const std::string& path, HandlerFunc h) { add_route("GET", path, std::move(h)); }
    void post(const std::string& path, HandlerFunc h) { add_route("POST", path, std::move(h)); }
    HttpResponse route(const HttpRequest& req) {
        auto it = routes_.find(req.method + " " + req.path);
        return (it != routes_.end()) ? it->second(req) : not_found_(req);
    }
    int route_count() const { return static_cast<int>(routes_.size()); }
};

// ============================================================================
// 7. 세션 관리 (LRU Session Manager)
// ============================================================================
// LRU = Least Recently Used (가장 오래 안 쓴 것을 먼저 삭제)
// C#의 MemoryCache와 비슷합니다!

struct Session {
    std::string session_id, user_id;
    std::unordered_map<std::string, std::string> data;
    uint64_t created_at, expires_at;
};

class SessionManager {
    size_t max_sessions_;
    uint64_t session_ttl_ms_;
    int next_num_ = 1;
    std::list<Session> sessions_;
    std::unordered_map<std::string, std::list<Session>::iterator> lookup_;
public:
    SessionManager(size_t max_s, uint64_t ttl) : max_sessions_(max_s), session_ttl_ms_(ttl) {}

    std::string create_session(const std::string& user_id, uint64_t now) {
        std::string sid = "sess_" + std::to_string(next_num_++);
        if (sessions_.size() >= max_sessions_) {
            lookup_.erase(sessions_.back().session_id);
            sessions_.pop_back();
        }
        sessions_.push_front({sid, user_id, {}, now, now + session_ttl_ms_});
        lookup_[sid] = sessions_.begin();
        return sid;
    }
    Session* get_session(const std::string& sid, uint64_t now) {
        auto it = lookup_.find(sid);
        if (it == lookup_.end()) return nullptr;
        if (it->second->expires_at < now) {
            sessions_.erase(it->second); lookup_.erase(it); return nullptr;
        }
        sessions_.splice(sessions_.begin(), sessions_, it->second); // LRU 갱신
        return &sessions_.front();
    }
    int cleanup_expired(uint64_t now) {
        int removed = 0;
        for (auto it = sessions_.begin(); it != sessions_.end();) {
            if (it->expires_at < now) { lookup_.erase(it->session_id); it = sessions_.erase(it); removed++; }
            else ++it;
        }
        return removed;
    }
    size_t active_count() const { return sessions_.size(); }
};

// ============================================================================
// 8. 로드 밸런서 (Load Balancer)
// ============================================================================
//  라운드 로빈: 1→2→3→1→2→3→...
//  최소 연결:   가장 한가한 서버에게 보냄

struct ServerNode {
    std::string name, address;
    int active_connections = 0, total_requests = 0;
    bool healthy = true;
};

enum class LBStrategy { RoundRobin, LeastConnections };

class LoadBalancer {
    std::vector<ServerNode> servers_;
    LBStrategy strategy_;
    int rr_index_ = 0;
public:
    explicit LoadBalancer(LBStrategy s) : strategy_(s) {}
    void add_server(const std::string& name, const std::string& addr) {
        servers_.push_back({name, addr, 0, 0, true});
    }
    ServerNode* select_server() {
        std::vector<int> healthy;
        for (int i = 0; i < (int)servers_.size(); i++)
            if (servers_[i].healthy) healthy.push_back(i);
        if (healthy.empty()) return nullptr;
        int sel;
        if (strategy_ == LBStrategy::RoundRobin) {
            sel = healthy[rr_index_++ % healthy.size()];
        } else {
            sel = healthy[0];
            for (int idx : healthy)
                if (servers_[idx].active_connections < servers_[sel].active_connections) sel = idx;
        }
        servers_[sel].active_connections++;
        servers_[sel].total_requests++;
        return &servers_[sel];
    }
    void release_server(const std::string& name) {
        for (auto& s : servers_) if (s.name == name && s.active_connections > 0) { s.active_connections--; return; }
    }
    void set_health(const std::string& name, bool h) {
        for (auto& s : servers_) if (s.name == name) { s.healthy = h; return; }
    }
    void print_stats() const {
        std::cout << "\n  === 로드 밸런서 통계 ===\n";
        for (const auto& s : servers_)
            std::cout << "  " << s.name << ": 총 " << s.total_requests << "건, "
                      << "현재 " << s.active_connections << "건, "
                      << (s.healthy ? "정상" : "장애") << "\n";
    }
    const std::vector<ServerNode>& servers() const { return servers_; }
};

// ============================================================================
// 9. 서버 통합
// ============================================================================

class HttpServer {
    Router router_;
    MiddlewareChain middleware_;
    ConnectionPool conn_pool_;
    SessionManager session_mgr_;
    EventLoop event_loop_;
    std::vector<std::string> access_log_;
    int total_requests_ = 0, successful_ = 0, failed_ = 0;

    void setup_routes() {
        // 라우터는 ASP.NET의 [Route("/api/users")] 속성과 같은 역할입니다!
        router_.get("/", [](const HttpRequest&) -> HttpResponse {
            return {200, "OK", {{"Content-Type","text/plain"}}, "Welcome to C++ Server!"};
        });
        router_.get("/health", [this](const HttpRequest&) -> HttpResponse {
            JsonBuilder j;
            j.begin_object().add_string("status","healthy")
             .add_number("connections", conn_pool_.active_count())
             .add_number("total_requests", total_requests_).end_object();
            return {200, "OK", {{"Content-Type","application/json"}}, j.build()};
        });
        router_.get("/api/users", [](const HttpRequest&) -> HttpResponse {
            JsonBuilder j;
            j.begin_object().begin_array("users").end_array().add_number("total",0).end_object();
            return {200, "OK", {{"Content-Type","application/json"}}, j.build()};
        });
        router_.post("/api/users", [](const HttpRequest& req) -> HttpResponse {
            JsonBuilder j;
            j.begin_object().add_string("message","User created").add_string("body",req.body).end_object();
            return {201, "Created", {{"Content-Type","application/json"}}, j.build()};
        });
        router_.get("/api/stats", [this](const HttpRequest&) -> HttpResponse {
            JsonBuilder j;
            j.begin_object().add_number("total",total_requests_)
             .add_number("success",successful_).add_number("failed",failed_).end_object();
            return {200, "OK", {{"Content-Type","application/json"}}, j.build()};
        });
    }
    void setup_middleware() {
        // 미들웨어는 ASP.NET Core의 app.UseMiddleware<T>()와 같습니다!
        middleware_.use(create_logging_middleware(access_log_));
        middleware_.use(create_auth_middleware());
    }
    void setup_event_handlers() {
        // 이벤트 루프는 C#의 async/await 뒤에서 돌아가는 TaskScheduler입니다!
        event_loop_.on(EventType::DataReceived, [this](const Event& e) { handle_request(e); });
        event_loop_.on(EventType::NewConnection, [this](const Event& e) {
            conn_pool_.acquire("client_" + std::to_string(e.connection_id), e.timestamp);
        });
        event_loop_.on(EventType::ConnectionClosed, [this](const Event& e) {
            conn_pool_.release(e.connection_id);
        });
    }
public:
    HttpServer() : conn_pool_(10000), session_mgr_(1000, 30*60*1000) {
        setup_routes(); setup_middleware(); setup_event_handlers();
    }
    HttpResponse handle_request(const Event& evt) {
        total_requests_++;
        HttpRequest req = HttpParser::parse(evt.data);
        HttpResponse resp; resp.headers["Content-Type"] = "application/json";
        MiddlewareContext ctx{req, resp, true, {}};
        middleware_.execute(ctx);
        if (ctx.should_continue) { resp = router_.route(req); successful_++; }
        else { failed_++; }
        return resp;
    }
    void submit_request(const std::string& raw, int conn_id, uint64_t ts) {
        event_loop_.push_event({EventType::DataReceived, conn_id, raw, ts});
    }
    int run_event_loop() { return event_loop_.run(); }
    void print_stats() const {
        std::cout << "  총 요청: " << total_requests_ << ", 성공: " << successful_
                  << ", 실패: " << failed_ << ", 활성 연결: " << conn_pool_.active_count()
                  << ", 세션: " << session_mgr_.active_count()
                  << ", 로그: " << access_log_.size() << "\n";
    }
    int total_requests() const { return total_requests_; }
    Router& router() { return router_; }
};

// ============================================================================
// main: 모든 것을 테스트합니다!
// ============================================================================
/*
=============================================================================
  실행 흐름 가이드
=============================================================================
  [1] HTTP 파서: GET /api/users?page=1&size=10 HTTP/1.1 + 헤더 3개
      method=GET, path=/api/users, version=HTTP/1.1, 헤더 3개
      쿼리: page=1, size=10

  [2] JSON 빌더: {"name":"Hong","age":25,"active":true}

  [3] Connection Pool (max 5):
      7개 acquire 시도 → 5개 성공, 6/7번째 "풀 꽉 참!"
      2개 release → 활성=3
      재acquire 성공

  [4] Session LRU (max 3, expire 5000ms):
      3개 생성 → s1 갱신 → s4 추가 → s2 evict
      s2 = 삭제됨, s1 = 있음

  [5] Middleware: 인증 미들웨어 통과/거부 시뮬

  [6] Router: /hello → 200 "Hello!", /nope → 404

  [7] Load Balancer:
      Round Robin: A,B,C,A,B,C 순환
      Least Connection: 가장 적은 active로 분배
      Health check: X 장애 → Y로 fallback

  [8] 통합 서버: 3개 요청 처리

  [9] 벤치마크 100K:
      처리 100000건, 보통 100~500ms
      초당 200K~1M req/s (시뮬레이터, 실제 네트워크 X)
      평균 지연: 1~5 us/req
=============================================================================
*/

int main() {
    std::cout << "============================================================\n";
    std::cout << "  고성능 네트워크 서버 시뮬레이터\n";
    std::cout << "============================================================\n\n";

    std::cout << "--- 1. HTTP 파서 테스트 ---\n";
    {
        std::string raw = "GET /api/users?page=1&size=10 HTTP/1.1\r\nHost: localhost\r\nAuthorization: Bearer tok\r\nContent-Type: application/json\r\n\r\n";
        HttpRequest req = HttpParser::parse(raw);
        // → method="GET", path="/api/users", version="HTTP/1.1"
        //   headers={"Host":"localhost", "Authorization":"Bearer tok", "Content-Type":"application/json"}
        //   query_params={"page":"1", "size":"10"}
        std::cout << "  메서드: " << req.method << ", 경로: " << req.path
                  << ", 버전: " << req.version << ", 헤더 수: " << req.headers.size() << "\n";
        // > 출력:   메서드: GET, 경로: /api/users, 버전: HTTP/1.1, 헤더 수: 3
        for (const auto& [k, v] : req.query_params) std::cout << "  쿼리: " << k << "=" << v << "\n";
        // > 출력:
        //   쿼리: page=1
        //   쿼리: size=10
    }

    // --- 2. JSON 빌더 ---
    std::cout << "\n--- 2. JSON 빌더 테스트 ---\n";
    {
        JsonBuilder j;
        j.begin_object().add_string("name","Hong").add_number("age",25).add_bool("active",true).end_object();
        std::cout << "  JSON: " << j.build() << "\n";
    }

    // --- 3. 커넥션 풀 ---
    std::cout << "\n--- 3. 커넥션 풀 테스트 ---\n";
    {
        ConnectionPool pool(5);
        std::vector<int> ids;
        for (int i = 0; i < 7; i++) {
            auto* c = pool.acquire("client_" + std::to_string(i), i * 100);
            if (c) { std::cout << "  연결 #" << c->id << " 획득\n"; ids.push_back(c->id); }
            else std::cout << "  풀 꽉 참!\n";
        }
        pool.release(ids[0]); pool.release(ids[1]);
        std::cout << "  2개 반납 후 활성: " << pool.active_count() << "\n";
        auto* reused = pool.acquire("new", 1000);
        if (reused) std::cout << "  재사용 연결 #" << reused->id << "\n";
    }

    // --- 4. 세션 관리 (LRU) ---
    std::cout << "\n--- 4. 세션 관리 (LRU) 테스트 ---\n";
    {
        SessionManager sm(3, 5000);
        std::string s1 = sm.create_session("user_1", 1000);
        std::string s2 = sm.create_session("user_2", 2000);
        std::string s3 = sm.create_session("user_3", 3000);
        std::cout << "  3개 생성: " << s1 << ", " << s2 << ", " << s3 << "\n";
        sm.get_session(s1, 3500);  // s1을 최근으로 갱신
        std::string s4 = sm.create_session("user_4", 4000);  // s2가 삭제됨
        std::cout << "  s4 추가 후 s2: " << (sm.get_session(s2, 4000) ? "있음" : "삭제됨") << "\n";
        std::cout << "  s1: " << (sm.get_session(s1, 4000) ? "있음" : "없음") << "\n";
        std::cout << "  만료 정리: " << sm.cleanup_expired(10000) << "개 삭제\n";
    }

    // --- 5. 미들웨어 ---
    std::cout << "\n--- 5. 미들웨어 체인 테스트 ---\n";
    {
        std::vector<std::string> logs;
        MiddlewareChain chain;
        chain.use(create_logging_middleware(logs));
        chain.use(create_auth_middleware());

        HttpRequest r1{"GET","/api/users","HTTP/1.1",{{"Authorization","Bearer abc"}},"",{}};
        HttpResponse resp1; MiddlewareContext c1{r1, resp1, true, {}};
        chain.execute(c1);
        std::cout << "  인증된 요청: 계속=" << (c1.should_continue?"예":"아니오") << "\n";

        HttpRequest r2{"GET","/api/users","HTTP/1.1",{},"",{}};
        HttpResponse resp2; MiddlewareContext c2{r2, resp2, true, {}};
        chain.execute(c2);
        std::cout << "  미인증 요청: 상태=" << resp2.status_code << ", 로그=" << logs.size() << "건\n";
    }

    // --- 6. 라우터 ---
    std::cout << "\n--- 6. 라우터 테스트 ---\n";
    {
        Router router;
        router.get("/hello", [](const HttpRequest&) -> HttpResponse { return {200,"OK",{},"Hello!"}; });
        HttpRequest r1{"GET","/hello","HTTP/1.1",{},"",{}};
        auto resp1 = router.route(r1);
        std::cout << "  GET /hello: " << resp1.status_code << " - " << resp1.body << "\n";
        HttpRequest r2{"GET","/nope","HTTP/1.1",{},"",{}};
        std::cout << "  GET /nope: " << router.route(r2).status_code << "\n";
    }

    // --- 7. 로드 밸런서 ---
    std::cout << "\n--- 7. 로드 밸런서 테스트 ---\n";
    {
        LoadBalancer rr(LBStrategy::RoundRobin);
        rr.add_server("A","10.0.0.1"); rr.add_server("B","10.0.0.2"); rr.add_server("C","10.0.0.3");
        std::cout << "  [라운드 로빈]\n";
        for (int i = 0; i < 6; i++) {
            auto* s = rr.select_server();
            std::cout << "    요청" << i+1 << " -> " << s->name << "\n";
            rr.release_server(s->name);
        }
        LoadBalancer lc(LBStrategy::LeastConnections);
        lc.add_server("X","10.0.1.1"); lc.add_server("Y","10.0.1.2");
        std::cout << "  [최소 연결]\n";
        auto* sx = lc.select_server(); std::cout << "    1st -> " << sx->name << "\n";
        auto* sy = lc.select_server(); std::cout << "    2nd -> " << sy->name << "\n";
        lc.set_health("X", false);
        auto* fb = lc.select_server(); std::cout << "    X장애 후 -> " << fb->name << "\n";
    }

    // --- 8. 통합 서버 ---
    std::cout << "\n--- 8. 통합 서버 테스트 ---\n";
    {
        HttpServer server;
        server.submit_request("GET / HTTP/1.1\r\nHost: localhost\r\n\r\n", 1, 100);
        server.submit_request("GET /health HTTP/1.1\r\nHost: localhost\r\n\r\n", 2, 200);
        server.submit_request("GET /api/users HTTP/1.1\r\nHost: localhost\r\nAuthorization: Bearer t\r\n\r\n", 3, 300);
        int processed = server.run_event_loop();
        std::cout << "  이벤트 루프: " << processed << "개 처리\n";
        server.print_stats();
    }

    // --- 9. 벤치마크: 10만 요청 ---
    std::cout << "\n--- 9. 벤치마크: 100,000 요청 처리 ---\n";
    {
        HttpServer server;
        std::vector<std::string> templates = {
            "GET / HTTP/1.1\r\nHost: localhost\r\n\r\n",
            "GET /health HTTP/1.1\r\nHost: localhost\r\n\r\n",
            "GET /api/users HTTP/1.1\r\nHost: localhost\r\nAuthorization: Bearer t\r\n\r\n",
            "POST /api/users HTTP/1.1\r\nHost: localhost\r\nAuthorization: Bearer t\r\n\r\n{\"name\":\"test\"}",
            "GET /api/stats HTTP/1.1\r\nHost: localhost\r\nAuthorization: Bearer t\r\n\r\n",
        };
        const int N = 100000;
        for (int i = 0; i < N; i++) server.submit_request(templates[i % templates.size()], i, i);

        auto start = std::chrono::high_resolution_clock::now();
        int processed = server.run_event_loop();
        auto end = std::chrono::high_resolution_clock::now();
        auto us = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
        double ms = us / 1000.0, sec = ms / 1000.0;
        double rps = (sec > 0) ? (processed / sec) : 0;

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "  처리: " << processed << "건, 시간: " << ms << "ms\n";
        std::cout << "  초당 처리량: " << rps << " req/s\n";
        std::cout << "  평균 지연: " << (processed > 0 ? (double)us/processed : 0) << " us/req\n";
        server.print_stats();
    }

    std::cout << "\n============================================================\n";
    std::cout << "  C#의 ASP.NET Core: 편리하고 생산성 높음\n";
    std::cout << "  C++ 서버: GC 없이 마이크로초 단위 응답, 수백만 동시 접속\n";
    std::cout << "  Nginx, HAProxy, 게임 서버 = 모두 C++!\n";
    std::cout << "============================================================\n";
    return 0;
}
