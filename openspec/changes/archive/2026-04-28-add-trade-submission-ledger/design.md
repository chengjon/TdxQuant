## Context

The previous desktop trade safety package made `submission_key` visible but intentionally left it as correlation-only metadata. That was the right first slice, but it still leaves the stable trade flows exposed to accidental repeated clicks when an upstream caller retries with the same request key.

The project already has durable state and event artifacts for desktop trading, so the natural next step is to add a durable submission ledger with conservative idempotency behavior. The key constraint is safety: if a prior keyed request may already have caused a real desktop side effect, the system must prefer not executing again.

## Goals / Non-Goals

**Goals:**
- Make `submission_key` meaningful for stable Ping An desktop trade workflows.
- Persist durable submission-ledger rows for keyed requests.
- Short-circuit duplicate keyed requests that match a prior side-effecting attempt.
- Reject keyed requests that reuse a key for a different trade intent after a prior side-effecting attempt.
- Extend `trade_safety` with normalized idempotency metadata.

**Non-Goals:**
- Do not generalize idempotency across all brokers.
- Do not add a background lock service or distributed coordination.
- Do not redesign task-layer guarded trading in this package.
- Do not add new user-facing CLI concepts beyond the already existing `submission_key`.

## Decisions

### 1. Use a local append-only submission ledger

The new artifact will be `runtime/pingan-submission-ledger.jsonl`. Each keyed attempt appends one durable row that captures:
- `submission_key`
- normalized request fingerprint
- risk-gate outcome
- final result snapshot
- idempotency decision

Append-only JSONL matches the current operational style already used for order events. It is simple to inspect manually and does not require schema migration machinery.

Alternative considered:
- Replace with a single mutable JSON object. Rejected because append-only history is safer for audit and easier to reason about after failures.

### 2. Bind idempotency to trade intent, not transport noise

The submission ledger will use a normalized fingerprint built from the business-relevant trade intent:
- broker
- method
- stock code
- price
- quantity

It will not include transport parameters such as COM port or timeout. Those settings can vary without changing the actual trading intent.

### 3. Use conservative skip semantics after any side-effecting attempt

If a keyed request already has a prior row whose risk gate passed, the new behavior is:
- same fingerprint: short-circuit and return the prior outcome without executing again
- different fingerprint: reject as a conflict

This is conservative by design. Even if the prior attempt ended in a non-OK result, the system must assume that the desktop may already have advanced far enough to produce a side effect.

### 4. Allow retries after non-side-effecting pre-trade rejection

If the prior keyed row failed before the risk gate passed, the system may continue and evaluate the new request normally. This avoids permanently burning a key when no desktop side effect happened yet.

### 5. Represent idempotency under `trade_safety`

The result contract will extend the existing `trade_safety` object with an `idempotency` block rather than inventing a new top-level payload shape. That keeps all operator-facing trade safety context together.

## Risks / Trade-offs

- [A failed desktop run might still have partially side effected the broker client] → Treat any prior post-risk-gate attempt as non-repeatable for the same key.
- [Operators may want to force a retry after a bad outcome] → Require a new `submission_key` for a new desktop attempt.
- [Ledger rows could grow over time] → Use append-only JSONL now; rotation or compaction can be a later operational package.
- [Fingerprint fields might be too narrow or too broad] → Limit the first slice to business intent fields and document the choice explicitly.

## Migration Plan

1. Add RED tests for duplicate skip, conflicting-key rejection, and ledger persistence.
2. Extend trade context with ledger path and JSONL helper functions.
3. Extend `TdxTradeManager` stable workflows to consult the ledger before desktop execution and append ledger rows after finalization.
4. Surface the ledger artifact path in result payloads and update docs.

Rollback is straightforward: remove ledger consultation while leaving `submission_key` as correlation-only metadata again.

## Open Questions

- Whether future operator tooling should expose a ledger lookup/report command.
- Whether task-layer guarded trading should share the same ledger or keep a higher-level workflow ledger.
