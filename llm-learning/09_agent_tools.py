# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#   LLM 학습 09단계: 에이전트와 도구 사용
#   ─ LLM이 생각하고, 도구를 쓰고, 행동하는 법 ─
#
#   비유: 똑똑한 비서
#     비서(LLM)가 혼자 모든 걸 알 수는 없습니다.
#     하지만 계산기, 인터넷, 캘린더 같은 도구를 쓸 수 있다면?
#     "내일 서울 날씨 확인해서 우산 필요한지 알려줘"
#     → 날씨 API 호출 → 결과 해석 → 답변
#
#   실행 방법:
#     python 09_agent_tools.py
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import math
import json


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 1: LLM as 추론 엔진
# ─────────────────────────────────────────────────────────────────────────

def lesson1_llm_as_reasoning_engine():
    """
    LLM은 단순 텍스트 생성기가 아니라 '추론 엔진'으로 쓸 수 있습니다.

    비유: 사람의 두뇌
      두뇌 자체는 인터넷 검색을 못 하지만,
      "검색해야겠다"는 판단은 할 수 있습니다.
      LLM도 마찬가지: 직접 계산은 못 하지만
      "계산기를 써야겠다"는 판단을 할 수 있습니다.
    """
    print("=" * 70)
    print("[레슨 1] LLM = 추론 엔진")
    print("=" * 70)
    print()
    print("  LLM의 역할 변화:")
    print()
    print("    과거: 텍스트 입력 → 텍스트 출력")
    print("    현재: 질문 → [생각] → [도구 선택] → [도구 실행] → 답변")
    print()
    print("  예시: '2847 × 391은?'")
    print("    일반 LLM: '약 1,113,177' (대충 계산, 틀릴 수 있음)")
    print("    에이전트:  '계산기를 쓰겠습니다' → calculate(2847, 391)")
    print("               → 1,113,177 (정확!)")
    print()
    print("  핵심: LLM이 '무슨 도구를 쓸지' 판단하고,")
    print("        도구가 '실제 작업'을 수행합니다.")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 2: 도구 사용 (Function Calling)
# ─────────────────────────────────────────────────────────────────────────

def lesson2_tool_use():
    """
    LLM이 사용할 수 있는 도구(함수)를 정의하고 호출하는 과정.

    비유: 스마트폰 앱 사용
      LLM = 사용자
      도구 = 설치된 앱 (계산기, 날씨, 지도 등)
      LLM이 상황에 맞는 앱을 골라서 사용!
    """
    print("=" * 70)
    print("[레슨 2] 도구 사용 (Function Calling)")
    print("=" * 70)
    print()

    # 도구 정의
    tools = {
        "calculate": {
            "description": "수학 계산을 수행합니다",
            "parameters": {"expression": "str"},
            "example": 'calculate(expression="2+3")',
        },
        "get_weather": {
            "description": "특정 도시의 날씨를 조회합니다",
            "parameters": {"city": "str"},
            "example": 'get_weather(city="서울")',
        },
        "search": {
            "description": "정보를 검색합니다",
            "parameters": {"query": "str"},
            "example": 'search(query="파이썬 리스트")',
        },
    }

    print("  등록된 도구들:")
    for name, info in tools.items():
        print(f"    {name}:")
        print(f"      설명: {info['description']}")
        print(f"      매개변수: {info['parameters']}")
        print(f"      예시: {info['example']}")
        print()

    # 도구 호출 시뮬레이션
    def calculate(expression):
        try:
            # 안전한 계산만 허용 (실제로는 더 엄격해야 함)
            allowed = set("0123456789+-*/.() ")
            if all(c in allowed for c in expression):
                return {"result": eval(expression)}
            return {"error": "허용되지 않는 문자"}
        except Exception as e:
            return {"error": str(e)}

    def get_weather(city):
        # 장난감 날씨 데이터
        weather_db = {
            "서울": {"temp": 22, "condition": "맑음", "rain_prob": 10},
            "부산": {"temp": 25, "condition": "구름 많음", "rain_prob": 40},
        }
        return weather_db.get(city, {"error": f"{city} 데이터 없음"})

    # LLM이 도구를 선택하는 시뮬레이션
    user_questions = [
        ("375 * 28은 얼마야?", "calculate", {"expression": "375 * 28"}),
        ("서울 날씨 어때?", "get_weather", {"city": "서울"}),
    ]

    print("  도구 호출 시뮬레이션:")
    print()
    for question, tool_name, params in user_questions:
        print(f"    사용자: '{question}'")
        print(f"    LLM 판단: {tool_name}({params})")

        if tool_name == "calculate":
            result = calculate(params["expression"])
        elif tool_name == "get_weather":
            result = get_weather(params["city"])
        else:
            result = {"error": "unknown tool"}

        print(f"    도구 결과: {result}")
        print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 3: ReAct 패턴 (Reason + Act)
