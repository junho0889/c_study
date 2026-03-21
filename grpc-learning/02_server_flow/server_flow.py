from dataclasses import dataclass


@dataclass
class HelloRequest:
    name: str
    class_name: str


@dataclass
class HelloReply:
    message: str
    accepted: bool


def say_hello(request: HelloRequest) -> HelloReply:
    # unary RPC는 "요청 1번, 응답 1번"인 가장 기본 형태입니다.
    # 학교 안내 데스크에 질문표 한 장을 내면 안내 문구 한 장을 돌려받는 모습과 비슷합니다.
    if not request.name.strip():
        return HelloReply(message="이름이 비어 있으면 안내 메시지를 만들 수 없습니다.", accepted=False)

    return HelloReply(
        message=f"{request.class_name}의 {request.name} 학생, 오늘도 학습 서버에 접속했습니다.",
        accepted=True,
    )


def lesson1_unary_rpc_flow():
    print("[레슨 1] 요청 한 번에 응답 한 번 받는 unary RPC")
    print()

    request = HelloRequest(name="민수", class_name="3학년 2반")
    reply = say_hello(request)
    print("  요청:", request)
    print("  응답:", reply)
    print()


def lesson2_validation_inside_server():
    print("[레슨 2] 서버는 요청을 그대로 믿지 않고 확인도 함")
    print()

    invalid_request = HelloRequest(name="   ", class_name="3학년 2반")
    reply = say_hello(invalid_request)
    print("  잘못된 요청:", invalid_request)
    print("  서버 응답:", reply)
    print("  설명: 서버는 '빈 이름' 같은 잘못된 값을 보고 거절할 수 있습니다.")
    print()


def lesson3_why_proto_contract_matters():
    print("[레슨 3] 왜 proto 계약서가 필요한가")
    print()
    print("  요청에는 name, class_name 이 있어야 하고 응답에는 message, accepted 가 있다고")
    print("  약속해 두면, 클라이언트와 서버가 같은 종이 설계도를 보고 일하게 됩니다.")
    print("  실사용 예시: 모바일 앱, 웹 서버, 관리자 도구가 모두 같은 gRPC 메서드를 호출할 수 있습니다.")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("gRPC 02단계: 서버의 기본 요청/응답 흐름")
    print("=" * 72)
    print()

    lesson1_unary_rpc_flow()
    lesson2_validation_inside_server()
    lesson3_why_proto_contract_matters()
