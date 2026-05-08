from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SUBSCRIPTION_WATCH_SCHEMA_VERSION = "2026-05-01"
SUBSCRIPTION_WATCH_CAPABILITY = "subscription.watch"
SUBSCRIPTION_WATCH_CAPABILITY_VERSION = "1"


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_subscription_watch_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


@dataclass(frozen=True)
class SubscriptionWatchRunPaths:
    run_id: str
    run_dir: Path
    manifest_path: Path
    status_path: Path
    summary_path: Path
    events_jsonl_path: Path
    events_csv_path: Path
    runner_log_path: Path


def build_subscription_watch_run_paths(root_dir: Path, *, run_id: str | None = None) -> SubscriptionWatchRunPaths:
    resolved_run_id = run_id or build_subscription_watch_run_id()
    run_dir = root_dir / resolved_run_id
    return SubscriptionWatchRunPaths(
        run_id=resolved_run_id,
        run_dir=run_dir,
        manifest_path=run_dir / "manifest.json",
        status_path=run_dir / "status.json",
        summary_path=run_dir / "summary.json",
        events_jsonl_path=run_dir / "events.jsonl",
        events_csv_path=run_dir / "events.csv",
        runner_log_path=run_dir / "runner.log",
    )


def build_subscription_watch_manifest(
    *,
    paths: SubscriptionWatchRunPaths,
    provider: str,
    provider_mode: str,
    requested_symbols: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": SUBSCRIPTION_WATCH_SCHEMA_VERSION,
        "capability": SUBSCRIPTION_WATCH_CAPABILITY,
        "capability_version": SUBSCRIPTION_WATCH_CAPABILITY_VERSION,
        "run_id": paths.run_id,
        "created_at": now_utc_iso(),
        "provider": provider,
        "provider_mode": provider_mode,
        "requested_symbols": list(requested_symbols),
        "output_dir": str(paths.run_dir),
        "artifacts": {
            "manifest_path": str(paths.manifest_path),
            "status_path": str(paths.status_path),
            "summary_path": str(paths.summary_path),
            "events_jsonl_path": str(paths.events_jsonl_path),
            "events_csv_path": str(paths.events_csv_path),
        },
    }


def build_subscription_watch_status_payload(
    *,
    paths: SubscriptionWatchRunPaths,
    state: str,
    started_at: str,
    updated_at: str,
    session_id: str | None,
    event_count: int,
    last_sequence: int,
    last_event_ts: str | None,
    last_symbol: str | None,
    warnings: list[str],
    heartbeat_at: str | None = None,
    last_source_ts: str | None = None,
    reconnect_count: int = 0,
    consecutive_reconnect_failures: int = 0,
    last_disconnect_at: str | None = None,
    last_reconnect_at: str | None = None,
    next_reconnect_at: str | None = None,
    degraded_since: str | None = None,
    last_error: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SUBSCRIPTION_WATCH_SCHEMA_VERSION,
        "capability": SUBSCRIPTION_WATCH_CAPABILITY,
        "run_id": paths.run_id,
        "state": state,
        "started_at": started_at,
        "updated_at": updated_at,
        "session_id": session_id,
        "event_count": event_count,
        "last_sequence": last_sequence,
        "last_event_ts": last_event_ts,
        "last_symbol": last_symbol,
        "heartbeat_at": heartbeat_at,
        "last_source_ts": last_source_ts,
        "reconnect_count": reconnect_count,
        "consecutive_reconnect_failures": consecutive_reconnect_failures,
        "last_disconnect_at": last_disconnect_at,
        "last_reconnect_at": last_reconnect_at,
        "next_reconnect_at": next_reconnect_at,
        "degraded_since": degraded_since,
        "last_error": dict(last_error) if last_error is not None else None,
        "output_paths": {
            "run_dir": str(paths.run_dir),
            "manifest_path": str(paths.manifest_path),
            "status_path": str(paths.status_path),
            "summary_path": str(paths.summary_path),
            "events_jsonl_path": str(paths.events_jsonl_path),
            "events_csv_path": str(paths.events_csv_path),
        },
        "warnings": list(warnings),
    }


def build_subscription_watch_summary_payload(
    *,
    paths: SubscriptionWatchRunPaths,
    final_state: str,
    started_at: str,
    finished_at: str,
    elapsed_ms: float,
    session_id: str | None,
    event_count: int,
    symbol_count: int,
    stop_reason: str,
    warning_count: int,
    reconnect_count: int = 0,
    degraded_duration_ms: float = 0.0,
    final_last_error: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SUBSCRIPTION_WATCH_SCHEMA_VERSION,
        "capability": SUBSCRIPTION_WATCH_CAPABILITY,
        "run_id": paths.run_id,
        "final_state": final_state,
        "started_at": started_at,
        "finished_at": finished_at,
        "elapsed_ms": elapsed_ms,
        "event_count": event_count,
        "symbol_count": symbol_count,
        "session_id": session_id,
        "stop_reason": stop_reason,
        "warning_count": warning_count,
        "reconnect_count": reconnect_count,
        "degraded_duration_ms": degraded_duration_ms,
        "final_last_error": dict(final_last_error) if final_last_error is not None else None,
        "artifacts": {
            "manifest_path": str(paths.manifest_path),
            "status_path": str(paths.status_path),
            "summary_path": str(paths.summary_path),
            "events_jsonl_path": str(paths.events_jsonl_path),
            "events_csv_path": str(paths.events_csv_path),
        },
    }
