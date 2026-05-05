/*
 * ============================================================================
 *  C++ 학습 29단원: 이벤트, 콜백, 시그널 시스템
 *  (Events, Callbacks, Signal Systems)
 * ============================================================================
 *  컴파일: g++ -std=c++17 main.cpp -o main
 *
 *  C#의 event/delegate 시스템을 C++에서 어떻게 구현하는지 완전히 설명합니다.
 *
 *  ┌──────────────────┬──────────────────────────────┬───────────────────┐
 *  │ C#               │ C++                          │ 비고              │
 *  ├──────────────────┼──────────────────────────────┼───────────────────┤
 *  │ delegate          │ std::function / 함수포인터    │ 호출 가능 객체     │
 *  │ event             │ 직접 구현 (Event<T>)          │ C++엔 내장 없음   │
 *  │ Action<T>         │ std::function<void(T)>       │ 반환 없는 콜백     │
 *  │ Func<T,R>         │ std::function<R(T)>          │ 반환 있는 콜백     │
 *  │ EventHandler      │ std::function<void(obj,Args)>│ 센더+인자 패턴    │
 *  │ += / -=           │ subscribe / unsubscribe      │ 이벤트 구독       │
 *  │ UnityEvent        │ Signal<Args...>              │ 시그널/슬롯       │
 *  │ Console.CancelKey │ signal(SIGINT, handler)      │ OS 시그널         │
 *  └──────────────────┴──────────────────────────────┴───────────────────┘
 */

#include <iostream>
#include <functional>   // std::function
#include <vector>
#include <string>
#include <map>
#include <memory>       // shared_ptr, weak_ptr
#include <algorithm>
#include <queue>
#include <csignal>      // signal(), SIGINT 등
#include <typeindex>

using namespace std;

// ============================================================================
//  레슨 1: 함수 포인터 (Function Pointers)
// ============================================================================
// C에서 온 가장 원시적인 콜백입니다.
// C# 비유: "delegate를 타입 없이 쓰는 것과 비슷합니다"
//
// C#:  delegate void MyCallback(int x);  MyCallback cb = SomeMethod;  cb(42);
// C++: void (*cb)(int) = SomeFunction;   cb(42);
//
// 차이점: C#은 delegate라는 타입 시스템이 있지만,
//        C++ 함수 포인터는 그냥 "메모리 주소"입니다.
//        마치 집 주소를 적어놓고 나중에 찾아가는 것과 같아요!
namespace Lesson1_FunctionPointers {

    void sayHello(int times) {
        for (int i = 0; i < times; i++) cout << "안녕하세요! ";
        cout << endl;
    }
    void sayGoodbye(int times) {
        for (int i = 0; i < times; i++) cout << "잘 가요! ";
        cout << endl;
    }
    int add(int a, int b) { return a + b; }
    int multiply(int a, int b) { return a * b; }

    // 방법 1: typedef로 가독성 높이기 (C 스타일)
    // C# 비유: delegate void GreetCallback(int times);
    typedef void (*GreetCallback)(int);

    // 방법 2: using으로 가독성 높이기 (C++11, 추천!)
    // C# 비유: using MathOp = Func<int, int, int>;
    using MathOperation = int (*)(int, int);

    // 콜백 등록/호출 패턴 - C# 비유: void DoWork(Action<int> callback)
    void repeatGreeting(GreetCallback callback, int times) {
        cout << "  [콜백 함수를 호출합니다!]" << endl;
        callback(times);
    }

    // 함수 포인터 배열 - C# 비유: Func<int,int,int>[] operations = { Add, Mul };
    void demonstrateFunctionPointerArray() {
        MathOperation ops[] = { add, multiply };
        const char* names[] = { "더하기", "곱하기" };
        cout << "  함수 포인터 배열:" << endl;
        for (int i = 0; i < 2; i++)
            cout << "    " << names[i] << "(3, 4) = " << ops[i](3, 4) << endl;
    }

    // 콜백을 사용하는 정렬 - C# 비유: Array.Sort(arr, comparison);
    using CompareFunc = bool (*)(int, int);
    void bubbleSort(int arr[], int size, CompareFunc compare) {
        for (int i = 0; i < size - 1; i++)
            for (int j = 0; j < size - i - 1; j++)
                if (compare(arr[j], arr[j + 1]))
                    swap(arr[j], arr[j + 1]);
    }
    bool ascending(int a, int b) { return a > b; }
    bool descending(int a, int b) { return a < b; }

    void run() {
        cout << "========================================" << endl;
        cout << " 레슨 1: 함수 포인터 (Function Pointers)" << endl;
        cout << "========================================" << endl;

        // 1) 기본 함수 포인터
        cout << "\n[1] 기본 함수 포인터:" << endl;
        void (*greet)(int) = sayHello;   // 함수 주소를 변수에 저장
        greet(3);
        greet = sayGoodbye;              // 다른 함수로 변경 가능!
        greet(2);

        // 2) typedef/using 사용
        cout << "\n[2] typedef/using으로 깔끔하게:" << endl;
        GreetCallback cb = sayHello;
        repeatGreeting(cb, 2);
        repeatGreeting(sayGoodbye, 1);

        // 3) 함수 포인터 배열
        cout << "\n[3] 함수 포인터 배열:" << endl;
        demonstrateFunctionPointerArray();

        // 4) 콜백으로 정렬 (C# Comparison<T> delegate와 비슷)
        cout << "\n[4] 콜백 정렬:" << endl;
        int arr[] = {5, 2, 8, 1, 9, 3};
        bubbleSort(arr, 6, ascending);
        cout << "  오름차순: ";
        for (int i = 0; i < 6; i++) cout << arr[i] << " ";
        cout << endl;
        bubbleSort(arr, 6, descending);
        cout << "  내림차순: ";
        for (int i = 0; i < 6; i++) cout << arr[i] << " ";
        cout << endl;

        cout << "\n  함수 포인터의 한계:" << endl;
        cout << "    - 람다(캡처 있는)를 저장할 수 없음" << endl;
        cout << "    - 멤버 함수를 직접 저장할 수 없음" << endl;
        cout << "    - 이 한계를 극복한 것이 std::function!" << endl;
    }
}

