/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  프론트엔드 12단계: React Hooks 완벽 정리                         ■
■  useState, useEffect, useContext, useReducer,                   ■
■  useMemo, useCallback, useRef, Custom Hooks                     ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  이 파일은 "쇼핑 카트 + 테마 전환" 앱을 만들면서
  React의 주요 Hook들을 하나씩 배웁니다.

  비유:
  - Hook은 "낚싯바늘"입니다.
    함수 컴포넌트라는 연못에 바늘을 던져서
    상태(state), 생명주기(lifecycle), 컨텍스트(context) 등
    React의 강력한 기능을 "낚아 올려" 사용합니다.
*/

import React, {
  useState,
  useEffect,
  useContext,
  useReducer,
  useMemo,
  useCallback,
  useRef,
  createContext,
} from "react";

/* ═══════════════════════════════════════════════════════════════
   섹션 1: useContext — 테마 & 언어 컨텍스트
   ═══════════════════════════════════════════════════════════════
   useContext는 "학교 방송 시스템"과 같습니다.
   교장 선생님(최상위 컴포넌트)이 방송(context)으로 알리면,
   모든 교실(하위 컴포넌트)에서 들을 수 있습니다.
   일일이 복도를 돌며 전달(props drilling)할 필요가 없습니다!
*/

// 테마 정의 — 밝은 모드와 어두운 모드
const themes = {
  light: {
    name: "light",
    bg: "#f8fafc",
    cardBg: "#ffffff",
    text: "#1e293b",
    primary: "#3b82f6",
    border: "#e2e8f0",
  },
  dark: {
    name: "dark",
    bg: "#0f172a",
    cardBg: "#1e293b",
    text: "#e2e8f0",
    primary: "#60a5fa",
    border: "#334155",
  },
};

// Context 생성 — 방송국 설치
const ThemeContext = createContext(themes.light);
const LanguageContext = createContext("ko");

/* ═══════════════════════════════════════════════════════════════
   섹션 2: useReducer — 장바구니 상태 관리
   ═══════════════════════════════════════════════════════════════
   useReducer는 "자판기 규칙표"입니다.
   - 현재 상태(state)와 어떤 일이 일어났는지(action)를 받아서
   - 규칙에 따라 다음 상태를 돌려줍니다.
   useState보다 복잡한 상태(여러 값이 서로 연결된 경우)에 적합합니다.
*/

// 상품 목록 데이터
const products = [
  { id: 1, name: "React 교과서", price: 28000, emoji: "📘" },
  { id: 2, name: "JavaScript 노트", price: 15000, emoji: "📒" },
  { id: 3, name: "TypeScript 스티커", price: 3000, emoji: "🏷️" },
  { id: 4, name: "Node.js 텀블러", price: 12000, emoji: "🥤" },
  { id: 5, name: "CSS 마우스패드", price: 8000, emoji: "🖱️" },
];

// 장바구니 초기 상태
const cartInitialState = {
  items: [],       // { productId, name, price, quantity }
  couponApplied: false,
};

// reducer 함수 — 자판기의 규칙표
function cartReducer(state, action) {
  // action.type으로 "무슨 버튼이 눌렸는지" 구분합니다.
  switch (action.type) {
    case "ADD_ITEM": {
      // 이미 담긴 상품인지 확인
      const existing = state.items.find(
        (item) => item.productId === action.payload.id
      );
      if (existing) {
        // 있으면 수량만 +1
        return {
          ...state,
          items: state.items.map((item) =>
            item.productId === action.payload.id
              ? { ...item, quantity: item.quantity + 1 }
              : item
          ),
        };
      }
      // 없으면 새로 추가
      return {
        ...state,
        items: [
          ...state.items,
          {
            productId: action.payload.id,
            name: action.payload.name,
            price: action.payload.price,
            quantity: 1,
          },
        ],
      };
    }

    case "REMOVE_ITEM":
      // 해당 상품을 장바구니에서 완전히 제거
      return {
        ...state,
        items: state.items.filter(
          (item) => item.productId !== action.payload.id
        ),
      };

    case "CHANGE_QUANTITY":
      // 수량 변경 (0 이하면 제거)
      if (action.payload.quantity <= 0) {
        return {
          ...state,
          items: state.items.filter(
            (item) => item.productId !== action.payload.id
          ),
        };
      }
      return {
        ...state,
        items: state.items.map((item) =>
          item.productId === action.payload.id
            ? { ...item, quantity: action.payload.quantity }
            : item
        ),
      };

    case "TOGGLE_COUPON":
      return { ...state, couponApplied: !state.couponApplied };

    case "CLEAR_CART":
      return cartInitialState;

    default:
      return state;
  }
}

