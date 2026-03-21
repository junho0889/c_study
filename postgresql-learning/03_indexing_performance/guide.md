# ■■■ PostgreSQL 인덱스 전략 가이드 ■■■

## ■■■ 1. 인덱스 선택 기준 ■■■

| 상황 | 추천 인덱스 | 이유 |
|------|------------|------|
| 등호(=), 범위(<, >, BETWEEN) 검색 | **B-tree** (기본) | 가장 범용적, 대부분의 경우 최선 |
| 등호(=)만 사용 | **Hash** | B-tree보다 약간 작고 빠를 수 있음 |
| 배열 포함(@>), JSONB 포함 검색 | **GIN** | 역색인, 포함 여부 검색에 최적 |
| 전문 검색 (tsvector) | **GIN** | Full-text search 인덱스 |
| 기하학/공간 데이터 (PostGIS) | **GiST** | 거리, 범위, 근접 검색 |
| 시계열/자연 정렬 대용량 테이블 | **BRIN** | 크기 매우 작음, 정렬된 데이터에 적합 |
| IP 주소, 전화번호 | **SP-GiST** | 분할 검색 트리 |

## ■■■ 2. 인덱스 생성 원칙 ■■■

```
[O] 해야 할 것:
  - WHERE 절에 자주 사용되는 컬럼에 인덱스 생성
  - JOIN 조건 컬럼에 인덱스 생성
  - ORDER BY 컬럼에 인덱스 생성 (정렬 비용 제거)
  - 카디널리티(고유 값 수)가 높은 컬럼에 인덱스 (예: email, ID)
  - CONCURRENTLY 옵션으로 생성 (프로덕션)
  - INCLUDE로 커버링 인덱스 활용 (Index-Only Scan)

[X] 하지 말아야 할 것:
  - 작은 테이블(수백 행)에 인덱스 (Seq Scan이 더 빠름)
  - 카디널리티가 낮은 컬럼에 단독 인덱스 (예: status, gender)
  - 자주 UPDATE되는 컬럼에 과도한 인덱스 (쓰기 성능 저하)
  - 사용되지 않는 인덱스 방치 (디스크 낭비 + 쓰기 오버헤드)
```

## ■■■ 3. 복합 인덱스 컬럼 순서 ■■■

```sql
-- 왼쪽 접두사 규칙 (Left-prefix Rule)
CREATE INDEX idx ON table (A, B, C);

-- 이 인덱스가 지원하는 쿼리:
--   WHERE A = ?               -- O (A만 사용)
--   WHERE A = ? AND B = ?     -- O (A, B 사용)
--   WHERE A = ? AND B = ? AND C = ?  -- O (A, B, C 모두 사용)
--   WHERE B = ?               -- X (A 없이 B만 → 인덱스 사용 불가)
--   WHERE C = ?               -- X (A, B 없이 C만 → 사용 불가)
--   WHERE A = ? AND C = ?     -- △ (A는 인덱스 사용, C는 필터)

-- 순서 결정 기준:
-- 1. 등호(=) 조건 컬럼을 앞에
-- 2. 범위(<, >) 조건 컬럼을 뒤에
-- 3. 선택도(selectivity)가 높은 컬럼을 앞에
```

## ■■■ 4. EXPLAIN ANALYZE 핵심 읽기법 ■■■

```
# 좋은 실행 계획 패턴:
  Index Scan / Index Only Scan → 빠름
  Nested Loop (작은 결과집합) → 적절
  actual rows ≈ rows (예측 정확) → 통계 양호

# 나쁜 실행 계획 패턴:
  Seq Scan (대용량 테이블) → 인덱스 필요
  Sort (큰 데이터셋) → 인덱스로 정렬 대체
  actual rows >> rows (예측 실패) → ANALYZE 필요
  Bitmap Heap Scan (Recheck) → 많은 행 접근
```

## ■■■ 5. 인덱스 유지보수 ■■■

```sql
-- 1. 사용되지 않는 인덱스 찾기
SELECT indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND indexrelname NOT LIKE '%_pkey';

-- 2. 인덱스 블로트 확인 및 재구축
REINDEX INDEX CONCURRENTLY idx_name;

-- 3. 통계 갱신
ANALYZE table_name;

-- 4. 인덱스 크기 모니터링
SELECT indexrelname, pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes ORDER BY pg_relation_size(indexrelid) DESC;
```

## ■■■ 6. 성능 최적화 체크리스트 ■■■

```
[ ] EXPLAIN ANALYZE로 느린 쿼리 분석
[ ] 적절한 인덱스 타입 선택 (B-tree, GIN, GiST 등)
[ ] 복합 인덱스 컬럼 순서 최적화
[ ] 부분 인덱스(Partial Index)로 크기 축소
[ ] INCLUDE로 커버링 인덱스 만들기
[ ] 사용 안 하는 인덱스 정리
[ ] 정기적 ANALYZE 실행 (autovacuum이 자동 처리)
[ ] pg_stat_statements로 느린 쿼리 모니터링
[ ] 적절한 work_mem 설정 (정렬/해시 성능)
[ ] 커넥션 풀링 (PgBouncer) 사용
```
