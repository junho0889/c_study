#!/bin/bash
# ■■■ 프로덕션 초기화 스크립트 ■■■
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- 앱 서비스 계정 생성
    CREATE ROLE app_service LOGIN PASSWORD 'app_service_pw_2025!';
    GRANT CONNECT ON DATABASE study_db TO app_service;
    GRANT USAGE ON SCHEMA public TO app_service;

    -- 모니터링 전용 계정 (exporter용)
    CREATE ROLE monitoring LOGIN PASSWORD 'monitoring_pw_2025!';
    GRANT pg_monitor TO monitoring;

    -- pg_stat_statements 확장 (느린 쿼리 추적)
    CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

    SELECT '■■■ 프로덕션 초기화 완료! ■■■' AS message;
EOSQL

echo "■■■ 프로덕션 초기화 스크립트 실행 완료 ■■■"
