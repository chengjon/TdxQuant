## Why

E-06 provider replay status now exposes requested reachability counts and failed-only reachability counts. Compact consumers can distinguish failed reachability, but they still need to inspect probe payloads to summarize the healthy set's reachability buckets. A healthy-only reachability count completes the read-only rollup symmetry without broadening probe or daemon behavior.

## What Changes

- Add additive `runtime.probe_summary.healthy_reachability_counts`.
- Derive the counts from existing requested probes whose status is `healthy`.
- Preserve the field in CLI `provider-replay status --view summary`, which already projects the compact `probe_summary`.

## Impact

- Code: `tdxquant/provider_transport_replay.py`.
- Tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`.
- Registry: update `FUNCTION_TREE.md` E-06 evidence and boundary.
- No new probe endpoint, socket startup, provider mutation, scheduler, restart/backoff, or daemon lifecycle behavior.
