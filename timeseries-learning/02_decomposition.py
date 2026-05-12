# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [시계열] 학습 02단계: 시계열 분해 (Decomposition)
#   ─ 가법/승법 분해 · STL · 트렌드/계절/잔차 분리 ─
#   ■ 실행 방법: python 02_decomposition.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 왜 분해하는가?
#   2. 가법(additive) vs 승법(multiplicative)
#   3. 이동평균(MA)으로 트렌드 추출하기
#   4. 계절성 추출 — 평균법
#   5. STL 분해 개념 — Loess 기반의 강건한 분해
#   6. 잔차 진단 — 분해가 잘 됐는지 어떻게 확인?
#   7. 실전: 30주 데이터에 직접 가법 분해 수행
#
# ─────────────────────────────────────────────────────────────────────────

import math
import random


def lesson1_why_decompose():
    # =========================================================================
    #   레슨 1 — 왜 분해하는가?
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 왜 분해하는가              │")
    print("└──────────────────────────────────────┘")
    # ■ 분해의 목적
    #   1) 이해: 트렌드가 진짜 우상향인지, 계절성이 7일/12개월 단위인지 분리해서 보기
    #   2) 모델링 보조: 트렌드/계절을 따로 모델링하고 잔차에만 ML 적용 가능
    #   3) 이상탐지: 잔차가 비정상적으로 튀는 시점 = 이상 후보
    #
    #   원시 시계열 Y(t)
    #         │  분해
    #         ▼
    #   Trend  T(t)  ─┐
    #   Season S(t)  ─┼─→ 원래대로 합치면 Y(t) (가법)
    #   Residual R(t) ┘
    print()


def lesson2_additive_vs_multiplicative():
    # =========================================================================
    #   레슨 2 — 가법 vs 승법
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : 가법 vs 승법               │")
    print("└──────────────────────────────────────┘")
    # ■ 가법(Additive):     Y = T + S + R
    #   - 계절성의 “진폭”이 시간이 흘러도 일정.
    #   - 예: 일일 평균 기온
    #
    # ■ 승법(Multiplicative): Y = T × S × R
    #   - 계절성의 진폭이 트렌드와 함께 커진다.
    #   - 예: 매출 (회사가 커지면 성수기 변동폭도 커짐)
    #
    # ■ 판별 팁:
    #   - 시계열 그림에서 봉우리/골짜기 간격은 일정한데 “높이”가 점점 커지면 → 승법.
    #   - 승법을 가법으로 다루려면 로그를 씌운다:  log(Y) = log(T) + log(S) + log(R)
    print()


def moving_average(series, window):
    # 단순 중심 이동평균 (window는 홀수가 편함)
    if window % 2 == 0:
        window += 1
    half = window // 2
    out = [None] * len(series)
    for i in range(half, len(series) - half):
        w = series[i - half : i + half + 1]
        out[i] = sum(w) / window
    return out


def lesson3_trend_via_ma():
    # =========================================================================
    #   레슨 3 — 이동평균으로 트렌드 추출
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : 이동평균 트렌드            │")
    print("└──────────────────────────────────────┘")
    random.seed(0)
    n = 24
    series = [50 + 2 * t + 10 * math.sin(2 * math.pi * t / 7) + random.gauss(0, 2) for t in range(n)]

    trend = moving_average(series, window=7)

    print(" t | series | trend")
    for t, (s, tr) in enumerate(zip(series, trend)):
        tr_str = f"{tr:7.2f}" if tr is not None else "   ---"
        print(f"{t:>2} | {s:6.2f} | {tr_str}")
    print()
    # ■ 관찰: 가장자리(window-1)/2 만큼 트렌드가 비어있다. 실무에서는 양끝을 “보간”하거나 STL을 쓴다.


def lesson4_seasonality_average():
    # =========================================================================
    #   레슨 4 — 계절성 추출(평균법)
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : 계절성 평균법              │")
    print("└──────────────────────────────────────┘")
    # ■ 가법 분해 절차 (수기):
    #   1) trend  T(t) = moving_average(Y, period)
    #   2) detrended  D(t) = Y(t) - T(t)
    #   3) 같은 “계절 슬롯”끼리 평균 → S(t)
    #      예: 주간 계절성(period=7) 이면 모든 월요일 detrend 값들의 평균이 “월요일의 계절성”
    #   4) residual  R(t) = Y(t) - T(t) - S(t)
    print(" 가법 분해: Y = T + S + R")
    print(" 1) T  ← 이동평균,   2) D = Y - T,   3) S = 같은 슬롯 평균(D),   4) R = Y - T - S")
    print()


