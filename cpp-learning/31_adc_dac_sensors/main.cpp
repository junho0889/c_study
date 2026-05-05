/*
 * =============================================================================
 *  C++ 임베디드 학습 #31: ADC/DAC와 센서 인터페이스
 *  (Analog-Digital Conversion & Sensor Interface)
 * =============================================================================
 *
 *  컴파일: g++ -std=c++17 -o adc_dac_sensors main.cpp
 *  실행: ./adc_dac_sensors
 *
 *  ★ 모든 하드웨어는 소프트웨어로 시뮬레이션합니다! ★
 *
 *  ADC: 온도 23.7°C → 디지털 163 / DAC: 디지털 128 → 전압 1.65V
 *  C# 비유: ADC는 (int)Math.Round(), DAC는 (float)digital과 비슷!
 */

#include <iostream>
#include <cstdint>
#include <cmath>
#include <vector>
#include <array>
#include <algorithm>
#include <numeric>
#include <string>
#include <cstring>
#include <functional>
#include <iomanip>
#include <sstream>
#include <fstream>
#include <chrono>
#include <random>
#include <cassert>

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

// 전역 난수 생성기 (센서 노이즈 시뮬레이션용)
static std::mt19937 g_rng(42);

static double addNoise(double value, double noiseLevel) {
    // 센서에는 항상 노이즈가 있어요! (잡음)
    // 진짜 온도가 25.0도여도 센서는 24.8~25.2 같이 흔들려요
    std::normal_distribution<double> dist(0.0, noiseLevel);
    return value + dist(g_rng);
}

// =================================================================
//  레슨 1: ADC (Analog to Digital Converter) 개념과 시뮬레이션
// =================================================================
/*
 *  ★ ADC란? ★
 *  현실 세계의 부드러운 값(아날로그)을 컴퓨터가 이해하는 숫자(디지털)로 바꿔주는 장치
 *
 *  C# 비유: double temperature = 23.456789;
 *           int digitalValue = (int)Math.Round(temperature);  // 23
 *           → 소수점이 사라지면서 정보가 약간 손실됩니다!
 *
 *  ① 샘플링: 일정 간격으로 아날로그 값을 찍어요
 *  ② 양자화: 가장 가까운 계단 값으로 반올림
 *  ③ 비트 해상도: 8비트=256단계, 10비트=1024, 12비트=4096
 */

// ADC 시뮬레이터: 실제 마이크로컨트롤러의 ADC를 흉내냅니다
class ADC_Simulator {
    // C# 비유: 이 클래스는 AnalogInput 같은 하드웨어 추상화 클래스입니다
public:
    // ADC 해상도 (비트 수)
    enum class Resolution : uint8_t {
        BIT_8  = 8,    // 256 단계 (Arduino 기본은 10비트이지만, 8비트로 설명)
        BIT_10 = 10,   // 1024 단계 (Arduino UNO)
        BIT_12 = 12    // 4096 단계 (STM32, ESP32)
    };

    // ADC 레지스터들 (하드웨어 레지스터를 흉내냄)
    // 실제 MCU에서는 메모리 주소에 매핑된 레지스터를 읽고 씁니다
    struct ADC_Registers {
        uint32_t CR;       // Control Register (제어 레지스터)
        uint32_t SR;       // Status Register (상태 레지스터)
        uint32_t DR;       // Data Register (데이터 레지스터 - 변환 결과)
        uint32_t SMPR;     // Sample Time Register (샘플링 시간)
        uint32_t SQR;      // Sequence Register (채널 순서)
    };

    // 제어 레지스터 비트 정의
    static constexpr uint32_t CR_ADON   = (1 << 0);  // ADC 켜기
    static constexpr uint32_t CR_START  = (1 << 1);  // 변환 시작
    static constexpr uint32_t SR_EOC    = (1 << 0);  // 변환 완료 (End Of Conversion)
    static constexpr uint32_t SR_BUSY   = (1 << 1);  // 변환 중

private:
    ADC_Registers regs_{};
    Resolution resolution_;
    double vref_;             // 기준 전압 (보통 3.3V 또는 5.0V)
    uint32_t maxValue_;       // 최대 디지털 값 (2^비트수 - 1)
    double inputVoltage_;     // 현재 입력 전압 (시뮬레이션)

public:
    explicit ADC_Simulator(Resolution res = Resolution::BIT_10, double vref = 3.3)
        : resolution_(res), vref_(vref), inputVoltage_(0.0)
    {
        maxValue_ = (1u << static_cast<uint8_t>(res)) - 1;
        std::memset(&regs_, 0, sizeof(regs_));
    }

    // ADC 켜기 (전원 인가)
    void powerOn() {
        regs_.CR |= CR_ADON;
        std::cout << "  [ADC] 전원 켜짐 (ADON=1)\n";
    }

    // 아날로그 전압 입력 설정 (시뮬레이션)
    void setInputVoltage(double voltage) {
        inputVoltage_ = std::clamp(voltage, 0.0, vref_);
    }

