# Catalog Block Read Watchlist Review And Export Bundle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a preset-backed catalog bundle named `read-zxg-review-and-export` that runs `read-zxg-watchlist`, then `read-zxg-full`, then `export-zxg-watchlist`, while allowing top-level `--block-code` fanout to all three steps and preserving the export preset's fixed `export_output`.

**Architecture:** This is a thin catalog-bundle addition, not a new execution model. The implementation should reuse the existing `runtime/command-bundles.json` schema, existing catalog bundle plan/run code, and existing preset-backed entries, then lock the behavior with focused CLI tests and sync the user/docs/OpenSpec surfaces.

**Tech Stack:** Python CLI (`argparse`, `unittest`), JSON runtime registries, OpenSpec markdown specs.

---

## File Map

**Modify:**
- `runtime/command-bundles.json`
  - Add the new `read-zxg-review-and-export` bundle definition.
- `tests/test_api_cli.py`
  - Add focused bundle list / plan / run coverage for the new bundle.
- `runtime/TdxQuant_Task_Layer_Usage.md`
  - Document the new review-and-export bundle as a preset-backed catalog workflow.
- `docs/TdxQuant_Project_Function_Map.md`
  - Reflect the new block read-side high-level bundle.
- `docs/TdxQuant_Next_Steps.md`
  - Update the block read-side ladder/status text.
- `openspec/specs/tdx-command-catalog/spec.md`
  - Add the stable bundle requirement and scenarios.

**Create later during lifecycle task:**
- `openspec/changes/catalog-block-read-watchlist-review-and-export-bundle/proposal.md`
- `openspec/changes/catalog-block-read-watchlist-review-and-export-bundle/design.md`
- `openspec/changes/catalog-block-read-watchlist-review-and-export-bundle/tasks.md`
- `openspec/changes/catalog-block-read-watchlist-review-and-export-bundle/specs/tdx-command-catalog/spec.md`

**Expected no code changes unless tests prove a gap:**
- `tdxquant/catalog.py`
- `tdxquant/cli.py`

---

### Task 1: Add focused failing tests for the new bundle

**Files:**
- Modify: `tests/test_api_cli.py`
- Reference: `runtime/command-bundles.json`

- [ ] **Step 1: Add failing bundle list/plan/run tests**

Add tests near the existing `read-zxg-review` bundle coverage in `tests/test_api_cli.py`:

```python
    def test_handle_catalog_bundle_list_includes_read_zxg_review_and_export(self) -> None:
        parser = cli.build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "bundle"])

        result = cli._handle_catalog_subcommand(args)

        self.assertTrue(result.success)
        bundle_names = [bundle["name"] for bundle in result.data["bundles"]]
        self.assertIn("read-zxg-review-and-export", bundle_names)

    def test_handle_catalog_bundle_list_returns_read_zxg_review_and_export_metadata(self) -> None:
        parser = cli.build_parser()
        args = parser.parse_args(["catalog", "list", "--kind", "bundle", "--bundle", "read-zxg-review-and-export"])

        result = cli._handle_catalog_subcommand(args)

        self.assertTrue(result.success)
        self.assertEqual(result.data["summary"]["selected_bundle"], "read-zxg-review-and-export")
        self.assertEqual(result.data["bundles"][0]["name"], "read-zxg-review-and-export")
        self.assertEqual(result.data["bundles"][0]["steps"][0]["entry"], "read-zxg-watchlist")
        self.assertEqual(result.data["bundles"][0]["steps"][1]["entry"], "read-zxg-full")
        self.assertEqual(result.data["bundles"][0]["steps"][2]["entry"], "export-zxg-watchlist")

    def test_handle_catalog_plan_read_zxg_review_and_export_bundle_returns_resolved_steps(self) -> None:
        parser = cli.build_parser()
        args = parser.parse_args(["catalog", "plan", "--bundle", "read-zxg-review-and-export"])

        result = cli._handle_catalog_subcommand(args)

        self.assertTrue(result.success)
        self.assertEqual(result.data["catalog_bundle"]["name"], "read-zxg-review-and-export")
        self.assertEqual(result.data["summary"]["selected_step_count"], 3)
        self.assertEqual(result.data["steps"][0]["entry"], "read-zxg-watchlist")
        self.assertEqual(result.data["steps"][1]["entry"], "read-zxg-full")
        self.assertEqual(result.data["steps"][2]["entry"], "export-zxg-watchlist")

    def test_handle_catalog_plan_read_zxg_review_and_export_bundle_applies_block_code_override_to_all_steps(self) -> None:
        parser = cli.build_parser()
        args = parser.parse_args(
            ["catalog", "plan", "--bundle", "read-zxg-review-and-export", "--block-code", "MYZXG", "--view", "summary"]
        )

        result = cli._handle_catalog_subcommand(args)

        self.assertTrue(result.success)
        self.assertEqual(result.data["steps"][0]["resolved_args"]["block_code"], "MYZXG")
        self.assertEqual(result.data["steps"][1]["resolved_args"]["block_code"], "MYZXG")
        self.assertEqual(result.data["steps"][2]["resolved_args"]["block_code"], "MYZXG")
        self.assertEqual(result.data["steps"][2]["resolved_args"]["export_output"], "runtime/exports/zxg.json")
        self.assertEqual(result.data["summary"]["steps"][0]["resolved_args"]["block_code"], "MYZXG")
        self.assertEqual(result.data["summary"]["steps"][1]["resolved_args"]["block_code"], "MYZXG")
        self.assertEqual(result.data["summary"]["steps"][2]["resolved_args"]["block_code"], "MYZXG")
    ```

