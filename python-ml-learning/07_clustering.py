# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#   파이썬 ML 학습 07단계: 클러스터링 (Clustering)
#   ─ 비슷한 데이터끼리 자동으로 묶기 ─
#
#   비유: 색깔별 구슬 분류하기
#     구슬이 섞여 있을 때, 비슷한 색끼리 그룹을 만드는 것.
#     정답을 미리 알려주지 않아도 스스로 그룹을 찾음!
#     이것이 '비지도 학습'의 핵심입니다.
#
#   실행 방법:
#     python 07_clustering.py
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import random


# ─────────────────────────────────────────────────────────────────────────
# ■ 도우미 함수
# ─────────────────────────────────────────────────────────────────────────

def euclidean_distance(a, b):
    """유클리드 거리: 두 점 사이의 직선 거리"""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def manhattan_distance(a, b):
    """맨해튼 거리: 격자 길을 따라가는 거리 (|x1-x2| + |y1-y2|)"""
    return sum(abs(x - y) for x, y in zip(a, b))


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 1: 클러스터링 개념
# ─────────────────────────────────────────────────────────────────────────

def lesson1_clustering_concept():
    """
    비유: 구슬 분류
      빨간 구슬, 파란 구슬, 초록 구슬이 섞여 있을 때
      비슷한 것끼리 모으면 자연스럽게 3개 그룹이 됨.
      정답 라벨 없이도 가능! (비지도 학습)
    """
    print("=" * 70)
    print("[레슨 1] 클러스터링 개념")
    print("=" * 70)
    print()
    print("  지도 학습 vs 비지도 학습:")
    print("  ┌──────────────┬─────────────────┬─────────────────┐")
    print("  │              │  지도 학습       │  비지도 학습    │")
    print("  ├──────────────┼─────────────────┼─────────────────┤")
    print("  │  정답 라벨   │  있음            │  없음           │")
    print("  │  예시        │  분류, 회귀      │  클러스터링     │")
    print("  │  비유        │  선생님이 답 줌  │  스스로 분류    │")
    print("  └──────────────┴─────────────────┴─────────────────┘")
    print()

    # 2D 점 데이터 시각화
    random.seed(42)
    points = []
    # 그룹 A: (2, 2) 근처
    for _ in range(5):
        points.append([2 + random.uniform(-0.5, 0.5),
                       2 + random.uniform(-0.5, 0.5)])
    # 그룹 B: (8, 8) 근처
    for _ in range(5):
        points.append([8 + random.uniform(-0.5, 0.5),
                       8 + random.uniform(-0.5, 0.5)])
    # 그룹 C: (2, 8) 근처
    for _ in range(5):
        points.append([2 + random.uniform(-0.5, 0.5),
                       8 + random.uniform(-0.5, 0.5)])

    # ASCII 플롯
    print("  데이터 분포 (10×10 격자):")
    grid = [["·" for _ in range(20)] for _ in range(10)]
    for p in points:
        x = min(int(p[0] * 2), 19)
        y = min(9 - int(p[1]), 9)
        if 0 <= x < 20 and 0 <= y < 10:
            grid[y][x] = "●"

    for row in grid:
        print("    " + "".join(row))
    print()
    print("  → 눈으로 봐도 3개 그룹이 보입니다!")
    print("  → K-Means가 이걸 자동으로 찾아줍니다.")
    print()

    return points


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 2: K-Means 알고리즘 단계별
# ─────────────────────────────────────────────────────────────────────────

