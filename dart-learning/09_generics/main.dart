/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Dart 학습 09단계: 제네릭 (Generics)
  ─ 제네릭 클래스 · 함수 · 타입 바운드 · 공변성 · 실전 패턴 ─

  ■ 실행: dart run main.dart
  ■ 컴파일: dart compile exe main.dart

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// =====================================================================
// 레슨 1 — 제네릭이 뭘까?
// =====================================================================
/*
★ 제네릭 = "상자 모양은 같고, 내용물 타입만 바꾸는 기술"

  비유: 서랍 정리함
  ┌──────────────────────────────────────────────────┐
  │  연필 서랍   → Box<연필>                          │
  │  과자 서랍   → Box<과자>                          │
  │  공책 서랍   → Box<공책>                          │
  │  서랍 모양은 같고, 안에 넣는 물건 종류만 다름!    │
  └──────────────────────────────────────────────────┘

★ 왜 쓸까?
  - 타입 안전성: 문자열 상자에 숫자를 넣으면 컴파일 에러
  - 코드 재사용: 같은 구조를 타입마다 반복해서 만들 필요 없음
  - 가독성: Box<String> 이면 "문자열 상자구나" 즉시 이해

★ 제네릭 없이 만든다면?
  class StringBox { String? item; ... }
  class IntBox    { int? item; ... }
  class DoubleBox { double? item; ... }
  → 구조가 똑같은데 타입만 다름 → 낭비!

★ 제네릭으로 만들면
  class Box<T> { T? item; ... }
  → Box<String>, Box<int>, Box<double> 자유자재!
*/

class Box<T> {
  T? _item;

  void put(T value) {
    _item = value;
    print('  📦 상자에 넣음: $value (타입: ${value.runtimeType})');
  }

  T? take() {
    final temp = _item;
    _item = null;
    return temp;
  }

  bool get isEmpty => _item == null;

  @override
  String toString() => 'Box<$T>(${_item ?? '비어있음'})';
}

void lesson1GenericBasics() {
  print('[레슨 1] 제네릭 기초');

  // 타입을 명시해서 상자 만들기
  final stringBox = Box<String>();
  stringBox.put('연필');
  print('  $stringBox');

  final intBox = Box<int>();
  intBox.put(42);
  print('  $intBox');

  // 타입 추론도 가능 (put 의 인자로부터)
  final autoBox = Box<double>();
  autoBox.put(3.14);
  print('  $autoBox');

  // 타입 안전성 — 아래는 컴파일 에러!
  // stringBox.put(123);  ← String 상자에 int 불가!
  // intBox.put('hello'); ← int 상자에 String 불가!
  print('');
}


// =====================================================================
// 레슨 2 — 제네릭 함수
// =====================================================================
/*
★ 함수에도 제네릭 적용 가능

  ┌──────────────────────────────────────────────────────┐
  │  T firstItem<T>(List<T> list) {                     │
  │    return list.first;                                │
  │  }                                                   │
  │                                                      │
  │  firstItem<int>([1, 2, 3]);      → 1                │
  │  firstItem<String>(['a', 'b']);   → 'a'              │
  │  firstItem([1, 2, 3]);           → 1 (타입 추론)     │
  └──────────────────────────────────────────────────────┘
*/

// ── 제네릭 함수: 첫 번째 요소 반환 ──
T firstItem<T>(List<T> items) {
  if (items.isEmpty) {
    throw StateError('리스트가 비어있습니다');
  }
  return items.first;
}

// ── 제네릭 함수: 두 값 교환한 쌍 반환 ──
(T, T) swap<T>(T a, T b) => (b, a);

// ── 제네릭 함수: 조건에 맞는 요소 필터링 ──
List<T> filterBy<T>(List<T> items, bool Function(T) predicate) {
  return items.where(predicate).toList();
}

void lesson2GenericFunctions() {
  print('[레슨 2] 제네릭 함수');

  // firstItem — 타입 추론
  final first = firstItem([10, 20, 30]);
  print('  첫 번째: $first');

  final firstStr = firstItem(['사과', '바나나', '포도']);
  print('  첫 번째: $firstStr');

  // swap
  final (a, b) = swap<int>(1, 2);
  print('  swap(1, 2) = ($a, $b)');

  final (x, y) = swap('안녕', '세상');
  print('  swap(안녕, 세상) = ($x, $y)');

  // filterBy
  final numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  final evens = filterBy(numbers, (n) => n % 2 == 0);
  print('  짝수만: $evens');

  final names = ['김민수', '이지우', '김서연', '박준호'];
  final kims = filterBy(names, (n) => n.startsWith('김'));
  print('  김씨만: $kims');
  print('');
}


