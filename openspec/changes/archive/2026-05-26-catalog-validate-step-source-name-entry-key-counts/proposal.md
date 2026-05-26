## Why

Catalog validate summary view already exposes selected bundle and task+report bundle step `source:name` / `source:entry` count maps. Explicit key-count fields make these source-qualified projections consistent with the existing source, label, step name, and step entry key-count fields.

## What Changes

- Add `bundle_step_source_name_key_count` derived from `bundle_step_source_name_counts`.
- Add `bundle_step_source_entry_key_count` derived from `bundle_step_source_entry_counts`.
- Add `task_report_bundle_step_source_name_key_count` derived from `task_report_bundle_step_source_name_counts`.
- Add `task_report_bundle_step_source_entry_key_count` derived from `task_report_bundle_step_source_entry_counts`.
- Keep all fields read-only and non-executing; they do not expose full manifests, execute steps, or prove workflow coverage/readiness.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-command-catalog`: Catalog validate summary view exposes selected bundle and task+report source-qualified step name/entry key-count fields derived from already projected count maps.

## Impact

- `tdxquant/cli.py`: summary view projection adds four derived count fields.
- `tests/test_api_cli.py`: catalog validate summary tests assert the new fields and non-execution behavior.
- `FUNCTION_TREE.md`: E-11 evidence/boundary registry is updated without promoting the node to fully implemented.
