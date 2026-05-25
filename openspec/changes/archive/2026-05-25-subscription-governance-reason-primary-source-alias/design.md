## Design

`_build_subscription_watch_governance_reason_summary` already computes `primary_source` from the first advisory reason using `_subscription_watch_governance_reason_source`. Add `primary_reason_source` to the returned summary with the same value.

The field is intentionally additive. Existing callers that read `primary_source` continue to work, while newer compact consumers can use the naming pattern shared with `governance.action_summary.primary_reason_source`.

## Boundary

`primary_reason_source` is a compact advisory alias over already-built governance reasons. It does not inspect raw control/watch payloads, expose full reason arrays in summary views, execute actions, or change reconnect/backoff/restart/lifecycle behavior.
