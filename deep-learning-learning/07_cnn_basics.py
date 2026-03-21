# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#   딥러닝 학습 07단계: CNN 기초 (합성곱 신경망)
#   ─ 이미지에서 특징을 찾아내는 방법 ─
#
#   비유: 돋보기로 사진 훑기
#     큰 사진을 한눈에 보면 세부를 놓칩니다.
#     작은 돋보기로 왼쪽 위부터 오른쪽 아래까지 훑으면
#     가장자리, 색 변화, 무늬 같은 세부 특징을 발견할 수 있습니다.
#     CNN의 필터(커널)가 바로 이 돋보기 역할을 합니다.
#
#   실행 방법:
#     python 07_cnn_basics.py
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ─────────────────────────────────────────────────────────────────────────
# ■ 도우미 함수
# ─────────────────────────────────────────────────────────────────────────

def print_matrix(matrix, label="", indent=4):
    """2D 행렬을 보기 좋게 출력"""
    prefix = " " * indent
    if label:
        print(f"{prefix}{label}")
    for row in matrix:
        print(prefix + "  [" + ", ".join(f"{v:>6.1f}" for v in row) + "]")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 1: 합성곱 연산 이해하기
# ─────────────────────────────────────────────────────────────────────────

def lesson1_convolution_concept():
    """
    합성곱(Convolution): 필터를 이미지 위에서 슬라이딩하며
    겹치는 부분끼리 곱하고 더하는 연산.

    비유: 돋보기(필터)를 사진 위에 대고
          돋보기 안에 보이는 부분의 점수를 매기는 것.
          돋보기를 한 칸씩 옮기며 전체 사진을 훑습니다.
    """
    print("=" * 70)
    print("[레슨 1] 합성곱 연산이란?")
    print("=" * 70)
    print()
    print("  돋보기(필터)를 사진 위에서 밀면서 점수를 매깁니다.")
    print()

    # 5x5 입력 이미지 (숫자로 된 흑백 이미지라고 생각)
    image = [
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
    ]

    # 3x3 필터 (가로선 감지)
    kernel = [
        [-1, -1, -1],
        [ 2,  2,  2],
        [-1, -1, -1],
    ]

    print_matrix(image, "입력 이미지 (5×5):")
    print_matrix(kernel, "필터/커널 (3×3) - 가로선 감지용:")

    # 합성곱 수행 (stride=1, no padding)
    img_h, img_w = len(image), len(image[0])
    k_h, k_w = len(kernel), len(kernel[0])
    out_h = img_h - k_h + 1  # 3
    out_w = img_w - k_w + 1  # 3

    output = []
    for i in range(out_h):
        row = []
        for j in range(out_w):
            total = 0.0
            for ki in range(k_h):
                for kj in range(k_w):
                    total += image[i + ki][j + kj] * kernel[ki][kj]
            row.append(total)
        output.append(row)

    print("  합성곱 계산 과정 (첫 번째 위치):")
    print("    왼쪽 위 3×3 영역과 필터를 겹쳐서 곱하고 더하기:")
    detail = 0
    for ki in range(k_h):
        parts = []
        for kj in range(k_w):
            val = image[ki][kj] * kernel[ki][kj]
            parts.append(f"{image[ki][kj]}×{kernel[ki][kj]:>2}={val:>2}")
            detail += val
        print(f"      {', '.join(parts)}")
    print(f"    합계 = {detail}")
    print()

    print_matrix(output, "합성곱 결과 (특성맵, 3×3):")
    print("  → 가로선이 있는 위치에서 높은 값이 나옵니다!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 2: 스트라이드 (Stride)
# ─────────────────────────────────────────────────────────────────────────

def lesson2_stride():
    """
    스트라이드: 돋보기를 한 번에 몇 칸씩 옮기느냐.

    비유: 책을 읽을 때
      stride=1 → 한 글자씩 읽기 (꼼꼼하지만 느림)
      stride=2 → 두 글자씩 건너뛰기 (빠르지만 놓칠 수 있음)
    """
    print("=" * 70)
    print("[레슨 2] 스트라이드 (Stride)")
    print("=" * 70)
    print()

    image = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16],
    ]
    kernel = [
        [1, 0],
        [0, 1],
    ]

    print_matrix(image, "입력 (4×4):")
    print_matrix(kernel, "필터 (2×2):")

    for stride in [1, 2]:
        k_h, k_w = len(kernel), len(kernel[0])
        out_h = (len(image) - k_h) // stride + 1
        out_w = (len(image[0]) - k_w) // stride + 1

        result = []
        for i in range(out_h):
            row = []
            for j in range(out_w):
                total = 0.0
                for ki in range(k_h):
                    for kj in range(k_w):
                        total += image[i*stride + ki][j*stride + kj] * kernel[ki][kj]
                row.append(total)
            result.append(row)

        print(f"  stride={stride}일 때 출력 ({out_h}×{out_w}):")
        for row in result:
            print("    [" + ", ".join(f"{v:>5.0f}" for v in row) + "]")
        print()

    print("  → stride가 클수록 출력이 작아짐 (정보를 압축)")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 3: 패딩 (Padding)
