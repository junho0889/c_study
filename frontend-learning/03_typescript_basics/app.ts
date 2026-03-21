type OrderStatus = "pending" | "done";

interface SnackOrder {
  studentName: string;
  itemName: string;
  price: number;
  status: OrderStatus;
}

function lesson1TypeInference(): void {
  console.log("[레슨 1] 타입 추론은 코드를 읽는 사람에게도 힌트를 준다.");
  console.log();

  // TypeScript는 값의 모양을 보고 변수 타입을 많이 알아냅니다.
  // 마치 선생님이 학생 이름표를 보고 "아, 3반 학생이구나" 하고 알아차리는 것과 비슷합니다.
  const lunchCount = 3;
  const snackTitle = "우유 급식";

  console.log("  lunchCount =", lunchCount);
  console.log("  snackTitle =", snackTitle);
  console.log();
}

function formatOrder(order: SnackOrder): string {
  const statusLabel = order.status === "done" ? "전달 완료" : "준비 중";
  return `${order.studentName} - ${order.itemName} (${order.price}원, ${statusLabel})`;
}

function lesson2UnionAndGuard(value: string | number): void {
  console.log("[레슨 2] 유니온 타입은 여러 종류가 들어올 수 있음을 미리 적는 약속");
  console.log();

  // typeof 검사는 "이 상자 안 물건이 글자인지 숫자인지 먼저 확인하자"는 안전 절차입니다.
  if (typeof value === "string") {
    console.log("  문자열 길이:", value.length);
  } else {
    console.log("  숫자에 10 더하기:", value + 10);
  }
  console.log();
}

function lesson3RealExample(): void {
  console.log("[레슨 3] 인터페이스를 쓰면 실제 데이터 표가 또렷해진다.");
  console.log();

  const orders: SnackOrder[] = [
    { studentName: "민수", itemName: "우유", price: 1200, status: "pending" },
    { studentName: "지우", itemName: "샌드위치", price: 2600, status: "done" },
  ];

  let total = 0;
  for (const order of orders) {
    total += order.price;
    console.log("  " + formatOrder(order));
  }

  console.log("  전체 금액:", total);
  console.log();
}

function main(): void {
  console.log("========================================================================");
  console.log("  TypeScript 기초 예제");
  console.log("========================================================================");
  console.log();

  lesson1TypeInference();
  lesson2UnionAndGuard("도시락");
  lesson2UnionAndGuard(25);
  lesson3RealExample();
}

main();
