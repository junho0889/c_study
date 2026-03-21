# ■■■ Kafka 실습 가이드 ■■■

## 목차
1. [Kafka 아키텍처 개요](#1-kafka-아키텍처-개요)
2. [실행 방법](#2-실행-방법)
3. [kafka-topics.sh 명령어 총정리](#3-kafka-topicssh-명령어-총정리)
4. [파티션/리플리케이션 설정 가이드](#4-파티션리플리케이션-설정-가이드)
5. [모니터링](#5-모니터링)
6. [프로덕션 설정 체크리스트](#6-프로덕션-설정-체크리스트)
7. [트러블슈팅 가이드](#7-트러블슈팅-가이드)

---

## 1. Kafka 아키텍처 개요

### 전체 시스템 구조
```
  ┌──────────────────────────────────────────────────────────────┐
  │                    Kafka Cluster                              │
  │                                                              │
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
  │  │  Broker #1   │  │  Broker #2   │  │  Broker #3   │         │
  │  │  (Leader P0) │  │  (Leader P1) │  │  (Leader P2) │         │
  │  │  (Replica P1)│  │  (Replica P2)│  │  (Replica P0)│         │
  │  │  (Replica P2)│  │  (Replica P0)│  │  (Replica P1)│         │
  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
  │         │                 │                 │                 │
  │         └────────┬────────┴────────┬────────┘                 │
  │                  │                 │                           │
  │           ┌──────┴──────┐  ┌──────┴──────┐                   │
  │           │  Zookeeper  │  │  Kafka UI   │                   │
  │           │  (메타데이터)│  │ (모니터링)  │                   │
  │           └─────────────┘  └─────────────┘                   │
  └──────────────────────────────────────────────────────────────┘
         ▲                                    │
         │                                    ▼
  ┌──────┴───────┐                    ┌───────┴──────┐
  │   Producer   │                    │   Consumer   │
  │  (메시지     │                    │  (메시지     │
  │   발행자)    │                    │   소비자)    │
  └──────────────┘                    └──────────────┘
```

### 토픽/파티션 구조
```
  Topic: "test-topic" (파티션 3개, 리플리케이션 팩터 3)

  ┌─── Partition 0 ──────────────────────────────┐
  │ Offset: 0 │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ ...    │  → Leader: Broker 1
  └──────────────────────────────────────────────┘    Replicas: Broker 2, 3

  ┌─── Partition 1 ──────────────────────────────┐
  │ Offset: 0 │ 1 │ 2 │ 3 │ 4 │ ...             │  → Leader: Broker 2
  └──────────────────────────────────────────────┘    Replicas: Broker 1, 3

  ┌─── Partition 2 ──────────────────────────────┐
  │ Offset: 0 │ 1 │ 2 │ 3 │ ...                 │  → Leader: Broker 3
  └──────────────────────────────────────────────┘    Replicas: Broker 1, 2
```

### 컨슈머 그룹과 파티션 할당
```
  Consumer Group: "test-consumer-group"

  ┌──────────┐     ┌─────────────┐
  │Consumer 1│ ◄── │ Partition 0 │
  └──────────┘     └─────────────┘

  ┌──────────┐     ┌─────────────┐
  │Consumer 2│ ◄── │ Partition 1 │
  └──────────┘     └─────────────┘

  ┌──────────┐     ┌─────────────┐
  │Consumer 3│ ◄── │ Partition 2 │
  └──────────┘     └─────────────┘

  ※ 컨슈머 수 > 파티션 수 → 일부 컨슈머는 유휴 상태
  ※ 컨슈머 수 < 파티션 수 → 일부 컨슈머가 여러 파티션 담당
```

### 메시지 생산/소비 흐름
```
  Producer                 Kafka Broker              Consumer
  ┌──────┐                ┌──────────┐              ┌──────┐
  │      │ ── produce ──► │ Append   │              │      │
  │      │                │ to Log   │              │      │
  │      │                │          │ ◄── poll ─── │      │
  │      │                │ Return   │              │      │
  │      │                │ Offset   │ ── batch ──► │      │
  │      │                │          │              │      │
  │      │                │          │ ◄── commit ─ │      │
  └──────┘                └──────────┘              └──────┘
```

---

## 2. 실행 방법

### Step 1: Docker Compose로 Kafka 클러스터 시작
```bash
# lab 디렉토리로 이동
cd kafka-learning/lab

# 백그라운드에서 모든 서비스 시작
docker-compose up -d

# 서비스 상태 확인
docker-compose ps

# 로그 확인 (실시간)
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f kafka-broker-1
```

### Step 2: 클러스터 상태 확인
```bash
# 브로커 상태 확인 (Zookeeper에서 조회)
docker exec -it zookeeper bash -c "echo dump | nc localhost 2181"

# Kafka UI 접속: 웹 브라우저에서
# http://localhost:8080
```

### Step 3: Python 환경 준비
```bash
# kafka-python 라이브러리 설치
pip install kafka-python

# (선택) 가상환경 사용 시
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install kafka-python
```

### Step 4: Producer 실행
```bash
# 프로듀서 실행 (메시지 20건 전송)
python producer.py
```

### Step 5: Consumer 실행
```bash
# 자동 커밋 모드 (기본)
python consumer.py

# 수동 커밋 모드
python consumer.py manual
```

### Step 6: 환경 종료
```bash
# 서비스 중지 (데이터 보존)
docker-compose down

# 서비스 중지 + 볼륨(데이터) 삭제
docker-compose down -v
```

---

## 3. kafka-topics.sh 명령어 총정리

> Docker 환경에서 실행 시 `docker exec -it kafka-broker-1` 을 앞에 붙여야 합니다.

### 토픽 생성
```bash
# 기본 토픽 생성
docker exec -it kafka-broker-1 kafka-topics \
  --bootstrap-server localhost:29092 \
  --create \
  --topic my-topic \
  --partitions 3 \
  --replication-factor 3

# 설정을 추가하며 토픽 생성
docker exec -it kafka-broker-1 kafka-topics \
  --bootstrap-server localhost:29092 \
  --create \
  --topic my-topic-custom \
  --partitions 6 \
  --replication-factor 3 \
  --config retention.ms=604800000 \
  --config segment.bytes=104857600 \
  --config min.insync.replicas=2
```

### 토픽 목록 조회
```bash
# 모든 토픽 목록
docker exec -it kafka-broker-1 kafka-topics \
  --bootstrap-server localhost:29092 \
  --list

# 내부 토픽 포함 조회
docker exec -it kafka-broker-1 kafka-topics \
  --bootstrap-server localhost:29092 \
  --list \
  --exclude-internal  # 내부 토픽 제외
```

### 토픽 상세 정보 확인
```bash
# 특정 토픽 상세 정보 (파티션, 리플리카, ISR 확인)
docker exec -it kafka-broker-1 kafka-topics \
  --bootstrap-server localhost:29092 \
  --describe \
  --topic test-topic

# 모든 토픽 상세 정보
docker exec -it kafka-broker-1 kafka-topics \
  --bootstrap-server localhost:29092 \
  --describe

# ISR이 부족한 토픽만 조회 (장애 감지용)
docker exec -it kafka-broker-1 kafka-topics \
  --bootstrap-server localhost:29092 \
  --describe \
  --under-replicated-partitions
```

### 토픽 설정 변경
```bash
# 파티션 수 증가 (줄일 수는 없음!)
docker exec -it kafka-broker-1 kafka-topics \
  --bootstrap-server localhost:29092 \
  --alter \
  --topic my-topic \
  --partitions 6

# 토픽 설정 변경 (kafka-configs 사용)
docker exec -it kafka-broker-1 kafka-configs \
  --bootstrap-server localhost:29092 \
  --alter \
  --entity-type topics \
  --entity-name my-topic \
  --add-config retention.ms=259200000  # 보존 기간 3일로 변경
```

### 토픽 삭제
```bash
docker exec -it kafka-broker-1 kafka-topics \
  --bootstrap-server localhost:29092 \
  --delete \
  --topic my-topic
```

### 메시지 직접 생산/소비 (CLI)
```bash
# 콘솔 프로듀서 (메시지 직접 입력)
docker exec -it kafka-broker-1 kafka-console-producer \
  --bootstrap-server localhost:29092 \
  --topic test-topic

# 콘솔 컨슈머 (처음부터 읽기)
docker exec -it kafka-broker-1 kafka-console-consumer \
  --bootstrap-server localhost:29092 \
  --topic test-topic \
  --from-beginning

# 특정 파티션만 읽기
docker exec -it kafka-broker-1 kafka-console-consumer \
  --bootstrap-server localhost:29092 \
  --topic test-topic \
  --partition 0 \
  --from-beginning

# 키와 함께 생산
docker exec -it kafka-broker-1 kafka-console-producer \
  --bootstrap-server localhost:29092 \
  --topic test-topic \
  --property parse.key=true \
  --property key.separator=:
# 입력 형식: key:value
```

### 컨슈머 그룹 관리
```bash
# 컨슈머 그룹 목록
docker exec -it kafka-broker-1 kafka-consumer-groups \
  --bootstrap-server localhost:29092 \
  --list

# 컨슈머 그룹 상세 (오프셋, 랙 확인)
docker exec -it kafka-broker-1 kafka-consumer-groups \
  --bootstrap-server localhost:29092 \
  --describe \
  --group test-consumer-group

# 오프셋 리셋 (컨슈머가 중지된 상태에서만 가능)
# earliest: 처음부터 다시 읽기
docker exec -it kafka-broker-1 kafka-consumer-groups \
  --bootstrap-server localhost:29092 \
  --group test-consumer-group \
  --topic test-topic \
  --reset-offsets \
  --to-earliest \
  --execute

# 특정 오프셋으로 리셋
docker exec -it kafka-broker-1 kafka-consumer-groups \
  --bootstrap-server localhost:29092 \
  --group test-consumer-group \
  --topic test-topic:0 \
  --reset-offsets \
  --to-offset 5 \
  --execute
```

---

## 4. 파티션/리플리케이션 설정 가이드

### 파티션 수 결정 기준

| 기준 | 설명 |
|------|------|
| 처리량 목표 | 단일 파티션 처리량: ~10MB/s. 목표 100MB/s → 최소 10 파티션 |
| 컨슈머 수 | 파티션 수 >= 컨슈머 수 (초과 컨슈머는 유휴) |
| 키 카디널리티 | 고유 키 수보다 파티션이 많으면 일부 파티션이 비어있음 |
| 브로커 수 | 파티션 수가 많으면 메타데이터 관리 부담 증가 |
| 장애 복구 시간 | 파티션이 많을수록 리밸런싱 시간 증가 |

### 리플리케이션 팩터 결정 기준

| 설정 | 용도 |
|------|------|
| RF=1 | 데이터 손실 가능. 개발/테스트 환경 |
| RF=2 | 1대 장애 허용. 비용과 안정성 절충 |
| RF=3 | 프로덕션 권장. 2대 동시 장애까지 허용 |

### acks와 min.insync.replicas 조합

| acks | min.insync.replicas | 의미 |
|------|---------------------|------|
| 0 | - | 전송만 하고 확인 안 함 (최고 속도, 데이터 손실 가능) |
| 1 | - | 리더만 확인 (리더 장애 시 손실 가능) |
| all | 1 | 리더만 확인과 동일 (ISR이 1이면) |
| all | 2 | 리더 + 1 팔로워 확인 (프로덕션 권장) |
| all | 3 | 모든 복제본 확인 (가장 안전, 가용성 낮음) |

---

## 5. 모니터링

### Consumer Lag 모니터링
```bash
# 컨슈머 그룹의 랙(lag) 확인
# LAG = 파티션의 최신 오프셋 - 컨슈머가 읽은 오프셋
docker exec -it kafka-broker-1 kafka-consumer-groups \
  --bootstrap-server localhost:29092 \
  --describe \
  --group test-consumer-group

# 출력 예시:
# GROUP              TOPIC       PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
# test-consumer-group test-topic 0          150             200             50
# test-consumer-group test-topic 1          180             200             20
# test-consumer-group test-topic 2          200             200             0
```

### 브로커 메트릭 확인
```bash
# 브로커 로그 디렉토리 크기 확인
docker exec -it kafka-broker-1 du -sh /var/lib/kafka/data/

# 토픽별 메시지 수 확인
docker exec -it kafka-broker-1 kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:29092 \
  --topic test-topic
```

### Kafka UI 활용 (http://localhost:8080)
- **Brokers**: 브로커 상태, JMX 메트릭 확인
- **Topics**: 토픽 목록, 파티션 정보, 메시지 조회
- **Consumers**: 컨슈머 그룹, 오프셋, 랙 모니터링
- **Schema Registry**: (설정 시) 스키마 관리

---

## 6. 프로덕션 설정 체크리스트

### 브로커 설정
- [ ] `min.insync.replicas=2` (데이터 안정성)
- [ ] `default.replication.factor=3` (기본 복제본 3개)
- [ ] `auto.create.topics.enable=false` (토픽 자동 생성 비활성화)
- [ ] `unclean.leader.election.enable=false` (데이터 손실 방지)
- [ ] `log.retention.hours=168` (7일 보존, 서비스에 맞게 조정)
- [ ] `num.partitions` (서비스 처리량에 맞게 설정)
- [ ] JVM 힙 메모리 6GB 이상 (`KAFKA_HEAP_OPTS`)
- [ ] 전용 디스크 (OS와 분리, SSD 권장)
- [ ] 페이지 캐시를 위한 충분한 시스템 메모리

### 프로듀서 설정
- [ ] `acks=all` (메시지 손실 방지)
- [ ] `retries >= 3` (일시적 장애 대비)
- [ ] `enable.idempotence=true` (중복 전송 방지)
- [ ] `compression.type=snappy` (네트워크 효율)
- [ ] `linger.ms=5~100` (배치 효율과 지연시간 트레이드오프)

### 컨슈머 설정
- [ ] `enable.auto.commit=false` (수동 커밋 권장)
- [ ] `auto.offset.reset=earliest` (신규 컨슈머는 처음부터)
- [ ] `max.poll.records` (처리 시간에 맞게 조정)
- [ ] `session.timeout.ms=30000` (리밸런싱 감도)
- [ ] 멱등성(idempotent) 처리 로직 구현

### 인프라
- [ ] Zookeeper 3대 이상 (또는 KRaft 모드)
- [ ] Kafka 브로커 3대 이상
- [ ] 네트워크 대역폭 충분히 확보
- [ ] 모니터링 시스템 구축 (Prometheus + Grafana)
- [ ] 알림 설정 (Consumer Lag, Broker Down)

---

## 7. 트러블슈팅 가이드

### 브로커 연결 실패
```
증상: NoBrokersAvailable 예외
원인: 브로커가 아직 시작되지 않았거나 네트워크 문제

해결:
1. docker-compose ps 로 브로커 상태 확인
2. docker-compose logs kafka-broker-1 로 에러 로그 확인
3. ADVERTISED_LISTENERS 설정이 올바른지 확인
4. 방화벽/포트 바인딩 확인
```

### Consumer Lag 증가
```
증상: 컨슈머가 메시지를 따라잡지 못함
원인: 처리 속도 < 생산 속도

해결:
1. 컨슈머 인스턴스 추가 (파티션 수까지)
2. max.poll.records 줄여서 처리 시간 단축
3. 비즈니스 로직 최적화
4. 파티션 수 증가 (신규 토픽 생성 권장)
```

### 리밸런싱 빈번 발생
```
증상: 컨슈머 그룹이 자주 리밸런싱됨
원인: session.timeout 내에 poll() 미호출

해결:
1. session.timeout.ms 늘리기
2. max.poll.records 줄이기
3. 처리 로직을 비동기로 변경
4. heartbeat.interval.ms 줄이기 (빠른 하트비트)
```

### 메시지 중복 소비
```
증상: 같은 메시지가 여러 번 처리됨
원인: 오프셋 커밋 전에 컨슈머가 재시작됨

해결:
1. 수동 커밋 사용 (처리 완료 후 커밋)
2. 비즈니스 로직에 멱등성 보장 (DB unique key 등)
3. Kafka Transactions 사용 (exactly-once)
```

### 디스크 공간 부족
```
증상: 브로커가 로그 쓰기 실패
원인: 로그 보존 기간 대비 디스크 용량 부족

해결:
1. log.retention.hours 줄이기
2. log.retention.bytes 설정
3. 디스크 용량 증설
4. 압축 토픽 사용 (log.cleanup.policy=compact)
```

### ISR 축소 (Under-Replicated Partitions)
```
증상: ISR 목록에서 일부 브로커 빠짐
원인: 팔로워 브로커가 리더를 따라잡지 못함

해결:
1. 해당 브로커의 상태/로그 확인
2. 네트워크 대역폭 확인
3. replica.lag.time.max.ms 조정 (기본 30초)
4. num.replica.fetchers 증가 (복제 스레드 수)
```

---

## 부록: 주요 포트 정리

| 서비스 | 내부 포트 | 외부 포트 | 용도 |
|--------|-----------|-----------|------|
| Zookeeper | 2181 | 2181 | 클라이언트 연결 |
| Broker 1 | 29092 / 9092 | 9092 | 내부통신 / 외부접속 |
| Broker 2 | 29093 / 9093 | 9093 | 내부통신 / 외부접속 |
| Broker 3 | 29094 / 9094 | 9094 | 내부통신 / 외부접속 |
| Kafka UI | 8080 | 8080 | 웹 UI |
