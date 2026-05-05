// ============================================================================
// 22장: 문자열 처리 & 정규표현식 (String Processing & Regex)
// ============================================================================
// 컴파일: g++ -std=c++17 -o string_regex main.cpp
//
// ┌──────────────────────────────────────────────────────────────┐
// │  학습 로드맵                                                  │
// ├──────────────────────────────────────────────────────────────┤
// │  레슨 1: std::string 심화 (모든 주요 멤버 함수 + SSO)        │
// │  레슨 2: string_view (C++17) - 성능, dangling 주의           │
// │  레슨 3: 문자열 변환 (to_string, stoi, from_chars 등)        │
// │  레슨 4: std::regex 기초 (match, search, replace)            │
// │  레슨 5: 정규표현식 실전 (이메일, URL, 로그, 전화번호)        │
// │  레슨 6: 문자열 알고리즘 (KMP, 토크나이저, CSV 파서)          │
// │  레슨 7: std::format (C++20) 및 포맷팅 대안                  │
// └──────────────────────────────────────────────────────────────┘
// ============================================================================

#include <iostream>
#include <string>
#include <string_view>
#include <sstream>
#include <vector>
#include <regex>
#include <algorithm>
#include <charconv>
#include <array>
#include <map>
#include <iomanip>
#include <cstring>
#include <functional>

using namespace std;

// ============================================================================
// 레슨 1: std::string 심화
// ============================================================================
//  ┌──────────────────────────────────────┐
//  │ std::string 내부 구조                │
//  │  ┌──────────┐                        │
//  │  │ data_ptr ─┼──> [힙: "Hello..."]   │  ← 긴 문자열
//  │  │ size_    │                        │
//  │  │ capacity_│                        │
//  │  └──────────┘                        │
//  │                                      │
//  │ SSO (Small String Optimization):     │
//  │  ┌─────────────────────┐             │
//  │  │ [내부 버퍼: "Hi"]   │             │  ← 짧은 문자열 (15~22B)
//  │  │ (힙 할당 없음!)     │             │    힙 할당 없이 직접 저장
//  │  └─────────────────────┘             │
//  └──────────────────────────────────────┘
namespace lesson1 {

    // --- 1-1: 검색 함수들 ---
    void demo_search() {
        cout << "[검색 함수]\n";
        string text = "Hello, World! Hello, C++! Hello, Everyone!";

        // find / rfind: 앞/뒤에서 검색. 실패 시 string::npos 반환
        size_t p1 = text.find("Hello");          // 첫 번째: 0
        size_t p2 = text.find("Hello", p1 + 1);  // 두 번째: 14
        size_t p3 = text.rfind("Hello");          // 마지막: 26
        cout << "  find(\"Hello\") = " << p1 << ", 두번째 = " << p2 << ", rfind = " << p3 << "\n";

        // find_first_of / find_last_of: 문자 집합 중 하나가 나타나는 위치
        size_t p4 = text.find_first_of("!?.");
        size_t p5 = text.find_last_of("!?.");
        cout << "  find_first_of(\"!?.\") = " << p4 << ", find_last_of = " << p5 << "\n";

        // find_first_not_of: 해당 문자가 아닌 첫 위치
        string spaces = "   Hello   ";
        cout << "  find_first_not_of(' ') = " << spaces.find_first_not_of(' ') << "\n";

        // npos 체크
        if (text.find("Python") == string::npos) cout << "  \"Python\" 없음\n";
    }

    // --- 1-2: 수정 함수들 ---
    void demo_modify() {
        cout << "\n[수정 함수]\n";

        // substr: 부분 문자열 추출
        string path = "/home/user/file.txt";
        cout << "  파일명: " << path.substr(path.rfind('/') + 1) << "\n";

        // replace: 특정 범위를 다른 문자열로 교체
        string g = "Hello, World!";
        g.replace(7, 5, "C++");  // 위치 7부터 5글자 → "C++"
        cout << "  replace: " << g << "\n";

        // insert + erase
        string m = "HelloWorld";
        m.insert(5, ", ");       // 위치 5에 삽입
        cout << "  insert: " << m << "\n";
        string d = "Hello---World";
        d.erase(5, 3);           // 위치 5부터 3글자 삭제
        cout << "  erase: " << d << "\n";

        // compare: <0 (작음), 0 (같음), >0 (큼)
        cout << "  \"apple\".compare(\"banana\") = " << string("apple").compare("banana")
             << " (음수 = 더 작음)\n";
    }

