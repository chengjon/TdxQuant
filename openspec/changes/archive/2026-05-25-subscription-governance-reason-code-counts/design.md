## Design

`_build_subscription_watch_governance_reason_summary()` already receives the normalized advisory reason list and returns a compact rollup. This change extends that rollup with a sorted `reason_code_counts` object:

- empty reason lists return `{}`;
- each non-empty string reason increments its exact reason key, such as `heartbeat:stale`;
- keys are sorted to keep JSON output deterministic.

Because bridge HTTP and CLI summary views already project `governance.reason_summary`, the new field flows through those compact views without exposing the full `governance.reasons` list.

## Boundaries

- `reason_code_counts` is read-only advisory metadata.
- It does not change `governance.decision`, `requires_manual_review`, reason generation, advisory action generation, reconnect, backoff, or lifecycle behavior.
- It does not start, stop, restart, daemonize, supervise, schedule, or probe any subscription worker.
- It does not expose raw `governance.reasons` or `governance.actions` in summary views.

## Verification

- Add focused unit coverage for observe and manual-review reason summaries.
- Add HTTP/CLI summary projection coverage for `reason_summary.reason_code_counts`.
- Run `python -m pytest tests/test_subscription_watch_background.py tests/test_bridge_http.py tests/test_api_cli.py -q`.
- Run `openspec validate --all --strict`.
- Run `git diff --check`.
- Run `python scripts/validate_function_tree_registry.py`.

