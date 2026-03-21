##############################################################################
# ■■■ Redis 실습 코드 - 모든 데이터 타입과 고급 기능 ■■■
#
# 이 스크립트는 Redis의 주요 데이터 타입과 고급 기능을 실습합니다.
#
# 사전 준비:
#   pip install redis
#
# 실행 방법:
#   python example.py
#
# 주요 학습 내용:
#   1. String (문자열) - 가장 기본적인 키-값 저장
#   2. Hash (해시) - 필드-값 쌍의 맵 (객체 저장에 적합)
#   3. List (리스트) - 순서가 있는 문자열 목록 (큐/스택)
#   4. Set (집합) - 중복 없는 문자열 모음 (태그, 팔로우)
#   5. Sorted Set (정렬 집합) - 스코어 기반 정렬 (랭킹, 리더보드)
#   6. Pub/Sub (발행/구독) - 실시간 메시지 브로드캐스팅
#   7. Pipeline (파이프라인) - 여러 명령을 한 번에 전송 (성능 최적화)
#   8. Transaction (트랜잭션) - 원자적 명령 실행
##############################################################################

import redis
import time
import json
import threading
from datetime import datetime, timedelta


# ■■■ Redis 연결 설정 ■■■
# docker-compose에서 매핑한 마스터 노드 포트 사용
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = "redis1234"  # redis.conf의 requirepass와 동일
REDIS_DB = 0                  # 사용할 데이터베이스 번호 (0~15)


def get_connection():
    """
    ■■■ Redis 연결 생성 ■■■

    redis.Redis 객체를 생성하여 Redis 서버에 연결합니다.
    decode_responses=True: 바이트 대신 문자열로 응답 받기

    Returns:
        redis.Redis: Redis 클라이언트 인스턴스
    """
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        db=REDIS_DB,
        # 응답을 자동으로 UTF-8 문자열로 디코딩
        decode_responses=True,
        # 소켓 연결 타임아웃 (초)
        socket_connect_timeout=5,
        # 소켓 읽기/쓰기 타임아웃 (초)
        socket_timeout=5,
        # 연결 재시도 횟수
        retry_on_timeout=True,
    )
    # 연결 테스트
    r.ping()
    print(f"[연결] Redis 서버 연결 성공 ({REDIS_HOST}:{REDIS_PORT})")
    return r


def example_string(r):
    """
    ■■■ 1. String (문자열) 데이터 타입 ■■■

    가장 기본적인 키-값 저장 구조
    최대 512MB의 문자열을 저장할 수 있음

    사용 사례:
    - 캐시 (API 응답, 세션 데이터)
    - 카운터 (조회수, 좋아요 수)
    - 분산 락 (SET NX EX 패턴)
    """
    print(f"\n{'='*60}")
    print("■■■ 1. String (문자열) 예제 ■■■")
    print(f"{'='*60}")

    # SET: 키에 값 저장
    r.set("user:name", "홍길동")
    print(f"SET user:name = '홍길동'")

    # GET: 키의 값 조회
    name = r.get("user:name")
    print(f"GET user:name = '{name}'")

    # SET with EX: TTL(만료 시간) 설정 (초 단위)
    # 캐시 구현의 핵심 - 일정 시간 후 자동 삭제
    r.set("cache:token", "abc123xyz", ex=300)  # 5분 후 만료
    print(f"SET cache:token (TTL=300초)")

    # TTL 확인: 남은 만료 시간 (초)
    ttl = r.ttl("cache:token")
    print(f"TTL cache:token = {ttl}초")

    # SETNX (SET if Not eXists): 키가 없을 때만 설정
    # 분산 락 구현에 사용되는 패턴
    result = r.setnx("lock:resource", "process-1")
    print(f"SETNX lock:resource = {result}")  # True (처음 설정)
    result = r.setnx("lock:resource", "process-2")
    print(f"SETNX lock:resource = {result}")  # False (이미 존재)

    # INCR / DECR: 숫자 값 증가/감소 (원자적 연산)
    # 조회수 카운터, 재고 수량 등에 활용
    r.set("counter:views", 0)
    r.incr("counter:views")       # +1
    r.incr("counter:views")       # +1
    r.incrby("counter:views", 10) # +10
    views = r.get("counter:views")
    print(f"카운터: counter:views = {views}")

    # MSET / MGET: 여러 키를 한 번에 설정/조회 (네트워크 왕복 절약)
    r.mset({"user:1:name": "김철수", "user:1:age": "30", "user:1:city": "서울"})
    values = r.mget("user:1:name", "user:1:age", "user:1:city")
    print(f"MGET user:1 = {values}")

    # 정리
    r.delete("user:name", "cache:token", "lock:resource",
             "counter:views", "user:1:name", "user:1:age", "user:1:city")


