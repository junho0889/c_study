/*
=============================================================================
  C++ 학습 11단계: 디버깅 가이드
=============================================================================
  [학습 목표]
  1. 흔한 버그 유형과 해결법을 안다
  2. 디버거(GDB, Visual Studio)를 사용할 수 있다
  3. 디버깅 기법(로그, assert, sanitizer)을 활용한다
  4. 컴파일 에러 메시지를 읽을 수 있다

  [컴파일 - 디버그 모드]
  g++ -std=c++17 -g -Wall -Wextra -o 11_debug main.cpp
    -g      : 디버그 정보 포함
    -Wall   : 모든 경고 표시
    -Wextra : 추가 경고 표시

  [Address Sanitizer (메모리 버그 검출)]
  g++ -std=c++17 -g -fsanitize=address -o 11_debug main.cpp
=============================================================================
*/
#include <iostream>
#include <string>
#include <vector>
#include <cassert>    // assert
#include <algorithm>
using namespace std;

void lesson1_common_bugs();
void lesson2_compiler_warnings();
void lesson3_assert_and_logging();
void lesson4_debugger_guide();
void lesson5_sanitizers();

int main() {
    cout << "========================================\n";
    cout << "  C++ 11단계 : 디버깅 가이드\n";
    cout << "========================================\n\n";

    lesson1_common_bugs();
    lesson2_compiler_warnings();
    lesson3_assert_and_logging();
    lesson4_debugger_guide();
    lesson5_sanitizers();

    cout << "\n11단계 학습 완료!\n";
    return 0;
}


// =====================================================================
// 레슨 1 — 흔한 버그 유형 TOP 10
// =====================================================================
void lesson1_common_bugs() {
    cout << "[레슨 1] 흔한 버그 TOP 10\n\n";

    /*
    ★ 버그 #1: 세미콜론 빠뜨림
    ─────────────────────────────
    int x = 5    // 여기 ; 빠짐!
    cout << x;
    → 에러 메시지가 아랫줄을 가리켜서 헷갈림

    ★ 버그 #2: = 와 == 혼동
    ─────────────────────────────
    if (x = 5)   // 대입!  항상 true!
    if (x == 5)  // 비교!  올바름!

    ★ 버그 #3: 배열 범위 초과
    ─────────────────────────────
    int arr[5];
    arr[5] = 10;  // 범위 밖! (0~4만 유효)
    → 컴파일 에러 안 남, 실행 시 크래시 또는 이상 동작

    ★ 버그 #4: 초기화 안 된 변수
    ─────────────────────────────
    int x;
    cout << x;   // 쓰레기 값!

    ★ 버그 #5: 정수 나눗셈
    ─────────────────────────────
    double result = 5 / 2;    // 2.0 (2.5가 아님!)
    double result = 5.0 / 2;  // 2.5 (올바름)

    ★ 버그 #6: 무한 루프
    ─────────────────────────────
    for (int i = 0; i < 10; ) {  // i++ 빠짐!
        // 영원히 반복
    }

    ★ 버그 #7: cin >> 후 getline 문제
    ─────────────────────────────
    cin >> number;
    getline(cin, name);  // 빈 줄이 읽힘!
    → cin.ignore() 필요

    ★ 버그 #8: 댕글링 포인터
    ─────────────────────────────
    int* p = new int(42);
    delete p;
    cout << *p;   // 이미 해제된 메모리!

    ★ 버그 #9: 메모리 누수
    ─────────────────────────────
    void func() {
        int* p = new int(42);
        return;  // delete 안 함!
    }

    ★ 버그 #10: 스위치 break 빠뜨림
    ─────────────────────────────
    switch (x) {
        case 1: do_a();  // break 없음!
        case 2: do_b();  // case 1일 때도 실행됨!
    }
    */

    // 실제 코드로 버그와 수정 예시
    cout << "  --- 버그 예시: 정수 나눗셈 ---\n";
    int a = 5, b = 2;
    double wrong   = a / b;                       // 2.0 (틀림)
    double correct = static_cast<double>(a) / b;   // 2.5 (맞음)
    cout << "  틀림: 5/2 = " << wrong << "\n";
    cout << "  맞음: 5/2 = " << correct << "\n\n";

    // 초기화 안 된 변수 방지: 항상 초기값을 주자
    int x = 0;     // 좋음
    // int y;      // 위험!

    cout << "  --- 버그 예시: 배열 범위 ---\n";
    vector<int> v = {10, 20, 30};
    // v[5];            // 범위 초과 (감지 안 됨, 위험!)
    // v.at(5);         // 범위 초과 (out_of_range 예외 발생)
    try {
        cout << "  v.at(5) 시도... ";
        cout << v.at(5) << "\n";
    } catch (const out_of_range& e) {
        cout << "에러: " << e.what() << "\n";
    }

    cout << endl;
}


