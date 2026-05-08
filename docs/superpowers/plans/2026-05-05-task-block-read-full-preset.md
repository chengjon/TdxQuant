# Task Block Read Full Preset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `block-read-full` as a supported `task run --preset ...` target, with a static preset default for `block_code` and explicit CLI `--block-code` override semantics.

**Architecture:** Reuse the existing task preset pipeline instead of introducing a second preset execution model. Extend the preset allowlist in `tdxquant/tasking.py`, add the missing `--block-code` task-run argument in `tdxquant/cli.py`, perform one small preset-path hardening for missing `block_code`, and lock the behavior with focused CLI tests plus one representative preset entry in `runtime/task-presets.json`.

**Tech Stack:** Python 3, `argparse`, existing task preset loader/resolver in `tdxquant/tasking.py`, CLI dispatch in `tdxquant/cli.py`, JSON preset registry, `pytest`, `unittest.mock`

---

## File Map

- Modify: `tdxquant/tasking.py`
  - Add `block-read-full` to `TASK_COMMAND_DEFAULT_PROFILES`
- Modify: `tdxquant/cli.py`
  - Add generic `--block-code` to `task run`
  - Validate `block-read-full` preset execution requires `block_code`
  - Reuse existing `block-read-full` dispatch unchanged
- Modify: `runtime/task-presets.json`
  - Add one representative `read-zxg-full` preset entry
- Modify: `tests/test_api_cli.py`
  - Add focused parser, preset listing, preset execution, override, and missing-field tests
- Modify: `runtime/TdxQuant_Task_Layer_Usage.md`
  - Document preset-driven `block-read-full` usage
- Modify: `docs/TdxQuant_Project_Function_Map.md`
  - Note preset availability for `task block-read-full`
- Modify: `docs/TdxQuant_Next_Steps.md`
  - Move this preset slice out of deferred block-read scenario work

## Task 1: Extend the preset allowlist and registry

**Files:**
- Modify: `tdxquant/tasking.py`
- Modify: `runtime/task-presets.json`
- Test: `tests/test_api_cli.py`

- [ ] **Step 1: Add the failing preset-listing test**

Add a focused CLI test that assumes `block-read-full` can appear in the preset list:

```python
def test_handle_task_presets_lists_block_read_full_preset(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["task", "presets"])
    with patch(
        "tdxquant.cli.load_task_presets",
        return_value={
            "read-zxg-full": {
                "command": "block-read-full",
                "description": "read zxg diagnostics",
                "profile": "default",
                "options": {"block_code": "ZXG"},
            }
        },
    ):
        result = _handle_task_subcommand(args)
    self.assertTrue(result.ok)
    self.assertEqual(result.data["summary"]["preset_count"], 1)
    self.assertEqual(result.data["presets"][0]["name"], "read-zxg-full")
    self.assertEqual(result.data["presets"][0]["command"], "block-read-full")
```

- [ ] **Step 2: Run the focused listing test and verify failure**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "lists_block_read_full_preset" -q
```

Expected:

- failing because `block-read-full` is not yet in `TASK_COMMAND_DEFAULT_PROFILES`
- or failing because preset execution path still treats the command as unsupported

- [ ] **Step 3: Add `block-read-full` to the preset allowlist**

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
    "block-read-full": "default",
}
```

This is the single allowlist gate used by `_build_task_preset_namespace(...)`.

- [ ] **Step 4: Add one representative preset entry**

Append one stable example to `runtime/task-presets.json`:

```json
  "read-zxg-full": {
    "command": "block-read-full",
    "description": "Read full diagnostics view for ZXG.",
    "profile": "default",
    "options": {
      "block_code": "ZXG"
    }
  }
```

Do not add `output`, `export_output`, or `overwrite`. This preset only carries a static `block_code` default.

