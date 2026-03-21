# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   파이썬 학습 18단계: 실전 프로젝트 (학생 성적 관리 시스템)
#   ─ 설계, 모델, 저장소, 서비스, CLI, 예외, 로깅, 테스트, 문서화 ─
#   ■ 실행 방법: python 18_real_project.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 프로젝트 설계 — 요구사항 분석, 클래스 설계, 데이터 모델
#   2. 핵심 모델 구현 — dataclass로 데이터 모델, 유효성 검사
#   3. 저장소(Repository) 패턴 — JSON 파일 기반 CRUD
#   4. 서비스 계층 — 비즈니스 로직 분리, 의존성 주입
#   5. CLI 인터페이스 — argparse 활용, 서브커맨드
#   6. 예외 처리 전략 — 계층별 예외, 사용자 친화적 에러 메시지
#   7. 로깅 전략 — 파일/콘솔 로깅, 로그 레벨 관리
#   8. 테스트 작성 — unittest로 각 계층 테스트
#   9. 문서화 — docstring, help() 출력, 사용 예제
#  10. 최종 통합: 학생 성적 관리 시스템 완성판
#
# ─────────────────────────────────────────────────────────────────────────

import json
import logging
import os
import tempfile
import unittest
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────
# ■ 공통 헬퍼 함수
# ─────────────────────────────────────────────────────────────────────────

def print_lesson(title: str) -> None:
    """레슨 제목을 눈에 띄게 출력한다."""
    print()
    print("┌──────────────────────────────────────┐")
    print(f"│  {title:<36s} │")
    print("└──────────────────────────────────────┘")
    print()


# =========================================================================
#
#   레슨 1 — 프로젝트 설계
#
# =========================================================================

def lesson1_project_design():
    print_lesson("레슨 1 : 프로젝트 설계")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 요구사항 분석
    # ─────────────────────────────────────────────────────────────────────
    #
    #   프로젝트: 학생 성적 관리 시스템
    #
    #   기능 요구사항:
    #     1. 학생 등록 (이름, 학년, 반)
    #     2. 성적 입력 (과목별 점수)
    #     3. 출석 기록 (출석/지각/결석)
    #     4. 성적 조회 (개별, 반 전체)
    #     5. 통계 분석 (평균, 최고점, 과목별)
    #     6. 데이터 저장/불러오기 (JSON 파일)
    #
    #   비기능 요구사항:
    #     - CLI로 조작 가능
    #     - 에러 발생 시 친절한 메시지
    #     - 로그 기록
    #     - 테스트 커버리지
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 요구사항 정리")
    print("  ─────────────────────────────────────")
    print("  1. 학생 CRUD (등록, 조회, 수정, 삭제)")
    print("  2. 성적 입력 및 조회")
    print("  3. 출석 관리")
    print("  4. 통계 분석")
    print("  5. JSON 파일 저장/복원")
    print("  6. CLI 인터페이스")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 클래스 설계 (계층 구조)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   실전 프로젝트에서는 "계층"을 나누는 것이 핵심!
    #
    #   ┌─────────────────────────┐
    #   │  CLI 계층 (사용자 인터페이스)  │  사용자와 대화
    #   ├─────────────────────────┤
    #   │  서비스 계층 (비즈니스 로직)   │  규칙 적용, 계산
    #   ├─────────────────────────┤
    #   │  저장소 계층 (데이터 접근)    │  파일 읽기/쓰기
    #   ├─────────────────────────┤
    #   │  모델 계층 (데이터 구조)      │  데이터 정의
    #   └─────────────────────────┘
    #
    #   비유: 레스토랑
    #     CLI    = 웨이터 (주문 받기, 음식 전달)
    #     서비스  = 셰프 (조리 규칙, 메뉴 결정)
    #     저장소  = 냉장고 관리 (재료 꺼내기/넣기)
    #     모델   = 재료 (양파, 고기, 소금)
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 계층 구조 설계")
    print("  ─────────────────────────────────────")
    print("  CLI (사용자) → 서비스 (비즈니스) → 저장소 (데이터) → 모델")
    print()
    print("  ★ 핵심 원칙:")
    print("  - 각 계층은 자기 역할만 한다")
    print("  - 위 계층은 아래 계층을 호출하지만 반대는 안 됨")
    print("  - 저장소를 교체해도 서비스 코드는 변경 불필요 (인터페이스)")
    print()


# =========================================================================
#
#   레슨 2 — 핵심 모델 구현
#
# =========================================================================

# ─────────────────────────────────────────────────────────────────────────
# ■ 모델 클래스 정의 (dataclass 활용)
# ─────────────────────────────────────────────────────────────────────────
#
#   dataclass를 사용하면:
#   - __init__, __repr__, __eq__ 등이 자동 생성
#   - 코드가 깔끔해짐
#   - 유효성 검사를 __post_init__에서 할 수 있음
#
# ─────────────────────────────────────────────────────────────────────────

