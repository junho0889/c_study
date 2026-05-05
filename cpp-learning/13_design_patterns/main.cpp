/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C++ 학습 13단계: 디자인 패턴 (Design Patterns)
  ─ 실무에서 반복적으로 등장하는 설계 문제의 검증된 해결책 ─

  디자인 패턴은 "이런 상황에서는 이렇게 설계하면 좋다"는 레시피입니다.
  암기하는 것이 아니라, 문제 상황을 이해하고 필요할 때 꺼내 쓰는 것입니다.

  ■ 컴파일: g++ -std=c++17 -Wall -o 13_patterns main.cpp

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <map>
#include <functional>
#include <algorithm>
using namespace std;


// =========================================================================
//  패턴 1 — 싱글톤 (Singleton)
// =========================================================================
//
//  ★ 문제: 프로그램 전체에서 딱 하나만 존재해야 하는 객체
//           (설정 관리자, 로거, DB 연결 등)
//
//  ★ 해결: 생성자를 private으로 막고, 정적 메서드로만 접근
//
//  ★ 주의: 멀티스레드 환경에서는 추가 처리 필요 (14단계)
//           남용하면 전역 변수와 다를 바 없음 → 테스트 어려움

class Logger {
private:
    vector<string> logs_;

    // 생성자를 private으로 → 외부에서 new Logger() 불가!
    Logger() {
        cout << "    [Logger 생성됨 - 딱 한 번만 호출됨]\n";
    }

    // 복사/이동 금지
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;

public:
    // ★ 핵심: 정적 메서드로 유일한 인스턴스에 접근
    //   C++11 이후 지역 정적 변수는 스레드 안전하게 초기화됨
    static Logger& instance() {
        static Logger inst;    // 최초 호출 시 1번만 생성
        return inst;
    }

    void log(const string& message) {
        logs_.push_back(message);
        cout << "    [LOG] " << message << "\n";
    }

    void show_all() const {
        cout << "    --- 전체 로그 (" << logs_.size() << "건) ---\n";
        for (const auto& l : logs_) {
            cout << "    > " << l << "\n";
        }
    }
};


// =========================================================================
//  패턴 2 — 팩토리 메서드 (Factory Method)
// =========================================================================
//
//  ★ 문제: 객체를 만들 때 어떤 구체 클래스를 쓸지 모르거나,
//           if/else로 분기하는 코드가 지저분해질 때
//
//  ★ 해결: "만드는 일"을 전담하는 팩토리 함수/클래스에 위임
//
//  ★ 비유: 피자 주문 시 "피자 주세요" 하면 됨
//           어떤 오븐으로 어떻게 굽는지는 주방(팩토리)이 알아서

class Enemy {
public:
    virtual ~Enemy() = default;
    virtual void attack() const = 0;   // 순수 가상 = 자식이 반드시 구현
    virtual string name() const = 0;
};

class Goblin : public Enemy {
public:
    void attack() const override { cout << "    고블린이 곤봉으로 때린다!\n"; }
    string name() const override { return "고블린"; }
};

class Dragon : public Enemy {
public:
    void attack() const override { cout << "    드래곤이 불을 뿜는다!\n"; }
    string name() const override { return "드래곤"; }
};

class Skeleton : public Enemy {
public:
    void attack() const override { cout << "    스켈레톤이 뼈를 던진다!\n"; }
    string name() const override { return "스켈레톤"; }
};

// ★ 팩토리 함수: 문자열 이름으로 적절한 Enemy를 생성
unique_ptr<Enemy> create_enemy(const string& type) {
    if (type == "goblin")   return make_unique<Goblin>();
    if (type == "dragon")   return make_unique<Dragon>();
    if (type == "skeleton") return make_unique<Skeleton>();
    return nullptr;
}


// =========================================================================
//  패턴 3 — 옵저버 (Observer)
// =========================================================================
//
//  ★ 문제: A가 변하면 B, C, D에게 자동으로 알려야 할 때
//           (이벤트 시스템, UI 업데이트, 알림 등)
//
//  ★ 해결: "구독/발행" 구조 → 관심 있는 객체가 등록하면
//           이벤트 발생 시 자동으로 알림
//
//  ★ 비유: 유튜브 구독 → 새 영상 올리면 구독자에게 알림

