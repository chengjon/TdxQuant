from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from uuid import uuid4

from .models import Result
from .result_contract import format_rfc3339, utc_now

BLOCK_MUTATION_SCHEMA_VERSION = "2026-04-28"


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


def _build_block_mutation_summary(
    *,
    mutation_id: str,
    mutation_key: str | None,
    operation: str,
    block_code: str,
    block_name: str | None,
    stocks: list[str] | None,
    show: bool | None,
    status: str,
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "schema_version": BLOCK_MUTATION_SCHEMA_VERSION,
        "mutation_id": mutation_id,
        "mutation_key": mutation_key,
        "operation": operation,
        "status": status,
        "block_code": block_code,
    }
    if block_name is not None:
        summary["block_name"] = block_name
    if stocks is not None:
        summary["requested_stocks"] = list(stocks)
        summary["requested_stock_count"] = len(stocks)
    if show is not None:
        summary["show"] = bool(show)
    return summary


def _write_audit_log(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def apply_block_mutation_safety(
    result: Result,
    *,
    operation: str,
    block_code: str,
    block_name: str | None = None,
    stocks: list[str] | None = None,
    show: bool | None = None,
    mutation_key: str | None = None,
    audit_dir: str | None = None,
) -> Result:
    mutation_id = uuid4().hex
    status = "applied" if result.ok else "failed"
    recorded_at = utc_now()
    summary = _build_block_mutation_summary(
        mutation_id=mutation_id,
        mutation_key=mutation_key,
        operation=operation,
        block_code=block_code,
        block_name=block_name,
        stocks=stocks,
        show=show,
        status=status,
    )
    audit_payload = {
        "schema_version": BLOCK_MUTATION_SCHEMA_VERSION,
        "recorded_at": format_rfc3339(recorded_at),
        "mutation_id": mutation_id,
        "mutation_key": mutation_key,
        "operation": operation,
        "status": status,
        "request": {
            "block_code": block_code,
            **({"block_name": block_name} if block_name is not None else {}),
            **({"stocks": list(stocks)} if stocks is not None else {}),
            **({"show": bool(show)} if show is not None else {}),
        },
        "result": result.to_dict(),
    }
    timestamp = recorded_at.strftime("%Y%m%dT%H%M%S%fZ")
    audit_log_path = _write_audit_log(
        _resolve_block_mutation_audit_dir(audit_dir)
        / f"{timestamp}-{_sanitize_filename_component(operation)}-{_sanitize_filename_component(block_code)}-{mutation_id[:8]}.json",
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