@dataclass
class Student:
    """학생 데이터 모델

    Attributes:
        student_id: 학생 고유 ID
        name: 이름
        grade: 학년 (1~6)
        class_num: 반 번호 (1~10)
        scores: 과목별 점수 딕셔너리
        attendance: 출석 기록 리스트 ("출석", "지각", "결석")
        notes: 메모 리스트
        created_at: 생성일시
    """
    student_id: str
    name: str
    grade: int
    class_num: int = 1
    scores: dict[str, int] = field(default_factory=dict)
    attendance: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        """생성 후 유효성 검사"""
        self.validate()

    def validate(self):
        """데이터 유효성을 검사한다."""
        if not self.name or not self.name.strip():
            raise ValueError("이름은 비어있을 수 없습니다.")
        if not (1 <= self.grade <= 6):
            raise ValueError(f"학년은 1~6이어야 합니다. (입력값: {self.grade})")
        if not (1 <= self.class_num <= 10):
            raise ValueError(f"반은 1~10이어야 합니다. (입력값: {self.class_num})")
        for subject, score in self.scores.items():
            if not (0 <= score <= 100):
                raise ValueError(f"{subject} 점수는 0~100이어야 합니다. (입력값: {score})")

    def average_score(self) -> float:
        """전체 과목 평균 점수를 반환한다."""
        if not self.scores:
            return 0.0
        return sum(self.scores.values()) / len(self.scores)

    def attendance_rate(self) -> float:
        """출석률을 반환한다 (0.0 ~ 1.0)."""
        if not self.attendance:
            return 0.0
        present = sum(1 for a in self.attendance if a == "출석")
        return present / len(self.attendance)

    def grade_letter(self) -> str:
        """평균 점수를 학점으로 변환한다."""
        avg = self.average_score()
        if avg >= 90: return "A"
        if avg >= 80: return "B"
        if avg >= 70: return "C"
        if avg >= 60: return "D"
        return "F"

    def summary(self) -> str:
        """학생 정보 요약 문자열을 반환한다."""
        avg = self.average_score()
        att = self.attendance_rate()
        return (f"[{self.student_id}] {self.grade}학년 {self.class_num}반 {self.name} | "
                f"평균 {avg:.1f}점({self.grade_letter()}) | "
                f"출석률 {att:.0%}")


def lesson2_model_implementation():
    print_lesson("레슨 2 : 핵심 모델 구현")

    # ■ 학생 생성
    print("  ■ 학생 모델 생성")
    print("  ─────────────────────────────────────")

    student = Student(
        student_id="S001",
        name="김민수",
        grade=5,
        class_num=3,
    )
    print(f"  생성: {student}")
    print(f"  요약: {student.summary()}")
    print()

    # ■ 점수 입력 후 평균
    student.scores = {"국어": 85, "수학": 92, "영어": 78, "과학": 88}
    student.attendance = ["출석", "출석", "지각", "출석", "결석"]

    print("  ■ 점수 입력 후")
    print("  ─────────────────────────────────────")
    print(f"  점수: {student.scores}")
    print(f"  평균: {student.average_score():.1f}점")
    print(f"  학점: {student.grade_letter()}")
    print(f"  출석률: {student.attendance_rate():.0%}")
    print(f"  요약: {student.summary()}")
    print()

    # ■ 유효성 검사 테스트
    print("  ■ 유효성 검사 (잘못된 데이터)")
    print("  ─────────────────────────────────────")

    invalid_cases = [
        {"student_id": "X", "name": "", "grade": 5},
        {"student_id": "X", "name": "홍길동", "grade": 0},
        {"student_id": "X", "name": "홍길동", "grade": 7},
    ]

    for case in invalid_cases:
        try:
            Student(**case)
            print(f"    {case} → 통과 (예상 밖!)")
        except ValueError as e:
            print(f"    {case} → 에러: {e}")
    print()

    # ■ 점수 유효성 검사
    print("  ■ 점수 유효성 검사")
    print("  ─────────────────────────────────────")

    bad_student = Student(student_id="X", name="테스트", grade=1)
    bad_student.scores = {"수학": 150}
    try:
        bad_student.validate()
    except ValueError as e:
        print(f"    점수 150 → 에러: {e}")
    print()


# =========================================================================
#
#   레슨 3 — 저장소(Repository) 패턴
#
# =========================================================================

# ─────────────────────────────────────────────────────────────────────────
# ■ 저장소 인터페이스 (추상 클래스)
# ─────────────────────────────────────────────────────────────────────────
#
#   왜 인터페이스를 분리하는가?
#   - 저장 방식을 JSON → DB → API 등으로 바꿔도
#     서비스 계층 코드는 변경할 필요 없음!
#   - 테스트할 때 가짜(Mock) 저장소로 교체 가능
#
# ─────────────────────────────────────────────────────────────────────────

class StudentRepository(ABC):
    """학생 저장소 인터페이스 (추상 클래스)"""

    @abstractmethod
    def save(self, student: Student) -> None:
        """학생을 저장한다."""

    @abstractmethod
    def find_by_id(self, student_id: str) -> Optional[Student]:
        """ID로 학생을 찾는다."""

    @abstractmethod
    def find_all(self) -> list[Student]:
        """모든 학생을 반환한다."""

    @abstractmethod
    def delete(self, student_id: str) -> bool:
        """학생을 삭제한다. 성공 여부를 반환."""

    @abstractmethod
    def save_to_file(self) -> None:
        """파일에 저장한다."""

    @abstractmethod
    def load_from_file(self) -> None:
        """파일에서 불러온다."""


