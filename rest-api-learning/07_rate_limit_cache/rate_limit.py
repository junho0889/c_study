# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   REST API 학습 07단계: 속도 제한과 캐싱
#   ─ Token Bucket, Sliding Window, ETag, Last-Modified, Cache-Control ─
#
#   API를 아무리 많이 호출해도 서버가 견딜 수 있도록 "속도 제한"을 걸고,
#   같은 데이터를 반복해서 보내지 않도록 "캐싱"을 활용합니다.
#
#   ■ 실행: python rate_limit.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import time
import hashlib
import json
from collections import deque


def lesson1_why_rate_limit():
    # =========================================================================
    #   레슨 1 — 왜 속도 제한이 필요한가?
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 1 : 속도 제한이 필요한 이유             │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Rate Limiting = "1분에 최대 60번만 요청할 수 있습니다"
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     놀이공원 놀이기구에 줄을 서야 하는 이유와 같습니다.
    #     모든 사람이 동시에 타면 기구가 고장 나니까
    #     "10분에 30명씩만" 태우는 것!
    #
    #   없으면 생기는 문제:
    #     1. 서버 과부하 → 모든 사용자에게 느려짐
    #     2. 악성 봇이 초당 1000번 요청 → 서버 다운
    #     3. 비용 폭증 → 클라우드 요금 폭탄
    #

    print("  [상황 시뮬레이션] 속도 제한 없이 10명이 동시 요청")
    server_capacity = 5  # 서버가 동시에 처리할 수 있는 수
    requests = 10

    print(f"    서버 동시 처리 용량: {server_capacity}명")
    print(f"    동시 요청 수:       {requests}명")
    print(f"    결과: {requests - server_capacity}명은 에러를 받거나 서버가 느려집니다!")
    print()
    print("  → 속도 제한을 걸면: 초과 요청에 429 Too Many Requests 응답")
    print()

    # Rate Limit 응답 헤더 예시
    headers = {
        "X-RateLimit-Limit": "60",       # 1분에 최대 60번
        "X-RateLimit-Remaining": "45",   # 남은 횟수
        "X-RateLimit-Reset": "1711036800",  # 리셋 시간 (Unix timestamp)
        "Retry-After": "15",             # 15초 후 재시도 (429일 때)
    }

    print("  속도 제한 관련 HTTP 응답 헤더:")
    for key, value in headers.items():
        print(f"    {key}: {value}")
    print()


def lesson2_token_bucket():
    # =========================================================================
    #   레슨 2 — Token Bucket 알고리즘
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 2 : Token Bucket 알고리즘              │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Token Bucket = "양동이에 토큰을 채워 두고 요청마다 하나씩 꺼내 쓰기"
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     게임 센터 코인통과 같습니다.
    #     - 코인통에 최대 10개의 코인이 들어감 (버킷 크기)
    #     - 게임을 하면 코인 1개를 꺼냄 (요청 1번)
    #     - 1초마다 코인이 1개씩 자동 충전됨 (토큰 충전 속도)
    #     - 코인이 0이면 게임을 못 함! (429 에러)
    #     - 코인이 꽉 차면 더 이상 충전 안 됨 (최대치)
    #
    #     장점: 순간적으로 많이 쓸 수 있음 (버스트 허용)
    #

    class TokenBucket:
        def __init__(self, capacity, refill_rate):
            self.capacity = capacity          # 양동이 크기
            self.tokens = capacity             # 현재 토큰 수 (처음엔 가득)
            self.refill_rate = refill_rate      # 초당 충전 토큰 수
            self.last_refill = time.time()

        def _refill(self):
            """시간 경과에 따라 토큰 충전"""
            now = time.time()
            elapsed = now - self.last_refill
            new_tokens = elapsed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.last_refill = now

        def allow_request(self):
            """요청 허용 여부 확인"""
            self._refill()
            if self.tokens >= 1:
                self.tokens -= 1
                return True, int(self.tokens)
            return False, 0

    # 양동이 크기 5, 초당 2개 충전
    bucket = TokenBucket(capacity=5, refill_rate=2)

    print("  Token Bucket: 용량=5, 충전속도=2개/초")
    print()

    # 빠르게 8번 요청 (버스트)
    print("  [빠르게 8번 요청]")
    for i in range(8):
        allowed, remaining = bucket.allow_request()
        status = "[O] 허용" if allowed else "[X] 거부 (429)"
        print(f"    요청 {i + 1}: {status}  (남은 토큰: {remaining})")
    print()

    # 잠시 기다린 후
    print("  [1초 대기 후 토큰 충전...]")
    time.sleep(1)
    allowed, remaining = bucket.allow_request()
    status = "[O] 허용" if allowed else "[X] 거부"
    print(f"    요청: {status}  (남은 토큰: {remaining})")
    print()


