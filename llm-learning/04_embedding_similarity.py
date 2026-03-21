# =============================================================================
#   LLM 학습 04단계: 임베딩 유사도
#   - 문장을 숫자 벡터로 바꿔
#   - 얼마나 비슷한지 계산하는 장난감 예제를 만든다.
#   - 실제 임베딩은 훨씬 복잡하지만, "숫자로 바꿔 비교한다"는 핵심 감각을 익힌다.
# =============================================================================

from collections import Counter
import math


CONCEPTS = {
    "fruit": ["사과", "바나나", "과일", "딸기"],
    "drink": ["우유", "주스", "음료"],
    "bread": ["빵", "샌드위치", "토스트"],
    "dessert": ["케이크", "디저트", "간식"],
}


def to_concept_vector(text: str) -> list[int]:
    """
    아주 단순한 '장난감 임베딩' 함수.

    실제 임베딩 모델은 문장을 수백~수천 차원의 실수 벡터로 바꾸지만,
    여기서는 concept별 단어 개수만 세서 숫자 벡터를 만든다.

    왜 이렇게 단순화하는가?
    인터넷 없이도 실행 가능해야 하고,
    핵심은 "문장을 숫자로 바꿔 거리나 각도를 비교한다"는 감각을 익히는 데 있기 때문이다.
    """
    words = Counter(text.split())
    vector: list[int] = []

    for concept_words in CONCEPTS.values():
        count = 0
        for word in concept_words:
            count += words[word]
        vector.append(count)

    return vector


def cosine_similarity(left: list[int], right: list[int]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return dot / (left_norm * right_norm)


def find_most_similar(query: str, candidates: list[str]) -> tuple[str, float]:
    query_vector = to_concept_vector(query)

    best_text = candidates[0]
    best_score = -1.0

    for candidate in candidates:
        score = cosine_similarity(query_vector, to_concept_vector(candidate))
        if score > best_score:
            best_text = candidate
            best_score = score

    return best_text, best_score


def lesson1_convert_sentence_to_vector() -> None:
    print("[레슨 1] 임베딩의 핵심 감각은 문장을 숫자로 바꾸는 것이다")
    print()

    sentence = "사과 우유 간식"
    vector = to_concept_vector(sentence)

    print("  문장:", sentence)
    print("  개념 순서:", list(CONCEPTS.keys()))
    print("  벡터:", vector)
    print()
    print("  설명: fruit, drink, dessert 같은 개념 통에 단어를 넣어 숫자로 바꿔 본 셈이다.")
    print()


def lesson2_compare_similarity() -> None:
    print("[레슨 2] 비슷한 문장끼리는 벡터 방향도 비슷해질 수 있다")
    print()

    sentence_a = "사과 우유 간식"
    sentence_b = "과일 주스 디저트"
    sentence_c = "빵 토스트 샌드위치"

    vector_a = to_concept_vector(sentence_a)
    vector_b = to_concept_vector(sentence_b)
    vector_c = to_concept_vector(sentence_c)

    print("  A-B 유사도:", round(cosine_similarity(vector_a, vector_b), 3))
    print("  A-C 유사도:", round(cosine_similarity(vector_a, vector_c), 3))
    print()
    print("  설명: A와 B는 과일/음료/간식 계열 개념을 더 많이 공유해 더 가깝게 나온다.")
    print()


def lesson3_use_similarity_for_search() -> None:
    print("[레슨 3] 유사도는 비슷한 문장을 찾는 검색에도 쓸 수 있다")
    print()

    candidates = [
        "사과 우유 도시락",
        "토스트 빵 아침식사",
        "딸기 주스 간식",
    ]
    query = "과일 음료 간식"

    best_text, best_score = find_most_similar(query, candidates)

    print("  검색 질문:", query)
    print("  후보들:", candidates)
    print("  가장 가까운 문장:", best_text)
    print("  유사도:", round(best_score, 3))
    print()
    print("  실사용 예시: FAQ 추천, 비슷한 상품 찾기, 문서 검색 초벌 후보 뽑기")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("  LLM 04단계 : 임베딩 유사도")
    print("=" * 72)
    print()

    lesson1_convert_sentence_to_vector()
    lesson2_compare_similarity()
    lesson3_use_similarity_for_search()
