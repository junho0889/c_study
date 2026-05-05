/*
=============================================================================
  C++ 학습 04단계: 배열, 포인터, 참조
=============================================================================
  [컴파일] g++ -std=c++17 -o 04_ptr main.cpp
  [주석 표기] // > 출력  // → 변수값  // ▶ 흐름

  ※ 출력 중 주소(0x...)는 실행마다 / 시스템마다 다릅니다.
    아래 주석의 주소는 64-bit Linux 예시. Windows/스택 위치 다름.
=============================================================================
*/
#include <iostream>
#include <string>
#include <cstring>
using namespace std;

void lesson1_arrays();
void lesson2_pointers();
void lesson3_pointer_and_array();
void lesson4_references();
void lesson5_strings();
void lesson6_dynamic_array();

int main() {
    cout << "========================================\n";
    cout << "  C++ 04단계 : 배열, 포인터, 참조\n";
    cout << "========================================\n\n";

    lesson1_arrays();
    lesson2_pointers();
    lesson3_pointer_and_array();
    lesson4_references();
    lesson5_strings();
    lesson6_dynamic_array();

    cout << "\n04단계 학습 완료!\n";
    return 0;
}


// =====================================================================
// 레슨 1 — 배열
// =====================================================================
void lesson1_arrays() {
    cout << "[레슨 1] 배열\n\n";

    int scores[5] = {95, 82, 71, 88, 63};
    // → 메모리: [95][82][71][88][63] (int 4바이트 × 5 = 20바이트 연속)

    cout << "  --- 배열 기본 ---\n";
    cout << "  scores[0] = " << scores[0] << "  (첫 번째)\n";
    // > 출력:   scores[0] = 95  (첫 번째)
    cout << "  scores[4] = " << scores[4] << "  (마지막)\n";
    // > 출력:   scores[4] = 63  (마지막)

    int size = sizeof(scores) / sizeof(scores[0]);
    // → sizeof(scores) = 20 (5×4)
    // → sizeof(scores[0]) = 4
    // → size = 5
    cout << "  배열 크기  = " << size << "\n\n";
    // > 출력:   배열 크기  = 5

    cout << "  전체 출력: ";
    for (int i = 0; i < size; i++) {
        // i: 0, 1, 2, 3, 4
        cout << scores[i] << " ";
    }
    cout << "\n";
    // > 출력:   전체 출력: 95 82 71 88 63

    cout << "  범위 기반 : ";
    for (int s : scores) {
        // s: 95, 82, 71, 88, 63 (값 복사)
        cout << s << " ";
    }
    cout << "\n";
    // > 출력:   범위 기반 : 95 82 71 88 63

    int sum = 0;
    for (int s : scores) sum += s;
    // 누적: 0+95=95 → +82=177 → +71=248 → +88=336 → +63=399
    // → sum = 399
    cout << "  합계=" << sum << "  평균=" << (sum / size) << "\n";
    // → 399 / 5 = 79 (정수 나눗셈)
    // > 출력:   합계=399  평균=79

    // 2차원 배열
    cout << "\n  --- 2차원 배열 ---\n";
    int matrix[2][3] = {
        {1, 2, 3},
        {4, 5, 6}
    };
    // 메모리 (row-major): [1][2][3][4][5][6]
    for (int row = 0; row < 2; row++) {
        cout << "  ";
        for (int col = 0; col < 3; col++) {
            // (0,0)=1 (0,1)=2 (0,2)=3
            // (1,0)=4 (1,1)=5 (1,2)=6
            cout << matrix[row][col] << " ";
        }
        cout << "\n";
    }
    // > 출력:
    //   1 2 3
    //   4 5 6
    cout << endl;
}


