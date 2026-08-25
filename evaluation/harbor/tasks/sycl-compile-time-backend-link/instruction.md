Repair the reproducible SYCL build in `/app/CMakeLists.txt` and write a concise diagnosis to `/app/diagnosis.md`.

The project deliberately compiles `/app/sycl_kernel.cpp` with the configured DPC++ compiler, but its final executable fails to link. A developer believes the CPU backend package is missing and wants to install additional runtimes until the error disappears.

Run `/app/reproduce.sh` before and after the repair. Preserve the original source files and public reproducer. Identify the first failing phase from the verbose build, fix the compiler/link contract in CMake, and verify the deterministic kernel through the explicitly selected CPU backend. The repair must work from a clean build directory and must not replace the executable with a script, constant output, or host-only reimplementation. In `diagnosis.md`, state the failing phase and root cause, the durable build change, the runtime/device evidence, and anything that remains unverified about other hardware.