    // 변환 시작
    void startConversion() {
        if (!(regs_.CR & CR_ADON)) {
            std::cout << "  [ADC] 오류! ADC가 꺼져있습니다. 먼저 powerOn() 하세요.\n";
            return;
        }
        regs_.CR |= CR_START;
        regs_.SR |= SR_BUSY;
        regs_.SR &= ~SR_EOC;

        // 변환 수행 (실제로는 수 마이크로초 걸림, 여기선 즉시)
        // 양자화: 아날로그 전압을 디지털 값으로 바꿉니다
        // 공식: digital = (voltage / vref) × maxValue
        double ratio = inputVoltage_ / vref_;
        regs_.DR = static_cast<uint32_t>(std::round(ratio * maxValue_));

        // 변환 완료
        regs_.SR &= ~SR_BUSY;
        regs_.SR |= SR_EOC;
        regs_.CR &= ~CR_START;
    }

    // 변환 완료 대기 (폴링 방식)
    bool isConversionDone() const {
        return (regs_.SR & SR_EOC) != 0;
    }

    // 결과 읽기
    uint32_t readValue() {
        if (!isConversionDone()) {
            std::cout << "  [ADC] 경고: 변환이 아직 완료되지 않았습니다!\n";
            return 0;
        }
        uint32_t val = regs_.DR;
        regs_.SR &= ~SR_EOC;  // 읽으면 플래그 클리어
        return val;
    }

    // 디지털 값을 전압으로 역변환 (표시용)
    double toVoltage(uint32_t digitalValue) const {
        return (static_cast<double>(digitalValue) / maxValue_) * vref_;
    }

    uint32_t getMaxValue() const { return maxValue_; }
    double getVref() const { return vref_; }
    uint8_t getBits() const { return static_cast<uint8_t>(resolution_); }
};

static void demonstrateNyquist() {
    printSubHeader("나이퀴스트 정리 (Nyquist Theorem)");
    // 나이퀴스트: 샘플링 주파수 ≥ 2 × 신호 주파수 이어야 원래 신호를 복원 가능
    // 부족하면 "앨리어싱" 발생 → 엉뚱한 저주파 신호가 나타남!

    double signalFreq = 100.0;  // 100Hz 신호
    double goodSampleRate = 400.0;
    double badSampleRate = 80.0;

    std::cout << "  신호 주파수: " << signalFreq << " Hz\n";
    std::cout << "  나이퀴스트 최소 샘플링: " << (2 * signalFreq) << " Hz\n";
    std::cout << "  좋은 샘플링(" << goodSampleRate << "Hz): "
              << (goodSampleRate >= 2 * signalFreq ? "OK ✓" : "부족 ✗") << "\n";
    std::cout << "  나쁜 샘플링(" << badSampleRate << "Hz): "
              << (badSampleRate >= 2 * signalFreq ? "OK ✓" : "부족 ✗ (앨리어싱 발생!)") << "\n";
}

static void lesson1_adc() {
    printHeader("레슨 1: ADC (Analog to Digital Converter)");

    std::cout << "  C# 비유: (int)Math.Round(23.7)→24 와 비슷합니다!\n";
    printSubHeader("비트 해상도 비교");
    double testVoltage = 1.5;  // 1.5V 테스트
    std::cout << "  입력 전압: " << testVoltage << "V (기준전압 3.3V)\n\n";

    ADC_Simulator::Resolution resolutions[] = {
        ADC_Simulator::Resolution::BIT_8,
        ADC_Simulator::Resolution::BIT_10,
        ADC_Simulator::Resolution::BIT_12
    };

    for (auto res : resolutions) {
        ADC_Simulator adc(res, 3.3);
        adc.powerOn();
        adc.setInputVoltage(testVoltage);
        adc.startConversion();
        uint32_t val = adc.readValue();
        double backVoltage = adc.toVoltage(val);
        double error = std::abs(testVoltage - backVoltage);
        double stepSize = adc.getVref() / adc.getMaxValue();

        std::cout << "  " << (int)adc.getBits() << "비트 ADC:\n";
        std::cout << "    최대값: " << adc.getMaxValue()
                  << " | 변환결과: " << val
                  << " | 복원전압: " << std::fixed << std::setprecision(4)
                  << backVoltage << "V"
                  << " | 오차: " << error << "V"
                  << " | 단계크기: " << stepSize << "V\n";
    }

    // 나이퀴스트 정리
    demonstrateNyquist();

    // ADC 레지스터 동작 시뮬레이션
    printSubHeader("ADC 레지스터 동작 시뮬레이션");
    ADC_Simulator adc(ADC_Simulator::Resolution::BIT_10, 3.3);

    std::cout << "  1단계: ADC 전원 켜기\n";
    adc.powerOn();

    std::cout << "  2단계: 입력 전압 설정 (2.0V)\n";
    adc.setInputVoltage(2.0);

    std::cout << "  3단계: 변환 시작\n";
    adc.startConversion();

    std::cout << "  4단계: 완료 확인 → " << (adc.isConversionDone() ? "완료!" : "대기중...") << "\n";

    uint32_t result = adc.readValue();
    std::cout << "  5단계: 결과 읽기 → " << result
              << " (전압: " << adc.toVoltage(result) << "V)\n";
}

