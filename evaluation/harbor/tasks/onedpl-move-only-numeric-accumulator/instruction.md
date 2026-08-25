Repair the host-policy numeric algorithm regression in the pinned oneDPL source at `/app/oneDPL`.

The public reproducer uses a non-copyable, movable accumulator with `transform_reduce` under both `par` and `par_unseq`. These standard-aligned host policies should accept the accumulator and compute the correct result, but the current headers fail to compile after trying to copy it.

Run `/app/reproduce.sh` before and after your repair. Preserve the deleted copy operations, both execution policies, the oneTBB host backend, and the public reproducer. Make a generalized source-level correction for move-only numeric accumulation; do not special-case the supplied type or make the consumer copyable. Briefly explain the failure, root cause, repair, and verification.
