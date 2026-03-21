# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#   딥러닝 학습 10단계: 전체 훈련 파이프라인
#   ─ 순전파→손실→역전파→업데이트의 완전한 사이클 ─
#
#   비유: 완전한 요리 수업
#     1. 재료 준비 (데이터 분할)
#     2. 요리하기 (순전파)
#     3. 맛보기 (손실 계산)
#     4. 레시피 수정 (역전파+업데이트)
#     5. 반복해서 완벽한 요리 만들기 (에폭)
#     6. 심사위원에게 제출 (평가)
#
#   실행 방법:
#     python 10_training_pipeline.py
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import random


# ─────────────────────────────────────────────────────────────────────────
# ■ 도우미 함수
# ─────────────────────────────────────────────────────────────────────────

def sigmoid(x):
    if x < -500:
        return 0.0
    if x > 500:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


def sigmoid_deriv(s):
    return s * (1.0 - s)


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 1: 데이터 분할 (Train / Validation / Test)
# ─────────────────────────────────────────────────────────────────────────

def lesson1_data_split():
    """
    데이터를 세 그룹으로 나눕니다.

    비유:
      훈련 세트 = 연습 문제 (공부용)
      검증 세트 = 모의고사 (공부 방법 조절용)
      테스트 세트 = 진짜 시험 (최종 실력 확인, 딱 한 번만)
    """
    print("=" * 70)
    print("[레슨 1] 데이터 분할 (Train / Validation / Test)")
    print("=" * 70)
    print()
    print("  비유: 시험 공부")
    print("    훈련(60%)   = 연습 문제로 공부")
    print("    검증(20%)   = 모의고사로 공부법 점검")
    print("    테스트(20%) = 진짜 시험 (실력 확인)")
    print()

    # 데이터 생성: XOR 패턴 + 약간의 변형
    random.seed(42)
    data = []
    for _ in range(50):
        x1 = random.uniform(0, 1)
        x2 = random.uniform(0, 1)
        # XOR-like: (x1>0.5) != (x2>0.5) → 1, 아니면 0
        label = 1 if (x1 > 0.5) != (x2 > 0.5) else 0
        data.append(([x1, x2], label))

    random.shuffle(data)

    n = len(data)
    train_end = int(n * 0.6)
    val_end = int(n * 0.8)

    train_data = data[:train_end]
    val_data = data[train_end:val_end]
    test_data = data[val_end:]

    print(f"  전체 데이터: {n}개")
    print(f"  훈련 세트:   {len(train_data)}개")
    print(f"  검증 세트:   {len(val_data)}개")
    print(f"  테스트 세트: {len(test_data)}개")
    print()

    return train_data, val_data, test_data


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 2: 배치 처리
# ─────────────────────────────────────────────────────────────────────────

def lesson2_batch_processing():
    """
    데이터를 작은 묶음(배치)으로 나눠서 처리합니다.

    비유: 학교 급식에서 줄 서기
      - 50명을 한 번에 다 먹이면 부엌이 터짐
      - 10명씩 5번에 나눠 먹이면 관리 가능
      - 배치 크기 = 한 번에 먹이는 학생 수
    """
    print("=" * 70)
    print("[레슨 2] 배치 처리")
    print("=" * 70)
    print()

    data = list(range(17))  # 17개 데이터
    batch_size = 5

    print(f"  데이터 {len(data)}개, 배치 크기 {batch_size}")
    print()

    batches = []
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        batches.append(batch)
        print(f"    배치 {len(batches)}: {batch}")

    print()
    print(f"  총 {len(batches)}개 배치")
    print("  마지막 배치는 크기가 작을 수 있음 (남은 데이터)")
    print()

    return batch_size


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 3: 미니 신경망 구축 (2입력 → 4은닉 → 1출력)
# ─────────────────────────────────────────────────────────────────────────

