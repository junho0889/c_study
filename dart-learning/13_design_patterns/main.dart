/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Dart 학습 13단계: 디자인 패턴
  ─ Singleton · Factory · Strategy · Observer · Builder · Repository ─

  ■ 실행: dart run main.dart
  ■ 컴파일: dart compile exe main.dart

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// =====================================================================
// 레슨 1 — 디자인 패턴이 뭘까?
// =====================================================================
/*
★ 디자인 패턴 = "자주 만나는 문제의 검증된 해결법 모음"

  비유: 요리 레시피
  ┌──────────────────────────────────────────────────────────┐
  │  처음 요리하는 사람 → 레시피(패턴) 따라 하면 실패 줄임  │
  │  경험 많은 요리사   → 레시피를 변형해서 자기만의 요리   │
  │                                                          │
  │  패턴을 "외우는 것" 이 아니라                            │
  │  "어떤 문제를 왜 이렇게 풀었는지" 이해하는 것이 핵심!   │
  └──────────────────────────────────────────────────────────┘

★ 주요 패턴 분류
  ┌──────────────┬──────────────────────────────────────────┐
  │ 생성 패턴    │ 객체를 어떻게 만들까? (Singleton, Factory)│
  │ 구조 패턴    │ 객체를 어떻게 조합할까? (Adapter, Decorator)│
  │ 행위 패턴    │ 객체가 어떻게 소통할까? (Observer, Strategy)│
  └──────────────┴──────────────────────────────────────────┘

★ 주의: 패턴 남용 금지!
  - 간단한 문제에 복잡한 패턴 → 오버엔지니어링
  - "이 문제에 정말 패턴이 필요한가?" 항상 먼저 생각
*/

void lesson1WhatIsDesignPattern() {
  print('[레슨 1] 디자인 패턴이 뭘까?');
  print('  패턴 = 자주 만나는 문제의 검증된 해결법');
  print('  핵심 = 이름을 외우는 게 아니라 "왜" 를 이해하는 것');
  print('  주의 = 간단한 문제에 복잡한 패턴은 오히려 해로움');
  print('');
}


// =====================================================================
// 레슨 2 — Singleton 패턴
// =====================================================================
/*
★ Singleton = "인스턴스를 딱 하나만 만들겠다"

  비유: 대통령
  - 나라에 대통령은 한 명만 있어야 함
  - 누가 "대통령" 을 요청해도 같은 사람을 가리킴

  ┌──────────────────────────────────────────────────────────┐
  │  class Database {                                        │
  │    static Database? _instance;                           │
  │    Database._();                       ← 프라이빗 생성자 │
  │    factory Database() {                                  │
  │      _instance ??= Database._();                        │
  │      return _instance!;                                  │
  │    }                                                     │
  │  }                                                       │
  │                                                          │
  │  final db1 = Database();                                 │
  │  final db2 = Database();                                 │
  │  identical(db1, db2);  // true! (같은 객체)              │
  └──────────────────────────────────────────────────────────┘

★ 용도: DB 연결, 설정 관리, 로거 등 "하나만 있어야 하는 것"
*/

class AppLogger {
  static AppLogger? _instance;
  final List<String> _logs = [];

  // 프라이빗 생성자
  AppLogger._internal();

  // 팩토리: 항상 같은 인스턴스 반환
  factory AppLogger() {
    _instance ??= AppLogger._internal();
    return _instance!;
  }

  void log(String message) {
    final timestamp = DateTime.now().millisecond;
    _logs.add('[$timestamp] $message');
  }

  void printAll() {
    for (final log in _logs) {
      print('    $log');
    }
  }

  int get count => _logs.length;
  void clear() => _logs.clear();
}

void lesson2Singleton() {
  print('[레슨 2] Singleton 패턴');

  final logger1 = AppLogger();
  final logger2 = AppLogger();

  logger1.log('앱 시작');
  logger2.log('사용자 로그인');  // 같은 인스턴스에 기록!

  print('  identical? ${identical(logger1, logger2)}');  // true
  print('  로그 수: ${logger1.count}');                   // 2
  logger1.printAll();
  logger1.clear();
  print('');
}


