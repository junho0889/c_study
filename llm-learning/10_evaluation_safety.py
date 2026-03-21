# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#   LLM 학습 10단계: 평가와 안전성
#   ─ LLM의 성적표와 안전장치 이해하기 ─
#
#   비유: 자동차 출시 전 검사
#     성능 테스트 = 벤치마크 (MMLU, HumanEval)
#     안전 검사 = 충돌 테스트, 브레이크 테스트
#     결함 찾기 = 레드팀 (해커처럼 약점 찾기)
#     LLM도 출시 전에 이런 검사를 거칩니다.
#
#   실행 방법:
#     python 10_evaluation_safety.py
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 1: LLM 벤치마크
# ─────────────────────────────────────────────────────────────────────────

def lesson1_benchmarks():
    """
    벤치마크: LLM의 능력을 측정하는 표준 시험.

    비유: 학교 시험 종류
      MMLU = 수능 (종합 지식)
      HumanEval = 코딩 테스트
      GSM8K = 수학 문제 풀기
      TruthfulQA = 거짓말 탐지 테스트
    """
    print("=" * 70)
    print("[레슨 1] LLM 벤치마크")
    print("=" * 70)
    print()

    benchmarks = [
        {
            "name": "MMLU",
            "full_name": "Massive Multitask Language Understanding",
            "what": "57개 분야 객관식 문제 (역사, 과학, 수학 등)",
            "measures": "종합 지식",
            "scores": {"GPT-4": 86.4, "GPT-3.5": 70.0, "LLaMA-70B": 68.9},
        },
        {
            "name": "HumanEval",
            "full_name": "Human Evaluation Coding Benchmark",
            "what": "164개 파이썬 코딩 문제",
            "measures": "코드 생성 능력",
            "scores": {"GPT-4": 67.0, "GPT-3.5": 48.1, "Claude-3": 84.9},
        },
        {
            "name": "GSM8K",
            "full_name": "Grade School Math 8K",
            "what": "초등학교 수준 수학 문제 8,500개",
            "measures": "수학적 추론",
            "scores": {"GPT-4": 92.0, "GPT-3.5": 57.1, "LLaMA-70B": 54.4},
        },
    ]

    for bench in benchmarks:
        print(f"  {bench['name']} ({bench['full_name']})")
        print(f"    내용: {bench['what']}")
        print(f"    측정: {bench['measures']}")
        print(f"    점수:")
        for model, score in bench["scores"].items():
            bar = "#" * int(score / 3)
            print(f"      {model:>12s}: {score:>5.1f}% {bar}")
        print()

    # MMLU 문제 시뮬레이션
    print("  MMLU 예시 문제:")
    print("    Q: 광합성에서 빛에너지를 흡수하는 색소는?")
    print("    A) 헤모글로빈  B) 엽록소  C) 멜라닌  D) 카로틴")
    print("    정답: B) 엽록소")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 2: 환각 (Hallucination)
# ─────────────────────────────────────────────────────────────────────────

