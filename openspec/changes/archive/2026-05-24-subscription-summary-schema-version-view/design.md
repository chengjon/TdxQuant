# Design: Subscription Summary Schema Version View

## Approach

Extend `_build_bridge_watch_status_summary_payload()` to include `schema_version` in the small `status_summary` projection. The field is copied only from the already-built detailed `status_summary`.

## Compatibility

The response change is additive. Existing summary fields and raw-payload omissions remain unchanged.

## Boundaries

`schema_version` is an identifier for the summary payload shape. It is not a capability flag, readiness signal, lifecycle control, or governance decision.
