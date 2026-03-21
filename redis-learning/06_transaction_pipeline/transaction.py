"""
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  Redis 06단계: 트랜잭션과 파이프라인                               ■
■  MULTI/EXEC, WATCH(낙관적 잠금), Pipeline, Lua 스크립팅 개념       ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
"""


class ToyRedisTransaction:
    """트랜잭션과 파이프라인을 흉내 내는 미니 Redis"""

    def __init__(self):
        self.data = {}
        self.watch_keys = {}       # WATCH 중인 키의 원래 값
        self.tx_queue = None       # MULTI 후 명령을 쌓아 두는 큐
        self.pipeline_queue = []   # 파이프라인 명령 큐

    def set(self, key, value):
        if self.tx_queue is not None:
            self.tx_queue.append(("SET", key, value))
            return "QUEUED"
        self.data[key] = value
        return "OK"

    def get(self, key):
        return self.data.get(key)

    def incrby(self, key, amount):
        if self.tx_queue is not None:
            self.tx_queue.append(("INCRBY", key, amount))
            return "QUEUED"
        self.data[key] = self.data.get(key, 0) + amount
        return self.data[key]

    # ── MULTI / EXEC ──
    def multi(self):
        """트랜잭션 시작: 이후 명령들은 바로 실행하지 않고 큐에 쌓는다."""
        self.tx_queue = []
        return "OK"

    def exec(self):
        """쌓아 둔 명령을 한 번에 실행한다. WATCH 위반 시 None 반환."""
        if self.tx_queue is None:
            return "ERR: MULTI가 호출되지 않았습니다"

        # WATCH 확인: 감시 중인 키가 바뀌었으면 트랜잭션 취소
        for key, original_value in self.watch_keys.items():
            if self.data.get(key) != original_value:
                self.tx_queue = None
                self.watch_keys = {}
                return None  # 실패!

        results = []
        for cmd in self.tx_queue:
            if cmd[0] == "SET":
                self.data[cmd[1]] = cmd[2]
                results.append("OK")
            elif cmd[0] == "INCRBY":
                self.data[cmd[1]] = self.data.get(cmd[1], 0) + cmd[2]
                results.append(self.data[cmd[1]])

        self.tx_queue = None
        self.watch_keys = {}
        return results

    def discard(self):
        """쌓아 둔 명령을 모두 버린다."""
        self.tx_queue = None
        return "OK"

    # ── WATCH ──
    def watch(self, *keys):
        """키를 감시한다. EXEC 전에 다른 곳에서 값이 바뀌면 트랜잭션 취소."""
        for k in keys:
            self.watch_keys[k] = self.data.get(k)

    # ── Pipeline (배치 전송) ──
    def pipeline_add(self, command, *args):
        self.pipeline_queue.append((command, args))

    def pipeline_execute(self):
        results = []
        for cmd, args in self.pipeline_queue:
            if cmd == "SET":
                self.data[args[0]] = args[1]
                results.append("OK")
            elif cmd == "GET":
                results.append(self.data.get(args[0]))
            elif cmd == "INCRBY":
                self.data[args[0]] = self.data.get(args[0], 0) + args[1]
                results.append(self.data[args[0]])
        self.pipeline_queue = []
        return results


# ── Lua 스크립트 시뮬레이션 ──
def lua_compare_and_set(redis_obj, key, expected, new_value):
    """
    Redis의 Lua 스크립팅을 흉내 낸 함수.
    서버 안에서 '읽기 + 비교 + 쓰기'를 한 번에 원자적으로 실행합니다.
    """
    current = redis_obj.data.get(key)
    if current == expected:
        redis_obj.data[key] = new_value
        return 1   # 성공
    return 0       # 실패


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 1: MULTI/EXEC - 은행 이체 예시                        │
# │  비유: 봉투에 편지를 여러 장 넣고 한꺼번에 보내기             │
# └─────────────────────────────────────────────────────────────┘
def lesson1_multi_exec():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 1: MULTI/EXEC - 은행 이체 예시                │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # MULTI/EXEC는 여러 명령을 '한 묶음'으로 실행합니다.
    # 봉투에 편지를 넣어 뒀다가 EXEC를 외치면 한꺼번에 전달되는 것처럼요.
    # 중간에 다른 명령이 끼어들 수 없어서 '원자적(atomic)'이라고 합니다.

    r = ToyRedisTransaction()
    r.data["account:민수"] = 10000
    r.data["account:지우"] = 5000
    print(f"  [이체 전] 민수: {r.data['account:민수']}원, 지우: {r.data['account:지우']}원")

    # 민수 -> 지우로 3000원 이체
    r.multi()
    r.incrby("account:민수", -3000)    # -> QUEUED
    r.incrby("account:지우", 3000)     # -> QUEUED
    results = r.exec()

    print(f"  EXEC 결과: {results}")
    print(f"  [이체 후] 민수: {r.data['account:민수']}원, 지우: {r.data['account:지우']}원")
    print("  -> 두 명령이 한 묶음으로 실행되어 돈이 사라지거나 복제되지 않습니다.")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 2: WATCH - 낙관적 잠금 (좌석 예매 예시)               │