def example_hash(r):
    """
    ■■■ 2. Hash (해시) 데이터 타입 ■■■

    필드-값 쌍의 맵 구조 (Python dict와 유사)
    하나의 키 아래에 여러 필드를 저장

    사용 사례:
    - 사용자 프로필 저장
    - 설정값 관리
    - 객체 캐시 (JSON보다 메모리 효율적)
    """
    print(f"\n{'='*60}")
    print("■■■ 2. Hash (해시) 예제 ■■■")
    print(f"{'='*60}")

    # HSET: 해시에 필드-값 설정 (여러 필드 동시 설정 가능)
    r.hset("user:100", mapping={
        "name": "이영희",
        "email": "yhlee@example.com",
        "age": "28",
        "city": "부산",
        "signup_date": datetime.now().isoformat(),
    })
    print("HSET user:100 (5개 필드 설정)")

    # HGET: 특정 필드 값 조회
    name = r.hget("user:100", "name")
    print(f"HGET user:100 name = '{name}'")

    # HGETALL: 모든 필드-값 조회 (주의: 키에 필드가 많으면 성능 저하)
    user_data = r.hgetall("user:100")
    print(f"HGETALL user:100 = {user_data}")

    # HMGET: 여러 필드 동시 조회
    values = r.hmget("user:100", "name", "email", "city")
    print(f"HMGET user:100 [name, email, city] = {values}")

    # HINCRBY: 해시 필드의 숫자 값 증가
    r.hincrby("user:100", "age", 1)
    age = r.hget("user:100", "age")
    print(f"HINCRBY user:100 age +1 = {age}")

    # HEXISTS: 필드 존재 여부 확인
    exists = r.hexists("user:100", "phone")
    print(f"HEXISTS user:100 phone = {exists}")  # False

    # HDEL: 특정 필드 삭제
    r.hdel("user:100", "city")
    print("HDEL user:100 city")

    # HLEN: 해시의 필드 수
    length = r.hlen("user:100")
    print(f"HLEN user:100 = {length}")

    # 정리
    r.delete("user:100")


def example_list(r):
    """
    ■■■ 3. List (리스트) 데이터 타입 ■■■

    순서가 있는 문자열 목록 (Linked List 기반)
    양쪽 끝에서 O(1) 삽입/삭제 가능

    사용 사례:
    - 메시지 큐 (LPUSH + RPOP)
    - 최근 활동 로그
    - 스택 (LPUSH + LPOP)
    - 타임라인 (최근 N개 조회)
    """
    print(f"\n{'='*60}")
    print("■■■ 3. List (리스트) 예제 ■■■")
    print(f"{'='*60}")

    # LPUSH: 왼쪽(앞)에 요소 추가
    r.lpush("queue:tasks", "작업1", "작업2", "작업3")
    print("LPUSH queue:tasks [작업3, 작업2, 작업1] (왼쪽부터 삽입)")

    # RPUSH: 오른쪽(뒤)에 요소 추가
    r.rpush("queue:tasks", "작업4", "작업5")
    print("RPUSH queue:tasks [작업4, 작업5] (오른쪽에 삽입)")

    # LRANGE: 범위 조회 (0부터 시작, -1은 마지막)
    all_tasks = r.lrange("queue:tasks", 0, -1)
    print(f"LRANGE queue:tasks 0 -1 = {all_tasks}")

    # LLEN: 리스트 길이
    length = r.llen("queue:tasks")
    print(f"LLEN queue:tasks = {length}")

    # RPOP: 오른쪽(뒤)에서 요소 제거 후 반환 (큐의 dequeue)
    task = r.rpop("queue:tasks")
    print(f"RPOP queue:tasks = '{task}' (큐에서 꺼냄)")

    # LPOP: 왼쪽(앞)에서 요소 제거 후 반환 (스택의 pop)
    task = r.lpop("queue:tasks")
    print(f"LPOP queue:tasks = '{task}' (스택에서 꺼냄)")

    # LINDEX: 인덱스로 요소 조회 (O(N) 주의)
    task = r.lindex("queue:tasks", 0)
    print(f"LINDEX queue:tasks 0 = '{task}'")

    # LTRIM: 범위 밖의 요소 삭제 (최근 N개만 유지에 유용)
    # 최근 활동 로그에서 최근 100개만 유지하는 패턴:
    # LPUSH + LTRIM 0 99
    r.ltrim("queue:tasks", 0, 1)
    remaining = r.lrange("queue:tasks", 0, -1)
    print(f"LTRIM queue:tasks 0 1 → 남은 요소: {remaining}")

    # BRPOP: 블로킹 POP (리스트가 비어있으면 대기)
    # 메시지 큐 구현의 핵심 - 새 메시지가 올 때까지 블로킹
    # timeout=1: 최대 1초 대기
    r.lpush("queue:blocking", "블로킹메시지")
    result = r.brpop("queue:blocking", timeout=1)
    print(f"BRPOP queue:blocking = {result}")

    # 정리
    r.delete("queue:tasks", "queue:blocking")


