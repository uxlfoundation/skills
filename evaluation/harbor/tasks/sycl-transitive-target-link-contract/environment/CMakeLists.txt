cmake_minimum_required(VERSION 3.20)
project(sycl_transitive_probe LANGUAGES CXX)

include(cmake/UXLSYCL.cmake)

add_library(sycl_stage OBJECT sycl_stage.cpp)
target_compile_features(sycl_stage PRIVATE cxx_std_17)
target_link_libraries(sycl_stage PRIVATE UXL::SYCL)

add_library(transform_pipeline STATIC
    pipeline.cpp
    $<TARGET_OBJECTS:sycl_stage>
)
target_compile_features(transform_pipeline PRIVATE cxx_std_17)

add_executable(transitive_probe main.cpp)
target_compile_features(transitive_probe PRIVATE cxx_std_17)
target_link_libraries(transitive_probe PRIVATE transform_pipeline)

# Bug: the object library consumes UXL::SYCL privately, so it compiles, but
# the final executable never receives the interface target's link requirement.