// =====================================================================
// 레슨 2 — 컴파일러 경고를 읽는 법
// =====================================================================
void lesson2_compiler_warnings() {
    cout << "[레슨 2] 컴파일러 경고 읽기\n\n";

    /*
    ★ 컴파일 옵션: 항상 -Wall -Wextra 를 켜자!

    ★ 자주 보는 에러 메시지 해석

    1) "expected ';'"
       → 세미콜론 빠뜨림, 보통 에러 위치의 윗줄을 확인

    2) "undeclared identifier 'xxx'"
       → xxx 변수/함수가 선언 안 됨
       → 오타? #include 빠뜨림? 선언 위치 확인

    3) "no matching function for call to 'xxx'"
       → 함수 매개변수 타입/개수가 안 맞음

    4) "cannot convert 'X' to 'Y'"
       → 타입 불일치, 캐스팅 필요

    5) "warning: unused variable 'x'"
       → 선언했는데 안 씀 (삭제하거나 사용)

    6) "warning: comparison between signed and unsigned"
       → int와 size_t 비교 (size_t 또는 캐스팅 사용)

    7) "segmentation fault (core dumped)"
       → 잘못된 메모리 접근 (nullptr, 범위 초과, 해제된 메모리)

    ★ 에러 읽기 요령
    1. 첫 번째 에러부터 고쳐라 (뒤의 에러는 앞 에러의 연쇄일 수 있음)
    2. 파일명과 줄 번호를 확인하라
    3. 에러 메시지를 구글에 검색하라
    4. "near '...'" 부분이 핵심 단서
    */

    cout << "  컴파일 시 항상 이 옵션을 사용하세요:\n";
    cout << "  g++ -std=c++17 -Wall -Wextra -g main.cpp\n\n";
    cout << "  -Wall    : 주요 경고 전부 표시\n";
    cout << "  -Wextra  : 추가 경고 표시\n";
    cout << "  -g       : 디버그 정보 포함\n";
    cout << "  -O2      : 최적화 (릴리스용)\n";
    cout << "  -pedantic: 엄격한 표준 준수\n";
    cout << endl;
}


// =====================================================================
// 레슨 3 — assert와 로그 디버깅
// =====================================================================

// 간단한 디버그 매크로
#ifdef DEBUG
    #define LOG(msg) cout << "[DEBUG] " << __FILE__ << ":" << __LINE__ << " " << msg << "\n"
#else
    #define LOG(msg)  // 릴리스 빌드에서는 아무것도 안 함
#endif

int safe_divide(int a, int b) {
    // assert: 조건이 false면 프로그램 중단 + 에러 메시지
    // 개발 중 "이 조건은 절대 거짓이면 안 된다"를 검증
    assert(b != 0 && "0으로 나눌 수 없습니다!");
    return a / b;
}

void lesson3_assert_and_logging() {
    cout << "[레슨 3] assert와 로그 디버깅\n\n";

    /*
    ★ assert(조건)
    - 조건이 false면 프로그램 즉시 중단 + 에러 위치 표시
    - #include <cassert>
    - 릴리스 빌드에서는 #define NDEBUG로 비활성화
    - "이것은 반드시 참이어야 한다"를 명시하는 용도

    ★ 로그 디버깅
    - cout으로 변수 값, 함수 진입/퇴장을 출력
    - 가장 원시적이지만 효과적인 방법
    - 릴리스에서 제거: #ifdef DEBUG ... #endif
    */

    cout << "  --- assert ---\n";
    int result = safe_divide(10, 2);
    cout << "  10 / 2 = " << result << "\n";
    // safe_divide(10, 0);  // ← 주석 해제하면 assert 발동!
    cout << "  (0으로 나누면 assert 발동 → 프로그램 중단)\n\n";

    // 로그 디버깅 예시
    cout << "  --- 로그 디버깅 패턴 ---\n";
    vector<int> data = {3, 1, 4, 1, 5};
    cout << "  정렬 전: ";
    for (int n : data) cout << n << " ";
    cout << "\n";

    sort(data.begin(), data.end());

    cout << "  정렬 후: ";
    for (int n : data) cout << n << " ";
    cout << "\n";

    /*
    ★ 실전 디버깅 절차
    1. 버그 재현: 버그가 발생하는 정확한 조건 확인
    2. 범위 좁히기: cout/LOG로 "여기까지 정상" 확인
    3. 변수 확인: 의심 가는 변수 값을 출력
    4. 이분법: 코드 중간에 출력문 넣고, 문제가 위인지 아래인지
    5. 수정 후 검증: 수정했으면 원래 실패하던 케이스로 재테스트
    */

    cout << endl;
}


