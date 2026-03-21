# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   gRPC 학습 05단계: 인터셉터와 미들웨어
#   ─ Unary/Stream 인터셉터, 로깅, 인증, 재시도, 체인 패턴 ─
#
#   인터셉터는 모든 요청/응답을 가로채서 공통 작업을 하는 장치입니다.
#   HTTP의 미들웨어(middleware)와 같은 개념입니다.
#
#   ■ 실행: python interceptor.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import time
import functools
from dataclasses import dataclass
from typing import Callable, Any, Optional, List


# ─────────────────────────────────────────────────────────────────────
# ■ 기본 구조: 요청, 응답, 서비스 함수
# ─────────────────────────────────────────────────────────────────────

@dataclass
class Request:
    method: str
    data: dict
    metadata: dict  # 메타데이터 (헤더와 비슷)


@dataclass
class Response:
    data: Any
    status: str = "OK"
    error: Optional[str] = None


# 가짜 서비스 함수들
def get_student_service(request: Request) -> Response:
    """학생 조회 서비스"""
    student_id = request.data.get("id")
    students = {1: "민수", 2: "지우", 3: "서연"}

    if student_id in students:
        return Response(data={"id": student_id, "name": students[student_id]})
    return Response(data=None, status="NOT_FOUND", error=f"학생 ID={student_id} 없음")


def create_student_service(request: Request) -> Response:
    """학생 등록 서비스"""
    name = request.data.get("name", "")
    if not name.strip():
        return Response(data=None, status="INVALID_ARGUMENT", error="이름이 비어 있음")
    return Response(data={"id": 4, "name": name}, status="OK")


def lesson1_what_is_interceptor():
    # =========================================================================
    #   레슨 1 — 인터셉터란?
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 1 : 인터셉터란?                        │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 인터셉터 = 요청/응답을 중간에 가로채는 장치
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     공항 보안 검색대를 떠올려 보세요!
    #
    #     승객(요청) → [보안검색] → [여권확인] → [짐검사] → 비행기(서비스)
    #
    #     모든 승객이 동일한 절차를 거치듯,
    #     모든 gRPC 요청이 동일한 인터셉터 체인을 거칩니다.
    #
    #     인터셉터가 없으면:
    #       - 모든 서비스 함수에 로깅 코드를 복붙해야 함
    #       - 모든 서비스 함수에 인증 코드를 복붙해야 함
    #       → 반복! 실수! 유지보수 지옥!
    #
    #     인터셉터가 있으면:
    #       - 로깅은 로깅 인터셉터에 한 번만 작성
    #       - 인증은 인증 인터셉터에 한 번만 작성
    #       → 깔끔! 재사용! 쉬운 유지보수!
    #
    #   두 종류:
    #     Unary Interceptor  → 일반 요청/응답 (1:1)
    #     Stream Interceptor → 스트리밍 요청/응답 (1:N, N:1, N:N)
    #

    print("  인터셉터 실행 순서:")
    print()
    print("    클라이언트 요청")
    print("        ↓")
    print("    ┌─ 인터셉터 1 (로깅) ─┐")
    print("    │  ┌─ 인터셉터 2 (인증) ─┐")
    print("    │  │  ┌─ 인터셉터 3 (재시도) ─┐")
    print("    │  │  │                       │")
    print("    │  │  │   실제 서비스 함수     │")
    print("    │  │  │                       │")
    print("    │  │  └───────────────────────┘")
    print("    │  └─────────────────────────┘")
    print("    └───────────────────────────┘")
    print("        ↓")
    print("    클라이언트 응답")
    print()


def lesson2_logging_interceptor():
    # =========================================================================
    #   레슨 2 — 로깅 인터셉터
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 2 : 로깅 인터셉터                      │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 로깅 인터셉터 = 모든 요청/응답을 기록
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     CCTV처럼 모든 출입을 기록하는 장치
    #     누가 언제 왔는지, 얼마나 걸렸는지 자동 기록!
    #

    def logging_interceptor(handler):
        """모든 요청/응답을 로깅하는 인터셉터"""
        @functools.wraps(handler)
        def wrapper(request: Request) -> Response:
            start = time.time()
            print(f"    [LOG] → 요청: {request.method} 데이터={request.data}")

            # 실제 서비스 호출
            response = handler(request)

            elapsed = (time.time() - start) * 1000
            print(f"    [LOG] ← 응답: status={response.status} ({elapsed:.1f}ms)")
            return response
        return wrapper

    # 로깅 인터셉터 적용
    logged_service = logging_interceptor(get_student_service)

    print("  [로깅 인터셉터 적용된 요청]")
    req = Request(method="GetStudent", data={"id": 1}, metadata={})
    result = logged_service(req)
    print(f"    결과: {result.data}")
    print()

    print("  [없는 학생 조회]")
    req2 = Request(method="GetStudent", data={"id": 999}, metadata={})
    result2 = logged_service(req2)
    print(f"    결과: {result2.error}")
    print()


