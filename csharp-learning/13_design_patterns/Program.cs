/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C# 학습 13단계: 디자인 패턴
  ─ Singleton, Factory, Strategy, Observer, Dependency Injection ─

  ■ 컴파일: dotnet build
  ■ 실행:   dotnet run

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  [학습 목표]
  1. 디자인 패턴이 무엇이고 왜 필요한지 이해한다
  2. Singleton 패턴: 인스턴스를 하나만 만들기
  3. Factory 패턴: 객체 생성을 위임하기
  4. Strategy 패턴: 알고리즘을 교체 가능하게 만들기
  5. Observer 패턴: 이벤트 기반 느슨한 결합
  6. Dependency Injection: 의존성을 외부에서 주입하기
  7. 패턴 남용의 위험성을 안다

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Lesson13
{
    // =====================================================================
    // 레슨 1 — 디자인 패턴이란?
    // =====================================================================
    /*
    ★ 디자인 패턴 = 자주 나오는 설계 문제의 검증된 해결법
      → 이름을 알면 개발자끼리 빠르게 소통 가능!

    ★ 비유: 요리 레시피
      "카레 만드는 법"을 매번 새로 고안하지 않고,
      검증된 레시피를 따라 하는 것!
      → 패턴도 검증된 "코드 레시피"

    ★ GoF(Gang of Four) 23가지 패턴 분류
    ┌──────────────┬──────────────────────────────────────┐
    │ 생성 패턴    │ Singleton, Factory, Builder, Prototype│
    │ 구조 패턴    │ Adapter, Decorator, Facade, Proxy    │
    │ 행위 패턴    │ Strategy, Observer, Command, Iterator│
    └──────────────┴──────────────────────────────────────┘

    ★ 주의: 패턴은 도구지 목적이 아님!
      "이 문제에 어떤 패턴을 쓸까?" O
      "어떤 패턴을 써야 하니까 문제를 만들자" X
    */


    // =====================================================================
    // 레슨 2 — Singleton 패턴
    // =====================================================================
    /*
    ★ Singleton = 클래스의 인스턴스가 딱 하나만 존재하게 보장
      → 설정 관리, 로거, DB 연결 풀 등에 사용

    ┌──────────────────────────────────────────────────┐
    │  AppConfig.Instance.Get("key");  // 항상 같은 객체│
    │  AppConfig.Instance.Get("key");  // 위와 동일!   │
    └──────────────────────────────────────────────────┘

    ★ 비유: 학교 교장 선생님
      학교에 교장은 한 명! 누가 물어봐도 같은 교장 선생님
    */

    class AppConfig
    {
        // ★ Lazy<T>: 스레드 안전한 싱글턴 (가장 추천!)
        private static readonly Lazy<AppConfig> _instance
            = new Lazy<AppConfig>(() => new AppConfig());

        public static AppConfig Instance => _instance.Value;

        private readonly Dictionary<string, string> settings;

        // ★ private 생성자: 외부에서 new 불가!
        private AppConfig()
        {
            settings = new Dictionary<string, string>
            {
                ["AppName"] = "학교 관리 시스템",
                ["Version"] = "2.1.0",
                ["MaxStudents"] = "500",
                ["DebugMode"] = "true",
            };
            Console.WriteLine("  [AppConfig] 인스턴스 생성됨 (딱 한 번만!)");
        }

        public string Get(string key)
        {
            return settings.TryGetValue(key, out string? value) ? value : "(없음)";
        }

        public void Set(string key, string value)
        {
            settings[key] = value;
        }
    }


    // =====================================================================
    // 레슨 3 — Factory 패턴
    // =====================================================================
    /*
    ★ Factory = 객체 생성 로직을 한 곳에 모아서 위임
      → 호출하는 쪽은 구체적인 클래스를 몰라도 됨!

    ┌──────────────────────────────────────────────────┐
    │  INotifier notifier = NotifierFactory.Create("email");│
    │  notifier.Send("Hello!");                        │
    │  // Email? SMS? Push? 몰라도 됨!                │
    └──────────────────────────────────────────────────┘

    ★ 비유: 음식점 주문
      "1번 세트요!" → 주방이 알아서 만들어서 줌
      손님은 요리 과정을 몰라도 됨
    */

    interface INotifier
    {
        void Send(string message);
        string Channel { get; }
    }

    class EmailNotifier : INotifier
    {
        public string Channel => "이메일";
        public void Send(string message)
        {
            Console.WriteLine($"  📧 [이메일] {message}");
        }
    }

    class SmsNotifier : INotifier
    {
        public string Channel => "SMS";
        public void Send(string message)
        {
            Console.WriteLine($"  📱 [SMS] {message}");
        }
    }

    class PushNotifier : INotifier
    {
        public string Channel => "푸시알림";
        public void Send(string message)
        {
            Console.WriteLine($"  🔔 [푸시] {message}");
        }
    }

    // ★ Factory: 문자열만으로 적절한 객체를 생성
    static class NotifierFactory
    {
        public static INotifier Create(string channel)
        {
            return channel.ToLower() switch
            {
                "email" => new EmailNotifier(),
                "sms" => new SmsNotifier(),
                "push" => new PushNotifier(),
                _ => throw new ArgumentException($"알 수 없는 채널: {channel}")
            };
        }
    }


    // =====================================================================
    // 레슨 4 — Strategy 패턴
    // =====================================================================
    /*
    ★ Strategy = 알고리즘(규칙)을 교체 가능한 객체로 분리
      → if-else를 끝없이 늘리지 않고, 규칙을 갈아 끼움!

    ┌──────────────────────────────────────────────────┐
    │  문제: 할인 규칙이 계속 추가됨                   │
    │  if (type == "학생") price -= 1000;              │
    │  else if (type == "vip") price -= 2000;          │
    │  else if (type == "직원") price -= 3000;         │
    │  ... (끝없이 늘어남!)                            │
    │                                                  │
    │  해결: Strategy 패턴                             │
    │  IDiscount discount = GetDiscount(type);         │
    │  price = discount.Apply(price);                  │
    └──────────────────────────────────────────────────┘

    ★ 비유: 내비게이션 앱
      "최단 경로", "최소 요금", "고속도로 우선" → 같은 인터페이스, 다른 알고리즘
    */

    interface IDiscountStrategy
    {
        int Apply(int price);
        string Label { get; }
    }

    class NoDiscount : IDiscountStrategy
    {
        public string Label => "일반 가격";
        public int Apply(int price) => price;
    }

    class StudentDiscount : IDiscountStrategy
    {
        public string Label => "학생 할인 (-1000원)";
        public int Apply(int price) => Math.Max(0, price - 1000);
    }

    class VipDiscount : IDiscountStrategy
    {
        public string Label => "VIP 할인 (-20%)";
        public int Apply(int price) => (int)(price * 0.8);
    }

    class CouponDiscount : IDiscountStrategy
    {
        private readonly int couponAmount;

        public CouponDiscount(int amount)
        {
            couponAmount = amount;
        }

        public string Label => $"쿠폰 할인 (-{couponAmount}원)";
        public int Apply(int price) => Math.Max(0, price - couponAmount);
    }

    // ★ 전략을 주입받는 클래스
    class Cashier
    {
        private readonly IDiscountStrategy strategy;

        public Cashier(IDiscountStrategy strategy)
        {
            this.strategy = strategy;
        }

        public void Checkout(string itemName, int price)
        {
            int finalPrice = strategy.Apply(price);
            Console.WriteLine($"  상품: {itemName}");
            Console.WriteLine($"  원가: {price:N0}원 → {strategy.Label}");
            Console.WriteLine($"  결제: {finalPrice:N0}원");
        }
    }


    // =====================================================================
    // 레슨 5 — Observer 패턴
    // =====================================================================
    /*
    ★ Observer = 한 객체의 상태가 바뀌면 구독자들에게 알림
      → C#에서는 event 키워드로 자연스럽게 구현!

    ┌──────────────────────────────────────────────────┐
    │  Publisher (발행자)                               │
    │    → event ScoreChanged                         │
    │                                                  │
    │  Subscriber (구독자)                             │
    │    → 이벤트가 발생하면 자동으로 호출됨          │
    └──────────────────────────────────────────────────┘

    ★ 비유: 유튜브 구독
      채널에 새 영상이 올라오면 구독자에게 알림이 감!
      → 채널 = Publisher, 구독자 = Observer
    */

    class ScoreBoard
    {
        // ★ event: 구독/발행 메커니즘
        public event Action<string, int>? OnScoreUpdated;
        public event Action<string>? OnStudentAdded;

        private readonly Dictionary<string, int> scores = new();

        public void AddStudent(string name, int score)
        {
            scores[name] = score;
            OnStudentAdded?.Invoke(name);
        }

        public void UpdateScore(string name, int newScore)
        {
            if (!scores.ContainsKey(name))
            {
                Console.WriteLine($"  ★ '{name}' 학생을 찾을 수 없습니다.");
                return;
            }
            scores[name] = newScore;
            OnScoreUpdated?.Invoke(name, newScore);  // ★ 구독자들에게 알림!
        }

        public int GetScore(string name)
        {
            return scores.TryGetValue(name, out int s) ? s : -1;
        }
    }

    // 구독자 1: 콘솔 로거
    class ConsoleLogger
    {
        public void OnScoreChanged(string name, int score)
        {
            Console.WriteLine($"  📝 [로그] {name}의 점수가 {score}점으로 변경됨");
        }

        public void OnNewStudent(string name)
        {
            Console.WriteLine($"  📝 [로그] 새 학생 등록: {name}");
        }
    }

    // 구독자 2: 알림 발송기
    class AlertService
    {
        public void OnScoreChanged(string name, int score)
        {
            if (score < 60)
            {
                Console.WriteLine($"  🚨 [경고] {name} 학생 점수 위험! ({score}점)");
            }
            else if (score >= 95)
            {
                Console.WriteLine($"  🎉 [축하] {name} 학생 우수 성적! ({score}점)");
            }
        }
    }


    // =====================================================================
    // 레슨 6 — Dependency Injection (DI)
    // =====================================================================
    /*
    ★ DI = 객체가 필요한 의존성을 직접 만들지 않고 외부에서 받는 것
      → 느슨한 결합 + 테스트 용이성!

    ┌──────────────────────────────────────────────────┐
    │  ✗ 나쁜 예 (직접 생성)                          │
    │  class Service {                                 │
    │      private EmailSender sender = new();  // ★  │
    │  }                                               │
    │                                                  │
    │  ✓ 좋은 예 (DI)                                 │
    │  class Service {                                 │
    │      private IMessageSender sender;              │
    │      Service(IMessageSender s) { sender = s; }   │
    │  }                                               │
    └──────────────────────────────────────────────────┘

    ★ 비유: 자동차와 엔진
      자동차가 엔진을 직접 만들면 엔진 교체가 불가!
      → 엔진을 외부에서 장착해야 가솔린↔전기 교체 가능
    */

    interface IMessageSender
    {
        void Send(string to, string message);
    }

    class EmailSender : IMessageSender
    {
        public void Send(string to, string message)
        {
            Console.WriteLine($"  📧 Email to {to}: {message}");
        }
    }

    class SmsSender : IMessageSender
    {
        public void Send(string to, string message)
        {
            Console.WriteLine($"  📱 SMS to {to}: {message}");
        }
    }

    // 가짜 구현 (테스트용!)
    class FakeSender : IMessageSender
    {
        public List<string> SentMessages { get; } = new();

        public void Send(string to, string message)
        {
            SentMessages.Add($"{to}: {message}");
            Console.WriteLine($"  🧪 [Fake] {to}: {message}");
        }
    }

    // ★ DI를 적용한 서비스
    class NotificationService
    {
        private readonly IMessageSender sender;

        // ★ 생성자 주입: 외부에서 sender를 받음
        public NotificationService(IMessageSender sender)
        {
            this.sender = sender;
        }

        public void NotifyLowScore(string studentName, int score)
        {
            if (score < 60)
            {
                sender.Send(studentName, $"점수가 {score}점입니다. 보충 수업에 참여하세요.");
            }
        }

        public void NotifyHighScore(string studentName, int score)
        {
            if (score >= 95)
            {
                sender.Send(studentName, $"축하합니다! {score}점 달성!");
            }
        }
    }


    // =====================================================================
    // Main
    // =====================================================================
    class Program
    {
        static void Lesson2Singleton()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 2: Singleton — 단 하나의 인스턴스");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // ★ 두 번 접근해도 같은 인스턴스!
            var config1 = AppConfig.Instance;
            var config2 = AppConfig.Instance;

            Console.WriteLine($"  같은 객체? {ReferenceEquals(config1, config2)}");
            Console.WriteLine($"  AppName: {config1.Get("AppName")}");
            Console.WriteLine($"  Version: {config1.Get("Version")}");
            Console.WriteLine();

            // config1에서 변경하면 config2에서도 보임
            config1.Set("Version", "2.2.0");
            Console.WriteLine($"  config2.Version: {config2.Get("Version")} (같은 객체!)");
            Console.WriteLine();
        }

        static void Lesson3Factory()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 3: Factory — 객체 생성 위임");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            string[] channels = { "email", "sms", "push" };

            foreach (string channel in channels)
            {
                INotifier notifier = NotifierFactory.Create(channel);
                Console.Write($"  채널: {notifier.Channel} → ");
                notifier.Send("내일 시험입니다!");
            }
            Console.WriteLine();

            // ★ 잘못된 채널
            try
            {
                NotifierFactory.Create("피둘기");
            }
            catch (ArgumentException ex)
            {
                Console.WriteLine($"  ★ 예외: {ex.Message}");
            }
            Console.WriteLine();
        }

        static void Lesson4Strategy()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 4: Strategy — 규칙 갈아 끼우기");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            IDiscountStrategy[] strategies =
            {
                new NoDiscount(),
                new StudentDiscount(),
                new VipDiscount(),
                new CouponDiscount(1500),
            };

            foreach (var strategy in strategies)
            {
                var cashier = new Cashier(strategy);
                cashier.Checkout("수학 문제집", 5000);
                Console.WriteLine();
            }

            // ★ 핵심: 새 할인 규칙 추가 시
            //    1. IDiscountStrategy를 구현하는 새 클래스 만들기
            //    2. Cashier 코드는 전혀 수정하지 않음!
            Console.WriteLine("  ★ 새 할인 규칙을 추가해도 Cashier 코드는 변경 불필요!");
            Console.WriteLine();
        }

        static void Lesson5Observer()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 5: Observer — 이벤트 기반 알림");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            var board = new ScoreBoard();
            var logger = new ConsoleLogger();
            var alert = new AlertService();

            // ★ 이벤트 구독 (+=)
            board.OnScoreUpdated += logger.OnScoreChanged;
            board.OnScoreUpdated += alert.OnScoreChanged;
            board.OnStudentAdded += logger.OnNewStudent;

            // 학생 추가
            board.AddStudent("민수", 82);
            board.AddStudent("지우", 95);
            Console.WriteLine();

            // 점수 변경 → 구독자들에게 자동 알림!
            Console.WriteLine("  [점수 변경]");
            board.UpdateScore("민수", 55);
            Console.WriteLine();
            board.UpdateScore("지우", 98);
            Console.WriteLine();

            // ★ 구독 해제 (-=)
            board.OnScoreUpdated -= alert.OnScoreChanged;
            Console.WriteLine("  [경고 서비스 구독 해제 후]");
            board.UpdateScore("민수", 45);
            Console.WriteLine("  → 로그만 출력되고 경고는 안 나옴!");
            Console.WriteLine();
        }

        static void Lesson6DependencyInjection()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 6: DI — 의존성 주입");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            // 프로덕션: 이메일로 발송
            Console.WriteLine("  [프로덕션 모드 — EmailSender]");
            var emailService = new NotificationService(new EmailSender());
            emailService.NotifyLowScore("서연", 55);
            emailService.NotifyHighScore("지우", 97);
            Console.WriteLine();

            // 테스트: 가짜 구현으로 교체
            Console.WriteLine("  [테스트 모드 — FakeSender]");
            var fakeSender = new FakeSender();
            var testService = new NotificationService(fakeSender);
            testService.NotifyLowScore("테스트학생", 40);
            Console.WriteLine($"  보낸 메시지 수: {fakeSender.SentMessages.Count}");
            Console.WriteLine();

            Console.WriteLine("  ★ DI의 핵심:");
            Console.WriteLine("    - NotificationService는 IMessageSender만 알면 됨");
            Console.WriteLine("    - Email, SMS, Fake 등 구현체를 자유롭게 교체");
            Console.WriteLine("    - 테스트할 때 가짜 객체를 주입하면 간단!");
            Console.WriteLine();

            // .NET의 DI 컨테이너 소개
            Console.WriteLine("  ★ ASP.NET Core의 내장 DI 컨테이너:");
            Console.WriteLine("    builder.Services.AddSingleton<IMessageSender, EmailSender>();");
            Console.WriteLine("    builder.Services.AddScoped<NotificationService>();");
            Console.WriteLine("    → 프레임워크가 자동으로 의존성을 연결해 줌!");
            Console.WriteLine();
        }

        static void Lesson7PatternOveruse()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 7: 패턴 남용 경고 — 언제 쓰고 언제 안 쓸까");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            Console.WriteLine("  ┌──────────────────────────────────────────────────┐");
            Console.WriteLine("  │ ★ 패턴 사용 판단 기준                          │");
            Console.WriteLine("  ├──────────────────────────────────────────────────┤");
            Console.WriteLine("  │ 쓸 때:                                          │");
            Console.WriteLine("  │  - 같은 구조의 문제가 반복될 때                │");
            Console.WriteLine("  │  - 코드를 확장해야 할 가능성이 높을 때         │");
            Console.WriteLine("  │  - 팀원과 설계 의도를 공유해야 할 때           │");
            Console.WriteLine("  │                                                  │");
            Console.WriteLine("  │ 안 쓸 때:                                       │");
            Console.WriteLine("  │  - 간단한 문제에 복잡한 패턴을 적용할 때       │");
            Console.WriteLine("  │  - 확장 가능성이 없는 일회성 코드일 때         │");
            Console.WriteLine("  │  - 패턴을 쓰기 위해 패턴을 쓰는 것            │");
            Console.WriteLine("  └──────────────────────────────────────────────────┘");
            Console.WriteLine();

            Console.WriteLine("  ★ KISS: Keep It Simple, Stupid!");
            Console.WriteLine("    단순한 if-else로 충분한 곳에 Strategy를 쓰면 오히려 복잡해짐");
            Console.WriteLine();
            Console.WriteLine("  ★ YAGNI: You Ain't Gonna Need It");
            Console.WriteLine("    \"나중에 필요할 것 같아서\" 미리 패턴을 적용하지 말 것");
            Console.WriteLine("    → 실제로 필요해질 때 리팩토링!");
            Console.WriteLine();
        }

        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine("  C# 13단계: 디자인 패턴");
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine();

            Lesson2Singleton();
            Lesson3Factory();
            Lesson4Strategy();
            Lesson5Observer();
            Lesson6DependencyInjection();
            Lesson7PatternOveruse();

            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  ★ 정리");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  1. Singleton: 인스턴스 하나만 (Lazy<T> 추천)");
            Console.WriteLine("  2. Factory: 객체 생성 로직을 한 곳에 모음");
            Console.WriteLine("  3. Strategy: 알고리즘을 교체 가능한 객체로 분리");
            Console.WriteLine("  4. Observer: event로 느슨한 결합 알림");
            Console.WriteLine("  5. DI: 의존성을 외부에서 주입 → 테스트 용이");
            Console.WriteLine("  6. KISS/YAGNI: 필요할 때만 패턴 적용!");
            Console.WriteLine();
        }
    }
}
