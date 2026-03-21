# #########################################################################
#
#   PyTorch 학습 09단계: 고급 아키텍처
#   - ResNet, Attention, Transformer, U-Net -
#   # 실행 방법: python 09_advanced_architectures.py (개념 학습용, PyTorch 없이 실행 가능)
#   # PyTorch 설치: pip install torch torchvision
#
# #########################################################################

import math
import random

random.seed(42)

# ===============================================================================
#  1. ResNet - 잔차 연결 (Residual Connection)
# ===============================================================================
print("=" * 70)
print("Part 1: ResNet (잔차 네트워크)")
print("=" * 70)

print("""
ResNet(2015)의 핵심 아이디어: 잔차 연결 (Skip Connection)

문제: 네트워크가 깊어지면 성능이 오히려 떨어짐 (기울기 소실/폭발)
해결: 입력을 출력에 직접 더해줌!

일반 블록:    F(x)      → 학습해야 할 것: 전체 변환
잔차 블록:    F(x) + x  → 학습해야 할 것: 잔차(변화량)만!

비유: 시험 점수 예측
  - 일반: "학생 A의 점수는 85점이다" (절대값 예측)
  - 잔차: "학생 A는 평균보다 +5점이다" (변화량 예측 → 더 쉬움!)

왜 더 잘 작동하나?
  - F(x) = 0이면 → 출력 = x (항등 함수, 최소한 입력은 유지)
  - 기울기가 shortcut을 통해 직접 전달 → 기울기 소실 완화
""")


class ResidualBlock:
    """잔차 블록 구현"""

    def __init__(self, size):
        self.size = size
        k = 1.0 / math.sqrt(size)
        # 두 개의 선형 변환
        self.w1 = [[random.uniform(-k, k) for _ in range(size)] for _ in range(size)]
        self.b1 = [random.uniform(-k, k) for _ in range(size)]
        self.w2 = [[random.uniform(-k, k) for _ in range(size)] for _ in range(size)]
        self.b2 = [random.uniform(-k, k) for _ in range(size)]

    def forward(self, x):
        # 잔차 경로: F(x)
        h = self._linear(x, self.w1, self.b1)
        h = [max(0, val) for val in h]  # ReLU
        h = self._linear(h, self.w2, self.b2)

        # 잔차 연결: F(x) + x
        out = [h[i] + x[i] for i in range(self.size)]

        # 최종 ReLU
        out = [max(0, val) for val in out]
        return out

    def _linear(self, x, w, b):
        return [sum(w[i][j] * x[j] for j in range(len(x))) + b[i]
                for i in range(len(w))]


# ResNet 블록 테스트
print("\n--- 잔차 블록 테스트 ---")
block = ResidualBlock(4)
x = [1.0, -0.5, 0.3, 0.8]
out = block.forward(x)

print(f"입력 x: {x}")
print(f"출력 F(x) + x: [{', '.join(f'{v:.4f}' for v in out)}]")
print(f"→ 입력 x가 출력에 직접 더해지므로 정보가 보존됩니다!")

# 깊은 네트워크 시뮬레이션
print("\n--- 잔차 연결 효과 (신호 전파) ---")

def pass_through_blocks(x, num_blocks, use_residual=True):
    """여러 블록을 통과하며 신호 크기 추적"""
    signal_norms = [math.sqrt(sum(v**2 for v in x))]
    for _ in range(num_blocks):
        # 변환 (간소화)
        fx = [v * 0.9 + random.gauss(0, 0.1) for v in x]
        if use_residual:
            x = [fx[i] + x[i] for i in range(len(x))]  # F(x) + x
        else:
            x = fx  # F(x) only
        signal_norms.append(math.sqrt(sum(v**2 for v in x)))
    return signal_norms

x0 = [1.0, 0.5, -0.3, 0.8]
norms_residual = pass_through_blocks(x0[:], 10, use_residual=True)
norms_plain = pass_through_blocks(x0[:], 10, use_residual=False)

print(f"\n{'블록':>4} {'잔차 있음':>12} {'잔차 없음':>12}")
print("-" * 32)
for i in range(0, 11, 2):
    print(f"{i:>4} {norms_residual[i]:>12.4f} {norms_plain[i]:>12.4f}")

print("→ 잔차 연결이 있으면 깊은 네트워크에서도 신호가 유지됩니다!")

