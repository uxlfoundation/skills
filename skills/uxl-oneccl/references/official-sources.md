# Official Sources

Use these first when answering oneCCL questions.

- oneCCL GitHub: https://github.com/uxlfoundation/oneCCL
- oneCCL documentation: https://uxlfoundation.github.io/oneCCL/index.html
- oneCCL specification: https://oneapi-spec.uxlfoundation.org/specifications/oneapi/latest/elements/oneccl/source/
- oneCCL releases: https://github.com/uxlfoundation/oneCCL/releases
- ALCF Aurora oneCCL guide: https://docs.alcf.anl.gov/aurora/data-science/frameworks/oneCCL/

## Incident Ledger

- [Issue #174: zero-count topology `alltoallv`](https://github.com/uxlfoundation/oneCCL/issues/174): the final zero-count peer could retain a one-past device pointer on Aurora GPUs.
- [Accepted repair](https://github.com/uxlfoundation/oneCCL/commit/993878af0301b2cd8c9c1e56a45d1d5273938b0d): canonicalizes zero-count send, receive, and temporary segments to null/empty.
- [oneCCL 2021.17 release](https://github.com/uxlfoundation/oneCCL/releases/tag/2021.17): contains the repair.

Incident links and release inclusion last verified 2026-08-27.

## Refresh Rule

If the task depends on the NCCL-like C API, plugin behavior, GPU support, PyTorch/Horovod integration, or release status, verify current upstream docs or releases.
