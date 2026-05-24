# Design: Subscription Summary Fresh Evaluation Counts

## Derivation

`fresh_components` is derived inside `_build_subscription_watch_governance_evaluation_summary()` from the same component summaries already used for `evaluated_components`, `stale_components`, and `not_evaluated_components`.

For each component:

- `not_evaluated` stays in `not_evaluated_components`.
- `stale` stays in `evaluated_components` and `stale_components`.
- `fresh` stays in `evaluated_components` and is added to `fresh_components`.

`fresh_count` is the length of `fresh_components`.

## Boundary

The field is an additive read-only summary. It does not change the governance decision, action generation, reconnect/backoff behavior, HTTP behavior, SSE behavior, or lifecycle controls.

## Testing

Add focused tests for:

- default not-evaluated summaries with no fresh components;
- mixed fresh/stale summaries;
- reconnect stale summaries preserving fresh counts for heartbeat/watermark.
