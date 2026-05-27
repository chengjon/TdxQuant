# provider replay health summary presence flags

## Why

Provider replay status already exposes top-level `has_healthy_probe`, `has_failed_probe`, and `has_unhealthy_probe` flags alongside the compact `runtime.probe_summary.health_summary` object. Consumers using the nested health summary still have to inspect sibling fields or recompute presence from counts to tell whether any healthy, failed, or unhealthy probe exists.

Adding matching read-only presence flags to `health_summary` keeps E-06's status summary self-contained without changing probe execution, daemon lifecycle, replay transport behavior, or write capability.

## What Changes

- Add `runtime.probe_summary.health_summary.has_healthy_probe`.
- Add `runtime.probe_summary.health_summary.has_failed_probe`.
- Add `runtime.probe_summary.health_summary.has_unhealthy_probe`.
- Derive the flags only from existing normalized probe summary counts/lists.
- Keep detailed status and CLI summary view read-only; the summary view exposes these fields through the existing copied `probe_summary`.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence/boundary notes.

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused pytest for provider replay/API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation

