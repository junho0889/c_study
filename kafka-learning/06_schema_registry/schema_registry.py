"""
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  Kafka 06단계: 스키마 레지스트리 (Schema Registry)               ■
■  스키마 진화, Avro/JSON 스키마 개념, 호환성 규칙, 검증 시뮬레이션  ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
"""


# ============================================================
#  토이 스키마 정의 및 레지스트리
# ============================================================
class Schema:
    """
    간단한 스키마 정의.
    비유: 편지 봉투의 양식 - '보내는 사람', '받는 사람', '우편번호' 칸이
    미리 정해져 있어야 편지가 제대로 전달됩니다.
    """

    def __init__(self, name, version, fields, required=None):
        self.name = name
        self.version = version
        self.fields = fields           # {필드명: 타입}
        self.required = required or list(fields.keys())

    def validate(self, data):
        """데이터가 스키마에 맞는지 검증"""
        errors = []
        # 필수 필드 확인
        for field in self.required:
            if field not in data:
                errors.append(f"필수 필드 '{field}'가 없습니다")

        # 타입 확인
        type_map = {"string": str, "int": int, "float": float, "bool": bool}
        for field, value in data.items():
            if field in self.fields:
                expected_type = self.fields[field]
                # optional 필드의 null 허용
                if value is None and field not in self.required:
                    continue
                if expected_type in type_map:
                    if not isinstance(value, type_map[expected_type]):
                        errors.append(f"'{field}'는 {expected_type}여야 하는데 {type(value).__name__}입니다")

        return len(errors) == 0, errors

    def __repr__(self):
        return f"Schema({self.name} v{self.version}, fields={list(self.fields.keys())})"


class SchemaRegistry:
    """
    스키마 레지스트리: 스키마의 버전 관리 저장소.
    비유: 학교에서 시험지 양식을 보관하는 서류함 - 올해 양식, 작년 양식 모두 보관.
    """

    def __init__(self):
        self.schemas = {}     # {subject: [schema_v1, schema_v2, ...]}
        self.compatibility = {}  # {subject: "BACKWARD"|"FORWARD"|"FULL"}

    def register(self, subject, schema):
        if subject not in self.schemas:
            self.schemas[subject] = []
            self.compatibility[subject] = "BACKWARD"  # 기본값

        # 호환성 체크
        if self.schemas[subject]:
            latest = self.schemas[subject][-1]
            ok, reason = self.check_compatibility(subject, schema, latest)
            if not ok:
                return False, reason

        self.schemas[subject].append(schema)
        return True, f"v{schema.version} 등록 완료"

    def get_latest(self, subject):
        if subject in self.schemas and self.schemas[subject]:
            return self.schemas[subject][-1]
        return None

    def get_all_versions(self, subject):
        return self.schemas.get(subject, [])

    def set_compatibility(self, subject, level):
        self.compatibility[subject] = level

    def check_compatibility(self, subject, new_schema, old_schema):
        mode = self.compatibility.get(subject, "BACKWARD")

        if mode == "BACKWARD":
            return self._check_backward(new_schema, old_schema)
        elif mode == "FORWARD":
            return self._check_forward(new_schema, old_schema)
        elif mode == "FULL":
            back_ok, back_reason = self._check_backward(new_schema, old_schema)
            fwd_ok, fwd_reason = self._check_forward(new_schema, old_schema)
            if back_ok and fwd_ok:
                return True, "FULL 호환"
            reasons = []
            if not back_ok:
                reasons.append(f"BACKWARD 실패: {back_reason}")
            if not fwd_ok:
                reasons.append(f"FORWARD 실패: {fwd_reason}")
            return False, "; ".join(reasons)

        return True, "호환성 검사 없음"

    def _check_backward(self, new_schema, old_schema):
        """
        BACKWARD 호환: 새 스키마로 옛 데이터를 읽을 수 있어야 함.
        -> 새 스키마에 추가된 필드는 optional이어야 함 (필수이면 옛 데이터에 없으니까).
        -> 옛 스키마의 필수 필드를 새 스키마에서 삭제하면 안 됨.
        """
        # 새로 추가된 필드가 required이면 안 됨
        for field in new_schema.fields:
            if field not in old_schema.fields:
                if field in new_schema.required:
                    return False, f"새 필수 필드 '{field}' 추가 불가 (BACKWARD 위반)"

        return True, "BACKWARD 호환"

    def _check_forward(self, new_schema, old_schema):
        """
        FORWARD 호환: 옛 스키마로 새 데이터를 읽을 수 있어야 함.
        -> 옛 스키마의 필수 필드를 새 스키마에서 삭제하면 안 됨.
        """
        for field in old_schema.required:
            if field not in new_schema.fields:
                return False, f"기존 필수 필드 '{field}' 삭제 불가 (FORWARD 위반)"

        return True, "FORWARD 호환"


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 1: 스키마가 왜 필요한가?                               │
# │  비유: 편지 봉투 양식 - 칸이 정해져 있어야 제대로 전달됨      │
# └─────────────────────────────────────────────────────────────┘
def lesson1_why_schema():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 1: 스키마가 왜 필요한가?                      │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 프로듀서와 컨슈머가 데이터를 주고받을 때,
    # '이 데이터에 어떤 필드가 있고, 어떤 타입인지' 약속이 필요합니다.
    # 편지 봉투에 칸이 정해져 있어야 우체국이 제대로 분류하는 것처럼요!

    schema = Schema("User", 1, {
        "name": "string",
        "age": "int",
        "email": "string",
    })

    # 올바른 데이터
    valid_data = {"name": "김민수", "age": 12, "email": "minsu@school.kr"}
    ok, errors = schema.validate(valid_data)
    print(f"  올바른 데이터: {valid_data}")
    print(f"  검증 결과: {'통과' if ok else '실패'}")

    # 잘못된 데이터
    bad_data = {"name": "김민수", "age": "열두살"}  # age가 문자열, email 누락
    ok, errors = schema.validate(bad_data)
    print(f"\n  잘못된 데이터: {bad_data}")
    print(f"  검증 결과: {'통과' if ok else '실패'}")
    for err in errors:
        print(f"    - {err}")
    print("  -> 스키마가 있으면 잘못된 데이터가 들어오는 것을 미리 막을 수 있습니다!")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 2: 스키마 레지스트리 - 버전별 양식 보관함               │
