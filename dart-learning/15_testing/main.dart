/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Dart 학습 15단계: 테스트
  ─ 단위 테스트 · expect · group · setUp · 테스트 패턴 · Mock 개념 ─

  ■ 실행: dart run main.dart
  ■ 실제 테스트: dart test (test 패키지 필요)

  ★ 이 파일은 test 패키지 없이도 실행 가능하도록
    테스트 개념을 순수 Dart 로 시뮬레이션합니다.

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// =====================================================================
// 레슨 1 — 테스트가 뭘까?
// =====================================================================
/*
★ 테스트 = "코드가 올바르게 동작하는지 자동으로 확인하는 코드"

  비유: 자동차 출고 검사
  ┌──────────────────────────────────────────────────────────┐
  │  브레이크 작동? → ✅ 통과                               │
  │  에어백 정상?   → ✅ 통과                               │
  │  엔진 소음?     → ❌ 실패 → 수리 후 재검사              │
  │                                                          │
  │  테스트 = 출고 전에 모든 기능을 자동 검사하는 장치       │
  │  테스트 없이 배포 = 검사 없이 차를 판매하는 것           │
  └──────────────────────────────────────────────────────────┘

★ 테스트 종류
  ┌──────────────┬──────────────────────────────────────────┐
  │ 종류         │ 설명                                     │
  ├──────────────┼──────────────────────────────────────────┤
  │ 단위 테스트  │ 함수/클래스 하나를 독립적으로 테스트      │
  │ 통합 테스트  │ 여러 모듈이 함께 잘 동작하는지            │
  │ 위젯 테스트  │ Flutter UI 위젯을 테스트                  │
  │ E2E 테스트   │ 사용자 시나리오 전체를 테스트              │
  └──────────────┴──────────────────────────────────────────┘

★ Dart 테스트 패키지
  - test 패키지: dart test 명령으로 실행
  - pubspec.yaml 의 dev_dependencies 에 추가
*/

void lesson1WhatIsTesting() {
  print('[레슨 1] 테스트가 뭘까?');
  print('  테스트 = 코드가 올바르게 동작하는지 자동 확인하는 코드');
  print('  없으면: "내가 바꾼 코드가 다른 곳을 망가뜨렸을까?" 불안');
  print('  있으면: 수정 후 테스트만 돌리면 안심!');
  print('');
}


// =====================================================================
// 테스트 프레임워크 시뮬레이션 (test 패키지 없이)
// =====================================================================

int _totalTests = 0;
int _passedTests = 0;
int _failedTests = 0;

void simExpect(dynamic actual, dynamic expected, String description) {
  _totalTests++;
  if (actual == expected) {
    _passedTests++;
    print('    ✅ PASS: $description');
  } else {
    _failedTests++;
    print('    ❌ FAIL: $description');
    print('       예상: $expected');
    print('       실제: $actual');
  }
}

void simExpectTrue(bool condition, String description) {
  simExpect(condition, true, description);
}

void simExpectThrows(void Function() fn, String description) {
  _totalTests++;
  try {
    fn();
    _failedTests++;
    print('    ❌ FAIL: $description (예외가 발생하지 않음)');
  } catch (e) {
    _passedTests++;
    print('    ✅ PASS: $description (예외 발생: $e)');
  }
}

void simGroup(String name, void Function() body) {
  print('  ── $name ──');
  body();
  print('');
}

void printTestSummary() {
  print('  ══════════════════════════════════════');
  print('  테스트 결과: $_totalTests 개 중 $_passedTests 통과, $_failedTests 실패');
  if (_failedTests == 0) {
    print('  🎉 모든 테스트 통과!');
  } else {
    print('  ⚠️ 실패한 테스트가 있습니다!');
  }
  print('  ══════════════════════════════════════');
}


// =====================================================================
// 레슨 2 — 테스트 대상 코드
// =====================================================================