# 실제 PyTorch 코드:
# class ResidualBlock(nn.Module):
#     def __init__(self, channels):
#         super().__init__()
#         self.conv1 = nn.Conv2d(channels, channels, 3, padding=1)
#         self.bn1 = nn.BatchNorm2d(channels)
#         self.conv2 = nn.Conv2d(channels, channels, 3, padding=1)
#         self.bn2 = nn.BatchNorm2d(channels)
#
#     def forward(self, x):
#         residual = x                          # shortcut
#         out = F.relu(self.bn1(self.conv1(x)))
#         out = self.bn2(self.conv2(out))
#         out += residual                        # 잔차 연결!
#         out = F.relu(out)
#         return out


# ===============================================================================
#  2. Self-Attention (자기 주의)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 2: Self-Attention")
print("=" * 70)

print("""
Attention = "어디에 주목할지" 결정하는 메커니즘

비유: 교실에서 선생님이 질문했을 때
  - 각 학생이 다른 학생들을 둘러보고
  - "이 질문에 답하려면 누구의 정보가 필요한지" 판단
  - 관련 있는 학생에게 더 많은 주의(가중치)를 줌

핵심 개념 (Query, Key, Value):
  Q (Query): "내가 찾고 있는 것" (질문)
  K (Key):   "내가 가진 정보의 레이블" (색인)
  V (Value): "실제 정보" (내용)

수식: Attention(Q, K, V) = softmax(Q @ K^T / sqrt(d_k)) @ V
  - Q @ K^T: 유사도 계산 (어떤 키가 쿼리와 관련 있는지)
  - / sqrt(d_k): 스케일링 (값이 너무 커지는 것 방지)
  - softmax: 확률로 변환 (가중치 합 = 1)
  - @ V: 가중합으로 값 추출
""")


def softmax(logits):
    """수치 안정 Softmax"""
    max_val = max(logits)
    exp_vals = [math.exp(x - max_val) for x in logits]
    total = sum(exp_vals)
    return [e / total for e in exp_vals]


def scaled_dot_product_attention(Q, K, V):
    """스케일드 닷 프로덕트 어텐션 구현

    Q: (seq_len, d_k) - 쿼리
    K: (seq_len, d_k) - 키
    V: (seq_len, d_v) - 값
    """
    seq_len = len(Q)
    d_k = len(Q[0])

    # 1. Q @ K^T → (seq_len, seq_len) 유사도 행렬
    scores = [[0.0] * seq_len for _ in range(seq_len)]
    for i in range(seq_len):
        for j in range(seq_len):
            scores[i][j] = sum(Q[i][k] * K[j][k] for k in range(d_k))

    # 2. 스케일링: / sqrt(d_k)
    scale = math.sqrt(d_k)
    scores = [[s / scale for s in row] for row in scores]

    # 3. Softmax (각 행마다)
    attn_weights = [softmax(row) for row in scores]

    # 4. @ V → (seq_len, d_v)
    d_v = len(V[0])
    output = [[0.0] * d_v for _ in range(seq_len)]
    for i in range(seq_len):
        for j in range(d_v):
            output[i][j] = sum(attn_weights[i][k] * V[k][j] for k in range(seq_len))

    return output, attn_weights


# Self-Attention 테스트
print("\n--- Self-Attention 테스트 ---")

# 3개의 단어, 각 4차원 임베딩
# "나는"(0) "고양이를"(1) "좋아한다"(2)
embeddings = [
    [1.0, 0.5, -0.2, 0.8],   # "나는"
    [0.3, 1.2, 0.7, -0.1],   # "고양이를"
    [0.8, -0.3, 1.0, 0.5],   # "좋아한다"
]

# Self-Attention: Q=K=V=입력 (자기 자신에게 주의)
output, weights = scaled_dot_product_attention(embeddings, embeddings, embeddings)

print("입력 (3 단어, 4차원):")
words = ["나는", "고양이를", "좋아한다"]
for w, e in zip(words, embeddings):
    print(f"  {w:8s}: [{', '.join(f'{v:6.3f}' for v in e)}]")

print("\n어텐션 가중치 (각 단어가 다른 단어에 주목하는 정도):")
print(f"{'':>12}", end="")
for w in words:
    print(f"{w:>10}", end="")
