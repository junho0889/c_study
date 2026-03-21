# #########################################################################
#
#   PyTorch 학습 08단계: 사전학습 모델과 전이 학습
#   - torchvision.models, Feature Extraction, Fine-Tuning -
#   # 실행 방법: python 08_pretrained_transfer.py (개념 학습용, PyTorch 없이 실행 가능)
#   # PyTorch 설치: pip install torch torchvision
#
# #########################################################################

import math
import random

random.seed(42)

# ===============================================================================
#  1. 전이 학습 (Transfer Learning) 이란?
# ===============================================================================
print("=" * 70)
print("Part 1: 전이 학습 개요")
print("=" * 70)

print("""
전이 학습 = 이미 학습된 모델의 지식을 새로운 문제에 활용

비유: 영어를 잘하는 사람이 프랑스어를 배울 때
  - 알파벳, 문법 구조 등의 기초 지식을 활용
  - 처음부터 배우는 것보다 훨씬 빠름
  - 적은 데이터로도 좋은 성능 달성!

ImageNet에서 학습된 모델의 계층적 특징:
  초기 레이어: 가장자리, 색상, 질감 (범용적)
  중간 레이어: 패턴, 모양 조합
  후기 레이어: 눈, 바퀴, 글자 등 (구체적)
  마지막 레이어: 1000개 ImageNet 클래스 분류

→ 초기~중간 레이어는 대부분의 이미지 문제에 재사용 가능!
""")


# ===============================================================================
#  2. torchvision.models 주요 모델
# ===============================================================================
print("\n" + "=" * 70)
print("Part 2: torchvision.models 주요 모델")
print("=" * 70)

models_info = {
    "ResNet-18":       {"params": "11.7M", "top1": "69.8%", "year": 2015, "특징": "잔차 연결, 가볍고 빠름"},
    "ResNet-50":       {"params": "25.6M", "top1": "76.1%", "year": 2015, "특징": "잔차 연결, 가장 많이 사용"},
    "ResNet-152":      {"params": "60.2M", "top1": "78.3%", "year": 2015, "특징": "매우 깊은 ResNet"},
    "VGG-16":          {"params": "138M",  "top1": "71.6%", "year": 2014, "특징": "3x3 필터 반복, 큰 모델"},
    "EfficientNet-B0": {"params": "5.3M",  "top1": "77.1%", "year": 2019, "특징": "효율적 스케일링, 경량"},
    "EfficientNet-B7": {"params": "66M",   "top1": "84.3%", "year": 2019, "특징": "최고 성능, 무거움"},
    "MobileNet-V3":    {"params": "5.4M",  "top1": "75.2%", "year": 2019, "특징": "모바일용, 매우 가벼움"},
    "ViT-B/16":        {"params": "86.6M", "top1": "81.8%", "year": 2020, "특징": "Vision Transformer"},
}

print(f"\n{'모델':>20} {'파라미터':>10} {'Top-1':>8} {'연도':>6} {'특징'}")
print("-" * 80)
for name, info in models_info.items():
    print(f"{name:>20} {info['params']:>10} {info['top1']:>8} {info['year']:>6} {info['특징']}")

print("""
선택 가이드:
  - 빠른 실험: ResNet-18, MobileNet-V3
  - 균형 잡힌 선택: ResNet-50, EfficientNet-B0
  - 최고 성능: EfficientNet-B7, ViT
  - 모바일/엣지: MobileNet-V3, EfficientNet-B0
""")

# 실제 PyTorch 코드:
# import torchvision.models as models
#
# # 사전학습 모델 불러오기 (새 API, PyTorch 2.0+)
# from torchvision.models import resnet50, ResNet50_Weights
# model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
#
# # 또는 기존 API
# model = models.resnet50(pretrained=True)
#
# # 다른 모델들:
# model = models.vgg16(pretrained=True)
# model = models.efficientnet_b0(pretrained=True)
# model = models.mobilenet_v3_small(pretrained=True)


# ===============================================================================
#  3. 특성 추출 (Feature Extraction)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 3: 특성 추출 (Feature Extraction)")
print("=" * 70)

print("""
특성 추출 = 사전학습 모델의 가중치를 동결(freeze)하고
            마지막 분류 레이어만 새로 학습

비유: 건물 리모델링
  - 건물 뼈대(사전학습 레이어)는 그대로 유지
  - 인테리어(분류기)만 새로 변경

장점:
  - 매우 빠른 학습 (분류기 파라미터만 업데이트)
  - 적은 데이터로도 가능
  - GPU 메모리 절약

단점:
  - 사전학습 도메인과 너무 다른 경우 성능 한계
""")


