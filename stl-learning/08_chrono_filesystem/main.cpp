/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  STL 학습 08단계: chrono (시간)과 filesystem (파일 시스템)
  실행 방법: g++ -std=c++17 main.cpp -o main && ./main
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  std::chrono    = 시간을 다루는 도구 모음 (타이머, 날짜, 시간 측정)
  std::filesystem = 파일과 폴더를 다루는 도구 (목록 보기, 만들기, 지우기)

  비유:
  - chrono     = 스톱워치 + 달력. 시간을 재거나 날짜를 다루는 도구.
  - filesystem = 파일 탐색기(윈도우의 "내 컴퓨터"). 폴더와 파일을 탐색.
===============================================================================
*/

#include <iostream>
#include <chrono>
#include <thread>       // sleep_for 용
#include <filesystem>
#include <fstream>      // 파일 쓰기용
#include <string>
#include <vector>
#include <iomanip>      // put_time 용
using namespace std;
namespace fs = std::filesystem;  // 타이핑을 줄이기 위한 별명

// ┌─────────────────────────────────────────────┐
// │  레슨 1: duration — 시간 길이 표현             │
// └─────────────────────────────────────────────┘
void lesson1_duration() {
    cout << "[레슨 1] chrono::duration — 시간 길이" << endl;
    cout << endl;

    /*
      duration은 "얼마 동안"을 나타냅니다.
      비유: "3시간", "45분", "100밀리초" 같은 시간의 길이.

      자주 쓰는 단위:
        chrono::hours        = 시간
        chrono::minutes      = 분
        chrono::seconds      = 초
        chrono::milliseconds = 밀리초 (1/1000초)
        chrono::microseconds = 마이크로초 (1/1000000초)
    */

    using namespace chrono;

    // 시간 만들기
    auto two_hours = hours(2);
    auto thirty_min = minutes(30);
    auto total = two_hours + thirty_min;

    // 변환: 전체를 분으로 바꾸기
    auto total_minutes = duration_cast<minutes>(total);
    cout << "  2시간 30분 = " << total_minutes.count() << "분" << endl;

    // 변환: 전체를 초로 바꾸기
    auto total_seconds = duration_cast<seconds>(total);
    cout << "  2시간 30분 = " << total_seconds.count() << "초" << endl;

    // C++14 리터럴 (using namespace chrono_literals; 필요)
    // auto t = 2h + 30min + 15s;

    // 비교
    auto a = seconds(90);
    auto b = minutes(1);
    cout << "  90초 > 1분? " << (a > b ? "예" : "아니오") << " (90초 vs 60초)" << endl;
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 2: clock과 time_point — 현재 시각       │
// └─────────────────────────────────────────────┘
void lesson2_clock_and_time_point() {
    cout << "[레슨 2] clock과 time_point — 지금 몇 시?" << endl;
    cout << endl;

    /*
      clock 종류:
        system_clock  = 벽시계 (현재 시각, 날짜)
        steady_clock  = 스톱워치 (측정용, 절대 뒤로 안 감)
        high_resolution_clock = 가장 정밀한 시계

      time_point = "시간 위의 한 점". 예: "2024년 3월 15일 14시 30분"

      비유:
        duration   = "2시간" (길이)
        time_point = "오후 3시" (시각)
    */

    using namespace chrono;

    // 현재 시각 구하기
    auto now = system_clock::now();

    // time_t로 변환해서 읽기 쉽게 출력
    time_t now_time = system_clock::to_time_t(now);
    cout << "  현재 시각: " << ctime(&now_time);

    // epoch(기준점)부터 지금까지의 초
    auto epoch_seconds = duration_cast<seconds>(now.time_since_epoch());
    cout << "  epoch 이후 초: " << epoch_seconds.count() << endl;
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 3: 실행 시간 측정 — 스톱워치             │
// └─────────────────────────────────────────────┘
void lesson3_measure_time() {
    cout << "[레슨 3] 실행 시간 측정 — 코드가 얼마나 걸릴까?" << endl;
    cout << endl;

    /*
      steady_clock은 "절대 뒤로 안 가는 시계"라서 시간 측정에 적합합니다.
      비유: 체육 시간에 달리기를 재는 스톱워치.
    */

    using namespace chrono;

    // 시작!
    auto start = steady_clock::now();

    // 측정할 작업: 100만 번 더하기
    long long sum = 0;
    for (int i = 0; i < 1000000; i++) {
        sum += i;
    }

    // 끝!
    auto end = steady_clock::now();

    // 걸린 시간 계산
    auto elapsed_us = duration_cast<microseconds>(end - start);
    auto elapsed_ms = duration_cast<milliseconds>(end - start);

    cout << "  100만 번 더하기 결과: " << sum << endl;
    cout << "  걸린 시간: " << elapsed_us.count() << " 마이크로초" << endl;
    cout << "  걸린 시간: " << elapsed_ms.count() << " 밀리초" << endl;
    cout << endl;

    // sleep_for — 잠깐 멈추기
    cout << "  100밀리초 대기 중..." << endl;
    auto sleep_start = steady_clock::now();
    this_thread::sleep_for(milliseconds(100));
    auto sleep_end = steady_clock::now();
    auto slept = duration_cast<milliseconds>(sleep_end - sleep_start);
    cout << "  실제 대기 시간: " << slept.count() << "ms" << endl;
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 4: filesystem::path — 경로 다루기       │
// └─────────────────────────────────────────────┘
void lesson4_path() {
    cout << "[레슨 4] filesystem::path — 경로 다루기" << endl;
    cout << endl;

    /*
      path는 파일이나 폴더의 경로를 다루는 클래스입니다.
      운영체제에 맞게 / 또는 \를 자동으로 처리해 줍니다.

      비유: 주소를 "서울시/강남구/테헤란로"처럼 계층적으로 표현하는 것.
    */

    fs::path file_path = "documents/report/2024/grades.txt";

    cout << "  전체 경로:   " << file_path << endl;
    cout << "  파일 이름:   " << file_path.filename() << endl;
    cout << "  확장자:      " << file_path.extension() << endl;
    cout << "  확장자 뺀 이름: " << file_path.stem() << endl;
    cout << "  부모 폴더:   " << file_path.parent_path() << endl;
    cout << endl;

    // 경로 합치기 (/ 연산자)
    fs::path base = "home";
    fs::path full = base / "user" / "documents" / "file.txt";
    cout << "  경로 합치기: " << full << endl;

    // 확장자 바꾸기
    fs::path original = "report.txt";
    original.replace_extension(".pdf");
    cout << "  확장자 변경: " << original << endl;
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 5: 파일·폴더 만들기와 탐색              │
// └─────────────────────────────────────────────┘
void lesson5_directory_operations() {
    cout << "[레슨 5] 폴더 만들기, 파일 쓰기, 목록 보기" << endl;
    cout << endl;

    /*
      filesystem으로 할 수 있는 일:
        - 폴더 만들기/지우기
        - 파일 존재 여부 확인
        - 파일 크기 확인
        - 디렉토리 안의 파일 목록 보기

      비유: 파일 탐색기에서 하는 일을 코드로 하는 것.
    */

    fs::path test_dir = "test_stl_08";

    // 1) 폴더 만들기
    if (!fs::exists(test_dir)) {
        fs::create_directories(test_dir / "sub1" / "deep");
        fs::create_directory(test_dir / "sub2");
        cout << "  폴더 생성 완료: " << test_dir << endl;
    }

    // 2) 파일 만들기
    vector<string> file_names = {"hello.txt", "data.csv", "notes.md"};
    for (const auto& name : file_names) {
        ofstream out(test_dir / name);
        out << "이 파일은 " << name << " 입니다." << endl;
        out.close();
    }

    // sub1에도 파일 만들기
    {
        ofstream out(test_dir / "sub1" / "inner.txt");
        out << "안쪽 파일입니다." << endl;
    }

    // 3) 디렉토리 내용 보기 (현재 폴더만)
    cout << "  [" << test_dir << "] 내용:" << endl;
    for (const auto& entry : fs::directory_iterator(test_dir)) {
        string type = entry.is_directory() ? "[폴더]" : "[파일]";
        cout << "    " << type << " " << entry.path().filename();
        if (entry.is_regular_file()) {
            cout << " (" << entry.file_size() << " 바이트)";
        }
        cout << endl;
    }
    cout << endl;

    // 4) 재귀적으로 모든 파일 보기 (하위 폴더 포함)
    cout << "  [재귀 탐색] 모든 파일:" << endl;
    for (const auto& entry : fs::recursive_directory_iterator(test_dir)) {
        // 깊이 표시를 위한 들여쓰기
        int depth = 0;
        for (auto p = entry.path().parent_path();
             p != test_dir && !p.empty();
             p = p.parent_path()) {
            depth++;
        }
        string indent(depth * 2 + 4, ' ');

        if (entry.is_directory()) {
            cout << indent << "[폴더] " << entry.path().filename() << endl;
        } else {
            cout << indent << entry.path().filename()
                 << " (" << entry.file_size() << "B)" << endl;
        }
    }
    cout << endl;

    // 5) 파일 존재 확인, 크기
    fs::path check_file = test_dir / "hello.txt";
    if (fs::exists(check_file)) {
        cout << "  " << check_file << " 존재, 크기: "
             << fs::file_size(check_file) << " 바이트" << endl;
    }
    cout << endl;

    // 6) 정리: 테스트 폴더 삭제
    fs::remove_all(test_dir);
    cout << "  테스트 폴더 삭제 완료" << endl;
    cout << endl;
}

// ┌─────────────────────────────────────────────┐
// │  레슨 6: 현재 경로와 유용한 함수들             │
// └─────────────────────────────────────────────┘
void lesson6_useful_functions() {
    cout << "[레슨 6] 현재 경로와 유용한 함수들" << endl;
    cout << endl;

    // 현재 작업 디렉토리
    cout << "  현재 경로: " << fs::current_path() << endl;

    // 임시 폴더 경로
    cout << "  임시 폴더: " << fs::temp_directory_path() << endl;

    // 디스크 공간 정보
    auto space = fs::space(fs::current_path());
    auto to_gb = [](uintmax_t bytes) { return bytes / (1024.0 * 1024.0 * 1024.0); };
    cout << "  디스크 전체: " << fixed << setprecision(1)
         << to_gb(space.capacity) << " GB" << endl;
    cout << "  사용 가능:   " << to_gb(space.available) << " GB" << endl;
    cout << endl;
}

int main() {
    cout << "============================================================" << endl;
    cout << "  STL 08단계 : chrono (시간)과 filesystem (파일)" << endl;
    cout << "============================================================" << endl;
    cout << endl;

    lesson1_duration();
    lesson2_clock_and_time_point();
    lesson3_measure_time();
    lesson4_path();
    lesson5_directory_operations();
    lesson6_useful_functions();

    return 0;
}
