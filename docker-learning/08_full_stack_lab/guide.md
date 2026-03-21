# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# ■ 파일명: guide.md
# ■ 목적: 풀스택 실습 종합 가이드
# ■ 설명: 전체 아키텍처 설명, 통신 흐름, 실행 방법, 트러블슈팅
# ■ 날짜: 2026-03-21
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# Docker Full Stack Lab - 종합 가이드

## 1. 프로젝트 개요

이 프로젝트는 **실제 웹 서비스와 동일한 구조**를 Docker Compose로 구현한 거야.
하나의 `docker-compose up` 명령어로 전체 시스템이 실행돼!

### 구성 서비스

| 서비스 | 기술 | 역할 | 포트 |
|--------|------|------|------|
| **Nginx** | Nginx 1.27 | 리버스 프록시, 정적 파일 서빙 | 80, 443 |
| **API** | Python Flask | REST API, 비즈니스 로직 | 8000 (내부) |
| **DB** | PostgreSQL 16 | 데이터 영구 저장 | 5432 (내부) |
| **Redis** | Redis 7 | 캐시, 세션, 카운터 | 6379 (내부) |
| **Prometheus** | Prometheus | 메트릭 수집 & 모니터링 | 9090 |

## 2. 전체 아키텍처

```
                        ┌──────────────────────────────────────────┐
                        │              사용자 브라우저                │
                        └──────────────────┬───────────────────────┘
                                           │
                                    http://localhost
                                           │
                        ┌──────────────────▼───────────────────────┐
                        │                Nginx                      │
                        │          (리버스 프록시 + 정적 서빙)          │
                        │                                          │
                        │   /            → frontend (정적 HTML)      │
                        │   /api/*       → Python API (포트 8000)    │
                        │   /health      → Nginx 상태 확인           │
                        │   /metrics     → API 메트릭 프록시          │
                        └─────┬──────────────────┬─────────────────┘
                              │                  │
                    정적 파일 제공           API 프록시
                              │                  │
               ┌──────────────┘    ┌─────────────▼──────────────┐
               │                   │        Python API           │
               │ index.html        │      (Flask:8000)           │
               │ style.css         │                             │
               │ script.js         │  /         → API 정보        │
               │                   │  /health   → 상태 확인       │
               │                   │  /api/items → 아이템 CRUD    │
               │                   │  /api/stats → 통계           │
               │                   │  /metrics  → Prometheus 메트릭│
               │                   └──────┬──────────┬───────────┘
               │                          │          │
               │                  DB 쿼리  │    캐시   │
               │                          │          │
               │             ┌────────────▼──┐ ┌────▼──────────┐
               │             │  PostgreSQL    │ │    Redis       │
               │             │  (포트 5432)   │ │  (포트 6379)    │
               │             │               │ │               │
               │             │  items 테이블   │ │  캐시 (60초)   │
               │             │  - id          │ │  visit_count  │
               │             │  - name        │ │  cache:items  │
               │             │  - description │ │               │
               │             │  - created_at  │ │               │
               │             └───────────────┘ └───────────────┘
               │
               │            ┌─────────────────────────┐
               │            │     Prometheus (9090)     │
               │            │                          │
               │            │  15초마다 API에서 메트릭 수집│
               │            │  7일간 데이터 보존          │
               │            └─────────────────────────┘
```

## 3. 서비스 간 통신 흐름

### 3.1 사용자가 웹 페이지를 열 때

```
1. 브라우저 → http://localhost/ 요청
2. Nginx가 요청을 받음
3. / 경로 → /usr/share/nginx/html/index.html 반환
4. 브라우저가 HTML을 렌더링
```

### 3.2 프론트엔드가 API를 호출할 때

```
1. JavaScript에서 fetch('/api/items') 호출
2. Nginx가 /api/ 요청을 받음
3. proxy_pass로 http://api:8000/items 에 전달
4. API 서버가 처리:
   a. Redis 캐시 확인 (cache:items 키)
   b. 캐시 있으면 → 캐시 반환 (빠름!)
   c. 캐시 없으면 → PostgreSQL에서 조회
   d. 결과를 Redis에 60초 캐싱
5. JSON 응답을 Nginx에 반환
6. Nginx가 브라우저에 전달
7. JavaScript가 결과를 화면에 표시
```

