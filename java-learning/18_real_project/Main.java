/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Java 학습 18단계: 실전 미니 프로젝트
  ─ 학생 성적 관리 시스템 (종합 실습) ─

  [학습 목표]
  1. 지금까지 배운 모든 개념을 종합 활용한다
  2. record, 제네릭, 스트림, Optional을 실전에서 쓴다
  3. 인터페이스와 디자인 패턴을 적용한다
  4. 예외 처리와 유효성 검사를 한다
  5. 파일 입출력으로 데이터를 저장/불러온다
  6. 체계적인 코드 구조를 만든다

  ■ 컴파일: javac Main.java
  ■ 실행:   java Main

  ★ 이 프로젝트는 06~17단계의 모든 기술을 사용합니다!

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.stream.*;


// =====================================================================
// 1. 데이터 모델 (record 활용 — 10단계)
// =====================================================================
/*
★ record로 불변 데이터 모델 정의
  → 학생, 성적, 보고서를 명확한 타입으로!
*/

record Student(int id, String name, String club) {
    // ★ compact constructor로 유효성 검사 (10단계)
    Student {
        Objects.requireNonNull(name, "이름은 null일 수 없습니다");
        if (name.isBlank()) throw new IllegalArgumentException("이름은 비어있을 수 없습니다");
    }

    String toCSV() {
        return id + "," + name + "," + club;
    }

    static Student fromCSV(String line) {
        String[] parts = line.split(",", 3);
        return new Student(
                Integer.parseInt(parts[0].trim()),
                parts[1].trim(),
                parts.length > 2 ? parts[2].trim() : "없음"
        );
    }
}

record Score(int studentId, String subject, int value) {
    // ★ 유효성 검사 (08단계 예외 처리)
    Score {
        if (value < 0 || value > 100) {
            throw new IllegalArgumentException(
                    "점수는 0~100 사이여야 합니다: " + value);
        }
    }

    String grade() {
        if (value >= 90) return "A";
        if (value >= 80) return "B";
        if (value >= 70) return "C";
        if (value >= 60) return "D";
        return "F";
    }

    boolean isPassed() {
        return value >= 60;
    }

    String toCSV() {
        return studentId + "," + subject + "," + value;
    }

    static Score fromCSV(String line) {
        String[] parts = line.split(",", 3);
        return new Score(
                Integer.parseInt(parts[0].trim()),
                parts[1].trim(),
                Integer.parseInt(parts[2].trim())
        );
    }
}


// =====================================================================
// 2. 커스텀 예외 (08단계)
// =====================================================================

class StudentNotFoundException extends RuntimeException {
    StudentNotFoundException(int id) {
        super("학생을 찾을 수 없습니다 (ID: " + id + ")");
    }

    StudentNotFoundException(String name) {
        super("학생을 찾을 수 없습니다 (이름: " + name + ")");
    }
}

class DuplicateStudentException extends RuntimeException {
    DuplicateStudentException(String name) {
        super("이미 존재하는 학생입니다: " + name);
    }
}


// =====================================================================
// 3. 인터페이스 & 제네릭 (07단계)
// =====================================================================

// ★ 제네릭 저장소 인터페이스
interface Repository<T> {
    void add(T item);
    Optional<T> findById(int id);
    List<T> findAll();
    boolean remove(int id);
    int count();
}

// ★ 보고서 출력 인터페이스
interface Reportable {
    String generateReport();
}


// =====================================================================
// 4. 이벤트 시스템 — Observer 패턴 (13단계)
// =====================================================================

interface StudentEventListener {
    void onStudentAdded(Student student);
    void onScoreAdded(Score score);
}

class ConsoleLogger implements StudentEventListener {
    @Override
    public void onStudentAdded(Student student) {
        System.out.println("    [LOG] 학생 등록: " + student.name());
    }

    @Override
    public void onScoreAdded(Score score) {
        System.out.println("    [LOG] 성적 입력: 학생" + score.studentId()
                + " " + score.subject() + " " + score.value() + "점");
    }
}


// =====================================================================
// 5. 학생 저장소 — Repository 구현 (07단계 인터페이스)
// =====================================================================

class StudentRepository implements Repository<Student> {
    private final List<Student> students = new ArrayList<>();
    private final List<StudentEventListener> listeners = new ArrayList<>();

    void addListener(StudentEventListener listener) {
        listeners.add(listener);
    }

