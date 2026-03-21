# #########################################################################
#
#   PyTorch 학습 07단계: 학습 트릭과 기법
#   - 가중치 초기화, Gradient Clipping, 조기 종료, 체크포인트, AMP -
#   # 실행 방법: python 07_training_tricks.py (개념 학습용, PyTorch 없이 실행 가능)
#   # PyTorch 설치: pip install torch torchvision
#
# #########################################################################

import math
import random
import json
import os

random.seed(42)

# ===============================================================================
#  1. 가중치 초기화 (Weight Initialization)
# ===============================================================================
print("=" * 70)
print("Part 1: 가중치 초기화")
print("=" * 70)

print("""
가중치 초기화 = 학습 시작 전 파라미터의 초기값 설정

왜 중요한가?
  - 0으로 초기화 → 모든 뉴런이 같은 값 → 대칭 문제 (학습 불가)
  - 너무 크게 → 기울기 폭발 → NaN 발생
  - 너무 작게 → 기울기 소실 → 학습 안 됨

비유: 등산 출발점
  - 좋은 출발점 → 정상에 빨리 도착
  - 나쁜 출발점 → 헤매거나 포기
""")


# --- Xavier (Glorot) 초기화 ---
print("\n--- Xavier 초기화 ---")
print("활성화 함수: sigmoid, tanh에 적합")
print("수식: std = sqrt(2 / (fan_in + fan_out))")

def xavier_uniform(fan_in, fan_out):
    """Xavier 균일 초기화"""
    limit = math.sqrt(6.0 / (fan_in + fan_out))
    return [[random.uniform(-limit, limit) for _ in range(fan_out)]
            for _ in range(fan_in)]

def xavier_normal(fan_in, fan_out):
    """Xavier 정규 초기화"""
    std = math.sqrt(2.0 / (fan_in + fan_out))
    return [[random.gauss(0, std) for _ in range(fan_out)]
            for _ in range(fan_in)]

# 테스트
w_xavier = xavier_uniform(256, 128)
values = [w_xavier[i][j] for i in range(len(w_xavier)) for j in range(len(w_xavier[0]))]
print(f"\nXavier Uniform (256, 128):")
print(f"  범위: [{min(values):.4f}, {max(values):.4f}]")
print(f"  평균: {sum(values)/len(values):.6f}")
print(f"  표준편차: {(sum((v - sum(values)/len(values))**2 for v in values)/len(values))**0.5:.4f}")

# 실제 PyTorch 코드:
# nn.init.xavier_uniform_(layer.weight)
# nn.init.xavier_normal_(layer.weight)


# --- He (Kaiming) 초기화 ---
print("\n--- He (Kaiming) 초기화 ---")
print("활성화 함수: ReLU에 적합 (현재 가장 많이 사용)")
print("수식: std = sqrt(2 / fan_in)")

def he_uniform(fan_in, fan_out):
    """He 균일 초기화"""
    limit = math.sqrt(6.0 / fan_in)
    return [[random.uniform(-limit, limit) for _ in range(fan_out)]
            for _ in range(fan_in)]

def he_normal(fan_in, fan_out):
    """He 정규 초기화"""
    std = math.sqrt(2.0 / fan_in)
    return [[random.gauss(0, std) for _ in range(fan_out)]
            for _ in range(fan_in)]

w_he = he_normal(256, 128)
values = [w_he[i][j] for i in range(len(w_he)) for j in range(len(w_he[0]))]
print(f"\nHe Normal (256, 128):")
print(f"  범위: [{min(values):.4f}, {max(values):.4f}]")
print(f"  평균: {sum(values)/len(values):.6f}")
print(f"  표준편차: {(sum((v - sum(values)/len(values))**2 for v in values)/len(values))**0.5:.4f}")