# ─────────────────────────────────────────────────────────────────────────

def lesson3_padding():
    """
    패딩: 입력 가장자리에 0을 덧대어 출력 크기를 유지합니다.

    비유: 사진 테두리에 흰 여백을 붙이는 것.
          돋보기가 모서리까지 도달할 수 있게 여유 공간을 만듦.
    """
    print("=" * 70)
    print("[레슨 3] 패딩 (Padding)")
    print("=" * 70)
    print()

    image = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]

    print_matrix(image, "원본 입력 (3×3):")

    # padding=1 적용
    pad = 1
    h, w = len(image), len(image[0])
    padded = [[0.0] * (w + 2*pad) for _ in range(h + 2*pad)]
    for i in range(h):
        for j in range(w):
            padded[i + pad][j + pad] = image[i][j]

    print_matrix(padded, "패딩 적용 후 (5×5, 가장자리에 0 추가):")

    # 3x3 필터로 합성곱 → 출력이 3x3 (원본 크기 유지!)
    kernel = [
        [0, 1, 0],
        [1, -4, 1],
        [0, 1, 0],
    ]
    k_h, k_w = 3, 3
    out_h = len(padded) - k_h + 1
    out_w = len(padded[0]) - k_w + 1

    result = []
    for i in range(out_h):
        row = []
        for j in range(out_w):
            total = 0.0
            for ki in range(k_h):
                for kj in range(k_w):
                    total += padded[i+ki][j+kj] * kernel[ki][kj]
            row.append(total)
        result.append(row)

    print_matrix(kernel, "필터 (3×3, 라플라시안 에지 감지):")
    print_matrix(result, f"합성곱 결과 ({out_h}×{out_w} → 원본 크기 유지!):")
    print("  → 패딩 덕분에 입력과 출력의 크기가 같습니다.")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 4: 풀링 (Pooling)
# ─────────────────────────────────────────────────────────────────────────

def lesson4_pooling():
    """
    풀링: 특성맵을 축소하여 중요한 정보만 남깁니다.

    비유: 사진을 축소(썸네일 만들기)하되, 가장 두드러진 부분을 유지.
          맥스 풀링 = 영역에서 가장 눈에 띄는 값만 남기기
          평균 풀링 = 영역의 평균을 남기기
    """
    print("=" * 70)
    print("[레슨 4] 풀링 (Pooling)")
    print("=" * 70)
    print()

    feature_map = [
        [1, 3, 2, 4],
        [5, 6, 7, 8],
        [3, 2, 1, 0],
        [1, 4, 3, 2],
    ]

    print_matrix(feature_map, "특성맵 (4×4):")

    pool_size = 2
    out_h = len(feature_map) // pool_size
    out_w = len(feature_map[0]) // pool_size

    # 맥스 풀링
    max_pool = []
    for i in range(out_h):
        row = []
        for j in range(out_w):
            vals = []
            for pi in range(pool_size):
                for pj in range(pool_size):
                    vals.append(feature_map[i*pool_size+pi][j*pool_size+pj])
            row.append(max(vals))
        max_pool.append(row)

    # 평균 풀링
    avg_pool = []
    for i in range(out_h):
        row = []
        for j in range(out_w):
            vals = []
            for pi in range(pool_size):
                for pj in range(pool_size):
                    vals.append(feature_map[i*pool_size+pi][j*pool_size+pj])
            row.append(sum(vals) / len(vals))
        avg_pool.append(row)

    print(f"  2×2 맥스 풀링 결과:")
    print(f"    영역 [1,3,5,6] → max = 6    영역 [2,4,7,8] → max = 8")
    print(f"    영역 [3,2,1,4] → max = 4    영역 [1,0,3,2] → max = 3")
    print_matrix(max_pool, "  맥스 풀링 결과:")
    print_matrix(avg_pool, "  평균 풀링 결과:")
    print("  → 풀링은 크기를 줄이면서 핵심 특징을 유지합니다.")
    print("  → 맥스 풀링: 가장 강한 신호 유지 (가장 많이 사용)")
    print("  → 평균 풀링: 전체적인 분위기 유지")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 5: 전체 CNN 파이프라인 시뮬레이션
