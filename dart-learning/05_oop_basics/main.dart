/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Dart 학습 05단계: OOP 기초 (클래스와 객체지향)
  ─ 클래스 · 객체 · 생성자 · this · getter/setter · 캡슐화 ─

  ■ 실행: dart run main.dart
  ■ 컴파일: dart compile exe main.dart

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// =====================================================================
// 레슨 1 — 클래스와 객체의 개념
// =====================================================================
/*
★ 클래스 = 설계도,  객체 = 그 설계도로 만든 실제 물건

  붕어빵 틀(클래스)  →  붕어빵(객체)
  학생 기록 양식(클래스)  →  "민수" 기록(객체)

  ┌─────────────────────────────────────────────┐
  │  class Student {          ← 설계도           │
  │    String name;           ← 필드(데이터)     │
  │    void study() { ... }   ← 메서드(행동)     │
  │  }                                          │
  │                                             │
  │  final s = Student();     ← 객체(인스턴스)   │
  └─────────────────────────────────────────────┘

★ Dart 특징
  - 모든 것이 객체 (int, double, bool 전부 Object 의 자식)
  - 클래스 멤버는 기본적으로 public (접근 제한은 _ 로 시작)
  - C++/Java 와 달리 파일 단위가 접근 제어 경계
*/

class Dog {
  // ── 필드(멤버 변수) ──
  // Dart 에서 _ 로 시작하면 라이브러리 프라이빗
  String name;
  int age;

  // ── 생성자: 가장 기본 형태 ──
  // this.name 은 "매개변수를 같은 이름의 필드에 자동 대입" 하는 Dart 약어
  Dog(this.name, this.age);

  // ── 메서드 ──
  void bark() {
    print('  $name: 멍멍!');
  }

  void info() {
    print('  이름: $name / 나이: ${age}살');
  }
}

void lesson1ClassBasic() {
  /*
     클래스는 "어떤 데이터와 행동을 묶어 놓은 상자"라고 생각하면 됩니다.
     Dog 클래스에는 이름, 나이(데이터)와 짖기, 정보 출력(행동)이 들어 있습니다.
  */
  print('[레슨 1] 클래스와 객체');

  final dog1 = Dog('초코', 3);
  final dog2 = Dog('나비', 5);

  dog1.info();    // 이름: 초코 / 나이: 3살
  dog2.bark();    // 나비: 멍멍!

  // dog1 과 dog2 는 같은 설계도(Dog)로 만든 서로 다른 객체
  print('  dog1 == dog2 ? ${identical(dog1, dog2)}');  // false
  print('');
}


// =====================================================================
// 레슨 2 — 다양한 생성자
// =====================================================================
/*
★ Dart 생성자 종류

  ┌──────────────────┬────────────────────────────────────────┐
  │ 종류             │ 문법                                   │
  ├──────────────────┼────────────────────────────────────────┤
  │ 기본 생성자      │ Student(this.name, this.score);        │
  │ 이름 있는 생성자 │ Student.freshman(this.name)            │
  │ 팩토리 생성자    │ factory Student.fromJson(Map m) {...}  │
  │ const 생성자     │ const Point(this.x, this.y);           │
  │ 리디렉팅 생성자  │ Student.noName() : this('무명', 0);    │
  └──────────────────┴────────────────────────────────────────┘

★ this 키워드
  - this 는 "지금 이 객체 자신"을 가리킴
  - this.name = name; 를 Dart 에서는 매개변수에 this.name 으로 축약
*/

class Student {
  String name;
  int score;

  // ── 기본 생성자 (약어 형태) ──
  Student(this.name, this.score);

  // ── 이름 있는 생성자 (Named Constructor) ──
  // 용도별로 여러 생성자를 만들 수 있음
  Student.freshman(this.name) : score = 0;

  // ── 리디렉팅 생성자 ──
  // 다른 생성자를 호출해서 중복 코드 제거
  Student.anonymous() : this('익명', 0);

