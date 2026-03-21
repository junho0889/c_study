# #########################################################################
#
#   PyTorch 학습 06단계: RNN과 자연어 처리(NLP)
#   - RNN, LSTM, GRU, Embedding, 양방향 RNN, 텍스트 분류 -
#   # 실행 방법: python 06_rnn_nlp.py (개념 학습용, PyTorch 없이 실행 가능)
#   # PyTorch 설치: pip install torch torchvision
#
# #########################################################################

import math
import random

random.seed(42)

# ===============================================================================
#  1. RNN (Recurrent Neural Network) 이란?
# ===============================================================================
print("=" * 70)
print("Part 1: RNN (순환 신경망) 이해")
print("=" * 70)

print("""
RNN = 시퀀스(순서가 있는) 데이터를 처리하는 신경망

비유: 일기를 읽는 사람
  - 어제 내용을 기억하면서(은닉 상태) 오늘 일기를 읽음
  - 이전 정보가 다음 처리에 영향을 줌

사용 분야:
  - 텍스트 (문장, 번역, 감정 분석)
  - 시계열 (주가, 날씨, 센서)
  - 음성 (음성 인식, 음악 생성)

핵심 수식:
  h_t = tanh(W_ih @ x_t + W_hh @ h_{t-1} + b)
  - h_t: 현재 은닉 상태
  - x_t: 현재 입력
  - h_{t-1}: 이전 은닉 상태
""")


# ===============================================================================
#  2. 기본 RNN 구현
# ===============================================================================
print("\n" + "=" * 70)
print("Part 2: 기본 RNN 구현")
print("=" * 70)


class SimpleRNN:
    """기본 RNN 셀 구현"""

    def __init__(self, input_size, hidden_size):
        self.input_size = input_size
        self.hidden_size = hidden_size

        # 가중치 초기화 (Xavier)
        k = 1.0 / math.sqrt(hidden_size)
        self.W_ih = [[random.uniform(-k, k) for _ in range(input_size)]
                     for _ in range(hidden_size)]    # 입력→은닉
        self.W_hh = [[random.uniform(-k, k) for _ in range(hidden_size)]
                     for _ in range(hidden_size)]    # 은닉→은닉
        self.b_h = [random.uniform(-k, k) for _ in range(hidden_size)]

    def forward(self, x_sequence, h_0=None):
        """
        x_sequence: 시퀀스 입력 [(x1), (x2), ..., (x_T)]
                    각 x_t는 (input_size,) 벡터
        h_0: 초기 은닉 상태
        반환: 모든 시점의 은닉 상태, 마지막 은닉 상태
        """
        seq_len = len(x_sequence)
        if h_0 is None:
            h = [0.0] * self.hidden_size
        else:
            h = h_0[:]

        all_hidden = []

        for t in range(seq_len):
            x_t = x_sequence[t]
            h_new = [0.0] * self.hidden_size

            for i in range(self.hidden_size):
                # W_ih @ x_t
                val = sum(self.W_ih[i][j] * x_t[j] for j in range(self.input_size))
                # + W_hh @ h_{t-1}
                val += sum(self.W_hh[i][j] * h[j] for j in range(self.hidden_size))
                # + bias
                val += self.b_h[i]
                # tanh 활성화
                h_new[i] = math.tanh(val)

            h = h_new
            all_hidden.append(h[:])

        return all_hidden, h  # (모든 은닉, 마지막 은닉)


# RNN 테스트
print("\n--- 기본 RNN 테스트 ---")
rnn = SimpleRNN(input_size=3, hidden_size=4)

# 시퀀스 입력: 길이 5, 각 벡터 크기 3
sequence = [[random.random() for _ in range(3)] for _ in range(5)]
all_hidden, last_hidden = rnn.forward(sequence)

print(f"입력 시퀀스 길이: {len(sequence)}")
print(f"입력 차원: {len(sequence[0])}")
print(f"은닉 상태 차원: {len(last_hidden)}")
print(f"출력 시퀀스 길이: {len(all_hidden)}")
print(f"마지막 은닉 상태: [{', '.join(f'{v:.4f}' for v in last_hidden)}]")

# 실제 PyTorch 코드:
# rnn = nn.RNN(input_size=3, hidden_size=4, batch_first=True)
# x = torch.randn(1, 5, 3)      # (batch, seq_len, input_size)
# output, h_n = rnn(x)
# # output: (1, 5, 4) - 모든 시점의 출력
# # h_n: (1, 1, 4) - 마지막 은닉 상태


