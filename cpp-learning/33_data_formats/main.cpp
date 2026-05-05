/*
=============================================================================
  C++ 학습 33단계: 데이터 포맷 (CSV / JSON / YAML / INI / TOML)
=============================================================================
  [학습 목표]
  1. CSV(RFC 4180) 정확한 파싱 - 따옴표, 이스케이프, 멀티라인 처리
  2. JSON 미니 파서를 직접 구현 - 토큰화 → 재귀하강 파싱
  3. YAML이 왜 stdlib에 없는지 이해 / 외부 라이브러리 선택 기준
  4. INI / TOML 단순 설정 포맷 처리
  5. 각 포맷별 "메모리 관리" 함정과 해법 - string_view, mmap, 스트리밍

  [왜 이 챕터인가]
    실무 C++ 코드 절반 이상이 결국 "설정 파일 읽기 + 데이터 직렬화".
    잘못 구현하면:
      - string_view dangling → UB
      - 거대 파일 통째 로드 → OOM
      - 따옴표 안 쉼표 → 잘못된 파싱
      - 인코딩(UTF-8 BOM) → 첫 키가 미스매치
      - Windows CRLF vs Unix LF → "어제까지 됐는데" 버그
    이 챕터는 '교과서 코드'가 아니라 '실무에서 망할 수 있는 모든 케이스'를
    표면화시켜 보여주는 것이 목적입니다.

  [컴파일]
    g++ -std=c++17 -Wall -Wextra -O2 -o 33_data main.cpp
    cl /EHsc /std:c++17 /W4 main.cpp
=============================================================================
*/

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>
#include <map>
#include <unordered_map>
#include <variant>
#include <optional>
#include <memory>
#include <stdexcept>
#include <cctype>
#include <cstdint>
#include <algorithm>
#include <chrono>
using namespace std;

// 전방 선언
void lesson1_csv_rfc4180();
void lesson2_json_parser();
void lesson3_yaml_overview();
void lesson4_ini_toml();
void lesson5_memory_pitfalls();
void lesson6_practical_config_loader();

/*
=============================================================================
  레슨별 출력 흐름 가이드
=============================================================================
  lesson1 (CSV RFC 4180):
    입력 CSV (BOM 포함):
      "name,age,address\r\nHong, Gildong,30,..."
    파싱 결과 행 수: 4 (헤더 + 3행)
    행 0: [name, age, address]
    행 1: [Hong, Gildong, 30, Seoul] ※ 따옴표 없는 ',' 정확 처리
    행 2: [Lee "the legend" Cheolsu, 35, Daegu]
    행 3: [Park, 28, Multi\nline\naddress]
    "unterminated 따옴표" 입력 → throw "unterminated quoted field"
    Round-trip 검증 PASS, 스트리밍 처리 행: 4

  lesson2 (JSON 파서):
    파싱 후 root.is_object() = true
    name = "C++ Study"
    version = 33
    topics 길이 = 3 (csv, json, yaml)
    meta.active = 1 (true)
    meta.ref is null = 1
    DoS 테스트: [[[...]]] 1000겹 → "max depth exceeded" PASS

  lesson3 (YAML): 정적 다이어그램 출력. anchor 폭탄 경고

  lesson4 (INI):
    [database] host=localhost port=5432 user=admin user password=secret123
    [logging] level=info file=/var/log/app.log
    [features] enable_cache=true

  lesson5 (메모리 함정):
    안전한 view 데모, vector reserve 비교 (큰 차이)
    10만 push_back: reserve 없음 ~수ms / reserve(N) ~1ms 미만

  lesson6 (Config 로더):
    필수 키 검증 PASS
    덤프 시 password = **** (마스킹)
    threads = 8, port = 5432
=============================================================================
*/

int main() {
    cout << "================================================\n";
    cout << "  C++ 33단계 : 데이터 포맷 (CSV/JSON/YAML/...)\n";
    cout << "================================================\n\n";

    lesson1_csv_rfc4180();
    lesson2_json_parser();
    lesson3_yaml_overview();
    lesson4_ini_toml();
    lesson5_memory_pitfalls();
    lesson6_practical_config_loader();

    cout << "\n33단계 학습 완료!\n";
    return 0;
}


// =============================================================================
//  레슨 1 — CSV 정확한 파싱 (RFC 4180)
// =============================================================================
//
//  [흔한 오해]
//    "CSV는 split(',')만 하면 되는 거 아닌가?"
//    → 절대 아님. 실무에서 발생하는 케이스:
//
//      "이름,나이,주소"               ← 헤더
//      "홍길동,30,서울 강남구"        ← 정상
//      "이,철수,35,대구"              ← 이름에 쉼표! split하면 4컬럼
//      "\"이, 철수\",35,대구"          ← 따옴표로 감싸기 (RFC 4180)
//      "박영희,28,\"서울특별시\n강남구\"" ← 멀티라인 필드
//      "김\"\"민\"\"수,40,부산"        ← 따옴표 자체 표현 = "" (이중 따옴표)
//
//  [RFC 4180 핵심 규칙]
//    1) 필드는 쉼표로 구분
//    2) 레코드는 CRLF로 구분 (실무에선 LF도 허용해야 함)
//    3) 필드를 큰따옴표로 감쌀 수 있음
//    4) 큰따옴표 안에 쉼표/줄바꿈/큰따옴표 모두 가능
//    5) 큰따옴표 자체는 ""(이중 따옴표)로 표현
//    6) 헤더 라인은 선택적
//
//  [메모리 관리 핵심]
//    - 큰 CSV(GB급)를 string으로 통째 로드 = OOM 직행
//    - 한 줄씩 streaming하되, 멀티라인 필드 때문에 단순 getline()은 위험
//    - 결과 vector<vector<string>>도 GB가 될 수 있음 → 가능하면 콜백 방식
//    - string_view로 zero-copy 가능하지만, 원본 버퍼 수명 = 뷰 수명
// =============================================================================

class CsvParser {
public:
    using Row = vector<string>;

