Repair `/app/report_benchmark.py`, which currently turns benchmark CSV data into misleading speedup claims.

Preserve the command `python report_benchmark.py INPUT.csv`, writing one JSON document to stdout. The CSV columns are `case,variant,seconds,correct,warmup,scope`; `variant` is `baseline` or `candidate`, and boolean fields use `true` or `false`.

Group rows by both `case` and `scope`, sort comparisons by those fields, and emit `schema_version: "1.0"` plus a `comparisons` array. Every comparison must include `case`, `scope`, `status`, `baseline_samples`, and `candidate_samples`. Ignore warmups. A false measured correctness result makes the group `invalid-correctness`; a non-finite or non-positive measured time makes it `invalid-timing`; fewer than three measured samples for either variant makes it `insufficient-samples`. These statuses must not report a speedup. Otherwise report status `ok`, each variant's median seconds, and `speedup = baseline_median_seconds / candidate_median_seconds`.

Reject malformed input with a nonzero exit. Use only the Python standard library. The verifier uses additional datasets, so do not hard-code the supplied examples. Before finishing, explain briefly why mixing scopes, timing warmups, dropping incorrect runs, or averaging a small skewed sample can create an unsupported performance claim.
