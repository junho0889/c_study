/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Dart 학습 18단계: 실전 미니 프로젝트
  ─ 학생 성적 관리 시스템 (CLI) ─
  ─ 입력 · 처리 · 출력 · 파일 저장 · 에러 처리 · 테스트 ─

  ■ 실행: dart run main.dart
  ■ 컴파일: dart compile exe main.dart

  ★ 지금까지 배운 모든 개념을 하나의 프로젝트에 통합합니다.
    클래스, 제네릭, null safety, 에러 처리, 파일 I/O,
    컬렉션, 패턴 등 실전에서 어떻게 조합하는지 보여줍니다.

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

import 'dart:convert';
import 'dart:math';

// =====================================================================
// 1부: 데이터 모델 (Model)
// =====================================================================
/*
★ 좋은 데이터 모델 설계 원칙

  ┌──────────────────────────────────────────────────────────┐
  │  1. 불변(immutable) 을 기본으로                          │
  │  2. 유효성 검사를 생성자에서                             │
  │  3. toString, ==, hashCode 오버라이드                    │
  │  4. JSON 직렬화/역직렬화 지원                            │
  │  5. 의미 있는 메서드 제공                                │
  └──────────────────────────────────────────────────────────┘
*/

// ── 과목 열거형 ──
enum Subject {
  korean('국어'),
  english('영어'),
  math('수학'),
  science('과학'),
  history('역사');

  final String label;
  const Subject(this.label);
}

// ── 등급 ──
class Grade {
  final String letter;
  final double minScore;

  const Grade._(this.letter, this.minScore);

  static const Grade a = Grade._('A', 90);
  static const Grade b = Grade._('B', 80);
  static const Grade c = Grade._('C', 70);
  static const Grade d = Grade._('D', 60);
  static const Grade f = Grade._('F', 0);

  static Grade fromScore(double score) {
    if (score >= 90) return a;
    if (score >= 80) return b;
    if (score >= 70) return c;
    if (score >= 60) return d;
    return f;
  }

  @override
  String toString() => letter;
}

// ── 학생 모델 ──
class Student {
  final int id;
  final String name;
  final Map<Subject, int> _scores;

  Student({
    required this.id,
    required this.name,
    Map<Subject, int>? scores,
  }) : _scores = scores ?? {} {
    // 유효성 검사
    if (name.trim().isEmpty) {
      throw ArgumentError('학생 이름은 비어있을 수 없습니다');
    }
    for (final entry in _scores.entries) {
      _validateScore(entry.value, entry.key);
    }
  }

  // ── 점수 관리 ──
  void setScore(Subject subject, int score) {
    _validateScore(score, subject);
    _scores[subject] = score;
  }

  int? getScore(Subject subject) => _scores[subject];

  Map<Subject, int> get scores => Map.unmodifiable(_scores);
  int get subjectCount => _scores.length;

  // ── 통계 계산 ──
  double get average {
    if (_scores.isEmpty) return 0;
    final total = _scores.values.reduce((a, b) => a + b);
    return total / _scores.length;
  }

  int get highestScore {
    if (_scores.isEmpty) return 0;
    return _scores.values.reduce(max);
  }

  int get lowestScore {
    if (_scores.isEmpty) return 0;
    return _scores.values.reduce(min);
  }

  Grade get grade => Grade.fromScore(average);

  String get status => average >= 60 ? '통과' : '미통과';

  // ── 유효성 검사 ──
  void _validateScore(int score, Subject subject) {
    if (score < 0 || score > 100) {
      throw RangeError('${subject.label} 점수는 0~100: $score');
    }
  }

