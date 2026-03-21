/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Dart 학습 11단계: 에러 처리와 디버깅
  ─ try/catch/finally · on · 커스텀 예외 · assert · 디버깅 기법 ─

  ■ 실행: dart run main.dart
  ■ 컴파일: dart compile exe main.dart

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// =====================================================================
// 레슨 1 — 에러와 예외의 차이
// =====================================================================
/*
★ Error vs Exception

  비유: 건물 사고
  ┌──────────────────────────────────────────────────────────┐
  │  Error (에러) = 건물 기둥이 부러짐 (복구 불가)           │
  │    → StackOverflowError, OutOfMemoryError                │
  │    → 프로그래머의 실수, 보통 잡지 않음                   │
  │                                                          │
  │  Exception (예외) = 엘리베이터 고장 (대체 수단 가능)     │
  │    → FormatException, IOException, HttpException         │
  │    → 예상 가능, try/catch 로 복구 가능                   │
  └──────────────────────────────────────────────────────────┘

★ Dart 예외 계층
  ┌─ Object
  │  ├─ Error (잡지 않는 게 일반적)
  │  │  ├─ TypeError
  │  │  ├─ StackOverflowError
  │  │  ├─ ArgumentError
  │  │  └─ StateError
  │  │
  │  └─ Exception (잡아서 처리)
  │     ├─ FormatException
  │     ├─ IOException
  │     └─ 사용자 정의 Exception
*/

void lesson1ErrorVsException() {
  print('[레슨 1] Error vs Exception');

  // ── Exception: 예상 가능, 복구 가능 ──
  try {
    int.parse('abc');   // FormatException 발생
  } on FormatException catch (e) {
    print('  FormatException 잡음: $e');
  }

  // ── Error: 프로그래머 실수 ──
  try {
    final list = <int>[];
    print(list[5]);     // RangeError 발생
  } on RangeError catch (e) {
    print('  RangeError 잡음: $e');
  }

  // ── 아무 것이나 throw 가능 (Dart 특징) ──
  try {
    throw '문자열도 던질 수 있다!';   // 비권장이지만 가능
  } catch (e) {
    print('  문자열 예외: $e');
  }
  print('');
}


// =====================================================================
// 레슨 2 — try / catch / finally
// =====================================================================
/*
★ try/catch/finally 구조

  ┌──────────────────────────────────────────────────┐
  │  try {                                           │
  │    // 위험한 코드                                │
  │  } on 특정예외 catch (e, stackTrace) {           │
  │    // 특정 예외 처리                             │
  │  } catch (e, stackTrace) {                       │
  │    // 나머지 모든 예외                           │
  │  } finally {                                     │
  │    // 성공이든 실패든 항상 실행                   │
  │  }                                               │
  └──────────────────────────────────────────────────┘

★ 비유: 요리
  - try    = 요리 시도
  - catch  = 실패 시 대처 (불 끄고, 창문 열기)
  - finally = 마무리 청소 (성공이든 실패든)

★ catch 의 두 번째 매개변수 stackTrace
  - 에러가 어디서 발생했는지 추적 경로
  - 디버깅에 매우 유용!
*/

double divide(int a, int b) {
  if (b == 0) throw ArgumentError('0으로 나눌 수 없습니다');
  return a / b;
}

void lesson2TryCatchFinally() {
  print('[레슨 2] try / catch / finally');

  // ── on: 특정 예외만 잡기 ──
  try {
    divide(10, 0);
  } on ArgumentError catch (e) {
    print('  on ArgumentError: ${e.message}');
  }

  // ── catch: 모든 예외 잡기 + stackTrace ──
  try {
    int.parse('not_a_number');
  } catch (e, stackTrace) {
    print('  catch all: $e');
    print('  스택 첫줄: ${stackTrace.toString().split('\n').first}');
  }

  // ── finally: 항상 실행 ──
  print('  --- finally 테스트 ---');
  try {
    final result = divide(10, 2);
    print('  성공: $result');
  } catch (e) {
    print('  실패: $e');
  } finally {
    print('  finally: 항상 이 줄은 실행됩니다');
  }

  // ── 여러 on 절 순서대로 ──
  try {
    throw FormatException('잘못된 형식');
  } on FormatException catch (e) {
    print('  FormatException: $e');
  } on ArgumentError catch (e) {
    print('  ArgumentError: $e');
  } catch (e) {
    print('  기타: $e');
  }
  print('');
}


