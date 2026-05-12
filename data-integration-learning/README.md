# 데이터 연계 (ETL · API · 클라우드) 학습 가이드

**ETL 파이프라인 · API 서버 · 클라우드 데이터 통합** 의 3 축을 한 번에 학습하는 **19단계** 종합 교재입니다.
모든 코드에 한글 주석, 비유, ASCII 다이어그램, 실전 예제, 연습문제가 포함되어 있습니다.

> 이 가이드는 `python-learning`, `pandas-learning`, `postgresql-learning`, `kafka-learning`,
> `rest-api-learning`, `grpc-learning`, `docker-learning`, `kubernetes-learning` 과 함께
> 학습하면 시너지가 큽니다.

## 학습 로드맵 한 줄 요약

```
   기초개념 ─▶ ETL/ELT ─▶ 오케스트레이션 ─▶ API Server ─▶ 클라우드 통합 ─▶ 실전 파이프라인
                  │                                  │
                  └── 데이터 품질 / CDC               └── 인증 · 캐싱 · 이벤트 아키텍처
```

## 커리큘럼

### PART 1 — 데이터 통합 기초 (01~02)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 01 | 데이터 통합 개념 | ETL vs ELT, 배치 vs 스트림, 데이터 메시, Lakehouse |
| 02 | 데이터 소스/포맷 | RDB / NoSQL / 파일(CSV/JSON/Parquet/Avro), 스키마 진화 |

### PART 2 — ETL 파이프라인 (03~08)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 03 | ETL 기초 | Extract / Transform / Load 패턴, idempotency, 재시도 |
| 04 | Pandas / Polars ETL | DataFrame 변환, 청크 처리, 메모리 관리 |
| 05 | SQL ETL & dbt | CTE / Window / dbt 모델·테스트 |
| 06 | Airflow / Prefect / Dagster | DAG, 스케줄링, 백필, 의존성 |
| 07 | CDC (Change Data Capture) | Debezium, log-based, outbox 패턴 |
| 08 | 데이터 품질 | Great Expectations, schema validation, lineage |

### PART 3 — API Server (09~14)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 09 | REST API 기초 | HTTP 메서드, 상태코드, REST 원칙, 버전 관리 |
| 10 | FastAPI 실전 | Pydantic, 비동기, dependency injection, OpenAPI |
| 11 | GraphQL | 스키마, 리졸버, N+1 문제, Federation |
| 12 | gRPC & Protobuf | IDL, 단방향/양방향 스트리밍, 직렬화 |
| 13 | 인증 / 인가 | JWT, OAuth2, API Key, mTLS, RBAC/ABAC |
| 14 | Rate Limit & Caching | 토큰버킷, 슬라이딩 윈도우, Redis, CDN, HTTP cache |

### PART 4 — 클라우드 데이터 연계 (15~17)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 15 | 클라우드 스토리지 & DW | S3/GCS/Azure Blob, BigQuery/Snowflake/Redshift, 데이터 레이크/Lakehouse |
| 16 | 메시지/스트리밍 | Kafka, Kinesis, Pub/Sub, exactly-once, schema registry |
| 17 | 매니지드 ETL & 이벤트 | AWS Glue, Dataflow, Data Factory, EventBridge, Lambda |

### PART 5 — 저장 전략 (18)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 18 | 파티셔닝 / 샤딩 / 보존 | Range·List·Hash·Composite, 분기/월/일 파티션 SQL, TimescaleDB·ClickHouse·Iceberg, Tiering(Hot/Warm/Cold), Retention/Archive |

### PART 6 — 통합 실전 프로젝트 (19)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 19 | End-to-End 파이프라인 | 멀티 소스 → CDC + ETL → DW → API → 알림 한 흐름으로 |

## 학습 방법

1. **순서대로 학습** — 뒤로 갈수록 앞 단계 개념(스키마, 멱등성, 비동기)을 재활용합니다.
2. 모든 코드는 “설명용 미니 구현”입니다. 실제 운영은 표시된 도구/라이브러리로 대체하세요.
3. 각 챕터 끝의 **연습문제** 를 직접 풀어보세요.
4. 본인의 사내 데이터(매출/로그/센서)에 즉시 적용해보면 학습 효과가 큽니다.

## 의존 라이브러리 / 도구 맵

```
ETL              : pandas, polars, duckdb, dbt, sqlglot
오케스트레이션   : Airflow, Prefect, Dagster, Argo Workflows
CDC              : Debezium, Maxwell, AWS DMS
데이터 품질      : Great Expectations, Soda, dbt tests
API 서버         : FastAPI, Express, Spring Boot, gRPC, GraphQL (strawberry, ariadne)
메시지 큐        : Kafka (Confluent), Redpanda, Kinesis, Pub/Sub, RabbitMQ
캐시 / 게이트웨이: Redis, Memcached, Nginx, Envoy, Kong, Apigee
클라우드 ETL     : AWS Glue, Dataflow, Azure Data Factory, Fivetran, Airbyte
DW / Lakehouse   : BigQuery, Snowflake, Redshift, Databricks, Delta Lake, Apache Iceberg
관측 / 거버넌스  : OpenTelemetry, DataDog, OpenLineage, Atlas, DataHub
```

## “ETL · API · 클라우드” 세 영역이 한 코스인 이유

```
              ┌──────────────┐
   소스시스템 →│   ETL        │→ DW / Lake
              └──────────────┘
                      │
                      ▼
              ┌──────────────┐
              │  API Server  │   ←─ 사용자 / 서비스
              └──────────────┘
                      │
                      ▼
              ┌──────────────┐
              │  클라우드    │   ←─ 메시지큐 / 이벤트
              └──────────────┘
```

세 영역은 “데이터의 입수 → 가공 → 노출 → 전파”라는 하나의 흐름이며,
하나만 잘 알면 운영 사고가 반드시 인접 영역에서 터집니다.
한 흐름으로 배우는 것이 가장 효율적이라는 것이 이 가이드의 전제입니다.
