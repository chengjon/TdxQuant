#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


DEFAULT_EXTERNAL_ROOT = Path(r"D:\MyCode3\tdx")

KNOWN_EXCLUDED_TESTS = {
    "pingan.py": "Historical PingAn scratch adapter that depends on the old BrokerAdapter package shape.",
}

ACTIVE_CHANGE_COVERAGE = {
    "add-securities-trader-gateway": {
        "specs": ("tdx-securities-trader-gateway",),
        "archive_suffix": "add-securities-trader-gateway",
    },
    "implement-pingan-win32-trading-adapter": {
        "specs": ("pingan-runtime-discovery", "pingan-win32-order-entry"),
        "archive_suffix": "implement-pingan-win32-trading-adapter",
    },
    "implement-tdx-wsl-windows-bridge": {
        "specs": (
            "tdx-windows-bridge",
            "tdx-data-api-bridge",
            "tdx-formula-bridge",
            "tdx-trading-hid-bridge",
        ),
        "archive_suffix": "implement-tdx-wsl-windows-bridge",
    },
}


def _relative_files(root: Path, pattern: str) -> list[str]:
    if not root.exists():
        return []
    values: list[str] = []
    for path in root.rglob(pattern):
        if not path.is_file():
            continue
        if any(part in {"__pycache__", ".pytest_cache", ".git"} for part in path.parts):
            continue
        values.append(path.relative_to(root).as_posix())
    return sorted(values)


def _top_level_files(root: Path) -> list[str]:
    if not root.exists():
        return []
    return sorted(path.name for path in root.iterdir() if path.is_file())


def _sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _archive_exists(root: Path, suffix: str) -> bool:
    archive_root = root / "openspec" / "changes" / "archive"
    if not archive_root.exists():
        return False
    return any(path.is_dir() and (path.name == suffix or path.name.endswith(f"-{suffix}")) for path in archive_root.iterdir())


def _active_external_changes(external_root: Path) -> list[str]:
    changes_root = external_root / "openspec" / "changes"
    if not changes_root.exists():
        return []
    return sorted(path.name for path in changes_root.iterdir() if path.is_dir() and path.name != "archive")


