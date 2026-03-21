# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# ■ 파일명: guide.md
# ■ 목적: 컨테이너 모니터링과 로그 관리 가이드
# ■ 설명: Prometheus, Grafana, 로그 관리, 헬스체크 전략
# ■ 날짜: 2026-03-21
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# 컨테이너 모니터링과 로그 관리 가이드

## 1. 왜 모니터링이 필요할까?

```
모니터링 없이 운영하는 것 = 속도계 없이 운전하는 것

알아야 할 것들:
- CPU, 메모리를 얼마나 쓰고 있어?
- 요청이 얼마나 들어오고 있어?
- 에러가 얼마나 발생하고 있어?
- 응답 시간이 느려지고 있진 않아?
- 디스크가 가득 차고 있진 않아?
```

## 2. 모니터링 스택 구성

```
┌──────────────────────────────────────────────┐
│               Grafana (시각화)                │
│         http://localhost:3000                │
│  ┌──────────────────────────────────────┐    │
│  │  📊 CPU 사용률 그래프                   │    │
│  │  📊 메모리 사용률 그래프                  │    │
│  │  📊 요청 수 / 응답 시간 그래프            │    │
│  └──────────────────────────────────────┘    │
│                     ↑ 데이터 조회              │
│             ┌───────┴───────┐               │
│             │  Prometheus   │               │
│             │  (데이터 저장)  │               │
│             └───┬───────┬───┘               │
│         메트릭 수집│       │메트릭 수집         │
│           ┌─────┘       └─────┐             │
│     ┌─────▼─────┐     ┌──────▼─────┐       │
│     │  cAdvisor  │     │   웹 앱     │       │
│     │ (컨테이너)  │     │ (/metrics) │       │
│     └───────────┘     └────────────┘       │
└──────────────────────────────────────────────┘
```

## 3. Prometheus 사용법

```bash
# Prometheus 웹 UI: http://localhost:9090

# ── PromQL (Prometheus Query Language) 기본 ──

# 총 요청 수
app_requests_total

# 최근 5분간 초당 요청 수
rate(app_requests_total[5m])

# 평균 응답 시간
rate(app_request_latency_seconds_sum[5m]) / rate(app_request_latency_seconds_count[5m])

# 컨테이너 CPU 사용률
rate(container_cpu_usage_seconds_total[5m]) * 100

# 컨테이너 메모리 사용량 (MB)
container_memory_usage_bytes / 1024 / 1024
```

## 4. Grafana 설정 방법

```
1. http://localhost:3000 접속
2. admin / admin 로그인
3. 데이터 소스 추가:
   - Configuration → Data Sources → Add
   - Type: Prometheus
   - URL: http://prometheus:9090
   - Save & Test

4. 대시보드 만들기:
   - Create → Dashboard → Add Panel
   - PromQL 쿼리 입력
   - 시각화 설정

5. 미리 만들어진 대시보드 가져오기:
   - Create → Import
   - Dashboard ID: 1860 (Node Exporter)
   - Dashboard ID: 893 (cAdvisor)
```

## 5. Docker 로그 관리

### 로그 드라이버 종류

| 드라이버 | 설명 | 사용 사례 |
|---------|------|----------|
| `json-file` | JSON 형식으로 로컬 저장 (기본) | 개발, 소규모 |
| `syslog` | Syslog 서버로 전송 | Linux 서버 |
| `journald` | systemd journal로 전송 | systemd 사용 시 |
| `fluentd` | Fluentd로 전송 | 중앙 로그 수집 |
| `awslogs` | AWS CloudWatch로 전송 | AWS 환경 |
| `none` | 로그 저장 안 함 | 로그 불필요 시 |

### 로그 관리 명령어

```bash
# 전체 로그 보기
docker logs 컨테이너명

# 실시간 로그 보기 (tail -f 같은 거)
docker logs -f 컨테이너명

# 마지막 100줄만
docker logs --tail 100 컨테이너명

# 시간 범위로 필터
docker logs --since 2026-03-21T10:00:00 컨테이너명
docker logs --since 30m 컨테이너명    # 최근 30분

# docker-compose로 모든 서비스 로그
docker-compose logs -f
docker-compose logs -f --tail 50 web prometheus
```

### 로그 용량 제한 (중요!)

```yaml
# docker-compose.yml에서:
services:
  web:
    logging:
      driver: json-file
      options:
        max-size: "10m"    # 파일당 최대 10MB
        max-file: "3"      # 최대 3개 파일 (총 30MB)
    # max-size * max-file = 최대 로그 용량
    # 이걸 안 하면 로그가 무한히 커져서 디스크가 가득 찰 수 있어!
```

## 6. 헬스체크 전략

```yaml
# ── HTTP 기반 헬스체크 (웹 앱) ──
healthcheck:
  test: ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
  interval: 30s        # 30초마다 확인
  timeout: 10s         # 10초 안에 응답해야 함
  retries: 3           # 3번 연속 실패 → unhealthy
  start_period: 40s    # 시작 후 40초 대기

# ── TCP 기반 헬스체크 (데이터베이스) ──
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  timeout: 5s
  retries: 5

# ── Redis 전용 ──
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 3s
  retries: 3
```

### 헬스체크 상태 확인

```bash
# 컨테이너 상태 확인
docker ps                     # STATUS 열에 (healthy)/(unhealthy) 표시
docker inspect --format='{{.State.Health.Status}}' 컨테이너명
```

## 7. 이 프로젝트 실행하기

```bash
# 1. 시작
cd 06_monitoring_logging/
docker-compose up -d

# 2. 웹 앱에 요청 보내기 (메트릭 생성)
for i in $(seq 1 100); do curl -s http://localhost:8000/ > /dev/null; done

# 3. 각 서비스 접속
# 웹 앱: http://localhost:8000
# 메트릭: http://localhost:8000/metrics
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
# cAdvisor: http://localhost:8081

# 4. Prometheus에서 쿼리 해보기
# http://localhost:9090 → 쿼리 입력:
#   app_requests_total
#   rate(app_requests_total[1m])

# 5. 종료
docker-compose down -v
```

## 8. 알림 설정 (참고)

```
Grafana에서 알림 규칙을 만들 수 있어:

예시:
- CPU 사용률이 80% 넘으면 → 슬랙 알림
- 메모리 사용률이 90% 넘으면 → 이메일 알림
- 에러율이 5% 넘으면 → PagerDuty 알림
- 응답 시간이 2초 넘으면 → 슬랙 알림

설정 방법:
1. Grafana → Alerting → Alert Rules
2. 조건 설정 (PromQL 쿼리)
3. 알림 채널 설정 (Slack, Email 등)
```
