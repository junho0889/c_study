# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   gRPC 학습 06단계: 로드 밸런싱과 헬스 체크
#   ─ 클라이언트 로드 밸런싱, 서비스 디스커버리, 헬스 체크, 커넥션 관리 ─
#
#   서버가 1대뿐이면 그 서버가 죽으면 끝입니다!
#   여러 서버에 요청을 나눠 보내는 것이 로드 밸런싱입니다.
#
#   ■ 실행: python load_balance.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import random
import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict


# ─────────────────────────────────────────────────────────────────────
# ■ 서버 노드 정의
# ─────────────────────────────────────────────────────────────────────

@dataclass
class ServerNode:
    address: str
    port: int
    healthy: bool = True
    weight: int = 1         # 가중치 (성능 좋은 서버에 높은 값)
    active_connections: int = 0
    total_requests: int = 0

    @property
    def endpoint(self):
        return f"{self.address}:{self.port}"


def lesson1_why_load_balance():
    # =========================================================================
    #   레슨 1 — 왜 로드 밸런싱이 필요한가?
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 1 : 로드 밸런싱이 필요한 이유           │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 로드 밸런싱 = 여러 서버에 요청을 고르게 나누기
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     마트 계산대가 3개 있을 때:
    #     - 1번 계산대에만 줄을 서면? → 1번만 바쁘고 2, 3번은 놀고 있음!
    #     - 짧은 줄에 서면? → 모두 고르게 일하고 빨리 처리됨!
    #
    #     이것이 바로 로드 밸런싱입니다.
    #
    #   gRPC 로드 밸런싱 방식:
    #
    #     1. 서버 쪽 (Proxy LB):
    #        클라이언트 → [프록시(nginx 등)] → 서버1, 서버2, 서버3
    #
    #     2. 클라이언트 쪽 (Client-side LB):
    #        클라이언트가 직접 서버 목록을 알고 골라서 보냄
    #        gRPC는 이 방식을 기본으로 지원합니다!
    #

    print("  서버 1대일 때의 문제:")
    print("    - 서버가 죽으면 서비스 전체가 멈춤 (단일 장애점)")
    print("    - 사용자가 많아지면 서버가 감당 못 함")
    print()
    print("  로드 밸런싱 후:")
    print("    - 서버 1대가 죽어도 나머지가 처리 (고가용성)")
    print("    - 요청을 나눠서 처리 (확장성)")
    print()

    print("  ┌─────────┐")
    print("  │클라이언트│")
    print("  └────┬────┘")
    print("       │ 로드 밸런서가 분배")
    print("  ┌────┼──────────┐")
    print("  ↓    ↓          ↓")
    print("  서버1  서버2     서버3")
    print()


def lesson2_round_robin():
    # =========================================================================
    #   레슨 2 — Round Robin 방식
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 2 : Round Robin (순서대로 돌아가며)     │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Round Robin = "1번 → 2번 → 3번 → 1번 → ..." 반복
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     카드 게임에서 시계 방향으로 돌아가며 한 장씩 나누는 것!
    #     모든 서버가 비슷한 성능이면 가장 공평한 방식입니다.
    #

    class RoundRobinBalancer:
        def __init__(self, servers: List[ServerNode]):
            self.servers = servers
            self.index = 0

        def next_server(self) -> Optional[ServerNode]:
            healthy = [s for s in self.servers if s.healthy]
            if not healthy:
                return None
            server = healthy[self.index % len(healthy)]
            self.index += 1
            server.total_requests += 1
            return server

    servers = [
        ServerNode("서버A", 50051),
        ServerNode("서버B", 50052),
        ServerNode("서버C", 50053),
    ]

    balancer = RoundRobinBalancer(servers)

    print("  [Round Robin으로 10번 요청 분배]")
    for i in range(10):
        server = balancer.next_server()
        print(f"    요청 {i + 1:2d} → {server.endpoint}")
    print()

    print("  각 서버 요청 수:")
    for s in servers:
        print(f"    {s.endpoint}: {s.total_requests}번")
    print()


