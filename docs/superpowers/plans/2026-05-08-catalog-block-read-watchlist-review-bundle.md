# Catalog Block Read Watchlist Review Bundle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a preset-backed catalog bundle `read-zxg-review` that sequentially runs `read-zxg-watchlist` then `read-zxg-full`, with a bundle-level `--block-code` override applied to both steps.

**Architecture:** Reuse the existing `runtime/command-bundles.json` schema and existing catalog bundle dispatch path. The only required code-path change is adding `--block-code` to `_add_catalog_run_arguments(...)` so bundle-level override can flow through existing namespace merge logic into both task-backed steps.

**Tech Stack:** Python CLI (`argparse`), existing catalog/task preset registries, `unittest`, OpenSpec markdown specs.

---

## File Map

- Modify: `tdxquant/cli.py`
  - Add `--block-code` to `_add_catalog_run_arguments(...)` so `catalog plan/run --bundle ... --block-code ...` parses and reaches bundle step dispatch.
- Modify: `runtime/command-bundles.json`
  - Add the new `read-zxg-review` bundle entry.
- Modify: `tests/test_api_cli.py`
  - Add focused parser/list/plan/run bundle coverage and the stop-on-step-1-failure case.
- Modify: `runtime/TdxQuant_Task_Layer_Usage.md`
  - Sync user-facing wording that this bundle is now a read-side preset-backed catalog bundle.
- Modify: `docs/TdxQuant_Project_Function_Map.md`
  - Sync function-map wording for the new read-side bundle.
- Modify: `docs/TdxQuant_Next_Steps.md`
  - Remove stale “bundle still missing” language and record the new bundle scope.
- Modify: `openspec/specs/tdx-command-catalog/spec.md`
  - Add the new stable bundle requirement to the main spec.
- Create: `openspec/changes/catalog-block-read-watchlist-review-bundle/proposal.md`
- Create: `openspec/changes/catalog-block-read-watchlist-review-bundle/design.md`
- Create: `openspec/changes/catalog-block-read-watchlist-review-bundle/tasks.md`
- Create: `openspec/changes/catalog-block-read-watchlist-review-bundle/specs/tdx-command-catalog/spec.md`
- Archive to: `openspec/changes/archive/YYYY-MM-DD-catalog-block-read-watchlist-review-bundle/`

## Task 1: Enable bundle-level `--block-code` and add failing parser coverage

**Files:**
- Modify: `tdxquant/cli.py`
- Test: `tests/test_api_cli.py`

- [ ] **Step 1: Write the failing parser test for bundle-level `--block-code`**

Add a new focused parser test near the existing catalog bundle parser tests in `tests/test_api_cli.py`:

```python
def test_catalog_bundle_plan_accepts_block_code_override(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["catalog", "plan", "--bundle", "read-zxg-review", "--block-code", "MYZXG"])
    self.assertEqual(args.command, "catalog")
    self.assertEqual(args.catalog_command, "plan")
    self.assertEqual(args.bundle, "read-zxg-review")
    self.assertEqual(args.block_code, "MYZXG")
```

- [ ] **Step 2: Run the focused test to verify it fails**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "catalog_bundle_plan_accepts_block_code_override" -q
```

Expected: FAIL with argparse rejecting `--block-code` as an unrecognized argument.

- [ ] **Step 3: Add the minimal parser support in `tdxquant/cli.py`**

Update `_add_catalog_run_arguments(...)` in `tdxquant/cli.py`:

```python
def _add_catalog_run_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--view", choices=["detailed", "summary"], default="detailed")
    subparser.add_argument("--from-step")
    subparser.add_argument("--to-step")
    subparser.add_argument("--only-step")
    subparser.add_argument("--profile")
    subparser.add_argument("--api-profile")
    subparser.add_argument("--trade-profile")
    subparser.add_argument("--strategy-path")
    subparser.add_argument("--port")
    subparser.add_argument("--baudrate", type=int)
    subparser.add_argument("--timeout", type=float)
    subparser.add_argument("--block-code")
```

Only add the single new argument; do not redesign parser shape.

- [ ] **Step 4: Re-run the focused parser test**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "catalog_bundle_plan_accepts_block_code_override" -q
```

Expected: PASS.

- [ ] **Step 5: Commit the parser hook**

```bash
git add tdxquant/cli.py tests/test_api_cli.py
git commit -m "Add block code override for catalog bundles"
```

## Task 2: Add the `read-zxg-review` bundle and list/plan coverage

