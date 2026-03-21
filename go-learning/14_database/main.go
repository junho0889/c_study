/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Go 학습 14단계: 데이터베이스
  ─ database/sql · 준비된 문 · 트랜잭션 · 인메모리 DB 시뮬레이션 ─

  [학습 목표]
  1. database/sql 패키지의 구조를 이해한다
  2. CRUD(생성/조회/수정/삭제) 패턴을 안다
  3. 준비된 문(Prepared Statement)의 필요성을 안다
  4. 트랜잭션의 개념과 사용법을 안다
  5. SQL 인젝션 방지법을 안다

  ■ 실행: go run main.go
  ■ 빌드: go build -o 14_database main.go

  ★ 이 파일은 실제 DB 없이 슬라이스로 DB를 시뮬레이션합니다.

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

package main

import (
	"errors"
	"fmt"
)

func main() {
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println("  Go 14단계 : 데이터베이스")
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println()

	lesson1DatabaseSQLOverview()
	lesson2InMemoryDB()
	lesson3CRUD()
	lesson4PreparedStatement()
	lesson5Transaction()
	lesson6SQLInjection()
	lesson7ConnectionPool()
	lesson8ORMOverview()

	fmt.Println("14단계 학습 완료!")
}

// ── 인메모리 DB 시뮬레이션 ──

type StudentRow struct {
	ID    int
	Name  string
	Score int
}

type InMemoryDB struct {
	rows   []StudentRow
	nextID int
}

func NewInMemoryDB() *InMemoryDB {
	return &InMemoryDB{nextID: 1}
}

// Insert — CREATE
func (db *InMemoryDB) Insert(name string, score int) (int, error) {
	if name == "" {
		return 0, errors.New("이름이 비어있습니다")
	}
	if score < 0 || score > 100 {
		return 0, fmt.Errorf("점수 %d는 범위 밖입니다", score)
	}
	row := StudentRow{ID: db.nextID, Name: name, Score: score}
	db.rows = append(db.rows, row)
	db.nextID++
	return row.ID, nil
}

// SelectAll — READ (전체)
func (db *InMemoryDB) SelectAll() []StudentRow {
	result := make([]StudentRow, len(db.rows))
	copy(result, db.rows)
	return result
}

// SelectByID — READ (단건)
func (db *InMemoryDB) SelectByID(id int) (StudentRow, error) {
	for _, row := range db.rows {
		if row.ID == id {
			return row, nil
		}
	}
	return StudentRow{}, fmt.Errorf("ID %d를 찾을 수 없습니다", id)
}

// SelectAbove — READ (조건)
func (db *InMemoryDB) SelectAbove(minScore int) []StudentRow {
	var result []StudentRow
	for _, row := range db.rows {
		if row.Score >= minScore {
			result = append(result, row)
		}
	}
	return result
}

// Update — UPDATE
func (db *InMemoryDB) Update(id int, newScore int) error {
	for i := range db.rows {
		if db.rows[i].ID == id {
			db.rows[i].Score = newScore
			return nil
		}
	}
	return fmt.Errorf("ID %d를 찾을 수 없습니다", id)
}

// Delete — DELETE
func (db *InMemoryDB) Delete(id int) error {
	for i, row := range db.rows {
		if row.ID == id {
			db.rows = append(db.rows[:i], db.rows[i+1:]...)
			return nil
		}
	}
	return fmt.Errorf("ID %d를 찾을 수 없습니다", id)
}