/* ═══════════════════════════════════════════════════════════════
   섹션 3: Custom Hook — useLocalStorage
   ═══════════════════════════════════════════════════════════════
   커스텀 훅은 "나만의 도구 만들기"입니다.
   자주 쓰는 기능을 하나의 함수로 묶어서
   여러 컴포넌트에서 재사용할 수 있습니다.
   이름은 반드시 use로 시작해야 합니다!
*/
function useLocalStorage(key, initialValue) {
  // localStorage에서 값을 읽거나, 없으면 초기값 사용
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn("localStorage 읽기 실패:", error);
      return initialValue;
    }
  });

  // 값이 바뀔 때마다 localStorage에도 저장
  const setValue = (value) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.warn("localStorage 쓰기 실패:", error);
    }
  };

  return [storedValue, setValue];
}

/* ═══════════════════════════════════════════════════════════════
   섹션 4: Custom Hook — useDebounce
   ═══════════════════════════════════════════════════════════════
   입력할 때마다 바로 검색하면 너무 잦은 요청이 생깁니다.
   useDebounce는 "타이핑이 멈춘 뒤 잠깐 기다렸다 실행"합니다.
   엘리베이터가 문을 닫기 전 잠깐 기다리는 것과 비슷합니다!
*/
function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    // delay 밀리초 후에 값을 업데이트
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // 값이 바뀌면 이전 타이머를 취소하고 새 타이머 시작
    // 이것이 cleanup 함수입니다 — useEffect의 "뒷정리"
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

/* ═══════════════════════════════════════════════════════════════
   컴포넌트: ProductList — 상품 목록
   useMemo, useCallback 활용
   ═══════════════════════════════════════════════════════════════ */
function ProductList({ onAddItem }) {
  const theme = useContext(ThemeContext);
  const lang = useContext(LanguageContext);

  // useRef — DOM 요소에 직접 접근하기
  // useRef는 "이름표가 붙은 손가락"입니다.
  // 특정 HTML 요소를 가리켜 놓으면, 언제든 그 요소에 접근할 수 있습니다.
  const searchInputRef = useRef(null);

  const [searchTerm, setSearchTerm] = useState("");

  // useDebounce 커스텀 훅 사용!
  const debouncedSearch = useDebounce(searchTerm, 300);

  // useMemo — 비싼 계산 결과를 기억하기
  // useMemo는 "정답 노트"입니다.
  // 한 번 풀어 놓은 수학 문제의 답을 적어 두고,
  // 같은 문제가 나오면 다시 풀지 않고 노트를 봅니다.
  // debouncedSearch가 바뀔 때만 필터링을 다시 실행합니다.
  const filteredProducts = useMemo(() => {
    console.log("상품 필터링 실행! (useMemo 덕분에 불필요한 재실행 방지)");
    if (!debouncedSearch) return products;
    return products.filter((p) =>
      p.name.toLowerCase().includes(debouncedSearch.toLowerCase())
    );
  }, [debouncedSearch]);

  // useCallback — 함수를 기억하기
  // useCallback은 "한 번 만든 레시피 카드"입니다.
  // 매번 새 카드를 쓰지 않고, 같은 카드를 재사용합니다.
  // 자식 컴포넌트가 불필요하게 다시 그려지는 것을 방지합니다.
  const handleFocusSearch = useCallback(() => {
    // useRef로 가리킨 input에 포커스!
    searchInputRef.current?.focus();
  }, []);

  return (
    <div>
      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        <input
          ref={searchInputRef}
          type="text"
          placeholder={lang === "ko" ? "상품 검색..." : "Search..."}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            flex: 1,
            minWidth: 150,
            padding: "10px 14px",
            border: `2px solid ${theme.border}`,
            borderRadius: 8,
            fontSize: "1rem",
            background: theme.cardBg,
            color: theme.text,
          }}
        />
        <button
          onClick={handleFocusSearch}
          style={{
            padding: "10px 16px",
            background: theme.primary,
            color: "white",
            border: "none",
            borderRadius: 8,
            cursor: "pointer",
          }}
        >
          {lang === "ko" ? "검색창 포커스 (useRef)" : "Focus (useRef)"}
        </button>
      </div>

      {filteredProducts.map((product) => (
        <div
          key={product.id}
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "12px 16px",
            marginBottom: 8,
            background: theme.cardBg,
            border: `1px solid ${theme.border}`,
            borderRadius: 8,
          }}
        >
          <span>
            {product.emoji} {product.name} — {product.price.toLocaleString()}
            {lang === "ko" ? "원" : " KRW"}
          </span>
          <button
            onClick={() => onAddItem(product)}
            style={{
              padding: "6px 14px",
              background: theme.primary,
              color: "white",
              border: "none",
              borderRadius: 6,
              cursor: "pointer",
            }}
          >
            {lang === "ko" ? "담기" : "Add"}
          </button>
        </div>
      ))}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   컴포넌트: CartView — 장바구니 보기
   useMemo로 총액 계산 최적화
   ═══════════════════════════════════════════════════════════════ */
