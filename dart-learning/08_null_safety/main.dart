/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Dart 학습 08단계: Null Safety (널 안전성)
  ─ ? · ! · late · required · ?. · ?? · ??= · 타입 승격 ─

  ■ 실행: dart run main.dart
  ■ 컴파일: dart compile exe main.dart

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// =====================================================================
// 레슨 1 — Null Safety 란?
// =====================================================================
/*
★ Null Safety = "비어 있을 수 있는 값과 절대 비면 안 되는 값을
                 컴파일 시점에 구분하는 안전장치"

  비유: 우유 컵 vs 빈 컵
  ┌────────────────────────────────────────────────────────┐
  │  String name = '민수';   ← 우유가 든 컵 (항상 값 있음) │
  │  String? name = null;    ← 비어 있을 수도 있는 컵      │
  └────────────────────────────────────────────────────────┘

★ Dart 2.12 이전: 모든 변수에 null 가능 → 런타임 에러 빈번
  Dart 2.12 이후: 기본이 non-nullable → 컴파일러가 미리 검사

★ 핵심 기호
  ┌────────┬────────────────────────────────────────────┐
  │ 기호   │ 의미                                       │
  ├────────┼────────────────────────────────────────────┤
  │ ?      │ "이 타입은 null 일 수 있다"                 │
  │ !      │ "null 아님을 내가 보장한다" (위험!)         │
  │ ?.     │ "null 이면 뒤를 실행하지 마"                │
  │ ??     │ "null 이면 대신 이 값을 써"                 │
  │ ??=    │ "null 일 때만 대입해"                       │
  │ late   │ "나중에 반드시 초기화할게"                   │
  │ required│ "이 매개변수는 반드시 넣어야 해"            │
  └────────┴────────────────────────────────────────────┘
*/

void lesson1WhatIsNullSafety() {
  print('[레슨 1] Null Safety 란?');

  // ── non-nullable: 항상 값이 있어야 함 ──
  String greeting = '안녕하세요';   // null 불가
  int count = 0;                     // null 불가

  // String greeting = null;  ← 컴파일 에러!

  // ── nullable: null 일 수 있음 ──
  String? nickname;                  // null 로 시작
  int? optionalScore;               // null 로 시작

  print('  greeting: $greeting (non-nullable)');
  print('  nickname: $nickname (nullable → null 출력)');
  print('  count: $count');
  print('  optionalScore: $optionalScore');
  print('');
}


// =====================================================================
// 레슨 2 — Null-aware 연산자들 (?. ?? ??=)
// =====================================================================
/*
★ ?. (null-aware 접근 연산자)
  "null 이면 뒤의 속성/메서드를 호출하지 않고 null 반환"

  비유: 택배 배달
  - 집이 있으면(?.집) → 택배 배달
  - 집이 없으면(null) → 택배 반송 (에러 안 남)

★ ?? (null 합체 연산자)
  "왼쪽이 null 이면 오른쪽 값 사용"
  final name = nickname ?? '손님';

★ ??= (null-aware 대입 연산자)
  "현재 null 일 때만 대입"
  nickname ??= '기본닉네임';

  ┌──────────────────────────────────────────────────┐
  │  String? name;                                   │
  │                                                  │
  │  name?.length     → null (에러 안 남)            │
  │  name ?? '없음'   → '없음'                       │
  │  name ??= '기본'  → name 은 이제 '기본'          │
  │  name?.length     → 2                            │
  └──────────────────────────────────────────────────┘
*/

void lesson2NullAwareOperators() {
  print('[레슨 2] Null-aware 연산자들');

  String? nickname;

  // ?. — null 이면 null 반환, 에러 안 남
  print('  nickname?.length = ${nickname?.length}');   // null

  // ?? — null 이면 기본값 사용
  final displayName = nickname ?? '손님';
  print('  displayName = $displayName');               // 손님

  // ??= — null 일 때만 대입
  nickname ??= '코딩왕';
  print('  nickname = $nickname');                      // 코딩왕

  // 이제 null 이 아니므로 ??= 무시됨
  nickname ??= '새닉네임';
  print('  nickname(변경 시도 후) = $nickname');        // 여전히 코딩왕

  // ?. 체이닝
  String? text;
  final upper = text?.toUpperCase()?.trim();
  print('  text?.toUpperCase()?.trim() = $upper');      // null

  text = '  hello  ';
  final upper2 = text.toUpperCase().trim();
  print('  text 설정 후: $upper2');                     // HELLO
  print('');
}


