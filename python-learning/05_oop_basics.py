# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   파이썬 학습 05단계: 객체지향 프로그래밍(OOP) 완전정복
#   ─ 클래스, 상속, 매직 메서드, 추상 클래스 ─
#
#   이 파일 하나로 파이썬 OOP의 모든 핵심 개념을 마스터합니다.
#   코드를 직접 타이핑하고, 값을 바꿔보면서 실험하세요!
#
#   ■ 실행 방법 (터미널에 입력)
#     python 05_oop_basics.py
#
#   ■ OOP란?
#     데이터(속성)와 행동(메서드)을 하나로 묶어서 관리하는 프로그래밍 방식입니다.
#     C++ : class MyClass { ... };
#     파이썬: class MyClass: ...
#     → 파이썬이 훨씬 유연하고 간결합니다!
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 클래스와 객체 기초
#   2. 인스턴스 변수 vs 클래스 변수
#   3. 메서드 종류 (인스턴스, 클래스, 정적)
#   4. 매직 메서드(던더 메서드) 완전정복
#   5. 프로퍼티(@property)
#   6. 상속(Inheritance)
#   7. 다중상속과 MRO
#   8. 추상 클래스와 인터페이스
#   9. 캡슐화와 접근 제어
#  10. 실전: 동물원 관리 시스템
#
# ─────────────────────────────────────────────────────────────────────────

from abc import ABC, abstractmethod


def lesson1_class_and_object():
    # =========================================================================
    #
    #   레슨 1 — 클래스와 객체 기초
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 클래스와 객체 기초         │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 클래스란? 객체란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   클래스 = 설계도 (붕어빵 틀)
    #   객체   = 설계도로 만든 실제 물건 (붕어빵)
    #
    #   비유: 붕어빵 틀(클래스) 하나로 붕어빵(객체) 여러 개를 만듦
    #         각 붕어빵에 팥, 슈크림, 피자 등 다른 속을 넣을 수 있음(속성)
    #
    #   C++ : class Dog { public: string name; Dog(string n) : name(n) {} };
    #   파이썬: 아래처럼 훨씬 간단!
    #

    class Dog:
        # __init__은 생성자! 객체가 만들어질 때 자동으로 호출됩니다.
        # C++의 생성자와 같은 역할입니다.
        def __init__(self, name, breed):
            # self = "방금 만들어진 나 자신"을 가리킵니다.
            # C++의 this 포인터와 같지만, 반드시 첫 번째 매개변수에 적어야 합니다!
            self.name = name        # 인스턴스 변수 (각 객체마다 다른 값)
            self.breed = breed
            self.tricks = []        # 빈 리스트로 초기화

        def learn_trick(self, trick):
            self.tricks.append(trick)
            print(f"  {self.name}이(가) '{trick}'을 배웠어요!")

        def show_info(self):
            tricks_str = ", ".join(self.tricks) if self.tricks else "아직 없음"
            print(f"  이름: {self.name}, 품종: {self.breed}, 기술: {tricks_str}")

    # 객체(인스턴스) 생성
    dog1 = Dog("멍멍이", "골든 리트리버")
    dog2 = Dog("초코", "푸들")

    # 각 객체는 독립적! (멍멍이가 배운 기술이 초코에게 전해지지 않음)
    dog1.learn_trick("앉아")
    dog1.learn_trick("악수")
    dog2.learn_trick("점프")

    dog1.show_info()
    dog2.show_info()

    # ★ 자주 하는 실수: self를 빼먹으면?
    # def learn_trick(trick):  ← self가 없으면 호출 시 TypeError!
    # 파이썬은 메서드 호출 시 자동으로 객체 자신을 첫 인자로 넘깁니다.

    # isinstance로 타입 확인
    print(f"  dog1은 Dog인가? {isinstance(dog1, Dog)}")
    print()