class JsonStudentRepository(StudentRepository):
    """JSON 파일 기반 학생 저장소 구현체"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self._students: dict[str, Student] = {}

    def save(self, student: Student) -> None:
        self._students[student.student_id] = student

    def find_by_id(self, student_id: str) -> Optional[Student]:
        return self._students.get(student_id)

    def find_all(self) -> list[Student]:
        return list(self._students.values())

    def delete(self, student_id: str) -> bool:
        if student_id in self._students:
            del self._students[student_id]
            return True
        return False

    def save_to_file(self) -> None:
        """JSON 파일로 저장한다."""
        data = {}
        for sid, student in self._students.items():
            data[sid] = asdict(student)
        self.file_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def load_from_file(self) -> None:
        """JSON 파일에서 불러온다."""
        if not self.file_path.exists():
            return
        text = self.file_path.read_text(encoding="utf-8")
        data = json.loads(text)
        self._students.clear()
        for sid, item in data.items():
            # scores의 값이 문자열일 수 있으므로 int 변환
            student = Student(
                student_id=item["student_id"],
                name=item["name"],
                grade=item["grade"],
                class_num=item.get("class_num", 1),
                scores={k: int(v) for k, v in item.get("scores", {}).items()},
                attendance=item.get("attendance", []),
                notes=item.get("notes", []),
                created_at=item.get("created_at", ""),
            )
            self._students[sid] = student

    def count(self) -> int:
        return len(self._students)


def lesson3_repository_pattern():
    print_lesson("레슨 3 : 저장소 패턴")

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "students.json")
        repo = JsonStudentRepository(db_path)

        # ■ CRUD 연산
        print("  ■ Create - 학생 등록")
        print("  ─────────────────────────────────────")

        students = [
            Student("S001", "김민수", 5, 3, {"국어": 85, "수학": 92}),
            Student("S002", "이지유", 5, 3, {"국어": 95, "수학": 98}),
            Student("S003", "박서연", 5, 3, {"국어": 72, "수학": 68}),
        ]

        for s in students:
            repo.save(s)
            print(f"    등록: {s.summary()}")
        print(f"  총 학생 수: {repo.count()}")
        print()

        # Read
        print("  ■ Read - 학생 조회")
        print("  ─────────────────────────────────────")

        found = repo.find_by_id("S001")
        if found:
            print(f"    ID로 검색: {found.summary()}")

        all_students = repo.find_all()
        print(f"    전체 학생 수: {len(all_students)}")
        print()

        # Update
        print("  ■ Update - 학생 정보 수정")
        print("  ─────────────────────────────────────")

        if found:
            found.scores["영어"] = 88
            found.attendance.append("출석")
            repo.save(found)  # 같은 ID로 저장하면 덮어쓰기
            print(f"    수정 후: {found.summary()}")
        print()

        # Delete
        print("  ■ Delete - 학생 삭제")
        print("  ─────────────────────────────────────")

        deleted = repo.delete("S003")
        print(f"    S003 삭제 결과: {deleted}")
        print(f"    남은 학생 수: {repo.count()}")
        print()

        # 파일 저장/불러오기
        print("  ■ 파일 저장 및 불러오기")
        print("  ─────────────────────────────────────")

        repo.save_to_file()
        print(f"    저장 완료: {db_path}")

        # 새 저장소에서 불러오기
        repo2 = JsonStudentRepository(db_path)
        repo2.load_from_file()
        print(f"    불러온 학생 수: {repo2.count()}")

        for s in repo2.find_all():
            print(f"    복원: {s.summary()}")
        print()


# =========================================================================
#
#   레슨 4 — 서비스 계층
#
# =========================================================================

# ─────────────────────────────────────────────────────────────────────────
# ■ 커스텀 예외 클래스
# ─────────────────────────────────────────────────────────────────────────

class StudentNotFoundError(Exception):
    """학생을 찾을 수 없을 때 발생"""
    pass


class DuplicateStudentError(Exception):
    """이미 존재하는 학생 ID로 등록 시도할 때 발생"""
    pass


class InvalidScoreError(Exception):
    """유효하지 않은 점수일 때 발생"""
    pass


class StudentService:
    """학생 관리 서비스 (비즈니스 로직 계층)

    저장소에 대한 의존성 주입을 받아 사용한다.
    이를 통해 저장소 구현체를 자유롭게 교체할 수 있다.
    """

    def __init__(self, repository: StudentRepository):
        self.repo = repository

    def register_student(self, student_id: str, name: str,
                         grade: int, class_num: int = 1) -> Student:
        """새 학생을 등록한다."""
        if self.repo.find_by_id(student_id):
            raise DuplicateStudentError(
                f"이미 등록된 학생 ID입니다: {student_id}")

        student = Student(student_id, name, grade, class_num)
        self.repo.save(student)
        return student

    def add_score(self, student_id: str, subject: str, score: int) -> Student:
        """학생에게 점수를 추가한다."""
        student = self._get_student_or_raise(student_id)

        if not (0 <= score <= 100):
            raise InvalidScoreError(
                f"점수는 0~100이어야 합니다. (입력값: {score})")

        student.scores[subject] = score
        self.repo.save(student)
        return student

    def record_attendance(self, student_id: str,
                          status: str = "출석") -> Student:
        """출석을 기록한다."""
        student = self._get_student_or_raise(student_id)

        valid_statuses = {"출석", "지각", "결석"}
        if status not in valid_statuses:
            raise ValueError(
                f"출석 상태는 {valid_statuses} 중 하나여야 합니다.")

        student.attendance.append(status)
        self.repo.save(student)
        return student

    def get_class_ranking(self, grade: int, class_num: int) -> list[Student]:
        """반의 성적 순위를 반환한다."""
        all_students = self.repo.find_all()
        class_students = [
            s for s in all_students
            if s.grade == grade and s.class_num == class_num
        ]
        return sorted(class_students,
                       key=lambda s: s.average_score(), reverse=True)

    def get_subject_stats(self, subject: str) -> dict:
        """특정 과목의 통계를 반환한다."""
        all_students = self.repo.find_all()
        scores = [
            s.scores[subject] for s in all_students
            if subject in s.scores
        ]

        if not scores:
            return {"subject": subject, "count": 0}

        return {
            "subject": subject,
            "count": len(scores),
            "average": sum(scores) / len(scores),
            "max": max(scores),
            "min": min(scores),
            "pass_rate": sum(1 for s in scores if s >= 60) / len(scores),
        }

    def get_students_needing_help(self, min_avg: float = 70.0) -> list[Student]:
        """도움이 필요한 학생 목록을 반환한다."""
        return [
            s for s in self.repo.find_all()
            if s.scores and s.average_score() < min_avg
        ]

    def _get_student_or_raise(self, student_id: str) -> Student:
        """학생을 찾거나 없으면 에러 발생"""
        student = self.repo.find_by_id(student_id)
        if not student:
            raise StudentNotFoundError(
                f"학생을 찾을 수 없습니다: {student_id}")
        return student


def lesson4_service_layer():
    print_lesson("레슨 4 : 서비스 계층")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 의존성 주입 (Dependency Injection)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   서비스가 저장소를 직접 생성하지 않고, 외부에서 전달받는다
    #
    #   나쁜 예: class Service:
    #              def __init__(self):
    #                  self.repo = JsonRepository("data.json")  # 강결합!
    #
    #   좋은 예: class Service:
    #              def __init__(self, repo: Repository):  # 의존성 주입!
    #                  self.repo = repo
    #
    #   장점:
    #     - 저장소를 JSON → DB로 바꿔도 서비스 코드 변경 불필요
    #     - 테스트 시 가짜(Mock) 저장소 주입 가능
    #
    # ─────────────────────────────────────────────────────────────────────

    with tempfile.TemporaryDirectory() as temp_dir:
        repo = JsonStudentRepository(os.path.join(temp_dir, "students.json"))
        service = StudentService(repo)

        # ■ 학생 등록
        print("  ■ 서비스 계층을 통한 학생 등록")
        print("  ─────────────────────────────────────")

        s1 = service.register_student("S001", "김민수", 5, 3)
        s2 = service.register_student("S002", "이지유", 5, 3)
        s3 = service.register_student("S003", "박서연", 5, 3)
        s4 = service.register_student("S004", "최하준", 5, 3)

        for s in [s1, s2, s3, s4]:
            print(f"    등록: {s.name}")

        # 중복 등록 시도
        try:
            service.register_student("S001", "김민수", 5, 3)
        except DuplicateStudentError as e:
            print(f"    중복 에러: {e}")
        print()

        # ■ 성적 입력
        print("  ■ 성적 입력")
        print("  ─────────────────────────────────────")

        scores_data = {
            "S001": {"국어": 85, "수학": 92, "영어": 78, "과학": 88},
            "S002": {"국어": 95, "수학": 98, "영어": 92, "과학": 96},
            "S003": {"국어": 62, "수학": 55, "영어": 68, "과학": 58},
            "S004": {"국어": 78, "수학": 82, "영어": 75, "과학": 80},
        }

        for sid, subjects in scores_data.items():
            for subject, score in subjects.items():
                service.add_score(sid, subject, score)

        for s in repo.find_all():
            print(f"    {s.summary()}")
        print()

        # ■ 반 석차
        print("  ■ 5학년 3반 성적 순위")
        print("  ─────────────────────────────────────")

        ranking = service.get_class_ranking(5, 3)
        for rank, student in enumerate(ranking, 1):
            print(f"    {rank}등: {student.name} (평균 {student.average_score():.1f}점)")
        print()

        # ■ 과목별 통계
        print("  ■ 과목별 통계")
        print("  ─────────────────────────────────────")

        for subject in ["국어", "수학", "영어", "과학"]:
            stats = service.get_subject_stats(subject)
            print(f"    {subject}: 평균={stats['average']:.1f}, "
                  f"최고={stats['max']}, 최저={stats['min']}, "
                  f"통과율={stats['pass_rate']:.0%}")
        print()

        # ■ 도움이 필요한 학생
        print("  ■ 도움이 필요한 학생 (평균 70점 미만)")
        print("  ─────────────────────────────────────")

        need_help = service.get_students_needing_help(70.0)
        if need_help:
            for s in need_help:
                print(f"    {s.name}: 평균 {s.average_score():.1f}점")
        else:
            print("    해당 학생 없음")
        print()


# =========================================================================
#
#   레슨 5 — CLI 인터페이스
#
# =========================================================================

def lesson5_cli_interface():
    print_lesson("레슨 5 : CLI 인터페이스")

    # ─────────────────────────────────────────────────────────────────────
    # ■ argparse를 사용한 CLI 설계
    # ─────────────────────────────────────────────────────────────────────
    #
    #   argparse = 파이썬 내장 CLI 파싱 도구
    #
    #   사용법:
    #     student-mgr add --name "김민수" --grade 5
    #     student-mgr score --id S001 --subject 수학 --score 95
    #     student-mgr list
    #     student-mgr rank --grade 5 --class 3
    #
    # ─────────────────────────────────────────────────────────────────────

    import argparse

    def build_parser() -> argparse.ArgumentParser:
        """CLI 파서를 생성한다."""
        parser = argparse.ArgumentParser(
            prog="student-mgr",
            description="학생 성적 관리 시스템"
        )
        subparsers = parser.add_subparsers(dest="command", help="명령어")

        # add 서브커맨드
        add_parser = subparsers.add_parser("add", help="학생 등록")
        add_parser.add_argument("--id", required=True, help="학생 ID")
        add_parser.add_argument("--name", required=True, help="이름")
        add_parser.add_argument("--grade", type=int, required=True, help="학년")
        add_parser.add_argument("--class-num", type=int, default=1, help="반")

        # score 서브커맨드
        score_parser = subparsers.add_parser("score", help="성적 입력")
        score_parser.add_argument("--id", required=True, help="학생 ID")
        score_parser.add_argument("--subject", required=True, help="과목")
        score_parser.add_argument("--score", type=int, required=True, help="점수")

        # list 서브커맨드
        subparsers.add_parser("list", help="학생 목록 조회")

        # rank 서브커맨드
        rank_parser = subparsers.add_parser("rank", help="성적 순위")
        rank_parser.add_argument("--grade", type=int, required=True)
        rank_parser.add_argument("--class-num", type=int, required=True)

        return parser

    # ■ CLI 시뮬레이션
    print("  ■ argparse CLI 구조")
    print("  ─────────────────────────────────────")

    parser = build_parser()
    print("  사용 가능한 명령어:")
    print("    student-mgr add --id S001 --name 김민수 --grade 5")
    print("    student-mgr score --id S001 --subject 수학 --score 95")
    print("    student-mgr list")
    print("    student-mgr rank --grade 5 --class-num 3")
    print()

    # 파싱 시뮬레이션
    test_commands = [
        ["add", "--id", "S001", "--name", "김민수", "--grade", "5"],
        ["score", "--id", "S001", "--subject", "수학", "--score", "95"],
        ["list"],
        ["rank", "--grade", "5", "--class-num", "3"],
    ]

    print("  ■ 명령어 파싱 결과")
    print("  ─────────────────────────────────────")

    for cmd in test_commands:
        args = parser.parse_args(cmd)
        print(f"    입력: {' '.join(cmd)}")
        print(f"    결과: {vars(args)}")
        print()


# =========================================================================
#
#   레슨 6 — 예외 처리 전략
#
# =========================================================================

def lesson6_exception_strategy():
    print_lesson("레슨 6 : 예외 처리 전략")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 계층별 예외 전략
    # ─────────────────────────────────────────────────────────────────────
    #
    #   모델 계층: ValueError (데이터 유효성 실패)
    #   저장소 계층: IOError, FileNotFoundError (파일 접근 실패)
    #   서비스 계층: 커스텀 비즈니스 예외 (StudentNotFoundError 등)
    #   CLI 계층: 모든 예외를 잡아서 사용자 친화적 메시지로 변환
    #
    #   원칙:
    #     - 예외는 가능한 발생 지점에 가까운 곳에서 처리
    #     - 처리할 수 없으면 상위 계층으로 전파
    #     - CLI에서 최종적으로 사용자에게 친절한 메시지 출력
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 계층별 예외 처리 예시")
    print("  ─────────────────────────────────────")

    def handle_cli_command(service: StudentService, command: str, **kwargs):
        """CLI 계층에서 예외를 잡아 사용자 친화적 메시지로 변환"""
        try:
            if command == "add_score":
                result = service.add_score(**kwargs)
                print(f"    성공: {result.name}의 {kwargs['subject']} 점수 등록")
            elif command == "register":
                result = service.register_student(**kwargs)
                print(f"    성공: {result.name} 학생 등록 완료")
        except StudentNotFoundError:
            print(f"    오류: 학생 ID '{kwargs.get('student_id', '?')}'를 찾을 수 없습니다.")
            print(f"    → 'list' 명령어로 등록된 학생을 확인해주세요.")
        except DuplicateStudentError:
            print(f"    오류: 이미 등록된 학생입니다.")
        except InvalidScoreError as e:
            print(f"    오류: {e}")
            print(f"    → 점수는 0~100 사이의 정수를 입력해주세요.")
        except ValueError as e:
            print(f"    오류: 잘못된 입력입니다 - {e}")
        except Exception as e:
            print(f"    시스템 오류: {e}")
            print(f"    → 관리자에게 문의해주세요.")

    with tempfile.TemporaryDirectory() as temp_dir:
        repo = JsonStudentRepository(os.path.join(temp_dir, "test.json"))
        service = StudentService(repo)
        service.register_student("S001", "김민수", 5, 3)

        # 성공 케이스
        handle_cli_command(service, "add_score",
                           student_id="S001", subject="수학", score=95)

        # 존재하지 않는 학생
        handle_cli_command(service, "add_score",
                           student_id="S999", subject="수학", score=95)

        # 잘못된 점수
        handle_cli_command(service, "add_score",
                           student_id="S001", subject="수학", score=150)

        # 중복 등록
        handle_cli_command(service, "register",
                           student_id="S001", name="김민수", grade=5)
    print()


# =========================================================================
#
#   레슨 7 — 로깅 전략
#
# =========================================================================

def lesson7_logging_strategy():
    print_lesson("레슨 7 : 로깅 전략")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 로깅이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   프로그램 실행 중 발생하는 이벤트를 기록하는 것
    #
    #   print vs logging:
    #     print   → 사용자에게 보여주는 출력 (삭제해야 할 수도)
    #     logging → 개발자/운영자를 위한 기록 (영구 보존)
    #
    #   로그 레벨:
    #     DEBUG    → 상세한 디버깅 정보
    #     INFO     → 일반적인 동작 확인
    #     WARNING  → 잠재적 문제
    #     ERROR    → 에러 발생 (기능 실패)
    #     CRITICAL → 심각한 에러 (프로그램 중단)
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ 로거 설정
    print("  ■ 로깅 설정 및 사용 예시")
    print("  ─────────────────────────────────────")

    # StringIO로 로그를 캡처 (화면에 출력하기 위해)
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    ))

    logger = logging.getLogger("student_manager")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    # 이전 핸들러 제거 (중복 방지)
    logger.handlers = [handler]

    # ■ 로그 사용 예시
    logger.debug("데이터베이스 연결 시도")
    logger.info("학생 'S001' 등록 완료")
    logger.warning("학생 'S003'의 평균이 60점 미만입니다")
    logger.error("파일 'data.json' 읽기 실패: FileNotFoundError")
    logger.critical("데이터베이스 연결 끊김!")

    # 캡처된 로그 출력
    log_output = log_stream.getvalue()
    for line in log_output.strip().split("\n"):
        print(f"    {line}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 실전 로깅 패턴
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 실전 로깅 패턴")
    print("  ─────────────────────────────────────")

    logging_config_example = """
    # 로깅 설정 (보통 앱 시작 시 한 번만)
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler("app.log", encoding="utf-8"),  # 파일
            logging.StreamHandler(),                            # 콘솔
        ]
    )

    # 모듈별 로거 생성
    logger = logging.getLogger(__name__)

    # 사용
    logger.info("서버 시작 (포트: %d)", 8000)
    logger.error("요청 처리 실패", exc_info=True)  # 스택 트레이스 포함
    """
    for line in logging_config_example.strip().split("\n"):
        print(f"    {line}")

    # 핸들러 정리
    logger.removeHandler(handler)
    print()


# =========================================================================
#
#   레슨 8 — 테스트 작성
#
# =========================================================================

def lesson8_testing():
    print_lesson("레슨 8 : 테스트 작성")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 테스트의 중요성
    # ─────────────────────────────────────────────────────────────────────
    #
    #   "테스트 없는 코드는 레거시 코드다" — Michael Feathers
    #
    #   테스트가 있으면:
    #     - 코드를 수정해도 기존 기능이 깨지지 않는지 확인 가능
    #     - 버그를 빠르게 찾을 수 있음
    #     - 리팩토링에 대한 자신감
    #
    #   테스트 종류:
    #     단위 테스트: 개별 함수/클래스 테스트
    #     통합 테스트: 여러 모듈이 함께 동작하는지 테스트
    #     E2E 테스트: 전체 시스템을 사용자 관점에서 테스트
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ unittest로 모델 테스트
    class TestStudent(unittest.TestCase):
        """Student 모델 테스트"""

        def test_create_valid_student(self):
            """유효한 학생 생성"""
            s = Student("S001", "김민수", 5, 3)
            self.assertEqual(s.name, "김민수")
            self.assertEqual(s.grade, 5)

        def test_invalid_grade(self):
            """잘못된 학년으로 생성 시 에러"""
            with self.assertRaises(ValueError):
                Student("S001", "김민수", 0, 1)

        def test_empty_name(self):
            """빈 이름으로 생성 시 에러"""
            with self.assertRaises(ValueError):
                Student("S001", "", 5, 1)

        def test_average_score(self):
            """평균 점수 계산"""
            s = Student("S001", "김민수", 5)
            s.scores = {"국어": 80, "수학": 90}
            self.assertEqual(s.average_score(), 85.0)

        def test_average_no_scores(self):
            """점수가 없을 때 평균 0"""
            s = Student("S001", "김민수", 5)
            self.assertEqual(s.average_score(), 0.0)

        def test_attendance_rate(self):
            """출석률 계산"""
            s = Student("S001", "김민수", 5)
            s.attendance = ["출석", "출석", "지각", "출석", "결석"]
            self.assertAlmostEqual(s.attendance_rate(), 0.6)

        def test_grade_letter(self):
            """학점 변환"""
            s = Student("S001", "김민수", 5)
            s.scores = {"수학": 95}
            self.assertEqual(s.grade_letter(), "A")

    # ■ 서비스 계층 테스트
    class TestStudentService(unittest.TestCase):
        """StudentService 테스트"""

        def setUp(self):
            """각 테스트 전에 실행: 임시 저장소 생성"""
            self.temp_dir = tempfile.mkdtemp()
            db_path = os.path.join(self.temp_dir, "test.json")
            self.repo = JsonStudentRepository(db_path)
            self.service = StudentService(self.repo)

        def test_register_student(self):
            """학생 등록"""
            s = self.service.register_student("S001", "김민수", 5, 3)
            self.assertEqual(s.name, "김민수")
            self.assertEqual(self.repo.count(), 1)

        def test_duplicate_registration(self):
            """중복 등록 시 에러"""
            self.service.register_student("S001", "김민수", 5)
            with self.assertRaises(DuplicateStudentError):
                self.service.register_student("S001", "이민수", 5)

        def test_add_score(self):
            """성적 추가"""
            self.service.register_student("S001", "김민수", 5)
            s = self.service.add_score("S001", "수학", 95)
            self.assertEqual(s.scores["수학"], 95)

        def test_add_invalid_score(self):
            """잘못된 점수 시 에러"""
            self.service.register_student("S001", "김민수", 5)
            with self.assertRaises(InvalidScoreError):
                self.service.add_score("S001", "수학", 150)

        def test_student_not_found(self):
            """존재하지 않는 학생"""
            with self.assertRaises(StudentNotFoundError):
                self.service.add_score("S999", "수학", 95)

    # ■ 테스트 실행
    print("  ■ 테스트 실행 결과")
    print("  ─────────────────────────────────────")

    # 출력을 캡처하기 위해 StringIO 사용
    test_output = StringIO()
    loader = unittest.TestLoader()

    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestStudent))
    suite.addTests(loader.loadTestsFromTestCase(TestStudentService))

    runner = unittest.TextTestRunner(stream=test_output, verbosity=2)
    result = runner.run(suite)

    # 결과 출력
    for line in test_output.getvalue().strip().split("\n"):
        print(f"    {line}")

    print()
    print(f"  총 테스트: {result.testsRun}")
    print(f"  성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  실패: {len(result.failures)}")
    print(f"  에러: {len(result.errors)}")
    print()


# =========================================================================
#
#   레슨 9 — 문서화
#
# =========================================================================

def lesson9_documentation():
    print_lesson("레슨 9 : 문서화")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 좋은 docstring의 구조
    # ─────────────────────────────────────────────────────────────────────
    #
    #   Google 스타일 docstring:
    #
    #   def function(arg1: int, arg2: str) -> bool:
    #       """함수가 하는 일을 한 줄로 설명한다.
    #
    #       더 자세한 설명이 필요하면 여기에 적는다.
    #       여러 줄이 될 수 있다.
    #
    #       Args:
    #           arg1: 첫 번째 인자 설명
    #           arg2: 두 번째 인자 설명
    #
    #       Returns:
    #           반환값 설명
    #
    #       Raises:
    #           ValueError: 잘못된 입력일 때
    #
    #       Example:
    #           >>> function(1, "hello")
    #           True
    #       """
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ docstring으로 문서 확인 (help())")
    print("  ─────────────────────────────────────")

    # Student 클래스의 docstring 출력
    print(f"  Student 클래스: {Student.__doc__}")
    print()
    print(f"  average_score 메서드: {Student.average_score.__doc__}")
    print(f"  attendance_rate 메서드: {Student.attendance_rate.__doc__}")
    print(f"  grade_letter 메서드: {Student.grade_letter.__doc__}")
    print()

    # ■ StudentService 메서드 문서
    print("  ■ StudentService 메서드 문서")
    print("  ─────────────────────────────────────")

    service_methods = [
        ("register_student", StudentService.register_student),
        ("add_score", StudentService.add_score),
        ("record_attendance", StudentService.record_attendance),
        ("get_class_ranking", StudentService.get_class_ranking),
        ("get_subject_stats", StudentService.get_subject_stats),
    ]

    for name, method in service_methods:
        doc = method.__doc__ or "문서 없음"
        print(f"    {name}(): {doc.strip()}")
    print()

    # ■ 사용 예제 문서
    print("  ■ 사용 예제")
    print("  ─────────────────────────────────────")
    print("""
    # 1. 저장소 생성
    repo = JsonStudentRepository("students.json")

    # 2. 서비스 생성 (의존성 주입)
    service = StudentService(repo)

    # 3. 학생 등록
    student = service.register_student("S001", "김민수", 5, 3)

    # 4. 성적 입력
    service.add_score("S001", "수학", 95)
    service.add_score("S001", "국어", 88)

    # 5. 출석 기록
    service.record_attendance("S001", "출석")

    # 6. 순위 조회
    ranking = service.get_class_ranking(grade=5, class_num=3)

    # 7. 데이터 저장
    repo.save_to_file()
    """)