# ─────────────────────────────────────────────────────────────────────────

def lesson3_react_pattern():
    """
    ReAct: 생각(Reasoning)과 행동(Acting)을 번갈아 수행.

    비유: 탐정의 수사 과정
      생각: "피해자의 일정을 확인해야겠다"
      행동: 일정표 확인
      관찰: "오후 3시에 은행 방문 예정이었네"
      생각: "은행 CCTV를 확인해야겠다"
      행동: CCTV 확인
      ...반복...
      결론: 사건 해결!
    """
    print("=" * 70)
    print("[레슨 3] ReAct 패턴 (Reason + Act)")
    print("=" * 70)
    print()
    print("  ReAct = 생각(Thought) → 행동(Action) → 관찰(Observation) 반복")
    print()

    # ReAct 루프 시뮬레이션
    # 질문: "서울과 부산 중 어디가 더 따뜻해?"

    react_trace = [
        {
            "thought": "서울과 부산의 온도를 비교해야 한다. 먼저 서울 날씨를 확인하자.",
            "action": "get_weather(city='서울')",
            "observation": "{'temp': 22, 'condition': '맑음'}",
        },
        {
            "thought": "서울은 22도. 이제 부산 날씨를 확인하자.",
            "action": "get_weather(city='부산')",
            "observation": "{'temp': 25, 'condition': '구름 많음'}",
        },
        {
            "thought": "서울 22도 < 부산 25도. 부산이 더 따뜻하다. 답을 정리하자.",
            "action": "final_answer('부산이 25도로 서울(22도)보다 3도 더 따뜻합니다.')",
            "observation": None,
        },
    ]

    print("  질문: '서울과 부산 중 어디가 더 따뜻해?'")
    print()

    for i, step in enumerate(react_trace):
        print(f"  --- 단계 {i+1} ---")
        print(f"  Thought: {step['thought']}")
        print(f"  Action:  {step['action']}")
        if step['observation']:
            print(f"  Observation: {step['observation']}")
        else:
            print(f"  → 최종 답변 생성!")
        print()

    print("  핵심: LLM이 한 번에 답하지 않고,")
    print("        '생각→행동→관찰'을 반복하며 정확한 답에 도달!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 4: 에이전트 루프 구현
# ─────────────────────────────────────────────────────────────────────────

def lesson4_agent_loop():
    """
    에이전트 루프: 목표가 달성될 때까지 반복하는 주 루프.
    """
    print("=" * 70)
    print("[레슨 4] 에이전트 루프 구현")
    print("=" * 70)
    print()

    # 도구 정의
    def calc(expr):
        allowed = set("0123456789+-*/.() ")
        if all(c in allowed for c in expr):
            return str(eval(expr))
        return "오류"

    def lookup(item):
        prices = {"사과": 1000, "바나나": 1500, "우유": 2500}
        return str(prices.get(item, "가격 정보 없음"))

    tools_registry = {"calc": calc, "lookup": lookup}

    # 간단한 에이전트 (규칙 기반으로 LLM 판단을 시뮬레이션)
    def simple_agent(goal):
        """규칙 기반 에이전트 (실제로는 LLM이 판단)"""
        print(f"  목표: {goal}")
        print()

        memory = []  # 단기 기억
        max_steps = 5

        # 미리 정의된 계획 (실제 에이전트는 LLM이 동적 생성)
        if "총 가격" in goal:
            items = []
            for item in ["사과", "바나나", "우유"]:
                if item in goal:
                    items.append(item)

            step = 0
            prices = {}
            for item in items:
                step += 1
                action = f"lookup('{item}')"
                result = lookup(item)
                memory.append(f"{item}={result}원")
                prices[item] = int(result) if result.isdigit() else 0
                print(f"    스텝 {step}: lookup('{item}') → {result}원")

            if prices:
                step += 1
                expr = "+".join(str(v) for v in prices.values())
                total = calc(expr)
                print(f"    스텝 {step}: calc('{expr}') → {total}원")
                print()
                print(f"  최종 답변: 총 가격은 {total}원입니다.")
            else:
                print("  물건을 찾을 수 없습니다.")
        else:
            print("  이 목표를 처리할 수 없습니다.")

        print()
        print(f"  단기 기억: {memory}")
        print()

    simple_agent("사과, 바나나, 우유의 총 가격을 알려줘")

    # 에이전트 루프 구조 설명
    print("  에이전트 루프 구조:")
    print("  ┌──────────────────────────────────────┐")
    print("  │  while 목표 달성 안 됨:              │")
    print("  │    1. LLM에게 상황 설명              │")
    print("  │    2. LLM이 다음 행동 결정           │")
    print("  │    3. 도구 실행                      │")
    print("  │    4. 결과를 기억에 저장              │")
    print("  │    5. 완료 여부 확인                  │")
    print("  └──────────────────────────────────────┘")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 5: 메모리와 계획
# ─────────────────────────────────────────────────────────────────────────

def lesson5_memory_and_planning():
    """
    에이전트의 기억과 계획 능력.

    비유: 여행 계획 세우기
      단기 기억 = 지금 진행 중인 대화 내용
      장기 기억 = 과거 여행 경험, 선호도 (DB에 저장)
      계획 = "먼저 항공권 → 숙소 → 관광지 → 음식점" 순서
    """
    print("=" * 70)
    print("[레슨 5] 메모리와 계획 (Memory & Planning)")
    print("=" * 70)
    print()

    # 단기 기억 (대화 컨텍스트)
    print("  1. 단기 기억 (Short-term Memory)")
    print("     = 현재 대화의 맥락")
    print()

    short_term = [
        {"role": "user", "content": "내 이름은 철수야"},
        {"role": "assistant", "content": "안녕하세요 철수님!"},
        {"role": "user", "content": "내 이름이 뭐라고 했지?"},
        {"role": "assistant", "content": "철수님이라고 하셨습니다."},
    ]

    for msg in short_term:
        icon = "U" if msg["role"] == "user" else "A"
        print(f"    [{icon}] {msg['content']}")
    print()
    print("    → 이전 대화를 기억해서 '철수'라고 대답 가능")
    print()

    # 장기 기억 (벡터 DB 개념)
    print("  2. 장기 기억 (Long-term Memory)")
    print("     = 벡터 DB나 파일에 저장된 과거 정보")
    print()

    long_term_db = [
        {"key": "user_name", "value": "철수", "timestamp": "2024-01-15"},
        {"key": "preference", "value": "매운 음식 선호", "timestamp": "2024-02-20"},
        {"key": "past_order", "value": "떡볶이 3번 주문", "timestamp": "2024-03-10"},
    ]

    print("    저장된 정보:")
    for item in long_term_db:
        print(f"      [{item['timestamp']}] {item['key']}: {item['value']}")
    print()
    print("    → 대화가 끝나도 정보가 유지됨!")
    print()

    # 계획 (Planning)
    print("  3. 계획 (Planning)")
    print("     = 복잡한 작업을 하위 작업으로 분해")
    print()

    goal = "주말에 부산 여행 계획을 세워줘"
    plan = [
        "1. 현재 날짜 확인 (주말이 언제인지)",
        "2. 부산 날씨 확인",
        "3. 교통편 검색 (KTX/비행기)",
        "4. 숙소 추천 (예산에 맞게)",
        "5. 관광지 추천 (날씨에 맞게)",
        "6. 전체 일정 정리해서 제시",
    ]

    print(f"    목표: '{goal}'")
    print("    생성된 계획:")
    for step in plan:
        print(f"      {step}")
    print()
    print("  → 큰 목표를 작은 단계로 쪼개서 순서대로 실행!")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■" * 72)
    print("  LLM 09단계 : 에이전트와 도구 사용")
    print("  비유: 도구를 쓸 줄 아는 똑똑한 비서")
    print("■" * 72)
    print()

    lesson1_llm_as_reasoning_engine()
    lesson2_tool_use()
    lesson3_react_pattern()
    lesson4_agent_loop()
    lesson5_memory_and_planning()


if __name__ == "__main__":
    main()