def lesson3_weighted_round_robin():
    # =========================================================================
    #   레슨 3 — 가중치 Round Robin
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 3 : 가중치 Round Robin                 │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 가중치 = 성능 좋은 서버에 더 많이 보내기
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     계산대 직원 중에 빠른 사람이 있으면
    #     그 사람에게 손님을 더 많이 보내는 것!
    #     CPU 8코어 서버에는 weight=3, 2코어 서버에는 weight=1
    #

    class WeightedRoundRobin:
        def __init__(self, servers: List[ServerNode]):
            self.servers = servers
            self.expanded = []
            for s in servers:
                self.expanded.extend([s] * s.weight)
            self.index = 0

        def next_server(self):
            healthy = [s for s in self.expanded if s.healthy]
            if not healthy:
                return None
            server = healthy[self.index % len(healthy)]
            self.index += 1
            server.total_requests += 1
            return server

    servers = [
        ServerNode("대형서버", 50051, weight=3),    # 성능 3배
        ServerNode("중형서버", 50052, weight=2),    # 성능 2배
        ServerNode("소형서버", 50053, weight=1),    # 기본
    ]

    balancer = WeightedRoundRobin(servers)

    print("  가중치: 대형=3, 중형=2, 소형=1")
    print()

    for i in range(12):
        server = balancer.next_server()
        print(f"    요청 {i + 1:2d} → {server.endpoint}")

    print()
    print("  결과:")
    for s in servers:
        print(f"    {s.endpoint} (가중치 {s.weight}): {s.total_requests}번")
    print()


def lesson4_health_check():
    # =========================================================================
    #   레슨 4 — 헬스 체크 프로토콜
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 4 : 헬스 체크 프로토콜                  │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 헬스 체크 = "이 서버 살아 있니?" 정기적으로 확인
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     학교에서 아침 출석 체크와 같습니다!
    #     매일 아침 "민수?" "네!" "지우?" "네!" "서연?" "..."
    #     대답이 없으면 결석 처리 → 그 서버에는 요청 안 보냄!
    #
    #   gRPC 헬스 체크 프로토콜:
    #     service Health {
    #       rpc Check(HealthCheckRequest) returns (HealthCheckResponse);
    #       rpc Watch(HealthCheckRequest) returns (stream HealthCheckResponse);
    #     }
    #
    #   상태 값:
    #     UNKNOWN     = 아직 확인 안 됨
    #     SERVING     = 정상 서비스 중
    #     NOT_SERVING = 서비스 중단 (점검 등)
    #

    class HealthChecker:
        def __init__(self, servers: List[ServerNode]):
            self.servers = servers
            self.check_count = 0

        def check_all(self):
            """모든 서버 헬스 체크"""
            self.check_count += 1
            results = {}
            for server in self.servers:
                # 시뮬레이션: 서버C는 3번째 체크부터 장애
                if server.address == "서버C" and self.check_count >= 3:
                    server.healthy = False
                    status = "NOT_SERVING"
                else:
                    status = "SERVING" if server.healthy else "NOT_SERVING"
                results[server.endpoint] = status
            return results

    servers = [
        ServerNode("서버A", 50051),
        ServerNode("서버B", 50052),
        ServerNode("서버C", 50053),
    ]

    checker = HealthChecker(servers)

    for round_num in range(1, 5):
        print(f"  [헬스 체크 #{round_num}]")
        results = checker.check_all()
        for endpoint, status in results.items():
            icon = "[O]" if status == "SERVING" else "[X]"
            print(f"    {icon} {endpoint}: {status}")
        print()

    print("  장애 감지 후:")
    healthy = [s for s in servers if s.healthy]
    print(f"    정상 서버: {[s.endpoint for s in healthy]}")
    print(f"    → 서버C에는 더 이상 요청을 보내지 않습니다!")
    print()


