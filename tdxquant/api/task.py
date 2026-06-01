from __future__ import annotations

import copy
import csv
import json
import os
import threading
import time
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from uuid import uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from ..block_watchlist_import import load_watchlist_import_file, plan_watchlist_import, sync_watchlist_import_request
from ..models import ErrorCode, Result
from ..replay_provider import materialize_subscription_watch_replay
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
from ..trade import TdxTradeManager, get_pingan_submission_ledger_path
from ..trade_audit_index import query_trade_audit_cross_ledger
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


def _build_task_lifecycle_owner_lock_guard_kwargs(
    *,
    lifecycle_statefile_path: str | None,
    lifecycle_owner_token: str | None,
    lifecycle_stale_after_seconds: float,
    require_lifecycle_owner_lock: bool,
) -> dict[str, Any]:
    if not (
        require_lifecycle_owner_lock
        or lifecycle_statefile_path is not None
        or lifecycle_owner_token is not None
        or lifecycle_stale_after_seconds != 300.0
    ):
        return {}
    return {
        "lifecycle_statefile_path": lifecycle_statefile_path,
        "lifecycle_owner_token": lifecycle_owner_token,
        "lifecycle_stale_after_seconds": lifecycle_stale_after_seconds,
        "require_lifecycle_owner_lock": require_lifecycle_owner_lock,
    }


def _build_task_broker_readiness_guard_kwargs(*, require_broker_readiness: bool) -> dict[str, Any]:
    if not require_broker_readiness:
        return {}
    return {"require_broker_readiness": True}


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


def _write_json_file_atomic(path: Path, payload: Any, *, overwrite: bool = True) -> Path:
    temp_path = path.parent / f".{path.name}.{uuid4().hex}.tmp"
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    try:
        temp_path.write_text(serialized, encoding="utf-8")
        if overwrite:
            temp_path.replace(path)
        else:
            os.link(temp_path, path)
            temp_path.unlink()
    except Exception:
        try:
            temp_path.unlink()
        except OSError:
            pass
        raise
    return path


def _probe_directory_writable(path: Path) -> None:
    probe_path = path / f".tdxquant-write-probe.{uuid4().hex}.tmp"
    try:
        probe_path.write_text("", encoding="utf-8")
    finally:
        try:
            probe_path.unlink()
        except FileNotFoundError:
            pass


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


def _extract_trade_audit_result_data(entry: dict[str, Any]) -> dict[str, Any]:
    payload = entry.get("payload")
    if not isinstance(payload, dict):
        return {}
    result_payload = payload.get("result")
    if not isinstance(result_payload, dict):
        return {}
    data_payload = result_payload.get("data", result_payload)
    if not isinstance(data_payload, dict):
        return {}
    return data_payload


def _first_present_value(payload: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in payload:
            return payload[key]
    return None


def _coerce_trade_audit_decimal(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str) and not value.strip():
        return None
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    if not parsed.is_finite():
        return None
    return parsed


def _extract_trade_audit_requested_order_value(entry: dict[str, Any]) -> Decimal | None:
    result_data = _extract_trade_audit_result_data(entry)
    price = _coerce_trade_audit_decimal(_first_present_value(result_data, ("price", "requested_price")))
    quantity = _coerce_trade_audit_decimal(_first_present_value(result_data, ("quantity", "requested_quantity")))
    if price is None or quantity is None:
        return None
    return price * quantity


def _format_trade_audit_decimal(value: Decimal) -> str:
    return format(value, "f")


def _new_trade_audit_value_bucket(label_key: str, label_value: str) -> dict[str, Any]:
    return {
        label_key: label_value,
        "entries_count": 0,
        "priced_entries": 0,
        "unpriced_entries": 0,
        "requested_order_value": Decimal("0"),
    }


def _record_trade_audit_value(bucket: dict[str, Any], requested_value: Decimal | None) -> None:
    bucket["entries_count"] += 1
    if requested_value is None:
        bucket["unpriced_entries"] += 1
        return
    bucket["priced_entries"] += 1
    bucket["requested_order_value"] += requested_value


def _finalize_trade_audit_value_bucket(bucket: dict[str, Any]) -> dict[str, Any]:
    return {
        key: (_format_trade_audit_decimal(value) if isinstance(value, Decimal) else value)
        for key, value in bucket.items()
    }


def _build_trade_audit_value_diagnostics(entries: list[dict[str, Any]], *, scope: str) -> dict[str, Any]:
    total_bucket = _new_trade_audit_value_bucket("scope", scope)
    by_status: dict[str, dict[str, Any]] = {}
    by_method: dict[str, dict[str, Any]] = {}
    for entry in entries:
        trade_audit = entry.get("trade_audit", {})
        requested_value = _extract_trade_audit_requested_order_value(entry)
        _record_trade_audit_value(total_bucket, requested_value)

        status = str(trade_audit.get("status", "")).strip() or "<unknown>"
        status_bucket = by_status.setdefault(status, _new_trade_audit_value_bucket("status", status))
        _record_trade_audit_value(status_bucket, requested_value)

        method = str(trade_audit.get("method", "")).strip() or "<unknown>"
        method_bucket = by_method.setdefault(method, _new_trade_audit_value_bucket("method", method))
        _record_trade_audit_value(method_bucket, requested_value)

    total_view = _finalize_trade_audit_value_bucket(total_bucket)
    return {
        "schema_version": "tdx.trade_audit.requested_value_diagnostics.v1",
        "scope": scope,
        "calculation": "requested_order_value = price * quantity from audit result data; excludes fills, fees, execution quality, account balances, and PnL.",
        "entries_count": total_view["entries_count"],
        "priced_entries": total_view["priced_entries"],
        "unpriced_entries": total_view["unpriced_entries"],
        "requested_order_value": total_view["requested_order_value"],
        "by_status": [_finalize_trade_audit_value_bucket(by_status[status]) for status in sorted(by_status)],
        "by_method": [_finalize_trade_audit_value_bucket(by_method[method]) for method in sorted(by_method)],
    }


_PINGAN_ACCEPTANCE_OUTCOME_COVERAGE_SCHEMA = "tdx.desktop_trade.pingan_acceptance_outcome_coverage_status.v1"
_PINGAN_LIVE_MANUAL_ACCEPTANCE_SCHEMA = "tdx.desktop_trade.pingan_live_manual_acceptance.v1"
_PINGAN_LIVE_MANUAL_ACCEPTANCE_RECORD_SCHEMA = "tdx.desktop_trade.pingan_live_manual_acceptance_record.v1"
_PINGAN_READINESS_EVIDENCE_ARTIFACT_PROVENANCE_SCHEMA = (
    "tdx.desktop_trade.pingan_readiness_evidence_artifact.v1"
)
_PINGAN_REQUIRED_AUTOMATED_OUTCOME_STATUSES = ("confirmed", "rejected", "failed", "exception")


def _build_pingan_readiness_evidence_artifact_provenance(
    *, source_kind: str, producer: str, evidence_schema: str
) -> dict[str, Any]:
    return {
        "schema": _PINGAN_READINESS_EVIDENCE_ARTIFACT_PROVENANCE_SCHEMA,
        "source_kind": source_kind,
        "producer": producer,
        "evidence_schema": evidence_schema,
    }


def _build_pingan_live_manual_acceptance_artifact_provenance_status(payload: dict[str, Any]) -> dict[str, Any]:
    provenance = payload.get("artifact_provenance")
    provenance = provenance if isinstance(provenance, dict) else None
    observed_schema = provenance.get("schema") if provenance else None
    observed_source_kind = provenance.get("source_kind") if provenance else None
    observed_producer = provenance.get("producer") if provenance else None
    observed_evidence_schema = provenance.get("evidence_schema") if provenance else None

    invalid_reasons: list[str] = []
    if provenance is None:
        invalid_reasons.append("missing_artifact_provenance")
    elif observed_schema != _PINGAN_READINESS_EVIDENCE_ARTIFACT_PROVENANCE_SCHEMA:
        invalid_reasons.append("invalid_artifact_provenance_schema")
    if provenance is not None and observed_source_kind != "live_manual_acceptance":
        invalid_reasons.append("source_kind_mismatch")
    if provenance is not None and observed_evidence_schema != _PINGAN_LIVE_MANUAL_ACCEPTANCE_SCHEMA:
        invalid_reasons.append("evidence_schema_mismatch")
    if provenance is not None and observed_producer != "task pingan-live-manual-acceptance":
        invalid_reasons.append("unsupported_producer")

    verified = not invalid_reasons
    return {
        "status": "verified" if verified else "unverified",
        "schema": observed_schema,
        "expected_schema": _PINGAN_READINESS_EVIDENCE_ARTIFACT_PROVENANCE_SCHEMA,
        "source_kind": observed_source_kind,
        "expected_source_kind": "live_manual_acceptance",
        "producer": observed_producer,
        "expected_producer": "task pingan-live-manual-acceptance",
        "evidence_schema": observed_evidence_schema,
        "expected_evidence_schema": _PINGAN_LIVE_MANUAL_ACCEPTANCE_SCHEMA,
        "invalid_reasons": invalid_reasons,
    }


def _normalize_pingan_live_manual_acceptance_outcomes(outcomes: list[str] | None) -> tuple[list[str], list[str], list[str]]:
    normalized = sorted({str(item).strip() for item in outcomes or [] if str(item).strip()})
    invalid = [status for status in normalized if status not in _PINGAN_REQUIRED_AUTOMATED_OUTCOME_STATUSES]
    missing = [status for status in _PINGAN_REQUIRED_AUTOMATED_OUTCOME_STATUSES if status not in normalized]
    return normalized, invalid, missing


def _build_pingan_live_manual_acceptance_artifact(
    *,
    operator: str,
    environment: str,
    outcomes: list[str],
    accepted_at: str,
    evidence_ref: str | None = None,
) -> dict[str, Any]:
    artifact: dict[str, Any] = {
        "schema": _PINGAN_LIVE_MANUAL_ACCEPTANCE_SCHEMA,
        "artifact_provenance": _build_pingan_readiness_evidence_artifact_provenance(
            source_kind="live_manual_acceptance",
            producer="task pingan-live-manual-acceptance",
            evidence_schema=_PINGAN_LIVE_MANUAL_ACCEPTANCE_SCHEMA,
        ),
        "operator": operator,
        "environment": environment,
        "accepted_at": accepted_at,
        "outcomes": [{"status": status, "accepted": True} for status in outcomes],
        "boundary": (
            "Operator-provided live/manual acceptance evidence only; does not execute PingAn workflows, "
            "control the desktop, submit orders, prove broker production readiness, or promote D-07/D-08 status."
        ),
    }
    if evidence_ref:
        artifact["evidence_ref"] = evidence_ref
    return artifact


def _build_pingan_live_manual_acceptance_status(live_manual_acceptance_path: str | None) -> dict[str, Any]:
    required_outcomes = list(_PINGAN_REQUIRED_AUTOMATED_OUTCOME_STATUSES)
    if not live_manual_acceptance_path:
        return {
            "status": "not_provided",
            "required_for_implemented_status": True,
            "source_path": None,
            "schema": None,
            "covered_outcomes": [],
            "missing_outcomes": required_outcomes,
            "invalid_outcome_count": 0,
            "artifact_provenance_status": {"status": "not_provided", "invalid_reasons": []},
            "operator": None,
            "environment": None,
            "boundary": (
                "Live/manual acceptance evidence was not provided; D-07/D-08 cannot be treated as implemented."
            ),
        }

    source_path = Path(live_manual_acceptance_path)
    base_status: dict[str, Any] = {
        "required_for_implemented_status": True,
        "source_path": str(source_path),
        "covered_outcomes": [],
        "missing_outcomes": required_outcomes,
        "invalid_outcome_count": 0,
        "artifact_provenance_status": {"status": "not_provided", "invalid_reasons": []},
        "operator": None,
        "environment": None,
        "boundary": (
            "Live/manual acceptance evidence is operator-provided read-only report evidence; it does not "
            "execute trades, control the desktop, prove broker production readiness, or promote D-07/D-08 status."
        ),
    }
    try:
        payload = json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            **base_status,
            "status": "invalid",
            "schema": None,
            "error": str(exc),
        }
    if not isinstance(payload, dict):
        return {
            **base_status,
            "status": "invalid",
            "schema": None,
            "error": "live/manual acceptance evidence must be a JSON object",
        }

    schema = payload.get("schema")
    outcomes = payload.get("outcomes")
    if not isinstance(outcomes, list):
        outcomes = []
    covered_outcomes: set[str] = set()
    invalid_outcome_count = 0
    for item in outcomes:
        if not isinstance(item, dict):
            invalid_outcome_count += 1
            continue
        status = str(item.get("status") or "").strip()
        accepted = bool(item.get("accepted"))
        if status in _PINGAN_REQUIRED_AUTOMATED_OUTCOME_STATUSES and accepted:
            covered_outcomes.add(status)
        else:
            invalid_outcome_count += 1
    missing_outcomes = [
        status for status in _PINGAN_REQUIRED_AUTOMATED_OUTCOME_STATUSES if status not in covered_outcomes
    ]
    schema_valid = schema == _PINGAN_LIVE_MANUAL_ACCEPTANCE_SCHEMA
    artifact_provenance_status = _build_pingan_live_manual_acceptance_artifact_provenance_status(payload)
    artifact_provenance_verified = artifact_provenance_status.get("status") == "verified"
    status = (
        "complete"
        if schema_valid and not missing_outcomes and invalid_outcome_count == 0 and artifact_provenance_verified
        else "incomplete"
    )
    result = {
        **base_status,
        "status": status,
        "schema": schema,
        "schema_valid": schema_valid,
        "covered_outcomes": sorted(covered_outcomes),
        "missing_outcomes": missing_outcomes,
        "invalid_outcome_count": invalid_outcome_count,
        "artifact_provenance": payload.get("artifact_provenance"),
        "artifact_provenance_status": artifact_provenance_status,
        "operator": payload.get("operator"),
        "environment": payload.get("environment"),
        "accepted_at": payload.get("accepted_at"),
    }
    if not schema_valid:
        result["error"] = f"expected schema {_PINGAN_LIVE_MANUAL_ACCEPTANCE_SCHEMA}"
    return result


