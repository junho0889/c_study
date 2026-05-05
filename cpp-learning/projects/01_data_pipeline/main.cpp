/*
 * ============================================================================
 *  고성능 데이터 수집/처리 파이프라인 (High-Performance Data Pipeline)
 *  컴파일: g++ -std=c++17 -O2 -o data_pipeline main.cpp
 * ============================================================================
 *
 *  이 프로젝트가 보여주는 것:
 *  C++이 데이터 처리에서 C#보다 빠른 이유 3가지
 *    1) 제로카피 파싱: 문자열을 복사하지 않고 원본 메모리를 직접 가리킴
 *    2) 캐시 친화적 메모리: 데이터를 연속된 메모리에 배치하여 CPU 캐시 적중률 극대화
 *    3) GC 없음: C#은 가비지 컬렉터가 갑자기 멈추지만, C++은 멈춤 없이 실시간 처리
 *
 *  데이터 흐름도 (Data Flow Diagram):
 *
 *    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
 *    │  CSV 생성기  │───▶│  링 버퍼     │───▶│   파서      │
 *    │ (센서 시뮬)  │    │ (순환 큐)    │    │ (제로카피)   │
 *    └─────────────┘    └─────────────┘    └─────────────┘
 *                                                │
 *                        ┌───────────────────────┘
 *                        ▼
 *    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
 *    │  필터링      │───▶│  변환        │───▶│  집계/통계   │
 *    │ (이상치제거) │    │ (단위변환)   │    │ (평균/중간값) │
 *    └─────────────┘    └─────────────┘    └─────────────┘
 *                                                │
 *                        ┌───────────────────────┘
 *                        ▼
 *    ┌─────────────┐    ┌─────────────┐
 *    │  CSV 출력    │───▶│  보고서 출력  │
 *    │ (결과저장)   │    │ (콘솔 리포트) │
 *    └─────────────┘    └─────────────┘
 *
 * ============================================================================
 */

// ============================================================================
// #include 설명 (각 헤더파일이 왜 필요한지)
// ============================================================================

// iostream: 화면에 글자를 출력하거나 키보드 입력을 받을 때 사용
// C#의 Console.WriteLine()을 쓰려면 using System; 하는 것과 같습니다
#include <iostream>

// vector: 크기가 자동으로 늘어나는 배열
// C#의 List<T>와 완전히 같은 역할을 합니다!
#include <vector>

// string: 문자열(글자 모음)을 다루는 도구
// C#의 string과 같지만, C++은 값 타입처럼 동작합니다
#include <string>

// string_view: 문자열을 '복사하지 않고' 들여다보는 창문 같은 것
// C#의 ReadOnlySpan<char>과 같습니다 - 원본을 복사하지 않아서 빠릅니다!
#include <string_view>

// sstream: 문자열을 스트림(물 흐르듯이)으로 읽거나 쓸 때 사용
// C#의 StringReader/StringWriter와 비슷합니다
#include <sstream>

// fstream: 파일을 읽거나 쓸 때 사용
// C#의 StreamReader/StreamWriter와 같습니다
#include <fstream>

// algorithm: 정렬, 검색 등 유용한 함수 모음
// C#의 LINQ와 비슷한 역할을 합니다 (sort, find, count 등)
#include <algorithm>

// numeric: 숫자 관련 계산 함수 (합계 구하기 등)
// C#의 Enumerable.Sum(), Enumerable.Aggregate() 같은 것들입니다
#include <numeric>

// cmath: 수학 함수 (제곱근, 절대값 등)
// C#의 Math.Sqrt(), Math.Abs() 같은 것들입니다
#include <cmath>

// random: 난수(무작위 숫자) 생성기
// C#의 Random 클래스와 같습니다
#include <random>

// chrono: 시간 측정 도구 (성능 측정에 사용)
// C#의 Stopwatch와 같은 역할을 합니다
#include <chrono>

// array: 고정 크기 배열 (크기가 변하지 않는 배열)
// C#의 일반 배열 int[]와 같습니다 (크기가 고정)
#include <array>

// functional: 함수를 변수처럼 저장하고 전달할 때 사용
// C#의 Func<>, Action<> 델리게이트와 같습니다
#include <functional>

// iomanip: 출력 형식을 예쁘게 맞출 때 사용 (소수점 자릿수 등)
// C#의 string.Format()이나 $"" 보간 문자열과 비슷합니다
#include <iomanip>

// memory: 스마트 포인터 (자동 메모리 관리)
// C#은 GC가 자동으로 하지만, C++은 unique_ptr로 직접 관리합니다
#include <memory>

// cassert: 프로그램이 올바르게 작동하는지 검증하는 도구
// C#의 Debug.Assert()와 같습니다
#include <cassert>

// ============================================================================
// namespace: C#의 namespace와 완전히 같습니다!
// 이름 충돌을 방지하기 위해 코드를 묶어두는 폴더 같은 것입니다
// ============================================================================
namespace pipeline {

// ============================================================================
// 1단계: 센서 데이터 구조체 정의
// ============================================================================

/*
 *  구조체(struct)는 C#의 struct와 거의 같습니다!
 *  여러 데이터를 하나로 묶는 '상자'라고 생각하면 됩니다.
 *
 *  왜 struct를 쓰는가?
 *  - class 대신 struct를 쓰면 데이터가 '연속된 메모리'에 배치됩니다
 *  - CPU는 연속된 메모리를 읽을 때 훨씬 빠릅니다 (캐시 히트!)
 *  - C#에서 class는 힙에 흩어지지만, C++ struct는 배열에 딱딱 붙어있습니다
 *
 *  메모리 배치 그림:
 *
 *  C++ vector<SensorData>  (연속! CPU가 좋아합니다)
 *  ┌────┬────┬────┬────┬────┬────┐
 *  │ D1 │ D2 │ D3 │ D4 │ D5 │ D6 │  ← 메모리에 줄줄이 붙어있음
 *  └────┴────┴────┴────┴────┴────┘
 *
 *  C# List<SensorData>  (class인 경우, 흩어져있음)
 *  ┌─ptr─┐  ┌─ptr─┐  ┌─ptr─┐
 *  │  ──────▶D1   │  │  ──────▶D3 (어딘가)
 *  │  ──────▶D2   │  │  ──────▶D4 (저 멀리)
 *  └─────┘  └─────┘  └─────┘
 */
struct SensorData {
    int sensor_id;          // 센서 번호 (어떤 센서인지 구분)
    double timestamp;       // 시간 (초 단위, 언제 측정했는지)
    double temperature;     // 온도 (섭씨, 예: 25.3도)
    double humidity;        // 습도 (퍼센트, 예: 60.5%)
    double pressure;        // 기압 (hPa, 예: 1013.25)

