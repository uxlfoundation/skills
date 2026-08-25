Repair the batched oneDNN matmul descriptor bug in `/app/batched_matmul.cpp`.

The application stores each weights matrix contiguously as `[batch][n][k]`, because it is shared with another framework, while oneDNN matmul consumes it logically as `[batch][k][n]`. The program currently declares the weights with a default contiguous descriptor. It executes successfully but produces incorrect results.

Run `/app/reproduce.sh` before and after your change. Preserve the physical weights buffer, input generator, oneDNN matmul primitive, direct application-owned memory handles, and output order. Do not repack, transpose, copy, or manually recompute the weights or result. Correct the logical memory description, and briefly explain the physical/logical mismatch, the descriptor repair, and how you verified it.