// =====================================================================
// 레슨 3 — Factory 패턴
// =====================================================================
/*
★ Factory = "생성 로직을 한 곳에 모아서 객체를 만들어 주는 공장"

  비유: 자동차 공장
  - "세단 주세요" → 세단 생산
  - "SUV 주세요"  → SUV 생산
  - 고객은 공장 내부를 몰라도 됨

  ┌──────────────────────────────────────────────────┐
  │  abstract class Shape {                          │
  │    factory Shape.create(String type) {           │
  │      switch (type) {                             │
  │        case 'circle': return Circle();           │
  │        case 'square': return Square();           │
  │        default: throw '알 수 없는 도형';          │
  │      }                                           │
  │    }                                             │
  │  }                                               │
  └──────────────────────────────────────────────────┘
*/

abstract class Notification {
  String get channel;
  void send(String message);

  // ── 팩토리 메서드 ──
  factory Notification.create(String type) {
    switch (type) {
      case 'email':
        return EmailNotification();
      case 'sms':
        return SmsNotification();
      case 'push':
        return PushNotification();
      default:
        throw ArgumentError('지원하지 않는 알림 타입: $type');
    }
  }
}

class EmailNotification implements Notification {
  @override
  String get channel => '이메일';

  @override
  void send(String message) {
    print('    📧 이메일 발송: $message');
  }
}

class SmsNotification implements Notification {
  @override
  String get channel => 'SMS';

  @override
  void send(String message) {
    print('    📱 SMS 발송: $message');
  }
}

class PushNotification implements Notification {
  @override
  String get channel => '푸시';

  @override
  void send(String message) {
    print('    🔔 푸시 알림: $message');
  }
}

void lesson3Factory() {
  print('[레슨 3] Factory 패턴');

  final types = ['email', 'sms', 'push'];

  for (final type in types) {
    final noti = Notification.create(type);
    print('  채널: ${noti.channel}');
    noti.send('주문이 완료되었습니다.');
  }

  // 잘못된 타입
  try {
    Notification.create('telegram');
  } on ArgumentError catch (e) {
    print('  에러: $e');
  }
  print('');
}


// =====================================================================
// 레슨 4 — Strategy 패턴
// =====================================================================
/*
★ Strategy = "같은 일을 하는 여러 방법을 바꿔 끼울 수 있게"

  비유: 출퇴근 방법
  - 버스 전략, 지하철 전략, 자전거 전략
  - "출퇴근" 이라는 행동은 같지만 방법이 다름
  - 날씨에 따라 전략을 바꿈

  ┌──────────────────────────────────────────────────┐
  │  abstract class SortStrategy {                   │
  │    List<int> sort(List<int> data);               │
  │  }                                               │
  │                                                  │
  │  class BubbleSort implements SortStrategy { }    │
  │  class QuickSort  implements SortStrategy { }    │
  │                                                  │
  │  class Sorter {                                  │
  │    SortStrategy strategy;  ← 바꿔 끼울 수 있음   │
  │    void doSort(List<int> data) {                 │
  │      strategy.sort(data);                        │
  │    }                                             │
  │  }                                               │
  └──────────────────────────────────────────────────┘
*/

abstract class DiscountStrategy {
  String get name;
  int apply(int price);
}

class NoDiscount implements DiscountStrategy {
  @override
  String get name => '할인 없음';

  @override
  int apply(int price) => price;
}

class PercentDiscount implements DiscountStrategy {
  final int percent;
  PercentDiscount(this.percent);

  @override
  String get name => '$percent% 할인';

  @override
  int apply(int price) => price - (price * percent ~/ 100);
}

class FixedDiscount implements DiscountStrategy {
  final int amount;
  FixedDiscount(this.amount);

  @override
  String get name => '${amount}원 할인';

  @override
  int apply(int price) => price - amount;
}

class ShoppingCart {
  DiscountStrategy _strategy;

  ShoppingCart(this._strategy);