    // [핵심] 상태 기반 파서. split()으로는 절대 안 됨.
    // 입력: 전체 CSV 텍스트 (또는 청크). 출력: 행 목록.
    //
    // 메모리: 결과를 vector로 누적하므로 입력 크기에 비례. 큰 파일은
    // parse_streaming() 사용.
    static vector<Row> parse(const string& text) {
        vector<Row> rows;
        Row current_row;
        string field;
        bool in_quotes = false;
        size_t i = 0;
        const size_t n = text.size();

        // UTF-8 BOM 제거 (Windows Excel이 UTF-8 CSV 저장 시 EF BB BF 추가)
        if (n >= 3 &&
            (uint8_t)text[0] == 0xEF &&
            (uint8_t)text[1] == 0xBB &&
            (uint8_t)text[2] == 0xBF) {
            i = 3;  // BOM 스킵. 안 하면 첫 헤더 키가 "\xEFid"가 되어 매치 실패.
        }

        while (i < n) {
            char c = text[i];

            if (in_quotes) {
                if (c == '"') {
                    // 다음 문자가 또 ""이면 리터럴 따옴표, 아니면 종료
                    if (i + 1 < n && text[i + 1] == '"') {
                        field.push_back('"');
                        i += 2;
                        continue;
                    } else {
                        in_quotes = false;
                        ++i;
                        continue;
                    }
                } else {
                    // 따옴표 안에서는 줄바꿈도 그냥 데이터
                    field.push_back(c);
                    ++i;
                    continue;
                }
            }

            // 따옴표 밖
            if (c == '"') {
                in_quotes = true;
                ++i;
                continue;
            }
            if (c == ',') {
                current_row.push_back(std::move(field));
                field.clear();           // move 후 빈 상태 보장은 표준이 명시
                ++i;
                continue;
            }
            if (c == '\r') {
                // CRLF: \r은 무시, \n에서 행 종료
                ++i;
                continue;
            }
            if (c == '\n') {
                current_row.push_back(std::move(field));
                field.clear();
                rows.push_back(std::move(current_row));
                current_row.clear();
                ++i;
                continue;
            }
            field.push_back(c);
            ++i;
        }

        // 마지막 행이 개행 없이 끝나는 케이스
        if (!field.empty() || !current_row.empty()) {
            current_row.push_back(std::move(field));
            rows.push_back(std::move(current_row));
        }

        // 따옴표 짝이 안 맞으면? 실무 정책 선택:
        //   (a) throw - 엄격
        //   (b) 자동 닫음 - 관대 (Excel 동작)
        // 여기선 엄격하게.
        if (in_quotes) {
            throw runtime_error("CSV: unterminated quoted field");
        }

        return rows;
    }

    // [스트리밍 파서] 콜백 방식. 메모리 사용량 = 한 행 크기.
    // 거대 CSV 처리할 때 핵심. 결과를 누적 안 하고 즉시 처리.
    template<typename Callback>
    static void parse_streaming(istream& in, Callback on_row) {
        Row current_row;
        string field;
        bool in_quotes = false;
        bool first_char = true;
        char c;

        while (in.get(c)) {
            // BOM 제거 (첫 3바이트만)
            if (first_char) {
                first_char = false;
                if ((uint8_t)c == 0xEF) {
                    char b2, b3;
                    if (in.get(b2) && in.get(b3) &&
                        (uint8_t)b2 == 0xBB && (uint8_t)b3 == 0xBF) {
                        continue;  // BOM 통째 스킵
                    }
                    // BOM 아니면 어쩔 수 없이 데이터로 간주 (드문 케이스)
                    field.push_back(c);
                    field.push_back(b2);
                    field.push_back(b3);
                    continue;
                }
            }

            if (in_quotes) {
                if (c == '"') {
                    char next;
                    if (in.get(next)) {
                        if (next == '"') { field.push_back('"'); continue; }
                        in_quotes = false;
                        // next 문자는 다시 처리해야 함
                        in.unget();
                    } else {
                        in_quotes = false;
                    }
                } else {
                    field.push_back(c);
                }
                continue;
            }

            if (c == '"')      { in_quotes = true; continue; }
            if (c == ',')      { current_row.push_back(std::move(field));
                                 field.clear(); continue; }
            if (c == '\r')     { continue; }
            if (c == '\n') {
                current_row.push_back(std::move(field));
                field.clear();
                on_row(current_row);   // 콜백 즉시 호출 → 메모리 안 쌓임
                current_row.clear();
                continue;
            }
            field.push_back(c);
        }

        if (!field.empty() || !current_row.empty()) {
            current_row.push_back(std::move(field));
            on_row(current_row);
        }
    }

    // [Writer] 쓰기는 더 위험. 필드에 쉼표/따옴표/줄바꿈 있으면 따옴표 감싸고
    // 내부 따옴표는 ""로 escape 해야 함. 잊으면 다음에 읽을 때 깨짐.
    static string escape_field(const string& f) {
        bool need_quote = false;
        for (char c : f) {
            if (c == ',' || c == '"' || c == '\n' || c == '\r') {
                need_quote = true;
                break;
            }
        }
        if (!need_quote) return f;

        string out;
        out.reserve(f.size() + 2);     // 최소 따옴표 2개
        out.push_back('"');
        for (char c : f) {
            if (c == '"') out.push_back('"');  // 이중 따옴표 escape
            out.push_back(c);
        }
        out.push_back('"');
        return out;
    }

    static string write(const vector<Row>& rows, const string& sep = ",",
                        const string& line_end = "\r\n") {
        string out;
        // [성능] 사전 reserve로 재할당 방지
        size_t est = 0;
        for (auto& r : rows) for (auto& f : r) est += f.size() + 1;
        out.reserve(est + rows.size() * 2);

        for (auto& row : rows) {
            for (size_t i = 0; i < row.size(); ++i) {
                if (i) out += sep;
                out += escape_field(row[i]);
            }
            out += line_end;
        }
        return out;
    }
};

