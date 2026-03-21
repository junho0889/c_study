"""
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  Redis 07단계: Sentinel과 Cluster                                ■
■  자동 장애 복구(Sentinel), 데이터 분산(Cluster), 해시 슬롯,       ■
■  복제(Replication), Master-Slave 개념                            ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
"""

import hashlib
import time
import random


# ============================================================
#  토이 구현: Redis 노드, Sentinel, Cluster
# ============================================================
class RedisNode:
    """Redis 서버 한 대를 흉내 내는 클래스"""

    def __init__(self, name, role="master"):
        self.name = name
        self.role = role         # "master" 또는 "slave"
        self.data = {}
        self.is_alive = True
        self.master = None       # slave일 때 연결된 master

    def set(self, key, value):
        if not self.is_alive:
            raise ConnectionError(f"{self.name}에 연결할 수 없습니다!")
        self.data[key] = value

    def get(self, key):
        if not self.is_alive:
            raise ConnectionError(f"{self.name}에 연결할 수 없습니다!")
        return self.data.get(key)

    def replicate_from(self, master_node):
        """master의 데이터를 통째로 복사해 온다 (초기 동기화)"""
        self.data = dict(master_node.data)
        self.master = master_node

    def __repr__(self):
        status = "살아있음" if self.is_alive else "죽음"
        return f"[{self.name}|{self.role}|{status}|데이터{len(self.data)}개]"


class RedisSentinel:
    """
    Redis Sentinel을 흉내 내는 감시자.
    비유: 학급 반장이 선생님(master)이 안 계시면 부반장(slave)을 대리로 세우는 것.
    """

    def __init__(self, master, slaves):
        self.master = master
        self.slaves = slaves
        self.check_interval = 1  # 초마다 확인

    def health_check(self):
        """master가 살아있는지 확인"""
        return self.master.is_alive

    def failover(self):
        """master가 죽었을 때 slave 중 하나를 새 master로 승격"""
        print(f"  [Sentinel] {self.master.name}이 응답하지 않습니다!")
        print(f"  [Sentinel] 장애 복구(failover)를 시작합니다...")

        # 살아있는 slave를 찾아 승격
        for slave in self.slaves:
            if slave.is_alive:
                slave.role = "master"
                old_master_name = self.master.name
                self.master = slave
                self.slaves = [s for s in self.slaves if s != slave]
                print(f"  [Sentinel] {slave.name}을 새 master로 승격했습니다!")
                print(f"  [Sentinel] 이전 master({old_master_name})가 복구되면 slave로 전환됩니다.")
                return True
        print("  [Sentinel] 승격할 수 있는 slave가 없습니다!")
        return False


def hash_slot(key):
    """
    Redis Cluster의 해시 슬롯 계산.
    실제로는 CRC16을 쓰지만 여기서는 간단히 해시값 % 16384를 사용합니다.
    Redis Cluster는 16384개의 슬롯을 여러 노드에 나눠 가집니다.
    """
    h = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return h % 16384


class RedisCluster:
    """
    Redis Cluster를 흉내 내는 클래스.
    비유: 교실을 3개 구역으로 나누고, 각 구역에 사물함 담당자를 두는 것.
    학생 이름(키)의 번호에 따라 어느 구역 담당인지가 정해집니다.
    """

    def __init__(self, nodes):
        self.nodes = nodes
        # 16384개 슬롯을 노드 수만큼 균등 분배
        slots_per_node = 16384 // len(nodes)
        self.slot_map = {}
        for i, node in enumerate(nodes):
            start = i * slots_per_node
            end = (i + 1) * slots_per_node if i < len(nodes) - 1 else 16384
            for s in range(start, end):
                self.slot_map[s] = node

    def get_node_for_key(self, key):
        slot = hash_slot(key)
        return self.slot_map[slot]

    def set(self, key, value):
        node = self.get_node_for_key(key)
        node.set(key, value)
        return node.name

    def get(self, key):
        node = self.get_node_for_key(key)
        return node.get(key), node.name


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 1: Master-Slave 복제 - 칠판 내용을 공책에 베끼기       │
# └─────────────────────────────────────────────────────────────┘
def lesson1_replication():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 1: Master-Slave 복제                          │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Master-Slave 복제는 선생님이 칠판에 쓴 내용을 학생들이 공책에 베끼는 것과 같습니다.
    # Master: 읽기 + 쓰기 담당 (선생님 칠판)
    # Slave: 읽기 전용 복사본 (학생 공책)
    # 이렇게 하면 읽기 요청을 여러 slave에 분산할 수 있어 빨라집니다.

    master = RedisNode("master-1", "master")
    slave1 = RedisNode("slave-1", "slave")
    slave2 = RedisNode("slave-2", "slave")

    # master에 데이터 쓰기
    master.set("name", "김민수")
    master.set("age", "12")
    print(f"  Master 데이터: {master.data}")

    # slave들이 master 데이터를 복제
    slave1.replicate_from(master)
    slave2.replicate_from(master)
    print(f"  Slave-1 데이터: {slave1.data}")
    print(f"  Slave-2 데이터: {slave2.data}")

    # 읽기 요청을 slave에 분산
    slaves = [slave1, slave2]
    chosen = random.choice(slaves)
    print(f"  읽기 요청 -> {chosen.name}에서 name={chosen.get('name')}")
    print("  -> Master에만 쓰고, 읽기는 여러 Slave로 분산하면 성능이 좋아집니다!")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 2: Sentinel - 반장이 선생님 부재를 감지하고 대리 세우기 │
