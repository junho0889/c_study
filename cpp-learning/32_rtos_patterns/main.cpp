/*
 * =============================================================================
 *  C++ 임베디드 학습 #32: RTOS 패턴과 실시간 시스템
 *  (Real-Time OS Patterns)
 * =============================================================================
 *
 *  컴파일: g++ -std=c++17 -o rtos_patterns main.cpp
 *  실행: ./rtos_patterns
 *
 *  ★ 실제 RTOS 없이, 패턴과 개념을 소프트웨어로 시뮬레이션합니다! ★
 *
 *  RTOS = "정해진 시간 안에 반드시 응답하는 운영체제"
 *  C# 비유: Task.Run()은 '언젠가' 실행되지만, RTOS는 '반드시 10ms 안에' 실행!
 *
 *  태스크 상태: Ready(준비) → Running(실행) → Blocked(대기) / Suspended(정지)
 *  스케줄링으로 Ready→Running, 선점/양보로 Running→Ready
 */

#include <iostream>
#include <cstdint>
#include <cstring>
#include <vector>
#include <array>
#include <queue>
#include <string>
#include <functional>
#include <algorithm>
#include <numeric>
#include <iomanip>
#include <sstream>
#include <cassert>
#include <cmath>
#include <random>
#include <map>

// ─────────────────────────────────────────────────────────────────
//  유틸리티
// ─────────────────────────────────────────────────────────────────
static void printHeader(const std::string& title) {
    std::cout << "\n";
    std::cout << "================================================================\n";
    std::cout << "  " << title << "\n";
    std::cout << "================================================================\n";
}

static void printSubHeader(const std::string& title) {
    std::cout << "\n--- " << title << " ---\n";
}

// 시뮬레이션용 시간 (틱 단위, 1틱 = 1ms)
using TickType = uint32_t;

// =================================================================
//  레슨 1: RTOS 개념
// =================================================================
/*
 *  ★ Hard Real-Time vs Soft Real-Time ★
 *
 *  Hard Real-Time (경성 실시간):
 *    데드라인을 절대 어기면 안 됨! 어기면 = 사고!
 *    예: 자동차 에어백, 심장 박동기, 비행기 제어
 *
 *  Soft Real-Time (연성 실시간):
 *    데드라인을 가끔 어겨도 괜찮음 (품질 저하 정도)
 *    예: 동영상 재생, 게임 프레임
 *
 *  실제 RTOS 종류:
 *    - FreeRTOS: 가장 널리 쓰이는 오픈소스 RTOS (ESP32, STM32)
 *    - Zephyr: Linux 재단이 관리하는 최신 RTOS
 *    - RT-Linux: 리눅스에 실시간 기능 추가
 *    - VxWorks: 상용 (화성 탐사 로버에 사용!)
 */

static void lesson1_rtos_concepts() {
    printHeader("레슨 1: RTOS 개념");

    std::cout << R"(
  ★ RTOS = Real-Time Operating System ★

  일반 OS: 태스크A ████░░████░░░░████ (불규칙, Best Effort)
  RTOS:    태스크A ██░░██░░██░░██░░██ (정확히 주기적, Deterministic)

  Hard RT: 데드라인 miss = 치명적 (에어백, 심장박동기)
  Soft RT: 데드라인 miss = 품질저하 (동영상, 게임 FPS)
)";

    std::cout << "  주요 RTOS: FreeRTOS(MIT/ESP32), Zephyr(Apache/Nordic), VxWorks(상용/항공우주)\n";
}

// =================================================================
//  레슨 2: 태스크 (Task) 관리
// =================================================================
// C# 비유: Thread보다 더 엄격한 우선순위. RTOS는 높은 우선순위가 반드시 먼저 실행됨을 보장!

// 태스크 상태 열거형
enum class TaskState : uint8_t {
    READY,       // 실행 준비 완료 (CPU만 있으면 바로 실행)
    RUNNING,     // 현재 CPU에서 실행 중
    BLOCKED,     // 이벤트/세마포어 대기 중
    SUSPENDED    // 일시 정지됨
};

static const char* taskStateToStr(TaskState s) {
    switch (s) {
        case TaskState::READY:     return "Ready";
        case TaskState::RUNNING:   return "Running";
        case TaskState::BLOCKED:   return "Blocked";
        case TaskState::SUSPENDED: return "Suspended";
    }
    return "?";
}

// TCB: Task Control Block (태스크 제어 블록)
// 각 태스크의 모든 정보를 담는 구조체 (실제 RTOS의 핵심!)
struct TCB {
    uint32_t        taskId;
    std::string     name;
    uint8_t         priority;       // 0=최저, 255=최고
    TaskState       state;
    TickType        period;         // 실행 주기 (ms)
    TickType        nextRunTick;    // 다음 실행 시각
    TickType        wcet;           // Worst Case Execution Time (최악 실행시간)
    TickType        lastRunTick;    // 마지막 실행 시각
    uint32_t        runCount;       // 실행 횟수
    std::function<void()> taskFunc; // 태스크 함수