// =================================================================
//  레슨 2: DAC (Digital to Analog Converter)
// =================================================================
// ★ DAC란? ADC의 반대! 숫자를 다시 전압으로 바꿔주는 장치
// C# 비유: float voltage = (float)digitalValue / 255.0f * 3.3f;
// ① 진짜 DAC: 숫자 → 바로 전압 출력 (128 → 1.65V)
// ② PWM+RC필터: 빠른 ON/OFF → 평균 전압 (50% PWM → 절반 전압)

class DAC_Simulator {
    uint8_t bits_;
    uint32_t maxValue_;
    double vref_;
    double outputVoltage_;

public:
    explicit DAC_Simulator(uint8_t bits = 8, double vref = 3.3)
        : bits_(bits), vref_(vref), outputVoltage_(0.0)
    {
        maxValue_ = (1u << bits) - 1;
    }

    // 디지털 값을 아날로그 전압으로 변환
    double convert(uint32_t digitalValue) {
        uint32_t clamped = std::min(digitalValue, maxValue_);
        outputVoltage_ = (static_cast<double>(clamped) / maxValue_) * vref_;
        return outputVoltage_;
    }

    double getOutput() const { return outputVoltage_; }
    uint32_t getMaxValue() const { return maxValue_; }
};

// PWM으로 DAC 흉내내기
class PWM_DAC {
    // PWM은 빠르게 켜고 끄는 것! 50% 켜면 평균 전압은 절반!
    // C# 비유: Timer로 LED를 빠르게 깜빡이면 밝기가 절반으로 보이는 것
    double dutyCycle_;    // 0.0 ~ 1.0 (0% ~ 100%)
    double vcc_;          // 전원 전압
    uint32_t frequency_;  // PWM 주파수

public:
    explicit PWM_DAC(double vcc = 3.3, uint32_t freq = 10000)
        : dutyCycle_(0.0), vcc_(vcc), frequency_(freq) {}

    void setDutyCycle(double duty) {
        dutyCycle_ = std::clamp(duty, 0.0, 1.0);
    }

    // RC 필터 후 평균 전압
    double getFilteredVoltage() const {
        return dutyCycle_ * vcc_;
    }

    // PWM 파형 시각화 (1주기)
    void printWaveform() const {
        int highSamples = static_cast<int>(dutyCycle_ * 20);
        int lowSamples = 20 - highSamples;

        std::cout << "    PWM(" << std::fixed << std::setprecision(0)
                  << (dutyCycle_ * 100) << "%): ";
        for (int i = 0; i < highSamples; i++) std::cout << "▓";
        for (int i = 0; i < lowSamples; i++) std::cout << "░";
        std::cout << " → " << std::setprecision(2) << getFilteredVoltage() << "V\n";
    }
};

// 사인파 룩업 테이블 (LUT) - 실제 임베디드에서 흔한 기법
// sin() 함수를 매번 계산하면 느리니까, 미리 계산해놓고 표에서 찾아요!
static constexpr int SINE_LUT_SIZE = 64;

static std::array<uint8_t, SINE_LUT_SIZE> generateSineLUT() {
    std::array<uint8_t, SINE_LUT_SIZE> lut{};
    for (int i = 0; i < SINE_LUT_SIZE; i++) {
        double angle = 2.0 * M_PI * i / SINE_LUT_SIZE;
        double value = (std::sin(angle) + 1.0) / 2.0;  // 0.0 ~ 1.0
        lut[i] = static_cast<uint8_t>(value * 255);
    }
    return lut;
}

static void lesson2_dac() {
    printHeader("레슨 2: DAC (Digital to Analog Converter)");

    std::cout << "  C# 비유: float voltage = (float)value / 255f * 3.3f;\n";
    // 기본 DAC 변환
    printSubHeader("8비트 DAC 변환 예시");
    DAC_Simulator dac(8, 3.3);

    uint32_t testValues[] = {0, 64, 128, 192, 255};
    for (auto val : testValues) {
        double voltage = dac.convert(val);
        std::cout << "    디지털 " << std::setw(3) << val
                  << " → " << std::fixed << std::setprecision(3) << voltage << "V\n";
    }

    // PWM으로 DAC 흉내내기
    printSubHeader("PWM으로 DAC 흉내내기");
    PWM_DAC pwm(3.3);

    double duties[] = {0.0, 0.25, 0.50, 0.75, 1.0};
    for (auto d : duties) {
        pwm.setDutyCycle(d);
        pwm.printWaveform();
    }

    // 사인파 룩업 테이블
    printSubHeader("사인파 출력 (룩업 테이블)");
    auto sineLUT = generateSineLUT();

    std::cout << "  사인파 LUT 처음 16개 샘플 (값 0~255):\n  ";
    for (int i = 0; i < 16; i++) {
        std::cout << std::setw(4) << (int)sineLUT[i];
    }
    std::cout << " ...\n\n  사인파 시각화 (DAC 출력, 매 4번째):\n";
    for (int i = 0; i < SINE_LUT_SIZE; i += 4) {
        int level = sineLUT[i] / 16;
        std::cout << "  " << std::setw(3) << (int)sineLUT[i] << " |";
        for (int j = 0; j < level; j++) std::cout << "█";
        std::cout << "\n";
    }
}

