/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C++ 학습 18단계: 실전 프로젝트 — 할 일 관리 앱 (TODO)
  ─ 지금까지 배운 모든 것을 종합하여 완전한 앱을 만듭니다 ─

  이 파일은 단독 실행 가능한 완전한 프로그램입니다.
  배운 개념들이 실제로 어떻게 조합되는지 보여줍니다.

  사용된 개념:
  - 클래스, 상속, 다형성 (05~06)
  - STL 컨테이너와 알고리즘 (07)
  - 스마트 포인터, RAII (08)
  - 파일 입출력, 예외 처리 (09)
  - 모던 C++ 기능 (10)
  - 디자인 패턴 (13: 싱글톤, 빌더, 옵저버)

  ■ 컴파일: g++ -std=c++17 -Wall -o todo main.cpp
  ■ 실행:   ./todo

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/
#include <iostream>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <optional>
#include <chrono>
#include <iomanip>
#include <functional>
using namespace std;


// =========================================================================
//  엔티티: Todo 항목
// =========================================================================
enum class Priority { LOW, MEDIUM, HIGH };

string priority_to_string(Priority p) {
    switch (p) {
        case Priority::LOW:    return "낮음";
        case Priority::MEDIUM: return "보통";
        case Priority::HIGH:   return "높음";
    }
    return "?";
}

Priority string_to_priority(const string& s) {
    if (s == "높음" || s == "high" || s == "3") return Priority::HIGH;
    if (s == "보통" || s == "medium" || s == "2") return Priority::MEDIUM;
    return Priority::LOW;
}

struct Todo {
    int         id;
    string      title;
    string      description;
    Priority    priority;
    bool        completed;
    string      created_at;

    // CSV 직렬화
    string to_csv() const {
        ostringstream oss;
        oss << id << ","
            << title << ","
            << description << ","
            << static_cast<int>(priority) << ","
            << completed << ","
            << created_at;
        return oss.str();
    }

    // CSV 역직렬화
    static optional<Todo> from_csv(const string& line) {
        istringstream iss(line);
        Todo t;
        string token;
        try {
            getline(iss, token, ','); t.id = stoi(token);
            getline(iss, t.title, ',');
            getline(iss, t.description, ',');
            getline(iss, token, ','); t.priority = static_cast<Priority>(stoi(token));
            getline(iss, token, ','); t.completed = (token == "1");
            getline(iss, t.created_at, ',');
            return t;
        } catch (...) {
            return nullopt;
        }
    }

    void print() const {
        cout << "  "
             << (completed ? "[v]" : "[ ]") << " "
             << "#" << id << " "
             << "[" << priority_to_string(priority) << "] "
             << title;
        if (!description.empty()) {
            cout << " — " << description;
        }
        cout << "  (" << created_at << ")\n";
    }
};


// =========================================================================
//  이벤트 시스템 (옵저버 패턴)
// =========================================================================
class EventBus {
    map<string, vector<function<void(const string&)>>> handlers_;
public:
    void on(const string& event, function<void(const string&)> handler) {
        handlers_[event].push_back(handler);
    }

    void emit(const string& event, const string& data = "") {
        if (handlers_.count(event)) {
            for (auto& handler : handlers_[event]) {
                handler(data);
            }
        }
    }
};


// =========================================================================
//  저장소: 파일 기반 영속성 (RAII 패턴)
// =========================================================================
class TodoRepository {
    string filepath_;
    vector<Todo> todos_;
    int next_id_ = 1;

public:
    explicit TodoRepository(const string& filepath)
        : filepath_(filepath) {
        load();
    }

    ~TodoRepository() {
        save();   // RAII: 소멸 시 자동 저장
    }

    void add(Todo todo) {
        todo.id = next_id_++;
        // 현재 시간 문자열
        auto now = chrono::system_clock::now();
        auto time = chrono::system_clock::to_time_t(now);
        ostringstream oss;
        oss << put_time(localtime(&time), "%Y-%m-%d %H:%M");
        todo.created_at = oss.str();
        todos_.push_back(todo);
    }

    bool remove(int id) {
        auto it = find_if(todos_.begin(), todos_.end(),
                          [id](const Todo& t) { return t.id == id; });
        if (it != todos_.end()) {
            todos_.erase(it);
            return true;
        }
        return false;
    }

    bool toggle(int id) {
        for (auto& t : todos_) {
            if (t.id == id) {
                t.completed = !t.completed;
                return true;
            }
        }
        return false;
    }