### 3.3 아이템을 생성할 때

```
1. JavaScript에서 POST /api/items 호출
2. Nginx → API로 전달
3. API가 PostgreSQL에 INSERT
4. Redis 캐시 무효화 (delete cache:items)
5. 201 Created 응답 반환
```

### 3.4 Prometheus가 메트릭을 수집할 때

```
1. Prometheus가 10초마다 http://api:8000/metrics 호출
2. API가 prometheus_client 라이브러리로 메트릭 생성
3. 요청 수, 응답 시간, 활성 연결 수 등 반환
4. Prometheus가 시계열 데이터로 저장
```

## 4. 네트워크 구성

```
┌─ frontend 네트워크 ─────────────────────────┐
│                                             │
│   Nginx ←────→ API ←────→ Prometheus        │
│                                             │
└─────────────────────────────────────────────┘

┌─ backend 네트워크 ──────────────────────────┐
│                                             │
│   API ←────→ PostgreSQL                     │
│   API ←────→ Redis                          │
│   API ←────→ Prometheus                     │
│                                             │
└─────────────────────────────────────────────┘

Nginx는 backend 네트워크에 없으므로:
  ✅ Nginx → API (frontend 네트워크 통해 가능)
  ❌ Nginx → DB (접근 불가! 보안!)
  ❌ Nginx → Redis (접근 불가! 보안!)
```

## 5. 실행 방법

### 5.1 시작

```bash
# 1. 프로젝트 디렉토리로 이동
cd 08_full_stack_lab/

# 2. 모든 서비스 시작 (이미지 빌드 포함)
docker-compose up -d --build

# 3. 상태 확인 (모든 서비스가 healthy인지)
docker-compose ps

# 4. 로그 확인
docker-compose logs -f
```

### 5.2 접속

```
웹 페이지: http://localhost
API 직접:  http://localhost/api/
헬스체크:  http://localhost/api/health
통계:      http://localhost/api/stats
메트릭:    http://localhost/metrics
Prometheus: http://localhost:9090
```

### 5.3 API 테스트 (curl)

```bash
# API 정보
curl http://localhost/api/

# 헬스체크
curl http://localhost/api/health

# 아이템 목록 조회
curl http://localhost/api/items

# 아이템 생성
curl -X POST http://localhost/api/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Docker 마스터", "description": "Docker를 완전히 이해했다!"}'

# 통계 확인
curl http://localhost/api/stats

# Prometheus 메트릭
curl http://localhost/api/metrics
```

### 5.4 종료

```bash
# 서비스만 종료 (데이터 보존)
docker-compose down

# 서비스 + 볼륨 전부 삭제 (초기화)
docker-compose down -v

# 이미지까지 삭제
docker-compose down -v --rmi all
```

## 6. 파일 구조

```
08_full_stack_lab/
├── docker-compose.yml          ← 전체 서비스 정의
├── .env                        ← 환경변수
├── prometheus.yml              ← Prometheus 설정
├── nginx/
│   └── nginx.conf              ← Nginx 리버스 프록시 설정
├── api/
│   ├── Dockerfile              ← API 이미지 빌드
│   ├── requirements.txt        ← Python 의존성
│   ├── app.py                  ← Flask API 소스코드
│   └── init.sql                ← DB 초기화 SQL
├── frontend/
│   ├── Dockerfile              ← 프론트엔드 이미지 (참고용)
│   └── index.html              ← 웹 페이지
└── guide.md                    ← 이 가이드
```

## 7. 학습 포인트

### 이 프로젝트에서 배울 수 있는 것들:

