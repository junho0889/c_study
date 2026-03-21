/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Dart 학습 17단계: 빌드와 배포
  ─ dart compile · 실행 파일 · AOT/JIT · 배포 체크리스트 · CI/CD 개념 ─

  ■ 실행: dart run main.dart
  ■ 컴파일: dart compile exe main.dart

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

import 'dart:io';

// =====================================================================
// 레슨 1 — 빌드가 뭘까?
// =====================================================================
/*
★ 빌드 = "소스 코드를 실행 가능한 형태로 변환하는 과정"

  비유: 요리
  ┌──────────────────────────────────────────────────────────┐
  │  재료(소스 코드) → 요리(빌드) → 음식(실행 파일)         │
  │                                                          │
  │  main.dart  → dart compile exe  → main.exe              │
  │  (레시피)      (조리 과정)         (완성 요리)           │
  └──────────────────────────────────────────────────────────┘

★ Dart 실행 방식 2가지

  ┌──────────────────────────────────────────────────────────┐
  │  JIT (Just-In-Time) — 개발용                             │
  │  ┌────────────────────────────────────────────────┐      │
  │  │ dart run main.dart                             │      │
  │  │ → 실행하면서 동시에 컴파일                     │      │
  │  │ → 핫 리로드 가능, 디버깅 편리                  │      │
  │  │ → 실행 속도는 좀 느림                          │      │
  │  └────────────────────────────────────────────────┘      │
  │                                                          │
  │  AOT (Ahead-Of-Time) — 배포용                            │
  │  ┌────────────────────────────────────────────────┐      │
  │  │ dart compile exe main.dart                     │      │
  │  │ → 미리 기계어로 변환                           │      │
  │  │ → Dart SDK 없이 실행 가능!                     │      │
  │  │ → 실행 속도 빠름, 파일 크기 큼                 │      │
  │  └────────────────────────────────────────────────┘      │
  └──────────────────────────────────────────────────────────┘
*/

void lesson1WhatIsBuild() {
  print('[레슨 1] 빌드가 뭘까?');

  print('  ┌────────────┬──────────────────────────────────┐');
  print('  │ 방식       │ 특징                              │');
  print('  ├────────────┼──────────────────────────────────┤');
  print('  │ JIT        │ 개발용, 핫리로드, dart run        │');
  print('  │ AOT        │ 배포용, 빠른 실행, dart compile   │');
  print('  └────────────┴──────────────────────────────────┘');
  print('');
}


// =====================================================================
// 레슨 2 — dart compile 명령어들
// =====================================================================
/*
★ dart compile 하위 명령어

  ┌──────────────────────┬──────────────────────────────────────┐
  │ 명령어               │ 결과                                  │
  ├──────────────────────┼──────────────────────────────────────┤
  │ dart compile exe     │ 독립 실행 파일 (.exe)                 │
  │                      │ Dart SDK 불필요, 배포에 적합          │
  │ dart compile aot-snapshot│ AOT 스냅샷 (dartaotruntime 필요)│
  │ dart compile jit-snapshot│ JIT 스냅샷 (dart 필요)          │
  │ dart compile kernel  │ Kernel 스냅샷 (.dill)                │
  │ dart compile js      │ JavaScript 로 변환 (웹용)            │
  └──────────────────────┴──────────────────────────────────────┘

★ 가장 많이 쓰는 것: dart compile exe
  → 하나의 파일로 배포 가능
  → 서버, CLI 도구에 적합
*/

void lesson2CompileCommands() {
  print('[레슨 2] dart compile 명령어');

  print('  1. dart compile exe main.dart');
  print('     → 독립 실행 파일 생성 (Dart SDK 없이 실행 가능)');
  print('');
  print('  2. dart compile exe main.dart -o my_app');
  print('     → 출력 파일 이름 지정');
  print('');
  print('  3. dart compile js main.dart -o main.js');
  print('     → 웹 브라우저용 JavaScript 변환');
  print('');

  // 현재 Dart 정보 출력
  print('  현재 Dart 버전: ${Platform.version}');
  print('  OS: ${Platform.operatingSystem}');
  print('  실행 파일: ${Platform.executable}');
  print('');
}


