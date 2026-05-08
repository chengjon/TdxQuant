# Subscription Watch Bridge Integration Regression Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden the existing `subscription-watch` control plane so worker-local background state, HTTP bridge responses, master-side registry/client calls, and CLI remote-control commands all preserve the same machine contract under active, degraded, stale, auth-failure, and transport-failure conditions.

**Architecture:** Keep `subscription_watch_background.py` as the single worker-local read/write model, keep `bridge_http.py` as a thin HTTP transport shell, and keep `bridge_registry.py` plus CLI `bridge watch-*` commands as master-side clients. The work is primarily regression-oriented: add end-to-end fixtures, widen negative-path tests, and only make code changes needed to preserve the existing contract across layers.

**Tech Stack:** Python 3 standard library (`http.server`, `urllib.request`, `json`, `threading`, `pathlib`), existing bridge/background controller modules, pytest, unittest-style tests, existing CLI JSON result conventions.

---

## File Structure

- Modify: `tests/test_bridge_http.py`
  - Add HTTP projection regression for `running / reconnecting / degraded / stale_process_state` and auth negative cases.
- Modify: `tests/test_bridge_registry.py`
  - Add master-side transport normalization coverage for HTTP error payloads, invalid JSON, and connection failures.
- Modify: `tests/test_api_cli.py`
  - Add CLI remote-control regression for `bridge health`, `watch-status`, `watch-list`, `watch-artifacts`, `watch-events`, and `watch-logs`, including bridge error propagation.
- Modify if needed: `tdxquant/bridge_http.py`
  - Only to preserve controller read-model fields or normalize bridge failure payloads; do not add endpoints.
- Modify if needed: `tdxquant/bridge_registry.py`
  - Only to normalize transport failures and preserve bridge error bodies; do not add registry concepts.
- Modify if needed: `tdxquant/cli.py`
  - Only to keep CLI JSON output aligned with registry/bridge contracts; no new commands.
- Modify docs:
  - `docs/TdxQuant_Task_Subscription_Watch_Contract.md`
  - `docs/TdxQuant_Project_Function_Map.md`
  - `docs/TdxQuant_Next_Steps.md`

## Implementation Notes

- Do not add new bridge endpoints in this change.
- Do not move control logic out of `SubscriptionWatchBackgroundController`; tests should verify the bridge only projects controller output.
- Preserve the bridge envelope shape:
  - success: `{"ok": true, "result": ..., "error": null, "meta": {...}}`
  - failure: `{"ok": false, "result": null, "error": {...}, "meta": {...}}`
- Preserve resilience fields from the background/watch contract:
  - `heartbeat_at`
  - `last_event_ts`
  - `last_source_ts`
  - `reconnect_count`
  - `consecutive_reconnect_failures`
  - `last_disconnect_at`
  - `last_reconnect_at`
  - `next_reconnect_at`
  - `degraded_since`
  - `last_error`
- Treat `starting`, `running`, `reconnecting`, `degraded`, and `stopping` as active-process states. If process liveness is missing, projection must normalize to `failed` with a stale-process reason instead of inventing a new bridge-only state.
- Transport failures at the registry/client layer must never be reported as task/runtime failures. They must stay transport-scoped.

### Task 1: Lock Worker-to-Bridge State Projection and Auth Failures

**Files:**
- Modify: `tests/test_bridge_http.py`
- Modify if needed: `tdxquant/bridge_http.py`

- [ ] **Step 1: Add failing HTTP projection and auth regression tests**

