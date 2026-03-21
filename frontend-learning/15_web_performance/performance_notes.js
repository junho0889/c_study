/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  프론트엔드 15단계: 웹 성능 최적화                                ■
■  Critical Rendering Path, Lazy Loading, Debounce/Throttle,      ■
■  Virtual DOM, Web Workers, Service Workers, Lighthouse 지표      ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  이 파일은 웹 성능 최적화의 핵심 개념과 실제 구현을 다룹니다.
  모든 코드는 브라우저 또는 Node.js에서 실행 가능합니다.
*/

/* ═══════════════════════════════════════════════════════════════
   레슨 1: Critical Rendering Path (핵심 렌더링 경로)
   ═══════════════════════════════════════════════════════════════
   브라우저가 HTML을 받아서 화면에 그리기까지의 과정입니다.
   마치 "요리사가 레시피(HTML)를 읽고 → 재료를 준비하고(파싱) →
   요리하고(레이아웃) → 접시에 담는(페인트)" 과정과 같습니다!

   단계:
   ┌──────────┐   ┌─────────┐   ┌────────────┐   ┌────────┐   ┌───────┐
   │ HTML 파싱 │→ │ DOM 생성 │→ │ CSSOM 생성  │→ │ Layout │→ │ Paint │
   └──────────┘   └─────────┘   └────────────┘   └────────┘   └───────┘

   성능을 높이려면:
   1. HTML/CSS/JS 파일 크기 줄이기 (minify)
   2. 렌더링을 막는 리소스 줄이기 (render-blocking)
   3. 중요한 CSS는 <head>에 인라인으로 넣기
   4. JavaScript는 defer/async로 비동기 로딩
*/

function lesson1CriticalRenderingPath() {
  console.log("[레슨 1] Critical Rendering Path — 핵심 렌더링 경로");
  console.log();
  console.log("  브라우저 렌더링 단계:");
  console.log("  1. HTML 파싱 → DOM 트리 생성");
  console.log("  2. CSS 파싱 → CSSOM 트리 생성");
  console.log("  3. DOM + CSSOM → Render Tree 합치기");
  console.log("  4. Layout — 각 요소의 위치와 크기 계산");
  console.log("  5. Paint — 실제 픽셀로 그리기");
  console.log("  6. Composite — 레이어 합성");
  console.log();
  console.log("  최적화 팁:");
  console.log("  - <script defer> → HTML 파싱 후 JS 실행 (렌더링 안 막음)");
  console.log("  - <script async> → JS 다운 완료 즉시 실행 (순서 보장 X)");
  console.log("  - <link rel='preload'> → 중요 리소스 미리 다운로드");
  console.log("  - CSS 인라인화 → <style>로 첫 화면에 필요한 CSS 직접 삽입");
  console.log();
}

/* ═══════════════════════════════════════════════════════════════
   레슨 2: Debounce — 연속 호출을 마지막 한 번만 실행
   ═══════════════════════════════════════════════════════════════
   비유: 엘리베이터 문
   사람이 계속 타고 있으면 문을 안 닫고 기다렸다가,
   더 이상 아무도 안 오면 그때 문을 닫고 출발합니다!

   사용 예: 검색창 자동완성
   - 글자를 칠 때마다 API 호출하면 서버가 힘들어요
   - 타이핑이 멈춘 뒤 300ms 후 한 번만 호출!
*/

function debounce(func, delay) {
  // timerId를 클로저로 기억합니다
  // 클로저: 함수가 만들어진 환경을 기억하는 것
  // 마치 배낭 안에 타이머를 넣고 다니는 것과 같습니다!
  let timerId = null;

  return function debounced(...args) {
    // 이전 타이머가 있으면 취소! (아직 엘리베이터 문 닫지 마!)
    if (timerId !== null) {
      clearTimeout(timerId);
    }

    // 새 타이머 시작 (delay 후에 실행)
    timerId = setTimeout(() => {
      func.apply(this, args);   // 원래 함수 실행
      timerId = null;            // 타이머 초기화
    }, delay);
  };
}

