# Add a Specialized Target Machine

This is the exact path for adding a GPU, CPU, accelerator, or distributed lab system to the UXL Skills Evaluator. GitHub dispatches a reviewed job; the target machine qualifies itself and runs one Harbor oracle; GitHub retains the artifact; the public dashboard receives only reviewed summary evidence.

## 1. Add the evaluator task

In `uxlfoundation/skills`:

1. Add a Harbor task under `evaluation/harbor/tasks/<task-name>/` with a deterministic reward-1.0 oracle.
2. Declare it in `evaluation/harbor/suites.json` with the owning skill and one of `target-cpu`, `target-gpu`, `target-device`, or `target-distributed` as its hardware class.
3. Make the verifier prove the relevant device behavior inside the task environment. A host label or inventory string is not proof.
4. Run `python scripts/validate_harbor_suites.py` and the task oracle on the target machine.

## 2. Create the private dispatcher

1. Create a small private GitHub repository. It is a security boundary for the machine, not a second evaluator implementation.
2. Copy `.github/workflows/specialized-target-oracle.yml` from `evaluation/runner-control-repo-template/`.
3. Copy `target-adapter.example.json` to `target-adapter.json`.
4. Replace the example workflow `runs-on` labels and the JSON fields with this machine's contract.
5. Keep only `workflow_dispatch` or a tightly controlled schedule. Never add public pull-request triggers.

The adapter JSON names one fixed skill/task pair, reviewed public display labels, an expiry period, the required routing labels, host probe commands, required probe output patterns, and the Harbor executable. The `publication` block is the only machine description copied into the generated sanitized record; keep it concise and free of names, serial numbers, local paths, or network details. Probe output is hashed by default. Set `publish_output` only after confirming that the command cannot expose sensitive machine data.

Validate the file before registering a runner:

```bash
python3 scripts/runner/run_target_adapter.py \
  --config /path/to/target-adapter.json \
  --source-root . \
  --expected-commit 0000000000000000000000000000000000000000 \
  --output /tmp/uxl-target-validation \
  --validate-only
```

## 3. Prepare and register the machine

1. Install Git, Python 3.12, Docker or the task's declared container runtime, Harbor 0.20.0, the vendor driver/runtime, and the GitHub Actions runner.
2. Verify the probe commands manually as the dedicated runner account.
3. Register the Actions runner only to the private dispatcher repository or a repository-restricted runner group.
4. Use `--ephemeral` for a one-job runner and assign the exact labels declared by the workflow and adapter.
5. Allow outbound HTTPS to GitHub and required image registries. Do not open an inbound firewall port.

For a Windows host using WSL, the reusable launcher is:

```powershell
.\scripts\runner\start-ephemeral-wsl-runner.ps1 `
  -Repository owner/private-runner-control `
  -Labels 'uxl,target-gpu,windows-wsl,trusted-lab'
```

Other environments may start `./run.sh --ephemeral` directly or use their laboratory scheduler, provided the same contract and artifact layout are preserved.

## 4. Approve and dispatch one job

1. Choose a full evaluator commit SHA already on `uxlfoundation/skills` main.
2. For an unmerged candidate, review it first and add the full SHA to `approved-commits.txt` in the private dispatcher. This makes approval an auditable control-repository change.
3. Start the ephemeral runner and confirm that GitHub shows it online.
4. Open the private repository's **Actions** page, select **UXL specialized target oracle**, choose **Run workflow**, and paste the approved SHA.

Anyone with permission to run that private workflow can queue the fixed qualification job. They cannot select an arbitrary command or task through workflow inputs. The runner still verifies the exact checkout, real host probes, declared task ownership and hardware class, and the reward-1.0 oracle.

## 5. Review the result

The private artifact contains:

- `qualification-summary.md`;
- `runner-provenance.json`, with configuration and probe-output hashes;
- `qualification-record.json`, emitted only after a passing oracle and ready for privacy review;
- `probe-logs/`, with access-controlled raw probe output for diagnosis;
- `oracle.log`;
- the complete `harbor-jobs/<job>/` directory.

Download and inspect it from a trusted evaluator checkout:

```powershell
python scripts/import_harbor_artifact.py <artifact.zip>
.\scripts\start_harbor_dashboards.ps1 -NoWsl -Restart -OpenBrowser
```

The importer verifies that the candidate is schema-valid and that its result and provenance hashes match the downloaded artifact. It stages only the sanitized candidate under `harbor-jobs/qualification-review/`; it never publishes it. Review its public labels and limitations, then copy that one JSON file into `evaluation/harbor/results/qualifications/` and run the repository validators.

A pass qualifies the lane; it does not prove that a skill helps. Run matched no-skill, previous-skill, and candidate-skill trials only after a target-dependent task has meaningful headroom. Retain the sanitized evaluation-cell JSON in the public ledger; keep `probe-logs/`, raw trajectories, and machine details access-controlled.

For that later comparison, use `scripts/compare_harbor_skill.ps1` and pass the qualification file with `-HardwareProbePath <artifact>/runner-provenance.json`. The evaluation cell stores its SHA-256 digest, not the private probe contents.

## Machine-specific versus shared pieces

| Shared in `uxlfoundation/skills` | Specific to the target machine/control repo |
| --- | --- |
| Task, oracle, verifier, policy, adapter schema, adapter runner, evidence-cell schema | Workflow labels, adapter JSON, probe commands, vendor runtime, device mapping, runner registration |
| Public static dashboard build on GitHub-hosted runners | Harbor execution and raw job artifacts on the specialized machine |
| CI validation of sanitized retained evidence | Private job logs, probe outputs, local caches, credentials, cleanup policy |
