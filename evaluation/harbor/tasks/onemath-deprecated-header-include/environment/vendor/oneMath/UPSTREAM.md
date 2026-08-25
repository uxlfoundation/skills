# Upstream fixture

The headers under `include/` are copied verbatim from UXL Foundation oneMath commit `be58ee06edbd9d98ec001c7ebcb8001b8b167a9a`, immediately before the repair for issue #623.

- Source: https://github.com/uxlfoundation/oneMath/tree/be58ee06edbd9d98ec001c7ebcb8001b8b167a9a
- Incident: https://github.com/uxlfoundation/oneMath/issues/623
- Accepted fix: https://github.com/uxlfoundation/oneMath/pull/625
- License: Apache-2.0, as retained in each header

Only the affected compatibility header and its installed namespace-alias target are retained. The evaluator stubs unrelated domain headers because this incident occurs during preprocessing and include resolution, before oneMath or SYCL declarations are used.
