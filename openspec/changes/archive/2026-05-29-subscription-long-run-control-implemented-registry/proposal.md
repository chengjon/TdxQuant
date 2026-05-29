## Why

B-16 and E-09 have accumulated implemented evidence for the subscription watch long-run control surface: persisted start requests, explicit restart, restart preflight, restart observation, bounded restart backoff, supervisor tick/run, supervisor daemon start/status/stop, statefile ownership diagnostics, lifecycle readiness, diagnostics, and operator runbook projections. `FUNCTION_TREE.md` still keeps both main rows at `[部分实现]` and leaves most of that evidence in supplemental notes, which makes the single feature registry harder to read and can imply the lifecycle work is still mostly pending.

## What Changes

- Promote B-16 and E-09 in `FUNCTION_TREE.md` from `[部分实现]` to `[已实现]`.
- Rewrite their main-row evidence so the implemented subscription watch control surface is visible in the registry itself.
- Preserve strict boundaries: implemented means explicit operator-managed subscription watch lifecycle control and diagnostics, not automatic production recovery, live provider availability, broker readiness, trading readiness, or a workflow builder.
- Add a focused registry test that prevents B-16/E-09 from silently drifting back to partial/stale wording.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-function-tree-registry`: B-16/E-09 may be registered as implemented when the subscription watch lifecycle control evidence is present and the boundary prevents overclaiming runtime/provider/trading readiness.

## Impact

- Affected registry: `FUNCTION_TREE.md`.
- Affected tests: `tests/test_function_tree_registry.py`.
- Verification: focused registry tests, focused subscription/bridge/CLI tests, OpenSpec strict validation, whitespace check, and FUNCTION_TREE registry validation.
