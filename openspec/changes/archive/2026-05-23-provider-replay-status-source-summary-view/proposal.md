## Why

`provider-replay status --view summary` already projects lifecycle, probe, and capability boundaries, but it does not identify the replay source in the compact payload. The detailed status includes `replay_source`, so callers can tell whether the fake provider is using default fixture resolution, a built-in fixture, or a fixture path only by inspecting the full detailed object.

E-06 tracks the fake provider as partial and boundary-sensitive. The summary view should expose a bounded source marker without copying full fixture path detail or implying daemon/runtime ownership.

## What Changes

- Add `summary_view.replay_source` to provider replay status summary output.
- Include:
  - `source_kind`
  - `fixture`
  - `fixture_path_provided`
- Continue omitting the full fixture path from status summary view.
- Preserve existing probe, capability, lifecycle, and no-daemon-management behavior.

## Capabilities

### Modified Capabilities

- `tdx-provider-transport-replay-service`: provider replay status summary exposes compact replay-source provenance.

## Impact

- Code: `tdxquant/cli.py`
- Tests: `tests/test_api_cli.py`
- Docs/registry: `FUNCTION_TREE.md`
