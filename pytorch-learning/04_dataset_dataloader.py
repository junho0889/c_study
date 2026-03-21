# #########################################################################
#
#   PyTorch 학습 04단계: Dataset과 DataLoader
#   - Dataset 클래스, DataLoader, 데이터 변환, 데이터 증강 -
#   # 실행 방법: python 04_dataset_dataloader.py (개념 학습용, PyTorch 없이 실행 가능)
#   # PyTorch 설치: pip install torch torchvision
#
# #########################################################################

import math
import random

random.seed(42)

# ===============================================================================
#  1. Dataset 클래스
# ===============================================================================
print("=" * 70)
print("Part 1: Dataset 클래스")
print("=" * 70)

print("""
Dataset은 데이터를 표준화된 방식으로 관리하는 클래스입니다.

비유: 도서관 카드 카탈로그
  - __len__(): "책이 총 몇 권인가요?" (데이터 개수)
  - __getitem__(idx): "3번 책 주세요" (특정 데이터 접근)

커스텀 Dataset을 만들려면 이 두 메서드만 구현하면 됩니다!
""")


class Dataset:
    """PyTorch Dataset 기본 클래스 모방"""

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx):
        raise NotImplementedError


# -----------------------------------------------------------------------
#  커스텀 Dataset 예제 1: 간단한 숫자 데이터
# -----------------------------------------------------------------------
class NumberDataset(Dataset):
    """간단한 숫자 데이터셋: y = 2x + 1"""

    def __init__(self, size=100):
        self.size = size
        self.X = [random.uniform(-10, 10) for _ in range(size)]
        self.Y = [2 * x + 1 + random.gauss(0, 0.5) for x in self.X]

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        return self.X[idx], self.Y[idx]


dataset = NumberDataset(size=50)
print(f"\n데이터셋 크기: {len(dataset)}")
print(f"첫 번째 데이터: {dataset[0]}")
print(f"다섯 번째 데이터: {dataset[4]}")

# 실제 PyTorch 코드:
# from torch.utils.data import Dataset
#
# class NumberDataset(Dataset):
#     def __init__(self, size=100):
#         self.X = torch.randn(size, 1) * 10
#         self.Y = 2 * self.X + 1 + torch.randn(size, 1) * 0.5
#
#     def __len__(self):
#         return len(self.X)
#
#     def __getitem__(self, idx):
#         return self.X[idx], self.Y[idx]


# -----------------------------------------------------------------------
#  커스텀 Dataset 예제 2: 이미지 데이터셋 시뮬레이션
# -----------------------------------------------------------------------
print("\n--- 이미지 데이터셋 시뮬레이션 ---")

class FakeImageDataset(Dataset):
    """가짜 이미지 데이터셋 (28x28 흑백 이미지 시뮬레이션)"""

    def __init__(self, num_images=100, num_classes=10, transform=None):
        self.num_images = num_images
        self.num_classes = num_classes
        self.transform = transform

        # 가짜 이미지 데이터 (28x28 = 784 픽셀)
        self.images = [[random.randint(0, 255) for _ in range(784)]
                       for _ in range(num_images)]
        self.labels = [random.randint(0, num_classes - 1) for _ in range(num_images)]

    def __len__(self):
        return self.num_images

    def __getitem__(self, idx):
        image = self.images[idx]
        label = self.labels[idx]

        if self.transform:
            image = self.transform(image)

        return image, label


img_dataset = FakeImageDataset(num_images=100)
print(f"이미지 데이터셋 크기: {len(img_dataset)}")
img, label = img_dataset[0]
print(f"이미지 shape: ({len(img)},) (= 28x28 펼친 것)")
print(f"라벨: {label}")
print(f"픽셀 값 범위: [{min(img)}, {max(img)}]")


# ===============================================================================
#  2. DataLoader
# ===============================================================================
print("\n" + "=" * 70)
print("Part 2: DataLoader")
print("=" * 70)

