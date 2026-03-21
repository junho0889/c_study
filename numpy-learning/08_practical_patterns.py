# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   NumPy 학습 08단계: 실전 패턴(Practical Patterns)
#   ─ 이미지 처리, 시계열, 거리 행렬, 원-핫, 배치, 추천 시스템 ─
#   ■ 실행 방법: python 08_practical_patterns.py
#   ■ NumPy 설치: pip install numpy
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


import math
import random


# ═══════════════════════════════════════════════════════════════════════════════
#  1. 이미지 처리 기초 - 이미지 = 3D 배열!
# ═══════════════════════════════════════════════════════════════════════════════
#
#  컴퓨터에서 이미지는 숫자 배열이야!
#  흑백: (높이, 너비) 2D 배열, 값 0~255 (0=검정, 255=흰색)
#  컬러: (높이, 너비, 3) 3D 배열, RGB 각각 0~255
#
#  작은 이미지로 연습해보자!

print("=" * 70)
print("1. 이미지 처리 기초")
print("=" * 70)

random.seed(42)


def create_gradient_image(h, w):
    """그라디언트(점점 밝아지는) 흑백 이미지"""
    return [[int(255 * c / (w - 1)) for c in range(w)] for r in range(h)]


def display_image(img, title=""):
    """이미지를 텍스트로 시각화"""
    if title:
        print(f"\n  {title}:")
    chars = " ░▒▓█"
    if isinstance(img[0][0], list):
        # RGB → 밝기로 변환해서 표시
        for row in img:
            line = "  "
            for pixel in row:
                brightness = int(0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2])
                idx = min(brightness * len(chars) // 256, len(chars) - 1)
                line += chars[idx] * 2
            print(line)
    else:
        for row in img:
            line = "  "
            for val in row:
                idx = min(int(val) * len(chars) // 256, len(chars) - 1)
                line += chars[idx] * 2
            print(line)


# ── 밝기 조절 ──
print(f"\n── 밝기 조절 ──")
img = create_gradient_image(6, 10)
display_image(img, "원본 그라디언트")


def adjust_brightness(img, factor):
    """밝기 조절: factor > 1 밝게, < 1 어둡게
    모든 픽셀에 factor를 곱하고 0~255로 클리핑!
    """
    return [[max(0, min(255, int(val * factor))) for val in row] for row in img]


bright = adjust_brightness(img, 1.5)
dark = adjust_brightness(img, 0.5)
display_image(bright, "밝게 (×1.5)")
display_image(dark, "어둡게 (×0.5)")

# 【NumPy】
# bright = np.clip(img * 1.5, 0, 255).astype(np.uint8)


# ── 흑백 변환 ──
print(f"\n── RGB → 흑백 변환 ──")


def rgb_to_grayscale(img):
    """컬러 → 흑백
    공식: Gray = 0.299×R + 0.587×G + 0.114×B
    """
    h = len(img)
    w = len(img[0])
    gray = [[0] * w for _ in range(h)]
    for r in range(h):
        for c in range(w):
            R, G, B = img[r][c]
            gray[r][c] = int(0.299 * R + 0.587 * G + 0.114 * B)
    return gray


# 간단한 RGB 이미지 만들기
rgb_img = [[[random.randint(0, 255) for _ in range(3)]
            for _ in range(8)] for _ in range(6)]
gray_img = rgb_to_grayscale(rgb_img)
display_image(rgb_img, "컬러 (랜덤)")
display_image(gray_img, "흑백 변환")

# 【NumPy】 gray = np.dot(rgb_img, [0.299, 0.587, 0.114])


# ── 이미지 회전 ──
print(f"\n── 이미지 회전 ──")


def rotate_90_clockwise(img):
    """시계방향 90도 회전"""
    h = len(img)
    w = len(img[0])
    return [[img[h - 1 - r][c] for r in range(h)] for c in range(w)]


def rotate_180(img):
    """180도 회전"""
    return [row[::-1] for row in img[::-1]]


small_img = [[10, 50, 100, 200],
             [20, 80, 150, 220],
             [30, 120, 180, 250]]

print(f"  원본 (3×4): {[row for row in small_img]}")
rotated = rotate_90_clockwise(small_img)
print(f"  90° 회전 (4×3): {[row for row in rotated]}")

# 【NumPy】 np.rot90(img, k=-1)  # 시계방향 90도


# ── 간단한 블러(흐림) 필터 ──
print(f"\n── 블러(흐림) 필터 ──")


def apply_blur(img, kernel_size=3):
    """평균 블러 필터
    각 픽셀을 주변 픽셀의 평균값으로 대체!
    kernel_size: 주변 몇 칸까지 볼지 (3이면 3×3 영역)
    """
    h = len(img)
    w = len(img[0])
    pad = kernel_size // 2
    result = [[0] * w for _ in range(h)]

    for r in range(h):
        for c in range(w):
            total = 0
            count = 0
            for dr in range(-pad, pad + 1):
                for dc in range(-pad, pad + 1):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < h and 0 <= nc < w:
                        total += img[nr][nc]
                        count += 1
            result[r][c] = total // count

    return result


original = create_gradient_image(6, 10)
blurred = apply_blur(original, 3)
display_image(original, "원본")
display_image(blurred, "블러 적용")
print(f"  → 각 픽셀이 주변 3×3 영역의 평균값으로 변환!")

# 【NumPy】
# from scipy.ndimage import uniform_filter
# blurred = uniform_filter(img, size=3)


# ═══════════════════════════════════════════════════════════════════════════════
#  2. 시계열 분석 - 이동 평균, 트렌드, 계절성
# ═══════════════════════════════════════════════════════════════════════════════
#
#  시계열 = 시간에 따라 변하는 데이터!
#  주가, 기온, 판매량, 심박수...

print("\n" + "=" * 70)
print("2. 시계열 분석")
print("=" * 70)

random.seed(42)


# ── 시계열 데이터 생성 ──
def generate_time_series(n, trend=0.5, seasonality=10, noise=5):
    """트렌드 + 계절성 + 노이즈가 있는 시계열"""
    data = []
    for t in range(n):
        value = (trend * t +                                    # 트렌드 (상승/하락)
                 seasonality * math.sin(2 * math.pi * t / 12) + # 계절성 (12개월 주기)
                 random.gauss(0, noise) +                        # 노이즈 (랜덤 변동)
                 50)                                             # 기본값
        data.append(round(value, 1))
    return data


sales = generate_time_series(36)  # 36개월 (3년)
print(f"\n월별 판매량 (36개월): {sales[:12]}...")


# ── 이동 평균 (Moving Average) ──
def moving_average(data, window):
    """이동 평균: 최근 window개의 평균
    노이즈를 줄이고 트렌드를 보여줘!

    예: window=3이면 최근 3개의 평균
    [1, 3, 5, 7, 9] → [-, -, 3, 5, 7]
    """
    result = [None] * (window - 1)  # 첫 부분은 계산 불가
    for i in range(window - 1, len(data)):
        avg = sum(data[i - window + 1:i + 1]) / window
        result.append(round(avg, 1))
    return result


ma_3 = moving_average(sales, 3)
ma_6 = moving_average(sales, 6)

print(f"\n── 이동 평균 ──")
print(f"  원본 (첫 12개):   {sales[:12]}")
print(f"  3개월 이동평균:   {ma_3[:12]}")
print(f"  6개월 이동평균:   {ma_6[:12]}")
print(f"  → window가 클수록 부드러워지지만, 반응이 느려!")

# 【NumPy】
# np.convolve(sales, np.ones(3)/3, mode='valid')  # 이동 평균


# ── 트렌드 감지 ──
def detect_trend(data, window=6):
    """트렌드 방향 감지
    이동 평균의 차이로 상승/하락 판단
    """
    ma = moving_average(data, window)
    valid = [x for x in ma if x is not None]
    if len(valid) < 2:
        return "불명"
    diffs = [valid[i+1] - valid[i] for i in range(len(valid)-1)]
    avg_diff = sum(diffs) / len(diffs)
    if avg_diff > 0.5:
        return f"상승 트렌드 (월 평균 +{avg_diff:.1f})"
    elif avg_diff < -0.5:
        return f"하락 트렌드 (월 평균 {avg_diff:.1f})"
    else:
        return f"횡보 (월 평균 {avg_diff:+.1f})"


trend = detect_trend(sales)
print(f"\n  트렌드 분석: {trend}")


# ── 계절성 분해 ──
def detect_seasonality(data, period=12):
    """계절성 패턴 추출
    같은 '월'의 데이터를 모아서 평균!
    """
    seasonal = [0.0] * period
    counts = [0] * period
    for i, val in enumerate(data):
        month = i % period
        seasonal[month] += val
        counts[month] += 1

    for i in range(period):
        if counts[i] > 0:
            seasonal[i] /= counts[i]

    # 전체 평균을 빼서 계절 효과만 추출
    overall_mean = sum(seasonal) / len(seasonal)
    seasonal = [round(s - overall_mean, 1) for s in seasonal]
    return seasonal


seasonality = detect_seasonality(sales)
print(f"\n── 계절성 패턴 (12개월) ──")
months = ["1월", "2월", "3월", "4월", "5월", "6월",
          "7월", "8월", "9월", "10월", "11월", "12월"]
for m, s in zip(months, seasonality):
    bar = "+" * max(0, int(s)) + "-" * max(0, int(-s))
    print(f"  {m}: {s:+6.1f}  {bar}")

# 【NumPy】
# seasonal = np.array(sales).reshape(-1, 12).mean(axis=0)
# seasonal -= seasonal.mean()


# ═══════════════════════════════════════════════════════════════════════════════
#  3. 거리 행렬 계산 - 모든 점 쌍의 거리 (KNN의 기초!)
# ═══════════════════════════════════════════════════════════════════════════════
#
#  N개의 점이 있을 때, 모든 점 쌍의 거리를 계산!
#  KNN(K-최근접 이웃) 알고리즘의 핵심!

print("\n" + "=" * 70)
print("3. 거리 행렬 - 모든 점 쌍의 거리")
print("=" * 70)


def euclidean_distance(p1, p2):
    """유클리드 거리"""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))


