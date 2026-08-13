import copy
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_script("validate_harbor_suites")
RENDERER = load_script("render_harbor_suites")


class HarborSuiteManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = VALIDATOR.load_manifest()

    def test_repository_manifest_is_valid(self) -> None:
        self.assertEqual(VALIDATOR.validate_manifest(self.manifest), [])

    def test_missing_planned_coverage_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        suite = manifest["suites"][0]
        suite["tasks"] = suite["tasks"][:2]

        errors = VALIDATOR.validate_manifest(manifest)

        self.assertTrue(any("target_task_count" in error for error in errors))
        self.assertTrue(any("no planned task coverage" in error for error in errors))

    def test_implemented_task_requires_a_real_task_directory(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        task = manifest["suites"][0]["tasks"][0]
        task["status"] = "implemented"
        task["calibration"] = "headroom"

        errors = VALIDATOR.validate_manifest(manifest)

        self.assertIn(
            "onednn-matmul-memory-descriptors: implemented task directory is missing",
            errors,
        )

    def test_task_requires_reproduction_audit_fields(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        task = manifest["suites"][0]["tasks"][0]
        del task["reproduction"]
        del task["origin"]
        del task["workflow"]
        del task["hardware"]

        errors = VALIDATOR.validate_manifest(manifest)

        self.assertTrue(any(".reproduction" in error for error in errors))
        self.assertTrue(any(".origin" in error for error in errors))
        self.assertTrue(any(".workflow" in error for error in errors))
        self.assertTrue(any(".hardware" in error for error in errors))

    def test_fixture_cannot_claim_live_workflow_stages(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        task = manifest["suites"][0]["tasks"][3]
        task["workflow"] = ["reproduce", "investigate", "verify"]

        errors = VALIDATOR.validate_manifest(manifest)

        self.assertTrue(
            any("fixture evaluation cannot claim reproduce or verify" in error for error in errors)
        )

    def test_debugging_capability_requires_planned_live_end_to_end_coverage(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        suite = manifest["suites"][0]
        for task in suite["tasks"]:
            if task["reproduction"] == "live":
                task["covers"] = [
                    item for item in task["covers"] if item != "backend-and-parity-triage"
                ]

        errors = VALIDATOR.validate_manifest(manifest)

        self.assertTrue(
            any("debugging capabilities lack planned live end-to-end coverage" in error for error in errors)
        )

    def test_target_environment_must_match_hardware(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        task = manifest["suites"][0]["tasks"][4]
        task["hardware"] = "generic-cpu"

        errors = VALIDATOR.validate_manifest(manifest)

        self.assertTrue(
            any("requires hardware 'target-device'" in error for error in errors)
        )

    def test_generated_matrix_matches_manifest(self) -> None:
        output = ROOT / "evaluation" / "harbor" / "CAPABILITY_MATRIX.md"
        self.assertEqual(output.read_text(encoding="utf-8"), RENDERER.render(self.manifest))

    def test_generated_matrix_summarizes_calibration_health(self) -> None:
        rendered = RENDERER.render(self.manifest)

        self.assertIn("## Evaluator health", rendered)
        self.assertIn(
            "| `uxl-onetbb` | 7 | 7 | 2 | 5 | 0 | 0 | 0 |",
            rendered,
        )


if __name__ == "__main__":
    unittest.main()