# 실제 PyTorch 코드:
# nn.init.kaiming_uniform_(layer.weight, mode='fan_in', nonlinearity='relu')
# nn.init.kaiming_normal_(layer.weight, mode='fan_in', nonlinearity='relu')
#
# # 모델 전체에 적용:
# def init_weights(m):
#     if isinstance(m, nn.Linear):
#         nn.init.kaiming_normal_(m.weight, nonlinearity='relu')
#         if m.bias is not None:
#             nn.init.zeros_(m.bias)
#     elif isinstance(m, nn.Conv2d):
#         nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
#
# model.apply(init_weights)  # 모든 레이어에 적용


# --- 초기화 비교 시뮬레이션 ---
print("\n--- 초기화 방법 비교 ---")

def simulate_forward_pass(init_method, num_layers=5, size=100):
    """여러 레이어를 통과하며 활성화 값의 분산 추적"""
    x = [random.gauss(0, 1) for _ in range(size)]
    variances = []

    for layer in range(num_layers):
        if init_method == "zeros":
            w = [[0.0] * size for _ in range(size)]
        elif init_method == "random_large":
            w = [[random.gauss(0, 1.0) for _ in range(size)] for _ in range(size)]
        elif init_method == "xavier":
            w = xavier_normal(size, size)
        elif init_method == "he":
            w = he_normal(size, size)
        else:
            w = [[random.gauss(0, 0.01) for _ in range(size)] for _ in range(size)]

        # 행렬곱 (간소화: 첫 뉴런만)
        new_x = [0.0] * size
        for i in range(size):
            new_x[i] = sum(w[i][j] * x[j] for j in range(size))
            new_x[i] = max(0, new_x[i])  # ReLU

        x = new_x
        var = sum(v ** 2 for v in x) / len(x)
        variances.append(var)

    return variances

for method in ["random_large", "xavier", "he"]:
    vars = simulate_forward_pass(method)
    var_str = " → ".join(f"{v:.2e}" for v in vars)
    print(f"  {method:15s}: {var_str}")

print("\n  → He 초기화가 ReLU와 함께 분산을 잘 유지합니다!")


# ===============================================================================
#  2. Gradient Clipping (기울기 클리핑)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 2: Gradient Clipping")
print("=" * 70)

print("""
기울기 클리핑 = 기울기의 크기를 제한하여 기울기 폭발 방지

비유: 볼륨 조절기의 최대치
  - 소리가 갑자기 커져도 최대 볼륨 이상은 안 올라감
  - 기울기가 폭발해도 max_norm 이상은 안 커짐

두 가지 방법:
  1. clip_grad_norm_: 전체 기울기의 L2 norm 제한 (더 많이 사용)
  2. clip_grad_value_: 각 기울기 값을 [-value, value]로 클리핑
""")

def clip_grad_norm(gradients, max_norm):
    """기울기 L2 norm 클리핑"""
    total_norm = math.sqrt(sum(g ** 2 for g in gradients))
    clip_coef = max_norm / (total_norm + 1e-6)

    if clip_coef < 1:
        clipped = [g * clip_coef for g in gradients]
        return clipped, total_norm
    return gradients[:], total_norm

# 테스트
grads = [10.0, 20.0, 30.0, -15.0, 25.0]
max_norm = 5.0
clipped, orig_norm = clip_grad_norm(grads, max_norm)

print(f"\n원래 기울기: {grads}")
print(f"원래 norm: {orig_norm:.4f}")
print(f"max_norm: {max_norm}")
print(f"클리핑 후: [{', '.join(f'{v:.4f}' for v in clipped)}]")
print(f"클리핑 후 norm: {math.sqrt(sum(g**2 for g in clipped)):.4f}")

# 실제 PyTorch 코드:
# # 학습 루프에서:
# loss.backward()
# torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
# optimizer.step()


# ===============================================================================
#  3. 조기 종료 (Early Stopping)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 3: 조기 종료 (Early Stopping)")
print("=" * 70)

