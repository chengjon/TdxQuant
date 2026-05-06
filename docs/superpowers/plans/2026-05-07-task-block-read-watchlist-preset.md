# Task Block Read Watchlist Preset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add preset support for `task block-read-watchlist` so `task run --preset ...` can reuse a static `block_code` default while still allowing explicit CLI `--block-code` overrides.

**Architecture:** Reuse the existing task preset pipeline exactly. Extend the preset allowlist/default-profile map, add one representative `read-zxg-watchlist` preset, and tighten `_build_task_preset_namespace(...)` so `block-read-watchlist` presets fail early when `block_code` is missing. Keep dispatch, provider behavior, and preset schema unchanged.

**Tech Stack:** Python CLI (`argparse`), `tdxquant/tasking.py`, `tdxquant/cli.py`, JSON preset registry, `pytest`, `unittest.mock`

---

## File Map

- Modify: `tdxquant/tasking.py`
  - Add `block-read-watchlist` to `TASK_COMMAND_DEFAULT_PROFILES`
- Modify: `tdxquant/cli.py`
  - Extend `_build_task_preset_namespace(...)` with the same required-`block_code` early failure rule used by `block-read-full`
- Modify: `runtime/task-presets.json`
  - Add representative preset `read-zxg-watchlist`
- Modify: `tests/test_api_cli.py`
  - Add focused preset listing / dispatch / override / missing-field tests
- Modify: `runtime/TdxQuant_Task_Layer_Usage.md`
  - Add `task run --preset read-zxg-watchlist` usage alongside other block read tasks
- Modify: `docs/TdxQuant_Project_Function_Map.md`
  - Sync feature map so plain watchlist snapshot read is listed with preset support
- Modify: `docs/TdxQuant_Next_Steps.md`
  - Sync roadmap note so `block-read-watchlist` joins the same preset-backed block read family

## Task 1: Add preset registry support and representative preset

**Files:**
- Modify: `tdxquant/tasking.py`
- Modify: `runtime/task-presets.json`
- Test: `tests/test_api_cli.py`

- [ ] **Step 1: Add the failing preset-listing test**

Add this focused test near the existing `read-zxg-full` / `export-zxg-watchlist` preset listing tests:

```python
def test_handle_task_presets_lists_block_read_watchlist_preset(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["task", "presets"])
    with patch(
        "tdxquant.cli.load_task_presets",
        return_value={
            "read-zxg-watchlist": {
                "command": "block-read-watchlist",
                "description": "read zxg watchlist snapshot",
                "options": {"block_code": "ZXG"},
            }
        },
    ):
        result = _handle_task_subcommand(args)
    self.assertTrue(result.ok)
    self.assertEqual(result.data["summary"]["preset_count"], 1)
    self.assertEqual(result.data["presets"][0]["name"], "read-zxg-watchlist")
    self.assertEqual(result.data["presets"][0]["command"], "block-read-watchlist")
    self.assertEqual(result.data["presets"][0]["profile"], "default")
```

- [ ] **Step 2: Run the focused listing test and verify the current failure**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "lists_block_read_watchlist_preset" -q
```

Expected:

- FAIL because `TASK_COMMAND_DEFAULT_PROFILES` does not yet contain `block-read-watchlist`

- [ ] **Step 3: Add `block-read-watchlist` to the preset allowlist/default-profile map**

Update `tdxquant/tasking.py`:

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
    "block-read-watchlist": "default",
    "block-read-watchlist-export": "default",
    "block-read-full": "default",
}
```

- [ ] **Step 4: Add the representative preset**

Append this entry to `runtime/task-presets.json` after the existing block-read presets:

```json
  "read-zxg-watchlist": {
    "command": "block-read-watchlist",
    "description": "读取 ZXG 板块标准化快照。",
    "options": {
      "block_code": "ZXG"
    }
  }
```