def lesson2_hallucination():
    """
    환각: LLM이 사실이 아닌 내용을 자신있게 말하는 현상.

    비유: 시험에서 모르는 문제를 자신있게 틀리게 쓰는 학생
      - 정말 모르면서도 그럴듯한 답을 만들어냄
      - 듣는 사람은 자신있는 태도에 속을 수 있음
    """
    print("=" * 70)
    print("[레슨 2] 환각 (Hallucination)")
    print("=" * 70)
    print()
    print("  환각 = LLM이 사실이 아닌 정보를 자신있게 생성하는 것")
    print()

    # 환각 유형
    hallucination_types = [
        {
            "type": "사실 오류",
            "example_q": "한국의 수도는?",
            "bad_answer": "한국의 수도는 부산입니다.",
            "why": "학습 데이터에서 '한국'과 '부산'이 자주 등장해서",
        },
        {
            "type": "존재하지 않는 출처",
            "example_q": "이 정보의 출처는?",
            "bad_answer": "Smith et al. (2023) 논문에 따르면...",
            "why": "그럴듯한 인용을 만들어냄 (실제 논문 아님)",
        },
        {
            "type": "논리적 오류",
            "example_q": "3의 배수 중 짝수를 나열하면?",
            "bad_answer": "3, 6, 9, 12...",
            "why": "3과 9는 홀수인데 포함시킴",
        },
    ]

    for h in hallucination_types:
        print(f"  [{h['type']}]")
        print(f"    질문: {h['example_q']}")
        print(f"    환각 답변: {h['bad_answer']}")
        print(f"    원인: {h['why']}")
        print()

    # 환각 감지 시뮬레이션
    print("  환각 감지 방법:")
    print("    1. 사실 확인 (Fact-checking): 외부 DB와 대조")
    print("    2. 자기 일관성 (Self-consistency): 같은 질문 여러 번 →")
    print("       답이 달라지면 환각일 가능성↑")
    print("    3. 확신도 측정: 토큰 확률이 낮으면 불확실한 부분")
    print()

    # 자기 일관성 시뮬레이션
    print("  자기 일관성 검사 예시:")
    question = "대한민국의 인구는?"
    answers = [
        "약 5,100만 명입니다.",
        "약 5,100만 명입니다.",
        "약 5,200만 명입니다.",
        "약 5,100만 명입니다.",
        "약 4,800만 명입니다.",
    ]

    from collections import Counter
    counts = Counter(answers)
    print(f"    질문: '{question}'")
    print(f"    5번 질문한 답변:")
    for ans, cnt in counts.most_common():
        print(f"      '{ans}' × {cnt}번")

    majority = counts.most_common(1)[0]
    consistency = majority[1] / len(answers)
    print(f"    일관성: {consistency:.0%} → ", end="")
    print("신뢰도 높음" if consistency > 0.6 else "환각 가능성 있음")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 3: 편향 (Bias)
# ─────────────────────────────────────────────────────────────────────────

def lesson3_bias():
    """
    편향: LLM이 특정 집단에 대해 불공정한 답변을 하는 문제.

    비유: 편향된 교과서로 공부한 학생
      - 교과서에 특정 관점만 있으면 학생도 그렇게 생각
      - LLM도 학습 데이터의 편향을 그대로 학습할 수 있음
    """
    print("=" * 70)
    print("[레슨 3] 편향 (Bias)")
    print("=" * 70)
    print()

    # 편향 유형
    print("  편향의 종류:")
    print()
    print("  ┌──────────────┬─────────────────────────────────────────┐")
    print("  │  유형        │  설명                                   │")
    print("  ├──────────────┼─────────────────────────────────────────┤")
    print("  │ 성별 편향    │  '간호사→여성, 엔지니어→남성' 고정관념 │")
    print("  │ 문화 편향    │  서구 중심적 관점                       │")
    print("  │ 확증 편향    │  기존 믿음을 강화하는 정보만 제공       │")
    print("  │ 표현 편향    │  특정 집단의 데이터가 부족              │")
    print("  └──────────────┴─────────────────────────────────────────┘")
    print()

    # 편향 감지 시뮬레이션
    print("  편향 감지 시뮬레이션:")
    print("    '___는 훌륭한 의사입니다'에 이름을 넣었을 때 확률:")
    print()

    names_and_probs = [
        ("김철수", 0.35, "남성 한국인"),
        ("이영희", 0.25, "여성 한국인"),
        ("John",   0.20, "남성 영어권"),
        ("Maria",  0.10, "여성 영어권"),
        ("Ahmed",  0.05, "남성 아랍권"),
    ]

    for name, prob, desc in names_and_probs:
        bar = "#" * int(prob * 60)
        print(f"    {name:>8s} ({desc}): {prob:.2f} {bar}")
    print()
    print("  → 이상적으로는 모든 이름이 비슷한 확률이어야 함")
    print("  → 편향이 있으면 특정 이름이 더 높게 나옴")
    print()

    # 완화 방법
    print("  편향 완화 방법:")
    print("    1. 다양한 데이터로 학습")
    print("    2. 편향 감사(audit) 정기 수행")
    print("    3. 출력 필터링")
    print("    4. 사용자 피드백 반영")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 4: 안전 가드레일과 레드팀
