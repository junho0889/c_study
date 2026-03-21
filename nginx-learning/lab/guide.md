# ■■■ Nginx 완벽 가이드 ■■■

## ■■■ 1. Nginx 아키텍처 ■■■

### 마스터/워커 프로세스 모델

```
┌─────────────────────────────────────────────┐
│              Master Process                  │
│  (설정 파일 읽기, 워커 관리, 포트 바인딩)      │
│  PID: /var/run/nginx.pid                     │
└──────────┬──────────┬──────────┬─────────────┘
           │          │          │
     ┌─────▼──┐ ┌─────▼──┐ ┌────▼───┐
     │Worker 1│ │Worker 2│ │Worker N│
     │(실제   │ │(실제   │ │(실제   │
     │ 요청   │ │ 요청   │ │ 요청   │
     │ 처리)  │ │ 처리)  │ │ 처리)  │
     └────────┘ └────────┘ └────────┘
```

- **마스터 프로세스**: root 권한으로 실행, 설정 파일 파싱, 워커 생성/관리
- **워커 프로세스**: nobody/nginx 사용자로 실행, 실제 요청 처리
- **이벤트 기반 비동기 처리**: 하나의 워커가 수천 개 동시 연결 처리 가능
- `worker_processes auto` → CPU 코어 수만큼 워커 생성 (권장)

### 설정 파일 구조 (Context 계층)

```
main (전역 설정)
├── events { }          ← 이벤트 처리 설정
└── http { }            ← HTTP 서버 설정
    ├── upstream { }    ← 백엔드 서버 그룹
    ├── server { }      ← 가상 호스트 (Virtual Host)
    │   ├── location { }  ← URL 경로별 처리
    │   │   └── location { }  ← 중첩 가능
    │   └── location { }
    └── server { }
```

## ■■■ 2. Location 블록 우선순위 ■■■

Nginx는 요청 URI와 location 블록을 매칭할 때 아래 우선순위를 따릅니다:

| 우선순위 | 수정자 | 이름 | 예시 | 설명 |
|---------|--------|------|------|------|
| 1 (최고) | `=` | 정확 매칭 | `location = /api` | URI가 정확히 일치할 때만 |
| 2 | `^~` | 접두사 매칭 (정규식 무시) | `location ^~ /images/` | 접두사 일치 시 정규식 검색 중단 |
| 3 | `~` | 정규식 매칭 (대소문자 구분) | `location ~ \.php$` | 정규식에 매칭 |
| 4 | `~*` | 정규식 매칭 (대소문자 무시) | `location ~* \.(jpg|png)$` | 대소문자 무관 정규식 |
| 5 (최저) | (없음) | 접두사 매칭 | `location /api/` | 가장 긴 접두사 매칭 |

### 매칭 알고리즘 흐름

```
1. 모든 접두사 location 검색 → 가장 긴 매칭 기억
2. = 매칭 발견? → 즉시 사용, 검색 중단
3. ^~ 매칭 발견? → 정규식 검색 건너뛰고 사용
4. 정규식 location 순서대로 검색 → 첫 번째 매칭 사용
5. 정규식 매칭 없으면 → 단계 1에서 기억한 접두사 location 사용
```

### 실전 예시

```nginx
# 1순위: 정확히 "/" 일 때만 매칭
location = / {
    return 200 "exact match";
}

# 2순위: /static/으로 시작하면 정규식보다 우선
location ^~ /static/ {
    root /var/www;
}

# 3순위: .php로 끝나는 URI (대소문자 구분)
location ~ \.php$ {
    fastcgi_pass 127.0.0.1:9000;
}

# 4순위: 이미지 파일 (대소문자 무시)
location ~* \.(jpg|jpeg|png|gif)$ {
    expires 30d;
}

# 5순위: /api/로 시작하는 모든 요청 (가장 낮은 우선순위)
location /api/ {
    proxy_pass http://backend;
}
```

## ■■■ 3. 로드밸런싱 알고리즘 비교 ■■■

