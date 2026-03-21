/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Dart 학습 10단계: 파일 입출력 (File I/O)
  ─ 파일 읽기/쓰기 · 동기/비동기 · 디렉토리 · JSON · CSV ─

  ■ 실행: dart run main.dart
  ■ 컴파일: dart compile exe main.dart

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

import 'dart:io';
import 'dart:convert';

// =====================================================================
// 레슨 1 — 파일이 뭘까?
// =====================================================================
/*
★ 파일 = "프로그램이 꺼져도 남아 있는 저장 공간"

  비유: 공책
  ┌──────────────────────────────────────────────────┐
  │  메모리(RAM) = 칠판                              │
  │    → 수업 끝나면 지워짐 (프로그램 종료 시 소멸)  │
  │                                                  │
  │  파일(디스크) = 공책                              │
  │    → 집에 가져가도 남아 있음 (프로그램 꺼져도 유지)│
  └──────────────────────────────────────────────────┘

★ Dart 파일 I/O 클래스 (dart:io)
  ┌──────────────┬──────────────────────────────────────┐
  │ 클래스       │ 역할                                  │
  ├──────────────┼──────────────────────────────────────┤
  │ File         │ 파일 읽기/쓰기/삭제                   │
  │ Directory    │ 디렉토리 생성/목록/삭제               │
  │ FileSystemEntity│ File, Directory 의 공통 부모       │
  │ IOSink       │ 파일에 점진적으로 쓰기                │
  │ stdin/stdout │ 표준 입출력 (콘솔)                    │
  └──────────────┴──────────────────────────────────────┘

★ 주의: dart:io 는 CLI/서버에서만 사용 가능!
  Flutter 웹에서는 사용 불가 (dart:html 사용)
*/

// 테스트용 디렉토리 경로
final _testDir = 'dart-learning/10_file_io/_test_output';

Future<void> lesson1BasicFileWrite() async {
  print('[레슨 1] 파일 쓰기 기본');

  // 디렉토리 생성 (없으면)
  await Directory(_testDir).create(recursive: true);

  // ── 비동기 쓰기 ──
  final file = File('$_testDir/hello.txt');
  await file.writeAsString('안녕하세요!\nDart 파일 I/O 학습 중입니다.\n');
  print('  비동기 쓰기 완료: ${file.path}');

  // ── 동기 쓰기 ──
  final syncFile = File('$_testDir/sync_hello.txt');
  syncFile.writeAsStringSync('동기 방식으로 작성된 파일입니다.\n');
  print('  동기 쓰기 완료: ${syncFile.path}');

  // ── 파일 존재 확인 ──
  print('  hello.txt 존재? ${await file.exists()}');
  print('');
}


// =====================================================================
// 레슨 2 — 파일 읽기
// =====================================================================
/*
★ 파일 읽기 방법들

  ┌─────────────────────┬──────────────────────────────────┐
  │ 메서드              │ 반환 타입                         │
  ├─────────────────────┼──────────────────────────────────┤
  │ readAsString()      │ Future<String> (전체를 문자열)    │
  │ readAsLines()       │ Future<List<String>> (줄별 리스트)│
  │ readAsBytes()       │ Future<List<int>> (바이트 배열)   │
  │ readAsStringSync()  │ String (동기)                    │
  │ readAsLinesSync()   │ List<String> (동기)              │
  └─────────────────────┴──────────────────────────────────┘
*/

Future<void> lesson2FileRead() async {
  print('[레슨 2] 파일 읽기');

  final file = File('$_testDir/hello.txt');

  // ── 전체 문자열로 읽기 ──
  final content = await file.readAsString();
  print('  전체 내용:');
  print('    $content');

  // ── 줄별로 읽기 ──
  final lines = await file.readAsLines();
  print('  줄 수: ${lines.length}');
  for (var i = 0; i < lines.length; i++) {
    print('    [$i] ${lines[i]}');
  }

  // ── 파일 크기 확인 ──
  final stat = await file.stat();
  print('  파일 크기: ${stat.size} bytes');
  print('  수정 시간: ${stat.modified}');
  print('');
}


// =====================================================================
// 레슨 3 — 파일 추가 쓰기와 모드
// =====================================================================
/*
★ 쓰기 모드

  ┌──────────────┬──────────────────────────────────────┐
  │ 모드         │ 동작                                  │
  ├──────────────┼──────────────────────────────────────┤
  │ write (기본) │ 기존 내용 지우고 새로 씀              │
  │ append       │ 기존 내용 뒤에 추가                   │
  │ writeOnly    │ 쓰기 전용 (읽기 불가)                 │
  └──────────────┴──────────────────────────────────────┘

  ★ 비유: 노트에 글쓰기
  - write = 새 페이지에 쓰기 (이전 내용 삭제)
  - append = 기존 페이지 끝에 이어 쓰기
*/

