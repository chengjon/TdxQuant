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
from tdxquant.api.task import TdxTaskManager
from tdxquant.models import ErrorCode, Result


def _write_import_file(tmp_path: Path, payload: dict[str, object]) -> Path:
    path = tmp_path / "watchlist-import.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _write_text_import_file(tmp_path: Path, filename: str, content: str) -> Path:
    path = tmp_path / filename
    path.write_text(content, encoding="utf-8")
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


def test_load_watchlist_import_file_normalizes_csv_schema(tmp_path: Path) -> None:
    path = _write_text_import_file(
        tmp_path,
        "watchlist-import.csv",
        "\n".join(
            [
                "block_code,block_name,mode,create_if_missing,mutation_key,symbol",
                " zxg ,自选股,merge,true,csv-001,000001.sz",
                "ZXG,,,,,600519.SH",
                "ZXG,,,,,000001.SZ",
            ]
        ),
    )

    request = load_watchlist_import_file(path)

    assert request.schema_version == "tdx.block.watchlist.import.v1"
    assert request.block_code == "ZXG"
    assert request.block_name == "自选股"
    assert request.mode == "merge"
    assert request.create_if_missing is True
    assert request.mutation_key == "csv-001"
    assert request.symbols == ["000001.SZ", "600519.SH"]
    assert request.source_path == path


def test_load_watchlist_import_file_normalizes_txt_directives(tmp_path: Path) -> None:
    path = _write_text_import_file(
        tmp_path,
        "watchlist-import.txt",
        "\n".join(
            [
                "# block_code=zxg",
                "# block_name=Custom Watchlist",
                "# mode=merge",
                "# create_if_missing=false",
                "# mutation_key=txt-001",
                "000001.sz",
                "",
                "# comment-only line",
                "600519.SH",
                "000001.SZ",
            ]
        ),
    )

    request = load_watchlist_import_file(path)

    assert request.block_code == "ZXG"
    assert request.block_name == "Custom Watchlist"
    assert request.mode == "merge"
    assert request.create_if_missing is False
    assert request.mutation_key == "txt-001"
    assert request.symbols == ["000001.SZ", "600519.SH"]


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


def test_load_watchlist_import_file_rejects_csv_missing_required_columns(tmp_path: Path) -> None:
    path = _write_text_import_file(tmp_path, "missing-block-code.csv", "symbol\n000001.SZ\n")

    with pytest.raises(ValueError, match="block_code"):
        load_watchlist_import_file(path)


def test_load_watchlist_import_file_rejects_csv_conflicting_block_codes(tmp_path: Path) -> None:
    path = _write_text_import_file(
        tmp_path,
        "conflicting-block-code.csv",
        "block_code,symbol\nZXG,000001.SZ\nLZXG,600519.SH\n",
    )

    with pytest.raises(ValueError, match="multiple block_code"):
        load_watchlist_import_file(path)


def test_load_watchlist_import_file_rejects_txt_missing_block_code(tmp_path: Path) -> None:
    path = _write_text_import_file(tmp_path, "missing-block-code.txt", "000001.SZ\n600519.SH\n")

    with pytest.raises(ValueError, match="block_code"):
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


def test_task_manager_block_watchlist_import_dry_run_returns_plan(tmp_path: Path) -> None:
    path = _write_import_file(
        tmp_path,
        {
            "schema_version": "tdx.block.watchlist.import.v1",
            "block_code": "ZXG",
            "symbols": ["000001.SZ"],
        },
    )
    with (
        patch("tdxquant.api.task.TdxApiManager"),
        patch("tdxquant.api.task.TdxTradeManager"),
    ):
        manager = TdxTaskManager()
        result = manager.block_watchlist_import(input_path=str(path), dry_run=True)
    assert result.ok
    assert result.data["watchlist_import"]["source_path"] == str(path)
    assert result.data["watchlist_import"]["dry_run"] is True
    assert result.data["task"]["name"] == "block_watchlist_import"


def test_task_manager_block_watchlist_import_csv_dry_run_returns_plan(tmp_path: Path) -> None:
    path = _write_text_import_file(
        tmp_path,
        "watchlist-import.csv",
        "block_code,mode,symbol\nZXG,merge,000001.SZ\nZXG,,600519.SH\n",
    )
    with (
        patch("tdxquant.api.task.TdxApiManager"),
        patch("tdxquant.api.task.TdxTradeManager"),
    ):
        manager = TdxTaskManager()
        result = manager.block_watchlist_import(input_path=str(path), dry_run=True)
    assert result.ok
    assert result.data["watchlist_import"]["source_path"] == str(path)
    assert result.data["watchlist_import"]["block_code"] == "ZXG"
    assert result.data["watchlist_import"]["mode"] == "merge"
    assert result.data["watchlist_import"]["symbols"] == ["000001.SZ", "600519.SH"]
    assert result.data["task"]["name"] == "block_watchlist_import"


def test_task_manager_block_watchlist_import_apply_delegates_to_import_adapter(tmp_path: Path) -> None:
    path = _write_import_file(
        tmp_path,
        {
            "schema_version": "tdx.block.watchlist.import.v1",
            "block_code": "ZXG",
            "block_name": "自选股",
            "symbols": ["000001.SZ"],
        },
    )
    expected = Result(ok=True, code=ErrorCode.OK, message="applied", data={})
    with (
        patch("tdxquant.api.task.TdxApiManager"),
        patch("tdxquant.api.task.TdxTradeManager"),
        patch("tdxquant.api.task.sync_watchlist_import_request", return_value=expected) as mocked_import,
    ):
        manager = TdxTaskManager()
        result = manager.block_watchlist_import(
            input_path=str(path),
            dry_run=False,
            show=False,
            audit_dir=str(tmp_path / "audit"),
        )
    assert result is expected
    assert mocked_import.call_count == 1
    _, kwargs = mocked_import.call_args
    assert kwargs["dry_run"] is False
    assert kwargs["show"] is False
    assert kwargs["audit_dir"] == str(tmp_path / "audit")
