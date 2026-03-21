# =============================================================================
#   LLM 학습 02단계: RAG 흐름
#   - 모델이 기억에만 기대지 않고
#   - 관련 문서를 먼저 찾은 뒤
#   - 그 문서를 바탕으로 답을 만드는 흐름을 장난감 코드로 구현한다.
# =============================================================================

from dataclasses import dataclass
import re


@dataclass
class Document:
    doc_id: str
    title: str
    text: str


DOCUMENTS = [
    Document(
        "doc-1",
        "상추 보관법",
        "상추는 씻은 뒤 물기를 잘 제거하고 키친타월과 함께 밀폐 용기에 넣으면 더 오래 간다.",
    ),
    Document(
        "doc-2",
        "토마토 보관법",
        "토마토는 너무 차갑게 두면 식감이 달라질 수 있어 실온 보관이 더 나은 경우가 있다.",
    ),
    Document(
        "doc-3",
        "딸기 보관법",
        "딸기는 물에 오래 담그지 말고 먹기 직전에 씻는 편이 무르지 않게 돕는다.",
    ),
]


def tokenize(text: str) -> list[str]:
    """
    아주 단순한 토크나이저.
    한글/영문/숫자 덩어리만 뽑아 소문자로 만든다.

    실제 검색기는 훨씬 복잡하지만,
    여기서는 "질문과 문서가 공통 단어를 얼마나 공유하는지"만 보기 위해 단순화한다.
    """
    raw_tokens = re.findall(r"[0-9A-Za-z가-힣]+", text.lower())
    return [normalize_token(token) for token in raw_tokens if normalize_token(token)]


def normalize_token(token: str) -> str:
    """
    아주 거친 정규화 함수.

    한국어 형태소 분석기를 쓰지 않고도
    조사와 자주 붙는 표현을 조금 떼어 내서 검색 성능을 약간 올린다.
    장난감 예제지만, "검색 전처리"가 왜 필요한지 보여 주는 데는 충분하다.
    """
    if "보관" in token:
        return "보관"

    for suffix in [
        "하려면",
        "하려고",
        "입니다",
        "이다",
        "으로",
        "에서",
        "에게",
        "처럼",
        "까지",
        "부터",
        "보다",
        "하고",
        "이라서",
        "라서",
        "를",
        "을",
        "이",
        "가",
        "은",
        "는",
        "에",
        "도",
        "와",
        "과",
        "로",
    ]:
        if token.endswith(suffix) and len(token) > len(suffix):
            token = token[: -len(suffix)]
            break

    return token


def overlap_score(query: str, document: Document) -> int:
    query_words = set(tokenize(query))
    doc_words = set(tokenize(document.text + " " + document.title))
    return len(query_words & doc_words)


def retrieve_top_k(query: str, documents: list[Document], k: int = 2) -> list[Document]:
    scored = sorted(
        documents,
        key=lambda document: overlap_score(query, document),
        reverse=True,
    )
    return scored[:k]


def build_context(documents: list[Document]) -> str:
    lines: list[str] = []
    for document in documents:
        lines.append(f"[{document.doc_id}] {document.title}: {document.text}")
    return "\n".join(lines)


def answer_without_rag(query: str) -> str:
    """
    검색 없이 막연히 답하는 장난감 함수.
    일부러 흐릿한 답을 만들어 RAG가 왜 필요한지 보여 준다.
    """
    return f"질문 '{query}' 에 대해 대충 생각해 보면, 냉장 보관이 도움이 될 수 있습니다."


def answer_with_rag(query: str, retrieved_docs: list[Document]) -> str:
    context = build_context(retrieved_docs)

    # 장난감 생성기:
    # 실제 LLM처럼 긴 문장을 멋지게 만들지는 않지만,
    # "찾아온 문서 내용만 근거로 답한다"는 핵심 감각을 보여 준다.
    best = retrieved_docs[0]
    return (
        f"질문: {query}\n"
        f"근거 문서: {best.title}\n"
        f"답변: {best.text}\n"
        f"참고한 문맥:\n{context}"
    )


def lesson1_retrieve_before_answer() -> None:
    print("[레슨 1] RAG는 답하기 전에 먼저 관련 문서를 찾는다")
    print()

    query = "상추를 시들지 않게 보관하려면?"
    retrieved_docs = retrieve_top_k(query, DOCUMENTS, k=2)

    print("  질문:", query)
    print("  검색 결과:")
    for document in retrieved_docs:
        print(f"   - {document.doc_id}: {document.title}")
    print()


def lesson2_compare_without_and_with_rag() -> None:
    print("[레슨 2] 검색 없이 답할 때와 검색 후 답할 때 비교하기")
    print()

    query = "딸기를 덜 무르게 보관하려면?"
    retrieved_docs = retrieve_top_k(query, DOCUMENTS, k=2)

    print("  검색 없이 바로 답한 경우:")
    print(answer_without_rag(query))
    print()

    print("  문서를 찾은 뒤 답한 경우:")
    print(answer_with_rag(query, retrieved_docs))
    print()

    print("  설명: RAG의 핵심은 '기억'보다 '근거 문서'를 먼저 붙잡는 것이다.")
    print()


def lesson3_why_chunking_and_ranking_matter() -> None:
    print("[레슨 3] 왜 문서 나누기와 순위 매기기가 중요한가")
    print()

    query = "토마토를 어디에 두는 게 좋을까?"

    for document in DOCUMENTS:
        print(
            f"  {document.title} -> 공통 단어 점수 {overlap_score(query, document)}"
        )

    print()
    print("  점수가 높을수록 질문과 겹치는 단어가 많다고 본다.")
    print("  실무에서는 문서를 너무 길게 두면 딱 맞는 부분을 놓치기 쉬워서")
    print("  짧은 조각(chunk)으로 나누고, 그중 상위 몇 개만 모델에게 준다.")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("  LLM 02단계 : RAG 흐름")
    print("=" * 72)
    print()

    lesson1_retrieve_before_answer()
    lesson2_compare_without_and_with_rag()
    lesson3_why_chunking_and_ranking_matter()
