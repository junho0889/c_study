/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Dart 학습 04단계: 컬렉션 (Collections)
  ─ List, Set, Map, 스프레드 연산자, 컬렉션 if/for ─

  ■ 실행 방법: dart run main.dart
  ■ Flutter에서 컬렉션은 아주 중요해요!
    화면에 여러 위젯을 나열할 때, 데이터 목록을 다룰 때
    항상 List, Map 등을 사용합니다!

  ■ 이번 단계에서 배울 것:
    - List<T>     : 순서 있는 목록 (중복 허용)
    - Set<T>      : 중복 없는 모음
    - Map<K, V>   : 키-값 쌍의 모음
    - 스프레드(...)  : 목록 펼치기
    - Collection if/for : Dart만의 특별한 기능!
    - where, map, reduce, fold : 함수형 프로그래밍

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

void main() {
  print('');
  print('┌────────────────────────────────────────┐');
  print('│  Dart 컬렉션 학습을 시작합니다!         │');
  print('└────────────────────────────────────────┘');
  print('');

  // ─────────────────────────────────────────────
  // 1단원: List<T> - 순서 있는 목록
  // ─────────────────────────────────────────────
  // List = 순서가 있는 항목들의 목록
  // 비유: 학교 출석부! 1번, 2번, 3번... 순서가 있고, 같은 이름도 있을 수 있어요
  // <T> = 제네릭 - 어떤 종류의 항목을 담을지 지정해요
  print('=== 1단원: List<T> ===');

  // 리스트 만들기
  List<String> fruits = ['사과', '바나나', '딸기', '포도', '수박'];
  List<int> numbers = [10, 20, 30, 40, 50];
  List<double> temperatures = [36.5, 37.0, 38.5, 36.8];

  print('과일 목록: $fruits');
  print('숫자 목록: $numbers');

  // 항목 접근 - 인덱스(번호)로 접근
  // 비유: 출석부의 번호! 1번이 아니라 0번부터 시작해요!
  //       인덱스 0 = 첫 번째 항목
  print('첫 번째 과일: ${fruits[0]}');   // 사과
  print('세 번째 과일: ${fruits[2]}');   // 딸기
  print('마지막 과일: ${fruits[fruits.length - 1]}');  // 수박
  print('마지막 과일(편리한 방법): ${fruits.last}');   // 수박
  print('첫 번째(편리한 방법): ${fruits.first}');      // 사과

  // 리스트 정보
  print('항목 수: ${fruits.length}');
  print('비어있나요? ${fruits.isEmpty}');
  print('비어있지 않나요? ${fruits.isNotEmpty}');

  // 항목 추가/수정/삭제
  print('');
  print('--- 리스트 수정 ---');
  fruits.add('멜론');           // 끝에 추가
  print('멜론 추가: $fruits');

  fruits.insert(1, '오렌지');   // 1번 위치에 삽입
  print('오렌지 삽입(1번): $fruits');

  fruits.remove('바나나');      // 값으로 삭제
  print('바나나 삭제: $fruits');

  fruits.removeAt(0);           // 인덱스로 삭제
  print('0번 삭제: $fruits');

  // 리스트 탐색
  print('');
  print('--- 리스트 탐색 ---');
  List<String> animals = ['고양이', '강아지', '토끼', '고양이', '햄스터'];
  print('동물 목록: $animals');
  print('고양이 있나요? ${animals.contains("고양이")}');
  print('고양이 첫 인덱스: ${animals.indexOf("고양이")}');
  print('고양이 마지막 인덱스: ${animals.lastIndexOf("고양이")}');

  // 리스트 변환
  print('');
  print('--- 리스트 변환 ---');
  List<int> nums = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5];
  print('원본: $nums');

  List<int> sortedNums = List.from(nums)..sort();  // 복사 후 정렬
  print('오름차순 정렬: $sortedNums');

  List<int> reversedNums = sortedNums.reversed.toList();
  print('내림차순: $reversedNums');

  // sublist - 일부만 가져오기
  List<int> sub = nums.sublist(2, 5);  // 인덱스 2~4
  print('부분 리스트 [2,5): $sub');

  // 리스트 합치기
  List<String> list1 = ['가', '나', '다'];
  List<String> list2 = ['라', '마', '바'];
  List<String> combined = [...list1, ...list2];  // 스프레드 연산자!
  print('합친 리스트: $combined');

  // ─────────────────────────────────────────────
  // 2단원: Set<T> - 중복 없는 모음
  // ─────────────────────────────────────────────
  // Set = 같은 항목이 중복으로 들어갈 수 없어요!
  // 비유: 학교 반에서 이름 목록! 같은 이름이 두 번 나올 수 없잖아요.
  //       아, 출석부와 달리 순서가 없어요!
  print('');
  print('=== 2단원: Set<T> ===');

  Set<String> colors = {'빨강', '파랑', '초록', '빨강', '노랑'};
  // '빨강'이 두 번 들어가도 한 번만 저장됩니다!
  print('색상 Set: $colors');
  print('항목 수: ${colors.length}');  // 4 (빨강 중복 제거)

  colors.add('보라');
  colors.add('빨강');  // 이미 있으니 추가 안 됨
  print('추가 후: $colors');

  // Set 활용: 중복 제거에 유용!
  List<int> withDups = [1, 2, 3, 2, 1, 4, 3, 5];
  Set<int> uniqueNums = withDups.toSet();   // List → Set = 중복 제거!
  List<int> noDups = uniqueNums.toList();   // Set → List = 다시 리스트로
  print('중복 있는 리스트: $withDups');
  print('중복 제거 후: $noDups');

  // Set 집합 연산
  Set<int> setA = {1, 2, 3, 4, 5};
  Set<int> setB = {4, 5, 6, 7, 8};
  print('A: $setA');
  print('B: $setB');
  print('합집합: ${setA.union(setB)}');          // A ∪ B
  print('교집합: ${setA.intersection(setB)}');   // A ∩ B
  print('차집합: ${setA.difference(setB)}');     // A - B

  // ─────────────────────────────────────────────
  // 3단원: Map<K, V> - 키-값 쌍의 모음
  // ─────────────────────────────────────────────
  // Map = 키(key)와 값(value)의 쌍으로 데이터 저장
  // 비유: 국어사전! "단어(키)"를 찾으면 "뜻(값)"이 나와요.
  //       또는 전화번호부: "이름(키)" → "전화번호(값)"
  print('');
  print('=== 3단원: Map<K, V> ===');

  // Map 만들기
  Map<String, int> ages = {
    '김철수': 12,
    '이영희': 11,
    '박민수': 13,
    '최지아': 12,
  };
  print('나이 정보: $ages');

  // 값 접근
  print('김철수 나이: ${ages["김철수"]}');
  print('이영희 나이: ${ages["이영희"]}');

  // 없는 키 접근 - null 반환 (안전해요!)
  print('홍길동 나이: ${ages["홍길동"]}');  // null

  // 기본값으로 접근
  int unknownAge = ages['홍길동'] ?? 0;
  print('홍길동 나이(기본값): $unknownAge');

  // 항목 추가/수정/삭제
  print('');
  print('--- Map 수정 ---');
  ages['홍길동'] = 14;       // 추가
  print('홍길동 추가: $ages');

  ages['김철수'] = 13;       // 수정 (이미 있는 키는 값이 바뀜)
  print('김철수 나이 수정: $ages');

  ages.remove('박민수');     // 삭제
  print('박민수 삭제: $ages');

  // Map 정보
  print('항목 수: ${ages.length}');
  print('키 목록: ${ages.keys.toList()}');
  print('값 목록: ${ages.values.toList()}');
  print('항목들: ${ages.entries.map((e) => "${e.key}:${e.value}").toList()}');

  // Map 탐색
  print('');
  print('--- Map 탐색 ---');
  ages.forEach((name, age) {
    String suffix = age >= 13 ? '(중학생이 될 나이!)' : '';
    print('  $name: $age 살 $suffix');
  });

  // Map 활용 예시: 학생 성적 관리
  print('');
  print('--- 성적 관리 ---');
  Map<String, Map<String, int>> studentGrades = {
    '김철수': {'국어': 85, '수학': 92, '영어': 78},
    '이영희': {'국어': 95, '수학': 88, '영어': 93},
    '박민수': {'국어': 72, '수학': 85, '영어': 80},
  };

  studentGrades.forEach((student, grades) {
    int total = grades.values.fold(0, (sum, g) => sum + g);
    double avg = total / grades.length;
    print('  $student: 평균 ${avg.toStringAsFixed(1)}점');
  });

  // ─────────────────────────────────────────────
  // 4단원: 스프레드 연산자 (...) - 목록 펼치기
  // ─────────────────────────────────────────────
  // ... = 스프레드(spread) 연산자. 목록을 "펼쳐서" 다른 목록에 합쳐요.
  // 비유: 카드 덱을 펼쳐서 다른 덱에 합치기!
  print('');
  print('=== 4단원: 스프레드 연산자 ===');

  List<String> breakfast = ['밥', '된장국', '김치'];
  List<String> lunch = ['피자', '콜라', '샐러드'];
  List<String> dinner = ['삼겹살', '쌈채소', '된장찌개'];

  // 모든 식사를 하나의 리스트로 합치기
  List<String> allMeals = [...breakfast, ...lunch, ...dinner];
  print('오늘의 모든 식사: $allMeals');

  // null-aware 스프레드 (?...) - null이면 무시
  List<String>? maybeList;
  List<String> safeList = ['기본값', ...?maybeList, '끝'];  // maybeList가 null이면 무시
  print('안전한 스프레드: $safeList');

  maybeList = ['추가1', '추가2'];
  List<String> safeList2 = ['기본값', ...?maybeList, '끝'];
  print('null 아닐 때: $safeList2');

  // Flutter에서 스프레드 사용 예시:
  // Column(children: [
  //   headerWidget,
  //   ...itemWidgets,  // 여러 위젯을 한 번에 추가!
  //   footerWidget,
  // ])

  // ─────────────────────────────────────────────
  // 5단원: Collection if와 Collection for (Dart 특별 기능!)
  // ─────────────────────────────────────────────
  // 컬렉션 안에서 if, for 를 사용할 수 있어요!
  // 이건 Dart만의 특별한 기능이에요!
  // Flutter에서 조건에 따라 위젯을 추가/제거할 때 엄청 유용해요!
  print('');
  print('=== 5단원: Collection if와 for (Dart 특별 기능!) ===');

  bool isLoggedIn = true;
  bool isAdmin = false;

  // Collection if - 조건에 따라 항목 포함/제외
  // 비유: "로그인한 사용자에게만 이 메뉴 보여주기!"
  List<String> menuItems = [
    '홈',
    '검색',
    if (isLoggedIn) '내 프로필',     // 로그인 했으면 포함
    if (isLoggedIn) '설정',
    if (isAdmin) '관리자 패널',       // 관리자이면 포함
    '도움말',
  ];
  print('메뉴 항목: $menuItems');

  // 로그인 안 했을 때
  bool notLoggedIn = false;
  List<String> guestMenu = [
    '홈',
    '검색',
    if (notLoggedIn) '내 프로필' else '로그인',  // else도 됩니다!
    '도움말',
  ];
  print('게스트 메뉴: $guestMenu');

  // Collection for - 반복으로 항목 추가
  // 비유: "학생 10명의 이름표를 자동으로 만들기!"
  List<String> studentNames = ['김민준', '이서연', '박도윤', '최하은'];

  List<String> greetings = [
    for (String s in studentNames) '안녕하세요, $s 님!',
  ];
  print('인사 목록:');
  greetings.forEach((g) => print('  $g'));

  // 숫자 제곱 리스트 만들기
  List<int> squares = [
    for (int i = 1; i <= 5; i++) i * i,
  ];
  print('1~5 제곱: $squares');

  // if + for 같이 사용
  List<int> allNums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  List<String> evenLabels = [
    for (int n in allNums)
      if (n % 2 == 0) '짝수: $n',  // 짝수만 포함!
  ];
  print('짝수 레이블: $evenLabels');

  // Flutter에서 Collection if 사용 예시:
  // Column(children: [
  //   Text('제목'),
  //   if (isLoading) CircularProgressIndicator(),  // 로딩 중에만 표시!
  //   if (!isLoading) ...dataWidgets,              // 데이터 있으면 표시!
  // ])

  // ─────────────────────────────────────────────
  // 6단원: 함수형 컬렉션 처리
  // ─────────────────────────────────────────────
  // where, map, reduce, fold, any, every
  // 비유: 공장 조립 라인! 재료가 각 공정을 거치며 변환돼요.
  print('');
  print('=== 6단원: 함수형 컬렉션 처리 ===');

  List<int> data = [3, 7, 2, 9, 4, 6, 1, 8, 5, 10];
  print('원본 데이터: $data');

  // where - 조건에 맞는 것만 필터링
  // 비유: 체(sieve)로 걸러내기! 큰 것만, 작은 것만 골라내요.
  var bigNums = data.where((n) => n > 5);
  print('5 초과: ${bigNums.toList()}');

  // map - 각 항목을 변환
  // 비유: 사과를 주스로 만드는 기계! 각 항목이 변환돼요.
  var doubled = data.map((n) => n * 2);
  print('두 배: ${doubled.toList()}');

  // 문자열로 변환
  var asStrings = data.map((n) => '[$n]');
  print('문자열로: ${asStrings.toList()}');

  // reduce - 모든 항목을 하나의 값으로 줄이기
  // 비유: 모든 과일을 하나의 큰 스무디로 만들기!
  int sum = data.reduce((acc, n) => acc + n);
  print('합계 (reduce): $sum');

  int maxVal = data.reduce((a, b) => a > b ? a : b);
  print('최댓값: $maxVal');

  // fold - 초기값과 함께 reduce
  // 비유: 빈 통에 하나씩 넣어 모으기! 시작 값을 정할 수 있어요.
  int sumFold = data.fold(0, (acc, n) => acc + n);
  print('합계 (fold): $sumFold');

  // 곱하기도 됩니다
  int product = [1, 2, 3, 4, 5].fold(1, (acc, n) => acc * n);
  print('1×2×3×4×5 = $product');

  // any - 하나라도 조건 만족하면 true
  bool hasLarge = data.any((n) => n > 9);
  print('10 이상 있나요? $hasLarge');

  // every - 모두 조건 만족하면 true
  bool allPositive = data.every((n) => n > 0);
  print('전부 양수? $allPositive');

  // 메서드 체이닝! (연결해서 쓰기)
  // 비유: 공장 라인처럼 순서대로 처리!
  var result = data
      .where((n) => n % 2 == 0)     // 짝수만 필터링
      .map((n) => n * n)            // 제곱으로 변환
      .toList()
    ..sort();                       // 정렬 (cascade notation!)
  print('짝수의 제곱 (정렬): $result');

  // ─────────────────────────────────────────────
  // 7단원: 정렬 (Sorting)
  // ─────────────────────────────────────────────
  print('');
  print('=== 7단원: 정렬 ===');

  // 숫자 정렬
  List<int> toSort = [5, 2, 8, 1, 9, 3, 7, 4, 6];
  toSort.sort();    // 오름차순 (기본)
  print('오름차순: $toSort');

  toSort.sort((a, b) => b.compareTo(a));  // 내림차순
  print('내림차순: $toSort');

  // 문자열 정렬
  List<String> names = ['박민수', '김철수', '이영희', '최지아', '강동원'];
  names.sort();    // 알파벳 순 (한글은 가나다 순)
  print('이름 정렬: $names');

  // 길이 순 정렬
  List<String> words = ['Dart', 'Flutter', 'iOS', 'Android', 'Go'];
  words.sort((a, b) => a.length.compareTo(b.length));  // 짧은 순서
  print('길이 순: $words');

  // 복잡한 객체 정렬 (Map으로 흉내내기)
  List<Map<String, dynamic>> students = [
    {'이름': '김철수', '점수': 85},
    {'이름': '이영희', '점수': 92},
    {'이름': '박민수', '점수': 78},
    {'이름': '최지아', '점수': 96},
  ];
  students.sort((a, b) => (b['점수'] as int).compareTo(a['점수'] as int));
  print('점수 내림차순:');
  students.forEach((s) => print('  ${s["이름"]}: ${s["점수"]}점'));

  // ─────────────────────────────────────────────
  // 마무리: Flutter와의 연결
  // ─────────────────────────────────────────────
  print('');
  print('┌────────────────────────────────────────────────────┐');
  print('│  Flutter와의 연결                                  │');
  print('│                                                    │');
  print('│  List: Flutter에서 위젯 목록 만들기               │');
  print('│  children: [Widget1(), Widget2(), ...]            │');
  print('│                                                    │');
  print('│  Map: 설정값, API 응답 데이터 처리                │');
  print('│  Map<String, dynamic> jsonData = {...}            │');
  print('│                                                    │');
  print('│  Collection if (Flutter에서 자주 씀!):           │');
  print("│  children: [                                      │");
  print("│    if (isLoading) CircularProgressIndicator(),   │");
  print("│    if (!isLoading) ...itemWidgets,               │");
  print("│  ]                                               │");
  print('│                                                    │');
  print('│  ListView.builder + List로 스크롤 목록 만들기!   │');
  print('└────────────────────────────────────────────────────┘');
  print('');
  print('04단계 완료! 다음은 05_oop_basics 입니다!');
}
