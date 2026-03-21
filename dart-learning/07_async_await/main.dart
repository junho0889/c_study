/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Dart 학습 07단계: async 와 await
  ─ Future · async/await · then · 에러 처리 · 병렬 실행 ─

  ■ 실행: dart run main.dart
  ■ 컴파일: dart compile exe main.dart

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// =====================================================================
// 레슨 1 — Future 가 뭘까?
// =====================================================================
/*
★ Future = "아직 완성되지 않았지만, 나중에 값이 들어올 약속"

  비유: 음식점 진동벨
  ┌──────────────────────────────────────────────────────┐
  │  1. 주문(함수 호출) → 진동벨(Future) 을 받음        │
  │  2. 기다리는 동안 다른 일 가능                       │
  │  3. 음식 완성(값 도착) → 벨이 울림                   │
  │  4. 음식 수령(await 로 값 꺼내기)                    │
  └──────────────────────────────────────────────────────┘

★ Future<T>
  - T = 나중에 받을 값의 타입
  - Future<String> → 문자열이 올 예정
  - Future<void>   → 값 없이 완료만 알려줌

★ 3가지 상태
  ┌────────────┬──────────────────────────────┐
  │ 상태       │ 의미                          │
  ├────────────┼──────────────────────────────┤
  │ uncompleted│ 아직 결과 없음 (진행 중)      │
  │ completed  │ 값이 도착 (성공)              │
  │ error      │ 에러 발생 (실패)              │
  └────────────┴──────────────────────────────┘
*/

Future<String> orderCoffee() async {
  print('  ☕ 커피 주문 접수...');
  await Future.delayed(const Duration(milliseconds: 200));
  return '아메리카노 완성!';
}

Future<String> orderCake() async {
  print('  🍰 케이크 주문 접수...');
  await Future.delayed(const Duration(milliseconds: 150));
  return '치즈케이크 완성!';
}

Future<void> lesson1Future() async {
  print('[레슨 1] Future 기본');

  // Future 를 직접 출력하면?
  final future = orderCoffee();
  print('  future 타입: ${future.runtimeType}');  // Future<String>

  // await 으로 결과를 기다림
  final result = await future;
  print('  결과: $result');
  print('');
}


// =====================================================================
// 레슨 2 — async / await 기본 패턴
// =====================================================================
/*
★ async = "이 함수 안에서 await 을 쓸 수 있다" 는 표시
  await = "이 Future 가 끝날 때까지 기다린다"

  ┌──────────────────────────────────────────────────────┐
  │  Future<반환타입> 함수이름() async {                  │
  │    final result = await 어떤Future();                │
  │    return result;                                    │
  │  }                                                   │
  └──────────────────────────────────────────────────────┘

★ 비유: 세탁기
  - async 함수 = 세탁기에 빨래를 넣은 것
  - await     = 세탁 완료될 때까지 기다리는 것
  - 기다리는 동안 Dart 이벤트 루프가 다른 일을 처리

★ 주의
  - await 은 async 함수 안에서만 사용 가능
  - async 함수의 반환 타입은 반드시 Future<T>
  - main() 도 async 로 만들 수 있음
*/

Future<String> boilWater() async {
  print('  🫖 물 끓이기 시작...');
  await Future.delayed(const Duration(milliseconds: 300));
  return '물 끓음!';
}

Future<String> toastBread() async {
  print('  🍞 빵 굽기 시작...');
  await Future.delayed(const Duration(milliseconds: 100));
  return '빵 구워짐!';
}

Future<String> fryEgg() async {
  print('  🍳 계란 프라이 시작...');
  await Future.delayed(const Duration(milliseconds: 150));
  return '계란 프라이 완성!';
}

Future<void> lesson2AsyncAwait() async {
  print('[레슨 2] async / await — 순차 실행');

  // 하나씩 순서대로 기다리기
  final water = await boilWater();     // 300ms
  final bread = await toastBread();    // 100ms
  final egg   = await fryEgg();        // 150ms
  // 총 약 550ms (직렬)

  print('  결과: $water / $bread / $egg');
  print('');
}


// =====================================================================
// 레슨 3 — Future.wait 으로 병렬 실행
// =====================================================================
/*
★ 순차 vs 병렬

  순차 (await 하나씩):
  ┌────┐ ┌────┐ ┌────┐
  │ A  │→│ B  │→│ C  │  총 = A + B + C
  └────┘ └────┘ └────┘

  병렬 (Future.wait):
  ┌────┐
  │ A  │
  ├────┤  총 = max(A, B, C)
  │ B  │
  ├────┤
  │ C  │
  └────┘

★ Future.wait([f1, f2, f3])
  - 여러 Future 를 동시에 시작
  - 모두 끝나면 결과를 리스트로 반환
  - 서로 의존하지 않는 작업에 적합!

★ 주의: 하나라도 에러 나면 전체가 에러!
*/