    const vector<Todo>& all() const { return todos_; }

    vector<Todo> filter(function<bool(const Todo&)> pred) const {
        vector<Todo> result;
        copy_if(todos_.begin(), todos_.end(),
                back_inserter(result), pred);
        return result;
    }

    optional<Todo> find_by_id(int id) const {
        for (const auto& t : todos_) {
            if (t.id == id) return t;
        }
        return nullopt;
    }

    int count_completed() const {
        return count_if(todos_.begin(), todos_.end(),
                        [](const Todo& t) { return t.completed; });
    }

private:
    void load() {
        ifstream file(filepath_);
        if (!file.is_open()) return;   // 파일 없으면 빈 상태로 시작

        string line;
        while (getline(file, line)) {
            if (auto todo = Todo::from_csv(line)) {
                todos_.push_back(*todo);
                if (todo->id >= next_id_) {
                    next_id_ = todo->id + 1;
                }
            }
        }
    }

    void save() {
        ofstream file(filepath_);
        if (!file.is_open()) {
            cerr << "  [오류] 파일 저장 실패: " << filepath_ << "\n";
            return;
        }
        for (const auto& t : todos_) {
            file << t.to_csv() << "\n";
        }
    }
};


// =========================================================================
//  서비스 계층: 비즈니스 로직
// =========================================================================
class TodoService {
    TodoRepository& repo_;
    EventBus& events_;

public:
    TodoService(TodoRepository& repo, EventBus& events)
        : repo_(repo), events_(events) {}

    void add(const string& title, const string& desc, Priority pri) {
        Todo t;
        t.title = title;
        t.description = desc;
        t.priority = pri;
        t.completed = false;
        repo_.add(t);
        events_.emit("todo_added", title);
    }

    bool complete(int id) {
        if (repo_.toggle(id)) {
            if (auto t = repo_.find_by_id(id)) {
                string state = t->completed ? "완료" : "미완료";
                events_.emit("todo_toggled", "#" + to_string(id) + " → " + state);
            }
            return true;
        }
        return false;
    }

    bool remove(int id) {
        if (repo_.remove(id)) {
            events_.emit("todo_removed", "#" + to_string(id));
            return true;
        }
        return false;
    }

    void show_all() const {
        const auto& todos = repo_.all();
        if (todos.empty()) {
            cout << "\n  할 일이 없습니다. 새로 추가해보세요!\n\n";
            return;
        }

        // 미완료 먼저, 우선순위 높은 것 먼저
        auto sorted = todos;
        sort(sorted.begin(), sorted.end(), [](const Todo& a, const Todo& b) {
            if (a.completed != b.completed) return !a.completed;
            return static_cast<int>(a.priority) > static_cast<int>(b.priority);
        });

        cout << "\n  ─────────── 할 일 목록 ───────────\n";
        for (const auto& t : sorted) {
            t.print();
        }
        cout << "  ──────────────────────────────────\n";
        cout << "  전체: " << todos.size()
             << "  완료: " << repo_.count_completed()
             << "  남음: " << (todos.size() - repo_.count_completed()) << "\n\n";
    }

    void show_by_priority(Priority pri) const {
        auto filtered = repo_.filter(
            [pri](const Todo& t) { return t.priority == pri; }
        );
        cout << "\n  [" << priority_to_string(pri) << " 우선순위]\n";
        for (const auto& t : filtered) t.print();
        cout << endl;
    }
};


// =========================================================================
//  UI 계층: 메뉴 시스템
// =========================================================================
void show_menu() {
    cout << "  ┌────────────────────────────┐\n";
    cout << "  │  TODO 관리 프로그램        │\n";
    cout << "  ├────────────────────────────┤\n";
    cout << "  │  1. 전체 목록 보기         │\n";
    cout << "  │  2. 할 일 추가             │\n";
    cout << "  │  3. 완료/미완료 전환       │\n";
    cout << "  │  4. 삭제                   │\n";
    cout << "  │  5. 우선순위별 보기        │\n";
    cout << "  │  0. 종료                   │\n";
    cout << "  └────────────────────────────┘\n";
    cout << "  선택: ";
}


