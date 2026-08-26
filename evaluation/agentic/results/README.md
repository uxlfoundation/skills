# Retained agentic benchmark results

Files in this directory are correctness-passing summaries from the frozen `uxl-agentic-reference-v1` contract. The filename identifies the date, machine, executor, and retriever.

The 2026-08-25 GLOW run used CPython 3.13.13 on Windows 11 with 28 logical CPUs, one warmup, five measured attempts, and four maximum workers. Every route, answer, cancellation control, and exception control passed.

These are prototype-selection measurements, not portable performance claims. Compare raw values only within the same dated environment and contract. Setup and conversion costs must stay in scope for a candidate integration.
