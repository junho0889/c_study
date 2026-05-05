/*
 * =============================================================================
 *  C++ 학습 30단계: 하드웨어 레벨 제어
 *  (Hardware-Level Control: DMA, Interrupts, MMIO, GPIO, Watchdog, Timer)
 * =============================================================================
 *
 *  왜 C++이 임베디드/시스템/드라이버 프로그래밍의 왕인가?
 *  → C++은 하드웨어를 "직접" 만질 수 있는 거의 유일한 고급 언어입니다.
 *  → C#은 OS가 중간에서 통역해주지만, C++은 하드웨어와 직접 대화합니다.
 *
 *  초등학생 비유:
 *  ┌──────────────────────────────────────────────────┐
 *  │  C#  = 리모컨으로 TV 조작 (OS가 중간에서 전달)   │
 *  │  C++ = TV 뚜껑 열고 회로판에 직접 납땜            │
 *  └──────────────────────────────────────────────────┘
 *
 *  ┌─────────────────────────────────────────────────────────┐
 *  │              MCU (마이크로컨트롤러) 블록 다이어그램      │
 *  │  ┌───────┐  ┌──────┐  ┌──────┐  ┌──────────┐          │
 *  │  │  CPU  │  │ SRAM │  │Flash │  │   DMA    │          │
 *  │  └───┬───┘  └──┬───┘  └──┬───┘  └────┬─────┘          │
 *  │      └─────────┴─────────┴────────────┤                │
 *  │              AHB / APB 시스템 버스     │                │
 *  │      ┌──────┬───────┬────────┬────────┘                │
 *  │  ┌───┴──┐┌──┴──┐┌───┴──┐┌───┴───┐┌─────┐             │
 *  │  │ NVIC ││GPIO ││Timer ││ UART  ││ SPI │             │
 *  │  └──────┘└─────┘└──────┘└───────┘└─────┘             │
 *  └─────────────────────────────────────────────────────────┘
 *
 *  컴파일: g++ -std=c++17 main.cpp -o main
 */

#include <iostream>
#include <cstdint>
#include <cstring>
#include <vector>
#include <functional>
#include <string>
#include <iomanip>
#include <chrono>
#include <queue>
#include <bitset>
#include <sstream>
#include <algorithm>
#include <numeric>

void printHeader(const std::string& t) {
    std::cout << "\n================================================================\n"
              << "  " << t << "\n"
              << "================================================================\n";
}
void printSub(const std::string& t) { std::cout << "\n--- " << t << " ---\n"; }

// =============================================================================
// 레슨 1: 메모리 매핑 I/O (MMIO)
// =============================================================================
/*
 *  MMIO란? 하드웨어 장치가 메모리 주소에 연결되어 있어서,
 *  특정 주소에 값을 쓰면 → 하드웨어가 동작!
 *  특정 주소에서 읽으면 → 하드웨어 상태 확인!
 *
 *  ┌──────────────┬───────────────────────────┐
 *  │ 메모리 주소  │ 연결된 하드웨어           │
 *  ├──────────────┼───────────────────────────┤
 *  │ 0x0000_0000  │ Flash (프로그램 코드)     │
 *  │ 0x2000_0000  │ SRAM  (변수, 스택)       │
 *  │ 0x4000_0000  │ GPIO 포트 A 레지스터     │
 *  │ 0x4001_0000  │ UART1 레지스터           │
 *  │ 0x4002_0000  │ DMA 컨트롤러             │
 *  │ 0xE000_E000  │ NVIC (인터럽트 컨트롤러) │
 *  └──────────────┴───────────────────────────┘
 *
 *  C# 비유: "C#의 Marshal.ReadInt32(IntPtr)와 비슷하지만,
 *           C++은 포인터로 직접 접근합니다"
 *  C#:  int val = Marshal.ReadInt32(new IntPtr(0x40000000));
 *  C++: volatile uint32_t* reg = (volatile uint32_t*)0x40000000;
 *       uint32_t val = *reg;   // 그냥 읽으면 됨!
 *
 *  volatile = "이 변수는 내가 안 바꿔도 값이 변할 수 있어!" (하드웨어가 바꿈)
 */
namespace Lesson1_MMIO {

    // 가상 레지스터 공간 (실제로는 하드웨어에 연결된 주소)
    static volatile uint32_t g_regs[64] = {0};

    // 레지스터 오프셋 (데이터시트에 정의됨)
    constexpr uint32_t LED_CTRL = 0x00, LED_STATUS = 0x04, LED_BRIGHT = 0x08;
    constexpr uint32_t SENSOR_DATA = 0x10, SENSOR_CFG = 0x14;

    // 비트 정의
    constexpr uint32_t LED0 = (1<<0), LED1 = (1<<1), LED2 = (1<<2), LED3 = (1<<3);
    constexpr uint32_t LED_BLINK = (1<<4), LED_ENABLE = (1<<7);

    // MMIO 접근 함수 (실제 드라이버 패턴)
    void regWrite(uint32_t off, uint32_t val) { g_regs[off/4] = val; }
    uint32_t regRead(uint32_t off) { return g_regs[off/4]; }
    void regSet(uint32_t off, uint32_t bits) { g_regs[off/4] |= bits; }
    void regClear(uint32_t off, uint32_t bits) { g_regs[off/4] &= ~bits; }
    bool regBit(uint32_t off, uint32_t bit) { return (regRead(off) & bit) != 0; }

