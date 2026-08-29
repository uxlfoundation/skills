# Cross-project SYCL build/debug skill maintainer review

Review state: not requested

Reviewed commit: pending

## Review request

Please review `uxl-sycl-build-debug` for technical accuracy, useful cross-project scope, vendor-neutral wording, and suitability for shared UXL working-group ownership.

The skill classifies configure, compile, link, runtime-load, and device-discovery failures; gathers a safe toolchain report; separates compiler/backend/package/runtime hypotheses; and routes library-specific failures to project skills.

Why this helps: agents get a common evidence-first workflow across UXL repositories without one project's device stack becoming the default story for every vendor.

The initial ask is a 45-minute cross-project review, agreement on routing boundaries, and a small owner group—not a commitment to operate every target machine.

## Evidence to inspect

- Instructions: `skills/uxl-sycl-build-debug/SKILL.md`
- Official sources: `skills/uxl-sycl-build-debug/references/official-sources.md`
- Probe: `skills/uxl-sycl-build-debug/scripts/sycl_probe.py`
- Prompt evals: `skills/uxl-sycl-build-debug/evals/evals.json`
- Public card: `skill-cards/uxl-sycl-build-debug.md`
- Harbor matrix: `evaluation/harbor/suites.json` (`uxl-sycl-build-debug`)

Coverage state: all 8 declared tasks are implemented; 1 discriminating task retains measured headroom; 1 live task reproduces a oneDNN maintainer incident. The target-GPU discovery tasks qualify execution lanes and are not represented as skill-benefit evidence. Sources were checked on 2026-08-25.

## Suggested reviewers

Please route through the UXL Open Source Working Group and include maintainers from projects using SYCL plus representatives for the compiler/runtime/device lanes being described. No individual has been assigned or contacted by this repository.

## Decision checklist

- [ ] Failure phases and probe guidance are technically accurate.
- [ ] Cross-project routing boundaries are clear.
- [ ] Compiler, backend, runtime, and hardware wording is vendor-neutral.
- [ ] Source ledger is sufficient and current.
- [ ] Eval prompts and Harbor tasks are realistic and balanced.
- [ ] A working-group team will own or periodically review the shared skill.

Decision: pending

Reviewer/date: pending

Required changes: pending