def example_set(r):
    """
    ■■■ 4. Set (집합) 데이터 타입 ■■■

    중복 없는 문자열 모음 (순서 없음)
    합집합, 교집합, 차집합 등 집합 연산 지원

    사용 사례:
    - 태그 시스템
    - 팔로잉/팔로워 관계
    - 고유 방문자 추적
    - 블랙리스트/화이트리스트
    """
    print(f"\n{'='*60}")
    print("■■■ 4. Set (집합) 예제 ■■■")
    print(f"{'='*60}")

    # SADD: 집합에 멤버 추가
    r.sadd("tags:post:1", "python", "redis", "docker", "backend")
    r.sadd("tags:post:2", "python", "fastapi", "redis", "api")
    print("SADD tags:post:1 = {python, redis, docker, backend}")
    print("SADD tags:post:2 = {python, fastapi, redis, api}")

    # SMEMBERS: 모든 멤버 조회
    tags = r.smembers("tags:post:1")
    print(f"SMEMBERS tags:post:1 = {tags}")

    # SCARD: 멤버 수
    count = r.scard("tags:post:1")
    print(f"SCARD tags:post:1 = {count}")

    # SISMEMBER: 멤버 존재 여부 확인 (O(1))
    is_member = r.sismember("tags:post:1", "python")
    print(f"SISMEMBER tags:post:1 'python' = {is_member}")

    # SINTER: 교집합 (두 게시물의 공통 태그)
    common = r.sinter("tags:post:1", "tags:post:2")
    print(f"SINTER (공통 태그) = {common}")

    # SUNION: 합집합 (모든 태그)
    all_tags = r.sunion("tags:post:1", "tags:post:2")
    print(f"SUNION (모든 태그) = {all_tags}")

    # SDIFF: 차집합 (post:1에만 있는 태그)
    diff = r.sdiff("tags:post:1", "tags:post:2")
    print(f"SDIFF tags:post:1 - tags:post:2 = {diff}")

    # SRANDMEMBER: 무작위 멤버 조회 (삭제하지 않음)
    random_tag = r.srandmember("tags:post:1")
    print(f"SRANDMEMBER tags:post:1 = '{random_tag}'")

    # SPOP: 무작위 멤버 제거 후 반환
    popped = r.spop("tags:post:1")
    print(f"SPOP tags:post:1 = '{popped}'")

    # 정리
    r.delete("tags:post:1", "tags:post:2")


