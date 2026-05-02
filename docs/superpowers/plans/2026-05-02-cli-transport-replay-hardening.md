# CLI Transport Replay Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden `tdxquant ... --provider-mode replay` into a stable CLI subprocess transport contract for supported nested `api`, flat provider commands, and `task subscription-watch`.

**Architecture:** Keep replay execution on the existing formal entrypoints, but add a centralized CLI replay policy in `tdxquant/cli.py` that enforces the supported-command matrix, selector rules, normalized failure payloads, and stdout/output mirroring. Preserve `tdxquant/replay_provider.py` as the fixture/materialization layer and make `TdxTaskManager.subscription_watch(...)` return stable replay failures instead of leaking replay bundle exceptions.

**Tech Stack:** Python 3, `argparse`, existing `Result` envelope, JSON file IO, pytest/unittest-style targeted tests, replay fixtures under `tdxquant/fixtures/provider/`, and project docs under `docs/`.

---

## File Structure

- Modify: `tdxquant/cli.py`
  - Add explicit replay support-matrix helpers for nested `api` and flat commands.
  - Add a reusable CLI replay failure-result builder.
  - Keep `_run_flat_replay_provider_command(...)` as the flat replay dispatch point and harden its failure outputs.
- Modify: `tdxquant/api/task.py`
  - Catch `subscription-watch` replay materialization failures and return stable `Result` failures with replay metadata instead of propagating exceptions.
- Modify: `tests/test_api_cli.py`
  - Lock nested `api` replay support matrix, flat replay failure shape, and `--output` mirroring contract.
- Modify: `tests/test_api_manager.py`
  - Lock successful `subscription-watch` replay artifact aliases and failed replay-bundle materialization behavior.
- Modify: `docs/TdxQuant_Provider_Replay_Fixtures.md`
  - Document CLI subprocess replay support matrix, selector algorithm, and no-live-fallback semantics.
- Modify: `docs/TdxQuant_Task_Subscription_Watch_Contract.md`
  - Document replay-mode artifact aliases and failure behavior for `subscription-watch`.
- Modify: `docs/TdxQuant_Next_Steps.md`
  - Mark CLI transport replay hardening as completed groundwork once the code lands.

## Task 1: Add Explicit CLI Replay Support Matrix For Nested `api`

**Files:**
- Modify: `tests/test_api_cli.py`
- Modify: `tdxquant/cli.py`

- [ ] **Step 1: Write the failing nested replay support-matrix tests**

```python
# tests/test_api_cli.py
def test_handle_api_snapshot_replay_rejects_unsupported_command_before_manager_construction(self) -> None:
    parser = build_parser()
    args = parser.parse_args(
        ["api", "snapshot", "--code", "000001.SZ", "--provider-mode", "replay"]
    )
    with patch("tdxquant.cli.TdxApiManager") as mocked_manager:
        result = _handle_api_subcommand(args)

    self.assertFalse(result.ok)
    self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
    self.assertEqual(result.message, "unsupported replay api command: snapshot")
    self.assertEqual(result.data["replay_source"]["mode"], "replay")
    self.assertEqual(result.data["replay_source"]["capability"], "market.snapshot")
    mocked_manager.assert_not_called()


def test_handle_api_send_user_block_replay_uses_replay_manager_configuration(self) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "api",
            "send-user-block",
            "--block-code",
            "ZXG",
            "--stock",
            "000001",
            "--provider-mode",
            "replay",
            "--fixture",
            "block-send-user-block-noop",
        ]
    )
    fake_result = Result(ok=True, code=ErrorCode.OK, message="noop", data={"block_mutation": {"status": "noop"}})
    fake_manager = MagicMock()
    fake_manager.block.send_user_block.return_value = fake_result

    with patch("tdxquant.cli.TdxApiManager", return_value=fake_manager) as mocked_manager:
        result = _handle_api_subcommand(args)

    self.assertTrue(result.ok)
    mocked_manager.assert_called_once_with(
        profile="default",
        strategy_path=None,
        provider_mode="replay",
        replay_fixture="block-send-user-block-noop",
        replay_fixture_path=None,
    )
```