class PretrainedModel:
    """사전학습 모델 시뮬레이션"""

    def __init__(self, model_name, num_classes=1000):
        self.model_name = model_name
        self.num_classes = num_classes

        # 모델 구조 시뮬레이션
        if "resnet" in model_name:
            self.layers = {
                "conv1": {"type": "Conv2d", "params": 9408, "frozen": False},
                "bn1": {"type": "BatchNorm2d", "params": 128, "frozen": False},
                "layer1": {"type": "ResBlock x2", "params": 147968, "frozen": False},
                "layer2": {"type": "ResBlock x2", "params": 526848, "frozen": False},
                "layer3": {"type": "ResBlock x2", "params": 2100224, "frozen": False},
                "layer4": {"type": "ResBlock x2", "params": 8396800, "frozen": False},
                "avgpool": {"type": "AdaptiveAvgPool2d", "params": 0, "frozen": False},
                "fc": {"type": f"Linear(512, {num_classes})", "params": 512 * num_classes + num_classes, "frozen": False},
            }
        else:
            self.layers = {
                "features": {"type": "ConvBlocks", "params": 5000000, "frozen": False},
                "classifier": {"type": f"Linear(→{num_classes})", "params": num_classes * 1000, "frozen": False},
            }

    def freeze_backbone(self):
        """백본(특성 추출기) 동결"""
        for name, layer in self.layers.items():
            if name != "fc" and name != "classifier":
                layer["frozen"] = True

    def replace_classifier(self, new_num_classes):
        """분류기 교체"""
        self.num_classes = new_num_classes
        if "fc" in self.layers:
            self.layers["fc"] = {
                "type": f"Linear(512, {new_num_classes})",
                "params": 512 * new_num_classes + new_num_classes,
                "frozen": False
            }
        elif "classifier" in self.layers:
            self.layers["classifier"] = {
                "type": f"Linear(→{new_num_classes})",
                "params": new_num_classes * 1000 + new_num_classes,
                "frozen": False
            }

    def count_trainable(self):
        """학습 가능한 파라미터 수"""
        return sum(l["params"] for l in self.layers.values() if not l["frozen"])

    def count_total(self):
        """전체 파라미터 수"""
        return sum(l["params"] for l in self.layers.values())

    def print_layers(self):
        print(f"\n  {'레이어':>15} {'타입':>25} {'파라미터':>10} {'상태':>10}")
        print("  " + "-" * 65)
        for name, layer in self.layers.items():
            status = "[동결] 동결" if layer["frozen"] else "[학습] 학습"
            print(f"  {name:>15} {layer['type']:>25} {layer['params']:>10,} {status:>10}")
        print(f"\n  학습 가능: {self.count_trainable():,} / 전체: {self.count_total():,}")


# 특성 추출 과정 시연
print("\n--- 특성 추출 과정 ---")

# Step 1: 사전학습 모델 로드
model = PretrainedModel("resnet18", num_classes=1000)
print("\n1. 사전학습 모델 (ImageNet 1000 클래스):")
model.print_layers()

# Step 2: 백본 동결
model.freeze_backbone()
print("\n2. 백본 동결 후:")

# Step 3: 분류기 교체 (1000 → 5 클래스)
model.replace_classifier(new_num_classes=5)
print("\n3. 분류기 교체 (5 클래스):")
model.print_layers()

# 실제 PyTorch 코드:
# # 1. 사전학습 모델 로드
# model = models.resnet50(pretrained=True)
#
# # 2. 모든 파라미터 동결
# for param in model.parameters():
#     param.requires_grad = False
#
# # 3. 마지막 분류기 교체
# num_features = model.fc.in_features  # 2048
# model.fc = nn.Sequential(
#     nn.Linear(num_features, 256),
#     nn.ReLU(),
#     nn.Dropout(0.5),
#     nn.Linear(256, num_classes)
# )
# # 새 분류기만 requires_grad=True (자동)
#
# # 4. 학습 (분류기만)
# optimizer = torch.optim.Adam(model.fc.parameters(), lr=0.001)


# ===============================================================================
#  4. 미세 조정 (Fine-Tuning)
# ===============================================================================
print("\n" + "=" * 70)
print("Part 4: 미세 조정 (Fine-Tuning)")
print("=" * 70)

