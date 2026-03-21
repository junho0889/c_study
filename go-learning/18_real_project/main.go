/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Go 학습 18단계: 실전 프로젝트 — 학생 성적 관리 시스템
  ─ 전체 종합 · CRUD · 정렬 · 통계 · 파일 저장 · 에러 처리 ─

  [학습 목표]
  1. 지금까지 배운 모든 것을 하나의 프로젝트에 적용한다
  2. 구조체, 메서드, 인터페이스, 에러 처리를 종합한다
  3. 파일 I/O, JSON, 정렬을 실전에서 사용한다
  4. 테스트 가능한 구조를 설계한다

  ■ 실행: go run main.go
  ■ 빌드: go build -o 18_project main.go

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"sort"
	"strings"
)

// ─────────────────────────────────────────────────────────────────────────
// 모델 (Model) — 데이터 구조 정의
// ─────────────────────────────────────────────────────────────────────────

/*
   ★ 프로젝트의 핵심 데이터 구조

   ┌──────────────────────────────┐
   │  Student                    │
   ├──────────────────────────────┤
   │  ID            int          │
   │  Name          string       │
   │  Score         int          │
   │  HomeworkCount int          │
   └──────────────────────────────┘
*/

type Student struct {
	ID            int    `json:"id"`
	Name          string `json:"name"`
	Score         int    `json:"score"`
	HomeworkCount int    `json:"homework_count"`
}

// GradeLabel — 점수에 따른 등급
func (s Student) GradeLabel() string {
	switch {
	case s.Score >= 90:
		return "우수"
	case s.Score >= 70:
		return "통과"
	default:
		return "복습 필요"
	}
}

// Summary — 한 줄 요약
func (s Student) Summary() string {
	return fmt.Sprintf("ID=%d  %-6s %3d점  숙제 %d개  [%s]",
		s.ID, s.Name, s.Score, s.HomeworkCount, s.GradeLabel())
}

// ─────────────────────────────────────────────────────────────────────────
// 에러 정의
// ─────────────────────────────────────────────────────────────────────────

var (
	ErrStudentNotFound = errors.New("학생을 찾을 수 없습니다")
	ErrEmptyName       = errors.New("이름이 비어있습니다")
	ErrInvalidScore    = errors.New("점수는 0~100 범위여야 합니다")
	ErrDuplicateName   = errors.New("같은 이름의 학생이 이미 있습니다")
)

// ─────────────────────────────────────────────────────────────────────────
// 저장소 인터페이스 (Repository Interface)
// ─────────────────────────────────────────────────────────────────────────

/*
   ★ 인터페이스로 저장소를 추상화 → 나중에 파일/DB로 교체 가능!
*/

type StudentRepository interface {
	Add(s Student) error
	FindByID(id int) (Student, error)
	FindAll() []Student
	Update(s Student) error
	Delete(id int) error
}

// ─────────────────────────────────────────────────────────────────────────
// 인메모리 저장소 구현
// ─────────────────────────────────────────────────────────────────────────

type MemoryRepository struct {
	students []Student
	nextID   int
}

func NewMemoryRepository() *MemoryRepository {
	return &MemoryRepository{nextID: 1}
}

func (r *MemoryRepository) Add(s Student) error {
	s.ID = r.nextID
	r.nextID++
	r.students = append(r.students, s)
	return nil
}

func (r *MemoryRepository) FindByID(id int) (Student, error) {
	for _, s := range r.students {
		if s.ID == id {
			return s, nil
		}
	}
	return Student{}, fmt.Errorf("%w: ID=%d", ErrStudentNotFound, id)
}

func (r *MemoryRepository) FindAll() []Student {
	result := make([]Student, len(r.students))
	copy(result, r.students)
	return result
}

func (r *MemoryRepository) Update(s Student) error {
	for i, existing := range r.students {
		if existing.ID == s.ID {
			r.students[i] = s
			return nil
		}
	}
	return fmt.Errorf("%w: ID=%d", ErrStudentNotFound, s.ID)
}

func (r *MemoryRepository) Delete(id int) error {
	for i, s := range r.students {
		if s.ID == id {
			r.students = append(r.students[:i], r.students[i+1:]...)
			return nil
		}
	}
	return fmt.Errorf("%w: ID=%d", ErrStudentNotFound, id)
}

// ─────────────────────────────────────────────────────────────────────────
// 서비스 (Service) — 비즈니스 로직
// ─────────────────────────────────────────────────────────────────────────

type StudentService struct {
	repo StudentRepository // ← 의존성 주입!
}

func NewStudentService(repo StudentRepository) *StudentService {
	return &StudentService{repo: repo}
}