- [ ] **Step 2: Run the targeted CLI tests to confirm failure**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "snapshot_replay_rejects_unsupported or send_user_block_replay_uses_replay_manager_configuration" -q
```

Expected:

```text
FAILED tests/test_api_cli.py::ApiCliDispatchTests::test_handle_api_snapshot_replay_rejects_unsupported_command_before_manager_construction
```

The current code constructs `TdxApiManager` for all nested `api` replay commands and returns a lower-level unsupported-capability failure instead of an explicit CLI support-matrix failure.

- [ ] **Step 3: Add explicit nested replay support helpers in `tdxquant/cli.py`**

```python
# tdxquant/cli.py
_SUPPORTED_API_REPLAY_COMMANDS = {
    "capabilities": "runtime.capabilities",
    "health": "runtime.health",
    "doctor": "runtime.doctor",
    "formula-screen": "formula.screen",
    "send-user-block": "block.send_user_block",
}


def _infer_api_capability_name(args: argparse.Namespace) -> str:
    if args.api_command == "snapshot":
        return "market.snapshot"
    if args.api_command == "send-user-block":
        return "block.send_user_block"
    if args.api_command == "formula-screen":
        return "formula.screen"
    return f"api.{args.api_command}"


def _build_cli_replay_failure_result(*, capability: str, message: str) -> Result:
    return Result(
        ok=False,
        code=ErrorCode.INVALID_REQUEST,
        message=message,
        data={
            "replay_source": {
                "mode": "replay",
                "capability": capability,
            }
        },
    )


def _reject_unsupported_api_replay(args: argparse.Namespace) -> Result | None:
    if getattr(args, "provider_mode", "live") != "replay":
        return None
    if args.api_command in _SUPPORTED_API_REPLAY_COMMANDS:
        return None
    return _build_cli_replay_failure_result(
        capability=_infer_api_capability_name(args),
        message=f"unsupported replay api command: {args.api_command}",
    )
```

And call it before constructing `TdxApiManager`:

```python
def _handle_api_subcommand(args: argparse.Namespace) -> Result:
    replay_guard = _reject_unsupported_api_replay(args)
    if replay_guard is not None:
        return replay_guard
    try:
        manager_kwargs = {"profile": args.profile, "strategy_path": args.strategy_path}
        ...
```

- [ ] **Step 4: Re-run the targeted CLI tests**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "snapshot_replay_rejects_unsupported or send_user_block_replay_uses_replay_manager_configuration" -q
```

Expected:

```text
2 passed
```

- [ ] **Step 5: Commit Task 1**

```bash
git add tests/test_api_cli.py tdxquant/cli.py
git commit -m "feat: add explicit nested api replay support matrix"
```

## Task 2: Return Stable `subscription-watch` Replay Failures And Lock Artifact Aliases

**Files:**
- Modify: `tests/test_api_manager.py`
- Modify: `tdxquant/api/task.py`

- [ ] **Step 1: Write the failing replay-task tests**

