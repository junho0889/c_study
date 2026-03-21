# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   파이썬 학습 16단계: 머신러닝 준비 (from scratch)
#   ─ 데이터 전처리, 거리 측정, KNN, 선형 회귀, 경사하강법, 평가 지표 ─
#   ■ 실행 방법: python 16_machine_learning_prep.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 머신러닝이란? — 규칙 기반 vs 데이터 기반
#   2. 데이터셋 만들기 — 특성(Feature)과 레이블(Label), 데이터 분할
#   3. 정규화와 표준화 — Min-Max, Z-Score, 왜 스케일링이 필요한지
#   4. 거리 측정 — 유클리드, 맨해튼, 코사인 유사도
#   5. k-최근접 이웃(KNN) 직접 구현 — 투표, k값 선택
#   6. 선형 회귀 직접 구현 — 최소제곱법, 기울기와 절편
#   7. 경사하강법 이해 — 손실 함수, 학습률, 수렴
#   8. 혼동 행렬과 평가 지표 — 정확도/정밀도/재현율/F1
#   9. 교차 검증 직접 구현 — K-Fold
#  10. 실전: 붓꽃 분류기 from scratch
#
# ─────────────────────────────────────────────────────────────────────────

import math
import random


# ─────────────────────────────────────────────────────────────────────────
# ■ 공통 헬퍼 함수
# ─────────────────────────────────────────────────────────────────────────

def print_lesson(title: str) -> None:
    """레슨 제목을 눈에 띄게 출력한다."""
    print()
    print("┌──────────────────────────────────────┐")
    print(f"│  {title:<36s} │")
    print("└──────────────────────────────────────┘")
    print()


# =========================================================================
#
#   레슨 1 — 머신러닝이란?
#
# =========================================================================

def lesson1_what_is_ml():
    print_lesson("레슨 1 : 머신러닝이란?")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 규칙 기반 프로그래밍 vs 머신러닝
    # ─────────────────────────────────────────────────────────────────────
    #
    #   규칙 기반: 프로그래머가 직접 규칙을 코딩한다
    #     if 키 > 180 and 몸무게 > 80: "농구 선수"
    #     → 규칙이 복잡해지면 한계에 부딪힘!
    #
    #   머신러닝: 데이터에서 규칙을 알아서 찾는다
    #     데이터(키, 몸무게, 직업) → 모델이 패턴을 학습
    #     → 새 데이터가 들어오면 자동으로 예측
    #
    #   비유: 규칙 기반 = 요리 레시피를 써주는 것
    #         머신러닝  = 여러 요리를 맛보게 하고 스스로 레시피를 깨닫게 하는 것
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ 규칙 기반 접근법
    print("  ■ 규칙 기반: 스팸 메일 필터")
    print("  ─────────────────────────────────────")

    def rule_based_spam(email_text: str) -> str:
        spam_words = ["무료", "당첨", "대출", "광고", "할인"]
        for word in spam_words:
            if word in email_text:
                return "스팸"
        return "정상"

    emails = [
        "오늘 회의 10시에 합시다",
        "무료 경품 당첨! 지금 확인하세요",
        "프로젝트 진행 상황 보고",
        "대출 상담 무료로 해드립니다",
    ]

    for email in emails:
        result = rule_based_spam(email)
        print(f"    '{email[:20]}...' → {result}")

    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 머신러닝의 3가지 유형
    # ─────────────────────────────────────────────────────────────────────
    #
    #   1. 지도학습 (Supervised Learning)
    #      - 정답이 있는 데이터로 학습
    #      - 예: 이 사진은 고양이다 / 개다 (분류)
    #      - 예: 이 집의 가격은 3억이다 (회귀)
    #
    #   2. 비지도학습 (Unsupervised Learning)
    #      - 정답 없이 데이터의 패턴을 찾음
    #      - 예: 고객을 비슷한 그룹으로 나누기 (클러스터링)
    #      - 예: 차원 축소 (PCA)
    #
    #   3. 강화학습 (Reinforcement Learning)
    #      - 시행착오를 통해 보상을 최대화하는 행동을 학습
    #      - 예: 게임 AI, 로봇 제어, AlphaGo
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 머신러닝의 3가지 유형")
    print("  ─────────────────────────────────────")
    print("  1. 지도학습   → 정답 있는 데이터로 학습 (분류, 회귀)")
    print("  2. 비지도학습 → 정답 없이 패턴 발견 (클러스터링)")
    print("  3. 강화학습   → 시행착오로 보상 최대화 (게임 AI)")
    print()

    # ■ 머신러닝의 핵심 워크플로
    print("  ■ 머신러닝 워크플로")
    print("  ─────────────────────────────────────")
    print("  데이터 수집 → 전처리 → 모델 학습 → 평가 → 배포")
    print("       ↑                                    │")
    print("       └────────── 피드백 ──────────────────┘")
    print()


# =========================================================================
#
#   레슨 2 — 데이터셋 만들기
#
# =========================================================================

