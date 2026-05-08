from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from tdxquant.subscription_watch_background import build_background_paths
from tdxquant.subscription_watch_background_runner import _handle_sigterm, main
from tdxquant.subscription_watch_run import build_subscription_watch_run_paths


def test_handle_sigterm_raises_keyboard_interrupt() -> None:
    with pytest.raises(KeyboardInterrupt):
        _handle_sigterm(None, None)


def test_main_writes_terminal_failed_state_when_post_processing_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = build_background_paths(tmp_path)
    paths.root_dir.mkdir(parents=True, exist_ok=True)
    paths.pid_path.write_text(f"{os.getpid()}\n", encoding="utf-8")
    paths.lock_path.write_text("locked\n", encoding="utf-8")

    class FakeTaskManager:
        def __init__(self, **kwargs) -> None:
            self.kwargs = kwargs

        def subscription_watch(self, **kwargs):
            return SimpleNamespace(ok=True, code="OK", message="done", data=None)

    monkeypatch.setattr("tdxquant.subscription_watch_background_runner.TdxTaskManager", FakeTaskManager)

    exit_code = main(["--root-dir", str(tmp_path), "--run-id", "run-001", "--code", "600519.SH"])
    payload = json.loads(paths.active_path.read_text(encoding="utf-8"))

    assert exit_code == 1
    assert payload["state"] == "failed"
    assert payload["reason"] == "unexpected_exception"
    assert payload["active"] is False
    assert payload["pid"] is None
    assert not paths.pid_path.exists()
    assert paths.lock_path.exists()


def test_main_writes_terminal_stopped_state_when_interrupted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = build_background_paths(tmp_path)
    paths.root_dir.mkdir(parents=True, exist_ok=True)
    paths.pid_path.write_text(f"{os.getpid()}\n", encoding="utf-8")
    paths.lock_path.write_text("locked\n", encoding="utf-8")

    class FakeTaskManager:
        def __init__(self, **kwargs) -> None:
            self.kwargs = kwargs

        def subscription_watch(self, **kwargs):
            raise KeyboardInterrupt()

    monkeypatch.setattr("tdxquant.subscription_watch_background_runner.TdxTaskManager", FakeTaskManager)

    exit_code = main(["--root-dir", str(tmp_path), "--run-id", "run-001", "--code", "600519.SH"])
    payload = json.loads(paths.active_path.read_text(encoding="utf-8"))

    assert exit_code == 1
    assert payload["state"] == "stopped"
    assert payload["reason"] == "keyboard_interrupt"
    assert payload["active"] is False
    assert payload["pid"] is None
    assert not paths.pid_path.exists()
    assert paths.lock_path.exists()


def test_main_persists_terminal_state_when_interrupted_during_early_setup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = build_background_paths(tmp_path)
    terminal_calls: list[dict[str, object]] = []

    def fake_write_background_state(*args, **kwargs):
        raise KeyboardInterrupt()

    def fake_write_terminal_background_state(*args, **kwargs):
        terminal_calls.append(kwargs)
        paths.root_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "state": kwargs["state"],
            "active": False,
            "run_id": kwargs["run_id"],
            "pid": None,
            "reason": kwargs["reason"],
            "runner_log_path": str(kwargs["runner_log_path"]) if kwargs.get("runner_log_path") else None,
        }
        paths.active_path.write_text(json.dumps(payload), encoding="utf-8")
        return payload

    monkeypatch.setattr(
        "tdxquant.subscription_watch_background_runner.write_background_state",
        fake_write_background_state,
    )
    monkeypatch.setattr(
        "tdxquant.subscription_watch_background_runner.write_terminal_background_state",
        fake_write_terminal_background_state,
    )

    exit_code = main(["--root-dir", str(tmp_path), "--run-id", "run-early", "--code", "600519.SH"])
    payload = json.loads(paths.active_path.read_text(encoding="utf-8"))
    run_paths = build_subscription_watch_run_paths(tmp_path, run_id="run-early")

    assert exit_code == 1
    assert terminal_calls == [
        {
            "run_id": "run-early",
            "state": "stopped",
            "reason": "keyboard_interrupt",
            "runner_log_path": run_paths.runner_log_path,
        }
    ]
    assert payload["state"] == "stopped"
    assert payload["reason"] == "keyboard_interrupt"
    assert payload["run_id"] == "run-early"


def test_main_clears_next_reconnect_at_from_terminal_status_payload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = build_background_paths(tmp_path)

    class FakeTaskManager:
        def __init__(self, **kwargs) -> None:
            self.kwargs = kwargs

        def subscription_watch(self, **kwargs):
            run_paths = build_subscription_watch_run_paths(tmp_path, run_id=kwargs["run_id"])
            run_paths.run_dir.mkdir(parents=True, exist_ok=True)
            run_paths.status_path.write_text(
                json.dumps(
                    {
                        "run_id": kwargs["run_id"],
                        "state": "completed",
                        "next_reconnect_at": "2026-05-03T09:01:00+00:00",
                    }
                ),
                encoding="utf-8",
            )
            return SimpleNamespace(
                ok=True,
                code="OK",
                message="done",
                data={"summary": {"interrupted": False}},
            )

    monkeypatch.setattr("tdxquant.subscription_watch_background_runner.TdxTaskManager", FakeTaskManager)

    exit_code = main(["--root-dir", str(tmp_path), "--run-id", "run-001", "--code", "600519.SH"])
    payload = json.loads(paths.active_path.read_text(encoding="utf-8"))
    run_paths = build_subscription_watch_run_paths(tmp_path, run_id="run-001")
    status_payload = json.loads(run_paths.status_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert payload["state"] == "completed"
    assert status_payload["state"] == "completed"
    assert status_payload["next_reconnect_at"] is None


def test_main_marks_degraded_failure_with_explicit_terminal_reason(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = build_background_paths(tmp_path)

    class FakeTaskManager:
        def __init__(self, **kwargs) -> None:
            self.kwargs = kwargs

        def subscription_watch(self, **kwargs):
            paths.active_path.write_text(
                json.dumps(
                    {
                        "state": "degraded",
                        "run_id": kwargs["run_id"],
                        "pid": os.getpid(),
                        "reason": None,
                        "active": True,
                    }
                ),
                encoding="utf-8",
            )
            return SimpleNamespace(ok=False, code="EXECUTION_FAILED", message="failed", data={"summary": {"interrupted": False}})

    monkeypatch.setattr("tdxquant.subscription_watch_background_runner.TdxTaskManager", FakeTaskManager)

    exit_code = main(["--root-dir", str(tmp_path), "--run-id", "run-degraded", "--code", "600519.SH"])
    payload = json.loads(paths.active_path.read_text(encoding="utf-8"))

    assert exit_code == 1
    assert payload["state"] == "failed"
    assert payload["reason"] == "degraded_unrecovered"
