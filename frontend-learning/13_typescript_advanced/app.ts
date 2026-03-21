/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  프론트엔드 13단계: TypeScript 심화                               ■
■  제네릭, 유틸리티 타입, 맵드 타입, 조건부 타입,                   ■
■  템플릿 리터럴 타입, 타입 가드, 판별 유니온                       ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  이 파일은 "타입 안전한 API 클라이언트"를 만들면서
  TypeScript의 심화 기능을 하나씩 배웁니다.
  모든 코드는 tsc로 컴파일 가능합니다.
*/

/* ═══════════════════════════════════════════════════════════════
   레슨 1: 제네릭 (Generics)
   ═══════════════════════════════════════════════════════════════
   제네릭은 "빈칸 있는 택배 상자"입니다.
   상자를 만들 때는 빈칸으로 두고,
   물건을 넣을 때 "이 상자는 과일용!" 또는 "이 상자는 책용!"이라고 적습니다.
   어떤 물건이든 넣을 수 있지만, 한번 정하면 다른 물건은 못 넣습니다.
*/

// ── 제네릭 함수: 배열의 첫 번째 요소 꺼내기 ──
// T는 "아직 모르는 타입"이라는 빈칸입니다.
// 호출할 때 TypeScript가 자동으로 T를 채워 넣습니다.
function getFirst<T>(items: T[]): T | undefined {
  return items[0];
}

// ── 제네릭 함수: 두 값을 묶어서 쌍(pair)으로 만들기 ──
function makePair<A, B>(first: A, second: B): [A, B] {
  return [first, second];
}

// ── 제네릭 + 제약 조건 (constraints) ──
// "빈칸이지만, 최소한 length 속성은 있어야 해!"라고 조건을 걸 수 있습니다.
// extends 키워드로 "이 타입은 최소한 이 모양이어야 한다"를 표현합니다.
interface HasLength {
  length: number;
}

function logWithLength<T extends HasLength>(value: T): T {
  console.log(`  길이: ${value.length}`);
  return value;
}

// ── 제네릭 클래스: 타입 안전한 저장소 ──
class TypedStorage<T> {
  private items: Map<string, T> = new Map();

  set(key: string, value: T): void {
    this.items.set(key, value);
  }

  get(key: string): T | undefined {
    return this.items.get(key);
  }

  getAll(): T[] {
    return Array.from(this.items.values());
  }
}

function lesson1Generics(): void {
  console.log("[레슨 1] 제네릭 — 타입을 매개변수로 넘기기");
  console.log();

  // getFirst<number> → T가 number로 확정됨
  const firstNum = getFirst([10, 20, 30]);
  console.log("  첫 번째 숫자:", firstNum);

  // getFirst<string> → T가 string으로 확정됨
  const firstStr = getFirst(["사과", "바나나", "체리"]);
  console.log("  첫 번째 과일:", firstStr);

  // makePair → A = string, B = number
  const pair = makePair("나이", 25);
  console.log("  쌍:", pair);

  // 제약 조건: length가 있는 값만 가능
  logWithLength("안녕하세요");     // 문자열은 length 있음
  logWithLength([1, 2, 3]);       // 배열도 length 있음
  // logWithLength(123);          // 숫자는 length 없음 → 컴파일 에러!

  // 제네릭 클래스 사용
  const scores = new TypedStorage<number>();
  scores.set("민수", 95);
  scores.set("지우", 88);
  console.log("  민수 점수:", scores.get("민수"));
  console.log("  전체:", scores.getAll());
  console.log();
}

/* ═══════════════════════════════════════════════════════════════
   레슨 2: 유틸리티 타입 (Utility Types)
   ═══════════════════════════════════════════════════════════════
   유틸리티 타입은 "기존 타입을 변형하는 마법 도구"입니다.
   이미 만든 레시피(타입)를 복사해서 일부만 바꿀 수 있습니다.

   - Partial<T>   → 모든 속성을 선택적(?)으로
   - Required<T>  → 모든 속성을 필수로
   - Pick<T, K>   → 특정 속성만 골라내기
   - Omit<T, K>   → 특정 속성만 빼기
   - Record<K, V> → 키-값 쌍의 타입 만들기
   - Readonly<T>  → 모든 속성을 읽기 전용으로
*/

