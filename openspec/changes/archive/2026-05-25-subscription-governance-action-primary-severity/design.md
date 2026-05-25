## Design

`_build_subscription_watch_governance_action_summary` already selects the first advisory action and returns `severity` as that action's severity, or `"none"` when there are no actions. Add `primary_severity` alongside `severity` using the same derivation.

The field is intentionally additive. Existing callers that read `severity` continue to work, while newer compact consumers can use `primary_severity` to avoid ambiguity with `severity_counts`.

## Boundary

`primary_severity` is a compact advisory hint over already-built governance actions. It does not inspect raw control/watch payloads, expose full action arrays in summary views, execute actions, or change reconnect/backoff/restart/lifecycle behavior.
