# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   [데이터 연계] 학습 11단계: GraphQL
#   ─ 스키마 · 리졸버 · N+1 · Federation ─
#   ■ 실행 방법: python 11_graphql.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. REST 의 한계와 GraphQL 등장 배경
#   2. 스키마 정의 (Type / Query / Mutation / Subscription)
#   3. 리졸버(Resolver) 의 동작 방식
#   4. N+1 문제와 DataLoader
#   5. 인증 / 권한 / 비용 제한 (depth/complexity)
#   6. Federation (마이크로서비스 통합)
#   7. 실전: 간단한 GraphQL 쿼리/응답 시뮬레이션
#
# ─────────────────────────────────────────────────────────────────────────


def lesson1_rest_limit():
    # =========================================================================
    #   레슨 1 — REST 의 한계
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : REST 한계                  │")
    print("└──────────────────────────────────────┘")
    # ■ Over-fetch:
    #   - GET /orders → 25 컬럼 다 받는데 화면은 3 컬럼만 사용
    #
    # ■ Under-fetch:
    #   - 화면 1 개 표시에 3-5 API 호출 (사용자, 주문, 결제, 배송)
    #
    # ■ 버전 폭증:
    #   - 클라이언트별 다른 응답 형태 요구 → v1.5, v1.6, …
    #
    # ■ GraphQL 의 약속:
    #   - 한 엔드포인트, 클라이언트가 ‘필요한 모양’으로 데이터를 요청
    print(" GraphQL = ‘API 의 셀프서비스’.  단, 서버 복잡도와 trade-off.")
    print()


def lesson2_schema():
    # =========================================================================
    #   레슨 2 — 스키마
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : 스키마                     │")
    print("└──────────────────────────────────────┘")
    sdl = r"""
type User {
  id: ID!
  email: String!
  orders: [Order!]!
}

type Order {
  id: ID!
  amount: Float!
  currency: String!
  user: User!
}

type Query {
  user(id: ID!): User
  recentOrders(limit: Int = 20): [Order!]!
}

type Mutation {
  createOrder(userId: ID!, amount: Float!): Order!
}

type Subscription {
  orderCreated: Order!     # 실시간 푸시
}
"""
    print(sdl)
    # ■ 스키마 = 강한 계약. 자동 문서 + 코드 생성 + 타입 안전.


def lesson3_resolver():
    # =========================================================================
    #   레슨 3 — Resolver
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : Resolver                   │")
    print("└──────────────────────────────────────┘")
    # ■ 리졸버 = ‘각 필드를 어떻게 채우는가’ 의 함수.
    #
    #     Query.user(id) → User                   (직접 DB 조회)
    #         User.orders → [Order]               (해당 user 의 주문 조회)
    #             Order.user → User               (역참조)
    #
    # ■ GraphQL 엔진은 쿼리를 ‘트리’로 보고 각 노드에서 리졸버를 호출.
    print(" 리졸버는 ‘필드 단위의 함수’.  체계적이지만 잘못 짜면 N+1 폭주.")
    print()


def lesson4_n_plus_1():
    # =========================================================================
    #   레슨 4 — N+1 문제
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : N+1                        │")
    print("└──────────────────────────────────────┘")
    # ■ 시나리오: 20 명의 user 와 각 user 의 orders 를 요청
    #   - User 20 명 1 쿼리
    #   - 각 User.orders 리졸버가 따로 SELECT * FROM orders WHERE user_id = ?
    #   → 총 21 쿼리 (1 + 20)
    #
    # ■ 해법: DataLoader
    #   - 같은 tick 안의 요청을 ‘배치’ 로 묶음
    #   - WHERE user_id IN (...) 한 번으로 해결
    #
    # ■ 캐싱:
    #   - 동일 요청 안에서 같은 키는 한 번만 조회 (per-request cache)
    print(" GraphQL 의 가장 흔한 운영 사고 = N+1.  DataLoader 거의 필수.")
    print()