print()
for i, w in enumerate(words):
    print(f"  {w:>8}:", end="")
    for j in range(len(words)):
        print(f"{weights[i][j]:>10.4f}", end="")
    print()

print("\n출력 (문맥 반영된 표현):")
for w, o in zip(words, output):
    print(f"  {w:8s}: [{', '.join(f'{v:6.3f}' for v in o)}]")


# ===============================================================================
#  3. Multi-Head Attention
# ===============================================================================
print("\n" + "=" * 70)
print("Part 3: Multi-Head Attention")
print("=" * 70)

print("""
Multi-Head Attention = 여러 개의 Attention을 병렬로 수행

비유: 영화 평론
  - Head 1: 연기에 주목
  - Head 2: 스토리에 주목
  - Head 3: 영상미에 주목
  → 각 헤드가 다른 측면에 주의를 기울여 종합적 판단

수식:
  MultiHead(Q, K, V) = Concat(head_1, ..., head_h) @ W_O
  head_i = Attention(Q @ W_Q_i, K @ W_K_i, V @ W_V_i)
""")

def multi_head_attention_sim(embeddings, num_heads=2, d_model=4):
    """멀티헤드 어텐션 시뮬레이션"""
    d_k = d_model // num_heads  # 각 헤드의 차원
    all_head_outputs = []

    for head in range(num_heads):
        # 각 헤드에 대해 Q, K, V를 변환 (간소화: 원본 슬라이싱)
        start = head * d_k
        end = start + d_k

        Q = [[row[start:end][j] if j < len(row[start:end]) else random.gauss(0, 0.5)
              for j in range(d_k)] for row in embeddings]
        K = [[row[start:end][j] if j < len(row[start:end]) else random.gauss(0, 0.5)
              for j in range(d_k)] for row in embeddings]
        V = [[row[start:end][j] if j < len(row[start:end]) else random.gauss(0, 0.5)
              for j in range(d_k)] for row in embeddings]

        head_out, head_weights = scaled_dot_product_attention(Q, K, V)
        all_head_outputs.append((head_out, head_weights))

    return all_head_outputs

heads = multi_head_attention_sim(embeddings, num_heads=2)
for i, (out, weights) in enumerate(heads):
    print(f"\n  Head {i+1} 어텐션 가중치:")
    for j, w in enumerate(words):
        print(f"    {w}: [{', '.join(f'{v:.3f}' for v in weights[j])}]")

print("\n→ 각 헤드가 서로 다른 패턴에 주목할 수 있습니다!")

# 실제 PyTorch 코드:
# attn = nn.MultiheadAttention(embed_dim=512, num_heads=8)
# # 입력: (seq_len, batch, embed_dim)
# output, attn_weights = attn(query, key, value)


# ===============================================================================
#  4. Transformer
# ===============================================================================
print("\n" + "=" * 70)
print("Part 4: Transformer")
print("=" * 70)

print("""
Transformer (2017, "Attention Is All You Need")
  - RNN 없이 Attention만으로 시퀀스 처리
  - 병렬 처리 가능 → RNN보다 훨씬 빠름
  - NLP의 패러다임을 바꿈 (BERT, GPT 등의 기반)

Transformer Encoder 블록 구성:
  +-------------------------+
  |  Multi-Head Attention   |
  |  + Add & LayerNorm      | ← 잔차 연결 + 정규화
  |  -----------------      |
  |  Feed Forward Network   |
  |  + Add & LayerNorm      | ← 잔차 연결 + 정규화
  +-------------------------+

Transformer Decoder 블록 (추가):
  - Masked Self-Attention (미래 토큰 가림)
  - Cross-Attention (인코더 출력 참조)
  - Feed Forward Network
""")


class LayerNorm:
    """Layer Normalization 구현"""

    def __init__(self, size, eps=1e-6):
        self.size = size
        self.eps = eps
        self.gamma = [1.0] * size
        self.beta = [0.0] * size

    def __call__(self, x):
        mean = sum(x) / len(x)
        var = sum((v - mean) ** 2 for v in x) / len(x)
        return [(self.gamma[i] * (x[i] - mean) / math.sqrt(var + self.eps) + self.beta[i])
                for i in range(len(x))]


