# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#   LLM 학습 07단계: 파인튜닝 (Fine-Tuning)
#   ─ 범용 모델을 특정 목적에 맞게 조정하기 ─
#
#   비유: 전학생의 적응
#     사전학습 = 기본 교육 (국어, 수학, 과학 등 기초 지식)
#     파인튜닝 = 전공 선택 (의대, 법대, 공대 등 전문 교육)
#     이미 기초가 있으니 전문 과정을 훨씬 빨리 배울 수 있습니다.
#
#   실행 방법:
#     python 07_fine_tuning.py
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import random


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 1: 사전학습 vs 파인튜닝
# ─────────────────────────────────────────────────────────────────────────

def lesson1_pretraining_vs_finetuning():
    """
    사전학습(Pre-training): 거대한 텍스트로 일반 지식을 배움
    파인튜닝(Fine-tuning): 특정 작업에 맞게 추가 학습

    비유: 자격증 취득 과정
      사전학습 = 대학교 4년 (폭넓은 기초 지식)
      파인튜닝 = 전문 자격증 공부 (특정 분야 집중)
    """
    print("=" * 70)
    print("[레슨 1] 사전학습 vs 파인튜닝")
    print("=" * 70)
    print()
    print("  ┌─────────────────────────────────────────────────────────┐")
    print("  │  단계         │  데이터           │  목적              │")
    print("  ├─────────────────────────────────────────────────────────┤")
    print("  │  사전학습     │  인터넷 전체 텍스트│  언어 이해 전반    │")
    print("  │  (수주~수개월)│  수TB             │  '다음 단어 예측'  │")
    print("  ├─────────────────────────────────────────────────────────┤")
    print("  │  파인튜닝     │  특정 작업 데이터  │  특정 작업 성능↑   │")
    print("  │  (수시간~며칠)│  수천~수만 건      │  감정분석, Q&A 등  │")
    print("  └─────────────────────────────────────────────────────────┘")
    print()

    # 시뮬레이션: 사전학습된 모델의 가중치
    random.seed(42)
    pretrained_weights = [random.gauss(0, 1) for _ in range(6)]

    print("  사전학습된 가중치 (일반 지식):")
    print(f"    {[round(w, 3) for w in pretrained_weights]}")
    print()

    # 파인튜닝: 작은 학습률로 조금만 조정
    fine_tune_lr = 0.01
    fine_tune_grads = [random.gauss(0, 0.5) for _ in range(6)]
    finetuned_weights = [w - fine_tune_lr * g
                         for w, g in zip(pretrained_weights, fine_tune_grads)]

    print("  파인튜닝 후 가중치 (약간만 변화):")
    print(f"    {[round(w, 3) for w in finetuned_weights]}")
    print()

    # 변화량 확인
    changes = [abs(a - b) for a, b in zip(pretrained_weights, finetuned_weights)]
    print("  변화량:")
    print(f"    {[round(c, 4) for c in changes]}")
    print("  → 아주 작은 변화! 기존 지식을 유지하면서 미세 조정")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 2: 전이 학습 (Transfer Learning)
# ─────────────────────────────────────────────────────────────────────────

