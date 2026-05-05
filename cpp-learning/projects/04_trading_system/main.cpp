/*
 * ============================================================================
 *   금융 트레이딩 시스템 (Financial Trading System)
 *   - C++은 고빈도 트레이딩(HFT)의 "공식 언어"입니다!
 *   - 나노초(10억분의 1초) 단위의 속도가 승부를 결정합니다
 * ============================================================================
 *
 *   왜 C++인가? GC(가비지 컬렉터)가 없어서 갑자기 멈추는 일이 없습니다!
 *   실제 월스트리트 트레이딩 회사들은 거의 다 C++을 씁니다.
 *
 *   시스템 구조:
 *   ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
 *   │  Price Feed  │────>│ Order Book   │────>│  Matching   │
 *   │  (가격 피드)  │     │ (주문장)      │     │  Engine     │
 *   └─────────────┘     └──────────────┘     └──────┬──────┘
 *                        ┌──────────────┐     ┌──────▼──────┐
 *                        │  Strategy    │<────│  PnL Track  │
 *                        │  (전략 엔진)  │     │  (손익 추적)  │
 *                        └──────────────┘     └─────────────┘
 *
 *   컴파일: g++ -std=c++17 -O2 -o trading main.cpp
 */

// === #include 설명 ===
#include <iostream>      // 화면 출력 (C#의 Console.WriteLine)
#include <string>        // 문자열 (C#의 string)
#include <vector>        // 동적 배열 (C#의 List<T>)
#include <map>           // 정렬된 맵 (C#의 SortedDictionary)
#include <unordered_map> // 해시맵 (C#의 Dictionary<K,V>)
#include <queue>         // 큐 (C#의 Queue<T>)
#include <algorithm>     // 정렬/검색 (C#의 LINQ 비슷)
#include <chrono>        // 시간 측정 - 나노초! (C#의 Stopwatch보다 정밀)
#include <random>        // 랜덤 숫자 (C#의 Random)
#include <numeric>       // 숫자 계산 (합계 등)
#include <cmath>         // 수학 함수 (C#의 Math)
#include <sstream>       // 문자열 스트림 (C#의 StringReader)
#include <iomanip>       // 출력 형식 (C#의 String.Format)
#include <deque>         // 양방향 큐 (C#의 LinkedList 비슷)
#include <optional>      // 값이 있을 수도 없을 수도 (C#의 Nullable<T>)

using namespace std;
using namespace std::chrono;

// 자주 쓰는 타입 별명 (C#의 using Price = double; 과 같습니다)
using Price = double;
using Quantity = int;
using OrderId = uint64_t;
using Timestamp = steady_clock::time_point;

// ============================================================================
// 열거형 - enum class는 C#의 enum과 거의 같습니다! C++에서도 타입 안전합니다
// ============================================================================
enum class Side { Buy, Sell };  // 매수/매도

// 주문 종류 - 가게에서 물건 사는 방법이 여러 가지인 것처럼!
enum class OrderType {
    Market,    // 시장가: "아무 가격이나 좋으니 지금 당장!"
    Limit,     // 지정가: "이 가격 이하면 사겠습니다" (알뜰 쇼핑)
    StopLoss   // 손절: "이 가격까지 떨어지면 자동으로 팔아주세요"
};

enum class OrderStatus { New, Filled, Partial, Cancelled };

// ============================================================================
// 주문(Order) 구조체 - 하나의 주문 정보를 담는 상자
// C#: public class Order { public ulong Id { get; set; } ... }
// ============================================================================
struct Order {
    OrderId id;
    Side side;
    OrderType type;
    Price price;
    Quantity quantity;
    Quantity filled_qty = 0;
    OrderStatus status = OrderStatus::New;
    Timestamp timestamp;

    Quantity remaining() const { return quantity - filled_qty; }
    bool is_active() const {
        return status == OrderStatus::New || status == OrderStatus::Partial;
    }
};

// 거래 기록
struct Trade {
    OrderId buy_order_id, sell_order_id;
    Price price;
    Quantity quantity;
    Timestamp timestamp;
};