    // 레지스터 맵 구조체 (비트필드 + #pragma pack)
    #pragma pack(push, 1)
    struct LedRegMap {
        struct {
            uint32_t led0:1, led1:1, led2:1, led3:1;   // 비트 0~3
            uint32_t blink:1, _rsvd:2, enable:1;        // 비트 4~7
            uint32_t _pad:24;
        } ctrl;
        uint32_t status;
        uint32_t brightness;
    };
    #pragma pack(pop)

    void demo() {
        printHeader("레슨 1: 메모리 매핑 I/O (MMIO)");
        std::cout << "[개념] MMIO = 메모리 주소로 하드웨어를 제어\n"
                  << "→ C#에서는 Marshal.ReadInt32(), C++에서는 포인터 직접 접근\n";

        printSub("예제 1: LED 레지스터 직접 제어");
        regWrite(LED_CTRL, 0x00);
        regSet(LED_CTRL, LED_ENABLE);
        std::cout << "LED 활성화 후: 0x" << std::hex << std::setw(8)
                  << std::setfill('0') << regRead(LED_CTRL) << std::dec << "\n";
        regSet(LED_CTRL, LED0 | LED2);
        std::cout << "LED0,2 켜기:  0x" << std::hex << std::setw(8)
                  << std::setfill('0') << regRead(LED_CTRL) << std::dec << "\n";
        std::cout << "LED0=" << (regBit(LED_CTRL,LED0)?"켜짐":"꺼짐")
                  << " LED1=" << (regBit(LED_CTRL,LED1)?"켜짐":"꺼짐") << "\n";
        regClear(LED_CTRL, LED0);
        std::cout << "비트 표현: " << std::bitset<8>(regRead(LED_CTRL) & 0xFF) << "\n";

        printSub("예제 2: 레지스터 맵 구조체 (비트필드)");
        LedRegMap led = {};
        led.ctrl.enable = 1; led.ctrl.led0 = 1; led.ctrl.led3 = 1;
        led.ctrl.blink = 1; led.brightness = 128;
        std::cout << "LED0:" << led.ctrl.led0 << " LED3:" << led.ctrl.led3
                  << " 깜빡임:" << led.ctrl.blink << " 밝기:" << led.brightness << "/255\n";

        printSub("예제 3: 센서 데이터 (volatile 중요성)");
        regWrite(SENSOR_DATA, 2350);
        std::cout << "센서: " << regRead(SENSOR_DATA) << " → "
                  << regRead(SENSOR_DATA)/100.0f << "°C\n"
                  << "※ volatile 없으면 컴파일러가 읽기를 생략할 수 있음!\n";
    }
}

// =============================================================================
// 레슨 2: 인터럽트 (Interrupts)
// =============================================================================
/*
 *  인터럽트 = 하드웨어가 CPU에게 "지금 하던 일 멈추고 나 좀 봐줘!"
 *
 *  비유: 수업 중 화재 경보 → 하던 일 멈추고 대피 → 해제되면 수업 계속
 *
 *  ┌─────────────────────────────────────────────┐
 *  │         인터럽트 처리 흐름도                 │
 *  │  메인 프로그램 실행 중...                    │
 *  │       │  ← 인터럽트 발생! (하드웨어 신호)   │
 *  │       ▼                                      │
 *  │  1. 현재 상태 저장 (레지스터, PC)            │
 *  │  2. 벡터 테이블에서 ISR 주소 찾기            │
 *  │  3. ISR 실행 (인터럽트 서비스 루틴)          │
 *  │  4. 상태 복원                                │
 *  │       ▼                                      │
 *  │  메인 프로그램 계속 실행...                   │
 *  └─────────────────────────────────────────────┘
 *
 *  C# 비유: "C#의 event가 OS 수준에서 하드웨어가 발생시키는 것입니다"
 *  C#:  button.Click += handler;    // OS가 이벤트 전달
 *  C++: void EXTI0_IRQHandler() {}  // 하드웨어가 직접 호출!
 */
namespace Lesson2_Interrupts {

    enum class IRQn : int {
        TIMER0=0, TIMER1=1, EXTI0=2, EXTI1=3,
        UART_RX=4, DMA_TC=5, ADC=6, MAX_IRQ=16
    };
    using ISR_Handler = std::function<void()>;

    // NVIC (Nested Vectored Interrupt Controller) 시뮬레이션
    class NVIC {
    public:
        static constexpr int N = 16;
        NVIC() : glob_(true) {
            for (int i=0;i<N;i++) { en_[i]=false; pend_[i]=false; pri_[i]=15; h_[i]=nullptr; }
        }
        void setHandler(IRQn q, ISR_Handler h) { h_[id(q)] = h; }
        void enable(IRQn q) { en_[id(q)] = true; }
        void disable(IRQn q) { en_[id(q)] = false; }
        void setPriority(IRQn q, int p) { pri_[id(q)] = p; }
        void disableAll() { glob_=false; std::cout << "  [NVIC] 전역 인터럽트 비활성화\n"; }
        void enableAll() { glob_=true; std::cout << "  [NVIC] 전역 인터럽트 활성화\n"; }

        void trigger(IRQn q) {
            int i = id(q);
            if (!glob_) { pend_[i]=true; std::cout<<"  [NVIC] IRQ "<<i<<" 보류됨\n"; return; }
            if (!en_[i]) { std::cout<<"  [NVIC] IRQ "<<i<<" 무시 (비활성)\n"; return; }
            if (h_[i]) {
                std::cout<<"  [NVIC] >>> IRQ "<<i<<" (우선순위:"<<pri_[i]<<") → ISR 실행\n";
                h_[i]();
                std::cout<<"  [NVIC] <<< IRQ "<<i<<" ISR 완료\n";
            }
        }

