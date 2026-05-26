# Design: Provider Replay Primary Requested Probe

## Behavior

`_build_provider_replay_probe_summary()` already builds a deterministic `requested` list by iterating `PROVIDER_REPLAY_STATUS_PROBE_KEYS`. The new field returns `requested[0]` when that list is non-empty and `None` otherwise.

The CLI provider replay summary view deep-copies the detailed `probe_summary`, so the same field appears there without a separate projection path.

## Boundary

`primary_requested_probe` is a compact diagnostic hint. It is not a new probe state, health guarantee, endpoint coverage proof, readiness signal, or execution instruction.

## Verification

- Add provider replay unit assertions for no-probe, one-probe, degraded, and all-probe cases.
- Add CLI summary assertion for `primary_requested_probe`.
- Run provider replay and API CLI tests, OpenSpec validation, diff check, and the FUNCTION_TREE validator.