def lesson2_kmeans_step_by_step(points):
    """
    K-Means: K개의 중심점을 찾아 데이터를 K개 그룹으로 나누는 알고리즘.

    비유: 학교 운동장에서 팀 나누기
      1. 대장 3명이 아무 곳에나 섬 (초기 중심)
      2. 각 학생은 가장 가까운 대장에게 감 (할당)
      3. 대장은 팀원들의 가운데로 이동 (중심 업데이트)
      4. 2-3을 반복하면 팀이 안정됨!
    """
    print("=" * 70)
    print("[레슨 2] K-Means 알고리즘 단계별")
    print("=" * 70)
    print()

    K = 3
    random.seed(10)

    # 초기 중심점 무작위 선택
    centroids = [[random.uniform(1, 9), random.uniform(1, 9)] for _ in range(K)]

    print(f"  K = {K} (3개 그룹으로 나눌 것)")
    print()

    for iteration in range(5):
        print(f"  --- 반복 {iteration + 1} ---")
        print(f"    중심점: ", end="")
        for i, c in enumerate(centroids):
            print(f"C{i}=({c[0]:.1f},{c[1]:.1f}) ", end="")
        print()

        # Step 1: 각 점을 가장 가까운 중심에 할당
        assignments = []
        for p in points:
            distances = [euclidean_distance(p, c) for c in centroids]
            nearest = distances.index(min(distances))
            assignments.append(nearest)

        # 그룹별 개수
        group_counts = [0] * K
        for a in assignments:
            group_counts[a] += 1
        print(f"    그룹별 개수: {group_counts}")

        # Step 2: 중심점 업데이트
        new_centroids = []
        for k in range(K):
            members = [points[i] for i in range(len(points)) if assignments[i] == k]
            if members:
                new_c = [sum(m[d] for m in members) / len(members) for d in range(2)]
            else:
                new_c = centroids[k]
            new_centroids.append(new_c)

        # 이동 거리
        moves = [euclidean_distance(centroids[k], new_centroids[k]) for k in range(K)]
        print(f"    중심 이동: [{', '.join(f'{m:.3f}' for m in moves)}]")

        centroids = new_centroids

        if max(moves) < 0.01:
            print("    → 수렴! 더 이상 중심이 움직이지 않음")
            break
        print()

    print()
    print("  최종 결과:")
    for k in range(K):
        members = [i for i in range(len(points)) if assignments[i] == k]
        print(f"    그룹 {k}: {len(members)}개 점, "
              f"중심=({centroids[k][0]:.1f}, {centroids[k][1]:.1f})")
    print()

    return centroids, assignments


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 3: K 선택하기 (엘보우 방법)
# ─────────────────────────────────────────────────────────────────────────

def lesson3_elbow_method(points):
    """
    K를 몇으로 할지 어떻게 정할까?

    비유: 피자 자르기
      2등분 → 너무 큼
      4등분 → 적당
      100등분 → 너무 작음, 의미 없음
      적당한 지점을 찾아야 함!

    엘보우 방법: K를 늘려가며 그룹 내 거리 합을 그림.
    팔꿈치(급격히 꺾이는) 지점이 적절한 K.
    """
    print("=" * 70)
    print("[레슨 3] K 선택하기 (엘보우 방법)")
    print("=" * 70)
    print()

    random.seed(42)

    print("  K를 1부터 6까지 늘려가며 그룹 내 거리 합(Inertia) 측정:")
    print()

    for K in range(1, 7):
        # 간단한 K-Means 실행
        centroids = [points[random.randint(0, len(points)-1)] for _ in range(K)]

        for _ in range(10):  # 10번 반복
            assignments = []
            for p in points:
                distances = [euclidean_distance(p, c) for c in centroids]
                assignments.append(distances.index(min(distances)))

            new_centroids = []
            for k in range(K):
                members = [points[i] for i in range(len(points)) if assignments[i] == k]
                if members:
                    new_centroids.append([sum(m[d] for m in members) / len(members) for d in range(2)])
                else:
                    new_centroids.append(centroids[k])
            centroids = new_centroids

        # Inertia 계산 (각 점과 소속 중심 사이 거리 제곱 합)
        inertia = 0
        for i, p in enumerate(points):
            inertia += euclidean_distance(p, centroids[assignments[i]]) ** 2

        bar = "#" * int(inertia / 5)
        elbow = " ← 팔꿈치!" if K == 3 else ""
        print(f"    K={K}: Inertia={inertia:>7.1f} {bar}{elbow}")

    print()
    print("  → K=3에서 급격히 꺾임! (3개 그룹이 자연스러움)")
    print("  → K를 더 늘려도 개선폭이 작음")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 4: 거리 측정 방법
# ─────────────────────────────────────────────────────────────────────────