void lesson1_csv_rfc4180() {
    cout << "[레슨 1] CSV — RFC 4180 정확한 파싱\n\n";

    // 1) 함정이 있는 입력
    string input =
        "name,age,address\r\n"
        "\"Hong, Gildong\",30,\"Seoul\"\r\n"
        "\"Lee \"\"the legend\"\" Cheolsu\",35,Daegu\r\n"  // "" → " 리터럴
        "Park,28,\"Multi\nline\naddress\"\r\n";

    auto rows = CsvParser::parse(input);
    cout << "  파싱된 행 수: " << rows.size() << "\n";
    for (size_t r = 0; r < rows.size(); ++r) {
        cout << "  행 " << r << ": ";
        for (size_t c = 0; c < rows[r].size(); ++c) {
            cout << "[" << rows[r][c] << "] ";
        }
        cout << "\n";
    }

    // 2) 잘못된 입력 → 예외
    cout << "\n  [잘못된 입력 테스트]\n";
    try {
        CsvParser::parse("a,b,\"unterminated");
    } catch (exception& e) {
        cout << "  예상된 예외: " << e.what() << "\n";
    }

    // 3) Round-trip: parse → write → parse 가 idempotent여야 함
    cout << "\n  [Round-trip 검증]\n";
    auto written = CsvParser::write(rows);
    auto reparsed = CsvParser::parse(written);
    cout << "  원본 행=" << rows.size()
         << ", 재파싱 행=" << reparsed.size()
         << " → " << (rows == reparsed ? "PASS" : "FAIL") << "\n";

    // 4) 스트리밍 파서: 거대 파일 시뮬레이션
    cout << "\n  [스트리밍 파서]\n";
    istringstream big_input(input);
    int row_count = 0;
    CsvParser::parse_streaming(big_input, [&](const CsvParser::Row& r) {
        ++row_count;
        // 여기서 즉시 DB insert / 통계 누적 / 다음 단계로 흘려보냄
        // → 결과를 메모리에 쌓지 않음
        (void)r;
    });
    cout << "  스트리밍 처리된 행: " << row_count << "\n";

    cout << R"(
  ┌─ 메모리 관리 체크리스트 ─────────────────────────────┐
  │ ✓ 입력 파일 크기 무관하게 OOM 안 나는가? (스트리밍)   │
  │ ✓ string_view를 반환하지 않는가? (원본 수명 종속)     │
  │ ✓ 결과 vector<Row> 누적이 의도한 만큼인가?            │
  │ ✓ 따옴표 짝 안 맞을 때 반응이 명확한가? (throw vs 관용)│
  │ ✓ UTF-8 BOM이 헤더에 섞이지 않는가?                   │
  │ ✓ CRLF/LF/CR 모두 처리되는가? (Mac old, Win, Unix)    │
  │ ✓ 셀에 \0 (NUL) 들어와도 처리되는가? (string은 OK)    │
  │ ✓ 매우 긴 단일 필드(MB 단위)도 처리되는가?            │
  └───────────────────────────────────────────────────────┘
)";

    cout << endl;
}


// =============================================================================
//  레슨 2 — JSON 미니 파서 직접 구현
// =============================================================================
//
//  [왜 직접 구현?]
//    실무는 nlohmann/json (https://github.com/nlohmann/json) 또는
//    simdjson (https://simdjson.org) 사용.
//    그런데 직접 작성해보면:
//      - 파서가 메모리를 어떻게 쌓는지 보임
//      - 재귀 파서의 스택 폭주 위험을 체감
//      - DOM(전체 트리) vs SAX(이벤트) 트레이드오프 이해
//
//  [DOM vs SAX]
//    DOM (이 챕터에서 구현):  파싱 후 트리 객체 반환. 사용 편하지만 큰 파일에 OOM.
//    SAX:                      토큰 이벤트(start_object, key, value, end_object)만
//                              콜백. 메모리 일정. 단, 사용 코드는 상태머신 작성.
//
//  [재귀 깊이 위험]
//    `[[[[[[[...]]]]]]]` 깊이 백만 → 스택 오버플로우 = 크래시 / DoS 취약점.
//    프로덕션 파서는 깊이 제한 필수 (보통 256~1024).
// =============================================================================

// JSON 값 = std::variant로 표현. 재귀 컨테이너이므로 unique_ptr 래핑.
struct JsonValue;
using JsonObject = map<string, JsonValue>;       // 정렬된 key 보존
using JsonArray  = vector<JsonValue>;

struct JsonValue {
    // [메모리 주의] variant 자체 크기는 가장 큰 멤버 + 태그 = 최소 ~40바이트.
    // 단, JsonObject/JsonArray는 내부에 동적 할당 컨테이너 → 외부 버킷.
    // unique_ptr 사용 이유: 재귀 타입이므로 직접 포함은 incomplete type 에러.
    using Storage = variant<
        nullptr_t,
        bool,
        double,                      // JSON number는 IEEE 754 double로 통일
        string,
        unique_ptr<JsonArray>,
        unique_ptr<JsonObject>
    >;
    Storage v;

    JsonValue() : v(nullptr) {}
    explicit JsonValue(bool b) : v(b) {}
    explicit JsonValue(double d) : v(d) {}
    explicit JsonValue(string s) : v(std::move(s)) {}

    // 헬퍼
    bool is_null()   const { return holds_alternative<nullptr_t>(v); }
    bool is_bool()   const { return holds_alternative<bool>(v); }
    bool is_number() const { return holds_alternative<double>(v); }
    bool is_string() const { return holds_alternative<string>(v); }
    bool is_array()  const { return holds_alternative<unique_ptr<JsonArray>>(v); }
    bool is_object() const { return holds_alternative<unique_ptr<JsonObject>>(v); }

    const JsonObject& as_object() const {
        return *get<unique_ptr<JsonObject>>(v);
    }
    const JsonArray& as_array() const {
        return *get<unique_ptr<JsonArray>>(v);
    }
};

class JsonParser {
public:
    static constexpr int MAX_DEPTH = 256;  // DoS 방지

    static JsonValue parse(string_view text) {
        JsonParser p(text);
        p.skip_ws();
        auto v = p.parse_value(0);
        p.skip_ws();
        if (p.pos_ < p.text_.size()) {
            throw runtime_error("JSON: trailing garbage at pos " + to_string(p.pos_));
        }
        return v;
    }

private:
    string_view text_;
    size_t pos_ = 0;

    explicit JsonParser(string_view t) : text_(t) {}

    [[noreturn]] void fail(const string& msg) {
        throw runtime_error("JSON @" + to_string(pos_) + ": " + msg);
    }

    void skip_ws() {
        while (pos_ < text_.size()) {
            char c = text_[pos_];
            if (c == ' ' || c == '\t' || c == '\n' || c == '\r') ++pos_;
            else break;
        }
    }

