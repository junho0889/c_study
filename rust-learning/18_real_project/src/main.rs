/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Rust 학습 18단계: 실전 미니 프로젝트
  ─ 학생 성적 관리 시스템 (전 단계 종합) ─

  [학습 목표]
  1. 지금까지 배운 모든 개념을 하나의 프로젝트에 통합한다
  2. 구조체, 열거형, 트레이트, 에러 처리를 실전에서 조합한다
  3. 이터레이터 체이닝으로 데이터를 처리한다
  4. 모듈 구조로 코드를 정리한다
  5. 테스트와 함께 개발하는 습관을 체험한다

  ■ 실행: cargo run
  ■ 테스트: cargo test
  ■ 빌드: cargo build --release

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

use std::fmt;
use std::collections::HashMap;

// =====================================================================
// 1. 데이터 모델: 열거형과 구조체
// =====================================================================
/*
★ 실전 프로젝트에서는 먼저 데이터 모델을 설계합니다

  ┌──────────────────────────────────────────────────────────┐
  │ Student       → 학생 정보 (이름, 학년, 과목별 점수)      │
  │ Subject       → 과목 (국어, 영어, 수학, 과학)           │
  │ Grade         → 등급 (A ~ F)                            │
  │ ReportCard    → 성적표 (학생별 분석 결과)               │
  │ ClassReport   → 반 전체 분석 보고서                     │
  └──────────────────────────────────────────────────────────┘
*/

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
enum Subject {
    Korean,
    English,
    Math,
    Science,
}

impl Subject {
    fn name(&self) -> &str {
        match self {
            Subject::Korean  => "국어",
            Subject::English => "영어",
            Subject::Math    => "수학",
            Subject::Science => "과학",
        }
    }

    fn all() -> &'static [Subject] {
        &[Subject::Korean, Subject::English, Subject::Math, Subject::Science]
    }
}

impl fmt::Display for Subject {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.name())
    }
}

#[derive(Debug, Clone, Copy, PartialEq)]
enum Grade {
    A, B, C, D, F,
}

impl Grade {
    fn from_score(score: i32) -> Self {
        match score {
            90..=100 => Grade::A,
            80..=89  => Grade::B,
            70..=79  => Grade::C,
            60..=69  => Grade::D,
            _        => Grade::F,
        }
    }

    fn description(&self) -> &str {
        match self {
            Grade::A => "우수",
            Grade::B => "양호",
            Grade::C => "보통",
            Grade::D => "노력 필요",
            Grade::F => "미달",
        }
    }
}

impl fmt::Display for Grade {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:?}({})", self, self.description())
    }
}

// =====================================================================
// 2. Student 구조체와 메서드
// =====================================================================

#[derive(Debug, Clone)]
struct Student {
    name: String,
    grade_level: u32,     // 학년
    scores: HashMap<Subject, i32>,
}

impl Student {
    fn new(name: &str, grade_level: u32) -> Self {
        Student {
            name: name.to_string(),
            grade_level,
            scores: HashMap::new(),
        }
    }

    fn add_score(&mut self, subject: Subject, score: i32) -> Result<(), String> {
        if !(0..=100).contains(&score) {
            return Err(format!("점수는 0~100 사이여야 합니다: {}", score));
        }
        self.scores.insert(subject, score);
        Ok(())
    }

    fn get_score(&self, subject: &Subject) -> Option<i32> {
        self.scores.get(subject).copied()
    }

    fn average(&self) -> Option<f64> {
        if self.scores.is_empty() {
            return None;
        }
        let total: i32 = self.scores.values().sum();
        Some(total as f64 / self.scores.len() as f64)
    }

    fn overall_grade(&self) -> Option<Grade> {
        self.average().map(|avg| Grade::from_score(avg as i32))
    }

    fn highest_subject(&self) -> Option<(Subject, i32)> {
        self.scores.iter()
            .max_by_key(|(_, &score)| score)
            .map(|(&subj, &score)| (subj, score))
    }

    fn lowest_subject(&self) -> Option<(Subject, i32)> {
        self.scores.iter()
            .min_by_key(|(_, &score)| score)
            .map(|(&subj, &score)| (subj, score))
    }

    fn is_passing(&self) -> bool {
        self.scores.values().all(|&s| s >= 60)
    }

    fn failing_subjects(&self) -> Vec<Subject> {
        self.scores.iter()
            .filter(|(_, &score)| score < 60)
            .map(|(&subj, _)| subj)
            .collect()
    }
}

