# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [데이터 연계] 학습 14단계: Rate Limit & Caching
#   ─ 토큰 버킷 · 슬라이딩 윈도우 · Redis · CDN · HTTP cache ─
#   ■ 실행 방법: python 14_rate_limit_cache.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 왜 Rate Limit 인가 — 보호 / 비용 / 공정성
#   2. 알고리즘: Fixed window / Sliding / Token bucket / Leaky bucket
#   3. 분산 환경의 Rate Limit — Redis 의 역할
#   4. HTTP Cache 헤더 (Cache-Control, ETag, Vary)
#   5. CDN 캐시 (CloudFront / Cloudflare)
#   6. 어플리케이션 캐시 (Redis / Memcached / in-process)
#   7. 실전: 토큰버킷 손코딩
#
# ─────────────────────────────────────────────────────────────────────────

import math
import time


def lesson1_why_rate_limit():
    # =========================================================================
    #   레슨 1 — 왜 Rate Limit
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 왜 Rate Limit              │")
    print("└──────────────────────────────────────┘")
    # ■ 보호: 폭주 트래픽 / 봇 / DDoS 차단
    # ■ 비용: 외부 API 호출 비용/쿼터 보호
    # ■ 공정성: 한 사용자가 자원을 독점하지 못하게
    # ■ 시그널: 429 Too Many Requests + Retry-After
    print(" Rate Limit = 시스템 안정의 ‘완충재’.  운영 첫 인프라 중 하나.")
    print()


def lesson2_algorithms():
    # =========================================================================
    #   레슨 2 — 알고리즘
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : 4 가지 알고리즘            │")
    print("└──────────────────────────────────────┘")
    # ■ Fixed window:
    #   - 60초마다 카운터 리셋. 단순. ‘경계 버스트’ 문제.
    #
    # ■ Sliding window:
    #   - 최근 60초의 가중 카운트. fixed 의 경계 문제 완화.
    #
    # ■ Token bucket:
    #   - 일정 속도(예: 10/s) 로 토큰 채움. 요청 시 토큰 1 개 소모. 비어있으면 거부.
    #   - 짧은 burst 허용, 장기 평균은 제한.
    #
    # ■ Leaky bucket:
    #   - 큐가 일정 속도로만 빠짐. 초과는 즉시 거부 or queue.
    #   - 출력률(throughput) 의 ‘선형 제한’.
    print(" 인기 = Token bucket.  burst 허용 + 평균 제한, 사용자 경험 좋음.")
    print()


def lesson3_distributed():
    # =========================================================================
    #   레슨 3 — 분산 Rate Limit
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : 분산 환경                  │")
    print("└──────────────────────────────────────┘")
    # ■ 문제:
    #   - 여러 서버가 같은 사용자에 대해 ‘각자’ 카운트 → 합치면 한도 초과
    #
    # ■ 해법:
    #   - 중앙 Redis 에 카운터/토큰 저장
    #   - Redis Lua 스크립트로 원자적 increment + TTL
    #   - 또는 게이트웨이(Envoy/Kong/Nginx) 가 토큰 버킷 분산 구현
    #
    # ■ 성능 팁:
    #   - “정확한 한도” 가 절대 필요한 게 아니면 약간 느슨해도 OK (운영 단순성 ↑)
    print(" 분산 Rate Limit = 중앙 저장소 + 원자적 연산. 정확도 vs 단순성 trade-off.")
    print()


def lesson4_http_cache():
    # =========================================================================
    #   레슨 4 — HTTP cache 헤더
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : HTTP cache                 │")
    print("└──────────────────────────────────────┘")
    # ■ Cache-Control: max-age=600, public, s-maxage=86400
    # ■ ETag: "v123"  → 다음 요청 If-None-Match: "v123" → 304 Not Modified
    # ■ Last-Modified / If-Modified-Since
    # ■ Vary: Accept-Language, Accept-Encoding  ← 응답이 헤더에 따라 달라질 때 명시
    # ■ Cache-Control: private — 사용자별 응답은 CDN/공유 캐시 금지
    #
    # ■ 자주 발생하는 사고:
    #   - 로그인 응답에 Cache-Control 미설정 → CDN 이 다른 사용자에게 표시
    print(" HTTP cache 는 ‘조회 비용의 90% 해결사’. 단, ‘무엇을’ ‘누가’ 캐시할지 명확히.")
    print()


