/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  프론트엔드 14단계: 테스트 기초 — 계산기 모듈                     ■
■  이 파일은 테스트 대상(피험자)이 되는 계산기 모듈입니다.            ■
■  app.test.js 에서 이 모듈의 함수들을 테스트합니다.                ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  비유:
  - 이 파일은 "자동차 엔진"입니다.
  - app.test.js는 "검사장"입니다.
  - 엔진을 검사장에 가져가서 잘 작동하는지 하나씩 확인합니다.
*/

/* ═══════════════════════════════════════════════════════════════
   섹션 1: 기본 사칙연산
   ═══════════════════════════════════════════════════════════════
   가장 단순한 함수부터 시작합니다.
   이런 함수야말로 테스트하기 가장 좋습니다.
   입력을 넣으면 항상 같은 출력이 나오니까요! (순수 함수)
*/

// 덧셈: 두 수를 더합니다
function add(a, b) {
  return a + b;
}

// 뺄셈: 두 수를 뺍니다
function subtract(a, b) {
  return a - b;
}

// 곱셈: 두 수를 곱합니다
function multiply(a, b) {
  return a * b;
}

// 나눗셈: 두 수를 나눕니다 (0으로 나누면 에러!)
// 에러 상황도 테스트해야 합니다 — 이것이 "방어적 프로그래밍"입니다.
function divide(a, b) {
  if (b === 0) {
    throw new Error("0으로 나눌 수 없습니다");
  }
  return a / b;
}

/* ═══════════════════════════════════════════════════════════════
   섹션 2: 계산 기록 관리
   ═══════════════════════════════════════════════════════════════
   상태(state)를 가진 함수는 테스트할 때 더 신경 써야 합니다.
   테스트마다 상태를 초기화해야 서로 영향을 주지 않습니다!
*/

// 계산 기록을 저장하는 배열
let history = [];

// 계산을 수행하고 기록에 남기기
function calculate(operation, a, b) {
  let result;

  switch (operation) {
    case "add":
      result = add(a, b);
      break;
    case "subtract":
      result = subtract(a, b);
      break;
    case "multiply":
      result = multiply(a, b);
      break;
    case "divide":
      result = divide(a, b);
      break;
    default:
      throw new Error(`알 수 없는 연산: ${operation}`);
  }

  // 기록에 저장
  const record = {
    operation,
    a,
    b,
    result,
    timestamp: Date.now(),
  };
  history.push(record);

  return result;
}

// 계산 기록 가져오기
function getHistory() {
  return [...history]; // 복사본 반환 (원본 보호!)
}

// 계산 기록 초기화
function clearHistory() {
  history = [];
}

// 마지막 계산 결과 가져오기
function getLastResult() {
  if (history.length === 0) {
    return null;
  }
  return history[history.length - 1].result;
}

/* ═══════════════════════════════════════════════════════════════
   섹션 3: 고급 계산 기능
   ═══════════════════════════════════════════════════════════════
   비동기(async) 함수도 테스트해 봅시다!
   실제로는 서버에서 환율을 가져오겠지만,
   여기서는 setTimeout으로 "느린 작업"을 시뮬레이션합니다.
*/

// 퍼센트 계산: value의 percent%
function percentage(value, percent) {
  return (value * percent) / 100;
}

// 배열의 평균 계산
function average(numbers) {
  if (!Array.isArray(numbers) || numbers.length === 0) {
    throw new Error("비어 있지 않은 숫자 배열이 필요합니다");
  }
  const sum = numbers.reduce((acc, num) => acc + num, 0);
  return sum / numbers.length;
}

// 비동기 계산 시뮬레이션: 서버에서 환율을 가져와 변환
// (실제 fetch 대신 Promise로 시뮬레이션)
async function convertCurrency(amount, from, to) {
  // 가짜 환율 데이터 (실제로는 API 호출)
  const rates = {
    "USD-KRW": 1300,
    "KRW-USD": 1 / 1300,
    "EUR-KRW": 1420,
    "KRW-EUR": 1 / 1420,
    "USD-EUR": 0.92,
    "EUR-USD": 1.09,
  };

  const key = `${from}-${to}`;
  const rate = rates[key];

  if (!rate) {
    throw new Error(`환율 정보 없음: ${key}`);
  }

  // 서버 응답 시뮬레이션 (100ms 지연)
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        amount,
        from,
        to,
        rate,
        result: Math.round(amount * rate * 100) / 100,
      });
    }, 100);
  });
}

// 콜백을 받는 함수 (콜백 테스트용)
function calculateWithCallback(a, b, operation, callback) {
  try {
    let result;
    switch (operation) {
      case "add": result = add(a, b); break;
      case "subtract": result = subtract(a, b); break;
      case "multiply": result = multiply(a, b); break;
      case "divide": result = divide(a, b); break;
      default: throw new Error(`알 수 없는 연산: ${operation}`);
    }
    callback(null, result);
  } catch (error) {
    callback(error, null);
  }
}

/* ═══════════════════════════════════════════════════════════════
   섹션 4: 포맷팅 유틸리티
   ═══════════════════════════════════════════════════════════════ */

// 숫자를 한국 원화 형식으로 포맷
function formatKRW(amount) {
  return `${amount.toLocaleString("ko-KR")}원`;
}

// 계산식을 읽기 좋은 문자열로 변환
function formatExpression(a, operation, b, result) {
  const symbols = {
    add: "+",
    subtract: "-",
    multiply: "x",
    divide: "÷",
  };
  const symbol = symbols[operation] || "?";
  return `${a} ${symbol} ${b} = ${result}`;
}

/* ═══════════════════════════════════════════════════════════════
   모듈 내보내기
   ═══════════════════════════════════════════════════════════════ */
module.exports = {
  // 기본 연산
  add,
  subtract,
  multiply,
  divide,
  // 계산 + 기록
  calculate,
  getHistory,
  clearHistory,
  getLastResult,
  // 고급 기능
  percentage,
  average,
  convertCurrency,
  calculateWithCallback,
  // 포맷팅
  formatKRW,
  formatExpression,
};
