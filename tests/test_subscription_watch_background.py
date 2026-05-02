from __future__ import annotations

import json
from pathlib import Path

from tdxquant.subscription_watch_background import (
    SubscriptionWatchBackgroundPaths,
    build_background_paths,
    reconcile_background_state,
)


def test_build_background_paths_uses_fixed_bridge_directory(tmp_path: Path) -> None:
    paths = build_background_paths(tmp_path)

    assert isinstance(paths, SubscriptionWatchBackgroundPaths)
    assert paths.root_dir == tmp_path
    assert paths.active_path == tmp_path / "active.json"
    assert paths.pid_path == tmp_path / "pid"
    assert paths.lock_path == tmp_path / "lock"


def test_reconcile_marks_missing_pid_as_failed(tmp_path: Path) -> None:
    paths = build_background_paths(tmp_path)
    paths.root_dir.mkdir(parents=True, exist_ok=True)
    paths.pid_path.write_text("12345\n", encoding="utf-8")
    paths.lock_path.write_text("locked\n", encoding="utf-8")
    paths.active_path.write_text(
        json.dumps(
            {
                "state": "running",
                "run_id": "run-001",
                "pid": 12345,
                "status_path": "runtime/subscription-watch/run-001/status.json",
            }
        ),
        encoding="utf-8",
    )

    reconciled = reconcile_background_state(paths, pid_is_alive=lambda pid: False)
    persisted = json.loads(paths.active_path.read_text(encoding="utf-8"))

    assert reconciled["state"] == "failed"
    assert reconciled["reason"] == "stale_process_state"
    assert persisted == reconciled
    assert not paths.pid_path.exists()
    assert not paths.lock_path.exists()


def test_reconcile_returns_stable_stopped_shape_when_no_active_state(tmp_path: Path) -> None:
    paths = build_background_paths(tmp_path)
    paths.root_dir.mkdir(parents=True, exist_ok=True)
    paths.pid_path.write_text("12345\n", encoding="utf-8")
    paths.lock_path.write_text("locked\n", encoding="utf-8")

    reconciled = reconcile_background_state(paths)

    assert reconciled == {
        "state": "stopped",
        "active": False,
        "run_id": None,
        "pid": None,
        "reason": None,
    }
    assert not paths.pid_path.exists()
    assert not paths.lock_path.exists()


def test_reconcile_malformed_pid_as_failed_terminal_payload(tmp_path: Path) -> None:
    paths = build_background_paths(tmp_path)
    paths.root_dir.mkdir(parents=True, exist_ok=True)
    paths.pid_path.write_text("abc\n", encoding="utf-8")
    paths.lock_path.write_text("locked\n", encoding="utf-8")
    paths.active_path.write_text(
        json.dumps(
            {
                "state": "running",
                "run_id": "run-002",
                "pid": "abc",
            }
        ),
        encoding="utf-8",
    )

    reconciled = reconcile_background_state(paths)
    persisted = json.loads(paths.active_path.read_text(encoding="utf-8"))

    assert reconciled["state"] == "failed"
    assert reconciled["reason"] == "stale_process_state"
    assert reconciled["pid"] is None
    assert reconciled["active"] is False
    assert persisted == reconciled
    assert not paths.pid_path.exists()
    assert not paths.lock_path.exists()


def test_reconcile_terminal_state_removes_stale_owned_files(tmp_path: Path) -> None:
    paths = build_background_paths(tmp_path)
    paths.root_dir.mkdir(parents=True, exist_ok=True)
    paths.pid_path.write_text("12345\n", encoding="utf-8")
    paths.lock_path.write_text("locked\n", encoding="utf-8")
    paths.active_path.write_text(
        json.dumps(
            {
                "state": "failed",
                "run_id": "run-003",
                "pid": None,
                "reason": "subscribe_failed",
                "active": False,
            }
        ),
        encoding="utf-8",
    )

    reconciled = reconcile_background_state(paths)

    assert reconciled["state"] == "failed"
    assert not paths.pid_path.exists()
    assert not paths.lock_path.exists()


def test_reconcile_missing_pid_file_as_failed_even_when_payload_pid_is_live(tmp_path: Path) -> None:
    paths = build_background_paths(tmp_path)
    paths.root_dir.mkdir(parents=True, exist_ok=True)
    paths.lock_path.write_text("locked\n", encoding="utf-8")
    paths.active_path.write_text(
        json.dumps(
            {
                "state": "running",
                "run_id": "run-004",
                "pid": 12345,
                "active": True,
            }
        ),
        encoding="utf-8",
    )

    reconciled = reconcile_background_state(paths, pid_is_alive=lambda pid: True)
    persisted = json.loads(paths.active_path.read_text(encoding="utf-8"))

    assert reconciled["state"] == "failed"
    assert reconciled["reason"] == "stale_process_state"
    assert reconciled["pid"] is None
    assert reconciled["active"] is False
    assert persisted == reconciled
    assert not paths.pid_path.exists()
    assert not paths.lock_path.exists()


def test_reconcile_mismatched_pid_file_as_failed_even_when_payload_pid_is_live(tmp_path: Path) -> None:
    paths = build_background_paths(tmp_path)
    paths.root_dir.mkdir(parents=True, exist_ok=True)
    paths.pid_path.write_text("99999\n", encoding="utf-8")
    paths.lock_path.write_text("locked\n", encoding="utf-8")
    paths.active_path.write_text(
        json.dumps(
            {
                "state": "running",
                "run_id": "run-005",
                "pid": 12345,
                "active": True,
            }
        ),
        encoding="utf-8",
    )

    reconciled = reconcile_background_state(paths, pid_is_alive=lambda pid: True)

    assert reconciled["state"] == "failed"
    assert reconciled["reason"] == "stale_process_state"
    assert reconciled["pid"] is None
    assert reconciled["active"] is False
    assert not paths.pid_path.exists()
    assert not paths.lock_path.exists()