# ===============================================================================
#  3. LSTM (Long Short-Term Memory)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 3: LSTM")
print("=" * 70)

print("""
LSTM = 장기 기억 문제를 해결한 개선된 RNN

기본 RNN의 문제: 긴 시퀀스에서 기울기 소실 → 먼 과거 정보 잊음
LSTM의 해결: "셀 상태(cell state)"라는 고속도로 추가

비유: 기본 RNN = 구전 전화기 (중간에 정보가 왜곡됨)
     LSTM = 메모장을 가진 전화기 (중요한 건 적어두고, 불필요한 건 지움)

LSTM의 3개 게이트:
  - 망각 게이트(Forget Gate): 뭘 잊을까? (σ)
  - 입력 게이트(Input Gate): 뭘 기억할까? (σ × tanh)
  - 출력 게이트(Output Gate): 뭘 출력할까? (σ)
""")


class SimpleLSTM:
    """LSTM 셀 구현 (간소화)"""

    def __init__(self, input_size, hidden_size):
        self.input_size = input_size
        self.hidden_size = hidden_size

        k = 1.0 / math.sqrt(hidden_size)

        # 4개의 게이트를 위한 가중치 (i, f, g, o)
        def init_weights(in_sz, out_sz):
            return [[random.uniform(-k, k) for _ in range(in_sz)]
                    for _ in range(out_sz)]

        # 입력→게이트, 은닉→게이트 가중치
        self.W_ii = init_weights(input_size, hidden_size)   # 입력 게이트
        self.W_hi = init_weights(hidden_size, hidden_size)
        self.W_if = init_weights(input_size, hidden_size)   # 망각 게이트
        self.W_hf = init_weights(hidden_size, hidden_size)
        self.W_ig = init_weights(input_size, hidden_size)   # 셀 후보
        self.W_hg = init_weights(hidden_size, hidden_size)
        self.W_io = init_weights(input_size, hidden_size)   # 출력 게이트
        self.W_ho = init_weights(hidden_size, hidden_size)

    def _sigmoid(self, x):
        return 1.0 / (1.0 + math.exp(-max(-500, min(500, x))))

    def _gate(self, W_x, x, W_h, h):
        """게이트 연산: W_x @ x + W_h @ h"""
        result = [0.0] * self.hidden_size
        for i in range(self.hidden_size):
            val = sum(W_x[i][j] * x[j] for j in range(len(x)))
            val += sum(W_h[i][j] * h[j] for j in range(self.hidden_size))
            result[i] = val
        return result

    def forward(self, x_sequence, h_0=None, c_0=None):
        seq_len = len(x_sequence)
        h = h_0[:] if h_0 else [0.0] * self.hidden_size
        c = c_0[:] if c_0 else [0.0] * self.hidden_size
        all_hidden = []

        for t in range(seq_len):
            x_t = x_sequence[t]

            # 입력 게이트: 새 정보를 얼마나 받아들일지
            i_gate = [self._sigmoid(v) for v in self._gate(self.W_ii, x_t, self.W_hi, h)]

            # 망각 게이트: 이전 정보를 얼마나 잊을지
            f_gate = [self._sigmoid(v) for v in self._gate(self.W_if, x_t, self.W_hf, h)]

            # 셀 후보: 새로운 후보 정보
            g_gate = [math.tanh(v) for v in self._gate(self.W_ig, x_t, self.W_hg, h)]

            # 출력 게이트: 얼마나 출력할지
            o_gate = [self._sigmoid(v) for v in self._gate(self.W_io, x_t, self.W_ho, h)]

            # 셀 상태 업데이트: c = f * c + i * g
            c = [f_gate[j] * c[j] + i_gate[j] * g_gate[j]
                 for j in range(self.hidden_size)]

            # 은닉 상태: h = o * tanh(c)
            h = [o_gate[j] * math.tanh(c[j]) for j in range(self.hidden_size)]

            all_hidden.append(h[:])

        return all_hidden, (h, c)  # 출력, (마지막 은닉, 마지막 셀)


print("\n--- LSTM 테스트 ---")
lstm = SimpleLSTM(input_size=3, hidden_size=4)
sequence = [[random.random() for _ in range(3)] for _ in range(5)]
all_hidden, (h_n, c_n) = lstm.forward(sequence)

