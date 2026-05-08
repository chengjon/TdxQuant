from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from .models import ErrorCode, Result
from .result_contract import format_rfc3339, utc_now

BLOCK_MUTATION_SCHEMA_VERSION = "2026-05-02"


def get_block_mutation_audit_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "runtime" / "block-mutations"


def _sanitize_filename_component(value: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-z._-]+", "-", value.strip())
    normalized = normalized.strip("-_.")
    return normalized or "unknown"


def _resolve_block_mutation_audit_dir(audit_dir: str | None) -> Path:
    if audit_dir:
        return Path(audit_dir)
    return get_block_mutation_audit_dir()


def _normalize_stock_list(stocks: list[str] | None) -> list[str]:
    if not stocks:
        return []
    seen: set[str] = set()
    normalized: list[str] = []
    for item in stocks:
        if not isinstance(item, str):
            continue
        symbol = item.strip()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        normalized.append(symbol)
    return sorted(normalized)


def _normalize_observed_state(observed_state: dict[str, Any] | None) -> dict[str, Any]:
    payload = dict(observed_state or {})
    if "stocks" in payload:
        payload["stocks"] = _normalize_stock_list(payload.get("stocks"))
        payload["stock_count"] = len(payload["stocks"])
    return payload


def _build_normalized_request(
    *,
    operation: str,
    block_code: str,
    block_name: str | None,
    stocks: list[str] | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "operation": operation,
        "block_code": block_code,
    }
    if block_name is not None:
        payload["block_name"] = block_name
    if stocks is not None:
        payload["stocks"] = _normalize_stock_list(stocks)
    return payload


def _build_desired_state(
    *,
    operation: str,
    block_code: str,
    block_name: str | None,
    stocks: list[str] | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "block_code": block_code,
    }
    if operation == "create_sector":
        payload.update({"exists": True, "block_name": block_name})
    elif operation == "delete_sector":
        payload.update({"exists": False})
    elif operation == "rename_sector":
        payload.update({"exists": True, "block_name": block_name})
    elif operation == "clear_sector":
        payload.update({"exists": True, "stocks": []})
    elif operation == "send_user_block":
        payload.update({"exists": True, "stocks": _normalize_stock_list(stocks)})
    else:
        raise ValueError(f"unsupported block mutation operation: {operation}")
    return payload


def _build_governance_summary(
    *,
    mutation_id: str,
    mutation_key: str | None,
    operation: str,
    block_code: str,
    block_name: str | None,
    stocks: list[str] | None,
    show: bool | None,
    status: str,
    governance_decision: str,
    governance_reason: str,
    desired_state: dict[str, Any],
    observed_state: dict[str, Any] | None,
    related_mutation_id: str | None = None,
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "schema_version": BLOCK_MUTATION_SCHEMA_VERSION,
        "mutation_id": mutation_id,
        "mutation_key": mutation_key,
        "operation": operation,
        "status": status,
        "governance_decision": governance_decision,
        "governance_reason": governance_reason,
        "block_code": block_code,
        "desired_state": desired_state,
        "observed_state": observed_state or {},
    }
    if block_name is not None:
        summary["block_name"] = block_name
    if stocks is not None:
        summary["requested_stocks"] = list(stocks)
        summary["requested_stock_count"] = len(stocks)
    if show is not None:
        summary["show"] = bool(show)
    if related_mutation_id is not None:
        summary["related_mutation_id"] = related_mutation_id
    return summary