**Files:**
- Modify: `runtime/command-bundles.json`
- Modify: `tests/test_api_cli.py`

- [ ] **Step 1: Add failing list/plan tests for the new bundle**

Add these focused tests in `tests/test_api_cli.py`:

```python
def test_handle_catalog_bundle_list_includes_read_zxg_review(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["catalog", "list", "--kind", "bundle"])
    result = _handle_catalog_subcommand(args)
    self.assertTrue(result.ok)
    bundle_names = [row["name"] for row in result.data["bundles"]]
    self.assertIn("read-zxg-review", bundle_names)

def test_handle_catalog_bundle_list_returns_read_zxg_review_metadata(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["catalog", "list", "--kind", "bundle", "--bundle", "read-zxg-review"])
    result = _handle_catalog_subcommand(args)
    self.assertTrue(result.ok)
    self.assertEqual(result.data["summary"]["selected_bundle"], "read-zxg-review")
    self.assertEqual(result.data["bundles"][0]["name"], "read-zxg-review")
    self.assertEqual(result.data["bundles"][0]["steps"][0]["entry"], "read-zxg-watchlist")
    self.assertEqual(result.data["bundles"][0]["steps"][1]["entry"], "read-zxg-full")

def test_handle_catalog_plan_read_zxg_review_bundle_returns_resolved_steps(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["catalog", "plan", "--bundle", "read-zxg-review"])
    with patch("tdxquant.cli._dispatch_catalog_resolved_entry") as mocked_dispatch:
        result = _handle_catalog_subcommand(args)
    self.assertTrue(result.ok)
    self.assertEqual(result.data["catalog_bundle"]["name"], "read-zxg-review")
    self.assertEqual(result.data["catalog_bundle"]["selected_step_count"], 2)
    self.assertEqual(result.data["steps"][0]["entry"], "read-zxg-watchlist")
    self.assertEqual(result.data["steps"][1]["entry"], "read-zxg-full")
    self.assertEqual(result.data["steps"][0]["resolved_args"]["block_code"], "ZXG")
    self.assertEqual(result.data["steps"][1]["resolved_args"]["block_code"], "ZXG")
    mocked_dispatch.assert_not_called()
```

- [ ] **Step 2: Run the focused bundle tests to verify they fail before the registry exists**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "read_zxg_review and catalog" -q
```

Expected: FAIL because `read-zxg-review` is not yet in `runtime/command-bundles.json`.

- [ ] **Step 3: Add the bundle entry to `runtime/command-bundles.json`**

Insert the new bundle:

```json
"read-zxg-review": {
  "description": "先读取 ZXG 标准化快照，再查看完整诊断视图。",
  "labels": ["block", "watchlist", "read", "review"],
  "steps": [
    {
      "name": "snapshot",
      "entry": "read-zxg-watchlist"
    },
    {
      "name": "full",
      "entry": "read-zxg-full"
    }
  ]
}
```

Keep the existing schema exactly; do not add shared/default parameter fields.

- [ ] **Step 4: Re-run the focused tests**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "read_zxg_review and catalog" -q
```

Expected: PASS for the new list/plan coverage.

- [ ] **Step 5: Commit the bundle registry addition**

```bash
git add runtime/command-bundles.json tests/test_api_cli.py
git commit -m "Add read zxg review catalog bundle"
```

## Task 3: Add bundle run coverage for override propagation and stop-on-failure

**Files:**
- Modify: `tests/test_api_cli.py`

- [ ] **Step 1: Add focused run tests for default, override, and failure-stop semantics**

Add these tests in `tests/test_api_cli.py`:

