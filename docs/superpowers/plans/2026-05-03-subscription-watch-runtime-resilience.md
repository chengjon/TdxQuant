# Subscription Watch Runtime Resilience Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add bounded reconnect, degraded low-frequency recovery, and shared runtime-state reporting to live `subscription-watch` without changing `run_id` or introducing a new transport.

**Architecture:** Keep the current foreground `subscription_watch(...)` task as the owner of the live subscription loop and run artifacts, but extend it with a reconnect state machine and runtime-state fields. Reuse the existing background controller and bridge transport, only widening their state interpretation and read models so they expose the same resilience contract instead of inventing a second lifecycle.

**Tech Stack:** Python 3 standard library (`time`, `threading`, `json`, `signal`, `pathlib`), existing `Result` envelope, existing `subscription_watch_run.py` artifact builders, background controller in `subscription_watch_background.py`, bridge HTTP read model, pytest.

---

## File Structure

- Modify: `tdxquant/subscription_watch_run.py`
  - Extend canonical `status.json` and `summary.json` payload builders with reconnect/degraded fields while keeping the existing run-artifact schema stable.
- Modify: `tdxquant/api/task.py`
  - Add the actual reconnect/degraded state machine, bounded retry policy, degraded probe loop, and runtime-state updates inside `TdxTaskManager.subscription_watch(...)`.
- Modify: `tdxquant/subscription_watch_background.py`
  - Teach background reconcile/read methods about `reconnecting` and `degraded`, and make `stale_process_state` normalization explicit for the new active-process states.
- Modify: `tdxquant/subscription_watch_background_runner.py`
  - Ensure runner-owned state transitions and terminal persistence stay correct when the foreground task ends from reconnect/degraded/stopping paths.
- Modify: `tdxquant/bridge_http.py`
  - Only if necessary to expose newly added runtime fields cleanly through existing status/artifact responses; no new endpoints.
- Modify replay fixtures:
  - `tdxquant/fixtures/provider/subscription-watch-status-completed.json`
  - `tdxquant/fixtures/provider/subscription-watch-summary-completed.json`
- Create replay fixtures:
  - `tdxquant/fixtures/provider/subscription-watch-status-reconnecting.json`
  - `tdxquant/fixtures/provider/subscription-watch-status-degraded.json`
  - `tdxquant/fixtures/provider/subscription-watch-summary-with-reconnect.json`
- Modify registry if needed:
  - `tdxquant/replay_fixtures.py`
- Modify tests:
  - `tests/test_subscription_watch_run.py`
  - `tests/test_subscription_watch_background.py`
  - `tests/test_subscription_watch_background_runner.py`
  - `tests/test_bridge_http.py`
  - `tests/test_api_manager.py`
  - `tests/test_replay_fixtures.py`
- Modify docs:
  - `docs/TdxQuant_Task_Subscription_Watch_Contract.md`
  - `docs/TdxQuant_Project_Function_Map.md`
  - `docs/TdxQuant_Next_Steps.md`

## Implementation Notes

- Keep a single `run_id` and a single `events.jsonl` across reconnects. Do not rotate runs on disconnect.
- Do not add synthetic reconnect lifecycle events to `events.jsonl` in v1. Reconnect state lives in `status.json`, `summary.json`, and `runner.log`.
- Reuse `last_event_ts`; do not introduce a second synonymous field like `last_event_at`.
- Do not add a redundant `runtime_health` field. Use `state` directly for `running`, `reconnecting`, and `degraded`.
- `reconnect_metadata` in normal event rows remains `{}` in v1.
- Background reconcile must treat `starting`, `running`, `reconnecting`, `degraded`, and `stopping` as active-process states.

### Task 1: Extend Run Artifact Builders for Resilience State

**Files:**
- Modify: `tdxquant/subscription_watch_run.py`
- Test: `tests/test_subscription_watch_run.py`

- [ ] **Step 1: Write the failing contract test for resilience-aware status/summary payloads**

```python
def test_build_subscription_watch_payloads_include_resilience_fields(tmp_path: Path) -> None:
    paths = build_subscription_watch_run_paths(tmp_path, run_id="run-001")

    status = build_subscription_watch_status_payload(
        paths=paths,
        state="reconnecting",
        started_at="2026-05-03T09:00:00+00:00",
        updated_at="2026-05-03T09:00:05+00:00",
        session_id="session-001",
        event_count=2,
        last_sequence=2,
        last_event_ts="2026-05-03T09:00:02+00:00",
        last_symbol="600519.SH",
        warnings=[],
        heartbeat_at="2026-05-03T09:00:05+00:00",
        last_source_ts="2026-05-03T17:00:02+08:00",
        reconnect_count=1,
        consecutive_reconnect_failures=1,
        last_disconnect_at="2026-05-03T09:00:03+00:00",
        last_reconnect_at=None,
        next_reconnect_at="2026-05-03T09:00:06+00:00",
        degraded_since=None,
        last_error={"code": "SESSION_LOST", "message": "session lost", "at": "2026-05-03T09:00:03+00:00"},
    )
    summary = build_subscription_watch_summary_payload(
        paths=paths,
        final_state="completed",
        started_at="2026-05-03T09:00:00+00:00",
        finished_at="2026-05-03T09:01:00+00:00",
        elapsed_ms=60000.0,
        session_id="session-001",
        event_count=2,
        symbol_count=1,
        stop_reason="completed",
        warning_count=0,
        reconnect_count=1,
        degraded_duration_ms=0.0,
        final_last_error=None,
    )

    assert status["state"] == "reconnecting"
    assert status["heartbeat_at"] == "2026-05-03T09:00:05+00:00"
    assert status["last_event_ts"] == "2026-05-03T09:00:02+00:00"
    assert status["next_reconnect_at"] == "2026-05-03T09:00:06+00:00"
    assert summary["reconnect_count"] == 1
    assert summary["degraded_duration_ms"] == 0.0
```

- [ ] **Step 2: Run the focused payload test and confirm it fails**

Run:

```bash
python -m pytest tests/test_subscription_watch_run.py -q
```

Expected:

```text
E   TypeError: build_subscription_watch_status_payload() got an unexpected keyword argument 'heartbeat_at'
```

- [ ] **Step 3: Extend status/summary payload builders with the resilience fields**

```python
# tdxquant/subscription_watch_run.py
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
    heartbeat_at: str | None,
    last_source_ts: str | None,
    reconnect_count: int,
    consecutive_reconnect_failures: int,
    last_disconnect_at: str | None,
    last_reconnect_at: str | None,
    next_reconnect_at: str | None,
    degraded_since: str | None,
    last_error: dict[str, Any] | None,
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
    reconnect_count: int,
    degraded_duration_ms: float,
    final_last_error: dict[str, Any] | None,
) -> dict[str, Any]:
    payload = {
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
    return payload
```

- [ ] **Step 4: Re-run the payload tests and confirm they pass**

Run:

```bash
python -m pytest tests/test_subscription_watch_run.py -q
```

Expected:

```text
2 passed
```

- [ ] **Step 5: Commit**

```bash
git add tdxquant/subscription_watch_run.py tests/test_subscription_watch_run.py
git commit -m "feat: extend subscription watch run artifacts for resilience"
```

### Task 2: Implement Foreground Reconnect and Degraded Recovery

**Files:**
- Modify: `tdxquant/api/task.py`
- Test: `tests/test_api_manager.py`

- [ ] **Step 1: Write the failing task-level tests for reconnect and degraded transitions**

```python
def test_subscription_watch_enters_reconnecting_and_recovers(monkeypatch, tmp_path: Path) -> None:
    events = [{"Now": 1.0, "UpdateTime": "2026-05-03T09:30:01+08:00"}]
    fake_session = build_fake_subscription_session(
        subscribe_ok=True,
        read_sequence=[RuntimeError("lost session"), None],
        emitted_batches=[events],
    )
    manager = build_task_manager_with_runtime_session(monkeypatch, fake_session, tmp_path)

    result = manager.subscription_watch(stock_list=["600519.SH"], max_events=1, poll_interval=0.0, run_id="run-001")

    assert result.ok is True
    assert result.data["status"]["reconnect_count"] == 1
    assert result.data["status"]["state"] == "running"


def test_subscription_watch_enters_degraded_after_retry_budget(monkeypatch, tmp_path: Path) -> None:
    fake_session = build_fake_subscription_session(
        subscribe_ok=True,
        read_sequence=[
            RuntimeError("lost session"),
            RuntimeError("lost session"),
            RuntimeError("lost session"),
            RuntimeError("lost session"),
        ],
        emitted_batches=[],
    )
    manager = build_task_manager_with_runtime_session(monkeypatch, fake_session, tmp_path)

    result = manager.subscription_watch(stock_list=["600519.SH"], max_seconds=0.1, poll_interval=0.0, run_id="run-002")

    assert result.ok is False
    assert result.data["status"]["state"] == "degraded"
    assert result.data["status"]["consecutive_reconnect_failures"] >= 3
```

- [ ] **Step 2: Run the focused task tests and verify they fail**

Run:

```bash
python -m pytest tests/test_api_manager.py -k "subscription_watch_enters_reconnecting or subscription_watch_enters_degraded" -q
```

Expected:

```text
FF
```

- [ ] **Step 3: Implement reconnect bookkeeping and bounded retry logic inside `subscription_watch(...)`**

```python
# tdxquant/api/task.py
FAST_RECONNECT_BACKOFF_SECONDS = (1.0, 2.0, 5.0)
DEGRADED_PROBE_INTERVAL_SECONDS = 60.0

reconnect_count = 0
consecutive_reconnect_failures = 0
heartbeat_at: str | None = None
last_source_ts: str | None = None
last_disconnect_at: str | None = None
last_reconnect_at: str | None = None
next_reconnect_at: str | None = None
degraded_since: str | None = None
degraded_started_monotonic: float | None = None
degraded_duration_ms = 0.0
last_error: dict[str, Any] | None = None

def enter_reconnecting(exc: Exception) -> None:
    nonlocal consecutive_reconnect_failures, last_disconnect_at, last_error
    consecutive_reconnect_failures += 1
    last_disconnect_at = _now_utc_iso()
    last_error = {"code": "SESSION_LOST", "message": str(exc), "at": last_disconnect_at}
    write_status(state="reconnecting")

def enter_degraded() -> None:
    nonlocal degraded_since, degraded_started_monotonic, next_reconnect_at
    degraded_since = _now_utc_iso()
    degraded_started_monotonic = time.monotonic()
    next_reconnect_at = _iso_after_seconds(DEGRADED_PROBE_INTERVAL_SECONDS)
    write_status(state="degraded")

def exit_degraded() -> None:
    nonlocal degraded_since, degraded_started_monotonic, degraded_duration_ms
    if degraded_started_monotonic is not None:
        degraded_duration_ms += (time.monotonic() - degraded_started_monotonic) * 1000.0
    degraded_since = None
    degraded_started_monotonic = None

def mark_recovered() -> None:
    nonlocal reconnect_count, consecutive_reconnect_failures, last_reconnect_at, next_reconnect_at, last_error
    reconnect_count += 1
    consecutive_reconnect_failures = 0
    last_reconnect_at = _now_utc_iso()
    next_reconnect_at = None
    last_error = None
    exit_degraded()
    write_status(state="running")
```

- [ ] **Step 4: Wire runtime-state fields into `build_status_payload(...)` and final summary**

```python
payload = build_subscription_watch_status_payload(
    paths=run_paths,
    state=state,
    started_at=started_at,
    updated_at=finished_at or _now_utc_iso(),
    session_id=session_id,
    event_count=current_event_count,
    last_sequence=current_event_count,
    last_event_ts=current_last_event_ts,
    last_symbol=current_last_symbol,
    warnings=[],
    heartbeat_at=heartbeat_at,
    last_source_ts=last_source_ts,
    reconnect_count=reconnect_count,
    consecutive_reconnect_failures=consecutive_reconnect_failures,
    last_disconnect_at=last_disconnect_at,
    last_reconnect_at=last_reconnect_at,
    next_reconnect_at=next_reconnect_at,
    degraded_since=degraded_since,
    last_error=last_error,
)
```

- [ ] **Step 5: Re-run the task tests and confirm they pass**

Run:

```bash
python -m pytest tests/test_api_manager.py -k "subscription_watch_enters_reconnecting or subscription_watch_enters_degraded" -q
```

Expected:

```text
2 passed
```

- [ ] **Step 6: Commit**

```bash
git add tdxquant/api/task.py tests/test_api_manager.py
git commit -m "feat: add subscription watch reconnect and degraded recovery"
```

### Task 3: Teach Background Control and Runner About New Active States

**Files:**
- Modify: `tdxquant/subscription_watch_background.py`
- Modify: `tdxquant/subscription_watch_background_runner.py`
- Test: `tests/test_subscription_watch_background.py`
- Test: `tests/test_subscription_watch_background_runner.py`
- Test: `tests/test_bridge_http.py`

- [ ] **Step 1: Write the failing reconcile and stop-cleanup tests**

```python
def test_reconcile_marks_reconnecting_process_loss_as_failed(tmp_path: Path) -> None:
    paths = build_background_paths(tmp_path)
    paths.root_dir.mkdir(parents=True, exist_ok=True)
    paths.pid_path.write_text("12345\n", encoding="utf-8")
    paths.active_path.write_text(
        json.dumps({"state": "reconnecting", "run_id": "run-001", "pid": 12345, "active": True}),
        encoding="utf-8",
    )

    reconciled = reconcile_background_state(paths, pid_is_alive=lambda pid: False)

    assert reconciled["state"] == "failed"
    assert reconciled["reason"] == "stale_process_state"


def test_status_clears_next_reconnect_at_when_stopping(tmp_path: Path) -> None:
    # build a run status payload through the controller read model
    ...
    assert payload["next_reconnect_at"] is None
```

- [ ] **Step 2: Run the focused background tests and verify they fail**

Run:

```bash
python -m pytest tests/test_subscription_watch_background.py tests/test_subscription_watch_background_runner.py tests/test_bridge_http.py -k "reconnecting or degraded or next_reconnect_at" -q
```

Expected:

```text
F...
```

- [ ] **Step 3: Expand active-process reconciliation and runner terminal persistence**

```python
# tdxquant/subscription_watch_background.py
ACTIVE_PROCESS_STATES = {"starting", "running", "reconnecting", "degraded", "stopping"}

if state in ACTIVE_PROCESS_STATES and (not pid_matches_owned_state or not pid_is_alive(payload_pid)):
    return _normalize_terminal_payload(
        paths,
        payload,
        state="stopped" if state == "stopping" else "failed",
        reason=(str(payload.get("reason") or "operator_stop") if state == "stopping" else "stale_process_state"),
    )
```

```python
# tdxquant/subscription_watch_background_runner.py
current_state = read_active_payload(paths) or {}
if current_state.get("state") == "stopping":
    terminal_state = "stopped"
    terminal_reason = str(current_state.get("reason") or "operator_stop")
elif not result.ok and current_state.get("state") == "degraded":
    terminal_state = "failed"
    terminal_reason = str(current_state.get("reason") or "degraded_unrecovered")
```

- [ ] **Step 4: Re-run the background and bridge tests and confirm they pass**

Run:

```bash
python -m pytest tests/test_subscription_watch_background.py tests/test_subscription_watch_background_runner.py tests/test_bridge_http.py -q
```

Expected:

```text
all selected tests passed
```

- [ ] **Step 5: Commit**

```bash
git add tdxquant/subscription_watch_background.py tdxquant/subscription_watch_background_runner.py tests/test_subscription_watch_background.py tests/test_subscription_watch_background_runner.py tests/test_bridge_http.py
git commit -m "feat: align background control with reconnect and degraded states"
```

### Task 4: Refresh Fixtures, Docs, and Full Regression Coverage

**Files:**
- Modify: `tdxquant/replay_fixtures.py`
- Create: `tdxquant/fixtures/provider/subscription-watch-status-reconnecting.json`
- Create: `tdxquant/fixtures/provider/subscription-watch-status-degraded.json`
- Create: `tdxquant/fixtures/provider/subscription-watch-summary-with-reconnect.json`
- Modify: `tdxquant/fixtures/provider/subscription-watch-status-completed.json`
- Modify: `tdxquant/fixtures/provider/subscription-watch-summary-completed.json`
- Modify: `tests/test_replay_fixtures.py`
- Modify: `docs/TdxQuant_Task_Subscription_Watch_Contract.md`
- Modify: `docs/TdxQuant_Project_Function_Map.md`
- Modify: `docs/TdxQuant_Next_Steps.md`

- [ ] **Step 1: Write the failing fixture-registry test for the new resilience samples**

```python
def test_replay_fixture_registry_includes_subscription_watch_resilience_variants() -> None:
    names = {fixture["name"] for fixture in list_provider_replay_fixtures()}

    assert "subscription-watch-status-reconnecting" in names
    assert "subscription-watch-status-degraded" in names
    assert "subscription-watch-summary-with-reconnect" in names
```

- [ ] **Step 2: Run the fixture test and verify it fails**

Run:

```bash
python -m pytest tests/test_replay_fixtures.py -q
```

Expected:

```text
E   AssertionError: assert 'subscription-watch-status-reconnecting' in names
```

- [ ] **Step 3: Add the resilience fixtures and register them**

```python
# tdxquant/replay_fixtures.py
{
    "name": "subscription-watch-status-reconnecting",
    "capability": "subscription.watch",
    "description": "Representative reconnecting subscription-watch status snapshot.",
    "relative_path": "subscription-watch-status-reconnecting.json",
},
{
    "name": "subscription-watch-status-degraded",
    "capability": "subscription.watch",
    "description": "Representative degraded subscription-watch status snapshot.",
    "relative_path": "subscription-watch-status-degraded.json",
},
{
    "name": "subscription-watch-summary-with-reconnect",
    "capability": "subscription.watch",
    "description": "Representative completed subscription-watch summary with reconnect history.",
    "relative_path": "subscription-watch-summary-with-reconnect.json",
},
```

- [ ] **Step 4: Update docs and run the broad resilience regression**

Run:

```bash
python -m pytest tests/test_subscription_watch_run.py tests/test_subscription_watch_background.py tests/test_subscription_watch_background_runner.py tests/test_bridge_http.py tests/test_api_manager.py tests/test_replay_fixtures.py tests/test_api_cli.py -q
```

Expected:

```text
all selected tests passed
```

- [ ] **Step 5: Commit**

```bash
git add tdxquant/replay_fixtures.py tdxquant/fixtures/provider tests/test_replay_fixtures.py docs/TdxQuant_Task_Subscription_Watch_Contract.md docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Next_Steps.md
git commit -m "docs: document subscription watch runtime resilience contract"
```

## Self-Review

- Spec coverage:
  - bounded reconnect and degraded loop: Task 2
  - same run identity and no synthetic lifecycle events: Tasks 1 and 2
  - background reconcile semantics: Task 3
  - fixture impact: Task 4
  - shared runtime-state contract across foreground/background/bridge: Tasks 1 through 3
- Placeholder scan:
  - No `TODO`/`TBD` markers remain.
  - Each code-changing step includes file-local code snippets or explicit expected edits.
- Type consistency:
  - The plan consistently uses `last_event_ts`, not `last_event_at`.
  - The plan does not introduce `runtime_health`.
  - Active-process states consistently include `reconnecting` and `degraded`.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-03-subscription-watch-runtime-resilience.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