class FeedForward:
    """Feed Forward Network (FFN)"""

    def __init__(self, d_model, d_ff):
        k = 1.0 / math.sqrt(d_model)
        self.w1 = [[random.uniform(-k, k) for _ in range(d_model)] for _ in range(d_ff)]
        self.b1 = [0.0] * d_ff
        self.w2 = [[random.uniform(-k, k) for _ in range(d_ff)] for _ in range(d_model)]
        self.b2 = [0.0] * d_model

    def __call__(self, x):
        # Linear1 + ReLU
        h = [max(0, sum(self.w1[i][j] * x[j] for j in range(len(x))) + self.b1[i])
             for i in range(len(self.w1))]
        # Linear2
        out = [sum(self.w2[i][j] * h[j] for j in range(len(h))) + self.b2[i]
               for i in range(len(self.w2))]
        return out


class TransformerEncoderBlock:
    """Transformer Encoder 블록 구현"""

    def __init__(self, d_model, d_ff=None):
        if d_ff is None:
            d_ff = d_model * 4
        self.d_model = d_model
        self.norm1 = LayerNorm(d_model)
        self.norm2 = LayerNorm(d_model)
        self.ffn = FeedForward(d_model, d_ff)

    def forward(self, x_sequence):
        """
        x_sequence: [(d_model,), (d_model,), ...] - 시퀀스
        """
        # 1. Self-Attention + 잔차 연결 + LayerNorm
        attn_out, _ = scaled_dot_product_attention(x_sequence, x_sequence, x_sequence)
        x_sequence = [self.norm1([attn_out[i][j] + x_sequence[i][j]
                                  for j in range(self.d_model)])
                      for i in range(len(x_sequence))]

        # 2. FFN + 잔차 연결 + LayerNorm
        ffn_out = [self.ffn(x) for x in x_sequence]
        x_sequence = [self.norm2([ffn_out[i][j] + x_sequence[i][j]
                                  for j in range(self.d_model)])
                      for i in range(len(x_sequence))]

        return x_sequence


# Transformer 블록 테스트
print("\n--- Transformer Encoder 블록 테스트 ---")
d_model = 4
encoder_block = TransformerEncoderBlock(d_model=d_model, d_ff=8)

input_seq = embeddings  # 3 단어, 4차원
output_seq = encoder_block.forward(input_seq)

print(f"입력 (3 토큰, {d_model}차원):")
for w, e in zip(words, input_seq):
    print(f"  {w}: [{', '.join(f'{v:7.4f}' for v in e)}]")

print(f"\n출력 (Transformer Encoder 통과):")
for w, o in zip(words, output_seq):
    print(f"  {w}: [{', '.join(f'{v:7.4f}' for v in o)}]")


# ===============================================================================
#  5. Positional Encoding
# ===============================================================================
print("\n" + "=" * 70)
print("Part 5: Positional Encoding (위치 인코딩)")
print("=" * 70)

print("""
Transformer는 순서를 모릅니다! (RNN과 달리)
→ 위치 정보를 직접 주입해야 합니다.

Sinusoidal Positional Encoding:
  PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
  PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))

서로 다른 위치는 서로 다른 패턴을 가지며,
상대적 위치도 학습할 수 있는 구조입니다.
""")

def positional_encoding(max_len, d_model):
    """Sinusoidal Positional Encoding"""
    pe = [[0.0] * d_model for _ in range(max_len)]
    for pos in range(max_len):
        for i in range(0, d_model, 2):
            angle = pos / (10000 ** (i / d_model))
            pe[pos][i] = math.sin(angle)
            if i + 1 < d_model:
                pe[pos][i + 1] = math.cos(angle)
    return pe

pe = positional_encoding(max_len=6, d_model=8)
print("\n위치 인코딩 (6 위치, 8차원):")
for pos in range(6):
    print(f"  위치 {pos}: [{', '.join(f'{v:7.4f}' for v in pe[pos])}]")

print("\n→ 각 위치마다 고유한 패턴을 가집니다!")

# 실제 PyTorch 코드:
# # PyTorch 내장 Transformer
# encoder_layer = nn.TransformerEncoderLayer(
#     d_model=512, nhead=8, dim_feedforward=2048, dropout=0.1
# )
# transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=6)
#
# decoder_layer = nn.TransformerDecoderLayer(
#     d_model=512, nhead=8, dim_feedforward=2048, dropout=0.1
# )
# transformer_decoder = nn.TransformerDecoder(decoder_layer, num_layers=6)
#
# # 전체 Transformer
# transformer = nn.Transformer(d_model=512, nhead=8, num_encoder_layers=6,
#                              num_decoder_layers=6)


