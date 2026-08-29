# Specialized target qualification contract

A target qualification proves one narrow fact: an immutable evaluator task passed its reward-1.0 oracle on a declared specialized execution lane. It does not prove that a skill helps, that another device is equivalent, or that a performance claim is valid.

## Public record

Accepted records live under `evaluation/harbor/results/qualifications/<qualification_id>.json` and validate against `schemas/target-qualification.schema.json`. Each record retains:

- the exact task commit plus Git-filtered task and verifier content digests;
- reviewed lane, vendor, device, interface, operating-system, and architecture labels;
- one completed, error-free oracle attempt with reward 1.0;
- hashes of the private result and provenance files;
- workflow visibility, expiry policy, and explicit limitations.

The public record deliberately excludes raw probe output, runner names, local paths, trajectories, credentials, network details, and private workflow URLs.

## Lifecycle

1. A private control repository dispatches a reviewed immutable evaluator revision.
2. The target adapter runs fixed host probes and the declared Harbor oracle.
3. Only a passing run emits `qualification-record.json` alongside the private artifacts.
4. The artifact importer validates the schema and evidence hashes, then stages the sanitized record under ignored local storage.
5. A reviewer checks the public labels and limitations, then copies only that record into the public ledger.
6. CI validates the schema and task contract. The dashboard reports the latest record for each lane as current, age-expired, or repository-changed.

A changed task or verifier invalidates current status without deleting the historical record. Age expiry requires the same lane to rerun its oracle. Failed qualifications remain private diagnostic evidence and are not committed as passing records.

Validate the ledger with:

```powershell
python scripts/validate_target_qualifications.py
```