def lesson5_service_discovery():
    # =========================================================================
    #   레슨 5 — 서비스 디스커버리
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 5 : 서비스 디스커버리                  │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 서비스 디스커버리 = "서버가 어디 있는지 자동으로 찾기"
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     전화번호부와 같습니다!
    #     "피자 가게 번호가 뭐지?" → 전화번호부에서 찾기!
    #     "학생 서비스 주소가 뭐지?" → 서비스 레지스트리에서 찾기!
    #
    #   방식:
    #     1. DNS 기반: student-service.school.local → 10.0.0.1, 10.0.0.2
    #     2. 레지스트리 기반: Consul, etcd, ZooKeeper 등에 등록
    #     3. Kubernetes: 자동으로 서비스 디스커버리 제공
    #

    class ServiceRegistry:
        """간단한 서비스 레지스트리 시뮬레이션"""
        def __init__(self):
            self.services: Dict[str, List[ServerNode]] = {}

        def register(self, service_name, node):
            """서비스 등록"""
            if service_name not in self.services:
                self.services[service_name] = []
            self.services[service_name].append(node)
            print(f"    [등록] {service_name} → {node.endpoint}")

        def deregister(self, service_name, address):
            """서비스 해제"""
            if service_name in self.services:
                self.services[service_name] = [
                    s for s in self.services[service_name]
                    if s.address != address
                ]
                print(f"    [해제] {service_name} ← {address}")

        def discover(self, service_name):
            """서비스 주소 조회"""
            nodes = self.services.get(service_name, [])
            return [n for n in nodes if n.healthy]

    registry = ServiceRegistry()

    print("  [1단계] 서비스 등록")
    registry.register("student-service", ServerNode("10.0.0.1", 50051))
    registry.register("student-service", ServerNode("10.0.0.2", 50052))
    registry.register("score-service", ServerNode("10.0.1.1", 50060))
    print()

    print("  [2단계] 서비스 검색")
    student_nodes = registry.discover("student-service")
    print(f"    student-service 서버 목록:")
    for node in student_nodes:
        print(f"      → {node.endpoint}")
    print()

    print("  [3단계] 서버 축소 (스케일 다운)")
    registry.deregister("student-service", "10.0.0.2")
    student_nodes = registry.discover("student-service")
    print(f"    student-service 서버 목록 (갱신):")
    for node in student_nodes:
        print(f"      → {node.endpoint}")
    print()


def lesson6_keepalive():
    # =========================================================================
    #   레슨 6 — Keepalive와 커넥션 관리
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 6 : Keepalive와 커넥션 관리            │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Keepalive = "연결이 살아 있는지 주기적으로 확인"
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     전화 통화 중 "여보세요? 듣고 있나요?" 하고 확인하는 것!
    #     상대방이 대답 없으면 → 전화가 끊어졌다고 판단!
    #
    #   gRPC는 HTTP/2 기반이라 하나의 연결로 여러 요청을 보냅니다.
    #   연결을 계속 유지하므로, 살아 있는지 확인하는 것이 중요합니다.
    #

    keepalive_settings = {
        "keepalive_time_ms": 10000,       # 10초마다 핑 보내기
        "keepalive_timeout_ms": 5000,     # 5초 안에 응답 없으면 연결 끊김
        "keepalive_without_calls": False,  # 활성 요청이 없으면 핑 안 보냄
        "max_connection_idle_ms": 300000,  # 5분 동안 요청 없으면 연결 해제
        "max_connection_age_ms": 3600000,  # 1시간 후 연결 강제 갱신
    }

    print("  gRPC Keepalive 설정 예시:")
    descriptions = {
        "keepalive_time_ms": "핑 보내는 간격",
        "keepalive_timeout_ms": "핑 응답 대기 시간",
        "keepalive_without_calls": "유휴 상태에서도 핑 보낼지",
        "max_connection_idle_ms": "유휴 시 연결 해제까지 시간",
        "max_connection_age_ms": "연결 최대 수명",
    }

    for key, value in keepalive_settings.items():
        desc = descriptions.get(key, "")
        if isinstance(value, bool):
            display = "예" if value else "아니오"
        elif key.endswith("_ms"):
            display = f"{value}ms ({value / 1000:.0f}초)"
        else:
            display = str(value)
        print(f"    {key}")
        print(f"      = {display} ({desc})")
    print()

    print("  커넥션 관리 팁:")
    print("    1. keepalive 간격을 너무 짧게 하면 네트워크 부하")
    print("    2. 너무 길면 죽은 연결을 모르고 계속 쓸 수 있음")
    print("    3. max_connection_age로 연결을 주기적으로 갱신하면")
    print("       로드 밸런싱이 더 고르게 됩니다.")
    print("    4. 프록시/방화벽이 유휴 연결을 끊을 수 있으니 주의!")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("  gRPC 06단계 : 로드 밸런싱과 헬스 체크")
    print("=" * 72)
    print()

    lesson1_why_load_balance()
    lesson2_round_robin()
    lesson3_weighted_round_robin()
    lesson4_health_check()
    lesson5_service_discovery()
    lesson6_keepalive()