| 알고리즘 | 지시어 | 장점 | 단점 | 적합한 사용 사례 |
|---------|--------|------|------|-----------------|
| Round Robin | (기본값) | 간단, 균등 분배 | 서버 부하 고려 안함 | 동일 성능 서버, 균일한 요청 |
| Weighted Round Robin | `weight=N` | 서버 성능 반영 | 동적 부하 반영 안함 | 서버 성능이 다를 때 |
| Least Connections | `least_conn` | 실시간 부하 반영 | 약간의 오버헤드 | 요청 처리 시간이 불균일할 때 |
| IP Hash | `ip_hash` | 세션 유지 (Sticky) | 부하 불균형 가능 | 세션 기반 애플리케이션 |
| Hash | `hash $key` | 커스텀 키 사용 | 서버 변경 시 재분배 | URI 기반 캐시 분배 |
| Hash (consistent) | `hash $key consistent` | 서버 추가/제거 시 영향 최소 | 약간의 불균형 | 캐시 서버 분배 |
| Random | `random two least_conn` | 분산 시스템에 적합 | 예측 불가 | 대규모 분산 환경 |

### 로드밸런싱 설정 예시

```nginx
# ■■■ 가중 Round Robin ■■■
upstream backend {
    server app1:5000 weight=5;    # 50% 트래픽
    server app2:5000 weight=3;    # 30% 트래픽
    server app3:5000 weight=2;    # 20% 트래픽
}

# ■■■ Least Connections + 가중치 ■■■
upstream backend {
    least_conn;
    server app1:5000 weight=3;
    server app2:5000 weight=1;
}

# ■■■ IP Hash (세션 유지) ■■■
upstream backend {
    ip_hash;
    server app1:5000;
    server app2:5000;
    server app3:5000 down;        # down: 일시적으로 비활성화
}

# ■■■ 서버 상태 옵션 ■■■
upstream backend {
    server app1:5000 max_fails=3 fail_timeout=30s;  # 3회 실패 시 30초 비활성화
    server app2:5000 backup;       # 백업: 다른 서버 모두 다운 시에만 사용
    server app3:5000 down;         # 다운: 트래픽 전달 안 함 (유지보수 시)
}
```

## ■■■ 4. SSL 인증서 설정 (Let's Encrypt + Certbot) ■■■

### 초기 인증서 발급

```bash
# 1. Certbot으로 인증서 발급 (webroot 방식)
docker-compose exec certbot certbot certonly \
    --webroot \
    -w /var/lib/letsencrypt \
    --email your@email.com \
    -d yourdomain.com \
    -d www.yourdomain.com \
    --agree-tos \
    --no-eff-email

# 2. 발급된 인증서 확인
docker-compose exec nginx ls -la /etc/letsencrypt/live/yourdomain.com/
# fullchain.pem  ← 서버 인증서 + 중간 인증서 (ssl_certificate)
# privkey.pem    ← 개인 키 (ssl_certificate_key)
# cert.pem       ← 서버 인증서만
# chain.pem      ← 중간 인증서만

# 3. Nginx에 SSL 설정 후 리로드
docker-compose exec nginx nginx -s reload
```

### 인증서 자동 갱신 (cron)

```bash
# 매일 새벽 3시에 갱신 시도 (만료 30일 전에만 갱신됨)
0 3 * * * docker-compose exec certbot certbot renew --quiet && docker-compose exec nginx nginx -s reload
```

### Nginx SSL 설정

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL 보안 설정
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:50m;
    ssl_session_timeout 1d;

    # HSTS (HTTPS 강제)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

## ■■■ 5. 성능 튜닝 가이드 ■■■

### 워커 설정

| 설정 | 권장값 | 설명 |
|------|--------|------|
| `worker_processes` | `auto` (CPU 코어 수) | 워커 프로세스 수 |
| `worker_connections` | 4096~65535 | 워커당 최대 동시 연결 |
| `worker_rlimit_nofile` | worker_connections × 2 | 파일 디스크립터 제한 |
| `multi_accept` | `on` | 한번에 여러 연결 수락 |

### 버퍼 설정

| 설정 | 권장값 | 설명 |
|------|--------|------|
| `client_body_buffer_size` | `128k` | 요청 본문 버퍼 |
| `client_header_buffer_size` | `4k` | 요청 헤더 버퍼 |
| `large_client_header_buffers` | `4 8k` | 큰 헤더용 버퍼 |
| `proxy_buffer_size` | `8k` | 프록시 응답 헤더 버퍼 |
| `proxy_buffers` | `8 8k` | 프록시 응답 본문 버퍼 |
| `proxy_busy_buffers_size` | `16k` | 전송 중 버퍼 크기 |

### 타임아웃 설정

