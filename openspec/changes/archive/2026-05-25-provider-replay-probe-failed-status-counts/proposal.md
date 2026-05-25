## Why

Provider replay probe summaries already expose requested status counts and failed target lists, but operators still need a compact distribution of only failed probe statuses. Counting failed statuses separately keeps the fake-provider diagnosis readable without expanding the raw probe payload in summary views.

## What Changes

- Add additive `runtime.probe_summary.failed_status_counts` to provider replay status.
- Mirror the same field through `provider-replay status --view summary` because the summary view carries the existing `probe_summary`.
- Keep the field read-only and derived from normalized probe objects only; do not add probe endpoints, socket startup, lifecycle management, restart/backoff, or write behavior.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-provider-transport-replay-service`

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Affected registry: `FUNCTION_TREE.md` E-06 evidence and boundary
