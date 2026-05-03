# Task Block Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a thin `task block-sync` entrypoint that reuses the existing provider-level `block.sync_watchlist` capability without redefining its machine contract.

**Architecture:** Keep the implementation deliberately thin. Add `TdxTaskManager.block_sync(...)` as a direct wrapper around `TdxApiManager.block.sync_watchlist(...)`, add `tdxquant task block-sync ...` parser/dispatch wiring, and update task-layer docs. Do not add presets, catalog entries, file-import parsing, or task-only artifact formats.

**Tech Stack:** Python 3, existing `TdxTaskManager` / `TdxApiManager`, argparse CLI, unittest/pytest test suites, existing Result/error contract.

---

## File Structure

- Modify: `tdxquant/api/task.py`
  - Add `TdxTaskManager.block_sync(...)` as a thin wrapper that attaches normal task metadata and forwards directly to `self.api_manager.block.sync_watchlist(...)`.
- Modify: `tdxquant/cli.py`
  - Add `task block-sync` parser wiring.
  - Add `_handle_task_subcommand(...)` dispatch branch that calls `manager.block_sync(...)`.
- Modify: `tests/test_api_manager.py`
  - Add focused `TdxTaskManager.block_sync(...)` tests that verify forwarding and metadata, without re-testing sync orchestration.
- Modify: `tests/test_api_cli.py`
  - Add parser and dispatch tests for `task block-sync`.
- Modify: `runtime/TdxQuant_Task_Layer_Usage.md`
  - Add a `task block-sync` usage section.
- Modify: `docs/TdxQuant_Project_Function_Map.md`
  - Add `task block-sync` to the scenario-task layer description.
- Modify: `docs/TdxQuant_Next_Steps.md`
  - Mark the `block sync task` follow-up as completed or moved forward appropriately.

## Task 1: Add `TdxTaskManager.block_sync(...)`

**Files:**
- Modify: `tdxquant/api/task.py`
- Test: `tests/test_api_manager.py`

- [ ] **Step 1: Write the failing task-manager tests**

Add these tests near the other `TdxTaskManagerTests` in `tests/test_api_manager.py`:

```python
def test_task_block_sync_uses_block_sync_watchlist_and_attaches_task_metadata(self) -> None:
    expected = Result(
        ok=True,
        code=ErrorCode.OK,
        message="planned block sync",
        data={"sync": {"status": "applied", "mode": "replace"}},
    )
    manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
    with patch.object(type(manager.api_manager.block), "sync_watchlist", return_value=expected) as mocked_sync:
        result = manager.block_sync(
            block_code="ZXG",
            symbols=["000001.SZ", "600519.SH"],
            mode="merge",
            create_if_missing=True,
            dry_run=True,
            show=False,
            mutation_key="sync-001",
            audit_dir="runtime/block-sync",
        )

    mocked_sync.assert_called_once_with(
        block_code="ZXG",
        symbols=["000001.SZ", "600519.SH"],
        mode="merge",
        create_if_missing=True,
        dry_run=True,
        show=False,
        mutation_key="sync-001",
        audit_dir="runtime/block-sync",
    )
    assert result.data["task"]["name"] == "block_sync"
    assert result.data["task_profile"]["name"] == "default"
    assert "task_call" in result.data["timing"]


def test_task_block_sync_preserves_provider_failure_contract(self) -> None:
    expected = Result(
        ok=False,
        code=ErrorCode.INVALID_REQUEST,
        message="rejected block sync because target block ZXG does not exist",
        data={"sync": {"status": "rejected"}},
    )
    manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
    with patch.object(type(manager.api_manager.block), "sync_watchlist", return_value=expected):
        result = manager.block_sync(block_code="ZXG", symbols=["000001.SZ"])

    assert result is expected
    assert result.data["task"]["name"] == "block_sync"
```

- [ ] **Step 2: Run the focused manager tests and verify they fail**

Run:

```bash
python -m pytest tests/test_api_manager.py -k "task_block_sync" -q
```