// =====================================================================
// 레슨 3 — 타입 승격 (Type Promotion)
// =====================================================================
/*
★ 타입 승격 = "null 체크 후 자동으로 non-nullable 로 취급"

  ┌──────────────────────────────────────────────────┐
  │  String? name = getName();                       │
  │                                                  │
  │  if (name != null) {                             │
  │    // 여기서는 name 이 String (non-nullable)     │
  │    print(name.length);  ← ?. 안 써도 됨!         │
  │  }                                               │
  │                                                  │
  │  // 여기서는 다시 String?                        │
  └──────────────────────────────────────────────────┘

★ 승격이 되는 경우
  - if (x != null) { ... }
  - if (x is String) { ... }
  - x ?? return;
  - assert(x != null);

★ 승격이 안 되는 경우
  - 클래스의 멤버 변수 (다른 코드가 바꿀 수 있으므로)
  - 이 경우 로컬 변수에 복사 후 사용!
*/

String? findNickname(int userId) {
  final nicknames = {1: '코딩왕', 2: '다트고수', 3: null};
  return nicknames[userId];
}

void lesson3TypePromotion() {
  print('[레슨 3] 타입 승격');

  final nick1 = findNickname(1);    // '코딩왕'
  final nick2 = findNickname(3);    // null
  final nick3 = findNickname(99);   // null (키 없음)

  // ── if 문으로 승격 ──
  if (nick1 != null) {
    // nick1 은 여기서 String (non-nullable)
    print('  nick1 길이: ${nick1.length}');  // ?. 안 써도 됨!
  }

  // ── is 로 승격 ──
  final dynamic value = '동적 값';
  if (value is String) {
    print('  value 대문자: ${value.toUpperCase()}');
  }

  // ── null 이면 early return ──
  void printLength(String? text) {
    if (text == null) {
      print('  text 가 null 이라 길이를 구할 수 없습니다.');
      return;
    }
    // 여기서 text 는 String
    print('  text 길이: ${text.length}');
  }

  printLength(nick2);
  printLength('안녕하세요');
  print('');
}


// =====================================================================
// 레슨 4 — ! 연산자 (bang operator)
// =====================================================================
/*
★ ! = "이 값은 절대 null 아니야!" 라고 컴파일러에게 선언

  ┌──────────────────────────────────────────────────────┐
  │  String? name = '민수';                              │
  │  print(name!.length);   ← "null 아님을 내가 보장!"   │
  │                                                      │
  │  String? bad;                                        │
  │  print(bad!.length);    ← 런타임 에러! (거짓말!)      │
  └──────────────────────────────────────────────────────┘

★ ★ ★ 경고 ★ ★ ★
  ! 는 "나는 이게 null 아닌 걸 100% 안다" 일 때만 사용!
  확신이 없으면 ?. 또는 ?? 를 쓰세요.
  ! 남용 = null safety 를 끈 것과 같음!

★ 안전한 대안
  ┌────────────────────────────────────────────────────────┐
  │  위험: value!.method()                                │
  │  안전: value?.method() ?? '기본값'                    │
  │  안전: if (value != null) { value.method(); }         │
  └────────────────────────────────────────────────────────┘
*/

void lesson4BangOperator() {
  print('[레슨 4] ! 연산자 (bang operator)');

  // 안전한 ! 사용 — 직전에 값을 넣었으므로 확실함
  String? name = '민수';
  print('  name!.length = ${name!.length}');   // 2

  // 위험한 ! 사용 예시 (주석 처리 — 런타임 에러 발생!)
  // String? danger;
  // print(danger!.length);  ← Null check operator used on a null value

  // 더 안전한 패턴
  String? uncertain = getNameOrNull(false);
  // print(uncertain!.length);  ← 위험!
  print('  안전한 방법: ${uncertain?.length ?? '값 없음'}');
  print('');
}

String? getNameOrNull(bool exists) => exists ? '이름' : null;


// =====================================================================
// 레슨 5 — late 키워드
// =====================================================================
/*
★ late = "지금은 초기화 안 하지만, 처음 사용 전에 반드시 초기화할게"

  ┌──────────────────────────────────────────────────┐
  │  late String name;                               │
  │  // ... 나중에 ...                               │
  │  name = '민수';          ← 사용 전에 초기화!     │
  │  print(name.length);     ← OK                    │
  │                                                  │
  │  late String bad;                                │
  │  print(bad.length);      ← LateInitError! 에러! │
  └──────────────────────────────────────────────────┘

★ late 의 두 가지 용도

  1. 지연 초기화: 비용이 큰 연산을 처음 접근할 때만 실행
     late final data = expensiveComputation();

  2. non-nullable 인데 나중에 초기화해야 할 때
     late String injectedValue;

★ 주의
  - 초기화 전에 접근하면 LateInitializationError (런타임 에러)
  - 확신이 없으면 nullable(?) 을 쓰는 게 안전
*/

class HeavyResource {
  // ── late 지연 초기화: 처음 접근할 때 한 번만 계산 ──
  late final String data = _loadData();