interface User {
  id: number;
  name: string;
  email: string;
  age: number;
  role: "admin" | "user" | "guest";
}

function lesson2UtilityTypes(): void {
  console.log("[레슨 2] 유틸리티 타입 — 기존 타입을 변형하는 도구들");
  console.log();

  // Partial<User> → 모든 속성이 선택적
  // 사용자 정보를 "일부만" 수정할 때 유용합니다.
  // 마치 "전체 양식 중 바꾸고 싶은 칸만 채우세요"라고 하는 것!
  const updateData: Partial<User> = {
    name: "새이름",
    // 나머지는 안 적어도 OK!
  };
  console.log("  Partial 예:", updateData);

  // Pick<User, "id" | "name"> → id와 name만 골라내기
  // 전체 성적표에서 이름과 번호만 뽑아 명단을 만드는 것과 같습니다.
  const nameCard: Pick<User, "id" | "name"> = {
    id: 1,
    name: "민수",
  };
  console.log("  Pick 예:", nameCard);

  // Omit<User, "email" | "age"> → email과 age만 빼기
  // Pick의 반대: "이것만 빼고 나머지 다 가져와!"
  const publicInfo: Omit<User, "email" | "age"> = {
    id: 1,
    name: "민수",
    role: "user",
  };
  console.log("  Omit 예:", publicInfo);

  // Record<string, number> → 키가 string, 값이 number인 객체
  // 사전(dictionary)처럼, 단어(키)마다 뜻(값)이 정해진 구조입니다.
  const scores: Record<string, number> = {
    수학: 95,
    영어: 88,
    과학: 92,
  };
  console.log("  Record 예:", scores);

  // Readonly<User> → 모든 속성이 읽기 전용
  // 박물관의 전시품처럼 "보기만 하고 건드리지 마세요!"
  const frozenUser: Readonly<User> = {
    id: 1,
    name: "민수",
    email: "minsu@test.com",
    age: 15,
    role: "user",
  };
  console.log("  Readonly 예:", frozenUser.name);
  // frozenUser.name = "다른이름";  // 컴파일 에러! 읽기 전용!

  console.log();
}

/* ═══════════════════════════════════════════════════════════════
   레슨 3: 맵드 타입 (Mapped Types)
   ═══════════════════════════════════════════════════════════════
   맵드 타입은 "복사기 + 수정 기능"입니다.
   기존 타입의 모든 속성을 하나씩 돌면서
   새로운 규칙을 적용합니다.

   문법: { [K in keyof T]: 변형규칙 }
   keyof T → T의 모든 키를 유니온으로 가져옴
*/

// 모든 속성을 nullable(null 가능)로 만드는 맵드 타입
type Nullable<T> = {
  [K in keyof T]: T[K] | null;
};

// 모든 속성을 getter 함수로 바꾸는 맵드 타입
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};
// Capitalize는 첫 글자를 대문자로 바꿉니다.
// name → getName, age → getAge

// 특정 속성만 필수로, 나머지는 선택적으로
type RequireOnly<T, K extends keyof T> = Partial<T> & Pick<T, K>;

function lesson3MappedTypes(): void {
  console.log("[레슨 3] 맵드 타입 — 타입을 복사하며 변형하기");
  console.log();

  // Nullable<User> → 모든 속성에 null을 넣을 수 있음
  const maybeUser: Nullable<Pick<User, "name" | "email">> = {
    name: "민수",
    email: null,     // null 허용!
  };
  console.log("  Nullable 예:", maybeUser);

  // RequireOnly → id만 필수, 나머지는 선택
  const partialUser: RequireOnly<User, "id"> = {
    id: 42,
    name: "지우",   // 있어도 되고
    // email, age, role은 없어도 OK
  };
  console.log("  RequireOnly 예:", partialUser);

  console.log();
}

/* ═══════════════════════════════════════════════════════════════
   레슨 4: 조건부 타입 (Conditional Types)
   ═══════════════════════════════════════════════════════════════
   조건부 타입은 "타입 세계의 if문"입니다.
   "A가 B의 부분이면 이 타입, 아니면 저 타입"이라고 정합니다.

   문법: T extends 조건 ? 참일때타입 : 거짓일때타입
*/