function lesson2Debounce() {
  console.log("[레슨 2] Debounce — 마지막 호출만 실행하기");
  console.log();

  let callCount = 0;

  const debouncedLog = debounce((text) => {
    callCount++;
    console.log(`  [실행 #${callCount}] 검색어: "${text}"`);
  }, 300);

  // 빠르게 여러 번 호출해도...
  console.log("  '사' 입력 → debounce 호출 (타이머 시작)");
  debouncedLog("사");

  console.log("  '사과' 입력 → 이전 타이머 취소, 새 타이머 시작");
  debouncedLog("사과");

  console.log("  '사과주스' 입력 → 이전 타이머 취소, 새 타이머 시작");
  debouncedLog("사과주스");

  console.log("  → 300ms 후 '사과주스'로 딱 1번만 실행됩니다!");
  console.log();
}

/* ═══════════════════════════════════════════════════════════════
   레슨 3: Throttle — 일정 간격마다 최대 한 번만 실행
   ═══════════════════════════════════════════════════════════════
   비유: 수도꼭지의 수압 조절기
   아무리 빨리 틀어도 1초에 한 컵만 나오게 제한합니다!

   사용 예: 스크롤 이벤트
   - 스크롤은 1초에 수십 번 발생합니다
   - throttle로 100ms마다 한 번만 처리하면 성능 개선!

   Debounce vs Throttle:
   ┌──────────┬─────────────────────────┬──────────────────────────┐
   │          │ Debounce                │ Throttle                 │
   ├──────────┼─────────────────────────┼──────────────────────────┤
   │ 실행시점 │ 마지막 호출 후 delay 뒤 │ 첫 호출 후 interval마다  │
   │ 비유     │ 엘리베이터 문           │ 수도꼭지 수압 조절       │
   │ 적합     │ 검색, 입력 검증         │ 스크롤, 리사이즈, 드래그 │
   └──────────┴─────────────────────────┴──────────────────────────┘
*/

function throttle(func, interval) {
  let lastTime = 0;         // 마지막 실행 시간
  let timerId = null;        // 대기 중인 타이머

  return function throttled(...args) {
    const now = Date.now();
    const remaining = interval - (now - lastTime);

    if (remaining <= 0) {
      // 충분한 시간이 지남 → 바로 실행!
      if (timerId !== null) {
        clearTimeout(timerId);
        timerId = null;
      }
      lastTime = now;
      func.apply(this, args);
    } else if (timerId === null) {
      // 아직 interval이 안 지남 → 남은 시간 뒤에 실행 예약
      timerId = setTimeout(() => {
        lastTime = Date.now();
        timerId = null;
        func.apply(this, args);
      }, remaining);
    }
    // 이미 타이머가 있으면 무시 (이미 예약됨)
  };
}

function lesson3Throttle() {
  console.log("[레슨 3] Throttle — 일정 간격마다 실행 제한하기");
  console.log();

  let eventCount = 0;
  let executionCount = 0;

  const throttledScroll = throttle(() => {
    executionCount++;
    console.log(`  [실행 #${executionCount}] 스크롤 처리됨`);
  }, 200);

  // 빠르게 10번 호출 시뮬레이션
  for (let i = 0; i < 10; i++) {
    eventCount++;
    throttledScroll();
  }

  console.log(`  스크롤 이벤트 발생: ${eventCount}회`);
  console.log("  → 하지만 throttle 덕분에 200ms마다 1번만 실행됩니다!");
  console.log();
}

