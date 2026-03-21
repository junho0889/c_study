/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Dart 학습 12단계: 패키지와 Pub (Packages & Pub)
  ─ pubspec.yaml · import · 표준 라이브러리 · pub.dev · 패키지 만들기 ─

  ■ 실행: dart run main.dart
  ■ 컴파일: dart compile exe main.dart

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

import 'dart:convert';
import 'dart:math';

// =====================================================================
// 레슨 1 — 패키지가 뭘까?
// =====================================================================
/*
★ 패키지 = "재사용 가능한 코드 도구 상자"

  비유: 공구 상자
  ┌──────────────────────────────────────────────────────────┐
  │  집을 지을 때 망치, 톱, 드라이버를 직접 만들지 않듯이   │
  │  프로그래밍에서도 이미 잘 만들어진 도구를 가져다 씀     │
  │                                                          │
  │  ★ 직접 만들기: 시간 오래 걸림, 버그 위험               │
  │  ★ 패키지 사용: 검증된 코드, 즉시 사용 가능             │
  └──────────────────────────────────────────────────────────┘

★ Dart 패키지 종류

  ┌──────────────────┬──────────────────────────────────────┐
  │ 종류             │ 설명                                  │
  ├──────────────────┼──────────────────────────────────────┤
  │ Dart 표준 라이브러리│ dart:core, dart:math, dart:io 등  │
  │ 외부 패키지      │ pub.dev 에서 다운로드                 │
  │ 프로젝트 내 패키지│ 내가 만든 lib/ 코드                  │
  └──────────────────┴──────────────────────────────────────┘

★ pub.dev = Dart/Flutter 패키지 저장소 (Python 의 PyPI 같은 것)
*/

void lesson1WhyPackages() {
  print('[레슨 1] 패키지가 뭘까?');

  print('  패키지 = 재사용 가능한 코드 도구 상자');
  print('  pub.dev = Dart/Flutter 공식 패키지 저장소');
  print('');
  print('  예시: HTTP 통신을 직접 구현하면 수백 줄');
  print('        http 패키지를 쓰면 3줄이면 끝!');
  print('');
}


// =====================================================================
// 레슨 2 — import 의 다양한 형태
// =====================================================================
/*
★ import 문법 정리

  ┌──────────────────────────────────────────────────────────┐
  │  // 1. 표준 라이브러리                                   │
  │  import 'dart:math';                                     │
  │  import 'dart:convert';                                  │
  │  import 'dart:io';                                       │
  │                                                          │
  │  // 2. 외부 패키지                                       │
  │  import 'package:http/http.dart';                        │
  │  import 'package:provider/provider.dart';                │
  │                                                          │
  │  // 3. 프로젝트 내 파일                                  │
  │  import 'src/utils.dart';                                │
  │  import '../models/user.dart';                           │
  │                                                          │
  │  // 4. 별칭 (as)                                         │
  │  import 'dart:math' as math;                             │
  │  math.sqrt(16);                                          │
  │                                                          │
  │  // 5. 선택적 import (show / hide)                       │
  │  import 'dart:math' show Random, pi;                     │
  │  import 'dart:math' hide Point;                          │
  │                                                          │
  │  // 6. 지연 import (deferred)                            │
  │  import 'heavy_lib.dart' deferred as heavy;              │
  │  await heavy.loadLibrary();                              │
  └──────────────────────────────────────────────────────────┘

★ show vs hide
  - show: 지정한 것만 가져옴 (화이트리스트)
  - hide: 지정한 것만 빼고 가져옴 (블랙리스트)
  - 이름 충돌 방지에 유용!
*/

void lesson2ImportVariants() {
  print('[레슨 2] import 의 다양한 형태');

  // dart:math 사용 (이 파일 상단에 import 됨)
  final random = Random(42);
  final score = 70 + random.nextInt(31);
  print('  dart:math → Random 점수: $score');
  print('  dart:math → pi = $pi');
  print('  dart:math → sqrt(144) = ${sqrt(144)}');

  // dart:convert 사용
  final data = {'name': '민수', 'score': score};
  final json = jsonEncode(data);
  print('  dart:convert → jsonEncode: $json');

  // jsonDecode 로 복원
  final decoded = jsonDecode(json) as Map<String, dynamic>;
  print('  dart:convert → jsonDecode: ${decoded['name']}');
  print('');
}


// =====================================================================
// 레슨 3 — pubspec.yaml 이해하기
// =====================================================================
/*
★ pubspec.yaml = "프로젝트의 신분증 + 도구 목록"

  ┌──────────────────────────────────────────────────────────┐
  │  name: my_app                ← 프로젝트 이름             │
  │  description: 학습용 앱       ← 설명                     │
  │  version: 1.0.0              ← 버전                      │
  │                                                          │
  │  environment:                                            │
  │    sdk: ^3.0.0               ← 지원하는 Dart SDK 버전    │
  │                                                          │
  │  dependencies:               ← 실행에 필요한 패키지      │
  │    http: ^1.2.0                                          │
  │    provider: ^6.0.0                                      │
  │                                                          │
  │  dev_dependencies:           ← 개발에만 필요한 패키지    │
  │    test: ^1.24.0                                         │
  │    lints: ^4.0.0                                         │
  └──────────────────────────────────────────────────────────┘

★ 버전 표기법 (Semantic Versioning)
  ┌──────────┬──────────────────────────────────────────────┐
  │ 표기     │ 의미                                         │
  ├──────────┼──────────────────────────────────────────────┤
  │ ^1.2.0   │ >=1.2.0, <2.0.0 (호환되는 최신 버전)        │
  │ >=1.0.0  │ 1.0.0 이상 아무 버전                         │
  │ any      │ 아무 버전 (비권장)                           │
  │ 1.2.3    │ 정확히 이 버전만 (핀 고정)                   │
  └──────────┴──────────────────────────────────────────────┘

★ 명령어
  ┌──────────────────┬──────────────────────────────────────┐
  │ 명령어           │ 동작                                  │
  ├──────────────────┼──────────────────────────────────────┤
  │ dart pub get     │ 의존성 다운로드                       │
  │ dart pub upgrade │ 최신 호환 버전으로 업그레이드          │
  │ dart pub outdated│ 오래된 패키지 확인                    │
  │ dart pub add http│ 패키지 추가 (pubspec 자동 수정)       │
  └──────────────────┴──────────────────────────────────────┘
*/

class FakePackageInfo {
  final String name;
  final String version;
  final String purpose;

  FakePackageInfo(this.name, this.version, this.purpose);
}

void lesson3PubspecYaml() {
  print('[레슨 3] pubspec.yaml 이해하기');

  final commonPackages = [
    FakePackageInfo('http', '^1.2.0', 'HTTP 클라이언트 (서버 통신)'),
    FakePackageInfo('provider', '^6.0.0', '상태 관리 (Flutter)'),
    FakePackageInfo('intl', '^0.19.0', '다국어, 날짜/숫자 형식'),
    FakePackageInfo('shared_preferences', '^2.2.0', '간단한 로컬 저장'),
    FakePackageInfo('path', '^1.9.0', '파일 경로 조작'),
    FakePackageInfo('json_annotation', '^4.9.0', 'JSON 직렬화 어노테이션'),
  ];

  print('  자주 쓰는 Dart/Flutter 패키지:');
  print('  ┌─────────────────────┬──────────┬──────────────────────┐');
  print('  │ 패키지              │ 버전     │ 용도                 │');
  print('  ├─────────────────────┼──────────┼──────────────────────┤');
  for (final p in commonPackages) {
    final name = p.name.padRight(19);
    final ver = p.version.padRight(8);
    print('  │ $name │ $ver │ ${p.purpose.padRight(20)} │');
  }
  print('  └─────────────────────┴──────────┴──────────────────────┘');
  print('');
}


