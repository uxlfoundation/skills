Repair the topology `alltoallv` buffer-slice regression in the pinned oneCCL incident fixture at `/app/oneCCL`.

The public reproducer models a neighbor exchange with a 16 KiB live segment and a final zero-count peer. The current topology builder represents zero-count send and receive segments with one-past-allocation pointers. A Level Zero implementation may reject those pointers while creating IPC handles even though no data is transferred.

Run `/app/reproduce.sh` before and after your repair. Make zero-count send, receive, and in-place temporary slices explicit null/empty slices while preserving live segment offsets, counts, datatype scaling, in-place behavior, and the topology algorithm. Do not remove zero-count peers, change counts, add padding, select a different algorithm, or weaken the reproducer. Briefly explain the failure, root cause, repair, and verification.