    // 스택 시뮬레이션 (실제 RTOS에서는 태스크마다 별도 스택)
    uint32_t        stackSize;
    uint32_t        stackUsed;
};

// 간단한 선점형 스케줄러
class PriorityScheduler {
    std::vector<TCB> tasks_;
    TickType currentTick_ = 0;
    int runningTaskIdx_ = -1;

    // 스케줄링 로그
    struct ScheduleLog {
        TickType tick;
        std::string taskName;
        std::string event;  // "시작", "선점됨", "완료"
    };
    std::vector<ScheduleLog> logs_;

public:
    void addTask(const std::string& name, uint8_t priority,
                 TickType period, TickType wcet,
                 std::function<void()> func) {
        TCB tcb{};
        tcb.taskId = static_cast<uint32_t>(tasks_.size());
        tcb.name = name;
        tcb.priority = priority;
        tcb.state = TaskState::READY;
        tcb.period = period;
        tcb.nextRunTick = 0;
        tcb.wcet = wcet;
        tcb.lastRunTick = 0;
        tcb.runCount = 0;
        tcb.taskFunc = func;
        tcb.stackSize = 512;
        tcb.stackUsed = 0;
        tasks_.push_back(tcb);
    }

    // 1틱 진행
    void tick() {
        currentTick_++;

        // 주기가 된 태스크를 Ready로 변경
        for (auto& t : tasks_) {
            if (t.state != TaskState::SUSPENDED && currentTick_ >= t.nextRunTick) {
                if (t.state == TaskState::BLOCKED) {
                    t.state = TaskState::READY;
                }
            }
        }

        // 가장 높은 우선순위의 Ready 태스크 선택
        int bestIdx = -1;
        uint8_t bestPriority = 0;
        for (int i = 0; i < (int)tasks_.size(); i++) {
            if (tasks_[i].state == TaskState::READY && currentTick_ >= tasks_[i].nextRunTick) {
                if (tasks_[i].priority > bestPriority) {
                    bestPriority = tasks_[i].priority;
                    bestIdx = i;
                }
            }
        }

        // 선점: 현재 실행 중인 태스크보다 높은 우선순위가 Ready이면 교체
        if (runningTaskIdx_ >= 0 && bestIdx >= 0 &&
            tasks_[bestIdx].priority > tasks_[runningTaskIdx_].priority) {
            tasks_[runningTaskIdx_].state = TaskState::READY;
            logs_.push_back({currentTick_, tasks_[runningTaskIdx_].name, "선점됨"});
            runningTaskIdx_ = -1;
        }

        // 실행 중인 태스크가 없으면 선택
        if (runningTaskIdx_ < 0 && bestIdx >= 0) {
            runningTaskIdx_ = bestIdx;
            tasks_[bestIdx].state = TaskState::RUNNING;
            tasks_[bestIdx].lastRunTick = currentTick_;
            tasks_[bestIdx].runCount++;
            logs_.push_back({currentTick_, tasks_[bestIdx].name, "시작"});

            // 태스크 실행 (시뮬레이션: 즉시 완료)
            if (tasks_[bestIdx].taskFunc) {
                tasks_[bestIdx].taskFunc();
            }

            // 실행 완료 → 다음 주기까지 Blocked
            tasks_[bestIdx].state = TaskState::BLOCKED;
            tasks_[bestIdx].nextRunTick = currentTick_ + tasks_[bestIdx].period;
            logs_.push_back({currentTick_, tasks_[bestIdx].name, "완료"});
            runningTaskIdx_ = -1;
        }
    }

    // N틱 시뮬레이션
    void runFor(TickType ticks) {
        for (TickType i = 0; i < ticks; i++) {
            tick();
        }
    }

    // 스케줄링 결과 출력
    void printTimeline(TickType maxTick = 50) const {
        std::cout << "\n  스케줄링 타임라인 (간트 차트):\n";
        std::cout << "  틱: ";
        for (TickType t = 0; t <= maxTick; t += 5) {
            std::cout << std::setw(5) << t;
        }
        std::cout << "\n";

        for (const auto& task : tasks_) {
            std::cout << "  " << std::setw(8) << task.name << ": ";
            for (TickType t = 1; t <= maxTick; t++) {
                bool ran = false;
                for (const auto& log : logs_) {
                    if (log.tick == t && log.taskName == task.name && log.event == "시작") {
                        ran = true;
                        break;
                    }
                }
                std::cout << (ran ? "█" : "░");
            }
            std::cout << "\n";
        }
    }

    void printTaskInfo() const {
        std::cout << "\n  태스크 정보:\n";
        for (const auto& t : tasks_) {
            std::cout << "    " << t.name << " (우선순위=" << (int)t.priority
                      << ", 주기=" << t.period << "ms, 실행=" << t.runCount << "회)\n";
        }
    }
};