def lesson3_auth_interceptor():
    # =========================================================================
    #   레슨 3 — 인증 인터셉터
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 3 : 인증 인터셉터                      │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 인증 인터셉터 = 토큰을 확인하고 권한 없으면 거부
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     건물 로비의 경비원
    #     출입증이 없으면 → "들어올 수 없습니다!" (UNAUTHENTICATED)
    #     출입증이 만료됨 → "갱신하고 오세요!" (UNAUTHENTICATED)
    #

    VALID_TOKENS = {"token-minsu-123": "민수", "token-teacher-456": "김선생님"}

    def auth_interceptor(handler):
        """인증 토큰을 확인하는 인터셉터"""
        @functools.wraps(handler)
        def wrapper(request: Request) -> Response:
            token = request.metadata.get("authorization", "")

            if not token:
                print(f"    [AUTH] [X] 토큰 없음 → UNAUTHENTICATED")
                return Response(data=None, status="UNAUTHENTICATED",
                                error="인증 토큰이 필요합니다")

            user = VALID_TOKENS.get(token)
            if user is None:
                print(f"    [AUTH] [X] 유효하지 않은 토큰 → UNAUTHENTICATED")
                return Response(data=None, status="UNAUTHENTICATED",
                                error="유효하지 않은 토큰입니다")

            print(f"    [AUTH] [O] 인증 성공: {user}")
            request.metadata["authenticated_user"] = user
            return handler(request)
        return wrapper

    authed_service = auth_interceptor(get_student_service)

    # 토큰 없이 요청
    print("  [토큰 없이 요청]")
    req1 = Request(method="GetStudent", data={"id": 1}, metadata={})
    r1 = authed_service(req1)
    print(f"    결과: {r1.status} — {r1.error}")
    print()

    # 유효한 토큰으로 요청
    print("  [유효한 토큰으로 요청]")
    req2 = Request(method="GetStudent", data={"id": 1},
                   metadata={"authorization": "token-minsu-123"})
    r2 = authed_service(req2)
    print(f"    결과: {r2.data}")
    print()

    # 잘못된 토큰
    print("  [잘못된 토큰으로 요청]")
    req3 = Request(method="GetStudent", data={"id": 1},
                   metadata={"authorization": "fake-token"})
    r3 = authed_service(req3)
    print(f"    결과: {r3.status} — {r3.error}")
    print()


def lesson4_retry_interceptor():
    # =========================================================================
    #   레슨 4 — 재시도 인터셉터
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 4 : 재시도 인터셉터                    │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 재시도 인터셉터 = 실패하면 자동으로 다시 시도
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     전화가 안 받으면 3번까지 다시 거는 것!
    #     단, 모든 에러를 재시도하면 안 됩니다.
    #     "번호가 없음"(NOT_FOUND)은 재시도해도 소용없고,
    #     "통화 중"(UNAVAILABLE)은 잠시 후 다시 걸면 될 수 있습니다.
    #

    call_count = 0

    def flaky_service(request: Request) -> Response:
        """불안정한 서비스 (3번째 시도에 성공)"""
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            return Response(data=None, status="UNAVAILABLE",
                            error="서버 일시 장애")
        return Response(data={"message": "성공!"})

    RETRYABLE_STATUSES = {"UNAVAILABLE", "DEADLINE_EXCEEDED", "RESOURCE_EXHAUSTED"}

    def retry_interceptor(max_retries=3):
        """재시도 인터셉터 (팩토리 함수)"""
        def decorator(handler):
            @functools.wraps(handler)
            def wrapper(request: Request) -> Response:
                last_response = None
                for attempt in range(1, max_retries + 1):
                    response = handler(request)
                    last_response = response

                    if response.status == "OK":
                        print(f"    [RETRY] 시도 {attempt}: 성공!")
                        return response

                    if response.status not in RETRYABLE_STATUSES:
                        print(f"    [RETRY] 시도 {attempt}: {response.status} — 재시도 불가")
                        return response

                    print(f"    [RETRY] 시도 {attempt}: {response.status} — 재시도...")

                print(f"    [RETRY] 최대 재시도 횟수({max_retries}) 초과!")
                return last_response
            return wrapper
        return decorator

    # 재시도 인터셉터 적용
    call_count = 0
    retried_service = retry_interceptor(max_retries=3)(flaky_service)

    print("  [불안정한 서비스에 재시도 인터셉터 적용]")
    req = Request(method="UnstableCall", data={}, metadata={})
    result = retried_service(req)
    print(f"    최종 결과: {result.data}")
    print()


