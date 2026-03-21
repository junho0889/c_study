/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  STL 학습 05단계: string, string_view, regex
  실행 방법: g++ -std=c++17 main.cpp -o main && ./main
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  std::string  = 글자를 담는 "고무줄 상자". 늘었다 줄었다 합니다.
  string_view  = 남의 string을 "구경만" 하는 창문. 복사 없이 빠릅니다.
  regex        = "패턴에 맞는 글자를 찾아줘!" 하는 규칙 돋보기.

  비유:
  - string     = 내 공책 (자유롭게 쓰고 지울 수 있음)
  - string_view = 친구 공책을 옆에서 보기만 (빠르지만 고칠 수 없음)
  - regex      = "전화번호처럼 생긴 글자를 찾아 줘" 같은 규칙표
===============================================================================
*/

#include <iostream>
#include <string>
#include <string_view>
#include <regex>
#include <vector>
#include <sstream>
using namespace std;

// ┌─────────────────────────────────────────────┐
// │  레슨 1: string 기본 메서드들                 │
// └─────────────────────────────────────────────┘
void lesson1_string_methods() {
    cout << "[레슨 1] string 기본 메서드" << endl;
    cout << endl;

    string greeting = "안녕하세요, 민수입니다!";

    // size() / length() — 글자 수 (바이트 수에 주의!)
    cout << "  문자열: " << greeting << endl;
    cout << "  바이트 크기: " << greeting.size() << endl;
    cout << "  비어있나? " << (greeting.empty() ? "예" : "아니오") << endl;
    cout << endl;

    // ═══════════════════════════════════════════
    // find() — 찾기
    // 비유: 문장에서 "민수"라는 단어가 어디에 있는지 찾는 것
    // ═══════════════════════════════════════════
    string sentence = "apple banana apple cherry apple";
    size_t pos = sentence.find("banana");
    if (pos != string::npos) {
        cout << "  'banana' 위치: " << pos << endl;
    }

    // rfind() — 뒤에서부터 찾기
    size_t last_apple = sentence.rfind("apple");
    cout << "  마지막 'apple' 위치: " << last_apple << endl;
    cout << endl;

    // ═══════════════════════════════════════════
    // substr() — 잘라내기
    // 비유: 긴 리본에서 원하는 부분만 가위로 자르는 것
    // ═══════════════════════════════════════════
    string full = "2024-03-15";
    string year  = full.substr(0, 4);   // 0번째부터 4글자
    string month = full.substr(5, 2);   // 5번째부터 2글자
    string day   = full.substr(8, 2);   // 8번째부터 2글자
    cout << "  년: " << year << ", 월: " << month << ", 일: " << day << endl;
    cout << endl;

    // ═══════════════════════════════════════════
    // replace() — 바꾸기
    // ═══════════════════════════════════════════
    string msg = "Hello World";
    msg.replace(6, 5, "C++");  // 6번째부터 5글자를 "C++"로
    cout << "  replace 결과: " << msg << endl;
    cout << endl;

    // ═══════════════════════════════════════════
    // insert(), erase(), append()
    // ═══════════════════════════════════════════
    string text = "I like C++";
    text.insert(7, "modern ");      // 7번째 위치에 삽입
    cout << "  insert: " << text << endl;

    text.erase(0, 2);               // 0번째부터 2글자 삭제
    cout << "  erase:  " << text << endl;

    text.append(" very much!");     // 끝에 추가 (+= 와 같음)
    cout << "  append: " << text << endl;
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 2: 문자열 분리 (split)                  │
// └─────────────────────────────────────────────┘
void lesson2_string_split() {
    cout << "[레슨 2] 문자열 분리 (split)" << endl;
    cout << endl;

    // C++에는 Python의 split()이 없으므로 직접 만들어야 합니다.
    // 비유: 기차 칸처럼 쉼표로 연결된 것을 칸별로 떼어내는 것.

    // 방법 1: stringstream으로 공백 기준 분리
    string words = "apple banana cherry date";
    istringstream iss(words);
    string word;
    cout << "  공백으로 분리:" << endl;
    while (iss >> word) {
        cout << "    - " << word << endl;
    }
    cout << endl;

    // 방법 2: getline으로 구분자 지정 분리
    string csv = "민수,85,수학,A";
    istringstream css(csv);
    string token;
    cout << "  쉼표로 분리:" << endl;
    while (getline(css, token, ',')) {
        cout << "    - " << token << endl;
    }
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 3: string_view — 복사 없는 구경         │
// └─────────────────────────────────────────────┘
void lesson3_string_view() {
    cout << "[레슨 3] string_view — 복사 없이 구경하기" << endl;
    cout << endl;

    /*
      string_view는 문자열의 "읽기 전용 창문"입니다.
      원본을 복사하지 않고 가리키기만 하므로 매우 빠릅니다.

      비유: 도서관에서 책을 빌려와서 복사하는 게 string이라면,
            도서관에서 책을 읽기만 하고 오는 게 string_view입니다.

      주의: 원본이 사라지면 string_view도 못 씁니다!
            (도서관이 문을 닫으면 책을 볼 수 없는 것처럼)
    */

    string original = "Hello, Modern C++ World!";
    string_view sv = original;  // 복사 없이 가리키기만

    // string_view의 substr은 또 다른 string_view를 만듭니다 (복사 없음!)
    string_view hello = sv.substr(0, 5);
    string_view world = sv.substr(19, 5);

    cout << "  원본:    " << sv << endl;
    cout << "  앞 5자:  " << hello << endl;
    cout << "  뒤 5자:  " << world << endl;
    cout << "  크기:    " << sv.size() << endl;
    cout << endl;

    // remove_prefix, remove_suffix — 앞뒤를 "가리는" 것 (삭제 아님!)
    string_view trimmed = sv;
    trimmed.remove_prefix(7);   // 앞 7글자 가림
    trimmed.remove_suffix(1);   // 뒤 1글자 가림 (!)
    cout << "  앞뒤 잘라본 결과: " << trimmed << endl;
    cout << "  원본은 변하지 않음: " << original << endl;
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 4: string_view를 함수에 쓰면 좋은 이유  │
// └─────────────────────────────────────────────┘
// string_view를 매개변수로 쓰면 string, const char*, string_view
// 모두 복사 없이 받을 수 있습니다!

void print_greeting(string_view name) {
    // name을 복사하지 않고 읽기만 합니다.
    cout << "  안녕하세요, " << name << "님!" << endl;
}

void lesson4_string_view_function() {
    cout << "[레슨 4] string_view를 함수 매개변수로" << endl;
    cout << endl;

    string str_name = "민수";
    const char* cstr_name = "지우";
    string_view sv_name = "서연";

    // 세 가지 타입 모두 복사 없이 전달!
    print_greeting(str_name);     // string → string_view (자동 변환)
    print_greeting(cstr_name);    // const char* → string_view (자동 변환)
    print_greeting(sv_name);      // string_view → string_view (그대로)
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 5: regex 기본 — 패턴 찾기               │
// └─────────────────────────────────────────────┘
void lesson5_regex_basic() {
    cout << "[레슨 5] regex 기본 — 패턴으로 찾기" << endl;
    cout << endl;

    /*
      regex는 "이런 모양의 글자를 찾아줘"라는 규칙입니다.

      자주 쓰는 패턴:
        \\d     = 숫자 하나 (0~9)
        \\d+    = 숫자 1개 이상
        \\w     = 글자 하나 (영문, 숫자, _)
        .       = 아무 글자 하나
        *       = 0번 이상 반복
        +       = 1번 이상 반복
        [a-z]   = 소문자 하나
        ^       = 문장 시작
        $       = 문장 끝

      비유: "숫자 3개 - 숫자 4개 - 숫자 4개" = 전화번호 패턴
    */

    // regex_match — 전체가 패턴에 맞는지 확인
    string phone1 = "010-1234-5678";
    string phone2 = "abc-defg-hijk";
    regex phone_pattern(R"(\d{3}-\d{4}-\d{4})");

    cout << "  '" << phone1 << "' 전화번호? "
         << (regex_match(phone1, phone_pattern) ? "예" : "아니오") << endl;
    cout << "  '" << phone2 << "' 전화번호? "
         << (regex_match(phone2, phone_pattern) ? "예" : "아니오") << endl;
    cout << endl;

    // regex_search — 문장 안에서 패턴 찾기
    string text = "민수의 전화번호는 010-9876-5432이고, 지우는 010-1111-2222입니다.";
    smatch match;
    string search_text = text;

    cout << "  문장에서 전화번호 찾기:" << endl;
    while (regex_search(search_text, match, phone_pattern)) {
        cout << "    발견: " << match[0] << endl;
        search_text = match.suffix();
    }
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 6: regex 치환과 그룹                    │
// └─────────────────────────────────────────────┘
void lesson6_regex_replace() {
    cout << "[레슨 6] regex 치환과 그룹 캡처" << endl;
    cout << endl;

    // regex_replace — 패턴에 맞는 부분을 바꾸기
    string text = "오늘은 2024-03-15이고, 내일은 2024-03-16입니다.";

    // 날짜를 "YYYY년 MM월 DD일" 형식으로 바꾸기
    // ()로 묶은 부분이 $1, $2, $3 으로 캡처됩니다.
    regex date_pattern(R"((\d{4})-(\d{2})-(\d{2}))");
    string result = regex_replace(text, date_pattern, "$1년 $2월 $3일");
    cout << "  원본: " << text << endl;
    cout << "  변환: " << result << endl;
    cout << endl;

    // 이메일 검증
    regex email_pattern(R"([\w.+-]+@[\w-]+\.[\w.]+)");
    vector<string> emails = {
        "minsu@school.com",
        "not-an-email",
        "jiwoo@test.co.kr",
        "@missing.com"
    };

    cout << "  이메일 검증:" << endl;
    for (const auto& email : emails) {
        bool valid = regex_match(email, email_pattern);
        cout << "    " << email << " → " << (valid ? "유효" : "무효") << endl;
    }
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 7: 숫자 ↔ 문자열 변환                   │
// └─────────────────────────────────────────────┘
void lesson7_conversion() {
    cout << "[레슨 7] 숫자 ↔ 문자열 변환" << endl;
    cout << endl;

    // 숫자 → 문자열: to_string()
    int score = 95;
    double pi = 3.14159;
    string score_str = to_string(score);
    string pi_str = to_string(pi);
    cout << "  to_string(95)    = \"" << score_str << "\"" << endl;
    cout << "  to_string(3.14)  = \"" << pi_str << "\"" << endl;
    cout << endl;

    // 문자열 → 숫자: stoi, stol, stof, stod
    string num_str = "42";
    string float_str = "3.14";
    int num = stoi(num_str);
    double fnum = stod(float_str);
    cout << "  stoi(\"42\")   = " << num << endl;
    cout << "  stod(\"3.14\") = " << fnum << endl;
    cout << endl;
}

int main() {
    cout << "============================================================" << endl;
    cout << "  STL 05단계 : string, string_view, regex" << endl;
    cout << "============================================================" << endl;
    cout << endl;

    lesson1_string_methods();
    lesson2_string_split();
    lesson3_string_view();
    lesson4_string_view_function();
    lesson5_regex_basic();
    lesson6_regex_replace();
    lesson7_conversion();

    return 0;
}
