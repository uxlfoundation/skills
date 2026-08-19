#!/usr/bin/env python3
"""Verify that the SYCL hardware task captured real Intel GPU execution."""

from __future__ import annotations

import json
import os
from pathlib import Path


def evaluate(probe: dict[str, object], diagnosis: str) -> dict[str, float]:
    """Return reward components for captured probe evidence and diagnosis."""
    sycl_ls = probe.get("tools", {}).get("sycl-ls", {})
    discovery = sycl_ls.get("discovery", {})
    devices = str(discovery.get("output") or "")
    smoke = probe.get("gpu_smoke", {})
    compile_result = smoke.get("compile", {})
    run_result = smoke.get("run", {})
    run_output = str(run_result.get("output") or "")
    nodes = probe.get("device_nodes", [])

    required = ["runtime", "device", "sycl-ls", "driver", "smoke test"]
    folded = diagnosis.casefold()
    checks = {
        "sycl_ls_available": bool(sycl_ls.get("path")),
        "intel_gpu_listed": (
            "gpu" in devices.casefold() and "intel" in devices.casefold()
        ),
        "render_node_visible": any(
            "renderd" in str(node.get("path", "")).casefold()
            for node in nodes
            if isinstance(node, dict)
        ),
        "smoke_compiled": compile_result.get("return_code") == 0,
        "smoke_executed": run_result.get("return_code") == 0,
        "smoke_selected_intel_gpu": (
            "device_type=gpu" in run_output.casefold()
            and "device_vendor=intel" in run_output.casefold()
        ),
        "smoke_result_correct": "result=pass" in run_output.casefold(),
        "diagnosis_complete": all(term in folded for term in required),
    }
    return {
        "reward": float(all(checks.values())),
        **{name: float(passed) for name, passed in checks.items()},
    }


def main() -> int:
    workspace = Path(os.environ.get("UXL_WORKSPACE", "/app"))
    probe_path = workspace / "sycl-probe.json"
    diagnosis_path = workspace / "diagnosis.md"
    try:
        probe = json.loads(probe_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        probe = {}
    diagnosis = (
        diagnosis_path.read_text(encoding="utf-8")
        if diagnosis_path.exists()
        else ""
    )

    scores = evaluate(probe, diagnosis)

    log_dir = Path(os.environ.get("UXL_VERIFIER_LOGS", "/logs/verifier"))
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "reward.json").write_text(
        json.dumps(scores, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(scores, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