- [ ] **Step 2: Run the new focused tests and confirm they fail**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "read_zxg_review_and_export and catalog" -q
```

Expected:

```text
FAIL ... read-zxg-review-and-export ... not found in bundle list/plan output
```

- [ ] **Step 3: Commit the failing-test checkpoint**

```bash
git add tests/test_api_cli.py
git commit -m "test: add failing coverage for read-zxg-review-and-export bundle"
```

---

### Task 2: Add the bundle definition and make the plan/list tests pass

**Files:**
- Modify: `runtime/command-bundles.json`
- Verify against: `runtime/task-presets.json`, `runtime/command-catalog.json`
- Test: `tests/test_api_cli.py`

- [ ] **Step 1: Add the new bundle to `runtime/command-bundles.json`**

Insert this JSON object next to the existing `read-zxg-review` bundle:

```json
  "read-zxg-review-and-export": {
    "description": "先读取 ZXG 标准化快照，再查看完整诊断视图，最后导出 watchlist JSON。",
    "labels": ["block", "watchlist", "read", "review", "export"],
    "steps": [
      {
        "name": "snapshot",
        "entry": "read-zxg-watchlist"
      },
      {
        "name": "full",
        "entry": "read-zxg-full"
      },
      {
        "name": "export",
        "entry": "export-zxg-watchlist"
      }
    ]
  }
```

- [ ] **Step 2: Run the focused bundle plan/list tests**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "read_zxg_review_and_export and catalog and not dispatches and not stops" -q
```

Expected:

```text
PASS
```

- [ ] **Step 3: Commit the bundle definition**

```bash
git add runtime/command-bundles.json tests/test_api_cli.py
git commit -m "feat: add read-zxg-review-and-export bundle definition"
```

---

### Task 3: Add run-path coverage for fanout and fail-fast execution

**Files:**
- Modify: `tests/test_api_cli.py`
- Reference: `tdxquant/cli.py`

- [ ] **Step 1: Add dispatch and failure-path tests**

Add these tests near the existing `read-zxg-review` run tests:

```python
    def test_handle_catalog_read_zxg_review_and_export_bundle_dispatches_steps_sequentially(self) -> None:
        parser = cli.build_parser()
        args = parser.parse_args(["catalog", "run", "--bundle", "read-zxg-review-and-export"])

        bundle = {
            "name": "read-zxg-review-and-export",
            "description": "",
            "labels": [],
            "steps": [
                {"index": 1, "name": "snapshot", "entry": "read-zxg-watchlist", "source": "task", "preset": "read-zxg-watchlist", "description": "", "options": {}},
                {"index": 2, "name": "full", "entry": "read-zxg-full", "source": "task", "preset": "read-zxg-full", "description": "", "options": {}},
                {"index": 3, "name": "export", "entry": "export-zxg-watchlist", "source": "task", "preset": "export-zxg-watchlist", "description": "", "options": {}},
            ],
        }

        with patch("tdxquant.cli.resolve_command_bundle", return_value=bundle), patch(
            "tdxquant.cli._dispatch_catalog_resolved_entry",
            side_effect=[
                Result.ok({"step": "snapshot"}),
                Result.ok({"step": "full"}),
                Result.ok({"step": "export"}),
            ],
        ) as dispatch:
            result = cli._handle_catalog_subcommand(args)

        self.assertTrue(result.success)
        self.assertEqual(dispatch.call_count, 3)
        self.assertEqual(result.data["catalog_bundle"]["name"], "read-zxg-review-and-export")

    def test_handle_catalog_read_zxg_review_and_export_bundle_applies_block_code_override_to_all_steps(self) -> None:
        parser = cli.build_parser()
        args = parser.parse_args(["catalog", "run", "--bundle", "read-zxg-review-and-export", "--block-code", "MYZXG"])

        bundle = {
            "name": "read-zxg-review-and-export",
            "description": "",
            "labels": [],
            "steps": [
                {"index": 1, "name": "snapshot", "entry": "read-zxg-watchlist", "source": "task", "preset": "read-zxg-watchlist", "description": "", "options": {}},
                {"index": 2, "name": "full", "entry": "read-zxg-full", "source": "task", "preset": "read-zxg-full", "description": "", "options": {}},
                {"index": 3, "name": "export", "entry": "export-zxg-watchlist", "source": "task", "preset": "export-zxg-watchlist", "description": "", "options": {}},
            ],
        }

        with patch("tdxquant.cli.resolve_command_bundle", return_value=bundle), patch(
            "tdxquant.cli._dispatch_catalog_resolved_entry",
            side_effect=[Result.ok({}), Result.ok({}), Result.ok({})],
        ) as dispatch:
            result = cli._handle_catalog_subcommand(args)

        self.assertTrue(result.success)
        first_args = dispatch.call_args_list[0].args[0]
        second_args = dispatch.call_args_list[1].args[0]
        third_args = dispatch.call_args_list[2].args[0]
        self.assertEqual(first_args.block_code, "MYZXG")
        self.assertEqual(second_args.block_code, "MYZXG")
        self.assertEqual(third_args.block_code, "MYZXG")

    def test_handle_catalog_read_zxg_review_and_export_bundle_stops_before_export_when_full_step_fails(self) -> None:
        parser = cli.build_parser()
        args = parser.parse_args(["catalog", "run", "--bundle", "read-zxg-review-and-export"])

        bundle = {
            "name": "read-zxg-review-and-export",
            "description": "",
            "labels": [],
            "steps": [
                {"index": 1, "name": "snapshot", "entry": "read-zxg-watchlist", "source": "task", "preset": "read-zxg-watchlist", "description": "", "options": {}},
                {"index": 2, "name": "full", "entry": "read-zxg-full", "source": "task", "preset": "read-zxg-full", "description": "", "options": {}},
                {"index": 3, "name": "export", "entry": "export-zxg-watchlist", "source": "task", "preset": "export-zxg-watchlist", "description": "", "options": {}},
            ],
        }

        with patch("tdxquant.cli.resolve_command_bundle", return_value=bundle), patch(
            "tdxquant.cli._dispatch_catalog_resolved_entry",
            side_effect=[Result.ok({"step": "snapshot"}), Result.fail("execution_failed", "full failed")],
        ) as dispatch:
            result = cli._handle_catalog_subcommand(args)

        self.assertFalse(result.success)
        self.assertEqual(dispatch.call_count, 2)
        self.assertEqual(result.data["catalog_bundle"]["failed_step"]["entry"], "read-zxg-full")
    ```

- [ ] **Step 2: Run the focused run-path tests**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "read_zxg_review_and_export and catalog" -q
```

Expected:

```text
PASS
```

- [ ] **Step 3: If these tests expose a real runtime gap, make the smallest fix**

Only if the run-path tests fail in runtime logic:

- inspect `tdxquant/cli.py:_plan_catalog_bundle(...)`
- inspect `tdxquant/cli.py:_run_catalog_bundle(...)`
- inspect `tdxquant/catalog.py:resolve_command_bundle_step_range(...)`

Allowed minimal fixes:
- preserve top-level `block_code` on all step namespaces
- preserve fail-fast stop-before-next-step behavior

Re-run:

```bash
python -m pytest tests/test_api_cli.py -k "read_zxg_review_and_export and catalog" -q
```

Expected:

```text
PASS
```

- [ ] **Step 4: Commit the run-path coverage (and any required minimal runtime fix)**

```bash
git add tests/test_api_cli.py tdxquant/cli.py tdxquant/catalog.py
git commit -m "test: cover review-and-export bundle fanout and fail-fast behavior"
```

If no runtime files changed, omit them from `git add`.

---

### Task 4: Sync user docs and the main OpenSpec spec

**Files:**
- Modify: `runtime/TdxQuant_Task_Layer_Usage.md`
- Modify: `docs/TdxQuant_Project_Function_Map.md`
- Modify: `docs/TdxQuant_Next_Steps.md`
- Modify: `openspec/specs/tdx-command-catalog/spec.md`

- [ ] **Step 1: Update task-layer usage docs**

Add a short section or bullet that states:

```md
- `read-zxg-review-and-export` is a preset-backed catalog bundle that reads the ZXG snapshot, reads the full diagnostics view, then exports the watchlist JSON using the existing `export-zxg-watchlist` preset.
- `catalog plan/run --bundle read-zxg-review-and-export --block-code <value>` fans the same `block_code` override out to all three steps.
- The export path remains the preset-owned `export_output`; V1 does not support top-level `--export-output` on the bundle.
```

- [ ] **Step 2: Update Function Map and Next Steps**

Add short bullets like:

```md
- `read-zxg-review-and-export` now packages the read-side review flow plus JSON export as a preset-backed catalog bundle.
```

and

```md
- `block` 读侧现在已有纯读 review bundle 与 review+export bundle 两条高层 catalog 场景入口。
```

- [ ] **Step 3: Update the main OpenSpec command-catalog spec**

Add an added requirement/scenarios to `openspec/specs/tdx-command-catalog/spec.md` covering:

- bundle exists in catalog bundle listings
- plan resolves 3 steps
- top-level `--block-code` propagates to all 3 steps
- run dispatches sequentially and stops before export if step 2 fails

Use wording consistent with the existing `read-zxg-review` requirement.

- [ ] **Step 4: Run the broader catalog regression slice**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "catalog" -q
```