// =====================================================================
// 레슨 4 — 표준 라이브러리 활용
// =====================================================================
/*
★ Dart 표준 라이브러리 (외부 설치 없이 사용 가능!)

  ┌──────────────┬──────────────────────────────────────────┐
  │ 라이브러리   │ 주요 기능                                 │
  ├──────────────┼──────────────────────────────────────────┤
  │ dart:core    │ 기본 타입, 컬렉션 (자동 import)           │
  │ dart:math    │ 수학 함수, Random, pi                     │
  │ dart:convert │ JSON, UTF-8, Base64 인코딩/디코딩         │
  │ dart:io      │ 파일, 소켓, HTTP (CLI/서버 전용)          │
  │ dart:async   │ Future, Stream, Timer                     │
  │ dart:collection │ LinkedList, Queue 등 추가 컬렉션       │
  │ dart:typed_data │ 바이트 배열, Int32List 등               │
  └──────────────┴──────────────────────────────────────────┘
*/

void lesson4StandardLibrary() {
  print('[레슨 4] 표준 라이브러리 활용');

  // ── dart:core (자동 import) ──
  print('  --- dart:core ---');
  final now = DateTime.now();
  print('  DateTime.now(): $now');
  print('  Duration: ${const Duration(hours: 2, minutes: 30)}');
  print('  RegExp: ${'hello123'.replaceAll(RegExp(r'\d'), '*')}');

  // ── dart:math ──
  print('  --- dart:math ---');
  print('  pi = $pi');
  print('  e  = $e');
  print('  sqrt(256) = ${sqrt(256)}');
  print('  pow(2, 10) = ${pow(2, 10)}');
  print('  min(3, 7) = ${min(3, 7)}');
  print('  max(3, 7) = ${max(3, 7)}');

  // ── dart:convert ──
  print('  --- dart:convert ---');
  final obj = {'items': ['사과', '바나나'], 'count': 2};
  final jsonStr = jsonEncode(obj);
  print('  jsonEncode: $jsonStr');

  final base64Str = base64Encode(utf8.encode('Hello Dart!'));
  print('  base64Encode: $base64Str');
  print('  base64Decode: ${utf8.decode(base64Decode(base64Str))}');
  print('');
}


// =====================================================================
// 레슨 5 — 프로젝트 구조와 lib 폴더
// =====================================================================
/*
★ 표준 Dart 프로젝트 구조

  ┌──────────────────────────────────────────────────┐
  │  my_project/                                     │
  │  ├── pubspec.yaml        ← 프로젝트 설정         │
  │  ├── pubspec.lock        ← 정확한 버전 잠금      │
  │  ├── analysis_options.yaml ← 린트 규칙           │
  │  ├── README.md                                   │
  │  │                                               │
  │  ├── lib/                ← 라이브러리 코드       │
  │  │   ├── my_project.dart ← 메인 라이브러리 파일  │
  │  │   └── src/            ← 내부 구현 (비공개)    │
  │  │       ├── models/                             │
  │  │       ├── services/                           │
  │  │       └── utils/                              │
  │  │                                               │
  │  ├── bin/                ← 실행 파일             │
  │  │   └── main.dart                               │
  │  │                                               │
  │  ├── test/               ← 테스트 코드           │
  │  │   └── my_project_test.dart                    │
  │  │                                               │
  │  └── example/            ← 사용 예제             │
  └──────────────────────────────────────────────────┘

★ lib/src/ 안의 파일은 외부에서 직접 import 하면 안 됨!
  → lib/my_project.dart 에서 export 로 공개할 것만 선택

★ part 와 export
  ┌──────────────────────────────────────────────────┐
  │  // lib/my_project.dart                          │
  │  export 'src/models/user.dart';    ← 공개        │
  │  export 'src/utils/helpers.dart';  ← 공개        │
  │  // src/internal.dart 는 export 안 함 → 비공개   │
  └──────────────────────────────────────────────────┘
*/

void lesson5ProjectStructure() {
  print('[레슨 5] 프로젝트 구조');

  // 프로젝트 구조를 코드로 시뮬레이션
  final structure = {
    'pubspec.yaml': '프로젝트 설정 (이름, 의존성)',
    'lib/': '라이브러리 코드 (패키지로 배포되는 부분)',
    'lib/src/': '내부 구현 (직접 import 금지!)',
    'bin/main.dart': '실행 진입점',
    'test/': '테스트 코드',
  };

  print('  표준 Dart 프로젝트 구조:');
  structure.forEach((path, desc) {
    print('    $path → $desc');
  });

  print('');
  print('  ★ dart create my_project  ← 이 명령으로 자동 생성!');
  print('  ★ dart create -t package my_package  ← 패키지 템플릿');
  print('');
}


// =====================================================================
// 레슨 6 — 패키지 만들기 (개념)
// =====================================================================
/*
★ 내가 만든 코드를 패키지로 배포하는 과정

  ┌──────────────────────────────────────────────────────────┐
  │  1. dart create -t package my_utils                      │
  │  2. lib/ 에 코드 작성                                    │
  │  3. test/ 에 테스트 작성                                  │
  │  4. pubspec.yaml 에 메타 정보 입력                       │
  │  5. dart pub publish --dry-run  ← 배포 전 검증           │
  │  6. dart pub publish            ← pub.dev 에 배포!       │
  └──────────────────────────────────────────────────────────┘

★ 좋은 패키지의 조건
  ┌───┬──────────────────────────────────────────┐
  │ 1 │ 문서화: 함수마다 /// 주석                 │
  │ 2 │ 테스트: 핵심 기능에 테스트 코드 작성      │
  │ 3 │ 예제: example/ 폴더에 사용 예제           │
  │ 4 │ 린트: analysis_options.yaml 설정          │
  │ 5 │ 최소 의존성: 꼭 필요한 패키지만 추가      │
  └───┴──────────────────────────────────────────┘
*/

// ── 패키지로 만들 법한 유틸리티 코드 예시 ──

/// 문자열의 첫 글자를 대문자로 변환합니다.
///
/// ```dart
/// capitalize('hello'); // 'Hello'
/// ```
String capitalize(String text) {
  if (text.isEmpty) return text;
  return text[0].toUpperCase() + text.substring(1);
}

/// 리스트를 청크(조각) 단위로 나눕니다.
///
/// ```dart
/// chunk([1,2,3,4,5], 2); // [[1,2],[3,4],[5]]
/// ```
List<List<T>> chunk<T>(List<T> list, int size) {
  final chunks = <List<T>>[];
  for (var i = 0; i < list.length; i += size) {
    final end = (i + size < list.length) ? i + size : list.length;
    chunks.add(list.sublist(i, end));
  }
  return chunks;
}

/// 두 날짜 사이의 일 수를 계산합니다.
int daysBetween(DateTime a, DateTime b) {
  return (a.difference(b).inDays).abs();
}

void lesson6CreatePackage() {
  print('[레슨 6] 패키지 만들기 (개념)');

  // capitalize 테스트
  print('  capitalize("hello") = ${capitalize("hello")}');
  print('  capitalize("dart")  = ${capitalize("dart")}');

  // chunk 테스트
  final numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  print('  chunk($numbers, 3) = ${chunk(numbers, 3)}');

  // daysBetween 테스트
  final today = DateTime.now();
  final birthday = DateTime(2000, 1, 1);
  print('  2000-01-01 부터 오늘까지: ${daysBetween(today, birthday)}일');
  print('');
}