def _write_audit_log(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _iter_audit_payloads(audit_dir: Path) -> list[dict[str, Any]]:
    if not audit_dir.exists():
        return []
    payloads: list[dict[str, Any]] = []
    for path in sorted(audit_dir.glob("*.json"), reverse=True):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(payload, dict):
            payloads.append(payload)
    return payloads


def _find_prior_mutation_by_key(mutation_key: str, audit_dir: Path) -> dict[str, Any] | None:
    for payload in _iter_audit_payloads(audit_dir):
        if payload.get("mutation_key") == mutation_key:
            return payload
    return None


def _build_probe_failure_result(operation: str, probe_result: Result) -> Result:
    return Result(
        ok=False,
        code=probe_result.code,
        message=f"{operation} governance probe failed",
        data={"state_probe_result": probe_result.to_dict()},
        warnings=list(probe_result.warnings),
        next_action=probe_result.next_action,
    )


def _decision_for_observed_state(
    *,
    operation: str,
    block_name: str | None,
    stocks: list[str] | None,
    observed_state: dict[str, Any],
) -> tuple[str, str]:
    exists = bool(observed_state.get("exists", False))
    observed_name = observed_state.get("block_name")
    observed_stocks = _normalize_stock_list(observed_state.get("stocks"))
    desired_stocks = _normalize_stock_list(stocks)

    if operation == "create_sector":
        if not exists:
            return "execute", "missing_block"
        if observed_name == block_name:
            return "skip", "already_applied"
        return "reject", "name_conflict"

    if operation == "delete_sector":
        if not exists:
            return "skip", "already_absent"
        return "execute", "existing_block"

    if operation == "rename_sector":
        if not exists:
            return "reject", "missing_block"
        if observed_name == block_name:
            return "skip", "already_applied"
        return "execute", "name_diff_detected"

    if operation == "clear_sector":
        if not exists:
            return "reject", "missing_block"
        if not observed_stocks:
            return "skip", "already_applied"
        return "execute", "state_diff_detected"

    if operation == "send_user_block":
        if not exists:
            return "reject", "missing_block"
        if observed_stocks == desired_stocks:
            return "skip", "already_applied"
        return "execute", "state_diff_detected"

    raise ValueError(f"unsupported block mutation operation: {operation}")


def _finalize_block_mutation_result(
    result: Result,
    *,
    audit_dir: Path,
    mutation_id: str,
    mutation_key: str | None,
    operation: str,
    block_code: str,
    block_name: str | None,
    stocks: list[str] | None,
    show: bool | None,
    status: str,
    governance_decision: str,
    governance_reason: str,
    desired_state: dict[str, Any],
    observed_state: dict[str, Any] | None,
    normalized_request: dict[str, Any],
    related_mutation_id: str | None = None,
) -> Result:
    recorded_at = utc_now()
    audit_request: dict[str, Any] = {"block_code": block_code}
    if block_name is not None:
        audit_request["block_name"] = block_name
    if stocks is not None:
        audit_request["stocks"] = list(stocks)
    if show is not None:
        audit_request["show"] = bool(show)

    normalized_observed_state = _normalize_observed_state(observed_state)
    summary = _build_governance_summary(
        mutation_id=mutation_id,
        mutation_key=mutation_key,
        operation=operation,
        block_code=block_code,
        block_name=block_name,
        stocks=stocks,
        show=show,
        status=status,
        governance_decision=governance_decision,
        governance_reason=governance_reason,
        desired_state=desired_state,
        observed_state=normalized_observed_state,
        related_mutation_id=related_mutation_id,
    )
    audit_payload: dict[str, Any] = {
        "schema_version": BLOCK_MUTATION_SCHEMA_VERSION,
        "recorded_at": format_rfc3339(recorded_at),
        "mutation_id": mutation_id,
        "mutation_key": mutation_key,
        "operation": operation,
        "status": status,
        "governance_decision": governance_decision,
        "governance_reason": governance_reason,
        "normalized_request": normalized_request,
        "desired_state": desired_state,
        "observed_state": normalized_observed_state,
        "request": audit_request,
        "result": result.to_dict(),
    }
    if related_mutation_id is not None:
        audit_payload["related_mutation_id"] = related_mutation_id
    timestamp = recorded_at.strftime("%Y%m%dT%H%M%S%fZ")
    audit_log_path = _write_audit_log(
        audit_dir / f"{timestamp}-{_sanitize_filename_component(operation)}-{_sanitize_filename_component(block_code)}-{mutation_id[:8]}.json",
        audit_payload,
    )

    result.data["block_mutation"] = summary
    artifacts = result.data.get("artifacts")
    if not isinstance(artifacts, dict):
        artifacts = {}
        result.data["artifacts"] = artifacts
    artifacts["audit_log_path"] = str(audit_log_path)
    result._provider_artifacts = [
        {
            "kind": "block_mutation_audit",
            "path": str(audit_log_path),
        }
    ]
    return result


def apply_block_mutation_safety(
    *,
    operation: str,
    block_code: str,
    execute_write: Callable[[], Result],
    observed_state: dict[str, Any] | Result | Callable[[], dict[str, Any] | Result],
    block_name: str | None = None,
    stocks: list[str] | None = None,
    show: bool | None = None,
    mutation_key: str | None = None,
    audit_dir: str | None = None,
) -> Result:
    mutation_id = uuid4().hex
    resolved_audit_dir = _resolve_block_mutation_audit_dir(audit_dir)
    normalized_request = _build_normalized_request(
        operation=operation,
        block_code=block_code,
        block_name=block_name,
        stocks=stocks,
    )
    desired_state = _build_desired_state(
        operation=operation,
        block_code=block_code,
        block_name=block_name,
        stocks=stocks,
    )

    if mutation_key is not None:
        prior_payload = _find_prior_mutation_by_key(mutation_key, resolved_audit_dir)
        if prior_payload is not None:
            prior_request = prior_payload.get("normalized_request")
            prior_mutation_id = prior_payload.get("mutation_id")
            if prior_request == normalized_request:
                duplicate_result = Result(
                    ok=True,
                    code=ErrorCode.OK,
                    message=f"skipped duplicate {operation} replay for mutation_key {mutation_key}",
                    data={},
                )
                return _finalize_block_mutation_result(
                    duplicate_result,
                    audit_dir=resolved_audit_dir,
                    mutation_id=mutation_id,
                    mutation_key=mutation_key,
                    operation=operation,
                    block_code=block_code,
                    block_name=block_name,
                    stocks=stocks,
                    show=show,
                    status="noop",
                    governance_decision="skip",
                    governance_reason="mutation_key_replay",
                    desired_state=desired_state,
                    observed_state={
                        "source": "mutation_key_history",
                        "prior_mutation_id": prior_mutation_id,
                        "prior_status": prior_payload.get("status"),
                    },
                    normalized_request=normalized_request,
                    related_mutation_id=prior_mutation_id if isinstance(prior_mutation_id, str) else None,
                )
            conflict_result = Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message=f"mutation_key {mutation_key} conflicts with a different prior block mutation request",
                data={},
                next_action="Use a new mutation_key for a different block mutation request.",
            )
            return _finalize_block_mutation_result(
                conflict_result,
                audit_dir=resolved_audit_dir,
                mutation_id=mutation_id,
                mutation_key=mutation_key,
                operation=operation,
                block_code=block_code,
                block_name=block_name,
                stocks=stocks,
                show=show,
                status="rejected",
                governance_decision="reject",
                governance_reason="mutation_key_conflict",
                desired_state=desired_state,
                observed_state={
                    "source": "mutation_key_history",
                    "prior_mutation_id": prior_payload.get("mutation_id"),
                    "prior_normalized_request": prior_request,
                },
                normalized_request=normalized_request,
                related_mutation_id=prior_payload.get("mutation_id")
                if isinstance(prior_payload.get("mutation_id"), str)
                else None,
            )

    resolved_observed_state = observed_state() if callable(observed_state) else observed_state

    if isinstance(resolved_observed_state, Result):
        return _finalize_block_mutation_result(
            _build_probe_failure_result(operation, resolved_observed_state),
            audit_dir=resolved_audit_dir,
            mutation_id=mutation_id,
            mutation_key=mutation_key,
            operation=operation,
            block_code=block_code,
            block_name=block_name,
            stocks=stocks,
            show=show,
            status="failed",
            governance_decision="reject",
            governance_reason="state_probe_failed",
            desired_state=desired_state,
            observed_state={"source": "state_probe", "available": False},
            normalized_request=normalized_request,
        )

    normalized_observed_state = _normalize_observed_state(resolved_observed_state)
    governance_decision, governance_reason = _decision_for_observed_state(
        operation=operation,
        block_name=block_name,
        stocks=stocks,
        observed_state=normalized_observed_state,
    )
    if governance_decision == "skip":
        noop_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message=f"skipped {operation} because the target block state is already applied",
            data={},
        )
        return _finalize_block_mutation_result(
            noop_result,
            audit_dir=resolved_audit_dir,
            mutation_id=mutation_id,
            mutation_key=mutation_key,
            operation=operation,
            block_code=block_code,
            block_name=block_name,
            stocks=stocks,
            show=show,
            status="noop",
            governance_decision="skip",
            governance_reason=governance_reason,
            desired_state=desired_state,
            observed_state=normalized_observed_state,
            normalized_request=normalized_request,
        )
    if governance_decision == "reject":
        reject_result = Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message=f"rejected {operation} because the current block state conflicts with the requested target state",
            data={},
            next_action="Inspect the block mutation governance summary and adjust the requested block state.",
        )
        return _finalize_block_mutation_result(
            reject_result,
            audit_dir=resolved_audit_dir,
            mutation_id=mutation_id,
            mutation_key=mutation_key,
            operation=operation,
            block_code=block_code,
            block_name=block_name,
            stocks=stocks,
            show=show,
            status="rejected",
            governance_decision="reject",
            governance_reason=governance_reason,
            desired_state=desired_state,
            observed_state=normalized_observed_state,
            normalized_request=normalized_request,
        )

    write_result = execute_write()
    return _finalize_block_mutation_result(
        write_result,
        audit_dir=resolved_audit_dir,
        mutation_id=mutation_id,
        mutation_key=mutation_key,
        operation=operation,
        block_code=block_code,
        block_name=block_name,
        stocks=stocks,
        show=show,
        status="applied" if write_result.ok else "failed",
        governance_decision="execute",
        governance_reason=governance_reason,
        desired_state=desired_state,
        observed_state=normalized_observed_state,
        normalized_request=normalized_request,
    )
