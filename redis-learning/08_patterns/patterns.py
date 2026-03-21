"""
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  Redis 08단계: 실전 패턴                                         ■
■  Rate Limiter, 분산 락, 세션 스토어, 메시지 큐, 캐시 패턴         ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
"""

import time
import threading


# ============================================================
#  토이 Redis 저장소
# ============================================================
class ToyRedis:
    def __init__(self):
        self.data = {}
        self.expiry = {}  # key -> 만료 시각

    def set(self, key, value, ex=None):
        self.data[key] = value
        if ex:
            self.expiry[key] = time.time() + ex

    def get(self, key):
        if key in self.expiry and time.time() > self.expiry[key]:
            self.data.pop(key, None)
            self.expiry.pop(key, None)
            return None
        return self.data.get(key)

    def setnx(self, key, value, ex=None):
        """SET if Not eXists: 키가 없을 때만 저장 (분산 락의 핵심!)"""
        if key in self.data:
            if key in self.expiry and time.time() > self.expiry[key]:
                pass  # 만료됨 -> 새로 설정 가능
            else:
                return False
        self.data[key] = value
        if ex:
            self.expiry[key] = time.time() + ex
        return True

    def delete(self, key):
        self.data.pop(key, None)
        self.expiry.pop(key, None)

    def incr(self, key):
        val = int(self.data.get(key, 0)) + 1
        self.data[key] = val
        return val

    def rpush(self, key, value):
        if key not in self.data:
            self.data[key] = []
        self.data[key].append(value)

    def lpop(self, key):
        lst = self.data.get(key, [])
        return lst.pop(0) if lst else None

    def brpop(self, key, timeout=1):
        """BRPOP: 리스트가 비어 있으면 값이 들어올 때까지 대기 (블로킹)"""
        start = time.time()
        while time.time() - start < timeout:
            lst = self.data.get(key, [])
            if lst:
                return lst.pop()
            time.sleep(0.05)
        return None

    def hset(self, key, field, value):
        if key not in self.data:
            self.data[key] = {}
        self.data[key][field] = value

    def hgetall(self, key):
        return dict(self.data.get(key, {}))

    def exists(self, key):
        if key in self.expiry and time.time() > self.expiry[key]:
            self.data.pop(key, None)
            self.expiry.pop(key, None)
            return False
        return key in self.data


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 1: Rate Limiter (요청 속도 제한)                      │
# │  비유: 급식실에서 1분에 5명까지만 줄 세우기                   │
# └─────────────────────────────────────────────────────────────┘
def lesson1_rate_limiter():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 1: Rate Limiter - 요청 속도 제한              │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Rate Limiter는 '일정 시간 안에 몇 번까지만 허용'하는 장치입니다.
    # 급식실에서 1분에 5명까지만 줄 세우는 것과 같아요.
    # API 서버에서 악의적인 과도한 요청을 막을 때 씁니다.

    r = ToyRedis()

    def is_allowed(user_id, limit=5, window_seconds=10):
        """슬라이딩 윈도우 방식 속도 제한"""
        key = f"rate:{user_id}"
        current = r.get(key)

        if current is None:
            r.set(key, 1, ex=window_seconds)
            return True, 1

        count = int(current)
        if count < limit:
            r.data[key] = count + 1
            return True, count + 1
        return False, count

    print("  사용자 '민수'가 API를 반복 호출합니다 (제한: 5회/10초):")
    for i in range(1, 8):
        allowed, count = is_allowed("민수", limit=5)
        status = "허용" if allowed else "차단"
        print(f"    요청 #{i}: {status} (현재 {count}회)")
    print("  -> 6번째부터 차단! 악의적 요청을 막을 수 있습니다.")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 2: 분산 락 (Distributed Lock) - SETNX 활용            │
