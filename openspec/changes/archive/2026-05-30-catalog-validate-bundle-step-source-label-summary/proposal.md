## Why

E-11 already registers task/report bundle discovery and several stable source/name/count summaries, but maintainers still cannot answer a common read-only question from one field: which step sources appear under which bundle labels. Adding source-label counts keeps FUNCTION_TREE evidence precise without implying workflow execution.

## What Changes

- Add `bundle_step_source_label_counts` and key-count fields to `catalog validate --kind bundle --view summary`.
- Add task/report-specific `task_report_bundle_step_source_label_counts` so E-11 can cite source-label coverage for task/report combo bundles.
- Update tests and `FUNCTION_TREE.md` evidence while keeping E-11 `[部分实现]`.
- Preserve the boundary: this is catalog structure validation only, not `catalog run`, not a workflow builder, and not task/report/trade execution.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-command-catalog`: add read-only source-label bundle step summary fields for catalog validation.
- `tdx-function-tree-registry`: register the E-11 evidence and non-execution boundary for the new summary fields.

## Impact

- Affected code: `tdxquant/cli.py`.
- Affected registry: `FUNCTION_TREE.md`.
- Affected tests: `tests/test_api_cli.py`, `tests/test_function_tree_registry.py`.
- Verification: focused API CLI and registry tests, OpenSpec strict validation, whitespace check, and FUNCTION_TREE registry validation.