/* ═══════════════════════════════════════════════════════════════
   레슨 4: Lazy Loading — 필요할 때만 로딩하기
   ═══════════════════════════════════════════════════════════════
   비유: 뷔페에서 접시를 한 번에 다 가져오지 않고,
   먹을 만큼만 가져오는 것과 같습니다!

   종류:
   1. 이미지 Lazy Loading → 화면에 보일 때만 로드
   2. 코드 분할 (Code Splitting) → 필요한 페이지의 JS만 로드
   3. 무한 스크롤 → 스크롤할 때 추가 데이터 로드
*/

// ── Intersection Observer: 요소가 화면에 보이는지 감시하기 ──
// "감시 카메라"와 같습니다.
// 특정 요소가 화면(viewport)에 들어오면 알림을 줍니다.
function createLazyImageLoader() {
  // 브라우저 환경 확인
  if (typeof IntersectionObserver === "undefined") {
    console.log("  (IntersectionObserver는 브라우저에서만 사용 가능합니다)");
    return null;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        // isIntersecting: 요소가 화면에 보이는지
        if (entry.isIntersecting) {
          const img = entry.target;
          // data-src에 실제 이미지 URL을 저장해 두었다가
          // 화면에 보이면 src에 넣어서 로딩 시작!
          const realSrc = img.getAttribute("data-src");
          if (realSrc) {
            img.setAttribute("src", realSrc);
            img.removeAttribute("data-src");
            console.log(`  이미지 로딩 시작: ${realSrc}`);
          }
          // 한 번 로드하면 더 이상 감시 안 함
          observer.unobserve(img);
        }
      });
    },
    {
      // 옵션
      root: null,           // 기준 요소 (null = 뷰포트)
      rootMargin: "100px",  // 100px 미리 로딩 시작 (미리 준비!)
      threshold: 0.1,       // 10% 보이면 트리거
    }
  );

  return {
    // 이미지 요소를 감시 대상에 추가
    observe(imgElement) {
      observer.observe(imgElement);
    },
    // 감시 중단
    disconnect() {
      observer.disconnect();
    },
  };
}

// ── 코드 분할 (Code Splitting) 개념 ──
// React.lazy()와 dynamic import()를 사용합니다.
function lesson4LazyLoading() {
  console.log("[레슨 4] Lazy Loading — 필요할 때만 로딩하기");
  console.log();

  console.log("  1. 이미지 Lazy Loading:");
  console.log("     <img data-src='big-photo.jpg' class='lazy' />");
  console.log("     → IntersectionObserver가 화면에 보이면 data-src → src로 교체");
  console.log();

  console.log("  2. 코드 분할 (React):");
  console.log("     const HeavyPage = React.lazy(() => import('./HeavyPage'));");
  console.log("     → 이 페이지에 접속할 때만 JS 파일을 다운로드");
  console.log();

  console.log("  3. Dynamic Import:");
  console.log("     const module = await import('./heavyModule.js');");
  console.log("     → 필요한 시점에 모듈을 비동기로 불러오기");
  console.log();

  // Intersection Observer 생성 데모
  const loader = createLazyImageLoader();
  if (loader) {
    console.log("  IntersectionObserver 생성 완료!");
    loader.disconnect();
  }
  console.log();
}

/* ═══════════════════════════════════════════════════════════════
   레슨 5: Virtual DOM 개념
   ═══════════════════════════════════════════════════════════════
   Virtual DOM은 "메모장에 먼저 써보기"입니다.
   진짜 벽(실제 DOM)에 바로 페인트칠하면 실수하기 쉽고 느립니다.
   메모장(가상 DOM)에 먼저 그려보고, 바뀐 부분만 벽에 옮기면 훨씬 빠릅니다!

   과정:
   1. 상태 변경 → 새 Virtual DOM 생성
   2. 이전 Virtual DOM과 비교 (Diffing)
   3. 바뀐 부분만 실제 DOM에 반영 (Reconciliation)
*/

// 간단한 Virtual DOM 시뮬레이션
function createVNode(tag, props, children) {
  return { tag, props: props || {}, children: children || [] };
}