// =====================================================================
// 레슨 2 — 포인터
// =====================================================================
void lesson2_pointers() {
    cout << "[레슨 2] 포인터\n\n";

    int x = 42;
    int* ptr = &x;
    // → x = 42, 메모리 어딘가 (예: 0x7ffd1234) 에 위치
    // → ptr = 0x7ffd1234 (x의 주소)

    cout << "  --- 포인터 기본 ---\n";
    cout << "  x의 값      = " << x << "\n";
    // > 출력:   x의 값      = 42
    cout << "  x의 주소 (&x)  = " << &x << "\n";
    // > 출력 예:   x의 주소 (&x)  = 0x7ffd1234abcd
    //   ※ 실제 주소는 실행마다 다름. ASLR(주소 무작위화) 때문.
    cout << "  ptr의 값     = " << ptr << "  (x의 주소와 같음)\n";
    // > 출력 예:   ptr의 값     = 0x7ffd1234abcd  (x의 주소와 같음)
    cout << "  *ptr (역참조) = " << *ptr << "  (x의 값과 같음)\n\n";
    // > 출력:   *ptr (역참조) = 42  (x의 값과 같음)

    *ptr = 100;
    // → 0x7ffd1234abcd 주소의 값을 100으로 변경 = x = 100

    cout << "  *ptr = 100 실행 후\n";
    cout << "  x = " << x << "  (원본도 바뀜!)\n\n";
    // > 출력:   x = 100  (원본도 바뀜!)

    int* null_ptr = nullptr;
    // → null_ptr = 0 (nullptr은 주소 0)
    cout << "  nullptr = " << null_ptr << "  (아무것도 안 가리킴)\n";
    // > 출력:   nullptr = 0  (아무것도 안 가리킴)
    cout << endl;
}


// =====================================================================
// 레슨 3 — 포인터와 배열의 관계
// =====================================================================
void lesson3_pointer_and_array() {
    cout << "[레슨 3] 포인터와 배열\n\n";

    int arr[] = {10, 20, 30, 40, 50};
    int* ptr = arr;
    // → arr 자체가 첫 요소 주소 (배열 → 포인터 decay)
    // → ptr 도 같은 주소
    // → 메모리: arr[0]=10 @ 0x1000
    //           arr[1]=20 @ 0x1004 (int 4바이트)
    //           arr[2]=30 @ 0x1008
    //           ...

    cout << "  --- 포인터로 배열 접근 ---\n";
    for (int i = 0; i < 5; i++) {
        // arr[i], *(ptr+i), *(arr+i) 모두 동일
        cout << "  arr[" << i << "]=" << arr[i]
             << "  *(ptr+" << i << ")=" << *(ptr + i)
             << "  *(arr+" << i << ")=" << *(arr + i) << "\n";
    }
    // > 출력:
    //   arr[0]=10  *(ptr+0)=10  *(arr+0)=10
    //   arr[1]=20  *(ptr+1)=20  *(arr+1)=20
    //   arr[2]=30  *(ptr+2)=30  *(arr+2)=30
    //   arr[3]=40  *(ptr+3)=40  *(arr+3)=40
    //   arr[4]=50  *(ptr+4)=50  *(arr+4)=50

    cout << "\n  포인터 이동으로 순회: ";
    int* p = arr;
    for (int i = 0; i < 5; i++) {
        // p++: int 4바이트씩 주소 증가
        // 출력: 10 → 20 → 30 → 40 → 50
        cout << *p << " ";
        p++;
    }
    cout << "\n";
    // > 출력:   포인터 이동으로 순회: 10 20 30 40 50
    cout << endl;
}


// =====================================================================
// 레슨 4 — 참조 (Reference)
// =====================================================================
void lesson4_references() {
    cout << "[레슨 4] 참조\n\n";

    int x = 42;
    int& ref = x;
    // → ref는 x의 또 다른 이름. 같은 메모리 주소.

    cout << "  x   = " << x << "\n";
    // > 출력:   x   = 42
    cout << "  ref = " << ref << "  (같은 값)\n";
    // > 출력:   ref = 42  (같은 값)
    cout << "  &x  = " << &x << "\n";
    // > 출력 예:   &x  = 0x7ffd...
    cout << "  &ref= " << &ref << "  (같은 주소!)\n\n";
    // > 출력 예:   &ref= 0x7ffd... (x와 동일)

    ref = 100;
    // → ref는 x의 별명이므로 x도 100이 됨
    cout << "  ref = 100 실행 후\n";
    cout << "  x = " << x << "  ref = " << ref << "\n";
    // > 출력:   x = 100  ref = 100
    cout << endl;
}


