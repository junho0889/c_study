/*
===============================================================================
  프론트엔드 자바스크립트 02단계: 변수, 객체, 함수, 배열
===============================================================================
*/

function lesson1_variables() {
  // 변수는 값을 담는 상자입니다.
  const name = "코딩 학생";
  let level = 1;

  console.log("[레슨 1] 변수");
  console.log("이름:", name);
  console.log("레벨:", level);
  console.log();

  level += 1;
  console.log("공부 후 레벨:", level);
  console.log();
}

function lesson2_object() {
  // 객체는 관련 있는 값을 한 덩어리로 묶습니다.
  const student = {
    name: "민수",
    score: 92,
  };

  console.log("[레슨 2] 객체");
  console.log(student);
  console.log();
}

function lesson3_array() {
  // 배열은 순서대로 값을 저장하는 줄입니다.
  const lessons = ["HTML", "CSS", "JavaScript"];

  console.log("[레슨 3] 배열");
  for (const lesson of lessons) {
    console.log("-", lesson);
  }
  console.log();
}

function lesson4_function() {
  function printResult(score) {
    const result = score >= 70 ? "통과" : "복습 필요";
    console.log(`점수 ${score}점 -> ${result}`);
  }

  console.log("[레슨 4] 함수");
  printResult(88);
  printResult(61);
  console.log();
}

console.log("============================================================");
console.log("  자바스크립트 02단계 : 변수, 객체, 함수, 배열");
console.log("============================================================");
console.log();

lesson1_variables();
lesson2_object();
lesson3_array();
lesson4_function();
