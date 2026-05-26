# Add catalog plan step source key count

## Why

Catalog bundle `plan` and `preview` summary views already expose `step_source_counts` for selected resolved steps. Automation can derive the number of distinct selected step sources from that map, but callers must currently parse the map to get the cardinality.

E-11 remains partial task/report combination registry work in `FUNCTION_TREE.md`. Adding a read-only `step_source_key_count` keeps plan/preview summaries easier to scan without changing catalog execution semantics.

## What Changes

- Add read-only `step_source_key_count` to bundle `catalog plan --view summary` and `catalog preview --view summary` payloads when `step_source_counts` is present.
- Derive the field from the number of keys in the selected-step `step_source_counts` map.
- Preserve existing `step_source_counts`, selected step metadata, provenance, constraints, and trade boundary projection.
- Do not execute catalog entries, tasks, reports, trades, or bundle steps.

## Capabilities

### Modified Capabilities

- `tdx-command-catalog`

## Impact

- Touches `tdxquant/cli.py` catalog summary projection only.
- Adds focused API CLI tests for plan and preview summary views.
- Updates `FUNCTION_TREE.md` as the single registry with explicit status, evidence, and boundary.

