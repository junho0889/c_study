<script>
  let snacks = [
    { name: "우유", count: 2 },
    { name: "바나나", count: 1 },
  ];

  let selectedIndex = 0;

  // $: 는 "이 값이 바뀌면 다시 계산해 줘"라는 Svelte 전용 표시입니다.
  // 칠판의 합계칸이 물건 수가 바뀔 때마다 자동으로 다시 써지는 느낌입니다.
  $: totalCount = snacks.reduce((sum, snack) => sum + snack.count, 0);
  $: selectedSnack = snacks[selectedIndex];

  function lesson1Select(index) {
    selectedIndex = index;
  }

  function lesson2IncreaseSelected() {
    snacks[selectedIndex].count += 1;
    snacks = snacks;
  }
</script>

<main class="page">
  <h1>Svelte 컴포넌트 교과서 예제</h1>

  <section class="card">
    <h2>레슨 1. 목록에서 현재 항목 선택하기</h2>
    {#each snacks as snack, index}
      <button on:click={() => lesson1Select(index)}>{snack.name}</button>
    {/each}
  </section>

  <section class="card">
    <h2>레슨 2. 현재 선택 항목 수량 올리기</h2>
    <p>선택한 간식: {selectedSnack.name}</p>
    <p>현재 수량: {selectedSnack.count}</p>
    <button on:click={lesson2IncreaseSelected}>수량 +1</button>
  </section>

  <section class="card">
    <h2>레슨 3. 파생 값 보기</h2>
    <p>전체 간식 수량: {totalCount}</p>
  </section>
</main>

<style>
  .page {
    padding: 24px;
    min-height: 100vh;
    background: #eef6ff;
    font-family: "Malgun Gothic", sans-serif;
  }

  .card {
    margin-bottom: 16px;
    padding: 18px;
    border-radius: 14px;
    background: white;
  }

  button {
    margin-right: 8px;
  }
</style>