Expected:

```text
PASS
```

- [ ] **Step 5: Commit the docs/spec sync**

```bash
git add runtime/TdxQuant_Task_Layer_Usage.md docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Next_Steps.md openspec/specs/tdx-command-catalog/spec.md
git commit -m "docs: sync review-and-export bundle docs and command catalog spec"
```

---

### Task 5: Add and archive the OpenSpec lifecycle

**Files:**
- Create: `openspec/changes/catalog-block-read-watchlist-review-and-export-bundle/proposal.md`
- Create: `openspec/changes/catalog-block-read-watchlist-review-and-export-bundle/design.md`
- Create: `openspec/changes/catalog-block-read-watchlist-review-and-export-bundle/tasks.md`
- Create: `openspec/changes/catalog-block-read-watchlist-review-and-export-bundle/specs/tdx-command-catalog/spec.md`
- Archive later to: `openspec/changes/archive/YYYY-MM-DD-catalog-block-read-watchlist-review-and-export-bundle/`

- [x] **Step 1: Create the lifecycle change artifacts in an isolated worktree**

Create:

```text
openspec/changes/catalog-block-read-watchlist-review-and-export-bundle/proposal.md
openspec/changes/catalog-block-read-watchlist-review-and-export-bundle/design.md
openspec/changes/catalog-block-read-watchlist-review-and-export-bundle/tasks.md
openspec/changes/catalog-block-read-watchlist-review-and-export-bundle/specs/tdx-command-catalog/spec.md
```

The change should formalize:

- the `read-zxg-review-and-export` bundle
- the fixed 3-step order
- the top-level `--block-code` fanout
- the fail-fast stop-before-export behavior
- the fact that `export_output` remains preset-owned

- [x] **Step 2: Validate the change**

Run:

```bash
openspec status --change catalog-block-read-watchlist-review-and-export-bundle --json
openspec validate catalog-block-read-watchlist-review-and-export-bundle --type change --strict
```

Expected:

```text
isComplete: true
Change 'catalog-block-read-watchlist-review-and-export-bundle' is valid
```

- [x] **Step 3: Archive the lifecycle**

First try:

```bash
openspec archive catalog-block-read-watchlist-review-and-export-bundle -y
```

If it fails with `requirement already exists`, do the established manual archive:

```bash
mv openspec/changes/catalog-block-read-watchlist-review-and-export-bundle \
   openspec/changes/archive/2026-05-08-catalog-block-read-watchlist-review-and-export-bundle
```

Then verify:

```bash
openspec list --json
```

Expected:

```text
{"changes":[]}
```

- [x] **Step 4: Commit the archived lifecycle**

```bash
git add openspec/changes/archive/2026-05-08-catalog-block-read-watchlist-review-and-export-bundle
git commit -m "docs: archive review-and-export bundle change"
```

---

## Self-Review Checklist

- Spec coverage:
  - 3-step bundle definition → Task 2
  - `--block-code` fanout to all 3 steps → Tasks 1 and 3
  - `export_output` remains preset-owned → Tasks 1, 4, 5
  - fail-fast stop-before-export on step 2 failure → Task 3
  - docs and main spec sync → Task 4
  - OpenSpec lifecycle → Task 5
- Placeholder scan:
  - No `TODO` / `TBD`
  - No unspecified “add validation” steps
- Type consistency:
  - Bundle name is always `read-zxg-review-and-export`
  - Step entries are always `read-zxg-watchlist`, `read-zxg-full`, `export-zxg-watchlist`
  - Override field is always `block_code`