function CartView({ cart, dispatch }) {
  const theme = useContext(ThemeContext);
  const lang = useContext(LanguageContext);

  // useMemo — 총액을 매번 계산하지 않고, items가 바뀔 때만 계산
  const subtotal = useMemo(() => {
    return cart.items.reduce(
      (sum, item) => sum + item.price * item.quantity,
      0
    );
  }, [cart.items]);

  // 쿠폰 적용 시 10% 할인
  const total = cart.couponApplied ? Math.floor(subtotal * 0.9) : subtotal;
  const discount = subtotal - total;

  if (cart.items.length === 0) {
    return (
      <p style={{ color: theme.text, opacity: 0.6 }}>
        {lang === "ko" ? "장바구니가 비어 있습니다." : "Cart is empty."}
      </p>
    );
  }

  return (
    <div>
      {cart.items.map((item) => (
        <div
          key={item.productId}
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "10px 0",
            borderBottom: `1px solid ${theme.border}`,
            color: theme.text,
          }}
        >
          <span>{item.name}</span>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <button
              onClick={() =>
                dispatch({
                  type: "CHANGE_QUANTITY",
                  payload: { id: item.productId, quantity: item.quantity - 1 },
                })
              }
              style={{ padding: "2px 10px", cursor: "pointer" }}
            >
              -
            </button>
            <span>{item.quantity}</span>
            <button
              onClick={() =>
                dispatch({
                  type: "CHANGE_QUANTITY",
                  payload: { id: item.productId, quantity: item.quantity + 1 },
                })
              }
              style={{ padding: "2px 10px", cursor: "pointer" }}
            >
              +
            </button>
            <span style={{ minWidth: 80, textAlign: "right" }}>
              {(item.price * item.quantity).toLocaleString()}
              {lang === "ko" ? "원" : " KRW"}
            </span>
            <button
              onClick={() =>
                dispatch({ type: "REMOVE_ITEM", payload: { id: item.productId } })
              }
              style={{
                padding: "4px 10px",
                background: "#ef4444",
                color: "white",
                border: "none",
                borderRadius: 4,
                cursor: "pointer",
              }}
            >
              X
            </button>
          </div>
        </div>
      ))}

      {/* 합계 영역 */}
      <div style={{ marginTop: 16, color: theme.text }}>
        <div>
          {lang === "ko" ? "소계" : "Subtotal"}: {subtotal.toLocaleString()}
          {lang === "ko" ? "원" : " KRW"}
        </div>
        {cart.couponApplied && (
          <div style={{ color: "#ef4444" }}>
            {lang === "ko" ? "할인 (10%)" : "Discount (10%)"}: -
            {discount.toLocaleString()}
            {lang === "ko" ? "원" : " KRW"}
          </div>
        )}
        <div style={{ fontSize: "1.2rem", fontWeight: "bold", marginTop: 4 }}>
          {lang === "ko" ? "총액" : "Total"}: {total.toLocaleString()}
          {lang === "ko" ? "원" : " KRW"}
        </div>
      </div>

      {/* 쿠폰 / 비우기 버튼 */}
      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <button
          onClick={() => dispatch({ type: "TOGGLE_COUPON" })}
          style={{
            padding: "8px 16px",
            background: cart.couponApplied ? "#ef4444" : "#10b981",
            color: "white",
            border: "none",
            borderRadius: 6,
            cursor: "pointer",
          }}
        >
          {cart.couponApplied
            ? lang === "ko" ? "쿠폰 해제" : "Remove Coupon"
            : lang === "ko" ? "10% 쿠폰 적용" : "Apply 10% Coupon"}
        </button>
        <button
          onClick={() => dispatch({ type: "CLEAR_CART" })}
          style={{
            padding: "8px 16px",
            background: "#64748b",
            color: "white",
            border: "none",
            borderRadius: 6,
            cursor: "pointer",
          }}
        >
          {lang === "ko" ? "장바구니 비우기" : "Clear Cart"}
        </button>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   메인 컴포넌트: App
   useState, useEffect, useContext(Provider), useReducer 통합
   ═══════════════════════════════════════════════════════════════ */