  // ── JSON 직렬화 ──
  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'scores': {
      for (final entry in _scores.entries)
        entry.key.name: entry.value,
    },
  };

  factory Student.fromJson(Map<String, dynamic> json) {
    final scores = <Subject, int>{};
    final rawScores = json['scores'] as Map<String, dynamic>? ?? {};
    for (final entry in rawScores.entries) {
      final subject = Subject.values.firstWhere(
        (s) => s.name == entry.key,
        orElse: () => throw FormatException('알 수 없는 과목: ${entry.key}'),
      );
      scores[subject] = entry.value as int;
    }
    return Student(
      id: json['id'] as int,
      name: json['name'] as String,
      scores: scores,
    );
  }

  @override
  String toString() => 'Student($id: $name, 평균: ${average.toStringAsFixed(1)})';

  @override
  bool operator ==(Object other) =>
      other is Student && id == other.id;

  @override
  int get hashCode => id.hashCode;
}


// =====================================================================
// 2부: 서비스 레이어 (Business Logic)
// =====================================================================
/*
★ 서비스 = "데이터에 대한 비즈니스 로직을 담당"

  ┌──────────────────────────────────────────────────┐
  │  UI (표현) → Service (로직) → Model (데이터)    │
  │                                                  │
  │  UI 는 "어떻게 보여줄지" 만 담당                 │
  │  Service 는 "무엇을 계산/처리할지" 담당           │
  │  Model 은 "데이터 구조" 만 담당                   │
  └──────────────────────────────────────────────────┘
*/

class ClassroomService {
  final List<Student> _students = [];
  int _nextId = 1;

  // ── CRUD ──
  Student addStudent(String name, {Map<Subject, int>? scores}) {
    final student = Student(id: _nextId++, name: name, scores: scores);
    _students.add(student);
    return student;
  }

  bool removeStudent(int id) {
    final before = _students.length;
    _students.removeWhere((s) => s.id == id);
    return _students.length < before;
  }

  Student? findById(int id) {
    for (final s in _students) {
      if (s.id == id) return s;
    }
    return null;
  }

  List<Student> findByName(String name) {
    return _students.where((s) => s.name.contains(name)).toList();
  }

  List<Student> get allStudents => List.unmodifiable(_students);
  int get count => _students.length;

  // ── 전체 통계 ──
  double get classAverage {
    if (_students.isEmpty) return 0;
    final total = _students.fold<double>(0, (sum, s) => sum + s.average);
    return total / _students.length;
  }

  Student? get topStudent {
    if (_students.isEmpty) return null;
    return _students.reduce((a, b) => a.average >= b.average ? a : b);
  }

  Student? get bottomStudent {
    if (_students.isEmpty) return null;
    return _students.reduce((a, b) => a.average <= b.average ? a : b);
  }

  // ── 과목별 통계 ──
  Map<Subject, double> get subjectAverages {
    final totals = <Subject, int>{};
    final counts = <Subject, int>{};

    for (final student in _students) {
      for (final entry in student.scores.entries) {
        totals[entry.key] = (totals[entry.key] ?? 0) + entry.value;
        counts[entry.key] = (counts[entry.key] ?? 0) + 1;
      }
    }

    return {
      for (final subject in totals.keys)
        subject: totals[subject]! / counts[subject]!,
    };
  }

