from __future__ import annotations

import sys
import subprocess
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

    def test_git_digest_ignores_generated_files_and_normalizes_line_endings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "core.autocrlf", "true"], check=True)
            (root / ".gitattributes").write_text("*.txt text eol=lf\n", encoding="utf-8")
            (root / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
            content = root / "content"
            content.mkdir()
            source = content / "a.txt"
            source.write_bytes(b"alpha\r\nbeta\r\n")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            original = directory_digest(content)

            (content / "__pycache__").mkdir()
            (content / "__pycache__" / "generated.pyc").write_bytes(b"generated")
            source.write_bytes(b"alpha\nbeta\n")
            normalized = directory_digest(content)

            (content / "new.txt").write_text("new\n", encoding="utf-8")
            changed = directory_digest(content)

        self.assertEqual(original, normalized)
        self.assertEqual(
            original,
            "406cf35b51a60c1dad89af88729d4c8109866076bea2318521024bb0675d411d",
        )
        self.assertNotEqual(original, changed)


if __name__ == "__main__":
    unittest.main()
