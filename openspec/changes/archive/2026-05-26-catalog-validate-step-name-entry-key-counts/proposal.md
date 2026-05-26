## Why

Catalog validate summary view already exposes selected bundle and task+report bundle step name/entry count maps. Adding explicit key-count fields makes the summary registry consistent with existing source/label key-count projections and avoids requiring callers to recompute map lengths.

## What Changes

- Add `bundle_step_name_key_count` derived from `bundle_step_name_counts`.
- Add `bundle_step_entry_key_count` derived from `bundle_step_entry_counts`.
- Add `task_report_bundle_step_name_key_count` derived from `task_report_bundle_step_name_counts`.
- Add `task_report_bundle_step_entry_key_count` derived from `task_report_bundle_step_entry_counts`.
- Keep all fields read-only and non-executing; they do not expose full bundle/step manifests or execute entries, tasks, reports, trades, or bundle steps.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-command-catalog`: Catalog validate summary view exposes selected bundle and task+report step name/entry key-count fields derived from already projected count maps.

## Impact

- `tdxquant/cli.py`: summary view projection adds four derived count fields.
- `tests/test_api_cli.py`: catalog validate summary tests assert the new fields and non-execution behavior.
- `FUNCTION_TREE.md`: E-11 evidence/boundary registry is updated without promoting the node to fully implemented.
