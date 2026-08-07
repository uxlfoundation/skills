Fix the nondeterministic stable compaction in `/app/stable_compact.cpp`.

Preserve the public `stable_compact(const std::vector<int>& values)` interface. The function must retain every nonnegative value in its original input order and must return deterministic results across scheduler choices. Replace the atomic slot allocation with the oneTBB algorithm intended for prefix-dependent output positions. The verifier inspects the algorithm choice as well as the output; a serial fallback, sorting, locks, or atomic slot allocation does not satisfy the task. A second parallel pass may scatter retained values into their computed positions.

Run the correctness checks before finishing and briefly explain why the original atomic implementation is race-free for its individual writes but still violates stable ordering.