  void setStrategy(DiscountStrategy strategy) {
    _strategy = strategy;
  }

  int checkout(int totalPrice) {
    final result = _strategy.apply(totalPrice);
    print('  전략: ${_strategy.name}');
    print('  원래: ${totalPrice}원 → 결제: ${result}원');
    return result;
  }
}

void lesson4Strategy() {
  print('[레슨 4] Strategy 패턴');

  final cart = ShoppingCart(NoDiscount());
  cart.checkout(10000);

  cart.setStrategy(PercentDiscount(20));
  cart.checkout(10000);

  cart.setStrategy(FixedDiscount(3000));
  cart.checkout(10000);
  print('');
}


// =====================================================================
// 레슨 5 — Observer 패턴
// =====================================================================
/*
★ Observer = "상태가 변하면 구독자들에게 자동 알림"

  비유: 유튜브 구독
  ┌──────────────────────────────────────────────────┐
  │  유튜버(Subject) → 새 영상 업로드                │
  │  구독자A(Observer) → 알림 받음                   │
  │  구독자B(Observer) → 알림 받음                   │
  │  비구독자         → 알림 안 받음                 │
  └──────────────────────────────────────────────────┘

★ Dart 에서는 Stream 이 Observer 패턴의 내장 구현!
  여기서는 직접 구현해서 원리를 이해합니다.
*/

typedef EventCallback = void Function(String event, dynamic data);

class EventBus {
  final Map<String, List<EventCallback>> _listeners = {};

  void subscribe(String event, EventCallback callback) {
    _listeners.putIfAbsent(event, () => []);
    _listeners[event]!.add(callback);
  }

  void unsubscribe(String event, EventCallback callback) {
    _listeners[event]?.remove(callback);
  }

  void emit(String event, [dynamic data]) {
    final callbacks = _listeners[event];
    if (callbacks != null) {
      for (final cb in callbacks) {
        cb(event, data);
      }
    }
  }
}

void lesson5Observer() {
  print('[레슨 5] Observer 패턴');

  final bus = EventBus();

  // 구독자 등록
  bus.subscribe('login', (event, data) {
    print('    [로그] $event: $data');
  });

  bus.subscribe('login', (event, data) {
    print('    [환영] ${data}님 환영합니다!');
  });

  bus.subscribe('purchase', (event, data) {
    print('    [결제] ${data}원 결제 완료');
  });

  // 이벤트 발행
  bus.emit('login', '민수');
  bus.emit('purchase', 25000);
  bus.emit('logout', '민수');   // 구독자 없음 → 조용히 넘어감
  print('');
}


// =====================================================================
// 레슨 6 — Builder 패턴
// =====================================================================
/*
★ Builder = "복잡한 객체를 단계적으로 조립"

  비유: 햄버거 커스텀 주문
  - 빵 선택 → 패티 선택 → 토핑 추가 → 소스 선택 → 완성!
  - 생성자에 매개변수 10개 넣는 것보다 가독성 좋음

  ┌──────────────────────────────────────────────────┐
  │  final burger = BurgerBuilder()                  │
  │    .setBun('참깨')                               │
  │    .setPatty('소고기')                           │
  │    .addTopping('양상추')                         │
  │    .addTopping('토마토')                         │
  │    .setSauce('케찹')                             │
  │    .build();                                     │
  └──────────────────────────────────────────────────┘
*/

class HttpRequest {
  final String method;
  final String url;
  final Map<String, String> headers;
  final String? body;
  final Duration timeout;

  HttpRequest._({
    required this.method,
    required this.url,
    required this.headers,
    this.body,
    required this.timeout,
  });

  void display() {
    print('    $method $url');
    print('    Headers: $headers');
    if (body != null) print('    Body: $body');
    print('    Timeout: ${timeout.inSeconds}s');
  }
}

class HttpRequestBuilder {
  String _method = 'GET';
  String _url = '';
  final Map<String, String> _headers = {};
  String? _body;
  Duration _timeout = const Duration(seconds: 30);

  HttpRequestBuilder(this._url);