    @Override
    public void add(Student student) {
        // ★ 중복 검사
        boolean exists = students.stream()
                .anyMatch(s -> s.name().equals(student.name()));
        if (exists) throw new DuplicateStudentException(student.name());

        students.add(student);
        listeners.forEach(l -> l.onStudentAdded(student));
    }

    @Override
    public Optional<Student> findById(int id) {
        return students.stream()
                .filter(s -> s.id() == id)
                .findFirst();
    }

    public Optional<Student> findByName(String name) {
        return students.stream()
                .filter(s -> s.name().equals(name))
                .findFirst();
    }

    @Override
    public List<Student> findAll() {
        return Collections.unmodifiableList(students);
    }

    @Override
    public boolean remove(int id) {
        return students.removeIf(s -> s.id() == id);
    }

    @Override
    public int count() {
        return students.size();
    }
}


// =====================================================================
// 6. 성적 저장소
// =====================================================================

class ScoreRepository implements Repository<Score> {
    private final List<Score> scores = new ArrayList<>();
    private final List<StudentEventListener> listeners = new ArrayList<>();

    void addListener(StudentEventListener listener) {
        listeners.add(listener);
    }

    @Override
    public void add(Score score) {
        scores.add(score);
        listeners.forEach(l -> l.onScoreAdded(score));
    }

    @Override
    public Optional<Score> findById(int id) {
        return scores.stream()
                .filter(s -> s.studentId() == id)
                .findFirst();
    }

    public List<Score> findByStudentId(int studentId) {
        return scores.stream()
                .filter(s -> s.studentId() == studentId)
                .collect(Collectors.toList());
    }

    public List<Score> findBySubject(String subject) {
        return scores.stream()
                .filter(s -> s.subject().equals(subject))
                .collect(Collectors.toList());
    }

    @Override
    public List<Score> findAll() {
        return Collections.unmodifiableList(scores);
    }

    @Override
    public boolean remove(int id) {
        return scores.removeIf(s -> s.studentId() == id);
    }

    @Override
    public int count() {
        return scores.size();
    }
}


// =====================================================================
// 7. 성적 관리 서비스 — 비즈니스 로직
// =====================================================================

class GradeService {
    private final StudentRepository studentRepo;
    private final ScoreRepository scoreRepo;

    GradeService(StudentRepository studentRepo, ScoreRepository scoreRepo) {
        this.studentRepo = studentRepo;
        this.scoreRepo = scoreRepo;
    }

    // ★ 학생별 평균 점수 (09단계 스트림)
    OptionalDouble getAverageScore(int studentId) {
        return scoreRepo.findByStudentId(studentId).stream()
                .mapToInt(Score::value)
                .average();
    }

    // ★ 전체 평균 (09단계 스트림)
    OptionalDouble getOverallAverage() {
        return scoreRepo.findAll().stream()
                .mapToInt(Score::value)
                .average();
    }

    // ★ 과목별 평균 (09단계 스트림 + groupingBy)
    Map<String, Double> getAverageBySubject() {
        return scoreRepo.findAll().stream()
                .collect(Collectors.groupingBy(
                        Score::subject,
                        Collectors.averagingInt(Score::value)
                ));
    }

    // ★ 동아리별 평균 (09단계 스트림)
    Map<String, Double> getAverageByClub() {
        Map<String, Double> result = new LinkedHashMap<>();
        Map<String, List<Student>> byClub = studentRepo.findAll().stream()
                .collect(Collectors.groupingBy(Student::club));

        byClub.forEach((club, students) -> {
            double avg = students.stream()
                    .flatMapToInt(s -> scoreRepo.findByStudentId(s.id()).stream()
                            .mapToInt(Score::value))
                    .average()
                    .orElse(0);
            result.put(club, avg);
        });
        return result;
    }

    // ★ 상위 N명 학생 (09단계 스트림 + sorted)
    List<Map.Entry<Student, Double>> getTopStudents(int n) {
        return studentRepo.findAll().stream()
                .map(s -> Map.entry(s, getAverageScore(s.id()).orElse(0)))
                .sorted((a, b) -> Double.compare(b.getValue(), a.getValue()))
                .limit(n)
                .collect(Collectors.toList());
    }

    // ★ 미통과 학생 목록
    List<Student> getFailingStudents() {
        return studentRepo.findAll().stream()
                .filter(s -> {
                    var avg = getAverageScore(s.id());
                    return avg.isPresent() && avg.getAsDouble() < 60;
                })
                .collect(Collectors.toList());
    }
}


