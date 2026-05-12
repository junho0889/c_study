# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [데이터 연계] 학습 12단계: gRPC & Protobuf
#   ─ IDL · 4 가지 호출 패턴 · 스트리밍 · 인터셉터 ─
#   ■ 실행 방법: python 12_grpc.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 왜 gRPC? — 마이크로서비스 내부 통신의 강자
#   2. Protobuf — IDL + 효율적 직렬화
#   3. 4 가지 호출 패턴 (단방향 / 서버 스트림 / 클라이언트 스트림 / 양방향)
#   4. 인증/인터셉터/메타데이터
#   5. 에러 모델과 retry, deadline
#   6. gRPC vs REST/GraphQL — 언제 무엇을
#   7. 실전: .proto 파일과 호출 의사코드
#
# ─────────────────────────────────────────────────────────────────────────


def lesson1_why_grpc():
    # =========================================================================
    #   레슨 1 — 왜 gRPC
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 왜 gRPC                    │")
    print("└──────────────────────────────────────┘")
    # ■ 장점:
    #   - HTTP/2 멀티플렉싱 → 한 커넥션에 다수 요청
    #   - Protobuf 직렬화 = 작고 빠름
    #   - 다국어(언어 11+) 자동 코드 생성
    #   - 스트리밍 자연스러움
    #
    # ■ 한계:
    #   - 브라우저에서 직접 호출 어려움 (gRPC-Web 별도)
    #   - 텍스트 디버깅 어려움
    #   - HTTP 캐시 활용 X
    print(" gRPC = ‘서버-서버 강 결합 마이크로서비스’의 사실상 표준.")
    print()


def lesson2_protobuf():
    # =========================================================================
    #   레슨 2 — Protobuf
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : Protobuf                   │")
    print("└──────────────────────────────────────┘")
    proto = r"""
syntax = "proto3";
package orders.v1;

option go_package = "github.com/example/orders/v1";

message Order {
  int64  id        = 1;
  int64  user_id   = 2;
  double amount    = 3;
  string currency  = 4;     // "KRW", "USD"
  google.protobuf.Timestamp created_at = 5;
}

message CreateOrderRequest {
  int64 user_id = 1;
  double amount = 2;
  string currency = 3;
}

service OrderService {
  rpc CreateOrder(CreateOrderRequest) returns (Order);
  rpc GetOrder(GetOrderRequest) returns (Order);
  rpc StreamOrders(StreamOrdersRequest) returns (stream Order);
}
"""
    print(proto)
    # ■ 핵심:
    #   - 필드 번호 1,2,3 은 ‘영구 식별자’. 절대 재사용 금지.
    #   - 추가는 OK (호환), 변경/제거는 위험.
    #   - reserved 키워드로 ‘예약/금지’ 명시 가능.


def lesson3_four_patterns():
    # =========================================================================
    #   레슨 3 — 4 호출 패턴
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : 4 호출 패턴                │")
    print("└──────────────────────────────────────┘")
    # ■ 1) Unary:                CreateOrder(req) → Order
    # ■ 2) Server streaming:     StreamOrders(req) → stream Order  (구독, 실시간)
    # ■ 3) Client streaming:     UploadEvents(stream Event) → Ack
    # ■ 4) Bidirectional:        Chat(stream Msg) → stream Msg
    #
    # ■ 도메인 매핑:
    #   - 실시간 알림 / 로그 → server streaming
    #   - 대용량 업로드 → client streaming
    #   - 양방향 대화 / 협업 → bidirectional
    print(" 4 패턴이 ‘REST 흉내’로는 어려운 흐름을 자연스럽게 표현.")
    print()


def lesson4_auth_interceptor():
    # =========================================================================
    #   레슨 4 — 인증 / 인터셉터
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : 인증 / 인터셉터            │")
    print("└──────────────────────────────────────┘")
    # ■ 메타데이터(metadata):
    #   - HTTP 헤더와 비슷한 key-value
    #   - 'authorization': 'Bearer ...'
    #
    # ■ 인터셉터:
    #   - 클라이언트/서버 모두 가능
    #   - 로깅, 인증, retry, deadline, 트레이싱
    #
    # ■ 보안:
    #   - mTLS (양방향 TLS) 가 흔함 — 마이크로서비스 간 신뢰
    #   - OPA / Authz 정책 엔진 결합
    print(" gRPC 의 인증/관측은 ‘인터셉터 체인’으로 표준화.")
    print()