    // --- 1-3: 유틸리티 함수 직접 구현 ---
    string replace_all(string s, const string& from, const string& to) {
        size_t pos = 0;
        while ((pos = s.find(from, pos)) != string::npos) {
            s.replace(pos, from.length(), to);
            pos += to.length();
        }
        return s;
    }

    string trim(const string& s) {
        size_t start = s.find_first_not_of(" \t\n\r");
        if (start == string::npos) return "";
        return s.substr(start, s.find_last_not_of(" \t\n\r") - start + 1);
    }

    string to_upper(string s) { transform(s.begin(), s.end(), s.begin(), ::toupper); return s; }
    string to_lower(string s) { transform(s.begin(), s.end(), s.begin(), ::tolower); return s; }

    bool starts_with(const string& s, const string& p) {
        return s.size() >= p.size() && s.compare(0, p.size(), p) == 0;
    }
    bool ends_with(const string& s, const string& sx) {
        return s.size() >= sx.size() && s.compare(s.size()-sx.size(), sx.size(), sx) == 0;
    }

    vector<string> split(const string& s, char delim) {
        vector<string> tokens;
        istringstream stream(s);
        string token;
        while (getline(stream, token, delim)) tokens.push_back(token);
        return tokens;
    }

    string join(const vector<string>& parts, const string& delim) {
        string r;
        for (size_t i = 0; i < parts.size(); ++i) { if (i) r += delim; r += parts[i]; }
        return r;
    }

    void run() {
        cout << "=== 레슨 1: std::string 심화 ===\n\n";
        demo_search();
        demo_modify();

        cout << "\n[유틸리티]\n";
        cout << "  replace_all(\"aabbcc\",\"bb\",\"XX\") = " << replace_all("aabbcc","bb","XX") << "\n";
        cout << "  trim(\"  hello  \") = \"" << trim("  hello  ") << "\"\n";
        cout << "  to_upper(\"hello\") = " << to_upper("hello") << "\n";
        cout << "  starts_with(\"hello world\",\"hello\") = " << (starts_with("hello world","hello")?"참":"거짓") << "\n";
        cout << "  ends_with(\"file.txt\",\".txt\") = " << (ends_with("file.txt",".txt")?"참":"거짓") << "\n";

        auto parts = split("사과,바나나,체리", ',');
        cout << "  split: "; for (auto& p : parts) cout << "[" << p << "] "; cout << "\n";
        cout << "  join: " << join(parts, " | ") << "\n\n";
    }
}

// ============================================================================
// 레슨 2: string_view (C++17)
// ============================================================================
//  ┌──────────────────────────────────────────┐
//  │ string_view = 포인터 + 길이 (메모리 비소유)│
//  │                                          │
//  │ std::string  "Hello, World!"  ← 소유     │
//  │     ▲                                    │
//  │     │ (포인터+길이만)                     │
//  │ string_view  [ptr, len=13]   ← 비소유    │
//  │                                          │
//  │ 장점: 복사 없이 substr(O(1)), 비교, 검색  │
//  │ 주의: 원본 소멸 → dangling 참조 위험!     │
//  │                                          │
//  │ *** 위험한 패턴 ***                       │
//  │ string_view bad() {                      │
//  │   string local = "hi";                   │
//  │   return local;  // local 소멸 → 위험!   │
//  │ }                                        │
//  └──────────────────────────────────────────┘
namespace lesson2 {

    // string_view를 매개변수로 → const string&, const char*, string_view 모두 수용
    size_t count_words(string_view sv) {
        if (sv.empty()) return 0;
        size_t count = 0; bool in = false;
        for (char c : sv) {
            if (c==' '||c=='\t'||c=='\n') in = false;
            else if (!in) { in = true; ++count; }
        }
        return count;
    }

    // substr이 O(1) - 복사 없이 포인터 조정만
    string_view get_extension(string_view path) {
        auto dot = path.rfind('.');
        return (dot == string_view::npos) ? "" : path.substr(dot);
    }

    string_view get_filename(string_view path) {
        auto slash = path.rfind('/');
        if (slash == string_view::npos) slash = path.rfind('\\');
        return (slash == string_view::npos) ? path : path.substr(slash + 1);
    }

    // split을 string_view로 구현 → 복사 제로
    vector<string_view> split_view(string_view sv, char delim) {
        vector<string_view> result;
        while (!sv.empty()) {
            auto pos = sv.find(delim);
            if (pos == string_view::npos) { result.push_back(sv); break; }
            result.push_back(sv.substr(0, pos));
            sv.remove_prefix(pos + 1);
        }
        return result;
    }