| 설정 | 권장값 | 설명 |
|------|--------|------|
| `keepalive_timeout` | `65s` | Keep-Alive 유지 시간 |
| `keepalive_requests` | `1000` | Keep-Alive당 최대 요청 |
| `client_body_timeout` | `12s` | 요청 본문 수신 타임아웃 |
| `client_header_timeout` | `12s` | 요청 헤더 수신 타임아웃 |
| `send_timeout` | `10s` | 응답 전송 타임아웃 |
| `proxy_connect_timeout` | `10s` | 업스트림 연결 타임아웃 |
| `proxy_read_timeout` | `30s` | 업스트림 응답 타임아웃 |

### 압축 설정

```nginx
gzip on;
gzip_comp_level 6;        # 1(빠름/낮음) ~ 9(느림/높음), 6이 균형점
gzip_min_length 256;      # 256바이트 미만은 압축 안함
gzip_vary on;              # Vary 헤더 추가 (CDN 캐시 구분)
gzip_proxied any;          # 프록시 요청도 압축
```

## ■■■ 6. 보안 강화 체크리스트 ■■■

```
[x] server_tokens off                     # Nginx 버전 정보 숨기기
[x] X-Frame-Options: SAMEORIGIN           # 클릭재킹 방지
[x] X-Content-Type-Options: nosniff       # MIME 스니핑 방지
[x] X-XSS-Protection: 1; mode=block       # XSS 필터
[x] Content-Security-Policy 설정          # CSP 콘텐츠 보안 정책
[x] Strict-Transport-Security (HSTS)      # HTTPS 강제
[x] Referrer-Policy                       # 리퍼러 정보 제한
[x] Permissions-Policy                    # 브라우저 기능 접근 제한
[x] Rate Limiting (limit_req)             # 요청 속도 제한
[x] 연결 수 제한 (limit_conn)              # 동시 연결 수 제한
[x] SSL/TLS 1.2+ 만 허용                  # 취약한 프로토콜 비활성화
[x] 강력한 Cipher Suite 사용              # 약한 암호화 비활성화
[x] 숨김 파일 접근 차단 (location ~ /\.)   # .env, .git 등
[x] client_max_body_size 제한             # 대용량 업로드 방지
[x] 불필요한 HTTP 메서드 차단              # TRACE, DELETE 등
[x] 디렉토리 목록 비활성화 (autoindex off)  # 디렉토리 탐색 방지
```

## ■■■ 7. 모니터링 ■■■

### stub_status 모듈

```nginx
# nginx.conf에 추가
server {
    listen 8080;
    location /nginx_status {
        stub_status on;
        allow 127.0.0.1;
        deny all;
    }
}
```

```bash
# 상태 확인
curl http://localhost:8080/nginx_status

# 출력 예시:
# Active connections: 291
# server accepts handled requests
#  16630948 16630948 31070465
# Reading: 6 Writing: 179 Waiting: 106
```

| 지표 | 설명 |
|------|------|
| Active connections | 현재 활성 연결 수 (Reading + Writing + Waiting) |
| accepts | 수락한 총 연결 수 |
| handled | 처리한 총 연결 수 (accepts와 같아야 정상) |
| requests | 처리한 총 요청 수 |
| Reading | 요청 헤더를 읽고 있는 연결 수 |
| Writing | 응답을 전송하고 있는 연결 수 |
| Waiting | Keep-Alive 대기 중인 유휴 연결 수 |

### 로그 분석

```bash
# 실시간 로그 모니터링
docker-compose exec nginx tail -f /var/log/nginx/access.log

# 상태 코드별 카운트
awk '{print $9}' access.log | sort | uniq -c | sort -rn

# 가장 많이 요청된 URL
awk '{print $7}' access.log | sort | uniq -c | sort -rn | head -20

# 느린 요청 (1초 이상)
awk '$NF > 1.0' access.log

# IP별 요청 수 (DDoS 탐지)
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -20
```

## ■■■ 8. 트러블슈팅 ■■■

### 502 Bad Gateway

```
원인: Nginx가 업스트림 서버에 연결했지만 유효한 응답을 받지 못함

해결 방법:
1. 백엔드 서버 상태 확인
   docker-compose logs app1

2. 업스트림 서버 연결 테스트
   docker-compose exec nginx curl http://app1:5000/health

3. proxy_pass URL 확인 (프로토콜, 호스트, 포트)

4. 버퍼 크기 증가
   proxy_buffer_size 16k;
   proxy_buffers 8 16k;

5. 로그 확인
   tail -f /var/log/nginx/error.log
```

### 504 Gateway Timeout

