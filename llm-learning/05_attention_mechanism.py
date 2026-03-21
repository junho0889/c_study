# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#   LLM 학습 05단계: 어텐션 메커니즘 (Attention Mechanism)
#   ─ 문장에서 중요한 단어에 집중하는 방법 ─
#
#   비유: 교실에서 집중하기
#     선생님이 긴 설명을 하는데, 학생은 모든 말에 똑같이
#     집중하지 않습니다. "시험에 나온다"는 부분에 귀가 쫑긋!
#     어텐션도 마찬가지로, 각 단어가 다른 단어에
#     얼마나 "집중"해야 하는지 점수를 매깁니다.
#
#   실행 방법:
#     python 05_attention_mechanism.py
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math


# ─────────────────────────────────────────────────────────────────────────
# ■ 도우미 함수
# ─────────────────────────────────────────────────────────────────────────

def softmax(values):
    """소프트맥스: 숫자 리스트를 합이 1인 확률로 변환"""
    max_v = max(values)
    exps = [math.exp(v - max_v) for v in values]  # overflow 방지
    total = sum(exps)
    return [e / total for e in exps]


def dot_product(a, b):
    return sum(x * y for x, y in zip(a, b))


def mat_vec_mul(matrix, vector):
    """행렬 × 벡터"""
    return [dot_product(row, vector) for row in matrix]


def vec_add(a, b):
    return [x + y for x, y in zip(a, b)]


def vec_scale(v, s):
    return [x * s for x in v]


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 1: 셀프 어텐션 개념
# ─────────────────────────────────────────────────────────────────────────

def lesson1_self_attention_concept():
    """
    셀프 어텐션: 문장 안에서 각 단어가 다른 모든 단어에 대해
    "얼마나 관련 있는지" 점수를 매기는 것.

    비유: 수업 중 노트 필기
      "고양이가 매트 위에서 잤다"
      '잤다'라는 단어를 이해하려면 '고양이가'에 주목해야 함.
      '위에서'보다 '고양이가'에 더 높은 점수를 줌.
    """
    print("=" * 70)
    print("[레슨 1] 셀프 어텐션 개념")
    print("=" * 70)
    print()
    print("  문장: '고양이가 매트 위에서 잤다'")
    print()
    print("  '잤다'에서 다른 단어들을 바라봤을 때:")
    print("    고양이가 → 높은 집중 (누가 잤는지 중요!)")
    print("    매트     → 중간 집중 (어디서?)")
    print("    위에서   → 낮은 집중 (부가 정보)")
    print("    잤다     → 자기 자신도 약간 참고")
    print()

    # 간단한 유사도 계산
    words = ["고양이가", "매트", "위에서", "잤다"]
    # 임의의 단어 벡터 (2차원으로 단순화)
    embeddings = {
        "고양이가": [0.9, 0.1],
        "매트":     [0.2, 0.8],
        "위에서":   [0.3, 0.7],
        "잤다":     [0.8, 0.3],
    }

    print("  단어 벡터 (2차원 장난감):")
    for word, vec in embeddings.items():
        print(f"    {word}: {vec}")
    print()

    # '잤다'와 각 단어의 유사도 (내적)
    query = embeddings["잤다"]
    scores = []
    for w in words:
        score = dot_product(query, embeddings[w])
        scores.append(score)

    attention_weights = softmax(scores)

    print("  '잤다'가 각 단어에 주는 어텐션 점수:")
    for w, score, weight in zip(words, scores, attention_weights):
        bar = "#" * int(weight * 40)
        print(f"    {w:>6s}: 내적={score:.2f}, 가중치={weight:.3f} {bar}")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 2: Query, Key, Value
# ─────────────────────────────────────────────────────────────────────────