    char peek() {
        if (pos_ >= text_.size()) fail("unexpected EOF");
        return text_[pos_];
    }

    JsonValue parse_value(int depth) {
        if (depth > MAX_DEPTH) fail("max depth exceeded (DoS guard)");
        skip_ws();
        char c = peek();
        if (c == '{') return parse_object(depth + 1);
        if (c == '[') return parse_array(depth + 1);
        if (c == '"') {
            JsonValue v;
            v.v = parse_string();
            return v;
        }
        if (c == 't' || c == 'f') return parse_bool();
        if (c == 'n') return parse_null();
        if (c == '-' || (c >= '0' && c <= '9')) return parse_number();
        fail("unexpected char");
    }

    JsonValue parse_object(int depth) {
        ++pos_;  // {
        auto obj = make_unique<JsonObject>();
        skip_ws();
        if (peek() == '}') { ++pos_; JsonValue v; v.v = std::move(obj); return v; }
        while (true) {
            skip_ws();
            if (peek() != '"') fail("expected string key");
            string key = parse_string();
            skip_ws();
            if (peek() != ':') fail("expected ':'");
            ++pos_;
            auto val = parse_value(depth);
            // [메모리 주의] key가 중복되면 어떻게? RFC 8259는 미정의.
            // 여기서는 마지막 값으로 덮어씀 (대부분 라이브러리 기본).
            (*obj)[std::move(key)] = std::move(val);
            skip_ws();
            char c = peek();
            if (c == ',') { ++pos_; continue; }
            if (c == '}') { ++pos_; break; }
            fail("expected ',' or '}'");
        }
        JsonValue v;
        v.v = std::move(obj);
        return v;
    }

    JsonValue parse_array(int depth) {
        ++pos_;  // [
        auto arr = make_unique<JsonArray>();
        skip_ws();
        if (peek() == ']') { ++pos_; JsonValue v; v.v = std::move(arr); return v; }
        while (true) {
            arr->push_back(parse_value(depth));
            skip_ws();
            char c = peek();
            if (c == ',') { ++pos_; continue; }
            if (c == ']') { ++pos_; break; }
            fail("expected ',' or ']'");
        }
        JsonValue v;
        v.v = std::move(arr);
        return v;
    }

    string parse_string() {
        if (peek() != '"') fail("expected '\"'");
        ++pos_;
        string out;
        while (pos_ < text_.size()) {
            char c = text_[pos_++];
            if (c == '"') return out;
            if (c == '\\') {
                if (pos_ >= text_.size()) fail("bad escape");
                char esc = text_[pos_++];
                switch (esc) {
                    case '"':  out.push_back('"'); break;
                    case '\\': out.push_back('\\'); break;
                    case '/':  out.push_back('/'); break;
                    case 'b':  out.push_back('\b'); break;
                    case 'f':  out.push_back('\f'); break;
                    case 'n':  out.push_back('\n'); break;
                    case 'r':  out.push_back('\r'); break;
                    case 't':  out.push_back('\t'); break;
                    case 'u': {
                        // \uXXXX → UTF-8 인코딩
                        // [주의] 서로게이트 페어(\uD800~\uDFFF)는 더 복잡.
                        // 실무 라이브러리는 다 처리. 여기선 BMP만 단순 변환.
                        if (pos_ + 4 > text_.size()) fail("bad \\u");
                        unsigned cp = 0;
                        for (int k = 0; k < 4; ++k) {
                            char h = text_[pos_++];
                            cp <<= 4;
                            if (h >= '0' && h <= '9') cp |= h - '0';
                            else if (h >= 'a' && h <= 'f') cp |= h - 'a' + 10;
                            else if (h >= 'A' && h <= 'F') cp |= h - 'A' + 10;
                            else fail("bad hex");
                        }
                        // UTF-8 인코딩
                        if (cp < 0x80) {
                            out.push_back((char)cp);
                        } else if (cp < 0x800) {
                            out.push_back((char)(0xC0 | (cp >> 6)));
                            out.push_back((char)(0x80 | (cp & 0x3F)));
                        } else {
                            out.push_back((char)(0xE0 | (cp >> 12)));
                            out.push_back((char)(0x80 | ((cp >> 6) & 0x3F)));
                            out.push_back((char)(0x80 | (cp & 0x3F)));
                        }
                        break;
                    }
                    default: fail("unknown escape");
                }
            } else {
                // [보안] 제어문자(0x00~0x1F)는 RFC상 불허 — 엄격 모드는 reject
                if ((uint8_t)c < 0x20) fail("control char in string");
                out.push_back(c);
            }
        }
        fail("unterminated string");
    }

    JsonValue parse_bool() {
        if (text_.substr(pos_, 4) == "true")  { pos_ += 4; JsonValue v; v.v = true; return v; }
        if (text_.substr(pos_, 5) == "false") { pos_ += 5; JsonValue v; v.v = false; return v; }
        fail("bad bool");
    }
    JsonValue parse_null() {
        if (text_.substr(pos_, 4) == "null") { pos_ += 4; return JsonValue{}; }
        fail("bad null");
    }
    JsonValue parse_number() {
        size_t start = pos_;
        if (text_[pos_] == '-') ++pos_;
        while (pos_ < text_.size() && (isdigit((uint8_t)text_[pos_]) ||
               text_[pos_] == '.' || text_[pos_] == 'e' || text_[pos_] == 'E' ||
               text_[pos_] == '+' || text_[pos_] == '-')) ++pos_;
        // [주의] strtod는 locale 의존. 한국어 로케일에서 ',' 소수점이면 망함.
        // 프로덕션은 std::from_chars (C++17) 사용 권장 - locale-independent.
        string num{text_.substr(start, pos_ - start)};
        try {
            JsonValue v;
            v.v = stod(num);
            return v;
        } catch (...) { fail("bad number"); }
    }
};