  // ── 팩토리 생성자 ──
  // 새 인스턴스를 꼭 만들 필요 없을 때, 캐시·싱글톤 등에 활용
  factory Student.fromJson(Map<String, dynamic> json) {
    return Student(
      json['name'] as String,
      json['score'] as int,
    );
  }

  void report() {
    final grade = score >= 90
        ? 'A'
        : score >= 80
            ? 'B'
            : score >= 70
                ? 'C'
                : 'F';
    print('  $name: ${score}점 (등급 $grade)');
  }
}

void lesson2Constructors() {
  print('[레슨 2] 다양한 생성자');

  final s1 = Student('민수', 92);
  final s2 = Student.freshman('지우');
  final s3 = Student.anonymous();
  final s4 = Student.fromJson({'name': '서연', 'score': 88});

  s1.report();  // 민수: 92점 (등급 A)
  s2.report();  // 지우: 0점  (등급 F)
  s3.report();  // 익명: 0점  (등급 F)
  s4.report();  // 서연: 88점 (등급 B)
  print('');
}


// =====================================================================
// 레슨 3 — getter 와 setter
// =====================================================================
/*
★ getter/setter 는 "필드를 읽거나 쓸 때 추가 로직을 넣는 관문"

  비유: 은행 창구
  - 돈을 맡길 때(setter) → 금액이 음수인지 확인
  - 돈을 찾을 때(getter) → 잔액을 계산해서 알려줌

  ┌────────────────────────────────────────────┐
  │  int get balance => _balance;              │
  │  set balance(int v) {                      │
  │    if (v < 0) throw '음수 불가!';          │
  │    _balance = v;                           │
  │  }                                         │
  └────────────────────────────────────────────┘

★ 왜 쓸까?
  - 필드 직접 노출 → 아무 값이나 넣을 수 있어 위험
  - getter/setter → 유효성 검사, 로그, 계산 등 추가 가능
*/

class BankAccount {
  // _ 접두사 = 라이브러리 프라이빗 (다른 파일에서 접근 불가)
  String _owner;
  int _balance;

  BankAccount(this._owner, this._balance);

  // ── getter ──
  String get owner => _owner;
  int get balance => _balance;

  // ── setter ──
  set balance(int amount) {
    if (amount < 0) {
      print('  ★ 경고: 잔액을 음수로 설정할 수 없습니다!');
      return;
    }
    _balance = amount;
  }

  // ── 계산형 getter (저장된 필드 없이 계산) ──
  String get status => _balance >= 10000 ? '우수 고객' : '일반 고객';

  void showInfo() {
    print('  [$_owner] 잔액: ${_balance}원 / $status');
  }
}

void lesson3GetterSetter() {
  print('[레슨 3] getter / setter');

  final account = BankAccount('민수', 50000);
  account.showInfo();              // [민수] 잔액: 50000원 / 우수 고객

  account.balance = 3000;          // setter 를 통해 변경
  account.showInfo();              // [민수] 잔액: 3000원 / 일반 고객

  account.balance = -100;          // ★ 경고 발생, 값 변경 안 됨
  account.showInfo();              // 잔액 여전히 3000원
  print('');
}


// =====================================================================
// 레슨 4 — 캡슐화와 접근 제어
// =====================================================================
/*
★ 캡슐화 = "내부 구현을 숨기고, 필요한 인터페이스만 공개"

  비유: 자동차 운전
  - 운전자 → 핸들, 페달 (public 인터페이스)
  - 엔진 내부 → 운전자가 직접 만질 필요 없음 (private 구현)

★ Dart 접근 제어
  ┌──────────────┬───────────────────────────────────┐
  │ 접근 수준    │ 규칙                               │
  ├──────────────┼───────────────────────────────────┤
  │ public       │ 이름이 _ 로 시작하지 않으면 공개  │
  │ private      │ 이름이 _ 로 시작하면 비공개       │
  │              │ (같은 라이브러리/파일 내에서는 접근 가능) │
  └──────────────┴───────────────────────────────────┘

★ 주의: Dart 에는 protected 가 없음!
  - 같은 파일 안에서는 _ 필드도 접근 가능
  - 접근 제어의 단위가 "클래스" 가 아닌 "라이브러리(파일)"
*/