// =================================================================
//  레슨 3: 센서 드라이버 구현
// =================================================================
// 센서 블록도: [온도/가속도/거리/조도] → [ADC] → [MCU] → [표시/저장]
// 각 센서는 물리량을 전압으로 바꾸고, ADC가 그 전압을 숫자로 바꿉니다!

// 센서 인터페이스 (추상 클래스)
// C# 비유: ISensor 인터페이스와 동일한 개념
class ISensor {
public:
    virtual ~ISensor() = default;
    virtual double read() = 0;                  // 센서 값 읽기
    virtual std::string getName() const = 0;    // 센서 이름
    virtual std::string getUnit() const = 0;    // 단위
};

// ① 온도 센서 (NTC 서미스터 시뮬레이션)
// NTC = 온도가 올라가면 저항이 내려가는 소자
// 데이터시트 핵심: B값(특성상수), R25(25°C 저항), 전압 분배 공식
class TemperatureSensor : public ISensor {
    double actualTemp_;     // 실제 온도 (시뮬레이션)
    double beta_;           // B값 (보통 3950)
    double r25_;            // 25°C에서의 저항 (10kΩ)

public:
    explicit TemperatureSensor(double initialTemp = 25.0)
        : actualTemp_(initialTemp), beta_(3950.0), r25_(10000.0) {}

    void setActualTemperature(double temp) { actualTemp_ = temp; }

    double read() override {
        // NTC 저항 계산: R = R25 × exp(B × (1/T - 1/T25))
        // 여기에 노이즈를 추가해서 현실적으로 만듭니다
        return addNoise(actualTemp_, 0.3);  // ±0.3°C 노이즈
    }

    std::string getName() const override { return "NTC 온도센서"; }
    std::string getUnit() const override { return "°C"; }
};

// ② 가속도 센서 (3축 X/Y/Z)
// 데이터시트 핵심: 감도(mV/g), 제로g 오프셋, 측정 범위(±2g, ±4g 등)
struct AccelData {
    double x, y, z;   // 단위: g (중력가속도)
    double magnitude() const { return std::sqrt(x*x + y*y + z*z); }
};

class AccelerometerSensor : public ISensor {
    AccelData actual_;

public:
    AccelerometerSensor() : actual_{0.0, 0.0, 1.0} {}  // 정지상태 = z축 1g

    void setActualAccel(double x, double y, double z) {
        actual_ = {x, y, z};
    }

    AccelData readXYZ() {
        return {
            addNoise(actual_.x, 0.02),
            addNoise(actual_.y, 0.02),
            addNoise(actual_.z, 0.02)
        };
    }

    double read() override { return readXYZ().magnitude(); }
    std::string getName() const override { return "3축 가속도센서"; }
    std::string getUnit() const override { return "g"; }
};

// ③ 거리 센서 (초음파)
// 원리: 초음파를 쏘고 돌아오는 시간 측정 → 거리 = 시간 × 음속 / 2
class UltrasonicSensor : public ISensor {
    double actualDistance_;   // 실제 거리 (cm)
    static constexpr double SOUND_SPEED = 34300.0;  // 음속 cm/s (20°C)

public:
    explicit UltrasonicSensor(double dist = 50.0) : actualDistance_(dist) {}

    void setActualDistance(double dist) { actualDistance_ = dist; }

    double read() override {
        // 왕복 시간 → 거리
        double measuredTime = (actualDistance_ * 2.0) / SOUND_SPEED;
        double noisyTime = addNoise(measuredTime, measuredTime * 0.01);
        return (noisyTime * SOUND_SPEED) / 2.0;
    }

    std::string getName() const override { return "초음파 거리센서"; }
    std::string getUnit() const override { return "cm"; }
};

// ④ 조도 센서 (광저항/LDR)
class LightSensor : public ISensor {
    double actualLux_;

public:
    explicit LightSensor(double lux = 500.0) : actualLux_(lux) {}
    void setActualLux(double lux) { actualLux_ = lux; }

    double read() override {
        return addNoise(actualLux_, actualLux_ * 0.05);
    }

    std::string getName() const override { return "조도센서 (LDR)"; }
    std::string getUnit() const override { return "lux"; }
};

static void lesson3_sensors() {
    printHeader("레슨 3: 센서 드라이버 구현");

    // 모든 센서 생성
    TemperatureSensor tempSensor(25.0);
    AccelerometerSensor accelSensor;
    UltrasonicSensor distSensor(30.0);
    LightSensor lightSensor(750.0);

    // 다형성으로 센서 배열 관리 (C#의 ISensor[] 와 동일!)
    std::vector<ISensor*> sensors = {&tempSensor, &accelSensor, &distSensor, &lightSensor};

    printSubHeader("각 센서 5회 읽기 (노이즈 포함)");
    for (auto* sensor : sensors) {
        std::cout << "\n  [" << sensor->getName() << "] (" << sensor->getUnit() << "):\n    ";
        for (int i = 0; i < 5; i++) {
            std::cout << std::fixed << std::setprecision(2) << sensor->read();
            if (i < 4) std::cout << ", ";
        }
        std::cout << "\n";
    }

    // 가속도 센서 3축 데이터
    printSubHeader("가속도 센서 3축 데이터");
    accelSensor.setActualAccel(0.1, -0.2, 0.98);
    for (int i = 0; i < 3; i++) {
        AccelData d = accelSensor.readXYZ();
        std::cout << "  읽기 " << (i+1) << ": X=" << std::setprecision(3) << d.x
                  << "g, Y=" << d.y << "g, Z=" << d.z
                  << "g, |크기|=" << d.magnitude() << "g\n";
    }
}

