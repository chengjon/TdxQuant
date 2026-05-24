# Design: Subscription Governance Detailed Reason Count

## Approach

Compute `reason_count` in `_build_subscription_watch_governance_summary()` immediately after the reasons list is built. The new field is serialized alongside `reasons` and `reason_source_counts`, so full status consumers can use a scalar count without parsing arrays.

## Compatibility

The field is additive. Existing consumers that read `reasons`, `reason_source_counts`, `actions`, or summary-view payloads continue to see the same structures.

## Boundaries

`reason_count` is a read-only projection. It does not trigger reconnect/backoff decisions, restart the background worker, mutate watch state, or replace the detailed reasons list.
