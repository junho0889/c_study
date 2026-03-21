# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#   파이썬 ML 학습 10단계: ML 파이프라인
#   ─ 데이터에서 배포까지 전체 흐름 ─
#
#   비유: 공장 조립 라인
#     원재료(데이터) → 세척(전처리) → 가공(특성공학)
#     → 조립(학습) → 검수(평가) → 출하(배포)
#     각 단계를 순서대로 연결한 것이 ML 파이프라인입니다.
#
#   실행 방법:
#     python 10_ml_pipeline.py
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import random


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 1: 데이터 전처리 - 결측치 처리
# ─────────────────────────────────────────────────────────────────────────

def lesson1_missing_values():
    """
    결측치: 데이터에 빈 칸이 있는 경우.

    비유: 학생 성적표에 빈 칸이 있으면
      방법1: 빈 칸을 평균으로 채움 (0점은 너무 불이익)
      방법2: 빈 칸이 있는 학생 데이터를 아예 버림
      방법3: 가장 흔한 값으로 채움
    """
    print("=" * 70)
    print("[레슨 1] 데이터 전처리 - 결측치 처리")
    print("=" * 70)
    print()

    # 결측치가 있는 데이터
    data = [
        {"이름": "철수", "국어": 85, "수학": 90, "영어": None},
        {"이름": "영희", "국어": 92, "수학": None, "영어": 88},
        {"이름": "민수", "국어": 78, "수학": 82, "영어": 75},
        {"이름": "지은", "국어": None, "수학": 95, "영어": 91},
        {"이름": "현우", "국어": 88, "수학": 76, "영어": 83},
    ]

    print("  원본 데이터 (None = 결측치):")
    print("  ┌────────┬────────┬────────┬────────┐")
    print("  │  이름  │  국어  │  수학  │  영어  │")
    print("  ├────────┼────────┼────────┼────────┤")
    for row in data:
        kor = f"{row['국어']:>5}" if row['국어'] is not None else "  ???"
        mat = f"{row['수학']:>5}" if row['수학'] is not None else "  ???"
        eng = f"{row['영어']:>5}" if row['영어'] is not None else "  ???"
        print(f"  │ {row['이름']:>4s}   │{kor}   │{mat}   │{eng}   │")
    print("  └────────┴────────┴────────┴────────┘")
    print()

    # 방법 1: 평균으로 채우기
    for subject in ["국어", "수학", "영어"]:
        values = [row[subject] for row in data if row[subject] is not None]
        mean_val = sum(values) / len(values)
        print(f"  {subject} 평균: {mean_val:.1f}")

        for row in data:
            if row[subject] is None:
                row[subject] = round(mean_val, 1)
                print(f"    → {row['이름']}의 {subject}를 {mean_val:.1f}로 채움")

    print()
    print("  결측치 처리 후:")
    for row in data:
        print(f"    {row['이름']}: 국어={row['국어']}, 수학={row['수학']}, 영어={row['영어']}")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 2: 범주형 데이터 인코딩
# ─────────────────────────────────────────────────────────────────────────

def lesson2_categorical_encoding():
    """
    범주형 데이터를 숫자로 변환하는 방법.

    비유: 컴퓨터는 "빨강", "파랑" 같은 글자를 못 읽어서
          숫자로 번역해줘야 합니다.
    """
    print("=" * 70)
    print("[레슨 2] 범주형 데이터 인코딩")
    print("=" * 70)
    print()

    # 원본 데이터
    animals = ["고양이", "강아지", "토끼", "고양이", "토끼"]
    print(f"  원본: {animals}")
    print()

    # 방법 1: 레이블 인코딩
    unique = sorted(set(animals))
    label_map = {name: i for i, name in enumerate(unique)}
    encoded = [label_map[a] for a in animals]

    print("  1. 레이블 인코딩 (각 범주에 숫자 하나 부여)")
    print(f"     매핑: {label_map}")
    print(f"     결과: {encoded}")
    print(f"     주의: 강아지(0) < 고양이(1) < 토끼(2)?")
    print(f"           순서 관계가 없는데 크기 비교가 됨! (문제)")
    print()

    # 방법 2: 원-핫 인코딩
    print("  2. 원-핫 인코딩 (각 범주를 별도 열로)")
    print(f"     범주: {unique}")
    print()
    print("     ┌──────────┬─────────┬─────────┬─────────┐")
    print("     │  원본    │ 강아지  │ 고양이  │  토끼   │")
    print("     ├──────────┼─────────┼─────────┼─────────┤")

    for animal in animals:
        one_hot = [1 if animal == u else 0 for u in unique]
        print(f"     │ {animal:>6s}   │    {one_hot[0]}    │    {one_hot[1]}    │    {one_hot[2]}    │")

    print("     └──────────┴─────────┴─────────┴─────────┘")
    print()
    print("  → 원-핫 인코딩은 순서 관계가 없어서 안전!")
    print("  → 단점: 범주가 많으면 열이 너무 많아짐")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 3: 특성 선택 (Feature Selection)
