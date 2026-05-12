# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [시계열] 학습 07단계: 피처 엔지니어링
#   ─ lag / rolling / EWM / calendar / Fourier / target encoding ─
#   ■ 실행 방법: python 07_feature_engineering.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 시계열을 “테이블” 로 바꾸는 첫 단계 — lag feature
#   2. Rolling 윈도우 통계 (mean, std, min, max)
#   3. EWM(지수이동평균) — 최근값에 더 큰 가중
#   4. Calendar feature (요일, 월, 공휴일, 연휴 직전/직후)
#   5. Fourier 피처 — 연속적 계절성 표현
#   6. Target / Group encoding — 카테고리 시계열에서 유용
#   7. 실전: 30일 매출 데이터 → 피처 매트릭스로 변환
#
# ─────────────────────────────────────────────────────────────────────────

import math
import random


def lesson1_lag_features():
    # =========================================================================
    #   레슨 1 — Lag feature
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : Lag feature                │")
    print("└──────────────────────────────────────┘")
    # ■ 핵심 아이디어: 시계열 Y(t) 를 예측할 때, 과거 값 Y(t-1), Y(t-7), Y(t-30) 을 ‘피처’로 사용.
    # ■ ML 모델은 시간을 모름 → 피처로 ‘시간 패턴’을 명시해주는 작업.
    #
    #   ┌───────┬───────┬───────┬───────┐
    #   |  Y_t  | Y_{t-1}| Y_{t-7}| Y_{t-30}|  ← 이 행이 ‘하나의 학습 샘플’
    #   └───────┴───────┴───────┴───────┘
    #
    # ■ 주의:
    #   - lag 만들 때 미래 누설(leakage) 금지 — “현재 시점에서 알 수 있는 과거”만.
    #   - 학습 시작 행에서 NaN 이 생김 → 적절히 drop 또는 보간.
    print(" lag = ‘과거 값 자체’를 피처로.  ML 의 입력에는 거의 항상 포함.")
    print()


def lesson2_rolling():
    # =========================================================================
    #   레슨 2 — Rolling
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : Rolling window             │")
    print("└──────────────────────────────────────┘")
    # ■ rolling_mean_7   : 최근 7일 평균 (단기 추세)
    # ■ rolling_std_30   : 최근 30일 변동성
    # ■ rolling_max_7    : 최근 7일 최댓값 (피크 detection)
    #
    # ■ 함정:
    #   - center=True 로 만들면 ‘미래’가 평균에 들어감 → ML 학습용으론 금지!
    #   - 항상 “과거만 보는 right-aligned” 윈도우 사용.
    series = [10, 12, 13, 14, 15, 17, 18, 19, 21, 22, 21, 20]
    win = 3
    rolling_mean = []
    for t in range(len(series)):
        if t + 1 < win:
            rolling_mean.append(None)
        else:
            rolling_mean.append(sum(series[t - win + 1 : t + 1]) / win)
    for t, (s, r) in enumerate(zip(series, rolling_mean)):
        r_str = f"{r:.2f}" if r is not None else "  -- "
        print(f" t={t:>2} | Y={s:>3} | rolling_mean({win})={r_str}")
    print()


def lesson3_ewm():
    # =========================================================================
    #   레슨 3 — EWM
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : EWM (지수가중)             │")
    print("└──────────────────────────────────────┘")
    # ■ EWM_t = α Y_t + (1-α) EWM_{t-1}      (SES 와 같은 식!)
    # ■ 의미: 최근값에 더 큰 가중, 옛 값에 점차 작은 가중
    # ■ pandas: df["y"].ewm(span=10, adjust=False).mean()
    series = [10, 12, 13, 14, 15, 17, 18, 19, 21, 22]
    alpha = 0.4
    ewm = [series[0]]
    for t in range(1, len(series)):
        ewm.append(alpha * series[t] + (1 - alpha) * ewm[-1])
    print(" t |  Y  | EWM(α=0.4)")
    for t, (s, e) in enumerate(zip(series, ewm)):
        print(f"{t:>2} | {s:>3} | {e:6.2f}")
    print()


def lesson4_calendar():
    # =========================================================================
    #   레슨 4 — Calendar feature
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : Calendar feature           │")
    print("└──────────────────────────────────────┘")
    # ■ 자주 쓰는 calendar feature:
    #   - dayofweek (월=0,…,일=6)
    #   - is_weekend
    #   - dayofmonth, month, quarter, weekofyear
    #   - is_holiday  (공휴일 캘린더 참조)
    #   - days_to_next_holiday / days_since_last_holiday
    #   - is_payday   (월급일 직후 매출 증가 패턴)
    #
    # ■ 인코딩 팁:
    #   - 카테고리(요일, 월) 는 원-핫 또는 “순환 인코딩”(sin/cos)
    #     sin(2π·dow/7), cos(2π·dow/7)  ← 일요일→월요일 거리 보존
    for dow in range(7):
        s = math.sin(2 * math.pi * dow / 7)
        c = math.cos(2 * math.pi * dow / 7)
        print(f" dow={dow}  sin={s:+.3f}  cos={c:+.3f}")
    print()