def audit_external_tdx_merge(root: Path, external_root: Path) -> dict[str, Any]:
    root = root.resolve()
    external_root = external_root.resolve()
    errors: list[str] = []

    if not external_root.exists():
        errors.append(f"external root does not exist: {external_root}")

    external_py = _relative_files(external_root / "tdxquant", "*.py")
    current_py = set(_relative_files(root / "tdxquant", "*.py"))
    missing_py = [path for path in external_py if path not in current_py]
    if missing_py:
        errors.append(f"missing external tdxquant python sources: {missing_py}")

    external_tests = _relative_files(external_root / "tests", "*.py")
    current_tests = set(_relative_files(root / "tests", "*.py"))
    missing_tests = [path for path in external_tests if path not in current_tests]
    unexpected_missing_tests = [path for path in missing_tests if path not in KNOWN_EXCLUDED_TESTS]
    if unexpected_missing_tests:
        errors.append(f"missing external tests without exclusion: {unexpected_missing_tests}")

    external_runtime_files = _top_level_files(external_root / "runtime")
    current_runtime_files = set(_top_level_files(root / "runtime"))
    missing_runtime_files = [name for name in external_runtime_files if name not in current_runtime_files]
    if missing_runtime_files:
        errors.append(f"missing external runtime top-level files: {missing_runtime_files}")

    external_hid = external_root / "hardware" / "tdx_hid_keyboard" / "tdx_hid_keyboard.ino"
    current_hid = root / "firmware" / "arduino" / "tdx_hid_keyboard" / "tdx_hid_keyboard.ino"
    hid_hashes = {"external": _sha256(external_hid), "current": _sha256(current_hid)}
    hid_firmware_matches = hid_hashes["external"] is not None and hid_hashes["external"] == hid_hashes["current"]
    if not hid_firmware_matches:
        errors.append("HID firmware asset is missing or does not match external source")

    plugin_assets = [
        root / "docs" / "tdx-plugin-dll-function-reference.md",
        root / "examples" / "tdx_plugin_tcalc" / "PluginTCalcFunc.h",
        root / "examples" / "tdx_plugin_tcalc" / "TCalcFuncSets.cpp",
        root / "openspec" / "specs" / "tdx-plugin-dll-example" / "spec.md",
    ]
    missing_plugin_assets = [str(path.relative_to(root).as_posix()) for path in plugin_assets if not path.exists()]
    if missing_plugin_assets:
        errors.append(f"missing plugin DLL example assets: {missing_plugin_assets}")

    active_changes = _active_external_changes(external_root)
    uncovered_active_changes: list[str] = []
    active_change_details: dict[str, Any] = {}
    for change in active_changes:
        coverage = ACTIVE_CHANGE_COVERAGE.get(change)
        if not coverage:
            uncovered_active_changes.append(change)
            active_change_details[change] = {"covered": False, "reason": "no coverage mapping"}
            continue
        missing_specs = [
            spec for spec in coverage["specs"] if not (root / "openspec" / "specs" / spec / "spec.md").exists()
        ]
        archive_present = _archive_exists(root, str(coverage["archive_suffix"]))
        covered = not missing_specs and archive_present
        if not covered:
            uncovered_active_changes.append(change)
        active_change_details[change] = {
            "covered": covered,
            "missing_specs": missing_specs,
            "archive_present": archive_present,
        }
    if uncovered_active_changes:
        errors.append(f"external active OpenSpec changes are not covered: {uncovered_active_changes}")

    giant_json_files = [
        path.relative_to(external_root).as_posix()
        for path in external_root.rglob("*.json")
        if path.is_file() and path.stat().st_size >= 1024 * 1024
    ] if external_root.exists() else []

    return {
        "valid": not errors,
        "problem_count": len(errors),
        "errors": errors,
        "external_root": str(external_root),
        "root": str(root),
        "tdxquant_python": {
            "external_count": len(external_py),
            "missing_count": len(missing_py),
            "missing": missing_py,
        },
        "tests": {
            "external_count": len(external_tests),
            "missing": missing_tests,
            "known_excluded": {
                path: KNOWN_EXCLUDED_TESTS[path] for path in missing_tests if path in KNOWN_EXCLUDED_TESTS
            },
            "unexpected_missing": unexpected_missing_tests,
        },
        "runtime": {
            "external_top_level_file_count": len(external_runtime_files),
            "missing_top_level_files": missing_runtime_files,
        },
        "hid_firmware": {
            "matches": hid_firmware_matches,
            "hashes": hid_hashes,
        },
        "plugin_dll_example": {
            "registered": not missing_plugin_assets,
            "missing_assets": missing_plugin_assets,
        },
        "openspec": {
            "external_active_changes": active_changes,
            "active_change_details": active_change_details,
            "uncovered_active_changes": uncovered_active_changes,
        },
        "excluded_evidence": {
            "giant_json_count": len(giant_json_files),
            "giant_json_samples": giant_json_files[:10],
            "policy": "Do not import raw real-machine dumps without redaction and size screening.",
        },
    }


def _summary(report: dict[str, Any]) -> str:
    status = "valid" if report["valid"] else "invalid"
    return (
        f"{status}; problems={report['problem_count']}; "
        f"missing_py={report['tdxquant_python']['missing_count']}; "
        f"unexpected_missing_tests={len(report['tests']['unexpected_missing'])}; "
        f"runtime_missing={len(report['runtime']['missing_top_level_files'])}; "
        f"hid_matches={report['hid_firmware']['matches']}; "
        f"plugin_registered={report['plugin_dll_example']['registered']}; "
        f"uncovered_changes={len(report['openspec']['uncovered_active_changes'])}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit external D:\\MyCode3\\tdx merge coverage.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Current TdxQuant repository root")
    parser.add_argument(
        "--external-root",
        type=Path,
        default=DEFAULT_EXTERNAL_ROOT,
        help="External tdx project root to audit",
    )
    parser.add_argument("--json", action="store_true", dest="json_output", help="Print JSON report")
    args = parser.parse_args(argv)

    report = audit_external_tdx_merge(args.root, args.external_root)
    if args.json_output:
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    else:
        print(_summary(report))
        for error in report["errors"]:
            print(error, file=sys.stderr)
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