static void lesson2_task_management() {
    printHeader("레슨 2: 태스크 (Task) 관리");

    std::cout << "  C# Thread vs RTOS: RTOS는 높은 우선순위가 반드시 먼저 실행!\n";
    printSubHeader("선점형 스케줄링 시뮬레이션");
    PriorityScheduler scheduler;

    scheduler.addTask("SensorHi", 3, 5, 1, []() {
        // 고우선순위: 센서 읽기 (5ms 주기)
    });
    scheduler.addTask("ProcessMd", 2, 10, 2, []() {
        // 중우선순위: 데이터 처리 (10ms 주기)
    });
    scheduler.addTask("DisplayLo", 1, 20, 3, []() {
        // 저우선순위: 화면 업데이트 (20ms 주기)
    });

    scheduler.runFor(50);
    scheduler.printTaskInfo();
    scheduler.printTimeline(50);

    // 라운드 로빈: 같은 우선순위 태스크가 타임슬라이스만큼 번갈아 실행
    printSubHeader("라운드 로빈 스케줄링");
    std::cout << "  A:████░░░░████░░░░  B:░░░░████░░░░████  (5ms씩 번갈아)\n";
}

// =================================================================
//  레슨 3: 세마포어와 뮤텍스 (RTOS 버전)
// =================================================================
// C# 비유: SemaphoreSlim/Mutex와 비슷하지만 RTOS에서는 "우선순위 역전 방지" 추가!
// 우선순위 역전: 저(L)가 뮤텍스 잡고, 고(H)가 대기 → 중(M)이 먼저 실행되는 문제
// 해결: 우선순위 상속 → L의 우선순위를 일시적으로 H로 올려서 빨리 끝내게 함

// 바이너리 세마포어 (이벤트 통지용)
// "신호등" 같은 것. 빨간불(0)이면 기다리고, 초록불(1)이면 통과!
class BinarySemaphore {
    bool available_;
    std::string name_;

public:
    explicit BinarySemaphore(const std::string& name, bool initial = false)
        : available_(initial), name_(name) {}

    // 세마포어 획득 시도
    bool take(TickType timeout = 0) {
        if (available_) {
            available_ = false;
            std::cout << "    [세마포어:" << name_ << "] 획득 성공 ✓\n";
            return true;
        }
        std::cout << "    [세마포어:" << name_ << "] 획득 실패 (사용중) ✗\n";
        return false;
    }

    // 세마포어 반환 (다른 태스크에게 신호)
    void give() {
        available_ = true;
        std::cout << "    [세마포어:" << name_ << "] 반환 (신호 보냄)\n";
    }

    bool isAvailable() const { return available_; }
};

// 카운팅 세마포어 (리소스 풀 관리)
// "주차장 빈자리 수" 같은 것. 0이면 만석!
class CountingSemaphore {
    int count_;
    int maxCount_;
    std::string name_;

public:
    CountingSemaphore(const std::string& name, int maxCount, int initialCount)
        : count_(initialCount), maxCount_(maxCount), name_(name) {}

    bool take() {
        if (count_ > 0) {
            count_--;
            std::cout << "    [카운팅:" << name_ << "] 획득 (남은:" << count_ << "/" << maxCount_ << ")\n";
            return true;
        }
        std::cout << "    [카운팅:" << name_ << "] 만석! 대기 필요\n";
        return false;
    }

    void give() {
        if (count_ < maxCount_) {
            count_++;
            std::cout << "    [카운팅:" << name_ << "] 반환 (남은:" << count_ << "/" << maxCount_ << ")\n";
        }
    }

    int available() const { return count_; }
};

// 뮤텍스 (우선순위 상속 포함)
// "화장실 열쇠" 같은 것. 열쇠 가진 사람만 쓸 수 있음!
class PriorityMutex {
    bool locked_ = false;
    int ownerPriority_ = -1;       // 원래 소유자 우선순위
    int inheritedPriority_ = -1;   // 상속받은 우선순위
    std::string ownerName_;
    std::string name_;

public:
    explicit PriorityMutex(const std::string& name) : name_(name) {}

    bool lock(const std::string& taskName, int taskPriority) {
        if (!locked_) {
            locked_ = true;
            ownerName_ = taskName;
            ownerPriority_ = taskPriority;
            inheritedPriority_ = taskPriority;
            std::cout << "    [뮤텍스:" << name_ << "] " << taskName << "이 잠금\n";
            return true;
        }

        // 이미 잠겨있고, 요청자가 더 높은 우선순위라면 → 우선순위 상속!
        if (taskPriority > inheritedPriority_) {
            std::cout << "    [뮤텍스:" << name_ << "] 우선순위 상속! "
                      << ownerName_ << "의 우선순위: "
                      << inheritedPriority_ << " → " << taskPriority << "\n";
            inheritedPriority_ = taskPriority;
        }

        std::cout << "    [뮤텍스:" << name_ << "] " << taskName
                  << "이 대기중 (소유자: " << ownerName_ << ")\n";
        return false;
    }