    // C#이라면 이렇게 썼을 겁니다:
    // public struct SensorData {
    //     public int SensorId;
    //     public double Timestamp;
    //     ...
    // }
};

// ============================================================================
// 2단계: 링 버퍼 (Ring Buffer / Circular Queue)
// ============================================================================

/*
 *  링 버퍼란?
 *  둥근 원 모양의 버퍼(임시 저장소)입니다.
 *  데이터가 가득 차면 가장 오래된 데이터를 덮어씁니다.
 *  실시간 센서 데이터처럼 끊임없이 들어오는 데이터를 처리할 때 사용합니다.
 *
 *  C#에는 기본으로 제공되지 않아서 직접 만들어야 합니다.
 *  (C# Channel<T>이 비슷하지만 정확히 같지는 않습니다)
 *
 *  동작 원리 그림:
 *
 *  처음 (비어있음):        데이터 3개 추가 후:     가득 찬 후 (덮어쓰기):
 *  ┌───┬───┬───┬───┐      ┌───┬───┬───┬───┐      ┌───┬───┬───┬───┐
 *  │   │   │   │   │      │ A │ B │ C │   │      │ E │ B │ C │ D │
 *  └───┴───┴───┴───┘      └───┴───┴───┴───┘      └───┴───┴───┴───┘
 *   ^                       ^           ^              ^   ^
 *   head=tail              head        tail           tail head
 *
 *  template은 C#의 제네릭(Generic)과 같은 개념입니다
 *  RingBuffer<int>는 C#의 RingBuffer<int>와 같은 문법입니다!
 */
template<typename T, size_t Capacity>
class RingBuffer {
private:
    // std::array는 C#의 고정크기 배열(int[])과 같습니다
    // 크기가 컴파일 시점에 정해져서 힙 할당이 필요 없어 빠릅니다
    std::array<T, Capacity> buffer_;

    size_t head_ = 0;   // 읽을 위치 (가장 오래된 데이터)
    size_t tail_ = 0;   // 쓸 위치 (새 데이터가 들어갈 곳)
    size_t count_ = 0;  // 현재 저장된 데이터 개수

public:
    // push: 데이터를 링 버퍼에 넣기
    // const T& 는 C#의 in 매개변수처럼 '읽기전용 참조'입니다
    // 데이터를 복사하지 않고 원본을 참조만 합니다 → 빠릅니다!
    void push(const T& item) {
        buffer_[tail_] = item;
        // % (나머지 연산)으로 원형으로 돌아가게 만듭니다
        // 예: tail이 3이고 Capacity가 4이면, (3+1)%4 = 0 → 처음으로!
        tail_ = (tail_ + 1) % Capacity;

        if (count_ == Capacity) {
            // 가득 찼으면 head도 앞으로 이동 (가장 오래된 데이터 버림)
            head_ = (head_ + 1) % Capacity;
        } else {
            count_++;
        }
    }

    // pop: 가장 오래된 데이터를 꺼내기
    // 반환값이 bool인 이유: 버퍼가 비어있으면 false를 반환하기 위해
    // C#이라면 bool TryDequeue(out T result) 패턴과 같습니다
    bool pop(T& out) {
        if (count_ == 0) return false;
        out = buffer_[head_];
        head_ = (head_ + 1) % Capacity;
        count_--;
        return true;
    }

    // 현재 저장된 데이터 개수 반환
    // C#의 Count 프로퍼티와 같습니다
    size_t size() const { return count_; }

    // 버퍼가 비어있는지 확인
    // C#에서 queue.Count == 0 확인하는 것과 같습니다
    bool empty() const { return count_ == 0; }

    // 버퍼가 가득 찼는지 확인
    bool full() const { return count_ == Capacity; }

    // 모든 데이터를 vector로 복사하여 꺼내기
    // C#의 ToList()와 비슷합니다
    std::vector<T> drain() {
        std::vector<T> result;
        // reserve: 미리 메모리를 확보합니다
        // C#의 new List<T>(capacity) 생성자와 같습니다
        // 이렇게 하면 vector가 커질 때마다 재할당하는 것을 방지합니다
        result.reserve(count_);
        T item;
        while (pop(item)) {
            // std::move는 C#에는 없는 개념입니다
            // C#은 GC가 알아서 하지만, C++은 직접 '이사'시켜야 합니다
            // 데이터를 '복사' 대신 '이동'해서 성능을 높입니다
            result.push_back(std::move(item));
        }
        return result;
    }
};

// ============================================================================
// 3단계: CSV 데이터 생성기 (센서/IoT 데이터 시뮬레이션)
// ============================================================================

/*
 *  왜 이 함수가 필요한가?
 *  실제 센서 데이터 대신 가짜(시뮬레이션) 데이터를 만들어서
 *  파이프라인을 테스트합니다. 실제 현장에서도 테스트용 데이터 생성기는 필수입니다.
 *
 *  생성되는 데이터 형태:
 *  sensor_id, timestamp, temperature, humidity, pressure
 *  1, 0.001, 23.5, 55.2, 1013.1
 *  2, 0.002, 24.1, 58.7, 1012.8
 *  ...
 */
class DataGenerator {
private:
    // mt19937: 고품질 난수 생성기 (메르센 트위스터 알고리즘)
    // C#의 Random보다 훨씬 고품질의 난수를 생성합니다
    std::mt19937 rng_;

    // normal_distribution: 정규분포(종 모양 분포)로 난수 생성
    // 실제 센서 데이터는 평균값 근처에 몰려있으므로 정규분포가 현실적입니다
    // C#에는 기본 제공되지 않아서 Box-Muller 변환을 직접 구현해야 합니다
    std::normal_distribution<double> temp_dist_;      // 온도 분포
    std::normal_distribution<double> humidity_dist_;   // 습도 분포
    std::normal_distribution<double> pressure_dist_;   // 기압 분포

    // uniform_int_distribution: 균등분포 정수 난수
    // C#의 Random.Next(min, max)와 같습니다
    std::uniform_int_distribution<int> sensor_id_dist_;

    int num_sensors_; // 센서 개수

public:
    // 생성자: 평균값과 표준편차를 설정합니다
    // explicit은 "이 생성자를 자동 형변환에 쓰지 마세요"라는 뜻입니다
    // C#에도 explicit 키워드가 있지만 연산자에 사용합니다
    explicit DataGenerator(int num_sensors = 100, unsigned int seed = 42)
        : rng_(seed)
        , temp_dist_(25.0, 5.0)       // 평균 25도, 표준편차 5도
        , humidity_dist_(60.0, 15.0)   // 평균 60%, 표준편차 15%
        , pressure_dist_(1013.25, 10.0) // 평균 1013.25hPa, 표준편차 10
        , sensor_id_dist_(1, num_sensors)
        , num_sensors_(num_sensors)
    {}

