# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   gRPC 학습 04단계: 에러 처리와 메타데이터
#   ─ gRPC 상태 코드, 메타데이터, 에러 디테일, Rich Error Model ─
#
#   gRPC에서 에러가 나면 HTTP처럼 숫자 코드 대신
#   이름이 있는 상태 코드(OK, NOT_FOUND 등)를 사용합니다.
#
#   ■ 실행: python error_handling.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import json
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any


# ─────────────────────────────────────────────────────────────────────
# ■ gRPC 상태 코드 정의 (실제 grpc 라이브러리의 코드를 흉내)
# ─────────────────────────────────────────────────────────────────────

class StatusCode:
    """gRPC 상태 코드 모음"""
    OK = 0                  # 성공
    CANCELLED = 1           # 클라이언트가 취소함
    UNKNOWN = 2             # 알 수 없는 에러
    INVALID_ARGUMENT = 3    # 잘못된 인자
    DEADLINE_EXCEEDED = 4   # 시간 초과
    NOT_FOUND = 5           # 찾을 수 없음
    ALREADY_EXISTS = 6      # 이미 존재함
    PERMISSION_DENIED = 7   # 권한 없음
    RESOURCE_EXHAUSTED = 8  # 자원 소진 (rate limit)
    FAILED_PRECONDITION = 9   # 전제 조건 실패
    ABORTED = 10            # 중단됨
    OUT_OF_RANGE = 11       # 범위 초과
    UNIMPLEMENTED = 12      # 구현되지 않음
    INTERNAL = 13           # 서버 내부 에러
    UNAVAILABLE = 14        # 서비스 이용 불가
    DATA_LOSS = 15          # 데이터 손실
    UNAUTHENTICATED = 16    # 인증되지 않음


STATUS_NAMES = {
    0: "OK", 1: "CANCELLED", 2: "UNKNOWN", 3: "INVALID_ARGUMENT",
    4: "DEADLINE_EXCEEDED", 5: "NOT_FOUND", 6: "ALREADY_EXISTS",
    7: "PERMISSION_DENIED", 8: "RESOURCE_EXHAUSTED", 9: "FAILED_PRECONDITION",
    10: "ABORTED", 11: "OUT_OF_RANGE", 12: "UNIMPLEMENTED",
    13: "INTERNAL", 14: "UNAVAILABLE", 15: "DATA_LOSS", 16: "UNAUTHENTICATED",
}


@dataclass
class GrpcError:
    """gRPC 에러 응답을 표현하는 클래스"""
    code: int
    message: str
    details: Optional[List[Dict]] = None

    @property
    def status_name(self):
        return STATUS_NAMES.get(self.code, "UNKNOWN")

    def __str__(self):
        return f"gRPC Error [{self.status_name}({self.code})]: {self.message}"


# ─────────────────────────────────────────────────────────────────────
# ■ 가짜 학생 데이터
# ─────────────────────────────────────────────────────────────────────
STUDENTS = {
    1: {"id": 1, "name": "민수", "grade": 3, "score": 92},
    2: {"id": 2, "name": "지우", "grade": 2, "score": 88},
}