def lesson5_fourier():
    # =========================================================================
    #   레슨 5 — Fourier 피처
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : Fourier 피처               │")
    print("└──────────────────────────────────────┘")
    # ■ 임의 주기 m 에 대해 K 차수의 Fourier 항을 추가:
    #     sin(2π k t / m), cos(2π k t / m),  k = 1..K
    # ■ 효과:
    #   - 연속 시간에서 부드러운 계절성 표현
    #   - Prophet 모델이 내부적으로 이 방식 사용
    #
    # ■ 직관:
    #   - m=365.25 (연), K=10 정도면 1년 안의 다양한 봉우리/골짜기를 매끈하게 표현
    print(" Fourier 피처는 ‘연속/혼합 주기’의 계절성을 잘 표현한다 (Prophet 핵심).")
    print()


def lesson6_target_encoding():
    # =========================================================================
    #   레슨 6 — Target / Group encoding
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : Target encoding            │")
    print("└──────────────────────────────────────┘")
    # ■ 카테고리 변수(매장ID, 상품ID 등)를 “그 카테고리의 과거 평균 매출”로 대체.
    # ■ 시계열에서는 반드시 “과거만” 으로 평균 계산해야 함 (rolling target encoding).
    #
    # ■ 예 (rolling 60일):
    #     store_avg_sales_60d[t] = mean(sales[t-60:t]) for the same store
    #
    # ■ 함정:
    #   - 미래 누설: 전체 평균 한 번 계산하고 모든 행에 붙이면 시계열 데이터 누설.
    #   - 데이터 적은 카테고리는 smoothing 필요 (글로벌 평균에 가중 평균).
    print(" Target encoding 은 ‘롤링’으로만.  전체 평균 = 누설!")
    print()


def lesson7_practice_feature_table():
    # =========================================================================
    #   레슨 7 — 실전: 30일 데이터 → 피처 매트릭스
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 피처 매트릭스 만들기       │")
    print("└──────────────────────────────────────┘")
    random.seed(0)
    n = 30
    sales = [100 + 1.2 * t + 15 * math.sin(2 * math.pi * t / 7) + random.gauss(0, 4) for t in range(n)]

    print(" t  |  y     | y_lag1 | y_lag7 | ma7    | dow_sin | dow_cos")
    for t in range(n):
        y = sales[t]
        y_lag1 = sales[t - 1] if t >= 1 else None
        y_lag7 = sales[t - 7] if t >= 7 else None
        ma7 = sum(sales[t - 6 : t + 1]) / 7 if t >= 6 else None
        dow = t % 7
        ds = math.sin(2 * math.pi * dow / 7)
        dc = math.cos(2 * math.pi * dow / 7)
        l1 = f"{y_lag1:6.2f}" if y_lag1 is not None else "  --- "
        l7 = f"{y_lag7:6.2f}" if y_lag7 is not None else "  --- "
        m7 = f"{ma7:6.2f}" if ma7 is not None else "  --- "
        print(f"{t:>3} | {y:6.2f} | {l1} | {l7} | {m7} | {ds:+.3f}  | {dc:+.3f}")
    print()
    # 이 표를 그대로 XGBoost 등에 학습시키면 “시계열 = 표 형식 ML 문제”로 풀린다.


# ─────────────────────────────────────────────────────────────────────────
# ■ 연습문제
# ─────────────────────────────────────────────────────────────────────────
#  Q1. 미래 누설 없이 “전월 동일자 평균 매출”을 피처로 만드는 절차를 적어라.
#  Q2. dow 를 sin/cos 로 인코딩하면 어떤 정보 손실이 있는가? 보완책은?
#  Q3. EWM 의 span 과 α 의 관계 (α = 2/(span+1)) 를 이용해 span=10 의 α 를 구하라.
#  Q4. 데이터가 적은 신규 매장은 target encoding 에서 어떤 위험이 있나? 글로벌 평균 가중 smoothing 식을 작성하라.
#  Q5. Prophet 의 Fourier 피처가 ARIMA 의 계절차분과 비교했을 때 어떤 장점을 갖는가?


if __name__ == "__main__":
    lesson1_lag_features()
    lesson2_rolling()
    lesson3_ewm()
    lesson4_calendar()
    lesson5_fourier()
    lesson6_target_encoding()
    lesson7_practice_feature_table()