// =====================================================================
// 레슨 3 — 배포 전 체크리스트
// =====================================================================
/*
★ 배포 전 확인 사항 체크리스트

  ┌───┬──────────────────────────────────────────────────────┐
  │ # │ 항목                                                 │
  ├───┼──────────────────────────────────────────────────────┤
  │ 1 │ dart test — 모든 테스트 통과?                         │
  │ 2 │ dart analyze — 정적 분석 경고 없음?                   │
  │ 3 │ 비밀 값(.env, API key) 이 코드에 하드코딩 안 됨?     │
  │ 4 │ pubspec.yaml 버전 업데이트 됨?                       │
  │ 5 │ CHANGELOG 작성 됨?                                   │
  │ 6 │ 불필요한 print/debugPrint 제거 됨?                   │
  │ 7 │ 에러 처리가 사용자 친화적인가?                       │
  │ 8 │ README 에 실행 방법이 명확한가?                      │
  │ 9 │ 의존성 버전이 최신 호환인가? (dart pub outdated)     │
  │10 │ 라이선스 파일 포함?                                  │
  └───┴──────────────────────────────────────────────────────┘

★ 비밀 값 관리
  ┌──────────────────────────────────────────────────┐
  │  ❌ 하드코딩 (절대 안 됨!)                       │
  │  final apiKey = 'sk-abc123xyz';                  │
  │                                                  │
  │  ✅ 환경 변수 사용                               │
  │  final apiKey = Platform.environment['API_KEY']; │
  │                                                  │
  │  ✅ .env 파일 + .gitignore                       │
  │  API_KEY=sk-abc123xyz                            │
  └──────────────────────────────────────────────────┘
*/

class DeployChecklist {
  final List<(String, bool)> _items = [];

  void add(String item, bool passed) {
    _items.add((item, passed));
  }

  void printReport() {
    int passed = 0;
    int failed = 0;

    for (final (item, ok) in _items) {
      final icon = ok ? '✅' : '❌';
      print('    $icon $item');
      if (ok) passed++; else failed++;
    }

    print('');
    print('  결과: $passed 통과 / $failed 실패');
    if (failed > 0) {
      print('  ★ 배포 전에 실패 항목을 수정하세요!');
    } else {
      print('  🎉 배포 준비 완료!');
    }
  }
}

void lesson3Checklist() {
  print('[레슨 3] 배포 전 체크리스트');

  final checklist = DeployChecklist();
  checklist.add('dart test 통과', true);
  checklist.add('dart analyze 경고 없음', true);
  checklist.add('비밀 값 하드코딩 없음', true);
  checklist.add('pubspec.yaml 버전 업데이트', true);
  checklist.add('CHANGELOG 작성', false);
  checklist.add('불필요한 print 제거', true);
  checklist.add('에러 메시지 사용자 친화적', true);

  checklist.printReport();
  print('');
}


// =====================================================================
// 레슨 4 — 환경 변수와 설정 관리
// =====================================================================
/*
★ 환경에 따라 다른 설정 사용

  ┌──────────────────────────────────────────────────┐
  │  개발 환경 (development)                         │
  │  ├─ DB: localhost:5432                           │
  │  ├─ 로그 레벨: debug                             │
  │  └─ API URL: http://localhost:8080               │
  │                                                  │
  │  운영 환경 (production)                           │
  │  ├─ DB: prod-server:5432                         │
  │  ├─ 로그 레벨: error                             │
  │  └─ API URL: https://api.myapp.com               │
  └──────────────────────────────────────────────────┘
*/

class AppEnvironment {
  final String name;
  final String apiUrl;
  final String logLevel;
  final bool debug;

  AppEnvironment._({
    required this.name,
    required this.apiUrl,
    required this.logLevel,
    required this.debug,
  });

  factory AppEnvironment.fromEnv() {
    final env = Platform.environment['APP_ENV'] ?? 'development';

    switch (env) {
      case 'production':
        return AppEnvironment._(
          name: 'production',
          apiUrl: 'https://api.myapp.com',
          logLevel: 'error',
          debug: false,
        );
      case 'staging':
        return AppEnvironment._(
          name: 'staging',
          apiUrl: 'https://staging-api.myapp.com',
          logLevel: 'warning',
          debug: true,
        );
      default:
        return AppEnvironment._(
          name: 'development',
          apiUrl: 'http://localhost:8080',
          logLevel: 'debug',
          debug: true,
        );
    }
  }

  void display() {
    print('  ┌─────────────────────────────────────┐');
    print('  │ 환경 설정                            │');
    print('  ├──────────┬──────────────────────────┤');
    print('  │ 환경     │ $name');
    print('  │ API URL  │ $apiUrl');
    print('  │ 로그     │ $logLevel');
    print('  │ 디버그   │ $debug');
    print('  └──────────┴──────────────────────────┘');
  }
}

