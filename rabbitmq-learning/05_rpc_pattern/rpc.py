"""
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  RabbitMQ 05단계: RPC 패턴                                      ■
■  요청-응답 패턴, correlation_id, reply_to 큐, 타임아웃 처리       ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
"""

import uuid
import time
import threading
from collections import deque


# ============================================================
#  토이 RPC 시스템
#  비유: 레스토랑 - 손님이 주문표에 테이블 번호(reply_to)와
#       주문번호(correlation_id)를 적어 주방에 넘기면,
#       주방이 요리해서 해당 테이블로 가져다 줍니다.
# ============================================================
class MessageBroker:
    """간단한 메시지 브로커"""

    def __init__(self):
        self.queues = {}

    def declare_queue(self, name):
        if name not in self.queues:
            self.queues[name] = deque()

    def publish(self, queue_name, message):
        self.declare_queue(queue_name)
        self.queues[queue_name].append(message)

    def consume(self, queue_name, timeout=2.0):
        self.declare_queue(queue_name)
        start = time.time()
        while time.time() - start < timeout:
            if self.queues[queue_name]:
                return self.queues[queue_name].popleft()
            time.sleep(0.01)
        return None


class RPCClient:
    """
    RPC 클라이언트: 요청을 보내고 응답을 기다리는 쪽.
    비유: 레스토랑 손님 - 주문표를 내고 음식이 오기를 기다립니다.
    """

    def __init__(self, broker, server_queue):
        self.broker = broker
        self.server_queue = server_queue
        # 응답을 받을 전용 큐 (테이블 번호와 같음)
        self.reply_queue = f"reply_{uuid.uuid4().hex[:8]}"
        self.broker.declare_queue(self.reply_queue)

    def call(self, request, timeout=2.0):
        """RPC 호출: 요청을 보내고 응답을 기다린다."""
        correlation_id = str(uuid.uuid4())[:8]

        message = {
            "body": request,
            "reply_to": self.reply_queue,       # 응답 보낼 큐
            "correlation_id": correlation_id,    # 요청-응답 매칭용 ID
        }

        self.broker.publish(self.server_queue, message)

        # 응답 대기
        start = time.time()
        while time.time() - start < timeout:
            response = self.broker.consume(self.reply_queue, timeout=0.1)
            if response and response.get("correlation_id") == correlation_id:
                return response["body"]
        return None  # 타임아웃


