# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [데이터 연계] 학습 10단계: FastAPI 실전
#   ─ Pydantic · async · DI · OpenAPI · 테스트 ─
#   ■ 실행 방법: python 10_fastapi_in_practice.py   (FastAPI 가 설치되어 있으면 코드를 그대로 실행)
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. FastAPI 의 설계 철학 (typed Python + ASGI)
#   2. Pydantic 모델 — 입력/출력의 ‘계약’
#   3. async / await — 동기 vs 비동기 핸들러
#   4. Dependency Injection 으로 ‘공유 자원’ 다루기
#   5. 미들웨어 / 예외 처리기 / CORS
#   6. OpenAPI 자동 생성 + 테스트
#   7. 실전: 미니 API 서버 의사코드 (Order CRUD)
#
# ─────────────────────────────────────────────────────────────────────────


def lesson1_design():
    # =========================================================================
    #   레슨 1 — FastAPI 철학
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : FastAPI 철학               │")
    print("└──────────────────────────────────────┘")
    # ■ 핵심: ‘Type Hint = 검증 + 직렬화 + 문서’
    #   - 함수 시그니처가 곧 API 명세
    #
    # ■ 기반:
    #   - Starlette (ASGI 웹 프레임워크)
    #   - Pydantic v2 (데이터 검증)
    #
    # ■ 장점:
    #   - 빠름 (Node/Go 와 같은 급)
    #   - 자동 OpenAPI / Swagger UI
    #   - 비동기 친화
    print(" FastAPI = ‘타입 → 검증 → 문서’ 의 자동화.  Python 3.10+ 의 표준 API 프레임워크.")
    print()


def lesson2_pydantic():
    # =========================================================================
    #   레슨 2 — Pydantic 모델
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : Pydantic                   │")
    print("└──────────────────────────────────────┘")
    code = r"""
from pydantic import BaseModel, Field, EmailStr
from typing import Literal
from datetime import datetime

class OrderIn(BaseModel):
    user_id: int = Field(gt=0)
    amount: float = Field(ge=0)
    currency: Literal["KRW","USD"] = "KRW"
    note: str | None = None

class OrderOut(OrderIn):
    id: int
    created_at: datetime

# 검증:
# OrderIn(user_id=-1, amount=10)  → ValidationError
"""
    print(code)
    # ■ 핵심:
    #   - Literal / EmailStr / 제약 조건은 ‘API 와 ETL’ 의 공통 자산
    #   - Pydantic 모델을 DB 저장용 / API DTO 로 ‘다른 인스턴스’ 로 분리해두면 운영이 깔끔


def lesson3_async():
    # =========================================================================
    #   레슨 3 — async / await
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : async / await              │")
    print("└──────────────────────────────────────┘")
    # ■ 언제 async?
    #   - I/O 대기(DB / HTTP / Redis) 가 주된 작업이면 async 가 throughput 에 유리
    #   - CPU bound 면 일반 def + thread pool / worker process 가 더 안전
    #
    # ■ 주의:
    #   - 동기(blocking) 라이브러리(psycopg2, requests) 를 async 핸들러 안에서 호출하면 이벤트 루프 정지
    #   - asyncpg, httpx, aiomysql 같은 async 친화 라이브러리 사용
    print(" async 는 ‘동시 I/O 많은 워크로드’의 도구.  잘못 쓰면 더 느려질 수 있다.")
    print()


def lesson4_di():
    # =========================================================================
    #   레슨 4 — Dependency Injection
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : DI                         │")
    print("└──────────────────────────────────────┘")
    code = r"""
from fastapi import Depends, FastAPI

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def current_user(token: str = Header(...)):
    return decode_token(token)

@app.get("/me")
def me(user = Depends(current_user)):
    return user

@app.get("/orders")
def list_orders(db = Depends(get_db), user = Depends(current_user)):
    return db.query(Order).filter_by(user_id=user.id).all()
"""
    print(code)
    # ■ 효과:
    #   - 인증/세션/DB 등 ‘공유 자원’ 을 핸들러 시그니처로 명시
    #   - 테스트에서 의존성 ‘override’ 로 손쉽게 모킹