        void processPending() {
            if (!glob_) return;
            std::vector<int> pl;
            for (int i=0;i<N;i++) if (pend_[i]&&en_[i]) pl.push_back(i);
            std::sort(pl.begin(),pl.end(),[this](int a,int b){return pri_[a]<pri_[b];});
            for (int i:pl) { pend_[i]=false; if(h_[i]){std::cout<<"  [NVIC] 보류 IRQ "<<i<<" 처리\n";h_[i]();}}
        }
    private:
        int id(IRQn q){return static_cast<int>(q);}
        bool en_[N], pend_[N], glob_;
        int pri_[N];
        ISR_Handler h_[N];
    };

    static NVIC g_nvic;
    static volatile uint32_t g_ticks = 0;
    static volatile bool g_btnPressed = false;
    static volatile uint8_t g_rxData = 0;

    void demo() {
        printHeader("레슨 2: 인터럽트 (Interrupts)");
        std::cout << "[개념] 인터럽트 = 하드웨어의 긴급 신호 → ISR 실행\n";

        g_nvic.setHandler(IRQn::TIMER0, [](){ g_ticks++; std::cout<<"    [ISR] Timer tick="<<g_ticks<<"\n"; });
        g_nvic.setHandler(IRQn::EXTI0, [](){ g_btnPressed=true; std::cout<<"    [ISR] 버튼 눌림!\n"; });
        g_nvic.setHandler(IRQn::UART_RX, [](){ g_rxData='A'; std::cout<<"    [ISR] UART 수신='"<<(char)g_rxData<<"'\n"; });

        g_nvic.setPriority(IRQn::TIMER0, 2);
        g_nvic.setPriority(IRQn::EXTI0, 1);
        g_nvic.setPriority(IRQn::UART_RX, 3);
        g_nvic.enable(IRQn::TIMER0); g_nvic.enable(IRQn::EXTI0); g_nvic.enable(IRQn::UART_RX);

        printSub("예제 1: 인터럽트 발생");
        std::cout << "메인 실행 중...\n"; g_nvic.trigger(IRQn::TIMER0);
        std::cout << "메인 계속...\n";    g_nvic.trigger(IRQn::EXTI0);

        printSub("예제 2: 비활성화된 인터럽트");
        g_nvic.disable(IRQn::UART_RX);
        g_nvic.trigger(IRQn::UART_RX);  // 무시!
        g_nvic.enable(IRQn::UART_RX);

        printSub("예제 3: 크리티컬 섹션");
        g_nvic.disableAll();
        g_nvic.trigger(IRQn::TIMER0);   // 보류
        g_nvic.trigger(IRQn::UART_RX);  // 보류
        g_nvic.enableAll();
        g_nvic.processPending();         // 우선순위 순 처리
    }
}

// =============================================================================
// 레슨 3: DMA (Direct Memory Access)
// =============================================================================
/*
 *  DMA = CPU 개입 없이 메모리↔장치 직접 전송
 *  비유: 사장님(CPU)이 직접 택배 옮기기 vs 택배기사(DMA)에게 맡기기
 *
 *  ┌─────────────────────────────────────────┐
 *  │ [CPU 복사]  소스→ CPU →목적지 (바쁨!)   │
 *  │ [DMA 전송]  소스 ──DMA──→ 목적지        │
 *  │             (CPU는 자유! 다른 일 가능)   │
 *  │                                          │
 *  │ [핑퐁 모드]                              │
 *  │  버퍼A→DMA전송 (CPU는 버퍼B 처리)       │
 *  │  버퍼B→DMA전송 (CPU는 버퍼A 처리)       │
 *  └─────────────────────────────────────────┘
 *
 *  C# 비유: "Buffer.BlockCopy()를 CPU가 아닌 별도 하드웨어가 해주는 것"
 */
namespace Lesson3_DMA {

    enum class DmaMode { SINGLE, BLOCK, PING_PONG };

    struct DmaConfig {
        const void* src; void* dst; uint32_t size;
        DmaMode mode; std::function<void()> onComplete;
    };

    class DmaController {
    public:
        void configure(int ch, const DmaConfig& cfg) {
            cfgs_[ch] = cfg;
            std::cout << "  [DMA] 채널" << ch << " 설정 (" << cfg.size << "B)\n";
        }
        void start(int ch) {
            auto& c = cfgs_[ch];
            std::cout << "  [DMA] 채널" << ch << " 전송 시작\n";
            switch (c.mode) {
                case DmaMode::SINGLE: {
                    auto s=(const uint8_t*)c.src; auto d=(uint8_t*)c.dst;
                    for(uint32_t i=0;i<c.size;i++) d[i]=s[i];
                    std::cout << "  [DMA] 단일 모드: " << c.size << "B 완료\n"; break;
                }
                case DmaMode::BLOCK:
                    std::memcpy(c.dst, c.src, c.size);
                    std::cout << "  [DMA] 블록 모드: " << c.size << "B 완료\n"; break;
                case DmaMode::PING_PONG: {
                    uint32_t half = c.size/2;
                    std::memcpy(c.dst, c.src, half);
                    std::cout << "  [DMA] 핑퐁: 버퍼A " << half << "B (CPU는 버퍼B 처리 가능)\n";
                    std::memcpy((uint8_t*)c.dst+half, (const uint8_t*)c.src+half, c.size-half);
                    std::cout << "  [DMA] 핑퐁: 버퍼B " << (c.size-half) << "B 완료\n"; break;
                }
            }
            if (c.onComplete) { std::cout << "  [DMA] 완료 인터럽트!\n"; c.onComplete(); }
        }
    private:
        DmaConfig cfgs_[8];
    };

