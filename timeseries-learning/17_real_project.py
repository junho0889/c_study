# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [시계열] 학습 17단계: 실전 프로젝트
#   ─ 다변량 센서 → ETL → 예측 + 이상탐지 + 알림까지 ─
#   ■ 실행 방법: python 17_real_project.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 프로젝트 시나리오
# ─────────────────────────────────────────────────────────────────────────
#
#   가상 공장에서 5분 단위로 들어오는 3 개 센서(온도, 진동, 전류) 데이터를
#   ① 수집 → ② 정제 → ③ 정상성 점검 → ④ 다음 1 시간 예측 → ⑤ 이상 탐지
#   → ⑥ 알림(콘솔) 까지 한 파이프라인으로 통합한다.
#
#   본 파일은 “데이터 흐름과 사고 절차”의 데모입니다.
#   실제 운영 코드는 numpy/pandas/statsmodels/torch + Kafka/Airflow 위에 올립니다.
#
# ─────────────────────────────────────────────────────────────────────────

import math
import random


# ─────────────────────────────────────────────────────────────────────────
# 1) 데이터 수집(시뮬레이션)
# ─────────────────────────────────────────────────────────────────────────
def generate_sensor_stream(n_minutes=24 * 60):
    """
    5분 간격으로 n_minutes/5 개 샘플 생성.
    온도: 평균 70 °C, 일주기 변동
    진동: 평균 0.5,   주기 변동 + 노이즈
    전류: 평균 10A,   드리프트 + 노이즈
    """
    random.seed(0)
    rows = []
    for k in range(n_minutes // 5):
        t = k * 5  # 분
        temp = 70 + 5 * math.sin(2 * math.pi * t / (60 * 24)) + random.gauss(0, 0.5)
        vib = 0.5 + 0.1 * math.sin(2 * math.pi * t / (60 * 6)) + random.gauss(0, 0.05)
        cur = 10 + 0.001 * t + random.gauss(0, 0.1)         # 천천히 드리프트
        rows.append({"t_min": t, "temp": temp, "vib": vib, "cur": cur})

    # 이상 이벤트 주입 (가짜 결함 시뮬레이션)
    if len(rows) > 200:
        rows[180]["temp"] += 8          # 점프 이상 (point)
        for i in range(220, 230):
            rows[i]["vib"] += 0.4       # collective 이상 (구간)
        rows[260]["cur"] += 1.5         # contextual 이상
    return rows


# ─────────────────────────────────────────────────────────────────────────
# 2) 정제 — 결측/이상치/시간 정렬
# ─────────────────────────────────────────────────────────────────────────
def clean(rows):
    """간단한 정제: 시간 등간격 보장, NaN forward-fill 흉내"""
    cleaned = []
    last_t = None
    for r in rows:
        # 등간격(5분) 확인
        if last_t is not None and r["t_min"] - last_t != 5:
            # gap 발견 — forward fill (실무에서는 보간 다양)
            missing = (r["t_min"] - last_t) // 5 - 1
            for _ in range(missing):
                cleaned.append(dict(cleaned[-1]))   # 직전 값 복사
        cleaned.append(r)
        last_t = r["t_min"]
    return cleaned


# ─────────────────────────────────────────────────────────────────────────
# 3) 정상성 점검(간이) — rolling mean/std 추세 확인
# ─────────────────────────────────────────────────────────────────────────
def rolling_stats(values, window):
    out = []
    for i in range(len(values)):
        if i + 1 < window:
            out.append((None, None))
        else:
            w = values[i - window + 1 : i + 1]
            m = sum(w) / window
            s = math.sqrt(sum((v - m) ** 2 for v in w) / window)
            out.append((m, s))
    return out


def stationarity_check(rows, key="cur"):
    vals = [r[key] for r in rows]
    rs = rolling_stats(vals, window=60)   # 5 시간 윈도우
    # 처음 / 마지막 평균 비교
    first_m = next((m for m, s in rs if m is not None), 0)
    last_m = next((m for m, s in reversed(rs) if m is not None), 0)
    drift = last_m - first_m
    return drift


# ─────────────────────────────────────────────────────────────────────────
# 4) 예측 — 단순 baseline (마지막 윈도우 평균)
# ─────────────────────────────────────────────────────────────────────────
def forecast_next_h(values, h=12, window=12):
    """다음 h step (= 1시간) 을 직전 window 의 평균으로 예측"""
    base = sum(values[-window:]) / window
    return [base] * h


# ─────────────────────────────────────────────────────────────────────────
# 5) 이상 탐지 — 잔차 기반(예측 vs 실제)
# ─────────────────────────────────────────────────────────────────────────
def detect_anomalies(values, predictions, threshold=3.0):
    """
    predictions[t] 는 ‘t 시점 이전의 정보로 만든 t 시점 예측’.
    잔차 = 실제 - 예측, |z| > threshold 면 이상.
    """
    errs = []
    for t, (y, p) in enumerate(zip(values, predictions)):
        if p is None:
            errs.append(0.0)
        else:
            errs.append(y - p)
    if not errs:
        return []
    mean = sum(errs) / len(errs)
    std = math.sqrt(sum((e - mean) ** 2 for e in errs) / len(errs)) or 1e-9
    alerts = []
    for t, e in enumerate(errs):
        z = (e - mean) / std
        if abs(z) > threshold:
            alerts.append((t, e, z))
    return alerts


# ─────────────────────────────────────────────────────────────────────────
# 6) 알림 — 콘솔 출력 (실무: Slack / 이메일 / Kafka)
# ─────────────────────────────────────────────────────────────────────────
def notify(alerts, sensor):
    if not alerts:
        print(f" [{sensor}] 이상 없음 ✅")
        return
    print(f" [{sensor}] 이상 {len(alerts)} 건:")
    for t, e, z in alerts[:5]:
        print(f"   - t_idx={t}, residual={e:+.3f}, z={z:+.2f}")
    if len(alerts) > 5:
        print(f"   ... 외 {len(alerts)-5} 건")


# ─────────────────────────────────────────────────────────────────────────
# 메인 파이프라인
# ─────────────────────────────────────────────────────────────────────────
def main():
    print("┌─────────────────────────────────────────────┐")
    print("│  시계열 통합 파이프라인 (시뮬레이션)        │")
    print("└─────────────────────────────────────────────┘")

    print("\n[1/6] 데이터 수집 ...")
    rows = generate_sensor_stream(n_minutes=24 * 60)
    print(f"  → {len(rows)} 샘플 수신 (5분 간격, 총 24시간)")

    print("\n[2/6] 정제 ...")
    rows = clean(rows)
    print(f"  → 등간격 확인 완료, 행 수 = {len(rows)}")

    print("\n[3/6] 정상성 점검 ...")
    drift = stationarity_check(rows, key="cur")
    print(f"  → 전류(cur) 채널의 평균 드리프트 ≈ {drift:+.3f} A (양수면 우상향 비정상)")

    print("\n[4/6] 다음 1시간 예측 ...")
    for ch in ["temp", "vib", "cur"]:
        vals = [r[ch] for r in rows]
        future = forecast_next_h(vals, h=12, window=12)
        print(f"  {ch} 미래 12개 예측 평균 = {sum(future)/len(future):.3f}")

    print("\n[5/6] 이상 탐지 (잔차 기반) ...")
    for ch in ["temp", "vib", "cur"]:
        vals = [r[ch] for r in rows]
        # walk-forward 예측: t 시점의 예측은 [t-12, t-1] 평균
        preds = [None] * 12
        for t in range(12, len(vals)):
            preds.append(sum(vals[t - 12 : t]) / 12)
        alerts = detect_anomalies(vals, preds, threshold=3.5)
        notify(alerts, sensor=ch)

    print("\n[6/6] 완료. 운영에서는 Kafka → Flink → DB → BI Dashboard 로 흐름을 잇는다.")


# ─────────────────────────────────────────────────────────────────────────
# ■ 확장 아이디어 (직접 해보기)
# ─────────────────────────────────────────────────────────────────────────
#  1) baseline 예측을 ARIMA / LSTM / N-BEATS / Foundation 모델로 교체해 비교
#  2) 이상 탐지를 Isolation Forest / Autoencoder 로 교체
#  3) 알림 채널을 Slack Webhook + 이메일 + 사내 ITSM 으로 확장
#  4) 다변량(temp+vib+cur) 모델로 한 번에 학습 (VAR 또는 PatchTST)
#  5) Concept drift 점검 — PSI 가 임계값 넘으면 ‘재학습 트리거’


if __name__ == "__main__":
    main()
