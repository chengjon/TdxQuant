# Review: 2026-05-07-catalog-block-read-watchlist-entry-design.md

**Type**: `.md` / `spec` | **Perspective**: `auto` (arch + completeness + consistency) | **Date**: 2026-05-07 | **Reviewer**: Claude

---

## Executive Summary

The spec is technically accurate and well-aligned with the existing codebase. All referenced files, functions, and infrastructure exist. The change is a straightforward addition of a single `read-zxg-watchlist` entry to `command-catalog.json`, following an established pattern already used by `export-zxg-watchlist` and `read-zxg-full`. The main gap is the absence of a concrete JSON snippet in the implementation surface.

## Document Metadata

| Field | Value |
|-------|-------|
| Source | `docs/superpowers/specs/2026-05-07-catalog-block-read-watchlist-entry-design.md` |
| File Type | `.md` |
| Doc Type | `spec` |
| Sections | 6 (Context, Goals/Non-Goals, Decisions, Risks/Trade-offs, Migration Plan, Open Questions) |
| Referenced Files | 2 found / 0 missing |
| Referenced Symbols | 8 found / 0 missing |

## Evidence Verification

### Files Referenced

| File | Exists? | Location |
|------|---------|----------|
| `runtime/command-catalog.json` | yes | `/opt/iflow/TdxQuant/runtime/command-catalog.json` |
| `runtime/task-presets.json` | yes | `/opt/iflow/TdxQuant/runtime/task-presets.json` |
| `openspec/specs/tdx-command-catalog/spec.md` | yes | `/opt/iflow/TdxQuant/openspec/specs/tdx-command-catalog/spec.md` |

### Functions/Classes/Symbols Referenced

| Symbol | Found? | Location |
|--------|--------|----------|
| `TdxTaskManager.block_read_watchlist(...)` | yes | `tdxquant/api/task.py:1126` |
| `catalog list` (subcommand) | yes | `tdxquant/cli.py:579` |
| `catalog plan` (subcommand) | yes | `tdxquant/cli.py:594` |
| `catalog run` (subcommand) | yes | `tdxquant/cli.py:588` |
| `resolve_command_catalog_entry(...)` | yes | `tdxquant/catalog.py:60` |
| `_dispatch_catalog_resolved_entry(...)` | yes | `tdxquant/cli.py:2307` |
| `_plan_catalog_resolved_entry(...)` | yes | `tdxquant/cli.py:2748` |
| `_build_task_preset_namespace(...)` | yes | `tdxquant/cli.py:3559` |

### Claims Verified

| Claim | Status | Evidence |
|-------|--------|----------|
| `read-zxg-watchlist` preset exists with `block_code=ZXG` | confirmed | `runtime/task-presets.json:88-95` — preset has `command: "block-read-watchlist"`, `api_profile: "safe_read"`, `options.block_code: "ZXG"` |
| `block-read-watchlist` is a valid task command | confirmed | `tdxquant/tasking.py:18` — `TASK_COMMAND_DEFAULT_PROFILES` includes `"block-read-watchlist": "default"` |
| `"task"` is a supported catalog source | confirmed | `tdxquant/catalog.py:8` — `SUPPORTED_COMMAND_CATALOG_SOURCES = frozenset({"report", "task", "trade"})` |
| `catalog run` dispatches `source: "task"` to `_handle_task_subcommand` | confirmed | `tdxquant/cli.py:2313-2314` — `elif source == "task": result = _handle_task_subcommand(forwarded)` |
| `catalog plan` resolves preset defaults including `block_code` | confirmed | `tdxquant/cli.py:2743-2744` routes to `_build_task_preset_namespace`, which merges `resolved_preset.get("options", {})` at line 3566-3568 |
| `command-catalog.json` already has analogous entries (`export-zxg-watchlist`, `read-zxg-full`) | confirmed | `runtime/command-catalog.json:218-229` — both exist as `source: "task"` entries |
| `read-zxg-watchlist` is currently absent from `command-catalog.json` | confirmed | `runtime/command-catalog.json` — no such key exists; the entry is the proposed addition |
| Tests exist for analogous entries (list, run dispatch, plan) | confirmed | `tests/test_api_cli.py:2548-2768` — covers `export-zxg-watchlist` and `read-zxg-full` for list, run, and plan |

