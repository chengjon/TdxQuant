# Worker Bridge HTTP Control Plane Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a worker-local `subscription-watch` background-control layer plus `tdxquant bridge serve` LAN HTTP control plane so a fixed Master can start, stop, inspect, and diagnose fixed worker machines without direct shell access.

**Architecture:** Keep `task subscription-watch` as the canonical run-artifact producer, but add a separate worker-local background controller that owns `active.json`, `pid`, `lock`, stale reconciliation, and single-active-watch semantics. Expose that controller through a stdlib HTTP bridge with token + source allowlist enforcement, then add a small Master-side registry/client layer and CLI commands that call fixed worker bridges over HTTP.

**Tech Stack:** Python 3 standard library (`argparse`, `json`, `pathlib`, `subprocess`, `signal`, `threading`, `http.server`, `urllib.request`), existing `Result` envelope, existing `subscription_watch` run-artifact helpers, pytest/unittest-style focused tests, JSON runtime config files under `runtime/bridge/`.

---

## File Structure

- Create: `tdxquant/subscription_watch_background.py`
  - Owns worker-local state paths, `active.json` schema, lock semantics, stale reconciliation, and `start/stop/status/list` control methods.
- Create: `tdxquant/subscription_watch_background_runner.py`
  - Dedicated child-process entrypoint that calls `TdxTaskManager.subscription_watch(...)` and translates SIGTERM into graceful task interruption.
- Create: `tdxquant/bridge_http.py`
  - Owns bridge HTTP request parsing, auth/allowlist, envelope building, and `/bridge/v1/watch/*` endpoint dispatch.
- Create: `tdxquant/bridge_registry.py`
  - Owns Master worker-registry loading plus outbound HTTP client helpers for `health/status/start/stop/list/artifacts/events/logs`.
- Modify: `tdxquant/cli.py`
  - Add `bridge` command group for worker `serve` and Master-side remote control commands.
- Modify: `tdxquant/subscription_watch_run.py`
  - Extend canonical run paths with worker-local runner log path so bridge can return stable log artifacts.
- Modify: `runtime/task-profiles.json`
  - Keep `subscription_watch.run_root_dir` as-is, but add recommended `bridge_root_dir` / `bridge_log_dir` profile defaults if needed by CLI defaults.
- Create runtime examples:
  - `runtime/bridge/worker-bridge.example.json`
  - `runtime/bridge/master-workers.example.json`
- Create tests:
  - `tests/test_subscription_watch_background.py`
  - `tests/test_subscription_watch_background_runner.py`
  - `tests/test_bridge_http.py`
  - `tests/test_bridge_registry.py`
- Modify tests:
  - `tests/test_api_cli.py`
  - `tests/test_api_manager.py` (only if runner/controller needs manager-facing contract assertions)
- Modify docs:
  - `docs/TdxQuant_Task_Subscription_Watch_Contract.md`
  - `docs/TdxQuant_Project_Function_Map.md`
  - `docs/TdxQuant_Next_Steps.md`
  - `docs/TdxQuant_Provider_Replay_Fixtures.md` (only if any replay-facing examples need bridge note)

## Implementation Notes

- The background-control state machine is **not** the same thing as the canonical `subscription-watch` task `status.json`.
  - Background control owns: `starting`, `running`, `stopping`, `completed`, `failed`, `stopped`
  - Task artifacts may still end in `completed` or `interrupted`
  - The controller translates task/process outcomes into the worker-local control state
- Do **not** add new third-party HTTP frameworks. Use Python stdlib only.
- Do **not** let replay or bridge code silently fall back to live runtime behavior.
- Keep bridge transport and worker-local lifecycle logic separate. `bridge_http.py` should call controller methods, not manipulate `pid`/`lock`/JSON files directly.

### Task 1: Build Worker-Local Background State and Reconciliation

**Files:**
- Create: `tdxquant/subscription_watch_background.py`
- Modify: `tdxquant/subscription_watch_run.py`
- Test: `tests/test_subscription_watch_background.py`