// 배열이면 요소 타입을 꺼내고, 아니면 그대로 돌려주는 타입
type UnwrapArray<T> = T extends (infer U)[] ? U : T;
// infer U → "배열 안에 들어있는 타입을 U라고 부르겠다"
// 선물 상자를 열어서 안에 든 것의 타입을 알아내는 것과 같습니다!

// Promise면 안의 값 타입을 꺼내는 타입
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;

// 문자열이면 "text", 숫자면 "number", 그 외 "other"
type TypeLabel<T> = T extends string
  ? "text"
  : T extends number
    ? "number"
    : "other";

function lesson4ConditionalTypes(): void {
  console.log("[레슨 4] 조건부 타입 — 타입 세계의 if문");
  console.log();

  // UnwrapArray 사용 예시 (타입 레벨에서 동작)
  type NumberArray = number[];
  type Unwrapped = UnwrapArray<NumberArray>;  // number
  type NotArray = UnwrapArray<string>;         // string (배열이 아니니 그대로)

  const a: Unwrapped = 42;          // number 타입
  const b: NotArray = "hello";      // string 타입

  // TypeLabel 사용 예시
  const label1: TypeLabel<string> = "text";
  const label2: TypeLabel<number> = "number";
  const label3: TypeLabel<boolean> = "other";

  console.log("  UnwrapArray<number[]>:", typeof a, "→", a);
  console.log("  UnwrapArray<string>:", typeof b, "→", b);
  console.log("  TypeLabel 결과:", label1, label2, label3);
  console.log();
}

/* ═══════════════════════════════════════════════════════════════
   레슨 5: 템플릿 리터럴 타입 (Template Literal Types)
   ═══════════════════════════════════════════════════════════════
   템플릿 리터럴 타입은 "문자열 패턴 도장"입니다.
   "무슨색-무슨크기" 같은 패턴을 미리 정해 놓으면,
   그 패턴에 맞는 문자열만 허용합니다.
*/

type Color = "red" | "blue" | "green";
type Size = "small" | "medium" | "large";

// Color-Size 조합을 자동 생성!
// "red-small" | "red-medium" | "red-large" | "blue-small" | ...
type ColorSize = `${Color}-${Size}`;

// 이벤트 이름 패턴: "on" + 대문자시작
type EventName<T extends string> = `on${Capitalize<T>}`;
type ClickEvent = EventName<"click">;      // "onClick"
type ChangeEvent = EventName<"change">;    // "onChange"

// API 엔드포인트 패턴
type HttpMethod = "GET" | "POST" | "PUT" | "DELETE";
type ApiVersion = "v1" | "v2";
type Endpoint = `/${ApiVersion}/${string}`;

function lesson5TemplateLiteralTypes(): void {
  console.log("[레슨 5] 템플릿 리터럴 타입 — 문자열 패턴 강제하기");
  console.log();

  const shirt: ColorSize = "blue-medium";   // OK
  // const wrong: ColorSize = "yellow-big"; // 에러! 패턴에 없는 조합!

  const handler: ClickEvent = "onClick";     // OK
  // const bad: ClickEvent = "onHover";      // 에러!

  const endpoint: Endpoint = "/v1/users";    // OK

  console.log("  ColorSize:", shirt);
  console.log("  EventName:", handler);
  console.log("  Endpoint:", endpoint);
  console.log();
}

/* ═══════════════════════════════════════════════════════════════
   레슨 6: 타입 가드 (Type Guards)
   ═══════════════════════════════════════════════════════════════
   타입 가드는 "보안 검색대"입니다.
   값이 어떤 타입인지 확인한 뒤에만 통과시킵니다.
   검색대를 통과하면 TypeScript가 "아, 이건 이 타입이구나!"라고 알게 됩니다.

   3가지 방법:
   - typeof    → 원시 타입 확인 (string, number, boolean)
   - instanceof → 클래스 인스턴스 확인
   - is 키워드  → 커스텀 타입 가드 함수
   - in 연산자  → 속성 존재 여부 확인
*/

// ── typeof 타입 가드 ──
function formatValue(value: string | number | boolean): string {
  if (typeof value === "string") {
    // 이 블록 안에서 value는 string 타입!
    return `문자열: "${value}" (길이: ${value.length})`;
  }
  if (typeof value === "number") {
    // 이 블록 안에서 value는 number 타입!
    return `숫자: ${value.toFixed(2)}`;
  }
  // 남은 건 boolean뿐!
  return `불리언: ${value ? "참" : "거짓"}`;
}

