# Proposal: Catalog Trade Plan Input Coverage Status

## Why

Add an explicit `input_coverage_status` field to non-executing catalog trade plan summaries so readers can distinguish complete preset input coverage, missing required order inputs, and commands that require no order inputs.

`trade_plan_boundary` already exposes required/provided/missing input field lists and counts, but consumers still need to infer whether a catalog plan is complete, incomplete, or input-free. That inference can be easy to miss in summary views, especially because these catalog plans are non-executing and must not imply live trade readiness.

## What Changes

- Expose a small derived status in `trade_plan_boundary` for trade-related catalog entries and bundle steps.
- Keep the status strictly tied to catalog input coverage, not broker readiness or live execution readiness.
- Preserve existing field lists, counts, side handling, and `dispatch_executed=false`.

## Non-Goals

- Do not execute catalog dispatch, live trade flows, safety approval, or broker probing.
- Do not change task presets, command catalog definitions, or real trading behavior.
- Do not claim that complete input coverage means the trade is safe or executable.

## Scope

The change is limited to `catalog plan` summary/preview payloads that already include `trade_plan_boundary`.
