# Diagnosis

The failure is in the execution phase, not compilation or device discovery. `ldd` loader evidence for the failing executable shows a SYCL CPU oneDNN build using TBB together with the application's OpenMP runtime. Repeated launches expose a nondeterministic runtime-composition failure.

Enabling oneDNN verbose output changes timing and scheduling, so its apparent stability is a diagnostic perturbation rather than a repair. The repair selects the pinned oneDNN OpenMP build and compiles the caller for OpenMP, yielding one coherent CPU threading runtime. The repaired loader evidence contains the local OpenMP `libdnnl` and `libiomp5`, without `libsycl` or `libtbb`.

This CPU-only reproducer verifies the pinned oneDNN 3.6.1 and Intel oneAPI 2026.1.0 combination. Other oneDNN/compiler versions, accelerators, and vendor runtime stacks remain unverified, and this test makes no performance claim.