print("""
미세 조정 = 사전학습 모델의 일부 레이어를 "해동"하여 함께 학습

비유: 건물 리모델링 + 일부 구조 변경
  - 기초(초기 레이어)는 유지
  - 상위 층(후기 레이어)은 목적에 맞게 수정

전략:
  1단계: 분류기만 학습 (특성 추출)
  2단계: 후기 레이어 해동 + 작은 학습률로 미세 조정

학습률 차별화 (Discriminative Learning Rate):
  - 초기 레이어: 아주 작은 학습률 (1e-5)
  - 중간 레이어: 중간 학습률 (1e-4)
  - 분류기: 큰 학습률 (1e-3)
""")


class FineTuningPipeline:
    """미세 조정 파이프라인 시뮬레이션"""

    def __init__(self, model):
        self.model = model

    def unfreeze_layers(self, layer_names):
        """특정 레이어 해동"""
        for name in layer_names:
            if name in self.model.layers:
                self.model.layers[name]["frozen"] = False

    def setup_discriminative_lr(self):
        """학습률 차별화 설정"""
        lr_groups = {}
        for name, layer in self.model.layers.items():
            if layer["frozen"]:
                lr_groups[name] = 0.0
            elif name in ["layer4", "layer3"]:
                lr_groups[name] = 1e-4
            elif name in ["fc", "classifier"]:
                lr_groups[name] = 1e-3
            else:
                lr_groups[name] = 1e-5
        return lr_groups


# 미세 조정 시연
print("\n--- 미세 조정 과정 ---")

# 1단계: 특성 추출 (이미 완료)
print("\n1단계: 특성 추출로 분류기 학습 (위에서 완료)")

# 2단계: 후기 레이어 해동
pipeline = FineTuningPipeline(model)
pipeline.unfreeze_layers(["layer3", "layer4"])
print("\n2단계: layer3, layer4 해동:")
model.print_layers()

# 학습률 차별화
lr_groups = pipeline.setup_discriminative_lr()
print("\n학습률 차별화:")
for name, lr in lr_groups.items():
    if lr > 0:
        print(f"  {name:>15}: lr = {lr}")

# 실제 PyTorch 코드:
# # 1단계: 분류기만 학습 (5~10 에폭)
# for param in model.parameters():
#     param.requires_grad = False
# model.fc = nn.Linear(2048, num_classes)
# optimizer = torch.optim.Adam(model.fc.parameters(), lr=1e-3)
# train(model, epochs=10)
#
# # 2단계: 미세 조정 (후기 레이어 해동)
# for param in model.layer4.parameters():
#     param.requires_grad = True
# for param in model.layer3.parameters():
#     param.requires_grad = True
#
# # 학습률 차별화
# optimizer = torch.optim.Adam([
#     {'params': model.layer3.parameters(), 'lr': 1e-5},
#     {'params': model.layer4.parameters(), 'lr': 1e-4},
#     {'params': model.fc.parameters(), 'lr': 1e-3},
# ])
# train(model, epochs=20)


# ===============================================================================
#  5. 모델 구조 수정
# ===============================================================================
print("\n" + "=" * 70)
print("Part 5: 모델 구조 수정")
print("=" * 70)

print("""
사전학습 모델의 구조를 목적에 맞게 수정하는 방법들:

1. 마지막 레이어 교체: 가장 기본적
2. 중간 특성 추출: 특정 레이어의 출력을 가져옴
3. 멀티 헤드: 여러 출력을 동시에 생성
""")

# 1. 마지막 레이어 교체
print("\n--- 1. 마지막 레이어 교체 ---")
print("""
ResNet의 마지막 레이어 (fc) 교체:
  원본:  fc = Linear(2048, 1000)     # ImageNet 1000 클래스
  수정:  fc = Sequential(
             Linear(2048, 512),
             ReLU(),
             Dropout(0.5),
             Linear(512, num_classes)  # 우리 클래스 수
         )
""")

# 실제 PyTorch 코드:
# # ResNet fc 교체
# num_features = model.fc.in_features  # 2048
# model.fc = nn.Sequential(
#     nn.Linear(num_features, 512),
#     nn.ReLU(),
#     nn.Dropout(0.5),
#     nn.Linear(512, num_classes)
# )
#
# # VGG classifier 교체
# model.classifier[-1] = nn.Linear(4096, num_classes)
#
# # EfficientNet classifier 교체
# num_features = model.classifier[1].in_features
# model.classifier = nn.Sequential(
#     nn.Dropout(0.2),
#     nn.Linear(num_features, num_classes)
# )

# 2. 중간 특성 추출
print("\n--- 2. 중간 특성 추출 ---")
print("""
특정 레이어의 출력을 추출하여 다른 목적으로 사용

사용 예:
  - 이미지 유사도 검색 (임베딩 추출)
  - 시각화 (특성 맵 확인)
  - 스타일 전이 (여러 레이어의 특성 결합)
""")