def lesson2_dataset():
    print_lesson("레슨 2 : 데이터셋 만들기")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 특성(Feature)과 레이블(Label)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   특성(Feature): 모델이 보는 입력 데이터 (힌트)
    #   레이블(Label):  모델이 맞춰야 하는 정답
    #
    #   비유: 시험에서
    #     특성 = 문제 지문 (공부시간, 출석률, 과제점수)
    #     레이블 = 정답 (합격/불합격)
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ 학생 합격 예측 데이터셋
    dataset = [
        # [공부시간, 출석률, 과제점수] → 합격여부(0=불합격, 1=합격)
        {"features": [2, 70, 40], "label": 0, "name": "민수"},
        {"features": [6, 95, 90], "label": 1, "name": "지유"},
        {"features": [5, 92, 88], "label": 1, "name": "서연"},
        {"features": [3, 75, 55], "label": 0, "name": "하준"},
        {"features": [7, 97, 93], "label": 1, "name": "도윤"},
        {"features": [4, 82, 72], "label": 1, "name": "수아"},
        {"features": [1, 68, 35], "label": 0, "name": "예준"},
        {"features": [5, 89, 84], "label": 1, "name": "서준"},
        {"features": [2, 78, 48], "label": 0, "name": "지민"},
        {"features": [6, 94, 91], "label": 1, "name": "윤아"},
        {"features": [3, 80, 60], "label": 0, "name": "시우"},
        {"features": [5, 90, 86], "label": 1, "name": "하은"},
    ]

    print("  ■ 데이터셋 구조")
    print("  ─────────────────────────────────────")
    print("  특성: [공부시간, 출석률, 과제점수]")
    print("  레이블: 합격 여부 (0 또는 1)")
    print()

    for row in dataset[:3]:
        print(f"    {row['name']}: 특성={row['features']}, 레이블={row['label']}")
    print(f"    ... 총 {len(dataset)}명")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 학습/검증/테스트 분할
    # ─────────────────────────────────────────────────────────────────────
    #
    #   왜 분할하는가?
    #     학습 데이터로 시험 보면 = "답지 보면서 시험 치는 것"
    #     → 진짜 실력을 알 수 없다!
    #
    #   일반적인 비율:
    #     학습(Train): 60~80%  → 모델이 배우는 데이터
    #     검증(Validation): 10~20%  → 하이퍼파라미터 튜닝용
    #     테스트(Test): 10~20%  → 최종 성능 평가
    #
    #   비유: 수학 공부
    #     학습 = 교과서 예제 풀기
    #     검증 = 모의고사 보기
    #     테스트 = 수능 시험
    #
    # ─────────────────────────────────────────────────────────────────────

    def train_val_test_split(data, train_ratio=0.6, val_ratio=0.2):
        """데이터를 학습/검증/테스트로 분할한다."""
        n = len(data)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))
        return data[:train_end], data[train_end:val_end], data[val_end:]

    train, val, test = train_val_test_split(dataset)

    print("  ■ 데이터 분할 결과")
    print("  ─────────────────────────────────────")
    print(f"  학습(Train):   {len(train)}명 → {[d['name'] for d in train]}")
    print(f"  검증(Val):     {len(val)}명 → {[d['name'] for d in val]}")
    print(f"  테스트(Test):  {len(test)}명 → {[d['name'] for d in test]}")
    print()

    # ★ 주의: 셔플(shuffle) 없이 분할하면 편향 발생 가능!
    print("  ★ 주의: 실제로는 데이터를 섞은 후 분할해야 합니다!")
    print("    (성적 순으로 정렬된 데이터를 그냥 나누면")
    print("     테스트셋에 잘하는 학생만 몰릴 수 있음)")
    print()


# =========================================================================
#
#   레슨 3 — 정규화와 표준화
#
# =========================================================================

