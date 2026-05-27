from __future__ import annotations

import json
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT = REPO_ROOT / "scripts" / "audit_external_tdx_merge.py"


def _write(path: Path, content: str = "sample\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def _run_audit(root: Path, external_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--root",
            str(root),
            "--external-root",
            str(external_root),
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def _create_required_assets(root: Path, external_root: Path) -> None:
    _write(external_root / "tdxquant" / "api" / "bridge.py")
    _write(root / "tdxquant" / "api" / "bridge.py")
    _write(external_root / "tests" / "test_existing.py")
    _write(root / "tests" / "test_existing.py")
    _write(external_root / "tests" / "pingan.py")
    _write(external_root / "runtime" / "command-catalog.json", "{}")
    _write(root / "runtime" / "command-catalog.json", "{}")
    _write(external_root / "hardware" / "tdx_hid_keyboard" / "tdx_hid_keyboard.ino", "firmware")
    _write(root / "firmware" / "arduino" / "tdx_hid_keyboard" / "tdx_hid_keyboard.ino", "firmware")
    _write(root / "docs" / "tdx-plugin-dll-function-reference.md")
    _write(root / "examples" / "tdx_plugin_tcalc" / "PluginTCalcFunc.h")
    _write(root / "examples" / "tdx_plugin_tcalc" / "TCalcFuncSets.cpp")
    _write(root / "openspec" / "specs" / "tdx-plugin-dll-example" / "spec.md")

    for change in (
        "add-securities-trader-gateway",
        "implement-pingan-win32-trading-adapter",
        "implement-tdx-wsl-windows-bridge",
    ):
        (external_root / "openspec" / "changes" / change).mkdir(parents=True, exist_ok=True)

    for spec in (
        "tdx-securities-trader-gateway",
        "pingan-runtime-discovery",
        "pingan-win32-order-entry",
        "tdx-windows-bridge",
        "tdx-data-api-bridge",
        "tdx-formula-bridge",
        "tdx-trading-hid-bridge",
    ):
        _write(root / "openspec" / "specs" / spec / "spec.md")

    for archive in (
        "2026-05-03-add-securities-trader-gateway",
        "2026-05-03-implement-pingan-win32-trading-adapter",
        "2026-05-03-implement-tdx-wsl-windows-bridge",
    ):
        (root / "openspec" / "changes" / "archive" / archive).mkdir(parents=True, exist_ok=True)


class ExternalTdxMergeAuditTests(unittest.TestCase):
    def test_audit_accepts_expected_current_migration_shape(self) -> None:
        with TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            root = base / "current"
            external_root = base / "external"
            _create_required_assets(root, external_root)

            result = _run_audit(root, external_root)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["valid"], True)
        self.assertEqual(payload["problem_count"], 0)
        self.assertEqual(payload["tdxquant_python"]["missing"], [])
        self.assertEqual(payload["tests"]["unexpected_missing"], [])
        self.assertEqual(payload["tests"]["known_excluded"], {"pingan.py": payload["tests"]["known_excluded"]["pingan.py"]})
        self.assertEqual(payload["runtime"]["missing_top_level_files"], [])
        self.assertEqual(payload["hid_firmware"]["matches"], True)
        self.assertEqual(payload["plugin_dll_example"]["registered"], True)
        self.assertEqual(payload["openspec"]["uncovered_active_changes"], [])

    def test_audit_rejects_unexpected_missing_candidates(self) -> None:
        with TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            root = base / "current"
            external_root = base / "external"
            _create_required_assets(root, external_root)
            _write(external_root / "tdxquant" / "new_module.py")
            _write(external_root / "tests" / "test_new_module.py")
            _write(external_root / "runtime" / "new-runtime.json", "{}")
            _write(external_root / "hardware" / "tdx_hid_keyboard" / "tdx_hid_keyboard.ino", "external firmware")
            (external_root / "openspec" / "changes" / "new-active-change").mkdir(parents=True)

            result = _run_audit(root, external_root)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["valid"], False)
        self.assertIn("new_module.py", payload["tdxquant_python"]["missing"])
        self.assertIn("test_new_module.py", payload["tests"]["unexpected_missing"])
        self.assertIn("new-runtime.json", payload["runtime"]["missing_top_level_files"])
        self.assertEqual(payload["hid_firmware"]["matches"], False)
        self.assertIn("new-active-change", payload["openspec"]["uncovered_active_changes"])


if __name__ == "__main__":
    unittest.main()