// Register — 학생 등록 (검증 포함)
func (svc *StudentService) Register(name string, score, homework int) (Student, error) {
	// 검증
	if name == "" {
		return Student{}, ErrEmptyName
	}
	if score < 0 || score > 100 {
		return Student{}, fmt.Errorf("%w: %d", ErrInvalidScore, score)
	}

	// 중복 이름 확인
	for _, existing := range svc.repo.FindAll() {
		if existing.Name == name {
			return Student{}, fmt.Errorf("%w: %s", ErrDuplicateName, name)
		}
	}

	s := Student{Name: name, Score: score, HomeworkCount: homework}
	err := svc.repo.Add(s)
	if err != nil {
		return Student{}, err
	}

	// Add가 ID를 부여하므로 다시 조회
	all := svc.repo.FindAll()
	return all[len(all)-1], nil
}

// UpdateScore — 점수 변경
func (svc *StudentService) UpdateScore(id, newScore int) error {
	if newScore < 0 || newScore > 100 {
		return fmt.Errorf("%w: %d", ErrInvalidScore, newScore)
	}
	s, err := svc.repo.FindByID(id)
	if err != nil {
		return err
	}
	s.Score = newScore
	return svc.repo.Update(s)
}

// ─────────────────────────────────────────────────────────────────────────
// 통계 (Statistics)
// ─────────────────────────────────────────────────────────────────────────

type Statistics struct {
	Count   int
	Average float64
	Max     int
	Min     int
	MaxName string
	MinName string
}

func (svc *StudentService) GetStatistics() Statistics {
	all := svc.repo.FindAll()
	if len(all) == 0 {
		return Statistics{}
	}

	total := 0
	maxS := all[0]
	minS := all[0]

	for _, s := range all {
		total += s.Score
		if s.Score > maxS.Score {
			maxS = s
		}
		if s.Score < minS.Score {
			minS = s
		}
	}

	return Statistics{
		Count:   len(all),
		Average: float64(total) / float64(len(all)),
		Max:     maxS.Score,
		Min:     minS.Score,
		MaxName: maxS.Name,
		MinName: minS.Name,
	}
}

// GetRanking — 점수 높은 순으로 정렬
func (svc *StudentService) GetRanking() []Student {
	all := svc.repo.FindAll()
	sort.Slice(all, func(i, j int) bool {
		return all[i].Score > all[j].Score
	})
	return all
}

// GetByGrade — 등급별 필터링
func (svc *StudentService) GetByGrade(grade string) []Student {
	var result []Student
	for _, s := range svc.repo.FindAll() {
		if s.GradeLabel() == grade {
			result = append(result, s)
		}
	}
	return result
}

// ─────────────────────────────────────────────────────────────────────────
// JSON 내보내기/가져오기
// ─────────────────────────────────────────────────────────────────────────

func (svc *StudentService) ExportJSON() (string, error) {
	all := svc.repo.FindAll()
	data, err := json.MarshalIndent(all, "", "  ")
	if err != nil {
		return "", fmt.Errorf("JSON 변환 실패: %w", err)
	}
	return string(data), nil
}

func (svc *StudentService) ImportJSON(jsonStr string) (int, error) {
	var students []Student
	err := json.Unmarshal([]byte(jsonStr), &students)
	if err != nil {
		return 0, fmt.Errorf("JSON 파싱 실패: %w", err)
	}

	count := 0
	for _, s := range students {
		_, err := svc.Register(s.Name, s.Score, s.HomeworkCount)
		if err != nil {
			fmt.Printf("    경고: '%s' 가져오기 실패 — %s\n", s.Name, err)
			continue
		}
		count++
	}
	return count, nil
}

// ─────────────────────────────────────────────────────────────────────────
// 보고서 생성
// ─────────────────────────────────────────────────────────────────────────

func (svc *StudentService) GenerateReport() string {
	var b strings.Builder

	b.WriteString("╔══════════════════════════════════════════╗\n")
	b.WriteString("║         학생 성적 관리 보고서             ║\n")
	b.WriteString("╠══════════════════════════════════════════╣\n")

	// 순위표
	ranking := svc.GetRanking()
	b.WriteString("║  순위  이름     점수  숙제  등급          ║\n")
	b.WriteString("╠══════════════════════════════════════════╣\n")
	for i, s := range ranking {
		line := fmt.Sprintf("║  %2d.  %-6s  %3d점  %d개   %-8s     ║\n",
			i+1, s.Name, s.Score, s.HomeworkCount, s.GradeLabel())
		b.WriteString(line)
	}

	// 통계
	stats := svc.GetStatistics()
	b.WriteString("╠══════════════════════════════════════════╣\n")
	b.WriteString(fmt.Sprintf("║  학생 수: %d명                           ║\n", stats.Count))
	b.WriteString(fmt.Sprintf("║  평균: %.1f점                            ║\n", stats.Average))
	b.WriteString(fmt.Sprintf("║  최고: %s(%d점)                          ║\n", stats.MaxName, stats.Max))
	b.WriteString(fmt.Sprintf("║  최저: %s(%d점)                          ║\n", stats.MinName, stats.Min))
	b.WriteString("╚══════════════════════════════════════════╝\n")

	return b.String()
}