print("""
DataLoader는 Dataset에서 데이터를 배치(batch) 단위로 꺼내주는 도구입니다.

비유: 급식 배식
  - Dataset = 큰 솥의 음식 전체
  - DataLoader = 한 번에 한 접시씩 나눠주는 배식원
  - batch_size = 한 접시에 담는 양
  - shuffle = 줄 서는 순서를 섞을지
  - drop_last = 마지막에 남는 소량을 버릴지

주요 파라미터:
  - batch_size: 한 번에 가져올 데이터 수 (기본 1)
  - shuffle: 데이터 순서 섞기 (학습: True, 검증: False)
  - num_workers: 데이터 로딩 병렬 프로세스 수
  - drop_last: 마지막 불완전 배치 버리기
""")


class DataLoader:
    """PyTorch DataLoader의 핵심 기능 구현"""

    def __init__(self, dataset, batch_size=1, shuffle=False, drop_last=False,
                 collate_fn=None):
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.drop_last = drop_last
        self.collate_fn = collate_fn or self._default_collate

    def _default_collate(self, batch):
        """기본 collate: 리스트를 분리"""
        # batch = [(x1,y1), (x2,y2), ...] → ([x1,x2,...], [y1,y2,...])
        xs = [item[0] for item in batch]
        ys = [item[1] for item in batch]
        return xs, ys

    def __iter__(self):
        """이터레이터 프로토콜"""
        indices = list(range(len(self.dataset)))
        if self.shuffle:
            random.shuffle(indices)

        batch = []
        for idx in indices:
            batch.append(self.dataset[idx])
            if len(batch) == self.batch_size:
                yield self.collate_fn(batch)
                batch = []

        # 남은 데이터 처리
        if batch and not self.drop_last:
            yield self.collate_fn(batch)

    def __len__(self):
        """배치 수 계산"""
        if self.drop_last:
            return len(self.dataset) // self.batch_size
        return math.ceil(len(self.dataset) / self.batch_size)


# DataLoader 테스트
print("\n--- DataLoader 테스트 ---")
dataset = NumberDataset(size=10)
loader = DataLoader(dataset, batch_size=3, shuffle=True, drop_last=False)

print(f"데이터셋 크기: {len(dataset)}")
print(f"배치 크기: 3")
print(f"총 배치 수: {len(loader)}")
print(f"drop_last=False → 마지막 배치 크기: {len(dataset) % 3} (나머지)")

print("\n배치 순회:")
for batch_idx, (x_batch, y_batch) in enumerate(loader):
    print(f"  배치 {batch_idx}: x 크기={len(x_batch)}, 첫 x={x_batch[0]:.2f}")

# drop_last=True 테스트
loader_drop = DataLoader(dataset, batch_size=3, shuffle=False, drop_last=True)
print(f"\ndrop_last=True → 총 배치 수: {len(loader_drop)} (마지막 불완전 배치 버림)")

# 실제 PyTorch 코드:
# from torch.utils.data import DataLoader
#
# loader = DataLoader(
#     dataset,
#     batch_size=32,
#     shuffle=True,
#     num_workers=4,      # 데이터 로딩 병렬화 (Windows: 0 권장)
#     drop_last=True,
#     pin_memory=True     # GPU 학습 시 속도 향상
# )
#
# for batch_idx, (inputs, labels) in enumerate(loader):
#     # inputs: (batch_size, ...)
#     # labels: (batch_size,)
#     pass


# ===============================================================================
#  3. 데이터 변환 (Transforms)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 3: 데이터 변환 (Transforms)")
print("=" * 70)

print("""
transforms는 데이터 전처리를 체인으로 연결하는 도구입니다.

비유: 공장의 생산 라인
  원재료 → 세척 → 규격화 → 포장 → 완제품
  이미지 → ToTensor → Resize → Normalize → 입력 데이터
""")


class Compose:
    """여러 변환을 순서대로 적용"""
    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, data):
        for t in self.transforms:
            data = t(data)
        return data


class Normalize:
    """정규화: (x - mean) / std"""
    def __init__(self, mean, std):
        self.mean = mean
        self.std = std

    def __call__(self, data):
        return [(x - self.mean) / self.std for x in data]


