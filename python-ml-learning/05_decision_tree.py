# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#   파이썬 ML 학습 05단계: 결정 트리 (Decision Tree)
#   ─ 예/아니오 질문으로 분류하기 ─
#
#   비유: 스무고개 놀이
#     "날개가 있나요?" → 예 → "물속에 사나요?" → 아니오 → "독수리!"
#     결정 트리도 이렇게 질문을 이어가며 정답을 찾아갑니다.
#     어떤 질문을 먼저 할지가 핵심!
#
#   실행 방법:
#     python 05_decision_tree.py
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 1: 결정 트리 개념
# ─────────────────────────────────────────────────────────────────────────

def lesson1_decision_tree_concept():
    """
    결정 트리: 데이터를 질문(조건)으로 나누어 분류하는 방법.

    비유: 스무고개 게임
      좋은 질문 = 후보를 절반으로 줄이는 질문
      나쁜 질문 = 후보가 거의 안 줄어드는 질문
    """
    print("=" * 70)
    print("[레슨 1] 결정 트리 개념")
    print("=" * 70)
    print()
    print("  비유: 과일 맞히기 스무고개")
    print()
    print("              빨간색인가?")
    print("              /        \\")
    print("            예          아니오")
    print("           /              \\")
    print("     둥근가?            길쭉한가?")
    print("     /    \\             /      \\")
    print("   예    아니오       예      아니오")
    print("   |       |          |         |")
    print("  사과   딸기       바나나     포도")
    print()

    # 간단한 데이터셋
    data = [
        {"색": "빨강", "모양": "둥근", "과일": "사과"},
        {"색": "빨강", "모양": "작은", "과일": "딸기"},
        {"색": "노랑", "모양": "길쭉", "과일": "바나나"},
        {"색": "보라", "모양": "둥근", "과일": "포도"},
        {"색": "빨강", "모양": "둥근", "과일": "사과"},
        {"색": "노랑", "모양": "길쭉", "과일": "바나나"},
    ]

    print("  훈련 데이터:")
    print("  ┌────────┬────────┬──────────┐")
    print("  │  색    │  모양  │  과일    │")
    print("  ├────────┼────────┼──────────┤")
    for row in data:
        print(f"  │ {row['색']:>4s}   │ {row['모양']:>4s}   │ {row['과일']:>6s}   │")
    print("  └────────┴────────┴──────────┘")
    print()
    print("  → '색'으로 먼저 나누면 효율적! (정보 이득이 높음)")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 2: 엔트로피 (Entropy)
# ─────────────────────────────────────────────────────────────────────────

def lesson2_entropy():
    """
    엔트로피: 데이터가 얼마나 '뒤죽박죽'인지 측정.

    비유: 장난감 상자의 정리 상태
      엔트로피 0 = 상자에 레고만 있음 (완전 정리)
      엔트로피 높음 = 레고, 인형, 공이 섞여 있음 (뒤죽박죽)

    공식: H = -sum(p_i * log2(p_i))
    """
    print("=" * 70)
    print("[레슨 2] 엔트로피 (Entropy)")
    print("=" * 70)
    print()
    print("  엔트로피 = 데이터의 '뒤죽박죽' 정도")
    print("  공식: H = -Σ p_i × log2(p_i)")
    print()

    def calculate_entropy(labels):
        """라벨 리스트의 엔트로피 계산"""
        total = len(labels)
        if total == 0:
            return 0.0
        counts = {}
        for label in labels:
            counts[label] = counts.get(label, 0) + 1

        entropy = 0.0
        for count in counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy

    # 다양한 경우의 엔트로피
    cases = [
        ("모두 같은 클래스", ["사과", "사과", "사과", "사과"]),
        ("반반 섞임",       ["사과", "사과", "바나나", "바나나"]),
        ("세 종류 고루",    ["사과", "바나나", "포도", "딸기"]),
        ("하나만 다름",     ["사과", "사과", "사과", "바나나"]),
    ]

    print("  ┌─────────────────────┬──────────┬────────────────────┐")
    print("  │  경우               │ 엔트로피 │ 시각화             │")
    print("  ├─────────────────────┼──────────┼────────────────────┤")

    for name, labels in cases:
        h = calculate_entropy(labels)
        bar = "#" * int(h * 10)
        print(f"  │ {name:>19s} │  {h:>6.3f} │ {bar:<18s} │")

    print("  └─────────────────────┴──────────┴────────────────────┘")
    print()
    print("  → 엔트로피가 0 = 완벽히 분류됨!")
    print("  → 엔트로피가 높으면 = 아직 뒤죽박죽")
    print()

    return calculate_entropy


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 3: 정보 이득 (Information Gain)
# ─────────────────────────────────────────────────────────────────────────