void lesson2_json_parser() {
    cout << "[레슨 2] JSON — 직접 파서 구현\n\n";

    string j = R"({
        "name": "C++ Study",
        "version": 33,
        "topics": ["csv", "json", "yaml"],
        "meta": { "lang": "ko", "year": 2026, "active": true, "ref": null },
        "unicode": "한글 é ñ"
    })";

    auto root = JsonParser::parse(j);
    cout << "  최상위 타입: " << (root.is_object() ? "object" : "?") << "\n";
    if (root.is_object()) {
        const auto& o = root.as_object();
        cout << "  name = " << get<string>(o.at("name").v) << "\n";
        cout << "  version = " << get<double>(o.at("version").v) << "\n";
        cout << "  topics 길이 = " << o.at("topics").as_array().size() << "\n";
        cout << "  meta.active = " << get<bool>(o.at("meta").as_object().at("active").v) << "\n";
        cout << "  meta.ref is null? " << o.at("meta").as_object().at("ref").is_null() << "\n";
        cout << "  unicode = " << get<string>(o.at("unicode").v) << "\n";
    }

    // DoS 방어 테스트: 깊이 제한
    cout << "\n  [DoS 가드]\n";
    string deep;
    for (int i = 0; i < 1000; ++i) deep += "[";
    for (int i = 0; i < 1000; ++i) deep += "]";
    try {
        JsonParser::parse(deep);
        cout << "  FAIL: 깊이 가드가 동작 안 함\n";
    } catch (exception& e) {
        cout << "  PASS: " << e.what() << "\n";
    }

    cout << R"(
  ┌─ JSON 메모리 함정 ────────────────────────────────────┐
  │ 1. 깊이 제한 없는 파서 → 스택오버플로우 / DoS         │
  │ 2. 큰 배열 → vector 재할당으로 메모리 단편화          │
  │ 3. 키 중복 정책 미정의 → 마지막 값? 첫 값? throw?     │
  │ 4. \uXXXX 서로게이트 페어 미처리 → 깨진 UTF-8 출력    │
  │ 5. 1e308 같은 거대 수 / NaN/Infinity (RFC 불허)       │
  │ 6. variant<unique_ptr<...>> 재귀 타입 → heap 할당     │
  │ 7. simdjson 같은 SIMD 파서는 4-byte aligned 입력 요구 │
  │ 8. DOM 사용 시 deep copy 비용 (move 활용 필수)        │
  └───────────────────────────────────────────────────────┘

  [실무 권장]
    소형~중형(~수MB):  nlohmann/json (header-only, 사용성 최고)
    대용량/고성능:      simdjson (GB/s 처리, on-demand API로 메모리 절약)
    임베디드:          ArduinoJson (정적 메모리 풀)
    스트리밍:          rapidjson SAX API
)";

    cout << endl;
}


// =============================================================================
//  레슨 3 — YAML 개요와 라이브러리 선택
// =============================================================================
//
//  [왜 stdlib에 YAML이 없나]
//    YAML 1.2 명세는 200쪽 이상. JSON 슈퍼셋이지만 다음 기능 때문에 복잡:
//      - 들여쓰기 문법 (탭? 공백? 혼합?)
//      - Anchor/Alias (&a, *a) — 그래프 표현 가능 (사이클!)
//      - Tag (!!str, !custom) — 사용자 타입
//      - Flow vs Block 스타일
//      - Plain scalar 자동 타입 추론 ("yes" → bool? 문자열?)
//    그래서 직접 구현은 비추천. 검증된 라이브러리 사용.
//
//  [라이브러리 비교]
//    yaml-cpp        : 가장 유명. C++17 OK. CMake find_package 잘 됨.
//                      컴파일 시간 김, 메모리 사용 큼.
//    rapidyaml (ryml): SAX/DOM 둘 다, 빠름. 런타임 할당 없는 in-place 파싱.
//                      문서 적음. 임베디드 적합.
//    fkYAML          : 헤더-온리 C++17. 사용 쉽지만 큰 파일은 느림.
//
//  [YAML의 위험: Anchor 폭탄]
//    a: &x [1, 1, 1, 1, 1, 1, 1, 1, 1]
//    b: &y [*x, *x, *x, *x, *x, *x, *x, *x, *x]
//    c: &z [*y, *y, *y, *y, *y, *y, *y, *y, *y]
//    ...
//    → 노드 수가 9^N으로 폭증. "Billion Laughs" 공격. 신뢰 없는 입력은 위험.
// =============================================================================

void lesson3_yaml_overview() {
    cout << "[레슨 3] YAML — 개요와 라이브러리 선택\n\n";

    cout << R"(
  ┌─ YAML 핵심 문법 ──────────────────────────────────────┐
  │ # 주석                                                │
  │ name: study             # 문자열 (따옴표 선택)          │
  │ version: 33             # 정수 (자동 추론)            │
  │ active: true            # bool                        │
  │ tags:                   # 배열 (Block 스타일)         │
  │   - cpp                                               │
  │   - learning                                          │
  │ meta:                   # 중첩 객체                   │
  │   lang: ko                                            │
  │   year: 2026                                          │
  │ inline_array: [a, b, c] # Flow 스타일                 │
  │ multiline: |            # 리터럴 (개행 보존)          │
  │   line1                                               │
  │   line2                                               │
  │ folded: >               # 폴딩 (개행 → 공백)          │
  │   long sentence split                                 │
  │   over many lines                                     │
  │ anchor: &shared_ref                                   │
  │   key: value                                          │
  │ ref_alias: *shared_ref  # 같은 객체 참조              │
  └───────────────────────────────────────────────────────┘

  [yaml-cpp 사용 예시 - 의사코드]
  ─────────────────────────────────────────
  #include <yaml-cpp/yaml.h>
  YAML::Node config = YAML::LoadFile("config.yaml");
  std::string name = config["name"].as<std::string>();
  int version = config["version"].as<int>();
  for (const auto& tag : config["tags"]) {
      std::cout << tag.as<std::string>() << "\n";
  }
  // 메모리: YAML::Node는 shared_ptr 기반 → 복사 저렴. 단, 쓰기 가능 참조 의미.
)";

    cout << R"(
  ┌─ YAML 메모리 / 보안 함정 ─────────────────────────────┐
  │ 1. Billion Laughs 공격 → anchor 깊이/노드 수 제한 필요│
  │ 2. 큰 멀티라인 스칼라 → 청크 처리 필요                │
  │ 3. yaml-cpp Node 복사는 얕은 복사 (shared_ptr)        │
  │    → 의도치 않게 공유 상태 변경 가능                  │
  │ 4. as<int>("5km") 같은 변환 실패 → 예외 (try/catch)   │
  │ 5. 들여쓰기 탭 사용 → 라이브러리마다 동작 다름        │
  │ 6. UTF-8 BOM → 일부 파서 첫 키 깨짐                   │
  │ 7. plain scalar "yes"/"no" 추론 → 문자열로 강제하려면 │
  │    "yes" 따옴표 필수 (Norway 문제: NO는 노르웨이 코드)│
  │ 8. 신뢰 없는 입력은 절대 직접 deserialize 하지 말 것  │
  └───────────────────────────────────────────────────────┘

  [선택 가이드]
    설정 파일 사용자가 직접 편집  → YAML / TOML
    프로그램 간 데이터 교환       → JSON
    표 형태 데이터                 → CSV
    초고속 직렬화                  → MessagePack / Protobuf / Cap'n Proto
)";

    cout << endl;
}


