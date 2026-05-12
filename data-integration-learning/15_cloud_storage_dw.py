# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [데이터 연계] 학습 15단계: 클라우드 스토리지 & DW
#   ─ S3/GCS/Azure Blob · BigQuery/Snowflake/Redshift · Lakehouse ─
#   ■ 실행 방법: python 15_cloud_storage_dw.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 객체 스토리지 (S3 / GCS / Azure Blob) 의 본질
#   2. 클라우드 DW: BigQuery / Snowflake / Redshift / Databricks
#   3. Lakehouse: Delta Lake / Apache Iceberg / Hudi
#   4. 비용/성능 모델 — Storage / Compute 분리
#   5. 권한과 데이터 거버넌스 (IAM, Lake Formation, Unity Catalog)
#   6. 데이터 공유 (Sharing, Data Clean Room)
#   7. 실전: S3 → Parquet → Iceberg → BigQuery 동기화 흐름 그리기
#
# ─────────────────────────────────────────────────────────────────────────


def lesson1_object_storage():
    # =========================================================================
    #   레슨 1 — 객체 스토리지
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 객체 스토리지              │")
    print("└──────────────────────────────────────┘")
    # ■ 특징:
    #   - 무한 확장 가능, GB 당 매우 저렴
    #   - 키-값 (key = path) 인터페이스
    #   - HTTP API (S3 호환이 사실상 표준)
    #
    # ■ 자주 쓰이는 기능:
    #   - 버전 관리 (versioning)
    #   - 객체 잠금(WORM)
    #   - 수명 주기(lifecycle): Standard → Glacier 자동 이행
    #   - 서버사이드 암호화 (SSE-S3 / SSE-KMS / SSE-C)
    #
    # ■ 함정:
    #   - 단일 객체 read-modify 가 비싸다 (해체 + 재업로드) → append 형 작업 비효율
    #   - 강한 일관성 = 최근에야 보장(AWS S3 2020+, GCS, Azure 도 강 일관성 모드 존재)
    print(" 객체 스토리지 = ‘무한 큰 디스크’의 비유. 하지만 read-modify 는 비싸다.")
    print()


def lesson2_cloud_dw():
    # =========================================================================
    #   레슨 2 — 클라우드 DW
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : 클라우드 DW                │")
    print("└──────────────────────────────────────┘")
    # ■ BigQuery (GCP)
    #   - serverless, scan 단위 과금
    #   - 강력한 SQL + UDF + ML (BQML)
    # ■ Snowflake
    #   - 멀티 클러스터 가상 웨어하우스
    #   - Sharing/Marketplace 강점
    # ■ Redshift (AWS)
    #   - 노드 기반 + Redshift Serverless
    #   - Spectrum 으로 S3 직접 쿼리
    # ■ Databricks SQL / Photon
    #   - Lakehouse 진영의 SQL 엔진. Delta Lake 위에서 동작
    #
    # ■ 공통점:
    #   - Storage 와 Compute 분리
    #   - SQL 표준 + 풍부한 ML/JSON 지원
    print(" 클라우드 DW 의 공식: ‘compute/storage 분리 + 분당 과금 + 자동 확장’.")
    print()


def lesson3_lakehouse():
    # =========================================================================
    #   레슨 3 — Lakehouse
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : Lakehouse                  │")
    print("└──────────────────────────────────────┘")
    # ■ 핵심:
    #   - 파일(Parquet/ORC) 위에 ‘트랜잭션 로그’ 를 얹어 DW 기능 제공
    #
    # ■ 비교:
    #   - Delta Lake (Databricks 주도)
    #   - Apache Iceberg (Netflix 출발, 가장 ‘오픈’ 표준)
    #   - Apache Hudi (Uber 출발, CDC/스트림 친화)
    #
    # ■ 공통 기능:
    #   - ACID 트랜잭션
    #   - 시간 여행(time travel)
    #   - 스키마 진화
    #   - 파티션 evolution
    #   - 통계/manifest 로 효율적 pruning
    print(" Iceberg/Delta/Hudi = ‘오픈 포맷의 DW 화’.  벤더 락인 회피의 핵심 도구.")
    print()