# 실제 PyTorch 코드:
# # 방법 1: Hook 사용
# features = {}
# def hook_fn(module, input, output):
#     features['layer4'] = output
#
# model.layer4.register_forward_hook(hook_fn)
# output = model(input)
# layer4_features = features['layer4']  # 중간 특성!
#
# # 방법 2: 모델 잘라서 사용
# feature_extractor = nn.Sequential(*list(model.children())[:-2])
# features = feature_extractor(input)  # (batch, 2048, 7, 7)

# 3. 멀티 헤드 모델
print("\n--- 3. 멀티 헤드 모델 ---")

class MultiHeadModel:
    """여러 출력을 가진 모델 (시뮬레이션)"""

    def __init__(self, backbone_output=2048):
        self.backbone = f"ResNet50 backbone (→{backbone_output})"
        self.head1 = f"분류 head: Linear({backbone_output}, 10)"     # 카테고리
        self.head2 = f"회귀 head: Linear({backbone_output}, 1)"      # 가격
        self.head3 = f"임베딩 head: Linear({backbone_output}, 128)"  # 유사도

    def describe(self):
        print(f"  백본: {self.backbone}")
        print(f"  헤드 1: {self.head1}")
        print(f"  헤드 2: {self.head2}")
        print(f"  헤드 3: {self.head3}")

multi_model = MultiHeadModel()
print("\n멀티 헤드 모델 구조:")
multi_model.describe()

# 실제 PyTorch 코드:
# class MultiHeadModel(nn.Module):
#     def __init__(self, backbone, num_classes, embed_dim):
#         super().__init__()
#         self.backbone = backbone
#         num_features = backbone.fc.in_features
#         backbone.fc = nn.Identity()  # 분류기 제거
#
#         self.cls_head = nn.Linear(num_features, num_classes)
#         self.reg_head = nn.Linear(num_features, 1)
#         self.embed_head = nn.Linear(num_features, embed_dim)
#
#     def forward(self, x):
#         features = self.backbone(x)
#         cls_out = self.cls_head(features)
#         reg_out = self.reg_head(features)
#         embed_out = self.embed_head(features)
#         return cls_out, reg_out, embed_out


# ===============================================================================
#  6. 전이 학습 실전 가이드
# ===============================================================================
print("\n" + "=" * 70)
print("Part 6: 전이 학습 실전 가이드")
print("=" * 70)

print("""
데이터 양과 도메인 유사도에 따른 전략:

+------------------------------------------------------+
|          도메인 유사도 높음    도메인 유사도 낮음     |
|                                                      |
| 데이터   특성 추출             전체 미세 조정         |
| 많음     (빠르고 효과적)       (새 도메인 적응)       |
|                                                      |
| 데이터   특성 추출             특성 추출              |
| 적음     (과적합 방지)         (조심스럽게, 정규화)   |
+------------------------------------------------------+

데이터 전처리 주의사항:
  - 사전학습 모델과 같은 정규화 사용!
  - ImageNet 정규화: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
  - 입력 크기: 보통 224x224 (ResNet), 일부 모델은 299x299 (Inception)
""")


# ===============================================================================
#  7. 실습: 사전학습 모델 활용 분류 파이프라인
# ===============================================================================
print("\n" + "=" * 70)
print("Part 7: 실습 - 전이 학습 전체 파이프라인")
print("=" * 70)