- [ ] **Step 5: Re-run the focused listing test and verify it passes**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "lists_block_read_watchlist_preset" -q
```

Expected:

- PASS

- [ ] **Step 6: Commit Task 1**

```bash
git add tdxquant/tasking.py runtime/task-presets.json tests/test_api_cli.py
git commit -m "Add block read watchlist preset support"
```

## Task 2: Add preset run coverage and required-field guard

**Files:**
- Modify: `tdxquant/cli.py`
- Modify: `tests/test_api_cli.py`

- [ ] **Step 1: Add the parser acceptance test**

Add this focused parser test near `test_task_run_parser_accepts_block_code_override`:

```python
def test_task_run_parser_accepts_block_read_watchlist_block_code_override(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["task", "run", "--preset", "read-zxg-watchlist", "--block-code", "ZXG"])
    self.assertEqual(args.command, "task")
    self.assertEqual(args.task_command, "run")
    self.assertEqual(args.preset, "read-zxg-watchlist")
    self.assertEqual(args.block_code, "ZXG")
```

- [ ] **Step 2: Add the preset default-dispatch test**

```python
def test_handle_task_run_uses_block_read_watchlist_preset_defaults(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["task", "run", "--preset", "read-zxg-watchlist"])
    expected = Result(ok=True, code=ErrorCode.OK, message="ok")
    manager = MagicMock()
    manager.block_read_watchlist.return_value = expected
    with (
        patch(
            "tdxquant.cli.resolve_task_preset",
            return_value={
                "command": "block-read-watchlist",
                "profile": "default",
                "api_profile": "safe_read",
                "trade_profile": None,
                "strategy_path": None,
                "options": {
                    "block_code": "ZXG",
                },
            },
        ),
        patch("tdxquant.cli.TdxTaskManager", return_value=manager),
    ):
        result = _handle_task_subcommand(args)
    self.assertIs(result, expected)
    manager.block_read_watchlist.assert_called_once_with(block_code="ZXG")
```

- [ ] **Step 3: Add the CLI override test**

```python
def test_handle_task_run_prefers_block_read_watchlist_cli_override(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["task", "run", "--preset", "read-zxg-watchlist", "--block-code", "MYZXG"])
    expected = Result(ok=True, code=ErrorCode.OK, message="ok")
    manager = MagicMock()
    manager.block_read_watchlist.return_value = expected
    with (
        patch(
            "tdxquant.cli.resolve_task_preset",
            return_value={
                "command": "block-read-watchlist",
                "profile": "default",
                "api_profile": "safe_read",
                "trade_profile": None,
                "strategy_path": None,
                "options": {
                    "block_code": "ZXG",
                },
            },
        ),
        patch("tdxquant.cli.TdxTaskManager", return_value=manager),
    ):
        result = _handle_task_subcommand(args)
    self.assertIs(result, expected)
    manager.block_read_watchlist.assert_called_once_with(block_code="MYZXG")
```

- [ ] **Step 4: Add the missing-required-field failure test**

```python
def test_handle_task_run_rejects_block_read_watchlist_preset_missing_block_code(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["task", "run", "--preset", "read-zxg-watchlist"])
    with (
        patch(
            "tdxquant.cli.resolve_task_preset",
            return_value={
                "command": "block-read-watchlist",
                "profile": "default",
                "api_profile": "safe_read",
                "trade_profile": None,
                "strategy_path": None,
                "options": {},
            },
        ),
        patch("tdxquant.cli.TdxTaskManager") as mocked_manager,
    ):
        result = _handle_task_subcommand(args)
    self.assertFalse(result.ok)
    self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
    self.assertIn("block_code", result.message)
    mocked_manager.assert_not_called()
```

- [ ] **Step 5: Run the new focused tests and verify the current failure mode**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "block_read_watchlist_preset or read_zxg_watchlist" -q
```

Expected:

- parser/default/override tests may already be close to passing once Task 1 is in place
- the missing-field failure test should fail until `_build_task_preset_namespace(...)` adds a `block-read-watchlist` guard

- [ ] **Step 6: Add the required-field early failure**

Update `tdxquant/cli.py` inside `_build_task_preset_namespace(...)`:

