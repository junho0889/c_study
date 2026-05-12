# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [시계열] 학습 08단계: 머신러닝 기반 예측
#   ─ RandomForest · XGBoost · LightGBM · CatBoost 의 시계열 적용 ─
#   ■ 실행 방법: python 08_ml_forecasting.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 시계열을 ML 문제로 변환 (지도학습 회귀)
#   2. Tree-based 모델이 시계열에 강한 이유
#   3. Direct vs Recursive vs MIMO 예측 전략
#   4. 글로벌(global) 모델 vs 로컬(local) 모델
#   5. 부스팅 하이퍼파라미터 핵심
#   6. SHAP 으로 ‘무엇이 매출을 끌어올렸나?’ 해석
#   7. 실전: 간단한 결정트리 직접 학습 (depth=2) 로 lag 회귀
#
# ─────────────────────────────────────────────────────────────────────────

import math
import random


def lesson1_to_supervised():
    # =========================================================================
    #   레슨 1 — 시계열 → 회귀 문제 변환
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 회귀 문제로 변환           │")
    print("└──────────────────────────────────────┘")
    # ■ Y(t) 를 예측 = 회귀 문제 풀기
    #     y     = f(x1, x2, …)
    #     Y(t)  = f(Y(t-1), Y(t-7), rolling_mean_7, dow, holiday, X(t-1), …)
    #
    # ■ 07단계의 피처 매트릭스가 곧 학습 입력.
    #
    # ■ scikit-learn 인터페이스가 그대로 사용 가능:
    #     from xgboost import XGBRegressor
    #     model = XGBRegressor(n_estimators=500, max_depth=6, learning_rate=0.05)
    #     model.fit(X_train, y_train)
    #     model.predict(X_test)
    print(" 시계열 = ‘과거 + 보조변수 → 미래 회귀’ 라는 표 형식 문제로 변환")
    print()


def lesson2_why_trees():
    # =========================================================================
    #   레슨 2 — 트리 기반이 강한 이유
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : Tree 가 강한 이유          │")
    print("└──────────────────────────────────────┘")
    # ■ 시계열 회귀 캐글/실무 단골 우승 = XGBoost / LightGBM / CatBoost.
    #
    # ■ 이유:
    #   1) 비선형 + 상호작용을 자동으로 잡음
    #   2) 카테고리 / 수치 혼합 입력 처리에 강함
    #   3) 결측치, 이상치에 비교적 강건
    #   4) 빠른 학습 / 추론
    #   5) SHAP/feature_importance 로 설명 가능
    #
    # ■ 한계:
    #   - 외삽(extrapolation) 약함 → 과거 보지 못한 ‘완전 새 레벨’에 약함
    #     → 변화에 강한 추세 피처(diff, momentum)나 ETS 잔차 학습으로 보강
    print(" 표 형식 시계열 회귀의 ‘기본 우승 무기’ = 부스팅 트리.")
    print()


def lesson3_strategies():
    # =========================================================================
    #   레슨 3 — 다중 horizon 전략
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : Direct / Recursive / MIMO  │")
    print("└──────────────────────────────────────┘")
    # ■ Direct:
    #   - 각 horizon h 마다 별도 모델: f_h(X_t) = Y_{t+h}
    #   - 장점: h 마다 최적화 가능, 오차 누적 없음
    #   - 단점: 모델 H 개 → 학습/유지비용↑
    #
    # ■ Recursive (iterative):
    #   - 1-step 모델로 ŷ_{t+1} 만든 뒤, 다음 입력에 ŷ 를 넣어 ŷ_{t+2} ...
    #   - 장점: 모델 1개
    #   - 단점: 오차 누적
    #
    # ■ MIMO (multi-output):
    #   - 한 모델이 [ŷ_{t+1}, …, ŷ_{t+H}] 를 한 번에 출력
    #   - 장점: horizon 간 일관성, 비용↓
    #   - 단점: 단일 모델로 H 다 최적화 어려움
    #
    # ■ 라이브러리: sktime, mlforecast, neuralforecast 가 자동으로 처리
    print(" Direct / Recursive / MIMO 의 trade-off 를 horizon 길이/도메인에 맞춰 선택.")
    print()


def lesson4_global_vs_local():
    # =========================================================================
    #   레슨 4 — Global vs Local
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : Global vs Local            │")
    print("└──────────────────────────────────────┘")
    # ■ Local: 매장/상품/센서마다 별도 모델 → 데이터 적으면 약함, 유지 비용↑
    # ■ Global: 모든 시계열을 한 모델에 — feature 로 “id” 를 인코딩
    #   - 작은 시계열도 다른 시계열에서 정보 차용
    #   - 부스팅/딥러닝의 표준
    #   - 베이스라인은 보통 Global LightGBM
    print(" 다수 시계열 = Global 모델로 시작.  부족한 시리즈는 글로벌이 보완.")
    print()