print(f"입력: seq_len=5, input_size=3")
print(f"출력 h_n: [{', '.join(f'{v:.4f}' for v in h_n)}]")
print(f"셀 상태 c_n: [{', '.join(f'{v:.4f}' for v in c_n)}]")
print(f"h_n ≠ c_n → 은닉 상태와 셀 상태는 다릅니다!")

# 실제 PyTorch 코드:
# lstm = nn.LSTM(input_size=3, hidden_size=4, batch_first=True)
# x = torch.randn(1, 5, 3)
# output, (h_n, c_n) = lstm(x)
# # output: (1, 5, 4) - 모든 시점의 h
# # h_n: (1, 1, 4) - 마지막 은닉 상태
# # c_n: (1, 1, 4) - 마지막 셀 상태


# ===============================================================================
#  4. GRU (Gated Recurrent Unit)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 4: GRU")
print("=" * 70)

print("""
GRU = LSTM의 간소화 버전 (2개 게이트)

LSTM: 3개 게이트 + 셀 상태 → 파라미터 많음
GRU:  2개 게이트, 셀 상태 없음 → 더 빠르고 간단

GRU 게이트:
  - 리셋 게이트(Reset): 이전 정보를 얼마나 리셋할지
  - 업데이트 게이트(Update): 이전 vs 새 정보 비율

성능은 LSTM과 비슷하거나, 데이터가 적을 때 더 좋을 수 있음!
""")


class SimpleGRU:
    """GRU 셀 구현"""

    def __init__(self, input_size, hidden_size):
        self.input_size = input_size
        self.hidden_size = hidden_size
        k = 1.0 / math.sqrt(hidden_size)

        def init_w(in_sz, out_sz):
            return [[random.uniform(-k, k) for _ in range(in_sz)]
                    for _ in range(out_sz)]

        self.W_ir = init_w(input_size, hidden_size)   # 리셋 게이트
        self.W_hr = init_w(hidden_size, hidden_size)
        self.W_iz = init_w(input_size, hidden_size)   # 업데이트 게이트
        self.W_hz = init_w(hidden_size, hidden_size)
        self.W_in = init_w(input_size, hidden_size)   # 새 은닉 후보
        self.W_hn = init_w(hidden_size, hidden_size)

    def _sigmoid(self, x):
        return 1.0 / (1.0 + math.exp(-max(-500, min(500, x))))

    def _gate(self, W_x, x, W_h, h):
        result = [0.0] * self.hidden_size
        for i in range(self.hidden_size):
            val = sum(W_x[i][j] * x[j] for j in range(len(x)))
            val += sum(W_h[i][j] * h[j] for j in range(self.hidden_size))
            result[i] = val
        return result

    def forward(self, x_sequence, h_0=None):
        h = h_0[:] if h_0 else [0.0] * self.hidden_size
        all_hidden = []

        for t in range(len(x_sequence)):
            x_t = x_sequence[t]

            # 리셋 게이트
            r = [self._sigmoid(v) for v in self._gate(self.W_ir, x_t, self.W_hr, h)]

            # 업데이트 게이트
            z = [self._sigmoid(v) for v in self._gate(self.W_iz, x_t, self.W_hz, h)]

            # 리셋된 은닉 상태
            rh = [r[j] * h[j] for j in range(self.hidden_size)]

            # 새 은닉 후보
            n = [math.tanh(v) for v in self._gate(self.W_in, x_t, self.W_hn, rh)]

            # 은닉 상태 업데이트: h = (1-z)*n + z*h
            h = [(1 - z[j]) * n[j] + z[j] * h[j] for j in range(self.hidden_size)]

            all_hidden.append(h[:])

        return all_hidden, h

# 실제 PyTorch 코드:
# gru = nn.GRU(input_size=3, hidden_size=4, batch_first=True)
# x = torch.randn(1, 5, 3)
# output, h_n = gru(x)  # LSTM과 달리 c_n 없음!

print("\n--- RNN vs LSTM vs GRU 비교 ---")
print(f"{'':>10} {'게이트':>10} {'상태':>15} {'파라미터':>10}")
print("-" * 50)
print(f"{'RNN':>10} {'0':>10} {'h만':>15} {'적음':>10}")
print(f"{'LSTM':>10} {'3':>10} {'h + c (셀)':>15} {'많음':>10}")
print(f"{'GRU':>10} {'2':>10} {'h만':>15} {'중간':>10}")


