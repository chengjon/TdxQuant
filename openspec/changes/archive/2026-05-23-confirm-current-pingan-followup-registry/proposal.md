## Why

D-07 tracks Ping An buy/sell/confirm_current as partially implemented. The runtime catalog already exposes `task-confirm-current` and shorter `confirm-pingan-*` follow-up bundles, but the method identity is less visible than the newer side-explicit sell submit-once entries.

Adding `confirm-current-pingan-*` bundle aliases keeps `FUNCTION_TREE.md` truthful: readers can see a confirm_current follow-up entry exists without mistaking it for a new desktop primitive or a broader workflow builder.

## What Changes

- Add method-explicit Ping An confirm_current follow-up bundle aliases:
  - `confirm-current-pingan-exception-review`
  - `confirm-current-pingan-rejection-review`
  - `confirm-current-pingan-failure-review`
- Each alias composes the existing `task-confirm-current` catalog entry with the matching existing Ping An confirm audit report entry.
- Add catalog list/plan tests proving the aliases resolve without executing dispatch.
- Update `FUNCTION_TREE.md` D-07/E-11 evidence and boundary.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-command-catalog`: add method-explicit confirm_current Ping An follow-up bundle aliases.

## Impact

- Runtime config: `runtime/command-bundles.json`
- Tests: `tests/test_api_cli.py`
- Registry docs: `FUNCTION_TREE.md`
- Specs: `openspec/specs/tdx-command-catalog/spec.md`