def lesson3_information_gain(calc_entropy):
    """
    정보 이득: 어떤 질문을 했을 때 엔트로피가 얼마나 줄어드는지.

    비유: 스무고개에서 좋은 질문
      좋은 질문 = 후보를 많이 줄임 (높은 정보 이득)
      나쁜 질문 = 후보가 거의 안 줄어듦 (낮은 정보 이득)

    정보 이득 = 부모 엔트로피 - 자식 가중 평균 엔트로피
    """
    print("=" * 70)
    print("[레슨 3] 정보 이득 (Information Gain)")
    print("=" * 70)
    print()

    # 운동할지 말지 데이터
    data = [
        {"날씨": "맑음", "온도": "높음", "운동": "예"},
        {"날씨": "맑음", "온도": "높음", "운동": "예"},
        {"날씨": "비",   "온도": "높음", "운동": "아니오"},
        {"날씨": "비",   "온도": "낮음", "운동": "아니오"},
        {"날씨": "맑음", "온도": "낮음", "운동": "예"},
        {"날씨": "비",   "온도": "낮음", "운동": "아니오"},
        {"날씨": "맑음", "온도": "보통", "운동": "예"},
        {"날씨": "비",   "온도": "보통", "운동": "아니오"},
    ]

    labels = [d["운동"] for d in data]
    parent_entropy = calc_entropy(labels)
    print(f"  전체 데이터의 엔트로피: {parent_entropy:.3f}")
    print()

    # 각 특징으로 나눌 때 정보 이득 계산
    features = ["날씨", "온도"]

    for feature in features:
        # 특징값별로 데이터 분할
        splits = {}
        for d in data:
            val = d[feature]
            if val not in splits:
                splits[val] = []
            splits[val].append(d["운동"])

        # 가중 평균 엔트로피
        weighted_entropy = 0.0
        print(f"  '{feature}'로 나눌 때:")
        for val, sub_labels in splits.items():
            h = calc_entropy(sub_labels)
            weight = len(sub_labels) / len(data)
            weighted_entropy += weight * h
            print(f"    {feature}={val}: {sub_labels} → 엔트로피={h:.3f}, "
                  f"비중={weight:.2f}")

        info_gain = parent_entropy - weighted_entropy
        print(f"    정보 이득 = {parent_entropy:.3f} - {weighted_entropy:.3f} = {info_gain:.3f}")
        print()

    print("  → 정보 이득이 가장 높은 특징으로 먼저 나눕니다!")
    print("  → 이 경우 '날씨'로 나누는 것이 더 효율적입니다.")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 4: 지니 불순도 (Gini Impurity)
# ─────────────────────────────────────────────────────────────────────────