    void demo() {
        printHeader("레슨 3: DMA (Direct Memory Access)");
        std::cout << "[개념] DMA = CPU 대신 데이터 옮겨주는 택배기사\n";

        DmaController dma;

        printSub("예제 1: 블록 전송");
        uint8_t src[64], dst[64]={};
        for(int i=0;i<64;i++) src[i]=(uint8_t)i;
        dma.configure(0, {src, dst, 64, DmaMode::BLOCK, [](){ std::cout<<"    전송 완료 콜백!\n"; }});
        dma.start(0);
        std::cout << "  검증: " << (memcmp(src,dst,64)==0?"성공":"실패") << "\n";

        printSub("예제 2: 핑퐁 전송");
        uint16_t sens[100], buf[100]={};
        for(int i=0;i<100;i++) sens[i]=(uint16_t)(i*10);
        dma.configure(1, {sens, buf, sizeof(sens), DmaMode::PING_PONG, nullptr});
        dma.start(1);

        printSub("예제 3: CPU복사 vs DMA 성능 비교");
        constexpr size_t SZ = 1000000;
        std::vector<uint8_t> bs(SZ), bd(SZ);
        std::iota(bs.begin(), bs.end(), 0);
        auto t0 = std::chrono::high_resolution_clock::now();
        for(size_t i=0;i<SZ;i++) bd[i]=bs[i];
        auto cpu_us = std::chrono::duration_cast<std::chrono::microseconds>(
            std::chrono::high_resolution_clock::now()-t0).count();
        std::fill(bd.begin(),bd.end(),0);
        t0 = std::chrono::high_resolution_clock::now();
        std::memcpy(bd.data(), bs.data(), SZ);
        auto dma_us = std::chrono::duration_cast<std::chrono::microseconds>(
            std::chrono::high_resolution_clock::now()-t0).count();
        std::cout << "  CPU 복사: " << cpu_us << " us\n"
                  << "  DMA 복사: " << dma_us << " us\n"
                  << "  (실제 DMA는 CPU 개입 없이 하드웨어가 수행!)\n";
    }
}

// =============================================================================
// 레슨 4: GPIO (General Purpose I/O)
// =============================================================================
/*
 *  GPIO = MCU 핀으로 전기를 내보내거나(출력) 받는(입력) 것
 *
 *  ┌─────────────────────────────────────────────┐
 *  │ [출력] MCU핀 ──→ LED ──→ GND               │
 *  │   레지스터=1이면 전류 흐름 → LED 켜짐       │
 *  │                                              │
 *  │ [입력+풀업]                                  │
 *  │   3.3V──[풀업저항]──┬──MCU핀                │
 *  │                      [버튼]                  │
 *  │                      GND                     │
 *  │   버튼 안 누름→HIGH, 누름→LOW               │
 *  └─────────────────────────────────────────────┘
 *
 *  C# 비유: "System.Device.Gpio의 GpioPin과 같은 개념"
 */
namespace Lesson4_GPIO {

    enum class PinMode { INPUT, OUTPUT, INPUT_PULLUP, INPUT_PULLDOWN, ALTERNATE, ANALOG };
    enum class PinState { LOW=0, HIGH=1 };

    class GpioPort {
    public:
        static constexpr int N = 16;
        explicit GpioPort(const std::string& name) : name_(name) {
            for(int i=0;i<N;i++){modes_[i]=PinMode::INPUT; states_[i]=PinState::LOW;}
        }
        void pinMode(int p, PinMode m) {
            if(p<0||p>=N) return;
            modes_[p]=m;
            const char* ms[]={"입력","출력","입력(풀업)","입력(풀다운)","대체기능","아날로그"};
            std::cout << "  [" << name_ << "] 핀" << p << " → " << ms[(int)m] << "\n";
        }
        void digitalWrite(int p, PinState s) {
            if(p<0||p>=N||modes_[p]!=PinMode::OUTPUT) return;
            states_[p]=s;
        }
        void digitalToggle(int p) {
            if(p<0||p>=N) return;
            states_[p] = states_[p]==PinState::HIGH ? PinState::LOW : PinState::HIGH;
        }
        PinState digitalRead(int p) { return (p>=0&&p<N)?states_[p]:PinState::LOW; }
        void simulateInput(int p, PinState s) { if(p>=0&&p<N) states_[p]=s; }
        void printStatus() const {
            std::cout << "  [" << name_ << "] ";
            for(int i=N-1;i>=0;i--){ std::cout<<(int)states_[i]; if(i%4==0&&i>0) std::cout<<"_"; }
            std::cout << "\n";
        }
        const std::string& getName() const { return name_; }
    private:
        std::string name_;
        PinMode modes_[N]; PinState states_[N];
    };

    /*
     *  PWM (Pulse Width Modulation) = 빠르게 껐다켰다 해서 밝기 조절
     *  듀티100%: ################  (항상 켜짐)
     *  듀티 50%: ########________  (반반)
     *  듀티  0%: ________________  (항상 꺼짐)
     */
    class PwmChannel {
    public:
        PwmChannel(int freq, int maxD=100) : freq_(freq), max_(maxD), duty_(0) {}
        void setDuty(int d) { duty_ = std::clamp(d, 0, max_); }
        void visualize(const std::string& label) const {
            int on = 32*duty_/max_;
            std::cout << "  " << label << " (듀티:" << std::setw(3) << duty_ << "%): ";
            for(int i=0;i<32;i++) std::cout<<(i<on?'#':'_');
            std::cout << "\n";
        }
    private:
        int freq_, max_, duty_;
    };