// ── instanceof 타입 가드 ──
class Dog {
  bark(): string { return "멍멍!"; }
}

class Cat {
  meow(): string { return "야옹!"; }
}

function makeSound(animal: Dog | Cat): string {
  if (animal instanceof Dog) {
    return animal.bark();    // Dog의 메서드 사용 가능!
  }
  return animal.meow();      // 남은 건 Cat!
}

// ── is 키워드: 커스텀 타입 가드 ──
// 반환 타입에 "is"를 쓰면, true를 반환할 때 TypeScript가 타입을 확정합니다.
interface Fish {
  swim: () => void;
  name: string;
}

interface Bird {
  fly: () => void;
  name: string;
}

function isFish(animal: Fish | Bird): animal is Fish {
  return "swim" in animal;  // swim 속성이 있으면 Fish!
}

// ── in 연산자 ──
function describeAnimal(animal: Fish | Bird): string {
  if ("swim" in animal) {
    // "swim"이 있으니 Fish 타입!
    return `${animal.name}은(는) 수영합니다.`;
  }
  // swim이 없으니 Bird 타입!
  return `${animal.name}은(는) 날아갑니다.`;
}

function lesson6TypeGuards(): void {
  console.log("[레슨 6] 타입 가드 — 타입을 안전하게 좁히기");
  console.log();

  // typeof
  console.log("  " + formatValue("안녕"));
  console.log("  " + formatValue(3.14159));
  console.log("  " + formatValue(true));

  // instanceof
  console.log("  " + makeSound(new Dog()));
  console.log("  " + makeSound(new Cat()));

  // is + in
  const goldfish: Fish = { name: "금붕어", swim: () => {} };
  const eagle: Bird = { name: "독수리", fly: () => {} };

  console.log("  isFish(금붕어):", isFish(goldfish));
  console.log("  " + describeAnimal(goldfish));
  console.log("  " + describeAnimal(eagle));
  console.log();
}

/* ═══════════════════════════════════════════════════════════════
   레슨 7: 판별 유니온 (Discriminated Unions)
   ═══════════════════════════════════════════════════════════════
   판별 유니온은 "이름표가 붙은 택배 상자"입니다.
   모든 상자에 "종류(type)" 이름표가 붙어 있어서,
   이름표만 보면 안에 뭐가 들어있는지 정확히 알 수 있습니다.

   핵심: 공통 속성(판별자, discriminant)으로 타입을 구분합니다.
*/

// API 응답 타입: 성공 또는 실패
interface ApiSuccess<T> {
  status: "success";        // 판별자! 이 값으로 타입 구분
  data: T;
  timestamp: number;
}

interface ApiError {
  status: "error";          // 판별자!
  message: string;
  code: number;
}

interface ApiLoading {
  status: "loading";        // 판별자!
}

type ApiResponse<T> = ApiSuccess<T> | ApiError | ApiLoading;

// ── 판별 유니온을 사용하는 함수 ──
// status 값에 따라 TypeScript가 자동으로 타입을 좁혀줍니다!
function handleResponse<T>(response: ApiResponse<T>): string {
  switch (response.status) {
    case "loading":
      // 여기서 response는 ApiLoading 타입!
      return "로딩 중...";

    case "success":
      // 여기서 response는 ApiSuccess<T> 타입!
      // data 속성에 접근 가능!
      return `성공! 데이터: ${JSON.stringify(response.data)}`;

    case "error":
      // 여기서 response는 ApiError 타입!
      // message, code 속성에 접근 가능!
      return `에러 ${response.code}: ${response.message}`;
  }
}

function lesson7DiscriminatedUnions(): void {
  console.log("[레슨 7] 판별 유니온 — 이름표로 타입 구분하기");
  console.log();

  const loading: ApiResponse<string> = { status: "loading" };
  const success: ApiResponse<string> = {
    status: "success",
    data: "환영합니다!",
    timestamp: Date.now(),
  };
  const error: ApiResponse<string> = {
    status: "error",
    message: "서버 연결 실패",
    code: 500,
  };

  console.log("  " + handleResponse(loading));
  console.log("  " + handleResponse(success));
  console.log("  " + handleResponse(error));
  console.log();
}