```python
# tests/test_api_manager.py
def test_task_subscription_watch_replay_mode_keeps_artifact_aliases(self) -> None:
    with TemporaryDirectory() as temp_dir:
        manager = TdxTaskManager(
            profile="subscription_watch",
            strategy_path="strategy.py",
            profile_overrides={"run_root_dir": temp_dir},
            provider_mode="replay",
        )
        result = manager.subscription_watch(stock_list=["600519.SH"])

    self.assertTrue(result.ok)
    artifacts = result.data["artifacts"]
    self.assertIn("events_csv_path", artifacts)
    self.assertIn("jsonl_output_path", artifacts)
    self.assertIn("csv_output_path", artifacts)
    self.assertIn("status_output_path", artifacts)
    self.assertEqual(artifacts["jsonl_output_path"], artifacts["events_jsonl_path"])
    self.assertEqual(artifacts["csv_output_path"], artifacts["events_csv_path"])
    self.assertEqual(artifacts["status_output_path"], artifacts["status_path"])


def test_task_subscription_watch_replay_mode_rejects_incomplete_source_directory_without_live_session(self) -> None:
    with TemporaryDirectory() as temp_dir:
        source_dir = Path(temp_dir) / "broken-run"
        source_dir.mkdir()
        (source_dir / "manifest.json").write_text("{}", encoding="utf-8")
        (source_dir / "status.json").write_text("{}", encoding="utf-8")
        (source_dir / "summary.json").write_text("{}", encoding="utf-8")
        manager = TdxTaskManager(
            profile="subscription_watch",
            strategy_path="strategy.py",
            profile_overrides={"run_root_dir": str(Path(temp_dir) / "output")},
            provider_mode="replay",
            replay_fixture_path=str(source_dir),
        )

        with patch.object(type(manager.api_manager.runtime), "open_subscription_session") as mocked_open:
            result = manager.subscription_watch(stock_list=["600519.SH"])

    self.assertFalse(result.ok)
    self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
    self.assertEqual(result.data["replay_source"]["mode"], "replay")
    self.assertEqual(result.data["replay_source"]["capability"], "subscription.watch")
    mocked_open.assert_not_called()
```

- [ ] **Step 2: Run the replay-task tests to confirm failure**

Run:

```bash
python -m pytest tests/test_api_manager.py -k "subscription_watch_replay_mode_keeps_artifact_aliases or subscription_watch_replay_mode_rejects_incomplete_source_directory_without_live_session" -q
```

Expected:

```text
FAILED tests/test_api_manager.py::ApiManagerTaskTests::test_task_subscription_watch_replay_mode_rejects_incomplete_source_directory_without_live_session
E   ValueError: replay subscription-watch source is missing required file: ...
```

The current replay task path lets replay bundle loader exceptions escape instead of returning a stable `Result` failure.

- [ ] **Step 3: Catch replay materialization failures in `tdxquant/api/task.py`**

```python
# tdxquant/api/task.py
if getattr(self.api_manager, "provider_mode", "live") == "replay":
    try:
        materialized = materialize_subscription_watch_replay(
            paths=run_paths,
            replay_fixture=getattr(self.api_manager, "replay_fixture", None),
            replay_fixture_path=getattr(self.api_manager, "replay_fixture_path", None),
        )
    except ValueError as exc:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message=str(exc),
            data={
                "replay_source": {
                    "mode": "replay",
                    "capability": "subscription.watch",
                }
            },
        )
```

Keep the existing success payload intact, including:

```python
artifact_paths = {
    "run_dir": str(run_paths.run_dir),
    "manifest_path": str(run_paths.manifest_path),
    "status_path": str(run_paths.status_path),
    "summary_path": str(run_paths.summary_path),
    "events_jsonl_path": str(run_paths.events_jsonl_path),
    "events_csv_path": str(run_paths.events_csv_path),
    "jsonl_output_path": str(legacy_jsonl_path or run_paths.events_jsonl_path),
    "csv_output_path": str(legacy_csv_path or run_paths.events_csv_path),
    "status_output_path": str(legacy_status_path or run_paths.status_path),
}
```

- [ ] **Step 4: Re-run the replay-task tests**

Run:

```bash
python -m pytest tests/test_api_manager.py -k "subscription_watch_replay_mode_keeps_artifact_aliases or subscription_watch_replay_mode_rejects_incomplete_source_directory_without_live_session" -q
```

Expected:

```text
2 passed
```

- [ ] **Step 5: Commit Task 2**

```bash
git add tests/test_api_manager.py tdxquant/api/task.py
git commit -m "fix: normalize subscription watch replay failures"
```

## Task 3: Harden Flat Replay Failure Results And Lock `--output` Mirroring

**Files:**
- Modify: `tests/test_api_cli.py`
- Modify: `tdxquant/cli.py`