    void unlock(const std::string& taskName) {
        if (locked_ && ownerName_ == taskName) {
            if (inheritedPriority_ != ownerPriority_) {
                std::cout << "    [뮤텍스:" << name_ << "] 우선순위 복원: "
                          << inheritedPriority_ << " → " << ownerPriority_ << "\n";
            }
            locked_ = false;
            ownerName_ = "";
            std::cout << "    [뮤텍스:" << name_ << "] " << taskName << "이 잠금 해제\n";
        }
    }

    bool isLocked() const { return locked_; }
    std::string getOwner() const { return ownerName_; }
};

static void lesson3_semaphore_mutex() {
    printHeader("레슨 3: 세마포어와 뮤텍스 (RTOS 버전)");

    // 바이너리 세마포어 데모
    printSubHeader("바이너리 세마포어 (이벤트 통지)");
    BinarySemaphore dataReady("DataReady", false);

    std::cout << "  [ISR] 데이터 수신 완료!\n";
    dataReady.give();   // ISR이 신호를 보냄

    std::cout << "  [태스크] 데이터 기다리는 중...\n";
    dataReady.take();   // 태스크가 신호를 받음

    std::cout << "  [태스크] 다시 기다려봄...\n";
    dataReady.take();   // 이미 소비됨 → 실패

    // 카운팅 세마포어 (주차장 빈자리 같은 리소스 풀)
    printSubHeader("카운팅 세마포어 (리소스 풀)");
    CountingSemaphore dmaPool("DMA_Buffer", 3, 3);

    dmaPool.take();  // 버퍼1 사용
    dmaPool.take();  // 버퍼2 사용
    dmaPool.take();  // 버퍼3 사용
    dmaPool.take();  // 만석!
    dmaPool.give();  // 버퍼1 반환
    dmaPool.take();  // 다시 사용 가능

    // 뮤텍스 + 우선순위 역전 데모
    printSubHeader("뮤텍스와 우선순위 역전");
    PriorityMutex sharedResource("공유자원");

    std::cout << "\n  [시나리오] 우선순위 역전과 해결:\n\n";

    std::cout << "  1) 저우선순위(L) 태스크가 뮤텍스 획득:\n";
    sharedResource.lock("Low_Task", 1);

    std::cout << "\n  2) 고우선순위(H) 태스크가 뮤텍스 요청 → 대기:\n";
    sharedResource.lock("High_Task", 3);

    std::cout << "\n  3) 저우선순위 태스크가 작업 완료 후 잠금 해제:\n";
    sharedResource.unlock("Low_Task");

    std::cout << "\n  4) 이제 고우선순위 태스크가 획득:\n";
    sharedResource.lock("High_Task", 3);
    sharedResource.unlock("High_Task");
}

// =================================================================
//  레슨 4: 메시지 큐와 이벤트 플래그
// =================================================================
// 메시지 큐: [생산자]→send()→[큐(FIFO)]→recv()→[소비자]
// C# 비유: ConcurrentQueue<T>이지만 RTOS에서는 크기 고정, 가득차면 send()가 블록

// RTOS 메시지 큐
template<typename T, int SIZE>
class MessageQueue {
    T buffer_[SIZE]{};
    int head_ = 0;
    int tail_ = 0;
    int count_ = 0;
    std::string name_;

public:
    explicit MessageQueue(const std::string& name) : name_(name) {}

    bool send(const T& msg) {
        if (count_ >= SIZE) {
            std::cout << "    [큐:" << name_ << "] 가득 참! 전송 실패\n";
            return false;
        }
        buffer_[head_] = msg;
        head_ = (head_ + 1) % SIZE;
        count_++;
        return true;
    }

    bool receive(T& msg) {
        if (count_ == 0) {
            return false;
        }
        msg = buffer_[tail_];
        tail_ = (tail_ + 1) % SIZE;
        count_--;
        return true;
    }

    int available() const { return count_; }
    bool isEmpty() const { return count_ == 0; }
    bool isFull() const { return count_ >= SIZE; }
};

// 이벤트 플래그 그룹
// 여러 이벤트를 비트로 관리. AND/OR 조합으로 대기 가능
class EventGroup {
    uint32_t flags_ = 0;
    std::string name_;

public:
    explicit EventGroup(const std::string& name) : name_(name) {}

    // 이벤트 비트 설정
    void setFlags(uint32_t bits) {
        flags_ |= bits;
        std::cout << "    [이벤트:" << name_ << "] 설정: 0x"
                  << std::hex << flags_ << std::dec << "\n";
    }

    // 이벤트 비트 클리어
    void clearFlags(uint32_t bits) {
        flags_ &= ~bits;
    }

    // AND 대기: 모든 비트가 설정되어야 통과
    bool waitAll(uint32_t bits) const {
        return (flags_ & bits) == bits;
    }

    // OR 대기: 하나라도 설정되면 통과
    bool waitAny(uint32_t bits) const {
        return (flags_ & bits) != 0;
    }

    uint32_t getFlags() const { return flags_; }
};

// 메시지 타입 정의
struct SensorMessage {
    uint8_t sensorId;
    float   value;
    uint32_t timestamp;
};

