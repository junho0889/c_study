const initialState = {
  count: 0,
  selectedSnack: "우유",
  cart: [],
};

function reducer(state, action) {
  // reducer는 "현재 상태"와 "무슨 일이 일어났는지"를 받아
  // 다음 상태를 돌려주는 규칙표입니다.
  // 자판기 버튼 안내판처럼, 버튼마다 어떤 결과가 나오는지 정해 둡니다.
  if (action.type === "increment") {
    return { ...state, count: state.count + 1 };
  }

  if (action.type === "selectSnack") {
    return { ...state, selectedSnack: action.payload };
  }

  if (action.type === "addToCart") {
    return { ...state, cart: [...state.cart, action.payload] };
  }

  return state;
}

function render(state) {
  console.log(
    `  화면 표시 -> 수량: ${state.count}, 선택한 간식: ${state.selectedSnack}, 장바구니: ${state.cart.join(", ") || "비어 있음"}`
  );
}

function lesson1SingleSourceOfTruth() {
  console.log("[레슨 1] 상태를 한 곳에 모아 두면 화면이 덜 헷갈린다.");
  console.log();

  let state = initialState;
  render(state);

  state = reducer(state, { type: "increment" });
  state = reducer(state, { type: "selectSnack", payload: "사과" });
  state = reducer(state, { type: "addToCart", payload: "사과" });
  render(state);
  console.log();
}

function lesson2WhyImmutableUpdateMatters() {
  console.log("[레슨 2] 새 상태를 만들어 돌려주면 이전 상태와 비교하기 쉽다.");
  console.log();

  const before = initialState;
  const after = reducer(before, { type: "increment" });

  console.log("  before === after ?", before === after);
  console.log("  이전 상태 count:", before.count);
  console.log("  다음 상태 count:", after.count);
  console.log("  설명: 복사본을 만들어 바꾸면 '무엇이 달라졌는지' 찾기 쉬워집니다.");
  console.log();
}

function lesson3CommonMistakeMutatingState() {
  console.log("[레슨 3] 원본 상태를 직접 바꾸면 생기는 문제");
  console.log();

  const state = { count: 0, selectedSnack: "우유", cart: [] };
  const badReference = state;

  // 초보자가 자주 하는 실수:
  // 같은 상자를 가리키는 다른 이름을 만든 뒤 직접 값을 바꿔 버리는 것입니다.
  // 이렇게 하면 "이전 상태"도 같이 망가져 디버깅이 어려워집니다.
  badReference.count += 1;
  badReference.cart.push("우유");

  console.log("  원본 state:", state);
  console.log("  badReference:", badReference);
  console.log("  설명: 둘이 사실 같은 상자라서 둘 다 같이 바뀝니다.");
  console.log();
}

console.log("========================================================================");
console.log("Frontend 10단계: 상태 관리 사고방식");
console.log("========================================================================");
console.log();

lesson1SingleSourceOfTruth();
lesson2WhyImmutableUpdateMatters();
lesson3CommonMistakeMutatingState();