void lesson4Environment() {
  print('[레슨 4] 환경 변수와 설정 관리');

  final env = AppEnvironment.fromEnv();
  env.display();

  print('  ★ 환경 변수 읽기: Platform.environment["KEY"]');
  print('  ★ 설정: APP_ENV=production dart run main.dart');
  print('');
}


// =====================================================================
// 레슨 5 — Semantic Versioning (버전 관리)
// =====================================================================
/*
★ Semantic Versioning = MAJOR.MINOR.PATCH

  ┌────────────────────────────────────────────────────────┐
  │  버전: 2.4.1                                          │
  │        ↑ ↑ ↑                                          │
  │        │ │ └─ PATCH: 버그 수정 (하위 호환)            │
  │        │ └─── MINOR: 기능 추가 (하위 호환)            │
  │        └───── MAJOR: 큰 변경 (하위 호환 깨짐!)        │
  └────────────────────────────────────────────────────────┘

★ 버전 올리기 가이드
  ┌──────────────┬──────────────────────────────────────────┐
  │ 변경 내용    │ 올리는 버전                               │
  ├──────────────┼──────────────────────────────────────────┤
  │ 버그 수정    │ 1.2.3 → 1.2.4 (PATCH)                   │
  │ 기능 추가    │ 1.2.3 → 1.3.0 (MINOR, PATCH 리셋)       │
  │ API 변경     │ 1.2.3 → 2.0.0 (MAJOR, 나머지 리셋)      │
  └──────────────┴──────────────────────────────────────────┘
*/

class SemanticVersion implements Comparable<SemanticVersion> {
  final int major;
  final int minor;
  final int patch;

  const SemanticVersion(this.major, this.minor, this.patch);

  factory SemanticVersion.parse(String version) {
    final parts = version.split('.');
    if (parts.length != 3) throw FormatException('잘못된 버전: $version');
    return SemanticVersion(
      int.parse(parts[0]),
      int.parse(parts[1]),
      int.parse(parts[2]),
    );
  }

  SemanticVersion bumpPatch() => SemanticVersion(major, minor, patch + 1);
  SemanticVersion bumpMinor() => SemanticVersion(major, minor + 1, 0);
  SemanticVersion bumpMajor() => SemanticVersion(major + 1, 0, 0);

  @override
  int compareTo(SemanticVersion other) {
    if (major != other.major) return major.compareTo(other.major);
    if (minor != other.minor) return minor.compareTo(other.minor);
    return patch.compareTo(other.patch);
  }

  @override
  String toString() => '$major.$minor.$patch';
}

void lesson5Versioning() {
  print('[레슨 5] Semantic Versioning');

  final v = SemanticVersion.parse('1.2.3');
  print('  현재 버전: $v');
  print('  버그 수정: ${v.bumpPatch()}');    // 1.2.4
  print('  기능 추가: ${v.bumpMinor()}');    // 1.3.0
  print('  큰 변경:   ${v.bumpMajor()}');    // 2.0.0

  // 버전 비교
  final versions = [
    SemanticVersion.parse('2.0.0'),
    SemanticVersion.parse('1.9.9'),
    SemanticVersion.parse('1.10.0'),
    SemanticVersion.parse('1.2.3'),
  ];
  versions.sort();
  print('  정렬: ${versions.join(' < ')}');
  print('');
}


// =====================================================================
// 레슨 6 — CI/CD 개념
// =====================================================================
/*
★ CI/CD = 코드 변경을 자동으로 빌드·테스트·배포

  CI (Continuous Integration):
  ┌──────────────────────────────────────────────────┐
  │  개발자가 코드 push                              │
  │       ↓                                          │
  │  자동으로 dart test 실행                          │
  │       ↓                                          │
  │  자동으로 dart analyze 실행                       │
  │       ↓                                          │
  │  통과하면 병합 허용, 실패하면 알림                │
  └──────────────────────────────────────────────────┘

  CD (Continuous Deployment):
  ┌──────────────────────────────────────────────────┐
  │  CI 통과                                         │
  │       ↓                                          │
  │  자동 빌드 (dart compile exe)                    │
  │       ↓                                          │
  │  자동 배포 (서버에 업로드)                        │
  └──────────────────────────────────────────────────┘

★ 인기 CI/CD 도구
  ┌────────────────┬──────────────────────────────────┐
  │ GitHub Actions │ GitHub 에서 바로 사용, 무료      │
  │ GitLab CI      │ GitLab 내장                      │
  │ Jenkins        │ 자체 서버 구축                   │
  │ CircleCI       │ 클라우드 기반                    │
  └────────────────┴──────────────────────────────────┘

★ GitHub Actions 예시 (.github/workflows/ci.yml):

  name: CI
  on: [push, pull_request]
  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: dart-lang/setup-dart@v1
        - run: dart pub get
        - run: dart analyze
        - run: dart test
*/