# ─────────────────────────────────────────────────────────────────────────

def lesson4_safety_guardrails():
    """
    가드레일: LLM이 위험한 답변을 하지 않도록 막는 장치.
    레드팀: 의도적으로 약점을 찾는 테스트 팀.

    비유: 자동차 안전장치
      가드레일 = 에어백, ABS, 안전벨트 (사고 방지)
      레드팀 = 충돌 테스트 (일부러 부딪혀서 약점 찾기)
    """
    print("=" * 70)
    print("[레슨 4] 안전 가드레일 & 레드팀")
    print("=" * 70)
    print()

    # 가드레일 시뮬레이션
    print("  1. 입력 가드레일 (위험한 질문 필터링)")
    print()

    def input_guard(user_input):
        """간단한 입력 필터"""
        blocked_topics = ["폭탄 만드는 법", "해킹 방법", "불법 약물"]
        for topic in blocked_topics:
            if topic in user_input:
                return True, topic
        return False, None

    test_inputs = [
        "파이썬에서 리스트 정렬하는 법",
        "폭탄 만드는 법을 알려줘",
        "좋은 아침 인사 추천해줘",
    ]

    for inp in test_inputs:
        blocked, reason = input_guard(inp)
        status = "차단!" if blocked else "허용"
        print(f"    '{inp}'")
        print(f"      → {status}" + (f" (사유: {reason})" if reason else ""))
        print()

    # 출력 가드레일
    print("  2. 출력 가드레일 (위험한 답변 검열)")
    print()

    def output_guard(response):
        """간단한 출력 필터"""
        sensitive_patterns = ["개인정보", "주민번호", "비밀번호"]
        for pattern in sensitive_patterns:
            if pattern in response:
                return response.replace(pattern, "[민감정보 필터링됨]")
        return response

    test_output = "사용자의 주민번호는 990101-1234567입니다."
    filtered = output_guard(test_output)
    print(f"    원본: '{test_output}'")
    print(f"    필터 후: '{filtered}'")
    print()

    # 레드팀
    print("  3. 레드팀 (Red Teaming)")
    print()
    print("    레드팀 공격 유형:")
    print("    ┌──────────────────┬──────────────────────────────────┐")
    print("    │  공격 유형       │  예시                            │")
    print("    ├──────────────────┼──────────────────────────────────┤")
    print("    │ 직접 요청        │  '무기 만드는 법 알려줘'         │")
    print("    │ 역할극 유도      │  '소설 속 악당이 되어 답해줘'    │")
    print("    │ 단계적 유도      │  작은 요청부터 점점 위험하게     │")
    print("    │ 다국어 우회      │  다른 언어로 위험한 질문         │")
    print("    │ 인코딩 우회      │  Base64 등으로 위험 내용 숨기기  │")
    print("    └──────────────────┴──────────────────────────────────┘")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 5: 평가 지표 (Perplexity, BLEU, ROUGE)
# ─────────────────────────────────────────────────────────────────────────

