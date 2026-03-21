# #########################################################################
#
#   PyTorch 학습 02단계: nn.Module (신경망 모듈)
#   - nn.Module, nn.Linear, nn.Sequential, 파라미터 관리 -
#   # 실행 방법: python 02_nn_module.py (개념 학습용, PyTorch 없이 실행 가능)
#   # PyTorch 설치: pip install torch torchvision
#
# #########################################################################

import math
import random

random.seed(42)

# ===============================================================================
#  1. nn.Module이란?
# ===============================================================================
print("=" * 70)
print("Part 1: nn.Module 이해")
print("=" * 70)

print("""
nn.Module은 PyTorch에서 모든 신경망의 기본 클래스입니다.
모든 레이어, 모든 모델은 nn.Module을 상속합니다.

비유: nn.Module = "레고 블록의 기본 규격"
     모든 레고 블록이 같은 규격으로 만들어져서 자유롭게 조합할 수 있듯이,
     nn.Module을 상속하면 모든 레이어를 자유롭게 조합할 수 있습니다.

핵심 규칙 두 가지:
  1. __init__(): 레이어(부품)를 정의하는 곳
  2. forward(): 데이터가 레이어를 통과하는 순서를 정의하는 곳
""")


# -----------------------------------------------------------------------
#  순수 파이썬으로 nn.Module 구현
# -----------------------------------------------------------------------
class Module:
    """PyTorch nn.Module의 핵심 기능을 순수 파이썬으로 구현"""

    def __init__(self):
        self._modules = {}      # 하위 모듈들
        self._parameters = {}   # 파라미터들
        self.training = True    # 학습 모드

    def forward(self, x):
        """순전파 - 서브클래스에서 반드시 오버라이드"""
        raise NotImplementedError("forward()를 구현해야 합니다!")

    def __call__(self, *args, **kwargs):
        """model(input) 호출 시 forward()를 실행"""
        # 실제 PyTorch에서는 여기서 hook도 실행
        return self.forward(*args, **kwargs)

    def __setattr__(self, name, value):
        """속성 설정 시 Module/Parameter를 자동 등록"""
        if isinstance(value, Module):
            # 하위 모듈 자동 등록
            if '_modules' not in self.__dict__:
                self.__dict__['_modules'] = {}
            self.__dict__['_modules'][name] = value
        if isinstance(value, Parameter):
            if '_parameters' not in self.__dict__:
                self.__dict__['_parameters'] = {}
            self.__dict__['_parameters'][name] = value
        self.__dict__[name] = value

    def parameters(self):
        """모든 파라미터를 반환 (하위 모듈 포함)"""
        params = []
        for name, param in self._parameters.items():
            params.append(param)
        for name, module in self._modules.items():
            params.extend(module.parameters())
        return params

    def named_parameters(self):
        """이름과 함께 파라미터 반환"""
        params = []
        for name, param in self._parameters.items():
            params.append((name, param))
        for mod_name, module in self._modules.items():
            for name, param in module.named_parameters():
                params.append((f"{mod_name}.{name}", param))
        return params

    def train(self, mode=True):
        """학습 모드 설정"""
        self.training = mode
        for module in self._modules.values():
            module.train(mode)
        return self

    def eval(self):
        """평가 모드 설정"""
        return self.train(False)

    def __repr__(self):
        lines = [f"{self.__class__.__name__}("]
        for name, module in self._modules.items():
            lines.append(f"  ({name}): {module}")
        lines.append(")")
        return "\n".join(lines)


class Parameter:
    """학습 가능한 파라미터"""

    def __init__(self, data):
        self.data = data    # 실제 값
        self.grad = None    # 기울기

    def __repr__(self):
        return f"Parameter({self.data})"

    def zero_grad(self):
        self.grad = None


# ===============================================================================
#  2. nn.Linear (완전연결 레이어)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 2: nn.Linear (완전연결 레이어)")
print("=" * 70)

print("""
nn.Linear(in_features, out_features, bias=True)

수학: y = x @ W^T + b
     입력(in_features) → 출력(out_features)

비유: 환전소
     - 달러(in_features=1)를 넣으면 원화, 엔화, 유로화(out_features=3)가 나옴
     - 환율이 weight, 수수료가 bias
""")