// =====================================================================
// 레슨 3 — 타입 바운드 (extends 제약)
// =====================================================================
/*
★ 타입 바운드 = "T 가 될 수 있는 타입을 제한"

  ┌──────────────────────────────────────────────────┐
  │  class NumberBox<T extends num> {                │
  │    T value;                                      │
  │    double get doubled => value * 2.0;            │
  │    //                    ↑ num 의 * 연산자 사용  │
  │  }                                               │
  │                                                  │
  │  NumberBox<int>(42);       ← OK (int extends num)│
  │  NumberBox<double>(3.14);  ← OK                  │
  │  NumberBox<String>('hi');  ← 에러! String ≠ num  │
  └──────────────────────────────────────────────────┘

★ 왜 쓸까?
  - T 에 아무 타입이나 오면 메서드 호출이 불가능
  - extends 로 제한하면 해당 클래스의 메서드/속성 사용 가능
*/

class NumericBox<T extends num> {
  final T value;

  NumericBox(this.value);

  double get doubled => value * 2.0;
  bool get isPositive => value > 0;
  bool get isZero => value == 0;

  @override
  String toString() => 'NumericBox<$T>($value)';
}

// ── Comparable 바운드: 비교 가능한 타입만 허용 ──
T findMax<T extends Comparable<T>>(List<T> items) {
  if (items.isEmpty) throw StateError('빈 리스트');
  return items.reduce((a, b) => a.compareTo(b) >= 0 ? a : b);
}

T findMin<T extends Comparable<T>>(List<T> items) {
  if (items.isEmpty) throw StateError('빈 리스트');
  return items.reduce((a, b) => a.compareTo(b) <= 0 ? a : b);
}

void lesson3TypeBounds() {
  print('[레슨 3] 타입 바운드 (extends 제약)');

  final intBox = NumericBox<int>(42);
  print('  $intBox → 2배: ${intBox.doubled}');

  final doubleBox = NumericBox<double>(3.14);
  print('  $doubleBox → 양수?: ${doubleBox.isPositive}');

  // 컴파일 에러:
  // final stringBox = NumericBox<String>('hello');

  // Comparable 바운드
  final maxNum = findMax([3, 1, 4, 1, 5, 9, 2, 6]);
  print('  최댓값: $maxNum');

  final maxStr = findMax(['바나나', '사과', '포도', '감']);
  print('  사전순 최대: $maxStr');

  final minNum = findMin([3, 1, 4, 1, 5]);
  print('  최솟값: $minNum');
  print('');
}


// =====================================================================
// 레슨 4 — 제네릭 인터페이스와 다중 타입 파라미터
// =====================================================================
/*
★ 타입 파라미터를 여러 개 쓸 수 있음

  ┌──────────────────────────────────────────────────┐
  │  class Pair<A, B> {                              │
  │    final A first;                                │
  │    final B second;                               │
  │    Pair(this.first, this.second);                │
  │  }                                               │
  │                                                  │
  │  Pair<String, int>('민수', 95);                  │
  │  Pair<int, bool>(42, true);                      │
  └──────────────────────────────────────────────────┘

★ 관례적 타입 파라미터 이름
  ┌────┬─────────────────┐
  │ T  │ Type (일반적)   │
  │ E  │ Element (요소)  │
  │ K  │ Key (키)        │
  │ V  │ Value (값)      │
  │ R  │ Return (반환)   │
  │ S  │ State (상태)    │
  └────┴─────────────────┘
*/

class Pair<A, B> {
  final A first;
  final B second;

  Pair(this.first, this.second);

  @override
  String toString() => 'Pair($first, $second)';
}

// ── 제네릭 인터페이스 ──
abstract class Repository<T> {
  void add(T item);
  T? findById(int id);
  List<T> getAll();
  void remove(int id);
}

class Product {
  final int id;
  final String name;
  final int price;

  Product(this.id, this.name, this.price);

  @override
  String toString() => 'Product($id: $name, ${price}원)';
}

// Repository<Product> 구현
class ProductRepository implements Repository<Product> {
  final List<Product> _products = [];

  @override
  void add(Product item) => _products.add(item);

  @override
  Product? findById(int id) {
    for (final p in _products) {
      if (p.id == id) return p;
    }
    return null;
  }

  @override
  List<Product> getAll() => List.unmodifiable(_products);

  @override
  void remove(int id) => _products.removeWhere((p) => p.id == id);
}

