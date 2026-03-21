# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   gRPC 학습 08단계: gRPC 패턴과 고급 기능
#   ─ gRPC vs REST, 양방향 스트리밍, Deadline, 취소, 압축, gRPC-Web ─
#
#   gRPC의 다양한 실전 패턴과 REST와의 차이를 정리합니다.
#
#   ■ 실행: python patterns.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import time
import json
from dataclasses import dataclass
from typing import Generator, List, Optional
from collections import deque


def lesson1_grpc_vs_rest():
    # =========================================================================
    #   레슨 1 — gRPC vs REST 비교
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 1 : gRPC vs REST 비교                  │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ gRPC와 REST는 각각 다른 상황에서 빛납니다
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     REST = 일반 우편 (편지를 쓰고 → 보내고 → 기다리고 → 답장 받기)
    #     gRPC = 전화 통화 (바로 연결되어 실시간으로 주고받기)
    #
    #     둘 다 좋은 방법이지만, 상황에 맞게 골라야 합니다!
    #

    comparisons = [
        ("프로토콜",     "HTTP/1.1 (주로)",       "HTTP/2"),
        ("데이터 형식",  "JSON (텍스트)",          "Protocol Buffers (바이너리)"),
        ("API 명세",     "OpenAPI/Swagger",        ".proto 파일"),
        ("코드 생성",    "선택사항",               "기본 제공 (protoc)"),
        ("스트리밍",     "제한적 (WebSocket 별도)", "기본 지원 (4가지 패턴)"),
        ("브라우저",     "직접 호출 가능",          "gRPC-Web 필요"),
        ("속도",         "빠름",                   "매우 빠름 (2~10배)"),
        ("디버깅",       "쉬움 (JSON 읽기 쉬움)",  "어려움 (바이너리)"),
        ("학습 난이도",  "쉬움",                   "보통~어려움"),
        ("적합한 곳",    "웹 API, 공개 API",       "마이크로서비스, 내부 통신"),
    ]

    print(f"  {'항목':<14s} {'REST':<26s} {'gRPC':<26s}")
    print(f"  {'─' * 14} {'─' * 26} {'─' * 26}")
    for item, rest, grpc in comparisons:
        print(f"  {item:<14s} {rest:<26s} {grpc:<26s}")
    print()

    print("  언제 REST?")
    print("    - 웹 브라우저에서 직접 호출해야 할 때")
    print("    - 외부 개발자에게 공개할 API")
    print("    - 간단한 CRUD 작업")
    print()
    print("  언제 gRPC?")
    print("    - 서버끼리 통신할 때 (마이크로서비스)")
    print("    - 실시간 양방향 통신이 필요할 때")
    print("    - 속도가 매우 중요할 때")
    print("    - 모바일 앱 ↔ 서버 통신 (데이터 절약)")
    print()


def lesson2_bidirectional_streaming_chat():
    # =========================================================================
    #   레슨 2 — 양방향 스트리밍 채팅
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 2 : 양방향 스트리밍 채팅                │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 양방향 스트리밍 = 클라이언트와 서버가 동시에 메시지를 주고받기
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     전화 통화! 한 사람이 말하는 동안 상대방도 동시에 말할 수 있음.
    #     (편지는 보내고 답장 올 때까지 기다려야 하지만, 전화는 동시에!)
    #
    #   gRPC 스트리밍 4가지:
    #     1. Unary:              요청 1개 → 응답 1개
    #     2. Server Streaming:   요청 1개 → 응답 여러 개
    #     3. Client Streaming:   요청 여러 개 → 응답 1개
    #     4. Bidirectional:      요청 여러 개 ↔ 응답 여러 개 (동시!)
    #

    @dataclass
    class ChatMessage:
        sender: str
        text: str
        timestamp: float

    class ChatRoom:
        """양방향 스트리밍 채팅방 시뮬레이션"""
        def __init__(self):
            self.messages: List[ChatMessage] = []

        def send(self, sender, text):
            msg = ChatMessage(sender=sender, text=text, timestamp=time.time())
            self.messages.append(msg)
            return msg

        def get_messages_after(self, count_from):
            """이전에 받은 메시지 수 이후의 새 메시지만 반환"""
            return self.messages[count_from:]

    room = ChatRoom()

    # 채팅 시뮬레이션
    conversation = [
        ("민수", "안녕하세요!"),
        ("지우", "안녕! 오늘 숙제 했어?"),
        ("민수", "아직... 수학 어렵다 ㅠ"),
        ("서연", "나도 같이 할래!"),
        ("지우", "그럼 도서관에서 만나자!"),
    ]

    print("  [양방향 채팅 시뮬레이션]")
    print()

    received_count = 0
    for sender, text in conversation:
        room.send(sender, text)
        new_messages = room.get_messages_after(received_count)
        for msg in new_messages:
            print(f"    [{msg.sender}] {msg.text}")
        received_count = len(room.messages)

    print()
    print(f"  총 {len(room.messages)}개 메시지가 실시간으로 교환됨!")
    print("  양방향 스트리밍은 채팅, 게임, 실시간 협업에 적합합니다.")
    print()