impl fmt::Display for Student {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}({}학년)", self.name, self.grade_level)
    }
}

// =====================================================================
// 3. 성적표 트레이트
// =====================================================================

trait Reportable {
    fn generate_report(&self) -> String;
    fn summary_line(&self) -> String;
}

impl Reportable for Student {
    fn generate_report(&self) -> String {
        let mut report = format!("┌─── {} 성적표 ───┐\n", self);
        report.push_str("│                              │\n");

        for subject in Subject::all() {
            if let Some(score) = self.get_score(subject) {
                let grade = Grade::from_score(score);
                report.push_str(&format!("│  {:>4}: {:>3}점 → {:>2}       │\n",
                    subject.name(), score, format!("{:?}", grade)));
            }
        }

        if let Some(avg) = self.average() {
            report.push_str("│                              │\n");
            report.push_str(&format!("│  평균: {:.1}점               │\n", avg));
            if let Some(grade) = self.overall_grade() {
                report.push_str(&format!("│  종합: {}                │\n", grade));
            }
        }

        if !self.is_passing() {
            let failing = self.failing_subjects();
            let names: Vec<&str> = failing.iter().map(|s| s.name()).collect();
            report.push_str(&format!("│  ★ 보충 필요: {}       │\n", names.join(", ")));
        }

        report.push_str("└──────────────────────────────┘");
        report
    }

    fn summary_line(&self) -> String {
        let avg = self.average().unwrap_or(0.0);
        let grade = self.overall_grade()
            .map(|g| format!("{:?}", g))
            .unwrap_or_else(|| "-".to_string());
        let status = if self.is_passing() { "통과" } else { "보충" };
        format!("{:>6} │ {:>5.1} │ {:>2} │ {}", self.name, avg, grade, status)
    }
}

// =====================================================================
// 4. 반(ClassRoom) 구조체
// =====================================================================

struct ClassRoom {
    name: String,
    students: Vec<Student>,
}

impl ClassRoom {
    fn new(name: &str) -> Self {
        ClassRoom {
            name: name.to_string(),
            students: Vec::new(),
        }
    }

    fn add_student(&mut self, student: Student) {
        self.students.push(student);
    }

    fn find_student(&self, name: &str) -> Option<&Student> {
        self.students.iter().find(|s| s.name == name)
    }

    fn class_average(&self) -> Option<f64> {
        let averages: Vec<f64> = self.students.iter()
            .filter_map(|s| s.average())
            .collect();
        if averages.is_empty() {
            return None;
        }
        Some(averages.iter().sum::<f64>() / averages.len() as f64)
    }

    fn top_students(&self, n: usize) -> Vec<&Student> {
        let mut sorted: Vec<&Student> = self.students.iter().collect();
        sorted.sort_by(|a, b| {
            let avg_b = b.average().unwrap_or(0.0);
            let avg_a = a.average().unwrap_or(0.0);
            avg_b.partial_cmp(&avg_a).unwrap()
        });
        sorted.into_iter().take(n).collect()
    }

    fn subject_average(&self, subject: &Subject) -> Option<f64> {
        let scores: Vec<i32> = self.students.iter()
            .filter_map(|s| s.get_score(subject))
            .collect();
        if scores.is_empty() {
            return None;
        }
        Some(scores.iter().sum::<i32>() as f64 / scores.len() as f64)
    }

    fn failing_students(&self) -> Vec<&Student> {
        self.students.iter()
            .filter(|s| !s.is_passing())
            .collect()
    }

    fn grade_distribution(&self) -> HashMap<Grade, usize> {
        let mut dist = HashMap::new();
        for student in &self.students {
            if let Some(grade) = student.overall_grade() {
                *dist.entry(grade).or_insert(0) += 1;
            }
        }
        dist
    }
}

// =====================================================================
// 5. 보고서 생성
// =====================================================================