// =================================================================
//  레슨 4: 센서 데이터 필터링
// =================================================================
/*
 *  센서 값이 왜 흔들릴까? → 노이즈(잡음) 때문!
 *  필터 = 흔들리는 값을 부드럽게 만드는 것
 *
 *  C# 비유: List<double>.Average()를 이동 창(window)에 적용하는 것
 */

// ① 이동 평균 필터 (Moving Average Filter)
// "최근 N개 값의 평균"을 구하는 가장 간단한 필터
template<int N>
class MovingAverage {
    double buffer_[N]{};
    int index_ = 0;
    int count_ = 0;

public:
    double update(double newValue) {
        buffer_[index_] = newValue;
        index_ = (index_ + 1) % N;
        if (count_ < N) count_++;

        double sum = 0;
        for (int i = 0; i < count_; i++) sum += buffer_[i];
        return sum / count_;
    }

    void reset() { index_ = 0; count_ = 0; }
};

// ② 지수 이동 평균 (EMA / 로우패스 필터)
// "새 값을 α만큼, 이전 결과를 (1-α)만큼 섞는다"
// α가 작으면 더 부드럽고 느리게 반응, α가 크면 빠르게 반응
class ExponentialMovingAverage {
    double alpha_;     // 0.0~1.0 (보통 0.1~0.3)
    double output_;
    bool initialized_;

public:
    explicit ExponentialMovingAverage(double alpha = 0.2)
        : alpha_(alpha), output_(0.0), initialized_(false) {}

    double update(double newValue) {
        if (!initialized_) {
            output_ = newValue;
            initialized_ = true;
        } else {
            output_ = alpha_ * newValue + (1.0 - alpha_) * output_;
        }
        return output_;
    }
};

// ③ 칼만 필터 (1D 간단 버전)
// "예측하고, 측정하고, 둘을 적절히 섞는다" → 가장 똑똑한 필터
class SimpleKalmanFilter {
    double q_;  // 프로세스 노이즈 공분산
    double r_;  // 측정 노이즈 공분산
    double p_;  // 추정 오차 공분산
    double x_;  // 추정값
    double k_;  // 칼만 이득

public:
    SimpleKalmanFilter(double processNoise, double measureNoise, double estimateError)
        : q_(processNoise), r_(measureNoise), p_(estimateError), x_(0.0), k_(0.0) {}

    double update(double measurement) {
        // 1) 예측 단계: 오차 증가
        p_ += q_;
        // 2) 칼만 이득 계산: 측정을 얼마나 믿을지
        k_ = p_ / (p_ + r_);
        // 3) 업데이트: 예측과 측정을 섞기
        x_ += k_ * (measurement - x_);
        // 4) 오차 줄이기
        p_ *= (1.0 - k_);
        return x_;
    }
};

// ④ 중앙값 필터 (Median Filter)
// "최근 N개 중 가운데 값" → 스파이크 노이즈에 강함!
template<int N>
class MedianFilter {
    double buffer_[N]{};
    int index_ = 0;
    int count_ = 0;

public:
    double update(double newValue) {
        buffer_[index_] = newValue;
        index_ = (index_ + 1) % N;
        if (count_ < N) count_++;

        // 정렬해서 중앙값 찾기
        double sorted[N];
        std::copy(buffer_, buffer_ + count_, sorted);
        std::sort(sorted, sorted + count_);
        return sorted[count_ / 2];
    }
};

// ⑤ 상보 필터 (Complementary Filter)
// 가속도센서(느리지만 정확) + 자이로(빠르지만 드리프트) = 합치면 좋다!
class ComplementaryFilter {
    double alpha_;   // 가속도 비중 (보통 0.02~0.05)
    double angle_;

public:
    explicit ComplementaryFilter(double alpha = 0.02) : alpha_(alpha), angle_(0.0) {}

    double update(double accelAngle, double gyroRate, double dt) {
        // 자이로: 빠른 변화 담당 / 가속도: 장기 안정성 담당
        angle_ = (1.0 - alpha_) * (angle_ + gyroRate * dt) + alpha_ * accelAngle;
        return angle_;
    }
};

