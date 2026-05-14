from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from .models import ErrorCode, Result
from .result_contract import format_rfc3339, utc_now

BLOCK_SYNC_SCHEMA_VERSION = "2026-05-03"
BLOCK_SYNC_WRITE_POLICIES: dict[str, tuple[str, bool]] = {
    "replace": ("replace", False),
    "merge": ("merge", False),
    "replace_dry_run": ("replace", True),
    "merge_dry_run": ("merge", True),
}


def _normalize_stock_list(values: list[str] | None) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for item in values or []:
        stock = str(item).strip().upper()
        if not stock or stock in seen:
            continue
        seen.add(stock)
        normalized.append(stock)
    return sorted(normalized)


def _sanitize_filename_component(value: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-z._-]+", "-", value.strip())
    normalized = normalized.strip("-_.")
    return normalized or "unknown"


def get_block_sync_audit_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "runtime" / "block-sync"


def _resolve_block_sync_audit_dir(audit_dir: str | None) -> Path:
    if audit_dir:
        return Path(audit_dir)
    return get_block_sync_audit_dir()


def _canonical_sync_request(
    *,
    block_code: str,
    symbols: list[str] | None,
    mode: str,
    create_if_missing: bool,
    dry_run: bool,
    show: bool,
    write_policy: str,
) -> dict[str, Any]:
    return {
        "block_code": block_code,
        "symbols": _normalize_stock_list(symbols),
        "write_policy": write_policy,
        "mode": mode,
        "create_if_missing": create_if_missing,
        "dry_run": dry_run,
        "show": show,
    }


def _policy_from_mode(mode: str, dry_run: bool) -> str:
    return f"{mode}_dry_run" if dry_run else mode


def _resolve_write_policy(
    *,
    write_policy: str | None,
    mode: str | None,
    dry_run: bool | None,
) -> tuple[str, str, bool, str | None]:
    if write_policy is None:
        resolved_mode = (mode or "replace").strip().lower()
        resolved_dry_run = bool(dry_run) if dry_run is not None else False
        return _policy_from_mode(resolved_mode, resolved_dry_run), resolved_mode, resolved_dry_run, None

    resolved_policy = str(write_policy).strip().lower()
    policy_mapping = BLOCK_SYNC_WRITE_POLICIES.get(resolved_policy)
    if policy_mapping is None:
        fallback_mode = (mode or "replace").strip().lower()
        fallback_dry_run = bool(dry_run) if dry_run is not None else False
        return resolved_policy, fallback_mode, fallback_dry_run, f"unsupported block sync write_policy: {write_policy}"

    policy_mode, policy_dry_run = policy_mapping
    explicit_mode = mode.strip().lower() if isinstance(mode, str) and mode.strip() else None
    if explicit_mode is not None and explicit_mode != policy_mode:
        return resolved_policy, policy_mode, policy_dry_run, (
            f"write_policy {resolved_policy} conflicts with mode {explicit_mode}"
        )
    if dry_run is not None and bool(dry_run) != policy_dry_run:
        return resolved_policy, policy_mode, policy_dry_run, (
            f"write_policy {resolved_policy} conflicts with dry_run {bool(dry_run)}"
        )
    return resolved_policy, policy_mode, policy_dry_run, None


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


def _find_prior_sync_by_key(mutation_key: str, audit_dir: Path) -> dict[str, Any] | None:
    for payload in _iter_audit_payloads(audit_dir):
        if payload.get("mutation_key") == mutation_key:
            return payload
    return None


def _normalize_observed_sync_state(observed_state: dict[str, Any] | None) -> dict[str, Any]:
    payload = dict(observed_state or {})
    payload["exists"] = bool(payload.get("exists", False))
    payload["stocks"] = _normalize_stock_list(payload.get("stocks"))
    payload["stock_count"] = len(payload["stocks"])
    if payload.get("block_name") is not None:
        payload["block_name"] = str(payload.get("block_name"))
    return payload