Future<void> lesson3AppendAndModes() async {
  print('[레슨 3] 파일 추가 쓰기');

  final logFile = File('$_testDir/log.txt');

  // ── write 모드: 기존 내용 덮어씀 ──
  await logFile.writeAsString('첫 번째 로그\n');
  print('  write: ${await logFile.readAsString()}');

  // ── append 모드: 끝에 추가 ──
  await logFile.writeAsString(
    '두 번째 로그\n',
    mode: FileMode.append,
  );
  await logFile.writeAsString(
    '세 번째 로그\n',
    mode: FileMode.append,
  );
  print('  append 후 전체:');
  final lines = await logFile.readAsLines();
  for (final line in lines) {
    print('    $line');
  }

  // ── IOSink 로 효율적 쓰기 (대량 데이터) ──
  final sink = logFile.openWrite(mode: FileMode.append);
  for (var i = 4; i <= 6; i++) {
    sink.writeln('$i번째 로그 (IOSink)');
  }
  await sink.flush();
  await sink.close();

  print('  IOSink 후 줄 수: ${(await logFile.readAsLines()).length}');
  print('');
}


// =====================================================================
// 레슨 4 — 디렉토리 다루기
// =====================================================================
/*
★ Directory 클래스

  ┌──────────────────────┬────────────────────────────────┐
  │ 메서드               │ 동작                           │
  ├──────────────────────┼────────────────────────────────┤
  │ create(recursive:)   │ 디렉토리 생성                  │
  │ exists()             │ 존재 여부 확인                  │
  │ list()               │ 하위 파일/디렉토리 목록         │
  │ delete(recursive:)   │ 삭제 (recursive=true면 하위도)  │
  │ rename(newPath)      │ 이름 변경 / 이동                │
  └──────────────────────┴────────────────────────────────┘
*/

Future<void> lesson4Directory() async {
  print('[레슨 4] 디렉토리 다루기');

  // ── 디렉토리 생성 ──
  final subDir = Directory('$_testDir/sub_folder');
  await subDir.create(recursive: true);
  print('  디렉토리 생성: ${subDir.path}');

  // 하위 파일 생성
  await File('${subDir.path}/a.txt').writeAsString('파일 A');
  await File('${subDir.path}/b.txt').writeAsString('파일 B');

  // ── 디렉토리 목록 ──
  final parentDir = Directory(_testDir);
  print('  $_testDir 내용물:');
  await for (final entity in parentDir.list()) {
    final type = entity is File ? '파일' : '폴더';
    final name = entity.path.split(Platform.pathSeparator).last;
    print('    [$type] $name');
  }

  // ── 현재 작업 디렉토리 ──
  print('  현재 디렉토리: ${Directory.current.path}');
  print('');
}


// =====================================================================
// 레슨 5 — JSON 파일 읽기/쓰기
// =====================================================================
/*
★ JSON = 데이터를 주고받는 표준 형식

  ┌──────────────────────────────────────────────────────┐
  │  Dart 맵 → jsonEncode → JSON 문자열 → 파일 저장     │
  │  파일 읽기 → JSON 문자열 → jsonDecode → Dart 맵     │
  └──────────────────────────────────────────────────────┘

★ dart:convert 패키지 사용
  - jsonEncode(object) → String
  - jsonDecode(string) → dynamic
*/

Future<void> lesson5JsonFile() async {
  print('[레슨 5] JSON 파일 읽기/쓰기');

  // ── JSON 쓰기 ──
  final students = [
    {'name': '민수', 'score': 92, 'grade': 'A'},
    {'name': '지우', 'score': 78, 'grade': 'C'},
    {'name': '서연', 'score': 100, 'grade': 'A'},
  ];

  final jsonFile = File('$_testDir/students.json');
  final encoder = const JsonEncoder.withIndent('  ');
  await jsonFile.writeAsString(encoder.convert(students));
  print('  JSON 파일 저장 완료');

  // ── JSON 읽기 ──
  final content = await jsonFile.readAsString();
  final decoded = jsonDecode(content) as List<dynamic>;

  print('  읽은 학생 수: ${decoded.length}');
  for (final student in decoded) {
    final s = student as Map<String, dynamic>;
    print('    ${s['name']}: ${s['score']}점 (${s['grade']})');
  }
  print('');
}