int applyDiscount(int total, int percent) {
  if (percent < 0 || percent > 100) {
    throw ArgumentError('할인율은 0~100 사이: $percent');
  }
  if (total < 0) {
    throw ArgumentError('금액은 양수여야 합니다: $total');
  }
  return total - (total * percent ~/ 100);
}

class Calculator {
  double add(double a, double b) => a + b;
  double subtract(double a, double b) => a - b;
  double multiply(double a, double b) => a * b;

  double divide(double a, double b) {
    if (b == 0) throw ArgumentError('0으로 나눌 수 없습니다');
    return a / b;
  }
}

class TodoItem {
  final String title;
  bool isDone;

  TodoItem(this.title, {this.isDone = false});

  void complete() => isDone = true;
  void uncomplete() => isDone = false;
}

class TodoList {
  final List<TodoItem> _items = [];

  void add(String title) => _items.add(TodoItem(title));

  int get total => _items.length;
  int get completedCount => _items.where((i) => i.isDone).length;
  int get pendingCount => total - completedCount;

  TodoItem? findByTitle(String title) {
    for (final item in _items) {
      if (item.title == title) return item;
    }
    return null;
  }

  void complete(String title) {
    final item = findByTitle(title);
    if (item == null) throw StateError('항목 없음: $title');
    item.complete();
  }

  void remove(String title) {
    _items.removeWhere((i) => i.title == title);
  }
}


// =====================================================================
// 레슨 2 — 기본 테스트 작성
// =====================================================================
/*
★ 테스트 기본 구조

  ┌──────────────────────────────────────────────────────────┐
  │  // test/discount_test.dart                              │
  │                                                          │
  │  import 'package:test/test.dart';                        │
  │                                                          │
  │  void main() {                                           │
  │    test('10000원에 10% 할인', () {                        │
  │      expect(applyDiscount(10000, 10), equals(9000));     │
  │    });                                                    │
  │                                                          │
  │    test('잘못된 할인율은 에러', () {                       │
  │      expect(                                              │
  │        () => applyDiscount(10000, -1),                   │
  │        throwsArgumentError,                               │
  │      );                                                   │
  │    });                                                    │
  │  }                                                        │
  └──────────────────────────────────────────────────────────┘

★ AAA 패턴 (Arrange, Act, Assert)
  1. Arrange: 테스트에 필요한 것 준비
  2. Act:     테스트 대상 실행
  3. Assert:  결과 확인
*/

void lesson2BasicTests() {
  print('[레슨 2] 기본 테스트 작성');

  simGroup('applyDiscount 함수', () {
    // ── Arrange + Act + Assert 한 줄 ──
    simExpect(applyDiscount(10000, 10), 9000, '10000원 10% → 9000원');
    simExpect(applyDiscount(5000, 0), 5000, '5000원 0% → 5000원');
    simExpect(applyDiscount(8000, 25), 6000, '8000원 25% → 6000원');
    simExpect(applyDiscount(10000, 100), 0, '10000원 100% → 0원');

    // ── 에러 케이스 ──
    simExpectThrows(
          () => applyDiscount(10000, -1),
      '음수 할인율은 에러',
    );
    simExpectThrows(
          () => applyDiscount(10000, 101),
      '100 초과 할인율은 에러',
    );
    simExpectThrows(
          () => applyDiscount(-100, 10),
      '음수 금액은 에러',
    );
  });
}


// =====================================================================
// 레슨 3 — group 과 setUp
// =====================================================================
/*
★ group = "관련 테스트를 묶기"
  setUp = "각 테스트 전에 실행할 준비 코드"
  tearDown = "각 테스트 후 정리 코드"

  ┌──────────────────────────────────────────────────────────┐
  │  group('Calculator', () {                                │
  │    late Calculator calc;                                 │
  │                                                          │
  │    setUp(() {                                            │
  │      calc = Calculator();  // 매 테스트 전에 새로 생성   │
  │    });                                                    │
  │                                                          │
  │    test('더하기', () {                                    │
  │      expect(calc.add(2, 3), equals(5));                  │
  │    });                                                    │
  │                                                          │
  │    test('나누기 에러', () {                               │
  │      expect(() => calc.divide(1, 0), throwsArgumentError);│
  │    });                                                    │
  │  });                                                      │
  └──────────────────────────────────────────────────────────┘
*/