// =====================================================================
// 8. 보고서 생성 — Strategy 패턴 (13단계)
// =====================================================================

interface ReportStrategy {
    String generate(StudentRepository studentRepo, ScoreRepository scoreRepo,
                    GradeService gradeService);
}

// ─── 요약 보고서 전략 ───────────────────────────────────
class SummaryReportStrategy implements ReportStrategy {
    @Override
    public String generate(StudentRepository studentRepo, ScoreRepository scoreRepo,
                           GradeService gradeService) {
        var sb = new StringBuilder();
        sb.append("  ┌──────────────────────────────────────┐\n");
        sb.append("  │        성적 요약 보고서               │\n");
        sb.append("  ├──────────────────────────────────────┤\n");
        sb.append("  │  총 학생 수: ").append(String.format("%-23d", studentRepo.count())).append("│\n");
        sb.append("  │  총 성적 수: ").append(String.format("%-23d", scoreRepo.count())).append("│\n");

        var avg = gradeService.getOverallAverage();
        sb.append("  │  전체 평균: ").append(String.format("%-24s", avg.isPresent()
                ? String.format("%.1f점", avg.getAsDouble()) : "없음")).append("│\n");
        sb.append("  └──────────────────────────────────────┘\n");
        return sb.toString();
    }
}

// ─── 상세 보고서 전략 ───────────────────────────────────
class DetailedReportStrategy implements ReportStrategy {
    @Override
    public String generate(StudentRepository studentRepo, ScoreRepository scoreRepo,
                           GradeService gradeService) {
        var sb = new StringBuilder();
        sb.append("  ┌────────┬───────────┬──────┬──────┬──────┐\n");
        sb.append("  │ ID     │ 이름      │ 평균 │ 등급 │ 상태 │\n");
        sb.append("  ├────────┼───────────┼──────┼──────┼──────┤\n");

        for (var student : studentRepo.findAll()) {
            var avg = gradeService.getAverageScore(student.id());
            double avgVal = avg.orElse(0);
            String grade = avgVal >= 90 ? "A" : avgVal >= 80 ? "B" :
                    avgVal >= 70 ? "C" : avgVal >= 60 ? "D" : "F";
            String status = avgVal >= 60 ? "통과" : "미통과";

            sb.append(String.format("  │ %-6d │ %-8s │ %4.1f │  %s   │ %-4s │%n",
                    student.id(), student.name(), avgVal, grade, status));
        }
        sb.append("  └────────┴───────────┴──────┴──────┴──────┘\n");
        return sb.toString();
    }
}


// =====================================================================
// 9. 파일 입출력 — 데이터 저장/불러오기 (08단계)
// =====================================================================

class DataFileManager {
    private final Path dataFolder;

    DataFileManager(Path dataFolder) {
        this.dataFolder = dataFolder;
    }

    void saveStudents(List<Student> students) throws IOException {
        Files.createDirectories(dataFolder);
        Path file = dataFolder.resolve("students.csv");
        var lines = students.stream()
                .map(Student::toCSV)
                .collect(Collectors.toList());
        lines.add(0, "id,name,club");  // 헤더
        Files.write(file, lines);
    }

    void saveScores(List<Score> scores) throws IOException {
        Files.createDirectories(dataFolder);
        Path file = dataFolder.resolve("scores.csv");
        var lines = scores.stream()
                .map(Score::toCSV)
                .collect(Collectors.toList());
        lines.add(0, "studentId,subject,value");  // 헤더
        Files.write(file, lines);
    }

    List<Student> loadStudents() throws IOException {
        Path file = dataFolder.resolve("students.csv");
        if (!Files.exists(file)) return new ArrayList<>();
        return Files.readAllLines(file).stream()
                .skip(1)  // 헤더 건너뛰기
                .filter(line -> !line.isBlank())
                .map(Student::fromCSV)
                .collect(Collectors.toList());
    }

    List<Score> loadScores() throws IOException {
        Path file = dataFolder.resolve("scores.csv");
        if (!Files.exists(file)) return new ArrayList<>();
        return Files.readAllLines(file).stream()
                .skip(1)
                .filter(line -> !line.isBlank())
                .map(Score::fromCSV)
                .collect(Collectors.toList());
    }
}


