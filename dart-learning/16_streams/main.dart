/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Dart 학습 16단계: Streams (스트림)
  ─ Stream · async* · StreamController · 변환 · 구독 · 브로드캐스트 ─

  ■ 실행: dart run main.dart
  ■ 컴파일: dart compile exe main.dart

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

import 'dart:async';

// =====================================================================
// 레슨 1 — Stream 이 뭘까?
// =====================================================================
/*
★ Stream = "데이터가 한 번에 오는 게 아니라 차례차례 흘러오는 것"

  비유: 컨베이어 벨트
  ┌──────────────────────────────────────────────────────────┐
  │  Future = 택배 1개 배달 (한 번에 끝)                     │
  │  Stream = 컨베이어 벨트 (물건이 하나씩 계속 흘러옴)      │
  │                                                          │
  │  [사과] → [바나나] → [포도] → [끝!]                     │
  │   ↑ 첫 데이터    ↑ 중간        ↑ 마지막                 │
  └──────────────────────────────────────────────────────────┘

★ Future vs Stream
  ┌──────────────┬──────────────────────────────────────────┐
  │ Future<T>    │ 값 하나를 나중에 반환                     │
  │ Stream<T>    │ 값 여러 개를 시간에 걸쳐 반환             │
  └──────────────┴──────────────────────────────────────────┘

★ Stream 이벤트 3종류
  ┌──────────────┬──────────────────────────────────────────┐
  │ data event   │ 실제 데이터 전달                          │
  │ error event  │ 에러 발생 알림                            │
  │ done event   │ 스트림 종료 알림                          │
  └──────────────┴──────────────────────────────────────────┘

★ 실제 사용 예
  - 채팅 메시지 수신
  - 센서 데이터 (GPS, 가속도계)
  - 파일 대용량 읽기
  - 웹소켓 데이터
  - Firebase 실시간 데이터
*/

void lesson1WhatIsStream() {
  print('[레슨 1] Stream 이란?');
  print('  Future = 택배 1개 (값 하나, 한 번)');
  print('  Stream = 컨베이어 벨트 (값 여러 개, 시간에 걸쳐)');
  print('  이벤트: data(데이터), error(에러), done(종료)');
  print('');
}


// =====================================================================
// 레슨 2 — async* 와 yield 로 Stream 만들기
// =====================================================================
/*
★ async* = "이 함수는 Stream 을 반환합니다"
  yield  = "값을 하나 내보냅니다"
  yield* = "다른 Stream 을 통째로 내보냅니다"

  ┌──────────────────────────────────────────────────────────┐
  │  Stream<int> countStream(int max) async* {               │
  │    for (var i = 1; i <= max; i++) {                      │
  │      await Future.delayed(Duration(seconds: 1));         │
  │      yield i;    ← 1초마다 값을 하나씩 내보냄            │
  │    }                                                     │
  │  }                                                       │
  │                                                          │
  │  ★ async* (별표 주의!) = Stream 을 만드는 함수           │
  │  ★ async  (별표 없음)  = Future 를 만드는 함수           │
  └──────────────────────────────────────────────────────────┘
*/

Stream<String> snackStream() async* {
  yield '우유 준비';
  await Future<void>.delayed(const Duration(milliseconds: 50));
  yield '샌드위치 준비';
  await Future<void>.delayed(const Duration(milliseconds: 50));
  yield '사과 준비';
  await Future<void>.delayed(const Duration(milliseconds: 50));
  yield '과자 준비';
}

Stream<int> countDown(int from) async* {
  for (var i = from; i >= 0; i--) {
    await Future<void>.delayed(const Duration(milliseconds: 30));
    yield i;
  }
}

// yield* : 다른 Stream 을 연결
Stream<int> doubleCountDown() async* {
  yield* countDown(3);    // 3, 2, 1, 0
  yield -1;               // 구분자
  yield* countDown(2);    // 2, 1, 0
}

