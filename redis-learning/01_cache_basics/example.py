class SimpleCache:
    def __init__(self):
        self.storage = {}
        self.expire_tick = {}

    def get(self, key, current_tick):
        # 만료 시간이 있고, 지금 시각이 그 시간을 넘었으면
        # 상자에 넣어 둔 쿠키가 유통기한이 지나 버린 것처럼 꺼내 버립니다.
        if key in self.expire_tick and current_tick >= self.expire_tick[key]:
            del self.storage[key]
            del self.expire_tick[key]
            return None

        return self.storage.get(key)

    def set(self, key, value, current_tick, ttl=None):
        self.storage[key] = value

        if ttl is None:
            self.expire_tick.pop(key, None)
        else:
            self.expire_tick[key] = current_tick + ttl


database_reads = 0


def read_menu_from_database(day_name):
    global database_reads
    database_reads += 1
    return f"{day_name} 급식: 비빔밥, 미역국, 우유"


def lesson1_cache_miss_then_hit():
    print("[레슨 1] 캐시에 없으면 원본 저장소를 읽고, 있으면 바로 꺼내기")
    print()

    cache = SimpleCache()
    current_tick = 1

    cached_menu = cache.get("menu:monday", current_tick)
    print("  첫 조회 결과:", cached_menu)

    if cached_menu is None:
        fresh_menu = read_menu_from_database("월요일")
        cache.set("menu:monday", fresh_menu, current_tick)
        print("  데이터베이스에서 읽어 캐시에 저장:", fresh_menu)

    cached_menu = cache.get("menu:monday", current_tick)
    print("  두 번째 조회 결과:", cached_menu)
    print("  데이터베이스 읽은 횟수:", database_reads)
    print()


def lesson2_expire_and_reload():
    print("[레슨 2] TTL이 지나면 다시 원본 저장소에서 읽기")
    print()

    cache = SimpleCache()
    current_tick = 5

    weather = "오늘의 날씨: 맑음"
    cache.set("weather:seoul", weather, current_tick, ttl=2)
    print("  tick=5 에 저장:", cache.get("weather:seoul", 5))
    print("  tick=6 에 조회:", cache.get("weather:seoul", 6))
    print("  tick=7 에 조회:", cache.get("weather:seoul", 7))
    print("  설명: ttl=2 이므로 5에서 저장한 값은 7이 되면 만료됩니다.")
    print()


def lesson3_real_use_case():
    print("[레슨 3] 캐시가 왜 빠른지 생활 비유로 이해하기")
    print()
    print("  자주 보는 책을 서랍 맨 앞에 두면 매번 책장 깊숙한 곳까지 가지 않아도 됩니다.")
    print("  캐시는 바로 그 '서랍 맨 앞자리'입니다.")
    print("  실사용 예시:")
    print("  - 메인 화면 인기 게시글")
    print("  - 오늘 환율")
    print("  - 로그인한 사용자 기본 정보")
    print("  자주 바뀌지 않지만 자주 읽는 데이터에 특히 잘 맞습니다.")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("Redis 01단계: 캐시 기본기")
    print("=" * 72)
    print()

    lesson1_cache_miss_then_hit()
    lesson2_expire_and_reload()
    lesson3_real_use_case()