## Checklist Results

### Architecture

| # | Check | Result | Notes |
|---|-------|--------|-------|
| A1 | Component boundaries | PASS | Clear separation: catalog entry = discovery view, preset = parameter storage, dispatch = existing task path |
| A2 | Data flow | PASS | `catalog run --entry read-zxg-watchlist` -> `resolve_command_catalog_entry` -> `_dispatch_catalog_resolved_entry(source="task")` -> `_handle_task_subcommand(preset="read-zxg-watchlist")` |
| A3 | Coupling | PASS | Entry only references preset name; no duplication of block_code or other defaults |
| A4 | Interface contracts | PASS | `source/preset/description/labels` schema matches `resolve_command_catalog_entry` expectations at `catalog.py:72-89` |
| A5 | Scalability | PASS | Adding one entry to a flat JSON catalog; no scaling concern |
| A6 | Terminology consistency | PASS | Terms (`entry`, `preset`, `source`, `catalog plan`, `catalog run`) used consistently and match codebase |
| A7 | Backward compatibility | PASS | Non-Goals explicitly state "不修改 catalog schema"; addition-only change |
| A8 | Implementation surface precision | FAIL | Migration Plan step 1 says "新增 read-zxg-watchlist task source entry" but does not provide the concrete JSON to add. Compare with `export-zxg-watchlist` and `read-zxg-full` entries which follow `source/preset/description/labels`. The implementer must infer the exact entry from existing examples. |
| A9 | Named entities verified | PASS | All 8 referenced symbols verified as existing in the codebase |

### Completeness

| # | Check | Result | Notes |
|---|-------|--------|-------|
| C1 | Required sections | PASS | Context, Goals/Non-Goals, Decisions, Risks, Migration Plan, Open Questions all present |
| C2 | Edge cases | N/A | Single-entry addition with no edge cases beyond normal catalog validation |
| C3 | Implicit assumptions | PASS | Assumes preset infrastructure is stable (confirmed); assumes existing dispatch paths handle task source (confirmed at cli.py:2313-2314) |
| C4 | Acceptance criteria | PASS | Decisions 3 and 4 specify verifiable outcomes: `catalog plan --entry read-zxg-watchlist` shows `block_code=ZXG`; `catalog run --entry read-zxg-watchlist` dispatches through preset-backed task path |
| C5 | Missing roles/stakeholders | N/A | Single-entry addition; no multi-stakeholder concern |

### Consistency

| # | Check | Result | Notes |
|---|-------|--------|-------|
| N1 | Terminology | PASS | `read-zxg-watchlist` used consistently throughout; matches preset key in `task-presets.json` |
| N2 | Naming conventions | PASS | Entry name matches preset name, following established pattern (`export-zxg-watchlist`, `read-zxg-full`) |
| N3 | Formatting | PASS | Consistent heading hierarchy, list style, and code block usage |
| N4 | Cross-references | PASS | Internal references to Decisions and Migration Plan steps resolve correctly |
| N5 | Style consistency | PASS | Uniform style throughout |

## Findings

### Medium Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 1 | Migration Plan:step 1 | No concrete JSON entry provided for the `read-zxg-watchlist` catalog addition | Implementer must infer the entry from existing examples (`export-zxg-watchlist`, `read-zxg-full`). Risk of inconsistency in `description` or `labels` values. | Codebase: `runtime/command-catalog.json:218-229` has two analogous entries with identical `source: "task"` and consistent structure. Doc: searched for JSON snippet or entry definition — none found in any section. | Add the exact JSON entry to Migration Plan step 1, e.g.: `"read-zxg-watchlist": { "source": "task", "preset": "read-zxg-watchlist", "description": "统一入口下的 ZXG 板块标准化快照读取模板。", "labels": ["task", "block", "watchlist", "read"] }` |