class ToFloat:
    """정수 픽셀값을 0~1 실수로 변환 (ToTensor 역할)"""
    def __call__(self, data):
        return [x / 255.0 for x in data]


class RandomNoise:
    """랜덤 노이즈 추가 (데이터 증강)"""
    def __init__(self, noise_level=0.01):
        self.noise_level = noise_level

    def __call__(self, data):
        return [x + random.gauss(0, self.noise_level) for x in data]


class MinMaxScale:
    """최소-최대 정규화: 0~1 범위로"""
    def __call__(self, data):
        min_val = min(data)
        max_val = max(data)
        if max_val == min_val:
            return [0.0] * len(data)
        return [(x - min_val) / (max_val - min_val) for x in data]


# 변환 파이프라인 구성
transform = Compose([
    ToFloat(),                        # 0~255 → 0~1
    Normalize(mean=0.5, std=0.5),     # 평균 0, 표준편차 1로 정규화
])

# 변환 적용 테스트
raw_pixels = [0, 128, 255, 64, 192]
transformed = transform(raw_pixels)
print(f"\n원본 픽셀: {raw_pixels}")
print(f"변환 후: [{', '.join(f'{v:.4f}' for v in transformed)}]")

# 실제 PyTorch 코드:
# from torchvision import transforms
#
# transform = transforms.Compose([
#     transforms.ToTensor(),              # PIL Image → Tensor, 0~255 → 0~1
#     transforms.Normalize(               # 채널별 정규화
#         mean=[0.485, 0.456, 0.406],     # ImageNet 평균
#         std=[0.229, 0.224, 0.225]       # ImageNet 표준편차
#     ),
#     transforms.Resize((224, 224)),       # 크기 조절
#     transforms.RandomHorizontalFlip(),   # 좌우 반전 (데이터 증강)
#     transforms.RandomRotation(10),       # 회전 (데이터 증강)
# ])


# ===============================================================================
#  4. torchvision.datasets 구조
# ===============================================================================
print("\n" + "=" * 70)
print("Part 4: torchvision.datasets 구조")
print("=" * 70)

print("""
torchvision.datasets는 유명한 데이터셋을 쉽게 사용할 수 있게 합니다.

MNIST: 손글씨 숫자 (28x28, 흑백, 10클래스, 60000+10000)
CIFAR10: 물체 이미지 (32x32, 컬러, 10클래스, 50000+10000)
ImageNet: 대규모 이미지 (다양한 크기, 1000클래스, 128만+)
""")

# MNIST 데이터셋 시뮬레이션
class FakeMNIST(Dataset):
    """MNIST 데이터셋 시뮬레이션"""

    def __init__(self, train=True, transform=None, download=False):
        self.train = train
        self.transform = transform
        n = 60000 if train else 10000  # 실제 크기

        # 시뮬레이션용으로 작게
        n = 100 if train else 20

        self.data = [[random.randint(0, 255) for _ in range(28 * 28)]
                     for _ in range(n)]
        self.targets = [random.randint(0, 9) for _ in range(n)]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        img = self.data[idx]
        label = self.targets[idx]
        if self.transform:
            img = self.transform(img)
        return img, label


# MNIST 사용 예시
mnist_train = FakeMNIST(train=True, transform=Compose([ToFloat(), Normalize(0.1307, 0.3081)]))
mnist_test = FakeMNIST(train=False, transform=Compose([ToFloat(), Normalize(0.1307, 0.3081)]))

print(f"\n학습 데이터: {len(mnist_train)}개")
print(f"테스트 데이터: {len(mnist_test)}개")

img, label = mnist_train[0]
print(f"이미지 차원: {len(img)} (= 28*28 = 784)")
print(f"라벨: {label}")

# 실제 PyTorch 코드:
# from torchvision import datasets, transforms
#
# transform = transforms.Compose([
#     transforms.ToTensor(),
#     transforms.Normalize((0.1307,), (0.3081,))  # MNIST 평균/표준편차
# ])
#
# train_dataset = datasets.MNIST(
#     root='./data',
#     train=True,
#     download=True,          # 없으면 자동 다운로드
#     transform=transform
# )
# test_dataset = datasets.MNIST(root='./data', train=False, transform=transform)
#
# train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
# test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False)


