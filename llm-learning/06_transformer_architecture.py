# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#   LLM 학습 06단계: 트랜스포머 아키텍처
#   ─ 현대 AI의 핵심 구조를 분해해서 이해하기 ─
#
#   비유: 번역 조립 라인
#     자동차 공장처럼 여러 작업 단계를 거칩니다.
#     1. 어텐션으로 단어 관계 파악 (부품 검사)
#     2. 피드포워드로 특징 강화 (부품 가공)
#     3. 잔차 연결로 원래 정보 유지 (원본 보존)
#     4. 레이어 정규화로 안정화 (품질 관리)
#     이 과정을 여러 층 쌓아서 복잡한 언어를 이해합니다.
#
#   실행 방법:
#     python 06_transformer_architecture.py
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math


# ─────────────────────────────────────────────────────────────────────────
# ■ 도우미 함수
# ─────────────────────────────────────────────────────────────────────────

def softmax(values):
    max_v = max(values)
    exps = [math.exp(v - max_v) for v in values]
    total = sum(exps)
    return [e / total for e in exps]


def dot_product(a, b):
    return sum(x * y for x, y in zip(a, b))


def relu(x):
    return max(0.0, x)


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 1: 인코더-디코더 구조
# ─────────────────────────────────────────────────────────────────────────

def lesson1_encoder_decoder():
    """
    트랜스포머의 큰 그림: 인코더와 디코더.

    비유: 통역사 2명이 일하는 방식
      인코더(이해 담당): 한국어를 듣고 핵심 의미를 메모
      디코더(생성 담당): 메모를 보고 영어로 한 단어씩 말함

    GPT계열: 디코더만 사용 (다음 단어 예측에 집중)
    BERT계열: 인코더만 사용 (문장 이해에 집중)
    원조 트랜스포머: 인코더+디코더 (번역에 사용)
    """
    print("=" * 70)
    print("[레슨 1] 인코더-디코더 구조")
    print("=" * 70)
    print()
    print("  트랜스포머 전체 구조:")
    print()
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │                 트랜스포머                      │")
    print("  │                                                 │")
    print("  │  ┌──────────────┐    ┌──────────────┐          │")
    print("  │  │   인코더     │    │   디코더     │          │")
    print("  │  │              │    │              │          │")
    print("  │  │ 셀프어텐션   │───→│ 크로스어텐션 │          │")
    print("  │  │ ↓            │    │ ↓            │          │")
    print("  │  │ 피드포워드   │    │ 피드포워드   │          │")
    print("  │  │ (×N층)       │    │ (×N층)       │          │")
    print("  │  └──────────────┘    └──────────────┘          │")
    print("  │       ↑                    ↑     ↓             │")
    print("  │    입력 문장           이전 출력  다음 단어     │")
    print("  └─────────────────────────────────────────────────┘")
    print()
    print("  모델별 사용 구조:")
    print("  ┌──────────┬────────────────┬─────────────────────┐")
    print("  │  모델    │  사용 구조     │  대표 용도          │")
    print("  ├──────────┼────────────────┼─────────────────────┤")
    print("  │ BERT     │ 인코더만       │ 문장 이해, 분류     │")
    print("  │ GPT      │ 디코더만       │ 텍스트 생성         │")
    print("  │ T5, BART │ 인코더+디코더  │ 번역, 요약          │")
    print("  └──────────┴────────────────┴─────────────────────┘")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 2: 레이어 정규화 (Layer Normalization)
# ─────────────────────────────────────────────────────────────────────────

