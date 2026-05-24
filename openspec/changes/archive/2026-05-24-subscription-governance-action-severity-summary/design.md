## Design

`_build_subscription_watch_governance_action_summary()` already receives the normalized advisory action list and returns a compact rollup. This change extends that rollup with a sorted `severity_counts` object:

- empty action lists return `{}` and keep `severity="none"`;
- each action with a non-empty string `severity` increments that severity key;
- keys are sorted to keep JSON output deterministic.

Because bridge HTTP and CLI summary views already project `governance.action_summary`, the new field flows through those summary views without exposing full `governance.actions`.

## Boundaries

- `severity_counts` is read-only advisory metadata.
- It does not change `governance.decision`, `requires_manual_review`, reason generation, or advisory action generation.
- It does not trigger reconnect, backoff, restart, lifecycle management, bridge HTTP behavior, SSE, or event-stream behavior.
- It does not expose the full `governance.actions` list in summary views.

## Verification

- Add focused unit coverage for observe and manual-review action summaries.
- Run `python -m pytest tests/test_subscription_watch_background.py tests/test_bridge_http.py tests/test_api_cli.py -q`.
- Run `openspec validate --all --strict`.
- Run `git diff --check`.
- Run `python scripts/validate_function_tree_registry.py`.
