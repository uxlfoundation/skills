Repair the standards-conformance iterator regression in the pinned oneDPL source at `/app/oneDPL`.

The public reproducer supplies a valid random-access iterator whose comma operator is deleted. `oneapi::dpl::transform` under the host `par` policy should accept it and produce the expected output, but the current headers fail to compile inside oneDPL.

Run `/app/reproduce.sh` before and after your repair. Preserve the custom iterator, deleted comma operator, host parallel policy, oneTBB backend, and public reproducer. Make a generalized library correction for valid iterators across affected algorithm families; do not weaken the iterator or special-case the supplied type. Briefly explain the failure, root cause, repair, and verification.