// 두 Virtual DOM을 비교하는 diff 함수 (개념 시뮬레이션)
function diff(oldNode, newNode) {
  const patches = [];

  // 노드가 완전히 다르면 교체
  if (oldNode.tag !== newNode.tag) {
    patches.push({ type: "REPLACE", node: newNode });
    return patches;
  }

  // props 비교
  const allProps = { ...oldNode.props, ...newNode.props };
  for (const key of Object.keys(allProps)) {
    if (oldNode.props[key] !== newNode.props[key]) {
      patches.push({
        type: "UPDATE_PROP",
        key,
        oldValue: oldNode.props[key],
        newValue: newNode.props[key],
      });
    }
  }

  // children 비교 (간단 버전)
  const maxLen = Math.max(oldNode.children.length, newNode.children.length);
  for (let i = 0; i < maxLen; i++) {
    if (!oldNode.children[i]) {
      patches.push({ type: "ADD_CHILD", node: newNode.children[i] });
    } else if (!newNode.children[i]) {
      patches.push({ type: "REMOVE_CHILD", index: i });
    } else if (typeof oldNode.children[i] === "string" && oldNode.children[i] !== newNode.children[i]) {
      patches.push({ type: "UPDATE_TEXT", oldText: oldNode.children[i], newText: newNode.children[i] });
    }
  }

  return patches;
}

function lesson5VirtualDOM() {
  console.log("[레슨 5] Virtual DOM — 바뀐 부분만 효율적으로 업데이트");
  console.log();

  // 이전 상태의 Virtual DOM
  const oldVDom = createVNode("div", { class: "card" }, [
    createVNode("h2", {}, ["민수의 프로필"]),
    createVNode("p", {}, ["점수: 85"]),
  ]);

  // 새 상태의 Virtual DOM (점수만 변경)
  const newVDom = createVNode("div", { class: "card" }, [
    createVNode("h2", {}, ["민수의 프로필"]),
    createVNode("p", {}, ["점수: 95"]),    // ← 여기만 바뀜!
  ]);

  // diff 실행
  const patches = diff(oldVDom, newVDom);
  console.log("  이전 DOM:", JSON.stringify(oldVDom.children[1].children));
  console.log("  새 DOM:  ", JSON.stringify(newVDom.children[1].children));

  // children의 diff
  const childPatches = diff(oldVDom.children[1], newVDom.children[1]);
  console.log("  변경 사항:", JSON.stringify(childPatches));
  console.log("  → '점수: 85'를 '점수: 95'로만 업데이트! 나머지는 그대로!");
  console.log();
}

/* ═══════════════════════════════════════════════════════════════
   레슨 6: Web Workers — 무거운 작업을 별도 스레드에서 실행
   ═══════════════════════════════════════════════════════════════
   비유: 식당에서 주방과 홀이 분리된 것과 같습니다.
   홀(메인 스레드)은 손님 응대(UI 반응)에 집중하고,
   주방(Web Worker)은 요리(무거운 계산)에 집중합니다.
   서로 "주문서(메시지)"를 주고받으며 소통합니다!

   주의: Web Worker 안에서는 DOM에 접근할 수 없습니다!
*/

// Web Worker용 코드 (실제로는 별도 파일에 작성)
const workerCode = `
  // worker.js — 별도 스레드에서 실행되는 코드
  self.onmessage = function(event) {
    const { type, data } = event.data;

    if (type === 'HEAVY_CALCULATION') {
      // 무거운 계산 (예: 큰 배열 정렬)
      const result = data.sort((a, b) => a - b);
      // 결과를 메인 스레드로 전달
      self.postMessage({ type: 'RESULT', data: result });
    }
  };
`;

