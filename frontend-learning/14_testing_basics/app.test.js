/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  프론트엔드 14단계: 테스트 기초 — 계산기 테스트 파일               ■
■  Jest를 사용한 단위 테스트(Unit Test) 작성법을 배웁니다.           ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  실행 방법: npx jest app.test.js
  (먼저 npm install --save-dev jest 필요)

  비유:
  - 테스트는 "자동 채점기"입니다.
    선생님이 시험 답안을 하나하나 채점하듯,
    테스트 코드가 함수의 결과를 하나하나 확인합니다.
    한 번 만들어 놓으면 버튼 하나로 수백 개를 자동 채점!

  테스트 구조:
  ┌─────────────────────────────────────────────┐
  │ describe("묶음 이름", () => {               │  ← 과목 (수학, 영어...)
  │   it("개별 테스트", () => {                 │  ← 문제 1번
  │     expect(실제값).toBe(기대값);            │  ← 채점: 정답 확인!
  │   });                                       │
  │ });                                         │
  └─────────────────────────────────────────────┘

  TDD (테스트 주도 개발) 흐름:
  1. RED    → 실패하는 테스트를 먼저 쓴다 (아직 코드가 없으니까!)
  2. GREEN  → 테스트를 통과할 최소한의 코드를 쓴다
  3. REFACTOR → 코드를 깔끔하게 정리한다 (테스트가 여전히 통과하는지 확인)
*/

const {
  add,
  subtract,
  multiply,
  divide,
  calculate,
  getHistory,
  clearHistory,
  getLastResult,
  percentage,
  average,
  convertCurrency,
  calculateWithCallback,
  formatKRW,
  formatExpression,
} = require("./calculator");

/* ═══════════════════════════════════════════════════════════════
   테스트 그룹 1: 기본 사칙연산
   ═══════════════════════════════════════════════════════════════
   가장 간단한 테스트부터 시작합니다.
   "입력 → 기대 출력"만 확인하면 됩니다.

   Matcher(비교기) 종류:
   - toBe(값)          → 정확히 같은지 (=== 비교)
   - toEqual(값)       → 객체/배열의 내용이 같은지 (깊은 비교)
   - toBeCloseTo(값)   → 소수점 비교 (부동소수점 오차 허용)
   - toBeTruthy()      → true로 평가되는지
   - toBeFalsy()       → false로 평가되는지
   - toBeNull()        → null인지
   - toContain(요소)   → 배열에 요소가 포함되어 있는지
   - toThrow()         → 에러가 발생하는지
*/

describe("기본 사칙연산", () => {
  // ── 덧셈 테스트 ──
  // describe 안에 describe를 넣어서 더 세분화할 수 있습니다.
  describe("add (덧셈)", () => {
    it("두 양수를 더한다", () => {
      // expect(실제값).toBe(기대값)
      // "add(2, 3)의 결과가 5인지 확인해!"
      expect(add(2, 3)).toBe(5);
    });

    it("음수를 더한다", () => {
      expect(add(-1, -2)).toBe(-3);
    });

    it("0을 더하면 원래 값이 나온다", () => {
      expect(add(7, 0)).toBe(7);
      expect(add(0, 7)).toBe(7);
    });

    it("소수를 더한다", () => {
      // 부동소수점 주의! 0.1 + 0.2 !== 0.3
      // toBe 대신 toBeCloseTo를 사용합니다.
      expect(add(0.1, 0.2)).toBeCloseTo(0.3);
    });
  });

  // ── 뺄셈 테스트 ──
  describe("subtract (뺄셈)", () => {
    it("큰 수에서 작은 수를 뺀다", () => {
      expect(subtract(10, 3)).toBe(7);
    });

    it("같은 수를 빼면 0이 된다", () => {
      expect(subtract(5, 5)).toBe(0);
    });

    it("음수 결과도 올바르게 처리한다", () => {
      expect(subtract(3, 10)).toBe(-7);
    });
  });

  // ── 곱셈 테스트 ──
  describe("multiply (곱셈)", () => {
    it("두 수를 곱한다", () => {
      expect(multiply(4, 5)).toBe(20);
    });

    it("0을 곱하면 0이 된다", () => {
      expect(multiply(100, 0)).toBe(0);
    });

    it("음수끼리 곱하면 양수가 된다", () => {
      expect(multiply(-3, -4)).toBe(12);
    });
  });

  // ── 나눗셈 테스트 ──
  describe("divide (나눗셈)", () => {
    it("두 수를 나눈다", () => {
      expect(divide(10, 2)).toBe(5);
    });

    it("나누어 떨어지지 않는 경우", () => {
      expect(divide(10, 3)).toBeCloseTo(3.3333, 3);
    });

    // toThrow() — 에러가 발생하는지 확인하는 matcher
    // "이 함수를 실행하면 에러가 터져야 해!"
    // 주의: expect 안에 함수를 넣어야 합니다 (직접 호출 X)
    it("0으로 나누면 에러가 발생한다", () => {
      expect(() => divide(10, 0)).toThrow("0으로 나눌 수 없습니다");
    });

    it("0으로 나누면 Error 타입이 발생한다", () => {
      expect(() => divide(10, 0)).toThrow(Error);
    });
  });
});

