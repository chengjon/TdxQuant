## Context

The finalized PingAn trade path already attaches audit metadata and writes last-order state, event rows, optional submission ledger rows, and immutable audit artifacts. The audit status resolver currently maps duplicate submissions to `replayed`, pre-trade rejection to `rejected`, successful results to `confirmed`, and all other failures to `failed`.

## Goals / Non-Goals

**Goals:**

- Add a minimal explicit exception classification path for finalized PingAn results.
- Preserve existing confirmed/replayed/rejected/failed classification.
- Keep exception evidence tied to standard finalized artifact persistence.
- Preserve D-07/D-08 partial status semantics in `FUNCTION_TREE.md`.

**Non-Goals:**

- Do not implement desktop exception popup discovery.
- Do not add retry/backoff policy.
- Do not catch arbitrary Python exceptions around live desktop dispatch.
- Do not mark D-07 or D-08 `[已实现]`.

## Decisions

- Use explicit result metadata as the signal: a finalized result with `data.desktop_exception` or `data.trade_exception` is classified as `exception`.
- Keep the signal inside the standard resolver instead of adding a separate persistence path. This ensures exception evidence writes the same state/event/audit artifacts as other finalized outcomes.
- Leave unmarked `ErrorCode.EXECUTION_FAILED` results classified as `failed`. A generic execution failure should not become exception evidence unless the result explicitly carries exception metadata.

## Risks / Trade-offs

- [Risk] Exception status could be mistaken for live exception-popup handling. -> FUNCTION_TREE and specs state that this only classifies explicit exception metadata and does not implement popup handling or retry policy.
- [Risk] Existing failed result behavior could change. -> Tests will cover only explicitly marked exception metadata and preserve the generic failure mapping.
- [Risk] The signal name may evolve. -> Support two explicit keys, `desktop_exception` and `trade_exception`, while avoiding broad heuristic matching.