# │  비유: 물건을 집었는데 계산 전에 누가 가격표를 바꿨다면 취소  │
# └─────────────────────────────────────────────────────────────┘
def lesson2_watch():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 2: WATCH - 낙관적 잠금 (좌석 예매)            │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # WATCH는 '이 키를 내가 보고 있을 테니, 누가 바꾸면 알려줘'라는 뜻입니다.
    # 마트에서 물건을 집었는데 계산 전에 누가 가격표를 바꿨다면,
    # '잠깐, 다시 확인할게요!'하고 계산을 취소하는 것과 같아요.
    # 이것을 '낙관적 잠금(Optimistic Locking)'이라고 합니다.

    r = ToyRedisTransaction()
    r.data["seat:A1"] = "available"

    # 사용자1이 좌석을 확인하고 예매 시도
    r.watch("seat:A1")
    print(f"  사용자1이 좌석 A1 확인: {r.data['seat:A1']}")

    # 그 사이 사용자2가 먼저 예매 완료! (WATCH 위반)
    r.data["seat:A1"] = "reserved_by_user2"
    print(f"  [끼어들기] 사용자2가 먼저 예매: {r.data['seat:A1']}")

    # 사용자1의 트랜잭션 실행 시도
    r.multi()
    r.set("seat:A1", "reserved_by_user1")
    result = r.exec()
    print(f"  사용자1 EXEC 결과: {result}")
    print(f"  좌석 상태: {r.data['seat:A1']}")
    print("  -> WATCH된 키가 중간에 바뀌었으므로 트랜잭션이 취소(None)되었습니다!")
    print("  -> 사용자1은 다시 시도해야 합니다. 이렇게 충돌을 안전하게 감지합니다.")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 3: Pipeline - 명령을 묶어서 한 번에 보내기             │
# │  비유: 택배를 하나씩 보내지 말고 박스에 모아 한 트럭에 싣기   │
# └─────────────────────────────────────────────────────────────┘
def lesson3_pipeline():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 3: Pipeline - 명령을 묶어서 한 번에 보내기     │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Pipeline은 여러 명령을 한 번의 네트워크 왕복에 보냅니다.
    # 택배를 하나씩 보내면 왕복 시간이 10번 걸리지만,
    # 박스에 모아 한 트럭에 실으면 왕복 1번이면 됩니다. 훨씬 빠르죠!
    # 주의: Pipeline은 원자적이지 않습니다 (중간에 다른 명령 끼어들 수 있음).

    r = ToyRedisTransaction()

    # 파이프라인 없이 하나씩 보내기 (느림)
    print("  [하나씩 보내기] 네트워크 왕복 5회:")
    for i in range(1, 6):
        r.set(f"key:{i}", f"value:{i}")
        print(f"    -> SET key:{i} 전송 & 응답 (왕복 {i}회)")

    # 파이프라인으로 묶어 보내기 (빠름)
    print("  [파이프라인] 네트워크 왕복 1회:")
    for i in range(6, 11):
        r.pipeline_add("SET", f"key:{i}", f"value:{i}")
    results = r.pipeline_execute()
    print(f"    -> 5개 명령 한 번에 전송, 결과: {results}")
    print("    -> 왕복 1회로 5개 명령 처리 완료!")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 4: Lua 스크립팅 - 서버에서 직접 로직 실행              │
# │  비유: 심부름 목록을 적어 보내면 현장에서 알아서 처리         │
# └─────────────────────────────────────────────────────────────┘
def lesson4_lua_scripting():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 4: Lua 스크립팅 - 서버에서 직접 로직 실행      │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Redis는 Lua라는 작은 프로그래밍 언어로 스크립트를 서버에 보낼 수 있습니다.
    # '읽기 -> 판단 -> 쓰기'를 서버 안에서 한 번에 하므로 원자적입니다.
    # 심부름 목록을 적어 보내면 현장에서 한꺼번에 알아서 처리하는 것과 같아요.

    r = ToyRedisTransaction()
    r.data["coupon:ABC"] = "unused"

    # 쿠폰을 '사용 안 됨'일 때만 '사용됨'으로 바꾸기
    result = lua_compare_and_set(r, "coupon:ABC", "unused", "used")
    print(f"  첫 번째 사용 시도: {'성공' if result else '실패'} (현재: {r.data['coupon:ABC']})")

    result = lua_compare_and_set(r, "coupon:ABC", "unused", "used")
    print(f"  두 번째 사용 시도: {'성공' if result else '실패'} (현재: {r.data['coupon:ABC']})")
    print("  -> 이미 'used'이므로 두 번째 시도는 실패합니다.")
    print("  -> 이런 '비교 후 교체(CAS)' 로직이 Lua 스크립팅의 대표 활용입니다.")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 5: 정리 - 트랜잭션 vs 파이프라인 vs Lua               │
# └─────────────────────────────────────────────────────────────┘
def lesson5_summary():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 5: 정리 - 트랜잭션 vs 파이프라인 vs Lua       │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    print("  ┌──────────────┬─────────────┬────────────┬────────────────┐")
    print("  │ 기능          │ 원자적?      │ 조건 분기? │ 주 용도         │")
    print("  ├──────────────┼─────────────┼────────────┼────────────────┤")
    print("  │ MULTI/EXEC   │ O           │ X          │ 간단한 묶음 실행 │")
    print("  │ Pipeline     │ X           │ X          │ 네트워크 최적화  │")
    print("  │ Lua Script   │ O           │ O          │ 복잡한 원자 로직 │")
    print("  └──────────────┴─────────────┴────────────┴────────────────┘")
    print()


def main():
    print("=" * 72)
    print("  Redis 06단계: 트랜잭션과 파이프라인")
    print("=" * 72)
    print()

    lesson1_multi_exec()
    lesson2_watch()
    lesson3_pipeline()
    lesson4_lua_scripting()
    lesson5_summary()


if __name__ == "__main__":
    main()
