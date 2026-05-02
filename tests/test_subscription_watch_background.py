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
    reconcile_background_state,
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
    controller._pid_is_alive = Mock(side_effect=[True, False, False])

    result = controller.stop(reason="operator_stop")
    persisted = json.loads(controller.paths.active_path.read_text(encoding="utf-8"))

    assert result["ok"] is True
    assert signal_calls == [signal.SIGTERM]
    assert persisted["state"] == "stopped"
    assert persisted["reason"] == "operator_stop"
    assert persisted["active"] is False