// ============================================================================
//  레슨 2: std::function & 람다 콜백
// ============================================================================
// "어떤 호출 가능한 것이든 담을 수 있는 만능 그릇"입니다.
// C# 비유: "Action<T>, Func<T,R>과 완전히 같습니다!"
//
// std::function<void()>        = C#의 Action
// std::function<void(int)>     = C#의 Action<int>
// std::function<int(int)>      = C#의 Func<int, int>
// std::function<bool(int,int)> = C#의 Func<int, int, bool>
//
// 람다란? 이름 없는 함수를 그 자리에서 만드는 것!
// C#: (x) => x * 2      C++: [](int x) { return x * 2; }
namespace Lesson2_StdFunction {

    using LogCallback = function<void(const string&)>;
    using Calculator = function<int(int, int)>;

    // 콜백 체인: 여러 콜백을 순서대로 실행
    // C# 비유: event에 += 로 여러 핸들러를 등록하는 것
    class CallbackChain {
        vector<LogCallback> callbacks_;
    public:
        void addCallback(LogCallback cb) { callbacks_.push_back(move(cb)); }
        void invoke(const string& msg) {
            for (auto& cb : callbacks_) cb(msg);
        }
        size_t count() const { return callbacks_.size(); }
    };

    // 템플릿 콜백 - 가장 빠른 방법! 컴파일 타임에 인라인 가능
    template<typename Func>
    auto applyTwice(Func f, int x) { return f(f(x)); }

    void run() {
        cout << "\n========================================" << endl;
        cout << " 레슨 2: std::function & 람다 콜백" << endl;
        cout << "========================================" << endl;

        // 1) std::function = C#의 Action/Func
        cout << "\n[1] std::function = C#의 Action/Func:" << endl;
        function<void()> action = []() { cout << "  Action 실행!" << endl; };
        action();

        function<void(const string&)> actionStr = [](const string& s) {
            cout << "  Action<string>: " << s << endl;
        };
        actionStr("안녕하세요");

        function<int(int)> doubler = [](int x) { return x * 2; };
        cout << "  Func<int,int>: doubler(5) = " << doubler(5) << endl;

        // 2) 람다 캡처 (C# 클로저와 같음)
        cout << "\n[2] 람다 캡처:" << endl;
        int multiplier = 10;
        // [=] 값으로 캡처(복사본), [&] 참조로 캡처(원본 공유)
        auto byValue = [=](int x) { return x * multiplier; };
        auto byRef = [&](int x) { multiplier++; return x * multiplier; };
        cout << "  값 캡처: 5 * 10 = " << byValue(5) << endl;
        cout << "  참조 캡처: 5 * 11 = " << byRef(5) << endl;
        cout << "  multiplier 변경됨: " << multiplier << endl;

        // 3) 콜백 등록 패턴 (C# event += 와 비슷)
        cout << "\n[3] 콜백 체인:" << endl;
        CallbackChain logger;
        logger.addCallback([](const string& msg) {
            cout << "    [콘솔] " << msg << endl;
        });
        logger.addCallback([](const string& msg) {
            cout << "    [대문자] ";
            for (char c : msg) cout << (char)toupper(c);
            cout << endl;
        });
        logger.addCallback([](const string& msg) {
            cout << "    [길이] " << msg.size() << "글자" << endl;
        });
        cout << "  " << logger.count() << "개 콜백 등록됨" << endl;
        logger.invoke("Hello World");

        // 4) std::function에 다양한 것 담기
        cout << "\n[4] std::function은 뭐든 담는 만능 그릇:" << endl;
        Calculator calc = [](int a, int b) { return a + b; };
        cout << "  람다(더하기): " << calc(3, 4) << endl;
        calc = [](int a, int b) { return a * b; };
        cout << "  람다(곱하기): " << calc(3, 4) << endl;

        // 5) 성능 비교
        cout << "\n[5] 성능 비교:" << endl;
        cout << "  템플릿: applyTwice(x*2, 3) = "
             << applyTwice([](int x) { return x * 2; }, 3) << " (3->6->12)" << endl;
        cout << "  성능 순위: 함수포인터 > 템플릿 > std::function" << endl;
        cout << "  대부분 std::function으로 충분합니다!" << endl;
    }
}

// ============================================================================
//  레슨 3: C# event 시스템을 C++로 완벽 구현
// ============================================================================
// C#: public event EventHandler<ClickEventArgs> OnClick;
//     button.OnClick += (sender, e) => { Console.WriteLine("클릭!"); };
//
// C++에는 event 키워드가 없습니다!
// 직접 Event<T> 클래스를 만들면 C#과 거의 동일하게 사용 가능!
namespace Lesson3_EventSystem {