// =====================================================================
// 레슨 1 — database/sql 개요
// =====================================================================
func lesson1DatabaseSQLOverview() {
	fmt.Println("[레슨 1] database/sql: Go의 DB 표준 인터페이스")
	fmt.Println()

	/*
	   ★ database/sql 은 "인터페이스"만 제공한다!
	   실제 DB 연결에는 "드라이버"가 별도로 필요하다.

	   ┌──────────────────────────────────────────────────┐
	   │  DB 종류        │  드라이버 패키지                  │
	   ├──────────────────────────────────────────────────┤
	   │  PostgreSQL     │  github.com/lib/pq              │
	   │  MySQL          │  github.com/go-sql-driver/mysql │
	   │  SQLite         │  github.com/mattn/go-sqlite3    │
	   │  SQL Server     │  github.com/denisenkom/go-mssqldb│
	   └──────────────────────────────────────────────────┘

	   ★ 연결 패턴:
	   ──────────────────────────────────────────
	   import (
	       "database/sql"
	       _ "github.com/lib/pq"  ← 드라이버 등록 (init)
	   )

	   db, err := sql.Open("postgres",
	       "host=localhost port=5432 user=admin dbname=school sslmode=disable")
	   if err != nil { log.Fatal(err) }
	   defer db.Close()

	   // 연결 확인
	   err = db.Ping()
	   if err != nil { log.Fatal(err) }
	   ──────────────────────────────────────────

	   ★ sql.Open은 실제로 연결하지 않는다!
	   → db.Ping()으로 확인해야 한다!
	*/

	fmt.Println("  1. sql.Open(드라이버, 연결문자열) → *sql.DB")
	fmt.Println("  2. db.Ping() → 실제 연결 확인")
	fmt.Println("  3. defer db.Close() → 종료 시 정리")
	fmt.Println("  ★ sql.Open은 연결하지 않음! Ping으로 확인!")

	fmt.Println()
}

// =====================================================================
// 레슨 2 — 인메모리 DB 시뮬레이션
// =====================================================================
func lesson2InMemoryDB() {
	fmt.Println("[레슨 2] 인메모리 DB: 슬라이스로 DB를 흉내내기")
	fmt.Println()

	db := NewInMemoryDB()

	// 데이터 추가
	db.Insert("민수", 85)
	db.Insert("지우", 92)
	db.Insert("서연", 78)

	// 전체 조회
	all := db.SelectAll()
	fmt.Println("  전체 데이터:")
	for _, row := range all {
		fmt.Printf("    ID=%d  이름=%s  점수=%d\n", row.ID, row.Name, row.Score)
	}

	fmt.Println()
}

// =====================================================================
// 레슨 3 — CRUD 패턴
// =====================================================================
func lesson3CRUD() {
	fmt.Println("[레슨 3] CRUD: Create, Read, Update, Delete")
	fmt.Println()

	/*
	   ★ CRUD = 데이터의 4가지 기본 연산

	   ┌──────────┬──────────────────────┬──────────────────┐
	   │  CRUD    │  SQL                 │  HTTP 메서드       │
	   ├──────────┼──────────────────────┼──────────────────┤
	   │  Create  │  INSERT INTO ...     │  POST             │
	   │  Read    │  SELECT ... FROM ... │  GET              │
	   │  Update  │  UPDATE ... SET ...  │  PUT / PATCH      │
	   │  Delete  │  DELETE FROM ...     │  DELETE           │
	   └──────────┴──────────────────────┴──────────────────┘
	*/

	db := NewInMemoryDB()

	// CREATE
	id, _ := db.Insert("민수", 85)
	fmt.Println("  [Create] 민수 추가, ID:", id)

	id2, _ := db.Insert("지우", 72)
	fmt.Println("  [Create] 지우 추가, ID:", id2)

	// READ (단건)
	student, err := db.SelectByID(1)
	if err == nil {
		fmt.Printf("  [Read] ID=1: %s %d점\n", student.Name, student.Score)
	}

	// UPDATE
	db.Update(1, 90)
	student, _ = db.SelectByID(1)
	fmt.Printf("  [Update] 민수 점수 변경: %d점\n", student.Score)

	// DELETE
	db.Delete(2)
	all := db.SelectAll()
	fmt.Printf("  [Delete] 지우 삭제 후 남은 수: %d명\n", len(all))

	// READ (조건)
	db.Insert("서연", 88)
	db.Insert("하준", 65)
	above80 := db.SelectAbove(80)
	fmt.Println("  [Read] 80점 이상:")
	for _, s := range above80 {
		fmt.Printf("    %s: %d점\n", s.Name, s.Score)
	}

	fmt.Println()
}

