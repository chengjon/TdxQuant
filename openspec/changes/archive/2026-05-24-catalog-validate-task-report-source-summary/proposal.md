## Why

E-11 tracks fixed task/report bundle entry coverage in `FUNCTION_TREE.md`, but the current catalog validation summary only reports bundle counts and bounded bundle-name samples. Maintainers need a compact, non-executing way to confirm the resolved task/report step mix behind those bundles without reading the full detailed payload or implying execution readiness.

## What Changes

- Add `task_report_bundle_step_source_counts` to catalog validation results for selected bundles whose resolved steps include both `task` and `report` sources.
- Include the same aggregate counts in `catalog validate --kind bundle --label followup --view summary`.
- Keep the field strictly derived from resolved catalog metadata; no task, report, trade, or bundle step is executed.
- Update command-catalog specs, focused CLI tests, and `FUNCTION_TREE.md` E-11 evidence/boundary text.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-command-catalog`: catalog validation summary exposes compact task/report bundle step-source counts.

## Impact

- Code: `tdxquant/cli.py`
- Tests: `tests/test_api_cli.py`
- Specs: `openspec/specs/tdx-command-catalog/spec.md`
- Registry: `FUNCTION_TREE.md` remains the single feature/status registry.