def lesson3_normalization():
    print_lesson("레슨 3 : 정규화와 표준화")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 왜 스케일링이 필요한가?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   문제: 공부시간(1~7)과 과제점수(35~93)의 범위가 다르다!
    #
    #   스케일링 없이 거리 계산하면:
    #     과제점수 차이가 거리에 훨씬 큰 영향 → 불공정!
    #
    #   비유: 축구장에서 키(cm)와 몸무게(kg)로 거리를 재면
    #     키 차이 10cm vs 몸무게 차이 10kg → 같은 10이지만 의미가 다름!
    #     → 둘 다 0~1 범위로 맞춰야 공정하게 비교 가능
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ Min-Max 정규화 (0~1 범위로 변환)
    print("  ■ Min-Max 정규화")
    print("  ─────────────────────────────────────")
    print("  공식: (값 - 최소값) / (최대값 - 최소값)")
    print()

    def min_max_normalize(values: list[float]) -> list[float]:
        """값을 0~1 범위로 정규화한다."""
        min_val = min(values)
        max_val = max(values)
        if max_val == min_val:
            return [0.0] * len(values)   # 모든 값이 같으면 0
        return [(v - min_val) / (max_val - min_val) for v in values]

    study_hours = [2, 6, 5, 3, 7, 4, 1, 5, 2, 6, 3, 5]
    homework    = [40, 90, 88, 55, 93, 72, 35, 84, 48, 91, 60, 86]

    norm_hours = min_max_normalize(study_hours)
    norm_homework = min_max_normalize(homework)

    print("  공부시간 (원본):    ", study_hours[:5], "...")
    print("  공부시간 (정규화):  ", [round(v, 3) for v in norm_hours[:5]], "...")
    print("  과제점수 (원본):    ", homework[:5], "...")
    print("  과제점수 (정규화):  ", [round(v, 3) for v in norm_homework[:5]], "...")
    print()

    # ■ Z-Score 표준화 (평균=0, 표준편차=1로 변환)
    print("  ■ Z-Score 표준화")
    print("  ─────────────────────────────────────")
    print("  공식: (값 - 평균) / 표준편차")
    print()

    def z_score_normalize(values: list[float]) -> list[float]:
        """Z-Score로 표준화한다."""
        n = len(values)
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / n
        std = math.sqrt(variance)
        if std == 0:
            return [0.0] * n
        return [(v - mean) / std for v in values]

    z_hours = z_score_normalize(study_hours)
    z_homework = z_score_normalize(homework)

    print("  공부시간 (Z-Score): ", [round(v, 3) for v in z_hours[:5]], "...")
    print("  과제점수 (Z-Score): ", [round(v, 3) for v in z_homework[:5]], "...")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Min-Max vs Z-Score 비교
    # ─────────────────────────────────────────────────────────────────────
    #
    #   Min-Max:
    #     - 범위가 정해짐 (0~1)
    #     - 이상치(outlier)에 민감
    #     - 신경망 입력에 주로 사용
    #
    #   Z-Score:
    #     - 범위가 정해지지 않음 (평균 0, 표준편차 1)
    #     - 이상치에 덜 민감
    #     - 통계 분석, SVM 등에 주로 사용
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ 이상치의 영향 시각화
    print("  ■ 이상치가 있을 때의 차이")
    print("  ─────────────────────────────────────")
    data_with_outlier = [10, 20, 30, 40, 50, 500]  # 500은 이상치!

    mm = min_max_normalize(data_with_outlier)
    zs = z_score_normalize(data_with_outlier)

    print(f"  원본 데이터:  {data_with_outlier}")
    print(f"  Min-Max:      {[round(v, 3) for v in mm]}")
    print(f"  Z-Score:      {[round(v, 3) for v in zs]}")
    print("  → Min-Max에서는 정상 데이터가 0~0.08 사이에 몰림!")
    print("  → Z-Score는 이상치를 높은 값으로 표현하되 나머지는 분산됨")
    print()


# =========================================================================
#
#   레슨 4 — 거리 측정
#
# =========================================================================

def lesson4_distance_metrics():
    print_lesson("레슨 4 : 거리 측정")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 유클리드 거리 (Euclidean Distance)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   가장 직관적인 거리 = 직선 거리 (피타고라스 정리)
    #   공식: sqrt( (x1-x2)^2 + (y1-y2)^2 + ... )
    #
    #   비유: 지도에서 두 점 사이에 자를 대고 재는 것
    #
    # ─────────────────────────────────────────────────────────────────────

    def euclidean_distance(a: list[float], b: list[float]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    print("  ■ 유클리드 거리")
    print("  ─────────────────────────────────────")

    p1 = [0, 0]
    p2 = [3, 4]
    print(f"  점 A{p1}과 점 B{p2} 사이 거리: {euclidean_distance(p1, p2):.3f}")
    print(f"  (3-4-5 삼각형 → 거리는 5)")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 맨해튼 거리 (Manhattan Distance)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   각 좌표 차이의 절대값 합
    #   공식: |x1-x2| + |y1-y2| + ...
    #
    #   비유: 맨해튼(뉴욕)의 격자형 도로에서 이동하는 거리
    #         대각선으로 갈 수 없고 블록을 따라가야 하는 거리
    #
    # ─────────────────────────────────────────────────────────────────────

    def manhattan_distance(a: list[float], b: list[float]) -> float:
        return sum(abs(x - y) for x, y in zip(a, b))

    print("  ■ 맨해튼 거리")
    print("  ─────────────────────────────────────")
    print(f"  점 A{p1}과 점 B{p2}: {manhattan_distance(p1, p2):.3f}")
    print(f"  (|3-0| + |4-0| = 7)")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 코사인 유사도 (Cosine Similarity)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   두 벡터 사이의 각도를 측정 (방향의 유사성)
    #   공식: (A·B) / (|A| × |B|)
    #   결과: -1 (반대) ~ 0 (무관) ~ 1 (같은 방향)
    #
    #   비유: 두 화살표가 같은 방향을 가리키는지 확인
    #         크기(길이)는 무시하고 방향만 비교!
    #
    #   활용: 텍스트 유사도, 추천 시스템
    #         "좋아요 10번 vs 100번"보다 "취향이 비슷한지"가 중요할 때
    #
    # ─────────────────────────────────────────────────────────────────────

    def cosine_similarity(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x ** 2 for x in a))
        mag_b = math.sqrt(sum(x ** 2 for x in b))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)

    print("  ■ 코사인 유사도")
    print("  ─────────────────────────────────────")

    # 같은 방향, 크기만 다른 벡터
    v1 = [1, 2, 3]
    v2 = [2, 4, 6]   # v1의 2배
    v3 = [3, 2, 1]   # 다른 방향

    print(f"  v1={v1}, v2={v2} (같은 방향)")
    print(f"    유사도: {cosine_similarity(v1, v2):.4f}  (1.0 = 완전 동일 방향)")
    print(f"  v1={v1}, v3={v3} (다른 방향)")
    print(f"    유사도: {cosine_similarity(v1, v3):.4f}")
    print()

    # ■ 거리 비교 표
    print("  ■ 세 가지 거리 비교")
    print("  ─────────────────────────────────────")
    a = [1, 5, 3]
    b = [4, 1, 2]
    print(f"  A={a}, B={b}")
    print(f"    유클리드 거리:  {euclidean_distance(a, b):.3f}")
    print(f"    맨해튼 거리:    {manhattan_distance(a, b):.3f}")
    print(f"    코사인 유사도:  {cosine_similarity(a, b):.4f}")
    print()