    // 하나의 센서 데이터 생성
    SensorData generate_one(double timestamp) {
        return SensorData{
            sensor_id_dist_(rng_),    // 랜덤 센서 ID
            timestamp,                // 시간
            temp_dist_(rng_),         // 랜덤 온도
            humidity_dist_(rng_),     // 랜덤 습도
            pressure_dist_(rng_)      // 랜덤 기압
        };
    }

    // 대량의 센서 데이터 생성
    // count개의 데이터를 벡터(동적 배열)에 담아 반환합니다
    std::vector<SensorData> generate_batch(size_t count) {
        std::vector<SensorData> data;
        data.reserve(count); // 미리 메모리 확보 (C#의 Capacity 설정과 같음)

        for (size_t i = 0; i < count; ++i) {
            double timestamp = static_cast<double>(i) * 0.001; // 1ms 간격
            // emplace_back: push_back보다 빠릅니다!
            // 객체를 밖에서 만들어 넣는 대신, 벡터 안에서 직접 생성합니다
            // C#에는 이런 최적화가 없습니다 - GC가 알아서 관리하니까요
            data.emplace_back(generate_one(timestamp));
        }
        return data;
    }

    // CSV 문자열로 데이터 생성 (파일 저장 또는 파싱 테스트용)
    std::string generate_csv(size_t count) {
        // ostringstream은 C#의 StringBuilder와 같습니다!
        // 문자열을 반복해서 붙일 때 매우 효율적입니다
        std::ostringstream oss;

        // CSV 헤더 (첫 번째 줄)
        oss << "sensor_id,timestamp,temperature,humidity,pressure\n";

        // std::fixed와 std::setprecision은 소수점 자릿수를 고정합니다
        // C#의 .ToString("F3")과 같습니다
        oss << std::fixed << std::setprecision(3);

        for (size_t i = 0; i < count; ++i) {
            double ts = static_cast<double>(i) * 0.001;
            auto d = generate_one(ts);
            oss << d.sensor_id << ","
                << d.timestamp << ","
                << d.temperature << ","
                << d.humidity << ","
                << d.pressure << "\n";
        }
        return oss.str(); // 완성된 문자열 반환
    }
};

// ============================================================================
// 4단계: 제로카피 CSV 파서 (Zero-Copy Parser)
// ============================================================================

/*
 *  "제로카피"란?
 *  문자열을 파싱할 때 새로운 문자열을 '복사'해서 만들지 않고,
 *  원본 문자열의 특정 부분을 '가리키기만' 하는 기법입니다.
 *
 *  비유: 책에서 중요한 부분을 찾을 때
 *  - 복사 방식: 중요한 문장을 노트에 베껴 적기 (느림, 종이 낭비)
 *  - 제로카피: 책에 포스트잇을 붙여서 표시만 하기 (빠름, 낭비 없음!)
 *
 *  C#에서는 Span<T>과 ReadOnlySpan<T>이 비슷한 역할을 합니다
 *  하지만 C++의 string_view가 훨씬 오래전부터 있었고, 더 자연스럽습니다
 *
 *  메모리 비교:
 *
 *  일반 파싱 (복사 발생):
 *  원본: "23.5,60.2,1013.1"
 *         ↓ ↓ ↓ (각각 새 메모리 할당 + 복사)
 *  copy1: "23.5"    copy2: "60.2"    copy3: "1013.1"
 *
 *  제로카피 파싱 (포인터만 저장):
 *  원본: "23.5,60.2,1013.1"
 *         ^──^  ^──^  ^────^
 *  view1: ┘  ┘  ┘  ┘  ┘    ┘  ← 원본 메모리를 그냥 가리킴!
 */
class ZeroCopyParser {
public:
    // CSV 한 줄을 파싱하여 SensorData로 변환합니다
    // string_view는 문자열을 복사하지 않고 들여다보는 '창문'입니다
    // C#의 ReadOnlySpan<char>과 같습니다
    static bool parse_line(std::string_view line, SensorData& out) {
        // 빈 줄이나 헤더는 건너뜁니다
        if (line.empty() || line[0] == 's') return false;

        // 쉼표(,) 위치를 찾아서 각 필드를 분리합니다
        // C#이라면 line.Split(',')을 쓰겠지만,
        // 그러면 Split이 새 배열과 새 문자열들을 만들어서 GC 부담이 생깁니다
        size_t pos = 0;
        int field = 0;

        // 각 필드의 시작 위치와 길이를 저장 (복사 없이!)
        // 이것이 바로 '제로카피'입니다
        std::string_view fields[5];

        size_t start = 0;
        for (size_t i = 0; i <= line.size(); ++i) {
            if (i == line.size() || line[i] == ',') {
                if (field < 5) {
                    // substr은 새 문자열을 만들지 않습니다!
                    // string_view의 substr은 원본의 일부를 가리키는 새 뷰만 만듭니다
                    fields[field] = line.substr(start, i - start);
                    field++;
                }
                start = i + 1;
            }
        }

        if (field != 5) return false; // 필드가 5개가 아니면 잘못된 데이터

        // 문자열을 숫자로 변환합니다
        // C#의 int.Parse(), double.Parse()와 같습니다
        // 여기서는 어쩔 수 없이 임시 string을 만듭니다 (stoi/stod가 string_view를 안 받아서)
        try {
            out.sensor_id   = std::stoi(std::string(fields[0]));
            out.timestamp   = std::stod(std::string(fields[1]));
            out.temperature = std::stod(std::string(fields[2]));
            out.humidity    = std::stod(std::string(fields[3]));
            out.pressure    = std::stod(std::string(fields[4]));
        } catch (...) {
            // 숫자 변환 실패시 false 반환
            // C#이라면 double.TryParse()를 쓰겠지만, C++은 try-catch를 씁니다
            return false;
        }
        return true;
    }

