# Proposal: Subscription Summary Fresh Evaluation Counts

## Why

`governance.evaluation_summary` already separates evaluated, stale, and not-evaluated subscription watch components, but it does not directly expose which evaluated components are fresh. Consumers must infer fresh components by subtracting stale components from evaluated components, which is easy to miss in compact long-run status summaries.

The summary should keep its advisory-only boundary while making fresh evaluated components explicit.

## What Changes

- Add `fresh_components` and `fresh_count` to `governance.evaluation_summary`.
- Derive both fields only from existing heartbeat/watermark/reconnect staleness values.
- Keep reconnect/backoff/lifecycle/event-stream behavior unchanged.

## Non-Goals

- Do not add automatic recovery, restart, reconnect, or backoff policy.
- Do not expose raw detailed payloads in compact summary views.
- Do not change default not-evaluated behavior when stale thresholds are absent.
