# Review: 2026-05-08-catalog-block-read-watchlist-review-bundle-design.md

**Type**: `.md` / `spec` | **Perspective**: `auto` (arch + completeness + consistency) | **Date**: 2026-05-08 | **Reviewer**: Claude

---

## Executive Summary

The spec proposes a well-structured two-step read-only bundle (`read-zxg-review`) that correctly reuses the existing bundle infrastructure. All referenced files, catalog entries, presets, and symbols exist in the codebase. However, Decision 3's core interface contract (`--block-code` bundle-level override) is not implementable without adding `--block-code` to `_add_catalog_run_arguments` in `cli.py` -- a change the Implementation Surface section frames as conditional rather than required.

## Document Metadata

| Field | Value |
|-------|-------|
| Source | `docs/superpowers/specs/2026-05-08-catalog-block-read-watchlist-review-bundle-design.md` |
| File Type | `.md` |
| Doc Type | `spec` |
| Sections | 12 (Context, Goals, Non-Goals, Decisions 1-5, Error Semantics, Implementation Surface, Test Boundaries, Migration Plan, Open Questions) |
| Referenced Files | 3 found / 0 missing |
| Referenced Symbols | 7 found / 0 missing |

## Evidence Verification

### Files Referenced

| File | Exists? | Location |
|------|---------|----------|
| `runtime/command-bundles.json` | yes | `/opt/iflow/TdxQuant/runtime/command-bundles.json` |
| `runtime/command-catalog.json` | yes | `/opt/iflow/TdxQuant/runtime/command-catalog.json` |
| `runtime/task-presets.json` | yes | `/opt/iflow/TdxQuant/runtime/task-presets.json` |

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

### Claims Verified

| Claim | Status | Evidence |
|-------|--------|----------|
| Bundle schema uses `description`, `labels`, `steps` (with `name`, `entry`, optional `options`) | confirmed | `runtime/command-bundles.json:1-362` -- all existing bundles follow this structure |
| `resolve_command_bundle(...)` resolves each step's entry against the catalog | confirmed | `tdxquant/catalog.py:121-132` -- calls `resolve_command_catalog_entry(entry_name, entries=available_entries)` for each step |
| `catalog plan --bundle` and `catalog run --bundle` exist | confirmed | `tdxquant/cli.py:588-598` -- both subparsers registered with `_add_catalog_run_arguments` |
| `--from-step / --to-step / --only-step` are supported | confirmed | `tdxquant/cli.py:516-518` -- registered in `_add_catalog_run_arguments` |
| Bundle step failure stops subsequent steps | confirmed | `tdxquant/cli.py:2988-2991` -- `if not step_result.ok: ... break` |
| `read-zxg-watchlist` preset has `block_code: "ZXG"` default | confirmed | `runtime/task-presets.json:88-95` -- `options: {"block_code": "ZXG"}` |
| `read-zxg-full` preset has `block_code: "ZXG"` default | confirmed | `runtime/task-presets.json:96-102` -- `options: {"block_code": "ZXG"}` |
| `block-read-watchlist` is in `TASK_COMMAND_DEFAULT_PROFILES` | confirmed | `tdxquant/tasking.py:18` -- `"block-read-watchlist": "default"` |
| `block-read-full` is in `TASK_COMMAND_DEFAULT_PROFILES` | confirmed | `tdxquant/tasking.py:20` -- `"block-read-full": "default"` |
| `--block-code` is available on the catalog run/plan parser | **contradicted** | `tdxquant/cli.py:514-573` -- `_add_catalog_run_arguments` does NOT include `--block-code`. Only `--required-block-code` (line 547). |
| Default path (no `--block-code`) resolves `block_code` from preset | confirmed | `tdxquant/cli.py:3566-3568` -- `_build_task_preset_namespace` merges `resolved_preset.get("options", {})`, which includes `block_code: "ZXG"` |
| `_build_catalog_bundle_step_namespace` propagates top-level args to each step | confirmed | `tdxquant/cli.py:2328-2335` -- `merged = dict(vars(args))` copies all parsed args, step options only fill gaps |

## Checklist Results

### Architecture

