from __future__ import annotations

import copy
import csv
import json
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from ..models import ErrorCode, Result
from ..subscription_event import (
    SUBSCRIPTION_EVENT_CAPABILITY,
    SUBSCRIPTION_EVENT_SCHEMA_VERSION,
    normalize_subscription_event_rows,
)
from ..subscription_watch_run import (
    build_subscription_watch_manifest,
    build_subscription_watch_run_paths,
    build_subscription_watch_status_payload,
    build_subscription_watch_summary_payload,
)
from ..trade import TdxTradeManager
from .manager import TdxApiManager


def get_task_profile_path() -> Path:
    return Path(__file__).resolve().parents[2] / "runtime" / "task-profiles.json"


def load_task_profiles(path: Path | None = None) -> dict[str, dict[str, Any]]:
    profile_path = path or get_task_profile_path()
    payload = json.loads(profile_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("task profile file must contain a JSON object")
    profiles: dict[str, dict[str, Any]] = {}
    for name, value in payload.items():
        if not isinstance(name, str) or not isinstance(value, dict):
            raise ValueError("task profile entries must map profile names to JSON objects")
        profiles[name] = value
    return profiles


def resolve_task_profile(
    profile_name: str,
    overrides: dict[str, Any] | None = None,
    *,
    path: Path | None = None,
    profiles: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    available = profiles if profiles is not None else load_task_profiles(path)
    try:
        resolved = copy.deepcopy(available[profile_name])
    except KeyError as exc:
        raise ValueError(f"unsupported task profile: {profile_name}") from exc
    for key, value in (overrides or {}).items():
        if value is not None:
            resolved[key] = copy.deepcopy(value)
    return resolved


def _capture_task_timing(step_name: str, fn: Any) -> tuple[Any, dict[str, Any]]:
    started_at = time.perf_counter()
    value = fn()
    total_ms = round((time.perf_counter() - started_at) * 1000, 3)
    return value, {"task_call": {"name": step_name, "total_ms": total_ms}}


def _extract_stock_codes(payload: Any) -> list[str]:
    if isinstance(payload, list):
        codes: list[str] = []
        for item in payload:
            if isinstance(item, str):
                codes.append(item)
            elif isinstance(item, dict):
                for key in ("code", "stock_code", "stock", "symbol"):
                    value = item.get(key)
                    if isinstance(value, str) and value:
                        codes.append(value)
                        break
        return codes
    if isinstance(payload, dict):
        for key in ("stocks", "stock_list", "rows", "items", "data"):
            if key in payload:
                codes = _extract_stock_codes(payload[key])
                if codes:
                    return codes
    return []


def _extract_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        rows: list[dict[str, Any]] = []
        for item in payload:
            if isinstance(item, dict):
                rows.append(dict(item))
        return rows
    if isinstance(payload, dict):
        for key in ("rows", "items", "data", "stocks", "stock_list"):
            if key in payload:
                rows = _extract_rows(payload[key])
                if rows:
                    return rows
        scalar_rows: list[dict[str, Any]] = []
        for key, value in payload.items():
            if isinstance(value, dict):
                row = {"stock_code": key}
                row.update(value)
                scalar_rows.append(row)
            elif not isinstance(value, (list, dict)):
                scalar_rows.append({"key": key, "value": value})
        return scalar_rows
    return []


def _write_json_file(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _write_csv_file(path: Path, rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized_rows = [dict(row) for row in rows]
    fieldnames: list[str] = []
    for row in normalized_rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(str(key))
    if not fieldnames:
        fieldnames = ["value"]
        normalized_rows = [{"value": ""}]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in normalized_rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})
    return path


def _resolve_export_dir(profile_options: dict[str, Any]) -> Path:
    export_dir = str(profile_options.get("export_dir", "runtime/exports"))
    return Path(export_dir)


def _resolve_export_stem(profile_options: dict[str, Any], default_stem: str) -> str:
    return str(profile_options.get("export_stem", default_stem))


def _resolve_ledger_stem(profile_options: dict[str, Any], default_stem: str) -> str:
    return str(profile_options.get("ledger_stem", default_stem))


def _resolve_status_stem(profile_options: dict[str, Any], default_stem: str) -> str:
    return str(profile_options.get("status_stem", default_stem))


def _resolve_subscription_watch_root_dir(profile_options: dict[str, Any]) -> Path:
    run_root_dir = profile_options.get("run_root_dir")
    if isinstance(run_root_dir, str) and run_root_dir.strip():
        return Path(run_root_dir)
    return Path("runtime/subscription-watch")


def _extract_numeric_field(payload: Any, candidate_keys: list[str]) -> float | None:
    if isinstance(payload, dict):
        for key in candidate_keys:
            value = payload.get(key)
            if value is not None:
                try:
                    return float(value)
                except (TypeError, ValueError):
                    pass
        for value in payload.values():
            extracted = _extract_numeric_field(value, candidate_keys)
            if extracted is not None:
                return extracted
    if isinstance(payload, list):
        for item in payload:
            extracted = _extract_numeric_field(item, candidate_keys)
            if extracted is not None:
                return extracted
    return None


def _formula_scan_has_match(payload: Any, target_code: str) -> bool:
    extracted_codes = _extract_stock_codes(payload)
    if target_code in extracted_codes:
        return True
    rows = _extract_rows(payload)
    return bool(rows)


def _append_jsonl_file(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return path


def _append_csv_row(path: Path, row: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized_row = {str(key): value for key, value in row.items()}
    fieldnames = list(normalized_row.keys())
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow({name: normalized_row.get(name, "") for name in fieldnames})
    return path


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_boolish(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y", "ok", "passed"}:
            return True
        if normalized in {"false", "0", "no", "n", "failed"}:
            return False
    return None


def _load_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        payload = json.loads(line)
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader]
    for row in rows:
        for key in ("trade_ok", "snapshot_price_check_passed", "block_membership_check_passed", "formula_check_passed"):
            if key in row:
                row[key] = _parse_boolish(row.get(key))
    return rows


def _coerce_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _coerce_int(value: Any) -> int | None:
    numeric = _coerce_float(value)
    if numeric is None:
        return None
    try:
        return int(numeric)
    except (TypeError, ValueError):
        return None


def _resolve_task_ledger_paths(
    profile_options: dict[str, Any],
    *,
    ledger_jsonl_path: str | None = None,
    ledger_csv_path: str | None = None,
) -> tuple[Path, Path]:
    export_dir = _resolve_export_dir(profile_options)
    ledger_stem = _resolve_ledger_stem(profile_options, "guarded-trade-buy-ledger")
    resolved_jsonl_path = Path(ledger_jsonl_path) if ledger_jsonl_path else export_dir / f"{ledger_stem}.jsonl"
    resolved_csv_path = Path(ledger_csv_path) if ledger_csv_path else export_dir / f"{ledger_stem}.csv"
    return resolved_jsonl_path, resolved_csv_path


def _load_task_ledger_source(
    profile_options: dict[str, Any],
    *,
    ledger_jsonl_path: str | None = None,
    ledger_csv_path: str | None = None,
) -> dict[str, Any]:
    resolved_jsonl_path, resolved_csv_path = _resolve_task_ledger_paths(
        profile_options,
        ledger_jsonl_path=ledger_jsonl_path,
        ledger_csv_path=ledger_csv_path,
    )
    if resolved_jsonl_path.exists():
        return {
            "entries": _load_jsonl_rows(resolved_jsonl_path),
            "source_path": resolved_jsonl_path,
            "source_format": "jsonl",
            "ledger_jsonl_path": resolved_jsonl_path,
            "ledger_csv_path": resolved_csv_path,
        }
    if resolved_csv_path.exists():
        return {
            "entries": _load_csv_rows(resolved_csv_path),
            "source_path": resolved_csv_path,
            "source_format": "csv",
            "ledger_jsonl_path": resolved_jsonl_path,
            "ledger_csv_path": resolved_csv_path,
        }
    raise FileNotFoundError


def _filter_task_ledger_entries(
    entries: list[dict[str, Any]],
    *,
    code: str | None = None,
    contract_no: str | None = None,
    trade_ok: bool | None = None,
    task_name: str | None = None,
) -> list[dict[str, Any]]:
    filtered_entries = entries
    if code is not None:
        filtered_entries = [entry for entry in filtered_entries if str(entry.get("code", "")) == code]
    if contract_no is not None:
        filtered_entries = [entry for entry in filtered_entries if str(entry.get("contract_no", "")) == contract_no]
    if task_name is not None:
        filtered_entries = [entry for entry in filtered_entries if str(entry.get("task_name", "")) == task_name]
    if trade_ok is not None:
        filtered_entries = [entry for entry in filtered_entries if _parse_boolish(entry.get("trade_ok")) is trade_ok]
    return filtered_entries


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


def _current_local_date_iso(timezone_name: str) -> str:
    return datetime.now(ZoneInfo(timezone_name)).date().isoformat()


def _extract_local_date_iso(entry: dict[str, Any], tzinfo: ZoneInfo) -> str | None:
    parsed_timestamp = _parse_iso_datetime(entry.get("timestamp"))
    if parsed_timestamp is None:
        return None
    return parsed_timestamp.astimezone(tzinfo).date().isoformat()


def _normalize_report_date_iso(value: str) -> str:
    return datetime.strptime(value, "%Y-%m-%d").date().isoformat()


def _filter_entries_by_local_date_range(
    entries: list[dict[str, Any]],
    *,
    tzinfo: ZoneInfo,
    start_date: str,
    end_date: str,
) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    for entry in entries:
        local_date = _extract_local_date_iso(entry, tzinfo)
        if local_date is None:
            continue
        if start_date <= local_date <= end_date:
            filtered.append(entry)
    return filtered


def _aggregate_entries_by_code(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for entry in entries:
        code = str(entry.get("code", "")).strip()
        if not code:
            code = "<unknown>"
        bucket = grouped.setdefault(
            code,
            {
                "code": code,
                "entries_count": 0,
                "success_count": 0,
                "failed_count": 0,
                "total_quantity": 0,
                "total_amount": 0.0,
                "latest_contract_no": "",
                "latest_timestamp": "",
            },
        )
        bucket["entries_count"] += 1
        trade_state = _parse_boolish(entry.get("trade_ok"))
        if trade_state is True:
            bucket["success_count"] += 1
        elif trade_state is False:
            bucket["failed_count"] += 1
        quantity = _coerce_int(entry.get("quantity"))
        if quantity is not None:
            bucket["total_quantity"] += quantity
        price = _coerce_float(entry.get("price"))
        if price is not None and quantity is not None:
            bucket["total_amount"] = round(float(bucket["total_amount"]) + price * quantity, 4)
        contract_no = entry.get("contract_no")
        if contract_no:
            bucket["latest_contract_no"] = str(contract_no)
        timestamp = entry.get("timestamp")
        if timestamp:
            bucket["latest_timestamp"] = str(timestamp)
    return [grouped[key] for key in sorted(grouped.keys())]


def _aggregate_entries_by_day(entries: list[dict[str, Any]], *, tzinfo: ZoneInfo) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for entry in entries:
        local_date = _extract_local_date_iso(entry, tzinfo)
        if local_date is None:
            continue
        bucket = grouped.setdefault(
            local_date,
            {
                "report_date": local_date,
                "entries_count": 0,
                "success_count": 0,
                "failed_count": 0,
                "unique_codes": set(),
                "total_quantity": 0,
                "total_amount": 0.0,
                "latest_timestamp": "",
            },
        )
        bucket["entries_count"] += 1
        trade_state = _parse_boolish(entry.get("trade_ok"))
        if trade_state is True:
            bucket["success_count"] += 1
        elif trade_state is False:
            bucket["failed_count"] += 1
        code = str(entry.get("code", "")).strip()
        if code:
            bucket["unique_codes"].add(code)
        quantity = _coerce_int(entry.get("quantity"))
        if quantity is not None:
            bucket["total_quantity"] += quantity
        price = _coerce_float(entry.get("price"))
        if price is not None and quantity is not None:
            bucket["total_amount"] = round(float(bucket["total_amount"]) + price * quantity, 4)
        timestamp = entry.get("timestamp")
        if timestamp:
            bucket["latest_timestamp"] = str(timestamp)

    rows: list[dict[str, Any]] = []
    for report_date in sorted(grouped.keys()):
        bucket = grouped[report_date]
        unique_codes = sorted(str(code) for code in bucket["unique_codes"])
        rows.append(
            {
                "report_date": report_date,
                "entries_count": int(bucket["entries_count"]),
                "success_count": int(bucket["success_count"]),
                "failed_count": int(bucket["failed_count"]),
                "unique_codes_count": len(unique_codes),
                "unique_codes": ",".join(unique_codes),
                "total_quantity": int(bucket["total_quantity"]),
                "total_amount": float(bucket["total_amount"]),
                "latest_timestamp": bucket["latest_timestamp"] or "",
            }
        )
    return rows


def _sort_ledger_entries_newest_first(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed_entries = list(enumerate(entries))

    def sort_key(item: tuple[int, dict[str, Any]]) -> tuple[datetime, int]:
        index, entry = item
        parsed = _parse_iso_datetime(entry.get("timestamp"))
        if parsed is None:
            parsed = datetime.min.replace(tzinfo=timezone.utc)
        return parsed, index

    sorted_pairs = sorted(indexed_entries, key=sort_key, reverse=True)
    return [entry for _, entry in sorted_pairs]


def _build_trade_report_entry_view(entry: dict[str, Any], *, tzinfo: ZoneInfo | None = None) -> dict[str, Any]:
    entry_view = copy.deepcopy(entry)
    report_json_path = str(entry.get("report_json_path", "") or "")
    report_csv_path = str(entry.get("report_csv_path", "") or "")
    entry_view["report_json_path"] = report_json_path
    entry_view["report_csv_path"] = report_csv_path
    entry_view["report_json_exists"] = bool(report_json_path) and Path(report_json_path).exists()
    entry_view["report_csv_exists"] = bool(report_csv_path) and Path(report_csv_path).exists()
    if tzinfo is not None:
        entry_view["local_date"] = _extract_local_date_iso(entry, tzinfo)
    return entry_view


def _load_json_file_if_exists(path_value: str) -> tuple[dict[str, Any] | None, str | None]:
    if not path_value:
        return None, None
    path = Path(path_value)
    if not path.exists():
        return None, None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"failed to load report json from {path}: {exc}"
    if isinstance(payload, dict):
        return payload, None
    return {"payload": payload}, None


def _resolve_trade_audit_dir(
    profile_options: dict[str, Any],
    *,
    audit_dir: str | None = None,
) -> Path:
    resolved_dir = audit_dir if audit_dir is not None else profile_options.get("audit_dir", "runtime/trade-audits")
    return Path(str(resolved_dir))


def _extract_trade_audit_code(payload: dict[str, Any]) -> str | None:
    result_payload = payload.get("result")
    if not isinstance(result_payload, dict):
        return None
    data_payload = result_payload.get("data", result_payload)
    codes = _extract_stock_codes(data_payload)
    if codes:
        return str(codes[0])
    if isinstance(data_payload, dict):
        for key in ("code", "stock_code", "stock", "symbol"):
            value = data_payload.get(key)
            if isinstance(value, str) and value:
                return value
    return None


def _load_trade_audit_source(
    profile_options: dict[str, Any],
    *,
    audit_dir: str | None = None,
) -> tuple[dict[str, Any], list[str]]:
    resolved_dir = _resolve_trade_audit_dir(profile_options, audit_dir=audit_dir)
    if not resolved_dir.exists() or not resolved_dir.is_dir():
        raise FileNotFoundError

    warnings: list[str] = []
    entries: list[dict[str, Any]] = []
    scanned_files = 0
    for path in sorted(resolved_dir.glob("*.json")):
        scanned_files += 1
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            warnings.append(f"failed to load trade audit from {path}: {exc}")
            continue
        if not isinstance(payload, dict):
            warnings.append(f"ignored non-object trade audit payload from {path}")
            continue
        trade_audit = payload.get("trade_audit")
        if not isinstance(trade_audit, dict):
            warnings.append(f"ignored trade audit without trade_audit object: {path}")
            continue
        entries.append(
            {
                "payload": payload,
                "trade_audit": trade_audit,
                "audit_path": str(path),
                "code": _extract_trade_audit_code(payload),
            }
        )
    return {
        "entries": entries,
        "source_path": resolved_dir,
        "scanned_files": scanned_files,
    }, warnings


def _filter_trade_audit_entries(
    entries: list[dict[str, Any]],
    *,
    audit_id: str | None = None,
    contract_no: str | None = None,
    submission_key: str | None = None,
    code: str | None = None,
    status: str | None = None,
    statuses: list[str] | None = None,
    method: str | None = None,
    methods: list[str] | None = None,
) -> list[dict[str, Any]]:
    filtered_entries = entries
    if audit_id is not None:
        filtered_entries = [
            entry for entry in filtered_entries if str(entry.get("trade_audit", {}).get("audit_id", "")) == audit_id
        ]
    if contract_no is not None:
        filtered_entries = [
            entry for entry in filtered_entries if str(entry.get("trade_audit", {}).get("contract_no", "")) == contract_no
        ]
    if submission_key is not None:
        filtered_entries = [
            entry
            for entry in filtered_entries
            if str(entry.get("trade_audit", {}).get("submission_key", "")) == submission_key
        ]
    if code is not None:
        filtered_entries = [entry for entry in filtered_entries if str(entry.get("code", "") or "") == code]
    if status is not None:
        filtered_entries = [entry for entry in filtered_entries if str(entry.get("trade_audit", {}).get("status", "")) == status]
    if statuses is not None:
        allowed_statuses = set(statuses)
        filtered_entries = [
            entry
            for entry in filtered_entries
            if str(entry.get("trade_audit", {}).get("status", "")) in allowed_statuses
        ]
    if method is not None:
        filtered_entries = [
            entry for entry in filtered_entries if str(entry.get("trade_audit", {}).get("method", "")) == method
        ]
    if methods is not None:
        allowed_methods = set(methods)
        filtered_entries = [
            entry
            for entry in filtered_entries
            if str(entry.get("trade_audit", {}).get("method", "")) in allowed_methods
        ]
    return filtered_entries


def _normalize_trade_audit_status_filters(
    *,
    status: str | None = None,
    statuses: list[str] | None = None,
) -> tuple[str | None, list[str] | None]:
    normalized_status = None
    if status is not None:
        stripped_status = str(status).strip()
        if stripped_status:
            normalized_status = stripped_status

    normalized_statuses = None
    if statuses is not None:
        filtered_statuses = [str(item).strip() for item in statuses if str(item).strip()]
        if filtered_statuses:
            normalized_statuses = filtered_statuses

    if normalized_status is not None and normalized_statuses is not None:
        raise ValueError("status and statuses cannot be used together")

    return normalized_status, normalized_statuses


def _normalize_trade_audit_method_filters(
    *,
    method: str | None = None,
    methods: list[str] | None = None,
) -> tuple[str | None, list[str] | None]:
    normalized_method = None
    if method is not None:
        stripped_method = str(method).strip()
        if stripped_method:
            normalized_method = stripped_method

    normalized_methods = None
    if methods is not None:
        filtered_methods = [str(item).strip() for item in methods if str(item).strip()]
        if filtered_methods:
            normalized_methods = filtered_methods

    if normalized_method is not None and normalized_methods is not None:
        raise ValueError("method and methods cannot be used together")

    return normalized_method, normalized_methods


def _sort_trade_audit_entries_newest_first(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed_entries = list(enumerate(entries))

    def sort_key(item: tuple[int, dict[str, Any]]) -> tuple[datetime, int]:
        index, entry = item
        parsed = _parse_iso_datetime(entry.get("trade_audit", {}).get("recorded_at"))
        if parsed is None:
            parsed = datetime.min.replace(tzinfo=timezone.utc)
        return parsed, index

    sorted_pairs = sorted(indexed_entries, key=sort_key, reverse=True)
    return [entry for _, entry in sorted_pairs]


def _build_trade_audit_entry_view(entry: dict[str, Any]) -> dict[str, Any]:
    trade_audit = entry.get("trade_audit", {})
    return {
        "audit_id": trade_audit.get("audit_id"),
        "recorded_at": trade_audit.get("recorded_at"),
        "status": trade_audit.get("status"),
        "method": trade_audit.get("method"),
        "broker": trade_audit.get("broker"),
        "code": entry.get("code"),
        "contract_no": trade_audit.get("contract_no"),
        "submission_key": trade_audit.get("submission_key"),
        "side_effect_level": trade_audit.get("side_effect_level"),
        "audit_path": entry.get("audit_path"),
    }


def _extract_trade_audit_local_date_iso(entry: dict[str, Any], tzinfo: ZoneInfo) -> str | None:
    parsed = _parse_iso_datetime(entry.get("trade_audit", {}).get("recorded_at"))
    if parsed is None:
        return None
    return parsed.astimezone(tzinfo).date().isoformat()


def _filter_trade_audit_entries_by_local_date_range(
    entries: list[dict[str, Any]],
    *,
    tzinfo: ZoneInfo,
    start_date: str,
    end_date: str,
) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    for entry in entries:
        local_date = _extract_trade_audit_local_date_iso(entry, tzinfo)
        if local_date is None:
            continue
        if start_date <= local_date <= end_date:
            filtered.append(entry)
    return filtered


def _aggregate_trade_audit_entries_by_status(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for entry in entries:
        trade_audit = entry.get("trade_audit", {})
        status = str(trade_audit.get("status", "")).strip() or "<unknown>"
        bucket = grouped.setdefault(
            status,
            {
                "status": status,
                "entries_count": 0,
                "unique_codes": set(),
                "unique_contracts": set(),
                "latest_recorded_at": "",
            },
        )
        bucket["entries_count"] += 1
        code = str(entry.get("code", "")).strip()
        if code:
            bucket["unique_codes"].add(code)
        contract_no = str(trade_audit.get("contract_no", "")).strip()
        if contract_no:
            bucket["unique_contracts"].add(contract_no)
        recorded_at = str(trade_audit.get("recorded_at", "")).strip()
        if recorded_at:
            bucket["latest_recorded_at"] = recorded_at

    rows: list[dict[str, Any]] = []
    for status in sorted(grouped.keys()):
        bucket = grouped[status]
        unique_codes = sorted(str(code) for code in bucket["unique_codes"])
        unique_contracts = sorted(str(contract_no) for contract_no in bucket["unique_contracts"])
        rows.append(
            {
                "status": status,
                "entries_count": int(bucket["entries_count"]),
                "unique_codes_count": len(unique_codes),
                "unique_codes": ",".join(unique_codes),
                "unique_contracts_count": len(unique_contracts),
                "latest_recorded_at": bucket["latest_recorded_at"] or "",
            }
        )
    return rows


def _aggregate_trade_audit_entries_by_code(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for entry in entries:
        trade_audit = entry.get("trade_audit", {})
        code = str(entry.get("code", "")).strip() or "<unknown>"
        bucket = grouped.setdefault(
            code,
            {
                "code": code,
                "entries_count": 0,
                "confirmed_count": 0,
                "replayed_count": 0,
                "rejected_count": 0,
                "failed_count": 0,
                "unique_contracts": set(),
                "latest_recorded_at": "",
            },
        )
        bucket["entries_count"] += 1
        status = str(trade_audit.get("status", "")).strip()
        if status == "confirmed":
            bucket["confirmed_count"] += 1
        elif status == "replayed":
            bucket["replayed_count"] += 1
        elif status == "rejected":
            bucket["rejected_count"] += 1
        elif status == "failed":
            bucket["failed_count"] += 1
        contract_no = str(trade_audit.get("contract_no", "")).strip()
        if contract_no:
            bucket["unique_contracts"].add(contract_no)
        recorded_at = str(trade_audit.get("recorded_at", "")).strip()
        if recorded_at:
            bucket["latest_recorded_at"] = recorded_at

    rows: list[dict[str, Any]] = []
    for code in sorted(grouped.keys()):
        bucket = grouped[code]
        unique_contracts = sorted(str(contract_no) for contract_no in bucket["unique_contracts"])
        rows.append(
            {
                "code": code,
                "entries_count": int(bucket["entries_count"]),
                "confirmed_count": int(bucket["confirmed_count"]),
                "replayed_count": int(bucket["replayed_count"]),
                "rejected_count": int(bucket["rejected_count"]),
                "failed_count": int(bucket["failed_count"]),
                "unique_contracts_count": len(unique_contracts),
                "latest_recorded_at": bucket["latest_recorded_at"] or "",
            }
        )
    return rows


def _aggregate_trade_audit_entries_by_day(entries: list[dict[str, Any]], *, tzinfo: ZoneInfo) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for entry in entries:
        trade_audit = entry.get("trade_audit", {})
        local_date = _extract_trade_audit_local_date_iso(entry, tzinfo)
        if local_date is None:
            continue
        bucket = grouped.setdefault(
            local_date,
            {
                "report_date": local_date,
                "entries_count": 0,
                "confirmed_count": 0,
                "replayed_count": 0,
                "rejected_count": 0,
                "failed_count": 0,
                "unique_codes": set(),
                "latest_recorded_at": "",
            },
        )
        bucket["entries_count"] += 1
        status = str(trade_audit.get("status", "")).strip()
        if status == "confirmed":
            bucket["confirmed_count"] += 1
        elif status == "replayed":
            bucket["replayed_count"] += 1
        elif status == "rejected":
            bucket["rejected_count"] += 1
        elif status == "failed":
            bucket["failed_count"] += 1
        code = str(entry.get("code", "")).strip()
        if code:
            bucket["unique_codes"].add(code)
        recorded_at = str(trade_audit.get("recorded_at", "")).strip()
        if recorded_at:
            bucket["latest_recorded_at"] = recorded_at

    rows: list[dict[str, Any]] = []
    for report_date in sorted(grouped.keys()):
        bucket = grouped[report_date]
        unique_codes = sorted(str(code) for code in bucket["unique_codes"])
        rows.append(
            {
                "report_date": report_date,
                "entries_count": int(bucket["entries_count"]),
                "confirmed_count": int(bucket["confirmed_count"]),
                "replayed_count": int(bucket["replayed_count"]),
                "rejected_count": int(bucket["rejected_count"]),
                "failed_count": int(bucket["failed_count"]),
                "unique_codes_count": len(unique_codes),
                "unique_codes": ",".join(unique_codes),
                "latest_recorded_at": bucket["latest_recorded_at"] or "",
            }
        )
    return rows


class TdxTaskManager:
    __slots__ = ("profile_name", "profile_options", "api_manager", "trade_manager", "strategy_path")

    def __init__(
        self,
        *,
        profile: str = "default",
        strategy_path: str | None = None,
        profile_overrides: dict[str, Any] | None = None,
        api_profile: str | None = None,
        api_profile_overrides: dict[str, Any] | None = None,
        trade_profile: str | None = None,
        trade_profile_overrides: dict[str, Any] | None = None,
        title_keyword: str = "平安证券",
        exe_path: str | None = None,
    ) -> None:
        self.profile_name = profile
        self.profile_options = resolve_task_profile(profile, overrides=profile_overrides)
        self.strategy_path = strategy_path
        resolved_api_profile = api_profile or str(self.profile_options.get("api_profile", "default"))
        resolved_trade_profile = trade_profile or str(self.profile_options.get("trade_profile", "balanced"))
        self.api_manager = TdxApiManager(
            profile=resolved_api_profile,
            strategy_path=strategy_path,
            profile_overrides=api_profile_overrides,
        )
        self.trade_manager = TdxTradeManager(
            profile=resolved_trade_profile,
            title_keyword=title_keyword,
            exe_path=exe_path,
            profile_overrides=trade_profile_overrides,
        )

    def _attach_task_metadata(self, result: Result, *, task_name: str, timing: dict[str, Any]) -> Result:
        result.data["task"] = {
            "entrypoint": "TdxTaskManager",
            "name": task_name,
        }
        result.data["task_profile"] = {
            "name": self.profile_name,
            "options": copy.deepcopy(self.profile_options),
        }
        result.data.setdefault("timing", {}).update(timing)
        return result

    def sector_research(
        self,
        block_code: str,
        *,
        block_type: int = 0,
        list_type: int | None = None,
        fields: list[str] | None = None,
    ) -> Result:
        def run() -> Result:
            sector_result = self.api_manager.meta.sector_stocks(
                block_code=block_code,
                block_type=block_type,
                list_type=list_type,
            )
            if not sector_result.ok:
                return sector_result
            stock_codes = _extract_stock_codes(sector_result.data)
            if not stock_codes:
                return Result(
                    ok=False,
                    code=ErrorCode.EXECUTION_FAILED,
                    message="sector research task could not extract stock codes from sector result",
                    data={"sector_result": sector_result.to_dict()},
                    next_action="Inspect the sector-stocks response shape and refine the extraction rule.",
                )
            gp_fields = list(fields) if fields is not None else list(self.profile_options.get("gp_one_fields", []))
            metrics_result = self.api_manager.meta.gp_one_data(stock_list=stock_codes, fields=gp_fields)
            if not metrics_result.ok:
                return metrics_result
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="completed sector research task",
                data={
                    "input": {
                        "block_code": block_code,
                        "block_type": block_type,
                        "list_type": list_type,
                        "fields": gp_fields,
                    },
                    "sector_result": sector_result.to_dict(),
                    "metrics_result": metrics_result.to_dict(),
                    "stock_codes": stock_codes,
                },
            )

        result, timing = _capture_task_timing("task.sector_research", run)
        return self._attach_task_metadata(result, task_name="sector_research", timing=timing)

    def formula_scan(
        self,
        *,
        formula_name: str,
        stock_list: list[str],
        formula_arg: str = "",
        return_count: int = 1,
        return_date: bool = False,
        stock_period: str = "1d",
        start_time: str = "",
        end_time: str = "",
        count: int = 0,
        dividend_type: int = 0,
    ) -> Result:
        result, timing = _capture_task_timing(
            "task.formula_scan",
            lambda: self.api_manager.formula.process_mul_xg(
                formula_name=formula_name,
                formula_arg=formula_arg,
                return_count=return_count,
                return_date=return_date,
                stock_list=stock_list,
                stock_period=stock_period,
                start_time=start_time,
                end_time=end_time,
                count=count,
                dividend_type=dividend_type,
            ),
        )
        result.data.setdefault(
            "input",
            {
                "formula_name": formula_name,
                "formula_arg": formula_arg,
                "stock_list": stock_list,
                "return_count": return_count,
                "return_date": return_date,
                "stock_period": stock_period,
                "start_time": start_time,
                "end_time": end_time,
                "count": count,
                "dividend_type": dividend_type,
            },
        )
        return self._attach_task_metadata(result, task_name="formula_scan", timing=timing)

    def watchlist_overview(self, *, stock_list: list[str], fields: list[str] | None = None) -> Result:
        resolved_fields = list(fields) if fields is not None else list(self.profile_options.get("gp_one_fields", []))
        result, timing = _capture_task_timing(
            "task.watchlist_overview",
            lambda: self.api_manager.meta.gp_one_data(stock_list=stock_list, fields=resolved_fields),
        )
        result.data.setdefault(
            "input",
            {
                "stock_list": stock_list,
                "fields": resolved_fields,
            },
        )
        return self._attach_task_metadata(result, task_name="watchlist_overview", timing=timing)

    def sector_formula_scan(
        self,
        *,
        block_code: str,
        formula_name: str,
        block_type: int = 0,
        list_type: int | None = None,
        formula_arg: str = "",
        return_count: int = 1,
        return_date: bool = False,
        stock_period: str = "1d",
        start_time: str = "",
        end_time: str = "",
        count: int = 0,
        dividend_type: int = 0,
    ) -> Result:
        def run() -> Result:
            sector_result = self.api_manager.meta.sector_stocks(
                block_code=block_code,
                block_type=block_type,
                list_type=list_type,
            )
            if not sector_result.ok:
                return sector_result
            stock_codes = _extract_stock_codes(sector_result.data)
            if not stock_codes:
                return Result(
                    ok=False,
                    code=ErrorCode.EXECUTION_FAILED,
                    message="sector formula scan task could not extract stock codes from sector result",
                    data={"sector_result": sector_result.to_dict()},
                    next_action="Inspect the sector-stocks response shape and refine the extraction rule.",
                )
            scan_result = self.api_manager.formula.process_mul_xg(
                formula_name=formula_name,
                formula_arg=formula_arg,
                return_count=return_count,
                return_date=return_date,
                stock_list=stock_codes,
                stock_period=stock_period,
                start_time=start_time,
                end_time=end_time,
                count=count,
                dividend_type=dividend_type,
            )
            if not scan_result.ok:
                return scan_result
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="completed sector formula scan task",
                data={
                    "input": {
                        "block_code": block_code,
                        "block_type": block_type,
                        "list_type": list_type,
                        "formula_name": formula_name,
                        "formula_arg": formula_arg,
                        "return_count": return_count,
                        "return_date": return_date,
                        "stock_period": stock_period,
                        "start_time": start_time,
                        "end_time": end_time,
                        "count": count,
                        "dividend_type": dividend_type,
                    },
                    "sector_result": sector_result.to_dict(),
                    "formula_result": scan_result.to_dict(),
                    "stock_codes": stock_codes,
                },
            )

        result, timing = _capture_task_timing("task.sector_formula_scan", run)
        return self._attach_task_metadata(result, task_name="sector_formula_scan", timing=timing)

    def watchlist_export(
        self,
        *,
        stock_list: list[str],
        fields: list[str] | None = None,
        json_output_path: str | None = None,
        csv_output_path: str | None = None,
    ) -> Result:
        result = self.watchlist_overview(stock_list=stock_list, fields=fields)
        if not result.ok:
            return result
        export_dir = _resolve_export_dir(self.profile_options)
        export_stem = _resolve_export_stem(self.profile_options, "watchlist-overview")
        json_path = Path(json_output_path) if json_output_path else export_dir / f"{export_stem}.json"
        csv_path = Path(csv_output_path) if csv_output_path else export_dir / f"{export_stem}.csv"
        rows = _extract_rows(result.data)
        if not rows:
            rows = [{"stock_code": code} for code in stock_list]
        _write_json_file(json_path, result.to_dict())
        _write_csv_file(csv_path, rows)
        result.data.setdefault("artifacts", {})
        result.data["artifacts"].update(
            {
                "json_output_path": str(json_path),
                "csv_output_path": str(csv_path),
            }
        )
        result.data["task"]["name"] = "watchlist_export"
        return result

    def sector_research_export(
        self,
        *,
        block_code: str,
        block_type: int = 0,
        list_type: int | None = None,
        fields: list[str] | None = None,
        json_output_path: str | None = None,
        csv_output_path: str | None = None,
    ) -> Result:
        result = self.sector_research(
            block_code=block_code,
            block_type=block_type,
            list_type=list_type,
            fields=fields,
        )
        if not result.ok:
            return result
        export_dir = _resolve_export_dir(self.profile_options)
        export_stem = _resolve_export_stem(self.profile_options, "sector-research")
        json_path = Path(json_output_path) if json_output_path else export_dir / f"{export_stem}.json"
        csv_path = Path(csv_output_path) if csv_output_path else export_dir / f"{export_stem}.csv"
        rows = _extract_rows(result.data.get("metrics_result", {}))
        if not rows:
            rows = [{"stock_code": code} for code in result.data.get("stock_codes", [])]
        _write_json_file(json_path, result.to_dict())
        _write_csv_file(csv_path, rows)
        result.data.setdefault("artifacts", {})
        result.data["artifacts"].update(
            {
                "json_output_path": str(json_path),
                "csv_output_path": str(csv_path),
            }
        )
        result.data["task"]["name"] = "sector_research_export"
        return result

    def refresh_environment(self, *, market: str | None = None, force: bool | None = None) -> Result:
        result, timing = _capture_task_timing(
            "task.refresh_environment",
            lambda: self.api_manager.refresh_cache(market=market, force=force),
        )
        return self._attach_task_metadata(result, task_name="refresh_environment", timing=timing)

    def subscription_watch(
        self,
        *,
        stock_list: list[str],
        max_events: int | None = None,
        max_seconds: float | None = None,
        poll_interval: float | None = None,
        jsonl_output_path: str | None = None,
        csv_output_path: str | None = None,
        status_output_path: str | None = None,
    ) -> Result:
        def run() -> Result:
            if not stock_list:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="subscription watch task requires at least one stock code",
                    next_action="Provide one or more --code values.",
                )

            resolved_max_events = max_events
            if resolved_max_events is not None and resolved_max_events <= 0:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="subscription watch task requires max_events > 0",
                    next_action="Provide a positive --max-events value or omit it.",
                )

            resolved_max_seconds = max_seconds
            if resolved_max_seconds is not None and resolved_max_seconds <= 0:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="subscription watch task requires max_seconds > 0",
                    next_action="Provide a positive --max-seconds value or omit it.",
                )

            resolved_poll_interval = float(
                self.profile_options.get("poll_interval", 0.25) if poll_interval is None else poll_interval
            )
            if resolved_poll_interval < 0:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="subscription watch task requires poll_interval >= 0",
                    next_action="Provide a non-negative --poll-interval value.",
                )

            run_root_dir = _resolve_subscription_watch_root_dir(self.profile_options)
            run_paths = build_subscription_watch_run_paths(run_root_dir)
            run_paths.run_dir.mkdir(parents=True, exist_ok=False)

            legacy_jsonl_path = Path(jsonl_output_path) if jsonl_output_path else None
            legacy_csv_path = Path(csv_output_path) if csv_output_path else None
            legacy_status_path = Path(status_output_path) if status_output_path else None

            session_id = uuid4().hex
            started_at = _now_utc_iso()
            subscription_id = uuid4().hex
            state_lock = threading.RLock()
            event_count = 0
            last_event_at: str | None = None
            last_symbol: str | None = None
            unique_symbols: set[str] = set()

            session = self.api_manager.runtime.open_subscription_session()
            provider_instance_id = str(getattr(session, "session_id", "unknown-session"))
            subscribed_symbols = list(stock_list)
            manifest_payload = build_subscription_watch_manifest(
                paths=run_paths,
                provider="tongdaxin",
                provider_mode="runtime_session",
                requested_symbols=subscribed_symbols,
            )
            _write_json_file(run_paths.manifest_path, manifest_payload)
            artifact_paths = {
                "run_dir": str(run_paths.run_dir),
                "manifest_path": str(run_paths.manifest_path),
                "status_path": str(run_paths.status_path),
                "summary_path": str(run_paths.summary_path),
                "events_jsonl_path": str(run_paths.events_jsonl_path),
                "events_csv_path": str(run_paths.events_csv_path),
                "jsonl_output_path": str(legacy_jsonl_path or run_paths.events_jsonl_path),
                "csv_output_path": str(legacy_csv_path or run_paths.events_csv_path),
                "status_output_path": str(legacy_status_path or run_paths.status_path),
            }

            def build_status_payload(*, state: str, stop_reason: str | None = None, finished_at: str | None = None) -> dict[str, Any]:
                with state_lock:
                    symbol_rows = sorted(unique_symbols)
                    current_event_count = event_count
                    current_last_event_at = last_event_at
                    current_last_symbol = last_symbol
                payload = build_subscription_watch_status_payload(
                    paths=run_paths,
                    state=state,
                    started_at=started_at,
                    updated_at=finished_at or _now_utc_iso(),
                    session_id=session_id,
                    event_count=current_event_count,
                    last_sequence=current_event_count,
                    last_event_ts=current_last_event_at,
                    last_symbol=current_last_symbol,
                    warnings=[],
                )
                payload.update(
                    {
                        "provider_instance_id": provider_instance_id,
                        "subscription_id": subscription_id,
                        "finished_at": finished_at,
                        "stop_reason": stop_reason,
                        "subscribed_symbols": subscribed_symbols,
                        "unique_symbols": symbol_rows,
                        "unique_symbol_count": len(symbol_rows),
                        "last_event_at": current_last_event_at,
                        "artifacts": dict(artifact_paths),
                    }
                )
                return payload

            def write_status(*, state: str, stop_reason: str | None = None, finished_at: str | None = None) -> None:
                payload = build_status_payload(state=state, stop_reason=stop_reason, finished_at=finished_at)
                _write_json_file(run_paths.status_path, payload)
                if legacy_status_path is not None and legacy_status_path != run_paths.status_path:
                    _write_json_file(legacy_status_path, payload)

            def append_event_rows(rows: list[dict[str, Any]]) -> None:
                nonlocal event_count, last_event_at, last_symbol
                with state_lock:
                    for row in rows:
                        _append_jsonl_file(run_paths.events_jsonl_path, row)
                        if legacy_jsonl_path is not None and legacy_jsonl_path != run_paths.events_jsonl_path:
                            _append_jsonl_file(legacy_jsonl_path, row)
                        _append_csv_row(
                            run_paths.events_csv_path,
                            {
                                "sequence": row["sequence"],
                                "symbol": row.get("symbol"),
                                "event_type": row["event_type"],
                                "source_ts": row.get("source_ts"),
                                "event_ts": row["event_ts"],
                                "session_id": row["session_id"],
                                "provider_instance_id": row["provider_instance_id"],
                                "subscription_id": row["subscription_id"],
                                "payload_json": json.dumps(row["payload"], ensure_ascii=False, sort_keys=True),
                            },
                        )
                        if legacy_csv_path is not None and legacy_csv_path != run_paths.events_csv_path:
                            _append_csv_row(
                                legacy_csv_path,
                                {
                                    "sequence": row["sequence"],
                                    "symbol": row.get("symbol"),
                                    "event_type": row["event_type"],
                                    "source_ts": row.get("source_ts"),
                                    "event_ts": row["event_ts"],
                                    "session_id": row["session_id"],
                                    "provider_instance_id": row["provider_instance_id"],
                                    "subscription_id": row["subscription_id"],
                                    "payload_json": json.dumps(row["payload"], ensure_ascii=False, sort_keys=True),
                                },
                            )
                        event_count += 1
                        symbol_value = row.get("symbol")
                        if isinstance(symbol_value, str) and symbol_value:
                            unique_symbols.add(symbol_value)
                            last_symbol = symbol_value
                        last_event_at = str(row["event_ts"])
                write_status(state="running")

            write_status(state="starting")

            def on_event(raw_payload: Any) -> None:
                with state_lock:
                    start_sequence = event_count + 1
                rows = normalize_subscription_event_rows(
                    raw_payload,
                    session_id=session_id,
                    provider_instance_id=provider_instance_id,
                    subscription_id=subscription_id,
                    run_id=run_paths.run_id,
                    capability=SUBSCRIPTION_EVENT_CAPABILITY,
                    start_sequence=start_sequence,
                )
                append_event_rows(rows)

            subscribe_result = session.subscribe_hq(stock_list=subscribed_symbols, callback=on_event)
            if not subscribe_result.ok:
                failed_at = _now_utc_iso()
                write_status(state="failed", stop_reason="subscribe_failed", finished_at=failed_at)
                _write_json_file(
                    run_paths.summary_path,
                    build_subscription_watch_summary_payload(
                        paths=run_paths,
                        final_state="failed",
                        started_at=started_at,
                        finished_at=failed_at,
                        elapsed_ms=0.0,
                        session_id=session_id,
                        event_count=event_count,
                        symbol_count=len(unique_symbols),
                        stop_reason="subscribe_failed",
                        warning_count=len(subscribe_result.warnings),
                    ),
                )
                session.close()
                return Result(
                    ok=False,
                    code=subscribe_result.code,
                    message="subscription watch task failed during subscribe step",
                    data={
                        "input": {
                            "stock_list": subscribed_symbols,
                            "max_events": resolved_max_events,
                            "max_seconds": resolved_max_seconds,
                            "poll_interval": resolved_poll_interval,
                        },
                        "artifacts": dict(artifact_paths),
                        "subscribe_result": subscribe_result.to_dict(),
                    },
                    warnings=list(subscribe_result.warnings),
                    next_action=subscribe_result.next_action,
                )

            write_status(state="running")
            stop_reason = "completed"
            interrupted = False
            started_monotonic = time.perf_counter()
            try:
                while True:
                    with state_lock:
                        current_event_count = event_count
                    if resolved_max_events is not None and current_event_count >= resolved_max_events:
                        stop_reason = "max_events"
                        break
                    if resolved_max_seconds is not None and (time.perf_counter() - started_monotonic) >= resolved_max_seconds:
                        stop_reason = "max_seconds"
                        break
                    time.sleep(resolved_poll_interval)
            except KeyboardInterrupt:
                interrupted = True
                stop_reason = "keyboard_interrupt"

            unsubscribe_result = session.unsubscribe_hq(stock_list=subscribed_symbols)
            session.close()
            finished_at = _now_utc_iso()
            write_status(
                state="interrupted" if interrupted else "completed",
                stop_reason=stop_reason,
                finished_at=finished_at,
            )

            final_status = build_status_payload(
                state="interrupted" if interrupted else "completed",
                stop_reason=stop_reason,
                finished_at=finished_at,
            )
            elapsed_ms = round((time.perf_counter() - started_monotonic) * 1000, 3)
            summary_payload = build_subscription_watch_summary_payload(
                paths=run_paths,
                final_state="interrupted" if interrupted else "completed",
                started_at=started_at,
                finished_at=finished_at,
                elapsed_ms=elapsed_ms,
                session_id=session_id,
                event_count=final_status["event_count"],
                symbol_count=final_status["unique_symbol_count"],
                stop_reason=stop_reason,
                warning_count=len(subscribe_result.warnings) + len(unsubscribe_result.warnings),
            )
            _write_json_file(run_paths.summary_path, summary_payload)
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="completed subscription watch task",
                data={
                    "input": {
                        "stock_list": subscribed_symbols,
                        "max_events": resolved_max_events,
                        "max_seconds": resolved_max_seconds,
                        "poll_interval": resolved_poll_interval,
                    },
                    "subscription": {
                        "session_id": session_id,
                        "provider_instance_id": provider_instance_id,
                        "subscription_id": subscription_id,
                        "run_id": run_paths.run_id,
                    },
                    "summary": {
                        "event_count": final_status["event_count"],
                        "unique_symbol_count": final_status["unique_symbol_count"],
                        "unique_symbols": final_status["unique_symbols"],
                        "stop_reason": stop_reason,
                        "interrupted": interrupted,
                        "started_at": started_at,
                        "finished_at": finished_at,
                        "elapsed_ms": elapsed_ms,
                        "last_event_at": final_status["last_event_at"],
                    },
                    "status": final_status,
                    "manifest": manifest_payload,
                    "artifacts": dict(artifact_paths),
                    "subscribe_result": subscribe_result.to_dict(),
                    "unsubscribe_result": unsubscribe_result.to_dict(),
                },
                warnings=list(subscribe_result.warnings) + list(unsubscribe_result.warnings),
                next_action=unsubscribe_result.next_action or subscribe_result.next_action,
            )

        result, timing = _capture_task_timing("task.subscription_watch", run)
        return self._attach_task_metadata(result, task_name="subscription_watch", timing=timing)

    def ledger_summary(
        self,
        *,
        limit: int | None = None,
        code: str | None = None,
        contract_no: str | None = None,
        trade_ok: bool | None = None,
        task_name: str | None = None,
        ledger_jsonl_path: str | None = None,
        ledger_csv_path: str | None = None,
        json_output_path: str | None = None,
        csv_output_path: str | None = None,
    ) -> Result:
        def run() -> Result:
            export_dir = _resolve_export_dir(self.profile_options)
            export_stem = _resolve_export_stem(self.profile_options, "ledger-summary")
            resolved_limit = int(self.profile_options.get("default_limit", 20) if limit is None else limit)
            try:
                ledger_source = _load_task_ledger_source(
                    self.profile_options,
                    ledger_jsonl_path=ledger_jsonl_path,
                    ledger_csv_path=ledger_csv_path,
                )
            except FileNotFoundError:
                resolved_jsonl_path, resolved_csv_path = _resolve_task_ledger_paths(
                    self.profile_options,
                    ledger_jsonl_path=ledger_jsonl_path,
                    ledger_csv_path=ledger_csv_path,
                )
                return Result(
                    ok=False,
                    code=ErrorCode.PATH_NOT_FOUND,
                    message="ledger summary task could not find a ledger file",
                    data={
                        "input": {
                            "ledger_jsonl_path": str(resolved_jsonl_path),
                            "ledger_csv_path": str(resolved_csv_path),
                        }
                    },
                    next_action="Run guarded trade workflows first or provide an explicit ledger path.",
                )
            entries = list(ledger_source["entries"])
            filtered_entries = _filter_task_ledger_entries(
                entries,
                code=code,
                contract_no=contract_no,
                trade_ok=trade_ok,
                task_name=task_name,
            )

            recent_entries = list(reversed(filtered_entries if resolved_limit <= 0 else filtered_entries[-resolved_limit:]))
            success_count = sum(1 for entry in filtered_entries if _parse_boolish(entry.get("trade_ok")) is True)
            failed_count = sum(1 for entry in filtered_entries if _parse_boolish(entry.get("trade_ok")) is False)
            latest_timestamp = None
            latest_contract_no = None
            for entry in reversed(filtered_entries):
                if latest_timestamp is None and entry.get("timestamp"):
                    latest_timestamp = str(entry.get("timestamp"))
                if latest_contract_no is None and entry.get("contract_no"):
                    latest_contract_no = str(entry.get("contract_no"))
                if latest_timestamp is not None and latest_contract_no is not None:
                    break

            result_payload: dict[str, Any] = {
                "input": {
                    "limit": resolved_limit,
                    "code": code,
                    "contract_no": contract_no,
                    "trade_ok": trade_ok,
                    "task_name": task_name,
                    "ledger_jsonl_path": str(ledger_source["ledger_jsonl_path"]),
                    "ledger_csv_path": str(ledger_source["ledger_csv_path"]),
                },
                "source": {
                    "path": str(ledger_source["source_path"]),
                    "format": str(ledger_source["source_format"]),
                },
                "summary": {
                    "total_entries": len(entries),
                    "matched_entries": len(filtered_entries),
                    "success_count": success_count,
                    "failed_count": failed_count,
                    "latest_timestamp": latest_timestamp,
                    "latest_contract_no": latest_contract_no,
                    "unique_codes": sorted({str(entry.get("code")) for entry in filtered_entries if entry.get("code")}),
                },
                "entries": recent_entries,
            }

            artifacts: dict[str, Any] = {}
            if json_output_path is not None or csv_output_path is not None:
                summary_json_path = Path(json_output_path) if json_output_path else export_dir / f"{export_stem}.json"
                summary_csv_path = Path(csv_output_path) if csv_output_path else export_dir / f"{export_stem}.csv"
                _write_json_file(summary_json_path, result_payload)
                _write_csv_file(summary_csv_path, [dict(entry) for entry in filtered_entries])
                artifacts.update(
                    {
                        "json_output_path": str(summary_json_path),
                        "csv_output_path": str(summary_csv_path),
                    }
                )
            if artifacts:
                result_payload["artifacts"] = artifacts

            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="completed ledger summary task",
                data=result_payload,
            )

        result, timing = _capture_task_timing("task.ledger_summary", run)
        return self._attach_task_metadata(result, task_name="ledger_summary", timing=timing)

    def daily_trade_report(
        self,
        *,
        report_date: str | None = None,
        timezone_name: str | None = None,
        recent_limit: int | None = None,
        code: str | None = None,
        trade_ok: bool | None = None,
        task_name: str | None = None,
        ledger_jsonl_path: str | None = None,
        ledger_csv_path: str | None = None,
        json_output_path: str | None = None,
        csv_output_path: str | None = None,
    ) -> Result:
        def run() -> Result:
            resolved_timezone_name = str(
                self.profile_options.get("default_timezone", "Asia/Shanghai")
                if timezone_name is None
                else timezone_name
            )
            try:
                tzinfo = ZoneInfo(resolved_timezone_name)
            except ZoneInfoNotFoundError:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"unsupported timezone: {resolved_timezone_name}",
                    next_action="Provide a valid IANA timezone such as Asia/Shanghai.",
                )

            resolved_report_date = report_date or _current_local_date_iso(resolved_timezone_name)
            try:
                normalized_report_date = datetime.strptime(resolved_report_date, "%Y-%m-%d").date().isoformat()
            except ValueError:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"invalid report date: {resolved_report_date}",
                    next_action="Use report dates in YYYY-MM-DD format.",
                )

            try:
                ledger_source = _load_task_ledger_source(
                    self.profile_options,
                    ledger_jsonl_path=ledger_jsonl_path,
                    ledger_csv_path=ledger_csv_path,
                )
            except FileNotFoundError:
                resolved_jsonl_path, resolved_csv_path = _resolve_task_ledger_paths(
                    self.profile_options,
                    ledger_jsonl_path=ledger_jsonl_path,
                    ledger_csv_path=ledger_csv_path,
                )
                return Result(
                    ok=False,
                    code=ErrorCode.PATH_NOT_FOUND,
                    message="daily trade report task could not find a ledger file",
                    data={
                        "input": {
                            "ledger_jsonl_path": str(resolved_jsonl_path),
                            "ledger_csv_path": str(resolved_csv_path),
                        }
                    },
                    next_action="Run guarded trade workflows first or provide an explicit ledger path.",
                )

            entries = list(ledger_source["entries"])
            prefiltered_entries = _filter_task_ledger_entries(
                entries,
                code=code,
                trade_ok=trade_ok,
                task_name=task_name,
            )
            report_entries = [
                entry
                for entry in prefiltered_entries
                if _extract_local_date_iso(entry, tzinfo) == normalized_report_date
            ]
            resolved_recent_limit = int(
                self.profile_options.get("default_recent_limit", 10) if recent_limit is None else recent_limit
            )
            recent_entries = list(
                reversed(report_entries if resolved_recent_limit <= 0 else report_entries[-resolved_recent_limit:])
            )
            by_code_rows = _aggregate_entries_by_code(report_entries)
            success_count = sum(1 for entry in report_entries if _parse_boolish(entry.get("trade_ok")) is True)
            failed_count = sum(1 for entry in report_entries if _parse_boolish(entry.get("trade_ok")) is False)
            total_quantity = sum(int(row["total_quantity"]) for row in by_code_rows)
            total_amount = round(sum(float(row["total_amount"]) for row in by_code_rows), 4)
            latest_timestamp = ""
            for entry in reversed(report_entries):
                timestamp = entry.get("timestamp")
                if timestamp:
                    latest_timestamp = str(timestamp)
                    break

            result_payload: dict[str, Any] = {
                "input": {
                    "report_date": normalized_report_date,
                    "timezone": resolved_timezone_name,
                    "recent_limit": resolved_recent_limit,
                    "code": code,
                    "trade_ok": trade_ok,
                    "task_name": task_name,
                    "ledger_jsonl_path": str(ledger_source["ledger_jsonl_path"]),
                    "ledger_csv_path": str(ledger_source["ledger_csv_path"]),
                },
                "source": {
                    "path": str(ledger_source["source_path"]),
                    "format": str(ledger_source["source_format"]),
                },
                "summary": {
                    "total_entries": len(entries),
                    "matched_entries": len(prefiltered_entries),
                    "report_entries": len(report_entries),
                    "success_count": success_count,
                    "failed_count": failed_count,
                    "unique_codes": [row["code"] for row in by_code_rows],
                    "total_quantity": total_quantity,
                    "total_amount": total_amount,
                    "latest_timestamp": latest_timestamp or None,
                },
                "by_code": by_code_rows,
                "entries": recent_entries,
            }

            artifacts: dict[str, Any] = {}
            if json_output_path is not None or csv_output_path is not None:
                export_dir = _resolve_export_dir(self.profile_options)
                export_stem = _resolve_export_stem(self.profile_options, "daily-trade-report")
                summary_json_path = (
                    Path(json_output_path)
                    if json_output_path
                    else export_dir / f"{export_stem}-{normalized_report_date}.json"
                )
                summary_csv_path = (
                    Path(csv_output_path)
                    if csv_output_path
                    else export_dir / f"{export_stem}-{normalized_report_date}.csv"
                )
                export_rows = by_code_rows if by_code_rows else [{"report_date": normalized_report_date}]
                _write_json_file(summary_json_path, result_payload)
                _write_csv_file(summary_csv_path, export_rows)
                artifacts.update(
                    {
                        "json_output_path": str(summary_json_path),
                        "csv_output_path": str(summary_csv_path),
                    }
                )
            if artifacts:
                result_payload["artifacts"] = artifacts

            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="completed daily trade report task",
                data=result_payload,
            )

        result, timing = _capture_task_timing("task.daily_trade_report", run)
        return self._attach_task_metadata(result, task_name="daily_trade_report", timing=timing)

    def trade_report_lookup(
        self,
        *,
        contract_no: str | None = None,
        code: str | None = None,
        report_date: str | None = None,
        timezone_name: str | None = None,
        limit: int | None = None,
        trade_ok: bool | None = None,
        task_name: str | None = None,
        ledger_jsonl_path: str | None = None,
        ledger_csv_path: str | None = None,
        json_output_path: str | None = None,
        csv_output_path: str | None = None,
    ) -> Result:
        def run() -> Result:
            if contract_no is None and code is None:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="trade report lookup task requires contract_no or code",
                    next_action="Provide --contract-no for exact lookup or --code for candidate lookup.",
                )

            resolved_timezone_name = str(
                self.profile_options.get("default_timezone", "Asia/Shanghai")
                if timezone_name is None
                else timezone_name
            )
            try:
                tzinfo = ZoneInfo(resolved_timezone_name)
            except ZoneInfoNotFoundError:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"unsupported timezone: {resolved_timezone_name}",
                    next_action="Provide a valid IANA timezone such as Asia/Shanghai.",
                )

            normalized_report_date: str | None = None
            if report_date is not None:
                try:
                    normalized_report_date = datetime.strptime(report_date, "%Y-%m-%d").date().isoformat()
                except ValueError:
                    return Result(
                        ok=False,
                        code=ErrorCode.INVALID_REQUEST,
                        message=f"invalid report date: {report_date}",
                        next_action="Use report dates in YYYY-MM-DD format.",
                    )

            try:
                ledger_source = _load_task_ledger_source(
                    self.profile_options,
                    ledger_jsonl_path=ledger_jsonl_path,
                    ledger_csv_path=ledger_csv_path,
                )
            except FileNotFoundError:
                resolved_jsonl_path, resolved_csv_path = _resolve_task_ledger_paths(
                    self.profile_options,
                    ledger_jsonl_path=ledger_jsonl_path,
                    ledger_csv_path=ledger_csv_path,
                )
                return Result(
                    ok=False,
                    code=ErrorCode.PATH_NOT_FOUND,
                    message="trade report lookup task could not find a ledger file",
                    data={
                        "input": {
                            "ledger_jsonl_path": str(resolved_jsonl_path),
                            "ledger_csv_path": str(resolved_csv_path),
                        }
                    },
                    next_action="Run guarded trade workflows first or provide an explicit ledger path.",
                )

            entries = list(ledger_source["entries"])
            filtered_entries = _filter_task_ledger_entries(
                entries,
                code=code,
                contract_no=contract_no,
                trade_ok=trade_ok,
                task_name=task_name,
            )
            if normalized_report_date is not None:
                filtered_entries = [
                    entry
                    for entry in filtered_entries
                    if _extract_local_date_iso(entry, tzinfo) == normalized_report_date
                ]
            ordered_entries = _sort_ledger_entries_newest_first(filtered_entries)
            resolved_limit = int(self.profile_options.get("default_limit", 10) if limit is None else limit)
            limited_entries = ordered_entries if resolved_limit <= 0 else ordered_entries[:resolved_limit]
            entry_views = [_build_trade_report_entry_view(entry, tzinfo=tzinfo) for entry in limited_entries]

            warnings: list[str] = []
            loaded_report: dict[str, Any] | None = None
            unique_match = len(ordered_entries) == 1
            if unique_match and entry_views:
                candidate_report_path = str(entry_views[0].get("report_json_path", ""))
                loaded_report, load_warning = _load_json_file_if_exists(candidate_report_path)
                if load_warning is not None:
                    warnings.append(load_warning)

            latest_timestamp = entry_views[0].get("timestamp") if entry_views else None
            latest_contract_no = entry_views[0].get("contract_no") if entry_views else None
            result_payload: dict[str, Any] = {
                "input": {
                    "contract_no": contract_no,
                    "code": code,
                    "report_date": normalized_report_date,
                    "timezone": resolved_timezone_name,
                    "limit": resolved_limit,
                    "trade_ok": trade_ok,
                    "task_name": task_name,
                    "ledger_jsonl_path": str(ledger_source["ledger_jsonl_path"]),
                    "ledger_csv_path": str(ledger_source["ledger_csv_path"]),
                },
                "source": {
                    "path": str(ledger_source["source_path"]),
                    "format": str(ledger_source["source_format"]),
                },
                "summary": {
                    "total_entries": len(entries),
                    "matched_entries": len(ordered_entries),
                    "returned_entries": len(entry_views),
                    "unique_match": unique_match,
                    "loaded_report": loaded_report is not None,
                    "latest_timestamp": latest_timestamp,
                    "latest_contract_no": latest_contract_no,
                },
                "entries": entry_views,
            }
            if loaded_report is not None:
                result_payload["report"] = loaded_report

            artifacts: dict[str, Any] = {}
            if json_output_path is not None or csv_output_path is not None:
                export_dir = _resolve_export_dir(self.profile_options)
                export_stem = _resolve_export_stem(self.profile_options, "trade-report-lookup")
                summary_json_path = Path(json_output_path) if json_output_path else export_dir / f"{export_stem}.json"
                summary_csv_path = Path(csv_output_path) if csv_output_path else export_dir / f"{export_stem}.csv"
                export_rows = entry_views if entry_views else [{"contract_no": contract_no or "", "code": code or ""}]
                _write_json_file(summary_json_path, result_payload)
                _write_csv_file(summary_csv_path, export_rows)
                artifacts.update(
                    {
                        "json_output_path": str(summary_json_path),
                        "csv_output_path": str(summary_csv_path),
                    }
                )
            if artifacts:
                result_payload["artifacts"] = artifacts

            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="completed trade report lookup task",
                data=result_payload,
                warnings=warnings,
            )

        result, timing = _capture_task_timing("task.trade_report_lookup", run)
        return self._attach_task_metadata(result, task_name="trade_report_lookup", timing=timing)

    def trade_audit_lookup(
        self,
        *,
        audit_id: str | None = None,
        contract_no: str | None = None,
        submission_key: str | None = None,
        code: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        audit_dir: str | None = None,
        json_output_path: str | None = None,
        csv_output_path: str | None = None,
    ) -> Result:
        def run() -> Result:
            if audit_id is None and contract_no is None and submission_key is None and code is None:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="trade audit lookup task requires audit_id, contract_no, submission_key, or code",
                    next_action="Provide --audit-id for exact lookup or another primary filter for candidate lookup.",
                )

            warnings: list[str] = []
            try:
                audit_source, load_warnings = _load_trade_audit_source(
                    self.profile_options,
                    audit_dir=audit_dir,
                )
            except FileNotFoundError:
                resolved_audit_dir = _resolve_trade_audit_dir(self.profile_options, audit_dir=audit_dir)
                return Result(
                    ok=False,
                    code=ErrorCode.PATH_NOT_FOUND,
                    message="trade audit lookup task could not find an audit directory",
                    data={"input": {"audit_dir": str(resolved_audit_dir)}},
                    next_action="Run stable desktop trade workflows first or provide an explicit audit directory.",
                )
            warnings.extend(load_warnings)

            entries = list(audit_source["entries"])
            filtered_entries = _filter_trade_audit_entries(
                entries,
                audit_id=audit_id,
                contract_no=contract_no,
                submission_key=submission_key,
                code=code,
                status=status,
            )
            ordered_entries = _sort_trade_audit_entries_newest_first(filtered_entries)
            resolved_limit = int(self.profile_options.get("default_limit", 10) if limit is None else limit)
            limited_entries = ordered_entries if resolved_limit <= 0 else ordered_entries[:resolved_limit]
            entry_views = [_build_trade_audit_entry_view(entry) for entry in limited_entries]

            unique_match = len(ordered_entries) == 1
            loaded_audit = copy.deepcopy(ordered_entries[0]["payload"]) if unique_match and ordered_entries else None
            latest_entry = entry_views[0] if entry_views else {}
            result_payload: dict[str, Any] = {
                "input": {
                    "audit_id": audit_id,
                    "contract_no": contract_no,
                    "submission_key": submission_key,
                    "code": code,
                    "status": status,
                    "limit": resolved_limit,
                    "audit_dir": str(audit_source["source_path"]),
                },
                "source": {
                    "path": str(audit_source["source_path"]),
                    "format": "directory",
                    "scanned_files": int(audit_source["scanned_files"]),
                },
                "summary": {
                    "total_entries": len(entries),
                    "matched_entries": len(ordered_entries),
                    "returned_entries": len(entry_views),
                    "unique_match": unique_match,
                    "loaded_audit": loaded_audit is not None,
                    "latest_recorded_at": latest_entry.get("recorded_at"),
                    "latest_audit_id": latest_entry.get("audit_id"),
                    "latest_contract_no": latest_entry.get("contract_no"),
                },
                "entries": entry_views,
            }
            if loaded_audit is not None:
                result_payload["audit"] = loaded_audit

            artifacts: dict[str, Any] = {}
            if json_output_path is not None or csv_output_path is not None:
                export_dir = _resolve_export_dir(self.profile_options)
                export_stem = _resolve_export_stem(self.profile_options, "trade-audit-lookup")
                summary_json_path = Path(json_output_path) if json_output_path else export_dir / f"{export_stem}.json"
                summary_csv_path = Path(csv_output_path) if csv_output_path else export_dir / f"{export_stem}.csv"
                export_rows = entry_views if entry_views else [{"audit_id": audit_id or "", "code": code or ""}]
                _write_json_file(summary_json_path, result_payload)
                _write_csv_file(summary_csv_path, export_rows)
                artifacts.update(
                    {
                        "json_output_path": str(summary_json_path),
                        "csv_output_path": str(summary_csv_path),
                    }
                )
            if artifacts:
                result_payload["artifacts"] = artifacts

            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="completed trade audit lookup task",
                data=result_payload,
                warnings=warnings,
            )

        result, timing = _capture_task_timing("task.trade_audit_lookup", run)
        return self._attach_task_metadata(result, task_name="trade_audit_lookup", timing=timing)

    def trade_audit_daily_report(
        self,
        *,
        report_date: str | None = None,
        timezone_name: str | None = None,
        recent_limit: int | None = None,
        code: str | None = None,
        status: str | None = None,
        statuses: list[str] | None = None,
        method: str | None = None,
        methods: list[str] | None = None,
        broker: str | None = None,
        submission_key: str | None = None,
        audit_dir: str | None = None,
        json_output_path: str | None = None,
        csv_output_path: str | None = None,
    ) -> Result:
        def run() -> Result:
            try:
                normalized_status, normalized_statuses = _normalize_trade_audit_status_filters(
                    status=status,
                    statuses=statuses,
                )
                normalized_method, normalized_methods = _normalize_trade_audit_method_filters(
                    method=method,
                    methods=methods,
                )
            except ValueError as exc:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message=str(exc),
                    next_action="Use either singular or plural trade_audit filters for the same field, but not both.",
                )

            resolved_timezone_name = str(
                self.profile_options.get("default_timezone", "Asia/Shanghai")
                if timezone_name is None
                else timezone_name
            )
            try:
                tzinfo = ZoneInfo(resolved_timezone_name)
            except ZoneInfoNotFoundError:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"unsupported timezone: {resolved_timezone_name}",
                    next_action="Provide a valid IANA timezone such as Asia/Shanghai.",
                )

            resolved_report_date = report_date or _current_local_date_iso(resolved_timezone_name)
            try:
                normalized_report_date = datetime.strptime(resolved_report_date, "%Y-%m-%d").date().isoformat()
            except ValueError:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"invalid report date: {resolved_report_date}",
                    next_action="Use report dates in YYYY-MM-DD format.",
                )

            warnings: list[str] = []
            try:
                audit_source, load_warnings = _load_trade_audit_source(self.profile_options, audit_dir=audit_dir)
            except FileNotFoundError:
                resolved_audit_dir = _resolve_trade_audit_dir(self.profile_options, audit_dir=audit_dir)
                return Result(
                    ok=False,
                    code=ErrorCode.PATH_NOT_FOUND,
                    message="trade audit daily report task could not find an audit directory",
                    data={"input": {"audit_dir": str(resolved_audit_dir)}},
                    next_action="Run stable desktop trade workflows first or provide an explicit audit directory.",
                )
            warnings.extend(load_warnings)

            entries = list(audit_source["entries"])
            prefiltered_entries = [
                entry
                for entry in _filter_trade_audit_entries(
                    entries,
                    code=code,
                    status=normalized_status,
                    statuses=normalized_statuses,
                    method=normalized_method,
                    methods=normalized_methods,
                    submission_key=submission_key,
                )
                if broker is None or str(entry.get("trade_audit", {}).get("broker", "")) == broker
            ]
            report_entries = [
                entry
                for entry in prefiltered_entries
                if _extract_trade_audit_local_date_iso(entry, tzinfo) == normalized_report_date
            ]
            ordered_entries = _sort_trade_audit_entries_newest_first(report_entries)
            resolved_recent_limit = int(
                self.profile_options.get("default_recent_limit", 10) if recent_limit is None else recent_limit
            )
            recent_entries = [
                _build_trade_audit_entry_view(entry)
                for entry in (ordered_entries if resolved_recent_limit <= 0 else ordered_entries[:resolved_recent_limit])
            ]
            by_code_rows = _aggregate_trade_audit_entries_by_code(report_entries)
            by_status_rows = _aggregate_trade_audit_entries_by_status(report_entries)
            latest_recorded_at = recent_entries[0].get("recorded_at") if recent_entries else None

            result_payload: dict[str, Any] = {
                "input": {
                    "report_date": normalized_report_date,
                    "timezone": resolved_timezone_name,
                    "recent_limit": resolved_recent_limit,
                    "code": code,
                    "status": normalized_status,
                    "statuses": copy.deepcopy(normalized_statuses),
                    "method": normalized_method,
                    "methods": copy.deepcopy(normalized_methods),
                    "broker": broker,
                    "submission_key": submission_key,
                    "audit_dir": str(audit_source["source_path"]),
                },
                "source": {
                    "path": str(audit_source["source_path"]),
                    "format": "directory",
                    "scanned_files": int(audit_source["scanned_files"]),
                },
                "summary": {
                    "total_entries": len(entries),
                    "matched_entries": len(prefiltered_entries),
                    "report_entries": len(report_entries),
                    "unique_codes": [row["code"] for row in by_code_rows],
                    "statuses": [row["status"] for row in by_status_rows],
                    "latest_recorded_at": latest_recorded_at,
                },
                "by_code": by_code_rows,
                "by_status": by_status_rows,
                "entries": recent_entries,
            }

            artifacts: dict[str, Any] = {}
            if json_output_path is not None or csv_output_path is not None:
                export_dir = _resolve_export_dir(self.profile_options)
                export_stem = _resolve_export_stem(self.profile_options, "trade-audit-daily-report")
                summary_json_path = (
                    Path(json_output_path)
                    if json_output_path
                    else export_dir / f"{export_stem}-{normalized_report_date}.json"
                )
                summary_csv_path = (
                    Path(csv_output_path)
                    if csv_output_path
                    else export_dir / f"{export_stem}-{normalized_report_date}.csv"
                )
                export_rows = by_code_rows if by_code_rows else [{"report_date": normalized_report_date}]
                _write_json_file(summary_json_path, result_payload)
                _write_csv_file(summary_csv_path, export_rows)
                artifacts.update(
                    {
                        "json_output_path": str(summary_json_path),
                        "csv_output_path": str(summary_csv_path),
                    }
                )
            if artifacts:
                result_payload["artifacts"] = artifacts

            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="completed trade audit daily report task",
                data=result_payload,
                warnings=warnings,
            )

        result, timing = _capture_task_timing("task.trade_audit_daily_report", run)
        return self._attach_task_metadata(result, task_name="trade_audit_daily_report", timing=timing)

    def trade_audit_period_report(
        self,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        timezone_name: str | None = None,
        recent_limit: int | None = None,
        code: str | None = None,
        status: str | None = None,
        statuses: list[str] | None = None,
        method: str | None = None,
        methods: list[str] | None = None,
        broker: str | None = None,
        submission_key: str | None = None,
        audit_dir: str | None = None,
        json_output_path: str | None = None,
        csv_output_path: str | None = None,
    ) -> Result:
        def run() -> Result:
            try:
                normalized_status, normalized_statuses = _normalize_trade_audit_status_filters(
                    status=status,
                    statuses=statuses,
                )
                normalized_method, normalized_methods = _normalize_trade_audit_method_filters(
                    method=method,
                    methods=methods,
                )
            except ValueError as exc:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message=str(exc),
                    next_action="Use either singular or plural trade_audit filters for the same field, but not both.",
                )

            if start_date is None and end_date is None:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="trade audit period report task requires start_date or end_date",
                    next_action="Provide at least one boundary date in YYYY-MM-DD format.",
                )

            resolved_timezone_name = str(
                self.profile_options.get("default_timezone", "Asia/Shanghai")
                if timezone_name is None
                else timezone_name
            )
            try:
                tzinfo = ZoneInfo(resolved_timezone_name)
            except ZoneInfoNotFoundError:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"unsupported timezone: {resolved_timezone_name}",
                    next_action="Provide a valid IANA timezone such as Asia/Shanghai.",
                )

            raw_start_date = start_date or end_date
            raw_end_date = end_date or start_date
            try:
                normalized_start_date = _normalize_report_date_iso(str(raw_start_date))
                normalized_end_date = _normalize_report_date_iso(str(raw_end_date))
            except ValueError:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="invalid period boundary",
                    next_action="Use start_date and end_date in YYYY-MM-DD format.",
                )
            if normalized_start_date > normalized_end_date:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="start_date must not be later than end_date",
                    next_action="Provide an inclusive date range with start_date <= end_date.",
                )

            warnings: list[str] = []
            try:
                audit_source, load_warnings = _load_trade_audit_source(self.profile_options, audit_dir=audit_dir)
            except FileNotFoundError:
                resolved_audit_dir = _resolve_trade_audit_dir(self.profile_options, audit_dir=audit_dir)
                return Result(
                    ok=False,
                    code=ErrorCode.PATH_NOT_FOUND,
                    message="trade audit period report task could not find an audit directory",
                    data={"input": {"audit_dir": str(resolved_audit_dir)}},
                    next_action="Run stable desktop trade workflows first or provide an explicit audit directory.",
                )
            warnings.extend(load_warnings)

            entries = list(audit_source["entries"])
            prefiltered_entries = [
                entry
                for entry in _filter_trade_audit_entries(
                    entries,
                    code=code,
                    status=normalized_status,
                    statuses=normalized_statuses,
                    method=normalized_method,
                    methods=normalized_methods,
                    submission_key=submission_key,
                )
                if broker is None or str(entry.get("trade_audit", {}).get("broker", "")) == broker
            ]
            report_entries = _filter_trade_audit_entries_by_local_date_range(
                prefiltered_entries,
                tzinfo=tzinfo,
                start_date=normalized_start_date,
                end_date=normalized_end_date,
            )
            ordered_entries = _sort_trade_audit_entries_newest_first(report_entries)
            resolved_recent_limit = int(
                self.profile_options.get("default_recent_limit", 20) if recent_limit is None else recent_limit
            )
            recent_entries = [
                _build_trade_audit_entry_view(entry)
                for entry in (ordered_entries if resolved_recent_limit <= 0 else ordered_entries[:resolved_recent_limit])
            ]
            by_day_rows = _aggregate_trade_audit_entries_by_day(report_entries, tzinfo=tzinfo)
            by_code_rows = _aggregate_trade_audit_entries_by_code(report_entries)
            by_status_rows = _aggregate_trade_audit_entries_by_status(report_entries)
            latest_recorded_at = recent_entries[0].get("recorded_at") if recent_entries else None

            result_payload: dict[str, Any] = {
                "input": {
                    "start_date": normalized_start_date,
                    "end_date": normalized_end_date,
                    "timezone": resolved_timezone_name,
                    "recent_limit": resolved_recent_limit,
                    "code": code,
                    "status": normalized_status,
                    "statuses": copy.deepcopy(normalized_statuses),
                    "method": normalized_method,
                    "methods": copy.deepcopy(normalized_methods),
                    "broker": broker,
                    "submission_key": submission_key,
                    "audit_dir": str(audit_source["source_path"]),
                },
                "source": {
                    "path": str(audit_source["source_path"]),
                    "format": "directory",
                    "scanned_files": int(audit_source["scanned_files"]),
                },
                "summary": {
                    "total_entries": len(entries),
                    "matched_entries": len(prefiltered_entries),
                    "report_entries": len(report_entries),
                    "trade_days": len(by_day_rows),
                    "unique_codes": [row["code"] for row in by_code_rows],
                    "statuses": [row["status"] for row in by_status_rows],
                    "latest_recorded_at": latest_recorded_at,
                },
                "by_day": by_day_rows,
                "by_code": by_code_rows,
                "by_status": by_status_rows,
                "entries": recent_entries,
            }

            artifacts: dict[str, Any] = {}
            if json_output_path is not None or csv_output_path is not None:
                export_dir = _resolve_export_dir(self.profile_options)
                export_stem = _resolve_export_stem(self.profile_options, "trade-audit-period-report")
                summary_json_path = (
                    Path(json_output_path)
                    if json_output_path
                    else export_dir / f"{export_stem}-{normalized_start_date}-to-{normalized_end_date}.json"
                )
                summary_csv_path = (
                    Path(csv_output_path)
                    if csv_output_path
                    else export_dir / f"{export_stem}-{normalized_start_date}-to-{normalized_end_date}.csv"
                )
                export_rows = by_day_rows if by_day_rows else [{"start_date": normalized_start_date, "end_date": normalized_end_date}]
                _write_json_file(summary_json_path, result_payload)
                _write_csv_file(summary_csv_path, export_rows)
                artifacts.update(
                    {
                        "json_output_path": str(summary_json_path),
                        "csv_output_path": str(summary_csv_path),
                    }
                )
            if artifacts:
                result_payload["artifacts"] = artifacts

            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="completed trade audit period report task",
                data=result_payload,
                warnings=warnings,
            )

        result, timing = _capture_task_timing("task.trade_audit_period_report", run)
        return self._attach_task_metadata(result, task_name="trade_audit_period_report", timing=timing)

    def trade_period_report(
        self,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        timezone_name: str | None = None,
        recent_limit: int | None = None,
        code: str | None = None,
        trade_ok: bool | None = None,
        task_name: str | None = None,
        ledger_jsonl_path: str | None = None,
        ledger_csv_path: str | None = None,
        json_output_path: str | None = None,
        csv_output_path: str | None = None,
    ) -> Result:
        def run() -> Result:
            if start_date is None and end_date is None:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="trade period report task requires start_date or end_date",
                    next_action="Provide --start-date, --end-date, or both in YYYY-MM-DD format.",
                )

            resolved_timezone_name = str(
                self.profile_options.get("default_timezone", "Asia/Shanghai")
                if timezone_name is None
                else timezone_name
            )
            try:
                tzinfo = ZoneInfo(resolved_timezone_name)
            except ZoneInfoNotFoundError:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"unsupported timezone: {resolved_timezone_name}",
                    next_action="Provide a valid IANA timezone such as Asia/Shanghai.",
                )

            raw_start_date = start_date or end_date or ""
            raw_end_date = end_date or start_date or ""
            try:
                normalized_start_date = _normalize_report_date_iso(raw_start_date)
                normalized_end_date = _normalize_report_date_iso(raw_end_date)
            except ValueError:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"invalid period date: {raw_start_date} -> {raw_end_date}",
                    next_action="Use start_date and end_date in YYYY-MM-DD format.",
                )
            if normalized_start_date > normalized_end_date:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="trade period report task requires start_date <= end_date",
                    next_action="Swap the date boundaries or correct the requested range.",
                )

            try:
                ledger_source = _load_task_ledger_source(
                    self.profile_options,
                    ledger_jsonl_path=ledger_jsonl_path,
                    ledger_csv_path=ledger_csv_path,
                )
            except FileNotFoundError:
                resolved_jsonl_path, resolved_csv_path = _resolve_task_ledger_paths(
                    self.profile_options,
                    ledger_jsonl_path=ledger_jsonl_path,
                    ledger_csv_path=ledger_csv_path,
                )
                return Result(
                    ok=False,
                    code=ErrorCode.PATH_NOT_FOUND,
                    message="trade period report task could not find a ledger file",
                    data={
                        "input": {
                            "ledger_jsonl_path": str(resolved_jsonl_path),
                            "ledger_csv_path": str(resolved_csv_path),
                        }
                    },
                    next_action="Run guarded trade workflows first or provide an explicit ledger path.",
                )

            entries = list(ledger_source["entries"])
            prefiltered_entries = _filter_task_ledger_entries(
                entries,
                code=code,
                trade_ok=trade_ok,
                task_name=task_name,
            )
            report_entries = _filter_entries_by_local_date_range(
                prefiltered_entries,
                tzinfo=tzinfo,
                start_date=normalized_start_date,
                end_date=normalized_end_date,
            )
            resolved_recent_limit = int(
                self.profile_options.get("default_recent_limit", 20) if recent_limit is None else recent_limit
            )
            ordered_entries = _sort_ledger_entries_newest_first(report_entries)
            recent_entries = ordered_entries if resolved_recent_limit <= 0 else ordered_entries[:resolved_recent_limit]
            by_day_rows = _aggregate_entries_by_day(report_entries, tzinfo=tzinfo)
            by_code_rows = _aggregate_entries_by_code(report_entries)
            success_count = sum(1 for entry in report_entries if _parse_boolish(entry.get("trade_ok")) is True)
            failed_count = sum(1 for entry in report_entries if _parse_boolish(entry.get("trade_ok")) is False)
            total_quantity = sum(int(row["total_quantity"]) for row in by_code_rows)
            total_amount = round(sum(float(row["total_amount"]) for row in by_code_rows), 4)
            latest_timestamp = recent_entries[0].get("timestamp") if recent_entries else None

            result_payload: dict[str, Any] = {
                "input": {
                    "start_date": normalized_start_date,
                    "end_date": normalized_end_date,
                    "timezone": resolved_timezone_name,
                    "recent_limit": resolved_recent_limit,
                    "code": code,
                    "trade_ok": trade_ok,
                    "task_name": task_name,
                    "ledger_jsonl_path": str(ledger_source["ledger_jsonl_path"]),
                    "ledger_csv_path": str(ledger_source["ledger_csv_path"]),
                },
                "source": {
                    "path": str(ledger_source["source_path"]),
                    "format": str(ledger_source["source_format"]),
                },
                "summary": {
                    "total_entries": len(entries),
                    "matched_entries": len(prefiltered_entries),
                    "report_entries": len(report_entries),
                    "trade_days": len(by_day_rows),
                    "success_count": success_count,
                    "failed_count": failed_count,
                    "unique_codes": [row["code"] for row in by_code_rows],
                    "total_quantity": total_quantity,
                    "total_amount": total_amount,
                    "latest_timestamp": latest_timestamp,
                },
                "by_day": by_day_rows,
                "by_code": by_code_rows,
                "entries": recent_entries,
            }

            artifacts: dict[str, Any] = {}
            if json_output_path is not None or csv_output_path is not None:
                export_dir = _resolve_export_dir(self.profile_options)
                export_stem = _resolve_export_stem(self.profile_options, "trade-period-report")
                range_suffix = f"{normalized_start_date}-to-{normalized_end_date}"
                summary_json_path = (
                    Path(json_output_path)
                    if json_output_path
                    else export_dir / f"{export_stem}-{range_suffix}.json"
                )
                summary_csv_path = (
                    Path(csv_output_path)
                    if csv_output_path
                    else export_dir / f"{export_stem}-{range_suffix}.csv"
                )
                export_rows = by_day_rows if by_day_rows else [{"start_date": normalized_start_date, "end_date": normalized_end_date}]
                _write_json_file(summary_json_path, result_payload)
                _write_csv_file(summary_csv_path, export_rows)
                artifacts.update(
                    {
                        "json_output_path": str(summary_json_path),
                        "csv_output_path": str(summary_csv_path),
                    }
                )
            if artifacts:
                result_payload["artifacts"] = artifacts

            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="completed trade period report task",
                data=result_payload,
            )

        result, timing = _capture_task_timing("task.trade_period_report", run)
        return self._attach_task_metadata(result, task_name="trade_period_report", timing=timing)

    def trade_buy(
        self,
        *,
        port: str,
        code: str,
        price: str,
        quantity: int,
        baudrate: int = 115200,
        timeout: float = 2.0,
        max_depth: int = 12,
        close_result_dialog: bool = True,
        submission_key: str | None = None,
        max_price: float | None = None,
        refresh_before_trade: bool | None = None,
        refresh_market: str | None = None,
        refresh_force: bool | None = None,
    ) -> Result:
        def run() -> Result:
            resolved_refresh_first = bool(
                self.profile_options.get("refresh_before_trade", False)
                if refresh_before_trade is None
                else refresh_before_trade
            )
            resolved_refresh_market = refresh_market if refresh_market is not None else self.profile_options.get("refresh_market")
            resolved_refresh_force = refresh_force if refresh_force is not None else self.profile_options.get("refresh_force")
            refresh_result: Result | None = None
            if resolved_refresh_first:
                refresh_result = self.api_manager.refresh_cache(
                    market=None if resolved_refresh_market is None else str(resolved_refresh_market),
                    force=None if resolved_refresh_force is None else bool(resolved_refresh_force),
                )
                if not refresh_result.ok:
                    return Result(
                        ok=False,
                        code=refresh_result.code,
                        message="trade buy task aborted during environment refresh",
                        data={
                            "input": {
                                "port": port,
                                "code": code,
                                "price": price,
                                "quantity": quantity,
                                "submission_key": submission_key,
                                "max_price": max_price,
                                "refresh_before_trade": resolved_refresh_first,
                                "refresh_market": resolved_refresh_market,
                                "refresh_force": resolved_refresh_force,
                            },
                            "refresh_result": refresh_result.to_dict(),
                        },
                        warnings=refresh_result.warnings,
                        next_action=refresh_result.next_action,
                    )
            trade_result = self.trade_manager.pingan.buy(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                code=code,
                price=price,
                quantity=quantity,
                max_depth=max_depth,
                close_result_dialog=close_result_dialog,
                submission_key=submission_key,
                max_price=max_price,
            )
            if not trade_result.ok:
                return trade_result
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="completed trade buy task",
                data={
                    "input": {
                        "port": port,
                        "code": code,
                        "price": price,
                        "quantity": quantity,
                        "baudrate": baudrate,
                        "timeout": timeout,
                        "max_depth": max_depth,
                        "close_result_dialog": close_result_dialog,
                        "submission_key": submission_key,
                        "max_price": max_price,
                        "refresh_before_trade": resolved_refresh_first,
                        "refresh_market": resolved_refresh_market,
                        "refresh_force": resolved_refresh_force,
                    },
                    "refresh_result": refresh_result.to_dict() if refresh_result is not None else None,
                    "trade_result": trade_result.to_dict(),
                    "artifacts": copy.deepcopy(trade_result.data.get("artifacts", {})),
                    "result_dialog": copy.deepcopy(trade_result.data.get("result_dialog", {})),
                },
                warnings=list(trade_result.warnings),
                next_action=trade_result.next_action,
            )

        result, timing = _capture_task_timing("task.trade_buy", run)
        return self._attach_task_metadata(result, task_name="trade_buy", timing=timing)

    def trade_submit_once(
        self,
        *,
        port: str,
        code: str,
        price: str,
        quantity: int,
        baudrate: int = 115200,
        timeout: float = 2.0,
        max_depth: int = 12,
        close_result_dialog: bool = True,
        submission_key: str | None = None,
        max_price: float | None = None,
        refresh_before_trade: bool | None = None,
        refresh_market: str | None = None,
        refresh_force: bool | None = None,
    ) -> Result:
        def run() -> Result:
            resolved_refresh_first = bool(
                self.profile_options.get("refresh_before_trade", False)
                if refresh_before_trade is None
                else refresh_before_trade
            )
            resolved_refresh_market = refresh_market if refresh_market is not None else self.profile_options.get("refresh_market")
            resolved_refresh_force = refresh_force if refresh_force is not None else self.profile_options.get("refresh_force")
            refresh_result: Result | None = None
            if resolved_refresh_first:
                refresh_result = self.api_manager.refresh_cache(
                    market=None if resolved_refresh_market is None else str(resolved_refresh_market),
                    force=None if resolved_refresh_force is None else bool(resolved_refresh_force),
                )
                if not refresh_result.ok:
                    return Result(
                        ok=False,
                        code=refresh_result.code,
                        message="trade submit-once task aborted during environment refresh",
                        data={
                            "input": {
                                "port": port,
                                "code": code,
                                "price": price,
                                "quantity": quantity,
                                "submission_key": submission_key,
                                "max_price": max_price,
                                "refresh_before_trade": resolved_refresh_first,
                                "refresh_market": resolved_refresh_market,
                                "refresh_force": resolved_refresh_force,
                            },
                            "refresh_result": refresh_result.to_dict(),
                        },
                        warnings=refresh_result.warnings,
                        next_action=refresh_result.next_action,
                    )
            trade_result = self.trade_manager.pingan.buy_submit_once(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                code=code,
                price=price,
                quantity=quantity,
                max_depth=max_depth,
                close_result_dialog=close_result_dialog,
                submission_key=submission_key,
                max_price=max_price,
            )
            if not trade_result.ok:
                return trade_result
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="completed trade submit-once task",
                data={
                    "input": {
                        "port": port,
                        "code": code,
                        "price": price,
                        "quantity": quantity,
                        "baudrate": baudrate,
                        "timeout": timeout,
                        "max_depth": max_depth,
                        "close_result_dialog": close_result_dialog,
                        "submission_key": submission_key,
                        "max_price": max_price,
                        "refresh_before_trade": resolved_refresh_first,
                        "refresh_market": resolved_refresh_market,
                        "refresh_force": resolved_refresh_force,
                    },
                    "refresh_result": refresh_result.to_dict() if refresh_result is not None else None,
                    "trade_result": trade_result.to_dict(),
                    "artifacts": copy.deepcopy(trade_result.data.get("artifacts", {})),
                    "result_dialog": copy.deepcopy(trade_result.data.get("result_dialog", {})),
                },
                warnings=list(trade_result.warnings),
                next_action=trade_result.next_action,
            )

        result, timing = _capture_task_timing("task.trade_submit_once", run)
        return self._attach_task_metadata(result, task_name="trade_submit_once", timing=timing)

    def trade_submit_ready(
        self,
        *,
        port: str,
        code: str,
        price: str,
        quantity: int,
        baudrate: int = 115200,
        timeout: float = 2.0,
        max_depth: int = 12,
        max_price: float | None = None,
        refresh_before_trade: bool | None = None,
        refresh_market: str | None = None,
        refresh_force: bool | None = None,
        dialog_lookup_mode: str | None = None,
        confirm_timeout: float | None = None,
    ) -> Result:
        def run() -> Result:
            resolved_refresh_first = bool(
                self.profile_options.get("refresh_before_trade", False)
                if refresh_before_trade is None
                else refresh_before_trade
            )
            resolved_refresh_market = refresh_market if refresh_market is not None else self.profile_options.get("refresh_market")
            resolved_refresh_force = refresh_force if refresh_force is not None else self.profile_options.get("refresh_force")
            refresh_result: Result | None = None
            if resolved_refresh_first:
                refresh_result = self.api_manager.refresh_cache(
                    market=None if resolved_refresh_market is None else str(resolved_refresh_market),
                    force=None if resolved_refresh_force is None else bool(resolved_refresh_force),
                )
                if not refresh_result.ok:
                    return Result(
                        ok=False,
                        code=refresh_result.code,
                        message="trade submit-ready task aborted during environment refresh",
                        data={
                            "input": {
                                "port": port,
                                "code": code,
                                "price": price,
                                "quantity": quantity,
                                "max_price": max_price,
                                "refresh_before_trade": resolved_refresh_first,
                                "refresh_market": resolved_refresh_market,
                                "refresh_force": resolved_refresh_force,
                                "dialog_lookup_mode": dialog_lookup_mode,
                                "confirm_timeout": confirm_timeout,
                            },
                            "refresh_result": refresh_result.to_dict(),
                        },
                        warnings=refresh_result.warnings,
                        next_action=refresh_result.next_action,
                    )
            trade_result = self.trade_manager.pingan.submit_ready(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                code=code,
                price=price,
                quantity=quantity,
                max_depth=max_depth,
                max_price=max_price,
                dialog_lookup_mode=dialog_lookup_mode,
                confirm_timeout=confirm_timeout,
            )
            if not trade_result.ok:
                return trade_result
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="completed trade submit-ready task",
                data={
                    "input": {
                        "port": port,
                        "code": code,
                        "price": price,
                        "quantity": quantity,
                        "baudrate": baudrate,
                        "timeout": timeout,
                        "max_depth": max_depth,
                        "max_price": max_price,
                        "refresh_before_trade": resolved_refresh_first,
                        "refresh_market": resolved_refresh_market,
                        "refresh_force": resolved_refresh_force,
                        "dialog_lookup_mode": dialog_lookup_mode,
                        "confirm_timeout": confirm_timeout,
                    },
                    "refresh_result": refresh_result.to_dict() if refresh_result is not None else None,
                    "trade_result": trade_result.to_dict(),
                    "artifacts": copy.deepcopy(trade_result.data.get("artifacts", {})),
                    "result_dialog": copy.deepcopy(trade_result.data.get("result_dialog", {})),
                },
                warnings=list(trade_result.warnings),
                next_action=trade_result.next_action,
            )

        result, timing = _capture_task_timing("task.trade_submit_ready", run)
        return self._attach_task_metadata(result, task_name="trade_submit_ready", timing=timing)

    def trade_confirm_current(
        self,
        *,
        dialog_lookup_mode: str | None = None,
        confirm_timeout: float | None = None,
        result_timeout: float | None = None,
        close_result_dialog: bool = True,
        result_close_pre_delay: float | None = None,
    ) -> Result:
        def run() -> Result:
            kwargs: dict[str, Any] = {
                "dialog_lookup_mode": dialog_lookup_mode,
                "confirm_timeout": confirm_timeout,
                "result_timeout": result_timeout,
                "close_result_dialog": close_result_dialog,
            }
            if result_close_pre_delay is not None:
                kwargs["result_close_pre_delay"] = result_close_pre_delay
            trade_result = self.trade_manager.pingan.confirm_current(**kwargs)
            if not trade_result.ok:
                return trade_result
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="completed trade confirm-current task",
                data={
                    "input": {
                        "dialog_lookup_mode": dialog_lookup_mode,
                        "confirm_timeout": confirm_timeout,
                        "result_timeout": result_timeout,
                        "close_result_dialog": close_result_dialog,
                        "result_close_pre_delay": result_close_pre_delay,
                    },
                    "trade_result": trade_result.to_dict(),
                    "artifacts": copy.deepcopy(trade_result.data.get("artifacts", {})),
                    "result_dialog": copy.deepcopy(trade_result.data.get("result_dialog", {})),
                },
                warnings=list(trade_result.warnings),
                next_action=trade_result.next_action,
            )

        result, timing = _capture_task_timing("task.trade_confirm_current", run)
        return self._attach_task_metadata(result, task_name="trade_confirm_current", timing=timing)

    def guarded_trade_buy(
        self,
        *,
        port: str,
        code: str,
        price: str,
        quantity: int,
        baudrate: int = 115200,
        timeout: float = 2.0,
        max_depth: int = 12,
        close_result_dialog: bool = True,
        submission_key: str | None = None,
        max_price: float | None = None,
        refresh_before_trade: bool | None = None,
        refresh_market: str | None = None,
        refresh_force: bool | None = None,
        max_snapshot_price: float | None = None,
        required_block_code: str | None = None,
        required_block_type: int = 0,
        required_list_type: int | None = None,
        formula_name: str | None = None,
        formula_arg: str = "",
        formula_return_count: int = 1,
        formula_return_date: bool = False,
        formula_stock_period: str = "1d",
        formula_start_time: str = "",
        formula_end_time: str = "",
        formula_count: int = 0,
        formula_dividend_type: int = 0,
        json_output_path: str | None = None,
        csv_output_path: str | None = None,
    ) -> Result:
        def run() -> Result:
            snapshot_result: Result | None = None
            snapshot_now: float | None = None
            if max_snapshot_price is not None:
                snapshot_result = self.api_manager.market.snapshot(code, fields=["Now"])
                if not snapshot_result.ok:
                    return Result(
                        ok=False,
                        code=snapshot_result.code,
                        message="guarded trade buy task aborted during snapshot precheck",
                        data={"snapshot_result": snapshot_result.to_dict()},
                        warnings=snapshot_result.warnings,
                        next_action=snapshot_result.next_action,
                    )
                snapshot_now = _extract_numeric_field(snapshot_result.data, ["Now", "now", "price", "last"])
                if snapshot_now is None:
                    return Result(
                        ok=False,
                        code=ErrorCode.EXECUTION_FAILED,
                        message="guarded trade buy task could not extract current price from snapshot result",
                        data={"snapshot_result": snapshot_result.to_dict()},
                        next_action="Inspect the snapshot response shape and refine the extraction rule.",
                    )
                if snapshot_now > float(max_snapshot_price):
                    return Result(
                        ok=False,
                        code=ErrorCode.INVALID_REQUEST,
                        message="guarded trade buy task blocked because snapshot price exceeded the configured maximum",
                        data={
                            "snapshot_result": snapshot_result.to_dict(),
                            "snapshot_now": snapshot_now,
                            "max_snapshot_price": max_snapshot_price,
                        },
                        next_action="Raise the max snapshot price or wait for the market price to move into range.",
                    )

            block_result: Result | None = None
            block_membership_ok: bool | None = None
            if required_block_code is not None:
                block_result = self.api_manager.meta.sector_stocks(
                    block_code=required_block_code,
                    block_type=required_block_type,
                    list_type=required_list_type,
                )
                if not block_result.ok:
                    return Result(
                        ok=False,
                        code=block_result.code,
                        message="guarded trade buy task aborted during block membership precheck",
                        data={"block_result": block_result.to_dict()},
                        warnings=block_result.warnings,
                        next_action=block_result.next_action,
                    )
                stock_codes = _extract_stock_codes(block_result.data)
                block_membership_ok = code in stock_codes
                if not block_membership_ok:
                    return Result(
                        ok=False,
                        code=ErrorCode.INVALID_REQUEST,
                        message="guarded trade buy task blocked because the stock is not in the required block",
                        data={
                            "required_block_code": required_block_code,
                            "required_block_type": required_block_type,
                            "required_list_type": required_list_type,
                            "block_result": block_result.to_dict(),
                        },
                        next_action="Adjust the required block constraint or verify the target stock universe.",
                    )

            formula_result: Result | None = None
            formula_check_ok: bool | None = None
            if formula_name is not None:
                formula_result = self.formula_scan(
                    formula_name=formula_name,
                    stock_list=[code],
                    formula_arg=formula_arg,
                    return_count=formula_return_count,
                    return_date=formula_return_date,
                    stock_period=formula_stock_period,
                    start_time=formula_start_time,
                    end_time=formula_end_time,
                    count=formula_count,
                    dividend_type=formula_dividend_type,
                )
                if not formula_result.ok:
                    return Result(
                        ok=False,
                        code=formula_result.code,
                        message="guarded trade buy task aborted during formula precheck",
                        data={"formula_result": formula_result.to_dict()},
                        warnings=formula_result.warnings,
                        next_action=formula_result.next_action,
                    )
                formula_check_ok = _formula_scan_has_match(formula_result.data, code)
                if not formula_check_ok:
                    return Result(
                        ok=False,
                        code=ErrorCode.INVALID_REQUEST,
                        message="guarded trade buy task blocked because the formula precheck did not match the target stock",
                        data={
                            "formula_name": formula_name,
                            "formula_arg": formula_arg,
                            "formula_result": formula_result.to_dict(),
                        },
                        next_action="Adjust the formula constraint or wait until the formula condition matches the target stock.",
                    )

            trade_result = self.trade_buy(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                code=code,
                price=price,
                quantity=quantity,
                max_depth=max_depth,
                close_result_dialog=close_result_dialog,
                submission_key=submission_key,
                max_price=max_price,
                refresh_before_trade=refresh_before_trade,
                refresh_market=refresh_market,
                refresh_force=refresh_force,
            )
            if not trade_result.ok:
                return trade_result

            export_dir = _resolve_export_dir(self.profile_options)
            export_stem = _resolve_export_stem(self.profile_options, f"guarded-trade-buy-{code}")
            ledger_stem = _resolve_ledger_stem(self.profile_options, "guarded-trade-buy-ledger")
            json_path = Path(json_output_path) if json_output_path else export_dir / f"{export_stem}.json"
            csv_path = Path(csv_output_path) if csv_output_path else export_dir / f"{export_stem}.csv"
            ledger_jsonl_path = export_dir / f"{ledger_stem}.jsonl"
            ledger_csv_path = export_dir / f"{ledger_stem}.csv"
            report_payload = {
                    "input": {
                    "port": port,
                    "code": code,
                    "price": price,
                    "quantity": quantity,
                    "baudrate": baudrate,
                    "timeout": timeout,
                    "max_depth": max_depth,
                    "close_result_dialog": close_result_dialog,
                    "submission_key": submission_key,
                    "max_price": max_price,
                    "refresh_before_trade": refresh_before_trade,
                    "refresh_market": refresh_market,
                    "refresh_force": refresh_force,
                    "max_snapshot_price": max_snapshot_price,
                        "required_block_code": required_block_code,
                        "required_block_type": required_block_type,
                        "required_list_type": required_list_type,
                        "formula_name": formula_name,
                        "formula_arg": formula_arg,
                        "formula_return_count": formula_return_count,
                        "formula_return_date": formula_return_date,
                        "formula_stock_period": formula_stock_period,
                        "formula_start_time": formula_start_time,
                        "formula_end_time": formula_end_time,
                        "formula_count": formula_count,
                        "formula_dividend_type": formula_dividend_type,
                    },
                    "prechecks": {
                        "snapshot_result": snapshot_result.to_dict() if snapshot_result is not None else None,
                        "snapshot_now": snapshot_now,
                        "snapshot_price_check_passed": None if max_snapshot_price is None else True,
                        "block_result": block_result.to_dict() if block_result is not None else None,
                        "block_membership_check_passed": block_membership_ok,
                        "formula_result": formula_result.to_dict() if formula_result is not None else None,
                        "formula_check_passed": formula_check_ok,
                    },
                    "trade_result": trade_result.to_dict(),
                }
            _write_json_file(json_path, report_payload)
            _write_csv_file(
                csv_path,
                [
                    {
                        "code": code,
                        "price": price,
                        "quantity": quantity,
                        "snapshot_now": snapshot_now,
                        "max_snapshot_price": max_snapshot_price,
                        "required_block_code": required_block_code or "",
                        "block_membership_check_passed": block_membership_ok,
                        "formula_name": formula_name or "",
                        "formula_check_passed": formula_check_ok,
                        "trade_ok": trade_result.ok,
                        "contract_no": trade_result.data.get("result_dialog", {}).get("contract_no", ""),
                    }
                ],
            )
            ledger_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "task_name": "guarded_trade_buy",
                "code": code,
                "price": price,
                "quantity": quantity,
                "snapshot_now": snapshot_now,
                "max_snapshot_price": max_snapshot_price,
                "snapshot_price_check_passed": None if max_snapshot_price is None else True,
                "required_block_code": required_block_code or "",
                "block_membership_check_passed": block_membership_ok,
                "formula_name": formula_name or "",
                "formula_check_passed": formula_check_ok,
                "trade_ok": trade_result.ok,
                "contract_no": trade_result.data.get("result_dialog", {}).get("contract_no", ""),
                "report_json_path": str(json_path),
                "report_csv_path": str(csv_path),
            }
            _append_jsonl_file(ledger_jsonl_path, ledger_entry)
            _append_csv_row(ledger_csv_path, ledger_entry)
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="completed guarded trade buy task",
                data={
                    "input": report_payload["input"],
                    "prechecks": report_payload["prechecks"],
                    "trade_result": trade_result.to_dict(),
                    "result_dialog": copy.deepcopy(trade_result.data.get("result_dialog", {})),
                    "artifacts": {
                        **copy.deepcopy(trade_result.data.get("artifacts", {})),
                        "json_output_path": str(json_path),
                        "csv_output_path": str(csv_path),
                        "ledger_jsonl_path": str(ledger_jsonl_path),
                        "ledger_csv_path": str(ledger_csv_path),
                    },
                },
                warnings=list(trade_result.warnings),
                next_action=trade_result.next_action,
            )

        result, timing = _capture_task_timing("task.guarded_trade_buy", run)
        return self._attach_task_metadata(result, task_name="guarded_trade_buy", timing=timing)