def lesson4_gini_impurity():
    """
    지니 불순도: 엔트로피의 대안. 계산이 더 빠름.

    비유: 주머니에서 구슬을 뽑았을 때 다른 색일 확률
      모든 구슬이 같은 색 → 지니=0 (순수)
      여러 색이 섞여 있으면 → 지니 높음 (불순)

    공식: Gini = 1 - sum(p_i^2)
    """
    print("=" * 70)
    print("[레슨 4] 지니 불순도 (Gini Impurity)")
    print("=" * 70)
    print()
    print("  공식: Gini = 1 - Σ p_i²")
    print()

    def gini(labels):
        total = len(labels)
        if total == 0:
            return 0.0
        counts = {}
        for l in labels:
            counts[l] = counts.get(l, 0) + 1
        return 1.0 - sum((c/total)**2 for c in counts.values())

    cases = [
        ("전부 A",         ["A", "A", "A", "A"]),
        ("A:3, B:1",       ["A", "A", "A", "B"]),
        ("A:2, B:2 (반반)", ["A", "A", "B", "B"]),
        ("A:1, B:1, C:1, D:1", ["A", "B", "C", "D"]),
    ]

    print("  ┌───────────────────────┬──────────┬────────────┐")
    print("  │  구성                 │   지니   │  엔트로피  │")
    print("  ├───────────────────────┼──────────┼────────────┤")

    for name, labels in cases:
        g = gini(labels)
        # 엔트로피도 비교
        total = len(labels)
        counts = {}
        for l in labels:
            counts[l] = counts.get(l, 0) + 1
        h = -sum((c/total) * math.log2(c/total) for c in counts.values() if c > 0)
        print(f"  │ {name:>21s} │  {g:>6.3f} │   {h:>7.3f}  │")

    print("  └───────────────────────┴──────────┴────────────┘")
    print()
    print("  → 지니와 엔트로피는 경향이 비슷함")
    print("  → 지니: log 계산 없어서 빠름 (sklearn 기본값)")
    print("  → 엔트로피: 이론적으로 더 정확할 수 있음")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 5: 결정 트리 구축 (직접 구현)
# ─────────────────────────────────────────────────────────────────────────

def lesson5_build_decision_tree():
    """
    간단한 결정 트리를 직접 만들어 봅니다.
    """
    print("=" * 70)
    print("[레슨 5] 결정 트리 직접 구축")
    print("=" * 70)
    print()

    # 데이터: [키(cm), 몸무게(kg)] → 운동 선수 유형
    data = [
        ([180, 80], "농구"),
        ([175, 75], "농구"),
        ([165, 60], "체조"),
        ([160, 55], "체조"),
        ([170, 90], "역도"),
        ([168, 85], "역도"),
    ]

    print("  훈련 데이터:")
    print("  ┌──────────┬───────────┬──────────┐")
    print("  │ 키(cm)   │ 몸무게(kg)│ 운동     │")
    print("  ├──────────┼───────────┼──────────┤")
    for features, label in data:
        print(f"  │  {features[0]:>5}   │   {features[1]:>5}   │ {label:>6s}   │")
    print("  └──────────┴───────────┴──────────┘")
    print()

    def gini(labels):
        total = len(labels)
        if total == 0:
            return 0.0
        counts = {}
        for l in labels:
            counts[l] = counts.get(l, 0) + 1
        return 1.0 - sum((c/total)**2 for c in counts.values())

    # 최적 분할점 찾기 (모든 특징, 모든 값 시도)
    def find_best_split(data):
        best_gini = float('inf')
        best_feature = 0
        best_threshold = 0
        feature_names = ["키", "몸무게"]

        for fi in range(2):  # 특징 인덱스
            values = sorted(set(d[0][fi] for d in data))
            for i in range(len(values) - 1):
                threshold = (values[i] + values[i+1]) / 2

                left = [d[1] for d in data if d[0][fi] <= threshold]
                right = [d[1] for d in data if d[0][fi] > threshold]

                w_gini = (len(left) * gini(left) + len(right) * gini(right)) / len(data)

                if w_gini < best_gini:
                    best_gini = w_gini
                    best_feature = fi
                    best_threshold = threshold

        return best_feature, best_threshold, best_gini

    fi, threshold, g = find_best_split(data)
    feature_names = ["키", "몸무게"]

    print(f"  최적 분할: {feature_names[fi]} <= {threshold} (지니={g:.3f})")
    print()

    left_data = [(f, l) for f, l in data if f[fi] <= threshold]
    right_data = [(f, l) for f, l in data if f[fi] > threshold]

    print(f"    왼쪽 ({feature_names[fi]}<={threshold}):")
    for f, l in left_data:
        print(f"      {f} → {l}")

    print(f"    오른쪽 ({feature_names[fi]}>{threshold}):")
    for f, l in right_data:
        print(f"      {f} → {l}")
    print()

    # 예측
    test_samples = [[172, 70], [163, 58], [169, 88]]
    print("  예측:")
    for sample in test_samples:
        if sample[fi] <= threshold:
            # 왼쪽에서 다수결
            labels = [l for f, l in left_data]
        else:
            labels = [l for f, l in right_data]

        from collections import Counter
        prediction = Counter(labels).most_common(1)[0][0]
        print(f"    키={sample[0]}, 몸무게={sample[1]} → {prediction}")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 6: 가지치기 (Pruning)