static void lesson4_queue_events() {
    printHeader("레슨 4: 메시지 큐와 이벤트 플래그");

    std::cout << "  C# 비유: ConcurrentQueue<T>와 ManualResetEventSlim의 RTOS 버전\n";

    // 메시지 큐 데모
    printSubHeader("메시지 큐: 태스크 간 데이터 전달");

    MessageQueue<SensorMessage, 5> sensorQueue("SensorData");

    // 생산자: 센서 데이터 전송
    std::cout << "  [생산자] 센서 데이터 전송:\n";
    SensorMessage msgs[] = {
        {1, 25.3f, 1000},
        {2, 60.5f, 1001},
        {3, 1013.2f, 1002},
        {1, 25.4f, 2000},
        {2, 61.0f, 2001}
    };
    const char* sensorNames[] = {"온도", "습도", "기압", "온도", "습도"};

    for (int i = 0; i < 5; i++) {
        bool ok = sensorQueue.send(msgs[i]);
        std::cout << "    send(" << sensorNames[i] << "=" << msgs[i].value << ") → "
                  << (ok ? "성공" : "실패") << " [큐:" << sensorQueue.available() << "/5]\n";
    }

    // 소비자: 센서 데이터 수신
    std::cout << "\n  [소비자] 센서 데이터 수신:\n";
    SensorMessage received;
    while (sensorQueue.receive(received)) {
        std::cout << "    recv: 센서#" << (int)received.sensorId
                  << " 값=" << received.value
                  << " 시각=" << received.timestamp << "ms\n";
    }

    // 이벤트 플래그 데모
    printSubHeader("이벤트 플래그: 여러 이벤트 AND/OR 대기");

    static constexpr uint32_t EVT_TEMP_READY   = (1 << 0);  // 비트0: 온도 준비
    static constexpr uint32_t EVT_HUMI_READY   = (1 << 1);  // 비트1: 습도 준비
    static constexpr uint32_t EVT_PRES_READY   = (1 << 2);  // 비트2: 기압 준비
    static constexpr uint32_t EVT_ALL_READY    = EVT_TEMP_READY | EVT_HUMI_READY | EVT_PRES_READY;

    EventGroup sensorEvents("SensorReady");

    std::cout << "\n  [온도센서] 데이터 준비 완료!\n";
    sensorEvents.setFlags(EVT_TEMP_READY);
    std::cout << "  AND 대기(모두준비): " << (sensorEvents.waitAll(EVT_ALL_READY) ? "통과" : "대기중...") << "\n";
    std::cout << "  OR 대기(하나라도): " << (sensorEvents.waitAny(EVT_ALL_READY) ? "통과!" : "대기중...") << "\n";

    std::cout << "\n  [습도센서] 데이터 준비 완료!\n";
    sensorEvents.setFlags(EVT_HUMI_READY);

    std::cout << "\n  [기압센서] 데이터 준비 완료!\n";
    sensorEvents.setFlags(EVT_PRES_READY);
    std::cout << "  AND 대기(모두준비): " << (sensorEvents.waitAll(EVT_ALL_READY) ? "통과! 모든 센서 준비됨!" : "대기중...") << "\n";

    // 메일박스 = 크기 1인 큐 (항상 최신 데이터만 유지, 센서 데이터에 적합)
    printSubHeader("메일박스 패턴");

    MessageQueue<float, 1> mailbox("온도Mailbox");
    mailbox.send(25.0f);
    std::cout << "  mailbox에 25.0 저장\n";
    float val;
    mailbox.receive(val);
    std::cout << "  mailbox에서 읽기: " << val << "\n";
}

// =================================================================
//  레슨 5: 타이밍과 데드라인
// =================================================================

// 소프트웨어 타이머
class SoftwareTimer {
public:
    enum class Mode { ONE_SHOT, PERIODIC };

private:
    std::string name_;
    Mode mode_;
    TickType period_;
    TickType nextExpiry_;
    bool active_;
    std::function<void()> callback_;
    uint32_t fireCount_ = 0;

public:
    SoftwareTimer(const std::string& name, Mode mode, TickType period,
                  std::function<void()> callback)
        : name_(name), mode_(mode), period_(period),
          nextExpiry_(0), active_(false), callback_(callback) {}

    void start(TickType currentTick) {
        active_ = true;
        nextExpiry_ = currentTick + period_;
        std::cout << "  [타이머:" << name_ << "] 시작 (주기=" << period_ << "ms, "
                  << (mode_ == Mode::ONE_SHOT ? "일회성" : "반복") << ")\n";
    }

    void stop() {
        active_ = false;
        std::cout << "  [타이머:" << name_ << "] 정지\n";
    }

    // 틱마다 호출하여 만료 확인
    bool process(TickType currentTick) {
        if (!active_) return false;
        if (currentTick >= nextExpiry_) {
            fireCount_++;
            if (callback_) callback_();

            if (mode_ == Mode::PERIODIC) {
                nextExpiry_ = currentTick + period_;
            } else {
                active_ = false;  // one-shot은 한 번만
            }
            return true;
        }
        return false;
    }

