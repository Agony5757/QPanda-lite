cmake_minimum_required(VERSION 3.26)
project(QPandaLitePy)

set(LIB_MahjongPy ${PROJECT_NAME})
file(GLOB_RECURSE QPandaLitePyWrapper_SRC_CPP *.cpp)

pybind11_add_module(${PROJECT_NAME} ${QPandaLitePyWrapper_SRC_CPP})

target_link_libraries(${PROJECT_NAME} PRIVATE QPandaLiteCppCore fmt)

target_compile_definitions(${PROJECT_NAME} PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO})