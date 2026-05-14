from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from .block_sync import sync_watchlist_to_block
from .models import Result

WATCHLIST_IMPORT_SCHEMA_VERSION = "tdx.block.watchlist.import.v1"
SUPPORTED_IMPORT_MODES = {"replace", "merge"}


@dataclass(frozen=True)
class WatchlistImportRequest:
    schema_version: str
    block_code: str
    symbols: list[str]
    source_path: Path
    block_name: str | None = None
    mode: str = "replace"
    create_if_missing: bool = False
    mutation_key: str | None = None


def load_watchlist_import_file(path: str | Path) -> WatchlistImportRequest:
    source_path = Path(path)
    try:
        payload = json.loads(source_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"watchlist import file is not valid JSON: {source_path}") from exc
    except OSError as exc:
        raise ValueError(f"unable to read watchlist import file: {source_path}") from exc
    if not isinstance(payload, Mapping):
        raise ValueError("watchlist import file must contain a JSON object")
    return _parse_watchlist_import_payload(payload, source_path=source_path)


def plan_watchlist_import(path: str | Path, *, dry_run: bool = True) -> dict[str, Any]:
    request = load_watchlist_import_file(path)
    return {
        "schema_version": request.schema_version,
        "source_path": str(request.source_path),
        "block_code": request.block_code,
        "block_name": request.block_name,
        "mode": request.mode,
        "create_if_missing": request.create_if_missing,
        "dry_run": bool(dry_run),
        "mutation_key": request.mutation_key,
        "symbol_count": len(request.symbols),
        "symbols": list(request.symbols),
    }


def sync_watchlist_import_file(
    path: str | Path,
    *,
    observed_state: dict[str, Any] | Result | Callable[[], dict[str, Any] | Result],
    create_block: Callable[[], Result] | None,
    sync_members: Callable[[list[str], bool], Result],
    dry_run: bool = False,
    show: bool = True,
    audit_dir: str | None = None,
) -> Result:
    request = load_watchlist_import_file(path)
    return sync_watchlist_to_block(
        block_code=request.block_code,
        symbols=list(request.symbols),
        mode=request.mode,
        create_if_missing=request.create_if_missing,
        dry_run=dry_run,
        show=show,
        mutation_key=request.mutation_key,
        observed_state=observed_state,
        create_block=create_block,
        sync_members=sync_members,
        audit_dir=audit_dir,
    )


def _parse_watchlist_import_payload(payload: Mapping[str, Any], *, source_path: Path) -> WatchlistImportRequest:
    schema_version = _required_str(payload, "schema_version")
    if schema_version != WATCHLIST_IMPORT_SCHEMA_VERSION:
        raise ValueError(f"unsupported watchlist import schema_version: {schema_version}")

    block_code = _required_str(payload, "block_code").upper()
    block_name = _optional_str(payload.get("block_name"))
    mode = (_optional_str(payload.get("mode")) or "replace").lower()
    if mode not in SUPPORTED_IMPORT_MODES:
        raise ValueError(f"unsupported watchlist import mode: {mode}")

    raw_create_if_missing = payload.get("create_if_missing", False)
    if not isinstance(raw_create_if_missing, bool):
        raise ValueError("watchlist import create_if_missing must be a boolean")

    symbols = _normalize_import_symbols(payload.get("symbols"))
    mutation_key = _optional_str(payload.get("mutation_key"))
    return WatchlistImportRequest(
        schema_version=schema_version,
        block_code=block_code,
        block_name=block_name,
        mode=mode,
        create_if_missing=raw_create_if_missing,
        mutation_key=mutation_key,
        symbols=symbols,
        source_path=source_path,
    )


def _normalize_import_symbols(raw_symbols: Any) -> list[str]:
    if not isinstance(raw_symbols, list) or not raw_symbols:
        raise ValueError("watchlist import symbols must be a non-empty array")
    normalized: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(raw_symbols):
        symbol = _symbol_from_import_item(item, index=index)
        if symbol not in seen:
            normalized.append(symbol)
            seen.add(symbol)
    if not normalized:
        raise ValueError("watchlist import symbols must contain at least one valid symbol")
    return normalized


def _symbol_from_import_item(item: Any, *, index: int) -> str:
    if isinstance(item, str):
        symbol = item.strip().upper()
    elif isinstance(item, Mapping):
        raw_symbol = item.get("symbol")
        if not isinstance(raw_symbol, str):
            raise ValueError(f"watchlist import symbol object at index {index} requires string field symbol")
        symbol = raw_symbol.strip().upper()
    else:
        raise ValueError(f"watchlist import symbol at index {index} must be a string or object")
    if not symbol:
        raise ValueError(f"watchlist import symbol at index {index} cannot be empty")
    return symbol


def _required_str(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    text = _optional_str(value)
    if text is None:
        raise ValueError(f"watchlist import requires non-empty {key}")
    return text


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