- [ ] **Step 1: Write the failing state-path and stale-reconciliation tests**

```python
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
    paths.active_path.write_text(
        '{"state":"running","run_id":"run-001","pid":999999,"status_path":"runtime/subscription-watch/run-001/status.json"}',
        encoding="utf-8",
    )

    reconciled = reconcile_background_state(paths)

    assert reconciled["state"] == "failed"
    assert reconciled["reason"] == "stale_process_state"
```

- [ ] **Step 2: Run the state tests to verify they fail**

Run:

```bash
python -m pytest tests/test_subscription_watch_background.py -q
```

Expected:

```text
ERROR tests/test_subscription_watch_background.py
E   ModuleNotFoundError: No module named 'tdxquant.subscription_watch_background'
```

- [ ] **Step 3: Implement the minimal background path + reconciliation helper**

```python
# tdxquant/subscription_watch_background.py
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


def reconcile_background_state(paths: SubscriptionWatchBackgroundPaths) -> dict[str, Any]:
    if not paths.active_path.exists():
        return {"state": "stopped", "active": False}

    payload = json.loads(paths.active_path.read_text(encoding="utf-8"))
    pid = int(payload.get("pid") or 0)
    state = str(payload.get("state") or "failed")
    if state in {"starting", "running", "stopping"} and (pid <= 0 or not _pid_is_alive(pid)):
        payload["state"] = "failed" if state != "stopping" else "stopped"
        payload["reason"] = "stale_process_state" if state != "stopping" else "forced_stop"
        paths.active_path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")
    return payload
```

- [ ] **Step 4: Extend run-path helpers with a stable runner-log path**

```python
# tdxquant/subscription_watch_run.py
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
```

- [ ] **Step 5: Run the focused state tests to verify they pass**

Run:

```bash
python -m pytest tests/test_subscription_watch_background.py tests/test_subscription_watch_run.py -q
```

Expected:

```text
..                                                                   [100%]
```

- [ ] **Step 6: Commit**

```bash
git add tdxquant/subscription_watch_background.py tdxquant/subscription_watch_run.py tests/test_subscription_watch_background.py tests/test_subscription_watch_run.py
git commit -m "feat: add subscription watch background state helpers"
```

### Task 2: Add the Worker-Local Background Controller and Runner

**Files:**
- Modify: `tdxquant/subscription_watch_background.py`
- Create: `tdxquant/subscription_watch_background_runner.py`
- Modify: `tdxquant/api/task.py`
- Test: `tests/test_subscription_watch_background.py`
- Test: `tests/test_subscription_watch_background_runner.py`

- [ ] **Step 1: Write the failing controller lifecycle tests**

```python
from pathlib import Path
from unittest.mock import Mock

from tdxquant.subscription_watch_background import SubscriptionWatchBackgroundController


def test_start_rejects_when_active_state_is_running(tmp_path: Path) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")
    controller._write_active_state(  # test helper
        {"state": "running", "run_id": "run-001", "pid": 1234, "reason": None}
    )

    result = controller.start(stock_list=["600519.SH"])

    assert result["ok"] is False
    assert result["error"]["code"] == "ALREADY_RUNNING"


def test_stop_marks_state_stopping_and_returns_run_id(tmp_path: Path) -> None:
    controller = SubscriptionWatchBackgroundController(root_dir=tmp_path, python_executable="python")
    controller._write_active_state(
        {"state": "running", "run_id": "run-001", "pid": 4321, "reason": None}
    )
    controller._signal_process = Mock(return_value=True)

    result = controller.stop(reason="operator_stop", grace_period_seconds=2)

    assert result["ok"] is True
    assert result["result"]["run_id"] == "run-001"
```

- [ ] **Step 2: Run the lifecycle tests to verify they fail**

Run:

```bash
python -m pytest tests/test_subscription_watch_background.py::test_start_rejects_when_active_state_is_running tests/test_subscription_watch_background.py::test_stop_marks_state_stopping_and_returns_run_id -q
```

Expected:

```text
E   AttributeError: module 'tdxquant.subscription_watch_background' has no attribute 'SubscriptionWatchBackgroundController'
```

- [ ] **Step 3: Implement the controller and dedicated runner contract**

```python
# tdxquant/subscription_watch_background.py
class SubscriptionWatchBackgroundController:
    def __init__(self, *, root_dir: Path, python_executable: str, cli_module: str = "tdxquant.subscription_watch_background_runner") -> None:
        self.paths = build_background_paths(root_dir)
        self.python_executable = python_executable
        self.cli_module = cli_module
        self._control_lock = threading.Lock()

    def start(self, *, stock_list: list[str], max_events: int | None = None, max_seconds: float | None = None, poll_interval: float | None = None, idempotency_key: str | None = None) -> dict[str, Any]:
        with self._control_lock:
            current = reconcile_background_state(self.paths)
            if current.get("state") in {"starting", "running", "stopping"}:
                return {"ok": False, "error": {"code": "ALREADY_RUNNING", "details": current}}
            # build run_id, spawn child runner, persist active.json + pid

    def stop(self, *, reason: str | None = None, grace_period_seconds: int | None = None) -> dict[str, Any]:
        with self._control_lock:
            current = reconcile_background_state(self.paths)
            if current.get("state") not in {"starting", "running", "stopping"}:
                return {"ok": True, "result": {"status": "noop", "reason": "NOT_RUNNING"}}
            # mark stopping, SIGTERM child, optional force-kill, refresh state


# tdxquant/subscription_watch_background_runner.py
from __future__ import annotations

import signal
import sys

from tdxquant.api.manager import TdxTaskManager

_STOP_REQUESTED = False


def _handle_sigterm(signum, frame) -> None:
    raise KeyboardInterrupt()


def main(argv: list[str] | None = None) -> int:
    signal.signal(signal.SIGTERM, _handle_sigterm)
    # parse args, construct TdxTaskManager(profile="subscription_watch"), call subscription_watch(...)
    # mirror runner stdout/stderr into runner.log, return 0 on success, non-zero on failure
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

- [ ] **Step 4: Add a failing signal-handling runner test**

```python
from tdxquant.subscription_watch_background_runner import _handle_sigterm


def test_handle_sigterm_raises_keyboard_interrupt() -> None:
    try:
        _handle_sigterm(None, None)
    except KeyboardInterrupt:
        return
    assert False, "SIGTERM handler must raise KeyboardInterrupt"
```

- [ ] **Step 5: Run controller + runner tests to verify they pass**

Run:

```bash
python -m pytest tests/test_subscription_watch_background.py tests/test_subscription_watch_background_runner.py -q
```

Expected:

```text
....                                                                 [100%]
```

- [ ] **Step 6: Commit**

```bash
git add tdxquant/subscription_watch_background.py tdxquant/subscription_watch_background_runner.py tdxquant/api/task.py tests/test_subscription_watch_background.py tests/test_subscription_watch_background_runner.py
git commit -m "feat: add local subscription watch background controller"
```

### Task 3: Implement the Worker HTTP Bridge

**Files:**
- Create: `tdxquant/bridge_http.py`
- Modify: `tdxquant/cli.py`
- Test: `tests/test_bridge_http.py`
- Test: `tests/test_api_cli.py`

- [ ] **Step 1: Write the failing HTTP envelope and auth tests**

```python
from pathlib import Path

from tdxquant.bridge_http import BridgeConfig, BridgeRequestHandler, build_bridge_success, build_bridge_failure


def test_build_bridge_success_uses_required_envelope_fields() -> None:
    payload = build_bridge_success(worker_id="worker-a", request_id="req-001", result={"status": "running"})

    assert payload["ok"] is True
    assert payload["result"]["status"] == "running"
    assert payload["error"] is None
    assert payload["meta"]["worker_id"] == "worker-a"


def test_bridge_config_rejects_missing_token() -> None:
    try:
        BridgeConfig(worker_id="worker-a", bind_host="0.0.0.0", port=8080, token="", master_allowlist=["127.0.0.1"])
    except ValueError:
        return
    assert False, "empty token must be rejected"