# ===============================================================================
#  5. 데이터 증강 (Data Augmentation)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 5: 데이터 증강 (Data Augmentation)")
print("=" * 70)

print("""
데이터 증강 = 기존 데이터를 변형하여 새로운 학습 데이터 생성

왜 필요한가?
  - 데이터가 부족할 때 모델 성능 향상
  - 과적합(overfitting) 방지
  - 모델의 일반화 능력 향상

비유: 같은 수학 문제를 숫자만 바꿔서 여러 번 풀기
     → 공식을 암기하는 게 아니라 진짜 이해하게 됨

주요 증강 기법:
  - RandomHorizontalFlip: 좌우 반전
  - RandomRotation: 회전
  - RandomCrop: 무작위 자르기
  - ColorJitter: 밝기/대비/채도 변경
  - RandomErasing: 일부 영역 지우기
""")


class RandomHorizontalFlip:
    """좌우 반전 (50% 확률)"""
    def __init__(self, p=0.5):
        self.p = p

    def __call__(self, data):
        if random.random() < self.p:
            return data[::-1]  # 뒤집기
        return data


class RandomBrightness:
    """밝기 랜덤 조절"""
    def __init__(self, factor=0.2):
        self.factor = factor

    def __call__(self, data):
        brightness = 1.0 + random.uniform(-self.factor, self.factor)
        return [max(0, min(1, x * brightness)) for x in data]


# 증강 파이프라인
train_transform = Compose([
    ToFloat(),
    RandomHorizontalFlip(p=0.5),
    RandomBrightness(factor=0.2),
    RandomNoise(noise_level=0.02),
    Normalize(mean=0.5, std=0.5),
])

test_transform = Compose([
    ToFloat(),
    Normalize(mean=0.5, std=0.5),
])

print("\n--- 학습용 vs 테스트용 변환 ---")
print("학습: ToFloat → RandomFlip → RandomBrightness → RandomNoise → Normalize")
print("테스트: ToFloat → Normalize (증강 없음!)")
print("\n[주의] 테스트/검증 시에는 데이터 증강을 적용하지 않습니다!")

sample = [100, 150, 200, 50, 75]
print(f"\n원본: {sample}")
for i in range(3):
    aug = train_transform(sample)
    print(f"증강 {i+1}: [{', '.join(f'{v:.3f}' for v in aug)}]")

# 실제 PyTorch 코드:
# train_transform = transforms.Compose([
#     transforms.RandomHorizontalFlip(),
#     transforms.RandomRotation(15),
#     transforms.RandomCrop(32, padding=4),
#     transforms.ColorJitter(brightness=0.2, contrast=0.2),
#     transforms.ToTensor(),
#     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
# ])
#
# test_transform = transforms.Compose([
#     transforms.ToTensor(),
#     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
# ])


# ===============================================================================
#  6. collate_fn - 커스텀 배치 구성
# ===============================================================================
print("\n" + "=" * 70)
print("Part 6: collate_fn (커스텀 배치 구성)")
print("=" * 70)

print("""
collate_fn은 개별 데이터를 배치로 묶는 방법을 정의합니다.

기본 동작: [(x1,y1), (x2,y2)] → ([x1,x2], [y1,y2])

언제 커스텀 collate_fn이 필요한가?
  - 가변 길이 시퀀스 (문장 길이가 다를 때) → 패딩 필요
  - 특수한 배치 구조가 필요할 때
  - 데이터가 딕셔너리나 복잡한 구조일 때
""")


# 가변 길이 시퀀스 데이터셋
class TextDataset(Dataset):
    """가변 길이 텍스트 데이터셋"""
    def __init__(self):
        self.texts = [
            [1, 2, 3],                # "나는 학생이다" (3 토큰)
            [4, 5, 6, 7, 8],          # "오늘 날씨가 정말 좋다" (5 토큰)
            [9, 10],                   # "안녕하세요" (2 토큰)
            [11, 12, 13, 14],          # "파이토치를 공부한다" (4 토큰)
        ]
        self.labels = [0, 1, 0, 1]

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        return self.texts[idx], self.labels[idx]


