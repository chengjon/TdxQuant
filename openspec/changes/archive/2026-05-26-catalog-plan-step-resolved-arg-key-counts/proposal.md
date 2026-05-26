# Add catalog selected step resolved-arg key counts

## Why

`catalog plan|preview --bundle ... --view summary` already exposes selected step source, name, entry, and source-qualified count maps. It also includes reduced per-step `resolved_args`, but there is no aggregate map showing which resolved argument keys appear across the selected steps without reading every step object.

E-11 remains partial because the task/report bundle work is still non-executing catalog discovery and planning metadata, not a workflow builder or execution guarantee. A key-count summary improves inspectability while preserving the non-execution boundary.

## What Changes

- Add read-only `step_resolved_arg_key_counts` to bundle `catalog plan` and `catalog preview` summary views.
- Add read-only `step_resolved_arg_key_count`.
- Add read-only `step_source_resolved_arg_key_counts` and `step_source_resolved_arg_key_count`.
- Count only keys from selected steps' resolved argument maps; do not expose option values beyond the existing reduced per-step view.
- Do not execute catalog entries, tasks, reports, trades, or bundle steps.

## Capabilities

### Modified Capabilities

- `tdx-command-catalog`

## Impact

- Touches catalog summary projection helpers only.
- Adds focused CLI summary assertions.
- Updates `FUNCTION_TREE.md` as the single registry with explicit E-11 status, evidence, and boundary.
