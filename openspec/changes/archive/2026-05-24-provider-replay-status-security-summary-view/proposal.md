## Why

`provider-replay status --view summary` now exposes compact lifecycle, capability, probe, and replay-source evidence. The detailed status also contains replay security boundaries, but the summary view does not currently project them.

E-06 records the fake provider as a partial, boundary-sensitive capability. A compact status summary should show that bearer-token and allowlist controls are configured without exposing secrets or allowlist members.

## What Changes

- Add `summary_view.security` to provider replay status summary output.
- Include:
  - `bearer_token_required`
  - `source_allowlist_enabled`
  - `master_allowlist_count`
- Continue omitting bearer token values and full allowlist members.
- Preserve existing no-daemon-management and explicit-probe-only behavior.

## Capabilities

### Modified Capabilities

- `tdx-provider-transport-replay-service`: provider replay status summary exposes compact security boundary metadata.

## Impact

- Code: `tdxquant/cli.py`
- Tests: `tests/test_api_cli.py`
- Docs/registry: `FUNCTION_TREE.md`
