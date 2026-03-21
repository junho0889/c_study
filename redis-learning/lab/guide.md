# ■■■ Redis 실습 가이드 ■■■

## 목차
1. [Redis 아키텍처](#1-redis-아키텍처)
2. [실행 방법](#2-실행-방법)
3. [redis-cli 명령어 총정리표](#3-redis-cli-명령어-총정리표)
4. [메모리 관리 전략](#4-메모리-관리-전략)
5. [백업/복원 방법](#5-백업복원-방법)
6. [보안 설정](#6-보안-설정)
7. [성능 튜닝 가이드](#7-성능-튜닝-가이드)

---

## 1. Redis 아키텍처

### Standalone 모드 (단독 실행)
```
  ┌─────────────────────────────┐
  │        Redis Server          │
  │                             │
  │  ┌─────────────────────┐   │
  │  │   메모리 (데이터)    │   │
  │  └─────────────────────┘   │
  │                             │
  │  ┌──────┐  ┌──────────┐   │
  │  │ RDB  │  │   AOF    │   │
  │  │스냅샷│  │ 로그파일  │   │
  │  └──────┘  └──────────┘   │
  └─────────────────────────────┘
         ▲
         │ TCP 6379
  ┌──────┴──────┐
  │   Client    │
  └─────────────┘

  장점: 구성 간단, 관리 쉬움
  단점: 단일 장애점(SPOF), 장애 시 서비스 중단
```

### Sentinel 모드 (이 실습 구성)
```
  ┌──────────────────────────────────────────────────────┐
  │                   Sentinel Cluster                    │
  │  ┌───────────┐  ┌───────────┐  ┌───────────┐       │
  │  │ Sentinel 1│  │ Sentinel 2│  │ Sentinel 3│       │
  │  │  :26379   │  │  :26380   │  │  :26381   │       │
  │  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘       │
  │        │              │              │              │
  │        └──────────────┼──────────────┘              │
  │                       │ 감시 & 페일오버              │
  └───────────────────────┼─────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
  ┌──────────┐    ┌──────────┐    ┌──────────┐
  │  Master  │───►│ Replica1 │    │ Replica2 │
  │  :6379   │    │  :6380   │    │  :6381   │
  │ (읽기/   │───►│ (읽기    │    │ (읽기    │
  │  쓰기)   │    │  전용)   │    │  전용)   │
  └──────────┘    └──────────┘    └──────────┘
       │                │                │
       └────────────────┼────────────────┘
                        │ 비동기 복제

  장점: 자동 페일오버, 고가용성, 읽기 확장
  단점: 쓰기는 마스터 1대만, 비동기 복제로 데이터 손실 가능
```

### Cluster 모드 (프로덕션 대규모)
```
  ┌─────────────────────────────────────────────────────────┐
  │                    Redis Cluster                         │
  │                                                         │
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
  │  │  Master A   │  │  Master B   │  │  Master C   │    │
  │  │ 슬롯 0-5460 │  │슬롯5461-10922│ │슬롯10923-16383│  │
  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
  │         │                │                │            │
  │  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐    │
  │  │  Replica A  │  │  Replica B  │  │  Replica C  │    │
  │  └─────────────┘  └─────────────┘  └─────────────┘    │
  └─────────────────────────────────────────────────────────┘

  장점: 수평 확장(쓰기 분산), 자동 샤딩, 고가용성
  단점: 복잡한 운영, 멀티키 명령 제한, 최소 6노드 필요
```

### 페일오버 과정
```
  1. 정상 상태
     Sentinel ──PING──► Master ──PONG──► Sentinel  ✓

  2. 마스터 장애 감지
     Sentinel ──PING──► Master  (응답 없음)
     → SDOWN (Subjective Down, 주관적 다운)

  3. 과반수 동의
     Sentinel 1: "마스터 죽었다" ─┐
     Sentinel 2: "나도 동의"     ├→ ODOWN (Objective Down, 객관적 다운)
     Sentinel 3: "나도 동의"     ─┘

  4. 페일오버 실행
     Sentinel: Replica 1을 새 Master로 승격!
     → SLAVEOF NO ONE (마스터로 승격)
     → 다른 Replica들은 새 Master를 바라보도록 재설정
```

---

## 2. 실행 방법

### Step 1: Docker Compose로 Redis 환경 시작
```bash
cd redis-learning/lab

# 모든 서비스 시작
docker-compose up -d

# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f redis-master
```

### Step 2: 연결 확인
```bash
# redis-cli로 마스터 연결
docker exec -it redis-master redis-cli -a redis1234

# PING 테스트
127.0.0.1:6379> PING
# 응답: PONG

# 복제 상태 확인
127.0.0.1:6379> INFO replication

# Sentinel 상태 확인
docker exec -it redis-sentinel-1 redis-cli -p 26379 SENTINEL masters
```

### Step 3: RedisInsight 접속
```
웹 브라우저에서 http://localhost:5540 접속
→ "Add Redis Database" 클릭
→ Host: redis-master, Port: 6379, Password: redis1234
```

### Step 4: Python 실습 코드 실행
```bash
pip install redis
python example.py
```

### Step 5: 페일오버 테스트
```bash
# 마스터를 강제로 중지하여 페일오버 트리거
docker stop redis-master

# Sentinel 로그에서 페일오버 과정 확인
docker logs -f redis-sentinel-1

# 잠시 후 새 마스터 확인
docker exec -it redis-sentinel-1 redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster

# 원래 마스터 다시 시작 (레플리카로 복귀)
docker start redis-master
```

---

## 3. redis-cli 명령어 총정리표

### 서버/연결 명령어

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `PING` | 연결 테스트 | `PING` → PONG |
| `AUTH` | 인증 | `AUTH redis1234` |
| `SELECT` | DB 선택 (0-15) | `SELECT 1` |
| `DBSIZE` | 현재 DB의 키 수 | `DBSIZE` |
| `INFO` | 서버 정보 | `INFO memory` |
| `CONFIG GET` | 설정값 조회 | `CONFIG GET maxmemory` |
| `CONFIG SET` | 설정값 변경 | `CONFIG SET maxmemory 512mb` |
| `FLUSHDB` | 현재 DB 전체 삭제 | `FLUSHDB` |
| `FLUSHALL` | 모든 DB 전체 삭제 | `FLUSHALL` |
| `SLOWLOG` | 느린 명령 로그 | `SLOWLOG GET 10` |
| `CLIENT LIST` | 접속 클라이언트 목록 | `CLIENT LIST` |
| `MONITOR` | 실시간 명령 모니터링 | `MONITOR` |

### 키 관련 명령어

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `SET` | 값 설정 | `SET key value` |
| `GET` | 값 조회 | `GET key` |
| `DEL` | 키 삭제 | `DEL key1 key2` |
| `EXISTS` | 키 존재 확인 | `EXISTS key` → 1/0 |
| `EXPIRE` | TTL 설정 (초) | `EXPIRE key 300` |
| `TTL` | 남은 TTL 확인 | `TTL key` |
| `PERSIST` | TTL 제거 | `PERSIST key` |
| `TYPE` | 키의 데이터 타입 | `TYPE key` |
| `RENAME` | 키 이름 변경 | `RENAME old new` |
| `SCAN` | 키 순회 (KEYS 대신 사용!) | `SCAN 0 MATCH user:*` |
| `KEYS` | 패턴 매칭 조회 (주의!) | `KEYS user:*` (프로덕션 금지) |
| `OBJECT ENCODING` | 내부 인코딩 확인 | `OBJECT ENCODING key` |

### String 명령어

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `SET` | 값 설정 | `SET name "홍길동"` |
| `GET` | 값 조회 | `GET name` |
| `SETNX` | 없을 때만 설정 | `SETNX lock:1 owner` |
| `SETEX` | TTL과 함께 설정 | `SETEX cache 300 data` |
| `MSET` | 다중 설정 | `MSET k1 v1 k2 v2` |
| `MGET` | 다중 조회 | `MGET k1 k2` |
| `INCR` | +1 증가 | `INCR counter` |
| `INCRBY` | N만큼 증가 | `INCRBY counter 10` |
| `DECR` | -1 감소 | `DECR counter` |
| `APPEND` | 문자열 이어붙이기 | `APPEND key " world"` |
| `STRLEN` | 문자열 길이 | `STRLEN key` |

### Hash 명령어

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `HSET` | 필드 설정 | `HSET user:1 name "김"` |
| `HGET` | 필드 조회 | `HGET user:1 name` |
| `HGETALL` | 전체 조회 | `HGETALL user:1` |
| `HMSET` | 다중 설정 | `HMSET user:1 a 1 b 2` |
| `HMGET` | 다중 조회 | `HMGET user:1 a b` |
| `HDEL` | 필드 삭제 | `HDEL user:1 name` |
| `HEXISTS` | 필드 존재 확인 | `HEXISTS user:1 name` |
| `HLEN` | 필드 수 | `HLEN user:1` |
| `HINCRBY` | 숫자 필드 증가 | `HINCRBY user:1 age 1` |
| `HSCAN` | 필드 순회 | `HSCAN user:1 0` |

### List 명령어

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `LPUSH` | 왼쪽에 추가 | `LPUSH list a b c` |
| `RPUSH` | 오른쪽에 추가 | `RPUSH list x y z` |
| `LPOP` | 왼쪽에서 제거 | `LPOP list` |
| `RPOP` | 오른쪽에서 제거 | `RPOP list` |
| `LRANGE` | 범위 조회 | `LRANGE list 0 -1` |
| `LLEN` | 길이 | `LLEN list` |
| `LINDEX` | 인덱스 조회 | `LINDEX list 0` |
| `LSET` | 인덱스 값 변경 | `LSET list 0 new` |
| `LTRIM` | 범위만 유지 | `LTRIM list 0 99` |
| `BRPOP` | 블로킹 POP | `BRPOP list 10` |
| `LMOVE` | 리스트 간 이동 | `LMOVE src dst LEFT RIGHT` |

### Set 명령어

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `SADD` | 멤버 추가 | `SADD set a b c` |
| `SREM` | 멤버 삭제 | `SREM set a` |
| `SMEMBERS` | 전체 조회 | `SMEMBERS set` |
| `SISMEMBER` | 멤버 확인 | `SISMEMBER set a` |
| `SCARD` | 멤버 수 | `SCARD set` |
| `SINTER` | 교집합 | `SINTER set1 set2` |
| `SUNION` | 합집합 | `SUNION set1 set2` |
| `SDIFF` | 차집합 | `SDIFF set1 set2` |
| `SPOP` | 랜덤 제거 | `SPOP set` |
| `SRANDMEMBER` | 랜덤 조회 | `SRANDMEMBER set 3` |

### Sorted Set 명령어

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `ZADD` | 멤버+스코어 추가 | `ZADD rank 100 "user1"` |
| `ZREM` | 멤버 삭제 | `ZREM rank "user1"` |
| `ZSCORE` | 스코어 조회 | `ZSCORE rank "user1"` |
| `ZRANK` | 순위 조회 (오름차순) | `ZRANK rank "user1"` |
| `ZREVRANK` | 순위 조회 (내림차순) | `ZREVRANK rank "user1"` |
| `ZRANGE` | 범위 조회 (오름차순) | `ZRANGE rank 0 9 WITHSCORES` |
| `ZREVRANGE` | 범위 조회 (내림차순) | `ZREVRANGE rank 0 9` |
| `ZINCRBY` | 스코어 증가 | `ZINCRBY rank 50 "user1"` |
| `ZCARD` | 멤버 수 | `ZCARD rank` |
| `ZRANGEBYSCORE` | 스코어 범위 조회 | `ZRANGEBYSCORE rank 0 100` |
| `ZCOUNT` | 스코어 범위 내 수 | `ZCOUNT rank 0 100` |

---

## 4. 메모리 관리 전략

### 메모리 사용량 확인
```bash
# 전체 메모리 정보
redis-cli -a redis1234 INFO memory

# 주요 지표
# used_memory: Redis가 할당한 메모리
# used_memory_rss: OS가 보고하는 실제 메모리 (RSS)
# used_memory_peak: 최대 메모리 사용량
# mem_fragmentation_ratio: 단편화 비율 (RSS/used, 1.5 이상이면 문제)
```

### Eviction 정책 선택 가이드

| 용도 | 권장 정책 | 이유 |
|------|-----------|------|
| 범용 캐시 | allkeys-lru | 오래된 키부터 제거 |
| 빈도 기반 캐시 | allkeys-lfu | 자주 접근하는 데이터 유지 |
| 세션 저장소 | volatile-ttl | TTL이 짧은 것부터 제거 |
| 데이터 저장소 | noeviction | 삭제 대신 에러 반환 |

### 메모리 최적화 팁
```bash
# 1. 키 이름을 짧게 (메모리 절약)
# 나쁜 예: user:profile:information:1234
# 좋은 예: u:p:1234

# 2. Hash 사용 (작은 해시는 ziplist로 압축 저장)
# 100개 이하 필드 + 64바이트 이하 값 → ziplist 인코딩 (메모리 효율적)

# 3. OBJECT ENCODING으로 내부 인코딩 확인
redis-cli -a redis1234 OBJECT ENCODING mykey

# 4. 큰 키 찾기 (메모리 분석)
redis-cli -a redis1234 --bigkeys

# 5. 메모리 사용량 분석 (키별)
redis-cli -a redis1234 MEMORY USAGE mykey
```

---

## 5. 백업/복원 방법

### RDB 스냅샷 백업
```bash
# 수동 스냅샷 생성 (백그라운드)
redis-cli -a redis1234 BGSAVE

# 스냅샷 상태 확인
redis-cli -a redis1234 LASTSAVE

# RDB 파일 복사 (Docker 환경)
docker cp redis-master:/data/dump.rdb ./backup/dump.rdb

# 복원: RDB 파일을 data 디렉토리에 복사 후 Redis 재시작
docker cp ./backup/dump.rdb redis-master:/data/dump.rdb
docker restart redis-master
```

### AOF 백업/복원
```bash
# AOF 파일 복사
docker cp redis-master:/data/appendonly.aof ./backup/

# AOF 무결성 체크
docker exec redis-master redis-check-aof /data/appendonly.aof

# AOF 손상 시 복구
docker exec redis-master redis-check-aof --fix /data/appendonly.aof

# AOF 수동 재작성 (파일 크기 최적화)
redis-cli -a redis1234 BGREWRITEAOF
```

### RDB vs AOF 비교

| 항목 | RDB | AOF |
|------|-----|-----|
| 데이터 손실 | 마지막 스냅샷 이후 손실 | 최대 1초 손실 (everysec) |
| 파일 크기 | 작음 (압축됨) | 큼 (모든 쓰기 명령 기록) |
| 복구 속도 | 빠름 | 느림 (명령 재실행) |
| 성능 영향 | fork() 시 일시적 부하 | 지속적 I/O 부하 |
| 권장 | 백업용 | 데이터 안정성 |

---

## 6. 보안 설정

### 인증 설정
```bash
# redis.conf에 비밀번호 설정
requirepass <강력한_비밀번호>

# 마스터-레플리카 인증
masterauth <마스터_비밀번호>

# ACL (Redis 6.0+): 사용자별 세밀한 권한 제어
# 사용자 생성 (읽기 전용)
ACL SETUSER readonly on >password123 ~* +get +mget +hget +hgetall -@write

# 사용자 생성 (특정 키 패턴만 접근)
ACL SETUSER app1 on >app1pass ~app1:* +@all

# ACL 목록 확인
ACL LIST

# 현재 사용자 확인
ACL WHOAMI
```

### 네트워크 보안
```bash
# bind: 특정 IP만 바인딩
bind 127.0.0.1 10.0.0.1

# protected-mode: 비밀번호/bind 없이는 외부 접속 차단
protected-mode yes

# 포트 변경 (보안 강화)
port 16379

# TLS/SSL 활성화 (Redis 6.0+)
tls-port 6380
tls-cert-file /path/to/redis.crt
tls-key-file /path/to/redis.key
tls-ca-cert-file /path/to/ca.crt
```

### 위험 명령어 비활성화
```bash
# redis.conf에서 설정
rename-command FLUSHDB ""       # FLUSHDB 비활성화
rename-command FLUSHALL ""      # FLUSHALL 비활성화
rename-command KEYS ""          # KEYS 비활성화 (SCAN 사용)
rename-command CONFIG "CONFIG_SECRET"  # CONFIG 명령어 이름 변경
rename-command DEBUG ""         # DEBUG 비활성화
rename-command SHUTDOWN "SHUTDOWN_SECRET"  # SHUTDOWN 명령어 이름 변경
```

---

## 7. 성능 튜닝 가이드

### KEYS 대신 SCAN 사용
```bash
# 나쁜 예 (O(N), 전체 키 스캔 → 서비스 블로킹!)
KEYS user:*

# 좋은 예 (커서 기반 순회, 블로킹 없음)
SCAN 0 MATCH user:* COUNT 100
# → 반환: 커서값 + 매칭된 키 목록
# 커서가 0이 될 때까지 반복
```

### Pipeline vs 개별 명령
```bash
# 개별 명령: 네트워크 왕복(RTT) * N회
# 100개 명령, RTT 1ms → 100ms

# Pipeline: 네트워크 왕복 1회
# 100개 명령, RTT 1ms → 1ms + 처리시간
# → 약 10~100배 성능 향상
```

### 슬로우 로그 분석
```bash
# 느린 명령 조회 (최근 10개)
SLOWLOG GET 10

# 느린 명령 총 수
SLOWLOG LEN

# 슬로우 로그 초기화
SLOWLOG RESET

# 임계값 변경 (마이크로초)
CONFIG SET slowlog-log-slower-than 5000  # 5ms
```

### 주요 성능 지표 모니터링
```bash
# 초당 처리 명령 수
redis-cli -a redis1234 INFO stats | grep instantaneous_ops_per_sec

# 연결된 클라이언트 수
redis-cli -a redis1234 INFO clients | grep connected_clients

# 메모리 단편화 비율
redis-cli -a redis1234 INFO memory | grep mem_fragmentation_ratio

# 히트율 (캐시 효율)
redis-cli -a redis1234 INFO stats | grep keyspace
# hit_rate = keyspace_hits / (keyspace_hits + keyspace_misses)
```

### 연결 풀 사용 (Python)
```python
import redis

# ConnectionPool: 연결을 재사용하여 오버헤드 최소화
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    password='redis1234',
    max_connections=20,     # 최대 연결 수
    decode_responses=True,
)

# 풀에서 연결 가져오기
r = redis.Redis(connection_pool=pool)
```

---

## 부록: 주요 포트 정리

| 서비스 | 포트 | 용도 |
|--------|------|------|
| Redis Master | 6379 | 읽기/쓰기 |
| Redis Replica 1 | 6380 | 읽기 전용 |
| Redis Replica 2 | 6381 | 읽기 전용 |
| Sentinel 1 | 26379 | 마스터 감시/페일오버 |
| Sentinel 2 | 26380 | 마스터 감시/페일오버 |
| Sentinel 3 | 26381 | 마스터 감시/페일오버 |
| RedisInsight | 5540 | 웹 UI |
