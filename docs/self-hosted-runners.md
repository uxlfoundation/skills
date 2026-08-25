# Self-Hosted Runners for Specialized Hardware

Hosted runners are the default for UXL skill evaluation. Skills should remain hardware-agnostic unless maintainer evidence shows that the guidance itself must differ. Plug in specialized hardware only when faithful reproduction or verification depends on a device, backend, topology, driver, instruction set, or other capability unavailable on hosted infrastructure.

## Shared runner contract

Every specialized-hardware lane should:

1. Run only reviewed evaluator code identified by an immutable commit SHA.
2. Reject untrusted pull-request triggers and avoid exposing model credentials during runner qualification.
3. Declare the required capabilities and probe the actual environment instead of trusting labels alone.
4. Run the task oracle before spending model tokens.
5. Record non-secret hardware, software, container, driver, and task provenance.
6. Return the complete Harbor job, verifier output, task artifacts, and runner provenance.
7. Treat provisioning, network, driver, and runner failures as infrastructure failures rather than failed skill attempts.

An approved execution lane may use a private GitHub self-hosted runner, SSH, Jenkins, a laboratory scheduler, or another controlled system. The evaluator consumes the resulting Harbor artifact structure rather than depending on one provider.

## Qualification before comparison

A reward-1.0 oracle establishes that the task and runner can produce a valid result. It does not prove that a skill helps. Add matched no-skill, previous-skill, and candidate-skill model trials only when a maintainer-backed task has meaningful headroom and genuinely depends on the specialized environment.

Keep the task revision, model, reasoning effort, attempt count, timeouts, and execution environment identical across comparison arms. Quality remains the gate; token or cost reductions do not compensate for fewer verified successes.

## Import and inspect remote evidence

Download the runner's complete artifact ZIP, then import and view it locally:

```powershell
python scripts/import_harbor_artifact.py <downloaded-artifact.zip>
.\scripts\start_harbor_dashboards.ps1 -NoWsl -Restart -OpenBrowser
```

Inspect the task instruction, verifier source, trial trajectory, verifier output, submitted artifacts, and runner provenance exactly as you would for a hosted run.

## Platform adapters

The current [Intel GPU guide](intel-gpu-runner.md) and access-controlled [`uxlfoundation/uxl-skills-runner-control`](https://github.com/uxlfoundation/uxl-skills-runner-control) repository provide one concrete adapter. Additional platforms should add their own narrowly scoped guide, qualification task, runner labels, device mapping, and provenance checks while preserving this shared contract.