// =========================================================================
//  main — 앱 실행
// =========================================================================
int main() {
    cout << "========================================\n";
    cout << "  C++ 18단계 : 실전 프로젝트 (TODO)\n";
    cout << "========================================\n\n";

    // ── 의존성 설정 ──
    EventBus events;
    TodoRepository repo("todos.csv");   // RAII: 소멸 시 자동 저장
    TodoService service(repo, events);

    // 이벤트 구독
    events.on("todo_added", [](const string& data) {
        cout << "  [알림] 새 할 일 추가: " << data << "\n";
    });
    events.on("todo_toggled", [](const string& data) {
        cout << "  [알림] 상태 변경: " << data << "\n";
    });
    events.on("todo_removed", [](const string& data) {
        cout << "  [알림] 삭제됨: " << data << "\n";
    });

    // ── 데모 데이터 (처음 실행 시) ──
    if (repo.all().empty()) {
        service.add("C++ 01~06단계 복습", "변수, 제어문, 함수, OOP", Priority::HIGH);
        service.add("디자인 패턴 공부", "싱글톤, 팩토리, 옵저버", Priority::MEDIUM);
        service.add("개인 프로젝트 시작", "TODO 앱 확장하기", Priority::LOW);
        cout << "  (데모 데이터 3개 추가됨)\n";
    }

    // ── 메인 루프 ──
    //
    //  ※ 실제 실행 시에는 아래 while문의 주석을 해제하세요.
    //  학습 파일이므로 데모 실행만 합니다.

    // 데모: 목록 보기
    service.show_all();

    // 데모: 추가
    service.add("CMake 배우기", "빌드 시스템 학습", Priority::MEDIUM);
    service.show_all();

    // 데모: 완료 처리
    service.complete(1);
    service.show_all();

    /*
    // ── 실제 대화형 모드 (주석 해제하면 동작) ──
    while (true) {
        show_menu();
        int choice;
        cin >> choice;
        cin.ignore();

        switch (choice) {
            case 0:
                cout << "\n  저장 후 종료합니다. 안녕!\n";
                return 0;

            case 1:
                service.show_all();
                break;

            case 2: {
                cout << "  제목: ";
                string title;
                getline(cin, title);
                cout << "  설명 (엔터=생략): ";
                string desc;
                getline(cin, desc);
                cout << "  우선순위 (1=낮음, 2=보통, 3=높음): ";
                string pri;
                getline(cin, pri);
                service.add(title, desc, string_to_priority(pri));
                break;
            }

            case 3: {
                cout << "  ID 번호: ";
                int id;
                cin >> id;
                if (!service.complete(id))
                    cout << "  해당 ID를 찾을 수 없습니다.\n";
                break;
            }

            case 4: {
                cout << "  삭제할 ID: ";
                int id;
                cin >> id;
                if (!service.remove(id))
                    cout << "  해당 ID를 찾을 수 없습니다.\n";
                break;
            }

            case 5: {
                cout << "  우선순위 (1=낮음, 2=보통, 3=높음): ";
                string pri;
                cin >> pri;
                cin.ignore();
                service.show_by_priority(string_to_priority(pri));
                break;
            }

            default:
                cout << "  잘못된 입력!\n";
        }
    }
    */

    // ── 프로젝트 구조 가이드 ──
    cout << R"(
  ■ 이 프로젝트를 확장하려면?
  ─────────────────────────────────────
  1. 여러 파일로 분리 (include/todo.hpp, src/todo.cpp)
  2. CMakeLists.txt 작성 (12단계 참고)
  3. Google Test 추가 (16단계 참고)
  4. JSON 저장으로 변경 (nlohmann/json)
  5. HTTP API 추가 (cpp-httplib, 15단계)
  6. CI/CD 설정 (17단계 참고)
  7. Docker 이미지 만들기 (17단계 참고)

  ■ 전체 커리큘럼 로드맵
  ═══════════════════════════════════════
  [기초]   01 변수/타입 → 02 제어문 → 03 함수 → 04 포인터
  [OOP]    05 클래스 → 06 상속/다형성
  [실전]   07 STL → 08 메모리 → 09 파일/예외 → 10 모던C++
  [도구]   11 디버깅 → 12 CMake/프레임워크
  [심화]   13 디자인패턴 → 14 멀티스레딩 → 15 네트워크
  [배포]   16 테스트 → 17 빌드/배포/CI → 18 실전 프로젝트
  ═══════════════════════════════════════
)" << endl;

    cout << "18단계 학습 완료! 전체 커리큘럼 완료!\n";
    return 0;
}