def lesson2_transfer_learning():
    """
    전이 학습: 한 분야에서 배운 지식을 다른 분야에 활용.

    비유: 피아노 치는 사람이 키보드 타자도 잘 치는 것
      - 손가락 근육, 리듬감이 이미 발달해 있음
      - 새 기술을 처음부터 배울 필요 없이 빨리 적응
    """
    print("=" * 70)
    print("[레슨 2] 전이 학습 (Transfer Learning)")
    print("=" * 70)
    print()

    # 전이 학습 시뮬레이션
    # 기존 모델: 감정 분석 학습
    # 새 작업: 상품 리뷰 감정 분류

    base_knowledge = {
        "긍정 표현 인식": 0.9,
        "부정 표현 인식": 0.85,
        "문법 이해": 0.95,
        "맥락 파악": 0.8,
        "상품 용어": 0.1,     # 이것만 부족
        "리뷰 패턴": 0.05,    # 이것도 부족
    }

    print("  사전학습 모델의 능력치:")
    for skill, level in base_knowledge.items():
        bar = "#" * int(level * 30)
        print(f"    {skill:>15s}: {level:.2f} {bar}")
    print()

    # 파인튜닝 후
    after_finetune = base_knowledge.copy()
    after_finetune["상품 용어"] = 0.8
    after_finetune["리뷰 패턴"] = 0.75
    after_finetune["맥락 파악"] = 0.85  # 기존 능력도 약간 향상

    print("  파인튜닝 후 능력치:")
    for skill, level in after_finetune.items():
        bar = "#" * int(level * 30)
        change = level - base_knowledge[skill]
        marker = f" (+{change:.2f})" if change > 0.01 else ""
        print(f"    {skill:>15s}: {level:.2f} {bar}{marker}")
    print()
    print("  → 기존 지식(긍정/부정 인식)은 유지하면서")
    print("    부족한 부분(상품 용어, 리뷰)만 빠르게 학습!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 3: LoRA (Low-Rank Adaptation)
# ─────────────────────────────────────────────────────────────────────────

def lesson3_lora():
    """
    LoRA: 원래 가중치는 고정하고, 작은 행렬을 추가해서 학습.

    비유: 교과서에 직접 쓰지 않고 포스트잇을 붙이는 것
      - 교과서(원래 가중치) = 건드리지 않음
      - 포스트잇(LoRA 행렬) = 추가 메모만 학습
      - 포스트잇은 작으니 메모리 절약!

    수학: W_new = W_original + A × B
      W_original: 고정 (예: 4096×4096)
      A: 학습 (4096×8)   ← rank가 낮음!
      B: 학습 (8×4096)
      파라미터 수: 4096² → 4096×8×2 = 65536 (99.8% 감소!)
    """
    print("=" * 70)
    print("[레슨 3] LoRA (Low-Rank Adaptation)")
    print("=" * 70)
    print()

    d = 8       # 원래 가중치 차원 (실제는 4096 등)
    rank = 2    # LoRA rank (실제는 4~64 등)

    original_params = d * d
    lora_params = d * rank * 2  # A + B

    print(f"  원래 가중치: {d}×{d} = {original_params}개 파라미터 (고정)")
    print(f"  LoRA 추가:   {d}×{rank} + {rank}×{d} = {lora_params}개 파라미터 (학습)")
    print(f"  파라미터 절감: {(1 - lora_params/original_params)*100:.1f}%!")
    print()

    # 수치 예제
    print("  수치 예제 (4×4 가중치, rank=2):")
    print()

    # 원래 가중치 (고정)
    W = [[1.0, 0.0, 0.5, 0.2],
         [0.3, 1.0, 0.0, 0.4],
         [0.1, 0.5, 1.0, 0.3],
         [0.2, 0.0, 0.3, 1.0]]

    # LoRA 행렬 (학습됨)
    A = [[0.1, 0.2],
         [0.0, 0.1],
         [-0.1, 0.0],
         [0.1, -0.1]]

    B = [[0.2, 0.0, -0.1, 0.1],
         [0.1, 0.3, 0.0, -0.2]]

    # A × B 계산
    AB = [[sum(A[i][k] * B[k][j] for k in range(rank))
           for j in range(4)] for i in range(4)]

    # W + AB = 새로운 가중치
    W_new = [[W[i][j] + AB[i][j] for j in range(4)] for i in range(4)]

    print("  원래 W:")
    for row in W:
        print(f"    [{', '.join(f'{v:>5.2f}' for v in row)}]")
    print()
    print("  A×B (LoRA 보정):")
    for row in AB:
        print(f"    [{', '.join(f'{v:>5.3f}' for v in row)}]")
    print()
    print("  W + A×B (최종):")
    for row in W_new:
        print(f"    [{', '.join(f'{v:>5.3f}' for v in row)}]")
    print()
    print("  → 원래 W는 전혀 안 건드리고, 작은 A,B만 학습!")
    print("  → GPU 메모리 절약, 여러 작업용 어댑터를 쉽게 교체 가능")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 4: 전체 파인튜닝 vs 파라미터 효율적 방법
# ─────────────────────────────────────────────────────────────────────────

def lesson4_full_vs_peft():
    """
    파인튜닝 방법 비교.
    """
    print("=" * 70)
    print("[레슨 4] 전체 파인튜닝 vs 파라미터 효율적 방법 (PEFT)")
    print("=" * 70)
    print()
    print("  ┌───────────────┬──────────────┬────────────┬──────────────┐")
    print("  │  방법         │ 학습 파라미터│  메모리    │  성능        │")
    print("  ├───────────────┼──────────────┼────────────┼──────────────┤")
    print("  │ 전체 파인튜닝 │ 100%         │  매우 큼   │  최고        │")
    print("  │ LoRA          │ 0.1~1%       │  적음      │  거의 동일   │")
    print("  │ 프롬프트 튜닝 │ < 0.01%      │  매우 적음 │  좋음        │")
    print("  │ 어댑터        │ 1~5%         │  적음      │  좋음        │")
    print("  └───────────────┴──────────────┴────────────┴──────────────┘")
    print()

    # 실제 모델 크기 비교
    models = [
        ("GPT-2",    "124M",   124_000_000),
        ("LLaMA-7B", "7B",     7_000_000_000),
        ("LLaMA-70B","70B",    70_000_000_000),
    ]

    print("  실제 모델별 파인튜닝 파라미터 수:")
    print()
    for name, size, params in models:
        full = params
        lora = int(params * 0.005)  # 약 0.5%
        print(f"    {name} ({size}):")
        print(f"      전체 파인튜닝: {full:>15,}개")
        print(f"      LoRA (0.5%):  {lora:>15,}개")
        print()

    print("  → LoRA를 쓰면 70B 모델도 일반 GPU에서 파인튜닝 가능!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 5: 인스트럭션 튜닝과 RLHF
# ─────────────────────────────────────────────────────────────────────────

def lesson5_instruction_tuning_rlhf():
    """
    인스트럭션 튜닝: "질문-답변" 형태로 모델을 가르침
    RLHF: 사람의 피드백으로 모델을 교정

    비유: 학생 교육 과정
      사전학습 = 교과서를 독학 (지식은 있지만 대화 못 함)
      인스트럭션 튜닝 = 선생님과 대화 연습 (질문에 답하는 법 학습)
      RLHF = 실전 피드백 (사람이 "이 답변이 더 좋아"라고 알려줌)
    """
    print("=" * 70)
    print("[레슨 5] 인스트럭션 튜닝과 RLHF")
    print("=" * 70)
    print()

    # 인스트럭션 튜닝 데이터 예시
    print("  1. 인스트럭션 튜닝 데이터 예시:")
    print()
    instruction_examples = [
        {
            "instruction": "다음 문장을 영어로 번역하세요.",
            "input": "오늘 날씨가 좋습니다.",
            "output": "The weather is nice today."
        },
        {
            "instruction": "다음 텍스트의 감정을 분석하세요.",
            "input": "이 영화 정말 재미있었어요!",
            "output": "긍정적인 감정입니다."
        },
        {
            "instruction": "핵심을 요약하세요.",
            "input": "인공지능은 데이터를 학습하여 패턴을 인식하고...",
            "output": "AI는 데이터에서 패턴을 학습하는 기술이다."
        },
    ]

    for i, ex in enumerate(instruction_examples):
        print(f"    예시 {i+1}:")
        print(f"      지시: {ex['instruction']}")
        print(f"      입력: {ex['input']}")
        print(f"      출력: {ex['output']}")
        print()

    # RLHF 과정
    print("  2. RLHF 과정:")
    print()
    print("    ┌────────────────────────────────────────────────┐")
    print("    │  Step 1: 모델이 여러 답변을 생성                │")
    print("    │    답변A: '날씨가 좋아서 산책하세요.'           │")
    print("    │    답변B: '오늘 맑고 기온은 22도입니다.'       │")
    print("    │                                                │")
    print("    │  Step 2: 사람이 순위를 매김                     │")
    print("    │    '답변B가 더 유용하고 정확해!'               │")
    print("    │                                                │")
    print("    │  Step 3: 보상 모델 학습                        │")
    print("    │    사람 선호를 예측하는 모델을 만듦             │")
    print("    │                                                │")
    print("    │  Step 4: PPO로 모델 업데이트                   │")
    print("    │    보상 모델의 점수를 높이도록 학습             │")
    print("    └────────────────────────────────────────────────┘")
    print()

    # 단순화된 보상 점수 시뮬레이션
    responses = [
        ("직접적이고 유용한 답변", 0.9),
        ("정확하지만 딱딱한 답변", 0.7),
        ("길지만 핵심 없는 답변",  0.3),
        ("무관한 답변",            0.1),
    ]

    print("  보상 점수 시뮬레이션:")
    for resp, score in responses:
        bar = "#" * int(score * 30)
        print(f"    {resp:>25s}: {score:.1f} {bar}")
    print()
    print("  → RLHF로 사람이 선호하는 답변 스타일을 학습합니다!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■" * 72)
    print("  LLM 07단계 : 파인튜닝 (Fine-Tuning)")
    print("  비유: 범용 교육을 받은 학생이 전공을 선택하는 과정")
    print("■" * 72)
    print()

    lesson1_pretraining_vs_finetuning()
    lesson2_transfer_learning()
    lesson3_lora()
    lesson4_full_vs_peft()
    lesson5_instruction_tuning_rlhf()


if __name__ == "__main__":
    main()