# ===============================================================================
#  5. nn.Embedding (단어 임베딩)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 5: nn.Embedding (단어 임베딩)")
print("=" * 70)

print("""
Embedding = 정수 인덱스를 밀집 벡터(dense vector)로 변환

비유: 학생 ID → 학생 프로필
  학생 ID 42 → [성적=85, 키=170, 체중=65, 성격=내향] (4차원 벡터)

  단어 "고양이"(ID=42) → [0.2, -0.5, 0.8, 0.1, ...] (임베딩 벡터)
  비슷한 의미의 단어는 비슷한 벡터를 가짐!

원핫 인코딩 vs 임베딩:
  원핫: [0,0,0,...,1,...,0,0] (10000차원, 대부분 0, 관계 없음)
  임베딩: [0.2, -0.5, 0.8, 0.1] (저차원, 밀집, 의미 포함)
""")


class Embedding:
    """단어 임베딩 테이블"""

    def __init__(self, num_embeddings, embedding_dim, padding_idx=None):
        self.num_embeddings = num_embeddings
        self.embedding_dim = embedding_dim
        self.padding_idx = padding_idx

        # 임베딩 테이블: (vocab_size, embedding_dim)
        self.weight = [[random.gauss(0, 1) for _ in range(embedding_dim)]
                       for _ in range(num_embeddings)]

        # 패딩 인덱스는 0 벡터
        if padding_idx is not None:
            self.weight[padding_idx] = [0.0] * embedding_dim

    def __call__(self, indices):
        """인덱스 → 임베딩 벡터"""
        if isinstance(indices, int):
            return self.weight[indices]
        return [self.weight[idx] for idx in indices]


# 임베딩 테스트
vocab_size = 100
embed_dim = 8
embed = Embedding(vocab_size, embed_dim, padding_idx=0)

print(f"\n어휘 크기: {vocab_size}")
print(f"임베딩 차원: {embed_dim}")

# 단어 인덱스로 임베딩 조회
word_ids = [5, 23, 0, 42]  # 0은 패딩
embeddings = embed(word_ids)

print(f"\n단어 ID: {word_ids}")
for wid, emb in zip(word_ids, embeddings):
    status = "(패딩)" if wid == 0 else ""
    print(f"  ID {wid:3d}: [{', '.join(f'{v:.3f}' for v in emb[:4])}...] {status}")

# 실제 PyTorch 코드:
# embed = nn.Embedding(num_embeddings=10000, embedding_dim=128, padding_idx=0)
# word_ids = torch.tensor([5, 23, 0, 42])
# embeddings = embed(word_ids)  # (4, 128)


# ===============================================================================
#  6. PackedSequence와 양방향 RNN
# ===============================================================================
print("\n" + "=" * 70)
print("Part 6: PackedSequence와 양방향(Bidirectional) RNN")
print("=" * 70)

print("""
--- PackedSequence ---
가변 길이 시퀀스를 효율적으로 처리하는 방법

문제: 배치 내 시퀀스 길이가 다르면?
  "나는 학생이다"      → [1, 2, 3]       (3 토큰)
  "오늘 날씨 좋다 매우" → [4, 5, 6, 7]   (4 토큰)

해결: 패딩 + PackedSequence
  1. 패딩으로 길이 통일: [1,2,3,0] [4,5,6,7]
  2. pack_padded_sequence로 패딩 부분 무시
  3. RNN 통과
  4. pad_packed_sequence로 다시 패딩 형태로

--- 양방향 RNN ---
  순방향: "나는 학생이다" → → →
  역방향: "나는 학생이다" ← ← ←
  양방향: 두 방향의 정보를 합침 → 문맥 이해 향상
""")

# 양방향 RNN 시뮬레이션
print("\n--- 양방향 RNN 시뮬레이션 ---")

def bidirectional_rnn(sequence, input_size, hidden_size):
    """양방향 RNN: 순방향 + 역방향"""
    forward_rnn = SimpleRNN(input_size, hidden_size)
    backward_rnn = SimpleRNN(input_size, hidden_size)

    # 순방향
    fwd_hidden, fwd_last = forward_rnn.forward(sequence)
    # 역방향 (시퀀스 뒤집기)
    bwd_hidden, bwd_last = backward_rnn.forward(sequence[::-1])
    bwd_hidden = bwd_hidden[::-1]  # 다시 원래 순서로

    # 양방향 출력: 순방향 + 역방향 연결 (concat)
    bi_hidden = [fwd_hidden[t] + bwd_hidden[t] for t in range(len(sequence))]
    bi_last = fwd_last + bwd_last  # 마지막 은닉: (2 * hidden_size)

    return bi_hidden, bi_last