print("""
조기 종료 = 검증 성능이 더 이상 개선되지 않으면 학습 중단

비유: 주식 투자
  - 수익이 계속 오르면 계속 보유
  - N일 연속 안 오르면 매도 (더 떨어지기 전에)

목적: 과적합 방지
  - 학습 손실은 계속 줄어도
  - 검증 손실이 올라가기 시작하면 → 과적합!
  - 그 시점에서 멈추는 것이 최선
""")


class EarlyStopping:
    """조기 종료 구현"""

    def __init__(self, patience=5, min_delta=0.0, restore_best=True):
        """
        patience: 개선 없이 기다릴 에폭 수
        min_delta: 개선으로 인정할 최소 변화량
        restore_best: 최적 모델 복원 여부
        """
        self.patience = patience
        self.min_delta = min_delta
        self.restore_best = restore_best
        self.counter = 0
        self.best_loss = float('inf')
        self.best_epoch = 0
        self.best_model_state = None
        self.should_stop = False

    def __call__(self, val_loss, model_state=None, epoch=0):
        if val_loss < self.best_loss - self.min_delta:
            # 개선됨!
            self.best_loss = val_loss
            self.best_epoch = epoch
            self.counter = 0
            if model_state is not None:
                self.best_model_state = model_state.copy()
            return False
        else:
            # 개선 안 됨
            self.counter += 1
            if self.counter >= self.patience:
                self.should_stop = True
                print(f"    [!] 조기 종료! (patience={self.patience} 소진)")
                print(f"    최적 에폭: {self.best_epoch}, 최적 손실: {self.best_loss:.4f}")
                return True
            return False


# 시뮬레이션
print("\n--- 조기 종료 시뮬레이션 ---")
early_stopping = EarlyStopping(patience=3, min_delta=0.01)

# 가짜 검증 손실 (처음에 줄다가 나중에 증가)
fake_val_losses = [1.0, 0.8, 0.6, 0.55, 0.52, 0.51, 0.52, 0.53, 0.55, 0.58]

for epoch, val_loss in enumerate(fake_val_losses):
    stop = early_stopping(val_loss, model_state={"epoch": epoch}, epoch=epoch)
    status = f"counter={early_stopping.counter}"
    print(f"  Epoch {epoch}: val_loss={val_loss:.2f} | {status}")
    if stop:
        break


# ===============================================================================
#  4. 모델 저장/로드 (state_dict)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 4: 모델 저장/로드")
print("=" * 70)

print("""
PyTorch 모델 저장 방법 2가지:

1. state_dict 저장 (권장!)
   torch.save(model.state_dict(), 'model.pth')
   model.load_state_dict(torch.load('model.pth'))

2. 모델 전체 저장 (비권장)
   torch.save(model, 'model.pth')
   model = torch.load('model.pth')

왜 state_dict가 권장되는가?
  - 모델 클래스 코드가 변경되어도 가중치 로드 가능
  - 더 유연하고 안전
  - 파일 크기가 작음
""")

# state_dict 시뮬레이션
class ModelStateDict:
    """state_dict 개념 시뮬레이션"""

    def __init__(self):
        self.params = {
            "layer1.weight": [[0.1, 0.2], [0.3, 0.4]],
            "layer1.bias": [0.01, 0.02],
            "layer2.weight": [[0.5, 0.6]],
            "layer2.bias": [0.03],
        }

    def state_dict(self):
        """모든 파라미터를 딕셔너리로 반환"""
        return self.params.copy()

    def load_state_dict(self, state_dict):
        """딕셔너리에서 파라미터 로드"""
        for key in self.params:
            if key in state_dict:
                self.params[key] = state_dict[key]
            else:
                print(f"  경고: '{key}'가 state_dict에 없습니다!")


model = ModelStateDict()
sd = model.state_dict()
print(f"\nstate_dict 키:")
for key, value in sd.items():
    print(f"  {key}: {value}")

# JSON으로 저장/로드 시뮬레이션
save_path = "model_state_simulation.json"
print(f"\n모델 저장 시뮬레이션 → {save_path}")

# 저장
with open(save_path, 'w') as f:
    json.dump(sd, f)
print("  저장 완료!")

# 로드
new_model = ModelStateDict()
with open(save_path, 'r') as f:
    loaded_sd = json.load(f)
new_model.load_state_dict(loaded_sd)
print("  로드 완료!")
print(f"  로드된 layer1.weight: {new_model.params['layer1.weight']}")

# 정리
os.remove(save_path)

# 실제 PyTorch 코드:
# # 저장
# torch.save(model.state_dict(), 'model.pth')
#
# # 로드
# model = MyModel()  # 같은 구조의 모델 생성
# model.load_state_dict(torch.load('model.pth'))
# model.eval()  # 추론 모드로 전환!
#
# # GPU에서 저장 → CPU에서 로드
# model.load_state_dict(torch.load('model.pth', map_location='cpu'))


# ===============================================================================
#  5. 체크포인트 (Checkpoint)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 5: 체크포인트")
print("=" * 70)

print("""
체크포인트 = 학습 중간 상태를 저장 (이어서 학습 가능)

포함해야 할 정보:
  - model.state_dict()      (모델 파라미터)
  - optimizer.state_dict()   (옵티마이저 상태)
  - epoch                    (현재 에폭)
  - loss                     (현재 손실)
  - 기타 (학습률 스케줄러, best accuracy 등)
""")


class CheckpointManager:
    """체크포인트 관리자"""

    def __init__(self, save_dir="checkpoints"):
        self.save_dir = save_dir
        self.best_val_loss = float('inf')

    def save_checkpoint(self, state, is_best=False):
        """체크포인트 저장"""
        print(f"  체크포인트 저장: epoch={state['epoch']}, loss={state['loss']:.4f}")
        if is_best:
            print(f"  * 최적 모델 갱신!")

    def load_checkpoint(self, path):
        """체크포인트 로드 (시뮬레이션)"""
        print(f"  체크포인트 로드: {path}")
        return {"epoch": 50, "loss": 0.15}


# 시뮬레이션
ckpt_mgr = CheckpointManager()
print("\n--- 체크포인트 저장 시뮬레이션 ---")

fake_losses = [0.5, 0.3, 0.25, 0.28, 0.22, 0.21, 0.23]
for epoch, loss in enumerate(fake_losses):
    is_best = loss < ckpt_mgr.best_val_loss
    if is_best:
        ckpt_mgr.best_val_loss = loss
    ckpt_mgr.save_checkpoint({"epoch": epoch, "loss": loss}, is_best=is_best)

# 실제 PyTorch 코드:
# # 저장
# checkpoint = {
#     'epoch': epoch,
#     'model_state_dict': model.state_dict(),
#     'optimizer_state_dict': optimizer.state_dict(),
#     'loss': loss,
#     'best_val_loss': best_val_loss,
# }
# torch.save(checkpoint, 'checkpoint.pth')
#
# # best model 별도 저장
# if val_loss < best_val_loss:
#     torch.save(model.state_dict(), 'best_model.pth')
#     best_val_loss = val_loss
#
# # 로드 (이어서 학습)
# checkpoint = torch.load('checkpoint.pth')
# model.load_state_dict(checkpoint['model_state_dict'])
# optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
# start_epoch = checkpoint['epoch'] + 1


# ===============================================================================
#  6. 혼합 정밀도 학습 (AMP)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 6: 혼합 정밀도 학습 (AMP)")
print("=" * 70)

print("""
AMP = Automatic Mixed Precision (자동 혼합 정밀도)

Float32 (단정밀도): 일반적인 부동소수점 (32비트)
Float16 (반정밀도): 절반 크기 (16비트)

혼합 정밀도 = 일부 연산은 FP16, 일부는 FP32 사용

장점:
  - 메모리 사용량 약 50% 감소
  - 학습 속도 2~3배 향상 (Tensor Core 활용)
  - 정확도 거의 동일!

비유: 계산기 두 개
  - 고급 계산기(FP32): 정밀하지만 느림 → 손실 계산, 기울기 스케일링
  - 간단 계산기(FP16): 빠르지만 덜 정밀 → 순전파, 역전파
""")