def lesson4_cost_model():
    # =========================================================================
    #   레슨 4 — 비용/성능 모델
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : 비용 모델                  │")
    print("└──────────────────────────────────────┘")
    # ■ 두 자원:
    #   - Storage: GB·month
    #   - Compute: 쿼리당 scan / 시간당 vCPU / credit
    #
    # ■ 절감 패턴:
    #   - 파티션 + 클러스터링 → scan 줄임
    #   - Materialized View, Aggregate Table
    #   - 다단계 압축 (Parquet + dict + RLE + ZSTD)
    #   - 쿼리 캐시 활용
    #   - “쿼리 인가” 와 “스캔 한도” 로 사고 방지
    print(" 가장 큰 비용 절감 = ‘파티션 잘 자르기 + 쿼리 한도 설정’.")
    print()


def lesson5_governance():
    # =========================================================================
    #   레슨 5 — 거버넌스
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : IAM / 거버넌스             │")
    print("└──────────────────────────────────────┘")
    # ■ AWS:
    #   - IAM 정책 + Lake Formation (행/열 수준)
    # ■ GCP:
    #   - IAM + BigQuery Authorized View + Data Catalog Policy Tags
    # ■ Azure:
    #   - Purview + Synapse 데이터 거버넌스
    # ■ Databricks:
    #   - Unity Catalog: 카탈로그/스키마/테이블/행/열 수준 + lineage
    #
    # ■ 권장 원칙:
    #   - Least privilege
    #   - 사용자 ID 기반(개인 키 X)
    #   - 모든 쿼리/접근 로그 + 보존
    print(" 데이터 거버넌스 = ‘카탈로그 + 정책 엔진 + 감사 로그’ 의 통합.")
    print()


def lesson6_sharing():
    # =========================================================================
    #   레슨 6 — 데이터 공유
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 데이터 공유                │")
    print("└──────────────────────────────────────┘")
    # ■ Snowflake Sharing / BigQuery Sharing / Delta Sharing:
    #   - 데이터 ‘복제 없이’ 다른 조직에 안전 공유
    #   - 비용 절감 + 최신성 보장
    #
    # ■ Data Clean Room:
    #   - 양쪽 회사가 ‘원본을 노출하지 않고’ 결합 분석
    #   - 광고/금융 협업의 새 표준
    print(" 데이터 공유는 ‘복제 없이 안전하게’.  계약 + 정책으로 강화.")
    print()


def lesson7_practice_flow():
    # =========================================================================
    #   레슨 7 — 통합 흐름 그리기
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : S3 → Iceberg → BigQuery    │")
    print("└──────────────────────────────────────┘")
    diagram = r"""
   소스 시스템 ──── Kafka(CDC) ────────────────┐
                                                  ▼
   S3 (raw zone, JSON)                       Flink / Spark Structured Streaming
        │                                          │
        │  Spark/Trino 변환                        │ 저장
        ▼                                          ▼
   S3 (curated zone, Parquet)            ───▶ Apache Iceberg 테이블 (ACID)
                                                  │
                                ┌─────────────────┼─────────────────┐
                                ▼                 ▼                 ▼
                          BigQuery Federation  Snowflake Iceberg  Databricks Unity
                          (외부 테이블)         (직접 쿼리)         (Unity Catalog)
"""
    print(diagram)
    # 핵심: ‘Iceberg 가 진실의 원본(SoT), 각 DW 는 컴퓨트 엔진’.


# ─────────────────────────────────────────────────────────────────────────
# ■ 연습문제
# ─────────────────────────────────────────────────────────────────────────
#  Q1. 한 쿼리가 100TB scan 으로 폭주했을 때 DW 가 사고를 막는 안전장치 두 가지?
#  Q2. Iceberg 의 ‘hidden partitioning’ 이 일반 Hive 파티션 대비 운영 측면에서 강한 점?
#  Q3. Snowflake 의 zero-copy clone 이 dev/test 비용을 어떻게 절감하나?
#  Q4. 데이터 공유에서 ‘복제’와 ‘공유’의 보안/비용 trade-off 를 비교하라.
#  Q5. PII 가 포함된 컬럼에 대한 거버넌스 정책(마스킹, 토큰화)을 한 줄로 설계하라.


if __name__ == "__main__":
    lesson1_object_storage()
    lesson2_cloud_dw()
    lesson3_lakehouse()
    lesson4_cost_model()
    lesson5_governance()
    lesson6_sharing()
    lesson7_practice_flow()
