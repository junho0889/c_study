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