# └─────────────────────────────────────────────────────────────┘
def lesson2_registry():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 2: 스키마 레지스트리 - 버전별 양식 보관함      │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 스키마 레지스트리는 스키마의 '버전 관리 저장소'입니다.
    # 학교 서류함에 올해 시험지 양식, 작년 양식을 모두 보관하는 것과 같아요.
    # 프로듀서가 메시지를 보낼 때 스키마 ID를 함께 보내면,
    # 컨슈머가 해당 ID로 레지스트리에서 스키마를 찾아 데이터를 읽습니다.

    registry = SchemaRegistry()

    schema_v1 = Schema("User", 1, {"name": "string", "age": "int"})
    ok, msg = registry.register("user-value", schema_v1)
    print(f"  v1 등록: {msg}")

    # v2: email 필드 추가 (optional)
    schema_v2 = Schema("User", 2,
                        {"name": "string", "age": "int", "email": "string"},
                        required=["name", "age"])  # email은 optional
    ok, msg = registry.register("user-value", schema_v2)
    print(f"  v2 등록: {msg}")

    print(f"  최신 스키마: {registry.get_latest('user-value')}")
    print(f"  전체 버전: {registry.get_all_versions('user-value')}")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 3: BACKWARD 호환 - 새 스키마로 옛 데이터 읽기          │
# │  비유: 새 시험지 양식으로 작년 답안도 채점할 수 있어야 함      │
# └─────────────────────────────────────────────────────────────┘
def lesson3_backward_compatibility():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 3: BACKWARD 호환                              │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # BACKWARD 호환: 새 스키마(컨슈머)가 옛 데이터(프로듀서)를 읽을 수 있어야 합니다.
    # 새 시험지에 '서술형' 칸이 추가되었는데, 작년 답안지에는 그 칸이 없어요.
    # 그래도 채점할 수 있으려면 '서술형'을 선택 사항(optional)으로 해야 합니다!

    registry = SchemaRegistry()
    registry.set_compatibility("user-value", "BACKWARD")

    v1 = Schema("User", 1, {"name": "string", "age": "int"})
    registry.register("user-value", v1)

    # 호환되는 변경: optional 필드 추가
    v2_ok = Schema("User", 2,
                    {"name": "string", "age": "int", "phone": "string"},
                    required=["name", "age"])  # phone은 optional
    ok, msg = registry.register("user-value", v2_ok)
    print(f"  optional 필드 추가: {'성공' if ok else '실패'} - {msg}")

    # 호환되지 않는 변경: required 필드 추가
    registry2 = SchemaRegistry()
    registry2.set_compatibility("order-value", "BACKWARD")
    v1_order = Schema("Order", 1, {"item": "string", "qty": "int"})
    registry2.register("order-value", v1_order)

    v2_bad = Schema("Order", 2,
                     {"item": "string", "qty": "int", "coupon": "string"},
                     required=["item", "qty", "coupon"])  # coupon이 필수!
    ok, msg = registry2.register("order-value", v2_bad)
    print(f"  required 필드 추가: {'성공' if ok else '실패'} - {msg}")
    print("  -> 기존 데이터에 'coupon'이 없으므로 BACKWARD 위반!")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 4: FORWARD / FULL 호환                                │
