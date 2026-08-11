# Maintainer failure intake

Use this template to source a real Harbor triage task from an owning project. A submitted scenario is not automatically accepted; it must be minimizable, redistributable, and verifiable in an available environment.

## Project and provenance

- UXL component:
- Maintainer or issue owner:
- Upstream issue, pull request, or incident reference:
- Affected revision or release:
- Fixed revision, if known:
- May the reproducer and artifacts be stored in this public repository?

## Failure contract

- Expected behavior:
- Actual behavior:
- Exact command that reproduces the failure:
- Smallest known source, data, and configuration:
- Stable failure signal or exit condition:
- Known nondeterminism or retry requirements:

## Environment

- Operating system and architecture:
- Compiler, runtime, library, driver, and backend versions:
- Required CPU, GPU, accelerator, topology, or instruction set:
- Can a free hosted runner reproduce it?
- If not, where can a trusted runner access the required target?
- Network, dataset, secret, or licensing constraints:

## Triage and verification

- Evidence a maintainer normally collects first:
- Useful tracing or verbose modes:
- Allowed repair surface:
- Deterministic correctness check:
- Performance check, only if the failure is performance-related:
- Known misleading diagnosis or unsafe workaround:

## Evaluator conversion

The task author must preserve the original behavior while removing unrelated project complexity. The Harbor task must let the agent reproduce, investigate, repair, and verify the issue. Its verifier must accept correct alternative repairs and reject answers or patches that only mention expected keywords.

Record the final task as `maintainer-incident` or `upstream-regression` in `suites.json`. Do not use those origins without a durable reference and maintainer-reviewable reproduction contract.
