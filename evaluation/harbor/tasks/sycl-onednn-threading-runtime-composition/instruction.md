Repair the intermittent execution failure in the pinned oneDNN RNN example under `/app`.

Run `bash /app/reproduce.sh` first. Inspect `/app/loader-evidence.txt`, the compiler/link configuration, `/app/runtime.cmake`, and the available oneDNN builds under `/opt/onednn`. The current application combines more than one CPU threading/runtime composition and can abort or segfault nondeterministically. Select one coherent supported composition in `/app/runtime.cmake`, then use repeated clean runs to verify the result.

Write a concise `/app/diagnosis.md` that records the failing phase, the conflicting libraries/runtimes shown by loader evidence, why enabling oneDNN verbose output is a diagnostic perturbation rather than a repair, the selected repair, and what hardware or runtime coverage remains unverified.

Do not modify the example, build harness, or reproducer; replace oneDNN with a stub; suppress crashes; use verbose logging as the repair; or claim a hardware speedup. Finish with `bash /app/reproduce.sh` passing.