    void run() {
        cout << "=== 레슨 2: string_view (C++17) ===\n\n";

        // 안전한 사용 예시
        string_view lit = "문자열 리터럴은 항상 안전";  // 리터럴: 프로그램 수명
        string orig = "원본 문자열";
        string_view sv2 = orig;  // 스코프 내에서 안전
        cout << "  리터럴: " << lit << "\n";
        cout << "  원본 참조: " << sv2 << "\n";

        // remove_prefix / remove_suffix (원본 불변, 뷰만 조정)
        string_view sv3 = "  Hello, World!  ";
        sv3.remove_prefix(2); sv3.remove_suffix(2);
        cout << "  트리밍: \"" << sv3 << "\"\n";

        cout << "  단어수(\"Hello World C++\"): " << count_words("Hello World C++") << "\n";

        string_view path = "/home/user/document.pdf";
        cout << "  확장자: " << get_extension(path) << ", 파일명: " << get_filename(path) << "\n";

        string data = "key1:value1:key2:value2";
        auto parts = split_view(data, ':');
        cout << "  split_view: ";
        for (auto& p : parts) cout << "[" << p << "] ";
        cout << "\n\n";
    }
}

// ============================================================================
// 레슨 3: 문자열 변환
// ============================================================================
//  ┌────────────────┬────────────┬──────────┬────────────────┐
//  │ 방법           │ 방향       │ 안전성   │ 성능           │
//  ├────────────────┼────────────┼──────────┼────────────────┤
//  │ to_string      │ 숫자→문자열│ 안전     │ 보통           │
//  │ stoi/stod      │ 문자열→숫자│ 예외 가능│ 보통           │
//  │ stringstream   │ 양방향     │ 안전     │ 느림           │
//  │ from/to_chars  │ 양방향     │ 에러코드 │ 매우 빠름(C++17)│
//  └────────────────┴────────────┴──────────┴────────────────┘
namespace lesson3 {

    void demo_to_string() {
        cout << "[to_string]\n";
        cout << "  42 → \"" << to_string(42) << "\"\n";
        cout << "  3.14 → \"" << to_string(3.14) << "\"\n";
    }

    void demo_sto() {
        cout << "\n[stoi/stod 등]\n";
        cout << "  stoi(\"42\") = " << stoi("42") << "\n";
        cout << "  stod(\"3.14\") = " << stod("3.14") << "\n";

        // 두 번째 매개변수: 처리된 문자 수
        size_t pos;
        cout << "  stoi(\"42abc\") = " << stoi("42abc", &pos) << " (처리: " << pos << "글자)\n";

        // 세 번째 매개변수: 진법
        cout << "  stoi(\"FF\",16) = " << stoi("FF",nullptr,16) << "\n";
        cout << "  stoi(\"1010\",2) = " << stoi("1010",nullptr,2) << "\n";

        // 예외 처리
        try { stoi("not_number"); }
        catch (const invalid_argument& e) { cout << "  예외(invalid): " << e.what() << "\n"; }
        try { stoi("99999999999999999"); }
        catch (const out_of_range& e) { cout << "  예외(range): " << e.what() << "\n"; }
    }

    void demo_stringstream() {
        cout << "\n[stringstream]\n";
        ostringstream oss;
        oss << "좌표: (" << 10.5 << ", " << 20.3 << ")";
        cout << "  oss: " << oss.str() << "\n";

        istringstream iss("100 3.14 hello");
        int a; double b; string c;
        iss >> a >> b >> c;
        cout << "  iss: a=" << a << " b=" << b << " c=" << c << "\n";

        ostringstream fmt;
        fmt << fixed << setprecision(2) << "금액: " << 12345.678 << "원";
        cout << "  포맷: " << fmt.str() << "\n";
    }

    void demo_charconv() {
        cout << "\n[from_chars/to_chars (C++17)] - 로케일 독립, 메모리 할당 없음, 매우 빠름\n";
        // to_chars: 숫자 → 버퍼
        array<char, 32> buf{};
        auto [ptr, ec] = to_chars(buf.data(), buf.data() + buf.size(), 42);
        if (ec == errc{}) cout << "  to_chars(42) = \"" << string(buf.data(), ptr) << "\"\n";

        // from_chars: 문자열 → 숫자
        const char* s = "12345";
        int val = 0;
        from_chars(s, s + strlen(s), val);
        cout << "  from_chars(\"12345\") = " << val << "\n";

        const char* hs = "FF"; int hv = 0;
        from_chars(hs, hs + strlen(hs), hv, 16);
        cout << "  from_chars(\"FF\",16) = " << hv << "\n";
    }

