## Why

`catalog validate` already reports `task_report_bundle_count` and a bounded `task_report_bundle_samples` list for E-11. The current payload does not explicitly say that the samples are capped, so a reader can mistake the five ids for the complete task/report bundle inventory.

`FUNCTION_TREE.md` is the single feature registry, so catalog evidence should make the same boundary visible in machine-readable validation output: samples are deterministic representatives, not the full registry.

## What Changes

- Add explicit sample metadata to command catalog validation:
  - `task_report_bundle_sample_limit`
  - `task_report_bundle_sample_truncated`
- Project the same fields through `catalog validate --view summary`.
- Preserve the existing non-execution validation behavior and default detailed payload shape aside from the additive fields.

## Capabilities

### Modified Capabilities

- `tdx-command-catalog`: catalog validation declares whether representative task/report bundle samples were truncated.

## Impact

- Code: `tdxquant/cli.py`
- Tests: `tests/test_api_cli.py`
- Docs/registry: `FUNCTION_TREE.md`
