# Task Block Read Watchlist Export Preset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `block-read-watchlist-export` as a supported `task run --preset ...` target, with static preset defaults for `block_code`, `export_output`, and `overwrite`, while preserving explicit CLI override semantics.

**Architecture:** Reuse the existing task preset pipeline instead of creating a new preset path. Extend the task preset allowlist in `tdxquant/tasking.py`, teach `task run` to carry `export_output` and tri-state `overwrite`, map preset `options.export_output` into the existing `task block-read-watchlist-export` dispatch, and lock the behavior with focused CLI tests plus one representative preset entry in `runtime/task-presets.json`.

**Tech Stack:** Python 3, `argparse`, existing task preset loader/resolver in `tdxquant/tasking.py`, CLI dispatch in `tdxquant/cli.py`, JSON preset registry, `pytest`, `unittest.mock`

---

## File Map

- Modify: `tdxquant/tasking.py`
  - Add `block-read-watchlist-export` to `TASK_COMMAND_DEFAULT_PROFILES`
- Modify: `tdxquant/cli.py`
  - Extend `task run` arguments with `--export-output`
  - Make preset-path `--overwrite/--no-overwrite` tri-state
  - Map preset `options.export_output` into the namespace consumed by the existing task dispatch
  - Validate required preset-backed fields for `block-read-watchlist-export`
- Modify: `runtime/task-presets.json`
  - Add one representative preset entry for block read watchlist export
- Modify: `tests/test_api_cli.py`
  - Add focused preset listing, preset execution, CLI override, and missing-field failure tests
- Modify: `runtime/TdxQuant_Task_Layer_Usage.md`
  - Document preset-based export usage
- Modify: `docs/TdxQuant_Project_Function_Map.md`
  - Note preset availability for the export task
- Modify: `docs/TdxQuant_Next_Steps.md`
  - Move this preset slice from “deferred scenario packaging” to delivered

## Task 1: Extend the task preset allowlist and preset registry

**Files:**
- Modify: `tdxquant/tasking.py`
- Modify: `runtime/task-presets.json`

- [ ] **Step 1: Add the failing CLI-preset tests first**

Add or update focused tests in `tests/test_api_cli.py` that assume the preset target is supported and that listing includes a representative export preset. The key failing expectations should include:

```python
def test_handle_task_presets_lists_export_watchlist_preset() -> None:
    parser = build_parser()
    args = parser.parse_args(["task", "presets"])
    with patch(
        "tdxquant.cli.load_task_presets",
        return_value={
            "export-zxg-watchlist": {
                "command": "block-read-watchlist-export",
                "description": "export zxg snapshot",
                "profile": "default",
                "api_profile": "safe_read",
                "options": {
                    "block_code": "ZXG",
                    "export_output": "runtime/exports/zxg.json",
                    "overwrite": False,
                },
            }
        },
    ):
        result = _handle_task_subcommand(args)
    assert result.ok is True
    assert result.data["summary"]["preset_count"] == 1
    assert result.data["presets"][0]["command"] == "block-read-watchlist-export"
```

- [ ] **Step 2: Run the focused CLI preset tests and verify failure**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "export_watchlist_preset or block_read_watchlist_export_preset" -q
```

Expected:

- failing because `block-read-watchlist-export` is not yet in `TASK_COMMAND_DEFAULT_PROFILES`
- or failing because preset listing / run path still rejects the command as unsupported

- [ ] **Step 3: Add the command to the preset allowlist**

Modify `tdxquant/tasking.py`:

```python
TASK_COMMAND_DEFAULT_PROFILES: dict[str, str] = {
    "refresh-environment": "maintenance",
    "trade-audit-lookup": "trade_audit_lookup",
    "trade-audit-daily-report": "trade_audit_daily_report",
    "trade-audit-period-report": "trade_audit_period_report",
    "trade-buy": "trade_buy",
    "trade-submit-once": "trade_submit_once",
    "trade-submit-ready": "trade_submit_ready",
    "trade-confirm-current": "trade_confirm_current",
    "guarded-trade-buy": "guarded_trade_buy",
    "block-read-watchlist-export": "default",
}
```

This is the single allowlist gate used by `_build_task_preset_namespace(...)`.

- [ ] **Step 4: Add one representative preset entry**

Append one stable example to `runtime/task-presets.json`:

```json
  "export-zxg-watchlist": {
    "command": "block-read-watchlist-export",
    "description": "Export ZXG watchlist snapshot to a fixed JSON path.",
    "profile": "default",
    "api_profile": "safe_read",
    "options": {
      "block_code": "ZXG",
      "export_output": "runtime/exports/zxg.json",
      "overwrite": false
    }
  }