    void run() {
        cout << "=== 레슨 3: 문자열 변환 ===\n\n";
        demo_to_string();
        demo_sto();
        demo_stringstream();
        demo_charconv();
        cout << "\n";
    }
}

// ============================================================================
// 레슨 4: std::regex 기초
// ============================================================================
//  ┌─────────┬──────────────────────────────┐
//  │ 패턴    │ 의미                          │
//  ├─────────┼──────────────────────────────┤
//  │ .       │ 임의 한 문자                  │
//  │ ^ / $   │ 시작 / 끝                     │
//  │ * + ?   │ 0+회, 1+회, 0~1회            │
//  │ {n,m}   │ n~m회                         │
//  │ [abc]   │ 문자 클래스                   │
//  │ \d \w \s│ 숫자, 단어문자, 공백          │
//  │ (...)   │ 캡처 그룹                     │
//  │ |       │ OR                            │
//  └─────────┴──────────────────────────────┘
//  주의: C++에서 \는 \\로 이스케이프. Raw 문자열 추천: R"(\d+)"
namespace lesson4 {

    void demo_match() {
        cout << "[regex_match: 전체 매치]\n";
        regex date_re(R"((\d{4})-(\d{2})-(\d{2}))");
        string good = "2026-04-06", bad = "26-4-6";
        cout << "  \"" << good << "\" 매치? " << (regex_match(good, date_re)?"예":"아니오") << "\n";
        cout << "  \"" << bad << "\" 매치? " << (regex_match(bad, date_re)?"예":"아니오") << "\n";

        // 캡처 그룹으로 부분 추출
        smatch m;
        if (regex_match(good, m, date_re))
            cout << "  년:" << m[1] << " 월:" << m[2] << " 일:" << m[3] << "\n";
    }

    void demo_search() {
        cout << "\n[regex_search: 부분 검색]\n";
        string text = "기온 23.5도, 내일 25.1도";
        regex num_re(R"(\d+\.?\d*)");
        smatch m;
        cout << "  원문: " << text << "\n  숫자: ";
        string::const_iterator it = text.cbegin();
        while (regex_search(it, text.cend(), m, num_re)) {
            cout << m[0] << " ";
            it = m.suffix().first;
        }
        cout << "\n";
    }

    void demo_replace() {
        cout << "\n[regex_replace: 패턴 치환]\n";
        // 전화번호 형식 통일
        string phones = "010-1234-5678, 01012345678, 010.1234.5678";
        regex ph_re(R"((\d{3})[-.]?(\d{4})[-.]?(\d{4}))");
        cout << "  원본: " << phones << "\n";
        cout << "  통일: " << regex_replace(phones, ph_re, "$1-$2-$3") << "\n";

        // HTML 태그 제거
        string html = "<h1>제목</h1><p>본문 <b>강조</b></p>";
        cout << "  HTML→텍스트: " << regex_replace(html, regex(R"(<[^>]+>)"), "") << "\n";

        // 연속 공백 정리
        string messy = "Hello    World     C++";
        cout << "  공백정리: \"" << regex_replace(messy, regex(R"(\s+)"), " ") << "\"\n";
    }

    void demo_iterator() {
        cout << "\n[sregex_iterator: 모든 매치 순회]\n";
        string code = "int x = 10; double y = 3.14; string name = \"hi\";";
        regex var_re(R"((\w+)\s+(\w+)\s*=)");
        cout << "  코드: " << code << "\n";
        for (auto it = sregex_iterator(code.begin(), code.end(), var_re);
             it != sregex_iterator(); ++it)
            cout << "  변수: 타입=" << (*it)[1] << " 이름=" << (*it)[2] << "\n";
    }

    void run() {
        cout << "=== 레슨 4: std::regex 기초 ===\n\n";
        demo_match(); demo_search(); demo_replace(); demo_iterator();
        cout << "\n";
    }
}

// ============================================================================
// 레슨 5: 정규표현식 실전
// ============================================================================
namespace lesson5 {

