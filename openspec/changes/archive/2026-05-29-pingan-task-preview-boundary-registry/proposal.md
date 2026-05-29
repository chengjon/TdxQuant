## Why

D-07 now records `catalog plan` boundaries for PingAn task buy/sell/confirm-current, but the same non-executing boundary is also available through `catalog preview`. The registry should show both read-only inspection modes so users do not infer that preview is unsupported or that they must execute a workflow to inspect the inputs.

## What Changes

- Add focused catalog preview tests for `task-buy` and `task-confirm-current` summary boundaries.
- Update D-07 evidence to say `catalog plan/preview` for the PingAn task entries.
- Preserve the non-goals: no `catalog run` expansion, no direct `trade-buy` / `trade-sell` catalog run entry, no broker readiness or trading safety claim.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-command-catalog`: documents read-only preview parity for PingAn task trade boundaries.
- `tdx-function-tree-registry`: D-07 evidence reflects plan/preview parity without changing execution status.

## Impact

- Affected registry: `FUNCTION_TREE.md`.
- Affected tests: `tests/test_api_cli.py`, `tests/test_function_tree_registry.py`.
- Verification: focused API CLI and registry tests, OpenSpec strict validation, whitespace check, and FUNCTION_TREE registry validation.