def pad_collate_fn(batch):
    """가변 길이 시퀀스를 패딩하여 같은 길이로 맞춤"""
    texts = [item[0] for item in batch]
    labels = [item[1] for item in batch]

    # 가장 긴 시퀀스 길이 찾기
    max_len = max(len(t) for t in texts)

    # 패딩 (0으로 채움)
    padded = [t + [0] * (max_len - len(t)) for t in texts]

    # 실제 길이 기록
    lengths = [len(t) for t in texts]

    return padded, labels, lengths


text_dataset = TextDataset()
text_loader = DataLoader(text_dataset, batch_size=3, collate_fn=pad_collate_fn)

print("\n--- 패딩 collate_fn 결과 ---")
for batch_idx, (texts, labels, lengths) in enumerate(text_loader):
    print(f"배치 {batch_idx}:")
    for i, (text, label, length) in enumerate(zip(texts, labels, lengths)):
        print(f"  텍스트: {text} (원래 길이: {length}, 라벨: {label})")

# 실제 PyTorch 코드:
# from torch.nn.utils.rnn import pad_sequence
#
# def collate_fn(batch):
#     texts, labels = zip(*batch)
#     texts_padded = pad_sequence(
#         [torch.tensor(t) for t in texts],
#         batch_first=True,
#         padding_value=0
#     )
#     return texts_padded, torch.tensor(labels)
#
# loader = DataLoader(dataset, batch_size=32, collate_fn=collate_fn)


# ===============================================================================
#  7. 데이터 분할 (train/val/test)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 7: 데이터 분할")
print("=" * 70)

print("""
데이터 분할 비율 (일반적):
  - 학습(train): 70~80%
  - 검증(validation): 10~15%
  - 테스트(test): 10~15%

비유: 시험 공부
  - 학습 데이터 = 교과서 문제 (공부용)
  - 검증 데이터 = 모의고사 (중간 점검, 하이퍼파라미터 조정)
  - 테스트 데이터 = 수능 (최종 평가, 한 번만!)
""")

# 데이터 분할 구현
def random_split(dataset, ratios):
    """데이터셋을 비율에 따라 분할"""
    n = len(dataset)
    indices = list(range(n))
    random.shuffle(indices)

    splits = []
    start = 0
    for ratio in ratios:
        end = start + int(n * ratio)
        splits.append(indices[start:end])
        start = end
    # 남은 데이터는 마지막에 추가
    if start < n:
        splits[-1].extend(indices[start:])
    return splits


class SubsetDataset(Dataset):
    """인덱스 서브셋으로 만든 데이터셋"""
    def __init__(self, original_dataset, indices):
        self.dataset = original_dataset
        self.indices = indices

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, idx):
        return self.dataset[self.indices[idx]]


full_dataset = NumberDataset(size=100)
train_idx, val_idx, test_idx = random_split(full_dataset, [0.7, 0.15, 0.15])

train_set = SubsetDataset(full_dataset, train_idx)
val_set = SubsetDataset(full_dataset, val_idx)
test_set = SubsetDataset(full_dataset, test_idx)

print(f"\n전체 데이터: {len(full_dataset)}")
print(f"학습: {len(train_set)}, 검증: {len(val_set)}, 테스트: {len(test_set)}")

# 실제 PyTorch 코드:
# from torch.utils.data import random_split
# train_set, val_set, test_set = random_split(
#     full_dataset, [700, 150, 150]  # 또는 비율
# )


# ===============================================================================
#  8. 실습: 학생 성적 Dataset + DataLoader
# ===============================================================================
print("\n" + "=" * 70)
print("Part 8: 실습 - 학생 성적 Dataset + DataLoader")
print("=" * 70)


