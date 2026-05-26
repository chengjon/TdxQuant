# Add catalog plan step entry counts

## Why

Catalog bundle plan/preview summary views now expose selected step source and name distributions. They still require callers to scan selected steps to understand which catalog entries are referenced by the selected plan/preview slice.

E-11 remains partial task/report combination registry work in `FUNCTION_TREE.md`. A read-only selected step entry rollup improves compact diagnostics without creating a workflow builder or changing catalog execution.

## What Changes

- Add read-only `step_entry_counts` to bundle `catalog plan --view summary` and `catalog preview --view summary` payloads.
- Add read-only `step_entry_key_count` derived from the number of keys in `step_entry_counts`.
- Preserve existing selected step list, `selected_step_count`, `step_source_counts`, `step_source_key_count`, `step_name_counts`, `step_name_key_count`, provenance, constraints, and trade boundary projection.
- Do not execute catalog entries, tasks, reports, trades, or bundle steps.

## Capabilities

### Modified Capabilities

- `tdx-command-catalog`

## Impact

- Touches `tdxquant/cli.py` catalog summary projection only.
- Adds focused API CLI tests for plan and preview summary views.
- Updates `FUNCTION_TREE.md` as the single registry with explicit status, evidence, and boundary.