```python
    if command_name == "block-read-watchlist":
        missing_required = [name for name in ("block_code",) if merged.get(name) in (None, "")]
        if missing_required:
            raise ValueError(f"task preset execution requires: {', '.join(missing_required)}")

    if command_name == "block-read-watchlist-export":
        missing_required = [name for name in ("block_code", "export_output") if merged.get(name) in (None, "")]
        if missing_required:
            raise ValueError(f"task preset execution requires: {', '.join(missing_required)}")

    if command_name == "block-read-full":
        missing_required = [name for name in ("block_code",) if merged.get(name) in (None, "")]
        if missing_required:
            raise ValueError(f"task preset execution requires: {', '.join(missing_required)}")
```

- [ ] **Step 7: Re-run the focused tests and verify they pass**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "block_read_watchlist_preset or read_zxg_watchlist" -q
```

Expected:

- PASS

- [ ] **Step 8: Commit Task 2**

```bash
git add tdxquant/cli.py tests/test_api_cli.py
git commit -m "Add task run coverage for block read watchlist preset"
```

## Task 3: Sync docs and run final focused verification

**Files:**
- Modify: `runtime/TdxQuant_Task_Layer_Usage.md`
- Modify: `docs/TdxQuant_Project_Function_Map.md`
- Modify: `docs/TdxQuant_Next_Steps.md`

- [ ] **Step 1: Add task-layer usage examples**

In `runtime/TdxQuant_Task_Layer_Usage.md`, add `read-zxg-watchlist` alongside the existing block read presets:

```bash
python -m tdxquant.cli task run --preset read-zxg-watchlist
python -m tdxquant.cli task run --preset read-zxg-watchlist --block-code MYZXG
python -m tdxquant.cli task run --preset read-zxg-full
python -m tdxquant.cli task run --preset read-zxg-full --block-code MYZXG
```

And update the surrounding prose to say:

```markdown
- `read-zxg-watchlist` 这类 preset 只提供静态 `block_code` 默认值
- `read-zxg-full` 这类 preset 也沿用同一套 `block_code` 覆盖语义
```

- [ ] **Step 2: Sync the feature map**

Update `docs/TdxQuant_Project_Function_Map.md` so the block read task ladder reflects:

```markdown
- `task block-read-watchlist`
- `task run --preset read-zxg-watchlist`
- `task block-read-full`
- `task run --preset read-zxg-full`
- `task block-read-watchlist-export`
- `task run --preset export-zxg-watchlist`
```

- [ ] **Step 3: Sync roadmap wording**

Update `docs/TdxQuant_Next_Steps.md` so the block read family says:

```markdown
- `task block-read-watchlist` 已接入现有 task preset 体系，当前只做静态 `block_code` 打包与显式 CLI 覆盖
- `task block-read-full` 已接入同一套 task preset 体系，当前只做静态 `block_code` 打包与显式 CLI 覆盖
```

- [ ] **Step 4: Run focused preset regression**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "block_read_watchlist_preset or read_zxg_watchlist or block_read_watchlist or task_presets" -q
```

Expected:

- the new block-read-watchlist preset tests pass
- existing `task presets` behavior still passes
- no regressions for the plain `task block-read-watchlist` command tests

- [ ] **Step 5: Run diff hygiene**

Run:

```bash
git diff --check -- tdxquant/tasking.py tdxquant/cli.py runtime/task-presets.json tests/test_api_cli.py runtime/TdxQuant_Task_Layer_Usage.md docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Next_Steps.md
```

Expected:

- clean diff with no whitespace or patch-format issues

- [ ] **Step 6: Commit Task 3**

```bash
git add runtime/TdxQuant_Task_Layer_Usage.md docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Next_Steps.md
git commit -m "Document block read watchlist preset usage"
```

- [ ] **Step 7: Summarize completion**

Record in the handoff:

- files changed
- exact focused test commands run
- that no provider/catalog/report/export behavior changed
- whether this line still needs OpenSpec lifecycle and a selective commit strategy