def lesson5_hyperparams():
    # =========================================================================
    #   레슨 5 — 부스팅 하이퍼파라미터
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 하이퍼파라미터             │")
    print("└──────────────────────────────────────┘")
    # ■ 핵심 4종:
    #   - n_estimators : 트리 개수 (early stopping 으로 자동)
    #   - learning_rate: 0.01 ~ 0.1
    #   - max_depth    : 4 ~ 8
    #   - min_child_weight / min_data_in_leaf: 과적합 억제
    #
    # ■ 시계열용 추가:
    #   - objective = "regression" 또는 "tweedie" (대량 0/소량 수요)
    #   - eval_metric = "rmse" / "mae"  (도메인에 맞춰)
    #   - subsample / colsample_bytree 로 ‘다양성’ 부여
    #
    # ■ 튜닝:
    #   - Optuna + walk-forward CV 가 강력
    print(" 보통 leaf-wise(LightGBM)는 max_depth 보다 num_leaves 로 통제.")
    print()


def lesson6_shap():
    # =========================================================================
    #   레슨 6 — SHAP 해석
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : SHAP                       │")
    print("└──────────────────────────────────────┘")
    # ■ SHAP value:
    #   - 각 피처가 “해당 예측값” 을 얼마나 끌어올렸는지/내렸는지 정량 분해.
    #   - 합: SHAP_sum + base = prediction
    #
    # ■ 실용:
    #   - 어느 매장의 매출 급증을 “요일/이벤트/광고/날씨” 중 무엇이 이끌었는지 분석
    #   - 이상치(예측↔실제 큰 차이) 디버깅에도 사용
    #
    # ■ 시계열 SHAP 주의:
    #   - lag 피처가 많을수록 ‘과거 자기 자신 영향’이 압도적
    #   - 외생변수의 영향을 보고 싶으면 그 변수만 따로 떼서 비교
    print(" SHAP = 모델 결정의 ‘이유’를 숫자로 분해.  의사결정 보고서에 강력.")
    print()


def lesson7_practice_tiny_tree():
    # =========================================================================
    #   레슨 7 — 실전: depth=2 단일 트리 학습
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 미니 결정트리 직접 학습    │")
    print("└──────────────────────────────────────┘")
    random.seed(0)
    n = 60
    series = [100 + 0.5 * t + 10 * math.sin(2 * math.pi * t / 7) + random.gauss(0, 3) for t in range(n)]

    # 피처: (Y_{t-1}, dow)  / 타깃: Y_t
    samples = []
    for t in range(1, n):
        samples.append({"y_lag1": series[t - 1], "dow": t % 7, "y": series[t]})

    train = samples[:50]
    test = samples[50:]

    # 아주 단순한 split 탐색 (수치 피처는 중앙값, 카테고리 피처는 ‘주말 vs 평일’)
    def mse(group):
        if not group:
            return 0.0
        m = sum(g["y"] for g in group) / len(group)
        return sum((g["y"] - m) ** 2 for g in group) / len(group)

    # split 1: 주말 여부
    weekend = [g for g in train if g["dow"] >= 5]
    weekday = [g for g in train if g["dow"] < 5]

    # 각 리프 내에서 y_lag1 중앙값으로 다시 split (depth 2)
    def leaf(group):
        if not group:
            return None
        m = sorted(g["y_lag1"] for g in group)[len(group) // 2]
        low = [g for g in group if g["y_lag1"] <= m]
        high = [g for g in group if g["y_lag1"] > m]
        pred_low = sum(g["y"] for g in low) / len(low) if low else 0
        pred_high = sum(g["y"] for g in high) / len(high) if high else 0
        return (m, pred_low, pred_high)

    leaf_we = leaf(weekend)
    leaf_wd = leaf(weekday)
    print(f" 주말 리프  median(y_lag1)={leaf_we[0]:.2f}, low pred={leaf_we[1]:.2f}, high pred={leaf_we[2]:.2f}")
    print(f" 평일 리프  median(y_lag1)={leaf_wd[0]:.2f}, low pred={leaf_wd[1]:.2f}, high pred={leaf_wd[2]:.2f}")

    # test 예측
    abs_err = 0.0
    for g in test:
        leaf_def = leaf_we if g["dow"] >= 5 else leaf_wd
        pred = leaf_def[1] if g["y_lag1"] <= leaf_def[0] else leaf_def[2]
        abs_err += abs(pred - g["y"])
    print(f" 테스트 MAE (depth=2 트리) = {abs_err / len(test):.2f}")
    print(" → XGBoost 같은 부스팅은 이런 작은 트리를 수백 개 합쳐 점수를 끌어올린다.")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 연습문제
# ─────────────────────────────────────────────────────────────────────────
#  Q1. Recursive 예측에서 오차가 누적되는 메커니즘을 한 줄 식으로 설명하라.
#  Q2. 신규 SKU(상품) 라서 데이터가 거의 없을 때 글로벌 모델이 유리한 이유는?
#  Q3. LightGBM 의 num_leaves=255, max_depth=4 의 충돌이 일어날 수 있다. 어느 쪽이 우선?
#  Q4. SHAP value 가 ‘로컬 해석’이라 불리는 이유는?
#  Q5. 위 미니 트리에서 split 기준을 ‘주말 vs 평일’ 외에 어떤 더 좋은 후보가 있는지 적어라.


if __name__ == "__main__":
    lesson1_to_supervised()
    lesson2_why_trees()
    lesson3_strategies()
    lesson4_global_vs_local()
    lesson5_hyperparams()
    lesson6_shap()
    lesson7_practice_tiny_tree()