Expected:

```text
FAILED tests/test_api_manager.py::TdxTaskManagerTests::test_task_block_sync_uses_block_sync_watchlist_and_attaches_task_metadata
```

- [ ] **Step 3: Add the minimal task-manager implementation**

Add this method in `tdxquant/api/task.py` near the other thin task wrappers such as `watchlist_overview(...)` / `refresh_environment(...)`:

```python
def block_sync(
    self,
    *,
    block_code: str,
    symbols: list[str],
    mode: str = "replace",
    create_if_missing: bool = False,
    dry_run: bool = False,
    show: bool = True,
    mutation_key: str | None = None,
    audit_dir: str | None = None,
) -> Result:
    result, timing = _capture_task_timing(
        "task.block_sync",
        lambda: self.api_manager.block.sync_watchlist(
            block_code=block_code,
            symbols=symbols,
            mode=mode,
            create_if_missing=create_if_missing,
            dry_run=dry_run,
            show=show,
            mutation_key=mutation_key,
            audit_dir=audit_dir,
        ),
    )
    result.data.setdefault(
        "input",
        {
            "block_code": block_code,
            "symbols": list(symbols),
            "mode": mode,
            "create_if_missing": create_if_missing,
            "dry_run": dry_run,
            "show": show,
            "mutation_key": mutation_key,
            "audit_dir": audit_dir,
        },
    )
    return self._attach_task_metadata(result, task_name="block_sync", timing=timing)
```

- [ ] **Step 4: Re-run the focused manager tests and verify they pass**

Run:

```bash
python -m pytest tests/test_api_manager.py -k "task_block_sync" -q
```

Expected:

```text
2 passed
```

- [ ] **Step 5: Commit**

```bash
git add tdxquant/api/task.py tests/test_api_manager.py
git commit -m "feat: add task block sync manager wrapper"
```

## Task 2: Add `task block-sync` CLI wiring

**Files:**
- Modify: `tdxquant/cli.py`
- Test: `tests/test_api_cli.py`

- [ ] **Step 1: Write the failing CLI parser and dispatch tests**

Add these tests to `tests/test_api_cli.py` near the other task parser/dispatch tests:

```python
def test_task_block_sync_command_parses(self) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "task",
            "block-sync",
            "--block-code",
            "ZXG",
            "--stock",
            "000001.SZ",
            "--stock",
            "600519.SH",
            "--mode",
            "merge",
            "--create-if-missing",
            "--dry-run",
            "--show",
            "--mutation-key",
            "sync-001",
            "--audit-dir",
            "runtime/block-sync",
        ]
    )
    self.assertEqual(args.command, "task")
    self.assertEqual(args.task_command, "block-sync")
    self.assertEqual(args.block_code, "ZXG")
    self.assertEqual(args.stock, ["000001.SZ", "600519.SH"])
    self.assertEqual(args.mode, "merge")
    self.assertTrue(args.create_if_missing)
    self.assertTrue(args.dry_run)
    self.assertTrue(args.show)
    self.assertEqual(args.mutation_key, "sync-001")
    self.assertEqual(args.audit_dir, "runtime/block-sync")


def test_handle_task_block_sync_uses_task_manager(self) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "task",
            "block-sync",
            "--block-code",
            "ZXG",
            "--stock",
            "000001.SZ",
            "--mode",
            "replace",
        ]
    )
    expected = Result(ok=True, code=ErrorCode.OK, message="ok")
    manager = MagicMock()
    manager.block_sync.return_value = expected
    with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
        result = _handle_task_subcommand(args)
    self.assertIs(result, expected)
    manager.block_sync.assert_called_once_with(
        block_code="ZXG",
        symbols=["000001.SZ"],
        mode="replace",
        create_if_missing=False,
        dry_run=False,
        show=True,
        mutation_key=None,
        audit_dir=None,
    )
```