// =====================================================================
// 레슨 4 — 디버거 사용법 (GDB / Visual Studio)
// =====================================================================
void lesson4_debugger_guide() {
    cout << "[레슨 4] 디버거 사용법\n\n";

    /*
    ═══════════════════════════════════════════
    GDB (Linux / MinGW)
    ═══════════════════════════════════════════

    1) 디버그 빌드
       g++ -g -std=c++17 -o myapp main.cpp

    2) GDB 시작
       gdb myapp

    3) 핵심 명령어
    ┌───────────────┬──────────────────────────────┐
    │ 명령          │ 설명                          │
    ├───────────────┼──────────────────────────────┤
    │ break main    │ main 함수에 중단점            │
    │ break 42      │ 42번째 줄에 중단점            │
    │ run           │ 프로그램 실행                 │
    │ next (n)      │ 다음 줄 (함수 안으로 안 들어감)│
    │ step (s)      │ 다음 줄 (함수 안으로 들어감)  │
    │ continue (c)  │ 다음 중단점까지 계속          │
    │ print x       │ 변수 x의 값 출력             │
    │ print *ptr    │ 포인터가 가리키는 값          │
    │ backtrace (bt)│ 함수 호출 스택 보기           │
    │ watch x       │ x가 바뀌면 멈춤              │
    │ quit (q)      │ GDB 종료                     │
    └───────────────┴──────────────────────────────┘

    예시 세션:
    $ gdb ./myapp
    (gdb) break main
    (gdb) run
    (gdb) next
    (gdb) print x
    (gdb) continue


    ═══════════════════════════════════════════
    Visual Studio  (Windows)
    ═══════════════════════════════════════════

    1) 중단점(Breakpoint) 설정
       → 줄 번호 왼쪽 클릭 (빨간 점 생김)
       또는 F9

    2) 디버그 실행
       → F5 (디버깅 시작)
       → F10 (한 줄 실행, Step Over)
       → F11 (함수 안으로, Step Into)
       → Shift+F5 (중단)

    3) 변수 확인
       → 변수 위에 마우스 올리면 값 표시
       → 조사식(Watch) 창에 변수명 입력
       → 로컬(Locals) 창에서 모든 지역 변수 확인

    4) 호출 스택 확인
       → 호출 스택(Call Stack) 창


    ═══════════════════════════════════════════
    VS Code + C/C++ 확장
    ═══════════════════════════════════════════

    1) .vscode/launch.json 설정
    2) 줄 번호 왼쪽 클릭으로 중단점
    3) F5로 디버그 시작
    4) 변수, 호출 스택, 조사식 패널 활용
    */

    cout << "  디버거 핵심 기능 3가지:\n";
    cout << "  1. 중단점(Breakpoint) : 원하는 줄에서 멈추기\n";
    cout << "  2. 한 줄씩 실행(Step) : 코드 흐름 추적\n";
    cout << "  3. 변수 조사(Watch)   : 변수 값 실시간 확인\n\n";

    cout << "  이 3가지만 알면 대부분의 버그를 잡을 수 있습니다!\n";
    cout << endl;
}


// =====================================================================
// 레슨 5 — Sanitizers (메모리 버그 자동 검출)
// =====================================================================
void lesson5_sanitizers() {
    cout << "[레슨 5] Sanitizers\n\n";

    /*
    ★ Sanitizer = 실행 시 메모리 에러를 자동 검출하는 도구

    컴파일 옵션으로 활성화:
    g++ -fsanitize=address  -g main.cpp   # AddressSanitizer (ASan)
    g++ -fsanitize=undefined -g main.cpp  # UndefinedBehaviorSan (UBSan)
    g++ -fsanitize=thread   -g main.cpp   # ThreadSanitizer (TSan)

    ★ ASan이 잡아주는 것
    - 배열 범위 초과 (buffer overflow)
    - 해제 후 사용 (use-after-free)
    - 메모리 누수 (memory leak)
    - 이중 해제 (double-free)

    ★ UBSan이 잡아주는 것
    - 정수 오버플로우
    - nullptr 역참조
    - 0으로 나누기

    ★ 사용법
    1. 위 옵션으로 컴파일
    2. 평소처럼 실행
    3. 에러가 있으면 상세한 리포트 출력됨

    ★ Valgrind (Linux)
    $ valgrind --leak-check=full ./myapp
    → 메모리 누수 상세 보고
    → Windows에서는 Visual Studio의 진단 도구 사용
    */

    cout << "  메모리 버그 검출 도구:\n\n";
    cout << "  1. ASan (AddressSanitizer)\n";
    cout << "     g++ -fsanitize=address -g main.cpp\n";
    cout << "     → 범위 초과, use-after-free, 메모리 누수\n\n";
    cout << "  2. UBSan (UndefinedBehaviorSanitizer)\n";
    cout << "     g++ -fsanitize=undefined -g main.cpp\n";
    cout << "     → 정수 오버플로우, 0 나누기\n\n";
    cout << "  3. Valgrind (Linux)\n";
    cout << "     valgrind --leak-check=full ./myapp\n\n";
    cout << "  4. Visual Studio 진단 도구 (Windows)\n";
    cout << "     디버그 > 성능 프로파일러\n";

    cout << endl;
}