    // 디바운싱: 버튼 떨림 제거
    // 실제: ──┐┌┐┌┐┌────  (바운싱) → 디바운싱 후: ──┐└──── (깔끔)
    class DebouncedButton {
    public:
        DebouncedButton(GpioPort& port, int pin, int ms=50)
            : port_(port), pin_(pin), debMs_(ms), last_(PinState::HIGH),
              stable_(PinState::HIGH), lastT_(0), t_(0) {}
        bool isPressed() {
            t_ += 10;
            PinState r = port_.digitalRead(pin_);
            if (r != last_) lastT_ = t_;
            if ((t_ - lastT_) > debMs_ && r != stable_) {
                stable_ = r;
                if (stable_ == PinState::LOW) { last_=r; return true; }
            }
            last_ = r; return false;
        }
    private:
        GpioPort& port_; int pin_, debMs_;
        PinState last_, stable_; int lastT_, t_;
    };

    void demo() {
        printHeader("레슨 4: GPIO (General Purpose I/O)");

        printSub("예제 1: LED 제어");
        GpioPort pa("GPIOA");
        for(int i=0;i<4;i++) pa.pinMode(i, PinMode::OUTPUT);
        for(int cycle=0;cycle<3;cycle++){
            for(int p=0;p<4;p++) pa.digitalWrite(p, PinState::HIGH);
            std::cout << "  [" << cycle << "] 켜짐: "; pa.printStatus();
            for(int p=0;p<4;p++) pa.digitalWrite(p, PinState::LOW);
            std::cout << "  [" << cycle << "] 꺼짐: "; pa.printStatus();
        }

        printSub("예제 2: 버튼 (디바운싱)");
        GpioPort pb("GPIOB"); pb.pinMode(0, PinMode::INPUT_PULLUP);
        DebouncedButton btn(pb, 0);
        PinState seq[] = {PinState::HIGH,PinState::LOW,PinState::HIGH,
                          PinState::LOW,PinState::LOW,PinState::LOW,
                          PinState::LOW,PinState::LOW,PinState::LOW};
        for(auto s : seq) { pb.simulateInput(0,s); if(btn.isPressed()) std::cout<<"  → 버튼 눌림 감지!\n"; }

        printSub("예제 3: PWM (밝기 제어)");
        PwmChannel led(1000);
        for(int d : {0, 25, 50, 75, 100}) { led.setDuty(d); led.visualize("LED"); }
        std::cout << "\n  서보 모터 (50Hz):\n";
        PwmChannel servo(50, 180);
        for(int a : {0, 45, 90, 135, 180}) { servo.setDuty(a); servo.visualize(std::to_string(a)+"도"); }
    }
}

// =============================================================================
// 레슨 5: 타이머와 워치독 (Timer & Watchdog)
// =============================================================================
/*
 *  타이머 = 하드웨어가 자동으로 세는 카운터 (째깍째깍)
 *  → 목표 숫자 도달 → 인터럽트 발생!
 *
 *  워치독 = 강아지에게 밥을 줘야 함
 *  → 일정 시간 안에 안 주면 → 시스템 리셋!
 *  → 프로그램이 멈추면 자동으로 재시작하는 안전장치
 *
 *  C# 비유: "System.Timers.Timer와 비슷하지만, 하드웨어가 직접 카운트"
 */
namespace Lesson5_TimerWatchdog {

    class HardwareTimer {
    public:
        HardwareTimer(const std::string& name, uint32_t clk=72000000)
            : name_(name), clk_(clk), psc_(0), arr_(0), cnt_(0), on_(false) {}
        void setPrescaler(uint32_t p) {
            psc_=p;
            std::cout << "  [" << name_ << "] PSC=" << p << " → " << clk_/(p+1) << "Hz\n";
        }
        void setAutoReload(uint32_t a) {
            arr_=a;
            std::cout << "  [" << name_ << "] ARR=" << a << " → "
                      << std::fixed << std::setprecision(2)
                      << 1000.0*(a+1)/(clk_/(psc_+1)) << "ms\n";
        }
        void setCallback(std::function<void()> cb) { cb_=cb; }
        void start() { on_=true; cnt_=0; std::cout<<"  ["<<name_<<"] 시작\n"; }
        void stop() { on_=false; std::cout<<"  ["<<name_<<"] 정지\n"; }
        void tick() {
            if(!on_) return;
            if(++cnt_ > arr_) { cnt_=0; if(cb_) cb_(); }
        }
    private:
        std::string name_; uint32_t clk_,psc_,arr_,cnt_; bool on_;
        std::function<void()> cb_;
    };

    class WatchdogTimer {
    public:
        WatchdogTimer(uint32_t timeout) : timeout_(timeout), cnt_(0), on_(false), reset_(false) {}
        void start() { on_=true; cnt_=0; std::cout<<"  [WDT] 시작 (타임아웃:"<<timeout_<<"틱)\n"; }
        void feed() { if(on_){cnt_=0; std::cout<<"  [WDT] 먹이 줌!\n";} }
        bool tick() {
            if(!on_||reset_) return false;
            if(++cnt_>=timeout_){ reset_=true; std::cout<<"  [WDT] *** 시스템 리셋!!! ***\n"; return true; }
            return false;
        }
        bool isReset() const { return reset_; }
    private:
        uint32_t timeout_, cnt_; bool on_, reset_;
    };

