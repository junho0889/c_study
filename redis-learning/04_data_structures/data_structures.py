"""
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  Redis 04단계: 핵심 자료구조 (String, List, Set, Sorted Set, Hash)     ■
■  실제 Redis가 제공하는 다섯 가지 자료형을 순수 파이썬으로 직접 만들어 봅니다. ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
"""


# ============================================================
#  Redis를 흉내 내는 작은 저장소
#  - 실제 Redis 서버 없이 자료구조 동작 원리를 직접 확인합니다.
# ============================================================
class ToyRedis:
    """순수 파이썬으로 만든 미니 Redis"""

    def __init__(self):
        self.store = {}          # 모든 키-값을 담는 딕셔너리

    # ── String 관련 ──
    def set(self, key, value):
        self.store[key] = str(value)

    def get(self, key):
        return self.store.get(key)

    def incr(self, key):
        val = int(self.store.get(key, "0")) + 1
        self.store[key] = str(val)
        return val

    # ── List 관련 ──
    def _ensure_list(self, key):
        if key not in self.store:
            self.store[key] = []

    def lpush(self, key, *values):
        self._ensure_list(key)
        for v in values:
            self.store[key].insert(0, v)
        return len(self.store[key])

    def rpush(self, key, *values):
        self._ensure_list(key)
        for v in values:
            self.store[key].append(v)
        return len(self.store[key])

    def lpop(self, key):
        lst = self.store.get(key, [])
        return lst.pop(0) if lst else None

    def rpop(self, key):
        lst = self.store.get(key, [])
        return lst.pop() if lst else None

    def lrange(self, key, start, stop):
        lst = self.store.get(key, [])
        return lst[start:stop + 1]

    # ── Set 관련 ──
    def _ensure_set(self, key):
        if key not in self.store:
            self.store[key] = set()

    def sadd(self, key, *members):
        self._ensure_set(key)
        before = len(self.store[key])
        self.store[key].update(members)
        return len(self.store[key]) - before

    def smembers(self, key):
        return self.store.get(key, set())

    def sinter(self, key1, key2):
        return self.store.get(key1, set()) & self.store.get(key2, set())

    def sunion(self, key1, key2):
        return self.store.get(key1, set()) | self.store.get(key2, set())

    # ── Sorted Set 관련 ──
    def zadd(self, key, mapping):
        """mapping = {member: score, ...}"""
        if key not in self.store:
            self.store[key] = {}
        self.store[key].update(mapping)

    def zrange(self, key, start, stop):
        data = self.store.get(key, {})
        sorted_items = sorted(data.items(), key=lambda x: x[1])
        return sorted_items[start:stop + 1]

    def zrangebyscore(self, key, min_score, max_score):
        data = self.store.get(key, {})
        return [(m, s) for m, s in sorted(data.items(), key=lambda x: x[1])
                if min_score <= s <= max_score]

    # ── Hash 관련 ──
    def hset(self, key, field, value):
        if key not in self.store:
            self.store[key] = {}
        self.store[key][field] = value

    def hget(self, key, field):
        return self.store.get(key, {}).get(field)

    def hgetall(self, key):
        return dict(self.store.get(key, {}))


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 1: String - 가장 기본적인 키-값 저장                   │
# │  비유: 사물함에 이름표를 붙이고 물건 하나를 넣는 것           │
# └─────────────────────────────────────────────────────────────┘
def lesson1_string():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 1: String - 가장 기본적인 키-값 저장           │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # String은 Redis에서 가장 간단한 자료형입니다.
    # 사물함 하나에 이름표(키)를 붙이고, 안에 물건(값) 하나를 넣는 느낌이에요.
    # 숫자를 넣으면 INCR로 1씩 올릴 수도 있어서 조회수, 좋아요 수에 딱 좋습니다.

    r = ToyRedis()

    # 기본 SET / GET
    r.set("greeting", "안녕하세요!")
    print(f"  SET greeting -> GET: {r.get('greeting')}")

    # INCR: 숫자 문자열을 1씩 올리기 (페이지 조회수 예시)
    r.set("page:home:views", "0")
    for _ in range(5):
        r.incr("page:home:views")
    print(f"  홈 페이지 조회수 5회 증가 -> {r.get('page:home:views')}")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 2: List - 순서가 있는 목록 (메시지 큐에 활용)          │
# │  비유: 양쪽이 열린 긴 상자 - 왼쪽/오른쪽 어디서든 넣고 빼기  │
# └─────────────────────────────────────────────────────────────┘
def lesson2_list():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 2: List - 순서가 있는 목록 (메시지 큐 활용)    │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Redis List는 양쪽이 열린 긴 상자와 같습니다.
    # LPUSH: 왼쪽(앞)에 넣기   RPUSH: 오른쪽(뒤)에 넣기
    # LPOP: 왼쪽에서 빼기      RPOP: 오른쪽에서 빼기
    # LPUSH + RPOP = FIFO 큐(먼저 넣은 것이 먼저 나옴)

    r = ToyRedis()

    # 메시지 큐 예시: 선생님이 숙제를 큐에 넣고, 학생이 하나씩 꺼냄
    r.rpush("homework_queue", "수학 3쪽", "국어 일기", "과학 실험")
    print(f"  큐 전체: {r.lrange('homework_queue', 0, -1)}")

    task = r.lpop("homework_queue")  # 앞에서 꺼냄 -> FIFO
    print(f"  LPOP으로 꺼낸 숙제: {task}")
    print(f"  남은 큐: {r.lrange('homework_queue', 0, -1)}")

    # 최근 알림 목록 예시: LPUSH로 최신을 앞에 넣고 LRANGE로 최근 N개만 조회
    r.lpush("notifications", "새 댓글", "좋아요", "팔로우")
    print(f"  최근 알림(최신순): {r.lrange('notifications', 0, 1)}")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 3: Set - 중복 없는 모임 (태그, 친구 목록)              │