// =====================================================================
// 레슨 3 — 커스텀 예외 만들기
// =====================================================================
/*
★ 커스텀 예외 = "내 앱에 맞는 전용 예외 클래스"

  ┌──────────────────────────────────────────────────┐
  │  class InsufficientFundsException implements     │
  │    Exception {                                   │
  │    final int requested;                          │
  │    final int available;                          │
  │    // ...                                        │
  │  }                                               │
  └──────────────────────────────────────────────────┘

★ 왜 만들까?
  - "어떤 종류의 문제인지" 타입으로 구분 가능
  - on 절로 정확히 잡을 수 있음
  - 에러 메시지에 유용한 정보 포함 가능
*/

class InsufficientFundsException implements Exception {
  final int requested;
  final int available;

  InsufficientFundsException({
    required this.requested,
    required this.available,
  });

  @override
  String toString() =>
      'InsufficientFundsException: ${requested}원 요청, ${available}원 가용';
}

class InvalidScoreException implements Exception {
  final int score;
  final String reason;

  InvalidScoreException(this.score, this.reason);

  @override
  String toString() => 'InvalidScoreException: $score점 — $reason';
}

class SimpleBank {
  int _balance;
  final String owner;

  SimpleBank(this.owner, this._balance);

  int get balance => _balance;

  void withdraw(int amount) {
    if (amount <= 0) {
      throw ArgumentError('출금액은 양수여야 합니다: $amount');
    }
    if (amount > _balance) {
      throw InsufficientFundsException(
        requested: amount,
        available: _balance,
      );
    }
    _balance -= amount;
  }
}

void lesson3CustomException() {
  print('[레슨 3] 커스텀 예외');

  final bank = SimpleBank('민수', 10000);

  // ── 정상 출금 ──
  try {
    bank.withdraw(3000);
    print('  출금 성공! 잔액: ${bank.balance}원');
  } catch (e) {
    print('  에러: $e');
  }

  // ── 잔액 부족 ──
  try {
    bank.withdraw(50000);
  } on InsufficientFundsException catch (e) {
    print('  잔액 부족: $e');
    print('    부족분: ${e.requested - e.available}원');
  }

  // ── 음수 출금 ──
  try {
    bank.withdraw(-100);
  } on ArgumentError catch (e) {
    print('  잘못된 인자: $e');
  }

  // ── InvalidScoreException ──
  try {
    final score = 150;
    if (score < 0 || score > 100) {
      throw InvalidScoreException(score, '0~100 범위를 벗어남');
    }
  } on InvalidScoreException catch (e) {
    print('  점수 오류: $e');
  }
  print('');
}


// =====================================================================
// 레슨 4 — rethrow 와 예외 전파
// =====================================================================
/*
★ rethrow = "예외를 잡아서 로깅 등 처리 후, 다시 던지기"

  ┌──────────────────────────────────────────────────┐
  │  try {                                           │
  │    riskyOperation();                             │
  │  } catch (e) {                                   │
  │    log('에러 발생: $e');  ← 로깅                 │
  │    rethrow;               ← 다시 던짐            │
  │  }                                               │
  └──────────────────────────────────────────────────┘

★ rethrow vs throw e
  - rethrow: 원래 스택 트레이스 보존 (디버깅에 좋음)
  - throw e: 새 스택 트레이스 생성 (원본 정보 손실)
*/

void innerFunction() {
  throw FormatException('내부 함수에서 발생한 에러');
}

void middleFunction() {
  try {
    innerFunction();
  } catch (e) {
    print('  [middle] 로깅: $e');
    rethrow;   // 스택 트레이스 보존하며 다시 던짐
  }
}

void lesson4Rethrow() {
  print('[레슨 4] rethrow 와 예외 전파');

  try {
    middleFunction();
  } on FormatException catch (e) {
    print('  [outer] 최종 처리: $e');
  }
  print('');
}