static void lesson4_filtering() {
    printHeader("레슨 4: 센서 데이터 필터링");

    // 노이즈가 있는 온도 데이터 생성 (실제 25.0도)
    const double actualTemp = 25.0;
    const int SAMPLES = 30;

    std::vector<double> rawData(SAMPLES);
    for (int i = 0; i < SAMPLES; i++) {
        rawData[i] = addNoise(actualTemp, 1.5);  // ±1.5도 노이즈
    }

    // 각 필터 적용
    MovingAverage<5> ma5;
    ExponentialMovingAverage ema(0.2);
    SimpleKalmanFilter kalman(0.01, 1.0, 1.0);
    MedianFilter<5> median;

    printSubHeader("필터 비교 (실제온도=25.0°C, 노이즈 ±1.5°C)");
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "  #    원본     이동평균  EMA      칼만     중앙값\n";
    std::cout << "  ──── ──────── ──────── ──────── ──────── ────────\n";

    for (int i = 0; i < SAMPLES; i++) {
        double raw = rawData[i];
        double maVal = ma5.update(raw);
        double emaVal = ema.update(raw);
        double kalVal = kalman.update(raw);
        double medVal = median.update(raw);

        std::cout << "  " << std::setw(3) << i
                  << "  " << std::setw(7) << raw
                  << "  " << std::setw(7) << maVal
                  << "  " << std::setw(7) << emaVal
                  << "  " << std::setw(7) << kalVal
                  << "  " << std::setw(7) << medVal << "\n";
    }

    // 스파이크 노이즈 테스트 (중앙값 필터가 잘 제거)
    printSubHeader("스파이크 노이즈 제거 (중앙값 필터)");
    MedianFilter<5> medSpike;
    double spikeData[] = {25.0, 25.1, 99.9, 24.9, 25.0, 25.1, 0.1, 25.0};
    for (int i = 0; i < 8; i++) {
        double med = medSpike.update(spikeData[i]);
        std::cout << "    원본=" << std::setw(5) << spikeData[i]
                  << " → 중앙값=" << std::setw(5) << med << "\n";
    }
}

// =================================================================
//  레슨 5: 데이터 로깅과 텔레메트리
// =================================================================
// C# 비유: BinaryWriter로 구조체 저장 → EEPROM에 저장 / SerialPort → UART 텔레메트리

// 센서 데이터를 담는 로그 엔트리
#pragma pack(push, 1)   // 패딩 없이 꽉 채워서 저장 (바이너리 파일용)
struct SensorLogEntry {
    uint32_t timestamp_ms;   // 타임스탬프 (밀리초)
    int16_t  temperature;    // 온도 × 100 (25.37°C → 2537)
    uint16_t humidity;       // 습도 × 100
    uint16_t pressure;       // 기압 × 10
    uint16_t light;          // 조도
    uint8_t  checksum;       // 체크섬

    uint8_t calcChecksum() const {
        const uint8_t* p = reinterpret_cast<const uint8_t*>(this);
        uint8_t sum = 0;
        for (size_t i = 0; i < sizeof(SensorLogEntry) - 1; i++) {
            sum += p[i];
        }
        return sum;
    }
};
#pragma pack(pop)

// 링버퍼 기반 실시간 로깅
// 링버퍼 = 원형 큐. 가득 차면 가장 오래된 데이터를 덮어씀
template<typename T, int SIZE>
class RingBuffer {
    T buffer_[SIZE]{};
    int head_ = 0;    // 쓰기 위치
    int tail_ = 0;    // 읽기 위치
    int count_ = 0;

public:
    bool push(const T& item) {
        buffer_[head_] = item;
        head_ = (head_ + 1) % SIZE;
        if (count_ < SIZE) {
            count_++;
        } else {
            tail_ = (tail_ + 1) % SIZE;  // 가장 오래된 것 버림
        }
        return true;
    }

    bool pop(T& item) {
        if (count_ == 0) return false;
        item = buffer_[tail_];
        tail_ = (tail_ + 1) % SIZE;
        count_--;
        return true;
    }

    int size() const { return count_; }
    bool isFull() const { return count_ == SIZE; }
    bool isEmpty() const { return count_ == 0; }
};

// 텔레메트리 프로토콜
// 구조: [SYNC1][SYNC2][TYPE][LENGTH][PAYLOAD...][CHECKSUM]
struct TelemetryPacket {
    static constexpr uint8_t SYNC1 = 0xAA;
    static constexpr uint8_t SYNC2 = 0x55;

    uint8_t type;
    uint8_t length;
    uint8_t payload[64];
    uint8_t checksum;

    void build(uint8_t msgType, const void* data, uint8_t dataLen) {
        type = msgType;
        length = std::min(dataLen, (uint8_t)64);
        std::memcpy(payload, data, length);

        // 체크섬 계산
        checksum = type ^ length;
        for (int i = 0; i < length; i++) {
            checksum ^= payload[i];
        }
    }

    bool verify() const {
        uint8_t calc = type ^ length;
        for (int i = 0; i < length; i++) {
            calc ^= payload[i];
        }
        return calc == checksum;
    }

    void printHex() const {
        std::cout << "  [" << std::hex << std::uppercase;
        std::cout << std::setw(2) << std::setfill('0') << (int)SYNC1 << " ";
        std::cout << std::setw(2) << (int)SYNC2 << " ";
        std::cout << std::setw(2) << (int)type << " ";
        std::cout << std::setw(2) << (int)length << " ";
        for (int i = 0; i < length; i++) {
            std::cout << std::setw(2) << (int)payload[i] << " ";
        }
        std::cout << std::setw(2) << (int)checksum;
        std::cout << "]" << std::dec << std::setfill(' ') << "\n";
    }
};