class MiniNetwork:
    """
    직접 만든 미니 신경망.
    구조: 입력(2) → 은닉(4) → 출력(1)

    비유: 요리 팀
      - 입력 = 재료 2가지
      - 은닉층 = 요리사 4명이 각각 다른 소스를 만듦
      - 출력 = 소스를 섞어 최종 요리 1개 완성
    """
    def __init__(self, input_size=2, hidden_size=4, output_size=1):
        random.seed(42)
        self.input_size = input_size
        self.hidden_size = hidden_size

        # 가중치 초기화 (작은 랜덤값)
        self.w_ih = [[random.gauss(0, 0.5) for _ in range(hidden_size)]
                     for _ in range(input_size)]
        self.b_h = [0.0] * hidden_size

        self.w_ho = [random.gauss(0, 0.5) for _ in range(hidden_size)]
        self.b_o = 0.0

    def forward(self, x):
        """순전파: 입력 → 은닉 → 출력"""
        # 은닉층
        self.last_x = x
        self.h_raw = [0.0] * self.hidden_size
        self.h = [0.0] * self.hidden_size

        for j in range(self.hidden_size):
            total = self.b_h[j]
            for i in range(self.input_size):
                total += x[i] * self.w_ih[i][j]
            self.h_raw[j] = total
            self.h[j] = sigmoid(total)

        # 출력층
        z = self.b_o
        for j in range(self.hidden_size):
            z += self.h[j] * self.w_ho[j]
        self.output = sigmoid(z)

        return self.output

    def backward(self, target, lr=0.5):
        """역전파: 기울기 계산 → 가중치 업데이트"""
        # 출력층 기울기
        dL_dout = -2.0 * (target - self.output)
        dout_dz = sigmoid_deriv(self.output)
        delta_o = dL_dout * dout_dz

        # 은닉→출력 가중치 업데이트
        for j in range(self.hidden_size):
            self.w_ho[j] -= lr * delta_o * self.h[j]
        self.b_o -= lr * delta_o

        # 은닉층 기울기
        for j in range(self.hidden_size):
            delta_h = delta_o * self.w_ho[j] * sigmoid_deriv(self.h[j])
            for i in range(self.input_size):
                self.w_ih[i][j] -= lr * delta_h * self.last_x[i]
            self.b_h[j] -= lr * delta_h

    def predict(self, x):
        return 1 if self.forward(x) > 0.5 else 0


def lesson3_build_network():
    """
    신경망을 직접 코드로 만들어 봅니다.
    """
    print("=" * 70)
    print("[레슨 3] 미니 신경망 구축")
    print("=" * 70)
    print()
    print("  구조: 입력(2) → 은닉(4, sigmoid) → 출력(1, sigmoid)")
    print()

    net = MiniNetwork()
    print(f"  은닉층 가중치 (2×4):")
    for i, row in enumerate(net.w_ih):
        print(f"    입력{i}: [{', '.join(f'{w:.3f}' for w in row)}]")
    print(f"  출력층 가중치 (4→1): [{', '.join(f'{w:.3f}' for w in net.w_ho)}]")
    print()

    # 테스트 순전파
    test_input = [0.3, 0.7]
    output = net.forward(test_input)
    print(f"  테스트 입력 {test_input} → 출력: {output:.4f}")
    print()

    return net


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 4: 완전한 훈련 루프
# ─────────────────────────────────────────────────────────────────────────

def lesson4_training_loop(train_data, val_data):
    """
    순전파 → 손실 계산 → 역전파 → 가중치 업데이트
    이 사이클을 여러 에폭 반복합니다.

    비유: 요리 수업 반복
      1. 요리한다 (순전파)
      2. 맛을 본다 (손실 계산)
      3. 레시피를 고친다 (역전파 + 업데이트)
      4. 처음부터 다시 (다음 에폭)
    """
    print("=" * 70)
    print("[레슨 4] 완전한 훈련 루프")
    print("=" * 70)
    print()

    net = MiniNetwork()
    lr = 1.0
    epochs = 30
    batch_size = 5

    print("  훈련 진행 (에폭별 손실과 정확도):")
    print("  ┌───────┬───────────┬───────────┬───────────┬───────────┐")
    print("  │ 에폭  │ 훈련 손실 │ 검증 손실 │ 훈련 정확 │ 검증 정확 │")
    print("  ├───────┼───────────┼───────────┼───────────┼───────────┤")

    for epoch in range(epochs):
        # 데이터 섞기
        random.shuffle(train_data)

        # 배치 단위 학습
        train_loss = 0.0
        train_correct = 0

        for start in range(0, len(train_data), batch_size):
            batch = train_data[start:start+batch_size]
            for x, y in batch:
                output = net.forward(x)
                train_loss += (y - output) ** 2
                if net.predict(x) == y:
                    train_correct += 1
                net.backward(y, lr)

        # 검증
        val_loss = 0.0
        val_correct = 0
        for x, y in val_data:
            output = net.forward(x)
            val_loss += (y - output) ** 2
            if net.predict(x) == y:
                val_correct += 1

        train_loss /= len(train_data)
        val_loss /= len(val_data)
        train_acc = train_correct / len(train_data)
        val_acc = val_correct / len(val_data)

        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"  │  {epoch+1:>3}  │  {train_loss:>7.4f}  │  {val_loss:>7.4f}  │  {train_acc:>7.1%}  │  {val_acc:>7.1%}  │")

    print("  └───────┴───────────┴───────────┴───────────┴───────────┘")
    print()

    return net


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 5: 모델 평가 지표
# ─────────────────────────────────────────────────────────────────────────

