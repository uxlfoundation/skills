# Official Sources

Use these first when answering oneDPL questions.

Last verified: 2026-09-04
Verified by: Codex maintainer-outreach refresh against current upstream documentation

- oneDPL GitHub: https://github.com/uxlfoundation/oneDPL
- oneDPL documentation: https://uxlfoundation.github.io/oneDPL/index.html
- oneDPL execution policies: https://oneapi-spec.uxlfoundation.org/specifications/oneapi/latest/elements/onedpl/source/parallel_api/execution_policies
- oneDPL execution policies (current oneAPI specification): https://uxlfoundation.github.io/oneAPI-spec/spec/elements/oneDPL/source/parallel_api/execution_policies.html
- oneDPL specification: https://oneapi-spec.uxlfoundation.org/specifications/oneapi/latest/elements/onedpl/source/
- oneDPL releases: https://github.com/uxlfoundation/oneDPL/releases
- oneDPL validation testing notes: https://github.com/uxlfoundation/oneDPL/blob/main/CONTRIBUTING.md

The September 2026 refresh confirmed that the upstream documentation continues to separate standard-aligned host policies from SYCL device policies and assigns queue/error-handling responsibilities to the caller. Release-specific restrictions remain deliberately outside the skill and must be checked upstream.

## Refresh Rule

If the task depends on device execution policy behavior, CUDA/AMD/Intel GPU support, iterator support, or release-specific algorithm fixes, verify current upstream docs or releases.