```python
def test_watch_status_preserves_reconnecting_runtime_fields(self) -> None:
    with TemporaryDirectory() as temp_dir:
        controller = _FakeController()
        controller.status_result = {
            "control": {
                "state": "reconnecting",
                "active": True,
                "run_id": "run-001",
                "pid": 1234,
                "reason": None,
            },
            "watch_status": {
                "run_id": "run-001",
                "state": "reconnecting",
                "heartbeat_at": "2026-05-03T09:00:05+00:00",
                "last_event_ts": "2026-05-03T09:00:02+00:00",
                "reconnect_count": 1,
                "consecutive_reconnect_failures": 1,
                "last_error": {"code": "SESSION_LOST", "message": "session lost"},
            },
        }
        config = BridgeConfig(
            worker_id="worker-a",
            bind_host="127.0.0.1",
            port=0,
            token="secret-token",
            master_allowlist=["127.0.0.1"],
            run_root_dir=temp_dir,
        )
        server, base_url, thread = self._start_server(config, controller=controller)
        try:
            payload = self._request(f"{base_url}/bridge/v1/watch/status", token="secret-token")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    assert payload["ok"] is True
    assert payload["result"]["watch_status"]["state"] == "reconnecting"
    assert payload["result"]["watch_status"]["reconnect_count"] == 1
    assert payload["result"]["watch_status"]["last_error"]["code"] == "SESSION_LOST"


def test_watch_status_preserves_degraded_runtime_fields(self) -> None:
    ...


def test_watch_status_surfaces_stale_process_failure_projection(self) -> None:
    ...


def test_watch_status_rejects_missing_or_invalid_token_before_controller_read(self) -> None:
    ...
```

- [ ] **Step 2: Run the focused bridge HTTP suite and verify failures**

Run:

```bash
python -m pytest tests/test_bridge_http.py -q
```

Expected:

```text
FAILED tests/test_bridge_http.py::BridgeRequestHandlerTests::test_watch_status_preserves_reconnecting_runtime_fields
```

- [ ] **Step 3: Make the bridge project controller state verbatim and keep auth failures transport-scoped**

```python
# tdxquant/bridge_http.py
def _handle_watch_status(self, request_id: str) -> None:
    result = self.server.bridge_controller.status()
    self._write_json(
        200,
        build_bridge_success(
            worker_id=self.server.bridge_config.worker_id,
            request_id=request_id,
            result=result,
        ),
    )


def _handle_request(self, method: str) -> None:
    ...
    if auth_header != expected:
        self._write_json(
            401,
            build_bridge_failure(
                worker_id=config.worker_id,
                request_id=request_id,
                code="UNAUTHORIZED",
                message="missing or invalid bearer token",
            ),
        )
        return
```

- [ ] **Step 4: Re-run bridge HTTP tests and verify they pass**

Run:

```bash
python -m pytest tests/test_bridge_http.py -q
```

Expected:

```text
all passed
```

- [ ] **Step 5: Commit**

```bash
git add tests/test_bridge_http.py tdxquant/bridge_http.py
git commit -m "test: harden bridge status projection and auth failures"
```

### Task 2: Normalize Master Registry and Client Transport Failures

**Files:**
- Modify: `tests/test_bridge_registry.py`
- Modify if needed: `tdxquant/bridge_registry.py`

- [ ] **Step 1: Add failing registry/client tests for non-task transport errors**

```python
def test_call_worker_returns_bridge_json_error_body_for_http_failures(self) -> None:
    worker = BridgeWorker(
        worker_id="worker-a",
        label="A",
        host="127.0.0.1",
        port=8787,
        token_env="BRIDGE_TOKEN_A",
        role_tags=["watch"],
        enabled=True,
    )
    error_payload = {
        "ok": False,
        "result": None,
        "error": {"code": "FORBIDDEN_SOURCE", "message": "source ip is not allowed", "details": {}},
        "meta": {"worker_id": "worker-a", "request_id": "req-1"},
    }
    http_error = HTTPError(
        url="http://127.0.0.1:8787/bridge/v1/watch/status",
        code=403,
        msg="Forbidden",
        hdrs=None,
        fp=io.BytesIO(json.dumps(error_payload).encode("utf-8")),
    )

    with patch("tdxquant.bridge_registry.urlopen", side_effect=http_error):
        payload = call_worker(worker, method="GET", route="/bridge/v1/watch/status", token="secret-token")

    assert payload == error_payload


def test_call_worker_raises_runtime_error_for_invalid_json_success_body(self) -> None:
    ...


def test_call_worker_raises_runtime_error_for_connection_refused(self) -> None:
    ...
```

