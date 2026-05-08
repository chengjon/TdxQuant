# Task Block Read Watchlist Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a thin `task block-read-watchlist` entrypoint that reuses the existing provider-level `block.read_watchlist_snapshot` capability without redefining its machine contract.

**Architecture:** Keep the task layer deliberately thin. Add `TdxTaskManager.block_read_watchlist(...)` as a direct wrapper around `TdxApiManager.block.read_watchlist_snapshot(...)` using the existing `_capture_task_timing(...)` + `_attach_task_metadata(...)` pattern, wire `tdxquant task block-read-watchlist ...` into the CLI, and document the usage. Do not add file export, preset, catalog, or task-only artifact formats.

**Tech Stack:** Python 3, existing `TdxTaskManager` / `TdxApiManager`, argparse CLI, unittest/pytest suites, existing Result/error contract.

---

## File Structure

- Modify: `tdxquant/api/task.py`
  - Add `TdxTaskManager.block_read_watchlist(...)` as a thin task wrapper that forwards directly to `self.api_manager.block.read_watchlist_snapshot(...)` and attaches standard task metadata.
- Modify: `tdxquant/cli.py`
  - Add `task block-read-watchlist` parser wiring with a required `--block-code`.
  - Add task-subcommand dispatch that calls `manager.block_read_watchlist(...)`.
- Modify: `tests/test_api_manager.py`
  - Add focused task-manager tests that verify forwarding and task metadata without re-testing snapshot normalization.
- Modify: `tests/test_api_cli.py`
  - Add parser and dispatch tests for `task block-read-watchlist`.
- Modify: `runtime/TdxQuant_Task_Layer_Usage.md`
  - Add a usage section for `task block-read-watchlist`.
- Modify: `docs/TdxQuant_Project_Function_Map.md`
  - Add the new task entry to the task-layer inventory.
- Modify: `docs/TdxQuant_Next_Steps.md`
  - Update roadmap text so `block.read_watchlist_snapshot` has a thin task follow-up recorded alongside `block sync`.

## Task 1: Add `TdxTaskManager.block_read_watchlist(...)`

**Files:**
- Modify: `tdxquant/api/task.py`
- Test: `tests/test_api_manager.py`

- [ ] **Step 1: Write the failing task-manager tests**

Add these tests near the other `TdxTaskManagerTests` in `tests/test_api_manager.py`:

```python
def test_task_block_read_watchlist_uses_provider_snapshot_and_attaches_task_metadata(self) -> None:
    expected = Result(
        ok=True,
        code=ErrorCode.OK,
        message="normalized block snapshot",
        data={"snapshot": {"block_code": "ZXG", "symbols": ["600519.SH"]}},
    )
    manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
    with patch.object(
        type(manager.api_manager.block),
        "read_watchlist_snapshot",
        return_value=expected,
    ) as mocked_snapshot:
        result = manager.block_read_watchlist(block_code="ZXG")

    mocked_snapshot.assert_called_once_with(block_code="ZXG")
    assert result is expected
    assert result.data["task"]["name"] == "block_read_watchlist"
    assert result.data["task_profile"]["name"] == "default"
    assert "task_call" in result.data["timing"]


def test_task_block_read_watchlist_preserves_provider_failure_contract(self) -> None:
    expected = Result(
        ok=False,
        code=ErrorCode.INVALID_REQUEST,
        message="block_code not found: ZXG",
        data={},
    )
    manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
    with patch.object(
        type(manager.api_manager.block),
        "read_watchlist_snapshot",
        return_value=expected,
    ):
        result = manager.block_read_watchlist(block_code="ZXG")

    assert result is expected
    assert result.data["task"]["name"] == "block_read_watchlist"
```

- [ ] **Step 2: Run the focused manager tests and verify they fail**

Run:

```bash
python -m pytest tests/test_api_manager.py -k "task_block_read_watchlist" -q
```

Expected:

```text
FAILED tests/test_api_manager.py::TdxTaskManagerTests::test_task_block_read_watchlist_uses_provider_snapshot_and_attaches_task_metadata
```

- [ ] **Step 3: Add the minimal task-manager implementation**

Add this method in `tdxquant/api/task.py` near `block_sync(...)` and `watchlist_overview(...)`:

```python
def block_read_watchlist(
    self,
    *,
    block_code: str,
) -> Result:
    result, timing = _capture_task_timing(
        "task.block_read_watchlist",
        lambda: self.api_manager.block.read_watchlist_snapshot(block_code=block_code),
    )
    return self._attach_task_metadata(result, task_name="block_read_watchlist", timing=timing)
```

- [ ] **Step 4: Re-run the focused manager tests and verify they pass**

Run:

```bash
python -m pytest tests/test_api_manager.py -k "task_block_read_watchlist" -q
```

Expected:

```text
2 passed
```

- [ ] **Step 5: Commit**

```bash
git add tdxquant/api/task.py tests/test_api_manager.py
git commit -m "feat: add task block read watchlist manager wrapper"
```

## Task 2: Add `task block-read-watchlist` CLI wiring

**Files:**
- Modify: `tdxquant/cli.py`
- Test: `tests/test_api_cli.py`

