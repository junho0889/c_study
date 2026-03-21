using System;
using System.Collections.Generic;

namespace ArchitectureLearning.StrategyDecorator
{
    /*
    ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
      전략 패턴 + 데코레이터 패턴 (Strategy & Decorator)
      실행 방법: dotnet script example.cs  또는  csc example.cs && example.exe
    ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

      전략 패턴이란?
      "같은 일을 하는 여러 방법" 중에서 하나를 골라 쓸 수 있게 하는 패턴입니다.
      비유: 학교에서 집에 가는 방법 — 버스, 지하철, 자전거, 걸어가기
            "교통수단"이라는 인터페이스는 같지만, 실제 방법은 다릅니다.

      데코레이터 패턴이란?
      기존 객체에 새로운 기능을 "겹겹이 감싸서" 추가하는 패턴입니다.
      비유: 커피에 옵션 추가!
            기본 커피 → 우유 추가 → 시럽 추가 → 휘핑 크림 추가
            원래 커피는 그대로 두고, 위에 덧붙이는 것.
    ═══════════════════════════════════════════════════════════════════════
    */

    // ┌─────────────────────────────────────────────┐
    // │  전략 패턴: 결제 시스템                       │
    // └─────────────────────────────────────────────┘

    // 결제 전략 인터페이스
    // "결제 방법"이라는 규칙만 정하고, 구체적인 방법은 각 전략이 구현합니다.
    public interface IPaymentStrategy
    {
        string Name { get; }
        bool Pay(int amount);
        string GetReceiptInfo();
    }

    // 전략 1: 신용카드 결제
    public class CreditCardPayment : IPaymentStrategy
    {
        public string Name => "신용카드";
        private readonly string _cardNumber;

        public CreditCardPayment(string cardNumber)
        {
            _cardNumber = cardNumber;
        }

        public bool Pay(int amount)
        {
            Console.WriteLine($"    [카드] {_cardNumber} 으로 {amount:N0}원 결제");
            return true;
        }

        public string GetReceiptInfo()
            => $"카드번호: ****-****-****-{_cardNumber.Substring(_cardNumber.Length - 4)}";
    }

    // 전략 2: 계좌이체
    public class BankTransferPayment : IPaymentStrategy
    {
        public string Name => "계좌이체";
        private readonly string _bankName;
        private readonly string _accountNumber;

        public BankTransferPayment(string bankName, string accountNumber)
        {
            _bankName = bankName;
            _accountNumber = accountNumber;
        }

        public bool Pay(int amount)
        {
            Console.WriteLine($"    [이체] {_bankName} {_accountNumber}에서 {amount:N0}원 이체");
            return true;
        }

        public string GetReceiptInfo()
            => $"은행: {_bankName}, 계좌: ***{_accountNumber.Substring(_accountNumber.Length - 4)}";
    }

    // 전략 3: 포인트 결제
    public class PointPayment : IPaymentStrategy
    {
        public string Name => "포인트";
        private int _points;

        public PointPayment(int points)
        {
            _points = points;
        }

        public bool Pay(int amount)
        {
            if (_points < amount)
            {
                Console.WriteLine($"    [포인트] 잔액 부족! (보유: {_points:N0}, 필요: {amount:N0})");
                return false;
            }
            _points -= amount;
            Console.WriteLine($"    [포인트] {amount:N0}P 사용 (잔여: {_points:N0}P)");
            return true;
        }

        public string GetReceiptInfo()
            => $"포인트 잔액: {_points:N0}P";
    }

    // 주문 처리기: 전략을 교체할 수 있습니다!
    public class OrderProcessor
    {
        private IPaymentStrategy _strategy;

        // 전략을 바꿀 수 있습니다 (런타임에!)
        public void SetPaymentMethod(IPaymentStrategy strategy)
        {
            _strategy = strategy;
            Console.WriteLine($"    결제 방법이 [{strategy.Name}](으)로 설정되었습니다.");
        }

        public bool ProcessOrder(string itemName, int amount)
        {
            if (_strategy == null)
            {
                Console.WriteLine("    결제 방법을 먼저 설정하세요!");
                return false;
            }

            Console.WriteLine($"    ── 주문: {itemName} ({amount:N0}원) ──");
            bool success = _strategy.Pay(amount);

            if (success)
            {
                Console.WriteLine($"    영수증: {_strategy.GetReceiptInfo()}");
                Console.WriteLine($"    주문 완료!");
            }
            else
            {
                Console.WriteLine($"    결제 실패!");
            }

            return success;
        }
    }

    // ┌─────────────────────────────────────────────┐
    // │  데코레이터 패턴: 커피 주문 시스템             │
    // └─────────────────────────────────────────────┘

    // 음료 인터페이스
    public interface IBeverage
    {
        string GetDescription();
        int GetCost();
    }

    // 기본 음료들
    public class Espresso : IBeverage
    {
        public string GetDescription() => "에스프레소";
        public int GetCost() => 3000;
    }

