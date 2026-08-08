The 12x claim is under-supported and must be withdrawn. A single tiny input mostly exposes fixed overhead, and timing an asynchronous submission without synchronization measures enqueue latency rather than completed GPU work. Reading the result before an event or queue wait also makes correctness unproven.

First define a correctness contract. Use deterministic inputs, compare every candidate result with a trusted CPU reference, state whether equality is exact or tolerance-based, and fail the benchmark before reporting timing when the comparison fails. Wait on the returned event with error propagation before either reading output or stopping a compute timer.

Measure a size sweep that includes the 1,024-element smoke case, expected crossover sizes, and representative production workloads. Record allocation and setup, host-to-device transfer, warmup, steady-state kernel execution, synchronization, device-to-host transfer, and teardown separately. Also report an end-to-end time whose boundaries include every cost paid by the application.

Run enough measured iterations to report the median plus dispersion such as standard deviation or percentile range, retaining per-iteration samples and investigating outliers. Compare against an optimized CPU baseline that performs the same work and passes the same correctness check.

Record GPU and CPU models, device selection, driver and runtime versions, compiler and optimization flags, build type, power mode, thread or affinity settings, and relevant library versions. Once a repeatable difference exists, use an event timeline and a profiler trace to locate transfer, launch, synchronization, or kernel bottlenecks; profiling should follow a reproducible result rather than substitute for one.

The final report should contain the correctness outcome, per-size baseline and candidate results, timing boundaries, iteration counts, dispersion, and limitations. A defensible claim would be limited to the tested hardware, software, problem sizes, and stated end-to-end or kernel-only scope—for example, that the GPU median was faster for the tested production-size range. It must not promise a general or guaranteed speedup.
