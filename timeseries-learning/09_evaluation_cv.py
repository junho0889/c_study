# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [시계열] 학습 09단계: 평가와 검증
#   ─ MAE/MAPE/SMAPE/MASE · Walk-forward CV · 백테스팅 ─
#   ■ 실행 방법: python 09_evaluation_cv.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 시계열에서 절대 하지 말아야 할 split
#   2. 점추정 지표: MAE / RMSE / MAPE / SMAPE / MASE
#   3. 예측구간 지표: pinball loss / coverage
#   4. Walk-forward CV (rolling / expanding)
#   5. 백테스팅 디자인 — 휴일/이벤트 격리, 비대칭 비용
#   6. 기준 모델(baseline): Naive / Seasonal Naive / Drift
#   7. 실전: walk-forward 로 ARIMA vs Naive 비교
#
# ─────────────────────────────────────────────────────────────────────────

import math
import random


def lesson1_no_random_split():
    # =========================================================================
    #   레슨 1 — 시계열 split
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 시계열 split               │")
    print("└──────────────────────────────────────┘")
    # ■ 절대 금지:
    #   - random_split → 미래 누설
    #   - K-Fold shuffle → 동일
    #
    # ■ 옳은 방식:
    #   - 시간순으로 train < val < test
    #   - 또는 walk-forward (rolling / expanding) — 운영을 모사
    #
    #   Train: [████████████]        Val: [████]      Test: [██]
    #          ─────────── 시간 ───────────────────────────►
    print(" 시계열 split = 항상 시간 ‘이전 → 이후’.  shuffle 금지.")
    print()


def lesson2_point_metrics():
    # =========================================================================
    #   레슨 2 — 점추정 지표
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : 점추정 지표                │")
    print("└──────────────────────────────────────┘")
    # ■ MAE  = mean(|y - ŷ|)               — 단위 동일, 직관적
    # ■ RMSE = sqrt(mean((y-ŷ)²))          — 큰 오차에 강한 페널티
    # ■ MAPE = mean(|y-ŷ|/|y|) × 100        — % 표현, y≈0 에 폭주
    # ■ SMAPE= mean(2|y-ŷ|/(|y|+|ŷ|)) × 100 — MAPE 의 비대칭 보완
    # ■ MASE = MAE / MAE(naive)            — naïve 대비 상대 성능 (1 미만이면 baseline 이김)

    y =  [100.0, 105.0, 110.0, 108.0]
    yh = [102.0, 103.0, 115.0, 110.0]

    mae = sum(abs(a - b) for a, b in zip(y, yh)) / len(y)
    rmse = math.sqrt(sum((a - b) ** 2 for a, b in zip(y, yh)) / len(y))
    mape = sum(abs(a - b) / a for a, b in zip(y, yh)) / len(y) * 100
    smape = sum(2 * abs(a - b) / (abs(a) + abs(b)) for a, b in zip(y, yh)) / len(y) * 100
    print(f" MAE   = {mae:.2f}")
    print(f" RMSE  = {rmse:.2f}")
    print(f" MAPE  = {mape:.2f}%")
    print(f" SMAPE = {smape:.2f}%")
    print()


def lesson3_interval_metrics():
    # =========================================================================
    #   레슨 3 — 예측구간 지표
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : 예측구간 평가              │")
    print("└──────────────────────────────────────┘")
    # ■ 점예측만으론 부족 — 의사결정엔 ‘불확실성’이 필요.
    #
    # ■ Pinball Loss (quantile loss, level τ):
    #     ρ_τ(y, q) = (y - q) · τ                if y ≥ q
    #               = (q - y) · (1 - τ)         if y <  q
    #   - q 는 τ-분위 예측값
    #   - τ=0.5 면 MAE 와 같음
    #
    # ■ Coverage:
    #   - 90% 예측구간이 실제로 90% 시점에 실제값을 포함하는지
    #   - 너무 넓으면 무의미, 너무 좁으면 과신
    print(" 비즈니스에서 ‘우리는 90% 확률로 X 이상 팔린다’가 점추정보다 훨씬 유용.")
    print()