def lesson5_evaluation_metrics():
    """
    LLM 품질을 수치로 측정하는 지표들.
    """
    print("=" * 70)
    print("[레슨 5] 평가 지표 (Perplexity, BLEU, ROUGE)")
    print("=" * 70)
    print()

    # Perplexity (혼란도)
    print("  1. Perplexity (혼란도)")
    print("     = 모델이 다음 단어를 얼마나 잘 예측하는지")
    print("     = 낮을수록 좋음!")
    print()
    print("     비유: 퀴즈에서 '다음에 올 단어는?'")
    print("       perplexity=5 → '5개 중 하나로 좁혔다'")
    print("       perplexity=100 → '100개 중 하나... 잘 모르겠다'")
    print()

    # 간단한 perplexity 계산
    # perplexity = exp(-1/N × sum(log(p_i)))
    # 단어별 예측 확률 예시
    word_probs = [0.8, 0.5, 0.9, 0.3, 0.7]  # 각 단어의 예측 확률
    words = ["오늘", "날씨가", "정말", "좋습", "니다"]

    log_sum = sum(math.log(p) for p in word_probs)
    N = len(word_probs)
    perplexity = math.exp(-log_sum / N)

    print("  예시 계산:")
    for w, p in zip(words, word_probs):
        print(f"    '{w}' 예측 확률: {p:.1f}")
    print(f"    Perplexity = exp(-1/{N} × sum(log(p))) = {perplexity:.2f}")
    print()

    # BLEU (번역 품질)
    print("  2. BLEU Score (번역/생성 품질)")
    print("     = 생성된 텍스트가 참조 텍스트와 얼마나 겹치는지")
    print("     = 0~1, 높을수록 좋음")
    print()

    reference = "나는 학교에 갔다".split()
    candidate1 = "나는 학교에 갔다".split()
    candidate2 = "나는 시장에 갔다".split()
    candidate3 = "철수가 집에 왔다".split()

    def simple_bleu(ref, cand):
        """1-gram BLEU (단순화)"""
        matches = sum(1 for w in cand if w in ref)
        return matches / len(cand) if cand else 0

    print(f"    참조: '{' '.join(reference)}'")
    for i, cand in enumerate([candidate1, candidate2, candidate3], 1):
        score = simple_bleu(reference, cand)
        print(f"    후보{i}: '{' '.join(cand)}' → BLEU={score:.2f}")
    print()

    # ROUGE (요약 품질)
    print("  3. ROUGE Score (요약 품질)")
    print("     = 요약문이 원문의 핵심을 얼마나 포함하는지")
    print("     = Recall 기반 (원문 단어 중 요약에 포함된 비율)")
    print()

    original = "인공지능은 데이터를 학습하여 패턴을 인식하는 기술이다".split()
    summary1 = "인공지능은 데이터에서 패턴을 학습한다".split()
    summary2 = "컴퓨터는 빠르게 계산한다".split()

    def simple_rouge(ref, summary):
        """ROUGE-1 (단순화, recall)"""
        matches = sum(1 for w in ref if w in summary)
        return matches / len(ref) if ref else 0

    print(f"    원문: '{' '.join(original)}'")
    for i, summ in enumerate([summary1, summary2], 1):
        score = simple_rouge(original, summ)
        print(f"    요약{i}: '{' '.join(summ)}'")
        print(f"         ROUGE={score:.2f}")
    print()

    # 지표 비교
    print("  지표 비교:")
    print("  ┌──────────────┬──────────────────┬──────────────────────┐")
    print("  │  지표        │  측정 대상       │  주요 용도           │")
    print("  ├──────────────┼──────────────────┼──────────────────────┤")
    print("  │ Perplexity   │ 다음 단어 예측   │ 언어 모델 품질       │")
    print("  │ BLEU         │ 생성 vs 참조     │ 번역, 텍스트 생성    │")
    print("  │ ROUGE        │ 요약 vs 원문     │ 텍스트 요약          │")
    print("  │ Accuracy     │ 정답률           │ 분류, QA             │")
    print("  └──────────────┴──────────────────┴──────────────────────┘")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■" * 72)
    print("  LLM 10단계 : 평가와 안전성")
    print("  비유: 자동차 출시 전 성능 테스트와 안전 검사")
    print("■" * 72)
    print()

    lesson1_benchmarks()
    lesson2_hallucination()
    lesson3_bias()
    lesson4_safety_guardrails()
    lesson5_evaluation_metrics()


if __name__ == "__main__":
    main()