// =====================================================================
// 레슨 5 — assert (디버그 전용 검증)
// =====================================================================
/*
★ assert = "이 조건이 참이어야 한다" 는 개발 중 안전장치

  ┌──────────────────────────────────────────────────┐
  │  assert(score >= 0 && score <= 100);             │
  │  assert(name.isNotEmpty, '이름은 비어있을 수 없음');│
  └──────────────────────────────────────────────────┘

★ 특징
  - 디버그 모드에서만 동작 (릴리스에서는 무시됨)
  - 실패 시 AssertionError 발생
  - 프로덕션 코드에서는 예외를 직접 던져야 함

★ assert vs throw
  ┌─────────┬──────────────────────────────────────────┐
  │ assert  │ 개발 중 버그 잡기 (릴리스에서 사라짐)     │
  │ throw   │ 실제 운영에서도 에러 처리 (항상 동작)     │
  └─────────┴──────────────────────────────────────────┘
*/

class ValidatedStudent {
  final String name;
  final int score;

  ValidatedStudent(this.name, this.score)
      : assert(name.isNotEmpty, '이름이 비어있습니다'),
        assert(score >= 0 && score <= 100, '점수는 0~100: $score');

  @override
  String toString() => 'ValidatedStudent($name, $score)';
}

void lesson5Assert() {
  print('[레슨 5] assert (디버그 전용 검증)');

  // ── 정상 ──
  final s1 = ValidatedStudent('민수', 92);
  print('  정상: $s1');

  // ── assert 실패 (디버그 모드에서만) ──
  // dart run 으로 실행하면 assert 가 작동함
  // dart compile exe 로 컴파일한 릴리스에서는 assert 무시됨
  try {
    // ignore: unnecessary_statements
    ValidatedStudent('', 50);
  } catch (e) {
    print('  assert 실패: $e');
  }

  try {
    // ignore: unnecessary_statements
    ValidatedStudent('지우', 150);
  } catch (e) {
    print('  assert 실패: $e');
  }

  // ── 함수 내 assert ──
  void setAge(int age) {
    assert(age > 0, '나이는 양수여야 합니다');
    print('  나이 설정: $age');
  }

  setAge(25);
  print('');
}


// =====================================================================
// 레슨 6 — 디버깅 기법: print 디버깅
// =====================================================================
/*
★ 가장 기본적인 디버깅 = "의심되는 곳에 print 찍기"

  비유: 보물찾기 힌트
  - 중간중간 "여기까지 왔다!", "이 값은 42이다" 출력
  - 어디서 문제가 생겼는지 범위를 좁혀감

★ 디버깅 3단계
  1. 재현: 버그를 다시 발생시킨다
  2. 추적: 중간값을 출력하며 원인을 좁힌다
  3. 수정: 원인을 고치고 테스트한다

★ 유용한 디버깅 도구들
  ┌──────────────────────┬──────────────────────────────┐
  │ 도구                 │ 용도                          │
  ├──────────────────────┼──────────────────────────────┤
  │ print()              │ 기본 출력                     │
  │ debugPrint()         │ Flutter 전용 (길이 제한)      │
  │ log() (dart:developer)│ 개발자 도구 연동             │
  │ assert()             │ 조건 검증                     │
  │ toString()           │ 객체 상태 확인                │
  │ runtimeType          │ 동적 타입 확인                │
  └──────────────────────┴──────────────────────────────┘
*/

int wrongAverage(List<int> scores) {
  final total = scores.reduce((a, b) => a + b);
  return total ~/ (scores.length - 1);   // 버그: length - 1 은 잘못됨!
}

double correctAverage(List<int> scores) {
  final total = scores.reduce((a, b) => a + b);
  return total / scores.length;          // 수정: length 로 나눔
}

void lesson6PrintDebugging() {
  print('[레슨 6] 디버깅 기법 — print 디버깅');

  final scores = [80, 90, 70];

  // ── 1단계: 재현 ──
  print('  잘못된 평균: ${wrongAverage(scores)}');   // 120 (???)
  print('  올바른 평균: ${correctAverage(scores)}'); // 80.0

  // ── 2단계: 추적 (중간값 출력) ──
  final total = scores.reduce((a, b) => a + b);
  print('  [추적] total = $total');                    // 240
  print('  [추적] scores.length = ${scores.length}');  // 3
  print('  [추적] length - 1 = ${scores.length - 1}'); // 2 ← 여기가 문제!
  print('  [추적] 240 / 2 = ${240 ~/ 2}');             // 120

  // ── 3단계: 원인 파악 ──
  print('  [결론] length - 1 이 아니라 length 로 나눠야 합니다!');
  print('');
}