def _build_pingan_acceptance_outcome_coverage_status(
    entries: list[dict[str, Any]],
    *,
    source_kind: str,
    producer: str,
    live_manual_acceptance_path: str | None = None,
) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    for entry in entries:
        trade_audit = entry.get("trade_audit", {})
        status = str(trade_audit.get("status", "")).strip() or "<unknown>"
        status_counts[status] = status_counts.get(status, 0) + 1

    covered_statuses = sorted(status_counts)
    missing_automated_statuses = [
        status for status in _PINGAN_REQUIRED_AUTOMATED_OUTCOME_STATUSES if status_counts.get(status, 0) <= 0
    ]
    automated_outcome_coverage_complete = not missing_automated_statuses
    live_manual_acceptance_status = _build_pingan_live_manual_acceptance_status(live_manual_acceptance_path)
    live_manual_acceptance_complete = live_manual_acceptance_status.get("status") == "complete"
    live_manual_acceptance_provenance_status = live_manual_acceptance_status.get(
        "artifact_provenance_status",
        {"status": "not_provided", "invalid_reasons": []},
    )

    return {
        "schema": _PINGAN_ACCEPTANCE_OUTCOME_COVERAGE_SCHEMA,
        "status": "partial",
        "source_kind": source_kind,
        "artifact_provenance": _build_pingan_readiness_evidence_artifact_provenance(
            source_kind="acceptance_coverage",
            producer=producer,
            evidence_schema=_PINGAN_ACCEPTANCE_OUTCOME_COVERAGE_SCHEMA,
        ),
        "evidence_scope": "selected_trade_audit_entries",
        "execution_mode": "readonly_report",
        "side_effect_level": "none",
        "entries_count": len(entries),
        "required_automated_outcome_statuses": list(_PINGAN_REQUIRED_AUTOMATED_OUTCOME_STATUSES),
        "covered_outcome_statuses": covered_statuses,
        "covered_outcome_status_counts": {status: status_counts[status] for status in covered_statuses},
        "missing_automated_outcome_statuses": missing_automated_statuses,
        "automated_outcome_coverage_complete": automated_outcome_coverage_complete,
        "live_manual_acceptance_required": True,
        "live_manual_acceptance_complete": live_manual_acceptance_complete,
        "live_manual_acceptance_provenance_status": live_manual_acceptance_provenance_status,
        "live_manual_acceptance": live_manual_acceptance_status,
        "acceptance_complete": bool(automated_outcome_coverage_complete and live_manual_acceptance_complete),
        "order_submitted": False,
        "control_dispatch_executed": False,
        "boundary": (
            "Read-only report coverage from selected immutable audit artifacts and optional operator-provided "
            "live/manual acceptance evidence; does not execute trades or prove broker readiness, production "
            "readiness, or D-07/D-08 implemented status."
        ),
    }


_PINGAN_PROMOTION_READINESS_ROLLUP_SCHEMA = "tdx.desktop_trade.pingan_promotion_readiness_rollup.v1"
_PINGAN_PROMOTION_READINESS_ROLLUP_ARTIFACT_SCHEMA = (
    "tdx.desktop_trade.pingan_promotion_readiness_rollup_artifact.v1"
)
_PINGAN_PROMOTION_READINESS_MANIFEST_SCHEMA = "tdx.desktop_trade.pingan_promotion_readiness_manifest.v1"
_PINGAN_IMPLEMENTED_STATUS_PROMOTION_DECISION_SCHEMA = (
    "tdx.desktop_trade.pingan_implemented_status_promotion_decision.v1"
)
_PINGAN_IMPLEMENTED_STATUS_REVIEW_PACKET_SCHEMA = (
    "tdx.desktop_trade.pingan_implemented_status_review_packet.v1"
)
_PINGAN_IMPLEMENTED_STATUS_REVIEW_RESULT_SCHEMA = (
    "tdx.desktop_trade.pingan_implemented_status_review_result.v1"
)
_PINGAN_IMPLEMENTED_STATUS_REVIEW_RESULT_RECORD_SCHEMA = (
    "tdx.desktop_trade.pingan_implemented_status_review_result_record.v1"
)
_PINGAN_IMPLEMENTED_STATUS_TRANSITION_GATE_SCHEMA = (
    "tdx.desktop_trade.pingan_implemented_status_transition_gate.v1"
)
_PINGAN_IMPLEMENTED_STATUS_TRANSITION_RECORD_SCHEMA = (
    "tdx.desktop_trade.pingan_implemented_status_transition_record.v1"
)
_PINGAN_PROMOTION_READINESS_EVIDENCE_CONTRACT_SCHEMA = (
    "tdx.desktop_trade.pingan_promotion_readiness_evidence_contract.v1"
)
_PINGAN_PROMOTION_READINESS_GATE_ORDER = (
    "provider_broker_ownership",
    "safety_gates",
    "desktop_lifecycle",
    "audit_evidence",
    "live_manual_acceptance",
    "acceptance_evidence",
)


def _load_json_evidence(path: str | None) -> tuple[dict[str, Any] | None, str | None]:
    if path is None:
        return None, None
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(payload, dict):
        return None, "evidence JSON must contain an object"
    return payload, None


def _load_pingan_promotion_readiness_manifest(
    path: str | None,
) -> tuple[dict[str, Any], dict[str, Any], str | None]:
    metadata: dict[str, Any] = {
        "schema": _PINGAN_PROMOTION_READINESS_MANIFEST_SCHEMA,
        "source_path": path,
        "loaded": False,
        "expected_gates": [],
        "missing_expected_gates": [],
        "resolved_overrides": [],
    }
    if path is None:
        return {}, metadata, None
    payload, error = _load_json_evidence(path)
    if error is not None:
        metadata["error"] = error
        return {}, metadata, error
    if payload is None:
        metadata["error"] = "manifest is missing"
        return {}, metadata, "manifest is missing"
    schema = payload.get("schema")
    metadata["schema"] = schema
    if schema != _PINGAN_PROMOTION_READINESS_MANIFEST_SCHEMA:
        error = f"expected schema {_PINGAN_PROMOTION_READINESS_MANIFEST_SCHEMA}"
        metadata["error"] = error
        return {}, metadata, error

    values: dict[str, Any] = {}
    for key in ("preflight_path", "dialog_readiness_path", "acceptance_coverage_path"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            values[key] = value.strip()
    max_age = payload.get("max_evidence_age_seconds")
    if isinstance(max_age, (int, float)):
        values["max_evidence_age_seconds"] = max_age
    expected_gates = payload.get("expected_gates")
    if isinstance(expected_gates, list):
        metadata["expected_gates"] = [str(gate).strip() for gate in expected_gates if str(gate).strip()]
    for key in ("example_only", "sample_only"):
        value = payload.get(key)
        if isinstance(value, bool):
            metadata[key] = value
    metadata["loaded"] = True
    return values, metadata, None


def _find_json_object(payload: dict[str, Any] | None, key: str) -> dict[str, Any] | None:
    if payload is None:
        return None
    stack: list[dict[str, Any]] = [payload]
    while stack:
        current = stack.pop()
        value = current.get(key)
        if isinstance(value, dict):
            return value
        for child in current.values():
            if isinstance(child, dict):
                stack.append(child)
    return None


def _json_status_text(payload: dict[str, Any] | None, *, default: str) -> str:
    if payload is None:
        return default
    status = payload.get("status")
    if isinstance(status, str) and status.strip():
        return status.strip()
    return default


def _json_status_is_ready(payload: dict[str, Any] | None) -> bool:
    if payload is None:
        return False
    status = _json_status_text(payload, default="").lower()
    if status in {"ready", "complete", "passed", "ok"}:
        return True
    if payload.get("complete") is True:
        return True
    return payload.get("ready") is True


def _build_rollup_gate_status(
    *,
    status: str,
    complete: bool,
    source_kind: str,
    source_path: str | None,
    reason: str,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": status,
        "complete": complete,
        "source_kind": source_kind,
        "reason": reason,
    }
    if source_path is not None:
        payload["source_path"] = source_path
    return payload


def _build_evidence_freshness_status(
    source_paths: dict[str, str],
    *,
    max_evidence_age_seconds: float | None,
) -> tuple[dict[str, dict[str, Any]], list[str], dict[str, str]]:
    source_kinds = ("preflight", "dialog_readiness", "acceptance_coverage")
    freshness: dict[str, dict[str, Any]] = {}
    stale_kinds: list[str] = []
    stale_paths: dict[str, str] = {}
    now = time.time()
    for source_kind in source_kinds:
        source_path = source_paths.get(source_kind)
        entry: dict[str, Any] = {
            "source_kind": source_kind,
            "source_path": source_path,
            "max_evidence_age_seconds": max_evidence_age_seconds,
        }
        if source_path is None:
            entry["status"] = "missing"
        elif max_evidence_age_seconds is None:
            entry["status"] = "not_checked"
        else:
            try:
                modified_at = Path(source_path).stat().st_mtime
            except OSError as exc:
                entry["status"] = "unreadable"
                entry["error"] = str(exc)
                stale_kinds.append(source_kind)
                stale_paths[source_kind] = source_path
            else:
                age_seconds = max(0.0, now - modified_at)
                entry["modified_at_epoch"] = modified_at
                entry["age_seconds"] = round(age_seconds, 3)
                if age_seconds > max_evidence_age_seconds:
                    entry["status"] = "stale"
                    stale_kinds.append(source_kind)
                    stale_paths[source_kind] = source_path
                else:
                    entry["status"] = "fresh"
        freshness[source_kind] = entry
    return freshness, stale_kinds, stale_paths


def _apply_stale_evidence_to_rollup_gates(
    gate_statuses: dict[str, dict[str, Any]],
    stale_evidence_kinds: list[str],
) -> None:
    affected_gates = {
        "preflight": ("provider_broker_ownership", "safety_gates"),
        "dialog_readiness": ("desktop_lifecycle",),
        "acceptance_coverage": ("audit_evidence", "live_manual_acceptance", "acceptance_evidence"),
    }
    for source_kind in stale_evidence_kinds:
        for gate_name in affected_gates.get(source_kind, ()):
            gate = gate_statuses[gate_name]
            gate["complete"] = False
            gate["status"] = "stale_evidence"
            gate["reason"] = f"{source_kind} evidence is stale or unreadable"


def _build_pingan_evidence_contract_status(
    *,
    preflight_status: dict[str, Any] | None,
    desktop_lifecycle_status: dict[str, Any] | None,
    acceptance_status: dict[str, Any] | None,
    source_paths: dict[str, str],
) -> dict[str, Any]:
    requirements = {
        "preflight": {
            "payload": preflight_status,
            "schema_key": "schema_version",
            "expected_schema": "tdx.desktop_trade.pingan_promotion_gate_status.v1",
        },
        "dialog_readiness": {
            "payload": desktop_lifecycle_status,
            "schema_key": "schema_version",
            "expected_schema": "tdx.desktop_trade.pingan_desktop_lifecycle_gate_status.v1",
        },
        "acceptance_coverage": {
            "payload": acceptance_status,
            "schema_key": "schema",
            "expected_schema": _PINGAN_ACCEPTANCE_OUTCOME_COVERAGE_SCHEMA,
        },
    }
    source_statuses: dict[str, dict[str, Any]] = {}
    invalid_source_kinds: list[str] = []
    for source_kind, requirement in requirements.items():
        payload = requirement["payload"]
        schema_key = str(requirement["schema_key"])
        expected_schema = str(requirement["expected_schema"])
        observed_schema = payload.get(schema_key) if isinstance(payload, dict) else None
        schema_valid = observed_schema == expected_schema
        if payload is None:
            status = "missing_evidence"
            reason = f"{source_kind} evidence is missing"
        elif schema_valid:
            status = "verified"
            reason = f"{source_kind} evidence schema matches expected producer contract"
        else:
            status = "unverified"
            reason = f"{source_kind} evidence schema is missing or does not match expected producer contract"
        if not schema_valid:
            invalid_source_kinds.append(source_kind)
        source_statuses[source_kind] = {
            "source_kind": source_kind,
            "source_path": source_paths.get(source_kind),
            "schema_key": schema_key,
            "expected_schema": expected_schema,
            "observed_schema": observed_schema,
            "schema_valid": schema_valid,
            "status": status,
            "reason": reason,
        }
    return {
        "schema": _PINGAN_PROMOTION_READINESS_EVIDENCE_CONTRACT_SCHEMA,
        "status": "verified" if not invalid_source_kinds else "unverified",
        "invalid_source_kinds": invalid_source_kinds,
        "source_statuses": source_statuses,
        "execution_mode": "readonly_evidence_contract_validation",
        "side_effect_level": "none",
        "boundary": (
            "Read-only source evidence schema-contract validation; does not execute PingAn workflows "
            "and does not prove production readiness or implemented status by itself."
        ),
    }


def _build_pingan_artifact_provenance_status(
    *,
    preflight_payload: dict[str, Any] | None,
    dialog_payload: dict[str, Any] | None,
    acceptance_payload: dict[str, Any] | None,
    source_paths: dict[str, str],
    evidence_contract_status: dict[str, Any],
) -> dict[str, Any]:
    contract_sources = evidence_contract_status.get("source_statuses")
    contract_sources = contract_sources if isinstance(contract_sources, dict) else {}
    requirements = {
        "preflight": {
            "payload": preflight_payload,
            "allowed_producers": {"trade preflight", "TdxTradeManager.pingan.preflight"},
        },
        "dialog_readiness": {
            "payload": dialog_payload,
            "allowed_producers": {"trade dialog-readiness", "TdxTradeManager.pingan.dialog_readiness"},
        },
        "acceptance_coverage": {
            "payload": acceptance_payload,
            "allowed_producers": {
                "task trade-audit-daily-report",
                "task trade-audit-period-report",
                "TdxTaskManager.trade_audit_daily_report",
                "TdxTaskManager.trade_audit_period_report",
            },
        },
    }
    source_statuses: dict[str, dict[str, Any]] = {}
    invalid_source_kinds: list[str] = []
    for source_kind, requirement in requirements.items():
        payload = requirement["payload"]
        provenance = _find_json_object(payload, "artifact_provenance") if isinstance(payload, dict) else None
        provenance = provenance if isinstance(provenance, dict) else None
        contract = contract_sources.get(source_kind)
        contract = contract if isinstance(contract, dict) else {}
        expected_evidence_schema = contract.get("expected_schema")
        observed_schema = provenance.get("schema") if provenance else None
        observed_source_kind = provenance.get("source_kind") if provenance else None
        observed_producer = provenance.get("producer") if provenance else None
        observed_evidence_schema = provenance.get("evidence_schema") if provenance else None
        allowed_producers = requirement["allowed_producers"]
        schema_valid = observed_schema == _PINGAN_READINESS_EVIDENCE_ARTIFACT_PROVENANCE_SCHEMA
        source_kind_valid = observed_source_kind == source_kind
        evidence_schema_valid = observed_evidence_schema == expected_evidence_schema
        producer_valid = observed_producer in allowed_producers
        verified = bool(schema_valid and source_kind_valid and evidence_schema_valid and producer_valid)
        invalid_reasons: list[str] = []
        if not schema_valid:
            invalid_reasons.append("invalid_artifact_provenance_schema")
        if not source_kind_valid:
            invalid_reasons.append("source_kind_mismatch")
        if not evidence_schema_valid:
            invalid_reasons.append("evidence_schema_mismatch")
        if not producer_valid:
            invalid_reasons.append("unsupported_producer")
        if not verified:
            invalid_source_kinds.append(source_kind)
        source_statuses[source_kind] = {
            "source_kind": source_kind,
            "source_path": source_paths.get(source_kind),
            "schema": observed_schema,
            "expected_schema": _PINGAN_READINESS_EVIDENCE_ARTIFACT_PROVENANCE_SCHEMA,
            "source_kind_valid": source_kind_valid,
            "producer": observed_producer,
            "allowed_producers": sorted(allowed_producers),
            "producer_valid": producer_valid,
            "evidence_schema": observed_evidence_schema,
            "expected_evidence_schema": expected_evidence_schema,
            "evidence_schema_valid": evidence_schema_valid,
            "verified": verified,
            "status": "verified" if verified else "unverified",
            "invalid_reasons": invalid_reasons,
        }
    return {
        "schema": "tdx.desktop_trade.pingan_readiness_artifact_provenance_status.v1",
        "status": "verified" if not invalid_source_kinds else "unverified",
        "invalid_source_kinds": invalid_source_kinds,
        "source_statuses": source_statuses,
        "execution_mode": "readonly_artifact_provenance_validation",
        "side_effect_level": "none",
        "boundary": (
            "Read-only artifact provenance metadata validation; does not execute PingAn workflows "
            "and does not prove production readiness or implemented status by itself."
        ),
    }


def _build_pingan_implemented_status_promotion_decision(
    *,
    gate_statuses: dict[str, dict[str, Any]],
    completed_gates: list[str],
    incomplete_gates: list[str],
    missing_evidence_kinds: list[str],
    source_errors: dict[str, str],
    stale_evidence_kinds: list[str],
    stale_evidence_paths: dict[str, str],
    evidence_manifest: dict[str, Any],
    evidence_contract_status: dict[str, Any],
    artifact_provenance_status: dict[str, Any],
    live_manual_acceptance_provenance_status: dict[str, Any],
) -> dict[str, Any]:
    missing_expected_gates = evidence_manifest.get("missing_expected_gates")
    if not isinstance(missing_expected_gates, list):
        missing_expected_gates = []
    invalid_contract_sources = evidence_contract_status.get("invalid_source_kinds")
    if not isinstance(invalid_contract_sources, list):
        invalid_contract_sources = []
    sample_manifest = bool(evidence_manifest.get("example_only") is True or evidence_manifest.get("sample_only") is True)

    blocked_reasons: list[str] = []
    if incomplete_gates:
        blocked_reasons.append("incomplete_required_gates")
    if missing_evidence_kinds:
        blocked_reasons.append("missing_evidence")
    if source_errors:
        blocked_reasons.append("source_errors")
    if stale_evidence_kinds:
        blocked_reasons.append("stale_evidence")
    if missing_expected_gates:
        blocked_reasons.append("missing_expected_gates")
    if evidence_contract_status.get("status") != "verified":
        blocked_reasons.append("unverified_evidence_contract")
    if artifact_provenance_status.get("status") != "verified":
        blocked_reasons.append("unverified_artifact_provenance")
    if live_manual_acceptance_provenance_status.get("status") == "unverified":
        blocked_reasons.append("unverified_live_manual_acceptance_artifact_provenance")
    if sample_manifest:
        blocked_reasons.append("sample_manifest")

    implemented_status_eligible = not blocked_reasons
    return {
        "schema": _PINGAN_IMPLEMENTED_STATUS_PROMOTION_DECISION_SCHEMA,
        "target_nodes": ["D-07", "D-08"],
        "decision": "eligible_for_review" if implemented_status_eligible else "blocked",
        "implemented_status_eligible": implemented_status_eligible,
        "required_gates": list(_PINGAN_PROMOTION_READINESS_GATE_ORDER),
        "completed_gates": completed_gates,
        "incomplete_gates": incomplete_gates,
        "blocked_reasons": blocked_reasons,
        "missing_evidence_kinds": missing_evidence_kinds,
        "source_errors": source_errors,
        "stale_evidence_kinds": stale_evidence_kinds,
        "stale_evidence_paths": stale_evidence_paths,
        "missing_expected_gates": missing_expected_gates,
        "evidence_contract_status": {
            "status": evidence_contract_status.get("status"),
            "invalid_source_kinds": invalid_contract_sources,
        },
        "artifact_provenance_status": {
            "status": artifact_provenance_status.get("status"),
            "invalid_source_kinds": artifact_provenance_status.get("invalid_source_kinds", []),
        },
        "live_manual_acceptance_provenance_status": {
            "status": live_manual_acceptance_provenance_status.get("status"),
            "invalid_reasons": live_manual_acceptance_provenance_status.get("invalid_reasons", []),
        },
        "sample_manifest": sample_manifest,
        "manual_status_review_required": True,
        "function_tree_status_transition_executed": False,
        "execution_mode": "readonly_evidence_decision",
        "side_effect_level": "none",
        "boundary": (
            "Read-only fail-closed decision over caller-provided evidence artifacts; sample evidence cannot "
            "satisfy D-07/D-08 implemented status. Does not execute PingAn workflows, does not claim production "
            "readiness, and does not automatically edit FUNCTION_TREE status."
        ),
    }


def _build_pingan_implemented_status_review_packet(
    *,
    gate_statuses: dict[str, dict[str, Any]],
    completed_gates: list[str],
    incomplete_gates: list[str],
    evidence_contract_status: dict[str, Any],
    artifact_provenance_status: dict[str, Any],
    live_manual_acceptance_provenance_status: dict[str, Any],
    evidence_freshness_status: dict[str, Any],
    evidence_manifest: dict[str, Any],
    decision: dict[str, Any],
) -> dict[str, Any]:
    review_status = (
        "ready_for_manual_review"
        if decision.get("decision") == "eligible_for_review"
        and decision.get("implemented_status_eligible") is True
        else "blocked"
    )
    gate_review_items = []
    for gate_name in _PINGAN_PROMOTION_READINESS_GATE_ORDER:
        gate_status = gate_statuses.get(gate_name, {})
        gate_review_items.append(
            {
                "gate": gate_name,
                "status": gate_status.get("status"),
                "complete": bool(gate_status.get("complete")),
                "source_kind": gate_status.get("source_kind"),
                "source_path": gate_status.get("source_path"),
                "reason": gate_status.get("reason"),
            }
        )

    manual_confirmation_items = [
        "Confirm provider/broker ownership evidence maps to the reviewed PingAn environment.",
        "Confirm safety gates and desktop lifecycle evidence are current for the reviewed environment.",
        "Confirm audit evidence and live/manual acceptance evidence represent the intended PingAn outcome set.",
        "Apply any FUNCTION_TREE status transition explicitly in a separate reviewed change.",
    ]
    if review_status == "blocked":
        manual_confirmation_items.insert(0, "Resolve blocked readiness reasons before manual status review.")

    return {
        "schema": _PINGAN_IMPLEMENTED_STATUS_REVIEW_PACKET_SCHEMA,
        "review_status": review_status,
        "target_nodes": ["D-07", "D-08"],
        "current_function_tree_status": "[部分实现]",
        "decision": decision.get("decision"),
        "implemented_status_eligible": bool(decision.get("implemented_status_eligible")),
        "completed_gates": completed_gates,
        "incomplete_gates": incomplete_gates,
        "blocked_reasons": decision.get("blocked_reasons", []),
        "manual_status_review_required": True,
        "automatic_status_transition_allowed": False,
        "function_tree_status_transition_executed": False,
        "order_submitted": False,
        "control_dispatch_executed": False,
        "promotion_status_transition_executed": False,
        "execution_mode": "readonly_status_review_packet",
        "side_effect_level": "none",
        "gate_review_items": gate_review_items,
        "evidence_summary": {
            "completed_gates": completed_gates,
            "incomplete_gates": incomplete_gates,
            "missing_evidence_kinds": decision.get("missing_evidence_kinds", []),
            "source_errors": decision.get("source_errors", {}),
            "stale_evidence_kinds": decision.get("stale_evidence_kinds", []),
            "stale_evidence_paths": decision.get("stale_evidence_paths", {}),
            "evidence_contract_status": {
                "status": evidence_contract_status.get("status"),
                "invalid_source_kinds": evidence_contract_status.get("invalid_source_kinds", []),
            },
            "artifact_provenance_status": {
                "status": artifact_provenance_status.get("status"),
                "invalid_source_kinds": artifact_provenance_status.get("invalid_source_kinds", []),
            },
            "live_manual_acceptance_provenance_status": {
                "status": live_manual_acceptance_provenance_status.get("status"),
                "invalid_reasons": live_manual_acceptance_provenance_status.get("invalid_reasons", []),
            },
            "evidence_freshness_status": copy.deepcopy(evidence_freshness_status),
            "evidence_manifest": {
                "source_path": evidence_manifest.get("source_path"),
                "expected_gates": evidence_manifest.get("expected_gates", []),
                "missing_expected_gates": evidence_manifest.get("missing_expected_gates", []),
                "sample_manifest": bool(
                    evidence_manifest.get("example_only") is True or evidence_manifest.get("sample_only") is True
                ),
            },
        },
        "manual_confirmation_items": manual_confirmation_items,
        "boundary": (
            "Read-only manual status review input derived from promotion readiness evidence; does not execute "
            "PingAn workflows, submit orders, prove production readiness, or modify FUNCTION_TREE status."
        ),
    }


def _load_pingan_implemented_status_review_packet(
    path: str | None,
) -> tuple[dict[str, Any] | None, str | None]:
    payload, error = _load_json_evidence(path)
    if error is not None:
        return None, error
    if payload is None:
        return None, "review packet JSON is missing"
    if payload.get("schema") == _PINGAN_IMPLEMENTED_STATUS_REVIEW_PACKET_SCHEMA:
        return copy.deepcopy(payload), None
    packet = _find_json_object(payload, "implemented_status_review_packet")
    if packet is None:
        return None, "implemented_status_review_packet not found"
    if packet.get("schema") != _PINGAN_IMPLEMENTED_STATUS_REVIEW_PACKET_SCHEMA:
        return None, "implemented_status_review_packet has unsupported schema"
    return copy.deepcopy(packet), None


def _list_from_json(value: Any) -> list[Any]:
    if isinstance(value, list):
        return copy.deepcopy(value)
    return []


def _build_pingan_implemented_status_review_result_artifact(
    *,
    packet: dict[str, Any],
    review_packet_path: str,
    reviewer: str,
    outcome: str,
    reason: str,
    reviewed_at: str,
    dry_run: bool,
) -> dict[str, Any]:
    return {
        "schema": _PINGAN_IMPLEMENTED_STATUS_REVIEW_RESULT_SCHEMA,
        "artifact_provenance": _build_pingan_readiness_evidence_artifact_provenance(
            source_kind="implemented_status_review_result",
            producer="task pingan-implemented-status-review-result",
            evidence_schema=_PINGAN_IMPLEMENTED_STATUS_REVIEW_RESULT_SCHEMA,
        ),
        "reviewer": reviewer,
        "outcome": outcome,
        "reason": reason,
        "reviewed_at": reviewed_at,
        "review_packet_path": review_packet_path,
        "packet_schema": packet.get("schema"),
        "packet_review_status": packet.get("review_status"),
        "packet_decision": packet.get("decision"),
        "implemented_status_eligible": packet.get("implemented_status_eligible") is True,
        "target_nodes": _list_from_json(packet.get("target_nodes")),
        "current_function_tree_status": packet.get("current_function_tree_status"),
        "completed_gates": _list_from_json(packet.get("completed_gates")),
        "incomplete_gates": _list_from_json(packet.get("incomplete_gates")),
        "blocked_reasons": _list_from_json(packet.get("blocked_reasons")),
        "manual_status_review_required": True,
        "automatic_status_transition_allowed": False,
        "function_tree_status_transition_executed": False,
        "order_submitted": False,
        "control_dispatch_executed": False,
        "promotion_status_transition_executed": False,
        "execution_mode": "manual_status_review_result_record",
        "side_effect_level": "none" if dry_run else "file_write",
        "boundary": (
            "Records a maintainer review result for an existing PingAn implemented-status review packet only; "
            "does not execute PingAn workflows, submit orders, prove production readiness, prove implemented "
            "status, or promote D-07/D-08."
        ),
    }


def _load_pingan_implemented_status_review_result(
    path: str | None,
) -> tuple[dict[str, Any] | None, str | None]:
    payload, error = _load_json_evidence(path)
    if error is not None:
        return None, error
    if payload is None:
        return None, "review result JSON is missing"
    if payload.get("schema") != _PINGAN_IMPLEMENTED_STATUS_REVIEW_RESULT_SCHEMA:
        return None, "review result has unsupported schema"
    return copy.deepcopy(payload), None


def _build_pingan_review_result_artifact_provenance_status(payload: dict[str, Any]) -> dict[str, Any]:
    provenance = payload.get("artifact_provenance")
    provenance = provenance if isinstance(provenance, dict) else None
    observed_schema = provenance.get("schema") if provenance else None
    observed_source_kind = provenance.get("source_kind") if provenance else None
    observed_producer = provenance.get("producer") if provenance else None
    observed_evidence_schema = provenance.get("evidence_schema") if provenance else None

    invalid_reasons: list[str] = []
    if provenance is None:
        invalid_reasons.append("missing_artifact_provenance")
    elif observed_schema != _PINGAN_READINESS_EVIDENCE_ARTIFACT_PROVENANCE_SCHEMA:
        invalid_reasons.append("invalid_artifact_provenance_schema")
    if provenance is not None and observed_source_kind != "implemented_status_review_result":
        invalid_reasons.append("source_kind_mismatch")
    if provenance is not None and observed_evidence_schema != _PINGAN_IMPLEMENTED_STATUS_REVIEW_RESULT_SCHEMA:
        invalid_reasons.append("evidence_schema_mismatch")
    if provenance is not None and observed_producer != "task pingan-implemented-status-review-result":
        invalid_reasons.append("unsupported_producer")

    verified = not invalid_reasons
    return {
        "status": "verified" if verified else "unverified",
        "schema": observed_schema,
        "expected_schema": _PINGAN_READINESS_EVIDENCE_ARTIFACT_PROVENANCE_SCHEMA,
        "source_kind": observed_source_kind,
        "expected_source_kind": "implemented_status_review_result",
        "producer": observed_producer,
        "expected_producer": "task pingan-implemented-status-review-result",
        "evidence_schema": observed_evidence_schema,
        "expected_evidence_schema": _PINGAN_IMPLEMENTED_STATUS_REVIEW_RESULT_SCHEMA,
        "invalid_reasons": invalid_reasons,
    }


def _build_pingan_implemented_status_transition_gate(
    *,
    review_result: dict[str, Any],
    review_result_path: str,
) -> dict[str, Any]:
    completed_checks: list[str] = []
    blocked_reasons: list[str] = []
    provenance_status = _build_pingan_review_result_artifact_provenance_status(review_result)
    if provenance_status.get("status") == "verified":
        completed_checks.append("verified_review_result_artifact_provenance")
    else:
        blocked_reasons.append("unverified_review_result_artifact_provenance")

    outcome = str(review_result.get("outcome") or "").strip().lower()
    if outcome == "approve":
        completed_checks.append("approved_review_result")
    else:
        blocked_reasons.append("review_result_not_approved")

    target_nodes = _list_from_json(review_result.get("target_nodes"))
    if target_nodes == ["D-07", "D-08"]:
        completed_checks.append("target_nodes_d07_d08")
    else:
        blocked_reasons.append("unexpected_target_nodes")

    packet_ready = (
        review_result.get("packet_review_status") == "ready_for_manual_review"
        and review_result.get("packet_decision") == "eligible_for_review"
        and review_result.get("implemented_status_eligible") is True
        and review_result.get("current_function_tree_status") == "[部分实现]"
        and not _list_from_json(review_result.get("incomplete_gates"))
        and not _list_from_json(review_result.get("blocked_reasons"))
    )
    if packet_ready:
        completed_checks.append("eligible_review_packet")
    else:
        blocked_reasons.append("review_packet_not_ready_for_transition")

    non_transition_flags_confirmed = (
        review_result.get("function_tree_status_transition_executed") is False
        and review_result.get("automatic_status_transition_allowed") is False
        and review_result.get("order_submitted") is False
        and review_result.get("control_dispatch_executed") is False
    )
    if non_transition_flags_confirmed:
        completed_checks.append("non_transition_flags_confirmed")
    else:
        blocked_reasons.append("review_result_transition_flags_invalid")

    blocked_reasons = sorted(set(blocked_reasons))
    eligible = not blocked_reasons
    return {
        "schema": _PINGAN_IMPLEMENTED_STATUS_TRANSITION_GATE_SCHEMA,
        "review_result_path": review_result_path,
        "gate_status": "eligible_for_status_transition_review" if eligible else "blocked",
        "eligible_for_status_transition_review": eligible,
        "completed_checks": completed_checks,
        "blocked_reasons": blocked_reasons,
        "artifact_provenance_status": provenance_status,
        "review_result_outcome": outcome,
        "reviewer": review_result.get("reviewer"),
        "reviewed_at": review_result.get("reviewed_at"),
        "target_nodes": target_nodes,
        "current_function_tree_status": review_result.get("current_function_tree_status"),
        "packet_review_status": review_result.get("packet_review_status"),
        "packet_decision": review_result.get("packet_decision"),
        "implemented_status_eligible": review_result.get("implemented_status_eligible") is True,
        "manual_status_transition_required": True,
        "automatic_status_transition_allowed": False,
        "function_tree_status_transition_executed": False,
        "order_submitted": False,
        "control_dispatch_executed": False,
        "promotion_status_transition_executed": False,
        "execution_mode": "readonly_status_transition_gate",
        "side_effect_level": "none",
        "boundary": (
            "Read-only pre-transition gate over a PingAn implemented-status review result; does not execute "
            "PingAn workflows, submit orders, prove production readiness, prove implemented status, or modify "
            "FUNCTION_TREE status."
        ),
    }


def _load_pingan_implemented_status_transition_gate(
    path: str | None,
) -> tuple[dict[str, Any] | None, str | None]:
    payload, error = _load_json_evidence(path)
    if error is not None:
        return None, error
    if payload is None:
        return None, "transition gate JSON is missing"
    if payload.get("schema") == _PINGAN_IMPLEMENTED_STATUS_TRANSITION_GATE_SCHEMA:
        return copy.deepcopy(payload), None
    gate = _find_json_object(payload, "implemented_status_transition_gate")
    if gate is None:
        return None, "implemented_status_transition_gate not found"
    if gate.get("schema") != _PINGAN_IMPLEMENTED_STATUS_TRANSITION_GATE_SCHEMA:
        return None, "implemented_status_transition_gate has unsupported schema"
    return copy.deepcopy(gate), None


def _normalize_function_tree_status_cell(value: str) -> str:
    return value.strip().strip("`")


def _load_function_tree_transition_lines(
    path: str,
) -> tuple[list[str] | None, dict[str, str], str | None]:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        return None, {}, str(exc)
    lines = text.splitlines()
    statuses: dict[str, str] = {}
    for line in lines:
        if not (line.startswith("| D-07 |") or line.startswith("| D-08 |")):
            continue
        cells = line.split("|")
        if len(cells) < 6:
            return None, statuses, "FUNCTION_TREE row shape is unsupported"
        node_id = cells[1].strip()
        statuses[node_id] = _normalize_function_tree_status_cell(cells[3])
    for node_id in ("D-07", "D-08"):
        if node_id not in statuses:
            return None, statuses, f"FUNCTION_TREE row missing: {node_id}"
    return lines, statuses, None


def _apply_pingan_function_tree_status_transition(lines: list[str]) -> list[str]:
    updated = list(lines)
    for index, line in enumerate(updated):
        if not (line.startswith("| D-07 |") or line.startswith("| D-08 |")):
            continue
        cells = line.split("|")
        cells[3] = "`[已实现]`"
        updated[index] = "|".join(cells)
    return updated


def _build_pingan_implemented_status_transition_plan(
    *,
    transition_gate: dict[str, Any],
    transition_gate_path: str,
    function_tree_path: str,
    output_path: str,
    operator: str,
    reason: str,
    dry_run: bool,
    apply: bool,
    confirm_transition: bool,
    transition_executed: bool,
    record_written: bool,
) -> dict[str, Any]:
    return {
        "schema": "tdx.desktop_trade.pingan_implemented_status_transition_plan.v1",
        "transition_gate_path": transition_gate_path,
        "function_tree_path": function_tree_path,
        "output_path": output_path,
        "operator": operator,
        "reason": reason,
        "dry_run": dry_run,
        "apply": apply,
        "confirm_transition": confirm_transition,
        "target_nodes": _list_from_json(transition_gate.get("target_nodes")),
        "status_changes": {
            "D-07": {"from": "[部分实现]", "to": "[已实现]"},
            "D-08": {"from": "[部分实现]", "to": "[已实现]"},
        },
        "transition_executed": transition_executed,
        "record_written": record_written,
        "function_tree_status_transition_executed": transition_executed,
        "order_submitted": False,
        "control_dispatch_executed": False,
        "execution_mode": (
            "function_tree_status_transition" if transition_executed else "function_tree_status_transition_dry_run"
        ),
        "side_effect_level": "function_tree_write" if transition_executed else "none",
        "boundary": (
            "Guarded FUNCTION_TREE status transition machinery only; does not execute PingAn workflows, submit "
            "orders, control the desktop, or prove production readiness by itself."
        ),
    }


def _build_pingan_implemented_status_transition_record(
    *,
    plan: dict[str, Any],
    transition_gate: dict[str, Any],
    transitioned_at: str,
) -> dict[str, Any]:
    return {
        "schema": _PINGAN_IMPLEMENTED_STATUS_TRANSITION_RECORD_SCHEMA,
        "artifact_provenance": _build_pingan_readiness_evidence_artifact_provenance(
            source_kind="implemented_status_transition_record",
            producer="task pingan-implemented-status-transition",
            evidence_schema=_PINGAN_IMPLEMENTED_STATUS_TRANSITION_RECORD_SCHEMA,
        ),
        "operator": plan["operator"],
        "reason": plan["reason"],
        "transitioned_at": transitioned_at,
        "transition_gate_path": plan["transition_gate_path"],
        "function_tree_path": plan["function_tree_path"],
        "target_nodes": plan["target_nodes"],
        "status_changes": copy.deepcopy(plan["status_changes"]),
        "gate_status": transition_gate.get("gate_status"),
        "eligible_for_status_transition_review": transition_gate.get("eligible_for_status_transition_review") is True,
        "completed_checks": _list_from_json(transition_gate.get("completed_checks")),
        "function_tree_status_transition_executed": True,
        "order_submitted": False,
        "control_dispatch_executed": False,
        "promotion_status_transition_executed": True,
        "execution_mode": "function_tree_status_transition",
        "side_effect_level": "function_tree_write",
        "boundary": (
            "Records an explicit FUNCTION_TREE status transition only; does not execute PingAn workflows, submit "
            "orders, control the desktop, or prove production readiness by itself."
        ),
    }


def _extract_live_manual_acceptance_provenance_status(
    acceptance_status: dict[str, Any] | None,
) -> dict[str, Any]:
    if acceptance_status is None:
        return {"status": "not_provided", "invalid_reasons": []}
    live_manual_acceptance = acceptance_status.get("live_manual_acceptance")
    if not isinstance(live_manual_acceptance, dict):
        if acceptance_status.get("live_manual_acceptance_complete") is True:
            return {
                "status": "unverified",
                "invalid_reasons": ["missing_live_manual_acceptance_status"],
            }
        return {"status": "not_provided", "invalid_reasons": []}
    provenance_status = live_manual_acceptance.get("artifact_provenance_status")
    if not isinstance(provenance_status, dict):
        return {
            "status": "unverified",
            "invalid_reasons": ["missing_artifact_provenance_status"],
        }
    return copy.deepcopy(provenance_status)


def _build_pingan_promotion_readiness_rollup(
    *,
    preflight_path: str | None = None,
    dialog_readiness_path: str | None = None,
    acceptance_coverage_path: str | None = None,
    max_evidence_age_seconds: float | None = None,
    evidence_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_paths = {
        key: value
        for key, value in {
            "preflight": preflight_path,
            "dialog_readiness": dialog_readiness_path,
            "acceptance_coverage": acceptance_coverage_path,
        }.items()
        if value is not None
    }
    evidence_freshness_status, stale_evidence_kinds, stale_evidence_paths = _build_evidence_freshness_status(
        source_paths,
        max_evidence_age_seconds=max_evidence_age_seconds,
    )
    source_errors: dict[str, str] = {}
    missing_evidence_kinds: list[str] = []

    preflight_payload, error = _load_json_evidence(preflight_path)
    if error is not None:
        source_errors["preflight"] = error
    dialog_payload, error = _load_json_evidence(dialog_readiness_path)
    if error is not None:
        source_errors["dialog_readiness"] = error
    acceptance_payload, error = _load_json_evidence(acceptance_coverage_path)
    if error is not None:
        source_errors["acceptance_coverage"] = error

    preflight_status = _find_json_object(preflight_payload, "promotion_gate_status")
    desktop_lifecycle_status = _find_json_object(dialog_payload, "desktop_lifecycle_gate_status")
    acceptance_status = _find_json_object(acceptance_payload, "acceptance_outcome_coverage_status")

    if preflight_status is None:
        missing_evidence_kinds.append("preflight")
    if desktop_lifecycle_status is None:
        missing_evidence_kinds.append("dialog_readiness")
    if acceptance_status is None:
        missing_evidence_kinds.append("acceptance_coverage")

    provider_broker = preflight_status.get("provider_broker_ownership") if preflight_status else None
    safety_gates = preflight_status.get("safety_gates") if preflight_status else None
    provider_broker = provider_broker if isinstance(provider_broker, dict) else None
    safety_gates = safety_gates if isinstance(safety_gates, dict) else None

    provider_broker_complete = _json_status_is_ready(provider_broker)
    safety_gates_complete = _json_status_is_ready(safety_gates)
    desktop_remaining = (
        desktop_lifecycle_status.get("remaining_lifecycle_gates") if desktop_lifecycle_status is not None else None
    )
    desktop_lifecycle_complete = _json_status_is_ready(desktop_lifecycle_status) or desktop_remaining == []
    audit_evidence_complete = bool(
        acceptance_status is not None and acceptance_status.get("automated_outcome_coverage_complete") is True
    )
    live_manual_acceptance_provenance_status = _extract_live_manual_acceptance_provenance_status(acceptance_status)
    live_manual_acceptance_provenance_verified = (
        live_manual_acceptance_provenance_status.get("status") == "verified"
    )
    live_manual_acceptance_complete = bool(
        acceptance_status is not None
        and acceptance_status.get("live_manual_acceptance_complete") is True
        and live_manual_acceptance_provenance_verified
    )
    acceptance_evidence_complete = bool(
        acceptance_status is not None
        and acceptance_status.get("acceptance_complete") is True
        and live_manual_acceptance_provenance_verified
    )

    gate_statuses = {
        "provider_broker_ownership": _build_rollup_gate_status(
            status=_json_status_text(
                provider_broker,
                default="missing_evidence" if preflight_status is None else "missing_gate",
            ),
            complete=provider_broker_complete,
            source_kind="preflight",
            source_path=source_paths.get("preflight"),
            reason=(
                "provider/broker ownership evidence reports ready"
                if provider_broker_complete
                else "provider/broker ownership evidence is missing or not ready"
            ),
        ),
        "safety_gates": _build_rollup_gate_status(
            status=_json_status_text(
                safety_gates,
                default="missing_evidence" if preflight_status is None else "missing_gate",
            ),
            complete=safety_gates_complete,
            source_kind="preflight",
            source_path=source_paths.get("preflight"),
            reason=(
                "safety gate evidence reports ready"
                if safety_gates_complete
                else "safety gate evidence is missing or not ready"
            ),
        ),
        "desktop_lifecycle": _build_rollup_gate_status(
            status=_json_status_text(
                desktop_lifecycle_status,
                default="complete" if desktop_lifecycle_complete else "missing_evidence",
            ),
            complete=desktop_lifecycle_complete,
            source_kind="dialog_readiness",
            source_path=source_paths.get("dialog_readiness"),
            reason=(
                "desktop lifecycle evidence reports complete"
                if desktop_lifecycle_complete
                else "desktop lifecycle evidence is missing or incomplete"
            ),
        ),
        "audit_evidence": _build_rollup_gate_status(
            status="complete" if audit_evidence_complete else "incomplete",
            complete=audit_evidence_complete,
            source_kind="acceptance_coverage",
            source_path=source_paths.get("acceptance_coverage"),
            reason=(
                "automated audit outcome coverage is complete"
                if audit_evidence_complete
                else "automated audit outcome coverage is missing or incomplete"
            ),
        ),
        "live_manual_acceptance": _build_rollup_gate_status(
            status="complete" if live_manual_acceptance_complete else "incomplete",
            complete=live_manual_acceptance_complete,
            source_kind="acceptance_coverage",
            source_path=source_paths.get("acceptance_coverage"),
            reason=(
                "live/manual acceptance evidence is complete"
                if live_manual_acceptance_complete
                else "live/manual acceptance evidence is missing or incomplete"
            ),
        ),
        "acceptance_evidence": _build_rollup_gate_status(
            status="complete" if acceptance_evidence_complete else "incomplete",
            complete=acceptance_evidence_complete,
            source_kind="acceptance_coverage",
            source_path=source_paths.get("acceptance_coverage"),
            reason=(
                "combined acceptance evidence is complete"
                if acceptance_evidence_complete
                else "combined acceptance evidence is missing or incomplete"
            ),
        ),
    }
    _apply_stale_evidence_to_rollup_gates(gate_statuses, stale_evidence_kinds)
    completed_gates = [name for name in _PINGAN_PROMOTION_READINESS_GATE_ORDER if gate_statuses[name]["complete"]]
    incomplete_gates = [name for name in _PINGAN_PROMOTION_READINESS_GATE_ORDER if not gate_statuses[name]["complete"]]
    evidence_contract_status = _build_pingan_evidence_contract_status(
        preflight_status=preflight_status,
        desktop_lifecycle_status=desktop_lifecycle_status,
        acceptance_status=acceptance_status,
        source_paths=source_paths,
    )
    artifact_provenance_status = _build_pingan_artifact_provenance_status(
        preflight_payload=preflight_payload,
        dialog_payload=dialog_payload,
        acceptance_payload=acceptance_payload,
        source_paths=source_paths,
        evidence_contract_status=evidence_contract_status,
    )
    evidence_manifest_status = copy.deepcopy(
        evidence_manifest
        or {
            "schema": _PINGAN_PROMOTION_READINESS_MANIFEST_SCHEMA,
            "source_path": None,
            "loaded": False,
            "expected_gates": [],
            "missing_expected_gates": [],
            "resolved_overrides": [],
        }
    )
    expected_gates = evidence_manifest_status.get("expected_gates")
    if not isinstance(expected_gates, list):
        expected_gates = []
    evidence_manifest_status["expected_gates"] = expected_gates
    evidence_manifest_status["missing_expected_gates"] = [
        gate_name for gate_name in expected_gates if gate_name not in gate_statuses
    ]
    implemented_status_promotion_decision = _build_pingan_implemented_status_promotion_decision(
        gate_statuses=gate_statuses,
        completed_gates=completed_gates,
        incomplete_gates=incomplete_gates,
        missing_evidence_kinds=missing_evidence_kinds,
        source_errors=source_errors,
        stale_evidence_kinds=stale_evidence_kinds,
        stale_evidence_paths=stale_evidence_paths,
        evidence_manifest=evidence_manifest_status,
        evidence_contract_status=evidence_contract_status,
        artifact_provenance_status=artifact_provenance_status,
        live_manual_acceptance_provenance_status=live_manual_acceptance_provenance_status,
    )
    implemented_status_review_packet = _build_pingan_implemented_status_review_packet(
        gate_statuses=gate_statuses,
        completed_gates=completed_gates,
        incomplete_gates=incomplete_gates,
        evidence_contract_status=evidence_contract_status,
        artifact_provenance_status=artifact_provenance_status,
        live_manual_acceptance_provenance_status=live_manual_acceptance_provenance_status,
        evidence_freshness_status=evidence_freshness_status,
        evidence_manifest=evidence_manifest_status,
        decision=implemented_status_promotion_decision,
    )
    return {
        "schema": _PINGAN_PROMOTION_READINESS_ROLLUP_SCHEMA,
        "status": "complete" if not incomplete_gates else "partial",
        "execution_mode": "readonly_evidence_rollup",
        "side_effect_level": "none",
        "order_submitted": False,
        "control_dispatch_executed": False,
        "promotion_status_transition_executed": False,
        "gate_statuses": gate_statuses,
        "completed_gates": completed_gates,
        "incomplete_gates": incomplete_gates,
        "missing_evidence_kinds": missing_evidence_kinds,
        "source_paths": source_paths,
        "source_errors": source_errors,
        "evidence_freshness_cutoff_seconds": max_evidence_age_seconds,
        "evidence_freshness_status": evidence_freshness_status,
        "stale_evidence_kinds": stale_evidence_kinds,
        "stale_evidence_paths": stale_evidence_paths,
        "evidence_manifest": evidence_manifest_status,
        "evidence_contract_status": evidence_contract_status,
        "artifact_provenance_status": artifact_provenance_status,
        "live_manual_acceptance_provenance_status": live_manual_acceptance_provenance_status,
        "implemented_status_promotion_decision": implemented_status_promotion_decision,
        "implemented_status_review_packet": implemented_status_review_packet,
        "boundary": (
            "Read-only evidence aggregation from caller-provided JSON artifacts; does not execute "
            "broker/desktop/trade/report/catalog workflows and does not prove production readiness "
            "or implemented status."
        ),
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


def _build_trade_audit_cross_ledger_csv_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    csv_rows: list[dict[str, Any]] = []
    for row in rows:
        audit = row.get("audit", {})
        submission_matches = row.get("submission_matches", [])
        task_matches = row.get("task_matches", [])
        csv_rows.append(
            {
                "audit_id": audit.get("audit_id"),
                "recorded_at": audit.get("recorded_at"),
                "status": audit.get("status"),
                "broker": audit.get("broker"),
                "method": audit.get("method"),
                "code": audit.get("code"),
                "contract_no": audit.get("contract_no"),
                "submission_key": audit.get("submission_key"),
                "submission_matches_count": len(submission_matches) if isinstance(submission_matches, list) else 0,
                "task_matches_count": len(task_matches) if isinstance(task_matches, list) else 0,
                "audit_path": audit.get("audit_path"),
            }
        )
    return csv_rows


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
        provider_mode: str = "live",
        replay_fixture: str | None = None,
        replay_fixture_path: str | None = None,
        replay_fixture_map: dict[str, Any] | None = None,
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
            provider_mode=provider_mode,
            replay_fixture=replay_fixture,
            replay_fixture_path=replay_fixture_path,
            replay_fixture_map=replay_fixture_map,
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

    def block_sync(
        self,
        *,
        block_code: str,
        symbols: list[str],
        mode: str = "replace",
        create_if_missing: bool = False,
        dry_run: bool = False,
        show: bool = True,
        write_policy: str | None = None,
        mutation_key: str | None = None,
        audit_dir: str | None = None,
    ) -> Result:
        result, timing = _capture_task_timing(
            "task.block_sync",
            lambda: self.api_manager.block.sync_watchlist(
                block_code=block_code,
                symbols=symbols,
                mode=mode,
                create_if_missing=create_if_missing,
                dry_run=dry_run,
                show=show,
                write_policy=write_policy,
                mutation_key=mutation_key,
                audit_dir=audit_dir,
            ),
        )
        return self._attach_task_metadata(result, task_name="block_sync", timing=timing)

    def block_watchlist_import(
        self,
        *,
        input_path: str,
        dry_run: bool = True,
        show: bool = True,
        audit_dir: str | None = None,
    ) -> Result:
        def run() -> Result:
            try:
                request = load_watchlist_import_file(input_path)
            except ValueError as exc:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message=str(exc),
                    data={"input_path": input_path},
                    next_action="Fix the JSON watchlist import file and retry.",
                )

            if dry_run:
                return Result(
                    ok=True,
                    code=ErrorCode.OK,
                    message="planned watchlist import",
                    data={"watchlist_import": plan_watchlist_import(input_path, dry_run=True)},
                )

            block_name = request.block_name or request.block_code
            return sync_watchlist_import_request(
                request,
                observed_state=lambda: self.api_manager.block.read_watchlist_snapshot(block_code=request.block_code),
                create_block=lambda: self.api_manager.block.create_sector(
                    block_code=request.block_code,
                    block_name=block_name,
                    audit_dir=audit_dir,
                ),
                sync_members=lambda symbols, requested_show: self.api_manager.block.send_user_block(
                    block_code=request.block_code,
                    stocks=symbols,
                    show=requested_show,
                    audit_dir=audit_dir,
                ),
                dry_run=False,
                show=show,
                audit_dir=audit_dir,
            )

        result, timing = _capture_task_timing("task.block_watchlist_import", run)
        return self._attach_task_metadata(result, task_name="block_watchlist_import", timing=timing)

    def pingan_promotion_readiness_rollup(
        self,
        *,
        evidence_manifest_path: str | None = None,
        preflight_path: str | None = None,
        dialog_readiness_path: str | None = None,
        acceptance_coverage_path: str | None = None,
        max_evidence_age_seconds: float | None = None,
        json_output_path: str | None = None,
    ) -> Result:
        def run() -> Result:
            manifest_values, manifest_metadata, manifest_error = _load_pingan_promotion_readiness_manifest(
                evidence_manifest_path
            )
            if manifest_error is not None:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"failed to load PingAn promotion readiness evidence manifest: {manifest_error}",
                    data={"evidence_manifest": manifest_metadata},
                    next_action="Fix the evidence manifest JSON and retry.",
                )
            resolved_overrides: list[str] = []
            resolved_preflight_path = str(manifest_values.get("preflight_path") or "") or None
            resolved_dialog_readiness_path = str(manifest_values.get("dialog_readiness_path") or "") or None
            resolved_acceptance_coverage_path = str(manifest_values.get("acceptance_coverage_path") or "") or None
            resolved_max_evidence_age_seconds = manifest_values.get("max_evidence_age_seconds")
            if preflight_path is not None:
                resolved_preflight_path = preflight_path
                resolved_overrides.append("preflight_path")
            if dialog_readiness_path is not None:
                resolved_dialog_readiness_path = dialog_readiness_path
                resolved_overrides.append("dialog_readiness_path")
            if acceptance_coverage_path is not None:
                resolved_acceptance_coverage_path = acceptance_coverage_path
                resolved_overrides.append("acceptance_coverage_path")
            if max_evidence_age_seconds is not None:
                resolved_max_evidence_age_seconds = max_evidence_age_seconds
                resolved_overrides.append("max_evidence_age_seconds")
            if not isinstance(resolved_max_evidence_age_seconds, (int, float)):
                resolved_max_evidence_age_seconds = None
            manifest_metadata["resolved_overrides"] = resolved_overrides
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="summarized PingAn promotion readiness",
                data={
                    "promotion_readiness_rollup": _build_pingan_promotion_readiness_rollup(
                        preflight_path=resolved_preflight_path,
                        dialog_readiness_path=resolved_dialog_readiness_path,
                        acceptance_coverage_path=resolved_acceptance_coverage_path,
                        max_evidence_age_seconds=resolved_max_evidence_age_seconds,
                        evidence_manifest=manifest_metadata,
                    )
                },
            )

        result, timing = _capture_task_timing("task.pingan_promotion_readiness_rollup", run)
        result = self._attach_task_metadata(result, task_name="pingan_promotion_readiness_rollup", timing=timing)
        if json_output_path is None:
            return result

        artifact_meta = {
            "schema": _PINGAN_PROMOTION_READINESS_ROLLUP_ARTIFACT_SCHEMA,
            "json_output_path": json_output_path,
            "written": False,
        }
        result.data["promotion_readiness_rollup_artifact"] = artifact_meta
        artifact_payload_meta = {**artifact_meta, "written": True}
        artifact_payload = {
            "schema": _PINGAN_PROMOTION_READINESS_ROLLUP_ARTIFACT_SCHEMA,
            "promotion_readiness_rollup": result.data["promotion_readiness_rollup"],
            "promotion_readiness_rollup_artifact": artifact_payload_meta,
            "task": result.data["task"],
            "task_profile": result.data["task_profile"],
            "timing": result.data["timing"],
        }
        try:
            output_path = Path(json_output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(artifact_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except OSError as exc:
            artifact_meta["error"] = str(exc)
            return Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message=f"failed to write promotion readiness rollup artifact: {exc}",
                data=result.data,
                next_action="Choose a writable JSON output path and retry.",
            )
        artifact_meta["written"] = True
        return result

    def block_read_watchlist(
        self,
        *,
        block_code: str,
    ) -> Result:
        result, timing = _capture_task_timing(
            "task.block_read_watchlist",
            lambda: self.api_manager.block.read_watchlist_snapshot(block_code=block_code),
        )
        return self._attach_task_metadata(result, task_name="block_read_watchlist", timing=timing)

    def block_read_full(
        self,
        *,
        block_code: str,
    ) -> Result:
        def run() -> Result:
            result = self.api_manager.block.read_watchlist_snapshot(block_code=block_code)
            if not result.ok:
                return result

            snapshot = result.data.get("snapshot")
            source_metadata = snapshot.get("source_metadata") if isinstance(snapshot, dict) else None
            metadata = source_metadata if isinstance(source_metadata, dict) else {}
            warnings = result.warnings if isinstance(result.warnings, list) else []
            result.data["read_full"] = {
                "sector_name": metadata.get("sector_name"),
                "raw_member_count": metadata.get("raw_member_count"),
                "duplicate_count": metadata.get("duplicate_count"),
                "warnings_present": len(warnings) > 0,
            }
            return result

        result, timing = _capture_task_timing("task.block_read_full", run)
        return self._attach_task_metadata(result, task_name="block_read_full", timing=timing)

    def block_read_watchlist_export(
        self,
        *,
        block_code: str,
        output: str,
        overwrite: bool = False,
    ) -> Result:
        def run() -> Result:
            result = self.api_manager.block.read_watchlist_snapshot(block_code=block_code)
            if not result.ok:
                return result

            snapshot = result.data.get("snapshot")
            export_metadata = {"output_path": str(output)}

            def fail_result(
                *,
                code: ErrorCode,
                message: str,
                error: str,
                next_action: str,
            ) -> Result:
                result.ok = False
                result.code = code
                result.message = message
                result.next_action = next_action
                result.data["export"] = {**export_metadata, "error": error}
                return result

            if not isinstance(snapshot, dict):
                return fail_result(
                    code=ErrorCode.EXECUTION_FAILED,
                    message="block watchlist export requires a snapshot object from the upstream provider",
                    error="snapshot payload missing or not an object",
                    next_action="Inspect the upstream block snapshot payload and retry once it returns data.snapshot as an object.",
                )

            try:
                output_path = Path(output).expanduser().resolve()
            except (OSError, RuntimeError, ValueError) as exc:
                return fail_result(
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"block watchlist export output path is invalid: {output}",
                    error=str(exc),
                    next_action="Provide a valid --output file path and retry the export.",
                )

            export_metadata["output_path"] = str(output_path)

            if output_path.exists() and output_path.is_dir():
                return fail_result(
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"block watchlist export output path must be a file: {output_path}",
                    error=f"output path is a directory: {output_path}",
                    next_action="Provide a file path for --output.",
                )

            parent_dir = output_path.parent
            if not parent_dir.exists():
                return fail_result(
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"block watchlist export parent directory does not exist: {parent_dir}",
                    error=f"parent directory does not exist: {parent_dir}",
                    next_action="Create the output directory before exporting the snapshot.",
                )

            if not parent_dir.is_dir():
                return fail_result(
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"block watchlist export parent path is not a directory: {parent_dir}",
                    error=f"parent path is not a directory: {parent_dir}",
                    next_action="Provide an output path whose parent is an existing directory.",
                )

            overwritten = output_path.exists()
            if overwritten and not overwrite:
                return fail_result(
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"block watchlist export output file already exists: {output_path}",
                    error=f"output file already exists: {output_path}",
                    next_action="Re-run with overwrite=True or choose a different output path.",
                )

            try:
                _probe_directory_writable(parent_dir)
            except OSError as exc:
                return fail_result(
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"block watchlist export parent directory is not writable: {parent_dir}",
                    error=str(exc),
                    next_action="Grant write access to the output directory or choose another location.",
                )

            try:
                _write_json_file_atomic(output_path, snapshot, overwrite=overwrite)
            except FileExistsError:
                return fail_result(
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"block watchlist export output file already exists: {output_path}",
                    error=f"output file already exists: {output_path}",
                    next_action="Re-run with overwrite=True or choose a different output path.",
                )
            except (OSError, TypeError, ValueError) as exc:
                return fail_result(
                    code=ErrorCode.EXECUTION_FAILED,
                    message=f"block watchlist export failed: {exc}",
                    error=str(exc),
                    next_action="Inspect the output path permissions and retry the export.",
                )

            result.data["export"] = {
                **export_metadata,
                "overwritten": overwritten,
                "file_size": output_path.stat().st_size,
            }
            return result

        result, timing = _capture_task_timing("task.block_read_watchlist_export", run)
        return self._attach_task_metadata(result, task_name="block_read_watchlist_export", timing=timing)

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
        run_id: str | None = None,
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
            run_paths = build_subscription_watch_run_paths(run_root_dir, run_id=run_id)
            run_paths.run_dir.mkdir(parents=True, exist_ok=False)

            legacy_jsonl_path = Path(jsonl_output_path) if jsonl_output_path else None
            legacy_csv_path = Path(csv_output_path) if csv_output_path else None
            legacy_status_path = Path(status_output_path) if status_output_path else None

            if getattr(self.api_manager, "provider_mode", "live") == "replay":
                try:
                    materialized = materialize_subscription_watch_replay(
                        paths=run_paths,
                        replay_fixture=getattr(self.api_manager, "replay_fixture", None),
                        replay_fixture_path=getattr(self.api_manager, "replay_fixture_path", None),
                    )
                except ValueError as exc:
                    return Result(
                        ok=False,
                        code=ErrorCode.INVALID_REQUEST,
                        message=str(exc),
                        data={
                            "replay_source": {
                                "mode": "replay",
                                "capability": "subscription.watch",
                            }
                        },
                    )
                if legacy_jsonl_path is not None and legacy_jsonl_path != run_paths.events_jsonl_path:
                    legacy_jsonl_path.parent.mkdir(parents=True, exist_ok=True)
                    legacy_jsonl_path.write_text(
                        run_paths.events_jsonl_path.read_text(encoding="utf-8"),
                        encoding="utf-8",
                    )
                if legacy_csv_path is not None and legacy_csv_path != run_paths.events_csv_path:
                    legacy_csv_path.parent.mkdir(parents=True, exist_ok=True)
                    legacy_csv_path.write_text(
                        run_paths.events_csv_path.read_text(encoding="utf-8"),
                        encoding="utf-8",
                    )
                if legacy_status_path is not None and legacy_status_path != run_paths.status_path:
                    legacy_status_path.parent.mkdir(parents=True, exist_ok=True)
                    legacy_status_path.write_text(
                        run_paths.status_path.read_text(encoding="utf-8"),
                        encoding="utf-8",
                    )

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
                status_payload = copy.deepcopy(materialized.status)
                status_payload["artifacts"] = dict(artifact_paths)
                status_payload["output_paths"] = {
                    "run_dir": str(run_paths.run_dir),
                    "manifest_path": str(run_paths.manifest_path),
                    "status_path": str(run_paths.status_path),
                    "summary_path": str(run_paths.summary_path),
                    "events_jsonl_path": str(run_paths.events_jsonl_path),
                    "events_csv_path": str(run_paths.events_csv_path),
                }
                _write_json_file(run_paths.status_path, status_payload)
                if legacy_status_path is not None and legacy_status_path != run_paths.status_path:
                    _write_json_file(legacy_status_path, status_payload)

                summary_payload = copy.deepcopy(materialized.summary)
                event_rows = [dict(row) for row in materialized.events]
                session_id = str(status_payload.get("session_id") or "replay-session")
                provider_instance_id = str(status_payload.get("provider_instance_id") or "replay-provider")
                subscription_id = str(status_payload.get("subscription_id") or "replay-subscription")
                stop_reason = str(summary_payload.get("stop_reason") or status_payload.get("stop_reason") or "completed")
                interrupted = str(summary_payload.get("final_state") or "completed") == "interrupted"
                started_at = str(summary_payload.get("started_at") or status_payload.get("started_at") or _now_utc_iso())
                finished_at = str(summary_payload.get("finished_at") or status_payload.get("finished_at") or _now_utc_iso())
                elapsed_ms = float(summary_payload.get("elapsed_ms") or 0.0)
                unique_symbols = list(status_payload.get("unique_symbols") or sorted({str(row.get("symbol")) for row in event_rows if row.get("symbol")}))
                subscribe_result = Result(
                    ok=True,
                    code=ErrorCode.OK,
                    message="materialized subscription watch replay run",
                    data={"mode": "replay"},
                )
                unsubscribe_result = Result(
                    ok=True,
                    code=ErrorCode.OK,
                    message="completed subscription watch replay cleanup",
                    data={"mode": "replay"},
                )
                return Result(
                    ok=True,
                    code=ErrorCode.OK,
                    message="completed subscription watch task",
                    data={
                        "input": {
                            "stock_list": list(stock_list),
                            "max_events": max_events,
                            "max_seconds": max_seconds,
                            "poll_interval": poll_interval,
                        },
                        "subscription": {
                            "session_id": session_id,
                            "provider_instance_id": provider_instance_id,
                            "subscription_id": subscription_id,
                            "run_id": run_paths.run_id,
                        },
                        "summary": {
                            "event_count": int(summary_payload.get("event_count", len(event_rows))),
                            "unique_symbol_count": int(status_payload.get("unique_symbol_count", len(unique_symbols))),
                            "unique_symbols": unique_symbols,
                            "stop_reason": stop_reason,
                            "interrupted": interrupted,
                            "started_at": started_at,
                            "finished_at": finished_at,
                            "elapsed_ms": elapsed_ms,
                            "last_event_at": status_payload.get("last_event_at"),
                        },
                        "status": status_payload,
                        "manifest": copy.deepcopy(materialized.manifest),
                        "artifacts": dict(artifact_paths),
                        "subscribe_result": subscribe_result.to_dict(),
                        "unsubscribe_result": unsubscribe_result.to_dict(),
                    },
                    warnings=[],
                )

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

    def pingan_live_manual_acceptance(
        self,
        *,
        output_path: str | None,
        operator: str | None,
        environment: str | None,
        outcomes: list[str] | None,
        accepted_at: str | None = None,
        evidence_ref: str | None = None,
        dry_run: bool = False,
        overwrite: bool = False,
    ) -> Result:
        def run() -> Result:
            normalized_operator = str(operator or "").strip()
            normalized_environment = str(environment or "").strip()
            normalized_outcomes, invalid_outcomes, missing_outcomes = _normalize_pingan_live_manual_acceptance_outcomes(
                outcomes
            )
            if not output_path:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="output_path is required",
                    data={"missing_fields": ["output_path"]},
                )
            missing_fields = []
            if not normalized_operator:
                missing_fields.append("operator")
            if not normalized_environment:
                missing_fields.append("environment")
            if missing_fields:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="missing live/manual acceptance recorder fields",
                    data={"missing_fields": missing_fields},
                )
            if invalid_outcomes:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="unsupported live/manual acceptance outcome",
                    data={
                        "invalid_outcomes": invalid_outcomes,
                        "supported_outcomes": list(_PINGAN_REQUIRED_AUTOMATED_OUTCOME_STATUSES),
                    },
                )
            if missing_outcomes:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="missing required live/manual acceptance outcomes",
                    data={
                        "covered_outcomes": normalized_outcomes,
                        "missing_outcomes": missing_outcomes,
                        "required_outcomes": list(_PINGAN_REQUIRED_AUTOMATED_OUTCOME_STATUSES),
                    },
                )

            target_path = Path(output_path)
            if target_path.exists() and not overwrite and not dry_run:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"live/manual acceptance artifact already exists: {target_path}",
                    data={"output_path": str(target_path), "overwrite": overwrite},
                )

            resolved_accepted_at = accepted_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            artifact = _build_pingan_live_manual_acceptance_artifact(
                operator=normalized_operator,
                environment=normalized_environment,
                outcomes=normalized_outcomes,
                accepted_at=resolved_accepted_at,
                evidence_ref=str(evidence_ref).strip() if evidence_ref else None,
            )
            artifact_written = False
            if not dry_run:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                artifact_written = True

            return Result(
                ok=True,
                code=ErrorCode.OK,
                message=(
                    "planned PingAn live/manual acceptance artifact"
                    if dry_run
                    else "wrote PingAn live/manual acceptance artifact"
                ),
                data={
                    "input": {
                        "output_path": str(target_path),
                        "operator": normalized_operator,
                        "environment": normalized_environment,
                        "outcomes": normalized_outcomes,
                        "accepted_at": resolved_accepted_at,
                        "evidence_ref": str(evidence_ref).strip() if evidence_ref else None,
                        "dry_run": dry_run,
                        "overwrite": overwrite,
                    },
                    "artifact": artifact,
                    "live_manual_acceptance_record": {
                        "schema": _PINGAN_LIVE_MANUAL_ACCEPTANCE_RECORD_SCHEMA,
                        "artifact_schema": _PINGAN_LIVE_MANUAL_ACCEPTANCE_SCHEMA,
                        "output_path": str(target_path),
                        "artifact_written": artifact_written,
                        "dry_run": dry_run,
                        "overwrite": overwrite,
                        "covered_outcomes": normalized_outcomes,
                        "missing_outcomes": [],
                        "execution_mode": "manual_acceptance_record",
                        "side_effect_level": "none" if dry_run else "file_write",
                        "boundary": (
                            "Records operator-provided live/manual acceptance evidence only; does not execute "
                            "PingAn workflows, control the desktop, submit orders, prove broker production "
                            "readiness, prove implemented status, or promote D-07/D-08."
                        ),
                    },
                },
            )

        result, timing = _capture_task_timing("task.pingan_live_manual_acceptance", run)
        return self._attach_task_metadata(result, task_name="pingan_live_manual_acceptance", timing=timing)

    def pingan_implemented_status_review_result(
        self,
        *,
        review_packet_path: str | None,
        output_path: str | None,
        reviewer: str | None,
        outcome: str | None,
        reason: str | None,
        reviewed_at: str | None = None,
        dry_run: bool = False,
        overwrite: bool = False,
    ) -> Result:
        def run() -> Result:
            normalized_review_packet_path = str(review_packet_path or "").strip()
            normalized_output_path = str(output_path or "").strip()
            normalized_reviewer = str(reviewer or "").strip()
            normalized_outcome = str(outcome or "").strip().lower()
            normalized_reason = str(reason or "").strip()
            missing_fields = []
            if not normalized_review_packet_path:
                missing_fields.append("review_packet_path")
            if not normalized_output_path:
                missing_fields.append("output_path")
            if not normalized_reviewer:
                missing_fields.append("reviewer")
            if not normalized_outcome:
                missing_fields.append("outcome")
            if not normalized_reason:
                missing_fields.append("reason")
            if missing_fields:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="missing implemented-status review result fields",
                    data={"missing_fields": missing_fields},
                )
            supported_outcomes = ["approve", "reject", "defer"]
            if normalized_outcome not in supported_outcomes:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="unsupported implemented-status review result outcome",
                    data={"outcome": normalized_outcome, "supported_outcomes": supported_outcomes},
                )

            packet, packet_error = _load_pingan_implemented_status_review_packet(normalized_review_packet_path)
            if packet_error is not None or packet is None:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="invalid implemented-status review packet",
                    data={"review_packet_path": normalized_review_packet_path, "error": packet_error},
                )

            packet_review_status = str(packet.get("review_status") or "").strip()
            packet_eligible = packet.get("implemented_status_eligible") is True
            if normalized_outcome == "approve" and (
                packet_review_status != "ready_for_manual_review" or not packet_eligible
            ):
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="blocked implemented-status review packet cannot be approved",
                    data={
                        "review_packet_path": normalized_review_packet_path,
                        "packet_review_status": packet_review_status,
                        "implemented_status_eligible": packet_eligible,
                        "blocked_reasons": [
                            "blocked_packet_not_approvable",
                            *_list_from_json(packet.get("blocked_reasons")),
                        ],
                    },
                )

            target_path = Path(normalized_output_path)
            if target_path.exists() and not overwrite and not dry_run:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"implemented-status review result artifact already exists: {target_path}",
                    data={"output_path": str(target_path), "overwrite": overwrite},
                )

            resolved_reviewed_at = reviewed_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            artifact = _build_pingan_implemented_status_review_result_artifact(
                packet=packet,
                review_packet_path=normalized_review_packet_path,
                reviewer=normalized_reviewer,
                outcome=normalized_outcome,
                reason=normalized_reason,
                reviewed_at=resolved_reviewed_at,
                dry_run=dry_run,
            )
            artifact_written = False
            if not dry_run:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                artifact_written = True

            return Result(
                ok=True,
                code=ErrorCode.OK,
                message=(
                    "planned PingAn implemented-status review result artifact"
                    if dry_run
                    else "wrote PingAn implemented-status review result artifact"
                ),
                data={
                    "input": {
                        "review_packet_path": normalized_review_packet_path,
                        "output_path": str(target_path),
                        "reviewer": normalized_reviewer,
                        "outcome": normalized_outcome,
                        "reason": normalized_reason,
                        "reviewed_at": resolved_reviewed_at,
                        "dry_run": dry_run,
                        "overwrite": overwrite,
                    },
                    "implemented_status_review_result": artifact,
                    "review_result_record": {
                        "schema": _PINGAN_IMPLEMENTED_STATUS_REVIEW_RESULT_RECORD_SCHEMA,
                        "artifact_schema": _PINGAN_IMPLEMENTED_STATUS_REVIEW_RESULT_SCHEMA,
                        "review_packet_path": normalized_review_packet_path,
                        "output_path": str(target_path),
                        "artifact_written": artifact_written,
                        "dry_run": dry_run,
                        "overwrite": overwrite,
                        "reviewer": normalized_reviewer,
                        "outcome": normalized_outcome,
                        "packet_review_status": packet_review_status,
                        "packet_decision": packet.get("decision"),
                        "implemented_status_eligible": packet_eligible,
                        "function_tree_status_transition_executed": False,
                        "automatic_status_transition_allowed": False,
                        "order_submitted": False,
                        "control_dispatch_executed": False,
                        "execution_mode": "manual_status_review_result_record",
                        "side_effect_level": "none" if dry_run else "file_write",
                        "boundary": (
                            "Records a maintainer review result only; does not execute PingAn workflows, submit "
                            "orders, prove production readiness, prove implemented status, or promote D-07/D-08."
                        ),
                    },
                },
            )

        result, timing = _capture_task_timing("task.pingan_implemented_status_review_result", run)
        return self._attach_task_metadata(
            result,
            task_name="pingan_implemented_status_review_result",
            timing=timing,
        )

    def pingan_implemented_status_transition_gate(
        self,
        *,
        review_result_path: str | None,
    ) -> Result:
        def run() -> Result:
            normalized_review_result_path = str(review_result_path or "").strip()
            if not normalized_review_result_path:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="review_result_path is required",
                    data={"missing_fields": ["review_result_path"]},
                )

            review_result, review_result_error = _load_pingan_implemented_status_review_result(
                normalized_review_result_path
            )
            if review_result_error is not None or review_result is None:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="invalid implemented-status review result artifact",
                    data={"review_result_path": normalized_review_result_path, "error": review_result_error},
                )

            gate = _build_pingan_implemented_status_transition_gate(
                review_result=review_result,
                review_result_path=normalized_review_result_path,
            )
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message=(
                    "PingAn implemented-status transition gate is eligible for manual review"
                    if gate["eligible_for_status_transition_review"]
                    else "PingAn implemented-status transition gate is blocked"
                ),
                data={
                    "input": {"review_result_path": normalized_review_result_path},
                    "implemented_status_transition_gate": gate,
                },
            )

        result, timing = _capture_task_timing("task.pingan_implemented_status_transition_gate", run)
        return self._attach_task_metadata(
            result,
            task_name="pingan_implemented_status_transition_gate",
            timing=timing,
        )

    def pingan_implemented_status_transition(
        self,
        *,
        transition_gate_path: str | None,
        function_tree_path: str | None,
        output_path: str | None,
        operator: str | None,
        reason: str | None,
        dry_run: bool = True,
        apply: bool = False,
        confirm_transition: bool = False,
        overwrite: bool = False,
    ) -> Result:
        def run() -> Result:
            normalized_transition_gate_path = str(transition_gate_path or "").strip()
            normalized_function_tree_path = str(function_tree_path or "").strip()
            normalized_output_path = str(output_path or "").strip()
            normalized_operator = str(operator or "").strip()
            normalized_reason = str(reason or "").strip()
            missing_fields = []
            if not normalized_transition_gate_path:
                missing_fields.append("transition_gate_path")
            if not normalized_function_tree_path:
                missing_fields.append("function_tree_path")
            if not normalized_output_path:
                missing_fields.append("output_path")
            if not normalized_operator:
                missing_fields.append("operator")
            if not normalized_reason:
                missing_fields.append("reason")
            if apply and not dry_run and not confirm_transition:
                missing_fields.append("confirm_transition")
            if missing_fields:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="missing implemented-status transition fields",
                    data={"missing_fields": missing_fields},
                )
            if not dry_run and not apply:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="apply=true is required when dry_run=false",
                    data={"apply": apply, "dry_run": dry_run},
                )

            transition_gate, transition_gate_error = _load_pingan_implemented_status_transition_gate(
                normalized_transition_gate_path
            )
            if transition_gate_error is not None or transition_gate is None:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="invalid implemented-status transition gate",
                    data={"transition_gate_path": normalized_transition_gate_path, "error": transition_gate_error},
                )
            if transition_gate.get("eligible_for_status_transition_review") is not True:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="implemented-status transition gate is blocked",
                    data={
                        "transition_gate_path": normalized_transition_gate_path,
                        "gate_status": transition_gate.get("gate_status"),
                        "blocked_reasons": _list_from_json(transition_gate.get("blocked_reasons")),
                    },
                )
            if transition_gate.get("gate_status") != "eligible_for_status_transition_review":
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="implemented-status transition gate status is not eligible",
                    data={
                        "transition_gate_path": normalized_transition_gate_path,
                        "gate_status": transition_gate.get("gate_status"),
                    },
                )
            if _list_from_json(transition_gate.get("target_nodes")) != ["D-07", "D-08"]:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="implemented-status transition gate target nodes are unsupported",
                    data={"target_nodes": _list_from_json(transition_gate.get("target_nodes"))},
                )
            if transition_gate.get("function_tree_status_transition_executed") is not False:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="transition gate already reports a status transition",
                    data={
                        "function_tree_status_transition_executed": transition_gate.get(
                            "function_tree_status_transition_executed"
                        )
                    },
                )

            lines, current_statuses, function_tree_error = _load_function_tree_transition_lines(
                normalized_function_tree_path
            )
            if function_tree_error is not None or lines is None:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="invalid FUNCTION_TREE transition target",
                    data={
                        "function_tree_path": normalized_function_tree_path,
                        "error": function_tree_error,
                        "current_statuses": current_statuses,
                    },
                )
            unexpected_statuses = {
                node_id: status for node_id, status in current_statuses.items() if status != "[部分实现]"
            }
            if unexpected_statuses:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="FUNCTION_TREE transition target is not partial",
                    data={"current_statuses": current_statuses, "unexpected_statuses": unexpected_statuses},
                )

            target_path = Path(normalized_output_path)
            if target_path.exists() and not overwrite and not dry_run:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"implemented-status transition record already exists: {target_path}",
                    data={"output_path": str(target_path), "overwrite": overwrite},
                )

            plan = _build_pingan_implemented_status_transition_plan(
                transition_gate=transition_gate,
                transition_gate_path=normalized_transition_gate_path,
                function_tree_path=normalized_function_tree_path,
                output_path=str(target_path),
                operator=normalized_operator,
                reason=normalized_reason,
                dry_run=dry_run,
                apply=apply,
                confirm_transition=confirm_transition,
                transition_executed=False,
                record_written=False,
            )
            record: dict[str, Any] | None = None
            if apply and not dry_run:
                updated_lines = _apply_pingan_function_tree_status_transition(lines)
                Path(normalized_function_tree_path).write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
                transitioned_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                plan = _build_pingan_implemented_status_transition_plan(
                    transition_gate=transition_gate,
                    transition_gate_path=normalized_transition_gate_path,
                    function_tree_path=normalized_function_tree_path,
                    output_path=str(target_path),
                    operator=normalized_operator,
                    reason=normalized_reason,
                    dry_run=dry_run,
                    apply=apply,
                    confirm_transition=confirm_transition,
                    transition_executed=True,
                    record_written=True,
                )
                record = _build_pingan_implemented_status_transition_record(
                    plan=plan,
                    transition_gate=transition_gate,
                    transitioned_at=transitioned_at,
                )
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            data: dict[str, Any] = {"implemented_status_transition_plan": plan}
            if record is not None:
                data["implemented_status_transition_record"] = record
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message=(
                    "planned PingAn implemented-status FUNCTION_TREE transition"
                    if dry_run
                    else "executed PingAn implemented-status FUNCTION_TREE transition"
                ),
                data=data,
            )

        result, timing = _capture_task_timing("task.pingan_implemented_status_transition", run)
        return self._attach_task_metadata(
            result,
            task_name="pingan_implemented_status_transition",
            timing=timing,
        )

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
        live_manual_acceptance_path: str | None = None,
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
                    "live_manual_acceptance_path": live_manual_acceptance_path,
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
                "value_diagnostics": _build_trade_audit_value_diagnostics(report_entries, scope="daily"),
                "acceptance_outcome_coverage_status": _build_pingan_acceptance_outcome_coverage_status(
                    report_entries,
                    source_kind="daily_report",
                    producer="task trade-audit-daily-report",
                    live_manual_acceptance_path=live_manual_acceptance_path,
                ),
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
        live_manual_acceptance_path: str | None = None,
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
                    "live_manual_acceptance_path": live_manual_acceptance_path,
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
                "value_diagnostics": _build_trade_audit_value_diagnostics(report_entries, scope="period"),
                "acceptance_outcome_coverage_status": _build_pingan_acceptance_outcome_coverage_status(
                    report_entries,
                    source_kind="period_report",
                    producer="task trade-audit-period-report",
                    live_manual_acceptance_path=live_manual_acceptance_path,
                ),
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

    def trade_audit_cross_ledger_query(
        self,
        *,
        audit_dir: str | None = None,
        submission_ledger_path: str | None = None,
        task_ledger_jsonl_path: str | None = None,
        task_ledger_csv_path: str | None = None,
        cache_output_path: str | None = None,
        audit_id: str | None = None,
        contract_no: str | None = None,
        submission_key: str | None = None,
        code: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        json_output_path: str | None = None,
        csv_output_path: str | None = None,
    ) -> Result:
        def run() -> Result:
            resolved_audit_dir = _resolve_trade_audit_dir(self.profile_options, audit_dir=audit_dir)
            resolved_submission_ledger_path = (
                Path(submission_ledger_path)
                if submission_ledger_path is not None
                else Path(
                    str(
                        self.profile_options.get(
                            "submission_ledger_path",
                            get_pingan_submission_ledger_path(),
                        )
                    )
                )
            )
            default_task_ledger_jsonl_path, default_task_ledger_csv_path = _resolve_task_ledger_paths(self.profile_options)
            if task_ledger_jsonl_path is None and task_ledger_csv_path is None:
                resolved_task_ledger_jsonl_path: Path | None = default_task_ledger_jsonl_path
                resolved_task_ledger_csv_path: Path | None = default_task_ledger_csv_path
            else:
                resolved_task_ledger_jsonl_path = (
                    Path(task_ledger_jsonl_path) if task_ledger_jsonl_path is not None else None
                )
                resolved_task_ledger_csv_path = Path(task_ledger_csv_path) if task_ledger_csv_path is not None else None
            resolved_cache_output_path = (
                Path(cache_output_path)
                if cache_output_path is not None
                else None
            )

            try:
                payload = query_trade_audit_cross_ledger(
                    audit_dir=resolved_audit_dir,
                    submission_ledger_path=resolved_submission_ledger_path,
                    task_ledger_jsonl_path=resolved_task_ledger_jsonl_path,
                    task_ledger_csv_path=resolved_task_ledger_csv_path,
                    cache_output_path=resolved_cache_output_path,
                    audit_id=audit_id,
                    contract_no=contract_no,
                    submission_key=submission_key,
                    code=code,
                    status=status,
                    limit=limit,
                )
            except FileNotFoundError:
                return Result(
                    ok=False,
                    code=ErrorCode.PATH_NOT_FOUND,
                    message="trade audit cross-ledger query task could not find an audit directory",
                    data={
                        "input": {
                            "audit_dir": str(resolved_audit_dir),
                            "submission_ledger_path": str(resolved_submission_ledger_path),
                            "task_ledger_jsonl_path": (
                                None if resolved_task_ledger_jsonl_path is None else str(resolved_task_ledger_jsonl_path)
                            ),
                            "task_ledger_csv_path": (
                                None if resolved_task_ledger_csv_path is None else str(resolved_task_ledger_csv_path)
                            ),
                        }
                    },
                    next_action="Run trade audit workflows first or provide explicit ledger paths.",
                )

            result_payload: dict[str, Any] = copy.deepcopy(payload)
            warnings = list(result_payload.pop("warnings", []))
            rows = list(result_payload.get("rows", []))
            artifacts: dict[str, Any] = {}
            if cache_output_path is not None:
                artifacts["cache_output_path"] = str(resolved_cache_output_path)
            if json_output_path is not None or csv_output_path is not None:
                export_dir = _resolve_export_dir(self.profile_options)
                export_stem = _resolve_export_stem(self.profile_options, "trade-audit-cross-ledger-query")
                summary_json_path = Path(json_output_path) if json_output_path else export_dir / f"{export_stem}.json"
                summary_csv_path = Path(csv_output_path) if csv_output_path else export_dir / f"{export_stem}.csv"
                _write_json_file(summary_json_path, result_payload)
                _write_csv_file(summary_csv_path, _build_trade_audit_cross_ledger_csv_rows(rows))
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
                message="completed trade audit cross-ledger query task",
                data=result_payload,
                warnings=warnings,
            )

        result, timing = _capture_task_timing("task.trade_audit_cross_ledger_query", run)
        return self._attach_task_metadata(result, task_name="trade_audit_cross_ledger_query", timing=timing)

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
        lifecycle_statefile_path: str | None = None,
        lifecycle_owner_token: str | None = None,
        lifecycle_stale_after_seconds: float = 300.0,
        require_lifecycle_owner_lock: bool = False,
        require_broker_readiness: bool = False,
    ) -> Result:
        def run() -> Result:
            lifecycle_guard_kwargs = _build_task_lifecycle_owner_lock_guard_kwargs(
                lifecycle_statefile_path=lifecycle_statefile_path,
                lifecycle_owner_token=lifecycle_owner_token,
                lifecycle_stale_after_seconds=lifecycle_stale_after_seconds,
                require_lifecycle_owner_lock=require_lifecycle_owner_lock,
            )
            broker_readiness_guard_kwargs = _build_task_broker_readiness_guard_kwargs(
                require_broker_readiness=require_broker_readiness
            )
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
                                **lifecycle_guard_kwargs,
                                **broker_readiness_guard_kwargs,
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
                **lifecycle_guard_kwargs,
                **broker_readiness_guard_kwargs,
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
                        **lifecycle_guard_kwargs,
                        **broker_readiness_guard_kwargs,
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

    def trade_sell(
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
        lifecycle_statefile_path: str | None = None,
        lifecycle_owner_token: str | None = None,
        lifecycle_stale_after_seconds: float = 300.0,
        require_lifecycle_owner_lock: bool = False,
        require_broker_readiness: bool = False,
    ) -> Result:
        def run() -> Result:
            lifecycle_guard_kwargs = _build_task_lifecycle_owner_lock_guard_kwargs(
                lifecycle_statefile_path=lifecycle_statefile_path,
                lifecycle_owner_token=lifecycle_owner_token,
                lifecycle_stale_after_seconds=lifecycle_stale_after_seconds,
                require_lifecycle_owner_lock=require_lifecycle_owner_lock,
            )
            broker_readiness_guard_kwargs = _build_task_broker_readiness_guard_kwargs(
                require_broker_readiness=require_broker_readiness
            )
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
                        message="trade sell task aborted during environment refresh",
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
                                **lifecycle_guard_kwargs,
                                **broker_readiness_guard_kwargs,
                            },
                            "refresh_result": refresh_result.to_dict(),
                        },
                        warnings=refresh_result.warnings,
                        next_action=refresh_result.next_action,
                    )
            trade_result = self.trade_manager.pingan.sell(
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
                **lifecycle_guard_kwargs,
                **broker_readiness_guard_kwargs,
            )
            if not trade_result.ok:
                return trade_result
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="completed trade sell task",
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
                        **lifecycle_guard_kwargs,
                        **broker_readiness_guard_kwargs,
                    },
                    "refresh_result": refresh_result.to_dict() if refresh_result is not None else None,
                    "trade_result": trade_result.to_dict(),
                    "artifacts": copy.deepcopy(trade_result.data.get("artifacts", {})),
                    "result_dialog": copy.deepcopy(trade_result.data.get("result_dialog", {})),
                },
                warnings=list(trade_result.warnings),
                next_action=trade_result.next_action,
            )

        result, timing = _capture_task_timing("task.trade_sell", run)
        return self._attach_task_metadata(result, task_name="trade_sell", timing=timing)

    def trade_submit_once(
        self,
        *,
        port: str,
        code: str,
        price: str,
        quantity: int,
        side: str = "buy",
        baudrate: int = 115200,
        timeout: float = 2.0,
        max_depth: int = 12,
        close_result_dialog: bool = True,
        submission_key: str | None = None,
        max_price: float | None = None,
        refresh_before_trade: bool | None = None,
        refresh_market: str | None = None,
        refresh_force: bool | None = None,
        lifecycle_statefile_path: str | None = None,
        lifecycle_owner_token: str | None = None,
        lifecycle_stale_after_seconds: float = 300.0,
        require_lifecycle_owner_lock: bool = False,
        require_broker_readiness: bool = False,
    ) -> Result:
        def run() -> Result:
            normalized_side = str(side or "buy").strip().lower()
            lifecycle_guard_kwargs = _build_task_lifecycle_owner_lock_guard_kwargs(
                lifecycle_statefile_path=lifecycle_statefile_path,
                lifecycle_owner_token=lifecycle_owner_token,
                lifecycle_stale_after_seconds=lifecycle_stale_after_seconds,
                require_lifecycle_owner_lock=require_lifecycle_owner_lock,
            )
            broker_readiness_guard_kwargs = _build_task_broker_readiness_guard_kwargs(
                require_broker_readiness=require_broker_readiness
            )
            common_input = {
                "port": port,
                "side": normalized_side,
                "code": code,
                "price": price,
                "quantity": quantity,
                "baudrate": baudrate,
                "timeout": timeout,
                "max_depth": max_depth,
                "close_result_dialog": close_result_dialog,
                "submission_key": submission_key,
                "max_price": max_price,
                **lifecycle_guard_kwargs,
                **broker_readiness_guard_kwargs,
            }
            if normalized_side not in {"buy", "sell"}:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"unsupported trade submit-once side: {side}",
                    data={"input": common_input, "supported_sides": ["buy", "sell"]},
                )
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
                                **common_input,
                                "refresh_before_trade": resolved_refresh_first,
                                "refresh_market": resolved_refresh_market,
                                "refresh_force": resolved_refresh_force,
                            },
                            "refresh_result": refresh_result.to_dict(),
                        },
                        warnings=refresh_result.warnings,
                        next_action=refresh_result.next_action,
                    )
            trade_kwargs = {
                "port": port,
                "baudrate": baudrate,
                "timeout": timeout,
                "code": code,
                "price": price,
                "quantity": quantity,
                "max_depth": max_depth,
                "close_result_dialog": close_result_dialog,
                "submission_key": submission_key,
                "max_price": max_price,
                **lifecycle_guard_kwargs,
                **broker_readiness_guard_kwargs,
            }
            if normalized_side == "sell":
                trade_result = self.trade_manager.pingan.sell_submit_once(**trade_kwargs)
            else:
                trade_result = self.trade_manager.pingan.buy_submit_once(**trade_kwargs)
            if not trade_result.ok:
                return trade_result
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="completed trade submit-once task",
                data={
                    "input": {
                        **common_input,
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
        lifecycle_statefile_path: str | None = None,
        lifecycle_owner_token: str | None = None,
        lifecycle_stale_after_seconds: float = 300.0,
        require_lifecycle_owner_lock: bool = False,
    ) -> Result:
        def run() -> Result:
            lifecycle_guard_kwargs = _build_task_lifecycle_owner_lock_guard_kwargs(
                lifecycle_statefile_path=lifecycle_statefile_path,
                lifecycle_owner_token=lifecycle_owner_token,
                lifecycle_stale_after_seconds=lifecycle_stale_after_seconds,
                require_lifecycle_owner_lock=require_lifecycle_owner_lock,
            )
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
                                **lifecycle_guard_kwargs,
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
                **lifecycle_guard_kwargs,
            )
            if not trade_result.ok:
                return trade_result
            input_payload = {
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
            }
            input_payload.update(lifecycle_guard_kwargs)
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="completed trade submit-ready task",
                data={
                    "input": input_payload,
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
        lifecycle_statefile_path: str | None = None,
        lifecycle_owner_token: str | None = None,
        lifecycle_stale_after_seconds: float = 300.0,
        require_lifecycle_owner_lock: bool = False,
        require_broker_readiness: bool = False,
    ) -> Result:
        def run() -> Result:
            lifecycle_guard_kwargs = _build_task_lifecycle_owner_lock_guard_kwargs(
                lifecycle_statefile_path=lifecycle_statefile_path,
                lifecycle_owner_token=lifecycle_owner_token,
                lifecycle_stale_after_seconds=lifecycle_stale_after_seconds,
                require_lifecycle_owner_lock=require_lifecycle_owner_lock,
            )
            broker_readiness_guard_kwargs = _build_task_broker_readiness_guard_kwargs(
                require_broker_readiness=require_broker_readiness
            )
            kwargs: dict[str, Any] = {
                "dialog_lookup_mode": dialog_lookup_mode,
                "confirm_timeout": confirm_timeout,
                "result_timeout": result_timeout,
                "close_result_dialog": close_result_dialog,
            }
            if result_close_pre_delay is not None:
                kwargs["result_close_pre_delay"] = result_close_pre_delay
            kwargs.update(lifecycle_guard_kwargs)
            kwargs.update(broker_readiness_guard_kwargs)
            trade_result = self.trade_manager.pingan.confirm_current(**kwargs)
            if not trade_result.ok:
                return trade_result
            input_payload = {
                "dialog_lookup_mode": dialog_lookup_mode,
                "confirm_timeout": confirm_timeout,
                "result_timeout": result_timeout,
                "close_result_dialog": close_result_dialog,
                "result_close_pre_delay": result_close_pre_delay,
            }
            input_payload.update(lifecycle_guard_kwargs)
            input_payload.update(broker_readiness_guard_kwargs)
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="completed trade confirm-current task",
                data={
                    "input": input_payload,
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
        lifecycle_statefile_path: str | None = None,
        lifecycle_owner_token: str | None = None,
        lifecycle_stale_after_seconds: float = 300.0,
        require_lifecycle_owner_lock: bool = False,
    ) -> Result:
        def run() -> Result:
            lifecycle_guard_kwargs = _build_task_lifecycle_owner_lock_guard_kwargs(
                lifecycle_statefile_path=lifecycle_statefile_path,
                lifecycle_owner_token=lifecycle_owner_token,
                lifecycle_stale_after_seconds=lifecycle_stale_after_seconds,
                require_lifecycle_owner_lock=require_lifecycle_owner_lock,
            )
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
                **lifecycle_guard_kwargs,
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
                        **lifecycle_guard_kwargs,
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