// =====================================================================
// 레슨 4 — 준비된 문 (Prepared Statement)
// =====================================================================
func lesson4PreparedStatement() {
	fmt.Println("[레슨 4] 준비된 문: 같은 쿼리를 반복할 때 효율적")
	fmt.Println()

	/*
	   ★ Prepared Statement = SQL을 미리 컴파일해 두고 재사용

	   장점:
	   1. 성능 향상 (같은 쿼리 반복 시)
	   2. SQL 인젝션 방지!
	   3. 타입 안전

	   ──────────────────────────────────────────
	   // 준비
	   stmt, err := db.Prepare("INSERT INTO students(name, score) VALUES($1, $2)")
	   if err != nil { log.Fatal(err) }
	   defer stmt.Close()

	   // 반복 사용
	   stmt.Exec("민수", 85)
	   stmt.Exec("지우", 92)
	   stmt.Exec("서연", 78)
	   ──────────────────────────────────────────

	   ★ 쿼리 실행 메서드 구분:
	   ┌────────────────────┬──────────────────────────┐
	   │  db.Query(sql)     │  SELECT (여러 행)          │
	   │  db.QueryRow(sql)  │  SELECT (한 행)            │
	   │  db.Exec(sql)      │  INSERT/UPDATE/DELETE      │
	   └────────────────────┴──────────────────────────┘

	   ★ Query 사용 시 반드시 rows.Close() 해야 한다!
	   rows, err := db.Query("SELECT * FROM students")
	   defer rows.Close()  ← 필수!
	*/

	fmt.Println("  db.Prepare(sql) → *sql.Stmt")
	fmt.Println("  stmt.Exec(args...) → INSERT/UPDATE/DELETE")
	fmt.Println("  stmt.Query(args...) → SELECT (여러 행)")
	fmt.Println("  stmt.QueryRow(args...) → SELECT (한 행)")
	fmt.Println("  ★ defer stmt.Close() 필수!")

	fmt.Println()
}

// =====================================================================
// 레슨 5 — 트랜잭션
// =====================================================================

// TransferScore — 점수 이전 (트랜잭션 시뮬레이션)
func TransferScore(db *InMemoryDB, fromID, toID, amount int) error {
	// 보내는 학생 조회
	from, err := db.SelectByID(fromID)
	if err != nil {
		return fmt.Errorf("보내는 학생 조회 실패: %w", err)
	}

	// 받는 학생 조회
	to, err := db.SelectByID(toID)
	if err != nil {
		return fmt.Errorf("받는 학생 조회 실패: %w", err)
	}

	// 검증
	if from.Score < amount {
		return fmt.Errorf("점수 부족 (보유: %d, 필요: %d)", from.Score, amount)
	}

	// 실행 (실제로는 트랜잭션 안에서!)
	db.Update(fromID, from.Score-amount)
	db.Update(toID, to.Score+amount)

	return nil
}

