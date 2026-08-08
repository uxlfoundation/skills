Repair `/app/compare_reduction.py`, which currently applies only a blanket absolute tolerance and silently drops evidence it cannot compare.

Preserve the command `python compare_reduction.py INPUT.json`, writing one JSON document to stdout. The input must be an object containing exactly `reference`, `candidate`, `atol`, and `rtol`. The two arrays must be non-empty, equal-length arrays of finite JSON numbers. Tolerances must be finite, non-negative numbers. Booleans are not numbers for this contract.

Compare each candidate value with its reference using the combined floating-point reduction tolerance `abs(candidate - reference) <= atol + rtol * abs(reference)`. Report `schema_version: "1.0"`, `status` (`pass` or `fail`), `sample_count`, `mismatch_count`, `atol`, `rtol`, `max_absolute_error`, and `worst_index`. `worst_index` is the lowest index having the largest absolute error. Reject malformed JSON, extra or missing fields, invalid values, empty arrays, or unequal lengths with a nonzero exit.

Use only the Python standard library. Do not round values before comparison, silently discard non-finite values, truncate unequal inputs, or special-case visible data. The verifier exercises large-magnitude relative tolerance, near-zero absolute tolerance, boundary values, and malformed inputs.
