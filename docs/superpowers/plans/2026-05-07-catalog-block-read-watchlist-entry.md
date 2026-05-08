# 2026-05-07 Catalog Block Read Watchlist Entry Plan

> **For agentic workers:** REQUIRED SUB-SILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a preset-backed catalog entry for `read-zxg-watchlist` so `catalog list / plan / run` can expose the existing `task run --preset read-zxg-watchlist` path without expanding catalog schema or introducing new catalog commands.

**Architecture:** Reuse the existing `runtime/command-catalog.json` schema exactly. Add one `task` source entry for `read-zxg-watchlist`, then extend focused CLI tests so `catalog list` shows it, `catalog list --entry` returns its metadata, `catalog plan` resolves to `task run --preset read-zxg-watchlist` with `block_code=ZXG`, and `catalog run` still dispatches through the existing preset-backed task path.

**Tech Stack:** JSON catalog registry, `tdxquant/catalog.py`, `tdxquant/cli.py`, `pytest`, `unittest.mock`

---

## File Map

- Modify: `runtime/command-catalog.json`
  - Add representative `read-zxg-watchlist` task source entry
- Modify: `tests/test_api_cli.py`
  - Add focused catalog list / plan / run tests for `read-zxg-watchlist`
- Modify: `docs/TdxQuant_Task_Layer_Usage.md`
  - Sync the task-layer usage wording so only `read-zxg-full` is described as catalog-backed while `read-zxg-watchlist` remains preset-only
- Modify: `docs/TdxQuant_Project_Function_Map.md`
  - Sync feature map so catalog-backed `read-zxg-full` and preset-only `read-zxg-watchlist` are both reflected accurately
- Modify: `docs/TdxQuant_Next_Steps.md`
  - Sync roadmap wording so the block read family reflects the new catalog-backed watchlist entry without implying any new provider behavior
- Modify only if tests expose a real gap: `tdxquant/catalog.py` or `tdxquant/cli.py`
  - Keep changes minimal; no schema or dispatch redesign

## Task 1: Add catalog registry support and representative entry

**Files:**
- Modify: `runtime/command-catalog.json`
- Test: `tests/test_api_cli.py`

- [ ] **Step 1: Add the failing catalog-list test**

Add a focused test near the existing `export-zxg-watchlist` and `read-zxg-full` catalog list tests:

```python
def test_handle_catalog_list_default_includes_read_zxg_watchlist_entry(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["catalog", "list"])
    result = _handle_catalog_subcommand(args)
    self.assertTrue(result.ok)
    entry_names = [row["name"] for row in result.data["entries"]]
    self.assertIn("read-zxg-watchlist", entry_names)
```

- [ ] **Step 2: Add the entry-metadata listing test**

Add a focused `--entry` metadata test near the existing `export-zxg-watchlist` and `read-zxg-full` tests:

```python
def test_handle_catalog_list_returns_read_zxg_watchlist_entry_metadata(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["catalog", "list", "--entry", "read-zxg-watchlist"])
    result = _handle_catalog_subcommand(args)
    self.assertTrue(result.ok)
    self.assertEqual(result.data["summary"]["selected_entry"], "read-zxg-watchlist")
    self.assertEqual(result.data["entries"][0]["name"], "read-zxg-watchlist")
    self.assertEqual(result.data["entries"][0]["source"], "task")
    self.assertEqual(result.data["entries"][0]["preset"], "read-zxg-watchlist")
    self.assertEqual(result.data["entries"][0]["command"], "block-read-watchlist")
```

- [ ] **Step 3: Run the focused failing tests**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "read_zxg_watchlist and catalog" -q
```

Expected:

- FAIL because `runtime/command-catalog.json` does not yet contain the new entry.

- [ ] **Step 4: Add the representative catalog entry**

Append this entry to `runtime/command-catalog.json` near the other block-read task entries:

```json
  "read-zxg-watchlist": {
    "source": "task",
    "preset": "read-zxg-watchlist",
    "description": "统一入口下的 ZXG 板块标准化快照读取模板。",
    "labels": ["task", "block", "watchlist", "read"]
  }
```

- [ ] **Step 5: Re-run the focused list tests and ensure they pass**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "read_zxg_watchlist and catalog" -q
```

Expected:

- PASS

- [ ] **Step 6: Commit Task 1**

```bash
git add runtime/command-catalog.json tests/test_api_cli.py
git commit -m "Add read zxg watchlist catalog entry"
```

## Task 2: Add catalog run / plan coverage and verify dispatch boundaries

**Files:**
- Modify: `tests/test_api_cli.py`

- [ ] **Step 1: Add the catalog plan test**