    // --- 5-1: 이메일 검증 ---
    //  구조: user@domain.tld  (간소화 패턴, 실제 RFC5322은 훨씬 복잡)
    bool is_valid_email(const string& e) {
        return regex_match(e, regex(R"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"));
    }

    // --- 5-2: URL 파싱 ---
    //  https://www.example.com:8080/path?query
    //  ^^^^^   ^^^^^^^^^^^^^^^ ^^^^ ^^^^ ^^^^^
    //  scheme    host         port path  query
    struct URLParts { string scheme, host, port, path, query; };
    URLParts parse_url(const string& url) {
        URLParts r;
        regex re(R"(^(https?):\/\/([^/:]+)(?::(\d+))?(\/[^?]*)?(?:\?(.*))?$)");
        smatch m;
        if (regex_match(url, m, re)) {
            r.scheme = m[1]; r.host = m[2];
            r.port = m[3].length() ? m[3].str() : "기본";
            r.path = m[4].length() ? m[4].str() : "/";
            r.query = m[5];
        }
        return r;
    }

    // --- 5-3: 로그 파싱 ---
    //  형식: [2026-04-06 10:30:45] [INFO] 메시지
    struct LogEntry { string timestamp, level, message; };
    vector<LogEntry> parse_log(const string& log) {
        vector<LogEntry> entries;
        regex re(R"(\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[(\w+)\] (.+))");
        for (auto it = sregex_iterator(log.begin(), log.end(), re);
             it != sregex_iterator(); ++it)
            entries.push_back({(*it)[1], (*it)[2], (*it)[3]});
        return entries;
    }

    // --- 5-4: 전화번호 추출 ---
    vector<string> extract_phones(const string& text) {
        vector<string> phones;
        regex re(R"(0\d{1,2}[-.\s]?\d{3,4}[-.\s]?\d{4})");
        for (auto it = sregex_iterator(text.begin(), text.end(), re);
             it != sregex_iterator(); ++it)
            phones.push_back(regex_replace((*it)[0].str(), regex(R"([.\s])"), "-"));
        return phones;
    }

    // --- 5-5: IP 주소 검증 ---
    bool is_valid_ipv4(const string& ip) {
        regex re(R"(^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$)");
        smatch m;
        if (!regex_match(ip, m, re)) return false;
        for (int i = 1; i <= 4; ++i)
            if (int o = stoi(m[i]); o < 0 || o > 255) return false;
        return true;
    }

    void run() {
        cout << "=== 레슨 5: 정규표현식 실전 ===\n\n";

        cout << "[이메일 검증]\n";
        for (auto& e : {"user@example.com", "invalid@", "test+tag@domain.co.kr", "good@mail.org"})
            cout << "  " << e << " → " << (is_valid_email(e)?"유효":"무효") << "\n";

        cout << "\n[URL 파싱]\n";
        auto u = parse_url("https://www.example.com:8080/api/data?key=val");
        cout << "  스킴:" << u.scheme << " 호스트:" << u.host << " 포트:" << u.port
             << " 경로:" << u.path << " 쿼리:" << u.query << "\n";

        cout << "\n[로그 파싱]\n";
        string log = "[2026-04-06 10:30:45] [INFO] 서버 시작\n"
                     "[2026-04-06 10:31:02] [WARNING] 메모리 높음\n"
                     "[2026-04-06 10:32:15] [ERROR] DB 연결 실패\n";
        for (auto& e : parse_log(log))
            cout << "  " << e.timestamp << " | " << e.level << " | " << e.message << "\n";

        cout << "\n[전화번호 추출]\n";
        for (auto& p : extract_phones("연락: 010-1234-5678, 02.345.6789, 031 987 6543"))
            cout << "  " << p << "\n";

        cout << "\n[IP 검증]\n";
        for (auto& ip : {"192.168.1.1", "256.1.2.3", "10.0.0.0", "1.2.3"})
            cout << "  " << ip << " → " << (is_valid_ipv4(ip)?"유효":"무효") << "\n";
        cout << "\n";
    }
}

// ============================================================================
// 레슨 6: 문자열 알고리즘
// ============================================================================
//  ┌───────────────────────────────────────────────────────┐
//  │ KMP 알고리즘: 실패 함수로 불필요한 비교를 건너뜀       │
//  │                                                       │
//  │ 텍스트:  A B C A B C A B D                            │
//  │ 패턴:    A B C A B D                                  │
//  │ 실패값: [0,0,0,1,2,0]  (접두사=접미사 최대 길이)      │
//  │                                                       │
//  │ 매치 실패 시 실패값만큼 건너뜀 → O(n+m)               │
//  └───────────────────────────────────────────────────────┘
namespace lesson6 {

