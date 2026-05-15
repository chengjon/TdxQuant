from __future__ import annotations

import copy
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TRADE_AUDIT_INDEX_SCHEMA_VERSION = "tdx.trade_audit.index.v1"


def _parse_iso_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _extract_stock_codes(payload: Any) -> list[str]:
    if isinstance(payload, dict):
        values: list[str] = []
        for key in ("code", "stock_code", "stock", "symbol"):
            value = payload.get(key)
            if isinstance(value, str) and value:
                values.append(value)
        for value in payload.values():
            values.extend(_extract_stock_codes(value))
        return values
    if isinstance(payload, list):
        values: list[str] = []
        for item in payload:
            values.extend(_extract_stock_codes(item))
        return values
    return []


def _extract_trade_audit_code(payload: dict[str, Any]) -> str | None:
    result_payload = payload.get("result")
    if not isinstance(result_payload, dict):
        return None
    data_payload = result_payload.get("data", result_payload)
    codes = _extract_stock_codes(data_payload)
    if codes:
        return str(codes[0])
    return None


def _normalize_trade_audit_entry(path: Path, payload: dict[str, Any]) -> dict[str, Any] | None:
    trade_audit = payload.get("trade_audit")
    if not isinstance(trade_audit, dict):
        return None
    recorded_at = trade_audit.get("recorded_at")
    return {
        "audit_id": trade_audit.get("audit_id"),
        "recorded_at": recorded_at,
        "status": trade_audit.get("status"),
        "broker": trade_audit.get("broker"),
        "method": trade_audit.get("method"),
        "code": _extract_trade_audit_code(payload),
        "contract_no": trade_audit.get("contract_no"),
        "submission_key": trade_audit.get("submission_key"),
        "side_effect_level": trade_audit.get("side_effect_level"),
        "audit_path": str(path),
    }