    bool isActive() const { return active_; }
    uint32_t getFireCount() const { return fireCount_; }
};

// 데드라인 모니터
struct DeadlineMonitor {
    std::string taskName;
    TickType deadline;         // 데드라인 (ms)
    TickType worstCase = 0;    // 관측된 최악 실행시간
    TickType bestCase = UINT32_MAX;
    uint32_t totalRuns = 0;
    uint32_t missCount = 0;    // 데드라인 미스 횟수
    double totalTime = 0;

    void recordExecution(TickType execTime) {
        totalRuns++;
        totalTime += execTime;
        if (execTime > worstCase) worstCase = execTime;
        if (execTime < bestCase) bestCase = execTime;
        if (execTime > deadline) {
            missCount++;
            std::cout << "    [!] " << taskName << " 데드라인 미스! "
                      << execTime << "ms > " << deadline << "ms\n";
        }
    }

    void printReport() const {
        double avgTime = totalRuns > 0 ? totalTime / totalRuns : 0;
        std::cout << "  " << std::setw(12) << taskName
                  << ": WCET=" << worstCase << "ms"
                  << ", BCET=" << (bestCase == UINT32_MAX ? 0 : bestCase) << "ms"
                  << ", 평균=" << std::fixed << std::setprecision(1) << avgTime << "ms"
                  << ", 데드라인=" << deadline << "ms"
                  << ", 미스=" << missCount << "/" << totalRuns
                  << (missCount == 0 ? " ✓" : " ✗") << "\n";
    }
};

static void lesson5_timing() {
    printHeader("레슨 5: 타이밍과 데드라인");

    // 소프트웨어 타이머 데모
    printSubHeader("소프트웨어 타이머");

    int periodicCount = 0;
    SoftwareTimer periodicTimer("주기타이머", SoftwareTimer::Mode::PERIODIC, 10,
        [&periodicCount]() {
            periodicCount++;
            std::cout << "    [주기타이머] 만료! (#" << periodicCount << ")\n";
        });

    bool oneShotFired = false;
    SoftwareTimer oneShotTimer("일회타이머", SoftwareTimer::Mode::ONE_SHOT, 25,
        [&oneShotFired]() {
            oneShotFired = true;
            std::cout << "    [일회타이머] 만료! (한 번만 실행)\n";
        });

    periodicTimer.start(0);
    oneShotTimer.start(0);

    // 50틱 시뮬레이션
    for (TickType t = 1; t <= 50; t++) {
        periodicTimer.process(t);
        oneShotTimer.process(t);
    }

    std::cout << "  주기 타이머 발생 횟수: " << periodicTimer.getFireCount() << "\n";
    std::cout << "  일회 타이머 발생 여부: " << (oneShotFired ? "예" : "아니오") << "\n";

    // 데드라인 모니터링
    printSubHeader("데드라인 모니터링 (WCET 분석)");
    std::mt19937 rng(42);

    DeadlineMonitor sensorMon{"센서읽기", 5};     // 데드라인 5ms
    DeadlineMonitor processMon{"데이터처리", 15};  // 데드라인 15ms
    DeadlineMonitor displayMon{"화면표시", 50};    // 데드라인 50ms

    // 실행시간 시뮬레이션 (약간의 변동)
    std::normal_distribution<double> sensorDist(3.0, 1.0);
    std::normal_distribution<double> processDist(10.0, 3.0);
    std::normal_distribution<double> displayDist(30.0, 10.0);

    for (int i = 0; i < 100; i++) {
        sensorMon.recordExecution(static_cast<TickType>(std::max(1.0, sensorDist(rng))));
        processMon.recordExecution(static_cast<TickType>(std::max(1.0, processDist(rng))));
        displayMon.recordExecution(static_cast<TickType>(std::max(1.0, displayDist(rng))));
    }

    std::cout << "\n  데드라인 분석 결과 (100회 실행):\n";
    sensorMon.printReport();
    processMon.printReport();
    displayMon.printReport();

    // 지터 = 실행 간격의 흔들림 (이상: 0ms, 현실: ±Nms)
    printSubHeader("지터(Jitter) 측정");

    std::vector<double> intervals;
    std::normal_distribution<double> jitterDist(10.0, 0.5);
    for (int i = 0; i < 20; i++) intervals.push_back(jitterDist(rng));
    double avgInterval = std::accumulate(intervals.begin(), intervals.end(), 0.0) / intervals.size();
    double maxJitter = 0;
    for (double v : intervals) maxJitter = std::max(maxJitter, std::abs(v - avgInterval));
    std::cout << "  목표=10.0ms, 평균=" << std::fixed << std::setprecision(2)
              << avgInterval << "ms, 최대지터=±" << maxJitter << "ms\n";
}

// =================================================================
//  레슨 6: 실전 — 미니 RTOS 시뮬레이터
// =================================================================
// SimpleRTOS: [Sensor(1ms,pri3)]─세마포어→[Process(10ms,pri2)]─큐→[Display(100ms,pri1)]

