## Context

The desktop trade line now has:

- stable `trade health` for broker/runtime plus optional HID ping
- stable `trade_safety` with risk gates
- durable submission-ledger idempotency
- low-level broker and page probe commands

What is still missing is a stable, single-request readiness answer for a concrete order attempt. Operators currently need to mentally combine:

- broker health
- buy-page detect
- order validation / `max_price`
- submission-key idempotency
- HID bridge reachability

This package narrows that gap without expanding the actual execution surface.

## Goals / Non-Goals

**Goals:**
- Expose `TdxTradeManager.pingan.preflight(...)` as a stable read-only workflow.
- Expose `trade preflight` as the nested CLI entrypoint.
- Evaluate buy-page detect, order-request risk gate, idempotency, and HID ping together for one concrete requested trade.
- Keep the workflow non-side-effecting and artifact-free.

**Non-Goals:**
- Do not execute any desktop input or confirmation action.
- Do not replace low-level experimental probe commands.
- Do not add `trade run --preset ...` support in this slice.
- Do not redesign `trade health`; preflight is a separate higher-granularity workflow.

## Decisions

### 1. Preflight is request-shaped, not environment-shaped

`trade health` already answers environment readiness. This package answers whether one concrete stable desktop trade request is ready to proceed. Therefore `preflight` will require the same core trade request fields as the stable buy path:

- `port`
- `code`
- `price`
- `quantity`

and it will optionally accept:

- `submission_key`
- `max_price`
- serial timing overrides needed for HID `PING`

### 2. Preflight combines stable checks but keeps them individually visible

The workflow will surface named checks rather than collapsing everything into one string:

- `broker_runtime`
- `buy_page_detection`
- `risk_gate`
- `idempotency`
- `hid_ping`

This preserves operator visibility and keeps test expectations stable.

### 3. Idempotency outcomes map to readiness semantics, not execution semantics

The existing idempotency helper yields:

- `no_submission_key`
- `execute`
- `skip_duplicate`
- `reject_conflict`

For preflight:

- `no_submission_key` becomes `skipped`
- `execute` becomes `ok`
- `skip_duplicate` becomes `warning`
- `reject_conflict` becomes `failed`

This reflects what the operator needs to know before deciding whether to place a live order.

### 4. Preflight stays outside trade finalization

Like `trade health`, this workflow must not call `_finalize_result(...)`. It will attach manager/profile metadata directly and return:

- requested input
- check list
- overall status
- artifact target paths

without writing state or ledger artifacts.

## Risks / Trade-offs

- [Preflight may be confused with actual execution] → Keep `preflight` explicitly read-only and separate from `buy`.
- [Buy-page detection may fail on client variants that still trade successfully via experimental paths] → Limit the promise to the stable Ping An desktop path.
- [Duplicate submission keys can be misread as a failure] → Represent same-request duplicate as warning instead of hard failure.

## Migration Plan

1. Add RED tests for manager and CLI behavior.
2. Implement stable preflight on the Ping An trade proxy.
3. Add nested CLI parser and dispatch.
4. Update docs, validate, and archive.

## Open Questions

- Whether future `trade preflight` should also expose confirm/result-dialog lookup readiness as separate non-side-effecting checks.