def lesson5_stl_concept():
    # =========================================================================
    #   레슨 5 — STL 분해 개념
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : STL 분해                   │")
    print("└──────────────────────────────────────┘")
    # ■ STL = Seasonal-Trend decomposition using Loess
    #   - Loess(국소 가중 회귀)를 반복 적용하여 트렌드/계절을 매끄럽게 분리.
    #   - 장점:
    #       * 계절 길이 어떤 값이든 OK (7, 12, 24, 96, …)
    #       * 이상치에 강건 (robust 옵션)
    #       * 시간이 흐르며 계절성의 모양이 “천천히” 변해도 따라감
    #   - statsmodels.tsa.seasonal.STL 로 한 줄로 사용 가능.
    #
    # ■ Python 실코드 예 (개념):
    #     from statsmodels.tsa.seasonal import STL
    #     res = STL(series, period=7, robust=True).fit()
    #     trend, seasonal, resid = res.trend, res.seasonal, res.resid
    print(" STL = Loess 기반 분해. 이상치에 강건하고, 계절성이 천천히 변화해도 추적.")
    print()


def lesson6_residual_diagnostics():
    # =========================================================================
    #   레슨 6 — 잔차 진단
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 잔차 진단                  │")
    print("└──────────────────────────────────────┘")
    # ■ “잘 분해된 시계열”의 잔차(R)는 다음을 만족해야 한다:
    #   1) 평균 ≈ 0
    #   2) 분산이 시간에 무관 (이분산성 없음)
    #   3) 자기상관 없음 → white noise
    #   4) 정규성 (필수는 아님, 신뢰구간 계산에 유용)
    #
    # ■ 검정:
    #   - 자기상관:  Ljung-Box test
    #   - 정규성:    Shapiro-Wilk, Jarque-Bera
    #   - 이분산성:  Breusch-Pagan
    print(" 잔차가 white noise 가 아니면 → 모델/분해가 아직 정보를 다 못 빼냈다.")
    print()


def lesson7_practice():
    # =========================================================================
    #   레슨 7 — 실전: 30주 시계열 가법 분해
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 가법 분해 직접 해보기     │")
    print("└──────────────────────────────────────┘")
    random.seed(1)
    period = 7
    n = 30
    Y = [40 + 0.8 * t + 8 * math.sin(2 * math.pi * t / period) + random.gauss(0, 1.5) for t in range(n)]

    # 1) Trend = 7-MA
    T = moving_average(Y, window=period)
    # 2) Detrended
    D = [(y - t) if t is not None else None for y, t in zip(Y, T)]
    # 3) 계절 슬롯 평균 → S 패턴 (length=period)
    slot_values = {i: [] for i in range(period)}
    for t, d in enumerate(D):
        if d is not None:
            slot_values[t % period].append(d)
    S_pattern = {i: sum(v) / len(v) if v else 0.0 for i, v in slot_values.items()}
    # 중심 0 으로 보정 (옵션)
    pattern_mean = sum(S_pattern.values()) / period
    S_pattern = {k: v - pattern_mean for k, v in S_pattern.items()}
    # 4) 전 구간 S(t)
    S = [S_pattern[t % period] for t in range(n)]
    # 5) Residual
    R = [(y - (t if t is not None else 0) - s) for y, t, s in zip(Y, T, S)]

    print(" t |   Y   |   T   |   S   |   R")
    for t in range(n):
        T_str = f"{T[t]:6.2f}" if T[t] is not None else "  --- "
        print(f"{t:>2} | {Y[t]:5.2f} | {T_str} | {S[t]:6.2f} | {R[t]:6.2f}")
    print()
    # ■ 관찰 포인트:
    #   - 양 끝 6 시점은 T 가 비어있음 (window=7 의 한계)
    #   - 가운데 구간 R 은 평균 0 근처에 머물러야 함
    #   - 잔차가 큰 시점(±3σ 이상)을 “이상치 후보”로 표시할 수 있음 → 15단계 이상탐지의 첫 단추


# ─────────────────────────────────────────────────────────────────────────
# ■ 연습문제
# ─────────────────────────────────────────────────────────────────────────
#  Q1. 매출 = 100 × (1 + 0.05*t) × (1 + 0.2*sin(2π t/12)) 의 데이터는 가법/승법 중 무엇으로 다뤄야 하나?
#  Q2. 위 문제에서 로그 변환을 취하면 가법 형태로 바뀜을 수식으로 보여라.
#  Q3. STL 분해의 robust=True 옵션은 어떤 상황에서 필수인가?
#  Q4. 잔차의 Ljung-Box 검정에서 p-value=0.02 가 나왔다면 모델은 충분한가? 보강 전략 두 가지를 제시하라.
#  Q5. period 후보를 어떻게 정하나? (힌트: 도메인 + ACF 첫 큰 봉우리 + 푸리에 변환)


if __name__ == "__main__":
    lesson1_why_decompose()
    lesson2_additive_vs_multiplicative()
    lesson3_trend_via_ma()
    lesson4_seasonality_average()
    lesson5_stl_concept()
    lesson6_residual_diagnostics()
    lesson7_practice()
