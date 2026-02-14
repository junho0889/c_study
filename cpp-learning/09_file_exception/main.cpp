/*
=============================================================================
  C++ 학습 09단계: 파일 입출력과 예외 처리
=============================================================================
  [학습 목표]
  1. 파일 읽기/쓰기를 할 수 있다 (ifstream, ofstream)
  2. 예외 처리(try/catch/throw)를 이해한다
  3. 사용자 정의 예외를 만들 수 있다
  4. 예외 안전성 개념을 안다

  [컴파일] g++ -std=c++17 -o 09_file main.cpp
=============================================================================
*/
#include <iostream>
#include <fstream>     // 파일 입출력
#include <sstream>     // 문자열 스트림
#include <string>
#include <vector>
#include <stdexcept>   // 표준 예외 클래스
using namespace std;

void lesson1_file_write();
void lesson2_file_read();
void lesson3_exceptions();
void lesson4_custom_exception();
void lesson5_practical();

int main() {
    cout << "========================================\n";
    cout << "  C++ 09단계 : 파일 IO & 예외 처리\n";
    cout << "========================================\n\n";

    lesson1_file_write();
    lesson2_file_read();
    lesson3_exceptions();
    lesson4_custom_exception();
    lesson5_practical();

    cout << "\n09단계 학습 완료!\n";
    return 0;
}


// =====================================================================
// 레슨 1 — 파일 쓰기
// =====================================================================
void lesson1_file_write() {
    cout << "[레슨 1] 파일 쓰기\n\n";

    /*
    ★ ofstream = 파일에 출력 (Output File Stream)
      → cout 대신 파일에 쓰는 것 (사용법이 cout과 동일!)

    모드:
      ios::out      쓰기 (기본, 기존 내용 덮어씀)
      ios::app      추가 (기존 내용 뒤에 이어씀)
      ios::binary   바이너리 모드
    */

    // 파일 쓰기
    ofstream outfile("test_output.txt");

    if (!outfile.is_open()) {
        cout << "  파일 열기 실패!\n";
        return;
    }

    // cout처럼 사용하면 됨!
    outfile << "C++ 파일 출력 테스트" << endl;
    outfile << "이름: 홍길동" << endl;
    outfile << "나이: 25" << endl;

    for (int i = 1; i <= 5; i++) {
        outfile << "라인 " << i << endl;
    }

    outfile.close();   // RAII라 안 닫아도 되지만, 명시적이 좋음
    cout << "  test_output.txt 생성 완료\n";

    // 추가 모드
    ofstream appendfile("test_output.txt", ios::app);
    appendfile << "--- 추가된 내용 ---" << endl;
    appendfile.close();
    cout << "  추가 쓰기 완료\n";
    cout << endl;
}


// =====================================================================
// 레슨 2 — 파일 읽기
// =====================================================================
void lesson2_file_read() {
    cout << "[레슨 2] 파일 읽기\n\n";

    /*
    ★ ifstream = 파일에서 입력 (Input File Stream)
      → cin 대신 파일에서 읽는 것

    읽기 방법:
      >> 연산자       : 공백 단위로 읽기
      getline(file, str) : 한 줄씩 읽기 (가장 많이 사용)
      file.get()      : 한 글자씩 읽기
    */

    ifstream infile("test_output.txt");

    if (!infile.is_open()) {
        cout << "  파일 열기 실패! (먼저 레슨1을 실행하세요)\n";
        return;
    }

    // 한 줄씩 읽기
    cout << "  --- 파일 내용 ---\n";
    string line;
    int line_num = 0;
    while (getline(infile, line)) {
        line_num++;
        cout << "  " << line_num << ": " << line << "\n";
    }

    infile.close();
    cout << "  총 " << line_num << "줄 읽음\n";

    // ── stringstream: 문자열을 스트림처럼 다루기 ──
    cout << "\n  --- stringstream ---\n";
    string data = "홍길동 25 90.5";
    istringstream iss(data);

    string name;
    int age;
    double score;
    iss >> name >> age >> score;

    cout << "  파싱 결과: 이름=" << name
         << " 나이=" << age
         << " 점수=" << score << "\n";
    cout << endl;
}