def lesson2_query_key_value():
    """
    Q, K, V는 어텐션의 세 가지 역할입니다.

    비유: 도서관 검색
      Query(Q) = 내가 찾고 싶은 것 ("고양이 관련 책")
      Key(K)   = 각 책의 제목/태그 ("동물", "요리", "고양이 키우기")
      Value(V) = 책의 실제 내용

      Q와 K를 비교해서 관련성을 구하고,
      그 관련성에 따라 V(내용)를 가중 합산합니다.
    """
    print("=" * 70)
    print("[레슨 2] Query, Key, Value")
    print("=" * 70)
    print()
    print("  비유: 도서관 검색")
    print("    Q = 찾고 싶은 것 (질문)")
    print("    K = 각 항목의 태그 (키워드)")
    print("    V = 실제 내용 (답)")
    print()
    print("  어텐션 공식:")
    print("    score = Q · K^T / sqrt(d_k)")
    print("    weight = softmax(score)")
    print("    output = weight × V")
    print()

    # 3개 토큰, 임베딩 차원 = 4
    # 입력 임베딩
    tokens = ["나는", "학생", "이다"]
    X = [
        [1.0, 0.0, 1.0, 0.0],  # 나는
        [0.0, 1.0, 0.0, 1.0],  # 학생
        [0.5, 0.5, 0.5, 0.5],  # 이다
    ]

    # Q, K, V 변환 행렬 (간단한 가중치)
    # 실제로는 학습되지만 여기서는 고정값
    W_q = [[1, 0], [0, 1], [1, 0], [0, 1]]  # 4×2
    W_k = [[0, 1], [1, 0], [0, 1], [1, 0]]  # 4×2
    W_v = [[1, 1], [0, 0], [1, 0], [0, 1]]  # 4×2

    # Q, K, V 계산
    Q = [mat_vec_mul(list(zip(*W_q)), x) for x in X]  # transpose trick
    K = [mat_vec_mul(list(zip(*W_k)), x) for x in X]
    V = [mat_vec_mul(list(zip(*W_v)), x) for x in X]

    # 간단한 행렬곱 (전치를 직접)
    d_k = len(Q[0])  # 키 차원
    scale = math.sqrt(d_k)

    print(f"  토큰: {tokens}")
    print(f"  Q (질문):")
    for i, q in enumerate(Q):
        print(f"    {tokens[i]}: [{', '.join(f'{v:.1f}' for v in q)}]")
    print(f"  K (키):")
    for i, k in enumerate(K):
        print(f"    {tokens[i]}: [{', '.join(f'{v:.1f}' for v in k)}]")
    print(f"  V (값):")
    for i, v in enumerate(V):
        print(f"    {tokens[i]}: [{', '.join(f'{v:.1f}' for v in v)}]")
    print()

    # 어텐션 스코어 계산
    print("  어텐션 스코어 (Q·K^T / sqrt(d_k)):")
    print(f"  scale = sqrt({d_k}) = {scale:.2f}")
    print()

    for i, q in enumerate(Q):
        scores = [dot_product(q, k) / scale for k in K]
        weights = softmax(scores)

        print(f"  '{tokens[i]}'의 어텐션:")
        for j, (s, w) in enumerate(zip(scores, weights)):
            bar = "#" * int(w * 30)
            print(f"    → {tokens[j]:>4s}: score={s:.2f}, weight={w:.3f} {bar}")

        # 가중 합으로 출력 계산
        output = [0.0] * len(V[0])
        for j, w in enumerate(weights):
            output = vec_add(output, vec_scale(V[j], w))
        print(f"    출력: [{', '.join(f'{v:.3f}' for v in output)}]")
        print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 3: 멀티헤드 어텐션
# ─────────────────────────────────────────────────────────────────────────