Future<void> lesson2AsyncStar() async {
  print('[레슨 2] async* 와 yield');

  // ── await for 로 Stream 소비 ──
  print('  간식 준비:');
  await for (final item in snackStream()) {
    print('    → $item');
  }

  // ── 카운트다운 ──
  final countdown = <int>[];
  await for (final n in countDown(5)) {
    countdown.add(n);
  }
  print('  카운트다운: $countdown');

  // ── yield* (스트림 연결) ──
  final double = <int>[];
  await for (final n in doubleCountDown()) {
    double.add(n);
  }
  print('  이중 카운트다운: $double');
  print('');
}


// =====================================================================
// 레슨 3 — Stream 변환 (map, where, take, skip)
// =====================================================================
/*
★ Stream 변환 메서드 (List 와 비슷!)

  ┌──────────────┬──────────────────────────────────────────┐
  │ 메서드       │ 동작                                     │
  ├──────────────┼──────────────────────────────────────────┤
  │ map          │ 각 요소를 변환                           │
  │ where        │ 조건에 맞는 요소만 통과                  │
  │ take         │ 처음 N개만 가져옴                        │
  │ skip         │ 처음 N개 건너뜀                          │
  │ distinct     │ 중복 제거                                │
  │ expand       │ 각 요소를 여러 개로 확장                 │
  │ transform    │ StreamTransformer 로 변환                │
  └──────────────┴──────────────────────────────────────────┘

★ 체이닝 가능!
  stream.where(조건).map(변환).take(3)
*/

Stream<int> numberStream() async* {
  for (var i = 1; i <= 10; i++) {
    yield i;
  }
}

Future<void> lesson3Transformations() async {
  print('[레슨 3] Stream 변환');

  // ── map: 변환 ──
  final doubled = await numberStream()
      .map((n) => n * 2)
      .toList();
  print('  map (2배): $doubled');

  // ── where: 필터 ──
  final evens = await numberStream()
      .where((n) => n % 2 == 0)
      .toList();
  print('  where (짝수): $evens');

  // ── take: 처음 N개 ──
  final firstThree = await numberStream()
      .take(3)
      .toList();
  print('  take(3): $firstThree');

  // ── skip: N개 건너뛰기 ──
  final afterSkip = await numberStream()
      .skip(7)
      .toList();
  print('  skip(7): $afterSkip');

  // ── 체이닝 ──
  final result = await numberStream()
      .where((n) => n > 3)       // 4이상
      .map((n) => n * 10)        // 10배
      .take(3)                   // 3개만
      .toList();
  print('  체이닝 (>3, *10, take 3): $result');

  // ── expand: 확장 ──
  final expanded = await Stream.fromIterable([1, 2, 3])
      .expand((n) => [n, n * 10])
      .toList();
  print('  expand: $expanded');
  print('');
}


// =====================================================================
// 레슨 4 — StreamController
// =====================================================================
/*
★ StreamController = "Stream 을 수동으로 제어하는 리모컨"

  ┌──────────────────────────────────────────────────────────┐
  │  final controller = StreamController<String>();          │
  │                                                          │
  │  // 데이터 넣기 (생산자 쪽)                               │
  │  controller.add('사과');                                  │
  │  controller.add('바나나');                                │
  │  controller.addError('에러!');                            │
  │  controller.close();                                     │
  │                                                          │
  │  // 데이터 듣기 (소비자 쪽)                               │
  │  controller.stream.listen(                               │
  │    (data) => print(data),                                │
  │    onError: (e) => print('에러: $e'),                    │
  │    onDone: () => print('끝!'),                           │
  │  );                                                      │
  └──────────────────────────────────────────────────────────┘

★ 주의: 일반 StreamController 는 리스너 1명만!
  여러 리스너가 필요하면 broadcast 사용 (레슨 5)
*/

Future<void> lesson4StreamController() async {
  print('[레슨 4] StreamController');

  final controller = StreamController<String>();
  final received = <String>[];

  // ── 리스너 등록 ──
  final subscription = controller.stream.listen(
    (data) {
      received.add(data);
      print('    수신: $data');
    },
    onError: (e) => print('    에러: $e'),
    onDone: () => print('    스트림 종료!'),
  );

  // ── 데이터 전송 ──
  controller.add('첫 번째 메시지');
  controller.add('두 번째 메시지');
  controller.addError('의도적 에러');
  controller.add('에러 후 메시지');

  // 비동기적으로 이벤트가 전달되므로 잠시 대기
  await Future<void>.delayed(const Duration(milliseconds: 50));

  // ── 닫기 ──
  await controller.close();
  await subscription.cancel();

  print('  받은 메시지 수: ${received.length}');
  print('');
}


