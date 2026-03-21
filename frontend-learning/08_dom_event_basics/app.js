function lesson1BuildLayout() {
  const app = document.createElement("main");
  app.style.padding = "24px";
  app.style.fontFamily = "'Malgun Gothic', sans-serif";

  app.innerHTML = `
    <h1>DOM 이벤트 교과서 예제</h1>
    <p id="message">버튼을 눌러 보세요.</p>
    <button id="countButton">횟수 올리기</button>
    <button id="resetButton">다시 0으로</button>
    <p id="countText">현재 클릭 수: 0</p>
  `;

  document.body.appendChild(app);
}

function lesson2AttachEvents() {
  let count = 0;
  const message = document.getElementById("message");
  const countText = document.getElementById("countText");
  const countButton = document.getElementById("countButton");
  const resetButton = document.getElementById("resetButton");

  // 이벤트는 "무슨 일이 일어났어요!"라는 알림입니다.
  // 초인종이 눌리면 집 안에 소리가 울리듯,
  // 버튼이 눌리면 click 이벤트가 자바스크립트 코드에 알려집니다.
  countButton.addEventListener("click", () => {
    count += 1;
    countText.textContent = `현재 클릭 수: ${count}`;
    message.textContent = "클릭 이벤트가 실행되었습니다.";
  });

  resetButton.addEventListener("click", () => {
    count = 0;
    countText.textContent = "현재 클릭 수: 0";
    message.textContent = "숫자를 다시 처음으로 돌렸습니다.";
  });
}

function main() {
  lesson1BuildLayout();
  lesson2AttachEvents();
}

main();