def lesson3_sliding_window():
    # =========================================================================
    #   레슨 3 — Sliding Window 알고리즘
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 3 : Sliding Window 알고리즘            │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Sliding Window = "최근 N초 동안의 요청 수를 세는 방식"
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     CCTV 재생 영상의 "최근 1분" 부분만 보는 것과 같습니다.
    #     시간이 흐르면 오래된 요청은 자동으로 창 밖으로 빠져나갑니다.
    #
    #     ─────────── 시간 축 ──────────→
    #     [  창 밖  ][    현재 창(1분)    ]
    #     오래된 요청은 무시  최근 요청만 카운트
    #

    class SlidingWindow:
        def __init__(self, max_requests, window_seconds):
            self.max_requests = max_requests
            self.window_seconds = window_seconds
            self.timestamps = deque()  # 요청 시각 기록

        def allow_request(self):
            """요청 허용 여부 확인"""
            now = time.time()

            # 창 밖으로 나간 오래된 요청 제거
            while self.timestamps and self.timestamps[0] < now - self.window_seconds:
                self.timestamps.popleft()

            if len(self.timestamps) < self.max_requests:
                self.timestamps.append(now)
                return True, self.max_requests - len(self.timestamps)
            return False, 0

    # 2초 창에 최대 3번
    window = SlidingWindow(max_requests=3, window_seconds=2)

    print("  Sliding Window: 2초 동안 최대 3번")
    print()

    print("  [빠르게 5번 요청]")
    for i in range(5):
        allowed, remaining = window.allow_request()
        status = "[O] 허용" if allowed else "[X] 거부 (429)"
        print(f"    요청 {i + 1}: {status}  (남은 횟수: {remaining})")
    print()

    print("  [2초 대기 후 창이 리셋...]")
    time.sleep(2)
    allowed, remaining = window.allow_request()
    status = "[O] 허용" if allowed else "[X] 거부"
    print(f"    요청: {status}  (남은 횟수: {remaining})")
    print()

    print("  Token Bucket vs Sliding Window:")
    print("    Token Bucket   → 버스트를 허용하되 평균 속도를 제한")
    print("    Sliding Window → 정확하게 '최근 N초에 M번'을 보장")
    print()


