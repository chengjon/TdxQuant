# Task Block Read Full Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a dedicated `task block-read-full` entrypoint that builds a task-level diagnostics summary on top of the existing canonical `block.read_watchlist_snapshot(...)` result.

**Architecture:** Keep `block-read-full` as a thin task-layer workflow above the existing provider-level snapshot capability. Implement a new `TdxTaskManager.block_read_full(...)`, wire an independent task CLI command, preserve `data.snapshot` as the source of truth, and add `data.read_full` only on successful snapshot reads.

**Tech Stack:** Python 3, existing `Result` envelope and task metadata helpers, `pytest`, `unittest.mock`

---

## File Map

- Modify: `tdxquant/api/task.py`
  - Add `TdxTaskManager.block_read_full(...)`
  - Build `data.read_full` from successful snapshot results
- Modify: `tdxquant/cli.py`
  - Add `task block-read-full` parser and dispatch
- Modify: `tests/test_api_manager.py`
  - Add focused manager/task tests for success, degraded metadata fallback, and provider failure passthrough
- Modify: `tests/test_api_cli.py`
  - Add focused parser/dispatch tests for the new task command
- Modify: `runtime/TdxQuant_Task_Layer_Usage.md`
  - Document the new task usage and clarify generic `--output` semantics
- Modify: `docs/TdxQuant_Project_Function_Map.md`
  - Add the new high-level block read task to the task-layer map
- Modify: `docs/TdxQuant_Next_Steps.md`
  - Move this diagnostics task from planned to delivered while keeping preset/export/write-back deferred

## Task 1: Implement manager-side `block_read_full(...)`

**Files:**
- Modify: `tdxquant/api/task.py`
- Test: `tests/test_api_manager.py`

- [ ] **Step 1: Write the failing manager tests**

Add tests that pin the intended task-level contract:

```python
def test_task_block_read_full_adds_read_summary_and_task_metadata(self) -> None:
    expected = Result(
        ok=True,
        code=ErrorCode.OK,
        message="normalized block snapshot",
        data={
            "snapshot": {
                "block_code": "ZXG",
                "symbols": ["600519.SH"],
                "symbol_count": 1,
                "source": "tongdaxin.custom_sector",
                "source_metadata": {
                    "sector_name": "自选股",
                    "raw_member_count": 2,
                    "duplicate_count": 1,
                },
            }
        },
        warnings=["duplicate members removed"],
    )
    manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
    with patch.object(
        type(manager.api_manager.block),
        "read_watchlist_snapshot",
        return_value=expected,
    ) as mocked_snapshot:
        result = manager.block_read_full(block_code="ZXG")

    mocked_snapshot.assert_called_once_with(block_code="ZXG")
    assert result is expected
    assert result.data["read_full"] == {
        "sector_name": "自选股",
        "raw_member_count": 2,
        "duplicate_count": 1,
        "warnings_present": True,
    }
    assert result.data["task"]["name"] == "block_read_full"
    assert result.data["task_profile"]["name"] == "default"
    assert "task_call" in result.data["timing"]


def test_task_block_read_full_skips_read_summary_on_provider_failure(self) -> None:
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
        result = manager.block_read_full(block_code="ZXG")

    assert result is expected
    assert "read_full" not in result.data
    assert result.data["task"]["name"] == "block_read_full"
```

- [ ] **Step 2: Run the focused manager tests and verify they fail**

Run:

```bash
python -m pytest tests/test_api_manager.py -k "block_read_full" -q
```

Expected:

- failing because `TdxTaskManager.block_read_full(...)` does not exist yet

- [ ] **Step 3: Implement the minimal manager workflow**

Add a new method to `tdxquant/api/task.py` with this shape:

```python
def block_read_full(
    self,
    *,
    block_code: str,
) -> Result:
    def run() -> Result:
        result = self.api_manager.block.read_watchlist_snapshot(block_code=block_code)
        if not result.ok:
            return result

        snapshot = result.data.get("snapshot")
        source_metadata = snapshot.get("source_metadata", {}) if isinstance(snapshot, dict) else {}
        warnings = result.warnings if isinstance(result.warnings, list) else []
        result.data["read_full"] = {
            "sector_name": source_metadata.get("sector_name"),
            "raw_member_count": source_metadata.get("raw_member_count"),
            "duplicate_count": source_metadata.get("duplicate_count"),
            "warnings_present": len(warnings) > 0,
        }
        return result

    result, timing = _capture_task_timing("task.block_read_full", run)
    return self._attach_task_metadata(result, task_name="block_read_full", timing=timing)
```

Implementation requirements:

- do not make a second read call
- do not reshape `data.snapshot`
- do not fabricate `data.read_full` on failure
- if `source_metadata` is partially missing, still emit `read_full` and fill missing summary fields with `None`
- preserve the original `Result` object returned by `read_watchlist_snapshot(...)`

- [ ] **Step 4: Expand tests for partial metadata and empty snapshot success**

Add at least:

```python
def test_task_block_read_full_tolerates_partial_source_metadata(self) -> None:
    expected = Result(
        ok=True,
        code=ErrorCode.OK,
        message="normalized block snapshot",
        data={
            "snapshot": {
                "block_code": "ZXG",
                "symbols": [],
                "symbol_count": 0,
                "source": "tongdaxin.custom_sector",
                "source_metadata": {"sector_name": "空板块"},
            }
        },
        warnings=[],
    )
    manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
    with patch.object(
        type(manager.api_manager.block),
        "read_watchlist_snapshot",
        return_value=expected,
    ):
        result = manager.block_read_full(block_code="ZXG")

    assert result.data["read_full"] == {
        "sector_name": "空板块",
        "raw_member_count": None,
        "duplicate_count": None,
        "warnings_present": False,
    }
```