Future<void> lesson3Parallel() async {
  print('[레슨 3] Future.wait — 병렬 실행');

  final stopwatch = Stopwatch()..start();

  // 세 작업을 동시에 시작
  final results = await Future.wait([
    boilWater(),     // 300ms
    toastBread(),    // 100ms
    fryEgg(),        // 150ms
  ]);
  // 총 약 300ms (가장 긴 것만큼만 기다림)

  stopwatch.stop();
  print('  결과: $results');
  print('  걸린 시간: ${stopwatch.elapsedMilliseconds}ms (병렬이라 빠름!)');
  print('');
}


// =====================================================================
// 레슨 4 — then / catchError (콜백 스타일)
// =====================================================================
/*
★ then / catchError = await 이전의 전통적 방식

  ┌──────────────────────────────────────────────────┐
  │  orderCoffee()                                   │
  │    .then((result) => print(result))              │
  │    .catchError((e) => print('에러: $e'));         │
  └──────────────────────────────────────────────────┘

★ async/await vs then
  ┌──────────────┬───────────────────────────────────┐
  │ 방식         │ 특징                               │
  ├──────────────┼───────────────────────────────────┤
  │ async/await  │ 읽기 쉬움, try/catch 가능         │
  │ then/catch   │ 체이닝 가능, 콜백 지옥 위험       │
  └──────────────┴───────────────────────────────────┘

★ 권장: async/await 을 기본으로 쓰고,
  간단한 변환이 필요할 때만 then 사용
*/

Future<void> lesson4ThenStyle() async {
  print('[레슨 4] then / catchError 스타일');

  // then 체이닝
  await orderCoffee()
      .then((result) {
    print('  then 결과: $result');
  }).catchError((error) {
    print('  에러 발생: $error');
  });

  // whenComplete: 성공/실패 상관없이 항상 실행 (finally 같은 것)
  await orderCake()
      .then((result) => print('  then 결과: $result'))
      .whenComplete(() => print('  whenComplete: 작업 종료'));

  print('');
}


// =====================================================================
// 레슨 5 — 에러 처리 (try/catch with async)
// =====================================================================
/*
★ 비동기 에러 처리 = try/catch 와 async/await 조합

  ┌──────────────────────────────────────────────────┐
  │  try {                                           │
  │    final data = await fetchData();               │
  │  } on TimeoutException {                         │
  │    print('시간 초과!');                           │
  │  } catch (e, stackTrace) {                       │
  │    print('기타 에러: $e');                        │
  │  } finally {                                     │
  │    print('항상 실행');                            │
  │  }                                               │
  └──────────────────────────────────────────────────┘

★ 주의
  - await 없이 Future 에서 에러가 나면 try/catch 로 잡히지 않음!
  - 반드시 await 을 해야 에러가 현재 함수로 전파됨
*/

Future<String> fetchUserData(int userId) async {
  await Future.delayed(const Duration(milliseconds: 100));
  if (userId <= 0) {
    throw ArgumentError('유효하지 않은 사용자 ID: $userId');
  }
  if (userId > 100) {
    throw Exception('사용자를 찾을 수 없습니다: $userId');
  }
  return '사용자_$userId';
}

Future<void> lesson5ErrorHandling() async {
  print('[레슨 5] 비동기 에러 처리');

  // 정상 케이스
  try {
    final user = await fetchUserData(42);
    print('  성공: $user');
  } catch (e) {
    print('  에러: $e');
  }

  // 에러 케이스 1: ArgumentError
  try {
    await fetchUserData(-1);
  } on ArgumentError catch (e) {
    print('  ArgumentError 잡음: $e');
  }

  // 에러 케이스 2: 일반 Exception
  try {
    await fetchUserData(999);
  } on Exception catch (e) {
    print('  Exception 잡음: $e');
  } finally {
    print('  finally: 항상 실행됩니다.');
  }

  print('');
}


// =====================================================================
// 레슨 6 — Future.delayed, Future.value, Future.error
// =====================================================================
/*
★ Future 팩토리 메서드들

  ┌───────────────────┬────────────────────────────────────┐
  │ 메서드            │ 용도                                │
  ├───────────────────┼────────────────────────────────────┤
  │ Future.delayed()  │ 지연 후 값 반환 (타이머 대용)       │
  │ Future.value()    │ 이미 완성된 값을 Future 로 감싸기   │
  │ Future.error()    │ 이미 실패한 Future 만들기           │
  │ Future.microtask()│ 마이크로태스크 큐에 작업 등록        │
  └───────────────────┴────────────────────────────────────┘
*/

