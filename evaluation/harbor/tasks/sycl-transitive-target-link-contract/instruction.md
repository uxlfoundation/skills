# Repair a transitive SYCL target-link failure

The project in `/app` uses the installed DPC++ compiler and a CMake interface target from `cmake/UXLSYCL.cmake`. Reproduce the clean build failure with `./reproduce.sh`, identify the first failing phase, and repair `CMakeLists.txt` so the SYCL link usage requirement reaches the final executable through the target graph.

Preserve the object-library and pipeline architecture. Do not edit source files, `reproduce.sh`, or `cmake/UXLSYCL.cmake`; do not hardcode oneAPI installation paths, `libsycl` filenames, or global CMake compiler/linker flags. Keep the repair target-scoped and durable across a clean configure.

Create `/app/diagnosis.md` explaining the failing phase, why the existing private usage requirement was insufficient, the durable CMake repair, the device/runtime evidence after rebuilding, and what hardware remains unverified. Finish by running `./reproduce.sh` successfully.