    // CSV 전체를 파싱하여 SensorData 벡터로 변환
    // const std::string& 는 C#의 in string과 비슷합니다 (읽기전용 참조)
    static std::vector<SensorData> parse_csv(const std::string& csv_data) {
        std::vector<SensorData> result;

        // string_view로 원본 CSV를 가리킵니다 (복사 없음!)
        std::string_view view(csv_data);

        size_t line_start = 0;
        for (size_t i = 0; i <= view.size(); ++i) {
            if (i == view.size() || view[i] == '\n') {
                // 한 줄씩 잘라서 파싱합니다
                auto line = view.substr(line_start, i - line_start);

                // \r 제거 (윈도우 줄바꿈 처리)
                if (!line.empty() && line.back() == '\r') {
                    line.remove_suffix(1);
                }

                SensorData data;
                if (parse_line(line, data)) {
                    result.push_back(data);
                }
                line_start = i + 1;
            }
        }
        return result;
    }
};

// ============================================================================
// 5단계: 파이프라인 스테이지들 (Processing Pipeline Stages)
// ============================================================================

/*
 *  파이프라인이란?
 *  수도관처럼 데이터가 한 단계씩 흘러가면서 처리되는 구조입니다.
 *  각 단계는 하나의 일만 합니다 (단일 책임 원칙 - C#의 SOLID 원칙과 같음!)
 *
 *  Read → Parse → Filter → Transform → Aggregate → Output
 *   (읽기)  (해석)  (걸러내기) (변환)     (통계)    (출력)
 */

// --- 5-1: 필터 (Filter Stage) ---

/*
 *  왜 필터링이 필요한가?
 *  센서 데이터에는 이상치(outlier)가 있을 수 있습니다.
 *  예: 센서 고장으로 온도가 -999도로 기록되는 경우
 *  이런 비정상 데이터를 걸러내야 정확한 분석이 가능합니다.
 *
 *  C#이라면 data.Where(d => d.Temperature > -50).ToList() 쓰겠지만,
 *  C++에서는 직접 구현하거나 std::copy_if를 사용합니다
 */
class DataFilter {
public:
    // 유효한 범위 안에 있는 데이터만 남깁니다
    // std::function은 C#의 Func<> 델리게이트와 같습니다!
    // 어떤 함수든 받을 수 있는 '만능 함수 보관함'입니다
    using Predicate = std::function<bool(const SensorData&)>;

    // 기본 필터: 물리적으로 말이 되는 범위만 통과
    static std::vector<SensorData> filter_valid(const std::vector<SensorData>& data) {
        std::vector<SensorData> result;
        result.reserve(data.size()); // 최대 크기 미리 확보 (재할당 방지)

        // std::copy_if는 C#의 Where()와 같습니다!
        // 조건을 만족하는 요소만 복사합니다
        std::copy_if(data.begin(), data.end(), std::back_inserter(result),
            // [](...)는 람다 함수입니다 - C#의 (d) => ... 와 같습니다!
            [](const SensorData& d) {
                return d.temperature > -50.0 && d.temperature < 60.0  // 온도: -50~60도
                    && d.humidity >= 0.0     && d.humidity <= 100.0    // 습도: 0~100%
                    && d.pressure > 900.0    && d.pressure < 1100.0;  // 기압: 900~1100hPa
            }
        );
        return result;
    }

    // 사용자 정의 필터: 원하는 조건을 자유롭게 지정
    static std::vector<SensorData> filter_by(
        const std::vector<SensorData>& data,
        Predicate pred  // C#의 Func<SensorData, bool>과 같습니다
    ) {
        std::vector<SensorData> result;
        result.reserve(data.size());
        std::copy_if(data.begin(), data.end(), std::back_inserter(result), pred);
        return result;
    }
};

// --- 5-2: 변환기 (Transform Stage) ---

/*
 *  왜 변환이 필요한가?
 *  센서에서 온 '원시 데이터'를 사용하기 좋은 형태로 바꿉니다.
 *  예: 섭씨→화씨 변환, 단위 변환, 보정값 적용 등
 *
 *  C#이라면 data.Select(d => new {...}).ToList() 와 같습니다
 */
class DataTransformer {
public:
    // 섭씨를 화씨로 변환한 '추가 필드'를 가진 결과 구조체
    struct TransformedData {
        SensorData original;     // 원본 데이터 보존
        double temp_fahrenheit;  // 화씨 온도
        double heat_index;       // 체감온도 (온도+습도 조합)
        double dew_point;        // 이슬점 (결로가 생기는 온도)
    };

    // 데이터 변환 함수
    static std::vector<TransformedData> transform(const std::vector<SensorData>& data) {
        std::vector<TransformedData> result;
        result.reserve(data.size());

        for (const auto& d : data) {
            // auto&는 C#의 var와 비슷합니다 (타입을 자동으로 추론)
            // const는 "이 변수를 바꾸지 않겠다"는 약속입니다
            TransformedData td;
            td.original = d;

            // 섭씨 → 화씨 변환 공식: F = C × 9/5 + 32
            td.temp_fahrenheit = d.temperature * 9.0 / 5.0 + 32.0;

            // 체감온도 계산 (간단한 근사식)
            // 실제로는 더 복잡하지만, 학습 목적으로 간단한 공식을 사용합니다
            td.heat_index = d.temperature + 0.33 * (d.humidity / 100.0 * 6.105
                * std::exp(17.27 * d.temperature / (237.7 + d.temperature))) - 4.0;

            // 이슬점 계산 (Magnus 공식의 간단 버전)
            double alpha = std::log(d.humidity / 100.0)
                + (17.27 * d.temperature) / (237.7 + d.temperature);
            td.dew_point = (237.7 * alpha) / (17.27 - alpha);

            result.push_back(td);
        }
        return result;
    }
};

// ============================================================================
// 6단계: 통계 분석 엔진 (Statistical Analysis Engine)
// ============================================================================

/*
 *  왜 C++로 통계 분석을 하는가?
 *  - C#의 LINQ는 편리하지만, 대량 데이터에서 느립니다 (박싱/언박싱, GC 오버헤드)
 *  - C++은 데이터가 연속 메모리에 있어서 CPU 캐시를 최대한 활용합니다
 *  - 수백만 건의 데이터를 실시간으로 분석해야 하는 경우 C++이 압도적입니다
 *
 *  template<typename T>는 C#의 <T> 제네릭과 같습니다
 *  어떤 타입이든 받을 수 있는 '틀'을 만듭니다
 */
class StatisticsEngine {
public:
    // 통계 결과를 담는 구조체
    struct Stats {
        double mean;        // 평균 (모든 값의 합 ÷ 개수)
        double median;      // 중간값 (정렬했을 때 가운데 값)
        double std_dev;     // 표준편차 (값들이 평균에서 얼마나 퍼져있는지)
        double min_val;     // 최솟값
        double max_val;     // 최댓값
        double p25;         // 25번째 백분위수 (하위 25% 지점의 값)
        double p75;         // 75번째 백분위수 (하위 75% 지점의 값)
        double p90;         // 90번째 백분위수
        double p99;         // 99번째 백분위수
        size_t count;       // 데이터 개수
    };