Add a focused plan test near the existing `read-zxg-full` and `export-zxg-watchlist` plan tests:

```python
def test_handle_catalog_plan_read_zxg_watchlist_returns_resolved_dispatch_without_execution(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["catalog", "plan", "--entry", "read-zxg-watchlist"])
    with patch("tdxquant.cli._handle_task_subcommand") as mocked_task_handler:
        result = _handle_catalog_subcommand(args)
    self.assertTrue(result.ok)
    self.assertEqual(result.data["catalog_entry"]["name"], "read-zxg-watchlist")
    self.assertEqual(result.data["dispatch"]["source"], "task")
    self.assertEqual(result.data["dispatch"]["command_group"], "task")
    self.assertEqual(result.data["dispatch"]["command_name"], "block-read-watchlist")
    self.assertEqual(result.data["resolved_args"]["block_code"], "ZXG")
    mocked_task_handler.assert_not_called()
```

- [ ] **Step 2: Add the catalog run dispatch test**

Add a focused run test near the existing `export-zxg-watchlist` and `read-zxg-full` run tests:

```python
def test_handle_catalog_read_zxg_watchlist_entry_dispatches_through_task_subcommand(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["catalog", "run", "--entry", "read-zxg-watchlist"])
    expected = Result(ok=True, code=ErrorCode.OK, message="ok")
    with patch("tdxquant.cli._handle_task_subcommand", return_value=expected) as mocked_handler:
        result = _handle_catalog_subcommand(args)
    self.assertIs(result, expected)
    forwarded = mocked_handler.call_args.args[0]
    self.assertEqual(forwarded.command, "task")
    self.assertEqual(forwarded.task_command, "run")
    self.assertEqual(forwarded.preset, "read-zxg-watchlist")
```

- [ ] **Step 3: Run the focused catalog tests**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "read_zxg_watchlist and catalog" -q
```

Expected:

- PASS
- `catalog plan` shows `block_code=ZXG`
- `catalog run` dispatches through `task run --preset read-zxg-watchlist`

- [ ] **Step 4: Commit Task 2**

```bash
git add tests/test_api_cli.py
git commit -m "Add catalog coverage for read zxg watchlist"
```

## Task 3: Sync docs and run final focused verification

**Files:**
- Modify: `runtime/TdxQuant_Task_Layer_Usage.md`
- Modify: `docs/TdxQuant_Project_Function_Map.md`
- Modify: `docs/TdxQuant_Next_Steps.md`

- [ ] **Step 1: Sync task-layer usage wording**

Update `runtime/TdxQuant_Task_Layer_Usage.md` so it states:
- `read-zxg-watchlist` is preset-only and not catalog-backed
- `read-zxg-full` is catalog-backed
- Both keep static `block_code` default semantics

- [ ] **Step 2: Sync the feature map**

Update `docs/TdxQuant_Project_Function_Map.md` so the block read ladder reflects:
- `task block-read-watchlist`
- `task run --preset read-zxg-watchlist`
- `task block-read-full`
- `task run --preset read-zxg-full`
- `task block-read-watchlist-export`
- `task run --preset export-zxg-watchlist`
- `catalog` only exposes `read-zxg-full` as catalog-backed for block read readout, while `read-zxg-watchlist` remains preset-only

- [ ] **Step 3: Sync roadmap wording**

Update `docs/TdxQuant_Next_Steps.md` so the block read family says:
- `task block-read-watchlist` is preset-backed and keeps its static `block_code` + `safe_read` metadata, but remains snapshot-read-only and not report/export/catalog-expanded
- `task block-read-full` keeps its preset-backed and catalog-backed status

- [ ] **Step 4: Run final focused regression**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "read_zxg_watchlist or read_zxg_full or export_zxg_watchlist or catalog" -q
```

Expected:

- new `read-zxg-watchlist` catalog tests pass
- existing `read-zxg-full` and `export-zxg-watchlist` catalog tests still pass
- no regressions for preset-only `task block-read-watchlist`

- [ ] **Step 5: Run diff hygiene**

Run:

```bash
git diff --check -- runtime/command-catalog.json tests/test_api_cli.py runtime/TdxQuant_Task_Layer_Usage.md docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Next_Steps.md
```

Expected:

- clean diff with no whitespace or patch-format issues

- [ ] **Step 6: Commit Task 3**

```bash
git add runtime/TdxQuant_Task_Layer_Usage.md docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Next_Steps.md
git commit -m "Document read zxg watchlist catalog entry usage"
```

- [ ] **Step 7: Summarize completion**

Record in the handoff:

- files changed
- exact focused test commands run
- that no provider/export/report/write-back behavior changed
- whether this line still needs OpenSpec lifecycle and a selective commit strategy
