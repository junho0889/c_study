/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Dart 학습 01단계: 기초의 기초
  ─ 변수, 자료형, 입출력, 연산자 ─

  ■ 실행 방법: dart run main.dart
  ■ Dart는 Flutter 앱 개발에 사용되는 언어입니다!
    Flutter로 스마트폰 앱을 만들려면 Dart를 먼저 알아야 해요.
    마치 요리를 배우려면 먼저 재료 이름을 알아야 하는 것처럼요! 🍳

  ■ Dart란?
    구글이 만든 프로그래밍 언어예요.
    스마트폰 앱(Flutter), 웹, 서버 프로그램을 만들 수 있어요.

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// dart:io 는 입력/출력 기능을 제공하는 라이브러리예요.
// 라이브러리 = 남이 미리 만들어놓은 도구 모음. 가져다 쓰면 돼요!
import 'dart:io';

// ┌─────────────────────────────────────────────┐
// │  main() 함수 - 프로그램의 시작점              │
// │  모든 Dart 프로그램은 main()에서 시작해요!    │
// └─────────────────────────────────────────────┘
// 비유: main() 은 학교 수업의 "자, 시작하겠습니다!" 와 같아요.
//      선생님이 수업을 시작하는 신호처럼, 컴퓨터가 프로그램을
//      시작하는 신호예요!
void main() {
  // void = 이 함수는 아무것도 돌려주지 않아요 (결과값 없음)
  // main = 함수 이름
  // () = 이 함수에 넣어줄 재료가 없어요

  print(''); // 빈 줄 출력
  print('┌────────────────────────────────────────┐');
  print('│  Dart 기초 학습을 시작합니다!           │');
  print('│  차근차근 같이 배워봐요!                │');
  print('└────────────────────────────────────────┘');
  print('');

  // ─────────────────────────────────────────────
  // 1단원: print() 함수 - 화면에 글자 출력하기
  // ─────────────────────────────────────────────
  // print() = 화면에 글자를 출력하는 함수
  // 비유: 칠판에 글씨 쓰기!
  //       print('안녕') 하면 화면에 "안녕"이 나타나요.
  print('=== 1단원: print() 함수 ===');
  print('안녕하세요! Dart입니다!');
  print('숫자도 출력할 수 있어요: 12345');
  print(42);       // 숫자를 바로 넣어도 돼요
  print(3.14);     // 소수도 돼요
  print(true);     // 참/거짓도 돼요

  // ─────────────────────────────────────────────
  // 2단원: 변수 (Variable) - 정보를 담는 상자
  // ─────────────────────────────────────────────
  // 변수 = 정보를 담아두는 이름표가 붙은 상자
  // 비유: 학교 사물함! 이름표(변수명)가 붙어있고, 안에 물건(값)을 넣어요.
  //       "철수의 사물함" 안에 "가방"이 들어있는 것처럼!
  print('');
  print('=== 2단원: 변수 ===');

  // var - 자동으로 자료형을 알아맞히는 변수
  // 비유: "뭐든 담을 수 있는 마법 상자" - 뭘 넣는지 보고 상자 종류를 정해요
  var name = '김철수';      // 글자를 넣었으니 자동으로 String(문자열) 상자가 됩니다
  var age = 10;             // 숫자를 넣었으니 자동으로 int(정수) 상자가 됩니다
  var height = 145.5;       // 소수를 넣었으니 자동으로 double(실수) 상자가 됩니다
  var isStudent = true;     // 참/거짓이니까 bool(불리언) 상자가 됩니다

  print('이름: $name');         // $ 기호로 변수 값을 문자열에 넣을 수 있어요!
  print('나이: $age 살');
  print('키: $height cm');
  print('학생인가요? $isStudent');

  // ─────────────────────────────────────────────
  // 3단원: 자료형 (Data Types) - 상자의 종류
  // ─────────────────────────────────────────────
  // 자료형 = 변수에 담을 수 있는 정보의 종류
  // 비유: 상자 종류! 신발 상자, 과자 상자, 책 상자처럼
  //       각각 다른 종류의 물건을 담는 상자가 있어요.
  print('');
  print('=== 3단원: 자료형 ===');

  // int - 정수 (소수점 없는 숫자)
  // 비유: 사과 개수 - 사과는 0.5개가 없잖아요! 딱 떨어지는 숫자!
  int appleCount = 5;
  int temperature = -3;    // 음수도 됩니다 (영하 3도)
  print('사과 개수: $appleCount 개');
  print('기온: $temperature 도');

  // double - 실수 (소수점 있는 숫자)
  // 비유: 체온계 - 36.5도처럼 소수점이 있는 숫자!
  double bodyTemp = 36.5;
  double pi = 3.14159;
  print('체온: $bodyTemp 도');
  print('원주율: $pi');

  // num - int와 double 모두 담을 수 있는 상자
  // 비유: 정수도, 소수도 담을 수 있는 "숫자 상자"
  num score = 95;        // 정수로 시작
  score = 95.5;          // 소수로 바꿔도 됩니다!
  print('점수: $score 점');

  // String - 문자열 (글자들의 모음)
  // 비유: 글자들이 줄 서 있는 것! "안녕"은 '안','녕' 두 글자가 줄 선 것
  String greeting = '안녕하세요!';
  String school = "초등학교";     // 작은따옴표, 큰따옴표 모두 사용 가능!
  print('인사: $greeting');
  print('학교: $school');

  // bool - 불리언 (참 또는 거짓, 둘 중 하나!)
  // 비유: 전등 스위치! ON(true) 또는 OFF(false), 두 가지만 있어요.
  bool isRaining = false;
  bool isSunny = true;
  print('비가 오나요? $isRaining');
  print('맑은가요? $isSunny');

  // dynamic - 뭐든 담을 수 있는 완전 자유로운 상자
  // 비유: 뭐든 넣을 수 있는 "큰 보자기" - 편하지만 조심해서 써야 해요!
  // Flutter에서는 가능하면 dynamic 사용을 피하는 게 좋아요!
  dynamic anything = '처음엔 문자열';
  print('dynamic 변수: $anything');
  anything = 42;           // 숫자로 바꿔도 됩니다
  print('dynamic 변수 변경: $anything');
  anything = true;         // 참/거짓으로 바꿔도 됩니다
  print('dynamic 변수 또 변경: $anything');

  // ─────────────────────────────────────────────
  // 4단원: final과 const - 바꿀 수 없는 변수
  // ─────────────────────────────────────────────
  // final = 한 번 정하면 바꿀 수 없는 변수 (프로그램 실행 중에 결정)
  // const = 컴파일(번역)할 때부터 정해지는 절대 불변 변수
  //
  // 비유:
  //   final = 학교 이름표. 한 번 만들면 못 바꿔요! (하지만 만들 때 이름 쓸 수 있음)
  //   const = 교과서에 인쇄된 글. 이미 인쇄됐으니 절대 못 바꿔요!
  print('');
  print('=== 4단원: final과 const ===');

  final String mySchool = '행복 초등학교';
  // mySchool = '다른 학교'; // 이렇게 하면 오류! final은 변경 불가!
  print('내 학교: $mySchool');

  const double GRAVITY = 9.8;   // 중력가속도 - 절대 안 변하는 물리 상수!
  const int MAX_SCORE = 100;    // 최대 점수 - 항상 100점이에요
  print('중력가속도: $GRAVITY m/s²');
  print('최대 점수: $MAX_SCORE 점');

  // Flutter에서 const 사용 예시 (코드만 보여줍니다)
  // const Text('안녕하세요') - Flutter에서 위젯을 const로 만들면 성능이 좋아져요!

  // ─────────────────────────────────────────────
  // 5단원: Null Safety - 빈 상자 조심하기!
  // ─────────────────────────────────────────────
  // null = 아무것도 없는 상태
  // 비유: 빈 상자. 상자는 있는데 안에 아무것도 없어요!
  //
  // Dart의 특별한 기능: "Null Safety" (안전한 null 처리)
  // 비유: 빈 상자를 열려면 먼저 "안에 뭐가 있나요?" 확인해야 해요!
  //       확인 없이 열다가 빈 상자면 손가락을 다칠 수 있으니까요!
  print('');
  print('=== 5단원: Null Safety ===');

  // String? = null을 담을 수도 있는 변수 (물음표!)
  // String  = null을 절대 담을 수 없는 변수 (물음표 없음)
  String? nickname;         // ? 를 붙이면 null(빈 값)을 담을 수 있어요
  print('별명 (null이에요): $nickname');   // null 출력

  nickname = '코딩왕';      // 이제 값을 넣었어요
  print('별명 (값이 생겼어요): $nickname');

  // ?. 연산자 - null일 수도 있는 상자를 안전하게 사용하기
  // 비유: "상자에 뭔가 있으면 꺼내고, 없으면 그냥 포기해요"
  String? maybeNull;
  int? length = maybeNull?.length;  // maybeNull이 null이면 length도 null
  print('글자 수 (null일 수 있음): $length');

  // ?? 연산자 - null이면 기본값 사용하기
  // 비유: "상자가 비어있으면 대신 이걸 써요"
  String displayName = nickname ?? '이름 없음';
  print('표시 이름: $displayName');

  String? emptyName;
  String displayName2 = emptyName ?? '손님';
  print('표시 이름2: $displayName2');   // '손님' 출력

  // ─────────────────────────────────────────────
  // 6단원: 문자열 다루기
  // ─────────────────────────────────────────────
  // 문자열 = 글자들의 모음
  // 비유: 목걸이에 꿰어진 구슬들! 각 구슬이 글자예요.
  print('');
  print('=== 6단원: 문자열 다루기 ===');

  String myName = '김다은';
  String friendName = '이준호';

  // 문자열 합치기 (+ 연산자)
  String together = myName + '와 ' + friendName;
  print('함께: $together');

  // 문자열 보간법 (String Interpolation) - $ 기호 사용
  // Flutter에서 자주 쓰이는 중요한 기능이에요!
  // 비유: 편지 템플릿! "__님 안녕하세요" 에서 __ 자리에 이름을 넣는 것
  int myAge = 11;
  print('저는 $myName 이고, $myAge 살이에요.');

  // ${} 로 복잡한 식도 넣을 수 있어요!
  print('내년에는 ${myAge + 1} 살이 될 거예요!');
  print('이름은 ${myName.length}글자예요.');

  // 여러 줄 문자열 - ''' 세 개로 감싸기
  String poem = '''
안녕 Dart!
나는 너를 배우고 있어.
Flutter도 함께 배울 거야!
  ''';
  print('시:');
  print(poem);

  // 문자열 메서드 (기능들)
  String message = '  안녕하세요! 저는 Dart 입니다.  ';
  print('원본: "$message"');
  print('앞뒤 공백 제거: "${message.trim()}"');
  print('대문자로: "${message.toUpperCase()}"');
  print('소문자로: "${message.toLowerCase()}"');
  print('글자 수: ${message.length}');
  print('"Dart" 포함되나요? ${message.contains("Dart")}');
  print('"Dart"를 "Flutter"로: "${message.replaceAll("Dart", "Flutter")}\"');

  // 문자열 나누기 (split)
  String fruits = '사과,바나나,딸기,포도';
  List<String> fruitList = fruits.split(',');  // 쉼표로 나누기
  print('과일 목록: $fruitList');

  // ─────────────────────────────────────────────
  // 7단원: 수학 연산자
  // ─────────────────────────────────────────────
  // 비유: 계산기 버튼들!
  print('');
  print('=== 7단원: 수학 연산자 ===');

  int a = 10;
  int b = 3;

  print('$a + $b = ${a + b}');   // 더하기
  print('$a - $b = ${a - b}');   // 빼기
  print('$a × $b = ${a * b}');   // 곱하기
  print('$a ÷ $b = ${a / b}');   // 나누기 (결과가 double이 됩니다)
  print('$a ÷ $b 몫 = ${a ~/ b}'); // 정수 나누기 (몫만, 소수점 버림)
  print('$a ÷ $b 나머지 = ${a % b}'); // 나머지 (나누고 남은 것)

  // 짝수/홀수 판별에 % 사용!
  print('10은 짝수인가요? ${10 % 2 == 0}');   // true
  print('7은 짝수인가요? ${7 % 2 == 0}');     // false

  // 증가, 감소 연산자
  int count = 5;
  count++;  // count = count + 1 (한 개 더하기)
  print('++ 후: $count');    // 6
  count--;  // count = count - 1 (한 개 빼기)
  print('-- 후: $count');    // 5

  // 복합 대입 연산자
  int score2 = 0;
  score2 += 10;   // score2 = score2 + 10
  print('+=10 후: $score2');   // 10
  score2 *= 2;    // score2 = score2 * 2
  print('*=2 후: $score2');    // 20
  score2 -= 5;    // score2 = score2 - 5
  print('-=5 후: $score2');    // 15

  // ─────────────────────────────────────────────
  // 8단원: 비교 연산자와 논리 연산자
  // ─────────────────────────────────────────────
  // 비유: "맞나요, 틀리나요?" 를 확인하는 연산자들
  print('');
  print('=== 8단원: 비교/논리 연산자 ===');

  int x = 10;
  int y = 20;

  print('$x > $y : ${x > y}');     // 크다
  print('$x < $y : ${x < y}');     // 작다
  print('$x >= $x : ${x >= x}');   // 크거나 같다
  print('$x <= $y : ${x <= y}');   // 작거나 같다
  print('$x == $x : ${x == x}');   // 같다
  print('$x != $y : ${x != y}');   // 다르다

  // 논리 연산자
  // && = AND (그리고) - 둘 다 참이어야 참
  // || = OR  (또는) - 하나만 참이어도 참
  // !  = NOT (반대로) - 참을 거짓으로, 거짓을 참으로
  //
  // 비유:
  //   && = 놀이터 가려면 숙제도 하고 AND 집안일도 해야 해요!
  //   || = 비가 와서 OR 몸이 아프면 학교를 쉬어요.
  //   !  = 비가 "안" 와요 = !isRaining

  bool hungry = true;
  bool hasFood = true;
  bool tired = false;

  print('배고프고 음식 있음: ${hungry && hasFood}');   // true
  print('배고프거나 피곤함: ${hungry || tired}');      // true
  print('피곤하지 않음: ${!tired}');                   // true

  // ─────────────────────────────────────────────
  // 9단원: 입력받기 (stdin)
  // ─────────────────────────────────────────────
  // stdin = Standard Input (표준 입력)
  // 비유: 사용자가 키보드로 입력하는 것을 받아오는 것!
  // 주의: 터미널에서만 동작해요. Flutter 앱에서는 Textfield 위젯을 사용해요!
  print('');
  print('=== 9단원: 입력받기 ===');
  print('※ 아래는 입력받기 코드 예시입니다 (실제 입력 없이 진행)');

  // 실제 입력받기 코드 예시:
  // stdout.write('이름을 입력하세요: ');
  // String? inputName = stdin.readLineSync();
  // print('입력하신 이름: $inputName');

  // 숫자로 변환하기
  // String? inputAge = stdin.readLineSync();
  // int parsedAge = int.parse(inputAge!);  // 문자열을 정수로 변환
  // double parsedHeight = double.parse('175.5');  // 소수로 변환

  print('int.parse("42") = ${int.parse("42")}');
  print('double.parse("3.14") = ${double.parse("3.14")}');
  print('42.toString() = ${'${42}'}');  // 숫자를 문자열로

  // ─────────────────────────────────────────────
  // 10단원: 타입 확인과 변환
  // ─────────────────────────────────────────────
  print('');
  print('=== 10단원: 타입 확인과 변환 ===');

  var value = 42;
  print('value의 타입: ${value.runtimeType}');   // int

  // is 연산자 - "~이에요?" 확인
  // 비유: "이게 사과예요?" 처럼 종류를 확인하는 것
  print('value는 int인가요? ${value is int}');       // true
  print('value는 String인가요? ${value is String}'); // false

  // as 연산자 - 타입 변환 (조심해서 써야 해요!)
  // 비유: 번역기처럼 한 종류를 다른 종류로 바꿔요
  dynamic dynamicValue = 'Hello Dart!';
  String stringValue = dynamicValue as String;
  print('변환된 값: $stringValue');

  // ─────────────────────────────────────────────
  // 마무리: Flutter와의 연결
  // ─────────────────────────────────────────────
  print('');
  print('┌────────────────────────────────────────────────────┐');
  print('│  Flutter와의 연결                                  │');
  print('│                                                    │');
  print('│  오늘 배운 것들이 Flutter에서 어떻게 쓰이나요?    │');
  print('│                                                    │');
  print('│  - String, int, double: 위젯에 표시할 텍스트,    │');
  print('│    숫자, 크기 값으로 사용돼요                     │');
  print('│  - bool: 버튼이 활성화되었는지, 체크박스 상태등  │');
  print('│  - null safety: Flutter 앱의 안전성을 보장해요   │');
  print('│  - final/const: Flutter 위젯 최적화에 사용돼요   │');
  print('│                                                    │');
  print('│  예시: Text(\'$name\') - String을 화면에 표시!    │');
  print('│        Icon(Icons.star, size: 24.0) - double!    │');
  print('└────────────────────────────────────────────────────┘');
  print('');
  print('01단계 완료! 수고하셨어요! 다음은 02_control_flow 입니다!');
}
