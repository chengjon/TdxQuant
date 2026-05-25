## Design

`_build_subscription_watch_governance_evaluation_summary()` already iterates over heartbeat, watermark, and reconnect summaries and records each component status. This change adds a second deterministic count map:

- `component_status_counts` continues to count every component, including `not_evaluated`;
- `evaluated_status_counts` increments only for components whose status is not `not_evaluated`;
- keys are sorted for stable JSON output;
- no explicit stale thresholds returns `{}`.

Because bridge HTTP and CLI summary views already project `governance.evaluation_summary`, the new field flows through those views without exposing raw payloads or lifecycle controls.

## Boundaries

- `evaluated_status_counts` is read-only advisory metadata.
- It does not change `governance.decision`, `requires_manual_review`, reason generation, or advisory action generation.
- It does not trigger reconnect, backoff, restart, lifecycle management, bridge HTTP behavior, SSE, or event-stream behavior.
- It does not treat fresh evaluated components as a health guarantee or readiness proof.

