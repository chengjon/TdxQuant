# Review: 2026-05-08-catalog-block-read-watchlist-review-and-export-bundle-design.md

**Type**: `.md` / `spec` | **Perspective**: `auto` (arch + completeness + consistency) | **Date**: 2026-05-08 | **Reviewer**: Claude

---

## Executive Summary

The spec proposes a three-step read-then-export bundle (`read-zxg-review-and-export`) that correctly reuses the existing bundle infrastructure and makes a well-reasoned decision to keep `export_output` preset-owned in V1. All referenced files, catalog entries, presets, and symbols exist. However, the same critical issue from the review-only bundle spec applies: Decision 3's `--block-code` bundle-level override is not implementable without adding the argument to `_add_catalog_run_arguments`, a change the Implementation Surface explicitly states "不应该需要修改".

## Document Metadata

| Field | Value |
|-------|-------|
| Source | `docs/superpowers/specs/2026-05-08-catalog-block-read-watchlist-review-and-export-bundle-design.md` |
| File Type | `.md` |
| Doc Type | `spec` |
| Sections | 12 (Context, Goals, Non-Goals, Decisions 1-6, Error Semantics, Implementation Surface, Test Boundaries, Migration Plan) |
| Referenced Files | 6 found / 0 missing |
| Referenced Symbols | 7 found / 0 missing |

## Evidence Verification

### Files Referenced

| File | Exists? | Location |
|------|---------|----------|
| `runtime/command-bundles.json` | yes | `/opt/iflow/TdxQuant/runtime/command-bundles.json` |
| `runtime/command-catalog.json` | yes | `/opt/iflow/TdxQuant/runtime/command-catalog.json` |
| `runtime/task-presets.json` | yes | `/opt/iflow/TdxQuant/runtime/task-presets.json` |
| `runtime/TdxQuant_Task_Layer_Usage.md` | yes | `/opt/iflow/TdxQuant/runtime/TdxQuant_Task_Layer_Usage.md` |
| `docs/TdxQuant_Project_Function_Map.md` | yes | `/opt/iflow/TdxQuant/docs/TdxQuant_Project_Function_Map.md` |
| `docs/TdxQuant_Next_Steps.md` | yes | `/opt/iflow/TdxQuant/docs/TdxQuant_Next_Steps.md` |
| `openspec/specs/tdx-command-catalog/spec.md` | yes | `/opt/iflow/TdxQuant/openspec/specs/tdx-command-catalog/spec.md` |

### Functions/Classes/Symbols Referenced

| Symbol | Found? | Location |
|--------|--------|----------|
| `block.read_watchlist_snapshot(...)` | yes | `tdxquant/api/block.py:25`, `tdxquant/api/manager.py:1150` |
| `resolve_command_bundle(...)` | yes | `tdxquant/catalog.py:99` |
| `resolve_command_bundle_step_range(...)` | yes | `tdxquant/catalog.py:172` |
| `_run_catalog_bundle(...)` | yes | `tdxquant/cli.py:2936` |
| `_plan_catalog_bundle(...)` | yes | `tdxquant/cli.py:2780` |
| `read-zxg-watchlist` (catalog entry) | yes | `runtime/command-catalog.json:230-235` |
| `read-zxg-full` (catalog entry) | yes | `runtime/command-catalog.json:224-229` |
| `export-zxg-watchlist` (catalog entry) | yes | `runtime/command-catalog.json:218-223` |

### Claims Verified

| Claim | Status | Evidence |
|-------|--------|----------|
| Bundle schema uses `description`, `labels`, `steps` (with `name`, `entry`, optional `options`) | confirmed | `runtime/command-bundles.json` -- all 24 existing bundles follow this structure |
| `resolve_command_bundle(...)` resolves each step's entry against the catalog | confirmed | `tdxquant/catalog.py:121-132` |
| Bundle step failure stops subsequent steps | confirmed | `tdxquant/cli.py:2988-2991` |
| `export-zxg-watchlist` preset provides `export_output: "runtime/exports/zxg.json"` and `overwrite: false` | confirmed | `runtime/task-presets.json:77-87` |
| `block-read-watchlist-export` is in `TASK_COMMAND_DEFAULT_PROFILES` | confirmed | `tdxquant/tasking.py:19` |
| `--block-code` is available on the catalog run/plan parser | **contradicted** | `tdxquant/cli.py:514-573` -- `_add_catalog_run_arguments` does NOT include `--block-code` |
| Default path resolves `block_code` from presets for all three steps | confirmed | `tdxquant/cli.py:3566-3568` merges preset options; `block_code` and `export_output` both flow through |
| `_build_task_preset_namespace` requires `block_code` and `export_output` for `block-read-watchlist-export` | confirmed | `tdxquant/cli.py:3610-3612` validates both fields |
| Steps 1-2 are pure read (no file side effects) | confirmed | `task-presets.json:88-95` (read-zxg-watchlist) and `:96-102` (read-zxg-full) have no output options |
| Step 3 has file side effects (export to JSON) | confirmed | `task-presets.json:84` -- `export_output: "runtime/exports/zxg.json"` with `overwrite: false` |