static void lesson5_logging() {
    printHeader("레슨 5: 데이터 로깅과 텔레메트리");

    // 링버퍼 데모
    printSubHeader("링버퍼 기반 로깅 (크기=8)");
    RingBuffer<SensorLogEntry, 8> logBuffer;

    for (uint32_t i = 0; i < 12; i++) {
        SensorLogEntry entry{};
        entry.timestamp_ms = i * 1000;
        entry.temperature = static_cast<int16_t>(2500 + (i * 10));
        entry.humidity = 6000 + i * 50;
        entry.pressure = 10130;
        entry.light = 500;
        entry.checksum = entry.calcChecksum();

        logBuffer.push(entry);
        std::cout << "  Push #" << i << " (t=" << entry.timestamp_ms << "ms)"
                  << " → 버퍼: " << logBuffer.size() << "/8"
                  << (logBuffer.isFull() ? " [가득참-오래된것 삭제]" : "") << "\n";
    }

    std::cout << "\n  링버퍼에서 꺼내기:\n";
    SensorLogEntry e;
    while (logBuffer.pop(e)) {
        std::cout << "    t=" << e.timestamp_ms << "ms, 온도="
                  << std::fixed << std::setprecision(2)
                  << (e.temperature / 100.0) << "°C\n";
    }

    // 텔레메트리 프로토콜
    printSubHeader("텔레메트리 패킷 (헤더+페이로드+체크섬)");
    // 패킷: [SYNC:0xAA][SYNC:0x55][TYPE][LENGTH][PAYLOAD...][CHECKSUM(XOR)]

    // 온도 데이터 전송 패킷
    int16_t tempData = 2537;  // 25.37°C
    TelemetryPacket pkt;
    pkt.build(0x01, &tempData, sizeof(tempData));

    std::cout << "  온도 데이터(25.37°C) 패킷:\n";
    pkt.printHex();
    std::cout << "  체크섬 검증: " << (pkt.verify() ? "OK ✓" : "실패 ✗") << "\n";

    // 손상된 패킷
    TelemetryPacket badPkt = pkt;
    badPkt.payload[0] = 0xFF;  // 데이터 손상!
    std::cout << "\n  손상된 패킷:\n";
    badPkt.printHex();
    std::cout << "  체크섬 검증: " << (badPkt.verify() ? "OK ✓" : "실패 ✗ (손상 감지!)") << "\n";
}

// =================================================================
//  레슨 6: 실전 — 미니 날씨 관측소
// =================================================================
// 미니 날씨 관측소: [온도/습도/기압] → [필터링] → [이상치감지] → [표시/CSV저장]

// 습도 센서 (시뮬레이션)
class HumiditySensor : public ISensor {
    double actualHumidity_;
public:
    explicit HumiditySensor(double h = 60.0) : actualHumidity_(h) {}
    void setActualHumidity(double h) { actualHumidity_ = h; }
    double read() override { return addNoise(actualHumidity_, 2.0); }
    std::string getName() const override { return "습도센서"; }
    std::string getUnit() const override { return "%"; }
};

// 기압 센서 (시뮬레이션)
class PressureSensor : public ISensor {
    double actualPressure_;  // hPa
public:
    explicit PressureSensor(double p = 1013.25) : actualPressure_(p) {}
    void setActualPressure(double p) { actualPressure_ = p; }
    double read() override { return addNoise(actualPressure_, 0.5); }
    std::string getName() const override { return "기압센서"; }
    std::string getUnit() const override { return "hPa"; }
};

// 이상치 감지기
struct ThresholdAlert {
    std::string name;
    double minVal, maxVal;

    bool check(double value) const {
        return value < minVal || value > maxVal;
    }

    std::string getMessage(double value) const {
        if (value < minVal) return name + " 너무 낮음! (" + std::to_string(value) + ")";
        if (value > maxVal) return name + " 너무 높음! (" + std::to_string(value) + ")";
        return "";
    }
};

struct WeatherData {
    uint32_t timestamp;
    double temperature;
    double humidity;
    double pressure;
};