func lesson5Transaction() {
	fmt.Println("[레슨 5] 트랜잭션: 여러 작업을 하나로 묶기")
	fmt.Println()

	/*
	   ★ 트랜잭션 = "전부 성공하거나, 전부 실패하거나"

	   비유: 은행 송금 — 내 계좌에서 빠지고 상대 계좌에 들어가야 한다.
	         하나만 성공하면 돈이 사라지는 사고!

	   ──────────────────────────────────────────
	   tx, err := db.Begin()         // 트랜잭션 시작
	   if err != nil { return err }

	   _, err = tx.Exec("UPDATE accounts SET balance = balance - $1 WHERE id = $2", 100, 1)
	   if err != nil {
	       tx.Rollback()             // 실패 → 되돌리기!
	       return err
	   }

	   _, err = tx.Exec("UPDATE accounts SET balance = balance + $1 WHERE id = $2", 100, 2)
	   if err != nil {
	       tx.Rollback()             // 실패 → 되돌리기!
	       return err
	   }

	   return tx.Commit()           // 성공 → 확정!
	   ──────────────────────────────────────────

	   ★ 트랜잭션의 ACID:
	   A (Atomicity)    → 전부 성공 or 전부 실패
	   C (Consistency)  → 규칙(제약)을 항상 만족
	   I (Isolation)    → 동시 작업이 서로 방해하지 않음
	   D (Durability)   → 커밋되면 영구 저장
	*/

	db := NewInMemoryDB()
	db.Insert("민수", 90) // ID=1
	db.Insert("지우", 70) // ID=2

	fmt.Println("  [이전 전]")
	printDB(db)

	err := TransferScore(db, 1, 2, 20)
	if err != nil {
		fmt.Println("  이전 실패:", err)
	} else {
		fmt.Println("  [이전 후] 민수→지우 20점 이전")
		printDB(db)
	}

	// 실패 케이스
	err = TransferScore(db, 1, 2, 200)
	if err != nil {
		fmt.Println("  200점 이전 시도:", err)
	}

	fmt.Println()
}

func printDB(db *InMemoryDB) {
	for _, row := range db.SelectAll() {
		fmt.Printf("    ID=%d  %s  %d점\n", row.ID, row.Name, row.Score)
	}
}

// =====================================================================
// 레슨 6 — SQL 인젝션 방지
// =====================================================================
func lesson6SQLInjection() {
	fmt.Println("[레슨 6] SQL 인젝션: 보안의 기본 중 기본!")
	fmt.Println()

	/*
	   ★ SQL 인젝션 = 사용자 입력을 SQL에 직접 넣어서 DB를 조작하는 공격

	   ┌────────────────────────────────────────────────────────┐
	   │  ★★★ 위험한 코드 (절대 하지 마라!) ★★★                  │
	   │                                                       │
	   │  name := r.FormValue("name")                          │
	   │  query := "SELECT * FROM students WHERE name='" + name + "'" │
	   │  db.Query(query)                                       │
	   │                                                       │
	   │  만약 name = "'; DROP TABLE students; --" 이면?         │
	   │  → SELECT * FROM students WHERE name='';               │
	   │    DROP TABLE students; --'                             │
	   │  → 테이블 삭제! 😱                                     │
	   ├────────────────────────────────────────────────────────┤
	   │  ★ 안전한 코드 (항상 이렇게!)                            │
	   │                                                       │
	   │  db.Query("SELECT * FROM students WHERE name=$1", name) │
	   │                                                  ^^    │
	   │  플레이스홀더($1)를 사용하면 자동으로 이스케이프!          │
	   └────────────────────────────────────────────────────────┘
	*/

	// 시뮬레이션: 위험한 쿼리 vs 안전한 쿼리
	userInput := "'; DROP TABLE students; --"

	// 위험한 방법
	dangerousQuery := "SELECT * FROM students WHERE name='" + userInput + "'"
	fmt.Println("  [위험!] 문자열 직접 조합:")
	fmt.Println("  ", dangerousQuery)

	// 안전한 방법
	safeQuery := "SELECT * FROM students WHERE name=$1"
	fmt.Println()
	fmt.Println("  [안전!] 플레이스홀더 사용:")
	fmt.Printf("    쿼리: %s\n", safeQuery)
	fmt.Printf("    인자: %s\n", userInput)
	fmt.Println("  → DB 드라이버가 자동으로 이스케이프!")

	fmt.Println()
}

