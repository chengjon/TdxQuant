from __future__ import annotations

import copy
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, TypeVar
from uuid import uuid4

from ..models import ErrorCode, OrderRequest, Result

T = TypeVar("T")
DEFAULT_TRADE_STABILITY = "beta"
DEFAULT_TRADE_SIDE_EFFECT_LEVEL = "live_side_effecting"
TRADE_AUDIT_SCHEMA_VERSION = "2026-04-29"


def get_trade_profile_path() -> Path:
    return Path(__file__).resolve().parents[2] / "runtime" / "trade-profiles.json"


def get_pingan_last_order_state_path() -> Path:
    return Path(__file__).resolve().parents[2] / "runtime" / "pingan-last-order.json"


def get_pingan_order_event_log_path() -> Path:
    return Path(__file__).resolve().parents[2] / "runtime" / "pingan-order-events.jsonl"


def get_pingan_submission_ledger_path() -> Path:
    return Path(__file__).resolve().parents[2] / "runtime" / "pingan-submission-ledger.jsonl"


def get_pingan_trade_audit_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "runtime" / "trade-audits"


def load_trade_profiles(path: Path | None = None) -> dict[str, dict[str, Any]]:
    profile_path = path or get_trade_profile_path()
    payload = json.loads(profile_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("trade profile file must contain a JSON object")
    profiles: dict[str, dict[str, Any]] = {}
    for name, value in payload.items():
        if not isinstance(name, str) or not isinstance(value, dict):
            raise ValueError("trade profile entries must map profile names to JSON objects")
        profiles[name] = value
    return profiles


def resolve_trade_profile(
    profile_name: str,
    overrides: dict[str, Any] | None = None,
    *,
    path: Path | None = None,
    profiles: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    available = profiles if profiles is not None else load_trade_profiles(path)
    try:
        resolved = copy.deepcopy(available[profile_name])
    except KeyError as exc:
        raise ValueError(f"unsupported trade profile: {profile_name}") from exc
    for key, value in (overrides or {}).items():
        if value is not None:
            resolved[key] = copy.deepcopy(value)
    return resolved


def capture_trade_timing(step_name: str, fn: Callable[[], T]) -> tuple[T, dict[str, Any]]:
    started_at = time.perf_counter()
    value = fn()
    total_ms = round((time.perf_counter() - started_at) * 1000, 3)
    return value, {"manager_call": {"name": step_name, "total_ms": total_ms}}


def attach_trade_metadata(
    result: Result,
    *,
    profile_name: str,
    profile_options: dict[str, Any],
    broker: str,
    method: str,
    title_keyword: str,
    exe_path: str | None,
    timing: dict[str, Any],
) -> Result:
    result.data["manager"] = {
        "entrypoint": "TdxTradeManager",
        "broker": broker,
        "method": method,
        "title_keyword": title_keyword,
        "exe_path": exe_path,
    }
    result.data["trade_profile"] = {
        "name": profile_name,
        "options": copy.deepcopy(profile_options),
    }
    result.data.setdefault("timing", {}).update(timing)
    return result


def evaluate_trade_risk_gate(
    *,
    code: str,
    price: str,
    quantity: int,
    max_price: float | None = None,
) -> dict[str, Any]:
    requested_price: float | None
    request = OrderRequest(code=code, quantity=quantity, price=price)
    order_request_issues = request.validate()
    checks: list[dict[str, Any]] = [
        {
            "name": "order_request",
            "passed": not order_request_issues,
            "issues": list(order_request_issues),
        }
    ]
    try:
        requested_price = float(price)
    except (TypeError, ValueError):
        requested_price = None

    rejection_messages = list(order_request_issues)
    if max_price is not None:
        max_price_passed = requested_price is not None and requested_price <= max_price
        max_price_issues: list[str] = []
        if not max_price_passed:
            if requested_price is None:
                max_price_issues.append("price is not numeric for max_price check")
            else:
                max_price_issues.append(f"requested price {requested_price:.6g} exceeds max_price {max_price:.6g}")
        checks.append(
            {
                "name": "max_price",
                "passed": max_price_passed,
                "requested_price": requested_price,
                "max_price": max_price,
                "issues": max_price_issues,
            }
        )
        rejection_messages.extend(max_price_issues)

    return {
        "passed": not rejection_messages,
        "checks": checks,
        "requested_price": requested_price,
        "max_price": max_price,
        "rejection_reason": "; ".join(rejection_messages) if rejection_messages else None,
    }


def attach_trade_safety_metadata(
    result: Result,
    *,
    submission_key: str | None,
    risk_gate: dict[str, Any],
    idempotency: dict[str, Any] | None = None,
    stability: str = DEFAULT_TRADE_STABILITY,
    side_effect_level: str = DEFAULT_TRADE_SIDE_EFFECT_LEVEL,
) -> Result:
    result.data["trade_safety"] = {
        "stability": stability,
        "side_effect_level": side_effect_level,
        "submission_key": submission_key,
        "risk_gate": copy.deepcopy(risk_gate),
        "idempotency": copy.deepcopy(idempotency or {"decision": "no_submission_key", "fingerprint": None, "ledger_consulted": False}),
    }
    return result


def _sanitize_filename_component(value: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-z._-]+", "-", value.strip())
    normalized = normalized.strip("-_.")
    return normalized or "unknown"


def _resolve_trade_audit_status(
    *,
    result: Result,
    risk_gate: dict[str, Any],
    idempotency: dict[str, Any] | None,
) -> str:
    idempotency_decision = str((idempotency or {}).get("decision") or "unknown")
    if idempotency_decision == "skip_duplicate":
        return "replayed"
    if idempotency_decision == "reject_conflict" or not bool(risk_gate.get("passed", True)) or result.code == ErrorCode.INVALID_REQUEST:
        return "rejected"
    if result.ok:
        return "confirmed"
    return "failed"


def attach_trade_audit_metadata(
    result: Result,
    *,
    broker: str,
    method: str,
    submission_key: str | None,
    risk_gate: dict[str, Any],
    idempotency: dict[str, Any] | None = None,
) -> Result:
    trade_safety = result.data.get("trade_safety", {})
    audit_summary = {
        "schema_version": TRADE_AUDIT_SCHEMA_VERSION,
        "audit_id": uuid4().hex,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "status": _resolve_trade_audit_status(result=result, risk_gate=risk_gate, idempotency=idempotency),
        "broker": broker,
        "method": method,
        "contract_no": extract_pingan_contract_no(result),
        "submission_key": submission_key,
        "side_effect_level": trade_safety.get("side_effect_level"),
        "risk_gate_passed": bool(risk_gate.get("passed", True)),
        "idempotency_decision": (idempotency or {}).get("decision"),
    }
    result.data["trade_audit"] = audit_summary
    return result


def build_trade_submission_fingerprint(
    *,
    broker: str,
    method: str,
    code: str,
    price: str,
    quantity: int,
) -> tuple[str, dict[str, Any]]:
    normalized_request = {
        "broker": broker,
        "method": method,
        "code": str(code),
        "price": str(price),
        "quantity": int(quantity),
    }
    fingerprint = hashlib.sha256(
        json.dumps(normalized_request, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return fingerprint, normalized_request


def load_pingan_submission_ledger_rows(path: Path | None = None) -> list[dict[str, Any]]:
    resolved_path = path or get_pingan_submission_ledger_path()
    if not resolved_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for raw_line in resolved_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        payload = json.loads(line)
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def evaluate_trade_submission_idempotency(
    *,
    submission_key: str | None,
    broker: str,
    method: str,
    code: str,
    price: str,
    quantity: int,
    ledger_path: Path | None = None,
) -> dict[str, Any]:
    if submission_key is None:
        return {
            "decision": "no_submission_key",
            "ledger_consulted": False,
            "fingerprint": None,
            "normalized_request": None,
            "conflict_reason": None,
            "prior_row": None,
        }

    fingerprint, normalized_request = build_trade_submission_fingerprint(
        broker=broker,
        method=method,
        code=code,
        price=price,
        quantity=quantity,
    )
    prior_pre_trade_rows: list[dict[str, Any]] = []
    for row in reversed(load_pingan_submission_ledger_rows(ledger_path)):
        if row.get("submission_key") != submission_key:
            continue
        risk_gate_passed = bool(row.get("risk_gate_passed"))
        if not risk_gate_passed:
            prior_pre_trade_rows.append(row)
            continue
        if row.get("fingerprint") == fingerprint:
            return {
                "decision": "skip_duplicate",
                "ledger_consulted": True,
                "fingerprint": fingerprint,
                "normalized_request": normalized_request,
                "conflict_reason": None,
                "prior_row": copy.deepcopy(row),
                "prior_pre_trade_rows": [copy.deepcopy(item) for item in prior_pre_trade_rows],
            }
        return {
            "decision": "reject_conflict",
            "ledger_consulted": True,
            "fingerprint": fingerprint,
            "normalized_request": normalized_request,
            "conflict_reason": "submission_key already used for a different stable desktop trade request",
            "prior_row": copy.deepcopy(row),
            "prior_pre_trade_rows": [copy.deepcopy(item) for item in prior_pre_trade_rows],
        }
    return {
        "decision": "execute",
        "ledger_consulted": True,
        "fingerprint": fingerprint,
        "normalized_request": normalized_request,
        "conflict_reason": None,
        "prior_row": None,
        "prior_pre_trade_rows": [copy.deepcopy(item) for item in prior_pre_trade_rows],
    }


def extract_pingan_contract_no(result: Result) -> str | None:
    result_dialog = result.data.get("result_dialog", {})
    contract_no = result_dialog.get("contract_no")
    return str(contract_no) if contract_no else None


def build_pingan_last_order_state_payload(result: Result) -> dict[str, object]:
    payload: dict[str, object] = {
        "ok": result.ok,
        "code": result.code.value,
        "message": result.message,
        "contract_no": extract_pingan_contract_no(result),
        "input": result.data.get("input", {}),
        "result_dialog": result.data.get("result_dialog", {}),
        "warnings": result.warnings,
        "next_action": result.next_action,
    }
    if "manager" in result.data:
        payload["manager"] = copy.deepcopy(result.data["manager"])
    if "trade_profile" in result.data:
        payload["trade_profile"] = copy.deepcopy(result.data["trade_profile"])
    if "trade_safety" in result.data:
        payload["trade_safety"] = copy.deepcopy(result.data["trade_safety"])
    if "trade_audit" in result.data:
        payload["trade_audit"] = copy.deepcopy(result.data["trade_audit"])
    return payload


def build_result_from_submission_ledger_row(row: dict[str, Any]) -> Result:
    snapshot = row.get("result") or {}
    if not isinstance(snapshot, dict):
        snapshot = {}
    code_value = str(snapshot.get("code") or ErrorCode.EXECUTION_FAILED.value)
    try:
        code = ErrorCode(code_value)
    except ValueError:
        code = ErrorCode.EXECUTION_FAILED
    data: dict[str, Any] = {
        "input": copy.deepcopy(snapshot.get("input", {})),
        "result_dialog": copy.deepcopy(snapshot.get("result_dialog", {})),
    }
    if "manager" in snapshot:
        data["manager"] = copy.deepcopy(snapshot["manager"])
    if "trade_profile" in snapshot:
        data["trade_profile"] = copy.deepcopy(snapshot["trade_profile"])
    if "trade_safety" in snapshot:
        data["trade_safety"] = copy.deepcopy(snapshot["trade_safety"])
    if "trade_audit" in snapshot:
        data["trade_audit"] = copy.deepcopy(snapshot["trade_audit"])
    return Result(
        ok=bool(snapshot.get("ok")),
        code=code,
        message=str(snapshot.get("message") or ""),
        data=data,
        warnings=list(snapshot.get("warnings", [])),
        next_action=snapshot.get("next_action"),
    )


def write_pingan_last_order_state(result: Result, state_path: Path | None = None) -> Path:
    resolved_path = state_path or get_pingan_last_order_state_path()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_pingan_last_order_state_payload(result)
    resolved_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return resolved_path


def append_pingan_order_event(result: Result, log_path: Path | None = None) -> Path:
    resolved_path = log_path or get_pingan_order_event_log_path()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ok": result.ok,
        "code": result.code.value,
        "message": result.message,
        "contract_no": extract_pingan_contract_no(result),
        "input": copy.deepcopy(result.data.get("input", {})),
        "manager": copy.deepcopy(result.data.get("manager", {})),
        "trade_profile": copy.deepcopy(result.data.get("trade_profile", {})),
        "trade_safety": copy.deepcopy(result.data.get("trade_safety", {})),
        "trade_audit": copy.deepcopy(result.data.get("trade_audit", {})),
    }
    with resolved_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    return resolved_path


def append_pingan_submission_ledger_entry(
    result: Result,
    *,
    submission_key: str,
    broker: str,
    method: str,
    code: str,
    price: str,
    quantity: int,
    ledger_path: Path | None = None,
) -> Path:
    resolved_path = ledger_path or get_pingan_submission_ledger_path()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    fingerprint, normalized_request = build_trade_submission_fingerprint(
        broker=broker,
        method=method,
        code=code,
        price=price,
        quantity=quantity,
    )
    trade_safety = copy.deepcopy(result.data.get("trade_safety", {}))
    risk_gate = trade_safety.get("risk_gate", {}) if isinstance(trade_safety, dict) else {}
    idempotency = trade_safety.get("idempotency", {}) if isinstance(trade_safety, dict) else {}
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "submission_key": submission_key,
        "fingerprint": fingerprint,
        "normalized_request": normalized_request,
        "risk_gate_passed": bool(risk_gate.get("passed")),
        "idempotency": copy.deepcopy(idempotency),
        "result": build_pingan_last_order_state_payload(result),
    }
    with resolved_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return resolved_path


def write_pingan_trade_audit(result: Result, audit_dir: Path | None = None) -> Path:
    resolved_dir = audit_dir or get_pingan_trade_audit_dir()
    resolved_dir.mkdir(parents=True, exist_ok=True)
    trade_audit = copy.deepcopy(result.data.get("trade_audit", {}))
    audit_id = str(trade_audit.get("audit_id") or uuid4().hex)
    method = str(trade_audit.get("method") or result.data.get("manager", {}).get("method") or "unknown")
    status = str(trade_audit.get("status") or "unknown")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    audit_path = resolved_dir / (
        f"{timestamp}-{_sanitize_filename_component(method)}-{_sanitize_filename_component(status)}-{audit_id[:8]}.json"
    )
    payload = {
        "schema_version": TRADE_AUDIT_SCHEMA_VERSION,
        "trade_audit": trade_audit,
        "result": result.to_dict(),
    }
    audit_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return audit_path