```
1. 멀티 서비스 아키텍처
   → 여러 서비스가 어떻게 함께 동작하는지

2. 리버스 프록시
   → Nginx가 요청을 어떻게 라우팅하는지

3. 데이터베이스 연동
   → 컨테이너에서 PostgreSQL 사용하기

4. 캐싱 전략
   → Redis로 API 응답 캐싱하기

5. 네트워크 분리
   → frontend/backend 네트워크로 보안 강화

6. 볼륨으로 데이터 보존
   → DB 데이터를 볼륨에 영구 저장

7. 헬스체크
   → 서비스 상태를 자동으로 모니터링

8. 모니터링
   → Prometheus로 메트릭 수집

9. 환경변수 관리
   → .env 파일로 설정 분리

10. 리소스 제한
    → CPU, 메모리 제한으로 안정성 확보
```

## 8. 트러블슈팅

### 문제 1: API가 시작하지 않아

```bash
# 로그 확인
docker-compose logs api

# 흔한 원인:
# - DB가 아직 준비 안 됨 → depends_on condition 확인
# - 환경변수 누락 → docker-compose config로 확인
# - 포트 충돌 → docker-compose ps로 확인
```

### 문제 2: DB 연결 실패

```bash
# DB가 실행 중인지 확인
docker-compose ps db
docker-compose logs db

# DB에 직접 접속 테스트
docker-compose exec db psql -U postgres -d fullstack -c "SELECT 1;"

# 흔한 원인:
# - 비밀번호 불일치 → .env 파일 확인
# - DB 이름 오타 → POSTGRES_DB와 DATABASE_URL 비교
# - 볼륨 권한 문제 → docker-compose down -v 후 재시작
```

### 문제 3: 브라우저에서 접속 안 됨

```bash
# Nginx 상태 확인
docker-compose ps nginx
docker-compose logs nginx

# Nginx 설정 검증
docker-compose exec nginx nginx -t

# 흔한 원인:
# - 포트 80을 다른 프로세스가 사용 중 → .env에서 포트 변경
# - nginx.conf 문법 오류 → nginx -t로 확인
# - API가 아직 healthy가 아님 → depends_on condition 확인
```

### 문제 4: 캐시가 안 되는 것 같아

```bash
# Redis 접속해서 확인
docker-compose exec redis redis-cli

# 키 목록 확인
127.0.0.1:6379> KEYS *

# 특정 키 값 확인
127.0.0.1:6379> GET cache:items

# TTL (남은 시간) 확인
127.0.0.1:6379> TTL cache:items
```

### 문제 5: 디스크 공간 부족

```bash
# Docker 디스크 사용량 확인
docker system df

# 불필요한 것 정리
docker system prune -a         # 안 쓰는 이미지/컨테이너 삭제
docker volume prune            # 안 쓰는 볼륨 삭제
```

## 9. 확장 아이디어

```
이 프로젝트를 기반으로 더 확장할 수 있어:

1. Grafana 추가 → 예쁜 대시보드로 메트릭 시각화
2. Celery 추가 → 비동기 작업 처리 (이메일 발송 등)
3. Elasticsearch + Kibana → 로그 수집/분석
4. SSL 인증서 → Let's Encrypt로 HTTPS 적용
5. CI/CD 파이프라인 → GitHub Actions로 자동 배포
6. Docker Swarm → 여러 서버에 분산 배포
7. 인증 시스템 → JWT 토큰 기반 로그인
8. 파일 업로드 → 볼륨에 파일 저장
```

## 10. 명령어 치트시트

```bash
# ── 서비스 관리 ──
docker-compose up -d --build         # 빌드 + 시작
docker-compose down                  # 종료
docker-compose down -v               # 종료 + 데이터 삭제
docker-compose restart api           # API만 재시작
docker-compose ps                    # 상태 확인

# ── 로그 ──
docker-compose logs -f api           # API 실시간 로그
docker-compose logs --tail 50        # 최근 50줄

# ── 디버깅 ──
docker-compose exec api bash         # API 컨테이너 접속
docker-compose exec db psql -U postgres -d fullstack
docker-compose exec redis redis-cli
docker-compose exec nginx nginx -t   # Nginx 설정 검증

# ── 모니터링 ──
docker stats                         # 리소스 사용량
docker-compose top                   # 프로세스 목록
```