void lesson4MultipleTypeParams() {
  print('[레슨 4] 다중 타입 파라미터와 제네릭 인터페이스');

  // Pair 사용
  final pair1 = Pair<String, int>('민수', 95);
  final pair2 = Pair<String, List<int>>('점수들', [90, 85, 78]);
  print('  $pair1');
  print('  $pair2');

  // Repository 패턴
  final repo = ProductRepository();
  repo.add(Product(1, '다트 입문서', 25000));
  repo.add(Product(2, 'Flutter 실전', 35000));
  repo.add(Product(3, '클린 코드', 30000));

  print('  전체 상품: ${repo.getAll()}');
  print('  ID 2 조회: ${repo.findById(2)}');

  repo.remove(1);
  print('  삭제 후: ${repo.getAll()}');
  print('');
}


// =====================================================================
// 레슨 5 — 제네릭과 컬렉션 심화
// =====================================================================
/*
★ Dart 컬렉션은 모두 제네릭!

  ┌──────────────────────────────────────────────────┐
  │  List<E>           → 리스트 (순서 있는 요소)     │
  │  Set<E>            → 집합 (중복 없는 요소)       │
  │  Map<K, V>         → 맵 (키-값 쌍)              │
  │  Iterable<E>       → 반복 가능한 것들            │
  │  Queue<E>          → 큐 (선입선출)               │
  │  Future<T>         → 미래 값                     │
  │  Stream<T>         → 연속된 미래 값              │
  └──────────────────────────────────────────────────┘

★ 타입 캐스팅 함수들
  - list.cast<TargetType>()      → 요소 타입 캐스팅
  - list.whereType<TargetType>() → 특정 타입만 필터링
*/

void lesson5CollectionGenerics() {
  print('[레슨 5] 컬렉션 제네릭 심화');

  // ── List 활용 ──
  final List<int> numbers = [1, 2, 3, 4, 5];
  final doubled = numbers.map((n) => n * 2).toList();  // List<int>
  print('  2배: $doubled');

  // ── Set 활용 ──
  final Set<String> fruits = {'사과', '바나나', '사과', '포도'};
  print('  과일 Set: $fruits');  // 중복 제거

  // ── Map 활용 ──
  final Map<String, List<int>> studentScores = {
    '민수': [90, 85, 92],
    '지우': [78, 82, 88],
  };

  studentScores.forEach((name, scores) {
    final avg = scores.reduce((a, b) => a + b) / scores.length;
    print('  $name 평균: ${avg.toStringAsFixed(1)}');
  });

  // ── whereType: 혼합 리스트에서 특정 타입만 ──
  final List<Object> mixed = [1, 'hello', 2, 'world', 3.14, true];
  final ints = mixed.whereType<int>().toList();
  final strings = mixed.whereType<String>().toList();
  print('  정수만: $ints');
  print('  문자열만: $strings');
  print('');
}


// =====================================================================
// 레슨 6 — 제네릭과 typedef
// =====================================================================
/*
★ typedef = "함수 타입에 이름을 붙이기"

  ┌──────────────────────────────────────────────────┐
  │  typedef Predicate<T> = bool Function(T item);   │
  │  typedef Mapper<T, R> = R Function(T item);      │
  │  typedef Callback = void Function();             │
  └──────────────────────────────────────────────────┘

★ 제네릭 typedef 를 쓰면 복잡한 함수 타입을 간결하게!
*/

typedef Predicate<T> = bool Function(T item);
typedef Mapper<T, R> = R Function(T item);
typedef Comparator<T> = int Function(T a, T b);

// typedef 를 활용한 제네릭 유틸리티 함수
List<R> mapList<T, R>(List<T> items, Mapper<T, R> mapper) {
  return items.map(mapper).toList();
}

List<T> filterList<T>(List<T> items, Predicate<T> test) {
  return items.where(test).toList();
}

void sortList<T>(List<T> items, Comparator<T> compare) {
  items.sort(compare);
}

void lesson6Typedef() {
  print('[레슨 6] 제네릭 typedef');

  final numbers = [5, 3, 8, 1, 9, 2, 7];

  // Mapper: int → String
  final labels = mapList<int, String>(numbers, (n) => '점수:$n');
  print('  변환: $labels');

  // Predicate: 5 이상만
  final big = filterList(numbers, (n) => n >= 5);
  print('  5이상: $big');

  // Comparator: 정렬
  final sorted = [...numbers];
  sortList(sorted, (a, b) => a.compareTo(b));
  print('  오름차순: $sorted');

  sortList(sorted, (a, b) => b.compareTo(a));
  print('  내림차순: $sorted');
  print('');
}