// =====================================================================
// 레슨 3 — 예외 처리
// =====================================================================
void lesson3_exceptions() {
    cout << "[레슨 3] 예외 처리 (try / catch / throw)\n\n";

    /*
    ★ 예외 = 실행 중 발생하는 에러 (0으로 나누기, 파일 없음 등)

    try {
        // 에러가 발생할 수 있는 코드
        throw 예외;    // 에러 발생시키기
    }
    catch (예외타입& e) {
        // 에러 처리
    }

    ★ 왜 예외를 쓸까?
    - if 에러 체크: 에러 처리 코드가 로직 사이에 섞여 지저분
    - 예외 처리: 정상 로직과 에러 처리를 깔끔하게 분리

    ★ 표준 예외 클래스 계층
    exception
    ├── runtime_error     (실행 중 에러)
    │   ├── overflow_error
    │   └── underflow_error
    ├── logic_error       (논리적 에러)
    │   ├── invalid_argument
    │   ├── out_of_range
    │   └── domain_error
    └── bad_alloc         (메모리 부족)
    */

    // 기본 try/catch
    cout << "  --- 기본 예외 처리 ---\n";
    try {
        int a = 10, b = 0;
        if (b == 0) {
            throw runtime_error("0으로 나눌 수 없습니다!");
        }
        cout << a / b << "\n";  // 실행 안 됨
    }
    catch (const runtime_error& e) {
        cout << "  에러 잡음: " << e.what() << "\n";
    }

    // 여러 타입의 예외 잡기
    cout << "\n  --- 여러 예외 타입 ---\n";
    try {
        vector<int> v = {1, 2, 3};
        cout << "  v.at(10) 시도...\n";
        cout << v.at(10) << "\n";     // out_of_range 발생!
    }
    catch (const out_of_range& e) {
        cout << "  범위 초과: " << e.what() << "\n";
    }
    catch (const exception& e) {      // 모든 표준 예외의 부모
        cout << "  기타 에러: " << e.what() << "\n";
    }

    // catch(...) = 모든 예외 잡기
    cout << "\n  --- catch(...) ---\n";
    try {
        throw 42;   // 정수도 throw 가능 (비추천)
    }
    catch (...) {    // 모든 것을 잡음
        cout << "  알 수 없는 예외 발생!\n";
    }

    cout << endl;
}


// =====================================================================
// 레슨 4 — 사용자 정의 예외
// =====================================================================
class InsufficientFundsError : public runtime_error {
    int balance_;
    int amount_;
public:
    InsufficientFundsError(int balance, int amount)
        : runtime_error("잔액 부족"),
          balance_(balance), amount_(amount) {}

    int get_balance() const { return balance_; }
    int get_amount() const { return amount_; }
};

class BankAccount {
    string owner_;
    int    balance_;
public:
    BankAccount(const string& owner, int balance)
        : owner_(owner), balance_(balance) {}

    void withdraw(int amount) {
        if (amount <= 0) {
            throw invalid_argument("출금액은 양수여야 합니다");
        }
        if (amount > balance_) {
            throw InsufficientFundsError(balance_, amount);
        }
        balance_ -= amount;
        cout << "  " << amount << "원 출금 (잔액: " << balance_ << ")\n";
    }
};

void lesson4_custom_exception() {
    cout << "[레슨 4] 사용자 정의 예외\n\n";

    BankAccount account("홍길동", 10000);

    try {
        account.withdraw(3000);   // 성공
        account.withdraw(50000);  // 잔액 부족!
    }
    catch (const InsufficientFundsError& e) {
        cout << "  에러: " << e.what()
             << " (잔액:" << e.get_balance()
             << ", 요청:" << e.get_amount() << ")\n";
    }
    catch (const exception& e) {
        cout << "  에러: " << e.what() << "\n";
    }

    cout << endl;
}


// =====================================================================
// 레슨 5 — 실전 종합 예제: CSV 파일 처리
// =====================================================================
void lesson5_practical() {
    cout << "[레슨 5] 실전: CSV 파일 처리\n\n";

    // CSV 파일 쓰기
    {
        ofstream file("students.csv");
        if (!file) {
            throw runtime_error("파일 생성 실패");
        }
        file << "이름,국어,영어,수학\n";
        file << "홍길동,90,85,92\n";
        file << "김철수,78,92,88\n";
        file << "이영희,95,88,76\n";
        cout << "  students.csv 생성 완료\n";
    }

    // CSV 파일 읽기 + 분석
    {
        ifstream file("students.csv");
        if (!file) {
            throw runtime_error("파일 읽기 실패");
        }

        string header;
        getline(file, header);  // 헤더 건너뛰기
        cout << "  헤더: " << header << "\n\n";

        string line;
        while (getline(file, line)) {
            istringstream iss(line);
            string name;
            int kor, eng, math;
            char comma;  // 쉼표 읽기용

            getline(iss, name, ',');  // 쉼표까지 읽기
            iss >> kor >> comma >> eng >> comma >> math;

            double avg = (kor + eng + math) / 3.0;
            cout << "  " << name
                 << " | 국:" << kor
                 << " 영:" << eng
                 << " 수:" << math
                 << " | 평균: " << avg << "\n";
        }
    }

    // 정리: 테스트 파일 삭제 (선택적)
    // remove("test_output.txt");
    // remove("students.csv");

    cout << endl;
}