def lesson4_walk_forward_cv():
    # =========================================================================
    #   레슨 4 — Walk-forward CV
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : Walk-forward CV            │")
    print("└──────────────────────────────────────┘")
    # ■ Expanding window:
    #   Fold 1:  [████]                   |  → predict [██]
    #   Fold 2:  [██████]                 |  → predict [██]
    #   Fold 3:  [████████]               |  → predict [██]
    #
    # ■ Rolling window (고정 크기):
    #   Fold 1:  [████]      |              → predict [██]
    #   Fold 2:    [████]    |              → predict [██]
    #   Fold 3:      [████]  |              → predict [██]
    #
    # ■ 코드:
    #     from sklearn.model_selection import TimeSeriesSplit
    #     tscv = TimeSeriesSplit(n_splits=5, test_size=14)
    #     for train_idx, test_idx in tscv.split(X):
    #         ...
    print(" Walk-forward = ‘운영 시뮬레이션’.  모델 평가의 황금 표준.")
    print()


def lesson5_backtest_design():
    # =========================================================================
    #   레슨 5 — 백테스트 디자인
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 백테스트 디자인            │")
    print("└──────────────────────────────────────┘")
    # ■ 흔한 실수:
    #   - 공휴일/이벤트가 train/test 분포에 한쪽에만 몰림
    #   - 한 번의 split 만으로 결론 (분산 큼)
    #   - 비즈니스 비용을 무시한 MAE 비교
    #
    # ■ 권장:
    #   1) 5~10 folds 의 walk-forward
    #   2) horizon 별 평균/분산 모두 보고
    #   3) 비대칭 비용 반영:
    #        - 재고 부족 vs 잉여, 어느쪽이 더 비싼지 → quantile 모델 활용
    #   4) “휴일만 모은 테스트셋”도 별도 보고
    print(" 백테스트는 ‘비용 함수와 fold 다양성’ 이 핵심.")
    print()


def lesson6_baselines():
    # =========================================================================
    #   레슨 6 — 기준 모델
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : Baseline                   │")
    print("└──────────────────────────────────────┘")
    # ■ Naive:           ŷ_{t+h} = y_t
    # ■ Seasonal Naive:  ŷ_{t+h} = y_{t+h-m}     (m = 계절 주기)
    # ■ Drift:           ŷ_{t+h} = y_t + h · (y_t - y_1)/(t-1)
    # ■ Moving Average:  ŷ_{t+h} = mean(마지막 k개)
    #
    # ■ 어떤 모델도 “Seasonal Naive”를 못 이기면 의미 없음.
    print(" 기준 모델은 ‘이걸 못 이기면 출시 금지’의 가드레일.")
    print()


def lesson7_practice_walkforward():
    # =========================================================================
    #   레슨 7 — 실전: walk-forward 로 모델 비교
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : Walk-forward 비교          │")
    print("└──────────────────────────────────────┘")
    random.seed(2025)
    n = 50
    Y = [50 + 0.2 * t + 5 * math.sin(2 * math.pi * t / 7) + random.gauss(0, 1) for t in range(n)]

    # ‘모델 A’ = Naive(전일값)
    # ‘모델 B’ = Seasonal Naive(7일 전)
    H = 5  # horizon
    fold_size = 10
    folds = []
    cursor = 25
    while cursor + H <= n:
        train = Y[:cursor]
        test = Y[cursor : cursor + H]
        folds.append((train, test))
        cursor += fold_size

    def naive_forecast(train, h):
        return [train[-1]] * h

    def seasonal_naive(train, h, m=7):
        return [train[len(train) - m + (i % m)] for i in range(h)]

    def mae(a, b):
        return sum(abs(x - y) for x, y in zip(a, b)) / len(a)

    for i, (tr, te) in enumerate(folds):
        a = mae(te, naive_forecast(tr, H))
        b = mae(te, seasonal_naive(tr, H))
        print(f" Fold {i+1}: Naive MAE={a:.2f},  Seasonal-Naive MAE={b:.2f}  {'←Seasonal-Naive 승' if b < a else '←Naive 승'}")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 연습문제
# ─────────────────────────────────────────────────────────────────────────
#  Q1. y=0 이 섞인 데이터에서 MAPE 가 무한대로 가는 이유와 대체 지표 2 가지를 적어라.
#  Q2. MASE 의 분모가 ‘훈련 구간의 naïve MAE’ 인 이유는?
#  Q3. Pinball loss 가 비대칭 비용(과대예측 vs 과소예측)을 어떻게 표현하나?
#  Q4. expanding vs rolling 의 trade-off 를 한 줄로 정리하라.
#  Q5. 매출 모델을 평가할 때 평일/주말/공휴일 세트로 분리 보고하면 어떤 이점?


if __name__ == "__main__":
    lesson1_no_random_split()
    lesson2_point_metrics()
    lesson3_interval_metrics()
    lesson4_walk_forward_cv()
    lesson5_backtest_design()
    lesson6_baselines()
    lesson7_practice_walkforward()
