# Design: Subscription Evaluation Has Stale Component

## Context

Subscription watch governance evaluation currently reports evaluated, fresh, stale, and not-evaluated component lists and counts. HTTP and CLI summary views preserve `governance.evaluation_summary` while intentionally omitting raw governance reasons/actions arrays.

## Design

Add `has_stale_component` to `_build_subscription_watch_governance_evaluation_summary()` as `bool(stale_components)`. This makes the existing stale signal easier for compact consumers to read while keeping `stale_components`, `stale_count`, and `primary_stale_component` authoritative for details.

Tests cover direct status summary output plus HTTP/CLI summary views, because those are the consumer-facing surfaces that project the evaluation summary.

## Non-Goals

- Do not change stale/fresh/not-evaluated classification.
- Do not change governance decision, action, reason, or manual-review semantics.
- Do not trigger reconnect, backoff, restart, lifecycle management, HTTP behavior, SSE behavior, event-stream behavior, provider mutation, or task execution.
