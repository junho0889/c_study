import { useState } from "react";

function LessonCard({ title, children }) {
  return (
    <section
      style={{
        background: "#ffffff",
        borderRadius: 16,
        padding: 20,
        boxShadow: "0 8px 24px rgba(15, 23, 42, 0.08)",
        marginBottom: 16,
      }}
    >
      <h2 style={{ marginTop: 0 }}>{title}</h2>
      {children}
    </section>
  );
}

function formatOrder(order) {
  const statusText = order.done ? "전달 완료" : "준비 중";
  return `${order.student} / ${order.item} / ${statusText}`;
}

export default function App() {
  // state 는 시간이 지나며 바뀌는 값입니다.
  // 칠판에 적힌 숫자를 지우고 다시 쓰듯, 화면도 state 가 바뀌면 다시 그려집니다.
  const [orders, setOrders] = useState([
    { id: 1, student: "민수", item: "우유", done: false },
    { id: 2, student: "지우", item: "샌드위치", done: true },
  ]);
  const [selectedId, setSelectedId] = useState(1);

  const selectedOrder = orders.find((order) => order.id === selectedId);
  const doneCount = orders.filter((order) => order.done).length;

  function lesson1SelectOrder(id) {
    // 사용자가 버튼을 누르면 selectedId 가 바뀌고,
    // React 는 "바뀐 값으로 다시 그려야겠다"라고 판단합니다.
    setSelectedId(id);
  }

  function lesson2ToggleDone() {
    setOrders((previousOrders) =>
      previousOrders.map((order) =>
        order.id === selectedId ? { ...order, done: !order.done } : order
      )
    );
  }

  return (
    <main
      style={{
        padding: 24,
        minHeight: "100vh",
        background: "linear-gradient(180deg, #e0f2fe 0%, #f8fafc 100%)",
        fontFamily: "'Segoe UI', sans-serif",
      }}
    >
      <h1>React 컴포넌트 교과서 예제</h1>
      <p>한 파일 안에서도 state, event, 화면 조각을 실제 예제로 묶어 볼 수 있습니다.</p>

      <LessonCard title="레슨 1. 목록을 렌더링하고 현재 선택을 바꾸기">
        <p>map 은 같은 모양의 카드 여러 장을 만들 때 가장 자주 쓰는 반복 도구입니다.</p>
        {orders.map((order) => (
          <button
            key={order.id}
            onClick={() => lesson1SelectOrder(order.id)}
            style={{
              marginRight: 8,
              marginBottom: 8,
              padding: "10px 14px",
              borderRadius: 999,
              border: selectedId === order.id ? "2px solid #0284c7" : "1px solid #cbd5e1",
              background: selectedId === order.id ? "#e0f2fe" : "#ffffff",
              cursor: "pointer",
            }}
          >
            {order.student}
          </button>
        ))}
      </LessonCard>

      <LessonCard title="레슨 2. 선택한 주문의 상태 바꾸기">
        <p>선택된 주문: {selectedOrder ? formatOrder(selectedOrder) : "없음"}</p>
        <button
          onClick={lesson2ToggleDone}
          style={{
            padding: "10px 16px",
            border: "none",
            borderRadius: 10,
            background: "#0f766e",
            color: "white",
            cursor: "pointer",
          }}
        >
          완료 상태 뒤집기
        </button>
      </LessonCard>

      <LessonCard title="레슨 3. 파생 값 계산하기">
        <p>전체 주문 수: {orders.length}</p>
        <p>완료된 주문 수: {doneCount}</p>
        <p>
          이런 값은 별도 state 로 또 저장하기보다, 원래 state 에서 계산해 내면 실수가 줄어듭니다.
        </p>
      </LessonCard>
    </main>
  );
}