def test_reconcile_completed_state_removes_stale_owned_files(tmp_path: Path) -> None:
    paths = build_background_paths(tmp_path)
    paths.root_dir.mkdir(parents=True, exist_ok=True)
    paths.pid_path.write_text("12345\n", encoding="utf-8")
    paths.lock_path.write_text("locked\n", encoding="utf-8")
    paths.active_path.write_text(
        json.dumps(
            {
                "state": "completed",
                "run_id": "run-006",
                "pid": None,
                "reason": "completed",
                "active": False,
            }
        ),
        encoding="utf-8",
    )

    reconciled = reconcile_background_state(paths)

    assert reconciled["state"] == "completed"
    assert not paths.pid_path.exists()
    assert not paths.lock_path.exists()


def test_reconcile_invalid_json_as_failed_terminal_payload(tmp_path: Path) -> None:
    paths = build_background_paths(tmp_path)
    paths.root_dir.mkdir(parents=True, exist_ok=True)
    paths.pid_path.write_text("12345\n", encoding="utf-8")
    paths.lock_path.write_text("locked\n", encoding="utf-8")
    paths.active_path.write_text("{not-json", encoding="utf-8")

    reconciled = reconcile_background_state(paths)
    persisted = json.loads(paths.active_path.read_text(encoding="utf-8"))

    assert reconciled["state"] == "failed"
    assert reconciled["reason"] == "stale_process_state"
    assert reconciled["active"] is False
    assert reconciled["pid"] is None
    assert persisted == reconciled
    assert not paths.pid_path.exists()
    assert not paths.lock_path.exists()


def test_reconcile_non_object_payload_as_failed_terminal_payload(tmp_path: Path) -> None:
    paths = build_background_paths(tmp_path)
    paths.root_dir.mkdir(parents=True, exist_ok=True)
    paths.pid_path.write_text("12345\n", encoding="utf-8")
    paths.lock_path.write_text("locked\n", encoding="utf-8")
    paths.active_path.write_text(json.dumps(["bad-payload"]), encoding="utf-8")

    reconciled = reconcile_background_state(paths)
    persisted = json.loads(paths.active_path.read_text(encoding="utf-8"))

    assert reconciled["state"] == "failed"
    assert reconciled["reason"] == "stale_process_state"
    assert reconciled["active"] is False
    assert reconciled["pid"] is None
    assert persisted == reconciled
    assert not paths.pid_path.exists()
    assert not paths.lock_path.exists()


def test_reconcile_terminal_state_normalizes_contradictory_payload_fields(tmp_path: Path) -> None:
    paths = build_background_paths(tmp_path)
    paths.root_dir.mkdir(parents=True, exist_ok=True)
    paths.pid_path.write_text("12345\n", encoding="utf-8")
    paths.lock_path.write_text("locked\n", encoding="utf-8")
    paths.active_path.write_text(
        json.dumps(
            {
                "state": "completed",
                "run_id": "run-007",
                "pid": 12345,
                "reason": "completed",
                "active": True,
            }
        ),
        encoding="utf-8",
    )

    reconciled = reconcile_background_state(paths)
    persisted = json.loads(paths.active_path.read_text(encoding="utf-8"))

    assert reconciled["state"] == "completed"
    assert reconciled["active"] is False
    assert reconciled["pid"] is None
    assert persisted == reconciled
    assert not paths.pid_path.exists()
    assert not paths.lock_path.exists()


def test_reconcile_healthy_active_state_remains_unchanged(tmp_path: Path) -> None:
    paths = build_background_paths(tmp_path)
    paths.root_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "state": "running",
        "run_id": "run-008",
        "pid": 12345,
        "active": True,
    }
    paths.pid_path.write_text("12345\n", encoding="utf-8")
    paths.lock_path.write_text("locked\n", encoding="utf-8")
    paths.active_path.write_text(json.dumps(payload), encoding="utf-8")

    reconciled = reconcile_background_state(paths, pid_is_alive=lambda pid: True)
    persisted = json.loads(paths.active_path.read_text(encoding="utf-8"))

    assert reconciled == payload
    assert persisted == payload
    assert paths.pid_path.exists()
    assert paths.lock_path.exists()


def test_reconcile_stale_stopping_state_yields_stopped_with_forced_stop(tmp_path: Path) -> None:
    paths = build_background_paths(tmp_path)
    paths.root_dir.mkdir(parents=True, exist_ok=True)
    paths.pid_path.write_text("12345\n", encoding="utf-8")
    paths.lock_path.write_text("locked\n", encoding="utf-8")
    paths.active_path.write_text(
        json.dumps(
            {
                "state": "stopping",
                "run_id": "run-009",
                "pid": 12345,
                "active": True,
            }
        ),
        encoding="utf-8",
    )

    reconciled = reconcile_background_state(paths, pid_is_alive=lambda pid: False)
    persisted = json.loads(paths.active_path.read_text(encoding="utf-8"))

    assert reconciled["state"] == "stopped"
    assert reconciled["reason"] == "forced_stop"
    assert reconciled["active"] is False
    assert reconciled["pid"] is None
    assert persisted == reconciled
    assert not paths.pid_path.exists()
    assert not paths.lock_path.exists()