  HttpRequestBuilder method(String m) {
    _method = m;
    return this;    // this 반환 → 체이닝 가능
  }

  HttpRequestBuilder header(String key, String value) {
    _headers[key] = value;
    return this;
  }

  HttpRequestBuilder body(String b) {
    _body = b;
    return this;
  }

  HttpRequestBuilder timeout(Duration d) {
    _timeout = d;
    return this;
  }

  HttpRequest build() {
    if (_url.isEmpty) throw StateError('URL 은 필수입니다');
    return HttpRequest._(
      method: _method,
      url: _url,
      headers: Map.unmodifiable(_headers),
      body: _body,
      timeout: _timeout,
    );
  }
}

void lesson6Builder() {
  print('[레슨 6] Builder 패턴');

  final request = HttpRequestBuilder('https://api.example.com/users')
      .method('POST')
      .header('Content-Type', 'application/json')
      .header('Authorization', 'Bearer token123')
      .body('{"name": "민수", "age": 25}')
      .timeout(const Duration(seconds: 10))
      .build();

  request.display();

  // 간단한 GET 요청
  final getReq = HttpRequestBuilder('https://api.example.com/items')
      .build();

  print('  --- 간단한 요청 ---');
  getReq.display();
  print('');
}


// =====================================================================
// 레슨 7 — Repository 패턴
// =====================================================================
/*
★ Repository = "데이터 접근 로직을 한 곳에 모아 추상화"

  비유: 도서관 사서
  ┌──────────────────────────────────────────────────┐
  │  앱 코드: "민수 정보 주세요"                     │
  │                    ↓                             │
  │  Repository: DB 인지, API 인지, 캐시인지 알아서  │
  │              찾아서 반환                          │
  │                    ↓                             │
  │  앱 코드: 데이터 받아서 사용 (출처 몰라도 됨)    │
  └──────────────────────────────────────────────────┘

★ 장점
  - 데이터 소스 변경 시 Repository 만 수정
  - 테스트할 때 Mock Repository 로 교체 쉬움
*/

class User {
  final int id;
  final String name;
  final String email;

  User(this.id, this.name, this.email);

  @override
  String toString() => 'User($id, $name, $email)';
}

// 추상 인터페이스
abstract class UserRepository {
  Future<User?> findById(int id);
  Future<List<User>> findAll();
  Future<void> save(User user);
  Future<void> delete(int id);
}

// 메모리 기반 구현 (테스트용)
class InMemoryUserRepository implements UserRepository {
  final Map<int, User> _store = {};

  @override
  Future<User?> findById(int id) async => _store[id];

  @override
  Future<List<User>> findAll() async => _store.values.toList();

  @override
  Future<void> save(User user) async => _store[user.id] = user;

  @override
  Future<void> delete(int id) async => _store.remove(id);
}

Future<void> lesson7Repository() async {
  print('[레슨 7] Repository 패턴');

  final repo = InMemoryUserRepository();

  // CRUD 연산
  await repo.save(User(1, '민수', 'minsu@example.com'));
  await repo.save(User(2, '지우', 'jiwoo@example.com'));
  await repo.save(User(3, '서연', 'seoyeon@example.com'));

  final all = await repo.findAll();
  print('  전체: $all');

  final found = await repo.findById(2);
  print('  ID 2: $found');

  await repo.delete(1);
  final afterDelete = await repo.findAll();
  print('  삭제 후: $afterDelete');

  // ★ 나중에 DB 기반으로 바꿔도 코드 구조는 동일!
  // final repo = PostgresUserRepository();  ← 이것만 바꾸면 됨
  print('');
}


// =====================================================================
// main — 전체 레슨 실행
// =====================================================================
Future<void> main() async {
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('  Dart 13단계 : 디자인 패턴');
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('');

  lesson1WhatIsDesignPattern();
  lesson2Singleton();
  lesson3Factory();
  lesson4Strategy();
  lesson5Observer();
  lesson6Builder();
  await lesson7Repository();

  print('■■■ 13단계 완료! ■■■');
}
