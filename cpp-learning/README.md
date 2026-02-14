# C++ 프로그래밍 학습 가이드

초보자부터 전문가까지, 18단계로 배우는 C++ 프로그래밍 교재입니다.
모든 코드에 한글 주석, 비유, 그림, 실전 예제가 포함되어 있습니다.

## 커리큘럼

### 기초 (01~04)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 01 | 기초의 기초 | 변수, 자료형, 입출력, 연산자, 형변환, 수학함수 |
| 02 | 제어문 | if/else, switch, for, while, break/continue, 실전연습 |
| 03 | 함수 | 선언, 매개변수 전달방식, 오버로딩, 재귀, 람다 |
| 04 | 배열/포인터 | 배열, 포인터, 참조, C-string vs string, 동적배열 |

### 객체지향 (05~06)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 05 | OOP 기초 | 클래스, 생성자/소멸자, 접근제어, this, static, 연산자 오버로딩 |
| 06 | 상속/다형성 | 상속, virtual, 다형성, 추상클래스, 인터페이스 |

### 실전 도구 (07~10)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 07 | 템플릿/STL | 함수/클래스 템플릿, vector, map, set, sort, find, count |
| 08 | 메모리 관리 | 스택/힙, unique_ptr, shared_ptr, RAII, move semantics |
| 09 | 파일/예외 | 파일 읽기/쓰기, try/catch, 사용자정의 예외, CSV 처리 |
| 10 | 모던 C++ | optional, variant, 구조적바인딩, constexpr if, C++20 미리보기 |

### 도구와 환경 (11~12)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 11 | 디버깅 | 흔한 버그 TOP 10, GDB/VS 사용법, Sanitizer |
| 12 | 프레임워크 | CMake, 프로젝트 구조, 주요 라이브러리, 패키지 관리 |

### 심화 (13~15) - NEW
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 13 | 디자인 패턴 | 싱글톤, 팩토리, 옵저버, 전략, 빌더, RAII |
| 14 | 멀티스레딩 | thread, mutex, atomic, async/future, 병렬 처리 |
| 15 | 네트워크 | TCP/IP, 소켓, HTTP, 직렬화, REST API, 서버 아키텍처 |

### 배포와 실전 (16~18) - NEW
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 16 | 테스트/TDD | 미니 테스트 프레임워크 직접 구현, Google Test, TDD 사이클 |
| 17 | 빌드/배포 | CMake 심화, Docker, GitHub Actions CI/CD, 릴리스 체크리스트 |
| 18 | 실전 프로젝트 | TODO 앱 (모든 개념 종합: OOP, 파일IO, 이벤트, STL) |

## 빠른 시작

### 방법 1: 개별 파일 컴파일 (가장 간단)
```bash
cd 01_basics
g++ -std=c++17 -Wall -o 01_basics main.cpp
./01_basics
```

### 방법 2: CMake로 전체 빌드
```bash
mkdir build && cd build
cmake ..
cmake --build .
```

### 방법 3: Windows MSVC
```cmd
cd 01_basics
cl /EHsc /std:c++17 /W4 main.cpp
main.exe
```

### 14단계 (멀티스레딩) 컴파일
```bash
g++ -std=c++17 -Wall -pthread -o 14_thread 14_multithreading/main.cpp
```

## 학습 로드맵

```
[기초]   01 → 02 → 03 → 04
              ↓
[OOP]    05 → 06
              ↓
[실전]   07 → 08 → 09 → 10
              ↓
[도구]   11 → 12
              ↓
[심화]   13 → 14 → 15
              ↓
[배포]   16 → 17 → 18 (실전 프로젝트!)
```

## 학습 팁

- 코드를 직접 타이핑하세요 (복사 붙여넣기 X)
- 주석을 읽고 값을 바꿔가며 실험하세요
- 컴파일 에러가 나면 첫 번째 에러부터 해결하세요
- 모르는 에러 메시지는 그대로 검색하세요

## 필요 환경

- C++17 이상 지원 컴파일러
  - Windows: MinGW-w64 또는 Visual Studio 2019+
  - Linux: GCC 7+ 또는 Clang 5+
  - Mac: Xcode Command Line Tools
- (선택) CMake 3.16 이상