def lesson4_distance_metrics():
    """
    클러스터링에서 '거리'를 어떻게 재는지.

    비유: 서울에서 부산까지의 거리
      유클리드 = 비행기 직선 거리
      맨해튼 = 도로를 따라 간 거리
      코사인 = 방향이 비슷한 정도
    """
    print("=" * 70)
    print("[레슨 4] 거리 측정 방법")
    print("=" * 70)
    print()

    a = [1, 2]
    b = [4, 6]

    euc = euclidean_distance(a, b)
    man = manhattan_distance(a, b)

    # 코사인 유사도 → 코사인 거리
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x**2 for x in a))
    norm_b = math.sqrt(sum(x**2 for x in b))
    cos_sim = dot / (norm_a * norm_b)
    cos_dist = 1 - cos_sim

    print(f"  점 A = {a}")
    print(f"  점 B = {b}")
    print()
    print(f"  유클리드 거리: √((4-1)² + (6-2)²) = √(9+16) = {euc:.2f}")
    print(f"    → 직선 거리")
    print()
    print(f"  맨해튼 거리:  |4-1| + |6-2| = 3 + 4 = {man:.0f}")
    print(f"    → 격자 도로 거리")
    print()
    print(f"  코사인 거리:  1 - cos(A,B) = 1 - {cos_sim:.3f} = {cos_dist:.3f}")
    print(f"    → 방향 차이 (텍스트/고차원에서 유용)")
    print()

    # 거리별 특성 비교
    print("  ┌──────────────┬──────────────────────────────────────┐")
    print("  │  거리        │  특징                                │")
    print("  ├──────────────┼──────────────────────────────────────┤")
    print("  │ 유클리드     │ 가장 직관적, 크기에 민감             │")
    print("  │ 맨해튼       │ 이상치에 덜 민감                     │")
    print("  │ 코사인       │ 크기 무시, 방향만 비교 (텍스트 추천) │")
    print("  └──────────────┴──────────────────────────────────────┘")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 5: DBSCAN 개념
# ─────────────────────────────────────────────────────────────────────────

def lesson5_dbscan_concept():
    """
    DBSCAN: 밀도 기반 클러스터링. K를 미리 정할 필요 없음!

    비유: 사람들이 모여있는 곳 찾기
      공원에서 사람들이 모여있는 그룹을 찾는 것.
      - 사람이 많이 몰려 있으면 → 하나의 그룹
      - 외따로 떨어진 사람 → 이상치(노이즈)
      K를 미리 정하지 않아도 그룹이 자동으로 정해짐!
    """
    print("=" * 70)
    print("[레슨 5] DBSCAN 개념")
    print("=" * 70)
    print()
    print("  DBSCAN 핵심 개념:")
    print("    eps = 이웃 반경 (이 안에 있으면 이웃)")
    print("    min_samples = 최소 이웃 수 (이 이상이면 핵심 점)")
    print()

    # 간단한 DBSCAN 시뮬레이션
    points = [
        [1, 1], [1.5, 1.2], [1.2, 0.8],  # 그룹 1
        [5, 5], [5.3, 5.1], [4.8, 5.2], [5.1, 4.9],  # 그룹 2
        [9, 1],  # 노이즈
    ]
    eps = 1.5
    min_pts = 2

    print(f"  점 데이터: {len(points)}개")
    print(f"  eps = {eps}, min_samples = {min_pts}")
    print()

    # 각 점의 이웃 찾기
    print("  각 점의 이웃 수:")
    neighbors = []
    for i, p in enumerate(points):
        n_count = 0
        for j, q in enumerate(points):
            if i != j and euclidean_distance(p, q) <= eps:
                n_count += 1
        neighbors.append(n_count)
        point_type = "핵심 점" if n_count >= min_pts else "경계/노이즈"
        print(f"    점{i} ({p[0]},{p[1]}): 이웃 {n_count}개 → {point_type}")

    print()
    print("  K-Means vs DBSCAN:")
    print("  ┌──────────────┬─────────────────┬─────────────────┐")
    print("  │              │  K-Means        │  DBSCAN         │")
    print("  ├──────────────┼─────────────────┼─────────────────┤")
    print("  │ K 필요?      │ 예              │ 아니오          │")
    print("  │ 모양 제한    │ 원형만          │ 자유로운 모양   │")
    print("  │ 이상치 처리  │ 못 함           │ 노이즈로 분류   │")
    print("  │ 파라미터     │ K               │ eps, min_pts    │")
    print("  └──────────────┴─────────────────┴─────────────────┘")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■" * 72)
    print("  파이썬 ML 07단계 : 클러스터링 (Clustering)")
    print("  비유: 색깔별 구슬을 자동으로 분류하기")
    print("■" * 72)
    print()

    points = lesson1_clustering_concept()
    centroids, assignments = lesson2_kmeans_step_by_step(points)
    lesson3_elbow_method(points)
    lesson4_distance_metrics()
    lesson5_dbscan_concept()


if __name__ == "__main__":
    main()
