## Context

`trade-sell` is already implemented as a task workflow and has ordinary Ping An sell audit report presets. The missing layer is discovery and non-executing plan coverage through the command catalog, mirroring the existing `task-buy` and sell submit-once follow-up patterns.

## Goals / Non-Goals

**Goals:**

- Add a stable default preset for `trade-sell`.
- Make ordinary sell available through `catalog list/plan`.
- Add fixed follow-up bundles for ordinary Ping An sell exception/rejection/failure audit review.
- Ensure catalog plan output preserves that the task step is `trade-sell`.

**Non-Goals:**

- No changes to sell desktop automation behavior.
- No new broker, order type, or submit semantics.
- No execution of trades in catalog plan tests.
- No relaxation of `max_price`, idempotency, user confirmation, or environment safety boundaries.

## Decisions

- Model `task-sell-default` after `task-buy-default` and use the existing `trade_sell` profile.
  - Rationale: the task command already owns sell behavior; the preset only provides a stable entry point.
- Add `task-sell` as a command catalog entry instead of broadening catalog source types.
  - Rationale: the catalog already supports `task` preset workflows and should keep using that boundary.
- Add three ordinary sell follow-up bundles: exceptions, rejected, and failed.
  - Rationale: this mirrors the already registered sell submit-once follow-up shape while keeping each bundle fixed and reviewable.

## Risks / Trade-offs

- A catalog entry may look executable without required order parameters. Mitigate by documenting this as a default template whose real execution still requires explicit trade parameters and existing safety controls.
- Adding bundles increases catalog size. Mitigate by adding only three high-signal ordinary sell review bundles tied to existing report presets.
