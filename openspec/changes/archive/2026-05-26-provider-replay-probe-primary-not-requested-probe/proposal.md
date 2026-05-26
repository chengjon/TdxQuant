## Why

E-06 provider replay status already exposes `not_requested` probe targets and request coverage status. Compact consumers can tell that unrequested probes exist, but still need to inspect the list to identify the first missing requested target. A single primary not-requested probe hint keeps coverage navigation compact without running additional probes or expanding daemon behavior.

## What Changes

- Add additive `runtime.probe_summary.primary_not_requested_probe`.
- Derive the value from the existing ordered `not_requested` probe list.
- Preserve the field in CLI `provider-replay status --view summary`, which already projects the compact `probe_summary`.

## Impact

- Code: `tdxquant/provider_transport_replay.py`.
- Tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`.
- Registry: update `FUNCTION_TREE.md` E-06 evidence and boundary.
- No new probe endpoint, socket startup, provider mutation, scheduler, restart/backoff, or daemon lifecycle behavior.