// =====================================================================
//  메인 실행 — 종합 시연
// =====================================================================
public class Main {
    public static void main(String[] args) {
        System.out.println("■■■ Java 18단계: 실전 미니 프로젝트 ■■■");
        System.out.println("■■■ 학생 성적 관리 시스템 ■■■\n");

        // ─── 초기화 ─────────────────────────────────────
        var studentRepo = new StudentRepository();
        var scoreRepo = new ScoreRepository();
        var gradeService = new GradeService(studentRepo, scoreRepo);
        var fileManager = new DataFileManager(
                Path.of("java-learning", "18_real_project", "data"));

        // Observer 등록 (13단계)
        var logger = new ConsoleLogger();
        studentRepo.addListener(logger);
        scoreRepo.addListener(logger);

        // ─── 1. 학생 등록 ───────────────────────────────
        System.out.println("── 1. 학생 등록 ─────────────────────────────────");
        int id = 1;
        studentRepo.add(new Student(id++, "김철수", "축구부"));
        studentRepo.add(new Student(id++, "이영희", "미술부"));
        studentRepo.add(new Student(id++, "박민수", "축구부"));
        studentRepo.add(new Student(id++, "최지은", "과학부"));
        studentRepo.add(new Student(id++, "정하나", "미술부"));

        // 중복 등록 시도 (08단계 예외 처리)
        try {
            studentRepo.add(new Student(99, "김철수", "테스트"));
        } catch (DuplicateStudentException e) {
            System.out.println("    [ERROR] " + e.getMessage());
        }
        System.out.println("  등록된 학생 수: " + studentRepo.count());
        System.out.println();

        // ─── 2. 성적 입력 ───────────────────────────────
        System.out.println("── 2. 성적 입력 ─────────────────────────────────");
        // 국어
        scoreRepo.add(new Score(1, "국어", 92));
        scoreRepo.add(new Score(2, "국어", 78));
        scoreRepo.add(new Score(3, "국어", 55));
        scoreRepo.add(new Score(4, "국어", 88));
        scoreRepo.add(new Score(5, "국어", 95));

        // 수학
        scoreRepo.add(new Score(1, "수학", 85));
        scoreRepo.add(new Score(2, "수학", 72));
        scoreRepo.add(new Score(3, "수학", 48));
        scoreRepo.add(new Score(4, "수학", 91));
        scoreRepo.add(new Score(5, "수학", 88));

        // 영어
        scoreRepo.add(new Score(1, "영어", 90));
        scoreRepo.add(new Score(2, "영어", 82));
        scoreRepo.add(new Score(3, "영어", 60));
        scoreRepo.add(new Score(4, "영어", 75));
        scoreRepo.add(new Score(5, "영어", 98));

        // 잘못된 점수 입력 시도
        try {
            scoreRepo.add(new Score(1, "체육", 150));
        } catch (IllegalArgumentException e) {
            System.out.println("    [ERROR] " + e.getMessage());
        }
        System.out.println("  입력된 성적 수: " + scoreRepo.count());
        System.out.println();

        // ─── 3. 개별 학생 조회 (Optional 활용) ──────────
        System.out.println("── 3. 개별 학생 조회 ────────────────────────────");

        // Optional 활용 (09단계)
        studentRepo.findById(1).ifPresentOrElse(
                s -> {
                    System.out.println("  " + s.name() + " (" + s.club() + ")");
                    var scores = scoreRepo.findByStudentId(s.id());
                    scores.forEach(sc ->
                            System.out.println("    " + sc.subject() + ": "
                                    + sc.value() + "점 [" + sc.grade() + "]"));
                    gradeService.getAverageScore(s.id()).ifPresent(avg ->
                            System.out.printf("    → 평균: %.1f점%n", avg));
                },
                () -> System.out.println("  학생을 찾을 수 없습니다.")
        );

        // 없는 학생 검색
        var notFound = studentRepo.findByName("없는사람");
        System.out.println("  '없는사람' 검색: "
                + notFound.map(Student::name).orElse("없음"));
        System.out.println();

        // ─── 4. 상세 보고서 (Strategy 패턴) ─────────────
        System.out.println("── 4. 상세 보고서 ───────────────────────────────");
        ReportStrategy detailed = new DetailedReportStrategy();
        System.out.print(detailed.generate(studentRepo, scoreRepo, gradeService));
        System.out.println();

        // ─── 5. 과목별 분석 (스트림 활용) ────────────────
        System.out.println("── 5. 과목별 분석 ───────────────────────────────");
        var bySubject = gradeService.getAverageBySubject();
        System.out.println("  ┌──────────┬──────────┐");
        System.out.println("  │ 과목     │ 평균     │");
        System.out.println("  ├──────────┼──────────┤");
        bySubject.forEach((subject, avg) ->
                System.out.printf("  │ %-8s │ %6.1f   │%n", subject, avg));
        System.out.println("  └──────────┴──────────┘");
        System.out.println();

        // ─── 6. 동아리별 분석 ───────────────────────────
        System.out.println("── 6. 동아리별 분석 ─────────────────────────────");
        var byClub = gradeService.getAverageByClub();
        byClub.forEach((club, avg) ->
                System.out.printf("  %s: 평균 %.1f점%n", club, avg));
        System.out.println();

        // ─── 7. TOP 학생 & 미통과 학생 ──────────────────
        System.out.println("── 7. 성적 순위 ─────────────────────────────────");
        System.out.println("  ★ TOP 3 학생:");
        var top3 = gradeService.getTopStudents(3);
        int rank = 1;
        for (var entry : top3) {
            System.out.printf("    %d위: %s (평균 %.1f점)%n",
                    rank++, entry.getKey().name(), entry.getValue());
        }

        System.out.println("  ★ 미통과 학생:");
        var failing = gradeService.getFailingStudents();
        if (failing.isEmpty()) {
            System.out.println("    없음");
        } else {
            failing.forEach(s ->
                    System.out.printf("    - %s (평균 %.1f점)%n",
                            s.name(), gradeService.getAverageScore(s.id()).orElse(0)));
        }
        System.out.println();

        // ─── 8. 요약 보고서 ─────────────────────────────
        System.out.println("── 8. 요약 보고서 ───────────────────────────────");
        ReportStrategy summary = new SummaryReportStrategy();
        System.out.print(summary.generate(studentRepo, scoreRepo, gradeService));
        System.out.println();

        // ─── 9. 파일 저장 (08단계 File I/O) ─────────────
        System.out.println("── 9. 데이터 파일 저장 ──────────────────────────");
        try {
            fileManager.saveStudents(studentRepo.findAll());
            fileManager.saveScores(scoreRepo.findAll());
            System.out.println("  students.csv 저장 완료");
            System.out.println("  scores.csv 저장 완료");

            // 저장된 파일 내용 확인
            Path studentFile = Path.of("java-learning", "18_real_project", "data", "students.csv");
            System.out.println("  ─── students.csv 내용 ─────────");
            Files.readAllLines(studentFile).forEach(line ->
                    System.out.println("    " + line));
        } catch (IOException e) {
            System.out.println("  ★ 저장 실패: " + e.getMessage());
        }
        System.out.println();

        // ─── 10. 파일에서 불러오기 ──────────────────────
        System.out.println("── 10. 데이터 파일 불러오기 ─────────────────────");
        try {
            var loadedStudents = fileManager.loadStudents();
            var loadedScores = fileManager.loadScores();
            System.out.println("  불러온 학생 수: " + loadedStudents.size());
            System.out.println("  불러온 성적 수: " + loadedScores.size());
            loadedStudents.forEach(s ->
                    System.out.println("    " + s));
        } catch (IOException e) {
            System.out.println("  ★ 불러오기 실패: " + e.getMessage());
        }
        System.out.println();

        // ─── 종합 정리 ──────────────────────────────────
        System.out.println("── 사용된 기술 정리 ─────────────────────────────");
        System.out.println("  ┌──────────┬──────────────────────────────────┐");
        System.out.println("  │ 단계     │ 사용된 기술                      │");
        System.out.println("  ├──────────┼──────────────────────────────────┤");
        System.out.println("  │ 06단계   │ 상속, 추상 클래스               │");
        System.out.println("  │ 07단계   │ 인터페이스, 제네릭 Repository   │");
        System.out.println("  │ 08단계   │ 예외 처리, 파일 I/O (CSV)       │");
        System.out.println("  │ 09단계   │ Stream, Optional, 람다          │");
        System.out.println("  │ 10단계   │ record, var, 텍스트 블록        │");
        System.out.println("  │ 11단계   │ 유효성 검사, 방어적 프로그래밍  │");
        System.out.println("  │ 13단계   │ Strategy, Observer 패턴         │");
        System.out.println("  │ 16단계   │ 테스트 가능한 코드 구조         │");
        System.out.println("  └──────────┴──────────────────────────────────┘");
        System.out.println();

        System.out.println("■■■ 18단계 학습 완료! 모든 단계를 마쳤습니다! ■■■");
    }
}
