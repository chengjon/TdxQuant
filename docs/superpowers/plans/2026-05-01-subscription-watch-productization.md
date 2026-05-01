# Subscription Watch Productization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn `task subscription-watch` into a stable front-foreground run-artifact contract with canonical `events.jsonl`, per-run directories, stable `status.json` / `summary.json` / `manifest.json`, and replay fixtures that lock the contract.

**Architecture:** Keep the existing `subscription-watch` entrypoint, but split the artifact responsibility out of `tdxquant/api/task.py` into a small helper module that owns `run_id` directories and JSON payload builders. Keep `tdxquant/subscription_event.py` as the event-row normalizer, then refactor `TdxTaskManager.subscription_watch(...)` to write the canonical run bundle and treat legacy CSV/custom output paths as compatibility projections rather than the primary contract.

**Tech Stack:** Python 3, `pathlib`, JSON/JSONL file IO, existing `Result` envelope, unittest/pytest-style targeted tests, OpenSpec-adjacent documentation in `docs/` and replay fixtures in `tdxquant/fixtures/provider/`.

---

## File Structure

- Create: `tdxquant/subscription_watch_run.py`
  - Owns `run_id` directory resolution, canonical artifact paths, and payload builders for `manifest.json`, `status.json`, and `summary.json`.
- Modify: `tdxquant/subscription_event.py`
  - Extend normalized event rows with stable run metadata such as `capability` and `run_id`.
- Modify: `tdxquant/api/task.py`
  - Refactor `subscription_watch(...)` to use the new run helper, write canonical files, and keep compatibility projections.
- Modify: `runtime/task-profiles.json`
  - Add an explicit `run_root_dir` for `subscription_watch`.
- Modify: `tdxquant/replay_fixtures.py`
  - Register stable `subscription-watch` run artifact fixtures.
- Create:
  - `tdxquant/fixtures/provider/subscription-watch-events.jsonl`
  - `tdxquant/fixtures/provider/subscription-watch-status-completed.json`
  - `tdxquant/fixtures/provider/subscription-watch-summary-completed.json`
  - `tdxquant/fixtures/provider/subscription-watch-manifest.json`
- Modify tests:
  - `tests/test_subscription_event_contract.py`
  - `tests/test_api_manager.py`
  - `tests/test_api_cli.py`
  - `tests/test_replay_fixtures.py`
- Modify docs:
  - `docs/TdxQuant_Project_Function_Map.md`
  - `docs/TdxQuant_Provider_Replay_Fixtures.md`
  - `docs/TdxQuant_Next_Steps.md`

### Task 1: Create the Canonical Run Artifact Helper

**Files:**
- Create: `tdxquant/subscription_watch_run.py`
- Test: `tests/test_subscription_watch_run.py`

- [ ] **Step 1: Write the failing helper tests**

```python
from pathlib import Path

from tdxquant.subscription_watch_run import (
    SUBSCRIPTION_WATCH_CAPABILITY,
    SUBSCRIPTION_WATCH_SCHEMA_VERSION,
    build_subscription_watch_manifest,
    build_subscription_watch_run_paths,
    build_subscription_watch_status_payload,
    build_subscription_watch_summary_payload,
)


def test_build_subscription_watch_run_paths_uses_run_id_directory(tmp_path: Path) -> None:
    paths = build_subscription_watch_run_paths(tmp_path, run_id="run-001")

    assert paths.run_id == "run-001"
    assert paths.run_dir == tmp_path / "run-001"
    assert paths.events_jsonl_path == tmp_path / "run-001" / "events.jsonl"
    assert paths.status_path == tmp_path / "run-001" / "status.json"
    assert paths.summary_path == tmp_path / "run-001" / "summary.json"
    assert paths.manifest_path == tmp_path / "run-001" / "manifest.json"


def test_build_subscription_watch_payloads_use_stable_contract_fields(tmp_path: Path) -> None:
    paths = build_subscription_watch_run_paths(tmp_path, run_id="run-001")
    manifest = build_subscription_watch_manifest(
        paths=paths,
        provider="tongdaxin",
        provider_mode="runtime_session",
        requested_symbols=["600519.SH"],
    )
    status = build_subscription_watch_status_payload(
        paths=paths,
        state="running",
        started_at="2026-05-01T08:00:00+00:00",
        updated_at="2026-05-01T08:00:01+00:00",
        session_id="session-001",
        event_count=2,
        last_sequence=2,
        last_event_ts="2026-05-01T08:00:01+00:00",
        last_symbol="600519.SH",
        warnings=[],
    )
    summary = build_subscription_watch_summary_payload(
        paths=paths,
        final_state="completed",
        started_at="2026-05-01T08:00:00+00:00",
        finished_at="2026-05-01T08:00:05+00:00",
        elapsed_ms=5000.0,
        session_id="session-001",
        event_count=2,
        symbol_count=1,
        stop_reason="completed",
        warning_count=0,
    )

    assert manifest["schema_version"] == SUBSCRIPTION_WATCH_SCHEMA_VERSION
    assert manifest["capability"] == SUBSCRIPTION_WATCH_CAPABILITY
    assert manifest["artifacts"]["events_jsonl_path"].endswith("events.jsonl")
    assert status["output_paths"]["summary_path"].endswith("summary.json")
    assert summary["final_state"] == "completed"
    assert summary["stop_reason"] == "completed"
```

- [ ] **Step 2: Run the helper tests to verify they fail**

Run:

```bash
python -m pytest tests/test_subscription_watch_run.py -q
```

Expected:

```text
ERROR tests/test_subscription_watch_run.py
E   ModuleNotFoundError: No module named 'tdxquant.subscription_watch_run'
```

- [ ] **Step 3: Implement the minimal run helper**

```python
# tdxquant/subscription_watch_run.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SUBSCRIPTION_WATCH_SCHEMA_VERSION = "2026-05-01"
SUBSCRIPTION_WATCH_CAPABILITY = "subscription.watch"
SUBSCRIPTION_WATCH_CAPABILITY_VERSION = "1"


def _now_utc_iso() -> str:
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
        "created_at": _now_utc_iso(),
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
        "artifacts": {
            "manifest_path": str(paths.manifest_path),
            "status_path": str(paths.status_path),
            "summary_path": str(paths.summary_path),
            "events_jsonl_path": str(paths.events_jsonl_path),
            "events_csv_path": str(paths.events_csv_path),
        },
    }
```

- [ ] **Step 4: Run the helper tests to verify they pass**

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
git commit -m "feat: add subscription watch run artifact helper"
```

### Task 2: Harden the Canonical Subscription Event Row Contract

**Files:**
- Modify: `tdxquant/subscription_event.py`
- Test: `tests/test_subscription_event_contract.py`

- [ ] **Step 1: Extend the event contract tests**

```python
from tdxquant.subscription_event import normalize_subscription_event_rows


def test_normalize_subscription_event_rows_adds_run_metadata() -> None:
    rows = normalize_subscription_event_rows(
        {"code": "600519.SH", "Now": 123.45, "UpdateTime": "2026-05-01T09:30:00+08:00"},
        session_id="local-session-001",
        provider_instance_id="provider-session-001",
        subscription_id="sub-001",
        run_id="run-001",
        capability="subscription.watch",
        start_sequence=7,
    )

    assert rows[0]["run_id"] == "run-001"
    assert rows[0]["capability"] == "subscription.watch"
    assert rows[0]["sequence"] == 7
    assert rows[0]["event_type"] == "quote_update"
    assert rows[0]["reconnect_metadata"] == {}
```

- [ ] **Step 2: Run the event contract tests to verify they fail**

Run:

```bash
python -m pytest tests/test_subscription_event_contract.py -q
```

Expected:

```text
E   TypeError: normalize_subscription_event_rows() got an unexpected keyword argument 'run_id'
```

- [ ] **Step 3: Implement the event row extension**

```python
# tdxquant/subscription_event.py
SUBSCRIPTION_EVENT_SCHEMA_VERSION = "2026-05-01"
SUBSCRIPTION_EVENT_TYPE = "quote_update"
SUBSCRIPTION_EVENT_CAPABILITY = "subscription.watch"


def build_subscription_event_row(
    payload: Any,
    *,
    session_id: str,
    provider_instance_id: str,
    subscription_id: str,
    run_id: str,
    capability: str,
    sequence: int,
    symbol: str | None = None,
    source_ts: str | None = None,
) -> dict[str, Any]:
    serialized_payload = serialize_value(payload)
    resolved_symbol = symbol or extract_subscription_symbol(serialized_payload)
    resolved_source_ts = source_ts or extract_subscription_source_ts(serialized_payload)
    return {
        "schema_version": SUBSCRIPTION_EVENT_SCHEMA_VERSION,
        "capability": capability,
        "run_id": run_id,
        "session_id": session_id,
        "provider_instance_id": provider_instance_id,
        "subscription_id": subscription_id,
        "sequence": sequence,
        "event_type": SUBSCRIPTION_EVENT_TYPE,
        "symbol": resolved_symbol,
        "source_ts": resolved_source_ts,
        "event_ts": _now_utc_iso(),
        "reconnect_metadata": {},
        "payload": serialized_payload,
    }


def normalize_subscription_event_rows(
    raw_payload: Any,
    *,
    session_id: str,
    provider_instance_id: str,
    subscription_id: str,
    run_id: str,
    capability: str = SUBSCRIPTION_EVENT_CAPABILITY,
    start_sequence: int,
) -> list[dict[str, Any]]:
    ...
    rows.append(
        build_subscription_event_row(
            item,
            session_id=session_id,
            provider_instance_id=provider_instance_id,
            subscription_id=subscription_id,
            run_id=run_id,
            capability=capability,
            sequence=next_sequence,
        )
    )
```

- [ ] **Step 4: Run the event contract tests to verify they pass**

Run:

```bash
python -m pytest tests/test_subscription_event_contract.py -q
```

Expected:

```text
all passed
```

- [ ] **Step 5: Commit**

```bash
git add tdxquant/subscription_event.py tests/test_subscription_event_contract.py
git commit -m "feat: harden subscription event row contract"
```

### Task 3: Refactor `subscription_watch` to Write Canonical Run Bundles

**Files:**
- Modify: `tdxquant/api/task.py`
- Modify: `runtime/task-profiles.json`
- Test: `tests/test_api_manager.py`

- [ ] **Step 1: Add the failing task-manager tests**

```python
def test_task_subscription_watch_creates_run_artifact_bundle(self) -> None:
    fake_session = _FakeTaskRuntimeSubscriptionSession(
        events=[{"600519.SH": {"Now": 123.45, "UpdateTime": "2026-05-01T09:30:01+08:00"}}]
    )
    with TemporaryDirectory() as temp_dir:
        manager = TdxTaskManager(
            profile="subscription_watch",
            strategy_path="strategy.py",
            profile_overrides={"run_root_dir": temp_dir, "poll_interval": 0.0},
        )
        with patch.object(type(manager.api_manager.runtime), "open_subscription_session", return_value=fake_session):
            result = manager.subscription_watch(stock_list=["600519.SH"], max_events=1, poll_interval=0.0)

    artifacts = result.data["artifacts"]
    manifest_path = Path(artifacts["manifest_path"])
    status_path = Path(artifacts["status_path"])
    summary_path = Path(artifacts["summary_path"])
    jsonl_path = Path(artifacts["events_jsonl_path"])

    assert result.ok is True
    assert Path(artifacts["run_dir"]).name == result.data["subscription"]["run_id"]
    assert manifest_path.exists()
    assert status_path.exists()
    assert summary_path.exists()
    assert jsonl_path.exists()
    assert json.loads(summary_path.read_text(encoding="utf-8"))["final_state"] == "completed"


def test_task_subscription_watch_keyboard_interrupt_writes_interrupted_summary(self) -> None:
    fake_session = _FakeTaskRuntimeSubscriptionSession(events=[])
    with TemporaryDirectory() as temp_dir:
        manager = TdxTaskManager(
            profile="subscription_watch",
            strategy_path="strategy.py",
            profile_overrides={"run_root_dir": temp_dir, "poll_interval": 0.1},
        )
        with (
            patch.object(type(manager.api_manager.runtime), "open_subscription_session", return_value=fake_session),
            patch("tdxquant.api.task.time.sleep", side_effect=KeyboardInterrupt),
        ):
            result = manager.subscription_watch(stock_list=["600519.SH"], poll_interval=0.1)

    summary_path = Path(result.data["artifacts"]["summary_path"])
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["final_state"] == "interrupted"
    assert payload["stop_reason"] == "keyboard_interrupt"
```

- [ ] **Step 2: Run the task-manager tests to verify they fail**

Run:

```bash
python -m pytest tests/test_api_manager.py -q -k subscription_watch
```

Expected:

```text
E   KeyError: 'manifest_path'
```

- [ ] **Step 3: Refactor the task to use the run helper and write canonical artifacts**

```python
# runtime/task-profiles.json
"subscription_watch": {
  "api_profile": "safe_read",
  "output_format": "json",
  "run_root_dir": "runtime/subscription-watch",
  "export_dir": "runtime/exports",
  "export_stem": "subscription-watch",
  "status_stem": "subscription-watch-status",
  "poll_interval": 0.25
}
```

```python
# tdxquant/api/task.py
from ..subscription_watch_run import (
    SUBSCRIPTION_WATCH_CAPABILITY,
    build_subscription_watch_manifest,
    build_subscription_watch_run_paths,
    build_subscription_watch_status_payload,
    build_subscription_watch_summary_payload,
)


def _resolve_subscription_watch_root_dir(profile_options: dict[str, Any]) -> Path:
    root_value = profile_options.get("run_root_dir")
    if isinstance(root_value, str) and root_value.strip():
        return Path(root_value)
    return _resolve_export_dir(profile_options) / "subscription-watch"


def subscription_watch(...):
    run_root_dir = _resolve_subscription_watch_root_dir(self.profile_options)
    run_paths = build_subscription_watch_run_paths(run_root_dir)
    run_paths.run_dir.mkdir(parents=True, exist_ok=False)

    session_id = uuid4().hex
    started_at = _now_utc_iso()
    subscription_id = uuid4().hex
    provider_instance_id = str(getattr(session, "session_id", "unknown-session"))

    manifest_payload = build_subscription_watch_manifest(
        paths=run_paths,
        provider="tongdaxin",
        provider_mode="runtime_session",
        requested_symbols=subscribed_symbols,
    )
    _write_json_file(run_paths.manifest_path, manifest_payload)

    artifact_paths = {
        "run_dir": str(run_paths.run_dir),
        "manifest_path": str(run_paths.manifest_path),
        "status_path": str(run_paths.status_path),
        "summary_path": str(run_paths.summary_path),
        "events_jsonl_path": str(run_paths.events_jsonl_path),
        "events_csv_path": str(run_paths.events_csv_path),
    }

    def write_status(state: str) -> None:
        payload = build_subscription_watch_status_payload(
            paths=run_paths,
            state=state,
            started_at=started_at,
            updated_at=_now_utc_iso(),
            session_id=session_id,
            event_count=event_count,
            last_sequence=event_count,
            last_event_ts=last_event_at,
            last_symbol=last_symbol,
            warnings=[],
        )
        _write_json_file(run_paths.status_path, payload)

    rows = normalize_subscription_event_rows(
        raw_payload,
        session_id=session_id,
        provider_instance_id=provider_instance_id,
        subscription_id=subscription_id,
        run_id=run_paths.run_id,
        capability=SUBSCRIPTION_WATCH_CAPABILITY,
        start_sequence=start_sequence,
    )

    _write_json_file(
        run_paths.summary_path,
        build_subscription_watch_summary_payload(
            paths=run_paths,
            final_state="interrupted" if interrupted else "completed",
            started_at=started_at,
            finished_at=finished_at,
            elapsed_ms=(time.perf_counter() - started_monotonic) * 1000,
            session_id=session_id,
            event_count=event_count,
            symbol_count=len(unique_symbols),
            stop_reason=stop_reason,
            warning_count=0,
        ),
    )
```

- [ ] **Step 4: Run the task-manager tests to verify they pass**

Run:

```bash
python -m pytest tests/test_api_manager.py -q -k subscription_watch
```

Expected:

```text
all passed
```

- [ ] **Step 5: Commit**

```bash
git add runtime/task-profiles.json tdxquant/api/task.py tests/test_api_manager.py
git commit -m "feat: productize subscription watch run artifacts"
```

### Task 4: Add Replay Fixtures for the Run Artifact Contract

**Files:**
- Modify: `tdxquant/replay_fixtures.py`
- Create: `tdxquant/fixtures/provider/subscription-watch-events.jsonl`
- Create: `tdxquant/fixtures/provider/subscription-watch-status-completed.json`
- Create: `tdxquant/fixtures/provider/subscription-watch-summary-completed.json`
- Create: `tdxquant/fixtures/provider/subscription-watch-manifest.json`
- Test: `tests/test_replay_fixtures.py`

- [ ] **Step 1: Add failing fixture-loader tests**

```python
def test_subscription_watch_run_fixture_names_are_exposed(self) -> None:
    fixtures = list_provider_replay_fixtures()
    names = {item["name"] for item in fixtures}
    self.assertIn("subscription-watch-events", names)
    self.assertIn("subscription-watch-status-completed", names)
    self.assertIn("subscription-watch-summary-completed", names)
    self.assertIn("subscription-watch-manifest", names)


def test_load_subscription_watch_summary_fixture(self) -> None:
    payload = load_provider_replay_fixture("subscription-watch-summary-completed")
    self.assertEqual(payload["capability"], "subscription.watch")
    self.assertEqual(payload["final_state"], "completed")
    self.assertEqual(payload["stop_reason"], "max_events")
```

- [ ] **Step 2: Run the fixture tests to verify they fail**

Run:

```bash
python -m pytest tests/test_replay_fixtures.py -q
```

Expected:

```text
E   AssertionError: 'subscription-watch-summary-completed' not found in {...}
```

- [ ] **Step 3: Add the fixture assets and registry descriptors**

```python
# tdxquant/replay_fixtures.py
_PROVIDER_REPLAY_FIXTURE_REGISTRY.extend(
    [
        {
            "name": "subscription-watch-events",
            "capability": "subscription.watch",
            "format": "jsonl",
            "description": "Representative canonical subscription-watch event stream sample.",
            "relative_path": "subscription-watch-events.jsonl",
        },
        {
            "name": "subscription-watch-status-completed",
            "capability": "subscription.watch",
            "format": "json",
            "description": "Representative completed subscription-watch status snapshot.",
            "relative_path": "subscription-watch-status-completed.json",
        },
        {
            "name": "subscription-watch-summary-completed",
            "capability": "subscription.watch",
            "format": "json",
            "description": "Representative completed subscription-watch final summary.",
            "relative_path": "subscription-watch-summary-completed.json",
        },
        {
            "name": "subscription-watch-manifest",
            "capability": "subscription.watch",
            "format": "json",
            "description": "Representative subscription-watch run manifest.",
            "relative_path": "subscription-watch-manifest.json",
        },
    ]
)
```

```json
// tdxquant/fixtures/provider/subscription-watch-summary-completed.json
{
  "schema_version": "2026-05-01",
  "capability": "subscription.watch",
  "run_id": "20260501T080000000000Z",
  "final_state": "completed",
  "started_at": "2026-05-01T08:00:00+00:00",
  "finished_at": "2026-05-01T08:00:05+00:00",
  "elapsed_ms": 5000.0,
  "event_count": 2,
  "symbol_count": 1,
  "session_id": "local-session-001",
  "stop_reason": "max_events",
  "warning_count": 0,
  "artifacts": {
    "manifest_path": "runtime/subscription-watch/20260501T080000000000Z/manifest.json",
    "status_path": "runtime/subscription-watch/20260501T080000000000Z/status.json",
    "summary_path": "runtime/subscription-watch/20260501T080000000000Z/summary.json",
    "events_jsonl_path": "runtime/subscription-watch/20260501T080000000000Z/events.jsonl",
    "events_csv_path": "runtime/subscription-watch/20260501T080000000000Z/events.csv"
  }
}
```

- [ ] **Step 4: Run the fixture tests to verify they pass**

Run:

```bash
python -m pytest tests/test_replay_fixtures.py -q
```

Expected:

```text
all passed
```

- [ ] **Step 5: Commit**

```bash
git add tdxquant/replay_fixtures.py tdxquant/fixtures/provider/subscription-watch-* tests/test_replay_fixtures.py
git commit -m "feat: add subscription watch replay fixtures"
```

### Task 5: Lock the CLI/Documentation Surface and Run Final Validation

**Files:**
- Modify: `tests/test_api_cli.py`
- Modify: `docs/TdxQuant_Project_Function_Map.md`
- Modify: `docs/TdxQuant_Provider_Replay_Fixtures.md`
- Modify: `docs/TdxQuant_Next_Steps.md`

- [ ] **Step 1: Add the final CLI coverage**

```python
def test_handle_task_subscription_watch_keeps_legacy_output_overrides(self) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "task",
            "subscription-watch",
            "--code",
            "600519.SH",
            "--jsonl-output-path",
            "runtime/legacy/watch.jsonl",
            "--csv-output-path",
            "runtime/legacy/watch.csv",
            "--status-output-path",
            "runtime/legacy/watch-status.json",
        ]
    )
    expected = Result(ok=True, code=ErrorCode.OK, message="ok")
    manager = MagicMock()
    manager.subscription_watch.return_value = expected
    with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
        result = _handle_task_subcommand(args)

    assert result is expected
    manager.subscription_watch.assert_called_once_with(
        stock_list=["600519.SH"],
        max_events=None,
        max_seconds=None,
        poll_interval=None,
        jsonl_output_path="runtime/legacy/watch.jsonl",
        csv_output_path="runtime/legacy/watch.csv",
        status_output_path="runtime/legacy/watch-status.json",
    )
```

- [ ] **Step 2: Run the CLI and targeted regression suite to verify the baseline**

Run:

```bash
python -m pytest tests/test_api_cli.py tests/test_api_manager.py tests/test_subscription_event_contract.py tests/test_replay_fixtures.py tests/test_subscription_watch_run.py -q
```

Expected:

```text
all passed
```

- [ ] **Step 3: Update the docs to reflect the new canonical contract**

```markdown
<!-- docs/TdxQuant_Project_Function_Map.md -->
- `task subscription-watch`
- 每次运行创建独立 `run_id` 目录
- canonical artifacts:
  - `events.jsonl`
  - `status.json`
  - `summary.json`
  - `manifest.json`
- `CSV` 仅保留兼容导出角色
```

```markdown
<!-- docs/TdxQuant_Provider_Replay_Fixtures.md -->
- 新增 `subscription-watch-events`
- 新增 `subscription-watch-status-completed`
- 新增 `subscription-watch-summary-completed`
- 新增 `subscription-watch-manifest`
- 说明 `subscription-watch` 的 canonical 机器消费入口为 run artifact bundle
```

```markdown
<!-- docs/TdxQuant_Next_Steps.md -->
- `subscription-watch` 已收口为前台 run artifact contract
- daemon 化 `start / stop / status / list` 继续后置
```

- [ ] **Step 4: Run the final validation**

Run:

```bash
python -m pytest tests/test_api_cli.py tests/test_api_manager.py tests/test_subscription_event_contract.py tests/test_replay_fixtures.py tests/test_subscription_watch_run.py -q
```

Expected:

```text
all passed
```

If an OpenSpec change is created before implementation, also run:

```bash
openspec validate <change-name> --type change --strict
```

- [ ] **Step 5: Commit**

```bash
git add tests/test_api_cli.py docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Provider_Replay_Fixtures.md docs/TdxQuant_Next_Steps.md
git commit -m "docs: document subscription watch artifact contract"
```

## Self-Review

- Spec coverage:
  - Run directory model: Task 1 and Task 3
  - Canonical `events.jsonl`: Task 2 and Task 3
  - Stable `status.json` / `summary.json` / `manifest.json`: Task 1 and Task 3
  - Replay fixtures: Task 4
  - CLI/documentation boundary: Task 5
- Placeholder scan:
  - No unresolved placeholders or cross-task shorthand remain.
- Type consistency:
  - `run_id`, `capability`, `state`, `final_state`, `stop_reason`, and artifact path keys are used consistently across tasks.
