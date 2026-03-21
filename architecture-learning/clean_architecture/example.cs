using System;
using System.Collections.Generic;
using System.Linq;

namespace ArchitectureLearning.CleanArchitecture
{
    /*
    ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
      클린 아키텍처 (Clean Architecture)
      실행 방법: dotnet script example.cs  또는  csc example.cs && example.exe
    ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

      클린 아키텍처란?
      코드를 양파 껍질처럼 "안쪽 → 바깥쪽" 4개 층으로 나누는 설계 방법입니다.
      가장 중요한 규칙: "바깥쪽이 안쪽에 의존하지, 안쪽은 바깥쪽을 모른다!"

      비유: 학교의 조직 구조
        ┌──────────────────────────────────────┐
        │  4층: 프레임워크 (도구)               │ ← 칠판, 컴퓨터, 사무실
        │  ┌──────────────────────────────────┐│
        │  │ 3층: 인터페이스 어댑터 (연결자)   ││ ← 교무실 (안팎 소통)
        │  │ ┌──────────────────────────────┐ ││
        │  │ │ 2층: 유스케이스 (규칙)        │ ││ ← 교칙 (이렇게 해라)
        │  │ │ ┌──────────────────────────┐ │ ││
        │  │ │ │ 1층: 엔티티 (핵심 데이터) │ │ ││ ← 학생 정보 (변하지 않음)
        │  │ │ └──────────────────────────┘ │ ││
        │  │ └──────────────────────────────┘ ││
        │  └──────────────────────────────────┘│
        └──────────────────────────────────────┘

      여기서는 "주문 처리 시스템"으로 4개 층을 보여줍니다.
    ═══════════════════════════════════════════════════════════════════════
    */

    // ┌─────────────────────────────────────────────┐
    // │  1층: Entity (엔티티) — 핵심 비즈니스 규칙     │
    // └─────────────────────────────────────────────┘
    // 엔티티는 가장 안쪽 층입니다. 다른 어떤 층에도 의존하지 않습니다.
    // "주문"이라는 개념 자체의 규칙만 담고 있습니다.
    //
    // 비유: 학생 카드에 적힌 기본 정보와 규칙.
    //       "점수는 0~100점 사이여야 한다" 같은 절대 불변의 규칙.

    public class OrderItem
    {
        public string ProductName { get; }
        public int Price { get; }
        public int Quantity { get; }

        public OrderItem(string productName, int price, int quantity)
        {
            if (price <= 0) throw new ArgumentException("가격은 0보다 커야 합니다.");
            if (quantity <= 0) throw new ArgumentException("수량은 0보다 커야 합니다.");
            ProductName = productName;
            Price = price;
            Quantity = quantity;
        }

        public int GetSubtotal() => Price * Quantity;
    }

    public class Order
    {
        public int Id { get; }
        public string CustomerName { get; }
        public List<OrderItem> Items { get; } = new List<OrderItem>();
        public DateTime CreatedAt { get; }
        public string Status { get; private set; } = "대기";

        public Order(int id, string customerName)
        {
            Id = id;
            CustomerName = customerName;
            CreatedAt = DateTime.Now;
        }

        public void AddItem(OrderItem item) => Items.Add(item);

        // 엔티티 스스로의 규칙: 총 금액 계산
        public int GetTotalAmount() => Items.Sum(i => i.GetSubtotal());

        // 상태 변경도 엔티티가 스스로 관리
        public void Confirm()
        {
            if (Items.Count == 0)
                throw new InvalidOperationException("상품이 없으면 주문 확정 불가!");
            Status = "확정";
        }

        public void Cancel() => Status = "취소";
    }

    // ┌─────────────────────────────────────────────┐
    // │  2층: Use Case (유스케이스) — 어플리케이션 규칙│
    // └─────────────────────────────────────────────┘
    // 유스케이스는 "이 앱에서 할 수 있는 행동"을 정의합니다.
    // 엔티티를 사용하지만, DB나 UI는 모릅니다 (인터페이스로만 소통).
    //
    // 비유: 교칙.
    //       "학생이 도서관에서 책을 빌리려면, 학생증을 보여주고, 3권까지만 가능"
    //       칠판이 뭔지, 컴퓨터가 뭔지는 모르고 규칙만 압니다.