/* ═══════════════════════════════════════════════════════════════
   테스트 그룹 2: 계산 + 기록 관리
   ═══════════════════════════════════════════════════════════════
   상태(state)가 있는 함수를 테스트할 때는
   beforeEach로 매 테스트 전 상태를 초기화해야 합니다.

   테스트 간 독립성이 중요합니다!
   시험을 볼 때 앞 문제의 답이 뒷 문제에 영향을 주면 안 되는 것처럼,
   각 테스트는 서로 영향을 주지 않아야 합니다.
*/

describe("계산 + 기록 관리", () => {
  // beforeEach: 각 테스트(it) 실행 전에 매번 실행됩니다.
  // "시험지 새로 나눠주기" — 매 문제마다 깨끗한 상태에서 시작!
  beforeEach(() => {
    clearHistory();
  });

  it("calculate로 덧셈을 수행한다", () => {
    const result = calculate("add", 3, 4);
    expect(result).toBe(7);
  });

  it("계산 후 기록이 남는다", () => {
    calculate("add", 1, 2);
    calculate("multiply", 3, 4);

    const history = getHistory();

    // toHaveLength — 배열 길이 확인
    expect(history).toHaveLength(2);

    // toEqual — 객체의 "내용"이 같은지 확인 (깊은 비교)
    // toBe는 참조(주소)가 같은지 확인하므로 객체에는 toEqual 사용!
    expect(history[0]).toEqual(
      expect.objectContaining({
        operation: "add",
        a: 1,
        b: 2,
        result: 3,
      })
    );
    // expect.objectContaining — "이 속성들은 반드시 포함해야 해!"
    // timestamp 등 매번 바뀌는 속성은 검사하지 않아도 됩니다.
  });

  it("getLastResult가 마지막 결과를 반환한다", () => {
    calculate("add", 10, 20);
    calculate("subtract", 100, 50);
    expect(getLastResult()).toBe(50);
  });

  it("기록이 없으면 getLastResult가 null을 반환한다", () => {
    expect(getLastResult()).toBeNull();
  });

  it("clearHistory로 기록을 초기화한다", () => {
    calculate("add", 1, 1);
    calculate("add", 2, 2);
    clearHistory();
    expect(getHistory()).toHaveLength(0);
  });

  it("알 수 없는 연산이면 에러가 발생한다", () => {
    expect(() => calculate("modulo", 10, 3)).toThrow("알 수 없는 연산");
  });
});

/* ═══════════════════════════════════════════════════════════════
   테스트 그룹 3: 고급 계산 기능
   ═══════════════════════════════════════════════════════════════ */

describe("고급 계산 기능", () => {
  // ── 퍼센트 계산 ──
  describe("percentage (퍼센트)", () => {
    it("200의 10%는 20이다", () => {
      expect(percentage(200, 10)).toBe(20);
    });

    it("50의 50%는 25이다", () => {
      expect(percentage(50, 50)).toBe(25);
    });

    it("100의 0%는 0이다", () => {
      expect(percentage(100, 0)).toBe(0);
    });
  });

  // ── 평균 계산 ──
  describe("average (평균)", () => {
    it("숫자 배열의 평균을 계산한다", () => {
      expect(average([10, 20, 30])).toBe(20);
    });

    it("하나의 숫자도 평균이 된다", () => {
      expect(average([42])).toBe(42);
    });

    it("빈 배열이면 에러가 발생한다", () => {
      expect(() => average([])).toThrow("비어 있지 않은 숫자 배열");
    });

    it("배열이 아니면 에러가 발생한다", () => {
      expect(() => average("숫자가 아닙니다")).toThrow();
    });
  });
});

/* ═══════════════════════════════════════════════════════════════
   테스트 그룹 4: 비동기 테스트 (async/await)
   ═══════════════════════════════════════════════════════════════
   비동기 함수를 테스트할 때는 it 콜백에 async를 붙이고,
   await로 결과를 기다립니다.
   "택배가 올 때까지 기다린 뒤 확인하기"와 같습니다!

   방법 1: async/await (가장 권장!)
   방법 2: .resolves / .rejects matcher
*/