// 같은 가격의 주문들 모음 (가격 레벨)
struct PriceLevel {
    Price price;
    deque<Order*> orders;
    Quantity total_quantity() const {
        Quantity total = 0;
        for (const auto* o : orders) total += o->remaining();
        return total;
    }
};

// ============================================================================
// 주문장 (OrderBook) - 트레이딩 시스템의 심장!
// ============================================================================
/*
 *   OrderBook은 C#의 SortedDictionary와 비슷하지만, 더 빠른 자료구조를 직접 만듭니다
 *
 *   ┌─── 매수 (Bids) ───┐  ┌─── 매도 (Asks) ───┐
 *   │ 가격  │ 수량        │  │ 가격  │ 수량        │
 *   │ 100   │ 50          │  │ 101   │ 30          │
 *   │ 99    │ 100         │  │ 102   │ 80          │
 *   └───────┴────────────┘  └───────┴────────────┘
 */
class OrderBook {
    map<Price, PriceLevel, greater<Price>> bids_;  // 매수: 높은 가격이 앞
    map<Price, PriceLevel, less<Price>> asks_;      // 매도: 낮은 가격이 앞
    unordered_map<OrderId, Order> orders_;
    OrderId next_id_ = 1;
    vector<Trade> trades_;

    void add_to_book(Order& order) {
        // bids_와 asks_는 타입이 다르므로 (비교자가 다름) 분기 처리
        if (order.side == Side::Buy) {
            bids_[order.price].price = order.price;
            bids_[order.price].orders.push_back(&orders_[order.id]);
        } else {
            asks_[order.price].price = order.price;
            asks_[order.price].orders.push_back(&orders_[order.id]);
        }
    }

    void execute_trade(Order& buy, Order& sell, Price price) {
        Quantity qty = min(buy.remaining(), sell.remaining());
        if (qty <= 0) return;
        buy.filled_qty += qty;  sell.filled_qty += qty;
        buy.status = buy.remaining() == 0 ? OrderStatus::Filled : OrderStatus::Partial;
        sell.status = sell.remaining() == 0 ? OrderStatus::Filled : OrderStatus::Partial;
        trades_.push_back({buy.id, sell.id, price, qty, steady_clock::now()});
    }

    // 시장가 매칭: "아무 가격이나 좋으니 바로 거래!"
    void match_market(Order& order) {
        if (order.side == Side::Buy) {
            while (order.is_active() && !asks_.empty()) {
                auto& [p, level] = *asks_.begin();
                while (!level.orders.empty() && order.is_active()) {
                    execute_trade(order, *level.orders.front(), p);
                    if (!level.orders.front()->is_active()) level.orders.pop_front();
                }
                if (level.orders.empty()) asks_.erase(asks_.begin());
            }
        } else {
            while (order.is_active() && !bids_.empty()) {
                auto& [p, level] = *bids_.begin();
                while (!level.orders.empty() && order.is_active()) {
                    execute_trade(*level.orders.front(), order, p);
                    if (!level.orders.front()->is_active()) level.orders.pop_front();
                }
                if (level.orders.empty()) bids_.erase(bids_.begin());
            }
        }
    }

