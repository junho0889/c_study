cmake_minimum_required(VERSION 3.16)
project(CppProjects LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ── 실전 프로젝트 10개 ──

# 01. 고성능 데이터 파이프라인
add_executable(proj_data_pipeline       01_data_pipeline/main.cpp)

# 02. 게임 엔진 코어
add_executable(proj_game_engine         02_game_engine/main.cpp)

# 03. 이미지 처리 엔진
add_executable(proj_image_processing    03_image_processing/main.cpp)

# 04. 금융 트레이딩 시스템
add_executable(proj_trading_system      04_trading_system/main.cpp)

# 05. 미니 데이터베이스 엔진
add_executable(proj_database_engine     05_database_engine/main.cpp)

# 06. 미니 프로그래밍 언어 인터프리터
add_executable(proj_compiler            06_compiler/main.cpp)

# 07. 오디오 프로세싱 엔진
add_executable(proj_audio_engine        07_audio_engine/main.cpp)

# 08. 고성능 네트워크 서버
add_executable(proj_network_server      08_network_server/main.cpp)

# 09. 2D 물리 엔진
add_executable(proj_physics_engine      09_physics_engine/main.cpp)

# 10. 머신러닝 추론 엔진
add_executable(proj_ml_inference        10_ml_inference/main.cpp)