    void demo() {
        printHeader("레슨 5: 타이머와 워치독 (Timer & Watchdog)");

        printSub("예제 1: 타이머 인터럽트");
        HardwareTimer t1("TIM1");
        t1.setPrescaler(71);    // 72MHz/72 = 1MHz
        t1.setAutoReload(999);  // 1MHz/1000 = 1ms
        int cnt=0;
        t1.setCallback([&cnt](){ cnt++; std::cout<<"    [TIM1 ISR] 1ms! (횟수:"<<cnt<<")\n"; });
        t1.start();
        for(int i=0;i<3000;i++) t1.tick();  // 3번 인터럽트
        t1.stop();

        printSub("예제 2: 워치독 — 정상 (먹이 줌)");
        { WatchdogTimer w(10); w.start();
          for(int i=0;i<30;i++){ if(i%8==0) w.feed(); if(w.tick()) break; }
          std::cout << "  결과: " << (w.isReset()?"리셋":"정상") << "\n"; }

        printSub("예제 3: 워치독 — 프로그램 멈춤!");
        { WatchdogTimer w(10); w.start();
          for(int i=0;i<30;i++) if(w.tick()) break;  // 먹이 안 줌!
          std::cout << "  결과: " << (w.isReset()?"리셋":"정상") << "\n"; }
    }
}

// =============================================================================
// 레슨 6: UART/SPI/I2C 통신 프로토콜
// =============================================================================
/*
 *  UART: 전화 통화 (1:1, 비동기, TX/RX 2선)
 *  SPI:  선생님-학생 (1:N, 동기, MOSI/MISO/SCK/CS 4선+)
 *  I2C:  무전기 (1:N, 2선 SDA/SCL, 주소 기반)
 *
 *  ┌──────────────────────────────────────────────┐
 *  │ UART: 유휴─┐시작┐D0┐D1┐..┐D7┐정지┐─유휴   │
 *  │            └───┘──┘──┘  └──┘──┘───┘          │
 *  │                                               │
 *  │ SPI:  SCK  ─┐┌┐┌┐┌┐┌┐┌┐┌┐┌┐┌─              │
 *  │             └┘└┘└┘└┘└┘└┘└┘└┘                 │
 *  │       MOSI ─D7─D6─D5─D4─D3─D2─D1─D0─       │
 *  │       CS   ┐                          ┌─     │
 *  │            └──────────────────────────┘       │
 *  │                                               │
 *  │ I2C:  SDA ─┐START┐ADDR(7bit)┐R/W┐ACK┐DATA  │
 *  │       SCL ──┐┌┐┌┐┌┐┌┐┌┐┌┐┌┐┌┐┌┐┌───        │
 *  └──────────────────────────────────────────────┘
 *
 *  ┌──────────┬──────────┬────────────┬────────────┐
 *  │ 프로토콜 │ 신호선   │ 속도       │ 용도       │
 *  ├──────────┼──────────┼────────────┼────────────┤
 *  │ UART     │ 2(TX/RX) │ ~115200bps │ 디버그,GPS │
 *  │ SPI      │ 4+       │ ~50Mbps    │ LCD, SD    │
 *  │ I2C      │ 2(SDA/SCL)│ ~400kbps  │ 센서,EEPROM│
 *  └──────────┴──────────┴────────────┴────────────┘
 *
 *  C# 비유: "System.IO.Ports.SerialPort가 UART의 상위 추상화"
 */
namespace Lesson6_Protocols {

    class UartDriver {
    public:
        UartDriver(const std::string& n, uint32_t baud=115200) : name_(n), baud_(baud) {
            std::cout << "  [" << n << "] UART 초기화 (보레이트:" << baud << ")\n";
        }
        void transmit(const std::string& s) {
            for(char c:s) tx_.push(c);
            std::cout << "  [" << name_ << "] TX: \"" << s << "\" (" << s.size() << "B)\n";
        }
        void simulateRx(const std::string& s) {
            for(char c:s) rx_.push(c);
            std::cout << "  [" << name_ << "] RX: \"" << s << "\"\n";
        }
        std::string readAll() {
            std::string r; while(!rx_.empty()){r+=rx_.front();rx_.pop();} return r;
        }
    private:
        std::string name_; uint32_t baud_;
        std::queue<char> tx_, rx_;
    };

    class SpiDriver {
    public:
        SpiDriver(const std::string& n) : name_(n) { std::cout<<"  ["<<n<<"] SPI 마스터 초기화\n"; }
        void csSelect(int id) { std::cout<<"  ["<<name_<<"] CS"<<id<<"=LOW\n"; }
        void csDeselect(int id) { std::cout<<"  ["<<name_<<"] CS"<<id<<"=HIGH\n"; }
        uint8_t transfer(uint8_t tx) {
            uint8_t rx = ~tx;
            std::cout << "  [" << name_ << "] TX:0x" << std::hex << std::setw(2)
                      << std::setfill('0') << (int)tx << " RX:0x" << std::setw(2)
                      << (int)rx << std::dec << "\n";
            return rx;
        }
    private:
        std::string name_;
    };

    class I2cDriver {
    public:
        I2cDriver(const std::string& n) : name_(n) { std::cout<<"  ["<<n<<"] I2C 마스터 초기화\n"; }
        void write(uint8_t addr, const std::vector<uint8_t>& data) {
            std::cout << "  [" << name_ << "] START→0x" << std::hex << std::setw(2)
                      << std::setfill('0') << (int)addr << std::dec << "(W)→ACK";
            for(auto b:data) std::cout << "→0x" << std::hex << std::setw(2) << (int)b << std::dec << " ACK";
            std::cout << "→STOP\n";
        }
        std::vector<uint8_t> read(uint8_t addr, size_t len) {
            std::cout << "  [" << name_ << "] START→0x" << std::hex << std::setw(2)
                      << std::setfill('0') << (int)addr << std::dec << "(R)→ACK";
            std::vector<uint8_t> d(len);
            for(size_t i=0;i<len;i++){
                d[i]=(uint8_t)(0x10+i);
                std::cout << "→0x" << std::hex << std::setw(2) << (int)d[i] << std::dec;
                std::cout << (i<len-1?" ACK":" NACK");
            }
            std::cout << "→STOP\n"; return d;
        }
        void scanBus(const std::vector<uint8_t>& devs) {
            std::cout << "  [" << name_ << "] 버스 스캔: ";
            for(auto a:devs) std::cout << "0x" << std::hex << std::setw(2)
                << std::setfill('0') << (int)a << std::dec << " ";
            std::cout << "(" << devs.size() << "개)\n";
        }
    private:
        std::string name_;
    };

