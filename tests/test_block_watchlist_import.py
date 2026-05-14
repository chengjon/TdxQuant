from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from tdxquant.block_watchlist_import import (
    load_watchlist_import_file,
    plan_watchlist_import,
    sync_watchlist_import_file,
)
from tdxquant.models import ErrorCode, Result


def _write_import_file(tmp_path: Path, payload: dict[str, object]) -> Path:
    path = tmp_path / "watchlist-import.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def test_load_watchlist_import_file_normalizes_json_schema(tmp_path: Path) -> None:
    path = _write_import_file(
        tmp_path,
        {
            "schema_version": "tdx.block.watchlist.import.v1",
            "block_code": " lzxg ",
            "block_name": "自选股",
            "mode": "merge",
            "create_if_missing": True,
            "mutation_key": "import-001",
            "symbols": [
                "000001.SZ",
                {"symbol": "600519.SH", "name": "贵州茅台"},
                "000001.SZ",
            ],
        },
    )

    request = load_watchlist_import_file(path)

    assert request.schema_version == "tdx.block.watchlist.import.v1"
    assert request.block_code == "LZXG"
    assert request.block_name == "自选股"
    assert request.mode == "merge"
    assert request.create_if_missing is True
    assert request.mutation_key == "import-001"
    assert request.symbols == ["000001.SZ", "600519.SH"]
    assert request.source_path == path


def test_load_watchlist_import_file_rejects_missing_symbols(tmp_path: Path) -> None:
    path = _write_import_file(
        tmp_path,
        {
            "schema_version": "tdx.block.watchlist.import.v1",
            "block_code": "LZXG",
        },
    )

    with pytest.raises(ValueError, match="symbols"):
        load_watchlist_import_file(path)


def test_load_watchlist_import_file_rejects_malformed_symbol_object(tmp_path: Path) -> None:
    path = _write_import_file(
        tmp_path,
        {
            "schema_version": "tdx.block.watchlist.import.v1",
            "block_code": "LZXG",
            "symbols": [{"code": "000001.SZ"}],
        },
    )

    with pytest.raises(ValueError, match="symbol"):
        load_watchlist_import_file(path)


def test_plan_watchlist_import_returns_dry_run_request_summary(tmp_path: Path) -> None:
    path = _write_import_file(
        tmp_path,
        {
            "schema_version": "tdx.block.watchlist.import.v1",
            "block_code": "LZXG",
            "symbols": ["000001.SZ", "600519.SH"],
        },
    )

    plan = plan_watchlist_import(path, dry_run=True)

    assert plan["source_path"] == str(path)
    assert plan["schema_version"] == "tdx.block.watchlist.import.v1"
    assert plan["block_code"] == "LZXG"
    assert plan["mode"] == "replace"
    assert plan["dry_run"] is True
    assert plan["create_if_missing"] is False
    assert plan["symbol_count"] == 2
    assert plan["symbols"] == ["000001.SZ", "600519.SH"]


def test_sync_watchlist_import_file_delegates_to_block_sync(tmp_path: Path) -> None:
    path = _write_import_file(
        tmp_path,
        {
            "schema_version": "tdx.block.watchlist.import.v1",
            "block_code": "LZXG",
            "mode": "merge",
            "create_if_missing": True,
            "mutation_key": "import-001",
            "symbols": ["000001.SZ", {"symbol": "600519.SH"}],
        },
    )
    calls: dict[str, object] = {}

    def fake_sync(**kwargs: object) -> Result:
        calls.update(kwargs)
        return Result(ok=True, code=ErrorCode.OK, message="dry-run import", data={"sync": {"status": "dry_run"}})

    with patch("tdxquant.block_watchlist_import.sync_watchlist_to_block", side_effect=fake_sync):
        result = sync_watchlist_import_file(
            path,
            dry_run=True,
            show=False,
            observed_state={"exists": True, "symbols": ["000001.SZ"]},
            create_block=None,
            sync_members=lambda _symbols, _show: Result(ok=True, code=ErrorCode.OK, message="unused"),
            audit_dir=str(tmp_path / "audit"),
        )

    assert result.ok is True
    assert calls["block_code"] == "LZXG"
    assert calls["symbols"] == ["000001.SZ", "600519.SH"]
    assert calls["mode"] == "merge"
    assert calls["create_if_missing"] is True
    assert calls["dry_run"] is True
    assert calls["show"] is False
    assert calls["mutation_key"] == "import-001"
    assert calls["audit_dir"] == str(tmp_path / "audit")