// =====================================================================
// 레슨 5 — 브로드캐스트 스트림
// =====================================================================
/*
★ Single vs Broadcast Stream

  ┌──────────────────────────────────────────────────────────┐
  │  Single-subscription Stream (기본)                       │
  │  → 리스너 1명만 가능                                     │
  │  → 리스너가 붙기 전까지 데이터 보류                      │
  │                                                          │
  │  Broadcast Stream                                        │
  │  → 리스너 여러 명 가능                                   │
  │  → 리스너 없으면 데이터 버려짐                           │
  └──────────────────────────────────────────────────────────┘

★ 비유:
  Single = 전화 통화 (1:1)
  Broadcast = 라디오 방송 (1:다)
*/

Future<void> lesson5Broadcast() async {
  print('[레슨 5] 브로드캐스트 스트림');

  final controller = StreamController<String>.broadcast();

  // ── 여러 리스너 등록 ──
  final sub1 = controller.stream.listen(
    (data) => print('    [리스너A] $data'),
  );

  final sub2 = controller.stream.listen(
    (data) => print('    [리스너B] $data'),
  );

  // 데이터 전송 → 두 리스너 모두 받음
  controller.add('공지사항: 서버 점검');
  controller.add('공지사항: 업데이트 완료');

  await Future<void>.delayed(const Duration(milliseconds: 50));

  // 리스너B 해제
  await sub2.cancel();
  print('    --- 리스너B 해제 ---');

  controller.add('리스너A만 받는 메시지');

  await Future<void>.delayed(const Duration(milliseconds: 50));

  await sub1.cancel();
  await controller.close();
  print('');
}


// =====================================================================
// 레슨 6 — Stream 구독 관리
// =====================================================================
/*
★ StreamSubscription 으로 구독 제어

  ┌──────────────────────────────────────────────────────────┐
  │  final sub = stream.listen((data) { ... });              │
  │                                                          │
  │  sub.pause();    ← 일시 중지 (데이터 버퍼에 쌓임)       │
  │  sub.resume();   ← 재개                                 │
  │  sub.cancel();   ← 완전 해제 (메모리 누수 방지!)        │
  └──────────────────────────────────────────────────────────┘

★ ★ ★ 중요 ★ ★ ★
  cancel() 을 잊으면 메모리 누수!
  Flutter 에서는 dispose() 에서 반드시 cancel()
*/

Future<void> lesson6SubscriptionManagement() async {
  print('[레슨 6] 구독 관리');

  final controller = StreamController<int>();
  final received = <int>[];

  final sub = controller.stream.listen((data) {
    received.add(data);
  });

  // 데이터 전송
  controller.add(1);
  controller.add(2);
  await Future<void>.delayed(const Duration(milliseconds: 20));

  // ── 일시 중지 ──
  sub.pause();
  controller.add(3);
  controller.add(4);
  await Future<void>.delayed(const Duration(milliseconds: 20));
  print('  pause 중 received: $received');   // [1, 2]

  // ── 재개 → 버퍼에 있던 데이터도 받음 ──
  sub.resume();
  await Future<void>.delayed(const Duration(milliseconds: 20));
  print('  resume 후 received: $received');  // [1, 2, 3, 4]

  // ── 취소 ──
  await sub.cancel();
  controller.add(5);   // 아무도 안 받음
  await Future<void>.delayed(const Duration(milliseconds: 20));
  print('  cancel 후 received: $received');  // [1, 2, 3, 4] (5 없음)

  await controller.close();
  print('');
}