    // 값 추출 함수를 받아서 통계를 계산합니다
    // std::function<double(const SensorData&)>는
    // C#의 Func<SensorData, double>과 같습니다
    // 예: [](const SensorData& d) { return d.temperature; }
    //     → C#: (SensorData d) => d.Temperature
    static Stats compute(
        const std::vector<SensorData>& data,
        std::function<double(const SensorData&)> extractor
    ) {
        Stats stats{};
        stats.count = data.size();

        if (data.empty()) return stats;

        // 1단계: 분석할 값들만 뽑아서 별도 벡터에 저장
        std::vector<double> values;
        values.reserve(data.size());
        for (const auto& d : data) {
            values.push_back(extractor(d));
        }

        // 2단계: 정렬 (중간값, 백분위수 계산에 필요)
        // std::sort는 C#의 List.Sort()와 같지만, 보통 더 빠릅니다
        // 인트로소트(Introsort) 알고리즘을 사용하여 O(n log n) 보장
        std::sort(values.begin(), values.end());

        // 3단계: 합계 계산
        // std::accumulate는 C#의 Enumerable.Sum()과 같습니다
        double sum = std::accumulate(values.begin(), values.end(), 0.0);

        // 4단계: 평균 계산
        stats.mean = sum / static_cast<double>(stats.count);

        // 5단계: 중간값(Median) 계산
        // 데이터 개수가 짝수면 가운데 두 값의 평균
        // 데이터 개수가 홀수면 정확히 가운데 값
        size_t n = values.size();
        if (n % 2 == 0) {
            stats.median = (values[n/2 - 1] + values[n/2]) / 2.0;
        } else {
            stats.median = values[n/2];
        }

        // 6단계: 표준편차 계산
        // 표준편차 = √(각 값과 평균의 차이의 제곱의 평균)
        // 쉽게 말하면: "값들이 평균에서 얼마나 멀리 퍼져있나"를 숫자로 표현
        double sq_sum = 0.0;
        for (double v : values) {
            double diff = v - stats.mean;
            sq_sum += diff * diff;
        }
        stats.std_dev = std::sqrt(sq_sum / static_cast<double>(stats.count));

        // 7단계: 최솟값, 최댓값 (이미 정렬되어 있으므로 양 끝에 있음)
        stats.min_val = values.front(); // C#의 First()와 같습니다
        stats.max_val = values.back();  // C#의 Last()와 같습니다

        // 8단계: 백분위수 계산
        // 백분위수란: 데이터를 작은 것부터 나열했을 때, 해당 %에 해당하는 값
        // 예: P90 = 90번째 백분위수 = "90%의 데이터가 이 값보다 작다"
        stats.p25 = percentile(values, 25.0);
        stats.p75 = percentile(values, 75.0);
        stats.p90 = percentile(values, 90.0);
        stats.p99 = percentile(values, 99.0);

        return stats;
    }

private:
    // 백분위수를 계산하는 헬퍼 함수
    // 이미 정렬된 벡터를 받습니다
    static double percentile(const std::vector<double>& sorted_values, double p) {
        if (sorted_values.empty()) return 0.0;

        // 인덱스 계산: p/100 * (n-1)
        double index = (p / 100.0) * static_cast<double>(sorted_values.size() - 1);
        size_t lower = static_cast<size_t>(std::floor(index));
        size_t upper = static_cast<size_t>(std::ceil(index));

        if (lower == upper) return sorted_values[lower];

        // 선형 보간 (두 값 사이의 중간값을 구함)
        double fraction = index - static_cast<double>(lower);
        return sorted_values[lower] * (1.0 - fraction) + sorted_values[upper] * fraction;
    }
};

// ============================================================================
// 7단계: 결과 출력기 (Output Stage)
// ============================================================================

/*
 *  파이프라인의 마지막 단계: 결과를 사람이 읽을 수 있는 형태로 출력합니다.
 *  1) CSV 파일로 저장 (다른 프로그램에서 사용 가능)
 *  2) 콘솔에 보고서 출력 (바로 확인 가능)
 */
class ReportGenerator {
public:
    // 통계 결과를 보기 좋게 콘솔에 출력합니다
    static void print_stats(const std::string& name, const StatisticsEngine::Stats& stats) {
        // std::setw는 출력 너비를 맞춥니다 (표 형식으로 정렬)
        // C#의 PadLeft(), PadRight()와 비슷합니다
        std::cout << "\n  === " << name << " 통계 ===" << "\n"
                  << std::fixed << std::setprecision(2)
                  << "  데이터 수: " << stats.count << "\n"
                  << "  평균:      " << std::setw(10) << stats.mean << "\n"
                  << "  중간값:    " << std::setw(10) << stats.median << "\n"
                  << "  표준편차:  " << std::setw(10) << stats.std_dev << "\n"
                  << "  최솟값:    " << std::setw(10) << stats.min_val << "\n"
                  << "  최댓값:    " << std::setw(10) << stats.max_val << "\n"
                  << "  P25:       " << std::setw(10) << stats.p25 << "\n"
                  << "  P75:       " << std::setw(10) << stats.p75 << "\n"
                  << "  P90:       " << std::setw(10) << stats.p90 << "\n"
                  << "  P99:       " << std::setw(10) << stats.p99 << "\n";
    }

    // 변환된 데이터를 CSV 파일로 저장합니다
    static bool export_csv(
        const std::string& filename,
        const std::vector<DataTransformer::TransformedData>& data
    ) {
        // ofstream은 C#의 StreamWriter와 같습니다
        std::ofstream file(filename);
        if (!file.is_open()) {
            std::cerr << "파일 열기 실패: " << filename << "\n";
            return false;
        }

        // CSV 헤더 쓰기
        file << "sensor_id,timestamp,temp_c,temp_f,humidity,pressure,heat_index,dew_point\n";
        file << std::fixed << std::setprecision(3);

        for (const auto& td : data) {
            const auto& d = td.original;
            file << d.sensor_id << ","
                 << d.timestamp << ","
                 << d.temperature << ","
                 << td.temp_fahrenheit << ","
                 << d.humidity << ","
                 << d.pressure << ","
                 << td.heat_index << ","
                 << td.dew_point << "\n";
        }

        // C#에서는 using문으로 자동 닫히지만
        // C++에서는 ofstream이 소멸자(destructor)에서 자동으로 닫힙니다
        // RAII(Resource Acquisition Is Initialization) 패턴이라고 합니다
        // C#의 IDisposable + using 패턴과 비슷하지만, C++이 원조입니다!
        return true;
    }

