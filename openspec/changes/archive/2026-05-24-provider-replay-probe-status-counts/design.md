## Design

`_build_provider_replay_probe_summary()` already walks the fixed `PROVIDER_REPLAY_STATUS_PROBE_KEYS` order and derives requested/healthy/failed/not-requested counts. This change adds a deterministic `status_counts` object during the same pass:

- every probe contributes exactly one status bucket;
- missing probe data is treated as `not_requested`;
- keys are sorted before returning.

Because CLI summary view copies `runtime.probe_summary`, the new field is visible in `provider-replay status --view summary` without extra summary code and without exposing new endpoint, token, fixture path, or allowlist detail.

## Boundaries

- This is read-only rollup metadata.
- It does not perform probes unless explicit probe flags are passed.
- It does not start, stop, restart, daemonize, supervise, schedule, or manage a replay service.
- It does not imply live provider readiness or long-running daemon governance.

## Verification

- Add focused provider replay status tests for `status_counts`.
- Run `python -m pytest tests/test_provider_transport_replay.py tests/test_api_cli.py -q`.
- Run `openspec validate --all --strict`.
- Run `git diff --check`.
- Run `python scripts/validate_function_tree_registry.py`.
