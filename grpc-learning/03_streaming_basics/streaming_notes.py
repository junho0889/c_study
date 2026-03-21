def server_streaming(student_names):
    for turn, name in enumerate(student_names, start=1):
        # 스트리밍은 결과를 한 번에 뭉쳐 보내지 않고
        # 준비되는 대로 한 장씩 넘겨주는 방식입니다.
        yield f"{turn}번째 알림: {name} 학생 차례입니다."


def client_streaming(scores):
    # client streaming은 반대로 클라이언트가 여러 조각을 보내고
    # 서버가 마지막에 한 번 정리해서 응답하는 그림입니다.
    total = sum(scores)
    average = total / len(scores)
    return {"count": len(scores), "average": average}


def lesson1_server_streaming():
    print("[레슨 1] 서버가 여러 번 나눠 보내는 server streaming")
    print()

    for message in server_streaming(["민수", "지우", "서연"]):
        print(" ", message)
    print()


def lesson2_client_streaming():
    print("[레슨 2] 클라이언트가 여러 조각을 보내고 마지막에 결과 받기")
    print()

    summary = client_streaming([80, 92, 75, 88])
    print("  보낸 점수 수:", summary["count"])
    print("  평균 점수:", f"{summary['average']:.1f}")
    print("  비유: 선생님이 시험지 여러 장을 다 받은 뒤 평균을 계산해서 알려 주는 모습입니다.")
    print()


def lesson3_why_streaming_is_useful():
    print("[레슨 3] 스트리밍이 특히 좋은 상황")
    print()
    print("  - 아주 긴 목록을 조금씩 보여 줄 때")
    print("  - 녹음, 센서, 채팅처럼 데이터가 계속 들어올 때")
    print("  - 전부 모일 때까지 기다리면 사용자가 너무 오래 기다리게 될 때")
    print("  핵심: '준비된 것부터 조금씩'이 스트리밍의 감각입니다.")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("gRPC 03단계: 스트리밍 기초")
    print("=" * 72)
    print()

    lesson1_server_streaming()
    lesson2_client_streaming()
    lesson3_why_streaming_is_useful()