| # | Check | Result | Notes |
|---|-------|--------|-------|
| A1 | Component boundaries | PASS | Bundle = orchestration only; no new business logic. Preset = parameter storage. Catalog entry = discovery. |
| A2 | Data flow | PASS | `catalog run --bundle read-zxg-review` -> `_run_catalog_bundle` -> per-step `_dispatch_catalog_resolved_entry(source="task")` -> `_handle_task_subcommand` |
| A3 | Coupling | PASS | Bundle only references entry names; no duplication of block_code or other defaults |
| A4 | Interface contracts | FAIL | Decision 3 specifies `--block-code` as bundle-level override, but `_add_catalog_run_arguments` (cli.py:514-573) does not register this argument. argparse will reject `--block-code` before dispatch |
| A5 | Scalability | PASS | Adding one bundle to a flat JSON registry; no scaling concern |
| A6 | Terminology consistency | PASS | Terms (`bundle`, `entry`, `step`, `preset`, `catalog plan/run`) used consistently and match codebase |
| A7 | Backward compatibility | PASS | Non-Goals explicitly state "不新增 bundle schema"; addition-only change |
| A8 | Implementation surface precision | FAIL | Required cli.py change (adding `--block-code` to `_add_catalog_run_arguments`) is framed as conditional ("如测试暴露真实缺口") when it is provably required for Decision 3 |
| A9 | Named entities verified | PASS | All 7 referenced symbols verified as existing in the codebase |

### Completeness

| # | Check | Result | Notes |
|---|-------|--------|-------|
| C1 | Required sections | PASS | Context, Goals, Non-Goals, 5 Decisions, Error Semantics, Implementation Surface, Test Boundaries, Migration Plan, Open Questions all present |
| C2 | Edge cases | PASS | Error Semantics section covers 5 failure scenarios; Decision 4 explicitly defers to existing failure semantics |
| C3 | Implicit assumptions | PASS | Assumes `read-zxg-watchlist` catalog entry exists (confirmed); assumes bundle infrastructure is stable (confirmed) |
| C4 | Acceptance criteria | PARTIAL | Test Boundaries (lines 237-253) specify 9 verifiable cases, but lines 245-250 depend on `--block-code` which is not available in the parser |
| C5 | Missing roles/stakeholders | N/A | Single-bundle addition; no multi-stakeholder concern |

### Consistency

| # | Check | Result | Notes |
|---|-------|--------|-------|
| N1 | Terminology | PASS | `read-zxg-review` used consistently as bundle name; step names (`snapshot`, `full`) consistent throughout |
| N2 | Naming conventions | PASS | Bundle name follows existing pattern; step `entry` values match catalog entry keys |
| N3 | Formatting | PASS | Consistent heading hierarchy, numbered decisions, code blocks |
| N4 | Cross-references | PASS | Decisions 1-5 cross-reference each other and Context consistently |
| N5 | Style consistency | PASS | Uniform style throughout |

## Findings

### Critical Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 1 | Decision 3 + Implementation Surface | `--block-code` is not registered in `_add_catalog_run_arguments` (cli.py:514-573). argparse will reject `catalog plan --bundle read-zxg-review --block-code MYZXG` and `catalog run --bundle read-zxg-review --block-code MYZXG` with "unrecognized arguments". This makes Decision 3's core interface contract unimplementable as written. The Implementation Surface (line 220) frames the required cli.py change as conditional ("如测试暴露真实缺口") when it is provably required. | Test Boundaries lines 245-250 cannot pass. Decision 3's `--block-code` override is the primary user-facing feature beyond the default path. | Codebase: `_add_catalog_run_arguments` at cli.py:514-573 has no `--block-code`. Only `--required-block-code` at line 547. Main entry uses `parser.parse_args()` (cli.py:3991), not `parse_known_args`. No existing bundle test uses `--block-code` (grep confirmed). Doc: searched for any mention of parser modification or `_add_catalog_run_arguments` -- none found. Implementation Surface says "如测试暴露真实缺口，再最小改动" (conditional) rather than "必须添加 --block-code" (required). | (1) Add `--block-code` to `_add_catalog_run_arguments` in cli.py. (2) Update Implementation Surface to list this as a required change, not conditional. (3) The mechanism will then work: `_build_catalog_bundle_step_namespace` at cli.py:2329 copies `args.block_code` to each step namespace, and `_build_task_preset_namespace` at cli.py:3567 only fills `block_code` when it's missing/None, so the bundle-level override takes precedence. |

