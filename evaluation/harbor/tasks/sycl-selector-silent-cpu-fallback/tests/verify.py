#!/usr/bin/env python3
"""Behavioral verifier for fail-closed SYCL runtime evidence."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile


CONTRACT = {
    "selector": "level_zero:gpu",
    "device_type": "gpu",
    "backend": "level_zero",
    "vendor_id": "0x8086",
    "minimum_elements": 1024,
    "result_sha256": "a" * 64,
}
OBSERVATION = {
    "selector": " LEVEL_ZERO:GPU ",
    "device": {
        "type": "GPU",
        "backend": "Level_Zero",
        "vendor_id": "0X8086",
        "name": "Intel Test GPU",
    },
    "kernel": {
        "submitted": True,
        "waited": True,
        "async_errors": [],
        "elements": 4096,
        "result_sha256": "A" * 64,
    },
}


def run_validator(script: Path, contract, observation, *, expect_success=True):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        contract_path = root / "contract.json"
        observation_path = root / "observation.json"
        contract_path.write_text(json.dumps(contract), encoding="utf-8")
        observation_path.write_text(json.dumps(observation), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(script), str(contract_path), str(observation_path)],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    if expect_success:
        assert result.returncode == 0, result.stderr
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise AssertionError(f"stdout is not one JSON document: {result.stdout!r}") from exc
    assert result.returncode != 0, result.stdout
    return None


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit("usage: verify.py SCRIPT")
    script = Path(argv[1])

    accepted = run_validator(script, CONTRACT, OBSERVATION)
    assert accepted == {
        "schema_version": "1.0",
        "status": "accepted",
        "reasons": [],
        "selected_device": {
            "type": "gpu",
            "backend": "level_zero",
            "vendor_id": "0x8086",
            "name": "intel test gpu",
        },
        "kernel": {
            "submitted": True,
            "waited": True,
            "async_error_count": 0,
            "elements": 4096,
        },
    }, accepted

    mutations = [
        (("selector",), "*:gpu", "selector-mismatch"),
        (("device", "type"), "cpu", "device-type-mismatch"),
        (("device", "backend"), "opencl", "backend-mismatch"),
        (("device", "vendor_id"), "0x10de", "vendor-mismatch"),
        (("kernel", "submitted"), False, "kernel-not-submitted"),
        (("kernel", "waited"), False, "completion-not-proven"),
        (("kernel", "async_errors"), ["asynchronous kernel failure"], "async-errors"),
        (("kernel", "elements"), 128, "insufficient-workload"),
        (("kernel", "result_sha256"), "b" * 64, "result-mismatch"),
    ]
    for path, value, reason in mutations:
        observation = copy.deepcopy(OBSERVATION)
        target = observation
        for part in path[:-1]:
            target = target[part]
        target[path[-1]] = value
        report = run_validator(script, CONTRACT, observation)
        assert report["status"] == "rejected", report
        assert report["reasons"] == [reason], report

    combined = copy.deepcopy(OBSERVATION)
    combined["selector"] = "default"
    combined["device"]["type"] = "cpu"
    combined["kernel"]["waited"] = False
    combined["kernel"]["result_sha256"] = "b" * 64
    report = run_validator(script, CONTRACT, combined)
    assert report["reasons"] == [
        "selector-mismatch",
        "device-type-mismatch",
        "completion-not-proven",
        "result-mismatch",
    ], report

    malformed = copy.deepcopy(OBSERVATION)
    del malformed["kernel"]["waited"]
    run_validator(script, CONTRACT, malformed, expect_success=False)
    malformed_contract = copy.deepcopy(CONTRACT)
    malformed_contract["minimum_elements"] = True
    run_validator(script, malformed_contract, OBSERVATION, expect_success=False)

    print("SYCL device evidence verifier passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
