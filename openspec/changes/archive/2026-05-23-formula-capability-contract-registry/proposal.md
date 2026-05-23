## Why

`formula.screen` now has a stable provider contract, fixtures, and tests, but the surrounding formula namespace still contains legacy bridge-only calls. Without an explicit per-capability registry, callers and `FUNCTION_TREE.md` readers can overgeneralize one stable contract into unsupported formula-provider guarantees.

## What Changes

- Add a formula capability contract registry that lists each public formula capability with status, evidence, replay/fixture support, and boundary notes.
- Expose the registry through `TdxApiManager.formula.capabilities()` so callers can inspect formula contract status without invoking formulas.
- Add a non-mutating CLI entry for formula capability status discovery.
- Update `FUNCTION_TREE.md` B-07/E-08 to point at this registry and keep bridge-only formula abilities explicitly outside provider-contract availability.

## Capabilities

### New Capabilities
- `tdx-formula-capability-contract-registry`: Per-formula capability contract status registry and discovery surface.

### Modified Capabilities
- None.

## Impact

- Affected code: formula registry module, manager formula proxy, API CLI parser/handler, focused tests, and `FUNCTION_TREE.md`.
- No external dependencies.
- No change to formula execution behavior, replay fixture payloads, or provider contract semantics for `formula.screen`.
