# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#   파이썬 ML 학습 08단계: 차원 축소 (Dimensionality Reduction)
#   ─ 데이터의 핵심만 남기고 줄이기 ─
#
#   비유: 그림자 투영
#     3차원 물체에 빛을 비추면 2차원 그림자가 생깁니다.
#     어떤 각도로 비추느냐에 따라 물체의 모양이 잘 보이기도,
#     안 보이기도 합니다. PCA는 "가장 정보가 많이 보이는
#     각도"를 찾아서 투영하는 것입니다.
#
#   실행 방법:
#     python 08_dimensionality_reduction.py
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import random


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 1: 차원의 저주
# ─────────────────────────────────────────────────────────────────────────

def lesson1_curse_of_dimensionality():
    """
    차원이 높아지면 데이터가 희박해져서 학습이 어려워집니다.

    비유: 방에서 사람 찾기
      1D: 복도에서 사람 찾기 → 쉬움
      2D: 운동장에서 찾기 → 좀 넓네
      3D: 빌딩 전체에서 찾기 → 어려움
      100D: 100차원 공간에서 찾기 → 거의 불가능!
    """
    print("=" * 70)
    print("[레슨 1] 차원의 저주 (Curse of Dimensionality)")
    print("=" * 70)
    print()
    print("  차원이 높아지면 생기는 문제:")
    print()

    # 공간의 부피와 필요한 데이터 수
    print("  단위 공간 안에 10개 구간으로 나눌 때:")
    print("  ┌──────────┬─────────────────┬─────────────────┐")
    print("  │  차원    │  격자 칸 수      │  필요 데이터    │")
    print("  ├──────────┼─────────────────┼─────────────────┤")

    for dim in [1, 2, 3, 5, 10, 20]:
        cells = 10 ** dim
        cells_str = f"{cells:,.0f}" if cells < 1e10 else f"10^{dim}"
        print(f"  │  {dim:>5}   │  {cells_str:>15s} │  {cells_str:>15s} │")

    print("  └──────────┴─────────────────┴─────────────────┘")
    print()

    # 거리 문제: 고차원에서 모든 점이 비슷하게 멀어짐
    print("  고차원에서의 거리 문제:")
    random.seed(42)

    for dim in [2, 10, 100, 1000]:
        distances = []
        for _ in range(100):
            a = [random.random() for _ in range(dim)]
            b = [random.random() for _ in range(dim)]
            dist = math.sqrt(sum((x-y)**2 for x, y in zip(a, b)))
            distances.append(dist)

        avg_dist = sum(distances) / len(distances)
        min_dist = min(distances)
        max_dist = max(distances)
        ratio = max_dist / min_dist if min_dist > 0 else 0

        print(f"    {dim:>4}차원: 평균거리={avg_dist:.2f}, "
              f"최대/최소 비율={ratio:.2f}")

    print()
    print("  → 차원이 높아지면 최대/최소 비율이 1에 가까워짐")
    print("  → 모든 점이 비슷하게 멀어서 구별이 어려워짐!")
    print("  → 해결책: 차원 축소 (불필요한 차원을 제거)")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 2: PCA 개념 (주성분 분석)
# ─────────────────────────────────────────────────────────────────────────