    // EventArgs 기본 클래스 - C# System.EventArgs와 동일
    struct EventArgs { virtual ~EventArgs() = default; };

    // Event<Args...> 클래스 - C# event EventHandler<TEventArgs> 와 동일!
    // subscribe = +=, unsubscribe = -=, invoke = Invoke()
    template<typename... Args>
    class Event {
    public:
        using HandlerFunc = function<void(Args...)>;
        using HandlerId = size_t;
    private:
        map<HandlerId, HandlerFunc> handlers_;
        HandlerId nextId_ = 0;
    public:
        // C# 비유: event += handler → ID를 반환해서 나중에 -= 가능
        HandlerId subscribe(HandlerFunc handler) {
            HandlerId id = nextId_++;
            handlers_[id] = move(handler);
            return id;
        }
        // C# 비유: event -= handler
        void unsubscribe(HandlerId id) { handlers_.erase(id); }
        // C# 비유: event?.Invoke(args)  멀티캐스트: 모든 핸들러 호출!
        void invoke(Args... args) {
            for (auto& [id, handler] : handlers_) handler(args...);
        }
        bool hasSubscribers() const { return !handlers_.empty(); }
        size_t subscriberCount() const { return handlers_.size(); }
        void clear() { handlers_.clear(); }
        // += 연산자로 C# 스타일에 더 가깝게!
        HandlerId operator+=(HandlerFunc handler) { return subscribe(move(handler)); }
    };

    // --- sender + EventArgs 패턴 ---
    // C# 비유: EventHandler<TEventArgs>(object sender, TEventArgs e)
    struct ClickEventArgs : EventArgs {
        int x, y;
        int clickCount;
        ClickEventArgs(int x, int y, int count = 1) : x(x), y(y), clickCount(count) {}
    };

    struct TextChangedEventArgs : EventArgs {
        string oldText, newText;
        TextChangedEventArgs(string o, string n) : oldText(move(o)), newText(move(n)) {}
    };

    // Button - C# System.Windows.Forms.Button
    class Button {
        string name_;
    public:
        Event<Button*, ClickEventArgs> onClick;  // C#: public event EventHandler<ClickEventArgs> OnClick;
        explicit Button(string name) : name_(move(name)) {}
        const string& name() const { return name_; }
        void click(int x, int y) {
            cout << "  [" << name_ << "] 클릭됨 at (" << x << "," << y << ")" << endl;
            onClick.invoke(this, ClickEventArgs(x, y));
        }
    };

    // TextBox - C# System.Windows.Forms.TextBox
    class TextBox {
        string name_, text_;
    public:
        Event<TextBox*, TextChangedEventArgs> onTextChanged;
        explicit TextBox(string name) : name_(move(name)) {}
        const string& name() const { return name_; }
        const string& text() const { return text_; }
        void setText(const string& newText) {
            if (text_ != newText) {
                string old = text_;
                text_ = newText;
                onTextChanged.invoke(this, TextChangedEventArgs(old, newText));
            }
        }
    };

    void run() {
        cout << "\n========================================" << endl;
        cout << " 레슨 3: C# event를 C++로 완벽 구현" << endl;
        cout << "========================================" << endl;

        // 1) 기본 Event<T>
        cout << "\n[1] 기본 Event<T> 사용:" << endl;
        Event<string> onMessage;
        auto id1 = onMessage.subscribe([](const string& msg) {
            cout << "    핸들러1: " << msg << endl;
        });
        auto id2 = onMessage.subscribe([](const string& msg) {
            cout << "    핸들러2: [" << msg << "]" << endl;
        });
        cout << "  구독자 수: " << onMessage.subscriberCount() << endl;
        onMessage.invoke("안녕하세요!");
        onMessage.unsubscribe(id1);
        cout << "  핸들러1 해제 후:" << endl;
        onMessage.invoke("핸들러1은 안 보임!");

        // 2) Button 이벤트 (sender + args)
        cout << "\n[2] Button OnClick (C# WinForms 스타일):" << endl;
        Button okButton("확인"), cancelButton("취소");

        okButton.onClick.subscribe([](Button* sender, ClickEventArgs e) {
            cout << "    -> [" << sender->name() << "] 처리! 좌표: ("
                 << e.x << "," << e.y << ")" << endl;
        });
        cancelButton.onClick.subscribe([](Button* sender, ClickEventArgs e) {
            cout << "    -> [" << sender->name() << "] 취소 처리!" << endl;
        });
        okButton.click(100, 50);
        cancelButton.click(200, 50);

        // 3) TextBox 이벤트
        cout << "\n[3] TextBox OnTextChanged:" << endl;
        TextBox nameBox("이름입력");
        nameBox.onTextChanged.subscribe([](TextBox* sender, TextChangedEventArgs e) {
            cout << "    -> [" << sender->name() << "] '" << e.oldText
                 << "' -> '" << e.newText << "'" << endl;
        });
        nameBox.setText("홍");
        nameBox.setText("홍길동");
        nameBox.setText("홍길동");  // 같으면 이벤트 안 발생!

        // 4) 멀티캐스트 (여러 핸들러)
        cout << "\n[4] 멀티캐스트 (+=로 여러 핸들러 등록):" << endl;
        Button multiBtn("다중이벤트");
        multiBtn.onClick += [](Button*, ClickEventArgs) {
            cout << "    -> 로깅: 클릭 기록" << endl;
        };
        multiBtn.onClick += [](Button*, ClickEventArgs) {
            cout << "    -> UI: 색상 변경" << endl;
        };
        multiBtn.onClick += [](Button*, ClickEventArgs) {
            cout << "    -> 분석: 통계 업데이트" << endl;
        };
        cout << "  " << multiBtn.onClick.subscriberCount() << "개 핸들러 등록" << endl;
        multiBtn.click(50, 50);
    }
}