  String _loadData() {
    print('  [heavy] 데이터 로딩 중... (비싼 연산)');
    return '로딩된 데이터';
  }
}

class UserProfile {
  // ── late non-nullable: 나중에 반드시 설정 ──
  late String name;
  late int age;

  void init(String n, int a) {
    name = n;
    age = a;
  }

  void display() {
    print('  이름: $name, 나이: ${age}살');
  }
}

void lesson5Late() {
  print('[레슨 5] late 키워드');

  // 지연 초기화 — data 에 접근할 때까지 _loadData 미실행
  final resource = HeavyResource();
  print('  아직 data 에 접근 안 함...');
  print('  data: ${resource.data}');   // 이때 _loadData 실행
  print('  data: ${resource.data}');   // 두 번째는 캐시됨 (재계산 안 함)

  // late non-nullable 사용
  final profile = UserProfile();
  profile.init('지우', 25);
  profile.display();

  // 초기화 안 하고 접근하면?
  // final bad = UserProfile();
  // bad.display();  ← LateInitializationError!
  print('');
}


// =====================================================================
// 레슨 6 — required 키워드
// =====================================================================
/*
★ required = "이름 있는 매개변수(named parameter) 중
              반드시 넣어야 하는 것을 표시"

  ┌──────────────────────────────────────────────────────┐
  │  void createUser({                                   │
  │    required String name,     ← 필수! 안 넣으면 에러  │
  │    required int age,         ← 필수!                 │
  │    String? nickname,         ← 선택 (null 가능)      │
  │    String role = '학생',     ← 선택 (기본값 있음)    │
  │  }) { ... }                                          │
  │                                                      │
  │  createUser(name: '민수', age: 20);  ← OK            │
  │  createUser(name: '민수');            ← 에러! age 필수│
  └──────────────────────────────────────────────────────┘

★ 왜 쓸까?
  - null safety 이전: 필수인데 깜빡 빼먹어도 런타임까지 모름
  - null safety 이후: required 덕분에 컴파일 시점에 잡아줌
*/

class UserConfig {
  final String name;
  final int age;
  final String? nickname;
  final String role;

  UserConfig({
    required this.name,       // 필수
    required this.age,        // 필수
    this.nickname,            // 선택 (nullable)
    this.role = '학생',       // 선택 (기본값)
  });

  void display() {
    print('  이름: $name / 나이: $age / 역할: $role');
    if (nickname != null) {
      print('  닉네임: $nickname');
    }
  }
}

void lesson6Required() {
  print('[레슨 6] required 키워드');

  final user1 = UserConfig(name: '민수', age: 20);
  final user2 = UserConfig(
    name: '지우',
    age: 25,
    nickname: '코딩고수',
    role: '선생님',
  );

  user1.display();
  user2.display();

  // 아래는 컴파일 에러 — name, age 가 required 이므로
  // final bad = UserConfig();  ← 에러!
  print('');
}


// =====================================================================
// 레슨 7 — 컬렉션의 Null Safety
// =====================================================================
/*
★ 컬렉션 + Null Safety 조합

  ┌───────────────────────┬──────────────────────────────────┐
  │ 타입                  │ 의미                              │
  ├───────────────────────┼──────────────────────────────────┤
  │ List<String>          │ null 불가 요소, 리스트도 non-null │
  │ List<String?>         │ 요소가 null 일 수 있음            │
  │ List<String>?         │ 리스트 자체가 null 일 수 있음     │
  │ List<String?>?        │ 둘 다 null 가능                  │
  └───────────────────────┴──────────────────────────────────┘

★ Map 의 [ ] 연산자는 항상 nullable 반환!
  Map<String, int> scores = {'A': 100};
  int? val = scores['B'];   ← null (키 없음)
  int val2 = scores['A']!;  ← 확실할 때만 !
*/

void lesson7CollectionNullSafety() {
  print('[레슨 7] 컬렉션의 Null Safety');

  // ── List<String?> : 요소가 null 가능 ──
  final List<String?> names = ['민수', null, '지우', null, '서연'];
  print('  원본: $names');

  // null 제거: whereType 으로 타입 필터링
  final nonNullNames = names.whereType<String>().toList();
  print('  null 제거: $nonNullNames');

  // null 제거: where + cast
  final filtered = names.where((n) => n != null).cast<String>().toList();
  print('  where로 제거: $filtered');

  // ── Map 조회는 항상 nullable ──
  final Map<String, int> scores = {'민수': 95, '지우': 82};

  final minsuScore = scores['민수'];   // int? (null 일 수 있음)
  final unknown = scores['서연'];       // null

  print('  민수 점수: $minsuScore');
  print('  서연 점수: ${unknown ?? '등록 안 됨'}');

  // ── List<String>? : 리스트 자체가 null 일 수 있음 ──
  List<int>? maybeList;
  print('  maybeList 길이: ${maybeList?.length ?? '리스트 없음'}');

  maybeList = [1, 2, 3];
  print('  maybeList 길이: ${maybeList.length}');  // 타입 승격!
  print('');
}