def distance_matrix(points):
    """모든 점 쌍의 거리 행렬 계산
    N개 점 → N×N 거리 행렬
    """
    n = len(points)
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = euclidean_distance(points[i], points[j])
            dist[i][j] = d
            dist[j][i] = d  # 대칭!
    return dist


def knn_predict(train_points, train_labels, query, k=3):
    """K-최근접 이웃 분류
    query 점에서 가장 가까운 k개 훈련 데이터의 라벨 중 다수결!
    """
    distances = [(euclidean_distance(query, p), label)
                 for p, label in zip(train_points, train_labels)]
    distances.sort(key=lambda x: x[0])
    nearest_k = distances[:k]

    # 다수결
    label_counts = {}
    for _, label in nearest_k:
        label_counts[label] = label_counts.get(label, 0) + 1
    return max(label_counts, key=label_counts.get), nearest_k


# 2D 점 데이터 (과일 분류: 무게 vs 단맛)
fruits = {
    '사과': [(150, 7), (160, 8), (140, 6), (155, 7.5)],
    '포도': [(5, 9), (4, 8.5), (6, 9.5), (5.5, 8)],
    '수박': [(3000, 6), (3500, 7), (2800, 5.5), (3200, 6.5)],
}

train_points = []
train_labels = []
for label, points in fruits.items():
    for p in points:
        train_points.append(p)
        train_labels.append(label)

