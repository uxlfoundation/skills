#!/usr/bin/env python3
"""Validate fail-closed evidence that a SYCL kernel used the intended device."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from typing import Any


CONTRACT_FIELDS = {
    "selector",
    "device_type",
    "backend",
    "vendor_id",
    "minimum_elements",
    "result_sha256",
}
OBSERVATION_FIELDS = {"selector", "device", "kernel"}
DEVICE_FIELDS = {"type", "backend", "vendor_id", "name"}
KERNEL_FIELDS = {"submitted", "waited", "async_errors", "elements", "result_sha256"}
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def exact_fields(value: Any, expected: set[str], name: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError(f"{name} must contain exactly {sorted(expected)}")
    return value


def text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip().casefold()


def sha256(value: Any, name: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value.strip()):
        raise ValueError(f"{name} must be a SHA-256 hex string")
    return value.strip().lower()


def integer(value: Any, name: str, *, positive: bool) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if (positive and value < 1) or (not positive and value < 0):
        raise ValueError(f"{name} is outside its valid range")
    return value


def boolean(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be a boolean")
    return value


def load(path: Path, name: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {name}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object")
    return value


def validate(contract_raw: dict[str, Any], observation_raw: dict[str, Any]) -> dict[str, Any]:
    contract = exact_fields(contract_raw, CONTRACT_FIELDS, "contract")
    observation = exact_fields(observation_raw, OBSERVATION_FIELDS, "observation")
    device = exact_fields(observation["device"], DEVICE_FIELDS, "observation.device")
    kernel = exact_fields(observation["kernel"], KERNEL_FIELDS, "observation.kernel")

    required = {
        "selector": text(contract["selector"], "contract.selector"),
        "device_type": text(contract["device_type"], "contract.device_type"),
        "backend": text(contract["backend"], "contract.backend"),
        "vendor_id": text(contract["vendor_id"], "contract.vendor_id"),
        "minimum_elements": integer(contract["minimum_elements"], "contract.minimum_elements", positive=True),
        "result_sha256": sha256(contract["result_sha256"], "contract.result_sha256"),
    }
    selected = {
        "type": text(device["type"], "observation.device.type"),
        "backend": text(device["backend"], "observation.device.backend"),
        "vendor_id": text(device["vendor_id"], "observation.device.vendor_id"),
        "name": text(device["name"], "observation.device.name"),
    }
    selector = text(observation["selector"], "observation.selector")
    submitted = boolean(kernel["submitted"], "observation.kernel.submitted")
    waited = boolean(kernel["waited"], "observation.kernel.waited")
    errors = kernel["async_errors"]
    if not isinstance(errors, list) or not all(isinstance(item, str) and item.strip() for item in errors):
        raise ValueError("observation.kernel.async_errors must be an array of non-empty strings")
    elements = integer(kernel["elements"], "observation.kernel.elements", positive=False)
    result_sha256 = sha256(kernel["result_sha256"], "observation.kernel.result_sha256")

    reasons = []
    if selector != required["selector"]:
        reasons.append("selector-mismatch")
    if selected["type"] != required["device_type"]:
        reasons.append("device-type-mismatch")
    if selected["backend"] != required["backend"]:
        reasons.append("backend-mismatch")
    if selected["vendor_id"] != required["vendor_id"]:
        reasons.append("vendor-mismatch")
    if not submitted:
        reasons.append("kernel-not-submitted")
    if not waited:
        reasons.append("completion-not-proven")
    if errors:
        reasons.append("async-errors")
    if elements < required["minimum_elements"]:
        reasons.append("insufficient-workload")
    if result_sha256 != required["result_sha256"]:
        reasons.append("result-mismatch")

    return {
        "schema_version": "1.0",
        "status": "accepted" if not reasons else "rejected",
        "reasons": reasons,
        "selected_device": selected,
        "kernel": {
            "submitted": submitted,
            "waited": waited,
            "async_error_count": len(errors),
            "elements": elements,
        },
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: validate_sycl_run.py CONTRACT.json OBSERVATION.json", file=sys.stderr)
        return 2
    try:
        result = validate(load(Path(argv[1]), "contract"), load(Path(argv[2]), "observation"))
    except ValueError as exc:
        print(f"SYCL evidence error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
