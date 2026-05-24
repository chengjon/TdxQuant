# Design

## Context

Catalog bundle planning already resolves selected bundle steps into `result.data["steps"]` and the summary view copies a reduced per-step payload for plan and preview modes. This gives detailed visibility, but callers that only need to classify a plan still have to scan every step to know whether the selected range is task-only, report-only, trade-only, or mixed.

## Goals

- Add compact source counts to bundle plan/preview summary views.
- Count only selected steps, respecting `--only-step`, `--from-step`, and `--to-step`.
- Preserve the existing `steps`, `provenance`, and `constraints` fields.
- Keep `catalog run` summary behavior unchanged.

## Non-Goals

- Do not add execution, dry-run execution, or provider probing.
- Do not infer whether a planned trade is available in a live broker environment.
- Do not modify runtime catalog or bundle schema files.
- Do not remove the detailed selected-step summary payload.

## Decisions

### 1. Derive counts inside the summary builder

The plan and preview handlers already resolve selected bundle steps before building the summary view. Computing `step_source_counts` from that resolved `steps` payload avoids duplicating bundle resolution logic and keeps selected-range behavior consistent with existing summary fields.

### 2. Use dispatch source as the count key

Each planned step includes `dispatch.source` and `dispatch.command_group`. Counting `dispatch.source` reflects the catalog entry source (`task`, `report`, `trade`) and matches the existing command catalog terminology.

### 3. Expose counts only for bundle plan/preview summaries

Entry plans have a single `dispatch` object and do not need step aggregation. Run summaries describe actual execution results and should not change as part of this non-execution visibility improvement.

## Risks / Trade-offs

- A caller could mistake source counts for execution evidence. The field is only emitted in plan/preview summaries that already include `constraints.execution_mode = "non_executing"` and `dispatch_executed = false`.
- Unknown or malformed step rows are ignored rather than reported. That matches the current summary builder's defensive behavior for reduced views.