// 옵저버 인터페이스 (구독자가 구현)
class IObserver {
public:
    virtual ~IObserver() = default;
    virtual void on_event(const string& event_name,
                          const string& data) = 0;
};

// 이벤트 발행자 (Subject)
class EventSystem {
    // 이벤트 이름 → 구독자 목록
    map<string, vector<IObserver*>> subscribers_;

public:
    void subscribe(const string& event, IObserver* observer) {
        subscribers_[event].push_back(observer);
    }

    void emit(const string& event, const string& data = "") {
        if (subscribers_.count(event)) {
            for (auto* obs : subscribers_[event]) {
                obs->on_event(event, data);
            }
        }
    }
};

// 구체 옵저버들
class SoundManager : public IObserver {
public:
    void on_event(const string& event, const string& data) override {
        cout << "    [사운드] " << event << " → 효과음 재생: " << data << "\n";
    }
};

class UIManager : public IObserver {
public:
    void on_event(const string& event, const string& data) override {
        cout << "    [UI] " << event << " → 화면 업데이트: " << data << "\n";
    }
};

class AchievementSystem : public IObserver {
public:
    void on_event(const string& event, const string& data) override {
        cout << "    [업적] " << event << " → 업적 체크: " << data << "\n";
    }
};


// =========================================================================
//  패턴 4 — 전략 (Strategy)
// =========================================================================
//
//  ★ 문제: 같은 작업을 여러 방법(알고리즘)으로 처리해야 할 때
//           if/else 분기 대신 알고리즘 자체를 교체 가능하게
//
//  ★ 해결: 알고리즘을 별도 클래스로 분리하고, 실행 시 교체
//
//  ★ 비유: 네비게이션 → "최단 거리" / "최소 시간" / "무료 도로만"
//           앱은 같은데 경로 계산 '전략'만 교체

class SortStrategy {
public:
    virtual ~SortStrategy() = default;
    virtual void sort(vector<int>& data) = 0;
    virtual string name() const = 0;
};

class BubbleSort : public SortStrategy {
public:
    void sort(vector<int>& data) override {
        for (size_t i = 0; i < data.size(); i++)
            for (size_t j = 0; j + 1 < data.size() - i; j++)
                if (data[j] > data[j + 1])
                    swap(data[j], data[j + 1]);
    }
    string name() const override { return "버블 정렬"; }
};

class SelectionSort : public SortStrategy {
public:
    void sort(vector<int>& data) override {
        for (size_t i = 0; i < data.size(); i++) {
            size_t min_idx = i;
            for (size_t j = i + 1; j < data.size(); j++)
                if (data[j] < data[min_idx])
                    min_idx = j;
            swap(data[i], data[min_idx]);
        }
    }
    string name() const override { return "선택 정렬"; }
};

class Sorter {
    unique_ptr<SortStrategy> strategy_;
public:
    void set_strategy(unique_ptr<SortStrategy> s) {
        strategy_ = move(s);
    }
    void sort(vector<int>& data) {
        if (strategy_) {
            cout << "    [" << strategy_->name() << "] 실행\n";
            strategy_->sort(data);
        }
    }
};


// =========================================================================
//  패턴 5 — 빌더 (Builder)
// =========================================================================
//
//  ★ 문제: 생성자 매개변수가 너무 많거나,
//           선택적 설정이 많은 복잡한 객체를 만들 때
//
//  ★ 해결: 단계별로 설정하고 마지막에 build()로 완성
//
//  ★ 비유: 햄버거 주문 — 빵, 패티, 치즈, 소스를 하나씩 고른 뒤 "완성!"

class HttpRequest {
public:
    string method;
    string url;
    map<string, string> headers;
    string body;
    int timeout_ms = 5000;

    void print() const {
        cout << "    " << method << " " << url << "\n";
        for (const auto& [k, v] : headers) {
            cout << "    " << k << ": " << v << "\n";
        }
        if (!body.empty()) cout << "    Body: " << body << "\n";
        cout << "    Timeout: " << timeout_ms << "ms\n";
    }
};