class TemperatureSensor {
  double _celsius;    // 내부에서만 직접 접근

  TemperatureSensor(this._celsius);

  // 공개 인터페이스
  double get celsius => _celsius;
  double get fahrenheit => _celsius * 9 / 5 + 32;

  void update(double newTemp) {
    // 유효 범위 검사 (캡슐화의 장점)
    if (newTemp < -273.15) {
      print('  ★ 절대영도(-273.15°C) 이하 온도는 불가능합니다!');
      return;
    }
    _celsius = newTemp;
  }

  void display() {
    print('  현재 온도: ${celsius.toStringAsFixed(1)}°C'
        ' / ${fahrenheit.toStringAsFixed(1)}°F');
  }
}

void lesson4Encapsulation() {
  print('[레슨 4] 캡슐화');

  final sensor = TemperatureSensor(25.0);
  sensor.display();        // 25.0°C / 77.0°F

  sensor.update(100.0);
  sensor.display();        // 100.0°C / 212.0°F

  sensor.update(-300.0);   // ★ 절대영도 경고
  sensor.display();        // 여전히 100.0°C
  print('');
}


// =====================================================================
// 레슨 5 — static 멤버와 싱글톤
// =====================================================================
/*
★ static = "객체가 아니라 클래스 자체에 소속된 변수/함수"

  비유: 교실 칠판
  - 학생(객체)마다 개인 공책(인스턴스 필드) 이 있지만
  - 칠판(static 필드) 은 교실(클래스) 에 하나만 있음

  ┌──────────────────────────────────────────────────┐
  │  class Counter {                                 │
  │    static int count = 0;   ← 클래스에 하나       │
  │    Counter() { count++; }                        │
  │  }                                               │
  │                                                  │
  │  Counter();  Counter();                          │
  │  print(Counter.count);     // 2                  │
  └──────────────────────────────────────────────────┘
*/

class AppConfig {
  // ── static 필드 ──
  static int _instanceCount = 0;
  static const String appName = '학습 앱';

  final int id;

  AppConfig() : id = ++_instanceCount;

  // ── static 메서드 ──
  static void resetCount() {
    _instanceCount = 0;
  }

  static int get instanceCount => _instanceCount;

  void show() {
    print('  [$appName] 이 객체 ID: $id / 총 생성 수: $_instanceCount');
  }
}

/*
★ 싱글톤 패턴 (Singleton)
  - "클래스의 인스턴스를 딱 하나만 만들겠다"
  - Dart 에서는 factory 생성자 + static 필드로 깔끔하게 구현

  비유: 대통령
  - 나라마다 대통령은 한 명뿐 → 새로 뽑아도 자리는 하나
*/

class DatabaseConnection {
  static DatabaseConnection? _instance;

  final String connectionString;

  // 프라이빗 생성자: 외부에서 직접 생성 불가
  DatabaseConnection._internal(this.connectionString);

  // 팩토리: 이미 있으면 기존 것 반환
  factory DatabaseConnection(String connStr) {
    _instance ??= DatabaseConnection._internal(connStr);
    return _instance!;
  }
}

void lesson5StaticAndSingleton() {
  print('[레슨 5] static 멤버와 싱글톤');

  // static 멤버 테스트
  final a = AppConfig();
  final b = AppConfig();
  final c = AppConfig();
  a.show();  // ID: 1 / 총: 3
  b.show();  // ID: 2 / 총: 3
  c.show();  // ID: 3 / 총: 3

  // 싱글톤 테스트
  final db1 = DatabaseConnection('mysql://localhost');
  final db2 = DatabaseConnection('postgresql://other');  // 무시됨

  print('  db1 == db2 ? ${identical(db1, db2)}');  // true (같은 객체)
  print('  연결: ${db1.connectionString}');          // mysql://localhost
  print('');

  AppConfig.resetCount();  // 다음 테스트를 위해 초기화
}