# └─────────────────────────────────────────────────────────────┘
def lesson4_forward_full():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 4: FORWARD / FULL 호환                        │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # FORWARD: 옛 스키마(컨슈머)가 새 데이터(프로듀서)를 읽을 수 있어야 합니다.
    # FULL: BACKWARD + FORWARD 모두 만족해야 합니다.

    print("  ┌───────────┬──────────────────────────────────────────────┐")
    print("  │ 호환 모드  │ 설명                                        │")
    print("  ├───────────┼──────────────────────────────────────────────┤")
    print("  │ BACKWARD  │ 새 컨슈머가 옛 데이터를 읽을 수 있음          │")
    print("  │           │ -> 필드 추가는 optional만 가능                │")
    print("  │ FORWARD   │ 옛 컨슈머가 새 데이터를 읽을 수 있음          │")
    print("  │           │ -> 기존 필수 필드 삭제 불가                   │")
    print("  │ FULL      │ 양방향 모두 가능                             │")
    print("  │           │ -> 가장 안전하지만 제약이 많음                │")
    print("  │ NONE      │ 호환성 검사 안 함 (위험!)                    │")
    print("  └───────────┴──────────────────────────────────────────────┘")

    # FORWARD 호환 시뮬레이션
    registry = SchemaRegistry()
    registry.set_compatibility("product-value", "FORWARD")

    v1 = Schema("Product", 1, {"name": "string", "price": "int"}, required=["name", "price"])
    registry.register("product-value", v1)

    # 기존 필수 필드 삭제 시도 -> FORWARD 위반
    v2_bad = Schema("Product", 2, {"name": "string"}, required=["name"])
    ok, msg = registry.register("product-value", v2_bad)
    print(f"\n  FORWARD: 필수 필드 'price' 삭제 시도: {'성공' if ok else '실패'}")
    print(f"  사유: {msg}")
    print()


# ┌─────────────────────────────────────────────────────────────┐
# │  레슨 5: 전체 흐름 시뮬레이션                                │
# └─────────────────────────────────────────────────────────────┘
def lesson5_full_flow():
    print("┌─────────────────────────────────────────────────────┐")
    print("│  레슨 5: 전체 흐름 시뮬레이션                       │")
    print("└─────────────────────────────────────────────────────┘")
    print()
    # 프로듀서 -> 스키마 레지스트리 -> 브로커 -> 스키마 레지스트리 -> 컨슈머

    registry = SchemaRegistry()
    schema = Schema("Event", 1, {"type": "string", "user_id": "int", "timestamp": "string"})
    registry.register("event-value", schema)

    # 프로듀서: 스키마 검증 후 전송
    messages = [
        {"type": "login", "user_id": 1001, "timestamp": "2024-01-15T10:00:00"},
        {"type": "click", "user_id": 1002, "timestamp": "2024-01-15T10:01:00"},
        {"type": "error", "user_id": "abc", "timestamp": "2024-01-15T10:02:00"},  # user_id 타입 오류
    ]

    broker_topic = []

    print("  [프로듀서] 메시지 전송 시 스키마 검증:")
    for msg in messages:
        current_schema = registry.get_latest("event-value")
        ok, errors = current_schema.validate(msg)
        if ok:
            broker_topic.append({"schema_id": current_schema.version, "data": msg})
            print(f"    통과 -> 전송: {msg['type']} (user={msg['user_id']})")
        else:
            print(f"    거부: {msg}")
            for e in errors:
                print(f"      - {e}")

    print(f"\n  [브로커] 저장된 메시지: {len(broker_topic)}개")
    print()
    print("  [컨슈머] 스키마 ID로 레지스트리에서 스키마를 찾아 역직렬화:")
    for record in broker_topic:
        s = registry.get_all_versions("event-value")[record["schema_id"] - 1]
        print(f"    스키마 v{s.version}로 읽기: {record['data']}")
    print()


def main():
    print("=" * 72)
    print("  Kafka 06단계: 스키마 레지스트리 (Schema Registry)")
    print("=" * 72)
    print()

    lesson1_why_schema()
    lesson2_registry()
    lesson3_backward_compatibility()
    lesson4_forward_full()
    lesson5_full_flow()


if __name__ == "__main__":
    main()