// =====================================================================
// 레슨 6 — CSV 파일 다루기
// =====================================================================
/*
★ CSV = Comma-Separated Values (쉼표로 구분된 값)

  ┌──────────────────────────────────────────────┐
  │  이름,점수,등급                               │
  │  민수,92,A                                    │
  │  지우,78,C                                    │
  │  서연,100,A                                   │
  └──────────────────────────────────────────────┘

★ 간단한 CSV 는 직접 파싱 가능
  복잡한 경우 csv 패키지 사용 권장
*/

Future<void> lesson6CsvFile() async {
  print('[레슨 6] CSV 파일 다루기');

  // ── CSV 쓰기 ──
  final csvFile = File('$_testDir/students.csv');
  final buffer = StringBuffer();
  buffer.writeln('이름,점수,등급');
  buffer.writeln('민수,92,A');
  buffer.writeln('지우,78,C');
  buffer.writeln('서연,100,A');
  buffer.writeln('준호,65,D');
  await csvFile.writeAsString(buffer.toString());
  print('  CSV 파일 저장 완료');

  // ── CSV 읽기 ──
  final lines = await csvFile.readAsLines();
  final header = lines.first.split(',');
  print('  헤더: $header');

  print('  데이터:');
  for (var i = 1; i < lines.length; i++) {
    if (lines[i].trim().isEmpty) continue;
    final cols = lines[i].split(',');
    print('    ${cols[0]} | ${cols[1]} | ${cols[2]}');
  }

  // ── CSV → Map 변환 ──
  final records = <Map<String, String>>[];
  for (var i = 1; i < lines.length; i++) {
    if (lines[i].trim().isEmpty) continue;
    final cols = lines[i].split(',');
    records.add({
      for (var j = 0; j < header.length; j++) header[j]: cols[j],
    });
  }
  print('  Map 변환: $records');
  print('');
}


// =====================================================================
// 레슨 7 — 에러 처리와 안전한 파일 작업
// =====================================================================
/*
★ 파일 작업에서 자주 발생하는 에러

  ┌───────────────────────┬──────────────────────────────┐
  │ 에러                  │ 원인                          │
  ├───────────────────────┼──────────────────────────────┤
  │ FileSystemException   │ 파일 없음, 권한 부족, 경로 오류│
  │ PathNotFoundException │ 경로가 존재하지 않음           │
  │ FormatException       │ JSON 파싱 실패                │
  └───────────────────────┴──────────────────────────────┘

★ 안전한 파일 작업 패턴
  1. exists() 로 먼저 확인
  2. try/catch 로 감싸기
  3. 임시 파일에 쓰고 성공 시 이름 변경 (원자적 쓰기)
*/

Future<void> lesson7SafeFileOps() async {
  print('[레슨 7] 안전한 파일 작업');

  // ── 존재하지 않는 파일 읽기 시도 ──
  try {
    final missing = File('$_testDir/없는파일.txt');
    await missing.readAsString();
  } on PathNotFoundException catch (e) {
    print('  PathNotFound: $e');
  } catch (e) {
    print('  에러: $e');
  }

  // ── 안전한 읽기 패턴 ──
  Future<String> safeRead(String path) async {
    final file = File(path);
    if (!await file.exists()) {
      return '(파일 없음)';
    }
    return file.readAsString();
  }

  final content = await safeRead('$_testDir/hello.txt');
  print('  안전한 읽기: ${content.substring(0, 10)}...');

  final missing = await safeRead('$_testDir/xxx.txt');
  print('  없는 파일: $missing');

  // ── 임시 파일 패턴 (원자적 쓰기) ──
  final targetFile = File('$_testDir/important.txt');
  final tempFile = File('$_testDir/important.txt.tmp');

  await tempFile.writeAsString('중요한 데이터\n');
  if (await targetFile.exists()) {
    await targetFile.delete();
  }
  await tempFile.rename(targetFile.path);
  print('  원자적 쓰기 완료: ${await targetFile.readAsString()}');
  print('');
}


// =====================================================================
// 레슨 8 — 정리 (테스트 파일 삭제)
// =====================================================================

Future<void> lesson8Cleanup() async {
  print('[레슨 8] 테스트 파일 정리');

  final dir = Directory(_testDir);
  if (await dir.exists()) {
    await dir.delete(recursive: true);
    print('  $_testDir 삭제 완료');
  } else {
    print('  정리할 파일 없음');
  }
  print('');
}


// =====================================================================
// main — 전체 레슨 실행
// =====================================================================
Future<void> main() async {
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('  Dart 10단계 : 파일 입출력 (File I/O)');
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('');

  await lesson1BasicFileWrite();
  await lesson2FileRead();
  await lesson3AppendAndModes();
  await lesson4Directory();
  await lesson5JsonFile();
  await lesson6CsvFile();
  await lesson7SafeFileOps();
  await lesson8Cleanup();

  print('■■■ 10단계 완료! ■■■');
}