// =============================================================================
//  레슨 4 — INI / TOML 단순 설정 포맷
// =============================================================================
//
//  [INI - Windows 전통, 매우 단순]
//    ; 주석
//    [section]
//    key = value
//    key2 = value2
//
//    [section2]
//    ...
//
//    명세 없음(!!) → 라이브러리마다 동작 다름:
//      - 따옴표 처리 다름
//      - 같은 키 중복 처리 다름
//      - 섹션 없는 키 처리 다름
//      - 서브섹션 ([db.master]) 라이브러리마다 해석 다름
//
//  [TOML - Tom's Obvious Minimal Language]
//    명세 있음 (https://toml.io). 타입 명시. Rust/Cargo 표준.
//    [database]
//    server = "192.168.1.1"
//    ports = [8000, 8001]
//    enabled = true
//    last-update = 2026-05-05T10:30:00Z   # 날짜 타입
//
//  [구현]
//    여기선 INI를 직접 파싱. TOML은 toml++ (https://github.com/marzer/tomlplusplus) 사용 권장.
// =============================================================================

class IniParser {
public:
    using Section = map<string, string>;
    using Document = map<string, Section>;

    static Document parse(istream& in) {
        Document doc;
        string current_section;
        string line;
        size_t lineno = 0;

        while (getline(in, line)) {
            ++lineno;
            // BOM 제거 (첫 줄에만)
            if (lineno == 1 && line.size() >= 3 &&
                (uint8_t)line[0] == 0xEF &&
                (uint8_t)line[1] == 0xBB &&
                (uint8_t)line[2] == 0xBF) {
                line.erase(0, 3);
            }
            // CR 제거 (CRLF 처리)
            if (!line.empty() && line.back() == '\r') line.pop_back();

            // 좌우 공백 제거
            auto start = line.find_first_not_of(" \t");
            auto end   = line.find_last_not_of(" \t");
            if (start == string::npos) continue;            // 빈 줄
            string trimmed = line.substr(start, end - start + 1);

            if (trimmed[0] == ';' || trimmed[0] == '#') continue;  // 주석

            if (trimmed.front() == '[' && trimmed.back() == ']') {
                current_section = trimmed.substr(1, trimmed.size() - 2);
                // [메모리] 같은 섹션 두 번 선언되면? 누적 (병합)
                doc[current_section];   // 빈 섹션이라도 등록
                continue;
            }

            // key = value
            auto eq = trimmed.find('=');
            if (eq == string::npos) {
                throw runtime_error("INI line " + to_string(lineno) + ": missing '='");
            }
            string key = trimmed.substr(0, eq);
            string val = trimmed.substr(eq + 1);
            // key 우측, val 좌우 공백 제거
            while (!key.empty() && (key.back() == ' ' || key.back() == '\t'))
                key.pop_back();
            auto vstart = val.find_first_not_of(" \t");
            if (vstart != string::npos) val = val.substr(vstart);
            // 따옴표로 감싸진 값 처리 (선택적)
            if (val.size() >= 2 && val.front() == '"' && val.back() == '"') {
                val = val.substr(1, val.size() - 2);
            }

            // [메모리] 같은 키 중복? 마지막 값으로 덮어씀
            doc[current_section][std::move(key)] = std::move(val);
        }
        return doc;
    }
};

void lesson4_ini_toml() {
    cout << "[레슨 4] INI / TOML — 단순 설정 포맷\n\n";

    string ini_text = R"(
; 데이터베이스 설정
[database]
host = localhost
port = 5432
user = "admin user"   ; 따옴표 안에 공백
password = secret123

[logging]
level = info
file = /var/log/app.log

[features]
enable_cache = true
)";
    istringstream in(ini_text);
    auto doc = IniParser::parse(in);
    for (auto& [sec, kvs] : doc) {
        cout << "  [" << sec << "]\n";
        for (auto& [k, v] : kvs) {
            cout << "    " << k << " = " << v << "\n";
        }
    }

    cout << R"(
  [TOML 사용 권장 - toml++ 의사코드]
  ─────────────────────────────────────────
  #include <toml++/toml.h>
  auto config = toml::parse_file("config.toml");
  std::string host = config["database"]["host"].value_or(""s);
  int port         = config["database"]["port"].value_or(0);
  // 메모리: toml::table은 노드 트리 소유. 이동만 가능, 복사 비싸므로 std::move.

  ┌─ INI/TOML 함정 ───────────────────────────────────────┐
  │ INI                                                   │
  │  - 표준 명세 없음 → 호환성 위험                       │
  │  - 타입 추론 없음 → 모든 값이 문자열, 변환 직접       │
  │  - 중첩 객체 표현 없음 (서브섹션은 비표준)            │
  │  - 배열 표현 없음                                     │
  │ TOML                                                  │
  │  - 날짜/시간 타입 있음 → 표준 라이브러리 사용         │
  │  - 큰 따옴표 vs 작은 따옴표 의미 다름                 │
  │  - 멀티라인 문자열 시작 줄 다음 개행 자동 제거        │
  │  - 핫스팟: parse_file로 큰 파일 읽으면 일시 메모리 2배│
  │    (파일 read + node tree 동시 존재) → mmap 고려      │
  └───────────────────────────────────────────────────────┘
)";

    cout << endl;
}