### Low Issues

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 1 | Migration Plan:step 4 | "同步更新 task usage / function map / next steps" is vague about which files/documents to update | Codebase: no specific target files identified. Doc: searched for specifics on what "task usage" or "function map" refers to -- no detail. | Specify which docs or files need updating (e.g., `openspec/specs/tdx-command-catalog/spec.md`, CLI help text). |
| 2 | Migration Plan:step 5 | "再补这条 bundle 的 OpenSpec lifecycle" is vague about what lifecycle steps are needed | Codebase: existing bundles have archived changes in `openspec/changes/archive/`. Doc: no specification of which lifecycle documents to create. | Note that a new change directory (e.g., `openspec/changes/add-read-zxg-review-bundle/`) with proposal, design, and tasks is expected, matching the pattern of archived bundle changes. |

## Strengths

- Precise scope control: 9 explicit Non-Goals prevent scope creep into export, report, write-back, batch processing, and distributed execution.
- Concrete example JSON: Decision 1 provides the exact bundle definition to add, making the primary artifact unambiguous.
- Comprehensive error semantics: 5 failure scenarios documented with explicit statement that no new error schema is introduced.
- Clear test boundaries: 9 specific test cases with pass/fail criteria, plus 4 explicit exclusions (replay fixture, report, export, multi-block).
- Correct default-path analysis: The doc correctly identifies that preset defaults (`block_code=ZXG`) will flow through `_build_task_preset_namespace` without requiring explicit per-step configuration.

## Detailed Recommendations

1. **Add `--block-code` to `_add_catalog_run_arguments` as a required change.** This is the most critical fix. The change is a single line in `_add_catalog_run_arguments` (cli.py:514-573):

   ```python
   subparser.add_argument("--block-code")
   ```

   This must be listed in Implementation Surface as a **required** change, not conditional. The propagation mechanism already works: `_build_catalog_bundle_step_namespace` copies all parsed args to each step namespace, and `_build_task_preset_namespace` only fills `block_code` from preset defaults when it's missing. So the bundle-level `--block-code MYZXG` will correctly override both steps.

2. **Update Implementation Surface to separate required from conditional changes.** Current wording ("如测试暴露真实缺口，再最小改动") groups a known-required change (adding `--block-code`) with genuinely conditional ones. Recommended structure:

   ```
   Required changes:
   - runtime/command-bundles.json: add read-zxg-review
   - tdxquant/cli.py: add --block-code to _add_catalog_run_arguments
   
   Conditional (only if tests reveal gaps):
   - tdxquant/catalog.py
   ```

3. **Specify Migration Plan targets for steps 4-5.** Step 4 should name the specific documents to update (e.g., `openspec/specs/tdx-command-catalog/spec.md`). Step 5 should note the expected change directory pattern matching `openspec/changes/archive/2026-05-0*-catalog-block-*`.

## Scoring

| Dimension | Score (1-5) | Evidence |
|-----------|-------------|----------|
| Technical Accuracy | 3 | Decision 3's `--block-code` interface is not supported by the existing catalog parser. Default-path analysis is correct. |
| Completeness | 4 | Strong test boundaries and error semantics. Missing parser-gap identification is the only gap. |
| Codebase Alignment | 4 | Bundle JSON, schema, and dispatch path all aligned. Parser gap is the sole exception. |
| Actionability | 3 | Implementation Surface misclassifies a required change as conditional, which risks an implementer missing it. |
| Terminology Consistency | 5 | All terms match codebase. `read-zxg-review`, step names, and entry references consistent throughout. |
| **Overall** | **3.8** | |

## Verdict

**NEEDS_REVISION** -- The `--block-code` parser gap makes Decision 3's core contract unimplementable without a cli.py change that the Implementation Surface frames as conditional. The fix is a single line (`subparser.add_argument("--block-code")` in `_add_catalog_run_arguments`), but the doc must explicitly acknowledge it as required rather than conditional. All other aspects of the spec are well-structured and aligned with the codebase.