# ─────────────────────────────────────────────────────────────────────────

def lesson5_cnn_pipeline():
    """
    실제 CNN의 흐름: 입력 → 합성곱 → 활성화 → 풀링 → 분류

    비유: 사진 분석 과정
      1. 사진을 받음 (입력)
      2. 돋보기로 특징 찾기 (합성곱)
      3. 중요한 것만 강조 (ReLU)
      4. 사진 축소 (풀링)
      5. 특징을 보고 판단 (분류)
    """
    print("=" * 70)
    print("[레슨 5] CNN 전체 파이프라인")
    print("=" * 70)
    print()
    print("  입력(6×6) → 합성곱(3×3필터) → ReLU → 맥스풀링(2×2) → 분류")
    print()

    # 6x6 입력 (간단한 'L' 모양)
    image = [
        [0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
        [0, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ]

    kernel = [
        [1, 0, -1],
        [1, 0, -1],
        [1, 0, -1],
    ]

    print_matrix(image, "1단계 - 입력 이미지 (L 모양):")
    print_matrix(kernel, "필터 (세로선 감지):")

    # 합성곱
    k_h, k_w = 3, 3
    out_h = len(image) - k_h + 1
    out_w = len(image[0]) - k_w + 1

    conv_out = []
    for i in range(out_h):
        row = []
        for j in range(out_w):
            total = 0.0
            for ki in range(k_h):
                for kj in range(k_w):
                    total += image[i+ki][j+kj] * kernel[ki][kj]
            row.append(total)
        conv_out.append(row)

    print_matrix(conv_out, "2단계 - 합성곱 결과:")

    # ReLU
    relu_out = []
    for row in conv_out:
        relu_out.append([max(0, v) for v in row])

    print_matrix(relu_out, "3단계 - ReLU 후 (음수→0):")

    # 맥스 풀링 2x2
    pool_h = len(relu_out) // 2
    pool_w = len(relu_out[0]) // 2
    pool_out = []
    for i in range(pool_h):
        row = []
        for j in range(pool_w):
            vals = [
                relu_out[i*2][j*2], relu_out[i*2][j*2+1],
                relu_out[i*2+1][j*2], relu_out[i*2+1][j*2+1]
            ]
            row.append(max(vals))
        pool_out.append(row)

    print_matrix(pool_out, "4단계 - 맥스풀링 결과:")

    # Flatten → 간단한 분류
    flat = []
    for row in pool_out:
        flat.extend(row)

    print(f"    5단계 - Flatten: {flat}")
    print(f"    → 이 숫자들을 일반 신경망에 넣어 'L이다/아니다'를 판단합니다.")
    print()
    print("  CNN 핵심 정리:")
    print("    합성곱 = 특징 추출 (돋보기로 패턴 찾기)")
    print("    풀링 = 정보 압축 (중요한 것만 남기기)")
    print("    층을 깊게 쌓으면 → 단순 특징 → 복잡한 특징을 점점 발견")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■" * 72)
    print("  딥러닝 07단계 : CNN 기초 (합성곱 신경망)")
    print("  비유: 돋보기로 사진을 훑으며 특징을 찾아내기")
    print("■" * 72)
    print()

    lesson1_convolution_concept()
    lesson2_stride()
    lesson3_padding()
    lesson4_pooling()
    lesson5_cnn_pipeline()


if __name__ == "__main__":
    main()