describe("비동기 테스트 — 환율 변환", () => {
  // 방법 1: async/await
  it("USD를 KRW로 변환한다", async () => {
    // await로 Promise가 완료될 때까지 기다립니다
    const result = await convertCurrency(100, "USD", "KRW");

    expect(result).toEqual(
      expect.objectContaining({
        amount: 100,
        from: "USD",
        to: "KRW",
        rate: 1300,
        result: 130000,
      })
    );
  });

  it("EUR를 KRW로 변환한다", async () => {
    const result = await convertCurrency(50, "EUR", "KRW");
    expect(result.result).toBe(71000);
  });

  // 방법 2: .resolves matcher
  // "이 Promise가 성공적으로 완료되면, 결과가 이것과 같아야 해!"
  it("KRW를 USD로 변환 (.resolves 사용)", async () => {
    await expect(convertCurrency(1300, "KRW", "USD")).resolves.toEqual(
      expect.objectContaining({
        from: "KRW",
        to: "USD",
        result: 1,
      })
    );
  });

  // .rejects — 에러가 발생하는 비동기 함수 테스트
  // "이 Promise가 실패(reject)하면, 에러 메시지가 이것이어야 해!"
  it("지원하지 않는 통화 쌍이면 에러가 발생한다", async () => {
    await expect(
      convertCurrency(100, "BTC", "KRW")
    ).rejects.toThrow("환율 정보 없음");
  });
});

/* ═══════════════════════════════════════════════════════════════
   테스트 그룹 5: 모킹 (Mocking) — jest.fn()
   ═══════════════════════════════════════════════════════════════
   모킹은 "대역 배우"입니다.
   실제 함수 대신 가짜 함수를 넣어서
   "이 함수가 호출되었는지", "몇 번 호출되었는지",
   "어떤 인자로 호출되었는지"를 확인합니다.

   jest.fn() — 빈 가짜 함수 만들기
   .toHaveBeenCalled()        — 호출되었는지
   .toHaveBeenCalledTimes(n)  — n번 호출되었는지
   .toHaveBeenCalledWith(...) — 이 인자로 호출되었는지
*/

describe("모킹 (Mocking)", () => {
  it("콜백 함수가 올바르게 호출되는지 확인한다", () => {
    // jest.fn()으로 가짜 콜백 생성
    const mockCallback = jest.fn();

    calculateWithCallback(3, 4, "add", mockCallback);

    // 콜백이 호출되었는지?
    expect(mockCallback).toHaveBeenCalled();

    // 정확히 1번 호출되었는지?
    expect(mockCallback).toHaveBeenCalledTimes(1);

    // 어떤 인자로 호출되었는지?
    // 성공 시: callback(null, result)
    expect(mockCallback).toHaveBeenCalledWith(null, 7);
  });

  it("에러 시 콜백에 에러 객체가 전달된다", () => {
    const mockCallback = jest.fn();

    calculateWithCallback(10, 0, "divide", mockCallback);

    // 에러 시: callback(error, null)
    expect(mockCallback).toHaveBeenCalledWith(
      expect.any(Error),  // Error 인스턴스면 OK (구체적인 값 대신 타입만 확인)
      null
    );
  });

  it("jest.fn()으로 반환값을 지정할 수 있다", () => {
    // mockReturnValue — 가짜 함수가 특정 값을 반환하도록 설정
    const mockFetch = jest.fn();
    mockFetch.mockReturnValue({ status: 200, data: "성공" });

    const result = mockFetch("https://api.example.com");
    expect(result).toEqual({ status: 200, data: "성공" });
    expect(mockFetch).toHaveBeenCalledWith("https://api.example.com");
  });

  it("jest.fn()으로 여러 번 호출 시 다른 값을 반환할 수 있다", () => {
    const mockRandom = jest.fn();
    // mockReturnValueOnce — 호출 순서대로 다른 값 반환
    mockRandom
      .mockReturnValueOnce(1)
      .mockReturnValueOnce(2)
      .mockReturnValueOnce(3);

    expect(mockRandom()).toBe(1);  // 첫 번째 호출
    expect(mockRandom()).toBe(2);  // 두 번째 호출
    expect(mockRandom()).toBe(3);  // 세 번째 호출
  });
});

