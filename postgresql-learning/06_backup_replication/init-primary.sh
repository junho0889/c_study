#!/bin/bash
# ■■■ Primary 서버 초기화 스크립트 ■■■
# 복제 사용자 생성 및 pg_hba.conf 설정

set -e

# ■■■ 복제 전용 사용자 생성 ■■■
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- REPLICATION: 스트리밍 복제 전용 권한
    CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'repl_secure_pw_2025';
    -- 복제 슬롯 생성 (WAL 세그먼트 보관 보장)
    SELECT pg_create_physical_replication_slot('standby_slot');
EOSQL

# ■■■ pg_hba.conf에 복제 허용 추가 ■■■
echo "# ■■■ 복제 허용 설정 ■■■" >> "$PGDATA/pg_hba.conf"
echo "host replication replicator 0.0.0.0/0 scram-sha-256" >> "$PGDATA/pg_hba.conf"

echo "■■■ Primary 초기화 완료! ■■■"
