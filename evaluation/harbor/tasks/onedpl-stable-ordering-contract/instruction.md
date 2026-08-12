The oneDPL host-parallel event ordering tool in `/app/order_events.cpp` sorts by event key, but downstream processing also requires equal-key events to preserve their original arrival order.

Run `bash /app/reproduce.sh`, diagnose the algorithm-contract mismatch, and repair `/app/order_events.cpp`. Keep oneDPL's host `par` execution policy, the key-only comparison contract, and the command-line interface. The repair must preserve the complete input permutation and stable equal-key order for other sizes and key distributions.