def lesson2_instance_vs_class_variable():
    # =========================================================================
    #
    #   레슨 2 — 인스턴스 변수 vs 클래스 변수
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : 인스턴스 변수 vs 클래스 변수│")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 인스턴스 변수 vs 클래스 변수
    # ─────────────────────────────────────────────────────────────────────
    #
    #   인스턴스 변수: 각 객체마다 따로 가지는 변수 (self.xxx)
    #                  비유: 각 학생의 이름, 점수 (사람마다 다름)
    #
    #   클래스 변수:   모든 객체가 공유하는 변수 (class 바로 아래)
    #                  비유: 학교 이름, 교훈 (모든 학생이 같은 학교)
    #
    #   C++ : static 멤버 변수 = 클래스 변수와 비슷
    #

    class Student:
        # 클래스 변수 (모든 Student 객체가 공유)
        school = "햇살초등학교"
        total_count = 0

        def __init__(self, name, grade):
            # 인스턴스 변수 (각 객체마다 독립)
            self.name = name
            self.grade = grade
            Student.total_count += 1    # 클래스 변수 수정

    s1 = Student("민수", 4)
    s2 = Student("지유", 5)
    s3 = Student("서연", 6)

    print(f"  {s1.name}의 학교: {s1.school}")
    print(f"  {s2.name}의 학교: {s2.school}")
    print(f"  전체 학생 수: {Student.total_count}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 주의사항! 클래스 변수의 함정
    # ─────────────────────────────────────────────────────────────────────
    #
    #   인스턴스에서 클래스 변수를 "읽는" 것은 괜찮지만,
    #   인스턴스에서 "대입"하면 새로운 인스턴스 변수가 만들어짐!
    #
    s1.school = "달빛초등학교"         # ★ 인스턴스 변수가 새로 생김!
    print(f"  s1.school: {s1.school}")        # 달빛초등학교 (인스턴스 변수)
    print(f"  s2.school: {s2.school}")        # 햇살초등학교 (클래스 변수)
    print(f"  Student.school: {Student.school}")  # 햇살초등학교

    # ★ 리스트형 클래스 변수는 특히 위험!
    class BadExample:
        shared_list = []   # ★ 모든 객체가 같은 리스트를 공유!
        def add(self, item):
            self.shared_list.append(item)

    b1 = BadExample()
    b2 = BadExample()
    b1.add("아이템1")
    print(f"  b2의 리스트: {b2.shared_list}")  # ["아이템1"]  ← b2도 영향!

    # 올바른 방법: __init__에서 인스턴스 변수로 만들기
    class GoodExample:
        def __init__(self):
            self.my_list = []   # 각 객체마다 독립적인 리스트
        def add(self, item):
            self.my_list.append(item)

    g1 = GoodExample()
    g2 = GoodExample()
    g1.add("아이템1")
    print(f"  g2의 리스트: {g2.my_list}")  # []  ← 영향 없음!
    print()


def lesson3_method_types():
    # =========================================================================
    #
    #   레슨 3 — 메서드 종류
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : 메서드 종류                │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 3가지 메서드 타입
    # ─────────────────────────────────────────────────────────────────────
    #
    #   1. 인스턴스 메서드: self 사용, 각 객체의 데이터에 접근
    #      → 가장 흔함! 기본 메서드
    #
    #   2. 클래스 메서드(@classmethod): cls 사용, 클래스 자체에 접근
    #      → 대안 생성자(팩토리 메서드)에 자주 사용
    #
    #   3. 정적 메서드(@staticmethod): self도 cls도 없음
    #      → 클래스와 관련은 있지만 객체/클래스 데이터 불필요할 때
    #
    #   비유:
    #   - 인스턴스 메서드 = 학생이 "내 이름은 민수입니다" (자기 정보 사용)
    #   - 클래스 메서드 = "우리 학교 이름은 햇살초입니다" (학교 전체 정보)
    #   - 정적 메서드 = "오늘 날짜는 3월 21일입니다" (학생/학교 무관)
    #

    class Pizza:
        # 클래스 변수
        total_made = 0

        def __init__(self, size, toppings):
            self.size = size
            self.toppings = toppings
            Pizza.total_made += 1

        # 인스턴스 메서드: self로 각 피자의 정보에 접근
        def describe(self):
            return f"{self.size}인치 피자 ({', '.join(self.toppings)})"

        # 클래스 메서드: cls로 클래스 자체에 접근
        @classmethod
        def get_total(cls):
            return f"지금까지 {cls.total_made}판 만들었습니다"

        # 클래스 메서드를 대안 생성자로 사용!
        @classmethod
        def margherita(cls, size):
            """마르게리타 피자를 쉽게 만드는 팩토리 메서드"""
            return cls(size, ["모짜렐라", "토마토", "바질"])

        @classmethod
        def pepperoni(cls, size):
            return cls(size, ["페퍼로니", "모짜렐라"])

        # 정적 메서드: self도 cls도 필요 없음
        @staticmethod
        def is_valid_size(size):
            """피자 크기가 유효한지 확인"""
            return size in [8, 10, 12, 14, 16]

    # 인스턴스 메서드 사용
    p1 = Pizza(12, ["페퍼로니", "올리브"])
    print(f"  {p1.describe()}")

    # 클래스 메서드로 간편 생성
    p2 = Pizza.margherita(14)
    print(f"  {p2.describe()}")

    # 클래스 메서드로 통계
    p3 = Pizza.pepperoni(10)
    print(f"  {Pizza.get_total()}")

    # 정적 메서드 사용
    print(f"  12인치 유효? {Pizza.is_valid_size(12)}")
    print(f"  13인치 유효? {Pizza.is_valid_size(13)}")
    print()


def lesson4_magic_methods():
    # =========================================================================
    #
    #   레슨 4 — 매직 메서드(던더 메서드) 완전정복
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : 매직 메서드 완전정복       │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 매직 메서드란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   __이름__ 형태의 특수 메서드입니다. (던더 = double underscore)
    #   파이썬이 특정 상황에서 자동으로 호출합니다!
    #
    #   비유: 리모컨의 숨겨진 버튼! 특정 상황에서 자동 작동
    #
    #   C++ : 연산자 오버로딩과 비슷
    #         operator+, operator<, operator<< 등
    #

    class Vector:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        # __str__: print()할 때 호출
        # 비유: "이름표에 뭐라고 쓸까?"
        def __str__(self):
            return f"Vector({self.x}, {self.y})"

        # __repr__: 개발자용 표현 (디버깅용)
        # str이 없으면 repr이 대신 사용됨
        def __repr__(self):
            return f"Vector(x={self.x}, y={self.y})"

        # __len__: len() 호출 시
        def __len__(self):
            return 2  # 2차원 벡터

        # __eq__: == 비교
        def __eq__(self, other):
            if not isinstance(other, Vector):
                return NotImplemented
            return self.x == other.x and self.y == other.y

        # __lt__: < 비교 (sorted에서도 사용!)
        def __lt__(self, other):
            # 벡터의 크기로 비교
            return (self.x**2 + self.y**2) < (other.x**2 + other.y**2)

        # __add__: + 연산
        def __add__(self, other):
            return Vector(self.x + other.x, self.y + other.y)

        # __mul__: * 연산 (스칼라 곱)
        def __mul__(self, scalar):
            return Vector(self.x * scalar, self.y * scalar)

        # __getitem__: 인덱스 접근 v[0], v[1]
        def __getitem__(self, index):
            if index == 0:
                return self.x
            elif index == 1:
                return self.y
            raise IndexError("Vector는 0 또는 1만 가능")

        # __contains__: in 연산자
        def __contains__(self, value):
            return value == self.x or value == self.y

        # __iter__: for문에서 사용 가능하게
        def __iter__(self):
            yield self.x
            yield self.y

        # __call__: 객체를 함수처럼 호출!
        def __call__(self):
            return (self.x**2 + self.y**2) ** 0.5

    v1 = Vector(3, 4)
    v2 = Vector(1, 2)

    print(f"  __str__:   {v1}")                    # Vector(3, 4)
    print(f"  __repr__:  {repr(v1)}")              # Vector(x=3, y=4)
    print(f"  __len__:   {len(v1)}")               # 2
    print(f"  __eq__:    {v1 == Vector(3, 4)}")    # True
    print(f"  __lt__:    {v2 < v1}")               # True
    print(f"  __add__:   {v1 + v2}")               # Vector(4, 6)
    print(f"  __mul__:   {v1 * 3}")                # Vector(9, 12)
    print(f"  __getitem__: v1[0]={v1[0]}")         # 3
    print(f"  __contains__: 3 in v1 → {3 in v1}") # True
    print(f"  __iter__:  {list(v1)}")              # [3, 4]
    print(f"  __call__:  v1() = {v1()}")           # 5.0 (벡터 크기)
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ __enter__/__exit__: with 문 (컨텍스트 매니저)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   with 문을 쓸 수 있는 객체를 만드는 매직 메서드
    #   비유: 도서관 입장(enter) → 책 읽기 → 퇴장(exit)
    #         입장/퇴장 절차를 자동으로 처리!
    #
    class Timer:
        def __enter__(self):
            import time
            self.start = time.perf_counter()
            print("  [타이머 시작]")
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            import time
            elapsed = time.perf_counter() - self.start
            print(f"  [타이머 종료] {elapsed:.4f}초 경과")
            return False  # 예외를 전파 (True면 예외 무시)

    with Timer():
        total = sum(range(1_000_000))
        print(f"  합계: {total}")
    print()

    # 매직 메서드 덕분에 sorted도 작동!
    vectors = [Vector(5, 0), Vector(1, 1), Vector(3, 4)]
    sorted_v = sorted(vectors)
    print("  정렬된 벡터:", [str(v) for v in sorted_v])
    print()


def lesson5_property():
    # =========================================================================
    #
    #   레슨 5 — 프로퍼티(@property)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 프로퍼티(@property)        │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 프로퍼티란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   메서드를 속성처럼 쓸 수 있게 해주는 기능!
    #
    #   비유: 체중계에 올라가면 몸무게가 "자동 계산"됨
    #         직접 몸무게를 입력하는 게 아니라, 올라가기만 하면 됨
    #
    #   C++ : getter/setter 메서드를 직접 작성
    #   파이썬: @property로 우아하게!
    #

    class Student:
        def __init__(self, name, score):
            self.name = name
            self._score = score     # _ 붙여서 "직접 건드리지 마" 신호

        # getter: 값을 읽을 때 호출
        @property
        def score(self):
            return self._score

        # setter: 값을 쓸 때 호출 → 유효성 검사 가능!
        @score.setter
        def score(self, value):
            if not isinstance(value, (int, float)):
                raise TypeError("점수는 숫자여야 합니다!")
            if value < 0 or value > 100:
                raise ValueError("점수는 0~100 사이여야 합니다!")
            self._score = value

        # 계산된 속성 (read-only property)
        @property
        def grade(self):
            """점수에 따른 등급을 자동 계산"""
            if self._score >= 90: return "A"
            if self._score >= 80: return "B"
            if self._score >= 70: return "C"
            if self._score >= 60: return "D"
            return "F"

        # 읽기 전용: setter를 정의하지 않으면 수정 불가!
        @property
        def report(self):
            return f"{self.name}: {self._score}점 ({self.grade})"

    s = Student("민수", 85)
    print(f"  점수: {s.score}")       # getter 호출 (메서드인데 ()없이!)
    print(f"  등급: {s.grade}")       # 계산된 속성
    print(f"  리포트: {s.report}")

    s.score = 95                      # setter 호출 → 유효성 검사!
    print(f"  수정 후: {s.report}")

    # 잘못된 값 넣기 시도
    try:
        s.score = 150
    except ValueError as e:
        print(f"  에러 발생: {e}")

    try:
        s.score = "백점"
    except TypeError as e:
        print(f"  에러 발생: {e}")

    # 읽기 전용 속성에 쓰기 시도
    try:
        s.grade = "A+"
    except AttributeError as e:
        print(f"  읽기 전용 에러: {e}")
    print()


def lesson6_inheritance():
    # =========================================================================
    #
    #   레슨 6 — 상속(Inheritance)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 상속(Inheritance)          │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 상속이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   기존 클래스(부모)의 기능을 물려받아 새 클래스(자식)를 만드는 것!
    #
    #   비유: 부모에게 유전자를 물려받지만,
    #         자식만의 특성도 추가로 가질 수 있음!
    #
    #   C++ : class Child : public Parent { ... };
    #   파이썬: class Child(Parent): ...
    #

    class Animal:
        def __init__(self, name, sound):
            self.name = name
            self.sound = sound

        def speak(self):
            return f"{self.name}이(가) {self.sound}!"

        def info(self):
            return f"동물: {self.name}"

    class Dog(Animal):
        def __init__(self, name, breed):
            # super()로 부모의 __init__ 호출!
            # C++에서 Parent::Parent(args) 하는 것과 같음
            super().__init__(name, "멍멍")
            self.breed = breed          # 자식만의 새 속성

        def fetch(self):                # 자식만의 새 메서드
            return f"{self.name}이(가) 공을 물어옵니다!"

        # 메서드 오버라이딩: 부모의 메서드를 덮어쓰기!
        def info(self):
            return f"강아지: {self.name} ({self.breed})"

    class Cat(Animal):
        def __init__(self, name, indoor):
            super().__init__(name, "야옹")
            self.indoor = indoor

        def purr(self):
            return f"{self.name}이(가) 그르릉~"

        def info(self):
            location = "실내" if self.indoor else "실외"
            return f"고양이: {self.name} ({location})"

    # 사용
    dog = Dog("멍멍이", "골든 리트리버")
    cat = Cat("나비", True)

    print(f"  {dog.speak()}")           # 부모 메서드 사용
    print(f"  {dog.fetch()}")           # 자식 고유 메서드
    print(f"  {dog.info()}")            # 오버라이딩된 메서드

    print(f"  {cat.speak()}")
    print(f"  {cat.purr()}")
    print(f"  {cat.info()}")

    # isinstance, issubclass
    print(f"  dog은 Dog? {isinstance(dog, Dog)}")         # True
    print(f"  dog은 Animal? {isinstance(dog, Animal)}")   # True (부모도!)
    print(f"  Dog은 Animal의 자식? {issubclass(Dog, Animal)}")  # True
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 다형성 (Polymorphism)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   같은 메서드 이름이지만 객체에 따라 다른 동작!
    #   비유: "말해봐!" → 강아지는 "멍멍", 고양이는 "야옹"
    #
    animals = [dog, cat, Animal("병아리", "삐약삐약")]
    for animal in animals:
        print(f"  {animal.speak()}")    # 각각 다른 동작!
    print()


def lesson7_multiple_inheritance():
    # =========================================================================
    #
    #   레슨 7 — 다중상속과 MRO
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 다중상속과 MRO             │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 다중상속이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   여러 부모 클래스에서 동시에 상속받는 것!
    #
    #   비유: 엄마에게서 요리 실력을, 아빠에게서 운동 능력을 물려받음
    #
    #   C++ : class Child : public Mom, public Dad { };
    #   파이썬: class Child(Mom, Dad): ...
    #
    #   ★ 주의: 다이아몬드 문제가 발생할 수 있음!
    #

    class Flyable:
        def fly(self):
            return "하늘을 날아요!"

    class Swimmable:
        def swim(self):
            return "물에서 헤엄쳐요!"

    class Duck(Flyable, Swimmable):
        def __init__(self, name):
            self.name = name

        def quack(self):
            return f"{self.name}: 꽥꽥!"

    duck = Duck("도널드")
    print(f"  {duck.quack()}")
    print(f"  {duck.fly()}")        # Flyable에서 상속
    print(f"  {duck.swim()}")       # Swimmable에서 상속
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 다이아몬드 문제와 MRO
    # ─────────────────────────────────────────────────────────────────────
    #
    #   다이아몬드 문제:
    #        A
    #       / \
    #      B   C
    #       \ /
    #        D
    #
    #   D에서 A의 메서드를 호출하면, B의 것? C의 것?
    #   → MRO(Method Resolution Order)로 해결!
    #

    class A:
        def greet(self):
            return "A입니다"

    class B(A):
        def greet(self):
            return "B입니다"

    class C(A):
        def greet(self):
            return "C입니다"

    class D(B, C):
        pass  # greet을 정의하지 않음

    d = D()
    print(f"  D().greet() = {d.greet()}")  # "B입니다" ← 왼쪽 부모 우선!

    # MRO 확인 방법
    print(f"  MRO: {[cls.__name__ for cls in D.__mro__]}")
    # → ['D', 'B', 'C', 'A', 'object']
    #   D → B → C → A → object 순서로 탐색!
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ super()와 다중상속에서의 협력적 호출
    # ─────────────────────────────────────────────────────────────────────
    class Base:
        def __init__(self):
            print("    Base.__init__")

    class Left(Base):
        def __init__(self):
            print("    Left.__init__")
            super().__init__()          # MRO 순서대로 다음 호출

    class Right(Base):
        def __init__(self):
            print("    Right.__init__")
            super().__init__()

    class Child(Left, Right):
        def __init__(self):
            print("    Child.__init__")
            super().__init__()          # Left → Right → Base 순서!

    print("  다중상속 초기화 순서:")
    c = Child()
    # Child → Left → Right → Base (MRO 순서!)
    print()


def lesson8_abstract_class():
    # =========================================================================
    #
    #   레슨 8 — 추상 클래스와 인터페이스
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 8 : 추상 클래스와 인터페이스   │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 추상 클래스란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   "이 메서드는 반드시 자식 클래스에서 구현해야 해!" 라고
    #   강제하는 설계도입니다.
    #
    #   비유: 시험지에 "이 문제는 반드시 풀어야 합니다" 표시!
    #         빈 칸으로 두면 제출 불가(에러)!
    #
    #   C++ : class Shape { virtual double area() = 0; };  (순수 가상 함수)
    #   파이썬: ABC + @abstractmethod
    #

    class Shape(ABC):
        @abstractmethod
        def area(self):
            """면적을 계산합니다 (자식이 반드시 구현!)"""
            pass

        @abstractmethod
        def perimeter(self):
            """둘레를 계산합니다"""
            pass

        # 추상 클래스도 일반 메서드를 가질 수 있음!
        def describe(self):
            return f"{self.__class__.__name__}: 면적={self.area():.2f}"

    class Circle(Shape):
        def __init__(self, radius):
            self.radius = radius

        def area(self):
            import math
            return math.pi * self.radius ** 2

        def perimeter(self):
            import math
            return 2 * math.pi * self.radius

    class Rectangle(Shape):
        def __init__(self, width, height):
            self.width = width
            self.height = height

        def area(self):
            return self.width * self.height

        def perimeter(self):
            return 2 * (self.width + self.height)

    # ★ 추상 클래스는 직접 인스턴스 생성 불가!
    try:
        s = Shape()
    except TypeError as e:
        print(f"  추상 클래스 생성 에러: {e}")

    # 자식 클래스는 모든 추상 메서드를 구현해야 함
    circle = Circle(5)
    rect = Rectangle(3, 4)

    print(f"  {circle.describe()}")
    print(f"  원 둘레: {circle.perimeter():.2f}")
    print(f"  {rect.describe()}")
    print(f"  사각형 둘레: {rect.perimeter():.2f}")
    print()

    # ★ 추상 메서드를 하나라도 빠뜨리면?
    # class BadTriangle(Shape):
    #     def area(self):       # perimeter 빠뜨림!
    #         return 0
    # t = BadTriangle()  ← TypeError!
    print("  ★ 모든 추상 메서드를 구현하지 않으면 인스턴스 생성 불가!")
    print()


def lesson9_encapsulation():
    # =========================================================================
    #
    #   레슨 9 — 캡슐화와 접근 제어
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 9 : 캡슐화와 접근 제어         │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 파이썬의 접근 제어 규칙
    # ─────────────────────────────────────────────────────────────────────
    #
    #   파이썬은 C++/Java와 달리 public/private/protected 키워드가 없습니다!
    #   대신 이름 규칙(naming convention)으로 신호를 줍니다.
    #
    #   name       → public (누구나 접근)
    #   _name      → protected (관례상 "내부용", 접근은 됨)
    #   __name     → private (name mangling으로 접근 어렵게 만듦)
    #
    #   C++ : public:, protected:, private: 키워드
    #   파이썬: 관례로 약속! (강제가 아님)
    #
    #   비유:
    #   - name  : 이름표 (누구나 봄)
    #   - _name : 직원 전용 문 (들어갈 순 있지만 "직원 전용"이라 적혀있음)
    #   - __name: 금고 (비밀번호 알면 열 수 있지만, 웬만하면 못 열게 함)
    #

    class BankAccount:
        def __init__(self, owner, balance):
            self.owner = owner          # public: 누구나 접근
            self._bank_name = "파이썬은행"  # protected: 내부용 (관례)
            self.__balance = balance    # private: 접근 어려움 (name mangling)

        def deposit(self, amount):
            if amount > 0:
                self.__balance += amount
                return f"  입금 {amount}원 → 잔액: {self.__balance}원"
            return "  유효하지 않은 금액"

        def get_balance(self):
            return self.__balance

    acc = BankAccount("민수", 10000)

    # public: 자유롭게 접근
    print(f"  계좌주: {acc.owner}")

    # protected: 접근은 되지만 "건드리지 마" 신호
    print(f"  은행명 (_protected): {acc._bank_name}")

    # private: 직접 접근 불가!
    try:
        print(acc.__balance)
    except AttributeError as e:
        print(f"  __private 접근 에러: {e}")

    # ─────────────────────────────────────────────────────────────────────
    # ■ Name Mangling (이름 뒤섞기)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   __name은 내부적으로 _ClassName__name으로 변환됩니다.
    #   완전히 숨기는 게 아니라, 실수로 접근하는 걸 막는 것!
    #
    print(f"  name mangling으로 접근: {acc._BankAccount__balance}")  # 됨!
    # → 하지만 이렇게 쓰면 안 됩니다! 캡슐화를 깨는 행위!

    # 올바른 방법: 메서드를 통해 접근
    print(f"  {acc.deposit(5000)}")
    print(f"  잔액 조회: {acc.get_balance()}원")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ ★ 정리: 실전에서의 관례
    # ─────────────────────────────────────────────────────────────────────
    #
    #   1. 대부분의 속성은 그냥 public으로 둠 (파이썬 철학)
    #   2. 내부 구현 세부사항은 _single_underscore
    #   3. __double_underscore는 상속에서 이름 충돌 방지할 때만 사용
    #   4. 유효성 검사가 필요하면 @property 사용
    #
    print("  ★ 파이썬 철학: 'We're all consenting adults'")
    print("    (우리는 모두 분별 있는 어른이니 규칙을 강제하지 않는다)")
    print()


def lesson10_zoo_system():
    # =========================================================================
    #
    #   레슨 10 — 실전: 동물원 관리 시스템
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 10 : 동물원 관리 시스템        │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 모든 OOP 개념을 통합한 종합 예제
    # ─────────────────────────────────────────────────────────────────────
    #
    #   사용하는 개념:
    #   - 추상 클래스 (Animal)
    #   - 상속 (Lion, Penguin, Parrot)
    #   - 매직 메서드 (__str__, __repr__, __len__, __iter__)
    #   - 프로퍼티 (@property)
    #   - 클래스 변수, 클래스 메서드
    #   - 캡슐화 (_protected)
    #

    class ZooAnimal(ABC):
        """동물원 동물의 추상 베이스 클래스"""
        _total_animals = 0

        def __init__(self, name, species, age):
            self.name = name
            self.species = species
            self._age = age
            self._health = 100
            ZooAnimal._total_animals += 1

        @abstractmethod
        def perform(self):
            """공연하기 (각 동물마다 다름)"""
            pass

        @property
        def age(self):
            return self._age

        @property
        def health(self):
            return self._health

        def feed(self, food):
            self._health = min(100, self._health + 10)
            return f"  {self.name}에게 {food}을(를) 줬습니다. 건강: {self._health}"

        @classmethod
        def get_total(cls):
            return cls._total_animals

        def __str__(self):
            return f"{self.species} '{self.name}' (나이: {self._age}살)"

        def __repr__(self):
            return f"ZooAnimal(name='{self.name}', species='{self.species}')"

    class Lion(ZooAnimal):
        def __init__(self, name, age, mane_color):
            super().__init__(name, "사자", age)
            self.mane_color = mane_color

        def perform(self):
            return f"  🦁 {self.name}이(가) 우렁차게 포효합니다! 어흥~!"

        def __str__(self):
            return f"사자 '{self.name}' ({self.mane_color} 갈기, {self._age}살)"

    class Penguin(ZooAnimal):
        def __init__(self, name, age, can_swim=True):
            super().__init__(name, "펭귄", age)
            self.can_swim = can_swim

        def perform(self):
            return f"  🐧 {self.name}이(가) 뒤뚱뒤뚱 행진합니다!"

        def slide(self):
            return f"  {self.name}이(가) 배로 미끄러집니다~ 쓩!"

    class Parrot(ZooAnimal):
        def __init__(self, name, age, vocabulary=None):
            super().__init__(name, "앵무새", age)
            self.vocabulary = vocabulary or []

        def perform(self):
            if self.vocabulary:
                word = self.vocabulary[0]
                return f"  🦜 {self.name}이(가) '{word}'라고 말합니다!"
            return f"  🦜 {self.name}이(가) 조용히 있습니다..."

        def learn_word(self, word):
            self.vocabulary.append(word)

    class Zoo:
        """동물원 클래스 — 동물들을 관리합니다"""
        def __init__(self, name):
            self.name = name
            self._animals = []

        def add_animal(self, animal):
            self._animals.append(animal)
            print(f"  [{self.name}] {animal.name} 입장!")

        def __len__(self):
            return len(self._animals)

        def __iter__(self):
            return iter(self._animals)

        def __getitem__(self, index):
            return self._animals[index]

        def show_all(self):
            print(f"\n  === {self.name} 동물 목록 ({len(self)}마리) ===")
            for animal in self:
                print(f"    • {animal}")

        def show_time(self):
            print(f"\n  === {self.name} 공연 시간! ===")
            for animal in self:
                print(animal.perform())

        def find_by_species(self, species):
            return [a for a in self._animals if a.species == species]

    # 동물원 시스템 실행!
    zoo = Zoo("파이썬 동물원")

    # 동물 추가
    simba = Lion("심바", 5, "황금")
    pororo = Penguin("뽀로로", 3)
    polly = Parrot("폴리", 2, ["안녕하세요", "사랑해"])

    zoo.add_animal(simba)
    zoo.add_animal(pororo)
    zoo.add_animal(Penguin("펭수", 4))
    zoo.add_animal(polly)

    # 동물원 정보
    zoo.show_all()

    # 공연!
    zoo.show_time()

    # 먹이주기
    print()
    print(simba.feed("고기"))
    print(pororo.feed("생선"))

    # 인덱스 접근 (__getitem__)
    print(f"\n  첫 번째 동물: {zoo[0]}")

    # 펭귄만 찾기
    penguins = zoo.find_by_species("펭귄")
    print(f"  펭귄 수: {len(penguins)}마리")

    # 전체 동물 수 (클래스 메서드)
    print(f"  총 동물 수: {ZooAnimal.get_total()}마리")
    print()


def main():
    print("■■■ Python 학습 05단계: 객체지향 프로그래밍(OOP) 완전정복 ■■■")
    print()
    lesson1_class_and_object()
    lesson2_instance_vs_class_variable()
    lesson3_method_types()
    lesson4_magic_methods()
    lesson5_property()
    lesson6_inheritance()
    lesson7_multiple_inheritance()
    lesson8_abstract_class()
    lesson9_encapsulation()
    lesson10_zoo_system()


if __name__ == "__main__":
    main()
