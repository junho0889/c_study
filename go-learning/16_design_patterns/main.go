/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Go 학습 16단계: 디자인 패턴
  ─ 전략 · 옵저버 · 팩토리 · 싱글턴 · 데코레이터 · 의존성 주입 ─

  [학습 목표]
  1. Go에서 디자인 패턴을 "인터페이스 + 조합"으로 구현한다
  2. 전략(Strategy) 패턴으로 알고리즘을 교체한다
  3. 옵저버(Observer) 패턴으로 이벤트를 알린다
  4. 팩토리(Factory) 패턴으로 객체 생성을 캡슐화한다
  5. 의존성 주입(DI) 패턴을 이해한다

  ■ 실행: go run main.go
  ■ 빌드: go build -o 16_patterns main.go

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

package main

import (
	"fmt"
	"strings"
	"sync"
)

func main() {
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println("  Go 16단계 : 디자인 패턴")
	fmt.Println("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
	fmt.Println()

	lesson1Strategy()
	lesson2Observer()
	lesson3Factory()
	lesson4Singleton()
	lesson5Decorator()
	lesson6DependencyInjection()
	lesson7OptionPattern()
	lesson8PatternSummary()

	fmt.Println("16단계 학습 완료!")
}

// =====================================================================
// 레슨 1 — 전략 패턴 (Strategy)
// =====================================================================

/*
   ★ 전략 패턴 = 알고리즘을 인터페이스로 분리하여 교체 가능하게

   비유: 네비게이션에서 "최단 거리", "최소 시간", "고속도로 우선"을
         상황에 따라 바꿔 끼울 수 있는 것!

   ┌─────────────────────────────────────┐
   │  DiscountStrategy 인터페이스         │
   ├─────────────────────────────────────┤
   │  Apply(price int) int              │
   └─────────────────────────────────────┘
        ↑              ↑             ↑
   NoDiscount   StudentDiscount  SeasonDiscount
*/

type DiscountStrategy interface {
	Apply(price int) int
	Name() string
}

type NoDiscount struct{}
type StudentDiscount struct{}
type SeasonDiscount struct{ Percent int }

func (d NoDiscount) Apply(price int) int      { return price }
func (d NoDiscount) Name() string              { return "할인 없음" }
func (d StudentDiscount) Apply(price int) int  { return price * 80 / 100 }
func (d StudentDiscount) Name() string         { return "학생 할인(20%)" }
func (d SeasonDiscount) Apply(price int) int   { return price * (100 - d.Percent) / 100 }
func (d SeasonDiscount) Name() string          { return fmt.Sprintf("시즌 할인(%d%%)", d.Percent) }

type PaymentProcessor struct {
	discount DiscountStrategy
}

func (p *PaymentProcessor) SetDiscount(d DiscountStrategy) {
	p.discount = d
}

func (p *PaymentProcessor) Calculate(price int) int {
	if p.discount == nil {
		return price
	}
	return p.discount.Apply(price)
}

func lesson1Strategy() {
	fmt.Println("[레슨 1] 전략 패턴: 알고리즘을 교체 가능하게")
	fmt.Println()

	processor := &PaymentProcessor{}
	originalPrice := 10000

	strategies := []DiscountStrategy{
		NoDiscount{},
		StudentDiscount{},
		SeasonDiscount{Percent: 30},
	}

	for _, s := range strategies {
		processor.SetDiscount(s)
		final := processor.Calculate(originalPrice)
		fmt.Printf("  %-20s: %d원 → %d원\n", s.Name(), originalPrice, final)
	}

	/*
	   ★ Go에서 전략 패턴의 또 다른 방법: 함수를 직접 전달!

	   type DiscountFunc func(int) int

	   halfOff := func(price int) int { return price / 2 }
	   calculate(10000, halfOff)

	   → 간단한 전략은 함수가 더 Go다운 방법!
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 2 — 옵저버 패턴 (Observer)
// =====================================================================

/*
   ★ 옵저버 패턴 = "이벤트가 발생하면 등록된 관찰자들에게 알린다"

   비유: 유튜브 구독 — 새 영상이 올라오면 구독자 전원에게 알림!
*/

type EventListener interface {
	OnEvent(event string, data string)
}

type EventBus struct {
	listeners map[string][]EventListener
}

func NewEventBus() *EventBus {
	return &EventBus{listeners: make(map[string][]EventListener)}
}

func (eb *EventBus) Subscribe(event string, listener EventListener) {
	eb.listeners[event] = append(eb.listeners[event], listener)
}

func (eb *EventBus) Publish(event string, data string) {
	for _, listener := range eb.listeners[event] {
		listener.OnEvent(event, data)
	}
}

// 로그 리스너
type LogListener struct{ Prefix string }

func (l LogListener) OnEvent(event, data string) {
	fmt.Printf("    [%s] 이벤트=%s 데이터=%s\n", l.Prefix, event, data)
}

// 알림 리스너
type AlertListener struct{}

func (a AlertListener) OnEvent(event, data string) {
	fmt.Printf("    [알림] ★ %s: %s\n", event, data)
}

func lesson2Observer() {
	fmt.Println("[레슨 2] 옵저버 패턴: 이벤트 기반 알림")
	fmt.Println()

	bus := NewEventBus()

	// 리스너 등록
	bus.Subscribe("학생추가", LogListener{Prefix: "LOG"})
	bus.Subscribe("학생추가", AlertListener{})
	bus.Subscribe("점수변경", LogListener{Prefix: "LOG"})

	// 이벤트 발행
	fmt.Println("  --- '학생추가' 이벤트 ---")
	bus.Publish("학생추가", "민수(85점)")

	fmt.Println("  --- '점수변경' 이벤트 ---")
	bus.Publish("점수변경", "민수: 85→92")

	fmt.Println()
}

// =====================================================================
// 레슨 3 — 팩토리 패턴 (Factory)
// =====================================================================

/*
   ★ 팩토리 패턴 = 객체 생성을 함수로 캡슐화

   비유: 자동차 공장에서 "세단", "SUV", "트럭"을
         주문에 따라 만들어 주는 것
*/

type Notifier interface {
	Send(message string) string
}

type EmailNotifier struct{ To string }
type SMSNotifier struct{ Phone string }
type SlackNotifier struct{ Channel string }

func (e EmailNotifier) Send(msg string) string {
	return fmt.Sprintf("이메일→%s: %s", e.To, msg)
}
func (s SMSNotifier) Send(msg string) string {
	return fmt.Sprintf("SMS→%s: %s", s.Phone, msg)
}
func (s SlackNotifier) Send(msg string) string {
	return fmt.Sprintf("Slack→#%s: %s", s.Channel, msg)
}

// 팩토리 함수!
func NewNotifier(nType string, target string) (Notifier, error) {
	switch nType {
	case "email":
		return EmailNotifier{To: target}, nil
	case "sms":
		return SMSNotifier{Phone: target}, nil
	case "slack":
		return SlackNotifier{Channel: target}, nil
	default:
		return nil, fmt.Errorf("알 수 없는 알림 타입: %s", nType)
	}
}

func lesson3Factory() {
	fmt.Println("[레슨 3] 팩토리 패턴: 타입 문자열로 객체 생성")
	fmt.Println()

	configs := []struct {
		nType  string
		target string
	}{
		{"email", "admin@school.com"},
		{"sms", "010-1234-5678"},
		{"slack", "general"},
		{"fax", "02-1234-5678"}, // 지원하지 않는 타입
	}

	for _, c := range configs {
		n, err := NewNotifier(c.nType, c.target)
		if err != nil {
			fmt.Printf("  [에러] %s\n", err)
			continue
		}
		fmt.Printf("  %s\n", n.Send("새 학생이 등록되었습니다"))
	}

	fmt.Println()
}

// =====================================================================
// 레슨 4 — 싱글턴 패턴 (Singleton)
// =====================================================================

/*
   ★ 싱글턴 = 프로그램 전체에서 딱 하나만 존재하는 객체

   Go에서는 sync.Once를 사용한다!
   init()으로도 가능하지만 sync.Once가 더 유연하다.
*/

type AppConfig struct {
	AppName string
	Version string
	Debug   bool
}

var (
	configInstance *AppConfig
	configOnce     sync.Once
)

func GetConfig() *AppConfig {
	configOnce.Do(func() {
		// 이 함수는 딱 한 번만 실행된다! (동시성 안전!)
		configInstance = &AppConfig{
			AppName: "학생관리시스템",
			Version: "1.0.0",
			Debug:   false,
		}
	})
	return configInstance
}

func lesson4Singleton() {
	fmt.Println("[레슨 4] 싱글턴: sync.Once로 딱 하나만 만들기")
	fmt.Println()

	c1 := GetConfig()
	c2 := GetConfig()

	fmt.Printf("  c1: %+v\n", c1)
	fmt.Printf("  c2: %+v\n", c2)
	fmt.Printf("  같은 객체인가? %v (포인터 비교)\n", c1 == c2)

	/*
	   ★ sync.Once의 장점:
	   1. 고루틴 안전 (여러 고루틴이 동시에 호출해도 딱 한 번만 실행)
	   2. 지연 초기화 (처음 호출할 때 생성)
	   3. 간결한 코드

	   ★ 주의: 싱글턴은 테스트하기 어렵다!
	   → 가능하면 의존성 주입(DI)을 쓰자
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 5 — 데코레이터 패턴 (Decorator)
// =====================================================================

/*
   ★ 데코레이터 = 기존 기능에 새 기능을 겹겹이 추가

   Go에서는 "함수를 감싸는 함수"로 깔끔하게 구현!
   (미들웨어와 같은 원리)
*/

type StringTransformer func(string) string

// 기본 변환기
func identity(s string) string { return s }

// 데코레이터: 대문자로
func withUpper(next StringTransformer) StringTransformer {
	return func(s string) string {
		return strings.ToUpper(next(s))
	}
}

// 데코레이터: 괄호 추가
func withBrackets(next StringTransformer) StringTransformer {
	return func(s string) string {
		return "[" + next(s) + "]"
	}
}

// 데코레이터: 접두사 추가
func withPrefix(prefix string) func(StringTransformer) StringTransformer {
	return func(next StringTransformer) StringTransformer {
		return func(s string) string {
			return prefix + next(s)
		}
	}
}

func lesson5Decorator() {
	fmt.Println("[레슨 5] 데코레이터: 함수를 겹겹이 감싸기")
	fmt.Println()

	input := "hello go"

	// 기본
	fmt.Println("  기본:", identity(input))

	// 대문자만
	upper := withUpper(identity)
	fmt.Println("  대문자:", upper(input))

	// 괄호 + 대문자 (안에서 밖으로 적용)
	bracketUpper := withBrackets(withUpper(identity))
	fmt.Println("  괄호+대문자:", bracketUpper(input))

	// 접두사 + 괄호 + 대문자
	full := withPrefix("★ ")(withBrackets(withUpper(identity)))
	fmt.Println("  전체:", full(input))

	/*
	   ★ 실행 순서 (안에서 밖으로):
	   identity("hello go")     → "hello go"
	   withUpper(...)           → "HELLO GO"
	   withBrackets(...)        → "[HELLO GO]"
	   withPrefix("★ ")(...)   → "★ [HELLO GO]"
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 6 — 의존성 주입 (Dependency Injection)
// =====================================================================

/*
   ★ 의존성 주입 = "필요한 것을 직접 만들지 말고 밖에서 받아라"

   비유: 요리사가 재료를 직접 사러 가는 대신,
         재료가 주방에 배달되어 오는 것!

   장점:
   1. 테스트할 때 가짜(mock) 객체를 넣을 수 있다
   2. 구현체를 쉽게 교체할 수 있다
   3. 느슨한 결합 (loosely coupled)
*/

type StudentRepository interface {
	FindByID(id int) (string, int, error)
	Save(name string, score int) error
}

// 실제 구현체
type MemoryStudentRepo struct {
	data map[int]struct{ Name string; Score int }
	nextID int
}

func NewMemoryStudentRepo() *MemoryStudentRepo {
	return &MemoryStudentRepo{
		data: make(map[int]struct{ Name string; Score int }),
		nextID: 1,
	}
}

func (r *MemoryStudentRepo) FindByID(id int) (string, int, error) {
	s, ok := r.data[id]
	if !ok {
		return "", 0, fmt.Errorf("ID %d 없음", id)
	}
	return s.Name, s.Score, nil
}

func (r *MemoryStudentRepo) Save(name string, score int) error {
	r.data[r.nextID] = struct{ Name string; Score int }{name, score}
	r.nextID++
	return nil
}

// 서비스: Repository를 "주입" 받는다!
type StudentService struct {
	repo StudentRepository // ← 인터페이스! 구현체를 몰라도 됨
}

func NewStudentService(repo StudentRepository) *StudentService {
	return &StudentService{repo: repo}
}

func (s *StudentService) Register(name string, score int) error {
	return s.repo.Save(name, score)
}

func (s *StudentService) GetInfo(id int) string {
	name, score, err := s.repo.FindByID(id)
	if err != nil {
		return fmt.Sprintf("에러: %s", err)
	}
	return fmt.Sprintf("%s: %d점", name, score)
}

func lesson6DependencyInjection() {
	fmt.Println("[레슨 6] 의존성 주입: 인터페이스로 구현체를 교체 가능하게")
	fmt.Println()

	// 실제 구현체를 주입
	repo := NewMemoryStudentRepo()
	service := NewStudentService(repo) // ← 의존성 주입!

	service.Register("민수", 85)
	service.Register("지우", 92)

	fmt.Println("  ID=1:", service.GetInfo(1))
	fmt.Println("  ID=2:", service.GetInfo(2))
	fmt.Println("  ID=9:", service.GetInfo(9))

	/*
	   ★ 테스트할 때는 가짜 repo를 넣으면 된다:

	   type MockRepo struct{}
	   func (m MockRepo) FindByID(id int) (string, int, error) {
	       return "테스트", 100, nil
	   }

	   service := NewStudentService(MockRepo{})
	   // → DB 없이 서비스 로직만 테스트 가능!
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 7 — 옵션 패턴 (Functional Options)
// =====================================================================

/*
   ★ 함수형 옵션 = Go에서 선택적 설정을 깔끔하게 전달하는 패턴

   문제: Go에는 기본 매개변수(default parameter)가 없다!
   해결: 옵션을 함수로 전달
*/

type Server struct {
	Host    string
	Port    int
	Timeout int
	Debug   bool
}

type ServerOption func(*Server)

func WithPort(port int) ServerOption {
	return func(s *Server) { s.Port = port }
}

func WithTimeout(timeout int) ServerOption {
	return func(s *Server) { s.Timeout = timeout }
}

func WithDebug(debug bool) ServerOption {
	return func(s *Server) { s.Debug = debug }
}

func NewServer(host string, opts ...ServerOption) *Server {
	s := &Server{
		Host:    host,
		Port:    8080,    // 기본값
		Timeout: 30,      // 기본값
		Debug:   false,   // 기본값
	}
	for _, opt := range opts {
		opt(s)
	}
	return s
}

func lesson7OptionPattern() {
	fmt.Println("[레슨 7] 함수형 옵션 패턴: 깔끔한 선택적 설정")
	fmt.Println()

	// 기본값만
	s1 := NewServer("localhost")
	fmt.Printf("  기본: %+v\n", s1)

	// 일부 옵션
	s2 := NewServer("0.0.0.0", WithPort(3000))
	fmt.Printf("  포트 변경: %+v\n", s2)

	// 모든 옵션
	s3 := NewServer("0.0.0.0",
		WithPort(9090),
		WithTimeout(60),
		WithDebug(true),
	)
	fmt.Printf("  전부 설정: %+v\n", s3)

	/*
	   ★ 이 패턴의 장점:
	   1. 기본값이 자연스럽다
	   2. 옵션 추가 시 기존 코드 변경 불필요
	   3. 가독성이 좋다 (이름이 있는 옵션)
	   4. 표준 라이브러리에서도 많이 사용
	*/

	fmt.Println()
}

// =====================================================================
// 레슨 8 — 패턴 정리
// =====================================================================
func lesson8PatternSummary() {
	fmt.Println("[레슨 8] Go 디자인 패턴 정리")
	fmt.Println()

	fmt.Println("  ┌──────────────────┬──────────────────────────────────────┐")
	fmt.Println("  │  패턴            │  Go에서의 핵심                        │")
	fmt.Println("  ├──────────────────┼──────────────────────────────────────┤")
	fmt.Println("  │  전략            │  인터페이스로 알고리즘 교체             │")
	fmt.Println("  │  옵저버          │  인터페이스 슬라이스로 이벤트 알림      │")
	fmt.Println("  │  팩토리          │  NewXxx() 함수로 객체 생성             │")
	fmt.Println("  │  싱글턴          │  sync.Once로 한 번만 초기화            │")
	fmt.Println("  │  데코레이터      │  함수를 감싸는 함수 (미들웨어)          │")
	fmt.Println("  │  의존성 주입     │  인터페이스를 인자로 받기               │")
	fmt.Println("  │  함수형 옵션     │  가변 인자 함수로 선택적 설정           │")
	fmt.Println("  └──────────────────┴──────────────────────────────────────┘")
	fmt.Println()
	fmt.Println("  ★ Go의 패턴 철학:")
	fmt.Println("  \"인터페이스는 작게, 조합(composition)으로 크게\"")
	fmt.Println("  \"상속 대신 임베딩, 프레임워크 대신 라이브러리\"")

	fmt.Println()
}