- [ ] **Step 5: Re-run the listing test and verify it passes**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "lists_block_read_full_preset" -q
```

Expected:

- preset listing passes
- listed command is `block-read-full`

## Task 2: Extend `task run` argument shape for `block-read-full` preset execution

**Files:**
- Modify: `tdxquant/cli.py`
- Test: `tests/test_api_cli.py`

- [ ] **Step 1: Add the failing parser and dispatch tests**

Add focused tests for parser support and preset execution:

```python
def test_task_run_block_read_full_preset_command_parses(self) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "task",
            "run",
            "--preset",
            "read-zxg-full",
            "--block-code",
            "MYZXG",
        ]
    )
    self.assertEqual(args.command, "task")
    self.assertEqual(args.task_command, "run")
    self.assertEqual(args.preset, "read-zxg-full")
    self.assertEqual(args.block_code, "MYZXG")
```

```python
def test_handle_task_run_uses_block_read_full_preset_defaults(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["task", "run", "--preset", "read-zxg-full"])
    expected = Result(ok=True, code=ErrorCode.OK, message="ok")
    manager = MagicMock()
    manager.block_read_full.return_value = expected
    with (
        patch(
            "tdxquant.cli.resolve_task_preset",
            return_value={
                "command": "block-read-full",
                "profile": "default",
                "api_profile": None,
                "trade_profile": None,
                "strategy_path": None,
                "options": {"block_code": "ZXG"},
            },
        ),
        patch("tdxquant.cli.TdxTaskManager", return_value=manager),
    ):
        result = _handle_task_subcommand(args)
    self.assertIs(result, expected)
    manager.block_read_full.assert_called_once_with(block_code="ZXG")
```

- [ ] **Step 2: Run the focused parser/dispatch tests and verify failure**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "block_read_full_preset_command_parses or uses_block_read_full_preset_defaults" -q
```

Expected:

- failing because `task run` does not yet accept `--block-code`
- or failing because preset execution cannot populate `args.block_code`

- [ ] **Step 3: Add generic `--block-code` to `task run`**

Modify `_add_task_run_arguments(...)` in `tdxquant/cli.py`:

```python
def _add_task_run_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--profile")
    subparser.add_argument("--api-profile")
    subparser.add_argument("--trade-profile")
    subparser.add_argument("--strategy-path")
    subparser.add_argument("--port")
    subparser.add_argument("--baudrate", type=int)
    subparser.add_argument("--timeout", type=float)
    subparser.add_argument("--code")
    subparser.add_argument("--price")
    subparser.add_argument("--quantity", type=int)
    subparser.add_argument("--max-depth", type=int)
    ...
    subparser.add_argument("--required-block-code")
    subparser.add_argument("--required-block-type", type=int)
    subparser.add_argument("--required-list-type", type=int)
    subparser.add_argument("--block-code")
    ...
    subparser.add_argument("--output", help="Optional path to write the JSON result")
```

Use an optional `--block-code`, not `required=True`, because `task run --preset ...` relies on late merge from preset defaults.

- [ ] **Step 4: Add the minimal preset-path hardening**

Modify `_build_task_preset_namespace(...)` in `tdxquant/cli.py` so `block-read-full` fails early when the preset path has no usable `block_code`:

```python
if command_name == "block-read-full":
    if merged.get("block_code") in (None, ""):
        raise ValueError("task preset execution requires: block_code")
```

Keep the rest of the generic merge model unchanged:

- preset `options` fill missing / `None` values
- explicit CLI values still win
- no new schema-validation pass for extra option keys in v1