def lesson3_multi_head_attention():
    """
    멀티헤드: 여러 개의 어텐션을 동시에 수행합니다.

    비유: 교실에서 여러 관점으로 동시에 집중하기
      헤드1: 문법 관계에 집중 ("주어-동사 관계는?")
      헤드2: 의미 관계에 집중 ("비슷한 의미의 단어는?")
      헤드3: 위치 관계에 집중 ("가까운 단어끼리 관련?")

      각 헤드가 다른 관점을 보고, 결과를 합칩니다.
    """
    print("=" * 70)
    print("[레슨 3] 멀티헤드 어텐션")
    print("=" * 70)
    print()
    print("  하나의 어텐션 = 하나의 관점")
    print("  멀티헤드 = 여러 관점을 동시에 보기")
    print()

    tokens = ["나는", "빨간", "사과를", "먹었다"]
    n = len(tokens)

    # 2개의 헤드 시뮬레이션
    # 헤드1: 주어-동사 관계 (나는-먹었다 높음)
    head1_weights = [
        [0.1, 0.1, 0.2, 0.6],  # 나는 → 먹었다에 집중
        [0.2, 0.3, 0.4, 0.1],  # 빨간 → 사과를에 집중
        [0.1, 0.5, 0.2, 0.2],  # 사과를 → 빨간에 집중
        [0.6, 0.1, 0.2, 0.1],  # 먹었다 → 나는에 집중
    ]

    # 헤드2: 수식 관계 (빨간-사과를 높음)
    head2_weights = [
        [0.4, 0.2, 0.2, 0.2],  # 나는 → 자기 자신
        [0.1, 0.2, 0.6, 0.1],  # 빨간 → 사과를에 집중
        [0.1, 0.6, 0.2, 0.1],  # 사과를 → 빨간에 집중
        [0.1, 0.1, 0.5, 0.3],  # 먹었다 → 사과를에 집중
    ]

    print("  헤드 1 (주어-동사 관계):")
    for i in range(n):
        bars = ""
        for j in range(n):
            w = head1_weights[i][j]
            bars += f"{tokens[j]}({w:.1f}) "
        print(f"    {tokens[i]:>6s} → {bars}")
    print()

    print("  헤드 2 (수식 관계):")
    for i in range(n):
        bars = ""
        for j in range(n):
            w = head2_weights[i][j]
            bars += f"{tokens[j]}({w:.1f}) "
        print(f"    {tokens[i]:>6s} → {bars}")
    print()

    print("  → 각 헤드가 다른 관계를 포착합니다!")
    print("  → 결과를 합쳐서(concat) 더 풍부한 표현을 만듦")
    print("  → 실제 GPT-3는 96개 헤드를 사용합니다!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 4: 위치 인코딩 (Positional Encoding)
# ─────────────────────────────────────────────────────────────────────────

def lesson4_positional_encoding():
    """
    트랜스포머는 RNN과 달리 순서 개념이 없습니다.
    위치 인코딩을 더해서 "몇 번째 단어인지"를 알려줍니다.

    비유: 학생들의 좌석 번호표
      교실에 들어온 순서가 중요한데,
      트랜스포머는 모두 동시에 들어오니 순서를 모름.
      그래서 각 학생에게 번호표(위치 인코딩)를 붙여줌.
    """
    print("=" * 70)
    print("[레슨 4] 위치 인코딩 (Positional Encoding)")
    print("=" * 70)
    print()
    print("  공식: PE(pos, 2i)   = sin(pos / 10000^(2i/d))")
    print("        PE(pos, 2i+1) = cos(pos / 10000^(2i/d))")
    print()

    seq_len = 6
    d_model = 8  # 임베딩 차원

    print(f"  시퀀스 길이={seq_len}, 차원={d_model}")
    print()

    # 위치 인코딩 계산
    pe = []
    for pos in range(seq_len):
        row = []
        for i in range(d_model):
            if i % 2 == 0:
                val = math.sin(pos / (10000 ** (i / d_model)))
            else:
                val = math.cos(pos / (10000 ** ((i - 1) / d_model)))
            row.append(val)
        pe.append(row)

    print("  위치별 인코딩 값 (처음 6차원):")
    print("  ┌──────┬" + "─" * 55 + "┐")
    print("  │ 위치 │ " + "   ".join(f"d{i}" for i in range(6)) + "          │")
    print("  ├──────┼" + "─" * 55 + "┤")
    for pos in range(seq_len):
        vals = "  ".join(f"{pe[pos][i]:>+.2f}" for i in range(6))
        print(f"  │  {pos}   │ {vals}       │")
    print("  └──────┴" + "─" * 55 + "┘")
    print()

    # 위치 간 유사도
    print("  위치 간 내적 유사도 (가까운 위치일수록 비슷):")
    for i in range(4):
        for j in range(i + 1, min(i + 3, seq_len)):
            sim = dot_product(pe[i], pe[j])
            print(f"    위치{i} · 위치{j} = {sim:.3f}")
    print()
    print("  → 가까운 위치일수록 유사도가 높고, 먼 위치는 낮음")
    print("  → 이렇게 순서 정보를 임베딩에 더해줍니다")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 5: 전체 어텐션 계산 수치 예제
# ─────────────────────────────────────────────────────────────────────────

def lesson5_full_attention_example():
    """
    3개 토큰에 대한 셀프 어텐션을 처음부터 끝까지 수치로 따라갑니다.
    """
    print("=" * 70)
    print("[레슨 5] 셀프 어텐션 전체 수치 예제")
    print("=" * 70)
    print()

    # 입력: 3개 토큰, 각 4차원
    tokens = ["I", "love", "AI"]
    X = [
        [1.0, 0.5, 0.0, 0.2],
        [0.3, 1.0, 0.7, 0.1],
        [0.8, 0.2, 1.0, 0.6],
    ]

    d_k = 2  # key/query 차원

    # 간단한 Q, K, V 행렬 (4→2 변환)
    W_q = [[0.5, 0.3], [0.2, 0.7], [0.1, 0.4], [0.6, 0.2]]
    W_k = [[0.3, 0.6], [0.7, 0.1], [0.4, 0.3], [0.2, 0.5]]
    W_v = [[0.8, 0.1], [0.3, 0.6], [0.5, 0.4], [0.1, 0.9]]

    print("  Step 1: Q, K, V 계산 (입력 × 가중치)")
    Q, K, V = [], [], []
    for i, x in enumerate(X):
        q = [sum(x[j] * W_q[j][k] for j in range(4)) for k in range(d_k)]
        k = [sum(x[j] * W_k[j][k] for j in range(4)) for k in range(d_k)]
        v = [sum(x[j] * W_v[j][k] for j in range(4)) for k in range(d_k)]
        Q.append(q)
        K.append(k)
        V.append(v)
        print(f"    {tokens[i]:>4s}: Q=[{q[0]:.3f},{q[1]:.3f}] "
              f"K=[{k[0]:.3f},{k[1]:.3f}] V=[{v[0]:.3f},{v[1]:.3f}]")
    print()

    scale = math.sqrt(d_k)
    print(f"  Step 2: 어텐션 스코어 계산 (Q·K^T / sqrt({d_k})={scale:.2f})")
    print()

    all_outputs = []
    for i in range(3):
        scores = [dot_product(Q[i], K[j]) / scale for j in range(3)]
        weights = softmax(scores)

        print(f"    '{tokens[i]}':")
        print(f"      raw scores: [{', '.join(f'{s:.3f}' for s in scores)}]")
        print(f"      softmax:    [{', '.join(f'{w:.3f}' for w in weights)}]")

        # 가중합
        output = [0.0, 0.0]
        for j in range(3):
            output[0] += weights[j] * V[j][0]
            output[1] += weights[j] * V[j][1]

        all_outputs.append(output)
        print(f"      출력:       [{output[0]:.3f}, {output[1]:.3f}]")
        print()

    print("  → 각 토큰이 다른 토큰들의 Value를 집중도에 따라 합산!")
    print("  → 이것이 트랜스포머의 핵심 연산입니다.")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■" * 72)
    print("  LLM 05단계 : 어텐션 메커니즘 (Attention Mechanism)")
    print("  비유: 수업 중 중요한 부분에 집중하기")
    print("■" * 72)
    print()

    lesson1_self_attention_concept()
    lesson2_query_key_value()
    lesson3_multi_head_attention()
    lesson4_positional_encoding()
    lesson5_full_attention_example()


if __name__ == "__main__":
    main()
