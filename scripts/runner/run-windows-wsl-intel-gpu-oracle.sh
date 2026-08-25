#!/usr/bin/env bash
set -euo pipefail

readonly job_name="uxl-windows-wsl-intel-gpu-oracle"
readonly result_path="harbor-jobs/${job_name}/result.json"
readonly oneapi_image="intel/oneapi:2026.1.0-devel-ubuntu24.04@sha256:e9db518398753434ee5aab9740a25f1d3134396a30be1569cfad8f8b0d90740c"

write_summary_and_exit() {
  local status=$?
  trap - EXIT

  if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    {
      echo "## UXL Windows/WSL Intel GPU qualification"
      echo
      echo "- Evaluator commit: \`${SKILLS_COMMIT:-unknown}\`"
      echo "- Runner: \`${RUNNER_NAME:-unknown}\`"
      echo "- Device interface: \`/dev/dxg\`"
      if [[ -f "$result_path" ]] && [[ -x .venv/bin/python ]]; then
        if .venv/bin/python scripts/check_harbor_job.py \
            "$result_path" \
            --expected-trials 1 \
            --reward-floor 1.0 >/dev/null 2>&1; then
          echo "- Oracle gate: passed"
        else
          echo "- Oracle gate: failed"
        fi
      else
        echo "- Oracle gate: result not produced"
      fi
    } >> "$GITHUB_STEP_SUMMARY"
  fi

  exit "$status"
}

trap write_summary_and_exit EXIT

if [[ ! "${SKILLS_COMMIT:-}" =~ ^[0-9a-fA-F]{40}$ ]]; then
  echo "SKILLS_COMMIT must be a full 40-character Git commit SHA" >&2
  exit 2
fi

actual_commit="$(git rev-parse HEAD)"
if [[ "${actual_commit,,}" != "${SKILLS_COMMIT,,}" ]]; then
  echo "Checked out $actual_commit instead of $SKILLS_COMMIT" >&2
  exit 3
fi

test "$(uname -m)" = "x86_64"
grep -qi microsoft /proc/sys/kernel/osrelease
test -c /dev/dxg
test -d /usr/lib/wsl/lib
python3 -c 'import sys; assert sys.version_info[:2] == (3, 12), sys.version'
docker version
docker compose version

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install harbor==0.20.0

mkdir -p harbor-jobs
source /opt/intel/oneapi/setvars.sh >/dev/null 2>&1
.venv/bin/python scripts/capture_hardware_provenance.py \
  --output harbor-jobs/runner-provenance.json \
  --require-intel-gpu

docker run --rm \
  --device /dev/dxg:/dev/dxg \
  --mount type=bind,src=/usr/lib/wsl,dst=/usr/lib/wsl,readonly \
  -e ONEAPI_DEVICE_SELECTOR=level_zero:gpu \
  "$oneapi_image" \
  bash -lc 'export LD_LIBRARY_PATH="/usr/lib/wsl/lib:${LD_LIBRARY_PATH}"; sycl-ls'

.venv/bin/harbor run \
  --path evaluation/harbor/tasks \
  --agent oracle \
  --include-task-name sycl-device-discovery-windows-wsl \
  --job-name "$job_name" \
  --jobs-dir harbor-jobs \
  --n-concurrent 1 \
  --yes

.venv/bin/python scripts/check_harbor_job.py \
  "$result_path" \
  --expected-trials 1 \
  --reward-floor 1.0