def lesson1_grpc_status_codes():
    # =========================================================================
    #   레슨 1 — gRPC 상태 코드
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 1 : gRPC 상태 코드                     │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ gRPC 상태 코드 = HTTP 상태 코드의 gRPC 버전
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     HTTP가 "200, 404, 500" 같은 숫자로 결과를 말한다면,
    #     gRPC는 "OK, NOT_FOUND, INTERNAL" 같은 이름으로 결과를 말합니다.
    #     이름이 있으니 코드 의미를 바로 알 수 있어서 편합니다!
    #
    #   HTTP ↔ gRPC 대응:
    #     HTTP 200  ↔  OK
    #     HTTP 400  ↔  INVALID_ARGUMENT
    #     HTTP 401  ↔  UNAUTHENTICATED
    #     HTTP 403  ↔  PERMISSION_DENIED
    #     HTTP 404  ↔  NOT_FOUND
    #     HTTP 429  ↔  RESOURCE_EXHAUSTED
    #     HTTP 500  ↔  INTERNAL
    #     HTTP 503  ↔  UNAVAILABLE
    #

    common_codes = [
        (StatusCode.OK, "성공! 모든 것이 정상입니다."),
        (StatusCode.INVALID_ARGUMENT, "요청 데이터가 잘못됨 (이름이 비어 있다거나)"),
        (StatusCode.NOT_FOUND, "찾으려는 학생이 존재하지 않음"),
        (StatusCode.ALREADY_EXISTS, "이미 같은 학번의 학생이 있음"),
        (StatusCode.PERMISSION_DENIED, "이 작업을 할 권한이 없음"),
        (StatusCode.UNAUTHENTICATED, "로그인이 필요함"),
        (StatusCode.INTERNAL, "서버 내부에서 뭔가 잘못됨"),
        (StatusCode.UNAVAILABLE, "서버가 잠시 점검 중"),
        (StatusCode.DEADLINE_EXCEEDED, "요청 처리 시간이 너무 오래 걸림"),
        (StatusCode.RESOURCE_EXHAUSTED, "요청을 너무 많이 보냄 (속도 제한)"),
    ]

    print("  자주 사용하는 gRPC 상태 코드:")
    print()
    for code, description in common_codes:
        name = STATUS_NAMES[code]
        print(f"    {code:2d} {name:<22s} → {description}")
    print()


def lesson2_error_in_service():
    # =========================================================================
    #   레슨 2 — 서비스에서 에러 발생시키기
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 2 : 서비스에서 에러 발생                │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 서비스 함수에서 상황에 맞는 에러를 돌려주기
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     도서관 사서가 책을 찾아달라고 했을 때:
    #     "그 책은 없어요" → NOT_FOUND
    #     "대출 카드가 없네요" → UNAUTHENTICATED
    #     "연체 중이라 대출 불가" → PERMISSION_DENIED
    #

    def get_student(student_id, auth_token=None):
        """학생 정보를 조회하는 gRPC 서비스 함수 (시뮬레이션)"""

        # 인증 확인
        if auth_token is None:
            return None, GrpcError(
                code=StatusCode.UNAUTHENTICATED,
                message="인증 토큰이 필요합니다",
            )

        # ID 유효성 검증
        if student_id <= 0:
            return None, GrpcError(
                code=StatusCode.INVALID_ARGUMENT,
                message=f"학생 ID는 양수여야 합니다. 전달된 값: {student_id}",
            )

        # 학생 조회
        student = STUDENTS.get(student_id)
        if student is None:
            return None, GrpcError(
                code=StatusCode.NOT_FOUND,
                message=f"ID={student_id}인 학생을 찾을 수 없습니다",
            )

        return student, None

    # 다양한 시나리오 테스트
    test_cases = [
        {"id": 1, "token": "valid-token", "desc": "정상 조회"},
        {"id": 999, "token": "valid-token", "desc": "없는 학생"},
        {"id": -1, "token": "valid-token", "desc": "잘못된 ID"},
        {"id": 1, "token": None, "desc": "토큰 없음"},
    ]

    for case in test_cases:
        print(f"  [{case['desc']}] GetStudent(id={case['id']})")
        result, err = get_student(case["id"], case["token"])
        if err:
            print(f"    에러: {err}")
        else:
            print(f"    결과: {result}")
        print()