def lesson5_interceptor_chain():
    # =========================================================================
    #   레슨 5 — 인터셉터 체인 (여러 인터셉터 조합)
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 5 : 인터셉터 체인                      │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 인터셉터 체인 = 여러 인터셉터를 순서대로 연결
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     공장 조립 라인:
    #     원재료 → [세척] → [검사] → [포장] → [라벨] → 완제품
    #
    #     각 단계가 독립적이고, 순서를 바꾸거나 단계를 추가/제거할 수 있음!
    #

    def apply_interceptors(handler, interceptors):
        """여러 인터셉터를 체인으로 연결"""
        result = handler
        # 뒤에서부터 감싸야 첫 번째 인터셉터가 가장 바깥에 위치
        for interceptor in reversed(interceptors):
            result = interceptor(result)
        return result

    # 인터셉터들 정의
    def timing_interceptor(handler):
        @functools.wraps(handler)
        def wrapper(request):
            start = time.time()
            response = handler(request)
            elapsed = (time.time() - start) * 1000
            print(f"    [TIMING] 처리 시간: {elapsed:.1f}ms")
            return response
        return wrapper

    def request_id_interceptor(handler):
        @functools.wraps(handler)
        def wrapper(request):
            req_id = f"req-{int(time.time() * 1000) % 100000}"
            request.metadata["request_id"] = req_id
            print(f"    [REQ-ID] 요청 ID: {req_id}")
            response = handler(request)
            return response
        return wrapper

    def validation_interceptor(handler):
        @functools.wraps(handler)
        def wrapper(request):
            if not request.data:
                print(f"    [VALID] [X] 데이터가 비어 있음")
                return Response(data=None, status="INVALID_ARGUMENT",
                                error="요청 데이터가 비어 있습니다")
            print(f"    [VALID] [O] 데이터 검증 통과")
            return handler(request)
        return wrapper

    # 체인 구성: 타이밍 → 요청ID → 검증 → 서비스
    interceptors = [timing_interceptor, request_id_interceptor, validation_interceptor]
    chained_service = apply_interceptors(get_student_service, interceptors)

    print("  [인터셉터 체인: TIMING → REQ-ID → VALID → 서비스]")
    print()
    req = Request(method="GetStudent", data={"id": 1}, metadata={})
    result = chained_service(req)
    print(f"    최종 결과: {result.data}")
    print()

    print("  인터셉터 체인 구성 팁:")
    print("    1. 로깅/타이밍 → 가장 바깥 (모든 것을 기록)")
    print("    2. 인증 → 그 다음 (권한 없으면 일찍 거부)")
    print("    3. 검증 → 서비스 직전 (데이터 확인)")
    print("    4. 순서가 중요합니다! 인증 전에 로깅이 와야")
    print("       인증 실패도 로그에 남습니다.")
    print()


def lesson6_stream_interceptor():
    # =========================================================================
    #   레슨 6 — 스트림 인터셉터
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 6 : 스트림 인터셉터                    │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 스트림 인터셉터 = 스트리밍 요청/응답을 가로채기
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     unary 인터셉터는 편지 1통을 검사하는 것이라면,
    #     stream 인터셉터는 컨베이어 벨트 위의 택배를 하나씩 검사하는 것!
    #     각 메시지가 지나갈 때마다 가로채서 확인합니다.
    #

    def server_streaming_service(request):
        """학생 알림을 스트리밍으로 보내는 서비스"""
        names = request.data.get("names", [])
        for i, name in enumerate(names, 1):
            yield Response(data={"turn": i, "message": f"{name} 학생 차례입니다"})

    def stream_logging_interceptor(stream_handler):
        """스트림 메시지를 하나씩 로깅하는 인터셉터"""
        @functools.wraps(stream_handler)
        def wrapper(request):
            print(f"    [STREAM-LOG] 스트림 시작: {request.method}")
            message_count = 0

            for response in stream_handler(request):
                message_count += 1
                print(f"    [STREAM-LOG] 메시지 #{message_count}: {response.data}")
                yield response

            print(f"    [STREAM-LOG] 스트림 종료: 총 {message_count}개 메시지")
        return wrapper

    logged_stream = stream_logging_interceptor(server_streaming_service)

    print("  [스트림 인터셉터 적용]")
    req = Request(
        method="NotifyStudents",
        data={"names": ["민수", "지우", "서연"]},
        metadata={},
    )

    results = list(logged_stream(req))
    print(f"    받은 메시지 수: {len(results)}")
    print()

    print("  스트림 인터셉터 활용:")
    print("    - 각 메시지의 크기/수를 모니터링")
    print("    - 메시지별 유효성 검증")
    print("    - 스트림 전체의 처리 시간 측정")
    print("    - 메시지 변환/가공 (압축, 암호화 등)")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("  gRPC 05단계 : 인터셉터와 미들웨어")
    print("=" * 72)
    print()

    lesson1_what_is_interceptor()
    lesson2_logging_interceptor()
    lesson3_auth_interceptor()
    lesson4_retry_interceptor()
    lesson5_interceptor_chain()
    lesson6_stream_interceptor()