    // 지정가 매칭: "이 가격 이하/이상이면 거래합니다"
    void match_limit(Order& order) {
        if (order.side == Side::Buy) {
            while (order.is_active() && !asks_.empty() && asks_.begin()->first <= order.price) {
                auto it = asks_.begin();
                while (!it->second.orders.empty() && order.is_active()) {
                    execute_trade(order, *it->second.orders.front(), it->first);
                    if (!it->second.orders.front()->is_active()) it->second.orders.pop_front();
                }
                if (it->second.orders.empty()) asks_.erase(it);
            }
        } else {
            while (order.is_active() && !bids_.empty() && bids_.begin()->first >= order.price) {
                auto it = bids_.begin();
                while (!it->second.orders.empty() && order.is_active()) {
                    execute_trade(*it->second.orders.front(), order, it->first);
                    if (!it->second.orders.front()->is_active()) it->second.orders.pop_front();
                }
                if (it->second.orders.empty()) bids_.erase(it);
            }
        }
    }

public:
    OrderId add_order(Side side, OrderType type, Price price, Quantity qty) {
        OrderId id = next_id_++;
        orders_[id] = {id, side, type, price, qty, 0, OrderStatus::New, steady_clock::now()};
        if (type == OrderType::Market) {
            match_market(orders_[id]);
        } else if (type == OrderType::Limit) {
            match_limit(orders_[id]);
            if (orders_[id].is_active()) add_to_book(orders_[id]);
        } else {
            add_to_book(orders_[id]);  // StopLoss: 주문장에 추가
        }
        return id;
    }

    optional<Price> best_bid() const { return bids_.empty() ? nullopt : optional(bids_.begin()->first); }
    optional<Price> best_ask() const { return asks_.empty() ? nullopt : optional(asks_.begin()->first); }
    const vector<Trade>& trades() const { return trades_; }
    size_t trade_count() const { return trades_.size(); }

    void print_book(int depth = 5) const {
        cout << "\n  ╔═══════════════════════════════════╗\n";
        cout << "  ║       주문장 (Order Book)          ║\n";
        cout << "  ╠═══════════════════════════════════╣\n";
        // 매도 (위쪽)
        vector<pair<Price, Quantity>> ask_levels;
        int cnt = 0;
        for (const auto& [p, level] : asks_) {
            if (cnt++ >= depth) break;
            ask_levels.push_back({p, level.total_quantity()});
        }
        for (int i = (int)ask_levels.size() - 1; i >= 0; i--)
            cout << "  ║ ASK " << fixed << setprecision(2) << setw(8) << ask_levels[i].first
                 << " | " << setw(5) << ask_levels[i].second << " 주      ║\n";
        cout << "  ║───────────────────────────────────║\n";
        // 매수 (아래쪽)
        cnt = 0;
        for (const auto& [p, level] : bids_) {
            if (cnt++ >= depth) break;
            cout << "  ║ BID " << fixed << setprecision(2) << setw(8) << p
                 << " | " << setw(5) << level.total_quantity() << " 주      ║\n";
        }
        cout << "  ╚═══════════════════════════════════╝\n";
    }
};

// ============================================================================
// 가격 피드 시뮬레이터 - 틱 데이터 생성
// 가격 변동: ~~~╱╲~~~╱╲╱~~~╲╱╲~~~
// ============================================================================
class PriceFeed {
    Price current_;
    mt19937 rng_;                // C#의 Random보다 훨씬 좋은 난수 생성기
    normal_distribution<> dist_; // 정규분포 (종 모양 곡선)
    vector<Price> history_;

public:
    PriceFeed(Price initial, double volatility, unsigned seed = 42)
        : current_(initial), rng_(seed), dist_(0.0, volatility) {
        history_.push_back(current_);
    }

    // 다음 가격 생성 (랜덤 워크 - 실제 주가와 비슷한 모델!)
    Price next_tick() {
        current_ += dist_(rng_);
        if (current_ < 0.01) current_ = 0.01;
        history_.push_back(current_);
        return current_;
    }

    Price current() const { return current_; }
    const vector<Price>& history() const { return history_; }
};

// ============================================================================
// 이동평균 계산기 (SMA, EMA) - 트레이딩 신호 생성
// ============================================================================
/*
 *   SMA: 최근 N개 가격의 단순 평균
 *   EMA: 최근 가격에 더 큰 가중치를 주는 평균 (더 민감!)
 *
 *   트레이딩 신호:
 *   단기 > 장기 → 골든 크로스 (매수!)
 *   단기 < 장기 → 데드 크로스 (매도!)
 */
class MovingAverage {
public:
    // SMA: C#의 prices.TakeLast(period).Average() 와 같습니다
    static double sma(const vector<Price>& prices, int period) {
        if ((int)prices.size() < period) return 0.0;
        double sum = 0;
        for (int i = (int)prices.size() - period; i < (int)prices.size(); i++)
            sum += prices[i];
        return sum / period;
    }

    // EMA: 최근 가격에 더 큰 비중 (더 빠르게 반응!)
    static double ema(const vector<Price>& prices, int period) {
        if (prices.empty()) return 0.0;
        if ((int)prices.size() < period) return sma(prices, (int)prices.size());
        double mult = 2.0 / (period + 1);
        double val = 0;
        for (int i = 0; i < period; i++) val += prices[i];
        val /= period;
        for (int i = period; i < (int)prices.size(); i++)
            val = (prices[i] - val) * mult + val;
        return val;
    }

    // SMA 시계열 전체 계산
    static vector<double> sma_series(const vector<Price>& prices, int period) {
        vector<double> result;
        for (int i = period - 1; i < (int)prices.size(); i++) {
            double sum = 0;
            for (int j = i - period + 1; j <= i; j++) sum += prices[j];
            result.push_back(sum / period);
        }
        return result;
    }
};

// ============================================================================
// 손익 추적기 (PnL Tracker)
// 100원에 사서 110원에 팔면 → PnL = +10원 (이익!)
// ============================================================================
class PnLTracker {
    double realized_ = 0;
    int position_ = 0;       // 보유 수량 (양수=보유중)
    double avg_price_ = 0;   // 평균 매입가
    int trades_ = 0, wins_ = 0;

public:
    void record(Side side, Price price, Quantity qty) {
        trades_++;
        if (side == Side::Buy) {
            double cost = avg_price_ * position_ + price * qty;
            position_ += qty;
            if (position_ > 0) avg_price_ = cost / position_;
        } else {
            if (position_ > 0) {
                double pnl = (price - avg_price_) * qty;
                realized_ += pnl;
                if (pnl > 0) wins_++;
            }
            position_ -= qty;
        }
    }

    double unrealized(Price current) const {
        return position_ == 0 ? 0 : (current - avg_price_) * position_;
    }
    double total_pnl(Price current) const { return realized_ + unrealized(current); }
    double win_rate() const { return trades_ == 0 ? 0 : 100.0 * wins_ / trades_; }
    int position() const { return position_; }

    void print(Price current) const {
        cout << "\n  ┌───────────────────────────────┐\n";
        cout << "  │    손익 요약 (PnL Summary)      │\n";
        cout << "  ├───────────────────────────────┤\n";
        cout << fixed << setprecision(2);
        cout << "  │ 확정 손익:   " << setw(12) << realized_ << " 원 │\n";
        cout << "  │ 미실현:     " << setw(12) << unrealized(current) << " 원 │\n";
        cout << "  │ 총 손익:     " << setw(12) << total_pnl(current) << " 원 │\n";
        cout << "  │ 포지션:     " << setw(12) << position_ << " 주 │\n";
        cout << "  │ 승률:       " << setw(11) << win_rate() << "%  │\n";
        cout << "  └───────────────────────────────┘\n";
    }
};

// ============================================================================
// 지연시간 측정기 - chrono::steady_clock은 C#의 Stopwatch와 같지만, 나노초 정밀도입니다
// ============================================================================
class LatencyMeasurer {
    vector<long long> data_;
    Timestamp start_;

public:
    void start() { start_ = steady_clock::now(); }
    long long stop() {
        auto ns = duration_cast<nanoseconds>(steady_clock::now() - start_).count();
        data_.push_back(ns);
        return ns;
    }

    template<typename F> long long measure(F&& f) { start(); f(); return stop(); }

    double avg_ns() const {
        if (data_.empty()) return 0;
        double s = 0; for (auto n : data_) s += n; return s / data_.size();
    }
    long long min_ns() const { return data_.empty() ? 0 : *min_element(data_.begin(), data_.end()); }
    long long max_ns() const { return data_.empty() ? 0 : *max_element(data_.begin(), data_.end()); }

