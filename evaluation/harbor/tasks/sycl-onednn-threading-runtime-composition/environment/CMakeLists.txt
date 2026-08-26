cmake_minimum_required(VERSION 3.20)
project(uxl_onednn_runtime_composition LANGUAGES CXX)

include(${CMAKE_CURRENT_SOURCE_DIR}/runtime.cmake)

if(UXL_ONEDNN_RUNTIME STREQUAL "sycl")
  set(UXL_ONEDNN_BUILD "/opt/onednn/build-sycl")
  set(UXL_COMPILE_OPTIONS -fsycl -qopenmp)
  set(UXL_LINK_OPTIONS -fsycl -qopenmp)
  find_library(UXL_TBB_LIBRARY tbb
    PATHS /opt/intel/oneapi/tbb/latest/lib/intel64/gcc4.8
    NO_DEFAULT_PATH
    REQUIRED
  )
  set(UXL_RUNTIME_LIBRARIES ${UXL_TBB_LIBRARY})
elseif(UXL_ONEDNN_RUNTIME STREQUAL "openmp")
  set(UXL_ONEDNN_BUILD "/opt/onednn/build-openmp")
  set(UXL_COMPILE_OPTIONS -qopenmp)
  set(UXL_LINK_OPTIONS -qopenmp)
else()
  message(FATAL_ERROR "UXL_ONEDNN_RUNTIME must be sycl or openmp")
endif()

add_executable(cpu_rnn_inference_int8 cpu_rnn_inference_int8.cpp)
target_compile_features(cpu_rnn_inference_int8 PRIVATE cxx_std_17)
target_compile_options(cpu_rnn_inference_int8 PRIVATE ${UXL_COMPILE_OPTIONS})
target_link_options(cpu_rnn_inference_int8 PRIVATE ${UXL_LINK_OPTIONS})
target_include_directories(cpu_rnn_inference_int8 PRIVATE
  /opt/onednn/include
  ${UXL_ONEDNN_BUILD}/include
)
target_link_libraries(cpu_rnn_inference_int8 PRIVATE
  ${UXL_ONEDNN_BUILD}/src/libdnnl.so.3
  ${UXL_RUNTIME_LIBRARIES}
)
set_target_properties(cpu_rnn_inference_int8 PROPERTIES
  BUILD_RPATH "${UXL_ONEDNN_BUILD}/src"
)
