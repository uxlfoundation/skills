from __future__ import annotations

import unittest

from scripts.capture_hardware_provenance import qualification


class HardwareProvenanceTests(unittest.TestCase):
    def test_accepts_visible_intel_gpu_and_render_node(self) -> None:
        report = {
            "commands": {
                "sycl_ls": {
                    "return_code": 0,
                    "output": "[level_zero:gpu:0] Intel(R) Data Center GPU Max",
                },
                "lspci": {"return_code": 0, "output": ""},
            },
            "device_nodes": [{"path": "/dev/dri/renderD128"}],
        }
        self.assertTrue(all(qualification(report).values()))

    def test_rejects_cpu_only_runner(self) -> None:
        report = {
            "commands": {
                "sycl_ls": {
                    "return_code": 0,
                    "output": "[opencl:cpu:0] Intel(R) Xeon(R)",
                },
                "lspci": {"return_code": 0, "output": ""},
            },
            "device_nodes": [],
        }
        self.assertFalse(all(qualification(report).values()))


if __name__ == "__main__":
    unittest.main()