# FP32 vs FP16 비교
print("\n--- 정밀도 비교 ---")
import struct

def float32_precision(value):
    """FP32 정밀도"""
    packed = struct.pack('f', value)
    return struct.unpack('f', packed)[0]

values = [0.1, 0.001, 3.14159265, 100000.0]
print(f"{'값':>15} {'FP32':>20} {'유효 자릿수':>12}")
print("-" * 50)
for v in values:
    fp32 = float32_precision(v)
    print(f"{v:>15.8f} {fp32:>20.8f} {'~7자리':>12}")

print("""
FP16 주의사항:
  - 표현 범위가 좁음 (±65504)
  - 기울기가 너무 작으면 0이 될 수 있음 (underflow)
  → GradScaler가 자동으로 스케일링하여 해결
""")

# 실제 PyTorch 코드:
# from torch.cuda.amp import autocast, GradScaler
#
# scaler = GradScaler()
#
# for inputs, labels in dataloader:
#     optimizer.zero_grad()
#
#     # 순전파에 autocast 적용
#     with autocast():
#         outputs = model(inputs)
#         loss = criterion(outputs, labels)
#
#     # GradScaler로 역전파
#     scaler.scale(loss).backward()
#     scaler.step(optimizer)
#     scaler.update()


# ===============================================================================
#  7. 실습: 완전한 학습 파이프라인
# ===============================================================================
print("\n" + "=" * 70)
print("Part 7: 실습 - 완전한 학습 파이프라인")
print("=" * 70)


class TrainingPipeline:
    """완전한 학습 파이프라인 시뮬레이션"""

    def __init__(self, model_name="SimpleNet", lr=0.01, patience=5):
        self.model_name = model_name
        self.lr = lr
        self.early_stopping = EarlyStopping(patience=patience)
        self.best_val_loss = float('inf')
        self.train_losses = []
        self.val_losses = []

    def init_weights(self):
        """가중치 초기화"""
        print("  [1/5] He 초기화 적용")

    def train_epoch(self, epoch):
        """한 에폭 학습 (시뮬레이션)"""
        # 가짜 학습 손실 (점점 줄어듦)
        train_loss = 1.0 * math.exp(-0.1 * epoch) + random.gauss(0, 0.02)
        self.train_losses.append(train_loss)
        return max(0.01, train_loss)

    def validate(self, epoch):
        """검증 (시뮬레이션)"""
        val_loss = 1.0 * math.exp(-0.08 * epoch) + random.gauss(0, 0.03)
        # 과적합 시뮬레이션: 에폭 15 이후부터 검증 손실 증가
        if epoch > 15:
            val_loss += 0.02 * (epoch - 15)
        self.val_losses.append(val_loss)
        return max(0.01, val_loss)

    def run(self, num_epochs=30):
        """전체 학습 실행"""
        print(f"\n{'='*50}")
        print(f"학습 시작: {self.model_name}")
        print(f"{'='*50}")

        # Step 1: 가중치 초기화
        self.init_weights()
        print(f"  [2/5] 옵티마이저: Adam (lr={self.lr})")
        print(f"  [3/5] 학습률 스케줄러: ReduceLROnPlateau")
        print(f"  [4/5] 조기 종료: patience={self.early_stopping.patience}")
        print(f"  [5/5] Gradient Clipping: max_norm=1.0")

        current_lr = self.lr

        print(f"\n{'Epoch':>6} {'Train':>10} {'Val':>10} {'LR':>12} {'상태':>10}")
        print("-" * 55)

        for epoch in range(num_epochs):
            # 학습
            train_loss = self.train_epoch(epoch)

            # 검증
            val_loss = self.validate(epoch)

            # 학습률 스케줄링 (간소화)
            if epoch > 0 and epoch % 10 == 0:
                current_lr *= 0.5

            # 최적 모델 저장
            status = ""
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                status = "* best"

            print(f"  {epoch:4d} {train_loss:10.4f} {val_loss:10.4f} {current_lr:12.6f} {status:>10}")

            # 조기 종료 체크
            if self.early_stopping(val_loss, epoch=epoch):
                break

        print(f"\n최종 결과:")
        print(f"  최적 검증 손실: {self.best_val_loss:.4f}")
        print(f"  최적 에폭: {self.early_stopping.best_epoch}")
        print(f"  총 학습 에폭: {len(self.train_losses)}")

        return self.train_losses, self.val_losses