seq = [[random.random() for _ in range(3)] for _ in range(5)]
bi_hidden, bi_last = bidirectional_rnn(seq, input_size=3, hidden_size=4)

print(f"입력: seq_len=5, input_size=3")
print(f"양방향 출력 차원: {len(bi_hidden[0])} (= 2 * hidden_size = 8)")
print(f"양방향 마지막 은닉: 길이 {len(bi_last)}")

# 실제 PyTorch 코드:
# lstm = nn.LSTM(input_size=3, hidden_size=4, bidirectional=True, batch_first=True)
# x = torch.randn(1, 5, 3)
# output, (h_n, c_n) = lstm(x)
# # output: (1, 5, 8)  - 2*hidden_size (양방향 concat)
# # h_n: (2, 1, 4)     - 2방향의 마지막 은닉
#
# # PackedSequence 사용:
# from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
# lengths = [5, 3, 4]  # 각 시퀀스의 실제 길이
# packed = pack_padded_sequence(x, lengths, batch_first=True, enforce_sorted=False)
# output_packed, (h_n, c_n) = lstm(packed)
# output, lengths = pad_packed_sequence(output_packed, batch_first=True)


# ===============================================================================
#  7. 실습: 간단한 텍스트 분류기
# ===============================================================================
print("\n" + "=" * 70)
print("Part 7: 실습 - 텍스트 감정 분류기")
print("=" * 70)

print("""
과제: 한국어 문장의 감정 분류 (긍정=1, 부정=0)

파이프라인:
  문장 → 토큰화 → 정수 인코딩 → 임베딩 → LSTM → 분류
""")

# 간단한 어휘 사전
vocab = {
    "<PAD>": 0, "<UNK>": 1,
    "좋다": 2, "나쁘다": 3, "최고": 4, "최악": 5,
    "행복": 6, "슬프다": 7, "맛있다": 8, "맛없다": 9,
    "사랑": 10, "싫다": 11, "재미있다": 12, "지루하다": 13,
    "아름답다": 14, "추하다": 15, "기쁘다": 16, "화나다": 17,
    "훌륭하다": 18, "별로다": 19, "감동": 20, "실망": 21,
    "오늘": 22, "영화": 23, "음식": 24, "정말": 25,
    "너무": 26, "매우": 27, "진짜": 28, "이": 29,
}

# 학습 데이터
train_data = [
    (["오늘", "정말", "좋다"], 1),
    (["영화", "너무", "재미있다"], 1),
    (["음식", "맛있다", "최고"], 1),
    (["정말", "행복", "기쁘다"], 1),
    (["매우", "훌륭하다", "감동"], 1),
    (["이", "영화", "최악"], 0),
    (["음식", "맛없다", "나쁘다"], 0),
    (["너무", "슬프다", "실망"], 0),
    (["정말", "지루하다", "별로다"], 0),
    (["진짜", "화나다", "싫다"], 0),
]


def tokenize_and_encode(words, vocab, max_len=5):
    """토큰화 + 정수 인코딩 + 패딩"""
    ids = [vocab.get(w, vocab["<UNK>"]) for w in words]
    # 패딩
    if len(ids) < max_len:
        ids.extend([vocab["<PAD>"]] * (max_len - len(ids)))
    return ids[:max_len]


# 데이터 준비
print("\n--- 학습 데이터 ---")
X_train = []
Y_train = []
for words, label in train_data:
    ids = tokenize_and_encode(words, vocab)
    X_train.append(ids)
    Y_train.append(label)
    sentiment = "긍정" if label == 1 else "부정"
    print(f"  {' '.join(words):20s} → {ids} → {sentiment}")