function lesson6WebWorkers() {
  console.log("[레슨 6] Web Workers — 멀티스레드로 UI 버벅임 방지");
  console.log();
  console.log("  사용법:");
  console.log("  1. worker.js 파일 생성 (별도 스레드 코드)");
  console.log("  2. const worker = new Worker('worker.js');");
  console.log("  3. worker.postMessage({ data }); → 작업 요청");
  console.log("  4. worker.onmessage = (e) => { ... }; → 결과 수신");
  console.log();
  console.log("  메인 스레드 코드 예시:");
  console.log("  ──────────────────────────────────────");
  console.log("  const worker = new Worker('worker.js');");
  console.log("  worker.postMessage({ type: 'HEAVY_CALCULATION', data: bigArray });");
  console.log("  worker.onmessage = (event) => {");
  console.log("    console.log('결과:', event.data);");
  console.log("    // UI 업데이트 (메인 스레드니까 DOM 접근 가능!)");
  console.log("  };");
  console.log("  ──────────────────────────────────────");
  console.log();
  console.log("  적합한 작업: 대용량 데이터 처리, 이미지 변환, 암호화 등");
  console.log("  부적합: DOM 조작, window/document 접근이 필요한 작업");
  console.log();
}

/* ═══════════════════════════════════════════════════════════════
   레슨 7: Service Worker — 오프라인 지원과 캐싱
   ═══════════════════════════════════════════════════════════════
   비유: 편의점 창고입니다.
   자주 사는 물건(자주 요청하는 파일)을 창고(캐시)에 미리 쟁여 두면,
   공장(서버)까지 가지 않아도 바로 꺼내 줄 수 있습니다.
   심지어 인터넷이 끊겨도(오프라인) 창고에서 꺼내 줍니다!
*/

function lesson7ServiceWorker() {
  console.log("[레슨 7] Service Worker — 오프라인 지원과 캐싱");
  console.log();
  console.log("  Service Worker 생명주기:");
  console.log("  ┌──────────┐   ┌───────────┐   ┌──────────┐");
  console.log("  │ 등록     │→ │ 설치      │→ │ 활성화   │");
  console.log("  │ register │   │ install   │   │ activate │");
  console.log("  └──────────┘   └───────────┘   └──────────┘");
  console.log();
  console.log("  1. 등록 (register):");
  console.log("     navigator.serviceWorker.register('/sw.js');");
  console.log();
  console.log("  2. 설치 (install) — 캐시에 파일 저장:");
  console.log("     self.addEventListener('install', (event) => {");
  console.log("       event.waitUntil(");
  console.log("         caches.open('v1').then((cache) => {");
  console.log("           cache.addAll(['/index.html', '/app.js', '/style.css']);");
  console.log("         })");
  console.log("       );");
  console.log("     });");
  console.log();
  console.log("  3. 요청 가로채기 (fetch) — 캐시 먼저 확인:");
  console.log("     self.addEventListener('fetch', (event) => {");
  console.log("       event.respondWith(");
  console.log("         caches.match(event.request)");
  console.log("           .then((cached) => cached || fetch(event.request))");
  console.log("       );");
  console.log("     });");
  console.log();
  console.log("  캐싱 전략:");
  console.log("  - Cache First   → 캐시 우선, 없으면 네트워크 (정적 파일에 적합)");
  console.log("  - Network First → 네트워크 우선, 실패하면 캐시 (API에 적합)");
  console.log("  - Stale-While-Revalidate → 캐시 즉시 반환 + 백그라운드 업데이트");
  console.log();
}

/* ═══════════════════════════════════════════════════════════════
   레슨 8: Lighthouse 지표 (Core Web Vitals)
   ═══════════════════════════════════════════════════════════════
   Lighthouse는 "건강 검진"입니다.
   웹사이트의 성능, 접근성, SEO 등을 점수로 알려줍니다.

   Core Web Vitals — Google이 가장 중요하게 보는 3가지 지표:

   ┌──────┬─────────────────────────┬──────────┬──────────────────┐
   │ 지표 │ 의미                    │ 좋음     │ 개선 방법        │
   ├──────┼─────────────────────────┼──────────┼──────────────────┤
   │ LCP  │ 가장 큰 콘텐츠 로딩    │ < 2.5초  │ 이미지 최적화    │
   │ FID  │ 첫 입력 반응 지연      │ < 100ms  │ JS 최소화        │
   │ CLS  │ 레이아웃 흔들림 정도   │ < 0.1    │ 크기 미리 지정   │
   └──────┴─────────────────────────┴──────────┴──────────────────┘
*/