class SimpleRTOS {
public:
    // 태스크 정보
    struct Task {
        uint32_t id;
        std::string name;
        uint8_t priority;
        TaskState state;
        TickType period;
        TickType nextRun;
        TickType executionTime;   // 실행에 걸리는 시간 (시뮬레이션)
        std::function<void(TickType)> func;
        uint32_t runCount = 0;
    };

private:
    std::vector<Task> tasks_;
    std::vector<SoftwareTimer> timers_;
    TickType currentTick_ = 0;
    bool running_ = false;

    // 스케줄링 이력 (간트 차트용)
    struct RunRecord {
        TickType tick;
        uint32_t taskId;
    };
    std::vector<RunRecord> history_;

public:
    // 태스크 생성 (FreeRTOS의 xTaskCreate에 해당)
    uint32_t createTask(const std::string& name, uint8_t priority,
                        TickType period, TickType execTime,
                        std::function<void(TickType)> func) {
        Task t;
        t.id = static_cast<uint32_t>(tasks_.size());
        t.name = name;
        t.priority = priority;
        t.state = TaskState::READY;
        t.period = period;
        t.nextRun = 0;
        t.executionTime = execTime;
        t.func = func;
        tasks_.push_back(t);
        std::cout << "  [RTOS] 태스크 생성: " << name
                  << " (우선순위=" << (int)priority
                  << ", 주기=" << period << "ms)\n";
        return t.id;
    }

    // 스케줄러 실행
    void run(TickType totalTicks) {
        running_ = true;
        std::cout << "\n  [RTOS] 스케줄러 시작! (" << totalTicks << "ms 시뮬레이션)\n";

        for (currentTick_ = 0; currentTick_ < totalTicks && running_; currentTick_++) {
            // 타이머 처리
            for (auto& timer : timers_) {
                timer.process(currentTick_);
            }

            // 주기 도달한 태스크를 Ready로
            for (auto& t : tasks_) {
                if (t.state == TaskState::BLOCKED && currentTick_ >= t.nextRun) {
                    t.state = TaskState::READY;
                }
            }

            // 가장 높은 우선순위의 Ready 태스크 선택
            Task* best = nullptr;
            for (auto& t : tasks_) {
                if (t.state == TaskState::READY) {
                    if (!best || t.priority > best->priority) {
                        best = &t;
                    }
                }
            }

            if (best) {
                best->state = TaskState::RUNNING;
                best->runCount++;

                // 태스크 실행
                if (best->func) {
                    best->func(currentTick_);
                }

                history_.push_back({currentTick_, best->id});

                // 완료 → Blocked (다음 주기까지)
                best->state = TaskState::BLOCKED;
                best->nextRun = currentTick_ + best->period;
            }
        }

        std::cout << "  [RTOS] 스케줄러 종료 (총 " << currentTick_ << "ms)\n";
    }

    // 간트 차트 출력 (처음 50ms)
    void printGanttChart(TickType start = 0, TickType end = 50) const {
        std::cout << "\n  간트 차트 (" << start << "~" << end << "ms):\n";
        for (const auto& task : tasks_) {
            std::cout << "  " << std::setw(9) << std::right << task.name << ": ";
            for (TickType t = start; t < end; t++) {
                bool ran = false;
                for (const auto& rec : history_) {
                    if (rec.tick == t && rec.taskId == task.id) { ran = true; break; }
                }
                std::cout << (ran ? "█" : "·");
            }
            std::cout << " (" << task.runCount << "회)\n";
        }
    }

    void printStats() const {
        std::cout << "\n  태스크 실행 통계:\n";
        for (const auto& t : tasks_) {
            std::cout << "    " << t.name << ": 우선순위=" << (int)t.priority
                      << ", 주기=" << t.period << "ms, 실행=" << t.runCount << "회\n";
        }
    }
};