def lesson2_pca_concept():
    """
    PCA: 데이터의 분산이 가장 큰 방향을 찾아 그쪽으로 투영.

    비유: 그림자 투영
      긴 막대를 빛으로 비출 때,
      옆에서 비추면 긴 그림자(정보 많음)
      위에서 비추면 점 하나(정보 없음)
      PCA는 "가장 긴 그림자가 나오는 방향"을 찾습니다.
    """
    print("=" * 70)
    print("[레슨 2] PCA 개념 (주성분 분석)")
    print("=" * 70)
    print()
    print("  비유: 가장 정보가 많이 보이는 그림자 각도 찾기")
    print()

    # 2D → 1D PCA 예시
    random.seed(42)
    # 키와 팔 길이 (상관관계 있음)
    data = []
    for _ in range(10):
        height = random.gauss(170, 10)
        arm = height * 0.44 + random.gauss(0, 2)  # 키와 비례
        data.append([height, arm])

    print("  데이터: 키(cm)와 팔 길이(cm) - 상관관계 높음")
    print("  ┌──────────┬──────────┐")
    print("  │ 키(cm)   │팔 길이   │")
    print("  ├──────────┼──────────┤")
    for h, a in data[:5]:
        print(f"  │ {h:>7.1f}  │ {a:>7.1f}  │")
    print("  │   ...    │   ...    │")
    print("  └──────────┴──────────┘")
    print()

    # Step 1: 평균 중심화
    mean_h = sum(d[0] for d in data) / len(data)
    mean_a = sum(d[1] for d in data) / len(data)
    centered = [[d[0] - mean_h, d[1] - mean_a] for d in data]

    print(f"  Step 1: 평균 중심화 (평균: 키={mean_h:.1f}, 팔={mean_a:.1f})")

    # Step 2: 공분산 행렬
    n = len(data)
    cov_hh = sum(c[0]**2 for c in centered) / n
    cov_aa = sum(c[1]**2 for c in centered) / n
    cov_ha = sum(c[0]*c[1] for c in centered) / n

    print(f"  Step 2: 공분산 행렬")
    print(f"    [{cov_hh:.2f}, {cov_ha:.2f}]")
    print(f"    [{cov_ha:.2f}, {cov_aa:.2f}]")
    print()

    # Step 3: 주성분 방향 (2×2 행렬의 고유벡터 근사)
    # 간단하게: 데이터의 분산이 가장 큰 방향 찾기
    total_var = cov_hh + cov_aa
    print(f"  Step 3: 분산 분석")
    print(f"    키의 분산: {cov_hh:.2f} ({cov_hh/total_var*100:.1f}%)")
    print(f"    팔의 분산: {cov_aa:.2f} ({cov_aa/total_var*100:.1f}%)")
    print()
    print("  → 키 방향이 분산이 크므로 '키 방향'이 제1 주성분!")
    print("  → 2D 데이터를 키 방향 1D로 줄여도 대부분의 정보 유지")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 3: 설명된 분산 비율
# ─────────────────────────────────────────────────────────────────────────