def lesson3_metadata():
    # =========================================================================
    #   레슨 3 — 메타데이터 (Headers / Trailers)
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 3 : 메타데이터                         │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 메타데이터 = gRPC의 HTTP 헤더 같은 것
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     편지를 보낼 때 봉투 겉면에 쓰는 정보입니다.
    #     - 보내는 사람 (인증 정보)
    #     - 받는 사람 (라우팅 정보)
    #     - 빠른우편 표시 (우선순위)
    #     편지 본문(payload)과는 별도로 전달되는 부가 정보!
    #
    #   두 종류:
    #     Headers  → 요청/응답 시작할 때 보내는 메타데이터
    #     Trailers → 응답이 끝날 때 보내는 메타데이터 (gRPC 고유!)
    #

    @dataclass
    class GrpcContext:
        """gRPC 요청 컨텍스트 (메타데이터 포함)"""
        headers: Dict[str, str] = field(default_factory=dict)
        trailers: Dict[str, str] = field(default_factory=dict)

        def add_header(self, key, value):
            self.headers[key] = value

        def add_trailer(self, key, value):
            self.trailers[key] = value

    # 클라이언트가 보내는 메타데이터
    ctx = GrpcContext()
    ctx.add_header("authorization", "Bearer my-token-123")
    ctx.add_header("x-request-id", "req-20260321-001")
    ctx.add_header("x-client-version", "1.2.0")

    print("  [클라이언트 → 서버] 요청 메타데이터 (Headers):")
    for key, value in ctx.headers.items():
        print(f"    {key}: {value}")
    print()

    # 서버가 보내는 메타데이터
    response_ctx = GrpcContext()
    response_ctx.add_header("x-server-region", "ap-northeast-2")
    response_ctx.add_header("x-ratelimit-remaining", "45")
    response_ctx.add_trailer("x-processing-time-ms", "23")
    response_ctx.add_trailer("x-cache-hit", "false")

    print("  [서버 → 클라이언트] 응답 메타데이터:")
    print("    Headers (시작 시):")
    for key, value in response_ctx.headers.items():
        print(f"      {key}: {value}")
    print("    Trailers (종료 시):")
    for key, value in response_ctx.trailers.items():
        print(f"      {key}: {value}")
    print()

    print("  메타데이터 키 규칙:")
    print("    - 일반 키: 소문자 + 숫자 + 하이픈 (예: x-request-id)")
    print("    - 바이너리 키: '-bin' 접미사 (예: icon-bin)")
    print("    - 바이너리 값은 base64로 인코딩됩니다.")
    print()


def lesson4_rich_error_model():
    # =========================================================================
    #   레슨 4 — Rich Error Model
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 4 : Rich Error Model                  │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Rich Error = 에러에 더 자세한 정보를 담는 방법
    # ─────────────────────────────────────────────────────────────────────
    #
    #   기본 에러:
    #     code: NOT_FOUND
    #     message: "학생을 찾을 수 없습니다"
    #     → 이것만으로는 정보가 부족할 수 있음!
    #
    #   Rich Error:
    #     code: INVALID_ARGUMENT
    #     message: "유효성 검증 실패"
    #     details: [
    #       BadRequest { field_violations: [...] },
    #       LocalizedMessage { locale: "ko", message: "..." },
    #       RetryInfo { retry_delay: 5s },
    #     ]
    #
    #   비유:
    #     병원에서 "아픕니다"만 하는 게 아니라
    #     "어디가 아픈지, 언제부터인지, 어떻게 하면 낫는지"
    #     자세한 진단서를 주는 것!
    #

    def create_rich_error():
        """유효성 검증 실패 시 Rich Error 생성"""
        return GrpcError(
            code=StatusCode.INVALID_ARGUMENT,
            message="학생 등록 데이터 유효성 검증에 실패했습니다",
            details=[
                {
                    "type": "BadRequest",
                    "field_violations": [
                        {
                            "field": "name",
                            "description": "이름은 비어 있을 수 없습니다",
                        },
                        {
                            "field": "score",
                            "description": "점수는 0~100 사이여야 합니다 (입력값: 150)",
                        },
                    ],
                },
                {
                    "type": "LocalizedMessage",
                    "locale": "ko-KR",
                    "message": "학생 정보를 다시 확인해 주세요.",
                },
                {
                    "type": "Help",
                    "links": [
                        {
                            "description": "학생 등록 API 문서",
                            "url": "https://api.school.kr/docs/students",
                        },
                    ],
                },
            ],
        )

    rich_err = create_rich_error()
    print(f"  에러: {rich_err}")
    print()
    print("  상세 정보 (details):")
    for detail in rich_err.details:
        print(f"    [{detail['type']}]")
        if detail["type"] == "BadRequest":
            for v in detail["field_violations"]:
                print(f"      - {v['field']}: {v['description']}")
        elif detail["type"] == "LocalizedMessage":
            print(f"      {detail['locale']}: {detail['message']}")
        elif detail["type"] == "Help":
            for link in detail["links"]:
                print(f"      {link['description']}: {link['url']}")
    print()

    # RetryInfo 예시
    print("  [서비스 이용 불가 시 RetryInfo 예시]")
    unavailable_err = GrpcError(
        code=StatusCode.UNAVAILABLE,
        message="서비스가 일시적으로 이용 불가합니다",
        details=[
            {
                "type": "RetryInfo",
                "retry_delay_seconds": 5,
                "description": "5초 후에 다시 시도해 주세요",
            },
        ],
    )
    print(f"  {unavailable_err}")
    print(f"  재시도 안내: {unavailable_err.details[0]['description']}")
    print()

    print("  Rich Error Model의 표준 타입들:")
    print("    BadRequest       → 어떤 필드가 왜 잘못됐는지")
    print("    RetryInfo        → 언제 다시 시도하면 되는지")
    print("    DebugInfo        → 디버깅용 스택 트레이스")
    print("    QuotaFailure     → 어떤 할당량을 초과했는지")
    print("    PreconditionFailure → 어떤 전제 조건이 안 맞는지")
    print("    LocalizedMessage → 사용자 언어에 맞는 메시지")
    print("    Help             → 관련 문서 링크")
    print()


