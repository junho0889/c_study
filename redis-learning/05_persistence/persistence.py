"""
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  Redis 05단계: 영속성 (Persistence) - RDB 스냅샷과 AOF          ■
■  메모리에 있는 데이터를 디스크에 저장해 서버가 꺼져도 복구하는 법 ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
"""

import json
import os
import time

# 임시 파일 경로 (실습용)
RDB_FILE = "_toy_rdb_snapshot.json"
AOF_FILE = "_toy_aof_log.txt"


class ToyRedisWithPersistence:
    """RDB 스냅샷과 AOF를 흉내 내는 미니 Redis"""

    def __init__(self):
        self.data = {}
        self.aof_log = []     # AOF: 실행한 명령을 순서대로 기록

    def set(self, key, value):
        self.data[key] = value
        self.aof_log.append(f"SET {key} {value}")

    def get(self, key):
        return self.data.get(key)

    def delete(self, key):
        if key in self.data:
            del self.data[key]
            self.aof_log.append(f"DEL {key}")

    # ── RDB: 현재 상태를 한 번에 사진 찍듯이 파일로 저장 ──
    def save_rdb(self, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def load_rdb(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    # ── AOF: 명령 기록을 줄 단위로 파일에 덧붙이기 ──
    def save_aof(self, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            for cmd in self.aof_log:
                f.write(cmd + "\n")

    def replay_aof(self, filepath):
        """AOF 파일을 한 줄씩 읽어 명령을 다시 실행해 상태를 복원한다."""
        self.data = {}
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(" ", 2)
                if parts[0] == "SET":
                    self.data[parts[1]] = parts[2]
                elif parts[0] == "DEL":
                    self.data.pop(parts[1], None)


def _cleanup():
    for f in [RDB_FILE, AOF_FILE]:
        if os.path.exists(f):
            os.remove(f)


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 1: RDB 스냅샷 - 정해진 시간마다 사진 찍기              │
# │  비유: 칠판에 적은 내용을 매 쉬는 시간마다 사진 찍어 두기      │
# └─────────────────────────────────────────────────────────────┘
def lesson1_rdb_snapshot():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 1: RDB 스냅샷 - 정해진 시간마다 사진 찍기      │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # RDB는 Redis의 '스냅샷' 방식입니다.
    # 칠판에 적은 모든 내용을 쉬는 시간마다 사진 찍어 두는 것과 같아요.
    # 장점: 복원이 빠르고, 파일 크기가 작습니다.
    # 단점: 사진을 찍기 전에 정전이 나면 마지막 사진 이후 내용은 사라집니다.

    r = ToyRedisWithPersistence()
    r.set("score:민수", "95")
    r.set("score:지우", "88")
    r.set("score:서연", "100")

    # 스냅샷 저장
    r.save_rdb(RDB_FILE)
    print("  [저장] RDB 스냅샷을 파일에 기록했습니다.")

    # 서버가 꺼진 상황을 흉내 - 새 인스턴스 생성
    r2 = ToyRedisWithPersistence()
    print(f"  [복구 전] r2 데이터: {r2.data}")
    r2.load_rdb(RDB_FILE)
    print(f"  [복구 후] r2 데이터: {r2.data}")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 2: AOF (Append-Only File) - 모든 명령을 일기처럼 기록  │
# │  비유: 수업 시간에 선생님이 하신 말씀을 빠짐없이 받아 적기    │
# └─────────────────────────────────────────────────────────────┘
def lesson2_aof():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 2: AOF - 모든 명령을 일기처럼 기록             │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # AOF는 '이 다음에 이거 했다, 저거 했다'를 시간 순서대로 기록합니다.
    # 수업 시간에 선생님 말씀을 노트에 빠짐없이 받아 적는 것과 같아요.
    # 장점: 명령 하나도 빠뜨리지 않아 데이터 손실이 거의 없습니다.
    # 단점: 파일이 점점 커지고, 복원 시 처음부터 다시 실행해야 해서 느릴 수 있습니다.

    r = ToyRedisWithPersistence()
    r.set("item:1", "연필")
    r.set("item:2", "지우개")
    r.set("item:3", "자")
    r.delete("item:2")        # 지우개는 나중에 삭제

    # AOF 파일 저장
    r.save_aof(AOF_FILE)
    print("  [AOF 기록 내용]")
    for cmd in r.aof_log:
        print(f"    {cmd}")

    # 복구: AOF를 처음부터 다시 재생(replay)
    r3 = ToyRedisWithPersistence()
    r3.replay_aof(AOF_FILE)
    print(f"  [AOF 복구 결과] {r3.data}")
    print("  -> item:2(지우개)는 DEL 명령이 있어서 복구 결과에 없습니다.")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 3: RDB vs AOF 비교                                    │
# └─────────────────────────────────────────────────────────────┘
def lesson3_comparison():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 3: RDB vs AOF 비교                            │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    print("  ┌────────────┬──────────────────┬──────────────────────┐")
    print("  │ 항목        │ RDB (스냅샷)      │ AOF (명령 기록)       │")
    print("  ├────────────┼──────────────────┼──────────────────────┤")
    print("  │ 저장 방식   │ 전체 사진 찍기    │ 명령 하나씩 기록       │")
    print("  │ 복구 속도   │ 빠름 (파일 로드)  │ 느림 (명령 재실행)     │")
    print("  │ 데이터 손실 │ 마지막 사진 이후  │ 거의 없음 (1초 이내)   │")
    print("  │ 파일 크기   │ 작음             │ 큼 (명령이 쌓이므로)   │")
    print("  │ 사용 예     │ 백업·재해 복구    │ 데이터 무손실 필요     │")
    print("  └────────────┴──────────────────┴──────────────────────┘")
    print()
    print("  실전 팁: Redis 공식 권장은 'RDB + AOF 모두 켜기'입니다.")
    print("  AOF로 거의 무손실을 보장하고, RDB로 빠르게 백업·복원합니다.")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 4: 백업 전략 시뮬레이션                                │
# └─────────────────────────────────────────────────────────────┘
def lesson4_backup_strategy():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 4: 백업 전략 시뮬레이션                        │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 실제 운영에서는 이런 식으로 주기적 백업을 합니다:
    # 1) 매 N초마다 RDB 스냅샷
    # 2) 매 명령마다 AOF 기록
    # 3) 스냅샷 파일을 다른 서버로 복사 (원격 백업)

    r = ToyRedisWithPersistence()

    # 시간이 흐르며 데이터가 쌓이는 상황 시뮬레이션
    snapshots_taken = 0
    for tick in range(1, 11):
        r.set(f"sensor:{tick}", f"온도={20 + tick}")
        # 매 5틱마다 RDB 스냅샷
        if tick % 5 == 0:
            r.save_rdb(RDB_FILE)
            snapshots_taken += 1
            print(f"  tick={tick}: RDB 스냅샷 #{snapshots_taken} 저장 (데이터 {len(r.data)}개)")

    # AOF도 저장
    r.save_aof(AOF_FILE)
    print(f"  AOF 로그: 총 {len(r.aof_log)}개 명령 기록")

    # 장애 발생! 마지막 RDB로 복구해 보기
    r_recovered = ToyRedisWithPersistence()
    r_recovered.load_rdb(RDB_FILE)
    print(f"  RDB로만 복구하면: {len(r_recovered.data)}개 데이터 (최대 5틱 손실 가능)")

    # AOF로 복구하면 전부 돌아옴
    r_full = ToyRedisWithPersistence()
    r_full.replay_aof(AOF_FILE)
    print(f"  AOF로 복구하면: {len(r_full.data)}개 데이터 (손실 없음)")
    print()


def main():
    print("=" * 72)
    print("  Redis 05단계: 영속성 (Persistence) - RDB 스냅샷과 AOF")
    print("=" * 72)
    print()

    try:
        lesson1_rdb_snapshot()
        lesson2_aof()
        lesson3_comparison()
        lesson4_backup_strategy()
    finally:
        _cleanup()


if __name__ == "__main__":
    main()