Future<void> lesson6FutureFactories() async {
  print('[레슨 6] Future 팩토리 메서드');

  // Future.value — 즉시 완성
  final instant = await Future.value('즉시 완성된 값');
  print('  Future.value: $instant');

  // Future.delayed — 지연 후 완성
  final delayed = await Future.delayed(
    const Duration(milliseconds: 50),
        () => '50ms 후 완성',
  );
  print('  Future.delayed: $delayed');

  // Future.error — 즉시 실패
  try {
    await Future<String>.error('의도적 에러');
  } catch (e) {
    print('  Future.error 잡음: $e');
  }

  print('');
}


// =====================================================================
// 레슨 7 — 실전 패턴: API 호출 시뮬레이션
// =====================================================================
/*
★ 실제 앱에서 async/await 이 쓰이는 대표적 상황

  ┌──────────────────────────────────────────────────┐
  │  사용자가 버튼 클릭                              │
  │  → API 호출 (네트워크 대기)                      │
  │  → 응답 파싱                                     │
  │  → 화면에 결과 표시                              │
  │  → 에러 발생 시 사용자에게 안내                  │
  └──────────────────────────────────────────────────┘
*/

// 가짜 API 응답 시뮬레이션
Future<Map<String, dynamic>> fetchProduct(int id) async {
  await Future.delayed(const Duration(milliseconds: 100));
  final products = {
    1: {'name': '다트 입문서', 'price': 25000},
    2: {'name': 'Flutter 실전', 'price': 35000},
    3: {'name': '클린 코드', 'price': 30000},
  };
  if (!products.containsKey(id)) {
    throw Exception('상품 #$id 를 찾을 수 없습니다');
  }
  return products[id]!;
}

Future<List<Map<String, dynamic>>> fetchMultipleProducts(
    List<int> ids) async {
  // 모든 상품을 병렬로 가져오기
  final futures = ids.map((id) => fetchProduct(id));
  return Future.wait(futures.toList());
}

Future<void> lesson7RealWorldPattern() async {
  print('[레슨 7] 실전 패턴 — API 호출 시뮬레이션');

  // 단일 상품 조회
  try {
    final product = await fetchProduct(1);
    print('  단일 조회: ${product['name']} (${product['price']}원)');
  } catch (e) {
    print('  에러: $e');
  }

  // 여러 상품 병렬 조회
  try {
    final products = await fetchMultipleProducts([1, 2, 3]);
    print('  병렬 조회 결과:');
    for (final p in products) {
      print('    - ${p['name']}: ${p['price']}원');
    }
  } catch (e) {
    print('  에러: $e');
  }

  // 존재하지 않는 상품
  try {
    await fetchProduct(99);
  } catch (e) {
    print('  예상된 에러: $e');
  }

  print('');
}


// =====================================================================
// 레슨 8 — Completer 와 타임아웃
// =====================================================================
/*
★ Completer = "Future 를 수동으로 완성시키는 도구"

  비유: 수동으로 여는 자물쇠
  - Future.delayed 는 자동 타이머
  - Completer 는 내가 원할 때 직접 열쇠를 돌림

★ timeout = "너무 오래 걸리면 포기"
  future.timeout(Duration(seconds: 5))
*/

import 'dart:async';

Future<String> slowOperation() async {
  await Future.delayed(const Duration(milliseconds: 500));
  return '느린 작업 완료';
}

Future<void> lesson8CompleterAndTimeout() async {
  print('[레슨 8] Completer 와 타임아웃');

  // ── Completer 사용 ──
  final completer = Completer<String>();

  // 비동기적으로 나중에 완성
  Future.delayed(const Duration(milliseconds: 100), () {
    completer.complete('Completer 로 완성!');
  });

  final result = await completer.future;
  print('  Completer 결과: $result');

  // ── 타임아웃 ──
  try {
    final quick = await slowOperation().timeout(
      const Duration(milliseconds: 100),  // 100ms 제한
    );
    print('  빠른 결과: $quick');
  } on TimeoutException {
    print('  ★ 타임아웃! 500ms 작업을 100ms 만에 포기');
  }

  print('');
}


// =====================================================================
// main — 전체 레슨 실행
// =====================================================================
Future<void> main() async {
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('  Dart 07단계 : async 와 await');
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('');

  await lesson1Future();
  await lesson2AsyncAwait();
  await lesson3Parallel();
  await lesson4ThenStyle();
  await lesson5ErrorHandling();
  await lesson6FutureFactories();
  await lesson7RealWorldPattern();
  await lesson8CompleterAndTimeout();

  print('■■■ 07단계 완료! ■■■');
}