# =========================================================================
#
#   레슨 5 — k-최근접 이웃(KNN) 직접 구현
#
# =========================================================================

def lesson5_knn():
    print_lesson("레슨 5 : KNN 직접 구현")

    # ─────────────────────────────────────────────────────────────────────
    # ■ KNN이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   "주변에 있는 k명의 이웃을 보고, 다수결로 결정한다"
    #
    #   비유: 새로 전학 온 학생의 반을 정할 때
    #     가장 가까이 사는 친구 3명(k=3)을 보고
    #     그 중 2명이 A반이면 → A반으로 배정!
    #
    #   알고리즘:
    #     1. 새 데이터와 모든 학습 데이터의 거리를 계산
    #     2. 거리가 가까운 k개를 선택
    #     3. k개의 레이블 중 가장 많은 것을 결과로
    #
    # ─────────────────────────────────────────────────────────────────────

    # 학습 데이터: [공부시간, 출석률, 과제점수]
    train_data = [
        ([2, 70, 40], 0), ([6, 95, 90], 1), ([5, 92, 88], 1),
        ([3, 75, 55], 0), ([7, 97, 93], 1), ([4, 82, 72], 1),
        ([1, 68, 35], 0), ([5, 89, 84], 1),
    ]
    test_data = [
        ([2, 78, 48], 0), ([6, 94, 91], 1),
        ([3, 80, 60], 0), ([5, 90, 86], 1),
    ]

    # ■ 정규화 함수
    def compute_min_max(data):
        n_features = len(data[0][0])
        mins = [min(row[0][i] for row in data) for i in range(n_features)]
        maxs = [max(row[0][i] for row in data) for i in range(n_features)]
        return mins, maxs

    def normalize(features, mins, maxs):
        return [
            (f - mn) / (mx - mn) if mx != mn else 0.0
            for f, mn, mx in zip(features, mins, maxs)
        ]

    # ■ KNN 구현
    def knn_predict(train, query_features, k=3, mins=None, maxs=None):
        """k-최근접 이웃으로 예측한다."""
        query_norm = normalize(query_features, mins, maxs)

        distances = []
        for features, label in train:
            feat_norm = normalize(features, mins, maxs)
            dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(query_norm, feat_norm)))
            distances.append((dist, label))

        distances.sort(key=lambda x: x[0])
        neighbors = distances[:k]

        # 투표 (다수결)
        votes = {}
        for _, label in neighbors:
            votes[label] = votes.get(label, 0) + 1

        return max(votes, key=votes.get)

    mins, maxs = compute_min_max(train_data)

    print("  ■ KNN 예측 결과 (k=3)")
    print("  ─────────────────────────────────────")

    correct = 0
    for features, actual in test_data:
        predicted = knn_predict(train_data, features, k=3, mins=mins, maxs=maxs)
        match = "O" if predicted == actual else "X"
        if predicted == actual:
            correct += 1
        label_str = "합격" if actual == 1 else "불합격"
        pred_str = "합격" if predicted == 1 else "불합격"
        print(f"    특성={features} → 예측={pred_str}, 실제={label_str} [{match}]")

    print(f"  정확도: {correct}/{len(test_data)} = {correct/len(test_data):.1%}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ k값에 따른 결과 변화
    # ─────────────────────────────────────────────────────────────────────
    #
    #   k가 너무 작으면 (k=1): 노이즈에 민감 (과적합)
    #   k가 너무 크면 (k=전체): 모든 것을 다수 클래스로 예측 (과소적합)
    #   → 보통 홀수를 선택 (동점 방지)
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ k값에 따른 정확도 변화")
    print("  ─────────────────────────────────────")

    for k in [1, 3, 5, 7]:
        correct = sum(
            1 for features, actual in test_data
            if knn_predict(train_data, features, k=k, mins=mins, maxs=maxs) == actual
        )
        acc = correct / len(test_data)
        bar = "#" * int(acc * 20)
        print(f"    k={k}: 정확도 {acc:.1%} {bar}")
    print()

    # ■ 가중 투표 KNN
    print("  ■ 가중 투표 KNN (거리가 가까울수록 높은 가중치)")
    print("  ─────────────────────────────────────")

    def weighted_knn_predict(train, query_features, k=3, mins=None, maxs=None):
        query_norm = normalize(query_features, mins, maxs)
        distances = []
        for features, label in train:
            feat_norm = normalize(features, mins, maxs)
            dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(query_norm, feat_norm)))
            distances.append((dist, label))

        distances.sort(key=lambda x: x[0])
        neighbors = distances[:k]

        # 거리의 역수를 가중치로 사용
        weighted_votes = {}
        for dist, label in neighbors:
            weight = 1.0 / (dist + 1e-10)   # 0으로 나누기 방지
            weighted_votes[label] = weighted_votes.get(label, 0) + weight

        return max(weighted_votes, key=weighted_votes.get)

    for features, actual in test_data[:2]:
        pred = weighted_knn_predict(train_data, features, k=3, mins=mins, maxs=maxs)
        pred_str = "합격" if pred == 1 else "불합격"
        actual_str = "합격" if actual == 1 else "불합격"
        print(f"    특성={features} → 가중 예측={pred_str}, 실제={actual_str}")
    print()


