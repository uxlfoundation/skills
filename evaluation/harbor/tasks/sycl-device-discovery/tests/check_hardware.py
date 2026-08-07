#!/usr/bin/env python3
"""Verify that the SYCL hardware task captured real GPU evidence."""

from __future__ import annotations

import json
import os
from pathlib import Path


def main() -> int:
    workspace = Path(os.environ.get("UXL_WORKSPACE", "/app"))
    probe_path = workspace / "sycl-probe.json"
    diagnosis_path = workspace / "diagnosis.md"
    try:
        probe = json.loads(probe_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        probe = {}
    diagnosis = diagnosis_path.read_text(encoding="utf-8") if diagnosis_path.exists() else ""
    sycl_ls = probe.get("tools", {}).get("sycl-ls", {})
    devices = str(sycl_ls.get("devices") or "")
    required = ["runtime", "device", "sycl-ls", "driver", "smoke test"]
    folded = diagnosis.casefold()
    scores = {
        "reward": float(bool(sycl_ls.get("path")) and "gpu" in devices.casefold() and all(term in folded for term in required)),
        "sycl_ls_available": float(bool(sycl_ls.get("path"))),
        "gpu_visible": float("gpu" in devices.casefold()),
        "diagnosis_complete": float(all(term in folded for term in required)),
    }
    log_dir = Path(os.environ.get("UXL_VERIFIER_LOGS", "/logs/verifier"))
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "reward.json").write_text(json.dumps(scores, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(scores, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
