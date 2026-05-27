# Design: Subscription Evaluation Has Not-Evaluated Component

## Context

Subscription watch governance evaluation reports evaluated and not-evaluated component lists and counts. HTTP and CLI summary views preserve `governance.evaluation_summary` while omitting raw governance reasons/actions arrays.

## Design

Add `has_not_evaluated_component` to `_build_subscription_watch_governance_evaluation_summary()` as `bool(not_evaluated_components)`. This makes the existing coverage gap signal easy for compact consumers to read while keeping `not_evaluated_components`, `not_evaluated_count`, and `primary_not_evaluated_component` authoritative for details.

Tests cover direct status summary output plus HTTP/CLI summary views, because those surfaces preserve the evaluation summary for users and tooling.

## Non-Goals

- Do not change stale/fresh/not-evaluated classification.
- Do not change governance decision, action, reason, or manual-review semantics.
- Do not trigger reconnect, backoff, restart, lifecycle management, HTTP behavior, SSE behavior, event-stream behavior, provider mutation, or task execution.