```

- [ ] **Step 2: Run the HTTP tests to verify they fail**

Run:

```bash
python -m pytest tests/test_bridge_http.py -q
```

Expected:

```text
ERROR tests/test_bridge_http.py
E   ModuleNotFoundError: No module named 'tdxquant.bridge_http'
```

- [ ] **Step 3: Implement the stdlib bridge HTTP layer**

```python
# tdxquant/bridge_http.py
from __future__ import annotations

from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from typing import Any


@dataclass(frozen=True)
class BridgeConfig:
    worker_id: str
    bind_host: str
    port: int
    token: str
    master_allowlist: list[str]
    root_dir: str

    def __post_init__(self) -> None:
        if not self.token:
            raise ValueError("bridge token is required")


def build_bridge_success(*, worker_id: str, request_id: str, result: dict[str, Any]) -> dict[str, Any]:
    return {"ok": True, "result": result, "error": None, "meta": {"bridge_version": "v1", "worker_id": worker_id, "request_id": request_id}}


def build_bridge_failure(*, worker_id: str, request_id: str, code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"ok": False, "result": None, "error": {"code": code, "message": message, "details": details or {}}, "meta": {"bridge_version": "v1", "worker_id": worker_id, "request_id": request_id}}


class BridgeRequestHandler(BaseHTTPRequestHandler):
    # parse Authorization header, source-IP allowlist, then dispatch:
    # POST /bridge/v1/watch/start
    # POST /bridge/v1/watch/stop
    # GET  /bridge/v1/watch/status
    # GET  /bridge/v1/watch/list
    # GET  /bridge/v1/watch/artifacts
    # GET  /bridge/v1/watch/events
    # GET  /bridge/v1/watch/logs
    # GET  /bridge/v1/health
    ...
```

- [ ] **Step 4: Add CLI parser tests for `bridge serve`**

```python
def test_bridge_serve_command_parses() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "bridge",
            "serve",
            "--config",
            "runtime/bridge/worker-bridge.json",
        ]
    )

    assert args.command == "bridge"
    assert args.bridge_command == "serve"
    assert args.config == "runtime/bridge/worker-bridge.json"
```

- [ ] **Step 5: Wire the new `bridge serve` CLI command**

```python
# tdxquant/cli.py
def _build_bridge_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> argparse.ArgumentParser:
    bridge_parser = subparsers.add_parser("bridge")
    bridge_subparsers = bridge_parser.add_subparsers(dest="bridge_command", required=True)

    bridge_serve_parser = bridge_subparsers.add_parser("serve")
    bridge_serve_parser.add_argument("--config", required=True)

    return bridge_parser
```

- [ ] **Step 6: Run HTTP + CLI tests to verify they pass**

Run:

```bash
python -m pytest tests/test_bridge_http.py tests/test_api_cli.py -k "bridge" -q
```

Expected:

```text
.....                                                                [100%]
```

- [ ] **Step 7: Commit**

```bash
git add tdxquant/bridge_http.py tdxquant/cli.py tests/test_bridge_http.py tests/test_api_cli.py
git commit -m "feat: add worker bridge HTTP serve command"
```

### Task 4: Add Master Registry and Remote-Control CLI

**Files:**
- Create: `tdxquant/bridge_registry.py`
- Modify: `tdxquant/cli.py`
- Test: `tests/test_bridge_registry.py`
- Test: `tests/test_api_cli.py`
- Create: `runtime/bridge/worker-bridge.example.json`
- Create: `runtime/bridge/master-workers.example.json`

- [ ] **Step 1: Write the failing registry-load and HTTP-client tests**

```python
from pathlib import Path

from tdxquant.bridge_registry import BridgeWorker, load_worker_registry