    // 백분위수 (p50, p99 등)
    long long percentile(double p) const {
        if (data_.empty()) return 0;
        auto sorted = data_;
        sort(sorted.begin(), sorted.end());
        return sorted[(int)(p / 100.0 * (sorted.size() - 1))];
    }

    void print() const {
        cout << "\n  ┌────────────────────────────────────┐\n";
        cout << "  │   지연시간 (Latency Stats)           │\n";
        cout << "  ├────────────────────────────────────┤\n";
        cout << "  │ 평균:  " << setw(12) << fixed << setprecision(0) << avg_ns() << " ns        │\n";
        cout << "  │ 최소:  " << setw(12) << min_ns() << " ns        │\n";
        cout << "  │ 최대:  " << setw(12) << max_ns() << " ns        │\n";
        cout << "  │ p50:   " << setw(12) << percentile(50) << " ns        │\n";
        cout << "  │ p99:   " << setw(12) << percentile(99) << " ns        │\n";
        cout << "  │ 횟수:  " << setw(12) << data_.size() << " 회         │\n";
        cout << "  └────────────────────────────────────┘\n";
    }
};

// ============================================================================
// 평균 회귀 전략 (Mean Reversion Strategy)
// ============================================================================
/*
 *   "많이 올랐으면 곧 내려오고, 많이 내려갔으면 곧 올라온다"
 *
 *          가격
 *           ╱╲
 *          ╱  ╲   ← 여기서 팔아! (이동평균보다 높음)
 *   ──────╱────╲──────── 이동평균선
 *                ╲  ╱
 *                 ╲╱ ← 여기서 사! (이동평균보다 낮음)
 */
class MeanReversionStrategy {
    int period_;
    double threshold_;
    int max_pos_;
    PnLTracker pnl_;

public:
    MeanReversionStrategy(int period = 20, double thresh = 1.5, int max_pos = 100)
        : period_(period), threshold_(thresh), max_pos_(max_pos) {}

    // 반환: 양수=매수수량, 음수=매도수량, 0=대기
    int signal(const vector<Price>& prices) {
        if ((int)prices.size() < period_) return 0;
        double sma = MovingAverage::sma(prices, period_);
        double dev = ((prices.back() - sma) / sma) * 100.0;
        int pos = pnl_.position();
        if (dev < -threshold_ && pos < max_pos_) return min(10, max_pos_ - pos);
        if (dev > threshold_ && pos > 0) return -min(10, pos);
        return 0;
    }

    void execute(Side side, Price p, Quantity q) { pnl_.record(side, p, q); }
    PnLTracker& pnl() { return pnl_; }
};

// ============================================================================
// 손절 관리자 (Stop Loss) - 가격이 떨어지면 자동 매도하는 안전장치
// C#의 이벤트 리스너처럼 가격 도달 시 자동 실행
// ============================================================================
class StopLossManager {
    struct Stop { Price trigger; Quantity qty; bool fired = false; };
    vector<Stop> stops_;
public:
    void add(Price trigger, Quantity qty) { stops_.push_back({trigger, qty, false}); }

    vector<pair<Price, Quantity>> check(Price current) {
        vector<pair<Price, Quantity>> triggered;
        for (auto& s : stops_)
            if (!s.fired && current <= s.trigger) { s.fired = true; triggered.push_back({s.trigger, s.qty}); }
        return triggered;
    }

    void clear() {
        stops_.erase(remove_if(stops_.begin(), stops_.end(), [](auto& s){ return s.fired; }), stops_.end());
    }
};