class RPCServer:
    """
    RPC 서버: 요청을 처리하고 응답을 보내는 쪽.
    비유: 레스토랑 주방 - 주문표를 받아 요리하고 테이블로 가져다 줍니다.
    """

    def __init__(self, broker, queue_name, handler):
        self.broker = broker
        self.queue_name = queue_name
        self.handler = handler
        self.broker.declare_queue(queue_name)

    def process_one(self):
        """요청 하나를 처리하고 응답을 보낸다."""
        message = self.broker.consume(self.queue_name, timeout=1.0)
        if message is None:
            return False

        # 요청 처리
        result = self.handler(message["body"])

        # 응답 보내기 (reply_to 큐로, correlation_id 포함)
        response = {
            "body": result,
            "correlation_id": message["correlation_id"],
        }
        self.broker.publish(message["reply_to"], response)
        return True


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 1: 기본 RPC 흐름 - 주문하고 음식 받기                  │
# │  비유: 레스토랑에서 주문표를 내고 음식을 기다리기              │
# └─────────────────────────────────────────────────────────────┘
def lesson1_basic_rpc():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 1: 기본 RPC 흐름                              │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # RPC(Remote Procedure Call)는 '원격 함수 호출'입니다.
    # 클라이언트가 서버에 함수 실행을 요청하고, 결과를 돌려받습니다.
    # 레스토랑에서 손님(클라이언트)이 주문표를 주방(서버)에 보내고,
    # 주방이 요리(처리)해서 테이블(reply_to 큐)로 가져다 주는 것과 같아요!

    broker = MessageBroker()

    def calculator(request):
        """서버 측 처리 함수"""
        a, op, b = request["a"], request["op"], request["b"]
        if op == "+":
            return {"result": a + b}
        elif op == "-":
            return {"result": a - b}
        elif op == "*":
            return {"result": a * b}
        return {"error": "지원하지 않는 연산"}

    server = RPCServer(broker, "calc_queue", calculator)
    client = RPCClient(broker, "calc_queue")

    # 요청 보내기 (비동기적으로 서버가 처리해야 하므로 스레드 사용)
    def run_server():
        for _ in range(3):
            server.process_one()

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    requests = [
        {"a": 10, "op": "+", "b": 20},
        {"a": 100, "op": "-", "b": 37},
        {"a": 7, "op": "*", "b": 8},
    ]

    for req in requests:
        response = client.call(req)
        print(f"  요청: {req['a']} {req['op']} {req['b']} = {response}")

    server_thread.join(timeout=3)
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 2: correlation_id - 어떤 요청의 응답인지 매칭          │
# │  비유: 주문번호로 '이 음식이 3번 테이블 것'이라고 확인하기    │
# └─────────────────────────────────────────────────────────────┘
def lesson2_correlation_id():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 2: correlation_id - 요청-응답 매칭             │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 여러 요청을 보내면 응답이 순서대로 오지 않을 수 있습니다.
    # correlation_id는 '이 응답이 어떤 요청에 대한 것인지' 매칭하는 표식입니다.
    # 주문번호로 '이 음식이 3번 테이블의 두 번째 주문'이라고 확인하는 것과 같아요!

    broker = MessageBroker()

    # correlation_id가 어떻게 매칭되는지 수동으로 보여주기
    reply_queue = "reply_demo"
    broker.declare_queue(reply_queue)

    # 요청 3개를 보냄
    requests_sent = {}
    for i, order in enumerate(["김치찌개", "된장찌개", "순두부찌개"]):
        cid = f"order_{i + 1:03d}"
        requests_sent[cid] = order
        broker.publish("kitchen", {
            "body": order,
            "reply_to": reply_queue,
            "correlation_id": cid,
        })
        print(f"  [요청] correlation_id={cid}, 주문={order}")

    # 서버가 역순으로 응답 (순서가 바뀔 수 있음을 보여줌)
    kitchen_msgs = []
    while True:
        msg = broker.consume("kitchen", timeout=0.1)
        if msg is None:
            break
        kitchen_msgs.append(msg)

    print()
    for msg in reversed(kitchen_msgs):
        broker.publish(msg["reply_to"], {
            "body": f"{msg['body']} 완성!",
            "correlation_id": msg["correlation_id"],
        })

    # 클라이언트가 응답을 받고 매칭
    print("  [응답] (역순으로 도착):")
    for _ in range(3):
        response = broker.consume(reply_queue, timeout=1)
        if response:
            original = requests_sent[response["correlation_id"]]
            print(f"    correlation_id={response['correlation_id']}, "
                  f"원래 주문={original}, 응답={response['body']}")
    print("  -> correlation_id 덕분에 순서가 바뀌어도 정확히 매칭됩니다!")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 3: 타임아웃 처리 - 응답이 안 오면?                     │
# │  비유: 주방이 30분 넘게 안 가져다주면 취소하기                │
# └─────────────────────────────────────────────────────────────┘
def lesson3_timeout():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 3: 타임아웃 처리                              │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 서버가 죽었거나 너무 오래 걸리면 클라이언트가 영원히 기다릴 수 없습니다.
    # 정해진 시간(타임아웃) 안에 응답이 안 오면 포기하고 에러를 반환합니다.
    # 레스토랑에서 30분 넘게 안 나오면 '주문 취소할게요' 하는 것과 같아요!

    broker = MessageBroker()
    client = RPCClient(broker, "slow_server")

    # 서버를 안 만들어서 응답이 안 옴
    print("  서버 없이 요청 보내기 (타임아웃 1초):")
    start = time.time()
    result = client.call({"action": "무한대기테스트"}, timeout=1.0)
    elapsed = time.time() - start
    print(f"  결과: {result}")
    print(f"  소요 시간: {elapsed:.1f}초")
    print("  -> None이 반환되었습니다. 타임아웃 덕분에 무한 대기를 방지합니다!")
    print()
    print("  타임아웃 처리 전략:")
    print("    1) 적절한 타임아웃 설정 (서비스 응답 시간 고려)")
    print("    2) 타임아웃 시 재시도 (최대 N회)")
    print("    3) 재시도 실패 시 폴백(fallback) 응답 반환")
    print("    4) 서킷 브레이커로 반복 실패 방지")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 4: 실전 예시 - 식당 주문 시스템                        │