def lesson3_deadline_timeout():
    # =========================================================================
    #   레슨 3 — Deadline / Timeout
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 3 : Deadline / Timeout                 │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Deadline = "이 시간까지 응답이 없으면 포기해!"
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     피자 배달: "30분 안에 안 오면 무료!"
    #     gRPC도: "3초 안에 응답 없으면 DEADLINE_EXCEEDED 에러!"
    #
    #   Timeout vs Deadline:
    #     Timeout  = "지금부터 3초" (상대적)
    #     Deadline = "10시 30분 15초까지" (절대적)
    #     gRPC는 내부적으로 Deadline을 사용합니다.
    #
    #   중요: Deadline은 전파됩니다!
    #     서비스A → 서비스B → 서비스C
    #     A가 3초 Deadline을 설정하면:
    #     A→B에서 1초 걸리면, B→C는 2초밖에 남지 않음!
    #

    def slow_service(request_data, processing_time):
        """느린 서비스 시뮬레이션"""
        time.sleep(processing_time)
        return {"result": f"{request_data} 처리 완료"}

    def call_with_deadline(service_func, request_data, timeout_seconds):
        """Deadline이 있는 gRPC 호출 시뮬레이션"""
        deadline = time.time() + timeout_seconds
        start = time.time()

        # 서비스 호출
        result = service_func(request_data, processing_time=0.1)
        elapsed = time.time() - start

        if time.time() > deadline:
            return {
                "status": "DEADLINE_EXCEEDED",
                "error": f"시간 초과! ({elapsed:.2f}초 > {timeout_seconds}초)",
            }
        return {
            "status": "OK",
            "data": result,
            "elapsed": f"{elapsed:.2f}초",
            "remaining": f"{deadline - time.time():.2f}초 남음",
        }

    # 여유로운 타임아웃
    print("  [테스트 1] 타임아웃 5초, 처리 시간 0.1초")
    r1 = call_with_deadline(slow_service, "학생 조회", timeout_seconds=5)
    print(f"    결과: {r1['status']} ({r1.get('elapsed', '')})")
    print()

    # Deadline 전파 예시
    print("  [Deadline 전파 시나리오]")
    print("    클라이언트 → 서비스A → 서비스B → 서비스C")
    print()
    total_deadline = 3.0
    print(f"    클라이언트가 설정한 Deadline: {total_deadline}초")

    services = [("서비스A", 0.8), ("서비스B", 0.5), ("서비스C", 0.3)]
    remaining = total_deadline

    for name, duration in services:
        remaining -= duration
        status = "[O] OK" if remaining > 0 else "[X] DEADLINE_EXCEEDED"
        print(f"    {name}: {duration}초 소요 → 남은 시간: {max(0, remaining):.1f}초 {status}")

    print()
    print("  Deadline 모범 사례:")
    print("    1. 항상 Deadline을 설정하세요 (기본값: 무한대는 위험!)")
    print("    2. 서비스 체인에서는 각 단계에서 남은 시간을 확인")
    print("    3. 남은 시간이 부족하면 요청을 시작하지 않는 것이 효율적")
    print()


def lesson4_cancellation():
    # =========================================================================
    #   레슨 4 — 취소 (Cancellation)
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 4 : 취소 (Cancellation)               │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 취소 = 진행 중인 요청을 중간에 멈추기
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     식당에서 주문 후 "아, 저 메뉴 취소할게요!" 하는 것
    #     아직 요리 시작 전이면 바로 취소 가능!
    #     이미 요리 중이면... 만들던 것을 멈추고 재료 낭비 최소화
    #
    #   취소가 필요한 상황:
    #     1. 사용자가 검색 취소 버튼을 누름
    #     2. 여러 서버에 동시 요청 후 가장 빠른 것만 사용
    #     3. 페이지 이동 시 이전 페이지 요청 취소
    #

    class CancellableOperation:
        def __init__(self):
            self.cancelled = False
            self.results = []

        def cancel(self):
            self.cancelled = True

        def long_running_task(self, total_steps):
            """취소 가능한 긴 작업"""
            for step in range(1, total_steps + 1):
                if self.cancelled:
                    return {
                        "status": "CANCELLED",
                        "completed_steps": step - 1,
                        "total_steps": total_steps,
                    }
                self.results.append(f"단계 {step} 완료")

            return {
                "status": "OK",
                "completed_steps": total_steps,
                "total_steps": total_steps,
            }

    # 취소 없이 완료
    print("  [테스트 1] 취소 없이 실행")
    op1 = CancellableOperation()
    r1 = op1.long_running_task(5)
    print(f"    결과: {r1['status']} ({r1['completed_steps']}/{r1['total_steps']} 완료)")
    print()

    # 중간에 취소
    print("  [테스트 2] 3단계 후 취소")
    op2 = CancellableOperation()
    # 3단계까지 수동 실행 후 취소
    for i in range(3):
        op2.results.append(f"단계 {i + 1} 완료")
    op2.cancel()
    r2 = op2.long_running_task(10)
    print(f"    결과: {r2['status']} ({r2['completed_steps']}/{r2['total_steps']} 완료)")
    print()

    print("  취소 처리 모범 사례:")
    print("    1. 서버는 주기적으로 취소 여부를 확인해야 함")
    print("    2. 취소 시 이미 변경된 데이터는 롤백 고려")
    print("    3. 스트리밍 중 취소는 즉시 스트림을 닫음")
    print("    4. 취소된 요청의 상태 코드: CANCELLED (1)")
    print()


