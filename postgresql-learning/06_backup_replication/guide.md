# ■■■ PostgreSQL 백업 & 복제 가이드 ■■■

## ■■■ 1. 백업 전략 개요 ■■■

| 방법 | 도구 | 특징 | 용도 |
|------|------|------|------|
| 논리 백업 | `pg_dump` | SQL 덤프, 선택적 복원 가능 | 소규모 DB, 마이그레이션 |
| 물리 백업 | `pg_basebackup` | 바이너리 복사, 빠름 | 대규모 DB, PITR |
| 연속 아카이빙 | WAL 아카이빙 | 시점 복구(PITR) 가능 | 프로덕션 필수 |
| 논리 복제 | Logical Replication | 테이블 단위 선택적 복제 | 업그레이드, 부분 동기화 |
| 스트리밍 복제 | Streaming Replication | 실시간 전체 복제 | 고가용성(HA) |

## ■■■ 2. pg_dump (논리 백업) ■■■

```bash
# ■■■ 전체 데이터베이스 백업 ■■■
# -Fc: 커스텀 포맷 (압축, pg_restore로 복원)
docker-compose exec primary pg_dump \
    -U postgres \
    -d study_db \
    -Fc \
    -f /tmp/study_db_backup.dump

# 호스트에서 직접 실행
pg_dump -h localhost -p 5432 -U postgres -d study_db -Fc > backup.dump

# ■■■ SQL 텍스트 포맷 백업 ■■■
pg_dump -h localhost -p 5432 -U postgres -d study_db > backup.sql

# ■■■ 특정 테이블만 백업 ■■■
pg_dump -h localhost -U postgres -d study_db \
    -t employees -t departments \
    -Fc > tables_backup.dump

# ■■■ 스키마만 백업 (데이터 제외) ■■■
pg_dump -h localhost -U postgres -d study_db \
    --schema-only > schema_only.sql

# ■■■ 데이터만 백업 (스키마 제외) ■■■
pg_dump -h localhost -U postgres -d study_db \
    --data-only > data_only.sql

# ■■■ 전체 클러스터 백업 (모든 DB + 역할) ■■■
pg_dumpall -h localhost -U postgres > full_cluster.sql
```

## ■■■ 3. pg_restore (복원) ■■■

```bash
# ■■■ 커스텀 포맷 복원 ■■■
# --clean: 기존 객체 삭제 후 복원
# --if-exists: 객체가 없어도 에러 안 남
# -j 4: 4개 병렬 작업 (빠른 복원)
pg_restore -h localhost -U postgres -d study_db \
    --clean --if-exists \
    -j 4 \
    backup.dump

# ■■■ 새 데이터베이스로 복원 ■■■
createdb -h localhost -U postgres new_study_db
pg_restore -h localhost -U postgres -d new_study_db backup.dump

# ■■■ 특정 테이블만 복원 ■■■
pg_restore -h localhost -U postgres -d study_db \
    -t employees \
    backup.dump

# ■■■ SQL 텍스트 파일 복원 ■■■
psql -h localhost -U postgres -d study_db < backup.sql

# ■■■ 복원 시 에러 무시하고 계속 진행 ■■■
pg_restore -h localhost -U postgres -d study_db \
    --no-owner --no-privileges \
    backup.dump 2>/dev/null || true
```

## ■■■ 4. WAL (Write-Ahead Logging) ■■■

```
WAL이란?
- 모든 데이터 변경사항을 먼저 WAL에 기록 후 데이터 파일에 반영
- 크래시 시 WAL을 재생(replay)하여 데이터 복구
- 복제, PITR(시점 복구)의 핵심 메커니즘

WAL 흐름:
  클라이언트 → SQL 실행
           → WAL 버퍼에 기록
           → WAL 파일에 기록 (fsync)  ← 이 시점에서 커밋 확정
           → 백그라운드에서 데이터 파일 반영 (checkpoint)
           → WAL을 Standby로 전송 (스트리밍 복제)
```

### WAL 설정

```
# postgresql.conf
wal_level = replica          # minimal | replica | logical
max_wal_size = 1GB           # 체크포인트 사이 최대 WAL 크기
min_wal_size = 80MB          # 유지할 최소 WAL 크기
wal_keep_size = 256MB        # Standby를 위해 유지할 WAL 크기
archive_mode = on            # WAL 아카이빙 활성화
archive_command = 'cp %p /archive/%f'  # 아카이브 명령
```

## ■■■ 5. 스트리밍 복제 ■■■

### 아키텍처

```
┌─────────────┐    WAL Stream    ┌─────────────┐
│   Primary   │ ──────────────→  │   Standby   │
│  (읽기/쓰기) │                  │  (읽기 전용)  │
│  port: 5432 │                  │  port: 5433 │
└─────────────┘                  └─────────────┘
      │                                │
      │ wal_sender 프로세스             │ wal_receiver 프로세스
      │ → WAL 레코드 전송               │ → WAL 수신 후 재생
```

### 복제 상태 확인