// ============================================================================
//  레슨 4: 옵저버 패턴 심화
// ============================================================================
// 옵저버 패턴: "관찰자"가 "대상"을 지켜보다가 변화시 알림 받는 패턴
// C# event가 사실 옵저버 패턴의 구현입니다!
// 유튜브 구독과 같아요: 유튜버가 영상 올리면 구독자가 알림 받음!
namespace Lesson4_ObserverAdvanced {

    // --- 약한 참조 옵저버 (weak_ptr로 dangling 방지) ---
    // 문제: 옵저버가 삭제되었는데 이벤트 발생하면? -> 크래시!
    // 해결: weak_ptr로 살아있는지 확인!  C# 비유: WeakReference<T>
    class IObserver {
    public:
        virtual ~IObserver() = default;
        virtual void onNotify(const string& event, int data) = 0;
    };

    class SafeEvent {
        vector<weak_ptr<IObserver>> observers_;
    public:
        void subscribe(shared_ptr<IObserver> obs) { observers_.push_back(obs); }
        void notify(const string& event, int data) {
            auto it = observers_.begin();
            while (it != observers_.end()) {
                if (auto obs = it->lock()) {  // 아직 살아있으면 호출
                    obs->onNotify(event, data);
                    ++it;
                } else {
                    cout << "    [자동 정리] 삭제된 옵저버 제거" << endl;
                    it = observers_.erase(it);
                }
            }
        }
    };

    class ConsoleLogger : public IObserver {
        string name_;
    public:
        explicit ConsoleLogger(string name) : name_(move(name)) {}
        ~ConsoleLogger() { cout << "    [소멸] " << name_ << " 삭제됨" << endl; }
        void onNotify(const string& event, int data) override {
            cout << "    [" << name_ << "] " << event << ": " << data << endl;
        }
    };

    // --- 이벤트 버스 (글로벌 이벤트 시스템) ---
    // C# 비유: MediatR, Prism의 EventAggregator
    // 서로 모르는 컴포넌트끼리 통신 가능!
    class EventBus {
        map<string, vector<function<void(int)>>> handlers_;
        EventBus() = default;
    public:
        static EventBus& instance() { static EventBus bus; return bus; }
        void subscribe(const string& name, function<void(int)> h) {
            handlers_[name].push_back(move(h));
        }
        void publish(const string& name, int data) {
            if (handlers_.count(name))
                for (auto& h : handlers_[name]) h(data);
        }
        void clear() { handlers_.clear(); }
    };

    // --- 비동기 이벤트 큐 (우선순위) ---
    // C# 비유: Channel<T>, BlockingCollection<T>
    // 게임/서버에서 이벤트를 나중에 처리할 때!
    struct GameEvent {
        string type;
        int data;
        int priority;
        bool operator<(const GameEvent& o) const { return priority < o.priority; }
    };

    class EventQueue {
        priority_queue<GameEvent> queue_;
        map<string, vector<function<void(const GameEvent&)>>> handlers_;
    public:
        void enqueue(const string& type, int data, int priority = 0) {
            queue_.push({type, data, priority});
        }
        void on(const string& type, function<void(const GameEvent&)> h) {
            handlers_[type].push_back(move(h));
        }
        void processAll() {
            while (!queue_.empty()) {
                GameEvent e = queue_.top(); queue_.pop();
                if (handlers_.count(e.type))
                    for (auto& h : handlers_[e.type]) h(e);
            }
        }
        size_t pending() const { return queue_.size(); }
    };

    void run() {
        cout << "\n========================================" << endl;
        cout << " 레슨 4: 옵저버 패턴 심화" << endl;
        cout << "========================================" << endl;

        // 1) 약한 참조 옵저버
        cout << "\n[1] 약한 참조 옵저버 (dangling 방지):" << endl;
        SafeEvent safeEvent;
        auto logger1 = make_shared<ConsoleLogger>("로거1");
        auto logger2 = make_shared<ConsoleLogger>("로거2");
        safeEvent.subscribe(logger1);
        safeEvent.subscribe(logger2);
        cout << "  두 옵저버에게 알림:" << endl;
        safeEvent.notify("플레이어이동", 100);
        cout << "\n  로거2 삭제:" << endl;
        logger2.reset();
        cout << "  삭제 후 알림 (자동 정리):" << endl;
        safeEvent.notify("플레이어점프", 200);

        // 2) 이벤트 버스
        cout << "\n[2] 이벤트 버스 (글로벌 이벤트):" << endl;
        auto& bus = EventBus::instance();
        bus.clear();
        bus.subscribe("PlayerDied", [](int id) {
            cout << "    [UI] 플레이어 " << id << " 사망 표시" << endl;
        });
        bus.subscribe("PlayerDied", [](int) {
            cout << "    [사운드] 사망 효과음 재생" << endl;
        });
        bus.subscribe("ScoreChanged", [](int score) {
            cout << "    [UI] 점수: " << score << endl;
        });
        bus.publish("PlayerDied", 1);
        bus.publish("ScoreChanged", 9999);

        // 3) 이벤트 큐 (우선순위)
        cout << "\n[3] 이벤트 큐 (우선순위):" << endl;
        EventQueue queue;
        queue.on("damage", [](const GameEvent& e) {
            cout << "    [처리] 데미지: " << e.data << " (우선순위:" << e.priority << ")" << endl;
        });
        queue.on("heal", [](const GameEvent& e) {
            cout << "    [처리] 힐: " << e.data << " (우선순위:" << e.priority << ")" << endl;
        });
        queue.enqueue("damage", 50, 1);
        queue.enqueue("heal", 30, 5);
        queue.enqueue("damage", 100, 10);  // 가장 높은 우선순위
        queue.enqueue("heal", 10, 3);
        cout << "  대기: " << queue.pending() << "개 -> 우선순위 순서로 처리:" << endl;
        queue.processAll();
    }
}