def lesson5_cdn():
    # =========================================================================
    #   레슨 5 — CDN
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : CDN                        │")
    print("└──────────────────────────────────────┘")
    # ■ CDN: 전 세계 엣지에서 캐시 + TLS 종료 + WAF
    # ■ Origin Shield: 오리진 부하를 한 단계 더 줄이는 ‘중간 캐시’
    # ■ 캐시 무효화:
    #   - Path purge (특정 경로)
    #   - Tag-based purge (Surrogate-Key)
    #   - 단축 TTL + 잦은 ETag 갱신
    #
    # ■ 동적 콘텐츠도 ‘마이크로 캐시(1~5초)’ 로 효과 큼
    print(" CDN = 1차 방어벽 + 광역 캐시.  TLS / DDoS / WAF 까지 함께.")
    print()


def lesson6_app_cache():
    # =========================================================================
    #   레슨 6 — 어플리케이션 캐시
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : Redis / Memcached / in-proc │")
    print("└──────────────────────────────────────┘")
    # ■ 계층:
    #   1) in-process (lru_cache)   — 매우 빠름, 노드별
    #   2) Memcached                — 단순 K/V, 메모리 강점
    #   3) Redis                    — 다양한 자료구조, persistence/replication
    #
    # ■ 캐시 패턴:
    #   - Cache-aside (read-through)
    #   - Write-through / Write-behind
    #   - Refresh-ahead
    #
    # ■ 함정:
    #   - 무한 cache → stale 데이터 노출
    #   - Thundering herd: 만료 직후 다수 요청이 한꺼번에 DB 강타 → 락 또는 jitter
    print(" 캐시는 ‘TTL + 무효화 전략 + thundering herd 방지’ 의 3종 세트.")
    print()


def lesson7_practice_token_bucket():
    # =========================================================================
    #   레슨 7 — 토큰 버킷 손코딩
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 토큰 버킷                  │")
    print("└──────────────────────────────────────┘")

    class TokenBucket:
        def __init__(self, rate_per_sec, capacity):
            self.rate = rate_per_sec
            self.cap = capacity
            self.tokens = capacity
            self.last = time.time()

        def allow(self, cost=1.0):
            now = time.time()
            # 시간 경과만큼 토큰 충전
            self.tokens = min(self.cap, self.tokens + (now - self.last) * self.rate)
            self.last = now
            if self.tokens >= cost:
                self.tokens -= cost
                return True
            return False

    # 5/s, 버킷 크기 5
    tb = TokenBucket(rate_per_sec=5.0, capacity=5)
    decisions = []
    for i in range(12):
        decisions.append((i, tb.allow()))
        time.sleep(0.05)        # 0.05초 간격으로 12회 요청 (≈ 240 req/s 의 burst)
    print(" 결과 (i, allow?)")
    for d in decisions:
        print(" ", d)
    print()
    # → 처음 5 개는 통과(버킷 가득), 그 다음은 토큰 부족으로 거부 → 충전 후 다시 통과.


# ─────────────────────────────────────────────────────────────────────────
# ■ 연습문제
# ─────────────────────────────────────────────────────────────────────────
#  Q1. Fixed window 의 ‘경계 버스트’ 가 사용자 경험에서 어떻게 나타나는가?
#  Q2. 위 토큰 버킷 코드에서 ‘분산 환경(여러 인스턴스)’ 으로 확장하려면 어떻게 바꿔야 하나?
#  Q3. HTTP 응답에 Cache-Control 을 ‘일부러’ no-store 로 두어야 하는 사례는?
#  Q4. Thundering herd 를 막는 두 가지 패턴을 적어라 (jitter, mutex).
#  Q5. CDN 의 ‘Stale-While-Revalidate’ 기능이 사용자 경험에 주는 효과를 설명하라.


if __name__ == "__main__":
    lesson1_why_rate_limit()
    lesson2_algorithms()
    lesson3_distributed()
    lesson4_http_cache()
    lesson5_cdn()
    lesson6_app_cache()
    lesson7_practice_token_bucket()
