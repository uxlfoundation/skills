#!/usr/bin/env python3
"""Collect a safe, minimal SYCL toolchain report."""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys


TOOLS = [
    "icpx",
    "icx",
    "clang++",
    "dpcpp",
    "cmake",
    "ninja",
    "sycl-ls",
    "nvidia-smi",
    "rocminfo",
    "clinfo",
]

ENV_KEYS = [
    "CMAKE_PREFIX_PATH",
    "CPATH",
    "LIBRARY_PATH",
    "LD_LIBRARY_PATH",
    "PATH",
    "ONEAPI_DEVICE_SELECTOR",
    "SYCL_DEVICE_FILTER",
]


def command_output(command: list[str], timeout: int = 5) -> str:
    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
        )
    except Exception as exc:  # noqa: BLE001 - report probe failure, do not fail hard
        return f"probe failed: {exc}"
    return result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""


def main() -> int:
    tools: dict[str, dict[str, str | None]] = {}
    for tool in TOOLS:
        path = shutil.which(tool)
        tools[tool] = {"path": path}
        if path and tool in {"icpx", "icx", "clang++", "dpcpp", "cmake"}:
            tools[tool]["version"] = command_output([path, "--version"])
        elif path and tool == "sycl-ls":
            tools[tool]["devices"] = command_output([path])

    report = {
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": sys.version.split()[0],
        },
        "tools": tools,
        "selected_environment": {key: os.environ.get(key) for key in ENV_KEYS if os.environ.get(key)},
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