# └─────────────────────────────────────────────────────────────┘
def lesson4_restaurant_system():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 4: 실전 예시 - 식당 주문 시스템                │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    broker = MessageBroker()

    # 메뉴와 가격
    menu = {
        "비빔밥": 8000,
        "김치찌개": 7000,
        "돈까스": 9000,
        "냉면": 8500,
    }

    def kitchen_handler(order):
        """주방 처리 로직"""
        item = order.get("item")
        qty = order.get("qty", 1)

        if item not in menu:
            return {"status": "error", "message": f"'{item}'은 메뉴에 없습니다"}

        price = menu[item] * qty
        return {
            "status": "success",
            "item": item,
            "qty": qty,
            "total": price,
            "message": f"{item} {qty}인분 준비 완료! 총 {price:,}원",
        }

    server = RPCServer(broker, "order_queue", kitchen_handler)
    client = RPCClient(broker, "order_queue")

    def run_kitchen():
        for _ in range(4):
            server.process_one()

    kitchen_thread = threading.Thread(target=run_kitchen, daemon=True)
    kitchen_thread.start()

    # 주문하기
    orders = [
        {"item": "비빔밥", "qty": 2},
        {"item": "김치찌개", "qty": 1},
        {"item": "스파게티", "qty": 1},     # 메뉴에 없음!
        {"item": "돈까스", "qty": 3},
    ]

    print("  주문 처리:")
    for order in orders:
        response = client.call(order, timeout=2)
        if response:
            status = response.get("status")
            if status == "success":
                print(f"    [성공] {response['message']}")
            else:
                print(f"    [실패] {response['message']}")
        else:
            print(f"    [타임아웃] {order}")

    kitchen_thread.join(timeout=3)
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 5: RPC 흐름 정리                                      │
# └─────────────────────────────────────────────────────────────┘
def lesson5_summary():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 5: RPC 흐름 정리                              │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    print("  RPC 메시지 흐름:")
    print()
    print("    클라이언트                       서버(주방)")
    print("    ─────────                       ────────")
    print("    1. 요청 메시지 생성")
    print("       - body: 요청 내용")
    print("       - reply_to: 응답 받을 큐")
    print("       - correlation_id: 매칭 ID")
    print("              │")
    print("              v")
    print("         [요청 큐]  ─────────────>  2. 요청 수신")
    print("                                    3. 처리(요리)")
    print("              <──────────────────   4. 응답 전송")
    print("         [reply_to 큐]                 (correlation_id 포함)")
    print("              │")
    print("              v")
    print("    5. correlation_id로 매칭")
    print("    6. 결과 사용")
    print()
    print("  주의사항:")
    print("    - RPC는 동기적이라 서버 장애 시 클라이언트도 멈출 수 있음")
    print("    - 반드시 타임아웃 설정 필요")
    print("    - 가능하면 비동기 메시징이 더 좋은 경우가 많음")
    print()


def main():
    print("=" * 72)
    print("  RabbitMQ 05단계: RPC 패턴")
    print("=" * 72)
    print()

    lesson1_basic_rpc()
    lesson2_correlation_id()
    lesson3_timeout()
    lesson4_restaurant_system()
    lesson5_summary()


if __name__ == "__main__":
    main()