// =====================================================================
// 레슨 5 — 문자열 (C-string vs std::string)
// =====================================================================
void lesson5_strings() {
    cout << "[레슨 5] 문자열\n\n";

    // C 문자열
    cout << "  --- C 문자열 (참고) ---\n";
    char c_str[] = "Hello";
    // → 메모리: [H][e][l][l][o][\0] = 6바이트
    cout << "  c_str = " << c_str << "\n";
    // > 출력:   c_str = Hello
    cout << "  strlen = " << strlen(c_str) << "  (\\0 제외 길이)\n";
    // → strlen = 5 (\0 만나면 멈춤)
    // > 출력:   strlen = 5  (\0 제외 길이)
    cout << "  sizeof = " << sizeof(c_str) << "  (\\0 포함 크기)\n\n";
    // → sizeof = 6 (배열 전체 크기)
    // > 출력:   sizeof = 6  (\0 포함 크기)

    // std::string
    cout << "  --- std::string (추천) ---\n";
    string s1 = "Hello";
    string s2 = " World";

    cout << "  결합:  " << (s1 + s2) << "\n";
    // → "Hello" + " World" = "Hello World"
    // > 출력:   결합:  Hello World

    cout << "  길이:  " << s1.length() << "\n";
    // → s1.length() = 5
    // > 출력:   길이:  5

    cout << "  비교:  " << (s1 == "Hello") << "\n";
    // → true → 1
    // > 출력:   비교:  1

    cout << "  부분:  " << s1.substr(1, 3) << "\n";
    // → s1[1] 부터 3글자: 'e','l','l' = "ell"
    // > 출력:   부분:  ell

    cout << "  찾기:  " << s1.find("ll") << "\n";
    // → "ll"의 시작 위치 = index 2
    // > 출력:   찾기:  2

    cout << "  글자:  ";
    for (char c : s1) {
        // c: 'H', 'e', 'l', 'l', 'o'
        cout << c << " ";
    }
    cout << "\n";
    // > 출력:   글자:  H e l l o
    cout << endl;
}


// =====================================================================
// 레슨 6 — 동적 배열 (new / delete)
// =====================================================================
void lesson6_dynamic_array() {
    cout << "[레슨 6] 동적 배열 (new / delete)\n\n";

    int size = 5;

    int* arr = new int[size];
    // → 힙에 int×5 = 20바이트 할당. arr는 그 주소.
    // → 초기값은 미정 (new int[size]() 면 0으로 초기화)

    for (int i = 0; i < size; i++) {
        arr[i] = (i + 1) * 10;
        // i=0 → arr[0] = 10
        // i=1 → arr[1] = 20
        // i=2 → arr[2] = 30
        // i=3 → arr[3] = 40
        // i=4 → arr[4] = 50
    }

    cout << "  동적 배열: ";
    for (int i = 0; i < size; i++) {
        cout << arr[i] << " ";
    }
    cout << "\n";
    // > 출력:   동적 배열: 10 20 30 40 50

    delete[] arr;
    // → 힙 메모리 해제. arr 자체는 여전히 옛 주소를 갖고 있음(댕글링).
    arr = nullptr;
    // → 명시적 무효화. 실수로 *arr 해도 즉시 크래시(디버깅 쉬움).

    cout << "  delete[] 완료 (메모리 해제)\n";
    // > 출력:   delete[] 완료 (메모리 해제)

    cout << endl;
}
