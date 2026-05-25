## Why

E-06 provider replay status already exposes healthy probe counts and the ordered `healthy` probe list. Compact consumers can tell whether healthy probes exist, but they still need to inspect the list to identify the first healthy target. A single primary healthy probe hint keeps summary navigation symmetric with `primary_failed_probe` without expanding probe execution or daemon behavior.

## What Changes

- Add additive `runtime.probe_summary.primary_healthy_probe`.
- Derive the value from the existing ordered `healthy` probe list.
- Preserve the field in CLI `provider-replay status --view summary`, which already projects the compact `probe_summary`.

## Impact

- Code: `tdxquant/provider_transport_replay.py`.
- Tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`.
- Registry: update `FUNCTION_TREE.md` E-06 evidence and boundary.
- No new probe endpoint, socket startup, provider mutation, scheduler, restart/backoff, or daemon lifecycle behavior.