fn print_class_report(classroom: &ClassRoom) {
    println!("  ╔══════════════════════════════════════════════╗");
    println!("  ║  {} 성적 보고서                         ║", classroom.name);
    println!("  ╚══════════════════════════════════════════════╝");
    println!();

    // ── 개인별 요약 ──
    println!("  ┌────────┬───────┬────┬──────┐");
    println!("  │ 이름   │ 평균  │등급│ 상태 │");
    println!("  ├────────┼───────┼────┼──────┤");
    for student in &classroom.students {
        println!("  │{}", student.summary_line());
    }
    println!("  └────────┴───────┴────┴──────┘");
    println!();

    // ── 과목별 평균 ──
    println!("  [과목별 반 평균]");
    for subject in Subject::all() {
        if let Some(avg) = classroom.subject_average(subject) {
            let bar_len = (avg / 5.0) as usize;
            let bar: String = "█".repeat(bar_len);
            println!("    {:>4}: {:>5.1}점 {}", subject.name(), avg, bar);
        }
    }
    println!();

    // ── 반 전체 평균 ──
    if let Some(avg) = classroom.class_average() {
        println!("  [반 전체 평균] {:.1}점", avg);
    }
    println!();

    // ── 상위 3명 ──
    let top3 = classroom.top_students(3);
    println!("  [상위 3명]");
    for (i, student) in top3.iter().enumerate() {
        let avg = student.average().unwrap_or(0.0);
        println!("    {}등: {} ({:.1}점)", i + 1, student.name, avg);
    }
    println!();

    // ── 등급 분포 ──
    let dist = classroom.grade_distribution();
    println!("  [등급 분포]");
    for grade in &[Grade::A, Grade::B, Grade::C, Grade::D, Grade::F] {
        let count = dist.get(grade).unwrap_or(&0);
        let bar: String = "●".repeat(*count);
        println!("    {:?}: {} ({}명)", grade, bar, count);
    }
    println!();

    // ── 보충 대상 ──
    let failing = classroom.failing_students();
    if failing.is_empty() {
        println!("  [보충 대상] 없음! 전원 통과!");
    } else {
        println!("  [보충 대상]");
        for student in &failing {
            let subjects: Vec<&str> = student.failing_subjects()
                .iter().map(|s| s.name()).collect();
            println!("    {} → 보충 과목: {}", student.name, subjects.join(", "));
        }
    }
    println!();
}

// =====================================================================
// 6. 개인 성적표 출력
// =====================================================================

fn print_individual_reports(classroom: &ClassRoom) {
    println!("  ══════════════════════════════════════════");
    println!("   개인 성적표");
    println!("  ══════════════════════════════════════════");
    println!();

    for student in &classroom.students {
        println!("{}", student.generate_report());
        println!();
    }
}

// =====================================================================
// 7. 데이터 분석 함수들
// =====================================================================

fn analyze_subject_difficulty(classroom: &ClassRoom) {
    println!("  [과목 난이도 분석]");

    let mut subject_stats: Vec<(Subject, f64)> = Subject::all().iter()
        .filter_map(|&subj| {
            classroom.subject_average(&subj).map(|avg| (subj, avg))
        })
        .collect();

    subject_stats.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap());

    println!("    가장 어려운 과목: {} (평균 {:.1}점)",
             subject_stats.first().map(|(s, _)| s.name()).unwrap_or("-"),
             subject_stats.first().map(|(_, a)| *a).unwrap_or(0.0));
    println!("    가장 쉬운 과목:   {} (평균 {:.1}점)",
             subject_stats.last().map(|(s, _)| s.name()).unwrap_or("-"),
             subject_stats.last().map(|(_, a)| *a).unwrap_or(0.0));
    println!();
}

fn find_most_improved_subject(student: &Student) {
    if let (Some((best_subj, best_score)), Some((worst_subj, worst_score))) =
        (student.highest_subject(), student.lowest_subject())
    {
        let gap = best_score - worst_score;
        println!("    {} → 최고: {} {}점, 최저: {} {}점 (격차: {}점)",
                 student.name,
                 best_subj.name(), best_score,
                 worst_subj.name(), worst_score,
                 gap);
    }
}

// =====================================================================
// main: 프로젝트 실행
// =====================================================================

