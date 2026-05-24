## Why

E-06 tracks the daemon fake provider as a partial, read-only replay transport. The current status summary exposes endpoint count and bounded samples, but maintainers still need a compact way to see which replay route families are represented without exposing the full endpoint list.

## What Changes

- Add `summary_view.capabilities.endpoint_family_counts` to `provider-replay status --view summary`.
- Derive the counts from the detailed `capabilities.endpoints` list.
- Keep the summary read-only and non-lifecycle-managing: no socket start, daemonization, scheduling, supervision, or implicit probes.
- Update focused CLI tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence/boundary text.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-provider-transport-replay-service`: provider replay status summary exposes compact endpoint family counts.

## Impact

- Code: `tdxquant/cli.py`
- Tests: `tests/test_api_cli.py`
- Specs: `openspec/specs/tdx-provider-transport-replay-service/spec.md`
- Registry: `FUNCTION_TREE.md` remains the single feature/status registry.