class HttpRequestBuilder {
    HttpRequest req_;
public:
    HttpRequestBuilder& method(const string& m) {
        req_.method = m; return *this;    // *this 반환 = 체이닝 가능
    }
    HttpRequestBuilder& url(const string& u) {
        req_.url = u; return *this;
    }
    HttpRequestBuilder& header(const string& key, const string& val) {
        req_.headers[key] = val; return *this;
    }
    HttpRequestBuilder& body(const string& b) {
        req_.body = b; return *this;
    }
    HttpRequestBuilder& timeout(int ms) {
        req_.timeout_ms = ms; return *this;
    }
    HttpRequest build() { return req_; }
};


// =========================================================================
//  패턴 6 — RAII (Resource Acquisition Is Initialization)
// =========================================================================
//
//  ★ C++에서 가장 중요한 패턴! (이미 08단계에서 배웠지만 복습)
//
//  ★ 핵심: 생성자에서 자원 획득, 소멸자에서 자원 해제
//           → 예외가 발생해도 자원이 반드시 정리됨
//
//  ★ 예시:  unique_ptr     → 메모리 자동 해제
//           lock_guard    → 뮤텍스 자동 해제
//           fstream       → 파일 자동 닫기
//           이 패턴 없이는 C++을 제대로 쓸 수 없음!

class Timer {
    string name_;
    // 실제로는 시작 시간을 기록하고 소멸자에서 경과 시간 출력
public:
    Timer(const string& name) : name_(name) {
        cout << "    [Timer] " << name_ << " 시작\n";
    }
    ~Timer() {
        cout << "    [Timer] " << name_ << " 종료 (자동 정리!)\n";
    }
};