class TransferLearningPipeline:
    """전이 학습 전체 파이프라인 시뮬레이션"""

    def __init__(self, model_name, num_classes, strategy="feature_extraction"):
        self.model_name = model_name
        self.num_classes = num_classes
        self.strategy = strategy

    def step1_load_pretrained(self):
        print(f"\n[Step 1] 사전학습 모델 로드: {self.model_name}")
        print(f"  → ImageNet 1000 클래스로 학습된 가중치 로드")

    def step2_modify_model(self):
        print(f"\n[Step 2] 모델 수정 (전략: {self.strategy})")
        if self.strategy == "feature_extraction":
            print(f"  → 모든 레이어 동결")
            print(f"  → 분류기 교체: 1000 → {self.num_classes} 클래스")
        else:
            print(f"  → 분류기 교체: 1000 → {self.num_classes} 클래스")
            print(f"  → 후기 레이어 해동 + 학습률 차별화")

    def step3_prepare_data(self):
        print(f"\n[Step 3] 데이터 준비")
        print(f"  → ImageNet 정규화 적용: mean=[0.485, 0.456, 0.406]")
        print(f"  → 이미지 크기 조절: 224x224")
        print(f"  → 데이터 증강 (학습 시)")

    def step4_train(self):
        print(f"\n[Step 4] 학습")
        lr = 0.001 if self.strategy == "feature_extraction" else 0.0001

        # 시뮬레이션
        for epoch in range(5):
            train_loss = 1.0 * math.exp(-0.5 * epoch) + random.gauss(0, 0.02)
            val_loss = 1.1 * math.exp(-0.4 * epoch) + random.gauss(0, 0.03)
            train_acc = min(0.95, 0.5 + 0.1 * epoch + random.gauss(0, 0.02))
            val_acc = min(0.93, 0.45 + 0.1 * epoch + random.gauss(0, 0.03))
            print(f"  Epoch {epoch}: train_loss={max(0.01,train_loss):.4f}, "
                  f"val_loss={max(0.01,val_loss):.4f}, "
                  f"train_acc={train_acc:.4f}, val_acc={val_acc:.4f}")

    def step5_evaluate(self):
        print(f"\n[Step 5] 평가")
        acc = 0.89 + random.gauss(0, 0.02)
        print(f"  테스트 정확도: {acc:.2%}")
        print(f"  → 전이 학습 없이 학습했을 때보다 훨씬 좋은 성능!")

    def run(self):
        print(f"\n{'='*60}")
        print(f"전이 학습 파이프라인: {self.model_name} → {self.num_classes}클래스")
        print(f"전략: {self.strategy}")
        print(f"{'='*60}")
        self.step1_load_pretrained()
        self.step2_modify_model()
        self.step3_prepare_data()
        self.step4_train()
        self.step5_evaluate()


# 특성 추출
pipeline1 = TransferLearningPipeline("ResNet-50", num_classes=5,
                                      strategy="feature_extraction")
pipeline1.run()

# 미세 조정
pipeline2 = TransferLearningPipeline("ResNet-50", num_classes=5,
                                      strategy="fine_tuning")
pipeline2.run()


# 실제 PyTorch 전체 코드:
# import torch
# import torch.nn as nn
# from torchvision import models, transforms, datasets
# from torch.utils.data import DataLoader
#
# # 1. 데이터 준비
# train_transform = transforms.Compose([
#     transforms.RandomResizedCrop(224),
#     transforms.RandomHorizontalFlip(),
#     transforms.ToTensor(),
#     transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
# ])
# val_transform = transforms.Compose([
#     transforms.Resize(256),
#     transforms.CenterCrop(224),
#     transforms.ToTensor(),
#     transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
# ])
#
# train_dataset = datasets.ImageFolder('data/train', transform=train_transform)
# val_dataset = datasets.ImageFolder('data/val', transform=val_transform)
# train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=4)
# val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False, num_workers=4)
#
# # 2. 모델 설정
# model = models.resnet50(pretrained=True)
# for param in model.parameters():
#     param.requires_grad = False
#
# num_features = model.fc.in_features
# model.fc = nn.Sequential(
#     nn.Linear(num_features, 256),
#     nn.ReLU(),
#     nn.Dropout(0.5),
#     nn.Linear(256, len(train_dataset.classes))
# )
# model = model.to(device)
#
# # 3. 학습
# criterion = nn.CrossEntropyLoss()
# optimizer = torch.optim.Adam(model.fc.parameters(), lr=0.001)
# scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)
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
#     scheduler.step()


# ===============================================================================
#  핵심 정리
# ===============================================================================
print("\n" + "=" * 70)
print("핵심 정리")
print("=" * 70)
print("""
1. 전이 학습: 사전학습된 지식을 새 문제에 활용 → 빠르고 적은 데이터로 가능

2. 특성 추출 (Feature Extraction):
   - 백본 동결 + 분류기만 학습
   - 빠르고 안전, 적은 데이터에 적합

3. 미세 조정 (Fine-Tuning):
   - 후기 레이어 해동 + 학습률 차별화
   - 더 좋은 성능, 데이터가 충분할 때

4. 모델 구조 수정:
   - fc/classifier 교체가 가장 기본
   - Hook으로 중간 특성 추출 가능
   - 멀티 헤드로 여러 태스크 동시 수행

5. 데이터 전처리: 사전학습 모델과 같은 정규화 사용!

[주의] 흔한 실수:
   - ImageNet 정규화 안 적용 → 성능 저하
   - 동결 안 하고 작은 데이터로 학습 → 과적합
   - 학습률이 너무 크면 사전학습 가중치 파괴
""")