def lesson3_explained_variance():
    """
    설명된 분산: 각 주성분이 전체 정보의 몇 %를 담고 있는지.

    비유: 사진 압축
      주성분1 = 사진의 대략적인 윤곽 (70% 정보)
      주성분2 = 세부 디테일 (20% 정보)
      주성분3 = 미세한 질감 (8% 정보)
      주성분4 = 노이즈 (2% 정보) ← 버려도 됨!
    """
    print("=" * 70)
    print("[레슨 3] 설명된 분산 비율")
    print("=" * 70)
    print()

    # 가상의 5차원 데이터의 설명된 분산 비율
    explained_ratios = [0.45, 0.25, 0.15, 0.10, 0.05]
    components = ["PC1", "PC2", "PC3", "PC4", "PC5"]

    print("  5차원 데이터의 주성분별 설명 비율:")
    print()

    cumulative = 0
    print("  ┌──────┬──────────┬──────────┬───────────────────────┐")
    print("  │  PC  │  분산%   │  누적%   │  시각화               │")
    print("  ├──────┼──────────┼──────────┼───────────────────────┤")

    for pc, ratio in zip(components, explained_ratios):
        cumulative += ratio
        bar = "#" * int(ratio * 40)
        cum_bar = "=" * int(cumulative * 20)
        print(f"  │ {pc:>4s} │  {ratio:>6.0%}  │  {cumulative:>6.0%}  │ {bar:<21s} │")

    print("  └──────┴──────────┴──────────┴───────────────────────┘")
    print()
    print("  보통 누적 분산 95% 이상이면 충분합니다.")
    print("  이 경우: PC1~PC3만 사용 (5차원 → 3차원, 정보 85% 유지)")
    print()

    # 차원 축소 전후 비교
    print("  차원 축소 효과:")
    print("    원본: 5차원, 100% 정보")
    print("    3차원: 85% 정보 유지, 계산 40% 감소")
    print("    2차원: 70% 정보 유지, 시각화 가능!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 4: 특성 중요도
# ─────────────────────────────────────────────────────────────────────────

def lesson4_feature_importance():
    """
    어떤 특성이 중요한지, 어떤 건 버려도 되는지 파악하기.

    비유: 시험 공부할 때
      "이 과목은 배점이 높으니 집중하고,
       저 과목은 배점이 낮으니 가볍게 보자"
    """
    print("=" * 70)
    print("[레슨 4] 특성 중요도 (Feature Importance)")
    print("=" * 70)
    print()

    # 가상의 특성 중요도
    features = [
        ("키",         0.35),
        ("몸무게",     0.25),
        ("나이",       0.20),
        ("신발 크기",  0.12),
        ("좋아하는 색", 0.05),
        ("생일 월",    0.03),
    ]

    print("  운동선수 유형 예측에 대한 특성 중요도:")
    print()

    for name, importance in features:
        bar = "#" * int(importance * 60)
        print(f"    {name:>10s}: {importance:.0%} {bar}")

    print()
    print("  해석:")
    print("    키(35%) > 몸무게(25%) > 나이(20%) → 중요!")
    print("    좋아하는 색(5%), 생일 월(3%) → 거의 무관!")
    print()

    # 특성 선택: 중요도 기준으로 버리기
    threshold = 0.1
    selected = [(n, i) for n, i in features if i >= threshold]
    dropped = [(n, i) for n, i in features if i < threshold]

    print(f"  중요도 {threshold:.0%} 이상만 선택:")
    print(f"    유지: {[n for n, _ in selected]}")
    print(f"    제거: {[n for n, _ in dropped]}")
    print(f"    → 6개 특성 → {len(selected)}개로 줄이면서 성능은 유지!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 5: PCA 직접 구현 (2D → 1D)
# ─────────────────────────────────────────────────────────────────────────

def lesson5_pca_implementation():
    """
    간단한 PCA를 직접 구현합니다.
    """
    print("=" * 70)
    print("[레슨 5] PCA 직접 구현 (2D → 1D)")
    print("=" * 70)
    print()

    # 데이터: 상관관계가 있는 2D 점들
    random.seed(42)
    data = []
    for _ in range(8):
        x = random.gauss(0, 3)
        y = x * 0.7 + random.gauss(0, 1)  # x와 상관
        data.append([x, y])

    print("  원본 데이터 (2D):")
    for i, (x, y) in enumerate(data):
        print(f"    점{i}: ({x:>+6.2f}, {y:>+6.2f})")
    print()

    # Step 1: 평균 중심화
    mean_x = sum(d[0] for d in data) / len(data)
    mean_y = sum(d[1] for d in data) / len(data)
    centered = [[d[0] - mean_x, d[1] - mean_y] for d in data]

    # Step 2: 공분산 행렬
    n = len(data)
    cov_xx = sum(c[0]**2 for c in centered) / n
    cov_yy = sum(c[1]**2 for c in centered) / n
    cov_xy = sum(c[0]*c[1] for c in centered) / n

    print(f"  공분산 행렬:")
    print(f"    [{cov_xx:>7.3f}, {cov_xy:>7.3f}]")
    print(f"    [{cov_xy:>7.3f}, {cov_yy:>7.3f}]")
    print()

    # Step 3: 주성분 방향 찾기 (2×2 고유값 공식)
    # 고유값: λ² - (a+d)λ + (ad-bc) = 0
    trace = cov_xx + cov_yy
    det = cov_xx * cov_yy - cov_xy * cov_xy
    discriminant = trace**2 - 4*det

    if discriminant >= 0:
        lambda1 = (trace + math.sqrt(discriminant)) / 2
        lambda2 = (trace - math.sqrt(discriminant)) / 2
    else:
        lambda1 = trace / 2
        lambda2 = trace / 2

    print(f"  고유값: λ1={lambda1:.3f}, λ2={lambda2:.3f}")
    total_var = lambda1 + lambda2
    print(f"  PC1 설명 비율: {lambda1/total_var:.1%}")
    print(f"  PC2 설명 비율: {lambda2/total_var:.1%}")
    print()

    # 고유벡터 (PC1 방향)
    if abs(cov_xy) > 1e-10:
        v1 = [cov_xy, lambda1 - cov_xx]
        norm = math.sqrt(v1[0]**2 + v1[1]**2)
        v1 = [v1[0]/norm, v1[1]/norm]
    else:
        v1 = [1.0, 0.0]

    print(f"  PC1 방향: ({v1[0]:.3f}, {v1[1]:.3f})")
    print()

    # Step 4: 투영 (2D → 1D)
    projected = []
    for c in centered:
        proj = c[0] * v1[0] + c[1] * v1[1]
        projected.append(proj)

    print("  투영 결과 (2D → 1D):")
    for i, (orig, proj) in enumerate(zip(data, projected)):
        bar_pos = int(proj * 3) + 15
        bar_pos = max(0, min(29, bar_pos))
        line = [" "] * 30
        line[bar_pos] = "●"
        print(f"    점{i}: ({orig[0]:>+6.2f},{orig[1]:>+6.2f}) → {proj:>+6.2f} "
              f"{''.join(line)}")
    print()
    print(f"  → 2차원 데이터를 1차원으로 줄이면서 {lambda1/total_var:.0%} 정보 유지!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■" * 72)
    print("  파이썬 ML 08단계 : 차원 축소 (Dimensionality Reduction)")
    print("  비유: 가장 정보가 잘 보이는 그림자 각도 찾기")
    print("■" * 72)
    print()

    lesson1_curse_of_dimensionality()
    lesson2_pca_concept()
    lesson3_explained_variance()
    lesson4_feature_importance()
    lesson5_pca_implementation()


if __name__ == "__main__":
    main()