// ============================================================================
// 미니 가격 차트 (ASCII)
// ============================================================================
void print_chart(const vector<Price>& data, int w = 60, int h = 12) {
    if (data.empty()) return;
    int start = max(0, (int)data.size() - w);
    vector<Price> v(data.begin() + start, data.end());
    Price lo = *min_element(v.begin(), v.end());
    Price hi = *max_element(v.begin(), v.end());
    double range = hi - lo; if (range < 0.01) range = 1.0;

    cout << "\n  가격 차트:\n";
    for (int row = h - 1; row >= 0; row--) {
        cout << "  " << (row == h - 1 ? fixed : "") << setprecision(1);
        if (row == h - 1) cout << setw(7) << hi << " |";
        else if (row == 0)  cout << setw(7) << lo << " |";
        else                cout << "        |";
        for (size_t c = 0; c < v.size() && c < (size_t)w; c++) {
            int y = (int)((v[c] - lo) / range * (h - 1));
            cout << (y == row ? "*" : " ");
        }
        cout << "\n";
    }
}

// ============================================================================
// 메인 함수 - 모든 것을 조합해서 시뮬레이션!
// ============================================================================
/*
=============================================================================
  실행 흐름 가이드 (시드 고정 → 결과 재현 가능)
=============================================================================
  [1] PriceFeed(시작=100, 변동=0.5, seed=42), 200틱 → 가격 추이
  [2] SMA(20), SMA(50), EMA(20) 계산 → 골든/데드 크로스 판단
  [3] OrderBook: 매수 5건 + 매도 5건 추가 후 출력
  [4] 시장가 매수 80주 → bid 호가 매칭 → 체결 발생
  [5] 1000건 주문 추가 latency 측정 (보통 us 단위)
  [6] MeanReversion 전략 500틱 시뮬레이션 → buys/sells/PnL
  [7] 성능 벤치: 100K 주문 / 100K SMA 시간 측정

  기대 출력 (대략):
    200개 틱 생성 | 시작: 100.00 | 현재: ~95~105 (시드 따라)
    SMA(20)=...  SMA(50)=...  EMA(20)=...  신호: 골든/데드
    Order book 출력 (매수/매도 호가 표)
    체결 거래: 1~3건
    Latency: 평균 ~수us
    매수: 수십회 | 매도: 수십회
    100K 주문: 수ms 정도
=============================================================================
*/