// ============================================================================
//  레슨 5: 시그널/슬롯 패턴 (Qt 스타일)
// ============================================================================
// Qt 프레임워크의 이벤트 시스템: 시그널 발생 -> 연결된 슬롯 실행
// C# 비유: "Unity의 UnityEvent와 거의 같습니다!"
//   UnityEvent.AddListener = connect,  UnityEvent.Invoke = emit
namespace Lesson5_SignalSlot {

    // Signal<Args...> 구현 - Qt의 시그널/슬롯을 간단하게 구현
    template<typename... Args>
    class Signal {
    public:
        using SlotFunc = function<void(Args...)>;
        using SlotId = size_t;
    private:
        map<SlotId, SlotFunc> slots_;
        SlotId nextId_ = 0;
    public:
        // connect = AddListener, disconnect = RemoveListener
        SlotId connect(SlotFunc slot) {
            SlotId id = nextId_++;
            slots_[id] = move(slot);
            return id;
        }
        void disconnect(SlotId id) { slots_.erase(id); }
        // emit = Invoke
        void emit(Args... args) {
            for (auto& [id, slot] : slots_) slot(args...);
        }
        void disconnectAll() { slots_.clear(); }
        size_t slotCount() const { return slots_.size(); }
    };

    // 게임 HealthComponent 예제
    class HealthComponent {
        int health_, maxHealth_;
    public:
        Signal<int, int> onHealthChanged;  // (현재HP, 최대HP)
        Signal<> onDeath;
        Signal<int> onDamaged;

        HealthComponent(int maxHp) : health_(maxHp), maxHealth_(maxHp) {}
        int health() const { return health_; }

        void takeDamage(int amount) {
            int old = health_;
            health_ = max(0, health_ - amount);
            cout << "  데미지 " << amount << "! HP: " << old << " -> " << health_ << endl;
            onDamaged.emit(amount);
            onHealthChanged.emit(health_, maxHealth_);
            if (health_ <= 0 && old > 0) onDeath.emit();
        }
        void heal(int amount) {
            int old = health_;
            health_ = min(maxHealth_, health_ + amount);
            if (health_ != old) {
                cout << "  회복 " << amount << "! HP: " << old << " -> " << health_ << endl;
                onHealthChanged.emit(health_, maxHealth_);
            }
        }
    };

    void run() {
        cout << "\n========================================" << endl;
        cout << " 레슨 5: 시그널/슬롯 패턴 (Qt 스타일)" << endl;
        cout << "========================================" << endl;

        // 1) 기본 Signal
        cout << "\n[1] 기본 Signal<Args...>:" << endl;
        Signal<string, int> onPlayerAction;
        auto id1 = onPlayerAction.connect([](const string& a, int v) {
            cout << "    [로그] " << a << ", 값: " << v << endl;
        });
        auto id2 = onPlayerAction.connect([](const string& a, int) {
            cout << "    [통계] " << a << " 기록됨" << endl;
        });
        onPlayerAction.emit("공격", 25);
        onPlayerAction.disconnect(id1);
        cout << "  슬롯1 해제 후:" << endl;
        onPlayerAction.emit("도망", 0);

        // 2) HealthComponent
        cout << "\n[2] HealthComponent (게임):" << endl;
        HealthComponent player(100);

        player.onHealthChanged.connect([](int cur, int mx) {
            int pct = (cur * 100) / mx;
            cout << "    [HP바] ";
            for (int i = 0; i < 10; i++) cout << (i < pct / 10 ? "#" : "-");
            cout << " " << cur << "/" << mx << " (" << pct << "%)" << endl;
        });
        player.onDamaged.connect([](int amt) {
            cout << "    [이펙트] 피해 " << amt << " 표시!" << endl;
        });
        player.onDeath.connect([]() {
            cout << "    [시스템] *** 플레이어 사망! 게임 오버! ***" << endl;
        });

        player.takeDamage(30);
        player.heal(10);
        player.takeDamage(85);  // 사망!

        // 3) 시그널 체인 (시그널 -> 시그널)
        cout << "\n[3] 시그널 체인:" << endl;
        Signal<string> sig1, sig2;
        sig1.connect([&sig2](const string& msg) {
            cout << "    sig1 -> sig2 전파" << endl;
            sig2.emit(msg);
        });
        sig2.connect([](const string& msg) {
            cout << "    sig2 최종 수신: " << msg << endl;
        });
        sig1.emit("체인 메시지!");
    }
}