/* ═══════════════════════════════════════════════════════════════
   레슨 8: 종합 실습 — 타입 안전한 API 클라이언트
   ═══════════════════════════════════════════════════════════════
   지금까지 배운 모든 것을 합쳐서
   실제로 사용할 수 있는 API 클라이언트를 만들어 봅시다!
*/

// ── API 엔드포인트별 요청/응답 타입 매핑 ──
interface UserData {
  id: number;
  name: string;
  email: string;
}

interface PostData {
  id: number;
  title: string;
  body: string;
  authorId: number;
}

// 엔드포인트 → 응답 타입 매핑 (맵드 타입 + 제네릭 활용)
interface ApiEndpoints {
  "/users": UserData[];
  "/users/:id": UserData;
  "/posts": PostData[];
  "/posts/:id": PostData;
}

// HTTP 메서드별 옵션 타입
interface RequestOptions<TBody = unknown> {
  headers?: Record<string, string>;
  body?: TBody;
  timeout?: number;
}

// ── 타입 안전한 API 클라이언트 클래스 ──
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  // 제네릭으로 엔드포인트에 맞는 응답 타입을 자동 추론!
  // K extends keyof ApiEndpoints → 등록된 엔드포인트만 허용
  async get<K extends keyof ApiEndpoints>(
    endpoint: K,
    options?: RequestOptions
  ): Promise<ApiResponse<ApiEndpoints[K]>> {
    console.log(`  GET ${this.baseUrl}${endpoint}`);

    // 시뮬레이션: 실제로는 fetch를 사용합니다
    try {
      // 성공 응답 시뮬레이션
      const mockData = this.getMockData(endpoint);
      return {
        status: "success",
        data: mockData as ApiEndpoints[K],
        timestamp: Date.now(),
      };
    } catch (err) {
      return {
        status: "error",
        message: err instanceof Error ? err.message : "알 수 없는 에러",
        code: 500,
      };
    }
  }

  // 목 데이터 (실제 앱에서는 서버 응답)
  private getMockData(endpoint: string): unknown {
    const mockDb: Record<string, unknown> = {
      "/users": [
        { id: 1, name: "민수", email: "minsu@test.com" },
        { id: 2, name: "지우", email: "jiwoo@test.com" },
      ],
      "/users/:id": { id: 1, name: "민수", email: "minsu@test.com" },
      "/posts": [
        { id: 1, title: "첫 글", body: "안녕하세요!", authorId: 1 },
      ],
      "/posts/:id": { id: 1, title: "첫 글", body: "안녕하세요!", authorId: 1 },
    };
    return mockDb[endpoint];
  }
}

async function lesson8ApiClient(): Promise<void> {
  console.log("[레슨 8] 종합 — 타입 안전한 API 클라이언트");
  console.log();

  const api = new ApiClient("https://api.example.com");

  // endpoint가 "/users"이면 응답은 자동으로 UserData[] 타입!
  const usersResponse = await api.get("/users");
  console.log("  " + handleResponse(usersResponse));

  // endpoint가 "/posts/:id"이면 응답은 자동으로 PostData 타입!
  const postResponse = await api.get("/posts/:id");
  console.log("  " + handleResponse(postResponse));

  // api.get("/wrong"); // 컴파일 에러! 등록되지 않은 엔드포인트!

  console.log();
}

/* ═══════════════════════════════════════════════════════════════
   실행: 모든 레슨을 순서대로 실행합니다
   ═══════════════════════════════════════════════════════════════ */
async function main(): Promise<void> {
  console.log("=".repeat(60));
  console.log("  TypeScript 심화 교과서");
  console.log("=".repeat(60));
  console.log();

  lesson1Generics();
  lesson2UtilityTypes();
  lesson3MappedTypes();
  lesson4ConditionalTypes();
  lesson5TemplateLiteralTypes();
  lesson6TypeGuards();
  lesson7DiscriminatedUnions();
  await lesson8ApiClient();

  console.log("=".repeat(60));
  console.log("  모든 레슨 완료!");
  console.log("=".repeat(60));
}

main();
