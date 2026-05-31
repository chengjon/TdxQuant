# PingAn Implemented Status Promotion Decision

## Why

D-07 and D-08 have accumulated real building blocks and read-only evidence aggregation, but the current rollup can only say whether evidence gates are complete or partial. It does not expose a fail-closed decision that explicitly answers whether the evidence package is eligible for an implemented-status review.

That gap is why recent work kept circling around registration and discovery. The mainline correction is to add a bounded promotion decision over the existing readiness rollup: it must block status promotion when evidence is missing, stale, unreadable, sample-only, or incomplete.

## What Changes

- Add a promotion decision object to PingAn promotion readiness rollup output.
- Preserve existing read-only behavior and side-effect flags.
- Treat sample/example manifests as ineligible for implemented-status promotion.
- Report blocked reasons, required gates, missing gates, stale evidence, source errors, and manual review requirements.
- Add tests that prove complete synthetic evidence may become eligible for review while partial/stale/sample evidence fails closed.
- Update `FUNCTION_TREE.md` D-07/D-08 as partial mainline evidence, not implemented status.

## Non-Goals

- Do not execute broker, desktop, trade, report, task, catalog, or bundle workflows.
- Do not mutate `FUNCTION_TREE.md` status automatically.
- Do not claim production readiness from unit-test fixtures.
- Do not replace live/manual acceptance evidence with sample manifests.
- Do not promote D-07 or D-08 to `[已实现]` in this change.
