# Sanitized target qualifications

This directory contains public, reviewable records for specialized execution lanes. Each JSON file proves that one immutable evaluator task passed its reward-1.0 oracle on the named lane. It does not prove that a skill improves agent behavior or that the same result applies to another device, vendor, operating system, or interface.

Raw probe output, runner names, local paths, trajectories, and private workflow logs stay access-controlled. A public record retains only reviewed lane labels, task and verifier identity, result and provenance hashes, the workflow visibility, expiry policy, and explicit limitations.

Validate the ledger with:

```powershell
python scripts/validate_target_qualifications.py
```
