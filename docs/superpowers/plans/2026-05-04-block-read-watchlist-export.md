# Block Read Watchlist Export Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a dedicated `task block-read-watchlist-export` workflow that reads a normalized block watchlist snapshot and atomically writes `data.snapshot` to a single JSON file.

**Architecture:** Keep export as a thin task-layer workflow above the existing provider-level `block.read_watchlist_snapshot(...)` contract. Implement export in `TdxTaskManager`, wire a dedicated `task` CLI entrypoint, and preserve the underlying `data.snapshot` while adding a minimal `data.export` object plus standard task metadata.

**Tech Stack:** Python 3, `pathlib`, JSON serialization, existing `Result` / task metadata helpers, `pytest`, `unittest.mock`

---

## File Map

- Modify: `tdxquant/api/task.py`
  - Add `TdxTaskManager.block_read_watchlist_export(...)`
  - Implement path validation, atomic JSON write, and thin export metadata
- Modify: `tdxquant/cli.py`
  - Add `task block-read-watchlist-export` parser and dispatch
- Modify: `tests/test_api_manager.py`
  - Add focused task-manager tests for export success and failure paths
- Modify: `tests/test_api_cli.py`
  - Add focused parser/dispatch tests for the new task entrypoint
- Modify: `runtime/TdxQuant_Task_Layer_Usage.md`
  - Document usage and output semantics
- Modify: `docs/TdxQuant_Project_Function_Map.md`
  - Add task-layer positioning note
- Modify: `docs/TdxQuant_Next_Steps.md`
  - Move file export from deferred to delivered for this block read path

## Task 1: Implement manager-side export workflow

**Files:**
- Modify: `tdxquant/api/task.py`
- Test: `tests/test_api_manager.py`

- [ ] **Step 1: Write the failing task-manager tests**

Add tests covering:

```python
def test_task_block_read_watchlist_export_writes_snapshot_json() -> None:
    expected = Result(
        ok=True,
        code=ErrorCode.OK,
        message="normalized block snapshot",
        data={"snapshot": {"block_code": "ZXG", "symbols": ["600519.SH"], "symbol_count": 1}},
    )
    with TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "zxg.json"
        manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
        with patch.object(
            type(manager.api_manager.block),
            "read_watchlist_snapshot",
            return_value=expected,
        ):
            result = manager.block_read_watchlist_export(block_code="ZXG", output=str(output_path))

        assert output_path.exists()
        assert json.loads(output_path.read_text(encoding="utf-8")) == expected.data["snapshot"]
        assert result.data["export"]["output_path"] == str(output_path)
        assert result.data["export"]["overwritten"] is False
        assert result.data["export"]["file_size"] > 0
        assert result.data["task"]["name"] == "block_read_watchlist_export"


def test_task_block_read_watchlist_export_rejects_existing_file_without_overwrite() -> None:
    expected = Result(
        ok=True,
        code=ErrorCode.OK,
        message="normalized block snapshot",
        data={"snapshot": {"block_code": "ZXG", "symbols": ["600519.SH"], "symbol_count": 1}},
    )
    with TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "zxg.json"
        output_path.write_text("{}", encoding="utf-8")
        manager = TdxTaskManager(profile="default", strategy_path="strategy.py")
        with patch.object(
            type(manager.api_manager.block),
            "read_watchlist_snapshot",
            return_value=expected,
        ):
            result = manager.block_read_watchlist_export(block_code="ZXG", output=str(output_path))

        assert result.ok is False
        assert result.code == ErrorCode.INVALID_REQUEST
        assert result.data["snapshot"]["block_code"] == "ZXG"
        assert result.data["export"]["output_path"] == str(output_path)
```

- [ ] **Step 2: Run the focused manager tests and verify they fail**

Run:

```bash
python -m pytest tests/test_api_manager.py -k "block_read_watchlist_export" -q
```

Expected:

- failing because `TdxTaskManager.block_read_watchlist_export(...)` does not exist yet

- [ ] **Step 3: Implement minimal manager workflow**

Add to `tdxquant/api/task.py` a new method with this shape:

```python
def block_read_watchlist_export(
    self,
    *,
    block_code: str,
    output: str,
    overwrite: bool = False,
) -> Result:
    ...
```

Implementation requirements:

- use `_capture_task_timing(...)`
- call `self.api_manager.block.read_watchlist_snapshot(block_code=block_code)`
- if snapshot read fails, return the provider failure unchanged except for standard task metadata
- normalize `output` with `Path(output).expanduser().resolve()`
- reject directory paths
- require parent directory to already exist and be writable
- reject existing file when `overwrite=False`
- write only `result.data["snapshot"]` to the file
- serialize with:
  - UTF-8
  - `ensure_ascii=False`
  - `indent=2`
- use same-directory temporary file + atomic publish
- when `overwrite=False`, use an equivalent no-clobber publish step instead of unconditional replace
- on success add:

```python
result.data["export"] = {
    "output_path": str(output_path),
    "overwritten": overwritten,
    "file_size": output_path.stat().st_size,
}
```

- on export failure after snapshot read, preserve `data.snapshot`, set failure result, and add:

```python
result.data["export"] = {
    "output_path": str(output_path),
    "error": "...",
}
```

- [ ] **Step 4: Expand tests to cover overwrite and write-failure paths**

Add at least:

```python
def test_task_block_read_watchlist_export_overwrites_when_enabled() -> None:
    ...


def test_task_block_read_watchlist_export_preserves_snapshot_when_write_fails() -> None:
    ...
```

