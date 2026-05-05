/*
=============================================================================
  C++ 학습 09단계: 파일 입출력과 예외 처리
=============================================================================
  [컴파일] g++ -std=c++17 -o 09_file main.cpp
  [주석 표기] // > 출력  // → 변수값  // ▶ 흐름
=============================================================================
*/
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <stdexcept>
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

    ofstream outfile("test_output.txt");
    // → 작업 디렉토리에 새 파일 생성. 기존 내용은 덮어씀.

    if (!outfile.is_open()) {
        // ▶ 보통 권한 문제. 정상이면 false.
        cout << "  파일 열기 실패!\n";
        return;
    }

    outfile << "C++ 파일 출력 테스트" << endl;
    outfile << "이름: 홍길동" << endl;
    outfile << "나이: 25" << endl;
    // → test_output.txt 안에 위 3줄 기록

    for (int i = 1; i <= 5; i++) {
        // i: 1, 2, 3, 4, 5
        outfile << "라인 " << i << endl;
    }
    // → 추가로 "라인 1" ~ "라인 5" 5줄 기록
    // → 파일 총 8줄

    outfile.close();
    cout << "  test_output.txt 생성 완료\n";
    // > 출력:   test_output.txt 생성 완료

    ofstream appendfile("test_output.txt", ios::app);
    // → 추가 모드. 기존 내용 뒤에 이어쓰기.
    appendfile << "--- 추가된 내용 ---" << endl;
    appendfile.close();
    cout << "  추가 쓰기 완료\n";
    // > 출력:   추가 쓰기 완료
    // → 파일 최종 9줄
    cout << endl;
}


// =====================================================================
// 레슨 2 — 파일 읽기
// =====================================================================
void lesson2_file_read() {
    cout << "[레슨 2] 파일 읽기\n\n";

    ifstream infile("test_output.txt");

    if (!infile.is_open()) {
        cout << "  파일 열기 실패! (먼저 레슨1을 실행하세요)\n";
        return;
    }

    cout << "  --- 파일 내용 ---\n";
    string line;
    int line_num = 0;
    while (getline(infile, line)) {
        // 1회차: line = "C++ 파일 출력 테스트", line_num = 1
        // 2회차: line = "이름: 홍길동", line_num = 2
        // 3회차: line = "나이: 25", line_num = 3
        // 4회차: line = "라인 1", line_num = 4
        // 5회차: line = "라인 2", line_num = 5
        // 6회차: line = "라인 3", line_num = 6
        // 7회차: line = "라인 4", line_num = 7
        // 8회차: line = "라인 5", line_num = 8
        // 9회차: line = "--- 추가된 내용 ---", line_num = 9
        // EOF 만나면 getline이 false → 종료
        line_num++;
        cout << "  " << line_num << ": " << line << "\n";
    }
    // > 출력:
    //   1: C++ 파일 출력 테스트
    //   2: 이름: 홍길동
    //   3: 나이: 25
    //   4: 라인 1
    //   5: 라인 2
    //   6: 라인 3
    //   7: 라인 4
    //   8: 라인 5
    //   9: --- 추가된 내용 ---

    infile.close();
    cout << "  총 " << line_num << "줄 읽음\n";
    // > 출력:   총 9줄 읽음

    cout << "\n  --- stringstream ---\n";
    string data = "홍길동 25 90.5";
    istringstream iss(data);

    string name;
    int age;
    double score;
    iss >> name >> age >> score;
    // → 공백 단위 파싱:
    //   name = "홍길동"
    //   age = 25
    //   score = 90.5

    cout << "  파싱 결과: 이름=" << name
         << " 나이=" << age
         << " 점수=" << score << "\n";
    // > 출력:   파싱 결과: 이름=홍길동 나이=25 점수=90.5
    cout << endl;
}


