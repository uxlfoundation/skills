#!/usr/bin/env python3
"""Collect SYCL device evidence and execute a deterministic GPU smoke test."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


TOOLS = [
    "icpx",
    "icx",
    "clang++",
    "dpcpp",
    "cmake",
    "ninja",
    "sycl-ls",
    "xpu-smi",
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


def run_command(
    command: list[str],
    *,
    timeout: int = 30,
    environment: dict[str, str] | None = None,
) -> dict[str, object]:
    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
            env=environment,
        )
        return {
            "command": command,
            "return_code": result.returncode,
            "output": result.stdout.strip(),
        }
    except Exception as error:
        return {
            "command": command,
            "return_code": None,
            "output": f"probe failed: {error}",
        }


def device_nodes() -> list[dict[str, object]]:
    dri = Path("/dev/dri")
    if not dri.is_dir():
        return []
    nodes = []
    for path in sorted(dri.iterdir()):
        try:
            stat = path.stat()
            nodes.append(
                {
                    "path": str(path),
                    "mode": oct(stat.st_mode & 0o777),
                    "uid": stat.st_uid,
                    "gid": stat.st_gid,
                }
            )
        except OSError as error:
            nodes.append({"path": str(path), "error": str(error)})
    return nodes


def tool_report() -> dict[str, dict[str, object]]:
    tools: dict[str, dict[str, object]] = {}
    for tool in TOOLS:
        path = shutil.which(tool)
        details: dict[str, object] = {"path": path}
        if path and tool in {"icpx", "icx", "clang++", "dpcpp", "cmake"}:
            details["version"] = run_command([path, "--version"], timeout=15)
        elif path and tool in {"sycl-ls", "xpu-smi", "clinfo"}:
            command = [path]
            if tool == "xpu-smi":
                command.append("discovery")
            details["discovery"] = run_command(command, timeout=20)
        tools[tool] = details
    return tools


def run_gpu_smoke(source: Path) -> dict[str, object]:
    compiler = shutil.which("icpx") or shutil.which("dpcpp")
    if not compiler:
        return {
            "compiler": None,
            "compile": {"return_code": None, "output": "No SYCL compiler found"},
            "run": {"return_code": None, "output": "Smoke test not run"},
        }

    binary = Path("/tmp/uxl-sycl-gpu-smoke")
    compile_result = run_command(
        [compiler, "-fsycl", "-O2", str(source), "-o", str(binary)],
        timeout=180,
    )
    if compile_result["return_code"] != 0:
        return {
            "compiler": compiler,
            "compile": compile_result,
            "run": {"return_code": None, "output": "Smoke test did not compile"},
        }

    runtime_environment = os.environ.copy()
    runtime_environment["ONEAPI_DEVICE_SELECTOR"] = "level_zero:gpu"
    run_result = run_command(
        [str(binary)], timeout=120, environment=runtime_environment
    )
    return {
        "compiler": compiler,
        "selector": runtime_environment["ONEAPI_DEVICE_SELECTOR"],
        "compile": compile_result,
        "run": run_result,
    }


def build_report(source: Path) -> dict[str, object]:
    return {
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": sys.version.split()[0],
        },
        "device_nodes": device_nodes(),
        "tools": tool_report(),
        "selected_environment": {
            key: os.environ[key] for key in ENV_KEYS if os.environ.get(key)
        },
        "gpu_smoke": run_gpu_smoke(source),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        help="Write the JSON report to this path instead of standard output.",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("/app/gpu_smoke.cpp"),
        help="SYCL smoke-test source file.",
    )
    args = parser.parse_args()

    report = build_report(args.source)
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
