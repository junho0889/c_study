# =============================================================================
#   LLM 학습 03단계: 토큰 기초
#   - 글자가 길이와 토큰 수가 항상 같지 않다는 점
#   - 문맥 창(context window) 안에 들어갈 수 있는 양이 제한된다는 점
#   - 입력/출력 예산을 같이 생각해야 한다는 점을 코드로 확인한다.
# =============================================================================

import re


def simple_tokenize(text: str) -> list[str]:
    """
    공백만 자르는 것보다 조금 더 그럴듯한 토크나이저를 만든다.
    한글/영문/숫자 덩어리와 문장 부호를 따로 떼어 본다.

    진짜 토크나이저는 훨씬 복잡하지만,
    여기서는 "문장 부호도 토큰이 될 수 있다"는 감각만 잡으면 충분하다.
    """
    return re.findall(r"[0-9A-Za-z가-힣]+|[^\s]", text)


def trim_to_budget(tokens: list[str], max_input_tokens: int) -> list[str]:
    return tokens[:max_input_tokens]


def estimate_total_budget(input_tokens: int, reserved_output_tokens: int) -> int:
    return input_tokens + reserved_output_tokens


def lesson1_tokens_are_pieces_not_characters() -> None:
    print("[레슨 1] 토큰은 글자 수와 꼭 같지 않다")
    print()

    text = "오늘 급식은 사과, 우유, 샌드위치입니다!"
    tokens = simple_tokenize(text)

    print("  문장:", text)
    print("  글자 수:", len(text))
    print("  토큰 목록:", tokens)
    print("  토큰 수:", len(tokens))
    print()
    print("  설명: 쉼표와 느낌표도 따로 세면 토큰 수가 글자 수 감각과 달라질 수 있다.")
    print()


def lesson2_context_window_is_like_desk_space() -> None:
    print("[레슨 2] 문맥 창은 책상 위에 펼칠 수 있는 종이 수와 비슷하다")
    print()

    text = "A B C D E F G H"
    tokens = simple_tokenize(text)
    max_input_tokens = 5
    trimmed = trim_to_budget(tokens, max_input_tokens)

    print("  전체 토큰:", tokens)
    print("  최대 입력 토큰:", max_input_tokens)
    print("  실제로 들어간 토큰:", trimmed)
    print()
    print("  비유: 책상이 작으면 종이를 다 펼치지 못하고 앞부분만 올려두는 것과 비슷하다.")
    print()


def lesson3_input_and_output_share_budget() -> None:
    print("[레슨 3] 입력 토큰과 출력 토큰은 같은 예산 상자를 나눠 쓴다")
    print()

    question = "광합성을 3단계로 설명하고 예시 2개를 들어 줘."
    input_tokens = len(simple_tokenize(question))
    reserved_output_tokens = 20
    total_budget = estimate_total_budget(input_tokens, reserved_output_tokens)

    print("  질문:", question)
    print("  입력 토큰 수:", input_tokens)
    print("  출력에 미리 남겨 둘 토큰:", reserved_output_tokens)
    print("  총 필요 예산:", total_budget)
    print()
    print("  자주 하는 실수: 입력을 너무 길게 넣고도 긴 답변이 그대로 나올 거라 기대하는 것")
    print("  실제로는 출력 자리도 남겨 둬야 모델이 답을 끝까지 쓸 수 있다.")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("  LLM 03단계 : 토큰 기초")
    print("=" * 72)
    print()

    lesson1_tokens_are_pieces_not_characters()
    lesson2_context_window_is_like_desk_space()
    lesson3_input_and_output_share_budget()