- [ ] **Step 5: Re-run the parser/dispatch tests and verify they pass**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "block_read_full_preset_command_parses or uses_block_read_full_preset_defaults" -q
```

Expected:

- parser accepts `--block-code` on `task run`
- preset execution dispatches to `manager.block_read_full(...)`

## Task 3: Lock override and missing-field behavior

**Files:**
- Modify: `tests/test_api_cli.py`

- [ ] **Step 1: Add explicit override and failure tests**

Add:

```python
def test_handle_task_run_prefers_block_read_full_cli_override(self) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "task",
            "run",
            "--preset",
            "read-zxg-full",
            "--block-code",
            "MYZXG",
        ]
    )
    expected = Result(ok=True, code=ErrorCode.OK, message="ok")
    manager = MagicMock()
    manager.block_read_full.return_value = expected
    with (
        patch(
            "tdxquant.cli.resolve_task_preset",
            return_value={
                "command": "block-read-full",
                "profile": "default",
                "api_profile": None,
                "trade_profile": None,
                "strategy_path": None,
                "options": {"block_code": "ZXG"},
            },
        ),
        patch("tdxquant.cli.TdxTaskManager", return_value=manager),
    ):
        result = _handle_task_subcommand(args)
    self.assertIs(result, expected)
    manager.block_read_full.assert_called_once_with(block_code="MYZXG")
```

```python
def test_handle_task_run_rejects_block_read_full_preset_missing_block_code(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["task", "run", "--preset", "read-zxg-full"])
    with patch(
        "tdxquant.cli.resolve_task_preset",
        return_value={
            "command": "block-read-full",
            "profile": "default",
            "api_profile": None,
            "trade_profile": None,
            "strategy_path": None,
            "options": {},
        },
    ):
        result = _handle_task_subcommand(args)
    self.assertFalse(result.ok)
    self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
    self.assertIn("block_code", result.message)
```

- [ ] **Step 2: Run the focused override/failure tests and verify they pass**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "prefers_block_read_full_cli_override or rejects_block_read_full_preset_missing_block_code" -q
```

Expected:

- both tests pass
- error message names `block_code`

- [ ] **Step 3: Re-run the broader task-preset regression**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "task_run or task_presets" -q
```

Expected:

- existing preset flows such as `guarded-default`, `refresh-default`, `export-zxg-watchlist`, and `confirm-current-default` still pass
- the new `block-read-full` preset path passes in the same suite

## Task 4: Document the delivered preset path

**Files:**
- Modify: `runtime/TdxQuant_Task_Layer_Usage.md`
- Modify: `docs/TdxQuant_Project_Function_Map.md`
- Modify: `docs/TdxQuant_Next_Steps.md`

- [ ] **Step 1: Update task usage docs**

Add a short example near the `block-read-full` section:

```bash
python -m tdxquant.cli task run --preset read-zxg-full
python -m tdxquant.cli task run --preset read-zxg-full --block-code MYZXG
```

Explain:

- preset provides a static default `block_code`
- explicit `--block-code` overrides that default
- generic `--output` still only writes the whole JSON result

- [ ] **Step 2: Update roadmap docs**

Add concise notes that:

- `task block-read-full` is now available through task presets
- this remains a static preset path, not catalog support and not report/export packaging

- [ ] **Step 3: Sanity-check the touched docs**

Run:

```bash
git diff --check -- runtime/TdxQuant_Task_Layer_Usage.md docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Next_Steps.md
```

Expected:

- no whitespace errors
- no conflict markers

## Task 5: Final focused verification and handoff

**Files:**
- Verify only

- [ ] **Step 1: Run the focused new-feature regression**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "block_read_full_preset or read_zxg_full or block_read_full" -q
```

Expected:

- parser test passes
- preset listing passes
- preset execution default path passes
- explicit override path passes
- missing-field failure path passes

- [ ] **Step 2: Run the broader preset regression**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "task_run or task_presets or block_read_full" -q
```

Expected:

- no regressions in existing preset-backed commands
- no regressions in existing `block-read-full` direct command coverage

- [ ] **Step 3: Summarize completion status**

Record in the handoff:

- files changed
- whether `runtime/task-presets.json` gained a representative `read-zxg-full` example
- exact focused test commands run
- whether this line still needs OpenSpec lifecycle or selective commit