    // 종합 보고서를 콘솔에 출력합니다
    static void print_summary_report(
        size_t total_generated,
        size_t after_filter,
        const StatisticsEngine::Stats& temp_stats,
        const StatisticsEngine::Stats& humidity_stats,
        const StatisticsEngine::Stats& pressure_stats
    ) {
        std::cout << "\n"
                  << "╔══════════════════════════════════════════════════╗\n"
                  << "║      데이터 파이프라인 종합 보고서               ║\n"
                  << "╠══════════════════════════════════════════════════╣\n"
                  << "║                                                  ║\n"
                  << "║  생성된 데이터:  " << std::setw(8) << total_generated << " 건"
                  << std::string(20 - std::to_string(total_generated).length(), ' ') << "║\n"
                  << "║  필터 후 데이터: " << std::setw(8) << after_filter << " 건"
                  << std::string(20 - std::to_string(after_filter).length(), ' ') << "║\n"
                  << "║  필터링 비율:    " << std::setw(7) << std::fixed << std::setprecision(1)
                  << (100.0 * static_cast<double>(after_filter) / static_cast<double>(total_generated))
                  << "%                  ║\n"
                  << "║                                                  ║\n"
                  << "╚══════════════════════════════════════════════════╝\n";

        print_stats("온도 (Temperature)", temp_stats);
        print_stats("습도 (Humidity)", humidity_stats);
        print_stats("기압 (Pressure)", pressure_stats);
    }
};

// ============================================================================
// 8단계: 성능 측정기 (Performance Benchmark)
// ============================================================================

/*
 *  왜 성능을 측정하는가?
 *  C++을 쓰는 이유가 "빠르니까"인데, 실제로 얼마나 빠른지 증명해야 합니다!
 *  서로 다른 처리 방식의 속도를 비교합니다.
 *
 *  chrono는 C#의 Stopwatch와 같은 역할을 합니다
 *  하지만 C++의 chrono는 나노초(ns) 단위까지 정밀하게 측정 가능합니다
 */
class Benchmark {
public:
    // 함수의 실행 시간을 측정하고 결과를 반환합니다
    // template<typename Func>은 C#의 제네릭처럼 어떤 함수든 받을 수 있게 합니다
    // 하지만 C++ 템플릿은 컴파일 시점에 결정되어 가상 호출 오버헤드가 없습니다!
    // C#의 Func<>은 런타임 델리게이트라서 약간의 오버헤드가 있습니다
    template<typename Func>
    static double measure_ms(const std::string& label, Func&& func) {
        // high_resolution_clock: 가장 정밀한 시계
        // C#의 Stopwatch.StartNew()와 같습니다
        auto start = std::chrono::high_resolution_clock::now();

        // std::forward는 C#에 없는 개념입니다
        // 전달받은 함수를 '완벽하게 전달(perfect forwarding)'합니다
        // 쉽게 말하면 "받은 그대로 넘겨주기"입니다
        func();

        auto end = std::chrono::high_resolution_clock::now();

        // duration_cast: 시간 차이를 원하는 단위로 변환
        // C#의 elapsed.TotalMilliseconds와 같습니다
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        double ms = static_cast<double>(duration.count()) / 1000.0;

        std::cout << "  [성능] " << std::setw(35) << std::left << label
                  << std::right << std::fixed << std::setprecision(3)
                  << std::setw(10) << ms << " ms\n";
        return ms;
    }
};

// ============================================================================
// 9단계: 전체 파이프라인 오케스트레이터
// ============================================================================

/*
 *  오케스트레이터란?
 *  오케스트라의 지휘자처럼, 모든 파이프라인 단계를 순서대로 실행하고
 *  조율하는 역할을 합니다.
 *
 *  C#이라면 이런 식이었을 겁니다:
 *  var data = generator.Generate(count)
 *      .Where(IsValid)
 *      .Select(Transform)
 *      .ToList();
 *  // LINQ 체이닝과 비슷한 개념이지만, C++은 각 단계를 명시적으로 호출합니다
 */
class PipelineOrchestrator {
public:
    // 전체 파이프라인 실행
    static void run(size_t data_count) {
        std::cout << "\n"
                  << "====================================================\n"
                  << "  고성능 데이터 수집/처리 파이프라인 시작\n"
                  << "  데이터 수: " << data_count << "\n"
                  << "====================================================\n\n";

        // ----------------------------------------------------------
        // 접근법 1: 구조체 배열 (Structure of Arrays 와 대비되는 AoS)
        //           모든 단계를 순서대로 실행
        // ----------------------------------------------------------
        std::cout << "--- 접근법 1: 전체 파이프라인 (CSV 생성 → 파싱 → 처리) ---\n";

        std::string csv_data;
        std::vector<SensorData> parsed_data;
        std::vector<SensorData> filtered_data;
        std::vector<DataTransformer::TransformedData> transformed_data;

        // 1단계: CSV 데이터 생성
        // C#: var csvData = generator.GenerateCsv(count);
        double gen_time = Benchmark::measure_ms("CSV 데이터 생성", [&]() {
            DataGenerator gen(100);
            csv_data = gen.generate_csv(data_count);
        });

        // 2단계: CSV 파싱 (제로카피)
        // C#: var parsedData = CsvParser.Parse(csvData);
        double parse_time = Benchmark::measure_ms("CSV 제로카피 파싱", [&]() {
            parsed_data = ZeroCopyParser::parse_csv(csv_data);
        });

        // 3단계: 데이터 필터링 (이상치 제거)
        // C#: var filteredData = parsedData.Where(IsValid).ToList();
        double filter_time = Benchmark::measure_ms("데이터 필터링", [&]() {
            filtered_data = DataFilter::filter_valid(parsed_data);
        });

        // 4단계: 데이터 변환 (섭씨→화씨, 체감온도 등)
        // C#: var transformedData = filteredData.Select(Transform).ToList();
        double transform_time = Benchmark::measure_ms("데이터 변환", [&]() {
            transformed_data = DataTransformer::transform(filtered_data);
        });

        // 5단계: 통계 분석
        StatisticsEngine::Stats temp_stats, humidity_stats, pressure_stats;
        double stats_time = Benchmark::measure_ms("통계 분석", [&]() {
            // 람다로 원하는 필드를 추출합니다
            // C#: stats = ComputeStats(data, d => d.Temperature);
            temp_stats = StatisticsEngine::compute(filtered_data,
                [](const SensorData& d) { return d.temperature; });

            humidity_stats = StatisticsEngine::compute(filtered_data,
                [](const SensorData& d) { return d.humidity; });

            pressure_stats = StatisticsEngine::compute(filtered_data,
                [](const SensorData& d) { return d.pressure; });
        });

        // 6단계: CSV 파일 출력
        double export_time = Benchmark::measure_ms("CSV 파일 출력", [&]() {
            ReportGenerator::export_csv("pipeline_output.csv", transformed_data);
        });

        // 전체 시간 합계
        double total_time = gen_time + parse_time + filter_time
                          + transform_time + stats_time + export_time;

        std::cout << "  ────────────────────────────────────────────\n"
                  << "  [성능] " << std::setw(35) << std::left << "전체 파이프라인"
                  << std::right << std::fixed << std::setprecision(3)
                  << std::setw(10) << total_time << " ms\n";

        // 종합 보고서 출력
        ReportGenerator::print_summary_report(
            data_count, filtered_data.size(),
            temp_stats, humidity_stats, pressure_stats
        );

        // ----------------------------------------------------------
        // 접근법 2: 직접 생성 (CSV 문자열 거치지 않음)
        //           CSV 단계를 건너뛰고 구조체를 직접 생성
        // ----------------------------------------------------------
        std::cout << "\n--- 접근법 2: 직접 생성 (CSV 없이, 메모리에서 바로 처리) ---\n";

        std::vector<SensorData> direct_data;
        std::vector<SensorData> direct_filtered;

        double direct_gen = Benchmark::measure_ms("직접 데이터 생성", [&]() {
            DataGenerator gen(100);
            direct_data = gen.generate_batch(data_count);
        });

        double direct_filter = Benchmark::measure_ms("직접 필터링", [&]() {
            direct_filtered = DataFilter::filter_valid(direct_data);
        });

        StatisticsEngine::Stats direct_temp_stats;
        double direct_stats = Benchmark::measure_ms("직접 통계 분석", [&]() {
            direct_temp_stats = StatisticsEngine::compute(direct_filtered,
                [](const SensorData& d) { return d.temperature; });
        });

        double direct_total = direct_gen + direct_filter + direct_stats;
        std::cout << "  ────────────────────────────────────────────\n"
                  << "  [성능] " << std::setw(35) << std::left << "직접 처리 전체"
                  << std::right << std::fixed << std::setprecision(3)
                  << std::setw(10) << direct_total << " ms\n";

        // ----------------------------------------------------------
        // 접근법 3: 링 버퍼를 이용한 스트리밍 처리
        //           실시간 센서 데이터 수집 시뮬레이션
        // ----------------------------------------------------------
        std::cout << "\n--- 접근법 3: 링 버퍼 스트리밍 처리 ---\n";

        // 링 버퍼 크기 1024: 2의 거듭제곱으로 하면 % 연산이 빠릅니다
        // 컴파일러가 % 대신 비트 연산(&)으로 최적화할 수 있기 때문입니다
        RingBuffer<SensorData, 1024> ring_buffer;
        DataGenerator stream_gen(50, 12345);
        size_t processed_count = 0;
        double running_sum = 0.0;

        double stream_time = Benchmark::measure_ms("링 버퍼 스트리밍", [&]() {
            // 센서 데이터가 끊임없이 들어오는 상황을 시뮬레이션합니다
            for (size_t i = 0; i < data_count; ++i) {
                double ts = static_cast<double>(i) * 0.001;
                auto sample = stream_gen.generate_one(ts);

                // 링 버퍼에 데이터를 넣습니다
                ring_buffer.push(sample);

                // 버퍼가 가득 차면 배치 처리합니다
                // 이것이 실시간 시스템에서 흔히 쓰는 패턴입니다:
                // "데이터가 일정량 모이면 한꺼번에 처리"
                if (ring_buffer.full()) {
                    auto batch = ring_buffer.drain();
                    for (const auto& d : batch) {
                        if (d.temperature > -50.0 && d.temperature < 60.0) {
                            running_sum += d.temperature;
                            processed_count++;
                        }
                    }
                }
            }

            // 남은 데이터 처리
            auto remaining = ring_buffer.drain();
            for (const auto& d : remaining) {
                if (d.temperature > -50.0 && d.temperature < 60.0) {
                    running_sum += d.temperature;
                    processed_count++;
                }
            }
        });

        double stream_avg = (processed_count > 0)
            ? running_sum / static_cast<double>(processed_count) : 0.0;
        std::cout << "  스트리밍 처리 결과: " << processed_count << "건 처리, "
                  << "평균 온도: " << std::fixed << std::setprecision(2)
                  << stream_avg << "도\n";

        // ----------------------------------------------------------
        // 성능 비교 요약
        // ----------------------------------------------------------
        std::cout << "\n"
                  << "╔══════════════════════════════════════════════════╗\n"
                  << "║              성능 비교 요약                     ║\n"
                  << "╠══════════════════════════════════════════════════╣\n"
                  << std::fixed << std::setprecision(3)
                  << "║  CSV 파이프라인 전체:  " << std::setw(10) << total_time       << " ms      ║\n"
                  << "║  직접 처리 전체:       " << std::setw(10) << direct_total     << " ms      ║\n"
                  << "║  링 버퍼 스트리밍:     " << std::setw(10) << stream_time      << " ms      ║\n"
                  << "╠══════════════════════════════════════════════════╣\n";

        if (total_time > 0 && direct_total > 0) {
            double speedup = total_time / direct_total;
            std::cout << "║  직접 처리가 CSV 대비 " << std::setw(5) << std::setprecision(1)
                      << speedup << "배 빠름            ║\n";
        }

        std::cout << "╠══════════════════════════════════════════════════╣\n"
                  << "║                                                  ║\n"
                  << "║  왜 C++인가?                                     ║\n"
                  << "║  - 제로카피 파싱: 메모리 복사 최소화              ║\n"
                  << "║  - 연속 메모리: CPU 캐시 적중률 극대화            ║\n"
                  << "║  - GC 없음: 실시간 처리 중 멈춤 없음             ║\n"
                  << "║  - 컴파일 최적화: -O2로 자동 벡터화 가능         ║\n"
                  << "║                                                  ║\n"
                  << "╚══════════════════════════════════════════════════╝\n";

        // ----------------------------------------------------------
        // 추가: 데이터 처리량 (throughput) 계산
        // ----------------------------------------------------------
        if (total_time > 0) {
            double throughput = static_cast<double>(data_count) / (total_time / 1000.0);
            std::cout << "\n  처리량: " << std::fixed << std::setprecision(0)
                      << throughput << " records/sec (CSV 파이프라인)\n";
        }
        if (direct_total > 0) {
            double throughput = static_cast<double>(data_count) / (direct_total / 1000.0);
            std::cout << "  처리량: " << std::fixed << std::setprecision(0)
                      << throughput << " records/sec (직접 처리)\n";
        }
    }
};

} // namespace pipeline 끝