// =====================================================================
// 레슨 6 — const 생성자와 불변 객체
// =====================================================================
/*
★ const 생성자 = "컴파일 시점에 만들어지는 불변 객체"

  ┌────────────────────────────────────────────────────┐
  │  class Point {                                     │
  │    final int x, y;              ← 모든 필드 final  │
  │    const Point(this.x, this.y); ← const 생성자     │
  │  }                                                 │
  │                                                    │
  │  const p1 = Point(1, 2);                           │
  │  const p2 = Point(1, 2);                           │
  │  identical(p1, p2);  // true! (같은 메모리)        │
  └────────────────────────────────────────────────────┘

★ 왜 쓸까?
  - 성능: 같은 값이면 메모리를 공유 (Flutter 위젯에서 많이 활용)
  - 안전: 한번 만든 뒤 절대 변경 불가
  - Flutter 의 const Text('안녕') 이 이 원리

★ 주의
  - const 생성자를 쓰려면 모든 필드가 final 이어야 함
  - 생성자 본문(body) 에 코드를 넣을 수 없음
*/

class Color {
  final int r, g, b;

  const Color(this.r, this.g, this.b);

  // ── 이름 있는 const 생성자 ──
  const Color.red()   : r = 255, g = 0, b = 0;
  const Color.green() : r = 0, g = 255, b = 0;
  const Color.blue()  : r = 0, g = 0, b = 255;

  @override
  String toString() => 'Color($r, $g, $b)';
}

void lesson6ConstConstructor() {
  print('[레슨 6] const 생성자와 불변 객체');

  const c1 = Color(255, 0, 0);
  const c2 = Color.red();

  // 같은 값이므로 컴파일 타임에 같은 객체로 최적화
  print('  c1: $c1');
  print('  c2: $c2');
  print('  identical(c1, c2): ${identical(c1, c2)}');  // true

  // const 가 아닌 경우
  // ignore: prefer_const_constructors
  final c3 = Color(255, 0, 0);
  print('  identical(c1, c3): ${identical(c1, c3)}');  // false (런타임 생성)
  print('');
}


// =====================================================================
// 레슨 7 — toString, operator==, hashCode 오버라이드
// =====================================================================
/*
★ 모든 클래스는 Object 를 상속
  - toString() : 객체를 문자열로 표현
  - operator== : 두 객체가 "같은 값" 인지 비교
  - hashCode   : 해시 기반 컬렉션(Set, Map) 에서 사용

  ┌───────────────────────────────────────────────────┐
  │  @override                                        │
  │  bool operator ==(Object other) =>                │
  │    other is Point && x == other.x && y == other.y;│
  │                                                   │
  │  @override                                        │
  │  int get hashCode => Object.hash(x, y);           │
  └───────────────────────────────────────────────────┘

★ 왜 중요할까?
  - print(object) 할 때 toString() 이 호출됨
  - Set/Map 에서 중복 판단할 때 == 과 hashCode 사용
  - 둘 중 하나만 오버라이드하면 버그 발생!
*/

class Point {
  final int x, y;
  const Point(this.x, this.y);

  @override
  String toString() => 'Point($x, $y)';

  @override
  bool operator ==(Object other) =>
      other is Point && x == other.x && y == other.y;

  @override
  int get hashCode => Object.hash(x, y);

  // ── 연산자 오버로딩 ──
  Point operator +(Point other) => Point(x + other.x, y + other.y);
  Point operator -(Point other) => Point(x - other.x, y - other.y);
}