def example_sorted_set(r):
    """
    ■■■ 5. Sorted Set (정렬 집합) 데이터 타입 ■■■

    각 멤버에 스코어(점수)가 부여된 정렬 집합
    스코어 기준으로 자동 정렬됨

    사용 사례:
    - 게임 리더보드 (랭킹)
    - 우선순위 큐
    - 시간순 이벤트 (스코어=타임스탬프)
    - 실시간 인기 검색어
    """
    print(f"\n{'='*60}")
    print("■■■ 5. Sorted Set (정렬 집합) 예제 ■■■")
    print(f"{'='*60}")

    # ZADD: 멤버와 스코어 추가
    # 리더보드 예시: 플레이어 점수 등록
    r.zadd("leaderboard", {
        "플레이어A": 1500,
        "플레이어B": 2300,
        "플레이어C": 1800,
        "플레이어D": 3100,
        "플레이어E": 2700,
    })
    print("ZADD leaderboard (5명 등록)")

    # ZRANGE: 스코어 오름차순 정렬 조회 (낮은 점수부터)
    low_to_high = r.zrange("leaderboard", 0, -1, withscores=True)
    print(f"ZRANGE (오름차순): {low_to_high}")

    # ZREVRANGE: 스코어 내림차순 정렬 조회 (높은 점수부터 = 랭킹)
    ranking = r.zrevrange("leaderboard", 0, -1, withscores=True)
    print(f"ZREVRANGE (랭킹):")
    for rank, (player, score) in enumerate(ranking, 1):
        print(f"  {rank}위: {player} ({int(score)}점)")

    # ZRANK / ZREVRANK: 멤버의 순위 조회 (0부터 시작)
    rank = r.zrevrank("leaderboard", "플레이어B")
    print(f"ZREVRANK 플레이어B = {rank + 1}위")

    # ZSCORE: 멤버의 스코어 조회
    score = r.zscore("leaderboard", "플레이어D")
    print(f"ZSCORE 플레이어D = {int(score)}점")

    # ZINCRBY: 스코어 증가 (게임 중 점수 추가)
    new_score = r.zincrby("leaderboard", 500, "플레이어A")
    print(f"ZINCRBY 플레이어A +500 = {int(new_score)}점")

    # ZRANGEBYSCORE: 스코어 범위로 조회
    mid_range = r.zrangebyscore("leaderboard", 2000, 3000, withscores=True)
    print(f"ZRANGEBYSCORE 2000~3000: {mid_range}")

    # ZCARD: 멤버 수
    count = r.zcard("leaderboard")
    print(f"ZCARD leaderboard = {count}")

    # ZREM: 멤버 삭제
    r.zrem("leaderboard", "플레이어E")
    print("ZREM 플레이어E (삭제)")

    # 정리
    r.delete("leaderboard")


def example_pubsub(r):
    """
    ■■■ 6. Pub/Sub (발행/구독) ■■■

    실시간 메시지 브로드캐스팅 패턴
    Publisher가 채널에 메시지를 발행하면, 해당 채널을 구독한 모든 Subscriber가 수신

    주의사항:
    - 메시지는 영속화되지 않음 (구독 시점 이후 메시지만 수신)
    - 구독자가 없으면 메시지는 사라짐
    - 신뢰성이 필요하면 Redis Streams 사용 권장

    사용 사례:
    - 실시간 알림
    - 채팅
    - 이벤트 브로드캐스트
    """
    print(f"\n{'='*60}")
    print("■■■ 6. Pub/Sub (발행/구독) 예제 ■■■")
    print(f"{'='*60}")

    # Pub/Sub은 별도의 연결이 필요 (구독 중에는 다른 명령 사용 불가)
    subscriber_conn = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT,
        password=REDIS_PASSWORD, decode_responses=True
    )

    # PubSub 객체 생성
    pubsub = subscriber_conn.pubsub()

    # 채널 구독
    channel_name = "notifications"
    pubsub.subscribe(channel_name)
    print(f"채널 '{channel_name}' 구독 시작")

    # 구독 확인 메시지 소비
    pubsub.get_message()

    # 메시지 발행 (별도 연결로 발행)
    messages = [
        "안녕하세요! 새 알림입니다.",
        "서버 점검 예정: 오후 2시",
        "업데이트 완료!",
    ]

    for msg in messages:
        # PUBLISH: 채널에 메시지 발행
        # 반환값: 메시지를 수신한 구독자 수
        receivers = r.publish(channel_name, msg)
        print(f"PUBLISH '{channel_name}' → '{msg}' (수신자: {receivers}명)")

    # 발행된 메시지 수신
    time.sleep(0.1)  # 메시지 전달 대기
    received_count = 0
    while True:
        message = pubsub.get_message()
        if message is None:
            break
        # message 타입:
        # - 'subscribe': 구독 확인
        # - 'message': 실제 메시지
        # - 'unsubscribe': 구독 해제 확인
        if message["type"] == "message":
            received_count += 1
            print(f"  수신: 채널={message['channel']}, 데이터='{message['data']}'")

    print(f"총 {received_count}건 수신 완료")

    # 패턴 구독: 와일드카드로 여러 채널 구독
    # psubscribe("news.*") → news.sports, news.tech 등 모두 구독
    pubsub.psubscribe("events.*")
    pubsub.get_message()  # 구독 확인 소비

    r.publish("events.login", "사용자 로그인")
    r.publish("events.purchase", "상품 구매")

    time.sleep(0.1)
    while True:
        message = pubsub.get_message()
        if message is None:
            break
        if message["type"] == "pmessage":
            print(f"  패턴 수신: 패턴={message['pattern']}, 채널={message['channel']}, 데이터='{message['data']}'")

    # 구독 해제 및 정리
    pubsub.unsubscribe()
    pubsub.punsubscribe()
    pubsub.close()
    subscriber_conn.close()


