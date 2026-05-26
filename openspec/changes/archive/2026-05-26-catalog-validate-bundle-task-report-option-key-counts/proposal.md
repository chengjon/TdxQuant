## Why

Catalog validate summary view already exposes selected bundle and task+report bundle option-key and source-qualified option-key count maps. Explicit key-count fields complete the summary registry symmetry with submit-once/PingAn option-key key counts and avoid forcing callers to recompute map lengths.

## What Changes

- Add `bundle_step_option_key_count` derived from `bundle_step_option_key_counts`.
- Add `bundle_step_source_option_key_count` derived from `bundle_step_source_option_key_counts`.
- Add `task_report_bundle_step_option_key_count` derived from `task_report_bundle_step_option_key_counts`.
- Add `task_report_bundle_step_source_option_key_count` derived from `task_report_bundle_step_source_option_key_counts`.
- Keep all fields read-only and non-executing; they do not expose option values, execute steps, validate option semantics, or prove workflow coverage/readiness.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-command-catalog`: Catalog validate summary view exposes selected bundle and task+report option-key/source-option-key key-count fields derived from already projected count maps.

## Impact

- `tdxquant/cli.py`: summary view projection adds four derived count fields.
- `tests/test_api_cli.py`: catalog validate summary tests assert the new fields and non-execution behavior.
- `FUNCTION_TREE.md`: E-11 evidence/boundary registry is updated without promoting the node to fully implemented.
