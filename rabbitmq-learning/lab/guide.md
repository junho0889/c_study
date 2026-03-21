# ■■■ RabbitMQ 실습 가이드 ■■■

## 목차
1. [RabbitMQ 아키텍처](#1-rabbitmq-아키텍처)
2. [실행 방법](#2-실행-방법)
3. [Management UI 사용법](#3-management-ui-사용법)
4. [Exchange 종류별 비교표](#4-exchange-종류별-비교표)
5. [rabbitmqctl 명령어 총정리](#5-rabbitmqctl-명령어-총정리)
6. [클러스터링 설정 가이드](#6-클러스터링-설정-가이드)
7. [모니터링과 알림 설정](#7-모니터링과-알림-설정)
8. [프로덕션 체크리스트](#8-프로덕션-체크리스트)

---

## 1. RabbitMQ 아키텍처

### 메시지 흐름 다이어그램
```
  Producer                    RabbitMQ Broker                     Consumer
  ┌──────┐                   ┌─────────────────────────────┐     ┌──────┐
  │      │                   │                             │     │      │
  │      │ ─── publish ────► │  ┌──────────┐               │     │      │
  │      │                   │  │ Exchange │               │     │      │
  │      │                   │  └────┬─────┘               │     │      │
  │      │                   │       │ routing              │     │      │
  │      │                   │       │ (binding rules)      │     │      │
  │      │                   │       ▼                      │     │      │
  │      │                   │  ┌──────────┐               │     │      │
  │      │                   │  │  Queue   │ ── deliver ──►│     │      │
  │      │                   │  └──────────┘               │     │      │
  │      │                   │                    ◄── ack ──│     │      │
  │      │                   │                             │     │      │
  └──────┘                   └─────────────────────────────┘     └──────┘
```

### 핵심 구성 요소
```
  ┌─────────────────────────────────────────────────────────────┐
  │                      RabbitMQ Broker                         │
  │                                                             │
  │  ┌───────────┐    Binding     ┌───────────┐                │
  │  │           │  (라우팅 규칙)  │           │                │
  │  │ Exchange  │ ──────────────► │   Queue   │ → Consumer    │
  │  │           │    routing_key  │           │                │
  │  └───────────┘                └───────────┘                │
  │                                                             │
  │  Exchange 종류:                Queue 속성:                   │
  │  ├─ Direct  (정확 매칭)        ├─ durable (영속)            │
  │  ├─ Topic   (패턴 매칭)        ├─ exclusive (독점)          │
  │  ├─ Fanout  (브로드캐스트)     ├─ auto_delete (자동삭제)    │
  │  └─ Headers (헤더 매칭)        └─ arguments (추가설정)      │
  └─────────────────────────────────────────────────────────────┘
```

### Exchange 라우팅 비교
```
  ■ Direct Exchange
  Producer ──[routing_key="error"]──► Exchange ──► Queue(binding="error")
                                                ╳  Queue(binding="info")

  ■ Topic Exchange
  Producer ──[routing_key="log.error.auth"]──► Exchange
    ──► Queue(binding="log.error.*")  ✓ 매칭
    ──► Queue(binding="log.#")        ✓ 매칭
    ──► Queue(binding="log.info.*")   ╳ 불일치

  ■ Fanout Exchange
  Producer ──[routing_key="무시됨"]──► Exchange
    ──► Queue A  ✓ (모든 바인딩된 큐)
    ──► Queue B  ✓ (모든 바인딩된 큐)
    ──► Queue C  ✓ (모든 바인딩된 큐)
```

### 메시지 확인(ACK) 흐름
```
  Consumer                    Broker
  ┌──────┐                   ┌──────┐
  │      │ ◄── deliver ────  │Queue │  메시지 전달 (unacked 상태)
  │      │                   │      │
  │ 처리 │                   │ 대기 │  처리 완료까지 대기
  │      │                   │      │
  │      │ ─── basic_ack ──► │ 삭제 │  ACK → 큐에서 메시지 삭제
  │      │                   │      │
  │ 실패 │ ─── basic_nack ─► │ 재입력│  NACK(requeue=true) → 재처리
  │      │                   │      │
  │ 거부 │ ─── basic_reject► │ DLQ  │  REJECT(requeue=false) → DLQ
  └──────┘                   └──────┘
```

---

## 2. 실행 방법

### Step 1: Docker Compose로 RabbitMQ 시작
```bash
cd rabbitmq-learning/lab

# 서비스 시작
docker-compose up -d

# 상태 확인
docker-compose ps

# 로그 확인 (부팅 완료까지 약 15-30초)
docker-compose logs -f rabbitmq
```

### Step 2: Management UI 접속 확인
```
웹 브라우저: http://localhost:15672
아이디: admin
비밀번호: admin1234
```

### Step 3: Python 환경 준비
```bash
pip install pika
```

### Step 4: Producer 실행
```bash
# 모든 Exchange 타입으로 메시지 발행
python producer.py
```

### Step 5: Consumer 실행
```bash
# 터미널 1: 주문 큐 소비
python consumer.py order

# 터미널 2: 에러 로그 큐 소비
python consumer.py log-error

# 터미널 3: 전체 로그 큐 소비
python consumer.py log-all

# 터미널 4: 알림 큐 소비
python consumer.py notification
```

### Step 6: 종료
```bash
docker-compose down      # 컨테이너 삭제
docker-compose down -v   # 컨테이너 + 데이터 삭제
```

---

## 3. Management UI 사용법

### 접속 정보
- URL: http://localhost:15672
- 계정: admin / admin1234

### 주요 탭 설명

| 탭 | 기능 |
|-----|------|
| **Overview** | 전체 개요 (메시지 Rate, 연결 수, 노드 상태) |
| **Connections** | 활성 TCP 연결 목록 (프로듀서/컨슈머 연결) |
| **Channels** | 활성 채널 목록 (채널별 메시지 Rate) |
| **Exchanges** | Exchange 목록 및 바인딩 관리 |
| **Queues** | 큐 목록, 메시지 수, 소비 상태, 메시지 조회 |
| **Admin** | 사용자/VHost/정책/제한 관리 |

### 큐 상태 모니터링 (Queues 탭)

| 지표 | 설명 |
|------|------|
| **Ready** | 소비 대기 중인 메시지 수 |
| **Unacked** | 전달됐지만 ACK 안 된 메시지 수 |
| **Total** | Ready + Unacked |
| **Publish rate** | 초당 발행 메시지 수 |
| **Deliver rate** | 초당 전달 메시지 수 |
| **Ack rate** | 초당 ACK 수 |

### 메시지 조회 (큐 상세 → Get messages)
```
1. Queues 탭 → 큐 이름 클릭
2. "Get messages" 섹션 찾기
3. "Ack mode" 선택:
   - Nack message requeue true: 조회만 하고 큐에 유지
   - Ack message: 조회 후 큐에서 삭제
4. "Get Message(s)" 클릭
```

---

## 4. Exchange 종류별 비교표

| 속성 | Direct | Topic | Fanout | Headers |
|------|--------|-------|--------|---------|
| **라우팅 기준** | 라우팅 키 정확 일치 | 라우팅 키 패턴 매칭 | 라우팅 키 무시 (전체 전달) | 메시지 헤더 속성 매칭 |
| **패턴 지원** | 없음 (정확 매칭) | `*` (1단어), `#` (0+단어) | 없음 | `x-match`: all/any |
| **성능** | 빠름 | 보통 | 가장 빠름 | 느림 |
| **유연성** | 낮음 | 높음 | 없음 | 매우 높음 |
| **사용 사례** | 작업 큐, RPC | 로그 라우팅, 이벤트 분류 | 알림, 브로드캐스트 | 복잡한 라우팅 규칙 |
| **라우팅 키 예** | `order.create` | `log.*.error` | (무관) | `format=pdf, type=report` |

### Topic Exchange 패턴 매칭 상세

| 라우팅 키 | 바인딩 키 | 매칭 여부 | 설명 |
|-----------|-----------|-----------|------|
| `log.error` | `log.error` | O | 정확 일치 |
| `log.error` | `log.*` | O | `*`는 1단어 매칭 |
| `log.error` | `*.error` | O | 앞부분 와일드카드 |
| `log.error` | `log.#` | O | `#`는 0개 이상 매칭 |
| `log.error` | `#` | O | 모든 메시지 매칭 |
| `log.error.auth` | `log.*` | X | `*`는 1단어만 |
| `log.error.auth` | `log.#` | O | `#`는 여러 단어 매칭 |
| `log.error.auth` | `log.*.auth` | O | 중간 와일드카드 |

---

## 5. rabbitmqctl 명령어 총정리

> Docker 환경: `docker exec -it rabbitmq` 를 앞에 붙여 실행

### 서버 상태
```bash
# 서버 상태 확인
docker exec -it rabbitmq rabbitmqctl status

# 노드 상태 리포트
docker exec -it rabbitmq rabbitmqctl report

# 환경 설정 확인
docker exec -it rabbitmq rabbitmqctl environment

# Erlang 버전 확인
docker exec -it rabbitmq rabbitmqctl eval 'erlang:system_info(otp_release).'
```

### 사용자 관리
```bash
# 사용자 목록
docker exec -it rabbitmq rabbitmqctl list_users

# 사용자 생성
docker exec -it rabbitmq rabbitmqctl add_user myuser mypassword

# 사용자 삭제
docker exec -it rabbitmq rabbitmqctl delete_user myuser

# 비밀번호 변경
docker exec -it rabbitmq rabbitmqctl change_password myuser newpass

# 태그 설정 (administrator, monitoring, policymaker, management)
docker exec -it rabbitmq rabbitmqctl set_user_tags myuser administrator

# 권한 설정 (configure, write, read)
docker exec -it rabbitmq rabbitmqctl set_permissions -p / myuser ".*" ".*" ".*"

# 권한 확인
docker exec -it rabbitmq rabbitmqctl list_permissions -p /
```

### 가상 호스트(VHost) 관리
```bash
# VHost 목록
docker exec -it rabbitmq rabbitmqctl list_vhosts

# VHost 생성
docker exec -it rabbitmq rabbitmqctl add_vhost my-vhost

# VHost 삭제 (내부 모든 데이터 삭제!)
docker exec -it rabbitmq rabbitmqctl delete_vhost my-vhost
```

### 큐 관리
```bash
# 큐 목록 (메시지 수 포함)
docker exec -it rabbitmq rabbitmqctl list_queues name messages consumers

# 큐 상세 정보
docker exec -it rabbitmq rabbitmqctl list_queues name durable auto_delete arguments messages_ready messages_unacknowledged

# 큐 삭제
docker exec -it rabbitmq rabbitmqctl delete_queue order.queue

# 큐 비우기 (모든 메시지 삭제)
docker exec -it rabbitmq rabbitmqctl purge_queue order.queue
```

### Exchange 관리
```bash
# Exchange 목록
docker exec -it rabbitmq rabbitmqctl list_exchanges name type durable auto_delete

# Binding 목록
docker exec -it rabbitmq rabbitmqctl list_bindings source_name destination_name routing_key
```

### 연결/채널 관리
```bash
# 연결 목록
docker exec -it rabbitmq rabbitmqctl list_connections user peer_host peer_port state

# 채널 목록
docker exec -it rabbitmq rabbitmqctl list_channels connection name consumer_count messages_unacknowledged

# 컨슈머 목록
docker exec -it rabbitmq rabbitmqctl list_consumers

# 특정 연결 강제 종료
docker exec -it rabbitmq rabbitmqctl close_connection "<connection_pid>" "maintenance"
```

### 정책(Policy) 관리
```bash
# 정책 목록
docker exec -it rabbitmq rabbitmqctl list_policies

# 정책 설정 (예: 모든 큐에 HA 미러링)
docker exec -it rabbitmq rabbitmqctl set_policy ha-all \
  ".*" '{"ha-mode":"all"}' \
  --priority 0 --apply-to queues

# 정책 삭제
docker exec -it rabbitmq rabbitmqctl clear_policy ha-all
```

### 플러그인 관리
```bash
# 활성화된 플러그인 목록
docker exec -it rabbitmq rabbitmq-plugins list --enabled

# 플러그인 활성화
docker exec -it rabbitmq rabbitmq-plugins enable rabbitmq_shovel_management

# 플러그인 비활성화
docker exec -it rabbitmq rabbitmq-plugins disable rabbitmq_shovel_management
```

---

## 6. 클러스터링 설정 가이드

### 클러스터 아키텍처
```
  ┌─────────────────────────────────────────────────┐
  │              RabbitMQ Cluster                     │
  │                                                  │
  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
  │  │  Node 1  │  │  Node 2  │  │  Node 3  │      │
  │  │ (disc)   │──│ (disc)   │──│ (ram)    │      │
  │  │          │  │          │  │          │      │
  │  │ Exchange │  │ Exchange │  │ Exchange │      │
  │  │ (동기화) │  │ (동기화) │  │ (동기화) │      │
  │  │          │  │          │  │          │      │
  │  │ Queue A  │  │ Queue B  │  │ Queue C  │      │
  │  │ (로컬)   │  │ (로컬)   │  │ (로컬)   │      │
  │  └──────────┘  └──────────┘  └──────────┘      │
  │                                                  │
  │  ※ Exchange/Binding: 모든 노드에 자동 동기화     │
  │  ※ Queue: 기본적으로 생성된 노드에만 존재        │
  │  ※ Mirrored Queue/Quorum Queue로 복제 가능      │
  └─────────────────────────────────────────────────┘
```

### 클러스터 구성 (Docker Compose)
```yaml
# docker-compose-cluster.yml (참고용)
# 실제 클러스터링은 Erlang Cookie이 동일해야 함
services:
  rabbitmq-node1:
    image: rabbitmq:3-management
    hostname: rabbit1
    environment:
      RABBITMQ_ERLANG_COOKIE: "cluster-secret"
      RABBITMQ_NODENAME: rabbit@rabbit1

  rabbitmq-node2:
    image: rabbitmq:3-management
    hostname: rabbit2
    environment:
      RABBITMQ_ERLANG_COOKIE: "cluster-secret"
      RABBITMQ_NODENAME: rabbit@rabbit2
      # 노드1에 자동 조인
```

### 클러스터 명령어
```bash
# 클러스터 상태 확인
rabbitmqctl cluster_status

# 노드를 클러스터에 조인
rabbitmqctl stop_app
rabbitmqctl join_cluster rabbit@rabbit1
rabbitmqctl start_app

# 노드를 클러스터에서 제거
rabbitmqctl stop_app
rabbitmqctl reset
rabbitmqctl start_app

# 원격 노드 강제 제거
rabbitmqctl forget_cluster_node rabbit@rabbit2
```

### Quorum Queue (RabbitMQ 3.8+, 권장)
```bash
# Quorum Queue: Raft 합의 알고리즘 기반 복제 큐
# Classic Mirrored Queue의 대체 (더 안정적)

# 선언 시 x-queue-type 인자 설정
# Python (pika):
# channel.queue_declare(
#     queue='my-quorum-queue',
#     durable=True,
#     arguments={'x-queue-type': 'quorum'}
# )
```

---

## 7. 모니터링과 알림 설정

### 주요 모니터링 지표

| 지표 | 정상 범위 | 경고 임계치 | 설명 |
|------|-----------|-------------|------|
| Queue Length (Ready) | 0~1000 | > 10000 | 소비되지 않는 메시지 누적 |
| Unacked Messages | 0~100 | > 1000 | 처리 중이지만 ACK 안 된 메시지 |
| Publish Rate | 서비스 의존 | 급격한 변화 | 초당 발행 메시지 수 |
| Deliver Rate | Publish에 근접 | Publish보다 낮음 | 초당 전달 메시지 수 |
| Memory Usage | < watermark | > 80% | 메모리 사용량 |
| Disk Free | > 2GB | < 1GB | 남은 디스크 공간 |
| Connection Count | 서비스 의존 | 급격한 변화 | 활성 TCP 연결 수 |
| Channel Count | 서비스 의존 | > 1000 | 활성 채널 수 |

### HTTP API를 이용한 모니터링
```bash
# 전체 개요
curl -u admin:admin1234 http://localhost:15672/api/overview

# 큐 목록 및 메시지 수
curl -u admin:admin1234 http://localhost:15672/api/queues

# 특정 큐 상세 정보
curl -u admin:admin1234 http://localhost:15672/api/queues/%2F/order.queue

# 노드 상태
curl -u admin:admin1234 http://localhost:15672/api/nodes

# 연결 목록
curl -u admin:admin1234 http://localhost:15672/api/connections

# Health Check 엔드포인트
curl -u admin:admin1234 http://localhost:15672/api/healthchecks/node
```

### Prometheus + Grafana 연동
```bash
# RabbitMQ Prometheus 플러그인 활성화
rabbitmq-plugins enable rabbitmq_prometheus

# Prometheus 메트릭 엔드포인트
# http://localhost:15692/metrics

# Grafana 대시보드: RabbitMQ-Overview (ID: 10991)
```

### 알림 설정 예시 (rabbitmqctl 기반)
```bash
# 큐 길이가 10000을 초과하는 큐 확인 스크립트
#!/bin/bash
THRESHOLD=10000
QUEUES=$(docker exec rabbitmq rabbitmqctl list_queues name messages --formatter json)
# JSON 파싱 후 THRESHOLD 초과하는 큐에 대해 알림 발송
```

---

## 8. 프로덕션 체크리스트

### 서버 설정
- [ ] 충분한 메모리 (vm_memory_high_watermark = 0.4)
- [ ] 디스크 여유 공간 확보 (disk_free_limit >= 2GB)
- [ ] 적절한 heartbeat 설정 (60초)
- [ ] channel_max 제한 설정
- [ ] consumer_timeout 설정 (처리 시간에 맞게)

### 보안
- [ ] 기본 guest 계정 비활성화 또는 비밀번호 변경
- [ ] 서비스별 전용 사용자 생성 (최소 권한 원칙)
- [ ] TLS/SSL 활성화
- [ ] Management UI 접근 제한 (IP 화이트리스트)
- [ ] VHost로 서비스 격리

### 메시지 안정성
- [ ] durable Exchange/Queue 사용
- [ ] delivery_mode=2 (persistent) 메시지
- [ ] Publisher Confirm 활성화
- [ ] Consumer manual ACK 사용 (auto_ack=False)
- [ ] Dead Letter Queue(DLQ) 설정
- [ ] 메시지 TTL 설정

### 성능
- [ ] Prefetch Count 최적화 (QoS)
- [ ] Connection/Channel 재사용 (풀링)
- [ ] Lazy Queue 활용 (메모리 부족 시)
- [ ] Quorum Queue 사용 (Mirrored Queue 대신)
- [ ] 불필요한 Exchange/Queue 정리

### 고가용성
- [ ] 3노드 이상 클러스터 구성
- [ ] Quorum Queue 사용 (자동 리더 선출)
- [ ] 로드밸런서 앞단 배치 (HAProxy/Nginx)
- [ ] 네트워크 파티션 처리 전략 설정

### 모니터링
- [ ] Management UI 접근 가능
- [ ] Prometheus + Grafana 대시보드
- [ ] 큐 길이 알림 설정
- [ ] 메모리/디스크 알림 설정
- [ ] 연결 수 모니터링
- [ ] Consumer Lag 모니터링

---

## 부록: 주요 포트 정리

| 포트 | 프로토콜 | 용도 |
|------|----------|------|
| 5672 | AMQP | 메시지 발행/소비 (프로듀서/컨슈머) |
| 15672 | HTTP | Management UI (웹 관리 도구) |
| 15692 | HTTP | Prometheus 메트릭 엔드포인트 |
| 25672 | Erlang | 클러스터 노드 간 통신 |
| 4369 | EPMD | Erlang Port Mapper Daemon |
| 1883 | MQTT | MQTT 프로토콜 (IoT) |
| 61613 | STOMP | STOMP 프로토콜 (웹소켓) |