- [ ] **Step 2: Run the registry suite and confirm failures**

Run:

```bash
python -m pytest tests/test_bridge_registry.py -q
```

Expected:

```text
FAILED tests/test_bridge_registry.py::BridgeRegistryTests::test_call_worker_raises_runtime_error_for_invalid_json_success_body
```

- [ ] **Step 3: Normalize bridge client failure paths without changing route semantics**

```python
# tdxquant/bridge_registry.py
def call_worker(
    worker: BridgeWorker,
    *,
    method: str,
    route: str,
    token: str,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    request = Request(...)
    try:
        with urlopen(request, timeout=5.0) as response:
            raw = response.read().decode("utf-8")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError("bridge worker returned invalid JSON payload") from exc
        if not isinstance(payload, dict):
            raise RuntimeError("bridge worker returned non-object JSON payload")
        return payload
    except HTTPError as exc:
        error_payload = _try_read_json_error_body(exc)
        if error_payload is not None:
            return error_payload
        raise RuntimeError(f"bridge worker request failed with HTTP {exc.code}: {exc.reason}") from exc
    except URLError as exc:
        raise RuntimeError(f"bridge worker request failed: {exc.reason}") from exc
```

- [ ] **Step 4: Re-run registry tests and verify they pass**

Run:

```bash
python -m pytest tests/test_bridge_registry.py -q
```

Expected:

```text
all passed
```

- [ ] **Step 5: Commit**

```bash
git add tests/test_bridge_registry.py tdxquant/bridge_registry.py
git commit -m "test: normalize bridge registry transport failures"
```

### Task 3: Lock CLI Remote-Control JSON Contract Across Status, List, and Artifact Reads

**Files:**
- Modify: `tests/test_api_cli.py`
- Modify if needed: `tdxquant/cli.py`

- [ ] **Step 1: Add failing CLI regression tests for remote-control reads**

```python
def test_handle_bridge_watch_list_dispatches_registry_client(self) -> None:
    args = build_parser().parse_args(
        ["bridge", "watch-list", "--registry", "runtime/bridge/master-workers.json", "--worker", "worker-a"]
    )
    expected = {
        "ok": True,
        "result": {
            "active": {"run_id": "run-001", "state": "degraded"},
            "last_completed": {"run_id": "run-000"},
            "last_failed": None,
        },
    }
    with (
        patch("tdxquant.cli.run_bridge_watch_list", return_value=expected) as mocked_run,
        patch("sys.stdout", new_callable=io.StringIO) as stdout,
    ):
        exit_code = _handle_bridge_subcommand(args)

    assert exit_code == 0
    mocked_run.assert_called_once_with(registry_path="runtime/bridge/master-workers.json", worker_id="worker-a")
    assert json.loads(stdout.getvalue()) == expected


def test_handle_bridge_watch_artifacts_dispatches_registry_client(self) -> None:
    ...


def test_handle_bridge_watch_events_dispatches_registry_client(self) -> None:
    ...


def test_handle_bridge_watch_logs_dispatches_registry_client(self) -> None:
    ...


def test_handle_bridge_health_dispatches_registry_client(self) -> None:
    ...


def test_handle_bridge_watch_status_preserves_bridge_error_payload(self) -> None:
    ...
```