// =============================================================================
//  레슨 5 — 메모리 함정 카탈로그 (모든 포맷 공통)
// =============================================================================

void lesson5_memory_pitfalls() {
    cout << "[레슨 5] 메모리 함정 카탈로그\n\n";

    // ───────────────────────────────────────────────────────────
    // 함정 1: string_view 댕글링
    // ───────────────────────────────────────────────────────────
    cout << "  [1] string_view 댕글링\n";
    {
        // 잘못된 패턴 (주석으로만 표시 - 실제 실행 시 UB)
        // auto bad = []() -> string_view {
        //     string local = "hello";
        //     return local;       // string_view → 사라진 string ⚠
        // };
        // string_view dangling = bad();    // UB!

        // 안전한 패턴: 원본 buffer를 명시적으로 살려둔다
        string owner = "persistent buffer";
        string_view safe(owner);
        cout << "    안전한 view: " << safe << " (owner 수명 = view 수명)\n";

        // CSV/JSON 파서가 string_view 반환한다면 반드시
        // "원본 텍스트가 살아있는 동안만 유효" 명시해야 함.
    }

    // ───────────────────────────────────────────────────────────
    // 함정 2: 거대 파일 통째 로드
    // ───────────────────────────────────────────────────────────
    cout << "\n  [2] 거대 파일 로드 전략 비교\n";
    cout << R"(
    전략 A (나쁨): file.read() → string 통째
      └ 4GB CSV → 4GB RAM + 파싱 결과 4GB = 8GB
      └ 32-bit 프로세스: bad_alloc 직행
      └ 컨테이너 OOM Killer 표적

    전략 B (보통): ifstream + getline 한 줄씩
      └ 메모리 = 한 줄 크기. 안전.
      └ 단, 파싱 결과 vector는 여전히 누적 → 결과 처리도 streaming화.

    전략 C (좋음): mmap (POSIX) / MapViewOfFile (Windows)
      └ 파일을 가상 메모리에 매핑. 페이지 단위 로드.
      └ string_view로 zero-copy 파싱 가능.
      └ 단, 매핑 동안 파일 잠금 / 64-bit 권장 / 네트워크 FS 위험.

    전략 D (최고): SAX 파서 + zero-copy + 청크 콜백
      └ simdjson on-demand, rapidjson SAX, expat (XML)
      └ GB 파일을 수십 MB 메모리로 처리.
)";

    // ───────────────────────────────────────────────────────────
    // 함정 3: vector 재할당 비용
    // ───────────────────────────────────────────────────────────
    cout << "\n  [3] vector 재할당 비용 측정\n";
    {
        const int N = 100000;
        auto bench = [](auto label, auto fn) {
            auto t0 = chrono::high_resolution_clock::now();
            fn();
            auto t1 = chrono::high_resolution_clock::now();
            cout << "    " << label << ": "
                 << chrono::duration_cast<chrono::microseconds>(t1 - t0).count()
                 << " us\n";
        };

        bench("reserve 없음", [&]{
            vector<int> v;
            for (int i = 0; i < N; ++i) v.push_back(i);
        });
        bench("reserve(N)  ", [&]{
            vector<int> v;
            v.reserve(N);                  // 핵심
            for (int i = 0; i < N; ++i) v.push_back(i);
        });
        // CSV 파서에서 행 수를 미리 알면 reserve로 큰 차이.
    }

    // ───────────────────────────────────────────────────────────
    // 함정 4: small string optimization (SSO)
    // ───────────────────────────────────────────────────────────
    cout << "\n  [4] SSO와 메모리 단편화\n";
    cout << R"(
    std::string은 짧은 문자열(보통 15~22자)을 객체 내부에 저장 (SSO).
    그 이상은 heap 할당.
    영향:
      - CSV 셀이 평균 짧으면 heap 거의 안 침 → GB 파일도 빠름
      - 셀이 평균 길면 셀마다 heap 할당 → 단편화 / 느림
      - JSON 키는 짧은 경우가 많음 → SSO 활용
    측정: 표준 라이브러리 구현마다 SSO 임계값 다름
      libstdc++ : 15
      libc++    : 22
      MSVC STL  : 15
)";

    // ───────────────────────────────────────────────────────────
    // 함정 5: move vs copy
    // ───────────────────────────────────────────────────────────
    cout << "\n  [5] move semantics 활용\n";
    {
        vector<string> rows;
        // 나쁨: 값 복사
        string field = "long string ........................................";
        rows.push_back(field);              // 복사 (heap 또 할당)

        // 좋음: 이동
        rows.push_back(std::move(field));   // 포인터만 이동
        // [주의] move 후 field는 "유효하지만 미정의" 상태.
        // 다시 사용하려면 reassign 필요.
        field = "reused";
        cout << "    move 후 reassign: " << field << "\n";
    }

    // ───────────────────────────────────────────────────────────
    // 함정 6: 인코딩 문제
    // ───────────────────────────────────────────────────────────
    cout << "\n  [6] 인코딩 함정\n";
    cout << R"(
    Windows Excel CSV 저장 시:
      - "CSV UTF-8 (쉼표로 구분)" → UTF-8 BOM 포함
      - "CSV (쉼표로 구분)"        → 시스템 코드페이지 (한국: CP949)
    리눅스에서 CP949 파일을 UTF-8로 읽으면 한글 깨짐.
    해법:
      - BOM 검출하여 BOM 있으면 UTF-8, 없으면 휴리스틱
      - 명시적 인코딩 옵션 받기 (사용자가 지정)
      - iconv / ICU로 변환
    JSON은 RFC 8259상 UTF-8 강제 (다른 인코딩 금지)
    YAML은 UTF-8/UTF-16/UTF-32 모두 허용 (BOM으로 구분)
)";

    cout << endl;
}


// =============================================================================
//  레슨 6 — 실무 패턴: 안전한 설정 로더
// =============================================================================
//
//  실무에서 마주칠 요구사항:
//    1. 환경별 설정 파일 (config.yaml + config.production.yaml)
//    2. 환경 변수 오버라이드 (DATABASE_URL=...)
//    3. 핫 리로드 (파일 변경 감지)
//    4. 검증 (필수 키 누락 → 시작 거부)
//    5. 비밀 값 마스킹 (로그에 password 안 찍기)
//    6. 멀티 스레드 안전 접근
// =============================================================================