# 거리 행렬
print(f"\n  과일 데이터 ({len(train_points)}개):")
for label, points in fruits.items():
    print(f"    {label}: {points}")

# KNN 분류
print(f"\n── KNN 분류 (K=3) ──")
test_points = [(145, 7), (5, 9), (3100, 6)]
for query in test_points:
    prediction, neighbors = knn_predict(train_points, train_labels, query, k=3)
    print(f"  ({query[0]:>4}, {query[1]}) → {prediction}")
    print(f"    가까운 3개: {[(f'{d:.1f}', l) for d, l in neighbors]}")

# 【NumPy로 거리 행렬 한 줄!】
# from scipy.spatial.distance import cdist
# dist_matrix = cdist(points, points, metric='euclidean')
#
# 또는 순수 NumPy:
# diff = points[:, np.newaxis, :] - points[np.newaxis, :, :]
# dist_matrix = np.sqrt((diff ** 2).sum(axis=-1))


# ═══════════════════════════════════════════════════════════════════════════════
#  4. 원-핫 인코딩 - 범주형 데이터 변환
# ═══════════════════════════════════════════════════════════════════════════════
#
#  컴퓨터는 "사과, 바나나, 체리"를 이해 못 해!
#  숫자로 바꿔야 해! 근데 사과=1, 바나나=2로 하면?
#  "바나나가 사과보다 2배 크다?"는 의미가 되어버려!
#
#  원-핫 인코딩: 해당 위치만 1, 나머지 0
#  사과   → [1, 0, 0]
#  바나나 → [0, 1, 0]
#  체리   → [0, 0, 1]