// ─────────────────────────────────────────────────────────────────────────
// main — 모든 기능 시연
// ─────────────────────────────────────────────────────────────────────────

func main() {
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println("  Go 18단계 : 실전 프로젝트")
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println()

	// ── 1. 서비스 생성 ──
	repo := NewMemoryRepository()
	svc := NewStudentService(repo)

	fmt.Println("=== 1. 학생 등록 ===")
	fmt.Println()
	testStudents := []struct {
		name     string
		score    int
		homework int
	}{
		{"민수", 85, 3},
		{"지우", 92, 5},
		{"서연", 78, 4},
		{"하준", 96, 6},
		{"예린", 65, 2},
	}

	for _, ts := range testStudents {
		s, err := svc.Register(ts.name, ts.score, ts.homework)
		if err != nil {
			fmt.Printf("  에러: %s\n", err)
		} else {
			fmt.Printf("  등록: %s\n", s.Summary())
		}
	}
	fmt.Println()

	// ── 2. 검증 테스트 ──
	fmt.Println("=== 2. 검증 테스트 ===")
	fmt.Println()

	_, err := svc.Register("", 80, 3)
	fmt.Printf("  빈 이름: %s\n", err)

	_, err = svc.Register("테스트", 150, 0)
	fmt.Printf("  잘못된 점수: %s\n", err)

	_, err = svc.Register("민수", 90, 5)
	fmt.Printf("  중복 이름: %s\n", err)
	fmt.Println()

	// ── 3. 점수 변경 ──
	fmt.Println("=== 3. 점수 변경 ===")
	fmt.Println()

	svc.UpdateScore(1, 90)
	s, _ := svc.repo.FindByID(1)
	fmt.Printf("  민수 점수 변경: %s\n", s.Summary())
	fmt.Println()

	// ── 4. 순위표 ──
	fmt.Println("=== 4. 순위표 ===")
	fmt.Println()

	ranking := svc.GetRanking()
	for i, s := range ranking {
		fmt.Printf("  %d위: %s\n", i+1, s.Summary())
	}
	fmt.Println()

	// ── 5. 통계 ──
	fmt.Println("=== 5. 통계 ===")
	fmt.Println()

	stats := svc.GetStatistics()
	fmt.Printf("  학생 수: %d명\n", stats.Count)
	fmt.Printf("  평균: %.1f점\n", stats.Average)
	fmt.Printf("  최고: %s (%d점)\n", stats.MaxName, stats.Max)
	fmt.Printf("  최저: %s (%d점)\n", stats.MinName, stats.Min)
	fmt.Println()

	// ── 6. 등급별 필터 ──
	fmt.Println("=== 6. 등급별 필터 ===")
	fmt.Println()

	for _, grade := range []string{"우수", "통과", "복습 필요"} {
		students := svc.GetByGrade(grade)
		names := make([]string, len(students))
		for i, s := range students {
			names[i] = s.Name
		}
		fmt.Printf("  [%s] %s\n", grade, strings.Join(names, ", "))
	}
	fmt.Println()

	// ── 7. JSON 내보내기 ──
	fmt.Println("=== 7. JSON 내보내기 ===")
	fmt.Println()

	jsonStr, _ := svc.ExportJSON()
	fmt.Println(jsonStr)
	fmt.Println()

	// ── 8. JSON 가져오기 ──
	fmt.Println("=== 8. JSON 가져오기 (새 데이터) ===")
	fmt.Println()

	importData := `[
  {"name": "수빈", "score": 88, "homework_count": 4},
  {"name": "도윤", "score": 73, "homework_count": 3},
  {"name": "민수", "score": 99, "homework_count": 7}
]`
	count, _ := svc.ImportJSON(importData)
	fmt.Printf("  %d명 가져오기 완료\n", count)
	fmt.Println()

	// ── 9. 삭제 ──
	fmt.Println("=== 9. 학생 삭제 ===")
	fmt.Println()

	err = svc.repo.Delete(5)
	if err != nil {
		fmt.Println("  삭제 에러:", err)
	} else {
		fmt.Println("  ID=5 (예린) 삭제 완료")
	}

	err = svc.repo.Delete(999)
	fmt.Println("  존재하지 않는 ID:", err)
	fmt.Println()

	// ── 10. 최종 보고서 ──
	fmt.Println("=== 10. 최종 보고서 ===")
	fmt.Println()
	fmt.Println(svc.GenerateReport())

	fmt.Println("18단계 학습 완료! 모든 과정을 마쳤습니다!")
}