    // --- 6-1: KMP ---
    vector<int> compute_failure(const string& pat) {
        int m = (int)pat.size();
        vector<int> fail(m, 0);
        int j = 0;
        for (int i = 1; i < m; ++i) {
            while (j > 0 && pat[i] != pat[j]) j = fail[j-1];
            if (pat[i] == pat[j]) ++j;
            fail[i] = j;
        }
        return fail;
    }

    vector<int> kmp_search(const string& text, const string& pat) {
        vector<int> result;
        if (pat.empty()) return result;
        auto fail = compute_failure(pat);
        int n = (int)text.size(), m = (int)pat.size(), j = 0;
        for (int i = 0; i < n; ++i) {
            while (j > 0 && text[i] != pat[j]) j = fail[j-1];
            if (text[i] == pat[j]) ++j;
            if (j == m) { result.push_back(i - m + 1); j = fail[j-1]; }
        }
        return result;
    }

    // --- 6-2: 고급 토크나이저 (따옴표 안 구분자 무시) ---
    class Tokenizer {
        string delims_;
        char quote_;
    public:
        Tokenizer(const string& d = " \t", char q = '"') : delims_(d), quote_(q) {}
        vector<string> tokenize(const string& text) const {
            vector<string> tokens;
            string cur;
            bool in_q = false;
            for (char c : text) {
                if (c == quote_) { in_q = !in_q; continue; }
                if (!in_q && delims_.find(c) != string::npos) {
                    if (!cur.empty()) { tokens.push_back(cur); cur.clear(); }
                } else cur += c;
            }
            if (!cur.empty()) tokens.push_back(cur);
            return tokens;
        }
    };

    // --- 6-3: CSV 파서 ---
    //  규칙: 쉼표 구분, 큰따옴표로 감싸면 쉼표 무시, ""는 " 이스케이프
    class CSVParser {
    public:
        using Row = vector<string>;
        vector<Row> parse(const string& csv) {
            vector<Row> table;
            istringstream stream(csv);
            string line;
            while (getline(stream, line))
                if (!line.empty()) table.push_back(parse_row(line));
            return table;
        }
    private:
        Row parse_row(const string& line) {
            Row fields;
            string field;
            bool in_q = false;
            for (size_t i = 0; i < line.size(); ++i) {
                char c = line[i];
                if (in_q) {
                    if (c == '"') {
                        if (i+1 < line.size() && line[i+1] == '"') { field += '"'; ++i; }
                        else in_q = false;
                    } else field += c;
                } else {
                    if (c == '"') in_q = true;
                    else if (c == ',') { fields.push_back(field); field.clear(); }
                    else field += c;
                }
            }
            fields.push_back(field);
            return fields;
        }
    };

    // --- 6-4: 간이 JSON 키-값 추출 ---
    map<string, string> extract_json_kv(const string& json) {
        map<string, string> result;
        regex re(R"("(\w+)"\s*:\s*(?:"([^"]*)"|([\d.]+)|(true|false|null)))");
        for (auto it = sregex_iterator(json.begin(), json.end(), re);
             it != sregex_iterator(); ++it) {
            string key = (*it)[1], val;
            if ((*it)[2].length()) val = (*it)[2];
            else if ((*it)[3].length()) val = (*it)[3];
            else if ((*it)[4].length()) val = (*it)[4];
            result[key] = val;
        }
        return result;
    }

    void run() {
        cout << "=== 레슨 6: 문자열 알고리즘 ===\n\n";

        // KMP
        string text = "ABCABCABD ABCABCABD", pat = "ABCABD";
        auto fail = compute_failure(pat);
        cout << "[KMP]\n  텍스트: " << text << "\n  패턴: " << pat << "\n  실패값: [";
        for (size_t i = 0; i < fail.size(); ++i) { if (i) cout << ","; cout << fail[i]; }
        cout << "]\n  매치 위치: ";
        for (auto p : kmp_search(text, pat)) cout << p << " ";
        cout << "\n";

        // 토크나이저
        cout << "\n[토크나이저 (따옴표 인식)]\n";
        Tokenizer tok(",", '"');
        for (auto& t : tok.tokenize(R"(apple,"hello, world",banana)"))
            cout << "  [" << t << "]\n";

        // CSV
        cout << "\n[CSV 파서]\n";
        CSVParser csv;
        auto table = csv.parse("이름,나이,도시\n홍길동,30,서울\n\"이, 철수\",35,대구\n");
        for (auto& row : table) {
            cout << "  ";
            for (size_t i = 0; i < row.size(); ++i) { if (i) cout << " | "; cout << row[i]; }
            cout << "\n";
        }

        // JSON
        cout << "\n[JSON 추출]\n";
        auto kv = extract_json_kv(R"({"name":"홍길동","age":30,"active":true})");
        for (auto& [k,v] : kv) cout << "  " << k << " = " << v << "\n";
        cout << "\n";
    }
}

// ============================================================================
// 레슨 7: std::format (C++20) 및 포맷팅 대안
// ============================================================================
//  C++20 std::format 참고:
//    format("이름: {}, 나이: {}", name, age)
//    format("{:.2f}", 3.14159)   → "3.14"
//    format("{:>10}", "hello")   → "     hello"
//    format("{:#x}", 255)        → "0xff"
//  C++17 이하에서는 아래 대안들을 사용합니다.
namespace lesson7 {