### Low Issues

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 1 | Migration Plan:step 2 | Test specification is generic ("增加 catalog list / plan / run focused tests") without enumerating specific test cases | Codebase: `tests/test_api_cli.py:2548-2768` has 10 test methods for `export-zxg-watchlist` and `read-zxg-full` catalog coverage. Doc: step 2 provides no test names or assertions. | Enumerate at least: (1) list includes `read-zxg-watchlist`, (2) `--entry read-zxg-watchlist` returns metadata, (3) `catalog run --entry read-zxg-watchlist` dispatches through task subcommand, (4) `catalog plan --entry read-zxg-watchlist` shows resolved `block_code=ZXG`. |
| 2 | Migration Plan:step 3 | "同步 tdx-command-catalog 主 spec" lacks detail on what to update | Codebase: `openspec/specs/tdx-command-catalog/spec.md` exists. Doc: no specification of what content changes are needed. | Add a brief note: "Add `read-zxg-watchlist` to the supported entries list and verify no schema changes needed." |

## Strengths

- Precise scope control: Non-Goals section explicitly excludes catalog schema changes, new subcommands, inline parameters, and preset CRUD — this prevents scope creep.
- Accurate infrastructure claims: Every referenced function, file, and command was verified as existing in the codebase.
- Clear decision trail: Four numbered decisions with explicit rationale, each pointing to existing code patterns rather than introducing new abstractions.
- Risk mitigation strategy: Each risk in Risks/Trade-offs includes a concrete mitigation through existing design constraints.
- Pattern consistency: The proposed entry follows the exact same `source/preset/description/labels` structure as `export-zxg-watchlist` and `read-zxg-full`.

## Detailed Recommendations

1. **Add concrete JSON to Migration Plan step 1.** The most impactful improvement. A 5-line JSON snippet eliminates ambiguity and matches the precedent set by analogous entries at `runtime/command-catalog.json:218-229`. Suggested entry:

   ```json
   "read-zxg-watchlist": {
     "source": "task",
     "preset": "read-zxg-watchlist",
     "description": "统一入口下的 ZXG 板块标准化快照读取模板。",
     "labels": ["task", "block", "watchlist", "read"]
   }
   ```

   Labels `["task", "block", "watchlist", "read"]` follow the pattern of `read-zxg-full` at line 224-229 which uses `["task", "block", "watchlist", "read"]`.

2. **Enumerate test cases in Migration Plan step 2.** The existing test suite (`tests/test_api_cli.py:2548-2768`) provides a clear pattern with four test categories per entry: list inclusion, metadata retrieval, run dispatch, and plan resolution. Adding the corresponding four test names for `read-zxg-watchlist` would make the step self-contained.

3. **Clarify Migration Plan step 3.** Specify whether the `tdx-command-catalog` spec needs a new entry in its supported-entries list, or just a cross-reference update. This is a minor point but would eliminate the need for the implementer to read the spec to determine the scope of the sync.

## Scoring

| Dimension | Score (1-5) | Evidence |
|-----------|-------------|----------|
| Technical Accuracy | 5 | All 8 referenced symbols verified. All claims confirmed against codebase. Zero factual errors. |
| Completeness | 3 | Missing concrete JSON entry (A8 failure). Missing specific test enumeration. Migration Plan steps 2-3 are high-level directives rather than actionable specifications. |
| Codebase Alignment | 5 | Perfect alignment with existing `source: "task"` pattern. Follows `export-zxg-watchlist` and `read-zxg-full` conventions exactly. |
| Actionability | 4 | Migration Plan provides clear 4-step sequence. Steps 2-3 could be more specific but are implementable with existing codebase context. |
| Terminology Consistency | 5 | All terms match codebase. `read-zxg-watchlist` used consistently as preset name, catalog entry key, and CLI argument value. |
| **Overall** | **4.4** | |

## Verdict

**APPROVE_WITH_NOTES** — The spec is technically accurate, well-scoped, and perfectly aligned with existing codebase patterns. Adding a concrete JSON snippet to Migration Plan step 1 would bring the implementation surface to the same precision level as the design decisions. The change is a straightforward single-entry addition with no architectural risk.
