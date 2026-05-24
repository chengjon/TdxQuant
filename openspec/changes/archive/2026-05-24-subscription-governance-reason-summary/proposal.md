# Change: Subscription Governance Reason Summary

## Why

`bridge watch-status --view summary` and the worker bridge HTTP summary already expose reason counts, bounded reason samples, and reason source counts. Operators still need a compact, stable reason rollup that identifies the primary advisory reason without relying on the bounded sample array or reading the detailed raw `governance.reasons` list.

## What Changes

- Add a read-only `governance.reason_summary` object to the subscription long-run status summary.
- Project `governance.reason_summary` through CLI and HTTP watch-status summary views.
- Keep the field derived only from existing advisory reasons; do not trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

## Out of Scope

- No scheduler, restart, reconnect, or backoff policy changes.
- No full raw reason/action arrays in summary views.
- No change to provider transport replay, subscription event streaming, or watch lifecycle control.