    void demo() {
        printHeader("레슨 6: UART/SPI/I2C 통신 프로토콜");

        printSub("UART (비동기 직렬 통신)");
        UartDriver u("UART1", 115200);
        u.transmit("Hello MCU!"); u.simulateRx("OK");
        std::cout << "  수신: \"" << u.readAll() << "\"\n";

        printSub("SPI (동기 직렬 통신)");
        SpiDriver spi("SPI1");
        spi.csSelect(0);
        spi.transfer(0xAA); spi.transfer(0x55);
        spi.csDeselect(0);

        printSub("I2C (2선 통신)");
        I2cDriver i2c("I2C1");
        i2c.scanBus({0x48, 0x50, 0x68});
        i2c.read(0x48, 2);
        i2c.write(0x50, {0x00, 0x10, 0x41, 0x42});
    }
}

// =============================================================================
// 레슨 7: 실전 종합 — 미니 임베디드 시스템 시뮬레이터
// =============================================================================
/*
 *  ┌──────────────────────────────────────────────────┐
 *  │            미니 임베디드 시스템                    │
 *  │                                                   │
 *  │  [온도센서]──I2C──┐    ┌──────────────────┐      │
 *  │  [버튼]──GPIO─────┤    │     MCU          │      │
 *  │  [LED x4]←GPIO────┼────┤ GPIO+Timer+DMA  │      │
 *  │  [PC]←UART────────┤    │ UART+WDT        │      │
 *  │                    └────└──────────────────┘      │
 *  │                                                   │
 *  │  동작: Timer ISR→센서읽기→DMA전송→UART출력       │
 *  │        버튼→LED모드변경, WDT→안정성 보장         │
 *  └──────────────────────────────────────────────────┘
 */
namespace Lesson7_MiniSystem {

    struct SysState { float temp=0; int ledMode=0, readCnt=0; bool running=true; };

    class MiniMCU {
    public:
        MiniMCU() : led_("GPIOA"), btn_("GPIOB"), uart_("UART1",115200),
                    spi_("SPI1"), i2c_("I2C1"), tim_("TIM1"), wdt_(20) {}

        void init() {
            printSub("1단계: 초기화");
            for(int i=0;i<4;i++) led_.pinMode(i, Lesson4_GPIO::PinMode::OUTPUT);
            btn_.pinMode(0, Lesson4_GPIO::PinMode::INPUT_PULLUP);
            tim_.setPrescaler(71); tim_.setAutoReload(499);
            tim_.setCallback([this](){ onTimer(); });
            wdt_.start();
            std::cout << "  *** 초기화 완료! ***\n";
        }

        void run(int cycles) {
            printSub("2단계: 시스템 동작");
            tim_.start();
            for(int c=0; c<cycles && st_.running; c++) {
                std::cout << "\n  ──── 사이클 " << c << " ────\n";
                for(int t=0;t<500;t++) tim_.tick();
                if(c%3==2) {
                    btn_.simulateInput(0, Lesson4_GPIO::PinState::LOW);
                    onButton();
                    btn_.simulateInput(0, Lesson4_GPIO::PinState::HIGH);
                }
                updateLeds();
                wdt_.feed(); wdt_.tick();
            }
            tim_.stop();
            std::cout << "\n  *** 시스템 종료 ***\n";
        }

    private:
        void onTimer() {
            st_.readCnt++;
            st_.temp = 20.0f + (st_.readCnt%10)*0.5f;
            std::cout << "    [Timer] 센서#" << st_.readCnt << " → "
                      << std::fixed << std::setprecision(1) << st_.temp << "°C\n";
            std::ostringstream o; o << "T=" << std::fixed << std::setprecision(1) << st_.temp << "C";
            uart_.transmit(o.str());
        }
        void onButton() {
            st_.ledMode = (st_.ledMode+1)%3;
            const char* modes[] = {"모두끔","순차점등","모두켬"};
            std::cout << "    [버튼] LED→" << modes[st_.ledMode] << "\n";
        }
        void updateLeds() {
            for(int i=0;i<4;i++) {
                Lesson4_GPIO::PinState s = Lesson4_GPIO::PinState::LOW;
                if(st_.ledMode==2) s = Lesson4_GPIO::PinState::HIGH;
                else if(st_.ledMode==1 && i==(st_.readCnt%4)) s = Lesson4_GPIO::PinState::HIGH;
                led_.digitalWrite(i, s);
            }
            std::cout << "    [LED] "; led_.printStatus();
        }

        Lesson4_GPIO::GpioPort led_, btn_;
        Lesson6_Protocols::UartDriver uart_;
        Lesson6_Protocols::SpiDriver spi_;
        Lesson6_Protocols::I2cDriver i2c_;
        Lesson5_TimerWatchdog::HardwareTimer tim_;
        Lesson5_TimerWatchdog::WatchdogTimer wdt_;
        SysState st_;
    };

    void demo() {
        printHeader("레슨 7: 미니 임베디드 시스템 시뮬레이터");
        std::cout << "GPIO(LED+버튼) + Timer + DMA + UART + 워치독 통합!\n";
        MiniMCU mcu; mcu.init(); mcu.run(5);
    }
}

