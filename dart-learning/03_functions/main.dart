/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Dart 학습 03단계: 함수 (Functions)
  ─ 선언, 매개변수, 화살표 함수, 고차 함수, 재귀 ─

  ■ 실행 방법: dart run main.dart
  ■ Flutter에서 함수는 정말 중요해요!
    특히 "Named Parameters(이름 붙은 매개변수)"는
    Flutter 위젯을 만들 때 핵심적으로 사용됩니다!
    예: Text('안녕', style: TextStyle(), textAlign: TextAlign.center)
        여기서 style:, textAlign: 이 Named Parameters예요!

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// ─────────────────────────────────────────────
// 전역 함수 (Global Functions) - main() 밖에 선언된 함수
// ─────────────────────────────────────────────

// 1. 기본 함수 선언
// 반환타입 함수이름(매개변수) { 코드 }
// 비유: 레시피! 재료(매개변수)를 받아서 요리(처리)하고 결과(반환값)를 줘요.

// 두 숫자를 더하는 함수
int add(int a, int b) {
  return a + b;   // return = 결과를 돌려줘요
}

// 인사하는 함수 (반환값 없음 → void)
void greet(String name) {
  print('안녕하세요, $name 님!');
}

// 원의 넓이 계산 (double 반환)
double circleArea(double radius) {
  return 3.14159 * radius * radius;
}

// ─────────────────────────────────────────────
// 2. Optional Positional Parameters (선택적 위치 매개변수)
// [] 대괄호로 감싸면 선택사항이 돼요!
// 비유: 피자 주문 - 크기는 필수, 토핑은 선택사항!
// ─────────────────────────────────────────────
String orderPizza(String size, [String? topping, String? crust]) {
  String order = '$size 사이즈 피자';
  if (topping != null) order += ', $topping 토핑';
  if (crust != null) order += ', $crust 크러스트';
  return order;
}

// 기본값이 있는 선택적 매개변수
String greetWithTitle(String name, [String title = '님']) {
  // title을 안 넣으면 자동으로 '님'이 사용돼요!
  return '안녕하세요, $name $title!';
}

// ─────────────────────────────────────────────
// 3. Named Parameters (이름 붙은 매개변수) - Flutter의 핵심!
// {} 중괄호로 감싸면 이름으로 값을 전달해요!
// 비유: 편지 봉투에 받는사람: 홍길동, 주소: 서울시... 처럼
//       이름표를 붙여서 값을 넣는 것!
// ─────────────────────────────────────────────
// required = 반드시 전달해야 하는 named parameter
String createProfile({
  required String name,      // required → 필수!
  required int age,          // required → 필수!
  String school = '미정',    // 기본값 있음 → 선택사항
  String? hobby,             // nullable → 선택사항
}) {
  String profile = '이름: $name, 나이: $age';
  profile += ', 학교: $school';
  if (hobby != null) profile += ', 취미: $hobby';
  return profile;
}

// Flutter 스타일 Named Parameter 예시 (Text 위젯 흉내내기)
void showText({
  required String text,
  double fontSize = 14.0,
  String color = '검정',
  bool bold = false,
}) {
  String style = '';
  if (bold) style += '굵게 ';
  print('[$color, ${fontSize}pt${style.isNotEmpty ? ", $style" : ""}] $text');
}

// ─────────────────────────────────────────────
// 4. 화살표 함수 (Arrow Functions) - => 기호 사용
// 한 줄짜리 함수를 짧게 쓰는 방법!
// 비유: 긴 말을 짧게 줄이는 것! "안녕하세요" → "안녕"
// ─────────────────────────────────────────────
int multiply(int a, int b) => a * b;  // return 없이 => 뒤 결과가 반환돼요
String sayHi(String name) => '안녕! $name!';
bool isEven(int n) => n % 2 == 0;    // 짝수이면 true
double square(double x) => x * x;    // 제곱 계산

// ─────────────────────────────────────────────
// 5. 재귀 함수 (Recursive Functions)
// 함수가 자기 자신을 호출하는 것!
// 비유: 거울 속의 거울. 계속 반복되다가 언젠가 멈춰요.
// ─────────────────────────────────────────────
// 팩토리얼: 5! = 5×4×3×2×1 = 120
int factorial(int n) {
  if (n <= 1) return 1;      // 멈추는 조건! (이게 없으면 무한 반복!)
  return n * factorial(n - 1); // 자기 자신을 호출!
}

