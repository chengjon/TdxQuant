## Context

The desktop trade management line now has real safety controls and a durable idempotency ledger, but the task layer still invokes those workflows with an older argument surface. In practice this means higher-level callers using `TdxTaskManager` cannot benefit from the trade safety contract unless they bypass the task layer and call trade management directly.

This package is intentionally narrow: it does not add new safety logic at the task layer. It only lifts the already-stable trade safety controls up into the existing stable task workflows.

## Goals / Non-Goals

**Goals:**
- Let `TdxTaskManager.trade_buy(...)` accept `submission_key` and `max_price`.
- Let `TdxTaskManager.trade_submit_once(...)` accept `submission_key` and `max_price`.
- Let `TdxTaskManager.guarded_trade_buy(...)` accept `submission_key` and `max_price` and forward them into its underlying trade step.
- Let `task run --preset ...` parse and preserve these fields so task presets can carry defaults and explicit CLI flags can override them.

**Non-Goals:**
- Do not introduce task-specific duplicate protection beyond what trade management already does.
- Do not redesign guarded-trade prechecks.
- Do not add new top-level CLI concepts.

## Decisions

### 1. Reuse the existing trade safety contract instead of wrapping it again

The task layer will forward `submission_key` and `max_price` directly into the existing trade manager calls. It will not create a separate task-specific safety envelope. This keeps the durable submission ledger and the normalized `trade_safety` result contract owned by trade management.

### 2. Extend both direct task commands and preset-driven task execution

The package will update:
- direct task subcommands
- `_add_task_run_arguments(...)`
- task dispatch forwarding

This ensures that both `task trade-buy ...` and `task run --preset ...` behave consistently.

### 3. Keep result visibility through task payloads

The task layer already stores `trade_result.to_dict()` inside task results. Because the underlying trade result now includes `trade_safety` and `submission_ledger_path`, the task package only needs to avoid stripping them out. The task input section should also include the passed safety controls so operator intent is visible in task artifacts.

## Risks / Trade-offs

- [Task and trade interfaces may drift again later] → Keep task methods as thin passthrough wrappers over the stable trade manager safety surface.
- [Preset defaults may hide safety behavior] → Preserve explicit CLI overrides and keep the fields visible in task input payloads.
- [Guarded trade can now combine both snapshot prechecks and trade-manager max_price gates] → Keep the semantics explicit: snapshot gate is market-precheck, `max_price` is submitted-order ceiling.

## Migration Plan

1. Add RED tests for parser, dispatch, and task-manager passthrough behavior.
2. Extend task manager method signatures and forwarding calls.
3. Extend task CLI parsing and preset-run argument collection.
4. Update docs and run focused validation.

## Open Questions

- Whether future report or ledger views should surface submission-key-specific filters.