# =========================================================================
#
#   레슨 10 — 최종 통합: 학생 성적 관리 시스템 완성판
#
# =========================================================================

def lesson10_final_integration():
    print_lesson("레슨 10 : 최종 통합 데모")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 시나리오: 학기말 5학년 3반 성적 관리
    # ─────────────────────────────────────────────────────────────────────

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "class_5_3.json")
        repo = JsonStudentRepository(db_path)
        service = StudentService(repo)

        # ■ 1단계: 학생 등록
        print("  ■ 1단계: 학생 등록")
        print("  ─────────────────────────────────────")

        students_info = [
            ("S001", "김민수", 5, 3),
            ("S002", "이지유", 5, 3),
            ("S003", "박서연", 5, 3),
            ("S004", "최하준", 5, 3),
            ("S005", "정도윤", 5, 3),
            ("S006", "한수아", 5, 3),
        ]

        for sid, name, grade, cls in students_info:
            service.register_student(sid, name, grade, cls)
            print(f"    등록: [{sid}] {name}")
        print()

        # ■ 2단계: 성적 입력
        print("  ■ 2단계: 성적 입력")
        print("  ─────────────────────────────────────")

        all_scores = {
            "S001": {"국어": 85, "수학": 92, "영어": 78, "과학": 88, "사회": 82},
            "S002": {"국어": 95, "수학": 98, "영어": 92, "과학": 96, "사회": 94},
            "S003": {"국어": 62, "수학": 55, "영어": 68, "과학": 58, "사회": 65},
            "S004": {"국어": 78, "수학": 82, "영어": 75, "과학": 80, "사회": 77},
            "S005": {"국어": 88, "수학": 95, "영어": 85, "과학": 91, "사회": 87},
            "S006": {"국어": 72, "수학": 68, "영어": 70, "과학": 74, "사회": 71},
        }

        for sid, subjects in all_scores.items():
            for subject, score in subjects.items():
                service.add_score(sid, subject, score)

        for s in repo.find_all():
            print(f"    {s.name}: 평균 {s.average_score():.1f}점 ({s.grade_letter()})")
        print()

        # ■ 3단계: 출석 기록
        print("  ■ 3단계: 출석 기록 (1주일)")
        print("  ─────────────────────────────────────")

        attendance_data = {
            "S001": ["출석", "출석", "지각", "출석", "출석"],
            "S002": ["출석", "출석", "출석", "출석", "출석"],
            "S003": ["출석", "결석", "출석", "지각", "결석"],
            "S004": ["출석", "출석", "출석", "출석", "지각"],
            "S005": ["출석", "출석", "출석", "출석", "출석"],
            "S006": ["출석", "출석", "지각", "출석", "출석"],
        }

        for sid, records in attendance_data.items():
            for status in records:
                service.record_attendance(sid, status)

        for s in repo.find_all():
            print(f"    {s.name}: 출석률 {s.attendance_rate():.0%} "
                  f"(출석 {s.attendance.count('출석')}/"
                  f"지각 {s.attendance.count('지각')}/"
                  f"결석 {s.attendance.count('결석')})")
        print()

        # ■ 4단계: 반 석차
        print("  ■ 4단계: 5학년 3반 성적 순위")
        print("  ─────────────────────────────────────")

        ranking = service.get_class_ranking(5, 3)
        for rank, student in enumerate(ranking, 1):
            avg = student.average_score()
            medal = ""
            if rank == 1: medal = " ★"
            elif rank == 2: medal = " ☆"
            elif rank == 3: medal = " △"
            print(f"    {rank}등: {student.name} "
                  f"(평균 {avg:.1f}점, {student.grade_letter()}){medal}")
        print()

        # ■ 5단계: 과목별 분석
        print("  ■ 5단계: 과목별 통계 분석")
        print("  ─────────────────────────────────────")

        subjects = ["국어", "수학", "영어", "과학", "사회"]
        print(f"    {'과목':<6s} {'평균':>6s} {'최고':>5s} {'최저':>5s} {'통과율':>6s}")
        print(f"    {'─'*6} {'─'*6} {'─'*5} {'─'*5} {'─'*6}")

        for subject in subjects:
            stats = service.get_subject_stats(subject)
            print(f"    {subject:<6s} {stats['average']:>6.1f} "
                  f"{stats['max']:>5d} {stats['min']:>5d} "
                  f"{stats['pass_rate']:>6.0%}")
        print()

        # ■ 6단계: 특별 관리 대상
        print("  ■ 6단계: 특별 관리가 필요한 학생")
        print("  ─────────────────────────────────────")

        need_help = service.get_students_needing_help(70.0)
        if need_help:
            for s in need_help:
                weak_subjects = [
                    subj for subj, score in s.scores.items() if score < 70
                ]
                print(f"    {s.name}: 평균 {s.average_score():.1f}점")
                if weak_subjects:
                    print(f"      취약 과목: {', '.join(weak_subjects)}")
                if s.attendance_rate() < 0.8:
                    print(f"      출석률 주의: {s.attendance_rate():.0%}")
        else:
            print("    해당 학생 없음")
        print()

        # ■ 7단계: 데이터 저장
        print("  ■ 7단계: 데이터 저장 및 복원")
        print("  ─────────────────────────────────────")

        repo.save_to_file()
        file_size = Path(db_path).stat().st_size
        print(f"    저장 완료: {db_path}")
        print(f"    파일 크기: {file_size:,} bytes")

        # 복원 검증
        repo2 = JsonStudentRepository(db_path)
        repo2.load_from_file()
        print(f"    복원된 학생 수: {repo2.count()}")

        # 복원된 데이터 검증
        original_top = ranking[0]
        restored = repo2.find_by_id(original_top.student_id)
        if restored:
            print(f"    1등 학생 검증: {restored.name} "
                  f"(평균 {restored.average_score():.1f}점) → 일치!")
        print()

        # ■ 최종 요약
        print("  =========================================")
        print("  ■ 최종 학기 보고서")
        print("  =========================================")
        print(f"  대상: 5학년 3반 ({len(ranking)}명)")
        all_avg = sum(s.average_score() for s in ranking) / len(ranking)
        all_att = sum(s.attendance_rate() for s in ranking) / len(ranking)
        print(f"  반 평균: {all_avg:.1f}점")
        print(f"  반 출석률: {all_att:.0%}")
        print(f"  1등: {ranking[0].name} ({ranking[0].average_score():.1f}점)")
        print(f"  관리 필요: {len(need_help)}명")
        print("  =========================================")
        print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인 실행 함수
# ─────────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 72)
    print("  파이썬 학습 18단계: 실전 프로젝트 (학생 성적 관리 시스템)")
    print("=" * 72)

    lesson1_project_design()
    lesson2_model_implementation()
    lesson3_repository_pattern()
    lesson4_service_layer()
    lesson5_cli_interface()
    lesson6_exception_strategy()
    lesson7_logging_strategy()
    lesson8_testing()
    lesson9_documentation()
    lesson10_final_integration()

    print()
    print("=" * 72)
    print("  모든 레슨 완료!")
    print("=" * 72)


if __name__ == "__main__":
    main()