fn main() {
    println!();
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  Rust 18단계: 실전 미니 프로젝트");
    println!("  ─ 학생 성적 관리 시스템 ─");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!();

    // ── 데이터 생성 ──
    let mut classroom = ClassRoom::new("3학년 1반");

    // 학생 데이터
    let student_data = vec![
        ("철수", 3, vec![(Subject::Korean, 92), (Subject::English, 88),
                         (Subject::Math, 95), (Subject::Science, 90)]),
        ("영희", 3, vec![(Subject::Korean, 85), (Subject::English, 92),
                         (Subject::Math, 78), (Subject::Science, 88)]),
        ("민수", 3, vec![(Subject::Korean, 70), (Subject::English, 65),
                         (Subject::Math, 72), (Subject::Science, 68)]),
        ("서연", 3, vec![(Subject::Korean, 98), (Subject::English, 95),
                         (Subject::Math, 100), (Subject::Science, 97)]),
        ("지우", 3, vec![(Subject::Korean, 55), (Subject::English, 62),
                         (Subject::Math, 48), (Subject::Science, 58)]),
        ("현우", 3, vec![(Subject::Korean, 80), (Subject::English, 82),
                         (Subject::Math, 85), (Subject::Science, 79)]),
    ];

    for (name, level, scores) in &student_data {
        let mut student = Student::new(name, *level);
        for (subject, score) in scores {
            student.add_score(*subject, *score).unwrap();
        }
        classroom.add_student(student);
    }

    // ── 보고서 출력 ──
    print_class_report(&classroom);
    print_individual_reports(&classroom);

    // ── 과목 난이도 분석 ──
    analyze_subject_difficulty(&classroom);

    // ── 과목별 격차 분석 ──
    println!("  [학생별 과목 격차]");
    for student in &classroom.students {
        find_most_improved_subject(student);
    }
    println!();

    // ── 특정 학생 검색 ──
    println!("  [학생 검색]");
    match classroom.find_student("서연") {
        Some(student) => {
            println!("    서연을 찾았습니다: 평균 {:.1}점, 등급 {}",
                     student.average().unwrap_or(0.0),
                     student.overall_grade().map(|g| format!("{}", g))
                         .unwrap_or_else(|| "-".to_string()));
        }
        None => println!("    학생을 찾을 수 없습니다"),
    }
    println!();

    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  18단계 완료! Rust 학습 커리큘럼 수료!");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
}

// =====================================================================
// 테스트 모듈
// =====================================================================
#[cfg(test)]
mod tests {
    use super::*;

    fn make_test_student() -> Student {
        let mut s = Student::new("테스트", 1);
        s.add_score(Subject::Korean, 90).unwrap();
        s.add_score(Subject::English, 80).unwrap();
        s.add_score(Subject::Math, 70).unwrap();
        s.add_score(Subject::Science, 60).unwrap();
        s
    }

    #[test]
    fn test_student_average() {
        let s = make_test_student();
        assert_eq!(s.average(), Some(75.0));
    }

    #[test]
    fn test_student_overall_grade() {
        let s = make_test_student();
        assert_eq!(s.overall_grade(), Some(Grade::C));
    }

    #[test]
    fn test_student_is_passing() {
        let s = make_test_student();
        assert!(s.is_passing());
    }

    #[test]
    fn test_student_failing() {
        let mut s = Student::new("낙제", 1);
        s.add_score(Subject::Korean, 50).unwrap();
        assert!(!s.is_passing());
        assert_eq!(s.failing_subjects(), vec![Subject::Korean]);
    }

    #[test]
    fn test_invalid_score() {
        let mut s = Student::new("에러", 1);
        assert!(s.add_score(Subject::Korean, 150).is_err());
        assert!(s.add_score(Subject::Korean, -10).is_err());
    }

    #[test]
    fn test_empty_student_average() {
        let s = Student::new("빈학생", 1);
        assert_eq!(s.average(), None);
        assert_eq!(s.overall_grade(), None);
    }

    #[test]
    fn test_highest_subject() {
        let s = make_test_student();
        let (subj, score) = s.highest_subject().unwrap();
        assert_eq!(subj, Subject::Korean);
        assert_eq!(score, 90);
    }

    #[test]
    fn test_grade_from_score() {
        assert_eq!(Grade::from_score(95), Grade::A);
        assert_eq!(Grade::from_score(85), Grade::B);
        assert_eq!(Grade::from_score(75), Grade::C);
        assert_eq!(Grade::from_score(65), Grade::D);
        assert_eq!(Grade::from_score(55), Grade::F);
    }

    #[test]
    fn test_classroom_average() {
        let mut class = ClassRoom::new("테스트반");
        let s1 = make_test_student();
        class.add_student(s1);
        assert_eq!(class.class_average(), Some(75.0));
    }

    #[test]
    fn test_find_student() {
        let mut class = ClassRoom::new("테스트반");
        class.add_student(Student::new("존재", 1));
        assert!(class.find_student("존재").is_some());
        assert!(class.find_student("없음").is_none());
    }
}