## Checklist Results

### Architecture

| # | Check | Result | Notes |
|---|-------|--------|-------|
| A1 | Component boundaries | PASS | Bundle = orchestration only; three entries = independent capabilities; preset = parameter storage |
| A2 | Data flow | PASS | `catalog run --bundle` -> `_run_catalog_bundle` -> per-step dispatch -> `_handle_task_subcommand` -> preset resolution |
| A3 | Coupling | PASS | Bundle only references entry names; no duplication of block_code, export_output, or overwrite |
| A4 | Interface contracts | FAIL | Decision 3 specifies `--block-code` as bundle-level override, but `_add_catalog_run_arguments` (cli.py:514-573) does not register this argument |
| A5 | Scalability | PASS | Adding one bundle to a flat JSON registry; no scaling concern |
| A6 | Terminology consistency | PASS | Terms consistent throughout; matches codebase |
| A7 | Backward compatibility | PASS | Non-Goals explicitly state "不新增 bundle schema"; addition-only change |
| A8 | Implementation surface precision | FAIL | cli.py is listed under "不应该需要修改" (line 243), but adding `--block-code` to `_add_catalog_run_arguments` is provably required for Decision 3 and Test Boundaries lines 266/271 |
| A9 | Named entities verified | PASS | All 8 referenced symbols and 7 files verified as existing |

### Completeness

| # | Check | Result | Notes |
|---|-------|--------|-------|
| C1 | Required sections | PASS | All expected sections present including 6 decisions |
| C2 | Edge cases | PARTIAL | Error Semantics covers 6 failure scenarios; however, the `overwrite: false` behavior from the export preset (file-already-exists failure) is not mentioned |
| C3 | Implicit assumptions | PASS | Assumes catalog entries exist (confirmed); assumes bundle infrastructure is stable (confirmed); assumes preset defaults flow correctly (confirmed) |
| C4 | Acceptance criteria | PARTIAL | Test Boundaries specify 8 verifiable cases, but lines 266-267/271-272 depend on `--block-code` which is not in the parser |
| C5 | Missing roles/stakeholders | N/A | Single-bundle addition |

### Consistency

| # | Check | Result | Notes |
|---|-------|--------|-------|
| N1 | Terminology | PASS | `read-zxg-review-and-export` used consistently; step names match entries |
| N2 | Naming conventions | PASS | Follows existing bundle naming pattern |
| N3 | Formatting | PASS | Consistent heading hierarchy and code blocks |
| N4 | Cross-references | PASS | Decisions cross-reference each other and Context correctly |
| N5 | Style consistency | PASS | Uniform style throughout |

## Findings

### Critical Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 1 | Decision 3 + Implementation Surface | `--block-code` is not registered in `_add_catalog_run_arguments` (cli.py:514-573). argparse will reject `catalog plan --bundle read-zxg-review-and-export --block-code MYZXG` and `catalog run --bundle read-zxg-review-and-export --block-code MYZXG`. Implementation Surface (line 243) explicitly states cli.py "不应该需要修改", which contradicts Decision 3's interface contract. | Test Boundaries lines 266-272 cannot pass. Decision 3's `--block-code` override is unimplementable without a cli.py change. | Codebase: `_add_catalog_run_arguments` at cli.py:514-573 has no `--block-code`. Only `--required-block-code` at line 547. `parser.parse_args()` (cli.py:3991) rejects unknown arguments. No existing bundle test uses `--block-code`. Doc: searched Implementation Surface (lines 227-252) for any mention of parser modification -- cli.py is listed under "不应该需要修改" (line 243). Decision 3 (line 126-127) and Test Boundaries (lines 266, 271) both specify `--block-code` as a supported argument. | (1) Add `subparser.add_argument("--block-code")` to `_add_catalog_run_arguments` in cli.py. (2) Move cli.py from "不应该需要修改" to a required change in Implementation Surface. (3) The propagation mechanism already works: `_build_catalog_bundle_step_namespace` copies all parsed args to each step, and `_build_task_preset_namespace` only fills `block_code` from preset when it's missing/None. |