// =====================================================================
// 레슨 7 — 스택 트레이스 읽는 법
// =====================================================================
/*
★ 스택 트레이스 = "에러가 발생하기까지의 함수 호출 경로"

  비유: 빵 부스러기 (헨젤과 그레텔)
  - 어디서 출발해서 어디에서 넘어졌는지 추적 가능

  ┌──────────────────────────────────────────────────┐
  │  #0  divide (file:///main.dart:42:5)             │
  │  #1  calculate (file:///main.dart:50:10)         │
  │  #2  main (file:///main.dart:60:3)               │
  │      ↑ 가장 최근     ↑ 파일        ↑ 줄번호      │
  └──────────────────────────────────────────────────┘

★ 읽는 순서
  1. #0 부터 위에서 아래로 읽기
  2. #0 이 에러가 실제 발생한 곳
  3. 위에서 아래로 갈수록 호출한 쪽 (원인 추적)
*/

void functionC() {
  throw StateError('functionC 에서 에러 발생!');
}

void functionB() {
  functionC();
}

void functionA() {
  functionB();
}

void lesson7StackTrace() {
  print('[레슨 7] 스택 트레이스 읽는 법');

  try {
    functionA();
  } catch (e, stackTrace) {
    print('  에러: $e');
    print('  --- 스택 트레이스 (처음 5줄) ---');
    final lines = stackTrace.toString().split('\n');
    for (var i = 0; i < lines.length && i < 5; i++) {
      print('  ${lines[i]}');
    }
  }

  // ── StackTrace.current 로 현재 위치 확인 ──
  print('  --- 현재 스택 (처음 3줄) ---');
  final current = StackTrace.current.toString().split('\n');
  for (var i = 0; i < current.length && i < 3; i++) {
    print('  ${current[i]}');
  }
  print('');
}


// =====================================================================
// 레슨 8 — 종합 예제: 안전한 계산기
// =====================================================================
/*
★ 지금까지 배운 에러 처리를 모두 합쳐서
  입력 검증 + 예외 처리 + 디버깅 로깅이 포함된 계산기
*/

class CalculatorException implements Exception {
  final String operation;
  final String reason;

  CalculatorException(this.operation, this.reason);

  @override
  String toString() => 'CalculatorException($operation): $reason';
}

class SafeCalculator {
  static final List<String> _log = [];

  static void _addLog(String entry) {
    _log.add('[${DateTime.now().millisecond}ms] $entry');
  }

  static double calculate(String op, double a, double b) {
    _addLog('$a $op $b 계산 시작');

    switch (op) {
      case '+':
        return a + b;
      case '-':
        return a - b;
      case '*':
        return a * b;
      case '/':
        if (b == 0) {
          _addLog('에러: 0으로 나누기 시도');
          throw CalculatorException('/', '0으로 나눌 수 없습니다');
        }
        return a / b;
      case '%':
        if (b == 0) {
          throw CalculatorException('%', '0으로 나머지 연산 불가');
        }
        return a % b;
      default:
        throw CalculatorException(op, '지원하지 않는 연산자');
    }
  }

  static void printLog() {
    print('  === 계산 로그 ===');
    for (final entry in _log) {
      print('    $entry');
    }
    _log.clear();
  }
}

void lesson8SafeCalculator() {
  print('[레슨 8] 종합 예제 — 안전한 계산기');

  final operations = [
    ('10 + 3', '+', 10.0, 3.0),
    ('10 / 3', '/', 10.0, 3.0),
    ('10 / 0', '/', 10.0, 0.0),
    ('10 ^ 3', '^', 10.0, 3.0),
  ];

  for (final (label, op, a, b) in operations) {
    try {
      final result = SafeCalculator.calculate(op, a, b);
      print('  $label = ${result.toStringAsFixed(2)}');
    } on CalculatorException catch (e) {
      print('  $label → 에러: ${e.reason}');
    }
  }

  SafeCalculator.printLog();
  print('');
}


// =====================================================================
// main — 전체 레슨 실행
// =====================================================================
void main() {
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('  Dart 11단계 : 에러 처리와 디버깅');
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('');

  lesson1ErrorVsException();
  lesson2TryCatchFinally();
  lesson3CustomException();
  lesson4Rethrow();
  lesson5Assert();
  lesson6PrintDebugging();
  lesson7StackTrace();
  lesson8SafeCalculator();

  print('■■■ 11단계 완료! ■■■');
}