def lesson5_compression():
    # =========================================================================
    #   레슨 5 — 압축 (Compression)
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 5 : 압축 (Compression)                │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 압축 = 데이터를 작게 줄여서 보내기
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     여행 갈 때 옷을 압축팩에 넣으면
    #     가방 공간이 절약되는 것처럼!
    #     데이터를 압축하면 네트워크 트래픽이 줄어듭니다.
    #
    #   gRPC 압축 알고리즘:
    #     - gzip: 압축률 높음, CPU 많이 사용
    #     - deflate: gzip과 비슷
    #     - snappy: 압축률 낮지만 빠름 (구글 개발)
    #

    import zlib

    # 압축 효과 비교
    data_samples = {
        "작은 데이터": json.dumps({"name": "민수"}).encode(),
        "반복 많은 데이터": json.dumps(
            [{"id": i, "name": f"학생{i}", "score": 85} for i in range(100)]
        ).encode(),
        "큰 텍스트": ("학생 정보를 관리하는 시스템입니다. " * 200).encode(),
    }

    print("  데이터 압축 효과 비교:")
    print(f"  {'데이터 종류':<18s} {'원본':<12s} {'압축 후':<12s} {'절약률':<10s}")
    print(f"  {'─' * 18} {'─' * 12} {'─' * 12} {'─' * 10}")

    for name, data in data_samples.items():
        compressed = zlib.compress(data)
        original_size = len(data)
        compressed_size = len(compressed)
        savings = (1 - compressed_size / original_size) * 100

        print(f"  {name:<18s} {original_size:>8d} B  {compressed_size:>8d} B  {savings:>6.1f}%")
    print()

    print("  압축 사용 가이드:")
    print("    - 큰 데이터: 압축하면 효과 큼!")
    print("    - 작은 데이터: 압축 오버헤드가 더 클 수 있음")
    print("    - CPU 여유 있고 네트워크 느린 환경: gzip 추천")
    print("    - CPU 부족하고 네트워크 빠른 환경: 압축 안 하는 게 나을 수도")
    print()


def lesson6_grpc_web():
    # =========================================================================
    #   레슨 6 — gRPC-Web
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 6 : gRPC-Web                          │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ gRPC-Web = 브라우저에서 gRPC를 쓸 수 있게 하는 것
    # ─────────────────────────────────────────────────────────────────────
    #
    #   문제:
    #     브라우저는 HTTP/2의 모든 기능을 직접 제어할 수 없습니다.
    #     gRPC는 HTTP/2가 필수인데, 브라우저에서 직접 gRPC 호출이 안 됨!
    #
    #   해결:
    #     gRPC-Web이라는 변환 계층을 사이에 넣습니다.
    #
    #     브라우저 → [gRPC-Web 프록시] → gRPC 서버
    #              (Envoy 등)
    #
    #   비유:
    #     외국인(브라우저)과 한국인(gRPC 서버) 사이에
    #     통역사(gRPC-Web 프록시)를 세우는 것!
    #

    print("  gRPC-Web 아키텍처:")
    print()
    print("    ┌──────────┐     ┌─────────────┐     ┌──────────┐")
    print("    │  브라우저 │ →→→ │ gRPC-Web    │ →→→ │  gRPC    │")
    print("    │ (React,  │     │ 프록시      │     │  서버    │")
    print("    │  Vue 등) │ ←←← │ (Envoy 등)  │ ←←← │          │")
    print("    └──────────┘     └─────────────┘     └──────────┘")
    print("     HTTP/1.1 or       변환 담당          HTTP/2")
    print("     HTTP/2                               + protobuf")
    print()

    print("  gRPC-Web 제약사항:")
    print("    - Unary 호출: [O] 지원")
    print("    - Server Streaming: [O] 지원")
    print("    - Client Streaming: [X] 미지원")
    print("    - Bidirectional Streaming: [X] 미지원")
    print()

    print("  gRPC-Web vs REST (브라우저 관점):")
    print("    REST:     브라우저에서 바로 fetch() 호출")
    print("    gRPC-Web: proto 파일로 생성된 클라이언트 코드 사용")
    print("              → 타입 안전성, 자동 완성 지원")
    print()

    print("  결론:")
    print("    - 백엔드 간 통신: gRPC 직접 사용")
    print("    - 프론트엔드: gRPC-Web 또는 REST (상황에 따라 선택)")
    print("    - gRPC-Web을 쓰면 프론트/백엔드가 같은 .proto 사용 가능!")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("  gRPC 08단계 : gRPC 패턴과 고급 기능")
    print("=" * 72)
    print()

    lesson1_grpc_vs_rest()
    lesson2_bidirectional_streaming_chat()
    lesson3_deadline_timeout()
    lesson4_cancellation()
    lesson5_compression()
    lesson6_grpc_web()