For write-failure, patch the temp-file write or no-clobber publish path so the test proves:

- `result.ok is False`
- `result.code == ErrorCode.EXECUTION_FAILED`
- `result.data["snapshot"]` is still present
- no half-written final file is left behind

- [ ] **Step 4.1: Cover directory-output rejection and no-clobber race**

Add focused tests proving:

- `--output` that resolves to an existing directory returns `invalid_request`
- `overwrite=False` treats a publish-time `FileExistsError` as an existing-file conflict instead of overwriting the newly created target

- [ ] **Step 5: Run focused manager tests and verify they pass**

Run:

```bash
python -m pytest tests/test_api_manager.py -k "block_read_watchlist_export" -q
```

Expected:

- all `block_read_watchlist_export` manager tests pass

## Task 2: Add CLI parser and dispatch

**Files:**
- Modify: `tdxquant/cli.py`
- Test: `tests/test_api_cli.py`

- [ ] **Step 1: Write the failing CLI tests**

Add tests like:

```python
def test_task_block_read_watchlist_export_command_parses() -> None:
    parser = build_parser()
    args = parser.parse_args(
        ["task", "block-read-watchlist-export", "--block-code", "ZXG", "--output", "runtime/exports/zxg.json"]
    )
    assert args.command == "task"
    assert args.task_command == "block-read-watchlist-export"
    assert args.block_code == "ZXG"
    assert args.output == "runtime/exports/zxg.json"
    assert args.overwrite is False


def test_handle_task_block_read_watchlist_export_uses_task_manager() -> None:
    parser = build_parser()
    args = parser.parse_args(
        ["task", "block-read-watchlist-export", "--block-code", "ZXG", "--output", "runtime/exports/zxg.json", "--overwrite"]
    )
    expected = Result(ok=True, code=ErrorCode.OK, message="ok")
    manager = MagicMock()
    manager.block_read_watchlist_export.return_value = expected
    with patch("tdxquant.cli.TdxTaskManager", return_value=manager):
        result = _handle_task_subcommand(args)
    assert result is expected
    manager.block_read_watchlist_export.assert_called_once_with(
        block_code="ZXG",
        output="runtime/exports/zxg.json",
        overwrite=True,
    )
```

- [ ] **Step 2: Run the focused CLI tests and verify they fail**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "block_read_watchlist_export" -q
```

Expected:

- parser or dispatch tests fail because the CLI entrypoint does not exist yet

- [ ] **Step 3: Implement parser and dispatch**

In `tdxquant/cli.py`:

- add `task block-read-watchlist-export` parser under the `task` group
- require:
  - `--block-code`
  - `--output`
- add `--overwrite` as `store_true`
- reuse `_add_task_common_arguments(...)`
- dispatch through `manager.block_read_watchlist_export(...)`

- [ ] **Step 4: Run focused CLI tests and verify they pass**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "block_read_watchlist_export" -q
```

Expected:

- all `block_read_watchlist_export` CLI tests pass

## Task 3: Document the new export workflow

**Files:**
- Modify: `runtime/TdxQuant_Task_Layer_Usage.md`
- Modify: `docs/TdxQuant_Project_Function_Map.md`
- Modify: `docs/TdxQuant_Next_Steps.md`

- [ ] **Step 1: Document usage in task-layer usage guide**

Add a new section showing:

```bash
python -m tdxquant.cli task block-read-watchlist-export \
  --block-code ZXG \
  --output runtime/exports/zxg.json
```

And explain:

- it is a thin export task above `manager.block.read_watchlist_snapshot(...)`
- it writes only `data.snapshot`
- it preserves `data.snapshot` in stdout result and appends `data.export`

- [ ] **Step 2: Update function map**

Add `block_read_watchlist_export` to the task inventory and state:

- underlying capability remains provider-level `block.read_watchlist_snapshot`
- task layer adds standard task metadata plus file export side effect
- this is still not a provider capability or catalog entry

- [ ] **Step 3: Update roadmap / next steps**

Adjust the `TongDaXin block -> 上层 watchlist` section so it reflects:

- thin read task exists
- JSON export task now exists
- thicker workflows like direct upper-layer write-back and richer export formats remain deferred

- [ ] **Step 4: Verify docs mention the right command names**

Run:

```bash
rg -n "block-read-watchlist-export|block_read_watchlist_export" runtime/TdxQuant_Task_Layer_Usage.md docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Next_Steps.md
```

Expected:

- the new export task is described in all three docs

## Task 4: Focused regression and handoff

**Files:**
- Verify the files changed in Tasks 1-3

- [ ] **Step 1: Run focused regression for manager + CLI**

Run:

```bash
python -m pytest tests/test_api_manager.py tests/test_api_cli.py -k "block_read_watchlist_export" -q
```

Expected:

- all export-focused tests pass

- [ ] **Step 2: Run a broader block-read focused regression**

Run:

```bash
python -m pytest tests/test_api_manager.py tests/test_api_cli.py -k "block_read_watchlist" -q
```

Expected:

- existing read task and new export task tests both pass

- [ ] **Step 3: Check formatting for touched files**

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

- touched files show only export-task related changes
- `git diff --check` is clean for touched files

- [ ] **Step 4: Do not commit from the worker**

Because the main worktree is already very dirty, stop after implementation + verification and report:

- changed files
- test commands run
- exact pass/fail results
- any remaining risks