- [ ] **Step 2: Run the focused CLI tests and verify they fail**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "task_block_sync" -q
```

Expected:

```text
FAILED tests/test_api_cli.py::ApiCliTests::test_task_block_sync_command_parses
```

- [ ] **Step 3: Add parser and dispatch wiring**

In `tdxquant/cli.py`, add a new task subparser entry inside `_build_task_parser(...)`:

```python
task_block_sync_parser = task_subparsers.add_parser("block-sync")
_add_block_sync_arguments(task_block_sync_parser)
_add_task_common_arguments(task_block_sync_parser)
```

Then add a new branch in `_handle_task_subcommand(...)` near the other thin task wrappers:

```python
if args.task_command == "block-sync":
    return manager.block_sync(
        block_code=args.block_code,
        symbols=args.stock,
        mode=args.mode,
        create_if_missing=args.create_if_missing,
        dry_run=args.dry_run,
        show=args.show,
        mutation_key=args.mutation_key,
        audit_dir=args.audit_dir,
    )
```

- [ ] **Step 4: Re-run the focused CLI tests and verify they pass**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "task_block_sync" -q
```

Expected:

```text
2 passed
```

- [ ] **Step 5: Commit**

```bash
git add tdxquant/cli.py tests/test_api_cli.py
git commit -m "feat: add task block sync cli entrypoint"
```

## Task 3: Document and verify the thin task contract

**Files:**
- Modify: `runtime/TdxQuant_Task_Layer_Usage.md`
- Modify: `docs/TdxQuant_Project_Function_Map.md`
- Modify: `docs/TdxQuant_Next_Steps.md`
- Test: `tests/test_api_manager.py`
- Test: `tests/test_api_cli.py`

- [ ] **Step 1: Update task-layer usage docs**

Add a new section to `runtime/TdxQuant_Task_Layer_Usage.md` after the existing task workflow sections:

```markdown
### 4.x Block Sync

```bash
python -m tdxquant.cli task block-sync \
  --block-code ZXG \
  --stock 000001.SZ \
  --stock 600519.SH \
  --mode replace
```

可选参数：

- `--mode replace|merge`
- `--create-if-missing`
- `--dry-run`
- `--mutation-key`
- `--show`
- `--api-profile`
- `--strategy-path`
- `--output`

这个任务当前只是一层薄包装：

1. 调 `manager.block.sync_watchlist(...)`
2. 直接返回既有 sync summary / governance result / audit artifact

当前不支持：

- 文件导入
- task preset
- catalog entry
```
```

- [ ] **Step 2: Update roadmap/docs to mark task-level block-sync as the next completed scene entry**

Update:

- `docs/TdxQuant_Project_Function_Map.md`
- `docs/TdxQuant_Next_Steps.md`

Add concise statements that:

- `task block-sync` now exists as a day-to-day task entrypoint
- it is a thin wrapper around provider-level `block.sync_watchlist`
- preset/catalog/file-import remain explicitly deferred

Use wording like:

```markdown
- 已提供 `tdxquant task block-sync ...`
- 该入口直接复用 provider-level `block.sync_watchlist`
- 当前仍未纳入文件导入、task preset 或 catalog 收口
```

- [ ] **Step 3: Run the focused regression for task block-sync**

Run:

```bash
python -m pytest tests/test_api_manager.py tests/test_api_cli.py -k "task_block_sync" -q
```

Expected:

```text
4 passed
```

- [ ] **Step 4: Run a broader task/block regression**

Run:

```bash
python -m pytest tests/test_api_manager.py tests/test_api_cli.py tests/test_block_sync.py -q
```

Expected:

```text
all passed
```

- [ ] **Step 5: Run diff sanity check**

Run:

```bash
git diff --check
```

Expected:

```text
no output
```

- [ ] **Step 6: Commit**

```bash
git add runtime/TdxQuant_Task_Layer_Usage.md docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Next_Steps.md tests/test_api_manager.py tests/test_api_cli.py
git commit -m "docs: add task block sync usage and roadmap notes"
```
