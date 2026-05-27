from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from unittest.mock import Mock

import pytest

from tdxquant.subscription_watch_background import (
    SubscriptionWatchBackgroundController,
    SubscriptionWatchBackgroundPaths,
    build_background_paths,
    build_subscription_watch_status_summary,
    reconcile_background_state,
    read_active_payload,
    write_terminal_background_state,
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
    assert paths.lock_path.exists()


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
    assert paths.lock_path.exists()


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
    assert paths.lock_path.exists()


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
    assert paths.lock_path.exists()


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
    assert paths.lock_path.exists()


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
    assert paths.lock_path.exists()


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
    assert paths.lock_path.exists()


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
    assert paths.lock_path.exists()


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
    assert paths.lock_path.exists()


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
    assert paths.lock_path.exists()


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


def test_reconcile_stale_stopping_state_defaults_to_graceful_stop_reason(tmp_path: Path) -> None:
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
    assert reconciled["reason"] == "operator_stop"
    assert reconciled["active"] is False
    assert reconciled["pid"] is None
    assert persisted == reconciled
    assert not paths.pid_path.exists()
    assert paths.lock_path.exists()


@pytest.mark.parametrize("state", ["reconnecting", "degraded"])
def test_reconcile_marks_resilience_active_process_loss_as_failed(tmp_path: Path, state: str) -> None:
    paths = build_background_paths(tmp_path)
    paths.root_dir.mkdir(parents=True, exist_ok=True)
    paths.pid_path.write_text("12345\n", encoding="utf-8")
    paths.lock_path.write_text("locked\n", encoding="utf-8")
    paths.active_path.write_text(
        json.dumps(
            {
                "state": state,
                "run_id": "run-resilience",
                "pid": 12345,
                "active": True,
            }
        ),
        encoding="utf-8",
    )

    reconciled = reconcile_background_state(paths, pid_is_alive=lambda pid: False)
    persisted = json.loads(paths.active_path.read_text(encoding="utf-8"))

    assert reconciled["state"] == "failed"
    assert reconciled["reason"] == "stale_process_state"
    assert reconciled["active"] is False
    assert reconciled["pid"] is None
    assert persisted == reconciled
    assert not paths.pid_path.exists()
    assert paths.lock_path.exists()


def test_start_rejects_when_active_state_is_running(tmp_path: Path) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")
    pid = os.getpid()
    controller._write_active_state(
        {
            "state": "running",
            "run_id": "run-001",
            "pid": pid,
            "reason": None,
            "active": True,
        }
    )
    controller.paths.pid_path.write_text(f"{pid}\n", encoding="utf-8")
    controller.paths.lock_path.write_text("locked\n", encoding="utf-8")

    result = controller.start(stock_list=["600519.SH"])

    assert result["ok"] is False
    assert result["error"]["code"] == "ALREADY_RUNNING"
    assert result["error"]["details"]["run_id"] == "run-001"


@pytest.mark.parametrize("state", ["reconnecting", "degraded"])
def test_start_rejects_when_active_state_is_resilience_runtime_state(tmp_path: Path, state: str) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")
    pid = os.getpid()
    controller._write_active_state(
        {
            "state": state,
            "run_id": "run-active",
            "pid": pid,
            "reason": None,
            "active": True,
        }
    )
    controller.paths.pid_path.write_text(f"{pid}\n", encoding="utf-8")
    controller.paths.lock_path.write_text("locked\n", encoding="utf-8")

    result = controller.start(stock_list=["600519.SH"])

    assert result["ok"] is False
    assert result["error"]["code"] == "ALREADY_RUNNING"
    assert result["error"]["details"]["run_id"] == "run-active"


def test_start_replays_current_active_run_for_same_idempotency_key(tmp_path: Path) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")
    pid = os.getpid()
    controller._write_active_state(
        {
            "state": "running",
            "run_id": "run-001",
            "pid": pid,
            "reason": None,
            "active": True,
            "runner_log_path": str(tmp_path / "run-001" / "runner.log"),
            "idempotency_key": "idem-001",
        }
    )
    controller.paths.pid_path.write_text(f"{pid}\n", encoding="utf-8")
    controller.paths.lock_path.write_text("locked\n", encoding="utf-8")

    result = controller.start(stock_list=["600519.SH"], idempotency_key="idem-001")

    assert result["ok"] is True
    assert result["result"]["run_id"] == "run-001"
    assert result["result"]["state"] == "running"
    assert result["result"]["pid"] == pid
    assert result["result"]["replayed"] is True


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"stock_list": []}, "subscription watch task requires at least one stock code"),
        ({"stock_list": ["600519.SH"], "max_events": 0}, "subscription watch task requires max_events > 0"),
        ({"stock_list": ["600519.SH"], "max_seconds": 0.0}, "subscription watch task requires max_seconds > 0"),
        ({"stock_list": ["600519.SH"], "poll_interval": -0.1}, "subscription watch task requires poll_interval >= 0"),
    ],
)
def test_start_rejects_invalid_watch_request_before_spawn(
    tmp_path: Path, kwargs: dict[str, object], message: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")
    spawn_calls: list[dict[str, object]] = []
    monkeypatch.setattr(controller, "_spawn_runner_process", lambda **spawn_kwargs: spawn_calls.append(spawn_kwargs))

    result = controller.start(**kwargs)

    assert result["ok"] is False
    assert result["error"]["code"] == "INVALID_REQUEST"
    assert result["error"]["message"] == message
    assert spawn_calls == []


def test_start_returns_failure_when_runner_exits_during_startup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    controller = SubscriptionWatchBackgroundController(
        root_dir=tmp_path,
        python_executable="python",
        start_timeout_seconds=0.2,
    )

    class FakeProcess:
        pid = 4321

        def poll(self) -> int:
            return 1

    monkeypatch.setattr(controller, "_spawn_runner_process", lambda **kwargs: FakeProcess())
    monkeypatch.setattr("tdxquant.subscription_watch_background.time.sleep", lambda _: None)
    controller._pid_is_alive = Mock(return_value=False)

    result = controller.start(stock_list=["600519.SH"])
    persisted = json.loads(controller.paths.active_path.read_text(encoding="utf-8"))

    assert result["ok"] is False
    assert result["error"]["code"] == "START_FAILED"
    assert result["error"]["details"]["run_id"] == persisted["run_id"]
    assert persisted["state"] == "failed"
    assert persisted["reason"] == "start_failed"
    assert persisted["active"] is False


def test_start_returns_start_timeout_when_runner_never_leaves_starting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    controller = SubscriptionWatchBackgroundController(
        root_dir=tmp_path,
        python_executable="python",
        start_timeout_seconds=0.0,
    )

    class FakeProcess:
        pid = 4321

    monkeypatch.setattr(controller, "_spawn_runner_process", lambda **kwargs: FakeProcess())
    monkeypatch.setattr("tdxquant.subscription_watch_background.time.sleep", lambda _: None)
    controller._pid_is_alive = Mock(return_value=True)

    result = controller.start(stock_list=["600519.SH"])
    persisted = read_active_payload(controller.paths)

    assert result["ok"] is False
    assert result["error"]["code"] == "START_TIMEOUT"
    assert result["error"]["details"]["run_id"] == persisted["run_id"]
    assert result["error"]["details"]["state"] == "starting"
    assert persisted["state"] == "starting"
    assert persisted["active"] is True


def test_stop_returns_run_id_and_coherent_terminal_state_when_process_exits(tmp_path: Path) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")
    pid = os.getpid()
    controller._write_active_state(
        {
            "state": "running",
            "run_id": "run-001",
            "pid": pid,
            "reason": None,
            "active": True,
        }
    )
    controller.paths.pid_path.write_text(f"{pid}\n", encoding="utf-8")
    controller.paths.lock_path.write_text("locked\n", encoding="utf-8")
    controller._signal_process = Mock(return_value=True)
    controller._pid_is_alive = Mock(side_effect=[True, False, False])

    result = controller.stop(reason="operator_stop", grace_period_seconds=2)
    persisted = json.loads(controller.paths.active_path.read_text(encoding="utf-8"))

    assert result["ok"] is True
    assert result["result"]["run_id"] == "run-001"
    assert persisted["state"] == "stopped"
    assert persisted["reason"] == "operator_stop"
    assert persisted["active"] is False


def test_status_view_returns_explicit_empty_watch_status_when_no_run_is_active(tmp_path: Path) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")

    status_view = controller.status()

    assert status_view["control"]["state"] == "stopped"
    assert status_view["control"]["active"] is False
    assert status_view["watch_status"] is None
    assert status_view["status_summary"]["schema_version"] == "tdx.subscription_watch.status_summary.v1"
    assert status_view["status_summary"]["state"] == "stopped"
    assert status_view["status_summary"]["overall_status"] == "stopped"
    assert status_view["status_summary"]["heartbeat"]["status"] == "missing"
    assert status_view["status_summary"]["watermark"]["event_count"] == 0
    assert status_view["status_summary"]["reconnect"]["reconnect_count"] == 0


def test_status_summary_keeps_heartbeat_staleness_not_evaluated_without_threshold() -> None:
    summary = build_subscription_watch_status_summary(
        control={"state": "running", "active": True, "run_id": "run-001"},
        watch_status={"run_id": "run-001", "state": "running", "heartbeat_at": "2026-05-17T09:30:00+00:00"},
    )

    assert summary["heartbeat"] == {
        "status": "present",
        "heartbeat_at": "2026-05-17T09:30:00+00:00",
        "staleness": "not_evaluated",
    }


def test_status_summary_keeps_watermark_staleness_not_evaluated_without_threshold() -> None:
    summary = build_subscription_watch_status_summary(
        control={"state": "running", "active": True, "run_id": "run-001"},
        watch_status={
            "run_id": "run-001",
            "state": "running",
            "last_event_ts": "2026-05-17T09:30:00+00:00",
        },
    )

    assert summary["watermark"]["last_event_ts"] == "2026-05-17T09:30:00+00:00"
    assert summary["watermark"]["staleness"] == "not_evaluated"


def test_status_summary_keeps_reconnect_staleness_not_evaluated_without_threshold() -> None:
    summary = build_subscription_watch_status_summary(
        control={"state": "reconnecting", "active": True, "run_id": "run-001"},
        watch_status={
            "run_id": "run-001",
            "state": "reconnecting",
            "last_disconnect_at": "2026-05-17T09:30:00+00:00",
        },
    )

    assert summary["reconnect"]["last_disconnect_at"] == "2026-05-17T09:30:00+00:00"
    assert summary["reconnect"]["staleness"] == "not_evaluated"


@pytest.mark.parametrize(
    ("now_utc", "threshold", "expected_staleness", "expected_age"),
    [
        ("2026-05-17T09:31:30+00:00", 60, "stale", 90.0),
        ("2026-05-17T09:30:45+00:00", 60, "fresh", 45.0),
    ],
)
def test_status_summary_evaluates_heartbeat_staleness_when_threshold_is_explicit(
    now_utc: str,
    threshold: int,
    expected_staleness: str,
    expected_age: float,
) -> None:
    summary = build_subscription_watch_status_summary(
        control={"state": "running", "active": True, "run_id": "run-001"},
        watch_status={"run_id": "run-001", "state": "running", "heartbeat_at": "2026-05-17T09:30:00+00:00"},
        heartbeat_stale_after_seconds=threshold,
        now_utc=now_utc,
    )

    assert summary["heartbeat"] == {
        "status": "present",
        "heartbeat_at": "2026-05-17T09:30:00+00:00",
        "staleness": expected_staleness,
        "age_seconds": expected_age,
        "stale_after_seconds": float(threshold),
        "evaluated_at": now_utc,
    }


@pytest.mark.parametrize(
    ("now_utc", "threshold", "expected_staleness", "expected_age"),
    [
        ("2026-05-17T09:31:30+00:00", 60, "stale", 90.0),
        ("2026-05-17T09:30:45+00:00", 60, "fresh", 45.0),
    ],
)
def test_status_summary_evaluates_watermark_staleness_when_threshold_is_explicit(
    now_utc: str,
    threshold: int,
    expected_staleness: str,
    expected_age: float,
) -> None:
    summary = build_subscription_watch_status_summary(
        control={"state": "running", "active": True, "run_id": "run-001"},
        watch_status={
            "run_id": "run-001",
            "state": "running",
            "last_event_ts": "2026-05-17T09:30:00+00:00",
        },
        watermark_stale_after_seconds=threshold,
        now_utc=now_utc,
    )

    assert summary["watermark"]["staleness"] == expected_staleness
    assert summary["watermark"]["age_seconds"] == expected_age
    assert summary["watermark"]["stale_after_seconds"] == float(threshold)
    assert summary["watermark"]["evaluated_at"] == now_utc


@pytest.mark.parametrize(
    ("now_utc", "threshold", "expected_staleness", "expected_age"),
    [
        ("2026-05-17T09:31:30+00:00", 60, "stale", 90.0),
        ("2026-05-17T09:30:45+00:00", 60, "fresh", 45.0),
    ],
)
def test_status_summary_evaluates_reconnect_staleness_when_threshold_is_explicit(
    now_utc: str,
    threshold: int,
    expected_staleness: str,
    expected_age: float,
) -> None:
    summary = build_subscription_watch_status_summary(
        control={"state": "reconnecting", "active": True, "run_id": "run-001"},
        watch_status={
            "run_id": "run-001",
            "state": "reconnecting",
            "last_disconnect_at": "2026-05-17T09:30:00+00:00",
        },
        reconnect_stale_after_seconds=threshold,
        now_utc=now_utc,
    )

    assert summary["reconnect"]["staleness"] == expected_staleness
    assert summary["reconnect"]["age_seconds"] == expected_age
    assert summary["reconnect"]["age_source"] == "last_disconnect_at"
    assert summary["reconnect"]["stale_after_seconds"] == float(threshold)
    assert summary["reconnect"]["evaluated_at"] == now_utc


def test_status_summary_reconnect_staleness_is_not_applicable_outside_resilience_state() -> None:
    summary = build_subscription_watch_status_summary(
        control={"state": "running", "active": True, "run_id": "run-001"},
        watch_status={
            "run_id": "run-001",
            "state": "running",
            "last_disconnect_at": "2026-05-17T09:30:00+00:00",
        },
        reconnect_stale_after_seconds=60,
        now_utc="2026-05-17T09:31:30+00:00",
    )

    assert summary["reconnect"]["staleness"] == "not_applicable"
    assert summary["reconnect"]["stale_after_seconds"] == 60.0


def test_status_summary_governance_observes_without_stale_thresholds() -> None:
    summary = build_subscription_watch_status_summary(
        control={"state": "running", "active": True, "run_id": "run-001"},
        watch_status={
            "run_id": "run-001",
            "state": "running",
            "heartbeat_at": "2026-05-17T09:30:00+00:00",
            "last_event_ts": "2026-05-17T09:30:00+00:00",
        },
    )

    assert summary["governance"] == {
        "decision": "observe",
        "requires_manual_review": False,
        "reasons": [],
        "reason_count": 0,
        "reason_source_counts": {},
        "reason_source_key_count": 0,
        "reason_summary": {
            "count": 0,
            "primary_reason": None,
            "primary_source": None,
            "primary_reason_source": None,
            "source_counts": {},
            "source_key_count": 0,
            "reason_code_counts": {},
            "reason_code_key_count": 0,
        },
        "actions": [],
        "action_count": 0,
        "action_summary": {
            "count": 0,
            "primary_action": None,
            "primary_reason": None,
            "primary_reason_source": None,
            "primary_severity": "none",
            "severity": "none",
            "severity_counts": {},
            "severity_key_count": 0,
            "action_name_counts": {},
            "action_name_key_count": 0,
            "reason_source_counts": {},
            "reason_source_key_count": 0,
            "reason_code_counts": {},
            "reason_code_key_count": 0,
        },
        "evaluation_summary": {
            "evaluated_components": [],
            "primary_evaluated_component": None,
            "stale_components": [],
            "primary_stale_component": None,
            "has_stale_component": False,
            "fresh_components": [],
            "primary_fresh_component": None,
            "has_fresh_component": False,
            "not_evaluated_components": ["heartbeat", "watermark", "reconnect"],
            "primary_not_evaluated_component": "heartbeat",
            "has_not_evaluated_component": True,
            "all_components_evaluated": False,
            "evaluated_count": 0,
            "stale_count": 0,
            "fresh_count": 0,
            "not_evaluated_count": 3,
            "component_status_counts": {"not_evaluated": 3},
            "component_status_key_count": 1,
            "evaluated_status_counts": {},
            "evaluated_status_key_count": 0,
        },
        "staleness_evaluated": False,
        "boundary": "advisory_only; does_not_trigger_reconnect_backoff_restart_or_lifecycle_changes",
    }


@pytest.mark.parametrize("state", ["reconnecting", "degraded", "failed"])
def test_status_summary_governance_requests_manual_review_for_resilience_states(state: str) -> None:
    summary = build_subscription_watch_status_summary(
        control={"state": state, "active": True, "run_id": "run-001"},
        watch_status={"run_id": "run-001", "state": state},
    )

    assert summary["governance"]["decision"] == "manual_review"
    assert summary["governance"]["requires_manual_review"] is True
    assert summary["governance"]["staleness_evaluated"] is False
    assert summary["governance"]["reasons"] == [f"overall_status:{state}"]
    assert summary["governance"]["reason_count"] == 1
    assert summary["governance"]["reason_source_counts"] == {"overall_status": 1}
    assert summary["governance"]["reason_source_key_count"] == 1
    assert summary["governance"]["action_count"] == 1
    assert summary["governance"]["actions"] == [
        {
            "action": "review_subscription_watch_resilience",
            "reason": f"overall_status:{state}",
            "severity": "review",
            "description": f"Inspect subscription-watch long-run process health for {state} status.",
        }
    ]
    assert summary["governance"]["action_summary"] == {
        "count": 1,
        "primary_action": "review_subscription_watch_resilience",
        "primary_reason": f"overall_status:{state}",
        "primary_reason_source": "overall_status",
        "primary_severity": "review",
        "severity": "review",
        "severity_counts": {"review": 1},
        "severity_key_count": 1,
        "action_name_counts": {"review_subscription_watch_resilience": 1},
        "action_name_key_count": 1,
        "reason_source_counts": {"overall_status": 1},
        "reason_source_key_count": 1,
        "reason_code_counts": {f"overall_status:{state}": 1},
        "reason_code_key_count": 1,
    }


def test_status_summary_governance_requests_manual_review_for_explicit_stale_inputs() -> None:
    summary = build_subscription_watch_status_summary(
        control={"state": "running", "active": True, "run_id": "run-001"},
        watch_status={
            "run_id": "run-001",
            "state": "running",
            "heartbeat_at": "2026-05-17T09:30:00+00:00",
            "last_event_ts": "2026-05-17T09:30:00+00:00",
        },
        heartbeat_stale_after_seconds=60,
        watermark_stale_after_seconds=60,
        now_utc="2026-05-17T09:31:30+00:00",
    )

    assert summary["governance"]["decision"] == "manual_review"
    assert summary["governance"]["requires_manual_review"] is True
    assert summary["governance"]["staleness_evaluated"] is True
    assert summary["governance"]["reasons"] == ["heartbeat:stale", "watermark:stale"]
    assert summary["governance"]["reason_count"] == 2
    assert summary["governance"]["reason_source_counts"] == {"heartbeat": 1, "watermark": 1}
    assert summary["governance"]["reason_source_key_count"] == 2
    assert summary["governance"]["reason_summary"] == {
        "count": 2,
        "primary_reason": "heartbeat:stale",
        "primary_source": "heartbeat",
        "primary_reason_source": "heartbeat",
        "source_counts": {"heartbeat": 1, "watermark": 1},
        "source_key_count": 2,
        "reason_code_counts": {"heartbeat:stale": 1, "watermark:stale": 1},
        "reason_code_key_count": 2,
    }
    assert summary["governance"]["actions"] == [
        {
            "action": "review_subscription_watch_heartbeat",
            "reason": "heartbeat:stale",
            "severity": "review",
            "description": "Inspect heartbeat freshness before changing reconnect or restart behavior.",
        },
        {
            "action": "review_subscription_watch_watermark",
            "reason": "watermark:stale",
            "severity": "review",
            "description": "Inspect event watermark freshness before changing reconnect or restart behavior.",
        },
    ]
    assert summary["governance"]["action_count"] == 2
    assert summary["governance"]["action_summary"] == {
        "count": 2,
        "primary_action": "review_subscription_watch_heartbeat",
        "primary_reason": "heartbeat:stale",
        "primary_reason_source": "heartbeat",
        "primary_severity": "review",
        "severity": "review",
        "severity_counts": {"review": 2},
        "severity_key_count": 1,
        "action_name_counts": {
            "review_subscription_watch_heartbeat": 1,
            "review_subscription_watch_watermark": 1,
        },
        "action_name_key_count": 2,
        "reason_source_counts": {"heartbeat": 1, "watermark": 1},
        "reason_source_key_count": 2,
        "reason_code_counts": {"heartbeat:stale": 1, "watermark:stale": 1},
        "reason_code_key_count": 2,
    }
    assert summary["governance"]["evaluation_summary"] == {
        "evaluated_components": ["heartbeat", "watermark"],
        "primary_evaluated_component": "heartbeat",
        "stale_components": ["heartbeat", "watermark"],
        "primary_stale_component": "heartbeat",
        "has_stale_component": True,
        "fresh_components": [],
        "primary_fresh_component": None,
        "has_fresh_component": False,
        "not_evaluated_components": ["reconnect"],
        "primary_not_evaluated_component": "reconnect",
        "has_not_evaluated_component": True,
        "all_components_evaluated": False,
        "evaluated_count": 2,
        "stale_count": 2,
        "fresh_count": 0,
        "not_evaluated_count": 1,
        "component_status_counts": {"not_evaluated": 1, "stale": 2},
        "component_status_key_count": 2,
        "evaluated_status_counts": {"stale": 2},
        "evaluated_status_key_count": 1,
    }


def test_status_summary_evaluation_summary_lists_fresh_components() -> None:
    summary = build_subscription_watch_status_summary(
        control={"state": "running", "active": True, "run_id": "run-001"},
        watch_status={
            "run_id": "run-001",
            "state": "running",
            "heartbeat_at": "2026-05-17T09:31:00+00:00",
            "last_event_ts": "2026-05-17T09:30:00+00:00",
        },
        heartbeat_stale_after_seconds=60,
        watermark_stale_after_seconds=60,
        now_utc="2026-05-17T09:31:30+00:00",
    )

    assert summary["governance"]["evaluation_summary"] == {
        "evaluated_components": ["heartbeat", "watermark"],
        "primary_evaluated_component": "heartbeat",
        "stale_components": ["watermark"],
        "primary_stale_component": "watermark",
        "has_stale_component": True,
        "fresh_components": ["heartbeat"],
        "primary_fresh_component": "heartbeat",
        "has_fresh_component": True,
        "not_evaluated_components": ["reconnect"],
        "primary_not_evaluated_component": "reconnect",
        "has_not_evaluated_component": True,
        "all_components_evaluated": False,
        "evaluated_count": 2,
        "stale_count": 1,
        "fresh_count": 1,
        "not_evaluated_count": 1,
        "component_status_counts": {"fresh": 1, "not_evaluated": 1, "stale": 1},
        "component_status_key_count": 3,
        "evaluated_status_counts": {"fresh": 1, "stale": 1},
        "evaluated_status_key_count": 2,
    }


def test_status_summary_governance_requests_manual_review_for_stale_reconnect() -> None:
    summary = build_subscription_watch_status_summary(
        control={"state": "reconnecting", "active": True, "run_id": "run-001"},
        watch_status={
            "run_id": "run-001",
            "state": "reconnecting",
            "last_disconnect_at": "2026-05-17T09:30:00+00:00",
        },
        reconnect_stale_after_seconds=60,
        now_utc="2026-05-17T09:31:30+00:00",
    )

    assert summary["governance"]["decision"] == "manual_review"
    assert summary["governance"]["requires_manual_review"] is True
    assert summary["governance"]["staleness_evaluated"] is True
    assert summary["governance"]["reasons"] == ["overall_status:reconnecting", "reconnect:stale"]
    assert summary["governance"]["reason_count"] == len(summary["governance"]["reasons"])
    assert summary["governance"]["reason_source_counts"] == {"overall_status": 1, "reconnect": 1}
    assert summary["governance"]["reason_source_key_count"] == 2
    assert summary["governance"]["reason_summary"] == {
        "count": 2,
        "primary_reason": "overall_status:reconnecting",
        "primary_source": "overall_status",
        "primary_reason_source": "overall_status",
        "source_counts": {"overall_status": 1, "reconnect": 1},
        "source_key_count": 2,
        "reason_code_counts": {"overall_status:reconnecting": 1, "reconnect:stale": 1},
        "reason_code_key_count": 2,
    }
    assert summary["governance"]["actions"] == [
        {
            "action": "review_subscription_watch_resilience",
            "reason": "overall_status:reconnecting",
            "severity": "review",
            "description": "Inspect subscription-watch long-run process health for reconnecting status.",
        },
        {
            "action": "review_subscription_watch_reconnect",
            "reason": "reconnect:stale",
            "severity": "review",
            "description": "Inspect reconnect/degraded duration before changing reconnect or restart behavior.",
        },
    ]
    assert summary["governance"]["action_summary"] == {
        "count": 2,
        "primary_action": "review_subscription_watch_resilience",
        "primary_reason": "overall_status:reconnecting",
        "primary_reason_source": "overall_status",
        "primary_severity": "review",
        "severity": "review",
        "severity_counts": {"review": 2},
        "severity_key_count": 1,
        "action_name_counts": {
            "review_subscription_watch_reconnect": 1,
            "review_subscription_watch_resilience": 1,
        },
        "action_name_key_count": 2,
        "reason_source_counts": {"overall_status": 1, "reconnect": 1},
        "reason_source_key_count": 2,
        "reason_code_counts": {"overall_status:reconnecting": 1, "reconnect:stale": 1},
        "reason_code_key_count": 2,
    }
    assert summary["governance"]["evaluation_summary"] == {
        "evaluated_components": ["reconnect"],
        "primary_evaluated_component": "reconnect",
        "stale_components": ["reconnect"],
        "primary_stale_component": "reconnect",
        "has_stale_component": True,
        "fresh_components": [],
        "primary_fresh_component": None,
        "has_fresh_component": False,
        "not_evaluated_components": ["heartbeat", "watermark"],
        "primary_not_evaluated_component": "heartbeat",
        "has_not_evaluated_component": True,
        "all_components_evaluated": False,
        "evaluated_count": 1,
        "stale_count": 1,
        "fresh_count": 0,
        "not_evaluated_count": 2,
        "component_status_counts": {"not_evaluated": 2, "stale": 1},
        "component_status_key_count": 2,
        "evaluated_status_counts": {"stale": 1},
        "evaluated_status_key_count": 1,
    }


def test_status_summary_evaluation_summary_preserves_fresh_counts_when_reconnect_is_stale() -> None:
    summary = build_subscription_watch_status_summary(
        control={"state": "reconnecting", "active": True, "run_id": "run-001"},
        watch_status={
            "run_id": "run-001",
            "state": "reconnecting",
            "heartbeat_at": "2026-05-17T09:31:15+00:00",
            "last_event_ts": "2026-05-17T09:31:10+00:00",
            "last_disconnect_at": "2026-05-17T09:30:00+00:00",
        },
        heartbeat_stale_after_seconds=60,
        watermark_stale_after_seconds=60,
        reconnect_stale_after_seconds=60,
        now_utc="2026-05-17T09:31:30+00:00",
    )

    assert summary["governance"]["reasons"] == ["overall_status:reconnecting", "reconnect:stale"]
    assert summary["governance"]["evaluation_summary"] == {
        "evaluated_components": ["heartbeat", "watermark", "reconnect"],
        "primary_evaluated_component": "heartbeat",
        "stale_components": ["reconnect"],
        "primary_stale_component": "reconnect",
        "has_stale_component": True,
        "fresh_components": ["heartbeat", "watermark"],
        "primary_fresh_component": "heartbeat",
        "has_fresh_component": True,
        "not_evaluated_components": [],
        "primary_not_evaluated_component": None,
        "has_not_evaluated_component": False,
        "all_components_evaluated": True,
        "evaluated_count": 3,
        "stale_count": 1,
        "fresh_count": 2,
        "not_evaluated_count": 0,
        "component_status_counts": {"fresh": 2, "stale": 1},
        "component_status_key_count": 2,
        "evaluated_status_counts": {"fresh": 2, "stale": 1},
        "evaluated_status_key_count": 2,
    }
    assert summary["governance"]["action_summary"]["count"] == 2


def test_status_view_returns_active_control_and_current_run_status(tmp_path: Path) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")
    run_dir = tmp_path / "run-001"
    run_dir.mkdir(parents=True)
    pid = os.getpid()
    controller._write_active_state(
        {
            "state": "running",
            "run_id": "run-001",
            "pid": pid,
            "reason": None,
            "active": True,
        }
    )
    controller.paths.pid_path.write_text(f"{pid}\n", encoding="utf-8")
    controller.paths.lock_path.write_text("locked\n", encoding="utf-8")
    (run_dir / "status.json").write_text(
        json.dumps(
            {
                "run_id": "run-001",
                "state": "running",
                "event_count": 3,
                "unique_symbol_count": 2,
                "heartbeat_at": "2026-05-17T09:30:00+00:00",
                "last_sequence": 12,
                "last_event_ts": "2026-05-17T09:30:01+00:00",
                "last_symbol": "688318.SH",
            }
        ),
        encoding="utf-8",
    )

    status_view = controller.status()

    assert status_view["control"]["run_id"] == "run-001"
    assert status_view["watch_status"]["event_count"] == 3
    assert status_view["status_summary"]["state"] == "running"
    assert status_view["status_summary"]["overall_status"] == "active"
    assert status_view["status_summary"]["run_id"] == "run-001"
    assert status_view["status_summary"]["heartbeat"]["status"] == "present"
    assert status_view["status_summary"]["heartbeat"]["heartbeat_at"] == "2026-05-17T09:30:00+00:00"
    assert status_view["status_summary"]["watermark"] == {
        "event_count": 3,
        "unique_symbol_count": 2,
        "last_sequence": 12,
        "last_event_ts": "2026-05-17T09:30:01+00:00",
        "last_symbol": "688318.SH",
        "last_source_ts": None,
        "staleness": "not_evaluated",
    }
    assert status_view["status_summary"]["governance"]["decision"] == "observe"
    assert status_view["status_summary"]["governance"]["staleness_evaluated"] is False


def test_status_view_evaluates_heartbeat_staleness_when_threshold_is_passed(tmp_path: Path) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")
    run_dir = tmp_path / "run-001"
    run_dir.mkdir(parents=True)
    pid = os.getpid()
    controller._write_active_state(
        {
            "state": "running",
            "run_id": "run-001",
            "pid": pid,
            "reason": None,
            "active": True,
        }
    )
    controller.paths.pid_path.write_text(f"{pid}\n", encoding="utf-8")
    controller.paths.lock_path.write_text("locked\n", encoding="utf-8")
    (run_dir / "status.json").write_text(
        json.dumps(
            {
                "run_id": "run-001",
                "state": "running",
                "heartbeat_at": "2026-05-17T09:30:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    status_view = controller.status(
        heartbeat_stale_after_seconds=60,
        now_utc="2026-05-17T09:31:30+00:00",
    )

    assert status_view["status_summary"]["heartbeat"]["staleness"] == "stale"
    assert status_view["status_summary"]["heartbeat"]["age_seconds"] == 90.0
    assert status_view["watch_status"]["heartbeat_at"] == "2026-05-17T09:30:00+00:00"


def test_status_view_evaluates_watermark_staleness_with_explicit_threshold(tmp_path: Path) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")
    run_dir = tmp_path / "run-001"
    run_dir.mkdir(parents=True)
    pid = os.getpid()
    controller._write_active_state(
        {
            "state": "running",
            "run_id": "run-001",
            "pid": pid,
            "reason": None,
            "active": True,
        }
    )
    controller.paths.pid_path.write_text(f"{pid}\n", encoding="utf-8")
    controller.paths.lock_path.write_text("locked\n", encoding="utf-8")
    (run_dir / "status.json").write_text(
        json.dumps(
            {
                "run_id": "run-001",
                "state": "running",
                "last_event_ts": "2026-05-17T09:30:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    status_view = controller.status(
        watermark_stale_after_seconds=60,
        now_utc="2026-05-17T09:31:30+00:00",
    )

    assert status_view["status_summary"]["watermark"]["staleness"] == "stale"
    assert status_view["status_summary"]["watermark"]["age_seconds"] == 90.0
    assert status_view["watch_status"]["last_event_ts"] == "2026-05-17T09:30:00+00:00"


@pytest.mark.parametrize("state", ["reconnecting", "degraded"])
def test_status_view_summarizes_resilience_runtime_fields(tmp_path: Path, state: str) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")
    run_dir = tmp_path / "run-001"
    run_dir.mkdir(parents=True)
    pid = os.getpid()
    controller._write_active_state(
        {
            "state": state,
            "run_id": "run-001",
            "pid": pid,
            "reason": None,
            "active": True,
        }
    )
    controller.paths.pid_path.write_text(f"{pid}\n", encoding="utf-8")
    controller.paths.lock_path.write_text("locked\n", encoding="utf-8")
    (run_dir / "status.json").write_text(
        json.dumps(
            {
                "run_id": "run-001",
                "state": state,
                "event_count": 7,
                "heartbeat_at": "2026-05-17T09:30:00+00:00",
                "reconnect_count": 2,
                "last_disconnect_at": "2026-05-17T09:29:00+00:00",
                "last_reconnect_at": "2026-05-17T09:29:10+00:00",
                "next_reconnect_at": "2026-05-17T09:30:10+00:00",
                "degraded_since": "2026-05-17T09:29:30+00:00",
                "consecutive_reconnect_failures": 1,
                "last_error": {"code": "SESSION_LOST"},
            }
        ),
        encoding="utf-8",
    )

    status_view = controller.status()

    assert status_view["status_summary"]["overall_status"] == state
    assert status_view["status_summary"]["reconnect"] == {
        "reconnect_count": 2,
        "last_disconnect_at": "2026-05-17T09:29:00+00:00",
        "last_reconnect_at": "2026-05-17T09:29:10+00:00",
        "next_reconnect_at": "2026-05-17T09:30:10+00:00",
        "degraded_since": "2026-05-17T09:29:30+00:00",
        "consecutive_reconnect_failures": 1,
        "last_error": {"code": "SESSION_LOST"},
        "staleness": "not_evaluated",
    }


def test_list_view_returns_active_last_completed_and_last_failed(tmp_path: Path) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")
    active_run = tmp_path / "run-003"
    completed_run = tmp_path / "run-002"
    failed_run = tmp_path / "run-001"
    active_run.mkdir(parents=True)
    completed_run.mkdir(parents=True)
    failed_run.mkdir(parents=True)
    pid = os.getpid()
    controller._write_active_state(
        {
            "state": "running",
            "run_id": "run-003",
            "pid": pid,
            "reason": None,
            "active": True,
        }
    )
    controller.paths.pid_path.write_text(f"{pid}\n", encoding="utf-8")
    controller.paths.lock_path.write_text("locked\n", encoding="utf-8")
    (active_run / "status.json").write_text(
        json.dumps({"run_id": "run-003", "state": "running"}),
        encoding="utf-8",
    )
    (completed_run / "summary.json").write_text(
        json.dumps({"run_id": "run-002", "final_state": "completed"}),
        encoding="utf-8",
    )
    (failed_run / "summary.json").write_text(
        json.dumps({"run_id": "run-001", "final_state": "failed"}),
        encoding="utf-8",
    )

    list_view = controller.list_runs()

    assert list_view["active"]["run_id"] == "run-003"
    assert list_view["last_completed"]["run_id"] == "run-002"
    assert list_view["last_failed"]["run_id"] == "run-001"


def test_artifacts_view_returns_canonical_paths_for_explicit_run_id(tmp_path: Path) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")
    run_dir = tmp_path / "run-001"
    run_dir.mkdir(parents=True)

    artifacts_view = controller.artifacts(run_id="run-001")

    assert artifacts_view["run_id"] == "run-001"
    assert artifacts_view["artifacts"]["run_dir"] == str(run_dir)
    assert artifacts_view["artifacts"]["events_jsonl_path"] == str(run_dir / "events.jsonl")
    assert artifacts_view["artifacts"]["events_csv_path"] == str(run_dir / "events.csv")
    assert artifacts_view["artifacts"]["runner_log_path"] == str(run_dir / "runner.log")


def test_events_and_logs_views_tail_canonical_run_artifacts(tmp_path: Path) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")
    run_dir = tmp_path / "run-001"
    run_dir.mkdir(parents=True)
    (run_dir / "events.jsonl").write_text(
        "\n".join(
            [
                json.dumps({"sequence": 1, "symbol": "000001"}),
                json.dumps({"sequence": 2, "symbol": "000002"}),
                json.dumps({"sequence": 3, "symbol": "000003"}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (run_dir / "runner.log").write_text("line-1\nline-2\nline-3\n", encoding="utf-8")

    events_view = controller.events(run_id="run-001", tail=2)
    logs_view = controller.logs(run_id="run-001", tail=2)

    assert [row["sequence"] for row in events_view["events"]] == [2, 3]
    assert logs_view["lines"] == ["line-2", "line-3"]


def test_reconcile_stale_stopping_state_preserves_graceful_stop_reason(tmp_path: Path) -> None:
    paths = build_background_paths(tmp_path)
    paths.root_dir.mkdir(parents=True, exist_ok=True)
    paths.pid_path.write_text("12345\n", encoding="utf-8")
    paths.lock_path.write_text("locked\n", encoding="utf-8")
    paths.active_path.write_text(
        json.dumps(
            {
                "state": "stopping",
                "run_id": "run-008",
                "pid": 12345,
                "reason": "operator_stop",
                "active": True,
            }
        ),
        encoding="utf-8",
    )

    reconciled = reconcile_background_state(paths, pid_is_alive=lambda pid: False)
    persisted = json.loads(paths.active_path.read_text(encoding="utf-8"))

    assert reconciled["state"] == "stopped"
    assert reconciled["reason"] == "operator_stop"
    assert reconciled["active"] is False
    assert reconciled["pid"] is None
    assert persisted == reconciled
    assert not paths.pid_path.exists()


def test_start_rejects_when_control_lock_is_held_by_other_process(tmp_path: Path) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")
    tmp_path.mkdir(parents=True, exist_ok=True)
    lock_script = (
        "import fcntl, pathlib, sys, time; "
        "path = pathlib.Path(sys.argv[1]); "
        "path.parent.mkdir(parents=True, exist_ok=True); "
        "handle = path.open('a+', encoding='utf-8'); "
        "fcntl.flock(handle.fileno(), fcntl.LOCK_EX); "
        "print('ready', flush=True); "
        "time.sleep(10)"
    )
    proc = subprocess.Popen(
        [sys.executable, "-c", lock_script, str(controller.paths.lock_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        ready = proc.stdout.readline().strip()
        assert ready == "ready"

        result = controller.start(stock_list=["600519.SH"])

        assert result["ok"] is False
        assert result["error"]["code"] == "CONTROL_LOCKED"
    finally:
        proc.terminate()
        proc.wait(timeout=5)


def test_stop_returns_error_when_signal_delivery_fails(tmp_path: Path) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")
    pid = os.getpid()
    controller._write_active_state(
        {
            "state": "running",
            "run_id": "run-001",
            "pid": pid,
            "reason": None,
            "active": True,
        }
    )
    controller.paths.pid_path.write_text(f"{pid}\n", encoding="utf-8")
    controller.paths.lock_path.write_text("locked\n", encoding="utf-8")
    controller._signal_process = Mock(return_value=False)

    result = controller.stop(reason="operator_stop", grace_period_seconds=1)

    assert result["ok"] is False
    assert result["error"]["code"] == "SIGNAL_FAILED"


def test_stop_preserves_startup_failure_guard_when_signal_delivery_fails(tmp_path: Path) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")
    controller._write_active_state(
        {
            "state": "starting",
            "run_id": "run-guarded",
            "pid": 4321,
            "reason": "startup_persistence_failed",
            "active": True,
        }
    )
    controller.paths.lock_path.write_text("locked\n", encoding="utf-8")
    controller._signal_process = Mock(return_value=False)
    controller._pid_is_alive = Mock(return_value=True)

    result = controller.stop(reason="operator_stop", grace_period_seconds=1)
    persisted = json.loads(controller.paths.active_path.read_text(encoding="utf-8"))

    assert result["ok"] is False
    assert result["error"]["code"] == "SIGNAL_FAILED"
    assert persisted["state"] == "starting"
    assert persisted["reason"] == "startup_persistence_failed"
    assert persisted["active"] is True
    assert persisted["pid"] == 4321
    assert not controller.paths.pid_path.exists()


def test_stop_returns_success_when_process_exits_before_signal_delivery(tmp_path: Path) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")
    controller._write_active_state(
        {
            "state": "running",
            "run_id": "run-race",
            "pid": 4321,
            "reason": None,
            "active": True,
        }
    )
    controller.paths.pid_path.write_text("4321\n", encoding="utf-8")
    controller.paths.lock_path.write_text("locked\n", encoding="utf-8")
    controller._signal_process = Mock(return_value=False)
    controller._pid_is_alive = Mock(side_effect=[True, False, False])

    result = controller.stop(reason="operator_stop", grace_period_seconds=1)
    persisted = json.loads(controller.paths.active_path.read_text(encoding="utf-8"))

    assert result["ok"] is True
    assert result["result"]["run_id"] == "run-race"
    assert result["result"]["state"] == "stopped"
    assert persisted["state"] == "stopped"
    assert persisted["reason"] == "operator_stop"
    assert persisted["active"] is False
    assert not controller.paths.pid_path.exists()


def test_stop_does_not_overwrite_fast_runner_terminal_payload(tmp_path: Path) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")
    controller._write_active_state(
        {
            "state": "running",
            "run_id": "run-fast-exit",
            "pid": 4321,
            "reason": None,
            "active": True,
        }
    )
    controller.paths.pid_path.write_text("4321\n", encoding="utf-8")
    controller.paths.lock_path.write_text("locked\n", encoding="utf-8")

    def signal_and_simulate_runner_exit(pid: int, sig: int) -> bool:
        write_terminal_background_state(
            controller.paths,
            run_id="run-fast-exit",
            state="stopped",
            reason="keyboard_interrupt",
        )
        return True

    controller._signal_process = Mock(side_effect=signal_and_simulate_runner_exit)
    controller._pid_is_alive = Mock(side_effect=[True, False])

    result = controller.stop(reason="operator_stop", grace_period_seconds=1)
    persisted = json.loads(controller.paths.active_path.read_text(encoding="utf-8"))

    assert result["ok"] is True
    assert result["result"]["run_id"] == "run-fast-exit"
    assert result["result"]["state"] == "stopped"
    assert persisted["state"] == "stopped"
    assert persisted["reason"] == "keyboard_interrupt"
    assert persisted["active"] is False
    assert not controller.paths.pid_path.exists()


def test_stop_force_stops_when_grace_period_expires(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    controller = SubscriptionWatchBackgroundController(
        root_dir=tmp_path,
        python_executable="python",
        stop_force_kill_timeout_seconds=0.2,
    )
    pid = 4321
    controller._write_active_state(
        {
            "state": "running",
            "run_id": "run-001",
            "pid": pid,
            "reason": None,
            "active": True,
        }
    )
    controller.paths.pid_path.write_text(f"{pid}\n", encoding="utf-8")
    controller.paths.lock_path.write_text("locked\n", encoding="utf-8")
    signal_calls: list[int] = []
    controller._signal_process = Mock(side_effect=lambda seen_pid, sig: signal_calls.append(sig) or True)
    monkeypatch.setattr("tdxquant.subscription_watch_background.time.sleep", lambda _: None)
    controller._pid_is_alive = Mock(side_effect=[True, True, False])
    persisted_before = json.loads(controller.paths.active_path.read_text(encoding="utf-8"))

    result = controller.stop(reason="operator_stop", grace_period_seconds=0)
    persisted_after = json.loads(controller.paths.active_path.read_text(encoding="utf-8"))

    assert persisted_before["state"] == "running"
    assert result["ok"] is True
    assert result["result"]["run_id"] == "run-001"
    assert signal_calls == [signal.SIGTERM, signal.SIGKILL]
    assert persisted_after["state"] == "stopped"
    assert persisted_after["reason"] == "forced_stop"
    assert persisted_after["active"] is False


def test_stop_returns_failure_when_force_signal_does_not_end_process(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")
    pid = 4321
    controller._write_active_state(
        {
            "state": "running",
            "run_id": "run-001",
            "pid": pid,
            "reason": None,
            "active": True,
        }
    )
    controller.paths.pid_path.write_text(f"{pid}\n", encoding="utf-8")
    controller.paths.lock_path.write_text("locked\n", encoding="utf-8")
    signal_calls: list[int] = []
    controller._signal_process = Mock(side_effect=lambda seen_pid, sig: signal_calls.append(sig) or True)
    monkeypatch.setattr("tdxquant.subscription_watch_background.time.sleep", lambda _: None)
    controller._pid_is_alive = Mock(return_value=True)

    result = controller.stop(reason="operator_stop", grace_period_seconds=0)
    persisted = json.loads(controller.paths.active_path.read_text(encoding="utf-8"))

    assert result["ok"] is False
    assert result["error"]["code"] == "FORCE_SIGNAL_FAILED"
    assert signal_calls == [signal.SIGTERM, signal.SIGKILL]
    assert persisted["state"] == "stopping"
    assert persisted["reason"] == "operator_stop"
    assert persisted["active"] is True
    assert controller.paths.pid_path.exists()
    assert controller.paths.lock_path.exists()


def test_start_terminates_spawned_process_when_pid_file_write_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")

    class FakeProcess:
        pid = 4321

        def __init__(self) -> None:
            self.terminate_calls = 0
            self.wait_calls: list[float | None] = []
            self.kill_calls = 0

        def terminate(self) -> None:
            self.terminate_calls += 1

        def wait(self, timeout: float | None = None) -> int:
            self.wait_calls.append(timeout)
            return 0

        def kill(self) -> None:
            self.kill_calls += 1

    process = FakeProcess()
    monkeypatch.setattr(controller, "_spawn_runner_process", lambda **kwargs: process)
    monkeypatch.setattr(
        type(controller.paths.pid_path),
        "write_text",
        lambda self, data, encoding=None: (_ for _ in ()).throw(OSError("pid write failed")),
    )

    with pytest.raises(OSError, match="pid write failed"):
        controller.start(stock_list=["600519.SH"])

    assert process.terminate_calls == 1
    assert process.wait_calls == [1.0]
    assert process.kill_calls == 0
    assert not controller.paths.pid_path.exists()
    assert not controller.paths.active_path.exists()


def test_start_terminates_spawned_process_when_active_state_write_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")

    class FakeProcess:
        pid = 4321

        def __init__(self) -> None:
            self.terminate_calls = 0
            self.wait_calls: list[float | None] = []
            self.kill_calls = 0

        def terminate(self) -> None:
            self.terminate_calls += 1

        def wait(self, timeout: float | None = None) -> int:
            self.wait_calls.append(timeout)
            return 0

        def kill(self) -> None:
            self.kill_calls += 1

    process = FakeProcess()
    monkeypatch.setattr(controller, "_spawn_runner_process", lambda **kwargs: process)
    monkeypatch.setattr(controller, "_write_active_state", lambda payload: (_ for _ in ()).throw(OSError("state write failed")))

    with pytest.raises(OSError, match="state write failed"):
        controller.start(stock_list=["600519.SH"])

    assert process.terminate_calls == 1
    assert process.wait_calls == [1.0]
    assert process.kill_calls == 0
    assert not controller.paths.pid_path.exists()
    assert not controller.paths.active_path.exists()


def test_start_preserves_blocking_state_when_spawned_process_cleanup_is_not_confirmed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")

    class FakeProcess:
        pid = 4321

    process = FakeProcess()
    monkeypatch.setattr(controller, "_spawn_runner_process", lambda **kwargs: process)
    monkeypatch.setattr(controller, "_terminate_spawned_process", lambda proc: False)
    original_write_text = Path.write_text

    def fake_write_text(path: Path, data: str, encoding: str | None = None, **kwargs: object) -> int:
        if path == controller.paths.pid_path:
            raise OSError("pid write failed")
        return original_write_text(path, data, encoding=encoding, **kwargs)

    monkeypatch.setattr(Path, "write_text", fake_write_text)

    with pytest.raises(OSError, match="pid write failed"):
        controller.start(stock_list=["600519.SH"])

    persisted = json.loads(controller.paths.active_path.read_text(encoding="utf-8"))
    monkeypatch.setattr(controller, "_pid_is_alive", lambda pid: pid == 4321)
    blocked = controller.start(stock_list=["000001.SZ"])

    assert not controller.paths.pid_path.exists()
    assert persisted["state"] == "starting"
    assert persisted["run_id"]
    assert persisted["pid"] == 4321
    assert persisted["active"] is True
    assert persisted["reason"] == "startup_persistence_failed"
    assert blocked["ok"] is False
    assert blocked["error"]["code"] == "ALREADY_RUNNING"
    assert blocked["error"]["details"]["pid"] == 4321


def test_stop_uses_graceful_timeout_when_grace_period_omitted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    controller = SubscriptionWatchBackgroundController(
        root_dir=tmp_path,
        python_executable="python",
        default_stop_grace_period_seconds=7,
    )
    pid = 4321
    controller._write_active_state(
        {
            "state": "running",
            "run_id": "run-001",
            "pid": pid,
            "reason": None,
            "active": True,
        }
    )
    controller.paths.pid_path.write_text(f"{pid}\n", encoding="utf-8")
    controller.paths.lock_path.write_text("locked\n", encoding="utf-8")
    signal_calls: list[int] = []
    controller._signal_process = Mock(side_effect=lambda seen_pid, sig: signal_calls.append(sig) or True)
    wait_calls: list[int] = []
    monkeypatch.setattr(controller, "_wait_for_process_exit", lambda seen_pid, grace: wait_calls.append(grace) or True)
    controller._pid_is_alive = Mock(side_effect=[True, False])

    result = controller.stop(reason="operator_stop")
    persisted = json.loads(controller.paths.active_path.read_text(encoding="utf-8"))

    assert result["ok"] is True
    assert signal_calls == [signal.SIGTERM]
    assert wait_calls == [7]
    assert persisted["state"] == "stopped"
    assert persisted["reason"] == "operator_stop"
    assert persisted["active"] is False