// ============================================================================
//  레슨 6: OS 시그널 (Unix Signals)
// ============================================================================
// 운영체제가 프로그램에게 보내는 "알림" (레슨 1~5와는 다른 개념!)
// C# 비유: "Console.CancelKeyPress += handler 와 같습니다"
//
// 주요 시그널:
//   SIGINT(2)=Ctrl+C, SIGTERM(15)=kill, SIGSEGV(11)=세그폴트
//   SIGFPE(8)=0나누기, SIGABRT(6)=abort()
namespace Lesson6_OSSignals {

    volatile sig_atomic_t g_signalReceived = 0;

    void sigintHandler(int signum) {
        g_signalReceived = signum;
        // 주의: 여기서 cout/new/malloc 쓰면 안 됩니다! 플래그만 설정!
    }

    void run() {
        cout << "\n========================================" << endl;
        cout << " 레슨 6: OS 시그널 (Unix Signals)" << endl;
        cout << "========================================" << endl;

        cout << "\n[1] OS 시그널 목록:" << endl;
        cout << "  SIGINT  (2)  : Ctrl+C - 중단 요청" << endl;
        cout << "  SIGTERM (15) : kill 명령 - 종료 요청" << endl;
        cout << "  SIGSEGV (11) : 잘못된 메모리 접근" << endl;
        cout << "  SIGFPE  (8)  : 0으로 나누기" << endl;
        cout << "  SIGABRT (6)  : abort() 호출" << endl;

        cout << "\n[2] signal() 함수로 핸들러 등록:" << endl;
        cout << "  C#: Console.CancelKeyPress += handler;" << endl;
        cout << "  C++: signal(SIGINT, myHandler);" << endl;

        auto prev = signal(SIGINT, sigintHandler);
        cout << "  SIGINT 핸들러 등록됨" << endl;
        signal(SIGINT, prev);  // 복원

        cout << "\n[3] 시그널 핸들러 안전 규칙:" << endl;
        cout << "  OK: 전역 플래그 설정, write() 시스템콜, _exit()" << endl;
        cout << "  NO: cout/printf, new/delete, malloc/free, mutex, STL" << endl;
        cout << "\n  올바른 패턴:" << endl;
        cout << "    volatile sig_atomic_t running = 1;" << endl;
        cout << "    void handler(int) { running = 0; }" << endl;
        cout << "    while(running) { /* 메인 루프 */ }" << endl;

        cout << "\n[4] C# vs C++ 시그널 대응:" << endl;
        cout << "  Console.CancelKeyPress    -> signal(SIGINT, handler)" << endl;
        cout << "  UnhandledException        -> signal(SIGSEGV, handler)" << endl;
        cout << "  Process.Kill()            -> kill(pid, SIGTERM)" << endl;
        cout << "  Environment.Exit()        -> _exit() 또는 raise(SIGTERM)" << endl;

        // 5) raise()로 직접 시그널 보내기 데모
        cout << "\n[5] raise() 데모:" << endl;
        signal(SIGINT, sigintHandler);
        raise(SIGINT);  // 자기 자신에게 SIGINT
        if (g_signalReceived == SIGINT)
            cout << "  SIGINT 수신! g_signalReceived = " << g_signalReceived << endl;
        signal(SIGINT, SIG_DFL);  // 기본 핸들러 복원
        g_signalReceived = 0;
    }
}

// ============================================================================
//  레슨 7: 실전 종합 -- GUI 이벤트 시뮬레이터
// ============================================================================
// C# WinForms/WPF 이벤트를 C++로 거의 동일하게 구현!
//
// C# WinForms/WPF와 1:1 대응:
//   Control=Widget, Button=GuiButton, TextBox=GuiTextBox, Form=Window
//   Click=onClick, TextChanged=onTextChanged, FormClosing=onClosing
//   Control.Parent=parent_, Event bubbling=propagateEvent()
namespace Lesson7_GuiSimulator {

    // Signal 재정의 (독립 네임스페이스)
    template<typename... Args>
    class Signal {
    public:
        using SlotFunc = function<void(Args...)>;
        using SlotId = size_t;
    private:
        map<SlotId, SlotFunc> slots_;
        SlotId nextId_ = 0;
    public:
        SlotId connect(SlotFunc slot) {
            SlotId id = nextId_++; slots_[id] = move(slot); return id;
        }
        void disconnect(SlotId id) { slots_.erase(id); }
        void emit(Args... args) { for (auto& [id, s] : slots_) s(args...); }
        size_t slotCount() const { return slots_.size(); }
    };

    // 이벤트 인자들
    struct MouseEventArgs {
        int x, y;
        string button;
        bool handled = false;  // true면 버블링 중단
    };
    struct KeyEventArgs {
        char key;
        bool shift, ctrl;
        bool handled = false;
    };
    struct ClosingEventArgs {
        bool cancel = false;  // C# FormClosingEventArgs.Cancel = true 와 동일
    };