int main() {
    cout << "============================================================\n";
    cout << "  금융 트레이딩 시스템 (C++ Trading System)\n";
    cout << "============================================================\n";

    cout << "\n[1] 가격 피드 시뮬레이션\n";
    PriceFeed feed(100.0, 0.5, 42);
    for (int i = 0; i < 200; i++) feed.next_tick();
    // → feed.history() 크기 200, 시드 42로 결정적 결과
    cout << "  " << feed.history().size() << "개 틱 생성 | 시작: "
         << fixed << setprecision(2) << feed.history().front()
         << " | 현재: " << feed.current() << "\n";

    // ── [2] 이동평균 ──
    cout << "\n[2] 이동평균 계산\n";
    double sma20 = MovingAverage::sma(feed.history(), 20);
    double sma50 = MovingAverage::sma(feed.history(), 50);
    double ema20 = MovingAverage::ema(feed.history(), 20);
    cout << "  SMA(20)=" << setprecision(4) << sma20
         << "  SMA(50)=" << sma50 << "  EMA(20)=" << ema20 << "\n";
    cout << "  신호: " << (sma20 > sma50 ? "골든 크로스 (상승)" : "데드 크로스 (하락)") << "\n";

    // ── [3] 주문장 테스트 ──
    cout << "\n[3] 주문장(OrderBook) 테스트\n";
    OrderBook book;
    // 매수 주문 5개
    for (auto [p, q] : vector<pair<double,int>>{{99,50},{98.5,100},{98,150},{97.5,200},{97,80}})
        book.add_order(Side::Buy, OrderType::Limit, p, q);
    // 매도 주문 5개
    for (auto [p, q] : vector<pair<double,int>>{{101,60},{101.5,90},{102,120},{102.5,70},{103,110}})
        book.add_order(Side::Sell, OrderType::Limit, p, q);
    book.print_book();

    // ── [4] 주문 매칭 ──
    cout << "\n[4] 주문 매칭 테스트\n";
    cout << "  시장가 매수 80주 전송!\n";
    book.add_order(Side::Buy, OrderType::Market, 0, 80);
    cout << "  체결 거래: " << book.trade_count() << "건\n";
    book.print_book();

    // ── [5] 지연시간 측정 ──
    cout << "\n[5] 지연시간 측정 (나노초 정밀도!)\n";
    LatencyMeasurer latency;
    OrderBook bench_book;
    for (int i = 0; i < 1000; i++) {
        latency.measure([&]() {
            bench_book.add_order(
                i % 2 == 0 ? Side::Buy : Side::Sell,
                OrderType::Limit, 100.0 + (i % 20) - 10, 10 + i % 50);
        });
    }
    latency.print();

    // ── [6] 평균 회귀 전략 시뮬레이션 ──
    cout << "\n[6] 평균 회귀 전략 (500틱 시뮬레이션)\n";
    MeanReversionStrategy strategy(20, 1.0, 100);
    StopLossManager stops;
    PriceFeed sim(100.0, 0.3, 123);
    int buys = 0, sells = 0;

    for (int t = 0; t < 500; t++) {
        Price p = sim.next_tick();
        int sig = strategy.signal(sim.history());
        if (sig > 0) {
            strategy.execute(Side::Buy, p, sig);
            stops.add(p * 0.98, sig);  // 2% 아래에 손절 설정
            buys++;
        } else if (sig < 0) {
            strategy.execute(Side::Sell, p, -sig);
            sells++;
        }
        // 손절 확인
        for (auto& [tp, qty] : stops.check(p)) {
            strategy.execute(Side::Sell, p, qty);
            sells++;
        }
        stops.clear();
    }
    cout << "  매수: " << buys << "회 | 매도: " << sells << "회\n";
    print_chart(sim.history());
    strategy.pnl().print(sim.current());

    // ── [7] 성능 벤치마크 ──
    cout << "\n[7] 성능 벤치마크 (C++의 진정한 힘!)\n";
    {
        OrderBook perf;
        auto t0 = steady_clock::now();
        for (int i = 0; i < 100000; i++)
            perf.add_order(i % 2 == 0 ? Side::Buy : Side::Sell,
                           OrderType::Limit, 100.0 + (i % 100) - 50, 1 + i % 10);
        auto us = duration_cast<microseconds>(steady_clock::now() - t0).count();
        cout << "  100K 주문: " << us << " us (주문당 " << us / 100000.0 << " us)\n";
        cout << "  체결: " << perf.trade_count() << "건\n";
    }
    {
        PriceFeed big(100.0, 0.5, 999);
        for (int i = 0; i < 100000; i++) big.next_tick();
        auto t0 = steady_clock::now();
        auto s = MovingAverage::sma_series(big.history(), 50);
        auto us = duration_cast<microseconds>(steady_clock::now() - t0).count();
        cout << "  100K SMA(50): " << us << " us (" << s.size() << " 포인트)\n";
    }

    // ── 최종 요약 ──
    cout << "\n============================================================\n";
    cout << "  배운 것들:\n";
    cout << "  1. OrderBook: map으로 가격-시간 우선순위 매칭\n";
    cout << "  2. 주문 타입: Market, Limit, StopLoss\n";
    cout << "  3. 매칭 엔진: 매수-매도 자동 매칭\n";
    cout << "  4. 가격 피드: 랜덤 워크 시뮬레이션\n";
    cout << "  5. SMA/EMA: 트레이딩 신호 생성\n";
    cout << "  6. PnL: 실시간 손익 추적\n";
    cout << "  7. 나노초 지연시간: chrono 라이브러리\n";
    cout << "  8. 평균 회귀: 실전 트레이딩 알고리즘\n";
    cout << "\n  C++ vs C#:\n";
    cout << "  - C++: GC 없음 -> 예측 가능한 지연시간\n";
    cout << "  - C++: 나노초 측정 가능 (chrono)\n";
    cout << "  - C#: 생산성 높음, 빠른 개발\n";
    cout << "  - 실무: 전략은 C#/Python, 실행 엔진은 C++\n";
    cout << "============================================================\n";

    return 0;
}