// =====================================================================
// 레슨 7 — 실전 패턴: Result 타입
// =====================================================================
/*
★ Result<T> = "성공 또는 실패를 타입으로 표현"

  비유: 시험 결과 봉투
  - 열어보면 성적표(성공) 또는 재시험 통지서(실패)
  - sealed class + 제네릭으로 깔끔하게 구현

  ┌──────────────────────────────────────────────────┐
  │  sealed class Result<T> { }                      │
  │                                                  │
  │  class Success<T> extends Result<T> {            │
  │    final T data;                                 │
  │  }                                               │
  │                                                  │
  │  class Failure<T> extends Result<T> {            │
  │    final String error;                           │
  │  }                                               │
  └──────────────────────────────────────────────────┘
*/

sealed class Result<T> {}

class Success<T> extends Result<T> {
  final T data;
  Success(this.data);
}

class Failure<T> extends Result<T> {
  final String error;
  Failure(this.error);
}

// Result 를 반환하는 함수
Result<int> divide(int a, int b) {
  if (b == 0) return Failure('0으로 나눌 수 없습니다');
  return Success(a ~/ b);
}

Result<String> findUser(int id) {
  final users = {1: '민수', 2: '지우', 3: '서연'};
  final name = users[id];
  if (name == null) return Failure('ID $id 사용자 없음');
  return Success(name);
}

// Result 를 switch 로 처리
void handleResult<T>(Result<T> result) {
  switch (result) {
    case Success<T>(:final data):
      print('  ✅ 성공: $data');
    case Failure<T>(:final error):
      print('  ❌ 실패: $error');
  }
}

void lesson7ResultPattern() {
  print('[레슨 7] 실전 패턴 — Result<T> 타입');

  handleResult(divide(10, 3));     // 성공: 3
  handleResult(divide(10, 0));     // 실패: 0으로 나눌 수 없음

  handleResult(findUser(1));       // 성공: 민수
  handleResult(findUser(99));      // 실패: ID 99 사용자 없음
  print('');
}


// =====================================================================
// 레슨 8 — 종합 예제: 제네릭 스택
// =====================================================================
/*
★ 스택 = "마지막에 넣은 것을 먼저 꺼내는 자료구조" (LIFO)

  비유: 접시 쌓기
  ┌─────┐
  │  C  │ ← 마지막에 넣은 것 (가장 먼저 꺼냄)
  ├─────┤
  │  B  │
  ├─────┤
  │  A  │ ← 처음에 넣은 것 (가장 나중에 꺼냄)
  └─────┘
*/

class Stack<T> {
  final List<T> _items = [];

  void push(T item) => _items.add(item);

  T pop() {
    if (_items.isEmpty) throw StateError('스택이 비어있습니다');
    return _items.removeLast();
  }

  T get peek {
    if (_items.isEmpty) throw StateError('스택이 비어있습니다');
    return _items.last;
  }

  bool get isEmpty => _items.isEmpty;
  bool get isNotEmpty => _items.isNotEmpty;
  int get size => _items.length;

  @override
  String toString() => 'Stack(${_items.reversed.join(' → ')})';
}

void lesson8GenericStack() {
  print('[레슨 8] 종합 예제 — 제네릭 스택');

  // ── 정수 스택 ──
  final intStack = Stack<int>();
  intStack.push(10);
  intStack.push(20);
  intStack.push(30);
  print('  $intStack');            // 30 → 20 → 10
  print('  peek: ${intStack.peek}');  // 30
  print('  pop:  ${intStack.pop()}'); // 30
  print('  pop 후: $intStack');       // 20 → 10

  // ── 문자열 스택: 브라우저 뒤로가기 시뮬레이션 ──
  final history = Stack<String>();
  history.push('google.com');
  history.push('dart.dev');
  history.push('flutter.dev');

  print('  현재 페이지: ${history.peek}');
  history.pop();  // flutter.dev 에서 뒤로
  print('  뒤로 가기: ${history.peek}');

  // ── 빈 스택에서 pop 시도 ──
  try {
    final empty = Stack<int>();
    empty.pop();
  } catch (e) {
    print('  빈 스택 pop: $e');
  }
  print('');
}


// =====================================================================
// main — 전체 레슨 실행
// =====================================================================
void main() {
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('  Dart 09단계 : 제네릭 (Generics)');
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('');

  lesson1GenericBasics();
  lesson2GenericFunctions();
  lesson3TypeBounds();
  lesson4MultipleTypeParams();
  lesson5CollectionGenerics();
  lesson6Typedef();
  lesson7ResultPattern();
  lesson8GenericStack();

  print('■■■ 09단계 완료! ■■■');
}