    // Widget 기본 클래스 - C# System.Windows.Forms.Control
    class Widget {
    protected:
        string name_;
        Widget* parent_ = nullptr;
        vector<Widget*> children_;
        bool visible_ = true, enabled_ = true;
    public:
        Signal<Widget*, MouseEventArgs&> onMouseClick;
        Signal<Widget*, KeyEventArgs&> onKeyPress;

        explicit Widget(string name) : name_(move(name)) {}
        virtual ~Widget() = default;
        const string& name() const { return name_; }
        Widget* parent() const { return parent_; }

        void addChild(Widget* child) {
            child->parent_ = this;
            children_.push_back(child);
        }
        // 이벤트 전파 (bubbling): 자식 -> 부모로 거품처럼 올라감!
        // C# WPF: RoutedEvent의 Bubble 전략
        void propagateMouseEvent(MouseEventArgs& e) {
            onMouseClick.emit(this, e);
            if (!e.handled && parent_) {
                cout << "    [버블링] " << name_ << " -> " << parent_->name() << endl;
                parent_->propagateMouseEvent(e);
            }
        }
        virtual string typeName() const { return "Widget"; }
    };

    // GuiButton - C# System.Windows.Forms.Button
    class GuiButton : public Widget {
    public:
        Signal<GuiButton*> onClick;
        explicit GuiButton(string name) : Widget(move(name)) {}
        void click(int x, int y) {
            if (!enabled_) { cout << "  [" << name_ << "] 비활성화" << endl; return; }
            cout << "  [" << name_ << "] 버튼 클릭!" << endl;
            onClick.emit(this);
            MouseEventArgs e{x, y, "left"};
            propagateMouseEvent(e);
        }
        void setEnabled(bool e) { enabled_ = e; }
        string typeName() const override { return "Button"; }
    };

    // GuiTextBox - C# System.Windows.Forms.TextBox
    class GuiTextBox : public Widget {
        string text_;
    public:
        Signal<GuiTextBox*, const string&, const string&> onTextChanged;
        explicit GuiTextBox(string name) : Widget(move(name)) {}
        const string& text() const { return text_; }
        void setText(const string& t) {
            if (text_ != t) {
                string old = text_; text_ = t;
                cout << "  [" << name_ << "] '" << old << "' -> '" << t << "'" << endl;
                onTextChanged.emit(this, old, t);
            }
        }
        string typeName() const override { return "TextBox"; }
    };

    // Window - C# System.Windows.Forms.Form
    class Window : public Widget {
        bool isOpen_ = true;
    public:
        Signal<Window*, ClosingEventArgs&> onClosing;
        Signal<Window*> onClosed;
        explicit Window(string title) : Widget(move(title)) {}
        bool isOpen() const { return isOpen_; }
        void close() {
            if (!isOpen_) return;
            cout << "  [" << name_ << "] 닫기 시도..." << endl;
            ClosingEventArgs args;
            onClosing.emit(this, args);
            if (args.cancel) {
                cout << "  [" << name_ << "] 닫기 취소됨!" << endl;
            } else {
                isOpen_ = false;
                cout << "  [" << name_ << "] 닫힘!" << endl;
                onClosed.emit(this);
            }
        }
        string typeName() const override { return "Window"; }
    };

    void run() {
        cout << "\n========================================" << endl;
        cout << " 레슨 7: 실전 종합 -- GUI 이벤트 시뮬레이터" << endl;
        cout << "========================================" << endl;

        // GUI 구성
        cout << "\n[GUI 구성]" << endl;
        Window mainWindow("메인 윈도우");
        GuiButton okBtn("확인 버튼"), cancelBtn("취소 버튼");
        GuiTextBox nameInput("이름 입력");
        mainWindow.addChild(&okBtn);
        mainWindow.addChild(&cancelBtn);
        mainWindow.addChild(&nameInput);
        cout << "  위젯 트리: 메인윈도우 -> 확인, 취소, 이름입력" << endl;

        // 이벤트 핸들러 등록
        cout << "\n[이벤트 핸들러 등록]" << endl;
        okBtn.onClick.connect([&](GuiButton*) {
            cout << "    -> [확인] 입력된 이름: '" << nameInput.text() << "'" << endl;
        });
        cancelBtn.onClick.connect([](GuiButton*) {
            cout << "    -> [취소] 작업 취소됨" << endl;
        });
        nameInput.onTextChanged.connect([](GuiTextBox*, const string&, const string& n) {
            cout << "    -> [검증] 글자 수: " << n.size() << endl;
            if (n.size() > 10) cout << "    -> [경고] 이름이 너무 깁니다!" << endl;
        });
        mainWindow.onMouseClick.connect([](Widget*, MouseEventArgs& e) {
            cout << "    -> [윈도우] 마우스 이벤트 수신 (버블링)" << endl;
        });

        bool unsaved = true;
        mainWindow.onClosing.connect([&](Window*, ClosingEventArgs& e) {
            if (unsaved) {
                cout << "    -> [경고] 저장 안 된 변경! 닫기 취소!" << endl;
                e.cancel = true;
            }
        });
        mainWindow.onClosed.connect([](Window*) {
            cout << "    -> [시스템] 윈도우 종료 완료" << endl;
        });

        // 시뮬레이션
        cout << "\n[시뮬레이션]" << endl;
        cout << "-----------------------------------" << endl;

        cout << "\n  >> 이름 입력:" << endl;
        nameInput.setText("홍길동");

        cout << "\n  >> 확인 버튼 클릭 (버블링 포함):" << endl;
        okBtn.click(100, 200);

        cout << "\n  >> 윈도우 닫기 (변경사항 있음 -> 취소):" << endl;
        mainWindow.close();

        cout << "\n  >> 저장 후 다시 닫기:" << endl;
        unsaved = false;
        mainWindow.close();

        cout << "\n  >> 취소 버튼 클릭:" << endl;
        cancelBtn.click(200, 200);

        // 최종 대응표
        cout << "\n-----------------------------------" << endl;
        cout << "[최종] C# <-> C++ 이벤트 완벽 대응표:" << endl;
        cout << "  delegate          -> std::function / 함수포인터" << endl;
        cout << "  event             -> Event<T> / Signal<T> (직접 구현)" << endl;
        cout << "  Action<T>         -> std::function<void(T)>" << endl;
        cout << "  Func<T,R>         -> std::function<R(T)>" << endl;
        cout << "  EventHandler      -> function<void(obj*, Args)>" << endl;
        cout << "  += / -=           -> subscribe / connect" << endl;
        cout << "  Invoke()          -> invoke() / emit()" << endl;
        cout << "  UnityEvent        -> Signal<Args...>" << endl;
        cout << "  EventArgs         -> 구조체 직접 정의" << endl;
        cout << "  event bubbling    -> propagateEvent()" << endl;
        cout << "  WeakReference     -> weak_ptr" << endl;
        cout << "  CancelKeyPress    -> signal(SIGINT, handler)" << endl;
    }
}

