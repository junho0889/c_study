/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Dart 학습 02단계: 제어 흐름 (Control Flow)
  ─ if/else, switch, 반복문, break/continue ─

  ■ 실행 방법: dart run main.dart
  ■ Flutter에서 제어 흐름은 매우 중요해요!
    예: 로그인 성공하면 홈 화면, 실패하면 오류 메시지 표시
    예: 목록을 반복해서 여러 위젯 만들기

  ■ 이번 단계에서 배울 것:
    - if/else if/else (조건 분기)
    - switch 문 (여러 경우 선택)
    - for 반복문 (정해진 횟수 반복)
    - while, do-while (조건 반복)
    - break, continue (반복 제어)

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

void main() {
  print('');
  print('┌────────────────────────────────────────┐');
  print('│  Dart 제어 흐름 학습을 시작합니다!      │');
  print('└────────────────────────────────────────┘');
  print('');

  // ─────────────────────────────────────────────
  // 1단원: if / else if / else
  // ─────────────────────────────────────────────
  // if = "만약에..." 라는 뜻!
  // 비유: 날씨에 따른 준비물 결정하기!
  //       만약(if) 비가 오면 → 우산 챙기기
  //       그렇지 않고(else if) 눈이 오면 → 장갑 챙기기
  //       아니면(else) → 그냥 나가기
  print('=== 1단원: if/else 조건문 ===');

  int score = 85;

  // 기본 if문
  if (score >= 90) {
    print('성적: 수 (90점 이상!)');
  } else if (score >= 80) {
    print('성적: 우 (80점 이상!)');  // 85점이니까 이게 실행돼요
  } else if (score >= 70) {
    print('성적: 미 (70점 이상!)');
  } else if (score >= 60) {
    print('성적: 양 (60점 이상!)');
  } else {
    print('성적: 가 (60점 미만...)');
  }

  // 날씨 예시
  print('');
  print('--- 날씨 준비물 ---');
  bool isRaining = true;
  bool isCold = false;

  if (isRaining) {
    print('비가 오네요! 우산을 챙겨요.');
    if (isCold) {
      print('춥기도 하니까 외투도 챙겨요!');  // if 안에 if - 중첩 if
    }
  } else if (isCold) {
    print('춥네요! 두꺼운 옷을 입어요.');
  } else {
    print('날씨가 좋아요! 그냥 나가요.');
  }

  // ─────────────────────────────────────────────
  // 2단원: 조건부 표현식 (삼항 연산자와 null 병합)
  // ─────────────────────────────────────────────
  // 비유: 짧게 쓰는 if-else 단축키!
  print('');
  print('=== 2단원: 조건부 표현식 ===');

  int age = 15;

  // 삼항 연산자: 조건 ? 참일때값 : 거짓일때값
  // 비유: "키가 120cm 이상이에요? 그러면 탑승가능, 아니면 탑승불가"
  String ageGroup = age >= 18 ? '성인' : '미성년자';
  print('나이: $age → $ageGroup');

  // ?? 연산자 (Null 병합 연산자)
  // 비유: "상자 열었을 때 비어있으면 대신 이걸 써요"
  String? userName;
  String displayName = userName ?? '손님';
  print('사용자: $displayName');   // '손님' 출력

  userName = '김민수';
  displayName = userName ?? '손님';
  print('사용자: $displayName');   // '김민수' 출력

  // ??= 연산자 - null이면 값 할당
  String? title;
  title ??= '제목 없음';    // title이 null이면 '제목 없음' 할당
  print('제목: $title');

  // Flutter에서 삼항 연산자 사용 예시:
  // Text(isLoggedIn ? '로그아웃' : '로그인')
  // Color(isSelected ? Colors.blue : Colors.grey)

  // ─────────────────────────────────────────────
  // 3단원: switch 문
  // ─────────────────────────────────────────────
  // switch = 여러 경우 중 하나를 선택하는 문법
  // 비유: 자동판매기 버튼!
  //       1번 버튼 → 콜라
  //       2번 버튼 → 사이다
  //       3번 버튼 → 물
  //       그 외 → 잘못된 선택
  print('');
  print('=== 3단원: switch 문 ===');

  // 전통적인 switch 문
  int dayNumber = 3;
  String dayName;

  switch (dayNumber) {
    case 1:
      dayName = '월요일';
      break;   // break = "여기서 멈춰요!" switch를 빠져나가요
    case 2:
      dayName = '화요일';
      break;
    case 3:
      dayName = '수요일';
      break;   // dayNumber가 3이니까 이게 실행돼요
    case 4:
      dayName = '목요일';
      break;
    case 5:
      dayName = '금요일';
      break;
    case 6:
      dayName = '토요일';
      break;
    case 7:
      dayName = '일요일';
      break;
    default:   // 어떤 case에도 안 맞으면 default 실행
      dayName = '알 수 없는 요일';
  }
  print('$dayNumber 번째 날은 $dayName');

  // 향상된 switch 표현식 (Dart 3.0+)
  // 비유: 더 짧고 깔끔하게 쓰는 스위치!
  print('--- 향상된 switch ---');
  String season = '여름';
  String activity = switch (season) {
    '봄' => '꽃구경',
    '여름' => '수영',
    '가을' => '단풍 구경',
    '겨울' => '눈썰매',
    _ => '집에서 쉬기',  // _ 는 default와 같아요
  };
  print('$season 에는 $activity 을(를) 해요!');

  // switch로 과일 색상 알기
  String fruit = '사과';
  String color = switch (fruit) {
    '사과' || '딸기' || '토마토' => '빨간색',  // || 는 "또는"
    '바나나' || '레몬' => '노란색',
    '포도' || '블루베리' => '보라색',
    '수박' => '초록/빨간색',
    _ => '색상 모름',
  };
  print('$fruit 의 색은 $color 이에요!');

  // ─────────────────────────────────────────────
  // 4단원: for 반복문 (C 스타일)
  // ─────────────────────────────────────────────
  // for = 정해진 횟수만큼 반복하기
  // 비유: "체육 시간에 줄넘기 10번 해!" 처럼 정해진 횟수 반복!
  //
  // for (시작값; 조건; 매 반복 후 변경) { 반복할 코드 }
  print('');
  print('=== 4단원: for 반복문 ===');

  // 1부터 5까지 출력
  print('--- 1부터 5까지 ---');
  for (int i = 1; i <= 5; i++) {
    // i = 1 로 시작
    // i <= 5 인 동안 반복
    // 매번 i++ (i를 1씩 증가)
    print('  숫자: $i');
  }

  // 5단 구구단
  print('--- 5단 구구단 ---');
  for (int i = 1; i <= 9; i++) {
    print('  5 × $i = ${5 * i}');
  }

  // 거꾸로 세기
  print('--- 카운트다운 ---');
  for (int i = 5; i >= 1; i--) {
    print('  $i...');
  }
  print('  발사! 🚀');

  // 짝수만 출력
  print('--- 1~10 짝수 ---');
  for (int i = 1; i <= 10; i++) {
    if (i % 2 == 0) {  // 2로 나누어 떨어지면 짝수
      print('  짝수: $i');
    }
  }

  // ─────────────────────────────────────────────
  // 5단원: for-in 반복문
  // ─────────────────────────────────────────────
  // for-in = 목록의 각 항목을 하나씩 꺼내서 처리하기
  // 비유: 도시락 통에서 반찬을 하나씩 꺼내 먹기!
  //       (반찬 in 도시락통) - 도시락통에 있는 반찬마다 하나씩
  print('');
  print('=== 5단원: for-in 반복문 ===');

  List<String> fruits = ['사과', '바나나', '딸기', '수박', '포도'];

  print('--- 과일 목록 ---');
  for (String fruit2 in fruits) {
    // fruits 리스트에서 하나씩 꺼내 fruit2에 담아요
    print('  과일: $fruit2');
  }

  // 숫자 합계 구하기
  List<int> numbers = [10, 20, 30, 40, 50];
  int total = 0;
  for (int num in numbers) {
    total += num;  // 하나씩 더해가요
  }
  print('합계: $total');   // 150

  // Flutter에서 for-in 사용 예시 (위젯 리스트 만들기):
  // children: [for (var item in items) Text(item)]

  // ─────────────────────────────────────────────
  // 6단원: forEach 메서드
  // ─────────────────────────────────────────────
  // forEach = 리스트의 각 항목에 함수를 적용하기
  // 비유: 반 학생들 모두에게 같은 편지 한 장씩 나눠주기!
  print('');
  print('=== 6단원: forEach ===');

  List<String> colors = ['빨강', '주황', '노랑', '초록', '파랑'];

  // 화살표 함수로 간단하게 (=> 기호 사용)
  colors.forEach((color) => print('  색상: $color'));

  // 여러 줄로 쓸 때는 중괄호 사용
  print('--- 번호 붙이기 ---');
  int index = 1;
  colors.forEach((color) {
    print('  $index. $color');
    index++;
  });

  // ─────────────────────────────────────────────
  // 7단원: while 반복문
  // ─────────────────────────────────────────────
  // while = "~인 동안 계속해!" 라는 뜻
  // 비유: 배가 부를 때까지 먹기! 배고프면(while 배고프다) 계속 먹어요.
  //       언제 멈출지 모르는 반복에 사용해요!
  print('');
  print('=== 7단원: while 반복문 ===');

  // 기본 while
  int count = 1;
  print('--- while로 1~5 출력 ---');
  while (count <= 5) {     // count가 5 이하인 동안 반복
    print('  count: $count');
    count++;               // 잊으면 안 돼요! 안 쓰면 무한 반복됩니다!
  }

  // 숫자 맞추기 게임 시뮬레이션
  print('--- 숫자 찾기 ---');
  int target = 7;
  int guess = 1;
  while (guess != target) {
    print('  $guess 는 아니에요...');
    guess++;
  }
  print('  $guess 를 찾았어요!');

  // ─────────────────────────────────────────────
  // 8단원: do-while 반복문
  // ─────────────────────────────────────────────
  // do-while = 일단 한 번 하고, 조건 확인!
  // 비유: 음식을 일단 한 입 먹어보고(do), 맛있으면(while) 계속 먹어요!
  //       while과 다른 점: 무조건 최소 1번은 실행됩니다!
  print('');
  print('=== 8단원: do-while 반복문 ===');

  int number = 1;
  print('--- do-while로 1~3 출력 ---');
  do {
    print('  number: $number');  // 일단 실행!
    number++;
  } while (number <= 3);        // 그다음 조건 확인

  // while과 do-while 차이 보여주기
  print('--- while vs do-while 차이 ---');
  int whileVar = 10;
  while (whileVar < 5) {   // 처음부터 조건이 false → 한 번도 안 실행!
    print('  while: 이게 출력되면 안 돼요!');
  }
  print('  while: 한 번도 실행 안 됐어요 (조건이 처음부터 false)');

  int doWhileVar = 10;
  do {
    print('  do-while: 조건 false여도 한 번은 실행돼요! (doWhileVar: $doWhileVar)');
  } while (doWhileVar < 5);   // 조건이 false여도 이미 한 번 실행됨

  // ─────────────────────────────────────────────
  // 9단원: break와 continue
  // ─────────────────────────────────────────────
  // break = 반복문 탈출! "그만!"
  // continue = 이번 건 건너뛰고 다음으로!
  //
  // 비유:
  //   break = 줄넘기 하다가 다리 아파서 완전히 멈추기
  //   continue = 줄넘기 하다가 한 번 실수해서 그 번만 넘기고 계속하기
  print('');
  print('=== 9단원: break와 continue ===');

  // break 예시
  print('--- break: 5를 찾으면 멈추기 ---');
  for (int i = 1; i <= 10; i++) {
    if (i == 5) {
      print('  5를 찾았어요! 멈춥니다!');
      break;   // 반복문 완전히 빠져나가기
    }
    print('  $i 확인 중...');
  }

  // continue 예시
  print('--- continue: 홀수만 건너뛰기 ---');
  for (int i = 1; i <= 8; i++) {
    if (i % 2 != 0) {   // 홀수이면
      continue;          // 이번 반복 건너뛰기
    }
    print('  짝수: $i');
  }

  // 중첩 반복문에서 break
  print('--- 중첩 for에서 break ---');
  bool found = false;
  outerLoop: for (int row = 1; row <= 3; row++) {   // 레이블(이름표) 붙이기
    for (int col = 1; col <= 3; col++) {
      if (row == 2 && col == 2) {
        print('  ($row, $col) 에서 찾았어요!');
        found = true;
        break outerLoop;   // 바깥 반복문까지 한 번에 탈출!
      }
      print('  ($row, $col) 확인 중...');
    }
  }

  // ─────────────────────────────────────────────
  // 10단원: 실용 예제 - 간단한 게임 점수 계산
  // ─────────────────────────────────────────────
  print('');
  print('=== 10단원: 실용 예제 - 점수 계산 ===');

  List<int> gameScores = [85, 92, 78, 95, 60, 88, 73, 100, 55, 91];
  int totalScore = 0;
  int passCount = 0;
  int highCount = 0;

  for (int gameScore in gameScores) {
    totalScore += gameScore;

    if (gameScore >= 90) {
      highCount++;
      print('  $gameScore 점 - 우수! ★');
    } else if (gameScore >= 70) {
      passCount++;
      print('  $gameScore 점 - 통과');
    } else {
      print('  $gameScore 점 - 분발하세요!');
    }
  }

  double average = totalScore / gameScores.length;
  print('');
  print('┌────────────────────────────┐');
  print('│  결과 요약                 │');
  print('├────────────────────────────┤');
  print('│  총 점수: $totalScore 점       │');
  print('│  평균: ${average.toStringAsFixed(1)} 점         │');
  print('│  우수: $highCount 명             │');
  print('│  통과: $passCount 명             │');
  print('└────────────────────────────┘');

  // ─────────────────────────────────────────────
  // 마무리: Flutter와의 연결
  // ─────────────────────────────────────────────
  print('');
  print('┌────────────────────────────────────────────────────┐');
  print('│  Flutter와의 연결                                  │');
  print('│                                                    │');
  print('│  - if/else: 로그인 상태에 따라 다른 화면 표시     │');
  print('│  - switch: 탭 인덱스에 따라 다른 화면 보여주기   │');
  print('│  - for-in: 데이터 목록으로 위젯 리스트 생성      │');
  print('│    예: [for (var item in items) ListTile(...)]    │');
  print('│  - while: 로딩 중인 동안 스피너 표시             │');
  print('│                                                    │');
  print('│  Flutter 위젯 트리에서:                           │');
  print('│  Column(children: [                               │');
  print('│    for (var score in scores)                      │');
  print('│      if (score > 90)                              │');
  print('│        Text(\'우수: \$score\')                      │');
  print('│  ])                                               │');
  print('└────────────────────────────────────────────────────┘');
  print('');
  print('02단계 완료! 다음은 03_functions 입니다!');
}
