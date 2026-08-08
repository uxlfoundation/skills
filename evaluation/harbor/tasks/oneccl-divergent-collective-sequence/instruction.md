A four-rank training job hangs in an asynchronous oneCCL allreduce. Rank 3 skips the allreduce when its local batch is empty, while the other ranks submit it and wait. Logs are aggregated without rank IDs, and a proposed fix only increases the timeout and changes worker affinity.

Write a concise root-cause analysis and validation plan to `/app/answer.md`. Address collective sequencing and completion, the rank-local evidence and communication contract to capture, a minimal reproduction, the correctness repair, and when plugin, transport, or affinity tuning becomes relevant.
