cmake_minimum_required(VERSION 3.10)
project($$NAME$$)

set(CMAKE_C_STANDARD 11)

include_directories(
        ${CMAKE_SOURCE_DIR}/Source
        C:/Keil_v5/C51/INC/Silabs
        Cygnal/
)

file(GLOB_RECURSE SOURCES "$$SOURCE$$/*.c" "$$SOURCE$$/*.h")

add_executable(${PROJECT_NAME} ${SOURCES})

# Define keywords for CLion parsing only
if(CMAKE_C_COMPILER_ID STREQUAL "GNU")
    target_compile_definitions(${PROJECT_NAME} PRIVATE
            code=
            data=
            xdata=
            bit=char
            "sbit=unsigned char"
            "__sbit(x)=unsigned char"
    )
endif()