```

Do not use `output` here. It must be `export_output` to match the namespace consumed by the task dispatch path.

- [ ] **Step 5: Run the focused preset-listing test and verify it passes**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "lists_export_watchlist_preset" -q
```

Expected:

- preset listing passes
- listed command is `block-read-watchlist-export`

## Task 2: Extend `task run` argument shape for export-task preset execution

**Files:**
- Modify: `tdxquant/cli.py`
- Test: `tests/test_api_cli.py`

- [ ] **Step 1: Write the failing parser and preset-execution tests**

Add focused tests covering:

```python
def test_task_run_block_read_watchlist_export_preset_command_parses() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "task",
            "run",
            "--preset",
            "export-zxg-watchlist",
            "--export-output",
            "runtime/exports/zxg-override.json",
            "--overwrite",
        ]
    )
    assert args.command == "task"
    assert args.task_command == "run"
    assert args.export_output == "runtime/exports/zxg-override.json"
    assert args.overwrite is True
```

and:

```python
def test_handle_task_run_uses_block_read_watchlist_export_preset_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args(["task", "run", "--preset", "export-zxg-watchlist"])
    expected = Result(ok=True, code=ErrorCode.OK, message="ok")
    manager = MagicMock()
    manager.block_read_watchlist_export.return_value = expected
    with (
        patch(
            "tdxquant.cli.resolve_task_preset",
            return_value={
                "command": "block-read-watchlist-export",
                "profile": "default",
                "api_profile": "safe_read",
                "trade_profile": None,
                "strategy_path": None,
                "options": {
                    "block_code": "ZXG",
                    "export_output": "runtime/exports/zxg.json",
                    "overwrite": False,
                },
            },
        ),
        patch("tdxquant.cli.TdxTaskManager", return_value=manager),
    ):
        result = _handle_task_subcommand(args)
    assert result is expected
    manager.block_read_watchlist_export.assert_called_once_with(
        block_code="ZXG",
        output="runtime/exports/zxg.json",
        overwrite=False,
    )
```

- [ ] **Step 2: Run the focused CLI tests and verify they fail**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "block_read_watchlist_export_preset" -q
```

Expected:

- failing because `task run` does not yet accept `--export-output`
- or because `overwrite` still behaves as plain `False` default instead of tri-state

- [ ] **Step 3: Extend `task run` arguments**

Modify `_add_task_run_arguments(...)` in `tdxquant/cli.py`:

```python
def _add_task_run_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--profile")
    subparser.add_argument("--api-profile")
    subparser.add_argument("--trade-profile")
    subparser.add_argument("--strategy-path")
    ...
    subparser.add_argument("--json-output-path")
    subparser.add_argument("--csv-output-path")
    subparser.add_argument("--output", help="Optional path to write the JSON result")
    subparser.add_argument("--export-output")
    subparser.add_argument("--overwrite", action=argparse.BooleanOptionalAction, default=None)
```

Requirements:

- keep the existing generic `--output` untouched because it still means “write the command JSON result”
- add a dedicated `--export-output` for the export task’s target file
- make `overwrite` tri-state so preset defaults can flow through when CLI did not explicitly choose `--overwrite` or `--no-overwrite`

- [ ] **Step 4: Update preset namespace merge semantics**

Modify `_build_task_preset_namespace(...)` in `tdxquant/cli.py` so that `block-read-watchlist-export` validates and preserves the correct fields.

After the existing option merge:

```python
if command_name == "block-read-watchlist-export":
    missing_required = [name for name in ("block_code", "export_output") if merged.get(name) in (None, "")]
    if missing_required:
        raise ValueError(f"task preset execution requires: {', '.join(missing_required)}")
```

Keep the generic merge model unchanged:

- preset `options` fill missing / `None` values
- explicit CLI values win

This validation is important because the task dispatch path reads `args.block_code` and `args.export_output` directly.

- [ ] **Step 5: Run the focused preset-execution tests and verify they pass**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "block_read_watchlist_export_preset" -q
```

Expected:

- parser accepts `--export-output`
- `task run --preset ...` dispatches to `manager.block_read_watchlist_export(...)`

## Task 3: Lock override semantics and failure cases

**Files:**
- Modify: `tests/test_api_cli.py`

- [ ] **Step 1: Add explicit override and missing-field tests**

Add tests for:

```python
def test_handle_task_run_prefers_export_output_cli_override() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "task",
            "run",
            "--preset",
            "export-zxg-watchlist",
            "--export-output",
            "runtime/exports/zxg-override.json",
            "--overwrite",
        ]
    )
    expected = Result(ok=True, code=ErrorCode.OK, message="ok")
    manager = MagicMock()
    manager.block_read_watchlist_export.return_value = expected
    with (
        patch(
            "tdxquant.cli.resolve_task_preset",
            return_value={
                "command": "block-read-watchlist-export",
                "profile": "default",
                "api_profile": "safe_read",
                "trade_profile": None,
                "strategy_path": None,
                "options": {
                    "block_code": "ZXG",
                    "export_output": "runtime/exports/zxg.json",
                    "overwrite": False,
                },
            },
        ),
        patch("tdxquant.cli.TdxTaskManager", return_value=manager),
    ):
        result = _handle_task_subcommand(args)
    assert result is expected
    manager.block_read_watchlist_export.assert_called_once_with(
        block_code="ZXG",
        output="runtime/exports/zxg-override.json",
        overwrite=True,
    )
```

and:

```python
def test_handle_task_run_rejects_block_read_watchlist_export_preset_missing_required_fields() -> None:
    parser = build_parser()
    args = parser.parse_args(["task", "run", "--preset", "export-zxg-watchlist"])
    with patch(
        "tdxquant.cli.resolve_task_preset",
        return_value={
            "command": "block-read-watchlist-export",
            "profile": "default",
            "api_profile": "safe_read",
            "trade_profile": None,
            "strategy_path": None,
            "options": {"block_code": "ZXG"},
        },
    ):
        result = _handle_task_subcommand(args)
    assert result.ok is False
    assert result.code == ErrorCode.INVALID_REQUEST
    assert "export_output" in result.message
```

- [ ] **Step 2: Run the focused override/failure tests and verify they pass**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "prefers_export_output_cli_override or rejects_block_read_watchlist_export_preset_missing_required_fields" -q
```

Expected:

- both tests pass

## Task 4: Document preset usage and delivered scope

**Files:**
- Modify: `runtime/TdxQuant_Task_Layer_Usage.md`
- Modify: `docs/TdxQuant_Project_Function_Map.md`
- Modify: `docs/TdxQuant_Next_Steps.md`

- [ ] **Step 1: Update task-layer usage docs**

Add a short preset example near the block-read-watchlist-export task section:

```bash
python -m tdxquant.cli task run --preset export-zxg-watchlist
python -m tdxquant.cli task run \
  --preset export-zxg-watchlist \
  --export-output runtime/exports/zxg-override.json \
  --overwrite
```

Explain:

- preset uses `export_output` internally
- `task run --output` still means JSON result output, not export target override
- `--export-output` is the dedicated override path for export destination

- [ ] **Step 2: Update function map / roadmap**

Add concise notes that:

- `task block-read-watchlist-export` is now available through task presets
- this is still static preset packaging, not catalog or template-variable support

- [ ] **Step 3: Do a focused docs sanity check**

Run:

```bash
git diff --check -- runtime/TdxQuant_Task_Layer_Usage.md docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Next_Steps.md
```

Expected:

- no whitespace or conflict-marker issues in the touched docs

## Task 5: Final focused regression and handoff

**Files:**
- Verify only

- [ ] **Step 1: Run the focused preset regression**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "task_presets or block_read_watchlist_export_preset or export_watchlist_preset" -q
```

Expected:

- listing tests pass
- preset execution tests pass
- override tests pass
- unsupported command tests still pass

- [ ] **Step 2: Run a focused broader CLI regression**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "task_run or task_presets" -q
```

Expected:

- existing task preset flows such as `guarded-default`, `refresh-default`, `submit-ready-default`, and `confirm-current-default` still pass

- [ ] **Step 3: Summarize completion status**

Record in the handoff:

- files changed
- whether `runtime/task-presets.json` gained a representative example
- exact focused test commands run
- whether this line still needs OpenSpec lifecycle or selective commit