def _sort_entries_newest_first(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed_entries = list(enumerate(entries))

    def sort_key(item: tuple[int, dict[str, Any]]) -> tuple[datetime, int]:
        index, entry = item
        parsed = _parse_iso_datetime(entry.get("recorded_at"))
        if parsed is None:
            parsed = datetime.min.replace(tzinfo=timezone.utc)
        return parsed, index

    return [entry for _, entry in sorted(indexed_entries, key=sort_key, reverse=True)]


def build_trade_audit_index_cache(
    *,
    audit_dir: str | Path,
    cache_path: str | Path | None = None,
) -> dict[str, Any]:
    resolved_audit_dir = Path(audit_dir)
    if not resolved_audit_dir.exists() or not resolved_audit_dir.is_dir():
        raise FileNotFoundError(str(resolved_audit_dir))

    warnings: list[str] = []
    entries: list[dict[str, Any]] = []
    scanned_files = 0
    for path in sorted(resolved_audit_dir.glob("*.json")):
        scanned_files += 1
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            warnings.append(f"failed to load trade audit from {path}: {exc}")
            continue
        if not isinstance(payload, dict):
            warnings.append(f"ignored non-object trade audit payload from {path}")
            continue
        entry = _normalize_trade_audit_entry(path, payload)
        if entry is None:
            warnings.append(f"ignored trade audit without trade_audit object: {path}")
            continue
        entries.append(entry)

    payload = {
        "schema_version": TRADE_AUDIT_INDEX_SCHEMA_VERSION,
        "source": {
            "audit_dir": str(resolved_audit_dir),
            "format": "trade_audit_json_directory",
        },
        "summary": {
            "scanned_files": scanned_files,
            "indexed_entries": len(entries),
            "warning_count": len(warnings),
        },
        "entries": _sort_entries_newest_first(entries),
        "warnings": warnings,
    }
    if cache_path is not None:
        resolved_cache_path = Path(cache_path)
        resolved_cache_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def _load_jsonl_rows(path: str | Path | None, *, source_name: str, warnings: list[str]) -> list[dict[str, Any]]:
    if path is None:
        return []
    resolved_path = Path(path)
    if not resolved_path.exists():
        warnings.append(f"{source_name} not found: {resolved_path}")
        return []

    rows: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(resolved_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            warnings.append(f"failed to load {source_name} row from {resolved_path}:{line_number}: {exc}")
            continue
        if not isinstance(payload, dict):
            warnings.append(f"ignored non-object {source_name} row from {resolved_path}:{line_number}")
            continue
        row = copy.deepcopy(payload)
        row.setdefault("_source_path", str(resolved_path))
        row.setdefault("_source_line", line_number)
        rows.append(row)
    return rows


def _load_csv_rows(path: str | Path | None, *, source_name: str, warnings: list[str]) -> list[dict[str, Any]]:
    if path is None:
        return []
    resolved_path = Path(path)
    if not resolved_path.exists():
        warnings.append(f"{source_name} not found: {resolved_path}")
        return []
    try:
        with resolved_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            return [
                {
                    **dict(row),
                    "_source_path": str(resolved_path),
                    "_source_line": index,
                }
                for index, row in enumerate(reader, start=2)
            ]
    except OSError as exc:
        warnings.append(f"failed to load {source_name} from {resolved_path}: {exc}")
        return []


def _matches_filters(
    entry: dict[str, Any],
    *,
    audit_id: str | None,
    contract_no: str | None,
    submission_key: str | None,
    code: str | None,
    status: str | None,
) -> bool:
    filters = {
        "audit_id": audit_id,
        "contract_no": contract_no,
        "submission_key": submission_key,
        "code": code,
        "status": status,
    }
    for key, expected in filters.items():
        if expected is None:
            continue
        if str(entry.get(key, "") or "") != str(expected):
            return False
    return True


def _submission_matches(entry: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    submission_key = entry.get("submission_key")
    if not submission_key:
        return []
    return [copy.deepcopy(row) for row in rows if str(row.get("submission_key", "") or "") == str(submission_key)]


def _task_matches(entry: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    contract_no = str(entry.get("contract_no", "") or "")
    code = str(entry.get("code", "") or "")
    matches: list[dict[str, Any]] = []
    for row in rows:
        row_contract_no = str(row.get("contract_no", "") or "")
        row_code = str(row.get("code", "") or "")
        if contract_no and row_contract_no and row_contract_no != contract_no:
            continue
        if code and row_code and row_code != code:
            continue
        if (contract_no and row_contract_no == contract_no) or (code and row_code == code):
            matches.append(copy.deepcopy(row))
    return matches


def query_trade_audit_cross_ledger(
    *,
    audit_dir: str | Path,
    submission_ledger_path: str | Path | None = None,
    task_ledger_jsonl_path: str | Path | None = None,
    task_ledger_csv_path: str | Path | None = None,
    cache_output_path: str | Path | None = None,
    audit_id: str | None = None,
    contract_no: str | None = None,
    submission_key: str | None = None,
    code: str | None = None,
    status: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    index_payload = build_trade_audit_index_cache(audit_dir=audit_dir, cache_path=cache_output_path)
    warnings = list(index_payload["warnings"])
    submission_rows = _load_jsonl_rows(submission_ledger_path, source_name="submission ledger", warnings=warnings)
    task_rows = _load_jsonl_rows(task_ledger_jsonl_path, source_name="task ledger", warnings=warnings)
    task_rows.extend(_load_csv_rows(task_ledger_csv_path, source_name="task ledger csv", warnings=warnings))

    filtered_entries = [
        entry
        for entry in index_payload["entries"]
        if _matches_filters(
            entry,
            audit_id=audit_id,
            contract_no=contract_no,
            submission_key=submission_key,
            code=code,
            status=status,
        )
    ]
    filtered_entries = _sort_entries_newest_first(filtered_entries)
    resolved_limit = None if limit is None else int(limit)
    returned_entries = filtered_entries if resolved_limit is None or resolved_limit <= 0 else filtered_entries[:resolved_limit]
    rows = []
    for entry in returned_entries:
        rows.append(
            {
                "audit": copy.deepcopy(entry),
                "join_keys": {
                    "submission_key": entry.get("submission_key"),
                    "contract_no": entry.get("contract_no"),
                    "code": entry.get("code"),
                },
                "submission_matches": _submission_matches(entry, submission_rows),
                "task_matches": _task_matches(entry, task_rows),
            }
        )

    return {
        "schema_version": TRADE_AUDIT_INDEX_SCHEMA_VERSION,
        "input": {
            "audit_dir": str(audit_dir),
            "submission_ledger_path": None if submission_ledger_path is None else str(submission_ledger_path),
            "task_ledger_jsonl_path": None if task_ledger_jsonl_path is None else str(task_ledger_jsonl_path),
            "task_ledger_csv_path": None if task_ledger_csv_path is None else str(task_ledger_csv_path),
            "cache_output_path": None if cache_output_path is None else str(cache_output_path),
            "audit_id": audit_id,
            "contract_no": contract_no,
            "submission_key": submission_key,
            "code": code,
            "status": status,
            "limit": resolved_limit,
        },
        "source": {
            "audit_index": index_payload["source"],
            "submission_ledger_rows": len(submission_rows),
            "task_ledger_rows": len(task_rows),
        },
        "join_rules": {
            "submission_matches": ["submission_key"],
            "task_matches": ["contract_no", "code"],
            "mode": "exact_key",
        },
        "summary": {
            "total_audit_entries": len(index_payload["entries"]),
            "filtered_entries": len(filtered_entries),
            "returned_rows": len(rows),
            "submission_ledger_rows": len(submission_rows),
            "task_ledger_rows": len(task_rows),
            "warning_count": len(warnings),
        },
        "rows": rows,
        "warnings": warnings,
    }