# =========================================================================
#
#   레슨 6 — 선형 회귀 직접 구현
#
# =========================================================================

def lesson6_linear_regression():
    print_lesson("레슨 6 : 선형 회귀 직접 구현")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 선형 회귀란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   데이터를 가장 잘 설명하는 직선(y = ax + b)을 찾는 것
    #
    #   비유: 학생의 공부 시간(x)으로 시험 점수(y)를 예측
    #     공부 2시간 → 60점, 4시간 → 80점, 6시간 → 90점
    #     이 데이터를 관통하는 최적의 직선을 찾자!
    #
    #   a(기울기): x가 1 증가할 때 y가 얼마나 변하는지
    #   b(절편):   x=0일 때의 y값
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ 최소제곱법(OLS)으로 직접 구현
    print("  ■ 최소제곱법으로 선형 회귀")
    print("  ─────────────────────────────────────")

    # 데이터: 공부 시간 → 시험 점수
    x_data = [1, 2, 3, 4, 5, 6, 7, 8]
    y_data = [45, 55, 60, 70, 75, 82, 88, 92]

    def linear_regression_ols(x: list, y: list):
        """최소제곱법으로 기울기(a)와 절편(b)을 구한다."""
        n = len(x)
        x_mean = sum(x) / n
        y_mean = sum(y) / n

        # a = Σ(xi - x̄)(yi - ȳ) / Σ(xi - x̄)²
        numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
        denominator = sum((xi - x_mean) ** 2 for xi in x)

        a = numerator / denominator    # 기울기
        b = y_mean - a * x_mean        # 절편

        return a, b

    a, b = linear_regression_ols(x_data, y_data)
    print(f"  기울기(a) = {a:.3f}")
    print(f"  절편(b)   = {b:.3f}")
    print(f"  회귀식: y = {a:.3f}x + {b:.3f}")
    print()

    # ■ 예측
    print("  ■ 예측 결과")
    print("  ─────────────────────────────────────")

    def predict(x_val, a, b):
        return a * x_val + b

    for xi, yi in zip(x_data, y_data):
        pred = predict(xi, a, b)
        error = yi - pred
        print(f"    공부 {xi}시간: 실제={yi}점, 예측={pred:.1f}점, 오차={error:+.1f}")

    # 새 데이터 예측
    print()
    new_x = 10
    print(f"  ★ 공부 {new_x}시간 예측: {predict(new_x, a, b):.1f}점")
    print()

    # ■ 결정계수 R² 계산
    print("  ■ 결정계수(R²) - 모델이 얼마나 잘 맞는지")
    print("  ─────────────────────────────────────")

    y_mean = sum(y_data) / len(y_data)
    ss_res = sum((yi - predict(xi, a, b)) ** 2 for xi, yi in zip(x_data, y_data))
    ss_tot = sum((yi - y_mean) ** 2 for yi in y_data)
    r_squared = 1 - (ss_res / ss_tot)

    print(f"  R² = {r_squared:.4f}")
    print(f"  → 모델이 데이터 변동의 {r_squared:.1%}를 설명")
    print("  (1에 가까울수록 좋은 모델)")
    print()


# =========================================================================
#
#   레슨 7 — 경사하강법 이해
#
# =========================================================================

