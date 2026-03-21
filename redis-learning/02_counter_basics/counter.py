class CounterStore:
    def __init__(self):
        self.data = {}

    def incr(self, key):
        # incr는 "현재 값 + 1"을 한 번에 처리하는 대표적인 카운터 연산입니다.
        # 출석 도장판에 도장 하나를 더 찍는다고 생각하면 쉽습니다.
        self.data[key] = self.data.get(key, 0) + 1
        return self.data[key]


def lesson1_visit_counter():
    print("[레슨 1] 방문 횟수처럼 1씩 올라가는 값 세기")
    print()

    store = CounterStore()
    for _ in range(3):
        print("  home 방문 수:", store.incr("home"))
    print()


def lesson2_multiple_keys():
    print("[레슨 2] 페이지별로 따로 카운트할 수 있음")
    print()

    store = CounterStore()
    print("  home 방문 수:", store.incr("home"))
    print("  about 방문 수:", store.incr("about"))
    print("  home 방문 수 다시:", store.incr("home"))
    print("  설명: key가 다르면 도장판도 따로 쓰는 것과 같습니다.")
    print()


def lesson3_real_use_case():
    print("[레슨 3] 실사용 예시")
    print()
    print("  - 게시글 조회 수")
    print("  - 좋아요 수")
    print("  - 오늘 로그인한 사람 수")
    print("  카운터는 숫자 하나만 빠르게 올리면 되는 문제에 특히 잘 맞습니다.")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("Redis 02단계: Counter 기본기")
    print("=" * 72)
    print()

    lesson1_visit_counter()
    lesson2_multiple_keys()
    lesson3_real_use_case()