void lesson3GroupAndSetUp() {
  print('[레슨 3] group 과 setUp');

  simGroup('Calculator 테스트', () {
    // setUp 시뮬레이션: 매번 새 Calculator
    final calc = Calculator();

    simExpect(calc.add(2, 3), 5.0, '2 + 3 = 5');
    simExpect(calc.subtract(10, 4), 6.0, '10 - 4 = 6');
    simExpect(calc.multiply(3, 4), 12.0, '3 * 4 = 12');
    simExpect(calc.divide(10, 4), 2.5, '10 / 4 = 2.5');

    simExpectThrows(
          () => calc.divide(1, 0),
      '0으로 나누기 에러',
    );
  });
}


// =====================================================================
// 레슨 4 — 클래스 테스트 (TodoList)
// =====================================================================
/*
★ 클래스 테스트 = "메서드 하나하나를 체계적으로 확인"

  ┌──────────────────────────────────────────────────┐
  │  테스트 관점:                                    │
  │  1. 정상 동작 (happy path)                       │
  │  2. 경계값 (빈 리스트, 최대값)                   │
  │  3. 에러 케이스 (잘못된 입력)                    │
  │  4. 상태 변경 (변경 전후 비교)                   │
  └──────────────────────────────────────────────────┘
*/

void lesson4ClassTesting() {
  print('[레슨 4] 클래스 테스트 (TodoList)');

  simGroup('TodoList — 항목 추가', () {
    final list = TodoList();
    list.add('장보기');
    list.add('운동');

    simExpect(list.total, 2, '2개 추가 후 total = 2');
    simExpect(list.pendingCount, 2, '미완료 = 2');
    simExpect(list.completedCount, 0, '완료 = 0');
  });

  simGroup('TodoList — 완료 처리', () {
    final list = TodoList();
    list.add('장보기');
    list.add('운동');
    list.add('공부');

    list.complete('운동');

    simExpect(list.completedCount, 1, '1개 완료');
    simExpect(list.pendingCount, 2, '2개 미완료');
    simExpectTrue(list.findByTitle('운동')!.isDone, '운동 isDone = true');
  });

  simGroup('TodoList — 삭제', () {
    final list = TodoList();
    list.add('장보기');
    list.add('운동');
    list.remove('장보기');

    simExpect(list.total, 1, '삭제 후 total = 1');
    simExpect(list.findByTitle('장보기'), null, '삭제된 항목 검색 = null');
  });

  simGroup('TodoList — 에러 케이스', () {
    final list = TodoList();

    simExpectThrows(
          () => list.complete('없는항목'),
      '없는 항목 완료 시 에러',
    );
  });
}


// =====================================================================
// 레슨 5 — 테스트 주도 개발 (TDD) 개념
// =====================================================================
/*
★ TDD = "테스트를 먼저 쓰고, 코드를 나중에 작성"

  ┌──────────────────────────────────────────────────┐
  │  🔴 Red:   실패하는 테스트 먼저 작성             │
  │       ↓                                          │
  │  🟢 Green: 테스트를 통과하는 최소한의 코드 작성  │
  │       ↓                                          │
  │  🔵 Refactor: 코드 정리 (테스트는 계속 통과)     │
  │       ↓                                          │
  │  🔴 다음 테스트 작성 → 반복...                   │
  └──────────────────────────────────────────────────┘

★ TDD 의 장점
  - 요구사항을 먼저 명확히 정의
  - 작은 단위로 점진적 개발
  - 리팩토링 시 안전망 확보

★ TDD 시뮬레이션: 비밀번호 검증기
*/