# ─────────────────────────────────────────────────────────────────────────

def lesson6_pruning():
    """
    가지치기: 너무 깊게 자란 트리를 잘라내는 것.

    비유: 스무고개에서 질문이 너무 세밀하면
      "오른쪽 눈썹 위에 점이 있나요?" 같은 쓸데없는 질문이 됨.
      적당한 깊이에서 멈춰야 일반화 성능이 좋음.
    """
    print("=" * 70)
    print("[레슨 6] 가지치기 (Pruning)")
    print("=" * 70)
    print()
    print("  가지치기가 필요한 이유:")
    print()
    print("  깊이 1: '날씨가 맑은가?' (간단, 일반적)")
    print("  깊이 2:   └→ '온도가 25도 이상?' (적당)")
    print("  깊이 3:       └→ '습도가 62.3% 이하?' (너무 세밀!)")
    print("  깊이 4:           └→ '풍속이 3.7m/s?' (과적합!)")
    print()

    # 깊이별 성능 시뮬레이션
    depths = [1, 2, 3, 5, 10, 20]
    print("  깊이별 성능:")
    print("  ┌───────┬──────────┬──────────┬────────────────────┐")
    print("  │ 깊이  │ 훈련 정확│ 테스트   │ 상태               │")
    print("  ├───────┼──────────┼──────────┼────────────────────┤")

    for depth in depths:
        # 시뮬레이션된 성능
        train_acc = min(0.5 + depth * 0.1, 1.0)
        if depth <= 3:
            test_acc = 0.5 + depth * 0.08
        else:
            test_acc = max(0.74 - (depth - 3) * 0.03, 0.5)

        status = ""
        if depth <= 1:
            status = "과소적합"
        elif depth <= 3:
            status = "적절"
        else:
            status = "과적합!"

        print(f"  │  {depth:>3}  │  {train_acc:>6.1%}  │  {test_acc:>6.1%}  │ {status:<18s} │")

    print("  └───────┴──────────┴──────────┴────────────────────┘")
    print()
    print("  가지치기 방법:")
    print("    사전 가지치기: max_depth, min_samples 등을 미리 설정")
    print("    사후 가지치기: 다 키운 후 불필요한 가지를 잘라냄")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■" * 72)
    print("  파이썬 ML 05단계 : 결정 트리 (Decision Tree)")
    print("  비유: 스무고개 놀이로 데이터 분류하기")
    print("■" * 72)
    print()

    lesson1_decision_tree_concept()
    calc_entropy = lesson2_entropy()
    lesson3_information_gain(calc_entropy)
    lesson4_gini_impurity()
    lesson5_build_decision_tree()
    lesson6_pruning()


if __name__ == "__main__":
    main()
