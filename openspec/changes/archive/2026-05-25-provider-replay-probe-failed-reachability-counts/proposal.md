## Why

E-06 provider replay status already exposes requested reachability counts and failed probe status/error rollups. Compact consumers can tell which probes failed, but they still need to inspect individual probe payloads to answer whether the failed set was reachable, unreachable, or unknown. A failed-only reachability count gives operators a tighter read-only diagnostic without broadening the replay service surface.

## What Changes

- Add additive `runtime.probe_summary.failed_reachability_counts`.
- Derive the counts from existing requested probes whose status is not `healthy`.
- Preserve the field in CLI `provider-replay status --view summary`, which already projects the compact `probe_summary`.

## Impact

- Code: `tdxquant/provider_transport_replay.py`.
- Tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`.
- Registry: update `FUNCTION_TREE.md` E-06 evidence and boundary.
- No new probe endpoint, socket startup, provider mutation, scheduler, restart/backoff, or daemon lifecycle behavior.