# ===============================================================================
#  6. U-Net 개념
# ===============================================================================
print("\n" + "=" * 70)
print("Part 6: U-Net (인코더-디코더 + Skip Connection)")
print("=" * 70)

print("""
U-Net (2015): 이미지 분할(segmentation)을 위한 아키텍처

구조가 U자 형태:
  인코더(왼쪽)          디코더(오른쪽)
  +---------+          +---------+
  | Conv+Pool| --skip-- |UpConv+  |
  | (축소)   |   연결   | (확대)  |
  +----+----+          +----+----+
       ↓                    ↑
  +----+----+          +----+----+
  | Conv+Pool| --skip-- |UpConv+  |
  +----+----+          +----+----+
       ↓                    ↑
       +---- Bottleneck ----+

Skip Connection의 역할:
  - 인코더의 세밀한 정보(가장자리, 질감)를 디코더에 직접 전달
  - 다운샘플링으로 잃어버린 공간 정보 복원
""")


class UNetSimulator:
    """U-Net 구조 시뮬레이션"""

    def trace(self, input_h=256, input_ch=3, num_classes=2):
        print(f"\n  U-Net 구조 (입력: {input_ch}x{input_h}x{input_h}):")
        print(f"\n  === 인코더 (다운샘플링) ===")

        h = input_h
        channels = [64, 128, 256, 512, 1024]

        # 인코더
        enc_sizes = []
        ch = input_ch
        for i, out_ch in enumerate(channels[:-1]):
            print(f"  Block {i+1}: Conv({ch}→{out_ch}) → ({out_ch}, {h}, {h})")
            enc_sizes.append((out_ch, h))
            h //= 2
            ch = out_ch
            print(f"           MaxPool → ({ch}, {h}, {h})")

        # 바닥 (Bottleneck)
        print(f"\n  === Bottleneck ===")
        print(f"  Conv({ch}→{channels[-1]}) → ({channels[-1]}, {h}, {h})")
        ch = channels[-1]

        # 디코더
        print(f"\n  === 디코더 (업샘플링 + Skip) ===")
        for i in range(len(enc_sizes) - 1, -1, -1):
            skip_ch, skip_h = enc_sizes[i]
            h *= 2
            ch = ch // 2
            print(f"  UpConv({ch*2}→{ch}) + Skip({skip_ch}) → ({ch + skip_ch}, {h}, {h})")
            print(f"  Conv({ch + skip_ch}→{ch}) → ({ch}, {h}, {h})")

        # 최종 출력
        print(f"\n  === 출력 ===")
        print(f"  Conv1x1({ch}→{num_classes}) → ({num_classes}, {h}, {h})")
        print(f"  → 각 픽셀이 {num_classes}개 클래스 중 하나로 분류됨!")


unet = UNetSimulator()
unet.trace(input_h=256, input_ch=3, num_classes=2)

# 실제 PyTorch 코드:
# class UNet(nn.Module):
#     def __init__(self, in_channels, num_classes):
#         super().__init__()
#         # 인코더
#         self.enc1 = self.conv_block(in_channels, 64)
#         self.enc2 = self.conv_block(64, 128)
#         self.enc3 = self.conv_block(128, 256)
#         self.pool = nn.MaxPool2d(2)
#
#         # 바닥
#         self.bottleneck = self.conv_block(256, 512)
#
#         # 디코더
#         self.up3 = nn.ConvTranspose2d(512, 256, 2, stride=2)
#         self.dec3 = self.conv_block(512, 256)  # 256(up) + 256(skip) = 512
#         self.up2 = nn.ConvTranspose2d(256, 128, 2, stride=2)
#         self.dec2 = self.conv_block(256, 128)
#         self.up1 = nn.ConvTranspose2d(128, 64, 2, stride=2)
#         self.dec1 = self.conv_block(128, 64)
#
#         self.final = nn.Conv2d(64, num_classes, 1)
#
#     def conv_block(self, in_ch, out_ch):
#         return nn.Sequential(
#             nn.Conv2d(in_ch, out_ch, 3, padding=1),
#             nn.BatchNorm2d(out_ch),
#             nn.ReLU(),
#             nn.Conv2d(out_ch, out_ch, 3, padding=1),
#             nn.BatchNorm2d(out_ch),
#             nn.ReLU(),
#         )
#
#     def forward(self, x):
#         # 인코더
#         e1 = self.enc1(x)
#         e2 = self.enc2(self.pool(e1))
#         e3 = self.enc3(self.pool(e2))
#
#         # 바닥
#         b = self.bottleneck(self.pool(e3))
#
#         # 디코더 + Skip Connection
#         d3 = self.dec3(torch.cat([self.up3(b), e3], dim=1))
#         d2 = self.dec2(torch.cat([self.up2(d3), e2], dim=1))
#         d1 = self.dec1(torch.cat([self.up1(d2), e1], dim=1))
#
#         return self.final(d1)