def example_pipeline(r):
    """
    ■■■ 7. Pipeline (파이프라인) ■■■

    여러 명령을 한 번에 서버로 전송하여 네트워크 왕복(RTT)을 최소화

    일반 방식: 명령1 → 응답1 → 명령2 → 응답2 → ... (N번 왕복)
    파이프라인: 명령1+명령2+...+명령N → 응답1+응답2+...+응답N (1번 왕복)

    성능 향상: 네트워크 지연이 클수록 효과 극대화
    주의: 원자성을 보장하지 않음 (원자성이 필요하면 트랜잭션 사용)
    """
    print(f"\n{'='*60}")
    print("■■■ 7. Pipeline (파이프라인) 예제 ■■■")
    print(f"{'='*60}")

    # ── 파이프라인 없이 개별 명령 실행 ──
    start = time.time()
    for i in range(100):
        r.set(f"bench:normal:{i}", f"value-{i}")
    normal_time = time.time() - start
    print(f"개별 명령 100회: {normal_time:.4f}초")

    # ── 파이프라인으로 일괄 명령 실행 ──
    start = time.time()
    # pipeline() 컨텍스트 매니저 사용 (with문 끝에서 자동 execute)
    pipe = r.pipeline()
    for i in range(100):
        # 명령을 파이프라인 버퍼에 추가 (아직 전송하지 않음)
        pipe.set(f"bench:pipeline:{i}", f"value-{i}")
    # execute(): 버퍼의 모든 명령을 한 번에 전송하고 응답 수신
    results = pipe.execute()
    pipeline_time = time.time() - start
    print(f"파이프라인 100회: {pipeline_time:.4f}초")
    print(f"성능 향상: {normal_time / pipeline_time:.1f}배 빠름")

    # 파이프라인 결과 확인 (각 명령의 반환값 리스트)
    print(f"파이프라인 결과 수: {len(results)}")

    # ── 파이프라인으로 GET 명령 일괄 실행 ──
    pipe = r.pipeline()
    for i in range(5):
        pipe.get(f"bench:pipeline:{i}")
    values = pipe.execute()
    print(f"파이프라인 GET 결과: {values}")

    # 정리
    pipe = r.pipeline()
    for i in range(100):
        pipe.delete(f"bench:normal:{i}", f"bench:pipeline:{i}")
    pipe.execute()


