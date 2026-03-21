# =============================================================================
#   LLM 학습 01단계: 프롬프트 파이프라인
#   - 질문을 한 줄로 툭 던지는 대신
#   - 역할, 목표, 출력 형식, 예시를 차례대로 붙여
#   - 더 읽기 쉬운 프롬프트를 만드는 과정을 코드로 직접 따라간다.
# =============================================================================

from dataclasses import dataclass


@dataclass
class PromptRequest:
    topic: str
    audience: str
    output_steps: int
    include_analogy: bool
    include_examples: bool


def build_prompt(request: PromptRequest) -> str:
    """
    프롬프트를 여러 조각으로 나눠 만드는 함수다.

    왜 굳이 나누는가?
    한 문장에 다 몰아 쓰면 나중에 고치기 어렵다.
    도시락을 쌀 때도 밥, 반찬, 수저를 따로 확인해야 빠뜨린 것이 보이듯,
    프롬프트도 역할/목표/형식/금지사항을 따로 쓰면 점검하기 쉽다.
    """
    parts: list[str] = []

    # system 역할에 해당하는 문장.
    # "너는 어떤 말투와 수준으로 대답해야 하는지"를 정해 준다.
    parts.append(
        "역할: 너는 초등학생도 이해할 수 있게 설명하는 과학 선생님이다."
    )

    # user 요청의 핵심 목표.
    parts.append(
        f"주제: {request.topic}를 {request.audience} 눈높이에 맞춰 설명하라."
    )

    # 출력 모양을 구체적으로 적어 두면 결과가 덜 흔들린다.
    parts.append(f"형식: {request.output_steps}단계로 나눠 설명하라.")

    if request.include_analogy:
        parts.append("반드시 쉬운 비유를 1개 포함하라.")

    if request.include_examples:
        parts.append("반드시 실생활 예시를 2개 포함하라.")

    # 자주 하는 실수:
    # "쉽게 설명해"만 적고 어떤 수준인지 안 적는 것.
    # 초등학생용인지, 개발자용인지에 따라 같은 주제도 문장이 크게 달라진다.
    parts.append("금지: 어려운 전문용어만 던지고 끝내지 마라.")

    return "\n".join(parts)


def fake_llm_response(prompt: str) -> str:
    """
    진짜 LLM 대신 아주 단순한 규칙 기반 응답기를 만든다.

    이유:
    이 학습 파일의 목적은 "프롬프트 구조가 출력에 어떤 영향을 주는지"를 보는 것이다.
    인터넷 연결이나 API 키 없이도 언제든 실행할 수 있어야 하므로
    장난감 모델을 직접 만든다.
    """
    is_for_child = "초등학생" in prompt
    wants_analogy = "비유" in prompt
    wants_examples = "실생활 예시" in prompt
    wants_steps = "3단계" in prompt or "4단계" in prompt
    topic = ""

    for line in prompt.splitlines():
        if line.startswith("주제:"):
            topic = line
            break

    lines: list[str] = []

    if "광합성" in topic and is_for_child:
        lines.append("1. 식물은 햇빛을 받아 스스로 먹을 것을 만든다.")
    elif "광합성" in topic:
        lines.append("1. 식물은 빛 에너지를 이용해 유기물을 합성한다.")
    elif "토마토" in topic and is_for_child:
        lines.append("1. 토마토는 자라면서 초록색 옷을 벗고 빨간색 색소가 많아진다.")
    elif "토마토" in topic:
        lines.append("1. 토마토는 익어 가면서 엽록소가 줄고 붉은 색소가 더 두드러진다.")
    else:
        lines.append("1. 질문 주제를 먼저 파악하고 핵심 개념부터 짧게 설명한다.")

    if "광합성" in topic:
        lines.append("2. 이때 물과 공기 속 이산화탄소를 함께 사용한다.")
    elif "토마토" in topic:
        lines.append("2. 햇빛과 온도, 익는 과정이 색 변화에 영향을 준다.")
    else:
        lines.append("2. 필요한 배경 정보와 이유를 이어서 설명한다.")

    if wants_steps:
        if "광합성" in topic:
            lines.append("3. 그래서 식물은 자라고, 우리에게 산소도 돌려준다.")
        elif "토마토" in topic:
            lines.append("3. 그래서 익은 토마토는 더 빨갛게 보이고 맛도 달라질 수 있다.")
        else:
            lines.append("3. 마지막에는 결과나 쓰임새를 알려 준다.")

    if wants_analogy:
        if "광합성" in topic:
            lines.append("비유: 식물이 햇빛 주방에서 요리하는 것과 비슷하다.")
        elif "토마토" in topic:
            lines.append("비유: 초록 크레파스를 지우고 빨간 크레파스를 더 칠하는 것과 비슷하다.")
        else:
            lines.append("비유: 큰 개념을 작은 생활 장면에 빗대어 설명한다.")

    if wants_examples:
        if "광합성" in topic:
            lines.append("예시 1: 창가 화분이 햇빛을 잘 받으면 더 잘 자란다.")
            lines.append("예시 2: 잎이 넓은 식물은 빛을 더 많이 받으려는 모습으로 볼 수 있다.")
        elif "토마토" in topic:
            lines.append("예시 1: 덜 익은 토마토는 초록빛이 돌고, 익으면 점점 빨개진다.")
            lines.append("예시 2: 마트 진열대의 익은 토마토가 더 빨갛게 보이는 이유를 떠올릴 수 있다.")
        else:
            lines.append("예시 1: 일상에서 바로 볼 수 있는 장면을 든다.")
            lines.append("예시 2: 비슷한 다른 상황도 하나 더 보여 준다.")

    return "\n".join(lines)


