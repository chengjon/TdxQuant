# Catalog Block Read Full Entry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `read-zxg-full` as a preset-backed catalog entry so existing `catalog list`, `catalog list --entry`, `catalog plan`, and `catalog run` can discover and execute the stable `block-read-full` task path without changing catalog schema or dispatch logic.

**Architecture:** Reuse the existing task-source preset-backed catalog pattern already proven by `export-zxg-watchlist`. Extend `runtime/command-catalog.json` with one new entry, then lock the behavior with focused CLI tests that validate discovery, planning, and dispatch through the existing catalog-to-preset-to-task pipeline.

**Tech Stack:** JSON command catalog registry, existing catalog validation in `tdxquant/catalog.py`, CLI dispatch in `tdxquant/cli.py`, task preset registry, `pytest`, `unittest.mock`

---

## File Map

- Modify: `runtime/command-catalog.json`
  - Add one task-source preset-backed entry for `read-zxg-full`
- Modify: `tests/test_api_cli.py`
  - Add focused catalog `list`, `list --entry`, `plan`, and `run` regression for the new entry
- Optional: `runtime/TdxQuant_Task_Layer_Usage.md`
  - Only if tests or current docs show a real discoverability gap
- Optional: `docs/TdxQuant_Project_Function_Map.md`
  - Only if current roadmap text explicitly tracks this catalog gap
- Optional: `docs/TdxQuant_Next_Steps.md`
  - Only if current roadmap text explicitly tracks this catalog gap

No catalog core code is expected to change unless focused tests expose a real defect.

## Task 1: Add the catalog registry entry

**Files:**
- Modify: `runtime/command-catalog.json`
- Test: `tests/test_api_cli.py`

- [ ] **Step 1: Add the failing catalog-list visibility test**

Add a focused CLI test that assumes the new entry appears in the default unfiltered catalog list:

```python
def test_handle_catalog_list_default_includes_read_zxg_full_entry(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["catalog", "list"])
    result = _handle_catalog_subcommand(args)
    self.assertTrue(result.ok)
    entry_names = [entry["name"] for entry in result.data["entries"]]
    self.assertIn("read-zxg-full", entry_names)
```

- [ ] **Step 2: Run the focused listing test and verify failure**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "includes_read_zxg_full_entry" -q
```

Expected:

- failing because `runtime/command-catalog.json` does not yet contain `read-zxg-full`

- [ ] **Step 3: Add the catalog entry**

Append one minimal compatible entry to `runtime/command-catalog.json`:

```json
  "read-zxg-full": {
    "source": "task",
    "preset": "read-zxg-full",
    "description": "统一入口下的 ZXG 自选板块完整诊断视图模板。",
    "labels": ["task", "block", "watchlist", "diagnostics"]
  }
```

Requirements:

- keep the existing schema exactly:
  - `source`
  - `preset`
  - `description`
  - `labels`
- do not duplicate:
  - `block_code`
  - `profile`
  - any resolved preset args

- [ ] **Step 4: Re-run the focused listing test and verify it passes**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "includes_read_zxg_full_entry" -q
```

Expected:

- the new entry is visible in the default `catalog list` output

## Task 2: Cover single-entry inspection and plan output

**Files:**
- Modify: `tests/test_api_cli.py`

- [ ] **Step 1: Add failing single-entry and plan tests**

Add focused tests:

```python
def test_handle_catalog_list_returns_read_zxg_full_entry_metadata(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["catalog", "list", "--entry", "read-zxg-full"])
    result = _handle_catalog_subcommand(args)
    self.assertTrue(result.ok)
    self.assertEqual(result.data["summary"]["entry_count"], 1)
    self.assertEqual(result.data["entries"][0]["name"], "read-zxg-full")
    self.assertEqual(result.data["entries"][0]["source"], "task")
    self.assertEqual(result.data["entries"][0]["preset"], "read-zxg-full")
```

```python
def test_handle_catalog_plan_read_zxg_full_returns_resolved_dispatch_without_execution(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["catalog", "plan", "--entry", "read-zxg-full"])
    result = _handle_catalog_subcommand(args)
    self.assertTrue(result.ok)
    self.assertEqual(result.data["dispatch"]["source"], "task")
    self.assertEqual(result.data["dispatch"]["preset"], "read-zxg-full")
    resolved_args = result.data["dispatch"]["resolved_args"]
    self.assertEqual(resolved_args["task_command"], "block-read-full")
    self.assertEqual(resolved_args["block_code"], "ZXG")
```

- [ ] **Step 2: Run the focused inspection/plan tests and verify the current failure mode**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "returns_read_zxg_full_entry_metadata or plan_read_zxg_full" -q
```

Expected:

- failing before the new entry exists
- or failing if the current catalog plan path does not surface the new entry correctly

- [ ] **Step 3: Re-run the inspection/plan tests after the registry entry is present**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "returns_read_zxg_full_entry_metadata or plan_read_zxg_full" -q
```