def lesson7_gradient_descent():
    print_lesson("레슨 7 : 경사하강법")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 경사하강법이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   "산에서 눈을 감고 가장 낮은 곳(최솟값)을 찾아 내려가는 방법"
    #
    #   비유:
    #     산꼭대기에 서 있다고 상상해보자.
    #     눈을 감고, 발밑의 경사(기울기)를 느끼면서
    #     경사가 가파른 쪽으로 한 발씩 내려간다.
    #     → 결국 골짜기(최솟값)에 도달!
    #
    #   손실 함수(Loss Function):
    #     모델의 예측과 실제 정답 사이의 차이를 숫자로 표현
    #     이 값을 최소화하는 것이 목표!
    #
    #   학습률(Learning Rate):
    #     한 발 내딛는 크기
    #     너무 크면 → 골짜기를 넘어가 버림 (발산)
    #     너무 작으면 → 너무 오래 걸림
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ 1변수 경사하강법 예시: y = (x - 3)² 의 최솟값 찾기
    print("  ■ 간단한 예: y = (x - 3)² 의 최솟값 찾기")
    print("  ─────────────────────────────────────")

    def loss(x):
        return (x - 3) ** 2

    def gradient(x):
        return 2 * (x - 3)    # 미분: dy/dx = 2(x-3)

    x = 10.0         # 시작점
    lr = 0.1          # 학습률

    print(f"  시작점: x = {x}, 손실 = {loss(x):.4f}")

    for step in range(1, 11):
        grad = gradient(x)
        x = x - lr * grad     # 기울기 반대 방향으로 이동
        print(f"  Step {step:2d}: x = {x:.4f}, 손실 = {loss(x):.4f}, 기울기 = {grad:+.4f}")

    print(f"  → 최종 x = {x:.4f} (정답: 3.0)")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 선형 회귀에 경사하강법 적용
    # ─────────────────────────────────────────────────────────────────────
    #
    #   손실 함수: MSE = (1/n) Σ (yi - (a*xi + b))²
    #   기울기:
    #     ∂MSE/∂a = -(2/n) Σ xi * (yi - (a*xi + b))
    #     ∂MSE/∂b = -(2/n) Σ (yi - (a*xi + b))
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 경사하강법으로 선형 회귀 학습")
    print("  ─────────────────────────────────────")

    x_data = [1, 2, 3, 4, 5, 6, 7, 8]
    y_data = [45, 55, 60, 70, 75, 82, 88, 92]
    n = len(x_data)

    a = 0.0    # 기울기 초기값
    b = 0.0    # 절편 초기값
    lr = 0.01  # 학습률
    epochs = 100

    for epoch in range(epochs):
        # 예측값 계산
        predictions = [a * xi + b for xi in x_data]

        # 손실(MSE) 계산
        mse = sum((yi - pi) ** 2 for yi, pi in zip(y_data, predictions)) / n

        # 기울기 계산
        grad_a = -(2 / n) * sum(xi * (yi - pi) for xi, yi, pi in zip(x_data, y_data, predictions))
        grad_b = -(2 / n) * sum(yi - pi for yi, pi in zip(y_data, predictions))

        # 파라미터 업데이트
        a = a - lr * grad_a
        b = b - lr * grad_b

        if epoch % 20 == 0 or epoch == epochs - 1:
            print(f"  Epoch {epoch:3d}: a={a:.4f}, b={b:.4f}, MSE={mse:.4f}")

    print(f"  → 최종 회귀식: y = {a:.3f}x + {b:.3f}")
    print()

    # ■ 학습률에 따른 수렴 비교
    print("  ■ 학습률에 따른 수렴 속도 비교")
    print("  ─────────────────────────────────────")

    for test_lr in [0.001, 0.01, 0.05]:
        test_a, test_b = 0.0, 0.0
        for _ in range(100):
            preds = [test_a * xi + test_b for xi in x_data]
            grad_a = -(2/n) * sum(xi * (yi - pi) for xi, yi, pi in zip(x_data, y_data, preds))
            grad_b = -(2/n) * sum(yi - pi for yi, pi in zip(y_data, preds))
            test_a -= test_lr * grad_a
            test_b -= test_lr * grad_b

        mse = sum((yi - (test_a * xi + test_b)) ** 2 for xi, yi in zip(x_data, y_data)) / n
        print(f"    lr={test_lr:.3f} → a={test_a:.3f}, b={test_b:.3f}, MSE={mse:.3f}")
    print()


# =========================================================================
#
#   레슨 8 — 혼동 행렬과 평가 지표
#
# =========================================================================

