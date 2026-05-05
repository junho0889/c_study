cmake_minimum_required(VERSION 3.16)
project(CppLearning LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ── 기초 (01~04) ──
add_executable(01_basics                    01_basics/main.cpp)
add_executable(02_control_flow              02_control_flow/main.cpp)
add_executable(03_functions                 03_functions/main.cpp)
add_executable(04_arrays_pointers           04_arrays_pointers/main.cpp)

# ── OOP (05~06) ──
add_executable(05_oop_basics                05_oop_basics/main.cpp)
add_executable(06_inheritance_polymorphism   06_inheritance_polymorphism/main.cpp)

# ── 실전 도구 (07~10) ──
add_executable(07_templates_stl             07_templates_stl/main.cpp)
add_executable(08_memory_management         08_memory_management/main.cpp)
add_executable(09_file_exception            09_file_exception/main.cpp)
add_executable(10_modern_cpp                10_modern_cpp/main.cpp)

# ── 도구 & 환경 (11~12) ──
add_executable(11_debugging                 11_debugging/main.cpp)
add_executable(12_frameworks_build          12_frameworks_build/main.cpp)

# ── 심화 (13~15) ──
add_executable(13_design_patterns           13_design_patterns/main.cpp)
add_executable(15_networking                15_networking/main.cpp)

# ── 14 멀티스레딩 (pthread 링크 필요) ──
add_executable(14_multithreading            14_multithreading/main.cpp)
find_package(Threads REQUIRED)
target_link_libraries(14_multithreading PRIVATE Threads::Threads)

# ── 배포 (16~18) ──
add_executable(16_testing                   16_testing/main.cpp)
add_executable(17_build_deploy              17_build_deploy/main.cpp)
add_executable(18_real_project              18_real_project/main.cpp)

# ── 자료구조 & 알고리즘 (19) ──
add_executable(19_data_structures           19_data_structures/main.cpp)

# ── 고급 C++ (20~23) ──
add_executable(20_advanced_oop              20_advanced_oop/main.cpp)
add_executable(21_advanced_templates        21_advanced_templates/main.cpp)
add_executable(22_string_regex              22_string_regex/main.cpp)
add_executable(23_functional                23_functional/main.cpp)

# ── 전문가 영역 (24~28) ──
add_executable(24_advanced_concurrency      24_advanced_concurrency/main.cpp)
target_link_libraries(24_advanced_concurrency PRIVATE Threads::Threads)

add_executable(25_performance               25_performance/main.cpp)
add_executable(26_cpp20_23                  26_cpp20_23/main.cpp)
add_executable(27_systems_programming       27_systems_programming/main.cpp)
add_executable(28_security_best_practices   28_security_best_practices/main.cpp)

# ── 이벤트/콜백 & 하드웨어 (29~32) ──
add_executable(29_events_callbacks          29_events_callbacks/main.cpp)
add_executable(30_hardware_control          30_hardware_control/main.cpp)
add_executable(31_adc_dac_sensors           31_adc_dac_sensors/main.cpp)
add_executable(32_rtos_patterns             32_rtos_patterns/main.cpp)

# ── PART 11 — 실무 통합 (33~36) ──
add_executable(33_data_formats              33_data_formats/main.cpp)

# 34 네트워크: Threads + Winsock 링크 필요
add_executable(34_network_layers            34_network_layers/main.cpp)
target_link_libraries(34_network_layers PRIVATE Threads::Threads)
if(WIN32)
    target_link_libraries(34_network_layers PRIVATE ws2_32)
endif()

add_executable(35_industrial_protocols      35_industrial_protocols/main.cpp)

# 36 Docker는 Dockerfile 기반이지만 가이드 main.cpp 빌드
add_executable(36_docker_cpp                36_docker_cpp/main.cpp)

# 37 ML 추론 - 가이드 모드. 실제 SDK 사용은 옆 폴더 CMakeLists.txt.template 참고
add_executable(37_ml_inference_runtimes     37_ml_inference_runtimes/main.cpp)

# ── 실전 프로젝트 (projects/) ──
add_subdirectory(projects)