# └─────────────────────────────────────────────────────────────┘
def lesson2_sentinel():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 2: Sentinel - 자동 장애 복구                  │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Sentinel은 교실의 반장과 같습니다.
    # 선생님(master)이 안 계시면 부반장(slave)을 대리 선생님으로 세웁니다.
    # 이것을 '자동 장애 복구(Automatic Failover)'라고 합니다.

    master = RedisNode("master-1", "master")
    slave1 = RedisNode("slave-1", "slave")
    slave2 = RedisNode("slave-2", "slave")

    master.set("score", "100")
    slave1.replicate_from(master)
    slave2.replicate_from(master)

    sentinel = RedisSentinel(master, [slave1, slave2])

    # 정상 상태 확인
    print(f"  정상 상태: master={sentinel.health_check()}")
    print(f"  현재 master: {sentinel.master}")

    # Master 장애 발생!
    master.is_alive = False
    print(f"\n  [장애 발생] master-1이 죽었습니다!")
    print(f"  건강 체크: {sentinel.health_check()}")

    # Sentinel이 감지하고 failover 실행
    sentinel.failover()
    print(f"  새 master: {sentinel.master}")
    print(f"  새 master에서 score 조회: {sentinel.master.get('score')}")
    print("  -> 데이터가 복제되어 있었으므로 새 master에서도 바로 사용 가능!")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 3: 해시 슬롯 - 사물함 번호로 담당 구역 정하기          │
# └─────────────────────────────────────────────────────────────┘
def lesson3_hash_slots():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 3: 해시 슬롯 - 사물함 번호로 담당 구역 정하기  │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Redis Cluster는 16384개의 '슬롯'이라는 칸을 가지고 있습니다.
    # 각 키는 해시 함수로 0~16383 사이 번호를 받고,
    # 그 번호가 어느 노드 담당인지에 따라 저장 위치가 결정됩니다.
    # 비유: 출석번호 1~10번은 1구역, 11~20번은 2구역 사물함을 쓰는 것!

    test_keys = ["user:민수", "user:지우", "user:서연", "order:1001", "product:A1"]
    print("  키 -> 해시 슬롯 매핑:")
    for key in test_keys:
        slot = hash_slot(key)
        print(f"    {key:20s} -> 슬롯 #{slot}")
    print("  -> 같은 키는 항상 같은 슬롯으로 가므로 어느 노드에 있는지 바로 알 수 있습니다.")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 4: Redis Cluster - 데이터를 여러 노드에 분산 저장      │
# │  비유: 교실 3구역에 각각 사물함 담당자를 두기                 │
# └─────────────────────────────────────────────────────────────┘
def lesson4_cluster():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 4: Redis Cluster - 데이터 분산 저장            │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # Cluster는 데이터를 여러 노드에 나누어 저장합니다.
    # 교실을 3개 구역으로 나누고 각 구역에 사물함 담당자를 두는 것과 같아요.
    # 학생이 많아지면(데이터가 커지면) 구역(노드)을 추가하면 됩니다!

    node_a = RedisNode("Node-A", "master")
    node_b = RedisNode("Node-B", "master")
    node_c = RedisNode("Node-C", "master")

    cluster = RedisCluster([node_a, node_b, node_c])

    # 여러 키를 저장하면 자동으로 다른 노드에 분산됨
    keys_to_store = {
        "user:민수": "학생1",
        "user:지우": "학생2",
        "user:서연": "학생3",
        "order:1001": "주문내역",
        "product:X1": "상품정보",
        "session:abc": "세션데이터",
    }

    print("  데이터 저장 (자동 분산):")
    for key, value in keys_to_store.items():
        target_node = cluster.set(key, value)
        print(f"    {key:20s} -> {target_node}")

    print()
    print("  데이터 조회:")
    for key in keys_to_store:
        value, node_name = cluster.get(key)
        print(f"    {key:20s} -> 값: {value}, 노드: {node_name}")

    # 각 노드에 저장된 데이터 수
    print()
    print("  노드별 데이터 분포:")
    for node in [node_a, node_b, node_c]:
        print(f"    {node.name}: {len(node.data)}개 - {list(node.data.keys())}")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 5: 정리 - Sentinel vs Cluster                         │
# └─────────────────────────────────────────────────────────────┘
def lesson5_summary():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 5: 정리 - Sentinel vs Cluster                 │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    print("  ┌────────────┬──────────────────────┬──────────────────────────┐")
    print("  │ 항목        │ Sentinel              │ Cluster                   │")
    print("  ├────────────┼──────────────────────┼──────────────────────────┤")
    print("  │ 목적        │ 자동 장애 복구(HA)    │ 데이터 분산(Sharding)      │")
    print("  │ 노드 구성   │ Master 1 + Slave N   │ Master N (각각 Slave 가능) │")
    print("  │ 데이터 위치 │ 모든 노드에 전체 복사 │ 슬롯별로 나눠 저장         │")
    print("  │ 확장성      │ 읽기만 분산 가능      │ 읽기 + 쓰기 모두 분산      │")
    print("  │ 비유        │ 반장이 대리 세우기    │ 교실을 구역으로 나누기      │")
    print("  └────────────┴──────────────────────┴──────────────────────────┘")
    print()
    print("  실전: 소규모 -> Sentinel, 대규모 -> Cluster를 주로 사용합니다.")
    print()


def main():
    print("=" * 72)
    print("  Redis 07단계: Sentinel과 Cluster")
    print("=" * 72)
    print()

    lesson1_replication()
    lesson2_sentinel()
    lesson3_hash_slots()
    lesson4_cluster()
    lesson5_summary()


if __name__ == "__main__":
    main()
