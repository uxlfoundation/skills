# Private Machine Runner

This is the reusable pattern used to let GitHub send one reviewed evaluation job to a privately owned machine without exposing that machine to public pull requests.

## How it works

1. The public project stores the evaluator, qualification task, and the script that performs the work.
2. A small private GitHub repository stores only a manually triggered workflow. It accepts a full Git commit SHA, checks out that exact public revision, runs its script, and uploads the results.
3. The private machine runs a GitHub Actions runner inside WSL. It is registered as **ephemeral**, so it accepts one job and then deregisters automatically.
4. The workflow checks the real hardware before doing evaluation work. Labels route the job, but device probes and a passing oracle are the proof that the machine is suitable.
5. GitHub retains the job log and artifact. The private machine needs outbound HTTPS, not an inbound firewall port.

The private repository is a security boundary, not a second product repository. Do not attach a personal runner directly to a public repository: a malicious pull request or changed workflow could otherwise execute on the machine.

## What another project needs

- A private control repository with manual or tightly controlled scheduled triggers only.
- A Linux x64 GitHub Actions runner installed in the chosen WSL distribution.
- A public, immutable evaluator revision and a script that can qualify the host before running the real job.
- Distinct labels for the operating system, hardware, and trust tier.
- Artifact upload configured with `if: always()` so failure evidence is retained.
- No model credentials until the hardware oracle passes and the workflow has been reviewed.

Start a one-job runner from a public checkout with:

```powershell
.\scripts\runner\start-ephemeral-wsl-runner.ps1 `
  -Repository owner/private-runner-control `
  -Labels 'project,gpu,windows-wsl,personal-lab'
```

The launcher refuses public repositories, requests a short-lived registration token through GitHub CLI, starts the WSL runner in a hidden process, and confirms that GitHub reports it online. After a host reboot, rerun the same command: if the local ephemeral configuration and its offline GitHub registration still agree, the launcher resumes them without requesting a new registration or creating a duplicate. It writes only non-secret local state under `tmp/runner/`. The Actions runner software must already be installed at `/home/uxlrunner/uxl-runner`, or the path must be supplied with `-RunnerRoot`.

The private workflow should stay small:

```yaml
on:
  workflow_dispatch:
    inputs:
      source_commit:
        required: true
        type: string

jobs:
  evaluate:
    runs-on: [self-hosted, linux, x64, project, gpu, windows-wsl, personal-lab]
    steps:
      - run: |
          if [[ ! "$SOURCE_COMMIT" =~ ^[0-9a-fA-F]{40}$ ]]; then
            exit 2
          fi
        env:
          SOURCE_COMMIT: ${{ inputs.source_commit }}
      - uses: actions/checkout@<reviewed-full-action-sha>
        with:
          repository: owner/public-project
          ref: ${{ inputs.source_commit }}
          persist-credentials: false
      - run: bash scripts/run-hardware-evaluation.sh
      - if: always()
        uses: actions/upload-artifact@<reviewed-full-action-sha>
        with:
          path: results
```

Pin every third-party action to a reviewed full commit SHA. The evaluator script should independently verify the checked-out SHA, device interface, driver/runtime visibility, container mapping, tool versions, and oracle result.

## UXL example

UXL's private dispatcher is `uxlfoundation/uxl-skills-runner-control`. The reusable launcher and Windows/WSL Intel GPU oracle are in this repository under [`scripts/runner/`](../scripts/runner/), and the copy-ready dispatcher is [`evaluation/runner-control-repo-template/.github/workflows/windows-wsl-intel-gpu-oracle.yml`](../evaluation/runner-control-repo-template/.github/workflows/windows-wsl-intel-gpu-oracle.yml). The current runner uses `/dev/dxg`, the read-only WSL runtime libraries at `/usr/lib/wsl`, and the `sycl-device-discovery-windows-wsl` oracle.

For a new vendor or laboratory target, use the [specialized target adapter](target-device-adapter.md) and [`specialized-target-oracle.yml`](../evaluation/runner-control-repo-template/.github/workflows/specialized-target-oracle.yml). It keeps the workflow fixed, records probe hashes, rejects secret-like configuration fields, verifies task ownership and hardware class, and accepts only a public-main revision or an explicitly approved candidate SHA.