def lesson5_error_handling_pattern():
    # =========================================================================
    #   레슨 5 — 에러 처리 패턴 요약
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 5 : 에러 처리 패턴 요약                │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 클라이언트에서 에러를 처리하는 패턴
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     전화를 걸었을 때 상황별 대응:
    #     - 통화 중 (UNAVAILABLE) → 잠시 후 다시 걸기
    #     - 번호 없음 (NOT_FOUND) → 번호 확인하기
    #     - 전화기 고장 (INTERNAL) → 수리 맡기기
    #

    def handle_grpc_error(err):
        """에러 코드별 처리 전략"""
        strategies = {
            StatusCode.INVALID_ARGUMENT: "입력값을 수정한 후 다시 시도",
            StatusCode.NOT_FOUND: "요청한 리소스가 존재하는지 확인",
            StatusCode.ALREADY_EXISTS: "중복 데이터를 확인",
            StatusCode.PERMISSION_DENIED: "권한을 요청하거나 관리자에게 문의",
            StatusCode.UNAUTHENTICATED: "로그인 후 다시 시도",
            StatusCode.RESOURCE_EXHAUSTED: "잠시 후 다시 시도 (속도 제한)",
            StatusCode.UNAVAILABLE: "잠시 후 재시도 (서버 점검 중)",
            StatusCode.DEADLINE_EXCEEDED: "타임아웃 늘리거나 요청 크기 줄이기",
            StatusCode.INTERNAL: "서버 관리자에게 로그 확인 요청",
        }

        strategy = strategies.get(err.code, "알 수 없는 에러 — 로그를 확인하세요")

        # 재시도 가능한 에러인지 판단
        retryable = err.code in [
            StatusCode.UNAVAILABLE,
            StatusCode.DEADLINE_EXCEEDED,
            StatusCode.RESOURCE_EXHAUSTED,
        ]

        return {
            "error": str(err),
            "strategy": strategy,
            "retryable": retryable,
        }

    test_errors = [
        GrpcError(StatusCode.NOT_FOUND, "학생을 찾을 수 없습니다"),
        GrpcError(StatusCode.UNAVAILABLE, "서버 점검 중"),
        GrpcError(StatusCode.INVALID_ARGUMENT, "이름이 비어 있습니다"),
        GrpcError(StatusCode.INTERNAL, "데이터베이스 연결 실패"),
    ]

    for err in test_errors:
        result = handle_grpc_error(err)
        print(f"  에러: {err.status_name}")
        print(f"    대응: {result['strategy']}")
        print(f"    재시도 가능: {'예' if result['retryable'] else '아니오'}")
        print()


if __name__ == "__main__":
    print("=" * 72)
    print("  gRPC 04단계 : 에러 처리와 메타데이터")
    print("=" * 72)
    print()

    lesson1_grpc_status_codes()
    lesson2_error_in_service()
    lesson3_metadata()
    lesson4_rich_error_model()
    lesson5_error_handling_pattern()