print("\n" + "=" * 70)
print("4. 원-핫 인코딩")
print("=" * 70)


def one_hot_encode(labels):
    """원-핫 인코딩
    np.eye() 활용 가능!
    """
    unique = sorted(set(labels))
    label_to_idx = {label: i for i, label in enumerate(unique)}
    n_classes = len(unique)

    # 단위행렬의 행을 선택하면 원-핫 벡터!
    eye = [[1 if i == j else 0 for j in range(n_classes)] for i in range(n_classes)]

    encoded = [eye[label_to_idx[label]] for label in labels]
    return encoded, unique


def one_hot_decode(encoded, classes):
    """원-핫 → 원래 라벨로 복원"""
    return [classes[row.index(1)] for row in encoded]


# 과일 라벨
labels = ["사과", "바나나", "사과", "체리", "바나나", "체리", "사과"]
encoded, classes = one_hot_encode(labels)

print(f"\n원본 라벨: {labels}")
print(f"클래스:    {classes}")
print(f"\n원-핫 인코딩:")
for label, vec in zip(labels, encoded):
    print(f"  {label:>4} → {vec}")

# 복원
decoded = one_hot_decode(encoded, classes)
print(f"\n복원: {decoded}")
print(f"원본과 같은가? {labels == decoded}")

# 【NumPy】
# classes = np.unique(labels)
# label_indices = np.searchsorted(classes, labels)
# one_hot = np.eye(len(classes))[label_indices]  ← 한 줄!

print(f"\n── np.eye 트릭! ──")
print(f"  단위행렬에서 인덱스로 행을 선택하면 원-핫 벡터!")
print(f"  np.eye(3)[0] → [1, 0, 0]  (0번 클래스)")
print(f"  np.eye(3)[2] → [0, 0, 1]  (2번 클래스)")
print(f"  np.eye(3)[[0,1,0,2]] → 한 번에 여러 개!")


# ═══════════════════════════════════════════════════════════════════════════════
#  5. 배치 처리 패턴 - 대용량 데이터 청크 처리
# ═══════════════════════════════════════════════════════════════════════════════
#
#  1000만 개 데이터를 한 번에 처리? 메모리 부족!
#  해결: "배치"로 나눠서 처리!
#  마치 이사할 때 박스에 나눠 담아 옮기듯이!

print("\n" + "=" * 70)
print("5. 배치 처리 패턴")
print("=" * 70)


def batch_generator(data, batch_size):
    """데이터를 batch_size 크기로 나눠서 반환
    메모리 효율적! 전체를 로드하지 않아도 됨!
    """
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]