// 1단계: 테스트를 먼저 생각
//   - 8자 이상이어야 함
//   - 대문자 포함
//   - 숫자 포함
//   - 특수문자 포함

// 2단계: 코드 구현
class PasswordValidator {
  static List<String> validate(String password) {
    final errors = <String>[];

    if (password.length < 8) {
      errors.add('8자 이상이어야 합니다');
    }
    if (!password.contains(RegExp(r'[A-Z]'))) {
      errors.add('대문자를 포함해야 합니다');
    }
    if (!password.contains(RegExp(r'[0-9]'))) {
      errors.add('숫자를 포함해야 합니다');
    }
    if (!password.contains(RegExp(r'[!@#$%^&*]'))) {
      errors.add('특수문자를 포함해야 합니다');
    }

    return errors;
  }

  static bool isValid(String password) => validate(password).isEmpty;
}

void lesson5TDD() {
  print('[레슨 5] TDD 개념 — 비밀번호 검증기');

  simGroup('비밀번호 검증', () {
    // 유효한 비밀번호
    simExpectTrue(
      PasswordValidator.isValid('MyPass1!'),
      '"MyPass1!" 은 유효',
    );

    // 너무 짧음
    simExpectTrue(
      !PasswordValidator.isValid('Ab1!'),
      '"Ab1!" 은 8자 미만',
    );

    // 대문자 없음
    simExpect(
      PasswordValidator.validate('mypass12!').contains('대문자를 포함해야 합니다'),
      true,
      '대문자 없으면 에러 메시지 포함',
    );

    // 숫자 없음
    simExpect(
      PasswordValidator.validate('MyPasswd!').contains('숫자를 포함해야 합니다'),
      true,
      '숫자 없으면 에러 메시지 포함',
    );

    // 특수문자 없음
    simExpect(
      PasswordValidator.validate('MyPass12').contains('특수문자를 포함해야 합니다'),
      true,
      '특수문자 없으면 에러 메시지 포함',
    );

    // 모든 조건 미달
    final errors = PasswordValidator.validate('abc');
    simExpect(errors.length, 4, '"abc" 는 4가지 조건 모두 미달');
  });
}


// =====================================================================
// 레슨 6 — Mock 의 개념
// =====================================================================
/*
★ Mock = "진짜 대신 쓰는 가짜 객체"

  비유: 영화 스턴트맨
  - 진짜 배우(실제 API) 대신 스턴트맨(Mock) 이 위험한 장면 촬영
  - 테스트에서 진짜 DB/API 를 호출하면:
    → 느리고, 비용 발생, 네트워크 필요

  ┌──────────────────────────────────────────────────────────┐
  │  // 실제 코드                                            │
  │  abstract class UserService {                            │
  │    Future<User> getUser(int id);                         │
  │  }                                                       │
  │                                                          │
  │  // Mock (테스트용 가짜)                                  │
  │  class MockUserService implements UserService {          │
  │    @override                                             │
  │    Future<User> getUser(int id) async {                  │
  │      return User(id, '가짜유저', 'fake@test.com');       │
  │    }                                                     │
  │  }                                                       │
  └──────────────────────────────────────────────────────────┘

★ Dart Mock 패키지: mockito (pub.dev)
  - when(mock.method()).thenReturn(value);
  - verify(mock.method()).called(1);
*/

// 추상 인터페이스
abstract class WeatherService {
  Future<int> getTemperature(String city);
}

// 실제 구현 (API 호출하는 척)
class RealWeatherService implements WeatherService {
  @override
  Future<int> getTemperature(String city) async {
    // 실제로는 HTTP 요청...
    throw UnimplementedError('실제 API 연결 필요');
  }
}

// Mock 구현 (테스트용)
class MockWeatherService implements WeatherService {
  final Map<String, int> _fakeData = {
    '서울': 22,
    '부산': 25,
    '제주': 28,
  };