# ─────────────────────────────────────────────────────────────────────────

def lesson3_feature_selection():
    """
    불필요한 특성을 제거하면 모델이 더 잘 동작합니다.

    비유: 이사할 때 짐 정리
      진짜 필요한 것만 챙기고 나머지는 버리면
      짐이 가벼워지고 새 집에서 정리도 쉬움.
    """
    print("=" * 70)
    print("[레슨 3] 특성 선택 (Feature Selection)")
    print("=" * 70)
    print()

    # 특성별 상관계수 시뮬레이션
    features = {
        "공부 시간":    0.85,   # 시험 점수와 높은 상관
        "수업 출석률":  0.72,
        "과제 제출률":  0.65,
        "수면 시간":    0.45,
        "좋아하는 색":  0.02,   # 거의 무관
        "생년월일":     0.01,   # 무관
        "신발 크기":    0.05,   # 무관
    }

    print("  시험 점수 예측을 위한 특성별 상관계수:")
    print()

    selected = []
    dropped = []

    for name, corr in sorted(features.items(), key=lambda x: -x[1]):
        bar = "#" * int(abs(corr) * 40)
        status = "선택" if corr >= 0.3 else "제거"
        if corr >= 0.3:
            selected.append(name)
        else:
            dropped.append(name)
        print(f"    {name:>12s}: {corr:.2f} {bar} [{status}]")

    print()
    print(f"  선택된 특성: {selected}")
    print(f"  제거된 특성: {dropped}")
    print()
    print("  특성 선택 방법:")
    print("    필터: 상관계수, 분산 기준 (빠름)")
    print("    래퍼: 특성 조합을 시도해보고 성능 비교 (정확하지만 느림)")
    print("    임베디드: 모델 학습 중에 자동 선택 (L1 등)")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 4: 완전한 ML 파이프라인
# ─────────────────────────────────────────────────────────────────────────

def lesson4_complete_pipeline():
    """
    데이터→전처리→학습→평가 전체 파이프라인을 실행합니다.

    비유: 공장 생산 라인
      원재료 투입 → 세척 → 가공 → 조립 → 검수 → 출하
    """
    print("=" * 70)
    print("[레슨 4] 완전한 ML 파이프라인")
    print("=" * 70)
    print()

    random.seed(42)

    # Step 1: 데이터 생성
    print("  Step 1: 데이터 생성 (합격/불합격 예측)")
    data = []
    for _ in range(40):
        study_hours = random.uniform(1, 10)
        attendance = random.uniform(50, 100)
        # 공부 많이 하고 출석 높으면 합격
        score = study_hours * 5 + attendance * 0.3 + random.gauss(0, 5)
        passed = 1 if score > 60 else 0
        data.append([study_hours, attendance, passed])

    print(f"    데이터 {len(data)}개 생성")
    print(f"    합격: {sum(1 for d in data if d[2]==1)}명, "
          f"불합격: {sum(1 for d in data if d[2]==0)}명")
    print()

    # Step 2: 전처리 (정규화)
    print("  Step 2: 특성 정규화 (0~1 범위)")
    features = [[d[0], d[1]] for d in data]
    labels = [d[2] for d in data]

    for fi in range(2):
        vals = [f[fi] for f in features]
        min_v = min(vals)
        max_v = max(vals)
        for f in features:
            f[fi] = (f[fi] - min_v) / (max_v - min_v) if max_v > min_v else 0

    print(f"    정규화 후 첫 3개: {[[round(v,2) for v in f] for f in features[:3]]}")
    print()

    # Step 3: Train/Test 분할
    print("  Step 3: Train/Test 분할 (80/20)")
    split = int(len(data) * 0.8)
    X_train, y_train = features[:split], labels[:split]
    X_test, y_test = features[split:], labels[split:]
    print(f"    훈련: {len(X_train)}개, 테스트: {len(X_test)}개")
    print()

    # Step 4: 모델 학습 (로지스틱 회귀 스타일)
    print("  Step 4: 모델 학습 (단순 가중합 분류)")
    w = [random.gauss(0, 0.5) for _ in range(2)]
    b = 0.0
    lr = 1.0

    for epoch in range(30):
        total_loss = 0
        for x, y in zip(X_train, y_train):
            z = w[0]*x[0] + w[1]*x[1] + b
            pred = 1.0 / (1.0 + math.exp(-max(-500, min(500, z))))
            error = pred - y
            total_loss += error ** 2

            w[0] -= lr * error * x[0]
            w[1] -= lr * error * x[1]
            b -= lr * error

        if (epoch + 1) % 10 == 0:
            print(f"    에폭 {epoch+1}: 손실={total_loss/len(X_train):.4f}")

    print(f"    학습된 가중치: w={[round(v,3) for v in w]}, b={b:.3f}")
    print()

    # Step 5: 평가
    print("  Step 5: 모델 평가")
    tp = fp = fn = tn = 0
    for x, y in zip(X_test, y_test):
        z = w[0]*x[0] + w[1]*x[1] + b
        pred_prob = 1.0 / (1.0 + math.exp(-max(-500, min(500, z))))
        pred = 1 if pred_prob > 0.5 else 0

        if pred == 1 and y == 1: tp += 1
        elif pred == 1 and y == 0: fp += 1
        elif pred == 0 and y == 1: fn += 1
        else: tn += 1

    total = tp + fp + fn + tn
    accuracy = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2*precision*recall/(precision+recall) if (precision+recall) > 0 else 0

    print(f"    정확도:  {accuracy:.3f}")
    print(f"    정밀도:  {precision:.3f}")
    print(f"    재현율:  {recall:.3f}")
    print(f"    F1:      {f1:.3f}")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 5: 전체 워크플로우 정리