// ============================================================================
//  main() -- 모든 레슨 실행
// ============================================================================
int main() {
    cout << "============================================================" << endl;
    cout << "  C++ 학습 29단원: 이벤트, 콜백, 시그널 시스템" << endl;
    cout << "  (Events, Callbacks, Signal Systems)" << endl;
    cout << "  C#의 event/delegate를 C++에서 완벽하게 구현하는 방법!" << endl;
    cout << "============================================================" << endl;

    cout << "\n목차:" << endl;
    cout << "  1. 함수 포인터 (가장 원시적인 콜백)" << endl;
    cout << "  2. std::function & 람다 (C# Action/Func)" << endl;
    cout << "  3. C# event 시스템 완벽 구현" << endl;
    cout << "  4. 옵저버 패턴 심화 (이벤트 버스, 큐)" << endl;
    cout << "  5. 시그널/슬롯 (Qt/Unity 스타일)" << endl;
    cout << "  6. OS 시그널 (SIGINT, SIGTERM)" << endl;
    cout << "  7. GUI 이벤트 시뮬레이터" << endl;

    /*
    =========================================================================
      레슨별 출력 흐름 가이드 (대략)
    =========================================================================
      Lesson1 (Function Pointers):
        int (*op)(int, int) = add; op(3,4) = 7
        op = sub; op(10,3) = 7
        함수 포인터 배열로 메뉴 시스템

      Lesson2 (std::function):
        function<void()> f = []{ cout << "hi"; };
        f() → "hi"
        function<int(int)> g = bind(multiply, _1, 3);
        g(5) = 15

      Lesson3 (Event<T>):
        Event<string> on_click;
        on_click += [](string s){ ... };
        on_click("button1") → 모든 구독자 호출

      Lesson4 (Observer + EventBus):
        EventBus 전역 인스턴스
        Subscribe("user.login", handler) → emit 시 호출
        weak_ptr로 자동 해제 처리 (객체 사라지면 구독 자동 해제)

      Lesson5 (Signal/Slot, Qt 스타일):
        Signal<int> value_changed;
        value_changed.connect([](int v){ ... });
        value_changed.emit(42);

      Lesson6 (OS Signals):
        signal(SIGINT, handler);  // Ctrl+C 처리
        SIGTERM, SIGSEGV 등 캡처 (단, 핸들러 안에서 가능 일은 매우 제한적)

      Lesson7 (GUI Simulator):
        Button.on_click 이벤트 → 핸들러 호출
        UI 업데이트 시뮬레이션
    =========================================================================
    */
    Lesson1_FunctionPointers::run();
    Lesson2_StdFunction::run();
    Lesson3_EventSystem::run();
    Lesson4_ObserverAdvanced::run();
    Lesson5_SignalSlot::run();
    Lesson6_OSSignals::run();
    Lesson7_GuiSimulator::run();

    cout << "\n========================================" << endl;
    cout << " 모든 레슨 완료!" << endl;
    cout << "========================================" << endl;
    cout << "\n핵심 정리:" << endl;
    cout << "  1. 함수 포인터: C 스타일, 빠르지만 제한적" << endl;
    cout << "  2. std::function: C# Action/Func과 동일한 만능 그릇" << endl;
    cout << "  3. Event<T>: C# event를 직접 구현, += 구독" << endl;
    cout << "  4. 옵저버: weak_ptr 안전, 이벤트 버스로 전역 통신" << endl;
    cout << "  5. Signal<T>: Qt/Unity 스타일 connect/emit" << endl;
    cout << "  6. OS 시그널: signal()로 Ctrl+C 등 처리" << endl;
    cout << "  7. GUI: 버블링으로 WPF 스타일 이벤트 전파" << endl;
    cout << "\n  C++에는 event 키워드가 없지만," << endl;
    cout << "  직접 만들면 오히려 더 유연하고 강력합니다!" << endl;

    return 0;
}
