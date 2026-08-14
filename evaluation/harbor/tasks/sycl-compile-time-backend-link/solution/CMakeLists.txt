cmake_minimum_required(VERSION 3.20)
project(sycl_link_probe LANGUAGES CXX)

set(DPCPP_COMPILER "icpx" CACHE STRING "DPC++ compiler driver")
find_program(DPCPP_DRIVER NAMES "${DPCPP_COMPILER}" REQUIRED)
set(SYCL_TARGET_FLAGS "$ENV{UXL_SYCL_TARGET_FLAGS}" CACHE STRING "SYCL target flags")
separate_arguments(SYCL_TARGET_ARGS NATIVE_COMMAND "${SYCL_TARGET_FLAGS}")

set(SYCL_OBJECT "${CMAKE_BINARY_DIR}/sycl_kernel.o")
set(SYCL_EXECUTABLE "${CMAKE_BINARY_DIR}/sycl_probe")

add_custom_command(
    OUTPUT "${SYCL_OBJECT}"
    COMMAND "${DPCPP_DRIVER}" -std=c++17 -O0 -fsycl ${SYCL_TARGET_ARGS}
            -c "${CMAKE_SOURCE_DIR}/sycl_kernel.cpp" -o "${SYCL_OBJECT}"
    DEPENDS "${CMAKE_SOURCE_DIR}/sycl_kernel.cpp"
    VERBATIM
)

add_custom_command(
    OUTPUT "${SYCL_EXECUTABLE}"
    COMMAND "${DPCPP_DRIVER}" -std=c++17 -O0 -fsycl ${SYCL_TARGET_ARGS}
            "${CMAKE_SOURCE_DIR}/main.cpp" "${SYCL_OBJECT}" -o "${SYCL_EXECUTABLE}"
    DEPENDS "${CMAKE_SOURCE_DIR}/main.cpp" "${SYCL_OBJECT}"
    VERBATIM
)

add_custom_target(build_sycl_probe ALL DEPENDS "${SYCL_EXECUTABLE}")