- [ ] **Step 2: Run the focused CLI bridge tests and confirm failures**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "bridge and (watch_list or watch_artifacts or watch_events or watch_logs or bridge_health)" -q
```

Expected:

```text
FAILED tests/test_api_cli.py::...::test_handle_bridge_watch_list_dispatches_registry_client
```

- [ ] **Step 3: Add/normalize CLI bridge read handlers without changing command names**

```python
# tdxquant/cli.py
def _handle_bridge_subcommand(args: argparse.Namespace) -> int:
    ...
    if args.bridge_command == "watch-list":
        payload = run_bridge_watch_list(registry_path=args.registry, worker_id=args.worker)
        print(json.dumps(payload, ensure_ascii=False))
        return 0 if payload.get("ok", False) else 1
    if args.bridge_command == "watch-artifacts":
        payload = run_bridge_watch_artifacts(registry_path=args.registry, worker_id=args.worker)
        print(json.dumps(payload, ensure_ascii=False))
        return 0 if payload.get("ok", False) else 1
    if args.bridge_command == "watch-events":
        payload = run_bridge_watch_events(registry_path=args.registry, worker_id=args.worker)
        print(json.dumps(payload, ensure_ascii=False))
        return 0 if payload.get("ok", False) else 1
    if args.bridge_command == "watch-logs":
        payload = run_bridge_watch_logs(registry_path=args.registry, worker_id=args.worker)
        print(json.dumps(payload, ensure_ascii=False))
        return 0 if payload.get("ok", False) else 1
```

- [ ] **Step 4: Re-run focused CLI bridge tests and verify they pass**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "bridge and (watch_list or watch_artifacts or watch_events or watch_logs or bridge_health)" -q
```

Expected:

```text
all passed
```

- [ ] **Step 5: Commit**

```bash
git add tests/test_api_cli.py tdxquant/cli.py
git commit -m "test: harden bridge remote-control CLI contract"
```

### Task 4: Refresh Control-Plane Docs and Run the End-to-End Regression Suite

**Files:**
- Modify: `docs/TdxQuant_Task_Subscription_Watch_Contract.md`
- Modify: `docs/TdxQuant_Project_Function_Map.md`
- Modify: `docs/TdxQuant_Next_Steps.md`
- Verify: `tests/test_bridge_http.py`
- Verify: `tests/test_bridge_registry.py`
- Verify: `tests/test_api_cli.py`
- Verify: `tests/test_subscription_watch_background.py`

- [ ] **Step 1: Document the stabilized bridge integration contract**

```md
## Bridge Integration Regression Surface

- Worker-local background control remains the source of truth for watch runtime state.
- HTTP bridge only projects controller output and never invents a bridge-only watch state.
- Master-side registry/client errors are transport-scoped (`invalid JSON`, `connection refused`, `HTTP non-JSON failure`) and must not be interpreted as task runtime failures.
- CLI `bridge watch-status/list/artifacts/events/logs` returns the same JSON payload the master-side client received.
```

- [ ] **Step 2: Run the focused regression suite**

Run:

```bash
python -m pytest tests/test_bridge_http.py tests/test_bridge_registry.py tests/test_api_cli.py -k "bridge" -q
```

Expected:

```text
all passed
```

- [ ] **Step 3: Run the broader background + bridge suite**

Run:

```bash
python -m pytest tests/test_subscription_watch_background.py tests/test_bridge_http.py tests/test_bridge_registry.py tests/test_api_cli.py -q
```

Expected:

```text
all passed
```

- [ ] **Step 4: Check patch hygiene**

Run:

```bash
git diff --check
```

Expected:

```text
# no output
```

- [ ] **Step 5: Commit**

```bash
git add docs/TdxQuant_Task_Subscription_Watch_Contract.md docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Next_Steps.md
git commit -m "docs: document bridge integration regression contract"
```

## Self-Review

- Spec coverage:
  - Worker-local → bridge status projection: Task 1
  - Auth / allowlist negative paths: Task 1
  - Registry/client transport normalization: Task 2
  - CLI remote-control projection: Task 3
  - Docs and end-to-end regression verification: Task 4
- Placeholder scan:
  - No `TODO`/`TBD`
  - Each task has explicit files, test commands, and implementation snippets
- Type consistency:
  - Uses existing bridge envelope fields `ok/result/error/meta`
  - Uses existing worker/runtime state names `running/reconnecting/degraded/failed`
  - Keeps registry/client contract in `dict[str, Any]` JSON payload form