def lesson1_split_prompt_into_sections() -> None:
    print("[레슨 1] 프롬프트를 역할, 목표, 형식으로 나눠 조립하기")
    print()

    request = PromptRequest(
        topic="광합성",
        audience="초등학생",
        output_steps=3,
        include_analogy=True,
        include_examples=True,
    )

    prompt = build_prompt(request)

    print("  조립된 프롬프트:")
    print(prompt)
    print()


def lesson2_compare_vague_and_structured_prompt() -> None:
    print("[레슨 2] 두루뭉술한 질문과 구조화된 질문 비교하기")
    print()

    vague_prompt = "광합성 설명해 줘."
    structured_prompt = build_prompt(
        PromptRequest(
            topic="광합성",
            audience="초등학생",
            output_steps=3,
            include_analogy=True,
            include_examples=True,
        )
    )

    print("  두루뭉술한 프롬프트:")
    print(vague_prompt)
    print("  장난감 LLM 응답:")
    print(fake_llm_response(vague_prompt))
    print()

    print("  구조화된 프롬프트:")
    print(structured_prompt)
    print("  장난감 LLM 응답:")
    print(fake_llm_response(structured_prompt))
    print()

    # 여기서 보고 싶은 핵심:
    # 프롬프트에 "초등학생", "비유", "예시"를 넣으면
    # 출력도 그 요구에 맞춰 더 구체적으로 변한다는 점이다.
    print("  설명: 프롬프트에 요구사항을 적을수록 출력도 덜 흐릿해진다.")
    print()


def lesson3_build_prompt_from_user_input() -> None:
    print("[레슨 3] 입력값만 바꿔 같은 프롬프트 틀을 재사용하기")
    print()

    requests = [
        PromptRequest("토마토가 빨개지는 이유", "초등학생", 3, True, False),
        PromptRequest("토마토가 빨개지는 이유", "중학생", 4, False, True),
    ]

    for index, request in enumerate(requests, start=1):
        prompt = build_prompt(request)
        print(f"  경우 {index} 프롬프트:")
        print(prompt)
        print("  응답:")
        print(fake_llm_response(prompt))
        print()

    print("  실무 감각: 같은 코드 틀을 두고 audience, format, examples만 바꿔 여러 요청을 만든다.")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("  LLM 01단계 : 프롬프트 파이프라인")
    print("=" * 72)
    print()

    lesson1_split_prompt_into_sections()
    lesson2_compare_vague_and_structured_prompt()
    lesson3_build_prompt_from_user_input()