// =====================================================================
// 레슨 3 — 예외 처리
// =====================================================================
void lesson3_exceptions() {
    cout << "[레슨 3] 예외 처리 (try / catch / throw)\n\n";

    cout << "  --- 기본 예외 처리 ---\n";
    try {
        int a = 10, b = 0;
        // → a=10, b=0
        if (b == 0) {
            // ▶ b==0 true → throw 실행 → catch로 점프
            throw runtime_error("0으로 나눌 수 없습니다!");
        }
        cout << a / b << "\n";   // 실행되지 않음
    }
    catch (const runtime_error& e) {
        // → e.what() = "0으로 나눌 수 없습니다!"
        cout << "  에러 잡음: " << e.what() << "\n";
        // > 출력:   에러 잡음: 0으로 나눌 수 없습니다!
    }

    cout << "\n  --- 여러 예외 타입 ---\n";
    try {
        vector<int> v = {1, 2, 3};
        cout << "  v.at(10) 시도...\n";
        // > 출력:   v.at(10) 시도...
        cout << v.at(10) << "\n";
        // ▶ at(10)은 size=3 초과 → out_of_range throw
    }
    catch (const out_of_range& e) {
        // → e.what() (구현마다 다름): 보통
        //   "vector::_M_range_check: __n (which is 10) >= this->size() (which is 3)"
        cout << "  범위 초과: " << e.what() << "\n";
        // > 출력 예:   범위 초과: vector::_M_range_check: __n (which is 10) >= this->size() (which is 3)
    }
    catch (const exception& e) {
        cout << "  기타 에러: " << e.what() << "\n";
    }

    cout << "\n  --- catch(...) ---\n";
    try {
        throw 42;
        // → int 자체를 throw. 표준 예외 아님.
    }
    catch (...) {
        // ▶ 모든 예외 잡음. 단, 무엇이었는지 알 수 없음.
        cout << "  알 수 없는 예외 발생!\n";
        // > 출력:   알 수 없는 예외 발생!
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
    // → owner_="홍길동", balance_=10000

    try {
        account.withdraw(3000);
        // → amount=3000, 잔액 10000 → 7000 → 출금 성공
        // > 출력:   3000원 출금 (잔액: 7000)

        account.withdraw(50000);
        // ▶ amount=50000 > balance_=7000 → InsufficientFundsError throw
    }
    catch (const InsufficientFundsError& e) {
        // → e.what()="잔액 부족", balance=7000, amount=50000
        cout << "  에러: " << e.what()
             << " (잔액:" << e.get_balance()
             << ", 요청:" << e.get_amount() << ")\n";
        // > 출력:   에러: 잔액 부족 (잔액:7000, 요청:50000)
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

    {
        ofstream file("students.csv");
        if (!file) {
            throw runtime_error("파일 생성 실패");
        }
        file << "이름,국어,영어,수학\n";
        file << "홍길동,90,85,92\n";
        file << "김철수,78,92,88\n";
        file << "이영희,95,88,76\n";
        // → students.csv 4줄 작성
        cout << "  students.csv 생성 완료\n";
        // > 출력:   students.csv 생성 완료
    }

    {
        ifstream file("students.csv");
        if (!file) {
            throw runtime_error("파일 읽기 실패");
        }

        string header;
        getline(file, header);
        // → header = "이름,국어,영어,수학"
        cout << "  헤더: " << header << "\n\n";
        // > 출력:   헤더: 이름,국어,영어,수학

        string line;
        while (getline(file, line)) {
            // 1회차: line = "홍길동,90,85,92"
            //   getline(iss, name, ',') → name="홍길동", iss 남은 부분: "90,85,92"
            //   iss >> kor → kor=90, iss 남은: ",85,92"
            //   iss >> comma → comma=',', iss 남은: "85,92"
            //   iss >> eng → eng=85, iss 남은: ",92"
            //   iss >> comma → comma=',', iss 남은: "92"
            //   iss >> math → math=92
            //   avg = (90+85+92)/3.0 = 89.0
            // 2회차: 김철수, 78, 92, 88, avg=86.0
            // 3회차: 이영희, 95, 88, 76, avg=86.333...
            istringstream iss(line);
            string name;
            int kor, eng, math;
            char comma;

            getline(iss, name, ',');
            iss >> kor >> comma >> eng >> comma >> math;

            double avg = (kor + eng + math) / 3.0;
            cout << "  " << name
                 << " | 국:" << kor
                 << " 영:" << eng
                 << " 수:" << math
                 << " | 평균: " << avg << "\n";
        }
        // > 출력:
        //   홍길동 | 국:90 영:85 수:92 | 평균: 89
        //   김철수 | 국:78 영:92 수:88 | 평균: 86
        //   이영희 | 국:95 영:88 수:76 | 평균: 86.3333
        //   ※ 기본 정밀도 6자리. 89.0은 "89"로 출력
    }

    cout << endl;
}
