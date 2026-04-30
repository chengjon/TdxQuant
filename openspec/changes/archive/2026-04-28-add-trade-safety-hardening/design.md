## Context

`TdxTradeManager` has already separated desktop trading from query management and persists a last-order state file plus append-only event logs. However, stable trade workflows still execute with a thin manager wrapper: caller correlation is weak, validation is mostly implicit, and result payloads do not expose a normalized safety view.

This package intentionally targets the first hardening slice only. The current user need is not a full trade-control plane, but a smaller contract that lets callers tag requests, reject obviously unsafe inputs before UI automation runs, and reason about the risk profile of returned trade results.

## Goals / Non-Goals

**Goals:**
- Add an explicit trade-safety metadata block to stable Ping An desktop trade results.
- Preserve an optional caller-supplied `submission_key` across result payloads and persisted trade artifacts.
- Reject invalid requests before any desktop automation side effects occur.
- Add a simple caller-controlled `max_price` risk ceiling for stable buy workflows.
- Expose the new safety controls through the stable nested and flat trade CLI entrypoints.

**Non-Goals:**
- Do not add automatic compare-and-skip idempotency yet.
- Do not add broker-generic abstractions beyond the current Ping An stable workflows.
- Do not redesign task-layer guarded trading in this package.
- Do not move desktop trade capabilities into the provider discovery mainline.

## Decisions

### 1. Scope the first risk gate to request validation plus `max_price`

The pre-trade risk gate will run before `run_pingan_buy_fast(...)` or `run_pingan_buy_submit_once(...)` is called. It will include:
- `OrderRequest.validate()` issues
- optional `max_price` ceiling comparison against the requested price

This keeps the first package deterministic and testable. It avoids mixing in runtime snapshot checks or confirmation dialogs, which belong to later guarded-trade layers.

Alternative considered:
- Add snapshot-based or block/formula-based risk checks here. Rejected because those already exist in task-level guarded flows and would make this package much larger.

### 2. Treat `submission_key` as correlation, not skip logic

`submission_key` will be preserved into:
- `result.data.trade_safety.submission_key`
- last-order state payload
- append-only event log

It will not automatically deduplicate or suppress execution. This preserves operator intent and avoids false safety claims before a proper idempotency ledger exists.

Alternative considered:
- Use `submission_key` to skip repeated trades immediately. Rejected because the current runtime has no durable compare-and-confirm model yet.

### 3. Reuse existing stability and side-effect vocabularies

The trade result safety block will use the same normalized grading words already established elsewhere in the project:
- `stability`: `beta`
- `side_effect_level`: `live_side_effecting`

This keeps trade safety output aligned with the broader capability-grading language without forcing desktop trade into the provider mainline.

### 4. Persist safety metadata alongside existing trade artifacts

The current last-order state and event-log files are already the durable operational artifacts for desktop trading. The new safety contract will extend those payloads instead of introducing a separate ledger in this first package.

Alternative considered:
- Write a separate trade-safety artifact. Rejected because it would duplicate state and make operator review harder.

### 5. Expose safety controls through existing stable CLI surfaces

The package will add `--submission-key` and `--max-price` to:
- `trade buy`
- `trade submit-once`
- `trade run`
- `pingan-buy`
- `pingan-buy-submit-once`

`trade run` will inherit the flags via existing preset merge behavior, so preset-defined defaults can be overridden explicitly at the CLI.

## Risks / Trade-offs

- [No true idempotent skip yet] → Document `submission_key` clearly as correlation-only and reserve dedupe for a later package.
- [Caller may confuse requested-price ceiling with market snapshot protection] → Name the check `max_price` and describe it as a guard against the submitted order price, not a live market validation.
- [Task-layer trading still lacks direct safety arguments] → Keep this package focused on stable trade manager and CLI entrypoints; task passthrough can be a follow-up.
- [Desktop trade result grading may be read as a provider guarantee] → Keep grading local to trade results and docs; do not register desktop trading in provider discovery mainline here.

## Migration Plan

1. Add tests for trade manager safety metadata, submission-key persistence, and pre-trade rejection.
2. Extend trade manager/context code with safety helpers and artifact payload updates.
3. Extend CLI parsers and dispatchers with the new safety flags.
4. Update docs and function map, then run focused test and OpenSpec validation.

Rollback is low risk because the change is additive to stable command arguments and result payloads. If needed, callers can ignore the new fields and arguments.

## Open Questions

- Whether task-layer `trade-buy` and `trade-submit-once` should expose the same safety flags in the next package.
- Whether future duplicate protection should live in the trade manager directly or in a higher-level guarded-trade ledger.
