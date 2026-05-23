## Context

`trade submit-once --side sell` and `task trade-submit-once --side sell` already expose the side boundary, but the sell branch intentionally routes through `pingan.sell`. That kept the prior change small and prevented readers from assuming a dedicated `run_pingan_sell_submit_once` implementation existed.

The codebase already has a stable sell desktop path (`run_pingan_sell_fast`) and a stable submit-once identity pattern for buy (`buy_submit_once`). A dedicated `sell_submit_once` manager method can combine those two existing pieces: use the sell automation flow, but record submit-once-specific method names, idempotency keys, timing labels, and audit metadata.

## Goals / Non-Goals

**Goals:**

- Add a dedicated `TdxTradeManager.pingan.sell_submit_once` method.
- Preserve existing order-entry behavior by reusing `run_pingan_sell_fast`.
- Record `sell_submit_once` as the manager method, idempotency method, timing label, and task route identity.
- Route gateway/task submit-once sell requests through the dedicated method.

**Non-Goals:**

- No new `run_pingan_sell_submit_once` desktop automation primitive.
- No new CLI command name; existing `--side sell` remains the public selector.
- No expansion to other brokers, order types, exception dialogs, or result-dialog parsing branches.

## Decisions

- Reuse `run_pingan_sell_fast` under `sell_submit_once`.
  - Rationale: the desktop steps for sell are already implemented and tested; this change is about identity and routing, not a new automation primitive.
- Use `method="sell_submit_once"` for idempotency, final metadata, and task evidence.
  - Rationale: buy/sell submit-once now share a clear audit namespace instead of mixing `buy_submit_once` and ordinary `sell`.
- Keep CLI surface unchanged.
  - Rationale: `trade submit-once --side sell` already states the user-facing intent; adding another command would duplicate surface area without a new capability.

## Risks / Trade-offs

- A reader may infer a dedicated desktop primitive exists -> mitigate by documenting that `sell_submit_once` reuses `run_pingan_sell_fast`.
- Reports that currently filter only `buy_submit_once` remain unchanged -> this package does not add sell-submit-once report presets; those should be registered separately if needed.