// ============================================================================
// main 함수: 프로그램의 시작점
// ============================================================================

/*
 *  main()은 C#의 static void Main()과 같습니다.
 *  프로그램이 시작되면 가장 먼저 이 함수가 호출됩니다.
 *
 *  argc: 명령줄 인수의 개수 (C#의 args.Length + 1)
 *  argv: 명령줄 인수의 배열 (C#의 args 배열과 비슷하지만, argv[0]은 프로그램 이름)
 *
 *  사용법:
 *    ./data_pipeline          → 기본 5000건 처리
 *    ./data_pipeline 10000    → 10000건 처리
 *    ./data_pipeline 100000   → 100000건 처리 (대규모 테스트)
 */
/*
=============================================================================
  실행 흐름 가이드
=============================================================================
  ./data_pipeline          → data_count = 5000 (기본)
  ./data_pipeline 10000    → data_count = 10000

  PipelineOrchestrator::run(N) 흐름:
    1. 센서 N개 데이터 생성 (시뮬레이션)
    2. CSV 파싱 → string_view 기반 zero-copy
    3. 통계 분석: 평균, 최소, 최대, 표준편차
    4. 결과를 pipeline_output.csv에 저장

  기대 출력 (5000건):
    파싱 완료: 5000행
    평균 온도: ~25.0°C, 표준편차: ~2.5
    처리 시간: ~5~20ms (단일 스레드)
    output.csv 행 수: 5000

  메모리 패턴:
    - 입력 버퍼: 1회 큰 할당 (vector reserve)
    - 파싱 결과: string_view → 원본 살아있는 동안만 유효
    - 통계는 누적기로 계산 (메모리 일정)
=============================================================================
*/