    // 저장소 인터페이스 (바깥쪽 구현은 모름)
    public interface IOrderRepository
    {
        void Save(Order order);
        Order FindById(int id);
        List<Order> FindAll();
    }

    // 유스케이스: 주문 생성
    public class CreateOrderUseCase
    {
        private readonly IOrderRepository _repository;

        public CreateOrderUseCase(IOrderRepository repository)
        {
            _repository = repository;
        }

        public Order Execute(string customerName, List<(string name, int price, int qty)> items)
        {
            // 비즈니스 규칙: 최소 1개 상품 필요
            if (items == null || items.Count == 0)
                throw new ArgumentException("최소 1개 상품이 필요합니다.");

            var order = new Order(_repository.FindAll().Count + 1, customerName);

            foreach (var (name, price, qty) in items)
            {
                order.AddItem(new OrderItem(name, price, qty));
            }

            // 비즈니스 규칙: 총 금액 100만 원 초과 불가
            if (order.GetTotalAmount() > 1000000)
                throw new InvalidOperationException("주문 금액이 100만 원을 초과할 수 없습니다.");

            order.Confirm();
            _repository.Save(order);
            return order;
        }
    }

    // 유스케이스: 주문 조회
    public class GetOrderUseCase
    {
        private readonly IOrderRepository _repository;

        public GetOrderUseCase(IOrderRepository repository)
        {
            _repository = repository;
        }

        public Order Execute(int orderId)
        {
            var order = _repository.FindById(orderId);
            if (order == null)
                throw new KeyNotFoundException($"주문 #{orderId}을 찾을 수 없습니다.");
            return order;
        }
    }

    // ┌─────────────────────────────────────────────┐
    // │  3층: Interface Adapter (인터페이스 어댑터)    │
    // └─────────────────────────────────────────────┘
    // 안쪽(유스케이스)과 바깥쪽(DB, UI) 사이를 연결합니다.
    // 데이터를 안쪽 형식 ↔ 바깥쪽 형식으로 변환합니다.
    //
    // 비유: 교무실.
    //       학생(안쪽)의 요청을 받아서 외부(학부모, 교육청)와 소통합니다.

    // Presenter: 주문 정보를 화면에 보기 좋게 변환
    public class OrderPresenter
    {
        public static string FormatOrder(Order order)
        {
            var lines = new List<string>
            {
                $"┌─── 주문서 #{order.Id} ───┐",
                $"  고객: {order.CustomerName}",
                $"  상태: {order.Status}",
                $"  날짜: {order.CreatedAt:yyyy-MM-dd HH:mm}",
                "  ────────────────────",
            };

            foreach (var item in order.Items)
            {
                lines.Add($"  {item.ProductName} x{item.Quantity} = {item.GetSubtotal():N0}원");
            }

            lines.Add("  ────────────────────");
            lines.Add($"  합계: {order.GetTotalAmount():N0}원");
            lines.Add("└────────────────────┘");

            return string.Join("\n", lines);
        }
    }

    // ┌─────────────────────────────────────────────┐
    // │  4층: Frameworks (프레임워크/드라이버)        │
    // └─────────────────────────────────────────────┘
    // 가장 바깥쪽 층. 실제 DB, 웹 프레임워크, UI 등.
    // 여기서는 메모리 DB(리스트)로 구현합니다.
    //
    // 비유: 칠판, 컴퓨터, 교실 같은 실제 도구.

    // 메모리 저장소 (실제로는 MySQL, PostgreSQL 등이 여기에 해당)
    public class InMemoryOrderRepository : IOrderRepository
    {
        private readonly List<Order> _orders = new List<Order>();

        public void Save(Order order) => _orders.Add(order);
        public Order FindById(int id) => _orders.FirstOrDefault(o => o.Id == id);
        public List<Order> FindAll() => new List<Order>(_orders);
    }