/* ═══════════════════════════════════════════════════════════════
   테스트 그룹 6: 포맷팅 유틸리티
   ═══════════════════════════════════════════════════════════════
   문자열 비교는 toBe로 충분합니다.
   toContain은 "이 문자열이 포함되어 있는지"를 확인합니다.
   toMatch는 정규표현식으로 패턴을 확인합니다.
*/

describe("포맷팅 유틸리티", () => {
  describe("formatKRW (원화 포맷)", () => {
    it("숫자를 원화 형식으로 변환한다", () => {
      const result = formatKRW(15000);
      // toContain — 문자열에 특정 텍스트가 포함되어 있는지
      expect(result).toContain("원");
      expect(result).toContain("15");
    });

    it("0원도 올바르게 표시한다", () => {
      expect(formatKRW(0)).toContain("0");
      expect(formatKRW(0)).toContain("원");
    });
  });

  describe("formatExpression (수식 포맷)", () => {
    it("덧셈 수식을 포맷한다", () => {
      expect(formatExpression(3, "add", 4, 7)).toBe("3 + 4 = 7");
    });

    it("뺄셈 수식을 포맷한다", () => {
      expect(formatExpression(10, "subtract", 3, 7)).toBe("10 - 3 = 7");
    });

    it("곱셈 수식을 포맷한다", () => {
      expect(formatExpression(4, "multiply", 5, 20)).toBe("4 x 5 = 20");
    });

    it("나눗셈 수식을 포맷한다", () => {
      // toMatch — 정규표현식으로 패턴 확인
      const result = formatExpression(10, "divide", 2, 5);
      expect(result).toMatch(/10\s*÷\s*2\s*=\s*5/);
    });
  });
});

/* ═══════════════════════════════════════════════════════════════
   테스트 그룹 7: DOM 테스트 개념 (주석 설명)
   ═══════════════════════════════════════════════════════════════
   실제 DOM 테스트는 @testing-library/dom 또는
   @testing-library/react를 사용합니다.
   여기서는 개념만 설명합니다.

   DOM 테스트의 핵심 도구:
   - render()              → 컴포넌트를 가상 DOM에 그리기
   - screen.getByText()    → 텍스트로 요소 찾기
   - screen.getByRole()    → 역할(button, heading 등)로 찾기
   - fireEvent.click()     → 클릭 이벤트 발생시키기
   - waitFor()             → 비동기 변경 기다리기

   예시 (React Testing Library):
   ──────────────────────────────────────────────
   import { render, screen, fireEvent } from '@testing-library/react';
   import Counter from './Counter';

   it('버튼을 클릭하면 숫자가 올라간다', () => {
     render(<Counter />);
     const button = screen.getByRole('button', { name: '올리기' });
     fireEvent.click(button);
     expect(screen.getByText('1')).toBeInTheDocument();
   });
   ──────────────────────────────────────────────
*/

/* ═══════════════════════════════════════════════════════════════
   테스트 그룹 8: TDD 워크플로우 예제
   ═══════════════════════════════════════════════════════════════
   TDD 단계를 따라가 봅시다.
   "최대값 구하기" 함수를 TDD로 만든다고 가정:

   1. RED: 먼저 테스트를 쓴다 (아직 함수가 없어 실패!)
   2. GREEN: 테스트를 통과할 최소한의 코드를 쓴다
   3. REFACTOR: 코드를 깔끔하게 정리한다

   아래는 이미 완성된 상태이지만, 과정을 주석으로 보여줍니다.
*/

// [TDD 2단계 - GREEN] 테스트를 통과할 최소한의 코드
function findMax(numbers) {
  if (!Array.isArray(numbers) || numbers.length === 0) {
    throw new Error("비어 있지 않은 배열이 필요합니다");
  }
  return Math.max(...numbers);
}

// [TDD 1단계 - RED → GREEN] 테스트 작성
describe("TDD 예제 — findMax", () => {
  it("배열에서 가장 큰 수를 찾는다", () => {
    expect(findMax([3, 7, 2, 9, 4])).toBe(9);
  });

  it("음수만 있어도 가장 큰 수를 찾는다", () => {
    expect(findMax([-5, -1, -10])).toBe(-1);
  });

  it("하나짜리 배열도 처리한다", () => {
    expect(findMax([42])).toBe(42);
  });

  it("빈 배열이면 에러가 발생한다", () => {
    expect(() => findMax([])).toThrow("비어 있지 않은 배열");
  });

  // [TDD 3단계 - REFACTOR]
  // 코드를 개선하더라도 위 테스트가 모두 통과하면 안전합니다!
  // 이것이 TDD의 힘 — 리팩토링할 때 "안전망"이 생깁니다.
});