def _write_audit_log(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _build_sync_summary(
    *,
    block_code: str,
    mode: str,
    create_if_missing: bool,
    dry_run: bool,
    show: bool,
    status: str,
    governance_decision: str,
    governance_reason: str,
    created_block: bool,
    would_create_block: bool,
    added_symbols: list[str],
    removed_symbols: list[str],
    unchanged_symbols: list[str],
    desired_symbols: list[str],
    observed_symbols: list[str],
    write_policy: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": BLOCK_SYNC_SCHEMA_VERSION,
        "block_code": block_code,
        "write_policy": write_policy or _policy_from_mode(mode, dry_run),
        "mode": mode,
        "create_if_missing": create_if_missing,
        "dry_run": dry_run,
        "show": show,
        "status": status,
        "governance_decision": governance_decision,
        "governance_reason": governance_reason,
        "created_block": created_block,
        "would_create_block": would_create_block,
        "added_symbols": added_symbols,
        "removed_symbols": removed_symbols,
        "unchanged_symbols": unchanged_symbols,
        "desired_symbols": desired_symbols,
        "observed_symbols": observed_symbols,
    }


def _finalize_sync_result(
    result: Result,
    *,
    sync_id: str,
    mutation_key: str | None,
    audit_dir: Path,
    normalized_request: dict[str, Any],
    observed_state: dict[str, Any],
    sync_summary: dict[str, Any],
    underlying_artifacts: list[dict[str, Any]] | None = None,
    stage_results: list[Result] | None = None,
) -> Result:
    recorded_at = utc_now()
    payload = {
        "schema_version": BLOCK_SYNC_SCHEMA_VERSION,
        "recorded_at": format_rfc3339(recorded_at),
        "sync_id": sync_id,
        "mutation_key": mutation_key,
        "normalized_request": normalized_request,
        "observed_state": observed_state,
        "sync": sync_summary,
        "result": result.to_dict(),
    }
    timestamp = recorded_at.strftime("%Y%m%dT%H%M%S%fZ")
    audit_log_path = _write_audit_log(
        audit_dir / f"{timestamp}-block-sync-{_sanitize_filename_component(sync_summary['block_code'])}-{sync_id[:8]}.json",
        payload,
    )
    result.data["sync"] = sync_summary
    preserved_mutations: list[dict[str, Any]] = []
    for stage_result in stage_results or []:
        stage_mutation = stage_result.data.get("block_mutation")
        if isinstance(stage_mutation, dict):
            preserved_mutations.append(copy.deepcopy(stage_mutation))
    if preserved_mutations:
        result.data["block_mutation"] = copy.deepcopy(preserved_mutations[-1])
        if len(preserved_mutations) > 1:
            result.data["block_mutation_stages"] = preserved_mutations
    artifacts = result.data.get("artifacts")
    if not isinstance(artifacts, dict):
        artifacts = {}
        result.data["artifacts"] = artifacts
    artifacts["audit_log_path"] = str(audit_log_path)
    provider_artifacts = [{"kind": "block_sync_audit", "path": str(audit_log_path)}]
    if underlying_artifacts:
        provider_artifacts.extend(underlying_artifacts)
    result._provider_artifacts = provider_artifacts
    return result


def sync_watchlist_to_block(
    *,
    block_code: str,
    symbols: list[str],
    mode: str | None = None,
    create_if_missing: bool = False,
    dry_run: bool | None = None,
    show: bool = True,
    write_policy: str | None = None,
    mutation_key: str | None = None,
    observed_state: dict[str, Any] | Result | Callable[[], dict[str, Any] | Result],
    create_block: Callable[[], Result] | None,
    sync_members: Callable[[list[str], bool], Result],
    audit_dir: str | None = None,
) -> Result:
    sync_id = uuid4().hex
    resolved_audit_dir = _resolve_block_sync_audit_dir(audit_dir)
    resolved_write_policy, resolved_mode, resolved_dry_run, policy_error = _resolve_write_policy(
        write_policy=write_policy,
        mode=mode,
        dry_run=dry_run,
    )
    normalized_request = _canonical_sync_request(
        block_code=block_code,
        symbols=symbols,
        mode=resolved_mode,
        create_if_missing=create_if_missing,
        dry_run=resolved_dry_run,
        show=show,
        write_policy=resolved_write_policy,
    )
    desired_input_symbols = normalized_request["symbols"]

    if policy_error is not None:
        invalid_result = Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message=policy_error,
            data={},
        )
        return _finalize_sync_result(
            invalid_result,
            sync_id=sync_id,
            mutation_key=mutation_key,
            audit_dir=resolved_audit_dir,
            normalized_request=normalized_request,
            observed_state={"block_code": block_code, "exists": False, "stocks": []},
            sync_summary=_build_sync_summary(
                block_code=block_code,
                mode=resolved_mode,
                create_if_missing=create_if_missing,
                dry_run=resolved_dry_run,
                show=show,
                status="rejected",
                governance_decision="reject",
                governance_reason="invalid_write_policy",
                created_block=False,
                would_create_block=False,
                added_symbols=[],
                removed_symbols=[],
                unchanged_symbols=[],
                desired_symbols=desired_input_symbols,
                observed_symbols=[],
                write_policy=resolved_write_policy,
            ),
        )

    if resolved_mode not in {"replace", "merge"}:
        invalid_result = Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message=f"unsupported block sync mode: {resolved_mode}",
            data={},
        )
        return _finalize_sync_result(
            invalid_result,
            sync_id=sync_id,
            mutation_key=mutation_key,
            audit_dir=resolved_audit_dir,
            normalized_request=normalized_request,
            observed_state={"block_code": block_code, "exists": False, "stocks": []},
            sync_summary=_build_sync_summary(
                block_code=block_code,
                mode=resolved_mode,
                create_if_missing=create_if_missing,
                dry_run=resolved_dry_run,
                show=show,
                status="rejected",
                governance_decision="reject",
                governance_reason="unsupported_mode",
                created_block=False,
                would_create_block=False,
                added_symbols=[],
                removed_symbols=[],
                unchanged_symbols=[],
                desired_symbols=[],
                observed_symbols=[],
                write_policy=resolved_write_policy,
            ),
        )

    if not desired_input_symbols:
        invalid_result = Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="block sync requires at least one normalized symbol",
            data={},
        )
        return _finalize_sync_result(
            invalid_result,
            sync_id=sync_id,
            mutation_key=mutation_key,
            audit_dir=resolved_audit_dir,
            normalized_request=normalized_request,
            observed_state={"block_code": block_code, "exists": False, "stocks": []},
            sync_summary=_build_sync_summary(
                block_code=block_code,
                mode=resolved_mode,
                create_if_missing=create_if_missing,
                dry_run=resolved_dry_run,
                show=show,
                status="rejected",
                governance_decision="reject",
                governance_reason="empty_symbols",
                created_block=False,
                would_create_block=False,
                added_symbols=[],
                removed_symbols=[],
                unchanged_symbols=[],
                desired_symbols=[],
                observed_symbols=[],
                write_policy=resolved_write_policy,
            ),
        )

    if mutation_key is not None:
        prior_payload = _find_prior_sync_by_key(mutation_key, resolved_audit_dir)
        if prior_payload is not None:
            prior_request = prior_payload.get("normalized_request")
            if prior_request == normalized_request:
                replay_result = Result(ok=True, code=ErrorCode.OK, message="skipped duplicate block sync replay", data={})
                replay_result.data["mutation_key_replay"] = {
                    "mutation_key": mutation_key,
                    "replayed": True,
                    "prior_sync_id": prior_payload.get("sync_id"),
                    "prior_request": copy.deepcopy(prior_request) if isinstance(prior_request, dict) else prior_request,
                }
                return _finalize_sync_result(
                    replay_result,
                    sync_id=sync_id,
                    mutation_key=mutation_key,
                    audit_dir=resolved_audit_dir,
                    normalized_request=normalized_request,
                    observed_state={"source": "mutation_key_history"},
                    sync_summary=_build_sync_summary(
                        block_code=block_code,
                        mode=resolved_mode,
                        create_if_missing=create_if_missing,
                        dry_run=resolved_dry_run,
                        show=show,
                        status="noop",
                        governance_decision="skip",
                        governance_reason="mutation_key_replay",
                        created_block=False,
                        would_create_block=False,
                        added_symbols=[],
                        removed_symbols=[],
                        unchanged_symbols=[],
                        desired_symbols=desired_input_symbols,
                        observed_symbols=[],
                        write_policy=resolved_write_policy,
                    ),
                )
            conflict_result = Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message=f"mutation_key {mutation_key} conflicts with a different prior block sync request",
                data={
                    "mutation_key_conflict": {
                        "mutation_key": mutation_key,
                        "prior_sync_id": prior_payload.get("sync_id"),
                        "prior_request": copy.deepcopy(prior_request) if isinstance(prior_request, dict) else prior_request,
                        "current_request": copy.deepcopy(normalized_request),
                    }
                },
                next_action="Use a new mutation_key for a different block sync request.",
            )
            return _finalize_sync_result(
                conflict_result,
                sync_id=sync_id,
                mutation_key=mutation_key,
                audit_dir=resolved_audit_dir,
                normalized_request=normalized_request,
                observed_state={"source": "mutation_key_history"},
                sync_summary=_build_sync_summary(
                    block_code=block_code,
                    mode=resolved_mode,
                    create_if_missing=create_if_missing,
                    dry_run=resolved_dry_run,
                    show=show,
                    status="rejected",
                    governance_decision="reject",
                    governance_reason="mutation_key_conflict",
                    created_block=False,
                    would_create_block=False,
                    added_symbols=[],
                    removed_symbols=[],
                    unchanged_symbols=[],
                    desired_symbols=desired_input_symbols,
                    observed_symbols=[],
                    write_policy=resolved_write_policy,
                ),
            )

    resolved_observed_state = observed_state() if callable(observed_state) else observed_state
    if isinstance(resolved_observed_state, Result):
        failure_result = Result(
            ok=False,
            code=resolved_observed_state.code,
            message="block sync state probe failed",
            data={"state_probe_result": resolved_observed_state.to_dict()},
            warnings=list(resolved_observed_state.warnings),
            next_action=resolved_observed_state.next_action,
        )
        return _finalize_sync_result(
            failure_result,
            sync_id=sync_id,
            mutation_key=mutation_key,
            audit_dir=resolved_audit_dir,
            normalized_request=normalized_request,
            observed_state={"source": "state_probe", "available": False},
            sync_summary=_build_sync_summary(
                block_code=block_code,
                mode=resolved_mode,
                create_if_missing=create_if_missing,
                dry_run=resolved_dry_run,
                show=show,
                status="failed",
                governance_decision="reject",
                governance_reason="state_probe_failed",
                created_block=False,
                would_create_block=False,
                added_symbols=[],
                removed_symbols=[],
                unchanged_symbols=[],
                desired_symbols=[],
                observed_symbols=[],
                write_policy=resolved_write_policy,
            ),
        )

    normalized_observed_state = _normalize_observed_sync_state(resolved_observed_state)
    observed_symbols = normalized_observed_state["stocks"]
    exists = bool(normalized_observed_state.get("exists", False))
    would_create_block = not exists and create_if_missing

    if resolved_mode == "replace":
        desired_symbols = desired_input_symbols
    else:
        desired_symbols = _normalize_stock_list([*observed_symbols, *desired_input_symbols])

    observed_set = set(observed_symbols)
    desired_set = set(desired_symbols)
    added_symbols = sorted(desired_set - observed_set)
    removed_symbols = sorted(observed_set - desired_set) if resolved_mode == "replace" else []
    unchanged_symbols = sorted(observed_set & desired_set)

    if not exists and not create_if_missing:
        rejected_result = Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message=f"rejected block sync because target block {block_code} does not exist",
            data={},
            next_action="Create the block first or set create_if_missing=true.",
        )
        return _finalize_sync_result(
            rejected_result,
            sync_id=sync_id,
            mutation_key=mutation_key,
            audit_dir=resolved_audit_dir,
            normalized_request=normalized_request,
            observed_state=normalized_observed_state,
            sync_summary=_build_sync_summary(
                block_code=block_code,
                mode=resolved_mode,
                create_if_missing=create_if_missing,
                dry_run=resolved_dry_run,
                show=show,
                status="rejected",
                governance_decision="reject",
                governance_reason="missing_block",
                created_block=False,
                would_create_block=False,
                added_symbols=added_symbols,
                removed_symbols=removed_symbols,
                unchanged_symbols=unchanged_symbols,
                desired_symbols=desired_symbols,
                observed_symbols=observed_symbols,
                write_policy=resolved_write_policy,
            ),
        )

    if exists and desired_symbols == observed_symbols:
        noop_result = Result(ok=True, code=ErrorCode.OK, message="block sync already applied", data={})
        return _finalize_sync_result(
            noop_result,
            sync_id=sync_id,
            mutation_key=mutation_key,
            audit_dir=resolved_audit_dir,
            normalized_request=normalized_request,
            observed_state=normalized_observed_state,
            sync_summary=_build_sync_summary(
                block_code=block_code,
                mode=resolved_mode,
                create_if_missing=create_if_missing,
                dry_run=resolved_dry_run,
                show=show,
                status="noop",
                governance_decision="skip",
                governance_reason="already_applied",
                created_block=False,
                would_create_block=False,
                added_symbols=[],
                removed_symbols=[],
                unchanged_symbols=unchanged_symbols,
                desired_symbols=desired_symbols,
                observed_symbols=observed_symbols,
                write_policy=resolved_write_policy,
            ),
        )

    if resolved_dry_run:
        plan_result = Result(ok=True, code=ErrorCode.OK, message="planned block sync", data={})
        return _finalize_sync_result(
            plan_result,
            sync_id=sync_id,
            mutation_key=mutation_key,
            audit_dir=resolved_audit_dir,
            normalized_request=normalized_request,
            observed_state=normalized_observed_state,
            sync_summary=_build_sync_summary(
                block_code=block_code,
                mode=resolved_mode,
                create_if_missing=create_if_missing,
                dry_run=True,
                show=show,
                status="applied",
                governance_decision="execute",
                governance_reason="state_diff_detected" if exists else "missing_block",
                created_block=False,
                would_create_block=would_create_block,
                added_symbols=added_symbols,
                removed_symbols=removed_symbols,
                unchanged_symbols=unchanged_symbols,
                desired_symbols=desired_symbols,
                observed_symbols=observed_symbols,
                write_policy=resolved_write_policy,
            ),
        )

    created_block = False
    underlying_artifacts: list[dict[str, Any]] = []
    stage_results: list[Result] = []
    if would_create_block:
        if create_block is None:
            create_result = Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message="create_if_missing requires a create_block callback",
                data={},
            )
            return _finalize_sync_result(
                create_result,
                sync_id=sync_id,
                mutation_key=mutation_key,
                audit_dir=resolved_audit_dir,
                normalized_request=normalized_request,
                observed_state=normalized_observed_state,
                sync_summary=_build_sync_summary(
                    block_code=block_code,
                    mode=resolved_mode,
                    create_if_missing=create_if_missing,
                    dry_run=False,
                    show=show,
                    status="failed",
                    governance_decision="reject",
                    governance_reason="missing_create_callback",
                    created_block=False,
                    would_create_block=True,
                    added_symbols=added_symbols,
                    removed_symbols=removed_symbols,
                    unchanged_symbols=unchanged_symbols,
                    desired_symbols=desired_symbols,
                    observed_symbols=observed_symbols,
                    write_policy=resolved_write_policy,
                ),
            )
        create_result = create_block()
        stage_results.append(create_result)
        underlying_artifacts.extend(list(create_result._provider_artifacts or []))
        if not create_result.ok:
            return _finalize_sync_result(
                create_result,
                sync_id=sync_id,
                mutation_key=mutation_key,
                audit_dir=resolved_audit_dir,
                normalized_request=normalized_request,
                observed_state=normalized_observed_state,
                sync_summary=_build_sync_summary(
                    block_code=block_code,
                    mode=resolved_mode,
                    create_if_missing=create_if_missing,
                    dry_run=False,
                    show=show,
                    status="failed",
                    governance_decision="execute",
                    governance_reason="missing_block",
                    created_block=False,
                    would_create_block=True,
                    added_symbols=added_symbols,
                    removed_symbols=removed_symbols,
                    unchanged_symbols=unchanged_symbols,
                    desired_symbols=desired_symbols,
                    observed_symbols=observed_symbols,
                    write_policy=resolved_write_policy,
                ),
                underlying_artifacts=underlying_artifacts,
                stage_results=stage_results,
            )
        created_block = True

    sync_result = sync_members(desired_symbols, show)
    stage_results.append(sync_result)
    underlying_artifacts.extend(list(sync_result._provider_artifacts or []))
    return _finalize_sync_result(
        sync_result,
        sync_id=sync_id,
        mutation_key=mutation_key,
        audit_dir=resolved_audit_dir,
        normalized_request=normalized_request,
        observed_state=normalized_observed_state,
        sync_summary=_build_sync_summary(
            block_code=block_code,
            mode=resolved_mode,
            create_if_missing=create_if_missing,
            dry_run=False,
            show=show,
            status="applied" if sync_result.ok else "failed",
            governance_decision="execute",
            governance_reason="state_diff_detected" if exists else "missing_block",
            created_block=created_block,
            would_create_block=False,
            added_symbols=added_symbols,
            removed_symbols=removed_symbols,
            unchanged_symbols=unchanged_symbols,
            desired_symbols=desired_symbols,
            observed_symbols=observed_symbols,
            write_policy=resolved_write_policy,
        ),
        underlying_artifacts=underlying_artifacts,
        stage_results=stage_results,
    )