### Low Issues

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 1 | Error Semantics | The `export-zxg-watchlist` preset sets `overwrite: false` (task-presets.json:86). If `runtime/exports/zxg.json` already exists, step 3 will fail. This is not listed in the Error Semantics section's failure scenarios. The doc's Error Semantics (line 222-223) says "step 3 export task failure → bundle 返回失败" which is correct but doesn't explain the most likely cause. | Codebase: `runtime/task-presets.json:86` -- `"overwrite": false`. Doc: searched Error Semantics (lines 208-225) for any mention of file-exists or overwrite behavior -- none found. Decision 5 (line 188-189) notes "step 3 才有文件副作用" but doesn't address re-run idempotency. | Add a note in Error Semantics or Decision 5: "Re-running the bundle will fail at step 3 if `runtime/exports/zxg.json` already exists, due to `overwrite: false` in the export preset." |
| 2 | Context:line 22 | Context lists `read-zxg-review` as an existing "pure read bundle" (line 22), implying it's already in `command-bundles.json`. | Codebase: `runtime/command-bundles.json` -- no `read-zxg-review` bundle exists. This bundle is defined in the companion spec (`2026-05-08-catalog-block-read-watchlist-review-bundle-design.md`) but has not been implemented yet. | Clarify whether `read-zxg-review` is a prerequisite (already shipped) or a sibling spec (pending implementation). If pending, note the dependency explicitly. |

## Strengths

- Decision 4 is a well-reasoned scope boundary: keeping `export_output` preset-owned avoids introducing path-override semantics, per-step parameter asymmetry, and plan display complexity.
- Decision 5 correctly identifies that steps 1-2 are pure read (no cleanup needed on failure), which simplifies failure semantics for the export step.
- Concrete example JSON (Decision 1) provides the exact bundle definition, making the primary artifact unambiguous.
- Comprehensive error semantics with 6 failure scenarios and explicit "no new error schema" statement.
- Implementation Surface identifies specific documentation files to sync (lines 235-238), which is more precise than the companion review-only bundle spec.

## Detailed Recommendations

1. **Add `--block-code` to `_add_catalog_run_arguments` as a required change.** Same fix as the companion review-only bundle spec. One line in cli.py:

   ```python
   subparser.add_argument("--block-code")
   ```

   Update Implementation Surface to list cli.py as required, not "不应该需要修改".

2. **Document the re-run failure scenario.** The export preset's `overwrite: false` means the bundle is not idempotent. Add to Error Semantics: "If `runtime/exports/zxg.json` already exists from a prior run, step 3 fails with overwrite protection. Delete the file or use `catalog run --only-step 1` or `--only-step 2` for read-only re-runs."

3. **Clarify `read-zxg-review` dependency status.** Line 22 lists it as an existing bundle, but it doesn't exist in `command-bundles.json` yet. If this spec depends on the review-only bundle being implemented first, state that explicitly. If they're independent, note that line 22 refers to a planned (not yet shipped) bundle.

## Scoring

| Dimension | Score (1-5) | Evidence |
|-----------|-------------|----------|
| Technical Accuracy | 3 | Decision 3's `--block-code` interface not supported by existing parser. Default-path analysis correct. |
| Completeness | 4 | Strong test boundaries and error semantics. Missing overwrite-behavior note and prerequisite clarification. |
| Codebase Alignment | 4 | Bundle JSON and dispatch path aligned. Parser gap and missing `read-zxg-review` bundle are exceptions. |
| Actionability | 3 | Implementation Surface misclassifies required cli.py change. Prerequisite dependency on companion spec unclear. |
| Terminology Consistency | 5 | All terms match codebase. Consistent throughout. |
| **Overall** | **3.8** | |

## Verdict

**NEEDS_REVISION** -- The `--block-code` parser gap (same as the companion review-only bundle spec) makes Decision 3 unimplementable, and the Implementation Surface explicitly contradicts this by listing cli.py as "不应该需要修改". Additionally, the Context section references `read-zxg-review` as an existing bundle when it has not been implemented. These must be corrected before implementation.