def lesson5_auth_cost():
    # =========================================================================
    #   레슨 5 — 인증 / 권한 / 비용 제한
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 인증/권한/비용             │")
    print("└──────────────────────────────────────┘")
    # ■ 인증: HTTP 헤더(Bearer) → context 에 user 주입.
    # ■ 권한: 리졸버에서 user.role 검사. 또는 @auth(role: "admin") 디렉티브.
    # ■ 비용 제한:
    #   - depth limit: 쿼리 트리의 최대 깊이
    #   - complexity limit: 각 필드의 ‘비용 계산식’ 누적
    #   - persisted queries: 클라이언트 쿼리를 사전 등록 → 임의 쿼리 차단
    #
    # ■ 이유:
    #   - 악성 쿼리로 “user{friends{friends{friends...}}}” 같은 DoS 가능
    print(" GraphQL 은 강력 = 위험. 비용 제한과 persisted query 가 운영 필수.")
    print()


def lesson6_federation():
    # =========================================================================
    #   레슨 6 — Federation
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : Federation                 │")
    print("└──────────────────────────────────────┘")
    # ■ 마이크로서비스 환경에서:
    #   - users 서비스, orders 서비스 각각이 ‘서브그래프’
    #   - 게이트웨이(Apollo Router / Hot Chocolate) 가 ‘하나의 스키마’ 로 합침
    #
    # ■ @key, @external, @requires 등 디렉티브로 ‘소유권 + 의존성’ 명시.
    #
    # ■ 대안:
    #   - Schema Stitching (구식)
    #   - 단일 모놀리식 GraphQL (작은 조직)
    print(" 큰 조직에서 GraphQL Federation 은 ‘BFF + 백엔드 마이크로서비스’의 표준 아키텍처.")
    print()


def lesson7_practice_simulate():
    # =========================================================================
    #   레슨 7 — 쿼리/응답 시뮬레이션
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 쿼리/응답 시뮬레이션       │")
    print("└──────────────────────────────────────┘")
    users = {1: {"id": 1, "email": "a@a.com"}, 2: {"id": 2, "email": "b@b.com"}}
    orders = [{"id": 11, "user_id": 1, "amount": 10}, {"id": 12, "user_id": 1, "amount": 20},
              {"id": 13, "user_id": 2, "amount": 30}]

    def resolve_user(id):
        return users[int(id)]

    def resolve_orders_for_user(user):
        return [o for o in orders if o["user_id"] == user["id"]]

    # 쿼리: { user(id:1){ email orders{ id amount } } }
    selected_user = resolve_user(1)
    response = {
        "data": {
            "user": {
                "email": selected_user["email"],
                "orders": [{"id": o["id"], "amount": o["amount"]} for o in resolve_orders_for_user(selected_user)]
            }
        }
    }
    print(" 쿼리:  { user(id:1){ email orders{ id amount } } }")
    print(" 응답: ", response)
    print()
    # → 클라이언트가 요청한 필드만 응답. over/under-fetch 모두 해결.


# ─────────────────────────────────────────────────────────────────────────
# ■ 연습문제
# ─────────────────────────────────────────────────────────────────────────
#  Q1. N+1 을 DataLoader 없이 해결할 다른 방법이 있는가? (예: SQL 조인 직접)
#  Q2. GraphQL 의 query depth limit 을 너무 작게 잡으면 어떤 사용성 문제?
#  Q3. persisted query 가 보안과 캐시 측면에서 갖는 두 가지 이점?
#  Q4. REST 와 GraphQL 을 한 시스템 안에서 ‘공존’ 시키는 패턴 두 가지?
#  Q5. Federation 의 단점/운영 부담 두 가지를 적어라.


if __name__ == "__main__":
    lesson1_rest_limit()
    lesson2_schema()
    lesson3_resolver()
    lesson4_n_plus_1()
    lesson5_auth_cost()
    lesson6_federation()
    lesson7_practice_simulate()