void lesson6CICD() {
  print('[레슨 6] CI/CD 개념');

  // CI 파이프라인 시뮬레이션
  final steps = [
    ('git push', true),
    ('dart pub get', true),
    ('dart analyze', true),
    ('dart test', true),
    ('dart compile exe', true),
    ('배포', true),
  ];

  print('  CI/CD 파이프라인 시뮬레이션:');
  for (final (step, success) in steps) {
    final icon = success ? '✅' : '❌';
    print('    $icon $step');
  }
  print('');
}


// =====================================================================
// 레슨 7 — 빌드 아티팩트 생성 시뮬레이션
// =====================================================================

void lesson7BuildArtifact() {
  print('[레슨 7] 빌드 아티팩트 생성');

  // 빌드 정보 생성
  final buildInfo = {
    'app': 'dart-study-app',
    'version': '1.0.0',
    'dartVersion': Platform.version.split(' ').first,
    'os': Platform.operatingSystem,
    'arch': Platform.version.contains('x64') ? 'x64' : 'arm64',
    'buildTime': DateTime.now().toIso8601String(),
    'mode': 'release',
  };

  print('  빌드 정보:');
  buildInfo.forEach((key, value) {
    print('    $key: $value');
  });

  print('');
  print('  빌드 명령어:');
  print('    dart compile exe main.dart -o dart-study-app');
  print('    → ${buildInfo['app']} 파일 생성');
  print('');
}


// =====================================================================
// 레슨 8 — 배포 전략과 롤백
// =====================================================================
/*
★ 배포 전략

  ┌──────────────────────────────────────────────────────────┐
  │  1. 직접 배포 (Big Bang)                                 │
  │     → 한번에 전체 교체                                   │
  │     → 간단하지만 위험                                    │
  │                                                          │
  │  2. 블루-그린 배포                                       │
  │     → 새 버전(그린)을 미리 준비                          │
  │     → 트래픽을 한번에 전환                               │
  │     → 문제 시 블루로 즉시 롤백                           │
  │                                                          │
  │  3. 카나리 배포                                          │
  │     → 전체 10% 에만 먼저 새 버전 적용                    │
  │     → 문제 없으면 점차 확대 (10% → 50% → 100%)          │
  │                                                          │
  │  4. 롤링 배포                                            │
  │     → 서버를 하나씩 순차적으로 업데이트                  │
  └──────────────────────────────────────────────────────────┘

★ 롤백 = "배포한 새 버전에 문제가 있을 때 이전 버전으로 되돌리기"
  → 이전 빌드 아티팩트를 보관해야 가능!
  → Git 태그로 버전 관리: git tag v1.0.0
*/

void lesson8DeployStrategies() {
  print('[레슨 8] 배포 전략과 롤백');

  print('  ┌────────────────┬──────────────────────────────┐');
  print('  │ 전략           │ 특징                          │');
  print('  ├────────────────┼──────────────────────────────┤');
  print('  │ Big Bang       │ 한번에 교체 (간단, 위험)      │');
  print('  │ 블루-그린      │ 새 환경 준비 후 전환          │');
  print('  │ 카나리         │ 소수에게 먼저, 점차 확대      │');
  print('  │ 롤링           │ 서버 하나씩 순차 업데이트     │');
  print('  └────────────────┴──────────────────────────────┘');
  print('');
  print('  ★ 롤백을 위해 이전 버전 빌드를 반드시 보관!');
  print('  ★ Git 태그: git tag v1.0.0 → git push --tags');
  print('');
}


// =====================================================================
// main — 전체 레슨 실행
// =====================================================================
void main() {
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('  Dart 17단계 : 빌드와 배포');
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('');

  lesson1WhatIsBuild();
  lesson2CompileCommands();
  lesson3Checklist();
  lesson4Environment();
  lesson5Versioning();
  lesson6CICD();
  lesson7BuildArtifact();
  lesson8DeployStrategies();

  print('■■■ 17단계 완료! ■■■');
}