function lesson8LighthouseMetrics() {
  console.log("[레슨 8] Lighthouse 지표 — Core Web Vitals");
  console.log();

  // LCP (Largest Contentful Paint) — 가장 큰 콘텐츠 로딩 시간
  console.log("  LCP (Largest Contentful Paint):");
  console.log("  → 페이지의 '주인공'(가장 큰 이미지나 텍스트)이 보이기까지 걸린 시간");
  console.log("  → 좋음: 2.5초 미만 / 개선 필요: 4초 초과");
  console.log("  → 개선: 이미지 압축, CDN 사용, 서버 응답 시간 줄이기");
  console.log();

  // FID (First Input Delay) → INP (Interaction to Next Paint)로 대체됨
  console.log("  INP (Interaction to Next Paint, 구 FID):");
  console.log("  → 사용자가 버튼을 눌렀을 때 반응까지 걸린 시간");
  console.log("  → 좋음: 200ms 미만");
  console.log("  → 개선: 무거운 JS 분할, Web Worker 활용, 메인 스레드 부하 줄이기");
  console.log();

  // CLS (Cumulative Layout Shift) — 레이아웃 흔들림
  console.log("  CLS (Cumulative Layout Shift):");
  console.log("  → 페이지 로딩 중 요소가 갑자기 이동하는 정도");
  console.log("  → 좋음: 0.1 미만");
  console.log("  → 개선: 이미지/동영상에 width, height 지정, 폰트 미리 로드");
  console.log();

  console.log("  Lighthouse 실행 방법:");
  console.log("  1. Chrome DevTools → Lighthouse 탭 → Generate report");
  console.log("  2. npx lighthouse https://example.com --view");
  console.log("  3. web.dev/measure 에서 온라인 측정");
  console.log();
}

/* ═══════════════════════════════════════════════════════════════
   레슨 9: 번들 최적화 (Bundle Optimization)
   ═══════════════════════════════════════════════════════════════
   비유: 이사할 때 짐 싸기
   - 안 쓰는 물건은 버리고 (Tree Shaking)
   - 큰 가구는 분해해서 (Code Splitting)
   - 자주 쓰는 건 손닿는 곳에 (Preloading)
*/

function lesson9BundleOptimization() {
  console.log("[레슨 9] 번들 최적화 — JavaScript 파일 크기 줄이기");
  console.log();

  console.log("  1. Tree Shaking (나무 흔들기):");
  console.log("     → import한 것 중 실제로 쓰는 것만 남기고 나머지는 제거");
  console.log("     → import { add } from 'math'  ← add만 번들에 포함!");
  console.log("     → import * as math from 'math' ← 전부 포함 (비효율적)");
  console.log();

  console.log("  2. Code Splitting (코드 분할):");
  console.log("     → 페이지별로 JS 파일을 나눠서 필요한 것만 로드");
  console.log("     → React.lazy() + Suspense");
  console.log("     → Next.js는 자동으로 페이지별 분할!");
  console.log();

  console.log("  3. Minification (압축):");
  console.log("     → 변수 이름 축약, 공백/주석 제거");
  console.log("     → 도구: Terser, esbuild, SWC");
  console.log();

  console.log("  4. Compression (전송 압축):");
  console.log("     → 서버에서 gzip 또는 brotli로 압축 전송");
  console.log("     → Content-Encoding: gzip");
  console.log("     → 파일 크기 60~80% 감소!");
  console.log();

  console.log("  5. 번들 분석:");
  console.log("     → webpack-bundle-analyzer로 어떤 라이브러리가 큰지 확인");
  console.log("     → npx webpack-bundle-analyzer stats.json");
  console.log();
}