    // --- 7-1: snprintf 래핑 ---
    template<typename... Args>
    string safe_sprintf(const char* fmt, Args... args) {
        int sz = snprintf(nullptr, 0, fmt, args...);
        if (sz <= 0) return "";
        string r(sz, '\0');
        snprintf(&r[0], sz + 1, fmt, args...);
        return r;
    }

    // --- 7-2: 자체 format 함수 (가변 인자 템플릿) ---
    template<typename T>
    string to_fmt(const T& v) { ostringstream o; o << v; return o.str(); }

    string format_str(const string& fmt) { return fmt; }
    template<typename First, typename... Rest>
    string format_str(const string& fmt, const First& first, const Rest&... rest) {
        string r;
        for (size_t i = 0; i < fmt.size(); ++i) {
            if (fmt[i]=='{' && i+1<fmt.size() && fmt[i+1]=='}')
                return r + to_fmt(first) + format_str(fmt.substr(i+2), rest...);
            r += fmt[i];
        }
        return r;
    }

    // --- 7-3: 정렬/패딩 유틸리티 ---
    string pad_left(const string& s, size_t w, char p=' ') {
        return s.size()>=w ? s : string(w-s.size(),p)+s;
    }
    string pad_right(const string& s, size_t w, char p=' ') {
        return s.size()>=w ? s : s+string(w-s.size(),p);
    }
    string pad_center(const string& s, size_t w, char p=' ') {
        if (s.size()>=w) return s;
        size_t t=w-s.size(), l=t/2;
        return string(l,p)+s+string(t-l,p);
    }

    // --- 7-4: 테이블 포맷터 ---
    class TableFormatter {
        vector<string> headers_;
        vector<vector<string>> rows_;
    public:
        TableFormatter(const vector<string>& h) : headers_(h) {}
        void add_row(const vector<string>& r) { rows_.push_back(r); }

        string render() {
            // 열 너비 계산
            vector<size_t> widths(headers_.size(), 0);
            for (size_t i = 0; i < headers_.size(); ++i) widths[i] = headers_[i].size();
            for (auto& row : rows_)
                for (size_t i = 0; i < row.size() && i < widths.size(); ++i)
                    widths[i] = max(widths[i], row[i].size());

            ostringstream o;
            auto sep = [&]() {
                o << "  +";
                for (auto w : widths) o << string(w+2,'-') << "+";
                o << "\n";
            };
            auto print_row = [&](const vector<string>& row) {
                o << "  |";
                for (size_t i = 0; i < widths.size(); ++i) {
                    string c = (i<row.size()) ? row[i] : "";
                    o << " " << pad_right(c, widths[i]) << " |";
                }
                o << "\n";
            };
            sep(); print_row(headers_); sep();
            for (auto& row : rows_) print_row(row);
            sep();
            return o.str();
        }
    };

