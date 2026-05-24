## Why

E-11 catalog validation can count task+report bundles and summarize their step sources, but maintainers still cannot see how those fixed combinations are distributed across existing labels without inspecting the full bundle definitions. A compact label count keeps validation useful for registry audits while preserving the non-execution boundary.

## What Changes

- Add `task_report_bundle_label_counts` to `catalog validate` validation payloads.
- Derive counts from labels on already resolved task+report bundles.
- Project the same object through `catalog validate --view summary`.
- Preserve existing counts, bounded samples, source counts, and non-execution behavior.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-11 evidence and boundary text.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-command-catalog`: catalog validation summarizes labels attached to fixed task+report bundle combinations.

## Impact

- Code: `tdxquant/cli.py`
- Tests: `tests/test_api_cli.py`
- Specs: `openspec/specs/tdx-command-catalog/spec.md`
- Registry: `FUNCTION_TREE.md` remains the single feature/status registry.