static void lesson6_weather_station() {
    printHeader("레슨 6: 실전 — 미니 날씨 관측소");

    // 센서 초기화
    TemperatureSensor tempSensor(23.0);
    HumiditySensor humiSensor(55.0);
    PressureSensor presSensor(1013.0);

    // 필터 초기화
    ExponentialMovingAverage tempFilter(0.3);
    ExponentialMovingAverage humiFilter(0.3);
    ExponentialMovingAverage presFilter(0.3);

    // 이상치 감지 설정
    ThresholdAlert tempAlert{"온도", -10.0, 50.0};
    ThresholdAlert humiAlert{"습도", 10.0, 95.0};
    ThresholdAlert presAlert{"기압", 950.0, 1050.0};

    // 데이터 저장소
    std::vector<WeatherData> dataLog;

    // 시뮬레이션: 20개 샘플 (1초 간격)
    printSubHeader("날씨 관측 시작 (20회 샘플링)");
    std::cout << std::fixed << std::setprecision(1);
    std::cout << "   시간(s)  온도(°C)  습도(%)  기압(hPa)  경보\n";
    std::cout << "   ───────  ────────  ───────  ─────────  ────\n";

    // 시나리오: 15번째 샘플부터 온도가 급상승 (이상치 테스트)
    for (int i = 0; i < 20; i++) {
        // 시나리오 적용
        if (i == 15) {
            tempSensor.setActualTemperature(55.0);  // 갑자기 뜨거워짐!
        }

        // 센서 읽기 + 필터링
        double rawTemp = tempSensor.read();
        double rawHumi = humiSensor.read();
        double rawPres = presSensor.read();

        double filtTemp = tempFilter.update(rawTemp);
        double filtHumi = humiFilter.update(rawHumi);
        double filtPres = presFilter.update(rawPres);

        // 이상치 감지
        std::string alert;
        if (tempAlert.check(filtTemp)) alert += " [!온도]";
        if (humiAlert.check(filtHumi)) alert += " [!습도]";
        if (presAlert.check(filtPres)) alert += " [!기압]";

        // 로그 저장
        dataLog.push_back({static_cast<uint32_t>(i * 1000),
                           filtTemp, filtHumi, filtPres});

        // 화면 표시
        std::cout << "   " << std::setw(5) << (i * 1000) << "ms"
                  << "  " << std::setw(7) << filtTemp
                  << "  " << std::setw(6) << filtHumi
                  << "  " << std::setw(8) << filtPres
                  << "  " << alert << "\n";
    }

    // CSV 저장 시뮬레이션 및 통계
    printSubHeader("CSV 데이터 로그 (처음 3개)");
    std::cout << "  timestamp_ms,temperature_c,humidity_pct,pressure_hpa\n";
    for (size_t i = 0; i < std::min(dataLog.size(), (size_t)3); i++) {
        const auto& d = dataLog[i];
        std::cout << "  " << d.timestamp << "," << std::setprecision(2)
                  << d.temperature << "," << d.humidity << "," << d.pressure << "\n";
    }
    std::cout << "  ... (총 " << dataLog.size() << "개 레코드)\n";

    // 이상치 보고
    int alertCount = 0;
    for (const auto& d : dataLog) {
        if (tempAlert.check(d.temperature)) alertCount++;
    }
    std::cout << "  이상치 발생 횟수: " << alertCount << "회"
              << (alertCount > 0 ? " ← 점검 필요!" : " (정상)") << "\n";
}

// =================================================================
//  메인 함수
// =================================================================
int main() {
    std::cout << R"(
 ╔═══════════════════════════════════════════════════════════════╗
 ║  C++ 임베디드 학습 #31: ADC/DAC와 센서 인터페이스            ║
 ║  (모든 하드웨어는 소프트웨어로 시뮬레이션합니다!)             ║
 ║  ADC: 아날로그→디지털 / DAC: 디지털→아날로그                  ║
 ║  C# 비유: (int)Math.Round(analog) ↔ (float)digital          ║
 ╚═══════════════════════════════════════════════════════════════╝
)";

    /*
    =========================================================================
      레슨별 출력 흐름 가이드 (시뮬레이션)
    =========================================================================
      lesson1 (ADC):
        12비트 ADC: 0~4095 → 0V~3.3V 매핑
        adc_value = 2048 → voltage = 1.65V
        샘플링: 100Hz, 1초 동안 100개 샘플 평균

      lesson2 (DAC):
        12비트 DAC: 0~4095 → 0V~3.3V 출력
        sin파 생성: phase 0~2π, 64샘플/주기
        결과 → 가상 출력 핀에 기록

      lesson3 (센서):
        온도 (LM35): 10mV/°C → ADC → 변환
        가속도 (MPU6050): I2C로 6축 read
        압력 (BMP280): SPI로 레지스터 read

      lesson4 (필터):
        Moving Average: window=10
        EMA (지수이동평균): alpha=0.1
        Kalman: predict → update 사이클
        노이즈 시뮬레이션 → 필터 적용 → 평탄화 결과

      lesson5 (로깅):
        ring buffer로 1초당 100샘플 저장
        디스크 I/O는 별도 스레드 또는 sd card 시뮬

      lesson6 (날씨 관측소):
        통합: 온도+습도+압력 read → 필터 → 저장 → 송신
        1분마다 평균값 보고
    =========================================================================
    */
    lesson1_adc();
    lesson2_dac();
    lesson3_sensors();
    lesson4_filtering();
    lesson5_logging();
    lesson6_weather_station();

    std::cout << "\n";
    std::cout << "================================================================\n";
    std::cout << "  학습 완료! ADC/DAC와 센서의 세계를 탐험했습니다!\n";
    std::cout << "  \n";
    std::cout << "  핵심 요약:\n";
    std::cout << "  1. ADC: 아날로그(전압) → 디지털(숫자) 변환\n";
    std::cout << "  2. DAC: 디지털(숫자) → 아날로그(전압) 변환\n";
    std::cout << "  3. 센서: 물리량 → 전압 → ADC → 숫자\n";
    std::cout << "  4. 필터: 노이즈 제거 (이동평균, EMA, 칼만, 중앙값)\n";
    std::cout << "  5. 로깅: 링버퍼 + 타임스탬프 + 체크섬\n";
    std::cout << "  6. 텔레메트리: 헤더 + 페이로드 + 체크섬 프로토콜\n";
    std::cout << "================================================================\n";

    return 0;
}