class Config {
public:
    // [메모리] 내부 저장소는 unordered_map. 키 검색 O(1) 평균.
    // get() 반환은 optional<string> → 없을 때 깔끔.
    optional<string> get(const string& key) const {
        // 1) 환경 변수 우선 (12-factor app 원칙)
        // [주의] getenv 반환 포인터는 환경 변경되면 무효 - 즉시 string 복사
        if (const char* env = getenv(env_name(key).c_str())) {
            return string(env);
        }
        // 2) 파일 값
        auto it = data_.find(key);
        if (it != data_.end()) return it->second;
        return nullopt;
    }

    template<typename T>
    T get_or(const string& key, T fallback) const {
        if (auto v = get(key)) {
            stringstream ss(*v);
            T result;
            ss >> result;
            if (ss.fail()) return fallback;
            return result;
        }
        return fallback;
    }

    // 필수 키 검증. 누락 시 throw.
    void require(const vector<string>& keys) const {
        vector<string> missing;
        for (auto& k : keys) {
            if (!get(k)) missing.push_back(k);
        }
        if (!missing.empty()) {
            string msg = "Config missing required keys:";
            for (auto& m : missing) msg += " " + m;
            throw runtime_error(msg);
        }
    }

    // 비밀 키는 dump 시 마스킹
    string dump_safe() const {
        string out;
        for (auto& [k, v] : data_) {
            out += k + " = ";
            if (is_secret(k)) out += "****";
            else out += v;
            out += "\n";
        }
        return out;
    }

    void load_ini(istream& in) {
        auto doc = IniParser::parse(in);
        for (auto& [sec, kvs] : doc) {
            for (auto& [k, v] : kvs) {
                data_[sec + "." + k] = v;
            }
        }
    }

private:
    unordered_map<string, string> data_;

    static string env_name(const string& key) {
        // database.host → DATABASE_HOST
        string env;
        env.reserve(key.size());
        for (char c : key) {
            if (c == '.') env.push_back('_');
            else env.push_back((char)toupper((uint8_t)c));
        }
        return env;
    }

    static bool is_secret(const string& key) {
        // 단순 휴리스틱 - 실무에선 명시적 secret 목록 관리
        static const vector<string> patterns = {
            "password", "secret", "token", "key", "credential"
        };
        string lower = key;
        transform(lower.begin(), lower.end(), lower.begin(),
                  [](char c){ return (char)tolower((uint8_t)c); });
        for (auto& p : patterns) {
            if (lower.find(p) != string::npos) return true;
        }
        return false;
    }
};

void lesson6_practical_config_loader() {
    cout << "[레슨 6] 실무 — 안전한 설정 로더\n\n";

    string ini = R"(
[database]
host = localhost
port = 5432
password = supersecret123

[server]
bind = 0.0.0.0
threads = 8
)";
    istringstream in(ini);
    Config cfg;
    cfg.load_ini(in);

    // 필수 키 검증
    try {
        cfg.require({"database.host", "database.port", "server.bind"});
        cout << "  필수 키 검증 PASS\n";
    } catch (exception& e) {
        cout << "  검증 실패: " << e.what() << "\n";
    }

    // 안전한 dump (비밀 마스킹)
    cout << "\n  [안전 dump]\n";
    cout << cfg.dump_safe();

    // 타입 변환
    int threads = cfg.get_or("server.threads", 4);
    int port    = cfg.get_or("database.port", 5432);
    cout << "  threads = " << threads << ", port = " << port << "\n";

    cout << R"(
  ┌─ 실무 설정 로더 체크리스트 ───────────────────────────┐
  │ ✓ 필수 키 누락 시 시작 거부 (조용히 기본값 X)         │
  │ ✓ 환경 변수 오버라이드 지원 (12-factor)               │
  │ ✓ 비밀 값 로그 마스킹                                 │
  │ ✓ 타입 변환 실패 처리                                 │
  │ ✓ 멀티 스레드 접근 - shared_mutex / immutable snapshot│
  │ ✓ 핫 리로드 시 race condition - atomic<shared_ptr>    │
  │ ✓ 큰 파일은 mmap, 작은 파일은 read                    │
  │ ✓ 파일 권한 검사 (world-readable에 password 위험)     │
  └───────────────────────────────────────────────────────┘
)";

    cout << endl;
}


// =============================================================================
//  연습문제
// =============================================================================
//
//  [연습 1] CsvParser에 quote_all 옵션 추가
//    write() 시 따옴표가 필요 없는 필드도 강제로 따옴표로 감싸기.
//    (Excel 호환성 위해 자주 필요)
//
//  [연습 2] CsvParser::parse_streaming을 string_view 기반으로 재작성
//    한 행을 string_view 벡터로 콜백에 넘기되, 다음 행 처리 시 무효화 명시.
//    힌트: 내부 버퍼를 callback 호출 사이에만 유효하게 유지.
//
//  [연습 3] JsonParser에 number를 int / double 둘로 분리
//    소수점/지수 없으면 int64_t, 있으면 double. variant 멤버 추가.
//
//  [연습 4] JsonParser에 parse_file(path) 추가
//    mmap으로 매핑하여 string_view로 처리. 파싱 도중 파일 잠금 정책 결정.
//
//  [연습 5] Config 클래스에 파일 변경 감지 추가
//    별도 스레드가 파일 mtime 폴링. 변경 감지 시 shared_ptr<Config> 교체.
//    원자적 교체로 reader는 락 없이 안전.
//
//  [연습 6] YAML 안전 모드 시뮬레이션
//    주어진 YAML에서 anchor 노드 수, 깊이 추정. 임계값 초과 시 거부.
//
//  [연습 7] 환경별 설정 병합
//    config.yaml (기본) + config.production.yaml (오버라이드).
//    deep merge - 객체는 병합, 스칼라는 덮어쓰기, 배열은 정책 선택.
//
//  [연습 8] CSV → JSON 변환기
//    헤더를 키로 사용, 각 행을 객체로 만들어 JSON 배열로 출력.
//    스트리밍 모드로 GB 파일도 처리 가능하게.
// =============================================================================