    // ┌─────────────────────────────────────────────┐
    // │  실행: 모든 층을 조립해서 사용                 │
    // └─────────────────────────────────────────────┘
    internal class Program
    {
        static void Main()
        {
            Console.WriteLine(new string('=', 60));
            Console.WriteLine("  클린 아키텍처 예제: 주문 처리 시스템");
            Console.WriteLine(new string('=', 60));
            Console.WriteLine();

            Lesson1_CreateOrder();
            Lesson2_DependencyRule();
            Lesson3_WhyCleanArchitecture();
        }

        static void Lesson1_CreateOrder()
        {
            Console.WriteLine("[레슨 1] 주문 생성 — 4개 층이 협력하는 모습");
            Console.WriteLine();

            // 4층: 저장소 생성 (프레임워크 층)
            var repository = new InMemoryOrderRepository();

            // 2층: 유스케이스 생성 (저장소 인터페이스를 주입)
            var createOrder = new CreateOrderUseCase(repository);

            // 실행: 주문 생성
            var order = createOrder.Execute("민수", new List<(string, int, int)>
            {
                ("삼각김밥", 1200, 3),
                ("초코우유", 1500, 2),
                ("컵라면", 1800, 1),
            });

            // 3층: Presenter가 보기 좋게 변환
            Console.WriteLine(OrderPresenter.FormatOrder(order));
            Console.WriteLine();
        }

        static void Lesson2_DependencyRule()
        {
            Console.WriteLine("[레슨 2] 의존성 규칙 — 안쪽은 바깥쪽을 모른다");
            Console.WriteLine();

            /*
              핵심 규칙: 의존성은 항상 "바깥 → 안쪽"으로만 향합니다.

              InMemoryOrderRepository (4층)
                → IOrderRepository (2층 인터페이스)
                → Order, OrderItem (1층 엔티티)

              만약 DB를 바꾸고 싶다면?
              InMemoryOrderRepository 대신 MySqlOrderRepository를 만들면 됩니다.
              1층, 2층 코드는 전혀 안 바꿔도 됩니다!

              비유: 칠판(4층)을 전자 칠판으로 바꿔도
                    교칙(2층)이나 학생 정보(1층)는 바뀌지 않는 것.
            */

            Console.WriteLine("  1층 Entity:     Order, OrderItem (핵심 규칙)");
            Console.WriteLine("  2층 Use Case:   CreateOrderUseCase (앱 규칙)");
            Console.WriteLine("  3층 Adapter:    OrderPresenter (형식 변환)");
            Console.WriteLine("  4층 Framework:  InMemoryOrderRepository (실제 저장)");
            Console.WriteLine();
            Console.WriteLine("  → DB를 바꿀 때: 4층만 교체! (1~3층은 그대로)");
            Console.WriteLine("  → UI를 바꿀 때: 3~4층만 교체! (1~2층은 그대로)");
            Console.WriteLine();
        }

        static void Lesson3_WhyCleanArchitecture()
        {
            Console.WriteLine("[레슨 3] 왜 클린 아키텍처를 쓸까?");
            Console.WriteLine();

            Console.WriteLine("  ┌──────────────────┬──────────────────────────────┐");
            Console.WriteLine("  │  장점            │  설명                         │");
            Console.WriteLine("  ├──────────────────┼──────────────────────────────┤");
            Console.WriteLine("  │  테스트 쉬움      │  각 층을 독립적으로 테스트 가능 │");
            Console.WriteLine("  │  교체 쉬움        │  DB, UI를 바꿔도 핵심 로직 무사│");
            Console.WriteLine("  │  이해 쉬움        │  역할별로 나뉘어 있어 찾기 쉬움 │");
            Console.WriteLine("  │  유지보수 쉬움    │  변경의 영향 범위가 작음        │");
            Console.WriteLine("  └──────────────────┴──────────────────────────────┘");
            Console.WriteLine();
            Console.WriteLine("  주의: 작은 프로젝트에서는 과할 수 있습니다.");
            Console.WriteLine("        규모가 커질수록 빛을 발합니다!");
            Console.WriteLine();
        }
    }
}
