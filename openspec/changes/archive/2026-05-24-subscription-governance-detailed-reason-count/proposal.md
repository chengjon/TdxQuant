# Proposal: Subscription Governance Detailed Reason Count

## Why

`build_subscription_watch_status_summary()` already returns detailed advisory governance reasons and `reason_source_counts`, while CLI/HTTP summary views expose a derived `reason_count`. Callers using the full status payload still need to parse the reasons list just to know whether the detailed governance decision has zero, one, or multiple reasons.

## What Changes

Add an additive `governance.reason_count` scalar to the detailed subscription watch status summary. The value is derived from the existing `governance.reasons` list and remains advisory-only.

## Out Of Scope

- No reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior changes.
- No hiding or replacing the full `governance.reasons` list.
- No escalation from advisory governance to automatic remediation.

## Success Criteria

- Detailed observe governance reports `reason_count: 0`.
- Detailed manual-review governance reports `reason_count` equal to the existing reasons list length.
- Existing summary-view `reason_count` behavior remains compatible.