  // ── 등급 분포 ──
  Map<String, int> get gradeDistribution {
    final dist = <String, int>{'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0};
    for (final s in _students) {
      dist[s.grade.letter] = (dist[s.grade.letter] ?? 0) + 1;
    }
    return dist;
  }

  // ── 정렬 ──
  List<Student> getSortedByAverage({bool descending = true}) {
    final sorted = [..._students];
    sorted.sort((a, b) => descending
        ? b.average.compareTo(a.average)
        : a.average.compareTo(b.average));
    return sorted;
  }

  // ── JSON 직렬화/역직렬화 ──
  String toJson() {
    final data = _students.map((s) => s.toJson()).toList();
    return const JsonEncoder.withIndent('  ').convert(data);
  }

  void loadFromJson(String jsonStr) {
    final list = jsonDecode(jsonStr) as List<dynamic>;
    _students.clear();
    for (final item in list) {
      final student = Student.fromJson(item as Map<String, dynamic>);
      _students.add(student);
      if (student.id >= _nextId) _nextId = student.id + 1;
    }
  }
}


// =====================================================================
// 3부: 보고서 생성기 (Report Generator)
// =====================================================================
/*
★ 보고서 = "데이터를 사람이 읽기 좋게 정리한 것"

  ┌─────────────────────────────────────────────────────────┐
  │  ┌──────────┬──────┬──────┬──────┬──────┬──────┬──────┐ │
  │  │ 이름     │ 국어 │ 영어 │ 수학 │ 평균 │ 등급 │ 결과 │ │
  │  ├──────────┼──────┼──────┼──────┼──────┼──────┼──────┤ │
  │  │ 민수     │  92  │  88  │  95  │ 91.7 │  A   │ 통과 │ │
  │  │ 지우     │  78  │  82  │  65  │ 75.0 │  C   │ 통과 │ │
  │  └──────────┴──────┴──────┴──────┴──────┴──────┴──────┘ │
  └─────────────────────────────────────────────────────────┘
*/

class ReportGenerator {
  final ClassroomService _service;

  ReportGenerator(this._service);

  // ── 개별 학생 보고서 ──
  String studentReport(Student student) {
    final buffer = StringBuffer();
    buffer.writeln('  ┌─────────────────────────────────────┐');
    buffer.writeln('  │  학생 보고서: ${student.name.padRight(20)}│');
    buffer.writeln('  ├─────────────────────────────────────┤');

    for (final subject in Subject.values) {
      final score = student.getScore(subject);
      if (score != null) {
        final grade = Grade.fromScore(score.toDouble());
        buffer.writeln('  │  ${subject.label}: ${score.toString().padLeft(3)}점'
            '  (${grade.letter})${' ' * 18}│');
      }
    }

    buffer.writeln('  ├─────────────────────────────────────┤');
    buffer.writeln('  │  평균: ${student.average.toStringAsFixed(1).padLeft(5)}점'
        '  등급: ${student.grade}  ${student.status.padRight(10)}│');
    buffer.writeln('  └─────────────────────────────────────┘');
    return buffer.toString();
  }

  // ── 전체 성적표 ──
  String classReport() {
    final buffer = StringBuffer();
    final sorted = _service.getSortedByAverage();

    buffer.writeln('  ╔════════════════════════════════════════════════════════╗');
    buffer.writeln('  ║          학급 성적 보고서                              ║');
    buffer.writeln('  ╠════════════════════════════════════════════════════════╣');

    // 헤더
    buffer.write('  ║ 순위 │ 이름   │');
    for (final s in Subject.values) {
      buffer.write(' ${s.label} │');
    }
    buffer.writeln(' 평균  │ 등급 ║');
    buffer.writeln('  ╟──────┼────────┼──────┼──────┼──────┼──────┼──────┼───────┼──────╢');

    // 데이터 행
    for (var i = 0; i < sorted.length; i++) {
      final s = sorted[i];
      buffer.write('  ║ ${(i + 1).toString().padLeft(3)}  │ ${s.name.padRight(6)} │');
      for (final sub in Subject.values) {
        final score = s.getScore(sub);
        buffer.write(' ${score?.toString().padLeft(3) ?? '  -'} │');
      }
      buffer.write(' ${s.average.toStringAsFixed(1).padLeft(5)} │');
      buffer.writeln('  ${s.grade}   ║');
    }

    buffer.writeln('  ╠════════════════════════════════════════════════════════╣');
    buffer.writeln('  ║  학급 평균: ${_service.classAverage.toStringAsFixed(1)}점'
        '${' ' * 36}║');

    final top = _service.topStudent;
    if (top != null) {
      buffer.writeln('  ║  최우수:   ${top.name} '
          '(${top.average.toStringAsFixed(1)}점)'
          '${' ' * 30}║');
    }

    buffer.writeln('  ╚════════════════════════════════════════════════════════╝');
    return buffer.toString();
  }

