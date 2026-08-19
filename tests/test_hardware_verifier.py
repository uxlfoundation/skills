from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


CHECKER_PATH = (
    Path(__file__).parents[1]
    / "evaluation"
    / "harbor"
    / "tasks"
    / "sycl-device-discovery"
    / "tests"
    / "check_hardware.py"
)
SPEC = importlib.util.spec_from_file_location("sycl_hardware_checker", CHECKER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load checker: {CHECKER_PATH}")
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


def passing_probe() -> dict[str, object]:
    return {
        "tools": {
            "sycl-ls": {
                "path": "/opt/intel/oneapi/compiler/latest/bin/sycl-ls",
                "discovery": {
                    "return_code": 0,
                    "output": "[level_zero:gpu:0] Intel(R) Data Center GPU Max",
                },
            }
        },
        "device_nodes": [{"path": "/dev/dri/renderD128"}],
        "gpu_smoke": {
            "compile": {"return_code": 0},
            "run": {
                "return_code": 0,
                "output": (
                    "device_type=gpu\n"
                    "device_vendor=Intel(R) Corporation\n"
                    "result=pass"
                ),
            },
        },
    }


class HardwareVerifierTests(unittest.TestCase):
    def test_accepts_real_gpu_execution_evidence(self) -> None:
        diagnosis = "runtime device sycl-ls driver smoke test"
        scores = CHECKER.evaluate(passing_probe(), diagnosis)
        self.assertEqual(scores["reward"], 1.0)
        self.assertTrue(all(value == 1.0 for value in scores.values()))

    def test_rejects_compilation_without_gpu_execution(self) -> None:
        probe = passing_probe()
        probe["gpu_smoke"]["run"] = {
            "return_code": 1,
            "output": "device_type=cpu\nresult=fail",
        }
        scores = CHECKER.evaluate(
            probe, "runtime device sycl-ls driver smoke test"
        )
        self.assertEqual(scores["reward"], 0.0)
        self.assertEqual(scores["smoke_executed"], 0.0)
        self.assertEqual(scores["smoke_selected_intel_gpu"], 0.0)


if __name__ == "__main__":
    unittest.main()