class Linear(Module):
    """nn.Linear 구현: y = x @ W^T + b"""

    def __init__(self, in_features, out_features, bias=True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features

        # 가중치 초기화 (Kaiming uniform 간소화)
        k = 1.0 / math.sqrt(in_features)
        self.weight = Parameter(
            [[random.uniform(-k, k) for _ in range(in_features)]
             for _ in range(out_features)]
        )

        if bias:
            self.bias = Parameter([random.uniform(-k, k) for _ in range(out_features)])
        else:
            self.bias = None

    def forward(self, x):
        """
        x: (batch_size, in_features) 또는 (in_features,)
        출력: (batch_size, out_features)
        """
        # 입력이 1차원이면 2차원으로
        if not isinstance(x[0], list):
            x = [x]

        batch_size = len(x)
        output = []

        for i in range(batch_size):
            row = []
            for j in range(self.out_features):
                # y_j = sum(x_k * w_jk) + b_j
                val = sum(x[i][k] * self.weight.data[j][k]
                          for k in range(self.in_features))
                if self.bias is not None:
                    val += self.bias.data[j]
                row.append(val)
            output.append(row)

        return output if batch_size > 1 else output[0]

    def __repr__(self):
        return f"Linear(in_features={self.in_features}, out_features={self.out_features}, bias={self.bias is not None})"


# Linear 테스트
print("\n--- nn.Linear 테스트 ---")
linear = Linear(3, 2)
print(f"레이어: {linear}")
print(f"weight shape: ({linear.out_features}, {linear.in_features})")
print(f"bias shape: ({len(linear.bias.data)},)")

x = [1.0, 2.0, 3.0]
y = linear(x)
print(f"\n입력: {x}")
print(f"출력: {y}")

# 실제 PyTorch 코드:
# linear = nn.Linear(3, 2)
# print(linear)
# print(linear.weight.shape)  # torch.Size([2, 3])
# print(linear.bias.shape)    # torch.Size([2])
# x = torch.tensor([1.0, 2.0, 3.0])
# y = linear(x)               # tensor([...], grad_fn=<AddBackward0>)

# weight와 bias에 직접 접근
print("\n--- weight와 bias 접근 ---")
print(f"weight: {linear.weight}")
print(f"bias: {linear.bias}")
# 실제 PyTorch 코드:
# print(linear.weight)        # Parameter containing: tensor([...])
# print(linear.bias)          # Parameter containing: tensor([...])
# print(linear.weight.data)   # 값만 (기울기 추적 없이)


# ===============================================================================
#  3. nn.Sequential
# ===============================================================================
print("\n" + "=" * 70)
print("Part 3: nn.Sequential")
print("=" * 70)

print("""
nn.Sequential은 레이어를 순서대로 쌓는 컨테이너입니다.

비유: 공장의 컨베이어 벨트
     원재료(입력) → 가공1 → 가공2 → 가공3 → 완제품(출력)
     각 단계(레이어)를 순서대로 통과합니다.
""")


class ReLU(Module):
    """ReLU 활성화 함수: max(0, x)"""
    def __init__(self):
        super().__init__()

    def forward(self, x):
        if isinstance(x[0], list):
            return [[max(0, val) for val in row] for row in x]
        return [max(0, val) for val in x]

    def __repr__(self):
        return "ReLU()"


class Sigmoid(Module):
    """시그모이드 활성화 함수: 1 / (1 + exp(-x))"""
    def __init__(self):
        super().__init__()

    def forward(self, x):
        def _sigmoid(val):
            # overflow 방지
            if val >= 0:
                return 1.0 / (1.0 + math.exp(-val))
            else:
                exp_val = math.exp(val)
                return exp_val / (1.0 + exp_val)

        if isinstance(x, list) and len(x) > 0 and isinstance(x[0], list):
            return [[_sigmoid(val) for val in row] for row in x]
        elif isinstance(x, list):
            return [_sigmoid(val) for val in x]
        return _sigmoid(x)

    def __repr__(self):
        return "Sigmoid()"


class Tanh(Module):
    """Tanh 활성화 함수"""
    def __init__(self):
        super().__init__()

    def forward(self, x):
        if isinstance(x, list) and len(x) > 0 and isinstance(x[0], list):
            return [[math.tanh(val) for val in row] for row in x]
        elif isinstance(x, list):
            return [math.tanh(val) for val in x]
        return math.tanh(x)

    def __repr__(self):
        return "Tanh()"


class Sequential(Module):
    """nn.Sequential 구현: 레이어를 순서대로 실행"""

    def __init__(self, *layers):
        super().__init__()
        for i, layer in enumerate(layers):
            self._modules[str(i)] = layer

    def forward(self, x):
        for module in self._modules.values():
            x = module(x)
        return x

    def __repr__(self):
        lines = ["Sequential("]
        for name, module in self._modules.items():
            lines.append(f"  ({name}): {module}")
        lines.append(")")
        return "\n".join(lines)


# Sequential 테스트
print("\n--- Sequential로 모델 만들기 ---")
model = Sequential(
    Linear(2, 4),    # 입력 2 → 은닉 4
    ReLU(),
    Linear(4, 3),    # 은닉 4 → 은닉 3
    ReLU(),
    Linear(3, 1),    # 은닉 3 → 출력 1
    Sigmoid()
)

print(model)

x = [0.5, -0.3]
y = model(x)
print(f"\n입력: {x}")
print(f"출력: {y}")

# 실제 PyTorch 코드:
# model = nn.Sequential(
#     nn.Linear(2, 4),
#     nn.ReLU(),
#     nn.Linear(4, 3),
#     nn.ReLU(),
#     nn.Linear(3, 1),
#     nn.Sigmoid()
# )
# x = torch.tensor([0.5, -0.3])
# y = model(x)


# ===============================================================================
#  4. 파라미터 관리
# ===============================================================================
print("\n" + "=" * 70)
print("Part 4: 파라미터 관리")
print("=" * 70)

# parameters() - 모든 학습 가능한 파라미터
print("\n--- 모든 파라미터 ---")
all_params = model.parameters()
print(f"파라미터 수: {len(all_params)}")

# named_parameters() - 이름 포함
print("\n--- 이름이 있는 파라미터 ---")
for name, param in model.named_parameters():
    if isinstance(param.data[0], list):
        shape = f"({len(param.data)}, {len(param.data[0])})"
    else:
        shape = f"({len(param.data)},)"
    print(f"  {name}: shape={shape}")

# 파라미터 수 세기
def count_parameters(model):
    """학습 가능한 파라미터 총 수"""
    total = 0
    for param in model.parameters():
        if isinstance(param.data[0], list):
            total += len(param.data) * len(param.data[0])
        else:
            total += len(param.data)
    return total

total_params = count_parameters(model)
print(f"\n총 파라미터 수: {total_params}")

# 실제 PyTorch 코드:
# for name, param in model.named_parameters():
#     print(f"{name}: {param.shape}")
#
# total = sum(p.numel() for p in model.parameters())
# print(f"총 파라미터 수: {total}")
#
# # 학습 가능한 파라미터만 세기
# trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
# print(f"학습 가능 파라미터 수: {trainable}")


# ===============================================================================
#  5. 모델 출력과 호출 흐름
# ===============================================================================
print("\n" + "=" * 70)
print("Part 5: 모델 출력과 호출 흐름")
print("=" * 70)

print("""
model(input)을 호출하면 내부적으로:
  1. model.__call__(input) 실행
  2. __call__ 안에서 forward(input) 호출
  3. forward()에서 정의한 순서대로 레이어 통과

[주의] 주의: model.forward(input)을 직접 호출하지 마세요!
   model(input)으로 호출해야 hook 등이 제대로 동작합니다.
""")

print("호출 흐름 추적:")
print("  model([0.5, -0.3])")
print("  → model.__call__([0.5, -0.3])")
print("  → model.forward([0.5, -0.3])")
print("  → Linear(2→4) → ReLU → Linear(4→3) → ReLU → Linear(3→1) → Sigmoid")


# ===============================================================================
#  6. 커스텀 nn.Module 클래스 만들기
# ===============================================================================
print("\n" + "=" * 70)
print("Part 6: 커스텀 Module 클래스")
print("=" * 70)

print("""
복잡한 모델은 Sequential 대신 직접 Module을 상속하여 만듭니다.

nn.Module 상속 시 규칙:
  1. super().__init__() 호출 필수!
  2. __init__에서 레이어 정의
  3. forward()에서 연산 순서 정의
  4. backward()는 구현하지 않음 (autograd가 자동 처리)
""")


class CustomNet(Module):
    """커스텀 신경망 예제"""

    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.fc1 = Linear(input_size, hidden_size)
        self.relu = ReLU()
        self.fc2 = Linear(hidden_size, output_size)
        self.sigmoid = Sigmoid()

    def forward(self, x):
        x = self.fc1(x)        # 첫 번째 선형 변환
        x = self.relu(x)       # 활성화
        x = self.fc2(x)        # 두 번째 선형 변환
        x = self.sigmoid(x)    # 출력 활성화
        return x

custom_model = CustomNet(3, 5, 1)
print(custom_model)
print(f"\n총 파라미터: {count_parameters(custom_model)}")

test_input = [1.0, 0.5, -0.2]
test_output = custom_model(test_input)
print(f"입력: {test_input}")
print(f"출력: {test_output}")

# 실제 PyTorch 코드:
# class CustomNet(nn.Module):
#     def __init__(self, input_size, hidden_size, output_size):
#         super().__init__()      # 또는 super(CustomNet, self).__init__()
#         self.fc1 = nn.Linear(input_size, hidden_size)
#         self.relu = nn.ReLU()
#         self.fc2 = nn.Linear(hidden_size, output_size)
#         self.sigmoid = nn.Sigmoid()
#
#     def forward(self, x):
#         x = self.fc1(x)
#         x = self.relu(x)
#         x = self.fc2(x)
#         x = self.sigmoid(x)
#         return x
#
# model = CustomNet(3, 5, 1)
# print(model)
# x = torch.randn(1, 3)
# y = model(x)


# ===============================================================================
#  7. 실습: XOR 문제 풀기
# ===============================================================================
print("\n" + "=" * 70)
print("Part 7: 실습 - XOR 문제 풀기")
print("=" * 70)

print("""
XOR 문제: 선형 모델로는 풀 수 없는 대표적인 문제
  입력      출력
  (0, 0) → 0
  (0, 1) → 1
  (1, 0) → 1
  (1, 1) → 0

비유: "둘 다 같으면 0, 다르면 1"
     단순한 직선 하나로는 구분 불가능 → 은닉층이 필요!
""")

# XOR 데이터
xor_data = [
    ([0.0, 0.0], 0.0),
    ([0.0, 1.0], 1.0),
    ([1.0, 0.0], 1.0),
    ([1.0, 1.0], 0.0),
]


class XORNet(Module):
    """XOR을 풀기 위한 신경망"""

    def __init__(self):
        super().__init__()
        self.fc1 = Linear(2, 4)    # 2 → 4 (은닉층)
        self.fc2 = Linear(4, 1)    # 4 → 1 (출력층)

    def forward(self, x):
        h = self.fc1(x)
        h = [max(0, val) for val in h]  # ReLU
        out = self.fc2(h)
        # Sigmoid
        out_val = out[0] if isinstance(out, list) else out
        sig = 1.0 / (1.0 + math.exp(-max(-500, min(500, out_val))))
        return sig


# 학습
xor_model = XORNet()
lr = 0.5
print(f"학습률: {lr}")
print("\n--- XOR 학습 시작 ---")

for epoch in range(2000):
    total_loss = 0.0

    for x, y_true in xor_data:
        # 순전파
        y_pred = xor_model(x)

        # BCE Loss (Binary Cross Entropy) 수동 계산
        eps = 1e-7
        loss = -(y_true * math.log(y_pred + eps) + (1 - y_true) * math.log(1 - y_pred + eps))
        total_loss += loss

        # 수치 미분으로 기울기 계산 (간소화)
        h = 1e-5
        for param in xor_model.parameters():
            if isinstance(param.data[0], list):
                for i in range(len(param.data)):
                    for j in range(len(param.data[i])):
                        original = param.data[i][j]
                        param.data[i][j] = original + h
                        loss_plus = 0.0
                        for x2, y2 in xor_data:
                            p = xor_model(x2)
                            loss_plus += -(y2 * math.log(p + eps) + (1 - y2) * math.log(1 - p + eps))
                        param.data[i][j] = original - h
                        loss_minus = 0.0
                        for x2, y2 in xor_data:
                            p = xor_model(x2)
                            loss_minus += -(y2 * math.log(p + eps) + (1 - y2) * math.log(1 - p + eps))
                        param.data[i][j] = original
                        grad = (loss_plus - loss_minus) / (2 * h)
                        param.data[i][j] -= lr * grad / len(xor_data)
            else:
                for i in range(len(param.data)):
                    original = param.data[i]
                    param.data[i] = original + h
                    loss_plus = 0.0
                    for x2, y2 in xor_data:
                        p = xor_model(x2)
                        loss_plus += -(y2 * math.log(p + eps) + (1 - y2) * math.log(1 - p + eps))
                    param.data[i] = original - h
                    loss_minus = 0.0
                    for x2, y2 in xor_data:
                        p = xor_model(x2)
                        loss_minus += -(y2 * math.log(p + eps) + (1 - y2) * math.log(1 - p + eps))
                    param.data[i] = original
                    grad = (loss_plus - loss_minus) / (2 * h)
                    param.data[i] -= lr * grad / len(xor_data)
        break  # 수치 미분은 한 번만 (전체 배치)

    if epoch % 400 == 0:
        avg_loss = total_loss / len(xor_data)
        print(f"  Epoch {epoch:4d}: loss={avg_loss:.4f}")

print("\n--- XOR 예측 결과 ---")
for x, y_true in xor_data:
    y_pred = xor_model(x)
    print(f"  입력: {x} → 예측: {y_pred:.4f} (정답: {y_true})")

print("""
참고: 순수 파이썬의 수치 미분은 매우 느리고 부정확합니다.
실제 PyTorch에서는 autograd가 정확하고 빠르게 기울기를 계산합니다.
""")

# 실제 PyTorch 코드:
# class XORNet(nn.Module):
#     def __init__(self):
#         super().__init__()
#         self.fc1 = nn.Linear(2, 4)
#         self.fc2 = nn.Linear(4, 1)
#
#     def forward(self, x):
#         x = torch.relu(self.fc1(x))
#         x = torch.sigmoid(self.fc2(x))
#         return x
#
# model = XORNet()
# criterion = nn.BCELoss()
# optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
#
# X = torch.tensor([[0,0],[0,1],[1,0],[1,1]], dtype=torch.float32)
# Y = torch.tensor([[0],[1],[1],[0]], dtype=torch.float32)
#
# for epoch in range(2000):
#     y_pred = model(X)
#     loss = criterion(y_pred, Y)
#     optimizer.zero_grad()
#     loss.backward()
#     optimizer.step()
#
# with torch.no_grad():
#     predictions = model(X)
#     print(predictions.round())


# ===============================================================================
#  8. train() vs eval() 모드
# ===============================================================================
print("\n" + "=" * 70)
print("Part 8: train() vs eval() 모드")
print("=" * 70)

print("""
model.train(): 학습 모드 (기본값)
  - Dropout이 활성화됨 (일부 뉴런 무작위 비활성화)
  - BatchNorm이 현재 배치의 통계 사용

model.eval(): 평가 모드
  - Dropout 비활성화 (모든 뉴런 사용)
  - BatchNorm이 학습 중 축적된 통계 사용

[주의] 주의: 추론(예측) 시에는 반드시 model.eval() 호출!
""")

test_model = CustomNet(3, 5, 1)
print(f"기본 모드 (training): {test_model.training}")
test_model.eval()
print(f"eval() 후 (training): {test_model.training}")
test_model.train()
print(f"train() 후 (training): {test_model.training}")

# 실제 PyTorch 코드:
# model.train()     # 학습 모드
# # ... 학습 ...
#
# model.eval()      # 평가 모드
# with torch.no_grad():   # 기울기 계산도 끄기
#     predictions = model(test_data)


# ===============================================================================
#  핵심 정리
# ===============================================================================
print("\n" + "=" * 70)
print("핵심 정리")
print("=" * 70)
print("""
1. nn.Module = 모든 신경망의 기본 클래스 (레고 블록의 규격)
2. __init__(): 레이어 정의, forward(): 연산 순서 정의
3. nn.Linear(in, out): 완전연결 레이어, y = xW^T + b
4. nn.Sequential: 레이어를 순서대로 쌓는 컨테이너
5. model.parameters(): 모든 학습 가능 파라미터 접근
6. model.named_parameters(): 이름 + 파라미터 접근
7. model(x)로 호출 (model.forward(x) 직접 호출 금지!)
8. model.train() / model.eval(): 학습/평가 모드 전환

[주의] 흔한 실수:
   - super().__init__() 호출 안 하기 → 에러
   - forward() 대신 backward() 구현 → autograd가 자동 처리
   - eval() 안 하고 추론 → Dropout/BatchNorm 결과 달라짐
""")