    public class HouseCoffee : IBeverage
    {
        public string GetDescription() => "하우스 커피";
        public int GetCost() => 2500;
    }

    public class GreenTea : IBeverage
    {
        public string GetDescription() => "녹차";
        public int GetCost() => 3500;
    }

    // ┌─────────────────────────────────────────────┐
    // │  데코레이터 (토핑/옵션)                       │
    // └─────────────────────────────────────────────┘
    // 데코레이터는 원래 음료를 "감싸서" 기능을 추가합니다.
    // 중요: 데코레이터도 IBeverage를 구현합니다!
    //       → 데코레이터 위에 또 데코레이터를 감쌀 수 있습니다! (겹겹이!)

    // 데코레이터 기본 클래스
    public abstract class BeverageDecorator : IBeverage
    {
        protected IBeverage _beverage;  // 감싸고 있는 원래 음료

        public BeverageDecorator(IBeverage beverage)
        {
            _beverage = beverage;
        }

        public abstract string GetDescription();
        public abstract int GetCost();
    }

    // 데코레이터: 우유 추가
    public class MilkDecorator : BeverageDecorator
    {
        public MilkDecorator(IBeverage beverage) : base(beverage) { }

        public override string GetDescription()
            => _beverage.GetDescription() + " + 우유";

        public override int GetCost()
            => _beverage.GetCost() + 500;  // 500원 추가
    }

    // 데코레이터: 시럽 추가
    public class SyrupDecorator : BeverageDecorator
    {
        private readonly string _syrupName;

        public SyrupDecorator(IBeverage beverage, string syrupName = "바닐라")
            : base(beverage)
        {
            _syrupName = syrupName;
        }

        public override string GetDescription()
            => _beverage.GetDescription() + $" + {_syrupName} 시럽";

        public override int GetCost()
            => _beverage.GetCost() + 300;  // 300원 추가
    }

    // 데코레이터: 휘핑 크림 추가
    public class WhipDecorator : BeverageDecorator
    {
        public WhipDecorator(IBeverage beverage) : base(beverage) { }

        public override string GetDescription()
            => _beverage.GetDescription() + " + 휘핑 크림";

        public override int GetCost()
            => _beverage.GetCost() + 700;  // 700원 추가
    }

    // 데코레이터: 사이즈 업
    public class SizeUpDecorator : BeverageDecorator
    {
        public SizeUpDecorator(IBeverage beverage) : base(beverage) { }

        public override string GetDescription()
            => _beverage.GetDescription() + " (사이즈 업)";

        public override int GetCost()
            => _beverage.GetCost() + 1000;  // 1000원 추가
    }

    // 주문서 출력 도우미
    public static class CafeHelper
    {
        public static void PrintOrder(IBeverage beverage)
        {
            Console.WriteLine($"    주문: {beverage.GetDescription()}");
            Console.WriteLine($"    가격: {beverage.GetCost():N0}원");
        }
    }

    // ┌─────────────────────────────────────────────┐
    // │  실행                                        │
    // └─────────────────────────────────────────────┘
    internal class Program
    {
        static void Main()
        {
            Console.WriteLine(new string('=', 60));
            Console.WriteLine("  전략 패턴 + 데코레이터 패턴");
            Console.WriteLine(new string('=', 60));
            Console.WriteLine();

            Lesson1_Strategy_Payment();
            Lesson2_Strategy_Runtime();
            Lesson3_Decorator_Coffee();
            Lesson4_Decorator_Stacking();
            Lesson5_Summary();
        }

        static void Lesson1_Strategy_Payment()
        {
            Console.WriteLine("[레슨 1] 전략 패턴 — 다양한 결제 방법");
            Console.WriteLine();

            var processor = new OrderProcessor();

            // 카드로 결제
            processor.SetPaymentMethod(new CreditCardPayment("1234-5678-9012-3456"));
            processor.ProcessOrder("노트북 가방", 35000);
            Console.WriteLine();

            // 같은 주문 처리기로, 결제 방법만 바꾸기!
            processor.SetPaymentMethod(new BankTransferPayment("국민은행", "123-456-789"));
            processor.ProcessOrder("마우스 패드", 15000);
            Console.WriteLine();
        }

        static void Lesson2_Strategy_Runtime()
        {
            Console.WriteLine("[레슨 2] 전략 패턴 — 런타임에 전략 교체");
            Console.WriteLine();

            /*
              전략 패턴의 핵심: if/else 없이 결제 방법을 바꿀 수 있습니다!

              나쁜 방법:
                if (method == "카드") { ... 카드 결제 코드 ... }
                else if (method == "이체") { ... 이체 코드 ... }
                → 결제 방법이 추가될 때마다 if를 추가해야 함!

              좋은 방법 (전략 패턴):
                processor.SetPaymentMethod(새로운_결제_전략);
                → 새 전략 클래스만 만들면 됨. 기존 코드 수정 불필요!
            */

            var processor = new OrderProcessor();

            // 포인트로 시도 → 잔액 부족 → 카드로 변경
            var pointPay = new PointPayment(5000);
            processor.SetPaymentMethod(pointPay);
            bool success = processor.ProcessOrder("텀블러", 12000);
            Console.WriteLine();

            if (!success)
            {
                Console.WriteLine("    → 포인트 부족! 카드로 변경합니다.");
                processor.SetPaymentMethod(new CreditCardPayment("9999-8888-7777-6666"));
                processor.ProcessOrder("텀블러", 12000);
            }
            Console.WriteLine();
        }

