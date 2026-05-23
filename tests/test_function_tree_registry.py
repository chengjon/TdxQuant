from __future__ import annotations

import subprocess
import sys
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "validate_function_tree_registry.py"


def _run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )


def _write_function_tree(root: Path, body: str) -> None:
    (root / "FUNCTION_TREE.md").write_text(textwrap.dedent(body).strip() + "\n", encoding="utf-8")


class FunctionTreeRegistryValidatorTests(unittest.TestCase):
    def test_current_function_tree_passes_validation(self) -> None:
        result = _run_validator(REPO_ROOT)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("rows=", result.stdout)
        self.assertIn("[已实现]", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_validator_rejects_missing_evidence_or_boundary(self) -> None:
        cases = {
            "missing evidence": "| A-01 | sample | `[已实现]` |  | implemented boundary |",
            "missing boundary": "| A-01 | sample | `[已实现]` | source.py |  |",
        }
        for name, row in cases.items():
            with self.subTest(name=name), TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                _write_function_tree(
                    root,
                    f"""
                    | ID | 功能 | 状态 | 证据 | 边界 |
                    | --- | --- | --- | --- | --- |
                    {row}
                    """,
                )

                result = _run_validator(root)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("A-01", result.stderr)

    def test_validator_rejects_duplicate_ids_bad_status_and_unsafe_pending_rows(self) -> None:
        cases = {
            "duplicate id": """
                | ID | 功能 | 状态 | 证据 | 边界 |
                | --- | --- | --- | --- | --- |
                | A-01 | sample | `[已实现]` | source.py | implemented boundary |
                | A-01 | sample again | `[部分实现]` | tests.py | partial boundary |
            """,
            "bad status": """
                | ID | 功能 | 状态 | 证据 | 边界 |
                | --- | --- | --- | --- | --- |
                | A-01 | sample | `[完成]` | source.py | implemented boundary |
            """,
            "unsafe pending row": """
                | ID | 功能 | 状态 | 证据 | 边界 |
                | --- | --- | --- | --- | --- |
                | A-01 | sample | `[已设计/待实现]` | design.md | ready for users |
            """,
        }
        for name, body in cases.items():
            with self.subTest(name=name), TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                _write_function_tree(root, body)

                result = _run_validator(root)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("A-01", result.stderr)

    def test_validator_rejects_competing_root_roadmap(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_function_tree(
                root,
                """
                | ID | 功能 | 状态 | 证据 | 边界 |
                | --- | --- | --- | --- | --- |
                | A-01 | sample | `[已实现]` | source.py | implemented boundary |
                """,
            )
            (root / "ROADMAP.md").write_text("competing roadmap\n", encoding="utf-8")

            result = _run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ROADMAP.md", result.stderr)


if __name__ == "__main__":
    unittest.main()