// =====================================================================
// 레슨 7 — Stream 집계 메서드
// =====================================================================
/*
★ Stream 을 하나의 값으로 줄이기

  ┌──────────────────┬──────────────────────────────────────┐
  │ 메서드           │ 반환 타입                             │
  ├──────────────────┼──────────────────────────────────────┤
  │ toList()         │ Future<List<T>>                      │
  │ first            │ Future<T>                            │
  │ last             │ Future<T>                            │
  │ length           │ Future<int>                          │
  │ isEmpty          │ Future<bool>                         │
  │ contains(value)  │ Future<bool>                         │
  │ fold(init, combine)│ Future<S>                          │
  │ reduce(combine)  │ Future<T>                            │
  │ join(separator)  │ Future<String>                       │
  │ any(test)        │ Future<bool>                         │
  │ every(test)      │ Future<bool>                         │
  └──────────────────┴──────────────────────────────────────┘
*/

Future<void> lesson7Aggregation() async {
  print('[레슨 7] Stream 집계 메서드');

  // toList
  final list = await numberStream().toList();
  print('  toList: $list');

  // first, last
  final first = await numberStream().first;
  final last = await numberStream().last;
  print('  first: $first, last: $last');

  // length
  final len = await numberStream().length;
  print('  length: $len');

  // fold (합계)
  final sum = await numberStream().fold<int>(0, (acc, n) => acc + n);
  print('  fold (합계): $sum');

  // any, every
  final hasEven = await numberStream().any((n) => n % 2 == 0);
  final allPositive = await numberStream().every((n) => n > 0);
  print('  짝수 있나? $hasEven, 전부 양수? $allPositive');

  // join
  final joined = await snackStream().join(' → ');
  print('  join: $joined');
  print('');
}


// =====================================================================
// 레슨 8 — 실전 패턴: 이벤트 버스 with Stream
// =====================================================================
/*
★ 이벤트 버스 = "앱 전체에서 이벤트를 주고받는 통로"

  Stream 의 Observer 패턴 활용
  ┌──────────────────────────────────────────────────┐
  │  화면 A → 이벤트 발행 → EventBus (Stream)        │
  │  화면 B → 구독 → 알림 받기                       │
  │  화면 C → 구독 → 알림 받기                       │
  └──────────────────────────────────────────────────┘
*/

class StreamEventBus {
  final _controller = StreamController<Map<String, dynamic>>.broadcast();

  Stream<Map<String, dynamic>> get stream => _controller.stream;

  void emit(String type, [dynamic data]) {
    _controller.add({'type': type, 'data': data});
  }

  Stream<Map<String, dynamic>> on(String type) {
    return stream.where((event) => event['type'] == type);
  }

  void dispose() {
    _controller.close();
  }
}

Future<void> lesson8EventBus() async {
  print('[레슨 8] 실전 패턴 — 이벤트 버스');

  final bus = StreamEventBus();
  final loginEvents = <String>[];
  final purchaseEvents = <int>[];

  // 타입별 구독
  final sub1 = bus.on('login').listen((e) {
    loginEvents.add(e['data'] as String);
    print('    [login] ${e['data']}님 로그인');
  });

  final sub2 = bus.on('purchase').listen((e) {
    purchaseEvents.add(e['data'] as int);
    print('    [purchase] ${e['data']}원 결제');
  });

  // 이벤트 발행
  bus.emit('login', '민수');
  bus.emit('purchase', 25000);
  bus.emit('login', '지우');
  bus.emit('purchase', 15000);
  bus.emit('logout', '민수');    // 아무도 구독 안 함

  await Future<void>.delayed(const Duration(milliseconds: 50));

  print('  로그인 이벤트: $loginEvents');
  print('  결제 이벤트: $purchaseEvents');

  await sub1.cancel();
  await sub2.cancel();
  bus.dispose();
  print('');
}


// =====================================================================
// main — 전체 레슨 실행
// =====================================================================
Future<void> main() async {
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('  Dart 16단계 : Streams (스트림)');
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('');

  lesson1WhatIsStream();
  await lesson2AsyncStar();
  await lesson3Transformations();
  await lesson4StreamController();
  await lesson5Broadcast();
  await lesson6SubscriptionManagement();
  await lesson7Aggregation();
  await lesson8EventBus();

  print('■■■ 16단계 완료! ■■■');
}
