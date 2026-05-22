from __future__ import annotations

import csv
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
        content = source_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"unable to read watchlist import file: {source_path}") from exc
    suffix = source_path.suffix.lower()
    if suffix == ".csv":
        return _parse_watchlist_import_csv(content, source_path=source_path)
    if suffix == ".txt":
        return _parse_watchlist_import_txt(content, source_path=source_path)
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"watchlist import file is not valid JSON: {source_path}") from exc
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
    return sync_watchlist_import_request(
        request,
        observed_state=observed_state,
        create_block=create_block,
        sync_members=sync_members,
        dry_run=dry_run,
        show=show,
        audit_dir=audit_dir,
    )


def sync_watchlist_import_request(
    request: WatchlistImportRequest,
    *,
    observed_state: dict[str, Any] | Result | Callable[[], dict[str, Any] | Result],
    create_block: Callable[[], Result] | None,
    sync_members: Callable[[list[str], bool], Result],
    dry_run: bool = False,
    show: bool = True,
    audit_dir: str | None = None,
) -> Result:
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


def _parse_watchlist_import_csv(content: str, *, source_path: Path) -> WatchlistImportRequest:
    reader = csv.DictReader(content.splitlines())
    fieldnames = _normalize_csv_fieldnames(reader.fieldnames)
    for required in ("block_code", "symbol"):
        if required not in fieldnames:
            raise ValueError(f"watchlist CSV import requires {required} column")
    rows = list(reader)
    block_codes = _unique_non_empty_csv_values(rows, fieldnames, "block_code")
    if not block_codes:
        raise ValueError("watchlist CSV import requires at least one non-empty block_code")
    if len(block_codes) > 1:
        raise ValueError("watchlist CSV import contains multiple block_code values")

    payload: dict[str, Any] = {
        "schema_version": WATCHLIST_IMPORT_SCHEMA_VERSION,
        "block_code": block_codes[0],
        "symbols": [_csv_cell(row, fieldnames, "symbol") for row in rows],
    }
    for key in ("block_name", "mode", "mutation_key"):
        value = _first_non_empty_csv_value(rows, fieldnames, key)
        if value is not None:
            payload[key] = value
    create_if_missing = _first_non_empty_csv_value(rows, fieldnames, "create_if_missing")
    if create_if_missing is not None:
        payload["create_if_missing"] = _parse_bool(create_if_missing, field_name="create_if_missing")
    return _parse_watchlist_import_payload(payload, source_path=source_path)


def _parse_watchlist_import_txt(content: str, *, source_path: Path) -> WatchlistImportRequest:
    directives: dict[str, str] = {}
    symbols: list[str] = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            directive = line[1:].strip()
            if "=" not in directive:
                continue
            key, value = directive.split("=", 1)
            normalized_key = key.strip().lower()
            normalized_value = value.strip()
            if normalized_key and normalized_value:
                directives[normalized_key] = normalized_value
            continue
        symbols.append(line)

    payload: dict[str, Any] = {
        "schema_version": WATCHLIST_IMPORT_SCHEMA_VERSION,
        "block_code": directives.get("block_code"),
        "symbols": symbols,
    }
    for key in ("block_name", "mode", "mutation_key"):
        if key in directives:
            payload[key] = directives[key]
    if "create_if_missing" in directives:
        payload["create_if_missing"] = _parse_bool(directives["create_if_missing"], field_name="create_if_missing")
    return _parse_watchlist_import_payload(payload, source_path=source_path)


def _normalize_csv_fieldnames(raw_fieldnames: list[str] | None) -> dict[str, str]:
    fieldnames: dict[str, str] = {}
    for raw_name in raw_fieldnames or []:
        normalized = str(raw_name).strip().lstrip("\ufeff").lower()
        if normalized:
            fieldnames[normalized] = raw_name
    return fieldnames


def _csv_cell(row: Mapping[str, Any], fieldnames: Mapping[str, str], key: str) -> str | None:
    fieldname = fieldnames.get(key)
    if fieldname is None:
        return None
    return _optional_str(row.get(fieldname))


def _unique_non_empty_csv_values(rows: list[Mapping[str, Any]], fieldnames: Mapping[str, str], key: str) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for row in rows:
        value = _csv_cell(row, fieldnames, key)
        if value is None:
            continue
        normalized = value.upper() if key == "block_code" else value
        if normalized not in seen:
            values.append(normalized)
            seen.add(normalized)
    return values


def _first_non_empty_csv_value(rows: list[Mapping[str, Any]], fieldnames: Mapping[str, str], key: str) -> str | None:
    for row in rows:
        value = _csv_cell(row, fieldnames, key)
        if value is not None:
            return value
    return None


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


def _parse_bool(value: str, *, field_name: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y"}:
        return True
    if normalized in {"0", "false", "no", "n"}:
        return False
    raise ValueError(f"watchlist import {field_name} must be a boolean")
