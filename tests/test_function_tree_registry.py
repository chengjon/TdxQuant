from __future__ import annotations

import json
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "validate_function_tree_registry.py"


def _run_validator(root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--root", str(root), *extra_args],
        check=False,
        capture_output=True,
        text=True,
    )


def _write_function_tree(root: Path, body: str) -> None:
    (root / "FUNCTION_TREE.md").write_text(textwrap.dedent(body).strip() + "\n", encoding="utf-8")


def _write_openspec_change(root: Path, change_id: str, *, archived: bool) -> None:
    if archived:
        change_dir = root / "openspec" / "changes" / "archive" / f"2026-05-23-{change_id}"
    else:
        change_dir = root / "openspec" / "changes" / change_id
    change_dir.mkdir(parents=True)
    (change_dir / ".openspec.yaml").write_text("id: test\n", encoding="utf-8")


def _current_function_tree_rows() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for line in (REPO_ROOT / "FUNCTION_TREE.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        columns = [column.strip() for column in line.strip().strip("|").split("|")]
        if len(columns) < 5 or columns[0] in {"ID", "---"}:
            continue
        rows[columns[0]] = {
            "feature": columns[1],
            "status": columns[2],
            "evidence": columns[3],
            "boundary": columns[4],
        }
    return rows


class FunctionTreeRegistryValidatorTests(unittest.TestCase):
    def test_current_function_tree_passes_validation(self) -> None:
        result = _run_validator(REPO_ROOT)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("rows=", result.stdout)
        self.assertIn("[已实现]", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_validator_json_report_summarizes_current_function_tree(self) -> None:
        result = _run_validator(REPO_ROOT, "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["valid"], True)
        self.assertGreater(payload["row_count"], 0)
        self.assertEqual(payload["problem_count"], 0)
        self.assertEqual(payload["errors"], [])
        self.assertIn("[已实现]", payload["status_counts"])
        self.assertEqual(result.stderr, "")

    def test_subscription_long_run_control_nodes_are_registered_as_implemented(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("B-16", "E-09"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[已实现]`")
                self.assertIn("SubscriptionWatchBackgroundController.restart", combined)
                self.assertIn("supervisor_tick", combined)
                self.assertIn("supervisor_run", combined)
                self.assertIn("statefile ownership", combined)
                self.assertIn("operator", combined)
                self.assertIn("不代表 live provider availability", combined)
                self.assertIn("不代表 broker readiness", combined)
                self.assertIn("不代表交易 readiness", combined)

    def test_pingan_task_plan_boundary_evidence_is_registered(self) -> None:
        row = _current_function_tree_rows()["D-07"]
        combined = f"{row['evidence']} {row['boundary']}"

        self.assertEqual(row["status"], "`[部分实现]`")
        self.assertIn("catalog plan --entry task-buy --view summary", combined)
        self.assertIn("catalog plan --entry task-sell --view summary", combined)
        self.assertIn("catalog plan --entry task-confirm-current --view summary", combined)
        self.assertIn("non_executing_catalog_plan", combined)
        self.assertIn("不执行 task/trade/report/bundle step", combined)
        self.assertIn("不代表 broker readiness", combined)
        self.assertIn("不代表交易安全审批", combined)

    def test_validator_json_report_returns_errors_without_stderr(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_function_tree(
                root,
                """
                | ID | 功能 | 状态 | 证据 | 边界 |
                | --- | --- | --- | --- | --- |
                | A-01 | sample | `[已实现]` |  | implemented boundary |
                """,
            )

            result = _run_validator(root, "--json")

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["valid"], False)
        self.assertEqual(payload["row_count"], 1)
        self.assertEqual(payload["problem_count"], 1)
        self.assertIn("A-01", payload["errors"][0])
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

    def test_validator_accepts_archived_and_active_openspec_evidence(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_function_tree(
                root,
                """
                | ID | 功能 | 状态 | 证据 | 边界 |
                | --- | --- | --- | --- | --- |
                | A-01 | archived | `[已实现]` | source.py；OpenSpec `archived-change` | implemented boundary |
                | A-02 | active | `[部分实现]` | tests.py；OpenSpec `active-change` | partial boundary |
                """,
            )
            _write_openspec_change(root, "archived-change", archived=True)
            _write_openspec_change(root, "active-change", archived=False)

            result = _run_validator(root)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("rows=2", result.stdout)

    def test_validator_rejects_missing_openspec_evidence(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_function_tree(
                root,
                """
                | ID | 功能 | 状态 | 证据 | 边界 |
                | --- | --- | --- | --- | --- |
                | A-01 | sample | `[已实现]` | source.py；OpenSpec `missing-change` | implemented boundary |
                """,
            )

            result = _run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("A-01", result.stderr)
            self.assertIn("missing-change", result.stderr)

    def test_validator_accepts_existing_local_evidence_paths(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "tests").mkdir()
            (root / "scripts").mkdir()
            (root / "tests" / "test_registry.py").write_text("def test_ok():\n    pass\n", encoding="utf-8")
            (root / "scripts" / "validate_registry.py").write_text("print('ok')\n", encoding="utf-8")
            _write_function_tree(
                root,
                """
                | ID | 功能 | 状态 | 证据 | 边界 |
                | --- | --- | --- | --- | --- |
                | A-01 | sample | `[已实现]` | `tests/test_registry.py`；`scripts/validate_registry.py` | implemented boundary |
                """,
            )

            result = _run_validator(root)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("rows=1", result.stdout)

    def test_validator_rejects_missing_local_evidence_path(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_function_tree(
                root,
                """
                | ID | 功能 | 状态 | 证据 | 边界 |
                | --- | --- | --- | --- | --- |
                | A-01 | sample | `[已实现]` | `tests/missing_registry_test.py` | implemented boundary |
                """,
            )

            result = _run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("A-01", result.stderr)
            self.assertIn("tests/missing_registry_test.py", result.stderr)

    def test_validator_ignores_non_literal_evidence_paths(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_function_tree(
                root,
                """
                | ID | 功能 | 状态 | 证据 | 边界 |
                | --- | --- | --- | --- | --- |
                | A-01 | sample | `[已实现]` | `build_subscription_watch_status_summary()`；`catalog validate --kind all`；`runtime/trade-audits/*`；`runtime/watchlist-imports/zxg-watchlist-import.example.json/csv/txt` | implemented boundary |
                """,
            )

            result = _run_validator(root)

            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