# ===============================================================================
#  7. 실습: 간단한 Transformer 블록 구현
# ===============================================================================
print("\n" + "=" * 70)
print("Part 7: 실습 - Transformer 분류기")
print("=" * 70)

print("Transformer Encoder를 사용한 시퀀스 분류 (시뮬레이션)")


class TransformerClassifier:
    """Transformer 기반 분류기"""

    def __init__(self, vocab_size, d_model, num_heads, num_classes, max_len=50):
        self.d_model = d_model

        # 임베딩
        self.embed_table = [[random.gauss(0, 1) for _ in range(d_model)]
                            for _ in range(vocab_size)]

        # 위치 인코딩
        self.pe = positional_encoding(max_len, d_model)

        # Transformer Encoder 블록
        self.encoder = TransformerEncoderBlock(d_model, d_ff=d_model * 2)

        # 분류 헤드
        k = 1.0 / math.sqrt(d_model)
        self.cls_w = [[random.uniform(-k, k) for _ in range(d_model)]
                      for _ in range(num_classes)]
        self.cls_b = [0.0] * num_classes

    def forward(self, token_ids):
        # 1. 임베딩 + 위치 인코딩
        seq = []
        for pos, tid in enumerate(token_ids):
            embed = self.embed_table[tid]
            pe = self.pe[pos]
            combined = [embed[i] + pe[i] for i in range(self.d_model)]
            seq.append(combined)

        # 2. Transformer Encoder
        encoded = self.encoder.forward(seq)

        # 3. 평균 풀링 (모든 토큰의 평균)
        pooled = [sum(encoded[t][d] for t in range(len(encoded))) / len(encoded)
                  for d in range(self.d_model)]

        # 4. 분류
        logits = [sum(self.cls_w[c][d] * pooled[d] for d in range(self.d_model)) + self.cls_b[c]
                  for c in range(len(self.cls_w))]

        return logits


# 테스트
print("\n--- Transformer 분류기 테스트 ---")
clf = TransformerClassifier(vocab_size=100, d_model=8, num_heads=2, num_classes=3)

sample_ids = [5, 23, 42, 7, 15]
logits = clf.forward(sample_ids)
probs = softmax(logits)

print(f"입력 토큰 IDs: {sample_ids}")
print(f"로짓: [{', '.join(f'{v:.4f}' for v in logits)}]")
print(f"확률: [{', '.join(f'{v:.4f}' for v in probs)}]")
print(f"예측 클래스: {probs.index(max(probs))}")


# ===============================================================================
#  핵심 정리
# ===============================================================================
print("\n" + "=" * 70)
print("핵심 정리")
print("=" * 70)
print("""
1. ResNet: 잔차 연결 (F(x) + x)
   → 깊은 네트워크 학습 가능, 기울기 소실 해결

2. Self-Attention: Q, K, V로 "어디에 주목할지" 결정
   → softmax(Q @ K^T / sqrt(d_k)) @ V

3. Multi-Head Attention: 여러 관점에서 동시에 주목
   → 각 헤드가 다른 패턴 학습

4. Transformer: Attention + FFN + LayerNorm + 잔차 연결
   → 병렬 처리, RNN보다 빠르고 강력

5. Positional Encoding: 위치 정보 주입 (sin/cos)
   → Transformer는 순서를 모르므로 필수

6. U-Net: 인코더-디코더 + Skip Connection
   → 이미지 분할에 강력 (세밀한 정보 보존)

현대 딥러닝의 핵심: Transformer + 잔차 연결 + Attention
  → GPT, BERT, ViT, Stable Diffusion 모두 이 조합!
""")