Expected:

- single-entry lookup passes
- plan output includes `task_command = block-read-full`
- plan output includes `block_code = ZXG`

## Task 3: Cover run dispatch through the existing preset-backed path

**Files:**
- Modify: `tests/test_api_cli.py`

- [ ] **Step 1: Add the failing run-dispatch test**

Add a focused run test that proves catalog delegates to the existing task preset workflow instead of inventing a new path:

```python
def test_handle_catalog_read_zxg_full_entry_dispatches_through_task_subcommand(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["catalog", "run", "--entry", "read-zxg-full"])
    expected = Result(ok=True, code=ErrorCode.OK, message="ok")
    with patch("tdxquant.cli._handle_task_subcommand", return_value=expected) as mocked_task_handler:
        result = _handle_catalog_subcommand(args)
    self.assertIs(result, expected)
    mocked_task_handler.assert_called_once()
    dispatched_args = mocked_task_handler.call_args.args[0]
    self.assertEqual(dispatched_args.command, "task")
    self.assertEqual(dispatched_args.task_command, "run")
    self.assertEqual(dispatched_args.preset, "read-zxg-full")
```

- [ ] **Step 2: Run the focused run-dispatch test and verify failure if any catalog gap exists**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "read_zxg_full_entry_dispatches_through_task_subcommand" -q
```

Expected:

- if the existing catalog pipeline already supports the new entry shape, the test may pass immediately after Task 1
- if not, this exposes the exact gap to fix

- [ ] **Step 3: Only patch catalog core if the new test proves a real defect**

If and only if the run-dispatch test fails because of a genuine catalog implementation gap, make the minimal fix in:

- `tdxquant/catalog.py`
- or `tdxquant/cli.py`

Do **not** change schema or create a new dispatch model. The only acceptable code change here is a narrowly-scoped repair that is required for the existing task-source preset-backed pattern to work.

- [ ] **Step 4: Re-run the run-dispatch test and verify it passes**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "read_zxg_full_entry_dispatches_through_task_subcommand" -q
```

Expected:

- the new catalog entry dispatches through `task run --preset read-zxg-full`

## Task 4: Optional doc sync only if still needed

**Files:**
- Optionally modify: `runtime/TdxQuant_Task_Layer_Usage.md`
- Optionally modify: `docs/TdxQuant_Project_Function_Map.md`
- Optionally modify: `docs/TdxQuant_Next_Steps.md`

- [ ] **Step 1: Decide whether docs actually need changes**

Check whether existing docs already make the entry discoverable enough through the catalog itself:

- `catalog list --entry read-zxg-full`
- `catalog plan --entry read-zxg-full`

If those are sufficient and no roadmap text explicitly claims this catalog gap is still open, skip doc edits.

- [ ] **Step 2: If needed, add only minimal doc sync**

If current docs still explicitly claim this catalog gap is open, add one concise update showing:

```bash
python -m tdxquant.cli catalog list --entry read-zxg-full
python -m tdxquant.cli catalog plan --entry read-zxg-full
python -m tdxquant.cli catalog run --entry read-zxg-full
```

Keep the wording narrow:

- this is a catalog entry for an existing task preset
- it does not add inline parameter editing
- it does not add report or write-back semantics

- [ ] **Step 3: If any docs changed, run a focused hygiene check**

Run:

```bash
git diff --check -- runtime/TdxQuant_Task_Layer_Usage.md docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Next_Steps.md
```

Expected:

- no whitespace or conflict-marker issues in the touched docs

## Task 5: Final focused verification and handoff

**Files:**
- Verify only

- [ ] **Step 1: Run the focused catalog regression for this new entry**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "read_zxg_full and catalog" -q
```

Expected:

- default list visibility passes
- `list --entry` passes
- `plan --entry` passes
- `run --entry` passes

- [ ] **Step 2: Run the broader catalog sanity suite**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "catalog" -q
```

Expected:

- no regressions in existing catalog-backed report, trade, or task entries
- `export-zxg-watchlist` behavior remains intact

- [ ] **Step 3: Run diff hygiene for the touched files**

Run:

```bash
git diff --check -- runtime/command-catalog.json tests/test_api_cli.py
```

If Task 4 changed docs, include those files in the same check.

Expected:

- clean diff with no whitespace or patch-format issues

- [ ] **Step 4: Summarize completion status**

Record in the handoff:

- files changed
- whether catalog core code remained untouched
- exact focused and broader test commands run
- whether this line still needs OpenSpec lifecycle or a selective commit