int main(int argc, char* argv[]) {
    size_t data_count = 5000;

    if (argc > 1) {
        try {
            data_count = std::stoul(argv[1]);
            // → "10000" → 10000
            //   "abc" → invalid_argument throw → catch
        } catch (...) {
            std::cerr << "잘못된 인수입니다. 숫자를 입력해주세요.\n";
            return 1;
        }
    }

    // 최소 100건, 최대 100만건으로 제한
    // std::clamp는 C#의 Math.Clamp()와 같습니다 (C++17 기능)
    data_count = std::clamp(data_count, static_cast<size_t>(100), static_cast<size_t>(1000000));

    std::cout << "╔══════════════════════════════════════════════════╗\n"
              << "║  고성능 데이터 수집/처리 파이프라인              ║\n"
              << "║  C++ Data Pipeline Project                      ║\n"
              << "║                                                  ║\n"
              << "║  이 프로그램은 C++이 대량 데이터 처리에서        ║\n"
              << "║  왜 C#보다 빠른지 보여줍니다.                   ║\n"
              << "║                                                  ║\n"
              << "║  핵심 기술:                                     ║\n"
              << "║  1. 제로카피 파싱 (string_view)                 ║\n"
              << "║  2. 캐시 친화적 메모리 (연속 배치)              ║\n"
              << "║  3. GC 없는 실시간 처리                         ║\n"
              << "║  4. 링 버퍼 스트리밍                            ║\n"
              << "╚══════════════════════════════════════════════════╝\n";

    // 파이프라인 실행!
    // pipeline:: 은 C#의 namespace를 쓰는 것과 같습니다
    // C#: Pipeline.PipelineOrchestrator.Run(dataCount);
    pipeline::PipelineOrchestrator::run(data_count);

    // 생성된 출력 파일 안내
    std::cout << "\n  출력 파일: pipeline_output.csv\n"
              << "  (이 파일을 Excel이나 Python pandas로 열어볼 수 있습니다)\n\n";

    return 0; // 0을 반환하면 "정상 종료"를 의미합니다 (C#에서도 같습니다)
}

/*
 * ============================================================================
 *  학습 포인트 요약
 * ============================================================================
 *
 *  C++ vs C# 핵심 차이점 (이 프로젝트에서 배운 것):
 *
 *  ┌─────────────────┬──────────────────────┬──────────────────────┐
 *  │     개념        │  C++                 │  C#                  │
 *  ├─────────────────┼──────────────────────┼──────────────────────┤
 *  │ 동적 배열       │ std::vector<T>       │ List<T>              │
 *  │ 문자열 뷰       │ std::string_view     │ ReadOnlySpan<char>   │
 *  │ 제네릭          │ template<typename T> │ <T> generic          │
 *  │ 함수 전달       │ std::function        │ Func<>, Action<>     │
 *  │ 메모리 관리     │ RAII + 스마트포인터  │ GC (자동)            │
 *  │ 데이터 이동     │ std::move            │ 없음 (GC가 처리)     │
 *  │ 읽기전용 참조   │ const&               │ in 매개변수          │
 *  │ 람다            │ [](auto x){...}      │ (x) => ...           │
 *  │ 정렬            │ std::sort            │ List.Sort() / LINQ   │
 *  │ 합계            │ std::accumulate      │ Enumerable.Sum()     │
 *  │ 필터            │ std::copy_if         │ .Where()             │
 *  │ 시간 측정       │ std::chrono          │ Stopwatch            │
 *  │ 파일 출력       │ std::ofstream        │ StreamWriter         │
 *  │ 문자열 빌더     │ std::ostringstream   │ StringBuilder        │
 *  │ 난수 생성       │ std::mt19937         │ Random               │
 *  │ 네임스페이스    │ namespace            │ namespace (동일!)    │
 *  └─────────────────┴──────────────────────┴──────────────────────┘
 *
 *  C++을 선택해야 하는 상황:
 *  1. 실시간 데이터 처리 (GC 멈춤이 허용되지 않는 경우)
 *  2. 대량 데이터 처리 (수백만~수억 건)
 *  3. 임베디드/IoT (메모리가 제한된 환경)
 *  4. 게임 엔진 (프레임마다 일정한 성능이 필요)
 *  5. 고빈도 금융 거래 (마이크로초 단위 지연이 중요)
 *
 *  C#을 선택해야 하는 상황:
 *  1. 웹 서비스 (ASP.NET Core)
 *  2. 빠른 프로토타이핑
 *  3. 팀의 생산성이 성능보다 중요한 경우
 *  4. UI 애플리케이션
 *
 * ============================================================================
 */
