# Add catalog plan step name counts

## Why

Catalog bundle `plan` and `preview` summary views expose selected steps and source counts, but callers still need to scan the selected step list to understand the distribution of step names. E-11 remains partial task/report combination registry work in `FUNCTION_TREE.md`, and a read-only step-name rollup improves compact plan/preview diagnostics without changing execution behavior.

## What Changes

- Add read-only `step_name_counts` to bundle `catalog plan --view summary` and `catalog preview --view summary` payloads.
- Add read-only `step_name_key_count` derived from the number of keys in `step_name_counts`.
- Preserve existing selected step list, `selected_step_count`, `step_source_counts`, `step_source_key_count`, provenance, constraints, and trade boundary projection.
- Do not execute catalog entries, tasks, reports, trades, or bundle steps.

## Capabilities

### Modified Capabilities

- `tdx-command-catalog`

## Impact

- Touches `tdxquant/cli.py` catalog summary projection only.
- Adds focused API CLI tests for plan and preview summary views.
- Updates `FUNCTION_TREE.md` as the single registry with explicit status, evidence, and boundary.

