# SYCL transitive-link task activation: 2026-08-16

## Outcome

`sycl-transitive-target-link-contract` is implemented as the harder `hosted-toolchain` task. It preserves a multi-target CMake architecture: a SYCL object library, a host pipeline static library that embeds its objects, and a final executable. The object library's private `UXL::SYCL` usage requirement is enough to compile its source with `-fsycl` but does not establish the link contract for the final consumer.

The accepted repair propagates the interface target through the pipeline as a target-scoped link usage requirement. The verifier rejects global CMake flags, hardcoded oneAPI paths, `link_directories`, and `libsycl` filenames. It independently inspects the generated final link command for `icpx -fsycl`, checks dynamic resolution of `libsycl`, and runs the public case plus four hidden cases on the selected CPU device.

## Discrimination

| Evaluation | Job | Reward | Exceptions | Evidence |
| --- | --- | ---: | ---: | --- |
| Direct unchanged baseline | local container | 0 | not applicable | SYCL object compiles; final link fails with unresolved `sycl::_V1` references |
| Direct oracle | local container | 1 | not applicable | Target-scoped repair; public plus four hidden cases pass |
| Harbor unchanged no-op | `sycl-transitive-baseline-20260816-r1` | 0.000 | 0 | No repair or diagnosis artifact |
| Harbor oracle | `sycl-transitive-oracle-20260816-r1` | 1.000 | 0 | Four hidden cases; one real OpenCL CPU device |

## Scope and next gate

The task evaluates build-system reasoning and authentic compiler/linker/runtime behavior, not device performance. It is hardware-agnostic at the skill level and inherits the hosted image's OpenCL CPU runner requirement. The subsequent [three-attempt calibration](2026-08-16-sycl-transitive-link-calibration-final.md) reached full reward in all arms and used more candidate tokens than no skill, so the task is classified as `smoke` / `ceiling`.