def lesson5_middleware_cors():
    # =========================================================================
    #   레슨 5 — 미들웨어 / 예외 / CORS
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : Middleware / CORS          │")
    print("└──────────────────────────────────────┘")
    code = r"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    rid = request.headers.get("x-request-id", uuid4().hex)
    response = await call_next(request)
    response.headers["x-request-id"] = rid
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=422, content={"errors": exc.errors()})
"""
    print(code)
    # ■ 미들웨어 / CORS / 에러 핸들러는 ‘프레임워크 표준 패턴’ — 모든 서비스에서 비슷.


def lesson6_openapi_test():
    # =========================================================================
    #   레슨 6 — OpenAPI / 테스트
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : OpenAPI / 테스트           │")
    print("└──────────────────────────────────────┘")
    # ■ OpenAPI:
    #   - /docs (Swagger UI), /redoc 자동 생성
    #   - openapi.json 을 코드 생성 도구(openapi-generator, fern)에 넘기면 SDK 자동 생성
    #
    # ■ 테스트:
    #     from fastapi.testclient import TestClient
    #     client = TestClient(app)
    #     r = client.get("/orders")
    #     assert r.status_code == 200
    #
    # ■ 권장:
    #   - 단위 테스트 + 계약 테스트(스키마)
    #   - 통합 테스트: testcontainers 로 실제 Postgres/Redis 띄우기
    print(" 자동 문서 + 자동 SDK + 자동 테스트 — 비용 큰 작업이 모두 ‘공짜’가 된다.")
    print()


def lesson7_practice_pseudo_order_api():
    # =========================================================================
    #   레슨 7 — 미니 API 의사코드
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : Order CRUD                 │")
    print("└──────────────────────────────────────┘")
    code = r"""
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Literal

app = FastAPI(title="Orders API", version="1.0.0")

# 메모리 ‘DB’
_db: dict[int, dict] = {}
_seq = {"id": 0}

class OrderIn(BaseModel):
    user_id: int = Field(gt=0)
    amount: float = Field(ge=0)
    currency: Literal["KRW","USD"] = "KRW"

class OrderOut(OrderIn):
    id: int

def auth(token: str = "demo"):
    if token != "demo":
        raise HTTPException(401, "invalid token")
    return {"sub": "demo-user"}

@app.post("/v1/orders", response_model=OrderOut, status_code=201)
def create(o: OrderIn, user = Depends(auth)):
    _seq["id"] += 1
    new = {"id": _seq["id"], **o.model_dump()}
    _db[new["id"]] = new
    return new

@app.get("/v1/orders/{oid}", response_model=OrderOut)
def get_one(oid: int, user = Depends(auth)):
    row = _db.get(oid)
    if not row:
        raise HTTPException(404, "not found")
    return row

@app.delete("/v1/orders/{oid}", status_code=204)
def delete(oid: int, user = Depends(auth)):
    _db.pop(oid, None)
"""
    print(code)


# ─────────────────────────────────────────────────────────────────────────
# ■ 연습문제
# ─────────────────────────────────────────────────────────────────────────
#  Q1. async 핸들러에서 ‘동기 라이브러리 호출’ 을 안전히 다루는 2 가지 방법은?
#  Q2. DI 로 의존성을 override 하여 테스트에서 외부 DB 를 모킹하는 패턴을 설명하라.
#  Q3. CORS 가 잘못 설정되었을 때 흔히 발생하는 두 가지 증상은?
#  Q4. Pydantic v2 의 model_dump vs dict() 차이가 마이그레이션에서 왜 중요한가?
#  Q5. OpenAPI 스펙 변경 시, 클라이언트 SDK 자동 생성 워크플로의 장점 두 가지?


if __name__ == "__main__":
    lesson1_design()
    lesson2_pydantic()
    lesson3_async()
    lesson4_di()
    lesson5_middleware_cors()
    lesson6_openapi_test()
    lesson7_practice_pseudo_order_api()