def lesson4_etag_caching():
    # =========================================================================
    #   레슨 4 — ETag 캐싱
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 4 : ETag 캐싱                         │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ ETag = 데이터의 "지문"(해시)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     책의 "개정판 번호"와 같습니다.
    #     "이 책이 3판이라면, 내가 가진 것도 3판이니 새로 안 사도 돼!"
    #     → 서버가 "3판이에요" 하면 클라이언트는 다시 받을 필요 없음!
    #
    #   흐름:
    #     1. 첫 요청: GET /students/1 → 서버: 200 + ETag: "abc123"
    #     2. 재요청: GET /students/1 + If-None-Match: "abc123"
    #        - 데이터 변경 없음 → 304 Not Modified (본문 없이!)
    #        - 데이터 변경됨   → 200 + 새 데이터 + 새 ETag
    #

    student_data = {"id": 1, "name": "민수", "score": 92}

    def generate_etag(data):
        """데이터의 해시를 ETag로 사용"""
        content = json.dumps(data, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()[:16]

    current_etag = generate_etag(student_data)

    # 첫 번째 요청
    print("  [1] 첫 요청: GET /students/1")
    print(f"      응답: 200 OK")
    print(f"      ETag: \"{current_etag}\"")
    print(f"      Body: {json.dumps(student_data, ensure_ascii=False)}")
    print()

    # 두 번째 요청 (데이터 변경 없음)
    client_etag = current_etag
    print(f"  [2] 재요청: GET /students/1")
    print(f"      If-None-Match: \"{client_etag}\"")
    if client_etag == current_etag:
        print(f"      응답: 304 Not Modified (본문 없음 → 네트워크 절약!)")
    print()

    # 데이터가 변경된 경우
    student_data["score"] = 95
    new_etag = generate_etag(student_data)
    print(f"  [3] 점수가 변경된 후 재요청: GET /students/1")
    print(f"      If-None-Match: \"{client_etag}\"")
    if client_etag != new_etag:
        print(f"      응답: 200 OK (데이터가 바뀌었으니 새로 보내줌!)")
        print(f"      새 ETag: \"{new_etag}\"")
        print(f"      Body: {json.dumps(student_data, ensure_ascii=False)}")
    print()


def lesson5_last_modified():
    # =========================================================================
    #   레슨 5 — Last-Modified / If-Modified-Since
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 5 : Last-Modified 캐싱                │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Last-Modified = "이 데이터가 마지막으로 바뀐 시간"
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     파일의 "수정한 날짜"를 보는 것과 같습니다.
    #     "내가 마지막으로 본 게 3월 15일인데, 그 뒤로 바뀐 거 있어?"
    #     → 없으면 304, 있으면 200 + 새 데이터
    #

    last_modified = "Fri, 21 Mar 2026 10:00:00 GMT"

    print("  [1] 첫 요청: GET /students")
    print(f"      응답 헤더: Last-Modified: {last_modified}")
    print()

    print("  [2] 재요청:")
    print(f"      요청 헤더: If-Modified-Since: {last_modified}")
    print(f"      서버 확인: 그 이후로 변경 없음!")
    print(f"      응답: 304 Not Modified")
    print()

    print("  ETag vs Last-Modified:")
    print("    ETag          → 더 정확함 (내용 자체의 해시)")
    print("    Last-Modified → 더 간단함 (시간만 비교)")
    print("    둘 다 사용해도 됩니다! ETag가 우선순위가 더 높습니다.")
    print()


def lesson6_cache_control():
    # =========================================================================
    #   레슨 6 — Cache-Control 헤더
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 6 : Cache-Control 헤더                │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Cache-Control = "이 응답을 얼마나 오래 기억해도 되는지" 알려 주는 헤더
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유:
    #     음식의 유통기한과 같습니다!
    #     "이 우유는 7일간 보관 가능" → max-age=604800
    #     "이 회는 보관 불가, 바로 드세요" → no-cache
    #
    #   주요 지시어:
    #     max-age=3600  → 1시간 동안 캐시 사용 가능
    #     no-cache      → 매번 서버에 확인해야 함 (캐시는 해도 됨)
    #     no-store      → 절대 캐시하지 마! (비밀 데이터)
    #     public        → 모두가 캐시 가능 (CDN 포함)
    #     private       → 해당 사용자만 캐시 가능 (CDN 불가)
    #

    cache_examples = [
        {
            "url": "GET /students (목록)",
            "header": "Cache-Control: public, max-age=60",
            "meaning": "모든 곳에서 60초간 캐시 가능 (자주 바뀌지 않는 목록)",
        },
        {
            "url": "GET /students/me (내 정보)",
            "header": "Cache-Control: private, max-age=300",
            "meaning": "이 사용자의 브라우저에서만 5분간 캐시 (개인 정보)",
        },
        {
            "url": "GET /students/me/password",
            "header": "Cache-Control: no-store",
            "meaning": "절대 캐시 금지! (비밀번호 같은 민감 정보)",
        },
        {
            "url": "GET /images/logo.png",
            "header": "Cache-Control: public, max-age=31536000",
            "meaning": "1년간 캐시 (거의 바뀌지 않는 로고 이미지)",
        },
    ]

    for example in cache_examples:
        print(f"  {example['url']}")
        print(f"    {example['header']}")
        print(f"    → {example['meaning']}")
        print()

    print("  요약:")
    print("    정적 파일(이미지, CSS) → max-age 길게")
    print("    자주 바뀌는 데이터     → max-age 짧게 또는 no-cache")
    print("    민감한 데이터          → no-store")
    print()


def lesson7_conditional_request_304():
    # =========================================================================
    #   레슨 7 — 조건부 요청과 304 응답
    # =========================================================================
    print("┌──────────────────────────────────────────────┐")
    print("│  레슨 7 : 조건부 요청 (304 Not Modified)     │")
    print("└──────────────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 전체 흐름을 한눈에 보기
    # ─────────────────────────────────────────────────────────────────────
    #
    #   ┌──────────┐                     ┌──────────┐
    #   │ 클라이언트│                     │   서버   │
    #   └────┬─────┘                     └────┬─────┘
    #        │  GET /students                 │
    #        │──────────────────────────────→ │
    #        │  200 OK + ETag: "abc"          │
    #        │  + Body: [{...}, {...}]        │
    #        │ ←────────────────────────────  │
    #        │                                │
    #        │  GET /students                 │
    #        │  If-None-Match: "abc"          │
    #        │──────────────────────────────→ │
    #        │  304 Not Modified (본문 없음!) │
    #        │ ←────────────────────────────  │
    #        │                                │
    #        │  → 클라이언트는 기존 캐시 사용! │
    #

    def simulate_conditional_request(client_cache, server_data):
        """조건부 요청 시뮬레이션"""
        server_etag = hashlib.md5(
            json.dumps(server_data, sort_keys=True).encode()
        ).hexdigest()[:16]

        if client_cache and client_cache.get("etag") == server_etag:
            return {
                "status": 304,
                "body": None,
                "message": "Not Modified — 기존 캐시를 사용하세요!",
            }
        return {
            "status": 200,
            "body": server_data,
            "etag": server_etag,
            "message": "새 데이터를 보냅니다.",
        }

    server_data = [{"id": 1, "name": "민수"}, {"id": 2, "name": "지우"}]

    # 첫 요청 (캐시 없음)
    print("  [1] 첫 요청 (캐시 없음)")
    r1 = simulate_conditional_request(None, server_data)
    print(f"      상태: {r1['status']} — {r1['message']}")
    client_cache = {"etag": r1["etag"], "data": r1["body"]}
    print()

    # 재요청 (데이터 동일)
    print("  [2] 재요청 (데이터 변경 없음)")
    r2 = simulate_conditional_request(client_cache, server_data)
    print(f"      상태: {r2['status']} — {r2['message']}")
    print(f"      → 네트워크 대역폭 절약! 본문을 다시 보내지 않았습니다.")
    print()

    # 데이터 변경 후 요청
    server_data.append({"id": 3, "name": "서연"})
    print("  [3] 데이터 변경 후 재요청")
    r3 = simulate_conditional_request(client_cache, server_data)
    print(f"      상태: {r3['status']} — {r3['message']}")
    print()

    print("  핵심: 304를 잘 활용하면 서버 부하와 네트워크 비용을 크게 줄일 수 있습니다!")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("  REST API 07단계 : 속도 제한과 캐싱")
    print("=" * 72)
    print()

    lesson1_why_rate_limit()
    lesson2_token_bucket()
    lesson3_sliding_window()
    lesson4_etag_caching()
    lesson5_last_modified()
    lesson6_cache_control()
    lesson7_conditional_request_304()
