from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from digest_directory import directory_digest  # noqa: E402


class DirectoryDigestTests(unittest.TestCase):
    def test_matches_canonical_fixture_digest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sub").mkdir()
            (root / "a.txt").write_bytes(b"alpha")
            (root / "sub" / "b.txt").write_bytes(b"beta")

            digest = directory_digest(root)

        self.assertEqual(
            digest,
            "e081ef401f7f57797868df34df60540cd9f6f033d8b3b862e9440fafafd33c57",
        )


if __name__ == "__main__":
    unittest.main()