# │  비유: 화장실 문 잠금 - 누가 쓰고 있으면 다른 사람은 대기     │
# └─────────────────────────────────────────────────────────────┘
def lesson2_distributed_lock():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 2: 분산 락 - SETNX로 잠금 구현                │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 분산 락은 여러 서버가 동시에 같은 자원에 접근하지 못하게 막습니다.
    # 화장실 문 잠금과 같아요 - 안에 누가 있으면 밖에서 기다려야 합니다.
    # SETNX(Set if Not eXists)로 '잠금 키가 없을 때만 설정'하면 됩니다.

    r = ToyRedis()

    def acquire_lock(lock_name, owner, ttl=5):
        """잠금 획득 시도. 성공하면 True."""
        return r.setnx(f"lock:{lock_name}", owner, ex=ttl)

    def release_lock(lock_name, owner):
        """자기가 건 잠금만 해제 (다른 사람 잠금을 풀면 안 됨!)"""
        current_owner = r.get(f"lock:{lock_name}")
        if current_owner == owner:
            r.delete(f"lock:{lock_name}")
            return True
        return False

    # 서버 A가 잠금 획득
    result = acquire_lock("payment:1001", "서버A")
    print(f"  서버A 잠금 시도: {'성공' if result else '실패'}")

    # 서버 B가 같은 잠금 시도 -> 실패
    result = acquire_lock("payment:1001", "서버B")
    print(f"  서버B 잠금 시도: {'성공' if result else '실패'} (이미 서버A가 잡고 있음)")

    # 서버 A가 작업 완료 후 잠금 해제
    release_lock("payment:1001", "서버A")
    print("  서버A 잠금 해제")

    # 이제 서버 B가 잠금 획득 가능
    result = acquire_lock("payment:1001", "서버B")
    print(f"  서버B 재시도: {'성공' if result else '실패'}")
    print("  -> SETNX + TTL로 안전한 분산 잠금을 구현할 수 있습니다.")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 3: 세션 스토어 - 로그인 상태 저장                      │
# │  비유: 놀이공원 입장 팔찌 - 팔찌 번호로 누구인지 확인         │
# └─────────────────────────────────────────────────────────────┘
def lesson3_session_store():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 3: 세션 스토어 - 로그인 상태 저장              │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 웹사이트에 로그인하면 서버가 '세션'이라는 임시 정보를 만듭니다.
    # 놀이공원 팔찌와 같아요 - 팔찌 번호(세션 ID)로 누구인지 확인합니다.
    # Redis에 세션을 저장하면 여러 서버가 같은 세션을 공유할 수 있습니다.

    r = ToyRedis()

    def create_session(user_id, user_name, ttl=1800):
        session_id = f"sess_{user_id}_{int(time.time())}"
        r.hset(f"session:{session_id}", "user_id", user_id)
        r.hset(f"session:{session_id}", "user_name", user_name)
        r.hset(f"session:{session_id}", "login_time", time.strftime("%H:%M:%S"))
        r.expiry[f"session:{session_id}"] = time.time() + ttl
        return session_id

    def get_session(session_id):
        return r.hgetall(f"session:{session_id}")

    # 로그인 -> 세션 생성
    sid = create_session("user_1001", "김민수")
    print(f"  로그인 성공! 세션 ID: {sid}")
    print(f"  세션 내용: {get_session(sid)}")

    # 다른 페이지 요청 시 세션 확인
    session = get_session(sid)
    if session:
        print(f"  인증 확인: {session['user_name']}님 환영합니다!")
    print("  -> Redis 덕분에 서버1에서 로그인해도 서버2에서 세션을 확인할 수 있습니다.")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 4: 메시지 큐 (BRPOP) - 일감이 올 때까지 대기           │
# │  비유: 피자 가게에서 주문이 올 때까지 기다리는 요리사          │
# └─────────────────────────────────────────────────────────────┘
def lesson4_message_queue():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 4: 메시지 큐 (BRPOP) - 일감 대기              │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # BRPOP은 리스트에 값이 없으면 값이 들어올 때까지 기다리는 명령입니다.
    # 피자 가게 요리사가 주문이 올 때까지 기다리다가, 주문이 오면 바로 만드는 것과 같아요.
    # 폴링(계속 확인)보다 효율적이고, 전용 메시지 큐(RabbitMQ)보다 간단합니다.

    r = ToyRedis()

    # 생산자가 작업을 넣음
    tasks = ["이메일 발송", "썸네일 생성", "알림 푸시"]
    print("  [생산자] 작업을 큐에 넣습니다:")
    for task in tasks:
        r.rpush("task_queue", task)
        print(f"    + {task}")

    # 소비자가 하나씩 꺼내 처리
    print("  [소비자] 작업을 하나씩 꺼내 처리합니다:")
    while True:
        task = r.lpop("task_queue")
        if task is None:
            break
        print(f"    처리 완료: {task}")
    print("  -> 간단한 백그라운드 작업 처리에 Redis 리스트가 딱 맞습니다.")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 5: Cache-Aside 패턴 - 캐시에 없으면 DB에서 읽기       │