// 피보나치 수열: 1, 1, 2, 3, 5, 8, 13, 21...
// 앞의 두 숫자를 더한 것이 다음 숫자!
int fibonacci(int n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

// ─────────────────────────────────────────────
// 6. 고차 함수 (Higher-Order Functions)
// 함수를 매개변수로 받거나, 함수를 반환하는 함수
// 비유: 선생님이 학생들에게 "이 방법으로 문제 풀어봐" 라고
//       방법(함수)을 주는 것!
// ─────────────────────────────────────────────
// 함수를 매개변수로 받는 함수
int applyOperation(int a, int b, int Function(int, int) operation) {
  // int Function(int, int) = "정수 두 개를 받아 정수를 반환하는 함수" 타입
  return operation(a, b);
}

// 함수를 반환하는 함수 (클로저)
// 비유: 팩토리(공장)처럼 함수를 만들어내는 함수!
Function makeMultiplier(int factor) {
  // factor를 기억하는 함수를 반환해요
  return (int n) => n * factor;
}


// ─────────────────────────────────────────────
// 메인 함수
// ─────────────────────────────────────────────
void main() {
  print('');
  print('┌────────────────────────────────────────┐');
  print('│  Dart 함수 학습을 시작합니다!           │');
  print('└────────────────────────────────────────┘');
  print('');

  // ─────────────────────────────────────────────
  // 1단원: 기본 함수 사용
  // ─────────────────────────────────────────────
  print('=== 1단원: 기본 함수 ===');

  int result = add(5, 3);
  print('5 + 3 = $result');

  greet('홍길동');

  double area = circleArea(5.0);
  print('반지름 5인 원의 넓이: ${area.toStringAsFixed(2)}');

  // ─────────────────────────────────────────────
  // 2단원: 선택적 위치 매개변수
  // ─────────────────────────────────────────────
  print('');
  print('=== 2단원: 선택적 위치 매개변수 ===');

  print(orderPizza('라지'));                          // 크기만
  print(orderPizza('미디엄', '불고기'));              // 크기 + 토핑
  print(orderPizza('스몰', '치즈', '씬 크러스트'));  // 전부

  print(greetWithTitle('김민수'));          // 기본값 '님' 사용
  print(greetWithTitle('박선생', '선생님')); // '선생님' 전달

  // ─────────────────────────────────────────────
  // 3단원: Named Parameters (Flutter의 핵심!)
  // ─────────────────────────────────────────────
  print('');
  print('=== 3단원: Named Parameters ===');
  print('※ Flutter 위젯의 매개변수와 동일한 방식입니다!');
  print('');

  // 이름을 붙여서 어떤 순서로든 전달 가능!
  String profile1 = createProfile(name: '김다은', age: 12);
  print(profile1);

  String profile2 = createProfile(
    name: '이준호',
    age: 11,
    school: '행복초등학교',
    hobby: '축구',
  );
  print(profile2);

  // age: 를 먼저 써도 됩니다! (순서 무관)
  String profile3 = createProfile(
    age: 13,
    name: '박지수',
    hobby: '독서',
    school: '미래초등학교',
  );
  print(profile3);

  print('');
  print('--- Flutter 스타일 텍스트 출력 ---');
  showText(text: '안녕하세요');                          // 기본값 사용
  showText(text: '제목입니다', fontSize: 24.0, bold: true);
  showText(text: '경고!', color: '빨강', fontSize: 16.0, bold: true);

  // Flutter 실제 사용 예시 설명:
  print('');
  print('※ Flutter에서 이런 형태로 사용돼요:');
  print('  Text(');
  print("    '안녕하세요',");
  print('    style: TextStyle(fontSize: 24.0),');
  print('    textAlign: TextAlign.center,');
  print('  )');
  print('  → style:, textAlign: 이 Named Parameters!');

  // ─────────────────────────────────────────────
  // 4단원: 화살표 함수
  // ─────────────────────────────────────────────
  print('');
  print('=== 4단원: 화살표 함수 ===');

  print('3 × 4 = ${multiply(3, 4)}');
  print(sayHi('Flutter'));
  print('7은 짝수? ${isEven(7)}');
  print('5.0의 제곱: ${square(5.0)}');

  // ─────────────────────────────────────────────
  // 5단원: 익명 함수 (Anonymous Functions)
  // ─────────────────────────────────────────────
  // 이름 없는 함수! 한 번만 사용하거나 변수에 담을 때 씁니다
  // 비유: 일회용 메모지! 이름 없이 바로 쓰고 버려요
  print('');
  print('=== 5단원: 익명 함수 ===');

  // 함수를 변수에 저장
  var double_ = (int n) => n * 2;  // 이름 없는 함수를 변수에 저장
  print('10의 두 배: ${double_(10)}');

  // 즉시 실행
  var result2 = ((int a, int b) => a + b)(10, 20);  // 만들자마자 실행!
  print('즉시 실행 결과: $result2');

  // 리스트에서 익명 함수 사용
  List<int> numbers = [1, 2, 3, 4, 5];

  // map - 각 항목을 변환
  var doubled = numbers.map((n) => n * 2);
  print('두 배: $doubled');

  // where - 조건에 맞는 것만 필터링
  var evens = numbers.where((n) => n % 2 == 0);
  print('짝수만: $evens');

  // forEach - 각 항목에 실행
  print('각 숫자에 "!" 붙이기:');
  numbers.forEach((n) => print('  $n!'));

  // ─────────────────────────────────────────────
  // 6단원: 고차 함수
  // ─────────────────────────────────────────────
  print('');
  print('=== 6단원: 고차 함수 ===');

  // 함수를 인수로 전달
  int sumResult = applyOperation(10, 5, add);     // add 함수 전달
  int mulResult = applyOperation(10, 5, multiply); // multiply 함수 전달
  print('더하기: $sumResult');    // 15
  print('곱하기: $mulResult');    // 50

  // 람다(익명 함수)도 전달 가능
  int subResult = applyOperation(10, 5, (a, b) => a - b);
  print('빼기: $subResult');     // 5

  // 함수를 반환하는 함수 (클로저)
  // 비유: "3을 곱하는 기계" 를 만들고, 그 기계를 사용해요
  var triple = makeMultiplier(3);    // 3을 곱하는 함수 반환
  var quintuple = makeMultiplier(5); // 5를 곱하는 함수 반환

  print('triple(4) = ${triple(4)}');    // 12
  print('quintuple(4) = ${quintuple(4)}'); // 20

  // ─────────────────────────────────────────────
  // 7단원: 재귀 함수
  // ─────────────────────────────────────────────
  print('');
  print('=== 7단원: 재귀 함수 ===');

  // 팩토리얼
  print('--- 팩토리얼 ---');
  for (int i = 1; i <= 7; i++) {
    print('  $i! = ${factorial(i)}');
  }

  // 피보나치
  print('--- 피보나치 수열 (첫 10개) ---');
  String fibStr = '';
  for (int i = 0; i < 10; i++) {
    fibStr += '${fibonacci(i)}';
    if (i < 9) fibStr += ', ';
  }
  print('  $fibStr');

  // ─────────────────────────────────────────────
  // 8단원: 클로저 (Closure)
  // ─────────────────────────────────────────────
  // 클로저 = 자신이 만들어진 환경의 변수를 기억하는 함수
  // 비유: 엄마가 레시피를 주면서 "우리 집 양념장 써!" 라고 했을 때
  //       그 요리사(함수)는 "우리 집 양념장"(외부 변수)을 기억해요!
  print('');
  print('=== 8단원: 클로저 ===');

  // 카운터 만들기
  Function makeCounter() {
    int count = 0;  // 이 변수를 기억해요!
    return () {
      count++;
      return count;
    };
  }

  var counter1 = makeCounter();
  var counter2 = makeCounter();   // 별개의 카운터!

  print('counter1: ${counter1()}');  // 1
  print('counter1: ${counter1()}');  // 2
  print('counter1: ${counter1()}');  // 3
  print('counter2: ${counter2()}');  // 1 (별개!)
  print('counter2: ${counter2()}');  // 2

  // ─────────────────────────────────────────────
  // 9단원: 유용한 내장 함수들
  // ─────────────────────────────────────────────
  print('');
  print('=== 9단원: 유용한 내장 함수들 ===');

  // 수학 관련
  print('최대값: ${[3, 1, 4, 1, 5, 9, 2, 6].reduce((a, b) => a > b ? a : b)}');
  print('최소값: ${[3, 1, 4, 1, 5, 9, 2, 6].reduce((a, b) => a < b ? a : b)}');
  print('합계: ${[1, 2, 3, 4, 5].reduce((a, b) => a + b)}');
  print('fold로 합계: ${[1, 2, 3, 4, 5].fold(0, (sum, n) => sum + n)}');

  // 문자열 관련
  List<String> words = ['Dart', 'is', 'awesome', 'for', 'Flutter'];
  print('단어 연결: ${words.join(' ')}');

  // any/every
  List<int> scores = [85, 92, 78, 95, 60];
  print('90점 이상 있나요? ${scores.any((s) => s >= 90)}');
  print('전원 60점 이상? ${scores.every((s) => s >= 60)}');

  // ─────────────────────────────────────────────
  // 마무리: Flutter와의 연결
  // ─────────────────────────────────────────────
  print('');
  print('┌────────────────────────────────────────────────────┐');
  print('│  Flutter와의 연결                                  │');
  print('│                                                    │');
  print('│  Named Parameters는 Flutter의 핵심이에요!         │');
  print('│                                                    │');
  print('│  // Flutter 코드 예시                             │');
  print('│  ElevatedButton(                                  │');
  print("│    onPressed: () => print('클릭!'),  // 익명함수  │");
  print('│    child: Text(\'버튼\'),              // named    │');
  print('│    style: ButtonStyle(...),         // named    │');
  print('│  )                                               │');
  print('│                                                    │');
  print('│  onPressed: () => ... 가 바로 익명 함수예요!      │');
  print('│  map(), where(), forEach() 도 Flutter에서        │');
  print('│  위젯 리스트 만들 때 많이 사용해요!               │');
  print('└────────────────────────────────────────────────────┘');
  print('');
  print('03단계 완료! 다음은 04_collections 입니다!');
}
