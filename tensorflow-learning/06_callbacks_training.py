# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   TensorFlow/Keras 학습 06단계: 콜백과 학습 관리
#   ─ EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, TensorBoard, 커스텀 콜백 ─
#   ■ 실행 방법: python 06_callbacks_training.py (개념 학습용 코드, TF 없이 실행 가능)
#   ■ TensorFlow 설치: pip install tensorflow
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import random

random.seed(42)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. 콜백(Callback)이란?
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("1. 콜백(Callback)이란?")
print("=" * 70)

print("""
■ 콜백 = 학습 중 특정 시점에 자동으로 실행되는 함수

  비유: 요리할 때 타이머 & 알람 설정!
  - "10분 지나면 불 줄여" → ReduceLROnPlateau
  - "맛이 더 안 좋아지면 멈춰" → EarlyStopping
  - "최고 맛이면 레시피 저장" → ModelCheckpoint
  - "매분마다 맛 기록" → TensorBoard

■ 콜백이 실행되는 시점:
  on_train_begin    → 학습 시작 시
  on_epoch_begin    → 각 에포크 시작 시
  on_batch_begin    → 각 배치 시작 시
  on_batch_end      → 각 배치 끝날 때
  on_epoch_end      → 각 에포크 끝날 때
  on_train_end      → 학습 종료 시
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. 기본 콜백 클래스 구현
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("2. 콜백 시스템 구현")
print("=" * 70)

class ToyCallback:
    """콜백 기본 클래스"""
    def on_train_begin(self, logs=None):
        pass
    def on_epoch_begin(self, epoch, logs=None):
        pass
    def on_epoch_end(self, epoch, logs=None):
        pass
    def on_train_end(self, logs=None):
        pass

class ToyEarlyStopping(ToyCallback):
    """EarlyStopping: 성능이 개선되지 않으면 학습 조기 종료"""
    def __init__(self, monitor='val_loss', patience=5, restore_best_weights=True,
                 min_delta=0.0, verbose=True):
        self.monitor = monitor
        self.patience = patience
        self.restore_best_weights = restore_best_weights
        self.min_delta = min_delta
        self.verbose = verbose
        self.best = float('inf')
        self.wait = 0
        self.best_epoch = 0
        self.best_weights = None
        self.stopped = False

    def on_epoch_end(self, epoch, logs=None):
        current = logs.get(self.monitor, 0)
        if current < self.best - self.min_delta:
            self.best = current
            self.wait = 0
            self.best_epoch = epoch
            self.best_weights = "saved"  # 실제로는 모델 가중치 저장
            if self.verbose:
                print(f"    [EarlyStopping] 개선됨! {self.monitor}={current:.6f} "
                      f"(best at epoch {epoch})")
        else:
            self.wait += 1
            if self.verbose:
                print(f"    [EarlyStopping] 개선 없음 ({self.wait}/{self.patience})")
            if self.wait >= self.patience:
                self.stopped = True
                if self.verbose:
                    print(f"    [EarlyStopping] 조기 종료! 최고 epoch: {self.best_epoch}")
                return True  # 학습 중단 신호
        return False

class ToyModelCheckpoint(ToyCallback):
    """ModelCheckpoint: 최고 성능 모델 저장"""
    def __init__(self, filepath='best_model.h5', monitor='val_loss',
                 save_best_only=True, verbose=True):
        self.filepath = filepath
        self.monitor = monitor
        self.save_best_only = save_best_only
        self.verbose = verbose
        self.best = float('inf')

    def on_epoch_end(self, epoch, logs=None):
        current = logs.get(self.monitor, 0)
        if not self.save_best_only or current < self.best:
            self.best = current
            if self.verbose:
                print(f"    [ModelCheckpoint] 모델 저장: {self.filepath} "
                      f"({self.monitor}={current:.6f})")

class ToyReduceLROnPlateau(ToyCallback):
    """ReduceLROnPlateau: 성능 정체 시 학습률 감소"""
    def __init__(self, monitor='val_loss', factor=0.5, patience=3,
                 min_lr=1e-6, verbose=True):
        self.monitor = monitor
        self.factor = factor
        self.patience = patience
        self.min_lr = min_lr
        self.verbose = verbose
        self.best = float('inf')
        self.wait = 0
        self.current_lr = 0.001  # 초기 학습률

    def on_epoch_end(self, epoch, logs=None):
        current = logs.get(self.monitor, 0)
        if current < self.best:
            self.best = current
            self.wait = 0
        else:
            self.wait += 1
            if self.wait >= self.patience:
                old_lr = self.current_lr
                self.current_lr = max(self.current_lr * self.factor, self.min_lr)
                self.wait = 0
                if self.verbose:
                    print(f"    [ReduceLR] 학습률 감소: {old_lr:.6f} → {self.current_lr:.6f}")

class ToyTensorBoard(ToyCallback):
    """TensorBoard 로깅 시뮬레이션"""
    def __init__(self, log_dir='./logs'):
        self.log_dir = log_dir
        self.logs_history = []

    def on_train_begin(self, logs=None):
        print(f"    [TensorBoard] 로그 디렉토리: {self.log_dir}")
        print(f"    [TensorBoard] 실행: tensorboard --logdir={self.log_dir}")

    def on_epoch_end(self, epoch, logs=None):
        self.logs_history.append(logs.copy() if logs else {})

class ToyCustomCallback(ToyCallback):
    """커스텀 콜백 예제"""
    def __init__(self, check_every=5):
        self.check_every = check_every
        self.train_losses = []

    def on_train_begin(self, logs=None):
        print("    [Custom] 학습을 시작합니다!")

    def on_epoch_end(self, epoch, logs=None):
        loss = logs.get('loss', 0)
        self.train_losses.append(loss)

        if (epoch + 1) % self.check_every == 0:
            avg_recent = sum(self.train_losses[-self.check_every:]) / self.check_every
            print(f"    [Custom] 최근 {self.check_every} 에포크 평균 손실: {avg_recent:.6f}")

    def on_train_end(self, logs=None):
        if self.train_losses:
            first = self.train_losses[0]
            last = self.train_losses[-1]
            improvement = (first - last) / first * 100 if first > 0 else 0
            print(f"    [Custom] 학습 완료! 손실 개선율: {improvement:.1f}%")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. EarlyStopping 상세
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("3. EarlyStopping - 과적합 방지의 핵심")
print("=" * 70)

print("""
■ EarlyStopping 파라미터:

  monitor='val_loss'       # 모니터링할 지표
  patience=5               # 개선 없이 기다릴 에포크 수
  min_delta=0.001           # 이 값 이상 개선되어야 "개선"으로 인정
  restore_best_weights=True # 종료 시 최고 성능 가중치로 복원

  비유: 물고기 낚시
  patience=5 → "5분 동안 입질 없으면 자리 이동"
  restore_best_weights → "그래도 제일 큰 물고기는 가져감"

■ 과적합 진단:
  - 학습 손실 ↓ + 검증 손실 ↓ → 정상 학습 중
  - 학습 손실 ↓ + 검증 손실 ↑ → 과적합 시작! → EarlyStopping!
  - 학습 손실 → + 검증 손실 → → 학습 정체 → 모델/데이터 재검토
""")

# 실제 코드: EarlyStopping
# 실제 코드: early_stop = tf.keras.callbacks.EarlyStopping(
# 실제 코드:     monitor='val_loss',
# 실제 코드:     patience=10,
# 실제 코드:     min_delta=0.001,
# 실제 코드:     restore_best_weights=True,
# 실제 코드:     verbose=1
# 실제 코드: )


# ═══════════════════════════════════════════════════════════════════════════════
# 4. ModelCheckpoint 상세
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("4. ModelCheckpoint - 최고 모델 저장")
print("=" * 70)

print("""
■ ModelCheckpoint 파라미터:

  filepath='best_model.h5'  # 저장 경로
  monitor='val_loss'        # 모니터링 지표
  save_best_only=True       # 최고 성능일 때만 저장
  save_weights_only=False   # True면 가중치만, False면 전체 모델
  mode='auto'               # 'min'(손실), 'max'(정확도)

  비유: 게임 세이브 포인트
  save_best_only=True → "최고 점수일 때만 세이브"
  save_best_only=False → "매 스테이지마다 세이브"

■ 파일 형식:
  - .h5     : HDF5 형식 (레거시, 단일 파일)
  - SavedModel : TF 표준 (폴더, 서빙에 적합)

■ 동적 파일명:
  filepath='model-{epoch:02d}-{val_loss:.2f}.h5'
  → model-05-0.23.h5, model-12-0.15.h5 등
""")

# 실제 코드: ModelCheckpoint
# 실제 코드: checkpoint = tf.keras.callbacks.ModelCheckpoint(
# 실제 코드:     filepath='best_model.keras',
# 실제 코드:     monitor='val_accuracy',
# 실제 코드:     save_best_only=True,
# 실제 코드:     mode='max',
# 실제 코드:     verbose=1
# 실제 코드: )


# ═══════════════════════════════════════════════════════════════════════════════
# 5. ReduceLROnPlateau 상세
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("5. ReduceLROnPlateau - 학습률 자동 감소")
print("=" * 70)

print("""
■ ReduceLROnPlateau 파라미터:

  monitor='val_loss'  # 모니터링 지표
  factor=0.5          # 학습률 곱할 계수 (절반으로)
  patience=5          # 기다릴 에포크 수
  min_lr=1e-6         # 최소 학습률

  비유: 목적지 근처에서 속도 줄이기!
  "5분 동안 가까워지지 않으면 속도를 절반으로 줄여!"

■ 학습률 변화 예시:
  lr = 0.001 (시작)
  → 0.0005 (5에포크 정체 후)
  → 0.00025 (또 5에포크 정체)
  → 0.000125
  → ...
  → 0.000001 (최소값, 더 이상 감소 안 함)
""")

# 실제 코드: ReduceLROnPlateau
# 실제 코드: reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
# 실제 코드:     monitor='val_loss',
# 실제 코드:     factor=0.5,
# 실제 코드:     patience=5,
# 실제 코드:     min_lr=1e-6,
# 실제 코드:     verbose=1
# 실제 코드: )


# ═══════════════════════════════════════════════════════════════════════════════
# 6. TensorBoard - 로그 시각화
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("6. TensorBoard - 학습 과정 시각화")
print("=" * 70)

print("""
■ TensorBoard란?
  학습 과정을 웹 브라우저에서 실시간 시각화하는 도구!

  ┌────────────────────────────────────────────┐
  │  TensorBoard 대시보드                       │
  ├────────────────────────────────────────────┤
  │  Scalars: 손실, 정확도 그래프              │
  │  Images:  입력/출력 이미지 시각화          │
  │  Graphs:  모델 구조 그래프                 │
  │  Histograms: 가중치 분포 변화             │
  │  Projector:  임베딩 시각화 (t-SNE)        │
  └────────────────────────────────────────────┘

■ 사용법:
  1. 콜백 추가: TensorBoard(log_dir='./logs')
  2. 터미널에서: tensorboard --logdir=./logs
  3. 브라우저: http://localhost:6006
""")

# 실제 코드: TensorBoard
# 실제 코드: import datetime
# 실제 코드: log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
# 실제 코드: tensorboard_cb = tf.keras.callbacks.TensorBoard(
# 실제 코드:     log_dir=log_dir,
# 실제 코드:     histogram_freq=1,    # 가중치 히스토그램 저장 빈도
# 실제 코드:     write_graph=True,    # 모델 그래프 저장
# 실제 코드:     write_images=True,   # 가중치를 이미지로 저장
# 실제 코드: )


# ═══════════════════════════════════════════════════════════════════════════════
# 7. 커스텀 콜백
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("7. 커스텀 콜백 만들기")
print("=" * 70)

print("""
■ 커스텀 콜백이 필요한 경우:
  - Slack/이메일로 학습 상태 알림
  - 특정 조건에서 학습률 동적 변경
  - 중간 결과 저장 및 시각화
  - 추가 메트릭 계산 및 로깅
""")

# 실제 코드: 커스텀 콜백
# 실제 코드: class CustomCallback(tf.keras.callbacks.Callback):
# 실제 코드:     def on_epoch_end(self, epoch, logs=None):
# 실제 코드:         if logs.get('val_accuracy', 0) > 0.95:
# 실제 코드:             print(f"\n95% 달성! Epoch {epoch}")
# 실제 코드:             self.model.stop_training = True
# 실제 코드:
# 실제 코드:     def on_train_end(self, logs=None):
# 실제 코드:         # Slack 알림 보내기 등
# 실제 코드:         print("학습 완료 알림 전송!")


# ═══════════════════════════════════════════════════════════════════════════════
# 8. 학습 곡선 분석 - 과적합/과소적합 진단
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("8. 학습 곡선 분석 - 과적합/과소적합 진단")
print("=" * 70)

def simulate_training(scenario='normal', epochs=50):
    """다양한 학습 시나리오 시뮬레이션"""
    train_loss = []
    val_loss = []

    for epoch in range(epochs):
        if scenario == 'normal':
            # 정상 학습
            tl = 2.0 * math.exp(-0.05 * epoch) + random.gauss(0, 0.02)
            vl = 2.2 * math.exp(-0.04 * epoch) + random.gauss(0, 0.03)
        elif scenario == 'overfit':
            # 과적합
            tl = 2.0 * math.exp(-0.08 * epoch) + random.gauss(0, 0.01)
            vl = 1.5 * math.exp(-0.03 * epoch) + 0.01 * epoch + random.gauss(0, 0.02)
        elif scenario == 'underfit':
            # 과소적합
            tl = 1.5 + 0.3 * math.exp(-0.01 * epoch) + random.gauss(0, 0.02)
            vl = 1.8 + 0.3 * math.exp(-0.01 * epoch) + random.gauss(0, 0.03)
        elif scenario == 'diverge':
            # 발산
            tl = 0.5 + 0.05 * epoch + random.gauss(0, 0.1)
            vl = 0.8 + 0.08 * epoch + random.gauss(0, 0.15)

        train_loss.append(max(0.01, tl))
        val_loss.append(max(0.01, vl))

    return train_loss, val_loss

def ascii_dual_plot(train, val, title, width=40):
    """학습/검증 손실 ASCII 그래프"""
    all_vals = train + val
    max_v = max(all_vals)
    min_v = min(all_vals)
    range_v = max_v - min_v if max_v != min_v else 1

    print(f"\n  {title}")
    print(f"  T=학습, V=검증")
    height = 8
    for row in range(height, -1, -1):
        threshold = min_v + range_v * row / height
        line = ""
        step = max(1, len(train) // width)
        for i in range(0, min(len(train), width * step), step):
            t_close = abs(train[i] - threshold) < range_v / height / 2 + 0.001
            v_close = abs(val[i] - threshold) < range_v / height / 2 + 0.001
            if t_close and v_close:
                line += "X"
            elif t_close:
                line += "T"
            elif v_close:
                line += "V"
            else:
                line += " "
        label = f"{threshold:5.2f}"
        print(f"  {label} │{line}│")
    print(f"  {'':5s}  └{'─' * min(width, len(train) // max(1, len(train) // width))}┘")

scenarios = {
    'normal': '정상 학습 (양쪽 다 감소)',
    'overfit': '과적합 (학습↓ 검증↑)',
    'underfit': '과소적합 (양쪽 다 높음)',
}

for scenario, desc in scenarios.items():
    train_l, val_l = simulate_training(scenario, 50)
    ascii_dual_plot(train_l, val_l, f"{desc}")

print("""
■ 진단별 해결책:

  과적합 (Overfitting):
    - Dropout 추가/증가
    - 데이터 증강 (Data Augmentation)
    - L2 정규화
    - EarlyStopping
    - 모델 크기 줄이기

  과소적합 (Underfitting):
    - 모델 크기 늘리기 (레이어/유닛 추가)
    - 학습률 조정
    - 에포크 수 늘리기
    - 특성 엔지니어링
    - 더 복잡한 모델 사용

  발산 (Diverging):
    - 학습률 낮추기!
    - 그래디언트 클리핑
    - 데이터 정규화 확인
    - BatchNormalization 추가
""")


# ═══════════════════════════════════════════════════════════════════════════════
# 9. [실습] 콜백으로 학습 최적화
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("9. [실습] 콜백으로 학습 최적화 시뮬레이션")
print("=" * 70)

def train_with_callbacks(epochs=60):
    """콜백을 활용한 학습 시뮬레이션"""
    # 콜백 생성
    early_stop = ToyEarlyStopping(monitor='val_loss', patience=8, verbose=True)
    checkpoint = ToyModelCheckpoint(filepath='best_model.h5', monitor='val_loss')
    reduce_lr = ToyReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=4)
    custom_cb = ToyCustomCallback(check_every=10)
    tb = ToyTensorBoard(log_dir='./logs')

    callbacks = [early_stop, checkpoint, reduce_lr, custom_cb, tb]

    # 학습 시작 콜백
    for cb in callbacks:
        cb.on_train_begin()

    # 학습 시뮬레이션 (과적합 시나리오)
    train_losses, val_losses = simulate_training('overfit', epochs)

    print(f"\n  {'Epoch':>5}  {'Train Loss':>11}  {'Val Loss':>11}  {'LR':>10}")
    print(f"  {'─'*5}  {'─'*11}  {'─'*11}  {'─'*10}")

    actual_epochs = 0
    for epoch in range(epochs):
        logs = {
            'loss': train_losses[epoch],
            'val_loss': val_losses[epoch],
            'lr': reduce_lr.current_lr
        }

        print(f"  {epoch+1:5d}  {logs['loss']:11.6f}  {logs['val_loss']:11.6f}  "
              f"{logs['lr']:10.6f}")

        # 각 콜백 실행
        stop = False
        for cb in callbacks:
            result = cb.on_epoch_end(epoch, logs)
            if result:
                stop = True

        actual_epochs = epoch + 1
        if stop:
            break

    # 학습 종료 콜백
    for cb in callbacks:
        cb.on_train_end()

    print(f"\n  학습 완료: {actual_epochs}/{epochs} 에포크 실행")
    if early_stop.stopped:
        print(f"  EarlyStopping 작동: 최고 에포크 {early_stop.best_epoch + 1}")
    print(f"  최종 학습률: {reduce_lr.current_lr:.6f}")

train_with_callbacks()


# ═══════════════════════════════════════════════════════════════════════════════
# 10. 콜백 조합 레시피
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("10. 콜백 조합 레시피 (실전 팁)")
print("=" * 70)

print("""
■ 레시피 1: 기본 학습 (가장 많이 사용)
  callbacks = [
      EarlyStopping(patience=10, restore_best_weights=True),
      ModelCheckpoint('best.keras', save_best_only=True),
      ReduceLROnPlateau(patience=5, factor=0.5),
  ]

■ 레시피 2: 실험 + 모니터링
  callbacks = [
      EarlyStopping(patience=15),
      ModelCheckpoint('model-{epoch:02d}.keras'),
      TensorBoard(log_dir='./logs/experiment_1'),
      ReduceLROnPlateau(patience=5),
  ]

■ 레시피 3: 프로덕션 학습
  callbacks = [
      EarlyStopping(patience=20, min_delta=0.0001),
      ModelCheckpoint('best.keras', save_best_only=True),
      ReduceLROnPlateau(patience=7, factor=0.2, min_lr=1e-7),
      TensorBoard(log_dir='./logs'),
      CustomSlackNotifier(),  # 학습 상태 알림
  ]

■ 주의사항:
  1. EarlyStopping의 patience > ReduceLR의 patience
     (학습률 줄여볼 기회를 줘야 함!)
  2. restore_best_weights=True 필수!
     (마지막 에포크가 최고가 아닐 수 있음)
  3. save_best_only=True로 디스크 절약
""")

# 실제 코드: 콜백 조합 사용
# 실제 코드: callbacks = [
# 실제 코드:     tf.keras.callbacks.EarlyStopping(
# 실제 코드:         monitor='val_loss', patience=10,
# 실제 코드:         restore_best_weights=True, verbose=1),
# 실제 코드:     tf.keras.callbacks.ModelCheckpoint(
# 실제 코드:         'best_model.keras', monitor='val_loss',
# 실제 코드:         save_best_only=True, verbose=1),
# 실제 코드:     tf.keras.callbacks.ReduceLROnPlateau(
# 실제 코드:         monitor='val_loss', factor=0.5,
# 실제 코드:         patience=5, min_lr=1e-6, verbose=1),
# 실제 코드:     tf.keras.callbacks.TensorBoard(log_dir='./logs'),
# 실제 코드: ]
# 실제 코드:
# 실제 코드: history = model.fit(
# 실제 코드:     x_train, y_train,
# 실제 코드:     epochs=100,
# 실제 코드:     batch_size=32,
# 실제 코드:     validation_split=0.2,
# 실제 코드:     callbacks=callbacks
# 실제 코드: )

print("\n" + "=" * 70)
print("요약: 콜백과 학습 관리 학습 완료!")
print("=" * 70)
print("""
  1. EarlyStopping: 과적합 감지 시 학습 중단
  2. ModelCheckpoint: 최고 성능 모델 자동 저장
  3. ReduceLROnPlateau: 정체 시 학습률 자동 감소
  4. TensorBoard: 학습 과정 실시간 시각화
  5. 커스텀 콜백: on_epoch_end 등 오버라이드
  6. 과적합 진단: 학습↓ + 검증↑ = 과적합!
  7. patience 설정: ReduceLR < EarlyStopping

  다음 단계 → 07_transfer_learning.py (전이학습!)
""")