```
원인: 업스트림 서버가 제한 시간 내에 응답하지 않음

해결 방법:
1. 타임아웃 증가
   proxy_connect_timeout 60s;
   proxy_read_timeout 120s;
   proxy_send_timeout 60s;

2. 백엔드 서버 성능 확인 (쿼리 최적화, 외부 API 호출 등)

3. keepalive 설정 확인
   upstream backend {
       keepalive 32;
   }
```

### 413 Request Entity Too Large

```
원인: 클라이언트 요청 본문이 client_max_body_size 초과

해결 방법:
1. client_max_body_size 증가
   client_max_body_size 100m;  # 100MB로 증가

2. 특정 location에만 적용
   location /upload {
       client_max_body_size 500m;
   }
```

### 기타 일반적인 문제

```
■ 403 Forbidden
  - 파일/디렉토리 권한 확인: ls -la /var/www/
  - nginx 사용자 권한 확인: user nginx; → chown -R nginx:nginx /var/www/
  - SELinux 확인 (CentOS): setsebool -P httpd_can_network_connect 1

■ 설정 변경이 적용 안 됨
  - 설정 문법 검사: nginx -t
  - 리로드: nginx -s reload (재시작 없이 설정 적용)
  - 캐시 삭제: rm -rf /var/cache/nginx/*

■ upstream과 연결이 안 됨
  - DNS 확인: docker-compose exec nginx nslookup app1
  - 네트워크 확인: docker network inspect lab_backend
```

## ■■■ 9. 자주 사용하는 명령어 ■■■

```bash
# ■■■ 설정 관리 ■■■
nginx -t                    # 설정 파일 문법 검사 (반드시 먼저 실행!)
nginx -T                    # 전체 설정 내용 출력 (디버깅용)
nginx -s reload             # 설정 다시 로드 (무중단, graceful)
nginx -s stop               # 즉시 중지 (강제)
nginx -s quit               # 현재 요청 처리 후 종료 (graceful)
nginx -s reopen             # 로그 파일 다시 열기 (로그 로테이션 후)

# ■■■ Docker Compose 명령어 ■■■
docker-compose up -d --build        # 빌드 후 백그라운드 실행
docker-compose down -v              # 중지 + 볼륨 삭제
docker-compose logs -f nginx        # Nginx 로그 실시간 확인
docker-compose exec nginx nginx -t  # 컨테이너 내에서 설정 검사
docker-compose exec nginx nginx -s reload  # 설정 리로드
docker-compose restart nginx        # Nginx 컨테이너 재시작

# ■■■ 테스트 명령어 ■■■
# 로드밸런싱 테스트 (여러 번 실행하여 서버 분배 확인)
for i in $(seq 1 10); do curl -s http://localhost/api/data | jq .server; done

# 헤더 확인
curl -I http://localhost/

# Rate Limiting 테스트
for i in $(seq 1 30); do curl -s -o /dev/null -w "%{http_code}\n" http://localhost/api/data; done

# SSL 인증서 확인
openssl s_client -connect localhost:443 -servername yourdomain.com

# 캐시 상태 확인
curl -I http://localhost/api/data | grep X-Cache

# stub_status 확인
curl http://localhost:8080/nginx_status
```

## ■■■ 10. 실습 시나리오 ■■■

### 시나리오 1: 로드밸런싱 확인

```bash
# 1. 환경 시작
docker-compose up -d --build

# 2. 여러 번 요청하여 서버 분배 확인
for i in $(seq 1 12); do
  echo "Request $i:"
  curl -s http://localhost/api/data | python3 -m json.tool | grep server
done

# 예상 결과: weight 비율(3:2:1)에 따라
# app1이 6회, app2가 4회, app3이 2회 응답
```

### 시나리오 2: Rate Limiting 테스트

```bash
# 빠르게 연속 요청 (초당 10개 제한 + burst 20)
for i in $(seq 1 50); do
  curl -s -o /dev/null -w "Request $i: %{http_code}\n" http://localhost/api/data
done

# 처음 30개(10+20burst)는 200, 이후 429 Too Many Requests
```

### 시나리오 3: 장애 복구 테스트

```bash
# 1. app1 중지
docker-compose stop app1

# 2. 요청 → app2, app3만 응답하는지 확인
curl -s http://localhost/api/data | jq .server

# 3. app1 재시작
docker-compose start app1

# 4. app1이 다시 응답하는지 확인
curl -s http://localhost/api/data | jq .server
```
