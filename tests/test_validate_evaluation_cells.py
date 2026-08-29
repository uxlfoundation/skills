from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_evaluation_cells as ledger  # noqa: E402
from tests.test_evaluation_cell import valid_record  # noqa: E402


class EvaluationCellLedgerTests(unittest.TestCase):
    def write_suites(self, root: Path) -> Path:
        path = root / "suites.json"
        path.write_text(
            json.dumps(
                {
                    "suites": [
                        {
                            "skill": "uxl-onetbb",
                            "tasks": [{"name": "onetbb-join-node-ordering"}],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_accepts_empty_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cells_root = root / "cells"
            cells_root.mkdir()
            count, errors = ledger.validate_ledger(cells_root, self.write_suites(root))
        self.assertEqual(count, 0)
        self.assertEqual(errors, [])

    def test_accepts_declared_record_and_rejects_wrong_filename(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cells_root = root / "cells"
            cells_root.mkdir()
            suites = self.write_suites(root)
            record = valid_record()
            good = cells_root / f"{record['cell_id']}.json"
            good.write_text(json.dumps(record), encoding="utf-8")
            count, errors = ledger.validate_ledger(cells_root, suites)
            self.assertEqual((count, errors), (1, []))

            renamed = copy.deepcopy(record)
            renamed["cell_id"] = "another-cell"
            good.write_text(json.dumps(renamed), encoding="utf-8")
            _, errors = ledger.validate_ledger(cells_root, suites)
        self.assertTrue(any("filename must be another-cell.json" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