- [ ] **Step 1: Write the failing flat-replay and output tests**

```python
# tests/test_api_cli.py
def test_run_flat_replay_provider_command_returns_replay_source_for_unsupported_command(self) -> None:
    args = argparse.Namespace(
        command="tdx-data-kline",
        provider_mode="replay",
        strategy_path=None,
        fixture=None,
        fixture_path=None,
    )

    result = _run_flat_replay_provider_command(args)

    self.assertFalse(result.ok)
    self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
    self.assertEqual(result.data["replay_source"]["mode"], "replay")
    self.assertEqual(result.data["replay_source"]["capability"], "tdx-data-kline")


def test_main_api_snapshot_replay_output_file_matches_stdout_json(self) -> None:
    with TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "snapshot.json"
        stdout_buffer = io.StringIO()
        with patch("sys.argv", [
            "tdxquant",
            "api",
            "snapshot",
            "--code",
            "000001.SZ",
            "--provider-mode",
            "replay",
            "--output",
            str(output_path),
        ]), patch("sys.stdout", stdout_buffer):
            exit_code = main()

        stdout_payload = json.loads(stdout_buffer.getvalue())
        file_payload = json.loads(output_path.read_text(encoding="utf-8"))

    self.assertEqual(exit_code, 1)
    self.assertEqual(stdout_payload, file_payload)
    self.assertEqual(stdout_payload["data"]["replay_source"]["mode"], "replay")
```

- [ ] **Step 2: Run the targeted CLI transport tests to confirm failure**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "run_flat_replay_provider_command_returns_replay_source_for_unsupported_command or main_api_snapshot_replay_output_file_matches_stdout_json" -q
```

Expected:

```text
FAILED tests/test_api_cli.py::ApiCliDispatchTests::test_run_flat_replay_provider_command_returns_replay_source_for_unsupported_command
```

The current flat replay helper returns `unsupported replay flat command` without `data.replay_source`.

- [ ] **Step 3: Reuse the shared CLI replay failure builder for flat commands**

```python
# tdxquant/cli.py
def _run_flat_replay_provider_command(args: argparse.Namespace) -> Result | None:
    if getattr(args, "provider_mode", "live") != "replay":
        return None
    try:
        manager = TdxApiManager(
            profile="default",
            strategy_path=getattr(args, "strategy_path", None),
            provider_mode="replay",
            replay_fixture=getattr(args, "fixture", None),
            replay_fixture_path=getattr(args, "fixture_path", None),
        )
    except ValueError as exc:
        return _build_cli_replay_failure_result(
            capability=str(args.command),
            message=str(exc),
        )
    ...
    return _build_cli_replay_failure_result(
        capability=str(args.command),
        message=f"unsupported replay flat command: {args.command}",
    )
```

Do not change the main serialization path:

```python
serialized = json.dumps(output_payload, ensure_ascii=False, indent=2)
if getattr(args, "output", None):
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(serialized + "\n", encoding="utf-8")
print(serialized)
```

The test is intended to lock that current mirroring behavior.

- [ ] **Step 4: Re-run the targeted CLI transport tests**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "run_flat_replay_provider_command_returns_replay_source_for_unsupported_command or main_api_snapshot_replay_output_file_matches_stdout_json" -q
```

Expected:

```text
2 passed
```

- [ ] **Step 5: Commit Task 3**

```bash
git add tests/test_api_cli.py tdxquant/cli.py
git commit -m "fix: normalize flat replay failure transport payloads"
```

## Task 4: Update Replay Transport Docs And Run Focused Verification

**Files:**
- Modify: `docs/TdxQuant_Provider_Replay_Fixtures.md`
- Modify: `docs/TdxQuant_Task_Subscription_Watch_Contract.md`
- Modify: `docs/TdxQuant_Next_Steps.md`

- [ ] **Step 1: Write the documentation deltas**