pipeline = TrainingPipeline(model_name="DemoNet", lr=0.001, patience=5)
train_losses, val_losses = pipeline.run(num_epochs=30)


# 실제 PyTorch 완전한 학습 파이프라인:
# import torch
# import torch.nn as nn
# from torch.cuda.amp import autocast, GradScaler
#
# # 1. 모델 & 초기화
# model = MyModel().to(device)
# model.apply(init_weights)
#
# # 2. 손실, 옵티마이저, 스케줄러
# criterion = nn.CrossEntropyLoss()
# optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)
# scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5)
# scaler = GradScaler()  # AMP
#
# # 3. 학습 루프
# best_val_loss = float('inf')
# patience_counter = 0
#
# for epoch in range(num_epochs):
#     # 학습
#     model.train()
#     for inputs, labels in train_loader:
#         inputs, labels = inputs.to(device), labels.to(device)
#
#         optimizer.zero_grad()
#         with autocast():
#             outputs = model(inputs)
#             loss = criterion(outputs, labels)
#
#         scaler.scale(loss).backward()
#         scaler.unscale_(optimizer)
#         torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
#         scaler.step(optimizer)
#         scaler.update()
#
#     # 검증
#     model.eval()
#     val_loss = 0
#     with torch.no_grad():
#         for inputs, labels in val_loader:
#             outputs = model(inputs)
#             val_loss += criterion(outputs, labels).item()
#     val_loss /= len(val_loader)
#
#     scheduler.step(val_loss)
#
#     # 체크포인트 & 조기 종료
#     if val_loss < best_val_loss:
#         best_val_loss = val_loss
#         torch.save(model.state_dict(), 'best_model.pth')
#         patience_counter = 0
#     else:
#         patience_counter += 1
#         if patience_counter >= patience:
#             print("Early stopping!")
#             break
#
# # 최적 모델 로드
# model.load_state_dict(torch.load('best_model.pth'))


# ===============================================================================
#  핵심 정리
# ===============================================================================
print("\n" + "=" * 70)
print("핵심 정리")
print("=" * 70)
print("""
1. 가중치 초기화:
   - ReLU → He (Kaiming) 초기화
   - Sigmoid/Tanh → Xavier (Glorot) 초기화
   - model.apply(init_fn)으로 일괄 적용

2. Gradient Clipping: clip_grad_norm_(params, max_norm=1.0)
   → RNN/LSTM 학습 시 필수!

3. 조기 종료: patience 에폭 동안 개선 없으면 중단
   → 과적합 방지의 핵심

4. 모델 저장: state_dict() 방식 권장
   → torch.save(model.state_dict(), path)

5. 체크포인트: model + optimizer + epoch + loss 함께 저장
   → 학습 중단 후 이어서 가능

6. AMP: autocast() + GradScaler
   → GPU 메모리 절약 + 속도 2~3배 향상

완전한 학습 파이프라인 순서:
  초기화 → 학습 루프 → 기울기 클리핑 → 검증 → 스케줄러 → 체크포인트 → 조기 종료
""")