// =============================================================================
// C# vs C++ 비교표
// =============================================================================
void printComparisonTable() {
    printHeader("C# vs C++ (임베디드) 비교표");
    std::cout << R"(
  ┌──────────────┬────────────────────────┬────────────────────────────────┐
  │ 개념         │ C#                     │ C++ (임베디드)                 │
  ├──────────────┼────────────────────────┼────────────────────────────────┤
  │ 하드웨어접근 │ Marshal, P/Invoke      │ volatile 포인터 직접 접근      │
  │ 인터럽트     │ event (OS가 변환)      │ ISR 함수 직접 작성             │
  │ DMA          │ 없음 (CPU가 처리)      │ DMA 컨트롤러 레지스터 직접    │
  │ GPIO         │ System.Device.Gpio     │ 레지스터 비트 직접 조작        │
  │ 타이머       │ System.Timers.Timer    │ 하드웨어 카운터 레지스터      │
  │ 워치독       │ 없음                   │ WDT 하드웨어 자동 리셋        │
  │ 직렬통신     │ SerialPort 클래스      │ UART/SPI/I2C 레지스터 직접    │
  │ 메모리       │ GC (자동, 비결정적)    │ 수동 관리 (결정론적)          │
  └──────────────┴────────────────────────┴────────────────────────────────┘

  C++이 임베디드의 왕인 이유:
  1. 포인터로 레지스터 직접 접근 (제로 오버헤드)
  2. GC 없음 → 실행 시간 예측 가능 (실시간 시스템 필수)
  3. 비트 조작 (&, |, ^, ~, <<, >>) 으로 하드웨어 제어
  4. volatile로 하드웨어 변경 감지
  5. #pragma pack으로 구조체를 하드웨어 레이아웃에 맞춤
  6. 수 KB 플래시에 들어가는 작은 바이너리
  7. 인라인 어셈블리까지 가능
)" << "\n";
}

// =============================================================================
// 메인 함수
// =============================================================================
int main() {
    std::cout << "================================================================\n"
              << "  C++ 학습 30단계: 하드웨어 레벨 제어 (시뮬레이션)\n"
              << "================================================================\n"
              << "  실제 하드웨어 없이 임베디드 핵심 개념을 배웁니다.\n"
              << "  코드 구조는 실제 MCU 개발과 동일합니다!\n";

    /*
    =========================================================================
      레슨별 demo() 출력 흐름 가이드 (시뮬레이션)
    =========================================================================
      Lesson1 (MMIO):
        volatile uint32_t* GPIO_DATA = (uint32_t*)0x40020000;
        *GPIO_DATA |= (1 << 5);   // 5번 비트 set (GPIO 5번 핀 HIGH)
        시뮬레이션이므로 가상 메모리 영역에 쓰고 읽음

      Lesson2 (Interrupts/ISR):
        타이머 ISR 등록 → 1ms마다 호출 시뮬레이션
        ISR 안에서는 짧게! (printf 금지, 변수 1개 set만)
        메인 루프가 변수 보고 처리

      Lesson3 (DMA):
        memcpy_dma(dst, src, 1024) 시뮬레이션
        CPU 안 거치고 백그라운드 복사 (실제로는 DMA 컨트롤러 동작)

      Lesson4 (GPIO):
        LED on/off, 버튼 입력 polling
        debouncing (튀는 현상 제거): 5ms 후 재읽기

      Lesson5 (Timer/Watchdog):
        SysTick 1kHz 시뮬레이션 → tick++
        Watchdog: 1초 안에 reset 안 하면 시스템 재시작 (시뮬)

      Lesson6 (UART/SPI/I2C):
        UART: send "Hello" → 시리얼 출력 시뮬레이션
        SPI: master/slave 클럭 동기 전송
        I2C: 7비트 주소 + read/write

      Lesson7 (Mini System):
        센서 read → DMA buffer → 처리 → UART 송신 통합 흐름

      printComparisonTable: 프로토콜 비교표
        UART: 비동기, 2선, 점대점, 1Mbps급
        SPI:  동기, 4선+, 멀티슬레이브, 50Mbps급
        I2C:  동기, 2선, 멀티마스터, 1~5Mbps
    =========================================================================
    */
    Lesson1_MMIO::demo();
    Lesson2_Interrupts::demo();
    Lesson3_DMA::demo();
    Lesson4_GPIO::demo();
    Lesson5_TimerWatchdog::demo();
    Lesson6_Protocols::demo();
    Lesson7_MiniSystem::demo();
    printComparisonTable();

    std::cout << "\n================================================================\n"
              << "  핵심 정리\n"
              << "================================================================\n"
              << "  1. MMIO: 메모리 주소 = 하드웨어 → volatile 포인터\n"
              << "  2. 인터럽트: 하드웨어 긴급 신호 → ISR → NVIC 우선순위\n"
              << "  3. DMA: CPU 없이 데이터 자동 전송 → CPU는 다른 일!\n"
              << "  4. GPIO: 핀으로 LED/버튼/PWM → 비트 조작\n"
              << "  5. 타이머: 하드웨어 카운터 → 정밀한 주기 작업\n"
              << "  6. 워치독: 먹이 안 주면 리셋 → 안정성 최후 방어선\n"
              << "  7. UART/SPI/I2C: 외부 장치 통신 → 용도별 선택\n\n"
              << "  C++이 임베디드의 왕인 이유:\n"
              << "  → 하드웨어 '직접' 제어 가능한 유일한 고급 언어\n"
              << "  → GC 없음 = 실시간 필수, 제로 오버헤드 추상화\n\n";
    return 0;
}