- [ ] **Step 5: Run the focused manager tests and verify they pass**

Run:

```bash
python -m pytest tests/test_api_manager.py -k "block_read_full" -q
```

Expected:

- all `block_read_full` manager tests pass

## Task 2: Add CLI parser and dispatch

**Files:**
- Modify: `tdxquant/cli.py`
- Test: `tests/test_api_cli.py`

- [ ] **Step 1: Write the failing CLI tests**

Add parser and dispatch tests:

```python
def test_task_block_read_full_command_parses(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["task", "block-read-full", "--block-code", "ZXG"])
    assert args.command == "task"
    assert args.task_command == "block-read-full"
    assert args.block_code == "ZXG"


def test_handle_task_block_read_full_uses_task_manager(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["task", "block-read-full", "--block-code", "ZXG"])
    expected = Result(ok=True, code=ErrorCode.OK, message="ok")
    manager = MagicMock()
    manager.block_read_full.return_value = expected
    with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
        result = _handle_task_subcommand(args)

    assert result is expected
    manager.block_read_full.assert_called_once_with(block_code="ZXG")
```

- [ ] **Step 2: Run the focused CLI tests and verify they fail**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "block_read_full" -q
```

Expected:

- parser or dispatch tests fail because the `block-read-full` task command does not exist yet

- [ ] **Step 3: Implement parser and dispatch**

In `tdxquant/cli.py`:

- add a `task block-read-full` parser next to `block-read-watchlist`
- require `--block-code`
- reuse `_add_task_common_arguments(...)`
- add a new dispatch branch:

```python
if args.task_command == "block-read-full":
    return manager.block_read_full(block_code=args.block_code)
```

- [ ] **Step 4: Run the focused CLI tests and verify they pass**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "block_read_full" -q
```

Expected:

- all `block_read_full` CLI tests pass

## Task 3: Update user-facing docs

**Files:**
- Modify: `runtime/TdxQuant_Task_Layer_Usage.md`
- Modify: `docs/TdxQuant_Project_Function_Map.md`
- Modify: `docs/TdxQuant_Next_Steps.md`

- [ ] **Step 1: Document the new task usage**

Add a usage example to `runtime/TdxQuant_Task_Layer_Usage.md`:

```bash
python -m tdxquant.cli task block-read-full --block-code ZXG
```

Explain:

- it is a high-level diagnostics task on top of `block.read_watchlist_snapshot(...)`
- it preserves canonical `data.snapshot`
- it adds task-level `data.read_full`
- generic task `--output` still means “write the whole JSON result”, not a block export parameter

- [ ] **Step 2: Update the function map**

Add `block_read_full` to the task-layer inventory and state:

- it is a high-level read-side task
- it does not create a new provider capability
- it does not export files
- it does not perform writes

- [ ] **Step 3: Update next-steps status**

Adjust the block read-side roadmap so it reflects:

- canonical snapshot exists
- thin watchlist read task exists
- export task exists
- new high-level diagnostics task now exists
- preset / catalog / write-back for `block-read-full` remain deferred

- [ ] **Step 4: Verify docs mention the right command names**

Run:

```bash
rg -n "block-read-full|block_read_full" runtime/TdxQuant_Task_Layer_Usage.md docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Next_Steps.md
```

Expected:

- all three docs mention the new task consistently

## Task 4: Focused regression and handoff

**Files:**
- Verify files changed in Tasks 1-3

- [ ] **Step 1: Run focused manager + CLI regression**

Run:

```bash
python -m pytest tests/test_api_manager.py tests/test_api_cli.py -k "block_read_full" -q
```

Expected:

- all `block_read_full` tests pass

- [ ] **Step 2: Run broader block read regression**

Run:

```bash
python -m pytest tests/test_api_manager.py tests/test_api_cli.py -k "block_read_watchlist or block_read_full" -q
```

Expected:

- existing block read task tests and new `block_read_full` tests both pass

- [ ] **Step 3: Check touched-file diff quality**

Run:

```bash
git diff -- \
  tdxquant/api/task.py \
  tdxquant/cli.py \
  tests/test_api_manager.py \
  tests/test_api_cli.py \
  runtime/TdxQuant_Task_Layer_Usage.md \
  docs/TdxQuant_Project_Function_Map.md \
  docs/TdxQuant_Next_Steps.md | sed -n '1,260p'
```

And:

```bash
git diff --check -- \
  tdxquant/api/task.py \
  tdxquant/cli.py \
  tests/test_api_manager.py \
  tests/test_api_cli.py \
  runtime/TdxQuant_Task_Layer_Usage.md \
  docs/TdxQuant_Project_Function_Map.md \
  docs/TdxQuant_Next_Steps.md
```

Expected:

- touched files show only `block-read-full` related changes
- `git diff --check` is clean for touched files

- [ ] **Step 4: Stop before commit and report**

Because the main worktree is already dirty, stop after implementation + verification and report:

- changed files
- exact test commands run
- exact pass/fail results
- remaining risks
- whether `data.read_full` stayed task-only and `data.snapshot` remained canonical
