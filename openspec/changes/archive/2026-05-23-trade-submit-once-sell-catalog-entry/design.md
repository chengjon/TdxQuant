## Context

`task-submit-once` defaults to buy, while explicit `side=sell` routes through `TdxTaskManager.trade_submit_once(side="sell")` and then `TdxTradeManager.pingan.sell_submit_once`. Existing sell submit-once bundles already pass `side=sell`, but that intent is hidden inside bundle step options rather than visible as a first-class catalog entry.

## Goals / Non-Goals

**Goals:**

- Make sell submit-once discoverable as a side-explicit task preset and catalog entry.
- Preserve current buy default behavior for `submit-once-default` / `task-submit-once`.
- Keep sell submit-once follow-up bundles non-executing under catalog plan and visibly resolved to `side=sell`.

**Non-Goals:**

- No new desktop primitive named `run_pingan_sell_submit_once`.
- No changes to broker automation, audit writing, idempotency, max-price, or dialog handling.
- No implicit execution in catalog plan/preview tests.

## Decisions

- Name the preset `sell-submit-once-default` and the catalog entry `task-sell-submit-once`.
  - Rationale: the names align with existing sell-submit-once audit entries while preserving the catalog convention that task entries start with `task-`.
- Put `side: "sell"` in the preset options rather than in each bundle step.
  - Rationale: the side boundary becomes visible at entry resolution and remains overridable only through normal explicit CLI argument precedence.
- Update existing sell submit-once follow-up bundles to use `task-sell-submit-once`.
  - Rationale: the bundle plan should show the side-specific entry directly instead of a generic entry with hidden options.

## Risks / Trade-offs

- Additional entries increase catalog surface area. Mitigate by adding only one side-explicit task entry and reusing existing report bundles.
- Operators may read the entry as a new desktop primitive. Mitigate through `FUNCTION_TREE.md` boundary text and OpenSpec scenarios that state the existing task/manager path is reused.