# ─────────────────────────────────────────────────────────────────────────

def lesson5_workflow_summary():
    """
    ML 프로젝트의 전체 흐름을 정리합니다.
    """
    print("=" * 70)
    print("[레슨 5] ML 워크플로우 정리")
    print("=" * 70)
    print()
    print("  ┌──────────────────────────────────────────────────┐")
    print("  │  1. 문제 정의                                    │")
    print("  │     '무엇을 예측/분류할 것인가?'                 │")
    print("  ├──────────────────────────────────────────────────┤")
    print("  │  2. 데이터 수집                                  │")
    print("  │     데이터베이스, CSV, API 등                    │")
    print("  ├──────────────────────────────────────────────────┤")
    print("  │  3. 데이터 탐색 (EDA)                            │")
    print("  │     분포 확인, 이상치, 결측치 파악               │")
    print("  ├──────────────────────────────────────────────────┤")
    print("  │  4. 전처리                                       │")
    print("  │     결측치, 인코딩, 정규화, 이상치 처리          │")
    print("  ├──────────────────────────────────────────────────┤")
    print("  │  5. 특성 공학                                    │")
    print("  │     특성 선택, 특성 생성, 차원 축소              │")
    print("  ├──────────────────────────────────────────────────┤")
    print("  │  6. 모델 선택 & 학습                             │")
    print("  │     여러 알고리즘 시도, 하이퍼파라미터 튜닝      │")
    print("  ├──────────────────────────────────────────────────┤")
    print("  │  7. 평가                                         │")
    print("  │     교차 검증, 혼동 행렬, ROC, F1                │")
    print("  ├──────────────────────────────────────────────────┤")
    print("  │  8. 배포                                         │")
    print("  │     API 서버, 모바일 앱, 배치 처리               │")
    print("  ├──────────────────────────────────────────────────┤")
    print("  │  9. 모니터링 & 유지보수                          │")
    print("  │     성능 저하 감지, 모델 재학습                  │")
    print("  └──────────────────────────────────────────────────┘")
    print()
    print("  흔한 실수:")
    print("    1. 테스트 데이터로 전처리 기준을 정하는 것 (데이터 누출!)")
    print("    2. 모델만 바꾸고 데이터 전처리를 안 하는 것")
    print("    3. 정확도만 보고 정밀도/재현율을 안 보는 것")
    print("    4. 교차 검증 없이 한 번의 분할로 평가하는 것")
    print()
    print("  이 과정을 체계적으로 자동화한 것이 'ML 파이프라인'입니다!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■" * 72)
    print("  파이썬 ML 10단계 : ML 파이프라인")
    print("  비유: 공장 조립 라인 (원재료→세척→가공→조립→검수→출하)")
    print("■" * 72)
    print()

    lesson1_missing_values()
    lesson2_categorical_encoding()
    lesson3_feature_selection()
    lesson4_complete_pipeline()
    lesson5_workflow_summary()


if __name__ == "__main__":
    main()