def test_load_worker_registry_reads_enabled_workers(tmp_path: Path) -> None:
    path = tmp_path / "master-workers.json"
    path.write_text(
        '[{"worker_id":"worker-a","label":"A","host":"127.0.0.1","port":8080,"token_env":"BRIDGE_TOKEN_A","role_tags":["watch"],"enabled":true}]',
        encoding="utf-8",
    )

    workers = load_worker_registry(path)

    assert len(workers) == 1
    assert workers[0].worker_id == "worker-a"
    assert workers[0].host == "127.0.0.1"
```

- [ ] **Step 2: Run the registry tests to verify they fail**

Run:

```bash
python -m pytest tests/test_bridge_registry.py -q
```

Expected:

```text
ERROR tests/test_bridge_registry.py
E   ModuleNotFoundError: No module named 'tdxquant.bridge_registry'
```

- [ ] **Step 3: Implement the registry and outbound bridge client helpers**

```python
# tdxquant/bridge_registry.py
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class BridgeWorker:
    worker_id: str
    label: str
    host: str
    port: int
    token_env: str
    role_tags: list[str]
    enabled: bool


def load_worker_registry(path: Path) -> list[BridgeWorker]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [BridgeWorker(**item) for item in payload if item.get("enabled", True)]


def call_worker(worker: BridgeWorker, *, method: str, route: str, token: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    request = Request(
        f"http://{worker.host}:{worker.port}{route}",
        method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        data=None if body is None else json.dumps(body).encode("utf-8"),
    )
    with urlopen(request, timeout=5.0) as response:
        return json.loads(response.read().decode("utf-8"))
```

- [ ] **Step 4: Add Master-side bridge CLI tests and commands**

```python
def test_bridge_watch_status_command_parses() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "bridge",
            "watch-status",
            "--registry",
            "runtime/bridge/master-workers.json",
            "--worker",
            "worker-a",
        ]
    )

    assert args.command == "bridge"
    assert args.bridge_command == "watch-status"
    assert args.worker == "worker-a"
```

```python
# tdxquant/cli.py
bridge_watch_status_parser = bridge_subparsers.add_parser("watch-status")
bridge_watch_status_parser.add_argument("--registry", required=True)
bridge_watch_status_parser.add_argument("--worker", required=True)

bridge_watch_start_parser = bridge_subparsers.add_parser("watch-start")
bridge_watch_start_parser.add_argument("--registry", required=True)
bridge_watch_start_parser.add_argument("--worker", required=True)
bridge_watch_start_parser.add_argument("--code", action="append", required=True)
bridge_watch_start_parser.add_argument("--max-events", type=int)
bridge_watch_start_parser.add_argument("--max-seconds", type=float)

bridge_watch_stop_parser = bridge_subparsers.add_parser("watch-stop")
bridge_watch_stop_parser.add_argument("--registry", required=True)
bridge_watch_stop_parser.add_argument("--worker", required=True)
```

- [ ] **Step 5: Add example JSON configs**

```json
// runtime/bridge/worker-bridge.example.json
{
  "worker_id": "worker-sh-01",
  "bind_host": "0.0.0.0",
  "port": 8787,
  "token_env": "TDX_BRIDGE_TOKEN",
  "master_allowlist": ["192.168.1.10"],
  "run_root_dir": "runtime/subscription-watch",
  "log_dir": "runtime/bridge/logs",
  "start_timeout_seconds": 10,
  "stop_grace_period_seconds": 5,
  "stop_force_kill_timeout_seconds": 2
}
```

```json
// runtime/bridge/master-workers.example.json
[
  {
    "worker_id": "worker-sh-01",
    "label": "Shanghai Worker",
    "host": "192.168.1.21",
    "port": 8787,
    "token_env": "TDX_BRIDGE_TOKEN_WORKER_SH_01",
    "role_tags": ["subscription-watch"],
    "enabled": true
  }
]
```

- [ ] **Step 6: Run registry + CLI tests to verify they pass**

Run:

```bash
python -m pytest tests/test_bridge_registry.py tests/test_api_cli.py -k "bridge and watch" -q
```

Expected:

```text
......                                                               [100%]
```

- [ ] **Step 7: Commit**

```bash
git add tdxquant/bridge_registry.py tdxquant/cli.py tests/test_bridge_registry.py tests/test_api_cli.py runtime/bridge/worker-bridge.example.json runtime/bridge/master-workers.example.json
git commit -m "feat: add master worker registry and bridge control CLI"
```

### Task 5: Documentation, Verification, and Integration Cleanup

**Files:**
- Modify: `docs/TdxQuant_Task_Subscription_Watch_Contract.md`
- Modify: `docs/TdxQuant_Project_Function_Map.md`
- Modify: `docs/TdxQuant_Next_Steps.md`
- Modify: `tests/test_api_cli.py`
- Modify: `tests/test_bridge_http.py`
- Modify: `tests/test_bridge_registry.py`

- [ ] **Step 1: Update the worker/control-plane docs**

```markdown
## Worker Bridge HTTP Control Plane