def example_transaction(r):
    """
    ■■■ 8. Transaction (트랜잭션) ■■■

    MULTI/EXEC로 여러 명령을 원자적으로 실행
    중간에 다른 클라이언트의 명령이 끼어들지 않음

    WATCH: 낙관적 락 (Optimistic Locking)
    - WATCH된 키가 EXEC 전에 다른 클라이언트에 의해 변경되면
      트랜잭션이 실패 (WatchError 발생)
    - 재시도 로직을 구현하여 처리

    사용 사례:
    - 계좌 이체 (잔액 확인 → 출금 → 입금을 원자적으로)
    - 재고 차감 (재고 확인 → 차감을 원자적으로)
    """
    print(f"\n{'='*60}")
    print("■■■ 8. Transaction (트랜잭션) 예제 ■■■")
    print(f"{'='*60}")

    # ── 기본 트랜잭션 (MULTI/EXEC) ──
    # pipeline(transaction=True)가 기본값
    print("\n[기본 트랜잭션]")
    pipe = r.pipeline(transaction=True)
    pipe.set("tx:key1", "value1")
    pipe.set("tx:key2", "value2")
    pipe.incr("tx:counter")
    # execute() 시 MULTI → SET → SET → INCR → EXEC 순서로 전송
    results = pipe.execute()
    print(f"트랜잭션 결과: {results}")

    # ── WATCH를 사용한 낙관적 락 ──
    # 계좌 이체 시뮬레이션
    print("\n[WATCH + 트랜잭션: 계좌 이체]")
    r.set("account:A", "10000")  # A 계좌 잔액 10,000원
    r.set("account:B", "5000")   # B 계좌 잔액 5,000원
    transfer_amount = 3000       # 이체 금액 3,000원

    # WATCH로 두 계좌를 감시
    # WATCH 이후 EXEC 전에 다른 클라이언트가 이 키를 변경하면 트랜잭션 실패
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # watch()로 키 감시 시작
            pipe = r.pipeline(transaction=True)
            pipe.watch("account:A", "account:B")

            # 현재 잔액 조회 (WATCH 상태에서 일반 명령 실행)
            balance_a = int(pipe.get("account:A"))
            balance_b = int(pipe.get("account:B"))

            if balance_a < transfer_amount:
                print("  잔액 부족!")
                pipe.unwatch()
                break

            # MULTI 시작 (이후 명령은 버퍼에 저장)
            pipe.multi()
            pipe.set("account:A", balance_a - transfer_amount)
            pipe.set("account:B", balance_b + transfer_amount)

            # EXEC: 트랜잭션 실행
            # WATCH된 키가 변경되었으면 여기서 WatchError 발생
            pipe.execute()
            print(f"  이체 성공! A: {balance_a} → {balance_a - transfer_amount}, "
                  f"B: {balance_b} → {balance_b + transfer_amount}")
            break

        except redis.WatchError:
            # 다른 클라이언트가 계좌 잔액을 변경한 경우
            print(f"  충돌 감지! 재시도 ({attempt + 1}/{max_retries})")
            continue

    # 최종 잔액 확인
    print(f"  최종 잔액: A={r.get('account:A')}, B={r.get('account:B')}")

    # 정리
    r.delete("tx:key1", "tx:key2", "tx:counter", "account:A", "account:B")


def main():
    """
    ■■■ 메인 실행 함수 ■■■

    모든 Redis 데이터 타입과 기능을 순서대로 실습합니다.
    """
    print("=" * 60)
    print("■■■ Redis 실습 시작 ■■■")
    print("=" * 60)

    try:
        # Redis 연결
        r = get_connection()

        # 1. String (문자열)
        example_string(r)

        # 2. Hash (해시)
        example_hash(r)

        # 3. List (리스트)
        example_list(r)

        # 4. Set (집합)
        example_set(r)

        # 5. Sorted Set (정렬 집합)
        example_sorted_set(r)

        # 6. Pub/Sub (발행/구독)
        example_pubsub(r)

        # 7. Pipeline (파이프라인)
        example_pipeline(r)

        # 8. Transaction (트랜잭션)
        example_transaction(r)

        print(f"\n{'='*60}")
        print("■■■ 모든 Redis 실습 완료! ■■■")
        print(f"{'='*60}")

    except redis.ConnectionError as e:
        print(f"[오류] Redis 연결 실패: {e}")
        print("  → docker-compose up -d 로 Redis를 먼저 시작하세요.")
    except Exception as e:
        print(f"[오류] 예상치 못한 오류: {e}")
    finally:
        if "r" in locals():
            r.close()
            print("[종료] Redis 연결이 종료되었습니다.")


if __name__ == "__main__":
    main()
