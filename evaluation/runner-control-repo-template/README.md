# Private Specialized-Hardware Runner Control Repository — Intel GPU Example

This directory demonstrates the reusable private-control-repository pattern with the current Intel GPU adapter. The security and evidence contract applies to any specialized hardware: accept only reviewed immutable evaluator revisions, avoid untrusted triggers, qualify the runner before model trials, and return complete provenance and Harbor artifacts. Platform-specific workflows must supply their own task, labels, device mapping, and oracle.

These copy-ready examples control personal or laboratory Intel GPU runners. Do not enable them unchanged in the public skills repository or claim that either device contract applies to other platforms.

For a new vendor or laboratory target, start with `specialized-target-oracle.yml` and copy `target-adapter.example.json` to `target-adapter.json`. Follow the exact [specialized target adapter guide](../../docs/target-device-adapter.md). The generic runner executes reviewed host probes, validates the declared task and hardware class, runs one Harbor oracle, and returns a common evidence layout. A passing run also emits `qualification-record.json`; review that sanitized file before copying it into the public qualification ledger.

Both workflows accept only a full 40-character commit SHA, check out `uxlfoundation/skills` at that immutable revision, run a hardware oracle, and upload the complete job directory. They do not run a model experiment or accept pull-request triggers.

- `intel-gpu-oracle.yml` contains the native-Linux `/dev/dri` implementation.
- `windows-wsl-intel-gpu-oracle.yml` is the thin dispatcher used for the private Windows/WSL machine. The hardware-specific implementation lives in the reviewed `skills` checkout at `scripts/runner/run-windows-wsl-intel-gpu-oracle.sh`.
- `specialized-target-oracle.yml` is the vendor-neutral dispatcher. Machine-specific settings live in the private `target-adapter.json`, not in the public evaluator implementation.

## Create the control repository

1. Create a new private GitHub repository, such as `uxl-skills-runner-control`.
2. Copy the contents of this template directory into its root, including only the workflow for the intended platform.
3. Review and commit the workflow on the default branch.
4. Keep Actions disabled for forks and do not add `pull_request`, `pull_request_target`, or public `repository_dispatch` triggers.
5. If organization administration is available, place the runner in a runner group restricted to this repository.

All templates accept commits already reachable from public `uxlfoundation/skills` main. To run an unmerged candidate, copy `approved-commits.example.txt` to `approved-commits.txt`, add the reviewed full SHA, and commit that approval in the private control repository first. A workflow input alone cannot authorize arbitrary public-repository code on the private machine.

The workflow pins its GitHub-authored actions to the full commits for `actions/checkout` v6.0.2 and `actions/upload-artifact` v7.0.1 as published on August 18, 2026. Use Dependabot or a reviewed manual change to update those pins. These action releases require a recent GitHub Actions runner; install the exact current runner offered by the control repository's settings page.

## Register one reviewed job

On a qualified native-Linux GPU host:

1. Open **Settings → Actions → Runners → New self-hosted runner** in the private control repository.
2. Select Linux x64 and use the exact download and checksum commands GitHub displays.
3. Register the runner interactively with custom labels `uxl,sycl,gpu,intel-gpu,personal-lab` and the `--ephemeral` option.
4. Start it with `./run.sh`. Do not install it as a service for the initial rollout.
5. From the control repository's **Actions** page, dispatch **UXL Intel GPU oracle** with a reviewed 40-character commit SHA from `uxlfoundation/skills`.

Do not paste the one-time registration token into chat, a report, a repository secret, or a helper script. Enter it only while running GitHub's registration command. The runner connects to GitHub over outbound HTTPS; no inbound firewall rule is required.

## Read the result

The job summary records the exact evaluator commit and whether the reward-1.0 oracle gate passed. The artifact is named `uxl-intel-gpu-oracle-<commit>` and contains:

- `runner-provenance.json` with non-secret host and GPU evidence;
- the Harbor `result.json`;
- the trial trajectory, verifier output, and collected artifacts;
- `sycl-probe.json` and the diagnosis produced inside the Harbor environment.

Download the artifact ZIP and import it into an evaluator checkout, then restart the local results dashboard:

```powershell
python scripts/import_harbor_artifact.py <downloaded-artifact.zip>
.\scripts\start_harbor_dashboards.ps1 -NoWsl -Restart -OpenBrowser
```

If the artifact contains a passing `qualification-record.json`, the importer validates its evidence hashes and stages the sanitized record under `harbor-jobs/qualification-review/`. It does not publish anything. Review that candidate before copying it into the public qualification ledger.

An ephemeral runner deregisters after one job. It does not erase its `_work` directory or Docker layers. Preserve the artifact first, then inspect and clean the dedicated runner workspace according to the host owner's policy.

For the Windows/WSL lane, install the GitHub runner inside WSL once, then start a waiting one-job runner from a `skills` checkout:

```powershell
.\scripts\runner\start-ephemeral-wsl-runner.ps1 `
  -Repository owner/private-runner-control `
  -Labels 'uxl,sycl,gpu,intel-gpu,windows-wsl,personal-lab'
```

See [Private Machine Runner](../../docs/private-machine-runner.md) for the same pattern in project-independent terms.

## Promotion beyond the oracle

Do not add model credentials or skill-comparison steps until this oracle passes on the intended device. The first successful run proves the runner contract, not that a skill improves agent behavior. A later model workflow must keep the host, task revision, image, model, reasoning effort, and attempt count identical across no-skill, previous-skill, and candidate-skill arms.