- [ ] **Step 1: Write the failing CLI parser and dispatch tests**

Add these tests near the other task parser/dispatch tests in `tests/test_api_cli.py`:

```python
def test_task_block_read_watchlist_command_parses(self) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "task",
            "block-read-watchlist",
            "--block-code",
            "ZXG",
        ]
    )
    self.assertEqual(args.command, "task")
    self.assertEqual(args.task_command, "block-read-watchlist")
    self.assertEqual(args.block_code, "ZXG")


def test_handle_task_block_read_watchlist_uses_task_manager(self) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "task",
            "block-read-watchlist",
            "--block-code",
            "ZXG",
        ]
    )
    expected = Result(ok=True, code=ErrorCode.OK, message="ok")
    manager = MagicMock()
    manager.block_read_watchlist.return_value = expected
    with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
        result = _handle_task_subcommand(args)

    self.assertIs(result, expected)
    manager.block_read_watchlist.assert_called_once_with(block_code="ZXG")
```

- [ ] **Step 2: Run the focused CLI tests and verify they fail**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "task_block_read_watchlist" -q
```

Expected:

```text
FAILED tests/test_api_cli.py::...::test_task_block_read_watchlist_command_parses
```

- [ ] **Step 3: Add the minimal CLI parser and dispatch**

In `tdxquant/cli.py`:

1. Add a new task parser next to `task block-sync`:

```python
task_block_read_watchlist_parser = task_subparsers.add_parser("block-read-watchlist")
task_block_read_watchlist_parser.add_argument("--block-code", required=True)
_add_task_common_arguments(task_block_read_watchlist_parser)
```

2. Add a task dispatch branch near `if args.task_command == "block-sync":`:

```python
if args.task_command == "block-read-watchlist":
    return manager.block_read_watchlist(block_code=args.block_code)
```

- [ ] **Step 4: Re-run the focused CLI tests and verify they pass**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "task_block_read_watchlist" -q
```

Expected:

```text
2 passed
```

- [ ] **Step 5: Commit**

```bash
git add tdxquant/cli.py tests/test_api_cli.py
git commit -m "feat: add task block read watchlist cli entry"
```

## Task 3: Update task-layer docs

**Files:**
- Modify: `runtime/TdxQuant_Task_Layer_Usage.md`
- Modify: `docs/TdxQuant_Project_Function_Map.md`
- Modify: `docs/TdxQuant_Next_Steps.md`

- [ ] **Step 1: Write the doc updates**

Add a `task block-read-watchlist` section to `runtime/TdxQuant_Task_Layer_Usage.md` with an example like:

```bash
python -m tdxquant.cli task block-read-watchlist \
  --block-code ZXG \
  --profile default
```

Document:
- it is a thin wrapper over `manager.block.read_watchlist_snapshot(...)`
- it returns the provider `data.snapshot` contract unchanged
- task metadata is attached in the usual `data.task / data.task_profile / data.timing` fields

Update `docs/TdxQuant_Project_Function_Map.md` so the task inventory includes:

```text
- block_read_watchlist
```

and add a short note near the block task discussion that `block_read_watchlist` is the read-side thin task counterpart to `block_sync`.

Update `docs/TdxQuant_Next_Steps.md` to reflect that the next thin task follow-up for block read snapshots is now implemented, rather than still pending.

- [ ] **Step 2: Run a focused grep sanity check**

Run:

```bash
rg -n "block-read-watchlist|block_read_watchlist" runtime/TdxQuant_Task_Layer_Usage.md docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Next_Steps.md
```

Expected:

```text
... matching lines in all three files ...
```

- [ ] **Step 3: Commit**

```bash
git add runtime/TdxQuant_Task_Layer_Usage.md docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Next_Steps.md
git commit -m "docs: add task block read watchlist usage"
```

## Task 4: Run final focused regression

**Files:**
- Verify: `tdxquant/api/task.py`
- Verify: `tdxquant/cli.py`
- Verify: `tests/test_api_manager.py`
- Verify: `tests/test_api_cli.py`

- [ ] **Step 1: Run the focused regression suite**

Run:

```bash
python -m pytest tests/test_api_manager.py tests/test_api_cli.py -k "block_read_watchlist" -q
```

Expected:

```text
all selected tests pass
```

- [ ] **Step 2: Run a diff hygiene check**

Run:

```bash
git diff --check
```

Expected:

```text
no output
```

- [ ] **Step 3: Commit the final verification state**

```bash
git add tdxquant/api/task.py tdxquant/cli.py tests/test_api_manager.py tests/test_api_cli.py runtime/TdxQuant_Task_Layer_Usage.md docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Next_Steps.md
git commit -m "test: verify task block read watchlist entrypoint"
```

## Self-Review

- Spec coverage: the plan covers the thin task wrapper, single `--block-code` CLI entry, unchanged provider snapshot contract, task metadata attachment, and docs follow-up. It intentionally does not add export, preset, catalog, or task-only artifact formats.
- Placeholder scan: every task includes explicit file paths, code to add, and concrete verification commands.
- Type consistency: the plan uses `block_read_watchlist(...)` as the task-manager method, `block-read-watchlist` as the CLI subcommand, and `block_code` as the only input across all tasks.