- Worker-local single-active `subscription-watch` background control
- `tdxquant bridge serve --config runtime/bridge/worker-bridge.json`
- Master-side static worker registry
- Supported bridge endpoints:
  - `POST /bridge/v1/watch/start`
  - `POST /bridge/v1/watch/stop`
  - `GET /bridge/v1/watch/status`
  - `GET /bridge/v1/watch/list`
  - `GET /bridge/v1/watch/artifacts`
  - `GET /bridge/v1/watch/events`
  - `GET /bridge/v1/watch/logs`
  - `GET /bridge/v1/health`
```

- [ ] **Step 2: Add integration-style CLI tests for failure normalization**

```python
def test_bridge_watch_start_requires_registry_and_worker() -> None:
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["bridge", "watch-start"])


def test_bridge_watch_status_uses_worker_registry_client(mocker) -> None:
    mock_call = mocker.patch("tdxquant.bridge_registry.call_worker", return_value={"ok": True, "result": {"state": "running"}, "error": None, "meta": {"worker_id": "worker-a"}})
    result = handle_args(parser.parse_args(["bridge", "watch-status", "--registry", "runtime/bridge/master-workers.json", "--worker", "worker-a"]))

    assert result.ok is True
    mock_call.assert_called_once()
```

- [ ] **Step 3: Run the focused bridge suite**

Run:

```bash
python -m pytest tests/test_subscription_watch_background.py tests/test_subscription_watch_background_runner.py tests/test_bridge_http.py tests/test_bridge_registry.py tests/test_api_cli.py -k "bridge or subscription_watch_background" -q
```

Expected:

```text
all selected tests pass
```

- [ ] **Step 4: Run the broader regression suite**

Run:

```bash
python -m pytest tests/test_api_manager.py tests/test_api_cli.py tests/test_subscription_watch_run.py tests/test_replay_provider.py tests/test_replay_fixtures.py -q
```

Expected:

```text
all selected tests pass with no replay/subscription-watch regressions
```

- [ ] **Step 5: Commit**

```bash
git add docs/TdxQuant_Task_Subscription_Watch_Contract.md docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Next_Steps.md tests/test_api_cli.py tests/test_bridge_http.py tests/test_bridge_registry.py
git commit -m "docs: document worker bridge control plane"
```

## Spec Coverage Check

- Worker-local single-active background control: covered by Task 1 and Task 2.
- State machine, stale reconciliation, timeout config: covered by Task 1 and Task 2.
- HTTP bridge endpoints, auth, allowlist, envelope, error normalization: covered by Task 3.
- Master static registry and remote control commands: covered by Task 4.
- Tail diagnostics (`events` / `logs`) and artifact semantics: covered by Task 3 and Task 5.
- Config format/path conventions and docs updates: covered by Task 4 and Task 5.

## Notes for Execution

- Start with TDD. Do not write `bridge_http.py` first and “come back for tests later.”
- Do not try to solve multi-worker scheduling, self-registration, or TLS in this plan.
- Keep the first transport implementation synchronous and boring. Correctness and contract stability matter more than throughput.
- Prefer creating small helper functions in `subscription_watch_background.py` over a single giant controller class.