/* ═══════════════════════════════════════════════════════════════
   레슨 10: Intersection Observer 실전 패턴
   ═══════════════════════════════════════════════════════════════
   Intersection Observer를 활용한 실전 패턴들을 구현합니다.
*/

// ── 무한 스크롤 구현 ──
// 마지막 아이템이 화면에 보이면 다음 페이지 데이터를 불러옵니다.
function createInfiniteScroll(loadMore) {
  if (typeof IntersectionObserver === "undefined") {
    return { observe() {}, disconnect() {} };
  }

  const observer = new IntersectionObserver(
    (entries) => {
      // 마지막 요소가 보이면 추가 데이터 로드!
      if (entries[0].isIntersecting) {
        loadMore();
      }
    },
    { threshold: 0.5 }   // 50% 보이면 트리거
  );

  return {
    // 감시할 "센티널(sentinel)" 요소 등록
    // 목록 맨 아래에 보이지 않는 요소를 두고, 그것이 보이면 로드!
    observe(sentinelElement) {
      observer.observe(sentinelElement);
    },
    disconnect() {
      observer.disconnect();
    },
  };
}

// ── 스크롤 애니메이션 (Scroll Reveal) ──
// 요소가 화면에 나타나면 애니메이션 실행
function createScrollReveal(animationClass) {
  if (typeof IntersectionObserver === "undefined") {
    return { observe() {}, disconnect() {} };
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add(animationClass || "revealed");
          observer.unobserve(entry.target); // 한 번만!
        }
      });
    },
    { threshold: 0.15 }
  );

  return {
    observe(element) {
      observer.observe(element);
    },
    disconnect() {
      observer.disconnect();
    },
  };
}

function lesson10IntersectionPatterns() {
  console.log("[레슨 10] Intersection Observer 실전 패턴");
  console.log();

  console.log("  1. 이미지 Lazy Loading → createLazyImageLoader()");
  console.log("  2. 무한 스크롤 → createInfiniteScroll(loadMoreFn)");
  console.log("  3. 스크롤 애니메이션 → createScrollReveal('fade-in')");
  console.log();

  console.log("  무한 스크롤 사용 예:");
  console.log("  const scroller = createInfiniteScroll(() => {");
  console.log("    fetchNextPage().then(data => appendToList(data));");
  console.log("  });");
  console.log("  scroller.observe(document.querySelector('#sentinel'));");
  console.log();
}

/* ═══════════════════════════════════════════════════════════════
   실행: 모든 레슨을 순서대로 실행합니다
   ═══════════════════════════════════════════════════════════════ */

function main() {
  console.log("=".repeat(60));
  console.log("  웹 성능 최적화 교과서");
  console.log("=".repeat(60));
  console.log();

  lesson1CriticalRenderingPath();
  lesson2Debounce();
  lesson3Throttle();
  lesson4LazyLoading();
  lesson5VirtualDOM();
  lesson6WebWorkers();
  lesson7ServiceWorker();
  lesson8LighthouseMetrics();
  lesson9BundleOptimization();
  lesson10IntersectionPatterns();

  console.log("=".repeat(60));
  console.log("  모든 레슨 완료!");
  console.log("=".repeat(60));
}

main();

/* ═══════════════════════════════════════════════════════════════
   모듈 내보내기 (다른 파일에서 재사용 가능)
   ═══════════════════════════════════════════════════════════════ */
if (typeof module !== "undefined") {
  module.exports = {
    debounce,
    throttle,
    createLazyImageLoader,
    createInfiniteScroll,
    createScrollReveal,
    createVNode,
    diff,
  };
}