def lesson2_layer_normalization():
    """
    레이어 정규화: 각 토큰의 벡터 값들을 평균=0, 분산=1로 정리합니다.

    비유: 학생들 점수를 상대 평가로 변환하는 것
      국어 90, 수학 30이면 차이가 너무 큼.
      정규화하면 둘 다 비슷한 범위가 되어 비교가 쉬움.
    """
    print("=" * 70)
    print("[레슨 2] 레이어 정규화 (Layer Normalization)")
    print("=" * 70)
    print()

    # 한 토큰의 벡터
    x = [2.0, 4.0, 6.0, 8.0]
    print(f"  입력 벡터: {x}")

    # 평균 계산
    mean = sum(x) / len(x)
    print(f"  평균: {mean}")

    # 분산 계산
    variance = sum((xi - mean) ** 2 for xi in x) / len(x)
    std = math.sqrt(variance + 1e-6)  # 0으로 나누기 방지
    print(f"  분산: {variance}")
    print(f"  표준편차: {std:.4f}")

    # 정규화
    normalized = [(xi - mean) / std for xi in x]
    print(f"  정규화 후: [{', '.join(f'{v:.4f}' for v in normalized)}]")

    # 스케일과 시프트 (감마, 베타) - 학습 파라미터
    gamma = [1.0, 1.0, 1.0, 1.0]  # 스케일
    beta = [0.0, 0.0, 0.0, 0.0]   # 시프트
    output = [g * n + b for g, n, b in zip(gamma, beta, normalized)]
    print(f"  감마×정규화+베타: [{', '.join(f'{v:.4f}' for v in output)}]")
    print()

    # 검증
    new_mean = sum(normalized) / len(normalized)
    new_var = sum((v - new_mean)**2 for v in normalized) / len(normalized)
    print(f"  정규화 후 평균: {new_mean:.6f} (~= 0)")
    print(f"  정규화 후 분산: {new_var:.6f} (~= 1)")
    print()
    print("  → 값의 범위가 안정적이어서 학습이 잘 됩니다!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 3: 피드포워드 네트워크 (FFN)
# ─────────────────────────────────────────────────────────────────────────

def lesson3_feed_forward_network():
    """
    트랜스포머 블록 안의 피드포워드 네트워크.
    어텐션이 "관계"를 봤다면, FFN은 "특징을 강화"합니다.

    비유: 어텐션이 "이 단어들이 관련있다"고 찾았으면,
          FFN은 그 관계를 더 뚜렷하게 만드는 형광펜 역할.

    구조: Linear → ReLU → Linear
    차원: d_model → d_ff → d_model
    보통 d_ff = 4 × d_model
    """
    print("=" * 70)
    print("[레슨 3] 피드포워드 네트워크 (FFN)")
    print("=" * 70)
    print()
    print("  FFN(x) = W2 × ReLU(W1 × x + b1) + b2")
    print("  차원 변화: d_model → 4×d_model → d_model")
    print()

    # d_model=3, d_ff=6 으로 단순화
    x = [0.5, -0.3, 0.8]
    d_model = 3
    d_ff = 6

    # W1: 3→6
    W1 = [[0.2, -0.1, 0.3], [0.5, 0.4, -0.2], [-0.3, 0.6, 0.1],
           [0.1, -0.5, 0.4], [0.7, 0.2, 0.3], [-0.4, 0.1, 0.5]]
    b1 = [0.1, 0.0, -0.1, 0.1, 0.0, -0.1]

    # W2: 6→3
    W2 = [[0.3, -0.2, 0.1, 0.4, 0.5, -0.1],
           [-0.1, 0.3, 0.5, -0.2, 0.1, 0.4],
           [0.2, 0.1, -0.3, 0.3, 0.2, 0.1]]
    b2 = [0.0, 0.0, 0.0]

    print(f"  입력: {x}")

    # 1단계: W1 × x + b1
    hidden = []
    for i in range(d_ff):
        val = sum(W1[i][j] * x[j] for j in range(d_model)) + b1[i]
        hidden.append(val)
    print(f"  W1×x + b1: [{', '.join(f'{v:.3f}' for v in hidden)}]")

    # 2단계: ReLU
    hidden_relu = [relu(v) for v in hidden]
    print(f"  ReLU 후:   [{', '.join(f'{v:.3f}' for v in hidden_relu)}]")

    # 3단계: W2 × hidden + b2
    output = []
    for i in range(d_model):
        val = sum(W2[i][j] * hidden_relu[j] for j in range(d_ff)) + b2[i]
        output.append(val)
    print(f"  W2×h + b2: [{', '.join(f'{v:.3f}' for v in output)}]")
    print()
    print("  → 차원을 확장했다가 다시 줄이면서 비선형 특징을 학습!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 4: 잔차 연결 (Residual Connection)
# ─────────────────────────────────────────────────────────────────────────

def lesson4_residual_connection():
    """
    잔차 연결: 입력을 건너뛰어서 출력에 더합니다.
    output = LayerNorm(x + SubLayer(x))

    비유: 시험 답안 작성할 때 연습장 내용(x)을 베껴 쓰고,
          추가 계산 결과(SubLayer)를 덧붙이는 것.
          원래 답(x)을 잃지 않으면서 보강합니다.

    왜 필요한가?
      - 층이 깊어지면 학습이 어려워짐 (기울기 소실)
      - 잔차 연결이 "지름길"을 만들어 기울기가 잘 흐르게 함
    """
    print("=" * 70)
    print("[레슨 4] 잔차 연결 (Residual Connection)")
    print("=" * 70)
    print()
    print("  공식: output = LayerNorm(x + SubLayer(x))")
    print()
    print("  비유: 원본 + 보강 = 최종 결과")
    print()

    # 수치 예제
    x = [1.0, 2.0, 3.0, 4.0]
    sublayer_output = [0.1, -0.3, 0.5, -0.2]  # 어텐션 또는 FFN의 출력

    print(f"  x (원래 입력):      {x}")
    print(f"  SubLayer(x) 출력:   {sublayer_output}")

    # 잔차 연결: x + SubLayer(x)
    residual = [a + b for a, b in zip(x, sublayer_output)]
    print(f"  x + SubLayer(x):    {residual}")

    # 레이어 정규화
    mean = sum(residual) / len(residual)
    variance = sum((v - mean)**2 for v in residual) / len(residual)
    std = math.sqrt(variance + 1e-6)
    normalized = [(v - mean) / std for v in residual]
    print(f"  LayerNorm 후:       [{', '.join(f'{v:.3f}' for v in normalized)}]")
    print()

    # 잔차 연결이 없다면?
    print("  잔차 연결이 없으면:")
    print("    10층을 지나면 원래 입력 정보가 거의 사라짐")
    print("  잔차 연결이 있으면:")
    print("    원래 입력이 지름길로 전달되어 정보가 보존됨")
    print()

    # 깊은 층에서의 효과 시뮬레이션
    print("  10층을 거칠 때 정보 보존율:")
    val_no_res = 1.0
    val_with_res = 1.0

    for layer in range(10):
        val_no_res *= 0.8       # 매 층에서 20% 정보 손실
        val_with_res = val_with_res + val_with_res * 0.1  # 잔차로 보존

    print(f"    잔차 연결 없이: {val_no_res:.4f} (정보 많이 잃음)")
    print(f"    잔차 연결 있으면: 원본이 항상 더해지므로 핵심 보존")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 5: 전체 트랜스포머 블록 시뮬레이션
# ─────────────────────────────────────────────────────────────────────────

def lesson5_full_transformer_block():
    """
    하나의 트랜스포머 블록 전체 과정:
      입력 → 멀티헤드 어텐션 → 잔차+정규화 → FFN → 잔차+정규화 → 출력
    """
    print("=" * 70)
    print("[레슨 5] 전체 트랜스포머 블록 시뮬레이션")
    print("=" * 70)
    print()
    print("  한 블록의 흐름:")
    print("  ┌──────────────────────────────────────┐")
    print("  │  입력 x                              │")
    print("  │    ↓                                  │")
    print("  │  [멀티헤드 셀프 어텐션] ──── + x     │")
    print("  │    ↓                                  │")
    print("  │  [레이어 정규화]                      │")
    print("  │    ↓                                  │")
    print("  │  [피드포워드 네트워크] ──── + 위 결과 │")
    print("  │    ↓                                  │")
    print("  │  [레이어 정규화]                      │")
    print("  │    ↓                                  │")
    print("  │  출력 (다음 블록으로)                 │")
    print("  └──────────────────────────────────────┘")
    print()

    # 간단한 수치 시뮬레이션 (1개 토큰, 4차원)
    x = [0.5, 1.2, -0.3, 0.8]
    print(f"  입력: {x}")

    # Step 1: 어텐션 (단순화: 자기 자신에 대한 가중합)
    attn_output = [v * 0.9 + 0.1 for v in x]  # 단순화된 어텐션
    print(f"  1. 어텐션 출력: [{', '.join(f'{v:.3f}' for v in attn_output)}]")

    # Step 2: 잔차 연결
    res1 = [a + b for a, b in zip(x, attn_output)]
    print(f"  2. 잔차 연결 (x + attn): [{', '.join(f'{v:.3f}' for v in res1)}]")

    # Step 3: 레이어 정규화
    mean1 = sum(res1) / len(res1)
    var1 = sum((v - mean1)**2 for v in res1) / len(res1)
    std1 = math.sqrt(var1 + 1e-6)
    norm1 = [(v - mean1) / std1 for v in res1]
    print(f"  3. 정규화: [{', '.join(f'{v:.3f}' for v in norm1)}]")

    # Step 4: FFN (단순화: 확장→ReLU→축소)
    ffn_output = [relu(v * 2.0 + 0.1) * 0.5 for v in norm1]
    print(f"  4. FFN 출력: [{', '.join(f'{v:.3f}' for v in ffn_output)}]")

    # Step 5: 두 번째 잔차 연결
    res2 = [a + b for a, b in zip(norm1, ffn_output)]
    print(f"  5. 잔차 연결: [{', '.join(f'{v:.3f}' for v in res2)}]")

    # Step 6: 두 번째 레이어 정규화
    mean2 = sum(res2) / len(res2)
    var2 = sum((v - mean2)**2 for v in res2) / len(res2)
    std2 = math.sqrt(var2 + 1e-6)
    norm2 = [(v - mean2) / std2 for v in res2]
    print(f"  6. 최종 출력: [{', '.join(f'{v:.3f}' for v in norm2)}]")
    print()

    print("  실제 트랜스포머:")
    print("    GPT-3: 이 블록을 96번 반복, 차원 12288, 헤드 96개")
    print("    GPT-4: 더 크고 복잡 (정확한 구조는 비공개)")
    print("    이 단순한 블록을 깊게 쌓는 것이 핵심!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■" * 72)
    print("  LLM 06단계 : 트랜스포머 아키텍처")
    print("  비유: 번역 조립 라인 (어텐션→정규화→FFN→잔차)")
    print("■" * 72)
    print()

    lesson1_encoder_decoder()
    lesson2_layer_normalization()
    lesson3_feed_forward_network()
    lesson4_residual_connection()
    lesson5_full_transformer_block()


if __name__ == "__main__":
    main()
