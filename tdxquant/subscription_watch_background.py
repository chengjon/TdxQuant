from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SubscriptionWatchBackgroundPaths:
    root_dir: Path
    active_path: Path
    pid_path: Path
    lock_path: Path


def build_background_paths(root_dir: Path) -> SubscriptionWatchBackgroundPaths:
    return SubscriptionWatchBackgroundPaths(
        root_dir=root_dir,
        active_path=root_dir / "active.json",
        pid_path=root_dir / "pid",
        lock_path=root_dir / "lock",
    )


def _pid_is_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _parse_pid(raw_pid: Any) -> int:
    try:
        return int(raw_pid or 0)
    except (TypeError, ValueError):
        return 0


def _cleanup_owned_state(paths: SubscriptionWatchBackgroundPaths) -> None:
    for owned_path in (paths.pid_path, paths.lock_path):
        if owned_path.exists():
            owned_path.unlink()


def _read_owned_pid(paths: SubscriptionWatchBackgroundPaths) -> int:
    if not paths.pid_path.exists():
        return 0
    return _parse_pid(paths.pid_path.read_text(encoding="utf-8").strip())


def _write_active_payload(paths: SubscriptionWatchBackgroundPaths, payload: dict[str, Any]) -> None:
    paths.active_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _normalize_terminal_payload(
    paths: SubscriptionWatchBackgroundPaths,
    payload: dict[str, Any],
    *,
    state: str,
    reason: str | None,
    run_id: Any = None,
) -> dict[str, Any]:
    normalized = dict(payload)
    normalized["state"] = state
    normalized["active"] = False
    normalized["pid"] = None
    normalized["reason"] = reason
    normalized["run_id"] = normalized.get("run_id", run_id)
    _write_active_payload(paths, normalized)
    _cleanup_owned_state(paths)
    return normalized


def reconcile_background_state(
    paths: SubscriptionWatchBackgroundPaths,
    *,
    pid_is_alive: Any = _pid_is_alive,
) -> dict[str, Any]:
    if not paths.active_path.exists():
        _cleanup_owned_state(paths)
        return {
            "state": "stopped",
            "active": False,
            "run_id": None,
            "pid": None,
            "reason": None,
        }

    try:
        raw_payload = json.loads(paths.active_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _normalize_terminal_payload(
            paths,
            {},
            state="failed",
            reason="stale_process_state",
        )

    if not isinstance(raw_payload, dict):
        return _normalize_terminal_payload(
            paths,
            {},
            state="failed",
            reason="stale_process_state",
        )

    payload = raw_payload
    state = str(payload.get("state") or "failed")
    payload_pid = _parse_pid(payload.get("pid"))
    owned_pid = _read_owned_pid(paths)
    pid_matches_owned_state = payload_pid > 0 and owned_pid == payload_pid

    if state in {"starting", "running", "stopping"} and (
        not pid_matches_owned_state or not pid_is_alive(payload_pid)
    ):
        return _normalize_terminal_payload(
            paths,
            payload,
            state="stopped" if state == "stopping" else "failed",
            reason="forced_stop" if state == "stopping" else "stale_process_state",
        )
    elif state in {"failed", "stopped", "completed"}:
        return _normalize_terminal_payload(
            paths,
            payload,
            state=state,
            reason=payload.get("reason"),
        )

    return payload
