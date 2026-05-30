## Context

PingAn `dialog_readiness` returns partial desktop lifecycle evidence. It already records dialog lookup status, passive exception popup lookup, and passive process/window observation. The retry policy gate remains incomplete because the workflow does not retry failed dialog states, back off, recover, or resubmit orders.

## Goals / Non-Goals

**Goals:**

- Add a stable `retry_policy_status` object to `desktop_lifecycle_gate_status`.
- Make the current no-retry behavior explicit and machine-readable.
- Keep `retry_policy` in `remaining_lifecycle_gates` until a real retry/backoff implementation and acceptance evidence exist.
- Preserve D-07/D-08 partial status semantics in `FUNCTION_TREE.md`.

**Non-Goals:**

- Do not retry failed lookups, failed orders, or exception popups.
- Do not add backoff timers, sleep loops, supervisor recovery, or resubmission.
- Do not write order state, submission ledger, or audit artifacts from dialog readiness.
- Do not mark D-07 or D-08 `[已实现]`.

## Decisions

- Represent the status as a top-level `desktop_lifecycle_gate_status.retry_policy_status` object, not as a health check. This makes the policy visible without changing dialog readiness pass/fail semantics.
- Use `status=not_configured`, `execution_mode=readonly_policy_status`, `retry_executed=false`, and `backoff_executed=false` for the current implementation. These fields intentionally avoid implying that retry/backoff is available.
- Keep `retry_policy` in `remaining_lifecycle_gates`. A status registry is not the same as executable retry/recovery.

## Risks / Trade-offs

- [Risk] Consumers might treat the status object as implemented retry. -> The status explicitly reports `not_configured` and false execution flags, and FUNCTION_TREE records the boundary.
- [Risk] Future retry profile fields may need a richer schema. -> The current payload includes a `policy_source` and `configured_policy` object so later changes can extend the status without changing the basic location.