def lesson8_confusion_matrix():
    print_lesson("레슨 8 : 혼동 행렬과 평가 지표")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 혼동 행렬(Confusion Matrix)이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   예측 결과를 4가지로 분류:
    #
    #                     예측 양성(P)    예측 음성(N)
    #   실제 양성(P)      TP (맞춤)       FN (놓침)
    #   실제 음성(N)      FP (오탐)       TN (맞춤)
    #
    #   TP = True Positive  : 암 환자를 암이라고 맞춤
    #   FP = False Positive : 정상인을 암이라고 잘못 진단 (오탐)
    #   FN = False Negative : 암 환자를 정상이라고 놓침 (누락)
    #   TN = True Negative  : 정상인을 정상이라고 맞춤
    #
    #   비유: 화재 경보기
    #     TP = 불이 났는데 경보가 울림 (제대로!)
    #     FP = 불이 안 났는데 경보가 울림 (오경보)
    #     FN = 불이 났는데 경보가 안 울림 (위험!)
    #     TN = 불이 안 났는데 경보도 안 울림 (정상)
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ 예시 데이터
    actual    = [1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1]
    predicted = [1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1]

    def compute_confusion_matrix(actual, predicted):
        tp = sum(1 for a, p in zip(actual, predicted) if a == 1 and p == 1)
        fp = sum(1 for a, p in zip(actual, predicted) if a == 0 and p == 1)
        fn = sum(1 for a, p in zip(actual, predicted) if a == 1 and p == 0)
        tn = sum(1 for a, p in zip(actual, predicted) if a == 0 and p == 0)
        return tp, fp, fn, tn

    tp, fp, fn, tn = compute_confusion_matrix(actual, predicted)

    print("  ■ 혼동 행렬")
    print("  ─────────────────────────────────────")
    print(f"                  예측=양성  예측=음성")
    print(f"  실제=양성(합격)    TP={tp}      FN={fn}")
    print(f"  실제=음성(불합격)  FP={fp}      TN={tn}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 평가 지표 직접 계산
    # ─────────────────────────────────────────────────────────────────────

    # 정확도 (Accuracy): 전체 중 맞춘 비율
    accuracy = (tp + tn) / (tp + fp + fn + tn)

    # 정밀도 (Precision): 양성이라고 예측한 것 중 실제 양성 비율
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0

    # 재현율 (Recall): 실제 양성 중 양성으로 예측한 비율
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    # F1 Score: 정밀도와 재현율의 조화 평균
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    print("  ■ 평가 지표")
    print("  ─────────────────────────────────────")
    print(f"  정확도(Accuracy):    {accuracy:.4f}  → 전체 중 맞춘 비율")
    print(f"  정밀도(Precision):   {precision:.4f}  → '합격'이라 한 것 중 진짜 합격")
    print(f"  재현율(Recall):      {recall:.4f}  → 진짜 합격 중 찾아낸 비율")
    print(f"  F1 Score:            {f1:.4f}  → 정밀도와 재현율의 조화 평균")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 정밀도 vs 재현율 — 언제 뭐가 중요한가?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   정밀도가 중요한 경우: 오탐(FP)이 치명적일 때
    #     예) 스팸 메일 필터 — 정상 메일을 스팸으로 분류하면 큰일!
    #
    #   재현율이 중요한 경우: 놓침(FN)이 치명적일 때
    #     예) 암 진단 — 암 환자를 정상이라고 놓치면 위험!
    #
    #   F1 Score: 정밀도와 재현율 둘 다 중요할 때 균형 잡힌 지표
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 정밀도 vs 재현율 트레이드오프")
    print("  ─────────────────────────────────────")
    print("  스팸 필터 → 정밀도 우선 (정상 메일을 스팸으로 보내면 안 됨)")
    print("  암 진단   → 재현율 우선 (환자를 놓치면 안 됨)")
    print("  검색 엔진 → F1 Score (정밀도와 재현율 균형)")
    print()


# =========================================================================
#
#   레슨 9 — 교차 검증 직접 구현
#
# =========================================================================

def lesson9_cross_validation():
    print_lesson("레슨 9 : 교차 검증")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 교차 검증(Cross Validation)이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   데이터를 k개 조각(fold)으로 나누어
    #   각 조각을 한 번씩 테스트셋으로 사용하는 방법
    #
    #   K=5일 때:
    #     1차: [테스트][학습][학습][학습][학습]
    #     2차: [학습][테스트][학습][학습][학습]
    #     3차: [학습][학습][테스트][학습][학습]
    #     4차: [학습][학습][학습][테스트][학습]
    #     5차: [학습][학습][학습][학습][테스트]
    #
    #   왜 필요한가?
    #     - 데이터가 적을 때 모든 데이터를 학습과 평가에 활용 가능
    #     - 한 번 분할의 운에 따른 결과 편향을 줄임
    #     - 모델의 일반화 성능을 더 정확하게 추정
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ K-Fold 교차 검증 구현
    dataset = [
        ([2, 70, 40], 0), ([6, 95, 90], 1), ([5, 92, 88], 1),
        ([3, 75, 55], 0), ([7, 97, 93], 1), ([4, 82, 72], 1),
        ([1, 68, 35], 0), ([5, 89, 84], 1), ([2, 78, 48], 0),
        ([6, 94, 91], 1),
    ]

    def k_fold_split(data, k=5):
        """데이터를 k개의 fold로 나눈다."""
        fold_size = len(data) // k
        folds = []
        for i in range(k):
            start = i * fold_size
            end = start + fold_size if i < k - 1 else len(data)
            test_fold = data[start:end]
            train_fold = data[:start] + data[end:]
            folds.append((train_fold, test_fold))
        return folds

    # 간단한 예측 함수 (과제 점수 기준)
    def simple_predict(features):
        return 1 if features[2] >= 70 else 0

    print("  ■ 5-Fold 교차 검증")
    print("  ─────────────────────────────────────")

    folds = k_fold_split(dataset, k=5)
    fold_accuracies = []

    for fold_idx, (train, test) in enumerate(folds):
        correct = sum(1 for features, label in test if simple_predict(features) == label)
        acc = correct / len(test) if test else 0
        fold_accuracies.append(acc)
        print(f"    Fold {fold_idx+1}: 학습={len(train)}개, 테스트={len(test)}개, 정확도={acc:.1%}")

    avg_acc = sum(fold_accuracies) / len(fold_accuracies)
    print(f"  평균 정확도: {avg_acc:.1%}")
    print()

    # ■ 왜 한 번 분할보다 교차 검증이 나은가?
    print("  ■ 교차 검증의 장점")
    print("  ─────────────────────────────────────")
    print("  - 모든 데이터가 한 번씩 테스트에 사용됨")
    print("  - 운 좋은 분할 / 운 나쁜 분할의 영향을 줄임")
    print(f"  - 단일 분할: Fold 1 정확도만 보면 {fold_accuracies[0]:.1%}")
    print(f"  - 교차 검증: 평균 정확도 {avg_acc:.1%} (더 신뢰성 높음)")
    print()


# =========================================================================
#
#   레슨 10 — 실전: 붓꽃 분류기 from scratch
#
# =========================================================================

def lesson10_iris_classifier():
    print_lesson("레슨 10 : 붓꽃 분류기 from scratch")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 붓꽃 데이터셋 (Fisher's Iris — 간소화 버전)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   특성: [꽃받침 길이, 꽃받침 너비, 꽃잎 길이, 꽃잎 너비]
    #   레이블: 0=Setosa, 1=Versicolor, 2=Virginica
    #
    # ─────────────────────────────────────────────────────────────────────

    iris_data = [
        # Setosa (0) — 꽃잎이 작음
        ([5.1, 3.5, 1.4, 0.2], 0), ([4.9, 3.0, 1.4, 0.2], 0),
        ([4.7, 3.2, 1.3, 0.2], 0), ([5.0, 3.6, 1.4, 0.2], 0),
        ([5.4, 3.9, 1.7, 0.4], 0), ([4.6, 3.4, 1.4, 0.3], 0),
        ([5.0, 3.4, 1.5, 0.2], 0), ([4.4, 2.9, 1.4, 0.2], 0),
        ([5.4, 3.7, 1.5, 0.2], 0), ([4.8, 3.4, 1.6, 0.2], 0),
        # Versicolor (1) — 중간 크기
        ([7.0, 3.2, 4.7, 1.4], 1), ([6.4, 3.2, 4.5, 1.5], 1),
        ([6.9, 3.1, 4.9, 1.5], 1), ([5.5, 2.3, 4.0, 1.3], 1),
        ([6.5, 2.8, 4.6, 1.5], 1), ([5.7, 2.8, 4.5, 1.3], 1),
        ([6.3, 3.3, 4.7, 1.6], 1), ([4.9, 2.4, 3.3, 1.0], 1),
        ([6.6, 2.9, 4.6, 1.3], 1), ([5.2, 2.7, 3.9, 1.4], 1),
        # Virginica (2) — 꽃잎이 큼
        ([6.3, 3.3, 6.0, 2.5], 2), ([5.8, 2.7, 5.1, 1.9], 2),
        ([7.1, 3.0, 5.9, 2.1], 2), ([6.3, 2.9, 5.6, 1.8], 2),
        ([6.5, 3.0, 5.8, 2.2], 2), ([7.6, 3.0, 6.6, 2.1], 2),
        ([4.9, 2.5, 4.5, 1.7], 2), ([7.3, 2.9, 6.3, 1.8], 2),
        ([6.7, 2.5, 5.8, 1.8], 2), ([7.2, 3.6, 6.1, 2.5], 2),
    ]

    # ■ 데이터 분할
    random.seed(42)
    shuffled = iris_data[:]
    random.shuffle(shuffled)

    split_point = int(len(shuffled) * 0.7)
    train_set = shuffled[:split_point]
    test_set = shuffled[split_point:]

    print(f"  학습 데이터: {len(train_set)}개")
    print(f"  테스트 데이터: {len(test_set)}개")
    print()

    # ■ 정규화
    def compute_stats(data):
        n_features = len(data[0][0])
        mins = [min(row[0][i] for row in data) for i in range(n_features)]
        maxs = [max(row[0][i] for row in data) for i in range(n_features)]
        return mins, maxs

    def normalize(features, mins, maxs):
        return [
            (f - mn) / (mx - mn) if mx != mn else 0.0
            for f, mn, mx in zip(features, mins, maxs)
        ]

    mins, maxs = compute_stats(train_set)

    # ■ KNN 분류기 (다중 클래스)
    def knn_classify(train, query, k=5):
        query_norm = normalize(query, mins, maxs)
        distances = []
        for features, label in train:
            feat_norm = normalize(features, mins, maxs)
            dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(query_norm, feat_norm)))
            distances.append((dist, label))

        distances.sort(key=lambda x: x[0])
        neighbors = distances[:k]

        votes = {}
        for _, label in neighbors:
            votes[label] = votes.get(label, 0) + 1
        return max(votes, key=votes.get)

    # ■ 예측 및 평가
    label_names = {0: "Setosa", 1: "Versicolor", 2: "Virginica"}

    print("  ■ KNN 분류 결과 (k=5)")
    print("  ─────────────────────────────────────")

    correct = 0
    # 클래스별 TP, FP, FN 추적
    class_tp = {0: 0, 1: 0, 2: 0}
    class_fp = {0: 0, 1: 0, 2: 0}
    class_fn = {0: 0, 1: 0, 2: 0}

    for features, actual in test_set:
        predicted = knn_classify(train_set, features, k=5)
        match = "O" if predicted == actual else "X"
        if predicted == actual:
            correct += 1
            class_tp[actual] += 1
        else:
            class_fp[predicted] += 1
            class_fn[actual] += 1
        print(f"    특성={[f'{v:.1f}' for v in features]}"
              f" → 예측={label_names[predicted]}, 실제={label_names[actual]} [{match}]")

    accuracy = correct / len(test_set)
    print()
    print(f"  ■ 전체 정확도: {correct}/{len(test_set)} = {accuracy:.1%}")
    print()

    # ■ 클래스별 정밀도/재현율
    print("  ■ 클래스별 성능")
    print("  ─────────────────────────────────────")

    for cls in [0, 1, 2]:
        tp = class_tp[cls]
        fp = class_fp[cls]
        fn = class_fn[cls]
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
        print(f"    {label_names[cls]:12s}: 정밀도={prec:.2f}, 재현율={rec:.2f}, F1={f1:.2f}")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인 실행 함수
# ─────────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 72)
    print("  파이썬 학습 16단계: 머신러닝 준비 (from scratch)")
    print("=" * 72)

    lesson1_what_is_ml()
    lesson2_dataset()
    lesson3_normalization()
    lesson4_distance_metrics()
    lesson5_knn()
    lesson6_linear_regression()
    lesson7_gradient_descent()
    lesson8_confusion_matrix()
    lesson9_cross_validation()
    lesson10_iris_classifier()

    print()
    print("=" * 72)
    print("  모든 레슨 완료!")
    print("=" * 72)


if __name__ == "__main__":
    main()