```python
def test_handle_catalog_read_zxg_review_bundle_dispatches_steps_sequentially(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["catalog", "run", "--bundle", "read-zxg-review"])
    bundle = {
        "description": "snapshot then full",
        "steps": [
            {"index": 1, "name": "snapshot", "entry": "read-zxg-watchlist", "source": "task", "preset": "read-zxg-watchlist", "description": "", "options": {}},
            {"index": 2, "name": "full", "entry": "read-zxg-full", "source": "task", "preset": "read-zxg-full", "description": "", "options": {}},
        ],
    }
    with patch("tdxquant.cli.resolve_command_bundle", return_value=bundle), patch(
        "tdxquant.cli._dispatch_catalog_resolved_entry",
        side_effect=[Result(ok=True, code=ErrorCode.OK, message="snapshot-ok"), Result(ok=True, code=ErrorCode.OK, message="full-ok")],
    ) as mocked_dispatch:
        result = _handle_catalog_subcommand(args)
    self.assertTrue(result.ok)
    self.assertEqual(mocked_dispatch.call_count, 2)

def test_handle_catalog_read_zxg_review_bundle_applies_block_code_override_to_both_steps(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["catalog", "run", "--bundle", "read-zxg-review", "--block-code", "MYZXG"])
    bundle = {
        "description": "snapshot then full",
        "steps": [
            {"index": 1, "name": "snapshot", "entry": "read-zxg-watchlist", "source": "task", "preset": "read-zxg-watchlist", "description": "", "options": {}},
            {"index": 2, "name": "full", "entry": "read-zxg-full", "source": "task", "preset": "read-zxg-full", "description": "", "options": {}},
        ],
    }
    with patch("tdxquant.cli.resolve_command_bundle", return_value=bundle), patch(
        "tdxquant.cli._dispatch_catalog_resolved_entry",
        side_effect=[Result(ok=True, code=ErrorCode.OK, message="snapshot-ok"), Result(ok=True, code=ErrorCode.OK, message="full-ok")],
    ) as mocked_dispatch:
        result = _handle_catalog_subcommand(args)
    self.assertTrue(result.ok)
    first_args = mocked_dispatch.call_args_list[0].kwargs["args"]
    second_args = mocked_dispatch.call_args_list[1].kwargs["args"]
    self.assertEqual(first_args.block_code, "MYZXG")
    self.assertEqual(second_args.block_code, "MYZXG")

def test_handle_catalog_read_zxg_review_bundle_stops_after_snapshot_failure(self) -> None:
    parser = build_parser()
    args = parser.parse_args(["catalog", "run", "--bundle", "read-zxg-review"])
    bundle = {
        "description": "snapshot then full",
        "steps": [
            {"index": 1, "name": "snapshot", "entry": "read-zxg-watchlist", "source": "task", "preset": "read-zxg-watchlist", "description": "", "options": {}},
            {"index": 2, "name": "full", "entry": "read-zxg-full", "source": "task", "preset": "read-zxg-full", "description": "", "options": {}},
        ],
    }
    with patch("tdxquant.cli.resolve_command_bundle", return_value=bundle), patch(
        "tdxquant.cli._dispatch_catalog_resolved_entry",
        side_effect=[Result(ok=False, code=ErrorCode.EXECUTION_FAILED, message="snapshot-failed")],
    ) as mocked_dispatch:
        result = _handle_catalog_subcommand(args)
    self.assertFalse(result.ok)
    self.assertEqual(mocked_dispatch.call_count, 1)
    self.assertEqual(result.data["catalog_bundle"]["failed_step"]["entry"], "read-zxg-watchlist")
```

- [ ] **Step 2: Run the focused run tests**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "read_zxg_review and catalog" -q
```

Expected: PASS with default, override, and failure-stop coverage.

- [ ] **Step 3: Run the broader catalog regression slice**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "catalog" -q
```

Expected: PASS without regressing existing entry or bundle behavior.

- [ ] **Step 4: Commit the bundle run coverage**

```bash
git add tests/test_api_cli.py
git commit -m "Add catalog coverage for read zxg review bundle"
```

## Task 4: Sync docs and main OpenSpec requirement

**Files:**
- Modify: `runtime/TdxQuant_Task_Layer_Usage.md`
- Modify: `docs/TdxQuant_Project_Function_Map.md`
- Modify: `docs/TdxQuant_Next_Steps.md`
- Modify: `openspec/specs/tdx-command-catalog/spec.md`

- [ ] **Step 1: Update task usage wording**

Add/update wording in `runtime/TdxQuant_Task_Layer_Usage.md` so it explicitly states:

```md
- `read-zxg-review` 现在作为纯读 catalog bundle，把 `read-zxg-watchlist` 与 `read-zxg-full` 收口到同一条日常入口。
- 它只复用现有 preset-backed catalog entry，不引入 export / report / write-back 语义。
```

- [ ] **Step 2: Update function map and next-steps wording**

Sync the higher-level docs so they no longer imply this bundle is missing:

```md
- `block` 读侧当前已有：
  - `read-zxg-watchlist`
  - `read-zxg-full`
  - `export-zxg-watchlist`
  - `read-zxg-review` bundle
```

Keep the wording narrow: this is a read-only bundle, not a new report or write-back flow.

- [ ] **Step 3: Add the main OpenSpec requirement**

In `openspec/specs/tdx-command-catalog/spec.md`, add an incremental requirement like:

```md
### Requirement: Command catalog SHALL expose block read watchlist review bundles once the preset-backed entries are stable
The system SHALL expose stable catalog bundles that compose preset-backed block read watchlist snapshot and diagnostics entries through the existing bundle workflow.

#### Scenario: Caller lists block read watchlist review bundles
- **WHEN** a caller lists catalog bundles after the stable `read-zxg-watchlist` and `read-zxg-full` task presets are available
- **THEN** the catalog MUST include a bundle named `read-zxg-review`

#### Scenario: Caller plans a block read watchlist review bundle
- **WHEN** a caller executes `catalog plan --bundle read-zxg-review`
- **THEN** the system MUST resolve both steps through the existing preset-backed entry workflow without executing the steps

#### Scenario: Caller runs a block read watchlist review bundle
- **WHEN** a caller executes `catalog run --bundle read-zxg-review`
- **THEN** the system MUST dispatch both steps sequentially through the existing bundle workflow and stop if the first step fails
```

- [ ] **Step 4: Run focused verification and diff hygiene**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "read_zxg_review or read_zxg_watchlist or read_zxg_full or catalog" -q
git diff --check -- tdxquant/cli.py runtime/command-bundles.json tests/test_api_cli.py runtime/TdxQuant_Task_Layer_Usage.md docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Next_Steps.md openspec/specs/tdx-command-catalog/spec.md
```

Expected:
- pytest slice passes
- `git diff --check` prints nothing

- [ ] **Step 5: Commit the docs/spec sync**

```bash
git add runtime/TdxQuant_Task_Layer_Usage.md docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Next_Steps.md openspec/specs/tdx-command-catalog/spec.md
git commit -m "Document read zxg review catalog bundle"
```

## Task 5: Add and archive the OpenSpec lifecycle change

**Files:**
- Create: `openspec/changes/catalog-block-read-watchlist-review-bundle/proposal.md`
- Create: `openspec/changes/catalog-block-read-watchlist-review-bundle/design.md`
- Create: `openspec/changes/catalog-block-read-watchlist-review-bundle/tasks.md`
- Create: `openspec/changes/catalog-block-read-watchlist-review-bundle/specs/tdx-command-catalog/spec.md`
- Archive to: `openspec/changes/archive/YYYY-MM-DD-catalog-block-read-watchlist-review-bundle/`

- [ ] **Step 1: Create the minimal change artifacts**

Write:

```md
proposal.md
- Why: formalize the new read-side bundle
- What: add one bundle, keep existing schema, keep existing dispatch

design.md
- Reuse existing bundle schema
- `--block-code` is a required parser hook
- Bundle stays pure read-side orchestration

tasks.md
- formalize requirement
- validate
- archive
```

And add a delta spec under `specs/tdx-command-catalog/spec.md` that mirrors the main-spec requirement added in Task 4.

- [ ] **Step 2: Validate the change**

Run:

```bash
openspec status --change catalog-block-read-watchlist-review-bundle --json
openspec validate catalog-block-read-watchlist-review-bundle --type change --strict
```

Expected:
- `isComplete: true`
- strict validation passes

- [ ] **Step 3: Archive the change**

Run:

```bash
openspec archive catalog-block-read-watchlist-review-bundle -y
```

If the archive command aborts with “requirement already exists” because the main spec was pre-synced, do the established equivalent manual archive:

```bash
mv openspec/changes/catalog-block-read-watchlist-review-bundle openspec/changes/archive/YYYY-MM-DD-catalog-block-read-watchlist-review-bundle
openspec list --json
```

Expected:
- the archived directory exists
- the new change no longer appears as active

- [ ] **Step 4: Commit lifecycle sync**

```bash
git add openspec/changes/archive/YYYY-MM-DD-catalog-block-read-watchlist-review-bundle
git commit -m "docs: archive catalog block read watchlist review bundle change"
```

## Self-check before execution

- This plan assumes isolated implementation in a dedicated worktree because the main worktree is dirty.
- The only required runtime code change is the parser hook for bundle-level `--block-code`.
- All other runtime behavior is expected to flow through existing bundle and preset namespace merge logic.
- If implementation reveals a second runtime gap beyond parser registration, keep the fix minimal and limited to existing bundle dispatch code.