// =====================================================================
// 레슨 7 — 커넥션 풀
// =====================================================================
func lesson7ConnectionPool() {
	fmt.Println("[레슨 7] 커넥션 풀: DB 연결을 재사용하기")
	fmt.Println()

	/*
	   ★ sql.DB는 단일 연결이 아니라 "커넥션 풀"이다!
	   매번 새 연결을 만들지 않고, 풀에서 빌려 쓰고 반납한다.

	   ┌──────────────────────────────────────────────┐
	   │  커넥션 풀 설정:                               │
	   │  db.SetMaxOpenConns(25)   ← 최대 동시 연결 수  │
	   │  db.SetMaxIdleConns(5)    ← 유휴 연결 유지 수  │
	   │  db.SetConnMaxLifetime(5 * time.Minute)       │
	   │                          ← 연결 최대 수명      │
	   │  db.SetConnMaxIdleTime(1 * time.Minute)       │
	   │                          ← 유휴 연결 만료 시간  │
	   └──────────────────────────────────────────────┘

	   ★ 왜 커넥션 풀이 필요한가?
	   1. 매번 연결 생성은 느리다 (TCP 핸드셰이크 + 인증)
	   2. DB가 감당할 수 있는 연결 수에 한계가 있다
	   3. 연결을 재사용하면 성능이 크게 향상된다

	   ★ 흔한 실수:
	   - rows.Close()를 안 하면 연결이 풀에 반환되지 않는다!
	   - 트랜잭션(tx)을 Commit/Rollback 안 하면 연결이 묶인다!
	*/

	fmt.Println("  db.SetMaxOpenConns(25)  → 최대 동시 연결")
	fmt.Println("  db.SetMaxIdleConns(5)   → 유휴 연결 유지")
	fmt.Println("  ★ rows.Close() 안 하면 → 연결 누수!")
	fmt.Println("  ★ tx.Commit/Rollback 안 하면 → 연결 묶임!")

	fmt.Println()
}

// =====================================================================
// 레슨 8 — ORM 개요
// =====================================================================
func lesson8ORMOverview() {
	fmt.Println("[레슨 8] ORM: SQL 대신 Go 코드로 DB 조작")
	fmt.Println()

	/*
	   ★ ORM = Object-Relational Mapping
	   SQL을 직접 쓰지 않고 Go 구조체와 메서드로 DB를 다루는 도구

	   ┌──────────────────────────────────────────────────────┐
	   │  database/sql (직접 SQL)                              │
	   │  ────────────────────────                             │
	   │  db.Query("SELECT * FROM students WHERE score > $1", 80)│
	   │                                                      │
	   │  GORM (ORM)                                          │
	   │  ────────────────────────                             │
	   │  db.Where("score > ?", 80).Find(&students)           │
	   │                                                      │
	   │  sqlx (sql 확장)                                      │
	   │  ────────────────────────                             │
	   │  sqlx.Select(db, &students,                          │
	   │      "SELECT * FROM students WHERE score > $1", 80)   │
	   └──────────────────────────────────────────────────────┘

	   ★ 인기 있는 Go DB 도구:
	   ┌──────────┬────────────────────────────────┐
	   │ GORM     │ 가장 인기. 마이그레이션 내장      │
	   │ sqlx     │ sql 확장. 구조체에 자동 매핑      │
	   │ sqlc     │ SQL에서 Go 코드 자동 생성!        │
	   │ ent      │ Facebook의 Go ORM               │
	   │ bun      │ 경량 ORM                         │
	   └──────────┴────────────────────────────────┘

	   ★ 선택 가이드:
	   단순한 프로젝트 → database/sql + sqlx
	   빠른 개발      → GORM
	   타입 안전성     → sqlc (SQL에서 코드 생성)
	   대규모 프로젝트 → ent
	*/

	fmt.Println("  database/sql: 직접 SQL (가장 기본)")
	fmt.Println("  sqlx: sql 확장 (구조체 자동 매핑)")
	fmt.Println("  GORM: ORM (마이그레이션 내장)")
	fmt.Println("  sqlc: SQL → Go 코드 자동 생성")

	fmt.Println()
}
