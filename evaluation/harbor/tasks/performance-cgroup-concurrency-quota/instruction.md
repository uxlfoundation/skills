A quota-based container can expose more schedulable CPUs than its CPU-time budget. The service in `/app/quota_parallel.cpp` passes the schedulable CPU count directly to a oneTBB `task_arena`, so `/app/reproduce.sh` reports an arena wider than the cgroup v2 quota allows.

Repair `/app/quota_parallel.cpp` so its requested and initialized arena concurrency use the smaller of the schedulable CPU count and the limit described by a cgroup v2 `cpu.max` file. The program accepts an optional `CPU_MAX_FILE` argument and otherwise reads `/sys/fs/cgroup/cpu.max`.

Treat `max` as unconstrained. For positive numeric quota and period values, convert the CPU-time ratio to a whole-worker limit by rounding up, cap it at the schedulable CPU count, and never request fewer than one worker. A missing or malformed file, zero value, extra field, or overflow must safely fall back to the schedulable CPU count. Preserve the deterministic parallel checksum and the existing `key=value` output contract.

Do not hardcode the visible two-CPU test quota, change the process affinity, add timing thresholds, or replace oneTBB. The verifier uses the live container quota plus hidden quota files, including fractional and unconstrained cases.