    void run() {
        cout << "=== 레슨 7: 포맷팅 ===\n\n";

        cout << "[safe_sprintf]\n";
        cout << "  " << safe_sprintf("이름: %s, 나이: %d, 점수: %.1f", "홍길동", 25, 98.5) << "\n";

        cout << "\n[format_str (자체 구현)]\n";
        cout << "  " << format_str("안녕, {}님! {}세 맞죠?", "홍길동", 25) << "\n";
        cout << "  " << format_str("{} + {} = {}", 10, 20, 30) << "\n";

        cout << "\n[정렬]\n";
        cout << "  pad_left(\"42\",8,'0'):  \"" << pad_left("42",8,'0') << "\"\n";
        cout << "  pad_right(\"hi\",8):     \"" << pad_right("hi",8) << "\"\n";
        cout << "  pad_center(\"OK\",10):   \"" << pad_center("OK",10) << "\"\n";

        cout << "\n[테이블]\n";
        TableFormatter tbl({"이름", "나이", "도시", "점수"});
        tbl.add_row({"홍길동", "30", "서울", "95.5"});
        tbl.add_row({"김영희", "25", "부산", "88.0"});
        tbl.add_row({"이철수", "35", "대구", "92.3"});
        cout << tbl.render();

        cout << "  [C++20 std::format 참고]\n";
        cout << "    format(\"{:.2f}\", 3.14159) → \"3.14\"\n";
        cout << "    format(\"{:>10}\", \"hello\") → \"     hello\"\n";
        cout << "    -std=c++20 플래그로 컴파일하세요.\n\n";
    }
}

// ============================================================================
// 연습 문제
// ============================================================================
//  [연습 1] string_view로 모음(a,e,i,o,u) 개수 세는 함수 작성
//  [연습 2] 정규표현식으로 주민등록번호(XXXXXX-XXXXXXX) 형식 검증
//  [연습 3] CSV 파서에 필드 앞뒤 공백 자동 제거 기능 추가
//  [연습 4] 문자열에서 가장 많이 등장하는 단어 찾기 (map 활용)
//  [연습 5] 간이 마크다운→HTML 변환기 (# 제목, **굵게**, *기울임*, `코드`)
//           힌트: regex_replace를 여러 번 적용
namespace exercises {
    // TODO: size_t count_vowels(string_view sv) { ... }
    // TODO: bool is_valid_ssn(const string& ssn) { ... }  // 900101-1234567
    // TODO: 트리밍 CSV 파서
    // TODO: string most_frequent_word(const string& text) { ... }
    // TODO: string markdown_to_html(const string& md) { ... }

    void run() {
        cout << "=== 연습 문제 (직접 풀어보세요!) ===\n";
        cout << "  위의 TODO를 구현하고 테스트해보세요.\n\n";
    }
}

// ============================================================================
/*
=============================================================================
  레슨별 run() 출력 흐름 가이드 (대략)
=============================================================================
  lesson1 (string 심화):
    "Hello, World!" → length=13
    substr(7, 5) → "World"
    find("World") → 7
    replace, append, insert 결과 출력

  lesson2 (string_view):
    원본 string에 대한 zero-copy view
    "Hello"의 일부분을 string_view로 잘라서 사용 (메모리 절약)

  lesson3 (regex):
    "+82-10-1234-5678" → 휴대폰 번호 패턴 매치
    이메일 추출: regex_search("Contact me@example.com", r) → match
    날짜 형식 검증: 2026-05-06 → valid

  lesson4 (KMP 알고리즘):
    텍스트 "ABABDABACDABABCABAB" 에서 "ABABCABAB" 찾기
    실패 함수 [0,0,1,2,0,...] 으로 O(n+m)에 매치

  lesson5 (토크나이저):
    "Hello world C++" → ["Hello", "world", "C++"]
    구분자 ',', ';', 공백 등 처리

  lesson6 (CSV 파서):
    parse("이름,나이,도시\n홍길동,30,서울\n\"이, 철수\",35,대구\n")
    → 3행, 따옴표 안 쉼표 정확히 처리

  lesson7 (JSON 파서):
    {"name":"hello", "value":42} → 키-값 추출
=============================================================================
*/

int main() {
    cout << "========================================================\n";
    cout << "  22장: 문자열 처리 & 정규표현식\n";
    cout << "========================================================\n\n";

    lesson1::run();   // string 심화
    lesson2::run();   // string_view
    lesson3::run();   // regex
    lesson4::run();   // KMP
    lesson5::run();   // 토크나이저
    lesson6::run();   // CSV 파서
    lesson7::run();   // JSON 파서
    exercises::run();

    cout << "========================================================\n";
    cout << "  학습 완료! 다음 단계:\n";
    cout << "  - C++20 Ranges와 문자열 처리 결합\n";
    cout << "  - ICU 라이브러리로 유니코드 완벽 지원\n";
    cout << "  - 실전 프로젝트에서 파서 구현 실습\n";
    cout << "========================================================\n";
    return 0;
}