```sql
-- ■■■ Primary에서 확인 ■■■
-- 복제 상태 확인
SELECT
    client_addr,           -- Standby IP
    state,                 -- 상태 (streaming, catchup, startup)
    sent_lsn,              -- 전송한 WAL 위치
    write_lsn,             -- Standby가 기록한 WAL 위치
    flush_lsn,             -- Standby가 디스크에 쓴 WAL 위치
    replay_lsn,            -- Standby가 재생한 WAL 위치
    pg_wal_lsn_diff(sent_lsn, replay_lsn) AS replay_lag_bytes  -- 복제 지연 (바이트)
FROM pg_stat_replication;

-- 복제 슬롯 상태
SELECT
    slot_name,
    active,
    restart_lsn
FROM pg_replication_slots;

-- ■■■ Standby에서 확인 ■■■
-- 복제 수신 상태
SELECT
    status,
    received_lsn,          -- 수신한 WAL 위치
    last_msg_send_time,    -- 마지막 메시지 전송 시각
    last_msg_receipt_time  -- 마지막 메시지 수신 시각
FROM pg_stat_wal_receiver;

-- 읽기 전용 상태 확인
SELECT pg_is_in_recovery();  -- true = Standby 모드
```

### 실습 단계

```bash
# 1. 환경 시작
cd postgresql-learning/06_backup_replication
docker-compose up -d

# 2. Primary에서 데이터 생성
docker exec -it pg-primary psql -U postgres -d study_db -c "
    CREATE TABLE repl_test (id SERIAL, msg TEXT, created_at TIMESTAMPTZ DEFAULT NOW());
    INSERT INTO repl_test (msg) VALUES ('Hello from Primary!');
"

# 3. Standby에서 복제 확인 (읽기만 가능)
docker exec -it pg-standby psql -U postgres -d study_db -c "
    SELECT * FROM repl_test;
"

# 4. Standby에서 쓰기 시도 → 에러 발생
docker exec -it pg-standby psql -U postgres -d study_db -c "
    INSERT INTO repl_test (msg) VALUES ('This will fail!');
"
# ERROR: cannot execute INSERT in a read-only transaction

# 5. 복제 지연 확인
docker exec -it pg-primary psql -U postgres -c "
    SELECT client_addr, state, pg_wal_lsn_diff(sent_lsn, replay_lsn) AS lag_bytes
    FROM pg_stat_replication;
"
```

## ■■■ 6. PITR (Point-in-Time Recovery) ■■■

```bash
# PITR: 특정 시점으로 데이터베이스 복구
# 필요 조건: 기본 백업(pg_basebackup) + WAL 아카이브

# 1. 기본 백업 수행
pg_basebackup -h localhost -U postgres \
    -D /backup/base \
    -Ft -z -Xs -P

# 2. 실수로 데이터 삭제 (오전 10:30에 발생)
# DELETE FROM employees;  -- 실수!

# 3. 복구 (postgresql.conf 또는 recovery.conf)
# restore_command = 'cp /archive/%f %p'
# recovery_target_time = '2026-03-21 10:29:00'  # 삭제 직전 시점
# recovery_target_action = 'promote'             # 복구 후 Primary로 승격

# 4. PostgreSQL 재시작
# pg_ctl start -D /var/lib/postgresql/data
```

## ■■■ 7. 백업 전략 권장사항 ■■■

```
프로덕션 백업 전략:
┌─────────────────────────────────────────────────────────┐
│ 1. 일일 pg_dump (논리 백업)                               │
│    - cron: 0 2 * * * pg_dump -Fc study_db > daily.dump  │
│    - 보관: 최근 7일                                      │
│                                                          │
│ 2. 주간 pg_basebackup (물리 백업)                         │
│    - cron: 0 3 * * 0 pg_basebackup ...                  │
│    - 보관: 최근 4주                                      │
│                                                          │
│ 3. 연속 WAL 아카이빙                                     │
│    - archive_mode = on                                   │
│    - 보관: 기본 백업 이후의 모든 WAL                       │
│                                                          │
│ 4. 스트리밍 복제 (Standby)                                │
│    - 실시간 복제로 장애 대비                               │
│    - 자동 페일오버 (Patroni, repmgr 등)                   │
│                                                          │
│ 5. 백업 검증                                             │
│    - 정기적으로 복원 테스트 수행 (월 1회 이상!)             │
│    - pg_restore --list backup.dump 으로 내용 확인         │
└─────────────────────────────────────────────────────────┘
```

## ■■■ 8. 유용한 명령어 ■■■

```bash
# 백업 파일 내용 목록 확인
pg_restore --list backup.dump

# 데이터베이스 크기 확인
psql -c "SELECT pg_size_pretty(pg_database_size('study_db'));"

# WAL 위치 확인
psql -c "SELECT pg_current_wal_lsn();"

# 체크포인트 강제 실행
psql -c "CHECKPOINT;"

# 복제 슬롯 삭제 (Standby가 영구히 다운된 경우)
psql -c "SELECT pg_drop_replication_slot('standby_slot');"
```
