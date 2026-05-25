## Why

Provider replay probe summaries expose requested status counts and failed status counts, but operators still need a compact view of probe reachability. Counting requested probe reachability makes it easier to distinguish HTTP reachability failures from other unhealthy results without expanding raw probe payloads.

## What Changes

- Add additive `runtime.probe_summary.requested_reachability_counts`.
- Count only requested fixed probe targets.
- Use stable bucket names: `reachable`, `unreachable`, and `unknown`.
- Mirror the field through `provider-replay status --view summary` because the summary view carries the existing `probe_summary`.
- Keep behavior read-only; do not add probes, start sockets, manage daemon lifecycle, or change replay transport behavior.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-provider-transport-replay-service`

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Affected registry: `FUNCTION_TREE.md` E-06 evidence and boundary