class StudentScoreDataset(Dataset):
    """학생 성적 데이터셋
    입력: [수학점수, 영어점수, 과학점수, 출석률, 과제제출률]
    출력: 합격(1) / 불합격(0)
    """

    def __init__(self, num_students=200, transform=None):
        self.transform = transform
        self.features = []
        self.labels = []

        for _ in range(num_students):
            math_score = random.gauss(65, 15)
            eng_score = random.gauss(60, 20)
            sci_score = random.gauss(70, 12)
            attendance = random.uniform(50, 100)
            homework = random.uniform(30, 100)

            features = [math_score, eng_score, sci_score, attendance, homework]

            # 합격 기준: 평균 60 이상 + 출석률 70% 이상
            avg_score = (math_score + eng_score + sci_score) / 3
            passed = 1 if (avg_score >= 60 and attendance >= 70) else 0

            self.features.append(features)
            self.labels.append(passed)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        x = self.features[idx]
        y = self.labels[idx]
        if self.transform:
            x = self.transform(x)
        return x, y


# 데이터셋 생성 및 분할
transform = Compose([
    Normalize(mean=65, std=15),  # 간단한 정규화
])

full_data = StudentScoreDataset(num_students=200, transform=transform)
train_idx, val_idx, test_idx = random_split(full_data, [0.7, 0.15, 0.15])
train_data = SubsetDataset(full_data, train_idx)
val_data = SubsetDataset(full_data, val_idx)
test_data = SubsetDataset(full_data, test_idx)

print(f"\n학생 성적 데이터셋:")
print(f"  전체: {len(full_data)}명")
print(f"  학습: {len(train_data)}명, 검증: {len(val_data)}명, 테스트: {len(test_data)}명")

# 합격률 확인
pass_count = sum(1 for _, y in [full_data[i] for i in range(len(full_data))] if y == 1)
print(f"  합격률: {pass_count/len(full_data)*100:.1f}%")

# DataLoader 생성
train_loader = DataLoader(train_data, batch_size=16, shuffle=True)
val_loader = DataLoader(val_data, batch_size=16, shuffle=False)

print(f"\n학습 DataLoader: {len(train_loader)} 배치 (batch_size=16)")
print(f"검증 DataLoader: {len(val_loader)} 배치 (batch_size=16)")

# 학습 시뮬레이션
print("\n--- 학습 루프 시뮬레이션 ---")
for epoch in range(3):
    batch_count = 0
    total_samples = 0
    for x_batch, y_batch in train_loader:
        batch_count += 1
        total_samples += len(x_batch)
    print(f"  Epoch {epoch}: {batch_count} 배치, {total_samples} 샘플 처리")

# 실제 PyTorch 코드:
# train_loader = DataLoader(train_data, batch_size=16, shuffle=True, num_workers=2)
# val_loader = DataLoader(val_data, batch_size=16, shuffle=False, num_workers=2)
#
# for epoch in range(num_epochs):
#     model.train()
#     for inputs, labels in train_loader:
#         inputs, labels = inputs.to(device), labels.to(device)
#         optimizer.zero_grad()
#         outputs = model(inputs)
#         loss = criterion(outputs, labels)
#         loss.backward()
#         optimizer.step()
#
#     model.eval()
#     with torch.no_grad():
#         for inputs, labels in val_loader:
#             outputs = model(inputs)
#             # 검증 손실 및 정확도 계산


# ===============================================================================
#  핵심 정리
# ===============================================================================
print("\n" + "=" * 70)
print("핵심 정리")
print("=" * 70)
print("""
1. Dataset: __len__(), __getitem__() 두 메서드만 구현
2. DataLoader: 배치 단위 데이터 로딩 (batch_size, shuffle, num_workers)
3. transforms.Compose: 변환 파이프라인 (ToTensor → Normalize → ...)
4. 데이터 증강: 학습 시에만! (테스트에는 적용 금지)
5. collate_fn: 가변 길이 데이터 → 패딩으로 통일
6. 데이터 분할: train/val/test (70/15/15 또는 80/10/10)

[주의] 흔한 실수:
   - num_workers > 0 시 Windows에서 에러 → if __name__ == '__main__' 필요
   - 테스트 데이터에 증강 적용 → 성능 평가 왜곡
   - 데이터 정규화 시 train 세트의 통계로 test도 정규화해야 함
""")