# 텍스트 분류기
class TextClassifier:
    """LSTM 기반 텍스트 분류기 (간소화)"""

    def __init__(self, vocab_size, embed_dim, hidden_size):
        self.embedding = Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = SimpleLSTM(embed_dim, hidden_size)
        # 분류 레이어 가중치
        k = 1.0 / math.sqrt(hidden_size)
        self.fc_w = [random.uniform(-k, k) for _ in range(hidden_size)]
        self.fc_b = random.uniform(-k, k)

    def forward(self, token_ids):
        # 1. 임베딩
        embedded = self.embedding(token_ids)

        # 2. LSTM
        _, (h_last, _) = self.lstm.forward(embedded)

        # 3. 분류 (선형 → 시그모이드)
        logit = sum(h_last[i] * self.fc_w[i] for i in range(len(h_last))) + self.fc_b
        prob = 1.0 / (1.0 + math.exp(-max(-500, min(500, logit))))
        return prob


classifier = TextClassifier(vocab_size=len(vocab), embed_dim=8, hidden_size=6)

print("\n--- 분류기 테스트 (학습 전) ---")
for words, label in train_data[:4]:
    ids = tokenize_and_encode(words, vocab)
    prob = classifier.forward(ids)
    pred = 1 if prob > 0.5 else 0
    status = "O" if pred == label else "X"
    print(f"  {' '.join(words):20s} → P={prob:.4f} → 예측:{pred} (정답:{label}) [{status}]")

print("\n(학습 전이라 예측이 부정확합니다)")

# 실제 PyTorch 코드:
# class TextClassifier(nn.Module):
#     def __init__(self, vocab_size, embed_dim, hidden_size, num_classes):
#         super().__init__()
#         self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
#         self.lstm = nn.LSTM(embed_dim, hidden_size, batch_first=True,
#                            bidirectional=True)
#         self.fc = nn.Linear(hidden_size * 2, num_classes)
#         self.dropout = nn.Dropout(0.5)
#
#     def forward(self, x):
#         embedded = self.embedding(x)           # (batch, seq_len, embed_dim)
#         embedded = self.dropout(embedded)
#         output, (h_n, c_n) = self.lstm(embedded)
#         # 양방향 마지막 은닉 연결
#         hidden = torch.cat([h_n[-2], h_n[-1]], dim=1)
#         hidden = self.dropout(hidden)
#         out = self.fc(hidden)                  # (batch, num_classes)
#         return out
#
# model = TextClassifier(vocab_size=10000, embed_dim=128,
#                        hidden_size=256, num_classes=2)
# criterion = nn.CrossEntropyLoss()
# optimizer = torch.optim.Adam(model.parameters(), lr=0.001)


# ===============================================================================
#  8. RNN 주의사항과 팁
# ===============================================================================
print("\n" + "=" * 70)
print("Part 8: RNN 주의사항과 팁")
print("=" * 70)

print("""
1. 기울기 폭발/소실:
   - 기울기 클리핑 필수: nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
   - LSTM/GRU가 기본 RNN보다 훨씬 안정적

2. batch_first:
   - batch_first=True: (batch, seq_len, features)  ← 권장
   - batch_first=False: (seq_len, batch, features)  ← PyTorch 기본값!

3. 다층 RNN:
   - num_layers=2 이상으로 깊게 쌓을 수 있음
   - 층 사이에 Dropout 적용 권장

4. Teacher Forcing:
   - 시퀀스 생성(번역 등)에서 학습 시 정답을 다음 입력으로 사용
   - 학습 속도 향상, 하지만 추론과 괴리 발생 가능

5. Attention 메커니즘:
   - RNN의 한계(긴 시퀀스 처리 어려움)를 보완
   - 이후 Transformer로 발전 → 현재 NLP의 주류
""")


# ===============================================================================
#  핵심 정리
# ===============================================================================
print("\n" + "=" * 70)
print("핵심 정리")
print("=" * 70)
print("""
1. RNN: 순서 데이터 처리, h_t = tanh(W*x + W*h + b)
2. LSTM: 3개 게이트 + 셀 상태 → 장기 기억 가능
3. GRU: 2개 게이트, LSTM보다 간단하고 비슷한 성능
4. Embedding: 정수 ID → 밀집 벡터 (의미 표현)
5. PackedSequence: 가변 길이 시퀀스 효율적 처리
6. Bidirectional: 양방향으로 문맥 파악 → 출력 크기 2배

[주의] 흔한 실수:
   - batch_first 설정 안 함 → shape 불일치
   - 기울기 클리핑 안 함 → 기울기 폭발
   - 양방향 LSTM의 출력 크기 2*hidden_size 잊음
   - 패딩 토큰이 임베딩에서 0 벡터인지 확인 안 함
""")