export default function App() {
  /* ── useState: 테마와 언어 상태 ──
     useState는 "칠판"입니다.
     현재 값을 보여주고, 지우고 새 값을 쓸 수 있습니다.
     값이 바뀌면 React가 화면을 다시 그립니다. */
  const [themeName, setThemeName] = useLocalStorage("theme", "light");
  const [language, setLanguage] = useState("ko");

  const currentTheme = themes[themeName] || themes.light;

  /* ── useReducer: 장바구니 상태 ──
     dispatch(action)을 호출하면 reducer가 다음 상태를 계산합니다.
     useState로도 가능하지만, 액션이 여러 종류일 때 reducer가 더 깔끔합니다. */
  const [cart, dispatch] = useReducer(cartReducer, cartInitialState);

  /* ── useEffect: 생명주기 (라이프사이클) ──
     useEffect는 "알람 시계"입니다.
     컴포넌트가 화면에 나타나면(mount) 알람이 울리고,
     사라지면(unmount) 알람을 끕니다.

     의존성 배열([])에 따라 언제 실행되는지 달라집니다:
     - [] (빈 배열)    → 처음 한 번만 실행
     - [변수]          → 변수가 바뀔 때마다 실행
     - 배열 생략       → 매 렌더링마다 실행 (보통 권장하지 않음)
  */
  useEffect(() => {
    // 마운트 시 실행: 페이지 제목 설정
    document.title =
      language === "ko"
        ? `장바구니 (${cart.items.length}개)`
        : `Cart (${cart.items.length} items)`;
  }, [cart.items.length, language]);
  // ↑ cart.items.length 또는 language가 바뀔 때마다 제목 업데이트

  useEffect(() => {
    // 테마에 맞게 body 배경색 변경
    document.body.style.background = currentTheme.bg;
    document.body.style.transition = "background 0.3s";

    // cleanup 함수: 컴포넌트가 사라질 때 원래대로 돌려놓기
    return () => {
      document.body.style.background = "";
    };
  }, [currentTheme.bg]);

  // useCallback으로 안정적인 콜백 전달 (ProductList에 넘기는 함수)
  const handleAddItem = useCallback(
    (product) => {
      dispatch({ type: "ADD_ITEM", payload: product });
    },
    [dispatch]
  );

  // useRef로 렌더링 횟수 세기 (화면에 영향 주지 않는 값 저장)
  // useRef의 .current는 바뀌어도 리렌더링을 일으키지 않습니다.
  const renderCount = useRef(0);
  renderCount.current += 1;

  const cardStyle = {
    background: currentTheme.cardBg,
    border: `1px solid ${currentTheme.border}`,
    borderRadius: 16,
    padding: 24,
    marginBottom: 20,
    boxShadow: "0 4px 16px rgba(0,0,0,0.06)",
  };

  return (
    // Context Provider로 테마와 언어를 하위 컴포넌트에 "방송"
    <ThemeContext.Provider value={currentTheme}>
      <LanguageContext.Provider value={language}>
        <main
          style={{
            maxWidth: 800,
            margin: "0 auto",
            padding: 24,
            fontFamily: "'Malgun Gothic', sans-serif",
            color: currentTheme.text,
            minHeight: "100vh",
          }}
        >
          <h1>{language === "ko" ? "React Hooks 쇼핑 카트" : "React Hooks Shopping Cart"}</h1>
          <p style={{ opacity: 0.6, marginBottom: 8 }}>
            {language === "ko"
              ? `렌더링 횟수 (useRef): ${renderCount.current}번`
              : `Render count (useRef): ${renderCount.current}`}
          </p>

          {/* ── 테마 & 언어 전환 (useState + useContext) ── */}
          <div style={{ ...cardStyle }}>
            <h2>{language === "ko" ? "설정 (useContext + useState)" : "Settings (useContext + useState)"}</h2>
            <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 12 }}>
              <button
                onClick={() => setThemeName(themeName === "light" ? "dark" : "light")}
                style={{
                  padding: "10px 20px",
                  background: currentTheme.primary,
                  color: "white",
                  border: "none",
                  borderRadius: 8,
                  cursor: "pointer",
                  fontSize: "1rem",
                }}
              >
                {themeName === "light"
                  ? language === "ko" ? "어두운 모드로" : "Dark Mode"
                  : language === "ko" ? "밝은 모드로" : "Light Mode"}
              </button>
              <button
                onClick={() => setLanguage(language === "ko" ? "en" : "ko")}
                style={{
                  padding: "10px 20px",
                  background: "#64748b",
                  color: "white",
                  border: "none",
                  borderRadius: 8,
                  cursor: "pointer",
                  fontSize: "1rem",
                }}
              >
                {language === "ko" ? "English" : "한국어"}
              </button>
            </div>
          </div>

          {/* ── 상품 목록 (useMemo + useCallback + useRef) ── */}
          <div style={{ ...cardStyle }}>
            <h2>{language === "ko" ? "상품 목록 (useMemo + useCallback + useRef)" : "Products (useMemo + useCallback + useRef)"}</h2>
            <div style={{ marginTop: 12 }}>
              <ProductList onAddItem={handleAddItem} />
            </div>
          </div>

          {/* ── 장바구니 (useReducer) ── */}
          <div style={{ ...cardStyle }}>
            <h2>{language === "ko" ? "장바구니 (useReducer)" : "Cart (useReducer)"}</h2>
            <div style={{ marginTop: 12 }}>
              <CartView cart={cart} dispatch={dispatch} />
            </div>
          </div>

          {/* ── 학습 정리 ── */}
          <div style={{ ...cardStyle, background: currentTheme.primary, color: "white" }}>
            <h2>{language === "ko" ? "이 앱에서 사용한 Hooks 정리" : "Hooks Used in This App"}</h2>
            <ul style={{ marginTop: 12, paddingLeft: 20, lineHeight: 2 }}>
              <li><strong>useState</strong> — {language === "ko" ? "테마, 언어, 검색어 등 간단한 상태" : "Simple state (theme, language, search)"}</li>
              <li><strong>useEffect</strong> — {language === "ko" ? "페이지 제목 변경, body 배경 변경 (생명주기)" : "Document title, body background (lifecycle)"}</li>
              <li><strong>useContext</strong> — {language === "ko" ? "테마·언어를 모든 자식에게 전달 (Props 대신)" : "Theme & language broadcast (no prop drilling)"}</li>
              <li><strong>useReducer</strong> — {language === "ko" ? "장바구니 담기/빼기/수량/쿠폰 (복잡한 상태)" : "Cart add/remove/quantity/coupon (complex state)"}</li>
              <li><strong>useMemo</strong> — {language === "ko" ? "상품 필터링, 총액 계산 캐시 (비싼 계산)" : "Filter & total caching (expensive computation)"}</li>
              <li><strong>useCallback</strong> — {language === "ko" ? "handleAddItem 함수 재생성 방지 (안정된 참조)" : "Stable handleAddItem reference"}</li>
              <li><strong>useRef</strong> — {language === "ko" ? "검색 input 포커스, 렌더링 횟수 (리렌더 없는 값)" : "Input focus, render count (no re-render)"}</li>
              <li><strong>Custom Hooks</strong> — {language === "ko" ? "useLocalStorage (테마 저장), useDebounce (검색 지연)" : "useLocalStorage (persist), useDebounce (delay)"}</li>
            </ul>
          </div>
        </main>
      </LanguageContext.Provider>
    </ThemeContext.Provider>
  );
}