void lesson7OverridesAndOperators() {
  print('[레슨 7] toString, ==, 연산자 오버로딩');

  final p1 = Point(1, 2);
  final p2 = Point(1, 2);
  final p3 = Point(3, 4);

  print('  p1 = $p1');               // Point(1, 2) — toString
  print('  p1 == p2 ? ${p1 == p2}'); // true  — operator==
  print('  p1 == p3 ? ${p1 == p3}'); // false

  // 연산자 오버로딩
  final sum = p1 + p3;
  print('  p1 + p3 = $sum');          // Point(4, 6)

  // Set 에서 중복 제거 (hashCode + == 덕분)
  final pointSet = {p1, p2, p3};
  print('  Set 크기: ${pointSet.length}');  // 2 (p1 == p2 이므로 중복 제거)
  print('');
}


// =====================================================================
// 레슨 8 — 종합 예제: 학생 성적 관리
// =====================================================================
/*
★ 지금까지 배운 것을 모두 합쳐서 작은 프로그램을 만들어 봅시다.

  ┌─────────────────────────────────────────────────────────┐
  │  Classroom                                              │
  │  ├─ students: List<GradeStudent>                        │
  │  ├─ addStudent(name, score)                             │
  │  ├─ get average → 평균 계산 (getter)                    │
  │  ├─ get topStudent → 최고 점수 학생                     │
  │  └─ printReport() → 전체 보고서 출력                    │
  └─────────────────────────────────────────────────────────┘
*/

class GradeStudent {
  final String name;
  int _score;

  GradeStudent(this.name, int score) : _score = score {
    if (score < 0 || score > 100) {
      throw ArgumentError('점수는 0~100 사이여야 합니다: $score');
    }
  }

  int get score => _score;
  set score(int value) {
    if (value < 0 || value > 100) {
      print('  ★ 점수 범위 초과! 변경하지 않습니다.');
      return;
    }
    _score = value;
  }

  String get grade {
    if (_score >= 90) return 'A';
    if (_score >= 80) return 'B';
    if (_score >= 70) return 'C';
    if (_score >= 60) return 'D';
    return 'F';
  }

  @override
  String toString() => '$name(${_score}점/$grade)';
}

class Classroom {
  final String className;
  final List<GradeStudent> _students = [];

  Classroom(this.className);

  void addStudent(String name, int score) {
    _students.add(GradeStudent(name, score));
  }

  // 계산형 getter
  double get average {
    if (_students.isEmpty) return 0;
    final total = _students.fold<int>(0, (sum, s) => sum + s.score);
    return total / _students.length;
  }

  GradeStudent? get topStudent {
    if (_students.isEmpty) return null;
    return _students.reduce((a, b) => a.score >= b.score ? a : b);
  }

  void printReport() {
    print('  ┌─────────────────────────────────────┐');
    print('  │  $className 성적표                     ');
    print('  ├──────────┬───────┬──────┤');
    print('  │ 이름     │ 점수  │ 등급 │');
    print('  ├──────────┼───────┼──────┤');
    for (final s in _students) {
      final name = s.name.padRight(6);
      final score = s.score.toString().padLeft(4);
      print('  │ $name   │ $score  │  ${s.grade}   │');
    }
    print('  └──────────┴───────┴──────┘');
    print('  평균: ${average.toStringAsFixed(1)}점');
    final top = topStudent;
    if (top != null) {
      print('  최우수: $top');
    }
  }
}

void lesson8ComprehensiveExample() {
  print('[레슨 8] 종합 예제 — 학생 성적 관리');
  print('');

  final room = Classroom('Dart 반');
  room.addStudent('민수', 92);
  room.addStudent('지우', 78);
  room.addStudent('서연', 100);
  room.addStudent('준호', 65);
  room.addStudent('하늘', 88);

  room.printReport();
  print('');
}


// =====================================================================
// main — 전체 레슨 실행
// =====================================================================
void main() {
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('  Dart 05단계 : OOP 기초 (클래스와 객체지향)');
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('');

  lesson1ClassBasic();
  lesson2Constructors();
  lesson3GetterSetter();
  lesson4Encapsulation();
  lesson5StaticAndSingleton();
  lesson6ConstConstructor();
  lesson7OverridesAndOperators();
  lesson8ComprehensiveExample();

  print('■■■ 05단계 완료! ■■■');
}