def lesson5_evaluation_metrics(net, test_data):
    """
    학습된 모델을 다양한 지표로 평가합니다.

    비유: 시험 채점 방법
      정확도 = 전체 문제 중 맞힌 비율
      정밀도 = "맞다"고 한 것 중 실제로 맞은 비율
      재현율 = 실제 정답 중 "맞다"고 찾아낸 비율
      F1 = 정밀도와 재현율의 조화 평균
    """
    print("=" * 70)
    print("[레슨 5] 모델 평가 지표")
    print("=" * 70)
    print()

    # 혼동 행렬 계산
    tp = fp = fn = tn = 0
    for x, y in test_data:
        pred = net.predict(x)
        if pred == 1 and y == 1:
            tp += 1
        elif pred == 1 and y == 0:
            fp += 1
        elif pred == 0 and y == 1:
            fn += 1
        else:
            tn += 1

    print("  혼동 행렬 (Confusion Matrix):")
    print("  ┌──────────────┬──────────────┬──────────────┐")
    print("  │              │ 예측: 양성   │ 예측: 음성   │")
    print("  ├──────────────┼──────────────┼──────────────┤")
    print(f"  │ 실제: 양성   │  TP = {tp:<5} │  FN = {fn:<5} │")
    print(f"  │ 실제: 음성   │  FP = {fp:<5} │  TN = {tn:<5} │")
    print("  └──────────────┴──────────────┴──────────────┘")
    print()

    total = tp + fp + fn + tn
    accuracy = (tp + tn) / total if total > 0 else 0

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    print("  각 지표 설명:")
    print()
    print(f"  정확도 (Accuracy) = (TP+TN) / 전체 = ({tp}+{tn}) / {total} = {accuracy:.3f}")
    print(f"    → 전체 중 맞힌 비율")
    print()
    print(f"  정밀도 (Precision) = TP / (TP+FP) = {tp} / ({tp}+{fp}) = {precision:.3f}")
    print(f"    → '양성'이라 했을 때 진짜 양성인 비율")
    print(f"    → 비유: '범인이다!'라고 했을 때 실제 범인 비율")
    print()
    print(f"  재현율 (Recall) = TP / (TP+FN) = {tp} / ({tp}+{fn}) = {recall:.3f}")
    print(f"    → 실제 양성 중 찾아낸 비율")
    print(f"    → 비유: 전체 범인 중 잡은 비율")
    print()
    print(f"  F1 점수 = 2 × P × R / (P + R) = {f1:.3f}")
    print(f"    → 정밀도와 재현율의 균형 점수")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■" * 72)
    print("  딥러닝 10단계 : 전체 훈련 파이프라인")
    print("  비유: 완전한 요리 수업 (준비→요리→맛보기→수정→반복)")
    print("■" * 72)
    print()

    train_data, val_data, test_data = lesson1_data_split()
    lesson2_batch_processing()
    lesson3_build_network()
    net = lesson4_training_loop(train_data, val_data)
    lesson5_evaluation_metrics(net, test_data)


if __name__ == "__main__":
    main()