def process_in_batches(data, batch_size, process_func):
    """배치 단위로 처리하고 결과 합치기"""
    results = []
    total_processed = 0

    for batch_idx, batch in enumerate(batch_generator(data, batch_size)):
        result = process_func(batch)
        results.append(result)
        total_processed += len(batch)

        if batch_idx < 3 or batch_idx == (len(data) // batch_size):
            print(f"    배치 {batch_idx}: {len(batch)}개 처리 "
                  f"(총 {total_processed}/{len(data)})")

    return results


# 10만 개 데이터 배치 처리
random.seed(42)
big_data = [random.gauss(0, 1) for _ in range(100_000)]

print(f"\n데이터 크기: {len(big_data):,}개")
print(f"\n── 배치별 평균 계산 (배치 크기: 10,000) ──")

batch_means = process_in_batches(
    big_data, 10_000,
    lambda batch: sum(batch) / len(batch)
)

overall_mean = sum(batch_means) / len(batch_means)
print(f"\n  배치별 평균: {[f'{m:.4f}' for m in batch_means]}")
print(f"  전체 평균:   {overall_mean:.4f}")
print(f"  실제 평균:   {sum(big_data)/len(big_data):.4f}")

# ── 온라인 학습 패턴 (누적 평균) ──
print(f"\n── 온라인 평균 (데이터가 계속 들어올 때) ──")


def online_mean(stream, report_every=20000):
    """데이터를 하나씩 받으며 평균 업데이트
    전체 데이터를 저장할 필요 없음!
    공식: new_mean = old_mean + (new_value - old_mean) / n
    """
    mean = 0.0
    for n, value in enumerate(stream, 1):
        mean += (value - mean) / n
        if n % report_every == 0:
            print(f"    {n:>6}개 처리: 현재 평균 = {mean:.6f}")
    return mean


result = online_mean(big_data)
print(f"  최종 평균: {result:.6f}")
print(f"  → 메모리 O(1)! 1억 개 데이터도 문제 없어!")

# 【NumPy 배치 처리】
# for i in range(0, len(data), batch_size):
#     batch = data[i:i+batch_size]
#     result = np.mean(batch)
# # 또는 np.array_split(data, n_batches)


# ═══════════════════════════════════════════════════════════════════════════════
#  6. 실전 프로젝트: 간단한 추천 시스템 (코사인 유사도)
# ═══════════════════════════════════════════════════════════════════════════════
#
#  넷플릭스, 유튜브의 추천 시스템 핵심 원리!
#  "비슷한 취향의 사용자가 좋아한 것을 추천!"
#
#  핵심: 코사인 유사도로 사용자 간 유사도 측정

print("\n" + "=" * 70)
print("실전 프로젝트: 추천 시스템")
print("=" * 70)


def cosine_similarity(a, b):
    """코사인 유사도: 두 벡터의 방향 유사도
    1에 가까울수록 취향이 비슷!
    """
    dot_product = sum(ai * bi for ai, bi in zip(a, b))
    norm_a = math.sqrt(sum(x ** 2 for x in a))
    norm_b = math.sqrt(sum(x ** 2 for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0
    return dot_product / (norm_a * norm_b)


def similarity_matrix(ratings):
    """모든 사용자 쌍의 유사도 행렬"""
    n = len(ratings)
    sim = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            sim[i][j] = cosine_similarity(ratings[i], ratings[j])
    return sim


def recommend(user_idx, ratings, sim_matrix, movie_names, top_n=3, k=3):
    """사용자에게 영화 추천!

    알고리즘:
    1. 대상 사용자와 가장 유사한 k명 찾기
    2. 대상 사용자가 안 본(0점) 영화 중
    3. 유사 사용자들의 평점을 가중평균으로 예측
    4. 예측 점수 높은 순으로 추천!
    """
    n_users = len(ratings)
    n_movies = len(ratings[0])

    # 유사한 사용자 k명 찾기 (자기 자신 제외)
    similarities = [(i, sim_matrix[user_idx][i])
                    for i in range(n_users) if i != user_idx]
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_k_users = similarities[:k]

    # 안 본 영화에 대해 예측 점수 계산
    predictions = []
    for movie_idx in range(n_movies):
        if ratings[user_idx][movie_idx] > 0:
            continue  # 이미 본 영화는 스킵

        # 유사 사용자들의 가중 평균
        weighted_sum = 0
        sim_sum = 0
        for similar_user, similarity in top_k_users:
            if ratings[similar_user][movie_idx] > 0:
                weighted_sum += similarity * ratings[similar_user][movie_idx]
                sim_sum += abs(similarity)

        if sim_sum > 0:
            predicted_rating = weighted_sum / sim_sum
            predictions.append((movie_idx, predicted_rating))

    predictions.sort(key=lambda x: x[1], reverse=True)
    return predictions[:top_n]


# 영화 평점 데이터 (0 = 안 봄, 1~5 = 평점)
movie_names = ["어벤져스", "로맨스", "코미디", "공포", "다큐", "SF", "애니"]
user_names = ["민수", "지영", "태호", "수진", "현우", "미라"]

# 사용자 × 영화 평점 행렬
ratings = [
    #  어벤  로맨  코미  공포  다큐   SF  애니
    [  5,    1,    3,    4,    2,    5,    3  ],  # 민수: 액션/SF 좋아함
    [  1,    5,    4,    1,    3,    1,    4  ],  # 지영: 로맨스/코미디
    [  5,    1,    2,    5,    1,    4,    2  ],  # 태호: 액션/공포
    [  2,    4,    5,    1,    4,    2,    5  ],  # 수진: 코미디/애니
    [  4,    2,    3,    3,    0,    0,    0  ],  # 현우: 일부만 봄!
    [  0,    0,    4,    0,    5,    0,    3  ],  # 미라: 일부만 봄!
]

print(f"\n영화 평점 (0=안봄, 1~5=평점):")
print(f"{'':>6}", end="")
for name in movie_names:
    print(f"{name:>6}", end="")
print()
for i, name in enumerate(user_names):
    print(f"{name:>6}", end="")
    for r in ratings[i]:
        if r == 0:
            print(f"{'  -':>6}", end="")
        else:
            print(f"{r:>6}", end="")
    print()

# 유사도 행렬 계산
sim = similarity_matrix(ratings)
print(f"\n사용자 유사도 행렬:")
print(f"{'':>6}", end="")
for name in user_names:
    print(f"{name:>6}", end="")
print()
for i, name in enumerate(user_names):
    print(f"{name:>6}", end="")
    for j in range(len(user_names)):
        print(f"{sim[i][j]:>6.2f}", end="")
    print()

# 추천!
print(f"\n═══ 추천 결과 ═══")
for user_idx in [4, 5]:  # 현우, 미라에게 추천
    name = user_names[user_idx]
    recs = recommend(user_idx, ratings, sim, movie_names, top_n=3)
    print(f"\n  {name}님 추천:")
    unseen = [movie_names[i] for i in range(len(movie_names)) if ratings[user_idx][i] == 0]
    print(f"    안 본 영화: {unseen}")

    if recs:
        for movie_idx, pred_rating in recs:
            print(f"    → {movie_names[movie_idx]:>6}: 예측 평점 {pred_rating:.1f}점 {'⭐' * round(pred_rating)}")
    else:
        print(f"    추천할 영화 없음")

# 현우의 가장 유사한 사용자 분석
print(f"\n── 현우와 가장 유사한 사용자 ──")
hyunwoo_sim = [(user_names[i], sim[4][i]) for i in range(6) if i != 4]
hyunwoo_sim.sort(key=lambda x: x[1], reverse=True)
for name, s in hyunwoo_sim:
    bar = "█" * int(max(0, s) * 20)
    print(f"  {name}: {s:+.3f}  {bar}")

# 【NumPy로 한다면】
# ratings = np.array(ratings, dtype=np.float64)
# # 코사인 유사도 행렬 (한 줄!)
# norms = np.linalg.norm(ratings, axis=1, keepdims=True)
# sim_matrix = ratings @ ratings.T / (norms @ norms.T + 1e-8)
#
# # 추천 예측 (벡터화)
# user_sims = sim_matrix[user_idx]
# weighted = user_sims[:, None] * ratings
# predictions = weighted.sum(axis=0) / (np.abs(user_sims).sum() + 1e-8)


# ═══════════════════════════════════════════════════════════════════════════════
#  핵심 정리
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("핵심 정리")
print("=" * 70)
print("""
  1. 이미지 = 3D 배열 (높이, 너비, 채널)
     - 밝기 조절: × factor + clip
     - 흑백 변환: 0.299R + 0.587G + 0.114B
     - 블러: 주변 픽셀 평균
  2. 시계열:
     - 이동 평균: 노이즈 제거, 트렌드 발견
     - 계절성: 같은 주기끼리 묶어서 패턴 추출
  3. 거리 행렬: 모든 점 쌍의 거리 → KNN의 기초
     - NumPy 브로드캐스팅으로 한 줄 계산 가능!
  4. 원-핫 인코딩: 범주 → [0,0,...,1,...,0]
     - np.eye(n)[indices] 트릭!
  5. 배치 처리: 대용량 데이터를 나눠서 처리
     - 온라인 평균: 메모리 O(1)!
  6. 추천 시스템: 코사인 유사도로 취향 비교
     - ratings @ ratings.T 로 유사도 행렬 한 번에!
""")
