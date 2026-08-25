#!/usr/bin/env python3
"""Capture reproducible, non-secret hardware-runner provenance as JSON."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path


COMMANDS = {
    "sycl_ls": ["sycl-ls"],
    "xpu_smi": ["xpu-smi", "discovery"],
    "clinfo": ["clinfo"],
    "lspci": ["lspci", "-nnk"],
    "lscpu": ["lscpu"],
    "docker_version": ["docker", "version", "--format", "{{json .}}"],
    "git_revision": ["git", "rev-parse", "HEAD"],
}


def run_command(command: list[str], timeout: int = 30) -> dict[str, object]:
    executable = shutil.which(command[0])
    if executable is None:
        return {
            "command": command,
            "available": False,
            "return_code": None,
            "output": "",
        }
    try:
        result = subprocess.run(
            [executable, *command[1:]],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
        )
        return {
            "command": command,
            "available": True,
            "return_code": result.returncode,
            "output": result.stdout.strip(),
        }
    except Exception as error:
        return {
            "command": command,
            "available": True,
            "return_code": None,
            "output": f"probe failed: {error}",
        }


def read_os_release() -> dict[str, str]:
    path = Path("/etc/os-release")
    if not path.exists():
        return {}
    values = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value.strip().strip('"')
    return values


def device_nodes() -> list[dict[str, object]]:
    nodes = []
    paths = [Path("/dev/dxg")]
    dri = Path("/dev/dri")
    if dri.is_dir():
        paths.extend(sorted(dri.iterdir()))
    for path in paths:
        if not path.exists():
            continue
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


def qualification(report: dict[str, object]) -> dict[str, bool]:
    commands = report.get("commands", {})
    sycl = commands.get("sycl_ls", {}) if isinstance(commands, dict) else {}
    lspci = commands.get("lspci", {}) if isinstance(commands, dict) else {}
    sycl_output = (
        str(sycl.get("output") or "") if isinstance(sycl, dict) else ""
    )
    pci_output = (
        str(lspci.get("output") or "") if isinstance(lspci, dict) else ""
    )
    evidence = f"{sycl_output}\n{pci_output}"
    nodes = report.get("device_nodes", [])
    return {
        "device_enumeration_succeeded": (
            (isinstance(sycl, dict) and sycl.get("return_code") == 0)
            or (isinstance(lspci, dict) and lspci.get("return_code") == 0)
        ),
        "intel_gpu_listed": (
            "intel" in evidence.casefold()
            and any(
                term in evidence.casefold()
                for term in ("gpu", "vga compatible", "display controller")
            )
        ),
        "gpu_device_interface_present": any(
            isinstance(node, dict)
            and (
                "renderd" in str(node.get("path", "")).casefold()
                or str(node.get("path", "")).casefold() == "/dev/dxg"
            )
            for node in nodes
        ),
    }


def build_report() -> dict[str, object]:
    report: dict[str, object] = {
        "schema_version": "1.0",
        "captured_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "node": platform.node(),
        },
        "os_release": read_os_release(),
        "device_nodes": device_nodes(),
        "runner": {
            key: os.environ[key]
            for key in (
                "GITHUB_ACTIONS",
                "GITHUB_REPOSITORY",
                "GITHUB_RUN_ID",
                "GITHUB_RUN_ATTEMPT",
                "RUNNER_NAME",
                "RUNNER_OS",
                "RUNNER_ARCH",
            )
            if os.environ.get(key)
        },
        "commands": {
            name: run_command(command, timeout=60)
            for name, command in COMMANDS.items()
        },
    }
    report["qualification"] = qualification(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-intel-gpu", action="store_true")
    args = parser.parse_args()

    report = build_report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    qualified = all(report["qualification"].values())
    print(f"Hardware provenance: {args.output}")
    print(f"Intel GPU qualified: {qualified}")
    return 0 if qualified or not args.require_intel_gpu else 2


if __name__ == "__main__":
    raise SystemExit(main())