static void lesson6_mini_rtos() {
    printHeader("레슨 6: 실전 — 미니 RTOS 시뮬레이터");

    SimpleRTOS rtos;

    // 공유 데이터 (센서 → 처리 → 디스플레이)
    struct SharedData {
        float sensorValue = 0.0f;
        float processedValue = 0.0f;
        bool sensorReady = false;
        bool processedReady = false;
        int sensorReadCount = 0;
        int processCount = 0;
        int displayCount = 0;
    };
    SharedData shared;

    BinarySemaphore sensorSem("SensorDone", false);
    MessageQueue<float, 10> displayQueue("DisplayQ");

    std::cout << "  구성: Sensor(1ms,pri3) / Process(10ms,pri2) / Display(100ms,pri1)\n\n";

    // 태스크 1: 센서 읽기 (고우선순위, 1ms 주기)
    rtos.createTask("Sensor", 3, 1, 1,
        [&shared, &sensorSem](TickType tick) {
            // 센서에서 온도 읽기 시뮬레이션
            std::mt19937 rng(tick);
            std::normal_distribution<float> noise(0.0f, 0.1f);
            shared.sensorValue = 25.0f + noise(rng);
            shared.sensorReady = true;
            shared.sensorReadCount++;
        });

    // 태스크 2: 데이터 처리 (중우선순위, 10ms 주기)
    rtos.createTask("Process", 2, 10, 2,
        [&shared, &displayQueue](TickType tick) {
            if (shared.sensorReady) {
                // 간단한 필터링 (이동평균 흉내)
                static float filtered = 25.0f;
                filtered = 0.8f * filtered + 0.2f * shared.sensorValue;
                shared.processedValue = filtered;
                shared.processedReady = true;
                shared.processCount++;

                // 디스플레이 큐로 전송
                displayQueue.send(filtered);
            }
        });

    // 태스크 3: 디스플레이 업데이트 (저우선순위, 100ms 주기)
    rtos.createTask("Display", 1, 100, 5,
        [&shared, &displayQueue](TickType tick) {
            float val;
            if (displayQueue.receive(val)) {
                shared.displayCount++;
                if (shared.displayCount <= 5) {  // 처음 5번만 출력
                    std::cout << "    [Display@" << tick << "ms] 온도: "
                              << std::fixed << std::setprecision(1) << val << "°C\n";
                }
            }
        });

    // 500ms 시뮬레이션 실행
    rtos.run(500);

    // 결과 출력
    rtos.printStats();
    rtos.printGanttChart(0, 50);  // 처음 50ms만 표시

    // 실행 결과 요약
    printSubHeader("시뮬레이션 결과 요약");
    std::cout << "  센서 읽기 횟수: " << shared.sensorReadCount << "회\n";
    std::cout << "  데이터 처리 횟수: " << shared.processCount << "회\n";
    std::cout << "  디스플레이 갱신 횟수: " << shared.displayCount << "회\n";
    std::cout << "  최종 센서값: " << std::fixed << std::setprecision(2)
              << shared.sensorValue << "°C\n";
    std::cout << "  최종 필터값: " << shared.processedValue << "°C\n";

    std::cout << "\n  데이터 흐름: Sensor(1ms)→shared→Process(10ms)→큐→Display(100ms)\n";
}

// =================================================================
//  메인 함수
// =================================================================
int main() {
    std::cout << R"(
 ╔═══════════════════════════════════════════════════════════════╗
 ║  C++ 임베디드 학습 #32: RTOS 패턴과 실시간 시스템            ║
 ║  TaskA(1ms) / TaskB(10ms) / TaskC(100ms) → RTOS 스케줄러    ║
 ║  C# 비유: Task.Run()="언젠가" vs RTOS="반드시 정해진 시간에" ║
 ╚═══════════════════════════════════════════════════════════════╝
)";

    /*
    =========================================================================
      레슨별 출력 흐름 가이드
    =========================================================================
      lesson1 (RTOS 개념):
        선점형 스케줄링 vs 협력적
        Hard real-time vs Soft real-time
        예: 자율주행 ABS = hard (놓치면 사고)
            화상회의 = soft (1프레임 놓쳐도 OK)

      lesson2 (Task 관리):
        Task A 우선순위 1, period 1ms
        Task B 우선순위 2, period 10ms
        Task C 우선순위 3, period 100ms
        스케줄러 시뮬레이션 → Gantt 차트 출력

      lesson3 (세마포어/뮤텍스):
        Binary semaphore: 0/1로 자원 보호
        Counting semaphore: 풀 자원 (예: 3개 슬롯)
        Mutex with priority inheritance: 우선순위 역전 방지
        예: 낮은 task가 락 보유 → 높은 task 깨어남 → 낮은 task 임시 승격

      lesson4 (메시지 큐):
        producer task가 enqueue
        consumer task가 dequeue (block 가능)
        고정 크기 메모리 풀 + atomic head/tail

      lesson5 (Timing):
        Deadline 분석: WCET (Worst-Case Execution Time)
        Rate Monotonic Scheduling 유틸리티 검사
        utilization = sum(WCET/period) ≤ ln(2) ≈ 0.693 (n개 task)

      lesson6 (Mini RTOS):
        간단한 협력적 스케줄러 직접 구현
        task 등록 → 라운드로빈 → context switch 시뮬

      ※ 이 챕터는 RTOS 시뮬레이션. 실제 STM32CubeIDE + FreeRTOS와
        유사한 코드 구조. 실제 보드 없이 개념 학습 목적.
    =========================================================================
    */
    lesson1_rtos_concepts();
    lesson2_task_management();
    lesson3_semaphore_mutex();
    lesson4_queue_events();
    lesson5_timing();
    lesson6_mini_rtos();

    std::cout << "\n================================================================\n";
    std::cout << "  학습 완료! 핵심: RTOS=데드라인 보장 OS, 선점형 스케줄링,\n";
    std::cout << "  세마포어/뮤텍스(우선순위역전방지), 메시지큐, WCET 분석\n";
    std::cout << "================================================================\n";

    return 0;
}