```markdown
<!-- docs/TdxQuant_Provider_Replay_Fixtures.md -->
## CLI subprocess replay contract

Supported nested `api` replay commands:

- `api capabilities`
- `api health`
- `api doctor`
- `api formula-screen`
- `api send-user-block`

Supported flat replay commands:

- `tdx-capabilities`
- `tdx-health`
- `tdx-doctor`
- `tdx-formula-screen`
- `tdx-send-user-block`

Selector algorithm:

1. `--fixture-path`
2. `--fixture`
3. capability default fixture

Failure rules:

- no silent fallback to live
- stdout always carries the JSON result
- `--output` mirrors the same JSON to file
```

```markdown
<!-- docs/TdxQuant_Task_Subscription_Watch_Contract.md -->
Replay-mode `subscription-watch` returns:

- canonical artifact paths:
  - `run_dir`
  - `manifest_path`
  - `status_path`
  - `summary_path`
  - `events_jsonl_path`
  - `events_csv_path`
- compatibility aliases:
  - `jsonl_output_path`
  - `csv_output_path`
  - `status_output_path`

If the replay bundle is malformed or incomplete, the task returns `invalid_request`
with `data.replay_source.mode = "replay"` and does not open a live runtime session.
```

```markdown
<!-- docs/TdxQuant_Next_Steps.md -->
CLI subprocess replay transport contract is now hardened for the supported provider-facing commands.
Remaining replay work is transport-level HTTP/SSE follow-up, not basic CLI contract stabilization.
```

- [ ] **Step 2: Run the focused verification suite**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "replay or subscription_watch" -q
python -m pytest tests/test_api_manager.py -k "subscription_watch_replay_mode" -q
```

Expected:

```text
<all selected tests pass>
```

- [ ] **Step 3: Run the full targeted replay regression set**

Run:

```bash
python -m pytest \
  tests/test_api_cli.py \
  tests/test_api_manager.py \
  tests/test_replay_provider.py \
  tests/test_replay_fixtures.py \
  tests/test_subscription_watch_run.py \
  tests/test_provider_result_contract.py \
  -q
```

Expected:

```text
<all selected tests pass>
```

- [ ] **Step 4: Spot-check docs and collect final diff**

Run:

```bash
git diff -- docs/TdxQuant_Provider_Replay_Fixtures.md docs/TdxQuant_Task_Subscription_Watch_Contract.md docs/TdxQuant_Next_Steps.md
git status --short
```

Expected:

```text
Only the intended replay transport files and tests are modified for this plan slice.
```

- [ ] **Step 5: Commit Task 4**

```bash
git add \
  docs/TdxQuant_Provider_Replay_Fixtures.md \
  docs/TdxQuant_Task_Subscription_Watch_Contract.md \
  docs/TdxQuant_Next_Steps.md \
  tests/test_api_cli.py \
  tests/test_api_manager.py \
  tests/test_replay_provider.py \
  tdxquant/cli.py \
  tdxquant/api/task.py
git commit -m "docs: document CLI replay transport contract"
```

## Spec Coverage Check

- Supported replay command matrix: covered by Task 1 and Task 3.
- Fixture selection algorithm and `--output` semantics: covered by Task 3 and Task 4.
- `subscription-watch` artifact discovery and replay failure normalization: covered by Task 2 and Task 4.
- No-live-fallback and stable failure payloads: covered by Task 1, Task 2, and Task 3.

## Placeholder Scan

- No `TBD`, `TODO`, or deferred “implement later” instructions remain.
- Each task includes exact files, concrete test code, exact commands, and a commit step.

## Type Consistency Check

- Replay metadata uses `data.replay_source.mode` and `data.replay_source.capability` consistently across tasks.
- Supported command naming is consistent between design and test snippets:
  - flat: `tdx-capabilities`, `tdx-health`, `tdx-doctor`, `tdx-formula-screen`, `tdx-send-user-block`
  - nested: `api capabilities`, `api health`, `api doctor`, `api formula-screen`, `api send-user-block`