def lesson5_errors_deadline():
    # =========================================================================
    #   레슨 5 — 에러 / 재시도 / deadline
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 에러 / deadline            │")
    print("└──────────────────────────────────────┘")
    # ■ gRPC Status codes:
    #   - OK / CANCELLED / INVALID_ARGUMENT / NOT_FOUND
    #   - PERMISSION_DENIED / RESOURCE_EXHAUSTED / FAILED_PRECONDITION
    #   - ABORTED / UNAVAILABLE / DEADLINE_EXCEEDED / INTERNAL
    #
    # ■ Deadline:
    #   - 호출 시 ‘여기까지 안 끝나면 실패’ 시간 명시
    #   - 분산 추적의 ‘우산’ — 호출 트리 전체에 propagate
    #
    # ■ Retry:
    #   - UNAVAILABLE / DEADLINE_EXCEEDED 류만 재시도
    #   - “Idempotent 한 메서드” 라는 라벨이 필수
    print(" Deadline + 멱등 메서드 라벨이 분산 시스템 안정의 두 기둥.")
    print()


def lesson6_compare():
    # =========================================================================
    #   레슨 6 — gRPC vs REST/GraphQL
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 비교                       │")
    print("└──────────────────────────────────────┘")
    # ┌─────────────┬──────────┬──────────┬──────────┐
    # │ 측면        │ REST     │ GraphQL  │ gRPC     │
    # ├─────────────┼──────────┼──────────┼──────────┤
    # │ 클라이언트   │ 풍부     │ 풍부     │ 코드생성   │
    # │ 브라우저    │ 자연스러움│ 자연스러움│ gRPC-Web  │
    # │ 직렬화      │ JSON     │ JSON     │ Protobuf   │
    # │ 스트리밍    │ SSE/WS   │ Subscription │ 4 가지   │
    # │ 캐시(CDN)   │ 강함     │ 약함     │ 거의 없음   │
    # │ 디버깅      │ 쉬움     │ 보통     │ 어려움     │
    # └─────────────┴──────────┴──────────┴──────────┘
    #
    # ■ 권장 매핑:
    #   - 공개/외부 API → REST or GraphQL
    #   - 사내 마이크로서비스 → gRPC
    #   - 모바일/실시간 → 혼합
    print(" 사내 = gRPC,  외부 = REST/GraphQL.  결합 사례도 늘고 있다 (Connect, Buf).")
    print()


def lesson7_practice_proto_and_call():
    # =========================================================================
    #   레슨 7 — proto + 호출 의사코드
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : Python 호출 의사코드       │")
    print("└──────────────────────────────────────┘")
    code = r"""
# Server side
import grpc
from concurrent import futures
from orders.v1 import orders_pb2, orders_pb2_grpc

class OrderService(orders_pb2_grpc.OrderServiceServicer):
    def CreateOrder(self, request, context):
        # 인증 메타데이터 검사
        meta = dict(context.invocation_metadata())
        if meta.get('authorization') != 'Bearer demo':
            context.abort(grpc.StatusCode.UNAUTHENTICATED, 'invalid token')
        return orders_pb2.Order(id=42, user_id=request.user_id, amount=request.amount)

server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
orders_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(), server)
server.add_insecure_port('[::]:50051')
server.start(); server.wait_for_termination()

# Client side
channel = grpc.insecure_channel('localhost:50051')
stub = orders_pb2_grpc.OrderServiceStub(channel)
metadata = (('authorization', 'Bearer demo'),)
order = stub.CreateOrder(orders_pb2.CreateOrderRequest(user_id=10, amount=99.0),
                        timeout=2.0, metadata=metadata)
print(order.id, order.amount)
"""
    print(code)


# ─────────────────────────────────────────────────────────────────────────
# ■ 연습문제
# ─────────────────────────────────────────────────────────────────────────
#  Q1. Protobuf 필드 번호를 재사용하면 어떤 종류의 호환성 사고가 생기나?
#  Q2. gRPC 의 ‘server streaming’ 이 SSE(Server-Sent Events) 보다 강한 점 두 가지?
#  Q3. 마이크로서비스 간 mTLS 가 OAuth2 토큰만 사용하는 것보다 갖는 이점은?
#  Q4. UNAVAILABLE 과 DEADLINE_EXCEEDED 의 재시도 정책이 같지 않은 이유?
#  Q5. gRPC-Web 의 동작 원리(브라우저 ↔ 게이트웨이)를 한 줄로 설명하라.


if __name__ == "__main__":
    lesson1_why_grpc()
    lesson2_protobuf()
    lesson3_four_patterns()
    lesson4_auth_interceptor()
    lesson5_errors_deadline()
    lesson6_compare()
    lesson7_practice_proto_and_call()
