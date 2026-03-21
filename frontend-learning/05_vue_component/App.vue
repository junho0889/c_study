<template>
  <main class="page">
    <h1>Vue 컴포넌트 교과서 예제</h1>
    <p>반응형 데이터가 바뀌면 화면이 자동으로 새로 그려집니다.</p>

    <section class="card">
      <h2>레슨 1. ref 로 바뀌는 값 만들기</h2>
      <p>현재 선택된 학생: {{ selectedStudent }}</p>
      <button v-for="name in students" :key="name" @click="lesson1SelectStudent(name)">
        {{ name }}
      </button>
    </section>

    <section class="card">
      <h2>레슨 2. computed 로 파생 값 만들기</h2>
      <p>완료된 간식 수: {{ completedCount }}</p>
      <button @click="lesson2ToggleFirst">첫 번째 주문 상태 바꾸기</button>
    </section>

    <section class="card">
      <h2>레슨 3. 실제 주문표 보기</h2>
      <ul>
        <li v-for="order in orders" :key="order.id">
          {{ order.student }} / {{ order.item }} / {{ order.done ? "완료" : "준비 중" }}
        </li>
      </ul>
    </section>
  </main>
</template>

<script setup>
import { computed, ref } from "vue";

const students = ["민수", "지우", "서연"];
const selectedStudent = ref("민수");
const orders = ref([
  { id: 1, student: "민수", item: "우유", done: false },
  { id: 2, student: "지우", item: "샌드위치", done: true },
]);

const completedCount = computed(() => orders.value.filter((order) => order.done).length);

function lesson1SelectStudent(name) {
  // ref 값은 .value 로 읽고 씁니다.
  // 상자 자체와 상자 안의 값을 구분한다고 생각하면 덜 헷갈립니다.
  selectedStudent.value = name;
}

function lesson2ToggleFirst() {
  orders.value[0].done = !orders.value[0].done;
}
</script>

<style scoped>
.page {
  padding: 24px;
  min-height: 100vh;
  background: #f8fafc;
  font-family: "Malgun Gothic", sans-serif;
}

.card {
  margin-bottom: 16px;
  padding: 20px;
  border-radius: 16px;
  background: white;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}

button {
  margin-right: 8px;
}
</style>
