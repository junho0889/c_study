# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   TensorFlow/Keras 학습 08단계: RNN과 텍스트 처리
#   ─ 시퀀스 데이터, SimpleRNN, LSTM, GRU, Embedding, Bidirectional ─
#   ■ 실행 방법: python 08_rnn_text.py (개념 학습용 코드, TF 없이 실행 가능)
#   ■ TensorFlow 설치: pip install tensorflow
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import random

random.seed(42)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. 시퀀스 데이터와 RNN의 필요성
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("1. 시퀀스 데이터와 RNN의 필요성")
print("=" * 70)

print("""
■ 시퀀스 데이터란?
  순서가 중요한 데이터!
  - 텍스트: "나는 행복하다" (단어 순서가 의미를 결정)
  - 시계열: 주가, 온도, 심박수 (과거가 미래에 영향)
  - 음성: 소리의 파형 (시간 순서대로)
  - DNA: ATCGATCG... (염기 서열)

■ 왜 Dense/CNN으로는 부족한가?
  Dense: 순서 정보 없음! "나는 행복하다" = "행복하다 나는" (동일 취급)
  CNN: 지역적 패턴만 감지 (전체 문맥 파악 어려움)
  RNN: 순서대로 하나씩 읽으며 "기억"을 축적!

  비유: 소설 읽기!
  Dense = 단어를 무작위로 섞어 읽기
  RNN   = 처음부터 끝까지 순서대로 읽기 (줄거리 파악 가능!)
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. SimpleRNN 레이어
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("2. SimpleRNN - 기본 순환 신경망")
print("=" * 70)

print("""
■ SimpleRNN 동작 원리:
  각 타임스텝에서:
  h_t = tanh(W_xh @ x_t + W_hh @ h_{t-1} + b)

  x_t     = 현재 입력
  h_{t-1} = 이전 은닉 상태 (기억)
  h_t     = 현재 은닉 상태 (업데이트된 기억)

  ┌────┐   ┌────┐   ┌────┐   ┌────┐
  │ h0 │──→│ h1 │──→│ h2 │──→│ h3 │──→ 출력
  └────┘   └────┘   └────┘   └────┘
    ↑        ↑        ↑        ↑
   x0       x1       x2       x3
  "나는"   "매우"   "행복"   "하다"
""")

class ToySimpleRNN:
    """SimpleRNN 토이 구현"""
    def __init__(self, input_size, hidden_size):
        self.input_size = input_size
        self.hidden_size = hidden_size

        # 가중치 초기화
        limit = math.sqrt(1.0 / hidden_size)
        self.W_xh = [[random.uniform(-limit, limit) for _ in range(hidden_size)]
                      for _ in range(input_size)]
        self.W_hh = [[random.uniform(-limit, limit) for _ in range(hidden_size)]
                      for _ in range(hidden_size)]
        self.b_h = [0.0] * hidden_size

    def forward(self, sequence, return_sequences=False):
        """
        sequence: list of vectors (각 타임스텝의 입력)
        return_sequences: True면 모든 h 반환, False면 마지막 h만
        """
        h = [0.0] * self.hidden_size  # 초기 은닉 상태
        all_h = []

        for t, x_t in enumerate(sequence):
            new_h = [0.0] * self.hidden_size

            for j in range(self.hidden_size):
                # W_xh @ x_t
                val = sum(x_t[i] * self.W_xh[i][j] for i in range(min(len(x_t), self.input_size)))
                # W_hh @ h_{t-1}
                val += sum(h[i] * self.W_hh[i][j] for i in range(self.hidden_size))
                # bias + tanh
                val += self.b_h[j]
                new_h[j] = math.tanh(val)

            h = new_h
            all_h.append(h[:])

        if return_sequences:
            return all_h  # 모든 타임스텝의 은닉 상태
        return h  # 마지막 타임스텝만

# SimpleRNN 시연
print("■ SimpleRNN 순전파 시연:")
rnn = ToySimpleRNN(input_size=3, hidden_size=4)

# 3개 타임스텝, 각 입력 차원=3
sequence = [
    [1.0, 0.0, 0.5],  # t=0
    [0.0, 1.0, 0.3],  # t=1
    [0.5, 0.5, 1.0],  # t=2
]

# return_sequences=False (마지막만)
last_h = rnn.forward(sequence, return_sequences=False)
print(f"  입력 시퀀스 길이: {len(sequence)}, 입력 차원: {len(sequence[0])}")
print(f"  return_sequences=False:")
print(f"    출력: {[f'{v:.4f}' for v in last_h]}")
print(f"    형태: ({len(last_h)},)  ← 마지막 은닉 상태만")

# return_sequences=True (전부)
all_h = rnn.forward(sequence, return_sequences=True)
print(f"\n  return_sequences=True:")
for t, h in enumerate(all_h):
    print(f"    t={t}: {[f'{v:.4f}' for v in h]}")
print(f"    형태: ({len(all_h)}, {len(all_h[0])})  ← 모든 타임스텝")

print("""
■ return_sequences 사용 시점:
  False: 마지막 출력만 필요 (분류, 감성 분석)
         시퀀스 → 하나의 라벨
  True:  모든 출력 필요 (다음 RNN 레이어에 입력, 시퀀스-시퀀스)
         시퀀스 → 시퀀스 (번역, 태깅)
""")

# 실제 코드: tf.keras.layers.SimpleRNN(64, return_sequences=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. LSTM - 장단기 기억 네트워크
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("3. LSTM (Long Short-Term Memory)")
print("=" * 70)

print("""
■ SimpleRNN의 문제: 기울기 소실 (Vanishing Gradient)
  긴 시퀀스에서 초기 정보가 사라짐!
  "처음에 읽은 내용을 끝에서 기억 못함"

■ LSTM의 해결: 3개의 게이트 + 셀 상태(Cell State)

  ┌───────────────────────────────────────────┐
  │            LSTM 셀 구조                    │
  │                                            │
  │  ┌──────┐  ┌──────┐  ┌──────┐             │
  │  │ 망각  │  │ 입력  │  │ 출력  │            │
  │  │ 게이트│  │ 게이트│  │ 게이트│            │
  │  └───┬──┘  └───┬──┘  └───┬──┘             │
  │      │         │         │                 │
  │  C_{t-1} ──→ C_t ──→ ──→ h_t             │
  │  (셀 상태: 장기 기억의 고속도로!)          │
  └───────────────────────────────────────────┘

  망각 게이트(f): 이전 기억 중 얼마나 잊을지 (0~1)
  입력 게이트(i): 새 정보 중 얼마나 기억할지 (0~1)
  출력 게이트(o): 기억 중 얼마나 출력할지 (0~1)

  비유:
  f = "어제 뉴스 중 쓸모없는 건 잊자" (0=완전 잊음, 1=전부 기억)
  i = "오늘 뉴스 중 중요한 것만 기억" (0=무시, 1=전부 기억)
  o = "기억 중 지금 필요한 것만 꺼내기" (0=숨김, 1=전부 출력)
""")

class ToyLSTM:
    """LSTM 토이 구현"""
    def __init__(self, input_size, hidden_size):
        self.input_size = input_size
        self.hidden_size = hidden_size

        # 4개의 게이트 가중치 (f, i, g, o)
        limit = math.sqrt(1.0 / hidden_size)
        self._init_gate = lambda: {
            'W_x': [[random.uniform(-limit, limit) for _ in range(hidden_size)]
                     for _ in range(input_size)],
            'W_h': [[random.uniform(-limit, limit) for _ in range(hidden_size)]
                     for _ in range(hidden_size)],
            'b': [0.0] * hidden_size
        }

        self.forget_gate = self._init_gate()
        self.input_gate = self._init_gate()
        self.cell_gate = self._init_gate()    # 후보 셀 (g)
        self.output_gate = self._init_gate()

    def _gate_forward(self, gate, x, h, activation='sigmoid'):
        """게이트 순전파"""
        result = [0.0] * self.hidden_size
        for j in range(self.hidden_size):
            val = sum(x[i] * gate['W_x'][i % self.input_size][j]
                     for i in range(min(len(x), self.input_size)))
            val += sum(h[i] * gate['W_h'][i][j]
                      for i in range(self.hidden_size))
            val += gate['b'][j]
            if activation == 'sigmoid':
                result[j] = 1.0 / (1.0 + math.exp(-max(-20, min(20, val))))
            elif activation == 'tanh':
                result[j] = math.tanh(val)
        return result

    def forward(self, sequence, return_sequences=False):
        h = [0.0] * self.hidden_size  # 은닉 상태
        c = [0.0] * self.hidden_size  # 셀 상태 (장기 기억!)
        all_h = []

        for x_t in sequence:
            # 망각 게이트: 이전 기억 중 얼마나 잊을지
            f = self._gate_forward(self.forget_gate, x_t, h, 'sigmoid')

            # 입력 게이트: 새 정보 중 얼마나 기억할지
            i = self._gate_forward(self.input_gate, x_t, h, 'sigmoid')

            # 후보 셀 상태: 새로 기억할 정보
            g = self._gate_forward(self.cell_gate, x_t, h, 'tanh')

            # 출력 게이트: 기억 중 얼마나 출력할지
            o = self._gate_forward(self.output_gate, x_t, h, 'sigmoid')

            # 셀 상태 업데이트: c = f * c_prev + i * g
            c = [f[j] * c[j] + i[j] * g[j] for j in range(self.hidden_size)]

            # 은닉 상태 업데이트: h = o * tanh(c)
            h = [o[j] * math.tanh(c[j]) for j in range(self.hidden_size)]

            all_h.append(h[:])

        return all_h if return_sequences else h

# LSTM 시연
print("■ LSTM 순전파 시연:")
lstm = ToyLSTM(input_size=3, hidden_size=4)
output_lstm = lstm.forward(sequence, return_sequences=False)
print(f"  LSTM 출력: {[f'{v:.4f}' for v in output_lstm]}")

# SimpleRNN vs LSTM 비교
print(f"\n■ SimpleRNN vs LSTM 비교:")
print(f"  SimpleRNN: 파라미터 = in*h + h*h + h = {3*4 + 4*4 + 4}")
print(f"  LSTM:      파라미터 = 4*(in*h + h*h + h) = {4*(3*4 + 4*4 + 4)}")
print(f"  → LSTM은 4배 많은 파라미터 (4개 게이트)")
print(f"  → 하지만 장기 기억 능력이 훨씬 우수!")

# 실제 코드: tf.keras.layers.LSTM(64, return_sequences=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. GRU - LSTM의 간소화 버전
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("4. GRU (Gated Recurrent Unit)")
print("=" * 70)

print("""
■ GRU = LSTM의 간소화 버전 (2014, Cho et al.)
  - 게이트가 3개 → 2개로 줄어듦
  - 셀 상태(C)와 은닉 상태(h) 통합
  - LSTM과 비슷한 성능, 더 적은 파라미터

  ┌───────────────────────────────┐
  │  GRU 셀 구조                  │
  │                                │
  │  리셋 게이트 (r):              │
  │    이전 기억 중 얼마나 무시?   │
  │                                │
  │  업데이트 게이트 (z):          │
  │    이전 vs 새로운 기억 비율?   │
  └───────────────────────────────┘

■ LSTM vs GRU:
  LSTM: 3게이트, 셀+은닉 분리, 파라미터 많음, 긴 시퀀스에 유리
  GRU:  2게이트, 은닉만, 파라미터 적음, 짧은 시퀀스에 효율적
""")

class ToyGRU:
    """GRU 토이 구현"""
    def __init__(self, input_size, hidden_size):
        self.input_size = input_size
        self.hidden_size = hidden_size

        limit = math.sqrt(1.0 / hidden_size)
        self._init_gate = lambda: {
            'W_x': [[random.uniform(-limit, limit) for _ in range(hidden_size)]
                     for _ in range(input_size)],
            'W_h': [[random.uniform(-limit, limit) for _ in range(hidden_size)]
                     for _ in range(hidden_size)],
            'b': [0.0] * hidden_size
        }

        self.reset_gate = self._init_gate()
        self.update_gate = self._init_gate()
        self.candidate_gate = self._init_gate()

    def _gate_forward(self, gate, x, h, activation='sigmoid'):
        result = [0.0] * self.hidden_size
        for j in range(self.hidden_size):
            val = sum(x[i] * gate['W_x'][i % self.input_size][j]
                     for i in range(min(len(x), self.input_size)))
            val += sum(h[i] * gate['W_h'][i][j] for i in range(self.hidden_size))
            val += gate['b'][j]
            if activation == 'sigmoid':
                result[j] = 1.0 / (1.0 + math.exp(-max(-20, min(20, val))))
            else:
                result[j] = math.tanh(val)
        return result

    def forward(self, sequence, return_sequences=False):
        h = [0.0] * self.hidden_size
        all_h = []

        for x_t in sequence:
            # 리셋 게이트
            r = self._gate_forward(self.reset_gate, x_t, h, 'sigmoid')
            # 업데이트 게이트
            z = self._gate_forward(self.update_gate, x_t, h, 'sigmoid')
            # 후보 은닉 상태 (리셋 적용)
            h_reset = [r[j] * h[j] for j in range(self.hidden_size)]
            h_candidate = self._gate_forward(self.candidate_gate, x_t, h_reset, 'tanh')
            # 최종 은닉 상태: z * h_prev + (1-z) * h_candidate
            h = [z[j] * h[j] + (1 - z[j]) * h_candidate[j]
                 for j in range(self.hidden_size)]
            all_h.append(h[:])

        return all_h if return_sequences else h

gru = ToyGRU(input_size=3, hidden_size=4)
output_gru = gru.forward(sequence)
print(f"\n■ GRU 출력: {[f'{v:.4f}' for v in output_gru]}")

print(f"\n■ 파라미터 수 비교 (input=3, hidden=4):")
print(f"  SimpleRNN: {3*4 + 4*4 + 4}")
print(f"  GRU:       {3*(3*4 + 4*4 + 4)}  (3개 게이트)")
print(f"  LSTM:      {4*(3*4 + 4*4 + 4)}  (4개 게이트)")

# 실제 코드: tf.keras.layers.GRU(64, return_sequences=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Embedding 레이어
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("5. Embedding 레이어 - 단어를 벡터로 변환")
print("=" * 70)

print("""
■ 왜 Embedding이 필요한가?
  컴퓨터는 "고양이"라는 단어를 직접 처리할 수 없음!
  단어 → 숫자(인덱스) → 벡터(실수 배열)로 변환 필요

  방법 1: 원핫 인코딩 (비효율적!)
    "고양이" → [0, 0, 1, 0, 0, ...]  (어휘 크기만큼 길어짐)
    문제: 10만 단어면 10만 차원! + 유사도 표현 불가

  방법 2: Embedding (효율적!)
    "고양이" → [0.23, -0.45, 0.78, 0.12]  (고정 길이 밀집 벡터)
    장점: 낮은 차원 + 유사한 단어는 가까운 벡터!

■ Embedding 비유:
  도서관 사서가 "고양이"라는 단어를 들으면
  머릿속에 [귀여움, 동물, 작음, 독립적] 같은 특성 벡터가 떠오름!
""")

class ToyEmbedding:
    """Embedding 레이어 토이 구현"""
    def __init__(self, vocab_size, embedding_dim):
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        # 임베딩 테이블: 각 단어 인덱스 → 벡터
        self.embeddings = [
            [random.gauss(0, 0.1) for _ in range(embedding_dim)]
            for _ in range(vocab_size)
        ]

    def forward(self, indices):
        """단어 인덱스 리스트 → 임베딩 벡터 시퀀스"""
        return [self.embeddings[idx] for idx in indices]

    def similarity(self, idx1, idx2):
        """두 단어의 코사인 유사도"""
        v1 = self.embeddings[idx1]
        v2 = self.embeddings[idx2]
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a ** 2 for a in v1))
        norm2 = math.sqrt(sum(b ** 2 for b in v2))
        return dot / (norm1 * norm2 + 1e-8)

# 간단한 단어 사전
vocab = {
    '<PAD>': 0, '나는': 1, '매우': 2, '행복': 3, '하다': 4,
    '슬프': 5, '영화': 6, '좋다': 7, '재미': 8, '없다': 9,
    '최고': 10, '별로': 11, '감동': 12, '지루': 13, '추천': 14
}

embedding = ToyEmbedding(vocab_size=15, embedding_dim=4)

# 문장을 인덱스로 변환 후 임베딩
sentence = "나는 매우 행복 하다"
indices = [vocab.get(word, 0) for word in sentence.split()]
embedded = embedding.forward(indices)

print(f"\n■ Embedding 시연:")
print(f"  문장: '{sentence}'")
print(f"  인덱스: {indices}")
print(f"  임베딩 (vocab_size={embedding.vocab_size}, dim={embedding.embedding_dim}):")
for word, idx, vec in zip(sentence.split(), indices, embedded):
    print(f"    '{word}' (idx={idx}) → [{', '.join(f'{v:.3f}' for v in vec)}]")

# 단어 유사도 (학습 전이므로 무작위)
print(f"\n  단어 유사도 (학습 전, 무작위):")
pairs = [('행복', '좋다'), ('행복', '슬프'), ('영화', '감동')]
for w1, w2 in pairs:
    sim = embedding.similarity(vocab[w1], vocab[w2])
    print(f"    '{w1}' vs '{w2}': {sim:.4f}")
print(f"  ※ 학습 후에는 유사한 단어끼리 높은 유사도를 가짐!")

# 실제 코드: tf.keras.layers.Embedding(vocab_size=10000, output_dim=128)
# 실제 코드:
# 실제 코드: # 사전학습 임베딩 사용 (Word2Vec, GloVe)
# 실제 코드: embedding_layer = tf.keras.layers.Embedding(
# 실제 코드:     input_dim=vocab_size,
# 실제 코드:     output_dim=300,
# 실제 코드:     weights=[glove_matrix],  # 사전학습 가중치
# 실제 코드:     trainable=False          # 동결 가능
# 실제 코드: )


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Bidirectional - 양방향 RNN
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("6. Bidirectional RNN - 양방향 처리")
print("=" * 70)

print("""
■ 양방향 RNN이란?
  시퀀스를 앞→뒤, 뒤→앞 두 방향으로 읽기!

  "나는 오늘 ___를 먹었다"
  →방향: "나는 오늘"까지 읽음 → "아마 음식?"
  ←방향: "먹었다"를 먼저 봄 → "확실히 음식!"
  양방향: 앞뒤 문맥 모두 활용 → 더 정확한 예측!

  ┌────→────→────→────→────┐ 순방향 h
  │ h0 │ h1 │ h2 │ h3 │ h4│
  │    │    │    │    │    │
  │ h4 │ h3 │ h2 │ h1 │ h0│
  └────←────←────←────←────┘ 역방향 h

  출력 = concat(순방향 h, 역방향 h)
  → 출력 차원이 2배!
""")

class ToyBidirectional:
    """양방향 RNN 시뮬레이션"""
    def __init__(self, rnn_class, input_size, hidden_size):
        self.forward_rnn = rnn_class(input_size, hidden_size)
        self.backward_rnn = rnn_class(input_size, hidden_size)
        self.hidden_size = hidden_size

    def forward(self, sequence, return_sequences=False):
        # 순방향
        forward_out = self.forward_rnn.forward(sequence, return_sequences=True)
        # 역방향 (시퀀스 뒤집기)
        backward_out = self.backward_rnn.forward(sequence[::-1], return_sequences=True)
        backward_out = backward_out[::-1]  # 원래 순서로 복원

        if return_sequences:
            # 각 타임스텝에서 순방향+역방향 연결
            return [fwd + bwd for fwd, bwd in zip(forward_out, backward_out)]
        else:
            # 마지막 순방향 + 첫 역방향(=마지막 역방향 처리)
            return forward_out[-1] + backward_out[0]

bi_lstm = ToyBidirectional(ToyLSTM, input_size=3, hidden_size=4)
bi_output = bi_lstm.forward(sequence, return_sequences=False)
print(f"\n■ Bidirectional LSTM 출력:")
print(f"  출력 차원: {len(bi_output)} (= hidden_size * 2 = 4 * 2)")
print(f"  출력: {[f'{v:.4f}' for v in bi_output]}")

# 실제 코드: tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64))
# 실제 코드: # 출력 차원 = 64 * 2 = 128


# ═══════════════════════════════════════════════════════════════════════════════
# 7. 텍스트 전처리 파이프라인
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("7. 텍스트 전처리 파이프라인")
print("=" * 70)

def build_vocab(texts, max_vocab=1000):
    """단어 사전 구축"""
    word_counts = {}
    for text in texts:
        for word in text.split():
            word_counts[word] = word_counts.get(word, 0) + 1

    # 빈도순 정렬
    sorted_words = sorted(word_counts.items(), key=lambda x: -x[1])
    vocab = {'<PAD>': 0, '<UNK>': 1}
    for word, count in sorted_words[:max_vocab - 2]:
        vocab[word] = len(vocab)
    return vocab

def texts_to_sequences(texts, vocab):
    """텍스트 → 인덱스 시퀀스"""
    sequences = []
    for text in texts:
        seq = [vocab.get(word, vocab['<UNK>']) for word in text.split()]
        sequences.append(seq)
    return sequences

def pad_sequences(sequences, maxlen, pad_value=0):
    """시퀀스 길이 통일 (패딩)"""
    result = []
    for seq in sequences:
        if len(seq) > maxlen:
            result.append(seq[:maxlen])  # 잘라내기
        else:
            result.append(seq + [pad_value] * (maxlen - len(seq)))  # 패딩
    return result

# 전처리 시연
texts = [
    "이 영화 정말 재미있다 강력 추천",
    "최악의 영화 시간 낭비",
    "배우 연기가 좋다 감동적",
    "지루하고 재미없다",
    "최고의 명작 다시 보고 싶다",
]
labels = [1, 0, 1, 0, 1]  # 1=긍정, 0=부정

print("■ 텍스트 전처리 파이프라인:")
print(f"\n  원본 텍스트:")
for text, label in zip(texts, labels):
    print(f"    {'긍정' if label else '부정'}: '{text}'")

# Step 1: 사전 구축
text_vocab = build_vocab(texts)
print(f"\n  Step 1 - 사전 구축 ({len(text_vocab)} 단어):")
for word, idx in list(text_vocab.items())[:10]:
    print(f"    '{word}' → {idx}")

# Step 2: 인덱스 변환
sequences = texts_to_sequences(texts, text_vocab)
print(f"\n  Step 2 - 인덱스 변환:")
for text, seq in zip(texts, sequences):
    print(f"    '{text[:20]}...' → {seq}")

# Step 3: 패딩
maxlen = 8
padded = pad_sequences(sequences, maxlen)
print(f"\n  Step 3 - 패딩 (maxlen={maxlen}):")
for seq in padded:
    print(f"    {seq}")

# 실제 코드: tf.keras.preprocessing.text.Tokenizer
# 실제 코드: tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words=10000)
# 실제 코드: tokenizer.fit_on_texts(texts)
# 실제 코드: sequences = tokenizer.texts_to_sequences(texts)
# 실제 코드: padded = tf.keras.preprocessing.sequence.pad_sequences(sequences, maxlen=200)


# ═══════════════════════════════════════════════════════════════════════════════
# 8. [실습] 감성 분석 시뮬레이션
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("8. [실습] 감성 분석 (긍정/부정 분류) 시뮬레이션")
print("=" * 70)

class ToySentimentModel:
    """감성 분석 모델 (Embedding → LSTM → Dense)"""
    def __init__(self, vocab_size, embed_dim, hidden_size):
        self.embedding = ToyEmbedding(vocab_size, embed_dim)
        self.lstm = ToyLSTM(embed_dim, hidden_size)
        self.hidden_size = hidden_size

        # 출력 Dense 가중치
        limit = math.sqrt(1.0 / hidden_size)
        self.w_out = [random.uniform(-limit, limit) for _ in range(hidden_size)]
        self.b_out = 0.0

    def predict(self, indices):
        """인덱스 시퀀스 → 감성 확률"""
        # Embedding
        embedded = self.embedding.forward(indices)
        # LSTM (마지막 은닉 상태)
        h = self.lstm.forward(embedded, return_sequences=False)
        # Dense + Sigmoid (이진 분류)
        logit = sum(h[i] * self.w_out[i] for i in range(self.hidden_size)) + self.b_out
        prob = 1.0 / (1.0 + math.exp(-max(-20, min(20, logit))))
        return prob

# 모델 생성 및 예측
model = ToySentimentModel(vocab_size=len(text_vocab), embed_dim=4, hidden_size=6)

print("\n■ 감성 분석 모델 구조:")
print(f"  Embedding(vocab={len(text_vocab)}, dim=4)")
print(f"  LSTM(hidden_size=6)")
print(f"  Dense(1, sigmoid)")

print(f"\n■ 예측 결과 (학습 전, 랜덤 가중치):")
print(f"  {'텍스트':<30} {'실제':>4} {'예측확률':>8} {'예측':>4}")
print(f"  {'─'*30} {'─'*4} {'─'*8} {'─'*4}")

for text, label, seq in zip(texts, labels, padded):
    prob = model.predict(seq)
    pred = "긍정" if prob > 0.5 else "부정"
    actual = "긍정" if label == 1 else "부정"
    print(f"  {text:<30} {actual:>4} {prob:>8.4f} {pred:>4}")

print(f"\n  ※ 학습 전이므로 예측이 무작위입니다.")
print(f"     실제 학습 후에는 90%+ 정확도 달성 가능!")

# 실제 코드: 감성 분석 모델
# 실제 코드: model = tf.keras.Sequential([
# 실제 코드:     tf.keras.layers.Embedding(10000, 128, input_length=200),
# 실제 코드:     tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64)),
# 실제 코드:     tf.keras.layers.Dropout(0.5),
# 실제 코드:     tf.keras.layers.Dense(32, activation='relu'),
# 실제 코드:     tf.keras.layers.Dense(1, activation='sigmoid')
# 실제 코드: ])
# 실제 코드:
# 실제 코드: model.compile(optimizer='adam',
# 실제 코드:               loss='binary_crossentropy',
# 실제 코드:               metrics=['accuracy'])
# 실제 코드:
# 실제 코드: # IMDB 데이터셋 사용
# 실제 코드: (x_train, y_train), (x_test, y_test) = tf.keras.datasets.imdb.load_data(num_words=10000)
# 실제 코드: x_train = tf.keras.preprocessing.sequence.pad_sequences(x_train, maxlen=200)
# 실제 코드: x_test = tf.keras.preprocessing.sequence.pad_sequences(x_test, maxlen=200)
# 실제 코드:
# 실제 코드: model.fit(x_train, y_train, epochs=5, batch_size=64, validation_split=0.2)
# 실제 코드: # → 테스트 정확도 ~87%


# ═══════════════════════════════════════════════════════════════════════════════
# 9. RNN 실전 팁
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("9. RNN 실전 팁")
print("=" * 70)

print("""
■ RNN 선택 가이드:
  SimpleRNN: 교육용만! (실전에서는 거의 안 씀)
  LSTM: 긴 시퀀스, 안정적, 가장 검증됨
  GRU: LSTM과 비슷한 성능, 더 빠름

■ 시퀀스 길이와 성능:
  짧은 시퀀스 (< 100): GRU 추천 (빠름)
  긴 시퀀스 (100~500): LSTM 추천 (안정적)
  매우 긴 시퀀스 (500+): Transformer 추천!

■ 스태킹 (여러 RNN 층 쌓기):
  LSTM(return_sequences=True)  ← 반드시 True!
  LSTM(return_sequences=True)
  LSTM(return_sequences=False) ← 마지막은 False 가능

■ 드롭아웃:
  - recurrent_dropout: 순환 연결에 드롭아웃 (GPU 호환 주의)
  - dropout: 입력에 드롭아웃
  → 과적합 방지에 효과적

■ 양방향 사용:
  - 전체 시퀀스를 볼 수 있을 때만! (분류, 태깅)
  - 미래를 모르는 경우 사용 불가 (시계열 예측, 생성)

■ 최신 대안: Transformer!
  - RNN보다 병렬화 가능 → 학습 속도 빠름
  - Self-Attention으로 장거리 의존성 해결
  - BERT, GPT 등의 기반
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 10. 시퀀스-시퀀스 모델 개요
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("10. 시퀀스-시퀀스 (Seq2Seq) 모델 개요")
print("=" * 70)

print("""
■ Seq2Seq란?
  입력 시퀀스 → 출력 시퀀스 (길이가 달라도 OK!)

  응용:
  - 기계 번역: "Hello world" → "안녕 세상"
  - 텍스트 요약: 긴 문서 → 짧은 요약
  - 챗봇: 질문 → 답변
  - 음성 인식: 음성 파형 → 텍스트

■ Encoder-Decoder 구조:
  ┌──────────────┐     ┌──────────────┐
  │   Encoder    │     │   Decoder    │
  │   (LSTM)     │────→│   (LSTM)     │
  │              │     │              │
  │  입력 시퀀스  │     │  출력 시퀀스  │
  │  "Hello"     │     │  "안녕"       │
  │  "world"     │     │  "세상"       │
  └──────────────┘     └──────────────┘

  Encoder: 입력을 이해하여 고정 크기 벡터(context)로 압축
  Decoder: context를 받아 출력 시퀀스 생성

■ Attention 메커니즘:
  Decoder가 Encoder의 모든 은닉 상태를 참조!
  → "world"를 번역할 때 "Hello"보다 "world"에 더 집중
  → Transformer의 기반!
""")

# 간단한 Encoder 시뮬레이션
print("■ Encoder-Decoder 시뮬레이션:")
encoder = ToyLSTM(input_size=4, hidden_size=6)
decoder = ToyLSTM(input_size=4, hidden_size=6)

# 인코더 입력 (예: "Hello world" 임베딩)
encoder_input = [
    [random.random() for _ in range(4)],  # "Hello"
    [random.random() for _ in range(4)],  # "world"
]

# 인코딩
context = encoder.forward(encoder_input, return_sequences=False)
print(f"  Encoder 출력 (context): {[f'{v:.3f}' for v in context]}")

# 디코딩 (context를 첫 입력으로)
decoder_input = [context[:4]]  # context를 잘라서 입력
decoded = decoder.forward(decoder_input, return_sequences=False)
print(f"  Decoder 출력:           {[f'{v:.3f}' for v in decoded]}")


print("\n" + "=" * 70)
print("요약: RNN과 텍스트 처리 학습 완료!")
print("=" * 70)
print("""
  1. 시퀀스 데이터: 순서가 중요한 데이터 (텍스트, 시계열)
  2. SimpleRNN: 기본 RNN, 기울기 소실 문제
  3. LSTM: 3게이트 + 셀 상태, 장기 기억 가능
  4. GRU: 2게이트, LSTM의 간소화, 비슷한 성능
  5. Embedding: 단어 → 밀집 벡터 변환
  6. Bidirectional: 앞뒤 양방향 처리
  7. 텍스트 전처리: 토큰화 → 인덱싱 → 패딩
  8. Seq2Seq: 인코더-디코더, Attention

  다음 단계 → 09_functional_api.py (Functional API로 복잡한 모델!)
""")