// =====================================================================
// 레슨 8 — 실전 패턴 모음
// =====================================================================
/*
★ Null Safety 실전에서 자주 쓰는 패턴

  1. 기본값 패턴:       value ?? defaultValue
  2. 조건부 호출:       object?.method()
  3. 안전한 캐스팅:     value as String?
  4. null-aware 할당:   variable ??= computeDefault()
  5. 리스트 안전 접근:  list.elementAtOrNull(index) (Dart 3)
*/

class ApiResponse {
  final String? data;
  final String? error;

  ApiResponse({this.data, this.error});

  // ── 패턴 1: 기본값으로 안전하게 처리 ──
  String get safeData => data ?? '데이터 없음';

  // ── 패턴 2: null 체크 + 변환 ──
  String get summary {
    if (error != null) return '에러: $error';
    if (data != null) return '성공: $data';
    return '응답 없음';
  }
}

// ── 패턴 3: cascade 와 null-aware 조합 ──
void configureIfNeeded(Map<String, String>? config) {
  // config 가 null 이면 아무것도 안 함
  config?['version'] ??= '1.0.0';
  config?['env'] ??= 'production';
}

void lesson8RealWorldPatterns() {
  print('[레슨 8] 실전 패턴 모음');

  // API 응답 처리
  final success = ApiResponse(data: '사용자 목록');
  final failure = ApiResponse(error: '서버 점검 중');
  final empty   = ApiResponse();

  print('  성공: ${success.summary}');
  print('  실패: ${failure.summary}');
  print('  빈값: ${empty.summary}');

  // null-aware cascade
  Map<String, String>? settings = {'app': 'dart-study'};
  configureIfNeeded(settings);
  print('  설정: $settings');

  configureIfNeeded(null);   // null 이면 아무 일도 안 일어남
  print('  null 설정: 에러 없이 통과!');
  print('');
}


// =====================================================================
// 레슨 9 — 흔한 실수와 해결법
// =====================================================================
/*
★ Null Safety 실수 TOP 5

  ┌───┬───────────────────────────┬──────────────────────────────┐
  │ # │ 실수                      │ 해결법                       │
  ├───┼───────────────────────────┼──────────────────────────────┤
  │ 1 │ ! 남용                    │ ?. 또는 ?? 사용              │
  │ 2 │ late 남발                 │ 정말 필요할 때만 사용         │
  │ 3 │ Map[key] 가 nullable 인  │ ?? 기본값 또는 containsKey   │
  │   │ 걸 모르고 ! 사용         │ 로 먼저 확인                 │
  │ 4 │ nullable 타입에 바로      │ 타입 승격 후 사용            │
  │   │ 메서드 호출              │ if (x != null) x.method()    │
  │ 5 │ dynamic 으로 null safety │ 가능한 한 구체적 타입 사용    │
  │   │ 우회                     │                              │
  └───┴───────────────────────────┴──────────────────────────────┘
*/

void lesson9CommonMistakes() {
  print('[레슨 9] 흔한 실수와 해결법');

  // ── 실수 1: ! 남용 ──
  print('  [실수 1] ! 남용');
  Map<String, int> scores = {'A': 100};
  // int bad = scores['B']!;  ← 런타임 에러!
  int safe = scores['B'] ?? 0;    // 안전!
  print('    안전한 접근: $safe');

  // ── 실수 2: 타입 승격 안 되는 경우 ──
  print('  [실수 2] 멤버 변수는 승격 안 됨');
  // 해결: 로컬 변수에 복사
  String? memberLike;
  final local = memberLike;
  if (local != null) {
    print('    승격됨: ${local.length}');
  } else {
    print('    null 이므로 건너뜀');
  }

  // ── 실수 3: dynamic 으로 우회 ──
  print('  [실수 3] dynamic 은 null safety 무력화');
  dynamic anything = null;
  // anything.length;  ← 런타임 에러! 컴파일러가 못 잡음
  if (anything is String) {
    print('    안전: ${anything.length}');
  } else {
    print('    dynamic 은 위험! 타입 확인 필수');
  }

  print('');
}


// =====================================================================
// main — 전체 레슨 실행
// =====================================================================
void main() {
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('  Dart 08단계 : Null Safety (널 안전성)');
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('');

  lesson1WhatIsNullSafety();
  lesson2NullAwareOperators();
  lesson3TypePromotion();
  lesson4BangOperator();
  lesson5Late();
  lesson6Required();
  lesson7CollectionNullSafety();
  lesson8RealWorldPatterns();
  lesson9CommonMistakes();

  print('■■■ 08단계 완료! ■■■');
}