# │  비유: 출석부 - 같은 이름은 두 번 적어도 한 번만 남음         │
# └─────────────────────────────────────────────────────────────┘
def lesson3_set():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 3: Set - 중복 없는 모임 (태그, 친구 목록)      │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Set은 출석부와 같습니다. 같은 이름을 두 번 써도 한 명으로 셉니다.
    # SADD: 멤버 추가   SMEMBERS: 전체 보기
    # SINTER: 교집합 (공통 친구)   SUNION: 합집합 (모든 친구)

    r = ToyRedis()

    # 태그 시스템 예시
    r.sadd("post:1:tags", "파이썬", "프로그래밍", "초보")
    r.sadd("post:1:tags", "파이썬")  # 중복 추가 -> 무시됨
    print(f"  게시글 1 태그: {sorted(r.smembers('post:1:tags'))}")

    # 공통 친구 찾기
    r.sadd("user:민수:friends", "지우", "서연", "하준")
    r.sadd("user:지우:friends", "서연", "도윤", "민수")

    common = r.sinter("user:민수:friends", "user:지우:friends")
    all_friends = r.sunion("user:민수:friends", "user:지우:friends")
    print(f"  민수와 지우의 공통 친구(SINTER): {sorted(common)}")
    print(f"  두 사람의 모든 친구(SUNION): {sorted(all_friends)}")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 4: Sorted Set - 점수가 있는 순위표 (리더보드)          │
# │  비유: 시험 점수 게시판 - 이름 옆에 점수가 써 있고 정렬됨     │
# └─────────────────────────────────────────────────────────────┘
def lesson4_sorted_set():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 4: Sorted Set - 점수 있는 순위표 (리더보드)    │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Sorted Set은 시험 점수 게시판과 같습니다.
    # 학생 이름(member)과 점수(score)를 함께 저장하면,
    # 항상 점수 순서대로 정렬된 상태를 유지합니다.
    # 게임 리더보드, 인기 순위에 아주 잘 맞습니다!

    r = ToyRedis()

    # 게임 리더보드
    r.zadd("leaderboard", {
        "민수": 1500,
        "지우": 2300,
        "서연": 1800,
        "하준": 3100,
        "도윤": 900,
    })

    print("  전체 순위 (점수 오름차순):")
    for rank, (player, score) in enumerate(r.zrange("leaderboard", 0, -1), 1):
        print(f"    {rank}위: {player} - {score}점")

    # 점수 범위로 검색 (1000~2000점 사이 플레이어)
    mid_tier = r.zrangebyscore("leaderboard", 1000, 2000)
    print(f"  1000~2000점 플레이어: {[(p, s) for p, s in mid_tier]}")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 5: Hash - 필드가 여러 개인 객체 (사용자 프로필)        │
# │  비유: 학생 카드 - 이름, 나이, 반 등 여러 칸이 있는 한 장     │
# └─────────────────────────────────────────────────────────────┘
def lesson5_hash():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 5: Hash - 필드가 여러 개인 객체 (사용자 프로필) │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Hash는 학생 카드와 같습니다.
    # 한 장의 카드(키) 안에 이름, 나이, 반 등 여러 칸(필드)이 있습니다.
    # HSET으로 칸을 채우고, HGET으로 한 칸만, HGETALL로 전체를 읽습니다.
    # 사용자 프로필, 상품 정보 등에 딱 맞습니다.

    r = ToyRedis()

    # 사용자 프로필 저장
    r.hset("user:1001", "name", "김민수")
    r.hset("user:1001", "age", "12")
    r.hset("user:1001", "class", "5학년 3반")
    r.hset("user:1001", "hobby", "축구")

    print(f"  이름만 조회(HGET): {r.hget('user:1001', 'name')}")
    print(f"  전체 프로필(HGETALL): {r.hgetall('user:1001')}")

    # 상품 정보 예시
    r.hset("product:A100", "name", "무선 이어폰")
    r.hset("product:A100", "price", "35000")
    r.hset("product:A100", "stock", "120")
    print(f"  상품 정보: {r.hgetall('product:A100')}")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 6: 실전 활용 정리 - 어떤 자료구조를 언제 쓸까?         │
# └─────────────────────────────────────────────────────────────┘
def lesson6_summary():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 6: 실전 활용 정리 - 어떤 자료구조를 언제 쓸까? │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    print("  ┌──────────────┬────────────────────────────────────┐")
    print("  │ 자료구조      │ 대표 활용 사례                     │")
    print("  ├──────────────┼────────────────────────────────────┤")
    print("  │ String       │ 캐시, 조회수, 세션 토큰             │")
    print("  │ List         │ 메시지 큐, 최근 알림, 채팅 기록     │")
    print("  │ Set          │ 태그, 좋아요 사용자, 공통 친구      │")
    print("  │ Sorted Set   │ 리더보드, 인기 검색어, 우선순위 큐  │")
    print("  │ Hash         │ 사용자 프로필, 상품 정보, 설정값    │")
    print("  └──────────────┴────────────────────────────────────┘")
    print()
    print("  팁: '이 데이터에 순서가 필요한가? 점수가 필요한가?'를")
    print("       먼저 생각하면 어떤 자료구조를 쓸지 자연스럽게 정해집니다.")
    print()


def main():
    print("=" * 72)
    print("  Redis 04단계: 핵심 자료구조")
    print("  (String, List, Set, Sorted Set, Hash)")
    print("=" * 72)
    print()

    lesson1_string()
    lesson2_list()
    lesson3_set()
    lesson4_sorted_set()
    lesson5_hash()
    lesson6_summary()


if __name__ == "__main__":
    main()