  @override
  Future<int> getTemperature(String city) async {
    final temp = _fakeData[city];
    if (temp == null) throw Exception('도시를 찾을 수 없음: $city');
    return temp;
  }
}

// 테스트 대상: WeatherService 에 의존
class WeatherReporter {
  final WeatherService _service;

  WeatherReporter(this._service);

  Future<String> getReport(String city) async {
    try {
      final temp = await _service.getTemperature(city);
      if (temp >= 30) return '$city: ${temp}도 (더움)';
      if (temp >= 20) return '$city: ${temp}도 (쾌적)';
      return '$city: ${temp}도 (선선)';
    } catch (e) {
      return '$city: 정보 없음';
    }
  }
}

Future<void> lesson6Mock() async {
  print('[레슨 6] Mock 의 개념');

  // Mock 을 주입해서 테스트
  final mockService = MockWeatherService();
  final reporter = WeatherReporter(mockService);

  simGroup('WeatherReporter with Mock', () async {
    final seoul = await reporter.getReport('서울');
    simExpect(seoul, '서울: 22도 (쾌적)', '서울 날씨');

    final busan = await reporter.getReport('부산');
    simExpect(busan, '부산: 25도 (쾌적)', '부산 날씨');

    final unknown = await reporter.getReport('뉴욕');
    simExpect(unknown, '뉴욕: 정보 없음', '없는 도시');
  });
}


// =====================================================================
// 레슨 7 — 테스트 팁과 모범 사례
// =====================================================================
/*
★ 테스트 작성 팁

  ┌───┬────────────────────────────────────────────────────────┐
  │ 1 │ 테스트 이름은 "무엇을 하면 어떻게 된다" 형식          │
  │   │ test('0으로 나누면 ArgumentError 발생')                │
  │ 2 │ 하나의 테스트에 하나의 검증 (단일 책임)               │
  │ 3 │ 테스트 간 독립성 유지 (서로 영향 주지 않기)           │
  │ 4 │ 경계값 테스트 (0, 빈 문자열, null, 최대값)            │
  │ 5 │ 테스트도 코드! 가독성 중요                            │
  └───┴────────────────────────────────────────────────────────┘

★ 테스트 파일 구조
  ┌──────────────────────────────────────────────────┐
  │  test/                                           │
  │  ├── calculator_test.dart                        │
  │  ├── todo_list_test.dart                         │
  │  ├── weather_reporter_test.dart                  │
  │  └── helpers/                                    │
  │      └── mock_services.dart                      │
  └──────────────────────────────────────────────────┘

★ 실행 명령어
  dart test                    ← 전체 테스트
  dart test test/calculator_test.dart  ← 특정 파일
  dart test --name "나누기"    ← 이름으로 필터
  dart test --coverage         ← 커버리지 측정
*/

void lesson7BestPractices() {
  print('[레슨 7] 테스트 팁과 모범 사례');

  print('  ┌─────────────────────────────────────────────────────┐');
  print('  │ 좋은 테스트의 특징 (FIRST)                          │');
  print('  ├─────────────────────────────────────────────────────┤');
  print('  │ F: Fast      — 빠르게 실행                          │');
  print('  │ I: Isolated  — 독립적 (다른 테스트에 영향 없음)     │');
  print('  │ R: Repeatable— 반복 실행해도 같은 결과              │');
  print('  │ S: Self-validating — 통과/실패 자동 판단            │');
  print('  │ T: Timely    — 코드와 함께 작성                     │');
  print('  └─────────────────────────────────────────────────────┘');
  print('');
}


// =====================================================================
// main — 전체 레슨 실행
// =====================================================================
Future<void> main() async {
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('  Dart 15단계 : 테스트');
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('');

  lesson1WhatIsTesting();
  lesson2BasicTests();
  lesson3GroupAndSetUp();
  lesson4ClassTesting();
  lesson5TDD();
  await lesson6Mock();
  lesson7BestPractices();

  print('');
  printTestSummary();

  print('');
  print('■■■ 15단계 완료! ■■■');
}