// =========================================================================
//  main
// =========================================================================
int main() {
    cout << "========================================\n";
    cout << "  C++ 13단계 : 디자인 패턴\n";
    cout << "========================================\n\n";

    // ── 패턴 1: 싱글톤 ──
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  패턴 1 : 싱글톤 (Singleton)         │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    Logger::instance().log("게임 시작");
    // → 첫 호출: static Logger inst 생성 (생성자 1번만 호출)
    //   → "[Logger 생성됨 - 딱 한 번만 호출됨]" 출력
    //   → log: logs_=["게임 시작"], "[LOG] 게임 시작" 출력
    Logger::instance().log("플레이어 생성");
    // → 같은 인스턴스. logs_ = ["게임 시작", "플레이어 생성"]
    Logger::instance().log("맵 로딩 완료");
    // → logs_.size() = 3
    Logger::instance().show_all();
    // > 출력 (이 패턴 전체):
    //   [Logger 생성됨 - 딱 한 번만 호출됨]
    //   [LOG] 게임 시작
    //   [LOG] 플레이어 생성
    //   [LOG] 맵 로딩 완료
    //   --- 전체 로그 (3건) ---
    //   > 게임 시작
    //   > 플레이어 생성
    //   > 맵 로딩 완료
    cout << endl;

    // ── 패턴 2: 팩토리 ──
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  패턴 2 : 팩토리 메서드 (Factory)    │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    vector<string> enemy_types = {"goblin", "dragon", "skeleton", "goblin"};
    for (const auto& type : enemy_types) {
        // 1회: type="goblin"  → Goblin 생성
        // 2회: type="dragon"  → Dragon
        // 3회: type="skeleton"→ Skeleton
        // 4회: type="goblin"  → Goblin (또 새로 생성)
        auto enemy = create_enemy(type);
        if (enemy) {
            cout << "    생성: " << enemy->name() << " → ";
            enemy->attack();
        }
        // ▶ 루프 끝 → unique_ptr 소멸 → Enemy 소멸자 호출
    }
    // > 출력:
    //     생성: 고블린 → 고블린이 곤봉으로 때린다!
    //     생성: 드래곤 → 드래곤이 불을 뿜는다!
    //     생성: 스켈레톤 → 스켈레톤이 뼈를 던진다!
    //     생성: 고블린 → 고블린이 곤봉으로 때린다!
    cout << endl;

    // ── 패턴 3: 옵저버 ──
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  패턴 3 : 옵저버 (Observer)          │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    EventSystem events;
    SoundManager sound;
    UIManager ui;
    AchievementSystem achievement;

    events.subscribe("enemy_killed", &sound);
    events.subscribe("enemy_killed", &ui);
    events.subscribe("enemy_killed", &achievement);
    events.subscribe("level_up", &sound);
    events.subscribe("level_up", &ui);
    // → subscribers_["enemy_killed"] = [&sound, &ui, &achievement]
    // → subscribers_["level_up"]      = [&sound, &ui]

    events.emit("enemy_killed", "드래곤 처치!");
    // ▶ 3개 구독자 모두에게 호출 (등록 순서대로)
    // > 출력:
    //     [사운드] enemy_killed → 효과음 재생: 드래곤 처치!
    //     [UI] enemy_killed → 화면 업데이트: 드래곤 처치!
    //     [업적] enemy_killed → 업적 체크: 드래곤 처치!
    cout << endl;
    events.emit("level_up", "레벨 10 달성!");
    // ▶ 2개 구독자
    // > 출력:
    //     [사운드] level_up → 효과음 재생: 레벨 10 달성!
    //     [UI] level_up → 화면 업데이트: 레벨 10 달성!
    cout << endl;

    // ── 패턴 4: 전략 ──
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  패턴 4 : 전략 (Strategy)            │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    vector<int> data = {5, 2, 8, 1, 9, 3};
    Sorter sorter;

    sorter.set_strategy(make_unique<BubbleSort>());
    sorter.sort(data);
    // → 버블 정렬: 인접 비교 + 큰 값 뒤로
    // → data = [1, 2, 3, 5, 8, 9]
    cout << "    결과: ";
    for (int n : data) cout << n << " ";
    cout << "\n\n";
    // > 출력:
    //     [버블 정렬] 실행
    //     결과: 1 2 3 5 8 9

    data = {5, 2, 8, 1, 9, 3};
    sorter.set_strategy(make_unique<SelectionSort>());
    sorter.sort(data);
    // → 선택 정렬: 매 회 최소값 찾아 앞으로
    // → data = [1, 2, 3, 5, 8, 9]
    cout << "    결과: ";
    for (int n : data) cout << n << " ";
    cout << "\n\n";
    // > 출력:
    //     [선택 정렬] 실행
    //     결과: 1 2 3 5 8 9

    // ── 패턴 5: 빌더 ──
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  패턴 5 : 빌더 (Builder)             │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    auto request = HttpRequestBuilder()
        .method("POST")
        .url("/api/users")
        .header("Content-Type", "application/json")
        .header("Authorization", "Bearer token123")
        .body(R"({"name": "홍길동", "age": 25})")
        .timeout(3000)
        .build();
    // → 체이닝으로 단계별 설정.
    //   final request:
    //     method="POST", url="/api/users",
    //     headers={"Authorization":"Bearer token123",
    //              "Content-Type":"application/json"},  // map은 키 정렬됨
    //     body=R"...", timeout_ms=3000

    request.print();
    // > 출력:
    //     POST /api/users
    //     Authorization: Bearer token123
    //     Content-Type: application/json
    //     Body: {"name": "홍길동", "age": 25}
    //     Timeout: 3000ms
    cout << endl;

    // ── 패턴 6: RAII ──
    cout << "┌──────────────────────────────────────┐\n";
    cout << "│  패턴 6 : RAII                       │\n";
    cout << "└──────────────────────────────────────┘\n\n";

    {
        Timer t("데이터 처리");
        // > 출력:   [Timer] 데이터 처리 시작
        cout << "    ... 작업 중 ...\n";
        // > 출력:   ... 작업 중 ...
    }
    // ▶ 블록 종료 → t 소멸자
    // > 출력:   [Timer] 데이터 처리 종료 (자동 정리!)
    cout << endl;

    // ── 패턴 정리 ──
    cout << "  ■ 디자인 패턴 요약\n";
    cout << "  ─────────────────────────────────────\n";
    cout << "  싱글톤   : 전체에서 딱 하나만 (로거, 설정)\n";
    cout << "  팩토리   : 객체 생성을 위임 (다형성 활용)\n";
    cout << "  옵저버   : 이벤트 구독/발행 (느슨한 결합)\n";
    cout << "  전략     : 알고리즘 교체 가능 (런타임)\n";
    cout << "  빌더     : 복잡한 객체를 단계별 생성\n";
    cout << "  RAII     : 자원을 생명주기에 묶기 (C++ 핵심!)\n";
    cout << "\n  기타 중요 패턴: 데코레이터, 어댑터, 커맨드,\n";
    cout << "  상태, 프록시, 컴포지트, 반복자, 템플릿 메서드\n";

    cout << "\n13단계 학습 완료!\n";
    return 0;
}