# │  비유: 서랍에 없으면 창고에서 가져와 서랍에 넣기              │
# └─────────────────────────────────────────────────────────────┘
def lesson5_cache_aside():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 5: Cache-Aside 패턴                           │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Cache-Aside는 가장 흔한 캐시 전략입니다.
    # 1) 캐시에서 찾기 (서랍 확인)
    # 2) 없으면 DB에서 읽기 (창고에서 가져오기)
    # 3) 캐시에 저장 (서랍에 넣기)
    # 다음 번에는 캐시에서 바로 꺼낼 수 있으므로 빠릅니다!

    cache = ToyRedis()
    database = {"product:1": "무선 이어폰 35000원", "product:2": "키보드 89000원"}
    db_reads = 0

    def get_product(product_id):
        nonlocal db_reads
        # 1단계: 캐시에서 찾기
        cached = cache.get(f"product:{product_id}")
        if cached:
            return cached, "캐시 HIT"

        # 2단계: DB에서 읽기
        db_reads += 1
        db_value = database.get(f"product:{product_id}")
        if db_value:
            # 3단계: 캐시에 저장 (TTL 60초)
            cache.set(f"product:{product_id}", db_value, ex=60)
        return db_value, "캐시 MISS -> DB 조회"

    val, src = get_product("1")
    print(f"  1차 조회: {val} ({src})")
    val, src = get_product("1")
    print(f"  2차 조회: {val} ({src})")
    print(f"  DB 읽기 횟수: {db_reads}회 (캐시 덕분에 1회만!)")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 6: Write-Through 캐시 - 쓸 때 캐시와 DB 동시 갱신     │
# │  비유: 서랍과 창고에 동시에 물건을 넣기                       │
# └─────────────────────────────────────────────────────────────┘
def lesson6_write_through():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 6: Write-Through 캐시                         │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Write-Through는 데이터를 쓸 때 캐시와 DB에 동시에 저장합니다.
    # 서랍(캐시)과 창고(DB)에 물건을 동시에 넣는 것과 같아요.
    # 캐시가 항상 최신이라 읽기가 항상 정확합니다!

    cache = ToyRedis()
    database = {}

    def write_through(key, value):
        # 캐시와 DB에 동시에 쓰기
        cache.set(key, value)
        database[key] = value
        return "OK"

    write_through("user:1001:name", "김민수")
    write_through("user:1001:point", "5000")

    print(f"  캐시: {cache.data}")
    print(f"  DB:   {database}")
    print(f"  읽기: {cache.get('user:1001:name')} (캐시에서 즉시 반환)")
    print()
    print("  ┌─────────────┬───────────────────────┬────────────────────────┐")
    print("  │ 패턴         │ Cache-Aside            │ Write-Through           │")
    print("  ├─────────────┼───────────────────────┼────────────────────────┤")
    print("  │ 쓰기 시      │ DB만 쓰고 캐시 무효화 │ 캐시 + DB 동시 쓰기     │")
    print("  │ 읽기 시      │ 캐시 미스면 DB 조회    │ 항상 캐시 히트           │")
    print("  │ 일관성       │ 일시적 불일치 가능     │ 항상 일치               │")
    print("  │ 쓰기 성능    │ 빠름 (DB만)           │ 느림 (캐시+DB)          │")
    print("  └─────────────┴───────────────────────┴────────────────────────┘")
    print()


def main():
    print("=" * 72)
    print("  Redis 08단계: 실전 패턴")
    print("=" * 72)
    print()

    lesson1_rate_limiter()
    lesson2_distributed_lock()
    lesson3_session_store()
    lesson4_message_queue()
    lesson5_cache_aside()
    lesson6_write_through()


if __name__ == "__main__":
    main()