// =====================================================================
// 레슨 7 — 자주 하는 실수
// =====================================================================
/*
★ 패키지 관련 자주 하는 실수 TOP 5

  ┌───┬──────────────────────────┬─────────────────────────────┐
  │ # │ 실수                     │ 해결법                      │
  ├───┼──────────────────────────┼─────────────────────────────┤
  │ 1 │ pubspec.yaml 들여쓰기    │ 공백 2칸 (탭 금지!)         │
  │   │ 오류                     │                             │
  │ 2 │ dart pub get 안 하고     │ 의존성 추가 후 반드시       │
  │   │ import                   │ dart pub get 실행           │
  │ 3 │ 버전 충돌               │ dart pub outdated 로 확인    │
  │ 4 │ lib/src/ 직접 import    │ lib/패키지명.dart 에서       │
  │   │                          │ export 한 것만 import       │
  │ 5 │ 불필요한 패키지 추가     │ 표준 라이브러리로 가능한지   │
  │   │                          │ 먼저 확인!                  │
  └───┴──────────────────────────┴─────────────────────────────┘
*/

void lesson7CommonMistakes() {
  print('[레슨 7] 자주 하는 실수');

  print('  1. pubspec.yaml 에 탭을 쓰면 파싱 에러! (공백 2칸만!)');
  print('  2. 패키지 추가 후 dart pub get 잊지 말기');
  print('  3. 버전 충돌 시 dart pub outdated 로 확인');
  print('  4. lib/src/ 파일을 외부에서 직접 import 금지');
  print('  5. 작은 기능은 표준 라이브러리로 충분한지 먼저 확인');
  print('');

  // ── 실제 사례: jsonEncode 를 위해 외부 패키지를 쓸 필요 없음 ──
  print('  예: JSON 변환은 dart:convert 로 충분!');
  final result = jsonEncode({'lesson': 7, 'complete': true});
  print('  $result');
  print('');
}


// =====================================================================
// 레슨 8 — pubspec.lock 과 의존성 관리
// =====================================================================
/*
★ pubspec.lock = "실제 설치된 정확한 버전 기록"

  ┌──────────────────────────────────────────────────┐
  │  pubspec.yaml  → "^1.2.0" (범위)                │
  │  pubspec.lock  → "1.2.3"  (정확한 버전)         │
  └──────────────────────────────────────────────────┘

★ 왜 lock 파일이 중요할까?
  - 팀원 A: ^1.2.0 → 1.2.3 설치
  - 팀원 B: ^1.2.0 → 1.2.5 설치 (새 버전 나옴)
  - lock 파일 공유 → 모두 같은 버전 사용!

★ 규칙
  ┌────────────────┬──────────────────────────────────┐
  │ 프로젝트 유형  │ lock 파일 Git 커밋?              │
  ├────────────────┼──────────────────────────────────┤
  │ 앱 (실행 가능) │ O (커밋) — 모든 팀원 같은 버전   │
  │ 패키지 (배포용)│ X (커밋 안 함) — 유연성 유지     │
  └────────────────┴──────────────────────────────────┘
*/

void lesson8DependencyManagement() {
  print('[레슨 8] pubspec.lock 과 의존성 관리');

  print('  ┌────────────────────────────────────────────────┐');
  print('  │  pubspec.yaml    pubspec.lock                  │');
  print('  │  http: ^1.2.0 →  http: 1.2.3 (정확한 버전)    │');
  print('  │                                                │');
  print('  │  dart pub get    → lock 파일 생성/업데이트      │');
  print('  │  dart pub upgrade → 최신 호환 버전으로 갱신     │');
  print('  └────────────────────────────────────────────────┘');
  print('');
  print('  ★ 앱 프로젝트: lock 파일을 Git 에 커밋!');
  print('  ★ 패키지:      lock 파일을 .gitignore 에 추가!');
  print('');
}


// =====================================================================
// main — 전체 레슨 실행
// =====================================================================
void main() {
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('  Dart 12단계 : 패키지와 Pub');
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('');

  lesson1WhyPackages();
  lesson2ImportVariants();
  lesson3PubspecYaml();
  lesson4StandardLibrary();
  lesson5ProjectStructure();
  lesson6CreatePackage();
  lesson7CommonMistakes();
  lesson8DependencyManagement();

  print('■■■ 12단계 완료! ■■■');
}