        static void Lesson3_Decorator_Coffee()
        {
            Console.WriteLine("[레슨 3] 데코레이터 — 커피에 옵션 추가하기");
            Console.WriteLine();

            // 1) 기본 에스프레소
            IBeverage order1 = new Espresso();
            Console.WriteLine("  === 주문 1 ===");
            CafeHelper.PrintOrder(order1);
            Console.WriteLine();

            // 2) 에스프레소 + 우유
            IBeverage order2 = new Espresso();
            order2 = new MilkDecorator(order2);  // 감싸기!
            Console.WriteLine("  === 주문 2 ===");
            CafeHelper.PrintOrder(order2);
            Console.WriteLine();

            // 3) 하우스 커피 + 바닐라 시럽 + 휘핑
            IBeverage order3 = new HouseCoffee();
            order3 = new SyrupDecorator(order3, "바닐라");  // 시럽 추가
            order3 = new WhipDecorator(order3);              // 휘핑 추가
            Console.WriteLine("  === 주문 3 ===");
            CafeHelper.PrintOrder(order3);
            Console.WriteLine();
        }

        static void Lesson4_Decorator_Stacking()
        {
            Console.WriteLine("[레슨 4] 데코레이터 — 겹겹이 쌓기");
            Console.WriteLine();

            /*
              데코레이터의 강점: 원하는 만큼 겹칠 수 있습니다!
              각 데코레이터는 자기가 감싼 것의 결과 + 자기 것을 더합니다.

              구조:
              SizeUp(Whip(Syrup(Milk(Espresso))))
              → "에스프레소 + 우유 + 카라멜 시럽 + 휘핑 크림 (사이즈 업)"
              → 3000 + 500 + 300 + 700 + 1000 = 5500원
            */

            IBeverage megaOrder = new Espresso();
            megaOrder = new MilkDecorator(megaOrder);
            megaOrder = new SyrupDecorator(megaOrder, "카라멜");
            megaOrder = new WhipDecorator(megaOrder);
            megaOrder = new SizeUpDecorator(megaOrder);

            Console.WriteLine("  === 풀 옵션 주문 ===");
            CafeHelper.PrintOrder(megaOrder);
            Console.WriteLine();

            // 녹차에도 같은 데코레이터 적용 가능!
            IBeverage teaOrder = new GreenTea();
            teaOrder = new MilkDecorator(teaOrder);
            teaOrder = new SyrupDecorator(teaOrder, "꿀");

            Console.WriteLine("  === 녹차 라테 ===");
            CafeHelper.PrintOrder(teaOrder);
            Console.WriteLine();

            // 가격 분해
            Console.WriteLine("  === 풀 옵션 가격 분해 ===");
            Console.WriteLine("    에스프레소     3,000원");
            Console.WriteLine("    + 우유           500원");
            Console.WriteLine("    + 카라멜 시럽    300원");
            Console.WriteLine("    + 휘핑 크림      700원");
            Console.WriteLine("    + 사이즈 업    1,000원");
            Console.WriteLine("    ─────────────────────");
            Console.WriteLine($"    합계         {megaOrder.GetCost():N0}원");
            Console.WriteLine();
        }

        static void Lesson5_Summary()
        {
            Console.WriteLine("[레슨 5] 정리 — 전략 vs 데코레이터");
            Console.WriteLine();

            Console.WriteLine("  ┌────────────────┬─────────────────────────────────────┐");
            Console.WriteLine("  │  패턴           │  핵심 아이디어                       │");
            Console.WriteLine("  ├────────────────┼─────────────────────────────────────┤");
            Console.WriteLine("  │  전략 패턴      │  '방법'을 교체. 여러 알고리즘 중      │");
            Console.WriteLine("  │                │  하나를 선택해서 사용                 │");
            Console.WriteLine("  │  데코레이터     │  '기능'을 추가. 기존 객체에 겹겹이     │");
            Console.WriteLine("  │                │  기능을 쌓아올림                     │");
            Console.WriteLine("  └────────────────┴─────────────────────────────────────┘");
            Console.WriteLine();
            Console.WriteLine("  전략: '어떻게 할까?'를 바꿀 때 (결제, 정렬, 압축 방식 등)");
            Console.WriteLine("  데코레이터: '무엇을 더할까?'를 쌓을 때 (옵션, 로깅, 캐시 등)");
            Console.WriteLine();
        }
    }
}