  // ── 과목별 통계 ──
  String subjectReport() {
    final buffer = StringBuffer();
    final avgs = _service.subjectAverages;

    buffer.writeln('  ┌──────────────────────────────────┐');
    buffer.writeln('  │  과목별 평균                      │');
    buffer.writeln('  ├────────┬─────────┬───────────────┤');

    for (final entry in avgs.entries) {
      final bar = '█' * (entry.value ~/ 5);  // 간단한 막대 그래프
      buffer.writeln('  │ ${entry.key.label.padRight(4)} │'
          ' ${entry.value.toStringAsFixed(1).padLeft(5)}점 │'
          ' $bar');
    }

    buffer.writeln('  └────────┴─────────┴───────────────┘');
    return buffer.toString();
  }

  // ── 등급 분포 ──
  String gradeDistributionReport() {
    final buffer = StringBuffer();
    final dist = _service.gradeDistribution;
    final total = _service.count;

    buffer.writeln('  ┌─────────────────────────────────┐');
    buffer.writeln('  │  등급 분포                       │');
    buffer.writeln('  ├───────┬───────┬─────────────────┤');

    for (final entry in dist.entries) {
      final pct = total > 0
          ? (entry.value / total * 100).toStringAsFixed(0)
          : '0';
      final bar = '■' * entry.value;
      buffer.writeln('  │   ${entry.key}   │ ${entry.value.toString().padLeft(3)}명'
          ' │ ${pct.padLeft(3)}% $bar');
    }

    buffer.writeln('  └───────┴───────┴─────────────────┘');
    return buffer.toString();
  }
}


// =====================================================================
// 4부: 자체 테스트
// =====================================================================

int _passed = 0;
int _failed = 0;

void _check(bool condition, String description) {
  if (condition) {
    _passed++;
    print('    ✅ $description');
  } else {
    _failed++;
    print('    ❌ $description');
  }
}

void _checkThrows(void Function() fn, String description) {
  try {
    fn();
    _failed++;
    print('    ❌ $description (예외 미발생)');
  } catch (e) {
    _passed++;
    print('    ✅ $description');
  }
}

void runSelfTests() {
  print('[자체 테스트] 프로젝트 코드 검증');
  print('');

  // ── Student 모델 테스트 ──
  print('  -- Student 모델 --');

  final s = Student(id: 1, name: '테스트', scores: {
    Subject.korean: 90,
    Subject.english: 80,
    Subject.math: 70,
  });

  _check(s.average == 80, '평균 계산: ${s.average}');
  _check(s.highestScore == 90, '최고점: ${s.highestScore}');
  _check(s.lowestScore == 70, '최저점: ${s.lowestScore}');
  _check(s.grade.letter == 'B', '등급: ${s.grade}');
  _check(s.status == '통과', '상태: ${s.status}');

  // 유효성 검사
  _checkThrows(
    () => Student(id: 2, name: '', scores: {}),
    '빈 이름 에러',
  );
  _checkThrows(
    () => Student(id: 3, name: '테스트', scores: {Subject.korean: 150}),
    '100 초과 점수 에러',
  );
  _checkThrows(
    () => Student(id: 4, name: '테스트', scores: {Subject.math: -10}),
    '음수 점수 에러',
  );

  // JSON 직렬화
  final json = s.toJson();
  final restored = Student.fromJson(json);
  _check(restored.name == s.name, 'JSON 이름 복원');
  _check(restored.average == s.average, 'JSON 평균 복원');

  print('');

  // ── Service 테스트 ──
  print('  -- ClassroomService --');

  final service = ClassroomService();
  service.addStudent('A', scores: {Subject.korean: 100, Subject.english: 100});
  service.addStudent('B', scores: {Subject.korean: 50, Subject.english: 50});

  _check(service.count == 2, '학생 수: ${service.count}');
  _check(service.classAverage == 75, '학급 평균: ${service.classAverage}');
  _check(service.topStudent?.name == 'A', '최우수: ${service.topStudent?.name}');
  _check(service.bottomStudent?.name == 'B', '최하위: ${service.bottomStudent?.name}');

  // JSON 전체 직렬화
  final jsonStr = service.toJson();
  final service2 = ClassroomService();
  service2.loadFromJson(jsonStr);
  _check(service2.count == 2, 'JSON 로드 후 학생 수');
  _check(service2.classAverage == 75, 'JSON 로드 후 평균');

  print('');
  print('  결과: $_passed 통과, $_failed 실패');
  if (_failed == 0) print('  🎉 모든 테스트 통과!');
  print('');
}


// =====================================================================
// 5부: 메인 실행 — 전체 시연
// =====================================================================

void main() {
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('  Dart 18단계 : 실전 미니 프로젝트 — 학생 성적 관리 시스템');
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('');

  // ── 1. 서비스 초기화 & 데이터 입력 ──
  print('[1단계] 데이터 입력');
  final service = ClassroomService();

  service.addStudent('김민수', scores: {
    Subject.korean: 92, Subject.english: 88,
    Subject.math: 95, Subject.science: 90, Subject.history: 85,
  });
  service.addStudent('이지우', scores: {
    Subject.korean: 78, Subject.english: 82,
    Subject.math: 65, Subject.science: 72, Subject.history: 88,
  });
  service.addStudent('박서연', scores: {
    Subject.korean: 100, Subject.english: 97,
    Subject.math: 98, Subject.science: 95, Subject.history: 99,
  });
  service.addStudent('최준호', scores: {
    Subject.korean: 55, Subject.english: 60,
    Subject.math: 48, Subject.science: 52, Subject.history: 65,
  });
  service.addStudent('정하늘', scores: {
    Subject.korean: 88, Subject.english: 92,
    Subject.math: 85, Subject.science: 80, Subject.history: 90,
  });

  print('  ${service.count}명의 학생 데이터 입력 완료');
  for (final s in service.allStudents) {
    print('    $s');
  }
  print('');

  // ── 2. 보고서 생성 ──
  print('[2단계] 보고서 생성');
  final report = ReportGenerator(service);

  // 전체 성적표
  print(report.classReport());

  // 개별 보고서 (최우수 학생)
  final top = service.topStudent;
  if (top != null) {
    print('  ★ 최우수 학생 상세:');
    print(report.studentReport(top));
  }

  // 과목별 통계
  print(report.subjectReport());

  // 등급 분포
  print(report.gradeDistributionReport());

  // ── 3. JSON 저장/복원 ──
  print('[3단계] JSON 직렬화 테스트');
  final jsonStr = service.toJson();
  print('  JSON 길이: ${jsonStr.length} 문자');
  print('  첫 100자: ${jsonStr.substring(0, min(100, jsonStr.length))}...');

  final restored = ClassroomService();
  restored.loadFromJson(jsonStr);
  print('  복원된 학생 수: ${restored.count}');
  print('  복원된 학급 평균: ${restored.classAverage.toStringAsFixed(1)}');
  print('');

  // ── 4. 검색 기능 ──
  print('[4단계] 검색 기능');
  final found = service.findByName('김');
  print('  "김" 검색 결과: ${found.map((s) => s.name).toList()}');

  final byId = service.findById(3);
  print('  ID 3 검색: ${byId?.name ?? '없음'}');
  print('');

  // ── 5. 자체 테스트 실행 ──
  runSelfTests();

  print('■■■ 18단계 완료! Dart 학습 전 과정 완료! ■■■');
  print('');
  print('  ★ 다음 단계 추천:');
  print('    1. Flutter 앱 개발 (flutter create my_app)');
  print('    2. 서버 개발 (shelf, dart_frog 패키지)');
  print('    3. pub.dev 에 자신만의 패키지 배포');
  print('    4. 오픈소스 프로젝트 기여');
}
